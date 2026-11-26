# Apple-Grade Homepage Experiment

This directory contains the local-only redesign pipeline for the Chinese and
US English editions.

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

`build-product-assets.py` composes seven legacy product stages from the same
Maibida photography:

```bash
python tools/redesign/build-product-assets.py
```

Outputs for the product-family pages are stored under
`cn/images/redesign/products/`.

`build-editorial-images.py` encodes the live-site product photography. Every
marketing hero is a curated 4:3 outpaint built from the original photograph,
keeping the full product silhouette, reflections, cables and machine sections
inside a seamless studio frame:

```bash
python tools/redesign/build-editorial-images.py
```

The full-resolution PNG masters live in `tools/redesign/source/`. The build
converts them to served WebP assets without recomposing or cropping the
products.

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
