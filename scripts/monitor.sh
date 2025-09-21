#!/bin/bash

# Production Monitoring Script for Patient Visit Management System
# This script checks the health of all services and provides status reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
LOG_FILE="./logs/monitoring.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Logging function
log() {
    echo -e "${BLUE}[$TIMESTAMP]${NC} $1" | tee -a "$LOG_FILE"
}

# Error logging function
error_log() {
    echo -e "${RED}[$TIMESTAMP] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Success logging function
success_log() {
    echo -e "${GREEN}[$TIMESTAMP] SUCCESS:${NC} $1" | tee -a "$LOG_FILE"
}

# Warning logging function
warning_log() {
    echo -e "${YELLOW}[$TIMESTAMP] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if Docker is running
check_docker() {
    log "Checking Docker status..."
    if ! docker info >/dev/null 2>&1; then
        error_log "Docker is not running or not accessible"
        return 1
    fi
    success_log "Docker is running"
    return 0
}

# Check if docker-compose file exists
check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        error_log "Docker Compose file '$COMPOSE_FILE' not found"
        return 1
    fi
    success_log "Docker Compose file found"
    return 0
}

# Check service health
check_service_health() {
    local service=$1
    local max_attempts=5
    local attempt=1

    log "Checking health of service: $service"

    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps "$service" | grep -q "Up"; then
            success_log "Service $service is running"
            return 0
        fi

        warning_log "Service $service not ready (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done

    error_log "Service $service failed to start after $max_attempts attempts"
    return 1
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    if docker-compose exec -T db pg_isready -U patient_user -d patient_visits >/dev/null 2>&1; then
        success_log "Database is accessible"
        return 0
    else
        error_log "Database is not accessible"
        return 1
    fi
}

# Check Redis connectivity
check_redis() {
    log "Checking Redis connectivity..."
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        success_log "Redis is accessible"
        return 0
    else
        error_log "Redis is not accessible"
        return 1
    fi
}

# Check application health endpoint
check_app_health() {
    log "Checking application health endpoint..."
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost/health >/dev/null 2>&1; then
            success_log "Application health check passed"
            return 0
        fi

        warning_log "Application health check failed (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done

    error_log "Application health check failed after $max_attempts attempts"
    return 1
}

# Check disk usage
check_disk_usage() {
    log "Checking disk usage..."
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

    if [ "$usage" -gt 90 ]; then
        error_log "Disk usage is high: ${usage}%"
        return 1
    elif [ "$usage" -gt 75 ]; then
        warning_log "Disk usage is moderate: ${usage}%"
    else
        success_log "Disk usage is normal: ${usage}%"
    fi
    return 0
}

# Check memory usage
check_memory_usage() {
    log "Checking memory usage..."
    local usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')

    if [ "$usage" -gt 90 ]; then
        error_log "Memory usage is high: ${usage}%"
        return 1
    elif [ "$usage" -gt 75 ]; then
        warning_log "Memory usage is moderate: ${usage}%"
    else
        success_log "Memory usage is normal: ${usage}%"
    fi
    return 0
}

# Get service logs
get_service_logs() {
    local service=$1
    local lines=${2:-50}

    log "Getting last $lines lines of logs for service: $service"
    docker-compose logs --tail="$lines" "$service" 2>/dev/null || warning_log "Could not retrieve logs for $service"
}

# Main monitoring function
main() {
    log "=== Starting Production Monitoring ==="

    local failed_checks=0

    # Basic checks
    check_docker || ((failed_checks++))
    check_compose_file || ((failed_checks++))

    # Service health checks
    check_service_health "db" || ((failed_checks++))
    check_service_health "redis" || ((failed_checks++))
    check_service_health "app" || ((failed_checks++))
    check_service_health "celery_worker" || ((failed_checks++))

    # Connectivity checks
    check_database || ((failed_checks++))
    check_redis || ((failed_checks++))
    check_app_health || ((failed_checks++))

    # System resource checks
    check_disk_usage || ((failed_checks++))
    check_memory_usage || ((failed_checks++))

    # Summary
    log "=== Monitoring Summary ==="
    if [ $failed_checks -eq 0 ]; then
        success_log "All checks passed! System is healthy."
        exit 0
    else
        error_log "$failed_checks check(s) failed. Please review the logs above."
        log "Getting recent logs for troubleshooting..."

        # Get logs for failed services
        get_service_logs "app" 20
        get_service_logs "db" 20
        get_service_logs "redis" 20

        exit 1
    fi
}

# Run main function
main "$@"