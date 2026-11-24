# Maibida Production Deployment

This setup is designed for a low-traffic static corporate website on Ubuntu 24.04.
EdgeOne serves cached public assets and runs a lightweight validation function for
`POST /api/messages`. Nginx and the Node service remain the authoritative origin.

## Architecture

```text
Visitor / Googlebot
        |
        v
EdgeOne CDN / Edge Function
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
symlink at `/var/www/maibida/current`. During the release build, every CSS/JS
reference is rewritten to the deployment minute (`v=YYYYMMDDHHMM`) before the
symlink switches. This keeps each release's assets unique while allowing the
EdgeOne stable-mode HTML cache to avoid origin round trips for nearby visitors.

Before the symlink switches, `deploy.sh` runs the static website-quality gate.
It blocks releases that lose contact-form accessibility metadata, explicit
labels, same-origin submission, safe external links, image alternatives, or
required page metadata.

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

## Inquiry Notifications

Notifications run only after the inquiry has been appended to
`messages.ndjson`. They are asynchronous, so a failed notification never turns
a successful form submission into an error. Configure either or both channels
in a root-owned environment file:

```bash
sudo install -d -m 755 /etc/maibida
sudo install -m 600 tools/deploy/notifications.env.example /etc/maibida/notifications.env
sudo editor /etc/maibida/notifications.env
sudo systemctl restart maibida-api.service
```

For WeChat delivery, create a WeCom group robot and set
`MAIBIDA_WECOM_WEBHOOK_URL`. The service posts a Markdown summary to the group
robot. Personal WeChat accounts cannot be automated through an official
standalone bot API; WeCom group robots, WeChat Official Accounts, or enterprise
WeChat APIs are the supported paths.

Typical WeCom setup:

1. Open the target group in WeCom.
2. Open group settings, add a group robot, and copy its webhook URL.
3. Set `MAIBIDA_WECOM_WEBHOOK_URL` in `/etc/maibida/notifications.env`.
4. Restart `maibida-api.service`.

For email delivery through SMTP, set `MAIBIDA_SMTP_HOST`,
`MAIBIDA_SMTP_USER`, `MAIBIDA_SMTP_PASS`, `MAIBIDA_SMTP_FROM`, and
`MAIBIDA_EMAIL_TO`. Port 465 uses implicit TLS and port 587 uses STARTTLS. The
notification uses a dependency-free Node SMTP client; credentials remain in
process memory and are never written to a temporary file.

For Tencent Exmail, use `smtp.exmail.qq.com` on port `465` or `587`, the full mailbox
address as `MAIBIDA_SMTP_USER` and `MAIBIDA_SMTP_FROM`, and the mailbox SMTP
authorization code as `MAIBIDA_SMTP_PASS`. QQ Mail and other providers work the
same way when they support SMTP on port 465 or port 587.

Preview formatting without sending:

```bash
node tools/test-notifications.js
```

Send a sample through the configured real channels:

```bash
MAIBIDA_NOTIFY_LIVE=1 node tools/test-notifications.js
```

Because systemd keeps the production credentials in its own environment, a
server-side live test can be run without exposing them in shell history:

```bash
sudo systemd-run --quiet --wait --pipe --collect \
  --property=EnvironmentFile=/etc/maibida/notifications.env \
  --property=Environment=MAIBIDA_NOTIFY_LIVE=1 \
  /usr/bin/node /home/ubuntu/maibida-ocr/tools/test-notifications.js
```

## Local Firewall

Enable the baseline firewall while preserving SSH access:

```bash
sudo tools/deploy/configure-firewall.sh
```

After choosing a CDN, replace the broad web rules with that provider's published
origin IP ranges where practical, or use authenticated origin pulls. Keep port
22 available for your SSH access path and port 80 open for certificate renewal.

## CDN Cutover

Recommended CDN behavior:

- Use `https://www.maibida.com` as the canonical public hostname.
- Configure the CDN origin with HTTPS, the `www.maibida.com` SNI/Host value, and
  the current origin certificate.
- Cache images, video, PDFs, fonts, CSS, and JavaScript for seven days.
- During active development, do not cache HTML, `robots.txt`, `sitemap.xml`,
  or `/api/messages`.
- In stable mode, force a short EdgeOne node-cache TTL for `/` and `*.html`.
  Browsers still receive `Cache-Control: no-cache` and revalidate with the
  nearby edge node. Purge all HTML URLs immediately after every release.
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

- The canonical host and Chinese homepage URL are `https://www.maibida.com/`.
- The apex domain and HTTP traffic use 301 redirects.
- Nginx serves `/` without exposing `/index.html`; the old `/index.html` URL
  uses a 301 redirect to `/`.
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
the SEO files. It also verifies that the release contact form is same-origin and
retains the autocomplete and live-error accessibility wiring.

Measure the live HTTP TTFB from six countries with Globalping:

```bash
node tools/measure-global-latency.js
node tools/measure-global-latency.js --id MEASUREMENT_ID
```

The output includes `EO-Cache-Status`, DNS/TCP/TLS timings, first-byte latency,
and total request time for each probe.

## EdgeOne Automation

EdgeOne uses the Tencent Cloud `teo` API, version `2022-09-01`. The repository
includes a dependency-free TC3-HMAC-SHA256 client plus purge and function
deployment commands.

Create a root-owned environment file outside the repository:

```bash
sudo install -d -m 755 /etc/maibida
sudo install -m 600 tools/edgeone/edgeone.env.example /etc/maibida/edgeone.env
sudo editor /etc/maibida/edgeone.env
```

Set `TENCENTCLOUD_SECRET_ID` and `TENCENTCLOUD_SECRET_KEY`. For an international
Tencent Cloud account set `TENCENTCLOUD_REGION=intl`; for a mainland account
use the default `https://teo.tencentcloudapi.com`. The configured zone is
`zone-3x9ct40r4u3w` and the public host is `www.maibida.com`.

The CAM policy needs these permissions:

```text
teo:CreatePurgeTask
teo:DescribeFunctions
teo:CreateFunction
teo:ModifyFunction
teo:DescribeFunctionRules
teo:CreateFunctionRule
teo:ModifyFunctionRule
teo:DescribeL7AccRules
teo:CreateL7AccRules
teo:ModifyL7AccRule
```

Preview the exact requests without sending credentials or making changes:

```bash
node tools/edgeone/edgeone-purge.js --dry-run
node tools/edgeone/deploy-function.js --dry-run
node tools/edgeone/configure-html-cache.js --dry-run
```

Deploy the contact API function:

```bash
sudo --preserve-env=EDGEONE_ENV_FILE \
  node tools/edgeone/deploy-function.js
```

The first run discovers a function named `maibida-contact-api` or creates it,
then creates a `www.maibida.com` + `/api/messages` trigger rule. Copy the returned
function/rule IDs into `/etc/maibida/edgeone.env`; later deploys update the
existing function deterministically.

Configure the HTML cache profile:

```bash
node tools/edgeone/configure-html-cache.js --mode stable --ttl 600
node tools/edgeone/configure-html-cache.js --mode development
```

Stable mode forces node caching for `/` and `*.html`, while API and SEO paths
keep their origin policies. Development mode disables that rule. The default
`EDGEONE_HTML_CACHE_TTL` is 600 seconds; deployment purges override it.

`tools/deploy/deploy.sh` invokes the function deployer, applies the configured
HTML cache mode, and then purges the homepage plus every HTML URL in batches of
50. Missing EdgeOne credentials produce a warning; set
`EDGEONE_FUNCTION_STRICT=1`, `EDGEONE_HTML_CACHE_STRICT=1`, or
`EDGEONE_PURGE_STRICT=1` when a release must fail instead.

Manual purge and targeted URL purge:

```bash
node tools/edgeone/edgeone-purge.js --dry-run
node tools/edgeone/edgeone-purge.js
node tools/edgeone/edgeone-purge.js --html --repo-root .
node tools/edgeone/edgeone-purge.js \
  --url https://www.maibida.com/contact.html
```

The Edge Function rejects non-POST requests and invalid content types, enforces
the 16 KB body limit, validates required fields and consent, silently absorbs
honeypot submissions, and applies a small per-isolate rate limit. Nginx and the
origin Node API remain authoritative for persistence and the shared request
limit. A function's in-memory limit is not a globally distributed quota.
