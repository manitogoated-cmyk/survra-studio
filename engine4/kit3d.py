"""Survra 3D kit (free: Blender bpy + Cycles on CPU). Faceted low-poly look.
Rig = jointed humanoid (shoulders, elbows, hips, knees, head, jaw). Episodes supply world3d.py with
build(K) -> scene handles and SHOTS3D = {kind: f(S, k, t, lt)}; run() renders every frame of the 3D shots.

Quality upgrade (2026-11-15, Animation Quality Director review of Case 001):
  * true 60 fps: every frame is rendered (was 15 fps held on twos, then doubled to 30)
  * 720x1280 render (was 432x768, a 2.5x upscale that made every frame soft), adaptive sampling + OpenImageDenoise
    with albedo/normal passes, AgX colour management (no more blown-out whites), depth of field on the look-at target
  * bevelled edges and subtle surface variation on every primitive, so the faceted style reads as designed models
  * mitten hands with a thumb instead of a ball, idle breathing on every rig, pose blends with anticipation/overshoot
Overrides per run: KIT3D_FPS, KIT3D_RES (e.g. 720x1280), KIT3D_SAMPLES, KIT3D_FSTOP, KIT3D_DEVICE (CPU | GPU for local previews)."""
import importlib.util
import json
import math
import os
import sys
import time

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
FPS3 = int(os.environ.get('KIT3D_FPS', 60))
RES = tuple(int(x) for x in os.environ.get('KIT3D_RES', '720x1280').split('x'))
SAMPLES = int(os.environ.get('KIT3D_SAMPLES', 20))
FSTOP = float(os.environ.get('KIT3D_FSTOP', 4.0))
_T = [0.0]              # current render time, so rigs add idle motion without every episode passing it in
LONG_LENS = 0.72        # 16:9 episodes: widen every shot's lens so portrait-style staging still fits
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
        if not emit and alpha >= 1:
            _grain(m, b, col, rough)
        _M[key] = m
    return _M[key]


def _grain(m, b, col, rough):
    """Soft large-scale value variation and rougher patches: flat single-colour plastic made every set look unfinished."""
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 3.5
    nz.inputs['Detail'].default_value = 3.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    vr = nt.nodes.new('ShaderNodeMapRange')
    vr.inputs['To Min'].default_value, vr.inputs['To Max'].default_value = 0.86, 1.06
    nt.links.new(nz.outputs['Fac'], vr.inputs['Value'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type, mix.blend_type = 'RGBA', 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    mix.inputs['A'].default_value = hexc(col)
    nt.links.new(vr.outputs['Result'], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    rr = nt.nodes.new('ShaderNodeMapRange')
    rr.inputs['To Min'].default_value, rr.inputs['To Max'].default_value = max(0.05, rough - 0.15), min(1.0, rough + 0.05)
    nt.links.new(nz.outputs['Fac'], rr.inputs['Value'])
    nt.links.new(rr.outputs['Result'], b.inputs['Roughness'])


def _bevel(o, scale):
    """Thin bevel on hard edges so highlights catch the silhouette. Width is in local units, so divide by the scale."""
    big = max(abs(v) for v in scale) or 1.0
    md = o.modifiers.new('bevel', 'BEVEL')
    md.width = min(0.12, 0.022 / big)
    md.segments = 2
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(35)


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    o = bpy.context.object
    o.scale = scale
    o.data.materials.append(mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        _bevel(o, scale)
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
    'hat':   dict(aR=(0.2, 1.9, 1.6, -1.5), head=(0.12, 0.0)),      # elbow out, fingers at the brim
    'cross': dict(aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3)),
    'shrug': dict(aL=(0.3, 0.75, 1.5, -0.9), aR=(0.3, 0.75, 1.5, -0.9), head=(-0.08, 0.0)),
    'up':    dict(aL=(2.8, 0.25, 0.1), aR=(2.8, 0.25, 0.1), head=(-0.3, 0.0)),
    'reach': dict(aR=(2.9, 0.05, 0.05), head=(-0.35, 0.0)),
    'hips':  dict(aL=(-0.25, 0.75, 1.9, 1.5), aR=(-0.25, 0.75, 1.9, 1.5)),
    'sit':   dict(lL=(1.45, 1.6), lR=(1.45, 1.6), aL=(0.7, -0.1, 1.5, 1.0), aR=(0.7, -0.1, 1.5, 1.0), lift=-0.5, lean=0.25, head=(0.3, 0.0)),
    'swim':  dict(aL=(2.9, 0.15, 0.1), aR=(2.6, 0.15, 0.3), head=(-0.9, 0.0)),
    # signature mannerisms from character/ROOK.md and acting poses found missing in the Case 001 review
    'tap':    dict(aR=(1.25, -0.25, 2.2, 0.6), aL=(0.45, -0.05, 1.7, 1.3), head=(0.18, -0.12)),   # taps his beak, thinking
    'think':  dict(aR=(0.9, -0.1, 2.3, 0.9), aL=(0.5, -0.05, 1.75, 1.3), head=(0.1, 0.25)),     # hand at chin, other arm across
    'brace':  dict(aL=(0.6, 0.85, 0.6), aR=(0.9, 0.7, 0.9), lL=(0.35, 0.55), lR=(-0.25, 0.35), lift=-0.12, lean=0.18, head=(0.25, 0.0)),
    'wash':   dict(aL=(1.1, -0.15, 1.7, 0.4), aR=(1.1, -0.15, 1.7, -0.4), lean=0.32, lL=(0.15, 0.1), lR=(0.15, 0.1), head=(0.45, 0.0)),
    'scream': dict(aL=(0.6, 1.1, 1.9, -0.6), aR=(0.6, 1.1, 1.9, -0.6), lean=-0.18, head=(-0.25, 0.0)),
}


def _arm(v):
    return tuple(v) + (0.0,) * (4 - len(v))


def P(name='stand', **over):
    d = dict(BASE)
    d.update(POSES[name])
    d.update(over)
    d['aL'], d['aR'] = _arm(d['aL']), _arm(d['aR'])
    return d


def act(k, c=0.9):
    """Ease-in-out-back: a small counter-move before the action and a settle past the target after it.
    Smoothstep made every gesture glide like a puppet on a rail."""
    k = max(0.0, min(1.0, k))
    c2 = c * 1.525
    if k < 0.5:
        return ((2 * k) ** 2 * ((c2 + 1) * 2 * k - c2)) / 2
    return ((2 * k - 2) ** 2 * ((c2 + 1) * (k * 2 - 2) + c2) + 2) / 2


def blend(a, b, k):
    k = act(k)
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
        self.phase = (len(bpy.data.objects) * 0.618) % (2 * math.pi)
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
            hnd = add('cube', C['hand'], (0, -0.01, -0.52), scale=(0.15, 0.09, 0.17), size=1, parent=el)
            add('cube', C['hand'], (s * -0.6, -0.4, 0.15), rot=(0, s * 0.5, 0), scale=(0.35, 0.6, 0.45), size=1, parent=hnd)
            self.hands.append(hnd)
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
        t, ph = _T[0], self.phase
        br = math.sin(t * 2 * math.pi / 3.4 + ph)                 # breathing, about 18 breaths a minute
        sw = math.sin(t * 0.9 + ph * 2)
        for i in range(2):
            r = self.sh[i].rotation_euler
            self.sh[i].rotation_euler = (r[0] - 0.025 * br, r[1], r[2])
        self.head.rotation_euler = (p['head'][0] + 0.02 * br, 0.025 * sw, p['head'][1] + 0.03 * math.sin(t * 0.7 + ph))
        self.body.rotation_euler = (p['lean'] + 0.012 * sw, 0.01 * math.sin(t * 0.6 + ph), 0)
        self.body.location.z = 1.05 + p['lift'] + 0.008 * br
        self.body.scale = (1 + 0.006 * br, 1 + 0.01 * br, 1)

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
        eyes.append(add('cube', 'FFB000', (s * 0.14, -0.285, 0.06), rot=(0.2, s * 0.32, s * -0.25), scale=(0.15, 0.03, 0.07), size=1, parent=head, rough=0.4, emit=5.0))
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
        eyes, brows = [], []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '0E0D14', (s * 0.105, -0.28, 0.035), scale=(0.04, 0.02, 0.045), size=1, parent=head)
            brows.append(add('cube', hair, (s * 0.105, -0.27, 0.125), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.025), size=1, parent=head))
        add('cube', '5E3822', (0, -0.285, -0.04), scale=(0.05, 0.05, 0.08), size=1, parent=head)
        jaw = empty((0, -0.255, -0.115), head)
        mouth = add('cube', '2A1218', (0, -0.012, -0.02), scale=(0.13, 0.03, 0.035), size=1, parent=jaw)
        return dict(jaw=jaw, eyes=eyes, brows=brows, mouth=mouth)
    return fn


def diver_head(head):
    add('ico_sphere', 'F2B531', (0, 0, 0.02), radius=0.36, subdivisions=1, parent=head, rough=0.5)
    add('cube', '0B1220', (0, -0.29, 0.03), scale=(0.46, 0.14, 0.26), size=1, parent=head, rough=0.2)
    eyes = [add('cube', 'FFFFFF', (s * 0.1, -0.365, 0.07), scale=(0.09, 0.02, 0.08), size=1, parent=head, emit=1.0) for s in (-1, 1)]
    mouth = add('cube', 'FF5A4A', (0, -0.372, -0.05), scale=(0.12, 0.02, 0.03), size=1, parent=head, emit=0.8)   # visor display mouth
    add('cube', '9AA0B4', (0, -0.2, 0.37), scale=(0.16, 0.2, 0.1), size=1, parent=head)
    aim = empty((0, -6, 0.1), head)
    lamp = light((0, -0.34, 0.37), 9000, 'FFF2C0', kind='SPOT', spot=0.75, target=aim, parent=head)
    cone = add('cone', 'FFF2C0', (0, -3.3, 0.24), rot=(math.radians(-90), 0, 0), radius1=0.8, radius2=0.06, depth=6, vertices=10, parent=head, emit=0.16, alpha=0.06)
    return dict(lamp=lamp, eyes=eyes, cone=cone, mouth=mouth)


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


def setup(samples=SAMPLES):
    sc = bpy.context.scene
    try:
        bpy.ops.preferences.addon_enable(module='cycles')
    except Exception:
        pass
    sc.render.engine = 'CYCLES'
    sc.cycles.samples, sc.cycles.device = samples, 'CPU'
    if os.environ.get('KIT3D_DEVICE') == 'GPU':           # local previews only; production renders on CPU runners
        try:
            pr = bpy.context.preferences.addons['cycles'].preferences
            for kind in ('OPTIX', 'CUDA'):
                try:
                    pr.compute_device_type = kind
                    pr.get_devices()
                    for d in pr.devices:
                        d.use = True
                    sc.cycles.device = 'GPU'
                    break
                except Exception:
                    continue
        except Exception:
            pass
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = float(os.environ.get('KIT3D_NOISE', 0.05))
    sc.cycles.adaptive_min_samples = 6
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces, sc.cycles.glossy_bounces = 3, 2
    sc.cycles.transparent_max_bounces = 6
    sc.cycles.use_denoising = True
    for k, v in (('denoiser', 'OPENIMAGEDENOISE'), ('denoising_input_passes', 'RGB_ALBEDO_NORMAL'), ('denoising_prefilter', os.environ.get('KIT3D_PREFILTER', 'FAST'))):
        try:
            setattr(sc.cycles, k, v)
        except Exception:
            pass
    sc.render.filter_size = 1.2
    sc.render.use_persistent_data = True
    sc.render.threads_mode = 'AUTO'
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 95
    try:                                   # AgX keeps highlights from clipping to flat white (Standard blew out lamps and flashes)
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Punchy'
    except Exception:
        sc.view_settings.view_transform = 'Filmic'
        sc.view_settings.look = 'Medium High Contrast'


def focus(S, fstop):
    """Depth of field on the shot's look-at point: separates the subject from the set (prm "fstop": 0 turns it off)."""
    cam = bpy.context.scene.camera
    if cam is None or 'camtgt' not in S:
        return
    cam.data.dof.use_dof = bool(fstop)
    if fstop:
        cam.data.dof.focus_object = S['camtgt']
        cam.data.dof.aperture_fstop = fstop * max(0.6, cam.data.lens / 50)   # long lenses already compress depth


def variant(S, alt):
    """prm "alt": [yaw_degrees, distance_multiplier, height_add, lens_multiplier] re-frames a shot around its own
    look-at point, so a shot type can be reused from a clearly different angle (needs S['camrig'] and S['camtgt'])."""
    if not alt or 'camrig' not in S or 'camtgt' not in S:
        return
    yaw, mul, dz, lm = (list(alt) + [0, 1, 0, 1][len(alt):])[:4]
    c, tg = S['camrig'].location, S['camtgt'].location
    dx, dy = c[0] - tg[0], c[1] - tg[1]
    a = math.radians(yaw)
    S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * mul, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * mul, c[2] + dz)
    bpy.context.scene.camera.data.lens *= lm


CAMLIFE = float(os.environ.get('KIT3D_CAMLIFE', 1.0))


def camlife(S, t, amount=1.0):
    """Handheld drift: the camera position floats by about 0.6 % of its distance to the subject on slow, unrelated
    sine waves, so no shot is ever perfectly frozen. prm "still": true switches it off (graphics, locked comedy beats)."""
    if 'camrig' not in S or 'camtgt' not in S or amount <= 0:
        return
    c, tg = S['camrig'].location, S['camtgt'].location
    d = math.sqrt(sum((c[i] - tg[i]) ** 2 for i in range(3))) * 0.006 * amount
    S['camrig'].location = (c[0] + d * (math.sin(t * 0.83) + 0.4 * math.sin(t * 2.1 + 1.3)),
                            c[1] + d * 0.5 * math.sin(t * 0.61 + 2.0),
                            c[2] + d * (math.sin(t * 1.07 + 0.7) + 0.3 * math.sin(t * 2.6)))


CAMFILL0 = float(os.environ.get('KIT3D_CAMFILL', 60))


def camfill_setup(S):
    """A soft fill that rides with the camera, the way a film crew puts a bounce or eye-light beside the lens: whatever
    the camera looks at gets some light on the side facing us, so faces never read as eyes in a black blob."""
    cf = light((0, 0, 0), 0, 'FFE6CC', size=2.5)
    cf.parent = bpy.context.scene.camera
    cf.location, cf.rotation_euler = (0.6, 0.5, 0.2), (0, 0, 0)     # camera space: beside and above the lens, aimed along the view
    S['camfill'] = cf
    return cf


def camfill(S, Wm, kind):
    """Per-shot level: world3d may define CAMFILL = {kind: watts, '*': default}. A shot can still override it."""
    table = getattr(Wm, 'CAMFILL', {})
    S['camfill'].data.energy = table.get(kind, table.get('*', CAMFILL0))


def run(ep_dir, mode='all', w=RES[0], h=RES[1], samples=SAMPLES, part=None):
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
    long_ = ep.get('format', 'short') == 'long'
    if long_:
        w, h = h, w
    shots = R3.edl(tl, board)[0]
    audio, sr = sf.read(os.path.join(build, 'voice.wav'))
    lips = LipSync(tl, audio.astype(np.float32), sr)
    print('3d scene: building', flush=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _M.clear()
    S = Wm.build()
    camfill_setup(S)
    setup(samples if mode == 'all' else 4)
    print('3d scene: built, rendering with', bpy.context.scene.render.engine, 'threads', bpy.context.scene.render.threads, flush=True)
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
        _T[0] = 0.5
        Wm.reset(S)
        fn(S, 0.5, 1.0, 0.5)
        Wm.finish(S, 1.0)
        sc.render.filepath = path
        keep = (sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples)
        if name == 'thumb':                      # the long-form thumbnail picture: 1280x720, clean
            sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = 1280, 720, 32
        elif long_:
            sc.camera.data.lens *= LONG_LENS
        bpy.ops.render.render(write_still=True)
        sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = keep
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
    if os.environ.get('KIT3D_SHOTS'):            # local spot checks: only these shot numbers
        want = {int(x) for x in os.environ['KIT3D_SHOTS'].split(',')}
        todo = [(i, sh) for i, sh in todo if sh['n'] in want]
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
        _T[0] = t
        Wm.reset(S)
        camfill(S, Wm, sh['kind'])
        Wm.SHOTS3D[sh['kind']](S, max(0.0, min(1.0, lt / d)), t, lt)
        Wm.finish(S, t)
        variant(S, S['prm'].get('alt'))
        camlife(S, t, 0 if S['prm'].get('still') else CAMLIFE)
        focus(S, S['prm'].get('fstop', FSTOP))
        if long_:
            sc.camera.data.lens *= LONG_LENS
        sc.render.filepath = path + '.tmp.jpg'
        bpy.ops.render.render(write_still=True)
        os.replace(path + '.tmp.jpg', path)
        done += 1
        if done % 20 == 0 or done <= 3:
            el = time.time() - t0
            print(f'3d {done}/{len(todo)} {el / done:.1f}s/frame eta {(len(todo) - done) * el / done / 60:.1f} min', flush=True)
    print('3d done', done, 'frames', round(time.time() - t0), 's', flush=True)


if __name__ == '__main__':
    import faulthandler
    faulthandler.dump_traceback_later(900, repeat=True)      # a stuck render shows where it is stuck
    a = sys.argv
    run(a[1], a[2] if len(a) > 2 else 'all', part=(int(a[3]), int(a[4])) if len(a) > 4 else None)
