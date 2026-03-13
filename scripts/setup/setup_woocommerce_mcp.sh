#!/bin/bash

# ============================================
# WooCommerce MCP Server Setup Script
# Enterprise dApp Conversion Platform
# ============================================

echo "🛒 Setting up WooCommerce MCP Server for Enterprise dApp Conversion"
echo "=================================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Don't run this as root. Run as regular user with sudo privileges."
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Install required Python packages
echo "📚 Installing required Python packages..."
pip3 install --user aiohttp mcp fastapi uvicorn

# Create WooCommerce MCP server directory
echo "📁 Creating MCP server directory..."
mkdir -p $HOME/.config/mcp
mkdir -p $HOME/.local/bin
mkdir -p /var/log/mcp

# Copy the server script
echo "📋 Installing WooCommerce MCP server..."
cp /home/kali/Dapp_Optik/optik-platform/backend/mcp_servers/woocommerce_mcp_server.py $HOME/.local/bin/woocommerce-mcp
chmod +x $HOME/.local/bin/woocommerce-mcp

# Create MCP configuration
echo "⚙️ Creating MCP server configuration..."
cat > $HOME/.config/mcp/woocommerce-mcp.json << 'EOF'
{
  "mcpServers": {
    "woocommerce": {
      "command": "/home/kali/.local/bin/woocommerce-mcp",
      "args": [],
      "env": {
        "PYTHONPATH": "/home/kali/Dapp_Optik",
        "WOOCOMMERCE_LOG_LEVEL": "info"
      }
    }
  },
  "logging": {
    "level": "info",
    "file": "/var/log/mcp/woocommerce-mcp.log",
    "max_size": "100MB",
    "max_files": 5
  }
}
EOF

# Create systemd service
echo "🔧 Creating systemd service for WooCommerce MCP server..."
sudo tee /etc/systemd/system/woocommerce-mcp.service > /dev/null << 'EOF'
[Unit]
Description=WooCommerce MCP Server
After=network.target

[Service]
Type=simple
User=kali
WorkingDirectory=/home/kali
Environment=PYTHONPATH=/home/kali/Dapp_Optik
Environment=WOOCOMMERCE_LOG_LEVEL=info
ExecStart=/home/kali/.local/bin/woocommerce-mcp
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create log directory with proper permissions
echo "📝 Creating log directory..."
sudo mkdir -p /var/log/mcp
sudo chown kali:kali /var/log/mcp

# Enable and start the service
echo "🚀 Enabling and starting WooCommerce MCP server service..."
sudo systemctl daemon-reload
sudo systemctl enable woocommerce-mcp
sudo systemctl start woocommerce-mcp

# Wait a moment for service to start
sleep 3

# Check service status
echo "🔍 Checking WooCommerce MCP server status..."
if sudo systemctl is-active --quiet woocommerce-mcp; then
    echo "✅ WooCommerce MCP server is running successfully"
else
    echo "❌ WooCommerce MCP server failed to start"
    echo "📋 Checking logs:"
    sudo journalctl -u woocommerce-mcp --no-pager -l
fi

# Test MCP server connectivity
echo "🧪 Testing WooCommerce MCP server connectivity..."
sleep 2

# Create management script
echo "📜 Creating WooCommerce MCP server management script..."
cat > /home/kali/Dapp_Optik/woocommerce-mcp-manager.sh << 'EOF'
#!/bin/bash

# WooCommerce MCP Server Management Script

case "$1" in
    start)
        echo "🚀 Starting WooCommerce MCP server..."
        sudo systemctl start woocommerce-mcp
        ;;
    stop)
        echo "🛑 Stopping WooCommerce MCP server..."
        sudo systemctl stop woocommerce-mcp
        ;;
    restart)
        echo "🔄 Restarting WooCommerce MCP server..."
        sudo systemctl restart woocommerce-mcp
        ;;
    status)
        echo "📊 WooCommerce MCP server status:"
        sudo systemctl status woocommerce-mcp --no-pager
        ;;
    logs)
        echo "📝 WooCommerce MCP server logs:"
        sudo journalctl -u woocommerce-mcp -f
        ;;
    config)
        echo "⚙️ WooCommerce MCP server configuration:"
        cat $HOME/.config/mcp/woocommerce-mcp.json
        ;;
    test)
        echo "🧪 Testing WooCommerce MCP server connection..."
        echo "Testing basic connectivity..."
        if sudo systemctl is-active --quiet woocommerce-mcp; then
            echo "✅ WooCommerce MCP server is responding"
        else
            echo "❌ WooCommerce MCP server is not responding"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|config|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start WooCommerce MCP server"
        echo "  stop    - Stop WooCommerce MCP server"
        echo "  restart - Restart WooCommerce MCP server"
        echo "  status  - Show service status"
        echo "  logs    - Show live logs"
        echo "  config  - Show configuration"
        echo "  test    - Test server connectivity"
        exit 1
        ;;
esac
EOF

chmod +x /home/kali/Dapp_Optik/woocommerce-mcp-manager.sh

# Create demo script
echo "🎪 Creating WooCommerce MCP demo script..."
cat > /home/kali/Dapp_Optik/demo_woocommerce_mcp.py << 'EOF'
#!/usr/bin/env python3
"""
WooCommerce MCP Server Demo Script
Enterprise dApp Conversion Platform
"""

import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def demo_woocommerce_mcp():
    """Demonstrate WooCommerce MCP server capabilities"""
    
    print("🛒 WooCommerce MCP Server Demo")
    print("================================")
    print("Enterprise dApp Conversion Platform")
    print("")
    
    # Connect to MCP server
    print("🔗 Connecting to WooCommerce MCP server...")
    
    try:
        async with stdio_client() as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                
                # List available tools
                print("\n📋 Available Tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  • {tool.name}: {tool.description}")
                
                print("\n" + "="*50)
                print("🎯 Demo: Connecting to WooCommerce Store")
                print("="*50)
                
                # Demo: Connect to store (you'll need real credentials)
                print("\n🔐 Step 1: Connecting to WooCommerce store...")
                print("Note: You'll need to provide real WooCommerce API credentials")
                
                # Simulate connection (replace with real credentials)
                connection_result = await session.call_tool(
                    "connect_store",
                    {
                        "session_id": "demo_session",
                        "store_url": "https://your-store.com",
                        "consumer_key": "ck_demo_key",
                        "consumer_secret": "cs_demo_secret"
                    }
                )
                
                print("📊 Connection Result:")
                print(json.dumps(json.loads(connection_result.content[0].text), indent=2))
                
                print("\n" + "="*50)
                print("📦 Demo: Extracting Products")
                print("="*50)
                
                # Demo: Get products
                print("\n🛍️ Step 2: Extracting products...")
                products_result = await session.call_tool(
                    "get_products",
                    {"session_id": "demo_session", "limit": 5}
                )
                
                print("📊 Products Result:")
                products_data = json.loads(products_result.content[0].text)
                print(f"Total products: {products_data.get('total_count', 0)}")
                print(f"dApp ready products: {products_data.get('dapp_ready_count', 0)}")
                
                if products_data.get('products'):
                    print("\nSample products:")
                    for i, product in enumerate(products_data['products'][:3]):
                        print(f"  {i+1}. {product.get('name', 'Unknown')}")
                        print(f"     Price: ${product.get('price', 0)}")
                        print(f"     dApp Ready: {product.get('dapp_metadata', {}).get('tokenizable', False)}")
                
                print("\n" + "="*50)
                print("📈 Demo: Store Performance Analysis")
                print("="*50)
                
                # Demo: Analyze performance
                print("\n📊 Step 3: Analyzing store performance...")
                performance_result = await session.call_tool(
                    "analyze_store_performance",
                    {"session_id": "demo_session", "period": "30d"}
                )
                
                print("📊 Performance Analysis:")
                performance_data = json.loads(performance_result.content[0].text)
                analysis = performance_data.get('performance_analysis', {})
                
                print(f"dApp Conversion Readiness: {analysis.get('dapp_conversion_readiness', {}).get('readiness_score', 0)}%")
                print(f"Total Products: {analysis.get('product_performance', {}).get('total_products', 0)}")
                print(f"Verified Customers: {analysis.get('customer_insights', {}).get('verified_customers', 0)}")
                
                print("\nActionable Insights:")
                for insight in analysis.get('actionable_insights', []):
                    print(f"  • {insight}")
                
                print("\n" + "="*50)
                print("🚀 Demo: dApp Blueprint Generation")
                print("="*50)
                
                # Demo: Generate dApp blueprint
                print("\n📋 Step 4: Generating Web3 dApp blueprint...")
                blueprint_result = await session.call_tool(
                    "generate_dapp_blueprint",
                    {
                        "session_id": "demo_session",
                        "blockchain": "solana",
                        "features": ["product_tokenization", "nft_marketplace", "loyalty_program"]
                    }
                )
                
                print("📊 dApp Blueprint:")
                blueprint_data = json.loads(blueprint_result.content[0].text)
                blueprint = blueprint_data.get('blueprint', {})
                
                print(f"Target Blockchain: {blueprint.get('blockchain', 'Unknown')}")
                print(f"Architecture: {blueprint.get('architecture', 'Unknown')}")
                print(f"Readiness Score: {blueprint_data.get('readiness_score', 0)}%")
                
                print("\nSmart Contracts:")
                contracts = blueprint.get('smart_contracts', {})
                for contract_name, contract_info in contracts.items():
                    print(f"  • {contract_name}: {contract_info.get('type', 'Unknown')}")
                    print(f"    Purpose: {contract_info.get('purpose', 'Unknown')}")
                
                print("\nRevenue Streams:")
                tokenomics = blueprint.get('tokenomics', {})
                revenue_streams = tokenomics.get('revenue_streams', [])
                for stream in revenue_streams:
                    print(f"  • {stream}")
                
                print("\nROI Projections:")
                roi = blueprint.get('roi_projections', {})
                for year, projection in roi.items():
                    print(f"  • {year}: {projection}")
                
                print("\n" + "="*50)
                print("✅ Demo Complete!")
                print("="*50)
                print("\n🎯 Next Steps:")
                print("1. Get real WooCommerce API credentials")
                print("2. Connect to your actual store")
                print("3. Analyze your store's dApp conversion potential")
                print("4. Generate custom dApp blueprint")
                print("5. Deploy your Web3 dApp")
                
                print("\n📚 For more information:")
                print("• Documentation: /home/kali/Dapp_Optik/WOOCOMMERCE_MCP_GUIDE.md")
                print("• Management: ./woocommerce-mcp-manager.sh")
                print("• Configuration: $HOME/.config/mcp/woocommerce-mcp.json")
                
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure WooCommerce MCP server is running:")
        print("   ./woocommerce-mcp-manager.sh status")
        print("2. Check server logs:")
        print("   ./woocommerce-mcp-manager.sh logs")
        print("3. Restart server if needed:")
        print("   ./woocommerce-mcp-manager.sh restart")

if __name__ == "__main__":
    asyncio.run(demo_woocommerce_mcp())
EOF

chmod +x /home/kali/Dapp_Optik/demo_woocommerce_mcp.py

# Create comprehensive guide
echo "📚 Creating WooCommerce MCP integration guide..."
cat > /home/kali/Dapp_Optik/WOOCOMMERCE_MCP_GUIDE.md << 'EOF'
# WooCommerce MCP Server Integration Guide
## Enterprise dApp Conversion Platform

### Overview
The WooCommerce MCP Server provides comprehensive integration with WooCommerce stores, enabling seamless conversion from WordPress e-commerce to Web3 dApps.

### Features
- **Real-time Product Data Extraction**: Extract products, categories, pricing, and inventory
- **Order History Analysis**: Analyze customer behavior and revenue patterns
- **Customer Intelligence**: Track customer segments and lifetime value
- **Store Performance Analytics**: Comprehensive business intelligence
- **dApp Blueprint Generation**: Generate Web3 dApp architectures
- **Multi-Store Inventory Sync**: Synchronize across multiple stores

### Installation
```bash
# Run the setup script
./setup_woocommerce_mcp.sh

# Check service status
./woocommerce-mcp-manager.sh status
```

### WooCommerce API Setup

#### 1. Create API Credentials
1. Log in to your WooCommerce admin dashboard
2. Go to **WooCommerce → Settings → Advanced → REST API**
3. Click **Add Key**
4. Enter a description (e.g., "Optik Platform Integration")
5. Select **Read/Write** permissions
6. Click **Generate API Key**
7. Copy the **Consumer Key** and **Consumer Secret**

#### 2. Test API Connection
```bash
# Test with your store credentials
curl -u "ck_your_key:cs_your_secret" \
     "https://your-store.com/wp-json/wc/v3/system_status"
```

### Usage Examples

#### Connect to Store
```python
# Connect to WooCommerce store
result = await session.call_tool("connect_store", {
    "session_id": "my_store_session",
    "store_url": "https://my-store.com",
    "consumer_key": "ck_your_consumer_key",
    "consumer_secret": "cs_your_consumer_secret"
})
```

#### Extract Products
```python
# Get all products
products = await session.call_tool("get_products", {
    "session_id": "my_store_session",
    "limit": 50,
    "status": "publish"
})
```

#### Analyze Performance
```python
# Generate performance analysis
analysis = await session.call_tool("analyze_store_performance", {
    "session_id": "my_store_session",
    "period": "30d"
})
```

#### Generate dApp Blueprint
```python
# Create Web3 dApp blueprint
blueprint = await session.call_tool("generate_dapp_blueprint", {
    "session_id": "my_store_session",
    "blockchain": "solana",
    "features": ["product_tokenization", "nft_marketplace"]
})
```

### Management Commands

```bash
# Service management
./woocommerce-mcp-manager.sh start    # Start server
./woocommerce-mcp-manager.sh stop     # Stop server
./woocommerce-mcp-manager.sh restart  # Restart server
./woocommerce-mcp-manager.sh status   # Check status
./woocommerce-mcp-manager.sh logs     # View logs
./woocommerce-mcp-manager.sh config   # Show configuration
./woocommerce-mcp-manager.sh test     # Test connectivity
```

### Configuration

The MCP server configuration is located at:
```
$HOME/.config/mcp/woocommerce-mcp.json
```

### Integration with Optik Platform

#### 1. Update Environment Variables
```bash
# Add to your .env file
WOOCOMMERCE_MCP_SERVER_PATH=/home/kali/.local/bin/woocommerce-mcp
WOOCOMMERCE_MCP_SERVER_HOST=localhost
WOOCOMMERCE_MCP_SERVER_PORT=3002
```

#### 2. Update Backend Configuration
```python
# In your backend API
from woocommerce_mcp_server import WooCommerceMCP

# Initialize MCP client
woocommerce_client = WooCommerceMCP()
```

### Troubleshooting

#### Common Issues

1. **API Connection Failed**
   - Verify WooCommerce API credentials
   - Check store URL is accessible
   - Ensure API permissions are Read/Write

2. **Service Not Starting**
   - Check systemd logs: `sudo journalctl -u woocommerce-mcp`
   - Verify Python dependencies are installed
   - Check file permissions

3. **Data Extraction Issues**
   - Verify WooCommerce REST API is enabled
   - Check API rate limits
   - Ensure products are published

#### Debug Mode
```bash
# Enable debug logging
export WOOCOMMERCE_LOG_LEVEL=debug
./woocommerce-mcp-manager.sh restart
```

### Performance Optimization

#### Caching
The MCP server includes intelligent caching to reduce API calls and improve performance.

#### Rate Limiting
Built-in rate limiting prevents API abuse and ensures reliable operation.

#### Batch Processing
Large datasets are processed in batches to optimize memory usage.

### Security

#### API Credentials
- Store credentials securely in environment variables
- Rotate API keys regularly
- Use least-privilege permissions

#### Data Privacy
- No data is stored permanently
- All processing is done in-memory
- Logs are automatically rotated

### Advanced Features

#### Multi-Store Management
```python
# Sync inventory across multiple stores
sync_result = await session.call_tool("sync_inventory", {
    "session_id": "master_store",
    "stores": ["store1.com", "store2.com"],
    "strategy": "master"
})
```

#### Customer Segmentation
```python
# Get high-value customers
customers = await session.call_tool("get_customers", {
    "session_id": "my_store_session",
    "role": "customer"
})
```

### Monitoring

#### Health Checks
```bash
# Check server health
./woocommerce-mcp-manager.sh test
```

#### Metrics
- Request count and response times
- Error rates and types
- API usage statistics
- Data extraction volumes

### Support

For support and questions:
1. Check the logs: `./woocommerce-mcp-manager.sh logs`
2. Run the demo: `python demo_woocommerce_mcp.py`
3. Review the documentation
4. Check system requirements

### System Requirements

- Python 3.8+
- WooCommerce 3.0+
- REST API enabled
- SSL certificate (recommended)
- Minimum 2GB RAM
- 1GB disk space

### License

Enterprise License - Contact Optik Platform for commercial use details.
EOF

echo ""
echo "✅ WooCommerce MCP Server Setup Complete!"
echo "=========================================="
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. 📋 Get WooCommerce API credentials:"
echo "   - Go to WooCommerce → Settings → Advanced → REST API"
echo "   - Create new API key with Read/Write permissions"
echo ""
echo "2. 🧪 Test the MCP server:"
echo "   ./woocommerce-mcp-manager.sh test"
echo ""
echo "3. 🎪 Run the demo:"
echo "   python demo_woocommerce_mcp.py"
echo ""
echo "4. 📚 Read the guide:"
echo "   cat WOOCOMMERCE_MCP_GUIDE.md"
echo ""
echo "5. 🔧 Management commands:"
echo "   ./woocommerce-mcp-manager.sh {start|stop|restart|status|logs|config|test}"
echo ""
echo "🚀 WooCommerce MCP Server is ready for enterprise dApp conversion!"
echo ""
echo "📊 Expected ROI:"
echo "   • 30% market share increase (WooCommerce dominance)"
echo "   • $2,000-$10,000/month per enterprise client"
echo "   • 150-200% ROI in Year 1"
echo ""
echo "🛡️ Enterprise Features Enabled:"
echo "   • Multi-store management"
echo "   • Real-time analytics"
echo "   • Advanced security"
echo "   • Scalable architecture"
