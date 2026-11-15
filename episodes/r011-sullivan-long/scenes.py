"""Case 011 - Roy Sullivan. The story is filmed in 3D (world3d.py). This file holds the flat inserts (the seven-bolt
counter, Rook's case board on a park noticeboard, two small drawings, the list of the seven strikes) and the 2D
overlays drawn on top of 3D shots (rain, the sign-off). Every card is a drawing made for this film; none of them
reproduces a real document, photograph, badge or logo."""
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
    for i in range(7):
        Wd.cloud(cv, 120 + i * 160, 150 + (i % 3) * 70, 1.7, h('2C3A54'), h('222E46'))


def noticeboard(cv):
    """Rook's board for this case: a park noticeboard, green felt in a timber frame, faint contour lines."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('5A4630')))
    for i in range(0, H, 64):
        cv.drawLine(0, i, W, i, P(0x22000000, 3))
    cv.drawRect(skia.Rect.MakeLTRB(46, 46, W - 46, H - 46), P(PINE))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(46, 46, W - 46, H - 46))
    for i in range(9):
        cv.drawOval(skia.Rect.MakeXYWH(700 - i * 70, 1420 - i * 46, 300 + i * 150, 200 + i * 96), P(0x1FFFFFFF, 3))
    for i in range(5):
        cv.drawOval(skia.Rect.MakeXYWH(40 - i * 50, 150 - i * 40, 200 + i * 110, 150 + i * 80), P(0x1FFFFFFF, 3))
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(46, 46, W - 46, H - 46), P(h('3A2C1E'), 14))
    for x, y in ((90, 90), (W - 90, 90), (90, H - 90), (W - 90, H - 90)):
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


# ------------------------------------------------------------------ flat inserts
def counter7(cv, c):
    """Seven bolts come down one after another, then the number."""
    stormy(cv)
    n = min(7, int(c.k / 0.075) + 1)
    for i in range(n):
        age = c.k - i * 0.075
        drop = 1 - ease(age / 0.06)
        x = 150 + i * 130
        y = 400 + (i % 2) * 60 - 500 * drop
        bolt_icon(cv, x, y, 220)
        if age < 0.08:
            cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFFFFFFF, a=0.35 * (1 - age / 0.08)))
    if c.k > 0.52:
        k = min(1.0, (c.k - 0.52) / 0.1)
        cv.save()
        cv.translate(540, 940)
        cv.scale(1.9 - 0.9 * k, 1.9 - 0.9 * k)
        Wd.text_card(cv, '7', 0, 150, 440, BOLT, 0xFF000000)
        cv.restore()
        Wd.text_card(cv, 'ONE MAN', 540, 1560, 96, 0xFFFFFFFF, 0xFF000000)
    Wd.rain(cv, W, H, c.t, density=80, c=0x33CFE6FF, slant=0.3, speed=2400, length=64)


def board_no(cv, c):
    noticeboard(cv)
    k = min(1, c.lt / 0.18)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 640)
    cv.scale(s, s)
    card(cv, 0, 0, 760, 640, -3)
    cv.rotate(-3)
    photo(cv, 'tower', 0, 24, 690, 520, (0.5, 0.3))
    cv.restore()
    if c.lt > 0.14:
        cv.drawLine(540, 950, 540, 1040, P(RED, 8))
        note(cv, 540, 1130, 640, 190, 3, h('FFD866'), ['7 STRIKES?'], 96)
    for i in range(7):
        if c.lt > 0.2 + i * 0.03:
            bolt_icon(cv, 200 + i * 114, 1560, 130)
    if c.k > 0.55:
        stamp(cv, 'NO CHANCE', 540, 700, -12, min(1, (c.k - 0.55) / 0.14), 132)


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
    """Strike 1, 1942: Guinness lists a lost big toenail; other accounts add a hole in his shoe."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('24354A')), (1, h('101826'))])
    k = ease(c.lt / 0.2)
    hit = ease((c.lt - 0.22) / 0.14)
    Wd.text_card(cv, 'STRIKE 1', 540, 330, 150, BOLT, 0xFF000000)
    Wd.text_card(cv, '1942', 540, 440, 76, 0xFFFFFFFF, 0xFF000000)
    cv.drawOval(skia.Rect.MakeXYWH(180, 1040, 720, 90), P(0x55000000))
    boot(cv, 500, 820 + 300 * (1 - k), 300, hit)
    if hit > 0:
        bolt_icon(cv, 800, 560, 360, a=max(0.0, 1 - (c.lt - 0.22) / 0.5))
        for i in range(4):
            u = (c.t * 0.9 + i * 0.25) % 1
            cv.drawCircle(748 + 30 * math.sin(c.t * 3 + i), 840 - 260 * u, 20 + 46 * u, P(0xFFC8C8CC, a=0.5 * (1 - u)))
    if c.k > 0.42:
        Wd.text_card(cv, 'LOST:', 540, 1500, 70, 0xFFFFFFFF, 0xFF000000)
        fit(cv, 'ONE BIG TOENAIL', 540, 1610, 100, 960, AMBER)


def brows(cv, c):
    """Strike 2, 1969: Guinness lists his eyebrows."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A4656')), (1, h('181E28'))])
    gone = ease((c.lt - 0.2) / 0.3)
    Wd.text_card(cv, 'STRIKE 2', 540, 330, 150, BOLT, 0xFF000000)
    Wd.text_card(cv, '1969', 540, 440, 76, 0xFFFFFFFF, 0xFF000000)
    cx, cy = 540, 990
    cv.drawOval(skia.Rect.MakeXYWH(cx - 230, cy - 250, 460, 540), P(h('E2B48C')))
    cv.drawOval(skia.Rect.MakeXYWH(cx - 230, cy - 250, 460, 540), P(INK, 10))
    cv.drawOval(skia.Rect.MakeXYWH(cx - 430, cy - 300, 860, 110), P(h('8A7450')))
    cv.drawOval(skia.Rect.MakeXYWH(cx - 430, cy - 300, 860, 110), P(INK, 10))
    cv.drawPath(poly([(cx - 210, cy - 250), (cx - 170, cy - 470), (cx + 170, cy - 470), (cx + 210, cy - 250)]), P(h('8A7450')))
    cv.drawPath(poly([(cx - 210, cy - 250), (cx - 170, cy - 470), (cx + 170, cy - 470), (cx + 210, cy - 250)]), P(INK, 10))
    cv.drawRect(skia.Rect.MakeLTRB(cx - 206, cy - 300, cx + 206, cy - 256), P(h('3A2E22')))
    for s in (-1, 1):
        ex = cx + s * 100
        cv.drawOval(skia.Rect.MakeXYWH(ex - 50, cy - 60 - 14 * gone, 100, 84 + 28 * gone), P(0xFFFFFFFF))
        cv.drawOval(skia.Rect.MakeXYWH(ex - 50, cy - 60 - 14 * gone, 100, 84 + 28 * gone), P(INK, 8))
        cv.drawCircle(ex, cy - 16, 20, P(INK))
        if gone < 1:
            cv.drawLine(ex - 66, cy - 112 - s * 8, ex + 66, cy - 112 + s * 8, P(h('5A3A22'), 30, a=1 - gone))
        if gone > 0.1:
            for i in range(3):
                u = (c.t * 1.3 + i * 0.33) % 1
                cv.drawCircle(ex + 24 * math.sin(c.t * 4 + i + s), cy - 120 - 190 * u, 16 + 34 * u, P(0xFFD8D8DC, a=0.55 * (1 - u) * gone))
    cv.drawOval(skia.Rect.MakeXYWH(cx - 60, cy + 120, 120, 30 + 50 * gone), P(h('2A1218')))
    if c.k > 0.45:
        Wd.text_card(cv, 'LOST:', 540, 1500, 70, 0xFFFFFFFF, 0xFF000000)
        fit(cv, 'BOTH EYEBROWS', 540, 1610, 100, 960, AMBER)


ROWS = (('1942', 'TOENAIL'), ('1969', 'EYEBROWS'), ('1970', 'SHOULDER'), ('1972', 'HAIR ON FIRE'), ('1973', 'HAIR AGAIN, LEGS'),
        ('1976', 'ANKLE'), ('1977', 'CHEST, STOMACH'))


def list7(cv, c):
    """The seven strikes as Guinness World Records lists them, on a card drawn for this film."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E3A2C')), (1, h('0E1E16'))])
    k = ease(c.lt / 0.2)
    cv.save()
    cv.translate(540, 700 + 420 * (1 - k))
    cv.rotate(-1.5)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-448, -510, 920, 1040), 22, 22, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-460, -530, 920, 1040), 22, 22, P(PAPER))
    cv.drawRect(skia.Rect.MakeXYWH(-460, -530, 920, 130), P(h('24352C')))
    Wd.text_card(cv, 'STRUCK BY LIGHTNING', 0, -440, 64, BOLT, None)
    for i, (yr, what) in enumerate(ROWS):
        y = -330 + i * 104
        on = c.k > 0.1 + i * 0.075
        cv.drawLine(-420, y + 34, 420, y + 34, P(h('C8BC98'), 3))
        Wd.text_card(cv, str(i + 1), -400, y, 54, h('8A7A58'), None, center=False)
        Wd.text_card(cv, yr, -330, y, 62, INK, None, center=False)
        if on:
            f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), 50)
            size = min(50, 50 * 400 / f.measureText(what))
            Wd.text_card(cv, what, -140, y - 4, size, h('8A2A1E'), None, center=False)
            cv.drawPath(poly([(342, y - 26), (368, y + 4), (420, y - 60)], closed=False), P(h('2E7A3A'), 14))
    Wd.text_card(cv, 'AS LISTED BY GUINNESS WORLD RECORDS', 0, 440, 30, h('6A5A3A'), None)
    Wd.text_card(cv, 'CARD DRAWN FOR THIS FILM', 0, 482, 26, h('9A8A68'), None)
    cv.restore()
    if c.k > 0.7:
        stamp(cv, '7 OF 7', 700, 1500, -10, min(1, (c.k - 0.7) / 0.1), 120, h('2E9A4A'))


def board_true(cv, c):
    noticeboard(cv)
    card(cv, 540, 650, 680, 780, 2)
    cv.save()
    cv.translate(540, 650)
    cv.rotate(2)
    photo(cv, 'roy', 0, 24, 610, 660, (0.5, 0.45))
    cv.restore()
    note(cv, 280, 1520, 420, 150, -5, h('FFD866'), ['1942 - 1977'], 60)
    note(cv, 800, 1530, 420, 150, 4, h('BFE0EC'), ['STRUCK 7 TIMES'], 60)
    if c.lt > 0.3:
        stamp(cv, 'TRUE', 560, 1010, -10, min(1, (c.lt - 0.3) / 0.12), 170)


SHOTS = {f.__name__: f for f in (counter7, board_no, toe, brows, list7, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=110, c=0x40CFE6FF, slant=0.3, speed=2500, length=70)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, density=45, c=0x2ACFE6FF, slant=0.2, speed=2100, length=50)


def closed(cv, c):
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 011  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(roy_steam=drizzle, water_can=drizzle, rook_can=drizzle, bolt_tower=rain, tower_wide=rain, roy_tower=drizzle, tower_hit=drizzle, roy_runs=rain, rook_gate=rain, rook_collar=rain,
            truck_drive=rain, bolt_truck=rain, rook_truck=drizzle, yard_wide=drizzle, yard_hit=rain, patrol_hit=drizzle,
            trail_hit=rain, roy_hop=drizzle, bolt_pond=rain, pond_wide=drizzle, pond_hit=rain, roy_burns=drizzle, signoff=closed)
