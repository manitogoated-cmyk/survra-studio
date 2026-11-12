"""Zero To Rescue brand assets: profile picture, banner, watermark, all drawn in code in the channel's art style."""
import math, skia, sys
from common import C, P, lerp, TF_BLACK, TF_BOLD
import rig
import render_short as R
OUT = '/home/claude/studio/brand'
NAVY, INK, AMBER, RED, PAPER, SEA = '#0f2a44', '#0b1320', '#ffb000', '#ff4b3e', '#f4efe6', '#1f6fb2'

def compass(cv, cx, cy, r, ring=True, route=True):
    if ring:
        cv.drawCircle(cx, cy, r, P(C(PAPER), 'stroke', r * 0.06))
        for i in range(32):
            a = i / 32 * 2 * math.pi; L = r * (0.16 if i % 8 == 0 else 0.08)
            cv.drawLine(cx + math.sin(a) * (r - L), cy - math.cos(a) * (r - L), cx + math.sin(a) * r * 0.97, cy - math.cos(a) * r * 0.97, P(C(PAPER), 'stroke', r * 0.022))
    # four-point star
    for i, col in enumerate((AMBER, PAPER, '#c9d3dc', PAPER)):
        a = i * math.pi / 2
        pt = lambda ang, d: (cx + math.sin(ang) * d, cy - math.cos(ang) * d)
        p = skia.Path(); p.moveTo(*pt(a, r * 0.78)); p.lineTo(*pt(a + math.pi / 4, r * 0.16)); p.lineTo(cx, cy); p.close()
        cv.drawPath(p, P(C(col)))
        p2 = skia.Path(); p2.moveTo(*pt(a, r * 0.78)); p2.lineTo(*pt(a - math.pi / 4, r * 0.16)); p2.lineTo(cx, cy); p2.close()
        cv.drawPath(p2, P(C(col), alpha=0.75))
    cv.drawCircle(cx, cy, r * 0.07, P(C(INK)))
    if route:  # dotted drift line ending in a red dot: the castaway's position
        path = skia.Path(); path.moveTo(cx - r * 0.95, cy + r * 0.55); path.cubicTo(cx - r * 0.3, cy + r * 1.05, cx + r * 0.2, cy + r * 0.1, cx + r * 0.62, cy + r * 0.48)
        dash = P(C(AMBER), 'stroke', r * 0.05); dash.setPathEffect(skia.DashPathEffect.Make([r * 0.09, r * 0.07], 0))
        cv.drawPath(path, dash); cv.drawCircle(cx + r * 0.62, cy + r * 0.48, r * 0.075, P(C(RED)))


def zero_mark(cv, cx, cy, r, label=True):
    """Day Zero mark: a thick '0' ring holding a dawn horizon, sea and a lone boat."""
    rx, ry = r * 0.78, r
    oval = skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry)
    clip = skia.Path(); clip.addOval(oval)
    cv.save(); cv.clipPath(clip, skia.ClipOp.kIntersect, True)
    cv.drawRect(oval, skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, cy - ry), (0, cy + ry * 0.2)], [C('#1a3a66'), C('#ff9a55')])))
    cv.drawCircle(cx, cy + ry * 0.18, r * 0.36, P(C('#ffd27a')))
    cv.drawRect(skia.Rect(cx - rx, cy + ry * 0.18, cx + rx, cy + ry), P(C('#123056')))
    for k in range(3):
        y = cy + ry * (0.32 + k * 0.17)
        w = skia.Path(); w.moveTo(cx - rx, y)
        for i in range(13): w.lineTo(cx - rx + i * rx / 6, y + r * 0.03 * math.sin(i * 1.4 + k))
        cv.drawPath(w, P(C('#ffffff'), 'stroke', r * 0.02, alpha=0.35))
    hull = skia.Path(); hull.moveTo(cx - r * 0.22, cy + ry * 0.2); hull.lineTo(cx + r * 0.2, cy + ry * 0.2); hull.lineTo(cx + r * 0.14, cy + ry * 0.29); hull.lineTo(cx - r * 0.16, cy + ry * 0.29); hull.close()
    cv.drawPath(hull, P(C(INK))); cv.drawCircle(cx - r * 0.05, cy + ry * 0.135, r * 0.045, P(C(INK)))
    cv.restore()
    cv.drawOval(oval, P(C(PAPER), 'stroke', r * 0.22))
    cv.drawOval(skia.Rect(cx - rx - r * 0.11, cy - ry - r * 0.11, cx + rx + r * 0.11, cy + ry + r * 0.11), P(C(INK), 'stroke', r * 0.03, alpha=0.6))

def profile():
    s = skia.Surface(800, 800); cv = s.getCanvas()
    cv.drawRect(skia.Rect(0, 0, 800, 800), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, 800)], [C('#123a5e'), C('#07192b')])))
    zero_mark(cv, 400, 400, 285)
    s.makeImageSnapshot().save(f'{OUT}/profile_800.png', skia.kPNG)

def watermark():
    s = skia.Surface(150, 150); cv = s.getCanvas(); cv.clear(skia.Color(0, 0, 0, 0))
    cv.drawCircle(75, 75, 72, P(C(NAVY))); zero_mark(cv, 75, 75, 48)
    s.makeImageSnapshot().save(f'{OUT}/watermark_150.png', skia.kPNG)

def banner(guides=False):
    BW, BH = 2560, 1440
    s = skia.Surface(BW, BH); cv = s.getCanvas()
    cv.drawRect(skia.Rect(0, 0, BW, BH), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, BH)], [C('#07142a'), C('#f08a5d')], [0.35, 0.62])))
    R.stars(cv, 1.0, 0.0)
    r = __import__('random').Random(4)
    for i in range(160): cv.drawCircle(r.uniform(0, BW), r.uniform(0, BH * 0.45), r.uniform(1, 3), P(C('#ffffff'), alpha=r.uniform(0.3, 0.9)))
    cv.drawCircle(BW * 0.66, BH * 0.565, 110, P(C('#ffd27a'), blur=60, alpha=0.6)); cv.drawCircle(BW * 0.66, BH * 0.565, 64, P(C('#ffe4a8')))
    horizon = BH * 0.575
    cols = ['#1d2f55', '#18284a', '#13213f', '#0e1a33']
    for layer in range(4):
        path = skia.Path(); path.moveTo(0, BH)
        for x in range(0, BW + 40, 40): path.lineTo(x, horizon + layer * 70 + 14 * math.sin(x * 0.005 + layer))
        path.lineTo(BW, BH); path.close(); cv.drawPath(path, P(C(cols[layer])))
    # moonlit path + tiny boat with José, left of centre, inside the safe area
    cv.drawRect(skia.Rect(BW * 0.635, horizon, BW * 0.685, BH), P(C('#ffd27a'), blur=40, alpha=0.10))
    bx, by = BW / 2 - 560, horizon + 40; bs = 0.5
    cv.save(); cv.translate(bx, by); cv.rotate(-2); cv.scale(bs, bs); rig.draw_person(cv, -150, -40, 0.9, rig.pose('sit', head=-10), rig.JOSE, 'determined', 1.0); cv.restore()
    R.boat(cv, bx, by, -2, bs, icebox=True)
    # drift route across the banner to the island at right
    path = skia.Path(); path.moveTo(bx + 175, by + 5); path.cubicTo(BW / 2 - 150, horizon + 170, BW / 2 + 300, horizon - 30, BW / 2 + 600, horizon + 20)
    dash = P(C(AMBER), 'stroke', 8); dash.setPathEffect(skia.DashPathEffect.Make([26, 18], 0)); cv.drawPath(path, dash)
    R.island(cv, BW / 2 + 650, horizon + 6, 0.36, 1.0)
    # wordmark + tagline centred in the safe area
    f = skia.Font(TF_BLACK, 132); f2 = skia.Font(TF_BOLD, 40)
    title = 'ZERO TO RESCUE'; tw = f.measureText(title); mark = 165
    x0 = BW / 2 - (tw + mark) / 2; ty = BH / 2 - 60
    zero_mark(cv, x0 + 46, ty - 54, 58)
    cv.drawString(title, x0 + mark, ty, f, P(C('#000000'), 'stroke', 16, alpha=0.5))
    cv.drawString(title, x0 + mark, ty, f, P(C(PAPER)))
    tag = 'EVERY SURVIVAL STORY STARTS ON DAY ZERO.'
    tx = BW / 2 - f2.measureText(tag) / 2
    cv.drawString(tag, tx, ty + 66, f2, P(C('#000000'), 'stroke', 8, alpha=0.5))
    cv.drawString(tag, tx, ty + 66, f2, P(C(AMBER)))
    if guides:
        cv.drawRect(skia.Rect((BW - 1546) / 2, (BH - 423) / 2, (BW + 1546) / 2, (BH + 423) / 2), P(C('#00ff88'), 'stroke', 4))
        cv.drawRect(skia.Rect((BW - 2560) / 2, (BH - 423) / 2, (BW + 2560) / 2, (BH + 423) / 2), P(C('#ff00ff'), 'stroke', 3))
    s.makeImageSnapshot().save(f'{OUT}/banner_2560x1440{"_guides" if guides else ""}.png', skia.kPNG)

profile(); watermark(); banner(); banner(True)
print('ok')
