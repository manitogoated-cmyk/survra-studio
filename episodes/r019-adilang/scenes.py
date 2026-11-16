"""Case 019 - Aldi Novel Adilang, adrift for 49 days in 2018. The story is filmed in 3D (world3d.py). This file
holds the flat inserts (a drawn chart of how far out the hut was moored, the count of days, the ships that
passed, Rook's case board on weathered planks) and the 2D overlays drawn on top of 3D shots (rain and spray,
glitter on the water, embers, the day count, the sign-off). Every card is a drawing made for this film; none
reproduces a real chart, photograph, document or logo. The chart is a diagram: the coast is an invented
outline, not the real coastline, and nothing on it is to scale."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('EFE6CC'), h('D8261E'), h('3EC46A')
SEA, SEAD, LAND = h('1C6E94'), h('0E3A5A'), h('6E8A4E')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 73.31 + j * 39.77) * 15731.743) % 1


def font(size):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def hut_mark(cv, x, y, s, lamp=True):
    """The little hut on its raft, as a mark on a card."""
    cv.drawRect(skia.Rect.MakeXYWH(x - 70 * s, y, 140 * s, 14 * s), P(h('8E6B43')))
    for dx in (-52, 0, 52):
        cv.drawOval(skia.Rect.MakeXYWH(x + (dx - 16) * s, y + 10 * s, 32 * s, 20 * s), P(h('2B6CA8')))
    cv.drawRect(skia.Rect.MakeXYWH(x - 52 * s, y - 50 * s, 62 * s, 50 * s), P(h('A48648')))
    cv.drawRect(skia.Rect.MakeXYWH(x - 34 * s, y - 34 * s, 24 * s, 34 * s), P(h('3A2A1A')))
    cv.drawPath(poly([(x - 66 * s, y - 48 * s), (x - 21 * s, y - 92 * s), (x + 24 * s, y - 48 * s)]), P(h('C9AB62')))
    cv.drawLine(x + 52 * s, y, x + 52 * s, y - 84 * s, P(h('B89E5E'), 5 * s))
    if lamp:
        cv.drawCircle(x + 52 * s, y - 88 * s, 10 * s, P(h('FFE9A8')))


def ship_mark(cv, x, y, s, col):
    cv.drawPath(poly([(x - 150 * s, y - 34 * s), (x + 170 * s, y - 34 * s), (x + 138 * s, y), (x - 138 * s, y)]), P(col))
    cv.drawRect(skia.Rect.MakeXYWH(x - 136 * s, y - 82 * s, 46 * s, 48 * s), P(col))
    cv.drawRect(skia.Rect.MakeXYWH(x - 122 * s, y - 106 * s, 16 * s, 24 * s), P(col))
    for j in range(4):
        cv.drawRect(skia.Rect.MakeXYWH(x + (-70 + 52 * j) * s, y - 46 * s, 40 * s, 12 * s), P(col))


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('3A5A7A')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def stamp(cv, s, x, y, ang, k, size=150, col=RED):
    f = font(size)
    tw = f.measureText(s)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    sc = 2.3 - 1.3 * k
    cv.scale(sc, sc)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-tw / 2 - 30, -size * 0.62, tw + 60, size * 1.2), 18, 18, P(col, 14, a=k))
    cv.drawString(s, -tw / 2, size * 0.36, f, P(col, a=k))
    cv.restore()


# ---------------------------------------------------------------- inserts
COAST = [(-20, 300), (150, 330), (250, 470), (210, 640), (300, 800), (240, 980), (300, 1130), (200, 1330), (250, 1540), (120, 1700), (-20, 1720)]


def map_card(cv, c):
    """'Land is 125 kilometres away.' A drawn chart: a coast, a dotted line out to the hut, then the wind takes the hut off the sheet."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A5A80')), (0.6, h('14466A')), (1, h('0C2C48'))])
    for i in range(9):                                             # chart grid
        cv.drawLine(0, 200 + 190 * i, W, 200 + 190 * i, P(0xFFFFFFFF, 2, a=0.08))
        cv.drawLine(130 * i, 0, 130 * i, H, P(0xFFFFFFFF, 2, a=0.08))
    cv.drawPath(poly(COAST), P(LAND))
    cv.drawPath(poly(COAST), P(h('D8D0A8'), 8))
    for i in range(7):
        cv.drawCircle(60 + 120 * rn(i, 1), 420 + 1150 * rn(i, 2), 14 + 16 * rn(i, 3), P(h('4E6A3A'), a=0.6))
    k = ease(c.k / 0.5)
    x0, y0, x1, y1 = 290, 900, 800, 900
    xe = lerp(x0, x1, k)
    n = int((xe - x0) / 34)
    for i in range(n):
        cv.drawCircle(x0 + 34 * i + 12, y0, 7, P(AMBER))
    go = ease((c.k - 0.66) / 0.34)
    hx, hy = lerp(xe, 1240, go), y0 - 260 * go
    cv.save()
    cv.translate(hx, hy)
    cv.rotate(-14 * go + 3 * math.sin(c.t * 5))
    hut_mark(cv, 0, 0, 1.25)
    cv.restore()
    if go > 0.02:                                                  # wind streaks
        for i in range(5):
            yy = 700 + 70 * i
            xx = 420 + 500 * ((c.t * 1.6 + i * 0.23) % 1)
            cv.drawLine(xx, yy, xx + 150, yy - 40, P(0xFFFFFFFF, 7, a=0.5))
    fit(cv, f'{int(round(125 * k))} KM', 580, 560, 200, 760, AMBER)
    fit(cv, 'FROM LAND', 580, 690, 76, 700, 0xFFFFFFFF)
    fit(cv, 'DIAGRAM, NOT TO SCALE', 540, 1660, 44, 800, 0x99FFFFFF, None)


def days_card(cv, c):
    """The days: a sun crosses the sky above the little hut, again and again, and the count climbs."""
    ph = (c.k * 6.0) % 1
    lightk = math.sin(ph * math.pi)
    top = Wd.mix(h('0E1A40'), h('6CB8E8'), lightk)
    low = Wd.mix(h('2A2A5A'), h('F2B078'), 1 - abs(lightk - 0.5) * 2 if lightk < 0.9 else 0.2)
    Wd.vgrad(cv, 0, 0, W, 1000, [(0, top), (1, low)])
    sx, sy = lerp(-80, W + 80, ph), 880 - 620 * math.sin(ph * math.pi)
    Wd.glow(cv, sx, sy, 260, h('FFE2A0'), 0.6)
    cv.drawCircle(sx, sy, 62, P(h('FFE9B0')))
    Wd.vgrad(cv, 0, 1000, W, H, [(0, Wd.mix(h('0E2A48'), h('1C6E94'), lightk)), (1, h('081828'))])
    for i in range(12):
        yy = 1030 + 70 * i
        xx = (rn(i, 4) * W + c.t * (30 + 20 * rn(i, 5))) % W
        cv.drawLine(xx, yy, xx + 90 + 80 * rn(i, 6), yy, P(0xFFFFFFFF, 5, a=0.18))
    cv.save()
    cv.translate(540, 1010 + 8 * math.sin(c.t * 2.2))
    cv.rotate(3 * math.sin(c.t * 1.7))
    hut_mark(cv, 0, 0, 1.5, lamp=False)
    cv.restore()
    n = 1 + int(47 * ease(c.k))
    fit(cv, f'DAY {n}', 540, 470, 210, 900, AMBER)
    fit(cv, 'ADRIFT', 540, 600, 84, 700, 0xFFFFFFFF)
    fit(cv, '14 JULY TO 31 AUGUST 2018', 540, 1660, 56, 960, 0xCCFFFFFF)


def ten_card(cv, c):
    """'So do more than ten others.' Ship after ship crosses and is struck through; the count climbs past ten."""
    Wd.vgrad(cv, 0, 0, W, 1000, [(0, h('7EBCE6')), (1, h('CFE6F2'))])
    Wd.vgrad(cv, 0, 1000, W, H, [(0, h('1C6E94')), (1, h('0A2E48'))])
    n = c.k * 12.5
    cnt = min(10, int(n))
    for i in range(11):
        k = n - i
        if k <= 0:
            continue
        row, col = i // 4, i % 4
        x = 150 + 260 * col + (130 if row == 2 else 0)
        y = 800 + 135 * row
        if k < 1:                                                  # this one is still crossing
            x = lerp(-200, x, ease(k))
        ship_mark(cv, x, y, 0.62, h('1F2A3E'))
        if k >= 1:
            cv.drawLine(x - 100, y - 70, x + 100, y + 6, P(RED, 12))
    cv.save()
    cv.translate(540, 1060 + 6 * math.sin(c.t * 2.4))
    hut_mark(cv, 0, 0, 0.9, lamp=False)
    cv.restore()
    if cnt >= 1:
        fit(cv, f'{cnt}+ SHIPS' if n >= 10.6 else f'{cnt}', 540, 480, 230 if n < 10.6 else 190, 960, AMBER)
    if n >= 11.2:
        fit(cv, 'NONE STOPPED', 540, 1660, 110, 940, 0xFFFFFFFF)


def board(cv, c):
    """Rook's board for this case: weathered planks lashed with rope, a photograph of the hut, and his question."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('24405A')), (0.5, h('1A2C42')), (1, h('0C141E'))])
    for i in range(7):                                             # planks
        x = 50 + 140 * i
        col = (h('8E6B43'), h('7A5A38'), h('9A7850'))[i % 3]
        cv.drawRect(skia.Rect.MakeXYWH(x, 150, 136, 1620), P(col))
        for j in range(5):
            yy = 200 + 1500 * rn(i, j)
            cv.drawLine(x + 20 + 90 * rn(i, j + 7), yy, x + 30 + 90 * rn(i, j + 7), yy + 120 + 160 * rn(j, i), P(h('5E4428'), 4, a=0.5))
    for yy in (240, 1700):                                         # rope lashings
        cv.drawLine(40, yy, 1040, yy, P(h('3A2A1A'), 30))
        cv.drawLine(40, yy, 1040, yy, P(h('D8C8A0'), 20))
        for i in range(22):
            cv.drawLine(60 + 45 * i, yy - 10, 80 + 45 * i, yy + 10, P(h('A89870'), 4))
    Wd.glow(cv, 540, 820, 900, h('FFC890'), 0.14)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 700)
    cv.scale(s, s)
    cv.rotate(-2.5)
    cv.drawRect(skia.Rect.MakeXYWH(-390 + 12, -400 + 16, 780, 800), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-390, -400, 780, 800), P(PAPER))
    photo(cv, 'hut', 0, -30, 710, 660, (0.5, 0.45))
    cv.restore()
    for x in (210, 870):
        cv.drawCircle(x, 330, 24, P(ORANGE))
        cv.drawCircle(x, 330, 24, P(INK, 5))
    if c.lt > 0.25:
        fit(cv, 'WOULD YOU HAVE', 540, 1540, 112, 900, 0xFFFFFFFF)
    if c.lt > 0.45:
        fit(cv, 'KEPT WAVING?', 540, 1660, 124, 900, AMBER)
    if c.lt > 0.7:
        stamp(cv, 'TRUE', 770, 380, -10, min(1, (c.lt - 0.7) / 0.12), 140, GREEN)


SHOTS = {f.__name__: f for f in (map_card, days_card, ten_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def storm(cv, c):
    Wd.rain(cv, W, H, c.t, 150, 0x77CFE6FF, 0.45, 2200, 5, 54)
    Wd.particles(cv, W, H, c.t, 30, 0x88EAF6FF, 71, size=(3, 8), drift=(520, 60), wobble=30)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 46, 0x99EAF6FF, 73, size=(3, 9), drift=(300, -120), wobble=40)


def glitter(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x88FFFFFF, 75, size=(2, 5), drift=(26, -14), wobble=20, twinkle=True)


def embers(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0xAAFFB060, 77, size=(2, 6), drift=(18, -150), wobble=40, twinkle=True)


def night_air(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x77DCE8FF, 79, size=(2, 4), drift=(10, -6), wobble=10, twinkle=True)


def big(cv, s, y, c, t0=0.3, size=190):
    if c.lt > t0:
        k = min(1, (c.lt - t0) / 0.15)
        cv.save()
        cv.translate(540, y)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        fit(cv, s, 0, 0, size, 900, AMBER)
        cv.restore()


def day_49(cv, c):
    glitter(cv, c)
    big(cv, 'DAY 49', 600, c, 0.15)


def days_49(cv, c):
    glitter(cv, c)
    big(cv, '49 DAYS', 560, c, 0.35)


def closed(cv, c):
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 019', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(snap_wide=storm, rope_close=storm, drift_off=storm, boy_face=storm, rook_roof=storm, no_engine=spray, dawn_empty=glitter, fishing=glitter,
            fence_break=glitter, cook=embers, sip=glitter, ship_appears=glitter, wave_cloth=glitter, sail_past=glitter, cry=night_air, day49=day_49,
            call=glitter, wait=glitter, turn=glitter, high_waves=spray, rope_throw=spray, jump=spray, haul=spray, alive=glitter, ship_away=days_49,
            rook_wrong=glitter, signoff=closed)
