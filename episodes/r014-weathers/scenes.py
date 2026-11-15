"""Case 014 - Beck Weathers. The story is filmed in 3D (world3d.py). This file holds the flat inserts (the double
stamp, Rook's case board pinned to a sheet of orange tent fabric, the two drawn hands) and the 2D overlays drawn on
top of 3D shots (blown snow, the blizzard, the white haze over his sight, rotor wash, the sign-off). Every card is
a drawing made for this film; none of them reproduces a real document, photograph, medical image or logo."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F0E8D2'), h('D8362A'), h('3EC46A')
ICE, DEEP = h('CFE2FA'), h('0A1428')


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
        cv.drawRect(dst, P(h('7A94B8')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def fabric_board(cv):
    """Rook's board for this case: a panel of orange tent fabric, stitched in squares, laced to a frame with cord."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('1C2434')))
    cv.drawRect(skia.Rect.MakeLTRB(50, 70, W - 50, H - 60), P(h('D9772A')))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(50, 70, W - 50, H - 60))
    for i in range(-H, W + H, 26):                                # ripstop weave
        cv.drawLine(i, 0, i + H, H, P(h('E8862E'), 2, a=0.35))
        cv.drawLine(i, H, i + H, 0, P(h('B85E1C'), 2, a=0.3))
    for x in (50, 380, 710, W - 50):                              # seams
        for y in range(80, H - 60, 34):
            cv.drawLine(x - 0, y, x, y + 18, P(h('7A3A12'), 6))
    for y in (70, 690, 1310, H - 60):
        for x in range(60, W - 50, 34):
            cv.drawLine(x, y, x + 18, y, P(h('7A3A12'), 6))
    cv.restore()
    for i in range(9):                                            # eyelets and lacing along the top and bottom
        x = 110 + i * 107.5
        for y, y2 in ((100, 30), (H - 90, H - 22)):
            cv.drawCircle(x, y, 15, P(h('D8DCE4')))
            cv.drawCircle(x, y, 7, P(h('1C2434')))
            cv.drawLine(x, y, x + (40 if i % 2 else -40), y2, P(h('F0E8D2'), 6))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.5, 0x00000000), (1, 0x66000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, tape=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if tape:
        for sx in (-1, 1):                                        # held by two steel clips
            cv.drawRoundRect(skia.Rect.MakeXYWH(sx * (w_ / 2 - 90) - 28, -h_ / 2 - 34, 56, 86), 20, 20, P(h('D8DCE4'), 12))
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
    cv.drawRoundRect(skia.Rect.MakeXYWH(-tw / 2 - 30, -size * 0.62, tw + 60, size * 1.2), 18, 18, P(col, 14, a=k))
    cv.drawString(s, -tw / 2, size * 0.36, f, P(col, a=k))
    cv.restore()


def flakes(cv, t, n=60, col=0xCCF4F8FF, drift=(-70, 230), size=(3, 8), seed=5):
    Wd.particles(cv, W, H, t, n, col, seed, size=size, drift=drift, wobble=26)


# ------------------------------------------------------------------ flat inserts
def twice(cv, c):
    """'Left him for dead. Twice.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A2C4E')), (1, h('060A14'))])
    for i in range(7):                                            # a far line of peaks, plain shapes
        x = -80 + i * 200
        cv.drawPath(poly([(x - 190, 1500), (x + 20, 1060 - 70 * (i % 3)), (x + 230, 1500)]), P(h('22385E')))
        cv.drawPath(poly([(x - 60, 1230 - 46 * (i % 3)), (x + 20, 1060 - 70 * (i % 3)), (x + 100, 1230 - 46 * (i % 3)), (x + 20, 1290 - 46 * (i % 3))]),
                    P(h('5A76A8')))
    cv.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), P(h('22385E')))
    flakes(cv, c.t, 70, 0xAAF4F8FF, (-240, 320))
    k1 = min(1, c.lt / 0.12)
    stamp(cv, 'LEFT FOR DEAD', 540, 560, -8, k1, 118)
    if c.k > 0.5:
        k2 = min(1, (c.k - 0.5) * c.d / 0.12)
        stamp(cv, 'LEFT FOR DEAD', 540, 900, 6, k2, 118)
        fit(cv, 'TWICE', 540, 1180 + 40 * (1 - k2), 170, 800, AMBER)


def board_no(cv, c):
    fabric_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 560)
    cv.scale(s, s)
    card(cv, 0, 0, 760, 680, -3)
    cv.rotate(-3)
    photo(cv, 'peak', 0, 20, 690, 580, (0.5, 0.35))
    cv.restore()
    if c.lt > 0.1:
        cv.drawLine(540, 905, 540, 955, P(h('F0E8D2'), 8))
        note(cv, 540, 1040, 760, 190, 3, h('FFD866'), ['DEAD TWICE?'], 96)
    fit(cv, '1996', 300, 1600, 120, 400, INK, None)
    fit(cv, 'EVEREST', 750, 1600, 96, 480, INK, None)
    if c.k > 0.45:
        stamp(cv, 'NO CHANCE', 540, 600, -12, min(1, (c.k - 0.45) * c.d / 0.1), 132)


def board_beck(cv, c):
    fabric_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 540)
    cv.scale(s, s)
    card(cv, 0, 0, 680, 760, 2)
    cv.rotate(2)
    photo(cv, 'beck', 0, 20, 610, 660, (0.5, 0.42))
    cv.restore()
    if c.lt > 0.12:
        cv.drawLine(540, 925, 540, 975, P(h('F0E8D2'), 8))
        note(cv, 540, 1060, 800, 180, -3, h('FFD866'), ['PATHOLOGIST'], 92)
    if c.lt > 0.95:
        j = ease((c.lt - 0.95) / 0.14)
        cv.save()
        cv.translate(540, 1600)
        cv.scale(1.3 - 0.3 * j, 1.3 - 0.3 * j)
        note(cv, 0, 0, 560, 170, 4, PAPER, ['DALLAS'], 100)
        cv.restore()
        cv.drawLine(540, 1150, 540, 1515, P(h('F0E8D2'), 8, a=j))


def hand_shape(cx, cy, s, flip=1):
    """A plain mitten-like outline of a hand, fingers up: palm path and four finger rects plus a thumb."""
    palm = skia.Rect.MakeXYWH(cx - 1.25 * s, cy - 0.2 * s, 2.5 * s, 2.5 * s)
    fingers = [skia.Rect.MakeXYWH(cx + (-1.25 + i * 0.64) * s, cy - (1.75 + (0.35 if i in (1, 2) else 0.0)) * s, 0.56 * s,
                                  (1.75 + (0.35 if i in (1, 2) else 0.0)) * s) for i in range(4)]
    thumb = skia.Rect.MakeXYWH(cx + flip * 1.25 * s - (0 if flip > 0 else 0.6 * s), cy + 0.2 * s, 0.6 * s, 1.5 * s)
    wrist = skia.Rect.MakeXYWH(cx - 0.95 * s, cy + 2.2 * s, 1.9 * s, 1.5 * s)
    return palm, fingers, thumb, wrist


def dashed(col, w_):
    pa = P(col, w_)
    pa.setPathEffect(skia.DashPathEffect.Make([22, 20], 0))
    return pa


def cost_card(cv, c):
    """Two drawn hands, backs towards us. The right one goes to a dotted outline, then the fingers of the left."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('20304E')), (1, h('080C16'))])
    flakes(cv, c.t, 40, 0x66F4F8FF, (-40, 120), (2, 5))
    fit(cv, 'THE COST', 540, 300, 130, 900, 0xFFFFFFFF)
    s = 96
    k_r = ease((c.lt - 0.75) / 0.35)                              # "his right hand"
    k_l = ease((c.lt - 1.45) / 0.3)                               # "the fingers of his left"
    skin, line = h('E2B694'), h('F4F8FF')
    for side, cx in ((-1, 290), (1, 790)):                        # left hand on the left of the picture, right on the right
        palm, fingers, thumb, wrist = hand_shape(cx, 760, s, flip=-side)
        gone = k_r if side == 1 else 0.0
        fg = k_r if side == 1 else k_l
        cv.drawRoundRect(wrist, 20, 20, P(skin))
        for rect, kk in [(palm, gone), (thumb, gone if side == 1 else k_l)] + [(f, fg) for f in fingers]:
            if kk < 1:
                cv.drawRoundRect(rect, 26, 26, P(skin, a=1 - kk))
            if kk > 0:
                cv.drawRoundRect(rect, 26, 26, dashed(line, 7))
                cv.drawRoundRect(rect, 26, 26, P(ICE, a=0.12 * kk))
        fit(cv, 'LEFT' if side == -1 else 'RIGHT', cx, 1240, 84, 400, AMBER if (side == 1 and k_r > 0) or (side == -1 and k_l > 0) else 0xFFFFFFFF)
    cv.drawLine(540, 560, 540, 1260, P(0x33FFFFFF, 4))


def board_true(cv, c):
    fabric_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 560)
    cv.scale(s, s)
    card(cv, 0, 0, 700, 720, 3)
    cv.rotate(3)
    photo(cv, 'walk', 0, 20, 630, 620, (0.5, 0.5))
    cv.restore()
    if c.lt > 0.1:
        cv.drawLine(540, 925, 540, 975, P(h('F0E8D2'), 8))
        note(cv, 540, 1065, 700, 180, -3, h('FFD866'), ['HE GOT UP'], 96)
    for i, s_ in enumerate(('LEFT FOR DEAD', 'TWICE')):
        if c.lt > 0.15 + i * 0.1:
            fit(cv, s_, 540, 1560 + i * 120, 88, 880, INK, None)
    if c.lt > 0.42:
        stamp(cv, 'TRUE', 720, 760, -10, min(1, (c.lt - 0.42) / 0.12), 150, GREEN)


SHOTS = {f.__name__: f for f in (twice, board_no, board_beck, cost_card, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def spindrift(cv, c, n=90, a=1.0, speed=1.0):
    """Snow blown flat across the frame, with a few long streaks."""
    Wd.particles(cv, W, H, c.t, n, 0xDDF4F8FF, 7, size=(3, 9), drift=(1500 * speed, 190 * speed), wobble=34)
    for j in range(10):
        ph = (math.sin(j * 12.9898) * 43758.5453) % 1
        x = ((c.t * 2600 * speed * (0.6 + ph)) + ph * 4000) % (W + 900) - 450
        y = (ph * 7919) % H + 120 * math.sin(c.t * 2 + j)
        cv.drawLine(x, y, x + 320, y + 44, P(0xFFFFFFFF, 10 + 8 * ph, a=0.16 * a))


def blow(cv, c):
    spindrift(cv, c, 80, 0.9, 0.8)


def blizzard(cv, c):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFD8E2F4, a=0.2 + 0.06 * math.sin(c.t * 9)))
    spindrift(cv, c, 170, 1.6, 1.3)


def night_storm(cv, c):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFF9FB4E8, a=0.1 + 0.03 * math.sin(c.t * 9)))
    spindrift(cv, c, 150, 1.2, 1.2)


def snow(cv, c):
    flakes(cv, c.t, 50, 0xCCF4F8FF)


def haze(cv, c):
    """His sight going: a milky white closes in from every side until almost nothing is left."""
    k = ease(c.k * 1.25)
    for i in range(5):
        r = lerp(1500, 260, k) + i * 190
        pa = P(0xFFF4F6FA, 170, a=min(1.0, 0.16 + 0.5 * k))
        cv.drawCircle(540 + 30 * math.sin(c.t * 3 + i), 800 + 24 * math.cos(c.t * 2.3 + i), r, pa)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFF4F6FA, a=0.72 * k))


def wash(cv, c):
    """Snow thrown outward by the rotor."""
    for i in range(70):
        ph = (math.sin(i * 12.9898) * 43758.5453) % 1
        a = (math.sin(i * 78.233) * 43758.5453) % 1 * 6.283
        d = ((c.t * 1.4 + ph) % 1) * 1300
        cv.drawCircle(540 + d * math.cos(a), 880 + d * math.sin(a) * 0.55, 4 + d * 0.012, P(0xFFF4F8FF, a=0.75 * (1 - d / 1400) * min(1, c.k * 2.5)))


def closed(cv, c):
    snow(cv, c)
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 014  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(ice_body=blizzard, col_wide=blow, left_walk=blow, eyes_open=blow, rook_jolt=blow, rook_cairn=snow, rook_go=snow, blur_pov=haze,
            descend=blow, blizzard_hit=blizzard, lost_group=night_storm, rescuer=night_storm, rescuer_no=night_storm, frozen_hand=snow,
            beck_rise=blow, beck_walks=blow, hollow=blow, heli_land=wash, rook_wrong=snow, signoff=closed)
