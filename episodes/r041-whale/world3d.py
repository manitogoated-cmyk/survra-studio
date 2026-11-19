"""Case 041 in 3D - the exploding whale of Florence, Oregon, 12 November 1970. A whale about 45 feet long and some
8 tons washed up dead on the beach south of the Siuslaw River. The Oregon State Highway Division, with assistant
district engineer George Thornton in charge, packed twenty 50-pound cases of dynamite (half a ton) against it, so the
blast would leave pieces small enough for seagulls and scavengers to clean up. Spectators were moved back into the
dunes. Walter Umenhofer, who knew explosives from his war service, said it was far too much and watched from further
back than everyone else. The blast threw a column of sand and whale into the air; blubber sailed over the crowd, and a
chunk crushed the roof of the new car he had bought days earlier in a "whale of a deal" sales promotion, parked about
a quarter of a mile away. Nobody was hit. Highway crews cleaned up the rest; Thornton said it "went just exactly right".
In 2020 Florence named a new park Exploding Whale Memorial Park.

Built for this story only: a wide Oregon beach with surf, a rock jetty and a headland; the dead whale and the stacked
crates; a long dune ridge with beach grass where the crowd stands; a gravel parking lot of 1970 sedans behind it; a
blasting machine and its wire; a bulldozer; a car dealer's forecourt with bunting; and a small park in the pines with a
wooden sign.

Everything is a generic low-poly reconstruction. Cars, crates, the bulldozer and the dealer carry no makes, logos or
brand names; the only words on screen are the documented promotion slogan and the park's documented name. Nobody's
likeness is attempted."""
import glob
import math

import bmesh
import bpy
from mathutils import Vector

from mathutils import Matrix

from engine4 import kit3d as K
from engine4.kit3d import P, blend, lerp, light

PI = math.pi
FAR = (0, 0, -30000)
BCH = (0.0, 0.0, 0.0)               # the beach, the dunes and the parking lot behind them
SHOW = (4000.0, 0.0, 0.0)           # the car dealer's forecourt, days before
PARK = (-4000.0, 0.0, 0.0)          # the park in the pines, fifty years later
CARP = (6.0, -136.0)                # the new car in the lot
HOST = {'rook_dune', 'rook_duck', 'rook_count', 'gull', 'expert', 'rook_eye', 'rook_roof', 'rook_laugh', 'rook_nose',
        'rook_stare', 'rook_park', 'signoff'}
CAMFILL = {'*': 150, 'blast_close': 60, 'column': 0, 'chunk_lens': 0, 'overhead_chunk': 0, 'slab_fall': 0, 'run_cars': 80,
           'car_crush': 80, 'bulldozer': 80, 'park_sign': 60, 'rook_dune': 180, 'rook_eye': 160, 'owner_face': 120,
           'rook_park': 320, 'signoff': 220}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SAND, SAND2, WET, DUNE = 'D9C59C', 'C9B48A', 'B49E78', 'D2BC8E'
WHALE, BELLY = '596169', '8E9294'
BLUB = ('F2DCD8', 'E6CCCA', 'F6E6E2', 'DCC4C4', 'EED6D2')
CARS = ('C9A44A', '3A6A5A', '8A3A2E', 'D8D2C2', '2E4A6E', '6A6E44')
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    day=('E2EAEE', '6E9CC8', 1.15, 3.4, 'FFF0DA', (0.55, -0.6, 0.5)),
    show=('EEF0EA', '7AA6D4', 1.2, 3.4, 'FFF2DE', (0.4, -0.7, 0.6)),
    park=('F2E4CC', '86A8C8', 1.1, 3.0, 'FFE6C4', (-0.6, -0.55, 0.42)))
_KEEP = []
TB = 0.22                           # the blast, seconds into the first shot

# Building with bpy.ops slows down with every object already in the scene (about 0.1 s per primitive here, over three
# minutes for this set). Each primitive is made once as a prototype mesh and copied, which gives the same geometry,
# materials and bevels in a fraction of the time; the new object is selected and made active as the operator leaves it.
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
    o = add('cylinder', col, radius=0.5, depth=1, vertices=6, parent=par, **kw)
    span(o, a, b, w)
    return o


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def lump(col, loc, s, par=None, seed=0, rough=1.0):
    """An irregular low-poly lump: blubber, rock, sand. The vertices are pushed about so no two read as spheres."""
    o = add('ico_sphere', col, loc, scale=s, radius=1, subdivisions=1, parent=par, rough=rough)
    for i, v in enumerate(o.data.vertices):
        f = 0.72 + 0.5 * rnd(i + seed * 7, 3 + seed)
        v.co = v.co * f
    return o


def blubber(i, s=(1, 1, 1)):
    """A lump of whale: pale fat with a cap of grey skin, so it never reads as a rock."""
    o = lump(BLUB[i % 5], FAR, s, None, i, rough=0.55)
    add('ico_sphere', ('5E666E', '6A7279')[i % 2], (0.08, 0.05, 0.36), rot=(0.2, 0.1, 0), scale=(1.0, 0.96, 0.66), radius=1, subdivisions=1, parent=o, rough=0.45)
    return o


def puff(col, i):
    """A soft ball of blown sand (rounder than a lump)."""
    o = add('ico_sphere', col, FAR, radius=1, subdivisions=2, rough=1.0)
    for j, v in enumerate(o.data.vertices):
        v.co = v.co * (0.9 + 0.18 * rnd(j + i * 5, 7))
    return o


# ---------------------------------------------------------------- the ground of the beach set
def bump(x, y):
    """Small rolls on the dunes only."""
    if y > -50 or y < -104:
        return 0.0
    w = min(1.0, (-50 - y) / 6.0, (y + 104) / 6.0)
    return w * (0.45 * math.sin(x * 0.11 + y * 0.23) + 0.3 * math.sin(x * 0.27 - y * 0.15 + 1.3))


def gz(x, y):
    """Ground height: flat beach, the dune front from y=-48 up to the ridge at y=-62, the ridge to y=-92, the back
    slope down to the lot at y=-106."""
    if y > -48:
        b = 0.0
    elif y > -62:
        b = 5.0 * sm((-48 - y) / 14.0)
    elif y > -92:
        b = 5.0
    elif y > -106:
        b = 5.0 * sm((y + 106) / 14.0)
    else:
        b = 0.0
    return b + bump(x, y)


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


_FONT = []


def font():
    if not _FONT:
        f = None
        for p in sorted(glob.glob('/usr/share/fonts/**/Inter-Bold.otf', recursive=True) + glob.glob('/usr/share/fonts/**/Inter*Bold*.ttf', recursive=True)):
            try:
                f = bpy.data.fonts.load(p)
                break
            except Exception:
                continue
        _FONT.append(f)
    return _FONT[0]


def text3d(par, s, loc, size, col, rot=(PI / 2, 0, 0), extrude=0.03, emit=0.0):
    """Raised letters (the dealer's banner, the park sign). Inter Bold when installed, Blender's own font otherwise."""
    bpy.ops.object.text_add(location=(0, 0, 0))
    o = bpy.context.object
    o.data.body = s
    f = font()
    if f:
        o.data.font = f
    o.data.align_x, o.data.align_y = 'CENTER', 'CENTER'
    o.data.size = size
    o.data.extrude = extrude
    o.data.materials.append(K.mat(col, 0.7, emit))
    o.parent = par
    o.location, o.rotation_euler = loc, rot
    return o


# ---------------------------------------------------------------- the beach, the whale, the crates
def make_whale(par):
    """A big dead whale lying on the sand, head towards -X, its flank towards the dunes (-Y): one long tapering body,
    a pale underside, a tail stock narrowing to broad flukes. Grey, no wounds."""
    w = empty((0, 0, 0), par)
    body = [add('uv_sphere', WHALE, (-1.2, 0, 2.45), scale=(9.6, 2.75, 2.5), radius=1, segments=20, ring_count=10, parent=w, rough=0.55),
            add('uv_sphere', BELLY, (-2.0, -0.25, 1.25), scale=(8.6, 2.45, 1.35), radius=1, segments=16, ring_count=8, parent=w, rough=0.55),
            add('uv_sphere', WHALE, (-8.6, 0, 2.35), scale=(2.6, 2.5, 2.3), radius=1, segments=14, ring_count=8, parent=w, rough=0.55)]
    stock = [add('cone', WHALE, (10.2, 0, 1.75), rot=(0, PI / 2, 0), scale=(0.8, 1.0, 1.0), radius1=2.1, radius2=0.55, depth=7.0, vertices=12, parent=w, rough=0.55)]
    for s in (-1, 1):
        stock.append(add('uv_sphere', WHALE, (14.4, s * 1.9, 1.15), rot=(0, 0.08, s * 0.5), scale=(1.5, 2.7, 0.2), radius=1, segments=12, ring_count=6, parent=w, rough=0.55))
    body.append(add('uv_sphere', WHALE, (-3.4, -2.55, 0.85), rot=(0.55, 0.25, -0.35), scale=(1.9, 0.3, 0.75), radius=1, segments=10, ring_count=6, parent=w, rough=0.55))
    body.append(add('cube', '262A2F', (-8.0, -2.42, 2.15), rot=(0, 0.1, 0.35), scale=(0.55, 0.06, 0.08), size=1, parent=w))         # the closed eye
    body.append(add('cube', '34383E', (-9.4, -2.05, 1.45), rot=(0, 0.06, 0.3), scale=(4.6, 0.06, 0.09), size=1, parent=w))          # mouth line
    for i in range(6):                                                                                                               # throat grooves
        body.append(add('cube', 'A4A8AA', (-7.0 + 0.4 * i, -2.25 - 0.02 * i, 0.75 + 0.12 * i), rot=(0.25, 0, 0.3), scale=(3.4, 0.04, 0.05), size=1, parent=w))
    for i in range(7):                                                                                                               # pale scars
        body.append(add('cube', '8C9498', (-5 + 2.0 * i, -2.62 + 0.12 * math.sin(i), 2.7 + 0.5 * rnd(i, 5)), rot=(0.3, 0, 0.4 * rnd(i, 6)),
                        scale=(0.9, 0.04, 0.05), size=1, parent=w))
    return w, body, stock


def make_crates(par):
    """Twenty plain wooden cases of dynamite stacked against the whale's flank (8, 7, 5), and the wire from them."""
    out = []
    n = 0
    for row, cnt in enumerate((8, 7, 5)):
        for i in range(cnt):
            x = -3.7 + i * 1.06 + row * 0.53
            c = empty((x, -3.35 - 0.05 * row, 0.3 + 0.58 * row), par, (0, 0, 0.04 * (rnd(n, 9) - 0.5)))
            add('cube', 'C49A64', (0, 0, 0), scale=(0.94, 0.7, 0.52), size=1, parent=c, rough=0.95)
            for z in (-0.17, 0.17):
                add('cube', '8A6034', (0, -0.36, z), scale=(0.96, 0.02, 0.05), size=1, parent=c)                    # slats
            add('cube', 'EFE6CC', (0, -0.365, 0.0), scale=(0.34, 0.02, 0.2), size=1, parent=c)                           # blank label
            out.append(c)
            n += 1
    return out


def make_beach(S):
    r = keep(empty(BCH))
    add('cube', SAND, (0, 0, -0.5), scale=(3000, 3000, 1), size=1, parent=r, rough=1.0)
    add('cube', WET, (0, 20, -0.49), scale=(3000, 14, 1), size=1, parent=r, rough=0.6)
    add('cube', '4A7A8C', (0, 727, -0.25), scale=(3000, 1400, 0.6), size=1, parent=r, rough=0.18)                       # the sea
    S['waves'] = [keep(add('cube', ('F2F6F6', 'DCE8EA')[i % 2], (0, 30 + 9 * i, 0.04), scale=(3000, 0.7 + 0.5 * rnd(i, 1), 0.08), size=1, parent=r, rough=0.5))
                  for i in range(6)]
    field('dunes', list(range(-330, 331, 6)), [-44 - 2.0 * j for j in range(34)], lambda x, y: gz(x, y) + 0.03, DUNE, r)
    for i in range(70):                                                                                                     # beach grass
        x = -120 + 240 * rnd(i, 11)
        y = -56 - 44 * rnd(i, 12)
        z = gz(x, y)
        for b in range(3):
            add('cone', ('8E9450', '6E7E42', 'A8A464')[b], (x + 0.3 * b, y + 0.2 * (b - 1), z + 0.8), rot=(0.25 * (b - 1), 0.2 * (rnd(i, b) - 0.5), 0),
                radius1=0.12, radius2=0.0, depth=1.6 + 0.8 * rnd(i, 13 + b), vertices=3, parent=r)
    for i in range(10):                                                                                                    # driftwood
        x, y = -60 + 120 * rnd(i, 14), -8 - 34 * rnd(i, 15)
        if abs(x) < 16 and y > -12:
            x += 24
        add('cylinder', 'B4A898', (x, y, 0.3), rot=(PI / 2, 0, rnd(i, 16) * PI), radius=0.32, depth=4 + 4 * rnd(i, 17), vertices=6, parent=r, rough=1.0)
    S['log'] = add('cylinder', 'B8AC9C', (11.0, -16.0, 0.42), rot=(0, PI / 2, 0.05), radius=0.42, depth=6.0, vertices=7, parent=r, rough=1.0)
    for i in range(28):                                                                                                    # the rock jetty
        lump(('5A5650', '6E6A62', '4A4844')[i % 3], (-150 + 2 * math.sin(i), 10 + 9 * i, 0.6), (3.0, 3.0, 2.0 + rnd(i, 18)), r, i)
    for i in range(9):                                                                                                     # the headland
        add('ico_sphere', ('3E5A3A', '4A6640', '34502F')[i % 3], (-420 - 60 * i, 600 + 90 * i, -10), scale=(160, 120, 70 + 30 * rnd(i, 19)),
            radius=1, subdivisions=1, parent=r, rough=1.0)
    for i in range(14):                                                                                                    # pines along the back
        x = -260 + 40 * i + 10 * rnd(i, 20)
        y = -200 - 20 * rnd(i, 21)
        for j in range(3):
            add('cone', ('2E4A30', '3A5838')[j % 2], (x, y, 6 + 5 * j), radius1=7 - 1.8 * j, radius2=0.0, depth=9, vertices=7, parent=r, rough=1.0)
    w, body, stock = make_whale(r)
    S['whale'], S['wbody'], S['wstock'] = w, body, stock
    S['crates'] = make_crates(r)
    S['wire'] = [bar(r, '2A2420', a, b, 0.06) for a, b in (((-3.6, -3.7, 0.08), (-8, -14, 0.06)), ((-8, -14, 0.06), (-15, -30, 0.06)),
                                                            ((-15, -30, 0.06), (-22.0, -43.6, 0.12)))]
    S['pbox'] = pb = empty((-22.0, -44.0, 0.0), r, (0, 0, 0.3))                                                            # the blasting machine
    add('cube', '7A5232', (0, 0, 0.42), scale=(0.95, 0.65, 0.84), size=1, parent=pb, rough=0.8)
    add('cube', '3A3A3C', (0, 0, 0.86), scale=(0.98, 0.68, 0.06), size=1, parent=pb, rough=0.4)
    S['plunger'] = pl = empty((0, 0, 0.9), pb)
    add('cylinder', 'A8ACB0', (0, 0, 0.45), radius=0.06, depth=0.9, vertices=6, parent=pl, rough=0.3)
    add('cylinder', '2A2A2C', (0, 0, 0.92), rot=(0, PI / 2, 0), radius=0.07, depth=0.9, vertices=6, parent=pl, rough=0.5)
    # after the blast: the hole, its rim, chunks lying on the sand
    S['crater'] = [add('cylinder', 'A38C64', (0, 0, 0.012), radius=8.5, depth=0.02, vertices=14, parent=r, rough=1.0),
                   add('torus', SAND2, (0, 0, 0.1), major_radius=9.2, minor_radius=1.1, major_segments=14, minor_segments=4, parent=r, rough=1.0),
                   add('cylinder', '7A6A4C', (0.6, -0.3, 0.02), radius=4.5, depth=0.02, vertices=10, parent=r, rough=1.0)]
    S['litter'] = []
    for i in range(34):
        a, d = rnd(i, 22) * 2 * PI, 6 + 30 * rnd(i, 23) ** 1.3
        s = 0.35 + 1.0 * rnd(i, 24)
        o = blubber(i + 40, (s, s * 0.8, s * 0.45))
        o.parent, o.location, o.rotation_euler = r, (d * math.cos(a), d * math.sin(a) * 0.8, s * 0.3), (0, 0, a)
        S['litter'].append(o)
    for i in range(260):                                                                                                  # wind ripples
        x, y = -70 + 140 * rnd(i, 25), -46 + 64 * rnd(i, 26)
        if abs(x) < 13 and abs(y) < 4:
            continue
        add('cube', ('C8B286', 'E4D2AC', 'BEA87C')[i % 3], (x, y, 0.01), rot=(0, 0, 0.15 * (rnd(i, 27) - 0.5)),
            scale=(1.5 + 3.5 * rnd(i, 28), 0.14 + 0.1 * rnd(i, 29), 0.03), size=1, parent=r, rough=1.0)
    for i in range(140):                                                                                                  # pebbles and shells
        x, y = -50 + 100 * rnd(i, 30), -46 + 62 * rnd(i, 31)
        add('ico_sphere', ('6E665A', '8A8070', 'F0E6DA', '4E4A44')[i % 4], (x, y, 0.05), scale=(1.0, 0.8, 0.45),
            radius=0.1 + 0.16 * rnd(i, 32), subdivisions=1, parent=r, rough=0.8)
    for i in range(90):                                                                                                   # more grass by the crowd
        x, y = -34 + 68 * rnd(i, 33), -60 - 42 * rnd(i, 34)
        z = gz(x, y)
        for b in range(2):
            add('cone', ('8E9450', '6E7E42')[b], (x + 0.25 * b, y, z + 0.6), rot=(0.3 * (b - 0.5), 0.2, 0), radius1=0.1, radius2=0.0,
                depth=1.1 + 0.6 * rnd(i, 35 + b), vertices=3, parent=r)
    for i in range(160):                                                                                                  # gravel in the lot
        add('cube', ('8A826E', 'C4BCA6', '6E6858')[i % 3], (-30 + 76 * rnd(i, 36), -122 - 38 * rnd(i, 37), 0.06),
            rot=(0, 0, rnd(i, 38) * 3), scale=(0.25, 0.18, 0.05), size=1, parent=r)
    S['beach'] = r


# ---------------------------------------------------------------- cars
def car(par, col, loc, yaw, shiny=False):
    """A big 1970 four-door sedan, length along local X (front +X). No badges."""
    c = empty(loc, par, (0, 0, yaw))
    ro = 0.3 if shiny else 0.55
    d = dict(root=c)
    d['body'] = add('cube', col, (0, 0, 0.98), scale=(9.4, 3.3, 1.0), size=1, parent=c, rough=ro)
    add('cube', col, (1.6, 0, 1.5), scale=(4.4, 3.2, 0.1), size=1, parent=c, rough=ro)                                     # hood
    add('cube', col, (-3.6, 0, 1.5), scale=(2.2, 3.2, 0.1), size=1, parent=c, rough=ro)                                    # deck
    for x in (4.85, -4.85):
        add('cube', 'D2D6DA', (x, 0, 0.62), scale=(0.28, 3.42, 0.3), size=1, parent=c, rough=0.15)                         # bumpers
    add('cube', 'B8BCC0', (4.73, 0, 1.08), scale=(0.06, 2.6, 0.42), size=1, parent=c, rough=0.2)                            # grille
    for s in (-1, 1):
        add('cylinder', 'FFF2D6', (4.74, s * 1.25, 1.08), rot=(0, PI / 2, 0), radius=0.22, depth=0.06, vertices=8, parent=c, emit=0.8)
        add('cube', 'B02A22', (-4.72, s * 1.3, 1.1), scale=(0.06, 0.6, 0.18), size=1, parent=c, emit=0.4)
        add('cube', 'C8CCD0', (0, s * 1.66, 1.12), scale=(8.6, 0.04, 0.06), size=1, parent=c, rough=0.2)
        for x in (3.0, -3.0):
            add('cylinder', '18181A', (x, s * 1.5, 0.72), rot=(PI / 2, 0, 0), radius=0.72, depth=0.5, vertices=10, parent=c, rough=0.9)
            add('cylinder', 'D6DADE', (x, s * 1.76, 0.72), rot=(PI / 2, 0, 0), radius=0.4, depth=0.04, vertices=10, parent=c, rough=0.15)
    d['glass'] = add('cube', '2C3844', (-0.6, 0, 1.92), scale=(4.4, 3.0, 0.82), size=1, parent=c, rough=0.12)
    d['roof'] = add('cube', col, (-0.7, 0, 2.36), scale=(3.9, 3.06, 0.12), size=1, parent=c, rough=ro)
    d['posts'] = [add('cube', col, (x, s * 1.47, 1.92), rot=(0, 0.35 * (1 if x > 0 else -1), 0), scale=(0.18, 0.1, 0.9), size=1, parent=c, rough=ro)
                  for x in (1.45, -2.85) for s in (-1, 1)]
    return d


def crush(d, u):
    """The roof caved in: u 0 (new) to 1 (flattened)."""
    d['roof'].location.z = lerp(2.36, 1.62, u)
    d['roof'].rotation_euler = (0.08 * u, -0.06 * u, 0)
    d['glass'].scale = (4.4, 3.0, lerp(0.82, 0.32, u))
    d['glass'].location.z = lerp(1.92, 1.6, u)
    for p in d['posts']:
        p.scale = (0.18, 0.1, lerp(0.9, 0.3, u))
        p.location.z = lerp(1.92, 1.58, u)


def make_lot(S):
    r = S['beach']
    add('cube', 'ACA48E', (8, -140, -0.45), scale=(90, 46, 1), size=1, parent=r, rough=1.0)                               # gravel lot
    for i in range(12):
        add('cylinder', '7A6A54', (-34 + 7 * i, -117.5, 0.25), rot=(0, PI / 2, 0), radius=0.25, depth=5.5, vertices=6, parent=r)   # parking logs
    for i in range(10):
        add('cylinder', '6A5640', (-36 + 9 * i, -163, 1.0), radius=0.14, depth=2.0, vertices=5, parent=r)                   # fence posts
    add('cube', '8A7458', (5, -163, 1.5), scale=(84, 0.1, 0.16), size=1, parent=r)
    add('cube', '8A7458', (5, -163, 0.9), scale=(84, 0.1, 0.16), size=1, parent=r)
    S['hero'] = car(r, CARS[0], (CARP[0], CARP[1], 0), 0.0, True)
    S['cars'] = [car(r, CARS[i], loc, yaw) for i, (loc, yaw) in enumerate((((-6.5, -137, 0), 0.04), ((18.5, -135.5, 0), -0.03),
                                                                             ((-2, -152, 0), PI + 0.05), ((12, -153, 0), PI), ((-18, -136.5, 0), 0.02)), 1)]
    S['slab'] = keep(blubber(99, (2.2, 1.7, 0.8)))


# ---------------------------------------------------------------- the bulldozer and the gulls
def make_dozer(S):
    d = keep(empty(FAR))
    Y = 'D8A824'
    add('cube', Y, (0, 0, 1.75), scale=(4.6, 2.6, 1.5), size=1, parent=d, rough=0.6)
    add('cube', Y, (1.6, 0, 2.7), scale=(2.2, 2.2, 0.5), size=1, parent=d, rough=0.6)
    add('cylinder', '2A2A2C', (2.2, 0.6, 3.6), radius=0.12, depth=1.6, vertices=6, parent=d)                              # exhaust
    for x, y in ((-1.9, 1.1), (-1.9, -1.1), (0.0, 1.1), (0.0, -1.1)):
        add('cube', '2A2A2C', (x, y, 3.4), scale=(0.12, 0.12, 2.0), size=1, parent=d)
    add('cube', Y, (-0.95, 0, 4.45), scale=(2.3, 2.6, 0.12), size=1, parent=d, rough=0.6)
    add('cube', '3A3A3C', (-1.0, 0, 2.7), scale=(1.4, 1.4, 0.3), size=1, parent=d)                                        # seat
    for s in (-1, 1):
        add('cube', '242426', (0, s * 1.55, 0.55), scale=(5.4, 0.85, 1.1), size=1, parent=d, rough=0.95)
        for i in range(9):
            add('cube', '3A3A3C', (-2.6 + 0.65 * i, s * 1.55, 1.12), scale=(0.18, 0.88, 0.08), size=1, parent=d)
        bar(d, Y, (1.6, s * 1.4, 0.9), (3.4, s * 1.4, 0.75), 0.18)
    add('cube', Y, (3.55, 0, 0.85), rot=(0, -0.15, 0), scale=(0.3, 4.4, 1.5), size=1, parent=d, rough=0.6)                 # blade
    S['dozer'] = d
    S['mound'] = [keep(lump(SAND2, FAR, (1.0, 1.0, 0.6), None, 70 + i)) for i in range(7)]


def gull(i):
    g = keep(empty(FAR))
    add('uv_sphere', 'F2F2EE', (0, 0, 0), scale=(0.42, 0.2, 0.2), radius=1, segments=10, ring_count=6, parent=g, rough=0.7)
    add('uv_sphere', 'F6F6F2', (-0.38, 0, 0.16), radius=0.14, segments=8, ring_count=5, parent=g, rough=0.7)
    add('cone', 'E8C040', (-0.6, 0, 0.14), rot=(0, -PI / 2, 0), radius1=0.04, radius2=0.0, depth=0.18, vertices=4, parent=g)
    for s in (-1, 1):
        add('cube', '101012', (-0.46, s * 0.09, 0.2), scale=(0.03, 0.02, 0.03), size=1, parent=g)
        add('cylinder', 'E89A7A', (0.02, s * 0.06, -0.25), radius=0.02, depth=0.24, vertices=4, parent=g)
    add('cube', '9AA4AE', (0.45, 0, 0.04), rot=(0, 0.1, 0), scale=(0.24, 0.16, 0.04), size=1, parent=g)                  # tail
    wings = []
    for s in (-1, 1):
        w = empty((0.0, s * 0.12, 0.1), g)
        add('cube', 'A8B2BC', (0.05, s * 0.32, 0), scale=(0.4, 0.62, 0.04), size=1, parent=w, rough=0.7)
        add('cube', '2A2C30', (0.1, s * 0.62, 0), scale=(0.28, 0.12, 0.045), size=1, parent=w)
        wings.append(w)
    return dict(root=g, wings=wings, head=g.children[1])


def flap(gd, a):
    for s, w in zip((-1, 1), gd['wings']):
        w.rotation_euler = (s * a, 0, 0)


# ---------------------------------------------------------------- the dealer's forecourt and the park
def make_show(S):
    r = keep(empty(SHOW))
    add('cube', 'A49E94', (0, 0, -0.5), scale=(160, 160, 1), size=1, parent=r, rough=0.9)
    for i in range(9):
        add('cube', 'ECE6D8', (-40 + 10 * i, -8, 0.01), scale=(0.2, 14, 0.02), size=1, parent=r)                         # bay lines
    add('cube', 'E8E2D2', (0, 16, 4.0), scale=(36, 8, 8), size=1, parent=r, rough=0.8)                                   # showroom
    add('cube', 'A8C8D8', (0, 11.95, 3.0), scale=(30, 0.1, 4.2), size=1, parent=r, rough=0.1, emit=0.35)                 # big windows
    for x in range(-15, 16, 5):
        add('cube', 'D8D2C2', (x, 11.9, 3.0), scale=(0.3, 0.2, 4.4), size=1, parent=r)
    add('cube', '5A6A7A', (0, 11.6, 8.3), scale=(37, 1.4, 0.6), size=1, parent=r)                                        # fascia
    add('cube', 'FAF6EC', (-2.0, 11.4, 6.0), scale=(10.5, 0.25, 4.0), size=1, parent=r, rough=0.7)                        # banner
    for s in (-1, 1):
        add('cube', 'B8302A', (-2.0 + s * 5.3, 11.3, 6.0), scale=(0.22, 0.2, 4.0), size=1, parent=r)
    text3d(r, 'A WHALE', (-2.0, 11.22, 6.95), 1.6, 'B8302A', (PI / 2, 0, 0), 0.05)
    text3d(r, 'OF A DEAL!', (-2.0, 11.22, 5.05), 1.6, 'B8302A', (PI / 2, 0, 0), 0.05)
    S['flags'] = []
    for row, (y0, z0) in enumerate(((11.0, 8.0), (11.0, 7.4))):
        for i in range(26):
            u = i / 25
            x = -18 + 36 * u
            y = lerp(y0, -14.0, abs(u - 0.5) * 2) if row == 0 else y0 - 25 * u
            z = z0 - 1.6 * math.sin(PI * u)
            f = add('cone', ('C8302A', 'F4F2EC', '2E5A9A', 'E8B830')[i % 4], (x, y, z), rot=(PI, 0, 0), radius1=0.36, radius2=0.0, depth=0.8,
                    vertices=3, parent=r, rough=0.8)
            f.scale = (1.0, 0.25, 1.0)
            S['flags'].append(f)
    for s in (-1, 1):
        add('cylinder', 'C8CCD0', (s * 19, -14, 4), radius=0.15, depth=8, vertices=6, parent=r, rough=0.3)
    for i in range(10):                                                                                                    # trees behind
        add('cone', ('2E4A30', '3A5838')[i % 2], (-50 + 11 * i, 34 + 6 * rnd(i, 30), 9), radius1=6, radius2=0, depth=20, vertices=7, parent=r, rough=1.0)
    S['newcar'] = car(r, CARS[0], (1.0, 0.0, 0), 0.35, True)
    nc = S['newcar']['root']
    for s in (-1, 1):                                                                                                      # a big ribbon bow
        add('torus', 'FF7A1A', (-0.6, s * 0.55, 2.85), rot=(PI / 2, 0.5 * s, 0), major_radius=0.5, minor_radius=0.12, major_segments=10, minor_segments=4, parent=nc, rough=0.6)
    add('cube', 'FF7A1A', (-0.6, 0, 2.5), scale=(0.25, 3.12, 0.06), size=1, parent=nc, rough=0.6)
    add('cube', 'FF7A1A', (-0.6, 0, 2.55), scale=(0.3, 0.3, 0.3), size=1, parent=nc, rough=0.6)
    car(r, CARS[3], (-12.0, 2.0, 0), 0.1)
    car(r, CARS[2], (13.0, 2.5, 0), -0.1)
    S['keys'] = keep(add('cube', 'E6E8EA', FAR, scale=(0.08, 0.04, 0.22), size=1, rough=0.15, emit=0.6))
    for i in range(70):                                                                                                   # oil spots and cracks
        add('cylinder', ('7E7A72', '8C877E')[i % 2], (-30 + 60 * rnd(i, 39), -26 + 34 * rnd(i, 40), 0.01), scale=(1.0, 0.6, 1.0),
            radius=0.3 + 0.6 * rnd(i, 41), depth=0.02, vertices=7, parent=r)
    S['show'] = r


def make_park(S):
    r = keep(empty(PARK))
    add('cube', '6A8A48', (0, 0, -0.5), scale=(400, 400, 1), size=1, parent=r, rough=1.0)
    add('cube', '4E7A8A', (0, 48, -0.45), scale=(400, 24, 1), size=1, parent=r, rough=0.2)                                # the river
    add('cube', 'B8A47C', (0, -4, 0.01), scale=(3.2, 30, 0.02), size=1, parent=r)                                         # path
    for i in range(16):
        x = -40 + 80 * rnd(i, 31)
        y = 8 + 26 * rnd(i, 32)
        if abs(x) < 9 and y < 14:
            x += 18 if x > 0 else -18
        add('cylinder', '5A4030', (x, y, 2), radius=0.35, depth=4, vertices=6, parent=r)
        for j in range(4):
            add('cone', ('2E4A30', '3A5838', '34523A')[j % 3], (x, y, 4 + 3.0 * j), radius1=4.0 - 0.8 * j, radius2=0.0, depth=5.5, vertices=7, parent=r, rough=1.0)
    for i in range(8):                                                                                                     # rhododendrons
        x = (-1) ** i * (6 + 2.5 * i)
        y = 1.0 + 3 * rnd(i, 33)
        add('ico_sphere', '3E6A3A', (x, y, 0.9), scale=(1.6, 1.3, 1.1), radius=1, subdivisions=1, parent=r, rough=1.0)
        for j in range(6):
            add('ico_sphere', ('E05A8A', 'F07AA0', 'D04A7A')[j % 3], (x + 1.2 * math.cos(j), y - 0.9 + 0.6 * math.sin(j * 2), 1.2 + 0.5 * math.sin(j)),
                radius=0.22, subdivisions=1, parent=r)
    sg = empty((0, 0, 0), r)                                                                                               # the sign
    for s in (-1, 1):
        add('cylinder', '6A4A2E', (s * 3.4, 0, 1.7), radius=0.26, depth=3.4, vertices=7, parent=sg, rough=1.0)
    add('cube', '8A5E3A', (0, 0, 2.35), scale=(7.2, 0.28, 1.9), size=1, parent=sg, rough=0.9)
    add('cube', '5A3E26', (0, 0, 3.4), scale=(7.8, 0.6, 0.2), size=1, parent=sg, rough=0.9)
    text3d(sg, 'EXPLODING WHALE', (0, -0.16, 2.78), 0.66, 'F2E6C8', (PI / 2, 0, 0), 0.03)
    text3d(sg, 'MEMORIAL PARK', (0, -0.16, 1.98), 0.66, 'F2E6C8', (PI / 2, 0, 0), 0.03)
    add('cube', '6A4A30', (-6.5, -3.2, 0.9), scale=(3.2, 0.9, 0.12), size=1, parent=r)                                   # bench
    add('cube', '6A4A30', (-6.5, -2.75, 1.4), scale=(3.2, 0.1, 0.6), size=1, parent=r)
    for x in (-7.8, -5.2):
        add('cube', '3A3A3C', (x, -3.2, 0.45), scale=(0.12, 0.8, 0.9), size=1, parent=r)
    for i in range(160):                                                                                                  # grass tufts and daisies
        x, y = -18 + 36 * rnd(i, 42), -16 + 22 * rnd(i, 43)
        if abs(x) < 2.0:
            continue
        add('cone', ('4E7A36', '5E8A3E', 'F4F0E0')[i % 3], (x, y, 0.25), rot=(0.2 * (rnd(i, 44) - 0.5), 0, 0), radius1=0.12, radius2=0.0,
            depth=0.5, vertices=3, parent=r)
    S['park'] = r


# ---------------------------------------------------------------- people
def walter_head(head):
    d = K.human_head('E8C0A0', '5A3E2A')(head)
    add('cube', 'F2F0EA', (0, -0.08, -0.36), scale=(0.34, 0.22, 0.1), size=1, parent=head)                                # shirt collar
    return d


def hardhat(col):
    def fn(head):
        d = K.human_head('E6B896', '3A2E24')(head)
        add('uv_sphere', col, (0, 0.0, 0.2), scale=(1.0, 1.08, 0.75), radius=0.33, segments=10, ring_count=5, parent=head, rough=0.4)
        add('cylinder', col, (0, -0.05, 0.16), scale=(1.0, 1.15, 1.0), radius=0.4, depth=0.04, vertices=12, parent=head, rough=0.4)
        return d
    return fn


def hatted(skin, hair, hat=None):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        if hat:
            add('cylinder', hat, (0, 0.02, 0.28), radius=0.42, depth=0.04, vertices=10, parent=head)
            add('cylinder', hat, (0, 0.02, 0.4), radius=0.27, depth=0.24, vertices=8, parent=head)
        return d
    return fn


CROWD = (('8A6A2E', '3A3A44', 'E4B892', '6A4A30', None), ('3E6A6A', '6A5A44', 'C89A78', '2A2420', '4A4A4C'),
         ('A04A2E', '2E3A52', '8A5A3E', '1E1A18', None), ('D8CCB0', '4A4A54', 'F0C8A8', 'B8904A', '6A5A44'),
         ('4A5A7A', '3A3630', 'B07A56', '2A2420', None), ('6A4A3A', '2E3A52', 'D8A884', '7A5A3A', '3A3A3C'))


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    _PROTO.clear()
    _LAST[0] = None
    K.add, K.empty = add, empty                 # the rigs and heads in kit3d use the same fast path
    S = {}
    make_beach(S)
    make_lot(S)
    make_dozer(S)
    make_show(S)
    make_park(S)
    S['gulls'] = [gull(i) for i in range(3)]
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['walt'] = wa = K.Rig(dict(top='7A5A3E', pants='4A4440', hand='E8C0A0', boot='2A2018', fore='7A5A3E'), walter_head)
    add('cube', '7A2A2A', (0, -0.33, 0.85), scale=(0.1, 0.03, 0.4), size=1, parent=wa.body)                                 # tie
    S['thorn'] = th = K.Rig(dict(top='BCD0DC', pants='8A7A5A', hand='E6B896', boot='3A2A1E', fore='BCD0DC'), hardhat('F2F2EE'))
    S['clip'] = add('cube', '8A6A44', (0.0, -0.18, -0.62), rot=(0.4, 0, 0), scale=(0.45, 0.04, 0.6), size=1, parent=th.el[0])
    add('cube', 'F4F2EA', (0, -0.03, 0.02), scale=(0.85, 1.2, 0.8), size=1, parent=S['clip'])
    S['workers'] = [K.Rig(dict(top=c, pants='3A3E48', hand='C89A78', boot='2A2018', fore=c), hardhat('E8C040')) for c in ('5A6A7A', '6A5A4A')]
    S['carry'] = [add('cube', '9A6038', (0, -0.55, -0.55), scale=(0.98, 0.72, 0.56), size=1, parent=w.el[1]) for w in S['workers']]
    S['sales'] = K.Rig(dict(top='C8A040', pants='4A3A2E', hand='F0C8A8', boot='1E1A18', fore='C8A040'), hatted('F0C8A8', '2A2420'))
    S['crowd'] = [K.Rig(dict(top=c[0], pants=c[1], hand=c[2], boot='2A2018', fore=c[0]), hatted(c[2], c[3], c[4])) for c in CROWD]
    S['humans'] = [wa, th] + S['workers'] + [S['sales']] + S['crowd']
    S['cast_all'] = [S['rook']] + S['humans']
    # props
    S['tape'] = keep(empty(FAR))
    add('cube', 'E8C030', (0, 0, 0), scale=(0.3, 0.18, 0.3), size=1, parent=S['tape'], rough=0.5)
    S['strip'] = add('cube', 'F0D040', (0, 0, 0), scale=(1, 0.06, 0.012), size=1, parent=S['tape'], rough=0.5)
    S['mag'] = keep(empty(FAR))
    add('torus', 'C89A3A', (0, 0, 0), rot=(PI / 2, 0, 0), major_radius=0.22, minor_radius=0.03, major_segments=14, minor_segments=4, parent=S['mag'], rough=0.3)
    add('cylinder', 'D8F0FF', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.21, depth=0.01, vertices=14, parent=S['mag'], rough=0.05, alpha=0.25)
    add('cylinder', '3A2A1E', (0, 0, -0.42), radius=0.035, depth=0.42, vertices=6, parent=S['mag'])
    S['shell'] = keep(add('cone', 'F4E6DC', FAR, scale=(1.0, 0.35, 1.0), radius1=0.2, radius2=0.03, depth=0.2, vertices=9, rough=0.25, emit=0.6))
    S['chunks'] = [keep(blubber(i)) for i in range(36)]
    S['sand'] = [keep(puff(('EADCC0', 'DCC8A4', 'F4EAD6', 'D0BC94')[i % 4], i)) for i in range(40)]
    S['puffs'] = [keep(puff('E6D6B6', 300 + i)) for i in range(10)]
    S['flash'] = keep(add('ico_sphere', 'FFC870', FAR, radius=1, subdivisions=2, emit=5.0))
    S['blamp'] = light(FAR, 0, 'FFC880', kind='POINT')
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
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 9000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w41')
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
    for l in (S['sun'], S['blamp'], S['glint']):
        l.data.energy = 0
    intact(S, True)
    crush(S['hero'], 0.0)
    for o in S['carry']:
        o.hide_render = True
    S['clip'].hide_render = True
    S['plunger'].location.z = 0.9
    for g in S['gulls']:
        flap(g, 0.2)
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, hat_to=(0.74, -0.14, -1.45), laugh=0.0, hat_drop=0.0)
    S['cam'].rotation_euler = (0, 0, 0)


def intact(S, yes):
    """Before the blast (whale, crates, wire) or after it (hole, rim, chunks on the sand, only the tail left)."""
    for o in S['wbody'] + [c for cr in S['crates'] for c in cr.children] + S['wire']:
        o.hide_render = not yes
    for o in S['crater'] + S['litter'] + [c for o in S['litter'] for c in o.children]:
        o.hide_render = yes
    S['whale'].location = (0, 0, 0) if yes else (-1.5, 0.8, -0.3)


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
    """A point on the beach set's ground."""
    return (x, y, gz(x, y) + dz)


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def head(rig):
    return wpos(rig.head)


def surf(S, t):
    for i, o in enumerate(S['waves']):
        u = (t * 0.12 + i / 6) % 1
        o.location = (0, lerp(64, 28, u), 0.09)
        o.scale = (3000, (0.7 + 0.5 * rnd(i, 1)) * (0.4 + 0.6 * math.sin(PI * u)), 0.08)


def column(S, u, c=(0, -1, 0), scale=1.0, chunks=True):
    """The blast at time u (s) after the plunger: a flash, a column of sand and whale going up, chunks flung out."""
    if u < 0:
        return
    if u < 0.12:
        S['blamp'].location = plus(c, (0, -1.5, 4))
        S['blamp'].data.energy = 2.5e5 * (1 - u / 0.12) * scale
    g = 22.0
    for i, o in enumerate(S['sand']):
        a = rnd(i, 50) * 2 * PI
        vz = (24 + 22 * rnd(i, 51)) * scale
        vr = (2.5 + 6 * rnd(i, 52)) * scale
        z = vz * u - 0.5 * g * u * u * (0.35 + 0.3 * rnd(i, 53))
        if z < -2:
            o.location = FAR
            continue
        s = scale * (0.8 + 3.2 * min(u, 1.6)) * (0.5 + 0.7 * rnd(i, 54))
        o.location = plus(c, (vr * u * math.cos(a), vr * u * math.sin(a), max(0.0, z) + 1))
        o.scale = (s, s, s * 0.9)
        o.rotation_euler = (u + i, 0.5 * u, i)
    if not chunks:
        return
    for i, o in enumerate(S['chunks']):
        a = rnd(i, 55) * 2 * PI
        vz = (14 + 22 * rnd(i, 56)) * scale
        vr = (5 + 16 * rnd(i, 57)) * scale
        z = 1.5 + vz * u - 0.5 * g * u * u
        if z < -0.5:
            o.location = FAR
            continue
        s = scale * (0.35 + 1.1 * rnd(i, 58))
        o.location = plus(c, (vr * u * math.cos(a), vr * u * math.sin(a) - 2 * u, z))
        o.scale = (s, s * 0.8, s * 0.6)
        o.rotation_euler = (u * 5 * rnd(i, 59), u * 4, i)


def rain(S, ctr, t, n=16, area=(12, 8), h=26.0, rate=0.8, i0=0, ground=None, dz=0.0):
    """Chunks dropping out of the sky round ctr, each with a puff of sand where it lands."""
    p = 0
    for j in range(n):
        i = i0 + j
        ph = t * rate * (0.7 + 0.6 * rnd(i, 60)) + rnd(i, 61)
        cyc, u = math.floor(ph), ph % 1
        x = ctr[0] + (rnd(i + cyc * 7, 62) - 0.5) * area[0]
        y = ctr[1] + (rnd(i + cyc * 7, 63) - 0.5) * area[1]
        g0 = (ground(x, y) if ground else ctr[2]) + dz
        o = S['chunks'][i]
        land = 0.82
        s = 0.4 + 0.9 * rnd(i, 64)
        if u < land:
            k = u / land
            o.location = (x - 3 * (1 - k), y + 2 * (1 - k), lerp(g0 + h, g0 + 0.3 * s, k * k))
            o.rotation_euler = (u * 9, u * 6, i)
            o.scale = (s, s * 0.8, s * 0.6)
        else:
            o.location = (x, y, g0 + 0.25 * s)
            o.scale = (s * 1.2, s, s * 0.35)
            o.rotation_euler = (0, 0, i)
            if p < len(S['puffs']):
                q = (u - land) / (1 - land)
                pf = S['puffs'][p]
                ps = s * (0.6 + 1.6 * q)
                pf.location, pf.scale = (x, y, g0 + 0.3 + 0.5 * q), (ps, ps, ps * 0.6)
                p += 1


def splat(S, pos, u, idx=0, s=0.9):
    """One chunk dropping onto pos: u<0 in the air above, 0 at the hit, then lying there with a puff."""
    o = S['chunks'][idx]
    if u < -1:
        return
    if u < 0:
        o.location = (pos[0] - 2 * u, pos[1] + 1 * u, pos[2] - 18 * u * (0.5 - 0.5 * u) + 0.3)
        o.scale = (s, s * 0.8, s * 0.6)
        o.rotation_euler = (u * 8, u * 5, idx)
    else:
        o.location = plus(pos, (0, 0, 0.25 * s))
        o.scale = (s * 1.25, s, s * 0.36)
        pf = S['puffs'][idx % len(S['puffs'])]
        q = min(1.0, u / 0.5)
        ps = s * (0.5 + 1.8 * q) * (1 - 0.5 * q)
        pf.location, pf.scale = plus(pos, (0, 0, 0.3 + 0.6 * q)), (ps, ps, ps * 0.6)


def crowd_on_ridge(S, t, duck=0.0, run=0.0, face='wide', n=6, y0=-67.0):
    """The spectators along the dune ridge, faces towards the whale (+Y)."""
    for j, rig in enumerate(S['crowd'][:n]):
        x = -10 + 4.0 * j + 1.2 * rnd(j, 70)
        y = y0 - 2.5 * rnd(j, 71) - run * 6 * (0.6 + 0.4 * rnd(j, 72))
        d = min(1.0, max(0.0, duck * 1.5 - 0.15 * j))
        pose = blend(P('stand', aR=(0.3 + 0.9 * rnd(j, 73), 0.2, 0.4), head=(-0.15, 0.1 * (j - 3))),
                     P('brace', aL=(2.4, 0.8, 1.9), aR=(2.4, 0.8, 1.9), head=(0.5, 0.0)), d)
        if run > 0:
            pose = dict(K.walk(t + 0.37 * j, 2.6), lean=0.25, aL=(2.2, 0.7, 1.8), aR=(2.0, 0.7, 1.9))
        stand(rig, on(x, y), PI if run == 0 else 0.0, pose, face)


# ---------------------------------------------------------------- hook
def blast_close(S, k, t, lt):
    """Low beside the dead whale's flank, the cases stacked against it: the beach erupts in a flash and a column of
    sand and whale. First shot; played without the blast as the last shot (the loop)."""
    sky(S, 'day')
    surf(S, t)
    loop = S['prm'].get('loop')
    d = lt / max(k, 1e-3) if k > 0 else 1.0
    if loop:
        u = sm(k / 0.95)
        cam(S, (lerp(10.5, 7.5, u), lerp(-15.5, -11.0, u), lerp(2.6, 1.3, u)), (lerp(-1.0, -1.5, u), lerp(-1.2, -0.8, u), lerp(2.6, 2.3, u)), lerp(24, 22, u))
        return
    ub = lt - TB
    if ub > 0:
        column(S, ub, (0, -3.5, 0), 0.55)
        for cr in S['crates']:
            for c in cr.children:
                c.hide_render = ub > 0.03
    sh = 0.25 * math.exp(-max(0, ub) * 3) if ub > 0 else 0.0
    cam(S, (7.5 + sh * math.sin(t * 61), -11.0 - 1.2 * max(0, ub), 1.3 + sh * math.cos(t * 53)), (-1.5, -0.8, 2.3 + 2.5 * sm(ub / 0.6)), 22)


def column_wide(S, k, t, lt, u0=0.75):
    sky(S, 'day')
    surf(S, t)
    column(S, u0 + lt, (0, -2, 0), 1.0)
    for j, rig in enumerate(S['crowd'][:5]):
        x = -9 + 4.4 * j
        stand(rig, on(x, -68.5 - 1.5 * rnd(j, 74)), PI + 0.1 * (j - 2), P('stand' if j % 2 else 'point', aL=(0.3, 0.3, 0.6), head=(-0.35, 0.0)), 'wide')
    cam(S, (lerp(5, 4, k), -80.5, 9.6), (0, -10, lerp(14, 22, k)), 30)


def column_shot(S, k, t, lt):
    """From the dunes behind the crowd: a column of sand and whale climbing high over the beach, chunks arcing out of it."""
    column_wide(S, k, t, lt)


def chunk_lens(S, k, t, lt):
    """Looking up from the dune: one big lump of blubber tumbles out of the sky straight at the lens; more sail over."""
    sky(S, 'day')
    u = sm(k)
    o = S['chunks'][0]
    o.location = (lerp(-6, 0.6, u), lerp(-36, -67.2, u), lerp(34, 8.6, u ** 1.4))
    s = 1.5
    o.scale = (s, s * 0.8, s * 0.6)
    o.rotation_euler = (2.4 + 0.8 * math.sin(t * 2.2), 0.5 * t, 0.4)
    for j in range(1, 8):
        a = (lt * 0.9 + rnd(j, 80)) % 1
        S['chunks'][j].location = (-30 + 60 * rnd(j, 81) + 10 * a, lerp(-30, -110, a), 30 + 12 * rnd(j, 82) - 10 * a * a)
        sj = 0.6 + 0.8 * rnd(j, 83)
        S['chunks'][j].scale = (sj, sj * 0.8, sj * 0.6)
        S['chunks'][j].rotation_euler = (a * 7, a * 5, j)
    for i, o2 in enumerate(S['sand'][:12]):
        o2.location = (-10 + 20 * rnd(i, 84), lerp(-20, -30, k) - 10 * rnd(i, 85), 22 + 14 * rnd(i, 86))
        s2 = 4 + 4 * rnd(i, 87)
        o2.scale = (s2, s2, s2 * 0.8)
    cam(S, on(1.0, -70.5, 1.6), (lerp(-3, -1, k), -40, 26), 24)


def rain_crowd(S, k, t, lt):
    """The crowd on the ridge: chunks thud into the sand round them, people duck with their arms over their heads."""
    sky(S, 'day')
    crowd_on_ridge(S, t, duck=sm(k / 0.4), face='wide')
    rain(S, (0, -68, 0), t, n=14, area=(22, 10), h=22, rate=1.3, ground=gz)
    splat(S, on(-2.6, -66.6), (lt - 0.45) / 0.35, 20, 1.0)
    cam(S, on(3.6, -62.6, 2.3), on(-1.0, -68.0, 2.0), 24)


# ---------------------------------------------------------------- doubt
def rook_dune(S, k, t, lt):
    """Rook on the ridge, arms crossed, hat brim low, the column climbing behind him: 'Raining whale? Not a chance.'
    A lump of blubber slaps into the sand beside him and his hat hops."""
    sky(S, 'day')
    surf(S, t)
    column(S, 1.9 + lt, (0, -2, 0), 1.0)
    rk = S['rook']
    hit = (lt - 0.95) / 0.3
    jump = sm(hit * 2) * (1 - sm((hit - 0.6) * 2)) if hit > 0 else 0.0
    pose = blend(P('cross', head=(0.1, 0.0)), P('brace', aL=(0.9, 0.9, 1.0), aR=(1.2, 0.9, 1.0), head=(-0.1, 0.4)), sm(hit * 3))
    stand(rk, on(-4.0, -66.5), 0.1, pose)
    S['rface'] = 'low' if hit < 0 else 'shocked'
    S['hat_tip'] = 0.85 if hit < 0 else 0.2
    S['hat_jump'] = 0.5 * jump
    splat(S, on(-2.4, -66.2), hit, 21, 1.1)
    for j, rig in enumerate(S['crowd'][:3]):
        stand(rig, on(4 + 4 * j, -68 - j), PI, P('stand', head=(-0.3, 0)), 'wide')
    h = head(rk)
    cam(S, plus(h, (1.0, -6.4, -0.5)), plus(h, (0.4, 0.0, 0.8)), 30)


# ---------------------------------------------------------------- rain
def overhead_chunk(S, k, t, lt):
    """Flat on the dune among the grass, looking up: chunks of blubber sail across the sky over everyone's heads."""
    sky(S, 'day')
    for j in range(9):
        a = (lt * 0.7 + j / 9) % 1
        o = S['chunks'][j]
        o.location = (lerp(-26, 26, a) + 6 * (rnd(j, 90) - 0.5), -88 - 14 * rnd(j, 91) - 6 * a, gz(0, -88) + 9 + 9 * rnd(j, 93) + 5 * math.sin(PI * a))
        s = 1.1 + 1.3 * rnd(j, 92)
        o.scale = (s, s * 0.8, s * 0.6)
        o.rotation_euler = (a * 8, a * 5, j)
    for j, rig in enumerate(S['crowd'][:3]):
        stand(rig, on(-3.5 + 3.5 * j, -86.5 - 0.8 * j), PI * 0.1 * (j - 1), P('up', aL=(2.4, 0.5, 1.2), aR=(2.4, 0.5, 1.2), head=(-0.6, 0.0)), 'wide')
    cam(S, on(0.5, -79.5, 1.4), on(0.0, -92.0, 7.5), 20, roll=lerp(-0.05, 0.08, k))


def run_cars(S, k, t, lt):
    """From the parking lot: people pour down the back of the dunes towards their cars; lumps drop between them."""
    sky(S, 'day')
    for j, rig in enumerate(S['crowd']):
        x = -10 + 4.2 * j
        y = lerp(-104, -129, min(1.0, k * 0.85 + 0.15 * rnd(j, 93)))
        stand(rig, on(x, y), 0.15 * (j - 3), dict(K.walk(t + 0.3 * j, 2.8), lean=0.22, aL=(2.1, 0.6, 1.7), aR=(1.9, 0.6, 1.8)), 'wide')
    rain(S, (0, -108, 0), t, n=12, area=(30, 18), h=26, rate=1.1, ground=gz)
    column(S, 3.4 + lt, (0, -2, 0), 1.0, chunks=False)
    cam(S, (lerp(11.5, 10.5, k), -143.5, 2.6), (-1.0, -114, 3.0), 32)


def rook_duck(S, k, t, lt):
    """Rook sprints down the dune clamping his hat on; a lump slaps down in front of him and he skids round it."""
    sky(S, 'day')
    rk = S['rook']
    y = lerp(-90, -101, k)
    x = -10 + 1.6 * sm((k - 0.35) / 0.3)
    hit = (lt - 0.38) / 0.3
    base = dict(K.walk(t, 3.0), lean=0.3, aR=(0.2, 1.9, 1.6, -1.5))
    stand(rk, on(x, y), 0.25 * sm((k - 0.3) / 0.3), base)
    S['rface'] = 'shocked' if hit > 0 else 'calm'
    S['hat_tip'] = 0.3
    splat(S, on(-9.6, -96.8), hit, 22, 1.2)
    rain(S, (-8, -98, 0), t, n=8, area=(16, 12), h=20, rate=1.2, i0=0, ground=gz)
    h = head(rk)
    cam(S, (h[0] + 2.6, h[1] - 7.0, h[2] - 0.6), (h[0] + 0.2, h[1], h[2] - 0.5), 30)


# ---------------------------------------------------------------- plan
def crates(S, k, t, lt):
    """Earlier that day: the stack of wooden cases against the whale's flank; two workmen in hard hats carry in more
    while the engineer in charge checks his clipboard."""
    sky(S, 'day')
    surf(S, t)
    for j, w in enumerate(S['workers']):
        x = lerp(-6.5, -2.2, k) - 2.4 * j
        stand(w, (x, -5.6 - 1.3 * j, 0), -PI / 2 + 0.25, dict(K.walk(t + 0.5 * j, 1.5), aL=(0.9, 0.2, 1.4, 0.3), aR=(0.9, 0.2, 1.4, -0.3)), 'hard')
        S['carry'][j].hide_render = False
    th = S['thorn']
    stand(th, (2.2, -7.6, 0), facing((2.2, -7.6), (0, -3.4)) + 0.4, P('stand', aL=(0.55, 0.1, 1.5, 0.6), aR=(0.4, 0.2, 0.6), head=(0.3 - 0.25 * sm((k - 0.5) / 0.3), 0.3)), 'calm')
    S['clip'].hide_render = False
    cam(S, (lerp(4.4, 2.2, k), lerp(-16.5, -13.6, k), lerp(3.6, 2.8, k)), (-0.6, -3.6, 1.6), 22)


def rook_count(S, k, t, lt):
    """Rook walks along the stack tapping each case with a wingtip, counting, and his eyes get wider at every one."""
    sky(S, 'day')
    rk = S['rook']
    x = lerp(4.6, -3.2, k)
    tap = abs(math.sin(lt * 9))
    stand(rk, (x, -5.0, 0), -PI / 2 + 0.5, dict(K.walk(t, 1.0), aR=(1.1, -0.4, 0.4 + 0.5 * tap), aL=(0.3, 0.2, 0.4), head=(0.15, 0.9 * sm((k - 0.7) / 0.2))))
    S['rface'] = 'shocked' if k > 0.72 else 'calm'
    S['hat_jump'] = 0.25 * sm((k - 0.75) / 0.1) * (1 - sm((k - 0.9) / 0.1))
    h = head(rk)
    cam(S, (h[0] - 0.6, h[1] - 5.6, h[2] - 0.3), (h[0] + 0.2, h[1] + 1.2, h[2] - 0.7), 30)


def _gull_shot(S, k, t, lt):
    """Rook and a seagull side by side on a log, the whale filling the sky behind them. The gull looks back at the whale,
    then at Rook. Rook shrugs."""
    sky(S, 'day')
    surf(S, t)
    rk = S['rook']
    rk.place((10.0, -16.25, 0.5), 0.15)
    sh = sm((k - 0.6) / 0.25)
    rk.apply(blend(P('sit', lL=(1.35, 1.5), lR=(1.35, 1.5), head=(0.0, 0.0)), P('shrug', lL=(1.35, 1.5), lR=(1.35, 1.5), lift=-0.5, lean=0.1), sh))
    S['rface'] = 'low' if sh > 0.3 else 'calm'
    g = S['gulls'][0]
    g['root'].location = (11.95, -16.1, 1.12)
    g['root'].scale = (1.7, 1.7, 1.7)
    look = sm((k - 0.1) / 0.2) * (1 - sm((k - 0.45) / 0.15))
    g['root'].rotation_euler = (0, 0, PI / 2 + lerp(0, PI, look) - 0.9 * sm((k - 0.45) / 0.15))
    fl = sm((k - 0.05) / 0.1) * (1 - sm((k - 0.45) / 0.1))
    flap(g, 0.15 + 0.9 * fl * (0.5 + 0.5 * math.sin(lt * 26)))
    cam(S, (lerp(14.6, 13.0, k), lerp(-24.0, -21.0, k), lerp(2.4, 1.8, k)), (10.9, -15.4, 1.9), 30)


def wire(S, k, t, lt):
    """At the foot of the dunes: the wire runs across the sand to a wooden blasting machine. A workman in a hard hat
    kneels behind it checking the T-handle, the whale far behind him. (Who pushed the plunger is not on record here,
    so it is a generic workman, not the engineer.)"""
    sky(S, 'day')
    surf(S, t)
    th = S['workers'][1]
    th.place((-22.3, -42.6, 0), PI - 0.3)
    th.apply(P('stand', lL=(1.5, 2.3), lR=(-0.2, 1.9), lift=-0.75, lean=0.4, aL=(1.0, 0.3, 0.6), aR=(1.0, -0.1, 0.6), head=(0.1, 0.0)))
    th.face = 'hard'
    cam(S, (lerp(-15.0, -19.8, k), lerp(-47.0, -48.8, k), lerp(0.7, 1.2, k)), (lerp(-19.0, -22.0, k), -43.6, 1.1), 28)


# ---------------------------------------------------------------- the warning
def expert(S, k, t, lt):
    """A man in a sports coat at the cases, frowning, slowly shaking his head. Rook, beside him, copies the head shake."""
    sky(S, 'day')
    wa, rk = S['walt'], S['rook']
    shake = 0.35 * math.sin(lt * 5.5) * sm(k / 0.2)
    stand(wa, (3.6, -8.2, 0), facing((3.6, -8.2), (0, -3.4)), P('cross', head=(0.15, shake)), 'hard')
    stand(rk, (5.5, -8.6, 0), facing((5.5, -8.6), (0.5, -3.4)), P('cross', head=(0.15, 0.35 * math.sin(lt * 5.5 - 0.6) * sm((k - 0.3) / 0.2))))
    S['rface'] = 'squint'
    S['hat_tip'] = 0.4
    cam(S, (lerp(1.2, 2.4, k), lerp(-4.2, -5.0, k), lerp(2.9, 2.5, k)), (4.5, -8.4, 2.35), 30)


def warn_talk(S, k, t, lt):
    """He points hard at the cases and talks; the engineer, clipboard in hand, waves him away."""
    sky(S, 'day')
    surf(S, t)
    wa, th = S['walt'], S['thorn']
    pt = sm(k / 0.25)
    stand(wa, (-6.4, -10.0, 0), facing((-6.4, -10), (-3.0, -10.6)) - 0.5, blend(P('stand'), P('point', aR=(1.4, -0.1, 0.1), head=(0.0, 0.3)), pt), 'hard')
    wa.jawv = 0.5 + 0.5 * math.sin(lt * 16)
    wave = sm((k - 0.45) / 0.2)
    stand(th, (-3.2, -10.4, 0), facing((-3.2, -10.4), (-6.4, -10.0)), blend(P('stand', aL=(0.9, 0.1, 1.6, 0.6)), P('stand', aL=(0.9, 0.1, 1.6, 0.6), aR=(1.0, 0.9, 1.4, -0.6 + 0.5 * math.sin(lt * 12)), head=(0.0, -0.4)), wave), 'calm')
    S['clip'].hide_render = False
    th.jawv = 0.3 * wave * (0.5 + 0.5 * math.sin(lt * 14))
    cam(S, (lerp(-1.8, -6.6, k), lerp(-16.4, -15.6, k), lerp(3.2, 2.5, k)), (-4.8, -9.6, 2.2), 30)


def walk_back(S, k, t, lt):
    """While the crowd stays on the ridge, he strides off over the back of the dunes, far behind everyone, towards
    the shiny new car in the lot."""
    sky(S, 'day')
    crowd_on_ridge(S, t, face='calm')
    wa = S['walt']
    u = min(1.0, k / 0.62)
    y = lerp(-83, -93.5, sm(u))
    turn = sm((k - 0.62) / 0.2)
    if turn <= 0:
        stand(wa, on(-9, y), 0.05, K.walk(t, 1.6), 'hard')
    else:
        stand(wa, on(-9, y), lerp(0.05, PI, turn), blend(P('stand'), P('cross', head=(-0.1, 0)), turn), 'hard')
    cam(S, (lerp(-9.5, -7.6, k), lerp(-97.0, -100.5, k), lerp(7.0, 7.8, k)), (-6.6, -72.0, 6.9), 28)


def rook_eye(S, k, t, lt):
    """Rook crouched in the beach grass holds up a magnifying glass, follows the man walking away behind everyone,
    then lowers it and gives us one raised brow."""
    sky(S, 'day')
    rk = S['rook']
    low = sm((k - 0.6) / 0.2)
    stand(rk, on(-6, -82), 0.35 - 0.35 * low, P('stand', lL=(0.5, 0.9), lR=(0.2, 0.7), lift=-0.3, lean=0.25,
                                                 aR=(lerp(1.35, 0.7, low), -0.3, lerp(1.55, 1.6, low), 0.3), aL=(0.5, 0.2, 0.9), head=(0.0, 0.0)))
    S['rface'] = 'squint' if low < 0.5 else 'low'
    S['hat_tip'] = 0.2
    hd = head(rk)
    yaw = 0.35 - 0.35 * low
    S['mag'].location = plus(hd, (lerp(0.15, 0.55, low) * math.cos(yaw) + 0.5 * math.sin(yaw) * (1 - low), -lerp(0.55, 0.35, low), lerp(0.05, -0.75, low)))
    S['mag'].rotation_euler = (0.0, 0, yaw)
    wa = S['walt']
    stand(wa, on(-15, -96), 0.0, P('cross'), 'hard')
    h = head(rk)
    cam(S, plus(h, (lerp(2.0, 0.8, k), lerp(-5.0, -3.4, k), -0.2)), plus(h, (0.1, 0.0, -0.15)), 32)


# ---------------------------------------------------------------- the car
def slab_fall(S, k, t, lt):
    """In the lot: a big slab of blubber tumbles down out of the sky, growing, right over the cars."""
    sky(S, 'day')
    sl = S['slab']
    u = sm(k)
    sl.location = (CARP[0] + lerp(-5, -1, u), CARP[1] + lerp(7, 0.5, u), lerp(22, 6.5, u))
    sl.scale = (2.6, 2.0, 0.95)
    sl.rotation_euler = (2.6 + 0.5 * math.sin(t * 3), 0.4 * math.sin(t * 2), 0.3 + t)
    cam(S, (CARP[0] - 7.5, CARP[1] - 10.0, 1.3), (CARP[0] - 1.5, CARP[1] + 2, lerp(9, 6, k)), 20)


def car_crush(S, k, t, lt):
    """The slab lands on the gold sedan's roof: the roof caves in, the car bucks on its springs, sand jumps."""
    sky(S, 'day')
    hit = 0.3
    u = (k - hit) / 0.08
    sl = S['slab']
    hc = S['hero']
    if k < hit:
        a = k / hit
        sl.location = (CARP[0] - 0.8, CARP[1], lerp(26, 3.0, a * a))
        sl.rotation_euler = (a * 2, a * 1.4, 0.3)
    else:
        crush(hc, sm(u))
        sl.location = (CARP[0] - 0.8, CARP[1], lerp(3.0, 2.25, sm(u)))
        sl.rotation_euler = (2.0, 1.4, 0.3)
        b = math.exp(-(k - hit) * 9) * math.sin((k - hit) * 70)
        hc['root'].location = (CARP[0], CARP[1], -0.12 * b)
        hc['root'].rotation_euler = (0.03 * b, 0, 0)
        for j in range(5):
            q = min(1.0, (k - hit) / 0.4)
            pf = S['puffs'][j]
            a = j * 1.26
            ps = (0.5 + 0.9 * q) * (1 - 0.7 * q)
            pf.location = (CARP[0] + 4.8 * math.cos(a) * (0.7 + 0.6 * q), CARP[1] + 2.2 * math.sin(a) * (0.7 + 0.6 * q), 0.3 + 0.5 * q)
            pf.scale = (ps, ps, ps * 0.6)
    cam(S, (CARP[0] - 8.0, CARP[1] - 9.0, lerp(3.8, 3.4, k)), (CARP[0] - 0.4, CARP[1], 1.6), 26)


def owner_face(S, k, t, lt):
    """His face, close: he stares at what is left of his new car, and his jaw drops."""
    sky(S, 'day')
    crush(S['hero'], 1.0)
    S['slab'].location, S['slab'].rotation_euler = (CARP[0] - 0.8, CARP[1], 2.25), (2.0, 1.4, 0.3)
    wa = S['walt']
    loc = (CARP[0] - 13, CARP[1] - 9, 0)
    drop = sm((k - 0.15) / 0.25)
    stand(wa, loc, facing(loc, CARP), P('stand', aL=(0.5 * drop, 0.4, 0.6), aR=(0.5 * drop, 0.4, 0.6), head=(-0.05, 0.0)), 'wide' if drop > 0.3 else 'hard')
    wa.jawv = 0.9 * drop
    h = head(wa)
    d = Vector((CARP[0] - loc[0], CARP[1] - loc[1], 0)).normalized()
    q = lerp(3.4, 2.2, sm(k)) + 0.08 * math.sin(lt * 40) * math.exp(-max(0.0, k - 0.2) * 6) * (k > 0.2)
    cam(S, plus(h, (d.x * q - d.y * 0.6, d.y * q + d.x * 0.6, lerp(0.3, -0.15, k))), plus(h, (0, 0, -0.05)), 34)


def rook_roof(S, k, t, lt):
    """Rook on the crumpled roof beside the slab pulls out a tape measure and runs it along the blubber, then pinches
    his beak shut against the smell."""
    sky(S, 'day')
    crush(S['hero'], 1.0)
    S['slab'].location, S['slab'].rotation_euler = (CARP[0] - 0.8, CARP[1], 2.25), (2.0, 1.4, 0.3)
    rk = S['rook']
    pinch = sm((k - 0.62) / 0.15)
    pose = blend(P('stand', aR=(1.25, 0.9, 0.2), aL=(0.9, -0.2, 0.6), head=(0.35, -0.5)), P('tap', head=(0.1, 0.0)), pinch)
    stand(rk, (CARP[0] + 2.3, CARP[1] - 0.2, 1.52), -PI / 2 + 0.55, pose)
    S['rface'] = 'squint' if pinch > 0.5 else 'calm'
    S['hat_tip'] = 0.3
    if pinch < 0.5:
        hl = wpos(rk.el[0], (0, -0.06, -0.6))
        S['tape'].location = hl
        S['tape'].rotation_euler = (0, 0, facing((0, 0), (-1, 0.3)) + PI / 2)
        L = lerp(0.2, 2.8, sm(k / 0.45))
        S['strip'].scale = (L, 0.06, 0.012)
        S['strip'].location = (-L / 2, 0, -0.05)
    h = head(rk)
    cam(S, plus(h, (lerp(3.6, 1.0, k), lerp(-3.8, -5.0, k), lerp(-0.2, -0.8, k))), plus(h, (-0.9, 0.3, -1.0)), 28)


# ---------------------------------------------------------------- the deal
def showroom(S, k, t, lt):
    """Days before, at a car dealer's forecourt under bunting: 'A WHALE OF A DEAL!' on the banner, the same gold sedan
    with a big ribbon bow. The salesman drops the keys into the man's hand; he grins."""
    sky(S, 'show')
    for i, f in enumerate(S['flags']):
        f.rotation_euler = (PI + 0.35 * math.sin(t * 6 + i * 0.7), 0.2 * math.sin(t * 4 + i), 0)
    sa, wa = S['sales'], S['walt']
    give = sm((k - 0.25) / 0.3)
    stand(sa, at(SHOW, -3.4, -4.2, 0), facing((-3.4, -4.2), (-1.4, -5.6)), blend(P('stand'), P('stand', aR=(1.2, 0.0, 0.3), head=(0.1, 0.0)), give), 'warm')
    sa.jawv = 0.4 + 0.4 * math.sin(lt * 15)
    stand(wa, at(SHOW, -1.4, -5.6, 0), facing((-1.4, -5.6), (-3.4, -4.2)), blend(P('stand'), P('stand', aL=(1.1, 0.0, 0.4), head=(0.1, 0.0)), give), 'warm')
    hr = wpos(sa.el[1], (0, -0.05, -0.62)) if give < 0.8 else wpos(wa.el[0], (0, -0.05, -0.62))
    S['keys'].location = hr
    S['keys'].rotation_euler = (t * 3, 0.4, t * 2)
    cam(S, at(SHOW, lerp(3.4, 0.6, k), lerp(-15.0, -11.6, k), lerp(1.8, 2.6, k)), at(SHOW, -1.8, 1.0, 3.6), 22)


def rook_laugh(S, k, t, lt):
    """Back at the flattened car: Rook doubles over with a cawing laugh and slaps the crumpled roof."""
    sky(S, 'day')
    crush(S['hero'], 1.0)
    S['slab'].location, S['slab'].rotation_euler = (CARP[0] - 0.8, CARP[1], 2.25), (2.0, 1.4, 0.3)
    rk = S['rook']
    slap = max(0.0, math.sin(lt * 9))
    stand(rk, (CARP[0] + 1.0, CARP[1] - 3.3, 0), 0.3 + PI * 0.12, P('wash', aR=(1.0 + 0.9 * slap, 0.5, 0.4), aL=(0.6, 0.4, 1.7, 0.4), lean=0.72, lL=(0.35, 0.3), lR=(0.35, 0.3), head=(-0.45, 0.0)))
    S['rface'] = 'laugh'
    S['laugh'] = 1.0
    S['hat_jump'] = 0.2 * slap
    rk.root.location.z += 0.12 * slap
    h = head(rk)
    cam(S, plus(h, (4.4, -2.6, 0.1)), plus(h, (-0.4, 0.6, -0.7)), 28)


# ---------------------------------------------------------------- the clean-up
def dozer_at(S, x, y, yaw=PI):
    d = S['dozer']
    d.location, d.rotation_euler = (x, y, 0), (0, 0, yaw)
    return d


def bulldozer(S, k, t, lt):
    """Afterwards: the hole in the sand and lumps of whale everywhere; a bulldozer shoves a wave of sand over them."""
    sky(S, 'day')
    surf(S, t)
    intact(S, False)
    x = lerp(16, 9, k)
    dozer_at(S, x, -6)
    for i, o in enumerate(S['mound']):
        o.location = (x - 4.4 - 0.6 * rnd(i, 100), -6 + (i - 3) * 0.75, 0.3 + 0.2 * rnd(i, 101))
        s = 0.9 + 0.5 * rnd(i, 102) + 0.4 * k
        o.scale = (s, s * 0.9, s * 0.55)
    dr = S['workers'][0]
    dr.place(wpos(S['dozer'], (-1.0, 0, 2.2)), -PI / 2)
    dr.apply(P('sit', aL=(1.2, 0.1, 0.9), aR=(1.2, 0.1, 0.9)))
    dr.face = 'hard'
    for i, o in enumerate(S['puffs'][:6]):
        q = (t * 0.9 + i / 6) % 1
        o.location = (x + 2.2 - 0.6 * q, -6.6 + 0.4 * i, 4.6 + 2.6 * q)
        s2 = 0.25 + 0.6 * q
        o.scale = (s2, s2, s2)
    cam(S, (lerp(22.5, 20.5, k), -17.0, 4.6), (4.0, -3.0, 1.2), 26)


def rook_nose(S, k, t, lt):
    """Rook rides on the bulldozer's track guard, one hand pinching his beak, the other fanning the air with his hat."""
    sky(S, 'day')
    intact(S, False)
    x = lerp(14, 8.5, k)
    dozer_at(S, x, -6)
    for i, o in enumerate(S['puffs'][:6]):
        q = (t * 1.2 + i / 6) % 1
        o.location = (x + 2.2 - 0.8 * q, -6.6 + 0.4 * i, 4.6 + 3.0 * q)
        s2 = 0.25 + 0.7 * q
        o.scale = (s2, s2, s2)
    rk = S['rook']
    stand(rk, (8.0, -10.6, 0), 0.25,
          P('tap', aL=(1.4, 0.6, 1.2 + 0.5 * math.sin(lt * 10), 0.3), head=(0.1, 0.25)))
    S['rface'] = 'squint'
    S['hat_off'] = 1.0
    S['hat_to'] = (-0.8, -0.3 + 0.2 * math.sin(lt * 10), -0.6)
    dr = S['workers'][0]
    dr.place(wpos(S['dozer'], (-1.0, 0, 2.2)), -PI / 2)
    dr.apply(P('sit', aL=(1.2, 0.1, 0.9), aR=(1.2, 0.1, 0.9)))
    h = head(rk)
    cam(S, plus(h, (lerp(2.4, 0.4, k), -5.6, -0.2)), plus(h, (lerp(0.4, -0.6, k), 1.4, -0.4)), 28)


def engineer_turn(S, k, t, lt):
    """Quiet. The engineer stands at the edge of the hole, clipboard under his arm, looking at the mess. He turns to us."""
    sky(S, 'day')
    surf(S, t)
    intact(S, False)
    th = S['thorn']
    turn = sm((k - 0.3) / 0.45)
    stand(th, (-2.0, -9.0, 0), lerp(PI, 0.15, turn), P('stand', aL=(0.35, 0.1, 1.2, 0.6), head=(0.1, 0.0)), 'calm')
    S['clip'].hide_render = False
    cam(S, (lerp(0.6, -1.6, k), lerp(-16.0, -13.2, k), lerp(3.2, 2.6, k)), (-2.0, -9.0, 2.3), 30)


# ---------------------------------------------------------------- payoff
def engineer(S, k, t, lt):
    """The engineer, close, pleased with himself: he sweeps an arm back at the hole and the lumps, then turns to us with
    a firm nod and a thumbs-up. Behind him the bulldozer is already rolling across the sand."""
    sky(S, 'day')
    surf(S, t)
    intact(S, False)
    th = S['thorn']
    sweep = sm(k / 0.3) * (1 - sm((k - 0.45) / 0.2))
    up = sm((k - 0.5) / 0.2)
    nod = 0.2 * math.sin(lt * 8) * sm((k - 0.55) / 0.15)
    pose = blend(P('stand', aL=(0.35, 0.1, 1.2, 0.6), aR=(0.2, 0.25, 0.3)), P('stand', aL=(0.35, 0.1, 1.2, 0.6), aR=(1.2, 1.3, 0.2), head=(0.0, 0.6)), sweep)
    if up > 0:
        pose = blend(pose, P('stand', aL=(0.35, 0.1, 1.2, 0.6), aR=(1.0, 0.4, 1.25, 0.3), head=(nod, 0.0)), up)
    stand(th, (-2.0, -9.0, 0), 0.15 + 0.5 * sweep, pose, 'proud')
    th.jawv = 0.04
    S['clip'].hide_render = False
    x = lerp(-16, 4, k)
    dozer_at(S, x, 2.0, 0.0)
    for i, o in enumerate(S['mound']):
        o.location = (x + 4.4 + 0.6 * rnd(i, 100), 2.0 + (i - 3) * 0.75, 0.3 + 0.2 * rnd(i, 101))
        sc = 1.0 + 0.5 * rnd(i, 102)
        o.scale = (sc, sc * 0.9, sc * 0.55)
    for i, o in enumerate(S['puffs'][:6]):
        q = (t * 1.1 + i / 6) % 1
        o.location = (x - 2.2 + 0.8 * q, 1.6 + 0.4 * i, 4.6 + 3.0 * q)
        s2 = 0.25 + 0.7 * q
        o.scale = (s2, s2, s2)
    h = head(th)
    cam(S, plus(h, (lerp(2.6, -0.6, k), lerp(-4.4, -3.0, k), lerp(-0.6, -0.1, k))), plus(h, (lerp(-0.6, 0.05, k), 0.0, -0.25)), 32)


def rook_stare(S, k, t, lt):
    """Rook, deadpan among the lumps of whale. Very slowly, his hat brim drops over his eyes."""
    sky(S, 'day')
    surf(S, t)
    intact(S, False)
    rk = S['rook']
    stand(rk, (3.0, -10.0, 0), 0.2, P('hips', head=(0.05, 0.0)))
    S['rface'] = 'low'
    S['hat_tip'] = lerp(0.2, 0.9, sm((k - 0.25) / 0.6))
    S['hat_drop'] = sm((k - 0.3) / 0.55)
    h = head(rk)
    cam(S, plus(h, (0.5, -3.4, -0.35)), plus(h, (0.0, 0.0, -0.1)), 34)


def park_sign(S, k, t, lt):
    """Fifty years on: a little park in the pines by the river, rhododendrons round a wooden sign that reads
    EXPLODING WHALE MEMORIAL PARK."""
    sky(S, 'park')
    cam(S, at(PARK, lerp(4.0, 0.6, k), lerp(-17.5, -9.0, k), lerp(1.2, 2.8, k)), at(PARK, 0, 0, 2.6), 28)


def rook_park(S, k, t, lt):
    """Rook beside the sign takes off his hat and holds it to his chest, then gives the sign a solemn little bow."""
    sky(S, 'park')
    rk = S['rook']
    bow = sm((k - 0.45) / 0.3) * (1 - sm((k - 0.85) / 0.15))
    stand(rk, at(PARK, -4.0, -2.2, 0), 0.25, P('stand', aR=(0.9, -0.25, 1.9, 0.6), lean=0.35 * bow, head=(0.1 + 0.3 * bow, 0.0)))
    S['hat_off'] = sm(k / 0.3)
    S['hat_to'] = (0.15, -0.55, -1.0)
    S['rface'] = 'soft'
    h = head(rk)
    cam(S, at(PARK, lerp(-1.4, -5.2, k), lerp(-7.4, -7.0, k), lerp(2.2, 2.7, k)), at(PARK, -3.3, -1.6, 2.4), 28)


# ---------------------------------------------------------------- end
def signoff(S, k, t, lt):
    """At the water's edge: Rook picks a pearly shell out of the wet sand, turns it so it glints, pockets it, and tugs
    his brim. The sea behind him."""
    sky(S, 'day')
    surf(S, t)
    rk = S['rook']
    pick = sm(k / 0.3)
    show_ = sm((k - 0.3) / 0.2) * (1 - sm((k - 0.7) / 0.15))
    pose = blend(P('stand', lL=(0.6, 1.1), lR=(0.2, 0.8), lift=-0.4, lean=0.5, aR=(0.9, 0.1, 0.3), head=(0.5, 0.0)),
                 P('stand', aR=(1.9, 0.0, 0.6, 0.4), head=(-0.2, 0.0)), pick)
    if k > 0.72:
        pose = blend(pose, P('hat'), sm((k - 0.72) / 0.2))
    stand(rk, (2.0, 15.0, 0), PI * 0.0 + 0.2, pose)
    S['rface'] = 'low' if k > 0.72 else 'calm'
    S['hat_tip'] = 0.25 + 0.35 * sm((k - 0.8) / 0.15)
    hr = wpos(rk.el[1], (0, -0.08, -0.62))
    S['shell'].location = plus(hr, (0, -0.1, 0.1)) if k < 0.78 else FAR
    S['shell'].rotation_euler = (1.2, 0.3 + t, 0.4)
    S['glint'].location = plus(hr, (0.3, -0.7, 0.4))
    S['glint'].data.energy = 260 * show_
    h = head(rk)
    cam(S, plus(h, (0.6, -4.8, -0.7)), plus(h, (0.0, 0.0, -0.5)), 30)


SHOTS3D = {'blast_close': blast_close, 'column': column_shot, 'chunk_lens': chunk_lens, 'rain_crowd': rain_crowd, 'rook_dune': rook_dune,
           'overhead_chunk': overhead_chunk, 'run_cars': run_cars, 'rook_duck': rook_duck, 'crates': crates, 'rook_count': rook_count,
           'gull': _gull_shot, 'wire': wire, 'expert': expert, 'warn_talk': warn_talk, 'walk_back': walk_back, 'rook_eye': rook_eye,
           'slab_fall': slab_fall, 'car_crush': car_crush, 'owner_face': owner_face, 'rook_roof': rook_roof, 'showroom': showroom,
           'rook_laugh': rook_laugh, 'bulldozer': bulldozer, 'rook_nose': rook_nose, 'engineer_turn': engineer_turn,
           'engineer': engineer, 'rook_stare': rook_stare, 'park_sign': park_sign, 'rook_park': rook_park, 'signoff': signoff}
