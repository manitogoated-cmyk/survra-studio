"""Case 007 - William Rankin. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(Rook's flight-chart case board, the altitude tape, the pilot file, the thermometer, the wristwatch) and the 2D
overlays drawn on top of 3D shots (speed streaks, driving rain, climb chevrons, the red warning pulse, the sign-off)."""
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
ORANGE, AMBER, RED, CREAM, BLUE, NAVY = h('FF7A1A'), h('FFB000'), h('E5392F'), h('F4EEDF'), h('7AB8FF'), h('1B2A4A')


def pop(lt, t0, d=0.14):
    return max(0.0, min(1.0, (lt - t0) / d))


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


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


def path(pts, close=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def jet_icon(cv, x, y, s, col, ang=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    cv.drawPath(path(((0, -70), (14, -20), (70, 30), (70, 46), (14, 28), (12, 54), (34, 72), (34, 82), (0, 74),
                      (-34, 82), (-34, 72), (-12, 54), (-14, 28), (-70, 46), (-70, 30), (-14, -20)), True), P(col))
    cv.restore()


def flight_chart(cv, t):
    """Rook's case board for this one: a paper flight chart of the East Coast with the route drawn in red."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('E4D7B6')))
    for i in range(1, 6):
        cv.drawLine(i * 180, 0, i * 180, H, P(0x223A5A8A, 3))
    for j in range(1, 11):
        cv.drawLine(0, j * 180, W, j * 180, P(0x223A5A8A, 3))
    sea = path(((1080, 0), (760, 0), (700, 190), (790, 330), (640, 560), (700, 760), (560, 980), (600, 1180), (430, 1420), (470, 1640), (330, 1920), (1080, 1920)), True)
    cv.drawPath(sea, P(h('B9D2DC')))
    cv.drawPath(sea, P(h('5A7E96'), 6))
    a, b = (760, 250), (420, 1560)
    n = 26
    for i in range(n):
        if i % 2 == 0:
            k0, k1 = i / n, (i + 0.7) / n
            cv.drawLine(lerp(a[0], b[0], k0), lerp(a[1], b[1], k0), lerp(a[0], b[0], k1), lerp(a[1], b[1], k1), P(RED, 9))
    for x, y in (a, b):
        cv.drawCircle(x, y, 20, P(RED))
        cv.drawCircle(x, y, 9, P(CREAM))
    cv.save()
    cv.translate(170, 1700)
    cv.rotate(8 * math.sin(t * 0.9))
    cv.drawCircle(0, 0, 96, P(NAVY, 6))
    cv.drawPath(path(((0, -120), (20, 0), (0, 120), (-20, 0)), True), P(NAVY))
    cv.drawPath(path(((0, -120), (20, 0), (-20, 0)), True), P(RED))
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(ORANGE, 10))


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


# ------------------------------------------------------------------ flat inserts
def alt_km(cv, c):
    """How high: an altitude tape; the jet marker climbs to 14 km."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('160F38')), (0.55, h('5A2E78')), (0.8, h('C8603E')), (1, h('F0A050'))])
    Wd.particles(cv, W, H, c.t * 0.3, 30, 0x88FFFFFF, 7, size=(2, 4), drift=(0, 0), wobble=0, twinkle=True)
    k = ease(c.k * 2.2)
    x0, top, bot = 230, 330, 1230
    cv.drawLine(x0, top - 60, x0, bot, P(0xFFFFFFFF, 8))
    for i in range(15):
        y = lerp(bot, top, i / 14)
        big = i % 2 == 0
        cv.drawLine(x0 - (46 if big else 26), y, x0, y, P(0xFFFFFFFF, 8 if big else 5))
        if big and i:
            Wd.text_card(cv, str(i), x0 - 110, y + 20, 56, 0xCCFFFFFF, None)
    for i in range(7):
        Wd.cloud(cv, 120 + i * 170, 1640 + 40 * math.sin(i * 2.0), 110 + 20 * (i % 3), h('F4D0B0'), h('D89A8A'))
    Wd.cloud(cv, 720, 1060, 150, h('C89AB0'), h('8A5C8E'))
    Wd.text_card(cv, 'THE STORM', 720, 1080, 60, 0xFFFFFFFF, 0xFF000000)
    y = lerp(bot, top, k)
    cv.drawLine(x0, y, 330, y, P(AMBER, 10))
    jet_icon(cv, 420 + 8 * math.sin(c.t * 7), y, 1.0, AMBER, 90)
    k2 = pop(c.lt, 0.5)
    v = min(14, int(14 * k + 0.5))
    cv.save()
    cv.translate(700, 640)
    cv.scale(1.5 - 0.5 * k2 if k2 > 0 else 1, 1.5 - 0.5 * k2 if k2 > 0 else 1)
    Wd.text_card(cv, f'{v} KM', 0, 0, 190, AMBER, 0xFF000000)
    if k2 > 0:
        Wd.text_card(cv, '47,000 FT', 0, 120, 84, 0xFFFFFFFF, 0xFF000000)
    cv.restore()


def board_no(cv, c):
    flight_chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 620)
    cv.scale(s, s)
    pinned(cv, 0, 0, 760, 640, 3)
    cv.rotate(3)
    photo(cv, 'storm', 0, 16, 690, 530, (0.5, 0.45))
    cv.restore()
    card(cv, '14 KM UP', 280, 1090, 420, 180, -5, 76, pop(c.lt, 0.25))
    card(cv, 'INTO A STORM', 775, 1120, 500, 180, 4, 60, pop(c.lt, 0.45), h('BFD8EC'))
    stamp(cv, 'NO CHANCE', 540, 640, -12, 124, pop(c.lt, 0.7, 0.12))


def id_card(cv, c):
    """Who he is: the pilot file."""
    flight_chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(540, 690)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    pinned(cv, 0, 0, 880, 900, -2)
    cv.rotate(-2)
    cv.drawRect(skia.Rect.MakeXYWH(-440, -380, 880, 210), P(NAVY))
    Wd.text_card(cv, 'LT. COL.', 0, -300, 58, 0xCCFFFFFF, None)
    Wd.text_card(cv, 'WILLIAM RANKIN', 0, -205, 92, AMBER, None)
    cv.save()
    cv.translate(0, -60)
    for sx in (-1, 1):
        cv.drawPath(path(((sx * 40, -10), (sx * 250, -44), (sx * 230, -8), (sx * 200, 4), (sx * 180, 24), (sx * 130, 30), (sx * 110, 46), (sx * 40, 40)), True), P(h('C89A3A')))
    cv.drawCircle(0, 12, 50, P(h('C89A3A')))
    cv.drawCircle(0, 12, 30, P(NAVY))
    cv.restore()
    Wd.text_card(cv, 'U.S. MARINE CORPS', 0, 110, 76, INK, None)
    k2 = pop(c.lt, 0.3)
    if k2 > 0:
        Wd.text_card(cv, 'PILOT, F-8 CRUSADER', 0, 205, 58, h('B02A20'), None)
    k3 = pop(c.lt, 0.55)
    if k3 > 0:
        cv.drawRoundRect(skia.Rect.MakeXYWH(-400, 260, 800, 150), 16, 16, P(NAVY))
        Wd.text_card(cv, 'MASSACHUSETTS', 0, 322, 46, 0xFFFFFFFF, None)
        Wd.text_card(cv, 'TO SOUTH CAROLINA', 0, 384, 46, 0xFFFFFFFF, None)
    cv.restore()


def thermo(cv, c):
    """The air outside: about fifty below zero."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1030')), (1, h('1E3C6A'))])
    Wd.particles(cv, W, H, c.t, 60, 0x77DFF4FF, 11, size=(2, 6), drift=(-260, -520), wobble=10)
    k = ease(c.k * 1.6)
    cx, top, bot = 300, 300, 1050
    j = 4 * math.sin(c.t * 45) * k
    cv.save()
    cv.translate(j, 0)
    cv.drawRoundRect(skia.Rect.MakeLTRB(cx - 62, top - 40, cx + 62, bot + 60), 62, 62, P(0xFFFFFFFF))
    cv.drawCircle(cx, bot + 90, 110, P(0xFFFFFFFF))
    col = Wd.mix(RED, BLUE, k)
    lvl = lerp(top + 60, bot, k)
    cv.drawRoundRect(skia.Rect.MakeLTRB(cx - 34, lvl, cx + 34, bot + 60), 30, 30, P(col))
    cv.drawCircle(cx, bot + 90, 82, P(col))
    for i in range(9):
        y = lerp(top + 60, bot, i / 8)
        cv.drawLine(cx + 80, y, cx + (150 if i % 2 == 0 else 120), y, P(0xFFFFFFFF, 8))
    cv.restore()
    v = int(lerp(20, -50, k))
    k2 = pop(c.lt, 0.5)
    cv.save()
    cv.translate(660, 620)
    cv.scale(1.5 - 0.5 * k2 if k2 > 0 else 1, 1.5 - 0.5 * k2 if k2 > 0 else 1)
    Wd.text_card(cv, f'{v}°', 0, 0, 210, Wd.mix(AMBER, 0xFFBFE4FF, k), 0xFF000000)
    cv.restore()
    Wd.text_card(cv, 'OUTSIDE AIR', 660, 760, 64, 0xCCFFFFFF, 0xFF000000)


def clock_40(cv, c):
    """His watch: 6:00 when he ejects, 6:40 when he lands."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1420')), (1, h('16283A'))])
    Wd.rain(cv, W, H, c.t, density=70, c=0x33BFE0FF, slant=0.2, speed=2400, length=80)
    cx, cy, r = 540, 700, 360
    cv.save()
    cv.translate(cx, cy)
    cv.rotate(-7 + 1.2 * math.sin(c.t * 30))
    cv.drawRect(skia.Rect.MakeLTRB(-190, -760, 190, 900), P(h('5A3A24')))
    for i in range(6):
        cv.drawCircle(0, 470 + i * 70, 12, P(h('2A1A10')))
    cv.drawRoundRect(skia.Rect.MakeLTRB(r + 20, -40, r + 80, 40), 12, 12, P(h('C8CCD8')))
    cv.drawCircle(0, 0, r + 36, P(h('C8CCD8')))
    cv.drawCircle(0, 0, r, P(h('101A2A')))
    mins = lerp(0, 40, ease(c.k * 1.45))
    cv.drawArc(skia.Rect.MakeLTRB(-r + 110, -r + 110, r - 110, r - 110), -90, max(1, mins * 6), False, P(ORANGE, 34))
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = r - (64 if i % 5 == 0 else 30)
        cv.drawLine(math.cos(a) * r0, math.sin(a) * r0, math.cos(a) * (r - 14), math.sin(a) * (r - 14), P(h('9AF0C0') if i % 5 == 0 else 0x88FFFFFF, 12 if i % 5 == 0 else 5))
    ah = math.radians(180 + mins / 60 * 30 - 90)
    cv.drawLine(0, 0, math.cos(ah) * (r - 170), math.sin(ah) * (r - 170), P(CREAM, 26))
    am = math.radians(mins * 6 - 90)
    cv.drawLine(0, 0, math.cos(am) * (r - 70), math.sin(am) * (r - 70), P(AMBER, 18))
    cv.drawCircle(0, 0, 28, P(CREAM))
    cv.restore()
    k2 = pop(c.lt, 0.42)
    if k2 > 0:
        cv.save()
        cv.translate(540, 1210)
        cv.scale(1.4 - 0.4 * k2, 1.4 - 0.4 * k2)
        Wd.text_card(cv, '6:00 TO 6:40', 0, 0, 96, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


def board_true(cv, c):
    flight_chart(cv, c.t)
    pinned(cv, 540, 660, 720, 800, -2)
    cv.save()
    cv.translate(540, 660)
    cv.rotate(-2)
    photo(cv, 'rankin', 0, 20, 650, 690, (0.5, 0.1))
    cv.restore()
    stamp(cv, 'TRUE', 560, 790, -14, 200, pop(c.lt, 0.2, 0.12), h('2FA866'))
    card(cv, '40 MINUTES', 310, 1180, 480, 180, -5, 72, pop(c.lt, 0.36), h('BFD8EC'))
    card(cv, 'FLEW AGAIN', 780, 1150, 470, 180, 5, 72, pop(c.lt, 0.5))


SHOTS = {f.__name__: f for f in (alt_km, board_no, id_card, thermo, clock_40, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def streaks(cv, c):
    """Falling: the air tears upward past the lens."""
    for i in range(16):
        x = (i * 173) % W
        y = H - ((c.t * 3400 + i * 290) % (H + 500))
        cv.drawLine(x, y, x + 10, y + 230 + (i % 3) * 70, P(0x33FFFFFF, 6))


def downpour(cv, c):
    Wd.rain(cv, W, H, c.t, density=120, c=0x44BFE0FF, slant=0.3, speed=2600, length=80)


def chevrons(cv, c):
    downpour(cv, c)
    for i in range(4):
        y = 1250 - ((c.t * 950 + i * 260) % 1040)
        a = 1 - abs(y - 730) / 560
        if a > 0:
            cv.drawLine(890, y + 60, 950, y, P(AMBER, 16, a))
            cv.drawLine(950, y, 1010, y + 60, P(AMBER, 16, a))


def warn(cv, c):
    a = 0.22 * (0.5 + 0.5 * math.sin(c.t * 22))
    cv.drawRect(skia.Rect.MakeWH(W, H), P(RED, None, a))


def frost(cv, c):
    Wd.particles(cv, W, H, c.t, 50, Wd.alpha(0xFFDFF4FF, 0.4), 13, size=(2, 6), drift=(-60, -420), wobble=18, twinkle=True)


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 007  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(fall_in=streaks, seat_away=streaks, rook_fall=streaks, swell=streaks, frost_hand=frost, chute_yank=downpour, rook_up=chevrons,
            fire_light=warn, rook_gulp=warn, handle_snap=warn, chute_open=downpour, storm_wide=downpour, updraft=chevrons, rook_chute=chevrons,
            hail_hit=downpour, blue_sheet=downpour, rook_zap=downpour, rain_breath=downpour, rook_watch=downpour, yo_yo=downpour,
            drop_out=downpour, tree_land=downpour, road=downpour, signoff=closed)
