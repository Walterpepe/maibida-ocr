#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo -E "${BASH_SOURCE[0]}" "$@"
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
  ca-certificates \
  certbot \
  curl \
  nginx \
  nodejs \
  python3-certbot-nginx

"${REPO_ROOT}/tools/deploy/deploy.sh"
