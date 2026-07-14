#!/usr/bin/env python3
"""Build the Hoodlanthropy site into dist/.

Assembles the template with the embedded fonts, the brain point cloud,
and the founder media paths, then copies media alongside the output:

    python3 site-src/build.py

Output: dist/index.html + dist/media/ — a self-contained static site.
"""
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "site-src"
DIST = ROOT / "dist"

MEDIA = {
    "__MEDIA_IMG__": "media/founder-portrait.png",
    "__MEDIA_VID1__": "media/founder-at-work.mp4",
    "__MEDIA_VID2__": "media/founder-mind.mp4",
    "__MEDIA_SKY_NYC__": "media/skyline-nyc.webp",
    "__MEDIA_SKY_DC__": "media/skyline-dc.webp",
}

html = (SRC / "hoodlanthropy_void_template.html").read_text(encoding="utf-8")

# fonts.css holds the Inter @font-face blocks with woff2 data URIs, extracted
# once from Google Fonts so builds are deterministic and offline-safe
fonts = (SRC / "fonts.css").read_text(encoding="utf-8")
assert "<!--FONTFACE-->" in html
html = html.replace("<!--FONTFACE-->", "<style>\n" + fonts + "</style>")

pts = (SRC / "brainpts.json").read_text(encoding="utf-8").strip()
assert "__BRAIN_PTS__" in html
html = html.replace("__BRAIN_PTS__", pts)

for placeholder, rel_path in MEDIA.items():
    assert placeholder in html, placeholder
    assert (ROOT / rel_path).is_file(), rel_path
    html = html.replace(placeholder, rel_path)

DIST.mkdir(exist_ok=True)
(DIST / "index.html").write_text(html, encoding="utf-8")
shutil.copytree(ROOT / "media", DIST / "media", dirs_exist_ok=True)
print("built", DIST / "index.html", f"({len(html):,} bytes)")
