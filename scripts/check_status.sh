#!/bin/bash

echo "🚀 Optik Platform Status Check"
echo "=============================="

# Check Frontend
echo "📱 Frontend (Next.js):"
if curl -s http://localhost:3003/ | grep -q "Optik Platform"; then
    echo "   ✅ Running on http://localhost:3003"
    echo "   📄 Title: $(curl -s http://localhost:3003/ | grep -o '<title[^>]*>.*</title>' | sed 's/<[^>]*>//g')"
else
    echo "   ❌ Not responding"
fi

echo ""

# Check Backend
echo "🔧 Backend (FastAPI):"
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Running on http://localhost:8000"
    echo "   📊 Health: $(curl -s http://localhost:8000/health | jq -r '.status // "unknown"')"
    echo "   📚 API Docs: http://localhost:8000/api/docs"
else
    echo "   ❌ Not responding"
fi

echo ""

# Check Shopify MCP Server
echo "🛒 Shopify MCP Server:"
if command -v shopify-mcp >/dev/null 2>&1; then
    echo "   ✅ Installed and available"
else
    echo "   ⚠️  Using npx shopify-mcp"
fi

echo ""

# Check Ports
echo "🔌 Port Status:"
if lsof -i :3003 >/dev/null 2>&1; then
    echo "   ✅ Port 3003: Frontend"
else
    echo "   ❌ Port 3003: Not in use"
fi

if lsof -i :8000 >/dev/null 2>&1; then
    echo "   ✅ Port 8000: Backend"
else
    echo "   ❌ Port 8000: Not in use"
fi

echo ""
echo "🎯 Quick Links:"
echo "   Frontend: http://localhost:3003"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"
echo ""
echo "📖 Usage Guides:"
echo "   Quick Start: QUICK_START_GUIDE.md"
echo "   Shopify Guide: SHOPIFY_SCRAPING_GUIDE.md"
echo "   Demo Script: python demo_shopify_scraping.py"
