"""Contact sheet of the low-res 3D stills (build/3d_sheet) for a quick composition check."""
import glob, os, sys
import skia
d = os.path.join(sys.argv[1], 'build', '3d_sheet'); out = sys.argv[2]
part = sys.argv[3] if len(sys.argv) > 3 else None
fs = sorted(glob.glob(os.path.join(d, '[0-9]*.jpg')))
if part:
    a, b = map(int, part.split('-')); fs = fs[a:b]
im0 = skia.Image.open(fs[0]); wide = im0.width() > im0.height()
cols = 5 if wide else 6; tw = 384 if wide else 300; th = int(tw * im0.height() / im0.width())
rows = (len(fs) + cols - 1) // cols
surf = skia.Surface(cols * tw, rows * (th + 26)); cv = surf.getCanvas(); cv.clear(0xFF202020)
f = skia.Font(skia.Typeface('Inter'), 17)
for i, p in enumerate(fs):
    img = skia.Image.open(p); x, y = (i % cols) * tw, (i // cols) * (th + 26)
    cv.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw - 4, th), skia.SamplingOptions(skia.FilterMode.kLinear))
    cv.drawString(os.path.basename(p)[:-4], x + 6, y + th + 19, f, skia.Paint(Color=0xFFFFFFFF))
surf.makeImageSnapshot().save(out, skia.kPNG)
