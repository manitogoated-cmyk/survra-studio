"""Case 013, the full case file - Anatoli Bugorski. The story is filmed in 3D (world3d.py). This file holds the flat
inserts for the 16:9 film (the drawn path of the beam through a head, Rook's case board on a sheet of graph paper, a
card for the machine and one for the man, the two dates, the burst of light, the dose figures and the dose gauge, the
thin line against the whole body, the three lasting effects, the secret decade, the 1996 form, the advice), the 2D
overlays drawn on top of 3D shots (snow, the white-out, the muted ear, the sign-off) and the thumbnail. Every card is
a drawing made for this film; none of them reproduces a real document, medical image, photograph or logo. The dose
figures are one set of estimates (about 2,000 gray in, 3,000 out) and are labelled as such, because sources differ."""
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


def left(cv, s, x, y, size, col=0xFFFFFFFF, stroke=0xFF000000, maxw=None):
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
    if maxw and w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, col, stroke, center=False)


def graph_board(cv):
    """Rook's board for this case: a big sheet of green graph paper clipped to a steel plate."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('2A303A')))
    for i in range(-H, W, 46):
        cv.drawLine(i, 0, i + H * 0.25, H, P(0x14FFFFFF, 10))
    cv.drawRect(skia.Rect.MakeLTRB(60, 50, W - 60, H - 40), P(h('DCE8D4')))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(60, 50, W - 60, H - 40))
    for i in range(0, W, 32):
        cv.drawLine(i, 0, i, H, P(h('7FB08A'), 4 if i % 160 == 0 else 1.5, a=0.55))
    for j in range(0, H, 32):
        cv.drawLine(0, j, W, j, P(h('7FB08A'), 4 if j % 160 == 0 else 1.5, a=0.55))
    cv.restore()
    for x in (480, 1440):                                        # two bulldog clips
        cv.drawRect(skia.Rect.MakeXYWH(x - 70, 10, 140, 90), P(h('8E96A4')))
        cv.drawRect(skia.Rect.MakeXYWH(x - 70, 10, 140, 90), P(h('1B1E26'), 6))
        cv.drawCircle(x, 40, 14, P(h('1B1E26')))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.5, 0x00000000), (1, 0x55000000)])


def blueprint(cv):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0E1C34')), (1, h('04070E'))])
    for i in range(0, W + 1, 96):
        cv.drawLine(i, 0, i, H, P(h('1E4A7A'), 2, a=0.5))
    for j in range(0, H + 1, 90):
        cv.drawLine(0, j, W, j, P(h('1E4A7A'), 2, a=0.5))


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


def beam_head(cv, c, cx, cy, s, t0=0.1, speed=1.0):
    """The drawn head with the beam going in at the back and out beside the nose. Returns the two crossing points."""
    hp = head_profile(cx, cy, s)
    cv.drawPath(hp, P(h('16365E')))
    cv.drawPath(hp, P(h('49C8FF'), 8))
    cv.drawOval(skia.Rect.MakeXYWH(cx - 2.2 * s, cy - 2.5 * s, 3.6 * s, 2.7 * s), P(h('2A4E86')))                    # the brain, as a plain shape
    cv.drawOval(skia.Rect.MakeXYWH(cx - 2.2 * s, cy - 2.5 * s, 3.6 * s, 2.7 * s), P(h('49C8FF'), 4, a=0.6))
    cv.drawCircle(cx + 1.45 * s, cy - 0.55 * s, 0.17 * s, P(h('CFF0FF')))                                           # eye
    y0, y1 = cy - 1.0 * s, cy + 0.72 * s
    xa, xb = cx - 2.62 * s, cx + 2.5 * s
    lt = (c.lt - t0) * speed
    k_in, k_th, k_out = ease(lt / 0.35), ease((lt - 0.35) / 0.3), ease((lt - 0.85) / 0.35)
    slope = (y1 - y0) / (xb - xa)
    for pa in (P(BEAM, 0.37 * s, a=0.25), P(0xFFFFFFFF, 0.12 * s)):
        cv.drawLine(-20, y0, lerp(-20, xa, k_in), y0, pa)
        if k_th > 0:
            cv.drawLine(xa, y0, lerp(xa, xb, k_th), lerp(y0, y1, k_th), pa)
        if k_out > 0:
            cv.drawLine(xb, y1, lerp(xb, W + 20, k_out), lerp(y1, y1 + (W + 20 - xb) * slope, k_out), pa)
    if k_in >= 1:
        cv.drawCircle(xa, y0, 0.22 * s + 6 * math.sin(c.t * 14), P(AMBER))
    if k_th >= 1:
        cv.drawCircle(xb, y1, 0.22 * s + 6 * math.sin(c.t * 14 + 1), P(AMBER))
    return (xa, y0), (xb, y1), k_in, k_th


# ------------------------------------------------------------------ flat inserts (1920 x 1080; captions sit at y 930, the HUD top right)
def path_card(cv, c):
    """'In at the back. Out beside his nose.'"""
    blueprint(cv)
    cx, cy, s = 960, 440, 92
    (xa, y0), (xb, y1), k_in, k_th = beam_head(cv, c, cx, cy, s)
    if c.lt > 0.12:
        k = ease((c.lt - 0.12) / 0.15)
        fit(cv, 'IN', 520, 250 + 30 * (1 - k), 150, 300, AMBER)
        arrow(cv, 560, 280, xa - 30, y0 - 30, AMBER, 14, k)
    if c.lt > 0.95:
        k = ease((c.lt - 0.95) / 0.15)
        fit(cv, 'OUT', 1420, 760 - 30 * (1 - k), 150, 330, AMBER)
        arrow(cv, 1380, 640, xb + 30, y1 + 36, AMBER, 14, k)


def board_no(cv, c):
    graph_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(620, 450)
    cv.scale(s, s)
    card(cv, 0, 0, 900, 620, -3)
    cv.rotate(-3)
    photo(cv, 'ring', 0, 16, 830, 530, (0.5, 0.5))
    cv.restore()
    if c.lt > 0.12:
        cv.drawLine(1090, 400, 1180, 330, P(RED, 8))
        note(cv, 1450, 300, 640, 200, 3, h('FFD866'), ['THROUGH', 'HIS HEAD?'], 84)
    hp = head_profile(1300, 560, 30)
    cv.drawPath(hp, P(h('16365E')))
    cv.drawLine(1150, 532, 1460, 580, P(RED, 10))
    fit(cv, '1978', 1620, 640, 120, 300, INK, None)
    if c.k > 0.5:
        stamp(cv, 'NO CHANCE', 900, 480, -12, min(1, (c.k - 0.5) / 0.16), 150)


def suns(cv, c):
    """'Brighter than a thousand suns': rays bursting from one point until the frame is white."""
    cx, cy = 960, 470
    k = ease(c.lt / 1.2)
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
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFFFFFFF, a=0.35 * ease((c.lt - 1.2) / 0.4)))


def dose(cv, c):
    """A drawn gauge with no figures: the needle swings far past the lethal mark."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('18222E')), (1, h('080B10'))])
    cx, cy, r = 1120, 620, 430
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(0, 0, W, 800))
    cv.drawCircle(cx, cy, r + 60, P(h('2B323A')))
    cv.drawCircle(cx, cy, r + 60, P(h('8E96A4'), 14))
    cv.drawCircle(cx, cy, r + 10, P(h('ECE6D2')))
    a0, a1 = math.radians(180), math.radians(0)
    ang = lambda u: a0 + (a1 - a0) * u
    arcp = skia.Path()
    arcp.addArc(skia.Rect.MakeXYWH(cx - r + 60, cy - r + 60, 2 * r - 120, 2 * r - 120), -180, 14)
    cv.drawPath(arcp, P(GREEN, 46))
    arcp = skia.Path()
    arcp.addArc(skia.Rect.MakeXYWH(cx - r + 60, cy - r + 60, 2 * r - 120, 2 * r - 120), -166, 166)
    cv.drawPath(arcp, P(RED, 46))
    for i in range(21):
        a = ang(i / 20)
        r0 = r - 110 if i % 5 else r - 150
        cv.drawLine(cx + r0 * math.cos(a), cy - r0 * math.sin(a), cx + (r - 90) * math.cos(a), cy - (r - 90) * math.sin(a), P(INK, 8 if i % 5 == 0 else 4))
    al = ang(0.078)
    cv.drawLine(cx + (r - 190) * math.cos(al), cy - (r - 190) * math.sin(al), cx + (r - 20) * math.cos(al), cy - (r - 20) * math.sin(al), P(INK, 12))
    fit(cv, 'LETHAL', cx - 205, cy - 95, 50, 230, INK, None)
    swing = ease((c.lt - 0.3) / 0.6)
    u = lerp(0.0, 0.97, swing) + (0.012 * math.sin(c.t * 40) if swing >= 1 else 0)
    a = ang(u)
    cv.drawLine(cx - 40 * math.cos(a), cy + 40 * math.sin(a), cx + (r - 70) * math.cos(a), cy - (r - 70) * math.sin(a), P(h('15171C'), 22))
    cv.drawLine(cx - 40 * math.cos(a), cy + 40 * math.sin(a), cx + (r - 70) * math.cos(a), cy - (r - 70) * math.sin(a), P(ORANGE, 10))
    cv.drawCircle(cx, cy, 44, P(h('15171C')))
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(0, 800, W, H), P(h('080B10')))
    left(cv, 'THE DOSE', 90, 250, 110)
    left(cv, 'BY SOME', 90, 400, 70, AMBER)
    left(cv, 'ESTIMATES', 90, 480, 70, AMBER)
    if c.lt > 0.9:
        k = ease((c.lt - 0.9) / 0.15)
        cv.save()
        cv.translate(330, 650)
        cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
        for i in range(3):
            cv.drawPath(poly([(-150 + i * 150 - 50, 40), (-150 + i * 150, -50), (-150 + i * 150 + 50, 40)]), P(AMBER))       # three warning triangles
        cv.restore()
        cv.drawRect(skia.Rect.MakeWH(W, H), P(RED, a=0.12 * (0.5 + 0.5 * math.sin(c.t * 12))))


def board_true(cv, c):
    graph_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(560, 450)
    cv.scale(s, s)
    card(cv, 0, 0, 760, 640, 3)
    cv.rotate(3)
    photo(cv, 'bug', 0, 16, 690, 550, (0.5, 0.4))
    cv.restore()
    if c.lt > 0.12:
        cv.drawLine(960, 380, 1060, 330, P(RED, 8))
        note(cv, 1400, 290, 760, 180, -3, h('FFD866'), ['BACK AT WORK'], 92)
    for i, s_ in enumerate(('1978', 'SAME ACCELERATOR')):
        if c.lt > 0.2 + i * 0.12:
            fit(cv, s_, 1400, 520 + i * 110, 96 if i == 0 else 72, 760, INK, None)
    if c.lt > 0.5:
        stamp(cv, 'TRUE', 820, 560, -10, min(1, (c.lt - 0.5) / 0.12), 170, GREEN)


def ring_drawing(cv, cx, cy, r, t, col=0xFF49C8FF):
    cv.drawCircle(cx, cy, r, P(col, 16))
    cv.drawCircle(cx, cy, r, P(h('0E1C34'), 4))
    for i in range(24):
        a = i * math.pi / 12
        cv.save()
        cv.translate(cx + r * math.cos(a), cy + r * math.sin(a))
        cv.rotate(math.degrees(a))
        cv.drawRect(skia.Rect.MakeXYWH(-22, -17, 44, 34), P(h('C9A227') if i % 3 == 0 else h('2B5FA8')))
        cv.restore()
    a = t * 5
    Wd.glow(cv, cx + r * math.cos(a), cy + r * math.sin(a), 60, 0xFFD6E6FF, 0.9)
    cv.drawCircle(cx + r * math.cos(a), cy + r * math.sin(a), 15, P(0xFFFFFFFF))


def machine(cv, c):
    """The machine: a drawn ring of magnets with a dot going round, and its name."""
    blueprint(cv)
    ring_drawing(cv, 520, 470, 290, c.t)
    for i, (s_, size, col) in enumerate((('U-70', 230, 0xFFFFFFFF), ('SYNCHROTRON', 104, AMBER), ('PROTVINO  1978', 78, 0xFFFFFFFF))):
        if c.lt > 0.1 + i * 0.4:
            k = ease((c.lt - 0.1 - i * 0.4) / 0.15)
            left(cv, s_, 960 + 40 * (1 - k), (350, 520, 650)[i], size, col, maxw=860)


def id_card(cv, c):
    """Who: a card with his portrait (a still from the film, not a photograph of him) and three lines."""
    graph_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.8 + 0.2 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 450)
    cv.scale(s, s)
    card(cv, 0, 0, 700, 640, -2)
    cv.rotate(-2)
    photo(cv, 'bug', 0, 16, 630, 550, (0.5, 0.4))
    cv.restore()
    for i, (s_, size) in enumerate((('ANATOLI', 150), ('BUGORSKI', 150), ('PHYSICIST', 84))):
        if c.lt > 0.15 + i * 0.25:
            left(cv, s_, 960, (330, 480, 620)[i], size, INK if i < 2 else RED, None, maxw=840)


def leaf(cv, x, y, w_, h_, ang, top, big, small, col):
    """One leaf of a tear-off calendar."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 10, -h_ / 2 + 14, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(PAPER))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_ * 0.24), P(col))
    for sx in (-1, 1):
        cv.drawCircle(sx * w_ * 0.3, -h_ / 2 + 6, 13, P(h('1B1E26')))
    fit(cv, top, 0, -h_ / 2 + h_ * 0.18, h_ * 0.15, w_ - 40, 0xFFFFFFFF, None)
    fit(cv, big, 0, h_ * 0.2, h_ * 0.42, w_ - 50, INK, None)
    if small:
        fit(cv, small, 0, h_ * 0.42, h_ * 0.1, w_ - 40, INK, None)
    cv.restore()


def dates(cv, c):
    """The accounts differ on the day: most say 13 July 1978, one says June."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('26303C')), (1, h('0C1016'))])
    if c.lt > 0.1:
        k = ease((c.lt - 0.1) / 0.2)
        leaf(cv, 600, 430 - 60 * (1 - k), 600, 560, -4, 'JULY 1978', '13', None, RED)
        if c.lt > 0.6:
            fit(cv, 'MOST ACCOUNTS', 600, 800, 70, 640, AMBER)
    if c.lt > 1.2:
        k = ease((c.lt - 1.2) / 0.2)
        leaf(cv, 1360, 460 - 60 * (1 - k), 480, 450, 5, 'JUNE 1978', '?', None, h('5A6670'))
        if c.lt > 1.6:
            fit(cv, 'ONE ACCOUNT', 1360, 800, 70, 560, 0xFFFFFFFF)
    if 0.5 < c.lt:
        fit(cv, 'OR', 1010, 470, 90, 200, 0xFFFFFFFF)


def bar(cv, x, y, w_, h_, col, k):
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w_ * k, h_), P(col))
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w_ * k, h_), P(0xFF000000, 5))


def dose_nums(cv, c):
    """One set of figures for the dose along the beam's path: about 2,000 gray going in, about 3,000 coming out."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('18222E')), (1, h('080B10'))])
    left(cv, 'THE DOSE', 110, 190, 100)
    left(cv, 'ONE SET OF FIGURES', 760, 185, 56, AMBER)
    x0, full = 110, 1560
    for i, (lab, val, frac, t0) in enumerate((('IN', 'ABOUT 2,000 GRAY', 2 / 3, 0.3), ('OUT', 'ABOUT 3,000 GRAY', 1.0, 1.3))):
        if c.lt > t0:
            k = ease((c.lt - t0) / 0.5)
            y = 300 + i * 270
            left(cv, lab, x0, y + 62, 84, AMBER)
            bar(cv, x0, y + 90, full * frac, 90, ORANGE if i == 0 else RED, k)
            if k > 0.6:
                left(cv, val, x0 + 260, y + 62, 84, 0xFFFFFFFF, maxw=1200)
    if c.lt > 2.3:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(RED, a=0.1 * (0.5 + 0.5 * math.sin(c.t * 12))))


def dose_five(cv, c):
    """The same scale: about 5 gray across the whole body can be enough to kill. On this scale it is a sliver."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('18222E')), (1, h('080B10'))])
    x0, full = 110, 1560
    left(cv, 'CAN KILL', 110, 190, 100)
    left(cv, 'ACROSS THE WHOLE BODY', 700, 185, 56, AMBER)
    k = ease((c.lt - 0.2) / 0.3)
    left(cv, 'ABOUT 5 GRAY', x0, 362, 84, GREEN)
    bar(cv, x0, 390, max(8.0, full * 5 / 3000) / max(k, 0.01), 90, GREEN, k)
    if c.lt > 0.6:
        j = ease((c.lt - 0.6) / 0.3)
        arrow(cv, x0 + 260, 560, x0 + 30, 490, GREEN, 10, j)
        left(cv, 'THIS SLIVER', x0 + 290, 590, 60, GREEN)
    if c.lt > 1.0:
        j = ease((c.lt - 1.0) / 0.5)
        left(cv, 'OUT', x0, 702, 64, AMBER)
        bar(cv, x0, 720, full, 60, RED, j)


def body_shape(cx, cy, s):
    """A plain standing figure, nobody's likeness."""
    pts = [(-0.5, -2.0), (0.5, -2.0), (0.55, -1.75), (1.3, -1.6), (1.5, 0.4), (1.1, 0.4), (0.95, -0.9), (0.8, 0.6), (0.85, 3.4), (0.2, 3.4),
           (0.0, 1.0), (-0.2, 3.4), (-0.85, 3.4), (-0.8, 0.6), (-0.95, -0.9), (-1.1, 0.4), (-1.5, 0.4), (-1.3, -1.6), (-0.55, -1.75)]
    return poly([(cx + x * s, cy + y * s) for x, y in pts])


def narrow(cv, c):
    """Why he lived, as usually explained: the dose ran along one thin line through his head, not through his whole body."""
    blueprint(cv)
    beam_head(cv, c, 520, 420, 74, 0.1, 1.6)
    if c.lt > 0.5:
        fit(cv, 'ONE THIN LINE', 520, 800, 84, 800, AMBER)
    if c.lt > 1.3:
        k = ease((c.lt - 1.3) / 0.3)
        cx, cy, s = 1400, 380, 92
        cv.drawCircle(cx, cy - 2.75 * s, 0.72 * s, P(h('D8362A'), a=0.75 * k))
        cv.drawPath(body_shape(cx, cy, s), P(h('D8362A'), a=0.75 * k))
        cv.drawCircle(cx, cy - 2.75 * s, 0.72 * s, P(h('49C8FF'), 6))
        cv.drawPath(body_shape(cx, cy, s), P(h('49C8FF'), 6))
        if c.lt > 1.7:
            j = ease((c.lt - 1.7) / 0.15)
            cv.drawLine(cx - 300, cy - 330, cx - 300 + 600 * j, cy - 330 + 700 * j, P(0xFF000000, 34))
            cv.drawLine(cx - 300, cy - 330, cx - 300 + 600 * j, cy - 330 + 700 * j, P(0xFFFFFFFF, 20))
            fit(cv, 'NOT THE WHOLE BODY', 1400, 800, 76, 880, 0xFFFFFFFF)


def cost_list(cv, c):
    graph_board(cv)
    rows = (('LEFT EAR', 'HEARING LOST'), ('LEFT SIDE OF THE FACE', 'PARALYSED'), ('SEIZURES', ''))
    for i, (a, b) in enumerate(rows):
        if c.lt > 0.1 + i * 0.3:
            k = ease((c.lt - 0.1 - i * 0.3) / 0.15)
            y = 250 + i * 210
            cv.drawRect(skia.Rect.MakeXYWH(170, y - 62, 70, 70), P(RED, 10))
            cv.drawLine(180, y - 52, 230, y - 2, P(RED, 12))
            cv.drawLine(230, y - 52, 180, y - 2, P(RED, 12))
            left(cv, a, 290 + 40 * (1 - k), y, 96, INK, None, maxw=1000)
            if b:
                left(cv, b, 290 + 40 * (1 - k), y + 80, 64, RED, None, maxw=1000)
    hp = head_profile(1560, 420, 60)
    cv.drawPath(hp, P(h('16365E')))
    cv.drawLine(1380, 360, 1740, 464, P(RED, 10))


def decade(cv, c):
    """About ten years in which the story was not public: calendar leaves falling away under a stamp."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('26303C')), (1, h('0C1016'))])
    n = 10
    cur = min(n - 1, int(c.k * 1.25 * n))
    for i in range(cur):                                          # leaves already torn off, drifting down
        age = c.k * 1.25 * n - i
        x = 960 + (i - 4.5) * 150 + 40 * math.sin(i * 2.1)
        y = 430 + 120 * min(age, 3.5) + 20 * math.sin(i)
        leaf(cv, x, y, 250, 250, (i * 37) % 40 - 20 + 8 * age, '', 'x', None, h('5A6670'))
    leaf(cv, 960, 400, 520, 480, -2, 'YEAR', str(cur + 1), None, RED)
    left(cv, 'ABOUT A DECADE', 110, 200, 84, 0xFFFFFFFF)
    if c.k > 0.55:
        stamp(cv, 'SECRET', 1300, 560, -14, min(1, (c.k - 0.55) / 0.12), 170)


def claim_card(cv, c):
    """A drawn form, not a real one: an application for disability status, 1996, stamped REFUSED."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('4A3A2A')))
    for j in range(0, H, 54):
        cv.drawLine(0, j, W, j + 30, P(0x18000000, 16))
    k = min(1, c.lt / 0.18)
    s = 0.86 + 0.14 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(960, 450)
    cv.scale(s, s)
    cv.rotate(-2)
    cv.drawRect(skia.Rect.MakeXYWH(-668, -374, 1360, 780), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-680, -390, 1360, 780), P(PAPER))
    cv.drawRect(skia.Rect.MakeXYWH(-680, -390, 1360, 120), P(h('5A6670')))
    fit(cv, 'APPLICATION', 0, -305, 80, 1200, 0xFFFFFFFF, None)
    fit(cv, 'DISABILITY STATUS', -160, -120, 110, 900, INK, None)
    fit(cv, '1996', 470, -110, 130, 320, RED, None)
    for i in range(4):
        cv.drawLine(-600, 0 + i * 80, 600 - (i % 2) * 260, 0 + i * 80, P(h('8A8474'), 10))
    cv.drawRect(skia.Rect.MakeXYWH(-600, 300, 60, 60), P(INK, 8))
    cv.restore()
    if c.lt > 0.9:
        stamp(cv, 'REFUSED', 1040, 560, -11, min(1, (c.lt - 0.9) / 0.14), 200)


def advice(cv, c):
    """Rook's advice: a warning lamp that is dark tells you nothing. Find out why before you lean in."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C2026')), (1, h('07080B'))])
    cx, cy = 440, 450
    for j in range(8):
        cv.drawRect(skia.Rect.MakeXYWH(cx - 280 + j * 70, cy + 250, 70, 44), P(ORANGE if j % 2 else h('15171C')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 250, cy - 250, 500, 500), 40, 40, P(h('22252C')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(cx - 250, cy - 250, 500, 500), 40, 40, P(h('8E96A4'), 10))
    cv.drawCircle(cx, cy, 180, P(h('3A1412')))
    cv.drawCircle(cx, cy, 180, P(h('8E96A4'), 14))
    cv.drawCircle(cx - 60, cy - 70, 34, P(0x22FFFFFF))
    if c.lt > 0.3:
        k = ease((c.lt - 0.3) / 0.15)
        fit(cv, '?', cx, cy + 90 - 20 * (1 - k), 280, 300, AMBER)
    for i, (s_, size, col) in enumerate((('DARK LAMP?', 150, 0xFFFFFFFF), ('FIND OUT WHY', 124, AMBER), ('BEFORE YOU LEAN IN', 78, 0xFFFFFFFF))):
        if c.lt > 0.2 + i * 0.45:
            k = ease((c.lt - 0.2 - i * 0.45) / 0.15)
            left(cv, s_, 800 + 40 * (1 - k), (330, 500, 630)[i], size, col, maxw=1040)


SHOTS = {f.__name__: f for f in (path_card, board_no, suns, dose, board_true, machine, id_card, dates, dose_nums, dose_five, narrow, cost_list,
                                 decade, claim_card, advice)}


# ------------------------------------------------------------------ overlays on 3D shots
def closed(cv, c):
    snow(cv, c)
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(430, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 013  CLOSED', 0, 96, 60, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 90, 0xCCF4F8FF, 5, size=(3, 8), drift=(-70, 230), wobble=26)


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
    x, y = 1180, 420
    for i in range(3):
        r = 80 + i * 56 + 10 * math.sin(c.t * 8 - i)
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -42, 84)
        for col, w_ in ((0xFF000000, 28), (0xFFFFFFFF, 14)):
            pa = P(col, w_, a=k * (0.95 - 0.15 * i))
            pa.setStrokeCap(skia.Paint.kRound_Cap)
            cv.drawPath(p, pa)
    if c.lt > 0.6:
        j = ease((c.lt - 0.6) / 0.12)
        cv.drawLine(1200, 280, lerp(1200, 1420, j), lerp(280, 560, j), P(0xFF000000, 34))
        cv.drawLine(1200, 280, lerp(1200, 1420, j), lerp(280, 560, j), P(RED, 20))


OVER = dict(signoff=closed, rook_gate=snow, rook_door=snow, rook_wrong=snow, flash_side=whiteout, bug_flash=whiteout, bug_ear=ear_mute,
            road_van=snow, rook_road=snow)


def THUMB(cv, c):
    """1280x720: the 3D still (the drawn beam crossing the gap at his head, Rook throwing his arms up) and a hook on the right."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0E1C34'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(640, 0), (1280, 0)], [0x00000000, 0xE6000000])))
    Wd.text_card(cv, 'BEAM', 985, 210, 150, BEAM, 0xFF000000)
    Wd.text_card(cv, 'THROUGH', 985, 350, 104, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'HIS HEAD', 985, 480, 112, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'HE LIVED', 985, 630, 118, AMBER, 0xFF000000)
