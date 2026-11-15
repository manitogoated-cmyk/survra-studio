"""Case 011, the full case file - Roy Sullivan. The story is filmed in 3D (world3d.py). This file holds the flat
inserts for the 16:9 film (the seven-bolt counter, Rook's case board on a park noticeboard, a ranger file card, three
small drawings, the 27 quiet years, the nicknames, the odds, the list of the seven strikes, the advice), the 2D overlays
drawn on top of 3D shots (rain, the year counter, the sign-off) and the thumbnail. Every card is a drawing made for this film; none of them
reproduces a real document, photograph, badge or logo."""
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
ORANGE, AMBER, PAPER, RED, PINE = h('FF7A1A'), h('FFB000'), h('EFE6CC'), h('D8362A'), h('1E3A2C')
BOLT = h('FFE45A')


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


def zigzag(cx, cy, s):
    """The outline of a lightning bolt about s tall, centred on (cx, cy)."""
    pts = [(0.12, -0.5), (-0.3, 0.06), (-0.04, 0.06), (-0.2, 0.5), (0.32, -0.12), (0.05, -0.12), (0.3, -0.5)]
    return poly([(cx + x * s, cy + y * s) for x, y in pts])


def bolt_icon(cv, cx, cy, s, col=BOLT, a=1.0):
    cv.drawPath(zigzag(cx + s * 0.03, cy + s * 0.04, s), P(0xFF000000, s * 0.1, a=a))
    cv.drawPath(zigzag(cx, cy, s), P(col, a=a))
    cv.drawPath(zigzag(cx, cy, s), P(0xFF1B1730, s * 0.035, a=a))


def stormy(cv, top='1C2940', bot='0A101C'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    for i in range(9):
        Wd.cloud(cv, 110 + i * 220, 130 + (i % 3) * 60, 1.9, h('2C3A54'), h('222E46'))


def noticeboard(cv):
    """Rook's board for this case: a park noticeboard, green felt in a timber frame, faint contour lines."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('5A4630')))
    for i in range(0, H, 60):
        cv.drawLine(0, i, W, i, P(0x22000000, 3))
    cv.drawRect(skia.Rect.MakeLTRB(40, 40, W - 40, H - 40), P(PINE))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(40, 40, W - 40, H - 40))
    for i in range(9):
        cv.drawOval(skia.Rect.MakeXYWH(1300 - i * 90, 620 - i * 40, 300 + i * 180, 200 + i * 80), P(0x1FFFFFFF, 3))
    for i in range(5):
        cv.drawOval(skia.Rect.MakeXYWH(40 - i * 60, 120 - i * 40, 220 + i * 130, 150 + i * 80), P(0x1FFFFFFF, 3))
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(40, 40, W - 40, H - 40), P(h('3A2C1E'), 14))
    for x, y in ((84, 84), (W - 84, 84), (84, H - 84), (W - 84, H - 84)):
        cv.drawCircle(x, y, 12, P(h('C89A3A')))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x66000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, pin=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if pin:
        cv.drawCircle(0, -h_ / 2 + 30, 20, P(0x66000000))
        cv.drawCircle(-4, -h_ / 2 + 24, 20, P(ORANGE))
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=64):
    card(cv, x, y, w_, h_, ang, col, pin=False)
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
    cv.drawRoundRect(box, 18, 18, P(0xEE0E1E16))
    cv.drawRoundRect(box, 18, 18, P(col, 18))
    Wd.text_card(cv, s, 0, size * 0.18, size, col, None)
    cv.restore()


def left(cv, s, x, y, size, col=0xFFFFFFFF, stroke=0xFF000000, maxw=None):
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
    if maxw and w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, col, stroke, center=False)


# ------------------------------------------------------------------ flat inserts (1920 x 1080; captions sit at y 930)
def counter7(cv, c):
    """Seven bolts come down one after another, then the number."""
    stormy(cv)
    n = min(7, int(c.k / 0.07) + 1)
    for i in range(n):
        age = c.k - i * 0.07
        drop = 1 - ease(age / 0.06)
        bolt_icon(cv, 240 + i * 240, 250 + (i % 2) * 50 - 500 * drop, 230)
        if age < 0.08:
            cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFFFFFFF, a=0.35 * (1 - age / 0.08)))
    if c.k > 0.5:
        k = min(1.0, (c.k - 0.5) / 0.1)
        cv.save()
        cv.translate(760, 640)
        cv.scale(1.9 - 0.9 * k, 1.9 - 0.9 * k)
        Wd.text_card(cv, '7', 0, 120, 360, BOLT, 0xFF000000)
        cv.restore()
        left(cv, 'STRIKES', 900, 640, 130)
        left(cv, 'ONE MAN', 900, 770, 100, AMBER)
    Wd.rain(cv, W, H, c.t, density=120, c=0x33CFE6FF, slant=0.3, speed=2400, length=64)


def board_no(cv, c):
    noticeboard(cv)
    k = min(1, c.lt / 0.18)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(560, 430)
    cv.scale(s, s)
    card(cv, 0, 0, 860, 600, -3)
    cv.rotate(-3)
    photo(cv, 'tower', 0, 20, 790, 490, (0.5, 0.3))
    cv.restore()
    if c.lt > 0.14:
        cv.drawLine(1000, 420, 1160, 330, P(RED, 8))
        note(cv, 1420, 300, 660, 200, 3, h('FFD866'), ['7 STRIKES?'], 104)
    for i in range(7):
        if c.lt > 0.2 + i * 0.03:
            bolt_icon(cv, 1130 + i * 100, 560, 120)
    if c.k > 0.5:
        stamp(cv, 'NO CHANCE', 1100, 520, -10, min(1, (c.k - 0.5) / 0.14), 150)


def id_card(cv, c):
    """A ranger's file card drawn for the film. The portrait is a silhouette, not a photograph of him."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E3A2C')), (1, h('0E1E16'))])
    k = ease(c.lt / 0.25)
    cv.save()
    cv.translate(960, 440 + 300 * (1 - k))
    cv.rotate(-1.2)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-738, -330, 1500, 680), 22, 22, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-750, -350, 1500, 680), 22, 22, P(PAPER))
    cv.drawRect(skia.Rect.MakeXYWH(-750, -350, 1500, 96), P(h('24352C')))
    left(cv, 'RANGER FILE', -710, -284, 54, BOLT, None)
    cv.drawRect(skia.Rect.MakeXYWH(-700, -210, 340, 420), P(h('B8C8B4')))
    cv.drawRect(skia.Rect.MakeXYWH(-700, -210, 340, 420), P(INK, 6))
    dk = h('3A4A3C')
    cv.drawCircle(-530, -40, 84, P(dk))
    cv.drawPath(poly([(-668, 210), (-648, 90), (-584, 54), (-476, 54), (-412, 90), (-392, 210)]), P(dk))
    cv.drawOval(skia.Rect.MakeXYWH(-680, -122, 300, 44), P(dk))
    cv.drawPath(poly([(-608, -104), (-590, -176), (-470, -176), (-452, -104)]), P(dk))
    rows = (('NAME', 'ROY C. SULLIVAN', 0.12), ('BORN', 'VIRGINIA, 1912', 0.3), ('WORK', 'PARK RANGER', 0.48))
    for i, (lab, val, at_) in enumerate(rows):
        y = -170 + i * 122
        left(cv, lab, -310, y, 30, h('7A6A48'), None)
        if c.k > at_:
            left(cv, val, -310, y + 62, 60, INK, None, 980)
    cv.drawLine(-310, 196, 700, 196, P(h('7A6A48'), 4))
    if c.k > 0.64:
        left(cv, 'SHENANDOAH NATIONAL PARK, BLUE RIDGE MOUNTAINS', -310, 250, 44, h('2E6A3A'), None, 1010)
    left(cv, 'CARD DRAWN FOR THIS FILM', -310, 304, 24, h('9A8A68'), None)
    cv.restore()


def boot(cv, x, y, s, hole):
    """A ranger boot seen from the side, toe to the right. hole (0..1) burns through the toe cap."""
    pts = [(-1.0, -1.25), (-0.25, -1.25), (-0.2, -0.3), (0.55, -0.12), (1.05, 0.1), (1.12, 0.45), (-1.02, 0.45)]
    cv.drawPath(poly([(x + px * s + 10, y + py * s + 14) for px, py in pts]), P(0x66000000))
    cv.drawPath(poly([(x + px * s, y + py * s) for px, py in pts]), P(h('4A3424')))
    cv.drawPath(poly([(x + px * s, y + py * s) for px, py in pts]), P(INK, 10))
    cv.drawRect(skia.Rect.MakeLTRB(x - 1.06 * s, y + 0.45 * s, x + 1.16 * s, y + 0.62 * s), P(h('1E1A18')))
    cv.drawRect(skia.Rect.MakeLTRB(x - 1.06 * s, y + 0.45 * s, x - 0.55 * s, y + 0.78 * s), P(h('1E1A18')))
    for i in range(4):
        cv.drawLine(x - 0.2 * s, y + (-1.05 + i * 0.22) * s, x - 0.02 * s, y + (-0.98 + i * 0.22) * s, P(h('C8B890'), 8))
    if hole > 0:
        hx, hy = x + 0.8 * s, y + 0.12 * s
        r = 0.2 * s * hole
        cv.drawCircle(hx, hy, r * 1.25, P(h('1A1410')))
        cv.drawCircle(hx, hy, r * 0.8, P(ORANGE, a=0.9))
        cv.drawCircle(hx, hy, r * 0.42, P(BOLT))


def toe(cv, c):
    """Strike 1, 1942: a burn down his right leg, a lost big toenail, a hole in his shoe."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('24354A')), (1, h('101826'))])
    k = ease(c.lt / 0.2)
    hit = ease((c.lt - 0.22) / 0.14)
    left(cv, 'STRIKE 1', 110, 190, 130, BOLT)
    left(cv, 'APRIL 1942', 110, 280, 64)
    cv.drawOval(skia.Rect.MakeXYWH(210, 740, 640, 80), P(0x55000000))
    boot(cv, 520, 580 + 300 * (1 - k), 250, hit)
    if hit > 0:
        bolt_icon(cv, 800, 330, 300, a=max(0.0, 1 - (c.lt - 0.22) / 0.5))
        for i in range(4):
            u = (c.t * 0.9 + i * 0.25) % 1
            cv.drawCircle(726 + 30 * math.sin(c.t * 3 + i), 600 - 240 * u, 18 + 42 * u, P(0xFFC8C8CC, a=0.5 * (1 - u)))
    for i, (lab, val) in enumerate((('RIGHT LEG', 'BURNED'), ('BIG TOENAIL', 'GONE'), ('SHOE', 'A HOLE IN IT'))):
        if c.k > 0.3 + i * 0.17:
            y = 330 + i * 150
            left(cv, lab, 1060, y, 50)
            left(cv, val, 1060, y + 76, 84, AMBER, 0xFF000000, 760)


def years27(cv, c):
    """Twenty-seven years with no strike: the year rolls from 1942 to 1969 under a clear sky."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3E6C9C')), (1, h('9CC0D8'))])
    for i in range(5):
        Wd.cloud(cv, (200 + i * 430 + c.t * 40) % 2200 - 140, 170 + (i % 2) * 90, 1.5, 0xFFFFFFFF, h('D8E4EE'))
    cv.drawPath(poly([(0, 1080), (0, 800), (300, 700), (620, 790), (900, 690), (1250, 800), (1560, 710), (1920, 790), (1920, 1080)]), P(h('2E4A3A')))
    cv.drawPath(poly([(0, 1080), (0, 880), (400, 800), (800, 880), (1200, 810), (1600, 880), (1920, 830), (1920, 1080)]), P(h('1E3428')))
    yr = 1942 + int(27 * ease(c.k / 0.6))
    Wd.text_card(cv, str(yr), 620, 520, 300, 0xFFFFFFFF, 0xFF000000)
    if c.k > 0.25:
        left(cv, '27 YEARS', 1100, 420, 130, AMBER)
    if c.k > 0.62:
        left(cv, 'NOT ONE STRIKE', 1100, 540, 80)


def brows(cv, c):
    """Strike 2, 1969: knocked unconscious, and his eyebrows."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A4656')), (1, h('181E28'))])
    gone = ease((c.lt - 0.3) / 0.4)
    left(cv, 'STRIKE 2', 1060, 250, 130, BOLT)
    left(cv, 'JULY 1969', 1060, 340, 64)
    cx, cy = 560, 560
    s = 0.8
    cv.save()
    cv.translate(cx, cy)
    cv.scale(s, s)
    cv.drawOval(skia.Rect.MakeXYWH(-230, -250, 460, 540), P(h('E2B48C')))
    cv.drawOval(skia.Rect.MakeXYWH(-230, -250, 460, 540), P(INK, 10))
    cv.drawOval(skia.Rect.MakeXYWH(-430, -300, 860, 110), P(h('8A7450')))
    cv.drawOval(skia.Rect.MakeXYWH(-430, -300, 860, 110), P(INK, 10))
    cv.drawPath(poly([(-210, -250), (-170, -470), (170, -470), (210, -250)]), P(h('8A7450')))
    cv.drawPath(poly([(-210, -250), (-170, -470), (170, -470), (210, -250)]), P(INK, 10))
    cv.drawRect(skia.Rect.MakeLTRB(-206, -300, 206, -256), P(h('3A2E22')))
    for sd in (-1, 1):
        ex = sd * 100
        cv.drawOval(skia.Rect.MakeXYWH(ex - 50, -60 - 14 * gone, 100, 84 + 28 * gone), P(0xFFFFFFFF))
        cv.drawOval(skia.Rect.MakeXYWH(ex - 50, -60 - 14 * gone, 100, 84 + 28 * gone), P(INK, 8))
        cv.drawCircle(ex, -16, 20, P(INK))
        if gone < 1:
            cv.drawLine(ex - 66, -112 - sd * 8, ex + 66, -112 + sd * 8, P(h('8A8A86'), 30, a=1 - gone))
        if gone > 0.1:
            for i in range(3):
                u = (c.t * 1.3 + i * 0.33) % 1
                cv.drawCircle(ex + 24 * math.sin(c.t * 4 + i + sd), -120 - 190 * u, 16 + 34 * u, P(0xFFD8D8DC, a=0.55 * (1 - u) * gone))
    cv.drawOval(skia.Rect.MakeXYWH(-60, 120, 120, 30 + 50 * gone), P(h('2A1218')))
    cv.restore()
    if c.k > 0.3:
        left(cv, 'KNOCKED OUT', 1060, 500, 84, AMBER, 0xFF000000, 780)
    if c.k > 0.55:
        left(cv, 'EYEBROWS: GONE', 1060, 620, 84, AMBER, 0xFF000000, 780)


def names(cv, c):
    """The nicknames, on two luggage tags pinned to the board. Drawn for the film."""
    noticeboard(cv)
    left(cv, 'THEY CALL HIM', 150, 190, 60, 0xFFFFFFFF)
    for i, (txt, y, ang, col, at_) in enumerate((('THE HUMAN LIGHTNING ROD', 380, -3, h('FFD866'), 0.12), ('THE SPARK RANGER', 660, 2.5, h('BFE0EC'), 0.5))):
        if c.k < at_:
            continue
        k = ease((c.k - at_) / 0.12)
        cv.save()
        cv.translate(960 + (i * 2 - 1) * -60, y - 120 * (1 - k))
        cv.rotate(ang)
        cv.drawPath(poly([(-700, -100), (640, -100), (720, 0), (640, 100), (-700, 100)]), P(0x66000000))
        cv.save()
        cv.translate(-12, -14)
        cv.drawPath(poly([(-700, -100), (640, -100), (720, 0), (640, 100), (-700, 100)]), P(col))
        cv.drawCircle(640, 0, 22, P(PINE))
        fit(cv, txt, -40, 36, 104, 1180, INK, None)
        cv.restore()
        cv.restore()
        bolt_icon(cv, 1690, y - 10, 170)


def odds(cv, c):
    """Guinness's figure: about 1 in 10,000 to be struck once in an 80-year life. Ten thousand dots, one bolt."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16243A')), (1, h('0A101C'))])
    cols, rows_ = 125, 80
    x0, y0, dx, dy = 110, 110, 6.6, 8.6
    n = int(cols * ease(c.k / 0.35))
    pa = P(0xFF6A7E9C)
    for j in range(rows_):
        for i in range(n):
            cv.drawRect(skia.Rect.MakeXYWH(x0 + i * dx, y0 + j * dy, 3.4, 4.6), pa)
    if c.k > 0.38:
        bx, by = x0 + 71 * dx, y0 + 33 * dy
        pulse = 1 + 0.25 * math.sin(c.t * 9)
        cv.drawCircle(bx, by, 26 * pulse, P(BOLT, 5))
        bolt_icon(cv, bx, by, 60)
    left(cv, 'STRUCK ONCE, IN A LIFETIME', 1010, 250, 46)
    if c.k > 0.2:
        left(cv, '1 IN', 1010, 400, 110)
        left(cv, '10,000', 1010, 560, 190, BOLT)
    left(cv, 'GUINNESS WORLD RECORDS, FOR AN 80-YEAR LIFE', 1010, 630, 28, h('9AAAC8'), None)
    if c.k > 0.72:
        k = min(1.0, (c.k - 0.72) / 0.1)
        cv.save()
        cv.translate(1380, 770)
        cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
        Wd.text_card(cv, 'ROY: 7 TIMES', 0, 0, 100, AMBER, 0xFF000000)
        cv.restore()


ROWS = (('APR 1942', 'LEG, TOENAIL'), ('JUL 1969', 'KNOCKED OUT, EYEBROWS'), ('JUL 1970', 'LEFT SHOULDER'), ('APR 1972', 'HAIR ON FIRE'),
        ('AUG 1973', 'HAIR AGAIN, LEGS'), ('JUN 1976', 'ANKLE, HAIR'), ('JUN 1977', 'CHEST, STOMACH'))


def list7(cv, c):
    """The seven strikes, date and damage, on a card drawn for this film."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E3A2C')), (1, h('0E1E16'))])
    k = ease(c.lt / 0.2)
    cv.save()
    cv.translate(960, 430 + 300 * (1 - k))
    cv.rotate(-1.0)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-688, -372, 1400, 780), 22, 22, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-700, -390, 1400, 780), 22, 22, P(PAPER))
    cv.drawRect(skia.Rect.MakeXYWH(-700, -390, 1400, 100), P(h('24352C')))
    left(cv, 'STRUCK BY LIGHTNING: THE DATE AND THE DAMAGE', -660, -322, 46, BOLT, None, 1320)
    for i, (yr, what) in enumerate(ROWS):
        y = -220 + i * 86
        on = c.k > 0.08 + i * 0.07
        cv.drawLine(-660, y + 26, 660, y + 26, P(h('C8BC98'), 3))
        left(cv, str(i + 1), -650, y, 46, h('8A7A58'), None)
        left(cv, yr, -580, y, 54, INK, None)
        if on:
            left(cv, what, -250, y - 2, 50, h('8A2A1E'), None, 760)
            cv.drawPath(poly([(580, y - 22), (604, y + 6), (652, y - 52)], closed=False), P(h('2E7A3A'), 13))
    left(cv, 'DATES AND INJURIES AS REPORTED BY GUINNESS WORLD RECORDS. CARD DRAWN FOR THIS FILM.', -660, 368, 24, h('7A6A48'), None)
    cv.restore()
    if c.k > 0.66:
        stamp(cv, '7 OF 7', 1560, 650, -10, min(1, (c.k - 0.66) / 0.1), 120, h('2E9A4A'))


def board_true(cv, c):
    noticeboard(cv)
    card(cv, 560, 420, 760, 640, 2)
    cv.save()
    cv.translate(560, 420)
    cv.rotate(2)
    photo(cv, 'roy', 0, 20, 690, 530, (0.5, 0.45))
    cv.restore()
    note(cv, 1400, 250, 560, 170, -4, h('FFD866'), ['1942 - 1977'], 84)
    note(cv, 1420, 500, 620, 170, 3, h('BFE0EC'), ['STRUCK 7 TIMES'], 76)
    if c.lt > 0.3:
        stamp(cv, 'TRUE', 1040, 640, -10, min(1, (c.lt - 0.3) / 0.12), 190)


def advice(cv, c):
    """The one piece of advice: when you hear thunder, go indoors."""
    stormy(cv, '202E48', '0A101C')
    cv.drawPath(poly([(250, 760), (250, 480), (470, 320), (690, 480), (690, 760)]), P(h('2E3E5A')))
    cv.drawPath(poly([(210, 500), (470, 300), (730, 500), (700, 530), (470, 356), (240, 530)]), P(h('46587A')))
    cv.drawRect(skia.Rect.MakeXYWH(410, 580, 120, 180), P(h('FFD890')))
    cv.drawRect(skia.Rect.MakeXYWH(560, 540, 80, 80), P(h('FFD890'), a=0.5 + 0.5 * ease(c.k / 0.3)))
    f = 1.0 if (c.lt * 1.1) % 1 < 0.12 else 0.0
    bolt_icon(cv, 1650, 300, 330, a=0.35 + 0.65 * f)
    if f:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFFFFFFF, a=0.12))
    left(cv, 'HEAR THUNDER?', 800, 440, 104)
    if c.k > 0.35:
        k = min(1.0, (c.k - 0.35) / 0.12)
        cv.save()
        cv.translate(800, 620)
        cv.scale(1.25 - 0.25 * k, 1.25 - 0.25 * k)
        left(cv, 'GO INDOORS.', 0, 0, 150, AMBER)
        cv.restore()
    Wd.rain(cv, W, H, c.t, density=120, c=0x33CFE6FF, slant=0.3, speed=2400, length=64)


SHOTS = {f.__name__: f for f in (counter7, board_no, id_card, toe, years27, brows, names, odds, list7, board_true, advice)}


# ------------------------------------------------------------------ overlays on 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=170, c=0x40CFE6FF, slant=0.3, speed=2500, length=70)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, density=70, c=0x2ACFE6FF, slant=0.2, speed=2100, length=50)


def years(cv, c):
    """The 27 quiet years, counted in the corner while the sun goes round."""
    yr = 1942 + int(27 * ease(c.k / 0.9))
    cv.drawRoundRect(skia.Rect.MakeXYWH(70, 60, 390, 150), 18, 18, P(0xCC0B1020))
    Wd.text_card(cv, str(yr), 265, 172, 120, BOLT, 0xFF000000)


def closed(cv, c):
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(1400, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 170, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 011  CLOSED', 0, 96, 60, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(roy_steam=drizzle, water_can=drizzle, rook_can=drizzle, bolt_tower=rain, tower_wide=rain, roy_tower=drizzle, tower_hit=drizzle,
            roy_runs=rain, rook_gate=rain, rook_collar=rain, truck_drive=rain, bolt_truck=rain, rook_truck=drizzle, yard_wide=drizzle,
            yard_hit=rain, patrol_hit=drizzle, trail_hit=rain, roy_hop=drizzle, bolt_pond=rain, pond_wide=drizzle, pond_hit=rain,
            roy_burns=drizzle, signoff=closed, tower_fire=rain, leg_cu=drizzle, cab_ride=rain, truck_out=rain, patrol_watch=drizzle,
            yard_after=drizzle, pond_gone=drizzle, look_years=years, look_alone=drizzle, rook_sits=drizzle, wash_hit=rain, wash_after=drizzle)


def THUMB(cv, c):
    """1280x720: the 3D still (the bolt on his hat, Rook ducking) and a three-word hook on the right."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('1E2A44'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(600, 0), (1280, 0)], [0x00000000, 0xE0000000])))
    Wd.text_card(cv, 'STRUCK', 975, 220, 128, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, '7 TIMES', 975, 400, 150, BOLT, 0xFF000000)
    Wd.text_card(cv, 'SURVIVED', 975, 560, 112, 0xFFFFFFFF, 0xFF000000)
