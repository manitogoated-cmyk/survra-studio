"""Case 007, the full case file - William Rankin. The story is filmed in 3D (world3d.py). This file holds the flat
graphic inserts on a 1920x1080 canvas (Rook's flight-chart case board, the altitude tape, the pilot file, his record,
the route, the storm-top diagram, the kit checklist, the thermometer, the parachute plan, the stopwatch, the automatic
release, the up-and-down trace, the wristwatch, the magazine note, the injuries, the book and the timeline), the 2D
overlays drawn on top of 3D shots, and the thumbnail."""
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
ORANGE, AMBER, RED, CREAM, BLUE, NAVY = h('FF7A1A'), h('FFB000'), h('E5392F'), h('F4EEDF'), h('7AB8FF'), h('1B2A4A')
GREEN, ICE = h('2FA866'), h('BFE4FF')
WHITE, BLACK = 0xFFFFFFFF, 0xFF000000


def pop(lt, t0, d=0.14):
    return max(0.0, min(1.0, (lt - t0) / d))


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def path(pts, close=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) pinned to the chart as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('6E4A80')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def jet_icon(cv, x, y, s, col, ang=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    cv.drawPath(path(((0, -70), (14, -20), (70, 30), (70, 46), (14, 28), (12, 54), (34, 72), (34, 82), (0, 74),
                      (-34, 82), (-34, 72), (-12, 54), (-14, 28), (-70, 46), (-70, 30), (-14, -20)), True), P(col))
    cv.restore()


def chute_icon(cv, x, y, s, col=CREAM, col2=ORANGE):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.drawArc(skia.Rect.MakeLTRB(-60, -70, 60, 30), 180, 180, True, P(col))
    cv.drawArc(skia.Rect.MakeLTRB(-22, -70, 22, 30), 180, 180, True, P(col2))
    for dx in (-58, -20, 20, 58):
        cv.drawLine(dx, -20, 0, 46, P(col, 4))
    cv.drawCircle(0, 54, 12, P(col2))
    cv.restore()


def storm_icon(cv, x, y, s, t=0.0):
    for i, (dx, dy, r) in enumerate(((-60, 20, 60), (0, -20, 80), (70, 14, 62), (10, 40, 70))):
        cv.drawCircle(x + dx * s, y + dy * s, r * s, P(h(('5E4878', '7A5A88', '6E4A80', '4A3A6A')[i])))
    if int(t * 6) % 3 == 0:
        cv.drawPath(path(((x - 10 * s, y + 50 * s), (x - 34 * s, y + 110 * s), (x - 6 * s, y + 104 * s), (x - 28 * s, y + 160 * s))), P(AMBER, 9 * s))


def flight_chart(cv, t):
    """Rook's case board for this one: a paper flight chart of the East Coast (a sketch, not a map)."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('E4D7B6')))
    for i in range(1, 11):
        cv.drawLine(i * 180, 0, i * 180, H, P(0x223A5A8A, 3))
    for j in range(1, 6):
        cv.drawLine(0, j * 180, W, j * 180, P(0x223A5A8A, 3))
    sea = path(((1920, 0), (1500, 0), (1420, 110), (1500, 200), (1330, 330), (1380, 450), (1210, 580), (1250, 700), (1060, 830), (1090, 960), (960, 1080), (1920, 1080)), True)
    cv.drawPath(sea, P(h('B9D2DC')))
    cv.drawPath(sea, P(h('5A7E96'), 6))
    cv.save()
    cv.translate(1760, 880)
    cv.rotate(8 * math.sin(t * 0.9))
    cv.drawCircle(0, 0, 80, P(NAVY, 6))
    cv.drawPath(path(((0, -100), (17, 0), (0, 100), (-17, 0)), True), P(NAVY))
    cv.drawPath(path(((0, -100), (17, 0), (-17, 0)), True), P(RED))
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, W - 14, H - 14), P(ORANGE, 10))


def pinned(cv, x, y, w_, h_, ang, col=CREAM):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 26, 18, P(0x55000000))
    cv.drawCircle(-3, -h_ / 2 + 22, 16, P(RED))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col=h('FFD866')):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, col)
    cv.rotate(ang)
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


def punch(cv, text, x, y, size, k, col=WHITE):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
    Wd.text_card(cv, text, 0, 0, size, col, BLACK)
    cv.restore()


def night(cv, t, a='0B1030', b='1E3C6A', n=40):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(a)), (1, h(b))])
    Wd.particles(cv, W, H, t * 0.4, n, 0x66FFFFFF, 7, size=(2, 4), drift=(30, -20), wobble=12, twinkle=True)


def tick_mark(cv, x, y, s, ok):
    if ok:
        cv.drawPath(path(((x - 30 * s, y), (x - 8 * s, y + 24 * s), (x + 34 * s, y - 30 * s))), P(GREEN, 16 * s))
    else:
        cv.drawLine(x - 28 * s, y - 28 * s, x + 28 * s, y + 28 * s, P(RED, 16 * s))
        cv.drawLine(x - 28 * s, y + 28 * s, x + 28 * s, y - 28 * s, P(RED, 16 * s))


# ------------------------------------------------------------------ flat inserts
def alt_km(cv, c):
    """How high: an altitude tape; the jet marker climbs to 14 km."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('160F38')), (0.55, h('5A2E78')), (0.8, h('C8603E')), (1, h('F0A050'))])
    Wd.particles(cv, W, H, c.t * 0.3, 40, 0x88FFFFFF, 7, size=(2, 4), drift=(0, 0), wobble=0, twinkle=True)
    k = ease(c.k * 2.2)
    x0, top, bot = 330, 130, 760
    cv.drawLine(x0, top - 40, x0, bot, P(WHITE, 8))
    for i in range(15):
        y = lerp(bot, top, i / 14)
        big = i % 2 == 0
        cv.drawLine(x0 - (46 if big else 26), y, x0, y, P(WHITE, 8 if big else 5))
        if big and i:
            Wd.text_card(cv, str(i), x0 - 100, y + 18, 48, 0xCCFFFFFF, None)
    for i in range(12):
        Wd.cloud(cv, 80 + i * 170 + 20 * math.sin(c.t * 0.6 + i), 900 + 34 * math.sin(i * 2.0), 110 + 20 * (i % 3), h('F4D0B0'), h('D89A8A'))
    Wd.cloud(cv, 760, 640, 150, h('C89AB0'), h('8A5C8E'))
    Wd.text_card(cv, 'THE STORM', 760, 660, 52, WHITE, BLACK)
    y = lerp(bot, top, k)
    cv.drawLine(x0, y, x0 + 90, y, P(AMBER, 10))
    jet_icon(cv, x0 + 170 + 8 * math.sin(c.t * 7), y, 0.9, AMBER, 90)
    k2 = pop(c.lt, 0.45 * c.d)
    v = min(14, int(14 * k + 0.5))
    cv.save()
    cv.translate(1260, 400)
    cv.scale(1.5 - 0.5 * k2 if k2 > 0 else 1, 1.5 - 0.5 * k2 if k2 > 0 else 1)
    Wd.text_card(cv, f'{v} KM', 0, 0, 230, AMBER, BLACK)
    if k2 > 0:
        Wd.text_card(cv, '47,000 FT', 0, 130, 96, WHITE, BLACK)
    cv.restore()


def board_no(cv, c):
    flight_chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(640, 430)
    cv.scale(s, s)
    pinned(cv, 0, 0, 860, 600, -2)
    cv.rotate(-2)
    photo(cv, 'storm', 0, 16, 790, 500, (0.5, 0.45))
    cv.restore()
    card(cv, '14 KM UP', 1400, 250, 460, 170, 4, 76, pop(c.lt, 0.25 * c.d))
    card(cv, 'INTO A STORM', 1420, 480, 560, 170, -3, 66, pop(c.lt, 0.42 * c.d), h('BFD8EC'))
    stamp(cv, 'NO CHANCE', 700, 440, -10, 130, pop(c.lt, 0.66 * c.d, 0.12))


def id_card(cv, c):
    """Who he is: the pilot file."""
    flight_chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(640, 420)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    pinned(cv, 0, 0, 980, 640, -2)
    cv.rotate(-2)
    cv.drawRect(skia.Rect.MakeXYWH(-490, -250, 980, 210), P(NAVY))
    Wd.text_card(cv, 'LT. COL.', 0, -172, 54, 0xCCFFFFFF, None)
    Wd.text_card(cv, 'WILLIAM RANKIN', 0, -78, 96, AMBER, None)
    cv.save()
    cv.translate(0, 30)
    cv.scale(0.8, 0.8)
    for sx in (-1, 1):
        cv.drawPath(path(((sx * 40, -10), (sx * 250, -44), (sx * 230, -8), (sx * 200, 4), (sx * 180, 24), (sx * 130, 30), (sx * 110, 46), (sx * 40, 40)), True), P(h('C89A3A')))
    cv.drawCircle(0, 12, 50, P(h('C89A3A')))
    cv.drawCircle(0, 12, 30, P(NAVY))
    cv.restore()
    Wd.text_card(cv, 'U.S. MARINE CORPS', 0, 160, 76, INK, None)
    if pop(c.lt, 0.35 * c.d) > 0:
        Wd.text_card(cv, 'PILOT, F-8 CRUSADER', 0, 250, 58, h('B02A20'), None)
    cv.restore()
    k3 = pop(c.lt, 0.15 * c.d, 0.2)
    if k3 > 0:
        cv.save()
        cv.translate(1440, 420 + 60 * (1 - k3))
        pinned(cv, 0, 0, 520, 620, 3)
        cv.rotate(3)
        photo(cv, 'rankin', 0, 18, 460, 530, (0.5, 0.1))
        cv.restore()


def record(cv, c):
    """His record: two wars, about a hundred combat missions (a tally fills in)."""
    night(cv, c.t, '0E1428', '2A2238')
    punch(cv, 'WORLD WAR TWO', 520, 210, 96, pop(c.lt, 0.05 * c.d))
    punch(cv, 'KOREA', 520, 340, 96, pop(c.lt, 0.3 * c.d))
    n = int(100 * ease((c.k - 0.45) / 0.45))
    for i in range(100):
        x, y = 1040 + (i % 20) * 38, 100 + (i // 20) * 72
        on = i < n
        cv.drawLine(x, y, x + (10 if (i % 5) != 4 else -150), y + 50 if (i % 5) != 4 else y + 44, P(AMBER if on else 0x33FFFFFF, 8))
    k2 = pop(c.lt, 0.5 * c.d)
    punch(cv, 'ABOUT 100', 1400, 640, 140, k2, AMBER)
    punch(cv, 'COMBAT MISSIONS', 1400, 750, 70, pop(c.lt, 0.62 * c.d))
    jet_icon(cv, 520 + 30 * math.sin(c.t * 1.3), 600 + 16 * math.sin(c.t * 2.1), 1.7, 0x55FFFFFF, 90)


def route(cv, c):
    """The flight on Rook's chart: Massachusetts to South Carolina, the storm on the way."""
    flight_chart(cv, c.t)
    a, b = (1330, 200), (880, 800)
    kk = ease(c.k * 1.25)
    end = (lerp(a[0], b[0], kk), lerp(a[1], b[1], kk))
    n = 26
    for i in range(n):
        u0, u1 = i / n, (i + 0.6) / n
        col = RED if u0 <= kk else 0x44B02A20
        cv.drawLine(lerp(a[0], b[0], u0), lerp(a[1], b[1], u0), lerp(a[0], b[0], u1), lerp(a[1], b[1], u1), P(col, 10))
    for x, y in (a, b):
        cv.drawCircle(x, y, 22, P(RED))
        cv.drawCircle(x, y, 10, P(CREAM))
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 90
    jet_icon(cv, end[0], end[1], 0.62, NAVY, ang)
    jet_icon(cv, end[0] + 70, end[1] - 30, 0.5, NAVY, ang)
    storm_icon(cv, 1010, 560, 0.85 + 0.06 * math.sin(c.t * 3), c.t)
    card(cv, 'SOUTH WEYMOUTH, MASS.', 760, 190, 820, 130, -2, 58, pop(c.lt, 0.08 * c.d))
    card(cv, 'BEAUFORT, S.C.', 440, 760, 580, 130, 3, 62, pop(c.lt, 0.55 * c.d), h('BFD8EC'))
    punch(cv, 'TWO F-8 CRUSADERS', 520, 460, 76, pop(c.lt, 0.32 * c.d), NAVY)


def alt_stack(cv, c):
    """The storm tops out around 45,000 ft; the two jets climb over it at 47,000."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('160F38')), (0.5, h('5A2E78')), (0.85, h('C8603E')), (1, h('F0A050'))])
    Wd.particles(cv, W, H, c.t * 0.3, 30, 0x88FFFFFF, 7, size=(2, 4), drift=(0, 0), wobble=0, twinkle=True)
    grow = ease(c.k * 1.6)
    topy = lerp(520, 330, grow)
    for i in range(16):
        u = i / 15
        y = lerp(860, topy + 40, u)
        r = lerp(210, 120, u) + 20 * math.sin(i * 2.3 + c.t * 0.8)
        cv.drawCircle(700 + 70 * math.sin(i * 1.9), y, r, P(h(('4A3A6A', '5E4878', '7A5A88', 'A0708E')[min(3, i // 4)])))
    for i in range(7):
        cv.drawCircle(420 + i * 95, topy + 30 + 12 * math.sin(i * 2), 80, P(h('C88A8E')))
    if int(c.t * 7) % 4 == 0:
        Wd.bolt(cv, 720, topy + 160, topy + 420, int(c.t * 7), AMBER, 8, 2)
    cv.drawLine(180, topy - 30, 1500, topy - 30, P(0xAAFFFFFF, 5))
    punch(cv, 'STORM TOP: ABOUT 45,000 FT', 1380, topy + 60, 60, pop(c.lt, 0.2 * c.d))
    jy = 215
    cv.drawLine(180, jy, 1500, jy, P(Wd.alpha(AMBER, 0.6), 5))
    x = lerp(240, 1000, c.k)
    jet_icon(cv, x, jy - 4 + 5 * math.sin(c.t * 6), 0.8, AMBER, 90)
    jet_icon(cv, x - 150, jy + 34 + 5 * math.sin(c.t * 5), 0.6, AMBER, 90)
    punch(cv, '47,000 FT', 1420, jy - 50, 110, pop(c.lt, 0.5 * c.d), AMBER)


def gear(cv, c):
    """What he has on: a flight suit, a helmet, an oxygen mask. What he does not: a pressure suit."""
    night(cv, c.t, '14101E', '3A1E22')
    a = 0.10 * (0.5 + 0.5 * math.sin(c.t * 16))
    cv.drawRect(skia.Rect.MakeWH(W, H), P(RED, None, a))
    rows = (('FLIGHT SUIT', True, 0.05), ('HELMET', True, 0.2), ('OXYGEN MASK', True, 0.35), ('PRESSURE SUIT', False, 0.55))
    for i, (txt, ok, at) in enumerate(rows):
        k = pop(c.lt, at * c.d)
        if k <= 0:
            continue
        y = 150 + i * 170
        cv.save()
        cv.translate(960, y)
        cv.scale(1.3 - 0.3 * k, 1.3 - 0.3 * k)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-620, -70, 1240, 140), 20, 20, P(0xDD0B1020))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-620, -70, 1240, 140), 20, 20, P(GREEN if ok else RED, 8))
        Wd.text_card(cv, txt, -90, 30, 88, WHITE if ok else h('FF8A80'), None)
        tick_mark(cv, 490, 0, 1.2 + (0 if ok else 0.15 * math.sin(c.t * 12)), ok)
        cv.restore()


def thermo(cv, c):
    """The air outside: about fifty below zero."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1030')), (1, h('1E3C6A'))])
    Wd.particles(cv, W, H, c.t, 70, 0x77DFF4FF, 11, size=(2, 6), drift=(-460, -260), wobble=10)
    k = ease(c.k * 1.6)
    cx, top, bot = 520, 120, 640
    j = 4 * math.sin(c.t * 45) * k
    cv.save()
    cv.translate(j, 0)
    cv.drawRoundRect(skia.Rect.MakeLTRB(cx - 56, top - 40, cx + 56, bot + 60), 56, 56, P(WHITE))
    cv.drawCircle(cx, bot + 90, 100, P(WHITE))
    col = Wd.mix(RED, BLUE, k)
    lvl = lerp(top + 50, bot, k)
    cv.drawRoundRect(skia.Rect.MakeLTRB(cx - 30, lvl, cx + 30, bot + 60), 28, 28, P(col))
    cv.drawCircle(cx, bot + 90, 74, P(col))
    for i in range(9):
        y = lerp(top + 50, bot, i / 8)
        cv.drawLine(cx + 74, y, cx + (140 if i % 2 == 0 else 112), y, P(WHITE, 8))
    cv.restore()
    v = int(lerp(20, -50, k))
    k2 = pop(c.lt, 0.45 * c.d)
    cv.save()
    cv.translate(1220, 400)
    cv.scale(1.5 - 0.5 * k2 if k2 > 0 else 1, 1.5 - 0.5 * k2 if k2 > 0 else 1)
    Wd.text_card(cv, f'{v}°', 0, 0, 280, Wd.mix(AMBER, ICE, k), BLACK)
    cv.restore()
    Wd.text_card(cv, 'OUTSIDE AIR', 1220, 560, 72, 0xCCFFFFFF, BLACK)


def chute_plan(cv, c):
    """The plan: free fall to 10,000 ft, where the parachute opens by itself. About three and a half minutes."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('160F38')), (0.6, h('3A2E68')), (1, h('7A5A88'))])
    Wd.particles(cv, W, H, c.t, 40, 0x44FFFFFF, 5, size=(2, 5), drift=(0, -700), wobble=6)
    x0, top, bot = 420, 110, 780
    cv.drawLine(x0, top, x0, bot, P(WHITE, 8))
    yy = lambda ft: lerp(bot, top, ft / 47000)
    for ft, txt in ((47000, '47,000 FT'), (10000, '10,000 FT')):
        y = yy(ft)
        cv.drawLine(x0 - 40, y, x0 + 900, y, P(0x88FFFFFF if ft > 20000 else Wd.alpha(GREEN, 0.9), 6))
        Wd.text_card(cv, txt, x0 - 200, y + 18, 50, WHITE, BLACK)
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 4, yy(10000), x0 + 900, bot), P(Wd.alpha(GREEN, 0.16)))
    Wd.text_card(cv, 'AIR THICK ENOUGH TO BREATHE', x0 + 460, yy(10000) + 90, 46, h('9AF0C0'), BLACK)
    kf = ease(c.k * 1.25)
    y = lerp(yy(47000), yy(10000), kf)
    xd = x0 + 300
    for i in range(14):
        u0 = i / 14
        if u0 < kf:
            cv.drawLine(xd, lerp(yy(47000), yy(10000), u0), xd, lerp(yy(47000), yy(10000), u0 + 0.045), P(AMBER, 8))
    if kf < 0.98:
        cv.drawCircle(xd, y, 20, P(AMBER))
        cv.drawLine(xd, y - 26, xd, y - 70 - 20 * math.sin(c.t * 20), P(0x99FFFFFF, 5))
    else:
        chute_icon(cv, xd, y - 40, 1.3)
        punch(cv, 'OPENS BY ITSELF', xd + 330, y - 30, 60, pop(c.lt, 0.82 * c.d), h('9AF0C0'))
    punch(cv, 'FREE FALL', 1380, 300, 110, pop(c.lt, 0.2 * c.d))
    punch(cv, 'ABOUT 3 1/2 MINUTES', 1380, 420, 76, pop(c.lt, 0.45 * c.d), AMBER)


def fall_timer(cv, c):
    """Counting the free fall he expects: three and a half minutes."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A0816')), (1, h('2B2148'))])
    for i in range(22):
        x = (i * 173) % W
        y = H - ((c.t * 2600 + i * 290) % (H + 500))
        cv.drawLine(x, y, x + 6, y + 200 + (i % 3) * 60, P(0x33FFFFFF, 6))
    secs = int(lerp(0, 210, ease(c.k * 1.2)))
    cx, cy, r = 620, 440, 300
    cv.drawCircle(cx, cy, r + 30, P(h('C8CCD8')))
    cv.drawCircle(cx, cy, r, P(h('101A2A')))
    cv.drawRoundRect(skia.Rect.MakeLTRB(cx - 34, cy - r - 90, cx + 34, cy - r - 20), 10, 10, P(h('C8CCD8')))
    cv.drawArc(skia.Rect.MakeLTRB(cx - r + 60, cy - r + 60, cx + r - 60, cy + r - 60), -90, max(1, secs / 210 * 360), False, P(ORANGE, 30))
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = r - (50 if i % 5 == 0 else 26)
        cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (r - 12), cy + math.sin(a) * (r - 12), P(0xAAFFFFFF, 8 if i % 5 == 0 else 4))
    a = math.radians(secs * 6 - 90)
    cv.drawLine(cx, cy, cx + math.cos(a) * (r - 70), cy + math.sin(a) * (r - 70), P(AMBER, 14))
    cv.drawCircle(cx, cy, 22, P(CREAM))
    Wd.text_card(cv, f'{secs // 60}:{secs % 60:02d}', 1340, 430, 260, AMBER, BLACK)
    punch(cv, 'UNTIL THE PARACHUTE', 1340, 560, 64, pop(c.lt, 0.3 * c.d))


def baro(cv, c):
    """The automatic release reads air pressure. Inside the storm the pressure is wild, and it trips early."""
    night(cv, c.t, '0C1420', '1D3644', 30)
    Wd.rain(cv, W, H, c.t, density=60, c=0x33BFE0FF, slant=0.2, speed=2400, length=70)
    cx, cy, r = 600, 440, 310
    cv.drawCircle(cx, cy, r + 34, P(h('C89A3A')))
    cv.drawCircle(cx, cy, r, P(h('F4EEDF')))
    for i in range(21):
        a = math.radians(-210 + i * 12)
        r0 = r - (60 if i % 5 == 0 else 34)
        cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (r - 14), cy + math.sin(a) * (r - 14), P(INK, 10 if i % 5 == 0 else 5))
    a0 = math.radians(-210 + 15 * 12)
    cv.drawArc(skia.Rect.MakeLTRB(cx - r + 24, cy - r + 24, cx + r - 24, cy + r - 24), -210 + 14 * 12, 36, False, P(GREEN, 26))
    Wd.text_card(cv, '10,000', cx + math.cos(a0) * (r - 120), cy + math.sin(a0) * (r - 120) + 14, 44, h('1E7A4A'), None)
    wild = ease(c.k * 2)
    ang = -150 + 70 * math.sin(c.t * 9) * wild + 40 * math.sin(c.t * 23) * wild + lerp(0, 130, ease((c.k - 0.5) * 2.5))
    an = math.radians(ang)
    cv.drawLine(cx - math.cos(an) * 50, cy - math.sin(an) * 50, cx + math.cos(an) * (r - 60), cy + math.sin(an) * (r - 60), P(RED, 16))
    cv.drawCircle(cx, cy, 30, P(INK))
    punch(cv, 'AUTOMATIC RELEASE', 1370, 250, 80, pop(c.lt, 0.08 * c.d))
    punch(cv, 'READS AIR PRESSURE', 1370, 350, 60, pop(c.lt, 0.25 * c.d), ICE)
    stamp(cv, 'TRIPPED EARLY', 1370, 560, -6, 104, pop(c.lt, 0.62 * c.d, 0.12))


def yoyo_graph(cv, c):
    """Up and down, as much as 6,000 ft at a time (the trace is an illustration, not his real track)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('120E26')), (1, h('1D3644'))])
    Wd.rain(cv, W, H, c.t, density=70, c=0x33BFE0FF, slant=0.25, speed=2400, length=70)
    x0, x1, y0, y1 = 220, 1700, 780, 380
    cv.drawLine(x0, y0, x1, y0, P(0xAAFFFFFF, 6))
    cv.drawLine(x0, y0, x0, y1 - 30, P(0xAAFFFFFF, 6))
    Wd.text_card(cv, 'HEIGHT', x0 + 90, y1 - 50, 44, 0xCCFFFFFF, BLACK)
    pts = []
    n = 120
    kk = ease(c.k * 1.15)
    for i in range(n + 1):
        u = i / n
        base = lerp(0.82, 0.12, u ** 1.6)
        wob = 0.26 * math.sin(u * 30) * math.sin(PI_ * min(1.0, u * 1.1)) + 0.07 * math.sin(u * 71)
        pts.append((lerp(x0, x1, u), lerp(y0, y1, max(0.03, min(1.0, base + wob)))))
    m = max(2, int(n * kk))
    cv.drawPath(path(pts[:m]), P(AMBER, 10))
    tip = pts[m - 1]
    chute_icon(cv, tip[0], tip[1] - 50, 0.85)
    k2 = pop(c.lt, 0.35 * c.d)
    if k2 > 0:
        bx, by0, by1 = 1640, 110, 300
        cv.drawLine(bx, by0, bx, by1, P(WHITE, 8))
        for yy_, s in ((by0, 1), (by1, -1)):
            cv.drawPath(path(((bx - 26, yy_ + 34 * s), (bx, yy_), (bx + 26, yy_ + 34 * s))), P(WHITE, 8))
    punch(cv, 'UP TO 6,000 FT', 1130, 200, 110, k2, AMBER)
    punch(cv, 'AT A TIME', 1130, 300, 70, pop(c.lt, 0.5 * c.d))


PI_ = math.pi


def clock_40(cv, c):
    """His watch: 6:00 when he ejects, 6:40 when he lands."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1420')), (1, h('16283A'))])
    Wd.rain(cv, W, H, c.t, density=90, c=0x33BFE0FF, slant=0.2, speed=2400, length=80)
    cx, cy, r = 620, 440, 300
    cv.save()
    cv.translate(cx, cy)
    cv.rotate(-7 + 1.2 * math.sin(c.t * 30))
    cv.drawRect(skia.Rect.MakeLTRB(-160, -700, 160, 800), P(h('5A3A24')))
    for i in range(4):
        cv.drawCircle(0, 390 + i * 70, 12, P(h('2A1A10')))
    cv.drawRoundRect(skia.Rect.MakeLTRB(r + 20, -40, r + 76, 40), 12, 12, P(h('C8CCD8')))
    cv.drawCircle(0, 0, r + 34, P(h('C8CCD8')))
    cv.drawCircle(0, 0, r, P(h('101A2A')))
    mins = lerp(0, 40, ease(c.k * 1.45))
    cv.drawArc(skia.Rect.MakeLTRB(-r + 96, -r + 96, r - 96, r - 96), -90, max(1, mins * 6), False, P(ORANGE, 30))
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = r - (56 if i % 5 == 0 else 28)
        cv.drawLine(math.cos(a) * r0, math.sin(a) * r0, math.cos(a) * (r - 14), math.sin(a) * (r - 14), P(h('9AF0C0') if i % 5 == 0 else 0x88FFFFFF, 11 if i % 5 == 0 else 5))
    ah = math.radians(180 + mins / 60 * 30 - 90)
    cv.drawLine(0, 0, math.cos(ah) * (r - 150), math.sin(ah) * (r - 150), P(CREAM, 24))
    am = math.radians(mins * 6 - 90)
    cv.drawLine(0, 0, math.cos(am) * (r - 60), math.sin(am) * (r - 60), P(AMBER, 16))
    cv.drawCircle(0, 0, 26, P(CREAM))
    cv.restore()
    punch(cv, '6:00 TO 6:40', 1370, 380, 120, pop(c.lt, 0.4 * c.d))
    punch(cv, '40 MINUTES', 1370, 520, 96, pop(c.lt, 0.6 * c.d), AMBER)


def time_mag(cv, c):
    """Where the boy comes from: Time magazine's report of 17 August 1959 (our card, not the magazine's page)."""
    flight_chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.25)
    cv.save()
    cv.translate(680, 430 + 50 * (1 - k))
    pinned(cv, 0, 0, 1180, 620, -2)
    cv.rotate(-2)
    cv.drawRect(skia.Rect.MakeXYWH(-590, -230, 1180, 120), P(NAVY))
    Wd.text_card(cv, 'REPORTED BY TIME MAGAZINE', 0, -150, 62, WHITE, None)
    Wd.text_card(cv, '17 AUGUST 1959', 0, -30, 70, h('B02A20'), None)
    if pop(c.lt, 0.3 * c.d) > 0:
        Wd.text_card(cv, 'A SMALL BOY IN THE CAR', 0, 90, 66, INK, None)
    if pop(c.lt, 0.5 * c.d) > 0:
        Wd.text_card(cv, 'SAW A JET PILOT', 0, 180, 66, INK, None)
        Wd.text_card(cv, 'STANDING IN THE ROAD', 0, 266, 66, INK, None)
    cv.restore()
    card(cv, 'ABOUT 12 CARS', 1600, 210, 520, 140, 5, 54, pop(c.lt, 0.12 * c.d), h('BFD8EC'))
    card(cv, 'PASSED HIM', 1610, 400, 440, 140, -3, 54, pop(c.lt, 0.2 * c.d), h('BFD8EC'))
    card(cv, 'ONE STOPPED', 1600, 610, 480, 140, -4, 58, pop(c.lt, 0.68 * c.d))


def injuries(cv, c):
    """What the doctors found."""
    night(cv, c.t, '0E1A1E', '24403A')
    cv.drawRoundRect(skia.Rect.MakeXYWH(250, 90, 190, 700), 30, 30, P(0x33FFFFFF))
    cv.drawRect(skia.Rect.MakeXYWH(315, 150, 60, 200), P(WHITE))
    cv.drawRect(skia.Rect.MakeXYWH(245 + 0, 220, 200, 60), P(WHITE))
    b = 0.5 + 0.5 * math.sin(c.t * 6)
    pts = [(250 + i * 6.3, 560 - (90 * math.exp(-((i % 15) - 6) ** 2 / 3.0)) * (1 if (i % 15) < 10 else 0)) for i in range(31)]
    cv.drawPath(path(pts), P(Wd.alpha(GREEN, 0.5 + 0.5 * b), 8))
    rows = (('FROSTBITE', 0.05, ICE), ('WELTS AND BRUISES', 0.3, h('FFD866')), ('DECOMPRESSION SHOCK', 0.55, h('FF8A80')))
    for i, (txt, at, col) in enumerate(rows):
        k = pop(c.lt, at * c.d)
        if k <= 0:
            continue
        cv.save()
        cv.translate(1130, 190 + i * 220)
        cv.scale(1.3 - 0.3 * k, 1.3 - 0.3 * k)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-560, -84, 1120, 168), 22, 22, P(0xDD0B1020))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-560, -84, 1120, 168), 22, 22, P(col, 8))
        Wd.text_card(cv, txt, 0, 30, 84, col, None)
        cv.restore()


def book(cv, c):
    """His book, 1960. Our own drawing of a book, not the real jacket."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A1420')), (1, h('3A2A22'))])
    Wd.particles(cv, W, H, c.t * 0.5, 40, 0x55FFE0C0, 5, size=(2, 5), drift=(40, -30), wobble=30, twinkle=True)
    k = pop(c.lt, 0.0, 0.3)
    cv.save()
    cv.translate(640, 440 + 80 * (1 - k))
    cv.rotate(-6 + 2 * math.sin(c.t * 1.4))
    cv.drawRect(skia.Rect.MakeXYWH(-250 + 26, -330 + 22, 520, 660), P(0x88000000))
    cv.drawRect(skia.Rect.MakeXYWH(-276, -330, 40, 660), P(h('0E1830')))
    cv.drawRect(skia.Rect.MakeXYWH(-240, -330, 500, 660), P(NAVY))
    cv.drawRect(skia.Rect.MakeXYWH(-240, -330, 500, 660), P(AMBER, 6))
    for i, (dx, dy, r) in enumerate(((-90, -40, 70), (-10, -70, 90), (80, -36, 72), (0, -10, 84))):
        cv.drawCircle(10 + dx, -150 + dy, r, P(h(('34406A', '465282', '3A4672', '2A345A')[i])))
    cv.drawPath(path(((20, -130), (-30, -40), (14, -48), (-34, 60))), P(AMBER, 14))
    Wd.text_card(cv, 'THE MAN WHO', 10, 110, 50, WHITE, None)
    Wd.text_card(cv, 'RODE THE', 10, 170, 50, WHITE, None)
    Wd.text_card(cv, 'THUNDER', 10, 240, 68, AMBER, None)
    Wd.text_card(cv, 'WILLIAM H. RANKIN', 10, 300, 30, 0xCCFFFFFF, None)
    cv.restore()
    punch(cv, 'HIS OWN ACCOUNT', 1340, 300, 92, pop(c.lt, 0.25 * c.d))
    punch(cv, '1960', 1340, 470, 190, pop(c.lt, 0.5 * c.d), AMBER)


def years(cv, c):
    """1959, 1964, 2009."""
    night(cv, c.t, '160F38', '3A2A5A', 50)
    x0, x1, y = 260, 1660, 470
    kk = ease(c.k * 1.3)
    cv.drawLine(x0, y, x1, y, P(0x55FFFFFF, 10))
    cv.drawLine(x0, y, lerp(x0, x1, kk), y, P(AMBER, 12))
    marks = ((1959, 'THE STORM', 0.0), (1964, 'RETIRES', 0.1), (2009, 'DIES, 6 JULY', 1.0))
    for yr, txt, u in marks:
        x = lerp(x0, x1, u)
        on = kk >= u - 0.01
        cv.drawCircle(x, y, 26, P(AMBER if on else 0x55FFFFFF))
        cv.drawCircle(x, y, 11, P(h('160F38')))
        if on:
            up = yr != 1964
            Wd.text_card(cv, str(yr), x + (0 if yr != 1964 else 60), y - 70 if up else y + 130, 100, WHITE, BLACK)
            Wd.text_card(cv, txt, x + (0 if yr != 1964 else 60), y - 170 if up else y + 200, 50, ICE, BLACK)
    k2 = pop(c.lt, 0.7 * c.d)
    if k2 > 0:
        cv.drawLine(x0, y + 60, x0, y + 250, P(WHITE, 6))
        cv.drawLine(x1, y + 60, x1, y + 250, P(WHITE, 6))
        cv.drawLine(x0, y + 250, x1, y + 250, P(WHITE, 6))
    punch(cv, 'ALMOST EXACTLY 50 YEARS', 1060, y + 330, 84, k2, AMBER)
    jet_icon(cv, lerp(x0, x1, kk), y - 6 + 6 * math.sin(c.t * 5), 0.5, AMBER, 90)


def board_true(cv, c):
    flight_chart(cv, c.t)
    pinned(cv, 620, 430, 620, 700, -2)
    cv.save()
    cv.translate(620, 430)
    cv.rotate(-2)
    photo(cv, 'rankin', 0, 20, 550, 600, (0.5, 0.1))
    cv.restore()
    stamp(cv, 'TRUE', 640, 520, -14, 200, pop(c.lt, 0.2 * c.d, 0.12), GREEN)
    card(cv, '14 KM UP', 1380, 200, 480, 160, 4, 76, pop(c.lt, 0.34 * c.d))
    card(cv, '40 MINUTES', 1420, 420, 520, 160, -4, 76, pop(c.lt, 0.48 * c.d), h('BFD8EC'))
    card(cv, 'FLEW AGAIN', 1380, 640, 500, 160, 3, 76, pop(c.lt, 0.62 * c.d))


SHOTS = {f.__name__: f for f in (alt_km, board_no, id_card, record, route, alt_stack, gear, thermo, chute_plan, fall_timer, baro, yoyo_graph,
                                 clock_40, time_mag, injuries, book, years, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def streaks(cv, c):
    """Falling: the air tears upward past the lens."""
    for i in range(22):
        x = (i * 173) % W
        y = H - ((c.t * 2800 + i * 290) % (H + 500))
        cv.drawLine(x, y, x + 8, y + 190 + (i % 3) * 60, P(0x33FFFFFF, 6))


def downpour(cv, c):
    Wd.rain(cv, W, H, c.t, density=150, c=0x44BFE0FF, slant=0.3, speed=2200, length=70)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, density=70, c=0x33BFE0FF, slant=0.12, speed=1500, length=50)


def chevrons(cv, c):
    downpour(cv, c)
    for i in range(4):
        y = 820 - ((c.t * 700 + i * 200) % 760)
        a = 1 - abs(y - 440) / 400
        if a > 0:
            cv.drawLine(1690, y + 56, 1750, y, P(AMBER, 16, a))
            cv.drawLine(1750, y, 1810, y + 56, P(AMBER, 16, a))


def warn(cv, c):
    a = 0.13 * (0.5 + 0.5 * math.sin(c.t * 22))
    cv.drawRect(skia.Rect.MakeWH(W, H), P(RED, None, a))


def frost(cv, c):
    Wd.particles(cv, W, H, c.t, 60, Wd.alpha(0xFFDFF4FF, 0.4), 13, size=(2, 6), drift=(-420, -60), wobble=18, twinkle=True)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x44FFE0C0, 5, size=(2, 5), drift=(30, -24), wobble=30, twinkle=True)


def label(text, x=420, y=190, size=84, at=0.3, col='FFFFFF', ang=-3):
    def f(cv, c):
        if c.lt > at:
            k = min(1, (c.lt - at) / 0.12)
            cv.save()
            cv.translate(x, y)
            cv.rotate(ang)
            cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
            Wd.text_card(cv, text, 0, 0, size, h(col), BLACK)
            cv.restore()
    return f


def both(*fs):
    def f(cv, c):
        for g in fs:
            if g:
                g(cv, c)
    return f


def pick(a, b):
    """a on the first use of a shot type, b on its re-framed or variant repeats (either may be None)."""
    def g(cv, c):
        f = b if c.prm else a
        if f:
            f(cv, c)
    return g


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1420, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, BLACK)
        Wd.text_card(cv, 'CASE 007  CLOSED', 0, 90, 54, WHITE, BLACK)
        cv.restore()


OVER = dict(
    fall_in=streaks, seat_away=streaks, rook_fall=streaks, swell=streaks, glove_off=streaks, mask_on=streaks, cloud_dive=streaks,
    frost_hand=frost, chute_yank=downpour, rook_up=chevrons, fire_light=warn, rook_gulp=warn, handle_snap=warn, rook_deadpan=warn,
    radio_call=warn, reach_handles=warn, dark_fall=both(streaks, downpour), chute_open=downpour, storm_wide=downpour, updraft=chevrons,
    rook_chute=chevrons, elevator=downpour, hail_hit=downpour, canopy_hail=downpour, blue_sheet=downpour, rook_zap=downpour,
    thunder_feel=downpour, rain_breath=downpour, rook_soak=downpour, chute_sheet=downpour, seasick=downpour, rook_watch=downpour,
    yo_yo=downpour, drop_out=downpour, calm_rain=drizzle, tree_hit=downpour, tree_land=downpour, helmet_cu=drizzle,
    wrist=both(drizzle, label('6:40 PM', 1420, 300, 150, 0.35, 'FFB000', -4)), woods_walk=drizzle, cars_pass=drizzle, road=downpour,
    boy_car=drizzle, store_out=drizzle, ambulance=drizzle, typing=motes, salute=motes, ward=motes, ward_cu=motes,
    signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (the pilot under his parachute inside the storm, Rook rising past) + a hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('26304A'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(600, 0), (960, 0)], [0x00000000, 0xD0000000])))
    Wd.text_card(cv, '40 MIN', 990, 300, 136, AMBER, BLACK)
    Wd.text_card(cv, 'INSIDE', 990, 420, 92, WHITE, BLACK)
    Wd.text_card(cv, 'A STORM', 990, 520, 92, WHITE, BLACK)
