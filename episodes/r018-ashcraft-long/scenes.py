"""Case 018, the full case file (16:9) - Tami Oldham (later Ashcraft), who sailed a dismasted yacht about 1,500 miles to
Hawaii alone in 1983. The story is filmed in 3D (world3d.py). This file holds the flat inserts on a 1920x1080 canvas
(Rook's case file, a drawn chart of the planned voyage, the same chart with the new course to Hawaii, a drawing of her
plan to sail north to 19 degrees and then west, and Rook's case board), the 2D overlays drawn on top of 3D shots, and
the thumbnail. Every card is a drawing made for this film: the charts are marked as drawings with approximate
positions and reproduce no real chart, photograph, document or logo. Captions run in a band around 86% of the height
and the label sits top right, so the cards keep both clear."""
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
ORANGE, AMBER, PAPER, RED = h('FF7A1A'), h('FFB000'), h('EFE6CC'), h('C8322A')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 41.71 + j * 93.17) * 31415.93) % 1


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
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


def plain(cv, s, x, y, size, color, weight=800):
    f = font(size, weight)
    w = f.measureText(s)
    cv.drawTextBlob(skia.TextBlob(s, f), x - w / 2, y, P(color))


def push(cv, c, amount=0.1, sway=0.0):
    """A slow push in on a card (and a little sway), so a held card is never a still picture."""
    z = 1 + amount * c.k
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.rotate(sway * math.sin(c.t * 1.3))
    cv.translate(-W / 2 + 22 * math.sin(c.t * 0.9), -H / 2 + 12 * math.sin(c.t * 1.4))


def teak(cv, seed=1):
    """Rook's board for this case: weathered teak deck planks with black seams."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('7A5232')), (0.5, h('6A4628')), (1, h('4A3020'))])
    for i in range(12):
        y = 90 * i
        cv.drawRect(skia.Rect.MakeXYWH(0, y, W, 86), P((h('8A6038'), h('7E5634'), h('86603A'))[i % 3]))
        cv.drawRect(skia.Rect.MakeXYWH(0, y + 86, W, 4), P(h('1A120C')))
        for j in range(8):
            x = (rn(i, seed + j) * W)
            cv.drawLine(x, y + 10 + 60 * rn(j, i), x + 200 + 300 * rn(i, j), y + 14 + 60 * rn(j, i), P(h('5A3E24'), 3, a=0.5))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x99000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.restore()


def pins(cv, pts):
    for x, y in pts:
        cv.drawCircle(x, y, 20, P(ORANGE))
        cv.drawCircle(x, y, 20, P(INK, 5))


def photo(cv, name, x, y, w_, h_):
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('2A5E70')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) / 2, (ih - sh) / 2, sw, sh), dst, skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def typed(cv, lines, x, y0, step, c, rate=0.5, sizes=None, cols=None, maxw=1000):
    shown = c.lt / rate
    for i, line in enumerate(lines):
        if shown < i:
            break
        n = max(1, int(len(line) * min(1.0, (shown - i) * 1.6)))
        left(cv, line[:n], x, y0 + step * i, (sizes or [76] * 9)[i], (cols or [0xFFFFFFFF] * 9)[i], maxw=maxw)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x66FFE8C0, 73, size=(3, 7), drift=(100, -40), wobble=30, twinkle=True)


# ---------------------------------------------------------------- the case file
FILE = ('TAMI OLDHAM, 23', 'FROM SAN DIEGO', 'YACHT HAZANA', 'TAHITI TO SAN DIEGO, 1983')


def file_card(cv, c):
    """Rook's case file: a pinned card with a drawn two-masted yacht, and four lines typed onto the teak beside it."""
    cv.save()
    push(cv, c, 0.06, 0.3)
    teak(cv, 3)
    card(cv, 420, 430, 460, 520, -3)
    cv.save()
    cv.translate(420, 420)
    cv.rotate(-3)
    cv.drawPath(poly([(-160, 90), (150, 90), (120, 140), (-130, 140)]), P(h('2E5E8E')))          # a drawn ketch, no name
    cv.drawPath(poly([(-160, 90), (150, 90), (120, 140), (-130, 140)], False), P(INK, 6))
    cv.drawLine(-20, 90, -20, -170, P(INK, 7))
    cv.drawLine(80, 90, 80, -60, P(INK, 6))
    cv.drawPath(poly([(-14, -160), (-14, 70), (100 - 30, 70)]), P(0xFFFFFFFF))
    cv.drawPath(poly([(-14, -160), (-14, 70), (70, 70)], False), P(INK, 5))
    cv.drawPath(poly([(-26, -150), (-150, 80), (-30, 80)]), P(0xFFF4EEDC))
    cv.drawPath(poly([(-26, -150), (-150, 80), (-30, 80)], False), P(INK, 5))
    cv.drawPath(poly([(86, -50), (86, 70), (140, 70)]), P(0xFFFFFFFF))
    cv.drawPath(poly([(86, -50), (86, 70), (140, 70)], False), P(INK, 5))
    for i in range(4):
        cv.drawLine(-200 + 100 * i, 175 + 6 * math.sin(c.t * 2 + i), -150 + 100 * i, 175 - 6 * math.sin(c.t * 2 + i), P(h('2E5E8E'), 6))
    fit(cv, 'CASE 018', 0, 240, 56, 360, h('2A2E38'), None)
    cv.restore()
    pins(cv, ((250, 190), (590, 180)))
    left(cv, 'CASE FILE', 760, 200, 50, 0xCCFFFFFF)
    typed(cv, FILE, 740, 320, 130, c, 0.45, [90, 72, 72, 66], [AMBER, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF], 1060)
    cv.restore()
    dust(cv, c)


# ---------------------------------------------------------------- the chart (a drawing, not a real chart)
def cxy(lon, lat):
    """Longitude/latitude to the chart card: roughly 162 W to 112 W, 22 S to 36 N."""
    return 300 + (lon + 162) / 50 * 1320, 900 - (lat + 22) / 58 * 760


TAH, SDG, HILO, STORM = cxy(-149.5, -17.5), cxy(-117.2, 32.7), cxy(-155.1, 19.7), cxy(-131.5, 15.5)


def chart_base(cv, c, amount=0.12):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2A1C')), (1, h('1A120C'))])
    push(cv, c, amount, 0.4)
    card(cv, 960, 520, 1600, 880, -0.8, h('D6E6EA'))
    for i in range(1, 12):
        cv.drawLine(160 + 133 * i, 80, 160 + 133 * i, 960, P(h('9EBAC4'), 2, a=0.7))
    for j in range(1, 7):
        cv.drawLine(160, 80 + 125 * j, 1760, 80 + 125 * j, P(h('9EBAC4'), 2, a=0.7))
    cv.drawPath(poly([(1760, 80), (1560, 80), (1600, 230), (1680, 400), (1760, 470)]), P(h('C9B98A')))     # a corner of coast, not a real outline
    cv.drawPath(poly([(1760, 80), (1560, 80), (1600, 230), (1680, 400), (1760, 470)], False), P(h('7A6A44'), 4))
    for dx, dy, r in ((0, 0, 20), (-45, -28, 11), (-72, -44, 9), (-100, -58, 8)):
        cv.drawCircle(HILO[0] + dx, HILO[1] + dy, r, P(h('5E8A5A')))
    cv.drawCircle(TAH[0], TAH[1], 13, P(h('5E8A5A')))
    cv.drawCircle(SDG[0], SDG[1], 11, P(INK))
    plain(cv, 'HAWAII', HILO[0] - 40, HILO[1] - 90, 46, INK, 900)
    plain(cv, 'TAHITI', TAH[0] + 150, TAH[1] - 24, 46, INK, 900)
    plain(cv, 'SAN DIEGO', SDG[0] - 70, SDG[1] + 70, 42, INK, 900)
    plain(cv, 'DRAWING, POSITIONS APPROXIMATE', 1390, 150, 26, h('5A6E76'), 700)
    pins(cv, ((200, 120), (1720, 120), (200, 920), (1720, 920)))


def dashes(cv, a, b, n, col, w, alpha=1.0, upto=1.0):
    for i in range(n):
        p, q = i / n, (i + 0.55) / n
        if p > upto:
            break
        q = min(q, upto)
        cv.drawLine(lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[0], b[0], q), lerp(a[1], b[1], q), P(col, w, a=alpha))


def route_card(cv, c):
    """The job: a dotted course grows from Tahiti up to San Diego, a small drawn ketch travelling along it; ABOUT 4,000 MILES."""
    cv.save()
    chart_base(cv, c)
    g = ease((c.lt - 0.2) / 1.6)
    dashes(cv, TAH, SDG, 22, INK, 7, 0.85, g)
    x, y = lerp(TAH[0], SDG[0], g), lerp(TAH[1], SDG[1], g)
    cv.drawCircle(x, y, 16, P(ORANGE))
    cv.drawCircle(x, y, 16, P(INK, 4))
    if c.lt > 0.8:
        fit(cv, 'ABOUT 4,000 MILES', 1030, 600, 70, 700, AMBER)
    cv.restore()


def hawaii_card(cv, c):
    """Where now: the course stops at a red cross; the leg to San Diego is struck through; an orange line grows west to Hawaii. 1,500 MILES."""
    cv.save()
    chart_base(cv, c, 0.1)
    dashes(cv, TAH, STORM, 14, INK, 6, 0.75)
    dashes(cv, STORM, SDG, 8, INK, 5, 0.3)
    s = 26
    cv.drawLine(STORM[0] - s, STORM[1] - s, STORM[0] + s, STORM[1] + s, P(RED, 11))
    cv.drawLine(STORM[0] - s, STORM[1] + s, STORM[0] + s, STORM[1] - s, P(RED, 11))
    plain(cv, 'THE STORM', STORM[0] + 20, STORM[1] + 70, 36, RED, 900)
    k1 = ease((c.lt - 0.2) / 0.4)
    mx, my = lerp(STORM[0], SDG[0], 0.55), lerp(STORM[1], SDG[1], 0.55)
    if k1 > 0:
        cv.drawLine(mx - 40, my - 40 * k1, mx - 40 + 80 * k1, my + 40 * k1 - 40 * (1 - k1), P(RED, 10))
    g = ease((c.lt - 0.6) / 1.2)
    ex, ey = lerp(STORM[0], HILO[0], g), lerp(STORM[1], HILO[1], g)
    cv.drawLine(STORM[0], STORM[1], ex, ey, P(ORANGE, 14))
    cv.drawCircle(ex, ey, 15, P(ORANGE))
    cv.drawCircle(ex, ey, 15, P(INK, 4))
    if c.lt > 1.0:
        fit(cv, '1,500 MILES', 760, 640, 84, 560, AMBER)
    cv.restore()


def lat_card(cv, c):
    """Her plan: from the storm position a line runs north up to a dashed line marked 19 N, turns left, and runs west along it to Hawaii."""
    cv.save()
    chart_base(cv, c, 0.08)
    y19 = cxy(-140, 19.0)[1]
    dashes(cv, (160, y19), (1760, y19), 40, h('2E5E8E'), 5, 0.8)
    plain(cv, '19 N', 1640, y19 - 22, 44, h('2E5E8E'), 900)
    s = 20
    cv.drawLine(STORM[0] - s, STORM[1] - s, STORM[0] + s, STORM[1] + s, P(RED, 9))
    cv.drawLine(STORM[0] - s, STORM[1] + s, STORM[0] + s, STORM[1] - s, P(RED, 9))
    corner = (STORM[0], y19)
    g1 = ease((c.lt - 0.15) / 0.7)
    cv.drawLine(STORM[0], STORM[1], STORM[0], lerp(STORM[1], y19, g1), P(ORANGE, 14))
    g2 = ease((c.lt - 0.85) / 1.0)
    if g2 > 0:
        cv.drawLine(corner[0], corner[1], lerp(corner[0], HILO[0] + 30, g2), y19, P(ORANGE, 14))
    tip = (STORM[0], lerp(STORM[1], y19, g1)) if g2 <= 0 else (lerp(corner[0], HILO[0] + 30, g2), y19)
    cv.drawCircle(tip[0], tip[1], 15, P(ORANGE))
    cv.drawCircle(tip[0], tip[1], 15, P(INK, 4))
    if c.lt > 0.5:
        left(cv, '1. NORTH TO 19', 1060, 520, 58, 0xFFFFFFFF, maxw=600)
    if c.lt > 1.2:
        left(cv, '2. TURN LEFT, WEST', 1060, 620, 58, AMBER, maxw=600)
    cv.restore()


def board(cv, c):
    """Rook's board for this case: two photographs (the ketch at the quay in Papeete; the wreck under her one small sail) and the count."""
    cv.save()
    push(cv, c, 0.07, 0.4)
    teak(cv, 5)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    for (x, y, ang, name) in ((450, 430, -2.5, 'quay'), (1040, 470, 3.0, 'thumb')):
        cv.save()
        cv.translate(x, y)
        cv.scale(s, s)
        card(cv, 0, 0, 560, 440, ang)
        cv.rotate(ang)
        photo(cv, name, 0, -10, 510, 380)
        cv.restore()
    pins(cv, ((280, 220), (620, 220), (870, 250), (1210, 260)))
    if c.lt > 0.25:
        left(cv, '41 DAYS', 1390, 330, 84, AMBER, maxw=440)
    if c.lt > 0.45:
        left(cv, '1,500 MILES', 1390, 450, 64, 0xFFFFFFFF, maxw=440)
    if c.lt > 0.65:
        left(cv, 'ALONE', 1390, 570, 64, 0xFFFFFFFF, maxw=440)
    cv.restore()
    dust(cv, c)


SHOTS = {f.__name__: f for f in (file_card, route_card, hawaii_card, lat_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, 90, 0x66E8ECF0, -0.25, 2200, 6, 90)
    if (c.t * 3.1) % 1 < 0.08:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(0x26FFFFFF))


def spray(cv, c):
    Wd.particles(cv, W, H, c.t, 40, 0x77EAF6FF, 85, size=(3, 8), drift=(-260, 60), wobble=40)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x55E8F4FF, 63, size=(2, 5), drift=(8, 18), wobble=18, twinkle=True)


def glint(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0x88FFFFFF, 87, size=(2, 5), drift=(24, -12), wobble=18, twinkle=True)


def stars(cv, c):
    Wd.particles(cv, W, H, c.t, 16, 0x44FFFFFF, 67, size=(2, 4), drift=(-30, 10), wobble=20, twinkle=True)


def hours(cv, c):
    """Out cold: the hours go by in the corner of the frame (kept out of the caption band and the label)."""
    motes(cv, c)
    n = int(lerp(1, 27, ease(c.k * 1.15)))
    fit(cv, f'{n} H', 1560, 420, 150, 500, AMBER if n >= 27 else 0xFFFFFFFF)


def days(cv, c):
    spray(cv, c)
    n = int(lerp(7, 40, ease(c.k * 1.1)))
    fit(cv, f'DAY {n}', 1540, 420, 120, 520, 0xFFFFFFFF)


def closed(cv, c):
    glint(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(430, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 018', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(wake=motes, out_cold=hours, pump=motes, bilge_watch=motes, storm_wave=rain, storm_roll=rain, reef_run=rain, clouds_build=spray,
            hatch_out=spray, helm_empty=spray, rook_mast=spray, cleat_line=spray, rook_ring=spray, stern_alone=spray, engine_dead=spray,
            pole_up=spray, sail_fill=spray, wide_sail=spray, plane_over=spray, wave_up=spray, rook_glass=spray, sextant=glint, rook_sun=glint,
            helm_days=days, ship_light=stars, her_light=stars, tow_in=stars, rook_hatjump=stars, sloop=spray, pendant=glint, line_dawn=glint,
            rook_wrong=glint, signoff=closed, harbour_wide=glint, quay=glint, quay_load=glint, sail_out=spray, easy_sail=glint, radio_chart=motes,
            hatch_below=rain, hear_shout=motes, tumble=motes, radio_dead=motes, beacon=motes, tins_count=motes, log_write=motes,
            shirt_night=motes, voice_helm=stars, hilo_quay=glint, desk_write=motes, book_close=motes)


def THUMB(cv, c):
    """1280x720: the 3D still (the wreck under its one small sail, her at the wheel, left of centre) and the hook on the right, over open sky and sea."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('3A6078'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(640, 0), (1280, 0)], [0x00000000, 0xB0000000])))
    Wd.text_card(cv, '41 DAYS', 1010, 190, 120, AMBER, 0xFF000000)
    Wd.text_card(cv, 'ALONE', 1010, 330, 130, 0xFFFFFFFF, 0xFF000000)
