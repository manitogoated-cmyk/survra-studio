"""Rook, Survra's host, in production form: pose blending, walk cycle, beak lip sync, blinks,
plus same-style supporting cast (adult 2D rig from concepts/v2.py)."""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from concepts import v2  # noqa: E402
from concepts.chars import EX, INK, P, face, fs, oval, poly  # noqa: E402

VIS = dict(rest=0.0, MBP=0.0, FV=0.8, TH=1.2, L=1.6, E=1.9, AI=3.4, O=2.6, WQ=1.2, etc=1.5)
HAT_EXPR = ('shocked', 'scared', 'awe', 'laugh')


def pose(name='stand', **over):
    d = dict(v2.POSES[name])
    d.update(over)
    return d


def blend(a, b, k):
    k = max(0.0, min(1.0, k))
    k = k * k * (3 - 2 * k)
    out = {}
    for key in ('hl', 'hr', 'fl', 'fr'):
        out[key] = (a[key][0] + (b[key][0] - a[key][0]) * k, a[key][1] + (b[key][1] - a[key][1]) * k)
    for key in ('tilt', 'lift'):
        out[key] = a[key] + (b[key] - a[key]) * k
    return out


def keys(t, frames):
    if t <= frames[0][0]:
        return frames[0][1]
    for (t0, p0), (t1, p1) in zip(frames, frames[1:]):
        if t <= t1:
            return blend(p0, p1, (t - t0) / max(1e-6, t1 - t0))
    return frames[-1][1]


def walk(t, speed=1.7, run=False):
    ph = t * speed * 2 * math.pi
    st = 14 if run else 8
    sn, cs = math.sin(ph), math.cos(ph)
    return dict(fl=(st * sn, -max(0, cs) * (8 if run else 4)), fr=(-st * sn, -max(0, -cs) * (8 if run else 4)),
                hl=(-4 - st * 0.9 * sn, 27 if not run else 16), hr=(4 + st * 0.9 * sn, 27 if not run else 16),
                tilt=11 if run else 2, lift=-abs(cs) * (3 if run else 1.4))


GEST = [pose('point', hr=(22, -2), tilt=0), pose('shrug'), pose('think', tilt=0), pose('point', hr=(17, 6), hl=(-12, 14), tilt=0)]


def draw_rook(cv, x, y, h, p, view='tq', facing=1, expr='happy', beak=None, t=0.0):
    en = expr
    if (t + 0.4) % 3.4 < 0.1 and expr not in HAT_EXPR:
        EX['_b'] = dict(EX[expr], closed=1)
        en = '_b'
    s = h / 110.0
    v2.BEAK_OPEN[0] = beak
    cv.save()
    cv.translate(x, y)
    cv.scale(s * facing, s)
    v2.rook(cv, view, en, p)
    cv.restore()
    v2.BEAK_OPEN[0] = None


def person(cv, x, y, h, p, C, head, view='tq', facing=1, rot=0.0):
    s = h / 110.0
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    cv.scale(s * facing, s)
    v2.humanoid(cv, view, p if isinstance(p, dict) else pose(p), C, head)
    cv.restore()


def human_head(skin, skin2, hair, expr='happy', hair2=None):
    def head(cv, v):
        side, back = v == 'side', v == 'back'
        f = 3.2 if side else (2.0 if v == 'tq' else 0)
        fs(cv, poly([(-2.6, -84), (2.6, -84), (2.6, -78), (-2.6, -78)]), skin2, v2.OW)
        if side:
            oval(cv, -2, -91.5, 2, 2.9, skin, v2.OW)
        else:
            for s_ in (-1, 1):
                oval(cv, s_ * 9.6, -91.5, 1.9, 2.8, skin if s_ < 0 else skin2, v2.OW)
        hd = poly([(-9.4, -95), (-8.6, -100), (0, -102.5), (8.6, -100), (9.4, -95), (8.6, -87), (4.4, -81.6), (0, -80.4), (-4.4, -81.6), (-8.6, -87)])
        v2.fsh(cv, hd, hair if back else skin, (hair2 or hair) if back else skin2, k=0.26)
        if not back:
            st = dict(dx=4.4, rx=3.0, ry=2.6, white=0xFFFFFFFF, iris=0xFF5A3A22, pupil=INK, lid=skin, fow=0.7, my=7.6, mw=6.6, almond=True, min_lid=0.1, browc=0xFF1E1A22)
            face(cv, f, -91.2, EX[expr], st, near=(0.72, 0.92) if side else ((0.85, 1.0) if v == 'tq' else (1, 1)))
            cv.drawPath(poly([(f + 0.4, -89.8), (f + 1.6, -87.2), (f + 0.2, -86.9)], False), P(skin2, 0.8))
            v2.fsh(cv, poly([(-9.8, -94), (-9.2, -100.4), (-4.4, -103.8), (4.4, -103.8), (9.2, -100.4), (9.8, -94), (6, -97.8), (0, -96.8), (-6, -97.8)]), hair, hair2 or hair, k=0.3)
    return head


def bowl(cv, x, y, h, facing=1):
    """Glass diving bowl over Rook's head (hat and all)."""
    s = h / 110.0
    cx, cy, r = x + facing * 1 * s, y - 96 * s, 25 * s
    cv.drawCircle(cx, cy, r, P(0xFFBFEFFF, a=0.16))
    a = skia.Path()
    a.addArc(skia.Rect.MakeLTRB(cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78), 200, 50)
    cv.drawPath(a, P(0xFFFFFFFF, 5 * s, 0.8))
    cv.drawCircle(cx, cy, r, P(INK, 1.3 * s))
    cv.drawRoundRect(skia.Rect.MakeLTRB(cx - 12 * s, cy + r - 3 * s, cx + 12 * s, cy + r + 3 * s), 2 * s, 2 * s, P(0xFFB9C2CC))
    cv.drawRoundRect(skia.Rect.MakeLTRB(cx - 12 * s, cy + r - 3 * s, cx + 12 * s, cy + r + 3 * s), 2 * s, 2 * s, P(INK, 1.0 * s))
