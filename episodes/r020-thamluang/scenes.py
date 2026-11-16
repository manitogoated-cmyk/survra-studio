"""Case 020 - the Tham Luang cave rescue. The story is filmed in 3D (world3d.py). This file holds the flat
inserts (the nine nights scratched on rock, a drawn cross-section of a flooded cave, the thirteen ticked off,
Rook's case board on a slab of limestone) and the 2D overlays drawn on top of 3D shots (monsoon rain, drips
in the cave, silt in the flooded tunnel, the count, the sign-off). Every card is a drawing made for this
film; none of them reproduces a real map, survey, document, photograph or logo, and the cross-section is a
diagram of the idea, not of the real cave: it shows no distances."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F0E8D2'), h('D8362A'), h('3EC46A')
ROCK, ROCKD, WATER, MUD = h('5C6258'), h('2A302C'), h('2F8FB8'), h('8A6A48')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 78.233 + j * 37.719) * 43758.5453) % 1


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
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


def rock_wall(cv, seed=1, glow=0.0):
    """A wall of wet limestone: Rook's board for this case."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('4A524A')), (0.5, h('343A36')), (1, h('1A1E1C'))])
    for i in range(14):                                           # facets
        x, y = rn(i, seed) * W, rn(i, seed + 1) * H
        s = 200 + 320 * rn(i, seed + 2)
        cv.drawPath(poly([(x, y), (x + s, y + 0.25 * s), (x + 0.8 * s, y + 0.9 * s), (x - 0.25 * s, y + 0.55 * s)]),
                    P(h('7E8676') if i % 2 else h('121614'), a=0.16))
    for i in range(9):                                            # wet streaks
        x = rn(i, seed + 3) * W
        cv.drawLine(x, 0, x + 40 * (rn(i, seed + 4) - 0.5), H * (0.3 + 0.6 * rn(i, seed + 5)), P(h('A8D8E8'), 6, a=0.12))
    if glow:
        Wd.glow(cv, 540, 900, 900, h('FFC890'), 0.18 * glow)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x44000000), (0.5, 0x00000000), (1, 0x88000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.restore()


def stamp(cv, s, x, y, ang, k, size=150, col=RED):
    """A rubber stamp that slams down (k 0..1)."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
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


# ---------------------------------------------------------------- inserts
def nights_card(cv, c):
    """'...for nine nights.' Nine marks scratched on the rock, one after another, each with a small moon."""
    rock_wall(cv, 3, 1.0)
    fit(cv, 'NINE NIGHTS', 540, 430, 150, 940, AMBER)
    n = min(9, int(c.k * 10.5) + 1)
    for i in range(9):
        x, y = 190 + 88 * i + (40 if i >= 5 else 0), 820
        if i < n:
            j = 8 * (rn(i, 7) - 0.5)
            cv.drawLine(x + j, y - 150, x - j, y + 150, P(0xFF000000, 30))
            cv.drawLine(x + j, y - 150, x - j, y + 150, P(h('F0E8D2'), 18))
            cv.drawCircle(x, y + 235, 22, P(h('E8EEF8')))
            cv.drawCircle(x + 11, y + 229, 19, P(h('343A36')))
        else:
            cv.drawLine(x, y - 150, x, y + 150, P(h('7E8676'), 6, a=0.25))
    if n >= 5:
        cv.drawLine(150, 900, 590, 740, P(0xFF000000, 30))
        cv.drawLine(150, 900, 590, 740, P(h('F0E8D2'), 18))
    Wd.particles(cv, W, H, c.t, 26, 0x88CFE8FF, 41, size=(2, 5), drift=(0, 420), wobble=6)


TUNNEL = [(150, 700), (300, 760), (420, 720), (540, 860), (660, 800), (780, 930), (900, 880)]


def map_card(cv, c):
    """A drawn cross-section: the way in on the left, the dry ledge on the right, and water in between."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1418')), (1, h('1A2428'))])
    cv.drawPath(poly([(-20, 620), (120, 520), (330, 400), (560, 330), (800, 420), (1100, 360), (1100, 1960), (-20, 1960)]), P(ROCK))
    cv.drawPath(poly([(-20, 1000), (200, 1040), (520, 1010), (820, 1080), (1100, 1050), (1100, 1960), (-20, 1960)]), P(ROCKD))
    for i in range(16):
        x, y = 60 + 64 * i, 380 + 90 * rn(i, 11) + (120 if i < 3 else 0)
        Wd.leaf(cv, x, y - 20, 70, -90 + 30 * (rn(i, 12) - 0.5), h('2B5A32'))
    path = skia.Path()
    path.moveTo(*TUNNEL[0])
    for q in TUNNEL[1:]:
        path.lineTo(*q)
    cv.drawPath(path, P(0xFF05080A, 96))
    cv.drawPath(poly([(60, 640), (190, 640), (190, 770), (60, 770)]), P(0xFF05080A))        # the mouth
    cv.drawCircle(940, 850, 92, P(0xFF05080A))                                             # the chamber
    k = ease(c.k * 1.6)
    wet = skia.Path()
    wet.moveTo(*TUNNEL[1])
    for q in TUNNEL[2:6]:
        wet.lineTo(*q)
    pa = P(WATER, 84)
    pa.setPathEffect(skia.DashPathEffect.Make([1300 * k + 1, 3000], 0))
    cv.drawPath(wet, pa)
    for i in range(6):                                                                     # ripples in the flooded part
        x = 320 + 80 * i
        if x < 300 + 520 * k:
            y = 745 + 0.35 * (x - 300) + 8 * math.sin(c.t * 6 + i)
            cv.drawLine(x - 16, y, x + 16, y, P(h('BFE8F8'), 5, a=0.7))
    cv.drawPath(poly([(880, 905), (1000, 880), (1010, 935), (880, 940)]), P(MUD))            # the ledge of mud
    for i in range(13):
        cv.drawCircle(893 + 9 * i, 893 - 2 * (i % 3) - 1.3 * i * 0.15, 7, P(AMBER))
    for i in range(3):
        cv.drawLine(84 + 34 * i, 590 - 60, 60 + 34 * i, 590, P(h('CFE6FF'), 6, a=0.8))        # rain at the mouth
    fit(cv, 'WAY OUT', 190, 560, 60, 330, 0xFFFFFFFF)
    if c.lt > 0.3:
        fit(cv, 'FLOODED', 530, 640, 84, 520, h('7FD4F4'))
    if c.lt > 0.6:
        fit(cv, '13', 930, 760, 96, 200, AMBER)
    fit(cv, 'NOT TO SCALE', 540, 1620, 44, 600, 0x99FFFFFF, None)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x66000000)])


def thirteen_card(cv, c):
    """'...all thirteen come out alive.' Thirteen small figures, ticked off one by one."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2A4A')), (0.6, h('2C3A5C')), (1, h('141C30'))])
    Wd.glow(cv, 540, 760, 900, h('FFC890'), 0.22)
    n = c.k * 15.5
    for i in range(13):
        row, col = (0, i) if i < 5 else (1, i - 5) if i < 9 else (2, i - 9)
        cnt = (5, 4, 4)[row]
        x = 540 + (col - (cnt - 1) / 2) * 190
        y = 560 + row * 250
        big = i == 12
        s = 1.25 if big else 1.0
        colr = h('34466A') if big else h(('B8322E', '2F6FB0', 'E4DFD0', '2E8A5A', 'D8A22A', '7A3FA0')[i % 6])
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 44 * s, y - 20 * s, 88 * s, 110 * s), 26, 26, P(colr))
        cv.drawCircle(x, y - 58 * s, 40 * s, P(h('C8946A')))
        cv.drawCircle(x, y - 70 * s, 41 * s, P(h('17131A'), a=1.0))
        cv.drawCircle(x, y - 50 * s, 38 * s, P(h('C8946A')))
        tick(cv, x + 46, y + 66, 1.5, min(1.0, max(0.0, n - i)))
    if c.k > 0.8:
        fit(cv, '13 OF 13', 540, 1680, 150, 900, GREEN)
    fit(cv, '8 TO 10 JULY 2018', 540, 330, 76, 900, 0xFFFFFFFF)


def pin_13(cv, c):
    """Rook's board: the thirteen on the ledge, and his own tally."""
    rock_wall(cv, 5, 0.6)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 640)
    cv.scale(s, s)
    card(cv, 0, 0, 800, 760, -3)
    cv.rotate(-3)
    photo(cv, 'ledge', 0, -30, 730, 620, (0.5, 0.55))
    cv.restore()
    for x in (180, 900):
        cv.drawCircle(x, 300, 26, P(h('D8DCE4')))
        cv.drawCircle(x, 300, 26, P(INK, 5))
    if c.lt > 0.15:
        cv.drawLine(540, 1040, 540, 1090, P(ORANGE, 8))
        card(cv, 540, 1140, 820, 110, 2, h('FFD866'))
    if c.lt > 0.3:
        fit(cv, 'THIRTEEN IN', 540, 1610, 110, 900, 0xFFFFFFFF)
    if c.lt > 0.55:
        fit(cv, 'THIRTEEN OUT', 540, 1740, 110, 900, AMBER)
    if c.lt > 0.8:
        stamp(cv, 'TRUE', 760, 330, -10, min(1, (c.lt - 0.8) / 0.12), 140, GREEN)


SHOTS = {f.__name__: f for f in (nights_card, map_card, thirteen_card, pin_13)}


# ---------------------------------------------------------------- overlays on the 3D shots
def monsoon(cv, c):
    Wd.rain(cv, W, H, c.t, 170, 0x99CFE6FF, 0.22, 2300, 3, 60)
    Wd.rain(cv, W, H, c.t, 60, 0x66FFFFFF, 0.3, 3000, 8, 90)


def mouth_rain(cv, c):
    """Seen from inside the cave: rain only in the bright opening, drips nearer the lens."""
    Wd.particles(cv, W, H, c.t, 22, 0x99CFE8FF, 43, size=(2, 5), drift=(0, 900), wobble=5)


def drips(cv, c):
    Wd.particles(cv, W, H, c.t, 18, 0x88CFE8FF, 47, size=(2, 5), drift=(0, 700), wobble=6)
    Wd.particles(cv, W, H, c.t, 14, 0x44FFF0D0, 49, size=(2, 4), drift=(20, 40), wobble=30, twinkle=True)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 46, 0x99DCF0F8, 51, size=(3, 8), drift=(-260, 520), wobble=24)


def silt(cv, c):
    Wd.particles(cv, W, H, c.t, 70, 0x66D8F0C8, 53, size=(2, 6), drift=(60, 110), wobble=34, twinkle=True)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x5506281E), (0.5, 0x0006281E), (1, 0x7706281E)])


def current(cv, c):
    Wd.particles(cv, W, H, c.t, 70, 0x88D8F0C8, 55, size=(2, 6), drift=(-240, 900), wobble=20)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x5506281E), (0.5, 0x0006281E), (1, 0x7706281E)])


def count(cv, c):
    """Rook's count along the ledge: twelve boys, and the coach makes thirteen."""
    drips(cv, c)
    n = min(13, 1 + int(min(1.0, c.k / 0.8) * 12.2))
    pop = 1.0 + 0.25 * max(0.0, 1 - ((c.k / 0.8 * 12.2) % 1) * 3) if n < 13 else 1.0 + 0.3 * max(0.0, 1 - (c.k - 0.8) / 0.1)
    cv.save()
    cv.translate(250, 560)
    cv.scale(pop, pop)
    Wd.text_card(cv, str(n), 0, 0, 300, AMBER if n == 13 else 0xFFFFFFFF, 0xFF000000)
    cv.restore()


def dusk_air(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x88FFE8C0, 57, size=(2, 6), drift=(60, -50), wobble=30, twinkle=True)


def closed(cv, c):
    if c.lt > 0.6:
        k = min(1, (c.lt - 0.6) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 020  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(mouth_wide=monsoon, bikes=monsoon, walk_in=mouth_rain, rain_gush=spray, fill=spray, rook_rock=spray, rook_drip=drips, chase=spray,
            scramble=drips, ledge_wide=drips, huddle=drips, torch_dies=drips, divers_fight=current, glow=drips, surface=drips, faces_lit=drips,
            rook_count=count, way_out=drips, sump_long=silt, toe_dip=drips, rook_sound=drips, tanks=drips, rook_vigil=drips, sleep=drips,
            mask_on=drips, carry_in=drips, carry_dark=silt, squeeze=silt, stretcher_out=dusk_air, pump_fail=dusk_air, reflood=spray,
            signoff=closed)
