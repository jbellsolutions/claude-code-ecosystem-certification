# Claude Code Ecosystem Certification

Static one-pager built from the supplied Descript video exports, arranged in source order, with transcript-derived curriculum copy, branded graphics, and optional video packaging scripts.

## What is included

- `index.html`, `styles.css`, `app.js`
  - GitHub Pages friendly landing page at repo root
- `site/data/course-data.json`
  - Source-of-truth course manifest used by the site and media scripts
- `transcripts/raw_srt`
  - Subtitle tracks extracted from the non-empty source videos
- `transcripts/plain_text`
  - Cleaned transcript text used for page excerpts and curriculum development
- `site/assets/posters`
  - Poster frames extracted from the supplied videos
- `site/assets/brand`
  - Generated hero art, social card, intro slate, outro slate, and module title slates
- `scripts/extract_assets.py`
  - Rebuilds posters and transcript files from the original Descript exports
- `scripts/render_brand_assets.py`
  - Rebuilds the branded PNG assets
- `scripts/render_video_package.py`
  - Optionally renders branded MP4 packages with intro/outro slates and audio normalization

## Preview locally

Run a static server from the repo root:

```bash
python3 -m http.server 8000
```

Then open `http://127.0.0.1:8000`.

## Regenerate assets

If the original source files are still in `/Users/home/Downloads/Descript videos`:

```bash
python3 scripts/extract_assets.py
python3 scripts/render_brand_assets.py
python3 scripts/render_video_package.py
```

## Notes

- The provided `M5` and `M6` exports were zero-byte placeholders, so the delivered curriculum preserves the usable order from the supplied source set: `M1`, `M2`, `M3`, `M4`, `M7`, `M8`, `M9`.
- Rendered MP4s are intentionally ignored by git because they are large. The repo keeps the scripts and branding needed to recreate them locally.
