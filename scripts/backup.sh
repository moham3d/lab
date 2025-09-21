#!/bin/bash

# Database Backup Script for Patient Visit Management System

set -e

# Configuration
BACKUP_DIR="./backups"
DB_CONTAINER="patient-visit-system_db_1"
DB_USER="patient_user"
DB_NAME="patient_visits"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

create_backup() {
    log_info "Starting database backup..."

    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"

    # Generate timestamp
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

    log_info "Creating backup: $BACKUP_FILE"

    # Create compressed backup
    docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

    # Check if backup was successful
    if [ $? -eq 0 ]; then
        log_info "Backup completed successfully: $BACKUP_FILE"

        # Get backup size
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log_info "Backup size: $BACKUP_SIZE"

        # Verify backup integrity
        if gzip -t "$BACKUP_FILE"; then
            log_info "Backup integrity check passed"
        else
            log_error "Backup integrity check failed!"
            exit 1
        fi
    else
        log_error "Backup failed!"
        exit 1
    fi
}

cleanup_old_backups() {
    log_info "Cleaning up old backups..."

    # Keep only last 7 backups
    cd "$BACKUP_DIR" || exit 1

    # Count total backups
    TOTAL_BACKUPS=$(ls -1 backup_*.sql.gz 2>/dev/null | wc -l)

    if [ "$TOTAL_BACKUPS" -gt 7 ]; then
        # Remove old backups (keep last 7)
        ls -t backup_*.sql.gz | tail -n +8 | xargs -r rm

        REMOVED=$((TOTAL_BACKUPS - 7))
        log_info "Removed $REMOVED old backup(s)"
    else
        log_info "No old backups to clean up ($TOTAL_BACKUPS total)"
    fi

    cd - || exit 1
}

list_backups() {
    log_info "Available backups:"

    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null || echo "No backups found"
    else
        echo "Backup directory does not exist"
    fi
}

restore_backup() {
    if [ $# -eq 0 ]; then
        log_error "Please specify backup file to restore"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi

    BACKUP_FILE="$1"

    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    log_warn "This will overwrite the current database!"
    read -p "Are you sure you want to restore from $BACKUP_FILE? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi

    log_info "Restoring from backup: $BACKUP_FILE"

    # Stop the application to prevent data corruption
    log_info "Stopping application..."
    docker-compose stop app celery_worker

    # Restore backup
    gunzip -c "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"

    if [ $? -eq 0 ]; then
        log_info "Database restored successfully"

        # Restart application
        log_info "Restarting application..."
        docker-compose start app celery_worker

        log_info "Restore completed successfully"
    else
        log_error "Database restore failed!"
        exit 1
    fi
}

show_usage() {
    echo "Database Backup Script for Patient Visit Management System"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  backup    Create a new database backup"
    echo "  list      List all available backups"
    echo "  restore   Restore from a backup file"
    echo "  cleanup   Remove old backups (keep last 7)"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 list"
    echo "  $0 restore ./backups/backup_20231201_120000.sql.gz"
    echo "  $0 cleanup"
}

# Main script
case "${1:-backup}" in
    "backup")
        create_backup
        cleanup_old_backups
        ;;
    "list")
        list_backups
        ;;
    "restore")
        restore_backup "$2"
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac