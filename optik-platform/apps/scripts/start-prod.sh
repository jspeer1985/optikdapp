#!/usr/bin/env bash
set -euo pipefail

# Enterprise-friendly production start helper for the Next.js app
# Usage: PORT=3000 ./scripts/start-prod.sh

PORT=${PORT:-3000}

echo "Building app..."
npm run build

echo "Starting Next.js in production on port ${PORT}..."
NODE_ENV=production next start -p ${PORT}
