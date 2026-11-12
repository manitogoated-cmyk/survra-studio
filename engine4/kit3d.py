"""Survra 3D kit (free: Blender bpy + Cycles on CPU). Faceted low-poly look.
Rig = jointed humanoid (shoulders, elbows, hips, knees, head, jaw). Episodes supply world3d.py with
build(K) -> scene handles and SHOTS3D = {kind: f(S, k, t, lt)}; run() renders the 3D shots of a storyboard on twos."""
import importlib.util
import json
import math
import os
import sys
import time

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
FPS3 = 15
_M = {}


def hexc(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)


def mat(col, rough=0.9, emit=0.0, alpha=1.0):
    key = (col, rough, emit, alpha)
    if key not in _M:
        m = bpy.data.materials.new(col)
        m.use_nodes = True
        b = m.node_tree.nodes.get('Principled BSDF')
        b.inputs['Base Color'].default_value = hexc(col)
        b.inputs['Roughness'].default_value = rough
        if emit:
            b.inputs['Emission Color'].default_value = hexc(col)
            b.inputs['Emission Strength'].default_value = emit
        if alpha < 1:
            b.inputs['Alpha'].default_value = alpha
        _M[key] = m
    return _M[key]


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    o = bpy.context.object
    o.scale = scale
    o.data.materials.append(mat(col, rough, emit, alpha))
    if parent:
        o.parent = parent
    return o


def empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    bpy.ops.object.empty_add(location=loc, rotation=rot)
    o = bpy.context.object
    if parent:
        o.parent = parent
    return o


def light(loc, energy, col, size=2.0, target=None, kind='AREA', spot=0.6, parent=None):
    bpy.ops.object.light_add(type=kind, location=loc)
    l = bpy.context.object
    l.data.energy, l.data.color = energy, hexc(col)[:3]
    if kind == 'AREA':
        l.data.size = size
    if kind == 'SPOT':
        l.data.spot_size, l.data.spot_blend = spot, 0.4
    if target:
        l.constraints.new('TRACK_TO').target = target
    if parent:
        l.parent = parent
    return l


def lerp(a, b, k):
    k = max(0.0, min(1.0, k))
    return a + (b - a) * k


BASE = dict(aL=(0.05, 0.12, 0.15, 0.0), aR=(0.05, 0.12, 0.15, 0.0), lL=(0.0, 0.0), lR=(0.0, 0.0), head=(0.0, 0.0), lean=0.0, lift=0.0)
# arm = (swing forward, spread out, elbow bend, forearm twist inward); leg = (hip forward, knee bend); head = (nod, turn)
POSES = {
    'stand': {},
    'point': dict(aR=(1.45, 0.1, 0.05), head=(0.0, -0.2)),
    'hat':   dict(aR=(2.3, 0.28, 0.4), head=(0.12, 0.0)),
    'cross': dict(aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3)),
    'shrug': dict(aL=(0.3, 0.75, 1.5, -0.9), aR=(0.3, 0.75, 1.5, -0.9), head=(-0.08, 0.0)),
    'up':    dict(aL=(2.8, 0.25, 0.1), aR=(2.8, 0.25, 0.1), head=(-0.3, 0.0)),
    'reach': dict(aR=(2.9, 0.05, 0.05), head=(-0.35, 0.0)),
    'hips':  dict(aL=(-0.25, 0.75, 1.9, 1.5), aR=(-0.25, 0.75, 1.9, 1.5)),
    'sit':   dict(lL=(1.45, 1.6), lR=(1.45, 1.6), aL=(0.7, -0.1, 1.5, 1.0), aR=(0.7, -0.1, 1.5, 1.0), lift=-0.5, lean=0.25, head=(0.3, 0.0)),
    'swim':  dict(aL=(2.9, 0.15, 0.1), aR=(2.6, 0.15, 0.3), head=(-0.9, 0.0)),
}


def _arm(v):
    return tuple(v) + (0.0,) * (4 - len(v))


def P(name='stand', **over):
    d = dict(BASE)
    d.update(POSES[name])
    d.update(over)
    d['aL'], d['aR'] = _arm(d['aL']), _arm(d['aR'])
    return d


def blend(a, b, k):
    k = max(0.0, min(1.0, k))
    k = k * k * (3 - 2 * k)
    out = {}
    for key in BASE:
        va, vb = a[key], b[key]
        out[key] = tuple(x + (y - x) * k for x, y in zip(va, vb)) if isinstance(va, tuple) else va + (vb - va) * k
    return out


def walk(t, speed=1.6, base='stand'):
    s = math.sin(t * speed * 2 * math.pi)
    c = math.cos(t * speed * 2 * math.pi)
    return P(base, lL=(0.55 * s, max(0, -c) * 0.9), lR=(-0.55 * s, max(0, c) * 0.9), aL=(-0.5 * s, 0.12, 0.3), aR=(0.5 * s, 0.12, 0.3), lift=-0.03 * abs(s), lean=0.08)


class Rig:
    def __init__(self, C, head_fn, coat=False):
        self.root = empty()
        self.body = b = empty((0, 0, 1.05), self.root)
        if coat:
            add('cone', C['top'], (0, 0, 0.48), radius1=0.44, radius2=0.3, depth=1.2, vertices=8, parent=b)
            add('cylinder', C['belt'], (0, 0, 0.43), radius=0.385, depth=0.07, vertices=8, parent=b)
            add('cube', 'FFC233', (0, -0.36, 0.43), scale=(0.07, 0.03, 0.06), size=1, parent=b, rough=0.35)
            add('cone', 'FF7A1A', (0, -0.3, 0.83), rot=(math.pi, 0, 0), radius1=0.09, radius2=0.0, depth=0.42, vertices=4, parent=b, rough=0.6)
            for s in (-1, 1):
                add('cube', C['lap'], (s * 0.15, -0.29, 0.86), rot=(0.22, 0, s * 0.5), scale=(0.13, 0.025, 0.34), size=1, parent=b)
                add('cube', C['lap'], (s * 0.2, -0.1, 1.23), rot=(0.1, 0, s * -0.35), scale=(0.16, 0.025, 0.28), size=1, parent=b)
        else:
            add('cone', C['top'], (0, 0, 0.5), radius1=0.3, radius2=0.37, depth=1.0, vertices=8, parent=b)
            add('cylinder', C['pants'], (0, 0, 0.0), radius=0.31, depth=0.16, vertices=8, parent=b)
        add('cube', C['top'], (0, 0, 1.06), scale=(0.74, 0.34, 0.12), size=1, parent=b)
        self.sh, self.el, self.hp, self.kn, self.hands = [], [], [], [], []
        for s in (-1, 1):
            sh = empty((s * 0.47, 0, 1.0), b)
            add('cylinder', C['top'], (0, 0, -0.23), radius=0.085, depth=0.5, vertices=6, parent=sh)
            el = empty((0, 0, -0.46), sh)
            add('cylinder', C.get('fore', C['top']), (0, 0, -0.22), radius=0.08, depth=0.46, vertices=6, parent=el)
            self.hands.append(add('ico_sphere', C['hand'], (0, 0, -0.5), radius=0.11, subdivisions=1, parent=el))
            hp = empty((s * 0.16, 0, 0), b)
            add('cylinder', C['pants'], (0, 0, -0.25), radius=0.095, depth=0.54, vertices=6, parent=hp)
            kn = empty((0, 0, -0.5), hp)
            add('cylinder', C['pants'], (0, 0, -0.24), radius=0.085, depth=0.5, vertices=6, parent=kn)
            add('cube', C['boot'], (0, -0.09, -0.48), scale=(0.2, 0.42, 0.14), size=1, parent=kn)
            self.sh.append(sh); self.el.append(el); self.hp.append(hp); self.kn.append(kn)
        self.head = empty((0, 0, 1.37), b)
        self.extra = head_fn(self.head) or {}
        self.apply(P())

    def apply(self, p):
        for i, s in enumerate((-1, 1)):
            a = _arm(p['aL'] if s < 0 else p['aR'])
            self.sh[i].rotation_euler = (-a[0], -s * a[1], 0)
            self.el[i].rotation_euler = (-a[2], 0, -s * a[3])
            l = p['lL'] if s < 0 else p['lR']
            self.hp[i].rotation_euler = (-l[0], 0, 0)
            self.kn[i].rotation_euler = (l[1], 0, 0)
        self.head.rotation_euler = (p['head'][0], 0, p['head'][1])
        self.body.rotation_euler = (p['lean'], 0, 0)
        self.body.location.z = 1.05 + p['lift']

    def place(self, loc, yaw=0.0, pitch=0.0, roll=0.0):
        self.root.location = loc
        self.root.rotation_euler = (pitch, roll, yaw)


def rook_head(head):
    add('ico_sphere', '2F2B4D', (0, 0, 0), scale=(1, 1, 1.08), radius=0.33, subdivisions=1, parent=head)
    add('cone', '8A90A6', (0, -0.52, -0.06), rot=(math.radians(100), 0, 0), radius1=0.14, radius2=0.0, depth=0.72, vertices=4, parent=head, rough=0.5)
    jaw = empty((0, -0.2, -0.13), head)
    add('cone', '6A7088', (0, -0.3, -0.03), rot=(math.radians(96), 0, 0), radius1=0.1, radius2=0.0, depth=0.56, vertices=4, parent=jaw, rough=0.5)
    eyes, brows = [], []
    for s in (-1, 1):
        eyes.append(add('cube', 'FFB000', (s * 0.14, -0.285, 0.06), rot=(0.2, s * 0.32, s * -0.25), scale=(0.15, 0.03, 0.07), size=1, parent=head, rough=0.4, emit=3.0))
        add('cube', '0E0D14', (s * 0.15, -0.305, 0.055), rot=(0.2, s * 0.32, s * -0.25), scale=(0.045, 0.02, 0.05), size=1, parent=head)
        brows.append(add('cube', '0E0D14', (s * 0.14, -0.29, 0.135), rot=(0.25, s * 0.5, s * -0.25), scale=(0.2, 0.05, 0.04), size=1, parent=head))
        for k in range(3):
            add('cone', '2F2B4D', (s * 0.04 * k, 0.3, -0.12 + k * 0.1), rot=(math.radians(-65), 0, 0), radius1=0.08, radius2=0, depth=0.26, vertices=4, parent=head)
    hat = empty((0, 0, 0.27), head, (-0.2, 0.07, 0))
    add('cylinder', '2B2733', (0, 0, 0), radius=0.66, depth=0.04, vertices=10, parent=hat)
    add('cone', '2B2733', (0, 0, 0.2), radius1=0.34, radius2=0.27, depth=0.38, vertices=8, parent=hat)
    add('cylinder', 'FF7A1A', (0, 0, 0.065), radius=0.35, depth=0.08, vertices=8, parent=hat, rough=0.6)
    # diving helmet: brass collar + cage rings + a hint of glass
    helmet = [add('ico_sphere', 'BFEFFF', (0, -0.05, 0.12), radius=0.86, subdivisions=3, parent=head, rough=0.02, alpha=0.045)]
    bpy.ops.object.shade_smooth()
    helmet.append(add('cylinder', 'C89A3A', (0, 0, -0.42), radius=0.5, depth=0.14, vertices=10, parent=head, rough=0.35))
    for rot in ((math.pi / 2, 0, 0.5), (math.pi / 2, 0, -0.5 + math.pi), (0, 0, 0)):
        helmet.append(add('torus', 'C89A3A', (0, -0.05, 0.12 if rot[0] else -0.2), rot=rot, major_radius=0.87 if rot[0] else 0.8, minor_radius=0.022,
                          major_segments=16, minor_segments=4, parent=head, rough=0.35))
    for o in helmet:
        o.hide_render = True
    return dict(jaw=jaw, hat=hat, eyes=eyes, brows=brows, helmet=helmet)


def human_head(skin='7A4A2E', hair='17131A'):
    def fn(head):
        add('ico_sphere', skin, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
        add('ico_sphere', hair, (0, 0.05, 0.1), scale=(0.95, 1, 1.0), radius=0.3, subdivisions=1, parent=head)
        eyes = []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '0E0D14', (s * 0.105, -0.28, 0.035), scale=(0.04, 0.02, 0.045), size=1, parent=head)
            add('cube', hair, (s * 0.105, -0.27, 0.125), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.025), size=1, parent=head)
        add('cube', '5E3822', (0, -0.285, -0.04), scale=(0.05, 0.05, 0.08), size=1, parent=head)
        jaw = empty((0, -0.2, -0.13), head)
        add('cube', '2A1218', (0, -0.07, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
        return dict(jaw=jaw, eyes=eyes)
    return fn


def diver_head(head):
    add('ico_sphere', 'F2B531', (0, 0, 0.02), radius=0.36, subdivisions=1, parent=head, rough=0.5)
    add('cube', '0B1220', (0, -0.29, 0.03), scale=(0.46, 0.14, 0.26), size=1, parent=head, rough=0.2)
    eyes = [add('cube', 'FFFFFF', (s * 0.1, -0.365, 0.04), scale=(0.09, 0.02, 0.09), size=1, parent=head, emit=1.0) for s in (-1, 1)]
    add('cube', '9AA0B4', (0, -0.2, 0.37), scale=(0.16, 0.2, 0.1), size=1, parent=head)
    aim = empty((0, -6, 0.1), head)
    lamp = light((0, -0.34, 0.37), 9000, 'FFF2C0', kind='SPOT', spot=0.75, target=aim, parent=head)
    cone = add('cone', 'FFF2C0', (0, -3.3, 0.24), rot=(math.radians(-90), 0, 0), radius1=0.8, radius2=0.06, depth=6, vertices=10, parent=head, emit=0.16, alpha=0.06)
    return dict(lamp=lamp, eyes=eyes, cone=cone)


class Hand:
    """Close-up hand prop. Fingers point along local -Y, palm faces -Z. grip(0..1) curls the fingers."""

    def __init__(self, skin, sleeve, s=1.0):
        self.root = r = empty()
        add('cylinder', sleeve, (0, 0.62, 0), rot=(math.pi / 2, 0, 0), radius=0.115, depth=1.0, vertices=6, parent=r)
        add('cylinder', skin, (0, 0.14, 0), rot=(math.pi / 2, 0, 0), radius=0.1, depth=0.12, vertices=6, parent=r)
        add('cube', skin, (0, -0.06, 0), scale=(0.27, 0.3, 0.09), size=1, parent=r)
        self.f = []
        for i in range(4):
            a = empty((-0.105 + i * 0.07, -0.21, 0), r)
            add('cube', skin, (0, -0.07, 0), scale=(0.058, 0.15, 0.065), size=1, parent=a)
            b = empty((0, -0.15, 0), a)
            add('cube', skin, (0, -0.06, 0), scale=(0.054, 0.13, 0.06), size=1, parent=b)
            self.f.append((a, b))
        self.th = empty((0.14, 0.02, -0.01), r, (0, 0, -0.9))
        add('cube', skin, (0, -0.09, 0), scale=(0.065, 0.19, 0.065), size=1, parent=self.th)
        r.scale = (s, s, s)
        self.grip(0.2)

    def grip(self, k):
        for i, (a, b) in enumerate(self.f):
            a.rotation_euler = (k * 1.15 + i * 0.03, 0, (i - 1.5) * 0.06 * (1 - k))
            b.rotation_euler = (k * 1.35, 0, 0)
        self.th.rotation_euler = (k * 0.5, k * 0.9, -0.9 + k * 0.5)

    def place(self, loc, rot=(0, 0, 0)):
        self.root.location, self.root.rotation_euler = loc, rot


def setup(samples=8):
    sc = bpy.context.scene
    try:
        bpy.ops.preferences.addon_enable(module='cycles')
    except Exception:
        pass
    sc.render.engine = 'CYCLES'
    sc.cycles.samples, sc.cycles.device = samples, 'CPU'
    sc.cycles.max_bounces = 3
    sc.cycles.transparent_max_bounces = 6
    sc.cycles.use_denoising = True
    sc.render.use_persistent_data = True
    sc.render.threads_mode = 'AUTO'
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 92
    sc.view_settings.view_transform = 'Standard'


def run(ep_dir, mode='all', w=432, h=768, samples=8, part=None):
    """mode: all | sheet (one low-res still per shot) | stills. part=(i, n) renders every n-th frame (parallel jobs)."""
    from engine3 import render3 as R3
    from engine3.voice3 import LipSync
    from engine3.host import VIS
    import numpy as np
    import soundfile as sf
    spec = importlib.util.spec_from_file_location('world3d', os.path.join(ep_dir, 'world3d.py'))
    Wm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Wm)
    build = os.path.join(ep_dir, 'build')
    tl = json.load(open(os.path.join(build, 'timeline.json')))
    board = json.load(open(os.path.join(ep_dir, 'storyboard.json')))
    ep = json.load(open(os.path.join(ep_dir, 'episode.json')))
    if ep.get('format', 'short') == 'long':
        w, h = h, w
    shots = R3.edl(tl, board)[0]
    audio, sr = sf.read(os.path.join(build, 'voice.wav'))
    lips = LipSync(tl, audio.astype(np.float32), sr)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _M.clear()
    S = Wm.build()
    setup(samples if mode == 'all' else 4)
    sc = bpy.context.scene
    out = os.path.join(build, '3d' if mode != 'sheet' else '3d_sheet')
    os.makedirs(out, exist_ok=True)
    sc.render.resolution_x, sc.render.resolution_y = (w, h) if mode != 'sheet' else (w // 2, h // 2)
    json.dump(dict(fps=FPS3, kinds=sorted(Wm.SHOTS3D), host=sorted(Wm.HOST)), open(os.path.join(out, 'manifest.json'), 'w'))
    t0 = time.time()
    for name, fn in getattr(Wm, 'STILLS', {}).items():
        path = os.path.join(out, f'still_{name}.jpg')
        if mode == 'sheet' or os.path.exists(path):
            continue
        S['beak'], S['prm'] = 0.0, {}
        Wm.reset(S)
        fn(S, 0.5, 1.0, 0.5)
        Wm.finish(S, 1.0)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    if mode == 'stills':
        return
    todo = []
    for sh in shots:
        if sh['kind'] not in Wm.SHOTS3D:
            continue
        if mode == 'all':
            i0, i1 = int(math.floor(sh['a'] * FPS3)), int(math.ceil(sh['b'] * FPS3))
            todo += [(i, sh) for i in range(i0, i1)]
        else:
            todo.append((int((sh['a'] + 0.55 * (sh['b'] - sh['a'])) * FPS3), sh))
    if part:
        todo = todo[part[0]::part[1]]
    done = 0
    for i, sh in todo:
        path = os.path.join(out, f"{sh['n']:02d}_{i:05d}.jpg" if mode == 'all' else f"{sh['n']:02d}_{sh['kind']}.jpg")
        if mode == 'all' and os.path.exists(path):
            continue
        t = max(sh['a'], min(sh['b'] - 1e-3, i / FPS3))
        lt, d = t - sh['a'], sh['b'] - sh['a']
        vis, ko = lips.at(t)
        S['beak'] = VIS.get(vis, 1.5) * min(1.2, ko)
        S['prm'] = sh.get('prm', {})
        Wm.reset(S)
        Wm.SHOTS3D[sh['kind']](S, max(0.0, min(1.0, lt / d)), t, lt)
        Wm.finish(S, t)
        sc.render.filepath = path + '.tmp.jpg'
        bpy.ops.render.render(write_still=True)
        os.replace(path + '.tmp.jpg', path)
        done += 1
        if done % 20 == 0 or done <= 3:
            el = time.time() - t0
            print(f'3d {done}/{len(todo)} {el / done:.1f}s/frame eta {(len(todo) - done) * el / done / 60:.1f} min', flush=True)
    print('3d done', done, 'frames', round(time.time() - t0), 's', flush=True)


if __name__ == '__main__':
    a = sys.argv
    run(a[1], a[2] if len(a) > 2 else 'all', part=(int(a[3]), int(a[4])) if len(a) > 4 else None)
