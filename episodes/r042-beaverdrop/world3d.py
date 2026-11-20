"""Case 042 in 3D - the Idaho beaver drop, August 1948. Beavers in and around the lake town of McCall (Payette Lake) were
felling trees and flooding yards as people built homes there, so Idaho Fish and Game set out to move them deep into the
backcountry of the Chamberlain Basin. Trucks could not get there, and horses and mules carrying the beavers became, in
Elmo Heter's words, "spooky and quarrelsome". Heter used war-surplus parachutes and a wooden box that held together in
the air and sprang open on landing. An old male beaver the crew named Geronimo was dropped on a landing field again and
again to test it; in the end he crawled back into his box by himself, ready to go again. In 1948 76 beavers were
dropped into the backcountry, Geronimo among the first with three young females; 75 of them landed safely. A year
later they had built dams and lodges and were on their way to colonies, Geronimo's among them.

Built for this story only: a high mountain basin with a meadow and a creek seen from the air and on the ground; a
twin-engine plane with a cargo hold full of beaver boxes; a parachute and the hinged box; the lake town with a gnawed
tree and a flooded yard; a pack mule; a landing field with a hangar and a windsock; the dam and lodge a year later.

Everything is a generic low-poly reconstruction. The plane carries no markings, makes or logos; nobody's likeness is
attempted; no words appear in the 3D world."""
import math

import bpy
from mathutils import Matrix, Vector

from engine4 import kit3d as K
from engine4.kit3d import P, blend, lerp, light

PI = math.pi
FAR = (0, 0, -30000)
BAS = (0.0, 0.0, 0.0)               # the Chamberlain Basin: mountains, the meadow and its creek
TOWN = (5000.0, 0.0, 0.0)           # the lake town: yards, a gnawed tree, a flooded lawn, the mule corral
FLD = (-5000.0, 0.0, 0.0)           # the landing field: grass strip, hangar, windsock
HOLD = (0.0, 5000.0, 400.0)         # the cargo hold, high over its own patch of mountains
LAND = (4.0, -2.0)                  # where the hero box lands in the meadow
HOST = {'rook_box_ride', 'rook_land', 'rook_flood', 'rook_mule', 'rook_test', 'rook_tally', 'rook_jaw', 'rook_heter',
        'rook_hold', 'rook_hush', 'rook_dam', 'signoff'}
CAMFILL = {'*': 140, 'drop_close': 90, 'drop_wide': 0, 'plane_wide': 0, 'test_drop': 40, 'rook_box_ride': 160,
           'rook_hold': 260, 'hold': 240, 'rook_hush': 200, 'signoff': 200, 'rook_jaw': 180}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
FUR, FUR2, BELLY = '6A4630', '5A3C2A', '8A6448'
WOOD, WOOD2, ROPE = 'B08A5A', '96744A', 'D8C8A0'
CANOPY = ('EEE6D2', 'D8CDB4')
GRASS, MEADOW, PINE = '5E7A3A', '8AA04E', ('2E4A30', '35553A', '3E5E3A')
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    high=('F2E2C8', '5A8CC4', 1.1, 3.6, 'FFE4BC', (0.5, -0.55, 0.45)),
    meadow=('F0E4CC', '6A98CC', 1.05, 3.4, 'FFE6C0', (0.45, -0.6, 0.55)),
    town=('E6EAEA', '7AA0C8', 1.1, 3.0, 'FFF0DC', (-0.4, -0.6, 0.6)),
    field=('F4E8D2', '7AA2CC', 1.15, 3.2, 'FFEAD0', (0.6, -0.5, 0.5)),
    dusk=('F2A868', '3A4E7A', 0.75, 1.6, 'FFB070', (0.75, -0.45, 0.16)),
    year=('EEE8D0', '78A4CC', 1.1, 3.3, 'FFEFD2', (-0.5, -0.6, 0.55)))
_KEEP = []

# Each primitive is made once as a prototype mesh and copied (much faster than an operator call per object).
_PROTO, _LAST = {}, [None]


def _select(o):
    if _LAST[0] is not None:
        try:
            _LAST[0].select_set(False)
        except (ReferenceError, RuntimeError):
            pass
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    _LAST[0] = o


def _unit(kind, kw):
    if kind in ('cube', 'plane'):
        v = kw.pop('size', 2.0)
        kw['size'] = 1.0
        return kw, (v, v, v)
    if kind == 'ico_sphere':
        r = kw.pop('radius', 1.0)
        kw['radius'] = 1.0
        return kw, (r, r, r)
    if kind == 'cylinder':
        r, d = kw.pop('radius', 1.0), kw.pop('depth', 2.0)
        kw.update(radius=1.0, depth=1.0)
        return kw, (r, r, d)
    if kind == 'cone':
        r1, r2, d = kw.pop('radius1', 1.0), kw.pop('radius2', 0.0), kw.pop('depth', 2.0)
        if r1 <= 0:
            kw.update(radius1=r1, radius2=r2, depth=d)
            return kw, (1.0, 1.0, 1.0)
        kw.update(radius1=1.0, radius2=round(r2 / r1, 5), depth=1.0)
        return kw, (r1, r1, d)
    return kw, (1.0, 1.0, 1.0)


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    kw, sc = _unit(kind, dict(kw))
    key = (kind, tuple(sorted(kw.items())))
    if key not in _PROTO or _PROTO[key].name not in bpy.data.meshes:
        getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=(0, 0, 0), **kw)
        o = bpy.context.object
        _PROTO[key] = o.data
        bpy.data.objects.remove(o)
    me = _PROTO[key].copy()
    if sc != (1.0, 1.0, 1.0):
        me.transform(Matrix.Diagonal((sc[0], sc[1], sc[2], 1.0)))
    o = bpy.data.objects.new(kind, me)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    me.materials.append(K.mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    if parent:
        o.parent = parent
    _select(o)
    return o


def empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new('Empty', None)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    _select(o)
    return o


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


def plus(a, b, s=1.0):
    return (a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s)


def span(o, a, b, w):
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def bar(par, col, a, b, w, **kw):
    o = add('cylinder', col, radius=0.5, depth=1, vertices=5, parent=par, **kw)
    span(o, a, b, w)
    return o


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def field(name, xs, ys, zf, col, par, rough=1.0):
    """A faceted height field: one quad per grid cell."""
    me = bpy.data.meshes.new(name)
    vs = [(x, y, zf(x, y)) for y in ys for x in xs]
    nx = len(xs)
    fs = [(j * nx + i, (j + 1) * nx + i, (j + 1) * nx + i + 1, j * nx + i + 1) for j in range(len(ys) - 1) for i in range(nx - 1)]
    me.from_pydata(vs, [], fs)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(K.mat(col, rough))
    o.parent = par
    return o


def dome(col, r, h, par=None, seg=12, col2=None):
    """A parachute canopy: an open hemisphere of gores (alternating panels), apex up, rim at z=0."""
    me = bpy.data.meshes.new('canopy')
    rings = 4
    vs = [(0, 0, h)]
    for j in range(1, rings + 1):
        a = (PI / 2) * j / rings
        for i in range(seg):
            b = 2 * PI * i / seg
            rr = r * math.sin(a) * (1.0 if j < rings else 0.97)
            vs.append((rr * math.cos(b), rr * math.sin(b), h * math.cos(a) - (0.12 * h if j == rings and i % 2 else 0)))
    fs = [(0, 1 + i, 1 + (i + 1) % seg) for i in range(seg)]
    for j in range(rings - 1):
        o0, o1 = 1 + j * seg, 1 + (j + 1) * seg
        fs += [(o0 + i, o1 + i, o1 + (i + 1) % seg, o0 + (i + 1) % seg) for i in range(seg)]
    me.from_pydata(vs, [], fs)
    me.update()
    o = bpy.data.objects.new('canopy', me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(K.mat(col, 0.8))
    o.data.materials.append(K.mat(col2 or col, 0.8))
    for p in o.data.polygons:
        ii = p.index % seg
        p.material_index = ii % 2
    if par:
        o.parent = par
    return o


# ---------------------------------------------------------------- the basin
def bz(x, y):
    """Ground height of the basin: a flat meadow round the origin, a creek bed, forested slopes rising to peaks."""
    r = math.hypot(x, y * 1.15)
    base = 0.0 if r < 70 else ((r - 70) ** 1.25) * 0.22
    ridges = 0.0 if r < 90 else min(1.0, (r - 90) / 120) * (24 * math.sin(x * 0.011 + 1.1) * math.cos(y * 0.013) + 14 * math.sin(x * 0.027 - y * 0.019))
    roll = 0.25 * math.sin(x * 0.17 + y * 0.09) + 0.2 * math.sin(x * 0.07 - y * 0.21) if r < 70 else 0.0
    return base + max(0.0, ridges) + roll


def creek_x(y):
    return -12 + 7 * math.sin(y * 0.045) + 3 * math.sin(y * 0.11)


def make_basin(S):
    r = keep(empty(BAS))
    xs = list(range(-900, 901, 30))
    field('slopes', xs, xs, lambda x, y: bz(x, y) - 0.05, '3E5A34', r)
    field('meadow', list(range(-80, 81, 4)), list(range(-80, 81, 4)), lambda x, y: bz(x, y) + 0.02 if math.hypot(x, y * 1.15) < 74 else bz(x, y) - 2.0, MEADOW, r)
    for i in range(46):                                                                                      # the creek
        y = -90 + 4 * i
        x = creek_x(y)
        add('cube', '4A7E96', (x, y, bz(x, y) + 0.05), rot=(0, 0, math.atan2(creek_x(y + 4) - x, 4) * -1), scale=(2.6, 4.4, 0.06), size=1, parent=r, rough=0.15)
    for i in range(240):                                                                                     # pines on the slopes
        a = 2 * PI * rnd(i, 1)
        d = 78 + 420 * rnd(i, 2) ** 1.3
        x, y = d * math.cos(a), d * math.sin(a) / 1.15
        z = bz(x, y)
        s = 1.6 + 1.6 * rnd(i, 3)
        add('cone', PINE[i % 3], (x, y, z + 4 * s), radius1=2.2 * s, radius2=0.0, depth=9 * s, vertices=6, parent=r, rough=1.0)
    for i in range(36):                                                                                      # a few pines at the meadow edge, close
        a = 2 * PI * rnd(i, 5)
        d = 52 + 20 * rnd(i, 6)
        x, y = d * math.cos(a), d * math.sin(a) / 1.15
        z = bz(x, y)
        add('cylinder', '4A3426', (x, y, z + 1.5), radius=0.35, depth=3, vertices=6, parent=r)
        for j in range(3):
            add('cone', PINE[(i + j) % 3], (x, y, z + 3.4 + 2.6 * j), radius1=3.0 - 0.7 * j, radius2=0.0, depth=4.6, vertices=7, parent=r, rough=1.0)
    for i in range(90):                                                                                      # grass tufts and flowers near the landing
        x, y = LAND[0] - 14 + 28 * rnd(i, 7), LAND[1] - 10 + 22 * rnd(i, 8)
        if abs(x - LAND[0]) < 1.6 and abs(y - LAND[1]) < 1.6:
            continue
        add('cone', ('6E8A3A', '7E9A44', 'E8D86A', '5E7A36')[i % 4], (x, y, bz(x, y) + 0.3), rot=(0.25 * (rnd(i, 9) - 0.5), 0.2 * (rnd(i, 10) - 0.5), 0),
            radius1=0.14, radius2=0.0, depth=0.6 + 0.4 * rnd(i, 11), vertices=3, parent=r)
    for i in range(12):                                                                                      # boulders by the creek
        y = -30 + 6 * i
        x = creek_x(y) + (3.5 if i % 2 else -3.5)
        o = add('ico_sphere', ('7A7670', '8A847A', '6A665E')[i % 3], (x, y, bz(x, y) + 0.3), scale=(1.0, 0.8, 0.55), radius=0.9 + 0.5 * rnd(i, 12),
                subdivisions=1, parent=r, rough=1.0)
    S['basin'] = r


# ---------------------------------------------------------------- the box, the parachute
def make_box(par=None):
    """The hinged beaver box: two lidless halves fitted together like a suitcase, breathing holes, a rope binding.
    Local: long side along X, hinge along the bottom edge at -Y, closed when 'open' is 0. Origin at the box's base."""
    root = keep(empty(FAR, par))
    L, Wd, Hh = 1.5, 0.74, 0.62
    halves = []
    for side in (-1, 1):
        hinge = empty((0, -Wd / 2 if side > 0 else Wd / 2, 0), root)
        h = empty((0, 0, 0), hinge)
        y0 = Wd / 4 * side                                               # centre of this half relative to its hinge
        add('cube', WOOD if side < 0 else WOOD2, (0, y0, 0.03), scale=(L, Wd / 2, 0.06), size=1, parent=h)                  # floor
        add('cube', WOOD2 if side < 0 else WOOD, (0, y0 - side * (Wd / 4 - 0.03), Hh / 2), scale=(L, 0.06, Hh), size=1, parent=h)    # outer wall
        for ex in (-1, 1):
            add('cube', WOOD, (ex * (L / 2 - 0.03), y0, Hh / 2), scale=(0.06, Wd / 2, Hh), size=1, parent=h)
        add('cube', WOOD2, (0, y0, Hh - 0.03), scale=(L, Wd / 2, 0.06), size=1, parent=h)                                   # top
        for i in range(4):                                                                                                 # breathing holes
            add('cylinder', '1E1610', (-0.5 + i * 0.33, y0 - side * (Wd / 4 + 0.005), Hh * 0.55), rot=(PI / 2, 0, 0), radius=0.07, depth=0.03, vertices=8, parent=h)
        add('cube', ROPE, (0.45, y0, Hh + 0.005), scale=(0.05, Wd / 2 + 0.02, 0.02), size=1, parent=h, rough=1.0)           # rope round
        add('cube', ROPE, (-0.45, y0, Hh + 0.005), scale=(0.05, Wd / 2 + 0.02, 0.02), size=1, parent=h, rough=1.0)
        halves.append((hinge, h, side))
    return dict(root=root, halves=halves, L=L, W=Wd, H=Hh)


def box_open(bx, u, side_mul=1.0):
    """0 closed, 1 both halves fallen flat (outward round their bottom hinges)."""
    for hinge, h, side in bx['halves']:
        hinge.rotation_euler = (side * 1.45 * u * side_mul, 0, 0)


def make_chute(par=None, s=1.0):
    root = keep(empty(FAR, par))
    can = empty((0, 0, 6.2 * s), root)
    dome(CANOPY[0], 3.6 * s, 1.9 * s, can, 14, CANOPY[1])
    add('cylinder', 'FF7A1A', (0, 0, 1.86 * s), radius=0.42 * s, depth=0.08 * s, vertices=10, parent=can, rough=0.7)      # vent band
    lines = []
    for i in range(8):
        b = 2 * PI * (i + 0.5) / 8
        lines.append(bar(root, 'E8E0CC', (3.4 * s * math.cos(b), 3.4 * s * math.sin(b), 6.2 * s), (0.5 * math.cos(b) * 0.9, 0.3 * math.sin(b), 0.65), 0.03, rough=1.0))
    return dict(root=root, can=can, lines=lines)


def chute_pose(ch, loc, sway=0.0, infl=1.0, yaw=0.0):
    """Hang the chute over a box whose base is at loc; infl < 1 squashes the canopy (opening or collapsing)."""
    ch['root'].location = loc
    ch['root'].rotation_euler = (0.0, sway, yaw)
    ch['can'].scale = (lerp(0.25, 1.0, infl), lerp(0.25, 1.0, infl), lerp(2.2, 1.0, infl))


def flat_chute(ch, loc, yaw=0.0, k=1.0):
    """The canopy collapsed on the grass beside its box."""
    ch['root'].location = loc
    ch['root'].rotation_euler = (0.0, 0.0, yaw)
    ch['can'].location = (lerp(0.0, 4.0, k), 0.0, lerp(6.2, 0.18, k))
    ch['can'].rotation_euler = (0.0, lerp(0.0, 1.35, k), 0.0)
    ch['can'].scale = (lerp(1.0, 0.25, k), 1.0, lerp(1.0, 1.2, k))
    for l in ch['lines']:
        l.hide_render = k > 0.3


# ---------------------------------------------------------------- beavers
def make_beaver(fur=FUR, muzzle='8A6A50', s=1.0):
    root = keep(empty(FAR))
    body = empty((0, 0.42, 0.34), root)                       # pivot at the hips so he can sit up
    add('ico_sphere', fur, (0, -0.42, 0.06), scale=(0.5, 0.74, 0.44), radius=1, subdivisions=2, parent=body, rough=1.0)
    add('ico_sphere', BELLY, (0, -0.5, -0.08), scale=(0.38, 0.6, 0.3), radius=1, subdivisions=1, parent=body, rough=1.0)
    head = empty((0, -1.02, 0.22), body)
    add('ico_sphere', fur, (0, -0.1, 0.02), scale=(0.36, 0.4, 0.31), radius=1, subdivisions=2, parent=head, rough=1.0)
    add('ico_sphere', muzzle, (0, -0.4, -0.05), scale=(0.21, 0.17, 0.15), radius=1, subdivisions=1, parent=head, rough=1.0)
    add('cube', '161012', (0, -0.55, 0.02), scale=(0.13, 0.06, 0.07), size=1, parent=head, rough=0.3)                       # nose
    jaw = empty((0, -0.5, -0.13), head)
    add('cube', 'E8862A', (0, -0.02, -0.04), scale=(0.1, 0.035, 0.12), size=1, parent=jaw, rough=0.35)                      # orange incisors
    add('cube', '1A1210', (0, 0.0, 0.03), scale=(0.006, 0.04, 0.12), size=1, parent=jaw)
    eyes = []
    for sd in (-1, 1):
        eyes.append(add('ico_sphere', '0C0A0A', (sd * 0.17, -0.33, 0.12), scale=(1, 0.7, 1), radius=0.06, subdivisions=1, parent=head, rough=0.1))
        add('ico_sphere', 'FFFFFF', (sd * 0.15, -0.375, 0.15), radius=0.016, subdivisions=1, parent=head, emit=2.0)
        add('ico_sphere', FUR2, (sd * 0.22, -0.02, 0.24), scale=(1, 0.6, 1), radius=0.08, subdivisions=1, parent=head, rough=1.0)  # ears
        for w in range(2):
            bar(head, 'E8E0D0', (sd * 0.12, -0.5, -0.04 - 0.04 * w), (sd * 0.42, -0.56, -0.02 - 0.08 * w), 0.008)          # whiskers
    tail = empty((0, 0.22, -0.12), body)
    add('cube', '3A2C26', (0, 0.42, 0), scale=(0.42, 0.74, 0.07), size=1, parent=tail, rough=0.7)
    for i in range(4):
        add('cube', '2C221E', (0, 0.15 + 0.17 * i, 0.04), scale=(0.4, 0.02, 0.01), size=1, parent=tail, rough=0.7)
    feet = []
    for sd in (-1, 1):
        f = empty((sd * 0.28, -0.12, -0.28), body)
        add('cube', '2A2220', (0, -0.1, 0), scale=(0.2, 0.38, 0.08), size=1, parent=f, rough=0.8)
        feet.append(f)
    for sd in (-1, 1):
        f = empty((sd * 0.22, -0.82, -0.24), body)
        add('cylinder', FUR2, (0, 0, 0.06), radius=0.07, depth=0.2, vertices=6, parent=f)
        add('cube', '2A2220', (0, -0.05, -0.04), scale=(0.11, 0.14, 0.06), size=1, parent=f, rough=0.8)
        feet.append(f)
    root.scale = (s, s, s)
    return dict(root=root, body=body, head=head, jaw=jaw, tail=tail, feet=feet, eyes=eyes, s=s)


def bv(b, loc, yaw=0.0, t=0.0, walk=0.0, rear=0.0, chew=0.0, nod=0.0, turn=0.0, tail=0.0, wide=0.0, roll=0.0, pitch=0.0):
    """Pose a beaver: walk (0..1 amount of waddle), rear (sits up on his haunches), chew (teeth go), nod/turn (head),
    tail (lifts the paddle; a slap is tail going up then down), wide (eyes pop)."""
    s = b['s']
    b['root'].location = loc
    b['root'].rotation_euler = (pitch, roll, yaw)
    ph = t * 2 * PI * 2.4
    bob = walk * 0.05 * abs(math.sin(ph))
    b['body'].location = (0, 0.42, 0.34 + bob + 0.12 * rear)
    b['body'].rotation_euler = (-1.05 * rear, walk * 0.08 * math.sin(ph), 0)
    b['head'].rotation_euler = (nod + 0.9 * rear * 0.6 + 0.04 * math.sin(t * 1.7), 0.0, turn + walk * 0.06 * math.sin(ph))
    b['jaw'].rotation_euler = (0.28 * chew * (0.5 + 0.5 * math.sin(t * 34)), 0, 0)
    b['tail'].rotation_euler = (-0.25 + tail + 0.35 * rear, 0, walk * 0.15 * math.sin(ph))
    for i, f in enumerate(b['feet']):
        sd = 1 if i in (0, 3) else -1
        f.location.y = (-0.12 if i < 2 else -0.82) + walk * 0.14 * sd * math.sin(ph)
        f.location.z = (-0.28 if i < 2 else -0.24) + walk * 0.05 * max(0.0, sd * math.cos(ph)) - (0.0 if i < 2 else 0.18 * rear)
        f.rotation_euler = (0.9 * rear if i < 2 else -0.6 * rear, 0, 0)
    for e in b['eyes']:
        e.scale = (1 + 0.5 * wide, 0.7, (1 + 0.5 * wide) * (0.1 if (t * 0.37 + rnd(int(s * 100), 1)) % 1 < 0.03 else 1.0))


# ---------------------------------------------------------------- the plane
def make_plane(S):
    """A generic twin-engine plane, flying along +X. No markings."""
    r = keep(empty(FAR))
    body = '9AA2AA'
    add('cylinder', body, (0, 0, 0), rot=(0, PI / 2, 0), scale=(1.0, 0.92, 1.0), radius=1.15, depth=10.0, vertices=12, parent=r, rough=0.4)
    add('cone', body, (6.0, 0, 0.05), rot=(0, PI / 2, 0), radius1=1.15, radius2=0.35, depth=2.2, vertices=12, parent=r, rough=0.4)          # nose
    add('cone', body, (-7.3, 0, 0.35), rot=(0, -PI / 2, 0), radius1=1.1, radius2=0.18, depth=4.8, vertices=12, parent=r, rough=0.4)         # tail cone
    add('cube', '2A3440', (5.6, 0, 0.62), rot=(0, -0.5, 0), scale=(0.9, 1.5, 0.5), size=1, parent=r, rough=0.1)                           # windscreen
    for i in range(4):
        for sd in (-1, 1):
            add('cube', '2A3440', (2.6 - 1.4 * i, sd * 1.06, 0.35), scale=(0.6, 0.06, 0.42), size=1, parent=r, rough=0.1)                  # windows
    add('cube', '5A6068', (-2.6, -1.07, -0.1), scale=(1.5, 0.05, 1.5), size=1, parent=r, rough=0.6)                                       # cargo door
    add('cube', 'FF7A1A', (0, 0, -0.95), scale=(9.6, 0.5, 0.08), size=1, parent=r, rough=0.6)                                              # belly stripe
    add('cube', body, (1.2, 0, -0.35), scale=(2.6, 19.0, 0.26), size=1, parent=r, rough=0.4)                                             # wing
    S['props'] = []
    for sd in (-1, 1):
        add('cylinder', body, (2.2, sd * 3.8, -0.25), rot=(0, PI / 2, 0), radius=0.62, depth=3.6, vertices=10, parent=r, rough=0.4)
        add('cone', '3A3E44', (4.2, sd * 3.8, -0.25), rot=(0, PI / 2, 0), radius1=0.5, radius2=0.1, depth=0.5, vertices=10, parent=r, rough=0.4)
        hub = empty((4.45, sd * 3.8, -0.25), r)
        for bl in range(3):
            add('cube', '2A2C30', (0, 0, 1.0), rot=(0, 0, 0), scale=(0.05, 0.22, 2.0), size=1, parent=empty((0, 0, 0), hub, (2 * PI * bl / 3, 0, 0)))
        disc = add('cylinder', 'C8CCD0', (0.05, 0, 0), rot=(0, PI / 2, 0), radius=1.95, depth=0.02, vertices=20, parent=hub, alpha=0.12)
        S['props'].append(hub)
    add('cube', body, (-8.6, 0, 0.5), scale=(1.8, 7.0, 0.16), size=1, parent=r, rough=0.4)                                              # stabiliser
    add('cube', body, (-8.8, 0, 1.7), rot=(0, 0.35, 0), scale=(1.8, 0.16, 2.6), size=1, parent=r, rough=0.4)                            # fin
    add('cube', 'FF7A1A', (-9.5, 0, 2.6), rot=(0, 0.35, 0), scale=(0.8, 0.18, 0.5), size=1, parent=r, rough=0.6)
    S['plane'] = r


def plane_at(S, loc, yaw=0.0, bank=0.0, t=0.0, pitch=0.0):
    S['plane'].location = loc
    S['plane'].rotation_euler = (bank, pitch, yaw)
    for i, h in enumerate(S['props']):
        h.rotation_euler = (t * 38 + i, 0, 0)


# ---------------------------------------------------------------- the cargo hold
def make_hold(S):
    """Inside the plane: ribbed walls, a row of beaver boxes strapped down, the open cargo door on the -Y side.
    Built at HOLD; local X along the fuselage."""
    r = keep(empty(HOLD))
    add('cube', '4A4E52', (0, 0, -0.05), scale=(14, 4.6, 0.1), size=1, parent=r, rough=0.7)                                             # floor
    add('cube', '6A7076', (0, 0, 3.3), scale=(14, 4.6, 0.1), size=1, parent=r, rough=0.6)                                                # ceiling
    add('cube', '6A7076', (0, 2.3, 1.6), scale=(14, 0.1, 3.4), size=1, parent=r, rough=0.6)                                             # far wall
    for x0, x1 in ((-7.0, -2.2), (1.2, 7.0)):                                                                                          # near wall either side of the door
        add('cube', '6A7076', ((x0 + x1) / 2, -2.3, 1.6), scale=(x1 - x0, 0.1, 3.4), size=1, parent=r, rough=0.6)
    add('cube', '6A7076', (-0.5, -2.3, 3.05), scale=(3.4, 0.1, 0.6), size=1, parent=r, rough=0.6)                                        # above the door
    add('cube', '6A7076', (-0.5, -2.3, 0.15), scale=(3.4, 0.1, 0.3), size=1, parent=r, rough=0.6)                                        # sill
    for i in range(8):                                                                                                                  # ribs
        x = -6.5 + 1.85 * i
        if -2.4 < x < 1.4:
            continue
        add('cube', '545A60', (x, 2.22, 1.6), scale=(0.16, 0.12, 3.4), size=1, parent=r, rough=0.6)
        add('cube', '545A60', (x, -2.22, 1.6), scale=(0.16, 0.12, 3.4), size=1, parent=r, rough=0.6)
        add('cube', '545A60', (x, 0, 3.22), scale=(0.16, 4.4, 0.12), size=1, parent=r, rough=0.6)
    add('cube', 'FF7A1A', (-0.5, -2.22, 3.3), scale=(3.6, 0.14, 0.12), size=1, parent=r, rough=0.6)                                     # door frame stripe
    S['holdlamp'] = light(at(HOLD, 0.5, 0.6, 3.0), 0, 'FFD6A0', size=3.0)
    S['holdboxes'] = []
    for i in range(6):                                                                                                                  # boxes along the far wall, two rows
        bx = make_box()
        S['holdboxes'].append((bx, at(HOLD, -5.6 + 1.9 * (i % 3) + (0 if i < 3 else 6.0), 1.2, 0.0)))
    S['holdstraps'] = r
    # the mountains far below the hold's door
    m = keep(empty(at(HOLD, 0, 0, -400)))
    for i in range(30):
        a = -PI / 2 + (rnd(i, 61) - 0.5) * 2.4
        d = 300 + 900 * rnd(i, 62)
        add('cone', ('3E5A3A', '4A6646', '566E52', '6E7E6A')[i % 4], (d * math.cos(a), d * math.sin(a), 0), radius1=160 + 120 * rnd(i, 63),
            radius2=0, depth=150 + 160 * rnd(i, 64), vertices=6, parent=m, rough=1.0)
    add('cube', '3E5634', (0, 0, -40), scale=(6000, 6000, 1), size=1, parent=m, rough=1.0)
    S['hold'] = r


# ---------------------------------------------------------------- the lake town
def tz(x, y):
    return 0.0


def cabin(par, x, y, yaw, wall='8A5A3A', roof='4A3A34', s=1.0):
    c = empty((x, y, 0), par, (0, 0, yaw))
    add('cube', wall, (0, 0, 2.0 * s), scale=(8 * s, 6 * s, 4 * s), size=1, parent=c)
    for sd in (-1, 1):
        add('cube', roof, (0, sd * 1.7 * s, 4.9 * s), rot=(sd * 0.62, 0, 0), scale=(8.8 * s, 4.2 * s, 0.25 * s), size=1, parent=c)
    add('cube', 'F2D68A', (-1.8 * s, -3.02 * s, 2.3 * s), scale=(1.4 * s, 0.06, 1.2 * s), size=1, parent=c, emit=0.6)                   # window
    add('cube', '3A2A22', (1.6 * s, -3.02 * s, 1.3 * s), scale=(1.2 * s, 0.06, 2.6 * s), size=1, parent=c)                              # door
    add('cube', '5A4A44', (2.6 * s, 1.2 * s, 5.8 * s), scale=(0.7 * s, 0.7 * s, 1.6 * s), size=1, parent=c)                             # chimney
    return c


def make_town(S):
    r = keep(empty(TOWN))
    add('cube', '6A8A44', (0, 0, -0.5), scale=(900, 900, 1), size=1, parent=r, rough=1.0)                                                # lawns
    add('cube', '3E6E86', (0, 260, -0.2), scale=(900, 420, 0.5), size=1, parent=r, rough=0.12)                                           # Payette Lake
    for i in range(10):                                                                                                                  # mountains over the lake
        add('cone', ('3E5A44', '4A6650', '35503E')[i % 3], (-500 + 110 * i, 520 + 60 * rnd(i, 21), -5), radius1=120 + 60 * rnd(i, 22),
            radius2=0, depth=90 + 70 * rnd(i, 23), vertices=7, parent=r, rough=1.0)
    for i in range(30):                                                                                                                  # pines round the yards
        x = -70 + 140 * rnd(i, 24)
        y = 6 + 40 * rnd(i, 25)
        if -14 < x < 22 and y < 30:
            x += 40 if x > 0 else -40
        add('cylinder', '4A3426', (x, y, 1.5), radius=0.35, depth=3, vertices=6, parent=r)
        for j in range(3):
            add('cone', PINE[(i + j) % 3], (x, y, 3.4 + 2.5 * j), radius1=2.8 - 0.7 * j, radius2=0.0, depth=4.4, vertices=7, parent=r, rough=1.0)
    cabin(r, -6, 30, 0.0)
    cabin(r, 30, 34, -0.3, 'A8744A', '3E3634', 0.9)
    cabin(r, -40, 26, 0.35, '7A6A5A', '4A3A34', 0.85)
    for i in range(13):                                                                                                                  # picket fence
        x = -12 + 2.0 * i
        add('cube', 'E8E2D4', (x, 12, 0.7), scale=(0.18, 0.12, 1.4), size=1, parent=r)
    add('cube', 'E8E2D4', (0, 12, 1.0), scale=(26, 0.1, 0.16), size=1, parent=r)
    add('cube', 'E8E2D4', (0, 12, 0.4), scale=(26, 0.1, 0.16), size=1, parent=r)
    # the gnawed tree in the yard: a trunk with the hourglass notch, and the fallen top
    tr = S['tree'] = empty((-2.0, 4.0, 0), r)
    add('cylinder', '6A4E36', (0, 0, 0.25), radius=0.6, depth=0.5, vertices=8, parent=tr)
    add('cone', 'D8B888', (0, 0, 0.68), radius1=0.6, radius2=0.18, depth=0.36, vertices=8, parent=tr)                                   # the chewed waist
    top = S['treetop'] = empty((0, 0, 0.88), tr)
    add('cone', 'D8B888', (0, 0, 0.18), radius1=0.18, radius2=0.6, depth=0.36, vertices=8, parent=top)
    add('cylinder', '6A4E36', (0, 0, 3.4), radius=0.55, depth=6.0, vertices=8, parent=top)
    for j in range(4):
        add('ico_sphere', ('4E7A36', '5A8A40', '467034')[j % 3], (0.6 * math.sin(j * 2), 0.6 * math.cos(j * 2), 6.5 + 1.0 * j), scale=(1.4, 1.4, 1.1),
            radius=1.6 - 0.25 * j, subdivisions=1, parent=top, rough=1.0)
    S['chips'] = [keep(add('cube', 'E8CFA0', FAR, scale=(0.12, 0.08, 0.03), size=1, rough=1.0)) for _ in range(14)]
    # the flooded yard: a lawn under a sheet of water behind a little stick dam across the ditch
    fy = S['flood'] = empty((22.0, -6.0, 0), r)
    S['floodwater'] = add('cube', '5A8AA0', (0, 0, 0.05), scale=(14, 10, 0.1), size=1, parent=fy, rough=0.08)
    for i in range(16):
        a = rnd(i, 26)
        bar(fy, ('6A5038', '7A5E42', '5A4430')[i % 3], (-7.2 + 0.9 * i, -5.4 + 0.3 * a, 0.2 + 0.25 * (i % 2)), (-6.6 + 0.9 * i, -5.0 - 0.3 * a, 0.5), 0.1)
    add('cube', 'E8E2D4', (6.4, 3.0, 0.6), scale=(0.4, 0.4, 1.2), size=1, parent=fy)                                                    # a birdbath, up to its knees
    add('cylinder', 'E8E2D4', (6.4, 3.0, 1.3), radius=0.6, depth=0.15, vertices=10, parent=fy)
    add('cube', 'A87A4A', (-3.0, 3.0, 0.3), scale=(1.2, 0.5, 0.6), size=1, parent=fy)                                                    # a garden bench, awash
    # the corral for the mule
    co = S['corral'] = empty((-34.0, -8.0, 0), r)
    add('cube', 'B8A07A', (0, 0, 0.02), scale=(16, 12, 0.04), size=1, parent=co, rough=1.0)
    for i in range(9):
        for sd in (-1, 1):
            add('cube', '7A5A3E', (-8 + 2 * i, sd * 6, 0.9), scale=(0.2, 0.2, 1.8), size=1, parent=co)
        add('cube', '7A5A3E', (-8 + 2 * i, 6, 1.5), scale=(2.0, 0.12, 0.16), size=1, parent=co)
    S['town'] = r


# ---------------------------------------------------------------- the mule
def make_mule(S):
    r = keep(empty(FAR))
    body = empty((0, 0, 2.3), r)
    add('ico_sphere', '6A5A4E', (0, 0, 0), scale=(0.9, 2.0, 0.95), radius=1, subdivisions=2, parent=body, rough=1.0)
    neck = empty((0, -1.7, 0.5), body)
    add('cylinder', '6A5A4E', (0, -0.4, 0.6), rot=(-0.7, 0, 0), radius=0.45, depth=1.7, vertices=8, parent=neck)
    hd = empty((0, -0.9, 1.3), neck)
    add('ico_sphere', '6A5A4E', (0, -0.5, -0.1), rot=(0.5, 0, 0), scale=(0.5, 1.1, 0.5), radius=1, subdivisions=1, parent=hd, rough=1.0)
    add('ico_sphere', 'B8A898', (0, -1.3, -0.45), scale=(0.42, 0.45, 0.38), radius=1, subdivisions=1, parent=hd, rough=1.0)              # pale muzzle
    ears = []
    for sd in (-1, 1):
        e = empty((sd * 0.25, -0.1, 0.4), hd)
        add('cone', '5A4A40', (0, 0, 0.55), radius1=0.18, radius2=0.0, depth=1.2, vertices=5, parent=e)
        ears.append(e)
        add('ico_sphere', 'FFFFFF', (sd * 0.38, -0.65, 0.05), radius=0.12, subdivisions=1, parent=hd, emit=0.3)
        add('ico_sphere', '0C0A0A', (sd * 0.43, -0.7, 0.05), radius=0.07, subdivisions=1, parent=hd)
    legs = []
    for fx, fy in ((-0.5, -1.3), (0.5, -1.3), (-0.5, 1.3), (0.5, 1.3)):
        l = empty((fx, fy, -0.5), body)
        add('cylinder', '5A4A40', (0, 0, -0.85), radius=0.2, depth=1.7, vertices=6, parent=l)
        add('cylinder', '1E1814', (0, 0, -1.75), radius=0.24, depth=0.2, vertices=6, parent=l)
        legs.append(l)
    tail = empty((0, 1.95, 0.4), body)
    add('cylinder', '3A302A', (0, 0.1, -0.7), rot=(0.3, 0, 0), radius=0.1, depth=1.4, vertices=5, parent=tail)
    add('cube', '8A6A44', (0, -0.1, 0.9), scale=(1.5, 1.6, 0.3), size=1, parent=body)                                                   # pack saddle
    S['mulebox'] = mb = make_box(body)
    mb['root'].location, mb['root'].rotation_euler = (1.25, 0.0, 0.2), (0, -0.25, PI / 2)
    S['mule'] = dict(root=r, body=body, neck=neck, head=hd, ears=ears, legs=legs, tail=tail)


def mule_pose(S, loc, yaw, t, buck=0.0, ears=0.0, walk=0.0):
    m = S['mule']
    m['root'].location, m['root'].rotation_euler = loc, (0, 0, yaw)
    kick = buck * max(0.0, math.sin(t * 9))
    m['body'].rotation_euler = (-0.45 * kick, 0.08 * buck * math.sin(t * 7), 0)
    m['body'].location.z = 2.3 + 0.6 * kick
    m['neck'].rotation_euler = (0.5 * kick - 0.2 * buck, 0, 0.3 * buck * math.sin(t * 5))
    for i, e in enumerate(m['ears']):
        e.rotation_euler = (1.1 * ears, (-1, 1)[i] * 0.4 * ears, 0)
    for i, l in enumerate(m['legs']):
        if i >= 2:
            l.rotation_euler = (-1.0 * kick + walk * 0.4 * math.sin(t * 6 + i * PI), 0, 0)
        else:
            l.rotation_euler = (0.3 * kick + walk * 0.4 * math.sin(t * 6 + i * PI + PI / 2), 0, 0)
    m['tail'].rotation_euler = (-0.6 * kick + 0.15 * math.sin(t * 3), 0, 0.3 * math.sin(t * 4))


# ---------------------------------------------------------------- the landing field
def make_field(S):
    r = keep(empty(FLD))
    add('cube', '8AA058', (0, 0, -0.5), scale=(2000, 2000, 1), size=1, parent=r, rough=1.0)
    add('cube', 'A8B070', (0, 0, 0.01), scale=(600, 26, 0.02), size=1, parent=r, rough=1.0)                                              # the strip, mown
    for i in range(12):
        add('cone', ('4E6A50', '5A7458', '465E48')[i % 3], (-600 + 110 * i, 520 + 80 * rnd(i, 31), -5), radius1=150 + 70 * rnd(i, 32),
            radius2=0, depth=110 + 70 * rnd(i, 33), vertices=7, parent=r, rough=1.0)
    hg = empty((-18, 36, 0), r)                                                                                                          # the hangar
    add('cube', '8A8A82', (0, 0, 2.5), scale=(16, 12, 5), size=1, parent=hg)
    add('cylinder', '7A7A74', (0, 0, 5.0), rot=(PI / 2, 0, 0), scale=(1.0, 0.45, 1.0), radius=8.0, depth=12.0, vertices=16, parent=hg)
    add('cube', '2A2A2C', (0, -6.02, 2.8), scale=(10, 0.1, 5.4), size=1, parent=hg)
    pole = empty((14, 20, 0), r)                                                                                                         # windsock
    add('cylinder', 'D8D8D0', (0, 0, 3.5), radius=0.12, depth=7, vertices=6, parent=pole)
    S['sock'] = add('cone', 'FF7A1A', (0, 1.4, 6.8), rot=(PI / 2, 0, 0), radius1=0.55, radius2=0.25, depth=2.8, vertices=10, parent=pole, rough=0.8)
    add('cube', '6A5A3E', (4, 10, 0.5), scale=(2.2, 1.6, 1.0), size=1, parent=r)                                                         # a crate of chutes
    for i in range(3):
        add('ico_sphere', '6A6A44', (3.4 + 0.6 * i, 10 + 0.3 * (i - 1), 1.25), scale=(0.6, 0.45, 0.35), radius=1, subdivisions=1, parent=r)
    S['fieldx'] = r


# ---------------------------------------------------------------- the dam and the lodge, a year later
def make_dam(S):
    """A year later on the creek: a stick dam backing up a pond, and a lodge in the pond. Built in the basin, upstream."""
    r = keep(empty((creek_x(40), 40, bz(creek_x(40), 40))))
    add('cylinder', '4A7E96', (0, 7, 0.25), scale=(1.4, 1.0, 1.0), radius=9, depth=0.1, vertices=18, parent=r, rough=0.08)              # the pond
    for i in range(26):                                                                                                                  # the dam
        a = rnd(i, 41)
        x = -9 + 0.72 * i
        bar(r, ('6A5038', '7A5E42', '5A4430', '8A6A4A')[i % 4], (x, -1.6 + 0.6 * a, 0.2 + 0.3 * (i % 3)), (x + 0.9, -1.0 - 0.5 * a, 0.9 + 0.2 * (i % 2)), 0.13)
    add('cone', '6A5640', (0, -1.3, 0.35), scale=(1.0, 0.24, 1.0), radius1=10.5, radius2=8.5, depth=0.9, vertices=14, parent=r, rough=1.0)   # mud
    lodge = empty((3.5, 8.0, 0), r)
    add('cone', '5E4A36', (0, 0, 1.0), radius1=3.2, radius2=0.6, depth=2.4, vertices=9, parent=lodge, rough=1.0)
    for i in range(18):
        b = 2 * PI * i / 18
        bar(lodge, ('6A5038', '7A5E42', '5A4430')[i % 3], (3.0 * math.cos(b), 3.0 * math.sin(b), 0.1), (0.5 * math.cos(b + 0.4), 0.5 * math.sin(b + 0.4), 2.2), 0.1)
    S['dam'] = r
    S['lodge'] = lodge


# ---------------------------------------------------------------- people
def heter_head(head):
    d = K.human_head('E2B08C', '5A4030')(head)
    add('cylinder', '6A5236', (0, 0.02, 0.27), radius=0.46, depth=0.04, vertices=12, parent=head)                                        # wide-brim field hat
    add('cone', '6A5236', (0, 0.02, 0.42), radius1=0.29, radius2=0.22, depth=0.28, vertices=8, parent=head)
    add('cylinder', '3A2C20', (0, 0.02, 0.32), radius=0.295, depth=0.05, vertices=8, parent=head)
    return d


def cap_head(skin, hair, cap):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('ico_sphere', cap, (0, 0.04, 0.2), scale=(1.0, 1.05, 0.6), radius=0.32, subdivisions=1, parent=head)
        add('cube', cap, (0, -0.32, 0.17), rot=(-0.2, 0, 0), scale=(0.44, 0.3, 0.03), size=1, parent=head)
        return d
    return fn


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    _PROTO.clear()
    _LAST[0] = None
    K.add, K.empty = add, empty
    S = {}
    make_basin(S)
    make_dam(S)
    make_plane(S)
    make_hold(S)
    make_town(S)
    make_mule(S)
    make_field(S)
    S['box'] = make_box()
    S['box2'] = make_box()
    S['chute'] = make_chute()
    S['chute2'] = make_chute()
    S['chutes'] = [make_chute(s=0.8) for _ in range(5)]
    S['boxes'] = [make_box() for _ in range(5)]
    S['geronimo'] = make_beaver(FUR, 'B8A894', 1.0)                      # an old beaver: a grey muzzle
    S['beavers'] = [make_beaver(c, m, s) for c, m, s in (('7A5236', '9A7A5A', 0.9), ('5E4030', '8A6A50', 0.88), ('6E4A34', '9A7A5E', 0.86),
                                                          (FUR2, '8A6A50', 0.95))]
    S['all_beavers'] = [S['geronimo']] + S['beavers']
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['heter'] = he = K.Rig(dict(top='B8A47A', pants='5A5A3A', hand='E2B08C', boot='3A2A1E', fore='B8A47A'), heter_head)
    add('cube', '8A7A4E', (0.18, -0.34, 1.0), scale=(0.14, 0.04, 0.16), size=1, parent=he.body)                                         # shirt pocket
    S['hand'] = K.Rig(dict(top='4A5A7A', pants='3A3A44', hand='D8A884', boot='2A2018', fore='4A5A7A'), cap_head('D8A884', '3A2A20', '8A3A2E'))
    S['towny'] = K.Rig(dict(top='A04A3A', pants='3E4A5A', hand='E6B896', boot='1E1A18', fore='A04A3A'), K.human_head('E6B896', 'B8B4AC'))
    S['humans'] = [he, S['hand'], S['towny']]
    S['cast_all'] = [S['rook']] + S['humans']
    # Rook's props
    S['mag'] = keep(empty(FAR))
    add('torus', 'C89A3A', (0, 0, 0), rot=(PI / 2, 0, 0), major_radius=0.22, minor_radius=0.03, major_segments=14, minor_segments=4, parent=S['mag'], rough=0.3)
    add('cylinder', 'D8F0FF', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.21, depth=0.01, vertices=14, parent=S['mag'], rough=0.05, alpha=0.25)
    add('cylinder', '3A2A1E', (0, 0, -0.42), radius=0.035, depth=0.42, vertices=6, parent=S['mag'])
    S['pad'] = keep(empty(FAR))
    add('cube', 'F2ECD8', (0, 0, 0), scale=(0.5, 0.04, 0.66), size=1, parent=S['pad'], rough=0.8)
    add('cube', 'FF7A1A', (0, 0.0, 0.34), scale=(0.52, 0.06, 0.06), size=1, parent=S['pad'], rough=0.6)
    S['marks'] = [add('cube', '22202A', (-0.16 + 0.08 * i if i < 4 else 0.0, -0.03, -0.05), rot=(0, 0, 0 if i < 4 else 1.1),
                      scale=(0.025, 0.01, 0.3 if i < 4 else 0.42), size=1, parent=S['pad']) for i in range(5)]
    S['ring'] = keep(add('torus', 'D8DCE0', FAR, rot=(PI / 2, 0, 0), major_radius=0.13, minor_radius=0.03, major_segments=12, minor_segments=4, rough=0.15, emit=0.4))
    S['feather'] = keep(add('cone', '2F2B4D', FAR, scale=(0.35, 0.1, 1.0), radius1=0.25, radius2=0.0, depth=0.8, vertices=4))
    S['lead'] = keep(bar(None, 'C8B890', FAR, plus(FAR, (0, 0, 1)), 0.05, rough=1.0))
    S['glint'] = light(FAR, 0, 'FFF4E0', kind='POINT')
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    S['sun'].data.angle = 0.06
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 12000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w42')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.05, 0.55
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs[2], mr.inputs[0])
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(mx.outputs[2], S['bg'].inputs[0])
    S['skymix'] = mx
    reset(S)
    return S


def reset(S):
    for rig in S['cast_all']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for l in (S['sun'], S['glint'], S['holdlamp']):
        l.data.energy = 0
    for bx in [S['box'], S['box2'], S['mulebox']] + S['boxes'] + [b for b, _ in S['holdboxes']]:
        box_open(bx, 0.0)
    S['mulebox']['root'].location, S['mulebox']['root'].rotation_euler = (1.25, 0.0, 0.2), (0, -0.25, PI / 2)
    for ch in [S['chute'], S['chute2']] + S['chutes']:
        ch['can'].location, ch['can'].rotation_euler, ch['can'].scale = (0, 0, 6.2 * (0.8 if ch in S['chutes'] else 1.0)), (0, 0, 0), (1, 1, 1)
        for l in ch['lines']:
            l.hide_render = False
    for b in S['all_beavers']:
        bv(b, FAR)
    S['treetop'].rotation_euler = (0, 0, 0)
    S['plane'].location = FAR
    for m in S['marks']:
        m.hide_render = True
    S['floodwater'].location.z = 0.05
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, hat_to=(0.15, -0.55, -1.0), laugh=0.0, hat_drop=0.0)
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinking and beak lip sync, once the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.43) % 1 < 0.035
    lg = S['laugh']
    ez = dict(calm=0.07, low=0.042, shocked=0.135, sad=0.055, soft=0.06, laugh=0.02, squint=0.035).get(e, 0.07)
    tilt = dict(low=-0.06, shocked=0.36, sad=0.45, soft=0.22, laugh=0.3, squint=-0.3).get(e, -0.22)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], sm(S['hat_off'])
    to = S['hat_to']
    r['hat'].rotation_euler = (lerp(-0.2 + tip * 0.38, 0.2, off), lerp(0.07, 1.25, off), 0)
    dr = S.get('hat_drop', 0.0)
    r['hat'].location = (lerp(0.0, to[0], off), lerp(-0.08 * dr, to[1], off), lerp(0.27 + S['hat_jump'] + tip * 0.1 - 0.3 * dr, to[2], off))
    r['hat'].rotation_euler.x += 0.25 * dr
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.36 if e == 'shocked' else 0.0) + lg * (0.45 + 0.15 * math.sin(t * 26)), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0) + lg * 0.12 * math.sin(t * 26), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.8, shut=0.07, tired=0.45, warm=0.8, sad=0.55, pain=0.35, hard=0.6, proud=0.75).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.045 if f in ('wide', 'proud') else -0.02 if f in ('hard', 'tired', 'pain') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide', 'pain') else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.2 if f in ('warm', 'proud') else 0.13, 0.03, 0.035 + 0.14 * rig.jawv + (0.05 if f in ('wide', 'pain') else 0))
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sky(S, name):
    A = SKIES[name]
    S['skymix'].inputs[6].default_value = K.hexc(A[0])
    S['skymix'].inputs[7].default_value = K.hexc(A[1])
    S['bg'].inputs[1].default_value = A[2]
    S['sun'].data.energy = A[3]
    S['sun'].data.color = K.hexc(A[4])[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(v * 500 for v in A[5])


def cam(S, pos, look, lens=35, roll=0.0):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


def stand(rig, loc, yaw=0.0, pose=None, face=None):
    rig.place(loc, yaw)
    rig.apply(pose or P())
    if face:
        rig.face = face
    return rig


def on(x, y, dz=0.0):
    """A point on the basin's ground."""
    return (x, y, bz(x, y) + dz)


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def head(rig):
    return wpos(rig.head)


def hand_of(rig, i=1):
    return wpos(rig.el[i], (0, -0.08, -0.62))


DROP0 = (-60.0, 30.0, 180.0)        # where the hero box is when the hook starts


def drop_pos(u):
    """The hero box's path down to the meadow (u from 0 high to 1 on the grass)."""
    g = on(*LAND)
    return (lerp(DROP0[0], g[0], u), lerp(DROP0[1], g[1], u), lerp(DROP0[2], g[2], u))


def peek(S, bx, b, t, out=0.25, yaw_box=0.0):
    """A beaver inside the box with his nose at a breathing hole (the box's -Y wall)."""
    p = wpos(bx['root'], (-0.17, 0.15, 0.08))
    bv(b, p, yaw_box, t, nod=0.04 * math.sin(t * 3), turn=0.05 * math.sin(t * 2.3), tail=1.3, wide=0.6)
    b['root'].scale = (0.45, 0.45, 0.45)


# ---------------------------------------------------------------- hook: the drop
def drop_close(S, k, t, lt):
    """Right beside the falling box: the canopy above snaps open with a jolt, a beaver's nose and eyes at a breathing
    hole, the mountains and the meadow far below. First shot; the loop's last shot returns to this framing."""
    sky(S, 'high')
    loop = S['prm'].get('loop')
    jolt = 0.0 if loop else max(0.0, lt - 0.15)
    infl = 1.0 if loop else sm(jolt / 0.25) * (1 + 0.12 * math.sin(jolt * 30) * math.exp(-jolt * 6))
    bxp = (DROP0[0], DROP0[1], DROP0[2] - (2.0 * lt if loop else (1.2 * lt + 0.8 * (1 - math.exp(-jolt * 8)))))
    bx = S['box']
    bx['root'].location = bxp
    sway = 0.12 * math.sin(t * 2.2) + (0.0 if loop else 0.25 * math.exp(-jolt * 4) * math.sin(jolt * 12))
    bx['root'].rotation_euler = (0, sway * 0.6, 0.3)
    chute_pose(S['chute'], bxp, sway * 0.4, max(0.05, infl), 0.3)
    peek(S, bx, S['geronimo'], t, yaw_box=0.3)
    c = plus(bxp, (2.5, -3.4, -0.5 + (0 if loop else 0.5 * math.exp(-jolt * 5))))
    cam(S, c, plus(bxp, (0.0, 0.0, 2.3)), 22)


def drop_wide(S, k, t, lt):
    """Wide over the basin: the plane banks away; the box swings under its canopy, other canopies blossoming below
    it over the meadow."""
    sky(S, 'high')
    u = 0.06 + 0.05 * k
    bxp = drop_pos(u)
    S['box']['root'].location = bxp
    S['box']['root'].rotation_euler = (0, 0.1 * math.sin(t * 2), 0.3)
    chute_pose(S['chute'], bxp, 0.08 * math.sin(t * 2), 1.0, 0.3)
    plane_at(S, (lerp(-10, 60, k), 70, 205 + 4 * k), 0.35, -0.35, t)
    for i, (ch, bx) in enumerate(zip(S['chutes'], S['boxes'])):
        p = (DROP0[0] + 14 + 9 * i, DROP0[1] + 8 - 6 * i, DROP0[2] - 26 - 16 * i - 6 * lt)
        bx['root'].location = p
        bx['root'].rotation_euler = (0, 0.1 * math.sin(t * 2 + i), i)
        chute_pose(ch, p, 0.1 * math.sin(t * 2 + i), 1.0, i)
    cam(S, (DROP0[0] - 24, DROP0[1] - 36, DROP0[2] + 14 - 3 * k), (DROP0[0] + 8, DROP0[1] + 4, DROP0[2] - 30), 26)


def hole_close(S, k, t, lt):
    """Inside the drop, very close: the beaver's whiskered face at the breathing hole, the ground turning far below."""
    sky(S, 'high')
    u = 0.2 + 0.1 * k
    bxp = drop_pos(u)
    bx = S['box']
    bx['root'].location = bxp
    bx['root'].rotation_euler = (0, 0.15 * math.sin(t * 2.4), 0.3 + 0.2 * k)
    chute_pose(S['chute'], bxp, 0.1 * math.sin(t * 2.4), 1.0, 0.3 + 0.2 * k)
    b = S['geronimo']
    peek(S, bx, b, t, yaw_box=0.3 + 0.2 * k)
    b['jaw'].rotation_euler = (0.18 + 0.1 * math.sin(t * 9), 0, 0)
    hp = wpos(b['head'], (0, -0.5, 0))
    yb = 0.3 + 0.2 * k
    fwd = (math.sin(yb), -math.cos(yb), 0)
    cam(S, plus(plus(hp, fwd, 1.3 + 0.3 * (1 - k)), (0.3, 0, 0.8)), plus(hp, (0, 0, -0.25)), 30, roll=0.05 * math.sin(t * 2.4))


# ---------------------------------------------------------------- doubt
def rook_box_ride(S, k, t, lt):
    """Rook sits on top of the swinging box, arms crossed, hat brim low, coat flapping, the canopy over him and the
    mountains below: 'A flying beaver? Please.' The beaver's nose pokes out under his boots."""
    sky(S, 'high')
    u = 0.32 + 0.06 * k
    bxp = drop_pos(u)
    bx = S['box']
    sway = 0.1 * math.sin(t * 2.0)
    bx['root'].location = bxp
    bx['root'].rotation_euler = (0, sway, 0.3)
    chute_pose(S['chute'], bxp, sway * 0.6, 1.0, 0.3)
    peek(S, bx, S['geronimo'], t, yaw_box=0.3)
    rk = S['rook']
    top = wpos(bx['root'], (0.1, 0.0, bx['H']))
    pose = P('sit', aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), head=(0.12 - 0.2 * sm((k - 0.6) / 0.2), 0.0))
    stand(rk, plus(top, (0, 0, -0.55)), 0.3 + 0.0, pose)
    rk.root.rotation_euler = (0, sway, 0.3)
    S['rface'] = 'low' if k < 0.62 else 'squint'
    S['hat_tip'] = 0.85 if k < 0.62 else 0.4
    h = head(rk)
    cam(S, plus(h, (0.9 * math.sin(0.3) - 1.0, -4.6, -0.9)), plus(h, (0.0, 0.0, -0.75)), 28, roll=-0.4 * sway)


# ---------------------------------------------------------------- land
def meadow_land(S, k, t, lt):
    """Low in the meadow grass: the box comes down out of the sky and thumps in, the canopy sagging over behind it."""
    sky(S, 'meadow')
    g = on(*LAND)
    tl = 0.4                                     # touchdown at 40% of the shot
    u = k / tl
    bx = S['box']
    if u < 1:
        p = (g[0], g[1], g[2] + 9 * (1 - u))
        bx['root'].location = p
        bx['root'].rotation_euler = (0, 0.1 * math.sin(t * 2), 0.3)
        chute_pose(S['chute'], p, 0.06 * math.sin(t * 2), 1.0, 0.3)
    else:
        v = (k - tl) / (1 - tl)
        bounce = 0.25 * math.exp(-v * 7) * abs(math.sin(v * 14))
        bx['root'].location = plus(g, (0, 0, bounce))
        bx['root'].rotation_euler = (0, 0.04 * math.exp(-v * 6) * math.sin(v * 20), 0.3)
        flat_chute(S['chute'], g, 0.3 + PI, sm(v / 0.8))
    cam(S, on(LAND[0] - 2.4, LAND[1] - 7.5, 0.55), plus(g, (0.5, 0, 2.2 + 1.8 * (1 - sm(k / 0.5)))), 22)


def box_open_shot(S, k, t, lt):
    """The box's halves spring apart and flop onto the grass; the beaver blinks in the light, shakes, and waddles out
    towards the creek."""
    sky(S, 'meadow')
    g = on(*LAND)
    bx = S['box']
    bx['root'].location, bx['root'].rotation_euler = g, (0, 0, 0.3)
    op = sm(k / 0.18)
    box_open(bx, op * (1 + 0.08 * math.sin(k * 30) * math.exp(-k * 8)))
    flat_chute(S['chute'], g, 0.3 + PI, 1.0)
    b = S['geronimo']
    w = sm((k - 0.35) / 0.2)
    yaw = 0.3
    p = plus(g, (lerp(0.0, -2.6, sm((k - 0.35) / 0.65)), lerp(0.0, -1.6, sm((k - 0.35) / 0.65)), 0.06))
    shake = 0.25 * math.sin(lt * 30) * (sm((k - 0.2) / 0.05) - sm((k - 0.33) / 0.05))
    bv(b, p, lerp(yaw, -1.02, w) + shake, t, walk=w, nod=-0.1, turn=0.3 * (1 - w) * math.sin(t * 3), wide=0.8 * (1 - w))
    cam(S, plus(g, (-1.0, -6.4, 1.6)), plus(g, (-0.9, -0.6, 0.45)), 26)


def rook_land(S, k, t, lt):
    """Rook drops in beside the open box on his own wings, lands in a crouch, and stares after the beaver waddling off;
    his hat hops."""
    sky(S, 'meadow')
    g = on(*LAND)
    bx = S['box']
    bx['root'].location, bx['root'].rotation_euler = g, (0, 0, 0.3)
    box_open(bx, 1.0)
    flat_chute(S['chute'], g, 0.3 + PI, 1.0)
    rk = S['rook']
    dn = sm(k / 0.35)
    p = plus(g, (1.8, -1.2, 3.0 * (1 - dn)))
    crouch = (1 - sm((k - 0.35) / 0.25)) * dn
    pose = blend(P('up', aL=(1.6, 1.4, 0.2), aR=(1.6, 1.4, 0.2), lL=(0.4, 0.8), lR=(0.4, 0.8)), P('stand', lL=(0.5, 1.0), lR=(0.5, 1.0), lift=-0.4, lean=0.3), dn)
    pose = blend(pose, P('point', aR=(1.35, 0.35, 0.05), head=(0.05, 0.6)), sm((k - 0.55) / 0.2))
    if crouch > 0.1 and k > 0.35:
        pose['lift'] = -0.4 * crouch
    stand(rk, p, -0.6, pose)
    S['rface'] = 'shocked' if 0.35 < k < 0.6 else 'squint'
    S['hat_jump'] = 0.45 * sm((k - 0.35) / 0.06) * (1 - sm((k - 0.45) / 0.1))
    b = S['geronimo']
    bv(b, plus(g, (-2.4 - 2.0 * k, -2.4 - 1.2 * k, 0.06)), -1.03, t, walk=1.0)
    h = head(rk)
    cam(S, plus(g, (4.6, -6.8, 2.0)), plus(g, (0.6, -1.4, 1.6)), 26)


# ---------------------------------------------------------------- why: the lake town
def town_tree(S, k, t, lt):
    """A town yard by the lake: a beaver gnaws the last of a trunk; chips fly; the tree creaks over onto the picket fence."""
    sky(S, 'town')
    tp = S['tree'].location
    base = at(TOWN, tp[0], tp[1], 0)
    b = S['beavers'][3]
    fall = sm((k - 0.45) / 0.4) ** 1.6
    S['treetop'].rotation_euler = (-1.25 * fall, 0, 0)
    bv(b, at(base, 0.0, -1.75, 0), PI, t, rear=0.35, chew=1.0 - sm((k - 0.45) / 0.1), nod=0.1, wide=1.0 * sm((k - 0.45) / 0.1))
    if k > 0.5:                                  # he scoots back as it goes
        bv(b, at(base, 0.6 * sm((k - 0.5) / 0.2), -1.35 - 1.6 * sm((k - 0.5) / 0.2), 0), 0.4 * sm((k - 0.5) / 0.2), t, walk=1.0 - sm((k - 0.75) / 0.1), wide=1.0)
    for i, c in enumerate(S['chips']):
        a = (lt * 1.6 + i / 14) % 1
        if k > 0.5:
            c.location = FAR
            continue
        c.location = at(base, 0.5 * math.cos(i * 2.1) * a * 2, -0.6 - 0.8 * a, 0.7 + 1.2 * a - 2.4 * a * a)
        c.rotation_euler = (a * 9, a * 7, i)
    cam(S, at(base, 5.2, -3.6, 1.4), at(base, 0.0, -0.6, 1.1 + 1.8 * fall), 24)


def town_flood(S, k, t, lt):
    """The yard next door under a sheet of water behind a stick dam; the owner in his slippers stands at the edge,
    hands on hips, and the water creeps over his toes."""
    sky(S, 'town')
    fy = S['flood'].location
    S['floodwater'].location.z = 0.05 + 0.06 * k
    tw = S['towny']
    p = (fy[0] - 2.0, fy[1] - 5.4, 0.0)
    stand(tw, p, 0.4, P('hips', head=(0.25 + 0.1 * math.sin(t * 1.3), 0.15 * math.sin(t * 0.9))), 'hard')
    if k > 0.55:
        tw.apply(P('hips', lL=(0.5, 0.6), head=(0.4, 0.0)))
        tw.face = 'wide'
    b = S['beavers'][0]
    bv(b, (fy[0] + 1.5, fy[1] - 5.6, 0.1), -1.4, t, walk=0.0, rear=0.8, chew=0.3, turn=0.3 * math.sin(t * 2))
    cam(S, (fy[0] + 5.0 - 1.2 * k, fy[1] - 13.0, 2.6), (fy[0] - 0.2, fy[1] - 3.6, 1.4), 26)


def rook_flood(S, k, t, lt):
    """Rook ankle-deep in the flooded lawn lifts one dripping boot, shakes it, and gives the beaver on the stick dam a
    flat look; the beaver looks back."""
    sky(S, 'town')
    fy = S['flood'].location
    S['floodwater'].location.z = 0.12
    rk = S['rook']
    lift = sm((k - 0.15) / 0.2) * (1 - sm((k - 0.75) / 0.15))
    pose = P('hips', lR=(0.9 * lift, 1.4 * lift), head=(0.35 * lift, -0.4 * sm((k - 0.6) / 0.15)), lean=-0.05)
    stand(rk, (fy[0] + 0.5, fy[1] - 2.0, -0.05), 0.3, pose)
    rk.root.rotation_euler = (0, 0, 0.3 + 0.03 * math.sin(lt * 30) * lift)
    S['rface'] = 'squint'
    S['hat_tip'] = 0.55
    b = S['beavers'][0]
    bv(b, (fy[0] - 2.6, fy[1] - 5.2, 0.55), -0.9, t, rear=0.7, nod=-0.1, turn=0.2 * math.sin(t * 1.5))
    h = head(rk)
    cam(S, plus(h, (-1.8, -5.6, -1.0)), plus(h, (-1.0, -0.8, -1.2)), 26)


# ---------------------------------------------------------------- mules
def mule_load(S, k, t, lt):
    """In the corral: Heter heaves a beaver box up onto the mule's pack saddle; the box jolts as the beavers inside
    shift, and the mule's ears swivel back."""
    sky(S, 'town')
    co = S['corral'].location
    mule_pose(S, (co[0], co[1], 0), -PI / 2 + 0.2, t, buck=0.0, ears=sm((k - 0.45) / 0.2))
    mb = S['mulebox']
    up = sm(k / 0.45)
    he = S['heter']
    hp = (co[0] - 0.4, co[1] - 2.6, 0)
    lift = P('reach', aL=(2.6, 0.2, 0.3), aR=(2.6, -0.2, 0.3), head=(-0.2, 0.0))
    stand(he, hp, PI + 0.1, blend(P('brace', aL=(1.4, 0.2, 0.8), aR=(1.4, -0.2, 0.8)), lift, up), 'hard')
    if up < 0.99:
        final = wpos(S['mule']['body'], (1.25, 0.0, 0.2))
        mb['root'].parent = None
        mb['root'].location = tuple(lerp(x0, x1, up) for x0, x1 in zip(plus(hp, (0.0, 0.7, 1.7)), final))
        mb['root'].rotation_euler = (0, -0.25 * up, -PI / 2 + 0.2 + PI / 2)
    jolt = 0.12 * math.sin(lt * 26) * (sm((k - 0.55) / 0.05) - sm((k - 0.75) / 0.1))
    mb['root'].rotation_euler.y += jolt
    cam(S, (co[0] + 2.0, co[1] - 9.5, 3.0), (co[0] - 0.3, co[1] - 0.6, 3.0), 26)


def mule_buck(S, k, t, lt):
    """The mule bucks, back legs kicking, ears flat, the box on its back jolting; Heter hangs on to the lead rope and
    gets towed off his feet."""
    sky(S, 'town')
    co = S['corral'].location
    b = sm(k / 0.15)
    mule_pose(S, (co[0] + 1.5 * math.sin(lt * 3), co[1], 0), -PI / 2 + 0.2 + 0.25 * math.sin(lt * 4), t, buck=b, ears=1.0)
    mb = S['mulebox']
    mb['root'].rotation_euler = (0.25 * math.sin(lt * 18) * b, -0.25 + 0.2 * math.sin(lt * 13) * b, PI / 2)
    he = S['heter']
    hp = (co[0] - 5.0 + 0.8 * math.sin(lt * 3), co[1] - 1.5, 0)
    stand(he, hp, -PI / 2 - 0.3, P('reach', aR=(1.5, 0.2, 0.2), aL=(1.4, -0.1, 0.4), lean=-0.35, lL=(0.6, 0.2), lR=(-0.3, 0.1), head=(0.0, 0.2)), 'wide')
    span(S['lead'], hand_of(he, 1), wpos(S['mule']['head'], (0, -1.3, -0.5)), 0.05)
    cam(S, (co[0] + 1.0, co[1] - 13.0, 2.4), (co[0] - 0.6, co[1], 2.6), 24)


def rook_mule(S, k, t, lt):
    """Rook, wary, edges along the corral rail away from the bucking mule and taps his beak, thinking."""
    sky(S, 'town')
    co = S['corral'].location
    mule_pose(S, (co[0] + 2.0, co[1] + 1.0, 0), -PI / 2 + 0.4, t, buck=0.7, ears=1.0)
    rk = S['rook']
    x = lerp(co[0] - 4.0, co[0] - 6.0, sm(k / 0.4))
    pose = blend(P('brace', head=(0.0, 0.6)), P('tap'), sm((k - 0.45) / 0.2))
    stand(rk, (x, co[1] - 4.0, 0), -0.4, pose)
    S['rface'] = 'shocked' if k < 0.45 else 'squint'
    S['hat_tip'] = 0.2 if k < 0.45 else 0.5
    h = head(rk)
    cam(S, plus(h, (-1.2, -6.4, -0.8)), plus(h, (1.6, 0.6, -0.9)), 24)


# ---------------------------------------------------------------- chutes
def chute_crate(S, k, t, lt):
    """At the hangar: Heter hauls a war-surplus parachute out of its pack; the canopy billows up in the wind."""
    sky(S, 'field')
    he = S['heter']
    p = at(FLD, 2.0, 8.6, 0)
    stand(he, p, PI + 0.6, blend(P('reach', aR=(1.2, 0.2, 0.4), aL=(1.0, -0.2, 0.6)), P('up', aL=(2.4, 0.4, 0.3), aR=(2.6, 0.2, 0.2)), sm(k / 0.6)), 'proud')
    ch = S['chute2']
    infl = sm((k - 0.15) / 0.6)
    ch['root'].location = at(FLD, 1.0, 11.4, 0.4 + 2.0 * infl)
    ch['root'].rotation_euler = (0.55 * (1 - infl) + 0.15, -0.5, 0.2 + 0.1 * math.sin(t * 2))
    ch['can'].scale = (lerp(0.2, 0.75, infl), lerp(0.2, 0.75, infl), lerp(0.3, 0.75, infl))
    ch['can'].location = (0, 0, lerp(0.5, 4.2, infl))
    for l in ch['lines']:
        l.hide_render = infl < 0.4
    S['sock'].rotation_euler = (PI / 2 + 0.1 * math.sin(t * 3), 0, 0.15 * math.sin(t * 2))
    cam(S, at(FLD, 7.4, 1.6, 2.2), at(FLD, 1.6, 10.2, 2.6 + 1.5 * infl), 24)


def rook_test(S, k, t, lt):
    """Rook leans in over a closed beaver box with his magnifying glass, follows the rope to its knot, gives the knot a
    poke, and the box springs open in his face; his hat jumps off his head."""
    sky(S, 'field')
    bx = S['box2']
    g = at(FLD, 6.0, 4.0, 0.0)
    bx['root'].location, bx['root'].rotation_euler = g, (0, 0, 0.0)
    pop = sm((k - 0.62) / 0.06)
    box_open(bx, pop * (1 + 0.1 * math.sin(lt * 30) * math.exp(-max(0, k - 0.62) * 10)))
    rk = S['rook']
    lean = sm(k / 0.2) * (1 - pop)
    pose = P('stand', aL=(1.1, 0.0, 0.7), aR=(1.0 + 0.3 * sm((k - 0.45) / 0.15), -0.2, 0.3), lean=0.5 * lean, head=(0.45 * lean, 0.0))
    pose = blend(pose, P('scream', lean=-0.2), pop)
    stand(rk, plus(g, (0.1, -1.6 - 0.6 * pop, 0)), 0.0, pose)
    S['rface'] = 'squint' if pop < 0.5 else 'shocked'
    S['hat_jump'] = 0.9 * pop * (1 - sm((k - 0.85) / 0.15))
    if pop < 0.5:
        S['mag'].location = plus(hand_of(rk, 0), (0.0, -0.15, 0.25))
        S['mag'].rotation_euler = (0.4, 0, 0)
    else:
        S['mag'].location = plus(hand_of(rk, 0), (0.6 * pop, -0.5, 0.8 * pop))
        S['mag'].rotation_euler = (lt * 9, 0.5, 0)
    h = head(rk)
    cam(S, plus(g, (2.6, -5.4, 2.2)), plus(g, (0.0, -1.0, 1.4)), 26)


# ---------------------------------------------------------------- test: Geronimo
def test_drop(S, k, t, lt):
    """Over the landing field: the plane passes low and a box under a small canopy drifts down onto the mown strip,
    the windsock streaming."""
    sky(S, 'field')
    plane_at(S, at(FLD, lerp(-60, 50, k), 20, 46), 0.0, 0.05, t)
    bx = S['box2']
    p = at(FLD, lerp(-8, 2, k), 4.0, lerp(32, 1.5, k))
    bx['root'].location, bx['root'].rotation_euler = p, (0, 0.1 * math.sin(t * 3), 0.0)
    chute_pose(S['chute2'], p, 0.08 * math.sin(t * 3), 1.0, 0.0)
    S['sock'].rotation_euler = (PI / 2 + 0.1 * math.sin(t * 3), 0, 0.15 * math.sin(t * 2))
    cam(S, at(FLD, 12.0, -26.0, 2.0), at(FLD, -2.0, 4.0, lerp(22, 8, k)), 26)


def geronimo_out(S, k, t, lt):
    """The box pops open on the strip and the old grey-muzzled beaver tumbles out and shakes himself off; the handler
    jogs in, scoops him up under the arms and carries him back."""
    sky(S, 'field')
    g = at(FLD, 2.0, 4.0, 0.0)
    bx = S['box2']
    bx['root'].location, bx['root'].rotation_euler = g, (0, 0, 0.0)
    box_open(bx, sm(k / 0.12))
    flat_chute(S['chute2'], g, PI * 0.5, 1.0)
    b = S['geronimo']
    sh = 0.3 * math.sin(lt * 28) * (sm((k - 0.15) / 0.05) - sm((k - 0.35) / 0.05))
    hd = S['hand']
    if k < 0.55:
        bv(b, plus(g, (0.2, -0.9 * sm(k / 0.2), 0.05)), 0.3 + sh, t, roll=sh * 0.5, wide=0.6)
        stand(hd, plus(g, (lerp(-6.0, -1.0, sm(k / 0.55)), -1.6, 0)), facing((-6, -1.6), (0.2, -0.9)), K.walk(t, 2.2), 'warm')
    else:
        v = sm((k - 0.55) / 0.15)
        hp = plus(g, (-1.0 - 2.4 * sm((k - 0.7) / 0.3), -1.6, 0))
        stand(hd, hp, -PI / 2 if k > 0.7 else 0.4, blend(P('reach', aL=(1.3, 0.1, 0.9), aR=(1.3, 0.1, 0.9), lean=0.5),
                                                       P('stand', aL=(1.0, 0.0, 1.5), aR=(1.0, 0.0, 1.5)), v) if k < 0.7 else
              dict(K.walk(t, 2.0), aL=(1.0, 0.0, 1.5), aR=(1.0, 0.0, 1.5)), 'warm')
        hpos = wpos(hd.body, (0, -0.55, 0.55))
        bv(b, (hpos[0], hpos[1], lerp(g[2] + 0.05, hpos[2] - 0.5, v)), hd.root.rotation_euler.z, t, rear=0.9 * v, tail=-0.2, nod=-0.2)
    cam(S, plus(g, (1.4, -7.4, 1.4)), plus(g, (-0.8, -0.6, 0.8)), 26)


def rook_tally(S, k, t, lt):
    """Rook on an upturned crate by the strip keeps count on his notepad: tick, tick, tick, a strike through, and a
    fresh line; behind him another box comes down."""
    sky(S, 'field')
    rk = S['rook']
    p = at(FLD, 10.0, -3.0, 0.0)
    pose = P('stand', aL=(1.2, -0.1, 1.5, 0.6), aR=(1.1, -0.25, 1.4 + 0.35 * abs(math.sin(lt * 9)), 0.5), head=(0.35, 0.0))
    if k > 0.75:
        pose = blend(pose, P('stand', aL=(1.2, -0.1, 1.5, 0.6), aR=(0.4, 0.2, 0.3), head=(-0.15, 0.5)), sm((k - 0.75) / 0.15))
    stand(rk, p, 0.6, pose)
    S['rface'] = 'squint' if k < 0.75 else 'low'
    S['hat_tip'] = 0.3
    pad = S['pad']
    pad.location = plus(hand_of(rk, 0), (0.15, -0.25, 0.25))
    pad.rotation_euler = (0.5, 0, 0.6)
    n = min(5, int(k * 6.5) + 1)
    for i, m in enumerate(S['marks']):
        m.hide_render = i >= n
    bx = S['box2']
    q = at(FLD, -2.0, 14.0, lerp(16, 6, k))
    bx['root'].location = q
    chute_pose(S['chute2'], q, 0.08 * math.sin(t * 3), 1.0, 0.0)
    h = head(rk)
    cam(S, plus(h, (-1.0, -3.4, 0.0)), plus(h, (0.0, 0.0, -0.9)), 26)


# ---------------------------------------------------------------- rehook: he climbs back in
def geronimo_back(S, k, t, lt):
    """Geronimo, set down by the open box, waddles back to it on his own, clambers in over the side, settles, and
    looks up at us: ready."""
    sky(S, 'field')
    g = at(FLD, 2.0, 4.0, 0.0)
    bx = S['box2']
    bx['root'].location, bx['root'].rotation_euler = g, (0, 0, 0.0)
    box_open(bx, 1.0 - sm((k - 0.7) / 0.25) * 0.75)
    flat_chute(S['chute2'], g, PI * 0.5, 1.0)
    b = S['geronimo']
    w = 1.0 - sm((k - 0.45) / 0.1)
    p = plus(g, (lerp(-3.2, 0.0, sm(k / 0.5)), lerp(-1.8, 0.0, sm(k / 0.5)), 0.05 + 0.25 * sm((k - 0.42) / 0.12)))
    yaw = facing((-3.2, -1.8), (0, 0)) if k < 0.5 else lerp(facing((-3.2, -1.8), (0, 0)), 0.0, sm((k - 0.5) / 0.2))
    bv(b, p, yaw, t, walk=w, rear=0.35 * sm((k - 0.6) / 0.15), nod=-0.25 * sm((k - 0.6) / 0.15), wide=0.3, tail=0.3 * sm((k - 0.8) / 0.1))
    cam(S, plus(g, (0.6, -4.4, 1.2)), plus(g, (-0.6, -0.5, 0.45)), 28)


def rook_jaw(S, k, t, lt):
    """Rook, close: his beak drops open and his hat lifts clean off his head."""
    sky(S, 'field')
    rk = S['rook']
    p = at(FLD, 4.6, -1.2, 0.0)
    shock = sm((k - 0.25) / 0.15)
    stand(rk, p, -0.5, blend(P('stand', head=(0.25, 0.0)), P('stand', aL=(0.4, 0.5, 0.4), aR=(0.4, 0.5, 0.4), lean=-0.15, head=(-0.1, 0.0)), shock))
    S['rface'] = 'shocked' if shock > 0.4 else 'calm'
    S['hat_jump'] = 0.7 * shock * (1 - sm((k - 0.75) / 0.2))
    S['laugh'] = 0.0
    h = head(rk)
    cam(S, plus(h, (-1.6, -3.4, -0.4)), plus(h, (0, 0, -0.1)), lerp(30, 38, k))


def rook_heter(S, k, t, lt):
    """Rook and Heter side by side over the box: Heter scratches his head under his hat, Rook copies him, then they
    both shrug."""
    sky(S, 'field')
    g = at(FLD, 2.0, 4.0, 0.0)
    bx = S['box2']
    bx['root'].location = g
    box_open(bx, 0.25)
    b = S['geronimo']
    bv(b, plus(g, (0.0, 0.0, 0.3)), 0.0, t, rear=0.35, nod=-0.25, wide=0.3)
    he, rk = S['heter'], S['rook']
    sc_ = P('stand', aR=(1.4, -0.3, 2.3, 0.4), head=(0.15, 0.2))
    sh = sm((k - 0.6) / 0.2)
    stand(he, plus(g, (-1.8, -2.4, 0)), 0.5, blend(sc_, P('shrug'), sh), 'wide')
    stand(rk, plus(g, (1.8, -2.4, 0)), -0.5, blend(P('stand', aL=(1.4, -0.3, 2.3, 0.4), head=(0.15, -0.2)), P('shrug'), sh))
    S['rface'] = 'squint'
    cam(S, plus(g, (0.0, -9.0, 2.4)), plus(g, (0.0, -1.6, 1.9)), 28)


# ---------------------------------------------------------------- flight
def hold(S, k, t, lt):
    """Inside the plane's hold: a row of beaver boxes strapped along the wall, noses at the breathing holes; the cargo
    door is open on blue sky and mountains, Geronimo's box nearest the door."""
    sky(S, 'high')
    S['holdlamp'].data.energy = 400
    for i, (bx, p) in enumerate(S['holdboxes']):
        bx['root'].location = p
        bx['root'].rotation_euler = (0, 0, 0.0)
    for i, b in enumerate(S['all_beavers'][:4]):
        bx, _ = S['holdboxes'][i if i < 3 else 3]
        peek(S, bx, b, t + i)
    shake = 0.02 * math.sin(t * 23)
    cam(S, at(HOLD, lerp(6.2, 5.4, k), -1.7, 2.0 + shake), at(HOLD, -3.0, 0.7, 0.9), 22, roll=0.03 * math.sin(t * 1.5))


def rook_hold(S, k, t, lt):
    """Rook braced in the open cargo door, hat clamped down, coat whipping in the wind, peering out at the mountains;
    a feather tears loose and whirls away."""
    sky(S, 'high')
    S['holdlamp'].data.energy = 300
    for i, (bx, p) in enumerate(S['holdboxes']):
        bx['root'].location = p
    rk = S['rook']
    p = at(HOLD, -0.2, -1.2, 0.0)
    pose = P('hat', aL=(1.5, 1.0, 0.4), lean=0.2 + 0.05 * math.sin(t * 9), head=(0.35, -0.3), lL=(0.2, 0.1), lR=(-0.2, 0.1))
    stand(rk, p, PI * 0.05, pose)
    rk.root.rotation_euler = (0, 0.03 * math.sin(t * 17), PI * 0.05)
    S['rface'] = 'shocked' if k > 0.5 else 'squint'
    S['hat_tip'] = 0.5
    f = S['feather']
    if k > 0.45:
        u = (k - 0.45) / 0.55
        f.location = plus(head(rk), (0.6 * u, -3.0 * u, 0.4 - 1.2 * u * u))
        f.rotation_euler = (u * 14, u * 9, u * 5)
    cam(S, at(HOLD, 2.6, 1.6, 2.2), at(HOLD, -0.4, -1.6, 1.8), 22)


def plane_wide(S, k, t, lt):
    """From beside the plane over the mountains: canopies blossom one after another behind it, boxes swinging under
    them, falling towards the green basin."""
    sky(S, 'high')
    pl = (lerp(-40, 40, k), 0.0, 220.0)
    plane_at(S, pl, 0.0, -0.08, t)
    for i, (ch, bx) in enumerate(zip(S['chutes'], S['boxes'])):
        age = lt + 0.55 * (4 - i) - 0.2
        if age < 0:
            bx['root'].location = FAR
            ch['root'].location = FAR
            continue
        p = (pl[0] - 3.0 - 7.0 * age - 2.5 * i, -1.2 - 1.6 * age, pl[2] - 1.5 - 4.0 * age - 0.5 * age * age)
        bx['root'].location = p
        bx['root'].rotation_euler = (0, 0.1 * math.sin(t * 2 + i), i)
        chute_pose(ch, p, 0.1 * math.sin(t * 2 + i), sm(age / 0.4), i)
    cam(S, (pl[0] + 14.0, -32.0, pl[2] + 3.0), (pl[0] - 6.0, -1.0, pl[2] - 6.0), 24)


# ---------------------------------------------------------------- landed: the hush
def rook_hush(S, k, t, lt):
    """Evening in the meadow: open boxes and slack canopies dotted across the grass, beavers waddling off towards the
    creek. Rook stands among them and quietly takes off his hat."""
    sky(S, 'dusk')
    for i, (ch, bx) in enumerate(zip(S['chutes'], S['boxes'])):
        p = on(LAND[0] - 18 + 8.0 * i, LAND[1] + 6 + 4.0 * math.sin(i * 1.7))
        bx['root'].location, bx['root'].rotation_euler = p, (0, 0, i * 0.9)
        box_open(bx, 1.0)
        flat_chute(ch, p, i * 0.9 + PI, 1.0)
    for i, b in enumerate(S['beavers']):
        p = on(LAND[0] - 16 + 8.0 * i - 2.0 * k, LAND[1] + 4.0 + 4.0 * math.sin(i * 1.7) - 2.5 * k)
        bv(b, (p[0], p[1], p[2] + 0.05), 1.0, t + i, walk=1.0)
    rk = S['rook']
    rp = on(LAND[0] - 1.0, LAND[1] - 4.0)
    stand(rk, rp, 0.2, P('stand', aR=(0.9, -0.25, 1.9, 0.6), head=(0.25, 0.0)))
    S['hat_off'] = sm((k - 0.2) / 0.35)
    S['rface'] = 'soft'
    cam(S, plus(rp, (lerp(3.0, 2.2, k), -8.4, 1.6)), plus(rp, (-2.0, 6.0, 1.6)), 26)


# ---------------------------------------------------------------- payoff: a year later
def dam_wide(S, k, t, lt):
    """A year later on the creek: a new stick dam holds back a pond, a lodge rising in the middle of it; a beaver
    swims across with a branch."""
    sky(S, 'year')
    d = S['dam'].location
    b = S['beavers'][1]
    bv(b, at(d, lerp(-5, 2, k), 5.0, -0.1), -PI / 2, t, nod=-0.1)
    cam(S, at(d, lerp(-7.0, -5.0, k), -14.0, 3.2), at(d, 0.5, 3.0, 0.8), 24)


def lodge(S, k, t, lt):
    """Geronimo sits up on top of his lodge, three younger beavers round him on the dam, and slaps the water with his
    tail."""
    sky(S, 'year')
    L = wpos(S['lodge'])
    b = S['geronimo']
    slap = sm((k - 0.55) / 0.08) * (1 - sm((k - 0.7) / 0.1))
    bv(b, (L[0], L[1], L[2] + 2.0), -0.3, t, rear=0.9 - 0.4 * slap, tail=0.9 * slap, nod=-0.2, chew=0.3)
    d = S['dam'].location
    for i, bb in enumerate(S['beavers'][:3]):
        bv(bb, at(d, -4.0 + 3.0 * i, -1.0, 1.0), 0.3 * (i - 1) - 0.2, t + i, chew=0.6 if i == 1 else 0.0, rear=0.4 if i == 2 else 0.0)
    cam(S, (L[0] - 2.0, L[1] - 13.0, L[2] + 3.4), (L[0] - 1.0, L[1] - 4.0, L[2] + 1.6), 28)


def rook_dam(S, k, t, lt):
    """Rook on the dam, a beaver chewing a stick beside him: he looks at the pond, at the lodge, at the beaver, and lets
    out a short caw of a laugh."""
    sky(S, 'year')
    d = S['dam'].location
    rk = S['rook']
    p = at(d, 1.2, -1.4, 0.9)
    lg = sm((k - 0.45) / 0.15)
    stand(rk, p, 0.4, blend(P('hips', head=(0.1, -0.5)), P('stand', aL=(0.3, 0.5, 0.6), aR=(0.3, 0.5, 0.6), lean=-0.15, head=(-0.25, 0.0)), lg))
    S['laugh'] = lg * (1 - sm((k - 0.85) / 0.1))
    S['rface'] = 'laugh' if lg > 0.3 else 'squint'
    b = S['beavers'][2]
    bv(b, at(d, -0.6, -1.6, 0.9), 0.9, t, rear=0.8, chew=1.0)
    h = head(rk)
    cam(S, plus(h, (-2.2, -5.0, -0.8)), plus(h, (-0.8, 0.0, -0.9)), 26)


# ---------------------------------------------------------------- end
def signoff(S, k, t, lt):
    """In the meadow by the slack canopy: Rook spots a shiny parachute ring in the grass, picks it up, turns it so it
    glints, pockets it, and tugs his brim."""
    sky(S, 'meadow')
    g = on(*LAND)
    bx = S['box']
    bx['root'].location, bx['root'].rotation_euler = g, (0, 0, 0.3)
    box_open(bx, 1.0)
    flat_chute(S['chute'], g, 0.3 + PI, 1.0)
    rk = S['rook']
    pick = sm(k / 0.3)
    show_ = sm((k - 0.3) / 0.2) * (1 - sm((k - 0.7) / 0.15))
    pose = blend(P('stand', lL=(0.6, 1.1), lR=(0.2, 0.8), lift=-0.4, lean=0.5, aR=(0.9, 0.1, 0.3), head=(0.5, 0.0)),
                 P('stand', aR=(1.9, 0.0, 0.6, 0.4), head=(-0.2, 0.0)), pick)
    if k > 0.72:
        pose = blend(pose, P('hat'), sm((k - 0.72) / 0.2))
    rp = plus(g, (1.6, -2.6, 0))
    stand(rk, rp, 0.15, pose)
    S['rface'] = 'low' if k > 0.72 else 'calm'
    S['hat_tip'] = 0.25 + 0.35 * sm((k - 0.8) / 0.15)
    hr = hand_of(rk, 1)
    S['ring'].location = plus(hr, (0, -0.1, 0.1)) if k < 0.78 else FAR
    S['ring'].rotation_euler = (1.2, 0.3 + t, 0.4)
    S['glint'].location = plus(hr, (0.3, -0.7, 0.4))
    S['glint'].data.energy = 260 * show_
    h = head(rk)
    cam(S, plus(h, (0.6, -4.8, -0.7)), plus(h, (0.0, 0.0, -0.5)), 30)


SHOTS3D = {'drop_close': drop_close, 'drop_wide': drop_wide, 'hole_close': hole_close, 'rook_box_ride': rook_box_ride,
           'meadow_land': meadow_land, 'box_open': box_open_shot, 'rook_land': rook_land, 'town_tree': town_tree,
           'town_flood': town_flood, 'rook_flood': rook_flood, 'mule_load': mule_load, 'mule_buck': mule_buck,
           'rook_mule': rook_mule, 'chute_crate': chute_crate, 'rook_test': rook_test, 'test_drop': test_drop,
           'geronimo_out': geronimo_out, 'rook_tally': rook_tally, 'geronimo_back': geronimo_back, 'rook_jaw': rook_jaw,
           'rook_heter': rook_heter, 'hold': hold, 'rook_hold': rook_hold, 'plane_wide': plane_wide, 'rook_hush': rook_hush,
           'dam_wide': dam_wide, 'lodge': lodge, 'rook_dam': rook_dam, 'signoff': signoff}
