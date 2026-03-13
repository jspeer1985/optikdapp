#!/bin/bash

# ============================================
# MCP Server Setup and Installation Script
# ============================================

echo "🚀 Setting up MCP Server for Optik Platform"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this as root. Use a regular user with sudo privileges."
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y curl wget git python3 python3-pip python3-venv build-essential

# Install Shopify MCP Server globally
echo "🛒 Installing Shopify MCP Server..."
npm install -g shopify-mcp

# Verify installation
echo "✅ Verifying MCP Server installation..."
if command -v shopify-mcp &> /dev/null; then
    echo "   ✅ shopify-mcp installed successfully"
    shopify-mcp --version
else
    echo "   ❌ shopify-mcp installation failed"
    exit 1
fi

# Create MCP server configuration directory
echo "📁 Creating MCP server configuration..."
MCP_CONFIG_DIR="$HOME/.config/mcp"
mkdir -p "$MCP_CONFIG_DIR"

# Create MCP server configuration file
echo "⚙️ Creating MCP server configuration..."
cat > "$MCP_CONFIG_DIR/shopify-mcp.json" << 'EOF'
{
  "server": {
    "host": "localhost",
    "port": 3001,
    "workers": 4,
    "timeout": 30,
    "max_connections": 100
  },
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
  },
  "logging": {
    "level": "info",
    "file": "/var/log/mcp/shopify-mcp.log",
    "max_size": "100MB",
    "max_files": 5
  }
}
EOF

# Create systemd service for MCP server
echo "🔧 Creating systemd service for MCP server..."
sudo tee /etc/systemd/system/shopify-mcp.service > /dev/null << EOF
[Unit]
Description=Shopify MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
Environment=NODE_ENV=production
Environment=MCP_CONFIG_PATH=$HOME/.config/mcp/shopify-mcp.json
ExecStart=/usr/local/bin/shopify-mcp --config \$MCP_CONFIG_PATH
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
echo "📝 Creating log directory..."
sudo mkdir -p /var/log/mcp
sudo chown $USER:$USER /var/log/mcp

# Enable and start the service
echo "🚀 Enabling and starting MCP server service..."
sudo systemctl daemon-reload
sudo systemctl enable shopify-mcp
sudo systemctl start shopify-mcp

# Check service status
echo "🔍 Checking MCP server status..."
sleep 3
if sudo systemctl is-active --quiet shopify-mcp; then
    echo "   ✅ MCP server is running"
    sudo systemctl status shopify-mcp --no-pager
else
    echo "   ❌ MCP server failed to start"
    echo "   Checking logs:"
    sudo journalctl -u shopify-mcp --no-pager -n 20
fi

# Test MCP server connectivity
echo "🧪 Testing MCP server connectivity..."
sleep 2
if curl -s http://localhost:3001/health > /dev/null; then
    echo "   ✅ MCP server is responding on port 3001"
else
    echo "   ⚠️  MCP server not responding - may need manual configuration"
fi

# Create MCP server management script
echo "📜 Creating MCP server management script..."
cat > "$HOME/mcp-manager.sh" << 'EOF'
#!/bin/bash

# MCP Server Management Script

case "$1" in
    start)
        echo "🚀 Starting MCP server..."
        sudo systemctl start shopify-mcp
        ;;
    stop)
        echo "🛑 Stopping MCP server..."
        sudo systemctl stop shopify-mcp
        ;;
    restart)
        echo "🔄 Restarting MCP server..."
        sudo systemctl restart shopify-mcp
        ;;
    status)
        echo "📊 MCP server status:"
        sudo systemctl status shopify-mcp --no-pager
        ;;
    logs)
        echo "📝 MCP server logs:"
        sudo journalctl -u shopify-mcp -f
        ;;
    config)
        echo "⚙️ MCP server configuration:"
        cat $HOME/.config/mcp/shopify-mcp.json
        ;;
    test)
        echo "🧪 Testing MCP server..."
        curl -s http://localhost:3001/health || echo "❌ MCP server not responding"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|config|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start MCP server"
        echo "  stop    - Stop MCP server"
        echo "  restart - Restart MCP server"
        echo "  status  - Show server status"
        echo "  logs    - Show server logs"
        echo "  config  - Show configuration"
        echo "  test    - Test server connectivity"
        exit 1
        ;;
esac
EOF

chmod +x "$HOME/mcp-manager.sh"

echo ""
echo "✅ MCP Server Setup Complete!"
echo "=================================="
echo ""
echo "🎯 Next Steps:"
echo "1. Update your .env file with real Shopify credentials:"
echo "   SHOPIFY_API_KEY=your_live_api_key"
echo "   SHOPIFY_API_SECRET=your_live_api_secret"
echo ""
echo "2. Test MCP server:"
echo "   ./mcp-manager.sh test"
echo ""
echo "3. Check MCP server status:"
echo "   ./mcp-manager.sh status"
echo ""
echo "4. View MCP server logs:"
echo "   ./mcp-manager.sh logs"
echo ""
echo "5. Integration with Optik Platform:"
echo "   - MCP server runs on http://localhost:3001"
echo "   - Backend connects via SHOPIFY_MCP_SERVER_PATH"
echo "   - All Shopify scraping functions will use MCP server"
echo ""
echo "🔧 MCP Server Management Commands:"
echo "   ./mcp-manager.sh {start|stop|restart|status|logs|config|test}"
echo ""
echo "📚 Documentation:"
echo "   - MCP Server Config: $HOME/.config/mcp/shopify-mcp.json"
echo "   - Service File: /etc/systemd/system/shopify-mcp.service"
echo "   - Logs: sudo journalctl -u shopify-mcp -f"
echo ""
echo "🚀 MCP Server is ready for integration!"
