"""Keyframed 2D skeletal character rig + expression system + detailed face for close-ups.

Angles are degrees. Limb angles are measured from straight down (0 = hanging), positive = toward the
direction the character faces. Torso/head angles: positive = lean forward. A pose is a dict of joint values;
poses are blended with keyframes and layered with secondary motion (breathing, blinking, head bob).
"""
import math
import skia
from common import C, P, lerp, clamp, ease

JOINTS = ['torso', 'head', 'armB_u', 'armB_l', 'armF_u', 'armF_l', 'legB_u', 'legB_l', 'legF_u', 'legF_l', 'rise', 'rot']
BASE = {k: 0.0 for k in JOINTS}

POSES = {
    'stand':   dict(armB_u=-8, armB_l=10, armF_u=10, armF_l=15, legB_u=-4, legF_u=4),
    'sit':     dict(torso=-4, armB_u=20, armB_l=40, armF_u=35, armF_l=50, legB_u=85, legB_l=-85, legF_u=80, legF_l=-80, rise=-55),
    'slump':   dict(torso=28, head=22, armB_u=10, armB_l=10, armF_u=15, armF_l=20, legB_u=85, legB_l=-85, legF_u=80, legF_l=-80, rise=-55),
    'brace':   dict(torso=-8, armB_u=150, armB_l=-30, armF_u=160, armF_l=-40, legB_u=-25, legB_l=15, legF_u=28, legF_l=-20, rise=-12),
    'panic':   dict(torso=-12, head=-15, armB_u=-135, armB_l=-25, armF_u=130, armF_l=35, legB_u=-10, legF_u=12),
    'pull_a':  dict(torso=20, armB_u=40, armB_l=30, armF_u=60, armF_l=10, legB_u=-15, legF_u=25, legF_l=-20, rise=-6),   # grab cord
    'pull_b':  dict(torso=-15, head=-8, armB_u=20, armB_l=20, armF_u=-60, armF_l=-20, legB_u=-15, legF_u=25, legF_l=-20, rise=-6),  # yank
    'grab_a':  dict(torso=40, head=15, armB_u=60, armB_l=20, armF_u=95, armF_l=10, legB_u=60, legB_l=-90, legF_u=70, legF_l=-80, rise=-50),
    'grab_b':  dict(torso=-5, head=-10, armB_u=40, armB_l=60, armF_u=130, armF_l=-60, legB_u=60, legB_l=-90, legF_u=70, legF_l=-80, rise=-50),
    'offer':   dict(torso=8, armB_u=10, armB_l=10, armF_u=75, armF_l=5, legB_u=85, legB_l=-85, legF_u=80, legF_l=-80, rise=-55),
    'turn_away': dict(torso=-10, head=-35, armB_u=-5, armB_l=30, armF_u=5, armF_l=40, legB_u=85, legB_l=-85, legF_u=80, legF_l=-80, rise=-55),
    'wave_a':  dict(torso=-5, armB_u=160, armB_l=20, armF_u=150, armF_l=40, legB_u=-6, legF_u=6),
    'wave_b':  dict(torso=-5, armB_u=170, armB_l=-25, armF_u=165, armF_l=-30, legB_u=-6, legF_u=6),
    'drop':    dict(torso=18, head=25, armB_u=-5, armB_l=5, armF_u=0, armF_l=5, legB_u=-6, legF_u=6),
    'scratch_a': dict(torso=30, head=20, armB_u=50, armB_l=40, armF_u=80, armF_l=30, legB_u=85, legB_l=-85, legF_u=80, legF_l=-80, rise=-55),
    'scratch_b': dict(torso=30, head=20, armB_u=50, armB_l=40, armF_u=65, armF_l=55, legB_u=85, legB_l=-85, legF_u=80, legF_l=-80, rise=-55),
    'drink':   dict(torso=-25, head=-45, armB_u=60, armB_l=90, armF_u=70, armF_l=95, legB_u=85, legB_l=-85, legF_u=80, legF_l=-80, rise=-55),
    'lie':     dict(rot=-90, armB_u=10, armF_u=-10, legB_u=4, legF_u=-4, rise=-10),
    'swim_a':  dict(rot=80, armB_u=170, armB_l=0, armF_u=40, armF_l=20, legB_u=25, legF_u=-20),
    'swim_b':  dict(rot=80, armB_u=40, armB_l=20, armF_u=170, armF_l=0, legB_u=-20, legF_u=25),
    'crawl_a': dict(rot=70, torso=0, head=-60, armB_u=100, armB_l=-30, armF_u=60, armF_l=-10, legB_u=80, legB_l=-90, legF_u=30, legF_l=-70),
    'crawl_b': dict(rot=70, torso=0, head=-60, armB_u=60, armB_l=-10, armF_u=100, armF_l=-30, legB_u=30, legB_l=-70, legF_u=80, legF_l=-90),
    'collapse': dict(rot=-88, head=-20, armB_u=150, armB_l=0, armF_u=120, armF_l=20, legB_u=8, legF_u=-6, rise=-30),
    'fist':    dict(torso=-10, head=-20, armB_u=-10, armB_l=20, armF_u=175, armF_l=-10, legB_u=60, legB_l=-90, legF_u=70, legF_l=-80, rise=-50),
    'dive':    dict(rot=55, torso=10, armB_u=175, armB_l=0, armF_u=175, armF_l=0, legB_u=-10, legF_u=-5),
}

def pose(name, **over):
    p = dict(BASE); p.update(POSES[name]); p.update(over); return p

def blend(a, b, k):
    return {j: lerp(a.get(j, 0), b.get(j, 0), k) for j in JOINTS}

def keyframes(t, frames):
    """frames: [(time, pose_dict), ...] -> eased blend at t."""
    if t <= frames[0][0]: return frames[0][1]
    for (t0, p0), (t1, p1) in zip(frames, frames[1:]):
        if t <= t1: return blend(p0, p1, ease((t - t0) / max(t1 - t0, 1e-6)))
    return frames[-1][1]

def cycle(t, a, b, period):
    k = 0.5 - 0.5 * math.cos(2 * math.pi * t / period)
    return blend(a, b, k)

# ---- characters (fixed design = always on-model) ----
JOSE = dict(skin='#b9784f', shirt='#d8452f', pants='#2b3440', cap='#1f6fb2', hair='#1d1410', beard=True)
EZEQ = dict(skin='#a86b45', shirt='#2f8a5a', pants='#3a3a46', cap=None, hair='#120c08', beard=False)

EXPR = {  # brow tilt, eye open, pupil size, mouth kind, mouth open
    'neutral':    dict(brow=0, eye=1.0, mouth='line', open=0),
    'happy':      dict(brow=-6, eye=0.9, mouth='smile', open=0.3),
    'determined': dict(brow=14, eye=0.8, mouth='grit', open=0.2),
    'fear':       dict(brow=-18, eye=1.35, mouth='o', open=0.8),
    'shock':      dict(brow=-24, eye=1.5, mouth='o', open=1.0),
    'sad':        dict(brow=-14, eye=0.75, mouth='frown', open=0),
    'exhausted':  dict(brow=-8, eye=0.45, mouth='o', open=0.35),
    'relief':     dict(brow=-10, eye=0.7, mouth='smile', open=0.6),
    'closed':     dict(brow=0, eye=0.0, mouth='line', open=0),
}

def _limb(cv, x0, y0, a1, l1, a2, l2, col, w, face_dir):
    r1 = math.radians(a1); x1 = x0 + l1 * math.sin(r1); y1 = y0 + l1 * math.cos(r1)
    r2 = math.radians(a1 + a2); x2 = x1 + l2 * math.sin(r2); y2 = y1 + l2 * math.cos(r2)
    ink = P(C('#0b1320'), 'stroke', w + 7); fill = P(C(col), 'stroke', w)
    for pnt in (ink, fill):
        cv.drawLine(x0, y0, x1, y1, pnt); cv.drawLine(x1, y1, x2, y2, pnt)
    return x2, y2

def draw_person(cv, x, y, s, p, who=JOSE, expr='neutral', t=0.0, face=1, alpha=1.0, wet=False):
    """Draw a character at hips (x, y). face=1 looks right, -1 left."""
    e = EXPR[expr]
    cv.save(); cv.translate(x, y + p['rise'] * s); cv.scale(s * face, s); cv.rotate(p['rot'])
    if alpha < 0.999: cv.saveLayerAlpha(None, int(255 * clamp(alpha)))
    breath = 2.0 * math.sin(t * 2.4)
    # back leg + back arm
    _limb(cv, -6, 0, p['legB_u'], 62, p['legB_l'], 60, '#222a35', 24, face)
    cv.save(); cv.rotate(p['torso'])
    hb = _limb(cv, -10, -128 - breath, p['armB_u'], 50, p['armB_l'], 48, who['skin'], 17, face)
    cv.drawCircle(hb[0], hb[1], 11, P(C(who['skin'])))
    # torso
    body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect(-38, -146 - breath, 38, 4), 28, 28))
    cv.drawPath(body, P(C(who['shirt']))); cv.drawPath(body, P(C('#0b1320'), 'stroke', 6))
    cv.drawRect(skia.Rect(-38, -20, 38, 4), P(C(who['pants'])))
    cv.restore()
    _limb(cv, 6, 0, p['legF_u'], 62, p['legF_l'], 60, who['pants'], 24, face)
    cv.save(); cv.rotate(p['torso'])
    hf = _limb(cv, 14, -128 - breath, p['armF_u'], 50, p['armF_l'], 48, who['skin'], 17, face)
    cv.drawCircle(hf[0], hf[1], 11, P(C(who['skin'])))
    # head
    cv.translate(0, -150 - breath); cv.rotate(p['head'] * 0.6)
    hy = -44
    cv.drawCircle(0, hy, 46, P(C(who['skin']))); cv.drawCircle(0, hy, 46, P(C('#0b1320'), 'stroke', 6))
    if who.get('beard'):
        bp = skia.Path(); bp.addArc(skia.Rect(-44, hy - 40, 44, hy + 46), 10, 160)
        cv.drawPath(bp, P(C('#3a2a20'), 'stroke', 9, alpha=0.6))
    if who.get('cap'):
        cv.drawArc(skia.Rect(-48, hy - 52, 48, hy + 22), 180, 180, True, P(C(who['cap'])))
        cv.drawRoundRect(skia.Rect(6, hy - 20, 70, hy - 8), 6, 6, P(C(who['cap'])))
    else:
        cv.drawArc(skia.Rect(-47, hy - 50, 47, hy + 26), 190, 165, True, P(C(who['hair'])))
    # face (side view: one eye)
    blink = 1.0 if (t % 2.7) > 0.12 else 0.1
    eo = e['eye'] * blink
    cv.drawOval(skia.Rect(10, hy - 14 - 9 * eo, 32, hy - 14 + 9 * eo), P(C('#ffffff')))
    if eo > 0.15: cv.drawCircle(24, hy - 14, 5.5 * min(1.2, 0.7 + 0.3 * e['eye']), P(C('#0b1320')))
    by = hy - 30; bt = e['brow']
    cv.drawLine(8, by + bt * 0.25, 34, by - bt * 0.25, P(C('#0b1320'), 'stroke', 5))
    mx, my = 24, hy + 18
    if e['mouth'] == 'o':
        cv.drawOval(skia.Rect(mx - 7, my - 5 - 8 * e['open'], mx + 7, my + 5 + 8 * e['open']), P(C('#3a0f0f')))
    elif e['mouth'] == 'smile':
        cv.drawArc(skia.Rect(mx - 14, my - 12, mx + 10, my + 6 + 6 * e['open']), 10, 150, False, P(C('#0b1320'), 'stroke', 4))
    elif e['mouth'] == 'frown':
        cv.drawArc(skia.Rect(mx - 14, my - 2, mx + 10, my + 14), 200, 140, False, P(C('#0b1320'), 'stroke', 4))
    elif e['mouth'] == 'grit':
        cv.drawRoundRect(skia.Rect(mx - 12, my - 5, mx + 10, my + 5), 3, 3, P(C('#ffffff')))
        cv.drawRoundRect(skia.Rect(mx - 12, my - 5, mx + 10, my + 5), 3, 3, P(C('#0b1320'), 'stroke', 3))
    else:
        cv.drawLine(mx - 12, my, mx + 8, my, P(C('#0b1320'), 'stroke', 4))
    if wet:
        for i in range(3):
            k = (t * 1.3 + i * 0.33) % 1
            cv.drawCircle(-20 + i * 18, hy - 10 + k * 60, 4, P(C('#bfe3ff'), alpha=0.8 * (1 - k)))
    cv.restore()
    if alpha < 0.999: cv.restore()
    cv.restore()

def draw_face_closeup(cv, cx, cy, s, who=JOSE, expr='neutral', t=0.0, look=(0.0, 0.0), wet=False, tear=0.0, light='#ffd9a8'):
    """Big front-facing face for extreme close-ups. s=1 -> head ~ 760 px wide."""
    e = EXPR[expr]
    cv.save(); cv.translate(cx, cy); cv.scale(s, s)
    skin = who['skin']
    cv.drawOval(skia.Rect(-400, -470, 400, 470), P(C(skin)))
    # rim light
    cv.drawOval(skia.Rect(-400, -470, 400, 470), P(C(light), 'stroke', 26, blur=18, alpha=0.5))
    cv.drawOval(skia.Rect(-400, -470, 400, 470), P(C('#0b1320'), 'stroke', 14))
    if who.get('beard'):
        for i in range(160):
            a = (i * 37.0) % 180; r = 340 + (i * 13) % 90
            x = r * math.cos(math.radians(a)); y = 120 + r * 0.55 * math.sin(math.radians(a))
            cv.drawCircle(x * 0.9, y, 6, P(C('#3a2a20'), alpha=0.55))
    if who.get('cap'):
        cv.drawArc(skia.Rect(-430, -560, 430, -60), 180, 180, True, P(C(who['cap'])))
        cv.drawRoundRect(skia.Rect(-460, -330, 460, -280), 30, 30, P(C(who['cap'])))
    blink = 1.0 if (t % 2.3) > 0.1 else 0.08
    eo = e['eye'] * blink
    for sx in (-1, 1):
        ex, ey = 170 * sx, -60
        cv.drawOval(skia.Rect(ex - 110, ey - 70 * eo, ex + 110, ey + 70 * eo), P(C('#ffffff')))
        if eo > 0.15:
            px, py = ex + look[0] * 50, ey + look[1] * 30
            cv.save(); cv.clipRect(skia.Rect(ex - 110, ey - 70 * eo, ex + 110, ey + 70 * eo))
            cv.drawCircle(px, py, 52, P(C('#4a2c18'))); cv.drawCircle(px, py, 30 * (0.8 + 0.25 * e['eye']), P(C('#0b1320')))
            cv.drawCircle(px + 18, py - 20, 12, P(C('#ffffff')))
            cv.restore()
        cv.drawOval(skia.Rect(ex - 110, ey - 70 * eo, ex + 110, ey + 70 * eo), P(C('#0b1320'), 'stroke', 10))
        bt = e['brow'] * sx
        cv.drawLine(ex - 110, ey - 130 + bt * 2.2, ex + 110, ey - 130 - bt * 2.2, P(C('#2a1a12'), 'stroke', 30))
    nose = skia.Path(); nose.moveTo(-10, -20); nose.quadTo(-55, 110, 10, 130)
    cv.drawPath(nose, P(C('#0b1320'), 'stroke', 10))
    my = 240
    if e['mouth'] == 'o':
        cv.drawOval(skia.Rect(-60, my - 40 - 60 * e['open'], 60, my + 40 + 40 * e['open']), P(C('#3a0f0f')))
    elif e['mouth'] == 'smile':
        cv.drawArc(skia.Rect(-130, my - 80, 130, my + 50 + 40 * e['open']), 15, 150, False, P(C('#0b1320'), 'stroke', 14))
    elif e['mouth'] == 'frown':
        cv.drawArc(skia.Rect(-120, my, 120, my + 120), 200, 140, False, P(C('#0b1320'), 'stroke', 14))
    elif e['mouth'] == 'grit':
        cv.drawRoundRect(skia.Rect(-110, my - 35, 110, my + 35), 20, 20, P(C('#ffffff')))
        cv.drawRoundRect(skia.Rect(-110, my - 35, 110, my + 35), 20, 20, P(C('#0b1320'), 'stroke', 10))
        cv.drawLine(-110, my, 110, my, P(C('#0b1320'), 'stroke', 6))
    else:
        cv.drawLine(-90, my, 90, my, P(C('#0b1320'), 'stroke', 14))
    if wet:
        for i in range(14):
            k = (t * 0.9 + i * 0.137) % 1; x = -330 + (i * 53) % 660
            cv.drawOval(skia.Rect(x - 9, -300 + k * 700, x + 9, -270 + k * 700), P(C('#cfe9ff'), alpha=0.85 * (1 - k)))
    if tear > 0:
        k = clamp(tear)
        cv.drawOval(skia.Rect(-200, -10 + 260 * k, -176, 30 + 260 * k), P(C('#cfe9ff'), alpha=0.95))
    cv.restore()
