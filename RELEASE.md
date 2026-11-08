# Release Notes

This project uses date-based production releases. Each entry records the
deployed Git revision, user-facing changes, infrastructure changes, and
operational follow-up.

## 2026-11-08 - Initial Production Release

- Git revision: `26e9140`
- Production URL: `https://www.maibida.com/`
- Server: Ubuntu 24.04, Tencent Cloud Shanghai
- Release directory: `/var/www/maibida/releases/20261108195947`

### Website

- Published the initial static multilingual corporate website.
- Enabled the clean canonical homepage URL at `/` and redirected
  `/index.html` to `/`.
- Included localized homepages, product pages, compliance pages, contact
  pages, `robots.txt`, and `sitemap.xml`.
- Preserved the OCR-rebuilt selectable HTML tables and semantic diagram text.

### Inquiry Service

- Deployed the dependency-free Node.js inquiry API on
  `127.0.0.1:8899`.
- Exposed the service through Nginx at `POST /api/messages`.
- Stored submissions outside the web root in
  `/var/lib/maibida/messages/messages.ndjson`.
- Enforced request-size limits, same-origin controls, rate limiting, and a
  24-month retention policy.
- Enabled the `maibida-purge.timer` systemd timer for retention enforcement.

### Web Server And Security

- Installed and enabled Nginx 1.24 with the production site configuration.
- Redirected HTTP traffic and the apex domain to
  `https://www.maibida.com/`.
- Closed direct requests to the server IP address with Nginx status `444`.
- Added HSTS, Content Security Policy, `X-Frame-Options`,
  `X-Content-Type-Options`, and `Referrer-Policy` headers.
- Configured no-cache headers for HTML and SEO files, and long cache headers
  for static assets.
- Enabled the host firewall for SSH, HTTP, and HTTPS only.

### TLS

- Installed the Tencent Cloud Nginx certificate covering
  `www.maibida.com` and `maibida.com`.
- Certificate validity: 2026-11-08 through 2027-02-06.
- TLS 1.2 and TLS 1.3 are enabled; HTTP/2 is active.

### Verification

- `nginx -t` passed.
- The full production acceptance suite passed with 25 successful checks and
  no failures.
- Public HTTPS, HTTP-to-HTTPS redirects, apex-to-www redirects, localized
  pages, compliance pages, the inquiry API, and private-store blocking were
  verified.

### Follow-Up

- Renew or replace the Tencent Cloud certificate before 2027-02-06.
- Submit `https://www.maibida.com/sitemap.xml` in Google Search Console.
- If Tencent Cloud CDN or EdgeOne is introduced, configure real visitor IP
  handling, edge cache rules, WAF/rate limiting, and origin access restrictions.
