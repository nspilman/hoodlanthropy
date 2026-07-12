# Hoodlanthropy

Marketing site for Hoodlanthropy LLC — philanthropic advisory for sport.

**Live site:** deployed to GitHub Pages automatically on every push to `main`.

## How to edit the site

All copy and structure live in one file:

```
site-src/hoodlanthropy_void_template.html
```

Edit the text there (it's plain HTML), commit, and push to `main`. GitHub
Actions rebuilds and deploys — the change is live in about a minute. You can
also edit directly on github.com if you don't have the repo checked out.

Do **not** edit `dist/` — it's generated and not checked in.

### Swapping media

The founder carousel media live in `media/`:

| File | Used as |
|------|---------|
| `media/founder-portrait.png` | Slide 1 — illustrated portrait |
| `media/founder-at-work.mp4` | Slide 2 — "at work" video |
| `media/founder-mind.mp4` | Slide 3 — "the mind" video |

Replace a file (keeping the same name), push, done. To add/remove slides,
edit the `.fc-frame` markup in the template and the `MEDIA` map in
`site-src/build.py`.

## Building locally (optional)

```
python3 site-src/build.py        # -> dist/index.html + dist/media/
python3 -m http.server -d dist   # preview at http://localhost:8000
```

No dependencies — stdlib only.

## How the build works

`site-src/build.py` takes the template and:

1. inlines `site-src/fonts.css` (Inter, woff2 embedded as data URIs — no
   Google Fonts request at runtime or build time) at `<!--FONTFACE-->`
2. injects `site-src/brainpts.json` at `__BRAIN_PTS__` — the particle cloud
   for the scroll-driven brain/heart constellation
3. replaces `__MEDIA_*__` placeholders with the `media/` paths

`site-src/build_brain_points.py` is how `brainpts.json` was generated —
it samples ~6000 points from `brain_nih.png` (public-domain NIH brain photo)
following the real gyri shading. You only need it (and Pillow) if you want to
regenerate the point cloud from a different image.
