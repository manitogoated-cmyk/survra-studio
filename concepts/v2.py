"""Round 2 host concepts: older, sharper, cooler. Adult proportions (about 5 heads), angular shapes,
two-tone cel shading, thinner lines, darker palettes with one hot accent. Strictly 2D vector (Skia)."""
import math

import skia

from concepts.chars import EX, FX, INK, P, face, fs, hose, oval, ovalpath, poly, smooth

OW = 0.85
SCALES = dict(turn=4.5, pose=3.05, line=4.6, sil=4.3, tag='2')

POSES = {
    'stand': dict(hl=(-4, 29), hr=(4, 29), fl=(0, 0), fr=(0, 0), tilt=0, lift=0),
    'point': dict(hl=(-6, 25), hr=(30, -7), fl=(-1, 0), fr=(5, 0), tilt=3, lift=0),
    'run':   dict(hl=(-17, 12), hr=(19, -3), fl=(-17, -9), fr=(15, -1), tilt=13, lift=-3),
    'shrug': dict(hl=(-18, 3), hr=(18, 3), fl=(0, 0), fr=(0, 0), tilt=0, lift=0),
    'think': dict(hl=(8, 17), hr=(-11, -7), fl=(0, 0), fr=(0, 0), tilt=-2, lift=0),
    'cross': dict(hl=(19, 13), hr=(-19, 15), fl=(-2, 0), fr=(2, 0), tilt=0, lift=0),
    'hype':  dict(hl=(-10, -31), hr=(13, -33), fl=(-4, -7), fr=(6, -3), tilt=0, lift=-8),
}


def fsh(cv, path, fill, shade, ow=OW, k=0.32):
    cv.drawPath(path, P(fill))
    b = path.getBounds()
    cv.save()
    cv.clipPath(path, True)
    x = b.left() + b.width() * (1 - k)
    sl = b.height() * 0.07
    cv.drawPath(poly([(x + sl, b.top() - 1), (b.right() + 1, b.top() - 1), (b.right() + 1, b.bottom() + 1), (x - sl, b.bottom() + 1)]), P(shade))
    cv.restore()
    if ow:
        cv.drawPath(path, P(INK, ow))


def humanoid(cv, v, pose, C, head, back_fn=None, torso_fn=None, coat=None, over_fn=None):
    p = POSES[pose]
    side, back = v == 'side', v == 'back'
    w = 0.62 if side else (0.86 if v == 'tq' else 1.0)
    cv.translate(0, p['lift'])
    cv.rotate(p['tilt'])
    sh = [(-13.5 * w, -77), (13.5 * w, -77)]
    hips = [(-4.8 * w, -50), (4.8 * w, -50)]
    feet = [(-6.5 * w + p['fl'][0], p['fl'][1]), (6.5 * w + p['fr'][0], p['fr'][1])]
    hands = [(sh[0][0] + p['hl'][0], -77 + p['hl'][1]), (sh[1][0] + p['hr'][0], -77 + p['hr'][1])]
    if back_fn:
        back_fn(cv, v, p)

    def arm(i, far=False):
        S, Hn = sh[i], hands[i]
        mx, my = (S[0] + Hn[0]) / 2, (S[1] + Hn[1]) / 2
        dx, dy = Hn[0] - S[0], Hn[1] - S[1]
        L = max(1e-3, math.hypot(dx, dy))
        b = (5.5 if L < 27 else 2.2) * (-1 if i == 0 else 1)
        elbow = (mx - dy / L * b, my + dx / L * b)
        hose(cv, [S, elbow, Hn], 6.0, C['top_sh'] if far else C.get('sleeve', C['top']), OW, straight=True)
        if C.get('cuff'):
            cx_, cy_ = Hn[0] - (Hn[0] - elbow[0]) * 0.22, Hn[1] - (Hn[1] - elbow[1]) * 0.22
            hose(cv, [(cx_, cy_), Hn], 6.4, C['cuff'], OW, straight=True)
        oval(cv, Hn[0], Hn[1], 3.7, 3.7, C['hand_sh'] if far else C['hand'], OW)

    def leg(i, far=False):
        Hp, F = hips[i], feet[i]
        ank = (F[0], F[1] - 4.5)
        knee = ((Hp[0] + ank[0]) / 2 + (2.2 if side else 0.6 * (-1 if i == 0 else 1)) + (F[0] - Hp[0]) * 0.15, (Hp[1] + ank[1]) / 2)
        hose(cv, [Hp, knee, ank], 7.2, C['pants_sh'] if far else C['pants'], OW, straight=True)
        d = 1 if side else (-1 if i == 0 else 1)
        if back:
            d = -d * 0.4
        boot = poly([(ank[0] - 4.2, ank[1] - 4), (ank[0] + 4.2, ank[1] - 4), (ank[0] + 4.4 + 4.6 * d, ank[1] + 2.4), (ank[0] + 4.4 + 4.6 * d, ank[1] + 4.6), (ank[0] - 4.6 + min(0, 4.6 * d), ank[1] + 4.6)])
        fsh(cv, boot, C['boot'], C['boot_sh'])
        if C.get('sole'):
            cv.drawLine(ank[0] - 4.2 + min(0, 4.6 * d), ank[1] + 4.3, ank[0] + 4.2 + max(0, 4.6 * d), ank[1] + 4.3, P(C['sole'], 1.3))

    if side:
        arm(0, True)
    leg(0, side)
    leg(1)
    fsh(cv, poly([(-9.6 * w, -57), (9.6 * w, -57), (10 * w, -46.5), (0, -44), (-10 * w, -46.5)]), C['pants'], C['pants_sh'])
    torso = poly([(-13.5 * w, -80), (13.5 * w, -80), (14.6 * w, -71), (10 * w, -57), (9.8 * w, -49.5), (-9.8 * w, -49.5), (-10 * w, -57), (-14.6 * w, -71)])
    if coat:
        torso = poly([(-13.5 * w, -80), (13.5 * w, -80), (14.6 * w, -71), (11 * w, -57), (13.5 * w, coat), (-13.5 * w, coat), (-11 * w, -57), (-14.6 * w, -71)])
    fsh(cv, torso, C['top'], C['top_sh'])
    if coat and not back:
        cv.drawLine(1.5 * w, -56, 2.5 * w, coat, P(INK, OW))
    if torso_fn:
        torso_fn(cv, v, w)
    if not side:
        arm(0)
        arm(1)
    head(cv, v)
    if side:
        arm(1)
    if over_fn:
        over_fn(cv, v, p)


def glowface(cv, x, y, en, col, dx=4.3, u=1.0, my=6.4):
    kinds = {'happy': ('slant', 'slant'), 'laugh': ('arc', 'arc'), 'awe': ('circle', 'circle'), 'curious': ('slant', 'circle'),
             'smirk': ('slant', 'flat'), 'deadpan': ('flat', 'flat'), 'shocked': ('ring', 'ring'), 'scared': ('dot', 'dot'),
             'sad': ('sadslant', 'sadslant'), 'angry': ('tri', 'tri'), 'thinking': ('flat', 'slant'), 'wink': ('slant', 'arc')}[en]
    m = EX[en]['m']

    def shapes(paint_fill, paint_line):
        for s_, kind in ((-1, kinds[0]), (1, kinds[1])):
            ex = x + s_ * dx * u
            T = lambda pts: poly([(ex + s_ * a * u, y + b * u) for a, b in pts])
            if kind == 'slant':
                cv.drawPath(T([(-2.7, 1.0), (-1.9, -1.0), (2.9, -2.3), (2.6, 0.6), (-1.0, 1.8)]), paint_fill)
            elif kind == 'sadslant':
                cv.drawPath(T([(-2.7, -1.7), (2.9, 0.1), (2.5, 2.0), (-2.3, 1.1)]), paint_fill)
            elif kind == 'tri':
                cv.drawPath(T([(-3.0, 1.3), (3.0, -2.7), (2.1, 1.7)]), paint_fill)
            elif kind == 'flat':
                cv.drawRoundRect(skia.Rect.MakeLTRB(ex - 2.7 * u, y - 0.4 * u, ex + 2.7 * u, y + 1.0 * u), 0.6, 0.6, paint_fill)
            elif kind == 'circle':
                cv.drawCircle(ex, y, 2.6 * u, paint_fill)
            elif kind == 'dot':
                cv.drawCircle(ex, y, 1.3 * u, paint_fill)
            elif kind == 'ring':
                cv.drawCircle(ex, y, 2.6 * u, paint_line)
                cv.drawCircle(ex, y, 0.8 * u, paint_fill)
            else:
                a = skia.Path()
                a.moveTo(ex - 2.6 * u, y + 1.0 * u)
                a.quadTo(ex, y - 2.6 * u, ex + 2.6 * u, y + 1.0 * u)
                cv.drawPath(a, paint_line)
        yy = y + my * u
        Z = lambda pts: poly([(x + a * u, yy + b * u) for a, b in pts], False)
        if m in ('grin', 'laugh'):
            cv.drawPath(Z([(-4.2, -0.3), (-2.6, 1.5), (-1.3, 0.4), (0, 1.9), (1.3, 0.4), (2.6, 1.5), (4.2, -0.3)]), paint_line)
            if m == 'laugh':
                cv.drawPath(Z([(-2.6, 2.4), (0, 3.6), (2.6, 2.4)]), paint_line)
        elif m == 'smile':
            cv.drawPath(Z([(-2.8, 0), (-1, 1.1), (1, 1.1), (2.8, 0)]), paint_line)
        elif m == 'smirk':
            cv.drawPath(Z([(-2.4, 1.0), (1.2, 1.0), (3.4, -0.9)]), paint_line)
        elif m == 'flat':
            cv.drawPath(Z([(-2.4, 0.6), (2.4, 0.6)]), paint_line)
        elif m == 'frown':
            cv.drawPath(Z([(-2.8, 1.6), (-1, 0.3), (1, 0.3), (2.8, 1.6)]), paint_line)
        elif m == 'teeth':
            cv.drawPath(Z([(-3.6, 0.9), (-2.4, -0.4), (-1.2, 0.9), (0, -0.4), (1.2, 0.9), (2.4, -0.4), (3.6, 0.9)]), paint_line)
        elif m in ('o', 'gasp'):
            r = 1.0 if m == 'o' else 1.7
            cv.drawOval(skia.Rect.MakeLTRB(x - r * u, yy - r * 0.2 * u, x + r * u, yy + r * 2.0 * u), paint_line)
        else:
            cv.drawPath(Z([(0.4, 0.9), (2.4, 0.4)]), paint_line)

    if FX['glow']:
        g1, g2 = P(col, a=0.75), P(col, 0.9 * u * 2.2, a=0.6)
        for g in (g1, g2):
            g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.5 * u))
        shapes(g1, g2)
    shapes(P(col), P(col, 0.95 * u))


# =================================================================== 1. NOX - the hooded drifter
def nox(cv, v, en, pose):
    C = dict(pants=0xFF211E30, pants_sh=0xFF171524, boot=0xFF15131E, boot_sh=0xFF0D0C14, sole=0xFF4FF0FF, top=0xFF2E2846, top_sh=0xFF211C34,
             hand=0xFF15131E, hand_sh=0xFF0D0C14, cuff=0xFF15131E)
    CAPE, CAPE2, GLOW = 0xFFC62B48, 0xFF8E1D33, 0xFF4FF0FF
    side, back = v == 'side', v == 'back'

    def cape(cv, v, p):
        if back:
            return
        if side:
            fsh(cv, poly([(-3, -79), (-15, -72), (-25, -40), (-19, -45), (-15, -31), (-10, -42), (-6, -35), (-3, -52)]), CAPE, CAPE2, k=0.5)
        else:
            sway = p['tilt'] * 0.6
            fsh(cv, poly([(-14, -79), (14, -79), (18 - sway, -52), (13 - sway, -39), (9 - sway, -46), (4 - sway, -33), (-2 - sway, -42), (-8 - sway, -28), (-13 - sway, -40), (-18 - sway, -33), (-19, -56)]), CAPE, CAPE2)

    def torso(cv, v, w):
        if back:
            fsh(cv, poly([(-14, -80), (14, -80), (18, -52), (13, -38), (8, -46), (3, -32), (-3, -42), (-9, -28), (-14, -40), (-19, -33), (-19, -56)]), CAPE, CAPE2)
            return
        cv.drawLine(-12 * w, -76, 9 * w, -53, P(0xFF15131E, 2.4))
        cv.drawLine(-12 * w, -76, 9 * w, -53, P(GLOW, 0.5))
        fs(cv, poly([(2 * w, -70), (7 * w, -70), (4.5 * w, -65.5)]), GLOW, 0.4)

    def head(cv, v):
        f = 3.2 if side else 0
        hood = poly([(-13, -79), (-15.5, -91), (-11, -102), (-2, -108), (4, -109.5), (8, -106), (11.5, -101), (15.5, -91), (13, -79), (6, -76), (-6, -76)])
        fsh(cv, hood, C['top'], C['top_sh'])
        if back:
            cv.drawLine(0, -108, 0, -78, P(INK, OW))
            return
        fs(cv, smooth([(-9 + f, -83.5), (-10 + f, -93), (-5 + f, -100), (5 + f, -100), (10 + f * 0.6, -93), (9 + f * 0.6, -83.5), (0 + f, -79.5)]), 0xFF0B0914, OW)
        glowface(cv, f, -91.5, en, GLOW, dx=4.2)
    humanoid(cv, v, pose, C, head, cape, torso)


# =================================================================== 2. MORT - the skeleton who has heard it all
def mort(cv, v, en, pose):
    BONE, BONE2, ORANGE, ORANGE2, TEAL = 0xFFF4ECDA, 0xFFD8CBAC, 0xFFFF7A1A, 0xFFD95E0E, 0xFF35D6CE
    C = dict(pants=0xFF4B5060, pants_sh=0xFF393D4B, boot=0xFFF4F4F4, boot_sh=0xFFCFCFD6, sole=ORANGE, top=0xFF22323D, top_sh=0xFF17232C,
             hand=BONE, hand_sh=BONE2, cuff=ORANGE)
    side, back = v == 'side', v == 'back'
    E = EX[en]

    def torso(cv, v, w):
        fsh(cv, poly([(-10 * w, -53.5), (10 * w, -53.5), (9.8 * w, -49), (-9.8 * w, -49)]), ORANGE, ORANGE2)
        if not back:
            o = 5 if side else 0
            cv.drawLine(o, -78, o, -54, P(0xFFB9C2CC, 0.8))
        hp = skia.Path()
        hp.moveTo(-7.5 * w, -80)
        hp.quadTo(0, -70.5, 7.5 * w, -80)
        cv.drawPath(hp, P(INK, 3.4))
        cv.drawPath(hp, P(TEAL, 1.9))
        for s_ in (-1, 1):
            oval(cv, s_ * 7.6 * w, -79.5, 2.6, 3.4, TEAL, OW)

    def head(cv, v):
        f = 3.4 if side else 0
        fs(cv, poly([(-2, -84), (2, -84), (2, -78), (-2, -78)]), BONE2, OW)
        open_ = {'laugh': 4.2, 'gasp': 4.6, 'grin': 1.8, 'o': 2.2}.get(E['m'], 0.0)
        if not back:
            cv.save()
            cv.translate(f, open_)
            if en in ('smirk', 'thinking', 'curious'):
                cv.rotate(7, 0, -82)
            if open_:
                fs(cv, poly([(-5, -84.5 - open_), (5, -84.5 - open_), (4.8, -82), (-4.8, -82)]), 0xFF2A1420, 0)
            fsh(cv, poly([(-5.8, -83.2), (5.8, -83.2), (4.8, -79), (-4.8, -79)]), BONE, BONE2)
            for k in (-3, -1, 1, 3):
                cv.drawLine(k, -83.2, k, -81.6, P(INK, 0.5))
            cv.restore()
        skull = poly([(-10, -93), (-9.2, -100.5), (-4, -104), (4, -104), (9.2, -100.5), (10, -93), (8.6, -88), (6.2, -86.2), (5.8, -83), (-5.8, -83), (-6.2, -86.2), (-8.6, -88)])
        fsh(cv, skull, BONE, BONE2)
        if not back:
            st = dict(dx=4.3, rx=3.3, ry=3.6, white=0xFF1E1A2B, pupil=0xFFFFB000, lid=BONE, fow=0.7, my=40, mw=1, browc=0xFF8A7A5C, almond=False)
            E2 = dict(E, m='none', ps=E.get('ps', 1.0) * 0.8)
            cv.save()
            cv.clipRect(skia.Rect.MakeLTRB(-12, -104, 12, -84.5))
            face(cv, f, -91.6, E2, st, near=(0.75, 0.9) if side else (1, 1))
            cv.restore()
            fs(cv, poly([(f - 1.3, -86.6), (f, -88.8), (f + 1.3, -86.6)]), 0xFF1E1A2B, 0)
            for k in (-3, -1, 1, 3):
                cv.drawLine(f + k, -85.4, f + k, -83.2, P(INK, 0.5))
            cv.drawRect(skia.Rect.MakeLTRB(f + 1.2, -85.3, f + 2.8, -83.3), P(0xFFFFC233))
        beanie = poly([(-10.6, -95), (-10.2, -101.5), (-5, -106.8), (0, -107.8), (5, -106.8), (10.2, -101.5), (10.6, -95)])
        fsh(cv, beanie, ORANGE, ORANGE2)
        fsh(cv, poly([(-11.2, -98.2), (11.2, -98.2), (11.2, -94.2), (-11.2, -94.2)]), ORANGE2, 0xFFB84C08)
        for k in range(-9, 10, 3):
            cv.drawLine(k, -98, k, -94.4, P(0xFF9E4208, 0.5))
    humanoid(cv, v, pose, C, head, None, torso)


# =================================================================== 3. ROOK - the crow in the long coat
BEAK_OPEN = [None]   # lip-sync override: beak opening in units


def rook(cv, v, en, pose):
    FEA, FEA2, BEAK, BEAK2, HAT, ORANGE = 0xFF2A2742, 0xFF1C1A2E, 0xFF7A8096, 0xFF565B6E, 0xFF34303B, 0xFFFF7A1A
    C = dict(pants=0xFF2B2834, pants_sh=0xFF1F1D27, boot=0xFF191720, boot_sh=0xFF100F16, top=0xFF566178, top_sh=0xFF404A5E,
             hand=FEA, hand_sh=FEA2)
    side, back = v == 'side', v == 'back'
    E = EX[en]

    def tail(cv, v, p):
        if back:
            for k in (-1, 0, 1):
                bx = (-9 if side else 0) + k * 3.2
                fs(cv, poly([(bx - 2, -30), (bx + 2, -30), (bx + 1.6 + k, -13), (bx - 1.6 + k, -13)]), FEA2, OW)

    def torso(cv, v, w):
        if back:
            cv.drawLine(0, -50, 0, -25, P(INK, OW))
            cv.drawLine(-10.5, -57, 10.5, -57, P(0xFF2B2834, 2.2))
            return
        o = 3 if side else 0
        fs(cv, poly([(-4 * w + o, -80), (4 * w + o, -80), (o, -68)]), ORANGE, OW)
        for s_ in (-1, 1):
            fsh(cv, poly([(s_ * 4.5 * w + o, -80), (s_ * 12 * w, -80), (s_ * 7.5 * w + o, -66)]), 0xFF6B7790, 0xFF566178, OW, k=0.2)
            fs(cv, poly([(s_ * 5 * w + o * 0.5, -80), (s_ * 10.5 * w, -80), (s_ * 9.5 * w, -87.5)]), 0xFF6B7790, OW)
        cv.drawLine(-11 * w, -57, 11 * w, -57, P(0xFF2B2834, 2.4))
        fs(cv, poly([(o - 2, -58.6), (o + 2, -58.6), (o + 2, -55.4), (o - 2, -55.4)]), 0xFFFFC233, 0.5)

    def head(cv, v):
        hd = poly([(-9.2, -92), (-8.4, -99.5), (0, -102.5), (8.4, -99.5), (9.2, -92), (6.2, -84.2), (0, -81), (-6.2, -84.2)])
        if side:
            for k in (0, 1, 2):
                fs(cv, poly([(-8, -96 + k * 3.4), (-13.5, -94 + k * 3.6), (-8, -92.4 + k * 3.4)]), FEA2, OW)
        fsh(cv, hd, FEA, FEA2)
        opn = {'laugh': 3.0, 'gasp': 3.4, 'grin': 1.4, 'o': 1.6, 'teeth': 1.0}.get(E['m'], 0)
        if BEAK_OPEN[0] is not None:
            opn = BEAK_OPEN[0]
        tq = v == 'tq'
        if side:
            if opn:
                fs(cv, poly([(7, -87.5), (19, -86.5 + opn * 0.7), (7.5, -84.5 + opn * 0.4)]), 0xFF8E2A3A, OW)
            fsh(cv, poly([(6.5, -94), (23, -88.6), (7, -86.4)]), BEAK, BEAK2, k=0.4)
            st = dict(dx=0.01, rx=3.0, ry=2.7, white=0xFFFFB000, pupil=INK, lid=FEA, fow=0.7, my=40, mw=1, browc=0xFF6E69A0, almond=True, min_lid=0.12)
            face(cv, 3.4, -93.6, dict(E, m='none', ps=E.get('ps', 1) * 0.75), st, near=(0, 1))
        elif not back:
            st = dict(dx=4.6, rx=3.0, ry=2.7, white=0xFFFFB000, pupil=INK, lid=FEA, fow=0.7, my=40, mw=1, browc=0xFF6E69A0, almond=True, min_lid=0.12)
            face(cv, 2.0 if tq else 0, -93.4, dict(E, m='none', ps=E.get('ps', 1) * 0.75), st, near=(0.78, 1.0) if tq else (1, 1))
            if tq:
                if opn:
                    fs(cv, poly([(2.4, -86.4), (8.4, -84.6 + opn * 0.5), (7.2, -80.6 + opn), (3.2, -83.2)]), 0xFF8E2A3A, OW)
                fsh(cv, poly([(-0.6, -91.6), (5.6, -91.2), (9.4, -84.6), (8.0, -82.6), (2.6, -85.4)]), BEAK, BEAK2, k=0.4)
            else:
                if opn:
                    fs(cv, poly([(-2, -85), (2, -85), (0, -80.5 + opn)]), 0xFF8E2A3A, OW)
                fsh(cv, poly([(-3.4, -91.4), (3.4, -91.4), (1.3, -83.2), (0, -81.2), (-1.3, -83.2)]), BEAK, BEAK2, k=0.45)
        hat = {'shocked': (-4.2, -9), 'scared': (-3.2, 7), 'awe': (-3.0, -5), 'deadpan': (0.9, 0), 'smirk': (0.6, 4), 'angry': (0.9, 0), 'laugh': (-1.2, -6)}.get(en, (0, 0))
        cv.save()
        cv.translate(0, hat[0])
        cv.rotate(hat[1], 0, -99)
        fsh(cv, poly([(-18, -99.6), (18, -99.6), (15, -97.2), (-15, -97.2)]), HAT, 0xFF24212A)
        fsh(cv, poly([(-9, -99.6), (-7.6, -109), (-2, -110.4), (7.6, -109), (9, -99.6)]), HAT, 0xFF24212A)
        fs(cv, poly([(-8.9, -102.4), (8.9, -102.4), (9, -99.8), (-9, -99.8)]), ORANGE, 0.5)
        cv.restore()
    humanoid(cv, v, pose, C, head, tail, torso, coat=-25)


# =================================================================== 4. KADE - the headband runner
def kade(cv, v, en, pose):
    SK, SK2, HAIR, HAIR2, BAND, BAND2 = 0xFFC98B5E, 0xFFA66D45, 0xFFF4F4F8, 0xFFC5C8D6, 0xFFFF4B2B, 0xFFC7331A
    C = dict(pants=0xFF3B404C, pants_sh=0xFF2B2F39, boot=0xFF1F2028, boot_sh=0xFF14151B, sole=BAND, top=0xFF28325A, top_sh=0xFF1B2340,
             hand=SK, hand_sh=SK2, cuff=0xFF14151B)
    side, back = v == 'side', v == 'back'

    def tails(cv, v, p):
        d = -1 if side else 1
        kx = (-9 if side else (0 if back else 9.5))
        sw = p['tilt'] * 0.5 + (4 if pose == 'run' else 0)
        for dy, L in ((0, 1.0), (4.5, 0.8)):
            pts = [(kx, -96 + dy * 0.3), (kx + d * 10 * L, -94 + dy + sw * 0.3), (kx + d * 19 * L, -99 + dy + sw), (kx + d * 27 * L, -94 + dy + sw * 1.6)]
            hose(cv, pts, 2.8, BAND if dy == 0 else BAND2, OW)

    def torso(cv, v, w):
        if back:
            cv.drawLine(11 * w, -78, -9 * w, -54, P(0xFF8A5A3A, 2.6))
            return
        o = 4 if side else 0
        cv.drawLine(o, -79, o, -50, P(BAND, 0.9))
        cv.drawLine(-11 * w, -78, 9 * w, -54, P(INK, 3.6))
        cv.drawLine(-11 * w, -78, 9 * w, -54, P(0xFF8A5A3A, 2.4))
        fsh(cv, poly([(4 * w, -62), (10 * w, -60), (9.6 * w, -53), (3.6 * w, -54.6)]), 0xFF8A5A3A, 0xFF6B4329)
        fsh(cv, poly([(-7.5 * w, -80), (7.5 * w, -80), (8.6 * w, -85.2), (3 * w + o * 0.4, -81.4), (-3 * w + o * 0.4, -81.4), (-8.6 * w, -85.2)]), 0xFF36427A, 0xFF28325A)

    def head(cv, v):
        f = 3.2 if side else 0
        fs(cv, poly([(-2.6, -84), (2.6, -84), (2.6, -78), (-2.6, -78)]), SK2, OW)
        if not side:
            for s_ in (-1, 1):
                oval(cv, s_ * 9.6, -91.5, 1.9, 2.8, SK if s_ < 0 else SK2, OW)
        else:
            oval(cv, -2, -91.5, 2, 2.9, SK, OW)
        hd = poly([(-9.4, -95), (-8.6, -100), (0, -102.5), (8.6, -100), (9.4, -95), (8.6, -87), (4.4, -81.6), (0, -80.4), (-4.4, -81.6), (-8.6, -87)])
        fsh(cv, hd, HAIR if back else SK, HAIR2 if back else SK2, k=0.26)
        if not back:
            st = dict(dx=4.4, rx=3.0, ry=2.5, white=0xFFFFFFFF, iris=0xFF19B5A5, pupil=INK, lid=SK, fow=0.7, my=7.6, mw=6.6, almond=True, min_lid=0.14, browc=0xFF4A4A58)
            face(cv, f, -91.2, EX[en], st, near=(0.72, 0.92) if side else (1, 1))
            cv.drawPath(poly([(f + 0.4, -89.8), (f + 1.6, -87.2), (f + 0.2, -86.9)], False), P(SK2, 0.8))
            cv.drawLine(f - 7.6, -90.2, f - 3.4, -86.6, P(0xFF8A4A32, 0.8))
        spikes = [(-10, -94.5), (-12.5, -101.5), (-8, -100.5), (-9, -108.5), (-3.4, -104.6), (0.6, -112), (3.8, -104.8), (9.6, -108.6), (8.4, -100.6), (12.6, -100), (10, -94.5)]
        fringe = [(6.4, -97.4), (2.6, -94.6), (-1, -97.2), (-5.4, -94.8)] if not back else [(9, -86), (4, -83.5), (0, -86), (-4, -83.5), (-9, -86)]
        fsh(cv, poly(spikes + fringe), HAIR, HAIR2, k=0.3)
        fsh(cv, poly([(-10, -98.2), (10, -98.2), (10, -95.2), (-10, -95.2)]), BAND, BAND2)
        kx = (-9.6 if side else (0 if back else 9.6))
        fs(cv, poly([(kx - 1.8, -98.8), (kx + 1.8, -98.8), (kx + 1.8, -94.6), (kx - 1.8, -94.6)]), BAND2, OW)
    humanoid(cv, v, pose, C, head, tails, torso)


# =================================================================== 5. SOL - the man with a flame for a head
def sol(cv, v, en, pose):
    C = dict(pants=0xFF2C2C35, pants_sh=0xFF1F1F26, boot=0xFF1B1B21, boot_sh=0xFF111116, sole=0xFFFF7A1A, top=0xFF37343F, top_sh=0xFF27242E,
             hand=0xFF1B1B21, hand_sh=0xFF111116, cuff=0xFFFF7A1A)
    mood = {'angry': (0xFFE5261F, 0xFFFF8A2E, 1.15), 'sad': (0xFF2F7BE0, 0xFF9AD0FF, 0.8), 'shocked': (0xFFFFC233, 0xFFFFF6C8, 1.2),
            'scared': (0xFF9C8CFF, 0xFFE4DCFF, 0.78), 'awe': (0xFFFF9A1F, 0xFFFFE680, 1.12), 'laugh': (0xFFFF8A1F, 0xFFFFD84A, 1.08)}.get(en, (0xFFFF7A1A, 0xFFFFC83D, 1.0))
    side, back = v == 'side', v == 'back'

    def torso(cv, v, w):
        if back:
            cv.drawLine(0, -78, 0, -50, P(INK, OW))
            return
        o = 4 if side else 0
        fs(cv, poly([(-5 * w + o, -80), (5 * w + o, -80), (o, -66)]), 0xFFFF7A1A, OW)
        cv.drawLine(o, -66, o, -50, P(0xFFFFC233, 0.9))
        for s_ in (-1, 1):
            fs(cv, poly([(s_ * 5.2 * w + o, -80), (s_ * 11.5 * w, -80), (s_ * 8 * w + o * 0.6, -70)]), 0xFF4A4654, OW)

    def head(cv, v):
        k = mood[2]
        lean = -3.5 if side else 0
        if FX['glow']:
            g = skia.GradientShader.MakeRadial(skia.Point(0, -94), 30, [(mood[1] & 0xFFFFFF) | 0x77000000, mood[1] & 0xFFFFFF])
            cv.drawCircle(0, -94, 30, skia.Paint(AntiAlias=True, Shader=g))
        base = [(-8, -2), (-10.4, -12), (-7.4, -18), (-9, -26.5), (-3.6, -21.5), (-0.6, -33.5), (3.8, -22.5), (8.4, -28.5), (7.8, -17.5), (10.8, -11.5), (8, -2), (0, 0.6)]

        def flame(sc, col, ow):
            pts = [(a * sc + lean * (-b / 30.0) * 1.6, -80.2 + b * sc * (k if b < -12 else 1)) for a, b in base]
            fs(cv, poly(pts), col, ow, 0xFF9E3A10)
        flame(1.0, mood[0], OW)
        flame(0.62, mood[1], 0)
        fsh(cv, poly([(-7, -82.6), (7, -82.6), (6, -78.4), (-6, -78.4)]), 0xFF9AA0B4, 0xFF6E7488)
        if not back:
            glowface(cv, 2.6 if side else 0, -90, en, 0xFFFFFFFF, dx=4.0, u=0.92, my=5.4)
        for q in ((-11, -108, 0.9), (9.5, -112, 0.7), (2, -119, 0.6)):
            cv.drawCircle(q[0], q[1], q[2], P(mood[1]))
    humanoid(cv, v, pose, C, head, None, torso)


CHARS = {'nox': nox, 'mort': mort, 'rook': rook, 'kade': kade, 'sol': sol}
_SP = ['point', 'run', 'shrug', 'think', 'cross']
INFO = {
    'nox':  dict(name='NOX', tag='The hooded drifter. You never see his face', head=(0, -92, 40), face=30, bg=0xFFC62B48, special=_SP,
                 palette=[0xFF2E2846, 0xFFC62B48, 0xFF4FF0FF, 0xFF0B0914, 0xFF15131E]),
    'mort': dict(name='MORT', tag='A skeleton who has heard every story', head=(0, -93, 36), face=30, bg=0xFF22323D, special=_SP,
                 palette=[0xFFF4ECDA, 0xFFFF7A1A, 0xFF22323D, 0xFF35D6CE, 0xFFFFC233]),
    'rook': dict(name='ROOK', tag='The crow in the long coat', head=(0, -95, 44), face=32, bg=0xFFFF7A1A, special=_SP,
                 palette=[0xFF2A2742, 0xFF566178, 0xFFFFB000, 0xFF34303B, 0xFFFF7A1A]),
    'kade': dict(name='KADE', tag='Headband, scar, zero patience', head=(0, -95, 42), face=32, bg=0xFF28325A, special=_SP,
                 palette=[0xFFC98B5E, 0xFFF4F4F8, 0xFFFF4B2B, 0xFF28325A, 0xFF19B5A5]),
    'sol':  dict(name='SOL', tag='The man with a flame for a head', head=(0, -96, 46), face=34, bg=0xFF27242E, special=_SP,
                 palette=[0xFFFF7A1A, 0xFFFFC83D, 0xFF37343F, 0xFF9AA0B4, 0xFFFFFFFF]),
}


def draw(name, cv, x, y, s, view='front', expr='happy', pose='stand'):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    CHARS[name](cv, view, expr, pose if pose in POSES else 'stand')
    cv.restore()

LINEUP = [('smirk', 'cross'), ('happy', 'shrug'), ('deadpan', 'think'), ('smirk', 'point'), ('happy', 'cross')]
