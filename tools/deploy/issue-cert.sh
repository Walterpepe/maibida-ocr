#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "$#" -ne 1 ]]; then
  echo "Usage: sudo $0 admin@example.com" >&2
  exit 64
fi

CERT_EMAIL="$1"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo -E "${BASH_SOURCE[0]}" "$@"
fi

certbot certonly \
  --webroot \
  --webroot-path /var/www/maibida/current \
  --non-interactive \
  --agree-tos \
  --keep-until-expiring \
  --email "${CERT_EMAIL}" \
  --deploy-hook "systemctl reload nginx" \
  --domain www.maibida.com \
  --domain maibida.com

"${REPO_ROOT}/tools/deploy/deploy.sh"
