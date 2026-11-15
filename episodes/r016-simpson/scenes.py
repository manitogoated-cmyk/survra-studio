"""Case 016 - Joe Simpson and the cut rope. The story is filmed in 3D (world3d.py). This file holds the flat
inserts (the days card, Rook's case board on a sheet of ice, the two-climbers card, the closing question) and
the 2D overlays drawn on top of 3D shots (storm snow, ice dust in the crevasse, glitter on the glacier, stars
over the camp, the sign-off). Every card is a drawing made for this film; none of them reproduces a real
document, photograph, book cover, film still or logo."""
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
ICE, NIGHT = h('3F6FAE'), h('070B1C')


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
        cv.drawRect(dst, P(h('7A94B8')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def ice_board(cv, t=0.0):
    """Rook's board for this case: a sheet of blue ice with cracks in it, held by four ice screws."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2C5C96')), (0.55, h('1B3F70')), (1, h('0E2244'))])
    for i in range(9):                                            # facets of lighter ice
        x, y = rn(i, 1) * W, rn(i, 2) * H
        s = 220 + 300 * rn(i, 3)
        cv.drawPath(poly([(x, y), (x + s, y + 0.2 * s), (x + 0.7 * s, y + 0.9 * s), (x - 0.2 * s, y + 0.6 * s)]), P(h('7FB0E0'), a=0.10))
    for i in range(7):                                            # cracks
        x, y = rn(i, 4) * W, rn(i, 5) * H
        pts = [(x, y)]
        for j in range(5):
            x, y = x + 90 * (rn(i, 6 + j) - 0.3), y + 70 + 90 * rn(i, 12 + j)
            pts.append((x, y))
        cv.drawPath(poly(pts, False), P(h('CFE4FA'), 5, a=0.35))
    cv.drawRoundRect(skia.Rect.MakeLTRB(40, 60, W - 40, H - 50), 30, 30, P(h('CFE4FA'), 14, a=0.5))
    for x, y in ((80, 100), (W - 80, 100), (80, H - 90), (W - 80, H - 90)):
        cv.drawCircle(x, y, 32, P(h('D8DCE4')))
        cv.drawCircle(x, y, 32, P(INK, 5))
        cv.drawLine(x - 16, y - 16, x + 16, y + 16, P(h('5A6070'), 9))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.5, 0x00000000), (1, 0x66000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=64):
    card(cv, x, y, w_, h_, ang, col)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    for i, s in enumerate(lines):
        fit(cv, s, 0, (i - (len(lines) - 1) / 2) * size * 1.12 + size * 0.36, size, w_ - 50, INK, None)
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


def twinkle(cv, t, n=70, top=1250, seed=4):
    for i in range(n):
        x, y = rn(i, seed) * W, rn(i, seed + 1) * top
        a = 0.35 + 0.65 * abs(math.sin(t * (1.5 + 3 * rn(i, seed + 2)) + i))
        cv.drawCircle(x, y, 2.5 + 3.5 * rn(i, seed + 3), P(0xFFF4F8FF, a=a))


def figure(cv, x, y, s, col, sit=False, hang=False):
    """A small drawn climber: a head, a body, a hat. Nobody in particular."""
    if sit:
        cv.drawPath(poly([(x - 26 * s, y - 60 * s), (x + 26 * s, y - 60 * s), (x + 34 * s, y), (x + 80 * s, y + 8 * s), (x + 80 * s, y + 30 * s), (x - 30 * s, y + 30 * s)]), P(col))
    else:
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 28 * s, y - 60 * s, 56 * s, 92 * s), 14 * s, 14 * s, P(col))
        cv.drawLine(x - 14 * s, y + 30 * s, x - 18 * s, y + 84 * s, P(h('27334F'), 20 * s))
        cv.drawLine(x + 14 * s, y + 30 * s, x + 26 * s, y + 80 * s, P(h('27334F'), 20 * s))
    if hang:
        cv.drawLine(x - 20 * s, y - 50 * s, x - 6 * s, y - 120 * s, P(col, 18 * s))
        cv.drawLine(x + 20 * s, y - 50 * s, x + 6 * s, y - 120 * s, P(col, 18 * s))
    cv.drawCircle(x, y - 84 * s, 26 * s, P(h('E0B090')))
    cv.drawPath(poly([(x - 28 * s, y - 88 * s), (x + 28 * s, y - 88 * s), (x + 20 * s, y - 116 * s), (x - 20 * s, y - 116 * s)]), P(h('2D5FA8') if hang else h('D8B030')))


def tick(cv, x, y, s, k):
    if k <= 0:
        return
    cv.drawCircle(x, y, 58 * s, P(GREEN, a=k))
    cv.drawPath(poly([(x - 28 * s, y), (x - 8 * s, y + 22 * s), (x + 30 * s, y - 24 * s)], False), P(0xFFFFFFFF, 14 * s, a=k))


# ------------------------------------------------------------------ flat inserts
def days_card(cv, c):
    """'...for days.' The sun and the moon go over; a dotted track creeps along. No number is given."""
    day = 0.5 + 0.5 * math.cos(c.k * 2 * math.pi * 2.0)             # two days and nights in the shot
    top = Wd.mix(h('0A1230'), h('4E94E0'), day)
    Wd.vgrad(cv, 0, 0, W, H, [(0, top), (0.62, Wd.mix(h('1A2450'), h('BFE0FF'), day)), (1, h('1A2440'))])
    if day < 0.5:
        twinkle(cv, c.t, 60, 1000, 9)
    a = c.k * 2 * math.pi * 2.0
    cx, cy, r = 540, 1150, 760
    sx, sy = cx - r * math.sin(a), cy - r * math.cos(a)             # the sun
    Wd.glow(cv, sx, sy, 150, h('FFD070'), 0.5)
    cv.drawCircle(sx, sy, 84, P(h('FFD070')))
    mx, my = cx + r * math.sin(a), cy + r * math.cos(a)             # the moon, opposite
    cv.drawCircle(mx, my, 62, P(h('E8EEF8')))
    cv.drawCircle(mx + 26, my - 14, 54, P(top))
    snow = Wd.mix(h('5A6C98'), h('F4F8FF'), day)
    cv.drawPath(poly([(-40, 1220), (220, 900), (360, 1010), (560, 760), (700, 930), (860, 840), (1120, 1180), (1120, 1960), (-40, 1960)]), P(Wd.mix(h('1E2A4E'), h('7E8AA6'), day)))
    cv.drawPath(poly([(560, 760), (640, 860), (590, 880), (540, 850), (490, 900), (470, 870)]), P(snow))
    cv.drawPath(poly([(-40, 1340), (300, 1250), (700, 1300), (1120, 1230), (1120, 1960), (-40, 1960)]), P(snow))
    cv.drawPath(poly([(-40, 1560), (400, 1500), (800, 1560), (1120, 1520), (1120, 1960), (-40, 1960)]), P(Wd.mix(h('2A2C3A'), h('8A847C'), day)))
    n = 16
    for i in range(n):                                            # the track: off the ice, down onto the rocks
        if i / n > c.k * 1.15:
            break
        x = 150 + i * 52
        y = 1300 + 16 * math.sin(i * 0.8) + (i / n) ** 2 * 300
        cv.drawCircle(x, y, 13, P(ORANGE))
    fit(cv, 'DAY AFTER DAY', 540, 420, 110, 900, 0xFFFFFFFF)


def pop_photo(cv, c, name, y, w_, h_, ang, focus):
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, y)
    cv.scale(s, s)
    card(cv, 0, 0, w_ + 70, h_ + 100, ang)
    cv.rotate(ang)
    photo(cv, name, 0, 20, w_, h_, focus)
    cv.restore()


def pin_same(cv, c):
    """'He said he would have done the same.' A note in Rook's words, not a quotation."""
    ice_board(cv, c.t)
    pop_photo(cv, c, 'men', 560, 700, 600, -3, (0.5, 0.5))
    if c.lt > 0.12:
        cv.drawLine(540, 930, 540, 985, P(ORANGE, 8))
        note(cv, 540, 1075, 860, 190, 3, h('FFD866'), ["HE'D HAVE DONE THE SAME"], 70)
    for i, s_ in enumerate(('JOE SIMPSON', 'ON SIMON YATES')):
        if c.lt > 0.3 + i * 0.2:
            fit(cv, s_, 540, 1560 + i * 110, 84, 880, 0xFFFFFFFF if i == 0 else AMBER, None)
    if c.lt > 0.8:
        stamp(cv, 'TRUE', 740, 300, -10, min(1, (c.lt - 0.8) / 0.12), 140, GREEN)


def cliff(cv, cut_k=0.0, taut=1.0):
    """The drawn cliff: a slope, a lip, an overhang, and the two of them on one rope."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B1C')), (0.7, h('1A2450')), (1, h('0C1228'))])
    cv.drawPath(poly([(1120, 380), (560, 760), (640, 1500), (1120, 1500)]), P(h('B8C8E4')))
    cv.drawPath(poly([(560, 760), (640, 1500), (1120, 1500), (1120, 900), (700, 880)]), P(h('3F6FAE')))
    cv.drawPath(poly([(560, 760), (700, 880), (1120, 900), (1120, 820)]), P(h('7FB0E0')))
    sx, sy = 900, 500                                             # the man in the seat
    jx, jy = 520, 1180                                            # the man on the rope
    mx, my = lerp(sx, 560, 0.55), lerp(sy + 30, 760, 0.55)
    if cut_k <= 0:
        cv.drawPath(poly([(sx - 40, sy + 30), (560, 756), (jx, jy - 120)], False), P(ORANGE, 12))
    else:
        cv.drawLine(sx - 40, sy + 30, mx + 20, my - 14, P(ORANGE, 12))
        d = 40 * cut_k
        cv.drawPath(poly([(mx - 20 - d, my + 14 + d), (560, 756 + d), (jx, jy - 120)], False), P(ORANGE, 12))
        for i in range(6):
            a = i * 1.05
            cv.drawLine(mx + 16 * math.cos(a), my + 16 * math.sin(a), mx + (40 + 30 * cut_k) * math.cos(a), my + (40 + 30 * cut_k) * math.sin(a), P(0xFFFFFFFF, 7, a=1 - 0.6 * cut_k))
    figure(cv, sx, sy, 1.25, h('2F9A68'), sit=True)
    figure(cv, jx, jy, 1.25, h('C8372D'), hang=True)
    return (sx, sy), (jx, jy)


def both_card(cv, c):
    """'He lived, and so did the man who cut it.'"""
    k = ease((c.lt - 0.1) / 0.2)
    (sx, sy), (jx, jy) = cliff(cv, k)
    Wd.particles(cv, W, H, c.t, 40, 0x88F4F8FF, 5, size=(3, 7), drift=(-260, 200), wobble=26)
    tick(cv, jx - 190, jy - 30, 1.5, ease((c.lt - 0.3) / 0.12))
    tick(cv, sx - 10, sy - 260, 1.5, ease((c.lt - 0.6) / 0.12))
    if c.lt > 0.6:
        fit(cv, 'BOTH LIVED', 440, 300, 120, 760, AMBER)


def question(cv, c):
    """The closing question."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B1C')), (0.5, h('14204A')), (1, h('070B1C'))])
    Wd.particles(cv, W, H, c.t, 60, 0x88F4F8FF, 7, size=(3, 8), drift=(-520, 240), wobble=30)
    y = 1010 + 10 * math.sin(c.t * 30) * max(0.0, 1 - c.lt / 0.4)
    cv.drawLine(-20, y - 60, W + 20, y + 60, P(h('C85A10'), 46))
    for i in range(24):
        x = -20 + i * 48
        yy = y - 60 + 120 * (x + 20) / (W + 40)
        cv.drawLine(x, yy - 18, x + 22, yy + 20, P(ORANGE, 12))
    bx = 540 + 30 * math.sin(c.t * 5)                              # a small blade resting on it
    cv.drawPath(poly([(bx - 20, y - 300), (bx + 60, y - 290), (bx + 26, y - 30), (bx - 8, y - 20)]), P(h('E8EEF8')))
    cv.drawPath(poly([(bx - 20, y - 300), (bx + 6, y - 296), (bx + 2, y - 24), (bx - 8, y - 20)]), P(h('9AA6BC')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(bx - 34, y - 470, 104, 180), 20, 20, P(h('A8472E')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(bx - 34, y - 470, 104, 180), 20, 20, P(INK, 6))
    k = ease(c.lt / 0.18)
    cv.save()
    cv.translate(540, 330)
    cv.scale(1.3 - 0.3 * k, 1.3 - 0.3 * k)
    fit(cv, 'WOULD YOU', 0, 0, 150, 960, 0xFFFFFFFF)
    fit(cv, 'HAVE CUT IT?', 0, 160, 150, 960, AMBER)
    cv.restore()


SHOTS = {f.__name__: f for f in (days_card, pin_same, both_card, question)}


# ------------------------------------------------------------------ overlays on 3D shots
def blizzard(cv, c):
    """Snow driven flat across the cliff."""
    Wd.particles(cv, W, H, c.t, 90, 0xCCF4F8FF, 7, size=(3, 8), drift=(-1100, 260), wobble=30)
    for j in range(8):
        ph = rn(j, 3)
        x = W + 450 - ((c.t * 2100 * (0.6 + ph)) + ph * 4000) % (W + 900)
        y = (ph * 7919) % H + 100 * math.sin(c.t * 2 + j)
        cv.drawLine(x, y, x - 320, y + 70, P(0xFFFFFFFF, 9 + 7 * ph, a=0.13))


def icefall(cv, c):
    """Ice dust sifting down inside the crevasse."""
    Wd.particles(cv, W, H, c.t, 46, 0xAACFE4FA, 13, size=(2, 6), drift=(20, 330), wobble=22, twinkle=True)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 36, 0xAAFFF0D0, 29, size=(2, 6), drift=(30, 90), wobble=30, twinkle=True)


def glitter(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0xEEFFFFFF, 11, size=(3, 7), drift=(160, -60), wobble=30, twinkle=True)


def dustblow(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x66FFF0D8, 31, size=(2, 6), drift=(260, 30), wobble=30)


def night_camp(cv, c):
    twinkle(cv, c.t, 46, 560, 23)
    Wd.particles(cv, W, H, c.t, 16, 0x66FFD8A0, 17, size=(2, 5), drift=(40, -60), wobble=30, twinkle=True)


def dawn_air(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0xCCFFE8D0, 19, size=(3, 7), drift=(170, 80), wobble=30, twinkle=True)


def closed(cv, c):
    dawn_air(cv, c)
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 016  YOUR VERDICT?', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(grip=blizzard, leg_hang=blizzard, hang_wide=blizzard, slack=blizzard, drop_away=blizzard, rook_lip=blizzard, rope_end=blizzard,
            fall_in=icefall, ledge_land=icefall, look_up=icefall, ice_try=icefall, pebble=icefall, rook_gulp=icefall, abseil=icefall,
            floor_dark=icefall, sunbeam=motes, climb_out=motes, exit_hole=glitter, crawl_glacier=glitter, hop_moraine=dustblow,
            bottle_drop=dustblow, camp_night=night_camp, tent_open=night_camp, bags_packed=night_camp, storm_face=blizzard, lowering=blizzard,
            rope_line=blizzard, seat_hold=blizzard, seat_crumble=blizzard, slide=blizzard, knife=blizzard, two_men=dustblow,
            rook_hatoff=dustblow, rook_turn=dawn_air, signoff=closed)
