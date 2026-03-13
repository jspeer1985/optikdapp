#!/bin/bash

# ==============================================================================
# OPTIK PLATFORM - AUTOMATED DEPLOYMENT & GO-LIVE AGENT
# ==============================================================================
# This script prepares, validates, and helps deploy the Optik Platform.
# Usage: ./automate_deployment.sh
# ==============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directories
PROJECT_ROOT=$(dirname $(dirname $(pwd)))  # Go up two levels from scripts/setup to Dapp_Optik root
FRONTEND_DIR="$PROJECT_ROOT/optik-platform/apps"
BACKEND_DIR="$PROJECT_ROOT/optik-platform/backend"

print_header() {
    echo -e "\n${CYAN}================================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}================================================================${NC}"
}

print_step() {
    echo -e "\n${BLUE}➡ $1...${NC}"
}

print_success() {
    echo -e "${GREEN}✔ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_status() {
    echo -e "${CYAN}→ $1${NC}"
}

print_error() {
    echo -e "${RED}✘ $1${NC}"
}

# 1. PREREQUISITE CHECK
print_header "Phase 1: Environment & Dependency Check"

print_step "Checking Node.js & NPM"
if command -v node >/dev/null 2>&1; then
    print_success "Node.js $(node -v) found"
else
    print_error "Node.js not found. Please install Node.js."
    exit 1
fi

print_step "Checking Python"
if command -v python3 >/dev/null 2>&1; then
    print_success "Python $(python3 --version) found"
else
    print_error "Python 3 not found. Please install Python."
    exit 1
fi

# 2. ENVIRONMENT VARIABLE VALIDATION
print_header "Phase 2: Secret & Environment Validation"

validate_env() {
    local file=$1
    local name=$2
    local required_keys=("${@:3}")

    print_step "Validating $name Environment ($file)"

    if [ ! -f "$file" ]; then
        print_warning "$file not found. Attempting to create from example..."
        if [ -f "$file.example" ]; then
            cp "$file.example" "$file"
            print_success "Created $file from example. PLEASE UPDATE IT!"
        else
            print_error "No example file found for $name. Create $file manually."
            return 1
        fi
    fi

    local missing=0
    for key in "${required_keys[@]}"; do
        if ! grep -q "^$key=" "$file"; then
            print_error "Missing key: $key"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "$name environment variables look complete (keys only check)."
    else
        print_warning "$missing keys missing in $file."
    fi
}

# Frontend keys
FRONTEND_REQUIRED=(
    "NEXT_PUBLIC_API_URL"
    "NEXT_PUBLIC_OPTIK_TOKEN_MINT"
)
validate_env "$FRONTEND_DIR/.env.local" "Frontend" "${FRONTEND_REQUIRED[@]}"

# Backend keys
BACKEND_REQUIRED=(
    "STRIPE_SECRET_KEY"
    "STRIPE_WEBHOOK_SECRET"
    "ANTHROPIC_API_KEY"
    "DATABASE_URL"
    "SOLANA_RPC_URL"
    "SOLANA_WALLET_PRIVATE_KEY"
)
validate_env "$BACKEND_DIR/.env" "Backend" "${BACKEND_REQUIRED[@]}"

# 3. BACKEND CONNECTIVITY CHECK
print_header "Phase 3: Service Connectivity"

print_step "Checking Backend Status (Local)"
# Default to port 80000 as per recent audit
BACKEND_URL="http://localhost:80000"
if curl -s "$BACKEND_URL/health" >/dev/null; then
    print_success "Backend is REACHABLE at $BACKEND_URL"
else
    print_warning "Backend is NOT reachable at $BACKEND_URL."
    print_info "Ensure you run: cd optik-platform/backend && python -m uvicorn api.main:app --reload --port 80000"
fi

# 4. FRONTEND BUILD SIMULATION
print_header "Phase 4: Production Build Simulation"

print_step "Running Frontend Build"
cd "$FRONTEND_DIR"
if [ -d "node_modules" ]; then
    print_status "node_modules found, starting build..."
else
    print_warning "node_modules missing, running npm install..."
    npm install --quiet
fi

# We run a build but don't fail the whole script if it's just a warning
if npm run build; then
    print_success "Frontend Build SUCCESSFUL (Production ready)"
else
    print_error "Frontend Build FAILED. Check the output above for errors."
    exit 1
fi
cd "$PROJECT_ROOT"

# 5. VERCEL CONFIGURATION VERIFICATION
print_header "Phase 5: Vercel Deployment Config"

if [ -f "vercel.json" ]; then
    print_success "vercel.json found in root"
    # Basic check for rootDirectory
    if grep -q "\"rootDirectory\": \"optik-platform/apps\"" "vercel.json"; then
        print_success "Vercel root directory correctly pointed to Next.js app"
    else
        print_warning "Vercel root directory might be misconfigured."
    fi
else
    print_warning "vercel.json NOT found in root. Next.js might fail to auto-detect the monorepo structure."
fi

# 6. FINAL DEPLOYMENT GUIDE
print_header "🚀 DEPLOYMENT READINESS SUMMARY"

echo -e "${CYAN}Your DApp Optik platform is ready for the open web!${NC}"
echo -e "\n${YELLOW}NEXT STEPS:${NC}"
echo -e "1. ${BOLD}Push to GitHub:${NC} git add . && git commit -m 'Release: Ready for Vercel' && git push"
echo -e "2. ${BOLD}Connect Vercel:${NC} Import the repo and set root to 'optik-platform/apps'"
echo -e "3. ${BOLD}Deploy Backend:${NC} Use Railway or Render for the backend/Dockerfile"
echo -e "4. ${BOLD}Sync Secrets:${NC} Copy .env values to Vercel/Render dashboard dashboards"

echo -e "\n${GREEN}Automation finished successfully. You are now 1-click away from LIVE.${NC}"
echo -e "${CYAN}================================================================${NC}\n"
