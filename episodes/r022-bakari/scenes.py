"""Case 022 - Bahia Bakari, the only survivor of Yemenia Flight 626 (30 June 2009). The story is filmed in 3D
(world3d.py). This file holds the flat inserts (two cards drawn like a child's picture of what she believed
had happened, and Rook's case board on a sheet of riveted aircraft skin) and the 2D overlays drawn on top of
3D shots (spray, a few stars, dust in the hospital light, the sign-off). Every card is a drawing
made for this film: the aeroplane on it is a generic shape with no livery, and none of it reproduces a real
photograph, document or logo."""
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
ORANGE, AMBER, PAPER = h('FF7A1A'), h('FFB000'), h('EFE6CC')
CHALK = h('F4EEDC')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 51.37 + j * 87.13) * 24634.63) % 1


def font(size):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def paper_night(cv, c):
    """Dark blue paper with crayon stars: both 'what she believed' cards are drawn on it."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16264A')), (0.7, h('1C3458')), (1, h('12203A'))])
    for i in range(46):
        x, y = 40 + 1000 * rn(i, 1), 60 + 1050 * rn(i, 2)
        r = 3 + 5 * rn(i, 3)
        a = 0.35 + 0.5 * abs(math.sin(c.t * 2.2 + i))
        cv.drawLine(x - r, y, x + r, y, P(CHALK, 3, a=a))
        cv.drawLine(x, y - r, x, y + r, P(CHALK, 3, a=a))
    fit(cv, 'WHAT SHE BELIEVED', 540, 250, 84, 940, AMBER)


def plane_mark(cv, x, y, s, ang, lights=1.0):
    """A plain airliner in chalk, nose to the right. No livery."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    body = skia.Path()
    body.addRoundRect(skia.Rect.MakeXYWH(-300, -44, 560, 88), 44, 44)
    cv.drawPath(body, P(CHALK))
    cv.drawPath(poly([(250, -40), (330, -6), (330, 12), (250, 44)]), P(CHALK))                 # nose
    cv.drawPath(poly([(-300, -30), (-370, -150), (-310, -150), (-220, -40)]), P(CHALK))       # fin
    cv.drawPath(poly([(-40, 10), (-170, 150), (-110, 150), (80, 20)]), P(h('D8D2C0')))        # wing
    cv.drawPath(poly([(-290, 0), (-360, 50), (-320, 52), (-240, 12)]), P(h('D8D2C0')))        # tailplane
    for i in range(11):
        cv.drawRoundRect(skia.Rect.MakeXYWH(-240 + 42 * i, -22, 22, 26), 6, 6, P(h('FFD060'), a=lights))
    cv.drawPath(body, P(INK, 6))
    cv.restore()


def child_mark(cv, x, y, s, ang):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    for (a, b) in (((0, -6), (0, 44)), ((0, 8), (-26, -18)), ((0, 8), (26, -18)), ((0, 44), (-18, 80)), ((0, 44), (18, 80))):
        cv.drawLine(a[0], a[1], b[0], b[1], P(h('E0705A'), 13))
    cv.drawCircle(0, -26, 22, P(h('8A5A3C')))
    for sx in (-1, 1):
        cv.drawCircle(sx * 22, -42, 10, P(h('15121A')))
    cv.restore()


def waves(cv, c, y0):
    cv.drawRect(skia.Rect.MakeXYWH(0, y0, W, H - y0), P(h('0D3440')))
    for j in range(5):
        pts = [(x, y0 + 40 * j + 14 * math.sin(x * 0.02 + c.t * 2.2 + j * 1.7)) for x in range(-20, W + 40, 30)]
        cv.drawPath(poly(pts, False), P(h('3E8C9C'), 7, a=0.8 - 0.12 * j))


# ---------------------------------------------------------------- inserts
def fell_card(cv, c):
    """'She thinks she just fell out of the plane.' The aeroplane flies on across the night; one small figure drops away from it."""
    paper_night(cv, c)
    waves(cv, c, 1560)
    px = lerp(330, 760, ease(c.k))
    plane_mark(cv, px, 560 + 8 * math.sin(c.t * 3), 1.0, -3)
    k = ease((c.k - 0.12) / 0.8)
    fx, fy = 330 - 60 * k, 650 + 560 * k * k
    n = int(k * 9)
    for i in range(n):
        q = i / 9
        cv.drawCircle(330 - 60 * q, 650 + 560 * q * q, 7, P(CHALK, a=0.7))
    child_mark(cv, fx, fy, 1.35, -25 + 50 * k)
    fit(cv, 'JUST HER', 540, 1700, 110, 900, 0xFFFFFFFF)


def landed_card(cv, c):
    """'...and that her mother landed safely without her.' The same aeroplane comes down onto a lit runway and stops."""
    paper_night(cv, c)
    cv.drawRect(skia.Rect.MakeXYWH(0, 1040, W, H - 1040), P(h('1A2230')))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1040, W, 16), P(h('3A4458')))
    for i in range(9):
        on = 0.5 + 0.5 * math.sin(c.t * 6 + i)
        cv.drawCircle(70 + 118 * i, 1100, 13, P(AMBER, a=0.5 + 0.5 * on))
        cv.drawRect(skia.Rect.MakeXYWH(40 + 118 * i, 1150, 64, 12), P(CHALK, a=0.5))
    k = ease(c.k / 0.7)
    x = lerp(-320, 560, k)
    y = lerp(520, 960, ease(c.k / 0.5))
    plane_mark(cv, x, y, 1.0, lerp(10, 0, ease(c.k / 0.5)))
    if c.k > 0.5:                                                   # wheels down
        for dx in (-150, 60, 200):
            cv.drawCircle(x + dx, y + 62, 18, P(INK))
            cv.drawCircle(x + dx, y + 62, 18, P(CHALK, 5))
    if c.k > 0.55:
        fit(cv, 'EVERYONE SAFE', 540, 1640, 104, 900, 0xFFFFFFFF)
    if c.k > 0.7:
        fit(cv, 'EXCEPT HER', 540, 1760, 104, 900, AMBER)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('14384A')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def board(cv, c):
    """Rook's board for this case: a sheet of riveted aircraft skin, a photograph of the girl at the wreckage, two figures. No stamp on this one."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('20323E')), (0.5, h('16242E')), (1, h('0A1218'))])
    for i in range(4):                                             # skin panels
        y = 150 + 405 * i
        cv.drawRect(skia.Rect.MakeXYWH(60, y, 960, 398), P((h('C4CAD2'), h('B6BCC6'))[i % 2]))
        for j in range(21):                                        # rivets along each seam
            cv.drawCircle(84 + 45.6 * j, y + 18, 6, P(h('8A929E')))
            cv.drawCircle(84 + 45.6 * j, y + 380, 6, P(h('8A929E')))
    for i in range(9):                                             # scratches
        x, y = 100 + 860 * rn(i, 4), 200 + 1500 * rn(i, 5)
        cv.drawLine(x, y, x + 90 * rn(i, 6) + 30, y + 26 * rn(i, 7), P(h('8A929E'), 3, a=0.6))
    Wd.glow(cv, 540, 800, 900, h('9CD8E8'), 0.1)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 690)
    cv.scale(s, s)
    cv.rotate(2.0)
    cv.drawRect(skia.Rect.MakeXYWH(-390 + 12, -400 + 16, 780, 800), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-390, -400, 780, 800), P(PAPER))
    photo(cv, 'girl', 0, -30, 710, 660, (0.5, 0.5))
    cv.restore()
    for x in (210, 870):
        cv.drawCircle(x, 320, 24, P(ORANGE))
        cv.drawCircle(x, 320, 24, P(INK, 5))
    if c.lt > 0.2:
        fit(cv, '153 ON BOARD', 540, 1560, 112, 900, 0xFFFFFFFF)
    if c.lt > 0.4:
        fit(cv, '1 SURVIVOR', 540, 1690, 128, 900, AMBER)


SHOTS = {f.__name__: f for f in (fell_card, landed_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def night(cv, c):
    Wd.particles(cv, W, H, c.t, 20, 0x66DCF0FF, 81, size=(2, 4), drift=(8, -5), wobble=8, twinkle=True)
    Wd.particles(cv, W, H, c.t, 16, 0x77E6F4FA, 83, size=(3, 7), drift=(260, -70), wobble=30)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x99EAF6FF, 85, size=(3, 9), drift=(300, -110), wobble=40)


def glint(cv, c):
    Wd.particles(cv, W, H, c.t, 20, 0x88FFFFFF, 87, size=(2, 5), drift=(24, -12), wobble=18, twinkle=True)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 18, 0x55FFE8C8, 89, size=(2, 5), drift=(10, -14), wobble=14, twinkle=True)


def closed(cv, c):
    glint(cv, c)
    if c.lt > 0.4:
        k = min(1, (c.lt - 0.4) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 022', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(girl_close=night, hands_grip=night, wide_night=night, plane_piece=night, rook_lands=night, rook_doubt=night, in_water=night, voices=night,
            dark_look=night, rook_quiet=night, big_wave=spray, climb_try=night, hold_on=night, face_tired=night, dawn_break=glint, morning=spray,
            boat_far=spray, boat_near=spray, ring_throw=spray, ring_miss=spray, reach_fail=spray, sailor_jump=spray, sailor_swim=spray, lift_aboard=spray,
            blanket=glint, alive=glint, look_back=glint, hospital_wait=dust, hospital_tell=dust, her_face=dust, empty_chair=dust, rook_wrong=dust,
            sea_after=spray, debris_close=spray, signoff=closed)
