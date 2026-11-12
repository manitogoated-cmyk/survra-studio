"""Concept sheets: turnaround, 12 expressions, poses, silhouette + small-icon test, palette. Plus a five-way lineup."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skia
import importlib
from concepts.chars import EX, FX, INK, P
M = importlib.import_module(os.environ.get('CONCEPTS', 'concepts.chars'))
CHARS, INFO, draw = M.CHARS, M.INFO, M.draw
SC = getattr(M, 'SCALES', dict(turn=4.85, pose=2.7, line=5.0, sil=4.6, tag='')) 

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out' + SC['tag'])
BG = 0xFFFBF6EC
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

def text(cv, s, x, y, size, color=INK, w=800, center=False):
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle(w, 5, skia.FontStyle.kUpright_Slant)), size)
    if center: x -= f.measureText(s) / 2
    cv.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Color=color))

def silhouette(cv, name, x, y, s, view='front', pose='stand'):
    FX['glow'] = False
    pa = skia.Paint(); pa.setColorFilter(skia.ColorFilters.Blend(INK, skia.BlendMode.kSrcIn))
    cv.saveLayer(None, pa); draw(name, cv, x, y, s, view, 'happy', pose); cv.restore()
    FX['glow'] = True

def icon(name, size=400):
    surf = skia.Surface(size, size); c = surf.getCanvas(); c.clear(0x00000000)
    clip = skia.Path(); clip.addCircle(size / 2, size / 2, size / 2); c.clipPath(clip, True)
    c.drawPaint(P(INFO[name]['bg']))
    hx, hy, hh = INFO[name]['head']; s = size / (hh * 1.12)
    draw(name, c, size / 2 - hx * s, size / 2 - hy * s + size * 0.04, s, 'front', 'happy')
    return surf.makeImageSnapshot()

def sheet(name):
    W, H = 2400, 1560; info = INFO[name]
    surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(BG)
    cv.drawRect(skia.Rect.MakeWH(W, 112), P(INK))
    text(cv, info['name'], 50, 84, 78, 0xFFFFB000, 900)
    text(cv, info['tag'], 90 + len(info['name']) * 60, 78, 36, 0xFFFFFFFF, 500)
    for i, c in enumerate(info['palette']):
        cv.drawRoundRect(skia.Rect.MakeXYWH(W - 470 + i * 84, 24, 68, 64), 12, 12, P(c))
        cv.drawRoundRect(skia.Rect.MakeXYWH(W - 470 + i * 84, 24, 68, 64), 12, 12, P(0xFFFFFFFF, 3))
    text(cv, 'TURNAROUND', 50, 160, 24, 0xFF8A8296)
    for i, v in enumerate(('front', 'side', 'back')):
        x = 250 + i * 420
        cv.drawOval(skia.Rect.MakeXYWH(x - 120, 716, 240, 26), P(0x1F000000))
        draw(name, cv, x, 730, SC['turn'], v, 'happy' if v != 'side' else 'curious')
        text(cv, v.upper(), x, 780, 24, center=True)
    text(cv, 'SILHOUETTE TEST', 1420, 160, 24, 0xFF8A8296)
    silhouette(cv, name, 1560, 730, SC['sil'])
    silhouette(cv, name, 1800, 730, SC['sil'] / 2, 'side')
    text(cv, 'PROFILE-ICON TEST', 1960, 160, 24, 0xFF8A8296)
    im = icon(name)
    for sz, x, y in ((240, 1960, 190), (96, 2240, 190), (48, 2240, 320), (32, 2240, 392)):
        cv.drawImageRect(im, skia.Rect.MakeXYWH(x, y, sz, sz), SAMP)
        text(cv, f'{sz}px', x + sz + 10 if sz < 200 else x, y + sz / 2 + 8 if sz < 200 else y + sz + 30, 20, 0xFF8A8296, 600)
    # how it looks on a dark YouTube comment row
    cv.drawRoundRect(skia.Rect.MakeXYWH(1960, 500, 400, 86), 14, 14, P(0xFF0F0F0F))
    cv.drawImageRect(im, skia.Rect.MakeXYWH(1976, 519, 48, 48), SAMP)
    text(cv, 'Survra', 2040, 538, 22, 0xFFFFFFFF, 700); text(cv, 'new video in 3, 2, 1...', 2040, 566, 19, 0xFFAAAAAA, 500)
    cv.drawRoundRect(skia.Rect.MakeXYWH(1960, 600, 400, 86), 14, 14, P(0xFFFFFFFF)); cv.drawRoundRect(skia.Rect.MakeXYWH(1960, 600, 400, 86), 14, 14, P(0x22000000, 2))
    cv.drawImageRect(im, skia.Rect.MakeXYWH(1976, 619, 48, 48), SAMP)
    text(cv, 'Survra', 2040, 638, 22, INK, 700); text(cv, 'subscribed', 2040, 666, 19, 0xFF777777, 500)
    text(cv, 'EXPRESSIONS', 50, 846, 24, 0xFF8A8296)
    hx, hy, hh = info['head']; s = 168 / info.get('face', hh)
    for i, e in enumerate(EX):
        x0 = 44 + i * 194
        box = skia.Rect.MakeXYWH(x0, 866, 182, 214)
        cv.drawRoundRect(box, 18, 18, P(0xFFFFFFFF)); cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(box, 18, 18), True)
        draw(name, cv, x0 + 91 - hx * s, 866 + 112 - hy * s, s, 'front', e)
        cv.restore(); cv.drawRoundRect(box, 18, 18, P(0x22000000, 2))
        text(cv, e, x0 + 91, 1108, 22, center=True, w=700)
    text(cv, 'POSES & MOVEMENT', 50, 1176, 24, 0xFF8A8296)
    pe = {'cheer': 'laugh', 'point': 'curious', 'run': 'scared', 'shrug': 'deadpan', 'think': 'thinking', 'rocket': 'awe', 'puddle': 'scared', 'ball': 'scared', 'cross': 'smirk', 'hype': 'laugh'}
    for i, pz in enumerate(info['special']):
        x = 260 + i * 460
        cv.drawOval(skia.Rect.MakeXYWH(x - 90, 1496, 180, 20), P(0x1F000000))
        draw(name, cv, x, 1506, SC['pose'], 'front', pe[pz], pz)
        text(cv, pz, x + 150, 1500, 22, 0xFF8A8296, 700, center=True)
    os.makedirs(OUT, exist_ok=True); p = os.path.join(OUT, f'{name}_sheet.png'); surf.makeImageSnapshot().save(p, skia.kPNG); return p

def lineup():
    W, H = 2400, 1150
    surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(BG)
    text(cv, 'SURVRA HOST: ROUND 2' if SC['tag'] else 'SURVRA HOST: FIVE CONCEPTS', 50, 70, 46, INK, 900)
    for i, n in enumerate(CHARS):
        x = 250 + i * 475
        cv.drawOval(skia.Rect.MakeXYWH(x - 120, 646, 240, 26), P(0x1F000000))
        ex_, pz_ = getattr(M, 'LINEUP', [('happy', 'stand'), ('smirk', 'stand'), ('deadpan', 'stand'), ('awe', 'stand'), ('curious', 'stand')])[i]
        draw(n, cv, x, 660, SC['line'], 'front', ex_, pz_)
        text(cv, INFO[n]['name'], x, 740, 44, INK, 900, center=True)
        text(cv, INFO[n]['tag'], x, 778, 20, 0xFF6A6478, 600, center=True)
        silhouette(cv, n, x - 90, 1090, SC['line'] * 0.48)
        im = icon(n)
        cv.drawImageRect(im, skia.Rect.MakeXYWH(x + 10, 880, 120, 120), SAMP)
        cv.drawImageRect(im, skia.Rect.MakeXYWH(x + 150, 950, 48, 48), SAMP)
        cv.drawImageRect(im, skia.Rect.MakeXYWH(x + 150, 900, 32, 32), SAMP)
    p = os.path.join(OUT, 'lineup.png'); os.makedirs(OUT, exist_ok=True); surf.makeImageSnapshot().save(p, skia.kPNG); return p

if __name__ == '__main__':
    print(lineup())
    for n in (sys.argv[1:] or CHARS): print(sheet(n))
