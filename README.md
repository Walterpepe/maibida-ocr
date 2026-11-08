# Maibida Website

Static, multilingual corporate website for Maibida, served by Nginx on Ubuntu
with a small dependency-free Node.js service for inquiry form submissions.

The production site is `https://www.maibida.com/`.

## Repository Layout

- `index*.html` and localized page variants: public website pages.
- `cn/`, `product/`, `productlist/`, `tools/`, `UserFiles/`, and `plug-in/`:
  site content, styles, scripts, images, downloadable files, and product pages.
- `tools/preview-server.js`: local preview server and the production inquiry
  API service.
- `tools/deploy/`: Nginx configuration, systemd units, firewall setup, TLS
  deployment, and production acceptance checks.
- `sitemap.xml` and `robots.txt`: search-engine controls.
- `README-OCR-REBUILD.md`: notes for the OCR-to-HTML rebuild work.

## Local Preview

The site has no build step. Run the Node.js preview server from the repository
root:

```bash
node tools/preview-server.js 8899
```

Then open:

```text
http://127.0.0.1:8899/
```

The preview server also exposes `POST /api/messages` and stores local test
submissions outside the web root.

## Production Architecture

```text
Visitor
   |
   v
Nginx :80/:443
   |                         |
   | static files            | /api/messages
   v                         v
/var/www/maibida/current    127.0.0.1:8899 Node API
                              |
                              v
                    /var/lib/maibida/messages/messages.ndjson
```

Each deployment creates a timestamped directory under
`/var/www/maibida/releases/` and updates the `/var/www/maibida/current`
symlink. The message store remains outside the web root and is never served as
a static file.

## First Server Setup

Run on a fresh Ubuntu 24.04 server:

```bash
sudo tools/deploy/bootstrap.sh
```

This installs Nginx, Node.js, Certbot, and support tools, then deploys the
current committed `HEAD`.

## Deploy A New Revision

Only committed files are published, so commit or stash local changes first.

```bash
sudo tools/deploy/deploy.sh
```

Roll back by pointing the current symlink at an earlier release and restarting
the local services:

```bash
sudo ln -sfn /var/www/maibida/releases/RELEASE_ID /var/www/maibida/current
sudo systemctl restart maibida-api.service
sudo systemctl reload nginx
```

## TLS And DNS

The Nginx HTTPS profile expects these files:

```text
/etc/letsencrypt/live/www.maibida.com/fullchain.pem
/etc/letsencrypt/live/www.maibida.com/privkey.pem
```

DNS should point both `www.maibida.com` and `maibida.com` at the production
server. The apex domain and HTTP traffic permanently redirect to
`https://www.maibida.com/`.

For an automatically renewed Let's Encrypt certificate, run:

```bash
sudo tools/deploy/issue-cert.sh admin@example.com
```

A manually issued certificate can also be installed at the paths above. Manual
certificates must be renewed and reinstalled before their expiry date.

## Firewall And Verification

Apply the baseline firewall rules:

```bash
sudo tools/deploy/configure-firewall.sh
```

After DNS and TLS are active, run the production acceptance suite:

```bash
sh tools/deploy/check-production.sh
```

The suite checks DNS, redirects, TLS, security headers, localized pages,
compliance pages, the inquiry API, private-data blocking, image delivery,
`robots.txt`, and `sitemap.xml`.

More operational details are available in
[`tools/deploy/README.md`](tools/deploy/README.md).
