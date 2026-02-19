#!/bin/bash

# ═══════════════════════════════════════════════════════════════
#  Dapp_Optik — Project Cleanup Script
#  Run from: /home/kali/Dapp_Optik/
#  Usage: chmod +x cleanup.sh && ./cleanup.sh
# ═══════════════════════════════════════════════════════════════

set -e
PROJECT="/home/kali/Dapp_Optik"
cd "$PROJECT"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     Dapp_Optik Cleanup Script            ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "⚠️  This will permanently delete files."
echo "    Make sure you have a git commit or backup first."
echo ""
read -p "   Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 1: Removing virtual environments"
echo "─────────────────────────────────────────────"

if [ -d ".venv" ]; then
  echo "  🗑️  Deleting .venv/ (~35,000 files)..."
  rm -rf .venv
  echo "  ✅ Done"
else
  echo "  ⏭️  .venv/ not found, skipping"
fi

if [ -d "optik-platform/backend/docker/venv" ]; then
  echo "  🗑️  Deleting optik-platform/backend/docker/venv/..."
  rm -rf optik-platform/backend/docker/venv
  echo "  ✅ Done"
else
  echo "  ⏭️  docker/venv not found, skipping"
fi

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 2: Removing Hardhat build artifacts"
echo "─────────────────────────────────────────────"

if [ -d "artifacts" ]; then
  echo "  🗑️  Deleting artifacts/..."
  rm -rf artifacts
  echo "  ✅ Done"
fi

if [ -d "cache" ]; then
  echo "  🗑️  Deleting cache/..."
  rm -rf cache
  echo "  ✅ Done"
fi

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 3: Removing duplicate audit docs"
echo "─────────────────────────────────────────────"

AUDIT_DOCS=(
  "AUDIT_EXECUTIVE_SUMMARY_2026-02-19.md"
  "AUDIT_IMPLEMENTATION_GUIDE.md"
  "AUDIT_INDEX_2026-02-19.md"
  "AUDIT_INDEX.txt"
  "AUDIT_PACKAGE_MANIFEST_2026-02-19.md"
  "AUDIT_QUICK_REFERENCE_2026-02-19.md"
  "AUDIT_SUMMARY.txt"
  "COMPREHENSIVE_AUDIT_REPORT_2026-02-18.md"
  "COMPREHENSIVE_AUDIT_REPORT.md"
  "ENTERPRISE_AUDIT_COMPLETE_DELIVERABLES.md"
  "ENTERPRISE_AUDIT_EXECUTIVE_SUMMARY.md"
  "ENTERPRISE_AUDIT_INDEX.md"
  "ENTERPRISE_AUDIT_REMEDIATION_ROADMAP.md"
  "ENTERPRISE_AUDIT_STATUS.txt"
  "ENTERPRISE_GRADE_AUDIT_2026-02-19.md"
  "API_KEY_SECURITY_DOCUMENTATION_INDEX.md"
  "API_KEY_SECURITY_FIX_REPORT.md"
  "API_KEY_SECURITY_QUICK_REFERENCE.md"
  "ENV_AUDIT_REPORT_2026-02-19.md"
)

for f in "${AUDIT_DOCS[@]}"; do
  if [ -f "$f" ]; then
    echo "  🗑️  Deleting $f"
    rm "$f"
  fi
done
echo "  ✅ Done (kept: COMPREHENSIVE_AUDIT_REPORT_2026-02-19.md, CRITICAL_SECURITY_FIXES_2026-02-19.md)"

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 4: Removing redundant shell scripts"
echo "─────────────────────────────────────────────"

# Keep integrate_payments.sh in case it's still needed
# Delete the duplicate API key fix scripts
for f in "FIX_API_KEYS_IMPLEMENTATION.sh" "fix_api_keys.sh"; do
  if [ -f "$f" ]; then
    echo "  🗑️  Deleting $f"
    rm "$f"
  fi
done
echo "  ✅ Done"

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 5: Removing zip archives"
echo "─────────────────────────────────────────────"

for f in "optikcoin-theme-final.zip" "optikcoin-theme.zip"; do
  if [ -f "$f" ]; then
    echo "  🗑️  Deleting $f"
    rm "$f"
  fi
done
echo "  ✅ Done"

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 6: Removing logs and temp files"
echo "─────────────────────────────────────────────"

if [ -f "firebase-debug.log" ]; then
  echo "  🗑️  Deleting firebase-debug.log"
  rm firebase-debug.log
fi

if [ -f "FILE_TREE.txt" ]; then
  echo "  🗑️  Deleting FILE_TREE.txt"
  rm FILE_TREE.txt
fi

find . -name "*.log" -not -path "./.git/*" -exec echo "  🗑️  Deleting {}" \; -exec rm {} \;
echo "  ✅ Done"

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 7: Removing Hardhat boilerplate contracts"
echo "─────────────────────────────────────────────"

echo ""
echo "  ⚠️  The following appear to be unused Hardhat boilerplate:"
echo "       contracts/Counter.sol"
echo "       contracts/Counter.t.sol"
echo "       ignition/modules/Counter.ts"
echo ""
read -p "  Delete these boilerplate contracts? (y/N): " del_counter
if [[ "$del_counter" == "y" || "$del_counter" == "Y" ]]; then
  [ -f "contracts/Counter.sol" ]       && rm contracts/Counter.sol       && echo "  🗑️  Deleted Counter.sol"
  [ -f "contracts/Counter.t.sol" ]     && rm contracts/Counter.t.sol     && echo "  🗑️  Deleted Counter.t.sol"
  [ -f "ignition/modules/Counter.ts" ] && rm ignition/modules/Counter.ts && echo "  🗑️  Deleted Counter.ts"
  echo "  ✅ Done"
else
  echo "  ⏭️  Skipped"
fi

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 8: Updating .gitignore"
echo "─────────────────────────────────────────────"

GITIGNORE_ADDITIONS=$(cat <<'EOF'

# === Auto-added by cleanup.sh ===
# Python
.venv/
__pycache__/
*.pyc
*.pyo

# Hardhat
artifacts/
cache/

# Logs
*.log
firebase-debug.log
logs/

# IDE
.idea/
.vscode/

# Env (keep .env.example, ignore real .env)
.env

# Archives
*.zip

# Temp
FILE_TREE.txt
managed_context/
EOF
)

if [ -f ".gitignore" ]; then
  # Only add if not already present
  if ! grep -q "Auto-added by cleanup.sh" .gitignore; then
    echo "$GITIGNORE_ADDITIONS" >> .gitignore
    echo "  ✅ Updated .gitignore"
  else
    echo "  ⏭️  .gitignore already updated, skipping"
  fi
else
  echo "$GITIGNORE_ADDITIONS" > .gitignore
  echo "  ✅ Created .gitignore"
fi

echo ""
echo "─────────────────────────────────────────────"
echo " STEP 9: Final file count"
echo "─────────────────────────────────────────────"
TOTAL=$(find . -not -path "./.git/*" -type f | wc -l)
echo "  📁 Remaining files in project: $TOTAL"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅  Cleanup complete!                   ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Next steps:"
echo "  1. Run 'git status' to review all changes"
echo "  2. Run 'git add -A && git commit -m \"chore: cleanup junk files\"'"
echo "  3. Upload your source folders here for a deep code audit"
echo ""