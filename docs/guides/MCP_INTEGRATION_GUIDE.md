# 🔌 MCP Server Integration Guide

## 📋 Overview

This guide covers the complete setup and integration of the Shopify MCP (Model Context Protocol) server with the Optik Platform for production use.

## 🎯 What is MCP Server Integration?

The MCP server provides direct access to Shopify's GraphQL Admin API, enabling:
- **Real-time data scraping** from Shopify stores
- **Conversion analytics** and metrics extraction
- **Product, customer, and order management**
- **AI-powered analysis** of store performance
- **dApp integration** recommendations

## 🚀 Quick Setup

### 1. Install MCP Server
```bash
# Run the setup script
./setup_mcp_server.sh
```

### 2. Update Configuration
```bash
# Update all placeholder values to production
./update_config_to_production.sh
```

### 3. Manual Configuration Updates
Edit `/home/kali/Dapp_Optik/optik-platform/backend/.env` and replace:

#### 🔑 API Keys
```env
# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXX
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXX

# Shopify (Get from Shopify Admin → Apps → Custom App)
SHOPIFY_API_KEY=shp_live_XXXXXXXXXXXXXXXXXXXX
SHOPIFY_API_SECRET=shp_live_XXXXXXXXXXXXXXXXXXXX
```

#### 🔐 Blockchain Keys
```env
# Solana (Generate with: solana-keygen new)
SOLANA_WALLET_PRIVATE_KEY=your_base58_private_key
TREASURY_WALLET=your_public_wallet_address
```

#### 🗄️ Database
```env
# PostgreSQL Production
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
REDIS_URL=redis://host:port/db
```

#### ☁️ AWS (Optional)
```env
USE_AWS_SECRETS=true
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

## 🔧 MCP Server Configuration

### Server Settings
```json
{
  "server": {
    "host": "localhost",
    "port": 3001,
    "workers": 4,
    "timeout": 30,
    "max_connections": 100
  }
}
```

### Shopify Integration
```json
{
  "shopify": {
    "api_version": "2026-01",
    "rate_limit": {
      "requests_per_minute": 60,
      "burst_size": 10
    },
    "cache": {
      "enabled": true,
      "ttl": 300
    }
  }
}
```

## 🛠 Shopify App Setup

### 1. Create Custom App
1. Go to **Shopify Admin** → **Settings** → **Apps and sales channels**
2. Click **Develop apps** → **Build app**
3. Set app name: "Optik Platform Integration"

### 2. Configure API Scopes
Required permissions:
- ✅ `read_products`
- ✅ `write_products`
- ✅ `read_customers`
- ✅ `write_customers`
- ✅ `read_orders`
- ✅ `write_orders`
- ✅ `read_inventory`
- ✅ `write_inventory`

### 3. Install App
1. Click **Install app**
2. Select your store
3. Copy **Client ID** and **Client Secret**

### 4. Get Credentials
```env
SHOPIFY_API_KEY=shp_live_xxxxxxxxxxxxxxxxxxxxxx
SHOPIFY_API_SECRET=shp_live_xxxxxxxxxxxxxxxxxxxxxx
```

## 🚀 MCP Server Management

### Start/Stop Server
```bash
# Start MCP server
./mcp-manager.sh start

# Stop MCP server
./mcp-manager.sh stop

# Restart MCP server
./mcp-manager.sh restart

# Check status
./mcp-manager.sh status

# View logs
./mcp-manager.sh logs

# Test connectivity
./mcp-manager.sh test
```

### Systemd Service
```bash
# Enable auto-start
sudo systemctl enable shopify-mcp

# Check service status
sudo systemctl status shopify-mcp

# View logs
sudo journalctl -u shopify-mcp -f
```

## 🔌 API Integration

### Shopify Scraping Endpoints

#### Single Store Scrape
```bash
curl -X POST "http://localhost:8000/api/shopify-scraping/scrape-single" \
  -H "Content-Type: application/json" \
  -d '{
    "store_domain": "your-store.myshopify.com",
    "client_id": "shp_live_xxxxxxxxxxxxxxxxxxxxxx",
    "client_secret": "shp_live_xxxxxxxxxxxxxxxxxxxxxx",
    "store_name": "Your Store Name"
  }'
```

#### Batch Scrape
```bash
curl -X POST "http://localhost:8000/api/shopify-scraping/scrape-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "stores": [
      {
        "store_domain": "store1.myshopify.com",
        "client_id": "client_id_1",
        "client_secret": "client_secret_1"
      },
      {
        "store_domain": "store2.myshopify.com",
        "client_id": "client_id_2",
        "client_secret": "client_secret_2"
      }
    ]
  }'
```

#### dApp Integration
```bash
curl "http://localhost:8000/api/dapp-integration/store-profile/your-store.myshopify.com"
```

## 📊 Data Structure

### ConversionData Model
```typescript
interface ConversionData {
  store_domain: string;
  conversion_rate: float;
  average_order_value: float;
  total_revenue: float;
  total_orders: int;
  unique_visitors: int;
  cart_abandonment_rate: float;
  customer_lifetime_value: float;
  top_products: ProductData[];
  traffic_sources: Record<string, float>;
  conversion_funnel: FunnelData;
  product_performance: ProductPerformance[];
  customer_segments: CustomerSegment[];
}
```

### dApp Features Available
1. **Loyalty Programs** - Token-based rewards
2. **Cart Recovery** - NFT incentives
3. **NFT Collectibles** - Premium digital items
4. **Token Rewards** - Purchase incentives
5. **Gamification** - Achievement systems

## 🔍 Testing Integration

### Test MCP Server
```bash
# Test MCP server connectivity
curl -s http://localhost:3001/health

# Test Shopify API connection
curl -X POST "http://localhost:8000/api/shopify-scraping/scraping-status"
```

### Test Frontend Integration
```bash
# Check frontend
curl -s http://localhost:3003/ | grep -o '<title[^>]*>.*</title>'

# Test backend
curl -s http://localhost:8000/health
```

### Test Complete Flow
```bash
# Run comprehensive test
python demo_shopify_scraping.py
```

## 🚨 Troubleshooting

### Common Issues

#### MCP Server Not Starting
```bash
# Check logs
sudo journalctl -u shopify-mcp -n 20

# Check configuration
cat ~/.config/mcp/shopify-mcp.json

# Restart service
sudo systemctl restart shopify-mcp
```

#### Shopify API Errors
```bash
# Verify credentials
curl -X SHOPIFY_WEBHOOK_ENDPOINT=https://optikcoin.com/api/webhooks/shopify.com/admin/api_permissions/current.json" \
  -H "X-Shopify-Access-Token: your_access_token"

# Check rate limits
curl -I https://your-store.myshopify.com/admin/api/2024-01/graphql.json
```

#### Backend Integration Issues
```bash
# Check backend logs
tail -f /home/kali/Dapp_Optik/optik-platform/backend/backend.log

# Test MCP connection
curl -s http://localhost:8000/api/shopify-scraping/scraping-status
```

## 📈 Performance Optimization

### MCP Server Optimization
```json
{
  "server": {
    "workers": 8,
    "max_connections": 200,
    "timeout": 60
  },
  "cache": {
    "enabled": true,
    "ttl": 600,
    "max_size": "1GB"
  }
}
```

### Rate Limiting
```env
RATE_LIMIT_PER_MINUTE=120
RATE_LIMIT_PER_HOUR=2000
RATE_LIMIT_BURST_SIZE=20
```

### Database Optimization
```env
# Connection pooling
REDIS_MAX_CONNECTIONS=100

# Cache settings
REDIS_TTL=3600
```

## 🔒 Security Best Practices

### Environment Variables
- ✅ Use strong, unique secrets
- ✅ Rotate credentials every 90 days
- ✅ Never commit .env to version control
- ✅ Use AWS Secrets Manager when possible

### API Security
- ✅ Use HTTPS in production
- ✅ Implement rate limiting
- ✅ Validate all inputs
- ✅ Monitor for suspicious activity

### Shopify Security
- ✅ Use custom apps, not private apps
- ✅ Limit API scopes to minimum required
- ✅ Monitor API usage
- ✅ Revoke unused credentials

## 📚 API Documentation

### Available Endpoints

#### Shopify Scraping
- `POST /api/shopify-scraping/scrape-single` - Scrape single store
- `POST /api/shopify-scraping/scrape-batch` - Scrape multiple stores
- `GET /api/shopify-scraping/scraping-status` - Check system status
- `GET /api/shopify-scraping/export-dapp-data` - Export for dApp integration

#### dApp Integration
- `GET /api/dapp-integration/store-profile/{domain}` - Generate store profile
- `GET /api/dapp-integration/market-analysis` - Market-wide analysis
- `GET /api/dapp-integration/feature-types` - Available features
- `GET /api/dapp-integration/roi-calculator` - Calculate ROI

### Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🚀 Production Deployment

### Pre-Deployment Checklist
- [ ] All placeholder values replaced
- [ ] MCP server installed and running
- [ ] Shopify apps configured
- [ ] Database connections tested
- [ ] SSL certificates installed
- [ ] Rate limiting configured
- [ ] Monitoring enabled

### Deployment Steps
```bash
# 1. Update configuration
./update_config_to_production.sh

# 2. Install MCP server
./setup_mcp_server.sh

# 3. Test integration
python demo_shopify_scraping.py

# 4. Start services
sudo systemctl start shopify-mcp
./start-dev.sh

# 5. Verify deployment
curl -s http://localhost:8000/health
curl -s http://localhost:3003/
```

## 🎯 Success Metrics

### Performance Targets
- **API Response Time**: < 2 seconds
- **Scraping Accuracy**: > 95%
- **Uptime**: > 99.9%
- **Error Rate**: < 0.1%

### Business Metrics
- **Stores Processed**: 1000+
- **Data Accuracy**: > 98%
- **Customer Satisfaction**: > 4.5/5
- **ROI Generation**: > 300%

---

## 🎉 Ready for Production!

Your Optik Platform is now fully integrated with the Shopify MCP server and ready for production deployment with real data processing capabilities! 🚀
