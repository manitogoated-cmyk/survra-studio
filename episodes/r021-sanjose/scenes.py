"""Case 021 - the San Jose mine, Chile, 2010. The story is filmed in 3D (world3d.py). This file holds the flat
inserts (the note in red ink, a cross-section of the depth, the seven holes that missed, the ration calendar,
the thirty-three ticked off, Rook's case board on a steel plate) and the 2D overlays drawn on top of 3D shots
(dust in the mine, desert air, the day count, the sign-off). Every card is a drawing made for this film; none
reproduces a real document, photograph, map or logo. The note card gives an English translation of the note's
wording in a drawn hand: it is not a facsimile of the real note. The cross-sections are diagrams, not surveys."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F4EEDC'), h('D8261E'), h('3EC46A')
ORE, ORED, SAND, SKY = h('6A5244'), h('2E221C'), h('B4875A'), h('10183A')


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
    cv.drawRect(skia.Rect.MakeXYWH(50, 150, 980, 1620), P(h('5E646E')))
    cv.drawRect(skia.Rect.MakeXYWH(50, 150, 980, 1620), P(h('22262E'), 10))
    for i in range(26):                                            # scuffs
        x, y = 80 + rn(i, seed) * 900, 190 + rn(i, seed + 1) * 1540
        L = 60 + 240 * rn(i, seed + 2)
        cv.drawLine(x, y, x + L, y + L * (rn(i, seed + 3) - 0.5), P(h('8A909C') if i % 2 else h('3A3F4A'), 3 + 5 * rn(i, seed + 4), a=0.35))
    for (x, y) in ((95, 195), (985, 195), (95, 1725), (985, 1725)):
        cv.drawCircle(x, y, 20, P(h('2A2E38')))
        cv.drawCircle(x - 4, y - 4, 8, P(h('9AA0AC')))
    if glow:
        Wd.glow(cv, 540, 820, 900, h('FFC890'), 0.2 * glow)
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


# ---------------------------------------------------------------- inserts
NOTE = ('WE ARE FINE', 'IN THE SHELTER,', 'THE 33 OF US')


def note_card(cv, c):
    """The note, held to the light: red ink on a creased sheet. English translation, written out line by line."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1230')), (0.6, h('1C1A2C')), (1, h('0A0A14'))])
    Wd.glow(cv, 540, 640, 1000, h('FFE2B0'), 0.3)
    k = min(1, c.lt / 0.14)
    s = 0.8 + 0.2 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 640)
    cv.scale(s, s)
    cv.rotate(-2.5 + 0.6 * math.sin(c.t * 2.2))
    cv.drawRect(skia.Rect.MakeXYWH(-450 + 14, -330 + 18, 900, 660), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-450, -330, 900, 660), P(PAPER))
    for x in (-150, 150):                                          # creases
        cv.drawLine(x, -330, x, 330, P(h('CFC6AE'), 4))
    cv.drawLine(-450, 0, 450, 0, P(h('DAD2BC'), 3))
    for i in range(7):                                             # dust and thumb marks
        cv.drawCircle(-380 + 760 * rn(i, 3), -280 + 560 * rn(i, 4), 16 + 30 * rn(i, 5), P(h('B4875A'), a=0.16))
    shown = c.lt / 0.22
    for i, line in enumerate(NOTE):
        if shown < i:
            break
        n = max(1, int(len(line) * min(1.0, shown - i)))
        f = font(102, True)
        tw = f.measureText(line)
        cv.drawString(line[:n], -tw / 2, -150 + 150 * i + 30, f, P(RED))
    cv.restore()
    fit(cv, 'RED INK. TRANSLATED.', 540, 1090, 46, 800, 0xCCFFFFFF, None)
    fit(cv, '22 AUGUST 2010', 540, 1640, 76, 900, AMBER)
    Wd.particles(cv, W, H, c.t, 20, 0x66FFE8C0, 61, size=(2, 5), drift=(30, -40), wobble=24, twinkle=True)


def section(cv, t, depth_k=1.0):
    """A drawn cross-section: night sky, desert, the rock, and one small room far below. Returns the room's centre."""
    Wd.vgrad(cv, 0, 0, W, 330, [(0, h('0A1030')), (1, h('2A2A5A'))])
    for i in range(18):
        cv.drawCircle(40 + 1000 * rn(i, 7), 30 + 230 * rn(i, 8), 2 + 2 * rn(i, 9), P(0xFFFFFFFF, a=0.5 + 0.4 * math.sin(t * 3 + i)))
    cv.drawPath(poly([(-20, 330), (240, 300), (520, 322), (800, 296), (1100, 318), (1100, 420), (-20, 420)]), P(SAND))
    Wd.vgrad(cv, 0, 380, W, H, [(0, h('7A5E4C')), (0.35, h('5A463A')), (1, h('2A201C'))])
    for i in range(22):                                            # strata and boulders
        x, y = rn(i, 11) * W, 440 + rn(i, 12) * 1400
        s = 60 + 150 * rn(i, 13)
        cv.drawPath(poly([(x, y), (x + s, y + 0.2 * s), (x + 0.7 * s, y + 0.6 * s), (x - 0.3 * s, y + 0.4 * s)]), P(h('8C7260') if i % 2 else h('1E1614'), a=0.22))
    rx, ry = 620, 1090
    cv.drawRoundRect(skia.Rect.MakeXYWH(rx - 150, ry - 50, 300, 100), 18, 18, P(0xFF0A0706))
    cv.drawRoundRect(skia.Rect.MakeXYWH(rx - 150, ry - 50, 300, 100), 18, 18, P(h('FFC890'), 5, a=0.6))
    for i in range(33):
        cv.drawCircle(rx - 128 + 16 * (i % 17), ry - 14 + 30 * (i // 17), 6, P(AMBER))
    return rx, ry


def derrick(cv, x, y, s=1.0):
    for sx in (-1, 1):
        cv.drawLine(x + sx * 46 * s, y, x + sx * 12 * s, y - 190 * s, P(h('C8CCD4'), 8 * s))
    for i in range(4):
        yy = y - 30 * s - i * 42 * s
        ww = 46 * s - (yy - y) / (-190 * s) * 34 * s
        cv.drawLine(x - ww, yy, x + ww, yy - 20 * s, P(h('C8CCD4'), 4 * s))
    cv.drawRect(skia.Rect.MakeXYWH(x - 20 * s, y - 206 * s, 40 * s, 18 * s), P(AMBER))


def depth_card(cv, c):
    """'...seven hundred metres down.' The derrick on top, the shelter far below, and the measure between them."""
    rx, ry = section(cv, c.t)
    derrick(cv, 330, 318)
    k = ease(c.k * 1.5)
    y1 = lerp(330, ry, k)
    cv.drawLine(210, 330, 210, y1, P(0xFF000000, 16))
    cv.drawLine(210, 330, 210, y1, P(AMBER, 8))
    for i in range(8):
        yy = 330 + (ry - 330) * i / 7
        if yy <= y1 + 1:
            cv.drawLine(190, yy, 230, yy, P(AMBER, 6))
    if k > 0.95:
        cv.drawLine(210, ry, rx - 160, ry, P(AMBER, 6))
    n = int(round(700 * k / 10) * 10)
    fit(cv, f'{n} M', 610, 700, 190, 620, AMBER)
    fit(cv, 'NOT TO SCALE', 540, 1650, 44, 600, 0x99FFFFFF, None)


MISS = [(-260, 0.80), (-200, 0.96), (-120, 0.62), (190, 0.90), (250, 0.70), (310, 1.0), (-320, 1.04)]


def miss_card(cv, c):
    """'Seven drill holes had missed.' Seven lines go down past the room, one after another; the eighth reaches it."""
    rx, ry = section(cv, c.t)
    derrick(cv, 540, 318, 0.9)
    n = c.k * 9.0
    for i, (dx, f) in enumerate(MISS):
        k = max(0.0, min(1.0, n - i))
        if k <= 0:
            continue
        x1, y1 = rx + dx, 330 + (ry + 90 - 330) * f
        x, y = lerp(540, x1, k), lerp(330, y1, k)
        cv.drawLine(540, 330, x, y, P(0xFF000000, 12))
        cv.drawLine(540, 330, x, y, P(h('C8CCD4'), 6))
        if k >= 1:
            for sgn in (-1, 1):
                cv.drawLine(x1 - 20, y1 - 20 * sgn, x1 + 20, y1 + 20 * sgn, P(RED, 9))
    k8 = max(0.0, min(1.0, n - 7.4))
    if k8 > 0:
        cv.drawLine(540, 330, lerp(540, rx - 40, k8), lerp(330, ry - 50, k8), P(0xFF000000, 14))
        cv.drawLine(540, 330, lerp(540, rx - 40, k8), lerp(330, ry - 50, k8), P(GREEN, 8))
    fit(cv, f'{min(7, int(n))} MISSED', 540, 560, 150, 900, 0xFFFFFFFF)
    if k8 >= 1:
        fit(cv, 'DAY 17', 540, 1650, 110, 800, GREEN)
    else:
        fit(cv, 'NOT TO SCALE', 540, 1650, 44, 600, 0x99FFFFFF, None)


def cal_card(cv, c):
    """'...every other day.' A row of days: a spoon on one, nothing on the next."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A201C')), (0.5, h('3E2F28')), (1, h('14100E'))])
    Wd.glow(cv, 540, 760, 900, h('FFC890'), 0.2)
    fit(cv, 'EVERY OTHER DAY', 540, 380, 110, 940, AMBER)
    n = c.k * 14
    for i in range(12):
        col, row = i % 4, i // 4
        x, y = 195 + 230 * col, 620 + 200 * row
        on = i < n
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 95, y - 80, 190, 160), 18, 18, P(PAPER, a=1.0 if on else 0.25))
        if not on:
            continue
        if i % 2 == 0:
            cv.drawLine(x - 10, y + 10, x + 62, y - 46, P(h('8A909C'), 12))
            cv.drawOval(skia.Rect.MakeXYWH(x - 62, y - 8, 70, 46), P(h('8A909C')))
            cv.drawOval(skia.Rect.MakeXYWH(x - 52, y - 4, 50, 30), P(h('E0A088')))
        else:
            cv.drawLine(x - 40, y, x + 40, y, P(h('B8AE98'), 10))
    fit(cv, '2 SPOONFULS OF TUNA', 540, 1650, 78, 940, 0xFFFFFFFF)


HELMC = ('E0B020', 'C8372D', 'E07A1E')


def count33(cv, c):
    """'...all thirty-three are out.' Thirty-three helmets, ticked off one by one."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10183A')), (0.6, h('2A2A5A')), (1, h('0C1024'))])
    Wd.glow(cv, 540, 760, 900, h('FFC890'), 0.22)
    fit(cv, '13 OCTOBER 2010', 540, 300, 80, 900, 0xFFFFFFFF)
    n = c.k * 40
    for i in range(33):
        col, row = i % 6, i // 6
        cnt = 6 if row < 5 else 3
        x = 540 + (col - (cnt - 1) / 2) * 160
        y = 470 + row * 124
        helmet(cv, x, y, 0.82, h('F2F2EC') if i == 32 else h(HELMC[i % 3]))
        tick(cv, x + 34, y + 26, 0.95, min(1.0, max(0.0, n - i)))
    if c.k > 0.82:
        fit(cv, '33 OF 33', 540, 1680, 160, 900, GREEN)


def board(cv, c):
    """Rook's board: the capsule at the surface, and the question he leaves with us."""
    plate(cv, 5, 0.7)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 660)
    cv.scale(s, s)
    card(cv, 0, 0, 780, 800, 2.5)
    cv.rotate(2.5)
    photo(cv, 'capsule', 0, -30, 710, 660, (0.5, 0.5))
    cv.restore()
    for x in (200, 880):
        cv.drawCircle(x, 280, 24, P(ORANGE))
        cv.drawCircle(x, 280, 24, P(INK, 5))
    if c.lt > 0.25:
        fit(cv, 'WOULD YOU', 540, 1600, 124, 880, 0xFFFFFFFF)
    if c.lt > 0.45:
        fit(cv, 'HAVE WAITED?', 540, 1740, 124, 900, AMBER)
    if c.lt > 0.7:
        stamp(cv, 'TRUE', 770, 330, -10, min(1, (c.lt - 0.7) / 0.12), 140, GREEN)


SHOTS = {f.__name__: f for f in (note_card, depth_card, miss_card, cal_card, count33, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def mine_dust(cv, c):
    Wd.particles(cv, W, H, c.t, 34, 0x77E8D0B0, 63, size=(2, 6), drift=(14, 60), wobble=26, twinkle=True)


def rock_fall(cv, c):
    Wd.particles(cv, W, H, c.t, 50, 0x99D8C0A0, 65, size=(3, 9), drift=(0, 900), wobble=14)
    mine_dust(cv, c)


def night_air(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x77FFE8C0, 67, size=(2, 5), drift=(50, -30), wobble=30, twinkle=True)


def day_dust(cv, c):
    Wd.particles(cv, W, H, c.t, 44, 0x88E8C898, 69, size=(3, 8), drift=(240, -40), wobble=30)


def streak(cv, c):
    """The ride up: grit streaking down past the cage."""
    Wd.rain(cv, W, H, c.t, 60, 0x66E8D0B0, 0.0, 2600, 9, 110)


def days69(cv, c):
    night_air(cv, c)
    if c.lt > 0.35:
        k = min(1, (c.lt - 0.35) / 0.15)
        cv.save()
        cv.translate(540, 420)
        cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
        Wd.text_card(cv, '69 DAYS', 0, 0, 210, AMBER, 0xFF000000)
        cv.restore()


def closed(cv, c):
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 021', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(tie_note=mine_dust, drill_up=rock_fall, rig_night=night_air, bit_out=night_air, rook_rig=night_air, rook_peer=night_air, unfold=night_air,
            cheer=night_air, refuge_wide=mine_dust, faces=mine_dust, tents=night_air, cabinet=mine_dust, spoon=mine_dust, line_up=mine_dust,
            hole_measure=day_dust, big_drill=day_dust, break_through=rock_fall, capsule_top=night_air, rook_stuck=day_dust, capsule_arrive=mine_dust,
            step_in=mine_dust, shaft_ride=streak, ride_face=streak, emerge=night_air, hug=days69, last_up=mine_dust, signoff=closed)
