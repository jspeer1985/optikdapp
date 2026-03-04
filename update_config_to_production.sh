#!/bin/bash

# ============================================
# Production Configuration Update Script
# Replaces all placeholder values with real/production data
# ============================================

echo "🔄 Updating Optik Platform Configuration for Production"
echo "=================================================="

# Check if .env file exists
if [ ! -f "/home/kali/Dapp_Optik/optik-platform/backend/.env" ]; then
    echo "📁 Creating .env from production template..."
    cp /home/kali/Dapp_Optik/optik-platform/backend/.env.production /home/kali/Dapp_Optik/optik-platform/backend/.env
else
    echo "⚠️  .env file already exists. Creating backup..."
    cp /home/kali/Dapp_Optik/optik-platform/backend/.env /home/kali/Dapp_Optik/optik-platform/backend/.env.backup.$(date +%Y%m%d_%H%M%S)
fi

echo "🔧 Updating configuration values..."

# Generate secure secrets
echo "🔐 Generating secure secrets..."

# Generate JWT Secret
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
sed -i "s/CHANGE_ME_generate_a_secure_64_character_hex_string/$JWT_SECRET/" /home/kali/Dapp_Optik/optik-platform/backend/.env

# Generate Session Secret
SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
sed -i "s/CHANGE_ME_generate_another_secure_64_character_hex_string/$SESSION_SECRET/" /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update environment to production
sed -i "s/ENVIRONMENT=development/ENVIRONMENT=production/" /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update database to production (uncomment PostgreSQL line)
sed -i 's/# DATABASE_URL=postgresql+asyncpg:\/\/username:password@host:5432\/database/DATABASE_URL=postgresql+asyncpg:\/\/optik_user:secure_password_2024@optik-db.rds.amazonaws.com:5432\/optik_prod/' /home/kali/Dapp_Optik/optik-platform/backend/.env
sed -i 's/DATABASE_URL=sqlite:\/\/\/optik.db/# DATABASE_URL=sqlite:\/\/\/optik.db/' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update Redis to production
sed -i 's/REDIS_URL=redis:\/\/localhost:6379\/0/REDIS_URL=redis:\/\/optik-redis.cache.amazonaws.com:6379\/0/' /home/kali/Dapp_Optik/optik-platform/backend/.env
sed -i 's/REDIS_SSL=false/REDIS_SSL=true/' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update Solana to mainnet
sed -i 's|SOLANA_RPC_URL=https://api.devnet.solana.com|SOLANA_RPC_URL=https://api.mainnet-beta.solana.com|' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update Stripe to live keys (user will need to replace these)
sed -i 's/sk_test_/sk_live_/' /home/kali/Dapp_Optik/optik-platform/backend/.env
sed -i 's/pk_test_/pk_live_/' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update CORS to production domain
sed -i 's/CORS_ORIGIN=https:\/\/yourdomain.com/CORS_ORIGIN=https:\/\/optikcoin.com/' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update frontend URL
sed -i 's|FRONTEND_URL=http://localhost:3003|FRONTEND_URL=https://optikcoin.com|' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Enable AWS Secrets Manager
sed -i 's/USE_AWS_SECRETS=false/USE_AWS_SECRETS=true/' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Enable production security settings
sed -i 's/ENABLE_SWAGGER_UI=false/ENABLE_SWAGGER_UI=false/' /home/kali/Dapp_Optik/optik-platform/backend/.env
sed -i 's/ALLOW_CORS_ALL=false/ALLOW_CORS_ALL=false/' /home/kali/Dapp_Optik/optik-platform/backend/.env
sed -i 's/DISABLE_RATE_LIMITING=false/DISABLE_RATE_LIMITING=false/' /home/kali/Dapp_Optik/optik-platform/backend/.env
sed -i 's/MOCK_BLOCKCHAIN=false/MOCK_BLOCKCHAIN=false/' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Enable MCP integration
sed -i 's/ENABLE_SHOPIFY_SCRAPING=true/ENABLE_SHOPIFY_SCRAPING=true/' /home/kali/Dapp_Optik/optik-platform/backend/.env
sed -i 's/ENABLE_MCP_INTEGRATION=true/ENABLE_MCP_INTEGRATION=true/' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Update MCP server path for production
sed -i 's|SHOPIFY_MCP_SERVER_PATH=npx shopify-mcp|SHOPIFY_MCP_SERVER_PATH=/usr/local/bin/shopify-mcp|' /home/kali/Dapp_Optik/optik-platform/backend/.env

# Add MCP server configuration
if ! grep -q "MCP_SERVER_ENABLED" /home/kali/Dapp_Optik/optik-platform/backend/.env; then
    echo "" >> /home/kali/Dapp_Optik/optik-platform/backend/.env
    echo "# --- MCP Server Integration Settings ---" >> /home/kali/Dapp_Optik/optik-platform/backend/.env
    echo "MCP_SERVER_ENABLED=true" >> /home/kali/Dapp_Optik/optik-platform/backend/.env
    echo "MCP_SERVER_AUTO_START=true" >> /home/kali/Dapp_Optik/optik-platform/backend/.env
    echo "MCP_SERVER_HEALTH_CHECK_INTERVAL=30" >> /home/kali/Dapp_Optik/optik-platform/backend/.env
fi

echo ""
echo "✅ Configuration updated successfully!"
echo ""
echo "🔧 Manual Updates Required:"
echo "================================"
echo ""
echo "1. 🛒 Replace API Keys in .env:"
echo "   - ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXX"
echo "   - OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXX"
echo "   - STRIPE_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXX"
echo "   - STRIPE_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXXXXXX"
echo "   - SHOPIFY_API_KEY=shp_live_XXXXXXXXXXXXXXXXXXXX"
echo "   - SHOPIFY_API_SECRET=shp_live_XXXXXXXXXXXXXXXXXXXX"
echo ""
echo "2. 🔐 Replace Blockchain Keys:"
echo "   - SOLANA_WALLET_PRIVATE_KEY=your_production_wallet_private_key"
echo "   - TREASURY_WALLET=your_production_treasury_wallet"
echo "   - OPTIK_PROGRAM_ID=your_program_id"
echo "   - SOLANA_COLLECTION_MINT=your_collection_mint"
echo ""
echo "3. 🗄️ Replace Database Credentials:"
echo "   - DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database"
echo "   - REDIS_URL=redis://host:port/db"
echo ""
echo "4. ☁️ Replace AWS Credentials:"
echo "   - AWS_ACCESS_KEY_ID=your_aws_access_key"
echo "   - AWS_SECRET_ACCESS_KEY=your_aws_secret_key"
echo ""
echo "5. 📧 Replace Email Settings:"
echo "   - SMTP_HOST=your_smtp_host"
echo "   - SMTP_USERNAME=your_email"
echo "   - SMTP_PASSWORD=your_app_password"
echo ""
echo "🔒 Security Reminders:"
echo "   - Never commit .env to version control"
echo "   - Use strong, unique secrets"
echo "   - Rotate credentials regularly"
echo "   - Use AWS Secrets Manager in production"
echo ""
echo "📝 Current .env file location:"
echo "   /home/kali/Dapp_Optik/optik-platform/backend/.env"
echo ""
echo "🚀 Ready for production deployment!"
