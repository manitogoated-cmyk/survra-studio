"""Case 020, the full case file (16:9) - the Tham Luang cave rescue. The story is filmed in 3D (world3d.py). This
file holds the flat inserts on a 1920x1080 canvas (the nine nights scratched on rock, a drawn cross-section of a
flooded cave, the air in the chamber, the three options, the three days, the thirteen ticked off, Rook's case
board), the 2D overlays drawn on top of 3D shots, and the thumbnail. Every card is a drawing made for this film;
none reproduces a real map, survey, document, photograph or logo. The cross-section and the chamber are diagrams
of the idea, not of the real cave: they show no distances and no measurements."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F0E8D2'), h('D8362A'), h('3EC46A')
ROCK, ROCKD, WATER, MUD = h('5C6258'), h('2A302C'), h('2F8FB8'), h('8A6A48')
SHIRTS = ('B8322E', '2F6FB0', 'E4DFD0', '2E8A5A', 'D8A22A', '7A3FA0')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 78.233 + j * 37.719) * 43758.5453) % 1


def font(size):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('6A5A48')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def rock_wall(cv, seed=1, glow=0.0, t=0.0):
    """A wall of wet limestone: Rook's board for this case."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('4A524A')), (0.5, h('343A36')), (1, h('1A1E1C'))])
    for i in range(18):
        x, y = rn(i, seed) * W, rn(i, seed + 1) * H
        s = 220 + 340 * rn(i, seed + 2)
        cv.drawPath(poly([(x, y), (x + s, y + 0.25 * s), (x + 0.8 * s, y + 0.9 * s), (x - 0.25 * s, y + 0.55 * s)]),
                    P(h('7E8676') if i % 2 else h('121614'), a=0.16))
    for i in range(14):
        x = rn(i, seed + 3) * W
        cv.drawLine(x, 0, x + 40 * (rn(i, seed + 4) - 0.5), H * (0.3 + 0.6 * rn(i, seed + 5)), P(h('A8D8E8'), 6, a=0.12))
    if glow:
        Wd.glow(cv, 960 + 60 * math.sin(t * 0.9), 520, 900, h('FFC890'), 0.18 * glow)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x44000000), (0.5, 0x00000000), (1, 0x88000000)])
    Wd.particles(cv, W, H, t, 30, 0x88CFE8FF, 41 + seed, size=(2, 5), drift=(0, 420), wobble=6)


def card(cv, x, y, w_, h_, ang, col=PAPER):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.restore()


def stamp(cv, s, x, y, ang, k, size=150, col=RED):
    """A rubber stamp that slams down (k 0..1)."""
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


def tick(cv, x, y, s, k, col=GREEN):
    if k <= 0:
        return
    a, b, c_ = (x - 22 * s, y), (x - 6 * s, y + 18 * s), (x + 26 * s, y - 24 * s)
    k1, k2 = min(1, k * 2), max(0, k * 2 - 1)
    cv.drawLine(a[0], a[1], lerp(a[0], b[0], k1), lerp(a[1], b[1], k1), P(col, 12 * s))
    if k2 > 0:
        cv.drawLine(b[0], b[1], lerp(b[0], c_[0], k2), lerp(b[1], c_[1], k2), P(col, 12 * s))


def person(cv, x, y, s, col, a=1.0):
    """A small drawn figure: a shirt and a head. Nobody in particular."""
    cv.drawRoundRect(skia.Rect.MakeXYWH(x - 44 * s, y - 20 * s, 88 * s, 110 * s), 26 * s, 26 * s, P(col, a=a))
    cv.drawCircle(x, y - 58 * s, 40 * s, P(h('C8946A'), a=a))
    cv.drawCircle(x, y - 70 * s, 41 * s, P(h('17131A'), a=a))
    cv.drawCircle(x, y - 50 * s, 38 * s, P(h('C8946A'), a=a))


# ---------------------------------------------------------------- inserts
def nights_card(cv, c):
    """'Nine nights go by.' Nine marks scratched on the rock, one after another, each with a small moon."""
    rock_wall(cv, 3, 1.0, c.t)
    fit(cv, 'NINE NIGHTS', 960, 210, 150, 1300, AMBER)
    n = min(9, int(c.k * 10.5) + 1)
    for i in range(9):
        x, y = 480 + 112 * i + (60 if i >= 5 else 0), 430
        if i < n:
            j = 8 * (rn(i, 7) - 0.5)
            cv.drawLine(x + j, y - 120, x - j, y + 120, P(0xFF000000, 30))
            cv.drawLine(x + j, y - 120, x - j, y + 120, P(h('F0E8D2'), 18))
            cv.drawCircle(x, y + 185, 22, P(h('E8EEF8')))
            cv.drawCircle(x + 11, y + 179, 19, P(h('343A36')))
        else:
            cv.drawLine(x, y - 120, x, y + 120, P(h('7E8676'), 6, a=0.25))
    if n >= 5:
        cv.drawLine(430, 500, 980, 360, P(0xFF000000, 30))
        cv.drawLine(430, 500, 980, 360, P(h('F0E8D2'), 18))


TUNNEL = [(260, 470), (500, 520), (700, 480), (900, 600), (1120, 540), (1330, 640), (1560, 590)]


def mountain(cv, t):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1418')), (1, h('1A2428'))])
    cv.drawPath(poly([(-20, 420), (220, 330), (560, 220), (980, 160), (1400, 240), (1940, 190), (1940, 1100), (-20, 1100)]), P(ROCK))
    cv.drawPath(poly([(-20, 720), (360, 760), (900, 730), (1420, 790), (1940, 760), (1940, 1100), (-20, 1100)]), P(ROCKD))
    for i in range(26):
        x, y = 60 + 72 * i, 190 + 70 * rn(i, 11) + (150 if i < 3 else 60 if i < 6 else 0)
        Wd.leaf(cv, x, y - 10, 70, -90 + 30 * (rn(i, 12) - 0.5) + 4 * math.sin(t * 1.3 + i), h('2B5A32'))


def map_card(cv, c):
    """A drawn cross-section: the way in on the left, the dry ledge on the right, and water in between."""
    mountain(cv, c.t)
    path = skia.Path()
    path.moveTo(*TUNNEL[0])
    for q in TUNNEL[1:]:
        path.lineTo(*q)
    cv.drawPath(path, P(0xFF05080A, 96))
    cv.drawPath(poly([(110, 410), (290, 410), (290, 540), (110, 540)]), P(0xFF05080A))        # the mouth
    cv.drawCircle(1610, 560, 100, P(0xFF05080A))                                             # the chamber
    k = ease(c.k * 1.6)
    wet = skia.Path()
    wet.moveTo(*TUNNEL[1])
    for q in TUNNEL[2:6]:
        wet.lineTo(*q)
    pa = P(WATER, 84)
    pa.setPathEffect(skia.DashPathEffect.Make([1000 * k + 1, 3000], 0))
    cv.drawPath(wet, pa)
    for i in range(9):
        x = 540 + 90 * i
        if x < 520 + 820 * k:
            y = 512 + 0.15 * (x - 520) + 8 * math.sin(c.t * 6 + i)
            cv.drawLine(x - 16, y, x + 16, y, P(h('BFE8F8'), 5, a=0.7))
    cv.drawPath(poly([(1540, 620), (1680, 590), (1690, 650), (1540, 655)]), P(MUD))            # the ledge of mud
    for i in range(13):
        cv.drawCircle(1556 + 10 * i, 606 - 2 * (i % 3) - 0.2 * i, 7, P(AMBER))
    for i in range(4):
        cv.drawLine(150 + 34 * i + 20 * ((c.t * 3 + i * 0.3) % 1), 300 + 60 * ((c.t * 3 + i * 0.3) % 1), 130 + 34 * i + 20 * ((c.t * 3 + i * 0.3) % 1),
                    350 + 60 * ((c.t * 3 + i * 0.3) % 1), P(h('CFE6FF'), 6, a=0.8))
    fit(cv, 'WAY OUT', 250, 250, 64, 400, 0xFFFFFFFF)
    if c.lt > 0.3:
        fit(cv, 'FLOODED', 920, 400, 96, 620, h('7FD4F4'))
    if c.lt > 0.6:
        fit(cv, '13', 1610, 420, 110, 240, AMBER)
    fit(cv, 'NOT TO SCALE', 960, 800, 44, 600, 0x99FFFFFF, None)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x66000000)])


def air_card(cv, c):
    """'The oxygen in their chamber is running down.' A pocket in the rock, thirteen dots, and a gauge with no numbers."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1418')), (1, h('1A2428'))])
    for i in range(16):
        x, y = rn(i, 21) * W, rn(i, 22) * H
        s = 240 + 300 * rn(i, 23)
        cv.drawPath(poly([(x, y), (x + s, y + 0.25 * s), (x + 0.8 * s, y + 0.9 * s), (x - 0.25 * s, y + 0.55 * s)]), P(h('5C6258') if i % 2 else h('2A302C'), a=0.5))
    k = ease(c.k * 1.15)
    pocket = skia.Path()
    pocket.addOval(skia.Rect.MakeXYWH(330, 170, 900, 440))
    cv.drawPath(pocket, P(0xFF05080A))
    cv.save()
    cv.clipPath(pocket, True)
    cv.drawRect(skia.Rect.MakeXYWH(330, 170, 900, 440), P(h('8FD8F0'), a=lerp(0.42, 0.1, k) * (0.9 + 0.1 * math.sin(c.t * 5))))
    cv.drawPath(poly([(330, 560), (640, 520), (1230, 420), (1230, 620), (330, 620)]), P(MUD))
    cv.drawPath(poly([(330, 548), (600, 540), (700, 620), (330, 620)]), P(WATER))
    for i in range(6):
        x = 360 + 44 * i
        cv.drawLine(x, 560 + 4 * math.sin(c.t * 5 + i), x + 22, 560 + 4 * math.sin(c.t * 5 + i + 1), P(h('BFE8F8'), 4, a=0.7))
    cv.restore()
    for i in range(13):
        cv.drawCircle(760 + 32 * i, 494 - 5.4 * i - 3 * (i % 2), 11, P(AMBER))
    fit(cv, 'THE CHAMBER', 780, 120, 64, 700, 0xFFFFFFFF)
    gx, gy, gw, gh = 1480, 200, 110, 400                                                              # the gauge: full to low, no figures
    cv.drawRoundRect(skia.Rect.MakeXYWH(gx - 8, gy - 8, gw + 16, gh + 16), 18, 18, P(0xFF05080A))
    lv = lerp(0.92, 0.3, k)
    col = h('8FD8F0') if lv > 0.5 else RED
    cv.drawRoundRect(skia.Rect.MakeXYWH(gx, gy + gh * (1 - lv), gw, gh * lv), 12, 12, P(col))
    cv.drawRoundRect(skia.Rect.MakeXYWH(gx - 8, gy - 8, gw + 16, gh + 16), 18, 18, P(0xFFFFFFFF, 6))
    fit(cv, 'OXYGEN', gx + gw / 2, 150, 64, 400, 0xFFFFFFFF)
    if c.lt > 0.5:
        fit(cv, 'RUNNING DOWN', 960, 790, 96, 1100, RED)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x66000000)])


def panel(cv, x, a):
    cv.drawRoundRect(skia.Rect.MakeXYWH(x - 250, 150, 500, 400), 28, 28, P(h('1A2428'), a=a))
    cv.drawRoundRect(skia.Rect.MakeXYWH(x - 250, 150, 500, 400), 28, 28, P(h('7E8676'), 6, a=a))


def options_card(cv, c):
    """'So what do you do?' Three drawings: wait for the water, drill down, teach the boys to dive."""
    rock_wall(cv, 9, 0.5, c.t)
    fit(cv, 'THE OPTIONS', 960, 100, 76, 900, 0xFFFFFFFF)
    a1, a2, a3 = ease((c.k - 0.03) / 0.1), ease((c.k - 0.32) / 0.1), ease((c.k - 0.58) / 0.1)
    if a1 > 0:                                                                                     # wait: a cloud, rain, a water line
        x = 380
        panel(cv, x, a1)
        for dx, dy, r in ((-70, 250, 46), (-10, 232, 60), (60, 252, 44)):
            cv.drawCircle(x + dx, dy, r, P(h('B8C4D0'), a=a1))
        for i in range(7):
            u = (c.t * 1.6 + i * 0.37) % 1
            cv.drawLine(x - 110 + 36 * i, 310 + 90 * u, x - 122 + 36 * i, 345 + 90 * u, P(h('CFE6FF'), 6, a=0.8 * a1))
        wl = skia.Path()
        wl.moveTo(x - 220, 480)
        for i in range(12):
            wl.lineTo(x - 220 + 40 * (i + 1), 480 + 10 * math.sin(c.t * 4 + i))
        cv.drawPath(wl, P(WATER, 16, a=a1))
        fit(cv, 'WAIT', x, 630, 84, 460, 0xFFFFFFFF)
    if a2 > 0:                                                                                     # drill: a shaft coming down to a pocket
        x = 960
        panel(cv, x, a2)
        cv.drawPath(poly([(x - 220, 260), (x - 60, 200), (x + 120, 230), (x + 220, 210), (x + 220, 520), (x - 220, 520)]), P(ROCK, a=a2))
        cv.drawOval(skia.Rect.MakeXYWH(x - 70, 430, 170, 70), P(0xFF05080A, a=a2))
        d = lerp(0, 150, ((c.k - 0.36) / 0.2))
        cv.drawLine(x + 20, 190, x + 20, 230 + d, P(h('D8DCE4'), 14, a=a2))
        cv.drawPath(poly([(x + 6, 230 + d), (x + 34, 230 + d), (x + 20, 258 + d)]), P(AMBER, a=a2))
        fit(cv, 'DRILL', x, 630, 84, 460, 0xFFFFFFFF)
    if a3 > 0:                                                                                     # dive: a mask
        x = 1540
        panel(cv, x, a3)
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 130, 250, 260, 180), 50, 50, P(h('E0C020'), a=a3))
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 104, 274, 208, 132), 36, 36, P(h('6FD0E8'), a=a3))
        cv.drawCircle(x, 462, 34, P(h('9AA0B4'), a=a3))
        for i in range(3):
            u = (c.t * 0.9 + i / 3) % 1
            cv.drawCircle(x + 70 + 20 * math.sin(i * 2 + c.t * 3), 440 - 200 * u, 8 + 8 * u, P(h('BFE8F8'), 5, a=a3 * (1 - u)))
        fit(cv, 'TEACH THEM TO DIVE', x, 630, 84, 470, 0xFFFFFFFF)
        if c.k > 0.8:
            s = ease((c.k - 0.8) / 0.08)
            cv.drawLine(x - 230, 520, x - 230 + 460 * s, 180, P(RED, 22))
            fit(cv, 'TOO RISKY', x, 780, 100, 700, RED)


def days_card(cv, c):
    """'Four boys come out that day. Four more the next. And on the tenth, the last four boys and their coach.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2A4A')), (0.6, h('2C3A5C')), (1, h('141C30'))])
    Wd.glow(cv, 960 + 80 * math.sin(c.t * 0.8), 420, 900, h('FFC890'), 0.22)
    Wd.particles(cv, W, H, c.t, 30, 0x88FFE8C0, 57, size=(2, 6), drift=(60, -50), wobble=30, twinkle=True)
    idx = 0
    for d, (x, label, n) in enumerate(((400, '8 JULY', 4), (960, '9 JULY', 4), (1520, '10 JULY', 5))):
        a = ease((c.k - 0.04 - 0.3 * d) / 0.1)
        if a <= 0:
            idx += n
            continue
        fit(cv, label, x, 190, 100, 470, AMBER)
        for i in range(n):
            big = idx == 12
            px = x + (i - (n - 1) / 2) * 104
            pop = ease((c.k - 0.08 - 0.3 * d - 0.04 * i) / 0.06)
            if pop > 0:
                person(cv, px, 440 - 30 * (1 - pop), 0.92 if not big else 1.12, h('34466A') if big else h(SHIRTS[idx % 6]), pop)
            idx += 1
        fit(cv, 'FOUR' if n == 4 else 'FOUR AND THE COACH', x, 630, 64, 480, 0xFFFFFFFF)
    if c.k > 0.86:
        fit(cv, 'ALL THIRTEEN', 960, 790, 110, 1000, GREEN)


def thirteen_card(cv, c):
    """'Thirteen out of thirteen.' Thirteen small figures, ticked off one by one."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2A4A')), (0.6, h('2C3A5C')), (1, h('141C30'))])
    Wd.glow(cv, 960 + 80 * math.sin(c.t * 0.8), 460, 900, h('FFC890'), 0.22)
    Wd.particles(cv, W, H, c.t, 30, 0x88FFE8C0, 59, size=(2, 6), drift=(60, -50), wobble=30, twinkle=True)
    n = c.k * 15.5
    for i in range(13):
        row, col = (0, i) if i < 7 else (1, i - 7)
        cnt = (7, 6)[row]
        x = 960 + (col - (cnt - 1) / 2) * 210
        y = 330 + row * 230
        big = i == 12
        person(cv, x, y, 1.15 if big else 0.95, h('34466A') if big else h(SHIRTS[i % 6]))
        tick(cv, x + 50, y + 62, 1.4, min(1.0, max(0.0, n - i)))
    if c.k > 0.8:
        fit(cv, '13 OF 13', 960, 800, 110, 900, GREEN)
    fit(cv, '8 TO 10 JULY 2018', 960, 130, 70, 900, 0xFFFFFFFF)


def pin_13(cv, c):
    """Rook's board: the thirteen on the ledge, and his own tally."""
    rock_wall(cv, 5, 0.6, c.t)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(620, 400)
    cv.scale(s, s)
    card(cv, 0, 0, 900, 600, -3)
    cv.rotate(-3)
    photo(cv, 'ledge', 0, -20, 840, 500, (0.5, 0.55))
    cv.restore()
    for x in (200, 1040):
        cv.drawCircle(x, 110, 24, P(h('D8DCE4')))
        cv.drawCircle(x, 110, 24, P(INK, 5))
    if c.lt > 0.3:
        fit(cv, 'THIRTEEN IN', 1470, 300, 100, 760, 0xFFFFFFFF)
    if c.lt > 0.55:
        fit(cv, 'THIRTEEN OUT', 1470, 440, 100, 760, AMBER)
    if c.lt > 0.8:
        stamp(cv, 'TRUE', 1470, 570, -8, min(1, (c.lt - 0.8) / 0.12), 120, GREEN)


SHOTS = {f.__name__: f for f in (nights_card, map_card, air_card, options_card, days_card, thirteen_card, pin_13)}


# ---------------------------------------------------------------- overlays on the 3D shots
def monsoon(cv, c):
    Wd.rain(cv, W, H, c.t, 200, 0x99CFE6FF, 0.22, 1700, 3, 50)
    Wd.rain(cv, W, H, c.t, 70, 0x66FFFFFF, 0.3, 2200, 8, 76)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, 110, 0x77CFE6FF, 0.18, 1500, 5, 40)


def mouth_rain(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x99CFE8FF, 43, size=(2, 5), drift=(0, 700), wobble=5)


def drips(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x88CFE8FF, 47, size=(2, 5), drift=(0, 560), wobble=6)
    Wd.particles(cv, W, H, c.t, 16, 0x44FFF0D0, 49, size=(2, 4), drift=(20, 40), wobble=30, twinkle=True)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 54, 0x99DCF0F8, 51, size=(3, 8), drift=(-300, 380), wobble=24)


def silt(cv, c):
    Wd.particles(cv, W, H, c.t, 80, 0x66D8F0C8, 53, size=(2, 6), drift=(80, 90), wobble=34, twinkle=True)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x5506281E), (0.5, 0x0006281E), (1, 0x7706281E)])


def current(cv, c):
    Wd.particles(cv, W, H, c.t, 80, 0x88D8F0C8, 55, size=(2, 6), drift=(-420, 520), wobble=20)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x5506281E), (0.5, 0x0006281E), (1, 0x7706281E)])


def count(cv, c):
    """Rook's count along the ledge: twelve boys, and the coach makes thirteen."""
    drips(cv, c)
    n = min(13, 1 + int(min(1.0, c.k / 0.8) * 12.2))
    pop = 1.0 + 0.25 * max(0.0, 1 - ((c.k / 0.8 * 12.2) % 1) * 3) if n < 13 else 1.0 + 0.3 * max(0.0, 1 - (c.k - 0.8) / 0.1)
    cv.save()
    cv.translate(300, 330)
    cv.scale(pop, pop)
    Wd.text_card(cv, str(n), 0, 0, 260, AMBER if n == 13 else 0xFFFFFFFF, 0xFF000000)
    cv.restore()


def dusk_air(cv, c):
    Wd.particles(cv, W, H, c.t, 34, 0x88FFE8C0, 57, size=(2, 6), drift=(60, -50), wobble=30, twinkle=True)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x66FFFFFF, 61, size=(2, 5), drift=(24, -14), wobble=22, twinkle=True)


def embers(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0xAAFFC070, 63, size=(2, 6), drift=(14, -110), wobble=36, twinkle=True)


def closed(cv, c):
    if c.lt > 0.6:
        k = min(1, (c.lt - 0.6) / 0.15)
        cv.save()
        cv.translate(470, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 020  CLOSED', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(mouth_wide=monsoon, bikes=monsoon, walk_in=mouth_rain, rain_gush=spray, fill=spray, rook_rock=spray, rook_drip=drips, chase=spray,
            scramble=drips, ledge_wide=drips, huddle=drips, torch_dies=drips, divers_fight=current, glow=drips, surface=drips, faces_lit=drips,
            rook_count=count, way_out=drips, sump_long=silt, toe_dip=drips, rook_sound=drips, tanks=drips, rook_vigil=drips, sleep=drips,
            mask_on=drips, carry_in=drips, carry_dark=silt, squeeze=silt, stretcher_out=dusk_air, pump_fail=dusk_air, reflood=spray,
            signoff=closed, take_under=drips, rook_edge=drips, arrive=motes, locked_bikes=monsoon, camp_wide=monsoon, pumps_row=monsoon, pipe_out=drizzle,
            fields_flood=drizzle, farmer=drizzle, doctor_stay=drips, letters=drips, letter_out=drips, coach_sorry=drips, search_map=drizzle,
            still_water=drips, doc_kit=drips, vials=drips, team_watch=drips, relay=silt, cheer=dusk_air, get_out=spray, out_mouth=dusk_air, ward=motes,
            walk_home=motes, novices=embers, candles=embers, tank_carry=drips, rook_wrong=motes)


def THUMB(cv, c):
    """1280x720: the 3D still (the sleeping boy in his mask on the blanket, the diver kneeling over him) and the hook on the left."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0B2A30'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(640, 0), (0, 0)], [0x00000000, 0xE0000000])))
    Wd.text_card(cv, 'CARRIED', 300, 270, 118, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'OUT', 300, 400, 118, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'ASLEEP', 300, 540, 126, AMBER, 0xFF000000)
