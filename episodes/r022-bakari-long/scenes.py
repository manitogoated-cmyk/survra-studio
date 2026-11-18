"""Case 022, the full case file (16:9) - Bahia Bakari, the only survivor of Yemenia Flight 626 (30 June 2009). The story
is filmed in 3D (world3d.py). This file holds the flat inserts on a 1920x1080 canvas (Rook's case file, a drawn chart of
the journey, a diagram of the night approach, the two cards for the moment she cannot remember, the two drawings of
what she believed, the investigators' findings, the verdict, and Rook's case board), the 2D overlays drawn on top of
3D shots, and the thumbnail. Every card is a drawing made for this film: the aeroplanes on them are generic shapes
with no livery, the chart and the approach diagram are not maps or charts of the real places and are marked as
diagrams, and none of it reproduces a real photograph, document, report or logo. Captions run in a band around 86%
of the height and the label sits top right, so the cards keep both clear."""
import math
import os

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1920, 1080
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER, CHALK = h('FF7A1A'), h('FFB000'), h('EFE6CC'), h('F4EEDC')
SEA, SEAL = h('0D3440'), h('3E8C9C')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 51.37 + j * 87.13) * 24634.63) % 1


def font(size):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def left(cv, s, x, y, size, color=0xFFFFFFFF, stroke=0xFF000000, maxw=None):
    if maxw:
        w = font(size).measureText(s)
        if w > maxw:
            size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke, center=False)


def push(cv, c, amount=0.1, sway=0.0):
    """A slow push in on a card (and a little sway), so a held card is never a still picture."""
    z = 1 + amount * c.k
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.rotate(sway * math.sin(c.t * 1.3))
    cv.translate(-W / 2 + 26 * math.sin(c.t * 0.9), -H / 2 + 14 * math.sin(c.t * 1.4))


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('14384A')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def skin(cv, seed=1, glow=0.0):
    """Rook's board for this case: a sheet of riveted aircraft skin."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('20323E')), (0.5, h('16242E')), (1, h('0A1218'))])
    for i in range(3):
        y = 40 + 340 * i
        cv.drawRect(skia.Rect.MakeXYWH(50, y, 1820, 334), P((h('C4CAD2'), h('B6BCC6'))[i % 2]))
        for j in range(40):
            cv.drawCircle(70 + 45.5 * j, y + 16, 6, P(h('8A929E')))
            cv.drawCircle(70 + 45.5 * j, y + 318, 6, P(h('8A929E')))
    for i in range(14):
        x, y = 100 + 1700 * rn(i, seed), 80 + 900 * rn(i, seed + 1)
        cv.drawLine(x, y, x + 120 * rn(i, seed + 2) + 30, y + 30 * rn(i, seed + 3), P(h('8A929E'), 3, a=0.6))
    if glow:
        Wd.glow(cv, 960, 480, 1000, h('9CD8E8'), 0.12 * glow)
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x88000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.restore()


def pins(cv, xs, y):
    for x in xs:
        cv.drawCircle(x, y, 22, P(ORANGE))
        cv.drawCircle(x, y, 22, P(INK, 5))


def typed(cv, lines, x, y0, step, c, rate=0.55, sizes=None, cols=None, maxw=1000):
    shown = c.lt / rate
    for i, line in enumerate(lines):
        if shown < i:
            break
        n = max(1, int(len(line) * min(1.0, (shown - i) * 1.6)))
        left(cv, line[:n], x, y0 + step * i, (sizes or [80] * 9)[i], (cols or [0xFFFFFFFF] * 9)[i], maxw=maxw)


def plane_mark(cv, x, y, s, ang, lights=1.0):
    """A plain airliner in chalk, nose to the right. No livery."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    body = skia.Path()
    body.addRoundRect(skia.Rect.MakeXYWH(-300, -44, 560, 88), 44, 44)
    cv.drawPath(body, P(CHALK))
    cv.drawPath(poly([(250, -40), (330, -6), (330, 12), (250, 44)]), P(CHALK))
    cv.drawPath(poly([(-300, -30), (-370, -150), (-310, -150), (-220, -40)]), P(CHALK))
    cv.drawPath(poly([(-40, 10), (-170, 150), (-110, 150), (80, 20)]), P(h('D8D2C0')))
    cv.drawPath(poly([(-290, 0), (-360, 50), (-320, 52), (-240, 12)]), P(h('D8D2C0')))
    for i in range(11):
        cv.drawRoundRect(skia.Rect.MakeXYWH(-240 + 42 * i, -22, 22, 26), 6, 6, P(h('FFD060'), a=lights))
    cv.drawPath(body, P(INK, 6))
    cv.restore()


def child_mark(cv, x, y, s, ang):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    for (a, b) in (((0, -6), (0, 44)), ((0, 8), (-26, -18)), ((0, 8), (26, -18)), ((0, 44), (-18, 80)), ((0, 44), (18, 80))):
        cv.drawLine(a[0], a[1], b[0], b[1], P(h('E0705A'), 13))
    cv.drawCircle(0, -26, 22, P(h('8A5A3C')))
    for sx in (-1, 1):
        cv.drawCircle(sx * 22, -42, 10, P(h('15121A')))
    cv.restore()


def paper_night(cv, c):
    """Dark blue paper with crayon stars: both 'what she believed' cards are drawn on it."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16264A')), (0.7, h('1C3458')), (1, h('12203A'))])
    for i in range(60):
        x, y = 40 + 1840 * rn(i, 1), 40 + 640 * rn(i, 2)
        r = 3 + 5 * rn(i, 3)
        a = 0.35 + 0.5 * abs(math.sin(c.t * 2.2 + i))
        cv.drawLine(x - r, y, x + r, y, P(CHALK, 3, a=a))
        cv.drawLine(x, y - r, x, y + r, P(CHALK, 3, a=a))
    fit(cv, 'WHAT SHE BELIEVED', 960, 130, 80, 1100, AMBER)


def waves(cv, c, y0):
    cv.drawRect(skia.Rect.MakeXYWH(0, y0, W, H - y0), P(SEA))
    for j in range(5):
        pts = [(x, y0 + 36 * j + 12 * math.sin(x * 0.02 + c.t * 2.2 + j * 1.7)) for x in range(-20, W + 40, 30)]
        cv.drawPath(poly(pts, False), P(SEAL, 7, a=0.8 - 0.12 * j))


# ---------------------------------------------------------------- inserts
FILE = ('BAHIA BAKARI, 12', 'ELDEST OF FOUR', 'WITH HER MOTHER, AZIZA', 'TO THE COMOROS, FOR THE SUMMER')


def file_card(cv, c):
    """Rook's case file for the trip: four lines typed onto the aircraft-skin board, beside a pinned card with a drawn suitcase."""
    cv.save()
    push(cv, c, 0.06, 0.3)
    skin(cv, 3, 0.6)
    card(cv, 400, 470, 440, 520, -3)
    cv.save()
    cv.translate(400, 470)
    cv.rotate(-3)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-140, -110, 280, 200), 20, 20, P(h('2E5A8C')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-140, -110, 280, 200), 20, 20, P(INK, 7))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-50, -150, 100, 50), 14, 14, P(INK, 9))
    cv.drawLine(-140, -20, 140, -20, P(INK, 5))
    fit(cv, 'CASE 022', 0, 190, 60, 360, h('2A2E38'), None)
    cv.restore()
    pins(cv, (250, 550), 220)
    left(cv, 'CASE FILE', 720, 200, 52, 0xCCFFFFFF)
    typed(cv, FILE, 700, 320, 130, c, 0.5, [92, 76, 76, 70], [AMBER, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF], 1020)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 40, 0x88FFE8C0, 73, size=(3, 7), drift=(120, -50), wobble=30, twinkle=True)


STOPS = (('PARIS', 300, 300), ('MARSEILLE', 470, 450), ("SANA'A", 1300, 560), ('MORONI', 1500, 860))


def route_card(cv, c):
    """A drawn chart, not a map: four stops joined by a dotted line, a small plain plane travelling along it."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2A3A')), (1, h('0E161E'))])
    cv.save()
    push(cv, c, 0.08, 0.2)
    card(cv, 960, 540, 1700, 900, -1, h('E8DFC4'))
    for i in range(14):                                       # faint blobs of land, nothing like a real coastline
        Wd.glow(cv, 200 + 1500 * rn(i, 5), 160 + 760 * rn(i, 6), 120 + 160 * rn(i, 7), h('C8B890'), 0.35)
    k = ease(c.k * 1.25)
    segs = list(zip(STOPS[:-1], STOPS[1:]))
    total = len(segs) * k
    px, py, ang = STOPS[0][1], STOPS[0][2], 0
    for i, (a, b) in enumerate(segs):
        f = max(0.0, min(1.0, total - i))
        for j in range(int(28 * f)):
            q = j / 28
            cv.drawCircle(lerp(a[1], b[1], q), lerp(a[2], b[2], q) - 60 * math.sin(q * math.pi), 6, P(INK))
        if 0 < f:
            px, py = lerp(a[1], b[1], f), lerp(a[2], b[2], f) - 60 * math.sin(f * math.pi)
            ang = math.degrees(math.atan2(b[2] - a[2], b[1] - a[1]))
    for i, (name, x, y) in enumerate(STOPS):
        if total >= i - 0.05:
            cv.drawCircle(x, y, 20, P(ORANGE))
            cv.drawCircle(x, y, 20, P(INK, 5))
            fit(cv, name, x + (0 if i != 1 else -40), y + (-48 if i != 3 else 64), 56, 460, 0xFFFFFFFF)
    if total > 2.1:
        fit(cv, 'CHANGE PLANES', STOPS[2][1], STOPS[2][2] + 66, 42, 420, AMBER)
    plane_mark(cv, px, py, 0.22, ang)
    fit(cv, 'DRAWN CHART, NOT A MAP', 1500, 180, 34, 520, 0xCCFFFFFF)
    cv.restore()


def approach_card(cv, c):
    """Diagram of the night approach: the coast, a runway, wind arrows, and a dotted path that swings out over the sea and comes back
    round to land from the other side. No figures that are not in the sources; marked as a diagram."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('06121A')), (1, h('0A1E28'))])
    cv.save()
    push(cv, c, 0.04, 0.15)
    land = poly([(-50, 1150), (-50, 250), (420, 200), (760, 300), (900, 520), (860, 780), (700, 1150)])
    cv.drawPath(land, P(h('16302A')))
    cv.drawPath(land, P(h('3E6A5A'), 5))
    for i in range(12):                                       # village lights
        cv.drawCircle(120 + 600 * rn(i, 4), 330 + 700 * rn(i, 5), 5, P(h('FFD080'), a=0.6 + 0.4 * math.sin(c.t * 3 + i)))
    cv.save()
    cv.translate(760, 560)
    cv.rotate(-12)
    cv.drawRect(skia.Rect.MakeXYWH(-24, -230, 48, 460), P(h('3A3F4C')))
    for j in range(10):
        cv.drawRect(skia.Rect.MakeXYWH(-3, -200 + 42 * j, 6, 22), P(CHALK, a=0.7))
    cv.restore()
    for i in range(7):                                        # gusting wind from the south
        x = 1050 + 120 * (i % 4) + 30 * math.sin(c.t * 2 + i)
        y = 920 - ((c.t * 260 + 140 * i) % 760)
        cv.drawLine(x, y + 90, x, y, P(SEAL, 9, a=0.8))
        cv.drawPath(poly([(x - 18, y + 20), (x, y - 10), (x + 18, y + 20)]), P(SEAL, a=0.8))
    k = ease(c.k * 1.2)
    pts = []
    for j in range(80):                                       # the swing out over the sea and back
        q = j / 79
        a = 0.1 + 2.9 * q
        pts.append((1000 + 250 * math.cos(a) - 200 * q, 470 + 250 * math.sin(a) + 160 * q))
    n = int(len(pts) * k)
    for j in range(0, n, 2):
        cv.drawCircle(pts[j][0], pts[j][1], 6, P(AMBER))
    if n > 2:
        x, y = pts[n - 1]
        cv.drawCircle(x, y, 14, P(0xFFFFFFFF))
    left(cv, 'NO MOON', 1180, 160, 64, 0xFFFFFFFF)
    left(cv, 'GUSTING WIND', 1180, 250, 64, SEAL, maxw=600)
    left(cv, 'SWING ROUND,', 1180, 340, 52, AMBER, maxw=600)
    left(cv, 'LAND THE OTHER WAY', 1180, 410, 52, AMBER, maxw=600)
    fit(cv, 'DIAGRAM, NOT TO SCALE', 380, 120, 34, 520, 0xAAFFFFFF)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 60, 0x66DCF0FF, 81, size=(2, 5), drift=(30, -260), wobble=20)


def shock_card(cv, c):
    """'Something like an electric shock.' White streaks crack across the frame and fade into the dark. Nothing else is shown."""
    cv.clear(h('05080C'))
    f = max(0.0, 1 - c.lt / 1.6)
    for i in range(9):
        y0 = 120 + 840 * rn(i, 2)
        pts = [(x, y0 + 60 * (rn(i * 30 + j, 3) - 0.5) + 30 * math.sin(c.t * 9 + j)) for j, x in enumerate(range(-40, W + 80, 120))]
        cv.drawPath(poly(pts, False), P(h('DCEBFF'), 3 + 6 * rn(i, 4), a=f * (0.5 + 0.5 * math.sin(c.t * 30 + i))))
    Wd.glow(cv, 960, 540, 900, h('BFD8FF'), 0.5 * f)
    fit(cv, 'SOMETHING LIKE', 960, 420, 86, 1400, 0xFFFFFFFF)
    fit(cv, 'AN ELECTRIC SHOCK', 960, 540, 104, 1500, AMBER)
    Wd.particles(cv, W, H, c.t, 50, 0x88DCEBFF, 61, size=(2, 6), drift=(0, -120), wobble=40, twinkle=True)


def black_card(cv, c):
    """'A black hole in her memory.' Near-black, dim specks drifting, the words coming up slowly. Nothing of the crash is shown."""
    cv.clear(h('020406'))
    Wd.glow(cv, 960 + 120 * math.sin(c.t * 0.7), 540, 700, h('1A3A4A'), 0.35 + 0.1 * math.sin(c.t * 1.3))
    cv.save()
    push(cv, c, 0.12, 0.3)
    a = ease(c.lt / 0.8)
    fit(cv, 'A BLACK HOLE', 960, 470, 120, 1400, (int(255 * a) << 24) | 0xFFFFFF, None)
    fit(cv, 'IN HER MEMORY', 960, 600, 76, 1200, (int(200 * ease((c.lt - 0.6) / 0.8)) << 24) | 0xFFB000, None)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 90, 0x77AACCDD, 63, size=(2, 6), drift=(40, -60), wobble=30, twinkle=True)


def fell_card(cv, c):
    """'She thinks she just fell out of the plane.' The aeroplane flies on across the night; one small figure drops away from it."""
    paper_night(cv, c)
    waves(cv, c, 860)
    px = lerp(560, 1360, ease(c.k))
    plane_mark(cv, px, 380 + 8 * math.sin(c.t * 3), 0.9, -3)
    k = ease((c.k - 0.12) / 0.8)
    fx, fy = 560 - 80 * k, 450 + 420 * k * k
    for i in range(int(k * 9)):
        q = i / 9
        cv.drawCircle(560 - 80 * q, 450 + 420 * q * q, 7, P(CHALK, a=0.7))
    child_mark(cv, fx, fy, 1.3, -25 + 50 * k)
    fit(cv, 'JUST HER', 1400, 760, 110, 800, 0xFFFFFFFF)


def landed_card(cv, c):
    """'...and that her mother landed safely without her.' The same aeroplane comes down onto a lit runway and stops."""
    paper_night(cv, c)
    cv.drawRect(skia.Rect.MakeXYWH(0, 700, W, H - 700), P(h('1A2230')))
    cv.drawRect(skia.Rect.MakeXYWH(0, 700, W, 16), P(h('3A4458')))
    for i in range(15):
        on = 0.5 + 0.5 * math.sin(c.t * 6 + i)
        cv.drawCircle(70 + 128 * i, 750, 12, P(AMBER, a=0.5 + 0.5 * on))
        cv.drawRect(skia.Rect.MakeXYWH(40 + 128 * i, 800, 64, 12), P(CHALK, a=0.5))
    k = ease(c.k / 0.7)
    x = lerp(-320, 900, k)
    y = lerp(300, 620, ease(c.k / 0.5))
    plane_mark(cv, x, y, 0.9, lerp(10, 0, ease(c.k / 0.5)))
    if c.k > 0.5:
        for dx in (-150, 60, 200):
            cv.drawCircle(x + dx * 0.9, y + 58, 16, P(INK))
            cv.drawCircle(x + dx * 0.9, y + 58, 16, P(CHALK, 5))
    if c.k > 0.5:
        fit(cv, 'EVERYONE SAFE', 1500, 330, 92, 700, 0xFFFFFFFF)
    if c.k > 0.65:
        fit(cv, 'EXCEPT HER', 1500, 450, 92, 700, AMBER)


REPORT = (('THE AIRCRAFT', 'NO FAULT FOUND'), ('THE APPROACH', 'AT NIGHT, IN A STRONG WIND'), ('THE CAUSE', "THE CREW'S ACTIONS: A STALL"))


def report_card(cv, c):
    """The investigators' findings in three lines on Rook's board (his summary in his own words, not a page of the report)."""
    cv.save()
    push(cv, c, 0.05, 0.3)
    skin(cv, 7, 0.5)
    card(cv, 330, 520, 380, 500, 3)
    cv.save()
    cv.translate(330, 520)
    cv.rotate(3)
    for j in range(9):
        cv.drawLine(-140, -170 + 40 * j, 140 - 60 * rn(j, 3), -170 + 40 * j, P(h('8A929E'), 8))
    fit(cv, 'REPORT, 2013', 0, 210, 44, 340, h('2A2E38'), None)
    cv.restore()
    pins(cv, (200, 460), 290)
    shown = c.lt / 0.7
    for i, (a, b) in enumerate(REPORT):
        if shown < i:
            break
        y = 240 + 230 * i
        left(cv, a, 640, y, 50, 0xCCFFFFFF)
        n = max(1, int(len(b) * min(1.0, (shown - i) * 1.6)))
        left(cv, b[:n], 640, y + 90, 76, AMBER if i == 2 else 0xFFFFFFFF, maxw=1060)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 30, 0x66FFE8C0, 75, size=(3, 7), drift=(120, -50), wobble=30, twinkle=True)


VERDICT = (('PARIS, SEPTEMBER 2022', 'GUILTY OF MANSLAUGHTER'), ('THE FINE', 'THE MAXIMUM: 225,000 EUROS'), ('2024', 'UPHELD ON APPEAL'))


def verdict_card(cv, c):
    """The verdict, three lines on Rook's board. No stamp, no gavel."""
    cv.save()
    push(cv, c, 0.05, 0.3)
    skin(cv, 11, 0.4)
    left(cv, 'THE AIRLINE', 200, 170, 54, 0xCCFFFFFF)
    shown = c.lt / 0.6
    for i, (a, b) in enumerate(VERDICT):
        if shown < i:
            break
        y = 300 + 230 * i
        left(cv, a, 200, y, 48, 0xCCFFFFFF)
        n = max(1, int(len(b) * min(1.0, (shown - i) * 1.6)))
        left(cv, b[:n], 200, y + 92, 88, AMBER if i == 0 else 0xFFFFFFFF, maxw=1400)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 30, 0x66FFE8C0, 77, size=(3, 7), drift=(120, -50), wobble=30, twinkle=True)


def board(cv, c):
    """Rook's board for this case: two photographs (the girl at the wreckage at night; the woman at the bar in 2022) and the count."""
    cv.save()
    push(cv, c, 0.07, 0.4)
    skin(cv, 5, 0.7)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    for (x, y, ang, name) in ((470, 440, -2.5, 'girl'), (1060, 470, 3.0, 'court')):
        cv.save()
        cv.translate(x, y)
        cv.scale(s, s)
        card(cv, 0, 0, 560, 460, ang)
        cv.rotate(ang)
        photo(cv, name, 0, -10, 510, 400)
        cv.restore()
    pins(cv, (290, 650, 880, 1240), 210)
    if c.lt > 0.25:
        left(cv, '153 ON BOARD', 1370, 360, 64, 0xFFFFFFFF, maxw=400)
    if c.lt > 0.45:
        left(cv, '1 SURVIVOR', 1370, 480, 76, AMBER, maxw=400)
    if c.lt > 0.65:
        left(cv, 'CASE 022', 1370, 600, 50, 0xCCFFFFFF)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 40, 0x88FFE8C0, 79, size=(3, 7), drift=(120, -50), wobble=30, twinkle=True)


SHOTS = {f.__name__: f for f in (file_card, route_card, approach_card, shock_card, black_card, fell_card, landed_card, report_card, verdict_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def night(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x66DCF0FF, 81, size=(2, 4), drift=(8, -5), wobble=8, twinkle=True)
    Wd.particles(cv, W, H, c.t, 24, 0x77E6F4FA, 83, size=(3, 7), drift=(260, -70), wobble=30)


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0x99EAF6FF, 85, size=(3, 9), drift=(300, -110), wobble=40)


def glint(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x88FFFFFF, 87, size=(2, 5), drift=(24, -12), wobble=18, twinkle=True)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 28, 0x55FFE8C8, 89, size=(2, 5), drift=(10, -14), wobble=14, twinkle=True)


def gale(cv, c):
    """The wind on the island: spray and leaves driven across the frame."""
    Wd.particles(cv, W, H, c.t, 90, 0x88DCF0FF, 91, size=(2, 6), drift=(-900, 60), wobble=40)
    Wd.particles(cv, W, H, c.t, 14, 0xAA2E5A3A, 93, size=(5, 10), drift=(-700, 120), wobble=80)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, 60, 0x55E8ECF0, -0.15, 1600, 6, 70)


def closed(cv, c):
    glint(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(430, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 022', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(girl_close=night, hands_grip=night, wide_night=night, plane_piece=night, rook_lands=night, rook_doubt=night, in_water=night, voices=night,
            dark_look=night, climb_try=night, big_wave=spray, hold_on=night, face_tired=night, dawn_break=glint, boat_far=spray, boat_near=spray,
            ring_throw=spray, ring_miss=spray, reach_fail=spray, sailor_jump=spray, sailor_swim=spray, lift_aboard=spray, blanket=glint, alive=glint,
            look_back=glint, hospital_wait=dust, hospital_tell=dust, her_face=dust, empty_chair=dust, rook_wrong=dust, sea_after=spray,
            debris_close=spray, signoff=closed, flat_pack=dust, doorway=dust, lounge=dust, cabin_seats=dust, window_dark=night, island_night=gale,
            cabin_shake=dust, bahia_look=dust, jet_arrive=drizzle, stairs=drizzle, father_hug=drizzle, court_wide=dust, testify=dust, families=dust,
            verdict=dust, court_rook=dust)


def THUMB(cv, c):
    """1280x720: the 3D still (her face and arms at the wreckage at night, right of frame) and the hook on the left, over black water."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0D3440'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(700, 0), (0, 0)], [0x00000000, 0xD0000000])))
    Wd.text_card(cv, 'ONLY ONE', 330, 280, 120, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'LIVED.', 330, 430, 140, AMBER, 0xFF000000)
