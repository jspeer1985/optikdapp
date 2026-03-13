# Security Setup Guide - Optik Platform Backend

## 🚨 Critical Security Setup Required

This document outlines the **mandatory security steps** before deploying the Optik Platform to production.

---

## 1. Environment Configuration

### ✅ **Create Secure .env File**
```bash
# Copy the secure template
cp .env.template .env

# Set restrictive permissions
chmod 600 .env

# Generate strong secrets (example commands)
openssl rand -hex 32  # for JWT_SECRET
openssl rand -hex 32  # for SESSION_SECRET
```

### 🔐 **Replace All Placeholder Values**
- `JWT_SECRET` - 32+ character random string
- `SESSION_SECRET` - 32+ character random string  
- `ANTHROPIC_API_KEY` - Your actual Anthropic API key
- `PINATA_API_KEY` - Your Pinata API key
- `REDIS_PASSWORD` - Strong Redis password
- All other API keys and secrets

---

## 2. Database Security

### MongoDB Hardening
```bash
# Ensure MongoDB uses authentication
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=your_strong_mongo_password

# Use environment variables (no hardcoded credentials)
ME_CONFIG_BASICAUTH_USERNAME=${OPTIK_MONGO_ROOT_USER}
ME_CONFIG_BASICAUTH_PASSWORD=${OPTIK_MONGO_ROOT_PASSWORD}
```

### Redis Security
```bash
# Set strong password
REDIS_PASSWORD=your_strong_redis_password_2024
```

---

## 3. Production Deployment

### Docker Compose Security
```bash
# Use production-ready configuration
docker-compose -f docker-compose.mongodb.yml --profile production up

# NEVER use --profile dev in production
```

### Network Security
```bash
# Firewall rules (example)
ufw allow 8000/tcp  # API only
ufw deny 8081/tcp  # Block MongoDB UI
ufw allow from 127.0.0.1 to any port 27017/tcp  # MongoDB only from localhost
```

---

## 4. Service Isolation

### Development Services
```bash
# MongoDB UI only in development
docker-compose -f docker-compose.mongodb.yml --profile dev up

# Production services (no MongoDB UI)
docker-compose -f docker-compose.mongodb.yml --profile production up
```

---

## 5. Monitoring & Logging

### Security Headers
```bash
# Verify HTTPS headers
curl -I https://api.optikcoin.com/health

# Check security headers
curl -I -H "Origin: https://optikcoin.com" https://api.optikcoin.com
```

### Access Logs
```bash
# API logs
docker logs optik-api

# MongoDB logs  
docker logs optik-mongodb

# Redis logs
docker logs optik-redis
```

---

## 6. Automated Security Scans

### Daily Checks
```bash
# Port scan
nmap -sS -p 8000,27017,8081 localhost

# SSL certificate check
ssl-checker https://api.optikcoin.com

# Dependency vulnerability scan
npm audit
pip audit
```

---

## 7. Backup & Recovery

### Database Backups
```bash
# MongoDB backup
mongodump --uri="$MONGODB_URL" --out=/backup/mongodb-$(date +%Y%m%d)

# Redis backup
redis-cli --rdb /backup/redis-$(date +%Y%m%d).rdb
```

### Configuration Backups
```bash
# Encrypt backup
tar -czf /backup/env-backup-$(date +%Y%m%d).tar.gz .env
gpg --symmetric --cipher-algo AES256 --compress-algo 1 /backup/env-backup-*.tar.gz
```

---

## 8. Incident Response

### Security Incident Checklist
- [ ] Isolate affected systems
- [ ] Preserve forensic evidence  
- [ ] Rotate all compromised credentials
- [ ] Update security configurations
- [ ] Notify stakeholders
- [ ] Document lessons learned

---

## 9. Compliance

### Data Protection
- [ ] GDPR compliance check
- [ ] CCPA compliance check
- [ ] Data retention policy implemented
- [ ] Right to deletion process

### Financial Regulations
- [ ] KYC/AML procedures
- [ ] Transaction monitoring
- [ ] Suspicious activity reporting
- [ ] Regulatory reporting

---

## 🔒 Security Checklist

### Pre-Deployment Security Checklist
- [ ] All secrets replaced with strong values
- [ ] Environment variables validated
- [ ] File permissions set to 600
- [ ] Development services disabled in production
- [ ] Network security rules configured
- [ ] SSL certificates valid
- [ ] Monitoring systems active
- [ ] Backup procedures tested
- [ ] Incident response plan ready
- [ ] Security audit completed

### Post-Deployment Monitoring
- [ ] Log aggregation working
- [ ] Security alerts configured
- [ ] Performance monitoring active
- [ ] Uptime monitoring active
- [ ] Regular security scans scheduled
- [ ] Access logs reviewed daily

---

## 🚨 Emergency Contacts

### Security Team
- **Security Lead:** [Contact Information]
- **DevOps Lead:** [Contact Information]  
- **Legal Counsel:** [Contact Information]

### External Services
- **Hosting Provider:** [Contact Information]
- **CDN Provider:** [Contact Information]
- **Security Auditor:** [Contact Information]

---

**Last Updated:** March 13, 2026  
**Version:** 1.0  
**Status:** Ready for Secure Deployment

⚠️ **CRITICAL:** Complete ALL steps before production deployment
