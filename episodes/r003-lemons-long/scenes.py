"""Case 003 - Chris Lemons. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(Rook's case wall, the emergency-gas gauge, the cold-and-oxygen card) and the 2D overlays drawn on top of 3D shots."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) pinned to the wall as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('2E6A70')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def wall(cv, t):
    """Rook's case wall for this one: a sea-green dive chart with a depth scale down the side."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E3A3C')), (1, h('051A1E'))])
    for j in range(0, H + 1, 96):
        cv.drawLine(0, j, W, j, P(0x16FFFFFF, 2))
    for i in range(11):
        y = 180 + i * 150
        cv.drawLine(40, y, 110 if i % 5 == 0 else 80, y, P(h('FFB000'), 6))
    cv.drawLine(40, 180, 40, 1680, P(h('FFB000'), 6))
    Wd.text_card(cv, '100 M', 150, 1700, 44, h('FFB000'), None)
    for i in range(7):
        x = 220 + i * 130
        y = (t * 60 + i * 290) % (H + 200)
        cv.drawCircle(x + 20 * math.sin(t * 2 + i), H - y, 9 + (i % 3) * 5, P(0x30BFF6FF, 4))
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(h('FF7A1A'), 10))


def pinned(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 30, 20, P(h('E5392F')))
    cv.drawCircle(-5, -h_ / 2 + 25, 7, P(0x88FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col='FFD866'):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, h(col))
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.42, size, INK, None)
    cv.restore()


def gauge(cv, cx, cy, r, frac, t, label, sub, danger=False):
    """A round pressure gauge. frac 1 = full, 0 = empty."""
    cv.drawCircle(cx, cy, r + 26, P(0xFF000000))
    cv.drawCircle(cx, cy, r + 14, P(h('C8CCD4')))
    cv.drawCircle(cx, cy, r, P(h('F4EEDF')))
    arc = skia.Rect.MakeLTRB(cx - r + 46, cy - r + 46, cx + r - 46, cy + r - 46)
    pa = P(h('E5392F'), 44)
    cv.drawArc(arc, 135, 62, False, pa)
    cv.drawArc(arc, 197, 208, False, P(h('3DAA6A'), 44))
    for i in range(11):
        a = math.radians(135 + i * 27)
        cv.drawLine(cx + math.cos(a) * (r - 96), cy + math.sin(a) * (r - 96), cx + math.cos(a) * (r - 22), cy + math.sin(a) * (r - 22), P(INK, 10))
    a = math.radians(135 + 270 * max(0.0, min(1.0, frac)) + (2.5 * math.sin(t * 40) if danger else 0))
    cv.drawLine(cx - math.cos(a) * 50, cy - math.sin(a) * 50, cx + math.cos(a) * (r - 70), cy + math.sin(a) * (r - 70), P(h('FF7A1A'), 22))
    cv.drawCircle(cx, cy, 34, P(INK))
    Wd.text_card(cv, label, cx, cy + r * 0.56, 76, INK, None)
    Wd.text_card(cv, sub, cx, cy - r - 90, 62, 0xFFFFFFFF, 0xFF000000)


def deepwater(cv, t, top='072A2C', bot='02090C'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    Wd.particles(cv, W, H, t, 50, Wd.alpha(h('BFF6FF'), 0.35), 4, size=(2, 6), drift=(-10, -50), wobble=22)


def gas_five(cv, c):
    """His bail-out bottles: about five minutes."""
    deepwater(cv, c.t)
    k = min(1, c.lt / 0.18)
    cv.save()
    cv.translate(540, 660)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    cv.translate(-540, -660)
    gauge(cv, 540, 660, 320, lerp(0.62, 0.5, c.k), c.t, 'GAS', 'EMERGENCY BOTTLES')
    cv.restore()
    k2 = min(1, max(0, (c.lt - 0.3) / 0.14))
    if k2 > 0:
        cv.save()
        cv.translate(540, 1150)
        cv.scale(1.6 - 0.6 * k2, 1.6 - 0.6 * k2)
        Wd.text_card(cv, 'ABOUT 5 MINUTES', 0, 0, 92, h('FFB000'), 0xFF000000)
        cv.restore()


def gas_zero(cv, c):
    """Then the needle reaches the stop."""
    deepwater(cv, c.t, '051C20', '010506')
    gauge(cv, 540, 660, 320, lerp(0.22, 0.0, min(1, c.lt / 0.55)), c.t, 'GAS', 'EMERGENCY BOTTLES', danger=c.lt > 0.55)
    if c.lt > 0.55:
        on = (c.t * 3) % 1 < 0.6
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('E5392F'), 0.16 if on else 0.05)))
        k2 = min(1, (c.lt - 0.55) / 0.12)
        cv.save()
        cv.translate(540, 1170)
        cv.scale(1.7 - 0.7 * k2, 1.7 - 0.7 * k2)
        Wd.text_card(cv, 'EMPTY', 0, 0, 170, h('E5392F'), 0xFF000000)
        cv.restore()


def board_gas(cv, c):
    wall(cv, c.t)
    k = min(1, c.lt / 0.22)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    pinned(cv, 560, 500, 760 * s, 560 * s, -2.5)
    cv.save()
    cv.translate(560, 500)
    cv.rotate(-2.5)
    cv.scale(s, s)
    photo(cv, 'bell', 0, 24, 700, 440, (0.5, 0.35))
    cv.restore()
    card(cv, '5 MIN OF GAS', 400, 900, 560, 170, -5, 70, min(1, max(0, (c.lt - 0.3) / 0.14)))
    card(cv, '30 MIN WAIT', 700, 1090, 540, 170, 4, 70, min(1, max(0, (c.lt - 0.55) / 0.14)), 'F4EEDF')
    if c.lt > 0.8:
        k3 = min(1, (c.lt - 0.8) / 0.12)
        cv.save()
        cv.translate(560, 1560)
        cv.rotate(-6)
        cv.scale(1.7 - 0.7 * k3, 1.7 - 0.7 * k3)
        Wd.text_card(cv, 'NO CHANCE', 0, 0, 150, h('E5392F'), 0xFF000000)
        cv.restore()


def why_cold(cv, c):
    """The best guess: near-freezing water and oxygen-rich gas."""
    wall(cv, c.t)
    k = min(1, c.lt / 0.16)
    cv.save()
    cv.translate(540, 420)
    cv.scale(0.55 + 0.25 * k, 0.55 + 0.25 * k)
    cv.rotate(c.t * 14)
    for i in range(6):
        cv.save()
        cv.rotate(i * 60)
        cv.drawLine(0, 0, 0, -250, P(h('BFEFFF'), 26))
        for d in (-110, -180):
            cv.drawLine(0, d, 62, d - 62, P(h('BFEFFF'), 20))
            cv.drawLine(0, d, -62, d - 62, P(h('BFEFFF'), 20))
        cv.restore()
    cv.restore()
    Wd.text_card(cv, 'COLD WATER', 540, 740, 110, 0xFFFFFFFF, 0xFF000000)
    k2 = min(1, max(0, (c.lt - 0.6) / 0.14))
    if k2 > 0:
        cv.save()
        cv.translate(540, 890)
        cv.scale(1.6 - 0.6 * k2, 1.6 - 0.6 * k2)
        Wd.text_card(cv, '+', 0, -30, 130, h('FFB000'), 0xFF000000)
        for i, x in enumerate((-250, 0, 250)):
            cv.drawCircle(x, 120 + 14 * math.sin(c.t * 4 + i), 80, P(h('FF7A1A')))
            cv.drawCircle(x, 120 + 14 * math.sin(c.t * 4 + i), 80, P(0xFF000000, 10))
            Wd.text_card(cv, 'O2', x, 150 + 14 * math.sin(c.t * 4 + i), 78, 0xFFFFFFFF, None)
        Wd.text_card(cv, 'OXYGEN-RICH GAS', 0, 310, 84, h('FFB000'), 0xFF000000)
        cv.restore()


def board_true(cv, c):
    wall(cv, c.t)
    pinned(cv, 560, 540, 640, 720, 2)
    cv.save()
    cv.translate(560, 540)
    cv.rotate(2)
    photo(cv, 'diver', 0, 28, 570, 590, (0.5, 0.25))
    cv.restore()
    k = min(1, max(0, (c.lt - 0.25) / 0.12))
    if c.lt > 0.25:
        cv.save()
        cv.translate(540, 830)
        cv.rotate(-13)
        cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
        cv.drawRoundRect(skia.Rect.MakeLTRB(-300, -110, 300, 110), 20, 20, P(h('E5392F'), 22))
        Wd.text_card(cv, 'TRUE', 0, 62, 180, h('E5392F'), None)
        cv.restore()
    card(cv, 'ABOUT 30 MIN, NO GAS', 580, 1090, 760, 170, 4, 60, min(1, max(0, (c.lt - 0.55) / 0.15)))


SHOTS = {f.__name__: f for f in (gas_five, gas_zero, board_gas, why_cold, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(cv, c, text, x, y, size, at=0.25, col='FFB000', ang=-5):
    if c.lt > at:
        k = min(1, (c.lt - at) / 0.12)
        cv.save()
        cv.translate(x, y)
        cv.rotate(ang)
        cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
        Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
        cv.restore()


def snow(cv, c):
    """Marine snow drifting through the lamp light."""
    Wd.particles(cv, W, H, c.t, 46, Wd.alpha(h('D8F6FF'), 0.3), 17, size=(2, 6), drift=(-22, 26), wobble=20)


def squall(cv, c):
    Wd.rain(cv, W, H, c.t, density=90, c=0x66DCEAEA, slant=0.4, speed=1900, seed=5, length=40)


def deep_stamp(cv, c):
    snow(cv, c)
    stamp(cv, c, '100 M DOWN', 540, 420, 130, 0.25, 'FFFFFF', -4)


def gone(cv, c):
    snow(cv, c)
    stamp(cv, c, 'THE BELL IS GONE', 540, 420, 92, 0.4, 'E5392F', 3)


def name(cv, c):
    snow(cv, c)
    stamp(cv, c, 'CHRIS LEMONS', 540, 400, 104, 0.15, 'FFFFFF', 3)


def lifeline(cv, c):
    snow(cv, c)
    stamp(cv, c, 'HIS GAS', 400, 470, 140, 0.45, 'FFB000', -6)


def dp_fail(cv, c):
    on = (c.t * 3.0) % 1 < 0.5
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('E5392F'), 0.12 if on else 0.0)))
    stamp(cv, c, 'POSITION LOST', 540, 430, 110, 0.3, 'E5392F', -4)


def drifting(cv, c):
    squall(cv, c)
    stamp(cv, c, 'DRIFTING', 540, 430, 170, 0.3, 'FFFFFF', 5)


def snagged(cv, c):
    snow(cv, c)
    stamp(cv, c, 'SNAGGED', 560, 420, 170, 0.35, 'FFB000', -5)


def rovcam(cv, c):
    """Camera furniture for the ROV feed: scan lines, corner brackets, a blinking REC dot."""
    for y in range(0, H, 8):
        cv.drawLine(0, y, W, y, P(0x16000000, 3))
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('3DDC84'), 0.07)))
    roll = (c.t * 700) % (H + 300) - 150
    cv.drawRect(skia.Rect.MakeXYWH(0, roll, W, 90), P(0x14FFFFFF))
    L = 110
    for x, y, sx, sy in ((70, 420, 1, 1), (W - 70, 420, -1, 1), (70, 1250, 1, -1), (W - 70, 1250, -1, -1)):
        cv.drawLine(x, y, x + sx * L, y, P(0xFFFFFFFF, 8))
        cv.drawLine(x, y, x, y + sy * L, P(0xFFFFFFFF, 8))
    cv.drawLine(540 - 46, 835, 540 + 46, 835, P(0x99FFFFFF, 4))
    cv.drawLine(540, 835 - 46, 540, 835 + 46, P(0x99FFFFFF, 4))
    if (c.t * 2.2) % 1 < 0.6:
        cv.drawCircle(120, 350, 22, P(h('E5392F')))
    Wd.text_card(cv, 'ROV CAM', 310, 372, 60, 0xFFFFFFFF, 0xFF000000)
    if c.k > 0.62:
        stamp(cv, c, 'NO MOVEMENT', 540, 1120, 92, 0.0, 'E5392F', -3)


def later(cv, c):
    squall(cv, c)
    stamp(cv, c, 'ABOUT 30 MIN LATER', 540, 430, 84, 0.2, 'FFFFFF', -3)


def alive(cv, c):
    stamp(cv, c, 'BREATHING', 540, 1175, 116, 0.55, 'FFB000', -3)


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'CASE 003  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(snap=snow, fall_back=snow, alone_wide=deep_stamp, bell_away=gone, ship_wide=squall, bell_down=snow, work=name, valve_cu=snow,
            rook_cable=lifeline, alarm=dp_fail, ship_drift=drifting, cable_tight=snagged, rook_flinch=snow, climb=snow, rook_sit=snow,
            still_body=snow, rov_in=snow, rov_pov=rovcam, rook_low=snow, ship_back=later, lift=snow, rook_point=snow, haul_up=snow,
            eyes_open=alive, signoff=closed)
