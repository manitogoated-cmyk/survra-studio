"""Case 025, the full case file (16:9) - Alan Magee, the ball turret gunner who fell about four miles without a usable
parachute on 3 January 1943 and went through the glass roof of the Saint-Nazaire railway station. The story is filmed in
3D (world3d.py). This file holds the flat inserts on a 1920x1080 canvas (Rook's chalk map of the raid, his scale of the
two heights the sources give, his card of the crew, and his case board), the 2D overlays drawn on top of 3D shots, and the
thumbnail. Every card is a drawing made for this film on Rook's sheet of riveted iron: the map is a sketch, not a chart,
and none of it reproduces a real photograph, document or emblem. Captions run in a band around 86% of the height and the
label sits top right, so the cards keep both clear."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1920, 1080
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER, CHALK, GLASS = h('FF7A1A'), h('FFB000'), h('EFE6CC'), h('F2F0E6'), h('BFE4F0')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def plain(cv, s, x, y, size, color, weight=900, maxw=None, centre=True):
    if not s:
        return 0
    f = font(size, weight)
    w = f.measureText(s)
    if maxw and w > maxw:
        f = font(size * maxw / w, weight)
        w = maxw
    cv.drawTextBlob(skia.TextBlob(s, f), x - (w / 2 if centre else 0), y, P(color))
    return w


def push(cv, c, amount=0.07, sway=0.3):
    z = 1.0 + amount * ease(c.k)
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.rotate(sway * math.sin(c.t * 0.7))
    cv.translate(-W / 2, -H / 2)


def iron(cv):
    """Rook's sheet of riveted iron: the ground of every card in this case."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A3E44')), (0.55, h('2A2E34')), (1, h('16181C'))])
    for i in range(40):
        cv.drawCircle(W * rn(i, 1), H * rn(i, 2), 60 + 160 * rn(i, 3), P(h('444A52'), a=0.12))
    for y in (46, 1034):
        cv.drawRect(skia.Rect.MakeXYWH(-40, y - 14, W + 80, 28), P(h('24282C')))
        for x in range(60, W, 150):
            cv.drawCircle(x, y, 10, P(h('5A6068')))
            cv.drawCircle(x - 3, y - 3, 4, P(h('8A9098')))


def chalk(cv, pts, color=None, width=7, close=False, a=1.0):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if close:
        path.close()
    cv.drawPath(path, P(color or CHALK, width, a=a))


def motes(cv, c, n=30, seed=91):
    Wd.particles(cv, W, H, c.t, n, 0x55F4ECDC, seed, size=(2, 5), drift=(14, 22), wobble=22, twinkle=True)


# ---------------------------------------------------------------- the raid, as a chalk sketch
ENGLAND = [(520, 96), (640, 110), (760, 96), (880, 140), (1010, 170), (1090, 250), (1050, 330), (1100, 392), (980, 420), (860, 404), (760, 432),
           (650, 420), (540, 452), (430, 440), (330, 470), (300, 440), (400, 396), (480, 330), (560, 300), (500, 240), (540, 170)]
FRANCE = [(1700, 500), (1500, 540), (1380, 520), (1300, 560), (1180, 548), (1120, 590), (1040, 560), (1000, 610), (900, 596), (780, 610), (660, 590),
          (560, 618), (640, 660), (560, 700), (680, 716), (790, 760), (900, 800), (940, 850), (1010, 880), (1060, 960), (1100, 1040), (1700, 1040)]
START, TARGET = (880, 250), (962, 868)


def map(cv, c):
    """Chalk on iron: the south of England, the Channel, Brittany. A dotted line leaves England, runs out round the
    peninsula over the sea and comes in to a ringed harbour. A sketch, not a chart."""
    iron(cv)
    cv.save()
    push(cv, c, 0.08, 0.25)
    cv.drawPath(_poly(ENGLAND), P(h('4A5A4A'), a=0.55))
    cv.drawPath(_poly(FRANCE), P(h('4A5A4A'), a=0.55))
    chalk(cv, ENGLAND, close=True)
    chalk(cv, FRANCE)
    plain(cv, 'ENGLAND', 760, 300, 60, CHALK, 900)
    plain(cv, 'FRANCE', 1420, 760, 60, CHALK, 900)
    route = [START, (700, 380), (470, 520), (400, 660), (520, 800), (760, 880), TARGET]
    n = 46
    shown = int(n * ease(c.lt / 1.9))
    for i in range(shown):
        u = i / (n - 1)
        x, y = _along(route, u)
        cv.drawCircle(x, y, 7, P(AMBER))
    cv.drawCircle(START[0], START[1], 13, P(CHALK))
    if c.lt > 1.7:
        g = ease((c.lt - 1.7) / 0.25)
        cv.drawCircle(TARGET[0], TARGET[1], 12, P(ORANGE))
        cv.drawCircle(TARGET[0], TARGET[1], 30 + 26 * (1 - g), P(ORANGE, 8))
        fit(cv, 'SAINT-NAZAIRE', 1330, 900, 76, 620, AMBER)
    cv.restore()
    motes(cv, c)


def _poly(pts):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    path.close()
    return path


def _along(pts, u):
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    d = u * sum(seg)
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if d <= L:
            k = d / L
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        d -= L
    return pts[-1]


# ---------------------------------------------------------------- how far: the two figures the sources give
def heights(cv, c):
    """A tall chalk rule on iron with two marks: the bomb group's report (about 20,000 feet) and the later tellings
    (22,000). A small chalk figure drops down the rule; one line under it all."""
    iron(cv)
    cv.save()
    push(cv, c, 0.07, 0.2)
    x0, top, bot = 430, 130, 800
    cv.drawLine(x0, top, x0, bot, P(CHALK, 9))
    for i in range(12):
        y = top + (bot - top) * i / 11
        cv.drawLine(x0 - (36 if i % 2 == 0 else 20), y, x0, y, P(CHALK, 6))
    cv.drawLine(x0 - 120, bot, x0 + 240, bot, P(CHALK, 9))
    plain(cv, 'GROUND', x0 + 70, bot + 56, 40, CHALK, 900)
    y22, y20 = top + 20, top + 20 + (bot - top - 20) * 2 / 22
    if c.lt > 0.25:
        g = ease((c.lt - 0.25) / 0.2)
        cv.drawLine(x0, y20, x0 + 150 * g, y20, P(AMBER, 8))
        plain(cv, 'THE GROUP\'S REPORT', x0 + 190, y20 + 64, 44, CHALK, 900, centre=False)
        fit(cv, 'ABOUT 20,000 FEET', x0 + 190 + 330, y20 + 150, 82, 660, AMBER)
    if c.lt > 1.0:
        g = ease((c.lt - 1.0) / 0.2)
        cv.drawLine(x0, y22, x0 + 150 * g, y22, P(GLASS, 8))
        plain(cv, 'LATER TELLINGS', x0 + 880, y22 + 20, 44, CHALK, 900, centre=False)
        fit(cv, '22,000 FEET', x0 + 880 + 260, y22 + 104, 82, 520, GLASS)
    if c.lt > 1.9:
        g = ease((c.lt - 1.9) / 0.25)
        cv.save()
        cv.translate(1240, 640)
        cv.scale(1.25 - 0.25 * g, 1.25 - 0.25 * g)
        Wd.text_card(cv, 'ABOUT 4 MILES', 0, 0, 132, 0xFFFFFFFF, 0xFF000000)
        cv.restore()
    # the falling figure: a chalk stick man, turning as he goes down the rule
    u = (c.lt * 0.3) % 1
    fy = top + 30 + (bot - top - 90) * u
    cv.save()
    cv.translate(x0 - 150, fy)
    cv.rotate(c.t * 70)
    cv.drawCircle(0, -22, 11, P(CHALK, 6))
    cv.drawLine(0, -11, 0, 20, P(CHALK, 6))
    cv.drawLine(-20, -4, 20, 4, P(CHALK, 6))
    cv.drawLine(0, 20, -14, 42, P(CHALK, 6))
    cv.drawLine(0, 20, 16, 40, P(CHALK, 6))
    cv.restore()
    for i in range(5):
        cv.drawLine(x0 - 150 + 18 * (i - 2), fy - 70 - 30 * rn(i, 5), x0 - 150 + 18 * (i - 2), fy - 120 - 40 * rn(i, 6), P(CHALK, 4, a=0.4))
    cv.restore()
    motes(cv, c)


# ---------------------------------------------------------------- the crew
def crewcard(cv, c):
    """Ten plain chalk figures in a row for the ten men aboard. Three are ringed in orange; a chalk line is drawn under
    the other seven. No names, no faces."""
    iron(cv)
    cv.save()
    push(cv, c, 0.16, 0.5)
    cv.translate(60 - 120 * c.k, 0)                    # a slow drift along the row, so the card never stands still
    fit(cv, 'TEN MEN ABOARD', 960, 190, 92, 1300, 0xFFFFFFFF)
    xs = [330 + 140 * i for i in range(10)]
    lived = (2, 5, 9)
    for i, x in enumerate(xs):
        if c.lt < 0.12 + 0.07 * i:
            continue
        y = 470
        col = CHALK
        cv.drawCircle(x, y - 84, 26, P(col, 8))
        cv.drawLine(x, y - 58, x, y + 40, P(col, 8))
        cv.drawLine(x - 40, y - 20, x + 40, y - 20, P(col, 8))
        cv.drawLine(x, y + 40, x - 28, y + 112, P(col, 8))
        cv.drawLine(x, y + 40, x + 28, y + 112, P(col, 8))
    if c.lt > 1.1:
        g = ease((c.lt - 1.1) / 0.3)
        for i in lived:
            cv.drawArc(skia.Rect.MakeXYWH(xs[i] - 66, 340, 132, 270), -90, 360 * g, False, P(ORANGE, 9))
        fit(cv, 'THREE LIVED', 960, 730, 84, 900, AMBER)
    if c.lt > 2.0:
        g = ease((c.lt - 2.0) / 0.3)
        for i in range(10):
            if i not in lived:
                cv.drawLine(xs[i] - 48, 618, xs[i] - 48 + 96 * g, 618, P(CHALK, 7))
        fit(cv, 'SEVEN DID NOT COME HOME', 960, 838, 70, 1300, 0xFFFFFFFF)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 70, 0x66F4ECDC, 95, size=(2, 6), drift=(40, 30), wobble=30, twinkle=True)


# ---------------------------------------------------------------- Rook's board
def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
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
    """Rook's board for this case: riveted iron, a cracked pane of glass bolted over a photograph of the hole in the
    station roof, and the case in three lines."""
    iron(cv)
    cv.save()
    push(cv, c, 0.07, 0.3)
    k = min(1, c.lt / 0.16)
    s = 0.78 + 0.22 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(560, 450)
    cv.scale(s, s)
    cv.rotate(-2.0)
    cv.drawRect(skia.Rect.MakeXYWH(-400 + 12, -300 + 16, 800, 600), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-400, -300, 800, 600), P(PAPER))
    photo(cv, 'hole', 0, -10, 740, 520, (0.5, 0.5))
    cv.drawRect(skia.Rect.MakeXYWH(-370, -270, 740, 520), P(0x22BFE4F0))
    for i in range(7):
        a = 0.4 + i * 0.85
        L = 130 + 190 * rn(i, 3)
        cv.drawLine(150, -120, 150 + L * math.cos(a), -120 + L * math.sin(a), P(0xCCF4FAFF, 4))
    cv.restore()
    for x in (230, 890):
        cv.drawCircle(x, 170, 20, P(ORANGE))
        cv.drawCircle(x, 170, 20, P(INK, 5))
    if c.lt > 0.2:
        fit(cv, 'NO PARACHUTE', 1380, 310, 100, 760, AMBER)
    if c.lt > 0.75:
        fit(cv, 'FOUR MILES', 1380, 460, 100, 760, 0xFFFFFFFF)
    if c.lt > 1.3:
        fit(cv, 'ONE GLASS ROOF', 1380, 610, 100, 760, GLASS)
    cv.restore()
    motes(cv, c, 24)


SHOTS = {f.__name__: f for f in (map, heights, crewcard, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def grit(cv, c):
    """Flak grit and sparks drifting past the lens."""
    Wd.particles(cv, W, H, c.t, 30, 0x99FFB040, 93, size=(2, 6), drift=(260, 60), wobble=40, twinkle=True)
    Wd.particles(cv, W, H, c.t, 22, 0x66303034, 95, size=(4, 9), drift=(200, 90), wobble=50)


def rush(cv, c):
    """Falling: streaks of air going up past the lens."""
    for i in range(34):
        x = W * rn(i, 11)
        y = H - ((c.t * (1300 + 800 * rn(i, 12)) + H * rn(i, 13)) % (H + 300))
        cv.drawLine(x, y, x + 6 * math.sin(i), y + 90 + 110 * rn(i, 14), P(h('F2F8FF'), 4, a=0.25))


def glints(cv, c):
    Wd.particles(cv, W, H, c.t, 44, 0xCCE8F8FF, 97, size=(2, 6), drift=(10, 420), wobble=20, twinkle=True)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 34, 0x55FFF0D8, 99, size=(2, 5), drift=(14, -16), wobble=16, twinkle=True)


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 70, 0xCCF4F8FF, 101, size=(3, 8), drift=(30, 150), wobble=30)


def haze(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x44FFF4DC, 61, size=(2, 5), drift=(30, -10), wobble=30, twinkle=True)


def seeds(cv, c):
    """Late sun on a grass field: seeds and insects drifting across the light."""
    Wd.particles(cv, W, H, c.t, 40, 0x77FFE8B0, 65, size=(2, 5), drift=(60, -14), wobble=40, twinkle=True)


def closed(cv, c):
    dust(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(1400, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 025', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(turret_close=grit, chute_rags=dust, bomber_down=grit, roof_rush=rush, rook_ridge=dust, formation=haze, flak_hit=grit,
            turret_climb=dust, chute_find=dust, rook_silk=dust, gasp_dim=dust, thrown_clear=grit, fall_wide=rush, rook_dive=rush,
            town_below=rush, rook_look=dust, smash=glints, shards=glints, hole_up=dust, found=dust, rook_shard=dust, stretcher=dust,
            doctor=dust, rook_bed=dust, camp=snow, memorial=dust, wreath=dust, signoff=closed,
            field_dawn=haze, turret_under=haze, rook_measure=haze, turret_side=grit, pack_hook=dust, nose_fly=haze, pens=grit, wing_hit=grit,
            spin_down=grit, fuse_spin=grit, fall_close=rush, station_out=haze, girders=dust, bed_leg=dust, arm_close=dust, doc_talk=dust,
            arm_wrap=dust, bed_sit=dust, camp_three=snow, gate_open=seeds, medals=dust, hangar_walk=seeds, cub_fly=seeds, mem_visit=dust,
            rook_verdict=haze)


def THUMB(cv, c):
    """1280x720: the 3D still (the gunner falling on the right, the glass roof of the station far below on the left) and
    the hook on the left, over a darkened sky."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('3E76BC'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(640, 0), (0, 0)], [0x00000000, 0xB0000000])))
    fit(cv, 'NO', 300, 210, 170, 520, 0xFFFFFFFF)
    fit(cv, 'PARACHUTE', 300, 370, 150, 540, 0xFFFFFFFF)
    fit(cv, '4 MILES', 300, 540, 170, 520, AMBER)
