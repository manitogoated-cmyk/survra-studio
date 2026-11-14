"""Case 010 - Tsutomu Yamaguchi. The story is filmed in 3D (world3d.py). This file holds the flat inserts (Rook's
case board on blueprint paper, the personnel file, two sketch maps, the clock, the years counter, the record
card) and the 2D overlays drawn on top of 3D shots (the white of the two flashes, dust, the sign-off).
Every card is a drawing made for this film; none of them reproduces a real document."""
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
ORANGE, AMBER, PAPER, RED, BLUE = h('FF7A1A'), h('FFB000'), h('F1E6CC'), h('D8362A'), h('1D3F6E')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) pinned to the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('8EA8C8')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def blueprint(cv, seed=10):
    """Rook's board for this case: a sheet of blueprint paper, because the man was a draughtsman."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('20508E')), (1, h('122E5A'))])
    for i in range(0, W, 54):
        cv.drawLine(i, 0, i, H, P(0x24FFFFFF, 5 if i % 270 == 0 else 2))
    for j in range(0, H, 54):
        cv.drawLine(0, j, W, j, P(0x24FFFFFF, 5 if j % 270 == 0 else 2))
    cv.drawRect(skia.Rect.MakeLTRB(40, 40, W - 40, H - 40), P(0x66FFFFFF, 5))
    cv.drawCircle(860, 1560, 150, P(0x33FFFFFF, 4))
    cv.drawCircle(860, 1560, 96, P(0x33FFFFFF, 4))
    cv.drawLine(660, 1560, 1040, 1560, P(0x33FFFFFF, 3))
    cv.drawLine(860, 1380, 860, 1740, P(0x33FFFFFF, 3))
    cv.drawPath(poly([(120, 1700), (420, 1700), (500, 1640), (560, 1700), (620, 1700)], closed=False), P(0x33FFFFFF, 4))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x44000000), (0.5, 0x00000000), (1, 0x77000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, tape=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if tape:
        cv.drawRect(skia.Rect.MakeXYWH(-70, -h_ / 2 - 24, 140, 48), P(0xCCFF7A1A))
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=64):
    card(cv, x, y, w_, h_, ang, col, tape=False)
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
    box = skia.Rect.MakeLTRB(-tw / 2 - 44, -size * 0.72, tw / 2 + 44, size * 0.42)
    cv.drawRoundRect(box, 18, 18, P(0xEE10244A))
    cv.drawRoundRect(box, 18, 18, P(col, 18))
    Wd.text_card(cv, s, 0, size * 0.18, size, col, None)
    cv.restore()


# ------------------------------------------------------------------ flat inserts
def board_no(cv, c):
    blueprint(cv)
    k = min(1, c.lt / 0.18)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 640)
    cv.scale(s, s)
    card(cv, 0, 0, 760, 620, -3)
    cv.rotate(-3)
    photo(cv, 'yard', 0, 10, 690, 520, (0.5, 0.35))
    cv.restore()
    if c.lt > 0.16:
        cv.drawLine(330, 380, 280, 1050, P(RED, 8))
        note(cv, 280, 1100, 440, 210, 5, h('FFD866'), ['HIROSHIMA', '6 AUG'], 62)
    if c.lt > 0.28:
        cv.drawLine(750, 380, 800, 1050, P(RED, 8))
        note(cv, 800, 1110, 440, 210, -6, h('BFE0EC'), ['NAGASAKI', '9 AUG'], 62)
    if c.k > 0.55:
        stamp(cv, 'NO CHANCE', 540, 700, -12, min(1, (c.k - 0.55) / 0.14), 132)


def id_card(cv, c):
    """A personnel file drawn for the film. The portrait is a silhouette, not a photograph of him."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A3C70')), (1, h('0C1E3E'))])
    k = ease(c.lt / 0.22)
    cv.save()
    cv.translate(540, 730 + 500 * (1 - k))
    cv.rotate(2.0)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-448, -420, 920, 900), 22, 22, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-460, -440, 920, 900), 22, 22, P(h('EFE6CC')))
    cv.drawRect(skia.Rect.MakeXYWH(-460, -440, 920, 120), P(BLUE))
    Wd.text_card(cv, 'PERSONNEL FILE', 0, -356, 70, PAPER, None)
    cv.drawRect(skia.Rect.MakeXYWH(-410, -280, 280, 340), P(h('B8C4D4')))
    cv.drawRect(skia.Rect.MakeXYWH(-410, -280, 280, 340), P(INK, 6))
    cv.drawCircle(-270, -160, 70, P(h('44546C')))
    cv.drawPath(poly([(-384, 60), (-366, -52), (-310, -82), (-230, -82), (-174, -52), (-156, 60)]), P(h('44546C')))
    rows = (('NAME', 'TSUTOMU YAMAGUCHI', 0.25), ('AGE', '29', 0.75), ('WORK', 'ENGINEER, SHIP DESIGN', 0.5))
    for i, (lab, val, at_) in enumerate(rows):
        y = -236 + i * 118
        Wd.text_card(cv, lab, -95, y, 32, h('7A6A48'), None, center=False)
        if c.k > at_ - 0.2:
            f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), 52)
            size = min(52, 52 * 520 / f.measureText(val))
            Wd.text_card(cv, val, -95, y + 58, size, INK, None, center=False)
    cv.drawLine(-410, 110, 410, 110, P(h('7A6A48'), 4))
    Wd.text_card(cv, 'EMPLOYER', -410, 166, 32, h('7A6A48'), None, center=False)
    Wd.text_card(cv, 'MITSUBISHI HEAVY INDUSTRIES', -410, 226, 50, BLUE, None, center=False)
    Wd.text_card(cv, 'SUMMER 1945', -410, 300, 32, h('7A6A48'), None, center=False)
    if c.k > 0.62:
        Wd.text_card(cv, 'WORK TRIP: HIROSHIMA', -410, 372, 62, RED, None, center=False)
    Wd.text_card(cv, 'DRAWN FOR THIS FILM', 0, 436, 26, h('9A8A68'), None)
    cv.restore()


def map_dist(cv, c):
    """Sketch only: how far he was from the centre of the explosion (about 3 km, under two miles)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A3C70')), (1, h('0C1E3E'))])
    cx, cy = 540, 690
    for i, r in enumerate((110, 220, 330)):
        k = ease((c.k - 0.05 - i * 0.12) / 0.2)
        if k > 0:
            cv.drawCircle(cx, cy, r * k, P(0xFFFFFFFF if i == 2 else 0x66FFFFFF, 10 if i == 2 else 4))
    cv.drawCircle(cx, cy, 26, P(0xFFFFFFFF))
    cv.drawCircle(cx, cy, 26 + 50 * ((c.t * 1.6) % 1), P(Wd.alpha(0xFFFFFFFF, 1 - (c.t * 1.6) % 1), 6))
    Wd.text_card(cv, 'CENTRE OF THE BLAST', cx, cy - 56, 40, 0xFFFFFFFF, 0xFF000000)
    if c.k > 0.4:
        a = math.radians(38)
        px, py = cx + math.cos(a) * 330, cy + math.sin(a) * 330
        cv.drawLine(cx, cy, px, py, P(AMBER, 8))
        cv.drawCircle(px, py, 30, P(AMBER))
        cv.drawCircle(px, py, 30, P(0xFF000000, 6))
        Wd.text_card(cv, 'HIM', px - 10, py + 96, 76, AMBER, 0xFF000000)
        Wd.text_card(cv, 'ABOUT 3 KM', 540, 1200, 110, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'SKETCH, NOT A MAP', 540, 1540, 34, 0xCCFFFFFF, None)


def map_two(cv, c):
    """Sketch only: two cities and the rail journey between them. Positions are schematic."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A3C70')), (1, h('0C1E3E'))])
    a, b = (800, 520), (260, 1010)
    k = ease(c.k / 0.6)
    n = 26
    for i in range(n + 1):
        u = i / n
        if u > k:
            break
        x, y = lerp(a[0], b[0], u), lerp(a[1], b[1], u) + 60 * math.sin(u * math.pi)
        cv.drawRect(skia.Rect.MakeXYWH(x - 12, y - 5, 24, 10), P(0xFFFFFFFF))
    cv.drawCircle(a[0], a[1], 30, P(0xFFFFFFFF))
    fit(cv, 'HIROSHIMA', 760, a[1] - 130, 84, 600, 0xFFFFFFFF)
    fit(cv, '6 AUG 1945', 760, a[1] - 60, 54, 600, 0xCCFFFFFF)
    if k >= 1:
        cv.drawCircle(b[0], b[1], 30, P(AMBER))
        cv.drawCircle(b[0], b[1], 30 + 44 * ((c.t * 2) % 1), P(Wd.alpha(AMBER, 1 - (c.t * 2) % 1), 7))
    fit(cv, 'NAGASAKI', 330, b[1] + 120, 84, 600, AMBER)
    fit(cv, '9 AUG 1945', 330, b[1] + 190, 54, 600, AMBER)
    fit(cv, 'HIS HOME', 330, b[1] + 250, 44, 600, 0xCCFFFFFF)
    Wd.text_card(cv, 'SKETCH, NOT TO SCALE', 540, 1300, 34, 0xCCFFFFFF, None)


def clock_1102(cv, c):
    """The time on record for Nagasaki: 11:02 in the morning."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('B8B09A')), (1, h('7E7868'))])
    cx, cy, r = 540, 760, 320
    cv.drawCircle(cx + 14, cy + 20, r + 30, P(0x55000000))
    cv.drawCircle(cx, cy, r + 30, P(h('3A2C1E')))
    cv.drawCircle(cx, cy, r, P(h('EFE6CC')))
    for i in range(12):
        a = i * math.pi / 6
        cv.drawLine(cx + math.sin(a) * (r - 60), cy - math.cos(a) * (r - 60), cx + math.sin(a) * (r - 18), cy - math.cos(a) * (r - 18),
                    P(INK, 18 if i % 3 == 0 else 9))
    mins = 2 - 0.5 * (1 - ease(c.k / 0.5))
    am, ah = math.radians(mins * 6), math.radians((11 + mins / 60) * 30)
    cv.drawLine(cx, cy, cx + math.sin(ah) * 175, cy - math.cos(ah) * 175, P(INK, 26))
    cv.drawLine(cx, cy, cx + math.sin(am) * 270, cy - math.cos(am) * 270, P(INK, 16))
    sa = math.radians(c.t * 6 * 8)
    cv.drawLine(cx, cy, cx + math.sin(sa) * 285, cy - math.cos(sa) * 285, P(RED, 6))
    cv.drawCircle(cx, cy, 24, P(INK))
    Wd.text_card(cv, '11:02', 540, 330, 170, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, '9 AUGUST 1945', 540, 1560, 60, 0xFFFFFFFF, 0xFF000000)


def years(cv, c):
    """He was 29 in August 1945 and 93 when he died in January 2010."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A3C70')), (1, h('0C1E3E'))])
    k = ease(c.k / 0.42)
    age = int(round(lerp(29, 93, k)))
    yr = int(round(lerp(1945, 2010, k)))
    for i in range(65):
        x = 90 + i * 14
        on = i <= (yr - 1945)
        cv.drawLine(x, 1060, x, 1060 - (70 if i % 5 == 0 else 40), P(AMBER if on else 0x55FFFFFF, 6))
    pop = 1 + 0.22 * max(0.0, 1 - abs(c.k - 0.45) / 0.1)
    cv.save()
    cv.translate(540, 700)
    cv.scale(pop, pop)
    Wd.text_card(cv, str(age), 0, 110, 400, AMBER if age >= 93 else 0xFFFFFFFF, 0xFF000000)
    cv.restore()
    Wd.text_card(cv, 'AGE', 540, 400, 96, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, str(yr), 540, 1180, 96, 0xFFFFFFFF, 0xFF000000)


def cert(cv, c):
    """A record card drawn for the film (not the real certificate): what Japan recognised in March 2009."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A3C70')), (1, h('0C1E3E'))])
    k = ease(c.lt / 0.22)
    cv.save()
    cv.translate(540, 720 + 500 * (1 - k))
    cv.rotate(-2.0)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-448, -420, 920, 900), 22, 22, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-460, -440, 920, 900), 22, 22, P(h('EFE6CC')))
    cv.drawRect(skia.Rect.MakeXYWH(-460, -440, 920, 120), P(BLUE))
    Wd.text_card(cv, 'SURVIVOR RECORD', 0, -356, 70, PAPER, None)
    Wd.text_card(cv, 'TSUTOMU YAMAGUCHI', 0, -240, 64, INK, None)
    for i, (city, date, at_) in enumerate((('HIROSHIMA', '6 AUG 1945', 0.25), ('NAGASAKI', '9 AUG 1945', 0.42))):
        y = -110 + i * 170
        cv.drawRect(skia.Rect.MakeXYWH(-410, y - 70, 110, 110), P(INK, 8))
        Wd.text_card(cv, city, -260, y - 6, 70, INK, None, center=False)
        Wd.text_card(cv, date, -260, y + 44, 40, h('7A6A48'), None, center=False)
        if c.k > at_:
            cv.drawPath(poly([(-396, y - 20), (-362, y + 22), (-296, y - 78)], closed=False), P(RED, 18))
    cv.drawLine(-410, 200, 410, 200, P(h('7A6A48'), 4))
    Wd.text_card(cv, 'RECOGNISED BY JAPAN', 0, 270, 52, BLUE, None)
    Wd.text_card(cv, 'MARCH 2009', 0, 340, 60, BLUE, None)
    Wd.text_card(cv, 'DRAWN FOR THIS FILM', 0, 436, 26, h('9A8A68'), None)
    cv.restore()
    if c.k > 0.62:
        stamp(cv, 'BOTH', 730, 1010, -14, min(1, (c.k - 0.62) / 0.12), 150)


def board_true(cv, c):
    blueprint(cv)
    card(cv, 540, 660, 680, 760, 2)
    cv.save()
    cv.translate(540, 660)
    cv.rotate(2)
    photo(cv, 'old', 0, 10, 610, 660, (0.5, 0.42))
    cv.restore()
    note(cv, 270, 1500, 420, 150, -5, h('FFD866'), ['HIROSHIMA'], 60)
    note(cv, 800, 1510, 420, 150, 4, h('BFE0EC'), ['NAGASAKI'], 60)
    if c.lt > 0.3:
        stamp(cv, 'TRUE', 560, 1010, -10, min(1, (c.lt - 0.3) / 0.12), 170)


SHOTS = {f.__name__: f for f in (board_no, id_card, map_dist, map_two, clock_1102, years, cert, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def white(cv, a):
    if a > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(Wd.alpha(0xFFFFFFFF, min(1.0, a))))


def flash_far(cv, c):
    """The first flash, seen from the road: the white grows from the horizon."""
    white(cv, 0.75 * ease((c.lt - 0.35) / 0.7))


def flash_near(cv, c):
    white(cv, 0.55 * ease(c.lt / 0.5))


def flash_room(cv, c):
    white(cv, 0.5 * ease((c.lt - 0.6) / 0.6))


def fade_white(cv, c):
    """Coming out of a flash: the white drains away."""
    white(cv, 0.8 * (1 - ease(c.lt / 0.45)))


def ash(cv, c):
    Wd.particles(cv, W, H, c.t, 46, 0x88E8D8C0, 4, size=(3, 8), drift=(-30, 70), wobble=30)


def ash_fade(cv, c):
    ash(cv, c)
    fade_white(cv, c)


def closed(cv, c):
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 010  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(flash_city=flash_far, flash_road=flash_near, flash_office=flash_room, thrown=fade_white, dust_rise=ash_fade,
            aftermath=ash, office_blast=fade_white, yama_stands=ash, signoff=closed)
