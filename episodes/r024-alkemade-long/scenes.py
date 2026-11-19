"""Case 024, the full case file (16:9) - Nicholas Alkemade, the rear gunner who fell about 18,000 feet without a parachute
on the night of 24 March 1944 and lived. The story is filmed in 3D (world3d.py). This file holds the flat inserts on a
1920x1080 canvas (a drawn diagram of the wind pushing the bombers off their course, a chalk drawing of what his
interrogators suspected, a typed sheet carrying the reported words of his certificate, and Rook's case board), the 2D
overlays drawn on top of 3D shots, and the thumbnail. Every card is a drawing made for this film: the diagram is not a
map and is marked as a diagram, the bomber shapes on it are generic, and the typed sheet is a plain re-setting of the
reported wording, not a copy of the original document. Captions run in a band around 86% of the height and the label
sits top right, so the cards keep both clear."""
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
ORANGE, AMBER, PAPER = h('FF7A1A'), h('FFB000'), h('EFE6CC')
CHALK = h('F0ECE0')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def plain(cv, s, x, y, size, color, weight=700, centre=True):
    f = font(size, weight)
    w = f.measureText(s)
    cv.drawTextBlob(skia.TextBlob(s, f), x - (w / 2 if centre else 0), y, P(color))
    return w


def push(cv, c, amount=0.1, sway=0.0):
    """A slow push in on a card (and a little sway), so a held card is never a still picture."""
    z = 1 + amount * c.k
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.rotate(sway * math.sin(c.t * 1.3))
    cv.translate(-W / 2 + 26 * math.sin(c.t * 0.9), -H / 2 + 14 * math.sin(c.t * 1.4))


def bomber_mark(cv, x, y, s, ang, col=INK):
    """A plain four-engined bomber seen from above, drawn as a flat shape. No markings."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    p = P(col)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-150, -18, 300, 36), 18, 18, p)                       # fuselage, nose to +x
    cv.drawPath(poly([(30, -20), (-10, -230), (-50, -230), (-40, -20)]), p)                     # wings
    cv.drawPath(poly([(30, 20), (-10, 230), (-50, 230), (-40, 20)]), p)
    cv.drawPath(poly([(-120, -16), (-150, -80), (-175, -80), (-160, -16)]), p)                 # tailplane
    cv.drawPath(poly([(-120, 16), (-150, 80), (-175, 80), (-160, 16)]), p)
    for yy in (-150, -80, 80, 150):
        cv.drawRoundRect(skia.Rect.MakeXYWH(-5, yy - 12, 60, 24), 10, 10, p)
    cv.restore()


# ---------------------------------------------------------------- inserts
def wind_card(cv, c):
    """A drawn diagram, not a map: the planned way home as a dotted line; big wind arrows push a row of bomber shapes
    south of it, the way the strong wind that night pushed the returning bombers off their course."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2A3A')), (1, h('0E161E'))])
    cv.save()
    push(cv, c, 0.12, 0.5)
    cv.drawRect(skia.Rect.MakeXYWH(150 + 14, 70 + 18, 1620, 760), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(150, 70, 1620, 760), P(h('E8DFC4')))
    for i in range(12):
        Wd.glow(cv, 250 + 1400 * rn(i, 5), 140 + 600 * rn(i, 6), 110 + 140 * rn(i, 7), h('C8B890'), 0.3)
    for j in range(40):                                                   # the planned way home: dotted, east to west
        cv.drawCircle(1600 - 35 * j, 300, 6, P(INK))
    plain(cv, 'THE WAY HOME', 1300, 270, 40, INK, 900)
    k = ease(c.k * 1.3)
    for i in range(5):                                                    # wind arrows from the north
        x = 380 + 300 * i
        y0, y1 = 120 + 30 * rn(i, 8), lerp(260, 520, k) + 30 * rn(i, 9)
        cv.drawLine(x, y0, x - 40, y1, P(h('3A6E9A'), 22))
        cv.drawPath(poly([(x - 80, y1 - 10), (x + 2, y1 - 10), (x - 44, y1 + 60)]), P(h('3A6E9A')))
    plain(cv, 'STRONG WIND', 420, 170, 46, h('2A5A8A'), 900)
    for i in range(4):                                                    # the bombers drift south of the line
        x = 1450 - 300 * i - 260 * k
        y = 300 + (60 + 70 * i) * k + 12 * math.sin(c.t * 2 + i)
        bomber_mark(cv, x, y, 0.32, 180 + 8 * k)
    fit(cv, 'DIAGRAM, NOT A MAP', 1460, 790, 34, 520, 0xCCFFFFFF)
    if c.k > 0.5:
        fit(cv, 'OFF COURSE, OVER GERMANY', 760, 760, 58, 1000, AMBER)
    cv.restore()


def chalk_pine(cv, x, y, s, a=1.0):
    for i in range(4):
        w_, top = s * (150 - 30 * i), y - s * (120 + 95 * i)
        cv.drawPath(poly([(x - w_, top + s * 150), (x, top), (x + w_, top + s * 150)]), P(h('3E7A5E'), a=a))
        cv.drawPath(poly([(x - w_, top + s * 150), (x, top), (x + w_, top + s * 150)]), P(CHALK, 6, a=0.8 * a))
    cv.drawLine(x, y, x, y - s * 120, P(h('8A6A48'), 18 * s, a=a))


def spy_card(cv, c):
    """'Then he's a spy, and he's hidden it.' Drawn in chalk on a slate: a figure with a spade under the pines, a bundle of
    parachute going into a hole. Headed WHAT THEY SUSPECTED: this is the accusation, not what happened."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E2A2C')), (0.6, h('172022')), (1, h('0E1416'))])
    for i in range(80):
        x, y = W * rn(i, 1), H * rn(i, 2)
        cv.drawLine(x, y, x + 40 * rn(i, 3), y + 8 * rn(i, 4), P(CHALK, 2, a=0.07))
    cv.save()
    push(cv, c, 0.08, 0.3)
    fit(cv, 'WHAT THEY SUSPECTED', 720, 140, 74, 1000, AMBER)
    gy = 800
    chalk_pine(cv, 260, gy, 0.95)
    chalk_pine(cv, 1180, gy, 1.05)
    chalk_pine(cv, 720, gy - 60, 0.6, 0.6)
    cv.drawLine(80, gy, 1500, gy, P(CHALK, 8, a=0.9))
    k = ease(c.k / 0.75)
    hx0 = 860
    cv.drawPath(poly([(hx0, gy), (hx0 + 40, gy + 35), (hx0 + 230, gy + 35), (hx0 + 270, gy)]), P(h('0A0E10')))
    by = lerp(gy - 150, gy, k)
    cv.save()
    cv.clipRect(skia.Rect.MakeXYWH(0, 0, W, gy + 28))
    cv.drawOval(skia.Rect.MakeXYWH(hx0 + 50, by - 70, 170, 110), P(h('E8E0C8')))
    cv.drawOval(skia.Rect.MakeXYWH(hx0 + 50, by - 70, 170, 110), P(INK, 6))
    for i in range(4):
        cv.drawLine(hx0 + 80 + 36 * i, by - 66, hx0 + 90 + 30 * i, by + 36, P(h('B8AE90'), 5))
    cv.restore()
    dig = math.sin(c.t * 7)
    fx, fy = 620, gy
    s = 0.8
    cv.drawLine(fx - 20 * s, fy, fx - 10 * s, fy - 150 * s, P(CHALK, 18))
    cv.drawLine(fx + 40 * s, fy, fx + 10 * s, fy - 150 * s, P(CHALK, 18))
    cv.drawLine(fx, fy - 150 * s, fx + 70 * s, fy - 330 * s, P(CHALK, 26))
    cv.drawCircle(fx + 100 * s, fy - 380 * s, 36, P(CHALK))
    hx, hy = fx + 190 * s, fy - 230 * s + 22 * dig
    cv.drawLine(fx + 70 * s, fy - 320 * s, hx, hy, P(CHALK, 16))
    cv.drawLine(hx - 32, hy - 90, hx + 48, hy + 120, P(h('B88A58'), 11))
    cv.drawPath(poly([(hx + 24, hy + 112), (hx + 72, hy + 104), (hx + 80, hy + 172), (hx + 40, hy + 184)]), P(h('9AA4AC')))
    if c.k > 0.35:
        q = 1.5 - 0.5 * ease((c.k - 0.35) / 0.12)
        cv.save()
        cv.translate(1500, 420)
        cv.rotate(-8)
        cv.scale(q, q)
        Wd.text_card(cv, 'SPY?', 0, 0, 200, h('E8483A'), 0xFF000000)
        cv.restore()
    cv.restore()


LINES = [('It has been investigated', 0.05), ('and corroborated by the', 0.12), ('German authorities that', 0.19), ('his claim is', 0.26)]


def cert_card(cv, c):
    """The typed sheet: the reported words of the certificate he was given, set plainly, with the witnesses' lines left blank.
    The key phrases are struck in as they are spoken."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A2420')), (0.5, h('1E1A16')), (1, h('120F0C'))])
    k = ease(min(1, c.lt / 0.25))
    cv.save()
    push(cv, c, 0.06, 0.0)
    cv.translate(960, 440)
    cv.rotate(-1.5 + 0.8 * math.sin(c.t * 0.8))
    cv.scale(0.92 + 0.08 * k, 0.92 + 0.08 * k)
    cv.drawRect(skia.Rect.MakeXYWH(-560 + 14, -400 + 18, 1120, 800), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-560, -400, 1120, 800), P(PAPER))
    for i in range(5):
        cv.drawLine(-560, -400 + 180 * i + 30 * rn(i, 5), 560, -396 + 180 * i + 30 * rn(i, 6), P(h('D8CCAC'), 2, a=0.6))
    plain(cv, 'CERTIFICATE', 0, -310, 64, INK, 900)
    cv.drawLine(-220, -284, 220, -284, P(INK, 5))
    for i, (s, at_) in enumerate(LINES):
        if c.k > at_:
            plain(cv, s, 0 if i < 2 else 0, -210 + 60 * i, 46, h('2A2622'), 600)
    if c.k > 0.34:
        s = 1.4 - 0.4 * ease((c.k - 0.34) / 0.1)
        cv.save()
        cv.translate(0, 90)
        cv.scale(s, s)
        plain(cv, 'TRUE IN ALL RESPECTS', 0, 0, 92, h('B02A1E'), 900)
        cv.restore()
    if c.k > 0.55:
        plain(cv, 'a descent without a parachute', 0, 190, 46, INK, 600)
    for i, x in enumerate((-360, 0, 360)):                                # the three witnesses' lines, left blank
        if c.k > 0.7 + 0.06 * i:
            cv.drawLine(x - 140, 330, x + 140, 330, P(INK, 3))
            plain(cv, 'WITNESS', x, 365, 26, h('6A6052'), 700)
    cv.restore()
    Wd.particles(cv, W, H, c.t, 18, 0x44FFE8C8, 91, size=(2, 5), drift=(10, -14), wobble=14, twinkle=True)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('9CB2D0')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def board(cv, c):
    """Rook's board for this case: pine planks with knots, a photograph of the man in the dent in the snow pinned with a sprig
    of pine needles, and the case in three lines."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A1E14')), (1, h('120C08'))])
    cv.save()
    push(cv, c, 0.07, 0.4)
    for i in range(9):
        x = 30 + 210 * i
        cv.drawRect(skia.Rect.MakeXYWH(x, 40, 202, 1000), P((h('B88E5C'), h('AA8250'), h('C09662'))[i % 3]))
        for j in range(6):
            y = 60 + 960 * rn(i * 9 + j, 7)
            cv.drawLine(x + 20 + 150 * rn(i + j, 8), y, x + 30 + 150 * rn(i + j, 8), y + 120, P(h('8A6438'), 3, a=0.5))
        ky = 140 + 760 * rn(i, 9)
        cv.drawOval(skia.Rect.MakeXYWH(x + 60, ky, 70, 44), P(h('6E4A26')))
        cv.drawOval(skia.Rect.MakeXYWH(x + 76, ky + 10, 38, 24), P(h('4A2E14')))
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(620, 430)
    cv.scale(s, s)
    cv.rotate(-2.5)
    cv.drawRect(skia.Rect.MakeXYWH(-380 + 12, -330 + 16, 760, 660), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-380, -330, 760, 660), P(PAPER))
    photo(cv, 'snow', 0, -10, 700, 580, (0.5, 0.5))
    cv.restore()
    for x in (300, 940):
        cv.drawCircle(x, 120, 22, P(ORANGE))
        cv.drawCircle(x, 120, 22, P(INK, 5))
    for i in range(7):
        a = -2.4 + 0.3 * i
        cv.drawLine(940, 120, 940 + 130 * math.cos(a), 120 - 130 * math.sin(a), P(h('2E6A4A'), 7))
    if c.lt > 0.2:
        fit(cv, '18,000 FEET', 1430, 330, 96, 760, 0xFFFFFFFF)
    if c.lt > 0.4:
        fit(cv, 'NO PARACHUTE', 1430, 470, 96, 760, AMBER)
    if c.lt > 0.6:
        fit(cv, 'ONE TWISTED KNEE', 1430, 610, 70, 760, 0xFFFFFFFF)
    if c.lt > 0.8:
        q = 1.5 - 0.5 * ease((c.lt - 0.8) / 0.12)
        cv.save()
        cv.translate(880, 700)
        cv.rotate(-12)
        cv.scale(q, q)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-170, -78, 340, 132), 14, 14, P(h('2E9A4E'), 12))
        plain(cv, 'TRUE', 0, 34, 110, h('2E9A4E'), 900)
        cv.restore()
    cv.restore()


SHOTS = {f.__name__: f for f in (wind_card, spy_card, cert_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def sparks(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0xCCFFB040, 93, size=(3, 8), drift=(-40, 420), wobble=40, twinkle=True)
    Wd.particles(cv, W, H, c.t, 16, 0x88FF6A20, 95, size=(4, 10), drift=(-70, 300), wobble=60)


def rush(cv, c):
    """Falling: streaks of cloud and ice going up past the lens."""
    for i in range(30):
        x = W * rn(i, 11)
        y = H - ((c.t * (1100 + 700 * rn(i, 12)) + H * rn(i, 13)) % (H + 300))
        cv.drawLine(x, y, x + 6 * math.sin(i), y + 90 + 100 * rn(i, 14), P(h('DCEBFF'), 4, a=0.22))


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 56, 0xCCF4F8FF, 97, size=(3, 8), drift=(40, 120), wobble=30)


def night(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x66DCF0FF, 81, size=(2, 4), drift=(8, -5), wobble=8, twinkle=True)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x55FFE8C8, 99, size=(2, 5), drift=(12, -16), wobble=16, twinkle=True)


def mist(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x66FFF0E0, 101, size=(2, 6), drift=(30, -10), wobble=24, twinkle=True)


def pollen(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x88FFF4D8, 103, size=(2, 5), drift=(40, -12), wobble=20, twinkle=True)


def petals(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0xAAF6D8E0, 105, size=(4, 8), drift=(90, 60), wobble=40)


def closed(cv, c):
    snow(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(430, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 024', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(bomber_wide=sparks, turret_fire=sparks, chute_burn=sparks, backflip=sparks, rook_fall=rush, fighter=sparks, wing_fire=sparks, fall_wide=rush,
            rook_maths=rush, fall_close=rush, rook_gives_up=rush, trees_rush=rush, crash_branches=snow, snow_hole=snow, hole_up=snow, rook_measure=snow,
            limbs=snow, knee=snow, lantern=snow, room_wide=dust, gestapo_laugh=dust, rook_room=dust, spy_point=dust, he_points=dust, officer_writes=dust,
            man_smile=dust, rook_hat=dust, search_wood=snow, harness=snow, wreck=snow, chute_pack=mist, four_stones=mist, signoff=closed,
            garden_wide=pollen, garden_close=pollen, field_dusk=dust, crew_seven=dust, takeoff=dust, stream=night, turret_calm=night, rack_calm=dust,
            gunner_face=sparks, cigarette=snow, whistle=snow, hospital=dust, witnesses=dust, camp_famous=dust, camp_wire=snow, long_march=snow,
            home_may=petals, works=mist, tv_studio=dust, plaque=pollen)


def THUMB(cv, c):
    """1280x720: the 3D still (the gunner falling on his back through the night, the burning bomber small above him) and the
    hook on the left, over the dark sky."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0A1428'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(720, 0), (0, 0)], [0x00000000, 0xC8000000])))
    fit(cv, 'NO', 300, 250, 150, 520, 0xFFFFFFFF)
    fit(cv, 'PARACHUTE', 300, 400, 120, 520, AMBER)
    fit(cv, '18,000 FT', 300, 530, 90, 520, 0xFFFFFFFF)
