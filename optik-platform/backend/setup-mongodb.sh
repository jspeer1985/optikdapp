#!/bin/bash

# ============================================
# Optik Platform - MongoDB Setup Script
# ============================================

set -e

echo "🚀 Optik Platform - MongoDB Setup"
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose detected${NC}"

# Ask user for setup method
echo ""
echo "Choose setup method:"
echo "1. Docker Compose (Recommended)"
echo "2. Local MongoDB installation"
echo "3. MongoDB Atlas (Cloud)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🐳 Setting up with Docker Compose..."

        # Check if docker daemon is running
        if ! docker ps &> /dev/null; then
            echo -e "${RED}❌ Docker daemon is not running${NC}"
            echo "Please start Docker and try again"
            exit 1
        fi

        echo -e "${GREEN}✅ Docker daemon is running${NC}"

        # Pull latest images
        echo "📥 Pulling Docker images..."
        docker-compose -f docker-compose.mongodb.yml pull

        # Start services
        echo "🚀 Starting MongoDB, Redis, and API services..."
        docker-compose -f docker-compose.mongodb.yml up -d

        # Wait for MongoDB to be ready
        echo "⏳ Waiting for MongoDB to be ready..."
        sleep 10

        # Check if MongoDB is healthy
        if docker-compose -f docker-compose.mongodb.yml ps | grep -q "optik-mongodb"; then
            echo -e "${GREEN}✅ MongoDB container is running${NC}"
        else
            echo -e "${RED}❌ MongoDB container failed to start${NC}"
            docker-compose -f docker-compose.mongodb.yml logs mongodb
            exit 1
        fi

        echo ""
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo ""
        echo "📊 Services:"
        echo "  MongoDB:       mongodb://optik_admin:secure_password_change_me@localhost:27017"
        echo "  Mongo Express: http://localhost:8081 (admin / admin)"
        echo "  Redis:         redis://localhost:6379"
        echo "  API Docs:      http://localhost:8000/docs"
        echo ""
        echo "Useful commands:"
        echo "  docker-compose -f docker-compose.mongodb.yml logs -f optik-api"
        echo "  docker-compose -f docker-compose.mongodb.yml down"
        echo ""
        ;;

    2)
        echo ""
        echo "📦 Setting up with Local MongoDB..."

        # Detect OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "🐧 Detected Linux"
            echo ""
            echo "To install MongoDB on Linux, run:"
            echo ""
            echo "curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -"
            echo "echo 'deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list"
            echo "sudo apt-get update"
            echo "sudo apt-get install -y mongodb-org"
            echo "sudo systemctl start mongod"
            echo ""

        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "🍎 Detected macOS"
            echo ""

            if ! command -v brew &> /dev/null; then
                echo -e "${RED}❌ Homebrew is not installed${NC}"
                echo "Install Homebrew from: https://brew.sh"
                exit 1
            fi

            echo -e "${GREEN}✅ Homebrew detected${NC}"
            echo ""
            echo "Installing MongoDB with Homebrew..."

            brew tap mongodb/brew
            brew install mongodb-community@7.0
            brew services start mongodb-community@7.0

            echo -e "${GREEN}✅ MongoDB installed and started${NC}"

        else
            echo -e "${YELLOW}⚠️  Unsupported OS${NC}"
            echo "Please install MongoDB manually from: https://www.mongodb.com/try/download/community"
            exit 1
        fi

        # Test connection
        echo ""
        echo "Testing MongoDB connection..."
        sleep 2

        if mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
            echo -e "${GREEN}✅ MongoDB connection successful${NC}"
        else
            echo -e "${RED}❌ MongoDB connection failed${NC}"
            exit 1
        fi

        # Copy environment file
        echo ""
        echo "Setting up environment..."
        if [ ! -f ".env" ]; then
            cp .env.mongodb .env
            echo -e "${GREEN}✅ Created .env file (modify MONGODB_URL if needed)${NC}"
        else
            echo -e "${YELLOW}⚠️  .env file already exists${NC}"
        fi

        # Install Python dependencies
        echo ""
        echo "Installing Python dependencies..."
        pip install motor pymongo

        echo -e "${GREEN}✅ Dependencies installed${NC}"

        echo ""
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo ""
        echo "To start the API:"
        echo "  uvicorn api.main:app --reload"
        echo ""
        ;;

    3)
        echo ""
        echo "☁️  Setting up with MongoDB Atlas..."
        echo ""
        echo "1. Go to https://www.mongodb.com/cloud/atlas"
        echo "2. Create a free account"
        echo "3. Create a cluster"
        echo "4. Create a database user"
        echo "5. Whitelist your IP"
        echo "6. Get your connection string"
        echo ""
        echo "Then update .env with your connection string:"
        echo "  MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/optik"
        echo ""
        ;;

    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "📖 For more information, see: MONGODB_SETUP.md"
