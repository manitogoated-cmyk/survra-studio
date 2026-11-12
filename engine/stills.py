import json, os, sys, skia
sys.path.insert(0, os.path.dirname(__file__))
import render_short as R
tl = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
segs = tl['segments']; words = [w for s in segs for w in s['words']]
surf = skia.Surface(R.W, R.H); cv = surf.getCanvas()
for i, s in enumerate(segs):
    d = (segs[i+1]['start'] if i+1 < len(segs) else tl['duration']) - s['start']
    t = d * (0.25 if s['scene']=='loss' else 0.6)
    cv.clear(R.C('#000000')); R.SCENES[s['scene']](cv, t, d)
    if s['scene'] != 'end': R.day_counter(cv, s['day'])
    if s['scene'] in ('alone','land'): R.map_inset(cv, 0.6 if s['scene']=='alone' else 0.97, 1.0)
    R.meter(cv, 'FOOD', 0.4, 150, '#ffb000'); R.meter(cv, 'WATER', 0.5, 230, '#3b8fd6')
    R.captions(cv, words, s['start'] + 0.8)
    surf.makeImageSnapshot().save(f"{out}/{i}_{s['scene']}.png", skia.kPNG)
print('ok')
