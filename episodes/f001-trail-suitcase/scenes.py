"""Reddit File 001 - the suitcase on the running trail. The story is filmed in 3D (world3d.py). This file holds the flat
graphic inserts (the story card, the 50 km route, shoe versus boot, the missing poster, Rook's theory wall) and the 2D
overlays drawn on top of 3D shots (drifting pollen, patrol-car flashes, stamps)."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
RED = 'E5392F'


def rnd(i, salt=0):
    x = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - math.floor(x)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('2A3A26')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def wall(cv, t):
    """Rook's wall for this file: pine green with drifting contour lines, like a trail map."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1F3A2A')), (1, h('0C1711'))])
    for j in range(9):
        path = skia.Path()
        for i in range(0, W + 41, 40):
            y = 160 + j * 215 + 46 * math.sin(i / 170 + j * 1.3 + t * 0.5) + 22 * math.sin(i / 61 + j)
            (path.moveTo if i == 0 else path.lineTo)(i, y)
        cv.drawPath(path, P(0x22FFFFFF, 3))
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(h('FF7A1A'), 10))


def pinned(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 30, 20, P(h(RED)))
    cv.drawCircle(-5, -h_ / 2 + 25, 7, P(0x88FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col='FFD866'):
    if k <= 0:
        return
    k = min(1.0, k)
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, h(col))
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.42, size, INK, None)
    cv.restore()


def stamp_at(cv, text, x, y, size, k, col='FFB000', ang=-5):
    if k <= 0:
        return
    k = min(1.0, k)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
    Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
    cv.restore()


# ------------------------------------------------------------------ flat inserts
def post_card(cv, c):
    """Where the story comes from: one Reddit user's account. Nobody has checked it."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A1D24')), (1, h('0B0D12'))])
    for i in range(14):
        y = (i * 173 + c.t * 60) % (H + 100) - 50
        cv.drawRoundRect(skia.Rect.MakeXYWH(60 + (i % 3) * 30, y, 960 - (i % 4) * 120, 16), 8, 8, P(0x10FFFFFF))
    k = 1 - (1 - min(1, c.lt / 0.25)) ** 3
    top = 430 + (1 - k) * 500
    cv.drawRoundRect(skia.Rect.MakeXYWH(70, top, 940, 650), 36, 36, P(h('F4EEDF')))
    cv.drawCircle(170, top + 100, 48, P(h('8A90A6')))
    cv.drawCircle(170, top + 88, 18, P(h('F4EEDF')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(140, top + 108, 60, 34), 16, 16, P(h('F4EEDF')))
    Wd.text_card(cv, 'A REDDIT USER SAYS', 250, top + 118, 54, INK, None, center=False)
    for i, (txt, at_) in enumerate((('A HUGE SUITCASE', 0.2), ('A MAN IN BOOTS', 0.4), ('THEN THE POLICE', 0.6))):
        kk = min(1, max(0, (c.lt - at_) / 0.14))
        if kk > 0:
            cv.drawCircle(150, top + 262 + i * 150, 14, P(h('FF7A1A')))
            Wd.text_card(cv, txt, 200 - (1 - kk) * 60, top + 290 + i * 150, 84, INK, None, center=False)
    stamp_at(cv, 'NOT VERIFIED', 540, top + 770, 100, (c.lt - 0.8) / 0.12, RED, -4)


def fifty_card(cv, c):
    """He says he is out running 50 km: a long loop draws itself on the wall."""
    wall(cv, c.t)
    n = int(90 * min(1, c.lt / 0.9))
    path = skia.Path()
    for i in range(n + 1):
        a = i / 90 * 2 * math.pi
        x = 540 + 380 * math.sin(a) * (1 + 0.18 * math.sin(3 * a))
        y = 760 + 430 * math.cos(a) * (1 + 0.12 * math.cos(2 * a + 1))
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    cv.drawPath(path, P(0x66000000, 34))
    cv.drawPath(path, P(h('FF7A1A'), 18))
    cv.drawCircle(540, 1190, 26, P(h('F4EEDF')))
    card(cv, 'HE SAYS:', 400, 660, 420, 130, -5, 62, (c.lt - 0.2) / 0.14, 'F4EEDF')
    stamp_at(cv, '50 KM', 560, 900, 250, (c.lt - 0.55) / 0.12, 'FFB000', -4)


def shoe(cv, x, y, s, boot):
    """Side view of a running shoe or a heavy work boot, toe to the right."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    p = skia.Path()
    if boot:
        pts = [(-150, -230), (-30, -230), (-20, -60), (120, -30), (170, 20), (170, 70), (-160, 70)]
        col, sole = h('3A2A1C'), h('120E0A')
    else:
        pts = [(-150, -70), (-60, -80), (0, -30), (110, -10), (170, 30), (170, 60), (-160, 60)]
        col, sole = h('F4F4F4'), h('FF7A1A')
    for i, q in enumerate(pts):
        (p.moveTo if i == 0 else p.lineTo)(*q)
    p.close()
    cv.drawPath(p, P(col))
    cv.drawPath(p, P(INK, 8))
    cv.drawRoundRect(skia.Rect.MakeLTRB(-172, 56, 182, 100 if boot else 86), 12, 12, P(sole))
    if boot:
        for i in range(5):
            cv.drawLine(-70, -200 + i * 34, -24, -190 + i * 34, P(h('C89A3A'), 9))
        for i in range(6):
            cv.drawRect(skia.Rect.MakeXYWH(-160 + i * 58, 100, 34, 18), P(sole))
    else:
        for i in range(3):
            cv.drawLine(-40 + i * 30, -40 + i * 6, -10 + i * 30, -8 + i * 6, P(h('8A90A6'), 9))
        cv.drawLine(-120, 20, 60, 20, P(h('D8F23A'), 14))
    cv.restore()


def boots_vs(cv, c):
    """A running shoe against a work boot. Fifty kilometres in those?"""
    wall(cv, c.t)
    k1 = 1 - (1 - min(1, c.lt / 0.18)) ** 3
    pinned(cv, 300, 620, 440, 460, -4)
    shoe(cv, 300, 660, 1.0 * k1, False)
    k2 = min(1, max(0, (c.lt - 0.25) / 0.18))
    if k2 > 0:
        pinned(cv, 770, 980, 480, 600, 3)
        shoe(cv, 770, 1100, 1.15 * (1 - (1 - k2) ** 3), True)
    if c.lt > 0.5:
        k3 = min(1, (c.lt - 0.5) / 0.1)
        L = 230 * k3
        cv.drawLine(770 - L, 1000 - L, 770 + L, 1000 + L, P(h(RED), 34))
        cv.drawLine(770 - L, 1000 + L, 770 + L, 1000 - L, P(h(RED), 34))
    stamp_at(cv, '50 KM?', 380, 1420, 200, (c.lt - 0.7) / 0.12, 'FFB000', -6)


def missing_card(cv, c):
    """The search. A poster with no name and no face: the account does not say who was missing."""
    wall(cv, c.t)
    on = (c.t * 2.6) % 1 < 0.5
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(h('FF2A1E') if on else h('2A6CFF'), a=0.10))
    k = 1 - (1 - min(1, c.lt / 0.3)) ** 3
    cv.save()
    cv.translate(540, 800)
    cv.rotate(-2 + 1.5 * math.sin(c.t * 0.8))
    cv.scale(0.8 + 0.2 * k + 0.04 * c.k, 0.8 + 0.2 * k + 0.04 * c.k)
    pinned(cv, 0, 0, 700, 940, 0)
    Wd.text_card(cv, 'MISSING', 0, -290, 130, h(RED), None)
    cv.drawRect(skia.Rect.MakeXYWH(-230, -230, 460, 470), P(h('C8C4B4')))
    cv.drawCircle(0, -70, 100, P(h('8A8678')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-170, 50, 340, 190), 90, 90, P(h('8A8678')))
    for i in range(3):
        cv.drawRoundRect(skia.Rect.MakeXYWH(-250, 290 + i * 46, 500 - i * 110, 20), 10, 10, P(h('B8B4A4')))
    cv.restore()
    card(cv, 'POLICE ON THE TRAILS', 540, 1530, 800, 140, 2, 62, (c.lt - 0.45) / 0.16, 'F4EEDF')


def theory_board(cv, c):
    """Rook's wall: the case, two guesses and a question mark."""
    wall(cv, c.t)
    k = min(1, c.lt / 0.2)
    s = 0.75 + 0.25 * (1 - (1 - k) ** 3)
    pinned(cv, 540, 600, 720 * s, 560 * s, -2.5)
    cv.save()
    cv.translate(540, 600)
    cv.rotate(-2.5)
    cv.scale(s, s)
    photo(cv, 'case', 0, 24, 660, 440, (0.5, 0.5))
    cv.restore()
    card(cv, 'LOST LUGGAGE?', 340, 1010, 560, 150, -4, 64, (c.lt - 0.15) / 0.14)
    card(cv, 'OR SOMETHING ELSE?', 610, 1200, 760, 150, 3, 64, (c.lt - 0.45) / 0.14, 'F4EEDF')
    q = (c.lt - 0.75) / 0.15
    if q > 0:
        cv.save()
        cv.translate(880, 330)
        cv.rotate(10 * math.sin(c.t * 3))
        cv.scale(1.7 - 0.7 * min(1, q), 1.7 - 0.7 * min(1, q))
        Wd.text_card(cv, '?', 0, 90, 280, h('FFB000'), 0xFF000000)
        cv.restore()


SHOTS = {f.__name__: f for f in (post_card, fifty_card, boots_vs, missing_card, theory_board)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(cv, c, text, x, y, size, at=0.25, col='FFB000', ang=-5):
    if c.lt > at:
        stamp_at(cv, text, x, y, size, (c.lt - at) / 0.12, col, ang)


def pollen(cv, c):
    """Seeds and dust drifting through the trees."""
    Wd.particles(cv, W, H, c.t, 46, Wd.alpha(h('F4F0C8'), 0.4), 23, size=(2, 6), drift=(28, -14), wobble=26)


def flashes(cv, c):
    """Patrol-car light washing over everything, red then blue."""
    on = (c.t * 2.6) % 1 < 0.5
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(h('FF2A1E') if on else h('2A6CFF'), a=0.09))
    Wd.particles(cv, W, H, c.t, 30, Wd.alpha(h('DCE6FF'), 0.3), 29, size=(2, 5), drift=(18, -10), wobble=20)


def hook_fx(cv, c):
    pollen(cv, c)


def trail_stamp(cv, c):
    pollen(cv, c)
    stamp(cv, c, 'THE TRAIL', 540, 430, 140, 0.3, 'FFFFFF', -4)


def never(cv, c):
    pollen(cv, c)
    stamp(cv, c, 'HE NEVER TOUCHES IT', 540, 430, 80, 0.35, 'FFB000', 3)


def boots(cv, c):
    pollen(cv, c)
    stamp(cv, c, 'BOOTS', 540, 470, 220, 0.3, RED, -5)


def unverified(cv, c):
    pollen(cv, c)


def watching(cv, c):
    pollen(cv, c)
    stamp(cv, c, 'NOBODY KNOWS', 540, 300, 110, 0.4, 'FFFFFF', 3)


def your_theory(cv, c):
    pollen(cv, c)
    stamp(cv, c, 'YOUR THEORY?', 540, 430, 116, 0.35, 'FFB000', -4)


def spot(cv, c):
    flashes(cv, c)
    stamp(cv, c, 'RIGHT HERE', 540, 430, 130, 0.5, 'FFFFFF', -3)


def still_open(cv, c):
    pollen(cv, c)
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'REDDIT FILE 001  STILL OPEN', 0, 90, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(suitcase_cu=hook_fx, runner_stop=pollen, grass_pov=pollen, man_out=pollen, rook_sign=unverified, trail_aerial=trail_stamp,
            runner_jog=pollen, suitcase_wide=pollen, rook_crouch=pollen, man_block=pollen, man_cu=pollen, case_between=never,
            rook_lean=pollen, boots_cu=boots, runner_eyes=pollen, runner_flee=pollen, police_lights=flashes, cops_search=flashes,
            runner_points=flashes, grass_reverse=spot, man_watch=watching, rook_cam=your_theory, trail_dusk=pollen, rook_tag=pollen,
            signoff=still_open)
