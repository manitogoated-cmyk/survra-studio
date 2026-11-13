"""Case 008 - Mauro Prosperi. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(Rook's desert survey-map case board, the nine tally marks, the runner file, the six stage bars, the sun's arc,
the off-course sketch map) and the 2D overlays drawn on top of 3D shots (blown sand, heat haze, the sign-off)."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
ease = lambda k: (lambda x: x * x * (3 - 2 * x))(max(0.0, min(1.0, k)))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, RED, CREAM, SANDC, BROWN, TEAL = h('FF7A1A'), h('FFB000'), h('D8402A'), h('F6ECD4'), h('E6C690'), h('4A2E1A'), h('1E5A66')


def pop(lt, t0, d=0.14):
    return max(0.0, min(1.0, (lt - t0) / d))


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) taped to the map as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('C89A5A')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def path(pts, close=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def wavy(y0, amp, ph, n=28, x0=-40, x1=W + 40):
    return path([(lerp(x0, x1, i / n), y0 + amp * math.sin(i * 0.55 + ph) + amp * 0.5 * math.sin(i * 1.3 + ph * 2)) for i in range(n + 1)])


def survey(cv, t):
    """Rook's case board for this one: a sand-coloured survey map of dune country, contour lines and a north arrow."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(SANDC))
    for j in range(17):
        cv.drawPath(wavy(60 + j * 118, 34 + 12 * math.sin(j * 1.9), j * 1.7), P(0x44A8703A if j % 3 else 0x77A8703A, 5 if j % 3 else 8))
    for i in range(9):
        cx, cy = (i * 397 + 140) % W, (i * 613 + 300) % H
        for rr in (46, 84, 122):
            cv.drawOval(skia.Rect.MakeXYWH(cx - rr * 1.5, cy - rr * 0.7, rr * 3, rr * 1.4), P(0x33A8703A, 4))
    cv.save()
    cv.translate(930, 1730)
    cv.rotate(5 * math.sin(t * 0.8))
    cv.drawPath(path(((0, -110), (34, 40), (0, 12), (-34, 40)), True), P(BROWN))
    cv.drawPath(path(((0, -110), (34, 40), (0, 12)), True), P(RED))
    Wd.text_card(cv, 'N', 0, 110, 60, BROWN, None)
    cv.restore()
    for i in range(6):
        cv.drawRect(skia.Rect.MakeXYWH(70 + i * 60, 1790, 60, 20), P(BROWN if i % 2 == 0 else CREAM))
    cv.drawRect(skia.Rect.MakeXYWH(70, 1790, 360, 20), P(BROWN, 4))
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(ORANGE, 10))


def taped(cv, x, y, w_, h_, ang, col=CREAM):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    for sx in (-1, 1):
        cv.save()
        cv.translate(sx * (w_ / 2 - 30), -h_ / 2 + 8)
        cv.rotate(sx * 38)
        cv.drawRect(skia.Rect.MakeXYWH(-62, -22, 124, 44), P(0xCCF2D48A))
        cv.restore()
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col=h('FFD866')):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 10, -h_ / 2 + 14, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, 26), P(BROWN))
    Wd.text_card(cv, text, 0, size * 0.52, size, INK, None)
    cv.restore()


def stamp(cv, text, x, y, ang, size, k, col=RED):
    if k <= 0:
        return
    w_ = font(size).measureText(text)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
    box = skia.Rect.MakeLTRB(-w_ / 2 - 40, -size * 0.62, w_ / 2 + 40, size * 0.62)
    cv.drawRoundRect(box, 18, 18, P(0xDD0B0E18))
    cv.drawRoundRect(box, 18, 18, P(col, 18))
    Wd.text_card(cv, text, 0, size * 0.36, size, col, None)
    cv.restore()


def sun_icon(cv, x, y, r, col, t, rays=10):
    for i in range(rays):
        a = i * 2 * math.pi / rays + t * 0.6
        cv.drawLine(x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3, x + math.cos(a) * r * 1.75, y + math.sin(a) * r * 1.75, P(col, r * 0.2))
    cv.drawCircle(x, y, r, P(col))


def dune_band(cv, y, amp, col, ph):
    p = wavy(y, amp, ph)
    p.lineTo(W + 40, H)
    p.lineTo(-40, H)
    p.close()
    cv.drawPath(p, P(col))


# ------------------------------------------------------------------ flat inserts
def days_9(cv, c):
    """Nine days: tally marks scratched into a mud wall."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2A1C')), (1, h('6A5238'))])
    for i in range(22):
        x, y = (i * 271) % W, (i * 433) % H
        cv.drawRect(skia.Rect.MakeXYWH(x, y, 150 + (i % 3) * 60, 16), P(0x22000000))
    n = min(9, int(c.k * 13) + 1)
    for i in range(n):
        j = i if i < 5 else i - 5
        row = 0 if i < 5 else 1
        x0, y0 = 250 + j * 130, 420 + row * 420
        wob = 2 * math.sin(c.t * 40 + i) if i == n - 1 else 0
        if j < 4:
            cv.drawLine(x0 + wob, y0, x0 + 14, y0 + 300, P(CREAM, 26))
        else:
            cv.drawLine(x0 - 4 * 130 - 50, y0 + 240, x0 - 60, y0 + 50, P(AMBER, 26))
    k2 = pop(c.lt, 0.45)
    if k2 > 0:
        cv.save()
        cv.translate(540, 1210)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        Wd.text_card(cv, '9 DAYS', 0, 0, 190, AMBER, 0xFF000000)
        cv.restore()


def board_no(cv, c):
    survey(cv, c.t)
    k = pop(c.lt, 0.0, 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 620)
    cv.scale(s, s)
    taped(cv, 0, 0, 760, 640, -3)
    cv.rotate(-3)
    photo(cv, 'desert', 0, 16, 690, 530, (0.5, 0.5))
    cv.restore()
    card(cv, '9 DAYS', 290, 1100, 400, 190, 5, 84, pop(c.lt, 0.25))
    card(cv, 'NO WATER', 770, 1120, 460, 190, -4, 72, pop(c.lt, 0.45), h('BFE0E4'))
    stamp(cv, 'NO CHANCE', 540, 640, -12, 124, pop(c.lt, 0.7, 0.12))


def id_card(cv, c):
    """Who he is: the runner's race file."""
    survey(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(540, 700)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    taped(cv, 0, 0, 900, 960, 2)
    cv.rotate(2)
    cv.drawRect(skia.Rect.MakeXYWH(-450, -480, 900, 150), P(TEAL))
    Wd.text_card(cv, 'RUNNER FILE', 0, -385, 64, 0xFFFFFFFF, None)
    photo(cv, 'mauro', -215, -80, 380, 440, (0.5, 0.12))
    cv.drawRect(skia.Rect.MakeXYWH(-405, -300, 380, 440), P(BROWN, 8))
    cv.drawRoundRect(skia.Rect.MakeXYWH(30, -290, 380, 200), 20, 20, P(ORANGE))
    Wd.text_card(cv, 'RACE', 220, -215, 56, INK, None)
    Wd.text_card(cv, 'NUMBER', 220, -140, 56, INK, None)
    for i in range(5):
        cv.drawRect(skia.Rect.MakeXYWH(40 + i * 76, -50, 46, 170 - (i % 2) * 40), P(0x554A2E1A))
    Wd.text_card(cv, 'MAURO', 0, 250, 96, INK, None)
    Wd.text_card(cv, 'PROSPERI', 0, 350, 96, INK, None)
    k2 = pop(c.lt, 0.35)
    if k2 > 0:
        cv.drawRoundRect(skia.Rect.MakeXYWH(-410, 385, 820, 80), 14, 14, P(TEAL))
        Wd.text_card(cv, 'POLICE OFFICER, ITALY', 0, 443, 54, 0xFFFFFFFF, None)
    cv.restore()
    k3 = pop(c.lt, 0.6)
    if k3 > 0:
        card(cv, 'PENTATHLETE', 720, 1290, 520, 160, -5, 62, k3)


def race_map(cv, c):
    """The race: six days, about 250 km. Day four is the long one."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('F0A860')), (0.6, h('E88A4A')), (1, h('B85A32'))])
    sun_icon(cv, 860, 300, 90, 0xFFFFF0C0, c.t)
    dune_band(cv, 1420, 50, h('C8743A'), 0.4)
    dune_band(cv, 1560, 40, h('A85A2E'), 2.0)
    Wd.text_card(cv, '6 DAYS', 400, 330, 150, 0xFFFFFFFF, 0xFF000000)
    hs = (260, 300, 290, 640, 330, 170)
    for i, hh in enumerate(hs):
        k = ease(c.k * 4.5 - i * 0.35)
        x = 110 + i * 150
        col = ORANGE if i == 3 else CREAM
        cv.drawRoundRect(skia.Rect.MakeLTRB(x, 1250 - hh * k, x + 112, 1250), 12, 12, P(0xFF000000))
        cv.drawRoundRect(skia.Rect.MakeLTRB(x + 8, 1258 - hh * k if hh * k > 16 else 1250, x + 104, 1242), 8, 8, P(col))
        Wd.text_card(cv, str(i + 1), x + 56, 1330, 70, 0xFFFFFFFF, 0xFF000000)
    k2 = pop(c.lt, 0.62)
    if k2 > 0:
        cv.save()
        cv.translate(616, 520)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        Wd.text_card(cv, 'DAY 4', 0, 0, 96, AMBER, 0xFF000000)
        cv.restore()
    Wd.text_card(cv, 'ABOUT 250 KM', 540, 1120 + 370, 84, 0xFFFFFFFF, 0xFF000000)


def sun_arc(cv, c):
    """How he travelled: at dawn and dusk, hiding from the midday sun."""
    k = ease(c.k * 1.15)
    night = abs(k - 0.5) * 2
    Wd.vgrad(cv, 0, 0, W, H, [(0, Wd.mix(h('4A9AE0'), h('3A2A6A'), night)), (0.62, Wd.mix(h('F6E0B0'), h('F08A4A'), night)), (1, h('C8743A'))])
    cx, cy, r = 540, 1080, 430
    for i in range(31):
        a = math.pi * (1 - i / 30)
        if i % 2 == 0:
            cv.drawCircle(cx + math.cos(a) * r, cy - math.sin(a) * r * 1.25, 9, P(0xAAFFFFFF))
    a = math.pi * (1 - k)
    sun_icon(cv, cx + math.cos(a) * r, cy - math.sin(a) * r * 1.25, 78, Wd.mix(0xFFFFF4C8, ORANGE, night), c.t)
    dune_band(cv, 1090, 46, h('D89A52'), 0.9)
    dune_band(cv, 1230, 40, h('B8743A'), 2.4)
    mid = 1 - night
    for x, lab, on in ((190, 'WALK', k < 0.3), (890, 'WALK', k > 0.7)):
        cv.save()
        cv.translate(x, 1330)
        s = 1.25 if on else 1.0
        cv.scale(s, s)
        Wd.text_card(cv, lab, 0, 0, 96, AMBER if on else 0x88FFFFFF, 0xFF000000)
        cv.restore()
    cv.save()
    cv.translate(540, 520)
    s = 1.0 + 0.25 * mid
    cv.scale(s, s)
    Wd.text_card(cv, 'HIDE', 0, 0, 110, 0xFFFFFFFF if mid > 0.5 else 0x77FFFFFF, 0xFF000000)
    cv.restore()
    Wd.text_card(cv, 'DAWN', 190, 1440, 56, 0xDDFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'DUSK', 890, 1440, 56, 0xDDFFFFFF, 0xFF000000)


def map_off(cv, c):
    """A sketch, not a survey: the marked course, and where he actually went."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(SANDC))
    for j in range(17):
        cv.drawPath(wavy(60 + j * 118, 30, j * 2.3), P(0x33A8703A, 5))
    border = [(1080, 420), (860, 520), (690, 500), (560, 640), (470, 860), (300, 960), (180, 1160), (0, 1230)]
    b = path(border)
    b.lineTo(0, 1920)
    b.lineTo(1080, 1920)
    b.close()
    cv.drawPath(b, P(0x55C88A4A))
    for p0, p1 in zip(border, border[1:]):
        for i in range(6):
            if i % 2 == 0:
                cv.drawLine(lerp(p0[0], p1[0], i / 6), lerp(p0[1], p1[1], i / 6), lerp(p0[0], p1[0], (i + 1) / 6), lerp(p0[1], p1[1], (i + 1) / 6), P(BROWN, 8))
    Wd.text_card(cv, 'MOROCCO', 300, 330, 78, 0xAA4A2E1A, None)
    Wd.text_card(cv, 'ALGERIA', 760, 1290, 78, 0xAA4A2E1A, None)
    route = [(150, 520), (300, 600), (420, 520), (560, 430), (700, 330), (860, 250)]
    for p0, p1 in zip(route, route[1:]):
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(TEAL, 12))
    for p in route:
        cv.drawCircle(p[0], p[1], 15, P(TEAL))
    Wd.text_card(cv, 'THE COURSE', 250, 470, 44, TEAL, None)
    wander = [(420, 520), (480, 640), (430, 760), (560, 830), (520, 960), (650, 1010), (610, 1120), (730, 1090), (800, 990)]
    k = ease(c.k * 1.5)
    n = len(wander) - 1
    for i in range(n):
        f = max(0.0, min(1.0, k * n - i))
        if f > 0:
            p0, p1 = wander[i], wander[i + 1]
            cv.drawLine(p0[0], p0[1], lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f), P(RED, 14))
    if k >= 1:
        x, y = wander[-1]
        cv.drawLine(x - 34, y - 34, x + 34, y + 34, P(RED, 16))
        cv.drawLine(x - 34, y + 34, x + 34, y - 34, P(RED, 16))
        Wd.text_card(cv, 'FOUND', x + 20, y - 60, 60, RED, 0xFFFFFFFF)
    cv.drawCircle(420, 520, 22, P(ORANGE))
    k2 = pop(c.lt, 0.55)
    v = int(lerp(0, 291, ease(c.k * 1.8)))
    cv.save()
    cv.translate(540, 1560)
    cv.scale(1.4 - 0.4 * k2 if k2 > 0 else 1, 1.4 - 0.4 * k2 if k2 > 0 else 1)
    Wd.text_card(cv, f'{v} KM', 0, 0, 200, AMBER, 0xFF000000)
    if k2 > 0:
        Wd.text_card(cv, 'OFF COURSE', 0, 110, 84, 0xFFFFFFFF, 0xFF000000)
    cv.restore()
    Wd.text_card(cv, 'SKETCH, NOT TO SCALE', 540, 1860, 34, 0x994A2E1A, None)
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(ORANGE, 10))


def board_true(cv, c):
    survey(cv, c.t)
    taped(cv, 540, 660, 720, 800, 2)
    cv.save()
    cv.translate(540, 660)
    cv.rotate(2)
    photo(cv, 'mauro', 0, 20, 650, 690, (0.5, 0.1))
    cv.restore()
    stamp(cv, 'TRUE', 560, 790, -14, 200, pop(c.lt, 0.2, 0.12), h('2FA866'))
    card(cv, '9 DAYS', 300, 1190, 400, 190, -5, 84, pop(c.lt, 0.36), h('BFE0E4'))
    card(cv, '291 KM', 780, 1160, 420, 190, 5, 84, pop(c.lt, 0.5))


SHOTS = {f.__name__: f for f in (days_9, board_no, id_card, race_map, sun_arc, map_off, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def blast(cv, c):
    """Sand driven flat across the lens."""
    for i in range(26):
        y = (i * 197 + 40 * math.sin(i)) % H
        x = W - ((c.t * 4200 * (0.7 + (i % 5) * 0.12) + i * 310) % (W + 700))
        cv.drawLine(x, y, x + 260 + (i % 3) * 120, y - 14, P(0x44F6D9A0 if i % 2 else 0x33FFFFFF, 7 + (i % 3) * 3))
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('C08A4A'), None, 0.12))


def gust(cv, c):
    for i in range(10):
        y = (i * 211 + 90) % H
        x = W - ((c.t * 2600 + i * 330) % (W + 600))
        cv.drawLine(x, y, x + 200, y - 8, P(0x2AF6D9A0, 6))


def haze(cv, c):
    Wd.particles(cv, W, H, c.t, 26, Wd.alpha(0xFFFFE8C0, 0.3), 5, size=(2, 5), drift=(-30, -20), wobble=14, twinkle=True)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 36, Wd.alpha(0xFFFFD9A0, 0.35), 9, size=(2, 5), drift=(8, 18), wobble=22, twinkle=True)


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 008  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(storm_hit=gust, vanish=blast, rook_sand=blast, trail_gone=blast, run_blind=blast, wall_come=gust, race_wide=haze, run_close=haze,
            rook_jog=haze, lizard=haze, beetle=haze, rook_bat=motes, bats_up=motes, bat_grab=motes, rook_gag=motes, signoff=closed)
