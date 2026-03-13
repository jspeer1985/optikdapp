# Optik Platform Scripts

## 📁 Script Organization

### **🚀 Setup Scripts** (`setup/`)
- `automate_deployment.sh` - One-click deployment automation
- `integrate_payments.sh` - Payment system integration
- `setup_automated_dapp_factory.sh` - Factory setup
- `setup_mcp_server.sh` - MCP server setup
- `setup_universal_ecommerce_mcp.sh` - Universal e-commerce MCP
- `setup_woocommerce_mcp.sh` - WooCommerce MCP
- `update_config_to_production.sh` - Production configuration

### **🔧 Utility Scripts** (`/`)
- `check_status.sh` - System status check
- `start-dev.sh` - Development server startup
- `upload_optik_metadata.sh` - IPFS metadata upload

### **🔒 Security Scripts** (`security/`)
- `cleanup.sh` - Security cleanup and file organization

## 🎮 Usage

### **Quick Setup**
```bash
# Automated deployment
./scripts/setup/automate_deployment.sh

# Development environment
./scripts/start-dev.sh
```

### **Factory Setup**
```bash
# Complete factory setup
./scripts/setup/setup_automated_dapp_factory.sh

# MCP servers
./scripts/setup/setup_universal_ecommerce_mcp.sh
./scripts/setup/setup_woocommerce_mcp.sh
```

### **Security**
```bash
# Clean up sensitive files
./scripts/security/cleanup.sh
```

### **Monitoring**
```bash
# Check system status
./scripts/check_status.sh
```

## ⚠️ Important Notes

- **All scripts require proper permissions**: `chmod +x scripts/**/*.sh`
- **Environment variables** must be configured in `.env.local`
- **Run security scripts** before committing to git
- **Backup important data** before running cleanup scripts

## 🔐 Security

All scripts are designed with security in mind:
- No hardcoded credentials
- Environment variable validation
- Safe file operations
- Proper error handling

---

**Optik Platform** - Automated dApp Factory Scripts
