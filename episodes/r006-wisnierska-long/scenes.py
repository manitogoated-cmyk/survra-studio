"""Case 006, the full case file (16:9) - Ewa Wisnierska. The story is filmed in 3D (world3d.py). This file holds the
flat graphic inserts on a 1920x1080 canvas (Rook's weather-chart case board, the flight computer, the Everest line,
the calendar, the route, the forecast, the climb rate, the cold, the stopwatch, the GPS, the memorial cards...), the
2D overlays drawn on top of 3D shots (sleet, ice crystals, climb arrows, gusts, the sign-off) and the thumbnail."""
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
ORANGE, AMBER, RED, CREAM, ICE, GREEN = h('FF7A1A'), h('FFB000'), h('E5392F'), h('F4EEDF'), h('CFEFFF'), h('3DDC84')
WHITE, BLACK = 0xFFFFFFFF, 0xFF000000


def pop(lt, t0, d=0.14):
    return max(0.0, min(1.0, (lt - t0) / d))


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def poly(cv, pts, paint):
    pth = skia.Path()
    pth.moveTo(*pts[0])
    for p_ in pts[1:]:
        pth.lineTo(*p_)
    pth.close()
    cv.drawPath(pth, paint)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) taped to the chart as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('5A6C98')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def chart(cv, t, cx=1500, cy=760):
    """Rook's case board for this one: a weather chart with pressure rings closing on a storm."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10213A')), (1, h('081220'))])
    for i in range(1, 16):
        cv.drawLine(i * 120, 0, i * 120, H, P(0x14FFFFFF, 2))
    for j in range(1, 9):
        cv.drawLine(0, j * 120, W, j * 120, P(0x14FFFFFF, 2))
    for i in range(8):
        r = 120 + i * 130 + 12 * math.sin(t * 1.3 + i)
        cv.drawOval(skia.Rect.MakeLTRB(cx - r * 1.3, cy - r, cx + r * 1.3, cy + r), P(0x2E8FC8FF, 5))
    for i in range(12):
        x, y = 90 + (i * 463) % 1740, 110 + (i * 297) % 860
        a = 0.6 + i + 0.2 * math.sin(t + i)
        cv.drawLine(x, y, x + 46 * math.cos(a), y + 46 * math.sin(a), P(0x338FC8FF, 5))
        cv.drawLine(x + 46 * math.cos(a), y + 46 * math.sin(a), x + 46 * math.cos(a) - 16 * math.cos(a - 0.6), y + 46 * math.sin(a) - 16 * math.sin(a - 0.6),
                    P(0x338FC8FF, 5))
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(ORANGE, 10))


def taped(cv, x, y, w_, h_, ang, col=CREAM):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    for sx in (-1, 1):
        cv.save()
        cv.translate(sx * (w_ / 2 - 30), -h_ / 2 + 6)
        cv.rotate(sx * 38)
        cv.drawRect(skia.Rect.MakeXYWH(-52, -17, 104, 34), P(0xCCFFB000))
        cv.restore()
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col=h('FFD866'), ink=INK):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    taped(cv, 0, 0, w_, h_, ang, col)
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.36, size, ink, None)
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
    """A label that pops in (k 0..1)."""
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
    Wd.text_card(cv, text, 0, 0, size, col, BLACK)
    cv.restore()


def glider_icon(cv, x, y, s, col=WHITE, ang=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    cv.drawArc(skia.Rect.MakeLTRB(-70, -60, 70, 40), 200, 140, False, P(col, 16))
    for dx in (-52, -20, 20, 52):
        cv.drawLine(dx, -44 + abs(dx) * 0.3, 0, 46, P(col, 3))
    cv.drawCircle(0, 54, 11, P(col))
    cv.restore()


def storm_icon(cv, x, y, s, t=0.0, dark=h('4A5670')):
    for dx, dy, r in ((-70, 10, 56), (0, -24, 78), (74, 6, 60), (10, 30, 70)):
        cv.drawCircle(x + dx * s, y + dy * s, r * s, P(dark))
    if (t * 3) % 1 < 0.7:
        poly(cv, [(x + 14 * s, y + 70 * s), (x - 26 * s, y + 150 * s), (x + 6 * s, y + 150 * s), (x - 16 * s, y + 220 * s), (x + 50 * s, y + 124 * s),
                  (x + 16 * s, y + 124 * s), (x + 44 * s, y + 70 * s)], P(AMBER))


def night(cv, t, a='0A0F1C', b='05070D', n=40):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(a)), (1, h(b))])
    Wd.particles(cv, W, H, t, n, 0x44CFEFFF, 9, size=(2, 5), drift=(-30, 50), wobble=20)


# ------------------------------------------------------------------ flat inserts (from the Short, re-laid for 16:9)
def device(cv, c, cx, cy, s=0.85):
    """Her flight computer body; leaves the canvas translated to the device centre."""
    j = 5 * math.sin(c.t * 40)
    cv.translate(cx + j, cy)
    cv.rotate(-3 + 1.5 * math.sin(c.t * 9))
    cv.scale(s, s)
    body = skia.Rect.MakeLTRB(-420, -440, 420, 440)
    cv.drawRoundRect(body.makeOffset(12, 18), 60, 60, P(0x99000000))
    cv.drawRoundRect(body, 60, 60, P(h('2A2F3A')))
    cv.drawRoundRect(body, 60, 60, P(ORANGE, 10))
    cv.drawRoundRect(skia.Rect.MakeLTRB(-360, -370, 360, 250), 26, 26, P(h('0E1A12')))
    for i in range(3):
        cv.drawCircle(-200 + i * 200, 345, 44, P(h('1A1E28')))


def alt_spin(cv, c):
    """Her flight computer: the altitude digits race upward (they never settle on an exact figure)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A0F1C')), (1, h('05070D'))])
    Wd.rain(cv, W, H, c.t, density=110, c=0x33CFE6FF, slant=0.45, speed=2600, length=70)
    lo, hi = (800, 9900) if not c.prm.get('mid') else (3600, 5200)
    cv.save()
    device(cv, c, 760, 440)
    Wd.text_card(cv, 'ALTITUDE', 0, -280, 62, h('6FE08A'), None)
    v = int(lerp(lo, hi, ease(c.k * 1.1)) / 7) * 7 + int(c.t * 60) % 7
    Wd.text_card(cv, f'{v:,}', -40, -40, 230, AMBER, None)
    Wd.text_card(cv, 'm', 300, -40, 110, AMBER, None)
    for i in range(12):
        on = i < 2 + 10 * c.k
        cv.drawRect(skia.Rect.MakeXYWH(-330 + i * 56, 200 - (20 + i * 9), 40, 20 + i * 9), P(h('6FE08A') if on else h('1E3A26')))
    cv.restore()
    for i in range(5):
        y = 760 - ((c.t * 700 + i * 170) % 760)
        a = 1 - abs(y - 400) / 420
        for x in (1380, 1560):
            cv.drawLine(x - 60, y + 60, x, y, P(AMBER, 18, max(0, a)))
            cv.drawLine(x, y, x + 60, y + 60, P(AMBER, 18, max(0, a)))
    if c.prm.get('mid'):
        punch(cv, 'STILL', 1470, 330, 110, pop(c.lt, 0.3))
        punch(cv, 'CLIMBING', 1470, 460, 110, pop(c.lt, 0.5), AMBER)


def everest_bar(cv, c):
    """A glider climbs past the summit line of Everest."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B24')), (0.6, h('1C2A5A')), (1, h('3A4A80'))])
    Wd.particles(cv, W, H, c.t * 0.3, 60, 0x88FFFFFF, 5, size=(2, 4), drift=(0, 0), wobble=0, twinkle=True)
    top = 500
    poly(cv, [(0, 1080), (260, 760), (470, 900), (700, 700), (900, 1080)], P(h('2A3558')))
    poly(cv, [(1150, 1080), (1420, 800), (1640, 900), (1920, 720), (1920, 1080)], P(h('2A3558')))
    poly(cv, [(420, 1080), (900, top), (1440, 1080)], P(h('3F4C78')))
    poly(cv, [(805, 600), (900, top), (1000, 610), (955, 585), (905, 640), (860, 575)], P(0xFFE8EEF8))
    for x in range(40, W - 40, 60):
        cv.drawLine(x, top, x + 34, top, P(WHITE, 6))
    Wd.text_card(cv, 'EVEREST  8,849 m', 330, top - 28, 54, WHITE, BLACK)
    gy = lerp(840, 250, ease(c.k * 1.25))
    cv.drawLine(1400, 900, 1400, gy + 90, P(AMBER, 8, 0.7))
    glider_icon(cv, 1400 + 10 * math.sin(c.t * 5), gy, 1.7, AMBER, 6 * math.sin(c.t * 4))
    k2 = pop(c.lt, 0.62)
    if k2 > 0 and gy < top:
        punch(cv, 'ALMOST', 420, 210, 96, k2)
        punch(cv, '10,000 m', 420, 360, 150, k2, AMBER)


def board_storm(cv, c):
    chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(620, 440)
    cv.scale(s, s)
    taped(cv, 0, 0, 900, 640, -3)
    cv.rotate(-3)
    photo(cv, 'storm', 0, 10, 830, 540, (0.5, 0.3))
    cv.restore()
    card(cv, '10 KM UP', 1430, 250, 500, 190, -5, 84, pop(c.lt, 0.3))
    card(cv, 'OUT COLD', 1480, 520, 520, 190, 4, 84, pop(c.lt, 0.5), h('BFE0EC'))
    stamp(cv, 'NO CHANCE', 700, 520, -12, 170, pop(c.lt, 0.72, 0.12))


def trophy(cv, c):
    """Who she is: a competition pilot."""
    chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(960, 440)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    taped(cv, 0, 0, 1500, 720, 1.5)
    cv.rotate(1.5)
    cv.drawRect(skia.Rect.MakeXYWH(-750, -360, 1500, 150), P(h('20242B')))
    Wd.text_card(cv, 'PILOT FILE:  EWA WISNIERSKA', 0, -258, 84, AMBER, None)
    cv.save()
    cv.translate(-520, 60)
    cv.rotate(8 * math.sin(c.t * 3))
    cv.scale(1.25, 1.25)
    poly(cv, [(-90, -110), (90, -110), (62, 30), (-62, 30)], P(AMBER))
    cv.drawArc(skia.Rect.MakeLTRB(-140, -100, -50, 0), 90, 180, False, P(AMBER, 16))
    cv.drawArc(skia.Rect.MakeLTRB(50, -100, 140, 0), 270, 180, False, P(AMBER, 16))
    cv.drawRect(skia.Rect.MakeXYWH(-16, 30, 32, 60), P(AMBER))
    cv.drawRect(skia.Rect.MakeXYWH(-80, 90, 160, 34), P(h('8A6A2A')))
    cv.restore()
    rows = (('BORN IN POLAND', 0.15, INK), ('FLIES FOR GERMANY', 0.36, INK), ('AGE 35', 0.55, INK), ('2005 WORLD CUP WINNER', 0.72, h('B02A20')))
    for i, (txt, at_, col) in enumerate(rows):
        k2 = pop(c.lt, at_)
        if k2 > 0:
            cv.save()
            cv.translate(130, -110 + i * 112)
            cv.scale(1.3 - 0.3 * k2, 1.3 - 0.3 * k2)
            Wd.text_card(cv, txt, 0, 0, 84, col, None)
            cv.restore()
    cv.restore()


def vario(cv, c):
    """Her climb gauge: pinned on UP."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('101626')), (1, h('05070D'))])
    Wd.rain(cv, W, H, c.t, density=100, c=0x2ECFE6FF, slant=0.45, speed=2600, length=70)
    cx, cy, r = 760, 440, 340
    cv.drawCircle(cx + 10, cy + 16, r + 40, P(0x88000000))
    cv.drawCircle(cx, cy, r + 40, P(h('2A2F3A')))
    cv.drawCircle(cx, cy, r + 40, P(ORANGE, 10))
    cv.drawCircle(cx, cy, r, P(h('0B0F18')))
    for i in range(25):
        a = math.radians(180 + (i - 12) * 11)
        up = i > 12
        col = Wd.mix(GREEN, RED, (i - 12) / 12) if up else h('5A6478')
        r0 = r - (70 if i % 4 == 0 else 44)
        cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (r - 14), cy + math.sin(a) * (r - 14), P(col, 16))
    Wd.text_card(cv, 'UP', cx + 20, cy - 150, 110, RED if (c.t * 6) % 1 < 0.6 else AMBER, None)
    Wd.text_card(cv, 'DOWN', cx + 20, cy + 230, 64, h('5A6478'), None)
    ang = math.radians(180 + lerp(-30, 128, ease(c.lt / 0.3)) + (3 * math.sin(c.t * 50) if c.lt > 0.3 else 0))
    cv.drawLine(cx, cy, cx + math.cos(ang) * (r - 90), cy + math.sin(ang) * (r - 90), P(WHITE, 22))
    cv.drawCircle(cx, cy, 44, P(WHITE))
    for i, at_ in enumerate((0.25, 0.75, 1.25)):
        k2 = pop(c.lt, at_)
        if k2 > 0:
            cv.save()
            cv.translate(1330 + i * 190, 330)
            cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
            cv.drawArc(skia.Rect.MakeLTRB(-62, -62, 62, 62), 30, 300, False, P(ICE, 14))
            poly(cv, [(44, -52), (86, -30), (42, -6)], P(ICE))
            cv.drawLine(-56, -56, 56, 56, P(RED, 16))
            cv.drawLine(-56, 56, 56, -56, P(RED, 16))
            cv.restore()
    punch(cv, 'SPIRAL DIVE  x3', 1520, 500, 78, pop(c.lt, 0.25))
    punch(cv, 'STILL CLIMBING', 1520, 620, 84, pop(c.lt, 1.5), AMBER)


def clock_30(cv, c):
    """Out cold: a stopwatch runs past half an hour."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B24')), (1, h('03050F'))])
    Wd.particles(cv, W, H, c.t, 60, 0x55CFEFFF, 9, size=(2, 5), drift=(-30, 50), wobble=20)
    cx, cy, r = 700, 460, 310
    cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 50, cy - r - 100, 100, 90), 16, 16, P(h('8A90A6')))
    cv.drawCircle(cx, cy, r + 34, P(h('8A90A6')))
    cv.drawCircle(cx, cy, r, P(h('F4EEDF')))
    mins = lerp(0, 34, ease(c.k * 1.15))
    sweep = min(360, mins / 30 * 360)
    cv.drawArc(skia.Rect.MakeLTRB(cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30), -90, sweep, True, P(0x55E5392F))
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = r - (60 if i % 5 == 0 else 30)
        cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (r - 12), cy + math.sin(a) * (r - 12), P(INK, 10 if i % 5 == 0 else 5))
    a = math.radians(mins / 30 * 360 - 90)
    cv.drawLine(cx, cy, cx + math.cos(a) * (r - 80), cy + math.sin(a) * (r - 80), P(RED, 18))
    cv.drawCircle(cx, cy, 30, P(INK))
    k2 = pop(c.lt, 0.66 * c.d)
    Wd.text_card(cv, 'OUT COLD', 1400, 330, 96, WHITE, BLACK)
    cv.save()
    cv.translate(1400, 520)
    cv.scale(1.4 - 0.4 * k2 if k2 > 0 else 1, 1.4 - 0.4 * k2 if k2 > 0 else 1)
    Wd.text_card(cv, '30+ MIN' if k2 > 0 else f'{int(min(mins, 29)):02d} MIN', 0, 0, 170, AMBER, BLACK)
    cv.restore()


def memorial(cv, c, lines):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A0F1E')), (1, h('04060C'))])
    Wd.particles(cv, W, H, c.t, 60, 0x44FFFFFF, 3, size=(2, 5), drift=(14, 46), wobble=18)
    s = 1.0 + 0.06 * c.k
    cv.save()
    cv.translate(960, 440)
    cv.scale(s, s)
    a = pop(c.lt, 0.0, 0.35)
    cv.drawLine(-lerp(0, 430, a), -230, lerp(0, 430, a), -230, P(WHITE, 4, 0.7))
    for txt, y, size, al, wt in lines:
        Wd.text_card(cv, txt, 0, y, size, Wd.alpha(WHITE, al * a), None, weight=wt)
    cv.drawLine(-lerp(0, 430, a), 250, lerp(0, 430, a), 250, P(WHITE, 4, 0.7))
    cv.restore()


def he_card(cv, c):
    """Who he was. No jokes, no effects."""
    memorial(cv, c, (('HE ZHONGPIN, 42', -60, 120, 1.0, 900), ('CHINESE PARAGLIDING TEAM', 60, 52, 0.75, 600),
                     ('MORE THAN TEN YEARS OF FLYING', 140, 52, 0.75, 600)))


def in_memory(cv, c):
    """The pilot who did not come back. No jokes, no effects."""
    memorial(cv, c, (('IN MEMORY OF', -120, 56, 0.75, 600), ('HE ZHONGPIN', 30, 132, 1.0, 900), ('PARAGLIDER PILOT, CHINA', 120, 46, 0.75, 600),
                     ('14 FEBRUARY 2007', 190, 46, 0.75, 600)))


def board_true(cv, c):
    chart(cv, c.t)
    taped(cv, 600, 440, 820, 700, 2)
    cv.save()
    cv.translate(600, 440)
    cv.rotate(2)
    photo(cv, 'ewa', 0, 10, 750, 600, (0.5, 0.2))
    cv.restore()
    stamp(cv, 'TRUE', 640, 560, -14, 210, pop(c.lt, 0.28, 0.12), GREEN)
    card(cv, 'ALMOST 10 KM UP', 1420, 240, 700, 160, -4, 62, pop(c.lt, 0.45))
    card(cv, 'OUT COLD 30+ MIN', 1450, 450, 700, 160, 3, 62, pop(c.lt, 0.6), h('BFE0EC'))
    card(cv, 'LANDED IT HERSELF', 1420, 660, 720, 160, -3, 62, pop(c.lt, 0.75), h('BFEFC8'))


# ------------------------------------------------------------------ flat inserts (new for the full case file)
def calendar(cv, c):
    """Ten days before the world championships."""
    chart(cv, c.t, 960, 900)

    def leaf_(x, y, day, sub, k, col):
        if k <= 0:
            return
        cv.save()
        cv.translate(x, y)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-232, -238, 480, 500), 24, 24, P(0x77000000))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-240, -250, 480, 500), 24, 24, P(CREAM))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-240, -250, 480, 130), 24, 24, P(col))
        Wd.text_card(cv, 'FEBRUARY 2007', 0, -165, 52, WHITE, None)
        Wd.text_card(cv, day, 0, 100, 260, INK, None)
        Wd.text_card(cv, sub, 0, 200, 36, col, None)
        for sx in (-120, 120):
            cv.drawRoundRect(skia.Rect.MakeXYWH(sx - 14, -290, 28, 80), 12, 12, P(h('8A90A6')))
        cv.restore()
    leaf_(520, 440, '14', 'WARM-UP FLIGHT', pop(c.lt, 0.0, 0.2), h('2E6AB8'))
    k2 = pop(c.lt, 0.9)
    leaf_(1400, 440, '24', 'WORLD CHAMPIONSHIPS', k2, h('B02A20'))
    if k2 > 0:
        x1 = lerp(800, 1120, k2)
        cv.drawLine(800, 440, x1, 440, P(AMBER, 18))
        poly(cv, [(x1, 400), (x1 + 50, 440), (x1, 480)], P(AMBER))
        Wd.text_card(cv, '10 DAYS', 960, 390, 70, AMBER, BLACK)
    punch(cv, '100+ PILOTS', 960, 800, 96, pop(c.lt, 0.72 * c.d))


def route(cv, c):
    """The flight on Rook's chart. prm mode: place | north | land. North is to the right."""
    mode = c.prm.get('mode', 'place')
    chart(cv, c.t, 1560, 330)
    a, b = (330, 620), (1560, 330)
    cv.save()
    cv.translate(1730, 850)
    cv.drawCircle(0, 0, 74, P(0xCC0B1020))
    cv.drawCircle(0, 0, 74, P(CREAM, 6))
    poly(cv, [(-34, -24), (50, 0), (-34, 24), (-14, 0)], P(ORANGE))
    Wd.text_card(cv, 'N', 96, 22, 60, CREAM, None)
    cv.restore()
    poly(cv, [(a[0] - 150, a[1] + 40), (a[0] - 30, a[1] - 150), (a[0] + 50, a[1] - 60), (a[0] + 110, a[1] - 110), (a[0] + 210, a[1] + 40)], P(h('3F6A4A')))
    poly(cv, [(a[0] - 60, a[1] - 100), (a[0] - 30, a[1] - 150), (a[0] + 6, a[1] - 108)], P(h('5E8A62')))
    cv.drawCircle(a[0], a[1], 22, P(ORANGE))
    cv.drawCircle(a[0], a[1], 22, P(BLACK, 6))
    Wd.text_card(cv, 'MOUNT BORAH', a[0] + 30, a[1] + 110, 60, WHITE, BLACK)
    if mode == 'place':
        punch(cv, 'MANILLA', 1080, 300, 150, pop(c.lt, 0.15), AMBER)
        punch(cv, 'NEW SOUTH WALES, AUSTRALIA', 1080, 400, 62, pop(c.lt, 0.4))
        punch(cv, 'FEBRUARY 2007', 1080, 500, 62, pop(c.lt, 0.6))
        for i in range(5):
            glider_icon(cv, a[0] + 240 + i * 120 + 14 * math.sin(c.t * 2 + i), a[1] - 20 - 46 * (i % 2) + 10 * math.sin(c.t * 3 + i), 0.5, WHITE, 5 * math.sin(c.t * 2 + i))
        return
    kk = ease(c.k * 1.2) if mode == 'north' else 1.0
    end = (lerp(a[0], b[0], kk * (0.55 if mode == 'north' else 1.0)), lerp(a[1], b[1], kk * (0.55 if mode == 'north' else 1.0)))
    n = 26
    for i in range(n):
        u0, u1 = i / n, (i + 0.55) / n
        cv.drawLine(lerp(a[0], end[0], u0), lerp(a[1], end[1], u0), lerp(a[0], end[0], u1), lerp(a[1], end[1], u1), P(AMBER, 12))
    if mode == 'north':
        for i in range(6):
            x = 140 + ((c.t * 420 + i * 290) % 1500)
            y = 760 + (i % 3) * 40 - x * 0.05
            cv.drawLine(x, y, x + 150, y - 8, P(0x99CFEFFF, 10))
            poly(cv, [(x + 150, y - 30), (x + 190, y - 10), (x + 150, y + 14)], P(0x99CFEFFF))
        Wd.text_card(cv, 'WIND FROM THE SOUTH', 560, 900 - 60, 56, ICE, BLACK)
        for i in range(4):
            glider_icon(cv, end[0] - 60 - i * 110, end[1] + 14 + 50 * (i % 2) + i * 26, 0.5, WHITE, 4 * math.sin(c.t * 2 + i))
        glider_icon(cv, end[0], end[1] - 30, 0.9, AMBER, 5 * math.sin(c.t * 3))
        storm_icon(cv, 1330, 250, 0.8 + 0.25 * kk, c.t)
        storm_icon(cv, lerp(1640, 1480, kk), 300, 0.7 + 0.25 * kk, c.t + 0.4)
        punch(cv, 'ABOUT 2 HOURS IN', 760, 200, 72, pop(c.lt, 0.5 * c.d))
    else:
        storm_icon(cv, 900, 200, 0.9, c.t, h('39445C'))
        k2 = pop(c.lt, 0.3)
        if k2 > 0:
            cv.drawLine(b[0] - 34, b[1] - 34, b[0] + 34, b[1] + 34, P(RED, 18))
            cv.drawLine(b[0] - 34, b[1] + 34, b[0] + 34, b[1] - 34, P(RED, 18))
        punch(cv, 'LANDED', b[0] - 30, b[1] + 130, 84, k2)
        punch(cv, 'ABOUT 60 KM', 1120, 650, 140, pop(c.lt, 0.45 * c.d), AMBER)
        punch(cv, 'ABOUT 3.5 HOURS IN THE AIR', 1120, 760, 62, pop(c.lt, 0.7 * c.d))


def forecast(cv, c):
    """The day's forecast as the pilots heard it: fine now, thunderstorms possible later."""
    chart(cv, c.t, 300, 900)
    taped(cv, 960, 440, 1560, 700, -1)
    cv.save()
    cv.translate(960, 440)
    cv.rotate(-1)
    cv.drawRect(skia.Rect.MakeXYWH(-780, -350, 1560, 130), P(h('20242B')))
    Wd.text_card(cv, "TODAY'S FORECAST", 0, -262, 80, AMBER, None)
    cv.drawLine(0, -200, 0, 320, P(0x55000000, 6))
    cv.save()
    cv.translate(-400, -20)
    cv.rotate(c.t * 20)
    for i in range(8):
        a = i * math.pi / 4
        cv.drawLine(math.cos(a) * 120, math.sin(a) * 120, math.cos(a) * 170, math.sin(a) * 170, P(AMBER, 18))
    cv.drawCircle(0, 0, 100, P(AMBER))
    cv.restore()
    for dx, dy, r in ((-250, 60, 44), (-200, 40, 56), (-150, 64, 40)):
        cv.drawCircle(dx + 12 * math.sin(c.t), dy, r, P(WHITE))
    Wd.text_card(cv, 'NOW', -400, 200, 64, h('2E6AB8'), None)
    Wd.text_card(cv, 'SUNNY, SMALL CLOUDS', -400, 280, 56, INK, None)
    k2 = pop(c.lt, 0.5 * c.d)
    if k2 > 0:
        cv.save()
        cv.translate(400, -70)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        storm_icon(cv, 0, 0, 1.0, c.t)
        cv.restore()
        Wd.text_card(cv, 'LATER', 400, 200, 64, h('B02A20'), None)
        Wd.text_card(cv, 'STORMS POSSIBLE', 400, 280, 56, INK, None)
    cv.restore()


def rate(cv, c):
    """Climb rate: good lift against what her instruments logged."""
    night(cv, c.t, '101626')
    base = 800
    cv.drawLine(260, base, 1660, base, P(0x66FFFFFF, 6))
    k1 = pop(c.lt, 0.0, 0.3)
    h1 = 96 * k1
    cv.drawRoundRect(skia.Rect.MakeLTRB(500, base - h1, 720, base), 12, 12, P(GREEN))
    Wd.text_card(cv, 'GOOD LIFT', 610, base - h1 - 110, 60, WHITE, BLACK)
    Wd.text_card(cv, '3-4 m/s', 610, base - h1 - 30, 84, GREEN, BLACK)
    k2 = ease((c.lt - 0.45 * c.d) / 0.5)
    if k2 > 0:
        h2 = 560 * k2
        j = 4 * math.sin(c.t * 50)
        cv.drawRoundRect(skia.Rect.MakeLTRB(1180 + j, base - h2, 1400 + j, base), 12, 12, P(RED))
        poly(cv, [(1130 + j, base - h2), (1290 + j, base - h2 - 120), (1450 + j, base - h2)], P(RED))
        for i in range(4):
            y = base - ((c.t * 900 + i * 150) % max(60, h2))
            cv.drawLine(1230, y + 40, 1290, y, P(0x66FFFFFF, 12))
            cv.drawLine(1290, y, 1350, y + 40, P(0x66FFFFFF, 12))
        if k2 > 0.9:
            Wd.text_card(cv, 'HER CLIMB', 1640, 330, 64, WHITE, BLACK)
            Wd.text_card(cv, 'ABOUT', 1640, 420, 64, WHITE, BLACK)
            Wd.text_card(cv, '20 m/s', 1640, 540, 120, AMBER, BLACK)
    glider_icon(cv, 960, 300 - 40 * math.sin(c.t * 4), 1.1, AMBER, 6 * math.sin(c.t * 3))


def cold(cv, c):
    """Around forty below, and air too thin to stay awake."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B24')), (1, h('12305A'))])
    Wd.particles(cv, W, H, c.t, 90, Wd.alpha(ICE, 0.5), 11, size=(2, 7), drift=(-40, 60), wobble=24, twinkle=True)
    x, top, bot = 520, 130, 700
    cv.drawRoundRect(skia.Rect.MakeLTRB(x - 44, top, x + 44, bot), 44, 44, P(h('E8ECF4')))
    cv.drawCircle(x, bot + 30, 84, P(h('E8ECF4')))
    lvl = lerp(top + 60, bot - 40, ease(c.k * 1.6))
    cv.drawRoundRect(skia.Rect.MakeLTRB(x - 20, lvl, x + 20, bot + 10), 20, 20, P(h('3A8AD8')))
    cv.drawCircle(x, bot + 30, 58, P(h('3A8AD8')))
    for i in range(8):
        y = top + 60 + i * 72
        cv.drawLine(x + 60, y, x + 110, y, P(WHITE, 6))
    Wd.text_card(cv, '0', x + 150, top + 80, 50, WHITE, None)
    Wd.text_card(cv, '-40', x + 180, bot - 20, 50, ICE, None)
    k2 = pop(c.lt, 0.3 * c.d)
    punch(cv, 'AROUND', 1230, 260, 80, k2)
    punch(cv, '-40°', 1230, 450, 230, k2, ICE)
    punch(cv, 'AND THIN AIR', 1230, 620, 96, pop(c.lt, 0.62 * c.d), AMBER)


def o2(cv, c):
    """What doctors said afterwards: unconscious, her body needed less oxygen."""
    night(cv, c.t, '0B1626', '05070D', 50)
    Wd.text_card(cv, 'OXYGEN HER BODY NEEDS', 960, 170, 84, WHITE, BLACK)
    for i, (lab, frac, col, at_) in enumerate((('AWAKE', 1.0, AMBER, 0.0), ('OUT COLD', 0.42, GREEN, 0.45 * c.d))):
        y = 340 + i * 230
        k = ease((c.lt - at_) / 0.5)
        cv.drawRoundRect(skia.Rect.MakeXYWH(640, y - 60, 1000, 120), 20, 20, P(h('1A2236')))
        if k > 0:
            cv.drawRoundRect(skia.Rect.MakeXYWH(640, y - 60, 1000 * frac * k, 120), 20, 20, P(col))
            Wd.text_card(cv, lab, 400, y + 24, 70, col, BLACK)
    punch(cv, 'LESS', 1340, 595, 84, pop(c.lt, 0.45 * c.d + 0.5), GREEN)
    Wd.text_card(cv, 'WHAT DOCTORS SAID AFTERWARDS', 960, 770, 48, 0xAAFFFFFF, None, weight=600)


def gps(cv, c):
    """She scratches the ice off the GPS: still almost seven thousand metres up (the last digits stay iced over)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16203A')), (1, h('080C18'))])
    Wd.particles(cv, W, H, c.t, 70, Wd.alpha(ICE, 0.4), 11, size=(2, 6), drift=(-26, 40), wobble=24, twinkle=True)
    cv.save()
    device(cv, c, 700, 440)
    Wd.text_card(cv, 'GPS  ALTITUDE', 0, -280, 62, h('6FE08A'), None)
    Wd.text_card(cv, '6,9', -150, -40, 230, AMBER, None)
    Wd.text_card(cv, 'm', 300, -40, 110, AMBER, None)
    for i in range(12):
        cv.drawRect(skia.Rect.MakeXYWH(-330 + i * 56, 200 - (20 + i * 9), 40, 20 + i * 9), P(h('6FE08A') if i < 8 else h('1E3A26')))
    for i in range(16):
        x, y = -330 + (i % 4) * 190, -330 + (i // 4) * 150
        keep = (i % 4 >= 2 and i // 4 == 1)
        s = 1.0 if keep else 1.0 - ease((c.k * 1.5 - ((i * 7) % 16) / 16 * 0.8) / 0.25)
        if s > 0.02:
            cv.save()
            cv.translate(x + 60, y + 60)
            cv.rotate(i * 23)
            poly(cv, [(-110 * s, -40 * s), (-30 * s, -100 * s), (90 * s, -70 * s), (120 * s, 30 * s), (20 * s, 100 * s), (-90 * s, 70 * s)], P(Wd.alpha(ICE, 0.92)))
            cv.restore()
    cv.restore()
    punch(cv, 'STILL ALMOST', 1420, 330, 84, pop(c.lt, 0.45 * c.d))
    punch(cv, '7,000 m', 1420, 500, 170, pop(c.lt, 0.45 * c.d), AMBER)
    punch(cv, 'UP', 1420, 640, 120, pop(c.lt, 0.45 * c.d + 0.25))


def lotto(cv, c):
    """The organiser's odds: winning the lottery ten times in a row."""
    chart(cv, c.t, 960, 900)
    for i in range(10):
        k = pop(c.lt, 0.1 + i * 0.16 * min(1.0, c.d / 2.2))
        if k <= 0:
            continue
        x, y = 330 + (i % 5) * 315, 250 + (i // 5) * 290
        cv.save()
        cv.translate(x, y)
        cv.rotate((-6, 4, -3, 5, -4)[i % 5])
        cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-128, -98, 270, 220), 14, 14, P(0x77000000))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-135, -110, 270, 220), 14, 14, P(CREAM))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-135, -110, 270, 60), 14, 14, P(ORANGE))
        Wd.text_card(cv, 'LOTTO', 0, -66, 40, WHITE, None)
        for j in range(4):
            cv.drawCircle(-84 + j * 56, 6, 22, P(h('2E6AB8')))
        Wd.text_card(cv, 'WIN', 0, 92, 60, h('B02A20'), None)
        cv.restore()
    punch(cv, '10 TIMES IN A ROW', 960, 760, 110, pop(c.lt, 0.72 * c.d), AMBER)


def film(cv, c):
    """2010: the documentary."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('14182A')), (1, h('06070E'))])
    for y in (70, 770):
        cv.drawRect(skia.Rect.MakeXYWH(0, y, W, 110), P(h('20242B')))
        for i in range(-1, 18):
            x = i * 120 - (c.t * 240) % 120
            cv.drawRoundRect(skia.Rect.MakeXYWH(x + 30, y + 28, 60, 54), 10, 10, P(h('0A0C14')))
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(960, 480)
    cv.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-640, -150, 1280, 400), 20, 20, P(h('20242B')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-640, -150, 1280, 400), 20, 20, P(CREAM, 8))
    cv.save()
    cv.translate(-640, -150)
    cv.rotate(-lerp(18, 0, ease(c.lt / 0.5)))
    cv.drawRect(skia.Rect.MakeXYWH(0, -90, 1280, 90), P(CREAM))
    for i in range(8):
        poly(cv, [(i * 160, -90), (i * 160 + 80, -90), (i * 160 + 40, 0), (i * 160 - 40, 0)], P(INK))
    cv.restore()
    Wd.text_card(cv, 'MIRACLE IN THE STORM', 0, 20, 96, AMBER, None)
    Wd.text_card(cv, 'DOCUMENTARY, 2010', 0, 150, 70, WHITE, None)
    cv.restore()


SHOTS = {f.__name__: f for f in (alt_spin, everest_bar, board_storm, trophy, vario, clock_30, he_card, in_memory, board_true, calendar, route,
                                 forecast, rate, cold, o2, gps, lotto, film)}


# ------------------------------------------------------------------ overlays on 3D shots
def sleet(cv, c):
    Wd.rain(cv, W, H, c.t, density=170, c=0x55DFF4FF, slant=0.45, speed=2700, length=70)


def crystals(cv, c):
    Wd.particles(cv, W, H, c.t, 70, Wd.alpha(ICE, 0.35), 11, size=(2, 6), drift=(-26, 40), wobble=24, twinkle=True)


def arrows(cv, c):
    sleet(cv, c)
    for i in range(4):
        y = 900 - ((c.t * 900 + i * 240) % 900)
        a = 1 - abs(y - 450) / 430
        if a > 0:
            for x in (110, 1810):
                cv.drawLine(x - 60, y + 60, x, y, P(AMBER, 16, a))
                cv.drawLine(x, y, x + 60, y + 60, P(AMBER, 16, a))


def gusts(cv, c):
    for i in range(9):
        y = 130 + i * 90 + 30 * math.sin(i * 2.1)
        x = ((c.t * 1700 + i * 470) % (W + 800)) - 400
        cv.drawLine(x, y, x + 300, y - 12, P(0x44FFFFFF, 6))


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0x55FFE0C0, 5, size=(2, 5), drift=(40, -30), wobble=30, twinkle=True)


def label(text, x=420, y=200, size=92, at=0.3, col='FFFFFF', ang=-3):
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
        Wd.text_card(cv, 'CASE 006  CLOSED', 0, 90, 54, WHITE, BLACK)
        cv.restore()


OVER = dict(
    suck_up=sleet, ewa_fight=sleet, blackout_cu=sleet, cloud_mouth=both(sleet, pick(label('CLOUD SUCK', 430, 210, 110, 0.4, 'FFB000'), None)),
    spiral=arrows, rook_brolly=arrows, rise_tower=arrows, hail=sleet, bolt=sleet, radio_ewa=sleet,
    rook_ice=crystals, top_out=crystals, slump_wide=crystals, ghost_fly=crystals, rook_watch=crystals, eyes_open=crystals, ice_hands=crystals,
    wing_ice=crystals, gps_scratch=crystals,
    rook_sock=gusts, storm_build=gusts, merge_rook=gusts, two_clouds=gusts, leader=gusts,
    dusk_hill=motes, rook_hat=motes, storm_far=motes,
    doctors=pick(label('ONE HOUR IN HOSPITAL', 560, 190, 84, 0.4, 'FFFFFF'), None),
    stitch=label('9,946 m', 1500, 230, 130, 1.6, 'FFB000'),
    school=label('BAVARIA, TODAY', 470, 190, 92, 0.3, 'FFFFFF'),
    signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (the glider yanked up inside the storm, Rook on his blown-out umbrella) + a hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('26304A'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(620, 0), (1000, 0)], [0x00000000, 0xC8000000])))
    Wd.text_card(cv, 'SUCKED UP', 960, 250, 96, WHITE, BLACK)
    Wd.text_card(cv, '10 KM', 960, 440, 180, h('FFB000'), BLACK)
    for i in range(3):
        y = 530 + i * 44
        cv.drawLine(960 - 70, y + 34, 960, y, P(h('FFB000'), 16))
        cv.drawLine(960, y, 960 + 70, y + 34, P(h('FFB000'), 16))
