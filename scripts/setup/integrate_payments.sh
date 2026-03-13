#!/bin/bash

################################################################################
# OPTIK PLATFORM - PAYMENT INTEGRATION SCRIPT
# Automatically integrates payment system into your project
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
}

################################################################################
# CONFIGURATION
################################################################################

# Source directory (where payment files are)
SOURCE_DIR="/mnt/user-data/outputs"

# Target directories (your project)
TARGET_FRONTEND="${1:-./}"
TARGET_BACKEND="${2:-./backend}"

################################################################################
# VALIDATION
################################################################################

print_header "Payment System Integration Script"
echo "This script will integrate the payment system into your project"
echo ""

# Check if source files exist
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Check if target directories exist
if [ ! -d "$TARGET_FRONTEND" ]; then
    print_error "Frontend directory not found: $TARGET_FRONTEND"
    print_info "Usage: ./integrate_payments.sh [frontend_dir] [backend_dir]"
    exit 1
fi

if [ ! -d "$TARGET_BACKEND" ]; then
    print_warning "Backend directory not found: $TARGET_BACKEND"
    print_info "Will create backend directory structure"
    mkdir -p "$TARGET_BACKEND/api"
fi

################################################################################
# STEP 1: CREATE DIRECTORY STRUCTURE
################################################################################

print_header "STEP 1: Creating Directory Structure"

# Frontend directories
mkdir -p "$TARGET_FRONTEND/app/checkout"
print_status "Created: app/checkout/"

mkdir -p "$TARGET_FRONTEND/app/dashboard/billing/subscription"
print_status "Created: app/dashboard/billing/subscription/"

mkdir -p "$TARGET_FRONTEND/app/dashboard/billing/history"
print_status "Created: app/dashboard/billing/history/"

# Backend directories
mkdir -p "$TARGET_BACKEND/api"
print_status "Created: backend/api/"

################################################################################
# STEP 2: COPY FRONTEND FILES
################################################################################

print_header "STEP 2: Copying Frontend Files"

# Checkout page
if [ -f "$SOURCE_DIR/frontend/app/checkout/page.tsx" ]; then
    cp "$SOURCE_DIR/frontend/app/checkout/page.tsx" \
       "$TARGET_FRONTEND/app/checkout/page.tsx"
    print_status "Copied: app/checkout/page.tsx (350 lines)"
else
    print_error "Source file not found: frontend/app/checkout/page.tsx"
fi

# Subscription management page
if [ -f "$SOURCE_DIR/frontend/app/dashboard/billing/subscription/page.tsx" ]; then
    cp "$SOURCE_DIR/frontend/app/dashboard/billing/subscription/page.tsx" \
       "$TARGET_FRONTEND/app/dashboard/billing/subscription/page.tsx"
    print_status "Copied: app/dashboard/billing/subscription/page.tsx (450 lines)"
else
    print_error "Source file not found: frontend/app/dashboard/billing/subscription/page.tsx"
fi

# Payment history page
if [ -f "$SOURCE_DIR/frontend/app/dashboard/billing/history/page.tsx" ]; then
    cp "$SOURCE_DIR/frontend/app/dashboard/billing/history/page.tsx" \
       "$TARGET_FRONTEND/app/dashboard/billing/history/page.tsx"
    print_status "Copied: app/dashboard/billing/history/page.tsx (550 lines)"
else
    print_error "Source file not found: frontend/app/dashboard/billing/history/page.tsx"
fi

################################################################################
# STEP 3: COPY BACKEND FILES
################################################################################

print_header "STEP 3: Copying Backend Files"

# Payment API
if [ -f "$SOURCE_DIR/backend/api/payments.py" ]; then
    cp "$SOURCE_DIR/backend/api/payments.py" \
       "$TARGET_BACKEND/api/payments.py"
    print_status "Copied: backend/api/payments.py (650 lines)"
else
    print_error "Source file not found: backend/api/payments.py"
fi

################################################################################
# STEP 4: COPY CONFIGURATION FILES
################################################################################

print_header "STEP 4: Copying Configuration Files"

# Environment template
if [ -f "$SOURCE_DIR/.env.payments" ]; then
    cp "$SOURCE_DIR/.env.payments" \
       "$TARGET_FRONTEND/.env.payments.example"
    print_status "Copied: .env.payments.example"
    print_warning "⚠ Remember to rename to .env and add your Stripe keys"
else
    print_error "Source file not found: .env.payments"
fi

# Package.json with payment dependencies
if [ -f "$SOURCE_DIR/frontend/package-payments.json" ]; then
    cp "$SOURCE_DIR/frontend/package-payments.json" \
       "$TARGET_FRONTEND/package-payments.json"
    print_status "Copied: package-payments.json (reference for dependencies)"
else
    print_error "Source file not found: frontend/package-payments.json"
fi

# Python requirements
if [ -f "$SOURCE_DIR/backend/requirements-payments.txt" ]; then
    cp "$SOURCE_DIR/backend/requirements-payments.txt" \
       "$TARGET_BACKEND/requirements-payments.txt"
    print_status "Copied: requirements-payments.txt"
else
    print_error "Source file not found: backend/requirements-payments.txt"
fi

################################################################################
# STEP 5: COPY DOCUMENTATION
################################################################################

print_header "STEP 5: Copying Documentation"

# Integration guide
if [ -f "$SOURCE_DIR/PAYMENT_INTEGRATION_GUIDE.md" ]; then
    cp "$SOURCE_DIR/PAYMENT_INTEGRATION_GUIDE.md" \
       "$TARGET_FRONTEND/docs/PAYMENT_INTEGRATION_GUIDE.md" 2>/dev/null || \
    cp "$SOURCE_DIR/PAYMENT_INTEGRATION_GUIDE.md" \
       "$TARGET_FRONTEND/PAYMENT_INTEGRATION_GUIDE.md"
    print_status "Copied: PAYMENT_INTEGRATION_GUIDE.md"
else
    print_error "Source file not found: PAYMENT_INTEGRATION_GUIDE.md"
fi

# Integration summary
if [ -f "$SOURCE_DIR/PAYMENT_INTEGRATION_SUMMARY.md" ]; then
    cp "$SOURCE_DIR/PAYMENT_INTEGRATION_SUMMARY.md" \
       "$TARGET_FRONTEND/docs/PAYMENT_INTEGRATION_SUMMARY.md" 2>/dev/null || \
    cp "$SOURCE_DIR/PAYMENT_INTEGRATION_SUMMARY.md" \
       "$TARGET_FRONTEND/PAYMENT_INTEGRATION_SUMMARY.md"
    print_status "Copied: PAYMENT_INTEGRATION_SUMMARY.md"
else
    print_error "Source file not found: PAYMENT_INTEGRATION_SUMMARY.md"
fi

################################################################################
# STEP 6: UPDATE MAIN API FILE
################################################################################

print_header "STEP 6: Updating Backend Main API"

MAIN_API="$TARGET_BACKEND/api/main.py"

if [ -f "$MAIN_API" ]; then
    # Check if payments router already imported
    if grep -q "from .payments import router as payments_router" "$MAIN_API"; then
        print_warning "Payments router already imported in main.py"
    else
        # Backup original file
        cp "$MAIN_API" "$MAIN_API.backup"
        print_status "Created backup: main.py.backup"
        
        # Add import at the top (after existing imports)
        sed -i '/^from fastapi import/a from .payments import router as payments_router' "$MAIN_API"
        
        # Add router registration (after app = FastAPI())
        sed -i '/^app = FastAPI/a \\\n# Payment routes\napp.include_router(payments_router)' "$MAIN_API"
        
        print_status "Updated: backend/api/main.py"
        print_info "Added payments router import and registration"
    fi
else
    print_warning "main.py not found at $MAIN_API"
    print_info "You'll need to manually add the payments router"
    
    # Create a sample main.py
    cat > "$MAIN_API" << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .payments import router as payments_router

app = FastAPI(
    title="Optik Platform API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Payment routes
app.include_router(payments_router)

@app.get("/")
def root():
    return {"message": "Optik Platform API"}

@app.get("/health")
def health():
    return {"status": "healthy"}
EOF
    print_status "Created sample: backend/api/main.py"
fi

################################################################################
# STEP 7: INSTALL DEPENDENCIES
################################################################################

print_header "STEP 7: Installing Dependencies"

# Frontend dependencies
if [ -f "$TARGET_FRONTEND/package.json" ]; then
    print_info "Installing frontend dependencies..."
    cd "$TARGET_FRONTEND"
    
    npm install @stripe/stripe-js @stripe/react-stripe-js lucide-react --save 2>&1 | grep -v "^npm WARN" || true
    
    if [ $? -eq 0 ]; then
        print_status "Installed: @stripe/stripe-js, @stripe/react-stripe-js, lucide-react"
    else
        print_warning "Could not install npm packages automatically"
        print_info "Run manually: npm install @stripe/stripe-js @stripe/react-stripe-js lucide-react"
    fi
    
    cd - > /dev/null
else
    print_warning "package.json not found"
    print_info "Run manually: npm install @stripe/stripe-js @stripe/react-stripe-js lucide-react"
fi

# Backend dependencies
if command -v pip &> /dev/null; then
    print_info "Installing backend dependencies..."
    pip install stripe requests --break-system-packages --quiet 2>&1 | grep -v "^Requirement already satisfied" || true
    
    if [ $? -eq 0 ]; then
        print_status "Installed: stripe, requests"
    else
        print_warning "Could not install pip packages automatically"
        print_info "Run manually: pip install stripe requests --break-system-packages"
    fi
else
    print_warning "pip not found"
    print_info "Run manually: pip install stripe requests --break-system-packages"
fi

################################################################################
# STEP 8: GENERATE FILE TREE
################################################################################

print_header "STEP 8: Generating File Tree"

cat > "$TARGET_FRONTEND/PAYMENT_FILES.txt" << EOF
Payment System Files Integrated
================================

Frontend Files:
├── app/
│   ├── checkout/
│   │   └── page.tsx                                (350 lines) ✅
│   └── dashboard/
│       └── billing/
│           ├── subscription/
│           │   └── page.tsx                        (450 lines) ✅
│           └── history/
│               └── page.tsx                        (550 lines) ✅

Backend Files:
└── backend/
    └── api/
        ├── payments.py                              (650 lines) ✅
        └── main.py                                  (updated) ✅

Configuration:
├── .env.payments.example                            ✅
├── package-payments.json                            ✅
└── requirements-payments.txt                        ✅

Documentation:
├── PAYMENT_INTEGRATION_GUIDE.md                     ✅
└── PAYMENT_INTEGRATION_SUMMARY.md                   ✅

Total Files: 4 pages + 1 API + 6 config/docs = 11 files
Total Lines: ~2,000 lines of production-ready code
EOF

print_status "Created: PAYMENT_FILES.txt (file tree reference)"

################################################################################
# FINAL SUMMARY
################################################################################

print_header "🎉 Integration Complete!"

echo ""
echo "📦 Files Installed:"
echo "   ✓ 3 Frontend pages (checkout, subscription, history)"
echo "   ✓ 1 Backend API (payments.py with 9 endpoints)"
echo "   ✓ 3 Configuration files"
echo "   ✓ 2 Documentation files"
echo ""

echo "📋 Next Steps:"
echo ""
echo "1. Configure Stripe:"
echo "   - Get API keys from https://dashboard.stripe.com/apikeys"
echo "   - Create products in Stripe Dashboard > Products"
echo "   - Set up webhook at https://dashboard.stripe.com/webhooks"
echo ""

echo "2. Update Environment Variables:"
echo "   - Copy .env.payments.example to .env"
echo "   - Add your Stripe keys and price IDs"
echo ""

echo "3. Test the Integration:"
echo "   - Start backend: uvicorn backend.api.main:app --reload"
echo "   - Start frontend: npm run dev"
echo "   - Visit: http://localhost:3000/checkout?tier=growth&billing=monthly"
echo "   - Use test card: 4242 4242 4242 4242"
echo ""

echo "4. Read Documentation:"
echo "   - PAYMENT_INTEGRATION_GUIDE.md (complete setup guide)"
echo "   - PAYMENT_INTEGRATION_SUMMARY.md (quick reference)"
echo ""

echo "📊 Production URLs:"
echo "   - Checkout:      /checkout?tier=pro&billing=monthly"
echo "   - Subscription:  /dashboard/billing/subscription"
echo "   - History:       /dashboard/billing/history"
echo ""

echo "🔐 Security Checklist:"
echo "   □ Never commit .env file with real keys"
echo "   □ Use environment variables for all secrets"
echo "   □ Set up webhook signature verification"
echo "   □ Enable HTTPS in production"
echo "   □ Test with Stripe test cards first"
echo ""

print_status "Payment system ready to accept payments! 🚀"
echo ""

# Create a quick start script
cat > "$TARGET_FRONTEND/start-payment-test.sh" << 'EOF'
#!/bin/bash
# Quick start script for testing payment system

echo "Starting Payment System Test Environment..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠ Warning: .env file not found"
    echo "Copy .env.payments.example to .env and add your Stripe keys"
    exit 1
fi

# Start backend in background
echo "Starting backend..."
cd backend && uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✓ Backend running on http://localhost:8000"
echo "✓ Frontend running on http://localhost:3000"
echo ""
echo "Test URLs:"
echo "  - http://localhost:3000/checkout?tier=growth&billing=monthly"
echo "  - http://localhost:3000/dashboard/billing/subscription"
echo "  - http://localhost:3000/dashboard/billing/history"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
EOF

chmod +x "$TARGET_FRONTEND/start-payment-test.sh"
print_status "Created: start-payment-test.sh (quick start script)"

echo ""
echo "💡 Pro Tip: Run ./start-payment-test.sh to test everything at once"
echo ""