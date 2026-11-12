"""ROOK model sheet v1: turnaround (front, 3/4, side, back), expressions, beak shapes for lip sync, hat acting, poses, palette."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skia
from concepts.chars import EX, FX, INK, P
from concepts import v2

BG = 0xFFFBF6EC; W, H = 2600, 1900
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
def text(cv, s, x, y, size, color=INK, w=800, center=False):
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(w, 5, skia.FontStyle.kUpright_Slant)), size)
    if center: x -= f.measureText(s) / 2
    cv.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Color=color))
def D(cv, x, y, s, view='front', expr='happy', pose='stand'): v2.draw('rook', cv, x, y, s, view, expr, pose)
def headbox(cv, x0, y0, bw, bh, s, view, expr, label, cy=-95):
    box = skia.Rect.MakeXYWH(x0, y0, bw, bh)
    cv.drawRoundRect(box, 16, 16, P(0xFFFFFFFF)); cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(box, 16, 16), True)
    D(cv, x0 + bw / 2, y0 + bh / 2 - cy * s, s, view, expr); cv.restore(); cv.drawRoundRect(box, 16, 16, P(0x22000000, 2))
    text(cv, label, x0 + bw / 2, y0 + bh + 28, 22, w=700, center=True)

surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(BG)
cv.drawRect(skia.Rect.MakeWH(W, 112), P(INK))
text(cv, 'ROOK', 50, 84, 78, 0xFFFFB000, 900); text(cv, 'Survra host  /  model sheet v1  /  strictly 2D', 330, 78, 34, 0xFFFFFFFF, 500)
pal = [('Feathers', 0xFF2A2742), ('Coat', 0xFF566178), ('Eyes', 0xFFFFB000), ('Hat', 0xFF34303B), ('Band + tie', 0xFFFF7A1A), ('Beak', 0xFF7A8096)]
for i, (n, c) in enumerate(pal):
    x = W - 1010 + i * 165
    cv.drawRoundRect(skia.Rect.MakeXYWH(x, 22, 58, 58), 10, 10, P(c)); cv.drawRoundRect(skia.Rect.MakeXYWH(x, 22, 58, 58), 10, 10, P(0xFFFFFFFF, 3))
    text(cv, n, x + 68, 46, 17, 0xFFFFFFFF, 700); text(cv, '#%06X' % (c & 0xFFFFFF), x + 68, 70, 16, 0xFFB9B4C8, 500)
text(cv, 'TURNAROUND', 50, 160, 24, 0xFF8A8296)
for i, (v, lab) in enumerate((('front', 'FRONT'), ('tq', 'THREE-QUARTER'), ('side', 'SIDE'), ('back', 'BACK'))):
    x = 230 + i * 360
    cv.drawOval(skia.Rect.MakeXYWH(x - 110, 728, 220, 24), P(0x1F000000)); D(cv, x, 740, 4.7, v, 'happy' if v == 'front' else 'curious')
    text(cv, lab, x, 792, 22, center=True)
text(cv, 'SILHOUETTE', 1690, 160, 24, 0xFF8A8296)
FX['glow'] = False; pa = skia.Paint(); pa.setColorFilter(skia.ColorFilters.Blend(INK, skia.BlendMode.kSrcIn))
cv.saveLayer(None, pa); D(cv, 1800, 740, 4.4); D(cv, 2010, 740, 2.6, 'side', 'happy', 'point'); cv.restore(); FX['glow'] = True
text(cv, 'PROFILE ICON', 2200, 160, 24, 0xFF8A8296)
isz = 400; s2 = skia.Surface(isz, isz); c2 = s2.getCanvas(); clip = skia.Path(); clip.addCircle(200, 200, 200); c2.clipPath(clip, True); c2.drawPaint(P(0xFFFF7A1A))
v2.draw('rook', c2, 200, 200 + 96 * 8.4 + 14, 8.4, 'front', 'smirk'); im = s2.makeImageSnapshot()
for sz, x, y in ((250, 2200, 190), (96, 2470, 190), (48, 2470, 310), (32, 2470, 380)): cv.drawImageRect(im, skia.Rect.MakeXYWH(x, y, sz, sz), SAMP)
cv.drawRoundRect(skia.Rect.MakeXYWH(2200, 480, 360, 80), 14, 14, P(0xFF0F0F0F)); cv.drawImageRect(im, skia.Rect.MakeXYWH(2214, 496, 48, 48), SAMP)
text(cv, 'Survra', 2276, 516, 22, 0xFFFFFFFF, 700); text(cv, 'Case closed.', 2276, 544, 19, 0xFFAAAAAA, 500)
text(cv, 'EXPRESSIONS  (the hat brim acts too: drops when unimpressed, jumps when shocked)', 50, 862, 24, 0xFF8A8296)
for i, e in enumerate(EX): headbox(cv, 44 + i * 212, 884, 198, 214, 5.4, 'front', e, e)
text(cv, 'BEAK SHAPES FOR LIP SYNC', 50, 1196, 24, 0xFF8A8296)
for i, (lab, o) in enumerate((('closed  M B P', 0), ('slight  S T N', 1.0), ('mid  E I', 2.0), ('open  A', 3.2), ('wide  shout', 4.6))):
    v2.BEAK_OPEN[0] = o; headbox(cv, 44 + i * 212, 1218, 198, 196, 5.4, 'tq', 'curious', lab, cy=-93)
for i, (lab, o) in enumerate((('side: closed', 0), ('side: open', 3.2))):
    v2.BEAK_OPEN[0] = o; headbox(cv, 44 + (5 + i) * 212, 1218, 198, 196, 5.4, 'side', 'happy', lab, cy=-93)
v2.BEAK_OPEN[0] = None
text(cv, 'POSES & MOVEMENT', 1600, 1196, 24, 0xFF8A8296)
text(cv, 'POSES & MOVEMENT', 50, 1520, 24, 0xFF8A8296)
cv.drawRect(skia.Rect.MakeXYWH(1590, 1170, 420, 40), P(BG))
pe = [('point', 'curious', 'point'), ('run', 'scared', 'run'), ('shrug', 'deadpan', 'shrug'), ('think', 'thinking', 'think'), ('cross', 'smirk', 'arms crossed'), ('hype', 'laugh', 'jump'), ('stand', 'shocked', 'hat pop')]
for i, (pz, e, lab) in enumerate(pe):
    x = 200 + i * 365
    cv.drawOval(skia.Rect.MakeXYWH(x - 80, 1858, 160, 18), P(0x1F000000)); D(cv, x, 1866, 2.75, 'tq' if pz in ('think', 'stand') else 'front', e, pz)
    text(cv, lab, x + 130, 1850, 21, 0xFF8A8296, 700, center=True)
os.makedirs('character', exist_ok=True); surf.makeImageSnapshot().save('character/rook_model_sheet.png', skia.kPNG); print('ok')
