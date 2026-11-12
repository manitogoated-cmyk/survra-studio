"""SURVRA brand (incredible true stories, animated): a distress flare whose smoke trail draws the 'S'. Profile, banner, watermark. All drawn in code."""
import math, random
import skia
from common import C, P, lerp, clamp, TF_BLACK, TF_BOLD
import rig
import render_short as R
OUT = '/home/claude/studio/brand'
INK, CREAM, AMBER, FLARE, EMBER = '#070b14', '#f6efe2', '#ffb000', '#ff3b1f', '#ffd36b'

def grain(cv, w, h, n, seed=1, a=0.06):
    r = random.Random(seed)
    for _ in range(n):
        cv.drawRect(skia.Rect.MakeXYWH(r.uniform(0, w), r.uniform(0, h), 1.6, 1.6), P(C('#ffffff' if r.random() < 0.5 else '#000000'), alpha=a))

def s_path(x, y, s):
    """The flare trail: an S rising from the raft (bottom) to the burning flare (top right)."""
    p = skia.Path()
    p.moveTo(x - 0.10 * s, y + 0.52 * s)
    p.cubicTo(x + 0.55 * s, y + 0.50 * s, x + 0.52 * s, y + 0.08 * s, x + 0.02 * s, y + 0.02 * s)
    p.cubicTo(x - 0.48 * s, y - 0.04 * s, x - 0.44 * s, y - 0.44 * s, x + 0.20 * s, y - 0.46 * s)
    return p

def flare_s(cv, x, y, s, t=0.0, smoke=True):
    path = s_path(x, y, s)
    meas = skia.PathMeasure(path, False); L = meas.getLength()
    # smoke puffs drifting off the trail
    if smoke:
        r = random.Random(3)
        for i in range(70):
            d = L * (i / 70)
            pos, tan = meas.getPosTan(d)
            off = r.uniform(-0.05, 0.05) * s
            cv.drawCircle(pos.x() + off - tan.y() * 0.03 * s, pos.y() + off + tan.x() * 0.03 * s, (0.025 + 0.035 * (1 - i / 70)) * s,
                          P(C('#b9b2aa'), blur=0.02 * s, alpha=0.10 + 0.10 * (1 - i / 70)))
    # glow layers then a hot core, colour shifting from deep red at the base to white-hot at the head
    for w, blur, a in ((0.16, 0.08, 0.35), (0.09, 0.035, 0.6), (0.055, 0.0, 1.0)):
        pnt = P(C(FLARE), 'stroke', w * s, blur=blur * s if blur else 0, alpha=a)
        pnt.setShader(skia.GradientShader.MakeLinear([(x, y + 0.55 * s), (x + 0.2 * s, y - 0.46 * s)],
                                                     [C('#7a0e08'), C(FLARE), C('#ff8a2a'), C(EMBER)], [0.0, 0.45, 0.8, 1.0]))
        cv.drawPath(path, pnt)
    core = P(C('#fff2c9'), 'stroke', 0.016 * s, alpha=0.9); seg = skia.Path(); meas.getSegment(L * 0.55, L, seg, True)
    cv.drawPath(seg, core)
    hx, hy = x + 0.20 * s, y - 0.46 * s
    cv.drawCircle(hx, hy, 0.20 * s, P(C('#ff6a2a'), blur=0.09 * s, alpha=0.55))
    cv.drawCircle(hx, hy, 0.075 * s, P(C(EMBER), blur=0.02 * s))
    cv.drawCircle(hx, hy, 0.035 * s, P(C('#ffffff')))
    r = random.Random(9)
    for i in range(26):  # sparks
        a = r.uniform(0, 2 * math.pi); d = r.uniform(0.06, 0.26) * s
        cv.drawLine(hx + math.cos(a) * d * 0.5, hy + math.sin(a) * d * 0.5, hx + math.cos(a) * d, hy + math.sin(a) * d + 0.02 * s,
                    P(C(EMBER), 'stroke', r.uniform(0.004, 0.009) * s, alpha=r.uniform(0.4, 1)))
    return x - 0.10 * s, y + 0.52 * s  # raft position

def raft(cv, x, y, s, figure=True):
    """Lone survivor on a raft, arm raised with the flare gun."""
    for i in range(5):
        cv.drawRoundRect(skia.Rect(x - 0.13 * s + i * 0.055 * s, y - 0.012 * s, x - 0.08 * s + i * 0.055 * s, y + 0.025 * s), 0.01 * s, 0.01 * s, P(C('#2a1a10')))
    if figure:
        cv.drawCircle(x + 0.01 * s, y - 0.10 * s, 0.022 * s, P(C(INK)))
        body = skia.Path(); body.moveTo(x - 0.03 * s, y - 0.01 * s); body.lineTo(x - 0.012 * s, y - 0.08 * s); body.lineTo(x + 0.03 * s, y - 0.08 * s); body.lineTo(x + 0.04 * s, y - 0.01 * s); body.close()
        cv.drawPath(body, P(C(INK)))
        cv.drawLine(x + 0.025 * s, y - 0.075 * s, x + 0.06 * s, y - 0.14 * s, P(C(INK), 'stroke', 0.012 * s))

def sea(cv, x0, x1, y, s, col='#0b1830', glint='#ff6a2a', seed=4):
    path = skia.Path(); path.moveTo(x0, y + 4 * s)
    for i in range(0, 61):
        xx = lerp(x0, x1, i / 60); path.lineTo(xx, y + math.sin(i * 0.9) * 0.006 * s)
    path.lineTo(x1, y + 3 * s); path.lineTo(x0, y + 3 * s); path.close()
    cv.drawPath(path, P(C(col)))
    r = random.Random(seed)
    for i in range(40):
        xx = r.uniform(x0, x1); yy = y + r.uniform(0.01, 0.25) * s
        cv.drawLine(xx, yy, xx + r.uniform(0.02, 0.07) * s, yy, P(C(glint), 'stroke', 0.004 * s, alpha=r.uniform(0.05, 0.35)))

def stars(cv, w, h, n, seed=2):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h); rr = r.uniform(0.6, 2.4)
        cv.drawCircle(x, y, rr, P(C('#ffffff'), alpha=r.uniform(0.2, 0.9)))

def profile():
    S = 800; surf = skia.Surface(S, S); cv = surf.getCanvas()
    cv.drawRect(skia.Rect(0, 0, S, S), skia.Paint(Shader=skia.GradientShader.MakeRadial((S * 0.62, S * 0.3), S * 0.9, [C('#3a1410'), C('#0d1426'), C(INK)], [0.0, 0.45, 1.0])))
    stars(cv, S, S * 0.7, 120)
    rx, ry = flare_s(cv, S * 0.47, S * 0.43, S * 0.86)
    sea(cv, 0, S, S * 0.84, S, seed=5)
    raft(cv, rx + 8, S * 0.84, S)
    cv.drawCircle(rx + 30, S * 0.86, 120, P(C('#ff4b1f'), blur=50, alpha=0.18))  # flare light on the water
    grain(cv, S, S, 4000)
    surf.makeImageSnapshot().save(f'{OUT}/survra_profile_800.png', skia.kPNG)

def watermark():
    S = 150; surf = skia.Surface(S, S); cv = surf.getCanvas(); cv.clear(skia.Color(0, 0, 0, 0))
    cv.drawCircle(S / 2, S / 2, S / 2 - 2, P(C(INK), alpha=0.85))
    flare_s(cv, S * 0.48, S * 0.50, S * 0.80, smoke=False)
    surf.makeImageSnapshot().save(f'{OUT}/survra_watermark_150.png', skia.kPNG)

def silhouettes(cv, BW, horizon):
    ink = P(C('#05080f'))
    # iceberg (left, storm side)
    ice = skia.Path(); ice.moveTo(BW * 0.24, horizon); ice.lineTo(BW * 0.27, horizon - 120); ice.lineTo(BW * 0.29, horizon - 70); ice.lineTo(BW * 0.31, horizon - 150); ice.lineTo(BW * 0.345, horizon); ice.close()
    cv.drawPath(ice, P(C('#1c2c44')))
    # crashed plane tail
    tail = skia.Path(); tail.moveTo(BW * 0.385, horizon); tail.lineTo(BW * 0.40, horizon - 95); tail.lineTo(BW * 0.415, horizon - 95); tail.lineTo(BW * 0.43, horizon - 30); tail.lineTo(BW * 0.445, horizon); tail.close()
    cv.drawPath(tail, ink)
    # mountain + jungle (right, dawn side)
    mtn = skia.Path(); mtn.moveTo(BW * 0.60, horizon); mtn.lineTo(BW * 0.66, horizon - 200); mtn.lineTo(BW * 0.69, horizon - 150); mtn.lineTo(BW * 0.73, horizon - 230); mtn.lineTo(BW * 0.79, horizon); mtn.close()
    cv.drawPath(mtn, P(C('#2a1e2e')))
    cv.drawPath(mtn, P(C('#ffb36b'), 'stroke', 3, alpha=0.35))
    for i, px in enumerate((0.765, 0.79, 0.815)):
        x = BW * px; h = 160 + i * 30
        trunk = skia.Path(); trunk.moveTo(x, horizon); trunk.quadTo(x + 20, horizon - h / 2, x + 8, horizon - h)
        cv.drawPath(trunk, P(C('#05080f'), 'stroke', 10))
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.55
            tip = (x + 8 + math.cos(a) * 120, horizon - h + 34 + abs(math.cos(a)) * 22)
            leaf = skia.Path(); leaf.moveTo(x + 8, horizon - h); leaf.quadTo(x + 8 + math.cos(a) * 60, horizon - h - 46, *tip)
            leaf.quadTo(x + 8 + math.cos(a) * 55, horizon - h - 18, x + 8, horizon - h); leaf.close()
            cv.drawPath(leaf, P(C('#05080f')))

def banner(guides=False):
    BW, BH = 2560, 1440; surf = skia.Surface(BW, BH); cv = surf.getCanvas()
    # sky: storm (left) -> dawn (right)
    cv.drawRect(skia.Rect(0, 0, BW, BH), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (BW, 0)], [C('#05070d'), C('#0d1630'), C('#3a1c2a'), C('#d8673a')], [0.0, 0.38, 0.62, 1.0])))
    cv.drawRect(skia.Rect(0, 0, BW, BH), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, BH)], [C('#000000', 150), C('#000000', 0), C('#000000', 120)], [0.0, 0.55, 1.0])))
    stars(cv, BW * 0.55, BH * 0.6, 260, 7)
    # storm clouds + lightning on the left
    r = random.Random(12)
    for i in range(40):
        cv.drawCircle(r.uniform(-100, BW * 0.42), r.uniform(BH * 0.18, BH * 0.45), r.uniform(60, 160), P(C('#141b2a'), blur=30, alpha=0.75))
    bolt = skia.Path(); x, y = BW * 0.205, BH * 0.30; bolt.moveTo(x, y)
    for k in range(8): x += r.uniform(-40, 40); y += 34; bolt.lineTo(x, y)
    cv.drawPath(bolt, P(C('#cfe0ff'), 'stroke', 16, blur=14, alpha=0.6)); cv.drawPath(bolt, P(C('#ffffff'), 'stroke', 4))
    # dawn sun on the right
    cv.drawCircle(BW * 0.865, BH * 0.585, 300, P(C('#ffb36b'), blur=130, alpha=0.55)); cv.drawCircle(BW * 0.865, BH * 0.592, 95, P(C('#ffe2a8')))
    horizon = BH * 0.6
    silhouettes(cv, BW, horizon)
    sea(cv, 0, BW, horizon, 900, '#070d1c', '#ff8a4a', 6)
    cv.drawRect(skia.Rect(BW * 0.83, horizon, BW * 0.90, BH), P(C('#ffb36b'), blur=40, alpha=0.14))
    # the mark: flare S fired from a raft, left of the wordmark
    mx, my, ms = BW / 2 - 560, BH / 2 - 30, 330
    rx, ry = flare_s(cv, mx, my, ms)
    raft(cv, rx + 4, horizon + 4, 330)
    for k in range(14):  # flare light trembling on the water below the raft
        cv.drawLine(rx - 60 + k * 9, horizon + 22 + k * 16, rx + 40 - k * 4, horizon + 22 + k * 16, P(C(FLARE), 'stroke', 5, alpha=0.5 * (1 - k / 14)))
    cv.drawCircle(rx, horizon + 40, 140, P(C(FLARE), blur=60, alpha=0.18))
    # wordmark with the S drawn by the flare: 'URVRA' set beside it
    f = skia.Font(TF_BLACK, 210); f.setScaleX(1.0)
    word = 'URVRA'; x0 = mx + 0.25 * ms; ty = BH / 2 + 70
    spacing = 18; xs = [x0]
    for ch in word[:-1]: xs.append(xs[-1] + f.measureText(ch) + spacing)
    for ch, xx in zip(word, xs):
        cv.drawString(ch, xx + 6, ty + 8, f, P(C('#000000'), alpha=0.55))
        fill = P(C(CREAM)); fill.setShader(skia.GradientShader.MakeLinear([(0, ty - 160), (0, ty + 10)], [C('#fffaf0'), C('#f1d9b3')]))
        cv.drawString(ch, xx, ty, f, fill)
    # thin flare streak cutting under the letters
    end_x = xs[-1] + f.measureText(word[-1])
    streak = P(C(FLARE), 'stroke', 5, alpha=0.9); streak.setShader(skia.GradientShader.MakeLinear([(x0, 0), (end_x, 0)], [C(FLARE), C(EMBER, 0)]))
    cv.drawLine(x0, ty + 34, end_x, ty + 34, streak)
    tag = 'INCREDIBLE TRUE STORIES  ·  ANIMATED'
    f2 = skia.Font(TF_BOLD, 42); f2.setScaleX(1.0)
    tx = x0 + 6; cv.drawString(tag, tx, ty + 98, f2, P(C(AMBER)))
    grain(cv, BW, BH, 26000, 3, 0.05)
    # vignette
    cv.drawRect(skia.Rect(0, 0, BW, BH), skia.Paint(Shader=skia.GradientShader.MakeRadial((BW / 2, BH / 2), BW * 0.62, [C('#000000', 0), C('#000000', 170)], [0.55, 1.0])))
    if guides:
        cv.drawRect(skia.Rect((BW - 1546) / 2, (BH - 423) / 2, (BW + 1546) / 2, (BH + 423) / 2), P(C('#00ff88'), 'stroke', 4))
    surf.makeImageSnapshot().save(f'{OUT}/survra_banner_2560x1440{"_guides" if guides else ""}.png', skia.kPNG)

if __name__ == '__main__':
    profile(); watermark(); banner(); banner(True); print('ok')
