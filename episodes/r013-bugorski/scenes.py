"""Case 013 - Anatoli Bugorski. The story is filmed in 3D (world3d.py). This file holds the flat inserts (the drawn
path of the beam through a head, Rook's case board on a sheet of graph paper, the burst of light, the dose gauge)
and the 2D overlays drawn on top of 3D shots (snow, the white-out, the muted ear, the sign-off). Every card is a
drawing made for this film; none of them reproduces a real document, medical image, photograph or logo, and the
gauge carries no figures because the sources disagree on them."""
import math
import os

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F0E8D2'), h('D8362A'), h('3EC46A')
BEAM, DEEP = h('D6E6FF'), h('0A1424')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) pinned to the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('5A7A9A')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def graph_board(cv):
    """Rook's board for this case: a big sheet of green graph paper clipped to a steel plate."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('2A303A')))
    for i in range(-H, W, 46):
        cv.drawLine(i, 0, i + H * 0.25, H, P(0x14FFFFFF, 10))
    cv.drawRect(skia.Rect.MakeLTRB(60, 90, W - 60, H - 70), P(h('DCE8D4')))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(60, 90, W - 60, H - 70))
    for i in range(0, W, 32):
        cv.drawLine(i, 0, i, H, P(h('7FB08A'), 4 if i % 160 == 0 else 1.5, a=0.55))
    for j in range(0, H, 32):
        cv.drawLine(0, j, W, j, P(h('7FB08A'), 4 if j % 160 == 0 else 1.5, a=0.55))
    cv.restore()
    for x in (300, 780):                                         # two bulldog clips
        cv.drawRect(skia.Rect.MakeXYWH(x - 70, 40, 140, 100), P(h('8E96A4')))
        cv.drawRect(skia.Rect.MakeXYWH(x - 70, 40, 140, 100), P(h('1B1E26'), 6))
        cv.drawCircle(x, 70, 16, P(h('1B1E26')))
    for x, y in ((40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)):
        cv.drawCircle(x, y, 16, P(h('8E96A4')))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.5, 0x00000000), (1, 0x55000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, tape=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if tape:
        for sx in (-1, 1):
            cv.save()
            cv.translate(sx * (w_ / 2 - 30), -h_ / 2 + 14)
            cv.rotate(sx * 38)
            cv.drawRect(skia.Rect.MakeXYWH(-70, -22, 140, 44), P(ORANGE, a=0.85))
            cv.restore()
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=64):
    card(cv, x, y, w_, h_, ang, col, tape=False)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    for i, s in enumerate(lines):
        fit(cv, s, 0, (i - (len(lines) - 1) / 2) * size * 1.12 + size * 0.36, size, w_ - 50, INK, None)
    cv.restore()


def stamp(cv, s, x, y, ang, k, size=150, col=RED):
    """A rubber stamp that slams down (k 0..1)."""
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    tw = f.measureText(s)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    sc = 2.3 - 1.3 * k
    cv.scale(sc, sc)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-tw / 2 - 30, -size * 0.62, tw + 60, size * 1.2), 18, 18, P(col, 14, a=k))
    cv.drawString(s, -tw / 2, size * 0.36, f, P(col, a=k))
    cv.restore()


def head_profile(cx, cy, s):
    """Side view of a head facing right, about 5.4*s wide. A plain outline, nobody's likeness."""
    pts = [(-0.4, -3.0), (1.0, -2.8), (1.9, -2.0), (2.25, -0.9), (2.2, -0.3), (2.95, 0.75), (2.3, 0.95), (2.35, 1.5), (2.1, 1.75), (2.2, 2.2),
           (1.9, 2.9), (0.9, 3.05), (0.5, 3.3), (0.5, 4.3), (-1.7, 4.3), (-1.6, 2.6), (-2.4, 1.4), (-2.75, -0.3), (-2.4, -1.8), (-1.6, -2.6)]
    return poly([(cx + x * s, cy + y * s) for x, y in pts])


def arrow(cv, x0, y0, x1, y1, col, w=22, k=1.0):
    x1, y1 = lerp(x0, x1, k), lerp(y0, y1, k)
    cv.drawLine(x0, y0, x1, y1, P(col, w))
    a = math.atan2(y1 - y0, x1 - x0)
    s = w * 2.3
    cv.drawPath(poly([(x1 + s * math.cos(a), y1 + s * math.sin(a)), (x1 + s * math.cos(a + 2.4), y1 + s * math.sin(a + 2.4)),
                      (x1 + s * math.cos(a - 2.4), y1 + s * math.sin(a - 2.4))]), P(col))


# ------------------------------------------------------------------ flat inserts
def path_card(cv, c):
    """'In at the back. Out beside his nose.'"""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E1C34')), (1, h('04070E'))])
    for i in range(0, W + 1, 90):
        cv.drawLine(i, 0, i, H, P(h('1E4A7A'), 2, a=0.5))
    for j in range(0, H + 1, 90):
        cv.drawLine(0, j, W, j, P(h('1E4A7A'), 2, a=0.5))
    cx, cy, s = 520, 760, 118
    pop = 0.9 + 0.1 * ease(c.lt / 0.2)
    cv.save()
    cv.translate(cx, cy)
    cv.scale(pop, pop)
    cv.translate(-cx, -cy)
    hp = head_profile(cx, cy, s)
    cv.drawPath(hp, P(h('16365E')))
    cv.drawPath(hp, P(h('49C8FF'), 10))
    cv.drawOval(skia.Rect.MakeXYWH(cx - 2.2 * s, cy - 2.5 * s, 3.6 * s, 2.7 * s), P(h('2A4E86')))                    # the brain, as a plain shape
    cv.drawOval(skia.Rect.MakeXYWH(cx - 2.2 * s, cy - 2.5 * s, 3.6 * s, 2.7 * s), P(h('49C8FF'), 5, a=0.6))
    cv.drawCircle(cx + 1.45 * s, cy - 0.55 * s, 0.17 * s, P(h('CFF0FF')))                                           # eye
    y0, y1 = cy - 1.0 * s, cy + 0.72 * s                                                                           # beam: in at the back, out beside the nose
    xa, xb = cx - 2.62 * s, cx + 2.5 * s
    k_in = ease((c.lt - 0.1) / 0.35)
    k_th = ease((c.lt - 0.45) / 0.3)
    k_out = ease((c.lt - 0.95) / 0.35)
    glow = P(BEAM, 44, a=0.25)
    core = P(0xFFFFFFFF, 14)
    for pa in (glow, core):
        cv.drawLine(-20, y0 - (xa + 20) * 0.0, lerp(-20, xa, k_in), y0, pa)
        if k_th > 0:
            cv.drawLine(xa, y0, lerp(xa, xb, k_th), lerp(y0, y1, k_th), pa)
        if k_out > 0:
            cv.drawLine(xb, y1, lerp(xb, W + 20, k_out), lerp(y1, y1 + (W + 20 - xb) * (y1 - y0) / (xb - xa), k_out), pa)
    if k_in >= 1:
        cv.drawCircle(xa, y0, 26 + 8 * math.sin(c.t * 14), P(AMBER))
    if k_th >= 1:
        cv.drawCircle(xb, y1, 26 + 8 * math.sin(c.t * 14 + 1), P(AMBER))
    cv.restore()
    if c.lt > 0.12:
        k = ease((c.lt - 0.12) / 0.15)
        fit(cv, 'IN', 190, 470 + 30 * (1 - k), 150, 300, AMBER)
        arrow(cv, 190, 500, 215, 615, AMBER, 16, k)
    if c.lt > 0.95:
        k = ease((c.lt - 0.95) / 0.15)
        fit(cv, 'OUT', 880, 1080 - 30 * (1 - k), 150, 330, AMBER)
        arrow(cv, 880, 960, 835, 880, AMBER, 16, k)


def board_no(cv, c):
    graph_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 560)
    cv.scale(s, s)
    card(cv, 0, 0, 780, 660, -3)
    cv.rotate(-3)
    photo(cv, 'ring', 0, 20, 710, 560, (0.5, 0.5))
    cv.restore()
    if c.lt > 0.12:
        cv.drawLine(540, 895, 540, 950, P(RED, 8))
        note(cv, 540, 1040, 820, 190, 3, h('FFD866'), ['THROUGH HIS HEAD?'], 84)
    hp = head_profile(300, 1560, 34)
    cv.drawPath(hp, P(h('16365E')))
    cv.drawLine(120, 1528, 480, 1584, P(RED, 10))
    fit(cv, '1978', 760, 1600, 120, 400, INK, None)
    if c.k > 0.5:
        stamp(cv, 'NO CHANCE', 540, 600, -12, min(1, (c.k - 0.5) / 0.16), 132)


def suns(cv, c):
    """'Brighter than a thousand suns': rays bursting from one point until the frame is white."""
    cx, cy = 540, 760
    k = ease(c.lt / 0.9)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('04070E')))
    n = 28
    for i in range(n):
        a = i * 2 * math.pi / n + c.t * 0.9 * (1 if i % 2 else -1) * 0.25
        w = 0.05 + 0.05 * ((i * 7) % 5) / 5 + 0.1 * k
        r = 2600
        col = h('FFF4D8') if i % 2 else h('FFD890')
        cv.drawPath(poly([(cx, cy), (cx + r * math.cos(a - w), cy + r * math.sin(a - w)), (cx + r * math.cos(a + w), cy + r * math.sin(a + w))]),
                    P(col, a=0.35 + 0.5 * k))
    for i in range(46):                                           # small discs flying outward
        ph = (math.sin(i * 12.9898) * 43758.5453) % 1
        a = (math.sin(i * 78.233) * 43758.5453) % 1 * 6.283
        d = ((c.t * 0.9 + ph) % 1) * 1500
        cv.drawCircle(cx + d * math.cos(a), cy + d * math.sin(a), 6 + d * 0.022, P(h('FFFFFF'), a=0.9))
    Wd.glow(cv, cx, cy, 220 + 500 * k, 0xFFFFFFFF, 0.9)
    cv.drawCircle(cx, cy, 90 + 250 * k + 14 * math.sin(c.t * 30), P(0xFFFFFFFF))
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFFFFFFF, a=0.35 * ease((c.lt - 0.95) / 0.3)))


def dose(cv, c):
    """A drawn gauge with no figures: the needle swings far past the lethal mark."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('18222E')), (1, h('080B10'))])
    cx, cy, r = 540, 760, 380
    cv.drawCircle(cx, cy, r + 60, P(h('2B323A')))
    cv.drawCircle(cx, cy, r + 60, P(h('8E96A4'), 14))
    cv.drawCircle(cx, cy, r + 10, P(h('ECE6D2')))
    a0, a1 = math.radians(200), math.radians(-20)                 # scale from lower left over the top to lower right
    ang = lambda u: a0 + (a1 - a0) * u
    arcp = skia.Path()
    arcp.addArc(skia.Rect.MakeXYWH(cx - r + 60, cy - r + 60, 2 * r - 120, 2 * r - 120), -200, 16)
    cv.drawPath(arcp, P(GREEN, 46))
    arcp = skia.Path()
    arcp.addArc(skia.Rect.MakeXYWH(cx - r + 60, cy - r + 60, 2 * r - 120, 2 * r - 120), -184, 204)
    cv.drawPath(arcp, P(RED, 46))
    for i in range(21):
        a = ang(i / 20)
        r0 = r - 110 if i % 5 else r - 150
        cv.drawLine(cx + r0 * math.cos(a), cy - r0 * math.sin(a), cx + (r - 90) * math.cos(a), cy - (r - 90) * math.sin(a), P(INK, 8 if i % 5 == 0 else 4))
    al = ang(0.08)
    cv.drawLine(cx + (r - 190) * math.cos(al), cy - (r - 190) * math.sin(al), cx + (r - 20) * math.cos(al), cy - (r - 20) * math.sin(al), P(INK, 12))
    fit(cv, 'LETHAL', 330, 900, 56, 260, INK, None)
    swing = ease((c.lt - 0.3) / 0.5)
    u = lerp(0.0, 0.97, swing) + (0.012 * math.sin(c.t * 40) if swing >= 1 else 0)
    a = ang(u)
    cv.drawLine(cx - 40 * math.cos(a), cy + 40 * math.sin(a), cx + (r - 70) * math.cos(a), cy - (r - 70) * math.sin(a), P(h('15171C'), 22))
    cv.drawLine(cx - 40 * math.cos(a), cy + 40 * math.sin(a), cx + (r - 70) * math.cos(a), cy - (r - 70) * math.sin(a), P(ORANGE, 10))
    cv.drawCircle(cx, cy, 44, P(h('15171C')))
    fit(cv, 'THE DOSE', 540, 250, 120, 900, 0xFFFFFFFF)
    if c.lt > 0.75:
        k = ease((c.lt - 0.75) / 0.15)
        cv.save()
        cv.translate(540, 1580)
        cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
        Wd.text_card(cv, 'HUNDREDS OF TIMES', 0, 0, 92, AMBER, 0xFF000000)
        cv.restore()
        cv.drawRect(skia.Rect.MakeWH(W, H), P(RED, a=0.12 * (0.5 + 0.5 * math.sin(c.t * 12))))


def board_true(cv, c):
    graph_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 560)
    cv.scale(s, s)
    card(cv, 0, 0, 660, 720, 3)
    cv.rotate(3)
    photo(cv, 'bug', 0, 20, 590, 620, (0.5, 0.4))
    cv.restore()
    if c.lt > 0.12:
        cv.drawLine(540, 925, 540, 975, P(RED, 8))
        note(cv, 540, 1065, 760, 180, -3, h('FFD866'), ['BACK AT WORK'], 92)
    for i, s_ in enumerate(('1978', 'SAME ACCELERATOR')):
        if c.lt > 0.2 + i * 0.12:
            fit(cv, s_, 540, 1560 + i * 120, 96 if i == 0 else 78, 880, INK, None)
    if c.lt > 0.5:
        stamp(cv, 'TRUE', 720, 760, -10, min(1, (c.lt - 0.5) / 0.12), 150, GREEN)


SHOTS = {f.__name__: f for f in (path_card, board_no, suns, dose, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def closed(cv, c):
    snow(cv, c)
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 013  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 60, 0xCCF4F8FF, 5, size=(3, 8), drift=(-70, 230), wobble=26)


def whiteout(cv, c):
    """The flash: the 3D light alone cannot burn the frame out, so the overlay finishes it."""
    t0 = 0.24 if c.sh['kind'] == 'flash_side' else 0.14
    if c.prm.get('v') == 2:
        a = 0.16 + 0.1 * math.sin(c.t * 30)
    else:
        a = 0.9 * ease((c.lt - t0) / 0.08) * (1 - 0.9 * ease((c.lt - t0 - 0.1) / 0.4))
    if a > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFFFFFFF, a=min(0.95, a)))


def ear_mute(cv, c):
    """Sound waves reaching his left ear, struck out."""
    if c.lt < 0.3:
        return
    k = ease((c.lt - 0.3) / 0.2)
    x, y = 760, 560
    for i in range(3):
        r = 90 + i * 62 + 10 * math.sin(c.t * 8 - i)
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -42, 84)
        for col, w_ in ((0xFF000000, 30), (0xFFFFFFFF, 16)):
            pa = P(col, w_, a=k * (0.95 - 0.15 * i))
            pa.setStrokeCap(skia.Paint.kRound_Cap)
            cv.drawPath(p, pa)
    if c.lt > 0.6:
        j = ease((c.lt - 0.6) / 0.12)
        cv.drawLine(790, 400, lerp(790, 1030, j), lerp(400, 720, j), P(0xFF000000, 36))
        cv.drawLine(790, 400, lerp(790, 1030, j), lerp(400, 720, j), P(RED, 22))


OVER = dict(signoff=closed, rook_gate=snow, rook_door=snow, rook_wrong=snow, flash_side=whiteout, bug_flash=whiteout, bug_ear=ear_mute)
