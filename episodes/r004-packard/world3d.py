"""Case 004 in 3D - Michael Packard, off Provincetown, Cape Cod, 11 June 2021. Sets built for this story only:
a fishing pier at first light, the sandy sea floor in green shallow water, the bright bay with the lobster boat,
the inside of a humpback's mouth, and a hospital room in the afternoon. The humpback itself is a jointed model."""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(sand=(0, 0, 0), pier=(500, 0, 0), gullet=(1000, 0, 0), ward=(1500, 0, 0), bay=(0, 700, 0))
FAR = (0, 0, -800)
HOST = {'rook_dock', 'rook_dive', 'boat_wide', 'descend', 'sand_hunt', 'shoal', 'shadow', 'mouth_wide', 'rook_quiet', 'flung', 'haul',
        'walk_out', 'rook_door', 'feeding', 'throat_look', 'rook_shrug', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SUIT = dict(top='1F2A36', pants='18212B', hand='101418', boot='101418', fore='27475E')
GOWN = dict(top='A9CBDD', pants='A9CBDD', hand='D9A888', boot='E8E2D4', fore='D9A888')
CREW = dict(top='3A4656', pants='E8761E', hand='C99672', boot='2A2622')
BACK, BELLY, FLESH, BRASS, FIN = '33475C', 'D2D8D6', 'C4607A', 'FFC233', 'F2C230'
DEN = (2.7, 1.5, 0.0)            # the rock ledge where the lobster sits
WS = 0.75                        # whale scale: about 18 units long, a young humpback beside 3-unit people


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def at(name, x, y, z):
    o = ORG[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def group(name, fn):
    before = set(bpy.data.objects)
    out = fn(empty(ORG[name]))
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    for o in set(bpy.data.objects) - before:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        c.objects.link(o)
    return c, out


def half(col, radii, parent, top=True, loc=(0, 0, 0), sub=2, **kw):
    """Half an ellipsoid (a dome or a bowl), open on the cut side."""
    o = add('ico_sphere', col, loc, radius=1, subdivisions=sub, parent=parent, **kw)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 0, 1),
                           clear_outer=not top, clear_inner=top)
    bm.to_mesh(o.data)
    bm.free()
    o.scale = radii
    return o


# ---------------------------------------------------------------- cast heads and props
def scuba_head(head):
    """Hooded head with a yellow-framed mask and a regulator."""
    add('ico_sphere', '14181E', (0, 0.02, 0.03), scale=(1, 1.03, 1.06), radius=0.34, subdivisions=2, parent=head)
    add('cube', 'D9A888', (0, -0.285, -0.03), scale=(0.34, 0.06, 0.36), size=1, parent=head)
    add('cube', FIN, (0, -0.3, 0.07), scale=(0.5, 0.1, 0.27), size=1, parent=head, rough=0.5)
    add('cube', '0C2836', (0, -0.33, 0.07), scale=(0.43, 0.08, 0.2), size=1, parent=head, rough=0.2)
    eyes = [add('cube', 'FFFFFF', (s * 0.1, -0.375, 0.07), scale=(0.085, 0.02, 0.08), size=1, parent=head, emit=1.1) for s in (-1, 1)]
    add('cylinder', '3A424C', (0, -0.39, -0.15), rot=(PI / 2, 0, 0), radius=0.15, depth=0.2, vertices=8, parent=head, rough=0.4)
    add('cylinder', '59626E', (0, -0.5, -0.15), rot=(PI / 2, 0, 0), radius=0.08, depth=0.04, vertices=8, parent=head, rough=0.3)
    add('cube', '3A424C', (0, -0.36, -0.15), scale=(0.44, 0.1, 0.1), size=1, parent=head)
    add('cylinder', '14181E', (0.24, -0.22, -0.2), rot=(0, PI / 2, 0.6), radius=0.035, depth=0.55, vertices=5, parent=head)
    return dict(eyes=eyes, eye0=0.08)


def person_head(skin, hair):
    base = K.human_head(skin, hair)

    def fn(head):
        d = base(head)
        d['eye0'] = 0.075
        return d
    return fn


def kit_up(rig):
    """A single steel tank, yellow fins and an orange catch bag."""
    add('cylinder', 'B4BCC6', (0, 0.38, 0.6), radius=0.18, depth=0.98, vertices=8, parent=rig.body, rough=0.35)
    add('cylinder', '14181E', (0, 0.38, 1.14), radius=0.07, depth=0.14, vertices=6, parent=rig.body)
    add('cube', '14181E', (0, 0.04, 0.72), scale=(0.8, 0.74, 0.08), size=1, parent=rig.body)
    add('cube', 'E8761E', (0, 0.04, 0.3), scale=(0.72, 0.7, 0.1), size=1, parent=rig.body)          # weight belt
    for kn in rig.kn:
        add('cube', FIN, (0, -0.62, -0.5), scale=(0.36, 1.0, 0.05), size=1, parent=kn)
    add('ico_sphere', 'E8761E', (-0.42, -0.05, -0.05), scale=(0.7, 0.8, 1.3), radius=0.24, subdivisions=1, parent=rig.body, rough=0.8)


def make_lobster(parent, loc, yaw=0.0, s=1.0, col='7A3222'):
    """Lobster, claws toward -Y."""
    r = empty(loc, parent, (0, 0, yaw))
    add('cube', col, (0, 0, 0.14), scale=(0.3, 0.62, 0.24), size=1, parent=r)
    for i in range(4):
        add('cube', col, (0, 0.42 + i * 0.2, 0.12 - i * 0.015), scale=(0.27 - i * 0.03, 0.19, 0.17 - i * 0.02), size=1, parent=r)
    add('cube', col, (0, 1.24, 0.08), scale=(0.42, 0.22, 0.05), size=1, parent=r)
    claws = []
    for sx in (-1, 1):
        a = empty((sx * 0.17, -0.25, 0.14), r)
        add('cylinder', col, (sx * 0.15, -0.26, 0.0), rot=(PI / 2, 0, sx * 0.5), radius=0.05, depth=0.6, vertices=5, parent=a)
        add('ico_sphere', 'A8482A', (sx * 0.3, -0.72, 0.02), scale=(0.75, 1.5, 0.5), radius=0.2, subdivisions=1, parent=a)
        add('cylinder', 'C86A3A', (sx * 0.08, -0.72, 0.2), rot=(PI / 2 + 0.45, 0, sx * -0.18), radius=0.012, depth=1.3, vertices=4, parent=r)
        for j in range(3):
            add('cube', col, (sx * 0.28, 0.0 + j * 0.17, 0.06), rot=(0, sx * 0.5, 0), scale=(0.34, 0.035, 0.035), size=1, parent=r)
        add('ico_sphere', '0E0D14', (sx * 0.08, -0.33, 0.27), radius=0.035, subdivisions=1, parent=r)
        claws.append(a)
    r.scale = (s, s, s)
    return dict(root=r, claws=claws)


def make_trap(parent, loc, yaw=0.0, col=FIN):
    """Wire lobster trap: dark mesh box, coloured hoops and runners, an orange funnel ring."""
    r = empty(loc, parent, (0, 0, yaw))
    add('cube', '26342C', (0, 0, 0.42), scale=(1.8, 1.1, 0.8), size=1, parent=r)
    for x in (-0.86, -0.3, 0.3, 0.86):
        add('cube', col, (x, 0, 0.42), scale=(0.07, 1.16, 0.86), size=1, parent=r)
    for y in (-0.55, 0.55):
        for z in (0.03, 0.83):
            add('cube', col, (0, y, z), scale=(1.86, 0.07, 0.07), size=1, parent=r)
    add('torus', 'E8761E', (0.92, 0, 0.45), rot=(0, PI / 2, 0), major_radius=0.22, minor_radius=0.04, major_segments=8, minor_segments=4, parent=r)
    return r


def make_buoy(parent, loc, col, s=1.0):
    r = empty(loc, parent)
    add('cylinder', col, (0, 0, 0), radius=0.2, depth=0.55, vertices=8, parent=r)
    add('cylinder', 'F4EEDF', (0, 0, 0.0), radius=0.205, depth=0.14, vertices=8, parent=r)
    add('cone', col, (0, 0, -0.42), rot=(PI, 0, 0), radius1=0.2, radius2=0.04, depth=0.3, vertices=8, parent=r)
    add('cylinder', '2A2622', (0, 0, 0.45), radius=0.03, depth=0.4, vertices=4, parent=r)
    r.scale = (s, s, s)
    return r


def make_whale():
    """Young humpback, head toward -Y. The jaws are two half shells on a hinge at the root, so the mouth can gape."""
    root = empty()
    w = empty(parent=root)
    w.scale = (WS, WS, WS)
    add('ico_sphere', BACK, (0, 5.6, 0.05), scale=(2.25, 6.7, 2.05), radius=1, subdivisions=2, parent=w)
    add('ico_sphere', BELLY, (0, 4.6, -0.4), scale=(2.0, 5.2, 1.85), radius=1, subdivisions=2, parent=w)
    add('ico_sphere', '8E3C52', (0, 0.3, 0), scale=(2.0, 2.3, 1.55), radius=1, subdivisions=2, parent=w)          # the back of the mouth
    add('cone', BACK, (0, 9.2, 2.0), rot=(-0.6, 0, 0), radius1=0.75, radius2=0.05, depth=1.1, vertices=4, parent=w)
    tl = empty((0, 10.2, 0), w)
    add('cone', BACK, (0, 3.2, 0), rot=(-PI / 2, 0, 0), radius1=1.55, radius2=0.33, depth=7.0, vertices=8, parent=tl)
    fk = empty((0, 6.5, 0), tl)
    for s in (-1, 1):
        add('ico_sphere', BACK, (s * 3.0, 0.7, 0), rot=(0, 0, s * -0.45), scale=(3.7, 1.45, 0.15), radius=1, subdivisions=1, parent=fk)
        add('ico_sphere', 'E4E8E6', (s * 3.2, 0.9, -0.08), rot=(0, 0, s * -0.45), scale=(2.4, 0.9, 0.1), radius=1, subdivisions=1, parent=fk)
    fl = []
    for s in (-1, 1):
        f = empty((s * 1.85, 2.0, -1.0), w, (0, s * 0.35, s * -0.45))
        add('ico_sphere', 'D8DEDC', (s * 2.5, 0, 0), scale=(2.7, 0.62, 0.13), radius=1, subdivisions=1, parent=f)
        for j in range(5):
            add('ico_sphere', 'D8DEDC', (s * (0.9 + j * 0.85), -0.52, 0), radius=0.2, subdivisions=1, parent=f)
        fl.append(f)
        add('ico_sphere', '0E0D14', (s * 2.08, 1.0, -0.2), radius=0.17, subdivisions=1, parent=w, rough=0.2)
        add('ico_sphere', 'FFFFFF', (s * 2.2, 0.94, -0.14), radius=0.055, subdivisions=1, parent=w, emit=2)
    up = empty((0, 0, 0.15), w)
    half(BACK, (2.15, 6.0, 1.15), up, True)
    half(FLESH, (1.98, 5.75, 0.98), up, True)
    for s in (-1, 1):
        for j in range(17):
            y = -0.5 - j * 0.31
            x = 1.9 * math.sqrt(max(0.0, 1 - (y / 5.8) ** 2))
            add('cube', ('2B2622', '3A342C')[j % 2], (s * x, y, -0.42), rot=(0, 0, s * 0.25 * (j / 17)), scale=(0.07, 0.25, 1.0), size=1, parent=up)
        for j in range(4):
            add('ico_sphere', '485E76', (s * (0.5 + 0.25 * (j % 2)), -1.6 - j * 1.0, 1.05 - 0.085 * j * j), radius=0.19, subdivisions=1, parent=up)
    add('cube', '22303E', (0, -0.9, 1.12), scale=(0.5, 0.7, 0.14), size=1, parent=up)                           # blowholes
    lo = empty((0, 0, -0.05), w)
    half(BELLY, (2.3, 6.1, 1.9), lo, False)
    half(FLESH, (2.12, 5.85, 1.72), lo, False)
    for i in range(-5, 6):
        f = math.sqrt(1 - (i * 0.36 / 2.3) ** 2)
        half('8C98A2', (0.035, 6.1 * f + 0.03, 1.9 * f + 0.03), lo, False, loc=(i * 0.36, 0, 0), sub=1)
    add('ico_sphere', 'DA7C92', (0, -2.4, -0.95), scale=(1.4, 2.8, 0.55), radius=1, subdivisions=2, parent=lo)
    return dict(root=root, w=w, up=up, lo=lo, tl=tl, fk=fk, fl=fl)


def make_boat(r):
    """Lobster boat, bow toward +X, about 16 long: white hull, blue sheer line, wheelhouse forward with an orange roof,
    open work deck aft with traps, a hauler and a diver-down flag."""
    add('cube', 'F0EEE6', (-1, 0, 0.9), scale=(13, 5, 2.2), size=1, parent=r)
    s = 5 / math.sqrt(2)
    add('cube', 'F0EEE6', (5.5, 0, 0.9), rot=(0, 0, PI / 4), scale=(s, s, 2.2), size=1, parent=r)
    add('cube', '8E2A24', (-1, 0, -0.25), scale=(13.06, 5.06, 0.7), size=1, parent=r)
    add('cube', '8E2A24', (5.5, 0, -0.25), rot=(0, 0, PI / 4), scale=(s + 0.04, s + 0.04, 0.7), size=1, parent=r)
    add('cube', '2C6E92', (-1, 0, 1.86), scale=(13.08, 5.08, 0.26), size=1, parent=r)
    add('cube', '2C6E92', (5.5, 0, 1.86), rot=(0, 0, PI / 4), scale=(s + 0.06, s + 0.06, 0.26), size=1, parent=r)
    add('cube', 'B4AE9C', (-1, 0, 2.02), scale=(12.8, 4.7, 0.06), size=1, parent=r)
    for sy in (-1, 1):
        add('cube', 'F0EEE6', (-1, sy * 2.42, 2.36), scale=(13, 0.16, 0.7), size=1, parent=r)
        add('cube', '8A6A48', (-1, sy * 2.42, 2.74), scale=(13.1, 0.26, 0.08), size=1, parent=r)
    add('cube', 'F0EEE6', (-7.42, 0, 2.36), scale=(0.16, 5, 0.7), size=1, parent=r)
    add('cube', 'F4F2EA', (3.3, 0, 3.6), scale=(4.2, 3.9, 3.2), size=1, parent=r)
    add('cube', '12303A', (5.41, 0, 4.1), scale=(0.06, 3.3, 1.1), size=1, parent=r, rough=0.2)
    for sy in (-1, 1):
        add('cube', '12303A', (3.6, sy * 1.96, 4.1), scale=(2.6, 0.06, 1.0), size=1, parent=r, rough=0.2)
    add('cube', 'E8761E', (3.1, 0, 5.3), scale=(5.0, 4.4, 0.2), size=1, parent=r)
    add('cylinder', 'C8CCD4', (3.6, 0, 6.6), radius=0.08, depth=2.6, vertices=5, parent=r)
    add('cube', 'F4F2EA', (3.6, 0, 6.9), scale=(0.25, 1.7, 0.2), size=1, parent=r)
    add('ico_sphere', 'FFFFFF', (3.6, 0, 7.95), radius=0.14, subdivisions=1, parent=r, emit=6)
    add('cylinder', '22262C', (1.6, 1.3, 5.6), radius=0.2, depth=1.5, vertices=6, parent=r)
    add('cylinder', 'C8CCD4', (1.2, -1.9, 6.6), radius=0.05, depth=2.6, vertices=4, parent=r)                   # flag staff
    add('cube', 'D8382C', (0.55, -1.9, 7.4), scale=(1.3, 0.04, 0.9), size=1, parent=r, emit=0.3)
    add('cube', 'FFFFFF', (0.55, -1.93, 7.4), rot=(0, 0.6, 0), scale=(1.55, 0.03, 0.2), size=1, parent=r, emit=0.5)
    add('cylinder', '8A90A0', (0.2, -2.3, 3.6), radius=0.11, depth=2.9, vertices=6, parent=r)                   # hauler davit
    add('cube', '8A90A0', (0.2, -2.9, 4.95), scale=(0.16, 1.5, 0.16), size=1, parent=r)
    add('cylinder', 'E8761E', (0.2, -3.5, 4.75), rot=(0, PI / 2, 0), radius=0.24, depth=0.14, vertices=8, parent=r)
    make_trap(r, (-4.6, 1.3, 2.05), 0.0)
    make_trap(r, (-4.5, 1.25, 2.93), 0.08, '3E9A5A')
    make_trap(r, (-2.4, 1.4, 2.05), 0.0, '3E9A5A')
    add('cylinder', '2C6E92', (-6.4, -1.4, 2.5), radius=0.55, depth=0.9, vertices=10, parent=r)                 # catch tub
    for i, col in enumerate(('E8761E', FIN, 'D8382C')):
        make_buoy(r, (1.6 + i * 0.55, 1.9, 5.75), col, 0.9)
    return r


# ---------------------------------------------------------------- sets
def set_sand(r):
    add('plane', 'B0A074', (0, 0, 0), size=520, parent=r, rough=1.0)
    R = np.random.RandomState(11)
    for i in range(34):
        x, y = R.uniform(-30, 30), R.uniform(-12, 40)
        add('cube', ('A6966A', 'D2C296')[i % 2], (x, y, 0.02), rot=(0, 0, R.uniform(-0.25, 0.25)), scale=(R.uniform(5, 13), 0.3, 0.07), size=1, parent=r)
    # the rock pile with the ledge the lobster lives under
    for i, (x, y, sc) in enumerate(((3.6, 2.6, 1.5), (4.9, 1.2, 1.1), (2.6, 3.6, 1.0), (5.4, 3.4, 1.3), (4.2, 4.6, 0.9))):
        add('ico_sphere', ('5C5E58', '6C6A5E', '4E524E')[i % 3], (x, y, sc * 0.45), rot=(0.3 * i, 0, 0.9 * i), scale=(sc * 1.25, sc, sc * 0.75),
            radius=1.0, subdivisions=1, parent=r)
    add('cube', '63645C', (3.1, 1.9, 1.0), rot=(0.08, -0.1, 0.5), scale=(2.6, 1.9, 0.34), size=1, parent=r)
    add('cube', '1E221F', (3.1, 1.9, 0.45), rot=(0, 0, 0.5), scale=(1.9, 1.3, 0.8), size=1, parent=r)
    for i in range(16):
        a = R.uniform(0, 2 * PI)
        d = R.uniform(7, 24)
        x, y = math.cos(a) * d, 4 + math.sin(a) * d * 0.8
        add('ico_sphere', ('5C5E58', '6C6A5E', '4E524E')[i % 3], (x, y, 0.2), rot=(R.uniform(0, 3), 0, R.uniform(0, 3)),
            scale=(R.uniform(0.5, 1.6), R.uniform(0.4, 1.1), R.uniform(0.3, 0.7)), radius=1.0, subdivisions=1, parent=r)
    for i in range(46):                                   # eelgrass in clumps
        c = i // 6
        cx, cy = ((-6.5, 3.5), (6.8, 5.5), (-3.5, 8.5), (8.5, -1.5), (-9.0, -2.5), (1.5, 10.5), (-12.0, 7.0), (12.5, 9.0))[c % 8]
        add('cone', ('3E9450', '2F7A44', '57A85A')[i % 3], (cx + R.uniform(-0.9, 0.9), cy + R.uniform(-0.9, 0.9), 1.0), rot=(R.uniform(-0.25, 0.25), R.uniform(-0.25, 0.25), 0),
            radius1=0.1, radius2=0.0, depth=R.uniform(1.6, 2.8), vertices=3, parent=r)
    for i in range(5):                                    # an orange starfish on the ledge
        a = i * 2 * PI / 5
        add('cone', 'FF7A1A', (2.2 + math.cos(a) * 0.2, 2.6 + math.sin(a) * 0.2, 1.24), rot=(PI / 2, 0, a - PI / 2), radius1=0.1, radius2=0.0, depth=0.42, vertices=4, parent=r)
    make_lobster(r, (5.0, 0.2, 0.0), 2.2, 0.8)
    make_lobster(r, (-4.4, 4.2, 0.0), -0.7, 0.75, '6A3A28')
    lob = make_lobster(r, (0, 0, -30), 0.0, 1.0)
    add('cylinder', 'A8F0E0', (2, 4, 34), radius=19, depth=0.2, vertices=28, parent=r, emit=0.75)
    add('cylinder', 'D8FFF4', (2, 4, 33.8), radius=9, depth=0.2, vertices=24, parent=r, emit=1.1)                     # the bright surface far above
    aim = empty((0, 2, 2), r)
    sun = light((4, -6, 26), 6000, 'E4FFF2', 12.0, aim, parent=r)
    fill = light((-9, -9, 3), 1200, '36B0A8', 7.0, aim, parent=r)
    rim = light((9, 10, 6), 1800, 'FFB868', 4.0, aim, parent=r)
    return dict(s_sun=sun, s_fill=fill, s_rim=rim, lob=lob)


def set_pier(r):
    add('plane', '0E3442', (0, 0, -2.4), size=700, parent=r, rough=0.25)
    for i in range(-11, 5):
        add('cube', ('6A5440', '5C4936', '755F48')[i % 3], (i * 0.9, 2, -0.1), scale=(0.85, 19, 0.2), size=1, parent=r)
    for y in (-6.5, -2.5, 1.5, 5.5, 9.5):
        add('cylinder', '43352A', (4.15, y, -0.9), radius=0.3, depth=4.6, vertices=8, parent=r)
        add('cylinder', 'E8E2D0', (4.15, y, 1.44), radius=0.33, depth=0.1, vertices=8, parent=r)
    for y in (-4.5, -0.5, 3.5, 7.5):
        add('cylinder', 'B8A67C', (4.15, y, 0.95), rot=(PI / 2, 0, 0), radius=0.05, depth=4.0, vertices=5, parent=r)
    # the bait shack with its wall of buoys
    add('cube', '747C86', (-4.2, 9.0, 2.4), scale=(9.0, 4.4, 4.8), size=1, parent=r)
    for z in (0.8, 1.6, 2.4, 3.2, 4.0):
        add('cube', '646C76', (-4.2, 6.78, z), scale=(9.0, 0.04, 0.06), size=1, parent=r)
    add('cube', '343640', (-4.2, 9.0, 5.1), rot=(0.14, 0, 0), scale=(9.8, 5.4, 0.3), size=1, parent=r)
    add('cube', 'A8442C', (-1.6, 6.76, 1.75), scale=(1.5, 0.08, 3.5), size=1, parent=r)
    add('cube', 'FFD890', (-6.0, 6.76, 2.7), scale=(1.7, 0.06, 1.3), size=1, parent=r, emit=5)
    add('cube', '343640', (-6.0, 6.72, 2.7), scale=(0.08, 0.08, 1.3), size=1, parent=r)
    add('cube', '343640', (-6.0, 6.72, 2.7), scale=(1.7, 0.08, 0.08), size=1, parent=r)
    cols = ('E8761E', FIN, '3A8AD0', 'E8E4D8', 'D8382C', '3E9A5A', 'E8761E')
    for i, col in enumerate(cols):
        make_buoy(r, (-8.2 + i * 0.62 + (2.6 if i > 3 else 0), 6.55, 3.9 - 0.25 * (i % 2)), col)
    for i, (x, y, z, yaw, col) in enumerate(((-7.2, 2.6, 0, 0.1, FIN), (-7.1, 3.9, 0, -0.05, '3E9A5A'), (-7.15, 3.2, 0.88, 0.04, FIN), (-7.0, 5.2, 0, 0.2, FIN),
                                             (-7.2, 2.7, 1.76, -0.1, '3E9A5A'), (1.8, 8.6, 0, 1.5, FIN), (1.9, 8.5, 0.88, 1.62, '3E9A5A'))):
        make_trap(r, (x, y, z), yaw, col)
    add('torus', 'C8B890', (-3.4, 4.6, 0.12), major_radius=0.6, minor_radius=0.13, major_segments=12, minor_segments=5, parent=r)
    add('torus', 'C8B890', (-3.4, 4.6, 0.34), major_radius=0.5, minor_radius=0.13, major_segments=12, minor_segments=5, parent=r)
    add('cylinder', '2C6E92', (-5.0, 0.6, 0.6), radius=0.55, depth=1.2, vertices=10, parent=r)
    add('cube', '8A6A48', (2.6, 3.6, 0.4), rot=(0, 0, 0.3), scale=(1.1, 0.9, 0.8), size=1, parent=r)
    add('cylinder', '2A2E38', (2.9, 6.0, 3.0), radius=0.09, depth=6.0, vertices=6, parent=r)
    add('cube', '2A2E38', (2.3, 6.0, 5.9), scale=(1.3, 0.1, 0.1), size=1, parent=r)
    add('ico_sphere', 'FFE2A8', (1.7, 6.0, 5.65), radius=0.24, subdivisions=1, parent=r, emit=16)
    lamp = light((1.7, 5.8, 5.2), 420, 'FFD8A0', kind='POINT', parent=r)
    # the far side of the harbour: a low shore, a tall thin tower, a few lit windows, moored boats
    add('cube', '1C2838', (0, 170, 2), scale=(900, 16, 9), size=1, parent=r)
    add('cube', '26344A', (60, 168, 26), scale=(4.2, 4.2, 44), size=1, parent=r)
    add('cube', '26344A', (60, 168, 49), scale=(6.0, 6.0, 4), size=1, parent=r)
    for i in range(14):
        add('cube', 'FFD890', (-150 + i * 23 + (i % 3) * 5, 161.5, 3.5 + (i % 2) * 1.6), scale=(1.6, 0.2, 1.1), size=1, parent=r, emit=8)
    for x, y in ((24, 44), (-30, 70), (52, 96)):
        add('cube', 'E8E4D8', (x, y, -1.6), scale=(7, 2.4, 1.4), size=1, parent=r)
        add('cube', 'E8E4D8', (x + 1.2, y, -0.3), scale=(2.4, 1.8, 1.3), size=1, parent=r)
    glow = add('cube', 'FF9A50', (0, 420, 16), scale=(2400, 1, 34), size=1, parent=r, emit=2.2)
    aim = empty((0, 0, 1.9), r)
    keyl = light((5.5, -7, 5), 1500, 'FFE2B8', 3.0, aim, parent=r)
    rim = light((-7, 5, 6), 2200, 'FF7A1A', 1.8, aim, parent=r)
    light((-6, -6, 2.5), 320, '5E8FD0', 4.0, aim, parent=r)
    pick = empty((0, 0, -5))                              # a brass lobster gauge: the case's shiny object
    add('cube', BRASS, (0, 0, 0), scale=(0.62, 0.05, 0.17), size=1, parent=pick, rough=0.25, emit=1.1)
    for x in (-0.27, 0.27):
        add('cube', BRASS, (x, 0, -0.14), scale=(0.08, 0.05, 0.2), size=1, parent=pick, rough=0.25, emit=1.1)
    add('torus', BRASS, (0.36, 0, 0.0), rot=(PI / 2, 0, 0), major_radius=0.07, minor_radius=0.025, major_segments=8, minor_segments=4, parent=pick, emit=1.1)
    return dict(pick=pick, p_key=keyl, p_rim=rim, p_lamp=lamp, p_glow=glow)


def set_gullet(r):
    """Inside the whale's mouth, opened up a little for the camera: the tongue for a floor, a ribbed roof, baleen down both sides."""
    add('ico_sphere', '6E2436', (0, 0, 0.5), scale=(3.9, 7.6, 3.2), radius=1, subdivisions=3, parent=r)
    tongue = add('ico_sphere', 'D0708A', (0, 0.4, -1.0), scale=(3.0, 6.2, 1.0), radius=1, subdivisions=2, parent=r)
    roof = empty((0, 0, 0), r)
    for j in range(9):
        y = -5.2 + j * 1.3
        f = math.sqrt(max(0.05, 1 - (y / 7.4) ** 2))
        add('torus', ('9A3A52', 'A8455C')[j % 2], (0, y, 0.5), rot=(PI / 2, 0, 0), scale=(3.7 * f, 3.0 * f, 1.6), major_radius=1, minor_radius=0.045,
            major_segments=18, minor_segments=5, parent=roof)
    for s in (-1, 1):
        for j in range(26):
            y = -5.0 + j * 0.4
            x = 2.75 * math.sqrt(max(0.05, 1 - (y / 7.2) ** 2))
            add('cube', ('2B2622', '3A342C')[j % 2], (s * x, y, 1.25), rot=(0, s * -0.16, 0), scale=(0.08, 0.3, 2.1), size=1, parent=r)
            add('cube', 'B4A486', (s * (x - 0.17), y, 0.3), rot=(0, s * -0.16, 0), scale=(0.05, 0.3, 0.5), size=1, parent=r)
    add('ico_sphere', '2A0C16', (0, 6.3, 0.6), scale=(1.3, 0.6, 1.0), radius=1, subdivisions=2, parent=r)        # the throat: far too small
    glow = light((0, -1.2, 2.2), 260, 'FF7088', kind='POINT', parent=r)
    light((0, 3.5, 1.6), 90, 'B84870', kind='POINT', parent=r)
    return dict(g_tongue=tongue, g_roof=roof, g_glow=glow)


def set_ward(r):
    add('cube', 'CFC8B6', (0, 0.5, -0.1), scale=(13, 12, 0.2), size=1, parent=r)
    add('cube', 'E8ECE8', (0, 0.5, 5.6), scale=(13, 12, 0.2), size=1, parent=r)
    for x, w_ in ((-2.0, 8.4), (5.45, 1.7)):                 # back wall with a door gap
        add('cube', 'B4CEC8', (x, 6.1, 2.75), scale=(w_, 0.2, 5.5), size=1, parent=r)
    add('cube', 'B4CEC8', (3.4, 6.1, 4.95), scale=(2.4, 0.2, 1.1), size=1, parent=r)
    add('cube', 'F4EEDC', (3.4, 7.6, 2.4), scale=(5, 0.1, 5), size=1, parent=r, emit=1.5)
    add('cube', '7C8A8C', (3.4, 6.04, 4.44), scale=(2.6, 0.3, 0.12), size=1, parent=r)
    for x in (2.14, 4.66):
        add('cube', '7C8A8C', (x, 6.04, 2.2), scale=(0.12, 0.3, 4.4), size=1, parent=r)
    door = empty((4.6, 6.0, 0), r, (0, 0, 1.25))
    add('cube', 'C8A070', (-1.15, 0, 2.15), scale=(2.3, 0.1, 4.3), size=1, parent=door)
    add('cube', 'C8CCD4', (-2.0, -0.1, 2.1), scale=(0.3, 0.1, 0.08), size=1, parent=door)
    for sx in (-1, 1):
        add('cube', 'A8C4BE', (sx * 6.4, 0.5, 2.75), scale=(0.2, 12, 5.5), size=1, parent=r)
    add('cube', '8FB0AA', (0, 5.98, 0.5), scale=(13, 0.06, 1.0), size=1, parent=r)
    # the window: afternoon light
    add('cube', 'FFE2A0', (-3.2, 5.98, 3.2), scale=(3.4, 0.06, 2.3), size=1, parent=r, emit=2.4)
    add('cube', 'F4F2EA', (-3.2, 5.94, 3.2), scale=(0.1, 0.1, 2.3), size=1, parent=r)
    add('cube', 'F4F2EA', (-3.2, 5.94, 3.2), scale=(3.4, 0.1, 0.1), size=1, parent=r)
    add('cube', 'F4F2EA', (-3.2, 5.9, 1.98), scale=(3.8, 0.3, 0.12), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '5AA6A2', (-3.2 + sx * 2.1, 5.85, 3.1), scale=(0.7, 0.12, 3.2), size=1, parent=r)
    # the bed, lengthways toward the camera
    add('cube', 'C4CAD2', (-2.6, 2.6, 0.32), scale=(3.1, 6.1, 0.14), size=1, parent=r)
    for sx in (-1, 1):
        for y in (-0.3, 5.5):
            add('cylinder', '9AA0AC', (-2.6 + sx * 1.45, y, 0.14), radius=0.07, depth=0.3, vertices=6, parent=r)
    add('cube', 'F6F4EC', (-2.6, 2.6, 0.57), scale=(2.9, 5.9, 0.38), size=1, parent=r)
    add('cube', '9CC2D6', (-2.6, 3.0, 0.8), scale=(2.94, 2.6, 0.12), size=1, parent=r)
    add('cube', 'FFFFFF', (-2.6, 4.9, 0.9), rot=(0.2, 0, 0), scale=(2.0, 0.9, 0.34), size=1, parent=r)
    add('cube', 'C4CAD2', (-2.6, 5.62, 1.2), scale=(3.1, 0.12, 1.7), size=1, parent=r)
    add('cube', 'C4CAD2', (-2.6, -0.42, 0.75), scale=(3.1, 0.1, 0.7), size=1, parent=r)
    add('cube', 'F4EEDC', (-2.6, -0.5, 0.86), rot=(0.1, 0, 0), scale=(0.9, 0.05, 0.6), size=1, parent=r)             # the chart clipped to the foot of the bed
    # bedside table, monitor, a chair, a wall clock
    add('cube', 'D8D2C0', (-5.2, 4.9, 0.8), scale=(1.4, 1.3, 1.6), size=1, parent=r)
    add('cylinder', 'FF7A1A', (-5.2, 4.7, 1.8), radius=0.18, depth=0.36, vertices=8, parent=r)
    add('cylinder', '9AA0AC', (-0.2, 5.3, 1.6), radius=0.06, depth=3.2, vertices=6, parent=r)
    add('cube', '22262C', (-0.2, 5.2, 3.3), scale=(1.4, 0.2, 1.0), size=1, parent=r)
    add('cube', '0C2A22', (-0.2, 5.09, 3.3), scale=(1.24, 0.03, 0.84), size=1, parent=r, emit=0.6)
    for i in range(7):
        add('cube', '3DDC84', (-0.7 + i * 0.17, 5.07, 3.3 + (0.25 if i == 3 else -0.12 if i == 4 else 0)), scale=(0.17, 0.02, 0.05), size=1, parent=r, emit=7)
    add('cube', '5AA6A2', (5.3, 2.4, 0.7), scale=(1.4, 1.3, 0.14), size=1, parent=r)
    add('cube', '5AA6A2', (5.9, 2.4, 1.5), scale=(0.14, 1.3, 1.6), size=1, parent=r)
    for sx in (-1, 1):
        for y in (1.9, 2.9):
            add('cylinder', '9AA0AC', (5.3 + sx * 0.6, y, 0.33), radius=0.05, depth=0.66, vertices=5, parent=r)
    add('cylinder', 'F4F2EA', (0.9, 5.96, 4.4), rot=(PI / 2, 0, 0), radius=0.45, depth=0.06, vertices=14, parent=r, emit=0.4)
    add('cube', '22262C', (0.9, 5.9, 4.52), scale=(0.04, 0.04, 0.3), size=1, parent=r)
    add('cube', '22262C', (1.0, 5.9, 4.4), scale=(0.24, 0.04, 0.04), size=1, parent=r)
    add('cube', 'F4F8FF', (0, 0.5, 5.48), scale=(3.0, 1.2, 0.05), size=1, parent=r, emit=1.6)
    aim = empty((-1.5, 1.0, 1.4), r)
    light((0, 0.5, 5.2), 110, 'F4F8FF', kind='POINT', parent=r)
    light((-3.4, 5.2, 3.4), 650, 'FFD890', 2.6, aim, parent=r)
    light((3.4, 6.8, 2.6), 260, 'FFF0D0', 2.0, empty((2.5, 3, 1.5), r), parent=r)
    light((4, -5, 3), 140, 'CFE8F4', 4.0, aim, parent=r)
    return {}


def set_bay(r):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=64, y_subdivisions=64, size=300, location=ORG['bay'])
    sea = bpy.context.object
    sea.data.materials.append(K.mat('1C6F8E', 0.55))
    co = np.zeros(len(sea.data.vertices) * 3)
    sea.data.vertices.foreach_get('co', co)
    xy = co.reshape(-1, 3)[:, :2].copy()
    boat = make_boat(empty((0, 0, -80), r))
    # the outer Cape: a long low strip of dune with beach grass, a white lighthouse and a keeper's shed
    add('cube', 'E0D09A', (0, 210, 2.5), scale=(900, 40, 7), size=1, parent=r)
    R = np.random.RandomState(5)
    for i in range(22):
        x = -260 + i * 25 + R.uniform(-8, 8)
        add('ico_sphere', ('E6D8A6', 'D4C48C')[i % 2], (x, 200 + R.uniform(-6, 6), 6), scale=(R.uniform(16, 30), 12, R.uniform(3, 7)), radius=1, subdivisions=1, parent=r)
        add('ico_sphere', ('7A9A52', '668848')[i % 2], (x + 6, 203, 9 + R.uniform(0, 3)), scale=(R.uniform(8, 16), 8, 2.2), radius=1, subdivisions=1, parent=r)
    add('cylinder', 'F6F4EC', (-46, 200, 22), radius=3.0, depth=26, vertices=8, parent=r)
    add('cylinder', '22262C', (-46, 200, 36.4), radius=3.6, depth=0.7, vertices=8, parent=r)
    add('cylinder', 'FFF2C0', (-46, 200, 38.2), radius=2.2, depth=3.0, vertices=8, parent=r, emit=4)
    add('cone', '22262C', (-46, 200, 41.0), radius1=2.8, radius2=0.2, depth=2.6, vertices=8, parent=r)
    add('cube', 'F6F4EC', (-36, 201, 12), scale=(9, 7, 6), size=1, parent=r)
    add('cube', 'A8442C', (-36, 201, 15.6), scale=(10, 8, 1.4), size=1, parent=r)
    for i in range(7):                                    # fair-weather clouds
        add('ico_sphere', 'FFFFFF', (-200 + i * 70 + R.uniform(-20, 20), 380, 70 + R.uniform(-12, 26)), scale=(R.uniform(26, 44), 10, R.uniform(7, 12)),
            radius=1, subdivisions=1, parent=r, emit=0.9)
    aim = empty((0, 10, 3), r)
    sun = light((-70, -80, 90), 300000, 'FFF4D8', 40.0, aim, parent=r)
    light((60, -40, 20), 40000, '9AD0E8', 30.0, aim, parent=r)
    return dict(sea=sea, xy=xy, boat=boat, b_sun=sun)


# ---------------------------------------------------------------- build / reset / finish
PEOPLE = ('pack', 'mike', 'mayo')
NFISH, NDROP = 72, 60


def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('sand', set_sand), ('pier', set_pier), ('gullet', set_gullet), ('ward', set_ward), ('bay', set_bay)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['pack'] = K.Rig(SUIT, scuba_head)
    kit_up(S['pack'])
    S['mike'] = K.Rig(GOWN, person_head('D9A888', '9A9690'))
    S['mayo'] = K.Rig(CREW, person_head('C99672', '4A3A2C'))
    add('cylinder', '2C6E92', (0, 0.0, 0.3), radius=0.31, depth=0.14, vertices=8, parent=S['mayo'].head)          # cap
    add('cube', '2C6E92', (0, -0.33, 0.25), scale=(0.44, 0.3, 0.05), size=1, parent=S['mayo'].head)
    for s in (-1, 1):                                    # bib straps of the orange oilskins
        add('cube', 'E8761E', (s * 0.17, -0.33, 0.62), scale=(0.1, 0.05, 0.9), size=1, parent=S['mayo'].body)
    add('cube', 'E8761E', (0, -0.34, 0.3), scale=(0.56, 0.05, 0.5), size=1, parent=S['mayo'].body)
    S['wh'] = make_whale()
    S['hand'] = K.Hand('2C3948', '1F2A36', 1.0)
    S['drops'] = [add('ico_sphere', 'E8FBFF', FAR, radius=0.08, subdivisions=1, emit=1.3) for _ in range(NDROP)]
    S['fish'] = [add('ico_sphere', ('7E9CB0', 'A4BCC8', '6A8A9E')[i % 3], FAR, scale=(0.18, 1.5, 0.3), radius=0.26, subdivisions=1, rough=0.3)
                 for i in range(NFISH)]
    S['frand'] = np.random.RandomState(4).uniform(-1, 1, (NFISH, 3))
    lant = empty(FAR)                                    # Rook's storm lantern
    add('cylinder', BRASS, (0, 0, 0.0), radius=0.14, depth=0.06, vertices=8, parent=lant, rough=0.3)
    add('cylinder', 'FFE2A0', (0, 0, 0.17), radius=0.09, depth=0.26, vertices=6, parent=lant, emit=18)
    add('cone', BRASS, (0, 0, 0.36), radius1=0.15, radius2=0.03, depth=0.12, vertices=8, parent=lant, rough=0.3)
    add('torus', BRASS, (0, 0, 0.5), rot=(PI / 2, 0, 0), major_radius=0.1, minor_radius=0.015, major_segments=8, minor_segments=4, parent=lant)
    S['lant'], S['lantl'] = lant, light((0, -0.1, 0.25), 0, 'FFC878', kind='POINT', parent=lant)
    S['kwa'], S['kca'] = empty(), empty()
    S['kw'] = light((0, 0, 0), 0, 'FFDCB8', 4.0, S['kwa'])
    S['kc'] = light((0, 0, 0), 0, '9AE4E0', 5.0, S['kca'])
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 1500
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    sc.world = w
    S['bg'] = w.node_tree.nodes['Background']
    return S


def sky(S, col, strength=1.0):
    S['bg'].inputs[0].default_value = K.hexc(col)
    S['bg'].inputs[1].default_value = strength


def show(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: at(name, x, y, z)


def cam(S, pos, look, lens=50, roll=0.0):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


def key(S, which, pos, look, energy):
    """Move one of the two free key lights (kw warm, kc cool) onto this shot's subject."""
    S[which].location, S[which + 'a'].location = pos, look
    S[which].data.energy = energy


def reset(S):
    for who in ('rook',) + PEOPLE:
        S[who].place(FAR)
        S[who].apply(P())
    for o in S['drops'] + S['fish']:
        o.location = FAR
    for o in S['drops']:
        o.scale = (1, 1, 1)
    S['face'] = dict(rook='calm', pack='calm', mike='calm', mayo='calm')
    S['hat_tip'], S['helm'], S['hat'] = 0.0, False, None
    for kk in ('kw', 'kc'):
        S[kk].data.energy = 0
    S['wh']['root'].location, S['wh']['root'].rotation_euler = FAR, (0, 0, 0)
    S['hand'].place(FAR)
    S['lant'].location, S['lantl'].data.energy = FAR, 0
    S['lob']['root'].location, S['lob']['root'].rotation_euler = (0, 0, -30), (0, 0, 0)
    S['s_sun'].data.energy, S['s_fill'].data.energy, S['s_rim'].data.energy = 6000, 1200, 1800
    S['p_key'].data.energy, S['p_rim'].data.energy, S['p_lamp'].data.energy = 1500, 2200, 420
    S['p_key'].data.color = K.hexc('FFE2B8')[:3]
    S['p_glow'].hide_render = False
    S['g_roof'].scale, S['g_tongue'].scale, S['g_glow'].data.energy = (1, 1, 1), (3.0, 6.2, 1.0), 260
    S['boat'].location, S['boat'].rotation_euler = (0, 0, -80), (0, 0, 0)
    S['b_sun'].data.energy = 300000
    S['pick'].location = FAR
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking, hat, helmet and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.43) % 1 < 0.035
    ez = dict(calm=0.07, smirk=0.045, deadpan=0.045, shocked=0.13, laugh=0.03, sad=0.055, warm=0.06).get(e, 0.07)
    tilt = dict(smirk=-0.5, deadpan=-0.05, shocked=0.35, laugh=0.3, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + (s * tilt if e != 'smirk' or s > 0 else 0.1), s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip = S['hat_tip']
    if S['hat'] == 'chest':                              # hat held against his chest
        r['hat'].location, r['hat'].rotation_euler = (0.0, -0.52, -0.95), (1.25, 0.0, 0.0)
    else:
        fly = S['hat'] or 0.0
        r['hat'].location = (0, 0, 0.27 + (0.11 if e == 'shocked' else 0.0) + tip * 0.1 + fly)
        r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.14, sad=0.22).get(e, 0.0) + tip * 0.35 + fly * 0.8, 0.07, fly * 2.0)
    for o in r['helmet']:
        o.hide_render = not S['helm']
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e in ('shocked', 'laugh') else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for who in PEOPLE:
        e = S['face'][who]
        x = S[who].extra
        kk = dict(scared=1.3, shock=1.7, calm=1.0, sad=0.6, happy=0.85, closed=0.08, tired=0.5).get(e, 1.0)
        for ey in x['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], x['eye0'] * kk)
        if 'jaw' in x:
            x['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
            x['jaw'].location.z = -0.13 - (0.05 if e == 'shock' else 0.0)


# ---------------------------------------------------------------- helpers: water, whale, fish, spray
def water(S, mode='day'):
    """Shows the sea floor. day = sunlit green shallows; dim = something very large is between him and the sun."""
    A = show(S, 'sand')
    if mode == 'day':
        sky(S, '1F8A88', 1.0)
    else:
        sky(S, '125C5E', 1.0)
        S['s_sun'].data.energy, S['s_rim'].data.energy = 2400, 700
    return A


def whale(S, loc, yaw=0.0, pitch=0.0, roll=0.0, gape=0.0, t=0.0, beat=1.0):
    W = S['wh']
    W['root'].location, W['root'].rotation_euler = loc, (pitch, roll, yaw)
    W['up'].rotation_euler = (-0.3 * gape, 0, 0)
    W['lo'].rotation_euler = (0.8 * gape, 0, 0)
    W['tl'].rotation_euler = (0.2 * math.sin(t * 3.0 * beat), 0, 0)
    W['fk'].rotation_euler = (0.3 * math.sin(t * 3.0 * beat - 0.9), 0, 0)
    for i, s in enumerate((-1, 1)):
        W['fl'][i].rotation_euler = (0, s * (0.35 + 0.2 * math.sin(t * 1.7 * beat)), s * -0.45)


def wpt(S, x, y, z):
    """World position of a point given in the whale's own coordinates (head at -Y, lips near y = -6)."""
    bpy.context.view_layer.update()
    return tuple(S['wh']['w'].matrix_world @ Vector((x, y, z)))


def in_mouth(S, t, out=0.6, face='scared', side=0.25):
    """The diver lies along the whale's mouth, head inside, fins toward the lips. out = how far his legs stick out."""
    bpy.context.view_layer.update()
    M = S['wh']['w'].matrix_world
    S['pack'].root.location = M @ Vector((side, -4.6 - out, -0.2))
    S['pack'].root.rotation_euler = (M.to_3x3().normalized() @ Euler((PI / 2, 0, PI)).to_matrix()).to_euler('XYZ')
    s = math.sin(t * 9)
    S['pack'].apply(P('stand', lL=(0.45 * s, 0.35), lR=(-0.45 * s, 0.35), aL=(0.6, 0.5, 0.8), aR=(0.5, 0.5, 0.9)))
    S['face']['pack'] = face


def head_of(S, who):
    bpy.context.view_layer.update()
    return tuple(S[who].head.matrix_world.translation)


def bub(S, org, t, n=8, start=0, spread=0.35, height=3.2, speed=1.5, seed=0, size=1.0):
    """A column of bubbles rising from org."""
    for i in range(n):
        b = S['drops'][start + i]
        u = (t * speed / height + (i * 0.618 + seed * 0.37) % 1) % 1
        a = i * 2.4 + seed
        rr = spread * (0.3 + 0.7 * ((i * 0.37) % 1)) * (0.4 + u)
        b.location = (org[0] + math.cos(a + t) * rr, org[1] + math.sin(a + t) * rr * 0.7, org[2] + u * height)
        s = size * (0.5 + ((i * 0.73) % 1)) * (0.6 + 0.7 * u)
        b.scale = (s, s, s)


def burst(S, org, k, n=14, start=0, r=1.6, seed=0, size=1.5, up=1.0):
    """Bubbles thrown outward from org."""
    for i in range(n):
        b = S['drops'][start + i]
        a, e = i * 2.4 + seed, ((i * 0.61) % 1) * 1.4 - 0.2
        d = r * (0.3 + 0.7 * ((i * 0.37) % 1)) * (1 - (1 - k) ** 2)
        b.location = (org[0] + math.cos(a) * math.cos(e) * d, org[1] + math.sin(a) * math.cos(e) * d, org[2] + math.sin(e) * d + 1.6 * k * up)
        s = size * (0.6 + ((i * 0.73) % 1)) * (1 - 0.6 * k)
        b.scale = (s, s, s)


def spray(S, org, k, n=20, start=0, r=5.0, h=6.0, seed=0, size=2.6):
    """White water thrown up from the surface and falling back."""
    k = max(0.0, min(1.0, k))
    for i in range(n):
        b = S['drops'][start + i]
        a = i * 2.4 + seed
        f, g = (i * 0.37) % 1, (i * 0.61) % 1
        u = min(1.0, k * (0.8 + 0.5 * g))
        b.location = (org[0] + math.cos(a) * r * (0.25 + 0.75 * f) * u, org[1] + math.sin(a) * r * (0.25 + 0.75 * f) * u,
                      org[2] + h * (0.4 + 0.6 * g) * 4 * u * (1 - u))
        s = size * (0.6 + f) * (1 - 0.5 * u)
        b.scale = (s, s, s)


def shoal(S, c, t, n=40, start=0, spread=(3, 3, 1.5), yaw=0.0, speed=4.0, run=10.0, scale=1.0):
    """Sand lance: a stream of silver slivers heading the way yaw points (yaw 0 = toward -Y)."""
    dx, dy = math.sin(yaw), -math.cos(yaw)
    for i in range(n):
        f, r = S['fish'][start + i], S['frand'][start + i]
        u = ((t * speed + i * 1.37) % run) - run / 2
        f.location = (c[0] + r[0] * spread[0] + dx * u, c[1] + r[1] * spread[1] + dy * u, c[2] + r[2] * spread[2] + 0.15 * math.sin(t * 6 + i))
        f.rotation_euler = (0, 0, yaw + 0.3 * math.sin(t * 11 + i))
        f.scale = (0.18 * scale, 1.5 * scale, 0.3 * scale)


def uw(S, who, loc, yaw, pose, t, pitch=0.0, roll=0.0, face=None, ph=0.0):
    """Place someone under water with a slow bob so nobody hangs dead still."""
    S[who].place((loc[0], loc[1], loc[2] + 0.05 * math.sin(t * 1.6 + ph)), yaw, pitch + 0.02 * math.sin(t * 1.2 + ph), roll)
    S[who].apply(pose)
    if face:
        S['face'][who] = face


def rook_uw(S, loc, yaw, pose, expr, t, bubbles=True, pitch=0.0):
    uw(S, 'rook', loc, yaw, pose, t, pitch=pitch, ph=1.3)
    S['face']['rook'] = expr
    S['helm'] = True
    if bubbles:
        h = head_of(S, 'rook')
        bub(S, (h[0], h[1], h[2] + 0.7), t, 5, NDROP - 6, 0.2, 2.6, 1.3, seed=3, size=0.7)


def swell(x, y, t, rough=0.6):
    return rough * (0.7 * math.sin(x * 0.11 + t * 1.3) + 0.4 * math.sin(y * 0.19 - t * 1.7 + x * 0.05) + 0.2 * math.sin((x - y) * 0.4 + t * 2.6))


def bay(S, t, rough=0.6, skycol='8CCBE6'):
    A = show(S, 'bay')
    xy = S['xy']
    z = rough * (0.7 * np.sin(xy[:, 0] * 0.11 + t * 1.3) + 0.4 * np.sin(xy[:, 1] * 0.19 - t * 1.7 + xy[:, 0] * 0.05)
                 + 0.2 * np.sin((xy[:, 0] - xy[:, 1]) * 0.4 + t * 2.6))
    S['sea'].data.vertices.foreach_set('co', np.column_stack([xy, z]).ravel())
    S['sea'].data.update()
    sky(S, skycol, 1.0)
    return A


def boat_at(S, x, y, yaw, t, rough=0.6):
    S['boat'].location = (x, y, -0.55 + 0.6 * swell(x, y, t, rough))
    S['boat'].rotation_euler = (0.05 * math.sin(t * 1.4), 0.03 * math.sin(t * 1.1 + 1), yaw)


def onboat(S, x, y, z):
    bpy.context.view_layer.update()
    return tuple(S['boat'].matrix_world @ Vector((x, y, z)))


def crew(S, who, bx, by, rel, pose, face=None):
    """Stand someone on the work deck. rel 0 = facing the bow."""
    S[who].place(onboat(S, bx, by, 2.05), S['boat'].rotation_euler[2] + PI / 2 + rel)
    S[who].apply(pose)
    if face:
        S['face'][who] = face


# ---------------------------------------------------------------- shots: hook
def gulp(S, k, t, lt):
    """From behind him, a mouth the size of a garage door."""
    A = water(S, 'dim')
    e = ease(k)
    wy = lerp(11.0, 3.4, e)
    g = 1.0 if k < 0.6 else lerp(1.0, 0.1, ease((k - 0.6) / 0.32))
    whale(S, A(0.2, wy, 3.5), 0.0, 0.05, 0.0, g, t, 1.6)
    if wy - 4.3 > 0.6:
        turn = ease((k - 0.1) / 0.3)
        uw(S, 'pack', A(0, 0.3, 1.5), 0.3, blend(P('stand', aL=(0.9, 0.3, 0.9), aR=(0.9, 0.3, 0.9), lL=(0.3, 0.5), lR=(-0.2, 0.6), head=(0.1, 0)),
                                                P('up', aL=(2.2, 0.8, 0.5), aR=(2.0, 0.9, 0.6), lL=(0.7, 0.6), lR=(-0.3, 0.9), head=(-0.2, 1.1)), turn), t, face='shock')
        bub(S, A(0, 0.3, 4.6), t, 6, 0, 0.3, 4.0, 2.2, size=1.3)
    else:
        in_mouth(S, t, 0.9, 'shock')
        burst(S, wpt(S, 0, -5.5, 0), ease((k - 0.6) / 0.4), 16, 0, 2.4, seed=2, size=1.6)
    shoal(S, A(-0.5, -2.0 - 6 * e, 3.0), t, 34, 0, (3.4, 2.5, 1.8), -0.5, 7.0, 9.0)
    key(S, 'kw', A(-6, -8, 2.5), A(0, 1, 3), 2600)
    key(S, 'kc', A(7, -6, 6), A(0, 3, 3.5), 2000)
    cam(S, A(lerp(-7.2, -6.4, k), lerp(-5.6, -4.8, k), 1.4), A(0.2, lerp(4.2, 2.6, k), 3.6), 20, 0.04 * math.sin(t * 21))


def jaws_shut(S, k, t, lt):
    """The jaws close. Two yellow fins are all that is left outside."""
    A = water(S, 'dim')
    g = lerp(0.6, 0.05, ease(lt / 0.32))
    whale(S, A(lerp(0.6, 0.0, k), lerp(5.2, 3.6, k), 3.4), 0.55, 0.03, 0.0, g, t, 1.2)
    in_mouth(S, t, 1.55, 'shock')
    tip = wpt(S, 0, -6.0, -0.1)
    burst(S, tip, min(1.0, lt / 0.9), 20, 0, 2.6, seed=4, size=1.5)
    key(S, 'kw', A(-1, -8, 2.2), tip, 3200)
    key(S, 'kc', A(8, -4, 6), tip, 3000)
    cam(S, A(lerp(-0.2, 0.4, k), lerp(-8.2, -7.4, k), 2.3), (tip[0] + 0.6, tip[1] + 0.8, tip[2] + 0.3), 36, 0.05 * math.sin(t * 26))


def whale_wide(S, k, t, lt):
    """Seen from the sand: the whale passes overhead against the bright surface."""
    A = water(S, 'day')
    whale(S, A(lerp(4.0, -1.5, k), lerp(11.0, 2.0, k), 9.2), 0.5, 0.0, 0.08 * math.sin(t * 2), 0.04, t, 1.2)
    in_mouth(S, t, 1.55, 'scared')
    bub(S, wpt(S, 0, -6.2, 0), t, 10, 0, 0.5, 6.0, 3.0, size=1.6)
    shoal(S, A(-3, -1, 4.5), t, 30, 0, (4, 3, 1.5), 1.2, 5.0, 12.0)
    key(S, 'kc', A(-6, -8, 1), A(0, 5, 9), 3000)
    cam(S, A(lerp(7.0, 6.2, k), lerp(-6.8, -6.0, k), 0.7), A(lerp(1.5, 0.0, k), 4.5, 7.6), 21, 0.03 * math.sin(t * 1.3))


def spat(S, k, t, lt):
    """The cold open's promise: the whale stands on its tail in white water and throws him clear."""
    A = bay(S, t, 0.5)
    boat_at(S, -17, 26, 0.5, t)
    crew(S, 'mayo', -4.5, -1.2, 2.2, P('up', aL=(2.4, 0.7, 0.6), aR=(2.4, 0.7, 0.6)), 'shock')
    g = lerp(0.25, 1.0, ease(lt / 0.3))
    rise = ease(lt / 0.35)
    whale(S, A(0.6, 2.0, lerp(-3.5, 2.0, rise)), PI / 2, -PI / 2 + 0.12, 0.12 * math.sin(t * 9), g, t, 2.0)
    j = max(0.0, min(1.0, (lt - 0.15) / 1.3))
    S['pack'].place(A(lerp(0.2, -3.4, j), lerp(1.6, 0.6, j), lerp(4.6, 10.5, 1 - (1 - j) ** 2)), 0.6 + lt * 2.2, 0.9 + lt * 4.0)
    S['pack'].apply(P('up', aL=(2.3, 0.9, 0.5), aR=(2.0, 1.0, 0.7), lL=(0.7, 0.9), lR=(-0.4, 0.6)))
    S['face']['pack'] = 'shock'
    spray(S, A(0.6, 2.0, 0.3), min(1.0, lt / 1.5), 34, 0, 6.0, 7.5, seed=1)
    spray(S, A(0.2, 1.5, 4.5), j, 14, 34, 2.4, 3.0, seed=6, size=1.8)
    cam(S, A(lerp(-2.0, -1.4, k), lerp(-12.5, -11.5, k), 1.2), A(-0.9, 2, lerp(5.0, 5.8, k)), 24, 0.04 * math.sin(t * 15))


# ---------------------------------------------------------------- shots: Rook takes the case
def pier(S, dusk=False):
    A = show(S, 'pier')
    if dusk:
        sky(S, '5A4258', 1.0)
        S['p_key'].data.color = K.hexc('FFA050')[:3]
        S['p_key'].data.energy, S['p_rim'].data.energy = 3200, 3400
    else:
        sky(S, '1A2740', 1.0)
    return A


def rook_dock(S, k, t, lt):
    A = pier(S)
    S['rook'].place(A(0, 0, 0), 0.3)
    S['rook'].apply(P('cross', head=(0.05, -0.2 + 0.26 * math.sin(t * 4.6) * max(0, 1 - lt / 0.9))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(2.9, 2.2, k), lerp(-6.4, -5.2, k), 1.9), A(0.2, 0, 2.05), 36)


def rook_dive(S, k, t, lt):
    """Collar up, helmet on, and over the side."""
    A = pier(S)
    u = k * 1.45
    e = ease((u - 0.3) / 0.55)
    j = max(0.0, (u - 0.85) / 0.5)
    x = lerp(0.6, 3.3, e) + 2.4 * min(j, 1.3)
    z = 1.8 * math.sin(PI * j) if j < 1 else -5.0 * (j - 1)
    S['rook'].place(A(x, 0.4, z), PI / 2 if u > 0.3 else 0.2)
    pop = math.sin(PI * ease(u / 0.3)) if u < 0.3 else 0
    pose = walk(t, 2.2) if 0.3 < u < 0.85 else P('stand')
    if j > 0:
        pose = P('up', aL=(2.6, 0.5, 0.3), aR=(2.6, 0.5, 0.3), lL=(0.9, 1.3), lR=(0.7, 1.1), head=(-0.1, 0))
    S['rook'].apply(blend(pose, P('stand', aL=(0.5, 0.5, 2.3, 0.4), aR=(0.5, 0.5, 2.3, 0.4), head=(0.1, 0)), pop))
    S['face']['rook'] = 'smirk'
    S['helm'] = u > 0.25
    key(S, 'kw', A(x - 2.5, -5, 3.5), A(x, 0.4, 2), 900)
    cam(S, A(lerp(0.4, 2.4, k), -5.8, 2.0), A(x - 0.3, 0.5, lerp(2.1, 1.8, k)), 30)


# ---------------------------------------------------------------- shots: the job
def boat_wide(S, k, t, lt):
    """A calm bright morning off the Cape. Rook rides the wheelhouse roof."""
    A = bay(S, t, 0.5)
    boat_at(S, lerp(1.5, -0.5, k), 19, 2.55, t)
    S['rook'].place(onboat(S, 2.4, -0.3, 5.4), 0.25)
    S['rook'].apply(P('hat', aL=(0.3, 0.5, 1.2), head=(0.05, 0.3 * math.sin(t * 1.3))))
    S['face']['rook'] = 'calm'
    crew(S, 'mayo', -1.6, -1.3, 2.4, P('stand', aL=(1.0, 0.2, 0.9), aR=(1.0, 0.2, 0.9), head=(0.1, 0.2 * math.sin(t * 2))))
    crew(S, 'pack', -5.9, 0.6, 2.9, P('stand', aL=(0.5, 0.3, 1.6), aR=(1.9, 0.4, 1.9, 0.5), head=(0.1, 0.0)))
    cam(S, A(lerp(13.0, 11.5, k), lerp(-6.0, -4.5, k), lerp(2.0, 2.6, k)), A(0.5, 19, 4.4), 40, 0.015 * math.sin(t * 0.9))


def descend(S, k, t, lt):
    """Down through the green: he fins for the bottom, Rook paddling after him."""
    A = water(S, 'day')
    z = lerp(15.5, 12.0, k)
    s = math.sin(t * 7)
    uw(S, 'pack', A(0.4, lerp(4.5, 2.6, k), z + 1.8), 0.25, P('stand', aL=(0.25, 0.2, 0.3), aR=(0.3, 0.25, 0.4), lL=(0.4 * s, 0.3), lR=(-0.4 * s, 0.3), head=(-0.5, 0)), t,
       pitch=PI / 2 + 0.75, face='calm')
    bub(S, head_of(S, 'pack'), t, 9, 0, 0.3, 6.0, 2.6, size=1.4)
    rook_uw(S, A(3.0, lerp(6.6, 5.2, k), z + 2.4), 0.5, P('swim', aL=(1.7 + 0.8 * math.sin(t * 5), 0.8, 0.5), aR=(1.7 - 0.8 * math.sin(t * 5), 0.8, 0.5),
                                                         lL=(0.5 * s, 0.6), lR=(-0.5 * s, 0.6), head=(-0.6, -0.2)), 'calm', t, pitch=1.0)
    shoal(S, A(-4, 0, z - 2), t, 26, 0, (3, 5, 2), 1.4, 3.5, 12.0)
    key(S, 'kw', A(4, -8, z - 3), A(1.2, 4, z + 1), 2500)
    key(S, 'kc', A(-6, -6, z + 5), A(1.2, 4, z + 1), 6000)
    cam(S, A(lerp(-2.6, -2.0, k), lerp(-5.6, -5.0, k), z - 2.6), A(1.5, 4.0, z + 1.6), 27, 0.03 * math.sin(t * 1.1))


def hunter(S, A, t, reach=1.0):
    """He crouches at the rock pile, one arm under the ledge."""
    s = math.sin(t * 2.6)
    uw(S, 'pack', A(0.75, 0.25, 0.0), 2.05, P('stand', lL=(1.0, 1.5), lR=(0.5, 1.6), lift=-0.52, lean=0.55, aL=(0.5, 0.3, 0.9),
                                              aR=(1.05 + 0.25 * reach + 0.06 * s, 0.1, 0.25), head=(-0.3, 0.1 * s)), t)
    bub(S, head_of(S, 'pack'), t, 7, 0, 0.3, 5.0, 1.9, size=1.3)


def sand_hunt(S, k, t, lt):
    A = water(S, 'day')
    hunter(S, A, t, ease(k))
    S['lob']['root'].location, S['lob']['root'].rotation_euler = A(2.0, 0.9, 0.02), (0, 0, 1.15)
    rook_uw(S, A(-1.5, -1.9, 0), 0.75, P('stand', aR=(1.9, 0.35, 2.3, 0.6), aL=(0.2, 0.2, 0.4), head=(0.05, -0.35)), 'calm', t)
    shoal(S, A(-6, 7, 3.4), t, 24, 0, (4, 3, 1.2), 1.57, 3.0, 14.0)
    key(S, 'kw', A(-5, -6, 3), A(-1.5, -1.9, 2), 1400)
    cam(S, A(lerp(-1.2, -0.6, k), lerp(-9.0, -8.0, k), 2.2), A(0.6, 0.8, 2.0), 30)


def lobster_cu(S, k, t, lt):
    """Close: the lobster backs under its ledge, claws up, as a gloved hand comes in."""
    A = water(S, 'day')
    e = ease(k)
    L = S['lob']
    L['root'].location = A(lerp(1.75, 2.2, e), lerp(0.7, 1.1, e), 0.03)
    L['root'].rotation_euler = (-0.25 * e, 0, 1.2 + 0.08 * math.sin(t * 14))
    for i, s in enumerate((-1, 1)):
        L['claws'][i].rotation_euler = (-0.5 * e - 0.15 * math.sin(t * 10 + i), 0, s * 0.3 * e)
    S['hand'].place(A(lerp(0.75, 1.25, e), lerp(-0.45, 0.1, e), lerp(0.95, 0.7, e)), (0.25, 0.0, PI - 0.8))
    S['hand'].grip(0.15 + 0.3 * e)
    bub(S, A(0.9, 0.2, 1.2), t, 5, 0, 0.3, 3.0, 1.7, size=0.8)
    key(S, 'kw', A(0.5, -2.5, 2.0), A(2.6, 1.4, 0.4), 900)
    cam(S, A(lerp(0.2, 0.5, k), lerp(-3.0, -2.6, k), 1.25), A(1.75, 0.7, 0.45), 36, 0.02 * math.sin(t * 2))


def shoal_(S, k, t, lt):
    """Sand lance pour past Rook. Then the light goes."""
    d = ease((k - 0.45) / 0.4)
    A = water(S, 'day')
    S['s_sun'].data.energy = lerp(6000, 2000, d)
    sky(S, '1F8A88' if d < 0.5 else '14605F')
    rook_uw(S, A(-0.6, -1.0, 0), 0.2, blend(P('stand', aL=(0.4, 0.5, 0.8), aR=(0.4, 0.5, 0.8), head=(0.0, -0.5 + 1.0 * min(1, lt / 0.7))),
                                             P('stand', aL=(0.7, 0.8, 1.0), aR=(0.7, 0.8, 1.0), head=(-0.55, 0.3)), d), 'shocked' if d > 0.5 else 'calm', t)
    shoal(S, A(-0.6, -1.4, 2.4), t, 62, 0, (5.5, 2.4, 1.7), -PI / 2, 9.0, 16.0)
    key(S, 'kw', A(3, -6, 3), A(-0.6, -1.0, 2.2), lerp(1200, 2200, d))
    cam(S, A(lerp(0.4, -0.1, k), lerp(-7.6, -6.6, k), 2.0), A(-0.6, -1.0, 2.35), 34)


# ---------------------------------------------------------------- shots: the hit
def shadow(S, k, t, lt):
    """He is busy with his catch bag. Behind him the water turns into a whale. Rook sees it first."""
    A = water(S, 'dim')
    e = ease(k)
    whale(S, A(2.6, lerp(22, 9.5, e), 4.9), -0.12, 0.04, 0.0, lerp(0.25, 1.0, e), t, 1.5)
    s = math.sin(t * 4)
    uw(S, 'pack', A(0.6, 0.6, 1.2), 0.25, P('stand', aL=(0.9, 0.2, 1.3), aR=(1.0 + 0.1 * s, 0.15, 1.4), lL=(0.3, 0.5), lR=(-0.2, 0.6), head=(0.35, 0.15)), t, face='calm')
    bub(S, head_of(S, 'pack'), t, 6, 0, 0.3, 4.0, 1.9, size=1.2)
    rook_uw(S, A(-1.8, -0.4, 0.2), 2.5, P('point', aR=(1.75, 0.2, 0.05), aL=(0.6, 0.9, 1.2), head=(-0.2, 1.3)), 'shocked', t, bubbles=False)
    shoal(S, A(0.5, 9 - 9 * e, 3.6), t, 40, 0, (4.5, 4, 2), 0.0, 8.0, 12.0)
    key(S, 'kw', A(-1, -7, 2.5), A(-0.6, 0, 2.4), 2400)
    key(S, 'kc', A(-9, 2, 7), A(2.5, 10, 4), 3500)
    cam(S, A(lerp(1.7, 1.3, k), lerp(-8.2, -7.4, k), 1.7), A(-0.6, 2.0, lerp(2.9, 3.2, k)), 28, 0.02 * math.sin(t * 9))


def gullet(S, t, heave=0.0):
    A = show(S, 'gullet')
    sky(S, '000000')
    b = 0.5 + 0.5 * math.sin(t * 5.2)
    S['g_roof'].scale = (1, 1, 1 - heave * 0.2 * b)
    S['g_tongue'].scale = (3.0, 6.2, 1.0 + heave * 0.22 * math.sin(t * 5.2 + 1.2))
    return A


def trapped(S, A, t, push=0.0, face='scared', rest=False):
    """He lies back on the tongue, knees up, shoving at the roof."""
    s = math.sin(t * 6.0)
    S['pack'].place(A(0.75, 0.9, -0.5 + 0.05 * math.sin(t * 5.2 + 1.2)), 0.45, -0.5)
    S['pack'].apply(P('sit', lL=(1.7 + 0.2 * push * s, 1.2), lR=(1.5 - 0.2 * push * s, 1.4), lift=-0.5, lean=0.1,
                      aL=(lerp(0.8, 2.3, push) + 0.15 * s, 0.5, lerp(1.4, 0.5, push)), aR=(lerp(0.9, 2.5, push) - 0.15 * s, 0.4, lerp(1.3, 0.4, push)),
                      head=(-0.2 * push, 0.25 * s)))
    if rest:
        S['pack'].apply(P('sit', lL=(1.7, 1.2), lR=(1.5, 1.4), lift=-0.5, lean=0.1, aL=(0.15, 0.5, 0.6), aR=(0.1, 0.5, 0.7), head=(0.0, 0.2 * s)))
    S['face']['pack'] = face
    h = head_of(S, 'pack')
    bub(S, (h[0], h[1] - 0.3, h[2]), t, 7, 0, 0.25, 1.7, 1.5, size=0.8)


def lantern(S, A, x, y, z, e=110):
    S['lant'].location, S['lantl'].data.energy = A(x, y, z), e


def rook_in(S, A, t, pose, expr):
    S['rook'].place(A(-1.7, -0.5, -0.5 + 0.05 * math.sin(t * 5.2)), 0.55, -0.12)
    S['rook'].apply(pose)
    S['face']['rook'], S['helm'] = expr, True


def feel_dark(S, k, t, lt):
    """His glove finds baleen where a shark would have teeth."""
    A = gullet(S, t, 0.5)
    e = ease(k)
    S['hand'].place(A(lerp(1.5, 2.25, ease(lt / 0.4)), lerp(-0.9, 0.5, e), lerp(1.2, 1.6, e)), (0.25, 1.0, PI / 2 + 0.2))
    S['hand'].grip(0.1 + 0.1 * math.sin(t * 6))
    bub(S, A(1.6, -0.3, 0.6), t, 6, 0, 0.3, 2.2, 1.4, size=0.8)
    key(S, 'kw', A(0.2, -2.6, 1.8), A(2.6, 0, 1.4), 320)
    cam(S, A(lerp(0.1, 0.4, k), lerp(-2.9, -2.5, k), 1.45), A(2.5, lerp(-0.2, 0.3, k), 1.4), 30, 0.03 * math.sin(t * 5))


def mouth_wide(S, k, t, lt):
    """Inside the mouth: one man, one tank of air, and a crow with a lantern who has stopped joking."""
    A = gullet(S, t, 1.0)
    trapped(S, A, t, 0.5)
    rook_in(S, A, t, P('sit', lift=-0.5, lean=0.2, aL=(0.6, 0.2, 1.3), aR=(1.3, 0.3, 0.9), head=(0.1, -0.55)), 'sad')
    lantern(S, A, -1.2, -1.45, 0.55)
    cam(S, A(lerp(0.5, 0.2, k), lerp(-5.2, -4.4, k), 1.35), A(-0.3, 0.4, 1.25), 21, 0.02 * math.sin(t * 5.2))


def reg_cu(S, k, t, lt):
    """Close on the mask: he is still breathing off his regulator."""
    A = gullet(S, t, 0.6)
    trapped(S, A, t, 0.0, 'scared', True)
    h = head_of(S, 'pack')
    key(S, 'kw', (h[0] - 1.2, h[1] - 2.4, h[2] + 0.6), h, 150)
    lantern(S, A, -1.2, -1.45, 0.55, 60)
    cam(S, (h[0] + lerp(-0.9, -0.6, k), h[1] - lerp(2.6, 2.2, k), h[2] + 0.35), (h[0], h[1], h[2] - 0.05), 40, 0.02 * math.sin(t * 5.2))


def squeeze(S, k, t, lt):
    """The mouth works around him. He shoves back with everything he has."""
    A = gullet(S, t, 1.8)
    trapped(S, A, t, 1.0, 'shock')
    key(S, 'kw', A(-2.5, -3, 2.2), A(0.6, 0.9, 1.0), 260)
    cam(S, A(lerp(-1.6, -1.3, k), lerp(-2.9, -2.6, k), lerp(1.9, 1.7, k)), A(0.6, 1.2, 1.0), 24, 0.06 * math.sin(t * 17))


def rook_quiet(S, k, t, lt):
    """Rook, hat against his chest. No jokes in here."""
    A = gullet(S, t, 0.6)
    trapped(S, A, t, 0.0, 'sad')
    rook_in(S, A, t, P('sit', lift=-0.5, lean=0.2, aL=(0.5, 0.2, 1.2), aR=(1.0, -0.15, 2.0, 1.0), head=(0.32, lerp(-0.5, -0.2, k))), 'sad')
    S['hat'], S['helm'] = 'chest', False
    lantern(S, A, -1.0, -1.5, 0.55, 90)
    h = head_of(S, 'rook')
    cam(S, (h[0] + lerp(1.0, 0.8, k), h[1] - lerp(3.3, 2.9, k), h[2] + 0.1), (h[0], h[1], h[2] - 0.25), 44)


# ---------------------------------------------------------------- shots: out
def rise(S, k, t, lt):
    """The whale drives for the surface."""
    A = water(S, 'day')
    e = ease(k)
    whale(S, A(lerp(1.5, 0.0, e), lerp(7.0, 2.0, e), lerp(6.0, 15.0, e)), 0.2, -1.05, 0.1 * math.sin(t * 5), 0.05, t, 2.6)
    in_mouth(S, t, 1.3)
    bub(S, wpt(S, 0, 3, 1.5), t, 22, 0, 2.2, 9.0, -7.0, size=1.8)
    key(S, 'kc', A(8, -8, 4), A(0, 3, 10), 3500)
    cam(S, A(lerp(6.5, 5.5, k), lerp(-8.5, -7.5, k), lerp(2.5, 3.5, k)), A(0.4, 3.5, lerp(7.5, 12.5, e)), 22, 0.05 * math.sin(t * 8))


def breach(S, k, t, lt):
    """Beside the boat the sea stands up."""
    A = bay(S, t, 0.6)
    boat_at(S, -8.5, 12, 0.25, t)
    j = ease(lt / 0.3)
    crew(S, 'mayo', -3.0, -1.4, PI + 0.5, blend(P('stand', aL=(0.6, 0.2, 0.8), aR=(0.6, 0.2, 0.8)), P('up', aL=(2.3, 0.8, 0.9), aR=(2.3, 0.8, 0.9), lean=-0.25, head=(-0.2, 0)), j), 'shock')
    e = ease(lt / 0.5)
    whale(S, A(3.4, 4.5, lerp(-6.0, 1.4, e)), 2.2, -PI / 2 + 0.2, 0.0, lerp(0.05, 0.35, e), t, 2.0)
    in_mouth(S, t, 1.3)
    spray(S, A(3.4, 4.5, 0.4), min(1.0, lt / 1.4), 44, 0, 7.5, 8.0, seed=3, size=3.0)
    cam(S, A(lerp(11.5, 10.5, k), lerp(-12.5, -11.5, k), 2.0), A(0.5, 6, lerp(3.6, 4.4, k)), 25, 0.05 * math.sin(t * 13))


def shake(S, k, t, lt):
    """Close on the head: it shakes from side to side, mouth working."""
    A = bay(S, t, 0.7)
    sw = math.sin(t * 13)
    whale(S, A(0, 0, 0.9), 1.9 + 0.25 * sw, -PI / 2 + 0.15, 0.3 * sw, lerp(0.3, 0.9, ease(k)), t, 2.2)
    in_mouth(S, t, lerp(1.4, 2.2, k))
    spray(S, A(0, 0, 0.4), (lt * 0.9) % 1.0, 30, 0, 5.0, 5.0, seed=2, size=2.4)
    spray(S, wpt(S, 0, -5.5, 0), (lt * 1.4) % 1.0, 16, 30, 2.6, 2.4, seed=5, size=1.6)
    cam(S, A(lerp(5.4, 4.8, k), lerp(-9.5, -8.7, k), 3.0), A(0, 0, lerp(3.4, 3.9, k)), 34, 0.07 * math.sin(t * 19))


def flung(S, k, t, lt):
    """Thrown clear: a diver, and one crow, against the morning sky."""
    A = bay(S, t, 0.7)
    whale(S, A(0.5, 2.5, 0.4), 1.9, -PI / 2 + 0.2, 0.1 * math.sin(t * 8), 1.0, t, 2.0)
    j = 1 - (1 - min(1.0, lt / 1.2)) ** 2
    S['pack'].place(A(lerp(0.0, -2.6, j), lerp(2.2, 0.2, j), lerp(5.0, 9.6, j)), 0.4 + lt * 1.6, 1.0 + lt * 3.4, 0.3)
    S['pack'].apply(P('up', aL=(2.2, 1.0, 0.5), aR=(1.8, 1.1, 0.8), lL=(0.8, 1.0), lR=(-0.5, 0.5)))
    S['face']['pack'] = 'shock'
    S['rook'].place(A(lerp(1.2, 3.2, j), lerp(1.6, -0.6, j), lerp(4.6, 8.0, j)), -0.3 - lt * 0.5, -0.35 + 0.3 * math.sin(lt * 5), 0.25)
    S['rook'].apply(P('up', aL=(2.4, 1.1, 0.6), aR=(2.2, 1.2, 0.5), lL=(0.9, 1.1), lR=(-0.3, 0.8), head=(-0.1, 0.2)))
    S['face']['rook'], S['hat'] = 'shocked', 0.25 + 0.9 * j
    spray(S, A(0.5, 2.0, 3.6), j, 40, 0, 6.5, 5.0, seed=4, size=2.6)
    cam(S, A(lerp(0.6, 0.2, k), lerp(-10.5, -9.5, k), 0.9), A(0.2, 1.0, lerp(6.6, 7.6, k)), 21, 0.05 * math.sin(t * 11))


def afloat(S, A, x, y, t, face='tired', wave=0.0):
    """On his back in the water."""
    S['pack'].place(A(x, y, 0.05 + 0.6 * swell(x, y, t, 0.6)), -PI / 2 + 0.3, -PI / 2 + 0.12 * math.sin(t * 2))
    S['pack'].apply(P('stand', aL=(0.3 + wave * 1.8, 0.9, 0.5), aR=(0.3, 0.9 + 0.1 * math.sin(t * 5), 0.4), lL=(0.3, 0.3), lR=(0.15, 0.5), head=(-0.2, 0.2)))
    S['face']['pack'] = face


def splashdown(S, k, t, lt):
    """He lands in white water. Behind him the flukes go down."""
    A = bay(S, t, 0.7)
    afloat(S, A, 0.0, 0.0, t, 'shock')
    spray(S, A(0, 0.3, 0.2), min(1.0, lt / 1.1), 34, 0, 4.2, 4.6, seed=7, size=2.4)
    e = ease(k)
    whale(S, A(-6.5, 13, lerp(4.2, -3.0, e)), 0.25, 1.25, 0.0, 0.0, t, 1.4)
    spray(S, A(-6.5, 14, 0.2), (lt * 0.8) % 1, 20, 34, 4.0, 2.0, seed=1, size=1.8)
    cam(S, A(lerp(4.6, 4.0, k), lerp(-7.8, -7.0, k), lerp(1.3, 1.6, k)), A(-1.0, 2.0, lerp(2.2, 1.9, k)), 26, 0.03 * math.sin(t * 7))


def haul(S, k, t, lt):
    """Josiah Mayo gets him over the stern. Rook pushes from below."""
    A = bay(S, t, 0.5)
    boat_at(S, 0, 6, 0.0, t)
    e = ease(k)
    crew(S, 'mayo', -6.75, 0.0, PI, P('stand', aL=(1.2 + 0.3 * e, 0.15, 0.3), aR=(1.2 + 0.3 * e, 0.15, 0.3), lL=(0.5, 0.9), lR=(-0.3, 0.6), lean=lerp(0.95, 0.6, e),
                                        lift=-0.25, head=(-0.3, 0)), 'scared')
    S['pack'].place(A(-8.7, 5.4, lerp(-1.7, -0.4, e)), PI / 2, 0.12)
    S['pack'].apply(P('up', aL=(2.75, 0.2, 0.2), aR=(2.75, 0.2, 0.2), lL=(0.3 * math.sin(t * 8), 0.4), lR=(-0.3 * math.sin(t * 8), 0.4), head=(-0.3, 0)))
    S['face']['pack'] = 'tired'
    S['rook'].place(A(-10.3, 3.6, lerp(-2.4, -1.8, e)), PI / 2 + 0.6, 0.1)
    S['rook'].apply(P('up', aL=(2.3, 0.3, 0.5), aR=(2.3, 0.3, 0.5), head=(-0.3, -0.3)))
    S['face']['rook'], S['helm'] = 'calm', True
    spray(S, A(-9.6, 6.6, 0.1), (lt * 0.8) % 1, 14, 0, 2.2, 1.0, seed=3, size=1.1)
    cam(S, A(lerp(-14.5, -13.5, k), lerp(-3.2, -2.4, k), 1.5), A(-7.8, 5.8, lerp(2.3, 2.7, k)), 28, 0.03 * math.sin(t * 3))


# ---------------------------------------------------------------- shots: home
def ward(S, k, t, lt):
    """That afternoon: on the edge of a hospital bed, checking that everything still bends."""
    A = show(S, 'ward')
    sky(S, '101418')
    f = 0.5 + 0.5 * math.sin(lt * 5.0)
    S['mike'].place(A(-1.35, 1.6, 0.22), 1.0)
    S['mike'].apply(P('sit', lift=-0.5, lean=0.15, aL=(0.5, 0.4, 1.0), aR=(lerp(0.6, 1.5, f), 0.5, lerp(1.0, 2.2, f)), lR=(lerp(1.45, 1.1, f), lerp(1.6, 0.7, f)),
                      head=(0.2, 0.2)))
    S['face']['mike'] = 'tired'
    cam(S, A(lerp(3.6, 3.0, k), lerp(-4.6, -3.8, k), 2.0), A(-1.0, 1.8, 1.75), 30)


def limp(t):
    p = walk(t, 1.15)
    p['lift'] = -0.1 * max(0.0, math.sin(t * 1.15 * 2 * PI))
    p['lean'] = 0.16
    return p


def walk_out(S, k, t, lt):
    """He walks out on his own legs, with a limp. Rook waits at the door."""
    A = show(S, 'ward')
    sky(S, '101418')
    S['mike'].place(A(lerp(0.4, 2.7, k), lerp(1.2, 3.9, k), 0), 2.43)
    S['mike'].apply(limp(t))
    S['face']['mike'] = 'happy'
    S['rook'].place(A(1.35, 5.0, 0), 0.5)
    S['rook'].apply(P('cross', head=(0.0, 0.5)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(-1.6, -1.0, k), lerp(-5.6, -4.8, k), 2.3), A(1.9, 3.6, 2.0), 29)


def rook_door(S, k, t, lt):
    """Rook tips his hat as the man goes by."""
    A = show(S, 'ward')
    sky(S, '101418')
    S['mike'].place(A(3.35, lerp(4.6, 6.4, k), 0), PI)
    p = limp(t)
    p['aR'] = (2.5, 0.6, 0.6 + 0.3 * math.sin(t * 9), 0.0)
    S['mike'].apply(p)
    e = math.sin(PI * ease((lt - 0.1) / 1.0))
    S['rook'].place(A(1.35, 5.0, 0), 0.75)
    S['rook'].apply(blend(P('stand', head=(0.0, 0.6)), P('hat', head=(0.1, 0.5)), e))
    S['face']['rook'], S['hat_tip'] = 'warm', e
    cam(S, A(lerp(1.3, 1.5, k), lerp(-0.6, 0.0, k), 2.0), A(2.2, 5.2, 2.2), 36)


# ---------------------------------------------------------------- shots: the end
def feeding(S, k, t, lt):
    """What the scientists think happened: a whale lunging through sand lance with its mouth wide open."""
    A = water(S, 'day')
    e = ease(k)
    x = lerp(-6.0, 1.0, e)
    whale(S, A(x, 4.0, 7.6), PI / 2, 0.03, 0.0, 0.95, t, 1.8)
    shoal(S, A(x + 8.5, 4.0, 7.3), t, 64, 0, (3.0, 2.4, 1.9), PI / 2, 5.0, 9.0)
    rook_uw(S, A(3.6, -8.2, 0.4), PI - 0.9, P('point', aR=(2.1, 0.2, 0.1), aL=(0.3, 0.3, 0.6), head=(-0.1, 1.25 - 0.3 * math.sin(lt * 3))), 'calm', t)
    key(S, 'kw', A(1, -13, 3), A(3.6, -8.2, 2.6), 1500)
    key(S, 'kc', A(8, -12, 8), A(2, 4, 6), 5000)
    cam(S, A(lerp(0.0, 1.0, k), lerp(-16.8, -15.6, k), 2.4), A(lerp(0.6, 1.6, k), 2.0, 5.6), 25)


def mouthful(S, k, t, lt):
    """Head-on: the open mouth comes through the fish straight at the camera."""
    A = water(S, 'day')
    e = ease(k)
    whale(S, A(0.3 * math.sin(t * 2), lerp(10.5, 4.6, e), 5.6), 0.0, 0.02, 0.0, 1.0, t, 1.8)
    shoal(S, A(0, lerp(2.5, -2.5, e), 5.3), t, 70, 0, (3.2, 3.0, 2.0), 0.0, 6.0, 8.0)
    key(S, 'kw', A(-4, -8, 4), A(0, 6, 5.4), 2000)
    key(S, 'kc', A(6, -6, 9), A(0, 6, 5.4), 3500)
    cam(S, A(lerp(1.2, 0.6, k), -7.5, lerp(4.4, 4.9, k)), A(0, 4, 5.5), 21, 0.03 * math.sin(t * 7))


def throat_look(S, k, t, lt):
    """Rook holds his lantern up to the whale's throat: nothing the size of a man is going down that."""
    A = gullet(S, t, 0.3)
    e = ease(lt / 0.5)
    S['rook'].place(A(-0.9, 2.6, -0.42), PI - 0.75 + 1.1 * ease((lt - 0.55) / 0.5), 0.0)
    S['rook'].apply(blend(P('stand', lL=(0.9, 1.5), lR=(0.9, 1.5), lift=-0.45, aR=(1.6, 0.3, 0.4), head=(-0.1, 0.0)),
                          P('shrug', lL=(0.9, 1.5), lR=(0.9, 1.5), lift=-0.45, head=(0.0, -0.3)), ease((lt - 0.6) / 0.4)))
    S['face']['rook'], S['helm'] = 'deadpan', False
    lantern(S, A, 0.0, lerp(3.2, 4.2, e), 0.9, 200)
    key(S, 'kw', A(0.5, -1, 2.2), A(0, 5.5, 0.8), 500)
    cam(S, A(lerp(1.3, 1.0, k), lerp(-2.6, -1.8, k), 1.5), A(-0.2, 4.6, 1.0), 26)


def rook_shrug(S, k, t, lt):
    """Evening on the pier. Right, and wrong."""
    A = pier(S, True)
    e = math.sin(PI * ease((lt - 0.15) / 1.0))
    S['rook'].place(A(1.2, -1.2, 0), 0.35)
    S['rook'].apply(blend(P('stand', head=(0.0, 0.25)), P('shrug', head=(-0.08, -0.1)), e))
    S['face']['rook'] = 'smirk'
    cam(S, A(lerp(3.1, 2.7, k), lerp(-6.6, -5.8, k), 1.6), A(1.2, -1.2, 2.25), 36)


def signoff(S, k, t, lt):
    A = pier(S, True)
    S['rook'].place(A(-1.4, -1.6, 0), 0.2)
    c = max(0.0, min(1.0, (lt - 0.2) / 0.9))
    S['rook'].apply(blend(P('stand', aR=(0.9, 0.25, 1.2), head=(0.05, 0)), P('stand', aR=(1.2, 0.2, 1.5), head=(-0.12, 0)), math.sin(c * PI)))
    S['face']['rook'] = 'smirk'
    S['pick'].location = A(-2.15 - 0.2 * c, -2.35, 1.8 + 2.4 * math.sin(c * PI))
    S['pick'].rotation_euler = (t * 19, t * 9, 0)
    S['pick'].scale = (1.3, 1.3, 1.3)
    cam(S, A(lerp(0.3, -0.1, k), lerp(-6.6, -5.8, k), 0.9), A(-1.4, -1.6, 2.25), 36)


# ---------------------------------------------------------------- stills for the case board
def photo_whale(S, k, t, lt):
    A = water(S, 'day')
    whale(S, A(-2, 6, 6), PI / 2 - 0.5, -0.1, 0.0, 0.0, 0.3)
    key(S, 'kc', A(6, -10, 8), A(2, 6, 6), 5000)
    cam(S, A(8, -13, 5), A(2.5, 7, 6), 30)


def photo_diver(S, k, t, lt):
    A = water(S, 'day')
    uw(S, 'pack', A(-8, -6, 0), 0.3, P('stand', aR=(2.3, 0.5, 1.8), aL=(0.4, 0.3, 0.5), head=(-0.05, 0.1)), 0.0)
    key(S, 'kw', A(-6.5, -10, 3.2), A(-8, -6, 2.3), 700)
    cam(S, A(-7.4, -10.6, 2.3), A(-8, -6, 2.0), 46)


SHOTS3D = {f.__name__.rstrip('_'): f for f in (
    gulp, jaws_shut, whale_wide, spat, rook_dock, rook_dive, boat_wide, descend, sand_hunt, lobster_cu, shoal_, shadow, feel_dark, mouth_wide,
    reg_cu, squeeze, rook_quiet, rise, breach, shake, flung, splashdown, haul, ward, walk_out, rook_door, feeding, mouthful, throat_look, rook_shrug, signoff)}
STILLS = dict(whale=photo_whale, diver=photo_diver)
