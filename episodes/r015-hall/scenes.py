"""Case 015 - Lincoln Hall. The story is filmed in 3D (world3d.py). This file holds the flat inserts (the DECLARED
DEAD stamp, Rook's case board framed in climbing rope, the crossed-out oxygen bottle, the drawn hands and foot) and
the 2D overlays drawn on top of 3D shots (ice glitter at sunrise, blown snow, stars, the swimming haze of altitude
sickness, the sign-off). Every card is a drawing made for this film; none of them reproduces a real document,
photograph, book cover, medical image or logo."""
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
TEAL, NIGHT = h('1F7FA0'), h('0A1030')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 91.3458 + j * 47.7231) * 24634.6345) % 1


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


def rope_board(cv, t=0.0):
    """Rook's board for this case: dark blue felt in a frame of twisted climbing rope, held by four ice screws."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('10141E')))
    cv.drawRoundRect(skia.Rect.MakeLTRB(46, 66, W - 46, H - 56), 40, 40, P(h('1E3A5C')))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(46, 66, W - 46, H - 56))
    for i in range(160):                                          # felt flecks
        x, y = rn(i, 1) * W, rn(i, 2) * H
        cv.drawLine(x, y, x + 14, y + 6, P(h('2C5078'), 3, a=0.5))
    cv.restore()
    def twist(x0, y0, x1, y1):
        n = int(math.hypot(x1 - x0, y1 - y0) / 30)
        cv.drawLine(x0, y0, x1, y1, P(h('C85A10'), 34))
        for i in range(n + 1):
            k = i / max(1, n)
            x, y = lerp(x0, x1, k), lerp(y0, y1, k)
            dx, dy = (0, 15) if abs(x1 - x0) > abs(y1 - y0) else (15, 0)
            cv.drawLine(x - dx - 8, y - dy + 8 * (dx > 0), x + dx + 8, y + dy - 8 * (dx > 0), P(TEAL if i % 3 == 0 else ORANGE, 12))
    twist(60, 80, W - 60, 80)
    twist(60, H - 70, W - 60, H - 70)
    twist(60, 80, 60, H - 70)
    twist(W - 60, 80, W - 60, H - 70)
    for x, y in ((60, 80), (W - 60, 80), (60, H - 70), (W - 60, H - 70)):
        cv.drawCircle(x, y, 30, P(h('D8DCE4')))
        cv.drawCircle(x, y, 13, P(h('3A3F4C')))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.5, 0x00000000), (1, 0x66000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, pins=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if pins:
        for sx in (-1, 1):                                        # two orange pins
            cv.drawCircle(sx * (w_ / 2 - 60), -h_ / 2 + 34, 20, P(ORANGE))
            cv.drawCircle(sx * (w_ / 2 - 60) - 5, -h_ / 2 + 29, 7, P(0xFFFFD0A0))
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=64):
    card(cv, x, y, w_, h_, ang, col, pins=False)
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


def twinkle(cv, t, n=70, top=1250, seed=4):
    for i in range(n):
        x, y = rn(i, seed) * W, rn(i, seed + 1) * top
        a = 0.35 + 0.65 * abs(math.sin(t * (1.5 + 3 * rn(i, seed + 2)) + i))
        cv.drawCircle(x, y, 2.5 + 3.5 * rn(i, seed + 3), P(0xFFF4F8FF, a=a))


def drift(cv, t, n=50, col=0xCCF4F8FF, vel=(-70, 230), size=(3, 8), seed=5):
    Wd.particles(cv, W, H, t, n, col, seed, size=size, drift=vel, wobble=26)


# ------------------------------------------------------------------ flat inserts
def stamp_dead(cv, c):
    """'He was declared dead last night.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A1030')), (0.7, h('2A2458')), (1, h('120E24'))])
    twinkle(cv, c.t, 90, 1100)
    z = 1.0 + 0.06 * c.k
    cv.save()
    cv.translate(540, 1300)
    cv.scale(z, z)
    cv.translate(-540, -1300)
    cv.drawPath(poly([(-80, 1500), (300, 1320), (520, 1255), (640, 1262), (860, 1345), (1160, 1470), (1160, 1960), (-80, 1960)]), P(h('05060E')))
    cv.drawPath(poly([(300, 1320), (520, 1255), (640, 1262), (700, 1300), (500, 1330)]), P(h('232A52')))
    cv.restore()
    drift(cv, c.t, 40, 0x88F4F8FF, (-200, 120))
    k1 = min(1, max(0.0, c.lt - 0.3) / 0.12)
    if c.lt > 0.3:
        stamp(cv, 'DECLARED DEAD', 540, 600, -8, k1, 112)
    if c.lt > 0.92:
        k2 = min(1, (c.lt - 0.92) / 0.12)
        fit(cv, 'LAST NIGHT', 540, 900 + 40 * (1 - k2), 130, 860, AMBER)


def pop_photo(cv, c, name, y, w_, h_, ang, focus):
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, y)
    cv.scale(s, s)
    card(cv, 0, 0, w_ + 70, h_ + 100, ang)
    cv.rotate(ang)
    photo(cv, name, 0, 20, w_, h_, focus)
    cv.restore()


def pin_no(cv, c):
    rope_board(cv, c.t)
    pop_photo(cv, c, 'peak', 560, 690, 560, -3, (0.5, 0.35))
    if c.lt > 0.1:
        cv.drawLine(540, 905, 540, 960, P(ORANGE, 8))
        note(cv, 540, 1050, 820, 200, 3, h('FFD866'), ["DEAD MEN DON'T SIT UP"], 70)
    fit(cv, '2006', 300, 1600, 120, 400, 0xFFFFFFFF, None)
    fit(cv, 'EVEREST', 750, 1600, 96, 480, 0xFFFFFFFF, None)
    if c.k > 0.42:
        stamp(cv, 'NO CHANCE', 540, 600, -12, min(1, (c.k - 0.42) * c.d / 0.1), 132)


def pin_hall(cv, c):
    rope_board(cv, c.t)
    pop_photo(cv, c, 'hall', 540, 610, 640, 2, (0.5, 0.45))
    if c.lt > 0.08:
        cv.drawLine(540, 925, 540, 975, P(ORANGE, 8))
        note(cv, 540, 1060, 800, 180, -3, h('FFD866'), ['AUSTRALIAN'], 96)
    if c.lt > 0.6:
        j = ease((c.lt - 0.6) / 0.14)
        cv.save()
        cv.translate(540, 1590)
        cv.scale(1.3 - 0.3 * j, 1.3 - 0.3 * j)
        note(cv, 0, 0, 560, 170, 4, PAPER, ['CLIMBER'], 100)
        cv.restore()
        cv.drawLine(540, 1150, 540, 1505, P(ORANGE, 8, a=j))


def no_card(cv, c):
    """'No oxygen.' A drawn bottle, crossed out."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A1030')), (1, h('1A1840'))])
    twinkle(cv, c.t, 60, 1900, 9)
    z = 1.0 + 0.1 * c.k
    cv.save()
    cv.translate(540, 660)
    cv.scale(z * 0.86, z * 0.86)
    cv.rotate(-14)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-130, -330, 260, 700), 120, 120, P(ORANGE))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-130, -330, 90, 700), 60, 60, P(0xFFFFA050, a=0.6))
    cv.drawRect(skia.Rect.MakeXYWH(-50, -410, 100, 90), P(h('B8BCC8')))
    cv.drawRect(skia.Rect.MakeXYWH(-90, -450, 180, 50), P(h('8A90A0')))
    cv.drawCircle(120, -425, 46, P(h('E8ECF4')))
    cv.drawLine(120, -425, 142, -452, P(RED, 8))
    cv.restore()
    k = min(1, max(0.0, c.lt - 0.08) / 0.1)
    if k > 0:
        for sx in (-1, 1):
            cv.drawLine(540 - sx * 300, 330, 540 - sx * 300 + sx * 600 * k, 330 + 660 * k, P(RED, 44))
    fit(cv, 'NO OXYGEN', 540, 1160, 150, 940, 0xFFFFFFFF)


def finger(cx, top, w_, len_):
    return skia.Rect.MakeXYWH(cx - w_ / 2, top, w_, len_)


def dashed(col, w_):
    pa = P(col, w_)
    pa.setPathEffect(skia.DashPathEffect.Make([16, 14], 0))
    return pa


def cost_tips(cv, c):
    """Two drawn hands lose their fingertips to dotted outlines; then a drawn foot loses one toe."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E3A5C')), (1, h('0A1020'))])
    for i in range(6):                                            # slow bands of light, so the card is never still
        x = ((c.t * 240 + i * 330) % (W + 700)) - 350
        cv.drawPath(poly([(x, 0), (x + 200, 0), (x - 160, H), (x - 360, H)]), P(0xFF7FB4E8, a=0.1))
    drift(cv, c.t, 90, 0x99F4F8FF, (-140, 380))
    z = 1.0 + 0.08 * c.k
    cv.translate(540, 760)
    cv.scale(z, z)
    cv.translate(-540, -760)
    fit(cv, 'THE COST', 540, 230, 120, 900, 0xFFFFFFFF)
    skin, line = h('E2B694'), h('F4F8FF')
    k_f = ease((c.lt - 0.55) / 0.35)                              # "his fingertips"
    k_t = ease((c.lt - 1.2) / 0.3)                                # "and a toe"
    s = 78
    for side, cx in ((-1, 290), (1, 790)):
        cy = 560
        cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 0.95 * s, cy + 2.2 * s, 1.9 * s, 1.2 * s), 18, 18, P(skin))
        cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 1.25 * s, cy - 0.2 * s, 2.5 * s, 2.5 * s), 24, 24, P(skin))
        rects = []
        for i in range(4):
            ln = (1.75 + (0.35 if i in (1, 2) else 0.0)) * s
            rects.append((cx + (-1.25 + 0.28 + i * 0.64) * s, cy - ln, 0.56 * s, ln))
        tx = cx + side * 1.25 * s + (0.3 * s if side > 0 else -0.3 * s)
        rects.append((tx, cy + 0.2 * s, 0.6 * s, 1.5 * s))
        for x0, top, w_, ln in rects:
            tip = 0.36 * ln
            cv.drawRoundRect(finger(x0, top + tip - 6, w_, ln - tip + 6), 14, 14, P(skin))
            r = finger(x0, top, w_, tip)
            if k_f < 1:
                cv.drawRoundRect(r, 22, 22, P(skin, a=1 - k_f))
            if k_f > 0:
                cv.drawRoundRect(r, 22, 22, dashed(line, 6))
    fit(cv, 'FINGERTIPS', 540, 905, 84, 800, AMBER if k_f > 0 else 0xFFFFFFFF)
    # the foot, seen from above, toes up
    fx, fy = 540, 1090
    cv.drawRoundRect(skia.Rect.MakeXYWH(fx - 120, fy - 60, 240, 150), 70, 70, P(skin))
    for i in range(5):
        w_ = 62 - i * 7
        x0 = fx - 118 + i * 52 + (62 - w_) / 2 - 4
        r = skia.Rect.MakeXYWH(x0, fy - 118 + i * 9, w_, 80 - i * 6)
        gone = k_t if i == 0 else 0.0
        if gone < 1:
            cv.drawRoundRect(r, 26, 26, P(skin, a=1 - gone))
        if gone > 0:
            cv.drawRoundRect(r, 26, 26, dashed(line, 6))
    fit(cv, 'ONE TOE', 800, 1100, 70, 300, AMBER if k_t > 0 else 0xFFFFFFFF)


def pin_true(cv, c):
    rope_board(cv, c.t)
    pop_photo(cv, c, 'sit', 550, 640, 620, 3, (0.5, 0.5))
    if c.lt > 0.1:
        cv.drawLine(540, 925, 540, 975, P(ORANGE, 8))
        note(cv, 540, 1065, 840, 180, -3, h('FFD866'), ['SURPRISED TO SEE ME?'], 74)
    for i, s_ in enumerate(('DECLARED DEAD', 'FOUND ALIVE')):
        if c.lt > 0.2 + i * 0.25:
            fit(cv, s_, 540, 1560 + i * 120, 88, 880, 0xFFFFFFFF if i == 0 else AMBER, None)
    if c.lt > 0.7:
        stamp(cv, 'TRUE', 720, 760, -10, min(1, (c.lt - 0.7) / 0.12), 150, GREEN)


SHOTS = {f.__name__: f for f in (stamp_dead, pin_no, pin_hall, no_card, cost_tips, pin_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def glitter(cv, c):
    """Ice crystals in the first sunlight, drifting past."""
    Wd.particles(cv, W, H, c.t, 46, 0xEEFFE8C8, 11, size=(3, 8), drift=(190, -70), wobble=30, twinkle=True)


def blown(cv, c):
    """Fine snow blown flat off the crest."""
    Wd.particles(cv, W, H, c.t, 70, 0xCCF4F8FF, 7, size=(3, 8), drift=(900, 140), wobble=30)
    for j in range(7):
        ph = rn(j, 3)
        x = ((c.t * 1900 * (0.6 + ph)) + ph * 4000) % (W + 900) - 450
        y = (ph * 7919) % H + 100 * math.sin(c.t * 2 + j)
        cv.drawLine(x, y, x + 300, y + 40, P(0xFFFFFFFF, 9 + 7 * ph, a=0.14))


def dusk_snow(cv, c):
    Wd.particles(cv, W, H, c.t, 50, 0xAAFFD8C0, 13, size=(3, 7), drift=(-520, 110), wobble=30)


def night_sky(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x99C8D8FF, 17, size=(2, 6), drift=(-260, 90), wobble=24, twinkle=True)


def house_stars(cv, c):
    twinkle(cv, c.t, 40, 620, 23)


def swim(cv, c):
    """Altitude sickness: the edges of his sight close in and pulse."""
    k = ease(c.k * 1.2)
    for i in range(4):
        r = lerp(1500, 520, k) + i * 200 + 40 * math.sin(c.t * 6 + i)
        pa = P(0xFF140A1E, 190, a=min(1.0, 0.25 + 0.5 * k))
        pa.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 80))
        cv.drawCircle(540 + 50 * math.sin(c.t * 3 + i), 860 + 40 * math.cos(c.t * 2.3 + i), r, pa)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFF140A1E, a=0.5 * ease((c.k - 0.6) / 0.4)))


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x88FFF0D0, 29, size=(2, 5), drift=(30, -50), wobble=30, twinkle=True)


def closed(cv, c):
    drift(cv, c.t, 40, 0xAAFFE8D0, (120, 90))
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 015  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(sun_ridge=glitter, sit_wide=glitter, sit_close=glitter, bare_head=glitter, bare_hands=glitter, rook_gape=glitter, rook_bell=blown,
            rook_off=blown, north_face=blown, hall_climb=blown, top_arms=blown, down_sway=dusk_snow, dizzy_pov=swim, collapse=dusk_snow,
            haul=dusk_snow, sun_sink=dusk_snow, sherpa_leave=dusk_snow, house_night=house_stars, night_alone=night_sky, night_face=night_sky,
            team_climb=glitter, find_pov=glitter, hall_talks=glitter, team_stare=glitter, rook_drop=glitter, summit_near=glitter, tea=glitter,
            ladder_up=blown, carry_down=blown, book_desk=motes, empty_crest=blown, rook_hatoff=glitter, signoff=closed)
