"""Marker-stroke backgrounds for Hoodlanthropy: solid navy ink, wavy marker
edges, faint streak texture, optional dry-brush end fade. No speckle field.
Sized for CSS border-image (slice 46): corners/edges keep native rag scale."""
import os, random
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "media")
W, H = 720, 180
EDGE = 16                # max blank margin the rag lives in
INK = (10, 22, 36)       # sampled from the retired swipe strips — the tier ink family

def wavy(rng, n, amp, base):
    """bounded random walk -> marker edge line"""
    pts, v, y = [], 0.0, base
    for i in range(n):
        v += rng.uniform(-1.6, 1.6)
        v *= 0.82
        y += v
        y = max(base - amp, min(base + amp, y))
        pts.append(y)
    return pts

def make(name, seed, fade=None):
    rng = random.Random(seed)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    step = 4
    n = W // step + 2
    top = wavy(rng, n, 7, EDGE)
    bot = wavy(rng, n, 7, H - EDGE)
    poly = []
    # left end: slightly ragged vertical
    lx = wavy(rng, 40, 5, EDGE)
    rx = wavy(rng, 40, 5, W - EDGE)
    for i in range(n):
        poly.append((i * step, top[i]))
    for i, y in enumerate(range(int(top[-1]), int(bot[-1]), 4)):
        poly.append((rx[min(i, 39)], y))
    for i in range(n - 1, -1, -1):
        poly.append((i * step, bot[i]))
    for i, y in enumerate(range(int(bot[0]), int(top[0]), -4)):
        poly.append((lx[min(i, 39)], y))
    d.polygon(poly, fill=INK + (255,))

    # streak texture near the edges only — the fill slice must stay flat ink,
    # or border-image stretch smears any mid-face texture on tall blocks
    for _ in range(rng.randint(10, 14)):
        y = rng.choice([rng.randint(EDGE + 4, 42), rng.randint(H - 42, H - EDGE - 4)])
        h = rng.randint(2, 4)
        x0 = rng.randint(0, W // 3)
        x1 = rng.randint(2 * W // 3, W)
        delta = rng.choice([-1, 1]) * rng.randint(5, 9)
        band = tuple(max(0, min(255, cch + delta)) for cch in INK)
        d.rectangle([x0, y, x1, y + h], fill=band + (255,))

    # edge nicks: small bites out of the rag, top and bottom only
    for _ in range(rng.randint(6, 9)):
        x = rng.randint(30, W - 30)
        w = rng.randint(6, 18)
        if rng.random() < 0.5:
            y = top[min(x // step, n - 1)]
            d.polygon([(x, y - 2), (x + w, y - 2), (x + w // 2, y + rng.randint(4, 9))], fill=(0, 0, 0, 0))
        else:
            y = bot[min(x // step, n - 1)]
            d.polygon([(x, y + 2), (x + w, y + 2), (x + w // 2, y - rng.randint(4, 9))], fill=(0, 0, 0, 0))

    # dry-brush end: the stroke lifts off in streaky slices
    if fade:
        px = im.load()
        fw = 110
        # per-row dryness: rows dry out in streaks (like bristles), not per-pixel salt
        rowbias = [0.0] * H
        b = 0.0
        for y in range(H):
            if y % rng.randint(3, 5) == 0:
                b = rng.uniform(-0.35, 0.35)
            rowbias[y] = b
        for x in range(fw):
            fx = (W - 1 - x) if fade == "r" else x
            t = 1 - x / fw          # 1 at the very end -> most eaten
            for y in range(H):
                if px[fx, y][3] == 0:
                    continue
                if t + rowbias[y] > rng.uniform(0.35, 0.75):
                    px[fx, y] = (0, 0, 0, 0)

    # no grain: the fixed #grade overlay grains the whole page, and any texture
    # in the fill slice would smear when border-image stretches tall blocks

    im.save(os.path.join(OUT, name), "WEBP", quality=88)
    print("wrote", name)

make("marker-a.webp", 11)
make("marker-b.webp", 47)
make("marker-l.webp", 23, fade="r")   # stroke ends dry on the right (single-line blocks only)
