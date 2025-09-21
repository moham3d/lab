"""
Audit service for HIPAA-compliant logging of user actions
"""

import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.report import AuditLogSummary
from app.core.config import settings


class AuditService:
    """Service for audit logging and compliance"""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        details: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        Log a user action for audit purposes
        """
        # Extract request context if available
        ip_address = None
        user_agent = None
        api_endpoint = None
        http_method = None

        if request:
            ip_address = AuditService._get_client_ip(request)
            user_agent = request.headers.get("user-agent")
            api_endpoint = str(request.url.path)
            http_method = request.method

        # Create audit log entry
        audit_entry = AuditLog.create_log_entry(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            api_endpoint=api_endpoint,
            http_method=http_method
        )

        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)

        return audit_entry

    @staticmethod
    def _get_client_ip(request: Request) -> Optional[str]:
        """Extract client IP address from request"""
        # Check for forwarded headers first (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP if multiple are present
            return forwarded_for.split(",")[0].strip()

        # Check for other proxy headers
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        return getattr(request.client, 'host', None) if request.client else None

    @staticmethod
    async def get_user_audit_logs(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific user with optional filters
        """
        query = select(AuditLog).where(AuditLog.user_id == user_id)

        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if action:
            query = query.where(AuditLog.action == action)
        if start_date:
            query = query.where(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.where(AuditLog.timestamp <= end_date)

        query = query.order_by(desc(AuditLog.timestamp)).limit(limit).offset(offset)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_resource_audit_logs(
        db: AsyncSession,
        resource_type: str,
        resource_id: UUID,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific resource
        """
        query = select(AuditLog).where(
            and_(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
        ).order_by(desc(AuditLog.timestamp)).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_audit_summary(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[UUID] = None
    ) -> AuditLogSummary:
        """
        Get audit log summary statistics
        """
        # Base query
        query = select(AuditLog)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if start_date:
            query = query.where(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.where(AuditLog.timestamp <= end_date)

        # Get total actions
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total_actions = total_result.scalar() or 0

        # Get actions by type
        actions_by_type_query = select(
            AuditLog.action,
            func.count(AuditLog.id)
        ).select_from(query.subquery()).group_by(AuditLog.action)

        actions_result = await db.execute(actions_by_type_query)
        actions_by_type = {row[0]: row[1] for row in actions_result.all()}

        # Get actions by user
        user_actions_query = select(
            AuditLog.user_id,
            func.count(AuditLog.id)
        ).select_from(query.subquery()).group_by(AuditLog.user_id)

        user_result = await db.execute(user_actions_query)
        actions_by_user = {str(row[0]): row[1] for row in user_result.all()}

        # Count sensitive actions
        sensitive_actions_query = select(func.count()).select_from(
            query.where(
                or_(
                    AuditLog.action.in_(["DELETE", "UPDATE"]),
                    AuditLog.resource_type.in_(["patient", "assessment"])
                )
            ).subquery()
        )
        sensitive_result = await db.execute(sensitive_actions_query)
        sensitive_actions = sensitive_result.scalar() or 0

        # Get recent actions
        recent_query = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(10)
        recent_result = await db.execute(recent_query)
        recent_actions = [
            {
                "id": str(log.id),
                "user_id": str(log.user_id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id),
                "timestamp": log.timestamp.isoformat(),
                "api_endpoint": log.api_endpoint
            }
            for log in recent_result.scalars().all()
        ]

        return AuditLogSummary(
            total_actions=total_actions,
            actions_by_type=actions_by_type,
            actions_by_user=actions_by_user,
            sensitive_actions=sensitive_actions,
            recent_actions=recent_actions
        )

    @staticmethod
    async def cleanup_old_logs(
        db: AsyncSession,
        retention_days: Optional[int] = None
    ) -> int:
        """
        Clean up old audit logs based on retention policy
        Returns number of deleted records
        """
        if retention_days is None:
            retention_days = settings.AUDIT_LOG_RETENTION_DAYS

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Delete old logs
        from sqlalchemy import delete
        delete_query = delete(AuditLog).where(AuditLog.timestamp < cutoff_date)

        result = await db.execute(delete_query)
        await db.commit()

        return result.rowcount

    @staticmethod
    async def export_audit_logs(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Export audit logs for compliance reporting
        """
        query = select(AuditLog).where(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
        )

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)

        query = query.order_by(AuditLog.timestamp)

        result = await db.execute(query)
        logs = result.scalars().all()

        # Convert to exportable format
        export_data = []
        for log in logs:
            export_data.append({
                "id": str(log.id),
                "timestamp": log.timestamp.isoformat(),
                "user_id": str(log.user_id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id),
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "api_endpoint": log.api_endpoint,
                "http_method": log.http_method,
                "response_status": log.response_status,
                "details": json.dumps(log.details) if log.details else None,
                "old_values": json.dumps(log.old_values) if log.old_values else None,
                "new_values": json.dumps(log.new_values) if log.new_values else None
            })

        return export_data

    @staticmethod
    def should_log_action(action: str, resource_type: str) -> bool:
        """
        Determine if an action should be logged based on compliance requirements
        """
        # Always log sensitive actions
        sensitive_actions = {"CREATE", "UPDATE", "DELETE"}
        if action in sensitive_actions:
            return True

        # Always log PHI-related resources
        phi_resources = {"patient", "assessment", "document"}
        if resource_type in phi_resources:
            return True

        # Log authentication actions
        auth_actions = {"LOGIN", "LOGOUT", "TOKEN_REFRESH"}
        if action in auth_actions:
            return True

        # Log admin actions
        if resource_type == "user" and action in {"CREATE", "UPDATE", "DELETE"}:
            return True

        return False</content>
<parameter name="filePath">C:\Users\Mohamed\Desktop\lab\app\services\audit_service.py