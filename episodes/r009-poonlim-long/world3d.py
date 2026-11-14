"""Case 009 in 3D - Poon Lim, SS Benlomond, 23 November 1942 to 5 April 1943. Sets built for this story only:
one open ocean that changes with the weather and the hour (a wartime steamer, a U-boat, the raft and everything
on it, a passing freighter, a patrol plane, a Brazilian fishing boat, a far green coast) and a harbour pier at
dusk where Rook starts and ends the case."""
import math

import bpy
import numpy as np
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(ocean=(0, 0, 0), pier=(600, 0, 0))
FAR = (0, 0, -700)
DECK = 0.47                                   # raft deck height above the raft's origin
HOST = {'rook_raft_cu', 'rook_pier', 'rook_jump', 'rook_deck', 'jump', 'raft_found', 'raft_top', 'tin_empty', 'line_cast',
        'rain_catch', 'bird_grab', 'shark', 'rook_wave', 'plane_over', 'storm_hide', 'rook_stunned', 'poon_safe', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
POON = dict(top='D8D2C0', pants='5A5648', hand='D9A878', boot='D9A878', fore='D9A878')
MEN = [dict(top=c, pants='4A4034', hand='9A623A', boot='9A623A', fore='9A623A') for c in ('C8503A', 'E8E0C8', '3A7A8A')]
SKIN = 'D9A878'


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def at(name, x, y, z):
    o = ORG[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def group(name, fn):
    """Build one set under its own origin and collection, so only one set renders per shot."""
    old = set(bpy.data.objects)
    out = fn(empty(ORG[name]))
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for o in set(bpy.data.objects) - old:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        coll.objects.link(o)
    return coll, out


def own_mat(name, col, rough=0.5, emit=0.0):
    """A material of its own (not shared through the kit's cache) whose colour a shot may change."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Roughness'].default_value = rough
    tint(m, col, emit)
    return m


def tint(m, col, emit=0.0):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)
    b.inputs['Emission Color'].default_value = K.hexc(col)
    b.inputs['Emission Strength'].default_value = emit


def span(o, a, b):
    """Stretch a unit-length rod (along its Z) from a to b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (1, 1, max(0.01, d.length))


# ---------------------------------------------------------------- props
def make_steamer(r, hull='474D56', upper='7A8088', stack='353A42'):
    """A 1920s cargo steamer in wartime grey: no name, no flag, no lights (ships sailed blacked out)."""
    add('cube', hull, (0, 0, 1.2), scale=(50, 8, 5), size=1, parent=r)
    add('cube', hull, (25, 0, 1.2), rot=(0, 0, PI / 4), scale=(5.66, 5.66, 5), size=1, parent=r)
    add('cylinder', hull, (-25, 0, 1.2), radius=4.0, depth=5, vertices=8, parent=r)
    add('cube', '5E1F1A', (0, 0, -1.05), scale=(51, 8.1, 0.6), size=1, parent=r)
    add('cube', '2C3138', (0, 0, 3.72), scale=(56, 7.4, 0.08), size=1, parent=r)
    add('cube', upper, (0, 0, 5.2), scale=(12, 6.4, 3.0), size=1, parent=r)
    add('cube', upper, (2.5, 0, 7.5), scale=(6, 5.2, 1.7), size=1, parent=r)
    add('cube', '1B1F26', (5.55, 0, 7.6), scale=(0.06, 4.6, 0.6), size=1, parent=r)
    add('cube', '2C3138', (2.5, 0, 8.45), scale=(6.6, 5.8, 0.16), size=1, parent=r)
    add('cylinder', stack, (-2.6, 0, 9.4), radius=1.25, depth=5.6, vertices=10, parent=r)
    add('cylinder', '15181D', (-2.6, 0, 12.25), radius=1.3, depth=0.3, vertices=10, parent=r)
    for x in (15.5, -15.5):
        add('cylinder', '2C3138', (x, 0, 9.0), radius=0.22, depth=10.6, vertices=6, parent=r)
        for s in (-1, 1):
            add('cylinder', '2C3138', (x + s * 3.0, 0, 6.6), rot=(0, s * 0.85, 0), radius=0.13, depth=8.2, vertices=5, parent=r)
        add('cube', '5A4A3A', (x + 5.0, 0, 4.1), scale=(5.0, 4.4, 0.7), size=1, parent=r)
        add('cube', '5A4A3A', (x - 5.0, 0, 4.1), scale=(5.0, 4.4, 0.7), size=1, parent=r)
    for s in (-1, 1):
        for i in range(-13, 14):
            add('cube', '2C3138', (i * 2.0, s * 3.8, 4.25), scale=(0.1, 0.1, 1.1), size=1, parent=r)
        add('cube', '2C3138', (0, s * 3.8, 4.8), scale=(54, 0.1, 0.1), size=1, parent=r)
        add('cube', '2C3138', (0, s * 3.8, 4.3), scale=(54, 0.07, 0.07), size=1, parent=r)
        add('cube', 'B8B4A8', (-1.0, s * 3.0, 7.2), scale=(3.4, 1.1, 0.8), size=1, parent=r)
    return r


def make_sub(r):
    """A submarine low in the water: a grey shape, no number, no emblem."""
    add('ico_sphere', '262C33', (0, 0, -0.75), scale=(17, 1.7, 1.5), radius=1.0, subdivisions=2, parent=r)
    add('cube', '2E353D', (0.5, 0, 1.25), scale=(4.0, 1.25, 2.2), size=1, parent=r)
    add('cube', '2E353D', (-1.9, 0, 0.85), scale=(1.6, 1.3, 1.1), size=1, parent=r)
    add('cylinder', '1B2026', (1.2, 0, 3.4), radius=0.08, depth=2.6, vertices=5, parent=r)
    add('cylinder', '1B2026', (0.3, 0, 3.0), radius=0.06, depth=1.6, vertices=5, parent=r)
    add('cylinder', '1B2026', (5.6, 0, 0.75), rot=(0, PI / 2 - 0.2, 0), radius=0.12, depth=2.2, vertices=5, parent=r)
    add('cube', '1B2026', (4.8, 0, 0.45), scale=(0.7, 0.7, 0.6), size=1, parent=r)


def make_raft(r):
    """A square wooden life raft, about eight feet a side. Its details (floats, poles, awning) are a reconstruction."""
    for i in range(9):
        add('cube', ('B08A58', '9C7848', 'A8824F')[i % 3], (0, -1.96 + i * 0.49, 0.42), scale=(4.4, 0.45, 0.1), size=1, parent=r)
    for x in (-1.9, 0, 1.9):
        add('cube', '6E5030', (x, 0, 0.27), scale=(0.24, 4.4, 0.22), size=1, parent=r)
    for y in (-1.55, 1.55):
        add('cylinder', '7A5A36', (0, y, 0.02), rot=(0, PI / 2, 0), radius=0.4, depth=4.5, vertices=8, parent=r)
    for x in (-2.12, 2.12):
        add('cube', '6E5030', (x, 0, 0.5), scale=(0.14, 4.4, 0.2), size=1, parent=r)
    for x in (-2.0, 2.0):
        add('cylinder', '6E5030', (x, 2.0, 1.75), radius=0.07, depth=2.6, vertices=6, parent=r)
        add('cylinder', '6E5030', (x, 0.35, 1.45), radius=0.07, depth=2.0, vertices=6, parent=r)
    add('cube', 'CDB98C', (0, 1.2, 2.72), rot=(0.34, 0, 0), scale=(4.3, 1.85, 0.05), size=1, parent=r)
    add('cube', 'B8A478', (0, 0.33, 2.42), rot=(0.34, 0, 0), scale=(4.34, 0.12, 0.07), size=1, parent=r)
    box = empty((-1.25, 1.45, DECK), r)
    add('cube', '5E7048', (0.55, 0.1, 0.22), scale=(0.9, 0.7, 0.44), size=1, parent=box)
    add('cylinder', 'A8B0B8', (-0.35, 0.0, 0.36), radius=0.32, depth=0.72, vertices=8, parent=box, rough=0.35)
    add('cylinder', '6A7078', (-0.35, 0.0, 0.76), radius=0.1, depth=0.1, vertices=6, parent=box)
    tins = []
    for i, (x, y, z) in enumerate(((0.35, -0.55, 0.14), (0.72, -0.5, 0.14), (0.53, -0.52, 0.42), (-0.05, -0.62, 0.14))):
        tins.append(add('cylinder', ('B8442E', 'D8B048')[i % 2], (x, y, z), radius=0.17, depth=0.28, vertices=8, parent=box, rough=0.4))
    add('torus', 'C8B48A', (2.75, -0.6, 0.06), major_radius=0.36, minor_radius=0.07, major_segments=10, minor_segments=4, parent=box)
    for i in range(3):
        add('cylinder', 'C8452E', (1.2 + i * 0.13, -0.15, 0.06), rot=(PI / 2, 0, 0.3), radius=0.05, depth=0.6, vertices=5, parent=box)
    return dict(tins=tins, box=box)


def make_boat(r):
    """A small Brazilian fishing boat under one sail."""
    add('cube', 'B8542E', (0, 0, 0.35), scale=(6.2, 2.3, 1.1), size=1, parent=r)
    add('cube', 'B8542E', (3.1, 0, 0.35), rot=(0, 0, PI / 4), scale=(1.63, 1.63, 1.1), size=1, parent=r)
    add('cube', 'F0E8D0', (0, 0, 0.93), scale=(6.3, 2.4, 0.12), size=1, parent=r)
    add('cube', 'F0E8D0', (3.1, 0, 0.93), rot=(0, 0, PI / 4), scale=(1.72, 1.72, 0.12), size=1, parent=r)
    add('cube', '6E4426', (0, 0, 0.62), scale=(5.8, 1.9, 0.5), size=1, parent=r)
    add('cube', '2E7A8A', (0, 0, 0.0), scale=(6.25, 2.34, 0.2), size=1, parent=r)
    for x in (-1.6, 0.9):
        add('cube', '8A5A34', (x, 0, 0.95), scale=(0.4, 2.0, 0.1), size=1, parent=r)
    add('cylinder', '6E4426', (1.4, 0, 4.3), radius=0.09, depth=7.0, vertices=6, parent=r)
    add('cone', 'F4ECD8', (-0.55, 0, 4.4), scale=(1, 0.02, 1), radius1=3.4, radius2=0.0, depth=6.0, vertices=4, parent=r)
    add('cylinder', '6E4426', (-0.5, 0, 1.5), rot=(0, PI / 2, 0), radius=0.06, depth=4.4, vertices=5, parent=r)
    add('cube', '6E4426', (-3.2, 0, 0.5), scale=(0.12, 0.3, 1.5), size=1, parent=r)


def make_plane(r):
    """A twin-engined patrol flying boat seen from below: plain blue-grey, no markings."""
    add('cylinder', '5C6E80', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.85, depth=9.5, vertices=8, parent=r)
    add('cone', '5C6E80', (5.6, 0, 0), rot=(0, PI / 2, 0), radius1=0.85, radius2=0.25, depth=1.8, vertices=8, parent=r)
    add('cone', '5C6E80', (-6.6, 0, 0.25), rot=(0, -PI / 2, 0), radius1=0.8, radius2=0.2, depth=4.0, vertices=8, parent=r)
    add('cube', '5C6E80', (1.0, 0, 1.3), scale=(1.3, 0.5, 1.2), size=1, parent=r)
    add('cube', '6E8094', (1.0, 0, 1.95), scale=(3.0, 19, 0.28), size=1, parent=r)
    props = []
    for s in (-1, 1):
        add('cylinder', '3E4A58', (2.2, s * 3.0, 1.95), rot=(0, PI / 2, 0), radius=0.55, depth=1.8, vertices=8, parent=r)
        props.append(add('cube', 'D8E0E8', (3.2, s * 3.0, 1.95), scale=(0.05, 2.6, 0.22), size=1, parent=r))
        add('cube', '6E8094', (0.6, s * 8.6, 1.2), scale=(0.9, 0.3, 1.2), size=1, parent=r)
    add('cube', '6E8094', (-8.0, 0, 1.4), scale=(1.5, 0.16, 2.2), size=1, parent=r)
    add('cube', '6E8094', (-8.0, 0, 1.3), scale=(1.3, 5.2, 0.14), size=1, parent=r)
    return props


def make_gull(col='F4F4F0'):
    g = empty(FAR)
    add('ico_sphere', col, (0, 0, 0), scale=(0.34, 0.16, 0.16), radius=1.0, subdivisions=1, parent=g)
    add('ico_sphere', col, (0.3, 0, 0.12), radius=0.11, subdivisions=1, parent=g)
    add('cone', 'F2A030', (0.46, 0, 0.11), rot=(0, PI / 2, 0), radius1=0.04, radius2=0.0, depth=0.16, vertices=4, parent=g)
    wings = []
    for s in (-1, 1):
        w = empty((0, s * 0.1, 0.08), g)
        add('cube', 'D8DCE0', (0, s * 0.36, 0), scale=(0.3, 0.72, 0.03), size=1, parent=w)
        add('cube', '3A4048', (0, s * 0.78, 0), scale=(0.22, 0.16, 0.03), size=1, parent=w)
        wings.append(w)
    return dict(root=g, wings=wings)


def flap(g, t, speed=9.0, amp=0.7, fold=False):
    for s, w in zip((-1, 1), g['wings']):
        w.rotation_euler = (s * (-1.35 if fold else amp * math.sin(t * speed)), 0, 0)


def make_fish():
    f = empty(FAR)
    add('ico_sphere', 'A8C0D0', (0, 0, 0), scale=(0.42, 0.1, 0.18), radius=1.0, subdivisions=1, parent=f, rough=0.25)
    add('cone', '7E98AC', (-0.5, 0, 0), rot=(0, PI / 2, 0), scale=(1, 0.25, 1), radius1=0.2, radius2=0.0, depth=0.26, vertices=4, parent=f, rough=0.3)
    add('ico_sphere', '10141A', (0.27, -0.085, 0.04), radius=0.03, subdivisions=1, parent=f)
    return f


def make_shark():
    s = empty(FAR)
    add('ico_sphere', '6E7C8A', (0, 0, 0), scale=(2.4, 0.5, 0.56), radius=1.0, subdivisions=2, parent=s, rough=0.4)
    add('cone', '36424E', (-0.1, 0, 0.78), rot=(0, -0.45, 0), scale=(1, 0.14, 1), radius1=0.5, radius2=0.0, depth=1.05, vertices=4, parent=s)
    add('cone', '5E6C7A', (-2.5, 0, 0.3), rot=(0, -0.9, 0), scale=(1, 0.14, 1), radius1=0.42, radius2=0.0, depth=1.2, vertices=4, parent=s)
    for d in (-1, 1):
        add('cone', '5E6C7A', (0.6, d * 0.6, -0.2), rot=(d * 1.3, 0, 0), scale=(1, 0.2, 1), radius1=0.3, radius2=0.0, depth=0.9, vertices=4, parent=s)
    return s


def make_hook():
    """The fish hook he bent out of the flashlight's spring. Rook keeps it."""
    h = empty(FAR)
    kw = dict(parent=h, rough=0.2, emit=1.2)
    add('cylinder', 'E8EEF4', (0, 0, 0.17), radius=0.022, depth=0.38, vertices=5, **kw)
    add('cylinder', 'E8EEF4', (0.085, 0, -0.02), rot=(0, PI / 2, 0), radius=0.022, depth=0.2, vertices=5, **kw)
    add('cylinder', 'E8EEF4', (0.17, 0, 0.05), radius=0.022, depth=0.16, vertices=5, **kw)
    add('cone', 'E8EEF4', (0.17, 0, 0.17), radius1=0.04, radius2=0.0, depth=0.1, vertices=4, **kw)
    add('torus', 'E8EEF4', (0, 0, 0.39), rot=(PI / 2, 0, 0), major_radius=0.04, minor_radius=0.015, major_segments=8, minor_segments=4, **kw)
    return h


def make_torch():
    tr = empty(FAR)
    add('cylinder', '39404A', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.13, depth=0.8, vertices=8, parent=tr, rough=0.4)
    add('cone', '4A525E', (-0.52, 0, 0), rot=(0, -PI / 2, 0), radius1=0.2, radius2=0.13, depth=0.26, vertices=8, parent=tr, rough=0.4)
    add('cylinder', 'FFF2C0', (-0.66, 0, 0), rot=(0, PI / 2, 0), radius=0.17, depth=0.03, vertices=8, parent=tr, emit=1.5)
    spring = empty((0.42, 0, 0), tr)
    for i in range(6):
        add('torus', 'E8EEF4', (i * 0.07, 0, 0), rot=(0, PI / 2, 0), major_radius=0.085, minor_radius=0.018, major_segments=8, minor_segments=4,
            parent=spring, rough=0.2, emit=0.9)
    return dict(root=tr, spring=spring)


def straw_head(skin, hair='1A1410'):
    base = K.human_head(skin, hair)

    def fn(head):
        out = base(head)
        add('cone', 'D9C27A', (0, 0, 0.36), radius1=0.62, radius2=0.12, depth=0.3, vertices=10, parent=head)
        return out
    return fn


# ---------------------------------------------------------------- sets
def set_ocean(r):
    seamat = own_mat('sea', '0F6E8E', 0.32)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=96, y_subdivisions=96, size=160, location=ORG['ocean'])
    sea = bpy.context.object
    sea.data.materials.append(seamat)
    co = np.zeros(len(sea.data.vertices) * 3)
    sea.data.vertices.foreach_get('co', co)
    xy = co.reshape(-1, 3)[:, :2].copy()
    fade = np.clip((80 - np.maximum(np.abs(xy[:, 0]), np.abs(xy[:, 1]))) / 22, 0, 1)
    farsea = add('plane', '000000', (0, 0, -0.35), size=5000, parent=r)
    farsea.data.materials[0] = seamat
    cloudmat = own_mat('cloud', 'FFFFFF', 0.9, 0.8)
    for i in range(13):
        a = i * 0.77 + 0.3
        d = 300 + (i * 53) % 150
        c = empty((math.sin(a) * d, math.cos(a) * d, 46 + (i * 29) % 70), r)
        for j in range(3):
            o = add('ico_sphere', '000000', ((j - 1) * 26, (j % 2) * 8, (j % 2) * 7), scale=(1.5, 1, 0.42), radius=20 + (i + j) % 3 * 7, subdivisions=1, parent=c)
            o.data.materials[0] = cloudmat
    target = empty((0, 0, 0), r)
    sun = light((40, -60, 120), 3.0, 'FFF4DC', kind='SUN', target=target, parent=r)
    sundisc = add('circle', 'FFF0C0', FAR, rot=(PI / 2, 0, 0), radius=20, vertices=20, fill_type='NGON', parent=r, emit=9)
    moon = add('circle', 'E6EEFF', FAR, rot=(PI / 2, 0, 0), radius=13, vertices=20, fill_type='NGON', parent=r, emit=5)
    stars = empty(FAR, r)
    for i in range(46):
        a, e = i * 2.4, 0.12 + ((i * 0.618) % 1) * 1.0
        add('ico_sphere', 'DCE6FF', (math.sin(a) * math.cos(e) * 620, math.cos(a) * math.cos(e) * 620, math.sin(e) * 620), radius=1.5 + i % 3,
            subdivisions=1, parent=stars, emit=6)
    ship = make_steamer(empty(FAR, r))
    frt = make_steamer(empty(FAR, r), hull='2E3238', upper='8A8478', stack='4A3A30')
    sub = empty(FAR, r)
    make_sub(sub)
    wake = add('cube', 'DFF4FF', FAR, scale=(1, 0.5, 0.05), size=1, parent=r, emit=1.4)
    raft = empty(FAR, r)
    out = make_raft(raft)
    boat = empty(FAR, r)
    make_boat(boat)
    plane = empty(FAR, r)
    props = make_plane(plane)
    coast = empty(FAR, r)
    add('cube', '2C6A3C', (0, 12, 3.0), scale=(900, 40, 7), size=1, parent=coast)
    add('cube', 'EAD9A4', (0, -9, 0.4), scale=(900, 6, 1.4), size=1, parent=coast)
    for i in range(22):
        add('cone', ('2C6A3C', '347A44', '25593A')[i % 3], (-420 + i * 41 + (i * 17) % 13, 22 + (i % 4) * 9, 11 + (i % 3) * 5),
            radius1=30 + (i % 5) * 7, radius2=3, depth=22 + (i % 3) * 10, vertices=7, parent=coast)
    return dict(sea=sea, xy=xy, fade=fade, seamat=seamat, cloudmat=cloudmat, sun=sun, sundisc=sundisc, moon=moon, stars=stars, ship=ship,
                frt=frt, sub=sub, wake=wake, raft=raft, boat=boat, plane=plane, props=props, coast=coast, **out)


def set_pier(r):
    """A harbour pier at dusk: Rook's start and finish."""
    add('plane', '2A3E58', (0, 0, 0), size=900, parent=r, rough=0.25)
    add('cube', '8A6A48', (0, 6, 1.25), scale=(6.4, 40, 0.3), size=1, parent=r)
    for i in range(-16, 31):
        add('cube', '5E4630', (0, i * 0.85, 1.41), scale=(6.4, 0.06, 0.02), size=1, parent=r)
    for y in range(-12, 27, 6):
        for sx in (-1, 1):
            add('cylinder', '4A3828', (sx * 2.9, y, 0.5), radius=0.26, depth=2.6, vertices=7, parent=r)
    for y in (-3.0, 5.0):
        add('cylinder', '2A2E36', (-2.6, y, 1.72), radius=0.24, depth=0.62, vertices=8, parent=r)
        add('cylinder', '2A2E36', (-2.6, y, 2.05), radius=0.32, depth=0.12, vertices=8, parent=r)
    add('cylinder', '2A2E36', (2.5, 2.4, 3.7), radius=0.09, depth=4.6, vertices=6, parent=r)
    add('cube', '2A2E36', (2.1, 2.4, 5.95), scale=(1.0, 0.1, 0.1), size=1, parent=r)
    add('cone', 'FFB45A', (1.65, 2.4, 5.65), radius1=0.32, radius2=0.14, depth=0.4, vertices=8, parent=r, emit=9)
    light((1.65, 2.2, 5.2), 900, 'FFB060', kind='POINT', parent=r)
    for x, y, z, s, c in ((-1.9, 3.6, 1.9, 1.0, '7A5A3A'), (-1.0, 4.1, 1.75, 0.7, '6A4E32'), (-1.8, 3.7, 2.75, 0.7, '8A6844'), (1.9, 6.2, 1.8, 0.8, '7A5A3A')):
        add('cube', c, (x, y, z), rot=(0, 0, x * 0.3), scale=(s, s, s), size=1, parent=r)
        add('cube', '4A3828', (x, y, z), rot=(0, 0, x * 0.3), scale=(s * 1.04, s * 0.16, s * 1.04), size=1, parent=r)
    add('torus', 'C8B48A', (1.3, -1.4, 1.5), major_radius=0.42, minor_radius=0.09, major_segments=10, minor_segments=4, parent=r)
    row = empty((4.6, 3.0, 0.1), r, (0, 0, 0.12))
    add('cube', '3A6A7A', (0, 0, 0.2), scale=(1.5, 3.6, 0.7), size=1, parent=row)
    add('cube', '3A6A7A', (0, 1.8, 0.2), rot=(0, 0, PI / 4), scale=(1.06, 1.06, 0.7), size=1, parent=row)
    add('cube', '274852', (0, 0, 0.38), scale=(1.2, 3.2, 0.4), size=1, parent=row)
    add('cube', 'B08A58', (0, -0.4, 0.5), scale=(1.4, 0.3, 0.07), size=1, parent=row)
    for i in range(9):
        x = -130 + i * 31 + (i * 13) % 9
        hgt = 9 + (i * 7) % 12
        add('cube', ('1E2238', '252A44', '1A1E30')[i % 3], (x, 120 + (i % 3) * 14, hgt / 2), scale=(24, 14, hgt), size=1, parent=r)
        for j in range(4):
            if (i + j) % 3:
                add('cube', 'FFC870', (x - 8 + j * 5, 112.8 + (i % 3) * 14, 2.5 + (j % 2) * 3), scale=(1.6, 0.2, 1.6), size=1, parent=r, emit=5)
    for x in (-60, 45):
        add('cube', '14172A', (x, 105, 16), scale=(1.4, 1.4, 32), size=1, parent=r)
        add('cube', '14172A', (x + 9, 105, 31), rot=(0, -0.25, 0), scale=(26, 1.2, 1.2), size=1, parent=r)
    add('circle', 'FFC070', (-24, 520, 26), rot=(PI / 2, 0, 0), radius=44, vertices=20, fill_type='NGON', parent=r, emit=7)
    aim = empty((0, 0, 3.2), r)
    light((-5, -7, 6.5), 1700, 'FFD8B0', 3.0, aim, parent=r)
    light((-6, 9, 5), 2600, 'FF7A1A', 2.0, aim, parent=r)
    light((6, -5, 2.5), 320, '6E8FD8', 4.0, aim, parent=r)
    return {}


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('ocean', set_ocean), ('pier', set_pier)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['poon'] = K.Rig(POON, K.human_head(SKIN, '14110F'))
    S['vest'] = [add('cube', 'D8C48C', (0, s * 0.3, 0.62), scale=(0.6, 0.2, 0.74), size=1, parent=S['poon'].body) for s in (-1, 1)]
    S['vest'].append(add('cube', 'B8A470', (0, 0, 0.62), scale=(0.78, 0.5, 0.1), size=1, parent=S['poon'].body))
    S['men'] = [K.Rig(c, straw_head('9A623A')) for c in MEN]
    S['hand_p'] = K.Hand(SKIN, SKIN, 1.0)
    S['hand_q'] = K.Hand(SKIN, SKIN, 1.0)
    S['hand_f'] = K.Hand('9A623A', 'C8503A', 1.0)
    S['gulls'] = [make_gull() for _ in range(4)]
    S['fish'] = [make_fish() for _ in range(5)]
    S['shark'] = make_shark()
    S['hook'] = make_hook()
    S['torch'] = make_torch()
    S['tin'] = add('cylinder', 'B8442E', FAR, radius=0.17, depth=0.28, vertices=8, rough=0.4)
    add('cylinder', '2A1410', (0, 0, 0.135), radius=0.15, depth=0.02, vertices=8, parent=S['tin'])
    S['blade'] = add('cube', 'D8E0E8', FAR, scale=(0.5, 0.16, 0.012), size=1, rough=0.15, emit=0.5)
    S['cloth'] = add('cone', 'CDB98C', FAR, rot=(PI, 0, 0), radius1=1.25, radius2=0.1, depth=0.55, vertices=6, emit=0.35)
    S['line'] = add('cylinder', 'E8E0C8', FAR, radius=0.022, depth=1.0, vertices=4, emit=0.5)
    S['strips'] = [add('cube', ('D88A78', 'C87868')[i % 2], FAR, scale=(0.12, 0.03, 0.42), size=1) for i in range(6)]
    S['fire'] = [add('ico_sphere', ('FF9A30', 'FFD060', 'FF6A20')[i % 3], FAR, radius=1.0, subdivisions=1, emit=14) for i in range(8)]
    S['plume'] = [add('cone', 'E4F0FF', FAR, radius1=1.0, radius2=0.3, depth=1.0, vertices=7, emit=0.4) for _ in range(3)]
    S['smoke'] = [add('ico_sphere', '30343C', FAR, radius=1.0, subdivisions=1) for _ in range(9)]
    S['drops'] = [add('ico_sphere', 'E4F4FF', FAR, radius=0.09, subdivisions=1, emit=0.9) for _ in range(18)]
    S['fea'] = [add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4) for _ in range(6)]
    S['planks'] = [add('cube', ('8A6A48', '6E5030')[i % 2], FAR, scale=(1.6 + i % 3 * 0.5, 0.4, 0.12), size=1) for i in range(6)]
    S['glow'] = light(FAR, 0, 'FF9A40', kind='POINT')
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 4000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    S['fill'] = light((0, 0, 0), 0, 'FFFFFF', 3.0, tgt)
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    sc.world = w
    S['bg'] = w.node_tree.nodes['Background']
    S['fillk'] = 0.0
    return S


def sky(S, col, strength=1.0):
    S['bg'].inputs[0].default_value = K.hexc(col)
    S['bg'].inputs[1].default_value = strength


def show(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: at(name, x, y, z)


#          sky       str  sea       sun  sun colour  sun position      cloud     emit  fill  fill colour
MOODS = dict(
    night=('0C1632', 1.0, '0E3656', 2.6, 'A8C0F0', (-70, 60, 90), '22304E', 0.3, 13.0, 'B8CCF8'),
    day=('7EC0EE', 0.9, '0F6E8E', 3.4, 'FFF4DC', (50, -70, 120), 'FFFFFF', 0.85, 9.0, 'FFF0DC'),
    noon=('A6D6F2', 1.0, '1284A4', 4.0, 'FFFBEF', (110, -70, 80), 'FFFFFF', 0.9, 8.0, 'FFFFFF'),
    dusk=('E88E52', 0.9, '6A4048', 2.6, 'FF9A50', (-60, 260, 40), 'FFB888', 0.7, 12.0, 'FFD0A8'),
    storm=('4A5662', 0.9, '24404E', 1.3, 'B8C8D8', (30, -40, 120), '2C343E', 0.2, 13.0, 'D0DCE8'),
    dawn=('F6BCA2', 1.0, '3C8494', 2.8, 'FFD2A4', (150, 330, 60), 'FFE4D4', 0.8, 12.0, 'FFE0C8'),
)


def mood(S, name, flash=0.0):
    sk, st, sea, se, sc_, sp, cc, ce, fk, fc = MOODS[name]
    sky(S, lerp_col(sk, 'C8D4F0', flash), st + 4 * flash)
    tint(S['seamat'], sea)
    tint(S['cloudmat'], cc, ce)
    S['sun'].data.energy = se + 6 * flash
    S['sun'].data.color = K.hexc(sc_)[:3]
    S['sun'].location = sp
    S['fillk'] = fk
    S['fill'].data.color = K.hexc(fc)[:3]
    if name == 'night':
        S['moon'].location = (-150, 560, 190)
        S['stars'].location = (0, 0, 0)
    if name == 'dusk':
        S['sundisc'].location = (-90, 640, 34)
    if name == 'dawn':
        S['sundisc'].location = (190, 620, 40)


def lerp_col(a, b, k):
    k = max(0.0, min(1.0, k))
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


def cam(S, pos, look, lens=50, roll=0.0, fill=1.0):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    dx, dy, dz = look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    h = math.hypot(dx, dy) + 1e-6
    S['fill'].location = (pos[0] - dy / h * 0.35 * d, pos[1] + dx / h * 0.35 * d, pos[2] + 0.35 * d)
    S['fill'].data.energy = S['fillk'] * fill * min(d, 16) ** 2
    S['fill'].data.size = max(2.0, 0.35 * d)


def wave_h(x, y, t, rough=1.0):
    f = max(0.0, min(1.0, (80 - max(abs(x), abs(y))) / 22))
    return f * rough * (0.5 * math.sin(x * 0.21 + t * 1.3) + 0.34 * math.sin(y * 0.17 - t * 1.7 + x * 0.09) + 0.16 * math.sin((x - y) * 0.5 + t * 2.6))


def seas(S, t, rough=1.0):
    x, y = S['xy'][:, 0], S['xy'][:, 1]
    z = S['fade'] * rough * (0.5 * np.sin(x * 0.21 + t * 1.3) + 0.34 * np.sin(y * 0.17 - t * 1.7 + x * 0.09) + 0.16 * np.sin((x - y) * 0.5 + t * 2.6))
    S['sea'].data.vertices.foreach_set('co', np.column_stack([S['xy'], z]).ravel())
    S['sea'].data.update()


def ocean(S, name, t, rough=0.6, flash=0.0):
    A = show(S, 'ocean')
    mood(S, name, flash)
    seas(S, t, rough)
    S['rough'] = rough
    return A


def ride(S, t, x=0.0, y=0.0, yaw=0.0, lift=0.12, tilt=1.0):
    """Float the raft on the swell at (x, y)."""
    r = S['rough']
    h = wave_h(x, y, t, r)
    px = (wave_h(x, y + 1.5, t, r) - wave_h(x, y - 1.5, t, r)) / 3.0
    py = (wave_h(x + 1.5, y, t, r) - wave_h(x - 1.5, y, t, r)) / 3.0
    S['raft'].location = (x, y, h + lift)
    S['raft'].rotation_euler = (px * 0.8 * tilt, -py * 0.8 * tilt, yaw)


def aboard(S, rig, x, y, yaw=0.0, pose=None, z=DECK, pitch=0.0, roll=0.0, on='raft'):
    """Stand a character on the raft (or boat): coordinates are the raft's own."""
    rig.root.parent = S[on]
    rig.place((x, y, z), yaw, pitch, roll)
    if pose:
        rig.apply(pose)


def on(S, o, where, loc, rot=(0, 0, 0)):
    """Put a prop on the raft/boat/a hand in that object's own coordinates."""
    o.parent = where
    o.location, o.rotation_euler = loc, rot


def edge_sit(**over):
    """Sitting on the raft's edge, shins hanging over the side."""
    d = dict(lL=(1.5, 1.45), lR=(1.5, 1.45), lift=-0.88, lean=0.12, aL=(0.6, 0.05, 1.0, 0.6), aR=(0.6, 0.05, 1.0, 0.6))
    d.update(over)
    return P('stand', **d)


def splash(S, org, k, n=10, r=1.6, seed=0, start=0, size=1.0):
    for i in range(n):
        b = S['drops'][start + i]
        a, e = i * 2.4 + seed, 0.5 + ((i * 0.61) % 1) * 0.9
        d = r * (0.4 + 0.6 * ((i * 0.37) % 1)) * k
        b.location = (org[0] + math.cos(a) * math.cos(e) * d, org[1] + math.sin(a) * math.cos(e) * d, org[2] + math.sin(e) * d * 1.7 - 2.6 * k * k)
        s = size * (0.7 + ((i * 0.73) % 1)) * (1.2 - 0.7 * k)
        b.scale = (s, s, s)


def smoke(S, org, t, n=6, rise=9.0, drift=(-1.0, 0.0), size=1.6, start=0):
    for i in range(n):
        o = S['smoke'][start + i]
        u = (t * 0.22 + i / n) % 1
        o.location = (org[0] + drift[0] * u * rise + 0.5 * math.sin(i * 2.1), org[1] + drift[1] * u * rise, org[2] + u * rise)
        s = size * (0.5 + 1.4 * u)
        o.scale = (s, s, s * 0.8)


def reset(S):
    for rig in [S['rook'], S['poon']] + S['men']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
    for hnd in ('hand_p', 'hand_q', 'hand_f'):
        S[hnd].root.parent = None
        S[hnd].root.scale = (1, 1, 1)
        S[hnd].place(FAR)
        S[hnd].grip(0.2)
    for g in S['gulls']:
        g['root'].parent = None
        g['root'].location, g['root'].rotation_euler, g['root'].scale = FAR, (0, 0, 0), (1, 1, 1)
        flap(g, 0.0)
    loose = S['fish'] + [S['shark'], S['hook'], S['torch']['root'], S['tin'], S['blade'], S['cloth'], S['line']] + S['strips'] + S['fire'] \
        + S['plume'] + S['smoke'] + S['drops'] + S['fea'] + S['planks']
    for o in loose:
        o.parent = None
        o.location, o.scale = FAR, (1, 1, 1)
    for o in S['fish'] + [S['shark'], S['hook'], S['torch']['root'], S['tin']] + S['strips'] + S['planks'] + S['fea']:
        o.rotation_euler = (0, 0, 0)
    S['blade'].scale = (0.5, 0.16, 0.012)
    S['cloth'].rotation_euler = (PI, 0, 0)
    for i, o in enumerate(S['strips']):
        o.scale = (0.12, 0.03, 0.42)
    for i, o in enumerate(S['planks']):
        o.scale = (1.6 + i % 3 * 0.5, 0.4, 0.12)
    S['torch']['spring'].location = (0.42, 0, 0)
    S['torch']['spring'].hide_render = False
    for o in S['torch']['spring'].children:
        o.hide_render = False
    for k in ('ship', 'frt', 'sub', 'raft', 'boat', 'plane', 'coast', 'wake', 'sundisc', 'moon', 'stars'):
        S[k].location = FAR
        if k not in ('sundisc', 'moon'):
            S[k].rotation_euler = (0, 0, 0)
    S['ship'].scale = S['frt'].scale = S['boat'].scale = S['plane'].scale = (1, 1, 1)
    S['wake'].scale = (1, 0.5, 0.05)
    for o in S['vest']:
        o.hide_render = True
    for o in S['tins']:
        o.hide_render = False
    S['glow'].location = FAR
    S['glow'].data.energy = 0
    S['glow'].data.color = K.hexc('FF9A40')[:3]
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['rough'] = 0.6
    S['face'] = dict(rook='calm', poon='calm', men='calm')
    S['hat_tip'] = 0.0
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.43) % 1 < 0.035
    ez = dict(calm=0.07, smirk=0.045, deadpan=0.05, shocked=0.13, laugh=0.03, sad=0.06, warm=0.06).get(e, 0.07)
    tilt = dict(smirk=-0.5, deadpan=-0.05, shocked=0.35, laugh=0.3, sad=0.4, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + (s * tilt if e != 'smirk' or s > 0 else 0.1), s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip = S['hat_tip']
    r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.12).get(e, 0.0) + tip * 0.35, 0.07, 0)
    r['hat'].location.z = 0.27 + (0.13 if e == 'shocked' else 0.0) + tip * 0.1
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e in ('shocked', 'laugh') else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0) - (0.25 if e == 'laugh' else 0), hd[1],
                                     hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for who, rigs in (('poon', [S['poon']]), ('men', S['men'])):
        k = dict(scared=1.3, shock=1.8, calm=1.0, tired=0.5, happy=0.85, closed=0.12).get(S['face'][who], 1.0)
        for rig in rigs:
            for ey in rig.extra['eyes']:
                ey.scale = (ey.scale[0], ey.scale[1], 0.075 * k)


def feathers(S, org, k, n=5):
    for i in range(n):
        f = S['fea'][i]
        a = i * 1.9
        f.location = (org[0] + math.cos(a) * (0.3 + 0.9 * k), org[1] + math.sin(a) * 0.4 * k - 0.2, org[2] + 0.5 * math.sin(k * PI) - 1.1 * k * k + i * 0.08)
        f.rotation_euler = (k * 5 + i, k * 3, i * 1.3)


def vest(S, shown=True):
    for o in S['vest']:
        o.hide_render = not shown


# ---------------------------------------------------------------- shots: the sinking
def torpedo_hit(S, k, t, lt):
    fl = max(0.0, 1 - lt / 0.35)
    A = ocean(S, 'night', t, 0.8, flash=fl * 0.7)
    S['ship'].location = A(0, 42, 0.2)
    S['ship'].rotation_euler = (-0.05 * ease(k * 2), 0, 0.12)
    b = ease(lt / 0.5)
    for i, o in enumerate(S['fire']):
        a = i * 0.8
        o.location = A(6 + math.cos(a) * 4.5 * b, 37.0 - 1.5 * b, 2.5 + (1.5 + i % 3 * 2.2) * b + math.sin(a) * 2.0 * b)
        s = (0.8 + (i % 3) * 0.9) * (0.4 + 2.2 * b) * (1 - 0.35 * k)
        o.scale = (s, s, s)
    for i, o in enumerate(S['plume']):
        hgt = (9 + i * 6) * ease(lt / (0.35 + i * 0.12))
        o.location = A(4 + i * 2.2, 36.6, hgt / 2)
        o.scale = (1.6 + i * 0.5, 1.6 + i * 0.5, max(0.1, hgt))
    S['glow'].location = A(6, 33, 5)
    S['glow'].data.energy = 400000 * (0.35 + 0.65 * fl)
    smoke(S, A(6, 38, 6), t + 2, 5, 14, (-0.3, 0), 2.6)
    cam(S, A(lerp(-16, -13, k), lerp(-4, 1, k), 1.3), A(5, 42, lerp(6.5, 8, k)), 26, 0.05, fill=0)


def ship_down(S, k, t, lt):
    A = ocean(S, 'night', t, 0.9)
    S['ship'].location = A(lerp(0, -3, k), 46, lerp(-2, -13, k))
    S['ship'].rotation_euler = (0.1, lerp(0.42, 0.95, k), 0.5)
    for i, o in enumerate(S['fire'][:4]):
        o.location = A(-6 + i * 2.2, 38 + i, 3.5 + 2 * math.sin(t * 9 + i) - 6 * k)
        s = 1.5 + 0.6 * math.sin(t * 13 + i * 2)
        o.scale = (s, s, s * 1.4)
    S['glow'].location = A(-4, 34, 5)
    S['glow'].data.energy = 160000 * (1 - 0.7 * k)
    smoke(S, A(-6, 42, 6), t, 9, 26, (-0.25, 0.1), 3.4)
    for i, o in enumerate(S['planks']):
        x, y = -14 + i * 5.5, 20 + (i % 3) * 5
        o.location = A(x, y, wave_h(x, y, t, 0.9) + 0.05)
        o.rotation_euler = (0, 0, i * 1.1)
    splash(S, A(8, 40, 0.5), (lt * 0.8) % 1, 12, 7, size=5)
    cam(S, A(lerp(-20, -24, k), lerp(-6, -10, k), lerp(2.5, 7, k)), A(-2, 46, lerp(11, 8, k)), 30, -0.04, fill=0)


def ship_wide(S, k, t, lt):
    A = ocean(S, 'night', t, 0.7)
    x = lerp(-12, 2, k)
    S['ship'].location = A(x, 34, 0.15 * math.sin(t * 1.1))
    S['ship'].rotation_euler = (0.02 * math.sin(t * 0.9), 0.015 * math.sin(t * 1.3), 0)
    smoke(S, A(x - 2.6, 34, 12.5), t, 9, 20, (-1.3, 0.1), 1.6)
    for i in range(8):
        d = S['drops'][i]
        u = (t * 1.6 + i * 0.37) % 1
        d.location = A(x + 28 - u * 5, 34 + (-1) ** i * (1 + u * 4), 0.4 + 1.6 * math.sin(u * PI))
        d.scale = (5, 5, 5)
    S['glow'].location = A(x + 26, 4, 44)
    S['glow'].data.energy = 420000
    S['glow'].data.color = K.hexc('A8C0F0')[:3]
    cam(S, A(lerp(48, 40, k), lerp(-16, -10, k), lerp(11, 6, k)), A(x + 4, 34, 6), 32, fill=0)


def sub_wake(S, k, t, lt):
    A = ocean(S, 'night', t, 0.55)
    S['sub'].location = A(-10.5, 4, 0.25 + 0.1 * math.sin(t * 1.4))
    S['sub'].rotation_euler = (0, 0, 1.2)
    S['ship'].location = A(22, 110, 0)
    S['ship'].rotation_euler = (0, 0, -0.2)
    S['ship'].scale = (1.5, 1.5, 1.5)
    n = ease(lt / 1.1)
    p0, p1 = Vector(A(-6.0, 15, 0.5)), Vector(A(14, 86, 0.5))
    p = p0 + (p1 - p0) * n
    span(S['wake'], p0, p)
    S['wake'].scale = (0.9, 0.06, max(0.1, (p - p0).length))
    for i in range(6):
        d = S['drops'][i]
        d.location = (p.x + math.sin(t * 20 + i) * 0.6, p.y + math.cos(t * 17 + i) * 0.6, 0.6 + 0.5 * abs(math.sin(t * 12 + i)))
        d.scale = (4, 4, 4)
    S['glow'].location = A(-17, -5, 12)
    S['glow'].data.energy = 30000
    S['glow'].data.color = K.hexc('A8C0F0')[:3]
    cam(S, A(lerp(-19, -17, k), lerp(-13, -10, k), lerp(7.5, 6.2, k)), A(0, 40, 2.0), 34, 0.03, fill=0)


def rook_deck(S, k, t, lt):
    A = ocean(S, 'night', t, 0.6)
    S['ship'].location = A(0, 0, 0.1 * math.sin(t * 1.2))
    S['ship'].rotation_euler = (0.015 * math.sin(t), 0, 0)
    j = ease((lt - 0.25) / 0.2)
    S['rook'].place(A(10.5, -3.25, 3.78 + 0.25 * math.sin(PI * j)), 0.25)
    S['rook'].apply(blend(P('hips', head=(0.1, -0.5)), P('point', aR=(1.2, 0.25, 0.05), aL=(0.4, 0.9, 1.2), head=(0.15, -0.35), lean=-0.1), j))
    S['face']['rook'] = 'shocked' if j > 0.3 else 'deadpan'
    if j > 0.3:
        feathers(S, A(10.5, -3.6, 6.3), min(1, (lt - 0.35) / 0.8), 3)
    p0 = Vector(A(40, -60, 0.45))
    p1 = p0 + (Vector(A(16, -8, 0.45)) - p0) * (0.3 + 0.7 * k)
    span(S['wake'], p0, p1)
    S['wake'].scale = (1.2, 0.06, (p1 - p0).length)
    cam(S, A(lerp(13.5, 12.6, k), lerp(-11.5, -9.8, k), lerp(6.6, 6.2, k)), A(10.4, -3.2, 6.1), 40, 0.03)


def jump(S, k, t, lt):
    A = ocean(S, 'night', t, 0.9)
    S['ship'].location = A(0, 2, -1.2 - 1.5 * k)
    S['ship'].rotation_euler = (lerp(0.2, 0.34, k), 0.06, 0)
    for i, o in enumerate(S['fire'][:5]):
        o.location = A(-14 + i * 2.5, 0.5, 6 + 1.6 * math.sin(t * 9 + i * 2))
        s = 1.6 + 0.6 * math.sin(t * 12 + i)
        o.scale = (s, s, s * 1.5)
    S['glow'].location = A(-10, -6, 7)
    S['glow'].data.energy = 90000
    smoke(S, A(-12, 1, 8), t, 6, 16, (-0.4, 0.2), 2.6)
    u = ease(k * 1.15)
    S['poon'].place(A(6.5, lerp(-3.4, -9.5, u), lerp(3.2, 0.4, u * u) + 3.2 * math.sin(PI * min(1, u))), -0.3, lerp(0.1, 0.5, u))
    S['poon'].apply(P('up', aL=(2.4, 0.9, 0.3), aR=(2.6, 0.8, 0.2), lL=(0.9, 1.3), lR=(-0.3, 0.8), head=(-0.2, 0)))
    S['face']['poon'] = 'scared'
    vest(S)
    v = ease((k - 0.25) * 1.5)
    S['rook'].place(A(9.6, lerp(-3.3, -8.0, v), lerp(3.0, 1.4, v * v) + 2.8 * math.sin(PI * min(1, v))), 0.3, lerp(0.0, 0.35, v))
    S['rook'].apply(P('hat', aL=(1.4, 1.1, 0.4), lL=(1.0, 1.4), lR=(0.2, 1.0)))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(11.5, 10.5, k), lerp(-17, -15.5, k), 1.0), A(7.6, -5.5, lerp(4.6, 3.6, k)), 30, -0.06)


def swim_night(S, k, t, lt):
    A = ocean(S, 'night', t, 0.8)
    y = lerp(3.6, 2.4, k)
    h = wave_h(0, y - 2.2, t, 0.8)
    kick = math.sin(t * 8)
    S['poon'].place(A(0, y, h - 0.75), 0.0, 1.2, 0.08 * kick)
    S['poon'].apply(P('swim', aL=(2.7 + 0.5 * kick, 0.35, 0.3), aR=(2.7 - 0.5 * kick, 0.35, 0.3), lL=(0.3 * kick, 0.3), lR=(-0.3 * kick, 0.3), head=(-1.0, 0.0)))
    S['face']['poon'] = 'scared'
    vest(S)
    for i, o in enumerate(S['planks']):
        px, py = -7 + i * 3.2, 5 + (i % 3) * 4.5
        o.location = A(px, py, wave_h(px, py, t, 0.8) + 0.06)
        o.rotation_euler = (0.1 * math.sin(t + i), 0, i * 1.3)
    smoke(S, A(-20, 70, 0), t, 6, 30, (0.2, 0), 5)
    splash(S, A(0.5, y - 2.6, h + 0.1), (lt * 1.6) % 1, 6, 0.8, size=0.6)
    cam(S, A(lerp(1.9, 1.4, k), lerp(-4.6, -4.0, k), 1.15), A(0, y - 2.0, 0.75), 52, 0.05)


def raft_found(S, k, t, lt):
    A = ocean(S, 'night', t, 0.6)
    ride(S, t, 0, 0, 0.15)
    u = ease(k * 1.3)
    aboard(S, S['poon'], -0.6, lerp(-3.4, -2.75, u), PI, P('up', aL=(2.0, 0.35, 0.5), aR=(2.1, 0.3, 0.4), head=(-0.3, 0.5), lean=0.35, lL=(0.2, 0.3), lR=(-0.2, 0.4)),
           z=lerp(-1.9, -1.25, u))
    S['face']['poon'] = 'tired'
    vest(S)
    aboard(S, S['rook'], 1.0, -0.2, -0.75, P('sit', aL=(0.3, 0.75, 1.5, -0.9), aR=(0.3, 0.75, 1.5, -0.9), head=(0.25, 0.3)))
    S['face']['rook'] = 'deadpan'
    splash(S, A(-0.6, -3.0, 0.3), (lt * 1.2) % 1, 8, 1.1, size=0.7)
    cam(S, A(lerp(-6.4, -5.6, k), lerp(-5.4, -4.6, k), lerp(2.5, 2.2, k)), A(0.0, -1.5, 1.35), 36, 0.03)


# ---------------------------------------------------------------- shots: the raft
def raft_alone(S, k, t, lt):
    A = ocean(S, 'day', t, 0.7)
    ride(S, t, 0, 0, 0.5)
    aboard(S, S['poon'], -0.3, -0.2, 0.6, P('sit', head=(0.35, 0.0)))
    S['face']['poon'] = 'tired'
    cam(S, A(lerp(5, 11, ease(k)), lerp(-9, -20, ease(k)), lerp(6, 30, ease(k))), A(0, 0, 0.6), lerp(34, 30, k), fill=0)


def rook_raft_cu(S, k, t, lt):
    A = ocean(S, 'day', t, 0.6)
    ride(S, t, 0, 0, 0.2)
    aboard(S, S['rook'], 0.35, -1.0, 0.1, P('sit', aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), head=(0.12, 0.1 * math.sin(t * 2))))
    S['face']['rook'] = 'deadpan'
    aboard(S, S['poon'], -1.3, 0.9, PI - 0.6, edge_sit())
    g = S['gulls'][0]
    u = ease(lt / 0.5)
    on(S, g['root'], S['rook'].extra['hat'], (0.0, lerp(1.2, 0.0, u), lerp(1.5, 0.52, u)), (0, 0, -PI / 2 + 0.4))
    g['root'].scale = (1.25, 1.25, 1.25)
    flap(g, t, 14, 0.9 * (1 - u) + 0.05, fold=u > 0.97)
    cam(S, A(lerp(1.7, 1.2, k), lerp(-8.2, -6.9, k), lerp(2.3, 2.2, k)), A(0.3, -0.9, 2.2), 48)


def raft_top(S, k, t, lt):
    A = ocean(S, 'noon', t, 0.5)
    ride(S, t, 0, 0, lerp(0.15, 0.4, k), tilt=0.5)
    aboard(S, S['poon'], -1.0, -1.75, 0.0, P('stand', aL=(0.2, 0.9, 0.2), aR=(0.2, 0.9, 0.2), head=(0, 0.3)), z=DECK + 0.2, pitch=-PI / 2)
    S['face']['poon'] = 'tired'
    aboard(S, S['rook'], 1.15, -0.9, 0.5, P('sit', aL=(0.3, 0.75, 1.5, -0.9), aR=(0.3, 0.75, 1.5, -0.9), head=(-0.5, 0.2 * math.sin(t * 3))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(0.3, lerp(-2.4, -1.2, k), lerp(15, 12.5, k)), A(0, 0.1, 0.5), 36, lerp(-0.1, 0.06, k))


def supplies(S, k, t, lt):
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, 0.0, tilt=0.6)
    u = ease(lt / 0.6)
    on(S, S['hand_p'].root, S['raft'], (lerp(0.5, -0.5, u), lerp(-0.9, 0.42, u), DECK + lerp(1.1, 0.72, u)), (-0.35, 0.0, PI + 0.25))
    S['hand_p'].root.scale = (0.85, 0.85, 0.85)
    S['hand_p'].grip(0.15 + 0.5 * ease((lt - 0.5) / 0.3))
    cam(S, A(lerp(1.5, 1.1, k), lerp(-3.4, -2.8, k), lerp(3.0, 2.6, k)), A(-0.8, 1.0, 0.85), 34)


def tin_empty(S, k, t, lt):
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, 0.15)
    for o in S['tins']:
        o.hide_render = True
    u = ease(lt / 0.45)
    aboard(S, S['rook'], 0.2, -0.9, 0.15, blend(P('stand', aR=(1.2, 0.2, 1.4)), P('stand', aR=(2.5, 0.75, 0.9, 0.3), head=(-0.5, -0.3)), u))
    S['face']['rook'] = 'sad'
    on(S, S['tin'], S['rook'].hands[1], (0, 0, -0.26), (0, 0, 0))
    S['tin'].scale = (1.2, 1.2, 1.2)
    c = max(0.0, min(1.0, (lt - 0.5) / 0.5))
    if c > 0:
        on(S, S['drops'][0], S['raft'], (0.62, -1.15, DECK + 3.3 - 2.6 * c * c))
        S['drops'][0].scale = (0.7, 0.7, 0.7)
    aboard(S, S['poon'], -1.25, 0.2, 0.9, P('sit', head=(0.45, 0.0)))
    S['face']['poon'] = 'tired'
    cam(S, A(lerp(1.6, 1.25, k), lerp(-6.8, -5.9, k), lerp(2.5, 2.9, k)), A(0.25, -0.9, 2.7), 42)


def spring_hook(S, k, t, lt):
    """Seen from above, stacked for the tall frame: the flashlight below, the spring drawn out of it upward, then the hook."""
    A = ocean(S, 'day', t, 0.4)
    ride(S, t, 0, 0, 0.0, tilt=0.4)
    R = S['raft']
    z = DECK + 0.7
    pull = ease(lt / 0.55)
    bend = ease((lt - 0.6) / 0.25)
    on(S, S['torch']['root'], R, (0.0, -1.35, z), (0, 0, PI / 2))
    S['torch']['root'].scale = (1.9, 1.9, 1.9)
    S['torch']['spring'].location = (0.42 + 0.42 * pull, 0, 0)
    on(S, S['hand_p'].root, R, (-0.75, -1.4, z + 0.3), (0.0, 0.0, PI / 2))
    S['hand_p'].grip(0.85)
    hy = -0.5 + 0.55 * pull
    on(S, S['hand_q'].root, R, (0.8, hy + 0.2 * bend, z + 0.3 + 0.2 * bend), (0.0, 0.0, -PI / 2))
    S['hand_q'].grip(0.85)
    if bend > 0.05:
        for o in S['torch']['spring'].children:
            o.hide_render = True
        on(S, S['hook'], R, (-0.1, hy - 0.15, z + 0.25 + 0.2 * bend), (-0.75, 0.2 * math.sin(t * 6), 0))
        sc = 2.8 + 1.0 * math.sin(PI * min(1, (lt - 0.6) / 0.3))
        S['hook'].scale = (sc, sc, sc)
    cam(S, A(lerp(0.15, 0.05, k), lerp(-4.9, -4.5, k), lerp(5.4, 5.0, k)), A(0.0, -1.35, DECK + 0.7), 38)


def line_cast(S, k, t, lt):
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, 0.0)
    tug = 0.3 * max(0.0, math.sin((lt - 0.6) * 14)) if lt > 0.6 else 0.0
    aboard(S, S['poon'], -0.75, -1.6, 0.0, edge_sit(aL=(1.0, 0.0, 0.5 + tug, 0.5), aR=(1.0, 0.0, 0.5 + tug, 0.5), head=(0.25, 0.0), lean=0.2 - 0.3 * tug))
    S['face']['poon'] = 'calm'
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-0.75, -2.45, DECK + 1.45 + 0.2 * tug), (-0.9, -5.2 + 0.4 * tug, -0.35))
    aboard(S, S['rook'], 0.95, -1.6, 0.0, edge_sit(aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), head=(0.1, lerp(0.75, 0.5, k))))
    S['face']['rook'] = 'smirk' if lt < 0.6 else 'shocked'
    if lt > 0.6:
        splash(S, A(-0.9, -5.0, 0.2), min(1, (lt - 0.6) / 0.5), 8, 1.0)
    cam(S, A(lerp(2.6, 2.0, k), lerp(-9.6, -8.4, k), lerp(1.5, 1.9, k)), A(0.1, -1.9, 1.75), 40)


def fish_up(S, k, t, lt):
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, -0.5)
    u = ease(k * 1.1)
    aboard(S, S['poon'], 0.3, -1.0, 0.25, blend(P('stand', aL=(1.2, 0.1, 0.6), aR=(1.2, 0.1, 0.6), lean=0.3), P('up', aL=(2.9, 0.3, 0.3), aR=(2.7, 0.2, 0.2), lean=-0.25), u))
    S['face']['poon'] = 'happy'
    f = S['fish'][0]
    fx, fy, fz = lerp(1.6, 0.5, u), lerp(-5.2, -1.9, u), -0.3 + 5.2 * math.sin(PI * 0.62 * u)
    on(S, f, S['raft'], (fx, fy, fz), (0.3 * math.sin(t * 9), 0.6 * math.sin(t * 22), 0.35))
    f.scale = (1.5, 1.5, 1.5)
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (0.25, -1.45, DECK + lerp(1.7, 3.3, u)), (fx, fy, fz))
    splash(S, A(1.8, -4.9, 0.2), min(1, lt / 0.6), 12, 1.8, size=1.4)
    cam(S, A(lerp(5.6, 4.6, k), lerp(-6.2, -5.2, k), lerp(1.1, 1.6, k)), A(0.7, -2.2, lerp(1.8, 2.5, k)), 32, 0.05)


def tin_knife(S, k, t, lt):
    A = ocean(S, 'day', t, 0.4)
    ride(S, t, 0, 0, 0.0, tilt=0.4)
    R = S['raft']
    f = S['fish'][1]
    on(S, f, R, (0.0, -0.9, DECK + 0.12), (PI / 2, 0, 0.15))
    f.scale = (1.9, 1.9, 1.9)
    saw = 0.3 * math.sin(lt * 13)
    on(S, S['hand_p'].root, R, (0.35 + saw, -1.55, DECK + 0.62), (-0.5, 0.0, PI - 0.2))
    S['hand_p'].grip(0.85)
    on(S, S['blade'], R, (0.25 + saw, -0.95, DECK + 0.4), (0.0, PI / 2 - 0.3, PI / 2 - 0.2))
    S['blade'].scale = (0.6, 0.22, 0.02)
    on(S, S['line'], R, (0, 0, 0))
    span(S['line'], (-2.0, 0.35, 2.3), (2.0, 0.35, 2.3))
    for i, o in enumerate(S['strips']):
        on(S, o, R, (-1.5 + i * 0.6, 0.35, 2.02 + 0.03 * math.sin(t * 3 + i)), (0.12 * math.sin(t * 2.5 + i), 0, 0))
        o.scale = (0.26, 0.05, 0.56)
    cam(S, A(lerp(1.0, 0.6, k), lerp(-5.6, -5.0, k), lerp(3.6, 3.3, k)), A(0.0, -0.4, 1.25), 38)


def rain_catch(S, k, t, lt):
    A = ocean(S, 'storm', t, 0.9)
    ride(S, t, 0, 0, 0.2)
    aboard(S, S['poon'], -0.75, -0.7, 0.2, P('up', aL=(2.5, 0.75, 0.3), aR=(2.5, 0.75, 0.3), head=(-0.45, 0.0)))
    S['face']['poon'] = 'happy'
    on(S, S['cloth'], S['raft'], (-0.75, -1.05, DECK + 3.2 + 0.05 * math.sin(t * 5)), (PI, 0, 0))
    on(S, S['tin'], S['raft'], (-0.75, -1.1, DECK + 0.25))
    S['tin'].scale = (2.2, 2.2, 2.2)
    for i in range(4):
        d = S['drops'][i]
        u = (t * 2.2 + i * 0.25) % 1
        on(S, d, S['raft'], (-0.75, -1.05, DECK + 3.1 - 2.4 * u))
        d.scale = (0.8, 0.8, 1.6)
    aboard(S, S['rook'], 1.0, -0.9, -0.25, P('shrug', aL=(0.5, 1.0, 1.2, -0.9), aR=(0.5, 1.0, 1.2, -0.9), head=(-0.38, 0.0)))
    S['face']['rook'] = 'laugh'
    cam(S, A(lerp(1.1, 0.7, k), lerp(-8.6, -7.6, k), lerp(1.6, 2.0, k)), A(0.1, -0.8, 2.5), 36)


def bird_grab(S, k, t, lt):
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, -0.15)
    aboard(S, S['rook'], 0.5, -1.1, 0.1, P('stand', aL=(0.1, 0.5, 0.3), aR=(0.1, 0.5, 0.3), head=(0.0, 0.0)))
    u = ease((lt - 0.45) / 0.3)
    S['face']['rook'] = 'shocked' if u > 0.5 else 'deadpan'
    g = S['gulls'][0]
    on(S, g['root'], S['rook'].extra['hat'], (0, 0, 0.52 + 0.1 * u), (0, 0, -PI / 2 + 0.5))
    g['root'].scale = (1.3, 1.3, 1.3)
    flap(g, t, 22, 0.9 * u, fold=u < 0.05)
    aboard(S, S['poon'], lerp(-1.0, 0.1, u), lerp(0.9, -0.25, u), 0.35, blend(P('stand', aL=(0.9, 0.4, 0.9), aR=(0.9, 0.4, 0.9), lean=0.25, lL=(0.3, 0.5), lR=(0.3, 0.5), lift=-0.2),
                                                                           P('up', aL=(2.35, 0.1, 0.5, 0.4), aR=(2.35, 0.1, 0.5, 0.4), lean=0.3), u))
    S['face']['poon'] = 'calm'
    for i, gg in enumerate(S['gulls'][1:3]):
        gg['root'].location = A(-5 + i * 7 + t * 1.5, 22 + i * 8, 7 + i * 2 + math.sin(t * 2 + i))
        gg['root'].scale = (2.5, 2.5, 2.5)
        flap(gg, t + i, 7, 0.6)
    cam(S, A(lerp(1.7, 1.2, k), lerp(-7.2, -6.0, k), lerp(2.4, 2.7, k)), A(0.4, -0.9, 2.75), 42)


def shark(S, k, t, lt):
    A = ocean(S, 'noon', t, 0.5)
    ride(S, t, 0, 0, 0.35)
    a = 2.2 + lt * 1.35
    sx, sy = math.cos(a) * 3.5, math.sin(a) * 4.4
    S['shark'].location = A(sx, sy, wave_h(sx, sy, t, 0.5) - 0.12)
    S['shark'].rotation_euler = (0, 0, a + PI / 2)
    S['shark'].scale = (1.6, 1.6, 1.6)
    aboard(S, S['rook'], 0.2, 0.0, a + PI / 2 + 0.4, P('hat', aL=(0.3, 0.9, 1.3), lL=(0.9, 1.5), lift=0.25 + 0.1 * abs(math.sin(t * 9)), head=(0.3, 0.0)))
    S['face']['rook'] = 'shocked'
    feathers(S, A(0.2, -0.3, 3.2), min(1, lt / 0.9), 5)
    aboard(S, S['poon'], -1.2, -1.2, 0.5, P('stand', aL=(1.0, 0.2, 0.7), aR=(1.0, 0.2, 0.7), lean=0.3, lL=(0.4, 0.7), lR=(0.2, 0.5), lift=-0.2, head=(0.1, 0.3)))
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-1.45, -1.9, DECK + 1.5), (-2.4, -4.4, -0.3))
    cam(S, A(lerp(4.5, 3.0, k), lerp(-13.5, -11.5, k), lerp(10.5, 12, k)), A(0.3, -0.4, 0.8), 30, lerp(0.05, -0.04, k))


# ---------------------------------------------------------------- shots: missed, then found
def freighter_pass(S, k, t, lt):
    A = ocean(S, 'dusk', t, 0.6)
    ride(S, t, 0, 0, 0.3)
    w = math.sin(t * 9)
    aboard(S, S['poon'], -0.3, 0.3, PI + 0.1, P('up', aL=(2.6, 0.5 + 0.35 * w, 0.2), aR=(2.6, 0.5 - 0.35 * w, 0.2), head=(-0.2, 0.0)))
    x = lerp(-55, 5, k)
    S['frt'].location = A(x, 190, 0)
    S['frt'].scale = (1.7, 1.7, 1.7)
    smoke(S, A(x - 5, 190, 21), t, 9, 40, (-1.4, 0), 3.4)
    cam(S, A(lerp(1.0, 1.8, k), lerp(-11.5, -10.0, k), lerp(4.6, 5.0, k)), A(lerp(-6, -2, k), 60, 3.0), 40, fill=0.6)


def rook_wave(S, k, t, lt):
    A = ocean(S, 'dusk', t, 0.6)
    ride(S, t, 0, 0, 0.2)
    u = ease((lt - 0.55) / 0.4)
    w = math.sin(t * 11) * (1 - u)
    aboard(S, S['rook'], 0.75, -1.2, 0.0, blend(P('up', aL=(2.7, 0.5 + 0.4 * w, 0.2), aR=(2.7, 0.5 - 0.4 * w, 0.2), head=(-0.25, 0.0), lift=0.12 * abs(w)),
                                              P('stand', aL=(0.1, 0.2, 0.1), aR=(0.1, 0.2, 0.1), head=(0.35, 0.0), lean=0.15), u))
    S['face']['rook'] = 'sad' if u > 0.5 else 'shocked'
    aboard(S, S['poon'], -0.9, -0.9, 0.1, blend(P('up', aL=(2.6, 0.5, 0.2), aR=(2.6, 0.5, 0.2)), P('stand', head=(0.3, 0.0), lean=0.1), ease((lt - 0.35) / 0.5)))
    S['face']['poon'] = 'tired'
    cam(S, A(lerp(0.6, 0.3, k), lerp(-9.4, -8.0, k), lerp(2.0, 2.4, k)), A(0.0, -1.0, 2.6), 40, fill=1.4)


def plane_over(S, k, t, lt):
    A = ocean(S, 'day', t, 0.6)
    ride(S, t, 0, 0, 0.2)
    aboard(S, S['poon'], -0.9, -0.2, PI - 0.15, P('up', aL=(2.7, 0.6 + 0.3 * math.sin(t * 9), 0.2), aR=(2.7, 0.6 - 0.3 * math.sin(t * 9), 0.2), head=(-0.5, 0.0)))
    aboard(S, S['rook'], 0.8, -0.6, PI + 0.35, P('reach', aR=(2.5, 0.2, 0.05), aL=(0.2, 1.9, 1.6, -1.5), head=(-0.5, 0.2)))
    S['face']['rook'] = 'shocked'
    S['plane'].location = A(lerp(5, 1, k), lerp(95, 8, k), lerp(26, 16.5, k))
    S['plane'].rotation_euler = (0.25 * math.sin(lt * 2.2), 0.08, -PI / 2)
    S['plane'].scale = (1.5, 1.5, 1.5)
    for p in S['props']:
        p.rotation_euler = (t * 40, 0, 0)
    cam(S, A(lerp(1.4, 1.0, k), lerp(-10.4, -9.6, k), 1.7), A(0.2, lerp(6, 2, k), lerp(7.0, 7.6, k)), 22, 0.04)


def storm_hide(S, k, t, lt):
    fl = 1 - (lt - 0.5) / 0.2 if 0.5 <= lt < 0.7 else 0.0
    A = ocean(S, 'storm', t * 1.5, 2.6, flash=fl)
    ride(S, t * 1.5, 0, 0, 0.3, tilt=1.6)
    aboard(S, S['poon'], -0.9, -1.7, 0.2, P('stand', aL=(2.6, 0.5, 0.2), aR=(2.6, 0.5, 0.2), head=(-0.5, 0.0)), z=DECK + 0.2, pitch=-PI / 2 + 0.05, roll=PI)
    aboard(S, S['rook'], 1.5, 0.75, 0.6, P('sit', aL=(1.3, -0.3, 1.2, 0.4), aR=(1.3, -0.3, 1.2, 0.4), head=(0.3, 0.0), lean=0.4))
    S['face']['rook'] = 'shocked'
    S['hat_tip'] = 0.6
    splash(S, A(-3, -1.5, 0.6), (lt * 1.4) % 1, 16, 4.5, size=3.5)
    cam(S, A(lerp(4.5, 3.4, k), lerp(-11, -9.6, k), lerp(4.2, 2.8, k) + wave_h(4, -10, t * 1.5, 1.2)), A(0, 0, 1.4), 30, 0.12 * math.sin(t * 2.2))


def coast_dawn(S, k, t, lt):
    A = ocean(S, 'dawn', t, 0.5)
    ride(S, t, 0, 0, 0.4)
    S['coast'].location = A(0, 330, 0)
    aboard(S, S['poon'], -0.4, 0.0, PI - 0.4, blend(P('sit', head=(0.4, 0.0)), P('sit', head=(-0.2, 0.3), aR=(1.3, 0.3, 0.4)), ease(k * 1.5)))
    for i, g in enumerate(S['gulls']):
        g['root'].location = A(-9 + i * 5.5 + t * 1.6, 16 + i * 7, 7.5 + i * 1.4 + 0.5 * math.sin(t * 2 + i))
        g['root'].rotation_euler = (0, 0, 0.2)
        g['root'].scale = (2.4, 2.4, 2.4)
        flap(g, t + i * 0.3, 7.5, 0.65)
    cam(S, A(lerp(-3.5, -2.2, k), lerp(-12.5, -10.5, k), lerp(3.0, 5.4, k)), A(0.5, 30, lerp(5.5, 6.5, k)), 36, fill=0.6)


def fish_boat(S, k, t, lt):
    A = ocean(S, 'dawn', t, 0.5)
    ride(S, t, 0, 0, 0.3)
    S['coast'].location = A(0, 330, 0)
    bx, by = lerp(15, 6.6, ease(k)), lerp(9, 3.2, ease(k))
    S['boat'].location = A(bx, by, wave_h(bx, by, t, 0.5) + 0.25)
    S['boat'].rotation_euler = (0.05 * math.sin(t * 1.6), 0.03 * math.sin(t * 1.2), PI + 0.45)
    S['boat'].scale = (1.35, 1.35, 1.35)
    for i, m in enumerate(S['men']):
        aboard(S, m, (2.0, 0.35, -1.6)[i], (0.45, 0.55, 0.45)[i], PI / 2 + (0.4, 0.2, -0.1)[i],
               (P('point', aR=(1.5, 0.3, 0.05)), P('stand', aL=(1.9, 0.3, 0.9), head=(0, -0.3)), P('hips', head=(0.05, -0.4)))[i], z=0.9, on='boat')
        m.root.scale = (0.74, 0.74, 0.74)
    S['face']['men'] = 'shock'
    aboard(S, S['poon'], -0.2, 0.3, PI - 1.0, blend(P('sit', head=(0.1, 0.0)), P('stand', aL=(2.4, 0.4, 0.4), head=(-0.15, 0.0), lean=0.1), ease(k * 1.4)))
    cam(S, A(lerp(-5.6, -4.6, k), lerp(-8.4, -7.4, k), lerp(2.6, 3.1, k)), A(lerp(4.0, 3.0, k), 1.4, 2.6), 34)


def hands_meet(S, k, t, lt):
    A = ocean(S, 'dawn', t, 0.4)
    S['boat'].location = A(7, 16, 0.2)
    S['boat'].rotation_euler = (0, 0, 0.3)
    S['boat'].scale = (1.5, 1.5, 1.5)
    S['coast'].location = A(0, 330, 0)
    for hnd in ('hand_p', 'hand_f'):
        S[hnd].root.scale = (1.5, 1.5, 1.5)
    u = ease(lt / 0.45)
    g = ease((lt - 0.4) / 0.15)
    S['hand_f'].place(A(lerp(1.5, 0.42, u), 0.0, lerp(3.9, 2.75, u)), (PI / 4, 0.0, -PI / 2))
    S['hand_f'].grip(0.15 + 0.7 * g)
    S['hand_p'].place(A(lerp(-1.6, -0.42, u), 0.1, lerp(0.7, 1.95, u)), (-PI / 4, 0.0, PI / 2))
    S['hand_p'].grip(0.15 + 0.7 * g)
    if lt > 0.42:
        splash(S, A(0, -0.3, 2.3), min(1, (lt - 0.42) / 0.5), 8, 1.0, size=0.6)
    cam(S, A(lerp(0.6, 0.3, k), lerp(-6.4, -5.4, k), lerp(2.2, 2.4, k)), A(0, 0, 2.35), 45, 0.06)


def rook_stunned(S, k, t, lt):
    A = ocean(S, 'dawn', t, 0.5)
    ride(S, t, 0, 0, 0.1)
    S['coast'].location = A(0, 330, 0)
    u = ease((lt - 0.6) / 0.4)
    aboard(S, S['rook'], 0.2, -0.9, 0.15, blend(P('stand', aL=(0.1, 0.6, 0.3), aR=(0.1, 0.6, 0.3), head=(-0.05, 0.0)), P('hat', head=(0.15, 0.0)), u))
    S['face']['rook'] = 'warm' if u > 0.5 else 'shocked'
    S['hat_tip'] = u * 0.6
    bx, by = lerp(-5, -9, k), lerp(12, 20, k)
    S['boat'].location = A(bx, by, wave_h(bx, by, t, 0.5) + 0.25)
    S['boat'].rotation_euler = (0, 0, 2.3)
    S['boat'].scale = (1.35, 1.35, 1.35)
    for i, m in enumerate(S['men'][:2]):
        aboard(S, m, (1.9, -1.9)[i], 0.2, PI / 2, P('stand'), z=0.9, on='boat')
        m.root.scale = (0.74, 0.74, 0.74)
    aboard(S, S['poon'], 0.0, 0.0, -PI / 2, P('sit', head=(0.0, 0.0)), z=1.0, on='boat')
    S['poon'].root.scale = (0.74, 0.74, 0.74)
    cam(S, A(lerp(1.3, 0.8, k), lerp(-6.6, -5.4, k), lerp(2.4, 2.7, k)), A(0.3, -0.8, 2.8), 44)


def poon_safe(S, k, t, lt):
    A = ocean(S, 'dawn', t, 0.5)
    S['coast'].location = A(0, 300, 0)
    S['boat'].location = A(lerp(-1.2, 0.4, k), 0, wave_h(0, 0, t, 0.5) + 0.3)
    S['boat'].rotation_euler = (0.04 * math.sin(t * 1.5), 0.03 * math.sin(t * 1.1), 0.25)
    S['boat'].scale = (1.6, 1.6, 1.6)
    aboard(S, S['poon'], 0.3, -0.5, -0.1, P('sit', head=(-0.1, 0.25), aL=(0.6, 0.0, 1.3, 0.8), aR=(0.6, 0.0, 1.3, 0.8)), z=1.0, on='boat')
    S['face']['poon'] = 'happy'
    aboard(S, S['men'][0], -0.5, -0.6, -0.4, P('stand', aR=(0.9, 0.2, 1.0), head=(0.2, 0.5)), z=0.9, on='boat')
    aboard(S, S['men'][1], -1.15, -0.2, -0.35, P('stand', aL=(1.2, 0.1, 0.9), aR=(1.2, 0.1, 0.9)), z=0.9, on='boat')
    S['face']['men'] = 'happy'
    tip = math.sin(PI * ease((lt - 0.3) / 0.9)) if lt > 0.3 else 0
    aboard(S, S['rook'], 1.15, -0.2, 0.2, blend(P('stand', head=(0, 0.3)), P('hat', head=(0.2, 0.3)), tip), z=1.0, on='boat')
    for rig in [S['poon'], S['rook']] + S['men'][:2]:
        rig.root.scale = (0.66, 0.66, 0.66)
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    for i, g in enumerate(S['gulls'][:3]):
        g['root'].location = A(-6 + i * 5 + t, 26 + i * 6, 9 + i + 0.5 * math.sin(t * 2 + i))
        g['root'].scale = (2.4, 2.4, 2.4)
        flap(g, t + i * 0.4, 7.5, 0.65)
    cam(S, A(lerp(1.7, 1.1, k), lerp(-11.2, -10.2, k), lerp(3.6, 3.3, k)), A(0.45, 0.0, 2.9), 36)


# ---------------------------------------------------------------- shots: the pier
def rook_pier(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, '5A3A6A', 0.9)
    S['rook'].place(A(0, 0, 1.4), 0.25)
    S['rook'].apply(P('cross', head=(0.05, -0.2 + 0.24 * math.sin(t * 4.2) * max(0, 1 - lt / 0.9))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(2.3, 1.6, k), lerp(-7.4, -5.6, k), 3.6), A(0.05, 0, 3.3), 40)


def rook_jump(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, '5A3A6A', 0.9)
    u = ease(lt / 0.35)
    y = lerp(0.5, 5.5, max(0.0, (lt - 0.3)) / max(0.3, 1.3))
    pose = blend(P('hat', aL=(0.2, 1.9, 1.6, -1.5)), walk(t, 1.9), ease((lt - 0.3) / 0.2))
    S['rook'].place(A(0.2, y, 1.4), PI + 0.1)
    S['rook'].apply(pose if lt > 0.3 else blend(P('stand'), P('hat', aL=(0.2, 1.9, 1.6, -1.5)), u))
    cam(S, A(lerp(-1.6, -1.2, k), lerp(-5.4, -4.2, k), 2.2), A(0.3, y + 1.5, 3.2), 32)


def signoff(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, '5A3A6A', 0.9)
    S['rook'].place(A(0, 0, 1.4), 0.15)
    tip = math.sin(PI * ease(lt / 0.8)) if lt < 0.8 else 0
    S['rook'].apply(blend(P('stand', aL=(0.9, 0.25, 1.2), head=(0.05, 0)), P('hat', aL=(0.9, 0.25, 1.2), head=(0.22, 0)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'smirk'
    c = max(0.0, min(1.0, (lt - 0.25) / 0.9))
    S['hook'].location = A(-0.85 - 0.15 * c, -0.8, 3.0 + 1.5 * math.sin(c * PI))
    S['hook'].rotation_euler = (t * 16, t * 7, 0)
    S['hook'].scale = (1.5, 1.5, 1.5)
    cam(S, A(lerp(1.1, 0.8, k), lerp(-6.6, -5.4, k), 2.4), A(0, 0, 3.45), 38)


# ---------------------------------------------------------------- stills for the case board
def photo_raft(S, k, t, lt):
    A = ocean(S, 'day', 3.0, 0.6)
    ride(S, 3.0, 0, 0, 0.6)
    cam(S, A(6.5, -9.5, 4.6), A(0, 0, 1.2), 40)


def photo_poon(S, k, t, lt):
    A = ocean(S, 'dawn', 1.0, 0.4)
    ride(S, 1.0, 0, 0, 0.3)
    aboard(S, S['poon'], 0.0, -0.6, 0.2, P('stand', head=(0, 0.1)))
    S['face']['poon'] = 'happy'
    cam(S, A(0.8, -6.2, 2.6), A(0.0, -0.6, 2.4), 48)


SHOTS3D = {f.__name__: f for f in (
    torpedo_hit, ship_down, raft_alone, rook_raft_cu, rook_pier, rook_jump, ship_wide, sub_wake, rook_deck, jump, swim_night, raft_found,
    raft_top, supplies, tin_empty, spring_hook, line_cast, fish_up, tin_knife, rain_catch, bird_grab, shark, freighter_pass, rook_wave,
    plane_over, storm_hide, coast_dawn, fish_boat, hands_meet, rook_stunned, poon_safe, signoff)}
STILLS = dict(raft=photo_raft, poon=photo_poon)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same ocean, more of it: the cabin boy who quit, the mess room, Cape Town, the plank, the other raft,
# the rationing, the wrist rope and the knots, the nail hook, the drying line, the nest, the storm's damage, the
# shark on the deck, the fins, the swimming, the moons, the freighter up close, the marker buoy, the green water,
# the shirt, Belem, the ward, the medal, the watch, the recruiting desk and a stoop in Brooklyn.
ORG.update(mess=(1200, 0, 0), quay=(1800, 0, 0), belem=(2400, 0, 0), ward=(3000, 0, 0), hall=(3600, 0, 0), stoop=(4200, 0, 0))
EXTRAS = [dict(top='2A3040', pants='2A3040', hand='E0B090', boot='15151A'), dict(top='F0F0E8', pants='E0E0D8', hand='C89A70', boot='E0E0D8'),
          dict(top='7A5A3A', pants='3A3A44', hand='B88860', boot='2A2420'), dict(top='5A6A7A', pants='2E3440', hand='D9A878', boot='2A2420')]
EXHEAD = [('E0B090', '6A5A4A'), ('C89A70', '2A1A10'), ('B88860', '1A1410'), ('D9A878', '14110F')]
OLD = dict(top='8A7A5A', pants='3A3A44', hand=SKIN, boot='2A2420')


# The kit's add() goes through Blender operators, which get slower with every object already in the scene. The same
# primitives built straight from mesh data cost the same however big the scene is (the operators call these very bmesh
# routines). From here on the whole file, including the Short's sets above, builds with the fast versions.
import bmesh  # noqa: E402

_add0 = add


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'plane':
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=kw.get('size', 2.0) / 2)
    elif kind in ('cylinder', 'cone'):
        r1, r2 = (kw.get('radius', 1.0),) * 2 if kind == 'cylinder' else (kw.get('radius1', 1.0), kw.get('radius2', 0.0))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=r1, radius2=r2, depth=kw.get('depth', 2.0))
    elif kind == 'ico_sphere':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('subdivisions', 2), radius=kw.get('radius', 1.0))
    else:
        bm.free()
        return _add0(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
    me = bpy.data.meshes.new(kind)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(kind, me)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    me.materials.append(K.mat(col, rough, emit, alpha))
    if parent:
        o.parent = parent
    return o


def empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new('empty', None)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    return o


def room(r, w, d0, d1, hgt, floor, wall, ceil=None):
    """Floor, back wall and two long side walls (the 16:9 lens sees a long way to each side)."""
    add('cube', floor, (0, (d0 + d1) / 2, -0.1), scale=(w, d1 - d0, 0.2), size=1, parent=r)
    add('cube', wall, (0, d1, hgt / 2), scale=(w, 0.2, hgt), size=1, parent=r)
    for s in (-1, 1):
        add('cube', wall, (s * w / 2, (d0 + d1) / 2, hgt / 2), scale=(0.2, d1 - d0, hgt), size=1, parent=r)
    if ceil:
        add('cube', ceil, (0, (d0 + d1) / 2, hgt + 0.1), scale=(w, d1 - d0, 0.2), size=1, parent=r)


def set_mess(r):
    """A steamer's mess room: riveted walls, portholes, a long table. Used for the cabin boy and for the steward."""
    room(r, 22, -14, 5, 4.4, '5A4632', '7E8A80', '5E6860')
    for x in (-8, -4, 0, 4, 8):
        add('cube', '66726A', (x + 2, 4.86, 2.2), scale=(0.16, 0.08, 4.4), size=1, parent=r)
        add('torus', 'C89A3A', (x, 4.86, 2.7), rot=(PI / 2, 0, 0), major_radius=0.55, minor_radius=0.08, major_segments=12, minor_segments=4, parent=r, rough=0.35)
        add('cylinder', '3A7AA8', (x, 4.88, 2.7), rot=(PI / 2, 0, 0), radius=0.5, depth=0.04, vertices=12, parent=r, emit=1.6)
    add('cube', '7A5A36', (1.5, 2.2, 1.25), scale=(6.4, 1.6, 0.12), size=1, parent=r)
    for x in (-1.4, 4.4):
        add('cube', '5A4028', (x, 2.2, 0.6), scale=(0.2, 1.3, 1.2), size=1, parent=r)
    for y in (0.9, 3.5):
        add('cube', '6A4C2E', (1.5, y, 0.7), scale=(6.4, 0.5, 0.1), size=1, parent=r)
        for x in (-1.2, 4.2):
            add('cube', '5A4028', (x, y, 0.35), scale=(0.14, 0.4, 0.7), size=1, parent=r)
    for i, x in enumerate((-0.4, 1.0, 2.4, 3.6)):
        add('cylinder', ('E8E0D0', 'D8B048')[i % 2], (x, 2.2 + (i % 2) * 0.3, 1.38), radius=0.12, depth=0.16, vertices=7, parent=r)
    add('cube', '4A525E', (-6.6, 3.9, 1.0), scale=(4.2, 1.6, 2.0), size=1, parent=r)
    add('cube', '2C3138', (-6.6, 3.9, 2.03), scale=(4.4, 1.7, 0.08), size=1, parent=r)
    for i, x in enumerate((-7.8, -6.6, -5.4)):
        add('cylinder', 'A8B0B8', (x, 3.9, 2.35 + (i % 2) * 0.08), radius=0.36, depth=0.56 + (i % 2) * 0.16, vertices=8, parent=r, rough=0.35)
    add('cylinder', '2C3138', (-8.6, 4.4, 3.2), radius=0.16, depth=2.4, vertices=6, parent=r)
    for z in (2.6, 3.3):
        add('cube', '6A4C2E', (7.6, 4.6, z), scale=(3.6, 0.5, 0.08), size=1, parent=r)
        for i in range(5):
            add('cylinder', ('B8442E', 'D8B048', '5E7048')[i % 3], (6.2 + i * 0.7, 4.6, z + 0.2), radius=0.16, depth=0.3, vertices=7, parent=r)
    add('cube', '3A4252', (10.85, 0.5, 1.75), scale=(0.12, 1.6, 3.5), size=1, parent=r)
    add('cylinder', '3A7AA8', (10.78, 0.5, 2.5), rot=(0, PI / 2, 0), radius=0.3, depth=0.04, vertices=10, parent=r, emit=1.2)
    add('cube', '3A4252', (-10.85, -2.0, 1.75), scale=(0.12, 1.6, 3.5), size=1, parent=r)
    for x in (-3.0, 5.0):
        add('cone', 'FFD8A0', (x, 2.0, 3.9), radius1=0.5, radius2=0.12, depth=0.36, vertices=8, parent=r, emit=6)
        light((x, 2.0, 3.5), 500, 'FFD8A0', kind='POINT', parent=r)
    aim = empty((0, 2, 1.8), r)
    light((-5, -8, 4.0), 2600, 'FFE2B8', 4.0, aim, parent=r)
    light((7, -6, 2.5), 900, '6E8FD8', 4.0, aim, parent=r)
    return {}


def set_quay(r):
    """Cape Town docks on a clear morning: a stone quay, a shed, a crane, and a flat-topped mountain behind."""
    add('plane', '1E5A78', (0, 0, 0), size=1400, parent=r, rough=0.25)
    add('cube', '8A8478', (0, -9, 0.9), scale=(220, 18, 1.8), size=1, parent=r)
    add('cube', '6E6A60', (0, -0.1, 1.62), scale=(220, 0.4, 0.4), size=1, parent=r)
    add('cube', 'A0522E', (-24, -11, 5.0), scale=(20, 9, 6.4), size=1, parent=r)
    add('cube', '6A3A26', (-24, -11, 8.4), scale=(21, 10, 0.5), size=1, parent=r)
    add('cube', '2C3138', (-24, -6.45, 4.0), scale=(6, 0.1, 4.4), size=1, parent=r)
    add('cube', '9A8A70', (30, -12, 4.2), scale=(16, 8, 4.8), size=1, parent=r)
    add('cube', '5E5648', (30, -12, 6.8), scale=(17, 9, 0.4), size=1, parent=r)
    for x in (-52, 56):
        add('cube', ('8A5A3A', '7A8A90')[x > 0], (x, -12, 4.6), scale=(22, 9, 5.6), size=1, parent=r)
    for i, (x, y, s, c) in enumerate(((-9, -3.2, 1.3, '7A5A3A'), (-7.6, -3.6, 1.0, '6A4E32'), (-8.6, -3.3, 1.0, '8A6844'), (9.5, -4.4, 1.2, '7A5A3A'),
                                      (11, -4.0, 0.9, '6A4E32'), (-14, -5, 1.4, '8A6844'), (17, -6, 1.3, '6A4E32'))):
        z = 1.8 + s / 2 + (1.3 if i == 2 else 0)
        add('cube', c, (x, y, z), rot=(0, 0, i * 0.4), scale=(s, s, s), size=1, parent=r)
        add('cube', '4A3828', (x, y, z), rot=(0, 0, i * 0.4), scale=(s * 1.04, s * 0.16, s * 1.04), size=1, parent=r)
    for x in range(-40, 41, 10):
        add('cylinder', '2A2E36', (x, -0.9, 2.1), radius=0.3, depth=0.6, vertices=8, parent=r)
        add('cylinder', '2A2E36', (x, -0.9, 2.45), radius=0.4, depth=0.12, vertices=8, parent=r)
    for i in range(4):
        add('cylinder', ('5E7048', '8A5A3A')[i % 2], (4.6 + i * 0.9, -5.2 - (i % 2) * 0.8, 2.35), radius=0.4, depth=1.1, vertices=8, parent=r)
    cr = empty((19, -5.5, 1.8), r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cube', '3A4048', (sx * 1.2, sy * 1.2, 4.5), scale=(0.3, 0.3, 9), size=1, parent=cr)
    add('cube', '3A4048', (0, 0, 9.4), scale=(3.4, 3.4, 1.4), size=1, parent=cr)
    add('cube', 'C89A3A', (0, 0, 11.0), scale=(2.2, 2.2, 1.8), size=1, parent=cr)
    add('cube', '3A4048', (-4.5, 5.5, 15.5), rot=(0.75, 0, 0.7), scale=(0.4, 18, 0.4), size=1, parent=cr)
    add('cylinder', '15181D', (-8.6, 10.5, 12.5), radius=0.04, depth=13, vertices=4, parent=cr)
    add('cube', '8A6844', (-8.6, 10.5, 5.4), scale=(1.6, 1.6, 1.3), size=1, parent=cr)
    # the mountain: a long flat top with shoulders, a cloth of cloud lying on it
    add('cube', '56685C', (0, 620, 60), scale=(560, 120, 120), size=1, parent=r)
    add('cube', '4C5E52', (0, 560, 22), scale=(900, 60, 44), size=1, parent=r)
    add('cone', '5E7062', (-390, 600, 62), radius1=150, radius2=4, depth=124, vertices=7, parent=r)
    add('cone', '4C5E52', (400, 610, 48), radius1=170, radius2=30, depth=96, vertices=7, parent=r)
    for i in range(9):
        add('ico_sphere', 'FFFFFF', (-250 + i * 62, 600, 124 + (i % 2) * 5), scale=(1.6, 1, 0.3), radius=30, subdivisions=1, parent=r, emit=0.9)
    for i in range(16):
        add('cube', ('E8E0D0', 'D8C8B0', 'C8D0D8')[i % 3], (-300 + i * 40 + (i * 13) % 17, 300 + (i % 3) * 20, 4 + (i % 4) * 2),
            scale=(22, 14, 8 + (i % 4) * 4), size=1, parent=r)
    ship = make_steamer(empty((0, 9, 0.3), r))
    tgt = empty((0, 0, 0), r)
    light((80, -90, 120), 3.6, 'FFE8C8', kind='SUN', target=tgt, parent=r)
    return dict(qship=ship)


def palm(r, x, y, z, hgt=7.0, lean=0.12):
    p = empty((x, y, z), r, (0, lean, x * 0.7))
    add('cylinder', '7A5A36', (0, 0, hgt / 2), radius=0.22, depth=hgt, vertices=6, parent=p)
    for i in range(7):
        a = i * 0.9
        add('cone', ('2C7A3C', '347A44')[i % 2], (math.cos(a) * 1.5, math.sin(a) * 1.5, hgt - 0.2), rot=(math.sin(a) * 1.25, -math.cos(a) * 1.25, 0),
            scale=(0.35, 1, 1), radius1=0.9, radius2=0.0, depth=3.6, vertices=4, parent=p)


def set_belem(r):
    """The waterfront at Belem (a reconstruction): a stone quay, painted houses, a church, palms."""
    add('plane', '3E7A64', (0, 0, 0), size=1400, parent=r, rough=0.3)
    add('cube', 'B8AE98', (0, 13, 0.7), scale=(240, 20, 1.4), size=1, parent=r)
    add('cube', '8E8672', (0, 2.9, 1.3), scale=(240, 0.4, 0.4), size=1, parent=r)
    cols = ('E8B04A', 'D86A4A', '6AA8C8', 'E8D8B0', '7AB87A', 'D88AA0', 'F0E4C8')
    for i in range(17):
        x = -64 + i * 8.0
        hgt = 6.0 + (i * 3) % 4
        add('cube', cols[i % 7], (x, 18, 1.4 + hgt / 2), scale=(7.6, 8, hgt), size=1, parent=r)
        add('cube', 'A8523A', (x, 18, 1.4 + hgt + 0.25), scale=(8.0, 8.4, 0.5), size=1, parent=r)
        add('cube', '3A2A20', (x - 1.8, 13.95, 2.9), scale=(1.4, 0.1, 3.0), size=1, parent=r)
        for j in range(2):
            add('cube', '2A3A44', (x + 0.6 + j * 2.0, 13.95, 3.6), scale=(1.1, 0.1, 1.6), size=1, parent=r)
            if hgt > 7:
                add('cube', '2A3A44', (x - 1.8 + j * 3.2, 13.95, 6.6), scale=(1.1, 0.1, 1.5), size=1, parent=r)
    ch = empty((-22, 30, 1.4), r)
    add('cube', 'F4F0E4', (0, 0, 7), scale=(12, 10, 14), size=1, parent=ch)
    for s in (-1, 1):
        add('cube', 'F4F0E4', (s * 5, -3, 11), scale=(3.4, 3.4, 22), size=1, parent=ch)
        add('cone', 'A8523A', (s * 5, -3, 23.5), radius1=2.6, radius2=0.2, depth=3.4, vertices=4, parent=ch)
    for x, y in ((-12, 6.5), (-5, 9.5), (9, 7.5), (16, 10), (27, 7), (-30, 8)):
        palm(r, x, y, 1.4, 6.5 + (x % 3))
    for x in range(-30, 31, 10):
        add('cylinder', '4A4A44', (x, 3.6, 1.7), radius=0.28, depth=0.6, vertices=8, parent=r)
    for i, (x, y, s) in enumerate(((6.5, 6.0, 1.1), (7.8, 6.3, 0.9), (-7.5, 5.6, 1.2), (12, 5.2, 1.0))):
        add('cube', ('7A5A3A', '8A6844')[i % 2], (x, y, 1.4 + s / 2), rot=(0, 0, i * 0.5), scale=(s, s, s), size=1, parent=r)
    for i in range(3):
        add('cube', ('E8E0D0', 'C8503A')[i % 2], (-3.4 + i * 1.3, 11.2, 4.6), rot=(0.35, 0, 0), scale=(1.3, 3.0, 0.06), size=1, parent=r)
    for x in (-4.0, 0.5):
        add('cylinder', '6E4426', (x, 9.9, 3.0), radius=0.07, depth=3.2, vertices=5, parent=r)
    boat = empty(FAR, r)
    make_boat(boat)
    tgt = empty((0, 0, 0), r)
    light((-60, -80, 110), 3.8, 'FFF0D0', kind='SUN', target=tgt, parent=r)
    return dict(bboat=boat)


def set_ward(r):
    """A hospital ward (a reconstruction): three beds, tall windows, a ceiling fan."""
    room(r, 24, -14, 5.4, 5.0, 'C8C0A8', 'A8C4B0', 'D8DCD0')
    for x in (-8, -2.6, 2.6, 8):
        add('cube', 'FFF4D0', (x, 5.26, 3.0), scale=(2.2, 0.06, 3.0), size=1, parent=r, emit=1.3)
        add('cube', 'E8E8E0', (x, 5.22, 3.0), scale=(0.1, 0.1, 3.0), size=1, parent=r)
        add('cube', 'E8E8E0', (x, 5.22, 3.0), scale=(2.3, 0.1, 0.1), size=1, parent=r)
        add('cube', 'E8E8E0', (x, 5.2, 1.44), scale=(2.6, 0.3, 0.12), size=1, parent=r)
    add('cube', '8AA894', (0, 5.24, 0.9), scale=(24, 0.1, 1.0), size=1, parent=r)
    for i, x in enumerate((-5.4, 0.0, 5.4)):
        add('cube', 'E8E8E0', (x, 3.0, 0.62), scale=(2.3, 4.4, 0.16), size=1, parent=r)
        add('cube', 'F4F4EC', (x, 3.0, 0.86), scale=(2.2, 4.3, 0.34), size=1, parent=r)
        for sx in (-1, 1):
            for y in (0.9, 5.05):
                add('cylinder', 'B8BCB8', (x + sx * 1.1, y, 0.75 if y < 2 else 1.1), radius=0.06, depth=1.5 if y < 2 else 2.2, vertices=6, parent=r)
        add('cube', 'B8BCB8', (x, 5.05, 2.1), scale=(2.3, 0.08, 0.1), size=1, parent=r)
        add('cube', 'B8BCB8', (x, 5.05, 1.5), scale=(2.3, 0.08, 0.1), size=1, parent=r)
        add('cube', 'FFFFFF', (x, 4.45, 1.14), rot=(0.5, 0, 0), scale=(1.6, 0.9, 0.3), size=1, parent=r)
        if i != 1:
            add('cube', ('7AA0C0', '8AB0A0')[i // 2], (x, 2.6, 1.08), scale=(2.26, 3.2, 0.16), size=1, parent=r)
        add('cube', 'D8D4C4', (x + 2.0, 4.6, 0.65), scale=(0.9, 0.9, 1.3), size=1, parent=r)
        add('cylinder', 'A8D0E0', (x + 2.0, 4.6, 1.52), radius=0.16, depth=0.44, vertices=8, parent=r, rough=0.2)
    add('cube', '8A6A48', (2.5, 1.6, 0.72), scale=(0.9, 0.9, 0.1), size=1, parent=r)
    add('cube', '8A6A48', (2.9, 1.6, 1.3), scale=(0.1, 0.9, 1.2), size=1, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cube', '6E5030', (2.5 + sx * 0.38, 1.6 + sy * 0.38, 0.36), scale=(0.08, 0.08, 0.72), size=1, parent=r)
    fan = empty((0, 1.5, 4.7), r)
    add('cylinder', '8A8E88', (0, 0, 0.1), radius=0.07, depth=0.5, vertices=5, parent=fan)
    for i in range(4):
        add('cube', '6E5030', (math.cos(i * PI / 2) * 1.1, math.sin(i * PI / 2) * 1.1, 0), rot=(0.15, 0, i * PI / 2), scale=(2.0, 0.34, 0.04), size=1, parent=fan)
    aim = empty((0, 2.5, 1.6), r)
    light((0, 4.0, 4.2), 260, 'FFF0D0', 6.0, aim, parent=r)
    light((-5, -7, 4.0), 420, 'FFF4E4', 4.0, aim, parent=r)
    light((6, -5, 2.0), 160, '9AC0E0', 4.0, aim, parent=r)
    return dict(fan=fan)


def set_hall(r):
    """Two rooms in New York (reconstructions): a ceremony hall with a low stage, and, far to the right, a recruiting desk."""
    room(r, 26, -14, 7, 7.0, '6A4A32', 'D8D0BC', 'E4DCCC')
    add('cube', '5A3E2A', (0, 4.6, 0.3), scale=(18, 4.8, 0.6), size=1, parent=r)
    add('cube', '8A6A48', (0, 2.18, 0.3), scale=(18, 0.06, 0.6), size=1, parent=r)
    for x in (-9, -3, 3, 9):
        add('cube', 'FFF0C8', (x, 6.86, 4.0), scale=(2.2, 0.06, 4.4), size=1, parent=r, emit=1.2)
        add('cube', '8A6A48', (x, 6.82, 4.0), scale=(0.12, 0.1, 4.4), size=1, parent=r)
    for x in (-12, -6, 0, 6, 12):
        add('cube', 'A83A2E', (x, 6.78, 3.8), scale=(1.5, 0.16, 6.0), size=1, parent=r)
        add('cube', '8E2E24', (x, 6.7, 6.6), scale=(2.2, 0.3, 0.6), size=1, parent=r)
    add('cube', '7A5A36', (4.4, 4.2, 1.25), scale=(1.1, 0.8, 1.3), size=1, parent=r)
    add('cube', '8A6A48', (4.4, 4.1, 1.95), rot=(0.3, 0, 0), scale=(1.3, 0.9, 0.08), size=1, parent=r)
    for row, y in enumerate((-0.6, -2.4)):
        for i in range(9):
            x = -7.2 + i * 1.8
            add('cube', '3A3028', (x, y, 0.72), scale=(1.1, 1.0, 0.1), size=1, parent=r)
            add('cube', '3A3028', (x, y - 0.45, 1.35), scale=(1.1, 0.1, 1.3), size=1, parent=r)
    for x in (-6, 6):
        add('cylinder', 'FFE8B0', (x, 2.0, 6.5), radius=0.6, depth=0.2, vertices=10, parent=r, emit=5)
        light((x, 2.0, 6.0), 300, 'FFE8B0', kind='POINT', parent=r)
    aim = empty((0, 4, 2.6), r)
    light((-6, -8, 5.5), 1100, 'FFE8C8', 5.0, aim, parent=r)
    light((8, -6, 3.0), 400, 'FFB070', 4.0, aim, parent=r)
    # the recruiting desk
    d = empty((60, 0, 0), r)
    room(d, 22, -14, 4.6, 5.0, '5A5A60', '8A9AA8', 'C8CCD0')
    add('cube', '6A4C2E', (1.4, 1.4, 1.2), scale=(1.5, 3.0, 0.12), size=1, parent=d)
    add('cube', '5A4028', (1.4, 1.4, 0.6), scale=(1.3, 2.8, 1.2), size=1, parent=d)
    add('cube', 'F4F0E4', (1.3, 1.2, 1.28), rot=(0, 0, 0.2), scale=(0.6, 0.8, 0.02), size=1, parent=d)
    add('cylinder', '2A2E36', (1.5, 2.3, 1.5), radius=0.08, depth=0.5, vertices=6, parent=d)
    add('cone', '3E6A5A', (1.5, 2.3, 1.85), radius1=0.34, radius2=0.14, depth=0.3, vertices=8, parent=d, emit=0.6)
    add('cube', '3A3028', (3.5, 1.4, 0.75), scale=(1.0, 1.0, 0.1), size=1, parent=d)
    add('cube', '3A3028', (4.0, 1.4, 1.5), scale=(0.1, 1.0, 1.5), size=1, parent=d)
    for i, x in enumerate((6.0, 7.5)):
        add('cube', '4A5660', (x, 3.9, 1.5), scale=(1.3, 1.0, 3.0), size=1, parent=d)
        for z in (0.6, 1.5, 2.4):
            add('cube', 'C89A3A', (x, 3.38, z), scale=(0.5, 0.04, 0.08), size=1, parent=d)
    add('cube', 'E8E4D8', (-3.6, 4.46, 2.6), scale=(1.0, 0.06, 3.6), size=1, parent=d)
    for i in range(9):
        add('cube', '2A2E36', (-3.6 - (0.18 if i % 2 else 0.0), 4.42, 1.0 + i * 0.4), scale=(0.64 if i % 2 == 0 else 0.3, 0.04, 0.03), size=1, parent=d)
    add('cube', 'FFF0C8', (-8, 4.46, 3.0), scale=(2.6, 0.06, 2.6), size=1, parent=d, emit=2.0)
    add('cube', '5A6670', (-8, 4.42, 3.0), scale=(0.1, 0.08, 2.6), size=1, parent=d)
    add('cube', '5A6670', (-8, 4.42, 3.0), scale=(2.6, 0.08, 0.1), size=1, parent=d)
    add('cube', 'D8D0BC', (3.0, 4.46, 3.2), scale=(2.4, 0.06, 1.6), size=1, parent=d)
    for i in range(4):
        add('cube', '6A7480', (3.0, 4.42, 3.7 - i * 0.3), scale=(1.9 - (i % 2) * 0.5, 0.04, 0.08), size=1, parent=d)
    for x in (-7.0, -5.8):
        add('cube', '3A3028', (x, 3.4, 0.72), scale=(1.0, 1.0, 0.1), size=1, parent=d)
        add('cube', '3A3028', (x, 3.9, 1.3), scale=(1.0, 0.1, 1.2), size=1, parent=d)
    aim2 = empty((0, 1.4, 2.0), d)
    light((-4, -8, 4.5), 3000, 'FFF0DC', 5.0, aim2, parent=d)
    light((7, -6, 2.5), 900, '9AB8E0', 4.0, aim2, parent=d)
    light((0, 1.0, 4.6), 500, 'FFF0DC', kind='POINT', parent=d)
    return {}


def set_stoop(r):
    """A street in Brooklyn at dusk (a reconstruction): brownstone fronts, a stoop, a street lamp, a tree."""
    add('plane', '2A2C34', (0, 0, 0), size=600, parent=r)
    add('cube', '6A6A70', (0, 2.6, 0.1), scale=(160, 6.8, 0.2), size=1, parent=r)
    add('cube', '8A8A90', (0, -0.9, 0.12), scale=(160, 0.3, 0.26), size=1, parent=r)
    cols = ('6A3A2E', '7A4634', '5A3228', '74402E')
    for i in range(13):
        x = -48 + i * 8.0
        hgt = 12 + (i % 3) * 1.5
        add('cube', cols[i % 4], (x, 10, hgt / 2), scale=(7.8, 8, hgt), size=1, parent=r)
        add('cube', '3A2420', (x, 5.9, hgt + 0.2), scale=(8.0, 0.6, 0.6), size=1, parent=r)
        for j in range(2):
            for z in (5.4, 9.0):
                lit = (i * 3 + j + int(z)) % 3 != 0
                add('cube', 'FFC870' if lit else '1A1E2A', (x + 0.4 + j * 2.4, 5.96, z), scale=(1.3, 0.1, 2.2), size=1, parent=r, emit=3.0 if lit else 0.0)
        add('cube', 'FFC870' if i % 2 else '1A1E2A', (x + 1.6, 5.96, 2.2), scale=(2.6, 0.1, 2.0), size=1, parent=r, emit=2.2 if i % 2 else 0.0)
        add('cube', '2A1A16', (x - 2.2, 5.96, 2.6), scale=(1.5, 0.1, 3.2), size=1, parent=r)
        for s in range(4):
            add('cube', '8A7868', (x - 2.2, 5.5 - s * 0.55, 0.95 - s * 0.25), scale=(2.4, 0.56, 0.26), size=1, parent=r)
        for sx in (-1, 1):
            add('cube', '1A1A20', (x - 2.2 + sx * 1.25, 4.7, 1.3), rot=(0.42, 0, 0), scale=(0.08, 2.4, 0.08), size=1, parent=r)
    add('cylinder', '1A1A20', (4.4, 0.2, 3.2), radius=0.1, depth=6.0, vertices=6, parent=r)
    add('ico_sphere', 'FFD08A', (4.4, 0.2, 6.4), radius=0.36, subdivisions=1, parent=r, emit=10)
    light((4.4, 0.0, 5.8), 1500, 'FFB060', kind='POINT', parent=r)
    add('cylinder', 'B8442E', (-5.4, 0.4, 0.6), radius=0.24, depth=0.9, vertices=8, parent=r)
    add('ico_sphere', 'B8442E', (-5.4, 0.4, 1.1), radius=0.26, subdivisions=1, parent=r)
    for x, c in ((-9.5, 'C87A3A'), (11.5, 'B8642E')):
        add('cylinder', '3A2A20', (x, 0.6, 2.6), radius=0.2, depth=5.0, vertices=6, parent=r)
        for j in range(3):
            add('ico_sphere', c, (x + (j - 1) * 1.3, 0.6 + (j % 2) * 0.6, 6.0 + (j % 2) * 1.0), radius=1.9, subdivisions=1, parent=r)
    add('circle', 'F2E8D0', (-30, 300, 70), rot=(PI / 2, 0, 0), radius=12, vertices=20, fill_type='NGON', parent=r, emit=4)
    aim = empty((-2, 4.5, 2.4), r)
    light((-8, -8, 6), 3200, 'FFD8B0', 4.0, aim, parent=r)
    light((-12, 6, 5), 2400, 'FF7A1A', 3.0, aim, parent=r)
    light((7, -6, 2.5), 700, '6E8FD8', 4.0, aim, parent=r)
    return {}


def make_hook2():
    """The bigger hook he bent from a nail out of the raft's boards."""
    h_ = empty(FAR)
    kw = dict(parent=h_, rough=0.35, emit=0.25)
    add('cylinder', '9AA0A8', (0, 0, 0.2), radius=0.035, depth=0.5, vertices=5, **kw)
    add('cylinder', '9AA0A8', (0.11, 0, -0.04), rot=(0, PI / 2, 0), radius=0.035, depth=0.26, vertices=5, **kw)
    add('cylinder', '9AA0A8', (0.22, 0, 0.06), radius=0.035, depth=0.22, vertices=5, **kw)
    add('cone', '9AA0A8', (0.22, 0, 0.22), radius1=0.06, radius2=0.0, depth=0.14, vertices=4, **kw)
    add('cylinder', '6A7078', (0, 0, 0.47), radius=0.08, depth=0.04, vertices=6, **kw)
    return h_


def extend(S):
    for name, fn in (('mess', set_mess), ('quay', set_quay), ('belem', set_belem), ('ward', set_ward), ('hall', set_hall), ('stoop', set_stoop)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['ex'] = [K.Rig(c, K.human_head(*hd)) for c, hd in zip(EXTRAS, EXHEAD)]
    add('cylinder', 'F0F0E8', (0, 0, 0.36), radius=0.3, depth=0.14, vertices=8, parent=S['ex'][1].head)        # a nurse's cap / a cook's cap
    S['old'] = K.Rig(OLD, K.human_head(SKIN, 'C8C8C4'))
    S['hand_o'] = K.Hand('E0B090', '2A3040', 1.0)
    S['raft2'] = empty(FAR)
    make_raft(S['raft2'])
    S['hook2'] = make_hook2()
    S['nail'] = add('cylinder', '9AA0A8', FAR, radius=0.04, depth=0.7, vertices=5, rough=0.35, emit=0.25)
    add('cylinder', '6A7078', (0, 0, 0.36), radius=0.09, depth=0.04, vertices=6, parent=S['nail'])
    S['cord'] = empty(FAR)
    add('cylinder', 'C9B48A', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.045, depth=3.6, vertices=5, parent=S['cord'])
    S['knots'] = [add('ico_sphere', 'E4D2A6', (-1.5 + i * 0.33, 0, 0), radius=0.1, subdivisions=1, parent=S['cord']) for i in range(10)]
    S['bisc'] = [add('cube', 'E0C080', FAR, scale=(0.3, 0.3, 0.06), size=1) for _ in range(2)]
    S['nest'] = empty(FAR)
    add('torus', '3E5A34', (0, 0, 0.08), major_radius=0.42, minor_radius=0.14, major_segments=9, minor_segments=4, parent=S['nest'])
    for i in range(6):
        add('cone', ('4E6A3A', '2E4A2C')[i % 2], (math.cos(i * 1.05) * 0.5, math.sin(i * 1.05) * 0.5, 0.1), rot=(math.sin(i * 1.05) * 1.3, -math.cos(i * 1.05) * 1.3, 0),
            radius1=0.1, radius2=0.0, depth=0.5, vertices=4, parent=S['nest'])
    S['jug'] = empty(FAR)
    add('cylinder', 'A8B0B8', (0, 0, 0.36), radius=0.32, depth=0.72, vertices=8, parent=S['jug'], rough=0.35)
    add('cylinder', '6A7078', (0, 0, 0.76), radius=0.1, depth=0.1, vertices=6, parent=S['jug'])
    add('torus', '6A7078', (0, 0, 0.5), rot=(0, PI / 2, 0), major_radius=0.36, minor_radius=0.03, major_segments=8, minor_segments=4, parent=S['jug'])
    S['fins'] = [add('cone', '5E6C7A', FAR, scale=(1, 0.14, 1), radius1=0.32, radius2=0.0, depth=0.7, vertices=4) for _ in range(3)]
    S['buoy'] = empty(FAR)
    add('cylinder', 'FF7A1A', (0, 0, 0.3), radius=0.5, depth=0.7, vertices=8, parent=S['buoy'], emit=0.5)
    add('cylinder', 'F4F4F0', (0, 0, 0.72), radius=0.5, depth=0.16, vertices=8, parent=S['buoy'])
    add('cylinder', '2A2E36', (0, 0, 1.6), radius=0.03, depth=1.7, vertices=4, parent=S['buoy'])
    add('cube', 'FF7A1A', (0.3, 0, 2.2), scale=(0.6, 0.02, 0.4), size=1, parent=S['buoy'], emit=0.8)
    S['dye'] = add('cylinder', 'FFC233', FAR, radius=1.0, depth=0.03, vertices=10, emit=0.9)
    S['shirt'] = add('cube', 'F0E8D0', FAR, scale=(0.75, 0.04, 0.6), size=1, emit=0.2)
    S['wraps'] = [add('cube', 'CDB98C', FAR, scale=(0.3, 0.3, 0.3), size=1) for _ in range(2)]
    S['cover'] = add('cone', 'D8C48C', FAR, rot=(PI, 0, 0), radius1=0.55, radius2=0.12, depth=0.26, vertices=7)
    S['line2'] = add('cylinder', 'E8E0C8', FAR, radius=0.03, depth=1.0, vertices=4, emit=0.4)
    S['tray'] = empty(FAR)
    add('cube', 'B8BCC0', (0, 0, 0), scale=(0.9, 0.6, 0.04), size=1, parent=S['tray'], rough=0.3)
    for i in range(3):
        add('cylinder', ('E8E0D0', 'D8B048')[i % 2], (-0.25 + i * 0.25, 0, 0.1), radius=0.08, depth=0.16, vertices=7, parent=S['tray'])
    S['mop'] = empty(FAR)
    add('cylinder', '8A6A48', (0, 0, 1.2), radius=0.04, depth=2.4, vertices=5, parent=S['mop'])
    add('cube', 'C8C4B0', (0, 0, 0.06), scale=(0.7, 0.24, 0.12), size=1, parent=S['mop'])
    S['bucket'] = add('cylinder', '6A7078', FAR, radius=0.3, depth=0.5, vertices=8)
    S['medal'] = empty(FAR)
    add('cube', 'B02A2A', (0, 0, 0.16), scale=(0.13, 0.02, 0.26), size=1, parent=S['medal'])
    add('cylinder', 'D8D8E0', (0, 0, -0.05), rot=(PI / 2, 0, 0), radius=0.11, depth=0.03, vertices=10, parent=S['medal'], rough=0.2, emit=0.8)
    S['watch'] = empty(FAR)
    add('torus', 'FFC233', (0, 0, 0), major_radius=0.13, minor_radius=0.035, major_segments=10, minor_segments=4, parent=S['watch'], rough=0.2, emit=0.7)
    add('cylinder', 'FFF6D8', (0, 0, 0), radius=0.11, depth=0.03, vertices=10, parent=S['watch'], emit=0.9)
    for s in (-1, 1):
        add('cube', '6A4426', (0, s * 0.26, 0), scale=(0.11, 0.3, 0.025), size=1, parent=S['watch'])
    S['bowl'] = add('cone', 'E8E0D0', FAR, rot=(PI, 0, 0), radius1=0.24, radius2=0.1, depth=0.16, vertices=8)
    S['clip'] = add('cube', '8A6A48', FAR, scale=(0.36, 0.03, 0.5), size=1)
    S['blanket'] = add('cube', '7AA0C0', FAR, scale=(2.26, 2.9, 0.42), size=1)
    S['paper'] = add('cube', 'F4F0E4', FAR, scale=(0.5, 0.02, 0.66), size=1, emit=0.3)


_build0, _reset0 = build, reset


def build():
    S = _build0()
    extend(S)
    return S


def reset(S):
    _reset0(S)
    for rig in S['ex'] + [S['old']]:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
    S['hand_o'].root.parent = None
    S['hand_o'].root.scale = (1, 1, 1)
    S['hand_o'].place(FAR)
    S['hand_o'].grip(0.2)
    for o in [S['raft2'], S['hook2'], S['nail'], S['cord'], S['nest'], S['jug'], S['buoy'], S['dye'], S['shirt'], S['cover'], S['line2'], S['tray'], S['mop'],
              S['bucket'], S['medal'], S['watch'], S['bowl'], S['clip'], S['blanket'], S['paper']] + S['bisc'] + S['fins'] + S['wraps']:
        o.parent = None
        o.location, o.rotation_euler = FAR, (0, 0, 0)
    for o in (S['hook2'], S['nail'], S['cord'], S['nest'], S['jug'], S['buoy'], S['tray'], S['mop'], S['bucket'], S['medal'], S['watch'], S['bowl'], S['raft2'],
              S['bboat']):
        o.scale = (1, 1, 1)
    S['bboat'].location, S['bboat'].rotation_euler = FAR, (0, 0, 0)
    S['cover'].rotation_euler = (PI, 0, 0)
    S['cover'].scale = (1, 1, 1)
    S['bowl'].rotation_euler = (PI, 0, 0)
    S['dye'].scale = (1, 1, 1)
    S['shirt'].scale = (0.75, 0.04, 0.6)
    S['line2'].scale = (1, 1, 1)
    S['blanket'].scale = (2.26, 2.9, 0.42)
    S['paper'].scale = (0.5, 0.02, 0.66)
    S['clip'].scale = (0.36, 0.03, 0.5)
    for o in S['bisc']:
        o.scale = (0.3, 0.3, 0.06)
    for o in S['fins']:
        o.scale = (1, 0.14, 1)
    for o in S['wraps']:
        o.scale = (0.3, 0.3, 0.3)
    for o in S['knots']:
        o.hide_render = False
    S['qship'].location, S['qship'].rotation_euler = (0, 9, 0.3), (0, 0, 0)
    S['fan'].rotation_euler = (0, 0, 0)
    S['face']['ex'] = 'calm'


def inside(S, name, col='0A0E14', fill=0.0):
    A = show(S, name)
    sky(S, col, 1.0)
    S['fillk'] = fill
    return A


def seat(rig, loc, yaw, **over):
    """Sit a character on a bench or chair whose top is at loc[2]."""
    rig.place((loc[0], loc[1], loc[2] - 0.55), yaw)
    rig.apply(P('sit', **over))


# ---------------------------------------------------------------- long shots: before the raft
def cabin_boy(S, k, t, lt):
    """At sixteen, a cabin boy on a British ship. prm quit: he puts the mop down and walks out."""
    A = inside(S, 'mess')
    quit_ = S['prm'].get('quit')
    b = S['poon']
    b.root.scale = (0.84, 0.84, 0.84)
    seat(S['ex'][0], A(3.2, 3.5, 0.75), 0.0, aL=(0.9, 0.1, 1.2), aR=(1.3, 0.2, 0.3) if not quit_ else (0.9, 0.1, 1.2), head=(0.1, 0.5 if not quit_ else lerp(0.3, -0.9, k)))
    seat(S['ex'][2], A(0.2, 3.5, 0.75), 0.0, aL=(0.9, 0.1, 1.3), aR=(1.0, 0.1, 1.4), head=(0.2, -0.3))
    S['bucket'].location = A(-3.6, 0.2, 0.25)
    if not quit_:
        sw = math.sin(t * 5)
        b.place(A(-2.2 + 0.25 * sw, -0.4, 0), 0.5)
        b.apply(P('stand', aL=(1.0 + 0.2 * sw, 0.1, 0.5), aR=(1.1 - 0.2 * sw, 0.0, 0.6), lean=0.4, head=(0.3, 0.0), lL=(0.3, 0.4), lR=(-0.2, 0.3)))
        S['face']['poon'] = 'tired'
        S['mop'].location = A(-1.95 + 0.5 * sw, -1.45, 0.0)
        S['mop'].rotation_euler = (-0.5, 0.0, 0.5)
        S['rook'].place(A(6.6, 0.3, 0), -0.7)
        S['rook'].apply(P('cross', head=(0.1, 0.25 + 0.15 * math.sin(t * 1.5))))
        S['face']['rook'] = 'deadpan'
        cam(S, A(lerp(1.2, 0.4, k), lerp(-9.5, -8.6, k), 2.9), A(1.2, 1.6, 1.9), 30, 0.015 * math.sin(t * 1.1))
    else:
        u = ease(k * 1.2)
        S['mop'].location = A(-2.0, -1.2, 0.08)
        S['mop'].rotation_euler = (-PI / 2 + 0.05, 0, 0.9)
        b.place(A(lerp(-1.6, 7.6, u), lerp(-0.4, 0.3, u), 0), PI / 2 + 0.1)
        b.apply(walk(t, 1.7))
        S['face']['poon'] = 'calm'
        S['rook'].place(A(5.0, -1.6, 0), lerp(-0.9, 0.9, u))
        S['rook'].apply(blend(P('cross'), P('hat', head=(0.1, 0.0)), ease((k - 0.4) * 3)))
        S['hat_tip'] = 0.5 * ease((k - 0.4) * 3)
        S['face']['rook'] = 'smirk'
        cam(S, A(lerp(0.5, 2.0, k), lerp(-9.0, -8.4, k), 2.7), A(lerp(1.0, 4.0, k), 1.0, 1.9), 30)


def mess(S, k, t, lt):
    """November 1942: second steward on the Benlomond."""
    A = inside(S, 'mess')
    x = lerp(-5.5, -1.4, k)
    S['poon'].place(A(x, 0.0, 0), PI / 2)
    w = walk(t, 1.3)
    w.update(aL=(1.1, 0.0, 1.0, 0.3), aR=(1.1, 0.0, 1.0, 0.3))
    S['poon'].apply(P('stand', **{kk: w[kk] for kk in ('aL', 'aR', 'lL', 'lR', 'lean', 'lift')}))
    S['face']['poon'] = 'calm'
    on(S, S['tray'], S['poon'].body, (0, -0.72, 0.52))
    seat(S['rook'], A(2.6, 3.5, 0.75), 0.0, aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), head=(0.1, lerp(0.9, 0.4, k)))
    S['face']['rook'] = 'deadpan'
    seat(S['ex'][0], A(0.4, 3.5, 0.75), 0.0, aL=(0.9, 0.1, 1.3), aR=(1.0, 0.1, 1.4), head=(0.25, 0.2))
    seat(S['ex'][3], A(-0.4, 0.9, 0.75), PI, aL=(0.9, 0.1, 1.3), aR=(1.0, 0.1, 1.4), head=(0.2, 0.0))
    seat(S['ex'][2], A(4.0, 0.9, 0.75), PI, aL=(0.9, 0.1, 1.3), aR=(1.0, 0.1, 1.4), head=(0.2, 0.3))
    cam(S, A(lerp(-2.0, -0.6, k), lerp(-9.0, -8.2, k), 2.8), A(0.6, 1.6, 1.9), 30, 0.025 * math.sin(t * 1.2))


def quay_leave(S, k, t, lt):
    """Cape Town, 10 November 1942: the steamer pulls away from the quay."""
    A = show(S, 'quay')
    sky(S, '9CCBEA', 1.0)
    S['fillk'] = 8.0
    S['fill'].data.color = K.hexc('FFF0DC')[:3]
    x = lerp(0, -16, ease(k))
    S['qship'].location = (x, lerp(9, 15, ease(k)), 0.3)
    S['qship'].rotation_euler = (0, 0, lerp(0, -0.12, ease(k)))
    smoke(S, A(x - 2.6, lerp(9, 15, ease(k)), 12.8), t, 9, 22, (1.2, 0.2), 1.8)
    u = ease(lt / 0.6)
    S['rook'].place(A(3.0, -4.6, 1.8), PI - 0.5)
    S['rook'].apply(blend(P('stand', head=(0.0, 0.3)), P('hat', aL=(0.2, 1.9, 1.6, -1.5), head=(0.0, 0.3)), u))
    S['face']['rook'] = 'calm'
    S['ex'][2].place(A(-3.5, -3.0, 1.8), PI + 0.3)
    S['ex'][2].apply(P('hips', head=(-0.1, 0.0)))
    S['ex'][3].place(A(7.5, -2.2, 1.8), PI - 0.2)
    S['ex'][3].apply(P('up', aL=(0.1, 0.2, 0.1), aR=(2.7, 0.4 + 0.3 * math.sin(t * 6), 0.2), head=(-0.15, 0.0)))
    for i, g in enumerate(S['gulls'][:3]):
        g['root'].location = A(-10 + i * 9 + t * 1.2, -2 + i * 3, 9 + i * 2.5 + math.sin(t * 2 + i))
        g['root'].scale = (2.0, 2.0, 2.0)
        flap(g, t + i, 7, 0.6)
    cam(S, A(lerp(9.5, 8.0, k), lerp(-13.5, -12.0, k), lerp(4.2, 4.8, k)), A(lerp(-1, -3, k), 6, 5.5), 30, fill=0.5)


def plank_float(S, k, t, lt):
    """Two hours in the water, holding on to a plank."""
    A = ocean(S, 'night', t, 0.8)
    h0 = wave_h(0, 0, t, 0.8)
    S['poon'].place(A(0, 0.4, h0 - 1.75), 0.15, 0.25, 0.05 * math.sin(t * 2))
    S['poon'].apply(P('stand', aL=(1.5, 0.5, 0.7, 0.6), aR=(1.5, 0.5, 0.7, 0.6), head=(-0.15, 0.2 * math.sin(t * 0.8)), lL=(0.3 * math.sin(t * 3), 0.4), lR=(-0.3 * math.sin(t * 3), 0.4)))
    S['face']['poon'] = 'scared'
    vest(S)
    pk = S['planks'][0]
    pk.location = A(0, -0.25, h0 + 0.12)
    pk.rotation_euler = (0.06 * math.sin(t * 2), 0, 0.1)
    pk.scale = (3.2, 0.5, 0.14)
    h1 = wave_h(3.4, 1.6, t, 0.8)
    S['rook'].place(A(3.4, 1.9, h1 - 1.7), -0.35, 0.2)
    S['rook'].apply(P('stand', aL=(1.5, 0.5, 0.7, 0.6), aR=(1.5, 0.5, 0.7, 0.6), head=(0.05, 0.5)))
    S['face']['rook'] = 'shocked'
    S['hat_tip'] = 0.5
    p2 = S['planks'][1]
    p2.location = A(3.4, 1.3, h1 + 0.12)
    p2.rotation_euler = (0, 0, -0.3)
    p2.scale = (2.4, 0.5, 0.14)
    for i, o in enumerate(S['planks'][2:]):
        px, py = -9 + i * 5.5, 7 + (i % 2) * 6
        o.location = A(px, py, wave_h(px, py, t, 0.8) + 0.06)
        o.rotation_euler = (0, 0, i * 1.3)
    smoke(S, A(-26, 80, 0), t, 6, 34, (0.2, 0), 6)
    S['glow'].location = A(-20, 60, 8)
    S['glow'].data.energy = 60000
    cam(S, A(lerp(3.6, 2.6, k), lerp(-7.4, -6.4, k), 1.5), A(1.5, 0.6, lerp(1.0, 1.3, k)), 40, 0.04 * math.sin(t * 0.9))


def ride2(S, t, x, y, yaw=0.0):
    r = S['rough']
    S['raft2'].location = (x, y, wave_h(x, y, t, r) + 0.12)
    S['raft2'].rotation_euler = (0.04 * math.sin(t * 1.3), 0.04 * math.sin(t * 1.7), yaw)


def other_raft(S, k, t, lt):
    """Another raft with a few men on it. He cannot reach them. prm far: the rafts have drifted apart."""
    far = S['prm'].get('far')
    A = ocean(S, 'night', t, 0.7)
    ride(S, t, 0, 0, 0.25)
    d = lerp(46, 64, k) if far else lerp(15, 19, k)
    ride2(S, t, (-16 - (d - 46) * 0.3) if far else -7.5, d, -0.4)
    wv = math.sin(t * 7)
    for i, m in enumerate(S['ex'][1:]):
        aboard(S, m, (-1.2, 0.2, 1.4)[i], (-1.0, -1.5, -0.8)[i], (0.2, -0.1, 0.1)[i],
               P('up', aL=(2.6, 0.5 + 0.3 * wv, 0.2), aR=(2.6, 0.5 - 0.3 * wv, 0.2)) if not far else P('stand', head=(0.1, 0.0)), on='raft2')
    if far:
        aboard(S, S['poon'], -0.5, 0.2, PI + 0.15, P('stand', aL=(0.1, 0.2, 0.1), aR=(0.1, 0.2, 0.1), head=(0.1, 0.0)))
        aboard(S, S['rook'], 1.2, -0.9, PI - 0.7, P('hat', head=(0.25, 0.0)))
        S['hat_tip'] = 0.5
    else:
        pd = math.sin(t * 6)
        aboard(S, S['poon'], -1.75, -0.9, -0.7 * PI, P('sit', aL=(1.6 + 0.5 * pd, 0.5, 0.4), aR=(1.6 - 0.5 * pd, 0.5, 0.4), lean=0.6, head=(-0.4, 0.0)))
        aboard(S, S['rook'], 1.3, -0.6, PI - 0.5, P('stand', aL=(0.1, 0.3, 0.2), aR=(1.3, 0.3, 0.2), head=(0.0, 0.0)))
        splash(S, A(-2.9, -0.6, 0.3), (lt * 1.5) % 1, 6, 0.9, size=0.6)
    vest(S)
    S['face']['poon'] = 'scared' if not far else 'tired'
    S['face']['rook'] = 'sad'
    S['glow'].location = A(10, 20, 30)
    S['glow'].data.energy = 160000 if not far else 220000
    S['glow'].data.color = K.hexc('A8C0F0')[:3]
    cam(S, A(lerp(-3.6, -2.8, k), lerp(-10.5, -9.5, k), lerp(4.0, 4.4, k)), A(-1.5 if not far else -3.0, 12 if not far else 22, 1.6), 38, fill=1.2)


# ---------------------------------------------------------------- long shots: the raft, one problem at a time
def ration(S, k, t, lt):
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, 0.1)
    u = ease((lt - 0.5) / 0.4)
    aboard(S, S['poon'], -1.0, -0.9, 0.35, P('sit', aL=(0.9, 0.15 + 0.2 * u, 1.3, 0.5), aR=(0.9, 0.15 + 0.2 * u, 1.3, 0.5), head=(0.35, 0.0)))
    S['face']['poon'] = 'calm'
    for i, s in enumerate((-1, 1)):
        on(S, S['bisc'][i], S['poon'].hands[i], (-s * 0.06 * (1 - u), -0.12, -0.1), (0.4, 0, 0))
        S['bisc'][i].scale = (0.22, 0.3, 0.06)
    aboard(S, S['rook'], 1.0, -1.0, -0.45, P('sit', aL=(0.6, 0.0, 1.5, 1.0), aR=(1.25, 0.25, 0.25), head=(0.15, 0.35)))
    S['face']['rook'] = 'smirk' if lt < 1.2 else 'deadpan'
    cam(S, A(lerp(0.9, 0.4, k), lerp(-7.6, -6.6, k), lerp(2.3, 2.1, k)), A(0.0, -0.9, 1.75), 42)


def wrist_rope(S, k, t, lt):
    """A rope from his wrist to the raft, in case he falls in."""
    A = ocean(S, 'day', t, 0.7)
    ride(S, t, 0, 0, -0.2)
    aboard(S, S['poon'], -0.9, -1.2, 0.15, P('stand', aL=(0.1, 0.2, 0.1), aR=(0.75, 0.5, 0.5), head=(0.3, -0.3), lean=0.1))
    S['face']['poon'] = 'calm'
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-0.2, -1.5, DECK + 1.55), (2.0, 0.35, DECK + 0.5))
    S['line'].scale = (1.6, 1.6, S['line'].scale[2])
    aboard(S, S['rook'], 1.0, -1.3, -0.2, P('shrug', head=(0.35, 0.3), lL=(0.5 + 0.2 * math.sin(t * 4), 0.6)))
    S['face']['rook'] = 'deadpan'
    on(S, S['line2'], S['raft'], (0, 0, 0))
    span(S['line2'], (0.85, -1.55, DECK + 0.5), (2.0, 0.35, DECK + 0.35))
    cam(S, A(lerp(2.4, 1.6, k), lerp(-8.4, -7.4, k), lerp(2.6, 2.3, k)), A(0.2, -1.0, 1.8), 38)


def knots_cu(S, k, t, lt):
    """Days counted as knots in a cord. Seen from above."""
    A = ocean(S, 'day' if not S['prm'].get('night') else 'night', t, 0.4)
    ride(S, t, 0, 0, 0.0, tilt=0.4)
    R = S['raft']
    z = DECK + 0.6
    on(S, S['cord'], R, (0.0, -1.2, z), (0, 0, 0.06))
    S['cord'].scale = (1.15, 1.6, 1.6)
    n = 4 + int(k * 5.99)
    for i, o in enumerate(S['knots']):
        o.hide_render = i >= n
    kx = (-1.5 + (n - 1) * 0.33) * 1.15
    pull = 0.12 * math.sin(lt * 9)
    on(S, S['hand_p'].root, R, (kx - 0.5 - pull, -1.75, z + 0.25), (0.0, 0.0, 0.6))
    on(S, S['hand_q'].root, R, (kx + 0.6 + pull, -1.7, z + 0.25), (0.0, 0.0, -0.7))
    for hnd in ('hand_p', 'hand_q'):
        S[hnd].grip(0.85)
        S[hnd].root.scale = (1.2, 1.2, 1.2)
    cam(S, A(lerp(-0.3, 0.3, k), lerp(-4.6, -4.2, k), lerp(5.0, 4.6, k)), A(0.0, -1.25, z), 40)


def nail_hook(S, k, t, lt):
    """A nail worked out of the raft's boards and bent into a bigger hook."""
    A = ocean(S, 'day', t, 0.4)
    ride(S, t, 0, 0, 0.0, tilt=0.4)
    R = S['raft']
    u = ease(lt / 0.7)
    bend = ease((lt - 0.9) / 0.3)
    wig = 0.08 * math.sin(lt * 16) * (1 - u)
    on(S, S['hand_p'].root, R, (0.9 + wig, -1.3, DECK + 0.55 + 0.75 * u), (0.9, 0.0, PI / 2))
    S['hand_p'].grip(0.9)
    S['hand_p'].root.scale = (1.3, 1.3, 1.3)
    if bend < 0.05:
        on(S, S['nail'], R, (0.25 + wig, -1.3, DECK + 0.1 + 0.75 * u), (0, 0.05 * math.sin(lt * 16), 0))
        S['nail'].scale = (0.8, 0.8, 0.8)
    else:
        on(S, S['hook2'], R, (0.2, -1.3, DECK + 0.75), (PI / 2 - 0.5, 0, 0.2 * math.sin(t * 5)))
        sc = 2.4 + 0.9 * math.sin(PI * min(1, (lt - 0.9) / 0.4))
        S['hook2'].scale = (sc, sc, sc)
    on(S, S['hook'], R, (-1.1, -1.5, DECK + 0.14), (PI / 2, 0, 0.7))
    S['hook'].scale = (1.6, 1.6, 1.6)
    cam(S, A(lerp(1.9, 1.4, k), lerp(-4.0, -3.7, k), lerp(2.9, 2.7, k)), A(0.2, -1.3, DECK + 0.6), 44)


def big_fish(S, k, t, lt):
    """Small fish as bait for a bigger one."""
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, 0.5)
    u = ease(k * 1.15)
    aboard(S, S['poon'], -0.6, -1.0, -0.3, blend(P('stand', aL=(1.2, 0.1, 0.6), aR=(1.2, 0.1, 0.6), lean=0.35, lL=(0.4, 0.6), lR=(0.1, 0.3)),
                                               P('up', aL=(2.7, 0.3, 0.4), aR=(2.5, 0.2, 0.3), lean=-0.3), u))
    S['face']['poon'] = 'happy'
    f = S['fish'][2]
    fx, fy, fz = lerp(-2.8, -1.4, u), lerp(-5.0, -2.6, u), -0.4 + 3.4 * math.sin(PI * 0.6 * u)
    on(S, f, S['raft'], (fx, fy, fz), (0.3 * math.sin(t * 9), 0.5 * math.sin(t * 20) + 0.6, 0.4))
    f.scale = (3.0, 3.0, 3.0)
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-0.75, -1.45, DECK + lerp(1.7, 3.2, u)), (fx, fy, fz))
    splash(S, A(-2.9, -4.6, 0.2), min(1, lt / 0.7), 12, 2.2, size=1.6)
    aboard(S, S['rook'], 1.5, -1.3, 0.3, P('stand', aR=(1.3, 0.25, 0.3), aL=(0.1, 0.3, 0.2), head=(lerp(0.2, -0.1, u), lerp(-0.3, 0.7, u))))
    on(S, S['fish'][3], S['rook'].hands[1], (0, 0.0, -0.5), (0, PI / 2, 0))
    S['fish'][3].scale = (0.9, 0.9, 0.9)
    S['face']['rook'] = 'shocked' if u > 0.4 else 'smirk'
    cam(S, A(lerp(-3.0, -2.2, k), lerp(-10.6, -9.6, k), lerp(1.8, 2.2, k)), A(-0.2, -1.8, lerp(2.2, 2.6, k)), 34, -0.03)


def hang(S, objs, x0, dx, z, t, sway=0.12):
    for i, o in enumerate(objs):
        on(S, o, S['raft'], (x0 + i * dx, 0.35, z + 0.03 * math.sin(t * 3 + i)), (sway * math.sin(t * 2.5 + i), 0, 0))


def dry_line(S, k, t, lt):
    """Fish cut into strips and hung on a line to dry."""
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, 0.0)
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-2.0, 0.35, 2.3), (2.0, 0.35, 2.3))
    hang(S, S['strips'][:5], -1.7, 0.55, 2.0, t)
    for o in S['strips']:
        o.scale = (0.24, 0.05, 0.56)
    f = S['fish'][1]
    on(S, f, S['raft'], (1.45, 0.35, 1.9), (0, PI / 2, 0.1 * math.sin(t * 2)))
    f.scale = (1.4, 1.4, 1.4)
    u = ease((lt - 0.4) / 0.5)
    aboard(S, S['poon'], -1.0, -0.4, PI - 0.5, P('up', aL=(2.2, 0.3, 0.6), aR=(2.3, 0.2, 0.5), head=(-0.2, 0.0)))
    S['face']['poon'] = 'calm'
    aboard(S, S['rook'], 0.9, -1.1, 0.15, blend(P('stand', aR=(1.5, 0.2, 1.2), head=(0.0, -0.1)), P('stand', aR=(1.2, 0.5, 0.4), aL=(0.9, 0.0, 2.2, 0.9), head=(-0.2, 0.5), lean=-0.15), u))
    on(S, S['strips'][5], S['rook'].hands[1], (0, 0, -0.34), (0, 0, 0))
    S['face']['rook'] = 'deadpan' if u < 0.5 else 'shocked'
    cam(S, A(lerp(1.4, 0.8, k), lerp(-8.2, -7.2, k), lerp(2.4, 2.6, k)), A(0.0, -0.3, 2.2), 38)


def life_cover(S, k, t, lt):
    """Rain caught in the canvas cover of his life jacket."""
    A = ocean(S, 'storm', t, 0.8)
    ride(S, t, 0, 0, -0.3)
    u = ease((lt - 0.8) / 0.6)
    aboard(S, S['poon'], -0.5, -0.9, -0.5, P('sit', aL=(lerp(1.0, 1.5, u), 0.0, lerp(1.0, 1.9, u), 0.7), aR=(lerp(1.0, 1.5, u), 0.0, lerp(1.0, 1.9, u), 0.7), head=(lerp(0.3, -0.25, u), 0.0), lean=0.1))
    S['face']['poon'] = 'happy'
    on(S, S['cover'], S['poon'].body, (0, lerp(-0.72, -0.5, u), lerp(0.45, 1.0, u)), (PI + 0.6 * u, 0, 0))
    S['cover'].scale = (0.85, 0.85, 0.85)
    aboard(S, S['rook'], 1.2, -0.7, 0.5, P('stand', aR=(1.9, 0.3, 0.9), aL=(0.1, 0.3, 0.2), head=(-0.35 + 0.5 * ease((lt - 1.2) / 0.3), 0.2)))
    on(S, S['tin'], S['rook'].hands[1], (0, 0, -0.26), (PI, 0, 0))
    S['tin'].scale = (1.3, 1.3, 1.3)
    S['face']['rook'] = 'laugh' if lt < 1.2 else 'deadpan'
    for o in S['tins']:
        o.hide_render = True
    cam(S, A(lerp(-3.6, -3.0, k), lerp(-7.2, -6.4, k), lerp(1.9, 2.2, k)), A(0.3, -0.8, 1.9), 38)


def nest_trap(S, k, t, lt):
    """By one account: a nest of seaweed, a fish for bait, and a wait."""
    A = ocean(S, 'day', t, 0.5)
    ride(S, t, 0, 0, 0.25)
    on(S, S['nest'], S['raft'], (1.5, -1.6, DECK + 0.02))
    S['nest'].scale = (1.3, 1.3, 1.3)
    on(S, S['fish'][4], S['raft'], (1.5, -1.6, DECK + 0.3), (PI / 2, 0, 0.6))
    S['fish'][4].scale = (0.9, 0.9, 0.9)
    u = ease(k * 1.3)
    g = S['gulls'][0]
    on(S, g['root'], S['raft'], (lerp(5.5, 1.5, u), lerp(-4.5, -1.6, u), DECK + lerp(4.0, 0.62, u)), (0, 0, PI - 0.5))
    g['root'].scale = (1.5, 1.5, 1.5)
    flap(g, t, 13, 0.9 * (1 - u) + 0.05, fold=u > 0.97)
    aboard(S, S['poon'], -1.25, 0.1, -1.0, P('sit', aL=(1.0, 0.3, 0.9), aR=(1.0, 0.3, 0.9), lean=0.5, head=(0.0, 0.0), lift=-0.6))
    S['face']['poon'] = 'calm'
    aboard(S, S['rook'], 0.1, -0.7, 0.25, P('cross', head=(0.05, lerp(-0.6, 0.0, ease((k - 0.5) * 3)))))
    S['face']['rook'] = 'deadpan'
    for i, gg in enumerate(S['gulls'][1:3]):
        gg['root'].location = A(-8 + i * 9 + t * 1.5, 24 + i * 8, 8 + i * 2 + math.sin(t * 2 + i))
        gg['root'].scale = (2.5, 2.5, 2.5)
        flap(gg, t + i, 7, 0.6)
    cam(S, A(lerp(4.6, 3.8, k), lerp(-7.6, -6.8, k), lerp(2.7, 2.4, k)), A(0.3, -0.9, 1.6), 36)


def storm_after(S, k, t, lt):
    """After the storm: the fish spoiled, the water fouled."""
    A = ocean(S, 'storm', t, 1.1)
    ride(S, t, 0, 0, 0.3, tilt=1.2)
    for o in S['tins']:
        o.hide_render = True
    on(S, S['tin'], S['raft'], (0.6, -1.5, DECK + 0.2), (PI / 2, 0, 0.5 + 0.3 * math.sin(t * 1.5)))
    S['tin'].scale = (1.4, 1.4, 1.4)
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-2.0, 0.35, 2.3), (-0.6, -0.8, DECK + 0.05))
    on(S, S['strips'][0], S['raft'], (-0.3, -1.3, DECK + 0.05), (PI / 2, 0, 0.4))
    S['strips'][0].scale = (0.24, 0.05, 0.56)
    aboard(S, S['poon'], -1.0, -0.5, 0.3, P('sit', head=(0.55, 0.0), aL=(0.7, 0.1, 1.2, 0.6), aR=(0.7, 0.1, 1.2, 0.6), lean=0.4))
    S['face']['poon'] = 'tired'
    aboard(S, S['rook'], 1.1, -0.9, -0.3, P('stand', aL=(1.0, 0.3, 1.5, 0.7), aR=(1.0, 0.3, 1.5, 0.7), head=(0.3, 0.25), lean=0.15))
    S['face']['rook'] = 'sad'
    S['hat_tip'] = 0.3
    for i in range(4):
        d = S['drops'][i]
        u = (t * 1.6 + i * 0.25) % 1
        on(S, d, S['raft'], (1.1 + (i - 1.5) * 0.12, -1.35, DECK + 1.9 - 1.8 * u))
        d.scale = (0.6, 0.6, 1.2)
    cam(S, A(lerp(-3.2, -2.4, k), lerp(-8.2, -7.4, k), lerp(2.8, 2.4, k)), A(0.1, -0.7, 1.6), 38, 0.05 * math.sin(t * 1.4))


def shark_haul(S, k, t, lt):
    """The line braided double, his hands wrapped in canvas."""
    A = ocean(S, 'noon', t, 0.6)
    ride(S, t, 0, 0, 0.0, tilt=1.3)
    tug = math.sin(t * 7)
    aboard(S, S['poon'], -0.3, -1.4, 0.0, P('stand', aL=(1.2, 0.0, 0.7 + 0.2 * tug, 0.4), aR=(1.2, 0.0, 0.7 + 0.2 * tug, 0.4), lean=-0.35 - 0.08 * tug, lL=(0.6, 0.5), lR=(0.3, 0.3), head=(0.15, 0.0)))
    S['face']['poon'] = 'scared'
    for i in range(2):
        on(S, S['wraps'][i], S['poon'].hands[i], (0, 0, 0))
    sx, sy = -0.6 + 0.8 * math.sin(t * 2.2), -5.2 + 0.5 * tug
    S['shark'].location = A(sx, sy, wave_h(sx, sy, t, 0.6) + 0.1)
    S['shark'].rotation_euler = (0.5 * math.sin(t * 9), 0.2 * tug, PI / 2 + 0.6 * math.sin(t * 5))
    S['shark'].scale = (0.55, 0.55, 0.55)
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-0.3, -2.1, DECK + 1.75), (sx, sy + 0.6, 0.0))
    S['line'].scale = (2.2, 2.2, S['line'].scale[2])
    splash(S, A(sx, sy, 0.3), (lt * 1.7) % 1, 14, 2.4, size=1.5)
    aboard(S, S['rook'], -0.5, 0.1, -0.2, P('stand', aL=(1.3, 0.1, 0.5), aR=(1.3, 0.1, 0.5), lean=-0.4 - 0.08 * tug, lL=(0.6, 0.5), lR=(0.3, 0.3), head=(0.1, -0.6)))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(7.0, 6.0, k), lerp(-4.4, -3.6, k), lerp(2.3, 2.7, k)), A(-0.3, -2.2, 1.6), 34, 0.04 * tug)


def shark_fight(S, k, t, lt):
    """It fights him on the deck. He wins, with the water jug. (No blood is shown.)"""
    A = ocean(S, 'noon', t, 0.6)
    ride(S, t, 0, 0, 0.2, tilt=1.4)
    th = math.sin(t * 11) * (1 - 0.6 * ease((k - 0.7) / 0.3))
    on(S, S['shark'], S['raft'], (0.3 + 0.2 * th, -1.35, DECK + 0.32 + 0.12 * abs(th)), (0.35 * th, 0, 0.5 * th + 0.1))
    S['shark'].scale = (0.55, 0.55, 0.55)
    sw = 0.5 + 0.5 * math.sin(t * 6.5)
    aboard(S, S['poon'], -1.3, -0.5, -0.6, P('up', aL=(2.9 - 1.6 * sw, 0.2, 0.3 + 0.4 * sw), aR=(2.9 - 1.6 * sw, 0.2, 0.3 + 0.4 * sw), lean=0.1 + 0.3 * sw, head=(0.2, 0.0), lL=(0.4, 0.5), lR=(-0.1, 0.2)))
    S['face']['poon'] = 'scared'
    on(S, S['jug'], S['poon'].hands[1], (-0.45, 0, -0.1), (PI, 0, 0))
    S['jug'].scale = (1.15, 1.15, 1.15)
    aboard(S, S['rook'], 1.75, 0.2, 0.5, P('up', aL=(1.9, 0.6, 1.4, 0.8), aR=(1.9, 0.6, 1.4, 0.8), lL=(1.2, 1.7), lR=(0.9, 1.5), head=(0.25, -0.5)), z=DECK + 0.9 + 0.08 * abs(th))
    S['face']['rook'] = 'shocked'
    feathers(S, A(1.6, -0.4, 3.4), min(1, (lt % 1.6) / 1.2), 5)
    splash(S, A(0.3, -1.6, 1.0), (lt * 1.5) % 1, 10, 1.4, size=0.7)
    cam(S, A(lerp(1.6, 0.8, k), lerp(-9.6, -8.6, k), lerp(3.8, 3.3, k)), A(0.1, -0.6, 2.2), 36, 0.05 * th)


def fins_dry(S, k, t, lt):
    """The fins dried in the sun."""
    A = ocean(S, 'noon', t, 0.4)
    ride(S, t, 0, 0, 0.0)
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-2.0, 0.35, 2.3), (2.0, 0.35, 2.3))
    poke = max(0.0, math.sin((lt - 0.7) * 5)) if lt > 0.7 else 0.0
    for i, o in enumerate(S['fins']):
        on(S, o, S['raft'], (-0.5 + i * 0.6, 0.35, 2.0), ((0.5 * poke if i == 2 else 0.0) + 0.08 * math.sin(t * 2 + i), 0, 0))
        o.scale = (0.85, 0.14, 0.85)
    hang(S, S['strips'][:2], -1.7, 0.45, 2.0, t)
    for o in S['strips'][:2]:
        o.scale = (0.24, 0.05, 0.56)
    aboard(S, S['poon'], -1.2, -0.7, 0.4, P('sit', head=(0.1, -0.2), aL=(0.7, 0.0, 1.4, 0.9), aR=(0.7, 0.0, 1.4, 0.9)))
    S['face']['poon'] = 'calm'
    aboard(S, S['rook'], 1.7, 0.1, -PI / 2 + 0.5, P('point', aR=(1.9, 0.2 + 0.1 * poke, 0.3), aL=(0.2, 0.3, 0.3), head=(-0.1, 0.9 * ease((lt - 1.6) / 0.4))))
    S['face']['rook'] = 'smirk'
    S['sundisc'].location = (60, 620, 300)
    cam(S, A(lerp(-1.0, -0.2, k), lerp(-7.8, -7.0, k), lerp(2.2, 2.5, k)), A(0.1, -0.2, 2.15), 40)


def swim_round(S, k, t, lt):
    """Twice a day, when the sea is calm, round the raft."""
    A = ocean(S, 'day', t, 0.3)
    ride(S, t, 0, 0, 0.3)
    a = -1.2 + lt * 0.75
    px, py = math.cos(a) * 4.6, math.sin(a) * 4.6
    kick = math.sin(t * 8)
    S['poon'].place(A(px, py, wave_h(px, py, t, 0.3) - 0.62), a + PI, 1.25, 0.1 * kick)
    S['poon'].apply(P('swim', aL=(2.7 + 0.6 * kick, 0.35, 0.3), aR=(2.7 - 0.6 * kick, 0.35, 0.3), lL=(0.3 * kick, 0.3), lR=(-0.3 * kick, 0.3), head=(-1.0, 0.0)))
    splash(S, A(px, py, 0.2), (lt * 1.8) % 1, 6, 0.9, size=0.7)
    S['line'].parent = None
    span(S['line'], A(px, py, 0.1), A(0.6, 0.1, DECK + 0.2))
    aboard(S, S['rook'], 0.0, -0.4, a + PI / 2, P('point', aR=(1.4, 0.1, 0.1), aL=(0.2, 0.9, 1.4), head=(0.2, 0.0)))
    S['face']['rook'] = 'smirk'
    cam(S, A(lerp(6.5, 5.5, k), lerp(-10.0, -9.0, k), lerp(7.0, 6.2, k)), A(0.0, -0.6, 0.4), 34)


def moon_count(S, k, t, lt):
    """He stops tying knots, and counts full moons instead."""
    A = ocean(S, 'night', t, 0.4)
    ride(S, t, 0, 0, 0.15, tilt=0.6)
    S['moon'].location = (-60, 560, 120)
    S['moon'].scale = (2.2, 2.2, 2.2)
    aboard(S, S['poon'], -1.1, -0.6, PI - 0.25, P('sit', head=(-0.45, 0.0), aL=(0.3, 0.6, 0.3), aR=(0.3, 0.6, 0.3), lean=-0.25))
    S['face']['poon'] = 'calm'
    c = int(lt * 1.6) % 4
    aboard(S, S['rook'], 0.9, -0.9, PI + 0.5, P('sit', aR=(1.7, 0.4, 1.3 - 0.25 * c), aL=(0.6, 0.0, 1.5, 1.0), head=(-0.3, -0.6 + 1.0 * ease((lt - 1.4) / 0.5))))
    S['face']['rook'] = 'calm'
    on(S, S['cord'], S['raft'], (0.2, -1.8, DECK + 0.08), (0, 0, 0.5))
    S['glow'].location = A(-6, 14, 16)
    S['glow'].data.energy = 26000
    S['glow'].data.color = K.hexc('C8D8FF')[:3]
    cam(S, A(lerp(1.8, 1.2, k), lerp(-10.0, -9.2, k), lerp(3.6, 3.8, k)), A(-0.6, 8, lerp(3.3, 3.6, k)), 40, fill=1.3)


# ---------------------------------------------------------------- long shots: seen, and left
def frt_close(S, k, t, lt):
    """A freighter close enough to hear him. prm away: it sails on."""
    away = S['prm'].get('away')
    A = ocean(S, 'dusk', t, 0.6)
    ride(S, t, 0, 0, 0.25)
    x = lerp(-58, -96, k) if away else lerp(34, 2, k)
    S['frt'].location = A(x, 34, 0.1 * math.sin(t))
    S['frt'].rotation_euler = (0, 0, PI)
    smoke(S, A(x + 2.6, 34, 12.6), t, 9, 24, (1.3, 0.1), 1.9)
    for i, m in enumerate(S['ex'][1:]):
        m.root.parent = S['frt']
        m.place(((-6, -1, 5)[i], 3.25, 3.78), PI - 0.2 + i * 0.2)
        m.apply(P('stand', aL=(0.9, 0.2, 0.9), aR=(0.9, 0.2, 0.9), head=(0.2, lerp(0.0, 1.0, ease((k - 0.45) * 3)) if not away else 1.2)))
    w = math.sin(t * 10)
    if away:
        aboard(S, S['poon'], -0.5, 0.3, PI + 0.4, P('stand', aL=(0.1, 0.2, 0.1), aR=(0.1, 0.2, 0.1), head=(0.15, 0.0), lean=0.1))
        aboard(S, S['rook'], 1.1, -0.6, PI + 0.8, P('hat', head=(0.25, 0.0)))
        S['hat_tip'] = 0.5
        S['face']['rook'] = 'sad'
        S['face']['poon'] = 'tired'
    else:
        aboard(S, S['poon'], -0.6, 0.6, PI + 0.1, P('up', aL=(2.0, 0.55, 2.0), aR=(2.0, 0.55, 2.0), head=(-0.3, 0.0), lift=0.1 * abs(w)))
        aboard(S, S['rook'], 1.1, -0.2, PI - 0.15, P('up', aL=(2.7, 0.5 + 0.35 * w, 0.2), aR=(2.7, 0.5 - 0.35 * w, 0.2), head=(-0.25, 0.0), lift=0.15 * abs(w)))
        S['face']['rook'] = 'shocked'
        S['face']['poon'] = 'scared'
    cam(S, A(lerp(3.4, 2.4, k), lerp(-9.6, -8.8, k), lerp(2.4, 2.8, k)), A(-2 if not away else -8, 16, 4.6), 32, fill=0.9)


def marker_drop(S, k, t, lt):
    """A patrol plane drops a marker buoy beside him."""
    A = ocean(S, 'day', t, 0.6)
    ride(S, t, 0, 0, 0.2)
    S['plane'].location = A(lerp(-40, 70, k), lerp(34, 60, k), lerp(17, 30, k))
    S['plane'].rotation_euler = (-0.3, -0.1, 0.25)
    S['plane'].scale = (1.3, 1.3, 1.3)
    for p in S['props']:
        p.rotation_euler = (t * 40, 0, 0)
    u = min(1.0, lt / 0.9)
    bx, by = 5.2, -2.6
    hz = wave_h(bx, by, t, 0.6)
    S['buoy'].location = A(bx - 3 * (1 - u), by, lerp(14, hz, u * u))
    S['buoy'].rotation_euler = (0.15 * math.sin(t * 2), 0.2 * math.sin(t * 2.6) + 1.2 * (1 - u), 0)
    S['buoy'].scale = (1.4, 1.4, 1.4)
    if u >= 1:
        v = min(1.0, (lt - 0.9) / 1.5)
        splash(S, A(bx, by, 0.3), min(1.0, (lt - 0.9) / 0.6), 12, 2.6, size=1.6)
        S['dye'].location = A(bx, by, hz + 0.1)
        S['dye'].scale = (1 + 2.5 * v, 1 + 1.8 * v, 1)
    w = math.sin(t * 9)
    aboard(S, S['poon'], -0.9, 0.2, PI - 0.5, P('up', aL=(2.7, 0.6 + 0.3 * w, 0.2), aR=(2.7, 0.6 - 0.3 * w, 0.2), head=(-0.4, 0.0), lift=0.12 * abs(w)))
    S['face']['poon'] = 'happy'
    aboard(S, S['rook'], 0.9, -0.9, 0.9, P('point', aR=(1.2, 0.2, 0.1), aL=(0.2, 1.9, 1.6, -1.5), head=(0.1, -0.2)))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(-3.0, -2.0, k), lerp(-11.5, -10.5, k), lerp(3.4, 3.8, k)), A(2.4, 3.0, lerp(4.4, 3.6, k)), 30)


def marker_lost(S, k, t, lt):
    """After the storm the marker is where they left it. The raft is not."""
    A = ocean(S, 'storm', t, 1.3)
    hz = wave_h(0, 0, t, 1.3)
    S['buoy'].location = A(0, 0, hz)
    S['buoy'].rotation_euler = (0.2 * math.sin(t * 1.9), 0.25 * math.sin(t * 2.3), 0)
    S['buoy'].scale = (1.6, 1.6, 1.6)
    S['dye'].location = A(1.5, 1.0, hz + 0.3)
    S['dye'].scale = (3.6, 2.4, 1)
    S['plane'].location = A(lerp(-90, 60, k), 170, 46)
    S['plane'].rotation_euler = (0.3, 0, 0)
    for p in S['props']:
        p.rotation_euler = (t * 40, 0, 0)
    S['rook'].root.parent = S['buoy']
    S['rook'].place((0, 0, 0.25), 0.25)
    S['rook'].root.scale = (0.62, 0.62, 0.62)
    S['rook'].apply(P('sit', aL=(0.3, 0.75, 1.5, -0.9), aR=(0.3, 0.75, 1.5, -0.9), head=(0.0, 0.8 * math.sin(t * 1.4)), lean=0.1))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(4.6, 3.6, k), lerp(-9.4, -8.4, k), 2.6 + wave_h(4, -9, t, 0.8)), A(0.0, 0.0, 1.9), 34, 0.06 * math.sin(t * 1.3))


def colour_change(S, k, t, lt):
    """April 1943: the sea is no longer deep-ocean blue. Seen from above."""
    A = ocean(S, 'noon', t, 0.4)
    tint(S['seamat'], lerp_col('1284A4', '5E8E5A', ease(k * 1.2)))
    ride(S, t, 0, 0, lerp(0.2, 0.5, k), tilt=0.5)
    aboard(S, S['poon'], -0.7, -1.5, 0.0, P('sit', aL=(1.4, 0.1, 0.3), aR=(0.7, 0.1, 1.2), lean=0.6, head=(0.3, 0.0), lift=-0.6))
    S['face']['poon'] = 'calm'
    aboard(S, S['rook'], 1.0, -1.0, 0.3, P('stand', aL=(0.1, 0.4, 0.3), aR=(0.1, 0.4, 0.3), head=(0.5, 0.4 * math.sin(t * 1.5)), lean=0.25))
    S['face']['rook'] = 'shocked'
    for i, g in enumerate(S['gulls'][:2]):
        g['root'].location = A(-4 + i * 7 + 2 * math.sin(t * 0.8 + i), 3 + i * 2 + 2 * math.cos(t * 0.8 + i), 5.5 + i)
        g['root'].scale = (1.6, 1.6, 1.6)
        flap(g, t + i, 7, 0.6)
    cam(S, A(lerp(1.0, 0.2, k), lerp(-5.4, -4.0, k), lerp(13.5, 11.0, k)), A(0, -0.2, 0.5), 34, lerp(0.08, -0.05, k))


def shirt_wave(S, k, t, lt):
    """5 April 1943: he waves a shirt and jumps. A sail turns toward him."""
    A = ocean(S, 'dawn', t, 0.5)
    ride(S, t, 0, 0, 0.35)
    S['coast'].location = A(0, 330, 0)
    w = math.sin(t * 9)
    j = abs(math.sin(t * 6))
    aboard(S, S['poon'], -0.5, 0.3, PI - 0.2, P('up', aL=(0.4, 0.4, 0.3), aR=(2.8, 0.3 + 0.5 * w, 0.2), head=(-0.2, 0.0), lL=(0.2 * j, 0.5 * j), lR=(0.2 * j, 0.5 * j)), z=DECK + 0.45 * j)
    S['face']['poon'] = 'happy'
    on(S, S['shirt'], S['poon'].hands[1], (0.25 * w, 0, -0.45), (0, 0.6 * w, 0))
    S['shirt'].scale = (1.2, 0.05, 0.95)
    aboard(S, S['rook'], 1.2, -0.5, PI - 0.6, P('up', aL=(2.7, 0.5 + 0.35 * w, 0.2), aR=(2.7, 0.5 - 0.35 * w, 0.2), head=(-0.2, 0.0)), z=DECK + 0.3 * abs(math.cos(t * 6)))
    S['face']['rook'] = 'shocked'
    u = ease(k)
    bx, by = lerp(-22, -12, u), lerp(44, 26, u)
    S['boat'].location = A(bx, by, wave_h(bx, by, t, 0.5) + 0.25)
    S['boat'].rotation_euler = (0.04 * math.sin(t * 1.6), 0.03 * math.sin(t), lerp(0.3, PI + 0.9, ease(k * 1.4)))
    S['boat'].scale = (1.6, 1.6, 1.6)
    for i, m in enumerate(S['men']):
        aboard(S, m, (1.8, 0.2, -1.6)[i], 0.3, PI / 2, P('point', aR=(1.5, 0.3, 0.05)) if i == 0 else P('stand'), z=0.9, on='boat')
        m.root.scale = (0.74, 0.74, 0.74)
    for i, g in enumerate(S['gulls'][:3]):
        g['root'].location = A(-12 + i * 6 + t * 1.5, 18 + i * 7, 8 + i * 1.5 + 0.5 * math.sin(t * 2 + i))
        g['root'].scale = (2.2, 2.2, 2.2)
        flap(g, t + i * 0.3, 7.5, 0.65)
    cam(S, A(lerp(2.4, 1.6, k), lerp(-9.6, -8.8, k), lerp(3.2, 3.6, k)), A(-2.5, 18, 3.6), 36, fill=0.8)


# ---------------------------------------------------------------- long shots: ashore
def belem_dock(S, k, t, lt):
    """Three days later: landed at Belem."""
    A = show(S, 'belem')
    sky(S, 'A8D4EE', 1.0)
    S['fillk'] = 7.0
    S['fill'].data.color = K.hexc('FFF4E0')[:3]
    S['bboat'].location = (-5.5, 0.9, 0.35 + 0.05 * math.sin(t * 1.5))
    S['bboat'].rotation_euler = (0.02 * math.sin(t * 1.3), 0, 0)
    S['bboat'].scale = (1.25, 1.25, 1.25)
    u = ease(k * 1.1)
    S['poon'].place(A(lerp(-2.6, 0.4, u), lerp(2.6, 4.6, u), lerp(1.6, 1.4, min(1, u * 2.5))), PI / 2 + 0.5)
    pw = walk(t, 0.9)
    S['poon'].apply(P('stand', lL=pw['lL'], lR=pw['lR'], aL=(0.2, 0.3, 0.3), aR=(0.3, 0.2, 0.4), lean=0.14, head=(0.1, 0.0)))
    S['face']['poon'] = 'tired'
    S['men'][0].root.parent = S['bboat']
    S['men'][0].place((1.9, 0.3, 0.9), PI / 2)
    S['men'][0].apply(P('stand', aR=(1.2, 0.2, 0.4), head=(0.0, 0.0)))
    S['men'][0].root.scale = (0.8, 0.8, 0.8)
    S['men'][1].root.parent = S['bboat']
    S['men'][1].place((-1.6, 0.2, 0.9), PI)
    S['men'][1].apply(P('hips'))
    S['men'][1].root.scale = (0.8, 0.8, 0.8)
    S['ex'][0].place(A(3.6, 5.2, 1.4), -PI / 2 - 0.3)
    S['ex'][0].apply(P('stand', aR=(1.0, 0.2, 0.9), head=(0.05, 0.0)))
    S['ex'][1].place(A(4.9, 6.3, 1.4), -PI / 2 - 0.1)
    S['ex'][1].apply(P('stand', aL=(0.8, 0.1, 1.2), aR=(0.8, 0.1, 1.2), head=(0.05, 0.0)))
    S['ex'][2].place(A(-1.5, 8.4, 1.4), 0.3)
    S['ex'][2].apply(P('hips', head=(0.0, 0.0)))
    S['ex'][3].place(A(2.2, 8.8, 1.4), 0.2)
    S['ex'][3].apply(P('point', aR=(1.4, 0.2, 0.1)))
    tip = ease((lt - 0.6) / 0.6)
    S['rook'].place(A(4.6, 3.9, 1.4), 0.9)
    S['rook'].apply(blend(P('stand', head=(0.0, 0.5)), P('hat', head=(0.15, 0.5)), tip))
    S['hat_tip'] = tip * 0.6
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(9.6, 8.6, k), lerp(-1.6, -0.8, k), lerp(3.6, 3.9, k)), A(0.2, 5.0, 2.9), 32, fill=0.6)


def ward(S, k, t, lt):
    """Weeks in hospital."""
    A = inside(S, 'ward', '0E1214')
    S['fan'].rotation_euler = (0, 0, t * 4.0)
    S['poon'].place(A(0, 4.0, 0.52), 0.0)
    sp = 0.5 + 0.5 * math.sin(t * 2.2)
    S['poon'].apply(P('stand', lL=(1.5, 0.05), lR=(1.5, 0.05), aL=(0.9, 0.1, 1.3, 0.5), aR=(0.9 + 0.4 * sp, 0.0, 1.3 + 0.6 * sp, 0.6), lean=-0.12, head=(0.2, 0.0), lift=0.0))
    S['face']['poon'] = 'happy'
    S['blanket'].location = A(0, 2.5, 1.2)
    on(S, S['bowl'], S['poon'].hands[0], (0.08, -0.1, -0.12), (PI, 0, 0))
    S['ex'][1].place(A(-2.1, 3.3, 0), PI / 2 + 0.35)
    S['ex'][1].apply(P('stand', aL=(1.0, 0.0, 1.3, 0.5), aR=(1.1, 0.0, 1.4, 0.4), head=(0.25, 0.0)))
    on(S, S['clip'], S['ex'][1].hands[0], (0.12, -0.14, -0.1), (0.5, 0, 0))
    seat(S['rook'], A(2.5, 1.6, 0.76), -0.9, aL=(0.6, 0.0, 1.5, 1.0), aR=(0.6, 0.0, 1.5, 1.0), head=(0.1, 0.25 * math.sin(t * 1.2)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(-1.0, 0.4, k), lerp(-6.8, -6.0, k), lerp(2.9, 2.6, k)), A(0.3, 2.8, 2.0), 32)


def medal(S, k, t, lt):
    """New York, 16 July 1943: the British Empire Medal. The official is a stand-in, not a likeness of anyone."""
    A = inside(S, 'hall', '14100C')
    u = ease((lt - 0.5) / 0.9)
    S['poon'].place(A(-0.9, 4.2, 0.6), PI / 2 - 0.35)
    S['poon'].apply(P('stand', head=(lerp(0.0, 0.2, u), 0.0)))
    S['face']['poon'] = 'happy'
    S['ex'][0].place(A(0.9, 4.0, 0.6), -PI / 2 + 0.35)
    S['ex'][0].apply(blend(P('stand', aR=(1.0, 0.1, 1.2), head=(0.1, 0.0)), P('stand', aR=(1.45, -0.1, 0.25), head=(0.15, 0.0)), math.sin(PI * u)))
    if u < 0.55:
        on(S, S['medal'], S['ex'][0].hands[1], (0, -0.1, -0.28))
    else:
        on(S, S['medal'], S['poon'].body, (-0.16, -0.36, 0.78))
    S['medal'].scale = (1.5, 1.5, 1.5)
    cl = 0.25 * abs(math.sin(t * 9)) if u > 0.55 else 0.0
    S['rook'].place(A(-4.2, 3.9, 0.6), 0.45)
    S['rook'].apply(P('stand', aL=(1.1, -0.1 + cl, 1.3, 0.9), aR=(1.1, -0.1 + cl, 1.3, 0.9), head=(0.05, -0.5)))
    S['face']['rook'] = 'warm'
    seat(S['ex'][2], A(-1.8, -0.6, 0.77), PI, aL=(0.9, 0.1 + cl, 1.4, 0.8), aR=(0.9, 0.1 + cl, 1.4, 0.8), head=(-0.1, 0.0))
    seat(S['ex'][3], A(3.6, -0.6, 0.77), PI, aL=(0.9, 0.1 + cl, 1.4, 0.8), aR=(0.9, 0.1 + cl, 1.4, 0.8), head=(-0.1, 0.0))
    seat(S['ex'][1], A(1.8, -2.4, 0.77), PI, aL=(0.9, 0.1, 1.4, 0.8), aR=(0.9, 0.1, 1.4, 0.8), head=(-0.1, 0.0))
    cam(S, A(lerp(0.9, 0.1, k), lerp(-5.6, -4.8, k), lerp(3.6, 3.4, k)), A(-1.2, 4.1, 3.0), 36)


def watch(S, k, t, lt):
    """A gold watch from his shipping line."""
    A = inside(S, 'hall', '14100C')
    for hnd in ('hand_p', 'hand_o'):
        S[hnd].root.scale = (1.5, 1.5, 1.5)
    u = ease(lt / 0.7)
    S['hand_o'].place(A(lerp(2.0, 0.62, u), 3.0, 2.6), (0, PI, -PI / 2))
    S['hand_o'].grip(0.25)
    S['hand_p'].place(A(lerp(-2.2, -0.7, u), 3.0, 2.38), (0, PI, PI / 2))
    S['hand_p'].grip(0.2 + 0.3 * ease((lt - 1.0) / 0.4))
    v = ease((lt - 0.9) / 0.5)
    S['watch'].location = A(lerp(lerp(2.0, 0.62, u) - 0.62, -0.2, v), 2.9, 2.74 - 0.2 * v + 0.25 * math.sin(PI * v))
    S['watch'].rotation_euler = (0.5, 0.0, 0.3 + 0.2 * math.sin(t * 2))
    sc = 1.5 + 0.15 * math.sin(t * 5)
    S['watch'].scale = (sc, sc, sc)
    S['glow'].location = A(0, 1.2, 3.2)
    S['glow'].data.energy = 40
    S['glow'].data.color = K.hexc('FFE0A0')[:3]
    cam(S, A(lerp(0.5, 0.1, k), lerp(-0.9, -0.4, k), lerp(3.0, 2.9, k)), A(0, 3.0, 2.55), 45, 0.04)


def flat_feet(S, k, t, lt):
    """He applies to the US Navy and is turned down for flat feet. The man at the desk is a stand-in."""
    A0 = inside(S, 'hall', '101216')
    A = lambda x, y, z: A0(60 + x, y, z)
    S['poon'].place(A(-1.2, 1.4, 0), PI / 2)
    S['poon'].apply(P('stand', head=(lerp(0.0, 0.3, ease((k - 0.5) * 3)), 0.0)))
    S['face']['poon'] = 'calm'
    sh = math.sin(t * 5) * (1 if k > 0.3 else 0)
    seat(S['ex'][0], A(3.4, 1.4, 0.8), -PI / 2, aL=(1.0, 0.1, 1.0), aR=(1.2, 0.0, 0.7), head=(0.15, 0.45 * sh))
    on(S, S['paper'], S['ex'][0].hands[1], (0, -0.2, 0.1), (0.3, 0, 0))
    u = ease((lt - 0.8) / 0.5)
    S['rook'].place(A(-4.2, 0.2, 0), 0.5)
    S['rook'].apply(blend(P('hips', head=(0.0, -0.5)), P('stand', aL=(0.1, 0.5, 0.3), aR=(0.1, 0.5, 0.3), lL=(1.0, 1.1), head=(0.6, 0.15), lean=0.2), u))
    S['face']['rook'] = 'deadpan' if u < 0.5 else 'shocked'
    cam(S, A(lerp(-1.4, -0.4, k), lerp(-8.0, -7.2, k), 2.9), A(-0.4, 1.4, 2.1), 34)


def brooklyn(S, k, t, lt):
    """Brooklyn, late in life. prm gone: the step beside Rook is empty."""
    A = show(S, 'stoop')
    sky(S, '4A3A6A', 0.9)
    gone = S['prm'].get('gone')
    if not gone:
        seat(S['old'], A(-2.9, 4.4, 0.72), 0.1, aL=(0.7, 0.0, 1.4, 0.9), aR=(0.7, 0.0, 1.4, 0.9), head=(lerp(0.2, -0.2, ease(k * 1.5)), 0.2), lean=0.15)
    tip = math.sin(PI * ease((lt - 0.8) / 1.4)) if lt > 0.8 else 0.0
    seat(S['rook'], A(-1.4, 4.4, 0.72), -0.1, aL=(0.6, 0.0, 1.5, 1.0), aR=(0.6, 0.0, 1.5, 1.0), head=(0.1 if not gone else 0.3, lerp(0.0, -0.5, ease(k * 2)) if not gone else -0.5 * (1 - ease(k * 1.5))))
    if gone:
        S['rook'].apply(blend(P('sit', aL=(0.6, 0.0, 1.5, 1.0), aR=(0.6, 0.0, 1.5, 1.0), head=(0.3, -0.4)), P('sit', aL=(0.6, 0.0, 1.5, 1.0), aR=(0.2, 1.9, 1.6, -1.5), head=(0.3, 0.0)), tip))
        S['hat_tip'] = tip * 0.7
    S['face']['rook'] = 'warm' if not gone else 'sad'
    cam(S, A(lerp(-0.4, -1.2, k), lerp(-3.4, -2.6, k), lerp(2.2, 2.4, k)), A(-2.1, 4.4, 2.3), 40)


def shark_won(S, k, t, lt):
    """He wins, with the water jug."""
    A = ocean(S, 'noon', t, 0.5)
    ride(S, t, 0, 0, -0.2)
    on(S, S['shark'], S['raft'], (0.5, -1.5, DECK + 0.3), (0.1, 0, 0.25))
    S['shark'].scale = (0.55, 0.55, 0.55)
    br = 0.06 * math.sin(t * 5)
    aboard(S, S['poon'], -1.1, -0.6, 0.45, P('sit', aL=(0.8, 0.2, 1.1, 0.6), aR=(0.8, 0.2, 1.1, 0.6), head=(0.35 + br, 0.0), lean=0.3 + br))
    S['face']['poon'] = 'tired'
    on(S, S['jug'], S['raft'], (-0.3, -1.5, DECK), (0, 0, 0))
    u = ease((lt - 0.6) / 0.6)
    aboard(S, S['rook'], 1.75, 0.0, 0.5, blend(P('up', aL=(1.9, 0.6, 1.4, 0.8), aR=(1.9, 0.6, 1.4, 0.8), lL=(1.2, 1.7), lR=(0.9, 1.5), head=(0.3, -0.5)),
                                               P('point', aR=(1.2, 0.3, 0.2), head=(0.3, -0.5)), u), z=DECK + 0.9 * (1 - u))
    S['face']['rook'] = 'shocked' if u < 0.6 else 'deadpan'
    cam(S, A(lerp(3.4, 2.6, k), lerp(-7.6, -6.8, k), lerp(2.2, 2.5, k)), A(0.2, -0.8, 1.5), 38)


def _with(fn, **flags):
    def g(S, k, t, lt):
        S['prm'] = dict(S['prm'], **flags)
        fn(S, k, t, lt)
    return g


drift_apart = _with(other_raft, far=1)
cabin_quit = _with(cabin_boy, quit=1)
frt_away = _with(frt_close, away=1)
brooklyn_end = _with(brooklyn, gone=1)
knots_night = _with(knots_cu, night=1)


def photo_thumb(S, k, t, lt):
    """Thumbnail: the man on the raft with a line in the water, a fin beside it, Rook's hat leaving his head."""
    A = ocean(S, 'day', 2.0, 0.6)
    ride(S, 2.0, 0, 0, 0.35)
    aboard(S, S['poon'], -0.9, -0.9, 0.35, P('stand', aL=(1.1, 0.2, 0.7), aR=(1.1, 0.2, 0.7), lean=0.25, lL=(0.4, 0.6), lR=(0.1, 0.3), head=(0.05, 0.3)))
    S['face']['poon'] = 'scared'
    on(S, S['line'], S['raft'], (0, 0, 0))
    span(S['line'], (-1.05, -1.65, DECK + 1.5), (0.2, -4.4, -0.3))
    aboard(S, S['rook'], 1.0, -0.6, 0.0, P('hat', aL=(0.3, 0.9, 1.3), lL=(0.9, 1.5), lift=0.3, head=(0.2, 0.3)))
    S['face']['rook'] = 'shocked'
    S['shark'].location = A(1.2, -3.9, 0.12)
    S['shark'].rotation_euler = (0, 0, 0.35)
    S['shark'].scale = (0.8, 0.8, 0.8)
    feathers(S, A(1.4, -0.9, 3.3), 0.45, 4)
    cam(S, A(5.2, -10.5, 3.6), A(2.6, -0.8, 1.9), 40)


HOST |= {'cabin_boy', 'mess', 'quay_leave', 'plank_float', 'other_raft', 'ration', 'wrist_rope', 'big_fish', 'dry_line', 'life_cover', 'nest_trap',
         'storm_after', 'shark_haul', 'shark_fight', 'fins_dry', 'swim_round', 'moon_count', 'frt_close', 'marker_drop', 'marker_lost', 'colour_change',
         'shirt_wave', 'belem_dock', 'ward', 'medal', 'flat_feet', 'brooklyn', 'shark_won', 'drift_apart', 'cabin_quit', 'frt_away', 'brooklyn_end'}
SHOTS3D.update({f.__name__: f for f in (
    cabin_boy, mess, quay_leave, plank_float, other_raft, ration, wrist_rope, knots_cu, nail_hook, big_fish, dry_line, life_cover, nest_trap, storm_after,
    shark_haul, shark_fight, fins_dry, swim_round, moon_count, frt_close, marker_drop, marker_lost, colour_change, shirt_wave, belem_dock, ward, medal, watch,
    flat_feet, brooklyn, shark_won)})
SHOTS3D.update(drift_apart=drift_apart, cabin_quit=cabin_quit, frt_away=frt_away, brooklyn_end=brooklyn_end, knots_night=knots_night)
STILLS['thumb'] = photo_thumb
