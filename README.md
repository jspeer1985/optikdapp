# 👁️ Optik Platform - Automated dApp Factory

Convert any e-commerce store to a Web3 dApp with AI-powered automation. Support for 9 major platforms including Shopify, WooCommerce, Amazon, and eBay.

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd Dapp_Optik

# 2. Install dependencies
npm install
pip install -r optik-platform/backend/requirements.txt

# 3. Configure environment
cp optik-platform/backend/.env.example optik-platform/apps/.env.local
# Edit .env.local with your API keys

# 4. Start development
npm run dev  # Frontend (port 3003)
cd optik-platform/backend && python -m uvicorn api.main:app --reload  # Backend (port 8000)
```

## 📚 Complete Documentation

📖 **[View Full Documentation](docs/README.md)**

### **Key Guides:**
- **[Quick Start Guide](docs/guides/QUICK_START_GUIDE.md)** - 5-minute setup
- **[Production Setup](docs/setup/PRODUCTION_SETUP_SUMMARY.md)** - Deployment guide
- **[MCP Integration](docs/guides/MCP_INTEGRATION_GUIDE.md)** - Platform integrations

## 🏗️ Project Structure

```
optik-platform/
├── apps/                    # Next.js frontend
├── backend/                 # FastAPI services
│   ├── services/           # Core automation logic
│   ├── mcp_servers/        # Platform integrations
│   └── demos/             # Development examples
├── contracts/              # Solana smart contracts
├── docs/                   # Complete documentation
└── scripts/               # Utility scripts
```

## 🎯 Features

- **9 E-commerce Platforms** - Shopify, WooCommerce, Wix, BigCommerce, Magento, Squarespace, Etsy, Amazon, eBay
- **AI-Powered Automation** - Complete conversion pipeline
- **NFT Creation with OPTIK Pairing** - Automatic token generation
- **Smart Contract Deployment** - Blockchain integration
- **Revenue Collection** - Transaction fee monitoring

## 💰 Business Model

- **Conversion Fees**: $5K-100K per dApp conversion
- **Transaction Fees**: 1-3% of all dApp transactions
- **NFT Minting**: Revenue from token creation
- **Premium Features**: Advanced analytics

## 🌐 Access

- **Frontend**: http://localhost:3003
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Documentation**: [docs/README.md](docs/README.md)

## 🛡️ Security & Audits

- Non-custodial wallet architecture
- Automated API rate limiting
- Secure environment variable handling
- Real-time revenue splitting

## 💰 Partnership Tiers

Revenue Share Model ($0 upfront):

- **Elite**: 15% share | 6 AI Agents | Full Autonomy
- **Scale**: 12% share | 4 AI Agents | Security Suite+
- **Global**: 9% share | 3 AI Agents | Multi-Region
- **Growth**: 5% share | 2 AI Agents | Automation Core
- **Basic**: 3% share | 1 AI Agent | Core Tools

---

## 📞 Support

- 📖 [Full Documentation](docs/README.md)
- 📧 Email: support@optikcoin.com
- 🐛 Issues: GitHub Issues

---

_Built with ❤️ by the Optik Core Team on Solana._
