"""Case 006 - Ewa Wisnierska. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(Rook's weather-chart case board, the flight computer, the Everest line, the climb gauge, the stopwatch, the
memorial card) and the 2D overlays drawn on top of 3D shots (sleet, ice crystals, climb arrows, the sign-off)."""
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
ORANGE, AMBER, RED, CREAM, ICE = h('FF7A1A'), h('FFB000'), h('E5392F'), h('F4EEDF'), h('CFEFFF')


def pop(lt, t0, d=0.14):
    return max(0.0, min(1.0, (lt - t0) / d))


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


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


def chart(cv, t):
    """Rook's case board for this one: a weather chart with pressure rings closing on a storm."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10213A')), (1, h('081220'))])
    for i in range(1, 9):
        cv.drawLine(i * 120, 0, i * 120, H, P(0x14FFFFFF, 2))
    for j in range(1, 16):
        cv.drawLine(0, j * 120, W, j * 120, P(0x14FFFFFF, 2))
    for i in range(7):
        r = 130 + i * 120 + 10 * math.sin(t * 1.3 + i)
        cv.drawOval(skia.Rect.MakeLTRB(760 - r * 1.25, 1500 - r, 760 + r * 1.25, 1500 + r), P(0x2E8FC8FF, 5))
    for i in range(9):
        x, y = 90 + (i * 263) % 900, 150 + (i * 397) % 1500
        a = 0.6 + i
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


def card(cv, text, x, y, w_, h_, ang, size, k, col=h('FFD866')):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    taped(cv, 0, 0, w_, h_, ang, col)
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.42, size, INK, None)
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


def glider_icon(cv, x, y, s, col=0xFFFFFFFF, ang=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    cv.drawArc(skia.Rect.MakeLTRB(-70, -60, 70, 40), 200, 140, False, P(col, 16))
    for dx in (-52, -20, 20, 52):
        cv.drawLine(dx, -44 + abs(dx) * 0.3, 0, 46, P(col, 3))
    cv.drawCircle(0, 54, 11, P(col))
    cv.restore()


# ------------------------------------------------------------------ flat inserts
def alt_spin(cv, c):
    """Her flight computer: the altitude digits race upward (they never settle on an exact figure)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A0F1C')), (1, h('05070D'))])
    Wd.rain(cv, W, H, c.t, density=70, c=0x33CFE6FF, slant=0.45, speed=2600, length=70)
    j = 5 * math.sin(c.t * 40)
    cv.save()
    cv.translate(540 + j, 760)
    cv.rotate(-4 + 1.5 * math.sin(c.t * 9))
    body = skia.Rect.MakeLTRB(-420, -440, 420, 440)
    cv.drawRoundRect(body.makeOffset(12, 18), 60, 60, P(0x99000000))
    cv.drawRoundRect(body, 60, 60, P(h('2A2F3A')))
    cv.drawRoundRect(body, 60, 60, P(ORANGE, 10))
    cv.drawRoundRect(skia.Rect.MakeLTRB(-360, -370, 360, 250), 26, 26, P(h('0E1A12')))
    Wd.text_card(cv, 'ALTITUDE', 0, -280, 62, h('6FE08A'), None)
    v = int(lerp(800, 9900, ease(c.k * 1.1)) / 7) * 7 + int(c.t * 60) % 7
    Wd.text_card(cv, f'{v:,}', -40, -40, 230, AMBER, None)
    Wd.text_card(cv, 'm', 300, -40, 110, AMBER, None)
    for i in range(12):
        on = i < 2 + 10 * c.k
        cv.drawRect(skia.Rect.MakeXYWH(-330 + i * 56, 200 - (20 + i * 9), 40, 20 + i * 9), P(h('6FE08A') if on else h('1E3A26')))
    for i in range(3):
        y = 60 - ((c.t * 420 + i * 60) % 180)
        cv.drawLine(-300, y + 40, -270, y, P(AMBER, 12))
        cv.drawLine(-270, y, -240, y + 40, P(AMBER, 12))
    for i in range(3):
        cv.drawCircle(-200 + i * 200, 345, 44, P(h('1A1E28')))
    cv.restore()


def everest_bar(cv, c):
    """A glider climbs past the summit line of Everest."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B24')), (0.6, h('1C2A5A')), (1, h('3A4A80'))])
    Wd.particles(cv, W, H, c.t * 0.3, 40, 0x88FFFFFF, 5, size=(2, 4), drift=(0, 0), wobble=0, twinkle=True)
    top = 900
    for pts, col in ((((60, 1920), (330, 1180), (520, 1500), (700, 1920)), h('2A3558')),
                     (((300, 1920), (640, top), (1020, 1920)), h('3F4C78')),
                     (((560, 1070), (640, top), (735, 1100), (690, 1060), (640, 1120), (600, 1040)), 0xFFE8EEF8)):
        pth = skia.Path()
        pth.moveTo(*pts[0])
        for p_ in pts[1:]:
            pth.lineTo(*p_)
        pth.close()
        cv.drawPath(pth, P(col))
    for x in range(40, W - 40, 60):
        cv.drawLine(x, top, x + 34, top, P(0xFFFFFFFF, 6))
    Wd.text_card(cv, 'EVEREST  8,849 m', 300, top - 30, 54, 0xFFFFFFFF, 0xFF000000)
    gy = lerp(1210, 480, ease(c.k * 1.25))
    cv.drawLine(840, 1290, 840, gy + 90, P(AMBER, 8, 0.7))
    glider_icon(cv, 840 + 10 * math.sin(c.t * 5), gy, 1.7, AMBER, 6 * math.sin(c.t * 4))
    k2 = pop(c.lt, 0.62)
    if k2 > 0 and gy < top:
        cv.save()
        cv.translate(470, 560)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        Wd.text_card(cv, 'ALMOST', 0, 0, 96, 0xFFFFFFFF, 0xFF000000)
        Wd.text_card(cv, '10,000 m', 0, 150, 150, AMBER, 0xFF000000)
        cv.restore()


def board_storm(cv, c):
    chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(520, 640)
    cv.scale(s, s)
    taped(cv, 0, 0, 760, 640, -3)
    cv.rotate(-3)
    photo(cv, 'storm', 0, 10, 690, 540, (0.5, 0.3))
    cv.restore()
    card(cv, '10 KM UP', 310, 1080, 420, 190, -5, 78, pop(c.lt, 0.3))
    card(cv, 'OUT COLD', 760, 1140, 420, 190, 4, 78, pop(c.lt, 0.5), h('BFE0EC'))
    stamp(cv, 'NO CHANCE', 540, 640, -12, 150, pop(c.lt, 0.72, 0.12))


def trophy(cv, c):
    """Who she is: a competition pilot."""
    chart(cv, c.t)
    k = pop(c.lt, 0.0, 0.2)
    cv.save()
    cv.translate(540, 700)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    taped(cv, 0, 0, 860, 900, 2)
    cv.rotate(2)
    cv.drawRect(skia.Rect.MakeXYWH(-430, -450, 860, 150), P(h('20242B')))
    Wd.text_card(cv, 'PILOT FILE', 0, -350, 84, AMBER, None)
    cv.save()
    cv.translate(-250, -70)
    cv.rotate(8 * math.sin(c.t * 3))
    pth = skia.Path()
    for x_, y_ in ((-90, -110), (90, -110), (62, 30), (-62, 30)):
        pth.lineTo(x_, y_) if pth.countPoints() else pth.moveTo(x_, y_)
    pth.close()
    cv.drawPath(pth, P(AMBER))
    cv.drawArc(skia.Rect.MakeLTRB(-140, -100, -50, 0), 90, 180, False, P(AMBER, 16))
    cv.drawArc(skia.Rect.MakeLTRB(50, -100, 140, 0), 270, 180, False, P(AMBER, 16))
    cv.drawRect(skia.Rect.MakeXYWH(-16, 30, 32, 60), P(AMBER))
    cv.drawRect(skia.Rect.MakeXYWH(-80, 90, 160, 34), P(h('8A6A2A')))
    cv.restore()
    Wd.text_card(cv, 'GERMAN', 130, -110, 96, INK, None)
    Wd.text_card(cv, 'TEAM', 130, 0, 96, INK, None)
    k2 = pop(c.lt, 0.3)
    if k2 > 0:
        Wd.text_card(cv, '2005 WORLD CUP WINNER', 0, 190, 58, h('B02A20'), None)
    k3 = pop(c.lt, 0.55)
    if k3 > 0:
        cv.drawRoundRect(skia.Rect.MakeXYWH(-370, 250, 740, 130), 16, 16, P(h('20242B')))
        Wd.text_card(cv, 'TRAINING: WORLDS 2007', 0, 337, 54, 0xFFFFFFFF, None)
    cv.restore()


def vario(cv, c):
    """Her climb gauge: pinned on UP."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('101626')), (1, h('05070D'))])
    Wd.rain(cv, W, H, c.t, density=60, c=0x2ECFE6FF, slant=0.45, speed=2600, length=70)
    cx, cy, r = 540, 800, 400
    cv.drawCircle(cx + 10, cy + 16, r + 40, P(0x88000000))
    cv.drawCircle(cx, cy, r + 40, P(h('2A2F3A')))
    cv.drawCircle(cx, cy, r + 40, P(ORANGE, 10))
    cv.drawCircle(cx, cy, r, P(h('0B0F18')))
    for i in range(25):
        a = math.radians(180 + (i - 12) * 11)
        up = i < 12
        col = Wd.mix(h('3DDC84'), RED, (12 - i) / 12) if up else h('5A6478')
        r0 = r - (70 if i % 4 == 0 else 44)
        cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (r - 14), cy + math.sin(a) * (r - 14), P(col, 16))
    Wd.text_card(cv, 'UP', cx + 20, cy - 190, 120, RED if (c.t * 6) % 1 < 0.6 else AMBER, None)
    Wd.text_card(cv, 'DOWN', cx + 20, cy + 270, 70, h('5A6478'), None)
    Wd.text_card(cv, 'CLIMB', cx + 150, cy + 30, 54, 0x99FFFFFF, None)
    ang = math.radians(180 + lerp(100, -128, ease(c.lt / 0.3)) + (3 * math.sin(c.t * 50) if c.lt > 0.3 else 0))
    cv.drawLine(cx, cy, cx + math.cos(ang) * (r - 90), cy + math.sin(ang) * (r - 90), P(0xFFFFFFFF, 22))
    cv.drawCircle(cx, cy, 44, P(0xFFFFFFFF))
    glider_icon(cv, 190, 300 - 60 * math.sin(c.t * 4), 0.9, AMBER)


def clock_30(cv, c):
    """Out cold: a stopwatch runs past half an hour."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B24')), (1, h('03050F'))])
    Wd.particles(cv, W, H, c.t, 40, 0x55CFEFFF, 9, size=(2, 5), drift=(-30, 50), wobble=20)
    cx, cy, r = 540, 760, 380
    cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 50, cy - r - 110, 100, 90), 16, 16, P(h('8A90A6')))
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
    k2 = pop(c.lt, 0.66)
    cv.save()
    cv.translate(540, 1230)
    cv.scale(1.4 - 0.4 * k2 if k2 > 0 else 1, 1.4 - 0.4 * k2 if k2 > 0 else 1)
    Wd.text_card(cv, '30+ MIN' if k2 > 0 else f'{int(min(mins, 29)):02d} MIN', 0, 0, 150, AMBER, 0xFF000000)
    cv.restore()


def in_memory(cv, c):
    """The pilot who did not come back. No jokes, no effects."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0A0F1E')), (1, h('04060C'))])
    Wd.particles(cv, W, H, c.t, 26, 0x33FFFFFF, 3, size=(2, 4), drift=(6, 22), wobble=14)
    s = 1.0 + 0.05 * c.k
    cv.save()
    cv.translate(540, 760)
    cv.scale(s, s)
    a = pop(c.lt, 0.0, 0.3)
    cv.drawLine(-lerp(0, 300, a), -200, lerp(0, 300, a), -200, P(0xFFFFFFFF, 4, 0.7))
    Wd.text_card(cv, 'IN MEMORY OF', 0, -90, 56, Wd.alpha(0xFFFFFFFF, 0.75 * a), None, weight=600)
    Wd.text_card(cv, 'HE ZHONGPIN', 0, 60, 122, Wd.alpha(0xFFFFFFFF, a), None)
    Wd.text_card(cv, 'PARAGLIDER PILOT, CHINA', 0, 170, 46, Wd.alpha(0xFFFFFFFF, 0.75 * a), None, weight=600)
    Wd.text_card(cv, '14 FEBRUARY 2007', 0, 250, 46, Wd.alpha(0xFFFFFFFF, 0.75 * a), None, weight=600)
    cv.drawLine(-lerp(0, 300, a), 320, lerp(0, 300, a), 320, P(0xFFFFFFFF, 4, 0.7))
    cv.restore()


def board_true(cv, c):
    chart(cv, c.t)
    taped(cv, 540, 680, 720, 800, 2)
    cv.save()
    cv.translate(540, 680)
    cv.rotate(2)
    photo(cv, 'ewa', 0, 10, 650, 700, (0.5, 0.1))
    cv.restore()
    stamp(cv, 'TRUE', 560, 800, -14, 200, pop(c.lt, 0.28, 0.12), h('3DDC84'))
    card(cv, 'FROSTBITE', 320, 1190, 440, 180, -5, 72, pop(c.lt, 0.55), h('BFE0EC'))
    card(cv, 'ALIVE', 790, 1170, 330, 180, 5, 84, pop(c.lt, 0.7))


SHOTS = {f.__name__: f for f in (alt_spin, everest_bar, board_storm, trophy, vario, clock_30, in_memory, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def sleet(cv, c):
    Wd.rain(cv, W, H, c.t, density=110, c=0x55DFF4FF, slant=0.45, speed=2700, length=70)


def crystals(cv, c):
    Wd.particles(cv, W, H, c.t, 44, Wd.alpha(ICE, 0.35), 11, size=(2, 6), drift=(-26, 40), wobble=24, twinkle=True)


def arrows(cv, c):
    sleet(cv, c)
    for i in range(4):
        y = 1250 - ((c.t * 900 + i * 260) % 1040)
        a = 1 - abs(y - 730) / 560
        if a > 0:
            cv.drawLine(70, y + 60, 130, y, P(AMBER, 16, a))
            cv.drawLine(130, y, 190, y + 60, P(AMBER, 16, a))


def gusts(cv, c):
    for i in range(7):
        y = 330 + i * 150 + 30 * math.sin(i * 2.1)
        x = ((c.t * 1500 + i * 370) % (W + 700)) - 350
        cv.drawLine(x, y, x + 260, y - 12, P(0x44FFFFFF, 6))


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 006  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(suck_up=sleet, ewa_fight=sleet, blackout_cu=sleet, cloud_mouth=sleet, spiral=arrows, rook_brolly=arrows, rise_tower=arrows,
            hail=sleet, bolt=sleet, rook_ice=crystals, top_out=crystals, slump_wide=crystals, ghost_fly=crystals, rook_watch=crystals,
            eyes_open=crystals, ice_hands=crystals, rook_sock=gusts, storm_build=gusts, signoff=closed)
