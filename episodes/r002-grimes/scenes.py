"""Case 002 - James Michael Grimes. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(Rook's case wall, the memory gap, the night clock) and the 2D overlays drawn on top of 3D shots."""
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
    """A 3D still (rendered by world3d.STILLS) taped to the wall as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('5E7088')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def slate(cv, t):
    """Rook's travelling case wall for this one: a navy chart with a compass grid."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('14233C')), (1, h('0A1424'))])
    for i in range(0, W + 1, 120):
        cv.drawLine(i, 0, i, H, P(0x1AFFFFFF, 2))
    for j in range(0, H + 1, 120):
        cv.drawLine(0, j, W, j, P(0x1AFFFFFF, 2))
    for r in (260, 520, 780):
        cv.drawCircle(820, 1500, r + 6 * math.sin(t * 2 + r), P(0x22FF7A1A, 3))
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(h('FF7A1A'), 10))


def taped(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    for sx in (-1, 1):
        cv.save()
        cv.translate(sx * (w_ / 2 - 30), -h_ / 2 + 6)
        cv.rotate(sx * 38)
        cv.drawRect(skia.Rect.MakeXYWH(-70, -24, 140, 48), P(Wd.alpha(h('FFD866'), 0.85)))
        cv.restore()
    cv.restore()


def board_fall(cv, c):
    slate(cv, c.t)
    k = min(1, c.lt / 0.22)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    taped(cv, 540, 640, 820 * s, 600 * s, 2.5)
    cv.save()
    cv.translate(540, 640)
    cv.rotate(2.5)
    cv.scale(s, s)
    photo(cv, 'liner', 0, 10, 760, 500, (0.5, 0.5))
    cv.restore()
    k2 = min(1, max(0, (c.lt - 0.3) / 0.25))
    if k2 > 0:
        x0, y0, x1, y1 = 700, 560, 760, 900
        ye = lerp(y0, y1, k2)
        cv.drawLine(x0, y0, lerp(x0, x1, k2), ye, P(h('FF7A1A'), 14))
        if k2 >= 1:
            cv.drawLine(x1, y1, x1 - 50, y1 - 46, P(h('FF7A1A'), 14))
            cv.drawLine(x1, y1, x1 + 34, y1 - 58, P(h('FF7A1A'), 14))
    k3 = min(1, max(0, (c.lt - 0.55) / 0.15))
    if k3 > 0:
        cv.save()
        cv.translate(430, 1080)
        cv.scale(1 + 0.5 * (1 - k3), 1 + 0.5 * (1 - k3))
        taped(cv, 0, 0, 560, 240, -5, h('FFD866'))
        cv.rotate(-5)
        Wd.text_card(cv, 'FELL OFF?', 0, 34, 92, INK, None)
        cv.restore()


def memory_gap(cv, c):
    """He remembers none of it: a dead screen where the memory should be."""
    t, k = c.t, c.k
    Wd.fill(cv, 0, 0, W, H, 0xFF05060A)
    R = Wd.Rand(int(t * 15) + 3)
    for i in range(70):
        y = R(0, H)
        cv.drawRect(skia.Rect.MakeXYWH(R(-200, W), y, R(80, 700), R(2, 9)), P(Wd.alpha(0xFFFFFFFF, R(0.04, 0.22))))
    roll = (t * 520) % (H + 300) - 150
    cv.drawRect(skia.Rect.MakeXYWH(0, roll, W, 110), P(0x18FFFFFF))
    s = 1 + 0.08 * math.sin(t * 9)
    cv.save()
    cv.translate(540 + 14 * math.sin(t * 31), 660)
    cv.scale(s, s)
    Wd.text_card(cv, '?', 0, 150, 620, h('FFB000'), 0xFF000000)
    cv.restore()
    if k > 0.3:
        Wd.text_card(cv, 'NO MEMORY', 540, 1100, 110, 0xFFFFFFFF, 0xFF000000)
    cv.drawCircle(120, 150, 26, P(h('E5392F') if (t * 2.5) % 1 < 0.6 else 0x33E5392F))
    Wd.text_card(cv, '11:00 PM', 330, 176, 64, 0xFFFFFFFF, 0xFF000000)


def all_night(cv, c):
    """The hours go by: a clock face spinning under a crossing moon."""
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('050A1A')), (0.6, h('0B2038')), (1, h('06101E'))])
    Wd.particles(cv, W, H * 0.6, t * 0.4, 60, Wd.alpha(0xFFFFFFFF, 0.7), 5, size=(2, 5), drift=(6, 0), wobble=3, twinkle=True)
    a = math.radians(lerp(200, 340, k))
    mx, my = 540 + math.cos(a) * 620, 1150 + math.sin(a) * 800
    Wd.glow(cv, mx, my, 150, h('E8F0FF'), 0.5)
    cv.drawCircle(mx, my, 62, P(h('E8F0FF')))
    cx, cy, r = 540, 900, 330
    cv.drawCircle(cx, cy, r + 18, P(0xFF000000))
    cv.drawCircle(cx, cy, r, P(h('F4EEDF')))
    for i in range(12):
        ang = math.radians(i * 30)
        cv.drawLine(cx + math.sin(ang) * (r - 50), cy - math.cos(ang) * (r - 50), cx + math.sin(ang) * (r - 14), cy - math.cos(ang) * (r - 14), P(INK, 12))
    hr = math.radians(lerp(330, 330 + 210, k))
    mn = math.radians(k * 360 * 7)
    cv.drawLine(cx, cy, cx + math.sin(hr) * 180, cy - math.cos(hr) * 180, P(INK, 24))
    cv.drawLine(cx, cy, cx + math.sin(mn) * 270, cy - math.cos(mn) * 270, P(h('FF7A1A'), 14))
    cv.drawCircle(cx, cy, 26, P(INK))
    for i in range(5):
        y = 1560 + i * 70
        off = (t * 140 * (1 + i * 0.3)) % 240
        for x in range(-240, W + 240, 240):
            cv.drawLine(x + off, y, x + off + 130, y, P(Wd.alpha(h('5E8FD0'), 0.5), 8))


def board_true(cv, c):
    slate(cv, c.t)
    taped(cv, 540, 640, 680, 760, -2)
    cv.save()
    cv.translate(540, 640)
    cv.rotate(-2)
    photo(cv, 'james', 0, 10, 610, 650, (0.5, 0.3))
    cv.restore()
    k = min(1, max(0, (c.lt - 0.25) / 0.12))
    if c.lt > 0.25:
        cv.save()
        cv.translate(520, 930)
        cv.rotate(-13)
        cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
        cv.drawRoundRect(skia.Rect.MakeLTRB(-300, -110, 300, 110), 20, 20, P(h('E5392F'), 22))
        Wd.text_card(cv, 'TRUE', 0, 62, 180, h('E5392F'), None)
        cv.restore()
    k2 = min(1, max(0, (c.lt - 0.55) / 0.15))
    if k2 > 0:
        cv.save()
        cv.translate(690, 1110)
        cv.scale(1 + 0.5 * (1 - k2), 1 + 0.5 * (1 - k2))
        taped(cv, 0, 0, 520, 210, 5, h('FFD866'))
        cv.rotate(5)
        Wd.text_card(cv, 'UP TO 20 HRS', 0, 26, 64, INK, None)
        cv.restore()


SHOTS = {f.__name__: f for f in (board_fall, memory_gap, all_night, board_true)}


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


def spindrift(cv, c):
    Wd.particles(cv, W, H, c.t, 34, Wd.alpha(h('CFE6FF'), 0.22), 13, size=(2, 5), drift=(-60, 10), wobble=18)


def how(cv, c):
    spindrift(cv, c)
    stamp(cv, c, 'HOW?', 540, 520, 230, 0.3)


def no_ship(cv, c):
    spindrift(cv, c)
    stamp(cv, c, 'NO SHIP', 540, 430, 150, 0.35, 'FFFFFF', 4)


def contest(cv, c):
    stamp(cv, c, 'AIR GUITAR CONTEST', 540, 480, 78, 0.1, 'FFD866', -3)


def winner(cv, c):
    stamp(cv, c, 'WINNER', 540, 420, 200, 0.2, 'FFB000', -7)


def age(cv, c):
    stamp(cv, c, 'JAMES, 28', 540, 420, 120, 0.15, 'FFFFFF', 3)


def never_back(cv, c):
    stamp(cv, c, 'NEVER CAME BACK', 540, 440, 92, 0.45, 'E5392F', -4)


def no_jacket(cv, c):
    spindrift(cv, c)
    stamp(cv, c, 'NO LIFE JACKET', 540, 430, 100, 0.3, 'FFFFFF', -4)


def murk(cv, c):
    Wd.particles(cv, W, H, c.t, 46, Wd.alpha(h('BFE6FF'), 0.3), 9, size=(2, 6), drift=(-14, -36), wobble=24)


def socks(cv, c):
    spindrift(cv, c)
    stamp(cv, c, 'SOCKS?', 560, 430, 190, 0.25, 'FFB000', 6)


def wash(cv, c):
    Wd.particles(cv, W, H, c.t * 2.2, 60, Wd.alpha(h('E8F4FF'), 0.3), 21, size=(2, 6), drift=(-160, 60), wobble=40)


def spotted(cv, c):
    stamp(cv, c, 'SPOTTED', 540, 430, 170, 0.3, 'FFB000', -6)


def minute(cv, c):
    wash(cv, c)
    stamp(cv, c, '1 MINUTE LEFT', 540, 400, 104, 0.3, 'E5392F', -4)


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'CASE 002  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(wake_wide=spindrift, no_ship=no_ship, top_down=how, lounge_wide=contest, guitar_cu=age, winner=winner, door_swing=never_back,
            ship_leaves=spindrift, tread_cu=no_jacket, rook_ring=spindrift, under_bump=murk, socks_wave=socks, rook_socks=spindrift,
            carrier_big=spindrift, bridge_spot=spotted, heli_in=wash, swimmer_down=wash, rook_hat=wash, hoist_up=minute, signoff=closed)
