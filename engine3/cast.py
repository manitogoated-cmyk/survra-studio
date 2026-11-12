"""Supporting cast: one parametric person rig, dressed fresh for every story.

Same skeleton, poses (kesta.POSES / walk / keyframes) and face system as Kesta, so
supporting characters act with the same quality, but each story gets its own people:
skin, hair, build, clothing, era and accessories all come from a Look.
"""
import math
from dataclasses import dataclass

import skia

from engine3.kesta import (BASE, COL, EXPR, INK, P, circle, draw_eye, draw_hand, draw_mouth, lerp, limb_pts, oval,
                           poly, seg)


@dataclass
class Look:
    skin: int = 0xFFE0B48F
    skin_sh: int = 0xFFC4946E
    hair: int = 0xFF6B4A2B
    hair_style: str = 'short'      # short, long, bun, bald, cap, helmet, hat, wide_hat, scarf, ponytail
    hat: int = 0xFF3A3A3A
    beard: str = ''                # '', stubble, full, moustache
    glasses: bool = False
    top: int = 0xFF4C7A9E
    top_sh: int = 0xFF3D6585
    top_style: str = 'shirt'       # shirt, coat, dress, uniform, vest, robe
    accent: int = 0xFFE8E0D0       # collar / trim
    pants: int = 0xFF3C3A36
    shoes: int = 0xFF2A2420
    bare_feet: bool = False
    width: float = 1.0
    height: float = 1.0
    eye: int = 0xFF5A3A22


def _hair_back(cv, L, fx):
    h = L.hair
    if L.hair_style in ('long', 'ponytail'):
        poly(cv, [(-13, -12), (12, -14), (13, 6), (8, 18 if L.hair_style == 'long' else 4), (-12, 20 if L.hair_style == 'long' else 6)], h, ow=2.0, smooth=True)
        if L.hair_style == 'ponytail':
            poly(cv, [(-12, -6), (-19, 4), (-17, 16), (-13, 8)], h, ow=2.0, smooth=True)
    elif L.hair_style == 'bun':
        circle(cv, -8, -16, 6.5, h, ow=2.0)


def _hair_front(cv, L, fx):
    h = L.hair
    st = L.hair_style
    if st == 'bald':
        return
    if st in ('cap', 'helmet', 'hat', 'wide_hat'):
        c = L.hat
        if st == 'cap':
            poly(cv, [(-13, -6), (-12, -16), (2, -20), (13, -14), (13, -7)], c, ow=2.0, smooth=True)
            poly(cv, [(10, -8), (21, -7), (20, -4.5), (9, -5)], c, ow=1.8)
        elif st == 'helmet':
            poly(cv, [(-14, -3), (-13, -17), (1, -22), (14, -15), (15, -3)], c, ow=2.0, smooth=True)
            seg(cv, (-15, -3), (16, -3), 1.6, c, ow=1.6)
        elif st == 'hat':
            poly(cv, [(-11, -10), (-10, -22), (11, -22), (12, -10)], c, ow=2.0)
            poly(cv, [(-19, -10), (20, -10), (18, -7), (-17, -7)], c, ow=1.8)
        else:
            poly(cv, [(-10, -11), (-6, -21), (8, -21), (12, -11)], c, ow=2.0, smooth=True)
            oval(cv, 1, -10, 24, 4, c, ow=1.8)
        return
    if st == 'scarf':
        poly(cv, [(-14, 4), (-14, -12), (0, -20), (14, -13), (14, -2), (10, -12), (-8, -12)], L.hat, ow=2.0, smooth=True)
        return
    poly(cv, [(-13, -4), (-12, -15), (0, -19), (12, -15), (14, -6), (8, -11), (0, -10), (-6, -12)], h, ow=2.0, smooth=True)


def draw_person(cv, x, y, s, pose_, t, L: Look, facing=1, expr='neutral', viseme='rest', look=(0.0, 0.0),
                blink=None, alpha=1.0, k_open=1.0, prop=None, wet=0.0):
    p = dict(BASE)
    p.update(pose_)
    if blink is None:
        ph = (t + (hash(L.top) % 97) / 31.0) % 4.1
        blink = 1.0 if ph < 0.09 else 0.0
    cv.save()
    if alpha < 1:
        cv.saveLayerAlpha(None, int(255 * alpha))
    cv.translate(x, y)
    cv.scale(s / 100.0 * facing * L.width ** 0.3, s / 100.0 * L.height)
    breathe = math.sin(t * 2.0 + L.top % 7) * 0.5
    hip = (p['rx'], -44 + p['crouch'] + p['ry'])
    lean = p['lean']
    neck = (hip[0] + math.sin(math.radians(lean)) * 26, hip[1] - math.cos(math.radians(lean)) * 26 - breathe * 0.3)
    shF, shB = (neck[0] + 3 * L.width, neck[1] + 4), (neck[0] - 5 * L.width, neck[1] + 4)
    hipF, hipB = (hip[0] + 3, hip[1]), (hip[0] - 3, hip[1])
    dress = L.top_style in ('dress', 'robe')

    def leg(base, foot, front):
        L1, L2 = 20.0, 21.0
        ank = (foot[0] - 1.0, foot[1] - 3.6)
        dx, dy = ank[0] - base[0], ank[1] - base[1]
        d = max(1e-3, min(L1 + L2 - 0.05, math.hypot(dx, dy)))
        a = math.atan2(dy, dx)
        b = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
        knee = (base[0] + L1 * math.cos(a - b), base[1] + L1 * math.sin(a - b))
        legc = L.skin if dress else (L.pants if front else _dark(L.pants))
        w = 6.0 if dress else 8.6 * L.width ** 0.5
        seg(cv, base, knee, w, legc if not dress else (L.skin if front else L.skin_sh))
        seg(cv, knee, ank, w * 0.92, legc if not dress else (L.skin if front else L.skin_sh))
        sc = (L.skin if front else L.skin_sh) if L.bare_feet else (L.shoes if front else _dark(L.shoes))
        poly(cv, [(ank[0] - 3, ank[1] - 2), (ank[0] + 6, ank[1] - 0.5), (ank[0] + 7.5, ank[1] + 3.4), (ank[0] - 3.6, ank[1] + 3.4)], sc, ow=2.0)

    def arm(base, u, l, kind, front):
        elb, wr = limb_pts(base, u, 15, l, 14)
        sl = L.top if front else L.top_sh
        seg(cv, base, elb, 7.4 * L.width ** 0.5, sl)
        if L.top_style in ('coat', 'uniform', 'robe'):
            seg(cv, elb, wr, 6.6 * L.width ** 0.5, sl)
        else:
            seg(cv, elb, wr, 5.4, L.skin if front else L.skin_sh)
        draw_hand(cv, wr, u + l, kind, L.skin if front else L.skin_sh)
        return wr, u + l

    arm(shB, p['aBu'], p['aBl'], p['hB'], False)
    leg(hipB, (p['fBx'] + p['rx'] * 0.3, p['fBy']), False)
    ang = math.radians(lean)
    ux, uy = math.sin(ang), -math.cos(ang)
    nx, ny = -uy, ux
    tw = 10.0 * L.width
    top = (neck[0] + ux, neck[1] + uy)
    bot = (hip[0] - ux * (3 if not dress else -16), hip[1] - uy * (3 if not dress else -16))
    flare = 1.0 if not dress else 1.6
    torso = [(top[0] - nx * (tw - 1.5), top[1] - ny * (tw - 1.5)), (top[0] + nx * (tw - 0.5), top[1] + ny * (tw - 0.5)),
             (bot[0] + nx * (tw + 0.5) * flare, bot[1] + ny * (tw + 0.5) * flare), (bot[0] - nx * (tw + 0.5) * flare, bot[1] - ny * (tw + 0.5) * flare)]
    poly(cv, torso, L.top)
    if L.top_style in ('shirt', 'uniform', 'coat', 'vest'):
        poly(cv, [(top[0] - nx * 3, top[1] - ny * 3), (top[0] + nx * 5, top[1] + ny * 5), (top[0] + nx * 1, top[1] + ny * 1 + 6)], L.accent, ow=1.6)
    if L.top_style == 'uniform':
        for k in (0.35, 0.6, 0.85):
            circle(cv, lerp(top[0], bot[0], k) + nx * 1.5, lerp(top[1], bot[1], k) + ny * 1.5, 0.9, 0xFFE8C860, ink=None)
    if L.top_style == 'vest':
        poly(cv, [(top[0] - nx * 2, top[1] - ny * 2), (bot[0] - nx * 2, bot[1] - ny * 2), (bot[0] - nx * 8, bot[1] - ny * 8), (top[0] - nx * 8, top[1] - ny * 8)], L.accent, ow=1.6)
    leg(hipF, (p['fFx'] + p['rx'] * 0.3, p['fFy']), True)
    if dress:  # skirt over legs
        poly(cv, [(bot[0] + nx * (tw + 0.5) * flare, bot[1] + ny * (tw + 0.5) * flare), (bot[0] - nx * (tw + 0.5) * flare, bot[1] - ny * (tw + 0.5) * flare),
                  (lerp(top[0], bot[0], 0.55) - nx * tw, lerp(top[1], bot[1], 0.55) - ny * tw), (lerp(top[0], bot[0], 0.55) + nx * tw, lerp(top[1], bot[1], 0.55) + ny * tw)], L.top)
    # neck
    seg(cv, (neck[0], neck[1] + 2), (neck[0] + 0.5, neck[1] - 4), 5.5, L.skin, ow=1.6)
    # head
    cv.save()
    cv.translate(neck[0] + 1, neck[1] - 1)
    cv.rotate(p['head'] + p['nod'] * 0.4 + lean * 0.3)
    cv.translate(0, -15)
    e = EXPR.get(expr, EXPR['neutral'])
    fx = 2.5
    _hair_back(cv, L, fx)
    hd = skia.Path()
    hd.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-11.5, -15, 12.5, 14), 11, 12))
    cv.drawPath(hd, P(L.skin))
    cv.drawPath(hd, P(INK, 2.4 * 0.62))
    oval(cv, -10, 2, 2.3, 3.2, L.skin, ow=1.8)
    if L.beard in ('full', 'stubble'):
        poly(cv, [(-9, 2), (14, 2), (12, 12), (4, 16), (-6, 12)], L.hair if L.beard == 'full' else _mix(L.skin, L.hair, 0.35), ink=INK if L.beard == 'full' else None, ow=1.6, smooth=True)
    _hair_front(cv, L, fx)
    ex_n, ex_f, ey = fx + 5.5, fx - 4.5, 0.5
    look_e = dict(e)
    draw_eye(cv, ex_f, ey, 2.6, 3.3, look_e, look, blink, near=False)
    draw_eye(cv, ex_n, ey, 3.1, 3.7, look_e, look, blink, near=True)
    if L.glasses:
        for gx in (ex_f, ex_n):
            circle(cv, gx, ey, 4.4, 0x00000000, ow=1.4)
        seg(cv, (ex_f + 4.2, ey), (ex_n - 4.2, ey), 0.4, INK, ow=0.4)
    bh, bt = e.get('bh', 0), e.get('bt', 0)
    for bx, sign, w in ((ex_f, -1, 2.8), (ex_n, 1, 3.4)):
        tilt = bt * (1 if sign > 0 else -1) * 0.12
        by = ey - 7.6 + bh * 0.5
        seg(cv, (bx - w, by + tilt), (bx + w, by - tilt), 0.9, L.hair if L.hair_style != 'bald' else INK, ow=0.5)
    path = skia.Path()
    path.moveTo(fx + 9.6, 2.5)
    path.quadTo(fx + 12.4, 6.2, fx + 9.0, 6.8)
    cv.drawPath(path, P(INK, 1.6))
    if L.beard == 'moustache':
        poly(cv, [(fx + 1, 8.2), (fx + 7, 8.2), (fx + 8, 9.6), (fx, 9.6)], L.hair, ow=1.0)
    draw_mouth(cv, fx + 4.0, 10.2, viseme, e, k_open, facing)
    if e.get('sweat') or wet > 0:
        poly(cv, [(-8, -8), (-6.6, -4.5), (-9.4, -4.5)], 0xFF9FE3FF, ow=1.0)
    cv.restore()
    wr, a = arm(shF, p['aFu'], p['aFl'], p['hF'], True)
    if prop:
        prop(cv, wr, a, t)
    if alpha < 1:
        cv.restore()
    cv.restore()


def _dark(c, k=0.78):
    a = (c >> 24) & 255
    r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
    return (a << 24) | (int(r * k) << 16) | (int(g * k) << 8) | int(b * k)


def _mix(c1, c2, k):
    out = 0xFF000000
    for sh in (16, 8, 0):
        out |= int(lerp((c1 >> sh) & 255, (c2 >> sh) & 255, k)) << sh
    return out
