"""Kesta reference sheet: generated from the production rig, so it can never drift from what renders."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skia
from engine3.kesta import draw_kesta, pose, EXPR, VISEMES, COL, INK

W, H = 3000, 2000
def text(cv, s, x, y, size, color=0xFF14121A, bold=True, center=False):
    f = skia.Font(skia.Typeface('Inter', skia.FontStyle.Bold() if bold else skia.FontStyle.Normal()), size)
    if center:
        x -= f.measureText(s) / 2
    cv.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Color=color))

def sheet(out, only=None):
    surf = skia.Surface(W, H); cv = surf.getCanvas(); cv.clear(0xFFF6F1E7)
    cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, 130), skia.Paint(Color=0xFF0B1020))
    text(cv, 'KESTA', 60, 92, 76, 0xFFFFB000)
    text(cv, 'Survra host  /  character reference sheet v1  /  rig: engine3/kesta.py', 330, 88, 34, 0xFFE8ECF4, bold=False)
    # turnaround-ish: facing right, facing left, walking, crouch
    text(cv, 'MAIN POSES', 60, 175, 26)
    poses = [('stand', 'neutral', 1), ('talk_a', 'happy', 1), ('point', 'curious', 1), ('stand', 'neutral', -1),
             ('journal', 'smirk', 1), ('flare_fire', 'determined', 1), ('inspect', 'curious', 1), ('gasp', 'shocked', 1),
             ('shrug', 'skeptical', 1), ('fist_pump', 'excited', 1)]
    for i, (pn, ex, fc) in enumerate(poses):
        x = 170 + i * 285; y = 920
        cv.drawOval(skia.Rect.MakeXYWH(x - 80, y - 8, 160, 18), skia.Paint(AntiAlias=True, Color=0x22000000))
        draw_kesta(cv, x, y, 600, pose(pn), 0.4, facing=fc, expr=ex, viseme='rest', blink=0,
                   goggles='down' if pn == 'flare_fire' else 'up', prop_glow=1 if pn == 'flare_fire' else 0)
        text(cv, pn.replace('_', ' '), x, 960, 24, center=True)
    # expressions: head close-ups
    text(cv, 'EXPRESSIONS', 60, 1060, 30)
    exs = list(EXPR)
    for i, ex in enumerate(exs):
        col, row = i % 8, i // 8
        x, y = 180 + col * 330, 1460 + row * 0
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(x - 150, 1080 + row * 440, 300, 380))
        draw_kesta(cv, x - 4*9, 1080 + row * 440 + 200 + 88*9, 900, pose('stand'), 0.3, expr=ex, blink=0,
                   goggles='down' if ex in ('determined',) else 'up', viseme='AI' if ex in ('shocked', 'excited', 'scared') else 'rest')
        cv.restore()
        text(cv, ex, x, 1080 + row * 440 + 410, 24, center=True)
    surf.makeImageSnapshot().save(out, skia.kPNG)

def visemes(out):
    surf = skia.Surface(2400, 520); cv = surf.getCanvas(); cv.clear(0xFFF6F1E7)
    text(cv, 'LIP-SYNC MOUTH SHAPES (driven by voice-model phoneme timings)', 40, 60, 30)
    for i, v in enumerate(VISEMES):
        x = 130 + i * 228
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(x - 110, 80, 220, 380))
        draw_kesta(cv, x - 4*8, 270 + 88*8, 800, pose('stand'), 0.3, expr='neutral', viseme=v, blink=0)
        cv.restore()
        text(cv, v, x, 495, 26, center=True)
    surf.makeImageSnapshot().save(out, skia.kPNG)

if __name__ == '__main__':
    os.makedirs('character', exist_ok=True)
    sheet('character/kesta_reference_sheet.png'); visemes('character/kesta_visemes.png')
    print('ok')
