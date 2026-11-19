"""Case 040 in 3D - the Emu War, Campion district, Western Australia, November to December 1932.
About 20,000 emus came into the wheatbelt after breeding season and raided the crops. Farmers, many of them former
soldiers, asked the Minister of Defence for machine guns. Major G. P. W. Meredith of the Royal Australian Artillery
went out with two soldiers, two Lewis guns and 10,000 rounds. On 4 November an ambush at a dam on about a thousand
emus ended when the gun jammed; a gun mounted on a truck could not keep up and the ride was too rough to shoot.
After bad press the troops were withdrawn on 8 November; at the farmers' request they returned on 13 November and
were recalled for good about four weeks later. Meredith claimed 986 birds for 9,860 rounds: exactly ten a bird.
Later requests for the army were refused; farmers relied on bounties and fences.

Built for this story only: a wheatbelt paddock under a big sky (farm dam and spoil bank, wheat, a fence line with a
gap, a dirt track, an iron-roofed homestead, windmills, gum trees), a 1930s army truck with a post-mounted gun, the
inside of an army bell tent at night, and a new wire fence at sunset. The emus are a new low-poly bird rig.

Comedy stays on the absurd parts: no bird is ever shown hit, hurt or dead; guns fire only at nothing in frame. The
uniforms carry no badges or insignia, the truck no markings, the newspaper no headline; nobody's likeness is
attempted."""
import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -6000)
FIELD = (0.0, 0.0, 0.0)             # the paddock, the dam, the track, the homestead
TENT = (5000.0, 0.0, 0.0)           # inside the bell tent
FEN = (0.0, 5000.0, 0.0)            # the new fence at the far end of a paddock
DAM = (0.0, 40.0)
GUN = (6.0, 21.0)                   # the spoil bank where the gun is hidden
TRACK = -12.0                       # the dirt track runs along x at this y
GATE = (-70.0, -8.0)
CAMP = (-30.0, -25.0)
HOST = {'rook_jam', 'rook_truck', 'rook_paper', 'pack_up', 'emu_tank', 'farmers_ask', 'round_two', 'recalled', 'rook_tens',
        'rook_squint', 'fence_build', 'fence_face', 'rook_question'}
CAMFILL = {'*': 90, 'dam_mob': 40, 'wheat_raid': 0, 'truck_chase': 30, 'weeks_sun': 0, 'gun_hide': 70, 'press_drop': 150,
           'rook_paper': 200, 'major_report': 160, 'ledger': 90, 'casings': 110, 'rook_tens': 190, 'rook_squint': 170,
           'pack_up': 320, 'fence_face': 160, 'rook_question': 200, 'round_two': 80, 'recalled': 130}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
KHAKI, KHAKI2, DRAB = 'A8915E', '8E7A4E', '5C6142'
WHEAT, WHEAD, EARTH, RED = 'B8963E', 'E2BE5E', 'A8744A', '9A5A36'
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    day=('E6EEF2', '3A78C8', 1.1, 3.6, 'FFF4E0', (0.45, -0.6, 0.75)),
    morning=('F4D8B0', '5A8ACC', 1.0, 3.0, 'FFE2B8', (0.8, -0.35, 0.35)),
    evening=('F6B878', '4A6AA8', 1.0, 2.6, 'FFB878', (-0.85, -0.4, 0.28)),
    dusk=('F08A58', '2A3868', 0.85, 1.7, 'FF9A60', (-0.9, -0.3, 0.13)),
    dawn=('F2C098', '6A86B8', 0.95, 2.4, 'FFD0A0', (0.85, 0.25, 0.22)),
    night=('1A2238', '060A14', 0.3, 0.12, '9AB0E0', (0.3, 0.4, 0.85)),
    tent=('2A1E14', '0E0A06', 0.2, 0.0, 'FFFFFF', (0, 0, 1)))
_KEEP = []


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rnd(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def keep(o):
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def at(o, x, y, z):
    return (o[0] + x, o[1] + y, o[2] + z)


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def box(par, col, x0, x1, y0, y1, z0, z1, **kw):
    return fadd('cube', col, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), scale=(x1 - x0, y1 - y0, z1 - z0), size=1, parent=par, **kw)


def bar(par, col, a, b, w, **kw):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = fadd('cylinder', col, tuple((a + b) / 2), radius=0.5, depth=1, vertices=6, parent=par, **kw)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w, w, max(0.01, d.length))
    return o


# ---------------------------------------------------------------- fast primitives (no bpy.ops: thousands of objects stay quick to build)
_MESH = {}


def _prim(kind, kw):
    key = (kind,) + tuple(sorted(kw.items()))
    if key in _MESH:
        return _MESH[key]
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'cylinder':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius', 1.0), radius2=kw.get('radius', 1.0), depth=kw.get('depth', 2.0))
    elif kind == 'cone':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius1', 1.0), radius2=kw.get('radius2', 0.0), depth=kw.get('depth', 2.0))
    elif kind == 'ico_sphere':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('subdivisions', 2), radius=kw.get('radius', 1.0))
    elif kind == 'plane':
        h = kw.get('size', 2.0) / 2
        vs = [bm.verts.new(v) for v in ((-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0))]
        bm.faces.new(vs)
    me = bpy.data.meshes.new(kind)
    bm.to_mesh(me)
    bm.free()
    _MESH[key] = me
    return me


def fempty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new('e', None)
    bpy.context.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    return o


def fadd(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, bevel=True, **kw):
    """Same as kit3d.add, built through bpy.data with shared meshes (the material sits on the object)."""
    if kind == 'torus':
        return add(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
    me = _prim(kind, kw)
    if not me.materials:
        me.materials.append(K.mat(col, rough, emit, alpha))
    o = bpy.data.objects.new(kind, me)
    bpy.context.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    o.material_slots[0].link = 'OBJECT'
    o.material_slots[0].material = K.mat(col, rough, emit, alpha)
    if bevel and kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    if parent:
        o.parent = parent
    return o


def np_boxes(name, col, cen, size, rotm, loc=(0, 0, 0), parent=None, rough=0.9, octa=False):
    """N boxes (or elongated octahedra, octa=True) from arrays: cen (N,3), size (N,3), rotm (N,3,3). One object."""
    import numpy as np
    if octa:
        unit = np.array([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)], float) * 0.5
        fc = np.array([(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)])
    else:
        unit = np.array([(x, y, z) for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5)], float)
        fc = np.array([(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)])
    n, nv = len(cen), len(unit)
    v = np.einsum('nij,nkj->nki', rotm, unit[None, :, :] * size[:, None, :]) + cen[:, None, :]
    f = (fc[None, :, :] + (np.arange(n) * nv)[:, None, None]).reshape(-1, fc.shape[1])
    me = bpy.data.meshes.new(name)
    me.from_pydata(v.reshape(-1, 3).tolist(), [], f.tolist())
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(K.mat(col, rough))
    o.location = loc
    if parent:
        o.parent = parent
    return o


def rotms(rx, ry, rz):
    """Rotation matrices (N,3,3) for XYZ Euler angle arrays, same convention as Blender."""
    import numpy as np
    cx, sx, cy, sy, cz, sz = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    o, z = np.ones_like(rx), np.zeros_like(rx)
    X = np.stack([o, z, z, z, cx, -sx, z, sx, cx], -1).reshape(-1, 3, 3)
    Y = np.stack([cy, z, sy, z, o, z, -sy, z, cy], -1).reshape(-1, 3, 3)
    Z = np.stack([cz, -sz, z, sz, cz, z, z, z, o], -1).reshape(-1, 3, 3)
    return Z @ Y @ X


# ---------------------------------------------------------------- one mesh made of many boxes (wheat, wire, tallies)
def boxes_mesh(name, col, items, loc=(0, 0, 0), parent=None, rough=0.9, emit=0.0):
    """items: (centre, (sx, sy, sz), (rx, ry, rz)) in object space. One object, so thousands of stalks stay cheap."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for c, s, r in items:
        m = Matrix.Translation(Vector(c)) @ Euler(r).to_matrix().to_4x4() @ Matrix.Diagonal((s[0], s[1], s[2], 1.0))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(K.mat(col, rough, emit))
    o.location = loc
    if parent:
        o.parent = parent
    return o


def seg_items(pts, w):
    """Thin boxes between point pairs (wires, rails)."""
    out = []
    for a, b in pts:
        a, b = Vector(a), Vector(b)
        d = b - a
        out.append((tuple((a + b) / 2), (w, w, d.length), tuple(d.to_track_quat('Z', 'Y').to_euler())))
    return out


def wheat(S, par, x0, x1, y0, y1, dens, seed, keepout=(), h=1.5, sway=False):
    """A patch of wheat as two meshes (thin stalks, pointed ears), origin at the patch centre so it can sway as one."""
    import numpy as np
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    n = int((x1 - x0) * (y1 - y0) * dens)
    if n <= 0:
        return
    rng = np.random.default_rng(seed)
    x = rng.uniform(x0, x1, n)
    y = rng.uniform(y0, y1, n)
    ok = np.ones(n, bool)
    for a, b, r in keepout:
        ok &= (x - a) ** 2 + (y - b) ** 2 >= r * r
    x, y = x[ok], y[ok]
    n = len(x)
    if not n:
        return
    hh = h * rng.uniform(0.78, 1.22, n)
    rx, ry, rz = rng.uniform(-0.08, 0.08, n), rng.uniform(-0.08, 0.08, n), rng.uniform(0, 6.28, n)
    R = rotms(rx, ry, rz)
    base = np.stack([x - cx, y - cy, np.zeros(n)], -1)
    up = R[:, :, 2]
    st = np_boxes('stalks', WHEAT, base + up * (hh / 2)[:, None], np.stack([np.full(n, 0.024), np.full(n, 0.024), hh], -1), R, at(par['o'], cx, cy, 0), rough=0.95)
    R2 = rotms(rx * 2.2, ry * 2.2, rz)
    np_boxes('ears', WHEAD, base + up * hh[:, None] + R2[:, :, 2] * 0.15, np.tile([0.075, 0.075, 0.34], (n, 1)), R2, (0, 0, 0), parent=st, rough=0.9, octa=True)
    if sway:
        S['sway'].append((st, (seed * 0.618) % 6.28))
    return st


# ---------------------------------------------------------------- the emu
class Emu:
    """Low-poly emu, about as tall as a man. Feet at the root, facing -Y. Legs bend the bird way (the 'knee' is the
    ankle, so the shin angles backwards); shaggy cones hang off the body; blue-grey skin on the upper neck."""

    def __init__(self, i):
        self.root = fempty(FAR)
        self.body = b = fempty((0, 0, 1.68), self.root)
        col = ('5A4A3A', '4E4034', '62503E', '544638')[i % 4]
        dk = ('42362A', '3A3026', '4A3C2E', '3E3428')[i % 4]
        fadd('ico_sphere', col, (0, 0.05, 0.02), scale=(0.62, 1.0, 0.72), radius=0.7, subdivisions=1, parent=b, rough=1.0, bevel=False)
        for j in range(11):                                          # shaggy feathers hanging off the body
            a = 2 * PI * j / 11
            fadd('cone', dk if j % 2 else col, (0.36 * math.cos(a), 0.62 * math.sin(a) + 0.08, -0.22), rot=(PI + 0.35 * math.sin(a), -0.35 * math.cos(a), 0),
                radius1=0.16, radius2=0.0, depth=0.55, vertices=4, parent=b, rough=1.0, bevel=False)
        for s in (-0.18, 0.0, 0.18):                                 # the drooping tail bustle
            fadd('cone', dk, (s, 0.72, -0.05), rot=(PI - 0.7, 0, 0), radius1=0.16, radius2=0.0, depth=0.6, vertices=4, parent=b, rough=1.0, bevel=False)
        self.nb = nb = fempty((0, -0.55, 0.28), b)
        fadd('cylinder', col, (0, 0, 0.36), radius=0.15, depth=0.78, vertices=6, parent=nb, rough=1.0, bevel=False)
        self.nu = nu = fempty((0, 0, 0.72), nb)
        fadd('cylinder', '7E90AC', (0, 0, 0.3), radius=0.085, depth=0.62, vertices=6, parent=nu, rough=0.8, bevel=False)
        self.hd = hd = fempty((0, 0, 0.64), nu)
        fadd('ico_sphere', '3A2E26', (0, -0.02, 0), scale=(0.85, 1.15, 0.9), radius=0.17, subdivisions=1, parent=hd, rough=1.0)
        fadd('cone', '5A4E44', (0, -0.24, -0.03), rot=(math.radians(98), 0, 0), radius1=0.065, radius2=0.0, depth=0.24, vertices=4, parent=hd, rough=0.6, bevel=False)
        self.eyes = []
        for s in (-1, 1):
            self.eyes.append(fadd('cube', 'D88A34', (s * 0.105, -0.09, 0.045), rot=(0, 0, s * 0.5), scale=(0.035, 0.09, 0.07), size=1, parent=hd, rough=0.4, emit=0.9))
            fadd('cube', '0E0D14', (s * 0.118, -0.1, 0.045), rot=(0, 0, s * 0.5), scale=(0.02, 0.045, 0.04), size=1, parent=hd, bevel=False)
        for j in range(3):
            fadd('cone', '2A221C', (0, 0.02 + 0.06 * j, 0.14), rot=(-0.4, 0, 0), radius1=0.04, radius2=0, depth=0.14, vertices=4, parent=hd, bevel=False)
        self.hip, self.knee = [], []
        for s in (-1, 1):
            hp = fempty((s * 0.2, 0.08, -0.3), b)
            fadd('cylinder', '8C8272', (0, 0, -0.34), radius=0.12, depth=0.72, vertices=6, parent=hp, rough=0.9, bevel=False)
            kn = fempty((0, 0, -0.7), hp)
            fadd('cylinder', '8E8476', (0, 0, -0.37), radius=0.065, depth=0.76, vertices=6, parent=kn, rough=0.8, bevel=False)
            ft = fempty((0, 0, -0.75), kn)
            for a in (-0.45, 0.0, 0.45):
                fadd('cube', '7E7466', (0.12 * math.sin(a), -0.13 * math.cos(a), 0.0), rot=(0, 0, a), scale=(0.055, 0.28, 0.05), size=1, parent=ft, bevel=False)
            self.foot = ft
            self.hip.append(hp)
            self.knee.append(kn)
        self.pose(0.0, 0.0)

    def place(self, loc, yaw=0.0):
        self.root.location = loc
        self.root.rotation_euler = (0, 0, yaw)

    def pose(self, ph, run=1.0, dip=0.0, look=0.0, tilt=0.0, up=0.0):
        """ph: stride phase (radians); run 0 stands, 1 runs; dip lowers the head to peck; look turns the head;
        tilt cocks it; up lifts the chest (proud)."""
        for i in range(2):
            a = ph + i * PI
            sw = math.sin(a)
            self.hip[i].rotation_euler = (-(0.35 + 0.6 * run * sw), 0, 0)
            self.knee[i].rotation_euler = (0.7 + run * (0.15 + 0.85 * max(0.0, -math.cos(a))), 0, 0)
        self.body.location.z = 1.68 + 0.08 * run * abs(math.cos(ph)) - 0.04 * run + 0.06 * up
        self.body.rotation_euler = (0.12 * run - 0.18 * up + 0.12 * dip, 0, 0.04 * run * math.sin(ph))
        pump = 0.1 * run * math.sin(2 * ph)
        self.nb.rotation_euler = (0.35 + 0.3 * run + 0.85 * dip - 0.35 * up + pump, 0, look * 0.4)
        self.nu.rotation_euler = (-0.25 - 0.2 * run + 1.65 * dip + 0.15 * up - pump * 0.6, 0, look * 0.6)
        self.hd.rotation_euler = (-0.1 - 1.3 * dip, tilt, 0)


def gait(t, speed, off):
    return t * (1.3 + 0.24 * speed) * 2 * PI + off * 6.28


def flock(S, idx, pts, t, speed=6.0, run=1.0, dirn=None):
    """Pose a group of emus: pts[i] = (x, y, yaw) world positions."""
    for j, (x, y, yaw) in zip(idx, pts):
        e = S['emus'][j]
        e.place((x, y, 0), yaw)
        e.pose(gait(t, speed, rnd(j, 41)), run, look=0.25 * math.sin(t * 1.3 + j))


def stream(S, idx, start, vel, t, lt, spread=(6.0, 10.0), speed=6.0, jitter=1.0, z=0.0):
    """Emus running together: start (x, y) world, vel (vx, vy) units/s; each bird keeps its own lane."""
    yaw = facing((0, 0), vel)
    sp = math.hypot(*vel) or 1.0
    ux, uy = vel[0] / sp, vel[1] / sp
    out = []
    for n, j in enumerate(idx):
        lane = (rnd(j, 11) - 0.5) * spread[0]
        back = rnd(j, 12) * spread[1]
        x = start[0] + ux * (sp * lt - back) - uy * lane + jitter * 0.3 * math.sin(t * 2 + j)
        y = start[1] + uy * (sp * lt - back) + ux * lane
        e = S['emus'][j]
        e.place((x, y, z), yaw + 0.12 * math.sin(t * 1.7 + j))
        e.pose(gait(t, speed, rnd(j, 41)), 1.0, look=0.2 * math.sin(t * 1.1 + j))
        out.append((x, y))
    return out


# ---------------------------------------------------------------- people
def soldier_head(skin, hair):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        fadd('cylinder', KHAKI2, (0, 0, 0.27), radius=0.62, depth=0.035, vertices=12, parent=head, rough=1.0)   # slouch hat brim
        fadd('cylinder', KHAKI2, (0, 0, 0.42), radius=0.29, depth=0.3, vertices=10, parent=head, rough=1.0)
        fadd('cylinder', '5A4A30', (0, 0, 0.32), radius=0.3, depth=0.07, vertices=10, parent=head, rough=1.0)
        fadd('cube', KHAKI2, (-0.45, 0, 0.42), rot=(0, -1.2, 0), scale=(0.34, 0.8, 0.03), size=1, parent=head, rough=1.0)   # one side turned up
        return d
    return fn


def major_head(head):
    d = K.human_head('E2B08C', '6A4A30')(head)
    fadd('cube', '5A3E26', (0, -0.29, -0.075), scale=(0.2, 0.04, 0.045), size=1, parent=head)                   # moustache
    fadd('cylinder', KHAKI, (0, 0.02, 0.33), radius=0.31, depth=0.16, vertices=12, parent=head, rough=0.9)        # peaked cap
    fadd('cylinder', '4A3A24', (0, 0.02, 0.27), radius=0.3, depth=0.05, vertices=12, parent=head)
    fadd('cube', '2A2218', (0, -0.3, 0.25), rot=(0.25, 0, 0), scale=(0.42, 0.2, 0.025), size=1, parent=head, rough=0.4)
    return d


def farmer_head(skin, hair, hat):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        d['hat'] = h = fempty((0, 0, 0.26), head)
        fadd('cylinder', hat, (0, 0, 0), radius=0.58, depth=0.04, vertices=12, parent=h, rough=1.0)
        fadd('cylinder', hat, (0, 0, 0.15), radius=0.28, depth=0.28, vertices=10, parent=h, rough=1.0)
        fadd('cylinder', '2A2018', (0, 0, 0.05), radius=0.29, depth=0.06, vertices=10, parent=h)
        return d
    return fn


# ---------------------------------------------------------------- the gun (a generic drum-fed light machine gun)
def make_gun(S):
    g = keep(fempty(FAR))
    m = '2C2E30'
    box(g, m, -0.09, 0.09, -0.35, 0.35, -0.1, 0.1, rough=0.35)                                          # receiver
    fadd('cylinder', '33363A', (0, -0.95, 0.0), rot=(PI / 2, 0, 0), radius=0.11, depth=1.2, vertices=10, parent=g, rough=0.4)   # cooling shroud
    for i in range(5):
        fadd('torus', '24262A', (0, -0.5 - 0.2 * i, 0), rot=(PI / 2, 0, 0), major_radius=0.115, minor_radius=0.018, major_segments=10, minor_segments=4, parent=g, rough=0.4)
    fadd('cylinder', '1E2022', (0, -1.66, 0.0), rot=(PI / 2, 0, 0), radius=0.045, depth=0.26, vertices=8, parent=g, rough=0.4)
    S['pan'] = fadd('cylinder', '3E403C', (0, -0.05, 0.16), radius=0.27, depth=0.08, vertices=14, parent=g, rough=0.5)   # the drum magazine
    fadd('cylinder', '55574F', (0, 0, 0.05), radius=0.07, depth=0.04, vertices=8, parent=S['pan'])
    for i in range(7):
        a = 2 * PI * i / 7
        fadd('cube', '2A2C2A', (0.2 * math.cos(a), 0.2 * math.sin(a), 0.045), rot=(0, 0, a), scale=(0.12, 0.03, 0.02), size=1, parent=S['pan'])
    fadd('cube', '6A4A2C', (0, 0.6, -0.08), rot=(-0.12, 0, 0), scale=(0.08, 0.55, 0.17), size=1, parent=g, rough=0.7)   # wooden butt
    fadd('cube', '5A3E24', (0, 0.25, -0.2), rot=(0.4, 0, 0), scale=(0.06, 0.08, 0.2), size=1, parent=g, rough=0.7)    # grip
    S['bipod'] = []
    for s in (-1, 1):
        S['bipod'].append(bar(g, '1E2022', (0, -1.25, -0.05), (s * 0.32, -1.38, -0.62), 0.03, rough=0.4))
    S['handle'] = fadd('cube', '6A6A60', (0.12, 0.05, 0.02), scale=(0.06, 0.08, 0.04), size=1, parent=g, rough=0.3)
    S['flash'] = fl = fempty((0, -1.85, 0), g)
    for r in ((PI / 2, 0, 0), (PI / 2, 0, PI / 2), (PI / 2, 0.8, 0)):
        fadd('cone', 'FFC060', (0, 0, 0), rot=r, radius1=0.16, radius2=0, depth=0.5, vertices=4, parent=fl, emit=40)
    S['flashl'] = light((0, -2.1, 0.1), 0, 'FFB050', size=0.3, kind='POINT', parent=g)
    S['cover'] = keep(fadd('cube', 'B4A47C', FAR, scale=(0.5, 2.4, 0.42), size=1, rough=1.0))                  # canvas cover
    S['puffs'] = [keep(fadd('ico_sphere', ('8A8A86', 'A6A6A0')[i % 2], FAR, radius=0.25, subdivisions=1, rough=1.0)) for i in range(5)]
    S['gun'] = g


def gun_at(S, loc, yaw, pitch=0.0, bipod=True):
    g = S['gun']
    g.parent = None
    g.location, g.rotation_euler = loc, (pitch, 0, yaw)
    for b in S['bipod']:
        b.hide_render = not bipod


def gun_fire(S, on, t):
    for o in S['flash'].children:
        o.hide_render = not on
    S['flash'].rotation_euler = (0, t * 40, 0)
    S['flashl'].data.energy = 900 if on else 0
    if on:
        S['pan'].rotation_euler.z = t * 9


# ---------------------------------------------------------------- the truck (generic 1930s army lorry, no markings)
def make_truck(S):
    tr = keep(fempty(FAR))
    b = fempty((0, 0, 0), tr)
    S['tbody'] = b
    S['wheels'] = []
    for x, y in ((-1.3, -2.8), (1.3, -2.8), (-1.3, 2.4), (1.3, 2.4)):
        w = fempty((x, y, 0.75), tr)
        fadd('cylinder', '1C1C1E', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.75, depth=0.42, vertices=12, parent=w, rough=0.9)
        fadd('cylinder', 'B8B098', (math.copysign(0.2, x), 0, 0), rot=(0, PI / 2, 0), radius=0.32, depth=0.06, vertices=8, parent=w, rough=0.5)
        for j in range(4):
            fadd('cube', '8A8470', (math.copysign(0.24, x), 0, 0), rot=(j * PI / 4, 0, 0), scale=(0.04, 0.5, 0.06), size=1, parent=w)
        S['wheels'].append(w)
    box(b, '2A2A26', -0.8, 0.8, -4.2, 4.0, 1.0, 1.3)                                                    # chassis
    box(b, DRAB, -0.78, 0.78, -4.3, -2.3, 1.3, 2.35)                                                    # bonnet
    box(b, '3A3C34', -0.82, 0.82, -4.45, -4.3, 1.25, 2.45)                                              # radiator
    for i in range(6):
        box(b, '9A9A88', -0.7 + 0.28 * i, -0.66 + 0.28 * i, -4.48, -4.44, 1.35, 2.35, rough=0.4)
    for s in (-1, 1):
        box(b, DRAB, s * 1.05 - 0.28, s * 1.05 + 0.28, -3.7, -1.9, 1.6, 1.7)                            # mudguards
        fadd('cube', DRAB, (s * 1.3, -3.85, 1.35), rot=(-0.9, 0, 0), scale=(0.5, 0.6, 0.08), size=1, parent=b)
        box(b, DRAB, s * 1.3 - 0.28, s * 1.3 + 0.28, 1.6, 3.2, 1.62, 1.72)
        fadd('cylinder', 'E8E0C0', (s * 0.62, -4.5, 2.1), rot=(PI / 2, 0, 0), radius=0.16, depth=0.16, vertices=10, parent=b, emit=0.4)
        box(b, '3A3C34', s * 1.0 - 0.06, s * 1.0 + 0.06, -2.25, -2.15, 1.3, 3.9)                        # windscreen posts
        box(b, '3A3C34', s * 1.0 - 0.06, s * 1.0 + 0.06, -0.35, -0.25, 1.3, 3.9)
        box(b, DRAB, s * 1.06 - 0.03, s * 1.06 + 0.03, -2.2, -0.3, 1.3, 2.1)                            # low cab doors
    box(b, DRAB, -1.15, 1.15, -2.4, -0.15, 3.9, 4.02)                                                   # cab roof
    box(b, '3A3C34', -1.0, 1.0, -2.24, -2.16, 3.75, 3.88)
    fadd('cube', 'BFE4F0', (0, -2.2, 3.0), scale=(1.9, 0.02, 1.4), size=1, parent=b, rough=0.05, alpha=0.12)
    box(b, DRAB, -1.06, 1.06, -0.32, -0.2, 1.3, 3.9)                                                    # cab back
    box(b, '4A3A2A', -0.95, 0.95, -1.3, -0.4, 1.3, 1.95)                                                # bench seat
    box(b, '4A3A2A', -0.95, 0.95, -0.5, -0.35, 1.95, 2.8)
    fadd('torus', '1E1E1E', (-0.5, -1.75, 2.45), rot=(1.1, 0, 0), major_radius=0.26, minor_radius=0.03, major_segments=12, minor_segments=4, parent=b)
    box(b, 'A0825C', -1.35, 1.35, -0.15, 4.1, 1.3, 1.45, rough=0.85)                                    # flatbed
    for s in (-1, 1):
        box(b, '8A6E4C', s * 1.35 - 0.05, s * 1.35 + 0.05, -0.15, 4.1, 1.45, 1.95)
    box(b, '8A6E4C', -1.35, 1.35, 4.05, 4.15, 1.45, 1.95)                                               # tailgate
    for i in range(5):
        box(b, '7A5E40', -1.3, 1.3, 0.4 + 0.8 * i, 0.44 + 0.8 * i, 1.45, 1.47)
    fadd('cylinder', '2A2C2E', (0, 2.0, 2.15), radius=0.08, depth=1.4, vertices=8, parent=b, rough=0.4)   # post mount
    fadd('cylinder', '2A2C2E', (0, 2.0, 1.5), radius=0.35, depth=0.08, vertices=8, parent=b, rough=0.4)
    S['mount'] = fempty((0, 2.0, 2.95), b)
    S['dust'] = [keep(fadd('ico_sphere', ('C09A70', 'B08A62', 'C8A47A')[i % 3], FAR, radius=1.0, subdivisions=2, rough=1.0, alpha=0.3)) for i in range(14)]
    S['truck'] = tr


def truck_at(S, x, y, yaw, t, bounce=1.0, dist=None):
    tr = S['truck']
    tr.location, tr.rotation_euler = (x, y, 0), (0, 0, yaw)
    b = S['tbody']
    b.location = (0, 0, 0.06 * bounce * abs(math.sin(t * 9.0)) + 0.04 * bounce * math.sin(t * 5.3))
    b.rotation_euler = (0.03 * bounce * math.sin(t * 7.1), 0.035 * bounce * math.sin(t * 6.3 + 1), 0)
    d = dist if dist is not None else 0.0
    for w in S['wheels']:
        w.rotation_euler = (-d / 0.75, 0, 0)


def truck_dust(S, t, back, amount=1.0):
    """Dust boiling up behind the truck. back: world point at the tail; amount 0..1."""
    tr = S['truck']
    yaw = tr.rotation_euler.z
    bx, by = math.sin(yaw), -math.cos(yaw)                   # the truck's forward direction
    for i, d in enumerate(S['dust']):
        f = ((t * 1.1 + rnd(i, 7)) % 1.0)
        dist = 1.0 + 10.0 * f
        side = (rnd(i, 3) - 0.5) * 4.0 * (0.4 + f)
        d.location = (back[0] - bx * dist - by * side, back[1] - by * dist + bx * side, 0.4 + 2.0 * f + 0.6 * rnd(i, 8))
        r = amount * (0.5 + 1.8 * f) * (1.0 - 0.7 * f)
        d.scale = (r, r, r * 0.75)


def gun_on_mount(S, aim=(0.0, 0.0)):
    g = S['gun']
    g.parent = S['mount']
    g.location, g.rotation_euler = (0, 0, 0.15), (aim[1], 0, PI + aim[0])
    for b in S['bipod']:
        b.hide_render = True


# ---------------------------------------------------------------- the paddock
def make_field(S):
    f = fempty(FIELD)
    par = dict(o=FIELD)
    fadd('plane', 'B49448', (0, 0, 0), size=1, scale=(3000, 3000, 1), parent=f, rough=1.0)                  # wheat to the horizon
    fadd('plane', 'B07A4E', (0, TRACK, 0.02), size=1, scale=(1400, 6.5, 1), parent=f, rough=1.0)            # the red dirt track
    for i in range(60):
        fadd('cube', '9A6440', (-500 + 1000 * rnd(i, 1), TRACK + (rnd(i, 2) - 0.5) * 5, 0.03), scale=(2 + 4 * rnd(i, 3), 0.3, 0.06), size=1, parent=f, rough=1.0)
    # the farm dam: water inside a red earth bank, bare earth round it, the spoil bank on its south side
    fadd('cylinder', 'A06A44', (DAM[0], DAM[1], 0.01), radius=19, depth=0.04, vertices=24, parent=f, rough=1.0)
    fadd('torus', EARTH, (DAM[0], DAM[1], 0.0), major_radius=13.5, minor_radius=2.2, major_segments=24, minor_segments=6, parent=f, rough=1.0).scale = (1, 1, 0.42)
    fadd('cylinder', '6E8A84', (DAM[0], DAM[1], 0.25), radius=12.5, depth=0.1, vertices=24, parent=f, rough=0.12)
    S['mound'] = fadd('ico_sphere', '9C6840', (GUN[0], GUN[1] + 0.6, -0.3), scale=(2.6, 1.7, 0.75), radius=1.6, subdivisions=2, parent=f, rough=1.0)
    # the rise to the north where the mob comes from, and low blue hills far off
    fadd('ico_sphere', 'B89A4E', (0, 260, -10), scale=(320, 90, 18), radius=1.0, subdivisions=2, parent=f, rough=1.0)
    for i in range(9):
        x = -900 + 220 * i + 60 * rnd(i, 5)
        fadd('cone', ('8A9A86', '7E8E82', '96A290')[i % 3], (x, 1100 + 120 * rnd(i, 6), -4), scale=(1, 0.5, 1), radius1=160 + 90 * rnd(i, 7), radius2=40, depth=60 + 40 * rnd(i, 8), vertices=9, parent=f, rough=1.0)
    # fence along the north side of the track, with a gap the emus smashed
    pts = []
    posts = []
    for i in range(70):
        x = -160 + 4 * i
        gap = 18 < x < 30
        tilt = (0.5 * (rnd(i, 9) - 0.5), 0.9 if gap else 0.05 * rnd(i, 10), 0)
        posts.append(((x, -8.0, 0.9 if not gap else 0.5), (0.14, 0.14, 1.9), tilt))
        if i and not (18 < x < 34):
            for z in (0.6, 1.1, 1.6):
                pts.append(((x - 4, -8.0, z), (x, -8.0, z)))
    for z in (0.15, 0.3):
        pts.append(((20, -8.0, z), (28, -7.6, z + 0.05)))
    boxes_mesh('posts', '7A6A58', posts, FIELD, rough=1.0)
    boxes_mesh('wires', 'B8B8B0', seg_items(pts, 0.02), FIELD, rough=0.4)
    # the farm gate on that fence
    S['gatep'] = fempty(at(FIELD, GATE[0] - 1.5, GATE[1], 0))
    for z in (0.4, 0.9, 1.4):
        box(S['gatep'], 'C8C0B0', 0, 3.0, -0.05, 0.05, z - 0.06, z + 0.06, rough=0.5)
    bar(S['gatep'], 'C8C0B0', (0, 0, 0.4), (3.0, 0, 1.4), 0.07)
    for x in (-1.7, 1.7):
        fadd('cylinder', '6A5A48', (GATE[0] + x, GATE[1], 1.1), radius=0.12, depth=2.2, vertices=8, parent=f)
    # the homestead: weatherboard walls, a corrugated iron roof, a veranda, a rain tank, a windmill
    hx, hy = -70, -42
    box(f, 'DCD2BC', hx - 7, hx + 7, hy - 5, hy + 5, 0, 4.2)
    for i in range(8):
        box(f, 'C8BEA6', hx - 7.05, hx + 7.05, hy - 5.05, hy - 4.95, 0.5 * i + 0.2, 0.5 * i + 0.24)
    for s in (-1, 1):
        fadd('cube', 'A9AFB3', (hx, hy + s * 3.0, 5.4), rot=(s * -0.55, 0, 0), scale=(15.2, 6.8, 0.12), size=1, parent=f, rough=0.45)
    box(f, '9AA0A4', hx - 7.5, hx + 7.5, hy - 8.2, hy - 5, 3.3, 3.42, rough=0.45)
    for i in range(5):
        fadd('cylinder', 'D8CCB4', (hx - 7 + 3.5 * i, hy - 8.0, 1.65), radius=0.1, depth=3.3, vertices=6, parent=f)
    box(f, '3A3028', hx - 1.0, hx + 1.0, hy - 5.06, hy - 5.0, 0, 2.6)
    for x in (-4.5, 4.5):
        box(f, '7A9AB0', hx + x - 0.8, hx + x + 0.8, hy - 5.06, hy - 5.0, 1.4, 2.8, rough=0.1)
    fadd('cylinder', 'B0B6B8', (hx + 9.5, hy, 1.8), radius=1.8, depth=3.6, vertices=14, parent=f, rough=0.45)
    S['vanes'] = []
    for wx, wy in ((-52, -34), (64, 96)):
        for s in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            bar(f, '8A8E92', (wx + s[0] * 1.6, wy + s[1] * 1.6, 0), (wx + s[0] * 0.25, wy + s[1] * 0.25, 13), 0.12)
        for z in (4, 8, 11):
            for a, b in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
                q = 1.6 - 1.35 * z / 13
                bar(f, '8A8E92', (wx + a[0] * q, wy + a[1] * q, z), (wx + b[0] * q, wy + b[1] * q, z), 0.06)
        hub = fempty((wx, wy - 0.6, 13.6), f)
        for j in range(14):
            fadd('cube', 'C8CCD0', (0, 0, 1.4), scale=(0.35, 0.04, 2.0), size=1, parent=fempty((0, 0, 0), hub, (0, j * 2 * PI / 14, 0)), rough=0.5)
        hub.rotation_euler = (0, 0, 0.4)
        fadd('cube', 'C8CCD0', (wx, wy + 2.2, 13.6), scale=(0.06, 3.0, 1.4), size=1, parent=f)
        S['vanes'].append(hub)
    # gum trees
    for i, (x, y) in enumerate(((-96, -30), (44, -30), (110, 62), (-130, 84), (78, 150), (-44, 110), (180, -60), (300, 20), (420, -40), (-110, -60))):
        hgt = 9 + 5 * rnd(i, 13)
        fadd('cylinder', 'D6CEC0', (x, y, hgt / 2), radius=0.45, depth=hgt, vertices=7, parent=f, rough=0.8)
        bar(f, 'C8C0B2', (x, y, hgt * 0.6), (x + 2.5, y + 1, hgt * 0.95), 0.25)
        for j in range(6):
            fadd('ico_sphere', ('6E7A4A', '5E6A40', '7A8650')[j % 3], (x + 3.5 * (rnd(i, j) - 0.5), y + 3.5 * (rnd(i, j + 7) - 0.5), hgt + 1.2 * rnd(i, j + 3)),
                scale=(1.4, 1.4, 0.8), radius=2.0 + rnd(i, j + 9), subdivisions=1, parent=f, rough=1.0)
    # wheat: the dam paddock (around the ambush), the gate, the camp, the chase stretch of the track
    S['sway'] = []
    ko = [(DAM[0], DAM[1], 17.5), (GUN[0], GUN[1] - 2.5, 4.0), (GUN[0] + 4.0, GUN[1] - 2.5, 4.0), (GUN[0] + 6.0, GUN[1] - 5.0, 3.5), (GUN[0] - 3.0, GUN[1] - 1.0, 2.5),
          (13.0, 27.0, 4.5), (16.5, 32.0, 3.5), (39.5, 67.0, 5.2), (3.4, 22.6, 2.4)]
    for i in range(6):
        for j in range(5):
            x0, y0 = -6 + 4 * i, 12 + 4 * j
            wheat(S, par, x0, x0 + 4, y0, y0 + 4, 7, 100 + 7 * i + 31 * j, ko, sway=True)
    for i in range(7):
        for j in range(6):
            x0, y0 = -40 + 12 * i, 8 + 18 * j
            if -10 <= x0 <= 14 and y0 < 30:
                continue
            wheat(S, par, x0, x0 + 12, y0, y0 + 18, 2.2, 300 + 7 * i + 31 * j, ko)
    for i in range(6):
        for j in range(4):
            x0, y0 = -80 + 4.5 * i, -6.5 + 4.5 * j
            wheat(S, par, x0, x0 + 4.5, y0, y0 + 4.5, 4.5, 600 + 7 * i + 31 * j, [(GATE[0], GATE[1], 2.4), (-62.6, 0.6, 3.0), (-66.8, -2.0, 2.2)], sway=True)
    for i in range(9):
        x0 = -52 + 8 * i
        wheat(S, par, x0, x0 + 8, -7.5, 1.0, 2.0, 800 + 7 * i)
        wheat(S, par, x0, x0 + 8, -42, -16, 1.6, 900 + 7 * i, [(CAMP[0], CAMP[1], 9.0), (-70, -42, 12)])
    for i in range(18):
        x0 = 100 + 20 * i
        wheat(S, par, x0, x0 + 20, -38, -18.2, 1.3, 1000 + 7 * i)
        wheat(S, par, x0, x0 + 20, -8.2, 8, 1.1, 1200 + 7 * i)
    for i in range(4):
        wheat(S, par, 18 + 5 * i, 23 + 5 * i, 46, 54, 5, 1500 + 7 * i, ko, sway=True)
    for i in range(4):
        for j in range(3):
            x0, y0 = 30 + 6 * i, 60 + 6 * j
            wheat(S, par, x0, x0 + 6, y0, y0 + 6, 5, 1400 + 7 * i + 31 * j, [(39.5, 67.0, 5.2)], sway=True)
    # far mob: hundreds of small emu shapes on the rise, one mesh so it costs almost nothing
    items = []
    for i in range(320):
        x, y = -140 + 280 * rnd(i, 21), 120 + 160 * rnd(i, 22) ** 0.8
        z = 2.0 + 8 * max(0.0, 1 - ((y - 260) / 90) ** 2) * 0.0
        a = 0.3 * (rnd(i, 23) - 0.5)
        items += [((x, y, 1.75), (0.8, 1.3, 0.9), (0, 0, a)), ((x - 0.6 * math.sin(a), y - 0.6, 2.5), (0.2, 0.2, 1.3), (0.3, 0, a)),
                  ((x + 0.2, y, 0.8), (0.12, 0.12, 1.6), (0.3 * math.sin(i), 0, 0)), ((x - 0.2, y, 0.8), (0.12, 0.12, 1.6), (-0.3 * math.sin(i), 0, 0))]
    S['horde'] = keep(boxes_mesh('horde', '4E4034', items, FIELD, rough=1.0))
    # the camp: a bell tent and crates by the track
    S['tentx'] = t_ = fempty(at(FIELD, CAMP[0], CAMP[1], 0))
    fadd('cone', 'D8CCAA', (0, 0, 2.8), radius1=4.0, radius2=0.12, depth=4.4, vertices=14, parent=t_, rough=1.0)
    fadd('cylinder', 'D0C4A2', (0, 0, 0.6), radius=4.0, depth=1.2, vertices=14, parent=t_, rough=1.0)
    fadd('cube', '3A3024', (0, -3.9, 1.3), rot=(-0.12, 0, 0), scale=(1.4, 0.06, 2.6), size=1, parent=t_)
    fadd('cylinder', '6A5040', (0, 0, 2.6), radius=0.08, depth=5.4, vertices=6, parent=t_)
    for j in range(8):
        a = 2 * PI * j / 8 + 0.2
        bar(t_, 'C8C0A8', (3.3 * math.cos(a), 3.3 * math.sin(a), 1.9), (6.2 * math.cos(a), 6.2 * math.sin(a), 0.0), 0.02)
    S['tdoor'] = fadd('cylinder', '6A5040', (0.8, -4.05, 1.6), radius=0.07, depth=3.2, vertices=6, parent=t_)
    for i in range(3):
        box(t_, 'A88A50', 3.6 + 0.9 * i, 4.4 + 0.9 * i, -3.0, -2.2, 0, 0.7 + 0.3 * (i % 2))
    S['field'] = f


# ---------------------------------------------------------------- inside the bell tent
def make_tent(S):
    t = fempty(TENT)
    fadd('cylinder', '8A7A5C', (0, 0, 0.0), radius=5.0, depth=0.05, vertices=16, parent=t, rough=1.0)              # ground sheet
    fadd('cone', 'C8B890', (0, 0, 3.8), radius1=5.0, radius2=0.12, depth=5.4, vertices=18, parent=t, rough=1.0)
    fadd('cylinder', 'BEAE86', (0, 0, 0.6), radius=5.0, depth=1.2, vertices=18, parent=t, rough=1.0)
    fadd('cylinder', '6A5040', (0, 1.8, 3.3), radius=0.1, depth=6.6, vertices=6, parent=t)
    box(t, '2A2018', -0.8, 0.8, -5.0, -4.9, 0, 2.4)                                                             # the door flap at night
    # camp table
    box(t, '9A7448', -1.4, 1.4, -0.7, 0.7, 1.18, 1.26, rough=0.7)
    for x in (-1.3, 1.3):
        for y in (-0.6, 0.6):
            fadd('cylinder', '7A5A38', (x, y, 0.6), radius=0.05, depth=1.18, vertices=6, parent=t)
    for i, (x, y, w_, d_, h_) in enumerate(((2.6, 1.6, 1.0, 0.7, 0.7), (2.6, 2.4, 1.0, 0.7, 0.7), (2.6, 2.0, 1.0, 0.7, 1.4), (-3.0, -1.9, 0.9, 0.6, 0.65))):
        box(t, ('A88A50', '9A7E48')[i % 2], x - w_ / 2, x + w_ / 2, y - d_ / 2, y + d_ / 2, 0.02 if h_ < 1 else 0.72, h_ if h_ < 1 else 1.42)
    S['seat'] = box(t, '8A6E44', -0.45, 0.45, 1.1, 1.7, 0.0, 0.72)
    S['crate'] = box(t, 'A88A50', -2.65, -1.75, 0.85, 1.55, 0.0, 0.75)
    # hurricane lamp on the table
    S['lamp'] = lp = fempty((TENT[0] + 0.9, TENT[1] + 0.25, 1.26))
    fadd('cylinder', '3A3634', (0, 0, 0.08), radius=0.16, depth=0.16, vertices=10, parent=lp, rough=0.4)
    fadd('cylinder', '3A3634', (0, 0, 0.62), radius=0.13, depth=0.08, vertices=10, parent=lp, rough=0.4)
    for j in range(3):
        a = 2 * PI * j / 3
        bar(lp, '3A3634', (0.15 * math.cos(a), 0.15 * math.sin(a), 0.15), (0.12 * math.cos(a), 0.12 * math.sin(a), 0.6), 0.025)
    fadd('ico_sphere', 'FFE6B8', (0, 0, 0.36), scale=(1, 1, 1.25), radius=0.15, subdivisions=2, parent=lp, rough=0.1, alpha=0.25)
    S['flame'] = fadd('cone', 'FFB040', (0, 0, 0.34), radius1=0.045, radius2=0, depth=0.14, vertices=6, parent=lp, emit=25)
    S['lampl'] = light((TENT[0] + 0.9, TENT[1] + 0.25, 1.75), 0, 'FFB060', size=0.2, kind='POINT')
    S['moths'] = [fadd('cube', 'D8D0C0', at(TENT, 0.9, 0.25, 2.2), scale=(0.08, 0.04, 0.01), size=1, rough=1.0) for _ in range(3)]
    # the report book, pen, figures sheet, telegram, newspapers, ammunition box and brass
    S['book'] = bk = fempty(at(TENT, -0.2, -0.1, 1.27))
    for s in (-1, 1):
        fadd('cube', 'F0E8D0', (s * 0.34, 0, 0.02), rot=(0, s * -0.08, 0), scale=(0.66, 0.9, 0.03), size=1, parent=bk, rough=0.9)
    box(bk, '5A2A1E', -0.7, 0.7, -0.47, 0.47, -0.01, 0.01)
    for i in range(10):
        box(bk, 'A8A49A', -0.62, -0.08, -0.38 + 0.08 * i, -0.36 + 0.08 * i, 0.04, 0.045)
    S['tally'] = []
    for g in range(9):
        for m in range(5):
            x = 0.12 + 0.11 * (g % 4) + 0.018 * m
            y = 0.34 - 0.2 * (g // 4)
            if m < 4:
                o = fadd('cube', '1E1E2A', (x, y, 0.045), scale=(0.008, 0.007, 0.006), size=1, parent=bk)
                o.scale = (0.008, 0.11, 0.006)
            else:
                o = fadd('cube', '1E1E2A', (x - 0.035, y, 0.046), rot=(0, 0, 0.9), scale=(0.008, 0.13, 0.006), size=1, parent=bk)
            S['tally'].append(o)
    S['pen'] = keep(fadd('cylinder', '1E1A18', FAR, radius=0.018, depth=0.32, vertices=6, rough=0.4))
    S['sheet'] = fadd('cube', 'ECE4CC', at(TENT, 0.75, -0.35, 1.275), rot=(0, 0, 0.25), scale=(0.5, 0.68, 0.01), size=1, rough=1.0)
    S['paper'] = pp = fempty(FAR)
    fadd('cube', 'E8E2D0', (0, 0, 0), scale=(0.9, 1.2, 0.012), size=1, parent=pp, rough=1.0)
    pp.scale = (0.75, 0.75, 0.75)
    keep(pp)
    for i in range(14):
        box(pp, '9A968C', -0.4 + (0.45 if i >= 7 else 0), -0.05 + (0.45 if i >= 7 else 0), -0.54 + 0.08 * (i % 7) - (0.0 if i < 7 else 0), -0.52 + 0.08 * (i % 7), 0.007, 0.009)
    for (cx, cy, sx, sy, r) in ((0.05, 0.25, 0.32, 0.18, 0.0), (-0.17, 0.39, 0.03, 0.2, -0.6), (-0.27, 0.49, 0.07, 0.05, 0), (0.08, 0.06, 0.025, 0.2, 0.2), (0.16, 0.07, 0.025, 0.2, -0.2)):
        fadd('cube', '2A2624', (cx, cy, 0.009), rot=(0, 0, r), scale=(sx, sy, 0.004), size=1, parent=pp)       # a drawn emu, no words
    S['bundle'] = bd = keep(fempty(FAR))
    for i in range(6):
        fadd('cube', ('E8E2D0', 'DCD6C4')[i % 2], (0.03 * rnd(i, 3), 0.03 * rnd(i, 4), 0.025 * i), rot=(0, 0, 0.06 * (rnd(i, 5) - 0.5)), scale=(0.9, 1.2, 0.024), size=1, parent=bd, rough=1.0)
    bar(bd, 'C8B890', (-0.46, 0, 0.08), (0.46, 0, 0.08), 0.02)
    S['telegram'] = tg = keep(fempty(FAR))
    fadd('cube', 'EFE6C8', (0, 0, 0), scale=(0.42, 0.012, 0.3), size=1, parent=tg, rough=1.0)
    for i in range(4):
        box(tg, '8A8478', -0.16, 0.12 - 0.06 * (i % 2), -0.008, -0.006, 0.06 - 0.05 * i, 0.075 - 0.05 * i)
    S['abox'] = ab = keep(fempty(FAR))
    box(ab, '7A6A40', -0.3, 0.3, -0.2, 0.2, 0, 0.36)
    box(ab, '6A5A36', -0.31, 0.31, -0.21, 0.21, 0.3, 0.36)
    S['cases'] = [keep(fadd('cylinder', 'C8901C', FAR, radius=0.035, depth=0.13, vertices=8, rough=0.18, bevel=False)) for _ in range(64)]
    K.mat('C8901C', 0.18).node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 1.0
    S['tent'] = t


# ---------------------------------------------------------------- the new fence
def make_fence(S):
    f = fempty(FEN)
    par = dict(o=FEN)
    fadd('plane', 'B8964C', (0, 0, 0), size=1, scale=(3000, 3000, 1), parent=f, rough=1.0)
    for i in range(8):
        fadd('cone', ('8A7E86', '7E7480', '96888A')[i % 3], (-700 + 200 * i, 900, -4), scale=(1, 0.5, 1), radius1=150, radius2=40, depth=60 + 30 * rnd(i, 3), vertices=9, parent=f, rough=1.0)
    posts, wires = [], []
    for i in range(41):
        x = -60 + 3 * i
        if x > 4:
            posts.append(((x - 0.0, -2.5 - 0.3 * (i % 3), 0.12), (0.16, 3.4, 0.16), (0, 0, 0.2 * rnd(i, 4))))   # posts still lying in the grass
            continue
        posts.append(((x, 0, 1.6), (0.18, 0.18, 3.2), (0, 0, 0)))
        if i:
            for z in (0.2, 0.6, 1.0, 1.4, 1.8, 2.2, 2.6, 3.0):
                wires.append(((x - 3, 0, z), (x, 0, z)))
            for j in range(8):
                xx = x - 3 + 0.375 * j
                wires.append(((xx, 0, 0.2), (xx, 0, 3.0)))
    boxes_mesh('fposts', '8A7860', posts, FEN, rough=1.0)
    boxes_mesh('mesh', 'C0C0B8', seg_items(wires, 0.018), FEN, rough=0.35)
    S['post'] = fadd('cylinder', '8A7860', (FEN[0] + 7.0, FEN[1], 1.6), radius=0.11, depth=3.2, vertices=8, parent=None)    # the post being driven
    fadd('cylinder', '7A6A58', (6.5, -2.0, 0.3), rot=(PI / 2, 0, 0), radius=0.6, depth=0.8, vertices=12, parent=f)         # a roll of wire
    S['hammer'] = hm = keep(fempty(FAR))
    fadd('cylinder', '7A5A38', (0, 0, 0.6), radius=0.04, depth=1.2, vertices=6, parent=hm)
    fadd('cube', '3A3A3E', (0, 0, 1.25), scale=(0.18, 0.4, 0.18), size=1, parent=hm, rough=0.4)
    for j in range(5):
        for i in range(5):
            x0, y0 = -24 + 9 * i, 0.9 + 4 * j
            wheat(S, par, x0, x0 + 9, y0, y0 + 4, 2.8 if j < 2 else 1.2, 2000 + 7 * i + 31 * j, [(9.5, 4.5, 4.5), (-2.0, 3.5, 3.5)], sway=(j < 1))
            wheat(S, par, x0, x0 + 9, -0.9 - 4 * (j + 1), -0.9 - 4 * j, 2.2 if j < 2 else 1.0, 2400 + 7 * i + 31 * j, [(8.0, -4.0, 6.5), (-3.2, -4.0, 6.0)])
    S['fen'] = f


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['major'] = K.Rig(dict(top=KHAKI, pants=KHAKI2, hand='E2B08C', boot='3A2A1E', fore=KHAKI), major_head)
    S['gunner'] = K.Rig(dict(top='B49A62', pants=KHAKI2, hand='D8A884', boot='3A2A1E', fore='D8A884'), soldier_head('D8A884', '4A3020'))
    S['sarge'] = K.Rig(dict(top='B09660', pants=KHAKI2, hand='C89070', boot='3A2A1E', fore='B09660'), soldier_head('C89070', '2A1E18'))
    S['farmer'] = K.Rig(dict(top='6A7FA0', pants='4A4038', hand='C8946C', boot='3A2A1E', fore='6A7FA0'), farmer_head('C8946C', '8A6A4A', '6A5A44'))
    S['farmer2'] = K.Rig(dict(top='8A6A4A', pants='3E3A34', hand='E0B898', boot='2A2018', fore='D8D0C0'), farmer_head('E0B898', '3A2A1E', '7A6A50'))
    S['humans'] = [S['major'], S['gunner'], S['sarge'], S['farmer'], S['farmer2']]
    make_field(S)
    make_gun(S)
    make_truck(S)
    make_tent(S)
    make_fence(S)
    S['emus'] = [Emu(i) for i in range(30)]
    S['cast'] = [S['rook']] + S['humans']
    S['suntgt'] = fempty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    S['sun'].data.angle = 0.02
    S['keyl'] = light((0, 0, 0), 0, 'FFE8D0', size=3.0)
    S['keytgt'] = fempty()
    S['keyl'].constraints.new('TRACK_TO').target = S['keytgt']
    tgt, rigc = fempty(), fempty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 2600
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w40')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.02, 0.55
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs[2], mr.inputs[0])
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(mx.outputs[2], S['bg'].inputs[0])
    S['skymix'] = mx
    reset(S)
    return S


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.face, rig.jawv = 'calm', 0.0
    for e in S['emus']:
        e.place(FAR)
        e.pose(0.0, 0.0)
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for l in (S['sun'], S['keyl'], S['lampl'], S['flashl']):
        l.data.energy = 0
    gun_fire(S, False, 0.0)
    for b in S['bipod']:
        b.hide_render = False
    for o in S['tally']:
        o.hide_render = False
    for o in S['moths']:
        o.location = FAR
    S['post'].location = (FEN[0] + 7.0, FEN[1], 1.6)
    S['flame'].scale = (1, 1, 1)
    for rig in (S['farmer'], S['farmer2']):
        h = rig.extra['hat']
        h.parent = rig.head
        h.location, h.rotation_euler = (0, 0, 0.26), (0, 0, 0)
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, brow1=0.0)
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinking and beak lip sync once the shot has posed everyone; the wheat sways and the windmills turn."""
    for o, ph in S['sway']:
        o.rotation_euler = (0.035 * math.sin(t * 1.6 + ph), 0.03 * math.sin(t * 1.15 + ph * 1.7), 0)
    for h in S['vanes']:
        h.rotation_euler = (0, t * 2.2, 0.4)
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.43) % 1 < 0.035 or e == 'shut'
    ez = dict(calm=0.07, low=0.042, shocked=0.135, sad=0.055, soft=0.06, squint=0.035, wide=0.12).get(e, 0.07)
    tilt = dict(low=-0.06, shocked=0.36, sad=0.45, soft=0.22, squint=-0.2, wide=0.3).get(e, -0.22)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        up = S['brow1'] if i == 1 else 0.0
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt + (s * 0.5 * up), s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e in ('shocked', 'wide') else 0.0) + 0.08 * up
    tip, off = S['hat_tip'], sm(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + tip * 0.38, 0.2, off), lerp(0.07, 1.25, off), 0)
    r['hat'].location = (lerp(0.0, 0.74, off), lerp(0.0, -0.14, off), lerp(0.27 + S['hat_jump'] + tip * 0.1, -1.45, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.36 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.8, shut=0.07, tired=0.5, warm=0.8, sad=0.55, hard=0.6, squint=0.3, pain=0.25).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.045 if f == 'wide' else -0.02 if f in ('hard', 'tired', 'squint', 'pain') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide', 'tired', 'pain') else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.2 if f == 'warm' else 0.13, 0.03, 0.035 + 0.14 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sky(S, a, b=None, k=0.0):
    A, B = SKIES[a], SKIES[b or a]
    mixc = lambda i: tuple(lerp(x, y, k) for x, y in zip(K.hexc(A[i]), K.hexc(B[i])))
    S['skymix'].inputs[6].default_value = mixc(0)
    S['skymix'].inputs[7].default_value = mixc(1)
    S['bg'].inputs[1].default_value = lerp(A[2], B[2], k)
    S['sun'].data.energy = lerp(A[3], B[3], k)
    S['sun'].data.color = mixc(4)[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(lerp(u, v, k) * 500 for u, v in zip(A[5], B[5]))


def shoot(S, o, pos, look, lens=40, roll=0.0):
    S['camrig'].location, S['camtgt'].location = at(o, *pos), at(o, *look)
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


def key(S, o, pos, look, watts, col='FFE8D0'):
    S['keyl'].location, S['keytgt'].location = at(o, *pos), at(o, *look)
    S['keyl'].data.energy, S['keyl'].data.color = watts, K.hexc(col)[:3]


def put(S, rig, o, x, y, z=0.0, yaw=0.0, pose=None, face=None, pitch=0.0):
    rig.place(at(o, x, y, z), yaw, pitch)
    rig.apply(pose or P())
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def head(S, rig):
    return wpos(rig.head)


def tentlight(S, w=260):
    S['lampl'].data.energy = w * (1 + 0.06 * math.sin(K._T[0] * 23) + 0.04 * math.sin(K._T[0] * 37))
    S['flame'].scale = (1, 1, 1 + 0.15 * math.sin(K._T[0] * 31))


def moths(S, t):
    for i, m in enumerate(S['moths']):
        a = t * (3.1 + i) + i * 2.1
        m.location = at(TENT, 0.9 + 0.35 * math.cos(a), 0.25 + 0.35 * math.sin(a), 2.05 + 0.15 * math.sin(a * 1.7))
        m.rotation_euler = (0, 0, a + PI / 2)


CROUCH = dict(lL=(1.25, 1.9), lR=(1.25, 1.9), lift=-0.75, lean=0.55)
AIM = dict(CROUCH, aL=(1.45, 0.1, 0.5), aR=(1.2, -0.1, 1.2), head=(0.15, 0.0))
GZ = 1.45                           # height of the gun on the spoil bank
MOB = list(range(0, 16))


def gun_scene(S, t, aim=0.0):
    """The ambush: the gun on its bipod on the spoil bank, the gunner and the sergeant crouched behind it."""
    gun_at(S, at(FIELD, GUN[0], GUN[1], GZ), PI + aim)
    put(S, S['gunner'], FIELD, GUN[0] + 0.05, GUN[1] - 2.05, 0.15, PI, P('stand', **AIM), 'hard')
    put(S, S['sarge'], FIELD, GUN[0] + 1.35, GUN[1] - 1.75, 0.1, PI - 0.25, P('stand', **CROUCH, aR=(1.5, 0.7, 1.4), head=(0.1, 0.0)), 'hard')


# ---------------------------------------------------------------- the hook: the ambush at the dam
def dam_mob(S, k, t, lt):
    """On the trampled ground east of the dam, low: the mob pours out of the wheat and runs at the lens, the lead bird charging right past it. First and last shot."""
    d = lt / k if k > 1e-3 else 1.1
    u = (1 - k) * d if S['prm'].get('loop') else lt
    sky(S, 'day')
    stream(S, MOB, (17.5, 39.0), (-1.9, -5.4), t, u, spread=(11.0, 20.0), speed=6.5)
    e = S['emus'][16]
    e.place(at(FIELD, lerp(15.2, 14.7, u / 1.1), lerp(33.0, 28.8, u / 1.1), 0), facing((0, 0), (-0.5, -4.2)))
    e.pose(gait(t, 7, 0.3), 1.0, look=-0.3)
    S['horde'].location = (0, -10.0 * u, 0)
    q = sm(u / 1.2)
    shoot(S, FIELD, (lerp(13.0, 12.8, q), lerp(26.4, 26.0, q), lerp(0.9, 1.0, q)), (lerp(18.0, 17.6, q), 46.0, lerp(2.6, 2.9, q)), 30)


def gun_hide(S, k, t, lt):
    """Behind the gun hidden on the spoil bank: the two soldiers crouched behind it, barrel and drum aimed at the dam, the emus coming round the water."""
    sky(S, 'day')
    gun_scene(S, t)
    stream(S, MOB, (12.0, 58.0), (-0.6, -3.2), t, lt + 1.0, spread=(22.0, 12.0), speed=4.0)
    S['horde'].location = (0, -16.0 - 6.0 * lt, 0)
    key(S, FIELD, (2, 14, 6), (6, 19, 2), 400)
    shoot(S, FIELD, (lerp(2.6, 3.2, k), lerp(15.2, 15.9, k), lerp(3.6, 3.4, k)), (lerp(6.4, 6.2, k), 26.0, 1.5), 24)


def gunner_eyes(S, k, t, lt):
    """Close on the gunner's face behind the stock, eyes narrowing as he tracks the birds; the sergeant beside him lifts a flat hand: wait."""
    sky(S, 'day')
    gun_scene(S, t)
    g = S['gunner']
    put(S, g, FIELD, GUN[0] + 0.05, GUN[1] - 2.05, 0.15, PI, P('stand', **dict(AIM, head=(0.15 + 0.05 * math.sin(lt * 3), lerp(0.3, -0.2, sm(k))))), 'squint' if lt > 0.6 else 'hard')
    hand = sm(lt / 0.6)
    put(S, S['sarge'], FIELD, GUN[0] + 1.35, GUN[1] - 1.75, 0.1, PI - 0.25, P('stand', **CROUCH, aR=(lerp(0.9, 2.3, hand), lerp(0.1, 0.35, hand), lerp(1.3, 0.6, hand), -0.8 * hand), head=(0.0, lerp(0.0, 0.35, hand))), 'hard')
    h = head(S, g)
    key(S, FIELD, (h[0] - 2, h[1] + 3, h[2] + 0.5), h, 600)
    q = sm(k)
    shoot(S, (0, 0, 0), (h[0] - lerp(2.6, 1.3, q), h[1] + lerp(3.4, 2.4, q), h[2] - lerp(0.75, 0.4, q)), (h[0] + lerp(0.7, 0.35, q), h[1], h[2] - 0.1), 32)


def jam(S, k, t, lt):
    """Close on the gun from the side: two bursts of flash, then the drum stops, a puff of smoke; the gunner yanks the handle, the sergeant slaps it."""
    sky(S, 'day')
    gun_scene(S, t)
    d = lt / k if k > 1e-3 else 2.0
    fire = (0.15 * d < lt < 0.25 * d or 0.31 * d < lt < 0.42 * d) and int(t * 30) % 2 == 0
    gun_fire(S, fire, t)
    j = sm((lt - 0.45 * d) / (0.25 * d))
    for i, p in enumerate(S['puffs']):
        f = max(0.0, (lt - 0.45 * d - 0.05 * i) / 0.8)
        if f > 0:
            p.location = at(FIELD, GUN[0] + 0.12 * i, GUN[1] + 0.1, GZ + 0.25 + 0.5 * f + 0.1 * i)
            r = 0.15 + 0.4 * min(1.0, f)
            p.scale = (r, r, r)
    S['handle'].location.y = 0.05 + 0.25 * math.sin(PI * min(1.0, max(0.0, (lt - 0.55 * d) / (0.15 * d))))
    smack = sm((lt - 0.68 * d) / (0.08 * d)) * (1 - sm((lt - 0.8 * d) / 0.12))
    put(S, S['sarge'], FIELD, GUN[0] + 1.35, GUN[1] - 1.75, 0.1, PI - 0.6, P('stand', **CROUCH, aR=(lerp(1.0, 1.8, smack), lerp(0.2, -0.6, smack), lerp(1.4, 0.4, smack)), head=(0.25, 0.4)), 'wide' if j > 0.5 else 'hard')
    put(S, S['gunner'], FIELD, GUN[0] + 0.05, GUN[1] - 2.05, 0.15, PI, P('stand', **dict(AIM, aR=(1.2, -0.1 + 0.5 * j, 1.2 - 0.6 * j))), 'wide' if j > 0.5 else 'hard')
    S['gunner'].jawv = S['sarge'].jawv = 0.5 * j
    for jdx in MOB:                                  # once it jams they scatter, out of focus beyond the gun
        e = S['emus'][jdx]
        a = rnd(jdx, 5) * PI
        x0, y0 = -4 + 16 * rnd(jdx, 11), 50 + 10 * rnd(jdx, 12)
        go = 7.0 * j * max(0.0, lt - 0.5 * d)
        e.place(at(FIELD, x0 + math.cos(a) * go, y0 + math.sin(a) * go, 0), facing((0, 0), (math.cos(a), math.sin(a))) if j > 0.2 else 0.0)
        e.pose(gait(t, 7, rnd(jdx, 41)), max(0.3, j), look=0.3 * math.sin(t + jdx))
    key(S, FIELD, (GUN[0] - 4, GUN[1] - 3, 4), (GUN[0], GUN[1], GZ), 500)
    shoot(S, FIELD, (lerp(2.6, 3.0, k), lerp(19.6, 19.9, k), 2.15), (GUN[0] + 0.3, GUN[1] + 0.4, GZ + 0.1), 30, roll=0.02 * math.sin(t * 40) * j)


# ---------------------------------------------------------------- doubt
def rook_jam(S, k, t, lt):
    """Rook standing beside the jammed gun on the spoil bank; behind him the emus scatter round the dam. He raps the gun, turns, speaks."""
    sky(S, 'day')
    gun_scene(S, t)
    S['gunner'].face = S['sarge'].face = 'wide'
    S['gunner'].jawv = 0.3
    for jdx in MOB:
        e = S['emus'][jdx]
        a = rnd(jdx, 5) * PI
        go = 7 * (lt + 0.6)
        x, y = -4 + 16 * rnd(jdx, 11) + math.cos(a) * go, 50 + 10 * rnd(jdx, 12) + math.sin(a) * go
        e.place(at(FIELD, x, y, 0), facing((0, 0), (math.cos(a), math.sin(a))))
        e.pose(gait(t, 7, rnd(jdx, 41)), 1.0)
    rap = lt < 0.5
    turn = sm((lt - 0.45) / 0.35)
    put(S, S['rook'], FIELD, GUN[0] + 1.9, GUN[1] - 0.4, 0.55, lerp(PI / 2 + 0.3, 0.75, turn),
        P('point', aR=(0.9, 0.35, 0.9 + 0.5 * math.sin(lt * 26)), head=(0.35, 0.1)) if rap else P('hips', head=(0.05, 0.0)), 'low')
    S['hat_tip'] = 0.45
    h = head(S, S['rook'])
    key(S, FIELD, (h[0] + 3, h[1] - 4, h[2] + 2), h, 700)
    shoot(S, (0, 0, 0), (h[0] + lerp(3.0, 2.7, k), h[1] - lerp(4.6, 4.1, k), h[2] - lerp(0.9, 0.7, k)), (h[0] - 0.4, h[1] + 0.8, h[2] - 0.55), 30)


# ---------------------------------------------------------------- the chase
def wheat_raid(S, k, t, lt):
    """High over the paddock: emus everywhere, trampling, streaming through the smashed gap in the fence and across the track."""
    sky(S, 'day')
    stream(S, list(range(0, 12)), (24.0, 6.0), (0.4, -5.0), t, lt, spread=(8.0, 20.0), speed=5.5)
    for j in range(12, 30):
        e = S['emus'][j]
        x, y = -40 + 90 * rnd(j, 31), 2 + 40 * rnd(j, 32)
        e.place(at(FIELD, x + 1.5 * lt * math.sin(j), y - 1.5 * lt, 0), rnd(j, 33) * 6.28)
        e.pose(gait(t, 2, rnd(j, 41)), 0.25 if j % 3 else 0.0, dip=0.0 if j % 3 else 0.6 + 0.3 * math.sin(t * 3 + j))
    S['horde'].location = (0, -40 - 3 * lt, 0)
    shoot(S, FIELD, (lerp(-8, -2, k), lerp(-50, -47, k), lerp(19, 17, k)), (lerp(14, 15, k), 6, 0), 26)


def wheat_eat(S, k, t, lt):
    """Low in the farmer's wheat: emu heads dip and tug at the ears either side of the lens; at the gate beyond them the farmer takes off his hat."""
    sky(S, 'day')
    for n, (x, y, yaw) in enumerate(((-63.9, -4.0, facing((0, 0), (-0.79, 0.61))), (-66.7, -2.8, facing((0, 0), (0.79, -0.61))), (-70.6, -3.2, facing((0, 0), (0.9, 0.3))))):
        e = S['emus'][n]
        e.place(at(FIELD, x, y, 0), yaw)
        e.pose(0.0, 0.0, dip=0.85 + 0.15 * math.sin(t * 6 + n * 2), look=0.2 * math.sin(t * 2 + n))
    u = sm((lt - 0.3) / 0.5)
    f = put(S, S['farmer'], FIELD, GATE[0] + 0.6, GATE[1] - 0.9, 0, facing((GATE[0] + 0.6, GATE[1] - 0.9), (-63.0, -0.6)),
            blend(P('stand', aR=(0.3, 0.2, 0.3)), P('stand', aR=(1.55, 0.0, 2.2, 0.6), aL=(0.4, 0.3, 0.5), head=(0.2, 0.0)), u), 'sad')
    hat = f.extra['hat']
    if u > 0.3:
        hat.parent = None
        hat.location = wpos(f.hands[0], (0, 0, -0.6))
        hat.rotation_euler = (1.2, 0, 0.2)
    key(S, FIELD, (-62, -2, 4), (-67, -6, 1.8), 600)
    shoot(S, FIELD, (lerp(-62.8, -63.1, k), lerp(-0.4, -0.8, k), lerp(1.55, 1.65, k)), (-69.2, -8.6, lerp(1.9, 2.3, k)), 30)


def truck_mount(S, k, t, lt):
    """Beside the truck on the track: the major points at the flatbed while the gunner swings the gun onto the post mount."""
    sky(S, 'day')
    truck_at(S, -24.0, TRACK, PI / 2, t, bounce=0.0)
    u = sm(lt / 0.9)
    gm = wpos(S['mount'])
    if u < 1.0:
        gun_at(S, (lerp(gm[0] - 1.4, gm[0], u), lerp(gm[1] - 0.8, gm[1], u), lerp(gm[2] - 0.6, gm[2] + 0.15, u)), PI / 2 + lerp(0.6, PI, u), bipod=False)
    else:
        gun_on_mount(S, (0.0, -0.05))
    put(S, S['gunner'], FIELD, -24.0 - 1.4, TRACK - 0.9, 1.45, -PI / 2 + 0.4, P('stand', aL=(1.4, 0.2, 0.4), aR=(1.4, -0.2, 0.4), lean=0.15 * (1 - u), head=(0.2, 0.0)), 'hard')
    nod = 0.25 * math.sin(PI * sm((lt - 1.0) / 0.3))
    put(S, S['major'], FIELD, -24.0 - 2.2, TRACK - 3.0, 0, 0.35, P('point', aR=(1.3, 0.1, 0.1), head=(-0.05 + nod, 0.15)), 'hard')
    key(S, FIELD, (-30, -20, 6), (-25, -13, 2.5), 900)
    shoot(S, FIELD, (lerp(-31.5, -30.8, k), lerp(-20.5, -19.6, k), lerp(3.4, 3.2, k)), (-25.0, -12.6, 2.6), 28)


def truck_chase(S, k, t, lt):
    """Tracking beside the truck as it lurches down the track; a line of emus runs alongside through the wheat, then easily pulls ahead."""
    sky(S, 'day')
    x = 180 + 8.0 * lt
    truck_at(S, x, TRACK, PI / 2, t, bounce=1.0, dist=8.0 * lt)
    gun_on_mount(S, (0.2 * math.sin(t * 6), 0.15 * math.sin(t * 8)))
    gp = wpos(S['mount'], (0, 1.2, -1.5))
    put(S, S['gunner'], (0, 0, 0), gp[0], gp[1], gp[2], -PI / 2, P('brace', aL=(1.5, 0.2, 0.6), aR=(1.5, -0.2, 0.6)), 'wide')
    put(S, S['sarge'], (0, 0, 0), *wpos(S['tbody'], (-0.5, -1.0, 1.4)), yaw=-PI / 2, pose=P('sit', aL=(1.3, 0.1, 0.7), aR=(1.3, 0.1, 0.7)), face='hard')
    for n in range(7):
        e = S['emus'][n]
        ex = x - 6 + 2.8 * n + 4.0 * lt + 1.2 * rnd(n, 3)
        ey = TRACK - 4.6 - 2.4 * rnd(n, 4) - (n % 2) * 1.4
        e.place(at(FIELD, ex, ey, 0), PI / 2 + 0.05 * math.sin(t * 2 + n))
        e.pose(gait(t, 11, rnd(n, 41)), 1.0)
    truck_dust(S, t, wpos(S['tbody'], (0, 4.2, 0.5)), 1.0)
    shoot(S, FIELD, (x - 3.0 + 3.0 * lt, TRACK - 17.0, 3.4), (x + 2.0 + 2.5 * lt, TRACK - 2.0, 2.0), 30, roll=0.01 * math.sin(t * 9))


def emu_legs(S, k, t, lt):
    """Ground level on the verge: an emu's long legs and three-toed feet pound the dirt beside the truck's spinning front wheel."""
    sky(S, 'day')
    x = 240 + 8.0 * lt
    truck_at(S, x, TRACK, PI / 2, t, bounce=1.0, dist=8.0 * lt)
    gun_on_mount(S)
    e = S['emus'][0]
    ex = x + 3.6 + 1.6 * lt
    e.place(at(FIELD, ex, TRACK - 4.0, 0), PI / 2)
    e.pose(gait(t, 11, 0.2), 1.0)
    e2 = S['emus'][1]
    e2.place(at(FIELD, ex + 5, TRACK - 5.4, 0), PI / 2)
    e2.pose(gait(t, 11, 0.6), 1.0)
    shoot(S, FIELD, (ex - 2.2, TRACK - 5.9, 0.45), (ex + 0.2, TRACK - 3.0, 0.75), 24, roll=0.03 * math.sin(t * 17))


def rook_truck(S, k, t, lt):
    """On the bouncing flatbed, filmed from beside the cab looking back: the gunner fights the gun, Rook clings to the side rail, hat bouncing, and stares at the emu running level with the tail."""
    sky(S, 'day')
    x = 300 + 8.0 * lt
    truck_at(S, x, TRACK, PI / 2, t, bounce=1.6, dist=8.0 * lt)
    gun_on_mount(S, (0.45 * math.sin(t * 7), 0.3 * math.sin(t * 11)))
    gp = wpos(S['mount'], (0, 1.1, -1.5))
    put(S, S['gunner'], (0, 0, 0), gp[0], gp[1], gp[2], PI / 2 + 0.3, P('brace', aL=(1.5, 0.2, 0.6), aR=(1.5, -0.2, 0.6)), 'wide')
    S['gunner'].jawv = 0.4
    rp = wpos(S['tbody'], (-0.85, 2.6, 1.45))
    put(S, S['rook'], (0, 0, 0), rp[0], rp[1], rp[2], PI / 2 + 0.25, P('brace', aR=(1.0, 0.9, 0.5), aL=(1.2, -0.3, 0.8), head=(0.05, -0.9)), 'shocked')
    S['hat_jump'] = 0.35 * abs(math.sin(t * 9.0))
    e = S['emus'][2]
    e.place(at(FIELD, x - 8.0 + 0.4 * math.sin(t), TRACK - 3.4, 0), PI / 2)
    e.pose(gait(t, 9, 0.1), 1.0, look=-0.9, tilt=0.2)
    truck_dust(S, t, wpos(S['tbody'], (0, 4.2, 0.5)), 0.35)
    h = head(S, S['rook'])
    key(S, FIELD, (x + 4, TRACK - 4, 6), h, 700)
    c = wpos(S['tbody'], (-0.3, -0.1, 3.4))
    shoot(S, (0, 0, 0), c, (h[0] - 1.0, h[1] - 1.5, h[2] - 0.8), 24, roll=0.04 * math.sin(t * 13))


# ---------------------------------------------------------------- the retreat
def press_drop(S, k, t, lt):
    """In the tent: a bundle of newspapers thumps onto the table in front of the major; the top paper shows a drawn emu."""
    sky(S, 'tent')
    tentlight(S, 300)
    put(S, S['major'], TENT, 0.0, 1.35, 0.25, 0.0, P('sit', aL=(0.9, 0.1, 1.6, 1.0), aR=(0.9, 0.1, 1.6, 1.0), head=(0.2, 0.0)), 'wide' if lt > 0.4 else 'hard')
    f = sm(lt / 0.22)
    S['bundle'].location = at(TENT, -0.3, -0.25, lerp(2.6, 1.27, f))
    S['bundle'].rotation_euler = (0, 0, 0.15)
    S['paper'].location = at(TENT, 0.15, -0.15, 1.44 if f >= 1 else -100)
    S['paper'].rotation_euler = (0, 0, lerp(-0.6, 0.2, sm((lt - 0.25) / 0.35)))
    key(S, TENT, (1.5, -2.5, 3.5), (0, 0, 1.4), 300, 'FFC890')
    q = sm(lt / 1.2)
    shoot(S, TENT, (lerp(0.25, 0.3, q), lerp(-1.9, -2.1, q), lerp(3.4, 3.2, q)), (0.05, lerp(0.2, 0.5, q), lerp(1.6, 1.9, q)), 28)


def rook_paper(S, k, t, lt):
    """Rook on an ammunition crate holding the newspaper up; he lowers it until only his eyes show over the top, one brow up."""
    sky(S, 'tent')
    tentlight(S, 300)
    u = sm((lt - 0.1) / 0.4)
    yaw = 0.6
    r = put(S, S['rook'], TENT, -2.2, 1.2, 0.25, yaw, P('sit', aL=(1.35, 0.25, 1.4, 1.0), aR=(1.35, 0.25, 1.4, 1.0), head=(lerp(0.1, 0.2, u), 0.0)), 'squint')
    S['brow1'] = u
    S['hat_tip'] = 0.1
    hd = wpos(r.hands[0])
    hr = wpos(r.hands[1])
    c = ((hd[0] + hr[0]) / 2, (hd[1] + hr[1]) / 2, (hd[2] + hr[2]) / 2)
    fx, fy = math.sin(yaw), -math.cos(yaw)
    S['paper'].location = (c[0] + 0.15 * fx, c[1] + 0.15 * fy, c[2] + lerp(0.45, -0.35, u))
    S['paper'].rotation_euler = (PI / 2 - 0.1, 0, yaw)
    h = head(S, r)
    key(S, TENT, (h[0] + 1.5 * fx, h[1] + 1.5 * fy, h[2] + 0.8), h, 240, 'FFC890')
    shoot(S, (0, 0, 0), (h[0] + 3.1 * fx + 0.3, h[1] + 3.1 * fy, h[2] - 0.25), (h[0], h[1], h[2] - 0.45), 36)


def pack_up(S, k, t, lt):
    """Evening on the track: the truck drives away with the gun under canvas, Rook sitting on the tailgate; three emus stand in the track and watch it go."""
    sky(S, 'evening')
    x = 1.0 - 5.0 * lt
    truck_at(S, x, TRACK, -PI / 2, t, bounce=0.6, dist=5.0 * lt)
    gun_on_mount(S)
    S['cover'].parent = S['mount']
    S['cover'].location, S['cover'].rotation_euler = (0, 0, 0.2), (0, 0, 0)
    rp = wpos(S['tbody'], (0.6, 4.05, 1.25))
    put(S, S['rook'], (0, 0, 0), rp[0], rp[1], rp[2], PI / 2, P('sit', lL=(1.4, 1.5), lR=(1.4, 1.3), aL=(0.4, 0.3, 0.6), aR=(0.4, 0.3, 0.6), head=(0.3, 0.0)), 'low')
    S['hat_tip'] = 0.6
    for n, (ex, ey, yaw) in enumerate(((10.5, TRACK + 1.9, -PI / 2 - 0.2), (12.6, TRACK - 1.6, -PI / 2 + 0.25), (8.4, TRACK - 1.3, -PI / 2 + 0.1))):
        e = S['emus'][n]
        e.place(at(FIELD, ex, ey, 0), yaw)
        e.pose(0.0, 0.0, look=0.15 * math.sin(t * 1.3 + n), tilt=0.15 * math.sin(t * 0.9 + n * 2), up=0.4)
    key(S, FIELD, (24, TRACK - 4, 6), (10, TRACK, 2.5), 2600, 'FFC898')
    shoot(S, FIELD, (lerp(21.0, 20.4, k), TRACK - 0.3, 1.6), (lerp(4.0, 2.0, k), TRACK, 2.6), 36)


def major_report(S, k, t, lt):
    """Night in the tent: the major writes by the hurricane lamp, then stops and looks up, brows raised. Moths circle the lamp."""
    sky(S, 'tent')
    tentlight(S, 320)
    moths(S, t)
    stop = sm((lt - 0.9) / 0.35)
    write = 0.06 * math.sin(lt * 18) * (1 - stop)
    m = put(S, S['major'], TENT, 0.0, 1.35, 0.25, 0.0, P('sit', aL=(0.9, 0.1, 1.6, 1.0), aR=(1.05 + write, -0.05, 1.5 - write), head=(lerp(0.45, -0.1, stop), 0.0)), 'wide' if stop > 0.5 else 'calm')
    hp = wpos(m.hands[1])
    S['pen'].location = (hp[0] + 0.02, hp[1] - 0.05, hp[2] + 0.06)
    S['pen'].rotation_euler = (0.5, 0.3, 0.2)
    h = head(S, m)
    key(S, TENT, (0.9, 0.25, 2.2), h, 80, 'FFB060')
    shoot(S, TENT, (lerp(-0.9, -0.7, k), lerp(-2.6, -2.2, k), 1.55), (0.0, 1.0, lerp(2.0, 2.3, k)), 30)


def emu_tank(S, k, t, lt):
    """Dawn: one big emu stands chest out like a tank, filmed from the ground right under it; Rook walks up, knocks on it, it does not blink."""
    sky(S, 'dawn')
    e = S['emus'][5]
    e.place(at(FIELD, 40.0, 70.0, 0), facing((40, 70), (38.8, 66.4)))
    e.pose(0.0, 0.0, look=0.0, up=1.0)
    for n, (x, y) in enumerate(((30.0, 82.0), (52.0, 86.0), (44.0, 95.0))):
        o = S['emus'][n]
        o.place(at(FIELD, x, y, 0), 2.6 + n)
        o.pose(0.0, 0.0, dip=0.7)
    wk = sm(lt / 0.8)
    knock = 0.8 < lt < 1.5
    put(S, S['rook'], FIELD, lerp(43.0, 41.2, wk), lerp(67.4, 68.9, wk), 0.0, facing((41.2, 68.9), (40.0, 70.0)) if wk >= 1 else -PI / 2 + 0.3,
        K.walk(t, 1.6) if wk < 1 else P('point', aR=(1.1, 0.2, 0.9 + 0.6 * abs(math.sin(lt * 18)) if knock else 0.9), head=(-0.2, 0.0)), 'low')
    S['hat_tip'] = lerp(0.2, 1.0, sm((lt - 1.5) / 0.3))
    key(S, FIELD, (44, 63, 3), (40, 70, 2.5), 900, 'FFD0A0')
    shoot(S, FIELD, (lerp(39.0, 39.2, k), lerp(66.9, 67.2, k), 0.35), (40.4, 69.9, lerp(2.6, 2.4, k)), 20)


# ---------------------------------------------------------------- re-hook: round two
def farmers_ask(S, k, t, lt):
    """In profile at the tent door: two farmers, hats in hands, point back at the wheat where emus graze; the major listens, arms folded; Rook leans by the door."""
    sky(S, 'day')
    cx, cy = CAMP
    for n, rig in enumerate((S['farmer'], S['farmer2'])):
        fx, fy = cx - 0.9 + 1.7 * n, cy - 8.4 - 0.3 * n
        pt = n == 1 or math.sin(lt * 4) > 0.0
        put(S, rig, FIELD, fx, fy, 0, facing((fx, fy), (cx + 0.4, cy - 4.6)),
            P('point', aR=(1.25, -0.9 + 0.2 * n, 0.2), aL=(0.6, 0.2, 1.4, 0.6), head=(0.0, 0.5 if pt else 0.0)) if pt else P('stand', aL=(0.6, 0.2, 1.4, 0.6), aR=(0.9, 0.2, 1.4)), 'sad')
        rig.jawv = 0.35 * abs(math.sin(lt * 9 + n))
        hat = rig.extra['hat']
        hat.parent = None
        hat.location = wpos(rig.hands[0], (0, 0, -0.5))
        hat.rotation_euler = (1.3, 0, 0.3)
    put(S, S['major'], FIELD, cx + 0.4, cy - 4.6, 0, facing((cx + 0.4, cy - 4.6), (cx, cy - 8.4)), P('cross', head=(0.05, 0.1 * math.sin(lt * 2))), 'hard')
    put(S, S['rook'], FIELD, cx + 1.9, cy - 4.3, 0, facing((cx + 1.9, cy - 4.3), (cx, cy - 8.4)) + 0.3, P('stand', aL=(0.5, -0.1, 1.7, 1.3), aR=(0.4, 0.7, 0.3), lean=-0.06, head=(0.0, 0.5 - 0.9 * sm((lt - 0.5) / 0.4))), 'low')
    for n in range(3, 8):
        e = S['emus'][n]
        e.place(at(FIELD, cx + 12 + 5 * rnd(n, 1), cy - 16 + 4 * (n - 3), 0), rnd(n, 3) * 6.28)
        e.pose(0.0, 0.0, dip=0.6 + 0.3 * math.sin(t * 3 + n))
    key(S, FIELD, (cx - 6, cy - 9, 6), (cx, cy - 6.5, 2.4), 900)
    shoot(S, FIELD, (lerp(cx - 7.6, cx - 7.0, k), lerp(cy - 8.4, cy - 8.0, k), 2.6), (cx + 0.6, cy - 6.4, 2.4), 28)


def round_two(S, k, t, lt):
    """The truck roars back down the track at the lens, gun uncovered; Rook stands on the cab roof, one wing pointing forward."""
    sky(S, 'day')
    x = 20.0 + 8.0 * lt
    truck_at(S, x, TRACK, PI / 2, t, bounce=1.0, dist=8.0 * lt)
    gun_on_mount(S, (0.1 * math.sin(t * 3), 0.0))
    gp = wpos(S['mount'], (0, 1.2, -1.5))
    put(S, S['gunner'], (0, 0, 0), gp[0], gp[1], gp[2], PI / 2 + PI, P('stand', aL=(1.4, 0.2, 0.6), aR=(1.4, -0.2, 0.6)), 'hard')
    rp = wpos(S['tbody'], (0.0, -1.3, 4.02))
    put(S, S['rook'], (0, 0, 0), rp[0], rp[1], rp[2], -PI / 2 + 0.25, P('point', aR=(1.5, 0.05, 0.05), aL=(0.4, 0.6, 0.6), head=(-0.1, 0.2), lean=0.06 * math.sin(t * 9)), 'low')
    S['hat_tip'] = 0.3
    truck_dust(S, t, wpos(S['tbody'], (0, 4.2, 0.5)), 1.0)
    key(S, FIELD, (x + 10, TRACK - 5, 6), (x, TRACK, 3), 900)
    shoot(S, FIELD, (x + 11.0 - 0.6 * lt, TRACK - 2.4, 1.3), (x, TRACK, 3.6), 30)


# ---------------------------------------------------------------- four weeks, recalled, the count
def weeks_sun(S, k, t, lt):
    """The camp from a distance while the weeks rush by: the sun swings across, shadows sweep, emus wander through in groups."""
    a = k * 1.0
    sky(S, 'morning', 'evening', a)
    sd = Vector((lerp(0.9, -0.9, a), lerp(-0.2, -0.3, a), 0.35 + 0.5 * math.sin(PI * a))).normalized()
    S['sun'].location = tuple(sd * 500)
    truck_at(S, -24.0, TRACK, PI / 2, t, bounce=0.0)
    gun_on_mount(S)
    for n in range(14):
        e = S['emus'][n]
        g = n // 5
        ph = (k * 3 + g * 0.37) % 1.0
        x = CAMP[0] - 30 + 60 * ph + 3 * rnd(n, 6)
        y = CAMP[1] + 16 - 9 * g + 4 * rnd(n, 7)
        e.place(at(FIELD, x, y, 0), PI / 2)
        e.pose(gait(t, 4, rnd(n, 41)), 0.6)
    shoot(S, FIELD, (CAMP[0] + 24, CAMP[1] - 36, 17), (CAMP[0] + 2, CAMP[1] + 7, 0), 26)


def recalled(S, k, t, lt):
    """Outside the tent: the major reads a telegram and lowers it with a long breath; the gunner covers the gun; Rook reads over his shoulder."""
    sky(S, 'evening')
    cx, cy = CAMP
    truck_at(S, -24.0, TRACK, PI / 2, t, bounce=0.0)
    gun_on_mount(S)
    cv = sm((lt - 0.4) / 0.8)
    S['cover'].parent = S['mount']
    S['cover'].location = (0, lerp(1.6, 0.0, cv), lerp(0.6, 0.2, cv))
    S['cover'].scale = (0.5, lerp(0.4, 2.4, cv), 0.42)
    put(S, S['gunner'], FIELD, -24.0 - 1.4, TRACK + 1.2, 1.45, -PI / 2, P('reach', aR=(1.6, 0.2, 0.3), aL=(1.4, 0.3, 0.4)), 'tired')
    low = sm((lt - 0.7) / 0.5)
    m = put(S, S['major'], FIELD, cx + 2.6, cy - 5.2, 0, 0.3, P('stand', aL=(lerp(0.95, 0.4, low), 0.1, 1.1, 0.8), aR=(lerp(0.95, 0.4, low), 0.1, 1.1, 0.8), head=(lerp(0.35, 0.5, low), 0.0)), 'tired')
    hl, hr = wpos(m.hands[0]), wpos(m.hands[1])
    S['telegram'].location = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2, (hl[2] + hr[2]) / 2 + 0.12)
    S['telegram'].rotation_euler = (0.7, 0, 0.3)
    put(S, S['rook'], FIELD, cx + 3.6, cy - 4.4, 0, 0.1, P('stand', aL=(-0.2, 0.4, 1.8, 1.2), aR=(-0.2, 0.4, 1.8, 1.2), lean=0.22, head=(0.35, 0.4)), 'squint')
    S['brow1'] = sm((lt - 0.5) / 0.3)
    h = head(S, m)
    key(S, FIELD, (cx + 4, cy - 12, 4), h, 700, 'FFB878')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.4, 1.2, k), h[1] - lerp(4.4, 3.8, k), h[2] - 0.6), (h[0] + 0.5, h[1], h[2] - 0.45), 32)


def ledger(S, k, t, lt):
    """Close on the report book by lamplight: the pen runs down a long column of tally marks in neat groups."""
    sky(S, 'tent')
    tentlight(S, 300)
    n = len(S['tally'])
    shown = int(lerp(14, n, sm(k * 1.1)))
    for i, o in enumerate(S['tally']):
        o.hide_render = i >= shown
    last = S['tally'][max(0, shown - 1)]
    lp = wpos(last)
    S['pen'].location = (lp[0] + 0.05, lp[1] - 0.04, lp[2] + 0.17)
    S['pen'].rotation_euler = (0.45, 0.25, 0.3 + 0.1 * math.sin(lt * 20))
    put(S, S['major'], TENT, 0.0, 1.35, 0.25, 0.0, P('sit', aL=(0.9, 0.1, 1.6, 1.0), aR=(1.1, -0.1, 1.5)), 'calm')
    shoot(S, TENT, (lerp(0.15, 0.1, k), lerp(-0.85, -0.65, k), lerp(2.45, 2.2, k)), (0.0, 0.05, 1.27), 34)


def casings(S, k, t, lt):
    """An ammunition box tips over and brass cases pour out across the table, rolling and glinting in the lamplight. (hush)"""
    sky(S, 'tent')
    tentlight(S, 340)
    tip = sm(lt / 0.5)
    S['abox'].location = at(TENT, -0.9, 0.2, 1.27)
    S['abox'].rotation_euler = (0, lerp(0.0, -1.75, tip), 0.2)
    for i, c in enumerate(S['cases']):
        f = max(0.0, lt - 0.25 - 0.032 * i)
        if f <= 0:
            c.location = at(TENT, -0.9 + 0.1 * (rnd(i, 1) - 0.5), 0.2 + 0.1 * (rnd(i, 2) - 0.5), 1.4)
            continue
        dist = min(1.0, f * 1.1)
        ang = 0.9 * (rnd(i, 3) - 0.5)
        L = 0.4 + 1.3 * rnd(i, 4)
        x = -0.75 + math.cos(ang) * L * sm(dist)
        y = 0.2 + math.sin(ang) * L * sm(dist) * 1.3 - 0.3 * rnd(i, 5)
        z = 1.3 + 0.25 * max(0.0, 1 - dist * 3) + 0.03
        c.location = at(TENT, x, y, z)
        c.rotation_euler = (PI / 2, 0, ang + f * 14 * (1 - dist) + rnd(i, 6) * 3)
    q = sm(k)
    shoot(S, TENT, (lerp(2.0, 1.1, q), lerp(-1.7, -1.2, q), lerp(1.95, 1.62, q)), (lerp(-0.4, 0.0, q), 0.15, 1.3), 30, roll=lerp(-0.05, 0.03, q))


# ---------------------------------------------------------------- suspiciously tidy
def lay_rows(S, rows, part, x0=-0.9, y0=-0.45):
    """Brass cases in neat rows of ten on the table; part = how many of the last row are placed."""
    n = 0
    for r in range(rows):
        for c in range(10):
            if r == rows - 1 and c >= part:
                break
            if n >= len(S['cases']):
                return
            S['cases'][n].location = at(TENT, x0 + 0.09 * c, y0 + 0.16 * r, 1.33)
            S['cases'][n].rotation_euler = (PI / 2, 0, 0)
            n += 1
    return n


def rook_tens(S, k, t, lt):
    """At the end of the camp table Rook slides brass cases into neat rows of ten with a wingtip, counts the last one and taps his beak."""
    sky(S, 'tent')
    tentlight(S, 300)
    part = min(10, int(lt * 7) + 4)
    n = lay_rows(S, 5, part)
    slide = (lt * 7) % 1.0
    if n is not None and n < len(S['cases']) and part < 10:
        c = S['cases'][n]
        c.location = at(TENT, -0.9 + 0.09 * part + 0.25 * (1 - sm(slide)), -0.45 + 0.64, 1.33)
        c.rotation_euler = (PI / 2, 0, 0)
    tap = lt > 1.2
    r = put(S, S['rook'], TENT, -1.85, -0.15, 0.0, PI / 2 - 0.15, P('tap', head=(0.1, 0.25)) if tap else P('point', aR=(1.15, 0.1, 0.5), aL=(0.4, 0.2, 1.6, 1.0), head=(0.45, 0.1), lean=0.25), 'squint' if tap else 'calm')
    S['hat_tip'] = -0.1
    h = head(S, r)
    key(S, TENT, (h[0] + 1.6, h[1] - 1.0, h[2] + 0.4), h, 320, 'FFC890')
    q = sm(k)
    shoot(S, TENT, (lerp(0.75, 0.5, q), lerp(-1.75, -1.5, q), lerp(2.55, 2.4, q)), (-1.2, -0.05, lerp(1.85, 1.95, q)), 28)


def rook_squint(S, k, t, lt):
    """Close on Rook in the lamplight at the end of the table: he lifts his brim with one finger, raises one brow and narrows his eyes at us."""
    sky(S, 'tent')
    tentlight(S, 280)
    lay_rows(S, 5, 10)
    u = sm(lt / 0.5)
    r = put(S, S['rook'], TENT, -1.85, -0.15, 0.0, facing((-1.85, -0.15), (-0.5, -1.15)), blend(P('stand', head=(0.1, 0.0)), P('hat', head=(0.0, 0.0)), u), 'squint')
    S['brow1'] = sm((lt - 0.3) / 0.3)
    S['hat_tip'] = lerp(0.4, -0.25, u)
    h = head(S, r)
    key(S, TENT, (0.6, -2.0, 2.6), h, 220, 'FFC890')
    dd = lerp(1.75, 1.45, k)
    shoot(S, (0, 0, 0), (h[0] + 0.8 * dd + 0.1, h[1] - 0.6 * dd, h[2] - 0.12), (h[0], h[1], h[2] - 0.05), 40)


# ---------------------------------------------------------------- the end
def asked_no(S, k, t, lt):
    """The farmer at his gate by the empty track reads a letter, lowers it, shoulders dropping; out in his wheat behind him the emus graze."""
    sky(S, 'day')
    drop = sm((lt - 0.7) / 0.5)
    f = put(S, S['farmer'], FIELD, GATE[0] + 0.4, GATE[1] - 1.2, 0, 0.25,
            P('stand', aL=(lerp(0.95, 0.3, drop), 0.1, lerp(1.1, 0.4, drop)), aR=(lerp(0.95, 0.2, drop), 0.1, lerp(1.1, 0.3, drop)), head=(lerp(0.45, 0.3, drop), 0.0), lean=0.1 * drop, lift=-0.04 * drop), 'sad')
    hl, hr = wpos(f.hands[0]), wpos(f.hands[1])
    S['telegram'].location = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2 - 0.1, (hl[2] + hr[2]) / 2 + 0.12)
    S['telegram'].rotation_euler = (0.7 + 0.7 * drop, 0, 0.25)
    for n, (x, y) in enumerate(((-75.0, 3.0), (-66.0, 4.0), (-71.0, 8.0), (-63.0, 1.0))):
        e = S['emus'][n]
        e.place(at(FIELD, x, y, 0), rnd(n, 9) * 6.28)
        e.pose(0.0, 0.0, dip=0.7 + 0.25 * math.sin(t * 3 + n))
    key(S, FIELD, (-66, -16, 5), (GATE[0], GATE[1] - 1, 2.4), 700)
    shoot(S, FIELD, (lerp(-67.8, -68.1, k), lerp(-15.0, -14.3, k), 2.4), (GATE[0] + 0.2, GATE[1] + 0.5, 2.5), 30)


def fence_build(S, k, t, lt):
    """Two farmers put up a tall wire fence: one swings a sledgehammer onto a post that Rook holds steady, flinching at every blow."""
    sky(S, 'day')
    hit = (lt * 2.2 + 0.25) % 1.0
    sw = math.sin(PI * min(1.0, hit / 0.5)) if hit < 0.5 else 0.0
    down = 0.42 <= hit < 0.62
    S['post'].location = (FEN[0] + 7.0, FEN[1], 1.6 - 0.04 * int(lt * 2.2))
    f = put(S, S['farmer'], FEN, 7.0, -1.5, 0, facing((7.0, -1.5), (7.0, 0.0)), P('stand', aL=(lerp(0.9, 2.9, sw), 0.1, 0.3), aR=(lerp(0.9, 2.9, sw), -0.1, 0.3), lean=-0.1 * sw + 0.15 * (1 - sw), head=(-0.2 * sw, 0.0)), 'hard')
    hp = wpos(f.hands[0])
    S['hammer'].location = hp
    S['hammer'].rotation_euler = (lerp(-0.4, -2.8, sw) + PI, 0, 0)
    put(S, S['farmer2'], FEN, 3.4, -1.8, 0, 0.9, P('reach', aR=(1.2, 0.3, 0.5), aL=(1.1, 0.4, 0.6), lean=0.3), 'calm')
    put(S, S['rook'], FEN, 7.85, -0.7, 0, -1.3, P('stand', aL=(1.4, -0.3, 0.6), aR=(1.4, 0.1, 0.6), lean=-0.08 if down else 0.05, head=(0.25 if down else 0.0, 0.3)), 'shut' if down else 'low')
    S['hat_jump'] = 0.12 if down else 0.0
    key(S, FEN, (10, 5, 5), (7.3, -1, 2.4), 800)
    shoot(S, FEN, (lerp(9.8, 9.5, k), lerp(4.6, 4.1, k), 2.6), (6.8, -1.0, 2.4), 28)


def fence_face(S, k, t, lt):
    """Sunset, from the emus' side of the new fence: the emu's head in the foreground, Rook's face through the wire; both tilt their heads."""
    sky(S, 'dusk')
    tl = math.sin(PI * sm((lt - 0.4) / 0.6))
    e = S['emus'][4]
    e.place(at(FEN, -4.5, 1.6, 0), facing((-4.5, 1.6), (-4.5, -1.0)))
    e.pose(0.0, 0.0, tilt=0.45 * tl, look=0.0, dip=0.12)
    for n, x in enumerate((-12.0, 3.0, 10.0)):
        o = S['emus'][n]
        o.place(at(FEN, x, 6.0 + 3 * n, 0), 2.6 + n)
        o.pose(0.0, 0.0, dip=0.6)
    put(S, S['rook'], FEN, -4.6, -1.3, 0.0, PI, P('cross', head=(0.0, 0.0)), 'low')
    S['rook'].head.rotation_euler.y = -0.4 * tl
    eh = wpos(e.hd)
    rh = head(S, S['rook'])
    key(S, FEN, (-3.5, -6, 4), rh, 800, 'FFA070')
    shoot(S, (0, 0, 0), (eh[0] + lerp(2.0, 1.7, k), eh[1] + lerp(2.4, 2.1, k), eh[2] + 0.1), (rh[0] - 0.1, rh[1], rh[2] - 0.2), 32)


def rook_question(S, k, t, lt):
    """Dusk by the fence: Rook flips a brass case like a coin, catches it, looks at it glint, pockets it, and looks straight at us."""
    sky(S, 'dusk')
    for n, x in enumerate((-6.0, 4.0)):
        o = S['emus'][n]
        o.place(at(FEN, x, 5.0 + 2 * n, 0), 3.2)
        o.pose(0.0, 0.0, dip=0.5 + 0.2 * math.sin(t * 2 + n))
    flip = lt < 0.7
    pocket = sm((lt - 0.8) / 0.3)
    pose = P('stand', aR=(lerp(1.1, 1.6, math.sin(PI * min(1, lt / 0.7))), 0.1, 1.4), head=(0.2 if flip else 0.0, 0.0)) if lt < 0.8 else P('stand', aR=(lerp(1.1, 0.1, pocket), 0.25, lerp(1.4, 0.9, pocket)), head=(0.0, 0.0))
    r = put(S, S['rook'], FEN, -3.5, -1.6, 0.0, 0.25, pose, 'squint' if lt > 1.0 else 'calm')
    S['brow1'] = sm((lt - 1.0) / 0.25)
    hp = wpos(r.hands[1])
    c = S['cases'][0]
    if pocket < 0.9:
        c.location = (hp[0], hp[1] - 0.1, hp[2] + 0.15 + (0.7 * math.sin(PI * lt / 0.7) if flip else 0.0))
        c.rotation_euler = (lt * 30 if flip else PI / 2, 0, 0.3)
    S['hat_tip'] = 0.2
    h = head(S, r)
    key(S, FEN, (-1.5, -7, 4), h, 800, 'FFA070')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.4, 1.2, k), h[1] - lerp(4.6, 3.9, k), h[2] - lerp(0.9, 0.7, k)), (h[0] + 0.05, h[1], h[2] - 0.45), 34)


def mob_still(S, k, t, lt):
    """The photograph on the case board: the mob coming down to the dam, from the trampled ground by the water."""
    sky(S, 'day')
    stream(S, MOB, (17.5, 39.0), (-1.9, -5.4), 0.3, 0.35, spread=(11.0, 20.0), speed=6.0)
    e = S['emus'][16]
    e.place(at(FIELD, 15.6, 33.5, 0), facing((0, 0), (-0.5, -4.2)))
    e.pose(gait(0.3, 7, 0.3), 1.0, look=-0.3)
    S['horde'].location = (0, -4, 0)
    shoot(S, FIELD, (12.6, 25.6, 1.5), (17.4, 44.0, 2.4), 30)


STILLS = {'mob': mob_still}

SHOTS3D = {f.__name__: f for f in (
    dam_mob, gun_hide, gunner_eyes, jam, rook_jam, wheat_raid, wheat_eat, truck_mount, truck_chase, emu_legs, rook_truck,
    press_drop, rook_paper, pack_up, major_report, emu_tank, farmers_ask, round_two, weeks_sun, recalled, ledger, casings,
    rook_tens, rook_squint, asked_no, fence_build, fence_face, rook_question)}
