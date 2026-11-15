"""Build every episode's 3D world and pose every shot once, without rendering: a quick check that a change to the
kit or the finish pass has not broken an existing episode. Usage: smoke3d.py [episode id ...]"""
import importlib.util
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def one(ep):
    sys.path.insert(0, ROOT)
    import bpy
    from engine4 import kit3d as K
    spec = importlib.util.spec_from_file_location('world3d', os.path.join(ROOT, 'episodes', ep, 'world3d.py'))
    Wm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Wm)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    K._M.clear()
    t0 = time.time()
    S = Wm.build()
    K.setup(4)
    n = K.finalize(S)
    bad = []
    for name, fn in list(Wm.SHOTS3D.items()) + list(getattr(Wm, 'STILLS', {}).items()):
        for k in (0.0, 0.5, 1.0):
            try:
                S['beak'], S['prm'] = 0.8, {}
                Wm.reset(S)
                fn(S, k, 10.0 + k * 2, k * 2)
                Wm.finish(S, 10.0 + k * 2)
                K.frame(S)
            except Exception as e:
                bad.append(f'{name}@{k}: {type(e).__name__}: {e}')
                break
    bpy.context.view_layer.update()
    print(f'{ep}: {len(bpy.data.objects)} objects, {len(Wm.SHOTS3D)} shots, polished {n}, {time.time() - t0:.0f}s, {len(bad)} failing', flush=True)
    for b in bad:
        print('   ', b, flush=True)
    return 1 if bad else 0


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--one':
        sys.exit(one(sys.argv[2]))
    eps = sys.argv[1:] or sorted(d for d in os.listdir(os.path.join(ROOT, 'episodes')) if os.path.exists(os.path.join(ROOT, 'episodes', d, 'world3d.py')))
    rc = 0
    for ep in eps:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), '--one', ep], capture_output=True, text=True)
        out = [ln for ln in r.stdout.splitlines() if ln.startswith(ep) or ln.startswith('    ')]
        print('\n'.join(out) if out else f'{ep}: CRASHED\n' + r.stderr[-1500:], flush=True)
        rc |= 1 if (r.returncode or not out) else 0
    sys.exit(rc)
