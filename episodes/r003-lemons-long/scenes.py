"""Case 003, full case file (16:9) - Chris Lemons. The story is filmed in 3D (world3d.py). This file holds the flat graphic
inserts (Rook's dive-chart wall, the map, the umbilical, the gauge, the drift, the oxygen cards, the disputed clock), the
overlays drawn on top of 3D shots, and the thumbnail."""
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
RED, AMB, WHITE = 'E5392F', 'FFB000', 'FFFFFF'


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) pinned to the wall as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('2E6A70')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def wall(cv, t):
    """Rook's case wall for this one: a sea-green dive chart with a depth scale down the left edge."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E3A3C')), (1, h('051A1E'))])
    for j in range(0, H + 1, 90):
        cv.drawLine(0, j, W, j, P(0x16FFFFFF, 2))
    for i in range(11):
        y = 110 + i * 84
        cv.drawLine(44, y, 120 if i % 5 == 0 else 88, y, P(h(AMB), 6))
    cv.drawLine(44, 110, 44, 950, P(h(AMB), 6))
    Wd.text_card(cv, '100 M', 170, 1000, 40, h(AMB), None)
    for i in range(9):
        x = 260 + i * 190
        y = (t * 60 + i * 290) % (H + 200)
        cv.drawCircle(x + 20 * math.sin(t * 2 + i), H - y, 9 + (i % 3) * 5, P(0x30BFF6FF, 4))
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, W - 14, H - 14), P(h('FF7A1A'), 8))


def pinned(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 26, 18, P(h(RED)))
    cv.drawCircle(-5, -h_ / 2 + 21, 6, P(0x88FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, ang, size, k, col='FFD866', h_=150):
    if k <= 0:
        return
    k = min(1, k)
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, h(col))
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.5, size, INK, None)
    cv.restore()


def pop(cv, text, x, y, size, k, col=AMB, ang=0):
    if k <= 0:
        return
    k = min(1, k)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(1.6 - 0.6 * k, 1.6 - 0.6 * k)
    Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
    cv.restore()


def after(c, at, dur=0.14):
    return (c.lt - at) / dur


def deepwater(cv, t, top='072A2C', bot='02090C'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    Wd.particles(cv, W, H, t, 60, Wd.alpha(h('BFF6FF'), 0.35), 4, size=(2, 6), drift=(-10, -50), wobble=22)


def gauge(cv, cx, cy, r, frac, t, label, danger=False):
    """A round pressure gauge. frac 1 = full, 0 = empty."""
    cv.drawCircle(cx, cy, r + 26, P(0xFF000000))
    cv.drawCircle(cx, cy, r + 14, P(h('C8CCD4')))
    cv.drawCircle(cx, cy, r, P(h('F4EEDF')))
    arc = skia.Rect.MakeLTRB(cx - r + 46, cy - r + 46, cx + r - 46, cy + r - 46)
    cv.drawArc(arc, 135, 62, False, P(h(RED), 44))
    cv.drawArc(arc, 197, 208, False, P(h('3DAA6A'), 44))
    for i in range(11):
        a = math.radians(135 + i * 27)
        cv.drawLine(cx + math.cos(a) * (r - 96), cy + math.sin(a) * (r - 96), cx + math.cos(a) * (r - 22), cy + math.sin(a) * (r - 22), P(INK, 10))
    a = math.radians(135 + 270 * max(0.0, min(1.0, frac)) + (2.5 * math.sin(t * 40) if danger else 0))
    cv.drawLine(cx - math.cos(a) * 50, cy - math.sin(a) * 50, cx + math.cos(a) * (r - 70), cy + math.sin(a) * (r - 70), P(h('FF7A1A'), 22))
    cv.drawCircle(cx, cy, 34, P(INK))
    Wd.text_card(cv, label, cx, cy + r * 0.56, 70, INK, None)


def bottles(cv, x, y, s, t):
    """Two bail-out cylinders, drawn flat."""
    for i in (-1, 1):
        cx = x + i * 62 * s
        cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 50 * s, y - 170 * s, 100 * s, 340 * s), 46 * s, 46 * s, P(h('D8D8D0')))
        cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 50 * s, y - 170 * s, 100 * s, 340 * s), 46 * s, 46 * s, P(0xFF000000, 8))
        cv.drawRect(skia.Rect.MakeXYWH(cx - 18 * s, y - 206 * s, 36 * s, 40 * s), P(h('FFC233')))
    cv.drawRect(skia.Rect.MakeXYWH(x - 130 * s, y - 30 * s, 260 * s, 46 * s), P(h('15181F')))


def gas_five(cv, c):
    """His bail-out bottles: about five minutes. On its second use (prm 'again') the needle is already falling."""
    again = c.prm.get('again')
    deepwater(cv, c.t, '051C20' if again else '072A2C')
    k = min(1, c.lt / 0.18)
    cv.save()
    cv.translate(620, 470)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    cv.translate(-620, -470)
    gauge(cv, 620, 470, 300, lerp(0.5, 0.3, c.k) if again else lerp(0.62, 0.5, c.k), c.t, 'GAS')
    cv.restore()
    bottles(cv, 1400, 330 if again else 300, 0.85, c.t)
    Wd.text_card(cv, 'EMERGENCY BOTTLES', 1400, 560, 54, 0xFFFFFFFF, 0xFF000000)
    pop(cv, 'ABOUT 5 MINUTES', 1400, 670, 84, after(c, 0.35))


def board_gas(cv, c):
    wall(cv, c.t)
    k = min(1, c.lt / 0.22)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    pinned(cv, 620, 440, 800 * s, 560 * s, -2.5)
    cv.save()
    cv.translate(620, 440)
    cv.rotate(-2.5)
    cv.scale(s, s)
    photo(cv, 'bell', 0, 20, 740, 450, (0.5, 0.35))
    cv.restore()
    card(cv, '5 MIN OF GAS', 1400, 250, 600, -4, 72, after(c, 0.3))
    card(cv, '30 MIN WAIT', 1440, 450, 580, 3, 72, after(c, 0.6), 'F4EEDF')
    pop(cv, 'NO CHANCE', 1380, 660, 116, after(c, 0.95, 0.12), RED, -5)


def map_north(cv, c):
    """Where it happened: a schematic chart, Aberdeen on the Scottish coast and the field about 200 km east."""
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('123E48')), (1, h('08222A'))])
    for i in range(0, W + 1, 120):
        cv.drawLine(i, 0, i, H, P(0x14FFFFFF, 2))
    for j in range(0, H + 1, 120):
        cv.drawLine(0, j, W, j, P(0x14FFFFFF, 2))
    land = skia.Path()
    pts = [(0, 0), (520, 0), (470, 90), (560, 170), (500, 250), (430, 300), (520, 380), (480, 470), (400, 560), (330, 640), (250, 700), (160, 730), (0, 760)]
    land.moveTo(*pts[0])
    for p in pts[1:]:
        land.lineTo(*p)
    land.close()
    cv.drawPath(land, P(h('3A5A4A')))
    cv.drawPath(land, P(h('9AD0B0'), 6))
    Wd.text_card(cv, 'SCOTLAND', 210, 330, 52, h('BFE8D0'), None)
    ax, ay, fx, fy = 500, 420, 1380, 420
    cv.drawCircle(ax, ay, 16, P(h('FFD866')))
    cv.drawCircle(ax, ay, 16, P(0xFF000000, 5))
    Wd.text_card(cv, 'ABERDEEN', ax - 20, ay + 78, 50, 0xFFFFFFFF, 0xFF000000)
    q = min(1, c.lt / 1.1)
    x = ax + 24
    while x < lerp(ax, fx - 40, q):
        cv.drawLine(x, ay, min(x + 26, fx - 40), ay, P(h('FF7A1A'), 9))
        x += 44
    if q >= 1:
        r = 30 + 8 * math.sin(t * 5)
        cv.drawCircle(fx, fy, r + 26, P(Wd.alpha(h(RED), 0.3), 6))
        cv.drawCircle(fx, fy, 24, P(h(RED)))
        cv.drawCircle(fx, fy, 24, P(0xFF000000, 6))
        pop(cv, 'HUNTINGTON FIELD', fx, fy - 80, 62, after(c, 1.1), WHITE)
        pop(cv, 'ABOUT 200 KM', (ax + fx) / 2, ay + 84, 76, after(c, 1.35))
    Wd.text_card(cv, 'NORTH SEA', 1380, 220, 66, Wd.alpha(0xFFFFFFFF, 0.5), None)
    for i in range(5):
        y = 560 + i * 26
        off = (t * 90 * (1 + i * 0.25)) % 260
        for xx in range(560, W + 260, 260):
            cv.drawLine(xx + off, y, xx + off + 120, y, P(Wd.alpha(h('8AD8E0'), 0.35), 6))


HOSES = (('BREATHING GAS', 'FFD866'), ('HOT WATER', 'FF7A1A'), ('POWER FOR HIS LAMP', '5EC8F0'), ('HIS SUPERVISOR\'S VOICE', '3DDC84'))


def umb_four(cv, c):
    t = c.t
    deepwater(cv, t)
    for i in range(14):                      # gas bubbles climbing past the cut cable, so the diagram never sits still
        u = (t * 0.28 + i * 0.173) % 1
        bx = (i * 151 + 60) % W + 26 * math.sin(t * 2.2 + i)
        cv.drawCircle(bx, H + 40 - u * (H + 80), 10 + (i % 4) * 5, P(Wd.alpha(h('BFF6FF'), 0.22), 5))
    z = 0.92 + 0.07 * c.k                     # slow push-in on the whole diagram (never past the frame edge)
    cv.save()
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-W / 2 + 14 * math.sin(t * 1.3), -H / 2 + 8 * math.sin(t * 1.9))
    cx, cy, r = 470, 460, 270
    cv.drawCircle(cx, cy, r + 22, P(0xFF000000))
    cv.drawCircle(cx, cy, r, P(h('E8B020')))
    cv.drawCircle(cx, cy, r - 30, P(h('20242B')))
    Wd.text_card(cv, 'THE UMBILICAL', cx, 120, 60, 0xFFFFFFFF, 0xFF000000)
    for i, (label, col) in enumerate(HOSES):
        on = c.k * 4.6 - 0.2 - i
        a = math.radians(-135 + i * 90)
        x, y = cx + math.cos(a) * 112, cy + math.sin(a) * 112
        cv.drawCircle(x, y, 78, P(h(col) if on > 0 else h('3A4048')))
        cv.drawCircle(x, y, 78, P(0xFF000000, 8))
        if on > 0:
            cv.drawCircle(x, y, 30 + 6 * math.sin(t * 6 + i), P(0xFF000000))
            kk = min(1, on / 0.2)
            ty = 215 + i * 150
            cv.drawLine(x + 78, y, lerp(x + 78, 860, kk), ty - 24, P(h(col), 6))
            if kk >= 1:
                Wd.text_card(cv, label, 890, ty, 70, h(col), 0xFF000000, center=False)
                for j in range(3):          # something is flowing down every line
                    u = (t * 0.9 + j / 3 + i * 0.21) % 1
                    cv.drawCircle(lerp(x + 78, 860, u), lerp(y, ty - 24, u), 13, P(0xFFFFFFFF))
                    cv.drawCircle(lerp(x + 78, 860, u), lerp(y, ty - 24, u), 13, P(0xFF000000, 4))
    cv.restore()


def umb_cut(cv, c):
    """Gas, heat, light, voices: struck out one after the other."""
    t = c.t
    deepwater(cv, t, '051C20', '010506')
    labels = ('GAS', 'HEAT', 'LIGHT', 'VOICES')
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), 150)
    for i, (label, (_, col)) in enumerate(zip(labels, HOSES)):
        on = c.k * 5.6 - 0.5 - i
        x, y = 250 + (i % 2) * 800, 330 + (i // 2) * 290
        dead = on > 0
        Wd.text_card(cv, label, x, y, 150, h('6A7482') if dead else h(col), 0xFF000000, center=False)
        if dead:
            kk = min(1, on / 0.22)
            cv.drawLine(x - 20, y - 52, x - 20 + (f.measureText(label) + 40) * kk, y - 52, P(h(RED), 22))
    if c.k > 0.84:
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h(RED), 0.12 if (t * 3) % 1 < 0.6 else 0.04)))


def drift_240(cv, c):
    """Seen from above: the yellow structure on the seabed, and the ship sliding about 240 metres off it."""
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E3E40')), (1, h('0A1E22'))])
    for i in range(7):
        y = 120 + i * 130
        off = (t * 120 * (1 + (i % 3) * 0.3)) % 300
        for xx in range(-300, W + 300, 300):
            cv.drawLine(xx + off, y, xx + off + 140, y - 16, P(Wd.alpha(h('BFE8E8'), 0.22), 8))
    sx, sy = 330, 520
    cv.drawRect(skia.Rect.MakeXYWH(sx - 60, sy - 44, 120, 88), P(h('E8B020'), 14))
    cv.drawCircle(sx, sy, 110 + 10 * math.sin(t * 4), P(Wd.alpha(h('FF7A1A'), 0.6), 6))
    Wd.text_card(cv, 'THE STRUCTURE', sx + 40, sy + 210, 46, h('FFD866'), 0xFF000000)
    e = min(1, c.lt / 1.5)
    e = e * e * (3 - 2 * e)
    x = lerp(sx + 40, 1380, e)
    cv.save()
    cv.translate(x, sy - 30 * e)
    cv.rotate(-14 * e + 3 * math.sin(t * 2))
    hull = skia.Path()
    hull.moveTo(-210, -62)
    hull.lineTo(120, -62)
    hull.lineTo(220, 0)
    hull.lineTo(120, 62)
    hull.lineTo(-210, 62)
    hull.close()
    cv.drawPath(hull, P(h('B8322A')))
    cv.drawPath(hull, P(0xFF000000, 8))
    cv.drawRect(skia.Rect.MakeXYWH(30, -44, 110, 88), P(h('ECE8DC')))
    cv.drawCircle(175, 0, 34, P(h('2E6A4A')))
    cv.drawRect(skia.Rect.MakeXYWH(-150, -30, 90, 60), P(h('E8B020')))
    cv.restore()
    if e > 0.2:
        cv.drawLine(sx, sy + 130, lerp(sx, x, 1), sy + 130, P(0xFFFFFFFF, 8))
        for xx in (sx, x):
            cv.drawLine(xx, sy + 104, xx, sy + 156, P(0xFFFFFFFF, 8))
    pop(cv, 'ABOUT 240 M', 900, 800 - 60, 130, after(c, 1.5), AMB, -3)
    pop(cv, 'OFF POSITION', 900, 880 - 60, 60, after(c, 1.8), WHITE, -3)


def body_o2(cv, c):
    """A body's oxygen store: a couple of litres."""
    wall(cv, c.t)
    x, y = 560, 470
    cv.drawCircle(x, y - 250, 90, P(h('BFE8E8'), 14))
    body = skia.Path()
    for i, p in enumerate(((-150, -140), (150, -140), (190, 120), (110, 150), (90, 330), (-90, 330), (-110, 150), (-190, 120))):
        (body.moveTo if i == 0 else body.lineTo)(x + p[0], y + p[1])
    body.close()
    cv.drawPath(body, P(h('BFE8E8'), 14))
    lvl = lerp(0.9, 0.3, c.k)
    cv.save()
    cv.clipPath(body)
    cv.drawRect(skia.Rect.MakeLTRB(x - 200, y + 330 - 470 * lvl, x + 200, y + 340), P(Wd.alpha(h('FF7A1A'), 0.8)))
    cv.restore()
    Wd.text_card(cv, 'O2', x, y + 130, 110, 0xFFFFFFFF, 0xFF000000)
    pop(cv, 'A COUPLE OF LITRES', 1300, 330, 80, after(c, 0.4))
    pop(cv, 'of oxygen in a body', 1300, 420, 56, after(c, 0.6), WHITE)
    card(cv, 'MINUTES. NOT HALF AN HOUR.', 1300, 640, 800, -3, 46, after(c, 1.5), 'F4EEDF')


def why_cold(cv, c):
    """Best guess one: the near-freezing water."""
    wall(cv, c.t)
    k = min(1, c.lt / 0.16)
    cv.save()
    cv.translate(560, 450)
    cv.scale(0.6 + 0.3 * k, 0.6 + 0.3 * k)
    cv.rotate(c.t * 14)
    for i in range(6):
        cv.save()
        cv.rotate(i * 60)
        cv.drawLine(0, 0, 0, -290, P(h('BFEFFF'), 26))
        for d in (-120, -200):
            cv.drawLine(0, d, 66, d - 66, P(h('BFEFFF'), 20))
            cv.drawLine(0, d, -66, d - 66, P(h('BFEFFF'), 20))
        cv.restore()
    cv.restore()
    Wd.text_card(cv, 'BEST GUESS 1', 1320, 250, 56, h(AMB), 0xFF000000)
    pop(cv, 'NEAR-FREEZING WATER', 1370, 400, 72, after(c, 0.3), WHITE)
    pop(cv, 'slowed his body right down', 1320, 500, 58, after(c, 0.9), 'BFEFFF')


def why_o2(cv, c):
    """Best guess two: the oxygen-rich gas he had been breathing under pressure."""
    wall(cv, c.t)
    for i in range(7):
        a = i * 0.9 + c.t * 0.7
        rr = 150 + 40 * math.sin(c.t * 1.3 + i)
        x, y = 560 + math.cos(a) * rr * 1.5, 450 + math.sin(a) * rr
        cv.drawCircle(x, y, 76, P(h('FF7A1A')))
        cv.drawCircle(x, y, 76, P(0xFF000000, 9))
        Wd.text_card(cv, 'O2', x, y + 26, 70, 0xFFFFFFFF, None)
    Wd.text_card(cv, 'BEST GUESS 2', 1320, 250, 56, h(AMB), 0xFF000000)
    pop(cv, 'OXYGEN-RICH GAS', 1370, 400, 84, after(c, 0.3), WHITE)
    pop(cv, 'breathed under pressure', 1320, 500, 58, after(c, 0.9), 'FFD0A0')
    card(cv, 'NOBODY KNOWS FOR SURE', 1320, 690, 820, 3, 56, after(c, 2.0))


def clock_dispute(cv, c):
    """The reports do not agree on how long: 29, 33, 38, 40 minutes."""
    wall(cv, c.t)
    Wd.text_card(cv, 'HOW LONG WITHOUT GAS?', 960, 170, 70, 0xFFFFFFFF, 0xFF000000)
    for i, (n, ang) in enumerate(((29, -4), (33, 3), (38, -2), (40, 5))):
        k = c.k * 5.2 - 0.6 - i
        x = 330 + i * 420
        if k > 0:
            kk = min(1, k / 0.2)
            cv.save()
            cv.translate(x, 430)
            cv.scale(1 + 0.5 * (1 - kk), 1 + 0.5 * (1 - kk))
            pinned(cv, 0, 0, 340, 330, ang, h(('FFD866', 'F4EEDF')[i % 2]))
            cv.rotate(ang)
            Wd.text_card(cv, str(n), 0, 60, 190, INK, None)
            Wd.text_card(cv, 'MIN', 0, 130, 56, INK, None)
            cv.restore()
    pop(cv, 'NOT 5', 960, 720, 120, (c.k - 0.86) / 0.06, RED, -4)


def board_after(cv, c):
    wall(cv, c.t)
    pinned(cv, 560, 430, 640, 560, -3)
    cv.save()
    cv.translate(560, 430)
    cv.rotate(-3)
    photo(cv, 'diver', 0, 20, 580, 450, (0.5, 0.3))
    cv.restore()
    card(cv, '3 WEEKS LATER: DIVING AGAIN', 1340, 230, 900, 3, 54, after(c, 0.15))
    card(cv, 'SAME STRUCTURE. SAME TEAM.', 1340, 430, 880, -3, 54, after(c, 0.45), 'F4EEDF')
    card(cv, 'MARRIED MORAG', 1340, 630, 640, 4, 66, after(c, 0.9))


def dp_fix(cv, c):
    """What the investigation found."""
    t = c.t
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('101A24')), (1, h('05080C'))])
    cv.drawRoundRect(skia.Rect.MakeXYWH(150, 110, 780, 560), 30, 30, P(h('06282C')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(150, 110, 780, 560), 30, 30, P(h('FF7A1A'), 6))
    for i in range(1, 7):
        cv.drawLine(150 + i * 111, 120, 150 + i * 111, 660, P(0x300E9AA0, 3))
    for j in range(1, 5):
        cv.drawLine(160, 110 + j * 112, 920, 110 + j * 112, P(0x300E9AA0, 3))
    fixed = c.k > 0.5
    col = h('3DDC84') if fixed else h(RED)
    cv.drawCircle(540, 390, 150, P(col, 14))
    cv.drawCircle(540, 390, 22, P(h('FFD866')))
    sx = 540 if fixed else 540 + 190 + 30 * math.sin(t * 3)
    cv.save()
    cv.translate(sx, 390 if fixed else 330)
    cv.rotate(0 if fixed else -20)
    cv.drawRect(skia.Rect.MakeXYWH(-90, -30, 180, 60), P(h('FF7A1A')))
    cv.restore()
    Wd.text_card(cv, 'DYNAMIC POSITIONING', 540, 180, 48, h('FF7A1A'), None)
    pop(cv, 'FAULT TRACED', 1380, 250, 90, after(c, 0.2), RED)
    pop(cv, 'inside the positioning system', 1400, 340, 52, after(c, 0.4), WHITE)
    pop(cv, 'HARDWARE REPLACED', 1380, 500, 64, (c.k - 0.5) / 0.05, '3DDC84')
    card(cv, 'SAFETY WARNING TO THE INDUSTRY', 1380, 660, 860, -3, 42, (c.k - 0.72) / 0.05)


def board_true(cv, c):
    wall(cv, c.t)
    pinned(cv, 600, 440, 640, 640, 2)
    cv.save()
    cv.translate(600, 440)
    cv.rotate(2)
    photo(cv, 'diver', 0, 24, 570, 520, (0.5, 0.25))
    cv.restore()
    k = min(1, max(0, (c.lt - 0.25) / 0.12))
    if c.lt > 0.25:
        cv.save()
        cv.translate(680, 640)
        cv.rotate(-13)
        cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
        cv.drawRoundRect(skia.Rect.MakeLTRB(-300, -110, 300, 110), 20, 20, P(h(RED), 22))
        Wd.text_card(cv, 'TRUE', 0, 62, 180, h(RED), None)
        cv.restore()
    card(cv, '5 MIN OF GAS', 1400, 280, 600, 4, 72, after(c, 0.6))
    card(cv, 'ABOUT 30 MIN ON THE SEABED', 1400, 520, 900, -3, 52, after(c, 1.0), 'F4EEDF')


SHOTS = {f.__name__: f for f in (gas_five, board_gas, map_north, umb_four, umb_cut, drift_240, body_o2, why_cold, why_o2, clock_dispute,
                                 board_after, dp_fix, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(text, x=760, y=180, size=84, at=0.3, col=AMB, ang=-3):
    def f(cv, c):
        if c.lt > at:
            pop(cv, text, x, y, size, (c.lt - at) / 0.12, col, ang)
    return f


def snow(cv, c):
    """Marine snow drifting through the lamp light."""
    Wd.particles(cv, W, H, c.t, 70, Wd.alpha(h('D8F6FF'), 0.3), 17, size=(2, 6), drift=(-22, 26), wobble=20)


def squall(cv, c):
    Wd.rain(cv, W, H, c.t, density=130, c=0x66DCEAEA, slant=0.4, speed=1900, seed=5, length=40)


def first(f):
    """Only on the first use of a shot type: re-framed repeats (prm alt) keep the picture clean."""
    def g(cv, c):
        if 'alt' not in c.prm:
            f(cv, c)
    return g


def second(f):
    def g(cv, c):
        if 'alt' in c.prm:
            f(cv, c)
    return g


def both(*fs):
    def f(cv, c):
        for g in fs:
            g(cv, c)
    return f


def amber(cv, c):
    on = (c.t * 3.0) % 1 < 0.5
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('FFA020'), 0.1 if on else 0.0)))


def redflash(cv, c):
    on = (c.t * 3.0) % 1 < 0.5
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h(RED), 0.12 if on else 0.0)))


def rovcam(cv, c):
    """Camera furniture for the ROV feed: scan lines, corner brackets, a blinking REC dot."""
    for y in range(0, H, 8):
        cv.drawLine(0, y, W, y, P(0x16000000, 3))
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('3DDC84'), 0.07)))
    roll = (c.t * 500) % (H + 300) - 150
    cv.drawRect(skia.Rect.MakeXYWH(0, roll, W, 70), P(0x14FFFFFF))
    L = 110
    for x, y, sx, sy in ((90, 90, 1, 1), (W - 90, 90, -1, 1), (90, 700, 1, -1), (W - 90, 700, -1, -1)):
        cv.drawLine(x, y, x + sx * L, y, P(0xFFFFFFFF, 8))
        cv.drawLine(x, y, x, y + sy * L, P(0xFFFFFFFF, 8))
    cv.drawLine(960 - 46, 400, 960 + 46, 400, P(0x99FFFFFF, 4))
    cv.drawLine(960, 400 - 46, 960, 400 + 46, P(0x99FFFFFF, 4))
    if (c.t * 2.2) % 1 < 0.6:
        cv.drawCircle(250, 150, 20, P(h(RED)))
    Wd.text_card(cv, 'ROV CAM', 420, 170, 56, 0xFFFFFFFF, 0xFF000000)
    if c.k > 0.62:
        pop(cv, 'NO MOVEMENT', 1420, 610, 92, (c.k - 0.62) / 0.05, RED, -3)


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1420, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h(AMB), 0xFF000000)
        Wd.text_card(cv, 'CASE 003  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


TL = (560, 170)          # where stamps sit on most shots: upper left, clear of faces and captions
OVER = dict(
    snap=snow, fall_back=both(snow, second(stamp('"LIKE A SHOTGUN"', 1380, 200, 84, 0.25, WHITE, 3))),
    alone_wide=both(snow, first(stamp('100 M DOWN', 1400, 220, 120, 0.25, WHITE, -4)), second(stamp('A FEW DEGREES ABOVE FREEZING', 960, 170, 70, 0.4, 'BFEFFF', -2))),
    bell_away=both(snow, first(stamp('THE BELL IS GONE', 620, 200, 92, 0.4, RED, 3))),
    ship_wide=both(squall, second(stamp('DSV BIBBY TOPAZ', 620, 170, 76, 0.3, WHITE, -2))),
    chamber_wide=first(stamp('SATURATION CHAMBER', 620, 150, 70, 0.3, 'FFD866', -2)), chamber_cu=stamp('HELIUM + OXYGEN', 1380, 200, 80, 0.3, AMB, 3),
    bell_down=snow, bell_stage=both(snow, stamp('THREE GO DOWN', 620, 170, 84, 0.3, WHITE, -3)),
    work=both(snow, stamp('CHRIS LEMONS', 1330, 300, 60, 0.3, WHITE, 0), stamp('DAVE YUASA', 640, 300, 60, 0.7, WHITE, 0)),
    dunc_tend=stamp('DUNCAN ALLCOCK, IN THE BELL', 700, 150, 60, 0.3, WHITE, -2),
    rook_line=snow, valve_cu=snow, rook_cable=both(snow, stamp('LOSE IT, LOSE ALL FOUR', 640, 170, 72, 0.4, AMB, -3)),
    storm_wide=both(squall, first(stamp('ROUGH SEA. HIGH WIND.', 640, 170, 76, 0.3, WHITE, -2))),
    bridge_calm=both(first(stamp('DYNAMIC POSITIONING', 640, 150, 72, 0.4, '3DDC84', -2)), second(stamp('THE FAULT WAS IN HERE', 640, 150, 72, 0.4, AMB, -2))),
    bridge_alarm=both(amber, stamp('SYSTEM FAILED', 640, 170, 110, 0.5, RED, -4)), bridge_fight=amber,
    alarm=both(redflash, first(stamp('POSITION LOST', 640, 170, 104, 0.3, RED, -4)), second(stamp('BACK TO THE BELL', 640, 170, 96, 0.3, WHITE, -3))),
    ship_drift=both(squall, first(stamp('DRIFTING', 1400, 220, 150, 0.3, WHITE, 5))),
    bell_drag=snow, go_back=snow, cable_tight=both(snow, stamp('SNAGGED', 1400, 220, 150, 0.35, AMB, -5)), rook_flinch=snow,
    yua_dragged=both(snow, stamp('DAVE YUASA', 1400, 220, 84, 0.3, WHITE, 3)), yua_climb=both(snow, stamp('HIS LINE WON\'T REACH', 640, 170, 72, 0.4, WHITE, -3)),
    lem_switch=both(snow, stamp('EMERGENCY BOTTLES', 620, 170, 76, 0.9, AMB, -3)), rook_dark=snow,
    climb=snow, lem_side=snow, rook_sit=snow, still_body=snow, rov_launch=snow, rov_in=snow, rov_pov=rovcam, rook_low=snow,
    ship_back=both(squall, stamp('ABOUT 30 MIN LATER', 640, 170, 84, 0.2, WHITE, -3)), yua_drop=snow,
    lift=snow, rook_point=snow, haul_up=snow,
    breaths=stamp('TWO RESCUE BREATHS', 640, 150, 76, 0.5, WHITE, -3), eyes_open=stamp('BREATHING', 1400, 240, 110, 0.55, AMB, -3),
    sits_up=second(stamp('NO LASTING DAMAGE', 640, 150, 80, 0.3, '3DDC84', -3)),
    back_work=both(snow, stamp('3 WEEKS LATER', 640, 170, 96, 0.3, AMB, -3)),
    signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (the diver thrown back, the cut line, the bell lights leaving, Rook) + a three-line hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0B1A22'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(700, 0), (1280, 0)], [0x00000000, 0xD0000000])))
    Wd.text_card(cv, 'LIFELINE CUT', 1000, 230, 66, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, '5 MIN OF GAS', 1000, 360, 76, h(AMB), 0xFF000000)
    Wd.text_card(cv, 'ALIVE', 1000, 530, 136, h('3DDC84'), 0xFF000000)
