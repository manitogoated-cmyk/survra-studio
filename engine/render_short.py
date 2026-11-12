"""Pilot animated Short renderer: code-drawn 2D cutout animation with skia, piped to ffmpeg.

Everything on screen is drawn here: sky, ocean layers, weather, boat, rigged characters,
island, map inset, day counter and captions. No third-party imagery.
"""
import json, math, random, subprocess, sys, os
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
rnd = random.Random(7)

# ---------- helpers ----------
def C(hexs, a=255):
    hexs = hexs.lstrip('#'); return skia.Color(int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16), a)

def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3

def mix_hex(h1, h2, t):
    a = [int(h1[i:i+2], 16) for i in (1, 3, 5)]; b = [int(h2[i:i+2], 16) for i in (1, 3, 5)]
    return '#' + ''.join('%02x' % int(lerp(x, y, clamp(t))) for x, y in zip(a, b))

def P(color, style='fill', width=0, blur=0, alpha=None):
    p = skia.Paint(AntiAlias=True, Color=color)
    if style == 'stroke':
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(width); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if alpha is not None: p.setAlphaf(alpha)
    return p

TF_BLACK = skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant))
TF_BOLD = skia.Typeface('Inter', skia.FontStyle(700, 5, skia.FontStyle.kUpright_Slant))

# Brand palette (working hypothesis, finalized in Phase 3)
BRAND = {'accent': '#ffb000', 'danger': '#ff4b3e', 'ink': '#0b1320', 'paper': '#f4efe6'}

# ---------- environment ----------
SKIES = {
    'dawn':   ('#2b3a67', '#f6a46b'),
    'day':    ('#3a8dde', '#bfe3ff'),
    'storm':  ('#0e141d', '#3a4656'),
    'grey':   ('#4f6273', '#a9b8c4'),
    'night':  ('#04070f', '#1a2a4a'),
    'sunset': ('#3b2a5a', '#ff8a4c'),
}
SEAS = {
    'dawn':  ['#1d3b5c', '#24507a', '#2f6798', '#3f80b3'],
    'day':   ['#0d4f8b', '#1665a8', '#1f7cc4', '#3496dc'],
    'storm': ['#0a1622', '#102232', '#163045', '#1d3d57'],
    'grey':  ['#21394f', '#2a4964', '#335a7a', '#3e6c90'],
    'night': ['#050c18', '#081324', '#0c1b31', '#11243f'],
    'sunset':['#2a2f5a', '#3a3f72', '#4b528a', '#5d66a3'],
}

def sky(cv, key, t, mix_to=None, m=0.0):
    top, bot = SKIES[key]
    if mix_to: top = mix_hex(top, SKIES[mix_to][0], m); bot = mix_hex(bot, SKIES[mix_to][1], m)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H * 0.62)], [C(top), C(bot)])
    p = skia.Paint(Shader=sh); cv.drawRect(skia.Rect(0, 0, W, H), p)

def stars(cv, t, alpha):
    if alpha <= 0: return
    r = random.Random(3)
    for i in range(140):
        x, y = r.uniform(0, W), r.uniform(0, H * 0.55); s = r.uniform(1, 3.2)
        tw = 0.6 + 0.4 * math.sin(t * 2 + i)
        cv.drawCircle(x, y, s, P(C('#ffffff'), alpha=alpha * tw))

def sun(cv, x, y, r, color='#ffd27a', glow=True):
    if glow: cv.drawCircle(x, y, r * 2.4, P(C(color), blur=r * 0.9, alpha=0.45))
    cv.drawCircle(x, y, r, P(C(color)))

def moon(cv, x, y, r, phase):
    """phase 0..1: 0 new, 0.5 full."""
    cv.drawCircle(x, y, r * 2.2, P(C('#cfe0ff'), blur=r * 0.8, alpha=0.25))
    cv.drawCircle(x, y, r, P(C('#eef3ff')))
    k = math.cos(phase * 2 * math.pi)  # 1 new .. -1 full
    if k > -0.98:
        cv.save(); cv.clipPath(skia.Path().addCircle(x, y, r), skia.ClipOp.kIntersect, True)
        off = r * 2 * (1 - (1 - k) / 2) if phase < 0.5 else -r * 2 * (1 - (1 - k) / 2)
        cv.drawCircle(x + off, y, r * 1.02, P(C('#0b1426')))
        cv.restore()

CLOUDS = [(rnd.uniform(0, 1), rnd.uniform(0.05, 0.4), rnd.uniform(0.6, 1.4)) for _ in range(9)]
def clouds(cv, t, color, alpha=0.9, speed=12, dark=False):
    for i, (u, v, s) in enumerate(CLOUDS):
        x = ((u * W * 1.6 + t * speed * s) % (W * 1.6)) - W * 0.3; y = v * H
        p = P(C(color), blur=18, alpha=alpha)
        for dx, dy, rr in [(-90, 10, 70), (-20, -20, 95), (60, 0, 80), (130, 18, 55), (0, 30, 90)]:
            cv.drawCircle(x + dx * s, y + dy * s, rr * s, p)

def wave_y(x, t, layer, amp, horizon):
    k = layer + 1
    return (horizon + layer * (H - horizon) * 0.2
            + amp * (0.55 * math.sin(x * 0.006 * (1 + layer * 0.35) + t * (0.9 + 0.25 * layer) + layer)
                     + 0.3 * math.sin(x * 0.013 + t * 1.7 + layer * 2.1)
                     + 0.15 * math.sin(x * 0.031 - t * 2.3)) * (0.6 + 0.4 * k / 4))

def ocean(cv, key, t, amp=26, horizon=None, upto=4, foam=True):
    horizon = horizon or H * 0.58
    cols = SEAS[key]
    for layer in range(upto):
        path = skia.Path(); path.moveTo(0, H)
        for x in range(0, W + 30, 30): path.lineTo(x, wave_y(x, t, layer, amp, horizon))
        path.lineTo(W, H); path.close()
        cv.drawPath(path, P(C(cols[layer])))
        if foam and layer >= 1:
            fp = skia.Path(); first = True
            for x in range(0, W + 30, 30):
                y = wave_y(x, t, layer, amp, horizon)
                if first: fp.moveTo(x, y); first = False
                else: fp.lineTo(x, y)
            cv.drawPath(fp, P(C('#ffffff'), 'stroke', 3, alpha=0.10 + 0.05 * layer))

def rain(cv, t, density=260, alpha=0.55, wind=-0.35):
    r = random.Random(11)
    p = P(C('#c9d6e3'), 'stroke', 2.2, alpha=alpha)
    for i in range(density):
        x0, y0, sp = r.uniform(-200, W + 200), r.uniform(0, H), r.uniform(1500, 2300)
        y = (y0 + t * sp) % (H + 200) - 100; x = x0 + wind * (y - y0) * 0.2
        cv.drawLine(x, y, x + wind * 40, y + 40, p)

def lightning(cv, strength, seed):
    if strength <= 0: return
    cv.drawRect(skia.Rect(0, 0, W, H), P(C('#dfe8ff'), alpha=0.35 * strength))
    r = random.Random(seed); x = r.uniform(W * 0.2, W * 0.8); y = 0
    path = skia.Path(); path.moveTo(x, y)
    while y < H * 0.5:
        x += r.uniform(-60, 60); y += r.uniform(40, 90); path.lineTo(x, y)
    cv.drawPath(path, P(C('#ffffff'), 'stroke', 6, alpha=strength))
    cv.drawPath(path, P(C('#9fb7ff'), 'stroke', 18, blur=10, alpha=0.6 * strength))

# ---------- props ----------
def boat(cv, x, y, ang, scale=1.0, engine_ok=True, icebox=True):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(scale, scale)
    hull = skia.Path(); hull.moveTo(-260, -30); hull.lineTo(250, -30); hull.quadTo(300, -32, 330, -70)
    hull.lineTo(300, 25); hull.quadTo(0, 60, -240, 30); hull.close()
    cv.drawPath(hull, P(C('#f2f2ee')))
    stripe = skia.Path(); stripe.moveTo(-252, -8); stripe.lineTo(312, -8); stripe.lineTo(306, 8); stripe.lineTo(-246, 8); stripe.close()
    cv.drawPath(stripe, P(C('#1f6fb2')))
    cv.drawPath(hull, P(C('#0b1320'), 'stroke', 5))
    # outboard motor at stern
    cv.drawRoundRect(skia.Rect(-300, -95, -250, -35), 10, 10, P(C('#2a2f36' if engine_ok else '#55585c')))
    cv.drawRect(skia.Rect(-285, -35, -270, 40), P(C('#2a2f36')))
    if icebox:
        cv.drawRoundRect(skia.Rect(60, -105, 200, -30), 8, 8, P(C('#e8eef2')))
        cv.drawRoundRect(skia.Rect(60, -105, 200, -30), 8, 8, P(C('#0b1320'), 'stroke', 4))
        cv.drawLine(60, -85, 200, -85, P(C('#9fb3c2'), 'stroke', 3))
    cv.restore()

def person(cv, x, y, s=1.0, pose='stand', t=0.0, shirt='#d8452f', skin='#b9784f', cap='#c0392b', hair='#1d1410',
           face='neutral', look=1, alpha=1.0):
    """2D cutout rig. Same proportions every time so a character stays on-model."""
    cv.save(); cv.translate(x, y); cv.scale(s * look, s)
    if alpha < 1: cv.saveLayerAlpha(None, int(255 * alpha))
    ink = P(C('#0b1320'), 'stroke', 5)
    def limb(x0, y0, l1, a1, l2, a2, col, w):
        x1, y1 = x0 + l1 * math.sin(a1), y0 + l1 * math.cos(a1)
        x2, y2 = x1 + l2 * math.sin(a1 + a2), y1 + l2 * math.cos(a1 + a2)
        pp = P(C(col), 'stroke', w); cv.drawLine(x0, y0, x1, y1, pp); cv.drawLine(x1, y1, x2, y2, pp)
        return x2, y2
    sw = math.sin(t * 2.2)
    if pose == 'stand':     legs = [(0.08, 0.0), (-0.08, 0.0)]; arms = [(0.35 + 0.05 * sw, -0.4), (-0.3, 0.3)]; torso_ang = 0
    elif pose == 'sit':     legs = [(-1.4, 1.5), (-1.3, 1.4)]; arms = [(0.6, -1.0), (-0.2, 0.6)]; torso_ang = 0.05
    elif pose == 'brace':   legs = [(0.45, -0.2), (-0.45, 0.2)]; arms = [(2.4 + 0.1 * sw, 0.4), (-2.3, -0.3)]; torso_ang = -0.12 * sw
    elif pose == 'reach':   legs = [(0.1, 0), (-0.1, 0)]; arms = [(2.9, 0.0), (-2.7, 0.2)]; torso_ang = 0
    elif pose == 'fish':    legs = [(-1.3, 1.4), (-1.2, 1.3)]; arms = [(1.2 + 0.25 * sw, -0.6), (1.0 + 0.2 * sw, -0.4)]; torso_ang = 0.25
    elif pose == 'lie':     cv.rotate(-90); legs = [(0.05, 0), (-0.05, 0)]; arms = [(0.2, 0), (-0.2, 0)]; torso_ang = 0
    elif pose == 'kneel':  cv.rotate(18); legs = [(-1.5, 2.6), (-1.35, 2.5)]; arms = [(-0.25 + 0.15 * sw, 0.2), (0.5, 0.3)]; torso_ang = 0
    elif pose == 'crawl':   cv.rotate(-62); legs = [(0.6 + 0.3 * sw, 0.6), (-0.3 - 0.3 * sw, 0.9)]; arms = [(2.2 + 0.4 * sw, -0.5), (1.6 - 0.4 * sw, -0.3)]; torso_ang = 0
    elif pose == 'swim':    cv.rotate(-80); legs = [(0.3 * sw, 0), (-0.3 * sw, 0)]; arms = [(2.6 + 0.9 * sw, 0.2), (2.6 - 0.9 * sw, 0.2)]; torso_ang = 0
    else: legs = [(0, 0), (0, 0)]; arms = [(0.3, -0.3), (-0.3, 0.3)]; torso_ang = 0
    cv.rotate(math.degrees(torso_ang))
    # back limbs
    limb(-8, -10, 58, legs[1][0], 58, legs[1][1], '#2b3440', 22)
    limb(-14, -128, 46, arms[1][0], 44, arms[1][1], skin, 16)
    # torso
    cv.drawRoundRect(skia.Rect(-36, -140, 36, -2), 26, 26, P(C(shirt)))
    cv.drawRoundRect(skia.Rect(-36, -140, 36, -2), 26, 26, ink)
    # front limbs
    limb(8, -10, 58, legs[0][0], 58, legs[0][1], '#323d4b', 22)
    hx, hy = limb(16, -128, 46, arms[0][0], 44, arms[0][1], skin, 16)
    # head
    cv.drawCircle(0, -178, 38, P(C(skin))); cv.drawCircle(0, -178, 38, ink)
    if cap:
        cv.drawArc(skia.Rect(-40, -222, 40, -150), 180, 180, True, P(C(cap)))
        cv.drawRoundRect(skia.Rect(4, -186, 58, -176), 5, 5, P(C(cap)))
    else:
        cv.drawArc(skia.Rect(-39, -218, 39, -156), 185, 170, True, P(C(hair)))
    # face
    eye = P(C('#0b1320'))
    if face == 'closed':
        cv.drawLine(8, -180, 20, -180, P(C('#0b1320'), 'stroke', 4))
    else:
        cv.drawCircle(14, -182, 4.5, eye)
    if face == 'worried': cv.drawArc(skia.Rect(6, -166, 30, -152), 200, 140, False, P(C('#0b1320'), 'stroke', 3.5))
    elif face == 'determined': cv.drawLine(8, -160, 28, -162, P(C('#0b1320'), 'stroke', 3.5))
    elif face == 'relief': cv.drawArc(skia.Rect(6, -172, 30, -156), 20, 140, False, P(C('#0b1320'), 'stroke', 3.5))
    else: cv.drawLine(10, -161, 26, -161, P(C('#0b1320'), 'stroke', 3))
    if alpha < 1: cv.restore()
    cv.restore()

def fish(cv, x, y, s, ang, col='#9fc6d8'):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    b = skia.Path(); b.moveTo(-40, 0); b.quadTo(0, -24, 40, 0); b.quadTo(0, 24, -40, 0); b.close()
    cv.drawPath(b, P(C(col)))
    tl = skia.Path(); tl.moveTo(-38, 0); tl.lineTo(-62, -18); tl.lineTo(-62, 18); tl.close(); cv.drawPath(tl, P(C(col)))
    cv.drawCircle(24, -4, 3.5, P(C('#0b1320'))); cv.restore()

def bird(cv, x, y, s, flap, col='#0b1320'):
    p = P(C(col), 'stroke', 5 * s); f = math.sin(flap) * 18 * s
    path = skia.Path(); path.moveTo(x - 34 * s, y - f); path.quadTo(x - 14 * s, y - 18 * s, x, y); path.quadTo(x + 14 * s, y - 18 * s, x + 34 * s, y - f)
    cv.drawPath(path, p)

def turtle(cv, x, y, s):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawOval(skia.Rect(-60, -34, 60, 34), P(C('#4f7a3a')))
    for gx in (-25, 0, 25): cv.drawCircle(gx, 0, 13, P(C('#3c5f2c')))
    cv.drawCircle(72, -4, 20, P(C('#6f9a55')))
    for fx, fy in ((-40, 34), (40, 34), (-40, -34), (40, -34)): cv.drawOval(skia.Rect(fx - 18, fy - 9, fx + 18, fy + 9), P(C('#6f9a55')))
    cv.restore()

def coconut(cv, x, y, s):
    cv.drawCircle(x, y, 26 * s, P(C('#5a3a1e'))); cv.drawCircle(x - 8 * s, y - 8 * s, 6 * s, P(C('#7a5230')))

def palm(cv, x, y, s, t):
    trunk = skia.Path(); trunk.moveTo(x, y); trunk.quadTo(x + 40 * s, y - 220 * s, x + 20 * s, y - 420 * s)
    cv.drawPath(trunk, P(C('#6b4a2b'), 'stroke', 26 * s))
    tx, ty = x + 20 * s, y - 420 * s
    for i in range(6):
        a = -math.pi / 2 + (i - 2.5) * 0.55 + 0.05 * math.sin(t * 1.5 + i)
        ex, ey = tx + math.cos(a) * 190 * s, ty + math.sin(a) * 120 * s + 60 * s
        lp = skia.Path(); lp.moveTo(tx, ty); lp.quadTo((tx + ex) / 2, ty - 70 * s, ex, ey)
        cv.drawPath(lp, P(C('#2f7a3a'), 'stroke', 22 * s))

def island(cv, cx, horizon, s, t):
    hill = skia.Path(); hill.moveTo(cx - 520 * s, horizon + 6); hill.quadTo(cx, horizon - 120 * s, cx + 520 * s, horizon + 6); hill.close()
    cv.drawPath(hill, P(C('#e9d39b')))
    palm(cv, cx - 120 * s, horizon - 40 * s, s, t); palm(cv, cx + 90 * s, horizon - 60 * s, s * 0.85, t + 1); palm(cv, cx + 260 * s, horizon - 20 * s, s * 0.7, t + 2)

def ship(cv, x, y, s):
    hp = skia.Path(); hp.moveTo(x - 160 * s, y); hp.lineTo(x + 160 * s, y); hp.lineTo(x + 130 * s, y + 34 * s); hp.lineTo(x - 140 * s, y + 34 * s); hp.close()
    cv.drawPath(hp, P(C('#1b2533')))
    cv.drawRect(skia.Rect(x - 60 * s, y - 50 * s, x + 40 * s, y), P(C('#1b2533')))
    cv.drawRect(skia.Rect(x - 20 * s, y - 90 * s, x, y - 50 * s), P(C('#1b2533')))

# ---------- HUD ----------
def day_counter(cv, day, accent=BRAND['accent'], pulse=0.0):
    f_label = skia.Font(TF_BOLD, 40); f_num = skia.Font(TF_BLACK, 132)
    label = 'DAY'; num = f'{int(day):,}'
    x = 70; y = 250
    cv.drawRoundRect(skia.Rect(x - 26, y - 168, x + 40 + f_num.measureText(num) + 30, y + 34), 28, 28, P(C('#000000'), alpha=0.35))
    cv.drawString(label, x, y - 118, f_label, P(C(accent)))
    cv.drawString(num, x - 6, y, f_num, P(C('#ffffff')))
    if pulse > 0: cv.drawString(num, x - 6, y, f_num, P(C(accent), alpha=pulse))

def meter(cv, label, val, y, col):
    f = skia.Font(TF_BOLD, 30); x = W - 330
    cv.drawString(label, x, y, f, P(C('#ffffff'), alpha=0.9))
    cv.drawRoundRect(skia.Rect(x, y + 12, x + 260, y + 34), 11, 11, P(C('#000000'), alpha=0.35))
    cv.drawRoundRect(skia.Rect(x, y + 12, x + 260 * clamp(val), y + 34), 11, 11, P(C(col)))

def map_inset(cv, prog, alpha=1.0):
    """Simplified Pacific: Mexico (right) to Marshall Islands (left); not to scale."""
    x0, y0, w, h = 90, 330, 900, 400
    cv.saveLayerAlpha(skia.Rect(x0 - 20, y0 - 20, x0 + w + 20, y0 + h + 20), int(255 * alpha))
    cv.drawRoundRect(skia.Rect(x0, y0, x0 + w, y0 + h), 30, 30, P(C('#0f2a44'), alpha=0.92))
    land = skia.Path(); land.moveTo(x0 + w, y0 + 40); land.lineTo(x0 + w - 60, y0 + 120); land.quadTo(x0 + w - 150, y0 + 230, x0 + w - 110, y0 + 300); land.lineTo(x0 + w, y0 + 340); land.close()
    cv.drawPath(land, P(C('#d8c79a')))
    start = (x0 + w - 135, y0 + 245); end = (x0 + 120, y0 + 265)
    for ix, iy in ((x0 + 105, y0 + 250), (x0 + 128, y0 + 268), (x0 + 140, y0 + 238)): cv.drawCircle(ix, iy, 6, P(C('#d8c79a')))
    path = skia.Path(); path.moveTo(*start); path.cubicTo(x0 + 560, y0 + 120, x0 + 330, y0 + 330, *end)
    meas = skia.PathMeasure(path, False); L = meas.getLength(); part = skia.Path()
    meas.getSegment(0, L * clamp(prog), part, True)
    dash = P(C(BRAND['accent']), 'stroke', 7); dash.setPathEffect(skia.DashPathEffect.Make([22, 14], 0))
    cv.drawPath(part, dash)
    pos, _ = meas.getPosTan(L * clamp(prog))
    cv.drawCircle(pos.x(), pos.y(), 14, P(C(BRAND['danger'])))
    f = skia.Font(TF_BOLD, 30)
    cv.drawString('MEXICO', x0 + w - 230, y0 + 60, f, P(C('#ffffff'), alpha=0.85))
    cv.drawString('MARSHALL ISLANDS', x0 + 40, y0 + 320, f, P(C('#ffffff'), alpha=0.85 if prog > 0.95 else 0.4))
    miles = int(6700 * clamp(prog))
    cv.drawString(f'{miles:,} MILES', x0 + 40, y0 + 70, skia.Font(TF_BLACK, 52), P(C(BRAND['accent'])))
    cv.drawString('Not to scale', x0 + w - 200, y0 + h - 22, skia.Font(TF_BOLD, 22), P(C('#ffffff'), alpha=0.45))
    cv.restore()

def captions(cv, words, t):
    """Big mobile captions: 3-4 words per line, current word highlighted."""
    cur = [w for w in words if w['start'] - 0.05 <= t]
    if not cur: return
    idx = len(cur) - 1
    if t > words[-1]['end'] + 0.4: return
    g0 = (idx // 4) * 4; grp = words[g0:g0 + 4]
    f = skia.Font(TF_BLACK, 84); space = f.measureText(' ')
    widths = [f.measureText(w['w'].upper()) for w in grp]; total = sum(widths) + space * (len(grp) - 1)
    if total > W - 120:  # shrink long groups
        f = skia.Font(TF_BLACK, 84 * (W - 120) / total); space = f.measureText(' ')
        widths = [f.measureText(w['w'].upper()) for w in grp]; total = sum(widths) + space * (len(grp) - 1)
    x = (W - total) / 2; y = H * 0.715
    for w, wd in zip(grp, widths):
        txt = w['w'].upper(); active = words.index(w) == idx
        stroke = P(C('#000000'), 'stroke', 16)
        cv.drawString(txt, x, y, f, stroke)
        cv.drawString(txt, x, y, f, P(C(BRAND['accent'] if active else '#ffffff')))
        x += wd + space

# ---------- scenes ----------
def scene_hook(cv, t, d):
    sky(cv, 'dawn', t); sun(cv, W * 0.7, H * 0.40, 70)
    horizon = H * 0.47
    island(cv, W * 0.5, horizon + 30, 1.2, t)
    sand = skia.Path(); sand.moveTo(0, H * 0.55); sand.quadTo(W * 0.5, H * 0.50, W, H * 0.56); sand.lineTo(W, H); sand.lineTo(0, H); sand.close()
    cv.drawPath(sand, P(C('#d9bf86')))
    # surf washing up
    for i in range(3):
        k = (t * 0.35 + i / 3) % 1
        cv.drawOval(skia.Rect(-100, H * 0.60 + k * 60, W + 100, H * 0.66 + k * 60), P(C('#ffffff'), 'stroke', 6, alpha=0.35 * (1 - k)))
    ocean(cv, 'dawn', t, amp=14, horizon=H * 0.70, upto=2)
    x = lerp(W * 0.40, W * 0.52, ease(t / max(d, 0.1)))
    person(cv, x, H * 0.60, 1.5, pose='kneel', t=t * 2, cap='#c0392b', shirt='#8a6a50', face='determined')
    gl = 0.5 + 0.5 * math.sin(t * 5)
    cv.drawCircle(x + 70, H * 0.60 - 150, 10 + 8 * gl, P(C('#ffffff'), blur=6, alpha=0.6 * gl))
    cv.drawRect(skia.Rect(0, 0, W, H), P(C('#1a0f05'), alpha=0.12))

def scene_depart(cv, t, d):
    sky(cv, 'day', t); sun(cv, W * 0.82, H * 0.18, 60); clouds(cv, t, '#ffffff', 0.9)
    horizon = H * 0.50
    coast = skia.Path(); coast.moveTo(W * 0.55, horizon + 4); coast.quadTo(W * 0.8, horizon - 90, W + 10, horizon - 140); coast.lineTo(W + 10, horizon + 4); coast.close()
    cv.drawPath(coast, P(C('#4c8a4e')))
    ocean(cv, 'day', t, amp=14, horizon=horizon)
    bx = lerp(W * 0.6, W * 0.4, ease(t / d)); by = wave_y(bx, t, 1, 14, horizon) - 10
    ang = 2 * math.sin(t * 1.4)
    cv.save(); cv.translate(bx, by); cv.rotate(ang)
    person(cv, -170, -45, 0.95, 'stand', t, look=-1, face='neutral')
    person(cv, 45, -45, 0.95, 'stand', t + 1, shirt='#2f8a5a', cap=None, look=-1)
    cv.restore()
    boat(cv, bx, by, ang, 1.0)

def scene_storm(cv, t, d):
    sky(cv, 'storm', t); clouds(cv, t, '#1c2532', 0.95, speed=60, dark=True)
    horizon = H * 0.47
    flash = max(0, 1 - abs(t - 1.2) * 6) + max(0, 1 - abs(t - 3.4) * 7)
    ocean(cv, 'storm', t * 1.8, amp=70, horizon=horizon)
    bx = W * 0.5; by = wave_y(bx, t * 1.8, 1, 70, horizon) - 20
    ang = 14 * math.sin(t * 2.1)
    cv.save(); cv.translate(bx, by); cv.rotate(ang)
    person(cv, -170, -45, 0.95, 'brace', t * 3, face='worried', look=-1)
    person(cv, 60, -45, 0.95, 'brace', t * 3 + 1, shirt='#2f8a5a', cap=None, face='worried')
    cv.restore()
    boat(cv, bx, by, ang, 1.0, engine_ok=t < 1.2)
    if t > 1.25:  # engine smoke
        for i in range(6):
            a = (t * 1.5 + i * 0.4) % 1.5
            cv.drawCircle(bx - 290 + a * 30, by - 120 - a * 200, 26 + a * 30, P(C('#3b3f45'), blur=8, alpha=0.5 * (1 - a / 1.5)))
    rain(cv, t, 320, 0.6)
    lightning(cv, flash, int(t > 2))

def scene_food(cv, t, d):
    sky(cv, 'grey', t, 'day', 0.4 + 0.3 * math.sin(t)); clouds(cv, t, '#e8eef2', 0.7)
    horizon = H * 0.50
    ocean(cv, 'grey', t, amp=22, horizon=horizon)
    bx = W * 0.5; by = wave_y(bx, t, 1, 22, horizon); ang = 3 * math.sin(t * 1.3)
    cv.save(); cv.translate(bx, by); cv.rotate(ang)
    person(cv, -180, -45, 0.95, 'fish', t * 2, face='determined', look=-1)
    person(cv, 60, -45, 0.95, 'sit', t, shirt='#2f8a5a', cap=None, face='neutral')
    cv.restore(); boat(cv, bx, by, ang, 1.0)
    # icons pop in: fish, turtle, bird, rain
    beats = [(0.0, 'fish'), (d * 0.28, 'turtle'), (d * 0.5, 'bird'), (d * 0.72, 'rain')]
    for i, (bt, kind) in enumerate(beats):
        k = ease_out((t - bt) / 0.5)
        if k <= 0: continue
        cx = 200 + i * 230; cy = 470
        cv.drawCircle(cx, cy, 95 * k, P(C('#ffffff'), alpha=0.92))
        if kind == 'fish': fish(cv, cx, cy, 1.2 * k, 0)
        elif kind == 'turtle': turtle(cv, cx - 6, cy, 0.85 * k)
        elif kind == 'bird': bird(cv, cx, cy + 10, 1.6 * k, t * 6)
        else:
            for j in range(5): cv.drawLine(cx - 40 + j * 20, cy - 40, cx - 50 + j * 20, cy + 30, P(C('#3b8fd6'), 'stroke', 7 * k))
    if t > beats[2][0]:
        for j in range(3): bird(cv, (W * 0.2 + j * 140 + t * 60) % W, 760 + j * 30, 0.9, t * 7 + j)

def scene_loss(cv, t, d):
    sky(cv, 'night', t); stars(cv, t, 0.9); moon(cv, W * 0.75, H * 0.38, 60, 0.5)
    horizon = H * 0.50
    ocean(cv, 'night', t * 0.6, amp=12, horizon=horizon)
    bx = W * 0.5; by = wave_y(bx, t * 0.6, 1, 12, horizon); ang = 1.5 * math.sin(t)
    fade = 1 - ease((t - d * 0.45) / (d * 0.35))
    cv.save(); cv.translate(bx, by); cv.rotate(ang)
    person(cv, -180, -45, 0.95, 'sit', t, face='worried', look=1)
    person(cv, 170, -60, 0.95, 'lie', t, shirt='#2f8a5a', cap=None, face='closed', alpha=fade)
    cv.restore(); boat(cv, bx, by, ang, 1.0)
    cv.drawCircle(bx, by - 120, 420, P(C('#9fb7ff'), blur=120, alpha=0.18))

def scene_alone(cv, t, d):
    cyc = t / d * 4  # four day/night cycles
    night = 0.5 + 0.5 * math.cos(cyc * 2 * math.pi)
    sky(cv, 'day', t, 'night', night); stars(cv, t, night)
    moon(cv, W * 0.2 + (cyc % 1) * W * 0.6, H * 0.43, 52, (cyc * 0.25 + 0.1) % 1)
    horizon = H * 0.50
    ship(cv, lerp(-200, W + 200, clamp(t / d * 1.4)), horizon - 6, 0.7)
    ocean(cv, 'day' if night < 0.5 else 'night', t, amp=16, horizon=horizon)
    bx = W * 0.5; by = wave_y(bx, t, 1, 16, horizon); ang = 2 * math.sin(t)
    cv.save(); cv.translate(bx, by); cv.rotate(ang)
    person(cv, 60, -45, 0.95, 'reach' if 0.25 < t / d < 0.55 else 'sit', t, face='worried', shirt='#8a6a50')
    cv.restore(); boat(cv, bx, by, ang, 1.0)

def scene_land(cv, t, d):
    k = ease(t / d)
    sky(cv, 'day', t, 'sunset', 0.2); sun(cv, W * 0.18, H * 0.44, 55)
    horizon = H * 0.56
    island(cv, W * 0.5, horizon + 4, lerp(0.25, 1.1, k), t)
    ocean(cv, 'day', t, amp=18, horizon=horizon)
    for j in range(4): bird(cv, (W * 0.15 + j * 170 + t * 80) % W, 800 + 40 * math.sin(j), 1.0, t * 7 + j)
    for j in range(3):
        cx = W * 0.25 + j * 260; cy = wave_y(cx, t, 1, 18, horizon) + 30
        if t > d * 0.1 * j: coconut(cv, cx, cy, 1.0)
    if t > d * 0.55:
        person(cv, W * 0.5, wave_y(W * 0.5, t, 1, 18, horizon) + 40, 1.1, 'swim', t * 3, face='determined', shirt='#8a6a50')

def scene_end(cv, t, d):
    sky(cv, 'sunset', t); sun(cv, W * 0.5, H * 0.52, 90)
    horizon = H * 0.56
    ocean(cv, 'sunset', t * 0.6, amp=10, horizon=horizon)
    k = ease_out(t / 0.8)
    f1 = skia.Font(TF_BLACK, 190 * (0.9 + 0.1 * k)); f2 = skia.Font(TF_BLACK, 84)
    for txt, f, y, col in (('438', f1, H * 0.34, BRAND['accent']), ('DAYS ADRIFT', f2, H * 0.34 + 110, '#ffffff'), ('6,700 MILES', f2, H * 0.34 + 215, '#ffffff')):
        x = (W - f.measureText(txt)) / 2
        cv.drawString(txt, x, y, f, P(C('#000000'), 'stroke', 18, alpha=0.6 * k))
        cv.drawString(txt, x, y, f, P(C(col), alpha=k))

SCENES = {'hook': scene_hook, 'depart': scene_depart, 'storm': scene_storm, 'food': scene_food,
          'loss': scene_loss, 'alone': scene_alone, 'land': scene_land, 'end': scene_end}
SHOW_MAP = {'depart': (0.0, 0.02), 'alone': (0.25, 0.85), 'land': (0.88, 1.0)}

def render(build_dir, out_path):
    tl = json.load(open(os.path.join(build_dir, 'timeline.json')))
    segs = tl['segments']; total = tl['duration']; n = int(total * FPS)
    # scene windows: each scene runs from its narration start to next segment start
    wins = []
    for i, s in enumerate(segs):
        a = 0 if i == 0 else s['start'] - 0.2
        b = segs[i + 1]['start'] - 0.2 if i + 1 < len(segs) else total
        wins.append((a, b, s))
    words = [w for s in segs for w in s['words']]
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    prev_day = segs[0]['day']; XF = 0.35
    for fi in range(n):
        t = fi / FPS
        wi = max(i for i, (a, b, s) in enumerate(wins) if a <= t or i == 0)
        a, b, s = wins[wi]
        cv.clear(C('#000000'))
        SCENES[s['scene']](cv, t - a, b - a)
        # crossfade from previous scene
        if wi > 0 and t - a < XF:
            pa, pb, ps = wins[wi - 1]
            cv.saveLayerAlpha(None, int(255 * (1 - (t - a) / XF)))
            SCENES[ps['scene']](cv, t - pa, pb - pa); cv.restore()
        # day counter ticks toward this segment's day
        start_day = wins[wi - 1][2]['day'] if wi > 0 else s['day']
        tick = ease_out((t - a) / 1.2); day = lerp(start_day, s['day'], tick) if s['day'] >= start_day else s['day']  # flashbacks cut, never count down
        if s['scene'] != 'end': day_counter(cv, day, pulse=max(0, 0.6 - (t - a)) if s['day'] > start_day else 0)
        # supplies meters (story-driven)
        food = {'hook': 0.08, 'depart': 1.0, 'storm': 0.8, 'food': 0.45, 'loss': 0.25, 'alone': 0.15, 'land': 0.08}.get(s['scene'])
        if food is not None:
            meter(cv, 'FOOD', food, 150, '#ffb000'); meter(cv, 'WATER', food * 0.9 + 0.05, 230, '#3b8fd6')
        if s['scene'] in SHOW_MAP:
            p0, p1 = SHOW_MAP[s['scene']]; k = clamp((t - a) / (b - a))
            alpha = ease((t - a) / 0.4) * (1 - ease((t - (b - 0.4)) / 0.4)) if s['scene'] != 'depart' else 0.0
            if alpha > 0: map_inset(cv, lerp(p0, p1, k), alpha)
        captions(cv, words, t)
        ff.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
        if fi % 150 == 0: print(f'frame {fi}/{n}', flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2])
