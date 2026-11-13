"""Case 005, full case file (16:9) - Vesna Vulovic. The story is filmed in 3D (world3d.py). This file holds the flat graphic
inserts (Rook's departures-board case wall, the altitude, the roster, the route, the clock, the blood-pressure gauge, the
X-ray, the record card), the overlays drawn on top of 3D shots, and the thumbnail."""
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
ORANGE, AMBER, RED, CREAM, GREEN = h('FF7A1A'), h('FFB000'), h('E5392F'), h('F4EEDF'), h('3DDC84')
NAVY = h('24408A')


def pop(lt, t0, d=0.14):
    return max(0.0, min(1.0, (lt - t0) / d))


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


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
    """Rook's case wall for this one: an old split-flap departures board, landscape."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('141A30')), (1, h('080A14'))])
    for j in range(7):
        y = 60 + j * 140
        cv.drawRoundRect(skia.Rect.MakeLTRB(50, y, W - 50, y + 114), 10, 10, P(h('1E2644')))
        cv.drawLine(50, y + 57, W - 50, y + 57, P(0x55000000, 4))
        for i in range(17):
            if (i * 7 + j * 3) % 4 == 0:
                continue
            a = 0.10 + 0.07 * math.sin(t * 3 + i + j * 1.7)
            cv.drawRoundRect(skia.Rect.MakeXYWH(72 + i * 105, y + 14, 92, 86), 6, 6, P(0xFFFFFFFF, a=a))
    cv.drawRect(skia.Rect.MakeLTRB(12, 12, W - 12, H - 12), P(ORANGE, 10))


def pinned(cv, x, y, w_, h_, ang, col=CREAM):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 26, 17, P(ORANGE))
    cv.drawCircle(-5, -h_ / 2 + 21, 5, P(0x99FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col=h('FFD866'), ink=INK):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, col)
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.42, size, ink, None)
    cv.restore()


def stamp_(cv, text, x, y, ang, size, k, col=RED):
    if k <= 0:
        return
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w_ = f.measureText(text)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
    cv.drawRoundRect(skia.Rect.MakeLTRB(-w_ / 2 - 36, -size * 0.62, w_ / 2 + 36, size * 0.62), 16, 16, P(0xDD0B0E18))
    cv.drawRoundRect(skia.Rect.MakeLTRB(-w_ / 2 - 36, -size * 0.62, w_ / 2 + 36, size * 0.62), 16, 16, P(col, 14))
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


def drift_dots(cv, t, n=40, col=0x33FFFFFF, speed=40):
    for i in range(n):
        x = (i * 271 + t * speed * (1 + i % 3)) % (W + 40) - 20
        y = (i * 173 + 30 * math.sin(t * 0.7 + i)) % H
        cv.drawCircle(x, y, 2 + i % 3, P(col))


# ------------------------------------------------------------------ flat inserts
def alt_10k(cv, c):
    """How high: a ruler from the ground to the jet."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E2A66')), (0.7, h('5A8AD8')), (1, h('C8D8F0'))])
    for i in range(7):
        Wd.cloud(cv, 160 + (i * 470) % 1700 + 40 * math.sin(c.t + i), 640 + (i * 113) % 200, 1.5 + 0.3 * (i % 3), 0xEEFFFFFF)
    cv.drawRect(skia.Rect.MakeLTRB(0, 970, W, H), P(h('E8EEF8')))
    for i in range(13):
        x = 40 + i * 150
        pth = skia.Path()
        pth.moveTo(x, 980)
        pth.lineTo(x + 40, 890 - (i % 3) * 26)
        pth.lineTo(x + 80, 980)
        pth.close()
        cv.drawPath(pth, P(h('1E3D36')))
    top, bot = 150, 970
    k = pop(c.lt, 0.05, 0.5)
    cv.drawLine(330, bot, 330, lerp(bot, top, k), P(AMBER, 10))
    for i in range(11):
        y = bot - (bot - top) * i / 10
        if y >= lerp(bot, top, k) - 1:
            cv.drawLine(330, y, 420 if i % 5 == 0 else 380, y, P(AMBER, 8))
    jet_icon(cv, 800 + 60 * c.k + 14 * math.sin(c.t * 3), top + 10 + 6 * math.sin(c.t * 5), 2.0)
    k2 = pop(c.lt, 0.45)
    if k2 > 0:
        cv.save()
        cv.translate(1250, 470)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        Wd.text_card(cv, '10,160 m', 0, 0, 210, AMBER, 0xFF000000)
        Wd.text_card(cv, '33,330 ft', 0, 120, 92, 0xFFFFFFFF, 0xFF000000)
        cv.restore()
    y = lerp(top + 50, bot - 30, max(0, (c.k - 0.4) / 0.6) ** 2)
    cv.drawCircle(330, y, 24, P(RED))
    cv.drawCircle(330, y, 24, P(0xFFFFFFFF, 6))


def board_fall(cv, c):
    flapboard(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    s = 0.8 + 0.2 * k
    cv.save()
    cv.translate(560, 420)
    cv.rotate(-3)
    cv.scale(s, s)
    pinned(cv, 0, 0, 840, 600, 0)
    photo(cv, 'jet', 0, 22, 770, 480, (0.5, 0.5))
    cv.restore()
    card(cv, '10 KM UP', 1330, 250, 560, 180, -4, 100, pop(c.lt, 0.3))
    card(cv, 'NO PARACHUTE', 1400, 480, 800, 180, 3, 92, pop(c.lt, 0.6), CREAM)
    stamp_(cv, 'NO CHANCE', 1000, 690, -8, 150, pop(c.lt, 0.95))


def roster(cv, c):
    """The mix-up, drawn as a crew roster: two Vesnas, one flight."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2E22')), (1, h('1E1810'))])
    cv.save()
    cv.translate(960, 430 + 6 * math.sin(c.t * 1.3))
    cv.rotate(-1.5)
    cv.drawRect(skia.Rect.MakeXYWH(-780 + 14, -380 + 18, 1560, 760), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-780, -380, 1560, 760), P(CREAM))
    cv.drawRect(skia.Rect.MakeXYWH(-780, -380, 1560, 150), P(NAVY))
    Wd.text_card(cv, 'CREW ROSTER', -360, -272, 96, 0xFFFFFFFF, None)
    Wd.text_card(cv, 'COPENHAGEN  26 JAN 1972', 360, -280, 50, 0xFFFFFFFF, None)
    rows = ((-90, 'VESNA', ''), (170, 'VESNA', 'V.'))
    k = ease(pop(c.lt, 0.7, 0.5))
    for y, a, b in rows:
        cv.drawRect(skia.Rect.MakeXYWH(-720, y - 105, 1440, 210), P(h('E4DCC8')))
        cv.drawRect(skia.Rect.MakeXYWH(-720, y - 105, 1440, 210), P(INK, 5))
        Wd.text_card(cv, 'FLIGHT ATTENDANT', -480, y - 40, 40, h('6A6458'), None)
        Wd.text_card(cv, a, -500, y + 60, 104, INK, None)
        if b:
            Wd.text_card(cv, b, -250, y + 60, 104, NAVY, None)
        else:
            cv.drawRect(skia.Rect.MakeXYWH(-330, y - 20, 300, 84), P(INK))
    ty = lerp(rows[0][0], rows[1][0], k)
    cv.save()
    cv.translate(420 + 8 * math.sin(c.t * 30) * (1 if 0 < k < 1 else 0), ty)
    cv.rotate(-5)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-190, -74, 380, 148), 14, 14, P(ORANGE))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-190, -74, 380, 148), 14, 14, P(INK, 6))
    Wd.text_card(cv, 'FLT 367', 0, 30, 84, INK, None)
    cv.restore()
    if k >= 1:
        stamp_(cv, 'MIX-UP', 40, 40, -8, 150, pop(c.lt, 1.35))
    cv.restore()


def alt_drop(cv, c):
    """The altimeter unwinds to zero."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A1230')), (1, h('2A3458'))])
    for i in range(40):
        x = (i * 173) % W
        y = (H - (c.t * 2200 + i * 311) % (H + 300)) + 150
        cv.drawLine(x, y, x, y + 130 + (i % 3) * 50, P(0xFFFFFFFF, 5, 0.18 + 0.1 * (i % 3)))
    cx, cy, r = 600, 450, 320
    cv.drawCircle(cx, cy, r + 30, P(0xFF000000))
    cv.drawCircle(cx, cy, r + 16, P(h('C8CCD4')))
    cv.drawCircle(cx, cy, r, P(h('10141C')))
    for i in range(10):
        a = math.radians(i * 36 - 90)
        cv.drawLine(cx + math.cos(a) * (r - 60), cy + math.sin(a) * (r - 60), cx + math.cos(a) * (r - 14), cy + math.sin(a) * (r - 14), P(0xFFFFFFFF, 12))
    alt = 10160 * (1 - c.k) ** 1.6
    for frac, ln, wd, col in ((alt / 1000, r - 90, 16, 0xFFFFFFFF), (alt / 10000, r - 180, 26, AMBER)):
        a = math.radians(frac * 360 - 90)
        cv.drawLine(cx, cy, cx + math.cos(a) * ln, cy + math.sin(a) * ln, P(col, wd))
    cv.drawCircle(cx, cy, 34, P(0xFFFFFFFF))
    Wd.text_card(cv, f'{int(alt / 10) * 10:,} m', 1340, 500, 190, RED if alt < 2500 and (c.t * 8) % 1 < 0.5 else AMBER, 0xFF000000)


def xray(cv, c):
    """What the doctors found, on an X-ray light box. Bones only, no detail."""
    Wd.fill(cv, 0, 0, W, H, h('05080E'))
    cv.save()
    cv.translate(330, -40)
    cv.scale(0.56, 0.56)
    cv.drawRoundRect(skia.Rect.MakeLTRB(90, 230, 990, 1660), 24, 24, P(h('0E2A44')))
    cv.drawRoundRect(skia.Rect.MakeLTRB(90, 230, 990, 1660), 24, 24, P(h('7FD8FF'), 8, 0.6 + 0.2 * math.sin(c.t * 9)))
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
    sweep = 230 + (c.t * 500) % 1430
    cv.drawLine(90, sweep, 990, sweep, P(h('7FD8FF'), 8, 0.5))
    marks = ((cx + 90, 430, 'FRACTURED SKULL', 0.08), (cx + 40, 880, '3 BROKEN VERTEBRAE', 0.36), (cx + 150, 1330, 'BOTH LEGS BROKEN', 0.62))
    for x, y, txt, t0 in marks:
        k = pop(c.lt / max(0.3, c.d), t0, 0.08)
        if k <= 0:
            continue
        rr = 70 + 60 * (1 - k)
        cv.drawCircle(x, y, rr, P(ORANGE, 14))
        cv.drawLine(x + rr, y, 1080, y, P(ORANGE, 10))
        Wd.text_card(cv, txt, 1110, y + 40, 116, ORANGE, 0xFF000000, center=False)
    cv.restore()


def record(cv, c):
    """The record card."""
    flapboard(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(960, 420)
    cv.rotate(1.5)
    cv.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    pinned(cv, 0, 0, 1180, 700, 0)
    cv.drawRect(skia.Rect.MakeXYWH(-560, -320, 1120, 640), P(h('C89A3A'), 10))
    Wd.text_card(cv, 'WORLD RECORD', 0, -200, 84, NAVY, None)
    Wd.text_card(cv, 'HIGHEST FALL SURVIVED', 0, -100, 66, INK, None)
    Wd.text_card(cv, 'WITHOUT A PARACHUTE', 0, -24, 66, INK, None)
    Wd.text_card(cv, '10,160 m', 0, 170, 180, RED, None)
    Wd.text_card(cv, 'VESNA VULOVIĆ  1972', 0, 260, 52, INK, None)
    cv.restore()
    card(cv, 'DISPUTED 2009', 300, 170, 500, 140, -6, 58, pop(c.lt, 0.3), h('D8D4C8'))
    stamp_(cv, 'STILL STANDS', 1380, 700, -7, 100, pop(c.lt, 0.7), GREEN)


def board_true(cv, c):
    flapboard(cv, c.t)
    pinned(cv, 600, 420, 620, 720, 2)
    cv.save()
    cv.translate(600, 420)
    cv.rotate(2)
    photo(cv, 'vesna', 0, 22, 550, 600, (0.5, 0.2))
    cv.restore()
    stamp_(cv, 'TRUE', 640, 560, -14, 190, pop(c.lt, 0.25, 0.12), GREEN)
    card(cv, 'FELL 10,160 M', 1360, 270, 700, 180, -4, 92, pop(c.lt, 0.55))
    card(cv, 'WALKED AGAIN', 1420, 500, 680, 170, 3, 86, pop(c.lt, 0.8), CREAM)


def gauge(cv, cx, cy, r, val, t):
    """A half-dial: red (low) on the left, green in the middle. val 0..1."""
    cv.drawCircle(cx, cy, r + 34, P(0xFF000000))
    cv.drawCircle(cx, cy, r + 20, P(h('C8CCD4')))
    cv.drawCircle(cx, cy, r, P(h('F4F0E6')))
    rect = skia.Rect.MakeLTRB(cx - r + 50, cy - r + 50, cx + r - 50, cy + r - 50)
    cv.drawArc(rect, 180, 55, False, P(RED, 44))
    cv.drawArc(rect, 235, 80, False, P(GREEN, 44))
    cv.drawArc(rect, 315, 45, False, P(AMBER, 44))
    for i in range(13):
        a = math.radians(180 + i * 15)
        cv.drawLine(cx + math.cos(a) * (r - 110), cy + math.sin(a) * (r - 110), cx + math.cos(a) * (r - 84), cy + math.sin(a) * (r - 84), P(INK, 8))
    a = math.radians(180 + 180 * val + 2.5 * math.sin(t * 17))
    cv.drawLine(cx, cy, cx + math.cos(a) * (r - 70), cy + math.sin(a) * (r - 70), P(INK, 18))
    cv.drawCircle(cx, cy, 30, P(INK))
    Wd.text_card(cv, 'BLOOD PRESSURE', cx, cy + 150, 54, INK, None)


def heart(cv, x, y, s, col):
    pth = skia.Path()
    pth.moveTo(0, 60)
    pth.cubicTo(-110, -20, -60, -110, 0, -40)
    pth.cubicTo(60, -110, 110, -20, 0, 60)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.drawPath(pth, P(col))
    cv.restore()


def bp(cv, c):
    """Her low blood pressure: first the problem at the medical, later the reason she lived."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E2E36')), (1, h('06141A'))])
    drift_dots(cv, c.t)
    out = c.prm.get('mode') == 'out'
    gauge(cv, 520, 520, 360, 0.12 + (0.0 if not out else -0.05 * ease(c.k)), c.t)
    if not out:
        k = pop(c.lt, 0.25)
        if k > 0:
            cv.save()
            cv.translate(1340, 360)
            cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
            Wd.text_card(cv, 'LOW', 0, 0, 260, RED, 0xFF000000)
            cv.restore()
        card(cv, 'AIRLINE MEDICAL', 1340, 520, 760, 150, -2, 78, pop(c.lt, 0.7), CREAM)
        stamp_(cv, 'FAIL?', 1500, 700, -8, 130, pop(c.lt, 1.2))
    else:
        d = max(0.6, c.d)
        card(cv, 'CABIN LOSES PRESSURE', 1340, 210, 900, 140, -2, 66, pop(c.lt, 0.1 * d), CREAM)
        card(cv, 'SHE PASSES OUT FAST', 1340, 400, 900, 140, 2, 70, pop(c.lt, 0.38 * d))
        k = pop(c.lt, 0.66 * d)
        if k > 0:
            heart(cv, 1050, 640, (1.0 + 0.12 * max(0, math.sin(c.t * 9))) * k, RED)
            Wd.text_card(cv, 'HEART HOLDS', 1470, 670, 96, GREEN, 0xFF000000)


def route_map(cv, c):
    """Stockholm - Copenhagen - Zagreb - Belgrade; the crew boards in Copenhagen."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10203C')), (1, h('081020'))])
    for i in range(0, W + 1, 120):
        cv.drawLine(i, 0, i, H, P(0x14FFFFFF, 2))
    for j in range(0, H + 1, 120):
        cv.drawLine(0, j, W, j, P(0x14FFFFFF, 2))
    for x, y, rx, ry in ((1150, 110, 300, 150), (820, 380, 130, 70), (1050, 560, 520, 190), (1180, 800, 420, 130), (520, 640, 300, 200)):
        cv.drawOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry), P(h('1E3A5A')))
    pts = (('STOCKHOLM', 1180, 130), ('COPENHAGEN', 880, 350), ('ZAGREB', 1010, 720), ('BELGRADE', 1260, 790))
    k = pop(c.lt, 0.1, max(0.8, c.d * 0.7))
    seg = k * 3
    for i in range(3):
        a, b = pts[i], pts[i + 1]
        kk = max(0.0, min(1.0, seg - i))
        n = 14
        for j in range(n):
            if j / n < kk:
                x, y = lerp(a[1], b[1], j / n), lerp(a[2], b[2], j / n)
                cv.drawCircle(x, y, 7, P(AMBER if i == 0 else 0x99FFFFFF))
    for name, x, y in pts:
        hot = name == 'COPENHAGEN'
        cv.drawCircle(x, y, 26 if hot else 16, P(ORANGE if hot else 0xFFFFFFFF))
        if hot:
            cv.drawCircle(x, y, 40 + 14 * math.sin(c.t * 6), P(ORANGE, 6))
        if hot:
            Wd.text_card(cv, name, x - 300, y + 24, 72, ORANGE, 0xFF000000)
        else:
            Wd.text_card(cv, name, x + 40, y + 18, 48, 0xFFFFFFFF, 0xFF000000, center=False)
    jet_icon(cv, lerp(1180, 880, min(1, seg)), lerp(130, 350, min(1, seg)) - 60, 1.0, 0xFFFFFFFF, 145)
    card(cv, 'NEW CREW BOARDS', 400, 560, 640, 140, -3, 64, pop(c.lt, 0.9))
    Wd.text_card(cv, 'DC-9  ·  FLIGHT 367', 330, 150, 60, 0xFFFFFFFF, 0xFF000000)


def clock(cv, c):
    """15:15 take-off; 46 minutes later, 16:01."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A2238')), (1, h('0A0E1A'))])
    drift_dots(cv, c.t, 30)
    late = c.prm.get('mode') == 'late'
    cx, cy, r = 560, 460, 340
    cv.drawCircle(cx, cy, r + 30, P(0xFF000000))
    cv.drawCircle(cx, cy, r + 16, P(ORANGE))
    cv.drawCircle(cx, cy, r, P(CREAM))
    for i in range(12):
        a = math.radians(i * 30 - 90)
        cv.drawLine(cx + math.cos(a) * (r - 56), cy + math.sin(a) * (r - 56), cx + math.cos(a) * (r - 16), cy + math.sin(a) * (r - 16), P(INK, 14 if i % 3 == 0 else 8))
    mins = 15 * 60 + 15 + (46 * ease(pop(c.lt, 0.15, max(0.7, c.d * 0.55))) if late else 0.4 * math.sin(c.t * 2))
    if late:                                        # the 46 minutes, shaded
        cv.drawArc(skia.Rect.MakeLTRB(cx - r + 80, cy - r + 80, cx + r - 80, cy + r - 80), 0, (mins - 915) * 6, True, P(Wd.alpha(RED, 0.35)))
    am, ah = math.radians(mins % 60 * 6 - 90), math.radians(mins / 60 % 12 * 30 - 90)
    cv.drawLine(cx, cy, cx + math.cos(ah) * (r - 170), cy + math.sin(ah) * (r - 170), P(INK, 26))
    cv.drawLine(cx, cy, cx + math.cos(am) * (r - 70), cy + math.sin(am) * (r - 70), P(INK, 16))
    a = math.radians((c.t * 360) % 360 - 90)
    cv.drawLine(cx, cy, cx + math.cos(a) * (r - 50), cy + math.sin(a) * (r - 50), P(RED, 6))
    cv.drawCircle(cx, cy, 26, P(INK))
    m = int(round(mins))
    Wd.text_card(cv, f'{m // 60}:{m % 60:02d}', 1370, 380, 250, AMBER, 0xFF000000)
    if late:
        Wd.text_card(cv, '+ 46 MIN', 1370, 560, 120, 0xFFFFFFFF, 0xFF000000)
        stamp_(cv, 'OVER CZECHOSLOVAKIA', 1370, 720, -3, 70, pop(c.lt, max(0.9, c.d * 0.7)), RED)
    else:
        Wd.text_card(cv, 'TAKE-OFF', 1370, 540, 120, 0xFFFFFFFF, 0xFF000000)
        Wd.text_card(cv, '28 ON BOARD', 1370, 690, 84, ORANGE, 0xFF000000)


def people(cv, c):
    """28 on board. One figure stays lit."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A2238')), (1, h('06080E'))])
    k = ease(pop(c.lt, 0.35, 0.6))
    for i in range(28):
        x, y = 250 + (i % 14) * 109, 330 + (i // 14) * 250
        keep = i == 19
        col = ORANGE if keep else Wd.alpha(0xFFFFFFFF, lerp(0.95, 0.2, k))
        cv.drawCircle(x, y - 62, 30, P(col))
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 34, y - 26, 68, 110), 26, 26, P(col))
        if keep:
            cv.drawCircle(x, y, 110 + 8 * math.sin(c.t * 5), P(ORANGE, 6, 0.3 + 0.7 * k))
    Wd.text_card(cv, '28 ON BOARD', 960, 170, 110, 0xFFFFFFFF, 0xFF000000)
    if k > 0.5:
        Wd.text_card(cv, '26 JANUARY 1972', 960, 800, 60, Wd.alpha(0xFFFFFFFF, 0.8), 0xFF000000)


def memory_gap(cv, c):
    """A strip of film with the middle frames missing."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('14141C')), (1, h('06060A'))])
    off = (c.t * 60) % 360
    cv.save()
    cv.translate(0, 400)
    cv.rotate(-2)
    cv.drawRect(skia.Rect.MakeXYWH(-100, -210, W + 200, 420), P(h('1E1E26')))
    for i in range(-1, 14):
        x = i * 180 - off % 180
        for y in (-190, 160):
            cv.drawRoundRect(skia.Rect.MakeXYWH(x + 60, y, 60, 30), 6, 6, P(h('06060A')))
    for i in range(-1, 7):
        x = i * 360 - off
        fr = skia.Rect.MakeXYWH(x + 20, -140, 320, 280)
        j = (i + 1) % 6
        if j in (0, 1):
            cv.drawRect(fr, P(h('2E62B8')))
            jet_icon(cv, x + 180, 0, 1.2)
        elif j == 5:
            cv.drawRect(fr, P(h('DDE8EC')))
            cv.drawRect(skia.Rect.MakeXYWH(x + 150, -70, 60, 140), P(RED))
            cv.drawRect(skia.Rect.MakeXYWH(x + 110, -30, 140, 60), P(RED))
        else:
            cv.drawRect(fr, P(h('0A0A0E')))
            Wd.text_card(cv, '?', x + 180, 60, 170, Wd.alpha(0xFFFFFFFF, 0.25 + 0.2 * math.sin(c.t * 5 + i)), None)
    cv.restore()
    stamp_(cv, 'NO MEMORY', 960, 770, -3, 130, pop(c.lt, 0.5), AMBER)


def fame(cv, c):
    """1985: the hall-of-fame certificate."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('4A1428')), (1, h('1A0810'))])
    for i in range(16):
        cv.drawRect(skia.Rect.MakeXYWH(i * 120, 0, 60, H), P(0x14000000))
    for i in range(12):
        a = math.radians(i * 30 + c.t * 20)
        cv.drawLine(960, 430, 960 + math.cos(a) * 1300, 430 + math.sin(a) * 1300, P(Wd.alpha(h('FFD866'), 0.07), 70))
    k = pop(c.lt, 0.0, 0.25)
    cv.save()
    cv.translate(960, 430)
    cv.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    cv.drawRect(skia.Rect.MakeXYWH(-620, -330, 1240, 660), P(CREAM))
    cv.drawRect(skia.Rect.MakeXYWH(-590, -300, 1180, 600), P(h('C89A3A'), 12))
    Wd.text_card(cv, 'HALL OF FAME  ·  1985', 0, -180, 80, h('8A2A4A'), None)
    Wd.text_card(cv, 'HIGHEST FALL SURVIVED', 0, -60, 70, INK, None)
    Wd.text_card(cv, 'WITHOUT A PARACHUTE', 0, 20, 70, INK, None)
    Wd.text_card(cv, 'VESNA VULOVIĆ', 0, 150, 110, NAVY, None)
    Wd.text_card(cv, '10,160 m', 0, 250, 70, RED, None)
    cv.restore()
    k2 = pop(c.lt, 0.6)
    if k2 > 0:
        cv.save()
        cv.translate(1560, 640)
        cv.scale(1.6 - 0.6 * k2, 1.6 - 0.6 * k2)
        cv.drawRect(skia.Rect.MakeXYWH(-34, -190, 68, 150), P(RED))
        cv.drawCircle(0, 0, 100, P(h('FFD866')))
        cv.drawCircle(0, 0, 100, P(h('C89A3A'), 12))
        cv.drawCircle(-30, -34, 22, P(0x88FFFFFF))
        Wd.text_card(cv, '1', 0, 42, 120, h('8A5A10'), None)
        cv.restore()


def unsolved(cv, c):
    flapboard(cv, c.t)
    card(cv, 'BOMB IN THE FORWARD HOLD', 620, 210, 1000, 150, -2, 66, pop(c.lt, 0.05), CREAM)
    card(cv, 'CLAIMED BY PHONE, 27 JAN 1972', 1180, 420, 1160, 150, 2, 64, pop(c.lt, 0.45))
    card(cv, 'ARRESTS: 0', 560, 640, 620, 170, -3, 104, pop(c.lt, 0.9), CREAM)
    stamp_(cv, 'UNSOLVED', 1400, 690, -8, 150, pop(c.lt, 1.4))


def dispute(cv, c):
    """The 2009 claim against the official height."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E2A66')), (0.75, h('5A8AD8')), (1, h('C8D8F0'))])
    for i in range(6):
        Wd.cloud(cv, 200 + (i * 430) % 1700 + 30 * math.sin(c.t + i), 560 + (i * 97) % 160, 1.4 + 0.3 * (i % 3), 0xDDFFFFFF)
    cv.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), P(h('E8EEF8')))
    k = ease(pop(c.lt, 0.05, 0.7))
    top = lerp(860, 120, k)
    cv.drawRect(skia.Rect.MakeLTRB(1180, top, 1330, 860), P(AMBER))
    cv.drawRect(skia.Rect.MakeLTRB(780, lerp(860, 802, k), 930, 860), P(RED))
    jet_icon(cv, 1255, top - 40, 1.1)
    jet_icon(cv, 855, lerp(860, 802, k) - 40, 1.1, 0xFFFFD0D0)
    Wd.text_card(cv, 'OFFICIAL', 1560, 250, 70, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, '10,160 m', 1570, 370, 120, AMBER, 0xFF000000)
    Wd.text_card(cv, '2009 CLAIM', 400, 600, 70, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'ABOUT 800 m', 400, 700, 84, RED, 0xFF000000)
    stamp_(cv, 'DISMISSED', 470, 400, -8, 120, pop(c.lt, max(1.2, c.d * 0.6)))


def memoriam(cv, c):
    """Vesna Vulovic, 1950-2016, and the 27 who died."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A2238')), (1, h('06080E'))])
    drift_dots(cv, c.t, 50, 0x30FFFFFF, 18)
    s = 1.0 + 0.04 * c.k
    cv.save()
    cv.translate(560, 420)
    cv.scale(s, s)
    cv.drawRect(skia.Rect.MakeXYWH(-270, -330, 540, 660), P(CREAM))
    photo(cv, 'vesna', 0, -20, 490, 560, (0.5, 0.2))
    cv.restore()
    Wd.text_card(cv, 'VESNA VULOVIĆ', 1300, 330, 110, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, '1950 – 2016', 1300, 470, 100, AMBER, 0xFF000000)
    if c.lt > 0.9:
        Wd.text_card(cv, 'AND THE 27 WHO DIED ON FLIGHT 367', 1300, 610, 46, Wd.alpha(0xFFFFFFFF, pop(c.lt, 0.9, 0.5)), None)


SHOTS = {f.__name__: f for f in (alt_10k, board_fall, roster, alt_drop, xray, record, board_true, bp, route_map, clock, people, memory_gap,
                                 fame, unsolved, dispute, memoriam)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(text, x=560, y=180, size=84, at=0.3, col='FFB000', ang=-3):
    def f(cv, c):
        if c.lt > at:
            k = min(1, (c.lt - at) / 0.12)
            cv.save()
            cv.translate(x, y)
            cv.rotate(ang)
            cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
            Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
            cv.restore()
    return f


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 80, 0x99FFFFFF, 5, size=(3, 7), drift=(-70, 200), wobble=30)


def wind(cv, c):
    for i in range(22):
        y = (i * 211 + int(c.t * 2000)) % (H + 400) - 200
        x = (i * 137) % W
        cv.drawLine(x, H - y, x, H - y - 200, P(0xFFFFFFFF, 6, 0.16))


def pick(a, b):
    """a on the first use of a shot type, b on its re-framed or variant repeats (either may be None)."""
    def g(cv, c):
        f = b if c.prm else a
        if f:
            f(cv, c)
    return g


def both(*fs):
    def f(cv, c):
        for g in fs:
            if g:
                g(cv, c)
    return f


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1420, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 005  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(
    rook_hat=snow, hill_wide=snow, impact=snow, villager=snow, wreck_in=snow, rook_lantern=snow, rescuers=snow, honke_hears=snow,
    rook_snow=snow, stretcher=snow, tail_fall=wind, fall_top=wind, plunge=wind,
    medical=pick(stamp('PASSED', 520, 220, 150, 1.3, '3DDC84', -6), None),
    dispatch=pick(None, stamp('THE WRONG VESNA', 640, 200, 96, 0.5, 'FF7A1A', -3)),
    rook_caw=pick(stamp('A CIGARETTE?', 520, 240, 96, 0.5, 'FFFFFF', -3), None),
    fly_home=pick(stamp('SEDATIVE?  NO.', 600, 190, 92, 0.5, 'FFFFFF', -3), stamp('NOTHING TO FEAR', 620, 190, 92, 0.3, '3DDC84', -3)),
    walks=pick(stamp('10 MONTHS LATER', 600, 190, 92, 0.3, 'FFB000', -3), None),
    desk_job=pick(stamp('FREIGHT CONTRACTS', 600, 190, 84, 0.5, 'FFFFFF', -3), None),
    stage_wide=stamp('HALL OF FAME, 1985', 600, 190, 96, 0.3, 'FFD866', -3),
    phone_call=pick(None, stamp('NOBODY ARRESTED', 640, 200, 96, 0.4, 'E5392F', -3)),
    reporters=pick(None, stamp('EVIDENCE: CIRCUMSTANTIAL', 760, 200, 84, 0.4, 'FFFFFF', -3)),
    signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (the torn fuselage falling, Rook falling beside it) + a three-line hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('2E62B8'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(700, 0), (1280, 0)], [0x00000000, 0xD0000000])))
    Wd.text_card(cv, 'FELL', 1010, 200, 110, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, '10 KM', 1010, 370, 170, h('FFB000'), 0xFF000000)
    Wd.text_card(cv, 'LIVED', 1010, 540, 150, h('3DDC84'), 0xFF000000)
