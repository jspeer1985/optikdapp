#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="optik-backend"
ECOSYSTEM_FILE="${ROOT_DIR}/ecosystem.config.cjs"

if ! command -v pm2 >/dev/null 2>&1; then
  echo "pm2 is not installed or not in PATH."
  echo "Install with: npm i -g pm2"
  exit 1
fi

ACTION="${1:-start}"
LINES="${2:-100}"

cd "${ROOT_DIR}"

case "${ACTION}" in
  start)
    pm2 start "${ECOSYSTEM_FILE}" --only "${APP_NAME}"
    ;;
  stop)
    pm2 stop "${APP_NAME}"
    ;;
  restart)
    pm2 restart "${APP_NAME}"
    ;;
  status)
    pm2 status "${APP_NAME}"
    ;;
  logs)
    pm2 logs "${APP_NAME}" --lines "${LINES}"
    ;;
  save)
    pm2 save
    ;;
  startup)
    pm2 startup
    ;;
  delete)
    pm2 delete "${APP_NAME}"
    ;;
  *)
    cat <<EOF
Usage: scripts/backendctl.sh [command]

Commands:
  start       Start backend with PM2 (default)
  stop        Stop backend process
  restart     Restart backend process
  status      Show backend process status
  logs [N]    Tail logs (default N=100)
  save        Save PM2 process list for reboot restore
  startup     Print PM2 startup command for your OS
  delete      Remove backend process from PM2
EOF
    exit 1
    ;;
esac
