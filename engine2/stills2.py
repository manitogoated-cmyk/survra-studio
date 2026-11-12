import json, sys, os, skia
from PIL import Image
import render
tl = json.load(open(sys.argv[1] + '/timeline.json')); board = json.load(open(sys.argv[2]))
shots, *_ = render.edl(tl, board)
ts = [sh['a'] + (sh['b'] - sh['a']) * float(sys.argv[4] if len(sys.argv) > 4 else 0.6) for sh in shots]
stills, _ = render.render(sys.argv[1], sys.argv[2], None, only=ts)
ims = []
for t, img in stills:
    img.save('/tmp/s.png', skia.kPNG); ims.append(Image.open('/tmp/s.png').convert('RGB').resize((180, 320)))
cols = 8; rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (180 * cols, 320 * rows))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 180, (i // cols) * 320))
sheet.save(sys.argv[3]); print(len(ims))
