#!/usr/bin/env sh
# Production go-live acceptance check for www.maibida.com (H1).
# Run AFTER DNS, TLS and the Node message service are deployed:
#   sh tools/deploy/check-production.sh
# Exits 0 only when every blocking check passes.
set -u
HOST=${1:-www.maibida.com}
BASE="https://$HOST"
PASS=0
FAIL=0

ok()   { PASS=$((PASS+1)); printf 'PASS  %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf 'FAIL  %s\n' "$1"; }
probe(){ curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$@" 2>/dev/null; }

printf '=== %s production acceptance ===\n' "$HOST"

# 1. DNS must resolve (H1 root cause: NXDOMAIN)
if nslookup "$HOST" >/dev/null 2>&1 || getent hosts "$HOST" >/dev/null 2>&1; then
  ok "DNS resolves: $HOST"
else
  bad "DNS does not resolve: $HOST (configure A/AAAA or CNAME at the registrar)"
fi

# 2. HTTP redirects to HTTPS
code=$(probe -I "http://$HOST/")
case "$code" in 301|302|307|308) ok "HTTP redirects to HTTPS ($code)";; *) bad "HTTP $code (expected 301/302)";; esac

# 3. HTTPS reachable
code=$(probe -I "$BASE/")
[ "$code" = 200 ] && ok "HTTPS homepage 200" || bad "HTTPS homepage returned $code"

# 4. TLS certificate chain
if curl -sS -o /dev/null --max-time 15 "$BASE/" 2>/dev/null; then
  ok "TLS handshake and certificate chain valid"
else
  bad "TLS handshake failed (check fullchain.pem / certificate chain)"
fi

# 5. Security headers (M9)
hdr=$(curl -sSI --max-time 15 "$BASE/" 2>/dev/null | tr 'A-Z' 'a-z')
for h in strict-transport-security content-security-policy x-frame-options x-content-type-options referrer-policy; do
  case "$hdr" in *"$h:"*) ok "security header: $h";; *) bad "missing security header: $h";; esac
done

# 6. robots.txt / sitemap.xml (SEO)
code=$(probe "$BASE/robots.txt")
[ "$code" = 200 ] && ok "robots.txt 200" || bad "robots.txt $code"
code=$(probe "$BASE/sitemap.xml")
[ "$code" = 200 ] && ok "sitemap.xml 200" || bad "sitemap.xml $code"

# 7. Googlebot user agent must get the same content
code=$(probe -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "$BASE/")
[ "$code" = 200 ] && ok "Googlebot UA 200" || bad "Googlebot UA $code"

# 8. Localized pages reachable in the six target markets
for p in index.es-MX.html index.en-SG.html index.vi-VN.html index.th-TH.html index.ko-KR.html; do
  code=$(probe "$BASE/$p")
  [ "$code" = 200 ] && ok "locale page $p 200" || bad "locale page $p $code"
done

# 9. Compliance pages reachable
for p in privacy.html privacy.es-MX.html terms.html terms.es-MX.html; do
  code=$(probe "$BASE/$p")
  [ "$code" = 200 ] && ok "compliance page $p 200" || bad "compliance page $p $code"
done

# 10. Message endpoint must be a real API, not a static 404 (H3)
code=$(probe -X POST -H 'Content-Type: application/json' \
  -d '{"name":"go-live probe","email":"probe@example.com","message":"probe","consent":"yes"}' \
  "$BASE/api/messages")
[ "$code" = 200 ] && ok "POST /api/messages 200 (Node service deployed)" || \
  bad "POST /api/messages $code (deploy the Node service or replace the backend)"

# 11. Private message store must never be statically readable
code=$(probe "$BASE/messages.ndjson")
[ "$code" = 404 ] || [ "$code" = 403 ] && ok "private store not readable ($code)" || \
  bad "private store returned $code"

# 12. WebP content negotiation (M8)
ctype=$(curl -sSI --max-time 15 -H 'Accept: image/webp,*/*' \
  "$BASE/UserFiles/upload/image/20260130/6390537782397634082084337.png" 2>/dev/null \
  | tr 'A-Z' 'a-z' | grep 'content-type' | head -1)
case "$ctype" in *webp*) ok "WebP negotiation active";; *) bad "WebP negotiation not active (check nginx map + Vary: Accept)";; esac

printf '\n=== RESULT: %s passed, %s failed ===\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] && printf 'GO-LIVE CHECK: PASS\n' || printf 'GO-LIVE CHECK: BLOCKED\n'
exit "$FAIL"
