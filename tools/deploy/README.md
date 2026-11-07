# Maibida Production Deployment

This setup is designed for a low-traffic static corporate website on Ubuntu 24.04.
Nginx serves the public files, while a small dependency-free Node service handles
only `POST /api/messages` inquiry submissions.

## Architecture

```text
Visitor / Googlebot
        |
        v
Future CDN: TLS, global cache, WAF, rate limiting
        |
        v
Ubuntu origin: Nginx :80/:443
        |                         |
        | static files            | /api/messages
        v                         v
/var/www/maibida/current    127.0.0.1:8899 Node API
                                  |
                                  v
                        /var/lib/maibida/messages/messages.ndjson
```

The message store is outside the web root and is not publicly served. The Node
process listens only on loopback and runs as the unprivileged `www-data` user.

## First Server Setup

Run this from the repository root:

```bash
sudo tools/deploy/bootstrap.sh
```

The script installs Nginx, Ubuntu's Node.js runtime, Certbot, and support tools,
then deploys the current committed `HEAD`. Uncommitted files and ignored artifacts
are not published.

The initial Nginx profile is HTTP-only because `www.maibida.com` does not resolve
yet. Direct requests to the server IP are closed with Nginx status 444 so the IP
address does not become a duplicate indexed site.

## DNS And HTTPS

1. Point DNS at the server:
   - `www.maibida.com`: `A`/`AAAA` record for the server
   - `maibida.com`: `A`/`AAAA` record for the server
2. Wait for DNS to resolve.
3. Issue the certificate and switch Nginx to the HTTPS profile:

```bash
sudo tools/deploy/issue-cert.sh ops@example.com
```

The certificate covers both `www.maibida.com` and `maibida.com`. Nginx permanently
redirects the apex domain and HTTP traffic to `https://www.maibida.com`.

## Deployments And Rollback

Deploy a new committed revision:

```bash
sudo tools/deploy/deploy.sh
```

Each release is unpacked under `/var/www/maibida/releases/`. The live path is a
symlink at `/var/www/maibida/current`.

Roll back by pointing the symlink at an earlier release and restarting the local
services:

```bash
sudo ln -sfn /var/www/maibida/releases/RELEASE_ID /var/www/maibida/current
sudo systemctl restart maibida-api.service
sudo systemctl reload nginx
```

## Service Operations

```bash
systemctl status maibida-api.service
journalctl -u maibida-api.service -f
systemctl status maibida-purge.timer
journalctl -u maibida-purge.service
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

Inquiry messages are stored in:

```text
/var/lib/maibida/messages/messages.ndjson
```

The monthly systemd timer enforces the 24-month retention promise used by the
privacy pages.

## CDN Cutover

Recommended CDN behavior:

- Use `https://www.maibida.com` as the canonical public hostname.
- Configure the CDN origin with HTTPS, the `www.maibida.com` SNI/Host value, and
  the current origin certificate.
- Cache images, video, PDFs, fonts, CSS, and JavaScript. Do not cache HTML,
  `robots.txt`, `sitemap.xml`, or `/api/messages`.
- Respect the origin's `Cache-Control` and `CDN-Cache-Control` headers.
- Enable the CDN WAF, bot protection, and edge rate limiting for `/api/messages`.
- Configure the provider's trusted IP ranges in Nginx with `set_real_ip_from`
  and `real_ip_header` so application rate limits see the visitor IP.
- After cutover, restrict origin ports 80/443 to the CDN ranges or use CDN
  authenticated origin pulls where supported.
- Serve Googlebot the same status codes, HTML, canonicals, hreflang tags, and
  assets as ordinary visitors.

The origin already sends long cache headers for static assets, no-cache headers
for HTML and SEO files, `Vary: Accept` for optional WebP negotiation, and security
headers that can pass through unchanged.

## SEO Controls

- The canonical host is `https://www.maibida.com`.
- The apex domain and HTTP traffic use 301 redirects.
- `/` redirects to `/index.html`, matching the existing canonical tags and
  sitemap entries.
- Retired locale URLs use permanent redirects.
- `robots.txt` allows search entry points and points to the XML sitemap.
- Custom error pages send `X-Robots-Tag: noindex, follow`.
- After DNS cutover, verify both domains and submit
  `https://www.maibida.com/sitemap.xml` in Google Search Console.

## Go-Live Verification

After DNS and HTTPS are active:

```bash
sh tools/deploy/check-production.sh
```

The check verifies DNS, redirects, TLS, security headers, localized pages,
compliance pages, the inquiry API, private-data blocking, image delivery, and
the SEO files.
