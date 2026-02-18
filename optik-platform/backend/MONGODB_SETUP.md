# MongoDB Setup Guide for Optik Platform

Complete guide to set up MongoDB for the Optik DApp Platform.

---

## 📋 Table of Contents

1. [Quick Start (Local)](#quick-start-local)
2. [Docker Compose Setup](#docker-compose-setup)
3. [MongoDB Atlas (Cloud)](#mongodb-atlas-cloud)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start (Local)

### Prerequisites
- MongoDB 7.0+ installed locally
- Python 3.13+
- Motor (async MongoDB driver)

### Installation

**1. Install MongoDB Locally**

**macOS:**
```bash
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows:**
```bash
# Download from: https://www.mongodb.com/try/download/community
# Run installer and follow prompts
```

**2. Install Python Dependencies**

```bash
cd optik-platform/backend

# Install MongoDB drivers
pip install motor pymongo

# Or update requirements
pip install -r requirements.txt
```

**3. Configure Environment**

```bash
# Copy MongoDB configuration
cp .env.mongodb .env

# Edit .env with your settings (if needed)
# Default: mongodb://localhost:27017/optik
```

**4. Run Application**

```bash
# Start the API
uvicorn api.main:app --reload

# MongoDB will auto-initialize on startup
```

---

## Docker Compose Setup

### Prerequisites
- Docker installed
- Docker Compose 2.0+
- 2GB free disk space

### Quick Setup

**1. Navigate to backend directory**
```bash
cd optik-platform/backend
```

**2. Start all services**
```bash
# Start MongoDB, Redis, and Optik API
docker-compose -f docker-compose.mongodb.yml up -d

# View logs
docker-compose -f docker-compose.mongodb.yml logs -f optik-api

# Stop all services
docker-compose -f docker-compose.mongodb.yml down
```

### Included Services

| Service | Port | Purpose | Username | Password |
|---------|------|---------|----------|----------|
| MongoDB | 27017 | Database | optik_admin | secure_password_change_me |
| Mongo Express | 8081 | Web UI | admin | admin |
| Redis | 6379 | Cache | - | - |
| Optik API | 8000 | Backend | - | - |

### Access Services

**MongoDB Shell:**
```bash
docker exec -it optik-mongodb mongosh -u optik_admin -p secure_password_change_me --authenticationDatabase admin
```

**Mongo Express UI:**
```
http://localhost:8081
Username: admin
Password: admin
```

**API Documentation:**
```
http://localhost:8000/docs
```

### Useful Commands

```bash
# View MongoDB logs
docker-compose -f docker-compose.mongodb.yml logs mongodb

# Check MongoDB status
docker exec optik-mongodb mongosh -u optik_admin -p secure_password_change_me --eval "db.adminCommand('ping')"

# Restart MongoDB
docker-compose -f docker-compose.mongodb.yml restart mongodb

# Reset MongoDB data (WARNING: Deletes data)
docker volume rm optik_mongodb_data
docker-compose -f docker-compose.mongodb.yml up -d mongodb
```

---

## MongoDB Atlas (Cloud)

### Setup on MongoDB Atlas

**1. Create Account**
- Go to https://www.mongodb.com/cloud/atlas
- Sign up for free account

**2. Create Cluster**
- Click "Create a Database"
- Choose free tier
- Select region (recommend same as your app)
- Create cluster

**3. Set Up User**
- Go to Database Access
- Click "Add New Database User"
- Username: optik_user
- Password: Generate secure password
- Database User Privileges: readWrite on any database
- Click "Add User"

**4. Whitelist IP**
- Go to Network Access
- Click "Add IP Address"
- Choose "Allow Access from Anywhere" (0.0.0.0/0) for development
- In production: Add specific IP ranges

**5. Get Connection String**
- Click "Connect" on cluster
- Choose "Connect your application"
- Copy connection string
- Should look like: `mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority`

**6. Configure Environment**

```bash
# Update .env file
MONGODB_URL=mongodb+srv://optik_user:your_password@cluster.mongodb.net/optik?retryWrites=true&w=majority
MONGODB_DB_NAME=optik
```

### Benefits of MongoDB Atlas

✅ Free tier (512MB storage)
✅ Automatic backups
✅ Monitoring & analytics
✅ Auto-scaling
✅ Enterprise security
✅ Global clusters

---

## Configuration

### Environment Variables

See `.env.mongodb` for all configuration options:

```bash
# Connection String
MONGODB_URL=mongodb://localhost:27017

# Database Name
MONGODB_DB_NAME=optik

# Connection Pool
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=10

# Timeouts (ms)
MONGODB_CONNECT_TIMEOUT=5000
MONGODB_SOCKET_TIMEOUT=5000

# Authentication
MONGODB_USER=optik_user
MONGODB_PASSWORD=your_secure_password

# Replica Set (for production)
MONGODB_REPLICA_SET=rs0
```

### Collection Schemas

**Jobs Collection:**
```javascript
{
  id: string,           // Unique ID
  user_id: string,      // User identifier
  store_url: string,    // E-commerce store URL
  platform: string,     // 'shopify' | 'woocommerce' | 'custom'
  tier: string,         // Service tier
  status: string,       // 'pending' | 'processing' | 'completed' | 'failed'
  message: string,      // Status message
  error?: string,       // Error message if failed
  deployment_config?: object,
  created_at: date,
  updated_at: date
}
```

**Products Collection:**
```javascript
{
  id: string,
  user_id: string,
  name: string,
  description?: string,
  supply: string,       // Quantity or "Unlimited"
  sold: number,         // Units sold
  price: string,        // Price string (e.g., "0.5 SOL")
  status: string,       // 'Live' | 'Draft' | 'Sold Out'
  created_at: date,
  updated_at: date
}
```

---

## Testing

### Test MongoDB Connection

**1. Using Python**

```python
from utils.mongo_db import mongodb
import asyncio

async def test_connection():
    connected = await mongodb.connect()
    if connected:
        print("✅ Connected to MongoDB")

        # Check health
        health = await mongodb.health_check()
        print(health)

        await mongodb.disconnect()
    else:
        print("❌ Failed to connect")

asyncio.run(test_connection())
```

**2. Using MongoDB Shell**

```bash
# Local
mongosh

# Docker
docker exec -it optik-mongodb mongosh -u optik_admin -p secure_password_change_me

# Commands
show dbs
use optik
show collections
db.jobs.countDocuments()
```

**3. Using Python Script**

```bash
python -c "
from utils.mongo_db import mongodb
import asyncio

async def main():
    result = await mongodb.health_check()
    print(result)

asyncio.run(main())
"
```

### Test CRUD Operations

```python
from utils.mongo_db import JobRepository, ProductRepository
import asyncio

async def test_crud():
    # Connect first
    from utils.mongo_db import mongodb
    await mongodb.connect()

    # Test Job CRUD
    job_repo = JobRepository()

    # Create
    job_id = await job_repo.create({
        "user_id": "test_user",
        "store_url": "https://test.com",
        "platform": "shopify",
        "status": "pending",
        "message": "Testing..."
    })
    print(f"Created job: {job_id}")

    # Read
    job = await job_repo.read_by_id(job_id)
    print(f"Retrieved job: {job}")

    # Update
    updated = await job_repo.update_by_id(job_id, {
        "status": "completed",
        "message": "Test complete"
    })
    print(f"Updated: {updated}")

    # Delete
    deleted = await job_repo.delete_by_id(job_id)
    print(f"Deleted: {deleted}")

    await mongodb.disconnect()

asyncio.run(test_crud())
```

---

## Troubleshooting

### Connection Issues

**Error: "Connection refused"**
```bash
# Check if MongoDB is running
mongosh

# Start MongoDB
brew services start mongodb-community@7.0  # macOS
sudo systemctl start mongod  # Linux
```

**Error: "Authentication failed"**
```bash
# Check credentials in .env
# Verify user exists in MongoDB
mongosh -u optik_admin -p secure_password_change_me --authenticationDatabase admin

# Create user if missing
db.createUser({
  user: "optik_user",
  pwd: "optik_password_change_me",
  roles: [{ role: "readWrite", db: "optik" }]
})
```

**Error: "Timeout connecting to server"**
```bash
# Increase timeout in .env
MONGODB_CONNECT_TIMEOUT=10000
MONGODB_SOCKET_TIMEOUT=10000

# Check firewall
# Ensure port 27017 is open
```

### Docker Issues

**Error: "Cannot connect to mongodb service from api"**
```bash
# Verify services are running
docker-compose -f docker-compose.mongodb.yml ps

# Check network
docker network inspect optik_optik-network

# Restart services
docker-compose -f docker-compose.mongodb.yml restart
```

**Error: "Mongo Express cannot connect"**
```bash
# Check MongoDB is healthy
docker healthcheck optik-mongodb

# Verify credentials in docker-compose
# Check MongoDB logs
docker logs optik-mongodb
```

### Performance Issues

**Slow queries:**
```bash
# Verify indexes exist
mongosh
db.jobs.getIndexes()

# Rebuild indexes if needed
db.jobs.reIndex()
```

**High memory usage:**
```bash
# Check memory stats
docker stats optik-mongodb

# Increase Docker memory limit in docker-compose.yml
# services:
#   mongodb:
#     deploy:
#       resources:
#         limits:
#           memory: 2G
```

---

## Production Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Network access configured (IP whitelisting)
- [ ] Database user created with least privileges
- [ ] Connection string secured in secrets manager
- [ ] Backups enabled
- [ ] Monitoring enabled
- [ ] Read replicas configured (optional)
- [ ] Performance indexes created
- [ ] Authentication required
- [ ] TLS/SSL enabled
- [ ] VPC peering configured (if needed)
- [ ] Load testing completed

---

## Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [MongoDB University](https://university.mongodb.com/)

---

**Last Updated:** February 15, 2026
**MongoDB Version:** 7.0+
**Status:** ✅ Production Ready
