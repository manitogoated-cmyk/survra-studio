"""Five mascot concepts for Survra's host. Strictly 2D vector drawing (Skia), one draw function per character.
draw(name, cv, x, y, s, view='front'|'side'|'back', expr=<EX key>, pose=<POSES key>)
Units: feet at y=0, character about 100 units tall; s = pixels per unit."""
import math

import skia

INK = 0xFF1B1730
FX = {'glow': True}


def P(c, sw=None, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=c)
    if a < 1:
        p.setAlphaf(p.getAlphaf() * a)
    if sw:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(sw)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def smooth(pts, closed=True):
    n = len(pts)
    path = skia.Path()
    path.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[0]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[-1]
        path.cubicTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                     p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1])
    if closed:
        path.close()
    return path


def poly(pts, closed=True):
    path = skia.Path()
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    if closed:
        path.close()
    return path


def fs(cv, path, fill, ow=1.2, ink=INK):
    if fill is not None:
        cv.drawPath(path, P(fill))
    if ow:
        cv.drawPath(path, P(ink, ow))


def hose(cv, pts, w, fill, ow=1.2, ink=INK, straight=False):
    path = poly(pts, False) if straight or len(pts) < 3 else smooth(pts, False)
    cv.drawPath(path, P(ink, w + 2 * ow))
    cv.drawPath(path, P(fill, w))


def limb(cv, a, b, w, fill, bend=0.22, ow=1.2):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    path = skia.Path()
    path.moveTo(*a)
    path.quadTo(mx - dy * bend, my + dx * bend, b[0], b[1])
    cv.drawPath(path, P(INK, w + 2 * ow))
    cv.drawPath(path, P(fill, w))


def oval(cv, x, y, rx, ry, fill, ow=1.2, ink=INK, rot=0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    r = skia.Rect.MakeLTRB(-rx, -ry, rx, ry)
    if fill is not None:
        cv.drawOval(r, P(fill))
    if ow:
        cv.drawOval(r, P(ink, ow))
    cv.restore()


def ovalpath(x, y, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry))
    return p


# ------------------------------------------------------------------ expressions (shared acting language)
EX = {
    'happy':    dict(lt=0.0, lb=0.22, bh=-1, bt=-3, m='grin'),
    'laugh':    dict(closed=1, bh=-2, bt=-4, m='laugh', blush=1),
    'awe':      dict(lt=0, bh=-4, bt=-6, ps=1.25, sparkle=1, m='o', wide=1),
    'curious':  dict(lt=0.05, bh=-1, bt=0, asym=3, look=(0.6, -0.3), m='smile'),
    'smirk':    dict(lt=0.42, lb=0.15, bh=1, bt=3, asym=2.5, look=(0.7, 0), m='smirk'),
    'deadpan':  dict(lt=0.5, bh=2, bt=0, ps=0.9, m='flat'),
    'shocked':  dict(lt=0, bh=-6, bt=0, ps=0.45, m='gasp', wide=1),
    'scared':   dict(lt=0, bh=-3, bt=-11, ps=0.5, m='teeth', sweat=1, wide=1),
    'sad':      dict(lt=0.3, bh=-1, bt=-13, ps=1.1, look=(0, 0.6), m='frown', tear=1),
    'angry':    dict(lt=0.3, lb=0.2, bh=3, bt=15, ps=0.8, m='teeth', anger=1),
    'thinking': dict(lt=0.2, lb=0.1, bh=0, bt=4, asym=3, look=(-0.7, -0.7), m='pout'),
    'wink':     dict(wink=1, lb=0.2, bh=-1, bt=-3, m='grin'),
}

POSES = {
    'stand': dict(hl=(-5, 19), hr=(5, 19), fl=(0, 0), fr=(0, 0), tilt=0, lift=0),
    'cheer': dict(hl=(-12, -25), hr=(12, -25), fl=(-3, -7), fr=(4, -4), tilt=0, lift=-9),
    'point': dict(hl=(-7, 13), hr=(27, -7), fl=(0, 0), fr=(4, 0), tilt=4, lift=0),
    'run':   dict(hl=(-15, 3), hr=(16, -3), fl=(-13, -7), fr=(12, -1), tilt=14, lift=-3),
    'shrug': dict(hl=(-17, -4), hr=(17, -4), fl=(0, 0), fr=(0, 0), tilt=0, lift=0),
    'think': dict(hl=(4, 12), hr=(-8, -13), fl=(0, 0), fr=(0, 0), tilt=-3, lift=0),
}


def eye(cv, x, y, rx, ry, E, st, side):
    line = st.get('line', INK)
    if E.get('closed') or (E.get('wink') and side > 0):
        path = skia.Path()
        path.moveTo(x - rx, y + ry * 0.2)
        path.quadTo(x, y - ry * 0.9, x + rx, y + ry * 0.2)
        cv.drawPath(path, P(line, st['fow'] * 1.5))
        return
    ps = E.get('ps', 1.0)
    white = st.get('white')
    dot = white is None
    if dot and ps < 0.7:           # dot eyes pop wide when shocked
        dot, white = False, 0xFFFFFFFF
        rx, ry = rx * 1.12, ry * 1.12
    lt = E.get('lt', 0)
    if not E.get('wide'):
        lt = max(lt, st.get('min_lid', 0))
    lb = E.get('lb', 0)
    lx, ly = E.get('look', (0, 0))
    path = ovalpath(x, y, rx, ry)
    cv.save()
    cv.clipPath(path, True)
    if dot:
        cv.drawPaint(P(st['pupil']))
        cv.drawCircle(x - rx * 0.28 + lx * rx * 0.2, y - ry * 0.38 + ly * ry * 0.15, rx * 0.34, P(0xFFFFFFFF))
        cv.drawCircle(x + rx * 0.3 + lx * rx * 0.2, y + ry * 0.3, rx * 0.16, P(0xFFFFFFFF))
    else:
        cv.drawPaint(P(white))
        r = min(rx, ry) * 0.62 * ps
        px, py = x + lx * rx * 0.36, y + ly * ry * 0.3
        if st.get('iris') and ps > 0.7:
            cv.drawCircle(px, py, r * 1.45, P(st['iris']))
        cv.drawCircle(px, py, r, P(st['pupil']))
        cv.drawCircle(px - r * 0.35, py - r * 0.4, r * 0.38, P(0xFFFFFFFF))
    if E.get('sparkle'):
        cv.drawCircle(x + rx * 0.3, y + ry * 0.35, rx * 0.2, P(0xFFFFFFFF))
        cv.drawCircle(x - rx * 0.1, y - ry * 0.1, rx * 0.12, P(0xFFFFFFFF))
    lid = st['lid']
    if lt > 0.01:
        cv.drawRect(skia.Rect.MakeLTRB(x - rx - 1, y - ry - 1, x + rx + 1, y - ry + 2 * ry * lt), P(lid))
        cv.drawLine(x - rx, y - ry + 2 * ry * lt, x + rx, y - ry + 2 * ry * lt, P(line, st['fow']))
    if lb > 0.01:
        cv.drawRect(skia.Rect.MakeLTRB(x - rx - 1, y + ry - 2 * ry * lb, x + rx + 1, y + ry + 1), P(lid))
        cv.drawLine(x - rx, y + ry - 2 * ry * lb, x + rx, y + ry - 2 * ry * lb, P(line, st['fow'] * 0.8))
    cv.restore()
    if st.get('eye_out', True):
        cv.drawPath(path, P(line, st['fow']))


def mouth(cv, x, y, w, kind, st):
    line = st.get('line', INK)
    ow = st['fow']
    inside = st.get('mouth_in', 0xFF7A1F2B)
    if kind in ('grin', 'laugh'):
        h = w * (0.62 if kind == 'laugh' else 0.42)
        path = skia.Path()
        path.moveTo(x - w / 2, y)
        path.lineTo(x + w / 2, y)
        path.cubicTo(x + w / 2, y + h * 1.3, x - w / 2, y + h * 1.3, x - w / 2, y)
        path.close()
        cv.drawPath(path, P(inside))
        cv.save()
        cv.clipPath(path, True)
        cv.drawRect(skia.Rect.MakeLTRB(x - w / 2, y, x + w / 2, y + h * 0.3), P(0xFFFFFFFF))
        cv.drawOval(skia.Rect.MakeLTRB(x - w * 0.28, y + h * 0.55, x + w * 0.28, y + h * 1.4), P(0xFFFF7B8E))
        cv.restore()
        cv.drawPath(path, P(line, ow))
    elif kind in ('o', 'gasp'):
        rx, ry = (w * 0.2, w * 0.24) if kind == 'o' else (w * 0.3, w * 0.42)
        path = ovalpath(x, y + ry * 0.6, rx, ry)
        cv.drawPath(path, P(inside))
        if kind == 'gasp':
            cv.save()
            cv.clipPath(path, True)
            cv.drawOval(skia.Rect.MakeLTRB(x - rx * 0.7, y + ry * 0.9, x + rx * 0.7, y + ry * 2), P(0xFFFF7B8E))
            cv.restore()
        cv.drawPath(path, P(line, ow))
    elif kind == 'teeth':
        r = skia.Rect.MakeLTRB(x - w * 0.42, y - w * 0.02, x + w * 0.42, y + w * 0.3)
        cv.drawRoundRect(r, w * 0.1, w * 0.1, P(0xFFFFFFFF))
        cv.drawRoundRect(r, w * 0.1, w * 0.1, P(line, ow))
        for k in (-0.2, 0, 0.2):
            cv.drawLine(x + w * k, y, x + w * k, y + w * 0.28, P(line, ow * 0.7))
        cv.drawLine(x - w * 0.42, y + w * 0.14, x + w * 0.42, y + w * 0.14, P(line, ow * 0.7))
    else:
        path = skia.Path()
        if kind == 'smile':
            path.moveTo(x - w * 0.4, y)
            path.quadTo(x, y + w * 0.4, x + w * 0.4, y)
        elif kind == 'frown':
            path.moveTo(x - w * 0.35, y + w * 0.22)
            path.quadTo(x, y - w * 0.12, x + w * 0.35, y + w * 0.22)
        elif kind == 'flat':
            path.moveTo(x - w * 0.3, y + w * 0.1)
            path.lineTo(x + w * 0.3, y + w * 0.1)
        elif kind == 'smirk':
            path.moveTo(x - w * 0.3, y + w * 0.12)
            path.quadTo(x + w * 0.15, y + w * 0.3, x + w * 0.45, y - w * 0.12)
            path.moveTo(x + w * 0.4, y - w * 0.22)
            path.lineTo(x + w * 0.52, y - w * 0.06)
        else:  # pout
            path.moveTo(x + w * 0.0, y + w * 0.18)
            path.quadTo(x + w * 0.18, y + w * 0.02, x + w * 0.36, y + w * 0.16)
        cv.drawPath(path, P(line, ow * 1.35))


def face(cv, x, y, E, st, fx=0.0, near=(1.0, 1.0)):
    """Eyes centred on (x+fx, y). near = rx scale for (left, right) eye (side views)."""
    line = st.get('line', INK)
    dx, rx, ry = st['dx'], st['rx'], st['ry']
    x += fx
    if E.get('blush'):
        for s_ in (-1, 1):
            oval(cv, x + s_ * (dx + rx * 0.3), y + ry + 1.2, rx * 0.7, ry * 0.28, 0x66FF5C7A, ow=0)
    for s_, k in ((-1, near[0]), (1, near[1])):
        eye(cv, x + s_ * dx * (0.5 + 0.5 * k), y, rx * k, ry, E, st, s_)
        if st.get('brow', True):
            bx = x + s_ * dx * (0.5 + 0.5 * k)
            by = y - ry - 1.8 + E.get('bh', 0) * 0.5 - (E.get('asym', 0) * 0.5 if s_ > 0 else 0)
            t = E.get('bt', 0) * 0.13
            hw = rx * k
            cv.drawLine(bx - hw, by + (t if s_ > 0 else -t), bx + hw, by + (-t if s_ > 0 else t), P(st.get('browc', line), st['fow'] * 1.7))
    mouth(cv, x + st.get('mx', 0), y + st['my'], st['mw'], E['m'], st)
    if E.get('sweat'):
        px, py = x + dx + rx + 2.5, y - ry - 1
        fs(cv, smooth([(px, py - 3.5), (px + 1.8, py + 0.6), (px, py + 2.2), (px - 1.8, py + 0.6)]), 0xFF8FDCFF, 0.6)
    if E.get('tear'):
        px, py = x + dx, y + ry + 2.6
        fs(cv, smooth([(px, py - 2.6), (px + 1.5, py + 0.6), (px, py + 2), (px - 1.5, py + 0.6)]), 0xFF8FDCFF, 0.6)
    if E.get('anger'):
        px, py = x + dx + rx + 2, y - ry - 5
        for a in range(4):
            cv.save()
            cv.translate(px, py)
            cv.rotate(a * 90)
            pth = skia.Path()
            pth.moveTo(0.8, 2.8)
            pth.quadTo(0.8, 0.8, 2.8, 0.8)
            cv.drawPath(pth, P(0xFFE5261F, 1.1))
            cv.restore()


def frame(p, w=1.0, sx=13, sy=-45, hx=6, hy=-20, fx=8):
    sh = [(-sx * w, sy), (sx * w, sy)]
    hands = [(sh[0][0] + p['hl'][0], sy + p['hl'][1]), (sh[1][0] + p['hr'][0], sy + p['hr'][1])]
    hips = [(-hx * w, hy), (hx * w, hy)]
    feet = [(-fx * w + p['fl'][0], p['fl'][1]), (fx * w + p['fr'][0], p['fr'][1])]
    return sh, hands, hips, feet


# =================================================================== 1. QUIP - the kid who is a question mark
def quip(cv, v, en, pose):
    E, p = EX[en], POSES.get(pose, POSES['stand'])
    SK, HAIR, HOOD, HOOD2, SHORT, RED = 0xFFF0AE7B, 0xFFFF5A36, 0xFF18BFAE, 0xFF0F978B, 0xFF2B2F5A, 0xFFFF5A36
    side, back = v == 'side', v == 'back'
    w = 0.8 if side else 1.0
    sh, hands, hips, feet = frame(p, w, hy=-19)
    cv.translate(0, p['lift'])
    cv.rotate(p['tilt'])
    st = dict(dx=8.6, rx=5.2, ry=6.6, white=0xFFFFFFFF, pupil=INK, lid=SK, fow=0.95, my=10.5, mw=12)
    if side:
        limb(cv, sh[0], hands[0], 7, HOOD2)
        oval(cv, hands[0][0], hands[0][1], 4.4, 4.4, SK)
    for (hx_, hy_), (fx_, fy_) in zip(hips, feet):
        limb(cv, (hx_, hy_), (fx_, fy_ - 3.5), 5.4, SK, 0.05)
        oval(cv, fx_ + (2 if not back else 0) * (1 if side else (1 if fx_ > 0 else -1)), fy_ - 2.6, 8, 4.4, 0xFFFFFFFF)
        cv.drawLine(fx_ - 5, fy_ + 0.6, fx_ + 8, fy_ + 0.6, P(RED, 1.6))
    fs(cv, smooth([(-14 * w, -27), (14 * w, -27), (14 * w, -18), (-14 * w, -18)]), SHORT)
    if side:
        oval(cv, -13, -50, 9, 8, HOOD2)
    fs(cv, smooth([(-13 * w, -47), (13 * w, -47), (16.5 * w, -34), (16 * w, -23.5), (-16 * w, -23.5), (-16.5 * w, -34)]), HOOD)
    if back:
        hose(cv, [(0, -30), (0, -34), (4, -37), (4.5, -41), (0, -43.5), (-4.5, -41)], 1.6, HOOD2, 0)
        cv.drawCircle(0, -26.5, 1.1, P(HOOD2))
    else:
        fs(cv, smooth([(-8 * w, -34), (8 * w, -34), (9 * w, -26.5), (-9 * w, -26.5)]), None, 0.8, HOOD2)
        for s_ in (-1, 1):
            cv.drawLine(s_ * 3.5 * w + (4 if side else 0), -46, s_ * 4 * w + (4 if side else 0), -38, P(0xFFFFFFFF, 1.1))
    if not side:
        for s_, hnd, shd in ((-1, hands[0], sh[0]), (1, hands[1], sh[1])):
            limb(cv, shd, hnd, 7, HOOD, 0.22 * s_)
            oval(cv, hnd[0], hnd[1], 4.5, 4.5, SK)
    # head
    hy = -64
    if not side:
        for s_ in (-1, 1):
            oval(cv, s_ * 21, hy + 2, 3.6, 4.2, SK)
    else:
        oval(cv, -3, hy + 2, 3.4, 4.2, SK)
        oval(cv, 20.5, hy + 4, 3, 2.6, SK)
    head = ovalpath(0, hy, 21, 18)
    fs(cv, head, HAIR if back else SK)
    if back:
        fs(cv, smooth([(-16, -50), (0, -46.5), (16, -50), (12, -43), (-12, -43)]), HOOD2)
    else:
        fringe = [(-21.5, -65), (-20, -76), (-12, -82.6), (0, -84.2), (12, -82.6), (20, -76), (21.5, -65),
                  (15.5, -72), (10, -67.5), (4, -73), (-3, -68), (-9, -73.5), (-16, -68)]
        if side:
            fringe = [(-21.5, -58)] + fringe[1:]
        fr = poly([(-30, -65 if not side else -58), (-30, -95), (30, -95), (30, -65)] + fringe[7:])
        fs(cv, skia.Op(fr, ovalpath(0, hy - 0.6, 22.2, 19.4), skia.PathOp.kIntersect_PathOp), HAIR)
        face(cv, 0, hy + 1, E, st, fx=6.5 if side else 0, near=(0.8, 0.8) if side else (1, 1))
        if not side:
            for q in ((-13, -57.5), (-10.5, -56.5), (13, -57.5), (10.5, -56.5)):
                cv.drawCircle(q[0], q[1], 0.55, P(0xFFC97F4F))
    # the curl: "?" normally, snaps to "!" on shock, zig-zags when angry/scared, droops when sad
    kind = {'shocked': '!', 'awe': '!', 'scared': 'zig', 'angry': 'zig', 'sad': 'droop'}.get(en, '?')
    shapes = {'?': [(0, 1), (0, -6), (6, -10), (10, -17), (7, -25), (-1, -28), (-8, -24), (-10, -18)],
              '!': [(0, 1), (0, -30)], 'zig': [(0, 1), (-5, -8), (5, -14), (-5, -21), (4, -29)],
              'droop': [(0, 1), (1, -8), (8, -13), (15, -9), (17, -1), (14, 5)]}
    m = -1 if back else 1
    hose(cv, [(m * a, -82 + b) for a, b in shapes[kind]], 5.6, HAIR, straight=kind in ('!', 'zig'))
    if side:
        limb(cv, sh[1], hands[1], 7, HOOD, 0.22)
        oval(cv, hands[1][0], hands[1][1], 4.5, 4.5, SK)


# =================================================================== 2. WICK - the living lantern
def wick(cv, v, en, pose):
    E, p = EX[en], POSES.get(pose, POSES['stand'])
    RED, RED2, GLASS, BRASS, COAT, COAT2, GLOVE, BOOT = 0xFFE8402F, 0xFFB52A20, 0xFFFFF6D6, 0xFFF2B531, 0xFF2C4F7C, 0xFF1D3657, 0xFFFFC83D, 0xFF4A2F22
    side, back = v == 'side', v == 'back'
    w = 0.82 if side else 1.0
    sh, hands, hips, feet = frame(p, w, sx=11, sy=-38, hx=5, hy=-17, fx=7)
    cv.translate(0, p['lift'])
    cv.rotate(p['tilt'])
    mood = {'angry': (0xFFE5261F, 0xFFFF9A2E, 1.18), 'sad': (0xFF3B8BEA, 0xFFA6DAFF, 0.72), 'shocked': (0xFFFFD54A, 0xFFFFFFFF, 1.2),
            'scared': (0xFFB9A8FF, 0xFFEDE6FF, 0.66), 'awe': (0xFFFFA21F, 0xFFFFF0A0, 1.12), 'laugh': (0xFFFF8A1F, 0xFFFFE066, 1.1)}.get(en, (0xFFFF8A1F, 0xFFFFD84A, 1.0))
    if FX['glow']:
        g = skia.GradientShader.MakeRadial(skia.Point(0, -62), 40, [(mood[1] & 0xFFFFFF) | 0x88000000, mood[1] & 0xFFFFFF])
        cv.drawCircle(0, -62, 40, skia.Paint(AntiAlias=True, Shader=g))
    if side:
        limb(cv, sh[0], hands[0], 6, COAT2)
        oval(cv, hands[0][0], hands[0][1], 4.4, 4.4, GLOVE)
    for (hx_, hy_), (fx_, fy_) in zip(hips, feet):
        limb(cv, (hx_, hy_), (fx_, fy_ - 3.5), 5, COAT2, 0.05)
        oval(cv, fx_ + (1.5 if side else (1.5 if fx_ > 0 else -1.5)), fy_ - 2.6, 7.4, 4.4, BOOT)
    fs(cv, smooth([(-10 * w, -42), (10 * w, -42), (14 * w, -28), (15.5 * w, -16.5), (-15.5 * w, -16.5), (-14 * w, -28)]), COAT)
    if back:
        cv.drawLine(0, -40, 0, -17, P(COAT2, 1))
        cv.drawLine(-14, -26, 14, -26, P(BRASS, 2))
    else:
        o = 5 if side else 0
        for by in (-36, -29.5, -23):
            cv.drawCircle(o, by, 1.5, P(BRASS))
            cv.drawCircle(o, by, 1.5, P(INK, 0.6))
    if not side:
        for s_, hnd, shd in ((-1, hands[0], sh[0]), (1, hands[1], sh[1])):
            limb(cv, shd, hnd, 6, COAT, 0.22 * s_)
            oval(cv, hnd[0], hnd[1], 4.5, 4.5, GLOVE)
    # lantern head
    if side:
        oval(cv, 0, -95, 2.4, 7, None, 2.6)
        oval(cv, 0, -95, 2.4, 7, None, 1.0, BRASS)
    else:
        cv.drawCircle(0, -95, 7, P(INK, 3))
        cv.drawCircle(0, -95, 7, P(BRASS, 1.2))
    for s_ in (-1, 1):
        g = skia.Path()
        g.moveTo(s_ * 13, -45)
        g.quadTo(s_ * 27, -62, s_ * 11, -82)
        cv.drawPath(g, P(INK, 1.5))
    glass = smooth([(-12, -46.5), (-19.5, -57), (-18.5, -70), (-11, -79.5), (11, -79.5), (18.5, -70), (19.5, -57), (12, -46.5)])
    cv.drawPath(glass, P(GLASS, a=0.92))
    fsz = mood[2]
    lean = 2.5 if side else 0

    def flame(k, col):
        pts = [(0 + lean * 2, -27), (5 + lean, -20.5), (10, -13.5), (11, -5.5), (6, 0), (-6, 0), (-11, -5.5), (-10, -13.5), (-4, -20), (-2.5 + lean, -24)]
        fs(cv, smooth([(a * k * (0.95 if fsz > 1.1 else 1), -49.5 + b * k * fsz) for a, b in pts]), col, 0.9 if k == 1 else 0, 0xFFB5451A)
    flame(1, mood[0])
    flame(0.6, mood[1])
    if not back:
        st = dict(dx=4.6, rx=2.5, ry=3.3, white=None, pupil=0xFF4A1A0A, lid=mood[0], fow=0.7, my=6.2, mw=7.5, line=0xFF4A1A0A, mouth_in=0xFF7A1F1F)
        face(cv, 0, -58.5, E, st, fx=4 if side else 0, near=(0.8, 0.9) if side else (1, 1))
    hl = skia.Path()
    hl.moveTo(-14.5, -60)
    hl.quadTo(-15, -70, -9, -75.5)
    cv.drawPath(hl, P(0xFFFFFFFF, 2.2, 0.85))
    cv.drawPath(glass, P(INK, 1.2))
    fs(cv, smooth([(-13.5, -47.5), (13.5, -47.5), (13, -41.5), (-13, -41.5)]), RED)
    fs(cv, poly([(-13, -79), (13, -79), (9, -86), (-9, -86)]), RED)
    fs(cv, poly([(-5, -86), (5, -86), (4.4, -90), (-4.4, -90)]), RED2)
    if back:
        fs(cv, poly([(-4, -46.4), (4, -46.4), (4, -42.6), (-4, -42.6)]), RED2, 0.7)
        for k in (-5, 0, 5):
            cv.drawCircle(k, -82.5, 0.9, P(INK))
    if side:
        limb(cv, sh[1], hands[1], 6, COAT, 0.22)
        oval(cv, hands[1][0], hands[1][1], 4.5, 4.5, GLOVE)


# =================================================================== 3. MOTHEW - the unimpressed moth
def mothew(cv, v, en, pose):
    E, p = EX[en], POSES.get(pose, POSES['stand'])
    CREAM, CREAM2, FLUFF, WING, WING2, SPOT, BROWN, EYE = 0xFFF8EACB, 0xFFE6CFA2, 0xFFFFFCF2, 0xFF6F4FD0, 0xFF4B309E, 0xFFFFA62B, 0xFF5A3A2A, 0xFF2A1B3D
    side, back = v == 'side', v == 'back'
    w = 0.85 if side else 1.0
    sh, hands, hips, feet = frame(p, w, sx=12, sy=-40, hx=5, hy=-13, fx=7)
    cv.translate(0, p['lift'])
    cv.rotate(p['tilt'])
    flap = 1.12 if pose in ('cheer', 'run') else 1.0

    def spot(x, y, r=6.5):
        oval(cv, x, y, r, r, SPOT, 1.0)
        oval(cv, x, y, r * 0.48, r * 0.48, EYE, 0)
        cv.drawCircle(x - r * 0.15, y - r * 0.18, r * 0.14, P(0xFFFFFFFF))

    def wings(closed=False):
        for s_ in (-1, 1):
            inner = 0 if closed else 10
            fs(cv, smooth([(s_ * inner, -22), (s_ * 28 * flap, -13), (s_ * 27 * flap, 3), (s_ * (2 if closed else 12), -3)]), WING2)
            fs(cv, smooth([(s_ * inner, -47), (s_ * 30 * flap, -59 * flap + 59 - 59), (s_ * 46 * flap, -51), (s_ * 44 * flap, -29), (s_ * 29, -9), (s_ * (0 if closed else 11), -14)]), WING)
            e = smooth([(s_ * 38 * flap, -50), (s_ * 42 * flap, -32), (s_ * 31, -14)], False)
            cv.drawPath(e, P(0xFFB9A4FF, 1.6))
            spot(s_ * 30 * (flap if not closed else 0.8), -36)
    if side:
        fs(cv, smooth([(-2, -47), (-24, -52), (-40, -32), (-35, -3), (-14, -7), (-4, -20)]), WING)
        cv.drawPath(smooth([(-33, -40), (-36, -18), (-22, -8)], False), P(0xFFB9A4FF, 1.6))
        spot(-22, -31)
    elif not back:
        wings()
    if side:
        limb(cv, sh[0], hands[0], 2.6, BROWN)
        oval(cv, hands[0][0], hands[0][1], 2.8, 2.8, BROWN)
    for (hx_, hy_), (fx_, fy_) in zip(hips, feet):
        limb(cv, (hx_, hy_), (fx_, fy_ - 2), 2.8, BROWN, 0.05)
        oval(cv, fx_ + (1.5 if side or fx_ > 0 else -1.5), fy_ - 1.6, 4.6, 2.3, BROWN)
    body = ovalpath(0, -28, 14.5 * w, 17)
    fs(cv, body, CREAM)
    if not back:
        for by in (-24, -17):
            a = skia.Path()
            a.moveTo(-9 * w, by)
            a.quadTo(0, by + 4, 9 * w, by)
            cv.drawPath(a, P(CREAM2, 1.2))
    if back:
        wings(closed=True)
    if not side:
        for s_, hnd, shd in ((-1, hands[0], sh[0]), (1, hands[1], sh[1])):
            limb(cv, shd, hnd, 2.6, BROWN, 0.22 * s_)
            oval(cv, hnd[0], hnd[1], 2.9, 2.9, BROWN)
    for i in range(9):
        oval(cv, (-16 + i * 4) * w, -45.5 + abs(i - 4) * 0.9, 5.6, 5.6, FLUFF, 1.0)
    for i in range(7):
        oval(cv, (-12 + i * 4) * w, -43.5, 4.6, 4.6, FLUFF, 0)
    # antennae act like eyebrows
    mode = {'sad': 'droop', 'scared': 'droop', 'angry': 'vee', 'deadpan': 'flat', 'curious': 'mix', 'thinking': 'mix', 'smirk': 'mix'}.get(en, 'up')
    for s_ in (-1, 1):
        tip = {'up': (17, -104), 'droop': (27, -82), 'vee': (9, -105), 'flat': (25, -93), 'mix': (17, -104) if s_ < 0 else (26, -86)}[mode]
        bx, by = s_ * 6 + (5 if side else 0), -77
        tx, ty = s_ * tip[0] + (9 if side else 0), tip[1]
        dx, dy = tx - bx, ty - by
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * 4.6, dx / L * 4.6
        mx, my = bx + dx * 0.55, by + dy * 0.55
        fs(cv, smooth([(bx, by), (mx + nx, my + ny), (tx, ty), (mx - nx, my - ny)]), 0xFF9A6A42, 1.0)
        cv.drawLine(bx, by, tx, ty, P(BROWN, 0.9))
        for k in (0.3, 0.5, 0.7):
            qx, qy = bx + dx * k, by + dy * k
            cv.drawLine(qx - nx * 0.6, qy - ny * 0.6, qx + nx * 0.6, qy + ny * 0.6, P(BROWN, 0.7))
    oval(cv, 0, -63, 17, 16.5, CREAM)
    if not back:
        st = dict(dx=8, rx=6.2, ry=7.6, white=None, pupil=EYE, lid=CREAM, fow=0.9, my=11.5, mw=8.5, min_lid=0.3, mouth_in=0xFF5A2440)
        face(cv, 0, -63.5, E, st, fx=5.5 if side else 0, near=(0.75, 0.9) if side else (1, 1))
    if side:
        limb(cv, sh[1], hands[1], 2.6, BROWN, 0.22)
        oval(cv, hands[1][0], hands[1][1], 2.9, 2.9, BROWN)


# =================================================================== 4. JOT - living ink that becomes anything
def jot(cv, v, en, pose):
    E, p = EX[en], POSES.get(pose, POSES['stand'])
    INKC, SHINE, GOLD, GOLD2 = 0xFF1D1A33, 0xFF62E3F0, 0xFFFFC233, 0xFFB77A0C
    side, back = v == 'side', v == 'back'
    st = dict(dx=8, rx=6, ry=7.6, white=0xFFFFFFFF, pupil=INKC, lid=INKC, fow=0.9, my=21.5, mw=11, line=0xFFFFFFFF, mouth_in=0xFFFF3E8A, eye_out=False)

    def nib(x, y, k=1.0):
        pth = skia.Path()
        pth.moveTo(x - 4.2 * k, y - 2)
        pth.quadTo(x - 4.2 * k, y - 6, x, y - 6)
        pth.quadTo(x + 4.2 * k, y - 6, x + 4.2 * k, y - 2)
        pth.lineTo(x, y + 6.5)
        pth.close()
        fs(cv, pth, GOLD, 0.8, GOLD2)
        cv.drawLine(x, y + 6, x, y - 1, P(GOLD2, 0.7))
        cv.drawCircle(x, y - 2, 0.95, P(GOLD2))

    def shine(pts):
        cv.drawPath(smooth(pts, False), P(SHINE, 2.2, 0.9))

    if pose == 'rocket':      # morph: Jot becomes the thing he is talking about
        cv.rotate(28)
        fs(cv, smooth([(0, -70), (11, -52), (13, -24), (10, -8), (-10, -8), (-13, -24), (-11, -52)]), INKC)
        for s_ in (-1, 1):
            fs(cv, smooth([(s_ * 12, -26), (s_ * 24, -8), (s_ * 22, 0), (s_ * 10, -9)]), INKC)
        fs(cv, smooth([(-6, -7), (0, 14), (6, -7)]), 0xFFFF8A1F, 0.9, 0xFFB5451A)
        fs(cv, smooth([(-3, -7), (0, 6), (3, -7)]), 0xFFFFD84A, 0)
        shine([(-8, -36), (-7.5, -50), (-3, -60)])
        st2 = dict(st, dx=5, rx=3.8, ry=5, my=14, mw=8)
        face(cv, 0, -44, EX['awe'], st2)
        nib(0, -35, 0.7)
        return
    if pose == 'puddle':      # melts flat when terrified
        fs(cv, smooth([(-34, -2), (-26, -9), (-10, -12), (10, -12), (26, -9), (34, -2), (20, 2), (0, 3), (-20, 2)]), INKC)
        shine([(-24, -5), (-14, -8.5), (-4, -9.5)])
        st2 = dict(st, dx=7, rx=5, ry=5.6, my=6.5, mw=7)
        face(cv, 0, -13, EX['scared'], st2)
        nib(0, -6.5, 0.6)
        return
    sh, hands, _, _ = frame(p, 1.0, sx=17, sy=-27)
    cv.translate(0, p['lift'] * 0.4)
    cv.rotate(p['tilt'])
    stretch = 1.22 if pose == 'cheer' else 1.0
    body = [(-18, -1), (-21, -14), (-18, -32), (-10, -47), (0, -52), (10, -47), (18, -32), (21, -14), (18, -1), (11, 1.5), (4, -1.2), (-4, -1.2), (-11, 1.5)]
    for s_, hnd, shd in ((-1, hands[0], sh[0]), (1, hands[1], sh[1])):
        if side and s_ < 0:
            continue
        far = 1.35 if pose == 'point' and s_ > 0 else 1.0
        hnd = (shd[0] + (hnd[0] - shd[0]) * far, (shd[1] + (hnd[1] - shd[1]) * far) * stretch)
        limb(cv, (shd[0] * 0.8, shd[1] * stretch), hnd, 3.4, INKC, 0.25 * s_)
        oval(cv, hnd[0], hnd[1], 3.8, 3.8, INKC)
    fs(cv, smooth([(a * (0.9 if stretch > 1 else 1), b * stretch) for a, b in body]), INKC)
    m = -1 if back else 1
    hose(cv, [(m * a, b * stretch) for a, b in [(0, -50), (-1, -58), (4, -65), (10, -63), (9, -57)]], 4.4, INKC)
    shine([(m * -16.5, -22 * stretch), (m * -15.5, -33 * stretch), (m * -10.5, -43 * stretch)])
    cv.drawCircle(m * -17, -15 * stretch, 1.3, P(SHINE))
    if back:
        return
    f = 3.5 if side else 0
    face(cv, 0, -32 * stretch, E, st, fx=f, near=(0.7, 0.8) if side else (1, 1))
    if side:
        fs(cv, poly([(18, -27), (31, -21.5), (18.5, -18.5)]), GOLD, 0.8, GOLD2)
        cv.drawLine(20, -22.8, 30, -21.6, P(GOLD2, 0.7))
    else:
        nib(0, -19.5 * stretch)


# =================================================================== 5. BOLO - the pangolin who rolls into every story
def scales(cv, clip, box, r, cols):
    x0, y0, x1, y1 = box
    cv.save()
    cv.clipPath(clip, True)
    cv.drawPaint(P(cols[-1]))
    rows = int((y1 - y0) / (r * 1.05)) + 2
    for j in range(rows):
        y = y1 - j * r * 1.05
        c = cols[min(len(cols) - 1, int((1 - j / max(1, rows - 1)) * len(cols)))]
        xx = x0 - r + (r if j % 2 else 0)
        while xx < x1 + r:
            cv.drawCircle(xx, y - r, r * 1.12, P(c))
            cv.drawCircle(xx, y - r, r * 1.12, P(INK, 0.7))
            xx += 2 * r
    cv.restore()
    cv.drawPath(clip, P(INK, 1.2))


def bolo(cv, v, en, pose):
    E, p = EX[en], POSES.get(pose, POSES['stand'])
    S = [0xFFFFCB3D, 0xFFFF9A2E, 0xFFF2603C, 0xFFD93A5E]
    BELLY, SKB, BAND, CLAW = 0xFFFFEFCB, 0xFFF0C08E, 0xFF13B5A8, 0xFF5A3A2A
    side, back = v == 'side', v == 'back'
    st = dict(dx=8.4, rx=5, ry=6.2, white=0xFFFFFFFF, pupil=INK, iris=0xFF2BB673, lid=SKB, fow=0.9, my=12.6, mw=9.5)
    if pose == 'ball':
        cv.translate(0, -21)
        cv.rotate(-18)
        scales(cv, ovalpath(0, 0, 21, 21), (-22, -22, 22, 22), 5.2, S)
        slot = smooth([(-13, -3), (0, -8), (13, -3), (12, 3), (0, 0), (-12, 3)])
        fs(cv, slot, 0xFF3A2030, 1.0)
        for s_ in (-1, 1):
            oval(cv, s_ * 5, -2.6, 2.6, 2.9, 0xFFFFFFFF, 0)
            cv.drawCircle(s_ * 5 + 0.6, -2.4, 1.3, P(INK))
        return
    w = 0.85 if side else 1.0
    sh, hands, hips, feet = frame(p, w, sx=14, sy=-40, hx=7, hy=-12, fx=8)
    cv.translate(0, p['lift'])
    cv.rotate(p['tilt'])
    tail = [(10, -14), (26, -8), (35, -19), (30, -31), (23, -27)] if not side else [(-10, -14), (-28, -8), (-39, -20), (-33, -33), (-26, -29)]
    if back:
        tail = [(0, -14), (3, -3), (13, 2), (23, -3), (24, -12)]
    else:
        hose(cv, tail, 10.5, S[2])
        hose(cv, tail[2:], 7, S[3], 0)
    if side:
        limb(cv, sh[0], hands[0], 5.5, 0xFFDCA878)
        oval(cv, hands[0][0], hands[0][1], 4, 4, 0xFFDCA878)
    for (hx_, hy_), (fx_, fy_) in zip(hips, feet):
        limb(cv, (hx_, hy_), (fx_, fy_ - 3), 7, SKB, 0.05)
        d = 2 if side or fx_ > 0 else -2
        oval(cv, fx_ + d, fy_ - 2.6, 7, 4, SKB)
        for k in (-2, 1, 4):
            cv.drawLine(fx_ + d * 2 + k * (0.6 if not side else 0.3) + (2 if side else 0), fy_ - 1.6, fx_ + d * 2 + k * 0.6 + (2 if side else 0), fy_ + 0.6, P(CLAW, 1.1))
    body = ovalpath(0, -29, 16 * w, 20)
    if back:
        scales(cv, body, (-17, -50, 17, -8), 4.6, S[1:3])
    else:
        scales(cv, body, (-17, -50, 17, -8), 4.6, S[1:3])
        oval(cv, (4 if side else 0), -27, (9.5 if side else 11.5), 16.5, BELLY, 1.0)
    if back:
        hose(cv, tail, 10.5, S[2])
        hose(cv, tail[2:], 7, S[3], 0)
    fs(cv, poly([(-12 * w, -47.5), (12 * w, -47.5), (0, -36)] if not back else [(-12, -47.5), (12, -47.5), (10, -43.5), (-10, -43.5)]), BAND)
    if back:
        fs(cv, poly([(-2, -44), (5, -36), (-1, -37)]), BAND, 0.9)
    if not side:
        for s_, hnd, shd in ((-1, hands[0], sh[0]), (1, hands[1], sh[1])):
            limb(cv, shd, hnd, 5.5, SKB, 0.22 * s_)
            oval(cv, hnd[0], hnd[1], 4.1, 4.1, SKB)
            for k in (-1, 0, 1):
                cv.drawLine(hnd[0] + k * 1.8, hnd[1] + 3, hnd[0] + k * 2.2, hnd[1] + 5.2, P(CLAW, 1.0))
    if side:
        head = smooth([(-15, -62), (-11, -74), (2, -79), (13, -73), (23, -63), (31.5, -57.5), (31.5, -52.5), (18, -50), (4, -47.5), (-10, -51)])
        oval(cv, -6, -75, 4, 4.4, SKB)
        fs(cv, head, SKB)
        cap = smooth([(-15, -62), (-11, -74), (2, -79), (13, -73), (10, -68), (0, -70), (-6, -62), (-10, -53)])
        scales(cv, cap, (-16, -80, 14, -52), 3.6, S[:2])
        oval(cv, 30.6, -56.2, 2.3, 1.9, CLAW, 0)
        st2 = dict(st, dx=0.01, my=11.5, mx=11, mw=9)
        E2 = dict(E)
        face(cv, 9, -62.5, E2, st2, near=(0.0, 1.0))
    else:
        for s_ in (-1, 1):
            oval(cv, s_ * 15.5, -73.5, 4.2, 4.4, SKB)
            if not back:
                oval(cv, s_ * 15.5, -73.5, 2, 2.2, 0xFFE59A8A, 0)
        head = smooth([(-18.5, -62), (-15, -73.5), (0, -78.5), (15, -73.5), (18.5, -62), (11, -50.5), (0, -46.5), (-11, -50.5)])
        if back:
            scales(cv, head, (-19, -79, 19, -46), 3.8, S[:2])
        else:
            fs(cv, head, SKB)
            cap = smooth([(-18.5, -63), (-15, -73.5), (0, -78.5), (15, -73.5), (18.5, -63), (11, -69), (0, -71.5), (-11, -69)])
            scales(cv, cap, (-19, -79, 19, -62), 3.6, S[:2])
            face(cv, 0, -63, E, st)
            oval(cv, 0, -55.2, 5.4, 3.6, 0xFFFFDDB4, 0.8)
            oval(cv, 0, -56.6, 2.2, 1.5, CLAW, 0)
    fs(cv, poly([(-2.8, -78), (0, -84), (2.8, -78)]), S[0], 1.0)
    if side:
        limb(cv, sh[1], hands[1], 5.5, SKB, 0.22)
        oval(cv, hands[1][0], hands[1][1], 4.1, 4.1, SKB)


CHARS = {'quip': quip, 'wick': wick, 'mothew': mothew, 'jot': jot, 'bolo': bolo}
INFO = {
    'quip':   dict(name='QUIP', tag='The kid who IS a question mark', head=(0, -84, 62), bg=0xFF2B2F5A, special=['cheer', 'point', 'run', 'shrug', 'think'],
                   palette=[0xFFFF5A36, 0xFFF0AE7B, 0xFF18BFAE, 0xFF2B2F5A, 0xFFFFFFFF]),
    'wick':   dict(name='WICK', tag='A living lantern with a short fuse', head=(0, -72, 56), bg=0xFF1D3657, special=['cheer', 'point', 'run', 'shrug', 'think'],
                   palette=[0xFFE8402F, 0xFFFF8A1F, 0xFFFFD84A, 0xFF2C4F7C, 0xFFF2B531]),
    'mothew': dict(name='MOTHEW', tag='A deeply unimpressed moth', head=(0, -74, 52), bg=0xFFFFA62B, special=['cheer', 'point', 'run', 'shrug', 'think'],
                   palette=[0xFFF8EACB, 0xFF6F4FD0, 0xFFFFA62B, 0xFF5A3A2A, 0xFF2A1B3D]),
    'jot':    dict(name='JOT', tag='Living ink that becomes the story', head=(0, -47, 66), bg=0xFFFFC233, special=['cheer', 'point', 'rocket', 'puddle', 'shrug'],
                   palette=[0xFF1D1A33, 0xFFFFFFFF, 0xFFFFC233, 0xFFFF3E8A, 0xFF62E3F0]),
    'bolo':   dict(name='BOLO', tag='The pangolin who rolls into every story', head=(0, -64, 44), bg=0xFF13B5A8, special=['cheer', 'point', 'run', 'ball', 'think'],
                   palette=[0xFFFFCB3D, 0xFFFF9A2E, 0xFFD93A5E, 0xFFF0C08E, 0xFF13B5A8]),
}


def draw(name, cv, x, y, s, view='front', expr='happy', pose='stand'):
    cv.save()
    cv.translate(x, y)
    if name == 'jot':
        s *= 1.4
    cv.scale(s, s)
    pz = pose if pose in POSES else 'stand'
    if name in ('jot', 'bolo') and pose in ('rocket', 'puddle', 'ball'):
        CHARS[name](cv, view, expr, pose)
    else:
        CHARS[name](cv, view, expr, pz)
    cv.restore()
