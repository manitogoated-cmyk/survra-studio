"""Case 016, the full case file (16:9) - Joe Simpson and the cut rope. The story is filmed in 3D (world3d.py).
This file holds the flat inserts on a 1920x1080 canvas (the date card, Rook's case board on a sheet of ice, the
three-days-up card, the no-gas card, the 3,000 ft card, the lowering plan, the three-days-crawl card, the six
operations, the book, the two-climbers card), the 2D overlays drawn on top of 3D shots (storm snow, ice dust in
the crevasse, glitter on the glacier, stars over the camp, the sign-off) and the thumbnail. Every card is a
drawing made for this film; none of them reproduces a real document, photograph, map, book cover, film still or
logo. The book on the book card is a plain invented cover with only the title lettered on it."""
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
    for i in range(4):                                            # a slow band of light, so the board is never still
        x = ((t * 190 + i * 620) % (W + 800)) - 400
        cv.drawPath(poly([(x, 0), (x + 150, 0), (x - 170, H), (x - 320, H)]), P(h('CFE4FA'), a=0.05))
    cv.drawRoundRect(skia.Rect.MakeLTRB(36, 34, W - 36, H - 34), 30, 30, P(h('CFE4FA'), 14, a=0.5))
    for x, y in ((70, 68), (W - 70, 68), (70, H - 68), (W - 70, H - 68)):
        cv.drawCircle(x, y, 28, P(h('D8DCE4')))
        cv.drawCircle(x, y, 28, P(INK, 5))
        cv.drawLine(x - 14, y - 14, x + 14, y + 14, P(h('5A6070'), 8))
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


def twinkle(cv, t, n=90, top=700, seed=4):
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


WHITE = 0xFFFFFFFF


def pop(cv, lt, t0, fn, x, y):
    """Run fn at (x, y), popping in at time t0."""
    if lt < t0:
        return
    j = ease((lt - t0) / 0.14)
    cv.save()
    cv.translate(x, y)
    cv.scale(1.3 - 0.3 * j, 1.3 - 0.3 * j)
    fn()
    cv.restore()


def pop_note(cv, lt, t0, x, y, w_, h_, ang, col, lines, size=64):
    pop(cv, lt, t0, lambda: note(cv, 0, 0, w_, h_, ang, col, lines, size), x, y)


def pop_photo(cv, c, name, x, y, w_, h_, ang, focus):
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    card(cv, 0, 0, w_ + 60, h_ + 90, ang)
    cv.rotate(ang)
    photo(cv, name, 0, 18, w_, h_, focus)
    cv.restore()


def drift(cv, t, n=50, col=0x88F4F8FF, vel=(-160, 200), seed=5):
    Wd.particles(cv, W, H, t, n, col, seed, size=(3, 7), drift=vel, wobble=26)


def range_path(base=860, seed=0):
    """A drawn range of peaks across the card."""
    pts = [(-40, base)]
    x = -40
    i = 0
    while x < W + 40:
        hgt = 160 + 330 * rn(i, 40 + seed)
        w_ = 150 + 150 * rn(i, 41 + seed)
        pts += [(x + w_ * 0.5, base - hgt), (x + w_, base - 60 * rn(i, 42 + seed))]
        x += w_
        i += 1
    return pts + [(W + 40, H + 20), (-40, H + 20)]


def snowcaps(cv, pts, col):
    for i in range(1, len(pts) - 2, 2):
        x, y = pts[i]
        cv.drawPath(poly([(x, y), (x + 52, y + 96), (x + 14, y + 80), (x - 8, y + 110), (x - 44, y + 84)]), P(col))


# ------------------------------------------------------------------ flat inserts
def card_1985(cv, c):
    """The date and the place, as a card (not a map)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2C6CC8')), (0.6, h('9CC8F0')), (1, h('E8F0FA'))])
    sx = lerp(1500, 1440, c.k)
    Wd.glow(cv, sx, 250, 200, h('FFE8A0'), 0.5)
    cv.drawCircle(sx, 250, 70, P(h('FFF2C0')))
    far = range_path(700, 3)
    cv.save()
    cv.translate(-40 * c.k, 0)
    cv.drawPath(poly(far), P(h('7E9CCC')))
    snowcaps(cv, far, h('E6EEFA'))
    cv.restore()
    near = range_path(900, 0)
    cv.save()
    cv.translate(-90 * c.k, 0)
    cv.drawPath(poly(near), P(h('3A4A6E')))
    snowcaps(cv, near, WHITE)
    cv.restore()
    drift(cv, c.t, 30, 0x66FFFFFF, (120, 40))
    pop(cv, c.lt, 0.1, lambda: fit(cv, 'JUNE 1985', 0, 0, 170, 900), 620, 330)
    pop(cv, c.lt, 0.9, lambda: fit(cv, 'THE ANDES, PERU', 0, 0, 96, 900, AMBER), 620, 470)


def pin_two(cv, c):
    ice_board(cv, c.t)
    pop_photo(cv, c, 'two', 560, 440, 640, 560, -2, (0.5, 0.42))
    if c.lt > 0.15:
        cv.drawLine(920, 330, 1040, 330, P(ORANGE, 8))
    pop_note(cv, c.lt, 0.5, 1400, 215, 700, 150, 2, PAPER, ['JOE SIMPSON'], 92)
    pop_note(cv, c.lt, 1.15, 1420, 400, 700, 150, -2, PAPER, ['SIMON YATES'], 92)
    pop_note(cv, c.lt, 1.9, 1390, 600, 760, 140, 2, h('FFD866'), ['BRITISH CLIMBERS'], 78)


def face_drawn(cv, col=h('3A4A6E')):
    """The west face as a drawing: one big wall, a summit, a ridge off to the right."""
    pts = [(420, 860), (760, 330), (900, 420), (1010, 200), (1130, 380), (1260, 330), (1560, 860)]
    cv.drawPath(poly(pts), P(col))
    cv.drawPath(poly([(1010, 200), (1090, 330), (1040, 315), (1005, 370), (960, 340), (930, 380)]), P(h('E6ECF8')))
    for i in range(7):
        x = 640 + i * 110
        cv.drawLine(x, 840, x + 40 + 22 * i, 470 + 30 * abs(i - 3), P(h('5A6C98'), 9, a=0.6))
    cv.drawLine(420, 860, 1560, 860, P(h('C9D4E8'), 6))


def days3(cv, c):
    """'It takes them three days.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16305A')), (1, h('0A1020'))])
    drift(cv, c.t, 50)
    face_drawn(cv)
    n = min(3, int(c.k * 3.3) + 1)
    for i in range(3):
        on = i < n
        cx, cy = 250, 330 + i * 170
        cv.drawCircle(cx, cy, 58, P(h('FFD070') if on else h('3A4A6E')))
        if on:
            Wd.glow(cv, cx, cy, 100, h('FFD070'), 0.35)
        fit(cv, f'DAY {i + 1}', cx + 30, cy + 22, 60, 220, INK if on else h('7E8AA6'), None)
    k = min(1.0, c.k * 1.1)
    a, b = (700, 850), (1010, 215)
    m = 26
    for i in range(m):
        if i / m > k:
            break
        cv.drawCircle(lerp(a[0], b[0], i / m) + 40 * math.sin(i * 0.5), lerp(a[1], b[1], i / m), 10, P(ORANGE))
    if c.k > 0.85:
        cv.drawLine(1010, 215, 1010, 130, P(WHITE, 8))
        cv.drawPath(poly([(1010, 130), (1090, 152), (1010, 178)]), P(ORANGE))


def nogas(cv, c):
    """'No gas means no melting snow. No melting snow means nothing to drink.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1228')), (1, h('1A2450'))])
    drift(cv, c.t, 40, 0x55C8D8FF, (-80, 120))
    xs = (400, 960, 1520)
    lab = ('NO GAS', 'NO MELTED SNOW', 'NOTHING TO DRINK')
    for i, x in enumerate(xs):
        t0 = 0.1 + i * 0.6
        if c.lt < t0:
            continue
        j = ease((c.lt - t0) / 0.14)
        cv.save()
        cv.translate(x, 420)
        cv.scale(1.25 - 0.25 * j, 1.25 - 0.25 * j)
        cv.drawCircle(0, 0, 190, P(h('22335E')))
        cv.drawCircle(0, 0, 190, P(h('7FB0E0'), 8))
        if i == 0:                                                # a flame, crossed out
            cv.drawPath(poly([(0, -120), (64, -10), (50, 70), (0, 110), (-50, 70), (-64, -10)]), P(h('4A7AC8')))
            cv.drawPath(poly([(0, -40), (30, 30), (0, 80), (-30, 30)]), P(h('9CC8F0')))
            cv.drawLine(-120, -120, 120, 120, P(RED, 22))
        elif i == 1:                                              # a pan heaped with snow
            cv.drawPath(poly([(-110, -10), (-60, -90), (0, -60), (50, -110), (110, -10)]), P(WHITE))
            cv.drawRoundRect(skia.Rect.MakeXYWH(-120, -14, 240, 110), 16, 16, P(h('B8BCC8')))
            cv.drawLine(120, 10, 185, -6, P(h('3A3F4C'), 18))
        else:                                                     # an empty cup, tipped
            cv.save()
            cv.rotate(60)
            cv.drawRoundRect(skia.Rect.MakeXYWH(-70, -80, 140, 160), 14, 14, P(ORANGE))
            cv.drawRect(skia.Rect.MakeXYWH(-54, -80, 108, 30), P(h('3A1A08')))
            cv.restore()
        cv.restore()
        fit(cv, lab[i], x, 720, 62, 500, WHITE if i < 2 else AMBER)
        if i < 2 and c.lt > t0 + 0.35:
            ax = x + 280
            cv.drawLine(ax - 50, 420, ax + 30, 420, P(ORANGE, 16))
            cv.drawPath(poly([(ax + 30, 388), (ax + 80, 420), (ax + 30, 452)]), P(ORANGE))


def profile(cv):
    """The mountain from the side: the ridge, and the long way down."""
    pts = [(-40, 250), (420, 180), (520, 215), (660, 235), (900, 420), (1150, 640), (1420, 790), (1960, 840), (1960, 1100), (-40, 1100)]
    cv.drawPath(poly(pts), P(h('B8C8E4')))
    cv.drawPath(poly([(-40, 330), (500, 300), (860, 520), (1120, 720), (1400, 860), (1960, 900), (1960, 1100), (-40, 1100)]), P(h('7E96C4')))
    return pts


def drop_card(cv, c):
    """'...nearly three thousand feet of mountain still below.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E4A9A')), (1, h('9CC8F0'))])
    profile(cv)
    drift(cv, c.t, 40, 0x88FFFFFF, (200, 60))
    for i, col in enumerate((h('C8372D'), h('2F9A68'))):
        figure(cv, 560 + i * 80, 150, 0.62, col)
    k = ease(c.k * 1.5)
    a, b = (640, 240), (1440, 790)
    m = 22
    for i in range(m):
        if i / m > k:
            break
        u = i / m
        cv.drawCircle(lerp(a[0], b[0], u), lerp(a[1], b[1], u ** 0.8) + 0, 9, P(ORANGE))
    if c.lt > 0.7:
        j = ease((c.lt - 0.7) / 0.15)
        cv.save()
        cv.translate(1400, 330)
        cv.scale(1.3 - 0.3 * j, 1.3 - 0.3 * j)
        fit(cv, 'NEARLY', 0, -110, 76, 700)
        fit(cv, '3,000 FT', 0, 40, 170, 760, AMBER)
        fit(cv, 'STILL TO GO DOWN', 0, 140, 66, 700)
        cv.restore()


def plan_card(cv, c):
    """The lowering: a seat at the top, 300 feet of rope, a man sliding on the end of it."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2A4A')), (0.6, h('A8684A')), (1, h('2A2440'))])
    cv.drawPath(poly([(-40, 190), (300, 230), (1960, 900), (1960, 1100), (-40, 1100)]), P(h('B8C8E4')))
    cv.drawPath(poly([(-40, 330), (1960, 1010), (1960, 1100), (-40, 1100)]), P(h('7E96C4')))
    drift(cv, c.t, 40, 0x88FFE8D8, (-300, 120))
    sx, sy = 420, 235
    u = 0.25 + 0.75 * ease(c.k * 1.3)
    jx, jy = lerp(sx, 1480, u), lerp(sy + 40, 700, u)
    cv.drawLine(sx + 50, sy + 20, jx - 40, jy - 30, P(ORANGE, 12))
    cv.drawCircle(lerp(sx, jx, 0.5), lerp(sy, jy, 0.5) - 6, 17, P(h('4AA8E0')))             # the knot
    figure(cv, sx, sy, 1.0, h('2F9A68'), sit=True)
    cv.save()
    cv.translate(jx, jy)
    cv.rotate(22)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-70, -26, 140, 52), 20, 20, P(h('C8372D')))
    cv.drawCircle(-92, -6, 26, P(h('E0B090')))
    cv.restore()
    for i in range(5):
        cv.drawCircle(jx + 70 + 22 * i, jy + 40 + 6 * i - 20 * abs(math.sin(c.t * 9 + i)), 7, P(WHITE, a=0.8))
    if c.lt > 0.5:
        j = ease((c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1330, 250)
        cv.scale(1.3 - 0.3 * j, 1.3 - 0.3 * j)
        fit(cv, '300 FT', 0, 0, 170, 760, AMBER)
        fit(cv, 'OF ROPE, THEN AGAIN', 0, 100, 60, 760)
        cv.restore()


def days_card(cv, c):
    """'For three days.' The sun and the moon go over three times; a dotted track creeps along."""
    turns = 3.0
    day = 0.5 + 0.5 * math.cos(c.k * 2 * math.pi * turns)
    top = Wd.mix(h('0A1230'), h('4E94E0'), day)
    Wd.vgrad(cv, 0, 0, W, H, [(0, top), (0.62, Wd.mix(h('1A2450'), h('BFE0FF'), day)), (1, h('1A2440'))])
    if day < 0.5:
        twinkle(cv, c.t, 70, 520, 9)
    a = c.k * 2 * math.pi * turns
    cx, cy, r = 960, 900, 720
    sx, sy = cx - r * math.sin(a), cy - r * math.cos(a)
    Wd.glow(cv, sx, sy, 140, h('FFD070'), 0.5)
    cv.drawCircle(sx, sy, 76, P(h('FFD070')))
    mx, my = cx + r * math.sin(a), cy + r * math.cos(a)
    cv.drawCircle(mx, my, 56, P(h('E8EEF8')))
    cv.drawCircle(mx + 24, my - 12, 50, P(top))
    snow = Wd.mix(h('5A6C98'), h('F4F8FF'), day)
    cv.drawPath(poly([(-40, 700), (380, 420), (560, 520), (900, 300), (1100, 470), (1400, 390), (1960, 680), (1960, 1100), (-40, 1100)]), P(Wd.mix(h('1E2A4E'), h('7E8AA6'), day)))
    cv.drawPath(poly([(900, 300), (990, 400), (930, 420), (880, 390), (820, 440), (800, 400)]), P(snow))
    cv.drawPath(poly([(-40, 760), (500, 700), (1100, 740), (1960, 690), (1960, 1100), (-40, 1100)]), P(snow))
    cv.drawPath(poly([(900, 760), (1400, 760), (1960, 740), (1960, 1100), (700, 1100)]), P(Wd.mix(h('2A2C3A'), h('8A847C'), day)))
    n = 26
    for i in range(n):
        if i / n > c.k * 1.12:
            break
        cv.drawCircle(260 + i * 56, 790 + 10 * math.sin(i * 0.8), 11, P(ORANGE))
    fit(cv, 'THREE DAYS', 520, 230, 150, 900)
    d = min(3, int(c.k * turns) + 1)
    fit(cv, f'DAY {d}', 1560, 230, 96, 400, AMBER)


def six_card(cv, c):
    """'His leg needs six operations.' A drawn leg in plaster and six ticks."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2C5C96')), (1, h('0E2244'))])
    drift(cv, c.t, 30, 0x55FFFFFF, (60, 40))
    cv.save()
    cv.translate(470, 470)
    cv.rotate(-12)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-330, -60, 660, 120), 56, 56, P(h('F4F2EA')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-330, -60, 660, 120), 56, 56, P(INK, 7))
    cv.drawRoundRect(skia.Rect.MakeXYWH(250, -150, 110, 210), 40, 40, P(h('F4F2EA')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(250, -150, 110, 210), 40, 40, P(INK, 7))
    for i in range(6):
        cv.drawLine(-260 + i * 90, -52, -240 + i * 90, 52, P(h('C9CCC0'), 8))
    cv.restore()
    cv.drawLine(700, 250, 760, 60, P(h('D8DCE4'), 8))                       # the sling
    n = 0
    for i in range(6):
        t0 = (0.15 + 0.75 * i / 6) * (c.d or 2.2)
        if c.lt >= t0:
            n += 1
            tick(cv, 1010 + (i % 3) * 250, 300 + (i // 3) * 210, 1.3, ease((c.lt - t0) / 0.1))
    if n:
        fit(cv, 'SIX OPERATIONS' if n == 6 else f'{n}', 1260, 760, 110, 900, AMBER if n == 6 else WHITE)


def pin_blame(cv, c):
    ice_board(cv, c.t)
    pop_photo(cv, c, 'simon', 540, 440, 560, 580, -3, (0.5, 0.35))
    if c.lt > 0.15:
        cv.drawLine(860, 330, 1010, 330, P(ORANGE, 8))
    pop_note(cv, c.lt, 0.4, 1380, 230, 760, 160, 2, PAPER, ['SIMON YATES'], 92)
    pop_note(cv, c.lt, 1.0, 1400, 440, 800, 170, -2, h('FFD866'), ['HE CUT THE ROPE'], 86)
    pop_note(cv, c.lt, 1.6, 1380, 650, 860, 150, 2, PAPER, ['SOME CLIMBERS BLAMED HIM'], 62)


def pin_same(cv, c):
    """'He says he would have done exactly the same.' A note in Rook's words, not a quotation."""
    ice_board(cv, c.t)
    pop_photo(cv, c, 'men', 540, 440, 640, 560, -3, (0.5, 0.5))
    if c.lt > 0.12:
        cv.drawLine(900, 330, 1010, 330, P(ORANGE, 8))
    pop_note(cv, c.lt, 0.15, 1390, 300, 880, 180, 3, h('FFD866'), ["HE'D HAVE DONE THE SAME"], 70)
    for i, s_ in enumerate(('JOE SIMPSON', 'ON SIMON YATES')):
        if c.lt > 0.5 + i * 0.3:
            fit(cv, s_, 1390, 520 + i * 100, 78, 800, WHITE if i == 0 else AMBER, None)
    if c.lt > 1.2:
        stamp(cv, 'TRUE', 1560, 720, -10, min(1, (c.lt - 1.2) / 0.12), 120, GREEN)


def book_card(cv, c):
    """The book: a plain invented cover with only its title on it. Not the real cover."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16305A')), (1, h('0A1020'))])
    drift(cv, c.t, 40)
    cv.drawRect(skia.Rect.MakeXYWH(0, 800, W, 280), P(h('2C5C96')))
    cv.drawLine(0, 800, W, 800, P(h('7FB0E0'), 10))
    k = ease(c.lt / 0.2)
    cv.save()
    cv.translate(620, 800)
    cv.rotate(-4 * k)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    cv.drawRect(skia.Rect.MakeXYWH(-232, -640, 34, 640), P(h('C9CCC0')))
    cv.drawRect(skia.Rect.MakeXYWH(-200, -640, 440, 640), P(h('22335E')))
    cv.drawRect(skia.Rect.MakeXYWH(-200, -640, 440, 640), P(INK, 8))
    cv.drawLine(-140, -150, 180, -520, P(ORANGE, 10))                         # one orange line: a rope
    cv.drawRect(skia.Rect.MakeXYWH(-160, -600, 360, 8), P(h('7FB0E0')))
    cv.drawRect(skia.Rect.MakeXYWH(-160, -60, 360, 8), P(h('7FB0E0')))
    for i, s_ in enumerate(('TOUCHING', 'THE', 'VOID')):
        fit(cv, s_, 20, -420 + i * 110, 84, 380, WHITE, None)
    cv.restore()
    pop(cv, c.lt, 0.5, lambda: fit(cv, 'TOUCHING THE VOID', 0, 0, 96, 900, AMBER), 1340, 300)
    pop(cv, c.lt, 1.0, lambda: fit(cv, 'BY JOE SIMPSON', 0, 0, 70, 900), 1340, 420)
    pop(cv, c.lt, 1.4, lambda: fit(cv, '1988', 0, 0, 150, 600), 1340, 620)


def cliff(cv, cut_k=0.0):
    """The drawn cliff: a slope, a lip, an overhang, and the two of them on one rope."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B1C')), (0.7, h('1A2450')), (1, h('0C1228'))])
    cv.drawPath(poly([(1960, 60), (860, 380), (940, 1100), (1960, 1100)]), P(h('B8C8E4')))
    cv.drawPath(poly([(860, 380), (940, 1100), (1960, 1100), (1960, 520), (1010, 480)]), P(h('3F6FAE')))
    cv.drawPath(poly([(860, 380), (1010, 480), (1960, 520), (1960, 440)]), P(h('7FB0E0')))
    sx, sy = 1400, 190
    jx, jy = 820, 760
    mx, my = lerp(sx, 860, 0.55), lerp(sy + 30, 380, 0.55)
    if cut_k <= 0:
        cv.drawPath(poly([(sx - 40, sy + 30), (860, 376), (jx, jy - 120)], False), P(ORANGE, 12))
    else:
        cv.drawLine(sx - 40, sy + 30, mx + 20, my - 8, P(ORANGE, 12))
        d = 40 * cut_k
        cv.drawPath(poly([(mx - 20 - d, my + 8 + d), (860, 376 + d), (jx, jy - 120)], False), P(ORANGE, 12))
        for i in range(6):
            a = i * 1.05
            cv.drawLine(mx + 16 * math.cos(a), my + 16 * math.sin(a), mx + (40 + 30 * cut_k) * math.cos(a), my + (40 + 30 * cut_k) * math.sin(a),
                        P(WHITE, 7, a=1 - 0.6 * cut_k))
    figure(cv, sx, sy, 1.25, h('2F9A68'), sit=True)
    figure(cv, jx, jy, 1.25, h('C8372D'), hang=True)
    return (sx, sy), (jx, jy)


def both_card(cv, c):
    """'Cutting the rope is what saved them both.' (what both men have said)"""
    k = ease((c.lt - 0.3) / 0.2)
    (sx, sy), (jx, jy) = cliff(cv, k)
    Wd.particles(cv, W, H, c.t, 50, 0x88F4F8FF, 5, size=(3, 7), drift=(-260, 200), wobble=26)
    tick(cv, jx - 190, jy - 30, 1.3, ease((c.lt - 0.9) / 0.12))
    tick(cv, sx + 230, sy - 20, 1.3, ease((c.lt - 1.5) / 0.12))
    if c.lt > 1.5:
        fit(cv, 'BOTH LIVED', 380, 260, 120, 660, AMBER)


SHOTS = {f.__name__: f for f in (card_1985, pin_two, days3, nogas, drop_card, plan_card, days_card, six_card, pin_blame, pin_same, book_card, both_card)}


# ------------------------------------------------------------------ overlays on 3D shots
def blizzard(cv, c):
    """Snow driven flat across the cliff."""
    Wd.particles(cv, W, H, c.t, 90, 0xCCF4F8FF, 7, size=(3, 8), drift=(-1300, 220), wobble=30)
    for j in range(9):
        ph = rn(j, 3)
        x = W + 450 - ((c.t * 2400 * (0.6 + ph)) + ph * 4000) % (W + 900)
        y = (ph * 7919) % H + 80 * math.sin(c.t * 2 + j)
        cv.drawLine(x, y, x - 360, y + 60, P(WHITE, 8 + 6 * ph, a=0.13))


def dusk_snow(cv, c):
    Wd.particles(cv, W, H, c.t, 70, 0xAAFFD8C0, 13, size=(3, 7), drift=(-600, 100), wobble=30)


def icefall(cv, c):
    """Ice dust sifting down inside the crevasse."""
    Wd.particles(cv, W, H, c.t, 60, 0xAACFE4FA, 13, size=(2, 6), drift=(20, 300), wobble=22, twinkle=True)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 44, 0xAAFFF0D0, 29, size=(2, 6), drift=(30, 80), wobble=30, twinkle=True)


def glitter(cv, c):
    Wd.particles(cv, W, H, c.t, 54, 0xEEFFFFFF, 11, size=(3, 7), drift=(180, -60), wobble=30, twinkle=True)


def blown(cv, c):
    """Fine snow blown off the ridge."""
    Wd.particles(cv, W, H, c.t, 80, 0xCCF4F8FF, 7, size=(3, 7), drift=(900, 110), wobble=30)


def dustblow(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x66FFF0D8, 31, size=(2, 6), drift=(280, 30), wobble=30)


def night_camp(cv, c):
    twinkle(cv, c.t, 60, 330, 23)
    Wd.particles(cv, W, H, c.t, 20, 0x66FFD8A0, 17, size=(2, 5), drift=(40, -60), wobble=30, twinkle=True)


def breath(cv, c):
    """Cold air in the snow hole."""
    Wd.particles(cv, W, H, c.t, 30, 0x55DCE8FF, 37, size=(3, 8), drift=(30, -70), wobble=40, twinkle=True)


def dawn_air(cv, c):
    Wd.particles(cv, W, H, c.t, 50, 0xCCFFE8D0, 19, size=(3, 7), drift=(170, 80), wobble=30, twinkle=True)


def closed(cv, c):
    dawn_air(cv, c)
    if c.lt > 0.6:
        k = min(1, (c.lt - 0.6) / 0.15)
        cv.save()
        cv.translate(1400, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 016  CLOSED', 0, 90, 54, WHITE, 0xFF000000)
        cv.restore()


OVER = dict(signoff=closed)
for _fn, _kinds in (
        (blizzard, 'grip leg_hang hang_wide slack drop_away rook_lip rope_end rook_go storm_face lowering rope_line seat_hold seat_crumble slide knife '
                   'lower_far rook_watch over_edge hands_slip pack_knife yates_after'),
        (dusk_snow, 'knot seat_dig lower_side ridge_down'),
        (icefall, 'fall_in ledge_land look_up ice_try pebble rook_gulp abseil floor_dark alive rope_dark'),
        (motes, 'sunbeam climb_out hosp_bed hosp_close desk_write'),
        (glitter, 'exit_hole crawl_glacier glac_far walk_alone look_face two_look face_wide face_climb'),
        (blown, 'summit ice_step step_fall leg_sit yates_sees ridge_two'),
        (dustblow, 'hop_moraine bottle_drop two_men rook_hatoff hawking_wave rook_coin mule yates_sit crag_climb'),
        (night_camp, 'camp_night tent_open bags_packed night_rocks embrace'),
        (breath, 'bivi_stove stove_out rook_can snowhole'),
        (dawn_air, 'rook_turn rook_think seat_dawn dawn_descend crev_look')):
    for _k in _kinds.split():
        OVER[_k] = _fn


def THUMB(cv, c):
    """1280x720: the 3D still (he hangs on the rope under the lip in the storm; Rook looks down from above) and a four-word hook on the left."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0E1C34'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(640, 0), (0, 0)], [0x00000000, 0xE6000000])))
    Wd.text_card(cv, 'HE CUT', 300, 250, 150, WHITE, 0xFF000000)
    Wd.text_card(cv, 'THE ROPE', 300, 420, 132, RED, 0xFF000000)
    Wd.text_card(cv, 'BOTH LIVED', 300, 570, 88, AMBER, 0xFF000000)
