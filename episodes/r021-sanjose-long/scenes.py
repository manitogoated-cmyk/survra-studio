"""Case 021, the full case file (16:9) - the San Jose mine, Chile, 2010. The story is filmed in 3D (world3d.py).
This file holds the flat inserts on a 1920x1080 canvas (the note in red ink, Rook's case file, cross-sections of
the trap, the depth, the seven holes that missed and the three drills, the ration calendar, the borehole against
a man's shoulders, the shaft against a bicycle wheel, the thirty-three ticked off, the line of 69 days, Rook's
case board), the 2D overlays drawn on top of 3D shots, and the thumbnail. Every card is a drawing made for this
film; none reproduces a real document, photograph, map or logo. The note card gives an English translation of
the note's wording in a drawn hand: it is not a facsimile of the real note. The cross-sections are diagrams, not
surveys, and are not to scale. Captions run in a band around 86% of the height and the label sits top right, so
the cards keep both clear."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F4EEDC'), h('D8261E'), h('3EC46A')
ORE, ORED, SAND, SKY = h('6A5244'), h('2E221C'), h('B4875A'), h('10183A')
GROUND = 190                      # the desert surface in the cross-sections
ROOM = (1270, 760)                # the shelter in the cross-sections


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 91.17 + j * 47.33) * 24634.6345) % 1


def font(size, italic=False):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kItalic_Slant if italic else skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def left(cv, s, x, y, size, color=0xFFFFFFFF, stroke=0xFF000000):
    return Wd.text_card(cv, s, x, y, size, color, stroke, center=False)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('5A4A3E')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def plate(cv, seed=1, glow=0.0):
    """A sheet of scuffed steel plate bolted to rock: Rook's board for this case."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('4A4038')), (0.5, h('32292A')), (1, h('181414'))])
    cv.drawRect(skia.Rect.MakeXYWH(70, 50, 1780, 980), P(h('5E646E')))
    cv.drawRect(skia.Rect.MakeXYWH(70, 50, 1780, 980), P(h('22262E'), 10))
    for i in range(30):
        x, y = 100 + rn(i, seed) * 1700, 80 + rn(i, seed + 1) * 900
        L = 60 + 260 * rn(i, seed + 2)
        cv.drawLine(x, y, x + L, y + L * (rn(i, seed + 3) - 0.5), P(h('8A909C') if i % 2 else h('3A3F4A'), 3 + 5 * rn(i, seed + 4), a=0.35))
    for (x, y) in ((112, 92), (1808, 92), (112, 988), (1808, 988)):
        cv.drawCircle(x, y, 20, P(h('2A2E38')))
        cv.drawCircle(x - 4, y - 4, 8, P(h('9AA0AC')))
    if glow:
        Wd.glow(cv, 960, 480, 900, h('FFC890'), 0.2 * glow)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x77000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.restore()


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


def tick(cv, x, y, s, k, col=GREEN):
    if k <= 0:
        return
    a, b, c_ = (x - 22 * s, y), (x - 6 * s, y + 18 * s), (x + 26 * s, y - 24 * s)
    k1, k2 = min(1, k * 2), max(0, k * 2 - 1)
    cv.drawLine(a[0], a[1], lerp(a[0], b[0], k1), lerp(a[1], b[1], k1), P(col, 12 * s))
    if k2 > 0:
        cv.drawLine(b[0], b[1], lerp(b[0], c_[0], k2), lerp(b[1], c_[1], k2), P(col, 12 * s))


def helmet(cv, x, y, s, col):
    cv.drawArc(skia.Rect.MakeXYWH(x - 46 * s, y - 46 * s, 92 * s, 92 * s), 180, 180, True, P(col))
    cv.drawRoundRect(skia.Rect.MakeXYWH(x - 58 * s, y - 6 * s, 116 * s, 16 * s), 8, 8, P(col))
    cv.drawRect(skia.Rect.MakeXYWH(x - 12 * s, y - 40 * s, 24 * s, 20 * s), P(h('FFF2C0')))


def line2(cv, a, b, col, w_=8):
    cv.drawLine(a[0], a[1], b[0], b[1], P(0xFF000000, w_ + 6))
    cv.drawLine(a[0], a[1], b[0], b[1], P(col, w_))


# ---------------------------------------------------------------- inserts
NOTE = ('WE ARE FINE', 'IN THE SHELTER,', 'THE 33 OF US')


def note_card(cv, c):
    """The note, held to the light: red ink on a creased sheet. English translation, written out line by line."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1230')), (0.6, h('1C1A2C')), (1, h('0A0A14'))])
    Wd.glow(cv, 960, 420, 1100, h('FFE2B0'), 0.3)
    k = min(1, c.lt / 0.14)
    s = 0.8 + 0.2 * (1 - (1 - k) ** 3) + 0.02 * c.k
    cv.save()
    cv.translate(960, 410)
    cv.scale(s, s)
    cv.rotate(-2.5 + 0.8 * math.sin(c.t * 2.2))
    cv.drawRect(skia.Rect.MakeXYWH(-520 + 14, -300 + 18, 1040, 600), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-520, -300, 1040, 600), P(PAPER))
    for x in (-173, 173):
        cv.drawLine(x, -300, x, 300, P(h('CFC6AE'), 4))
    cv.drawLine(-520, 0, 520, 0, P(h('DAD2BC'), 3))
    for i in range(7):
        cv.drawCircle(-440 + 880 * rn(i, 3), -250 + 500 * rn(i, 4), 16 + 30 * rn(i, 5), P(h('B4875A'), a=0.16))
    shown = c.lt / 0.3
    for i, line in enumerate(NOTE):
        if shown < i:
            break
        n = max(1, int(len(line) * min(1.0, shown - i)))
        f = font(104, True)
        tw = f.measureText(line)
        cv.drawString(line[:n], -tw / 2, -140 + 150 * i + 30, f, P(RED))
    cv.restore()
    left(cv, '22 AUGUST 2010', 90, 110, 56, AMBER)
    fit(cv, 'RED INK. TRANSLATED.', 960, 800, 40, 800, 0xCCFFFFFF, None)
    Wd.particles(cv, W, H, c.t, 30, 0x66FFE8C0, 61, size=(2, 5), drift=(50, -40), wobble=24, twinkle=True)


FILE = ('5 AUGUST 2010', 'SAN JOSÉ MINE', 'ATACAMA DESERT, CHILE', 'COPPER AND GOLD')


def file_card(cv, c):
    """Rook's case file for the day it began: four lines on the steel plate, typed in one after another."""
    plate(cv, 9, 0.6)
    cv.save()
    cv.translate(960, 540)
    cv.scale(1 + 0.03 * c.k, 1 + 0.03 * c.k)
    cv.translate(-960, -540)
    card(cv, 400, 400, 420, 520, -3)
    cv.save()
    cv.translate(400, 400)
    cv.rotate(-3)
    helmet(cv, 0, 20, 2.4, h('E0B020'))
    cv.drawLine(-150, 110, 150, 110, P(h('8A909C'), 10))
    fit(cv, 'CASE 021', 0, 200, 64, 360, h('2A2E38'), None)
    cv.restore()
    left(cv, 'CASE FILE', 720, 190, 54, 0xCCFFFFFF)
    shown = c.lt / 0.55
    for i, line in enumerate(FILE):
        if shown < i:
            break
        n = max(1, int(len(line) * min(1.0, (shown - i) * 1.6)))
        left(cv, line[:n], 720, 310 + 128 * i, 92 if i < 2 else 78, AMBER if i == 0 else 0xFFFFFFFF)
    cv.restore()
    for x in (250, 550):
        cv.drawCircle(x, 150, 20, P(ORANGE))
        cv.drawCircle(x, 150, 20, P(INK, 5))


def section(cv, t, lit=True):
    """A drawn cross-section: night sky, desert, the rock, and one small room far below."""
    Wd.vgrad(cv, 0, 0, W, GROUND, [(0, h('0A1030')), (1, h('2A2A5A'))])
    for i in range(24):
        cv.drawCircle(40 + 1840 * rn(i, 7), 14 + 130 * rn(i, 8), 2 + 2 * rn(i, 9), P(0xFFFFFFFF, a=0.5 + 0.4 * math.sin(t * 3 + i)))
    cv.drawPath(poly([(-20, GROUND), (300, GROUND - 26), (760, GROUND - 6), (1200, GROUND - 30), (1640, GROUND - 8), (1940, GROUND - 20), (1940, GROUND + 60), (-20, GROUND + 60)]), P(SAND))
    Wd.vgrad(cv, 0, GROUND + 30, W, H, [(0, h('7A5E4C')), (0.4, h('5A463A')), (1, h('2A201C'))])
    for i in range(30):
        x, y = rn(i, 11) * W, GROUND + 60 + rn(i, 12) * 820
        s = 70 + 170 * rn(i, 13)
        dx = 14 * math.sin(t * 0.5 + i)
        cv.drawPath(poly([(x + dx, y), (x + s + dx, y + 0.2 * s), (x + 0.7 * s + dx, y + 0.6 * s), (x - 0.3 * s + dx, y + 0.4 * s)]), P(h('8C7260') if i % 2 else h('1E1614'), a=0.22))
    rx, ry = ROOM
    cv.drawRoundRect(skia.Rect.MakeXYWH(rx - 150, ry - 50, 300, 100), 18, 18, P(0xFF0A0706))
    cv.drawRoundRect(skia.Rect.MakeXYWH(rx - 150, ry - 50, 300, 100), 18, 18, P(h('FFC890'), 5, a=0.6 + 0.2 * math.sin(t * 4)))
    if lit:
        for i in range(33):
            cv.drawCircle(rx - 128 + 16 * (i % 17), ry - 14 + 30 * (i // 17), 6, P(AMBER))
    return rx, ry


def derrick(cv, x, y, s=1.0, col='C8CCD4'):
    for sx in (-1, 1):
        cv.drawLine(x + sx * 40 * s, y, x + sx * 10 * s, y - 150 * s, P(h(col), 8 * s))
    for i in range(3):
        yy = y - 30 * s - i * 40 * s
        ww = 40 * s - (y - yy) / (150 * s) * 30 * s
        cv.drawLine(x - ww, yy, x + ww, yy - 18 * s, P(h(col), 4 * s))
    cv.drawRect(skia.Rect.MakeXYWH(x - 18 * s, y - 164 * s, 36 * s, 16 * s), P(AMBER))


def note_scale(cv):
    fit(cv, 'DIAGRAM, NOT TO SCALE', 300, 1040, 30, 500, 0x99FFFFFF, None)


RAMP = [(420, GROUND), (760, 300), (480, 400), (820, 500), (540, 600), (900, 700), (1120, 760)]


def trap_card(cv, c):
    """The trap: the road down to the shelter is cut by one block; the ventilation shaft beside it has a ladder that stops."""
    rx, ry = section(cv, c.t)
    for a, b in zip(RAMP, RAMP[1:]):
        cv.drawLine(a[0], a[1], b[0], b[1], P(0xFF0A0706, 30))
    k = ease(c.lt / 0.5)
    bx, by = lerp(480, 650, 0.5), lerp(400, 450, 0.5)
    cv.save()
    cv.translate(bx, by - 260 * (1 - k))
    cv.rotate(16)
    cv.drawRect(skia.Rect.MakeXYWH(-70, -46, 140, 92), P(h('8E877C')))
    cv.drawRect(skia.Rect.MakeXYWH(-70, -46, 140, 92), P(RED, 8))
    cv.restore()
    if c.lt > 0.5:
        left(cv, 'THE ROAD: BLOCKED', 110, 470, 54, RED)
    # the ventilation shaft
    vx = 1040
    cv.drawLine(vx, GROUND, vx, 690, P(0xFF0A0706, 34))
    cv.drawLine(vx, 690, 1010, 730, P(0xFF0A0706, 30))
    k2 = ease((c.lt - 0.9) / 0.9)
    top = lerp(690, 500, k2)
    if c.lt > 0.9:
        for sx in (-9, 9):
            cv.drawLine(vx + sx, 690, vx + sx, top, P(AMBER, 4))
        y = 680
        while y > top:
            cv.drawLine(vx - 9, y, vx + 9, y, P(AMBER, 4))
            y -= 16
    if k2 >= 1:
        for sgn in (-1, 1):
            cv.drawLine(vx - 26, 480 - 22 * sgn, vx + 26, 480 + 22 * sgn, P(RED, 10))
        left(cv, 'THE LADDER STOPS', 1110, 420, 54, RED)
    note_scale(cv)


def depth_card(cv, c):
    """'...seven hundred metres under the desert.' The derrick on top, the shelter far below, and the measure between them."""
    rx, ry = section(cv, c.t)
    derrick(cv, 900, GROUND - 4)
    k = ease(c.k * 1.5)
    y1 = lerp(GROUND, ry, k)
    line2(cv, (700, GROUND), (700, y1), AMBER, 8)
    for i in range(8):
        yy = GROUND + (ry - GROUND) * i / 7
        if yy <= y1 + 1:
            cv.drawLine(676, yy, 724, yy, P(AMBER, 6))
    if k > 0.95:
        cv.drawLine(700, ry, rx - 160, ry, P(AMBER, 6))
    n = int(round(700 * k / 10) * 10)
    fit(cv, f'{n} M', 360, 560, 210, 560, AMBER)
    left(cv, 'THE SHELTER', rx - 150, ry - 80, 40, 0xFFFFFFFF)
    note_scale(cv)


MISS = [(-330, 0.80), (-250, 0.98), (-190, 0.64), (220, 0.92), (300, 0.72), (380, 1.02), (-420, 1.06)]


def miss_card(cv, c):
    """'Seven holes.' Seven lines go down past the room, one after another, each ending in a red cross."""
    rx, ry = section(cv, c.t)
    derrick(cv, 960, GROUND - 4, 0.9)
    n = c.k * 8.2
    for i, (dx, f) in enumerate(MISS):
        k = max(0.0, min(1.0, n - i))
        if k <= 0:
            continue
        x1, y1 = rx + dx, GROUND + (ry + 70 - GROUND) * f
        x, y = lerp(960, x1, k), lerp(GROUND, y1, k)
        line2(cv, (960, GROUND), (x, y), h('C8CCD4'), 6)
        if k >= 1:
            for sgn in (-1, 1):
                cv.drawLine(x1 - 20, y1 - 20 * sgn, x1 + 20, y1 + 20 * sgn, P(RED, 9))
    if n >= 1:
        fit(cv, f'{min(7, int(n))} MISSED', 400, 560, 150, 620, 0xFFFFFFFF)
    note_scale(cv)


def plans_card(cv, c):
    """Three drills race down towards the room: A, B and C, each from its own rig."""
    rx, ry = section(cv, c.t)
    for i, (x0, name, col, speed) in enumerate(((560, 'A', 'C8CCD4', 0.62), (960, 'B', 'FFB000', 1.0), (1500, 'C', 'D8261E', 0.5))):
        derrick(cv, x0, GROUND - 4, 0.8, col)
        k = min(1.0, ease(c.k * 1.15) * speed)
        tx, ty = rx - 60 + 60 * i, ry - 56
        x, y = lerp(x0, tx, k), lerp(GROUND, ty, k)
        line2(cv, (x0, GROUND), (x, y), h(col), 10)
        cv.drawCircle(x, y, 13 + 3 * math.sin(c.t * 20 + i), P(h(col)))
        fit(cv, 'PLAN ' + name, x0, GROUND + 78, 46, 300, h(col))
    left(cv, 'THREE DRILLS', 110, 640, 76, 0xFFFFFFFF)
    left(cv, 'ONE TARGET', 110, 730, 76, AMBER)
    note_scale(cv)


def shaft_card(cv, c):
    """Plan B's shaft: more than six hundred metres long, and about as wide as a bicycle wheel."""
    rx, ry = section(cv, c.t)
    derrick(cv, 1210, GROUND - 4, 0.9, 'FFB000')
    k = ease(c.lt / 0.8)
    y1 = lerp(GROUND, ry - 50, k)
    cv.drawLine(1210, GROUND, 1210, y1, P(0xFF000000, 22))
    cv.drawLine(1210, GROUND, 1210, y1, P(AMBER, 10))
    fit(cv, f'{int(round(620 * k / 10) * 10)} M +', 1500, 470, 110, 420, AMBER)
    # the wheel
    wx, wy, r = 470, 520, 190
    cv.drawCircle(wx, wy, r + 22, P(0xFF0A0706))
    cv.drawCircle(wx, wy, r, P(h('1E1614')))
    cv.drawCircle(wx, wy, r - 12, P(h('C8CCD4'), 16))
    cv.drawCircle(wx, wy, r + 10, P(AMBER, 6))
    a0 = c.t * 1.4
    for i in range(12):
        a = a0 + i * math.pi / 6
        cv.drawLine(wx, wy, wx + (r - 14) * math.cos(a), wy + (r - 14) * math.sin(a), P(h('9AA0AC'), 4))
    cv.drawCircle(wx, wy, 18, P(h('9AA0AC')))
    if c.lt > 0.9:
        fit(cv, 'THE SHAFT: ABOUT AS WIDE', 470, 800, 44, 760, 0xFFFFFFFF)
        fit(cv, 'AS A BICYCLE WHEEL', 470, 856, 44, 760, AMBER)
    note_scale(cv)


def cal_card(cv, c):
    """'...every other day.' A row of days: a spoon on one, nothing on the next."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A201C')), (0.5, h('3E2F28')), (1, h('14100E'))])
    Wd.glow(cv, 960, 480, 1000, h('FFC890'), 0.2)
    fit(cv, 'EVERY OTHER DAY', 960, 190, 110, 1300, AMBER)
    n = c.k * 16
    for i in range(14):
        col, row = i % 7, i // 7
        x, y = 330 + 210 * col, 400 + 210 * row + 6 * math.sin(c.t * 2 + i)
        on = i < n
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 90, y - 80, 180, 160), 18, 18, P(PAPER, a=1.0 if on else 0.25))
        if not on:
            continue
        if i % 2 == 0:
            cv.drawLine(x - 10, y + 10, x + 62, y - 46, P(h('8A909C'), 12))
            cv.drawOval(skia.Rect.MakeXYWH(x - 62, y - 8, 70, 46), P(h('8A909C')))
            cv.drawOval(skia.Rect.MakeXYWH(x - 52, y - 4, 50, 30), P(h('E0A088')))
        else:
            cv.drawLine(x - 40, y, x + 40, y, P(h('B8AE98'), 10))
    fit(cv, '2 SPOONFULS OF TUNA', 960, 800, 60, 1200, 0xFFFFFFFF)


def hole_card(cv, c):
    """'That hole fits a note. It does not fit a man.' The borehole and a man's shoulders, drawn to one scale."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2C22')), (0.5, h('5A463A')), (1, h('1E1614'))])
    Wd.glow(cv, 960, 460, 1000, h('FFC890'), 0.18)
    k1 = ease(c.lt / 0.3)
    hx, hy = 560, 470
    r = 52 * k1 * (1 + 0.04 * math.sin(c.t * 5))
    cv.drawCircle(hx, hy, r + 16, P(h('C8CCD4')))
    cv.drawCircle(hx, hy, r, P(0xFF050505))
    fit(cv, 'THE BOREHOLE', hx, 700, 60, 600, 0xFFFFFFFF)
    k2 = ease((c.lt - 0.6) / 0.35)
    if k2 > 0:
        mx, my = 1300, 470
        cv.save()
        cv.translate(mx, my)
        cv.scale(0.6 + 0.4 * k2, 0.6 + 0.4 * k2)
        cv.drawOval(skia.Rect.MakeXYWH(-175, -70, 350, 140), P(h('7A5230')))
        cv.drawOval(skia.Rect.MakeXYWH(-175, -70, 350, 140), P(INK, 6))
        cv.drawCircle(0, -6, 62, P(h('E0B020')))
        cv.drawCircle(0, -6, 62, P(INK, 6))
        cv.drawRect(skia.Rect.MakeXYWH(-16, -72, 32, 22), P(h('FFF2C0')))
        cv.restore()
        fit(cv, 'A MAN, FROM ABOVE', mx, 700, 60, 600, AMBER)
    if c.lt > 1.2:
        fit(cv, 'DRAWN TO THE SAME SCALE', 960, 180, 54, 1200, 0xCCFFFFFF)


HELMC = ('E0B020', 'C8372D', 'E07A1E')


def count33(cv, c):
    """'...thirty-three out of thirty-three.' Thirty-three helmets, ticked off one by one."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10183A')), (0.6, h('2A2A5A')), (1, h('0C1024'))])
    Wd.glow(cv, 960, 460, 1000, h('FFC890'), 0.22)
    left(cv, '13 OCTOBER 2010', 90, 110, 56, 0xFFFFFFFF)
    n = c.k * 44
    for i in range(33):
        col, row = i % 11, i // 11
        x = 960 + (col - 5) * 150
        y = 300 + row * 150
        helmet(cv, x, y, 0.86, h('F2F2EC') if i == 32 else h(HELMC[i % 3]))
        tick(cv, x + 34, y + 28, 0.95, min(1.0, max(0.0, n - i)))
    if c.k > 0.78:
        fit(cv, '33 OF 33', 660, 790, 120, 700, GREEN)
    if c.k > 0.88:
        fit(cv, '69 DAYS', 1330, 790, 120, 600, AMBER)


DAYS = ((0, '5 AUGUST', 'THE COLLAPSE'), (17, '22 AUGUST', 'THE NOTE'), (65, '9 OCTOBER', 'THE SHAFT'), (69, '13 OCTOBER', 'ALL OUT'))


def timeline_card(cv, c):
    """One line of sixty-nine days, with the four dates on it."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10183A')), (0.6, h('1C1A2C')), (1, h('0A0A14'))])
    Wd.glow(cv, 960, 480, 1000, h('FFC890'), 0.16)
    fit(cv, '69 DAYS', 960, 190, 130, 1000, AMBER)
    x0, x1, y = 200, 1720, 470
    k = ease(c.k * 1.3)
    cv.drawLine(x0, y, x1, y, P(0x55FFFFFF, 10))
    cv.drawLine(x0, y, lerp(x0, x1, k), y, P(AMBER, 12))
    for i, (d, date, what) in enumerate(DAYS):
        x = x0 + (x1 - x0) * d / 69
        if k * 69 < d:
            continue
        cv.drawCircle(x, y, 22, P(GREEN if i == 3 else 0xFFFFFFFF))
        cv.drawCircle(x, y, 22, P(INK, 5))
        up = i % 2 == 0
        tx = min(max(x, 330), 1590) if i != 2 else x - 190
        fit(cv, date, tx, y - 120 if up else y + 110, 52, 420, 0xFFFFFFFF)
        fit(cv, what, tx, y - 62 if up else y + 168, 44, 420, AMBER if i != 3 else GREEN)
        cv.drawLine(x, y - (40 if up else -40), x, y - (56 if up else -56), P(0xFFFFFFFF, 4))


def board(cv, c):
    """Rook's board: the capsule at the surface, and the count."""
    plate(cv, 5, 0.7)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3) + 0.02 * c.k
    cv.save()
    cv.translate(560, 450)
    cv.scale(s, s)
    card(cv, 0, 0, 820, 640, -2.5)
    cv.rotate(-2.5)
    photo(cv, 'capsule', 0, -20, 760, 520, (0.5, 0.5))
    cv.restore()
    for x in (220, 900):
        cv.drawCircle(x, 130, 22, P(ORANGE))
        cv.drawCircle(x, 130, 22, P(INK, 5))
    left(cv, 'CASE 021', 1080, 250, 70, 0xCCFFFFFF)
    if c.lt > 0.25:
        left(cv, '33 OF 33', 1080, 400, 130, 0xFFFFFFFF)
    if c.lt > 0.45:
        left(cv, '69 DAYS', 1080, 550, 130, AMBER)
    if c.lt > 0.7:
        stamp(cv, 'TRUE', 1400, 720, -10, min(1, (c.lt - 0.7) / 0.12), 130, GREEN)


SHOTS = {f.__name__: f for f in (note_card, file_card, trap_card, depth_card, miss_card, plans_card, shaft_card, cal_card, hole_card, count33, timeline_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def mine_dust(cv, c):
    Wd.particles(cv, W, H, c.t, 44, 0x77E8D0B0, 63, size=(2, 6), drift=(24, 60), wobble=26, twinkle=True)


def rock_fall(cv, c):
    Wd.particles(cv, W, H, c.t, 64, 0x99D8C0A0, 65, size=(3, 9), drift=(0, 900), wobble=14)
    mine_dust(cv, c)


def thick_dust(cv, c):
    """Dust you cannot see through: a brown wash that breathes, and a lot of it in the air."""
    cv.drawRect(skia.Rect(0, 0, W, H), P(h('B49A7C'), a=0.2 + 0.06 * math.sin(c.t * 1.3)))
    for i in range(7):
        x = (rn(i, 21) * W + c.t * (40 + 60 * rn(i, 22))) % (W + 600) - 300
        Wd.glow(cv, x, 150 + 780 * rn(i, 23), 260 + 200 * rn(i, 24), h('C8B090'), 0.2)
    Wd.particles(cv, W, H, c.t, 110, 0x99E8D0B0, 71, size=(3, 9), drift=(90, 30), wobble=40)


def night_air(cv, c):
    Wd.particles(cv, W, H, c.t, 36, 0x77FFE8C0, 67, size=(2, 5), drift=(60, -30), wobble=30, twinkle=True)


def day_dust(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0x88E8C898, 69, size=(3, 8), drift=(300, -40), wobble=30)


def streak(cv, c):
    """The ride up: grit streaking down past the cage."""
    Wd.rain(cv, W, H, c.t, 80, 0x66E8D0B0, 0.0, 2600, 9, 110)


def closed(cv, c):
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(430, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 021', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(tie_note=mine_dust, drill_up=rock_fall, rig_night=night_air, bit_out=night_air, rook_rig=night_air, rook_peer=night_air, unfold=night_air,
            cheer=night_air, refuge_wide=mine_dust, faces=mine_dust, tents=night_air, cabinet=mine_dust, spoon=mine_dust, line_up=mine_dust,
            hole_measure=day_dust, big_drill=day_dust, break_through=rock_fall, capsule_top=night_air, rook_stuck=day_dust, capsule_arrive=mine_dust,
            step_in=mine_dust, shaft_ride=streak, ride_face=streak, emerge=night_air, hug=night_air, last_up=mine_dust, signoff=closed,
            shift=mine_dust, cave_in=rock_fall, dust_blind=thick_dust, block_wall=mine_dust, chimney=rock_fall, ladder_end=mine_dust, vote=mine_dust,
            battery=mine_dust, heat=mine_dust, listen=rock_fall, bang_bit=rock_fall, vigil=night_air, three_rigs=day_dust, dove=day_dust,
            dove_arrive=mine_dust, letter=mine_dust, muck=rock_fall, workshop=day_dust, first_down=night_air, greet=mine_dust, shades=night_air,
            gift=night_air, lights_out=mine_dust, sealed=day_dust)


def THUMB(cv, c):
    """1280x720: the 3D still (a miner's hands on the note tied to the drill, his face in the lamp behind it) and the hook on the left."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('3E2F28'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(640, 0), (0, 0)], [0x00000000, 0xE0000000])))
    Wd.text_card(cv, '17 DAYS', 310, 250, 132, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'BURIED.', 310, 395, 132, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'A NOTE.', 310, 540, 132, RED, 0xFF000000)
