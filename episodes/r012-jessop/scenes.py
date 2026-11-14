"""Case 012 - Violet Jessop. The story is filmed in 3D (world3d.py). This file holds the flat inserts (the three-ship
counter, Rook's case board on a ship's notice board, the list of the three ships) and the 2D overlays drawn on top of
3D shots (the sign-off). Every card is a drawing made for this film; none of them reproduces a real document,
photograph, flag, badge or logo."""
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
ORANGE, AMBER, PAPER, RED, NAVY = h('FF7A1A'), h('FFB000'), h('F0E8D2'), h('D8362A'), h('16263E')
BUFF, FOAM = h('E0A848'), h('DCEBF4')


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


def liner_icon(cv, cx, cy, w, hull=0xFF14161C, upper=0xFFE8E4D8, a=1.0, tilt=0.0):
    """Side view of a four-funnel liner about w wide, bow to the right. A plain drawing, no markings."""
    u = w / 100.0
    cv.save()
    cv.translate(cx, cy)
    cv.rotate(tilt)
    cv.drawPath(poly([(-50 * u, -4 * u), (47 * u, -4 * u), (50 * u, -6 * u), (46 * u, 5 * u), (-46 * u, 5 * u), (-50 * u, -1 * u)]), P(hull, a=a))
    cv.drawRect(skia.Rect.MakeLTRB(-46 * u, 3.4 * u, 46 * u, 5 * u), P(h('8A2E28'), a=a))
    cv.drawRect(skia.Rect.MakeLTRB(-34 * u, -8.5 * u, 30 * u, -4 * u), P(upper, a=a))
    cv.drawRect(skia.Rect.MakeLTRB(-30 * u, -11 * u, 26 * u, -8.5 * u), P(upper, a=a))
    for i in range(4):
        x = (20 - i * 13.5) * u
        cv.drawPath(poly([(x - 2.6 * u, -11 * u), (x - 4.2 * u, -22 * u), (x + 0.6 * u, -22 * u), (x + 2.2 * u, -11 * u)]), P(BUFF, a=a))
        cv.drawPath(poly([(x - 3.7 * u, -19 * u), (x - 4.2 * u, -22 * u), (x + 0.6 * u, -22 * u), (x + 1.1 * u, -19 * u)]), P(0xFF14161C, a=a))
    for x0, x1 in ((40, 37), (-40, -43)):
        cv.drawLine(x0 * u, -4 * u, x1 * u, -26 * u, P(h('8A6A4A'), 0.7 * u, a=a))
    for i in range(22):
        cv.drawRect(skia.Rect.MakeXYWH((-32 + i * 2.8) * u, -7.2 * u, 1.3 * u, 1.3 * u), P(h('FFD890'), a=a))
    cv.restore()


def night_sea(cv, top='101C30', bot='060A12'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    for i in range(46):
        x = (math.sin(i * 12.9898) * 43758.5453) % 1 * W
        y = (math.sin(i * 78.233) * 43758.5453) % 1 * 700
        cv.drawCircle(x, y, 2 + i % 3, P(0xFFFFFFFF, a=0.25 + 0.5 * ((i * 7) % 5) / 5))


def ship_board(cv):
    """Rook's board for this case: a ship's notice board, navy baize in a varnished frame with a rope border."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('6A4630')))
    for i in range(0, W, 90):
        cv.drawLine(i, 0, i, H, P(0x22000000, 3))
    cv.drawRect(skia.Rect.MakeLTRB(50, 50, W - 50, H - 50), P(NAVY))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(50, 50, W - 50, H - 50))
    for i in range(12):
        y = 240 + i * 150
        path = skia.Path()
        path.moveTo(50, y)
        for x in range(50, W, 60):
            path.quadTo(x + 15, y - 16, x + 30, y)
            path.quadTo(x + 45, y + 16, x + 60, y)
        cv.drawPath(path, P(0x16FFFFFF, 3))
    cv.restore()
    for i in range(0, 2 * (W + H), 34):                         # rope border
        if i < W - 100:
            x, y = 50 + i, 50
        elif i < W + H - 200:
            x, y = W - 50, 50 + i - (W - 100)
        elif i < 2 * W + H - 300:
            x, y = W - 50 - (i - (W + H - 200)), H - 50
        else:
            x, y = 50, max(50, H - 50 - (i - (2 * W + H - 300)))
        cv.drawCircle(x, y, 13, P(h('D8C49A')))
        cv.drawCircle(x, y, 13, P(h('8A7448'), 3))
    for x, y in ((50, 50), (W - 50, 50), (50, H - 50), (W - 50, H - 50)):
        cv.drawCircle(x, y, 22, P(h('C89A3A')))
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
    cv.drawRect(skia.Rect.MakeXYWH(-tw / 2 - 30, -size * 0.62, tw + 60, size * 1.2), P(col, 14, a=k))
    cv.drawString(s, -tw / 2, size * 0.36, f, P(col, a=k))
    cv.restore()


def tick(cv, x, y, s, k):
    if k <= 0:
        return
    k = min(1.0, k)
    path = skia.Path()
    path.moveTo(x - 0.4 * s, y)
    path.lineTo(x - 0.4 * s + 0.3 * s * min(1, k * 2), y + 0.3 * s * min(1, k * 2))
    if k > 0.5:
        u = (k - 0.5) * 2
        path.lineTo(x - 0.1 * s + 0.6 * s * u, y + 0.3 * s - 0.8 * s * u)
    p = P(h('3EC46A'), s * 0.2)
    p.setStrokeCap(skia.Paint.kRound_Cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    cv.drawPath(path, p)


SHIPS = (('1911', 'OLYMPIC', 'COLLISION'), ('1912', 'TITANIC', 'ICEBERG'), ('1916', 'BRITANNIC', 'MINE'))


# ------------------------------------------------------------------ flat inserts
def three_ships(cv, c):
    """Three liners drop in one after another with their years, then the count."""
    night_sea(cv)
    for i, (yr, name, what) in enumerate(SHIPS):
        age = c.k - 0.06 - i * 0.17
        if age < 0:
            continue
        drop = 1 - ease(age / 0.08)
        y = 330 + i * 285 - 420 * drop
        white = i == 2
        liner_icon(cv, 600, y, 760, hull=0xFFECE8DC if white else 0xFF1A1E28, a=1.0, tilt=-2.0 * drop)
        if white:
            cv.drawRect(skia.Rect.MakeLTRB(262, y - 12, 938, y - 2), P(h('2E7A4A')))
        cv.drawRect(skia.Rect.MakeLTRB(120, y + 44, 1040, y + 52), P(FOAM, a=0.5))
        Wd.text_card(cv, yr, 150, y - 150, 84, AMBER, 0xFF000000)
        if age < 0.07:
            cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFFFFFFF, a=0.25 * (1 - age / 0.07)))
    if c.k > 0.6:
        k = min(1.0, (c.k - 0.6) / 0.1)
        cv.save()
        cv.translate(540, 1100)
        cv.scale(1.8 - 0.8 * k, 1.8 - 0.8 * k)
        Wd.text_card(cv, '3 SHIPS', 0, 50, 190, AMBER, 0xFF000000)
        cv.restore()


def board_no(cv, c):
    ship_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 620)
    cv.scale(s, s)
    card(cv, 0, 0, 760, 640, 3)
    cv.rotate(3)
    photo(cv, 'ship', 0, 24, 690, 520, (0.5, 0.35))
    cv.restore()
    if c.lt > 0.12:
        cv.drawLine(540, 930, 540, 1030, P(RED, 8))
        note(cv, 540, 1120, 640, 190, -3, h('FFD866'), ['3 SHIPS?'], 100)
    for i in range(3):
        if c.lt > 0.16 + i * 0.04:
            liner_icon(cv, 240 + i * 300, 1600, 250, hull=0xFFECE8DC if i == 2 else 0xFF0E1016)
    if c.k > 0.5:
        stamp(cv, 'NO CHANCE', 540, 700, -12, min(1, (c.k - 0.5) / 0.16), 132)


def list3(cv, c):
    """A list drawn for the film: the three ships, what happened to each, a tick for each."""
    night_sea(cv, '14243C', '0A1220')
    Wd.text_card(cv, 'VIOLET JESSOP', 540, 210, 104, AMBER, 0xFF000000)
    Wd.text_card(cv, 'STEWARDESS', 540, 300, 56, 0xFFFFFFFF, 0xFF000000)
    for i, (yr, name, what) in enumerate(SHIPS):
        k = ease((c.k - 0.06 - i * 0.16) / 0.1)
        if k <= 0:
            continue
        y = 470 + i * 270
        cv.save()
        cv.translate((1 - k) * -700, 0)
        cv.drawRoundRect(skia.Rect.MakeXYWH(60, y - 110, 960, 220), 26, 26, P(0xE6101C30))
        cv.drawRoundRect(skia.Rect.MakeXYWH(60, y - 110, 960, 220), 26, 26, P(h('C89A3A'), 5))
        liner_icon(cv, 250, y + 40, 330, hull=0xFFECE8DC if i == 2 else 0xFF05070A)
        Wd.text_card(cv, yr, 250, y - 52, 62, AMBER, 0xFF000000)
        Wd.text_card(cv, name, 640, y - 12, 78, 0xFFFFFFFF, 0xFF000000)
        Wd.text_card(cv, what, 640, y + 66, 52, h('9CC4E0'), 0xFF000000)
        cv.restore()
        tick(cv, 940, y - 10, 110, (c.k - 0.14 - i * 0.16) / 0.08)
    if c.k > 0.66:
        k = min(1.0, (c.k - 0.66) / 0.1)
        cv.save()
        cv.translate(540, 1600)
        cv.scale(1.6 - 0.6 * k, 1.6 - 0.6 * k)
        Wd.text_card(cv, 'SURVIVED ALL 3', 0, 0, 112, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


def board_true(cv, c):
    ship_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 640)
    cv.scale(s, s)
    card(cv, 0, 0, 700, 800, -3)
    cv.rotate(-3)
    photo(cv, 'vi', 0, 24, 630, 680, (0.5, 0.42))
    cv.restore()
    if c.lt > 0.12:
        cv.drawLine(540, 1040, 540, 1090, P(RED, 8))
        note(cv, 540, 1180, 760, 180, 3, h('FFD866'), ['AT SEA UNTIL 1950'], 84)
    for i in range(3):
        liner_icon(cv, 240 + i * 300, 1620, 250, hull=0xFFECE8DC if i == 2 else 0xFF0E1016)
        tick(cv, 250 + i * 300, 1690, 54, (c.lt - 0.2 - i * 0.05) / 0.08)
    if c.lt > 0.34:
        stamp(cv, 'TRUE', 690, 900, -10, min(1, (c.lt - 0.34) / 0.12), 150)


SHOTS = {f.__name__: f for f in (three_ships, board_no, list3, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def closed(cv, c):
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 012  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x66FFFFFF, 7, size=(3, 8), drift=(-260, 120), wobble=30)


def snow_air(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x55DCEBFF, 5, size=(2, 5), drift=(-60, 90), wobble=20, twinkle=True)


OVER = dict(signoff=closed, props_pull=spray, stern_up=spray, boat_pov=spray, vi_jump=spray, rook_dive=spray, mine_hit=spray,
            tit_night=snow_air, berg_scrape=snow_air, tit_sink=snow_air)
