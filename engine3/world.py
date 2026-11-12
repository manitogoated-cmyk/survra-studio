"""World-building toolkit. Building blocks only - every episode composes its own world in
episodes/<id>/scenes.py with its own palette, layout, props and cast. Nothing here is a finished scene.
"""
import math
import random

import skia

from engine3.kesta import INK, P, circle, lerp, oval, poly, seg


def hexc(h, a=255):
    h = h.lstrip('#')
    return (a << 24) | int(h, 16)


def mix(c1, c2, k):
    k = max(0.0, min(1.0, k))
    out = 0
    for sh in (24, 16, 8, 0):
        out |= int(lerp((c1 >> sh) & 255, (c2 >> sh) & 255, k)) << sh
    return out


def alpha(c, a):
    return (int(255 * max(0, min(1, a))) << 24) | (c & 0xFFFFFF)


def fill(cv, x0, y0, x1, y1, c):
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), P(c))


def vgrad(cv, x0, y0, x1, y1, stops):
    """stops: [(pos 0-1, color)]"""
    pts = [skia.Point(0, y0), skia.Point(0, y1)]
    sh = skia.GradientShader.MakeLinear(pts, [c for _, c in stops], [p for p, _ in stops])
    pa = skia.Paint(Shader=sh)
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), pa)


def glow(cv, x, y, r, c, a=1.0, blur=None):
    pa = skia.Paint(AntiAlias=True, Color=c)
    pa.setAlphaf(a)
    pa.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur or r * 0.6))
    cv.drawCircle(x, y, r, pa)


def radial(cv, x, y, r, c_in, c_out):
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [c_in, c_out])
    cv.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh))


class Rand:
    def __init__(self, seed):
        self.r = random.Random(seed)

    def __call__(self, a=0.0, b=1.0):
        return self.r.uniform(a, b)

    def pick(self, xs):
        return self.r.choice(xs)


def ridge(cv, W, H, y, amp, c, seed, rough=6, ink=None, ow=3.0, x_off=0.0):
    """Silhouette band (hills, canopy line, dunes, skyline-noise)."""
    R = Rand(seed)
    ph = [R(0, 6.28) for _ in range(rough)]
    fr = [R(0.6, 1.4) * (k + 1) for k in range(rough)]
    path = skia.Path()
    path.moveTo(-10, H + 10)
    for i in range(0, 61):
        x = -10 + (W + 20) * i / 60
        v = sum(math.sin((x + x_off) / W * fr[k] * 6.28 + ph[k]) / (k + 1) for k in range(rough))
        path.lineTo(x, y - amp * (0.5 + 0.35 * v))
    path.lineTo(W + 10, H + 10)
    path.close()
    cv.drawPath(path, P(c))
    if ink:
        cv.drawPath(path, P(ink, ow))


def cloud(cv, x, y, s, c, shade=None, ink=None):
    blobs = [(-1.0, 0.1, 0.55), (-0.45, -0.25, 0.7), (0.25, -0.35, 0.8), (0.9, 0.0, 0.6), (0.2, 0.15, 0.7), (-0.5, 0.2, 0.55)]
    if shade:
        for bx, by, r in blobs:
            cv.drawCircle(x + bx * s, y + by * s + s * 0.12, r * s, P(shade))
    for bx, by, r in blobs:
        cv.drawCircle(x + bx * s, y + by * s, r * s, P(c))
    if ink:
        for bx, by, r in blobs:
            cv.drawCircle(x + bx * s, y + by * s, r * s, P(ink, 3))


def rain(cv, W, H, t, density=140, c=0x88CFE6FF, slant=0.25, speed=1800, seed=3, length=46):
    R = Rand(seed)
    pa = P(c, 3)
    for i in range(density):
        x0, y0, v = R(0, W * 1.3), R(0, H), R(0.7, 1.3)
        y = (y0 + t * speed * v) % (H + 100) - 50
        x = (x0 - (y * slant)) % (W * 1.2) - W * 0.1
        cv.drawLine(x, y, x - length * slant, y - length, pa)


def bolt(cv, x, y0, y1, seed, c=0xFFFFFFFF, width=7, branches=2):
    R = Rand(seed)
    pts = [(x, y0)]
    yy = y0
    while yy < y1:
        yy += R(40, 90)
        pts.append((pts[-1][0] + R(-60, 60), min(yy, y1)))
    for w, col, a in ((width * 5, 0xFFB8D8FF, 0.35), (width, c, 1.0)):
        path = skia.Path()
        path.moveTo(*pts[0])
        for q in pts[1:]:
            path.lineTo(*q)
        pa = P(col, w)
        pa.setAlphaf(a)
        if w > width:
            pa.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        cv.drawPath(path, pa)
    for b in range(branches):
        i = int(R(1, max(2, len(pts) - 1)))
        bx, by = pts[i]
        path = skia.Path()
        path.moveTo(bx, by)
        for k in range(3):
            bx += R(-70, 70)
            by += R(30, 70)
            path.lineTo(bx, by)
        cv.drawPath(path, P(c, width * 0.45))


def particles(cv, W, H, t, n, c, seed, size=(2, 5), drift=(0, -40), wobble=20, twinkle=False):
    R = Rand(seed)
    for i in range(n):
        x0, y0, s, ph = R(0, W), R(0, H), R(*size), R(0, 6.28)
        x = (x0 + drift[0] * t + math.sin(t * 1.3 + ph) * wobble) % W
        y = (y0 + drift[1] * t + math.cos(t * 1.1 + ph) * wobble) % H
        a = 0.5 + 0.5 * math.sin(t * 3 + ph) if twinkle else 1.0
        pa = P(c)
        pa.setAlphaf(((c >> 24) & 255) / 255 * a)
        cv.drawCircle(x, y, s, pa)


def mist(cv, W, y, h, c, t, seed=1, speed=20):
    R = Rand(seed)
    for i in range(6):
        x = (R(0, W) + t * speed * R(0.5, 1.5)) % (W + 600) - 300
        oval(cv, x, y + R(-h, h) * 0.3, R(220, 420), h * R(0.3, 0.6), c, ink=None)


def leaf(cv, x, y, L, ang, c, vein=None, ink=INK, ow=2.6):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    path = skia.Path()
    path.moveTo(0, 0)
    path.quadTo(L * 0.5, -L * 0.28, L, 0)
    path.quadTo(L * 0.5, L * 0.28, 0, 0)
    cv.drawPath(path, P(c))
    if vein:
        cv.drawLine(0, 0, L * 0.9, 0, P(vein, 2))
    if ink:
        cv.drawPath(path, P(ink, ow))
    cv.restore()


def fern(cv, x, y, s, ang, c, t=0.0, sway=3.0, vein=None, ink=INK):
    """Big tropical frond: a curved stem with leaflets."""
    a0 = ang + math.sin(t * 1.4 + x * 0.01) * sway
    px, py = x, y
    for i in range(9):
        k = i / 8
        a = math.radians(a0 + k * 40)
        nx, ny = px + math.cos(a) * s * 0.12, py + math.sin(a) * s * 0.12
        cv.drawLine(px, py, nx, ny, P(ink if ink else c, 4))
        L = s * 0.32 * (1 - k * 0.6)
        leaf(cv, nx, ny, L, math.degrees(a) - 65, c, vein, ink, 2.0)
        leaf(cv, nx, ny, L, math.degrees(a) + 65, c, vein, ink, 2.0)
        px, py = nx, ny


def tree_jungle(cv, x, ground, h, trunk, canopy, canopy_sh, t=0.0, seed=1, ink=INK, buttress=True):
    R = Rand(seed)
    w = h * 0.07
    path = skia.Path()
    path.moveTo(x - w * (2.4 if buttress else 1.1), ground)
    path.quadTo(x - w * 0.8, ground - h * 0.12, x - w * 0.7, ground - h * 0.4)
    path.lineTo(x - w * 0.5, ground - h * 0.92)
    path.lineTo(x + w * 0.5, ground - h * 0.92)
    path.lineTo(x + w * 0.7, ground - h * 0.4)
    path.quadTo(x + w * 0.8, ground - h * 0.12, x + w * (2.4 if buttress else 1.1), ground)
    path.close()
    cv.drawPath(path, P(trunk))
    if ink:
        cv.drawPath(path, P(ink, 3))
    sway = math.sin(t * 0.8 + seed) * h * 0.006
    for i in range(7):
        bx = x + R(-h * 0.32, h * 0.32) + sway
        by = ground - h * R(0.85, 1.05)
        r = h * R(0.13, 0.2)
        cv.drawCircle(bx, by + r * 0.15, r, P(canopy_sh))
        cv.drawCircle(bx, by, r, P(canopy))
        if ink:
            cv.drawCircle(bx, by, r, P(ink, 3))


def vine(cv, x, y0, y1, c, t, seed=1, ink=INK, leaves=True):
    R = Rand(seed)
    path = skia.Path()
    path.moveTo(x, y0)
    sw = math.sin(t * 1.1 + seed) * 12
    path.cubicTo(x + 30 + sw, lerp(y0, y1, 0.33), x - 30 + sw, lerp(y0, y1, 0.66), x + sw * 1.4, y1)
    cv.drawPath(path, P(ink, 7))
    cv.drawPath(path, P(c, 4))
    if leaves:
        for i in range(6):
            k = (i + 1) / 7
            leaf(cv, x + sw * k * 1.2 + R(-10, 10), lerp(y0, y1, k), 26, R(-40, 220), c, None, ink, 2)


def river(cv, W, y_top, y_bot, c_deep, c_light, t, flow=1.0, seed=2, perspective=True):
    vgrad(cv, 0, y_top, W, y_bot, [(0, c_light), (1, c_deep)])
    R = Rand(seed)
    for i in range(46):
        k = R(0, 1)
        yy = lerp(y_top, y_bot, k ** (1.6 if perspective else 1))
        L = lerp(30, 160, k)
        x = (R(0, W + 400) + t * flow * lerp(40, 240, k)) % (W + 400) - 200
        pa = P(alpha(0xFFFFFFFF, 0.25 + 0.3 * k), lerp(2, 5, k))
        cv.drawLine(x, yy, x + L, yy, pa)


def rock(cv, x, y, s, c, shade, ink=INK, seed=1):
    R = Rand(seed)
    pts = [(x + math.cos(a) * s * R(0.7, 1.0), y + math.sin(a) * s * R(0.45, 0.6)) for a in [i * math.pi / 5 + math.pi for i in range(6)]]
    pts += [(x + s, y), (x - s, y)]
    pts = sorted(pts, key=lambda q: math.atan2(q[1] - y, q[0] - x))
    poly(cv, pts, c, ink, 3)
    oval(cv, x - s * 0.2, y - s * 0.15, s * 0.4, s * 0.18, shade, ink=None)


def hut(cv, x, ground, s, wall, roof, roof_sh, ink=INK, door=0xFF2A1A10, stilts=True):
    y = ground - (s * 0.28 if stilts else 0)
    if stilts:
        for dx in (-0.42, -0.1, 0.22, 0.45):
            seg(cv, (x + dx * s, y), (x + dx * s, ground), s * 0.035, 0xFF6B4A2B, ink, 3)
    poly(cv, [(x - s * 0.5, y), (x + s * 0.5, y), (x + s * 0.5, y - s * 0.38), (x - s * 0.5, y - s * 0.38)], wall, ink, 3)
    for i in range(1, 6):
        xx = x - s * 0.5 + i * s / 6
        cv.drawLine(xx, y, xx, y - s * 0.38, P(mix(wall, 0xFF000000, 0.25), 3))
    poly(cv, [(x - s * 0.1, y), (x + s * 0.1, y), (x + s * 0.1, y - s * 0.27), (x - s * 0.1, y - s * 0.27)], door, ink, 3)
    poly(cv, [(x - s * 0.66, y - s * 0.34), (x, y - s * 0.78), (x + s * 0.66, y - s * 0.34)], roof, ink, 3.5)
    for i in range(9):
        k = i / 8
        cv.drawLine(lerp(x - s * 0.6, x + s * 0.6, k), y - s * 0.36, x + (k - 0.5) * s * 0.15, y - s * 0.74, P(roof_sh, 3))


def canoe(cv, x, y, s, hull, inner, ink=INK, ang=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    path = skia.Path()
    path.moveTo(-s, -s * 0.06)
    path.quadTo(0, s * 0.3, s, -s * 0.1)
    path.lineTo(s * 0.9, -s * 0.02)
    path.quadTo(0, s * 0.1, -s * 0.9, 0)
    path.close()
    cv.drawPath(path, P(hull))
    cv.drawPath(path, P(ink, 3.5))
    oval(cv, 0, -s * 0.02, s * 0.8, s * 0.05, inner, ink=None)
    cv.restore()


def airliner(cv, x, y, s, body, trim, window, ink=INK, ang=0.0, props_t=0.0, parts=None, breakup=0.0):
    """Generic four-turboprop airliner, side view, facing right. breakup 0..1 splits it apart."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    gap = breakup * s * 0.25

    def front():
        path = skia.Path()
        path.moveTo(-s * 0.1, -s * 0.07)
        path.lineTo(s * 0.42, -s * 0.07)
        path.quadTo(s * 0.55, -s * 0.06, s * 0.56, 0)
        path.quadTo(s * 0.52, s * 0.06, s * 0.4, s * 0.07)
        path.lineTo(-s * 0.1, s * 0.07)
        path.close()
        cv.drawPath(path, P(body))
        cv.drawRect(skia.Rect.MakeLTRB(-s * 0.1, -s * 0.005, s * 0.5, s * 0.015), P(trim))
        for i in range(8):
            cv.drawCircle(-s * 0.05 + i * s * 0.055, -s * 0.03, s * 0.012, P(window))
        poly(cv, [(s * 0.47, -s * 0.05), (s * 0.53, -s * 0.03), (s * 0.47, -s * 0.03)], window, ink, 2)
        cv.drawPath(path, P(ink, 3.5))
        # wing + engines
        poly(cv, [(s * 0.05, s * 0.02), (s * 0.22, s * 0.02), (s * 0.02, s * 0.2), (-s * 0.08, s * 0.2)], trim, ink, 3)
        for ex in (s * 0.12, s * 0.02):
            oval(cv, ex, s * 0.06, s * 0.05, s * 0.02, body, ink, 2.5)
            blur = abs(math.sin(props_t * 40))
            cv.drawLine(ex + s * 0.055, s * 0.06 - s * 0.05 * blur, ex + s * 0.055, s * 0.06 + s * 0.05 * blur, P(ink, 3))

    def back():
        path = skia.Path()
        path.moveTo(-s * 0.1, -s * 0.07)
        path.lineTo(-s * 0.4, -s * 0.05)
        path.lineTo(-s * 0.5, -s * 0.03)
        path.lineTo(-s * 0.5, s * 0.02)
        path.lineTo(-s * 0.1, s * 0.07)
        path.close()
        cv.drawPath(path, P(body))
        cv.drawRect(skia.Rect.MakeLTRB(-s * 0.48, -s * 0.005, -s * 0.1, s * 0.015), P(trim))
        for i in range(5):
            cv.drawCircle(-s * 0.36 + i * s * 0.055, -s * 0.03, s * 0.012, P(window))
        cv.drawPath(path, P(ink, 3.5))
        poly(cv, [(-s * 0.38, -s * 0.05), (-s * 0.5, -s * 0.2), (-s * 0.54, -s * 0.2), (-s * 0.5, -s * 0.03)], trim, ink, 3)
        poly(cv, [(-s * 0.42, 0), (-s * 0.56, s * 0.03), (-s * 0.5, s * 0.05)], trim, ink, 2.5)

    cv.save()
    cv.translate(-gap, gap * 0.4)
    cv.rotate(-breakup * 25)
    back()
    cv.restore()
    cv.save()
    cv.translate(gap, -gap * 0.2)
    cv.rotate(breakup * 18)
    front()
    cv.restore()
    cv.restore()


def text_card(cv, s, x, y, size, color=0xFFFFFFFF, stroke=0xFF000000, center=True, weight=900):
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)
    w = f.measureText(s)
    if center:
        x -= w / 2
    blob = skia.TextBlob(s, f)
    if stroke:
        cv.drawTextBlob(blob, x, y, P(stroke, size * 0.16))
    cv.drawTextBlob(blob, x, y, P(color))
    return w


def journal_page(cv, x, y, w, h, t_in, paper=0xFFF3E6C8, ink=0xFF3A2A1A, title=None):
    """Kesta's journal: all maps / numbers pop out as hand-drawn pages. Returns content rect."""
    k = min(1.0, t_in / 0.25)
    sc = 0.6 + 0.4 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(x + w / 2, y + h / 2)
    cv.rotate(-3 + 3 * k)
    cv.scale(sc, sc)
    cv.translate(-w / 2, -h / 2)
    shadow = P(0x55000000)
    cv.drawRoundRect(skia.Rect.MakeXYWH(10, 14, w, h), 18, 18, shadow)
    cv.drawRoundRect(skia.Rect.MakeXYWH(0, 0, w, h), 18, 18, P(paper))
    for i in range(1, int(h / 46)):
        cv.drawLine(30, i * 46, w - 30, i * 46, P(alpha(ink, 0.12), 2))
    cv.drawRoundRect(skia.Rect.MakeXYWH(0, 0, w, h), 18, 18, P(INK, 5))
    if title:
        text_card(cv, title, w / 2, 70, 54, ink, None)
    cv.restore()
    return k
