# 📋 OPTIK AUDIT - IMPLEMENTATION GUIDE

**This document provides step-by-step instructions to fix all identified issues.**

---

## PRIORITY 1: CRITICAL SECURITY FIXES (DO IMMEDIATELY)

### Fix #1: Move API Keys to Secrets Vault

**Status:** 🔴 CRITICAL
**Time Estimate:** 4 hours
**Risk if not done:** Account compromise, financial loss

#### Step 1: Regenerate All Keys (AWS Example)

```bash
# 1. Go to Anthropic Console
# https://console.anthropic.com/account/keys
# Click "Create" to generate new API key
NEW_ANTHROPIC_KEY="sk-ant-..."

# 2. Go to Stripe Dashboard
# https://dashboard.stripe.com/apikeys
# Click "Reveal live key" to create new secret key
NEW_STRIPE_KEY="sk_live_..."

# 3. Go to Pinata Dashboard
# Create new API key and secret

# 4. Create new Solana wallet (devnet first!)
# Don't use existing with balance
```

#### Step 2: Create AWS Secrets Manager

```bash
# Create Anthropic API Key Secret
aws secretsmanager create-secret \
  --name optik/anthropic-api-key \
  --secret-string "$NEW_ANTHROPIC_KEY" \
  --region us-east-1

# Create Stripe Secret Key
aws secretsmanager create-secret \
  --name optik/stripe-secret-key \
  --secret-string "$NEW_STRIPE_KEY" \
  --region us-east-1

# Create Stripe Webhook Secret
aws secretsmanager create-secret \
  --name optik/stripe-webhook-secret \
  --secret-string "whsec_..." \
  --region us-east-1

# Create Pinata Keys
aws secretsmanager create-secret \
  --name optik/pinata-api-key \
  --secret-string "..." \
  --region us-east-1

# Create Solana Private Key
aws secretsmanager create-secret \
  --name optik/solana-private-key \
  --secret-string "[...]" \
  --region us-east-1
```

#### Step 3: Update Python Code

**File:** `optik-platform/backend/.env` → DELETE IT

**File:** `optik-platform/backend/optik_gpt/config.py` (add)

```python
import boto3
import os
import json

def get_secret(secret_name: str) -> str:
    """Fetch secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager',
                         region_name=os.getenv('AWS_REGION', 'us-east-1'))
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except client.exceptions.ResourceNotFoundException:
        raise ValueError(f"Secret {secret_name} not found")

# Load secrets
ANTHROPIC_API_KEY = get_secret('optik/anthropic-api-key')
STRIPE_SECRET_KEY = get_secret('optik/stripe-secret-key')
STRIPE_WEBHOOK_SECRET = get_secret('optik/stripe-webhook-secret')
PINATA_API_KEY = get_secret('optik/pinata-api-key')
PINATA_SECRET_KEY = get_secret('optik/pinata-secret-key')
SOLANA_WALLET_PRIVATE_KEY = get_secret('optik/solana-private-key')
```

**File:** Update all imports

```python
# Before
from dotenv import load_dotenv
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# After
from optik_gpt.config import ANTHROPIC_API_KEY
```

#### Step 4: Create .env.example (Safe)

**File:** `optik-platform/backend/.env.example`

```
# OPTIK PLATFORM - Environment Variables
# All sensitive values are managed in AWS Secrets Manager

# --- Server Basics ---
PORT=8000
HOST=0.0.0.0
DEBUG=False  # Set to False in production

# --- AWS Configuration ---
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# --- Database ---
DATABASE_URL=postgresql://user:pass@localhost:5432/optik

# --- Redis Cache ---
REDIS_URL=redis://localhost:6379

# --- Logging ---
LOG_LEVEL=INFO

# NOTE: All API keys, secrets, and private keys are stored in AWS Secrets Manager
# See config.py for details
```

#### Step 5: Update Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY . .

# Set environment for AWS access
ENV AWS_REGION=us-east-1

# Run application
CMD ["uvicorn", "optik_gpt.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 6: Test

```bash
# Test secret retrieval
python -c "from optik_gpt.config import ANTHROPIC_API_KEY; print(f'✅ Got key: {ANTHROPIC_API_KEY[:20]}...')"
```

---

### Fix #2: Implement Rate Limiting

**Status:** 🔴 CRITICAL
**Time Estimate:** 2-4 hours
**Risk if not done:** DDoS attacks, runaway costs

#### Step 1: Install Dependencies

```bash
pip install slowapi python-dotenv
```

#### Step 2: Create Rate Limiter Module

**File:** `optik-platform/backend/utils/rate_limiter.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import os

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# Default limits
DEFAULT_LIMIT = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
CHAT_LIMIT = os.getenv("RATE_LIMIT_CHAT", "10/minute")
PAYMENT_LIMIT = os.getenv("RATE_LIMIT_PAYMENT", "5/minute")
AUTH_LIMIT = os.getenv("RATE_LIMIT_AUTH", "5/minute")

def rate_limit_error(request, exc):
    """Custom rate limit error response."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": str(exc.detail),
            "retry_after": 60
        }
    )
```

#### Step 3: Update FastAPI App

**File:** `optik-platform/backend/api/main.py` (modify)

```python
from utils.rate_limiter import limiter, rate_limit_error
from slowapi.errors import RateLimitExceeded

# Add to app initialization
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_error)

# Add rate limiting decorator to endpoints
@app.post("/api/optik-gpt/chat")
@limiter.limit("10/minute")
async def chat(request: ChatRequest, request_obj):
    ...

@app.post("/api/payments/webhook")
@limiter.limit("100/minute")  # Higher limit for webhook
async def webhook(request: Request):
    ...

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(credentials: LoginRequest):
    ...
```

#### Step 4: Add per-Merchant Limits

```python
# Advanced: Per-merchant rate limiting
from slowapi.util import get_remote_address
from typing import Callable

def get_merchant_id(request: Request) -> str:
    """Extract merchant ID from request."""
    # If authenticated, use merchant ID
    if hasattr(request.state, 'merchant_id'):
        return request.state.merchant_id
    # Otherwise use IP
    return get_remote_address(request)

merchant_limiter = Limiter(key_func=get_merchant_id)

@app.post("/api/products")
@merchant_limiter.limit("100/hour")
async def create_product(product: ProductRequest):
    ...
```

#### Step 5: Test

```bash
# Test rate limiting
for i in {1..15}; do
    curl -X POST http://localhost:8000/api/optik-gpt/chat \
        -H "Content-Type: application/json" \
        -d '{"message":"test","merchant_id":"test"}' \
        -w "\n%{http_code}\n"
done
# Should return 429 after 10th request
```

---

### Fix #3: Add Security Headers

**Status:** 🔴 CRITICAL
**Time Estimate:** 1-2 hours

#### Step 1: Create Security Middleware

**File:** `optik-platform/backend/utils/security.py`

```python
from fastapi import Request
from fastapi.responses import Response
import os

async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Clickjacking protection
    response.headers["X-Frame-Options"] = "DENY"

    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # HSTS (forces HTTPS)
    response.headers["Strict-Transport-Security"] = \
        "max-age=31536000; includeSubDomains"

    # CSP (Content Security Policy)
    response.headers["Content-Security-Policy"] = \
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Feature Policy
    response.headers["Permissions-Policy"] = \
        "camera=(), microphone=(), geolocation=()"

    return response
```

#### Step 2: Add to FastAPI App

**File:** `optik-platform/backend/api/main.py`

```python
from utils.security import add_security_headers

# Add security middleware
app.middleware("http")(add_security_headers)

# Also add TrustedHost middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,optik-platform.com").split(",")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

# Add HTTPS redirect in production
if not os.getenv("DEBUG"):
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)
```

#### Step 3: Test

```bash
# Check headers
curl -I http://localhost:8000/api/optik-gpt/health

# Should show:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Strict-Transport-Security: max-age=31536000
# etc.
```

---

## PRIORITY 2: HIGH PRIORITY FIXES (Next Week)

### Fix #4: Migrate to PostgreSQL

**Time Estimate:** 12 hours

#### Step 1: Create PostgreSQL Database

```bash
# Install PostgreSQL (if needed)
brew install postgresql@15  # macOS
# or
sudo apt install postgresql  # Ubuntu

# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb optik

# Create user
createuser -P optik_user  # Set password when prompted
```

#### Step 2: Update Database Connection

**File:** `optik-platform/backend/utils/database.py` (modify)

```python
# Change from SQLite to PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://optik_user:password@localhost:5432/optik"
)

# No more SQLite detection needed
ASYNC_DATABASE_URL = DATABASE_URL
SYNC_DATABASE_URL = DATABASE_URL.replace("asyncpg", "")
```

#### Step 3: Create Migration Script

**File:** `optik-platform/backend/scripts/migrate_to_postgres.py`

```python
import sqlite3
import asyncpg
import asyncio
import json

async def migrate():
    """Migrate data from SQLite to PostgreSQL."""
    # Connect to both databases
    sqlite_conn = sqlite3.connect("/path/to/optik.db")
    sqlite_cursor = sqlite_conn.cursor()

    pg_conn = await asyncpg.connect(
        "postgresql://optik_user:password@localhost:5432/optik"
    )

    # Migrate jobs table
    sqlite_cursor.execute("SELECT * FROM jobs")
    rows = sqlite_cursor.fetchall()

    for row in rows:
        await pg_conn.execute(
            """INSERT INTO jobs VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)""",
            *row
        )

    print(f"✅ Migrated {len(rows)} jobs")

    # Similar for other tables...
    await pg_conn.close()
    sqlite_conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
```

#### Step 4: Run Migration

```bash
cd optik-platform/backend
python scripts/migrate_to_postgres.py
```

---

### Fix #5: Implement Comprehensive Logging

**Time Estimate:** 4-6 hours

#### Step 1: Create Logging Configuration

**File:** `optik-platform/backend/utils/logging_config.py`

```python
import logging
import json
from datetime import datetime
import os

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for parsing."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logging(app_name: str = "optik"):
    """Configure structured logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(f"logs/{app_name}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JSONFormatter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

#### Step 2: Add Request Logging Middleware

**File:** `optik-platform/backend/api/main.py`

```python
import uuid
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with correlation ID."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info({
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(process_time * 1000),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent", "Unknown")
    })

    return response
```

---

## PRIORITY 3: MEDIUM PRIORITY (This Month)

### Additional Recommended Fixes

1. **Add Monitoring (Sentry)**
   - Time: 4 hours
   - Cost: Free tier available

2. **Add Performance Monitoring (Datadog)**
   - Time: 6 hours
   - Cost: ~$15/day

3. **Add Load Testing**
   - Time: 8 hours
   - Tools: Locust, Apache JMeter

4. **Create Admin Dashboard**
   - Time: 20 hours
   - Tech: React, Chart.js

---

## VERIFICATION CHECKLIST

After implementing all fixes, verify:

```bash
# Security
[ ] API keys moved to secrets vault
[ ] Rate limiting working (test with 20 requests)
[ ] Security headers present (curl -I)
[ ] HTTPS only (check .env)
[ ] CORS restricted (check allowed origins)

# Database
[ ] PostgreSQL running
[ ] Data migrated successfully
[ ] Queries work
[ ] Backups automated

# Logging
[ ] Logs are JSON formatted
[ ] Request IDs in all logs
[ ] Structured logging working
[ ] Log rotation configured

# Performance
[ ] Response times <200ms
[ ] Database queries optimized
[ ] Redis caching working
[ ] No N+1 queries

# Monitoring
[ ] Sentry capturing errors
[ ] Datadog tracking metrics
[ ] Alerts configured
[ ] Dashboards set up
```

---

## ROLLOUT PLAN

### Phase 1: Development (Week 1)
- [ ] Implement all fixes in dev environment
- [ ] Test thoroughly
- [ ] Get code review

### Phase 2: Staging (Week 2)
- [ ] Deploy to staging
- [ ] Run full test suite
- [ ] Load test
- [ ] Security audit

### Phase 3: Production (Week 3)
- [ ] Deploy with feature flags
- [ ] Monitor closely
- [ ] Have rollback plan ready
- [ ] Gradual rollout (10% → 50% → 100%)

---

## ESTIMATED TIMELINE

| Task | Hours | Days | Priority |
|------|-------|------|----------|
| Secrets Management | 4 | 1 | CRITICAL |
| Rate Limiting | 4 | 1 | CRITICAL |
| Security Headers | 2 | 0.5 | CRITICAL |
| PostgreSQL Migration | 12 | 2-3 | HIGH |
| Comprehensive Logging | 6 | 1 | HIGH |
| Monitoring Setup | 10 | 2 | HIGH |
| E2E Testing | 20 | 3 | MEDIUM |
| Load Testing | 8 | 1 | MEDIUM |
| **TOTAL** | **66** | **10-12** | - |

---

## BUDGET ESTIMATE

| Item | Cost | Notes |
|------|------|-------|
| AWS Secrets Manager | $0.40/secret/month | 5 secrets = $2/month |
| PostgreSQL (RDS) | $50-100/month | Development to small production |
| Redis (ElastiCache) | $15-30/month | Small cluster |
| Sentry | Free tier | $29/month for full features |
| Datadog | $15/day | $450/month |
| LoadTesting.io | $20/month | Load testing service |
| **TOTAL** | **~$150-200/month** | - |

---

**Next Steps:** Start with CRITICAL fixes this week!

