"""Case 002, full case file (16:9) - James Michael Grimes. The story is filmed in 3D (world3d.py). This file holds the flat
graphic inserts (Rook's case wall, the memory gap, the night clock, the call, the search box), the overlays drawn on top
of 3D shots, and the thumbnail."""
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
    for r in (220, 440, 660):
        cv.drawCircle(1560, 820, r + 6 * math.sin(t * 2 + r), P(0x22FF7A1A, 3))
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, W - 14, H - 14), P(h('FF7A1A'), 8))


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
        cv.drawRect(skia.Rect.MakeXYWH(-60, -20, 120, 40), P(Wd.alpha(h('FFD866'), 0.85)))
        cv.restore()
    cv.restore()


def note(cv, c, text, x, y, w_, at, ang=4, size=60, col='FFD866'):
    k = min(1, max(0, (c.lt - at) / 0.15))
    if k > 0:
        cv.save()
        cv.translate(x, y)
        cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
        taped(cv, 0, 0, w_, 170, ang, h(col))
        cv.rotate(ang)
        Wd.text_card(cv, text, 0, size * 0.36, size, INK, None)
        cv.restore()


def board_fall(cv, c):
    slate(cv, c.t)
    k = min(1, c.lt / 0.22)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    taped(cv, 700, 430, 900 * s, 600 * s, -2.5)
    cv.save()
    cv.translate(700, 430)
    cv.rotate(-2.5)
    cv.scale(s, s)
    photo(cv, 'liner', 0, 10, 840, 520, (0.5, 0.5))
    cv.restore()
    k2 = min(1, max(0, (c.lt - 0.4) / 0.3))
    if k2 > 0:
        x0, y0, x1, y1 = 880, 380, 960, 640
        cv.drawLine(x0, y0, lerp(x0, x1, k2), lerp(y0, y1, k2), P(h('FF7A1A'), 14))
        if k2 >= 1:
            cv.drawLine(x1, y1, x1 - 50, y1 - 40, P(h('FF7A1A'), 14))
            cv.drawLine(x1, y1, x1 + 30, y1 - 56, P(h('FF7A1A'), 14))
    note(cv, c, 'FELL OFF?', 1480, 330, 520, 0.8, 5, 84)
    note(cv, c, 'AND LIVED?', 1500, 560, 520, 1.3, -4, 76, 'F4EEDF')


def board_family(cv, c):
    slate(cv, c.t)
    taped(cv, 620, 440, 620, 660, 2)
    cv.save()
    cv.translate(620, 440)
    cv.rotate(2)
    photo(cv, 'james', 0, 10, 550, 560, (0.5, 0.3))
    cv.restore()
    note(cv, c, 'JAMES GRIMES, 28', 1400, 250, 640, 0.3, -4, 58, 'F4EEDF')
    note(cv, c, 'LAFAYETTE, ALABAMA', 1420, 470, 660, 0.9, 3, 54)
    note(cv, c, '18 FAMILY ON BOARD', 1380, 690, 680, 1.6, -3, 56)


def memory_gap(cv, c):
    """He remembers none of it: a dead screen where the memory should be."""
    t, k = c.t, c.k
    Wd.fill(cv, 0, 0, W, H, 0xFF05060A)
    R = Wd.Rand(int(t * 15) + 3)
    for i in range(90):
        y = R(0, H)
        cv.drawRect(skia.Rect.MakeXYWH(R(-200, W), y, R(80, 900), R(2, 9)), P(Wd.alpha(0xFFFFFFFF, R(0.04, 0.22))))
    roll = (t * 420) % (H + 300) - 150
    cv.drawRect(skia.Rect.MakeXYWH(0, roll, W, 90), P(0x18FFFFFF))
    s = 1 + 0.08 * math.sin(t * 9)
    cv.save()
    cv.translate(640 + 14 * math.sin(t * 31), 420)
    cv.scale(s, s)
    Wd.text_card(cv, '?', 0, 150, 520, h('FFB000'), 0xFF000000)
    cv.restore()
    if k > 0.25:
        Wd.text_card(cv, 'NO MEMORY', 1300, 480, 120, 0xFFFFFFFF, 0xFF000000)
    if k > 0.55:
        Wd.text_card(cv, 'of the walk. Or the fall.', 1300, 600, 60, h('FFB000'), 0xFF000000)
    cv.drawCircle(110, 110, 22, P(h('E5392F') if (t * 2.5) % 1 < 0.6 else 0x33E5392F))
    Wd.text_card(cv, '11:00 PM', 300, 132, 56, 0xFFFFFFFF, 0xFF000000)


def all_night(cv, c):
    """The hours go by: a clock face spinning under a crossing moon."""
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('050A1A')), (0.6, h('0B2038')), (1, h('06101E'))])
    Wd.particles(cv, W, H * 0.7, t * 0.4, 80, Wd.alpha(0xFFFFFFFF, 0.7), 5, size=(2, 5), drift=(6, 0), wobble=3, twinkle=True)
    a = math.radians(lerp(200, 340, k))
    mx, my = 960 + math.cos(a) * 900, 900 + math.sin(a) * 760
    Wd.glow(cv, mx, my, 150, h('E8F0FF'), 0.5)
    cv.drawCircle(mx, my, 56, P(h('E8F0FF')))
    cx, cy, r = 700, 480, 300
    cv.drawCircle(cx, cy, r + 16, P(0xFF000000))
    cv.drawCircle(cx, cy, r, P(h('F4EEDF')))
    for i in range(12):
        ang = math.radians(i * 30)
        cv.drawLine(cx + math.sin(ang) * (r - 46), cy - math.cos(ang) * (r - 46), cx + math.sin(ang) * (r - 14), cy - math.cos(ang) * (r - 14), P(INK, 12))
    hr = math.radians(lerp(330, 330 + 210, k))
    mn = math.radians(k * 360 * 7)
    cv.drawLine(cx, cy, cx + math.sin(hr) * 160, cy - math.cos(hr) * 160, P(INK, 22))
    cv.drawLine(cx, cy, cx + math.sin(mn) * 240, cy - math.cos(mn) * 240, P(h('FF7A1A'), 14))
    cv.drawCircle(cx, cy, 24, P(INK))
    Wd.text_card(cv, 'WATER: ABOUT 70°F', 1400, 400, 76, h('FFB000'), 0xFF000000)
    Wd.text_card(cv, 'no life jacket', 1400, 500, 60, 0xFFFFFFFF, 0xFF000000)
    for i in range(4):
        y = 880 + i * 50
        off = (t * 140 * (1 + i * 0.3)) % 240
        for x in range(-240, W + 240, 240):
            cv.drawLine(x + off, y, x + off + 130, y, P(Wd.alpha(h('5E8FD0'), 0.5), 8))


def call_cg(cv, c):
    """The ship calls the Coast Guard."""
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('101A24')), (1, h('05080C'))])
    cv.drawRoundRect(skia.Rect.MakeXYWH(240, 170, 1440, 560), 40, 40, P(h('1B2A38')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(240, 170, 1440, 560), 40, 40, P(h('FF7A1A'), 6))
    Wd.text_card(cv, 'SHIP TO COAST GUARD, NEW ORLEANS', 960, 250, 44, h('FF7A1A'), None)
    n = 60
    for i in range(n):
        a = abs(math.sin(i * 0.9 + t * 14) * math.sin(i * 0.23 + t * 5)) * (0.25 + 0.75 * min(1, k * 3))
        x = 320 + i * (1280 / n)
        cv.drawLine(x, 440 - a * 130, x, 440 + a * 130, P(h('FF7A1A'), 12))
    s = 1 + 0.5 * max(0, 1 - c.lt * 5)
    cv.save()
    cv.translate(960, 650)
    cv.scale(s, s)
    Wd.text_card(cv, 'PASSENGER MISSING', 0, 0, 104, h('FFB000'), 0xFF000000)
    cv.restore()
    cv.drawCircle(110, 110, 22, P(h('E5392F') if (t * 2.5) % 1 < 0.6 else 0x33E5392F))
    Wd.text_card(cv, 'ABOUT 2:30 PM', 380, 132, 56, 0xFFFFFFFF, 0xFF000000)


def map_box(cv, c):
    """The search area on Rook's chart."""
    t, k = c.t, c.k
    slate(cv, t)
    k1 = min(1, c.lt / 0.5)
    x0, y0, x1, y1 = 230, 250, 1010, 760
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), P(Wd.alpha(h('FF7A1A'), 0.16)))
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    per = k1 * 4
    for i in range(4):
        q = min(1, max(0, per - i))
        if q > 0:
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            cv.drawLine(ax, ay, lerp(ax, bx, q), lerp(ay, by, q), P(h('FF7A1A'), 12))
    a = t * 1.6
    sx, sy = 620 + 250 * math.cos(a), 505 + 150 * math.sin(a * 1.3)
    cv.drawCircle(sx, sy, 60, P(Wd.alpha(0xFFFFFFFF, 0.25), 6))
    cv.drawCircle(sx, sy, 8, P(0xFFFFFFFF))
    cv.drawCircle(700, 590, 7, P(h('E5392F')))
    Wd.text_card(cv, 'SEARCH AREA', 620, 210, 60, h('FFB000'), 0xFF000000)
    if k > 0.3:
        Wd.text_card(cv, '7,000+', 1440, 360, 170, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'SQUARE NAUTICAL MILES', 1440, 450, 54, 0xFFFFFFFF, 0xFF000000)
    if k > 0.6:
        note(cv, c, 'ABOUT ONE MASSACHUSETTS', 1440, 660, 760, 0.0, -3, 50)


def board_true(cv, c):
    slate(cv, c.t)
    taped(cv, 640, 440, 620, 660, -2)
    cv.save()
    cv.translate(640, 440)
    cv.rotate(-2)
    photo(cv, 'james', 0, 10, 550, 560, (0.5, 0.3))
    cv.restore()
    k = min(1, max(0, (c.lt - 0.25) / 0.12))
    if c.lt > 0.25:
        cv.save()
        cv.translate(720, 650)
        cv.rotate(-13)
        cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
        cv.drawRoundRect(skia.Rect.MakeLTRB(-300, -110, 300, 110), 20, 20, P(h('E5392F'), 22))
        Wd.text_card(cv, 'TRUE', 0, 62, 180, h('E5392F'), None)
        cv.restore()
    note(cv, c, 'UP TO 20 HOURS', 1420, 300, 620, 0.6, 5, 64)
    note(cv, c, 'NO JACKET. NO BOAT.', 1420, 560, 680, 1.1, -4, 56, 'F4EEDF')


SHOTS = {f.__name__: f for f in (board_fall, board_family, memory_gap, all_night, call_cg, map_box, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(text, x=760, y=180, size=84, at=0.3, col='FFB000', ang=-3):
    def f(cv, c):
        if c.lt > at:
            k = min(1, (c.lt - at) / 0.12)
            cv.save()
            cv.translate(x, y)
            cv.rotate(ang)
            cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
            Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
            cv.restore()
    return f


def spindrift(cv, c):
    Wd.particles(cv, W, H, c.t, 40, Wd.alpha(h('CFE6FF'), 0.22), 13, size=(2, 5), drift=(-60, 10), wobble=18)


def murk(cv, c):
    Wd.particles(cv, W, H, c.t, 56, Wd.alpha(h('BFE6FF'), 0.3), 9, size=(2, 6), drift=(-14, -36), wobble=24)


def wash(cv, c):
    Wd.particles(cv, W, H, c.t * 2.2, 70, Wd.alpha(h('E8F4FF'), 0.3), 21, size=(2, 6), drift=(-160, 60), wobble=40)


def first(f):
    """Only on the first use of a shot type: re-framed repeats (prm alt) keep the picture clean."""
    def g(cv, c):
        if 'alt' not in c.prm:
            f(cv, c)
    return g


def both(*fs):
    def f(cv, c):
        for g in fs:
            g(cv, c)
    return f


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1420, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'CASE 002  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(
    wake_wide=spindrift, no_ship=both(spindrift, stamp('NO SHIP', 960, 180, 130, 0.35, 'FFFFFF', 3)),
    top_down=both(spindrift, first(stamp('HOW?', 1420, 300, 200, 0.3))),
    lounge_wide=stamp('AIR GUITAR CONTEST', 760, 180, 72, 0.1, 'FFD866'), winner=stamp('WINNER', 1400, 260, 170, 0.2, 'FFB000', -7),
    door_swing=stamp('NEVER CAME BACK', 760, 180, 88, 0.45, 'E5392F', -3),
    ship_leaves=spindrift, tread_cu=both(spindrift, first(stamp('NO LIFE JACKET', 1380, 220, 84, 0.3, 'FFFFFF', -4))),
    rook_ring=spindrift, swim_night=spindrift, ship_night=both(spindrift, stamp('THE SHIP SAILS ON', 760, 180, 76, 0.4, 'FFFFFF', -2)),
    jelly=both(murk, first(stamp('JELLYFISH. TWICE.', 760, 180, 80, 0.4, 'F05A8C', -3))), under_bump=murk,
    sunrise=stamp('THANKSGIVING MORNING', 760, 180, 72, 0.4, 'FFD866', -2),
    deck_search=stamp('NOON: REPORTED MISSING', 760, 180, 72, 0.3, 'E5392F', -2),
    ship_turn=stamp('THE VALOR TURNS BACK', 760, 180, 76, 0.4, 'FFFFFF', -2),
    search_air=stamp('HELICOPTER: NEW ORLEANS', 760, 180, 68, 0.3), search_boat=stamp('BOAT: VENICE', 760, 180, 76, 0.3),
    search_plane=stamp('PLANE: MOBILE', 760, 180, 76, 0.3),
    socks_wave=both(spindrift, first(stamp('SOCKS?', 1420, 300, 180, 0.25, 'FFB000', 6))), rook_socks=spindrift, carrier_big=spindrift,
    bridge_spot=first(stamp('8:25 PM: SPOTTED', 760, 180, 92, 0.3, 'FFB000', -4)),
    heli_in=wash, swimmer_down=wash, rook_hat=wash, hoist_up=wash,
    sling=both(wash, stamp('A MINUTE LEFT. MAYBE LESS.', 760, 180, 76, 0.5, 'E5392F', -3)),
    ward=first(stamp('4 DAYS IN INTENSIVE CARE', 760, 180, 68, 0.4, 'FFFFFF', -2)),
    ten_feet=first(stamp('TEN FOOT FROM THE RAIL', 760, 180, 72, 0.5, 'FFD866', -2)),
    signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (James in the swell, the ship leaving, Rook) + a three-word hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0B1A22'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(720, 0), (1280, 0)], [0x00000000, 0xD0000000])))
    Wd.text_card(cv, 'OVERBOARD', 990, 210, 76, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, '20 HOURS', 990, 350, 104, h('FFB000'), 0xFF000000)
    Wd.text_card(cv, 'ALIVE', 990, 510, 130, h('3DDC84'), 0xFF000000)
