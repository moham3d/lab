#!/bin/bash

# Patient Visit Management System - Production Deployment Script
# This script handles the complete deployment process

set -e

echo "🚀 Starting Patient Visit Management System Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="patient-visit-system"
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Please copy .env.example to .env and configure your settings."
        exit 1
    fi

    log_info "Requirements check passed!"
}

create_backup() {
    log_info "Creating database backup..."

    mkdir -p "$BACKUP_DIR"

    # Create timestamp for backup
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

    # If database is running, create backup
    if docker-compose ps db | grep -q "Up"; then
        docker-compose exec -T db pg_dump -U patient_user -d patient_visits > "$BACKUP_FILE"
        log_info "Database backup created: $BACKUP_FILE"
    else
        log_warn "Database is not running, skipping backup"
    fi
}

stop_services() {
    log_info "Stopping existing services..."
    docker-compose down || true
}

build_services() {
    log_info "Building services..."
    docker-compose build --no-cache
}

start_services() {
    log_info "Starting services..."
    docker-compose up -d
}

wait_for_services() {
    log_info "Waiting for services to be healthy..."

    # Wait for database
    log_info "Waiting for database..."
    for i in {1..30}; do
        if docker-compose exec -T db pg_isready -U patient_user -d patient_visits &>/dev/null; then
            log_info "Database is ready!"
            break
        fi
        sleep 2
    done

    # Wait for Redis
    log_info "Waiting for Redis..."
    for i in {1..30}; do
        if docker-compose exec -T redis redis-cli ping &>/dev/null; then
            log_info "Redis is ready!"
            break
        fi
        sleep 2
    done

    # Wait for application
    log_info "Waiting for application..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            log_info "Application is ready!"
            break
        fi
        sleep 2
    done
}

run_migrations() {
    log_info "Running database migrations..."
    docker-compose exec app alembic upgrade head
}

run_tests() {
    log_info "Running tests..."
    docker-compose exec app python -m pytest app/tests/ -v
}

cleanup_old_backups() {
    log_info "Cleaning up old backups..."

    # Keep only last 7 backups
    cd "$BACKUP_DIR" || exit
    ls -t backup_*.sql | tail -n +8 | xargs -r rm
    cd - || exit

    log_info "Old backups cleaned up"
}

run_monitoring() {
    log_info "Running system monitoring checks..."
    if [ -f "./scripts/monitor.sh" ]; then
        ./scripts/monitor.sh
    else
        log_warn "Monitoring script not found, skipping monitoring checks"
    fi
}

show_status() {
    log_info "Deployment completed successfully!"
    log_info "Service Status:"
    docker-compose ps

    log_info "Application Health:"
    if curl -f -s http://localhost/health >/dev/null 2>&1; then
        curl -s http://localhost/health | python -m json.tool 2>/dev/null || curl -s http://localhost/health
    else
        log_warn "Could not access health endpoint through nginx"
        log_info "Trying direct app access..."
        curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
    fi

    log_info "Useful commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Run migrations: docker-compose exec app alembic upgrade head"
    echo "  • Access database: docker-compose exec db psql -U patient_user -d patient_visits"
    echo "  • Run monitoring: ./scripts/monitor.sh"
    echo "  • Create backup: ./scripts/backup.sh"
}

# Main deployment process
main() {
    echo "=========================================="
    echo "Patient Visit Management System Deployment"
    echo "=========================================="

    check_requirements
    create_backup
    stop_services
    build_services
    start_services
    wait_for_services
    run_migrations

    # Optional: run tests in production (comment out for faster deployment)
    # run_tests

    run_monitoring
    cleanup_old_backups
    show_status

    log_info "🎉 Deployment completed successfully!"
    log_info "Application is available at: http://localhost:8000"
    log_info "API Documentation: http://localhost:8000/docs"
}

# Handle command line arguments
case "${1:-}" in
    "backup")
        create_backup
        ;;
    "stop")
        stop_services
        ;;
    "start")
        start_services
        ;;
    "restart")
        stop_services
        start_services
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "test")
        run_tests
        ;;
    *)
        main
        ;;
esac