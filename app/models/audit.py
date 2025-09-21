"""
Audit log model for HIPAA-compliant logging
"""

from uuid import uuid4
from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models import Base


class AuditLog(Base):
    """
    Audit log model for tracking all user actions on PHI data
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)

    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., "CREATE", "READ", "UPDATE", "DELETE"
    resource_type = Column(String(50), nullable=False, index=True)  # e.g., "patient", "visit", "document"
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # ID of the resource being acted upon

    # Additional context
    details = Column(JSON, nullable=True)  # JSON object with action-specific details
    old_values = Column(JSON, nullable=True)  # Previous values for UPDATE actions
    new_values = Column(JSON, nullable=True)  # New values for CREATE/UPDATE actions

    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6 address
    user_agent = Column(Text, nullable=True)  # Browser/client user agent
    session_id = Column(String(100), nullable=True)  # Session identifier

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    api_endpoint = Column(String(255), nullable=True)  # API endpoint accessed
    http_method = Column(String(10), nullable=True)  # HTTP method (GET, POST, etc.)
    response_status = Column(String(10), nullable=True)  # HTTP response status

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user={self.user_id}, action={self.action}, resource={self.resource_type}:{self.resource_id})>"

    @staticmethod
    def create_log_entry(
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        details: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        response_status: Optional[str] = None
    ) -> "AuditLog":
        """Factory method to create audit log entry"""
        return AuditLog(
            user_id=user_id,
            action=action.upper(),
            resource_type=resource_type.lower(),
            resource_id=resource_id,
            details=details,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            api_endpoint=api_endpoint,
            http_method=http_method,
            response_status=response_status
        )

    @property
    def is_sensitive_action(self) -> bool:
        """Check if this action involves sensitive operations"""
        sensitive_actions = {"DELETE", "UPDATE"}
        sensitive_resources = {"patient", "assessment"}
        return (
            self.action in sensitive_actions or
            self.resource_type in sensitive_resources
        )

    @property
    def action_description(self) -> str:
        """Get human-readable action description"""
        return f"{self.action} {self.resource_type} {self.resource_id}"

    @property
    def has_data_changes(self) -> bool:
        """Check if this log entry includes data changes"""
        return self.old_values is not None or self.new_values is not None

    def get_changed_fields(self) -> list:
        """Get list of fields that were changed"""
        if not self.has_data_changes:
            return []

        changed_fields = set()

        if self.old_values:
            changed_fields.update(self.old_values.keys())
        if self.new_values:
            changed_fields.update(self.new_values.keys())

        return sorted(list(changed_fields))