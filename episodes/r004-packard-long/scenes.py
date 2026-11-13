"""Case 004, full case file (16:9) - Michael Packard. The story is filmed in 3D (world3d.py). This file holds the flat
graphic inserts (Rook's chart wall, the stopwatch, the blackout, the family photograph, the readings, the light box,
the front page, the film strip, the dinner plate, the throat diagram), the overlays drawn on top of 3D shots, and the
thumbnail."""
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
ORANGE, AMBER, RED, PAPER = 'FF7A1A', 'FFB000', 'E5392F', 'F4EEDF'


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) pinned to the wall as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('1F8A88')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def cape(cv, x, y, s, col, width):
    """The hooked arm of Cape Cod, as a single stroke."""
    p = skia.Path()
    p.moveTo(x - 260 * s, y + 250 * s)
    p.cubicTo(x - 60 * s, y + 260 * s, x + 120 * s, y + 250 * s, x + 200 * s, y + 170 * s)
    p.cubicTo(x + 280 * s, y + 60 * s, x + 250 * s, y - 150 * s, x + 130 * s, y - 250 * s)
    p.cubicTo(x + 40 * s, y - 320 * s, x - 80 * s, y - 290 * s, x - 70 * s, y - 210 * s)
    p.cubicTo(x - 60 * s, y - 170 * s, x - 10 * s, y - 170 * s, x + 10 * s, y - 200 * s)
    pa = P(col, width)
    pa.setStrokeCap(skia.Paint.kRound_Cap)
    cv.drawPath(p, pa)


def wall(cv, t, land=True):
    """Rook's case wall for this one: a navy sea chart of the Cape with soundings and a compass rose."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('12314E')), (1, h('07121F'))])
    for j in range(0, H + 1, 120):
        cv.drawLine(0, j, W, j, P(0x14FFFFFF, 2))
    for i in range(0, W + 1, 120):
        cv.drawLine(i, 0, i, H, P(0x14FFFFFF, 2))
    if land:
        cape(cv, 1560, 520, 1.15, 0x26E8D8A8, 60)
        cape(cv, 1560, 520, 1.15, 0x44E8D8A8, 8)
    cv.save()
    cv.translate(170, 800)
    cv.rotate(8 * math.sin(t * 0.8))
    cv.drawCircle(0, 0, 84, P(0x66FFB000, 5))
    for i in range(8):
        cv.save()
        cv.rotate(i * 45)
        L = 116 if i % 2 == 0 else 70
        pth = skia.Path()
        pth.moveTo(0, -L)
        pth.lineTo(13, 0)
        pth.lineTo(-13, 0)
        pth.close()
        cv.drawPath(pth, P(0x88FFB000 if i else 0xFFFF7A1A))
        cv.restore()
    cv.restore()
    for i, (x, y, n) in enumerate(((120, 150, '45'), (700, 110, '38'), (1250, 170, '52'), (420, 620, '41'), (1100, 760, '60'), (1780, 900, '47'))):
        Wd.text_card(cv, n, x, y + 6 * math.sin(t * 1.5 + i), 36, 0x55BFE6FF, None)
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, W - 14, H - 14), P(h(ORANGE), 8))


def pinned(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 26, 18, P(h(ORANGE)))
    cv.drawCircle(-5, -h_ / 2 + 21, 6, P(0x88FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col='FFD866'):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, h(col))
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.48, size, INK, None)
    cv.restore()


def punch(cv, text, x, y, size, k, col, ang=0.0, box=None):
    """Text that lands with a scale punch. box = (half width, half height) draws a rubber-stamp frame."""
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(1.8 - 0.8 * k, 1.8 - 0.8 * k)
    if box:
        cv.drawRoundRect(skia.Rect.MakeLTRB(-box[0], -box[1], box[0], box[1]), 20, 20, P(h(col), 20))
        Wd.text_card(cv, text, 0, size * 0.35, size, h(col), None)
    else:
        Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
    cv.restore()


def ramp(lt, at, d=0.13):
    return min(1.0, max(0.0, (lt - at) / d))


def greenwater(cv, t, top='0E5A5E', bot='04181C'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    Wd.particles(cv, W, H, t, 60, Wd.alpha(h('BFF6FF'), 0.35), 4, size=(2, 6), drift=(-10, -50), wobble=22)


# ------------------------------------------------------------------ flat inserts
def clock30(cv, c):
    """A stopwatch. The hook says half a minute; his own count was thirty to forty seconds."""
    greenwater(cv, c.t)
    cx, cy, r = 560, 450, 280
    k = min(1, c.lt / 0.16)
    wide = 'TO' in c.prm.get('txt', '')
    cv.save()
    cv.translate(cx, cy)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-44, -r - 92, 88, 76), 14, 14, P(h('C8CCD4')))
    cv.drawCircle(0, 0, r + 30, P(0xFF000000))
    cv.drawCircle(0, 0, r + 18, P(h('C8CCD4')))
    cv.drawCircle(0, 0, r, P(h(PAPER)))
    sweep = lerp(0, 240 if wide else 180, c.lt / (1.6 if wide else 0.8))
    cv.drawArc(skia.Rect.MakeLTRB(-r + 40, -r + 40, r - 40, r - 40), -90, min(sweep, 180), True, P(Wd.alpha(h(ORANGE), 0.45)))
    if sweep > 180:
        cv.drawArc(skia.Rect.MakeLTRB(-r + 40, -r + 40, r - 40, r - 40), 90, sweep - 180, True, P(Wd.alpha(h(RED), 0.5)))
    for i in range(12):
        a = math.radians(i * 30 - 90)
        cv.drawLine(math.cos(a) * (r - 60), math.sin(a) * (r - 60), math.cos(a) * (r - 16), math.sin(a) * (r - 16), P(INK, 12 if i % 3 == 0 else 6))
    a = math.radians(sweep - 90)
    cv.drawLine(-math.cos(a) * 40, -math.sin(a) * 40, math.cos(a) * (r - 50), math.sin(a) * (r - 50), P(h(RED), 16))
    cv.drawCircle(0, 0, 28, P(INK))
    cv.restore()
    punch(cv, c.prm.get('txt', 'HALF A MINUTE'), 1390, 380, 100 if not wide else 82, ramp(c.lt, 0.3 if not wide else 0.7), AMBER, -3)
    punch(cv, 'BY HIS OWN COUNT' if wide else "IN A WHALE'S MOUTH", 1390, 520, 56, ramp(c.lt, 0.6 if not wide else 1.4), 'FFFFFF', -3)


def board_whale(cv, c):
    wall(cv, c.t, False)
    k = min(1, c.lt / 0.2)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    pinned(cv, 600, 430, 900 * s, 600 * s, -2.5)
    cv.save()
    cv.translate(600, 430)
    cv.rotate(-2.5)
    cv.scale(s, s)
    photo(cv, 'whale', 0, 22, 840, 490, (0.5, 0.45))
    cv.restore()
    card(cv, "WHALES DON'T", 1420, 230, 600, 150, -4, 68, ramp(c.lt, 0.3))
    card(cv, 'EAT PEOPLE', 1500, 420, 520, 150, 3, 68, ramp(c.lt, 0.42), PAPER)
    punch(cv, 'NO CHANCE', 1380, 680, 118, ramp(c.lt, 0.62), RED, -6)


def black(cv, c):
    """Everything goes black: only his bubbles and the glint of his own mask."""
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(0xFF020405))
    pulse = 0.5 + 0.5 * math.sin(c.t * 9)
    Wd.glow(cv, 960, 440, 760, h('7A1028'), 0.22 + 0.16 * pulse)
    Wd.particles(cv, W, H, c.t * 3.0, 44, Wd.alpha(h('BFF6FF'), 0.5), 9, size=(4, 13), drift=(14, -150), wobble=30)
    j = 14 * math.sin(c.t * 31)
    blink = (c.lt * 2.3) % 1 < 0.12
    for sx in (-1, 1):
        cv.drawRoundRect(skia.Rect.MakeXYWH(960 + sx * 105 - 62 + j, 420 - (6 if blink else 46), 124, 12 if blink else 92), 22, 22, P(0xFFF4FBFF))
    cv.drawRoundRect(skia.Rect.MakeXYWH(960 - 235 + j, 340, 470, 190), 50, 50, P(Wd.alpha(h('F2C230'), 0.5), 14))


def shark_q(cv, c):
    """The first thought, his and then his crewman's: shark. Then: no."""
    wall(cv, c.t)
    k = min(1, c.lt / 0.16)
    cv.save()
    cv.translate(760, 430)
    cv.scale(0.75 + 0.25 * k, 0.75 + 0.25 * k)
    for i in range(3):
        y = 150 + i * 46
        cv.drawLine(-520 + i * 30, y + 8 * math.sin(c.t * 4 + i), 520 - i * 30, y + 8 * math.sin(c.t * 4 + i + 2), P(0x66BFE6FF, 10))
    fin = skia.Path()
    fin.moveTo(-190, 150)
    fin.cubicTo(-120, -40, -20, -220, 120, -300)
    fin.cubicTo(110, -150, 150, 20, 240, 150)
    fin.close()
    cv.drawPath(fin, P(h('8A96A8')))
    cv.drawPath(fin, P(0xFF000000, 12))
    k2 = ramp(c.lt, 0.58, 0.1)
    if k2 > 0:
        for sgn in (-1, 1):
            cv.drawLine(-300 * k2, sgn * -300 * k2 - 60, 300 * k2, sgn * 300 * k2 - 60, P(h(RED), 44))
    cv.restore()
    Wd.text_card(cv, 'SHARK?', 1400, 420, 170, 0xFFFFFFFF, 0xFF000000)
    punch(cv, 'A GREAT WHITE?', 1400, 560, 70, ramp(c.lt, 0.3), AMBER, -3)


def family(cv, c):
    """What he thought about in there. Drawn plainly: a photograph of three people."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A1422')), (1, h('0C0508'))])
    Wd.glow(cv, 960, 430, 800, h('FFB878'), 0.2 + 0.05 * math.sin(c.t * 2))
    Wd.particles(cv, W, H, c.t, 26, Wd.alpha(h('FFD8B0'), 0.3), 3, size=(2, 5), drift=(0, -24), wobble=16)
    k = min(1, c.lt / 0.5)
    s = (lerp(0.9, 1.0, k) + 0.02 * c.k) * 1.02
    cv.save()
    cv.translate(960, 420)
    cv.rotate(-2)
    cv.scale(s, s)
    cv.drawRect(skia.Rect.MakeXYWH(-420 + 14, -340 + 18, 840, 720), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-420, -340, 840, 720), P(h(PAPER)))
    cv.drawRect(skia.Rect.MakeXYWH(-380, -300, 760, 540), P(h('F2B276')))
    cv.drawRect(skia.Rect.MakeXYWH(-380, 100, 760, 140), P(h('C98248')))
    for x, hh, col in ((-170, 260, '4A2E38'), (20, 310, '3A2430'), (195, 225, '4A2E38')):
        cv.drawCircle(x, 110 - hh, 46, P(h(col)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 64, 110 - hh + 38, 128, hh - 38 + 130), 50, 50, P(h(col)))
    cv.drawRect(skia.Rect.MakeXYWH(-380, 240, 760, 6), P(h(PAPER)))
    Wd.text_card(cv, 'HIS WIFE. HIS TWO BOYS.', 0, 330, 54, INK, None)
    cv.restore()


def whale_outline(cv, x, y, s):
    """Side view of a humpback, head to the right, as a flat chart drawing."""
    body = skia.Path()
    body.moveTo(x + 400 * s, y - 10 * s)
    body.cubicTo(x + 330 * s, y - 130 * s, x + 60 * s, y - 150 * s, x - 190 * s, y - 70 * s)
    body.cubicTo(x - 300 * s, y - 40 * s, x - 370 * s, y - 20 * s, x - 430 * s, y - 110 * s)
    body.lineTo(x - 400 * s, y)
    body.lineTo(x - 440 * s, y + 90 * s)
    body.cubicTo(x - 360 * s, y + 20 * s, x - 300 * s, y + 40 * s, x - 190 * s, y + 70 * s)
    body.cubicTo(x + 40 * s, y + 160 * s, x + 320 * s, y + 170 * s, x + 400 * s, y - 10 * s)
    body.close()
    cv.drawPath(body, P(h('33475C')))
    cv.drawPath(body, P(0xFF000000, 10))
    fl = skia.Path()
    fl.moveTo(x + 110 * s, y + 90 * s)
    fl.cubicTo(x + 40 * s, y + 190 * s, x - 60 * s, y + 250 * s, x - 130 * s, y + 250 * s)
    fl.cubicTo(x - 60 * s, y + 200 * s, x, y + 140 * s, x + 30 * s, y + 90 * s)
    fl.close()
    cv.drawPath(fl, P(h('D2D8D6')))
    cv.drawPath(fl, P(0xFF000000, 8))
    cv.drawCircle(x + 215 * s, y + 10 * s, 12 * s, P(0xFF000000))


def throat(cv, c):
    """A mouth that takes in a roomful of water, and a throat far too narrow for a man."""
    wall(cv, c.t, False)
    k = min(1, c.lt / 0.18)
    cv.save()
    cv.translate(700, 400)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    whale_outline(cv, 0, 0, 1.3)
    cv.scale(1.3, 1.3)
    mouth = skia.Path()
    mouth.moveTo(410, -10)
    mouth.cubicTo(350, -70, 290, -78, 232, -30)
    mouth.cubicTo(290, 60, 350, 80, 410, -10)
    mouth.close()
    cv.drawPath(mouth, P(h('C4607A')))
    pulse = 0.5 + 0.5 * math.sin(c.t * 8)
    cv.drawLine(232, -30, 60, -6, P(h(ORANGE), 12 + 5 * pulse))
    cv.drawCircle(232, -30, 18 + 5 * pulse, P(h(ORANGE), 7))
    cv.restore()
    k2 = ramp(c.lt, 0.35)
    if k2 > 0:
        cv.save()
        cv.translate(1500, 420)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        cv.drawCircle(0, -150, 34, P(h(PAPER)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-44, -112, 88, 150), 30, 30, P(h(PAPER)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-40, 20, 34, 120), 14, 14, P(h(PAPER)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(6, 20, 34, 120), 14, 14, P(h(PAPER)))
        cv.restore()
        Wd.text_card(cv, 'DOES NOT FIT', 1500, 660, 70, h(PAPER), 0xFF000000)
    punch(cv, 'THROAT: TOO NARROW', 760, 760, 80, ramp(c.lt, 0.55), AMBER, -3)


def board_true(cv, c):
    wall(cv, c.t)
    pinned(cv, 520, 440, 700, 720, 2)
    cv.save()
    cv.translate(520, 440)
    cv.rotate(2)
    photo(cv, 'diver', 0, 26, 630, 610, (0.5, 0.3))
    cv.restore()
    punch(cv, 'TRUE', 520, 520, 190, ramp(c.lt, 0.2, 0.12), RED, -13, (310, 115))
    card(cv, 'IN ITS MOUTH: YES', 1350, 300, 700, 150, -3, 66, ramp(c.lt, 0.6))
    card(cv, 'SWALLOWED: NO', 1400, 560, 620, 150, 3, 66, ramp(c.lt, 1.5), PAPER)


def map_cape(cv, c):
    """Where: the tip of the Cape. A schematic chart, not a survey."""
    wall(cv, c.t, False)
    k = min(1, c.lt / 0.25)
    cape(cv, 900, 470, 1.2, Wd.alpha(h('E8D8A8'), 0.25 * k), 90)
    cape(cv, 900, 470, 1.2, Wd.alpha(h('E8D8A8'), k), 14)
    Wd.text_card(cv, 'CAPE COD', 760, 560, 70, 0x66E8D8A8, None)
    for i, (x, y, name, lx, at_, col) in enumerate(((910, 232, 'PROVINCETOWN', 1300, 0.15, AMBER), (816, 216, 'HERRING COVE', 440, 0.4, ORANGE), (1200, 420, 'WELLFLEET', 1520, 0.65, 'FFFFFF'))):
        kk = ramp(c.lt, at_)
        if kk <= 0:
            continue
        pulse = 0.5 + 0.5 * math.sin(c.t * 6 + i)
        cv.drawCircle(x, y, 16 + 22 * pulse * (i == 1), P(Wd.alpha(h(col), 0.5), 6))
        cv.drawCircle(x, y, 13, P(h(col)))
        cv.drawLine(x, y, lx + (-170 if lx > x else 190), y - 20 + i * 14, P(Wd.alpha(h(col), 0.8), 5))
        punch(cv, name, lx, y - 4 + i * 14, 62, kk, col, 0)
    card(cv, 'FRIDAY, 11 JUNE 2021', 420, 620, 620, 130, -3, 52, ramp(c.lt, 0.5), PAPER)


def conditions(cv, c):
    """The two readings the Cape Cod Times gave for that dive."""
    greenwater(cv, c.t, '127078', '052A30')
    k1, k2 = ramp(c.lt, 0.1, 0.2), ramp(c.lt, 0.5, 0.2)
    cv.save()                                             # a thermometer
    cv.translate(330, 450)
    cv.scale(0.8 + 0.2 * k1, 0.8 + 0.2 * k1)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-34, -290, 68, 480), 34, 34, P(h(PAPER)))
    cv.drawCircle(0, 220, 74, P(h(PAPER)))
    cv.drawCircle(0, 220, 52, P(h('3A8AD0')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-16, 220 - lerp(60, 300, k1), 32, lerp(60, 300, k1)), 16, 16, P(h('3A8AD0')))
    for i in range(7):
        cv.drawLine(40, -250 + i * 60, 70, -250 + i * 60, P(h(PAPER), 6))
    cv.restore()
    punch(cv, 'ABOUT 60°F', 700, 330, 110, k1, 'FFFFFF', -2)
    punch(cv, 'THE WATER', 700, 450, 56, k1, AMBER, -2)
    if k2 > 0:                                            # visibility: a row of fish fading into the green
        for i in range(9):
            a = max(0.0, 1 - i / 5.2)
            x = 1040 + i * 96
            fish = skia.Path()
            fish.moveTo(x - 34, 640)
            fish.cubicTo(x - 10, 615, x + 22, 620, x + 34, 640)
            fish.cubicTo(x + 22, 660, x - 10, 665, x - 34, 640)
            fish.lineTo(x - 52, 622)
            fish.lineTo(x - 52, 658)
            fish.close()
            cv.drawPath(fish, P(Wd.alpha(h('D8F6FF'), a * k2)))
        cv.drawLine(1010, 700, 1010 + 480 * k2, 700, P(h(AMBER), 8))
        for x in (1010, 1250, 1490):
            cv.drawLine(x, 684, x, 716, P(h(AMBER), 8))
        punch(cv, 'HE CAN SEE ABOUT 20 FEET', 1330, 560, 54, k2, 'FFFFFF', 2)
        Wd.text_card(cv, '0', 1010, 770, 44, h(AMBER), 0xFF000000)
        Wd.text_card(cv, '20 FT', 1490, 770, 44, h(AMBER), 0xFF000000)


def xray(cv, c):
    """A light box. Two legs, everything where it should be."""
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(h('0A1016')))
    fl = 0.92 + 0.08 * math.sin(c.t * 23) * (c.lt < 0.4)
    cv.drawRoundRect(skia.Rect.MakeXYWH(150, 90, 760, 720), 18, 18, P(h('2A3440')))
    cv.drawRect(skia.Rect.MakeXYWH(180, 120, 700, 660), P(Wd.alpha(h('BFE6F4'), 0.85 * fl)))
    cv.drawRect(skia.Rect.MakeXYWH(210, 150, 640, 600), P(h('10202C')))
    bone = P(Wd.alpha(h('E4F4FA'), 0.9))
    for x in (400, 660):
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 26, 180, 52, 250), 24, 24, bone)
        cv.drawCircle(x, 440, 44, bone)
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 30, 470, 34, 250), 16, 16, bone)
        cv.drawRoundRect(skia.Rect.MakeXYWH(x + 8, 480, 20, 235), 10, 10, bone)
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 70, 300, 140, 300), 60, 60, P(Wd.alpha(h('BFE6F4'), 0.12)))
    k1 = ramp(c.lt, 0.15)
    card(cv, 'FIRST REPORT: A BROKEN LEG', 1360, 250, 800, 130, -3, 50, k1, PAPER)
    k2 = ramp(c.lt, 0.45, 0.1)
    if k2 > 0:
        cv.drawLine(970, 268, 970 + 780 * k2, 232, P(h(RED), 16))
    punch(cv, 'BRUISING. A LOT OF IT.', 1360, 470, 66, ramp(c.lt, 0.7), 'FFFFFF', -4)
    punch(cv, 'NO BROKEN BONES', 1360, 640, 82, ramp(c.lt, 1.5), AMBER, -4)


def headline(cv, c):
    """A front page with no words on it yet, and what the editor wanted."""
    wall(cv, c.t, False)
    k = min(1, c.lt / 0.2)
    s = 0.75 + 0.25 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(600, 440)
    cv.rotate(-3)
    cv.scale(s, s)
    cv.drawRect(skia.Rect.MakeXYWH(-330 + 14, -370 + 18, 660, 740), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-330, -370, 660, 740), P(h(PAPER)))
    cv.drawRect(skia.Rect.MakeXYWH(-290, -335, 580, 70), P(INK))
    cv.drawRect(skia.Rect.MakeXYWH(-290, -245, 580, 6), P(INK))
    for i in range(2):
        cv.drawRect(skia.Rect.MakeXYWH(-290, -205 + i * 62, 580 - i * 150, 40), P(INK))
    photo(cv, 'whale', -130, 90, 300, 250, (0.5, 0.45))
    for i in range(7):
        cv.drawRect(skia.Rect.MakeXYWH(50, -30 + i * 38, 240 - (i % 3) * 30, 14), P(0x993A3A3A))
    for i in range(3):
        cv.drawRect(skia.Rect.MakeXYWH(-290, 250 + i * 34, 580 - i * 70, 14), P(0x993A3A3A))
    cv.restore()
    card(cv, 'THE ASSIGNMENT:', 1400, 250, 600, 130, 3, 56, ramp(c.lt, 0.3), 'FFD866')
    punch(cv, 'DEBUNK IT', 1400, 470, 150, ramp(c.lt, 0.55), RED, -6, (430, 110))
    punch(cv, 'A FISH TALE?', 1400, 700, 80, ramp(c.lt, 0.8), 'FFFFFF', 3)


def film(cv, c):
    """Two years on: not a debunking. A documentary."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A1420')), (1, h('06040A'))])
    Wd.glow(cv, 960, 420, 760, h(AMBER), 0.12 + 0.04 * math.sin(c.t * 3))
    off = (c.t * 90) % 300
    cv.save()
    cv.translate(0, 300)
    cv.rotate(-3)
    cv.drawRect(skia.Rect.MakeXYWH(-100, -150, W + 200, 300), P(0xFF0A0A0E))
    for i in range(-1, 9):
        x = i * 300 - off
        cv.drawRect(skia.Rect.MakeXYWH(x + 20, -105, 260, 210), P(h('1F8A88')))
        photo(cv, ('whale', 'diver')[i % 2], x + 150, 0, 260, 210, (0.5, 0.4))
        for j in range(5):
            cv.drawRoundRect(skia.Rect.MakeXYWH(x + 16 + j * 60, -138, 30, 20), 5, 5, P(h(PAPER)))
            cv.drawRoundRect(skia.Rect.MakeXYWH(x + 16 + j * 60, 118, 30, 20), 5, 5, P(h(PAPER)))
    cv.restore()
    k = ramp(c.lt, 0.2)
    punch(cv, 'TWO YEARS LATER', 960, 600, 76, k, 'FFFFFF', -2)
    punch(cv, 'A DOCUMENTARY', 960, 740, 130, ramp(c.lt, 0.5), AMBER, -2)


def fly(cv, c):
    """Stormy Mayo's comparison, as reported by CNN: a really nice meal, and a fly goes into your mouth."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('7A2E2A')), (1, h('3A1412'))])
    for i in range(-2, 18):
        cv.drawLine(i * 130, 0, i * 130 + 300, H, P(0x14FFFFFF, 40))
    cx, cy = 660, 430
    cv.drawCircle(cx + 10, cy + 14, 300, P(0x55000000))
    cv.drawCircle(cx, cy, 300, P(h(PAPER)))
    cv.drawCircle(cx, cy, 215, P(h('E4DCC8'), 6))
    for i, (px, py, r, col) in enumerate(((-70, -30, 86, 'C98248'), (70, 40, 70, '3E9A5A'), (30, -90, 50, 'E8B43A'), (-60, 90, 44, 'D8382C'))):
        cv.drawCircle(cx + px, cy + py, r, P(h(col)))
    for sx in (-1, 1):
        x = cx + sx * 400
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 14, cy - 230, 28, 480), 14, 14, P(h('C8CCD4')))
        if sx < 0:
            for j in (-1, 0, 1):
                cv.drawRoundRect(skia.Rect.MakeXYWH(x - 9 + j * 26, cy - 300, 18, 110), 9, 9, P(h('C8CCD4')))
        else:
            cv.drawRoundRect(skia.Rect.MakeXYWH(x - 26, cy - 300, 52, 230), 26, 26, P(h('C8CCD4')))
    u = min(1.0, c.lt / 2.2)
    a = c.t * 5.5
    rad = lerp(330, 0, u * u)
    fx, fy = lerp(1300, cx, u) + math.cos(a) * rad * 0.6, lerp(250, cy - 30, u) + math.sin(a) * rad * 0.4
    for sx in (-1, 1):
        cv.save()
        cv.translate(fx, fy)
        cv.rotate(sx * (35 + 25 * math.sin(c.t * 60)))
        cv.drawOval(skia.Rect.MakeXYWH(-10, -44, 20, 44), P(0xAAFFFFFF))
        cv.restore()
    cv.drawOval(skia.Rect.MakeXYWH(fx - 17, fy - 11, 34, 24), P(0xFF14121A))
    cv.drawCircle(fx + 15, fy, 9, P(0xFF14121A))
    card(cv, 'A REALLY NICE MEAL', 1440, 330, 640, 130, -3, 54, ramp(c.lt, 0.4), PAPER)
    card(cv, 'AND A FLY', 1500, 540, 420, 130, 3, 60, ramp(c.lt, 2.2))


def before(cv, c):
    """Sober: years earlier he lived through a plane crash in which other people died. No stamps, no jokes."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2430')), (1, h('090C12'))])
    Wd.particles(cv, W, H, c.t, 24, Wd.alpha(h('C8D8E8'), 0.22), 7, size=(2, 4), drift=(0, -14), wobble=10)
    k = min(1, c.lt / 0.6)
    cv.save()                                             # a small plane seen from above, nose to the upper right
    cv.translate(440 + 60 * c.lt, 450 - 22 * c.lt)          # it keeps flying: a slow drift up and to the right
    cv.rotate(-28)
    pl = P(Wd.alpha(h('8A96A8'), k))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-300, -26, 600, 52), 26, 26, pl)
    wing = skia.Path()
    wing.moveTo(60, 0)
    wing.lineTo(-30, -235)
    wing.lineTo(-95, -235)
    wing.lineTo(-70, 0)
    wing.lineTo(-95, 235)
    wing.lineTo(-30, 235)
    wing.close()
    cv.drawPath(wing, pl)
    tail = skia.Path()
    tail.moveTo(-235, 0)
    tail.lineTo(-275, -90)
    tail.lineTo(-305, -90)
    tail.lineTo(-295, 0)
    tail.lineTo(-305, 90)
    tail.lineTo(-275, 90)
    tail.close()
    cv.drawPath(tail, pl)
    cv.drawCircle(120, -150 * 0 - 0, 0, pl)
    for sy in (-1, 1):
        cv.drawRoundRect(skia.Rect.MakeXYWH(-10, sy * 110 - 16, 70, 32), 14, 14, pl)
    cv.restore()
    Wd.text_card(cv, 'YEARS EARLIER', 1300, 300, 64, Wd.alpha(h(AMBER), min(1, max(0, (c.lt - 0.4) / 0.5))), None)
    Wd.text_card(cv, 'COSTA RICA', 1300, 440, 110, Wd.alpha(h(PAPER), min(1, max(0, (c.lt - 1.5) / 0.5))), None)
    Wd.text_card(cv, 'A PLANE CRASH. HE LIVED.', 1300, 570, 56, Wd.alpha(h(PAPER), min(1, max(0, (c.lt - 2.1) / 0.5))), None)


SHOTS = {f.__name__: f for f in (clock30, board_whale, black, shark_q, family, throat, board_true, map_cape, conditions, xray, headline, film, fly, before)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(text, x=760, y=180, size=84, at=0.3, col='FFB000', ang=-3):
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


def first(f):
    """Only on the first use of a shot type: re-framed repeats (prm alt) keep the picture clean."""
    def g(cv, c):
        if 'alt' not in c.prm:
            f(cv, c)
    return g


def both(*fs):
    def f(cv, c):
        for g in fs:
            g(cv, c)
    return f


def rays(cv, c, a=0.1):
    """Shafts of sunlight slanting down through shallow water, and drifting motes."""
    for i in range(8):
        x = 160 + i * 250 + 50 * math.sin(c.t * 0.7 + i * 1.9)
        wdt = 80 + 40 * math.sin(c.t * 0.9 + i)
        p = skia.Path()
        p.moveTo(x, -20)
        p.lineTo(x + wdt, -20)
        p.lineTo(x + wdt - 300, 900)
        p.lineTo(x - 400, 900)
        p.close()
        pa = skia.Paint(AntiAlias=True)
        pa.setShader(skia.GradientShader.MakeLinear([(0, 0), (0, 900)], [Wd.alpha(h('E8FFF4'), a * (0.7 + 0.3 * math.sin(c.t * 1.3 + i))), 0x00E8FFF4]))
        cv.drawPath(p, pa)
    Wd.particles(cv, W, H, c.t, 50, Wd.alpha(h('E8FFF4'), 0.3), 13, size=(2, 5), drift=(-16, -18), wobble=18)


def murk(cv, c):
    Wd.particles(cv, W, H, c.t, 56, Wd.alpha(h('D8F6FF'), 0.28), 17, size=(2, 6), drift=(-26, 20), wobble=20)


def breath(cv, c):
    """Inside the mouth: a faint red pulse and drifting bubbles."""
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('7A1028'), 0.08 + 0.06 * math.sin(c.t * 5.2))))
    Wd.particles(cv, W, H, c.t, 22, Wd.alpha(h('FFE0E6'), 0.25), 5, size=(2, 5), drift=(6, -30), wobble=14)


def mist(cv, c):
    """Sea spray blowing across the lens."""
    Wd.particles(cv, W, H, c.t * 2.5, 48, Wd.alpha(h('FFFFFF'), 0.4), 21, size=(2, 7), drift=(-120, 60), wobble=26)


def glare(cv, c):
    """Daylight flooding in as the jaws part."""
    breath(cv, c)
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('E8FBFF'), 0.5 * max(0.0, c.k - 0.45) ** 1.5)))


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1420, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h(AMBER), 0xFF000000)
        Wd.text_card(cv, 'CASE 004  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(
    gulp=murk, jaws_shut=murk, whale_wide=rays, spat=mist, lobster_cu=rays, shoal=rays,
    gear_up=stamp('MICHAEL PACKARD, 56', 700, 180, 80, 0.3, 'FFFFFF', -2),
    crewman=both(first(stamp('JOSIAH MAYO', 640, 180, 96, 0.3, 'FFFFFF', -2)), lambda cv, c: stamp("STORMY MAYO'S SON", 700, 180, 84, 0.3, 'FFB000', -2)(cv, c) if 'alt' in c.prm else None),
    bass_boats=first(stamp('BOATS OUT FOR STRIPED BASS', 800, 180, 64, 0.3, 'FFFFFF', -2)),
    pluck=both(rays, stamp('BY HAND', 620, 200, 130, 0.35, 'FFB000', -4)),
    bubble_watch=stamp('FOLLOW THE BUBBLES', 760, 180, 84, 0.4, 'FFFFFF', -2),
    roll_in=both(mist, first(stamp('IN HE GOES', 660, 180, 100, 0.5, 'FFFFFF', -3))),
    cruise=rays,
    sand_hunt=rays, shadow=murk, shove=both(murk, stamp('A HUGE SHOVE', 700, 190, 110, 0.45, 'FFFFFF', -4)),
    feel_dark=both(breath, stamp('NO TEETH', 620, 220, 150, 0.35, 'FFB000', -5)),
    tumble=both(breath, first(stamp("IT'S MOVING", 660, 190, 110, 0.4, 'FFFFFF', -4))),
    squeeze=both(breath, first(stamp('SQUEEZING', 640, 190, 120, 0.35, 'E5392F', -4))),
    mouth_wide=both(breath, first(stamp("A WHALE'S MOUTH", 760, 180, 96, 0.4, 'FFB000', -3))),
    reg_lost=both(breath, stamp('THE REGULATOR', 700, 180, 90, 0.3, 'FFFFFF', -3)),
    reg_cu=both(breath, stamp('STILL BREATHING', 720, 180, 96, 0.4, 'FFFFFF', -3)),
    gauge=both(breath, stamp('UNTIL IT RUNS OUT?', 760, 180, 88, 0.6, 'E5392F', -3)),
    rook_quiet=breath, rise=rays, breach=mist, shake=both(mist, stamp('IT SHAKES ITS HEAD', 760, 180, 84, 0.3, 'FFFFFF', -3)),
    light_slit=both(glare, stamp('LIGHT', 620, 220, 170, 0.3, 'FFFFFF', -4)),
    flung=both(mist, first(stamp('IN THE AIR', 660, 200, 120, 0.25, 'FFB000', -4))),
    splashdown=both(mist, first(stamp('IN THE WATER', 700, 200, 110, 0.25, 'FFFFFF', -4))),
    float_free=mist, mayo_sees=both(mist, stamp('AN ERUPTION OF WATER', 720, 180, 78, 0.4, 'FFFFFF', -3)), pop_up=mist,
    francis=stamp('JOE FRANCIS, CHARTER CAPTAIN', 800, 180, 62, 0.3, 'FFFFFF', -2),
    feet_first=both(mist, stamp('FEET FIRST. FLIPPERS ON.', 800, 180, 76, 0.3, 'FFB000', -3)),
    haul=mist, radio=stamp('RADIO TO SHORE', 700, 180, 90, 0.3, 'FFFFFF', -3), race_home=mist,
    ward_doc=stamp('JUST BRUISES', 660, 180, 100, 0.3, 'FFB000', -3),
    rook_door=stamp('OUT THE SAME AFTERNOON', 780, 180, 76, 0.3, 'FFFFFF', -2),
    newsroom=first(stamp('TOLD TO DEBUNK IT', 720, 190, 92, 0.6, 'E5392F', -4)),
    tape=stamp('HE CHECKED', 640, 190, 110, 0.5, 'FFFFFF', -3),
    lab_wide=first(stamp('AN ACCIDENT', 660, 190, 120, 0.5, 'FFFFFF', -3)),
    feeding=both(rays, first(stamp('LUNGE FEEDING', 700, 190, 100, 0.3, 'FFB000', -3))),
    mouthful=both(rays, first(stamp('MOUTH WIDE OPEN', 720, 190, 90, 0.25, 'FFFFFF', -3))),
    blind_spot=both(rays, stamp("IT CAN'T SEE AHEAD", 760, 190, 92, 0.5, 'FFB000', -3)),
    throat_look=breath, baleen_cu=stamp('MICHAEL = THE FLY', 760, 190, 96, 0.25, 'FFB000', -3), descend=both(rays, stamp('HE CAN SEE ABOUT 20 FEET', 800, 180, 70, 0.3, 'FFFFFF', -2)), fluke_dusk=stamp('SORRY, WHALE', 660, 200, 100, 1.0, 'FFFFFF', -3),
    signoff=closed)


def THUMB(cv, c):
    """1280x720: the 3D still (the whale upright, the diver's fins at its lips, Rook in the swell) + a four-word hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('1C6F8E'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(700, 0), (1280, 0)], [0x00000000, 0xD8000000])))
    Wd.text_card(cv, 'IN ITS', 990, 190, 120, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'MOUTH', 990, 330, 120, h(AMBER), 0xFF000000)
    Wd.text_card(cv, 'ALIVE', 990, 520, 140, h('3DDC84'), 0xFF000000)
