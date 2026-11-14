"""Case 010, the full case file - Tsutomu Yamaguchi. The story is filmed in 3D (world3d.py). This file holds the flat
inserts for the 16:9 film (Rook's case board on blueprint paper, the personnel file, a tanker plan, sketch maps, two
clocks, a calendar, the 1957 and 2009 record cards, the count of double survivors, the years counter), the 2D overlays
drawn on top of 3D shots (the white of the two flashes, dust, the sign-off) and the thumbnail.
Every card is a drawing made for this film; none of them reproduces a real document."""
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
ORANGE, AMBER, PAPER, RED, BLUE = h('FF7A1A'), h('FFB000'), h('F1E6CC'), h('D8362A'), h('1D3F6E')
WHITE, BLACK, DIM, TAN = 0xFFFFFFFF, 0xFF000000, 0xCCFFFFFF, h('7A6A48')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def fit(cv, s, x, y, size, maxw, color=WHITE, stroke=BLACK, center=True):
    """Text that shrinks to stay inside maxw."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke, center=center)


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


def night(cv):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A3C70')), (1, h('0C1E3E'))])


def blueprint(cv):
    """Rook's board for this case: a sheet of blueprint paper, because the man was a draughtsman."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('20508E')), (1, h('122E5A'))])
    for i in range(0, W, 60):
        cv.drawLine(i, 0, i, H, P(0x24FFFFFF, 5 if i % 300 == 0 else 2))
    for j in range(0, H, 60):
        cv.drawLine(0, j, W, j, P(0x24FFFFFF, 5 if j % 300 == 0 else 2))
    cv.drawRect(skia.Rect.MakeLTRB(36, 36, W - 36, H - 36), P(0x66FFFFFF, 5))
    cv.drawCircle(1660, 760, 150, P(0x33FFFFFF, 4))
    cv.drawCircle(1660, 760, 96, P(0x33FFFFFF, 4))
    cv.drawLine(1460, 760, 1860, 760, P(0x33FFFFFF, 3))
    cv.drawLine(1660, 580, 1660, 940, P(0x33FFFFFF, 3))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x44000000), (0.5, 0x00000000), (1, 0x77000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, tape=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if tape:
        cv.drawRect(skia.Rect.MakeXYWH(-70, -h_ / 2 - 22, 140, 44), P(0xCCFF7A1A))
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=60):
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


def sheet(cv, c, x, y, w_, h_, ang, title, slide=True):
    """A paper record card with a blue title band; returns after translating to its centre (caller restores)."""
    k = ease(c.lt / 0.25) if slide else 1.0
    cv.save()
    cv.translate(x, y + 700 * (1 - k))
    cv.rotate(ang)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), 20, 20, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), 20, 20, P(h('EFE6CC')))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, 96), P(BLUE))
    Wd.text_card(cv, title, 0, -h_ / 2 + 68, 56, PAPER, None)
    Wd.text_card(cv, 'DRAWN FOR THIS FILM', 0, h_ / 2 - 20, 22, h('9A8A68'), None)


# ------------------------------------------------------------------ flat inserts
def board_no(cv, c):
    blueprint(cv)
    k = min(1, c.lt / 0.18)
    s = 0.8 + 0.2 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(560, 450)
    cv.scale(s, s)
    card(cv, 0, 0, 800, 560, -3)
    cv.rotate(-3)
    photo(cv, 'yard', 0, 6, 740, 480, (0.5, 0.4))
    cv.restore()
    if c.lt > 0.14:
        cv.drawLine(940, 300, 1180, 250, P(RED, 8))
        note(cv, 1400, 250, 520, 190, 4, h('FFD866'), ['HIROSHIMA', '6 AUG 1945'], 58)
    if c.lt > 0.26:
        cv.drawLine(940, 560, 1180, 640, P(RED, 8))
        note(cv, 1400, 640, 520, 190, -5, h('BFE0EC'), ['NAGASAKI', '9 AUG 1945'], 58)
    if c.k > 0.5:
        stamp(cv, 'NO CHANCE', 900, 470, -12, min(1, (c.k - 0.5) / 0.14), 150)


def id_card(cv, c):
    """A personnel file drawn for the film. The portrait is a silhouette, not a photograph of him."""
    night(cv)
    sheet(cv, c, 960, 450, 1500, 640, 1.2, 'PERSONNEL FILE')
    cv.drawRect(skia.Rect.MakeXYWH(-700, -190, 330, 400), P(h('B8C4D4')))
    cv.drawRect(skia.Rect.MakeXYWH(-700, -190, 330, 400), P(INK, 6))
    cv.drawCircle(-535, -50, 82, P(h('44546C')))
    cv.drawPath(poly([(-668, 210), (-648, 80), (-584, 44), (-486, 44), (-422, 80), (-402, 210)]), P(h('44546C')))
    rows = (('NAME', 'TSUTOMU YAMAGUCHI', 0.15), ('BORN', 'NAGASAKI, 1916', 0.35), ('WORK', 'DRAUGHTSMAN, OIL TANKERS', 0.55))
    for i, (lab, val, at_) in enumerate(rows):
        y = -160 + i * 118
        Wd.text_card(cv, lab, -310, y, 30, TAN, None, center=False)
        if c.k > at_:
            fit(cv, val, -310, y + 60, 58, 960, INK, None, center=False)
    cv.drawLine(-310, 200, 690, 200, P(TAN, 4))
    if c.k > 0.72:
        fit(cv, 'MITSUBISHI HEAVY INDUSTRIES', -310, 262, 52, 960, BLUE, None, center=False)
    cv.restore()


def tanker_plan(cv, c):
    """A side view of a plain tanker, drawn line by line as on a drawing table. Not a real ship's plan."""
    blueprint(cv)
    k = ease(c.k / 0.75)
    pts = [(330, 560), (360, 650), (1480, 650), (1600, 560), (1560, 560), (1560, 520), (1380, 520), (1380, 560), (700, 560), (700, 430),
           (520, 430), (520, 560), (330, 560)]
    n = len(pts) - 1
    line = P(0xFFEAF2FF, 9)
    for i in range(n):
        u = max(0.0, min(1.0, k * n - i))
        if u <= 0:
            break
        a, b = pts[i], pts[i + 1]
        cv.drawLine(a[0], a[1], lerp(a[0], b[0], u), lerp(a[1], b[1], u), line)
    if k > 0.55:
        cv.drawRect(skia.Rect.MakeXYWH(575, 330, 70, 100), P(0xFFEAF2FF, 8))
        for x in (800, 960, 1120, 1280):
            cv.drawLine(x, 560, x, 650, P(0x88EAF2FF, 5))
        cv.drawLine(360, 690, 1480, 690, P(AMBER, 5))
        for x in (360, 1480):
            cv.drawLine(x, 674, x, 706, P(AMBER, 5))
    if k > 0.8:
        Wd.text_card(cv, 'OIL TANKER', 960, 250, 110, WHITE, BLACK)
        Wd.text_card(cv, 'ILLUSTRATION, NOT A REAL PLAN', 960, 770, 30, DIM, None)


def rail_dots(cv, a, b, k, bow=60, n=30, col=WHITE):
    for i in range(n + 1):
        u = i / n
        if u > k:
            break
        x, y = lerp(a[0], b[0], u), lerp(a[1], b[1], u) + bow * math.sin(u * math.pi)
        cv.drawRect(skia.Rect.MakeXYWH(x - 13, y - 5, 26, 10), P(col))


def map_trip(cv, c):
    """Sketch only: sent from Nagasaki to the shipyard in Hiroshima for about three months. Positions are schematic."""
    night(cv)
    a, b = (420, 610), (1500, 330)
    cv.drawCircle(a[0], a[1], 28, P(AMBER))
    fit(cv, 'NAGASAKI', a[0], a[1] + 100, 76, 620, AMBER)
    fit(cv, 'HOME', a[0], a[1] + 156, 40, 620, DIM)
    k = ease(c.k / 0.55)
    rail_dots(cv, a, b, k, bow=-70)
    if k >= 1:
        cv.drawCircle(b[0], b[1], 28, P(WHITE))
        cv.drawCircle(b[0], b[1], 28 + 44 * ((c.t * 2) % 1), P(Wd.alpha(WHITE, 1 - (c.t * 2) % 1), 7))
        fit(cv, 'HIROSHIMA', b[0], b[1] - 60, 76, 620, WHITE)
        fit(cv, 'THE SHIPYARD', b[0], b[1] + 100, 40, 620, DIM)
    if c.k > 0.62:
        Wd.text_card(cv, '3 MONTHS', 960, 640, 150, WHITE, BLACK)
    Wd.text_card(cv, 'SKETCH, NOT TO SCALE', 960, 790, 30, DIM, None)


def clock_face(cv, c, hour, minute, label, date, bg=('B8B09A', '7E7868')):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(bg[0])), (1, h(bg[1]))])
    cx, cy, r = 640, 450, 300
    cv.drawCircle(cx + 14, cy + 20, r + 30, P(0x55000000))
    cv.drawCircle(cx, cy, r + 30, P(h('3A2C1E')))
    cv.drawCircle(cx, cy, r, P(h('EFE6CC')))
    for i in range(12):
        a = i * math.pi / 6
        cv.drawLine(cx + math.sin(a) * (r - 56), cy - math.cos(a) * (r - 56), cx + math.sin(a) * (r - 18), cy - math.cos(a) * (r - 18),
                    P(INK, 18 if i % 3 == 0 else 9))
    mins = minute - 0.6 * (1 - ease(c.k / 0.5))
    am, ah = math.radians(mins * 6), math.radians((hour + mins / 60) * 30)
    cv.drawLine(cx, cy, cx + math.sin(ah) * 165, cy - math.cos(ah) * 165, P(INK, 26))
    cv.drawLine(cx, cy, cx + math.sin(am) * 250, cy - math.cos(am) * 250, P(INK, 16))
    sa = math.radians(c.t * 6 * 8)
    cv.drawLine(cx, cy, cx + math.sin(sa) * 268, cy - math.cos(sa) * 268, P(RED, 6))
    cv.drawCircle(cx, cy, 24, P(INK))
    Wd.text_card(cv, label, 1370, 420, 220, WHITE, BLACK)
    Wd.text_card(cv, date, 1370, 540, 58, WHITE, BLACK)


def clock_815(cv, c):
    """The time on record for Hiroshima: 8:15 in the morning."""
    clock_face(cv, c, 8, 15, '8:15', '6 AUGUST 1945', ('9CB8C8', '6A8494'))
    Wd.text_card(cv, 'HIROSHIMA', 1370, 640, 58, WHITE, BLACK)


def clock_1102(cv, c):
    """The time on record for Nagasaki: 11:02 in the morning."""
    clock_face(cv, c, 11, 2, '11:02', '9 AUGUST 1945')
    Wd.text_card(cv, 'NAGASAKI', 1370, 640, 58, WHITE, BLACK)


def map_dist(cv, c):
    """Sketch only: how far he was from the centre of each explosion (about 3 km both times)."""
    night(cv)
    city = c.prm.get('city', 'HIROSHIMA')
    cx, cy = 620, 440
    for i, r in enumerate((100, 200, 300)):
        k = ease((c.k - 0.05 - i * 0.1) / 0.2)
        if k > 0:
            cv.drawCircle(cx, cy, r * k, P(WHITE if i == 2 else 0x66FFFFFF, 10 if i == 2 else 4))
    cv.drawCircle(cx, cy, 24, P(WHITE))
    cv.drawCircle(cx, cy, 24 + 50 * ((c.t * 1.6) % 1), P(Wd.alpha(WHITE, 1 - (c.t * 1.6) % 1), 6))
    Wd.text_card(cv, 'CENTRE', cx, cy - 46, 36, WHITE, BLACK)
    if c.k > 0.35:
        a = math.radians(32 if city == 'HIROSHIMA' else 205)
        px, py = cx + math.cos(a) * 300, cy + math.sin(a) * 300
        cv.drawLine(cx, cy, px, py, P(AMBER, 8))
        cv.drawCircle(px, py, 28, P(AMBER))
        cv.drawCircle(px, py, 28, P(BLACK, 6))
        Wd.text_card(cv, 'HIM', px + (0 if city == 'HIROSHIMA' else -20), py + 86, 64, AMBER, BLACK)
        Wd.text_card(cv, city, 1380, 330, 96, WHITE, BLACK)
        Wd.text_card(cv, 'ABOUT 3 KM', 1380, 470, 120, AMBER, BLACK)
        if city != 'HIROSHIMA':
            Wd.text_card(cv, 'AGAIN', 1380, 590, 96, WHITE, BLACK)
    Wd.text_card(cv, 'SKETCH, NOT A MAP', 1380, 760, 30, DIM, None)


def map_two(cv, c):
    """Sketch only: two cities and the rail journey between them. Positions are schematic."""
    night(cv)
    a, b = (1500, 330), (420, 610)
    k = ease(c.k / 0.6)
    rail_dots(cv, a, b, k, bow=70)
    cv.drawCircle(a[0], a[1], 28, P(WHITE))
    fit(cv, 'HIROSHIMA', a[0], a[1] - 110, 76, 620, WHITE)
    fit(cv, '6 AUG 1945', a[0], a[1] - 52, 46, 620, DIM)
    if k >= 1:
        cv.drawCircle(b[0], b[1], 28, P(AMBER))
        cv.drawCircle(b[0], b[1], 28 + 44 * ((c.t * 2) % 1), P(Wd.alpha(AMBER, 1 - (c.t * 2) % 1), 7))
    fit(cv, 'NAGASAKI', b[0], b[1] + 100, 76, 620, AMBER)
    fit(cv, 'HOME', b[0], b[1] + 156, 40, 620, DIM)
    Wd.text_card(cv, 'SKETCH, NOT TO SCALE', 960, 790, 30, DIM, None)


def cal_15(cv, c):
    """August 1945: the 6th, the 9th, and the 15th, when the war ended."""
    night(cv)
    Wd.text_card(cv, 'AUGUST 1945', 960, 200, 80, WHITE, BLACK)
    days = list(range(5, 17))
    x0, cw = 240, 120
    tags = {6: ('HIROSHIMA', WHITE), 9: ('NAGASAKI', WHITE), 15: ('THE WAR ENDS', AMBER)}
    sweep = lerp(9, 15, ease(c.k / 0.6))
    for i, d in enumerate(days):
        x = x0 + i * cw
        on = d in tags and (d < 15 or sweep >= 15)
        passed = 9 < d <= sweep
        col = h('EFE6CC') if not on else (AMBER if d == 15 else WHITE)
        cv.drawRoundRect(skia.Rect.MakeXYWH(x, 300, cw - 14, 150), 12, 12, P(col if on else (0x66FFFFFF if passed else 0x2AFFFFFF)))
        Wd.text_card(cv, str(d), x + (cw - 14) / 2, 404, 76, INK if on else WHITE, None)
        if on:
            lab, lc = tags[d]
            cv.drawLine(x + (cw - 14) / 2, 450, x + (cw - 14) / 2, 520, P(lc, 6))
            fit(cv, lab, max(260, min(1660, x + (cw - 14) / 2)), 590, 56 if d != 15 else 84, 520, lc)
    if sweep >= 15:
        Wd.text_card(cv, '6 DAYS LATER', 960, 760, 64, DIM, BLACK)


def card_1957(cv, c):
    """A record card drawn for the film: in 1957 he was registered as a survivor of Nagasaki only."""
    night(cv)
    sheet(cv, c, 960, 450, 1400, 640, -1.5, 'SURVIVOR RECORD   1957')
    Wd.text_card(cv, 'TSUTOMU YAMAGUCHI', 0, -150, 64, INK, None)
    for i, (city, date, on) in enumerate((('NAGASAKI', '9 AUG 1945', True), ('HIROSHIMA', '6 AUG 1945', False))):
        y = -20 + i * 150
        cv.drawRect(skia.Rect.MakeXYWH(-560, y - 64, 100, 100), P(INK, 8))
        Wd.text_card(cv, city, -420, y - 4, 70, INK if on else h('A89A7A'), None, center=False)
        Wd.text_card(cv, date, -420, y + 42, 36, TAN, None, center=False)
        if on and c.k > 0.3:
            cv.drawPath(poly([(-546, y - 16), (-514, y + 22), (-452, y - 72)], closed=False), P(RED, 18))
        if not on and c.k > 0.5:
            Wd.text_card(cv, 'NOT ON THE RECORD', 330, y + 10, 46, RED, None)
    cv.restore()
    if c.k > 0.6:
        stamp(cv, 'ONLY ONE', 1420, 300, 10, min(1, (c.k - 0.6) / 0.12), 96)


def count_165(cv, c):
    """About 165 people are thought to have been under both bombs (the number differs between sources)."""
    night(cv)
    n = int(round(lerp(0, 165, ease(c.k / 0.6))))
    for i in range(165):
        x, y = 150 + (i % 33) * 49.5, 480 + (i // 33) * 56
        cv.drawCircle(x, y, 15, P(AMBER if i < n else 0x33FFFFFF))
    Wd.text_card(cv, 'ABOUT ' + str(n), 960, 330, 190, WHITE, BLACK)
    Wd.text_card(cv, 'PEOPLE THOUGHT TO HAVE BEEN UNDER BOTH', 960, 420, 44, DIM, BLACK)
    Wd.text_card(cv, 'AN ESTIMATE; COUNTS DIFFER', 960, 800, 28, DIM, None)


def cert(cv, c):
    """A record card drawn for the film (not the real booklet): what Japan recognised in March 2009."""
    night(cv)
    sheet(cv, c, 960, 450, 1400, 640, 1.5, 'SURVIVOR RECORD   2009')
    Wd.text_card(cv, 'TSUTOMU YAMAGUCHI', 0, -150, 64, INK, None)
    for i, (city, date, at_) in enumerate((('NAGASAKI', '9 AUG 1945', 0.0), ('HIROSHIMA', '6 AUG 1945', 0.4))):
        y = -20 + i * 150
        cv.drawRect(skia.Rect.MakeXYWH(-560, y - 64, 100, 100), P(INK, 8))
        Wd.text_card(cv, city, -420, y - 4, 70, INK, None, center=False)
        Wd.text_card(cv, date, -420, y + 42, 36, TAN, None, center=False)
        if c.k > at_:
            cv.drawPath(poly([(-546, y - 16), (-514, y + 22), (-452, y - 72)], closed=False), P(RED, 18))
    if c.k > 0.5:
        Wd.text_card(cv, 'ADDED MARCH 2009', 330, 140, 46, RED, None)
    cv.restore()
    if c.k > 0.62:
        stamp(cv, 'BOTH', 1420, 300, -12, min(1, (c.k - 0.62) / 0.12), 130)


def board_true(cv, c):
    blueprint(cv)
    card(cv, 560, 450, 760, 600, 2)
    cv.save()
    cv.translate(560, 450)
    cv.rotate(2)
    photo(cv, 'old', 0, 6, 700, 520, (0.5, 0.4))
    cv.restore()
    note(cv, 1400, 250, 520, 150, -4, h('FFD866'), ['HIROSHIMA'], 60)
    note(cv, 1400, 450, 520, 150, 4, h('BFE0EC'), ['NAGASAKI'], 60)
    note(cv, 1400, 650, 520, 150, -3, PAPER, ['THE ONLY ONE ON RECORD'], 44)
    if c.lt > 0.35:
        stamp(cv, 'TRUE', 930, 520, -10, min(1, (c.lt - 0.35) / 0.12), 190)


def years(cv, c):
    """He was 29 in August 1945 and 93 when he died in January 2010."""
    night(cv)
    k = ease(c.k / 0.5)
    age = int(round(lerp(29, 93, k)))
    yr = int(round(lerp(1945, 2010, k)))
    for i in range(66):
        x = 300 + i * 20.3
        on = i <= (yr - 1945)
        cv.drawLine(x, 760, x, 760 - (70 if i % 5 == 0 else 40), P(AMBER if on else 0x55FFFFFF, 7))
    Wd.text_card(cv, 'AGE', 560, 400, 96, WHITE, BLACK)
    Wd.text_card(cv, str(age), 960, 520, 380, AMBER if age >= 93 else WHITE, BLACK)
    Wd.text_card(cv, str(yr), 1400, 400, 96, WHITE, BLACK)
    Wd.text_card(cv, '1945', 300, 820, 36, DIM, None)
    Wd.text_card(cv, '2010', 1620, 820, 36, DIM, None)


SHOTS = {f.__name__: f for f in (board_no, id_card, tanker_plan, map_trip, clock_815, clock_1102, map_dist, map_two, cal_15, card_1957,
                                 count_165, cert, board_true, years)}


# ------------------------------------------------------------------ overlays on 3D shots
def white(cv, a):
    if a > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(Wd.alpha(WHITE, min(1.0, a))))


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
    Wd.particles(cv, W, H, c.t, 60, 0x88E8D8C0, 4, size=(3, 8), drift=(-30, 70), wobble=30)


def ash_fade(cv, c):
    ash(cv, c)
    fade_white(cv, c)


def closed(cv, c):
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(480, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, BLACK)
        Wd.text_card(cv, 'CASE 010  CLOSED', 0, 90, 54, WHITE, BLACK)
        cv.restore()


OVER = dict(flash_city=flash_far, flash_road=flash_near, flash_office=flash_room, thrown=fade_white, dust_rise=ash_fade,
            aftermath=ash, found_three=ash, office_blast=fade_white, yama_stands=ash, signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (him bandaged before the white windows, Rook beside him) + a three-word hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('20508E'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(640, 0), (1280, 0)], [0x00000000, 0xD8000000])))
    Wd.text_card(cv, 'SURVIVED', 980, 230, 104, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'BOTH', 980, 410, 190, h('FFB000'), 0xFF000000)
    Wd.text_card(cv, 'BOMBS', 980, 570, 150, 0xFFFFFFFF, 0xFF000000)
