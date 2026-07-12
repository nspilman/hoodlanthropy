import json
import random
from PIL import Image, ImageDraw

SCRATCH = r"C:\Users\aj_al\AppData\Local\Temp\claude\C--Users-aj-al\e013dfe4-2999-408f-8e09-1431445e66b6\scratchpad"
random.seed(42)

img = Image.open(SCRATCH + r"\brain_nih.png").convert("RGB")
W, H = img.size
px = img.load()

# brain mask: beige/saturated pixels (excludes white bg and gray drop shadow)
def is_brain(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    if mx > 245 and mn > 235:          # white background
        return False
    sat = (mx - mn) / max(mx, 1)
    return sat > 0.12 and r > g > b * 0.9   # warm beige ordering

mask = []
lums = []
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        if is_brain(r, g, b):
            mask.append((x, y))
            lums.append(0.299 * r + 0.587 * g + 0.114 * b)

srt = sorted(lums)
p10, p92 = srt[int(len(srt) * 0.10)], srt[int(len(srt) * 0.92)]
print("mask px:", len(mask), "p10/p92:", round(p10), round(p92))

# silhouette boundary: mask pixels touching non-mask — gives the crisp outer edge
mask_set = set(mask)
boundary = [(x, y) for (x, y) in mask
            if (x - 1, y) not in mask_set or (x + 1, y) not in mask_set
            or (x, y - 1) not in mask_set or (x, y + 1) not in mask_set]
print("boundary px:", len(boundary))

# 22% of points trace the silhouette; the rest follow gyri shading
# (ridges dense+bright, sulci nearly empty — the fold structure IS the contrast)
N = 6000
pts = []
idx = list(range(len(mask)))
n_edge = int(N * 0.22)
for _ in range(n_edge):
    x, y = random.choice(boundary)
    x += random.uniform(-1.5, 1.5); y += random.uniform(-1.5, 1.5)
    pts.append((x, y, random.uniform(0.7, 1.0), random.uniform(0.5, 0.9)))
while len(pts) < N:
    i = random.choice(idx)
    ln = max(0.0, min(1.0, (lums[i] - p10) / (p92 - p10)))
    if random.random() < ln ** 2.2 + 0.02:
        x, y = mask[i]
        k = 0.25 + 0.75 * ln ** 1.3             # draw brightness follows shading
        pts.append((x, y, k, ln))

# normalize to units ~[-16,16], preserve aspect
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
span = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
scale = 16.0 / span

# clustered color patches: stable pseudo-random palette index per ~grid cell
PALETTE_W = [0.30, 0.22, 0.16, 0.12, 0.10, 0.10]  # amber, spark, court, sky, rose, peach
def cell_color(x, y):
    cxi, cyi = int(x // 26), int(y // 26)
    rnd = random.Random(cxi * 73856093 ^ cyi * 19349663)
    return rnd.choices(range(6), weights=PALETTE_W)[0]

out = []
for x, y, k, ln in pts:
    if ln > 0.82 and random.random() < 0.55:
        c = 6                                   # warm-white specular highlight on the brightest ridges
    elif random.random() > 0.12:
        c = cell_color(x, y)
    else:
        c = random.randrange(6)
    out.append([round((x - cx) * scale, 2), round((y - cy) * scale, 2), round(k, 2), c])

with open(SCRATCH + r"\brainpts.json", "w") as f:
    json.dump(out, f, separators=(",", ":"))
print("points:", len(out), "json bytes:", len(json.dumps(out, separators=(',', ':'))))

# preview render: triangles on black, roughly as the site draws them
PALETTE = ["#e87722", "#ffb829", "#35a87a", "#4e87b8", "#c14654", "#f0955a", "#f5efe6"]
pv = Image.new("RGB", (900, 700), "black")
d = ImageDraw.Draw(pv, "RGBA")
for ux, uy, k, c in out:
    sx = 450 + ux * 19
    sy = 340 + uy * 19
    s = random.uniform(1.1, 2.6)
    col = PALETTE[c]
    a = int(255 * k)
    rgb = tuple(int(col[i:i+2], 16) for i in (1, 3, 5)) + (a,)
    rot = random.uniform(0, 6.28)
    import math
    tri = [(sx + s * math.cos(rot + t), sy + s * math.sin(rot + t)) for t in (0, 2.09, 4.19)]
    d.polygon(tri, outline=rgb)
pv.save(SCRATCH + r"\brain_preview.png")
print("preview written")
