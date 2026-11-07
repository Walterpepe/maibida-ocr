#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo -E "${BASH_SOURCE[0]}" "$@"
fi

ufw allow OpenSSH
ufw allow 80/tcp comment "Maibida HTTP and ACME"
ufw allow 443/tcp comment "Maibida HTTPS"
ufw --force enable
ufw status verbose
