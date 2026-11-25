# Commercial Product Site Redesign

This directory contains the local-only commercial redesign pipeline for the
Chinese and US English editions. The visual direction is product-led: dense
merchandising, direct specifications, technical proof and clear selection
paths rather than an editorial, whitespace-heavy presentation.

## Scope

Rebuilt entirely:

- `index.html`
- `index.en-US.html`

Premium interior shell applied:

- `product/*.html` and `product/*.en-US.html`
- `productlist/*.html` and `productlist/*.en-US.html`
- `contact.html` and `contact.en-US.html`
- `privacy.html` and `privacy.en-US.html`
- `terms.html` and `terms.en-US.html`

Other locale editions are intentionally unchanged.

## Assets

`derive-assets.js` creates text-free crops from the existing product
photography. It requires Sharp:

```bash
node tools/redesign/derive-assets.js
```

Outputs are stored under `cn/images/redesign/`.

`build-product-assets.py` composes seven new live-site product stages from the
same Maibida photography:

```bash
python tools/redesign/build-product-assets.py
```

Outputs for the product-family pages are stored under
`cn/images/redesign/products/`.

## Build

The homepage builder reads metadata from the pinned pre-redesign commit
`86f6b2e`, preserving canonical URLs, hreflang entries, structured data,
analytics and favicon declarations.

```bash
python tools/redesign/build-home.py
python tools/redesign/apply-inner-shell.py
python tools/redesign/build-product-pages.py
```

## Verification

```bash
python tools/redesign/test-build-home.py
python tools/redesign/test-inner-shell.py
python tools/redesign/test-product-pages.py
node tools/check-website-quality.js --static-only
node tools/check-website-quality.js
```

The full browser suite requires Playwright. The implementation was also
checked across 390, 768 and 1440 pixel viewports for every selected subpage.
