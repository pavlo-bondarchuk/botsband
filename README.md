# BotsBand static frontend

Static HTML/CSS/JavaScript reconstruction of https://botsband.online/.

## Preview

https://pavlo-bondarchuk.github.io/botsband/

## Structure

- `index.html` — static homepage markup
- `assets/css/style.css` — responsive layout and styles
- `assets/css/motion.css` — animations and ticker
- `assets/js/main.js` — navigation, dialog, and form
- `assets/js/motion.js` — scroll reveals and dynamic logo ticker
- `assets/img/` — local image destination
- `scripts/archive_assets.py` — original public asset archiver
- `scripts/visual_review.py` — desktop/mobile browser smoke checks and screenshots
- `scripts/compare_images.py` — pixel comparison reports

## Mirror source assets

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4
python scripts/archive_assets.py
```

The archive script downloads public images, stylesheets, scripts, and font files discovered on the current original homepage. It updates image URLs in `index.html`, saves downloaded assets under `assets/`, and creates `assets/asset-manifest.json`.

Downloaded original CSS and JS are preserved in `assets/css/original/` and `assets/js/original/`. These WordPress-dependent bundles are **not** automatically loaded by the standalone page. Treat them as references for careful behavior migration, not as working standalone components.

## Browser comparison

```bash
pip install playwright pillow
python -m playwright install chromium
python scripts/visual_review.py
python scripts/compare_images.py
```

Screenshots and reports are generated under `reports/`. Compare the images manually, because pixel similarity alone cannot prove interactive parity.

## Status

The first-page design and a subset of behaviors have been reconstructed. Full image localization, full original content, WP form submission, slider parity, and pixel-perfect visual fidelity remain unverified until the archive and visual testing jobs have run successfully.

At the time of setup, GitHub Actions custom archive jobs failed before a runner was assigned (jobs exposed no executed steps), while GitHub Pages deployments succeeded. Check the Actions workflow run details to identify the account/runner restriction or execute the scripts locally.

The static contact form currently opens an email draft rather than submitting to the original WordPress backend.
