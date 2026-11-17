"""Case 019, the full case file (16:9) - Aldi Novel Adilang, adrift for 49 days in 2018. The story is filmed in 3D
(world3d.py). This file holds the flat inserts on a 1920x1080 canvas (charts of where the hut was moored, where it
went and where the ship took him; his age and pay; the two earlier drifts; the count of days; the ships that
passed; Rook's case board), the 2D overlays drawn on top of 3D shots, and the thumbnail. Every card is a drawing made for this film; none
reproduces a real chart, photograph, document or logo. The chart is a diagram: the coast is an invented
outline, not the real coastline, and nothing on it is to scale."""
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
# Captions sit at 86% of the height (y 860 to 1000) and the HUD label in the top right corner: cards keep both clear.
def chart(cv, c, top='1A5A80', low='0C2C48'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (0.6, h('14466A')), (1, h(low))])
    for i in range(12):
        cv.drawLine(0, 90 * i, W, 90 * i, P(0xFFFFFFFF, 2, a=0.07))
    for i in range(16):
        cv.drawLine(130 * i, 0, 130 * i, H, P(0xFFFFFFFF, 2, a=0.07))
    for i in range(26):                                            # the sea keeps moving under the chart
        yy = 40 + 40 * i
        xx = (rn(i, 31) * W + c.t * (90 + 80 * rn(i, 32))) % (W + 300) - 300
        cv.drawLine(xx, yy, xx + 160 + 140 * rn(i, 33), yy, P(0xFFFFFFFF, 7, a=0.24))
    for i in range(9):                                             # and the wind over it
        yy = 120 + 105 * i
        xx = (rn(i, 51) * W + c.t * (520 + 260 * rn(i, 52))) % (W + 500) - 400
        cv.drawLine(xx, yy, xx + 260, yy - 60, P(0xFFFFFFFF, 9, a=0.3))


def land(cv, pts, seed=1):
    cv.drawPath(poly(pts), P(LAND))
    cv.drawPath(poly(pts), P(h('D8D0A8'), 7))


def note(cv):
    fit(cv, 'DIAGRAM, NOT TO SCALE', 1650, 1036, 30, 500, 0x99FFFFFF, None)


COAST = [(-20, 140), (190, 170), (330, 300), (300, 450), (400, 560), (330, 700), (380, 820), (250, 1000), (120, 1100), (-20, 1100)]


def map_card(cv, c):
    """'Floating a hundred and twenty-five kilometres off the coast.' A drawn chart: a coast, a dotted line out to the hut."""
    chart(cv, c)
    land(cv, COAST)
    for i in range(7):
        cv.drawCircle(60 + 190 * rn(i, 1), 240 + 700 * rn(i, 2), 14 + 16 * rn(i, 3), P(h('4E6A3A'), a=0.6))
    k = ease(c.k / 0.6)
    x0, y0, x1 = 400, 600, 1380
    xe = lerp(x0, x1, k)
    for i in range(int((xe - x0) / 36)):
        cv.drawCircle(x0 + 36 * i + 14, y0, 7, P(AMBER))
    cv.save()
    cv.translate(xe + 90, y0 + 20 + 5 * math.sin(c.t * 2.2))
    cv.rotate(3 * math.sin(c.t * 1.7))
    hut_mark(cv, 0, 0, 1.3)
    cv.restore()
    cv.drawLine(xe + 150, y0 + 40, xe + 190, y0 + 240, P(h('D8C8A0'), 6))            # the one rope, down to the seabed
    fit(cv, f'{int(round(125 * k))} KM', 900, 330, 190, 800, AMBER)
    fit(cv, 'FROM LAND', 900, 430, 70, 700, 0xFFFFFFFF)
    fit(cv, 'NORTH SULAWESI', 200, 640, 32, 300, 0xFFFFFFFF)
    note(cv)


def pay_card(cv, c):
    """'He has done this since he was sixteen. The pay is about a hundred and thirty dollars a month.'"""
    Wd.vgrad(cv, 0, 0, W, 620, [(0, h('0A1432')), (1, h('2A4078'))])
    Wd.vgrad(cv, 0, 620, W, H, [(0, h('143660')), (1, h('060E20'))])
    for i in range(40):
        cv.drawCircle(W * rn(i, 1), 560 * rn(i, 2), 1.5 + 2 * rn(i, 3), P(0xFFFFFFFF, a=0.3 + 0.5 * abs(math.sin(c.t * 2 + i))))
    for i in range(14):
        yy = 650 + 30 * i
        xx = (rn(i, 4) * W + c.t * (30 + 20 * rn(i, 5))) % W
        cv.drawLine(xx, yy, xx + 110 + 80 * rn(i, 6), yy, P(0xFFFFFFFF, 4, a=0.14))
        cv.drawLine((xx * 1.7 + c.t * 120) % W, yy + 15, (xx * 1.7 + c.t * 120) % W + 150, yy + 15, P(0xFFFFFFFF, 4, a=0.1))
    Wd.glow(cv, 1460, 560, 330, h('FFE2A0'), 0.5)
    cv.save()
    cv.translate(1400, 640 + 8 * math.sin(c.t * 2.2))
    cv.rotate(3 * math.sin(c.t * 1.7))
    hut_mark(cv, 0, 0, 2.0)
    cv.restore()
    k1 = ease(c.lt / 0.3)
    fit(cv, 'SINCE HE WAS', 620, 210, 80, 900, 0xFFFFFFFF)
    cv.save()
    cv.translate(620, 420)
    cv.scale(1.3 - 0.3 * k1, 1.3 - 0.3 * k1)
    fit(cv, '16', 0, 0, 220, 500, AMBER)
    cv.restore()
    if c.k > 0.45:
        k2 = ease((c.k - 0.45) / 0.15)
        cv.save()
        cv.translate(620, 640)
        cv.scale(1.3 - 0.3 * k2, 1.3 - 0.3 * k2)
        fit(cv, 'ABOUT $130', 0, 0, 150, 1000, AMBER)
        cv.restore()
        fit(cv, 'A MONTH', 620, 740, 76, 700, 0xFFFFFFFF)


def boat_mark(cv, x, y, s, col):
    cv.drawPath(poly([(x - 70 * s, y - 22 * s), (x + 84 * s, y - 22 * s), (x + 60 * s, y), (x - 60 * s, y)]), P(col))
    cv.drawRect(skia.Rect.MakeXYWH(x - 40 * s, y - 46 * s, 34 * s, 24 * s), P(col))


def before_card(cv, c):
    """'This has happened to him before. Twice. Both times, the owner's boat came out and found him.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('7EBCE6')), (0.52, h('CFE6F2')), (0.53, h('1C6E94')), (1, h('0A2E48'))])
    for j, (lab, sub) in enumerate((('1ST TIME', 'ADRIFT A WEEK'), ('2ND TIME', 'ADRIFT TWO DAYS'))):
        t0 = 0.05 + 0.4 * j
        if c.k < t0:
            continue
        k = ease((c.k - t0) / 0.3)
        cx = 500 + 920 * j
        cv.save()
        cv.translate(cx - 110, 590 + 6 * math.sin(c.t * 2.2 + j))
        hut_mark(cv, 0, 0, 1.25, lamp=False)
        cv.restore()
        boat_mark(cv, lerp(cx + 520, cx + 130, k), 600, 1.5, h('E4E8EC'))
        fit(cv, lab, cx, 230, 96, 760, AMBER)
        fit(cv, sub, cx, 330, 62, 760, 0xFFFFFFFF)
        if k > 0.9:
            stamp(cv, 'FOUND', cx + 40, 740, -6, min(1, (k - 0.9) / 0.1), 76, GREEN)
    cv.drawLine(960, 150, 960, 800, P(0xFFFFFFFF, 6, a=0.5))


SUL = [(-20, 760), (220, 720), (420, 800), (520, 930), (470, 1100), (-20, 1100)]


def track(cv, k, pts, col=AMBER, r=7, step=30):
    """A dotted track through pts, drawn up to fraction k; returns where its head is."""
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    tot = sum(seg)
    d, pos = 0.0, pts[0]
    while d <= tot * k:
        u, i = d, 0
        while i < len(seg) - 1 and u > seg[i]:
            u -= seg[i]
            i += 1
        f = min(1.0, u / seg[i])
        pos = (lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f))
        cv.drawCircle(pos[0], pos[1], r, P(col))
        d += step
    return pos


DRIFT = [(560, 700), (760, 560), (1000, 440), (1240, 360), (1480, 300)]


def north_card(cv, c):
    """'This time, no boat comes. The wind carries him north, away from every other hut, and out into open ocean.'"""
    chart(cv, c)
    land(cv, SUL)
    fit(cv, 'NORTH SULAWESI', 245, 850, 36, 380, 0xFFFFFFFF)
    for i in range(16):                                            # the other huts, still on their ropes
        x, y = 420 + 330 * rn(i, 21), 560 + 200 * rn(i, 22)
        cv.drawCircle(x, y, 9, P(h('FFE9A8'), a=0.9))
        cv.drawCircle(x, y, 18, P(h('FFE9A8'), a=0.18))
    k = ease(c.k / 0.85)
    pos = track(cv, k * 0.62, DRIFT)
    cv.save()
    cv.translate(pos[0], pos[1] - 10)
    cv.rotate(-10 + 4 * math.sin(c.t * 5))
    hut_mark(cv, 0, 0, 0.95)
    cv.restore()
    for i in range(6):                                             # wind
        yy = 240 + 80 * i
        xx = 300 + 1300 * ((c.t * 0.9 + i * 0.19) % 1)
        cv.drawLine(xx, yy, xx + 150, yy - 70, P(0xFFFFFFFF, 6, a=0.4))
    cv.drawLine(1700, 330, 1700, 150, P(0xFFFFFFFF, 10))
    cv.drawPath(poly([(1670, 170), (1700, 100), (1730, 170)]), P(0xFFFFFFFF))
    fit(cv, 'N', 1700, 400, 60, 100, 0xFFFFFFFF)
    fit(cv, 'NO BOAT COMES', 1280, 770, 110, 1000, AMBER)
    note(cv)


def guam_card(cv, c):
    """'He is in the waters off Guam now, thousands of kilometres from home.' The track of the hut across the chart, to a small island."""
    chart(cv, c)
    land(cv, SUL)
    fit(cv, 'NORTH SULAWESI', 245, 850, 36, 380, 0xFFFFFFFF)
    cv.drawPath(poly([(1600, 250), (1640, 215), (1672, 240), (1655, 300), (1615, 310)]), P(LAND))
    fit(cv, 'GUAM', 1640, 190, 54, 300, 0xFFFFFFFF)
    k = ease(c.k / 0.7)
    pos = track(cv, k, DRIFT)
    cv.save()
    cv.translate(pos[0], pos[1] - 10 + 4 * math.sin(c.t * 2.2))
    cv.rotate(6 * math.sin(c.t * 4))
    hut_mark(cv, 0, 0, 1.5, lamp=False)
    cv.restore()
    fit(cv, '14 JULY', 560, 640, 46, 400, 0xFFFFFFFF)
    if k > 0.95:
        fit(cv, '31 AUGUST', 1380, 420, 46, 400, 0xFFFFFFFF)
    fit(cv, 'DAY 49', 1180, 760, 150, 900, AMBER)
    note(cv)


JAPAN = [(1180, 60), (1420, 40), (1500, 120), (1400, 210), (1250, 250), (1120, 330), (1010, 320), (1060, 220), (1150, 160)]


def japan_card(cv, c):
    """'The ship is bound for Japan. So that's where Aldi goes.' The ship's line north from Guam to a harbour."""
    chart(cv, c)
    land(cv, JAPAN)
    fit(cv, 'JAPAN', 1280, 150, 60, 300, 0xFFFFFFFF)
    cv.drawPath(poly([(1500, 760), (1540, 725), (1572, 750), (1555, 810), (1515, 820)]), P(LAND))
    fit(cv, 'GUAM', 1660, 790, 50, 300, 0xFFFFFFFF)
    k = ease(c.k / 0.75)
    pos = track(cv, k, [(1470, 740), (1330, 600), (1180, 470), (1090, 350)])
    ship_mark(cv, pos[0], pos[1] + 14, 0.5, h('E8E6DE'))
    cv.drawCircle(1090, 330, 14, P(RED))
    fit(cv, 'TOKUYAMA', 560, 330, 120, 900, AMBER)
    fit(cv, '6 SEPTEMBER 2018', 560, 430, 62, 900, 0xFFFFFFFF)
    cv.drawLine(900, 330, 1070, 330, P(0xFFFFFFFF, 5, a=0.7))
    note(cv)


def days_card(cv, c):
    """The days: a sun crosses the sky above the little hut, again and again, and the count climbs."""
    ph = (c.k * 5.0) % 1
    lightk = math.sin(ph * math.pi)
    top = Wd.mix(h('0E1A40'), h('6CB8E8'), lightk)
    low = Wd.mix(h('2A2A5A'), h('F2B078'), 1 - abs(lightk - 0.5) * 2 if lightk < 0.9 else 0.2)
    Wd.vgrad(cv, 0, 0, W, 640, [(0, top), (1, low)])
    sx, sy = lerp(-80, W + 80, ph), 600 - 480 * math.sin(ph * math.pi)
    Wd.glow(cv, sx, sy, 240, h('FFE2A0'), 0.6)
    cv.drawCircle(sx, sy, 56, P(h('FFE9B0')))
    Wd.vgrad(cv, 0, 640, W, H, [(0, Wd.mix(h('0E2A48'), h('1C6E94'), lightk)), (1, h('081828'))])
    for i in range(12):
        yy = 660 + 34 * i
        xx = (rn(i, 4) * W + c.t * (30 + 20 * rn(i, 5))) % W
        cv.drawLine(xx, yy, xx + 110 + 80 * rn(i, 6), yy, P(0xFFFFFFFF, 5, a=0.18))
    cv.save()
    cv.translate(1380, 650 + 8 * math.sin(c.t * 2.2))
    cv.rotate(3 * math.sin(c.t * 1.7))
    hut_mark(cv, 0, 0, 1.7, lamp=False)
    cv.restore()
    n = 1 + int(47 * ease(c.k))
    fit(cv, f'DAY {n}', 600, 330, 200, 900, AMBER)
    fit(cv, 'ADRIFT', 600, 440, 80, 700, 0xFFFFFFFF)


def ten_card(cv, c):
    """'More than ten ships pass that hut. Not one of them stops.' Ship after ship crosses and is struck through."""
    Wd.vgrad(cv, 0, 0, W, 560, [(0, h('7EBCE6')), (1, h('CFE6F2'))])
    Wd.vgrad(cv, 0, 560, W, H, [(0, h('1C6E94')), (1, h('0A2E48'))])
    for i in range(16):
        yy = 590 + 30 * i
        xx = (rn(i, 41) * W + c.t * (110 + 90 * rn(i, 42))) % (W + 300) - 300
        cv.drawLine(xx, yy, xx + 170 + 120 * rn(i, 43), yy, P(0xFFFFFFFF, 7, a=0.28))
    n = c.k * 15.0
    cnt = min(10, int(n))
    for i in range(11):
        k = n - i
        if k <= 0:
            continue
        row, col = i // 6, i % 6
        x = 330 + 250 * col + (125 if row == 1 else 0)
        y = 420 + 120 * row
        if k < 1:
            x = lerp(-200, x, ease(k))
        ship_mark(cv, x, y, 0.56, h('1F2A3E'))
        if k >= 1:
            cv.drawLine(x - 95, y - 66, x + 95, y + 6, P(RED, 11))
    cv.save()
    cv.translate(960, 640 + 6 * math.sin(c.t * 2.4))
    hut_mark(cv, 0, 0, 1.0, lamp=False)
    cv.restore()
    if cnt >= 1:
        fit(cv, f'{cnt}+ SHIPS' if n >= 10.6 else f'{cnt}', 960, 220, 170, 900, AMBER)
    if n >= 11.2:
        fit(cv, 'NONE STOPPED', 960, 800, 90, 900, 0xFFFFFFFF)


def board(cv, c):
    """Rook's board for this case: weathered planks lashed with rope, a photograph of the hut, and what he found."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('24405A')), (0.5, h('1A2C42')), (1, h('0C141E'))])
    for i in range(13):                                            # planks
        x = 60 + 139 * i
        col = (h('8E6B43'), h('7A5A38'), h('9A7850'))[i % 3]
        cv.drawRect(skia.Rect.MakeXYWH(x, 70, 135, 940), P(col))
        for j in range(4):
            yy = 100 + 800 * rn(i, j)
            cv.drawLine(x + 20 + 90 * rn(i, j + 7), yy, x + 30 + 90 * rn(i, j + 7), yy + 100 + 120 * rn(j, i), P(h('5E4428'), 4, a=0.5))
    for yy in (120, 960):                                          # rope lashings
        cv.drawLine(40, yy, 1880, yy, P(h('3A2A1A'), 28))
        cv.drawLine(40, yy, 1880, yy, P(h('D8C8A0'), 18))
        for i in range(41):
            cv.drawLine(60 + 45 * i, yy - 9, 80 + 45 * i, yy + 9, P(h('A89870'), 4))
    Wd.glow(cv, 600, 500, 800, h('FFC890'), 0.14)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(600, 480)
    cv.scale(s, s)
    cv.rotate(-2.5)
    cv.drawRect(skia.Rect.MakeXYWH(-430 + 12, -290 + 16, 860, 580), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-430, -290, 860, 580), P(PAPER))
    photo(cv, 'hut', 0, -20, 800, 480, (0.5, 0.45))
    cv.restore()
    for x in (240, 960):
        cv.drawCircle(x, 215, 22, P(ORANGE))
        cv.drawCircle(x, 215, 22, P(INK, 5))
    fit(cv, 'CASE 019', 1420, 290, 84, 700, 0xFFFFFFFF)
    if c.lt > 0.3:
        fit(cv, '49 DAYS', 1420, 450, 170, 760, AMBER)
    if c.lt > 0.6:
        fit(cv, 'IN A HUT', 1420, 560, 96, 760, 0xFFFFFFFF)
    if c.lt > 1.0:
        stamp(cv, 'TRUE', 1420, 730, -8, min(1, (c.lt - 1.0) / 0.12), 120, GREEN)


SHOTS = {f.__name__: f for f in (map_card, pay_card, before_card, north_card, guam_card, japan_card, days_card, ten_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def storm(cv, c):
    Wd.rain(cv, W, H, c.t, 170, 0x77CFE6FF, 0.45, 1500, 5, 44)
    Wd.particles(cv, W, H, c.t, 34, 0x88EAF6FF, 71, size=(3, 7), drift=(520, 60), wobble=30)


def rainfall(cv, c):
    Wd.rain(cv, W, H, c.t, 230, 0x88DCEBFF, 0.12, 1700, 9, 50)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 50, 0x99EAF6FF, 73, size=(3, 8), drift=(300, -120), wobble=40)


def glitter(cv, c):
    Wd.particles(cv, W, H, c.t, 24, 0x88FFFFFF, 75, size=(2, 5), drift=(26, -14), wobble=20, twinkle=True)


def embers(cv, c):
    Wd.particles(cv, W, H, c.t, 24, 0xAAFFB060, 77, size=(2, 6), drift=(18, -150), wobble=40, twinkle=True)


def night_air(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x77DCE8FF, 79, size=(2, 4), drift=(10, -6), wobble=10, twinkle=True)


def big(cv, s, x, y, c, t0=0.3, size=150, maxw=800):
    if c.lt > t0:
        k = min(1, (c.lt - t0) / 0.15)
        cv.save()
        cv.translate(x, y)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        fit(cv, s, 0, 0, size, maxw, AMBER)
        cv.restore()


def day_49(cv, c):
    glitter(cv, c)
    big(cv, 'DAY 49', 480, 300, c, 0.15)


def passes(cv, c):
    n = 1 + min(3, int(c.k * 4))
    big(cv, f'PASS {n} OF 4', 520, 240, c, 0.0, 110, 700)
    cv.drawCircle(960, 540, 54, P(AMBER, 7))
    fit(cv, 'THE HUT', 960, 660, 44, 300, 0xFFFFFFFF)


def closed(cv, c):
    if c.lt > 0.9:
        k = min(1, (c.lt - 0.9) / 0.15)
        cv.save()
        cv.translate(430, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 019', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(snap_wide=storm, rope_close=storm, drift_off=storm, boy_face=storm, rook_roof=storm, rope_strain=storm, no_engine=spray, dawn_empty=glitter,
            fishing=glitter, fence_break=glitter, cook=embers, sip=glitter, ship_appears=glitter, wave_cloth=glitter, sail_past=glitter, cry=night_air,
            day49=day_49, call=glitter, wait=glitter, turn=glitter, high_waves=spray, rope_throw=spray, jump=spray, haul=spray, alive=glitter,
            ship_away=glitter, rook_wrong=glitter, signoff=closed, job_wide=glitter, rook_coin=glitter, moored=glitter, supply_boat=glitter,
            walkie=night_air, fifty_huts=night_air, rook_quip=night_air, fish_glow=night_air, wait_boat=glitter, rain=rainfall, wring=glitter,
            rook_tip=glitter, shark_fin=spray, bible=glitter, rook_quiet=glitter, lamp_signal=glitter, night_ship=night_air, alone_wide=night_air,
            carrier_pass=glitter, circle=passes, decide=spray, swim=spray, haircut=glitter, home=glitter, walk_inland=glitter, rook_shore=glitter)


def THUMB(cv, c):
    """1280x720: the 3D still (he waves the cloth at the corner of the raft; a huge hull goes past behind him) and the hook on the left."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('1C6E94'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(600, 0), (0, 0)], [0x00000000, 0xD8000000])))
    Wd.text_card(cv, '10 SHIPS', 300, 290, 128, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'PASSED', 300, 430, 128, RED, 0xFF000000)
    Wd.text_card(cv, 'HIM', 300, 570, 128, RED, 0xFF000000)
