import base64
import re
import urllib.request

SCRATCH = r"C:\Users\aj_al\AppData\Local\Temp\claude\C--Users-aj-al\e013dfe4-2999-408f-8e09-1431445e66b6\scratchpad"
TEMPLATE = SCRATCH + r"\hoodlanthropy_void_template.html"
OUT_E = r"E:\Dennis Hoodlanthropy\hoodlanthropy_v5_void.html"
OUT_ART = SCRATCH + r"\hoodlanthropy_v5_artifact.html"

CSS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@200;400;600&display=swap"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req).read()


css = fetch(CSS_URL).decode("utf-8")
blocks = re.findall(r"/\* ([\w-]+) \*/\s*(@font-face\s*\{[^}]+\})", css)
latin = [b for name, b in blocks if name == "latin"]
print("latin blocks:", len(latin))

seen = {}
out_css = []
for block in latin:
    url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
    if url not in seen:
        data = fetch(url)
        seen[url] = "data:font/woff2;base64," + base64.b64encode(data).decode("ascii")
        print("embedded", url.split("/")[-1], len(data), "bytes")
    out_css.append(block.replace(url, seen[url]))

font_style = "<style>\n" + "\n".join(out_css) + "\n</style>"

html = open(TEMPLATE, encoding="utf-8").read()
html = html.replace("<!--FONTFACE-->", font_style)

brain_pts = open(SCRATCH + r"\brainpts.json", encoding="utf-8").read()
assert "__BRAIN_PTS__" in html
html = html.replace("__BRAIN_PTS__", brain_pts)
print("injected brain points:", len(brain_pts), "bytes")

MEDIA = {
    "__MEDIA_IMG__": ("Screenshot_2026-06-29_235827-removebg-preview.png", "image/png"),
    "__MEDIA_VID1__": ("u3362124173_httpss.mj.runNEg5FTp2-Sw_have_the_character_worki_7938288b-f22a-4892-aa4b-174d5a2038c3_1.mp4", "video/mp4"),
    "__MEDIA_VID2__": ("u3362124173_httpss.mj.runNEg5FTp2-Sw_go_into_the_mind_of_the__71c37275-9db6-43d3-b858-32758a6bf374_3.mp4", "video/mp4"),
}

# E: copy references the files sitting next to it
html_e = html
for ph, (fname, _) in MEDIA.items():
    html_e = html_e.replace(ph, fname)
open(OUT_E, "w", encoding="utf-8").write(html_e)
print("wrote", OUT_E)

# artifact copy embeds them as data URIs (CSP blocks file/network requests)
for ph, (fname, mime) in MEDIA.items():
    with open(r"E:\Dennis Hoodlanthropy" + "\\" + fname, "rb") as f:
        data = f.read()
    html = html.replace(ph, "data:%s;base64,%s" % (mime, base64.b64encode(data).decode("ascii")))
    print("embedded media", fname, len(data), "bytes")

title = re.search(r"<title>.*?</title>", html, re.S).group(0)
head_styles = re.findall(r"<style>.*?</style>", re.search(r"<head>.*?</head>", html, re.S).group(0), re.S)
body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
open(OUT_ART, "w", encoding="utf-8").write(title + "\n" + "\n".join(head_styles) + "\n" + body)
print("wrote", OUT_ART)
