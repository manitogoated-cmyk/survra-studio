"""Case 009 - Poon Lim. The story is filmed in 3D (world3d.py). This file holds the flat inserts (Rook's case
board on a sea chart, the knotted-rope day counter, the crew file, the drift sketch) and the 2D overlays drawn on
top of 3D shots (rain, the raft's size, the day stamp, the sign-off)."""
import math
import os

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER, RED = h('FF7A1A'), h('FFB000'), h('F1E6CC'), h('D8362A')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) pinned to the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('7EC0EE')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def chart(cv, t=0.0):
    """Rook's board for this case: an old sea chart, soundings and a compass rose."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C4A5E')), (1, h('0E2C3C'))])
    for i in range(1, 9):
        cv.drawLine(i * 135, 0, i * 135, H, P(0x2EBFE6F2, 2))
    for i in range(1, 15):
        cv.drawLine(0, i * 135, W, i * 135, P(0x2EBFE6F2, 2))
    R = Wd.Rand(9)
    f = skia.Font(skia.Typeface('Inter'), 26)
    for i in range(46):
        cv.drawString(str(int(R(12, 4800))), R(30, W - 90), R(60, H - 40), f, skia.Paint(Color=0x44BFE6F2, AntiAlias=True))
    cx, cy = 880, 1620
    for i in range(16):
        a = i * math.pi / 8
        r = 150 if i % 4 == 0 else (105 if i % 2 == 0 else 70)
        cv.drawLine(cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r, P(0x66F1E6CC, 5 if i % 4 == 0 else 3))
    cv.drawCircle(cx, cy, 112, P(0x55F1E6CC, 4))
    cv.drawRect(skia.Rect.MakeLTRB(18, 18, W - 18, H - 18), P(h('0A1C26'), 36))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x66000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, tape=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if tape:
        cv.drawRect(skia.Rect.MakeXYWH(-70, -h_ / 2 - 24, 140, 48), P(0xCCFFB000))
    cv.restore()


def stamp(cv, s, x, y, ang, k, size=150, col=RED, w_=None):
    """A rubber stamp that slams down (k 0..1)."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    tw = f.measureText(s)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    sc = 2.3 - 1.3 * k
    cv.scale(sc, sc)
    cv.drawRoundRect(skia.Rect.MakeLTRB(-tw / 2 - 44, -size * 0.72, tw / 2 + 44, size * 0.42), 18, 18, P(0xEE0E2C3C))
    cv.drawRoundRect(skia.Rect.MakeLTRB(-tw / 2 - 44, -size * 0.72, tw / 2 + 44, size * 0.42), 18, 18, P(col, 18))
    Wd.text_card(cv, s, 0, size * 0.18, size, col, None)
    cv.restore()


# ------------------------------------------------------------------ flat inserts
def tally_133(cv, c):
    """He counted days with knots in a rope (and later by the moon): the count runs up to 133."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C2233')), (1, h('05101A'))])
    n = int(round(133 * ease(c.k / 0.72)))
    for row in range(7):
        y = 330 + row * 62 if row < 3 else 980 + (row - 3) * 62
        cv.drawLine(70, y, W - 70, y + 10 * math.sin(row * 1.7), P(h('C9B48A'), 10))
        cv.drawLine(70, y + 4, W - 70, y + 4 + 10 * math.sin(row * 1.7), P(h('8E7A52'), 3))
        for i in range(19):
            idx = row * 19 + i
            if idx < n:
                x = 100 + i * 49
                yy = y + 10 * math.sin(row * 1.7) * (x - 70) / (W - 140)
                cv.drawCircle(x, yy, 15, P(h('E4D2A6')))
                cv.drawCircle(x, yy, 15, P(h('6E5C3A'), 4))
    pop = 1 + 0.25 * max(0.0, 1 - abs(c.k - 0.74) / 0.1)
    cv.save()
    cv.translate(540, 740)
    cv.scale(pop, pop)
    Wd.text_card(cv, str(n), 0, 70, 330, AMBER if n >= 133 else 0xFFFFFFFF, 0xFF000000)
    cv.restore()
    Wd.text_card(cv, 'DAYS', 540, 930, 110, 0xFFFFFFFF, 0xFF000000)


def board_no(cv, c):
    chart(cv)
    k = min(1, c.lt / 0.22)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(520, 700)
    cv.scale(s, s)
    card(cv, 0, 0, 800, 640, -3)
    cv.rotate(-3)
    photo(cv, 'raft', 0, 10, 730, 540, (0.5, 0.6))
    cv.restore()
    k2 = min(1, max(0, (c.lt - 0.3) / 0.14))
    if k2 > 0:
        cv.drawLine(300, 420, lerp(300, 250, k2), lerp(420, 1090, k2), P(RED, 8))
        card(cv, 270, 1130, 420, 190, 5, h('FFD866'), tape=False)
        cv.save()
        cv.translate(270, 1130)
        cv.rotate(5)
        Wd.text_card(cv, '133 DAYS', 0, 28, 78, INK, None)
        cv.restore()
    k3 = min(1, max(0, (c.lt - 0.5) / 0.14))
    if k3 > 0:
        cv.drawLine(760, 420, lerp(760, 800, k3), lerp(420, 1090, k3), P(RED, 8))
        card(cv, 800, 1140, 330, 190, -6, h('BFE0EC'), tape=False)
        cv.save()
        cv.translate(800, 1140)
        cv.rotate(-6)
        Wd.text_card(cv, 'ALONE', 0, 28, 78, INK, None)
        cv.restore()
    k4 = min(1, max(0, (c.k - 0.7) / 0.1))
    if c.k > 0.7:
        stamp(cv, 'NO CHANCE', 540, 720, -12, k4, 132)


def id_card(cv, c):
    """Crew file. The portrait is a drawn silhouette, not a photograph of him."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10283A')), (1, h('081620'))])
    k = ease(c.lt / 0.22)
    cv.save()
    cv.translate(540, 760 + 500 * (1 - k))
    cv.rotate(-2.5)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-448, -420, 920, 880), 22, 22, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-460, -440, 920, 880), 22, 22, P(h('E6D3A6')))
    cv.drawRect(skia.Rect.MakeXYWH(-460, -440, 920, 120), P(h('2A4658')))
    Wd.text_card(cv, 'CREW FILE', 0, -356, 76, PAPER, None)
    cv.drawRect(skia.Rect.MakeXYWH(-410, -280, 300, 360), P(h('B8C8CC')))
    cv.drawRect(skia.Rect.MakeXYWH(-410, -280, 300, 360), P(INK, 6))
    cv.drawCircle(-260, -150, 74, P(h('3A4A56')))
    cv.drawPath(poly([(-380, 80), (-360, -40), (-300, -72), (-220, -72), (-160, -40), (-140, 80)]), P(h('3A4A56')))
    for i, (lab, val) in enumerate((('NAME', 'POON LIM'), ('RATING', '2ND STEWARD'), ('BORN', 'HAINAN, CHINA'))):
        y = -230 + i * 122
        Wd.text_card(cv, lab, -70, y, 34, h('7A6A48'), None, center=False)
        on = c.lt > 0.3 + i * 0.18
        if on:
            Wd.text_card(cv, val, -70, y + 62, 60 if len(val) < 12 else 50, INK, None, center=False)
    cv.drawLine(-410, 150, 410, 150, P(h('7A6A48'), 4))
    Wd.text_card(cv, 'SHIP', -410, 212, 34, h('7A6A48'), None, center=False)
    if c.lt > 0.84:
        Wd.text_card(cv, 'SS BENLOMOND', -410, 300, 84, h('2A4658'), None, center=False)
        Wd.text_card(cv, 'BRITISH CARGO STEAMER', -410, 368, 40, h('7A6A48'), None, center=False)
    cv.restore()


LAND = [(-55, 6.2), (-52, 5), (-50.5, 1.5), (-48.5, -0.6), (-44.5, -2.6), (-40, -2.9), (-37.2, -4.7), (-35, -5.6), (-35, -9), (-38, -13),
        (-55, -13)]
AFR = [(-17.5, 13), (-16.5, 11), (-13, 8.5), (-9, 5), (-4, 5.2), (-4, 13)]


def map_drift(cv, c):
    """Sketch of the equatorial Atlantic. The two ends are from the record; the path between them is not known."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C5A72')), (1, h('0E3446'))])
    px = lambda lon, lat: (540 + (lon + 30) * 21.0, 760 - lat * 21.0)
    for lon in range(-55, 0, 10):
        cv.drawLine(px(lon, 0)[0], 360, px(lon, 0)[0], 1040, P(0x33BFE6F2, 2))
    cv.drawLine(0, 760, W, 760, P(0x66BFE6F2, 3))
    Wd.text_card(cv, 'EQUATOR', 930, 748, 26, 0x99BFE6F2, None)
    for pts, name, lx, ly in ((LAND, 'BRAZIL', -47, -7.5), (AFR, 'AFRICA', -10.5, 9.5)):
        path = poly([px(*p) for p in pts])
        cv.drawPath(path, P(h('D8C890')))
        cv.drawPath(path, P(h('5E4E2A'), 5))
        Wd.text_card(cv, name, px(lx, ly)[0], px(lx, ly)[1], 44, h('5E4E2A'), None)
    Wd.text_card(cv, 'ATLANTIC OCEAN', 600, 520, 40, 0x88DFF4FF, None)
    a, b = px(-38.75, 0.5), px(-47.3, -0.4)
    k = ease(c.k / 0.7)
    for i in range(22):
        u = i / 21
        if u > k:
            break
        x = lerp(a[0], b[0], u)
        y = lerp(a[1], b[1], u) + 26 * math.sin(u * 9.0) * (1 - u)
        cv.drawCircle(x, y, 7, P(0xFFFFFFFF))
    cv.drawLine(a[0] - 22, a[1] - 22, a[0] + 22, a[1] + 22, P(RED, 10))
    cv.drawLine(a[0] - 22, a[1] + 22, a[0] + 22, a[1] - 22, P(RED, 10))
    fit(cv, 'SUNK 23 NOV 1942', a[0] + 150, a[1] - 52, 40, 520, 0xFFFFFFFF)
    if k >= 1:
        cv.drawCircle(b[0], b[1], 20, P(AMBER))
        cv.drawCircle(b[0], b[1], 20 + 30 * ((c.t * 2) % 1), P(Wd.alpha(AMBER, 1 - (c.t * 2) % 1), 6))
        fit(cv, 'FOUND 5 APR 1943', b[0] + 150, b[1] + 86, 40, 520, AMBER)
    Wd.text_card(cv, '133 DAYS ADRIFT', 540, 300, 96, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'SKETCH: THE DRIFT PATH IS NOT KNOWN', 540, 1110, 32, 0xAAFFFFFF, None)


def board_true(cv, c):
    chart(cv)
    card(cv, 540, 720, 700, 800, 2)
    cv.save()
    cv.translate(540, 720)
    cv.rotate(2)
    photo(cv, 'poon', 0, 10, 630, 700, (0.5, 0.3))
    cv.restore()
    k = min(1, max(0, (c.lt - 0.3) / 0.12))
    if c.lt > 0.3:
        stamp(cv, 'TRUE', 560, 900, -14, k, 190)
    card(cv, 300, 1500, 400, 200, -5, h('FFD866'), tape=False)
    cv.save()
    cv.translate(300, 1500)
    cv.rotate(-5)
    Wd.text_card(cv, '133 DAYS', 0, 26, 76, INK, None)
    cv.restore()


SHOTS = {f.__name__: f for f in (tally_133, board_no, id_card, map_drift, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=130, c=0x77D8ECFF, slant=0.22, speed=2100, seed=5, length=58)


def squall(cv, c):
    Wd.rain(cv, W, H, c.t, density=210, c=0x88D8ECFF, slant=0.55, speed=2900, seed=8, length=84)


def size8(cv, c):
    k = ease((c.lt - 0.15) / 0.2)
    if k <= 0:
        return
    y = 400
    x0, x1 = 540 - 330 * k, 540 + 330 * k
    cv.drawLine(x0, y, x1, y, P(0xFF000000, 16))
    cv.drawLine(x0, y, x1, y, P(AMBER, 8))
    for x in (x0, x1):
        cv.drawLine(x, y - 34, x, y + 34, P(0xFF000000, 16))
        cv.drawLine(x, y - 34, x, y + 34, P(AMBER, 8))
    Wd.text_card(cv, '8 FT', 540, y - 50, 120, AMBER, 0xFF000000)


def day133(cv, c):
    k = ease(c.lt / 0.14)
    cv.save()
    cv.translate(540, 520)
    cv.rotate(-5)
    cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
    Wd.text_card(cv, 'DAY 133', 0, 0, 190, AMBER, 0xFF000000)
    cv.restore()


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 009  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(rain_catch=rain, storm_hide=squall, raft_top=size8, coast_dawn=day133, signoff=closed)
