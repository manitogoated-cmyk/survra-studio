"""Kesta - Survra's host. A 2D cut-out rig drawn with Skia.

Local units: feet at y=0, top of hair at about y=-112. Scale s = pixels per 100 units.
facing=+1 looks to the right (3/4 view), -1 mirrors.

Public API
  draw_kesta(cv, x, y, s, pose, t, facing=1, expr='neutral', viseme='rest', look=(0,0),
             blink=None, goggles='up', wind=0.0, speed=0.0, alpha=1.0, light=None)
  POSES, pose(name, **over), blend(a, b, k), keyframes(t, [(t0, pose), ...]), walk(t, speed)
  EXPR (expression presets), VISEMES (mouth shapes)
"""
import math

import skia

INK = 0xFF14121A
OW = 0.62  # global outline scale
COL = dict(
    skin=0xFF8A5A3C, skin_sh=0xFF6E4630, hair=0xFF241814, hair_hi=0xFF3A2A22,
    scarf=0xFFFF7A1A, scarf_st=0xFFFFB000, scarf_sh=0xFFD95E0E,
    jacket=0xFF1F5F6B, jacket_sh=0xFF174954, shirt=0xFFF2E8D8,
    pants=0xFF2B2F36, pants_sh=0xFF22252B, boots=0xFF6B4127, sole=0xFF3B2414,
    gog=0xFFD4A640, lens=0xFF7FD3E6, strap=0xFF5A3A22, satchel=0xFF8B5A2B,
    eye_w=0xFFFFFBF2, iris=0xFFE89B2C, pupil=0xFF1A1010, mouth=0xFF4A1C1C,
    tongue=0xFFD9646A, teeth=0xFFFFFFFF, blush=0x55FF6A5A, band=0xFFFF7A1A,
    flare=0xFFFF7A1A, journal=0xFFC9A46A,
)

# ---------------------------------------------------------------- utilities

def P(c, stroke=None, aa=True, a=1.0):
    p = skia.Paint(AntiAlias=aa, Color=c)
    if a < 1:
        p.setAlphaf(p.getAlphaf() * a)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def lerp(a, b, k):
    return a + (b - a) * k


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rot(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return x * c - y * s, x * s + y * c


def limb_pts(base, a1, l1, a2, l2):
    """Angles in degrees, 0 = straight down, positive = forward (toward facing)."""
    bx, by = base
    ex = bx + math.sin(math.radians(a1)) * l1
    ey = by + math.cos(math.radians(a1)) * l1
    tx = ex + math.sin(math.radians(a1 + a2)) * l2
    ty = ey + math.cos(math.radians(a1 + a2)) * l2
    return (ex, ey), (tx, ty)


def seg(cv, a, b, w, fill, ink=INK, ow=2.4, alpha=1.0):
    ow *= OW
    path = skia.Path()
    path.moveTo(*a)
    path.lineTo(*b)
    cv.drawPath(path, P(ink, w + ow * 2, a=alpha))
    cv.drawPath(path, P(fill, w, a=alpha))


def poly(cv, pts, fill, ink=INK, ow=2.4, alpha=1.0, close=True, smooth=False):
    ow *= OW
    path = skia.Path()
    path.moveTo(*pts[0])
    if smooth and len(pts) > 2:
        for i in range(1, len(pts) - 1):
            mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
            path.quadTo(pts[i][0], pts[i][1], mx, my)
        path.lineTo(*pts[-1])
    else:
        for q in pts[1:]:
            path.lineTo(*q)
    if close:
        path.close()
    if fill is not None:
        cv.drawPath(path, P(fill, a=alpha))
    if ink is not None:
        cv.drawPath(path, P(ink, ow, a=alpha))
    return path


def circle(cv, x, y, r, fill, ink=INK, ow=2.4, alpha=1.0):
    ow *= OW
    cv.drawCircle(x, y, r, P(fill, a=alpha))
    if ink is not None:
        cv.drawCircle(x, y, r, P(ink, ow, a=alpha))


def oval(cv, x, y, rx, ry, fill, ink=INK, ow=2.4, alpha=1.0, ang=0):
    ow *= OW
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    r = skia.Rect.MakeLTRB(-rx, -ry, rx, ry)
    cv.drawOval(r, P(fill, a=alpha))
    if ink is not None:
        cv.drawOval(r, P(ink, ow, a=alpha))
    cv.restore()


# ---------------------------------------------------------------- poses
# Angles: arms/legs 0 = hanging down; positive swings toward the facing side.
# Elbow/knee are relative bends. 'B' = back limb (far from camera), 'F' = front limb.
BASE = dict(
    rx=0.0, ry=0.0, lean=0.0, head=0.0, nod=0.0, turn=0.0,
    aBu=-8.0, aBl=-14.0, aFu=10.0, aFl=-18.0,
    lBu=-6.0, lBl=4.0, lFu=6.0, lFl=4.0,
    hB='open', hF='open', crouch=0.0, prop=None, prop_k=0.0,
    fFx=5.0, fFy=0.0, fBx=-4.0, fBy=0.0,
)

POSES = {
    'stand':    dict(),
    'idle':     dict(aBu=-6, aBl=-10, aFu=6, aFl=-14),
    'talk_a':   dict(aFu=40, aFl=-75, hF='open', aBu=-12, aBl=-20),
    'talk_b':   dict(aFu=25, aFl=-95, hF='open', aBu=-20, aBl=-60, hB='open'),
    'talk_c':   dict(aFu=55, aFl=-40, hF='point2', lean=3),
    'point':    dict(aFu=95, aFl=-6, hF='point2', lean=4, head=2),
    'point_up': dict(aFu=150, aFl=-10, hF='point2', head=-10, lean=-2),
    'point_down': dict(aFu=60, aFl=10, hF='point2', head=12, lean=8, nod=8),
    'wave_a':   dict(aFu=150, aFl=-30, hF='open', head=-3),
    'wave_b':   dict(aFu=150, aFl=10, hF='open', head=-3),
    'shrug':    dict(aBu=-40, aBl=-100, aFu=40, aFl=-100, hB='open', hF='open', head=6, ry=-2),
    'gasp':     dict(aFu=40, aFl=-150, hF='open', aBu=-35, aBl=-120, hB='open', lean=-6, head=-6, ry=-1),
    'cover_mouth': dict(aFu=30, aFl=-160, hF='open', aBu=-10, aBl=-30, lean=-2, head=4),
    'think':    dict(aFu=25, aFl=-155, hF='fist', aBu=10, aBl=-95, hB='fist', head=8, nod=6),
    'cross':    dict(aFu=20, aFl=-110, hF='fist', aBu=-15, aBl=-110, hB='fist', lean=-3),
    'fist_pump': dict(aFu=160, aFl=-25, hF='fist', aBu=-20, aBl=-60, hB='fist', head=-8, ry=-3),
    'brace':    dict(aFu=60, aFl=-60, hF='open', aBu=-50, aBl=-40, fFx=13, fBx=-11, crouch=6, lean=8),
    'crouch':   dict(crouch=22, fFx=10, fBx=-8, lean=24, nod=14, aFu=70, aFl=-40, aBu=20, aBl=-40),
    'inspect':  dict(crouch=22, fFx=10, fBx=-8, lean=26, nod=16, aFu=88, aFl=-8, hF='point2', aBu=40, aBl=-70),
    'journal':  dict(aFu=35, aFl=-95, hF='hold', aBu=30, aBl=-80, hB='hold', head=10, nod=10, prop='journal'),
    'flare_aim': dict(aFu=120, aFl=-5, hF='hold', aBu=-10, aBl=-20, head=-6, lean=-2, prop='flare'),
    'flare_fire': dict(aFu=165, aFl=-5, hF='hold', aBu=-30, aBl=-40, head=-16, lean=-5, ry=-2, prop='flare'),
    'step_back': dict(lean=-10, head=-8, aFu=50, aFl=-70, aBu=-40, aBl=-50, fFx=12, fBx=-12, rx=-3, crouch=2),
    'shiver':   dict(aFu=30, aFl=-140, hF='fist', aBu=25, aBl=-140, hB='fist', lean=6, head=8, crouch=3),
    'look_around': dict(head=0, aBu=-4, aBl=-8, aFu=4, aFl=-10),
    'sad':      dict(aBu=-2, aBl=-4, aFu=2, aFl=-6, head=14, nod=12, lean=4),
    'goggle_grab': dict(aFu=40, aFl=-170, hF='hold', head=-4),
    'reach':    dict(aFu=80, aFl=-15, hF='open', lean=12, fFx=13, fBx=-9, crouch=3),
}


def pose(name, **over):
    p = dict(BASE)
    p.update(POSES.get(name, {}))
    p.update(over)
    return p


def blend(a, b, k):
    k = ease(k)
    out = {}
    for key in BASE:
        va, vb = a.get(key, BASE[key]), b.get(key, BASE[key])
        out[key] = lerp(va, vb, k) if isinstance(va, (int, float)) and isinstance(vb, (int, float)) else (va if k < 0.5 else vb)
    return out


def keyframes(t, frames):
    """frames: [(time, pose_dict)] sorted. Holds at the ends."""
    if t <= frames[0][0]:
        return frames[0][1]
    for (t0, p0), (t1, p1) in zip(frames, frames[1:]):
        if t <= t1:
            return blend(p0, p1, (t - t0) / max(1e-6, t1 - t0))
    return frames[-1][1]


def walk(t, speed=1.0, base='stand', run=False):
    """Walk/run cycle with planted feet (IK). speed = cycles per second."""
    ph = t * speed * 2 * math.pi
    stride = 15 if run else 10
    p = pose(base)
    p['fFx'] = 1 + stride * math.sin(ph)
    p['fBx'] = -1 - stride * math.sin(ph)
    p['fFy'] = -max(0.0, math.cos(ph)) * (9 if run else 5)
    p['fBy'] = -max(0.0, -math.cos(ph)) * (9 if run else 5)
    amp = 34 if run else 22
    p['aFu'] = -amp * math.sin(ph) + (25 if run else 6)
    p['aBu'] = amp * math.sin(ph) - (10 if run else 4)
    p['aFl'] = -(75 if run else 22)
    p['aBl'] = -(75 if run else 22)
    p['hF'] = p['hB'] = 'fist' if run else 'open'
    p['ry'] = -abs(math.cos(ph)) * (5 if run else 2.2) + (3 if run else 1)
    p['lean'] = 12 if run else 3
    return p


# ---------------------------------------------------------------- face
EXPR = {
    #            browL  browR  browTilt lidTop lidBot mouthCurve blush
    'neutral':   dict(bh=0, bt=0, lid=0.15, low=0.0, curve=0.15, blush=0, sweat=0),
    'happy':     dict(bh=-2, bt=4, lid=0.10, low=0.35, curve=0.8, blush=1, sweat=0),
    'excited':   dict(bh=-4, bt=6, lid=0.0, low=0.15, curve=0.9, blush=1, sweat=0),
    'curious':   dict(bh=-3, bt=-6, lid=0.1, low=0.0, curve=0.1, blush=0, sweat=0, asym=1),
    'smirk':     dict(bh=-1, bt=2, lid=0.3, low=0.1, curve=0.5, blush=0, sweat=0, asym=1),
    'worried':   dict(bh=-2, bt=-14, lid=0.1, low=0.0, curve=-0.4, blush=0, sweat=1),
    'scared':    dict(bh=-5, bt=-16, lid=0.0, low=0.0, curve=-0.6, blush=0, sweat=1, small_pupil=1),
    'shocked':   dict(bh=-7, bt=0, lid=0.0, low=0.0, curve=-0.2, blush=0, sweat=0, small_pupil=1),
    'sad':       dict(bh=0, bt=-16, lid=0.35, low=0.1, curve=-0.7, blush=0, sweat=0, tear=1),
    'determined': dict(bh=2, bt=12, lid=0.3, low=0.15, curve=-0.05, blush=0, sweat=0),
    'awed':      dict(bh=-6, bt=-4, lid=0.0, low=0.0, curve=0.4, blush=1, sweat=0, sparkle=1),
    'skeptical': dict(bh=0, bt=10, lid=0.4, low=0.1, curve=-0.2, blush=0, sweat=0, asym=1),
    'angry':     dict(bh=3, bt=18, lid=0.25, low=0.2, curve=-0.6, blush=0, sweat=0),
    'relieved':  dict(bh=-1, bt=-8, lid=0.45, low=0.2, curve=0.6, blush=1, sweat=0),
    'wince':     dict(bh=2, bt=-10, lid=0.75, low=0.4, curve=-0.5, blush=0, sweat=1),
}

# Mouth shapes: (width, open height, roundness 0-1, show teeth, show tongue)
VISEMES = {
    'rest': (7.0, 0.0, 0.0, False, False),
    'MBP':  (6.5, 0.0, 0.0, False, False),
    'FV':   (7.0, 1.6, 0.0, True, False),
    'TH':   (7.0, 2.2, 0.2, True, True),
    'L':    (7.0, 3.2, 0.3, True, True),
    'E':    (8.6, 2.6, 0.1, True, False),
    'AI':   (8.2, 5.4, 0.35, True, True),
    'O':    (5.6, 4.8, 0.95, False, True),
    'WQ':   (4.0, 2.6, 1.0, False, False),
    'etc':  (7.4, 2.4, 0.2, True, False),
}

_V = {}
for ch in 'mbp':
    _V[ch] = 'MBP'
for ch in 'fv':
    _V[ch] = 'FV'
for ch in 'θð':
    _V[ch] = 'TH'
_V['l'] = 'L'
for ch in 'aæɑʌɐ':
    _V[ch] = 'AI'
for ch in 'eɛɪiəɚɜᵻ':
    _V[ch] = 'E'
for ch in 'oɔɒ':
    _V[ch] = 'O'
for ch in 'wuʊ':
    _V[ch] = 'WQ'


def phoneme_viseme(ph):
    if not ph or ph in ' .,!?;:—…"\'':
        return 'rest'
    return _V.get(ph[0], 'etc')


def draw_mouth(cv, x, y, vis, e, k_open=1.0, facing=1):
    w, h, rnd, teeth, tongue = VISEMES.get(vis, VISEMES['rest'])
    h *= k_open
    curve = e.get('curve', 0)
    if h < 0.6:
        # closed mouth: a curve whose corners follow the expression
        path = skia.Path()
        cy = y
        dl = -curve * 2.4
        dr = -curve * 2.4 + (e.get('asym', 0) * -1.2)
        path.moveTo(x - w / 2, cy + dl)
        path.quadTo(x, cy + curve * 2.2, x + w / 2, cy + dr)
        cv.drawPath(path, P(INK, 1.3))
        if vis == 'MBP':
            cv.drawPath(path, P(INK, 1.8))
        return
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - w / 2, y - h / 2 + curve * 0.6, x + w / 2, y + h / 2 + curve * 0.6),
                               w / 2 * (0.4 + 0.6 * rnd), h / 2)
    cv.drawRRect(rr, P(COL['mouth']))
    cv.save()
    cv.clipRRect(rr, True)
    if teeth:
        cv.drawRect(skia.Rect.MakeLTRB(x - w / 2, y - h / 2 + curve * 0.6 - 1, x + w / 2, y - h / 2 + curve * 0.6 + min(1.6, h * 0.35)), P(COL['teeth']))
    if tongue and h > 2:
        cv.drawOval(skia.Rect.MakeLTRB(x - w * 0.32, y + h * 0.05, x + w * 0.32, y + h / 2 + 2 + curve * 0.6), P(COL['tongue']))
    cv.restore()
    cv.drawRRect(rr, P(INK, 1.0))


def draw_eye(cv, x, y, rx, ry, e, look, blink, near=True):
    lid = max(e.get('lid', 0), blink)
    low = e.get('low', 0)
    top = y - ry + 2 * ry * lid
    bot = y + ry - 2 * ry * low * 0.5
    if bot - top < 0.8:
        # closed / happy eye arc
        path = skia.Path()
        path.moveTo(x - rx, y)
        path.quadTo(x, y - (ry * 0.7 if e.get('curve', 0) > 0.5 else -ry * 0.3), x + rx, y)
        cv.drawPath(path, P(INK, 2.4))
        return
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(x - rx - 2, top, x + rx + 2, bot))
    oval(cv, x, y, rx, ry, COL['eye_w'], ink=None)
    ir = rx * (0.62 if near else 0.58)
    ix, iy = x + look[0] * rx * 0.38, y + look[1] * ry * 0.3
    circle(cv, ix, iy, ir, COL['iris'], ink=None)
    pr = ir * (0.38 if e.get('small_pupil') else 0.55)
    circle(cv, ix, iy, pr, COL['pupil'], ink=None)
    circle(cv, ix + ir * 0.35, iy - ir * 0.4, ir * 0.24, 0xFFFFFFFF, ink=None)
    if e.get('sparkle'):
        circle(cv, ix - ir * 0.3, iy + ir * 0.3, ir * 0.14, 0xFFFFFFFF, ink=None)
    cv.restore()
    oval(cv, x, y, rx, ry, None if False else 0x00000000, ink=INK, ow=1.6)
    # lash line on top lid
    path = skia.Path()
    path.moveTo(x - rx - 1, top + (ry * 0.25 if lid < 0.05 else 0))
    path.quadTo(x, top - ry * 0.35 * (1 - lid), x + rx + 1.5, top + (ry * 0.15 if lid < 0.05 else 0))
    cv.drawPath(path, P(INK, 2.2))


def draw_head(cv, p, t, facing, expr, viseme, look, blink, goggles, k_open):
    e = EXPR.get(expr, EXPR['neutral'])
    turn = p.get('turn', 0.0)  # -1..1 toward/away
    fx = 2.5 + turn * 2  # face centre shifts toward the facing side
    # back hair puff (the silhouette signature)
    blobs = [(-9, -24, 9.5), (-1, -28, 10.5), (7, -25, 9), (-3, -19, 9.5), (-12, -17, 7.5), (4, -19, 8)]
    for (dx, dy, r) in blobs:
        circle(cv, dx, dy, r, COL['hair'], ow=2.2)
    for (dx, dy, r) in blobs:
        circle(cv, dx, dy, r - 1.4, COL['hair'], ink=None)
    for (dx, dy) in [(-5, -31), (5, -28), (-11, -22)]:
        path = skia.Path()
        path.addArc(skia.Rect.MakeXYWH(dx - 3, dy - 2, 6, 5), 200, 140)
        cv.drawPath(path, P(COL['hair_hi'], 1.4))
    # hair band
    poly(cv, [(-13, -15.5), (9, -18.5), (9.6, -15.4), (-12.4, -12.2)], COL['band'], ow=1.8)
    # back ear
    # head shape
    head = skia.Path()
    head.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-12, -16, 13, 15), 12, 13))
    cv.drawPath(head, P(COL['skin']))
    # jaw toward facing
    poly(cv, [(fx - 7, 8), (fx + 9, 6), (fx + 5, 15), (fx - 6, 16)], COL['skin'], ink=None)
    cv.drawPath(head, P(INK, 2.4))
    # ear (back side)
    oval(cv, -10.5, 2, 2.4, 3.4, COL['skin'], ow=1.8)
    oval(cv, -10.5, 2, 1.0, 1.8, COL['skin_sh'], ink=None)
    # front curls / fringe
    poly(cv, [(-12, -6), (-10, -15), (0, -18), (12, -14), (14, -6), (8, -10), (2, -8), (-4, -11)], COL['hair'], ow=2.2, smooth=True)
    # loose curl
    path = skia.Path()
    path.moveTo(fx + 6, -12)
    path.cubicTo(fx + 12, -8, fx + 8, -2, fx + 11, 1)
    cv.drawPath(path, P(INK, 4.2))
    cv.drawPath(path, P(COL['hair'], 2.4))
    # goggles
    gy = -14 if goggles == 'up' else -2
    if goggles == 'up':
        seg(cv, (-12, gy + 1), (13, gy - 1), 2.4, COL['strap'], ow=1.4)
        for gx in (fx - 4, fx + 6):
            circle(cv, gx, gy - 2, 4.6, COL['gog'], ow=2.0)
            circle(cv, gx, gy - 2, 3.0, COL['lens'], ink=None)
            circle(cv, gx + 1, gy - 3.4, 0.9, 0xFFFFFFFF, ink=None)
    # brows + eyes
    bh, bt = e.get('bh', 0), e.get('bt', 0)
    ex_n, ex_f = fx + 5.5, fx - 4.5
    ey = 0.5
    draw_eye(cv, ex_f, ey, 2.9, 3.9, e, look, blink, near=False)
    draw_eye(cv, ex_n, ey, 3.6, 4.3, e, look, blink, near=True)
    for bx, sign, w in ((ex_f, -1, 3.2), (ex_n, 1, 4.0)):
        tilt = bt * (1 if sign > 0 else -1) * 0.12
        by = ey - 8.6 + bh * 0.5
        if e.get('asym') and sign > 0:
            by -= 1.6
        seg(cv, (bx - w, by + tilt), (bx + w, by - tilt), 0.9, INK, ow=0.5)
    # nose
    path = skia.Path()
    path.moveTo(fx + 9.6, 2.5)
    path.quadTo(fx + 12.6, 6.4, fx + 9.0, 6.9)
    cv.drawPath(path, P(INK, 1.8))
    # blush / freckles
    if e.get('blush'):
        oval(cv, ex_n + 1, 7.4, 3.2, 1.4, COL['blush'], ink=None)
    for (dx, dy) in [(ex_n - 2, 6.6), (ex_n + 1.5, 7.5), (ex_n + 3.8, 6.4), (ex_f + 1, 6.8)]:
        circle(cv, dx, dy, 0.45, COL['skin_sh'], ink=None)
    # mouth
    draw_mouth(cv, fx + 4.0, 10.2, viseme, e, k_open, facing)
    # goggles down sit over eyes
    if goggles == 'down':
        seg(cv, (-12, gy), (14, gy - 1), 2.6, COL['strap'], ow=1.4)
        for gx, r in ((ex_f, 4.6), (ex_n, 5.4)):
            circle(cv, gx, ey, r, COL['gog'], ow=2.0)
            circle(cv, gx, ey, r - 1.6, COL['lens'], ink=None, alpha=0.85)
            circle(cv, gx + 1.4, ey - 1.8, 1.1, 0xFFFFFFFF, ink=None)
    if e.get('sweat'):
        poly(cv, [(-9, -9), (-7.4, -5), (-10.6, -5)], 0xFF9FE3FF, ow=1.2)
    if e.get('tear'):
        poly(cv, [(ex_n + 1, 5), (ex_n + 2.4, 9.5), (ex_n - 0.4, 9.5)], 0xFF9FE3FF, ow=1.0)


def draw_hand(cv, at, ang, kind, fill=COL['skin']):
    x, y = at
    cv.save()
    cv.translate(x, y)
    cv.rotate(-ang)
    if kind == 'point2':
        seg(cv, (0, 0), (0, 9), 2.2, fill, ow=1.6)
        seg(cv, (1.6, 0), (2.2, 8), 2.2, fill, ow=1.6)
        circle(cv, 0.4, 0, 3.6, fill, ow=2.0)
    elif kind == 'fist':
        circle(cv, 0, 1, 3.8, fill, ow=2.0)
        seg(cv, (-1.5, 1.2), (2, 1.2), 0.1, INK, ow=0.6)
    elif kind == 'hold':
        circle(cv, 0, 1, 3.8, fill, ow=2.0)
    else:  # open mitt + thumb
        oval(cv, 0, 3, 3.4, 4.8, fill, ow=2.0)
        seg(cv, (2.2, 0), (4.6, 2.4), 1.8, fill, ow=1.4)
        for fxx in (-1.2, 0.6):
            seg(cv, (fxx, 5.5), (fxx, 6.6), 0.1, INK, ow=0.5)
    cv.restore()


def draw_prop(cv, kind, hand, ang, t):
    if kind == 'journal':
        cv.save()
        cv.translate(hand[0] + 2, hand[1] - 2)
        cv.rotate(-10)
        poly(cv, [(-10, -7), (10, -7), (10, 7), (-10, 7)], COL['journal'], ow=2.0)
        seg(cv, (0, -7), (0, 7), 0.6, 0xFF8A6A3A, ow=0)
        for i in range(3):
            seg(cv, (-8, -3 + i * 3), (-2, -3 + i * 3), 0.6, 0xFF8A6A3A, ow=0)
        cv.restore()
    elif kind == 'flare':
        cv.save()
        cv.translate(*hand)
        cv.rotate(-ang + 90)
        poly(cv, [(-2, -3), (12, -3), (12, 1.6), (2, 1.6), (1, 6), (-3, 6)], COL['flare'], ow=2.0)
        circle(cv, 12, -0.7, 1.6, 0xFF2A2A2A, ow=1.0)
        cv.restore()


def scarf_tail(t, facing_motion, speed, wind, n=7):
    """Tail points (local, behind the neck). Procedural flutter, reacts to speed and wind."""
    pts = []
    stream = min(1.0, abs(speed) * 0.6 + abs(wind))
    for i in range(n):
        k = i / (n - 1)
        hang = 30 * k * (1 - stream * 0.85)
        back = -26 * k * (0.25 + stream)
        flutter = math.sin(t * (6 + 6 * stream) - k * 4.5) * (1.2 + 4.0 * stream) * k
        pts.append((back - flutter * 0.3, hang + flutter))
    return pts


def draw_kesta(cv, x, y, s, pose_, t, facing=1, expr='neutral', viseme='rest', look=(0.0, 0.0),
               blink=None, goggles='up', wind=0.0, speed=0.0, alpha=1.0, k_open=1.0, prop_glow=0.0):
    p = dict(BASE)
    p.update(pose_)
    if blink is None:
        # natural blink every ~3.7 s
        ph = (t + 0.37) % 3.7
        blink = 1.0 if ph < 0.09 else (0.5 if ph < 0.14 else 0.0)
    cv.save()
    if alpha < 1:
        cv.saveLayerAlpha(None, int(255 * alpha))
    cv.translate(x, y)
    cv.scale(s / 100.0 * facing, s / 100.0)
    breathe = math.sin(t * 2.2) * 0.6
    crouch = p['crouch']
    hip = (p['rx'], -44 + crouch + p['ry'])
    lean = p['lean']
    neck = (hip[0] + math.sin(math.radians(lean)) * 26, hip[1] - math.cos(math.radians(lean)) * 26 - breathe * 0.3)
    shF = (neck[0] + 3, neck[1] + 4)
    shB = (neck[0] - 5, neck[1] + 4)
    hipF, hipB = (hip[0] + 3, hip[1]), (hip[0] - 3, hip[1])

    def leg(base, foot, front):
        L1, L2 = 20.0, 21.0
        ank = (foot[0] - 1.0, foot[1] - 3.6)
        dx, dy = ank[0] - base[0], ank[1] - base[1]
        d = max(1e-3, min(L1 + L2 - 0.05, math.hypot(dx, dy)))
        a = math.atan2(dy, dx)
        c = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
        b = math.acos(max(-1, min(1, c)))
        ka = a - b  # knee bends forward (+x)
        knee = (base[0] + L1 * math.cos(ka), base[1] + L1 * math.sin(ka))
        if math.hypot(dx, dy) > L1 + L2:
            ank = (base[0] + (L1 + L2) * math.cos(a), base[1] + (L1 + L2) * math.sin(a))
        col = COL['pants'] if front else COL['pants_sh']
        seg(cv, base, knee, 9.5, col)
        boot_k = (lerp(knee[0], ank[0], 0.5), lerp(knee[1], ank[1], 0.5))
        seg(cv, knee, boot_k, 8.6, col)
        seg(cv, boot_k, ank, 8.0, COL['boots'] if front else 0xFF57341F)
        bc = COL['boots'] if front else 0xFF57341F
        poly(cv, [(ank[0] - 3.8, ank[1] - 3), (ank[0] + 6.5, ank[1] - 0.8), (ank[0] + 8.5, ank[1] + 3.4), (ank[0] - 4.2, ank[1] + 3.4)], bc, ow=2.2)
        seg(cv, (ank[0] - 4.2, ank[1] + 3.6), (ank[0] + 8.6, ank[1] + 3.6), 1.4, COL['sole'], ow=0.4)

    def arm(base, u, l, hand_kind, front):
        elb, wr = limb_pts(base, u, 15, l, 14)
        sleeve = COL['jacket'] if front else COL['jacket_sh']
        seg(cv, base, elb, 8.2, sleeve)
        cuff = (lerp(elb[0], wr[0], 0.18), lerp(elb[1], wr[1], 0.18))
        seg(cv, elb, cuff, 8.6, COL['jacket_sh'])
        seg(cv, cuff, wr, 6.0, COL['skin'] if front else COL['skin_sh'])
        draw_hand(cv, wr, u + l, hand_kind, COL['skin'] if front else COL['skin_sh'])
        return wr, u + l

    # scarf tail behind everything
    tail = scarf_tail(t, facing, speed, wind)
    tp = [(neck[0] - 4 + q[0], neck[1] + 3 + q[1]) for q in tail]
    path = skia.Path()
    path.moveTo(*tp[0])
    for q in tp[1:]:
        path.lineTo(*q)
    cv.drawPath(path, P(INK, 9.6))
    cv.drawPath(path, P(COL['scarf'], 6.0))
    cv.drawPath(path, P(COL['scarf_st'], 1.6))
    end = tp[-1]
    poly(cv, [(end[0] - 3, end[1] - 2), (end[0] + 3, end[1] - 2), (end[0] + 4, end[1] + 4), (end[0] - 4, end[1] + 4)], COL['scarf'], ow=1.8)

    arm(shB, p['aBu'], p['aBl'], p['hB'], False)
    leg(hipB, (p['fBx'] + p['rx'] * 0.3, p['fBy']), False)
    # torso: jacket
    tw = 10.5
    ang = math.radians(lean)
    ux, uy = math.sin(ang), -math.cos(ang)
    nx, ny = -uy, ux
    top = (neck[0] + ux * 1, neck[1] + uy * 1)
    bot = (hip[0] - ux * 3, hip[1] - uy * 3)
    torso = [(top[0] - nx * (tw - 1.5), top[1] - ny * (tw - 1.5)), (top[0] + nx * (tw - 0.5), top[1] + ny * (tw - 0.5)),
             (bot[0] + nx * (tw + 0.5), bot[1] + ny * (tw + 0.5)), (bot[0] - nx * (tw + 0.5), bot[1] - ny * (tw + 0.5))]
    poly(cv, torso, COL['jacket'])
    # shirt V + jacket opening (toward facing side)
    v = [(top[0] + nx * 1.5, top[1] + ny * 1.5), (top[0] + nx * 7.5, top[1] + ny * 7.5),
         (lerp(top[0], bot[0], 0.55) + nx * 4.5, lerp(top[1], bot[1], 0.55) + ny * 4.5)]
    poly(cv, v, COL['shirt'], ow=1.8)
    # satchel strap + bag
    seg(cv, (top[0] + nx * 8, top[1] + ny * 8), (bot[0] - nx * 9, bot[1] - ny * 9 - 2), 2.4, COL['strap'], ow=1.2)
    bag = (bot[0] - nx * 9.5, bot[1] - ny * 9.5 + 1)
    poly(cv, [(bag[0] - 6, bag[1] - 5), (bag[0] + 3, bag[1] - 5), (bag[0] + 3, bag[1] + 5), (bag[0] - 6, bag[1] + 5)], COL['satchel'], ow=2.0)
    seg(cv, (bag[0] - 6, bag[1] - 2), (bag[0] + 3, bag[1] - 2), 0.8, COL['strap'], ow=0)
    # belt line
    seg(cv, (bot[0] - nx * (tw + 0.5), bot[1] - ny * (tw + 0.5) - 1), (bot[0] + nx * (tw + 0.5), bot[1] + ny * (tw + 0.5) - 1), 1.0, COL['jacket_sh'], ow=0)
    leg(hipF, (p['fFx'] + p['rx'] * 0.3, p['fFy']), True)
    # scarf wrap at neck
    oval(cv, neck[0] + 1, neck[1] + 1, 9.5, 4.6, COL['scarf'], ow=2.2, ang=lean * 0.5)
    seg(cv, (neck[0] - 7, neck[1] + 1.5), (neck[0] + 8, neck[1] + 0.5), 1.4, COL['scarf_st'], ow=0)
    # scarf front end hangs over the chest and swings with motion
    sw = math.sin(t * 3.1) * 1.2 + speed * 3 + wind * 4
    fe = [(neck[0] + 5, neck[1] + 3), (neck[0] + 6.5 - sw * 0.3, neck[1] + 10), (neck[0] + 7 - sw, neck[1] + 17)]
    path = skia.Path()
    path.moveTo(*fe[0]); path.quadTo(*fe[1], *fe[2])
    cv.drawPath(path, P(INK, 7.6 * 1.0))
    cv.drawPath(path, P(COL['scarf'], 5.2))
    cv.drawPath(path, P(COL['scarf_st'], 1.3))
    for k in (-1.6, 0, 1.6):
        seg(cv, (fe[2][0] + k, fe[2][1] + 1), (fe[2][0] + k - sw * 0.2, fe[2][1] + 3.2), 0.7, COL['scarf_sh'], ow=0)
    # head
    cv.save()
    head_ang = p['head'] + p['nod'] * 0.4 + lean * 0.3 + math.sin(t * 1.3) * 0.8
    cv.translate(neck[0] + 1, neck[1] - 1)
    cv.rotate(head_ang)
    cv.translate(0, -15)
    draw_head(cv, p, t, facing, expr, viseme, look, blink, goggles, k_open)
    cv.restore()
    # front arm + prop
    wr, a = arm(shF, p['aFu'], p['aFl'], p['hF'], True)
    if p.get('prop'):
        draw_prop(cv, p['prop'], wr, a, t)
        if p['prop'] == 'flare' and prop_glow > 0:
            g = skia.Paint(AntiAlias=True, Color=0xFFFFB000)
            g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
            g.setAlphaf(min(1, prop_glow))
            cv.drawCircle(wr[0] + math.sin(math.radians(a)) * 12, wr[1] + math.cos(math.radians(a)) * 12, 6 + 8 * prop_glow, g)
    if alpha < 1:
        cv.restore()
    cv.restore()
