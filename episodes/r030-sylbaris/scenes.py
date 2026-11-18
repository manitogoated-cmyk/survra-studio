"""Case 030 - Ludger Sylbaris, who lived through the burning cloud of Mount Pelee in 1902 in a half-buried stone cell.
The story is filmed in 3D (world3d.py). This file holds the one flat insert (a circus bill on a board, drawn for this
film in a generic period style: no real poster, show name or logo is copied) and the 2D overlays drawn on top of 3D
shots (embers, falling ash, dust in the slit light, stars, the sign-off)."""
import math

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
ORANGE, AMBER, PAPER, RED = h('FF7A1A'), h('FFB000'), h('EFE2C0'), h('B8302A')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def plain(cv, s, x, y, size, color, weight=900, maxw=None):
    f = font(size, weight)
    w = f.measureText(s)
    if maxw and w > maxw:
        f = font(size * maxw / w, weight)
        w = maxw
    cv.drawTextBlob(skia.TextBlob(s, f), x - w / 2, y, P(color))
    return w


# ---------------------------------------------------------------- the circus bill
def poster(cv, c):
    """A circus bill pasted on a wooden board, lit by a lamp: a stone cell drawn in the middle, big type above and below.
    The type says only what the sources say he was billed as."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A1A10')), (1, h('120A06'))])
    for i in range(9):                                                                                  # boards
        cv.drawRect(skia.Rect.MakeXYWH(0, i * 220, W, 214), P(h('3E2A1A') if i % 2 else h('46301E')))
    z = 1.0 + 0.06 * ease(c.k)
    cv.save()
    cv.translate(540, 980)
    cv.scale(z, z)
    cv.rotate(-1.2)
    cv.translate(-540, -980)
    cv.drawRect(skia.Rect.MakeXYWH(118, 238, 860, 1300), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(100, 220, 860, 1300), P(PAPER))
    for i in range(40):                                                                                 # age stains
        cv.drawCircle(100 + 860 * rn(i, 1), 220 + 1300 * rn(i, 2), 20 + 50 * rn(i, 3), P(h('D8C49A'), a=0.35))
    cv.drawRect(skia.Rect.MakeXYWH(130, 250, 800, 1240), P(RED, 8))
    plain(cv, 'COME AND SEE', 530, 360, 64, INK, 900, 700)
    plain(cv, 'THE MAN WHO', 530, 480, 110, RED, 900, 760)
    plain(cv, 'LIVED THROUGH', 530, 600, 104, RED, 900, 760)
    # a drawn stone cell
    cv.drawRect(skia.Rect.MakeXYWH(330, 700, 400, 300), P(h('8C8478')))
    for j in range(4):
        for i in range(5):
            cv.drawRect(skia.Rect.MakeXYWH(330 + 80 * i + (40 if j % 2 else 0) % 80, 700 + 75 * j, 80, 75), P(INK, 3, a=0.5))
    cv.drawRect(skia.Rect.MakeXYWH(470, 820, 120, 180), P(h('4A3220')))
    cv.drawRect(skia.Rect.MakeXYWH(490, 850, 80, 18), P(INK))
    cv.drawRect(skia.Rect.MakeXYWH(320, 690, 420, 20), P(h('6E675E')))
    for i in range(7):                                                                                  # rays
        a = -math.pi * (0.1 + 0.8 * i / 6)
        cv.drawLine(530 + 240 * math.cos(a), 700 + 240 * math.sin(a), 530 + 330 * math.cos(a), 700 + 330 * math.sin(a), P(AMBER, 10))
    g = ease((c.lt - 0.15) / 0.3)
    cv.save()
    cv.translate(530, 1190)
    s = 1.15 - 0.15 * g
    cv.scale(s, s)
    plain(cv, 'DOOMSDAY', 0, 0, 160, INK, 900, 760)
    cv.restore()
    for x, y in ((130, 250), (930, 250), (130, 1490), (930, 1490)):
        cv.drawCircle(x, y, 12, P(h('9A9690')))
    cv.restore()
    if c.lt > 0.3:
        fit(cv, 'ON TOUR', 540, 1700, 120, 900, AMBER)


SHOTS = {f.__name__: f for f in (poster,)}


# ---------------------------------------------------------------- overlays on the 3D shots
def embers(cv, c):
    for i in range(46):
        x = (W * rn(i, 11) + c.t * (180 + 260 * rn(i, 12))) % (W + 100) - 50
        y = (H * rn(i, 13) - c.t * (300 + 500 * rn(i, 14))) % (H + 100) - 50
        r = 2 + 5 * rn(i, 15)
        cv.drawCircle(x, y, r, P(h('FF8A3A'), a=0.55 + 0.4 * math.sin(c.t * 9 + i)))
    Wd.particles(cv, W, H, c.t, 30, 0x88A09890, 71, size=(3, 7), drift=(140, 40), wobble=40, twinkle=False)


def ashfall(cv, c):
    Wd.particles(cv, W, H, c.t, 70, 0xAAE0DCD4, 73, size=(3, 8), drift=(30, 140), wobble=40, twinkle=False)


def heavyash(cv, c):
    ashfall(cv, c)
    Wd.particles(cv, W, H, c.t * 1.3, 60, 0x99C8C4BC, 79, size=(4, 10), drift=(-40, 180), wobble=50, twinkle=False)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x88F4ECDC, 63, size=(3, 7), drift=(20, 50), wobble=30, twinkle=True)


def stars(cv, c):
    Wd.particles(cv, W, H, c.t, 12, 0x55FFFFFF, 67, size=(2, 4), drift=(-20, 6), wobble=10, twinkle=True)


def closed(cv, c):
    if c.lt > 0.3:
        k = min(1, (c.lt - 0.3) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 030', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(bay_blast=ashfall, cloud_town=embers, jail_yard=embers, cell_face=motes, rook_slit=embers, rook_tap=motes, slit_close=motes,
            cloud_rush=embers, slit_glow=embers, rook_brace=embers, shield=embers, sleeve_look=ashfall, rook_listen=ashfall, town_ash=heavyash,
            ruins_street=ashfall, rook_hatoff=ashfall, dark_wait=motes, rescuers=ashfall, shout=motes, dig_out=ashfall, rook_wall=ashfall,
            pardon=ashfall, wall_sneak=stars, circus_ring=motes, rook_crowd=motes, signoff=closed)
