"""Case 024 - Nicholas Alkemade, the rear gunner who fell about 18,000 feet without a parachute on the night of
24 March 1944 and lived. The story is filmed in 3D (world3d.py). This file holds the flat inserts (a chalk
drawing of what his interrogators suspected, a typed sheet carrying the words of his certificate, and Rook's
case board on a pine plank) and the 2D overlays drawn on top of 3D shots (sparks, snow, dust, the sign-off).
Every card is a drawing made for this film; none of it reproduces a real photograph, document or emblem. The
typed sheet is a plain re-setting of the reported wording, not a copy of the original document."""
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
ORANGE, AMBER, PAPER = h('FF7A1A'), h('FFB000'), h('EFE6CC')
CHALK = h('F0ECE0')


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


def plain(cv, s, x, y, size, color, weight=700, centre=True):
    f = font(size, weight)
    w = f.measureText(s)
    cv.drawTextBlob(skia.TextBlob(s, f), x - (w / 2 if centre else 0), y, P(color))
    return w


# ---------------------------------------------------------------- inserts
def chalk_pine(cv, x, y, s, a=1.0):
    for i in range(4):
        w_, top = s * (150 - 30 * i), y - s * (120 + 95 * i)
        cv.drawPath(poly([(x - w_, top + s * 150), (x, top), (x + w_, top + s * 150)]), P(h('3E7A5E'), a=a))
        cv.drawPath(poly([(x - w_, top + s * 150), (x, top), (x + w_, top + s * 150)]), P(CHALK, 6, a=0.8 * a))
    cv.drawLine(x, y, x, y - s * 120, P(h('8A6A48'), 18 * s, a=a))


def spy_card(cv, c):
    """'Then he's a spy, and he buried it.' Drawn in chalk on a slate: a figure with a spade under the pines, a bundle of parachute going into a hole."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E2A2C')), (0.6, h('172022')), (1, h('0E1416'))])
    for i in range(60):
        x, y = W * rn(i, 1), H * rn(i, 2)
        cv.drawLine(x, y, x + 40 * rn(i, 3), y + 8 * rn(i, 4), P(CHALK, 2, a=0.07))
    fit(cv, 'WHAT THEY SUSPECTED', 540, 250, 80, 940, AMBER)
    chalk_pine(cv, 190, 1140, 1.15)
    chalk_pine(cv, 900, 1150, 1.3)
    chalk_pine(cv, 560, 1010, 0.8, 0.6)
    cv.drawLine(40, 1150, 1040, 1150, P(CHALK, 8, a=0.9))
    k = ease(c.k / 0.75)
    # the hole and the bundle
    cv.drawPath(poly([(560, 1150), (600, 1185), (790, 1185), (830, 1150)]), P(h('0A0E10')))
    by = lerp(1000, 1150, k)
    cv.save()
    cv.clipRect(skia.Rect.MakeXYWH(0, 0, W, 1178))
    cv.drawOval(skia.Rect.MakeXYWH(610, by - 70, 170, 110), P(h('E8E0C8')))
    cv.drawOval(skia.Rect.MakeXYWH(610, by - 70, 170, 110), P(INK, 6))
    for i in range(4):
        cv.drawLine(640 + 36 * i, by - 66, 650 + 30 * i, by + 36, P(h('B8AE90'), 5))
    cv.restore()
    # the figure, bent over a spade
    dig = math.sin(c.t * 7)
    fx, fy = 400, 1150
    cv.drawLine(fx - 20, fy, fx - 10, fy - 150, P(CHALK, 20))
    cv.drawLine(fx + 40, fy, fx + 10, fy - 150, P(CHALK, 20))
    cv.drawLine(fx, fy - 150, fx + 70, fy - 330, P(CHALK, 30))
    cv.drawCircle(fx + 100, fy - 380, 42, P(CHALK))
    hx, hy = fx + 190, fy - 230 + 26 * dig
    cv.drawLine(fx + 70, fy - 320, hx, hy, P(CHALK, 18))
    cv.drawLine(hx - 40, hy - 110, hx + 60, hy + 150, P(h('B88A58'), 12))
    cv.drawPath(poly([(hx + 30, hy + 140), (hx + 90, hy + 130), (hx + 100, hy + 215), (hx + 50, hy + 230)]), P(h('9AA4AC')))
    for i in range(5):
        u = (c.t * 1.6 + i * 0.2) % 1
        cv.drawCircle(hx + 70 + 110 * u, hy + 120 - 160 * u + 240 * u * u, 9, P(CHALK, a=1 - u))
    if c.k > 0.35:
        s = 1.5 - 0.5 * ease((c.k - 0.35) / 0.12)
        cv.save()
        cv.translate(760, 660)
        cv.rotate(-8)
        cv.scale(s, s)
        Wd.text_card(cv, 'SPY?', 0, 0, 230, h('E8483A'), 0xFF000000)
        cv.restore()
    fit(cv, 'NO PARACHUTE = HE BURIED IT', 540, 1640, 76, 960, 0xFFFFFFFF)


LINES = [('It has been investigated', 0.05), ('and corroborated by the', 0.13), ('German authorities that', 0.21), ('his claim is', 0.29)]


def cert_card(cv, c):
    """The typed sheet: the reported words of the certificate he was given, set plainly. The key phrases are struck in as they are spoken."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A2420')), (0.5, h('1E1A16')), (1, h('120F0C'))])
    k = ease(min(1, c.lt / 0.2))
    cv.save()
    cv.translate(540, 900)
    cv.rotate(-2.0 + 1.0 * math.sin(c.t * 0.8))
    cv.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
    cv.drawRect(skia.Rect.MakeXYWH(-450 + 14, -720 + 18, 900, 1440), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-450, -720, 900, 1440), P(PAPER))
    for i in range(7):
        cv.drawLine(-450, -720 + 205 * i + 30 * rn(i, 5), 450, -716 + 205 * i + 30 * rn(i, 6), P(h('D8CCAC'), 2, a=0.6))
    plain(cv, 'CERTIFICATE', 0, -600, 74, INK, 900)
    cv.drawLine(-250, -570, 250, -570, P(INK, 5))
    for i, (s, at_) in enumerate(LINES):
        if c.k > at_:
            plain(cv, s, 0, -470 + 78 * i, 56, h('2A2622'), 600)
    if c.k > 0.34:
        s = 1.4 - 0.4 * ease((c.k - 0.34) / 0.1)
        cv.save()
        cv.translate(0, -90)
        cv.scale(s, s)
        plain(cv, 'TRUE IN ALL', 0, 0, 104, h('B02A1E'), 900)
        plain(cv, 'RESPECTS', 0, 108, 104, h('B02A1E'), 900)
        cv.restore()
    # the caption band (62 to 78 % of the frame) is left clear on the sheet
    # the spoken figure (18,000) is popped on screen by the engine, in the band left clear here
    if c.k > 0.62:
        plain(cv, 'FEET, WITHOUT', 0, 570, 78, INK, 900)
        plain(cv, 'A PARACHUTE', 0, 655, 78, INK, 900)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 14, 0x44FFE8C8, 91, size=(2, 5), drift=(10, -14), wobble=14, twinkle=True)


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
    """Rook's board for this case: pine planks with knots, a photograph of the man in the dent in the snow pinned with a pine needle sprig."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A1E14')), (1, h('120C08'))])
    for i in range(5):
        x = 30 + 206 * i
        cv.drawRect(skia.Rect.MakeXYWH(x, 110, 198, 1700), P((h('B88E5C'), h('AA8250'), h('C09662'))[i % 3]))
        for j in range(9):
            y = 130 + 1660 * rn(i * 9 + j, 7)
            cv.drawLine(x + 20 + 150 * rn(i + j, 8), y, x + 30 + 150 * rn(i + j, 8), y + 150, P(h('8A6438'), 3, a=0.5))
        ky = 300 + 1300 * rn(i, 9)
        cv.drawOval(skia.Rect.MakeXYWH(x + 60, ky, 70, 44), P(h('6E4A26')))
        cv.drawOval(skia.Rect.MakeXYWH(x + 76, ky + 10, 38, 24), P(h('4A2E14')))
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 660)
    cv.scale(s, s)
    cv.rotate(-2.5)
    cv.drawRect(skia.Rect.MakeXYWH(-380 + 12, -420 + 16, 760, 840), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-380, -420, 760, 840), P(PAPER))
    photo(cv, 'snow', 0, -40, 690, 700, (0.5, 0.5))
    cv.restore()
    for x in (220, 860):
        cv.drawCircle(x, 270, 22, P(ORANGE))
        cv.drawCircle(x, 270, 22, P(INK, 5))
    for i in range(7):                                             # a sprig of pine needles tucked under one pin
        a = -2.4 + 0.3 * i
        cv.drawLine(860, 270, 860 + 130 * math.cos(a), 270 - 130 * math.sin(a), P(h('2E6A4A'), 7))
    if c.lt > 0.2:
        fit(cv, '18,000 FEET', 540, 1560, 124, 920, 0xFFFFFFFF)
    if c.lt > 0.4:
        fit(cv, 'NO PARACHUTE', 540, 1690, 124, 920, AMBER)
    if c.lt > 0.55:
        q = 1.5 - 0.5 * ease((c.lt - 0.55) / 0.12)
        cv.save()
        cv.translate(770, 1020)
        cv.rotate(-12)
        cv.scale(q, q)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-170, -78, 340, 132), 14, 14, P(h('2E9A4E'), 12))
        plain(cv, 'TRUE', 0, 34, 110, h('2E9A4E'), 900)
        cv.restore()


SHOTS = {f.__name__: f for f in (spy_card, cert_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def sparks(cv, c):
    Wd.particles(cv, W, H, c.t, 34, 0xCCFFB040, 93, size=(3, 8), drift=(-40, 520), wobble=40, twinkle=True)
    Wd.particles(cv, W, H, c.t, 14, 0x88FF6A20, 95, size=(4, 10), drift=(-70, 380), wobble=60)


def rush(cv, c):
    """Falling: streaks of cloud and ice going up past the lens."""
    for i in range(22):
        x = W * rn(i, 11)
        y = H - ((c.t * (1500 + 900 * rn(i, 12)) + H * rn(i, 13)) % (H + 300))
        cv.drawLine(x, y, x + 6 * math.sin(i), y + 110 + 120 * rn(i, 14), P(h('DCEBFF'), 4, a=0.22))


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 46, 0xCCF4F8FF, 97, size=(3, 8), drift=(26, 150), wobble=30)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 20, 0x55FFE8C8, 99, size=(2, 5), drift=(12, -16), wobble=16, twinkle=True)


def mist(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x66FFF0E0, 101, size=(2, 6), drift=(30, -10), wobble=24, twinkle=True)


def closed(cv, c):
    snow(cv, c)
    if c.lt > 0.4:
        k = min(1, (c.lt - 0.4) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 024', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(bomber_wide=sparks, turret_fire=sparks, chute_burn=sparks, backflip=sparks, rook_fall=rush, fighter=sparks, wing_fire=sparks, fall_wide=rush,
            rook_maths=rush, fall_close=rush, rook_gives_up=rush, trees_rush=rush, crash_branches=snow, snow_hole=snow, hole_up=snow, rook_measure=snow,
            limbs=snow, knee=snow, lantern=snow, room_wide=dust, gestapo_laugh=dust, rook_room=dust, spy_point=dust, he_points=dust, officer_writes=dust,
            man_smile=dust, rook_hat=dust, search_wood=snow, harness=snow, wreck=snow, chute_pack=mist, four_stones=mist, signoff=closed)
