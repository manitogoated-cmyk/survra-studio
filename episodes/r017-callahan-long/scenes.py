"""Case 017, the full case file (16:9) - Steven Callahan, 76 days adrift in an inflatable raft in 1982.
The story is filmed in 3D (world3d.py). This file holds the flat inserts on a 1920x1080 canvas (a drawn diagram of his
route before the sinking, a drawing of his log with the drift creeping west, and Rook's case board), the 2D overlays
drawn on top of 3D shots, and the thumbnail. Every card is a drawing made for this film: the route and the drift are
diagrams, marked as diagrams and not to scale, with no map copied. Captions run in a band low in the frame and the label
sits top right, so the cards keep both clear."""
import math
import os

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1920, 1080
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER, SEA = h('FF7A1A'), h('FFB000'), h('EFE6CC'), h('2A6A8E')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def plain(cv, s, x, y, size, color, weight=700, centre=True):
    f = font(size, weight)
    w = f.measureText(s)
    cv.drawTextBlob(skia.TextBlob(s, f), x - (w / 2 if centre else 0), y, P(color))
    return w


def push(cv, c, amount=0.1, sway=0.0):
    """A slow push in on a card (and a little sway), so a held card is never a still picture."""
    z = 1 + amount * c.k
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.rotate(sway * math.sin(c.t * 1.3))
    cv.translate(-W / 2 + 26 * math.sin(c.t * 0.9), -H / 2 + 14 * math.sin(c.t * 1.4))


def paper(cv, x, y, w_, h_, col=None):
    cv.drawRect(skia.Rect.MakeXYWH(x + 14, y + 18, w_, h_), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w_, h_), P(col or PAPER))
    for i in range(10):
        Wd.glow(cv, x + w_ * rn(i, 5), y + h_ * rn(i, 6), 90 + 120 * rn(i, 7), h('C8B890'), 0.25)


def land(cv, pts, col=h('C8B48A')):
    cv.drawPath(poly(pts), P(col))
    cv.drawPath(poly(pts), P(INK, 4, a=0.6))


def dotted(cv, pts, k, col=INK, r=6, step=34):
    """Dots along a polyline, drawn up to fraction k of its length."""
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(math.dist(a, b) for a, b in segs)
    n = int(tot / step)
    for j in range(int(n * k)):
        d = j * step
        for a, b in segs:
            L = math.dist(a, b)
            if d <= L:
                u = d / L
                cv.drawCircle(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, r, P(col))
                break
            d -= L


# ---------------------------------------------------------------- inserts
def route_card(cv, c):
    """A drawn diagram, not a map: his route before the sinking. From America across to England, then south to the
    Canary Islands, then a dashed arrow aimed west at Antigua, and a red cross a week out where it ends."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2A3A')), (1, h('0E161E'))])
    cv.save()
    push(cv, c, 0.1, 0.4)
    paper(cv, 150, 60, 1620, 760, h('DCE6E4'))
    land(cv, [(150, 60), (520, 60), (560, 200), (470, 330), (400, 470), (300, 560), (150, 600)])            # the American side
    land(cv, [(1620, 60), (1770, 60), (1770, 560), (1660, 520), (1600, 420), (1640, 300), (1612, 200)])    # the European side
    land(cv, [(1480, 92), (1530, 70), (1566, 118), (1548, 196), (1494, 186)], h('B8A47A'))                 # England, a rough shape
    for x, y in ((1300, 560), (1340, 545), (1375, 565)):                                                   # the Canaries, dots
        cv.drawCircle(x, y, 13, P(h('B8A47A')))
    cv.drawPath(poly([(330, 680), (350, 672), (360, 690), (340, 698)]), P(h('B8A47A')))                     # Antigua, a speck
    k = ease(c.k / 0.75)
    dotted(cv, [(480, 300), (1000, 150), (1480, 150)], min(1, k * 2.2))
    dotted(cv, [(1500, 205), (1560, 330), (1350, 535)], min(1, max(0, k * 2.2 - 1.0)))
    if k > 0.75:
        u = ease((k - 0.75) / 0.25)
        x1 = lerp(1320, 380, u)
        for j in range(int(abs(1320 - x1) / 40)):
            x = 1320 - 40 * j
            cv.drawLine(x, 560 + (x - 1320) * -0.12, x - 22, 560 + (x - 22 - 1320) * -0.12, P(ORANGE, 8))
    plain(cv, 'AMERICA', 330, 250, 40, INK, 900)
    plain(cv, 'ENGLAND', 1380, 110, 38, INK, 900)
    plain(cv, 'CANARY ISLANDS', 1420, 625, 36, INK, 900)
    plain(cv, 'ANTIGUA', 345, 750, 36, INK, 900)
    if c.k > 0.8:
        x, y = 1050, 594
        cv.drawLine(x - 22, y - 22, x + 22, y + 22, P(h('D8322A'), 10))
        cv.drawLine(x - 22, y + 22, x + 22, y - 22, P(h('D8322A'), 10))
        plain(cv, 'A WEEK OUT', x, y - 40, 34, h('B02A1E'), 900)
    plain(cv, 'DIAGRAM, NOT TO SCALE', 1500, 790, 28, h('3A4A5A'), 700)
    cv.restore()


def drift_card(cv, c):
    """His log, drawn: a ruled page with a dotted line of daily positions creeping west, one dot at a time, and the three
    pencils that measured them lying on the page. A drawing of the idea, not a copy of his chart."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A2420')), (1, h('120F0C'))])
    cv.save()
    push(cv, c, 0.08, 0.3)
    cv.translate(960, 440)
    cv.rotate(-2)
    paper(cv, -760, -390, 1520, 760)
    for i in range(14):
        cv.drawLine(-740, -330 + 52 * i, 740, -330 + 52 * i, P(h('9AB8D0'), 2, a=0.6))
    cv.drawLine(-640, -390, -640, 370, P(h('D88A8A'), 3, a=0.7))
    plain(cv, 'WEST', -540, -300, 44, INK, 900)
    cv.drawLine(-450, -262, -600, -262, P(INK, 6))
    cv.drawPath(poly([(-600, -280), (-640, -262), (-600, -244)]), P(INK))
    k = ease(c.k / 0.85)
    n = int(6 + 34 * k)
    for j in range(n):
        x = 600 - 30 * j
        y = 60 + 70 * math.sin(j * 0.3) + 18 * rn(j, 3)
        cv.drawCircle(x, y, 9, P(INK))
        if j % 7 == 0:
            cv.drawLine(x, y + 16, x, y + 40, P(INK, 3))
    cv.drawLine(600 - 22, 60 - 22, 600 + 22, 60 + 22, P(h('D8322A'), 8))
    cv.drawLine(600 - 22, 60 + 22, 600 + 22, 60 - 22, P(h('D8322A'), 8))
    cx, cy = 400, -170                                                    # the three pencils, lashed into a triangle
    pts = [(cx + 130 * math.cos(a), cy + 130 * math.sin(a)) for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)]
    for i in range(3):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % 3]
        cv.drawLine(x0 - 0.12 * (x1 - x0), y0 - 0.12 * (y1 - y0), x1 + 0.12 * (x1 - x0), y1 + 0.12 * (y1 - y0), P(h('F2C030'), 16))
    for x, y in pts:
        cv.drawCircle(x, y, 12, P(h('E8E2D0')))
    plain(cv, 'HIS DRIFT, DRAWN, NOT TO SCALE', 0, 330, 34, h('3A3430'), 700)
    cv.restore()


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('9CB2D0')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def board(cv, c):
    """Rook's board for this case: cork, the photograph of the man in the raft, a red string from a pin marked CANARIES to
    a pin marked MARIE-GALANTE, and the case in three lines."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('6A4A2E')), (1, h('3A2818'))])
    for i in range(260):
        cv.drawCircle(W * rn(i, 1), H * rn(i, 2), 3 + 4 * rn(i, 3), P(h('8A6438'), a=0.35))
    cv.save()
    push(cv, c, 0.07, 0.4)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(560, 420)
    cv.scale(s, s)
    cv.rotate(-2.5)
    cv.drawRect(skia.Rect.MakeXYWH(-360 + 12, -260 + 16, 720, 520), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-360, -260, 720, 520), P(PAPER))
    photo(cv, 'thumb', 0, -10, 660, 440, (0.65, 0.4))
    cv.restore()
    pins = [(1000, 150, 'CANARIES'), (1000, 700, 'MARIE-GALANTE')]
    u = ease((c.lt - 0.1) / 0.5)
    cv.drawLine(pins[0][0], pins[0][1], lerp(pins[0][0], pins[1][0] + 30, u), lerp(pins[0][1], pins[1][1], u), P(h('C8322A'), 6))
    for x, y, s_ in pins:
        cv.drawCircle(x, y, 20, P(ORANGE))
        cv.drawCircle(x, y, 20, P(INK, 5))
        cv.drawRect(skia.Rect.MakeXYWH(x + 34, y - 30, 330, 56), P(PAPER))
        plain(cv, s_, x + 199, y + 12, 34, INK, 900)
    if c.lt > 0.25:
        fit(cv, '76 DAYS', 1440, 300, 110, 620, 0xFFFFFFFF)
    if c.lt > 0.6:
        fit(cv, '1,800 NAUTICAL MILES', 1440, 440, 70, 620, AMBER)
    if c.lt > 1.0:
        fit(cv, 'ONE FORK', 1440, 560, 70, 620, 0xFFFFFFFF)
    cv.restore()


SHOTS = {f.__name__: f for f in (route_card, drift_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0x99C8DCF0, 81, size=(2, 6), drift=(-220, 90), wobble=30, twinkle=False)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 46, 0x77D8F4FF, 83, size=(2, 6), drift=(10, -40), wobble=30, twinkle=True)


def glare(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x55FFF8E0, 85, size=(3, 8), drift=(16, -12), wobble=20, twinkle=True)


def stars(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x88FFFFFF, 87, size=(2, 4), drift=(-6, 2), wobble=4, twinkle=True)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x55FFE8C8, 99, size=(2, 5), drift=(12, -16), wobble=16, twinkle=True)


def rain(cv, c):
    for i in range(70):
        x = (W * rn(i, 11) + c.t * 260) % (W + 200) - 100
        y = (c.t * (1500 + 500 * rn(i, 12)) + H * rn(i, 13)) % (H + 200) - 100
        cv.drawLine(x, y, x - 18, y + 70, P(h('D8E4F0'), 3, a=0.35))


def closed(cv, c):
    glare(cv, c)
    if c.lt > 1.0:
        k = min(1, (c.lt - 1.0) / 0.15)
        cv.save()
        cv.translate(1440, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 017', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(cabin_flood=spray, boat_sink=spray, raft_jump=spray, raft_alone=spray, rook_raft=spray, still_close=glare, rook_still=glare,
            under_fish=motes, fish_catch=motes, spear_hole=motes, fish_hull=motes, patch_fail=glare, fork_fix=glare, thin_man=glare,
            night_lights=stars, rook_lights=stars, signoff=closed,
            night_alone=stars, rook_deck=spray, shed_build=dust, deck_swamped=spray, rook_hatch=motes, dive_cabin=motes, kit_spread=glare,
            still_open=glare, rain_catch=rain, reef_under=motes, shark_under=motes, flare_night=stars, pump_night=stars, fork_find=glare,
            pencil_sextant=stars, sun_beat=glare, desk_book=dust, film_tank=dust)


def THUMB(cv, c):
    """1280x720: the 3D still (him in the raft, thin and bearded, squinting into the sun, Rook on the canopy behind) and
    the hook on the left, over open sea and sky."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('1A6A8E'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(700, 0), (0, 0)], [0x00000000, 0xB0000000])))
    fit(cv, 'ALONE', 290, 300, 160, 520, 0xFFFFFFFF)
    fit(cv, '6-FOOT RAFT', 290, 440, 110, 520, AMBER)
