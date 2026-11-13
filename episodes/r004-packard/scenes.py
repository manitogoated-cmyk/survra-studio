"""Case 004 - Michael Packard. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(Rook's chart wall, the stopwatch, the blackout, the family photograph, the throat diagram) and the 2D overlays
drawn on top of 3D shots (sun rays, stamps)."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1080, 1920
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


def wall(cv, t):
    """Rook's case wall for this one: a navy sea chart of the Cape with soundings and a compass rose."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('12314E')), (1, h('07121F'))])
    for j in range(0, H + 1, 120):
        cv.drawLine(0, j, W, j, P(0x14FFFFFF, 2))
    for i in range(0, W + 1, 120):
        cv.drawLine(i, 0, i, H, P(0x14FFFFFF, 2))
    cape(cv, 700, 1380, 1.25, 0x30E8D8A8, 60)
    cape(cv, 700, 1380, 1.25, 0x55E8D8A8, 8)
    cv.save()
    cv.translate(190, 1640)
    cv.rotate(8 * math.sin(t * 0.8))
    cv.drawCircle(0, 0, 110, P(0x66FFB000, 6))
    for i in range(8):
        cv.save()
        cv.rotate(i * 45)
        L = 150 if i % 2 == 0 else 90
        pth = skia.Path()
        pth.moveTo(0, -L)
        pth.lineTo(16, 0)
        pth.lineTo(-16, 0)
        pth.close()
        cv.drawPath(pth, P(0x88FFB000 if i else 0xFFFF7A1A))
        cv.restore()
    cv.restore()
    for i, (x, y, n) in enumerate(((150, 300, '45'), (930, 420, '38'), (120, 1000, '52'), (960, 1010, '41'), (480, 1760, '60'))):
        Wd.text_card(cv, n, x, y + 6 * math.sin(t * 1.5 + i), 40, 0x55BFE6FF, None)
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(h(ORANGE), 10))


def pinned(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 30, 20, P(h(ORANGE)))
    cv.drawCircle(-5, -h_ / 2 + 25, 7, P(0x88FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col='FFD866'):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, h(col))
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.42, size, INK, None)
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
        cv.drawRoundRect(skia.Rect.MakeLTRB(-box[0], -box[1], box[0], box[1]), 20, 20, P(h(col), 22))
        Wd.text_card(cv, text, 0, size * 0.35, size, h(col), None)
    else:
        Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
    cv.restore()


def ramp(lt, at, d=0.13):
    return min(1.0, max(0.0, (lt - at) / d))


def greenwater(cv, t, top='0E5A5E', bot='04181C'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    Wd.particles(cv, W, H, t, 50, Wd.alpha(h('BFF6FF'), 0.35), 4, size=(2, 6), drift=(-10, -50), wobble=22)


# ------------------------------------------------------------------ flat inserts
def clock30(cv, c):
    """A stopwatch: about thirty seconds."""
    greenwater(cv, c.t)
    cx, cy, r = 540, 640, 300
    k = min(1, c.lt / 0.16)
    cv.save()
    cv.translate(cx, cy)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-46, -r - 96, 92, 80), 14, 14, P(h('C8CCD4')))
    cv.drawCircle(0, 0, r + 30, P(0xFF000000))
    cv.drawCircle(0, 0, r + 18, P(h('C8CCD4')))
    cv.drawCircle(0, 0, r, P(h(PAPER)))
    sweep = lerp(0, 180, c.lt / 0.72)
    cv.drawArc(skia.Rect.MakeLTRB(-r + 40, -r + 40, r - 40, r - 40), -90, sweep, True, P(Wd.alpha(h(ORANGE), 0.45)))
    for i in range(12):
        a = math.radians(i * 30 - 90)
        cv.drawLine(math.cos(a) * (r - 60), math.sin(a) * (r - 60), math.cos(a) * (r - 16), math.sin(a) * (r - 16), P(INK, 12 if i % 3 == 0 else 6))
    a = math.radians(sweep - 90)
    cv.drawLine(-math.cos(a) * 40, -math.sin(a) * 40, math.cos(a) * (r - 50), math.sin(a) * (r - 50), P(h(RED), 16))
    cv.drawCircle(0, 0, 28, P(INK))
    cv.restore()
    punch(cv, 'ABOUT 30 SECONDS', 540, 1130, 80, ramp(c.lt, 0.7), AMBER)


def board_whale(cv, c):
    wall(cv, c.t)
    k = min(1, c.lt / 0.2)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    pinned(cv, 550, 500, 780 * s, 560 * s, -2.5)
    cv.save()
    cv.translate(550, 500)
    cv.rotate(-2.5)
    cv.scale(s, s)
    photo(cv, 'whale', 0, 24, 720, 440, (0.5, 0.45))
    cv.restore()
    card(cv, "WHALES DON'T", 380, 900, 600, 160, -5, 68, ramp(c.lt, 0.3))
    card(cv, 'EAT PEOPLE', 700, 1075, 520, 160, 4, 68, ramp(c.lt, 0.42), PAPER)
    punch(cv, 'NO CHANCE', 550, 1530, 150, ramp(c.lt, 0.62), RED, -6)


def black(cv, c):
    """Everything goes black: only his bubbles and the glint of his own mask."""
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(0xFF020405))
    pulse = 0.5 + 0.5 * math.sin(c.t * 9)
    Wd.glow(cv, 540, 760, 620, h('7A1028'), 0.22 + 0.16 * pulse)
    Wd.particles(cv, W, H, c.t * 3.0, 34, Wd.alpha(h('BFF6FF'), 0.5), 9, size=(4, 13), drift=(14, -150), wobble=30)
    j = 14 * math.sin(c.t * 31)
    blink = (c.lt * 2.3) % 1 < 0.12
    for sx in (-1, 1):
        cv.drawRoundRect(skia.Rect.MakeXYWH(540 + sx * 105 - 62 + j, 720 - (6 if blink else 46), 124, 12 if blink else 92), 22, 22, P(0xFFF4FBFF))
    cv.drawRoundRect(skia.Rect.MakeXYWH(540 - 235 + j, 640, 470, 190), 50, 50, P(Wd.alpha(h('F2C230'), 0.5), 14))


def shark_q(cv, c):
    """His first thought: shark. Then: no teeth."""
    wall(cv, c.t)
    k = min(1, c.lt / 0.16)
    cv.save()
    cv.translate(540, 720)
    cv.scale(0.75 + 0.25 * k, 0.75 + 0.25 * k)
    for i in range(3):
        y = 150 + i * 46
        cv.drawLine(-420 + i * 30, y + 8 * math.sin(c.t * 4 + i), 420 - i * 30, y + 8 * math.sin(c.t * 4 + i + 2), P(0x66BFE6FF, 10))
    fin = skia.Path()
    fin.moveTo(-190, 150)
    fin.cubicTo(-120, -40, -20, -220, 120, -300)
    fin.cubicTo(110, -150, 150, 20, 240, 150)
    fin.close()
    cv.drawPath(fin, P(h('8A96A8')))
    cv.drawPath(fin, P(0xFF000000, 12))
    Wd.text_card(cv, 'SHARK?', 0, 360, 150, 0xFFFFFFFF, 0xFF000000)
    k2 = ramp(c.lt, 0.58, 0.1)
    if k2 > 0:
        for sgn in (-1, 1):
            cv.drawLine(-330 * k2, sgn * -330 * k2 + 20, 330 * k2, sgn * 330 * k2 + 20, P(h(RED), 44))
    cv.restore()


def family(cv, c):
    """What he thought about in there. Drawn plainly: a photograph of three people."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A1422')), (1, h('0C0508'))])
    Wd.glow(cv, 540, 700, 700, h('FFB878'), 0.2 + 0.05 * math.sin(c.t * 2))
    Wd.particles(cv, W, H, c.t, 22, Wd.alpha(h('FFD8B0'), 0.3), 3, size=(2, 5), drift=(0, -24), wobble=16)
    k = min(1, c.lt / 0.5)
    s = lerp(0.9, 1.0, k) + 0.02 * c.k
    cv.save()
    cv.translate(540, 690)
    cv.rotate(-2)
    cv.scale(s, s)
    cv.drawRect(skia.Rect.MakeXYWH(-340 + 14, -330 + 18, 680, 700), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-340, -330, 680, 700), P(h(PAPER)))
    cv.drawRect(skia.Rect.MakeXYWH(-300, -290, 600, 520), P(h('F2B276')))
    cv.drawRect(skia.Rect.MakeXYWH(-300, 90, 600, 140), P(h('C98248')))
    for x, hh, col in ((-150, 250, '4A2E38'), (20, 300, '3A2430'), (175, 215, '4A2E38')):
        cv.drawCircle(x, 100 - hh, 44, P(h(col)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 62, 100 - hh + 36, 124, hh - 36 + 130), 50, 50, P(h(col)))
    cv.drawRect(skia.Rect.MakeXYWH(-300, 230, 600, 6), P(h(PAPER)))
    Wd.text_card(cv, 'HIS WIFE. HIS SONS.', 0, 318, 52, INK, None)
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
    wall(cv, c.t)
    k = min(1, c.lt / 0.18)
    cv.save()
    cv.translate(540, 640)
    cv.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    whale_outline(cv, 0, 0, 1.05)
    mouth = skia.Path()                                   # the mouth cavity, pink
    mouth.moveTo(410, -10)
    mouth.cubicTo(350, -70, 290, -78, 232, -30)
    mouth.cubicTo(290, 60, 350, 80, 410, -10)
    mouth.close()
    cv.drawPath(mouth, P(h('C4607A')))
    pulse = 0.5 + 0.5 * math.sin(c.t * 8)
    cv.drawLine(232, -30, 60, -6, P(h(ORANGE), 14 + 6 * pulse))                                        # the throat, drawn as the thin line it is
    cv.drawCircle(232, -30, 20 + 6 * pulse, P(h(ORANGE), 8))
    cv.restore()
    # a man for scale, and the verdict
    k2 = ramp(c.lt, 0.35)
    if k2 > 0:
        cv.save()
        cv.translate(250, 1090)
        cv.scale(1.5 - 0.5 * k2, 1.5 - 0.5 * k2)
        cv.drawCircle(0, -150, 34, P(h(PAPER)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-44, -112, 88, 150), 30, 30, P(h(PAPER)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-40, 20, 34, 120), 14, 14, P(h(PAPER)))
        cv.drawRoundRect(skia.Rect.MakeXYWH(6, 20, 34, 120), 14, 14, P(h(PAPER)))
        cv.restore()
        Wd.text_card(cv, 'DOES NOT FIT', 640, 1090, 78, h(PAPER), 0xFF000000)
    punch(cv, 'THROAT: TOO NARROW', 540, 1560, 72, ramp(c.lt, 0.55), AMBER, -3)


def board_true(cv, c):
    wall(cv, c.t)
    pinned(cv, 550, 540, 640, 720, 2)
    cv.save()
    cv.translate(550, 540)
    cv.rotate(2)
    photo(cv, 'diver', 0, 28, 570, 590, (0.5, 0.3))
    cv.restore()
    punch(cv, 'TRUE', 540, 800, 180, ramp(c.lt, 0.25, 0.12), RED, -13, (300, 110))
    card(cv, 'IN ITS MOUTH: YES', 420, 1085, 640, 150, -4, 60, ramp(c.lt, 0.5))
    card(cv, 'SWALLOWED: NO', 690, 1560, 560, 150, 4, 60, ramp(c.lt, 0.68), PAPER)


SHOTS = {f.__name__: f for f in (clock30, board_whale, black, shark_q, family, throat, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(cv, c, text, x, y, size, at=0.25, col='FFB000', ang=-5):
    punch(cv, text, x, y, size, ramp(c.lt, at, 0.12), col, ang)


def rays(cv, c, a=0.1):
    """Shafts of sunlight slanting down through shallow water, and drifting motes."""
    for i in range(5):
        x = 120 + i * 230 + 50 * math.sin(c.t * 0.7 + i * 1.9)
        wdt = 70 + 40 * math.sin(c.t * 0.9 + i)
        p = skia.Path()
        p.moveTo(x, -20)
        p.lineTo(x + wdt, -20)
        p.lineTo(x + wdt - 330, 1500)
        p.lineTo(x - 420, 1500)
        p.close()
        pa = skia.Paint(AntiAlias=True)
        pa.setShader(skia.GradientShader.MakeLinear([(0, 0), (0, 1500)], [Wd.alpha(h('E8FFF4'), a * (0.7 + 0.3 * math.sin(c.t * 1.3 + i))), 0x00E8FFF4]))
        cv.drawPath(p, pa)
    Wd.particles(cv, W, H, c.t, 40, Wd.alpha(h('E8FFF4'), 0.3), 13, size=(2, 5), drift=(-16, -18), wobble=18)


def murk(cv, c):
    Wd.particles(cv, W, H, c.t, 44, Wd.alpha(h('D8F6FF'), 0.28), 17, size=(2, 6), drift=(-26, 20), wobble=20)


def breath(cv, c):
    """Inside the mouth: a faint red pulse and drifting bubbles."""
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(Wd.alpha(h('7A1028'), 0.08 + 0.06 * math.sin(c.t * 5.2))))
    Wd.particles(cv, W, H, c.t, 16, Wd.alpha(h('FFE0E6'), 0.25), 5, size=(2, 5), drift=(6, -30), wobble=14)


def mist(cv, c):
    """Sea spray blowing across the lens."""
    Wd.particles(cv, W, H, c.t * 2.5, 36, Wd.alpha(h('FFFFFF'), 0.4), 21, size=(2, 7), drift=(-120, 60), wobble=26)


def name(cv, c):
    rays(cv, c)
    stamp(cv, c, 'MICHAEL PACKARD', 540, 420, 84, 0.15, 'FFFFFF', 3)


def no_teeth(cv, c):
    breath(cv, c)
    stamp(cv, c, 'NO TEETH', 540, 430, 150, 0.35, 'FFB000', -5)


def breathing(cv, c):
    breath(cv, c)
    stamp(cv, c, 'STILL BREATHING', 540, 430, 96, 0.4, 'FFFFFF', -3)


def thirty(cv, c):
    mist(cv, c)
    stamp(cv, c, 'ABOUT 30 SECONDS', 540, 400, 84, 0.3, 'FFB000', -3)


def no_breaks(cv, c):
    stamp(cv, c, 'NO BROKEN BONES', 540, 420, 96, 0.35, 'FFB000', -4)


def same_day(cv, c):
    stamp(cv, c, 'HOME THE SAME DAY', 540, 430, 86, 0.3, 'FFFFFF', 3)


def accident(cv, c):
    rays(cv, c)
    stamp(cv, c, 'AN ACCIDENT', 540, 420, 130, 0.3, 'FFFFFF', -4)


def was_feeding(cv, c):
    rays(cv, c)
    stamp(cv, c, 'IT WAS FEEDING', 540, 430, 100, 0.25, 'FFB000', 3)


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h(AMBER), 0xFF000000)
        Wd.text_card(cv, 'CASE 004  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(gulp=murk, jaws_shut=murk, whale_wide=rays, spat=mist, descend=rays, sand_hunt=name, lobster_cu=rays, shoal=rays, shadow=murk,
            feel_dark=no_teeth, mouth_wide=breath, squeeze=breath, reg_cu=breathing, rook_quiet=breath, rise=rays, breach=mist, shake=mist,
            flung=thirty, splashdown=mist, ward=no_breaks, rook_door=same_day, feeding=accident, mouthful=was_feeding, throat_look=breath,
            signoff=closed)
