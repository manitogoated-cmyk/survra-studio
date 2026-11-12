"""Contact sheet: one still per shot (at 55% of each shot) for visual review."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skia
from engine3.render3 import render
ep = sys.argv[1]; out = sys.argv[2]
board = json.load(open(os.path.join(ep, 'storyboard.json')))
import engine3.render3 as R
tl = json.load(open(os.path.join(ep, 'build', 'timeline.json')))
shots = R.edl(tl, board)[0]
times = [s['a'] + 0.55 * (s['b'] - s['a']) for s in shots]
stills, _ = render(ep, None, only=times)
cols = 6; tw = 270; th = int(tw * stills[0][1].height() / stills[0][1].width())
rows = (len(stills) + cols - 1) // cols
surf = skia.Surface(cols * tw, rows * (th + 30)); cv = surf.getCanvas(); cv.clear(0xFF202020)
f = skia.Font(skia.Typeface('Inter'), 18)
for i, ((t, img), sh) in enumerate(zip(stills, shots)):
    x, y = (i % cols) * tw, (i // cols) * (th + 30)
    cv.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw, th), skia.SamplingOptions(skia.FilterMode.kLinear))
    cv.drawString(f"{sh['n']} {sh['kind']}", x + 6, y + th + 22, f, skia.Paint(Color=0xFFFFFFFF))
surf.makeImageSnapshot().save(out, skia.kPNG); print('sheet', out)
