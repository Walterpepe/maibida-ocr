#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP_ROOT="/var/www/maibida"
RELEASE_ROOT="${APP_ROOT}/releases"
CURRENT_LINK="${APP_ROOT}/current"
MESSAGE_DIR="/var/lib/maibida/messages"
STAMP="$(date +%Y%m%d%H%M%S)"
RELEASE_DIR="${RELEASE_ROOT}/${STAMP}"
CERT_FILE="/etc/letsencrypt/live/www.maibida.com/fullchain.pem"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo -E "${BASH_SOURCE[0]}" "$@"
fi

for command_name in git node nginx systemctl curl; do
  command -v "${command_name}" >/dev/null
done

TARBALL="$(mktemp /tmp/maibida-deploy.XXXXXX.tar)"
trap 'rm -f "${TARBALL}"' EXIT

(cd "${REPO_ROOT}" && git archive --format=tar --output="${TARBALL}" HEAD)

install -d -o root -g root -m 755 "${APP_ROOT}" "${RELEASE_ROOT}" "${RELEASE_DIR}"
tar -xpf "${TARBALL}" -C "${RELEASE_DIR}"

chown -R root:www-data "${RELEASE_DIR}"
find "${RELEASE_DIR}" -type d -exec chmod 755 {} +
find "${RELEASE_DIR}" -type f -exec chmod 644 {} +
chmod 755 "${RELEASE_DIR}"/tools/deploy/*.sh

install -d -o www-data -g www-data -m 750 "${MESSAGE_DIR}"

ln -sfn "${RELEASE_DIR}" "${CURRENT_LINK}.tmp"
mv -Tf "${CURRENT_LINK}.tmp" "${CURRENT_LINK}"

install -d -m 755 /etc/nginx/snippets /etc/nginx/sites-available /etc/nginx/sites-enabled
install -m 644 "${RELEASE_DIR}/tools/deploy/maibida-http-maps.conf" /etc/nginx/snippets/
install -m 644 "${RELEASE_DIR}/tools/deploy/maibida-security-headers.conf" /etc/nginx/snippets/
install -m 644 "${RELEASE_DIR}/tools/deploy/maibida.locations.conf" /etc/nginx/snippets/

if [[ -f "${CERT_FILE}" ]]; then
  install -m 644 "${RELEASE_DIR}/tools/deploy/maibida.nginx.conf" /etc/nginx/sites-available/maibida.conf
else
  install -m 644 "${RELEASE_DIR}/tools/deploy/maibida.nginx.http-only.conf" /etc/nginx/sites-available/maibida.conf
fi

ln -sfn /etc/nginx/sites-available/maibida.conf /etc/nginx/sites-enabled/maibida.conf
ln -sfn /dev/null /etc/nginx/sites-enabled/default

install -m 644 "${RELEASE_DIR}/tools/deploy/maibida-api.service" /etc/systemd/system/
install -m 644 "${RELEASE_DIR}/tools/deploy/maibida-purge.service" /etc/systemd/system/
install -m 644 "${RELEASE_DIR}/tools/deploy/maibida-purge.timer" /etc/systemd/system/

systemctl daemon-reload
systemctl enable --now maibida-api.service maibida-purge.timer
systemctl restart maibida-api.service

nginx -t
systemctl enable --now nginx
systemctl reload nginx

if [[ -f "${CERT_FILE}" ]]; then
  curl --fail --silent --show-error --insecure \
    --resolve www.maibida.com:443:127.0.0.1 \
    "https://www.maibida.com/index.html" >/dev/null
else
  curl --fail --silent --show-error \
    --resolve www.maibida.com:80:127.0.0.1 \
    "http://www.maibida.com/index.html" >/dev/null
fi

api_code="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' \
  --request POST --header 'Content-Type: application/json' --data '{}' \
  http://127.0.0.1:8899/api/messages)"
[[ "${api_code}" == "400" ]]

printf '\nDeployed %s\nCurrent release: %s\nMessage store: %s\n' \
  "$(git -C "${REPO_ROOT}" rev-parse --short HEAD)" "${RELEASE_DIR}" "${MESSAGE_DIR}/messages.ndjson"
