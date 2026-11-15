"""Local 3D preview: render chosen shots of an episode as stills, without voice, compositing or CI.

  blender -b --factory-startup -P engine4/preview3d.py -- episodes/<id> <out_dir> [kind[@k],kind...] [WxH]

Each storyboard shot of the listed kinds (all shots if omitted) is rendered at k (default 0.55 of the shot) using
storyboard weights as stand-in timings. Uses the same kit3d settings as production (KIT3D_* env vars apply).
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy  # noqa: E402
from engine4 import kit3d as K  # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:]
ep_dir, out = os.path.abspath(argv[0]), os.path.abspath(argv[1])
want = [w for w in (argv[2].split(',') if len(argv) > 2 and argv[2] else [])]
w, h = (int(x) for x in (argv[3] if len(argv) > 3 else '360x640').split('x'))
os.makedirs(out, exist_ok=True)

spec = importlib.util.spec_from_file_location('world3d', os.path.join(ep_dir, 'world3d.py'))
Wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Wm)
board = json.load(open(os.path.join(ep_dir, 'storyboard.json')))['shots']
t, spans = 0.0, []
for sh in board:
    d = 1.3 * sh.get('weight', 1.0)
    spans.append((sh, t, t + d))
    t += d

bpy.ops.wm.read_factory_settings(use_empty=True)
K._M.clear()
S = Wm.build()
K.setup()
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = w, h
picks = {}
for x in want:
    kind, _, k = x.partition('@')
    picks.setdefault(kind, []).append(float(k) if k else 0.55)
for sh, a, b in spans:
    if sh['kind'] not in Wm.SHOTS3D or (want and sh['kind'] not in picks):
        continue
    for k in picks.get(sh['kind'], [0.55]):
        tt = a + k * (b - a)
        S['beak'], S['prm'] = 0.6, sh.get('prm', {})
        K._T[0] = tt
        Wm.reset(S)
        Wm.SHOTS3D[sh['kind']](S, k, tt, tt - a)
        Wm.finish(S, tt)
        K.variant(S, S['prm'].get('alt'))
        K.focus(S, S['prm'].get('fstop', K.FSTOP))
        sc.render.filepath = os.path.join(out, f"{sh['n']:02d}_{sh['kind']}_{int(k * 100):02d}.jpg")
        bpy.ops.render.render(write_still=True)
        print("preview", sc.render.filepath, "device", sc.cycles.device, f"{__import__('time').time():.1f}", flush=True)
