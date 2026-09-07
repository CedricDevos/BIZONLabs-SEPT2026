# BIZON Labs Website

Semi-stealth landing page for BIZON Labs.

## Build

```bash
python3 build_site.py
```

The generated static site is written to `dist/`.

## Preview Locally

```bash
python3 -m http.server 8000 --directory dist
```

Then open `http://localhost:8000`.

## Edit Content

Most public copy lives in `content/site.json`.

The page template lives in `site/index.template.html`, with styling in `site/styles.css`.

## Brand Assets

Logo assets are stored in `assets/logos/`.

## Images And Videos

Add approved public-facing photos and videos to `assets/media-library/`.

After running `python3 build_site.py`, they appear automatically in the media section of `dist/index.html`.

Use JPG, JPEG, PNG, WEBP, GIF, MP4, MOV, or WEBM. MP4 is best for reliable website playback.

## Papers

Add approved public-facing paper PDFs to `assets/papers/`.

After running `python3 build_site.py`, each PDF appears automatically in the Scientific Expertise section as a first-page preview. The preview links to the PDF.

## GoDaddy

For static hosting, upload the contents of `dist/` to the public web directory for the domain.
