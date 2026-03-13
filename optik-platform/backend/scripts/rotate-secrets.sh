#!/bin/bash

# ============================================
# SECRETS ROTATION SCRIPT
# ============================================
# Automates rotation of sensitive credentials
# Run monthly: 0 0 1 * * (first day of month)
# ============================================

set -euo pipefail

# Configuration
ENV_FILE="/optik-platform/apps/.env.secure"
BACKUP_DIR="/optik-platform/backups/secrets"
LOG_FILE="/optik-platform/logs/secret-rotation.log"

# Ensure directories exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Generate secure random string
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Backup current secrets
backup_secrets() {
    log "Creating backup of current secrets..."
    cp "$ENV_FILE" "$BACKUP_DIR/.env.secure.backup.$(date +%Y%m%d_%H%M%S)"
    chmod 600 "$BACKUP_DIR"/.env.secure.backup.*
    log "Backup completed"
}

# Rotate JWT secrets
rotate_jwt_secrets() {
    log "Rotating JWT secrets..."
    
    local new_jwt_secret=$(generate_secret)
    local new_session_secret=$(generate_secret)
    
    sed -i "s/JWT_SECRET=.*/JWT_SECRET=${new_jwt_secret}/" "$ENV_FILE"
    sed -i "s/SESSION_SECRET=.*/SESSION_SECRET=${new_session_secret}/" "$ENV_FILE"
    
    log "JWT secrets rotated"
}

# Rotate database passwords
rotate_db_secrets() {
    log "Rotating database passwords..."
    
    local new_redis_password=$(generate_secret)
    local new_mongo_password=$(generate_secret)
    
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=${new_redis_password}/" "$ENV_FILE"
    sed -i "s|MONGODB_URL=.*|MONGODB_URL=mongodb://username:${new_mongo_password}@localhost:27017/optik|" "$ENV_FILE"
    
    log "Database passwords rotated"
}

# Rotate API keys (requires manual intervention)
rotate_api_keys() {
    log "API keys require manual rotation..."
    log "Please update: ANTHROPIC_API_KEY, OPENAI_API_KEY, PINATA_API_KEY"
}

# Update services with new secrets
update_services() {
    log "Restarting services with new secrets..."
    
    # Restart application
    cd /optik-platform/apps
    npm run build
    pkill -f "next start" || true
    nohup npm run start:prod > /dev/null 2>&1 &
    
    # Restart backend
    cd /optik-platform/backend
    pkill -f "uvicorn" || true
    nohup python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4 > /dev/null 2>&1 &
    
    log "Services restarted with new secrets"
}

# Verify services are healthy
verify_services() {
    log "Verifying service health..."
    
    sleep 30
    
    # Check frontend
    if curl -f http://localhost:3003/api/health > /dev/null 2>&1; then
        log "✅ Frontend is healthy"
    else
        log "❌ Frontend health check failed"
        return 1
    fi
    
    # Check backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ Backend is healthy"
    else
        log "❌ Backend health check failed"
        return 1
    fi
}

# Send notification
send_notification() {
    local status=$1
    local webhook_url=${SECURITY_WEBHOOK:-}
    
    if [[ -n "$webhook_url" ]]; then
        local message="Secret rotation completed with status: $status"
        curl -X POST "$webhook_url" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$message\",\"timestamp\":\"$(date -Iseconds)\"}" \
            2>/dev/null || true
    fi
}

# Main execution
main() {
    log "Starting secret rotation process..."
    
    # Check if environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log "Error: Environment file not found at $ENV_FILE"
        exit 1
    fi
    
    # Create backup
    backup_secrets
    
    # Rotate different types of secrets
    rotate_jwt_secrets
    rotate_db_secrets
    rotate_api_keys
    
    # Update services
    if update_services; then
        # Verify services
        if verify_services; then
            send_notification "SUCCESS"
            log "✅ Secret rotation completed successfully"
        else
            send_notification "FAILED - Health check failed"
            log "❌ Secret rotation failed - health check failed"
            exit 1
        fi
    else
        send_notification "FAILED - Service update failed"
        log "❌ Secret rotation failed - service update failed"
        exit 1
    fi
    
    # Cleanup old backups (keep last 5)
    find "$BACKUP_DIR" -name ".env.secure.backup.*" -type f -mtime +30 -delete 2>/dev/null || true
    log "Cleanup completed"
}

# Execute main function
main "$@"
