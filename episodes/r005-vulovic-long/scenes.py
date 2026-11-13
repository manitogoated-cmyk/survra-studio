"""Case 005 - Vesna Vulovic. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(Rook's departures-board case wall, the altitude drop, the crew roster, the X-ray, the record card) and the 2D overlays."""
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
ORANGE, AMBER, RED, CREAM = h('FF7A1A'), h('FFB000'), h('E5392F'), h('F4EEDF')


def pop(lt, t0, d=0.14):
    return max(0.0, min(1.0, (lt - t0) / d))


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) pinned to the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('3A5A9A')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def flapboard(cv, t):
    """Rook's case wall for this one: an old split-flap departures board."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('141A30')), (1, h('080A14'))])
    for j in range(13):
        y = 120 + j * 138
        cv.drawRoundRect(skia.Rect.MakeLTRB(50, y, W - 50, y + 112), 10, 10, P(h('1E2644')))
        cv.drawLine(50, y + 56, W - 50, y + 56, P(0x55000000, 4))
        n = 9
        for i in range(n):
            if (i * 7 + j * 3) % 4 == 0:
                continue
            a = 0.10 + 0.06 * math.sin(t * 3 + i + j * 1.7)
            cv.drawRoundRect(skia.Rect.MakeXYWH(70 + i * 106, y + 14, 92, 84), 6, 6, P(0xFFFFFFFF, a=a))
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, W - 14, H - 14), P(ORANGE, 12))


def pinned(cv, x, y, w_, h_, ang, col=CREAM):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 28, 19, P(ORANGE))
    cv.drawCircle(-5, -h_ / 2 + 23, 6, P(0x99FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col=h('FFD866')):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, col)
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.42, size, INK, None)
    cv.restore()


def stamp(cv, text, x, y, ang, size, k, col=RED):
    if k <= 0:
        return
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w_ = f.measureText(text)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
    cv.drawRoundRect(skia.Rect.MakeLTRB(-w_ / 2 - 40, -size * 0.62, w_ / 2 + 40, size * 0.62), 18, 18, P(0xDD0B0E18))
    cv.drawRoundRect(skia.Rect.MakeLTRB(-w_ / 2 - 40, -size * 0.62, w_ / 2 + 40, size * 0.62), 18, 18, P(col, 18))
    Wd.text_card(cv, text, 0, size * 0.36, size, col, None)
    cv.restore()


def jet_icon(cv, x, y, s, col=0xFFFFFFFF, ang=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    cv.drawRoundRect(skia.Rect.MakeLTRB(-70, -11, 70, 11), 11, 11, P(col))
    pth = skia.Path()
    for pts in (((-8, 0), (-44, 62), (-22, 62), (26, 0)), ((-8, 0), (-44, -62), (-22, -62), (26, 0)), ((-70, 0), (-92, -34), (-78, -34), (-52, 0))):
        pth.moveTo(*pts[0])
        for p_ in pts[1:]:
            pth.lineTo(*p_)
        pth.close()
    cv.drawPath(pth, P(col))
    cv.restore()


# ------------------------------------------------------------------ flat inserts
def alt_10k(cv, c):
    """How high: a ruler from the ground to the jet."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E2A66')), (0.7, h('5A8AD8')), (1, h('C8D8F0'))])
    for i in range(6):
        Wd.cloud(cv, 120 + (i * 370) % 900 + 30 * math.sin(c.t + i), 1180 + (i * 113) % 300, 1.6 + 0.3 * (i % 3), 0xEEFFFFFF)
    cv.drawRect(skia.Rect.MakeLTRB(0, 1700, W, H), P(h('E8EEF8')))
    for i in range(7):
        x = 60 + i * 160
        pth = skia.Path()
        pth.moveTo(x, 1712)
        pth.lineTo(x + 46, 1600 - (i % 3) * 30)
        pth.lineTo(x + 92, 1712)
        pth.close()
        cv.drawPath(pth, P(h('1E3D36')))
    top, bot = 330, 1700
    k = pop(c.lt, 0.05, 0.45)
    cv.drawLine(170, bot, 170, lerp(bot, top, k), P(AMBER, 10))
    for i in range(11):
        y = bot - (bot - top) * i / 10
        if y >= lerp(bot, top, k) - 1:
            cv.drawLine(170, y, 250 if i % 5 == 0 else 215, y, P(AMBER, 8))
    jet_icon(cv, 600 + 14 * math.sin(c.t * 3), top + 6 * math.sin(c.t * 5), 2.2)
    k2 = pop(c.lt, 0.4)
    if k2 > 0:
        cv.save()
        cv.translate(600, 700)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        Wd.text_card(cv, '10,160 m', 0, 0, 190, AMBER, 0xFF000000)
        Wd.text_card(cv, '33,330 ft', 0, 110, 84, 0xFFFFFFFF, 0xFF000000)
        cv.restore()
    y = lerp(top + 60, bot - 40, max(0, (c.k - 0.45) / 0.55) ** 2)
    cv.drawCircle(170, y, 26, P(RED))
    cv.drawCircle(170, y, 26, P(0xFFFFFFFF, 6))


def board_fall(cv, c):
    flapboard(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    s = 0.75 + 0.25 * k
    cv.save()
    cv.translate(540, 520)
    cv.rotate(-3)
    cv.scale(s, s)
    pinned(cv, 0, 0, 800, 640, 0)
    photo(cv, 'jet', 0, 24, 730, 510, (0.5, 0.5))
    cv.restore()
    card(cv, '10 KM UP', 320, 930, 480, 170, -5, 92, pop(c.lt, 0.3))
    card(cv, 'NO PARACHUTE', 620, 1105, 700, 170, 4, 84, pop(c.lt, 0.55), CREAM)
    stamp(cv, 'NO CHANCE', 540, 520, -12, 150, pop(c.lt, 0.85))


def roster(cv, c):
    """The mix-up, drawn as a crew roster: two Vesnas, one flight."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2E22')), (1, h('1E1810'))])
    cv.save()
    cv.translate(540, 800)
    cv.rotate(-2)
    cv.drawRect(skia.Rect.MakeXYWH(-450 + 14, -700 + 18, 900, 1110), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-450, -700, 900, 1110), P(CREAM))
    cv.drawRect(skia.Rect.MakeXYWH(-450, -700, 900, 170), P(h('24408A')))
    Wd.text_card(cv, 'CREW ROSTER', 0, -590, 100, 0xFFFFFFFF, None)
    Wd.text_card(cv, 'COPENHAGEN  26 JAN 1972', 0, -450, 52, INK, None)
    rows = ((-260, 'VESNA', ''), (20, 'VESNA', 'V.'))
    k = pop(c.lt, 0.45, 0.35)
    for i, (y, a, b) in enumerate(rows):
        cv.drawRect(skia.Rect.MakeXYWH(-400, y - 110, 800, 230), P(h('E4DCC8')))
        cv.drawRect(skia.Rect.MakeXYWH(-400, y - 110, 800, 230), P(INK, 5))
        Wd.text_card(cv, a, -230, y + 36, 104, INK, None)
        if b:
            Wd.text_card(cv, b, 30, y + 36, 104, h('24408A'), None)
        else:
            cv.drawRect(skia.Rect.MakeXYWH(-40, y - 40, 150, 84), P(INK))
    # the flight tag slides from the first Vesna to the second
    ty = lerp(rows[0][0], rows[1][0], k * k * (3 - 2 * k))
    cv.save()
    cv.translate(250 + 8 * math.sin(c.t * 30) * (1 if 0 < k < 1 else 0), ty)
    cv.rotate(-6)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-150, -70, 300, 140), 14, 14, P(ORANGE))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-150, -70, 300, 140), 14, 14, P(INK, 6))
    Wd.text_card(cv, 'FLT 367', 0, 28, 70, INK, None)
    cv.restore()
    if k >= 1:
        stamp(cv, 'MIX-UP', 0, 290, -8, 120, pop(c.lt, 0.85))
    cv.restore()


def alt_drop(cv, c):
    """The altimeter unwinds to zero."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A1230')), (1, h('2A3458'))])
    for i in range(34):
        x = (i * 173) % W
        y = (H - (c.t * 2600 + i * 311) % (H + 300)) + 150
        cv.drawLine(x, y, x, y + 150 + (i % 3) * 60, P(0xFFFFFFFF, 5, 0.18 + 0.1 * (i % 3)))
    cx, cy, r = 540, 600, 340
    cv.drawCircle(cx, cy, r + 30, P(0xFF000000))
    cv.drawCircle(cx, cy, r + 16, P(h('C8CCD4')))
    cv.drawCircle(cx, cy, r, P(h('10141C')))
    for i in range(10):
        a = math.radians(i * 36 - 90)
        cv.drawLine(cx + math.cos(a) * (r - 60), cy + math.sin(a) * (r - 60), cx + math.cos(a) * (r - 14), cy + math.sin(a) * (r - 14), P(0xFFFFFFFF, 12))
    alt = 10160 * (1 - c.k) ** 1.6
    for frac, ln, wd, col in ((alt / 1000, r - 90, 16, 0xFFFFFFFF), (alt / 10000, r - 190, 26, AMBER)):
        a = math.radians(frac * 360 - 90)
        cv.drawLine(cx, cy, cx + math.cos(a) * ln, cy + math.sin(a) * ln, P(col, wd))
    cv.drawCircle(cx, cy, 34, P(0xFFFFFFFF))
    Wd.text_card(cv, f'{int(alt / 10) * 10:,} m', cx, 1180, 150, RED if alt < 2500 and (c.t * 8) % 1 < 0.5 else AMBER, 0xFF000000)


def xray(cv, c):
    """What the doctors found, on an X-ray light box. Bones only, no detail."""
    Wd.fill(cv, 0, 0, W, H, h('05080E'))
    cv.save()
    cv.translate(150, 130)
    cv.scale(0.66, 0.66)
    cv.drawRoundRect(skia.Rect.MakeLTRB(90, 230, W - 90, 1660), 24, 24, P(h('0E2A44')))
    cv.drawRoundRect(skia.Rect.MakeLTRB(90, 230, W - 90, 1660), 24, 24, P(h('7FD8FF'), 8, 0.6 + 0.2 * math.sin(c.t * 9)))
    bone = P(h('BFEFFF'), 26, 0.85)
    cx = 540
    cv.drawCircle(cx, 470, 105, P(h('BFEFFF'), 22, 0.85))
    cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 52, 540, 104, 70), 18, 18, P(h('BFEFFF'), 18, 0.85))
    for i in range(9):
        cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 30, 640 + i * 54, 60, 40), 10, 10, P(h('BFEFFF'), a=0.85))
    for i in range(4):
        for s in (-1, 1):
            cv.drawArc(skia.Rect.MakeXYWH(cx - 190 if s < 0 else cx - 10, 680 + i * 70, 200, 110), 180 if s < 0 else 270, 90, False, P(h('BFEFFF'), 14, 0.7))
    cv.drawLine(cx - 150, 1150, cx + 150, 1150, bone)
    for s in (-1, 1):
        cv.drawLine(cx + s * 110, 1170, cx + s * 130, 1380, bone)
        cv.drawLine(cx + s * 130, 1410, cx + s * 120, 1610, bone)
    marks = ((cx + 90, 430, 'SKULL', 0.12), (cx + 40, 880, 'SPINE', 0.42), (cx + 150, 1330, 'LEGS', 0.72))
    for x, y, txt, t0 in marks:
        k = pop(c.lt / max(0.3, c.d), t0, 0.1)
        if k <= 0:
            continue
        rr = 70 + 60 * (1 - k)
        cv.drawCircle(x, y, rr, P(ORANGE, 14))
        cv.drawLine(x + rr, y, x + 190, y, P(ORANGE, 10))
        Wd.text_card(cv, txt, x + 200, y + 36, 110, ORANGE, 0xFF000000, center=False)
    cv.restore()


def record(cv, c):
    """The record card."""
    flapboard(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(540, 690)
    cv.rotate(2)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    pinned(cv, 0, 0, 880, 960, 0)
    cv.drawRect(skia.Rect.MakeXYWH(-400, -430, 800, 860), P(h('C89A3A'), 10))
    Wd.text_card(cv, 'WORLD RECORD', 0, -290, 84, h('24408A'), None)
    for i, line in enumerate(('HIGHEST FALL', 'SURVIVED WITHOUT', 'A PARACHUTE')):
        Wd.text_card(cv, line, 0, -170 + i * 80, 64, INK, None)
    Wd.text_card(cv, '10,160 m', 0, 190, 170, h('E5392F'), None)
    Wd.text_card(cv, 'VESNA VULOVIĆ  1972', 0, 275, 52, INK, None)
    cv.restore()
    card(cv, 'DISPUTED 2009', 290, 215, 500, 140, -6, 58, pop(c.lt, 0.25), h('D8D4C8'))
    stamp(cv, 'STILL STANDS', 560, 1085, -7, 110, pop(c.lt, 0.5), h('3DDC84'))


def board_true(cv, c):
    flapboard(cv, c.t)
    pinned(cv, 540, 600, 740, 860, 2)
    cv.save()
    cv.translate(540, 600)
    cv.rotate(2)
    photo(cv, 'vesna', 0, 24, 660, 720, (0.5, 0.22))
    cv.restore()
    stamp(cv, 'TRUE', 560, 800, -14, 190, pop(c.lt, 0.22, 0.12))
    card(cv, 'FELL 10,160 M', 320, 1125, 540, 160, -5, 72, pop(c.lt, 0.5))
    card(cv, 'WALKED AGAIN', 770, 1010, 500, 150, 4, 64, pop(c.lt, 0.7), CREAM)


SHOTS = {f.__name__: f for f in (alt_10k, board_fall, roster, alt_drop, xray, record, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 70, 0x99FFFFFF, 5, size=(3, 8), drift=(-60, 220), wobble=30)


def wind(cv, c):
    for i in range(16):
        y = (i * 211 + int(c.t * 2400)) % (H + 400) - 200
        x = (i * 137) % W
        cv.drawLine(x, H - y, x, H - y - 220, P(0xFFFFFFFF, 6, 0.16))


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 005  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(rook_hat=snow, hill_wide=snow, impact=snow, villager=snow, wreck_in=snow, rook_lantern=snow, rescuers=snow,
            tail_fall=wind, fall_top=wind, plunge=wind, signoff=closed)
