"""Case 030, the full case file (16:9) - Ludger Sylbaris, who lived through the burning cloud of Mount Pelee on 8 May 1902 in
a half-buried stone cell. The story is filmed in 3D (world3d.py). This file holds the flat inserts on a 1920x1080 canvas
(a card of the warning weeks, a circus bill, Rook's case board), the 2D overlays drawn on top of 3D shots, and the
thumbnail. Every card is a drawing made for this film: the bill copies no real poster, show name or logo, and the card of
dates carries only what the sources agree on. Captions run in a band around 86% of the height and the label sits top
right, so the cards keep both clear."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1920, 1080
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
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


def plain(cv, s, x, y, size, color, weight=900, maxw=None, centre=True):
    if not s:
        return 0
    f = font(size, weight)
    w = f.measureText(s)
    if maxw and w > maxw:
        f = font(size * maxw / w, weight)
        w = maxw
    cv.drawTextBlob(skia.TextBlob(s, f), x - (w / 2 if centre else 0), y, P(color))
    return w


def push(cv, c, amount=0.07, sway=0.3):
    z = 1.0 + amount * ease(c.k)
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.rotate(sway * math.sin(c.t * 0.7))
    cv.translate(-W / 2, -H / 2)


def planks(cv, cols=(('3E2A1A', '46301E'))):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A1A10')), (1, h('120A06'))])
    for i in range(10):
        cv.drawRect(skia.Rect.MakeXYWH(i * 196, 0, 190, H), P(h(cols[i % 2])))
        for j in range(5):
            y = H * rn(i * 7 + j, 3)
            cv.drawLine(i * 196 + 30 + 120 * rn(i + j, 4), y, i * 196 + 40 + 120 * rn(i + j, 4), y + 140, P(h('2E1E12'), 3, a=0.6))


# ---------------------------------------------------------------- the warning weeks
LINES = (('APRIL', 'STEAM AT THE SUMMIT. TREMORS.'), ('EARLY MAY', 'ASH FALLS ON THE TOWN.'), ('', 'SNAKES IN THE STREETS.'),
         ('5 MAY', 'MUD BURIES A FACTORY.'))


def timeline(cv, c):
    """A sheet pinned to boards: the warning weeks, one line at a time, and under them, ringed, the election on Sunday."""
    planks(cv)
    cv.save()
    push(cv, c)
    cv.save()
    cv.translate(960, 440)
    cv.rotate(-1.0)
    cv.drawRect(skia.Rect.MakeXYWH(-742, -372, 1500, 760), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-750, -380, 1500, 760), P(PAPER))
    for i in range(30):
        cv.drawCircle(-750 + 1500 * rn(i, 1), -380 + 760 * rn(i, 2), 20 + 50 * rn(i, 3), P(h('D8C49A'), a=0.3))
    plain(cv, 'SAINT-PIERRE, 1902', -690, -290, 54, h('6A5A48'), 900, centre=False)
    cv.drawLine(-690, -262, 690, -262, P(INK, 4))
    for i, (d, s) in enumerate(LINES):
        if c.lt > 0.15 + 0.3 * i:
            y = -170 + 104 * i
            plain(cv, d, -690, y, 62, RED, 900, centre=False)
            plain(cv, s, -300, y, 62, INK, 900, 990, centre=False)
    if c.lt > 1.45:
        g = ease((c.lt - 1.45) / 0.25)
        plain(cv, 'SUNDAY 11 MAY', -690, 290, 76, RED, 900, centre=False)
        plain(cv, 'ELECTION DAY', -20, 290, 76, INK, 900, 700, centre=False)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-716, 204, 1432 * g, 118), 20, 20, P(ORANGE, 9))
    cv.restore()
    for x in (250, 1670):
        cv.drawCircle(x, 96, 20, P(ORANGE))
        cv.drawCircle(x, 96, 20, P(INK, 5))
    cv.restore()
    Wd.particles(cv, W, H, c.t, 40, 0x77E0DCD4, 73, size=(3, 7), drift=(26, 120), wobble=40, twinkle=False)


# ---------------------------------------------------------------- the circus bill
def poster(cv, c):
    """A circus bill pasted on a board fence, lit by a lamp: a stone cell drawn on the left under rays, big type on the right.
    The type says only what the sources say he was billed as."""
    planks(cv)
    cv.save()
    push(cv, c, 0.06, 0.25)
    cv.save()
    cv.translate(960, 440)
    cv.rotate(-1.2)
    cv.drawRect(skia.Rect.MakeXYWH(-772, -382, 1560, 780), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-780, -390, 1560, 780), P(PAPER))
    for i in range(40):
        cv.drawCircle(-780 + 1560 * rn(i, 1), -390 + 780 * rn(i, 2), 20 + 50 * rn(i, 3), P(h('D8C49A'), a=0.35))
    cv.drawRect(skia.Rect.MakeXYWH(-750, -360, 1500, 720), P(RED, 8))
    # the drawn cell, with rays behind it
    for i in range(9):
        a = -math.pi * (0.06 + 0.88 * i / 8)
        cv.drawLine(-430 + 250 * math.cos(a), 110 + 250 * math.sin(a), -430 + 350 * math.cos(a), 110 + 350 * math.sin(a), P(AMBER, 11))
    cv.drawRect(skia.Rect.MakeXYWH(-640, 0, 420, 300), P(h('8C8478')))
    for j in range(4):
        for i in range(6):
            cv.drawRect(skia.Rect.MakeXYWH(-640 + 70 * i + (35 if j % 2 else 0), 75 * j, 70, 75), P(INK, 3, a=0.45))
    cv.drawRect(skia.Rect.MakeXYWH(-650, -14, 440, 22), P(h('6E675E')))
    cv.drawRect(skia.Rect.MakeXYWH(-490, 110, 120, 190), P(h('4A3220')))
    cv.drawRect(skia.Rect.MakeXYWH(-470, 140, 80, 18), P(INK))
    plain(cv, 'COME AND SEE', 250, -250, 60, INK, 900, 800)
    plain(cv, 'THE MAN WHO', 250, -130, 112, RED, 900, 860)
    plain(cv, 'LIVED THROUGH', 250, -10, 108, RED, 900, 860)
    g = ease((c.lt - 0.2) / 0.3)
    cv.save()
    cv.translate(250, 190)
    s = 1.12 - 0.12 * g
    cv.scale(s, s)
    plain(cv, 'DOOMSDAY', 0, 0, 176, INK, 900, 860)
    cv.restore()
    for x, y in ((-750, -360), (750, -360), (-750, 360), (750, 360)):
        cv.drawCircle(x, y, 12, P(h('9A9690')))
    cv.restore()
    cv.restore()
    Wd.particles(cv, W, H, c.t, 30, 0x66F4ECDC, 63, size=(3, 6), drift=(16, 30), wobble=30, twinkle=True)


# ---------------------------------------------------------------- Rook's board
def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('5A3A26')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def board(cv, c):
    """Rook's board for this case: grey stone blocks, the photograph of the man in the light of the slit, held by an iron
    nail, and the end of the case in three lines."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A3632')), (1, h('1A1816'))])
    cv.save()
    push(cv, c, 0.07, 0.3)
    for j in range(6):
        for i in range(8):
            x = -120 + 280 * i + (140 if j % 2 else 0)
            cv.drawRect(skia.Rect.MakeXYWH(x, 190 * j - 20, 272, 182), P(h(('8C8478', '7E776C', '968E82')[(i + j) % 3])))
            cv.drawRect(skia.Rect.MakeXYWH(x, 190 * j - 20, 272, 182), P(h('5A544C'), 4))
    k = min(1, c.lt / 0.16)
    s = 0.76 + 0.24 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(560, 430)
    cv.scale(s, s)
    cv.rotate(-2.2)
    cv.drawRect(skia.Rect.MakeXYWH(-400 + 12, -300 + 16, 800, 600), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-400, -300, 800, 600), P(PAPER))
    photo(cv, 'thumb', 0, -10, 740, 520, (0.9, 0.5))
    cv.restore()
    cv.drawCircle(560, 150, 18, P(h('2A2A2E')))
    cv.drawCircle(556, 146, 7, P(h('6A6A70')))
    if c.lt > 0.25:
        fit(cv, 'LUDGER SYLBARIS', 1350, 300, 96, 740, 0xFFFFFFFF)
    if c.lt > 0.6:
        fit(cv, 'PARDONED', 1350, 440, 96, 740, AMBER)
    if c.lt > 0.95:
        fit(cv, 'DIED AROUND 1929', 1350, 580, 84, 740, 0xFFFFFFFF)
    if c.lt > 1.3:
        fit(cv, 'IN PANAMA', 1350, 690, 84, 740, 0xFFFFFFFF)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 24, 0x55F4ECDC, 91, size=(2, 5), drift=(12, 20), wobble=20, twinkle=True)


SHOTS = {f.__name__: f for f in (timeline, poster, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def embers(cv, c):
    for i in range(70):
        x = (W * rn(i, 11) + c.t * (220 + 300 * rn(i, 12))) % (W + 100) - 50
        y = (H * rn(i, 13) - c.t * (200 + 320 * rn(i, 14))) % (H + 100) - 50
        cv.drawCircle(x, y, 2 + 4 * rn(i, 15), P(h('FF8A3A'), a=0.55 + 0.4 * math.sin(c.t * 9 + i)))
    Wd.particles(cv, W, H, c.t, 40, 0x88A09890, 71, size=(3, 6), drift=(160, 40), wobble=40, twinkle=False)


def ashfall(cv, c):
    Wd.particles(cv, W, H, c.t, 110, 0xAAE0DCD4, 73, size=(2, 6), drift=(30, 120), wobble=40, twinkle=False)


def lightash(cv, c):
    Wd.particles(cv, W, H, c.t, 50, 0x88E0DCD4, 75, size=(2, 5), drift=(20, 90), wobble=40, twinkle=False)


def heavyash(cv, c):
    ashfall(cv, c)
    Wd.particles(cv, W, H, c.t * 1.3, 90, 0x99C8C4BC, 79, size=(3, 8), drift=(-40, 150), wobble=50, twinkle=False)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0x88F4ECDC, 63, size=(2, 5), drift=(20, 40), wobble=30, twinkle=True)


def stars(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x55FFFFFF, 67, size=(2, 3), drift=(-14, 5), wobble=8, twinkle=True)


def haze(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x44FFF4DC, 61, size=(2, 5), drift=(30, -10), wobble=30, twinkle=True)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 50, 0x66C8B8A0, 77, size=(3, 8), drift=(-260, 60), wobble=30, twinkle=False)


def closed(cv, c):
    haze(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(1380, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 030', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(bay_blast=lightash, cloud_town=embers, jail_yard=embers, cell_face=motes, rook_slit=embers, rook_tap=motes, slit_close=motes,
            cloud_rush=embers, slit_glow=embers, rook_brace=embers, shield=embers, sleeve_look=ashfall, rook_listen=ashfall, town_ash=heavyash,
            ruins_street=ashfall, rook_hatoff=ashfall, dark_wait=motes, rescuers=ashfall, shout=motes, dig_out=ashfall, rook_wall=ashfall,
            pardon=ashfall, wall_sneak=stars, circus_ring=motes, rook_crowd=motes, signoff=closed,
            bay_calm=haze, quay_life=haze, quay_close=haze, quay_ash=heavyash, summit_steam=haze, snake_lane=lightash, snake_close=lightash,
            mud_valley=spray, mud_after=heavyash, hall_report=motes, hall_window=motes, road_in=lightash, gov_arrive=ashfall, party_night=stars,
            rook_room=motes, ships_fire=embers, roddam_away=embers, slit_dark=motes, cloth_slit=embers, edge_house=heavyash, cell_stands=ashfall,
            ring_tell=motes, geologist=lightash, spine_rise=lightash, bay_today=haze, rook_question=haze, led_in=haze, back_gate=haze, door_shut=haze)


def THUMB(cv, c):
    """1280x720: the 3D still (his face in the orange light from the slit, on the right) and the hook on the left, over the
    dark of the cell."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('140C08'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(700, 0), (0, 0)], [0x00000000, 0xD0000000])))
    fit(cv, 'SAVED BY', 330, 300, 150, 580, 0xFFFFFFFF)
    fit(cv, 'HIS CELL', 330, 460, 150, 580, AMBER)
