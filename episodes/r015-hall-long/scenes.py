"""Case 015, the full case file (16:9) - Lincoln Hall. The story is filmed in 3D (world3d.py). This file holds the
flat inserts (the DECLARED DEAD stamp, Rook's case board framed in climbing rope, the 1984 route card, the nine-hour
clock, the crossed-out oxygen bottle and sleeping bag, the plain name card for David Sharp, the drawn hands and
foot, the 2006-2012 line), the 2D overlays drawn on top of 3D shots (ice glitter, blown snow, stars, the swimming
haze of altitude sickness, the sign-off) and the thumbnail. Every card is a drawing made for this film; none of
them reproduces a real document, photograph, book cover, medical image, map or logo."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F0E8D2'), h('D8362A'), h('3EC46A')
TEAL, NIGHT, WHITE = h('1F7FA0'), h('0A1030'), 0xFFFFFFFF


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 91.3458 + j * 47.7231) * 24634.6345) % 1


def fit(cv, s, x, y, size, maxw, color=WHITE, stroke=0xFF000000):
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
    cv.drawRoundRect(skia.Rect.MakeLTRB(50, 46, W - 50, H - 46), 36, 36, P(h('1E3A5C')))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(50, 46, W - 50, H - 46))
    for i in range(200):                                          # felt flecks
        x, y = rn(i, 1) * W, rn(i, 2) * H
        cv.drawLine(x, y, x + 14, y + 6, P(h('2C5078'), 3, a=0.5))
    for i in range(5):                                            # a slow band of light, so the board is never still
        x = ((t * 190 + i * 520) % (W + 800)) - 400
        cv.drawPath(poly([(x, 0), (x + 150, 0), (x - 170, H), (x - 320, H)]), P(0xFF7FB4E8, a=0.06))
    cv.restore()

    def twist(x0, y0, x1, y1):
        n = int(math.hypot(x1 - x0, y1 - y0) / 30)
        cv.drawLine(x0, y0, x1, y1, P(h('C85A10'), 30))
        for i in range(n + 1):
            k = i / max(1, n)
            x, y = lerp(x0, x1, k), lerp(y0, y1, k)
            dx, dy = (0, 13) if abs(x1 - x0) > abs(y1 - y0) else (13, 0)
            cv.drawLine(x - dx - 7, y - dy + 7 * (dx > 0), x + dx + 7, y + dy - 7 * (dx > 0), P(TEAL if i % 3 == 0 else ORANGE, 11))
    twist(62, 58, W - 62, 58)
    twist(62, H - 58, W - 62, H - 58)
    twist(62, 58, 62, H - 58)
    twist(W - 62, 58, W - 62, H - 58)
    for x, y in ((62, 58), (W - 62, 58), (62, H - 58), (W - 62, H - 58)):
        cv.drawCircle(x, y, 27, P(h('D8DCE4')))
        cv.drawCircle(x, y, 12, P(h('3A3F4C')))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.5, 0x00000000), (1, 0x66000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, pins=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if pins:
        for sx in (-1, 1):                                        # two orange pins
            cv.drawCircle(sx * (w_ / 2 - 56), -h_ / 2 + 30, 18, P(ORANGE))
            cv.drawCircle(sx * (w_ / 2 - 56) - 5, -h_ / 2 + 25, 6, P(0xFFFFD0A0))
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=64):
    card(cv, x, y, w_, h_, ang, col, pins=False)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    for i, s in enumerate(lines):
        fit(cv, s, 0, (i - (len(lines) - 1) / 2) * size * 1.12 + size * 0.36, size, w_ - 50, INK, None)
    cv.restore()


def pop_note(cv, lt, t0, x, y, w_, h_, ang, col, lines, size=64):
    if lt < t0:
        return
    j = ease((lt - t0) / 0.14)
    cv.save()
    cv.translate(x, y)
    cv.scale(1.3 - 0.3 * j, 1.3 - 0.3 * j)
    note(cv, 0, 0, w_, h_, ang, col, lines, size)
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


def twinkle(cv, t, n=90, top=760, seed=4):
    for i in range(n):
        x, y = rn(i, seed) * W, rn(i, seed + 1) * top
        a = 0.35 + 0.65 * abs(math.sin(t * (1.5 + 3 * rn(i, seed + 2)) + i))
        cv.drawCircle(x, y, 2.0 + 3.0 * rn(i, seed + 3), P(0xFFF4F8FF, a=a))


def drift(cv, t, n=50, col=0xCCF4F8FF, vel=(-70, 230), size=(3, 8), seed=5):
    Wd.particles(cv, W, H, t, n, col, seed, size=size, drift=vel, wobble=26)


def bands(cv, t, col=0xFF7FB4E8, a=0.08):
    for i in range(6):
        x = ((t * 260 + i * 430) % (W + 900)) - 450
        cv.drawPath(poly([(x, 0), (x + 220, 0), (x - 180, H), (x - 400, H)]), P(col, a=a))


def dashed(col, w_, on=16, off=14):
    pa = P(col, w_)
    pa.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    return pa


def pop_photo(cv, c, name, x, y, w_, h_, ang, focus):
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    card(cv, 0, 0, w_ + 60, h_ + 90, ang)
    cv.rotate(ang)
    photo(cv, name, 0, 18, w_, h_, focus)
    cv.restore()


# ------------------------------------------------------------------ flat inserts
def stamp_dead(cv, c):
    """'Last night, he was declared dead.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A1030')), (0.7, h('2A2458')), (1, h('120E24'))])
    twinkle(cv, c.t, 120, 700)
    z = 1.0 + 0.06 * c.k
    cv.save()
    cv.translate(960, 800)
    cv.scale(z, z)
    cv.translate(-960, -800)
    cv.drawPath(poly([(-80, 900), (520, 760), (900, 690), (1090, 700), (1460, 800), (2000, 880), (2000, 1120), (-80, 1120)]), P(h('05060E')))
    cv.drawPath(poly([(520, 760), (900, 690), (1090, 700), (1180, 745), (860, 775)]), P(h('232A52')))
    cv.restore()
    drift(cv, c.t, 50, 0x88F4F8FF, (-240, 110))
    if c.lt > 0.5:
        stamp(cv, 'DECLARED DEAD', 960, 330, -6, min(1, (c.lt - 0.5) / 0.12), 150)
    if c.lt > 1.25:
        k2 = min(1, (c.lt - 1.25) / 0.12)
        fit(cv, 'LAST NIGHT', 960, 600 + 40 * (1 - k2), 120, 1200, AMBER)


def pin_no(cv, c):
    rope_board(cv, c.t)
    pop_photo(cv, c, 'peak', 560, 420, 720, 480, -3, (0.5, 0.35))
    fit(cv, '2006', 400, 830, 84, 400, WHITE, None)
    fit(cv, 'EVEREST', 720, 830, 76, 420, WHITE, None)
    if c.lt > 0.1:
        cv.drawLine(960, 420, 1040, 420, P(ORANGE, 8))
        note(cv, 1400, 400, 760, 300, 3, h('FFD866'), ['DEAD MEN', "DON'T SIT UP"], 92)
    if c.k > 0.5:
        stamp(cv, 'NO CHANCE', 1380, 680, -9, min(1, (c.k - 0.5) * c.d / 0.1), 128)


def pin_hall(cv, c):
    rope_board(cv, c.t)
    pop_photo(cv, c, 'hall', 540, 450, 600, 580, 2, (0.5, 0.45))
    if c.lt > 0.15:
        cv.drawLine(880, 330, 1010, 330, P(ORANGE, 8))
    pop_note(cv, c.lt, 0.15, 1400, 220, 760, 160, -2, PAPER, ['LINCOLN HALL'], 96)
    pop_note(cv, c.lt, 1.25, 1330, 410, 600, 130, 3, h('FFD866'), ['AUSTRALIAN'], 80)
    pop_note(cv, c.lt, 1.75, 1480, 570, 480, 130, -3, h('FFD866'), ['CLIMBER'], 80)
    pop_note(cv, c.lt, 2.45, 1300, 730, 440, 130, 2, PAPER, ['WRITER'], 80)


def peak_path():
    return poly([(560, 900), (900, 520), (1010, 600), (1180, 250), (1330, 520), (1420, 470), (1700, 900)])


def card_1984(cv, c):
    """The first attempt: a drawn mountain and a dotted line that stops short of the top."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16305A')), (1, h('0A1020'))])
    bands(cv, c.t)
    drift(cv, c.t, 60, 0x88F4F8FF, (-160, 200))
    cv.drawPath(peak_path(), P(h('3A4A6E')))
    cv.drawPath(poly([(1180, 250), (1262, 400), (1200, 380), (1160, 430), (1100, 410)]), P(h('E6ECF8')))
    cv.drawLine(560, 900, 1700, 900, P(h('C9D4E8'), 6))
    fit(cv, '1984', 330, 420, 210, 480, AMBER)
    fit(cv, 'FIRST AUSTRALIAN', 330, 540, 54, 480, WHITE)
    fit(cv, 'EVEREST EXPEDITION', 330, 610, 54, 480, WHITE)
    pts = [(820, 880), (930, 740), (1010, 660), (1090, 520), (1140, 420), (1158, 372)]
    k = ease((c.lt - 0.3) / 1.3)
    n = max(1, int(1 + k * (len(pts) - 1) * 12))
    pa = dashed(ORANGE, 12, 18, 20)
    path = skia.Path()
    path.moveTo(*pts[0])
    for i in range(1, n + 1):
        u = i / 12
        j = min(len(pts) - 2, int(u))
        f = u - j
        path.lineTo(lerp(pts[j][0], pts[j + 1][0], f), lerp(pts[j][1], pts[j + 1][1], f))
    cv.drawPath(path, pa)
    if k >= 1:
        cv.drawCircle(1158, 372, 20, P(ORANGE))
        fit(cv, 'HALL', 1020, 360, 60, 240, WHITE)
    if c.lt > 1.0:                                                # two teammates on the top
        j = ease((c.lt - 1.0) / 0.2)
        for dx in (-16, 16):
            cv.drawCircle(1180 + dx, 236, 15 * j, P(AMBER))
        fit(cv, '2 ON THE SUMMIT', 1500, 250, 56, 440, AMBER)


def nine_hours(cv, c):
    """A clock hand sweeps nine hours while the sky goes from day to dusk."""
    k = ease(c.k * 1.15)
    top = Wd.mix(h('5E9AE6'), h('3A2A68'), k)
    bot = Wd.mix(h('BFD8F4'), h('E0705A'), k)
    Wd.vgrad(cv, 0, 0, W, H, [(0, top), (1, bot)])
    cv.drawPath(poly([(-40, 900), (500, 700), (900, 610), (1100, 620), (1500, 760), (1960, 860), (1960, 1120), (-40, 1120)]), P(h('1A1E38')))
    drift(cv, c.t, 60, 0x99F4F8FF, (-380, 120))
    cx, cy, r = 640, 440, 290
    cv.drawCircle(cx, cy, r + 26, P(h('10141E')))
    cv.drawCircle(cx, cy, r, P(PAPER))
    a0 = -math.pi / 2
    a1 = a0 + k * 2 * math.pi * 9 / 12
    wedge = skia.Path()
    wedge.moveTo(cx, cy)
    wedge.arcTo(skia.Rect.MakeXYWH(cx - r + 16, cy - r + 16, 2 * r - 32, 2 * r - 32), -90, math.degrees(a1 - a0), False)
    wedge.close()
    cv.drawPath(wedge, P(ORANGE, a=0.55))
    for i in range(12):
        a = a0 + i * math.pi / 6
        cv.drawLine(cx + (r - 44) * math.cos(a), cy + (r - 44) * math.sin(a), cx + (r - 14) * math.cos(a), cy + (r - 14) * math.sin(a), P(INK, 12))
    cv.drawLine(cx, cy, cx + (r - 70) * math.cos(a1), cy + (r - 70) * math.sin(a1), P(INK, 20))
    cv.drawCircle(cx, cy, 22, P(INK))
    fit(cv, str(int(round(9 * k))), 1330, 470, 330, 520, AMBER)
    fit(cv, 'HOURS', 1330, 640, 150, 620, WHITE)


def no_card(cv, c):
    """'No oxygen. No sleeping bag.' A drawn bottle and a drawn bag, each crossed out."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A1030')), (1, h('1A1840'))])
    twinkle(cv, c.t, 90, 1080, 9)
    drift(cv, c.t, 40, 0x77F4F8FF, (-200, 90))
    z = 1.0 + 0.06 * c.k
    cv.save()
    cv.translate(560, 420)
    cv.scale(z * 0.62, z * 0.62)
    cv.rotate(-14)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-130, -330, 260, 700), 120, 120, P(ORANGE))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-130, -330, 90, 700), 60, 60, P(0xFFFFA050, a=0.6))
    cv.drawRect(skia.Rect.MakeXYWH(-50, -410, 100, 90), P(h('B8BCC8')))
    cv.drawRect(skia.Rect.MakeXYWH(-90, -450, 180, 50), P(h('8A90A0')))
    cv.drawCircle(120, -425, 46, P(h('E8ECF4')))
    cv.drawLine(120, -425, 142, -452, P(RED, 8))
    cv.restore()
    cv.save()
    cv.translate(1360, 430)
    cv.scale(z, z)
    cv.rotate(10)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-290, -120, 580, 240), 120, 120, P(TEAL))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-290, -120, 190, 240), 110, 110, P(h('2E9CC0')))
    cv.drawOval(skia.Rect.MakeXYWH(-250, -70, 110, 140), P(h('0E3A4C')))
    for i in range(5):
        cv.drawLine(-60 + i * 70, -110, -60 + i * 70, 110, P(h('166480'), 8))
    cv.restore()
    for cx, t0, w_ in ((560, 0.1, 230), (1360, 0.95, 330)):
        k = min(1, max(0.0, c.lt - t0) / 0.1)
        if k > 0:
            for sx in (-1, 1):
                cv.drawLine(cx - sx * w_, 190, cx - sx * w_ + sx * 2 * w_ * k, 190 + 460 * k, P(RED, 38))
    fit(cv, 'NO OXYGEN', 560, 745, 90, 760, WHITE)
    if c.lt > 0.95:
        fit(cv, 'NO SLEEPING BAG', 1360, 745, 90, 860, WHITE)


def sharp_card(cv, c):
    """A plain card for the climber who died on the same route earlier that month. No picture, no stamp."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070A16')), (1, h('1A2038'))])
    drift(cv, c.t, 70, 0x66F4F8FF, (-110, 150), (2, 6))
    z = 1.0 + 0.04 * c.k
    cv.save()
    cv.translate(960, 480)
    cv.scale(z, z)
    cv.translate(-960, -480)
    k = ease((c.lt - 0.2) / 0.5)
    cv.drawLine(960 - 420 * k, 300, 960 + 420 * k, 300, P(h('8FA4E8'), 5, a=0.9))
    if c.lt > 0.9:
        a = ease((c.lt - 0.9) / 0.4)
        Wd.text_card(cv, 'DAVID SHARP', 960, 450, 130, Wd.mix(0x00FFFFFF, WHITE, a), None)
        Wd.text_card(cv, 'BRITISH CLIMBER', 960, 530, 50, Wd.mix(0x00C8D4F0, h('C8D4F0'), a), None, weight=600)
    if c.lt > 1.8:
        a = ease((c.lt - 1.8) / 0.3)
        Wd.text_card(cv, 'SAME MONTH.  SAME ROUTE.', 960, 700, 76, Wd.mix(0x00FFB000, AMBER, a), None)
    cv.restore()


def finger(cx, top, w_, len_):
    return skia.Rect.MakeXYWH(cx - w_ / 2, top, w_, len_)


def cost_tips(cv, c):
    """Two drawn hands lose their fingertips to dotted outlines; then a drawn foot loses one toe."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E3A5C')), (1, h('0A1020'))])
    bands(cv, c.t, a=0.1)
    drift(cv, c.t, 90, 0x99F4F8FF, (-140, 380))
    z = 1.0 + 0.05 * c.k
    cv.translate(960, 480)
    cv.scale(z, z)
    cv.translate(-960, -480)
    fit(cv, 'THE COST', 960, 150, 110, 900, WHITE)
    skin, line = h('E2B694'), h('F4F8FF')
    k_f = ease((c.lt - 1.5) / 0.4)                                # "the tips of his fingers"
    k_t = ease((c.lt - 2.7) / 0.3)                                # "and one toe"
    s = 70
    for side, cx in ((-1, 420), (1, 900)):
        cy = 470
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
    fit(cv, 'FINGERTIPS', 660, 780, 76, 800, AMBER if k_f > 0 else WHITE)
    fx, fy = 1460, 520
    cv.drawRoundRect(skia.Rect.MakeXYWH(fx - 130, fy - 60, 260, 210), 80, 80, P(skin))
    for i in range(5):
        w_ = 66 - i * 7
        x0 = fx - 128 + i * 56 + (66 - w_) / 2 - 4
        r = skia.Rect.MakeXYWH(x0, fy - 124 + i * 10, w_, 86 - i * 6)
        gone = k_t if i == 0 else 0.0
        if gone < 1:
            cv.drawRoundRect(r, 26, 26, P(skin, a=1 - gone))
        if gone > 0:
            cv.drawRoundRect(r, 26, 26, dashed(line, 6))
    fit(cv, 'ONE TOE', 1460, 780, 76, 400, AMBER if k_t > 0 else WHITE)


def years_card(cv, c):
    """2006 to 2012 on one line."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A1838')), (0.6, h('5A3A5E')), (1, h('C0705A'))])
    cv.drawPath(poly([(-40, 940), (420, 800), (800, 730), (1000, 740), (1400, 840), (1960, 900), (1960, 1120), (-40, 1120)]), P(h('120E24')))
    drift(cv, c.t, 50, 0x77FFE8D0, (90, -60), (2, 6))
    fit(cv, 'LINCOLN HALL', 960, 190, 84, 1200, WHITE)
    x0, x1, y = 460, 1460, 470
    k = ease((c.lt - 0.2) / 1.5)
    cv.drawLine(x0, y, x1, y, P(0x66FFFFFF, 10))
    cv.drawLine(x0, y, lerp(x0, x1, k), y, P(AMBER, 14))
    cv.drawCircle(x0, y, 24, P(AMBER))
    cv.drawCircle(lerp(x0, x1, k), y, 24 + 6 * math.sin(c.t * 5), P(AMBER))
    fit(cv, '2006', x0, 400, 96, 400, WHITE)
    if k > 0.97:
        fit(cv, '2012', x1, 400, 96, 400, WHITE)
        fit(cv, 'AGED 56', x1, 580, 56, 400, h('E8D8C8'))
    if c.lt > 1.9:
        j = ease((c.lt - 1.9) / 0.2)
        fit(cv, 'NEARLY SIX MORE YEARS', 960, 730 + 30 * (1 - j), 100, 1500, AMBER)


def pin_true(cv, c):
    rope_board(cv, c.t)
    pop_photo(cv, c, 'sit', 560, 440, 700, 520, 3, (0.5, 0.5))
    if c.lt > 0.1:
        cv.drawLine(950, 360, 1030, 360, P(ORANGE, 8))
        note(cv, 1400, 270, 760, 230, -3, h('FFD866'), ['SURPRISED', 'TO SEE ME?'], 80)
    for i, s_ in enumerate(('DECLARED DEAD', 'FOUND ALIVE')):
        if c.lt > 0.3 + i * 0.4:
            fit(cv, s_, 1400, 500 + i * 100, 80, 760, WHITE if i == 0 else AMBER, None)
    if c.lt > 1.2:
        stamp(cv, 'TRUE', 1420, 740, -8, min(1, (c.lt - 1.2) / 0.12), 120, GREEN)


SHOTS = {f.__name__: f for f in (stamp_dead, pin_no, pin_hall, card_1984, nine_hours, no_card, sharp_card, cost_tips, years_card, pin_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def glitter(cv, c):
    """Ice crystals in the first sunlight, drifting past."""
    Wd.particles(cv, W, H, c.t, 60, 0xEEFFE8C8, 11, size=(3, 7), drift=(210, -70), wobble=30, twinkle=True)


def blown(cv, c):
    """Fine snow blown flat off the crest."""
    Wd.particles(cv, W, H, c.t, 90, 0xCCF4F8FF, 7, size=(3, 7), drift=(1000, 120), wobble=30)
    for j in range(8):
        ph = rn(j, 3)
        x = ((c.t * 2200 * (0.6 + ph)) + ph * 4000) % (W + 900) - 450
        y = (ph * 7919) % H + 80 * math.sin(c.t * 2 + j)
        cv.drawLine(x, y, x + 340, y + 30, P(WHITE, 8 + 6 * ph, a=0.13))


def dusk_snow(cv, c):
    Wd.particles(cv, W, H, c.t, 70, 0xAAFFD8C0, 13, size=(3, 7), drift=(-600, 100), wobble=30)


def night_sky(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0x99C8D8FF, 17, size=(2, 6), drift=(-300, 80), wobble=24, twinkle=True)


def night_snow(cv, c):
    Wd.particles(cv, W, H, c.t, 110, 0x99C8D8FF, 19, size=(2, 6), drift=(-520, 160), wobble=30)


def house_stars(cv, c):
    twinkle(cv, c.t, 50, 330, 23)


def swim(cv, c):
    """Altitude sickness: the edges of his sight close in and pulse."""
    k = ease(c.k * 1.2)
    for i in range(4):
        r = lerp(1700, 640, k) + i * 220 + 40 * math.sin(c.t * 6 + i)
        pa = P(0xFF140A1E, 210, a=min(1.0, 0.25 + 0.5 * k))
        pa.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 90))
        cv.drawCircle(960 + 60 * math.sin(c.t * 3 + i), 520 + 40 * math.cos(c.t * 2.3 + i), r, pa)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFF140A1E, a=0.5 * ease((c.k - 0.6) / 0.4)))


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x88FFF0D0, 29, size=(2, 5), drift=(40, -50), wobble=30, twinkle=True)


def closed(cv, c):
    drift(cv, c.t, 50, 0xAAFFE8D0, (140, 80))
    if c.lt > 0.6:
        k = min(1, (c.lt - 0.6) / 0.15)
        cv.save()
        cv.translate(1380, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 015  CLOSED', 0, 90, 54, WHITE, 0xFF000000)
        cv.restore()


OVER = dict(signoff=closed, dizzy_pov=swim, house_night=house_stars, book_desk=motes, desk_empty=motes, phone_room=motes, leader_order=motes,
            leader_hears=motes, radio_hand=motes, alcove_wide=night_snow, alcove_pass=night_snow, rook_alcove=night_snow)
for _k in ('sun_ridge', 'sit_wide', 'sit_close', 'bare_head', 'bare_hands', 'rook_gape', 'team_climb', 'find_pov', 'hall_talks', 'team_stare', 'rook_drop',
           'summit_near', 'tea', 'rook_hatoff', 'first_light', 'summit_way', 'name_a', 'name_b', 'sit_back', 'suit_open', 'rook_note', 'hall_dazed',
           'boat_look', 'four_think', 'look_back', 'kneel_round', 'oxygen', 'radio_call', 'wait_four', 'rook_ridge', 'camp_rest', 'top_two'):
    OVER[_k] = glitter
for _k in ('rook_bell', 'rook_off', 'north_face', 'hall_climb', 'top_arms', 'ladder_up', 'carry_down', 'empty_crest', 'ledge_look', 'camp_arrive',
           'rook_clap', 'hicamp_go', 'slope_down', 'four_down', 'home_day'):
    OVER[_k] = blown
for _k in ('down_sway', 'collapse', 'haul', 'sun_sink', 'sherpa_leave', 'halluc', 'hall_refuse', 'drag_wide', 'sherpa_spent'):
    OVER[_k] = dusk_snow
for _k in ('night_alone', 'night_face', 'night_wide', 'rook_watch'):
    OVER[_k] = night_sky
OVER['home_day'] = motes


def THUMB(cv, c):
    """1280x720: the 3D still (he sits on the crest at sunrise with a hand lifted, Rook jumping behind him) and a four-word hook on the right."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0E1C34'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(640, 0), (1280, 0)], [0x00000000, 0xE6000000])))
    Wd.text_card(cv, 'DECLARED', 990, 230, 100, WHITE, 0xFF000000)
    Wd.text_card(cv, 'DEAD', 990, 400, 190, RED, 0xFF000000)
    Wd.text_card(cv, 'SAID HELLO', 990, 560, 92, AMBER, 0xFF000000)
