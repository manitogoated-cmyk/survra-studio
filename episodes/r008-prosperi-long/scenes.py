"""Case 008, the full case file (16:9) - Mauro Prosperi. The story is filmed in 3D (world3d.py). This file holds the
flat graphic inserts on a 1920x1080 canvas (Rook's desert survey-map case board, the tally marks, the runner file, the
five events, the stage bars, the eight-hour clock, the two bottles, the race rule, the bat count, the sun's arc, the
off-course sketch map, the scale, the calendar, the stamps and the checklists), the 2D overlays drawn on top of 3D
shots (blown sand, heat haze, dust motes, the sign-off) and the thumbnail."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1920, 1080
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
ease = lambda k: (lambda x: x * x * (3 - 2 * x))(max(0.0, min(1.0, k)))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, RED, CREAM, SANDC, BROWN, TEAL, GREEN = h('FF7A1A'), h('FFB000'), h('D8402A'), h('F6ECD4'), h('E6C690'), h('4A2E1A'), h('1E5A66'), h('2FA866')
WHITE, BLACK = 0xFFFFFFFF, 0xFF000000
T = Wd.text_card


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


def wavy(y0, amp, ph, n=40, x0=-40, x1=W + 40):
    return path([(lerp(x0, x1, i / n), y0 + amp * math.sin(i * 0.55 + ph) + amp * 0.5 * math.sin(i * 1.3 + ph * 2)) for i in range(n + 1)])


def survey(cv, t):
    """Rook's case board for this one: a sand-coloured survey map of dune country, contour lines and a north arrow."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(SANDC))
    for j in range(11):
        cv.drawPath(wavy(40 + j * 104 + 8 * math.sin(t * 0.7 + j), 30 + 10 * math.sin(j * 1.9), j * 1.7 + t * 0.15), P(0x44A8703A if j % 3 else 0x77A8703A, 5 if j % 3 else 8))
    for i in range(9):
        cx, cy = (i * 397 + 140) % W, (i * 613 + 200) % H
        for rr in (40, 74, 108):
            cv.drawOval(skia.Rect.MakeXYWH(cx - rr * 1.5, cy - rr * 0.7, rr * 3, rr * 1.4), P(0x33A8703A, 4))
    cv.save()
    cv.translate(110, 150)
    cv.rotate(6 * math.sin(t * 0.9))
    cv.drawPath(path(((0, -80), (26, 30), (0, 9), (-26, 30)), True), P(BROWN))
    cv.drawPath(path(((0, -80), (26, 30), (0, 9)), True), P(RED))
    T(cv, 'N', 0, 84, 46, BROWN, None)
    cv.restore()
    for i in range(6):
        cv.drawRect(skia.Rect.MakeXYWH(60 + i * 50, 770, 50, 16), P(BROWN if i % 2 == 0 else CREAM))
    cv.drawRect(skia.Rect.MakeXYWH(60, 770, 300, 16), P(BROWN, 4))
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, W - 14, H - 14), P(ORANGE, 10))


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
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, 22), P(BROWN))
    T(cv, text, 0, size * 0.5, size, INK, None)
    cv.restore()


def stamp(cv, text, x, y, ang, size, k, col=RED):
    if k <= 0:
        return
    w_ = font(size).measureText(text)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
    box = skia.Rect.MakeLTRB(-w_ / 2 - 36, -size * 0.62, w_ / 2 + 36, size * 0.62)
    cv.drawRoundRect(box, 16, 16, P(0xDD0B0E18))
    cv.drawRoundRect(box, 16, 16, P(col, 14))
    T(cv, text, 0, size * 0.36, size, col, None)
    cv.restore()


def punch(cv, text, x, y, size, k, col=WHITE):
    """Big text that lands with a small overshoot."""
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
    T(cv, text, 0, 0, size, col, BLACK)
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


def streaks(cv, t, n=22, col=0x33F6D9A0, speed=2600):
    for i in range(n):
        y = (i * 131 + 40 * math.sin(i)) % H
        x = W - ((t * speed * (0.7 + (i % 5) * 0.12) + i * 310) % (W + 700))
        cv.drawLine(x, y, x + 240 + (i % 3) * 110, y - 10, P(col, 6 + (i % 3) * 3))


def paper(cv, x, y, w_, h_, ang, k, head, head_col=TEAL):
    """A cream file page with a coloured header strip; leaves the canvas rotated and centred on the page."""
    cv.translate(x, y)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 14, -h_ / 2 + 18, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(CREAM))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, 110), P(head_col))
    T(cv, head, 0, -h_ / 2 + 78, 60, WHITE, None)


def tick(cv, x, y, s, k, col=GREEN):
    if k <= 0:
        return
    p = path(((x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)))
    cv.drawPath(p, P(BLACK, s * 0.62))
    cv.drawPath(p, P(col, s * 0.4))


# ------------------------------------------------------------------ flat inserts
def days_9(cv, c):
    """Nine days: tally marks scratched into a mud wall."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2A1C')), (1, h('6A5238'))])
    for i in range(26):
        x, y = (i * 271) % W, (i * 233) % H
        cv.drawRect(skia.Rect.MakeXYWH(x, y, 150 + (i % 3) * 60, 14), P(0x22000000))
    n = min(9, int(c.k * 13) + 1)
    for i in range(n):
        j = i if i < 5 else i - 5
        x0, y0 = (170 if i < 5 else 760) + j * 96, 250
        wob = 2 * math.sin(c.t * 40 + i) if i == n - 1 else 0
        if j < 4:
            cv.drawLine(x0 + wob, y0, x0 + 12, y0 + 330, P(CREAM, 24))
        else:
            cv.drawLine(x0 - 4 * 96 - 44, y0 + 270, x0 - 50, y0 + 60, P(AMBER, 24))
    punch(cv, '9 DAYS', 1340, 480, 160, pop(c.lt, 0.45), AMBER)


def board_no(cv, c):
    survey(cv, c.t)
    k = pop(c.lt, 0.0, 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(620, 420)
    cv.scale(s, s)
    taped(cv, 0, 0, 860, 590, -3)
    cv.rotate(-3)
    photo(cv, 'desert', 0, 14, 800, 500, (0.5, 0.5))
    cv.restore()
    card(cv, '9 DAYS', 1430, 250, 420, 180, 5, 84, pop(c.lt, 0.25))
    card(cv, 'NO WATER', 1470, 520, 480, 180, -4, 76, pop(c.lt, 0.45), h('BFE0E4'))
    stamp(cv, 'NO CHANCE', 700, 450, -12, 130, pop(c.lt, 0.7, 0.12))


def id_card(cv, c):
    """Who he is: the runner's race file."""
    survey(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    paper(cv, 960, 420, 1380, 700, 1.5, k, 'RUNNER FILE')
    photo(cv, 'mauro', -430, 50, 400, 460, (0.5, 0.12))
    cv.drawRect(skia.Rect.MakeXYWH(-630, -180, 400, 460), P(BROWN, 8))
    T(cv, 'MAURO', 210, -40, 120, INK, None)
    T(cv, 'PROSPERI', 210, 90, 120, INK, None)
    k2 = pop(c.lt, 0.35)
    if k2 > 0:
        cv.drawRoundRect(skia.Rect.MakeXYWH(-150, 140, 720, 84), 14, 14, P(TEAL))
        T(cv, 'POLICE OFFICER', 210, 202, 60, WHITE, None)
    k3 = pop(c.lt, 0.6)
    if k3 > 0:
        cv.drawRoundRect(skia.Rect.MakeXYWH(40, 244, 340, 76), 14, 14, P(ORANGE))
        T(cv, 'ITALY', 210, 300, 56, INK, None)
    cv.restore()


def _ev_icon(cv, i, x, y, col):
    if i == 0:                      # fence: a foil with its guard
        cv.drawLine(x - 62, y + 62, x + 66, y - 66, P(col, 12))
        cv.drawLine(x - 52, y + 16, x - 16, y + 52, P(col, 14))
    elif i == 1:                    # shoot: a target
        for r in (66, 40, 14):
            cv.drawCircle(x, y, r, P(col, 11))
    elif i == 2:                    # swim: three waves
        for j in range(3):
            cv.drawPath(path([(x - 70 + q * 14, y - 38 + j * 38 + 13 * math.sin(q * 1.25)) for q in range(11)]), P(col, 12))
    elif i == 3:                    # ride: a horseshoe
        cv.drawArc(skia.Rect.MakeXYWH(x - 56, y - 66, 112, 124), 150, 240, False, P(col, 22))
    else:                           # run: chevrons
        for j in range(3):
            cv.drawPath(path(((x - 62 + j * 44, y - 54), (x - 18 + j * 44, y), (x - 62 + j * 44, y + 54))), P(col, 16))


def pentathlon(cv, c):
    """Five events, one athlete."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('123E48')), (1, h('0A2228'))])
    for j in range(7):
        cv.drawPath(wavy(120 + j * 150, 26, j * 1.3 + c.t * 0.4), P(0x1AFFFFFF, 5))
    T(cv, 'MODERN PENTATHLON', 760, 150, 84, WHITE, BLACK)
    n = c.k * 6.2
    for i, lab in enumerate(('FENCE', 'SHOOT', 'SWIM', 'RIDE', 'RUN')):
        x, y = 240 + i * 360, 460
        on = pop(n, i + 0.25, 0.3)
        s = 1 + 0.18 * math.sin(math.pi * on) if on < 1 else 1.0
        cv.save()
        cv.translate(x, y)
        cv.scale(s, s)
        cv.drawCircle(0, 0, 138, P(BLACK))
        cv.drawCircle(0, 0, 126, P(Wd.mix(h('1E5A66'), ORANGE, on)))
        _ev_icon(cv, i, 0, 0, WHITE if on > 0.5 else 0x66FFFFFF)
        cv.restore()
        T(cv, lab, x, 700, 68, AMBER if on > 0.5 else 0x77FFFFFF, BLACK)


def _bars(cv, c, hs, base, x0, dx, bw, hot=3, speed=4.5):
    for i, hh in enumerate(hs):
        k = ease(c.k * speed - i * 0.35)
        x = x0 + i * dx
        col = ORANGE if i == hot else CREAM
        cv.drawRoundRect(skia.Rect.MakeLTRB(x, base - hh * k, x + bw, base), 12, 12, P(BLACK))
        if hh * k > 18:
            cv.drawRoundRect(skia.Rect.MakeLTRB(x + 8, base - hh * k + 8, x + bw - 8, base - 8), 8, 8, P(col))
        T(cv, str(i + 1), x + bw / 2, base + 70, 60, WHITE, BLACK)


def race_map(cv, c):
    """The race: six days, about 250 km."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('F0A860')), (0.6, h('E88A4A')), (1, h('B85A32'))])
    sun_icon(cv, 1690, 190, 80, 0xFFFFF0C0, c.t)
    dune_band(cv, 800, 40, h('C8743A'), 0.4 + c.t * 0.05)
    dune_band(cv, 900, 34, h('A85A2E'), 2.0)
    _bars(cv, c, (230, 265, 255, 520, 290, 150), 700, 150, 150, 112, hot=-1)
    T(cv, 'STAGES', 590, 130, 60, 0xCCFFFFFF, BLACK)
    punch(cv, '6 DAYS', 1370, 330, 150, pop(c.lt, 0.25))
    punch(cv, 'ABOUT 250 KM', 1370, 520, 92, pop(c.lt, 0.62), AMBER)


def long_day(cv, c):
    """Day four, the long one."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A3A6A')), (0.65, h('C86A4A')), (1, h('7A3A2A'))])
    for i in range(30):
        cv.drawCircle((i * 331) % W, (i * 97) % 420, 3 + (i % 3), P(0x55FFFFFF))
    dune_band(cv, 820, 46, h('8A4A30'), 1.1 + c.t * 0.05)
    dune_band(cv, 930, 30, h('5A2E22'), 2.7)
    _bars(cv, c, (150, 172, 166, 560, 188, 98), 720, 980, 138, 104, speed=6)
    punch(cv, 'STAGE 4', 480, 300, 150, pop(c.lt, 0.15))
    punch(cv, '80+ KM', 480, 520, 210, pop(c.lt, 0.5), AMBER)
    k = pop(c.lt, 0.5, 0.3)
    if k > 0:
        cv.drawLine(800, 440, lerp(800, 1380, k), lerp(440, 300, k), P(BLACK, 22))
        cv.drawLine(800, 440, lerp(800, 1380, k), lerp(440, 300, k), P(AMBER, 12))


def storm_clock(cv, c):
    """Eight hours of it, by his account."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('7A4E26')), (1, h('B47C40'))])
    streaks(cv, c.t, 30, 0x44F6D9A0, 3600)
    cx, cy, r = 600, 440, 300
    cv.drawCircle(cx + 10, cy + 14, r + 18, P(0x66000000))
    cv.drawCircle(cx, cy, r + 18, P(BROWN))
    cv.drawCircle(cx, cy, r, P(CREAM))
    k = ease(c.k * 1.35)
    ang = 240 * k
    cv.drawArc(skia.Rect.MakeXYWH(cx - r + 20, cy - r + 20, 2 * r - 40, 2 * r - 40), -90, ang, True, P(0xAAFF7A1A))
    for i in range(12):
        a = i * math.pi / 6
        cv.drawLine(cx + math.sin(a) * (r - 44), cy - math.cos(a) * (r - 44), cx + math.sin(a) * (r - 12), cy - math.cos(a) * (r - 12), P(BROWN, 14 if i % 3 == 0 else 8))
    a = math.radians(ang)
    cv.drawLine(cx, cy, cx + math.sin(a) * (r - 110), cy - math.cos(a) * (r - 110), P(BLACK, 26))
    a2 = a * 12
    cv.drawLine(cx, cy, cx + math.sin(a2) * (r - 50), cy - math.cos(a2) * (r - 50), P(RED, 12))
    cv.drawCircle(cx, cy, 24, P(BLACK))
    v = int(lerp(0, 8, k) + 0.001)
    T(cv, f'{v} HOURS', 1380, 470, 200, AMBER, BLACK)
    streaks(cv, c.t + 3, 12, 0x33FFFFFF, 4400)


def _bottle(cv, x, y, s, level, col=0xFF3A8AC8):
    body = skia.Rect.MakeXYWH(x - 70 * s, y - 150 * s, 140 * s, 330 * s)
    cv.drawRoundRect(skia.Rect.MakeXYWH(x - 70 * s + 10, y - 150 * s + 14, 140 * s, 330 * s), 26 * s, 26 * s, P(0x44000000))
    cv.drawRoundRect(body, 26 * s, 26 * s, P(0xFFE4F2F6))
    if level > 0:
        cv.save()
        cv.clipRRect(skia.RRect.MakeRectXY(body, 26 * s, 26 * s), True)
        cv.drawRect(skia.Rect.MakeXYWH(x - 70 * s, y + 180 * s - 330 * s * level, 140 * s, 330 * s * level), P(col))
        cv.restore()
    cv.drawRoundRect(body, 26 * s, 26 * s, P(BROWN, 9))
    cv.drawRect(skia.Rect.MakeXYWH(x - 30 * s, y - 196 * s, 60 * s, 50 * s), P(0xFFE4F2F6))
    cv.drawRect(skia.Rect.MakeXYWH(x - 30 * s, y - 196 * s, 60 * s, 50 * s), P(BROWN, 9))
    cv.drawRoundRect(skia.Rect.MakeXYWH(x - 38 * s, y - 236 * s, 76 * s, 44 * s), 8, 8, P(ORANGE))


def trick(cv, c):
    """Two bottles: the water that is nearly gone, and the spare."""
    survey(cv, c.t)
    lvl = lerp(0.45, 0.07, ease(c.k * 1.6))
    _bottle(cv, 520, 430, 1.25, lvl)
    T(cv, 'WATER', 520, 760, 76, INK, None)
    k = pop(c.lt, 0.3)
    if k > 0:
        cv.save()
        cv.translate(980, 430)
        cv.scale(1.3 - 0.3 * k, 1.3 - 0.3 * k)
        _bottle(cv, 0, 0, 1.25, 0.0)
        cv.restore()
        T(cv, 'SPARE', 980, 760, 76, INK, None)
    card(cv, "GRANDFATHER'S", 1500, 340, 620, 150, 4, 64, pop(c.lt, 0.55))
    card(cv, 'TRICK', 1500, 510, 360, 170, -3, 96, pop(c.lt, 0.68), h('BFE0E4'))


def rule_card(cv, c):
    """The race rule he followed."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('E88A4A')), (1, h('A8502A'))])
    dune_band(cv, 860, 40, h('8A3E22'), 0.7 + c.t * 0.05)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    paper(cv, 960, 420, 1300, 640, -1.5, k, 'RACE RULE', ORANGE)
    T(cv, 'IF YOU ARE LOST', 0, -70, 110, INK, None)
    k2 = pop(c.lt, 0.4)
    if k2 > 0:
        cv.drawRoundRect(skia.Rect.MakeXYWH(-560, 0, 1120, 230), 20, 20, P(TEAL))
        cv.save()
        cv.translate(0, 150)
        cv.scale(1.3 - 0.3 * k2, 1.3 - 0.3 * k2)
        T(cv, 'STAY PUT. WAIT.', 0, -6, 112, WHITE, None)
        cv.restore()
    cv.restore()
    for i in range(3):
        a = c.t * 2 + i * 2.1
        cv.drawCircle(1690, 190, 34 + 26 * ((a / 6.28) % 1), P(Wd.alpha(WHITE, 0.6 * (1 - (a / 6.28) % 1)), 8))
    cv.drawCircle(1690, 190, 26, P(RED))


def bat_count(cv, c):
    """About twenty, by his own account."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A1410')), (1, h('4A3A28'))])
    beam = path(((0, 60), (1150, 380), (1150, 720), (0, 520)), True)
    cv.drawPath(beam, P(0x22FFE2A8))
    for i in range(20):
        x, y = (i * 271 + 60) % W, (i * 197 + 30) % 820
        cv.drawRect(skia.Rect.MakeXYWH(x, y, 130 + (i % 3) * 50, 12), P(0x22000000))
    n = min(20, int(c.k * 27) + 1)
    for i in range(n):
        g, j = divmod(i, 5)
        x0, y0 = 150 + g * 250 + j * 40, 260
        wob = 2 * math.sin(c.t * 40 + i) if i == n - 1 else 0
        if j < 4:
            cv.drawLine(x0 + wob, y0, x0 + 8, y0 + 250, P(CREAM, 16))
        else:
            cv.drawLine(x0 - 190, y0 + 200, x0 - 10, y0 + 50, P(AMBER, 16))
    punch(cv, 'ABOUT 20', 1440, 400, 140, pop(c.lt, 0.5), AMBER)
    k = pop(c.lt, 0.68)
    if k > 0:
        T(cv, 'BY HIS OWN ACCOUNT', 1440, 510, 54, WHITE, BLACK)
    Wd.particles(cv, W, H, c.t, 30, Wd.alpha(0xFFFFD9A0, 0.35), 9, size=(2, 5), drift=(8, 18), wobble=22, twinkle=True)


def sun_arc(cv, c):
    """How he travelled: at dawn and dusk, hiding from the midday sun."""
    k = ease(c.k * 1.15)
    night = abs(k - 0.5) * 2
    Wd.vgrad(cv, 0, 0, W, H, [(0, Wd.mix(h('4A9AE0'), h('3A2A6A'), night)), (0.7, Wd.mix(h('F6E0B0'), h('F08A4A'), night)), (1, h('C8743A'))])
    cx, cy, rx, ry = 960, 700, 760, 520
    for i in range(41):
        a = math.pi * (1 - i / 40)
        if i % 2 == 0:
            cv.drawCircle(cx + math.cos(a) * rx, cy - math.sin(a) * ry, 8, P(0xAAFFFFFF))
    a = math.pi * (1 - k)
    sun_icon(cv, cx + math.cos(a) * rx, cy - math.sin(a) * ry, 70, Wd.mix(0xFFFFF4C8, ORANGE, night), c.t)
    dune_band(cv, 720, 40, h('D89A52'), 0.9)
    dune_band(cv, 830, 34, h('B8743A'), 2.4)
    mid = 1 - night
    for x, lab, sub, on in ((300, 'WALK', 'DAWN', k < 0.3), (1620, 'WALK', 'DUSK', k > 0.7)):
        cv.save()
        cv.translate(x, 560)
        s = 1.15 if on else 1.0
        cv.scale(s, s)
        T(cv, lab, 0, 0, 110, AMBER if on else 0x88FFFFFF, BLACK)
        cv.restore()
        T(cv, sub, x, 640, 52, 0xDDFFFFFF, BLACK)
    cv.save()
    cv.translate(960, 470)
    s = 1.0 + 0.25 * mid
    cv.scale(s, s)
    T(cv, 'HIDE', 0, 0, 130, WHITE if mid > 0.5 else 0x77FFFFFF, BLACK)
    cv.restore()
    T(cv, 'MIDDAY', 960, 560, 52, 0xDDFFFFFF if mid > 0.5 else 0x66FFFFFF, BLACK)


def map_off(cv, c):
    """A sketch, not a survey: the marked course, and where he actually went."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(SANDC))
    for j in range(11):
        cv.drawPath(wavy(40 + j * 104, 26, j * 2.3 + c.t * 0.2), P(0x33A8703A, 5))
    border = [(1240, 0), (1150, 130), (960, 210), (860, 360), (700, 430), (620, 600), (430, 690), (330, 860), (130, 940), (0, 1010)]
    b = path(border)
    b.lineTo(0, H)
    b.lineTo(W, H)
    b.lineTo(W, 0)
    b.close()
    cv.drawPath(b, P(0x55C88A4A))
    for p0, p1 in zip(border, border[1:]):
        for i in range(6):
            if i % 2 == 0:
                cv.drawLine(lerp(p0[0], p1[0], i / 6), lerp(p0[1], p1[1], i / 6), lerp(p0[0], p1[0], (i + 1) / 6), lerp(p0[1], p1[1], (i + 1) / 6), P(BROWN, 8))
    T(cv, 'MOROCCO', 330, 130, 84, 0xAA4A2E1A, None)
    T(cv, 'ALGERIA', 1010, 800, 84, 0xAA4A2E1A, None)
    route = [(110, 330), (270, 400), (400, 330), (540, 250), (690, 170), (850, 90)]
    for p0, p1 in zip(route, route[1:]):
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(TEAL, 12))
    for p in route:
        cv.drawCircle(p[0], p[1], 14, P(TEAL))
    T(cv, 'THE COURSE', 190, 300, 42, TEAL, None)
    wander = [(400, 330), (470, 440), (430, 540), (570, 560), (650, 500), (760, 560), (860, 500), (960, 590), (1080, 560), (1170, 640)]
    verdict = bool(c.prm.get('verdict'))
    k = 1.0 if verdict else ease(c.k * 1.5)
    n = len(wander) - 1
    for i in range(n):
        f = max(0.0, min(1.0, k * n - i))
        if f > 0:
            p0, p1 = wander[i], wander[i + 1]
            cv.drawLine(p0[0], p0[1], lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f), P(RED, 14))
    x, y = wander[-1]
    if k >= 1:
        cv.drawLine(x - 30, y - 30, x + 30, y + 30, P(RED, 16))
        cv.drawLine(x - 30, y + 30, x + 30, y - 30, P(RED, 16))
    cv.drawCircle(400, 330, 22, P(ORANGE))
    if verdict:
        pulse = 1 + 0.12 * math.sin(c.t * 7)
        cv.drawCircle(400, 330, 46 * pulse, P(ORANGE, 8))
        cv.drawCircle(x, y, 58 * pulse, P(RED, 8))
        k1, k2 = pop(c.lt, 0.15), pop(c.lt, 0.6)
        if k1 > 0:
            T(cv, 'LOST HERE', 480, 250, 64, INK, WHITE)
        if k2 > 0:
            T(cv, 'FOUND HERE', x + 60, y - 80, 64, RED, WHITE)
        punch(cv, 'MOROCCO', 1420, 250, 90, k1)
        punch(cv, 'TO ALGERIA', 1420, 380, 90, k2, AMBER)
    else:
        if k >= 1:
            T(cv, 'FOUND', x + 20, y - 54, 60, RED, WHITE)
        k2 = pop(c.lt, 0.55)
        v = int(lerp(0, 291, ease(c.k * 1.8)))
        cv.save()
        cv.translate(1400, 300)
        s = 1.4 - 0.4 * k2 if k2 > 0 else 1
        cv.scale(s, s)
        T(cv, f'{v} KM', 0, 0, 160, AMBER, BLACK)
        if k2 > 0:
            T(cv, 'OFF COURSE', 0, 110, 84, WHITE, BLACK)
        cv.restore()
    T(cv, 'SKETCH, NOT TO SCALE', 1650, 60, 34, 0x994A2E1A, None)
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, W - 14, H - 14), P(ORANGE, 10))


def scale(cv, c):
    """What nine days cost him."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('24424A')), (1, h('12262C'))])
    cx, cy, r = 620, 640, 420
    cv.drawArc(skia.Rect.MakeXYWH(cx - r - 26, cy - r - 26, 2 * r + 52, 2 * r + 52), 180, 180, True, P(BLACK))
    cv.drawArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), 180, 180, True, P(CREAM))
    for i in range(21):
        a = math.pi * (1 - i / 20)
        r0 = r - (70 if i % 5 == 0 else 40)
        cv.drawLine(cx + math.cos(a) * r0, cy - math.sin(a) * r0, cx + math.cos(a) * (r - 14), cy - math.sin(a) * (r - 14), P(BROWN, 12 if i % 5 == 0 else 6))
    k = ease(c.k * 1.5)
    f = lerp(0.72, 0.42, k) + 0.012 * math.sin(c.t * 16) * (1 - k * 0.6)
    cv.drawArc(skia.Rect.MakeXYWH(cx - r + 90, cy - r + 90, 2 * r - 180, 2 * r - 180), 180 + 180 * f, 180 * (0.72 - f), True, P(0x99D8402A))
    a = math.pi * (1 - f)
    cv.drawLine(cx, cy, cx + math.cos(a) * (r - 90), cy - math.sin(a) * (r - 90), P(BLACK, 28))
    cv.drawLine(cx, cy, cx + math.cos(a) * (r - 90), cy - math.sin(a) * (r - 90), P(RED, 14))
    cv.drawCircle(cx, cy, 34, P(BLACK))
    cv.drawRect(skia.Rect.MakeXYWH(cx - r - 26, cy, 2 * r + 52, 40), P(BLACK))
    v = int(lerp(0, 15, k) + 0.001)
    T(cv, f'-{v} KG', 1440, 420, 220, AMBER, BLACK)
    if pop(c.lt, 0.55) > 0:
        T(cv, 'ABOUT 15 KILOS LOST', 1440, 540, 62, WHITE, BLACK)


def recover(cv, c):
    """How long it took to come back from it."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2E5A66')), (1, h('183038'))])
    for j in range(6):
        cv.drawPath(wavy(140 + j * 150, 22, j * 1.9 + c.t * 0.3), P(0x14FFFFFF, 5))
    n = c.k * 9
    for i in range(8):
        k = pop(n, i * 0.9, 0.8)
        if k <= 0:
            continue
        x, y = 180 + (i % 4) * 215, 250 + (i // 4) * 280
        cv.save()
        cv.translate(x, y)
        cv.rotate((i % 3 - 1) * 3)
        cv.scale(1, 0.2 + 0.8 * k)
        cv.drawRect(skia.Rect.MakeXYWH(-86 + 8, -104 + 10, 172, 208), P(0x55000000))
        cv.drawRect(skia.Rect.MakeXYWH(-86, -104, 172, 208), P(CREAM))
        cv.drawRect(skia.Rect.MakeXYWH(-86, -104, 172, 52), P(RED))
        for r_ in range(3):
            for q in range(5):
                cv.drawRect(skia.Rect.MakeXYWH(-70 + q * 30, -34 + r_ * 40, 20, 24), P(0x554A2E1A))
        cv.restore()
    punch(cv, 'MONTHS', 1440, 240, 130, pop(c.lt, 0.15))
    if pop(c.lt, 0.3) > 0:
        T(cv, 'NO SOLID FOOD', 1440, 320, 58, 0xDDFFFFFF, BLACK)
    punch(cv, 'ALMOST', 1440, 500, 96, pop(c.lt, 0.6))
    punch(cv, '2 YEARS', 1440, 660, 170, pop(c.lt, 0.68), AMBER)


def fabrication(cv, c):
    """What the race's founder said of the story."""
    survey(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    paper(cv, 700, 430, 1000, 700, -2, k, 'HIS ACCOUNT', BROWN)
    for i in range(8):
        cv.drawRect(skia.Rect.MakeXYWH(-420, -200 + i * 62, 840 - (i % 3) * 150, 22), P(0x334A2E1A))
    cv.restore()
    stamp(cv, 'A FABRICATION', 760, 330, -9, 120, pop(c.lt, 0.2, 0.12))
    stamp(cv, 'PHYSICALLY IMPOSSIBLE', 900, 590, 5, 84, pop(c.lt, 0.58, 0.12))
    card(cv, "THE RACE'S FOUNDER", 1540, 300, 620, 150, 4, 50, pop(c.lt, 0.3), h('BFE0E4'))
    card(cv, 'SAID IN 1998', 1560, 480, 480, 150, -3, 58, pop(c.lt, 0.45))


def finds(cv, c):
    """What the film crew reported finding along his route."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2E22')), (1, h('1E1812'))])
    Wd.particles(cv, W, H, c.t, 26, Wd.alpha(0xFFFFD9A0, 0.3), 5, size=(2, 5), drift=(10, -14), wobble=18, twinkle=True)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    paper(cv, 960, 430, 1320, 720, 1, k, 'REPORTED FOUND', ORANGE)
    for i, lab in enumerate(('THE SHRINE', 'HIS BELONGINGS', 'BAT SKELETONS')):
        y = -140 + i * 170
        k2 = pop(c.lt, 0.2 + i * 0.22)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-560, y - 60, 120, 120), 14, 14, P(BROWN, 10))
        if k2 > 0:
            T(cv, lab, -390, y + 34, 96, INK, None, center=False)
            tick(cv, -500, y + 4, 58 * (1.5 - 0.5 * k2), k2)
    cv.restore()


def review(cv, c):
    """The conclusion of the doctor who went through the account."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('24424A')), (1, h('12262C'))])
    for j in range(6):
        cv.drawPath(wavy(140 + j * 150, 22, j * 1.9 + c.t * 0.3), P(0x14FFFFFF, 5))
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    paper(cv, 760, 430, 1080, 720, -1.5, k, "DOCTOR'S REVIEW", TEAL)
    for i in range(7):
        cv.drawRect(skia.Rect.MakeXYWH(-460, -190 + i * 66, 920 - (i % 3) * 170, 22), P(0x334A2E1A))
    for i in range(3):
        tick(cv, 400, -180 + i * 132, 30, pop(c.lt, 0.15 + i * 0.12))
    cv.restore()
    stamp(cv, 'TELLING THE TRUTH', 900, 500, -8, 110, pop(c.lt, 0.55, 0.12), GREEN)
    cx, cy = 1620, 330
    cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 50, cy - 140, 100, 280), 16, 16, P(RED))
    cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 140, cy - 50, 280, 100), 16, 16, P(RED))
    cv.drawCircle(cx, cy, 190 + 8 * math.sin(c.t * 4), P(0x66FFFFFF, 10))


def rules_after(cv, c):
    """After 1994 the race tightened its safety rules."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('F0A860')), (0.6, h('E88A4A')), (1, h('B85A32'))])
    sun_icon(cv, 230, 200, 76, 0xFFFFF0C0, c.t)
    dune_band(cv, 830, 40, h('C8743A'), 1.4 + c.t * 0.05)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    paper(cv, 1000, 430, 1180, 620, 1.5, k, 'THE RACE, AFTER 1994', TEAL)
    T(cv, 'SAFETY RULES', 0, -40, 124, INK, None)
    for i in range(3):
        kk = pop(c.lt, 0.3 + i * 0.1)
        if kk > 0:
            x = -330 + i * 330
            yy = 190 - 30 * kk + 8 * math.sin(c.t * 5 + i)
            cv.drawPath(path(((x - 70, yy + 40), (x, yy - 50), (x + 70, yy + 40))), P(BLACK, 40))
            cv.drawPath(path(((x - 70, yy + 40), (x, yy - 50), (x + 70, yy + 40))), P(ORANGE, 24))
    cv.restore()
    stamp(cv, 'TIGHTENED', 1250, 560, -8, 120, pop(c.lt, 0.6, 0.12), GREEN)


def board_true(cv, c):
    survey(cv, c.t)
    taped(cv, 620, 420, 600, 680, 2)
    cv.save()
    cv.translate(620, 420)
    cv.rotate(2)
    photo(cv, 'mauro', 0, 16, 530, 590, (0.5, 0.12))
    cv.restore()
    stamp(cv, 'TRUE', 660, 560, -14, 200, pop(c.lt, 0.2, 0.12), GREEN)
    card(cv, '9 DAYS', 1430, 300, 420, 180, -5, 84, pop(c.lt, 0.36), h('BFE0E4'))
    card(cv, '291 KM', 1470, 560, 440, 180, 5, 84, pop(c.lt, 0.5))


SHOTS = {f.__name__: f for f in (days_9, board_no, id_card, pentathlon, race_map, long_day, storm_clock, trick, rule_card, bat_count, sun_arc, map_off, scale,
                                 recover, fabrication, finds, review, rules_after, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def blast(cv, c):
    """Sand driven flat across the lens."""
    streaks(cv, c.t, 30, 0x44F6D9A0, 5200)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('C08A4A'), None, 0.12))


def gust(cv, c):
    streaks(cv, c.t, 12, 0x2AF6D9A0, 3200)


def haze(cv, c):
    Wd.particles(cv, W, H, c.t, 30, Wd.alpha(0xFFFFE8C0, 0.3), 5, size=(2, 5), drift=(-30, -20), wobble=14, twinkle=True)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 44, Wd.alpha(0xFFFFD9A0, 0.35), 9, size=(2, 5), drift=(8, 18), wobble=22, twinkle=True)


def stars(cv, c):
    Wd.particles(cv, W, 420, c.t, 30, Wd.alpha(0xFFFFFFFF, 0.5), 3, size=(1, 3), drift=(2, 0), wobble=2, twinkle=True)


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1380, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        T(cv, 'SURVRA', 0, 0, 170, AMBER, BLACK)
        T(cv, 'CASE 008  CLOSED', 0, 96, 60, WHITE, BLACK)
        cv.restore()


OVER = dict(storm_hit=gust, vanish=blast, rook_sand=blast, trail_gone=blast, run_blind=blast, storm_night=blast, wall_come=gust, race_wide=haze,
            run_close=haze, rook_jog=haze, lizard=haze, beetle=haze, checkpoint=haze, wadi_shade=haze, roots=haze, snake=haze, caravan=haze, village=haze,
            jeep=gust, toe=haze, rook_bat=motes, bats_up=motes, bat_grab=motes, rook_gag=motes, rook_bones=motes, hall_shade=motes, hall_days=motes,
            hall_low=motes, hall_dawn=motes, shrine_night=stars, signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (the thin runner coming over a dune at sunset, Rook's hat in the air) + a hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('C8743A'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(640, 0), (1010, 0)], [0x00000000, 0xC8000000])))
    T(cv, 'LOST', 965, 240, 120, WHITE, BLACK)
    T(cv, '9 DAYS', 965, 420, 150, h('FFB000'), BLACK)
    T(cv, 'IN THE SAHARA', 965, 520, 60, WHITE, BLACK)
