"""Case 018 - Tami Oldham (later Ashcraft), who sailed a dismasted yacht about 1,500 miles to Hawaii alone in 1983.
The story is filmed in 3D (world3d.py). This file holds the one flat insert (a chart pinned to Rook's case board,
used twice: the plan, and the plan carried out) and the 2D overlays drawn on top of 3D shots (rain, spray, dust
in the cabin light, a count of hours, a count of days, the sign-off). The chart is a drawing made for this film,
with approximate positions; it reproduces no real chart, photograph or document."""
import math

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
ORANGE, AMBER, PAPER = h('FF7A1A'), h('FFB000'), h('EFE6CC')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def plain(cv, s, x, y, size, color, weight=700, centre=True):
    f = font(size, weight)
    w = f.measureText(s)
    cv.drawTextBlob(skia.TextBlob(s, f), x - (w / 2 if centre else 0), y, P(color))
    return w


# ---------------------------------------------------------------- the chart on Rook's board
def xy(lon, lat):
    return 110 + (lon + 163) / 51 * 860, 1090 - (lat + 22) / 58 * 760


HILO, SDG, TAH, STORM = xy(-155.1, 19.7), xy(-117.2, 32.7), xy(-149.5, -17.5), xy(-131.5, 15.5)


def chart(cv, c):
    """A sea chart on cork, pinned at the corners: Tahiti at the bottom, San Diego top right, Hawaii top left. A dashed line runs up from Tahiti to a
    red cross where the storm hit; from the cross an orange line grows west to Hawaii. On its second use the line is complete and the count is stamped."""
    done = bool(c.prm.get('done'))
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2A1C')), (1, h('1A120C'))])
    for i in range(240):
        cv.drawCircle(W * rn(i, 1), H * rn(i, 2), 3 + 5 * rn(i, 3), P(h('5A4028'), a=0.5))
    cv.save()
    cv.translate(540, 700)
    cv.rotate(-1.5 + 0.4 * math.sin(c.t * 1.3))
    cv.translate(-540, -700)
    cv.drawRect(skia.Rect.MakeXYWH(72, 262, 960, 900), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(60, 250, 960, 900), P(h('D6E6EA')))
    for i in range(1, 8):
        cv.drawLine(60 + 120 * i, 250, 60 + 120 * i, 1150, P(h('9EBAC4'), 2, a=0.7))
        if i < 8:
            cv.drawLine(60, 250 + 112 * i, 1020, 250 + 112 * i, P(h('9EBAC4'), 2, a=0.7))
    cv.drawPath(poly([(1020, 250), (900, 250), (930, 330), (985, 420), (1020, 470)]), P(h('C9B98A')))      # a corner of the American coast
    cv.drawPath(poly([(1020, 250), (900, 250), (930, 330), (985, 420), (1020, 470)], False), P(h('7A6A44'), 4))
    for dx, dy, r in ((0, 0, 17), (-40, -26, 9), (-62, -40, 8), (-88, -52, 7)):                             # Hawaii: a chain of dots
        cv.drawCircle(HILO[0] + dx, HILO[1] + dy, r, P(h('5E8A5A')))
    cv.drawCircle(TAH[0], TAH[1], 11, P(h('5E8A5A')))
    plain(cv, 'HAWAII', HILO[0] - 20, HILO[1] - 86, 44, INK, 900)
    plain(cv, 'TAHITI', TAH[0] + 20, TAH[1] + 62, 40, INK, 900)
    plain(cv, 'SAN DIEGO', SDG[0] - 150, SDG[1] + 70, 36, INK, 900)
    cv.drawCircle(SDG[0], SDG[1], 9, P(INK))
    n = 12
    for i in range(n):                                                                                     # the course they were on
        a, b = i / n, (i + 0.55) / n
        cv.drawLine(lerp(TAH[0], STORM[0], a), lerp(TAH[1], STORM[1], a), lerp(TAH[0], STORM[0], b), lerp(TAH[1], STORM[1], b), P(INK, 6, a=0.75))
    for i in range(6):
        a, b = i / 6, (i + 0.5) / 6
        cv.drawLine(lerp(STORM[0], SDG[0], a), lerp(STORM[1], SDG[1], a), lerp(STORM[0], SDG[0], b), lerp(STORM[1], SDG[1], b), P(INK, 4, a=0.28))
    s = 22
    cv.drawLine(STORM[0] - s, STORM[1] - s, STORM[0] + s, STORM[1] + s, P(h('C8322A'), 10))
    cv.drawLine(STORM[0] - s, STORM[1] + s, STORM[0] + s, STORM[1] - s, P(h('C8322A'), 10))
    plain(cv, 'THE STORM', STORM[0] + 40, STORM[1] + 60, 34, h('C8322A'), 900)
    g = 1.0 if done else ease((c.lt - 0.25) / 0.9)
    ex, ey = lerp(STORM[0], HILO[0], g), lerp(STORM[1], HILO[1], g)
    cv.drawLine(STORM[0], STORM[1], ex, ey, P(ORANGE, 14))
    cv.drawCircle(ex, ey, 15, P(ORANGE))
    cv.drawCircle(ex, ey, 15, P(INK, 4))
    plain(cv, 'POSITIONS APPROXIMATE', 540, 1128, 24, h('5A6E76'), 700)
    for x, y in ((90, 280), (990, 280), (90, 1120), (990, 1120)):
        cv.drawCircle(x, y, 16, P(ORANGE))
        cv.drawCircle(x, y, 16, P(INK, 4))
    cv.restore()
    if done:
        q = 1.5 - 0.5 * ease(c.lt / 0.14)
        cv.save()
        cv.translate(540, 1640)
        cv.scale(q, q)
        fit(cv, '41 DAYS', 0, 0, 170, 900, AMBER)
        cv.restore()
        if c.lt > 0.3:
            fit(cv, 'ALONE', 540, 1780, 110, 900, 0xFFFFFFFF)
    else:
        if c.lt > 0.3:
            fit(cv, '1,500 MILES', 540, 1640, 150, 940, AMBER)
        if c.lt > 0.75:
            fit(cv, 'TO HAWAII', 540, 1770, 100, 900, 0xFFFFFFFF)


SHOTS = {f.__name__: f for f in (chart,)}


# ---------------------------------------------------------------- overlays on the 3D shots
def rain(cv, c):
    for i in range(70):
        x = (W * rn(i, 11) + c.t * (900 + 500 * rn(i, 12))) % (W + 200) - 100
        y = (H * rn(i, 13) + c.t * (2600 + 900 * rn(i, 14))) % (H + 200) - 100
        cv.drawLine(x, y, x + 34, y + 110, P(h('DCE8F0'), 3, a=0.3))
    if (c.t * 3.1) % 1 < 0.1:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(0x30FFFFFF))


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 16, 0x66FFFFFF, 61, size=(2, 5), drift=(-90, 30), wobble=30, twinkle=True)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x55E8F4FF, 63, size=(2, 5), drift=(8, 18), wobble=18, twinkle=True)


def hours(cv, c):
    """Out cold: the hours go by in the corner of the frame."""
    motes(cv, c)
    n = int(lerp(1, 27, ease(c.k * 1.15)))
    fit(cv, f'{n} H', 540, 430, 190, 800, AMBER if n >= 27 else 0xFFFFFFFF)


def days(cv, c):
    spray(cv, c)
    n = int(lerp(2, 41, ease(c.k * 1.1)))
    fit(cv, f'DAY {n}', 540, 430, 170, 860, AMBER if n >= 41 else 0xFFFFFFFF)


def stars(cv, c):
    Wd.particles(cv, W, H, c.t, 10, 0x44FFFFFF, 67, size=(2, 4), drift=(-30, 10), wobble=20, twinkle=True)


def closed(cv, c):
    if c.lt > 0.3:
        k = min(1, (c.lt - 0.3) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 018', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(wake=motes, out_cold=hours, pump=motes, bilge_watch=motes, storm_wave=rain, storm_roll=rain, hatch_out=spray, helm_empty=spray, rook_mast=spray,
            cleat_line=spray, rook_ring=spray, stern_alone=spray, engine_dead=spray, pole_up=spray, sail_fill=spray, wide_sail=spray, plane_over=spray,
            wave_up=spray, plane_gone=spray, rook_glass=spray, sextant=spray, rook_sun=spray, helm_days=days, ship_light=stars, her_light=stars,
            tow_in=stars, rook_hatjump=stars, sloop=spray, signoff=closed)
