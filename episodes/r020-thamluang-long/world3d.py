"""Case 020 in 3D - the Tham Luang cave rescue. On 23 June 2018 twelve boys of a junior football team and
their assistant coach walked into the Tham Luang cave in northern Thailand; heavy rain flooded the passages
behind them. They were found alive on 2 July by two British cave divers, and between 8 and 10 July they were
sedated, fitted with full-face masks and carried out underwater by divers, one at a time. A Thai rescuer,
Saman Kunan, died on 6 July while placing air tanks in the cave.

Built for this story only: a cave mouth in a limestone cliff under monsoon rain (bicycles at a rail outside,
later pumps, hoses and floodlights), a flooded passage with a low arch, a chamber with a slope of mud above
black water, and a flooded tunnel with a guide line and a squeeze.

Everything is a generic low-poly reconstruction, not a survey of the real cave or a model of the real site.
The thirteen are simple figures in plain shirts, the divers and rescuers are plain figures in plain gear:
nobody's likeness is attempted, and no emblem, flag, sign, brand, team badge or lettering appears in the sets.
Nothing graphic is shown: the rescuer's death is a lamp that goes out and a hat held to a chest."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
SETS = dict(mouth=(0, 0, 0), tun=(4000, 0, 0), ledge=(8000, 0, 0), sump=(12000, 0, 0))
AWAY = (0, 0, -3000)
HOST = {'bikes', 'rook_rock', 'rook_drip', 'scramble', 'huddle', 'glow', 'rook_count', 'toe_dip', 'rook_sound', 'rook_vigil',
        'carry_in', 'stretcher_out', 'pump_fail', 'reflood', 'rook_wrong', 'signoff'}
CAMFILL = {'*': 170, 'mouth_wide': 60, 'bikes': 220, 'stretcher_out': 120, 'pump_fail': 200, 'rook_wrong': 50, 'signoff': 60,
           'ledge_wide': 420, 'glow': 120, 'sump_long': 260, 'carry_dark': 260, 'squeeze': 200, 'divers_fight': 260, 'faces_lit': 260,
           'walk_in': 260, 'rain_gush': 200}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
ROCK, ROCKD, ROCKL, MUD, MUDL, MUDD = '5C6258', '353B36', '7E8676', '6B4E34', '8A6A48', '3E2C1E'
LIME, LIMED, LIMEL = '9A9C88', '6E7264', 'BCBEA8'
WATER, LEAF, LEAFL, LINE = '0B2A30', '2B5A32', '4A8A44', 'F0DC5A'
SHIRTS = ('B8322E', '2F6FB0', 'E4DFD0', '2E8A5A', 'D8A22A', '7A3FA0')
SKINS = ('C8946A', 'B88458', 'D2A070')
TH = 0.30                                   # the mud slope in the chamber
BOULDER = (3.4, 2.0, 2.7)                   # Rook's rock in the flooded passage (x, y, top)
SEATS = [(-3.6, 2.7), (-1.8, 2.6), (0.0, 2.8), (1.8, 2.6), (3.6, 2.7), (-2.7, 4.7), (-0.9, 4.6), (0.9, 4.7), (2.7, 4.6),
         (-1.8, 6.7), (1.8, 6.6), (3.6, 6.7), (0.0, 6.8)]          # twelve boys, then the coach (last)
PUMP = (8.0, 1.0)
_KEEP = []


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def loc(name, x, y, z):
    o = SETS[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def stage(name, fn):
    """Build one set at its own origin and in its own collection, so that only one set renders per shot."""
    before = set(bpy.data.objects)
    out = fn(empty(SETS[name]))
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for o in set(bpy.data.objects) - before:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        coll.objects.link(o)
    return coll, out


def newmat(name, col, rough=0.6, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Roughness'].default_value = rough
    b.inputs['Alpha'].default_value = alpha
    paint(m, col, emit)
    return m


def paint(m, col, emit=0.0):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)
    b.inputs['Emission Color'].default_value = K.hexc(col)
    b.inputs['Emission Strength'].default_value = emit


def wear(o, m):
    o.data.materials[0] = m
    return o


def keep(o):
    """Remember how a movable prop was built so reset() can put it back."""
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def rn(i, j=0):
    return (math.sin(i * 78.233 + j * 37.719) * 43758.5453) % 1


def seen(objs, on):
    for o in objs:
        o.hide_render = not on


def tree_of(o):
    return [o] + [c for ch in o.children for c in tree_of(ch)]


def look_yaw(frm, to):
    """Yaw that turns a rig standing at frm towards to (rigs face -Y at yaw 0)."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def span(o, a, b, w):
    """Stretch a unit-long object (built along Z, radius 0.5) between two points."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def tube(r, col, a, b, w, **kw):
    o = add('cylinder', col, radius=0.5, depth=1, vertices=6, parent=r, **kw)
    span(o, a, b, w)
    return o


def lp(x, y, up=0.0):
    """A point on the mud slope in the chamber (the water's edge is near y = 0.7)."""
    return (x, y, y * math.tan(TH) - 0.2 + up)


def mz(y):
    """Floor height on the path into the cave mouth: level outside, sloping down inside."""
    return 0.0 if y < 14 else -0.09 * (y - 14)


def lumps(r, n, seed, fn, cols=(ROCK, ROCKD, ROCKL), s0=0.8, s1=1.6, flat=1.0):
    for j in range(n):
        p = fn(j)
        if p is None:
            continue
        s = s0 + s1 * rn(j, seed)
        add('ico_sphere', cols[j % len(cols)], p, rot=(rn(j, seed + 1), rn(j, seed + 2), rn(j, seed + 3) * 3),
            scale=(s * (1 + rn(j, seed + 4)), s, s * flat * (0.7 + 0.6 * rn(j, seed + 5))), radius=1, subdivisions=1, parent=r)


# ---------------------------------------------------------------- the cave mouth
def bike(r, x, y, col, lean, turn):
    e = empty((x, y, 0), r, (0, lean, turn))
    for s in (-1, 1):
        add('torus', '15161A', (0, s * 0.8, 0.55), rot=(0, PI / 2, 0), major_radius=0.5, minor_radius=0.06, major_segments=12, minor_segments=4, parent=e)
        add('cylinder', 'B8BCC8', (0, s * 0.8, 0.55), rot=(0, PI / 2, 0), radius=0.07, depth=0.12, vertices=6, parent=e, rough=0.3)
    R, F, B, ST, HD = (0, -0.8, 0.55), (0, 0.8, 0.55), (0, -0.1, 0.5), (0, -0.35, 1.25), (0, 0.55, 1.3)
    for a, b in ((R, B), (B, ST), (ST, HD), (B, HD), (R, ST)):
        tube(e, col, a, b, 0.045)
    tube(e, 'B8BCC8', (0, 0.5, 1.5), F, 0.04, rough=0.3)
    tube(e, '22262E', (-0.36, 0.5, 1.5), (0.36, 0.5, 1.5), 0.04)
    add('cube', '22262E', (0, -0.4, 1.33), scale=(0.2, 0.42, 0.08), size=1, parent=e)
    return e


def set_mouth(r):
    out = {}
    add('cube', '6A5C44', (0, -30, -0.5), scale=(400, 160, 1), size=1, parent=r)                        # wet ground
    add('cube', '9A8460', (0, -8, 0.0), scale=(5.5, 46, 0.06), size=1, parent=r)                        # the path
    for sd in (-1, 1):                                                                                 # the cliff either side of the mouth
        add('cube', LIME, (sd * 36, 30, 11), scale=(60, 32, 26), size=1, parent=r)
    add('cube', LIME, (0, 30, 17), scale=(14, 32, 14), size=1, parent=r)
    lumps(r, 30, 100, lambda j: (-60 + 120 * rn(j, 101), 16 + 10 * rn(j, 102), 24.5), cols=(LEAF, LEAFL, '1F4428'), s0=2.5, s1=3.0, flat=0.8)                                # the rock over the mouth
    add('cube', '020304', (0, 46, 2), scale=(14, 1, 18), size=1, parent=r)                              # the dark inside
    for j in range(9):                                                                                 # the floor going down into the cave
        add('cube', MUDD if j % 2 else MUD, (0, 16 + 3.2 * j, mz(16 + 3.2 * j) - 0.5), rot=(-0.09, 0, 0), scale=(12.4, 3.4, 1), size=1, parent=r)
    for j in range(22):                                                                                # the rim of the mouth: an arch of boulders
        a = PI * j / 21
        s = 1.2 + 1.0 * rn(j, 1)
        add('ico_sphere', (LIMEL, LIME, LIMED)[j % 3], (6.6 * math.cos(a), 13.6 - 0.6 * rn(j, 2), 0.4 + 8.2 * math.sin(a)), rot=(rn(j, 3), rn(j, 4), j),
            scale=(s, s * 0.9, s * 1.2), radius=1, subdivisions=1, parent=r)
    lumps(r, 60, 5, lambda j: None if abs(-50 + 100 * rn(j, 6)) < 8.5 and 24 * rn(j, 7) < 10.5 else (-50 + 100 * rn(j, 6), 13.6, 24 * rn(j, 7)),
          cols=(LIME, LIMED, LIMEL), s0=1.2, s1=2.6)
    lumps(r, 30, 8, lambda j: (-50 + 100 * rn(j, 9), 13.2, 3 + 20 * rn(j, 10)) if abs(-50 + 100 * rn(j, 9)) > 9 or 3 + 20 * rn(j, 10) > 13 else None,
          cols=(LEAF, LEAFL, '1F4428'), s0=1.0, s1=2.0, flat=0.8)
    lumps(r, 26, 110, lambda j: (-8 + 16 * rn(j, 111), 13.7, 10.5 + 13 * rn(j, 112)), cols=(LIME, LIMED, LIMEL, LEAF), s0=1.3, s1=2.0)
    for j in range(12):                                                                                # creepers hanging over the mouth
        x = -5.6 + 11.2 * rn(j, 11)
        d = 1.2 + 2.6 * rn(j, 12)
        add('cylinder', LEAF if j % 2 else '1F4428', (x, 13.0, 8.6 - d / 2 + 1.5 * (1 - (x / 6.2) ** 2)), radius=0.05, depth=d, vertices=4, parent=r)
    for j in range(26):                                                                                # jungle either side of the path
        sd = -1 if j % 2 else 1
        x, y = sd * (15 + 30 * rn(j, 13)), -34 + 44 * rn(j, 14)
        hgt = 5 + 6 * rn(j, 15)
        add('cylinder', '3E3226', (x, y, hgt / 2), radius=0.28, depth=hgt, vertices=6, parent=r)
        for q in range(3):
            add('ico_sphere', (LEAF, LEAFL, '1F4428')[(j + q) % 3], (x + 1.4 * (rn(j, 16 + q) - 0.5), y + 1.4 * (rn(j, 19 + q) - 0.5), hgt + 0.8 * q),
                scale=(2.6 - 0.5 * q, 2.6 - 0.5 * q, 1.5), radius=1, subdivisions=1, parent=r)
    lumps(r, 30, 22, lambda j: (-28 + 56 * rn(j, 23), -30 + 40 * rn(j, 24), 0.1) if abs(-28 + 56 * rn(j, 23)) > 3.6 else None,
          cols=(LEAF, '1F4428', '4A4030'), s0=0.4, s1=0.7, flat=0.5)
    for x in (-10.4, -7.4, -4.4):                                                                      # the rail the bicycles stand at
        add('cylinder', '6A5238', (x, -11, 0.6), radius=0.09, depth=1.2, vertices=6, parent=r)
    tube(r, '7A6044', (-10.8, -11, 1.15), (-4.0, -11, 1.15), 0.07)
    out['bikes'] = []
    for j, col in enumerate(('C8372D', '2F6FB0', 'E0B030', '2E8A5A', 'D8D4C8')):
        out['bikes'].append(bike(r, -9.8 + 1.25 * j, -12.05, col, 0.1 + 0.08 * rn(j, 25), 0.2 * (rn(j, 26) - 0.5)))
    out['wheel'] = empty((-9.8 + 1.25 * 4 + 0.02, -12.85, 0.55), r)                                       # spokes on the nearest back wheel, turning
    for q in range(3):
        add('cylinder', 'D8DCE4', (0, 0, 0), rot=(q * PI / 3, 0, 0), radius=0.012, depth=0.92, vertices=4, parent=out['wheel'], rough=0.3)
    # rescue gear, switched on for the later scenes
    kit = []
    for j, (px, py) in enumerate((PUMP, (PUMP[0] + 2.6, PUMP[1] + 1.2))):
        b = empty((px, py, 0), r)
        add('cube', '3A3F4C', (0, 0, 0.25), scale=(1.9, 1.3, 0.3), size=1, parent=b)
        add('cube', 'D8822A', (0, 0, 0.85), scale=(1.5, 1.0, 0.9), size=1, parent=b)
        add('cylinder', '8A90A0', (-0.55, 0, 1.55), radius=0.12, depth=0.7, vertices=6, parent=b, rough=0.4)
        add('cylinder', '8A90A0', (0.6, -0.62, 0.8), rot=(PI / 2, 0, 0), radius=0.3, depth=0.3, vertices=8, parent=b, rough=0.4)
        kit += tree_of(b)
        out['pump' if j == 0 else 'pump2'] = b
    hose = [(PUMP[0] - 0.9, PUMP[1], 0.3), (5.2, 4.0, 0.2), (3.4, 9.0, 0.2), (3.0, 15.0, 0.1), (2.6, 24.0, mz(24) + 0.2)]
    out['hose'] = [tube(r, '2C4E8A', a, b, 0.22) for a, b in zip(hose, hose[1:])]
    hose2 = [(PUMP[0] + 0.9, PUMP[1] - 0.2, 0.3), (12.0, -4.0, 0.2), (18.0, -14.0, 0.2), (30.0, -30.0, 0.2)]
    kit += out['hose'] + [tube(r, '2C4E8A', a, b, 0.22) for a, b in zip(hose2, hose2[1:])]
    out['floodm'] = newmat('flood', 'FFF2D0', 0.4, 0.0)
    out['floods'] = []
    for x, y in ((-7.5, 6.0), (11.5, 9.5)):
        kit.append(add('cylinder', '3A3F4C', (x, y, 2.2), radius=0.07, depth=4.4, vertices=5, parent=r))
        kit.append(wear(add('cube', 'FFF2D0', (x, y + 0.1, 4.5), rot=(0.5, 0, 0), scale=(1.1, 0.2, 0.7), size=1, parent=r), out['floodm']))
        out['floods'].append(light((x * 0.8, y + 1.0, 4.4), 0, 'FFE8C0', kind='POINT', parent=r))
    for j in range(5):                                                                                 # crates and coiled line
        kit.append(add('cube', ('5A6A50', '7A6044')[j % 2], (-6.5 - 1.3 * (j % 3), 1.5 + 1.2 * (j // 3), 0.45), rot=(0, 0, 0.2 * j), scale=(1.1, 0.9, 0.9), size=1,
                       parent=r))
    kit.append(add('torus', LINE, (-5.0, 3.6, 0.2), major_radius=0.55, minor_radius=0.12, major_segments=12, minor_segments=5, parent=r))
    out['kit'] = kit
    out['puddles'] = [add('cylinder', '8FA4B0', (-2 + 4 * rn(j, 27), -20 + 26 * rn(j, 28), 0.04 + 0.012 * j), scale=(1.4, 1.0, 1), radius=0.9, depth=0.02, vertices=8, parent=r,
                          rough=0.42) for j in range(8)]
    return out


# ---------------------------------------------------------------- the flooded passage
def set_tun(r):
    out = {}
    add('cube', MUD, (0, 4, -0.5), scale=(16, 70, 1), size=1, parent=r)
    for sd in (-1, 1):
        add('cube', ROCKD, (sd * 9.5, 4, 5), scale=(8, 70, 16), size=1, parent=r)
        lumps(r, 30, 30 + sd, lambda j: (sd * (5.6 - 0.6 * rn(j, 33)), -24 + 52 * rn(j, 34 + sd), 7.5 * rn(j, 36 + sd)), s0=0.9, s1=1.4)
    add('cube', ROCKD, (0, 4, 8.5), scale=(16, 70, 2), size=1, parent=r)                               # the roof
    for j in range(34):                                                                                # stalactites
        x, y = -5 + 10 * rn(j, 38), -22 + 46 * rn(j, 39)
        d = 0.8 + 2.4 * rn(j, 40)
        add('cone', ROCKL if j % 3 else ROCK, (x, y, 7.6 - d / 2), rot=(PI, 0, 0), radius1=0.25 + 0.3 * rn(j, 41), radius2=0, depth=d, vertices=5, parent=r)
    for sd in (-1, 1):                                                                                 # the low arch: the way out
        add('cube', ROCK, (sd * 5.6, 19.5, 4), scale=(6.4, 3, 8), size=1, parent=r)
    add('cube', ROCK, (0, 19.5, 4.9), scale=(5, 3, 6.4), size=1, parent=r)
    add('cube', '010203', (0, 21.5, 1.2), scale=(5, 0.4, 2.6), size=1, parent=r)
    lumps(r, 16, 42, lambda j: (-3.4 + 6.8 * rn(j, 43), 17.9, 1.9 + 1.2 * rn(j, 44) + 1.5 * abs(-1 + 2 * rn(j, 43))), s0=0.6, s1=0.6)
    add('ico_sphere', ROCKL, (BOULDER[0], BOULDER[1], 1.0), scale=(1.6, 1.5, 1.75), radius=1, subdivisions=1, parent=r)   # Rook's rock
    add('ico_sphere', ROCK, (BOULDER[0] + 1.3, BOULDER[1] + 1.0, 0.7), scale=(1.4, 1.2, 1.3), radius=1, subdivisions=1, parent=r)
    lumps(r, 14, 45, lambda j: (-4.6 + 9.2 * rn(j, 46), -20 + 34 * rn(j, 47), 0.2) if abs(-4.6 + 9.2 * rn(j, 46)) > 2.6 else None, s0=0.4, s1=0.6, flat=0.7)
    add('cube', '010203', (0, -31, 4), scale=(16, 1, 9), size=1, parent=r)
    out['water'] = keep(add('cube', WATER, (0, 4, -3.5), scale=(16, 70, 6), size=1, parent=r, rough=0.06))
    return out


# ---------------------------------------------------------------- the chamber with the slope of mud
def set_ledge(r):
    out = {}
    L = 15 / math.cos(TH)
    add('cube', MUD, (0, 6.5 + math.sin(TH), 6.5 * math.tan(TH) - 0.2 - math.cos(TH)), rot=(TH, 0, 0), scale=(17, L, 2), size=1, parent=r)
    lumps(r, 22, 50, lambda j: lp(-7.5 + 15 * rn(j, 51), 1.2 + 11 * rn(j, 52), -0.15) if j % 2 or abs(-7.5 + 15 * rn(j, 51)) > 5 else None,
          cols=(MUDL, MUDD, MUD), s0=0.5, s1=0.7, flat=0.35)
    add('cube', WATER, (0, -30, -3.0), scale=(60, 64, 6), size=1, parent=r, rough=0.05)                # black water
    for sd in (-1, 1):
        add('cube', ROCKD, (sd * 13, -6, 7), scale=(9, 60, 22), size=1, parent=r)
        lumps(r, 26, 53 + sd, lambda j: (sd * (8.6 - 0.8 * rn(j, 55)), -24 + 38 * rn(j, 56 + sd), 9 * rn(j, 58 + sd)), s0=1.0, s1=1.5)
    add('cube', ROCKD, (0, 15.5, 7), scale=(30, 3, 22), size=1, parent=r)                              # the back wall
    lumps(r, 18, 60, lambda j: (-8 + 16 * rn(j, 61), 13.8, 3.5 + 6 * rn(j, 62)), s0=1.0, s1=1.4)
    add('cube', ROCKD, (0, -6, 11.2), scale=(30, 60, 3), size=1, parent=r)                             # the roof
    for j in range(40):
        x, y = -8 + 16 * rn(j, 63), -22 + 34 * rn(j, 64)
        d = 0.8 + 2.8 * rn(j, 65)
        add('cone', ROCKL if j % 3 else ROCK, (x, y, 9.8 - d / 2), rot=(PI, 0, 0), radius1=0.25 + 0.35 * rn(j, 66), radius2=0, depth=d, vertices=5, parent=r)
    add('cube', '010203', (0, -44, 4), scale=(30, 1, 16), size=1, parent=r)
    lumps(r, 10, 67, lambda j: (-7.5 + 15 * rn(j, 68), 0.4 + 0.8 * rn(j, 69), 0.0) if abs(-7.5 + 15 * rn(j, 68)) > 4.2 else None, s0=0.5, s1=0.6, flat=0.7)
    out['glowm'] = newmat('glow', 'BFF2FF', 0.3, 0.0)
    out['glow'] = keep(wear(add('cylinder', 'BFF2FF', (0, -3.2, 0.03), radius=1, depth=0.02, vertices=14, parent=r), out['glowm']))
    out['glowl'] = light((0, -3.0, 0.9), 0, 'CFF4FF', kind='POINT', parent=r)
    out['blanket'] = keep(add('cube', 'C8D0DC', AWAY, scale=(1.5, 3.2, 0.06), size=1, parent=r, rough=0.2))
    return out


# ---------------------------------------------------------------- the flooded tunnel
def set_sump(r):
    out = {}
    for z in (-3.2, 3.2):
        add('cube', ROCKD, (0, 20, z), scale=(9, 90, 2), size=1, parent=r)
    for sd in (-1, 1):
        add('cube', ROCKD, (sd * 4.2, 20, 0), scale=(3, 90, 8), size=1, parent=r)
        lumps(r, 46, 70 + sd, lambda j: (sd * (2.9 - 0.5 * rn(j, 72)), -18 + 74 * rn(j, 73 + sd), -2.2 + 4.4 * rn(j, 75 + sd)),
              cols=('4A5A4E', '2C3A34', '66786A'), s0=0.6, s1=0.9)
    lumps(r, 40, 77, lambda j: (-2.6 + 5.2 * rn(j, 78), -18 + 74 * rn(j, 79), -2.3 if j % 2 else 2.3), cols=('4A5A4E', '2C3A34', '66786A'), s0=0.6, s1=0.9,
          flat=0.6)
    for sd in (-1, 1):                                                                                 # the squeeze
        add('ico_sphere', '66786A', (sd * 2.05, 20, 0.1), scale=(1.5, 1.6, 2.6), radius=1, subdivisions=1, parent=r)
        add('ico_sphere', '4A5A4E', (sd * 1.9, 20.6, -1.6), scale=(1.3, 1.4, 1.2), radius=1, subdivisions=1, parent=r)
    add('ico_sphere', '4A5A4E', (0.2, 20, 2.3), scale=(2.2, 1.6, 1.2), radius=1, subdivisions=1, parent=r)
    add('ico_sphere', '2C3A34', (-0.1, 20, -2.4), scale=(2.2, 1.6, 1.0), radius=1, subdivisions=1, parent=r)
    for y in (-25.5, 65.5):
        add('cube', '010403', (0, y, 0), scale=(9, 1, 8), size=1, parent=r)
    pts = [(-0.9 + 0.5 * math.sin(j * 1.3), -20 + 6 * j, -1.0 + 0.3 * math.cos(j * 0.9)) for j in range(15)]
    pts = [(0.0, p[1], -0.4) if abs(p[1] - 20) < 4 else p for p in pts]
    out['line'] = pts
    for a, b in zip(pts, pts[1:]):
        tube(r, LINE, a, b, 0.03, emit=0.5)
    for p in pts[::3]:
        add('cone', 'B8BCC8', (p[0], p[1], p[2] - 0.3), rot=(PI, 0, 0), radius1=0.08, radius2=0, depth=0.5, vertices=4, parent=r, rough=0.3)
    return out


def line_pt(S, y):
    pts = S['sump']['line']
    for a, b in zip(pts, pts[1:]):
        if a[1] <= y <= b[1]:
            k = (y - a[1]) / (b[1] - a[1])
            return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))
    return pts[0] if y < pts[0][1] else pts[-1]


# ---------------------------------------------------------------- heads and gear
def cave_diver(helm):
    """A cave diver's head: hood, helmet with two side lamps, a mask and a regulator. No face is shown."""
    def fn(head):
        add('ico_sphere', '14161C', (0, 0, 0.02), radius=0.31, subdivisions=1, parent=head)
        add('ico_sphere', helm, (0, 0.03, 0.15), scale=(1.0, 1.05, 0.68), radius=0.35, subdivisions=1, parent=head, rough=0.4)
        beads = []
        for s in (-1, 1):
            add('cube', '2A2E38', (s * 0.31, -0.1, 0.2), scale=(0.1, 0.2, 0.1), size=1, parent=head)
            beads.append(add('ico_sphere', 'F4FBFF', (s * 0.31, -0.22, 0.2), radius=0.06, subdivisions=1, parent=head, emit=16.0))
        add('cube', '0B1220', (0, -0.27, 0.02), scale=(0.46, 0.12, 0.2), size=1, parent=head, rough=0.15)
        add('cube', '6FD0E8', (0, -0.335, 0.03), scale=(0.38, 0.02, 0.13), size=1, parent=head, rough=0.15, emit=0.5)
        add('cylinder', '9AA0B4', (0, -0.34, -0.15), rot=(PI / 2, 0, 0), radius=0.1, depth=0.14, vertices=7, parent=head, rough=0.35)
        aim = empty((0, -6, -0.4), head)
        lamp = light((0, -0.4, 0.26), 0, 'E8F6FF', kind='SPOT', spot=0.95, target=aim, parent=head)
        cone = add('cone', 'DDF4FF', (0, -3.3, 0.1), rot=(math.radians(-90), 0, 0), radius1=1.1, radius2=0.06, depth=6, vertices=10, parent=head, emit=0.14,
                   alpha=0.05)
        return dict(lamp=lamp, cone=cone, beads=beads)
    return fn


def hard_hat(col):
    def fn(head):
        x = K.human_head('C8946A', '17131A')(head)
        add('ico_sphere', col, (0, 0.02, 0.16), scale=(1.0, 1.08, 0.62), radius=0.35, subdivisions=1, parent=head, rough=0.4)
        add('cube', col, (0, -0.3, 0.14), scale=(0.5, 0.2, 0.04), size=1, parent=head, rough=0.4)
        return x
    return fn


def make_torch(i):
    e = keep(empty(AWAY))
    add('cylinder', '3A3F4C', (0, 0, 0), radius=0.07, depth=0.42, vertices=6, parent=e)
    add('cylinder', 'C89A3A', (0, 0, 0.2), radius=0.1, depth=0.1, vertices=8, parent=e, rough=0.25)
    m = newmat(f'torch{i}', 'FFF2C0', 0.3, 0.0)
    wear(add('cylinder', 'FFF2C0', (0, 0, 0.26), radius=0.085, depth=0.02, vertices=8, parent=e), m)
    return e, m


def make_tank(col='D8DCE4'):
    e = keep(empty(AWAY))
    add('cylinder', col, (0, 0, 0), radius=0.2, depth=1.1, vertices=8, parent=e, rough=0.3)
    add('ico_sphere', col, (0, 0, 0.55), scale=(1, 1, 0.6), radius=0.2, subdivisions=1, parent=e, rough=0.3)
    add('cylinder', '22262E', (0, 0, 0.72), radius=0.06, depth=0.16, vertices=6, parent=e)
    add('cube', '22262E', (0.1, 0, 0.78), scale=(0.22, 0.07, 0.07), size=1, parent=e)
    return e


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = dict(colls={})
    for name, fn in (('mouth', set_mouth), ('tun', set_tun), ('ledge', set_ledge), ('sump', set_sump)):
        S['colls'][name], S[name] = stage(name, fn)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['rook'].sc = 1.0
    S['team'] = []
    for i in range(13):
        coach = i == 12
        rig = K.Rig(dict(top='34466A' if coach else SHIRTS[i % 6], pants='1E2230', hand=SKINS[i % 3], boot='D8D4C8' if i % 2 else '2A2C34',
                         fore=SKINS[i % 3]), K.human_head(SKINS[i % 3], '17131A'))
        rig.sc = 1.0 if coach else 0.70 + 0.045 * ((i * 5) % 5)
        S['team'].append(rig)
    S['pat'] = K.Rig(dict(top='2A4E8A', pants='1E2A44', hand=SKINS[1], boot='171A20'), K.human_head(SKINS[1], '14161C'))   # a boy in a wetsuit
    S['pat'].sc = 0.8
    S['divers'] = []
    for helm in ('C8372D', 'E4DFD0'):
        d = K.Rig(dict(top='1B1E26', pants='1B1E26', hand='101216', boot='E0C020'), cave_diver(helm))
        d.sc = 1.0
        for s in (-1, 1):                                                                              # side-mounted cylinders
            add('cylinder', 'B8BCC8', (s * 0.47, 0.08, 0.3), radius=0.13, depth=0.95, vertices=7, parent=d.body, rough=0.3)
        for kn in d.kn:                                                                                # fins
            add('cube', 'E0C020', (0, -0.55, -0.5), scale=(0.3, 0.9, 0.06), size=1, parent=kn)
        S['divers'].append(d)
    S['res'] = []
    for col in ('E8E4D8', 'E0B030'):
        rr = K.Rig(dict(top='C86A22', pants='2A3040', hand=SKINS[0], boot='22262E'), hard_hat(col))
        rr.sc = 1.0
        S['res'].append(rr)
    S['humans'] = S['team'] + [S['pat']] + S['res']
    S['cast'] = [S['rook']] + S['humans'] + S['divers']
    S['mask'] = mk = keep(empty(AWAY))                                                                  # a full-face mask
    add('cube', 'BFEFFF', (0, 0, 0.0), scale=(0.5, 0.05, 0.44), size=1, parent=mk, rough=0.05, alpha=0.3)
    for z in (-0.23, 0.23):
        add('cube', 'E0C020', (0, 0, z), scale=(0.56, 0.1, 0.06), size=1, parent=mk)
    for x in (-0.27, 0.27):
        add('cube', 'E0C020', (x, 0, 0), scale=(0.06, 0.1, 0.5), size=1, parent=mk)
    add('cylinder', '9AA0B4', (0, -0.08, -0.13), rot=(PI / 2, 0, 0), radius=0.11, depth=0.14, vertices=7, parent=mk, rough=0.35)
    S['torch'] = [make_torch(i) for i in range(3)]
    S['tanks'] = [make_tank('D8DCE4' if i % 2 else 'E0C020') for i in range(5)]
    S['fea'] = [keep(add('cone', '2F2B4D', AWAY, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(2)]
    S['foam'] = [keep(add('ico_sphere', 'DCE8EC', AWAY, radius=0.2, subdivisions=1, rough=0.3)) for _ in range(14)]
    S['drops'] = [keep(add('ico_sphere', 'CFE8FF', AWAY, radius=0.05, subdivisions=1, emit=1.2)) for _ in range(8)]
    S['rings'] = [keep(add('torus', '9FD0E0', AWAY, major_radius=1.0, minor_radius=0.03, major_segments=16, minor_segments=4, emit=0.25)) for _ in range(3)]
    S['streamm'] = newmat('stream', '8FA8B4', 0.08, 0.15)
    S['streams'] = [keep(wear(add('cube', '8FA8B4', AWAY, scale=(2.4, 3.4, 0.1), size=1), S['streamm'])) for _ in range(7)]
    S['ropes'] = [keep(add('cylinder', LINE, AWAY, radius=0.5, depth=1, vertices=5, rough=0.7, emit=0.5)) for _ in range(3)]
    S['weight'] = keep(add('cone', 'B8BCC8', AWAY, rot=(PI, 0, 0), radius1=0.09, radius2=0.02, depth=0.3, vertices=5, rough=0.3))
    S['hands'] = [K.Hand('101216', '1B1E26', 1.0) for _ in range(2)]
    S['bhand'] = K.Hand(SKINS[0], SHIRTS[0], 1.0)
    for hnd in S['hands'] + [S['bhand']]:
        keep(hnd.root)
    S['stretcher'] = st = keep(empty(AWAY))
    add('cube', 'D8822A', (0, 0, 0), scale=(0.95, 3.0, 0.1), size=1, parent=st)
    for x in (-0.5, 0.5):
        add('cylinder', 'B8BCC8', (x, 0, 0), rot=(PI / 2, 0, 0), radius=0.045, depth=3.8, vertices=5, parent=st, rough=0.3)
    add('ico_sphere', 'C8D0DC', (0, 0.1, 0.25), scale=(0.42, 1.25, 0.26), radius=1, subdivisions=2, parent=st, rough=0.2)        # a foil blanket
    S['flood_prop'] = fp = keep(empty(AWAY))                                                            # a work light on a stand, left in the passage
    add('cylinder', '3A3F4C', (0, 0, 1.2), radius=0.06, depth=2.4, vertices=5, parent=fp)
    S['fpm'] = newmat('worklight', 'FFF2D0', 0.4, 0.0)
    wear(add('cube', 'FFF2D0', (0, -0.1, 2.5), scale=(0.9, 0.2, 0.6), size=1, parent=fp), S['fpm'])
    S['lamps'] = [light(AWAY, 0, 'FFF0C8', kind='POINT') for _ in range(5)]
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 5000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    S['fill'] = light((0, 0, 0), 0, 'FFFFFF', 3.0, tgt)
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    sc.world = w
    S['bg'] = w.node_tree.nodes['Background']
    S['fillk'] = 0.0
    reset(S)
    return S


def sky(S, col, strength=1.0):
    S['bg'].inputs[0].default_value = K.hexc(col)
    S['bg'].inputs[1].default_value = strength


def only(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: loc(name, x, y, z)


def shoot(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='DCE4F4'):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    dx, dy, dz = look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    hh = math.hypot(dx, dy) + 1e-6
    S['fill'].location = (pos[0] - dy / hh * 0.3 * d, pos[1] + dx / hh * 0.3 * d, pos[2] + 0.3 * d)
    S['fill'].data.energy = S['fillk'] * fill * min(d, 14) ** 2
    S['fill'].data.size = max(2.0, 0.3 * d)
    S['fill'].data.color = K.hexc(fcol)[:3]


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(AWAY)
        rig.apply(P())
        rig.root.scale = (rig.sc,) * 3
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for hnd in S['hands'] + [S['bhand']]:                              # the close-up hands were built at the origin: park them out of sight
        hnd.root.location = AWAY
    for d in S['divers']:
        d.extra['lamp'].data.energy = 0
        d.extra['cone'].hide_render = True
    for _, m in S['torch']:
        paint(m, 'FFF2C0', 0.0)
    M = S['mouth']
    seen(M['kit'], False)
    paint(M['floodm'], 'FFF2D0', 0.0)
    for l in M['floods']:
        l.data.energy = 0
    M['pump'].location = (PUMP[0], PUMP[1], 0)
    M['pump'].rotation_euler = (0, 0, 0)
    M['wheel'].rotation_euler = (0, 0, 0)
    paint(S['ledge']['glowm'], 'BFF2FF', 0.0)
    S['ledge']['glow'].hide_render = True
    S['ledge']['glowl'].data.energy = 0
    paint(S['fpm'], 'FFF2D0', 0.0)
    paint(S['streamm'], '8FA8B4', 0.15)
    for l in S['lamps']:
        l.location = AWAY
        l.data.energy = 0
        l.data.color = K.hexc('FFF0C8')[:3]
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['rface'] = 'calm'
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
    S['hat_jump'] = 0.0
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.43) % 1 < 0.035
    ez = dict(calm=0.07, deadpan=0.05, shocked=0.13, sad=0.055, warm=0.06, shut=0.012).get(e, 0.07)
    tilt = dict(deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], sm(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + (0.12 if e == 'deadpan' else 0.0) + tip * 0.35, 1.35, off), lerp(0.07, 0.0, off), 0)
    r['hat'].location = (0.0, lerp(0.0, -0.5, off), lerp(0.27 + S['hat_jump'] + tip * 0.1, -0.92, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.7, shut=0.07, tired=0.5, warm=0.85, squint=0.35, sad=0.6).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for br in x['brows']:
            br.location.z = 0.125 + (0.03 if f == 'wide' else -0.012 if f in ('sad', 'tired', 'squint') else 0.0)
        x['jaw'].rotation_euler = (0, 0, 0)
        x['mouth'].scale = (0.13 if f != 'warm' else 0.17, 0.03, 0.035 + 0.12 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def env(S, name, skyc='000000', sun=0.0, sunc='FFFFFF', sdir=(-0.4, -0.6, 0.7), fk=2.4, skyk=1.0):
    A = only(S, name)
    sky(S, skyc, skyk)
    S['suntgt'].location = A(0, 0, 0)
    S['sun'].location = A(sdir[0] * 400, sdir[1] * 400, sdir[2] * 400)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(sunc)[:3]
    S['fillk'] = fk
    return A


def rain_eve(S, flash=0.0):
    """The cave mouth in the monsoon, late in the day."""
    return env(S, 'mouth', lerp_hex('6E808E', 'E8F0FF', flash), sun=2.6 + 8 * flash, sunc='B8C8E0', sdir=(-0.3, -0.7, 0.6), fk=2.2, skyk=2.0 + 3.0 * flash)


def rescue_dusk(S):
    """The same mouth during the rescue: pumps, hoses and work lights."""
    A = env(S, 'mouth', '3A4A78', sun=1.6, sunc='9FB4F0', sdir=(0.4, -0.6, 0.6), fk=2.4, skyk=1.6)
    M = S['mouth']
    seen(M['kit'], True)
    paint(M['floodm'], 'FFF2D0', 9.0)
    for l in M['floods']:
        l.data.energy = 9000
    return A


def morning(S):
    return env(S, 'mouth', '9CC4DC', sun=4.5, sunc='FFE8C8', sdir=(0.5, -0.7, 0.5), fk=2.0, skyk=2.2)


def passage(S, wl=0.0):
    A = env(S, 'tun', '000000', fk=2.4)
    S['tun']['water'].location = (0, 4, wl - 3.0)
    return A


def chamber(S):
    return env(S, 'ledge', '000000', fk=2.2)


def sump(S):
    return env(S, 'sump', '06201A', fk=2.0, skyk=0.6)


def lerp_hex(a, b, k):
    k = max(0.0, min(1.0, k))
    pa, pb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(pa, pb))


def world_of(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def lampat(S, i, pos, e, col='FFF0C8'):
    S['lamps'][i].location = pos
    S['lamps'][i].data.energy = e
    S['lamps'][i].data.color = K.hexc(col)[:3]


def torch(S, i, rig, e=1.0, hand=1, li=None, watts=120):
    """Put a lit torch in a rig's hand, with a small light in front of it."""
    obj, m = S['torch'][i]
    obj.location = world_of(rig.hands[hand], (0, -0.12, -0.05))
    obj.rotation_euler = (-PI / 2, 0, rig.root.rotation_euler[2])
    paint(m, 'FFF2C0', 12.0 * e)
    if li is not None:
        lampat(S, li, world_of(rig.hands[hand], (0, -1.3, 0.5)), watts * e)


def dlamp(S, d, e=6000, cone=True):
    d.extra['lamp'].data.energy = e
    d.extra['cone'].hide_render = not cone


def rope(S, i, a, b, w=0.03):
    span(S['ropes'][i], a, b, w)


def feather(S, pos, lt, t0=0.0, n=2):
    for i in range(n):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def foam(S, pts, s=1.0):
    for o, p in zip(S['foam'], pts):
        o.location = p
        o.scale = (s, s, s * 0.7)


def drips(S, pos, t, n=4, spread=0.5, fall=2.4, rate=1.3):
    """Drops falling from a point (a hat brim, a stalactite)."""
    for i in range(n):
        u = (t * rate + i / n) % 1
        S['drops'][i].location = (pos[0] + spread * math.cos(i * 2.4), pos[1] + spread * 0.5 * math.sin(i * 2.4), pos[2] - fall * u * u)


def bubbles(S, pos, t, n=6, i0=0, rise=1.6):
    for i in range(n):
        u = (t * 0.9 + i / n) % 1
        o = S['foam'][i0 + i]
        o.location = (pos[0] + 0.25 * math.sin(i * 2.2 + t * 3), pos[1] + 0.25 * math.cos(i * 1.7), pos[2] + rise * u)
        s = 0.25 + 0.35 * u
        o.scale = (s, s, s)


def to_chest(**over):
    d = dict(aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.28, 0.0))
    d.update(over)
    return P('stand', **d)


KNEE = P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.4, aL=(0.6, 0.1, 0.7), aR=(1.0, 0.0, 0.5), head=(0.3, 0.0))
HUG = dict(lL=(1.75, 2.1), lR=(1.75, 2.1), aL=(1.2, -0.2, 1.2, 0.6), aR=(1.2, -0.2, 1.2, 0.6), lift=-0.62, lean=0.42)


def seat_team(S, A, t, face='tired', turn=0.0, nod=0.3, skip=()):
    """The thirteen sitting on the slope of mud: twelve boys in three rows and the coach at the back."""
    for i, (rig, (x, y)) in enumerate(zip(S['team'], SEATS)):
        if i in skip:
            continue
        rig.place(A(*lp(x, y)), 0.2 * math.sin(i * 2.1))
        d = dict(HUG)
        if i % 3 == 1:
            d.update(aL=(0.9, 0.15, 0.5), aR=(0.9, 0.15, 0.5))
        elif i % 3 == 2:
            d.update(aL=(0.5, 0.3, 1.2, 0.8), aR=(1.1, 0.1, 2.0, 0.6))
        d['head'] = (nod + 0.05 * math.sin(t * 1.3 + i), turn + 0.25 * math.sin(i * 1.7) * (1 - abs(turn)))
        rig.apply(P('sit', **d))
        rig.face = face
    S['team'][12].face = 'calm' if face == 'tired' else face


def wade(S, A, rigs, pts, t, yaw=0.0, face='wide', bob=0.0):
    for i, (rig, p) in enumerate(zip(rigs, pts)):
        rig.place(A(p[0], p[1], p[2] + bob * abs(math.sin(t * 5 + i))), yaw + 0.15 * math.sin(t * 3 + i * 2))
        rig.apply(walk(t + i * 0.37, 1.9))
        rig.face = face
        rig.jawv = 0.5 if face == 'wide' else 0.0


def swim_pose(t, sp=1.2, hold=False):
    s = math.sin(t * sp * 2 * PI)
    arms = dict(aL=(1.0, 0.15, 1.2, 0.5), aR=(1.0, 0.15, 1.2, 0.5)) if hold else dict(aL=(2.6 + 0.3 * s, 0.2, 0.3 - 0.2 * s), aR=(2.6 - 0.3 * s, 0.2, 0.3 + 0.2 * s))
    return P('stand', lL=(0.3 * s, 0.25 + 0.2 * s), lR=(-0.3 * s, 0.25 - 0.2 * s), head=(-0.9, 0.0), **arms)


def limp_pose():
    return P('stand', aL=(0.25, 0.25, 0.3), aR=(0.25, 0.25, 0.3), lL=(0.1, 0.25), lR=(-0.05, 0.2), head=(-0.2, 0.0))


def wear_mask(S, rig):
    S['mask'].parent = rig.head
    S['mask'].location, S['mask'].rotation_euler = (0, -0.31, 0.0), (0, 0, 0)


# ---------------------------------------------------------------- the hook: into the cave, and the rain
def mouth_wide(S, k, t, lt):
    loop = S['prm'].get('loop')
    kk = 1 - k if loop else k
    fl = max(0.0, 1 - lt / 0.14) if not loop else sm((k - 0.9) / 0.1)
    A = rain_eve(S, fl)
    for j, o in enumerate(S['streams']):
        y = -22 + ((j * 6.0 + t * 15) % 42)
        o.location = A(0.7 * math.sin(j * 1.9 + y * 0.2), y, mz(y) + 0.1)
        o.rotation_euler = (-0.09 if y > 14 else 0, 0, 0.2 * math.sin(j + y * 0.3))
    T = S['team']
    for i, rig in enumerate((T[12], T[3], T[7])):
        y = 2.0 + 2.6 * (2 - i) + 2.6 * kk
        rig.place(A(-1.2 + 1.2 * i, y, mz(y)), PI + 0.1 * (i - 1))
        rig.apply(walk(t + i * 0.3, 1.7))
    torch(S, 0, T[3], 1.0, li=0, watts=300)
    lampat(S, 1, A(0, 9, 5), 500, 'DCE8F4')
    S['mouth']['wheel'].rotation_euler = (t * 2.2, 0, 0)
    shoot(S, A(lerp(-6.4, -5.9, kk), lerp(-17.6, -16.2, kk), lerp(1.5, 1.8, kk)), A(-2.2, 4.0, 4.6), 22, fill=0.8)


def walk_in(S, k, t, lt):
    A = rain_eve(S)
    T = S['team']
    order = (T[0], T[5], T[2], T[9], T[4], T[12])
    for i, rig in enumerate(order):
        y = 17.5 - 2.0 * i + 3.2 * k
        x = (-1.3, 1.1, -0.2, 1.6, -1.6, 0.3)[i]
        rig.place(A(x, y, mz(y)), PI + 0.12 * math.sin(i * 2.0))
        rig.apply(walk(t + i * 0.31, 1.7, 'stand'))
        rig.face = 'warm' if i % 2 else 'calm'
    torch(S, 0, order[0], 1.0, li=0, watts=260)
    torch(S, 1, order[2], 1.0, li=1, watts=200)
    for j, o in enumerate(S['streams'][:4]):
        y = 12 + ((j * 4.0 + t * 9) % 14)
        o.location = A(3.6 + 0.4 * math.sin(j * 2.0), y, mz(y) + 0.08)
        o.scale = (1.2, 2.6, 0.08)
        o.rotation_euler = (-0.09 if y > 14 else 0, 0, 0)
    shoot(S, A(lerp(0.9, 0.5, k), lerp(25.5, 24.6, k), mz(25) + lerp(1.7, 1.9, k)), A(0.0, 14.0, 1.7), 27, fill=0.8)


def bikes(S, k, t, lt):
    A = rain_eve(S)
    S['mouth']['wheel'].rotation_euler = (t * 2.6, 0, 0)
    rk = S['rook']
    rp = (-5.2, -11.0, 1.2)
    rk.place(A(*rp), look_yaw(rp, (0, 14)) + lerp(0.0, 2.6, sm((lt - 0.45) / 0.3)))
    rk.apply(P('cross', head=(0.1, 0.0), lean=0.05))
    S['rface'] = 'deadpan'
    drips(S, world_of(rk.head, (0, -0.5, 0.25)), t, 4, 0.45, 1.6)
    for j, o in enumerate(S['streams'][:5]):
        y = -24 + ((j * 6.0 + t * 15) % 40)
        o.location = A(0.7 * math.sin(j * 1.9 + y * 0.2), y, 0.1)
    lampat(S, 0, A(-3.9, -14.0, 3.3), 900, 'FFC890')
    shoot(S, A(lerp(-2.2, -2.8, k), lerp(-18.6, -18.0, k), lerp(1.3, 1.6, k)), A(-6.0, -11.4, 2.3), 24, fill=1.0)


def rain_gush(S, k, t, lt):
    A = rain_eve(S)
    paint(S['streamm'], '4E86AC', 0.5)
    for j, o in enumerate(S['streams']):
        y = 12 + ((j * 1.9 + t * 11) % 11)
        o.location = A(-3.9 + 1.3 * j + 0.3 * math.sin(t * 5 + j), y, mz(y) + 0.2 + 0.12 * math.sin(t * 9 + j))
        o.scale = (2.2, 3.4, 0.4)
        o.rotation_euler = (-0.09 if y > 14 else 0, 0, 0.25 * math.sin(j * 1.3))
    foam(S, [A(-4.2 + 8.4 * rn(i, 80), 15.0 + ((i * 1.3 + t * 9) % 6.5), mz(18) + 0.4 + 0.8 * abs(math.sin(t * 8 + i))) for i in range(14)], 2.0)
    lampat(S, 0, A(0, 19, 4), 1500, 'BFD4E8')
    shoot(S, A(lerp(1.6, 1.0, k), lerp(23.6, 22.6, k), mz(23) + lerp(1.0, 1.3, k)), A(0.0, 14.0, 0.9), 20, roll=0.05 * math.sin(t * 3), fill=1.2)


def fill(S, k, t, lt):
    wl = lerp(0.35, 1.5, sm(k * 1.05))
    A = passage(S, wl)
    T = S['team']
    rigs = (T[1], T[6], T[10])
    pts = [(-1.7 + 1.7 * i, 6.0 - 2.2 * i - 5.0 * k, 0.0) for i in range(3)]
    wade(S, A, rigs, pts, t, 0.0, 'wide', 0.12)
    torch(S, 0, rigs[0], 1.0, li=0, watts=500)
    torch(S, 1, rigs[2], 1.0, li=1, watts=500)
    surge = sm(k * 1.2)
    foam(S, [A(-3.6 + 7.2 * rn(i, 81), 17.4 - 9 * surge * rn(i, 82), wl + 0.2 + (1.6 - 1.2 * rn(i, 82)) * surge * (0.6 + 0.4 * abs(math.sin(t * 7 + i))))
             for i in range(14)], 2.2)
    lampat(S, 2, A(0, 11, 5.0), 2600, 'A8D8E8')
    lampat(S, 3, A(1.5, -3 - 5 * k, 3.5), 700, 'FFD8B0')
    shoot(S, A(lerp(0.9, 0.5, k), lerp(-3.2, -7.4, k), lerp(2.0, 2.5, k)), A(0.0, lerp(8.0, 5.0, k), 1.9), 24, roll=0.03 * math.sin(t * 4), fill=1.4)


# ---------------------------------------------------------------- Rook, in the flood
def rook_on_rock(S, A, t, shake=1.0):
    rk = S['rook']
    rk.place(A(BOULDER[0], BOULDER[1], BOULDER[2]), -0.75, 0.0, 0.06 * shake * math.sin(t * 34))
    return rk


def flood_run(S, A, t, wl):
    foam(S, [A(-4.5 + 9 * rn(i, 84), 16 - ((i * 2.7 + t * 9) % 30), wl + 0.08 + 0.12 * math.sin(t * 6 + i)) for i in range(14)], 1.2)


def rook_rock(S, k, t, lt):
    wl = 2.1 + 0.06 * math.sin(t * 3)
    A = passage(S, wl)
    sh = max(0.0, 1 - lt / 0.3)
    rk = rook_on_rock(S, A, t, sh)
    rk.apply(blend(P('shrug', head=(0.1, 0.25), lean=0.1), P('cross', head=(0.05, 0.5)), (lt - 0.2) / 0.3))
    S['rface'] = 'deadpan'
    flood_run(S, A, t, wl)
    drips(S, world_of(rk.head, (0, -0.4, 0.3)), t, 5, 0.5, 2.2, 1.6)
    lampat(S, 0, A(1.0, -1.0, 5.8), 900, 'FFC890')
    lampat(S, 1, A(0, 12, 5.5), 2200, 'A8D8E8')
    shoot(S, A(lerp(-1.0, -0.5, k), lerp(-3.6, -3.0, k), lerp(4.0, 4.3, k)), A(3.0, 2.3, 4.25), 35, fill=1.4)


def rook_drip(S, k, t, lt):
    wl = 2.1 + 0.06 * math.sin(t * 3)
    A = passage(S, wl)
    rk = rook_on_rock(S, A, t, 0.0)
    tap = 0.5 + 0.5 * math.sin(lt * 15)
    rk.apply(blend(P('cross', head=(0.05, 0.5)), P('tap', aR=(1.25 + 0.12 * tap, -0.25, 2.2, 0.6), head=(0.2, 0.5)), lt / 0.18))
    S['rface'] = 'deadpan'
    S['hat_tip'] = 0.6
    flood_run(S, A, t, wl)
    drips(S, world_of(rk.head, (0, -0.4, 0.3)), t, 5, 0.5, 1.6, 1.8)
    lampat(S, 0, A(1.0, -1.0, 5.6), 300, 'FFC890')
    lampat(S, 1, A(0, 12, 5.5), 420, 'A8D8E8')
    shoot(S, A(lerp(1.9, 2.1, k), lerp(-1.9, -1.5, k), 5.25), A(BOULDER[0] - 0.1, BOULDER[1] - 0.1, BOULDER[2] + 2.5), 50, fill=1.4)


# ---------------------------------------------------------------- deeper, and up onto the mud
def chase(S, k, t, lt):
    wl = 0.95 + 0.08 * math.sin(t * 5)
    A = passage(S, wl)
    T = S['team']
    rigs = (T[12], T[0], T[8], T[4], T[11])
    y0 = 12.0 - 5.0 * k
    pts = [((-1.5, 0.2, 1.6, -0.8, 1.0)[i], y0 - 1.5 * i, 0.0) for i in range(5)]
    wade(S, A, rigs, pts, t, 0.0, 'wide', 0.1)
    rigs[0].place(A(-1.5, y0 + 0.6, 0.0), 2.4)
    rigs[0].apply(P('stand', aR=(1.9, 0.5, 0.4 + 0.4 * math.sin(t * 9)), aL=(0.3, 0.4, 0.6), head=(0.0, -0.3), lean=0.1))       # the coach waves them on
    rigs[0].jawv = 0.8
    torch(S, 0, rigs[1], 1.0, li=0, watts=500)
    torch(S, 1, rigs[3], 1.0, li=1, watts=500)
    foam(S, [A(-4.0 + 8 * rn(i, 85), y0 + 2.2 + 3.5 * rn(i, 86), wl + 0.3 + 0.9 * rn(i, 87) * abs(math.sin(t * 8 + i))) for i in range(14)], 2.0)
    lampat(S, 2, A(0, y0 + 3, 5.5), 1800, 'A8D8E8')
    lampat(S, 3, A(2.5, y0 - 9, 3.6), 900, 'FFD8B0')
    shoot(S, A(lerp(1.5, 1.2, k), y0 - lerp(10.6, 9.8, k), lerp(2.9, 2.6, k)), A(0.0, y0 - 2.5, 1.9), 26, fill=1.4)


def scramble(S, k, t, lt):
    A = chamber(S)
    T = S['team']
    for i, rig in enumerate((T[2], T[5], T[9], T[1])):
        y = 1.0 + 1.4 * i + 1.6 * k
        x = (-1.6, 0.2, -0.8, 1.3)[i]
        rig.place(A(*lp(x, y)), PI + 0.2 * (i - 1.5), 0.75)
        s = math.sin(t * 7 + i * 1.7)
        rig.apply(P('stand', aL=(2.2 + 0.5 * s, 0.3, 0.6), aR=(2.2 - 0.5 * s, 0.3, 0.6), lL=(0.9 + 0.5 * s, 1.2), lR=(0.9 - 0.5 * s, 1.2), head=(-0.5, 0.0)))
        rig.face = 'wide'
    co = T[12]                                                         # the coach, last out of the water, pushes the smallest up
    co.place(A(-1.2, 0.0 + 0.8 * k, -0.9 + 0.3 * k), PI - 0.1, 0.3)
    co.apply(P('stand', aL=(1.7, 0.2, 0.3), aR=(1.7, 0.2, 0.3), lL=(0.5, 0.5), lR=(-0.2, 0.3), head=(-0.3, 0.0)))
    torch(S, 0, T[9], 1.0, li=0, watts=500)
    rk = S['rook']
    hop = abs(math.sin(lt * 6.5))
    rp = lp(2.5, 1.6 + 1.3 * k, 0.5 * hop)
    rk.place(A(*rp), PI - 2.0, 0.0, 0.0)
    fl = math.sin(lt * 22)
    rk.apply(P('stand', aL=(0.3, 1.3 + 0.4 * fl, 0.4), aR=(0.3, 1.3 + 0.4 * fl, 0.4), lL=(0.5 * hop, 0.6 * hop), lR=(0.3 * hop, 0.5 * hop), head=(0.0, 0.5)))
    S['rface'] = 'shocked'
    foam(S, [A(-5 + 10 * rn(i, 87), -0.6 - 3.5 * rn(i, 88), 0.05 + 0.15 * abs(math.sin(t * 7 + i))) for i in range(14)], 0.6)
    lampat(S, 1, A(3.6, -2.5, 3.6), 900, 'FFC890')
    lampat(S, 2, A(-2, -3, 4.5), 1400, 'A8D8E8')
    shoot(S, A(lerp(1.4, 1.0, k), lerp(-4.6, -3.9, k), lerp(1.3, 1.7, k)), A(0.3, 2.8, 2.1), 24, fill=1.4)


def ledge_wide(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t)
    torch(S, 0, S['team'][2], 0.8, li=0, watts=420)
    torch(S, 1, S['team'][9], 0.8, li=1, watts=420)
    lampat(S, 2, A(0, 4.5, 6.5), 900, 'FFD8A8')
    lampat(S, 3, A(0, -12, 5), 500, '7FB8D0')
    shoot(S, A(lerp(-3.0, -2.2, k), lerp(-13.5, -11.8, k), lerp(1.4, 1.8, k)), A(0.0, 3.8, 3.0), 26, fill=1.0)


# ---------------------------------------------------------------- nine nights
def huddle(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, nod=0.38)
    dim = lerp(1.0, 0.35, k) * (0.85 + 0.15 * math.sin(t * 23))
    torch(S, 0, S['team'][1], dim, li=0, watts=420)
    rk = S['rook']
    rp = lp(-5.0, 2.2)
    rk.place(A(*rp), 0.5)
    rk.apply(P('sit', **dict(HUG, head=(0.35, -0.5 + 0.3 * sm((lt - 0.5) / 0.4)))))
    S['rface'] = 'sad'
    lampat(S, 1, A(-4.6, -0.4, 3.4), 420, 'FFC890')
    lampat(S, 2, A(1, 3, 6.0), 260 * dim, 'FFD8A8')
    shoot(S, A(lerp(-1.9, -2.4, k), lerp(-2.7, -2.3, k), lerp(2.0, 2.2, k)), A(-3.5, 2.7, 1.9), 27, fill=1.1, fcol='FFE0C0')


def torch_dies(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, nod=0.45)
    h = S['bhand']
    hp = A(*lp(0.9, 1.5, 1.35))
    h.place((hp[0], hp[1] + 0.25, hp[2]), (0.25, 0.0, 0.5))
    h.grip(0.95)
    e = (0.0 if lt > 0.8 else max(0.0, (1 - lt / 0.8) * (0.6 + 0.4 * math.sin(lt * 40)) * (1 if (lt * 9) % 1 > 0.25 else 0.15)))
    obj, m = S['torch'][0]
    obj.location = (hp[0] - 0.02, hp[1] - 0.3, hp[2] - 0.1)
    obj.rotation_euler = (-PI / 2 - 0.25, 0, 0.5)
    paint(m, 'FFF2C0', 0.4 + 14 * e)
    lampat(S, 0, (hp[0] - 0.5, hp[1] - 1.4, hp[2] + 0.4), 20 + 300 * e)
    lampat(S, 2, A(1, 3, 6.0), 40 + 160 * e, 'FFD8A8')
    shoot(S, A(lerp(-0.6, -0.3, k), lerp(-0.7, -0.4, k), lerp(1.9, 1.75, k)), (hp[0], hp[1] - 0.25, hp[2] - 0.05), 44, fill=0.25 + 0.9 * e)


def diver_at(S, i, pos, yaw=0.0, t=0.0, hold=False, e=6000, cone=True, pitch=PI / 2, sp=1.2):
    d = S['divers'][i]
    d.place(pos, yaw, pitch)
    d.apply(swim_pose(t, sp, hold))
    dlamp(S, d, e, cone)
    return d


def divers_fight(S, k, t, lt):
    A = sump(S)
    y = lerp(6.5, 4.6, k) + 0.35 * math.sin(t * 5)
    p = line_pt(S, y - 3)
    d = S['divers'][0]
    d.place(A(p[0] + 0.25, y, p[2] + 0.5), 0.0, PI / 2 - 0.08, 0.1 * math.sin(t * 6))
    pull = math.sin(t * 5)
    d.apply(P('stand', aL=(2.75 + 0.3 * pull, 0.1, 0.2 - 0.2 * pull), aR=(2.75 - 0.3 * pull, 0.1, 0.2 + 0.2 * pull), lL=(0.4 * math.sin(t * 9), 0.3),
              lR=(-0.4 * math.sin(t * 9), 0.3), head=(-1.0, 0.0)))
    dlamp(S, d, 2500, False)
    bubbles(S, world_of(d.head, (0, 0, 0.2)), t, 6)
    for i, o in enumerate(S['foam'][6:]):                             # silt and debris racing past on the current
        yy = y + 3 - ((i * 3.1 + t * 13) % 7)
        o.location = A(-1.6 + 3.2 * rn(i, 89), yy, -1.4 + 2.8 * rn(i, 90))
        o.scale = (0.1, 0.45, 0.1)
    lampat(S, 0, A(1.2, y - 4.4, 1.0), 500, 'DFF6F0')
    shoot(S, A(lerp(1.0, 0.85, k), y - lerp(5.6, 5.1, k), lerp(1.3, 1.15, k)), A(p[0] + 0.25, y - 1.9, p[2] + 0.6), 30, roll=0.06 * math.sin(t * 2.2), fill=1.5,
          fcol='BFE8D8')


# ---------------------------------------------------------------- found
def glow_k(S, A, e, r=2.5):
    L = S['ledge']
    paint(L['glowm'], '2FA8C8', 0.5 * e)
    L['glow'].hide_render = e <= 0.01
    L['glow'].scale = (r, r, 1)
    L['glowl'].data.energy = 1800 * e


def glow(S, k, t, lt):
    A = chamber(S)
    e = sm(k * 1.15)
    seat_team(S, A, t, face='wide' if e > 0.45 else 'tired', nod=lerp(0.4, 0.15, e))
    glow_k(S, A, e, lerp(0.8, 3.0, e))
    rk = S['rook']
    rp = lp(3.4, 6.2)
    rk.place(A(*rp), 0.25)
    rk.apply(blend(P('sit', **HUG), P('stand', lean=0.45, head=(0.3, 0.0), aL=(0.4, 0.5, 0.4), aR=(0.4, 0.5, 0.4)), (lt - 0.3) / 0.4))
    S['rface'] = 'shocked' if e > 0.5 else 'sad'
    S['hat_jump'] = 0.25 * sm((e - 0.5) / 0.2) * max(0.0, 1 - (e - 0.7) / 0.3)
    lampat(S, 1, A(2, 10, 6.5), 200, 'FFD8A8')
    foam(S, [A(0.9 * math.cos(i * 0.9) * (0.5 + e), -3.2 + 0.9 * math.sin(i * 0.9) * (0.5 + e), 0.05) for i in range(8)], 0.5 * e)
    shoot(S, A(lerp(2.6, 2.0, k), lerp(10.6, 9.8, k), lerp(6.2, 5.8, k)), A(0.3, lerp(1.0, -0.6, k), 0.8), 26, fill=0.5)


def surface(S, k, t, lt):
    A = chamber(S)
    up = sm(lt / 0.5)
    S['ledge']['glowl'].data.energy = 500 * (1 - 0.5 * up)
    d = S['divers'][0]
    d.place(A(0.0, -3.2, lerp(-3.0, -1.55, up) + 0.04 * math.sin(t * 4)), look_yaw((0, -3.2), (2.0, 4.0)))
    d.apply(P('stand', aL=(0.3, 0.3, 0.5), aR=(lerp(0.3, 2.3, sm((lt - 0.55) / 0.3)), 0.3, 0.4), head=(-0.15, 0.0)))
    dlamp(S, d, 7000, True)
    d2 = S['divers'][1]
    up2 = sm((lt - 0.35) / 0.5)
    d2.place(A(-2.2, -5.4, lerp(-3.0, -1.7, up2)), look_yaw((-2.2, -5.4), (0, 4.0)))
    d2.apply(P('stand', aL=(0.4, 0.6, 0.5), aR=(0.4, 0.6, 0.5)))
    dlamp(S, d2, 3000 * up2, False)
    for i, o in enumerate(S['rings']):
        u = max(0.0, lt - 0.12 - 0.22 * i)
        if u > 0:
            o.location = A(0.0, -3.2, 0.03)
            o.scale = (0.5 + 2.6 * u, 0.5 + 2.6 * u, 1)
    for i, o in enumerate(S['drops']):
        u = max(0.0, lt - 0.15)
        o.location = A(0.9 * math.cos(i * 0.8) * (0.4 + 1.6 * u), -3.2 + 0.9 * math.sin(i * 0.8) * (0.4 + 1.6 * u), 0.3 + 3.0 * u - 4.5 * u * u)
        o.scale = (1.4, 1.4, 1.4)
    lampat(S, 0, A(3.0, 0.5, 2.6), 500, 'FFD8A8')
    shoot(S, A(lerp(3.0, 2.6, k), lerp(0.2, -0.2, k), lerp(0.7, 0.95, k)), A(-0.2, -3.3, lerp(0.3, 0.75, up)), 30, fill=1.0)


def faces_lit(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='wide', nod=0.05)
    T = S['team']
    for i in (0, 1, 2, 3, 4, 6, 7):                                    # hands up against the light, then they are on their feet
        rig = T[i]
        x, y = SEATS[i]
        st = sm((lt - 0.35 - 0.06 * i) / 0.35)
        rig.place(A(*lp(x, y)), 0.1 * math.sin(i * 2.1))
        shield = P('sit', aR=(2.0, 0.3, 1.5, 0.6), head=(0.1, 0.0))
        cheer = P('up', aL=(2.7 + 0.2 * math.sin(t * 14 + i), 0.4, 0.2), aR=(2.7 - 0.2 * math.sin(t * 14 + i), 0.4, 0.2), head=(-0.1, 0.0),
                  lift=0.12 * abs(math.sin(t * 9 + i)))
        rig.apply(blend(shield, cheer if i % 2 == 0 else P('stand', aR=(2.0, 0.3, 1.2, 0.5)), st))
        rig.face = 'squint' if st < 0.4 else 'warm'
        rig.jawv = st
    lampat(S, 0, A(0.5, -3.0, 1.6), 2600, 'E8F6FF')
    lampat(S, 1, A(-3, -2.0, 3.5), 500, 'E8F6FF')
    shoot(S, A(lerp(0.8, 0.4, k), lerp(-3.4, -2.6, k), lerp(1.3, 1.6, k)), A(0.0, 3.6, 2.5), 27, fill=1.4)


def rook_count(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='warm', nod=0.1, turn=-0.3 + 0.6 * k)
    for rig in S['team']:
        rig.jawv = 0.4
    rk = S['rook']
    x = lerp(-4.4, 3.2, sm(k / 0.8))
    rp = lp(x, 1.25)
    end = sm((k - 0.8) / 0.12)
    rk.place(A(*rp), lerp(look_yaw(rp, (rp[0] + 1.0, rp[1] + 0.7)), look_yaw(rp, (rp[0] + 2.0, rp[1] - 2.2)), end))
    jab = 0.25 * abs(math.sin(lt * 15))
    rk.apply(blend(blend(walk(t, 1.5), P('point', aR=(1.45 + jab, -0.1, 0.1), head=(-0.05, 0.0)), 0.75), P('point', aR=(1.7, -0.2, 0.05), head=(-0.3, 0.0)), end))
    S['rface'] = 'shocked' if end > 0.3 else 'calm'
    S['hat_jump'] = 0.3 * end
    d = S['divers'][0]
    d.place(A(5.6, -0.6, -1.5), look_yaw((5.6, -0.6), (0, 4)))
    d.apply(P('stand', aL=(0.4, 0.6, 0.5), aR=(0.4, 0.6, 0.5)))
    dlamp(S, d, 5000, False)
    lampat(S, 0, A(0, -2.6, 3.0), 1500, 'E8F6FF')
    lampat(S, 1, A(x, -1.6, 3.4), 260, 'FFC890')
    shoot(S, A(x + lerp(4.6, 2.6, k), lerp(-2.4, -3.0, k), lerp(2.3, 2.6, k)), A(x * 0.8, 2.6, 2.3), 25, fill=1.2)


# ---------------------------------------------------------------- the easy part is over
def way_out(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.2, skip=(12,))
    d = S['divers'][0]
    dp = (0.9, -1.3)
    d.place(A(dp[0], dp[1], -1.45), look_yaw(dp, (-1.0, 1.4)))
    pt = sm((lt - 0.2) / 0.35)
    d.apply(blend(P('stand', aL=(0.4, 0.5, 0.5), aR=(0.4, 0.5, 0.5)), P('stand', aR=(-1.0, 1.1, 0.1), aL=(0.4, 0.5, 0.5), head=(0.0, -1.0)), pt))
    dlamp(S, d, 1200, False)
    co = S['team'][12]
    cp = lp(-1.0, 1.25)
    co.place(A(*cp), look_yaw(cp, dp))
    co.apply(dict(KNEE, head=(0.25, 0.0)))
    co.face = 'calm'
    rope(S, 0, A(2.2, 0.9, 0.35), A(3.4, -7.0, -0.3))
    S['weight'].location = A(2.2, 0.9, 0.2)
    S['weight'].scale = (2, 2, 2)
    lampat(S, 0, A(-1.5, -3.5, 3.0), 1200, 'E8F6FF')
    lampat(S, 1, A(4, -8, 2.5), 900, '7FD0E0')
    shoot(S, A(lerp(-3.8, -3.3, k), lerp(-4.2, -3.6, k), lerp(1.3, 1.5, k)), A(0.3, lerp(-0.2, -0.6, k), 1.25), 27, fill=1.3)


def sump_long(S, k, t, lt):
    A = sump(S)
    y = lerp(4.0, 14.5, k)
    for i, o in enumerate(S['foam']):                                 # silt hanging in the water
        yy = y + 1.5 + ((i * 2.3 + 7) % 14)
        o.location = A(-2 + 4 * rn(i, 91), yy, -1.6 + 3.2 * rn(i, 92) + 0.1 * math.sin(t * 2 + i))
        o.scale = (0.12, 0.12, 0.12)
    lampat(S, 0, A(0.4, y + 2.5, 0.6), 320, 'DFF6F0')
    lampat(S, 1, A(-0.4, y + 9, 0.2), 260, 'BFE8D8')
    shoot(S, A(0.35 + 0.25 * math.sin(t * 1.4), y, 0.25 + 0.15 * math.sin(t * 1.9)), A(0.0, y + 9.0, -0.35), 20, roll=0.07 * math.sin(t * 1.3), fill=0.45,
          fcol='BFE8D8')


def toe_dip(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.25, skip=(3,))
    b = S['team'][3]
    bp = lp(0.3, 1.05)
    dip = sm(lt / 0.35) * (1 - sm((lt - 0.55) / 0.2))
    back = sm((lt - 0.6) / 0.3)
    b.place(A(bp[0], bp[1] + 0.5 * back, bp[2] + 0.15 * back), 0.15)
    b.apply(blend(P('stand', lR=(0.9 * dip, 0.1), aL=(0.3, 0.7, 0.4), aR=(0.3, 0.7, 0.4), head=(0.5, 0.0), lean=0.1),
                  P('cross', head=(0.3, -0.4), lean=-0.05, lift=-0.05), back))
    b.face = 'wide' if back > 0.3 else 'calm'
    rk = S['rook']
    rp = lp(2.2, 1.1)
    rk.place(A(*rp), 0.35)
    low = sm(lt / 0.9)
    rk.apply(P('stand', aR=(1.35, 0.15, 0.25 + 0.3 * math.sin(lt * 9)), head=(0.45, 0.2), lean=0.3))
    S['rface'] = 'calm'
    hand = world_of(rk.hands[1], (0, -0.1, -0.1))
    bob = (hand[0], hand[1] - 0.2, hand[2] - 0.5 - 2.6 * low)
    rope(S, 0, hand, bob, 0.02)
    S['weight'].location = bob
    S['weight'].scale = (1.3, 1.3, 1.3)
    for i, o in enumerate(S['rings'][:2]):
        u = (lt * 0.9 + 0.5 * i) % 1
        o.location = (bob[0], bob[1], A(0, 0, 0.03)[2])
        o.scale = (0.15 + 0.5 * u, 0.15 + 0.5 * u, 1)
    lampat(S, 0, A(-0.5, -2.6, 2.6), 900, 'E8F6FF')
    lampat(S, 1, A(3.5, -1.5, 3.2), 420, 'FFC890')
    shoot(S, A(lerp(-2.6, -2.2, k), lerp(-2.9, -2.5, k), lerp(1.0, 1.25, k)), A(1.2, 1.0, 1.75), 26, fill=1.2)


def rook_sound(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.25)
    rk = S['rook']
    rp = lp(2.2, 1.1)
    rk.place(A(*rp), 0.35)
    j = sm((lt - 0.3) / 0.15)
    rk.apply(blend(P('stand', aR=(1.35, 0.15, 0.4), head=(0.5, 0.2), lean=0.3), P('stand', aR=(1.2, 0.2, 0.9), head=(-0.05, 0.0), lean=0.0), j))
    S['rface'] = 'shocked' if j > 0.5 else 'calm'
    S['hat_jump'] = 0.3 * j * max(0.0, 1 - (lt - 0.45) / 0.4)
    hand = world_of(rk.hands[1], (0, -0.1, -0.1))
    rope(S, 0, hand, (hand[0], hand[1] - 0.25, A(0, 0, -3.5)[2]), 0.02)
    feather(S, world_of(rk.head, (0.3, 0.2, 0.0)), lt, 0.4, 1)
    lampat(S, 0, A(1.5, -2.6, 2.6), 600, 'E8F6FF')
    lampat(S, 1, A(4.0, -0.5, 3.6), 300, 'FFC890')
    shoot(S, A(lerp(3.5, 3.3, k), lerp(-1.9, -1.6, k), lerp(2.3, 2.5, k)), A(2.2, 1.0, lp(2.2, 1.1)[2] + 2.3), 40, fill=1.3)


# ---------------------------------------------------------------- Saman Kunan
def tank_row(S, A, n=4):
    for i in range(n):
        tk = S['tanks'][i]
        tk.location = A(-3.9 + 0.12 * (i % 2), 0.4 + 2.3 * i, 0.55)
        tk.rotation_euler = (0.12, 0.1 * (i % 2), 0.4 * i)
    rope(S, 0, A(-4.3, -6, 1.3), A(-4.2, 5, 1.2))
    rope(S, 1, A(-4.2, 5, 1.2), A(-3.6, 16, 0.9))


def tank_carry(S, k, t, lt):
    A = passage(S, 0.5)
    tank_row(S, A, 2)
    d = S['divers'][1]
    y = lerp(-2.5, 3.2, k)
    d.place(A(-2.3, y, 0.0), PI + 0.1 * math.sin(t * 4))
    w = walk(t, 1.5)
    d.apply(dict(w, aL=(1.0, -0.1, 1.2, 0.5), aR=(1.0, -0.1, 1.2, 0.5), head=(0.1, 0.35 * math.sin(t * 2.5))))
    tk = S['tanks'][3]
    tk.location = world_of(d.body, (0.0, -0.5, 0.75))
    tk.rotation_euler = (0.0, PI / 2 - 0.15, PI + 0.1)
    dlamp(S, d, 6000, True)
    foam(S, [world_of(d.root, (0.5 * math.cos(i * 1.3), 0.6 * math.sin(i * 1.3) + 0.5, 0.55 + 0.2 * abs(math.sin(t * 9 + i)))) for i in range(6)], 0.45)
    lampat(S, 0, A(0.5, y + 4.5, 3.0), 1500, 'FFE8C8')
    lampat(S, 1, A(0, 14, 5), 1200, '7FB8D0')
    shoot(S, A(lerp(1.4, 0.6, k), y + lerp(5.6, 4.6, k), lerp(1.5, 1.9, k)), A(-2.2, y + 0.3, 1.9), 26, roll=0.03 * math.sin(t * 3), fill=1.3)


def tanks(S, k, t, lt):
    A = passage(S, 0.12)
    tank_row(S, A, 3)
    d = S['divers'][1]
    dp = (-2.5, 7.2)
    d.place(A(dp[0], dp[1], 0.0), look_yaw(dp, (-4.4, 7.4)))
    put = sm(lt / 0.55)
    look = sm((lt - 0.7) / 0.3)
    d.apply(dict(KNEE, aL=(1.2 - 0.3 * put, 0.1, 0.5), aR=(1.2 - 0.3 * put, 0.1, 0.5), head=(0.35 - 0.3 * look, -0.9 * look)))
    tk = S['tanks'][3]
    hp = world_of(d.hands[1], (0.15, -0.2, 0.2))
    tk.location = (lerp(hp[0], A(-3.85, 7.3, 0.55)[0], put), lerp(hp[1], A(-3.85, 7.3, 0.55)[1], put), lerp(hp[2] + 0.3, A(0, 0, 0.55)[2], put))
    tk.rotation_euler = (0.12, 0.0, 1.2)
    for i, o in enumerate(S['rings'][:2]):
        u = max(0.0, lt - 0.5 - 0.25 * i)
        if u > 0:
            o.location = A(-3.85, 7.3, 0.14)
            o.scale = (0.3 + 1.5 * u, 0.3 + 1.5 * u, 1)
    drips(S, A(-1.6, 5.2, 4.4), t, 5, 1.6, 4.0, 0.9)
    dim = 1 - 0.8 * sm((k - 0.55) / 0.45)
    dlamp(S, d, 3500 * dim, False)
    lampat(S, 0, A(-1.2, 4.0, 3.0), 2200 * dim + 150, 'FFE8C8')
    lampat(S, 1, A(0, 14, 5), 900, '7FB8D0')
    shoot(S, A(lerp(1.6, -0.6, k), lerp(1.2, 3.4, k), lerp(2.3, 1.3, k)), A(-3.1, 6.8, 1.2), 28, fill=1.3 * dim + 0.3)


def rook_vigil(S, k, t, lt):
    A = passage(S, 0.12)
    tank_row(S, A, 4)
    rk = S['rook']
    rp = (-1.9, 6.6, 0.0)
    walk_in = sm(lt / 0.45)
    rk.place(A(rp[0] + 1.6 * (1 - walk_in), rp[1] - 1.4 * (1 - walk_in), 0.0), look_yaw(rp, (-4.2, 7.0)) * lerp(1.0, 0.6, sm(k)))
    S['hat_off'] = sm((lt - 0.35) / 0.5)
    rk.apply(blend(walk(t, 1.3) if walk_in < 1 else P('stand', head=(0.2, 0.0)), to_chest(), (lt - 0.35) / 0.5))
    S['rface'] = 'sad'
    obj, m = S['torch'][0]                                              # one small light left burning by the tanks
    obj.location = A(-3.2, 6.0, 0.25)
    obj.rotation_euler = (0, 0, 0)
    fl = 0.75 + 0.25 * math.sin(t * 11) * math.sin(t * 3.3)
    paint(m, 'FFD8A0', 12 * fl)
    lampat(S, 0, A(-3.1, 5.6, 1.0), 700 * fl, 'FFC890')
    lampat(S, 1, A(0, 14, 5), 900, '7FB8D0')
    lampat(S, 2, A(-0.5, 3.5, 3.6), 500, 'FFE0C0')
    drips(S, A(-2.6, 5.0, 4.6), t, 5, 1.4, 4.2, 0.9)
    for i, o in enumerate(S['rings'][:3]):
        u = (lt * 0.8 + i / 3) % 1
        o.location = A(-2.6 + 1.4 * math.cos(i * 2.4), 5.0 + 0.7 * math.sin(i * 2.4), 0.14)
        o.scale = (0.2 + 0.9 * u, 0.2 + 0.9 * u, 1)
    shoot(S, A(lerp(0.9, -1.9, k), lerp(0.6, 2.2, k), lerp(1.3, 2.3, k)), A(-2.4, 6.5, lerp(1.9, 2.3, k)), 34, fill=1.0, fcol='FFE0C0')


# ---------------------------------------------------------------- sedated, masked, carried
def lie_pat(S, A, t, shut=1.0):
    p = S['pat']
    pp = lp(0.0, 1.5, 0.28)
    p.place(A(pp[0], pp[1], pp[2]), 0.0, -PI / 2 + TH)
    p.apply(P('stand', aL=(0.1, 0.2, 0.15), aR=(0.1, 0.2, 0.15), head=(0.0, 0.0)))
    p.face = 'shut' if shut > 0.5 else 'tired'
    bl = S['ledge']['blanket']
    bl.location = lp(0.0, 2.9, 0.06)
    bl.rotation_euler = (TH, 0, 0)
    return p


def sleep(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.3, turn=0.0)
    p = lie_pat(S, A, t, sm((lt - 0.7) / 0.2))
    d = S['divers'][1]
    dp = lp(1.6, 3.0)
    d.place(A(*dp), look_yaw(dp, (0.0, 3.4)))
    d.apply(dict(KNEE, aR=(1.25, 0.25, 0.5 + 0.1 * math.sin(lt * 5)), aL=(0.9, 0.0, 0.8), head=(0.4, 0.0)))
    dlamp(S, d, 0, False)
    co = S['team'][12]
    cp = lp(-1.7, 3.3)
    co.place(A(*cp), look_yaw(cp, (0.0, 3.4)))
    co.apply(dict(KNEE, aR=(1.1, 0.2, 0.7), head=(0.4, 0.0)))
    co.face = 'calm'
    lampat(S, 0, A(1.0, -1.0, 3.4), 900, 'E8F6FF')
    lampat(S, 1, A(-3, 1, 3.0), 300, 'FFC890')
    hd = world_of(p.head)
    shoot(S, A(lerp(3.3, 2.7, k), lerp(-2.0, -1.4, k), lerp(2.6, 2.9, k)), (hd[0] + lerp(0.5, 0.3, k), hd[1] - 0.7, hd[2] + 0.3), 27, fill=1.2)


def mask_on(S, k, t, lt):
    A = chamber(S)
    p = lie_pat(S, A, t, 1.0)
    hd = world_of(p.head)
    dn = sm(lt / 0.75)
    mk = S['mask']
    off = lerp(1.1, 0.31, dn)
    c, s = math.cos(TH), math.sin(TH)
    mk.location = (hd[0], hd[1] + off * s * 0.0 - 0.0, hd[2] + off)
    mk.location = (hd[0], hd[1] - off * s, hd[2] + off * c)
    mk.rotation_euler = (-PI / 2 + TH, 0, 0)
    for i, sgn in enumerate((-1, 1)):
        h = S['hands'][i]
        h.place((mk.location[0] + sgn * 0.62, mk.location[1], mk.location[2] + 0.12), (0.0, sgn * 0.9, -sgn * PI / 2))
        h.grip(0.55)
    lampat(S, 0, (hd[0] + 0.8, hd[1] - 1.6, hd[2] + 2.2), 420, 'E8F6FF')
    shoot(S, (hd[0] + lerp(0.9, 0.6, k), hd[1] - lerp(2.4, 2.0, k), hd[2] + lerp(2.4, 2.1, k)), (hd[0], hd[1] - 0.15, hd[2] + 0.1), 40, fill=1.5)


def carry_in(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.2, skip=(12,))
    dn = sm((lt - 0.35) / 0.75)
    d = S['divers'][0]
    dp = (-0.6, -2.4 - 0.9 * dn)
    d.place(A(dp[0], dp[1], -1.5 - 0.9 * dn), look_yaw(dp, (-0.6, -9)) + 0.5)
    d.apply(P('stand', aL=(1.1, 0.35, 0.6), aR=(1.1, 0.35, 0.6), head=(0.35, 0.0)))
    dlamp(S, d, 4500, True)
    p = S['pat']
    p.place(A(dp[0] + 1.75, dp[1] + 0.25, 0.12 - 0.75 * dn + 0.03 * math.sin(t * 4)), -PI / 2 + 0.5, PI / 2)
    p.apply(limp_pose())
    p.face = 'shut'
    wear_mask(S, p)
    for i, o in enumerate(S['rings'][:2]):
        u = (lt * 0.8 + 0.5 * i) % 1
        o.location = A(dp[0] + 0.5, dp[1], 0.03)
        o.scale = (0.8 + 1.8 * u, 0.8 + 1.8 * u, 1)
    co = S['team'][12]
    cp = lp(-2.6, 1.2)
    co.place(A(*cp), look_yaw(cp, dp))
    co.apply(P('stand', aL=(0.6, 0.0, 1.6, 1.0), aR=(0.6, 0.0, 1.6, 1.0), head=(0.3, 0.0)))
    co.face = 'sad'
    rk = S['rook']
    rp = lp(2.6, 1.15)
    rk.place(A(*rp), look_yaw(rp, dp))
    rk.apply(P('think', head=(0.3, 0.1), lean=0.12))
    S['rface'] = 'sad'
    rope(S, 0, A(1.6, 0.9, 0.35), A(1.0, -9.0, -0.6))
    lampat(S, 0, A(1.5, -0.5, 3.0), 800, 'E8F6FF')
    lampat(S, 1, A(4.6, -0.6, 3.4), 300, 'FFC890')
    shoot(S, A(lerp(-3.4, -2.9, k), lerp(-5.9, -5.4, k), lerp(1.7, 1.4, k)), A(0.7, -1.4, 0.9), 27, fill=1.2)


def carried(S, A, y, t, x=None, z=None, lead=0.0, dz=-0.62):
    """A diver swimming along the line with the sleeping boy held under his chest. Returns the diver."""
    p0 = line_pt(S, y)
    x = p0[0] + 0.5 if x is None else x
    z = p0[2] + 1.1 if z is None else z
    d = S['divers'][0]
    d.place(A(x, y, z + 0.06 * math.sin(t * 3)), PI, PI / 2)
    d.apply(swim_pose(t, 1.1, True))
    p = S['pat']
    p.place(A(x + 0.05, y - 0.55 + lead, z + dz + 0.06 * math.sin(t * 3)), PI, PI / 2)
    p.apply(limp_pose())
    p.face = 'shut'
    wear_mask(S, p)
    return d


def carry_dark(S, k, t, lt):
    A = sump(S)
    y = lerp(2.0, 6.5, k)
    d = carried(S, A, y, t, x=-0.7, z=0.2)
    dlamp(S, d, 5200, True)
    bubbles(S, world_of(d.head, (0, 0.2, 0.3)), t, 5)
    bubbles(S, world_of(S['pat'].head, (0, 0.2, 0.3)), t + 0.4, 4, 5, 1.0)
    for i, o in enumerate(S['foam'][9:]):
        o.location = A(-2 + 4 * rn(i, 93), y + 1 + 2.2 * i, -1.5 + 3 * rn(i, 94))
        o.scale = (0.1, 0.1, 0.1)
    lampat(S, 0, A(1.0, y + 2.6, 0.6), 420, 'DFF6F0')
    shoot(S, A(lerp(1.15, 1.0, k), y + lerp(4.6, 4.0, k), lerp(-0.9, -0.6, k)), A(-0.6, y + 1.2, -0.1), 18, roll=0.05 * math.sin(t * 1.6), fill=1.3, fcol='BFE8D8')


def squeeze(S, k, t, lt):
    A = sump(S)
    y = lerp(15.6, 18.3, sm(k))
    d = carried(S, A, y, t, x=0.0, z=0.45, lead=-0.6 - 1.4 * sm(k), dz=-0.3)
    dlamp(S, d, 2600, False)
    bubbles(S, world_of(S['pat'].head, (0, 0.2, 0.3)), t, 5, 0, 1.0)
    lampat(S, 0, A(0.9, 23.2, 0.9), 360, 'DFF6F0')
    lampat(S, 1, A(0.0, 17.0, 1.4), 900, 'E8F6FF')
    shoot(S, A(lerp(0.5, 0.25, k), lerp(25.2, 24.3, k), lerp(0.25, 0.1, k)), A(0.0, 20.0, -0.1), 26, roll=0.04 * math.sin(t * 1.7), fill=1.2, fcol='BFE8D8')


# ---------------------------------------------------------------- out
def stretcher_out(S, k, t, lt):
    A = rescue_dusk(S)
    y = lerp(12.5, 7.0, k)
    st = S['stretcher']
    bob = 0.05 * math.sin(t * 9)
    st.location = A(-0.4, y, mz(y) + 1.35 + bob)
    st.rotation_euler = (0, 0, 0.06)
    for i, (rr, dy) in enumerate(zip(S['res'], (-2.25, 2.25))):
        rr.place(A(-0.4 + 0.14 * dy, y + dy, mz(y + dy)), 0.06)
        rr.apply(dict(walk(t + 0.5 * i, 1.8), aL=(0.2 if i == 0 else -0.2, 0.12, 0.5), aR=(0.2 if i == 0 else -0.2, 0.12, 0.5), head=(0.05, 0.0)))
        rr.face = 'warm'
    rk = S['rook']
    fl = math.sin(lt * 20)
    rp = (1.4, y - 1.2, 0.9 + 0.3 * math.sin(lt * 5))
    rk.place(A(*rp), 0.3, 0.2)
    rk.apply(P('stand', aL=(0.2, 1.35 + 0.5 * fl, 0.25), aR=(0.2, 1.35 + 0.5 * fl, 0.25), lL=(0.5, 0.9), lR=(0.3, 0.8), head=(-0.1, 0.5)))
    S['rface'] = 'warm'
    pulse = 1 + 0.03 * math.sin(t * 30)
    S['mouth']['pump'].scale = (pulse, pulse, pulse)
    lampat(S, 0, A(-1.0, y - 6.0, 3.4), 1500, 'FFC890')
    shoot(S, A(lerp(2.6, 2.2, k), y - lerp(9.6, 8.8, k), lerp(1.5, 1.8, k)), A(-0.8, y - 0.5, 2.2), 24, fill=1.2, fcol='FFE8D0')


def pump_fail(S, k, t, lt):
    A = rescue_dusk(S)
    M = S['mouth']
    run = 1 - sm((lt - 0.7) / 0.25)
    M['pump'].location = (PUMP[0] + 0.05 * run * math.sin(t * 47), PUMP[1] + 0.04 * run * math.sin(t * 53), 0.03 * run * abs(math.sin(t * 41)))
    M['pump'].rotation_euler = (0, 0.02 * run * math.sin(t * 39), 0)
    for i in range(5):                                                # exhaust puffs, then nothing
        u = (t * 1.4 + i / 5) % 1
        o = S['foam'][i]
        o.location = A(PUMP[0] - 0.55 + 0.3 * u, PUMP[1], 2.0 + 1.6 * u) if run > 0.15 else AWAY
        o.scale = (0.3 + 0.6 * u,) * 3
    rk = S['rook']
    rp = (PUMP[0] - 2.3, PUMP[1] + 0.5, 0.0)
    rk.place(A(*rp), look_yaw(rp, (PUMP[0] - 0.4, PUMP[1] - 3.0)))
    j = sm((lt - 0.85) / 0.25)
    rk.apply(blend(P('cross', head=(0.1, 0.5)), P('point', aL=(1.1, 0.5, 0.25), aR=(0.1, 0.2, 0.2), head=(0.2, 0.6), lean=0.1), j))
    S['rface'] = 'calm' if j < 0.5 else 'shocked'
    lampat(S, 0, A(PUMP[0] - 1.0, PUMP[1] - 4.5, 2.8), 1200, 'FFC890')
    lampat(S, 1, A(PUMP[0] - 1.9, PUMP[1] - 2.2, 1.9), 420, 'FFD8B0')
    shoot(S, A(PUMP[0] + lerp(0.2, 0.6, k), PUMP[1] - lerp(7.0, 6.4, k), lerp(1.6, 1.8, k)), A(PUMP[0] - 1.2, PUMP[1] - 0.3, 1.6), 27, fill=1.2, fcol='FFE8D0')


def reflood(S, k, t, lt):
    wl = lerp(0.3, 3.4, sm(k))
    A = passage(S, wl)
    tank_row(S, A, 4)
    fp = S['flood_prop']
    tip = sm((k - 0.45) / 0.3)
    fp.location = A(1.2, 4.5, 0.0)
    fp.rotation_euler = (0, 1.35 * tip, 0.4)
    on = 1.0 if k < 0.62 else (0.5 + 0.5 * math.sin(t * 60)) * max(0.0, 1 - (k - 0.62) / 0.15)
    paint(S['fpm'], 'FFF2D0', 12 * on)
    lampat(S, 0, A(0.6, 3.2, 2.8), 1500 * on + 60, 'FFE8C0')
    lampat(S, 1, A(0, 12, 5.5), 2000, 'A8D8E8')
    foam(S, [A(-4.5 + 9 * rn(i, 95), 17 - 18 * sm(k) * rn(i, 96) - 2 * rn(i, 97), wl + 0.15 + 0.4 * abs(math.sin(t * 8 + i))) for i in range(14)], 1.8)
    rk = S['rook']
    fl = math.sin(lt * 22)
    rp = (lerp(1.8, 0.6, k), lerp(3.0, -1.5, k), lerp(1.2, 4.2, sm(k)))
    rk.place(A(*rp), 0.3, 0.3)
    rk.apply(P('stand', aL=(0.2, 1.35 + 0.5 * fl, 0.25), aR=(0.2, 1.35 + 0.5 * fl, 0.25), lL=(0.6, 1.0), lR=(0.4, 0.9), head=(0.3, 0.0)))
    S['rface'] = 'shocked'
    lampat(S, 2, A(rp[0] - 0.5, rp[1] - 2.5, rp[2] + 2.5), 700, 'FFC890')
    shoot(S, A(lerp(-2.0, -1.6, k), lerp(-6.0, -8.5, k), lerp(4.6, 5.4, k)), A(0.0, 6.0, lerp(1.0, 2.6, k)), 22, roll=0.04 * math.sin(t * 3), fill=1.3)


# ---------------------------------------------------------------- afterwards
def rook_wrong(S, k, t, lt):
    A = morning(S)
    rk = S['rook']
    rp = (-0.6, 2.0, 0.0)
    cam = (lerp(-3.4, -2.8, k), lerp(-4.6, -3.9, k), 2.3)
    turn = sm((lt - 0.1) / 0.3)
    rk.place(A(*rp), lerp(PI, look_yaw(rp, cam), turn))
    rk.apply(blend(P('hips', head=(-0.2, 0.0)), P('shrug', head=(0.05, 0.0)), turn))
    S['rface'] = 'warm' if turn > 0.5 else 'calm'
    shoot(S, A(*cam), A(-0.4, 2.4, 2.3), 38, fill=1.0, fcol='FFE8D0')


def signoff(S, k, t, lt):
    A = morning(S)
    rk = S['rook']
    rp = (-2.6, -8.6, 0.0)
    rk.place(A(*rp), 0.45)
    grab = sm((lt - 0.05) / 0.25)
    up = sm((lt - 0.35) / 0.25)
    away = sm((lt - 0.95) / 0.3)
    low = P('stand', aR=(0.9, 0.2, 0.2), head=(0.55, 0.3), lean=0.75, lL=(0.5, 0.9), lR=(0.5, 0.9), lift=-0.35)
    hold = P('stand', aR=(1.15, 0.25, 1.3, 0.3), head=(0.25, 0.35))
    rk.apply(blend(blend(blend(P('stand'), low, grab), hold, up), P('hat'), away))
    S['hat_tip'] = away
    S['rface'] = 'warm' if away < 0.5 else 'deadpan'
    obj, m = S['torch'][0]                                              # the shiny thing: a small brass torch left in the mud
    ground = A(rp[0] + 0.75, rp[1] - 1.0, 0.12)
    hand = world_of(rk.hands[1], (0, -0.12, -0.08))
    u = sm((lt - 0.25) / 0.12)
    obj.location = tuple(ground[i] + (hand[i] - ground[i]) * u for i in range(3))
    obj.rotation_euler = (lerp(PI / 2, -0.4, up), 0.3, 0.6)
    obj.scale = (1.5, 1.5, 1.5)
    lit = 1.0 if 0.62 < lt < 0.95 else 0.0
    paint(m, 'FFF2C0', 16 * lit)
    lampat(S, 0, world_of(rk.head, (0.4, -1.2, 0.2)), 160 * lit)
    if lt > 1.05:
        obj.location = AWAY
    shoot(S, A(lerp(-0.6, -1.0, k), lerp(-14.2, -13.2, k), lerp(1.9, 2.3, k)), A(rp[0] + 0.2, rp[1], 2.3), 30, fill=1.0, fcol='FFE8D0')


# ---------------------------------------------------------------- a photograph for the case board
def photo_ledge(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='warm', nod=0.05)
    lampat(S, 0, A(0.5, -3.0, 2.2), 2600, 'E8F6FF')
    shoot(S, A(0.6, -4.2, 2.0), A(0.0, 4.2, 2.6), 26, fill=1.4)


SHOTS3D = {f.__name__: f for f in (
    mouth_wide, walk_in, bikes, rain_gush, fill, rook_rock, rook_drip, chase, scramble, ledge_wide, huddle, torch_dies, divers_fight, glow, surface,
    faces_lit, rook_count, way_out, sump_long, toe_dip, rook_sound, tank_carry, tanks, rook_vigil, sleep, mask_on, carry_in, carry_dark, squeeze, stretcher_out,
    pump_fail, reflood, rook_wrong, signoff)}
STILLS = dict(ledge=photo_ledge)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same cave, more of it. New in the Short's sets: the moment the diver takes the sleeping boy under
# (the cold open), the team arriving, the locked bicycles found in the dark, the navy divers and the doctor who
# stayed, the letters, the coach's note, the case of medicines, the wait on the mud, the relay in the flooded
# tunnel, the still water after the rescuer's death, the workers getting out. New sets, each at its own origin:
# a rescue camp of canopies, pumps and lamps; rice fields under a ridge with a pipe pouring onto them; a hospital
# ward; a temple hall with candles. Still generic: no name, flag, emblem, sign, logo or lettering anywhere, no
# medical or religious symbol; none of the sets is a model of a real place and the extra people (rescue workers,
# navy divers, a doctor, a farmer, boys in hospital gowns, novices) are plain stand-ins: nobody's likeness is attempted.
SETS.update(camp=(16000, 0, 0), fields=(20000, 0, 0), ward=(24000, 0, 0), temple=(28000, 0, 0))
CAMFILL.update(take_under=200, rook_edge=220, arrive=90, locked_bikes=160, camp_wide=120, pumps_row=200, pipe_out=60, fields_flood=0, farmer=110,
               doctor_stay=240, letters=160, letter_out=220, coach_sorry=260, search_map=220, still_water=120, doc_kit=240, vials=160, team_watch=300, relay=260,
               cheer=220, get_out=420, out_mouth=160, ward=120, walk_home=120, novices=160, candles=200)
CREWC = (('C86A22', 'E8E4D8'), ('2E6A4A', 'E0B030'), ('C86A22', 'E0B030'), ('3A5A8A', 'E8E4D8'), ('8A7A4A', 'D8822A'))
PUMPS = [(10.0 + 2.4 * j, -2.0) for j in range(4)]
BEDS = (-7.5, -2.5, 2.5, 7.5)
KNEEL = dict(lL=(0.3, 1.7), lR=(0.3, 1.7), lift=-0.78, lean=0.1)


import bmesh

_add_ops, _empty_ops = add, empty
_LAST = [None]


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """The kit's add(), without the operator: the same primitive, material and bevel, built straight into a mesh.
    Operators slow down with every object already in the scene, and this film has several thousand."""
    if kind == 'torus':
        return _add_ops(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'cylinder':
        r_ = kw.get('radius', 1.0)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=r_, radius2=r_, depth=kw.get('depth', 2.0))
    elif kind == 'cone':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius1', 1.0), radius2=kw.get('radius2', 0.0),
                              depth=kw.get('depth', 2.0))
    elif kind == 'ico_sphere':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('subdivisions', 2), radius=kw.get('radius', 1.0))
    else:
        bm.free()
        return _add_ops(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
    me = bpy.data.meshes.new(kind)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(kind, me)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    vl = bpy.context.view_layer                                       # leave it selected and active, as the operator would
    for x in (_LAST[0], vl.objects.active):
        if x is not None:
            try:
                x.select_set(False)
            except (ReferenceError, RuntimeError):
                pass
    o.select_set(True)
    vl.objects.active = o
    _LAST[0] = o
    me.materials.append(K.mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    if parent:
        o.parent = parent
    return o


def empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new('e', None)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    return o


def box(col, lc, scale, parent, rot=(0, 0, 0), **kw):
    return add('cube', col, lc, rot=rot, scale=scale, size=1, parent=parent, **kw)


def hood_head(skin, hood):
    def fn(head):
        d = K.human_head(skin, hood)(head)
        add('ico_sphere', hood, (0, 0.04, 0.04), scale=(1.02, 1.0, 1.12), radius=0.31, subdivisions=1, parent=head)
        return d
    return fn


def straw_head(skin):
    def fn(head):
        d = K.human_head(skin, '2A2428')(head)
        add('cone', 'D8C080', (0, 0.0, 0.36), radius1=0.7, radius2=0.06, depth=0.34, vertices=10, parent=head, rough=1.0)
        return d
    return fn


def figure(r, x, y, col, hat, s=1.0, yaw=0.0):
    """A far-off standing person for the crowd: a body, a head and a helmet. Not a rig; it does not move."""
    e = empty((x, y, 0), r, (0, 0, yaw))
    add('cone', col, (0, 0, 1.35 * s), radius1=0.34 * s, radius2=0.4 * s, depth=1.3 * s, vertices=6, parent=e)
    add('cylinder', '2A3040', (0, 0, 0.36 * s), radius=0.3 * s, depth=0.72 * s, vertices=6, parent=e)
    add('ico_sphere', 'C8946A', (0, 0, 2.3 * s), radius=0.28 * s, subdivisions=1, parent=e)
    add('ico_sphere', hat, (0, 0.02, 2.42 * s), scale=(1, 1.05, 0.6), radius=0.33 * s, subdivisions=1, parent=e, rough=0.4)
    return e


def tree(r, x, y, hgt, j):
    add('cylinder', '3E3226', (x, y, hgt / 2), radius=0.3, depth=hgt, vertices=6, parent=r)
    for q in range(3):
        add('ico_sphere', (LEAF, LEAFL, '1F4428')[(j + q) % 3], (x + 1.4 * (rn(j, 216 + q) - 0.5), y + 1.4 * (rn(j, 219 + q) - 0.5), hgt + 0.8 * q),
            scale=(2.7 - 0.5 * q, 2.7 - 0.5 * q, 1.5), radius=1, subdivisions=1, parent=r)


def set_camp(r):
    """The rescue camp below the cave: canopies, a map table, air tanks, pumps, lamps on poles, people everywhere."""
    out = {}
    box('5A4E3C', (0, 10, -0.5), (300, 200, 1), r)
    lumps(r, 40, 200, lambda j: (-70 + 140 * rn(j, 201), 36 + 12 * rn(j, 202), 18 * rn(j, 203)), cols=(LEAF, LEAFL, '1F4428'), s0=4.0, s1=5.0, flat=0.9)
    box(LIMED, (0, 56, 16), (220, 10, 44), r)
    lumps(r, 24, 204, lambda j: (-80 + 160 * rn(j, 205), 50, 10 + 26 * rn(j, 206)), cols=(LIME, LIMED, LEAF), s0=3.0, s1=4.0)
    for j in range(18):
        sd = -1 if j % 2 else 1
        tree(r, sd * (24 + 22 * rn(j, 207)), -14 + 44 * rn(j, 208), 6 + 6 * rn(j, 209), j)
    for j, (x, y, col) in enumerate(((-7, 6, '2F6FB0'), (7, 9, 'E4DFD0'), (-1, 18, '2E8A5A'), (18, 15, '2F6FB0'), (-19, 14, 'E4DFD0'))):
        for sx in (-1, 1):
            for sy in (-1, 1):
                add('cylinder', 'B8BCC8', (x + sx * 3.6, y + sy * 2.6, 1.8), radius=0.07, depth=3.6, vertices=5, parent=r, rough=0.4)
        box(col, (x, y, 3.7), (8.0, 6.0, 0.14), r, rot=(0.06, 0.03 * (j - 2), 0))
        box(col, (x, y + 2.9, 3.2), (8.0, 0.1, 1.0), r)
    box('7A6044', (-7, 6, 1.25), (3.8, 2.0, 0.12), r)                                                  # the map table
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', '5A4630', (-7 + sx * 1.7, 6 + sy * 0.8, 0.6), radius=0.07, depth=1.2, vertices=5, parent=r)
    box('E8E0C8', (-7, 6, 1.33), (2.9, 1.5, 0.03), r)
    cave = [(-8.2, 5.7), (-7.7, 6.2), (-7.2, 5.9), (-6.7, 6.35), (-6.2, 6.0), (-5.8, 6.3)]                 # a line drawn on the paper: no lettering
    for a, b in zip(cave, cave[1:]):
        tube(r, '2A2E38', (a[0], a[1], 1.36), (b[0], b[1], 1.36), 0.03)
    for a, b in zip(cave[2:5], cave[3:6]):
        tube(r, '2F8FB8', (a[0], a[1], 1.37), (b[0], b[1], 1.37), 0.045)
    add('cylinder', 'D8362A', (-5.8, 6.3, 1.37), radius=0.09, depth=0.03, vertices=8, parent=r)
    box('7A6044', (7, 9.4, 1.2), (5.0, 1.6, 0.12), r)
    for j in range(5):
        box(('3A3F4C', '5A6A50', '22262E')[j % 3], (5.2 + 0.9 * j, 9.4, 1.5), (0.7, 0.9, 0.5), r)
    for j in range(8):                                                                                 # air tanks standing in a row
        add('cylinder', 'D8DCE4' if j % 2 else 'E0C020', (3.2 + 0.55 * j, 5.6, 0.6), radius=0.2, depth=1.2, vertices=8, parent=r, rough=0.3)
    for j in range(9):
        box(('5A6A50', '7A6044')[j % 2], (-15 + 1.3 * (j % 4), 0.5 + 1.2 * (j // 4), 0.45 + (0.9 if j == 8 else 0)), (1.1, 0.9, 0.9), r, rot=(0, 0, 0.2 * j))
    box('5A6A50', (-12.0, -4.0, 0.55), (1.6, 1.4, 1.1), r)                                               # Rook's crate
    out['pumps'] = []
    for j, (px, py) in enumerate(PUMPS):
        b = empty((px, py, 0), r)
        box('3A3F4C', (0, 0, 0.25), (1.9, 1.3, 0.3), b)
        box('D8822A', (0, 0, 0.85), (1.5, 1.0, 0.9), b)
        add('cylinder', '8A90A0', (-0.55, 0, 1.55), radius=0.12, depth=0.7, vertices=6, parent=b, rough=0.4)
        add('cylinder', '8A90A0', (0.6, -0.62, 0.8), rot=(PI / 2, 0, 0), radius=0.3, depth=0.3, vertices=8, parent=b, rough=0.4)
        out['pumps'].append(b)
        hs = [(px, py + 0.7, 0.3), (px - 0.6, py + 6, 0.2), (px - 2.0 - j, 22, 0.2), (px - 4.0, 34, 0.2)]
        for a, c in zip(hs, hs[1:]):
            tube(r, '2C4E8A', a, c, 0.2)
        hs = [(px, py - 0.7, 0.3), (px + 1.0, py - 7, 0.2), (px + 6.0, -30, 0.2)]
        for a, c in zip(hs, hs[1:]):
            tube(r, '2C4E8A', a, c, 0.2)
    out['lampm'] = newmat('camplamp', 'FFF2D0', 0.4, 0.0)
    out['poles'] = [(-12.5, 2.5), (1.5, 3.0), (13.5, 3.5), (4.0, 21.0), (-14, 20)]
    for x, y in out['poles']:
        add('cylinder', '3A3F4C', (x, y, 2.6), radius=0.07, depth=5.2, vertices=5, parent=r)
        wear(box('FFF2D0', (x, y - 0.1, 5.3), (1.1, 0.25, 0.7), r, rot=(-0.5, 0, 0)), out['lampm'])
    cols = ('C86A22', '2E6A4A', '3A5A8A', '8A7A4A', 'B8322E', '4A5A6A')
    hats = ('E8E4D8', 'E0B030', 'D8822A', '2E6A4A')
    for j in range(34):                                                                                # the crowd
        x, y = -22 + 46 * rn(j, 210), 11 + 20 * rn(j, 211)
        figure(r, x, y, cols[j % 6], hats[j % 4], 0.92 + 0.16 * rn(j, 212), 6.3 * rn(j, 213))
    for j in range(8):
        add('cylinder', '8FA4B0', (-16 + 34 * rn(j, 214), -8 + 12 * rn(j, 215), 0.04 + 0.012 * j), scale=(1.5, 1.0, 1), radius=0.9, depth=0.02, vertices=8,
            parent=r, rough=0.42)
    return out


def set_fields(r):
    """Rice fields under a wooded ridge, with a pipe pouring onto them. An invented valley, not the real one."""
    out = {}
    box('4A4030', (0, 20, -0.9), (400, 300, 1), r)
    greens = ('5E8A3A', '6E9A44', '4E7A34', '7EA84C')
    for i in range(8):
        for j in range(6):
            box(greens[(i * 3 + j) % 4], (-35 + 10 * i, -12 + 10 * j, -0.3), (9.3, 9.3, 0.6), r)
    for i in range(9):
        box('6A5238', (-40 + 10 * i, 13, -0.2), (0.7, 60, 1.1), r)
    for j in range(7):
        box('6A5238', (0, -17 + 10 * j, -0.2), (80, 0.7, 1.1), r)
    for j in range(150):                                                                               # young rice in the near plots
        x, y = -14 + 28 * rn(j, 230), -11 + 16 * rn(j, 231)
        if abs((x + 40) % 10) < 0.8 or abs((y + 17) % 10) < 0.8:
            continue
        add('cone', 'A8D060' if j % 2 else '8EC050', (x, y, 0.28), radius1=0.09, radius2=0, depth=0.6, vertices=4, parent=r)
    lumps(r, 46, 232, lambda j: (-110 + 220 * rn(j, 233), 62 + 26 * rn(j, 234), 30 * rn(j, 235) * (1 - 0.6 * abs(-1 + 2 * rn(j, 233)))),
          cols=(LEAF, '1F4428', LEAFL, '2A4A3A'), s0=7.0, s1=8.0, flat=0.9)
    box('2A4A3A', (0, 96, 12), (300, 20, 40), r)
    pipe = [(1.5, 62, 6.0), (1.0, 40, 1.4), (0.4, 16, 1.2), (0.0, 9.0, 1.1)]
    for a, b in zip(pipe, pipe[1:]):
        tube(r, '2C4E8A', a, b, 0.42)
    add('torus', '22262E', (0, 9.0, 1.1), rot=(PI / 2, 0, 0), major_radius=0.46, minor_radius=0.08, major_segments=10, minor_segments=4, parent=r)
    for y in (12, 22, 32):
        box('3A3F4C', (0.5, y, 0.5), (1.2, 0.3, 1.0), r)
    out['water'] = keep(box('8A7450', (0, 13, -0.75), (82, 62, 0.5), r, rough=0.07))
    h_ = empty((-21, 24, 0), r)                                                                        # a farmhouse on stilts
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', '5A4630', (sx * 2.2, sy * 1.6, 0.9), radius=0.14, depth=1.8, vertices=5, parent=h_)
    box('8A6A48', (0, 0, 2.9), (5.2, 4.0, 2.4), h_)
    add('cone', '4A3A2C', (0, 0, 5.0), rot=(0, 0, PI / 4), scale=(1.25, 1.0, 1), radius1=3.6, radius2=0.2, depth=2.0, vertices=4, parent=h_)
    for j in range(12):
        sd = -1 if j % 2 else 1
        tree(r, sd * (30 + 18 * rn(j, 236)), 2 + 44 * rn(j, 237), 6 + 5 * rn(j, 238), j)
    for j in range(5):
        tree(r, -16 + 9 * j + 3 * rn(j, 239), 50, 7 + 3 * rn(j, 240), j + 3)
    return out


def set_ward(r):
    """A plain hospital ward: four beds under three bright windows, a doorway full of daylight."""
    out = {}
    box('8E9C98', (0, -2, -0.1), (26, 22, 0.2), r)
    box('B4CCC6', (0, 7.2, 6), (26, 0.3, 12), r)
    box('9AB8B0', (0, 7.0, 0.7), (26, 0.1, 1.4), r)
    box('DCE4E0', (-13, -2, 6), (0.3, 22, 12), r)
    for y, d in ((3.4, 7.6), (-9.6, 6.8)):                                                             # the right wall, with a doorway in it
        box('DCE4E0', (13, y, 6), (0.3, d, 12), r)
    box('DCE4E0', (13, -3.3, 8.6), (0.3, 5.8, 6.8), r)
    out['doorm'] = newmat('daylight', 'FFF4E0', 0.4, 2.2)
    wear(box('FFF4E0', (13.6, -3.3, 2.6), (0.1, 5.8, 5.2), r), out['doorm'])
    for x in (-8.5, 0, 8.5):
        wear(box('EAF4FF', (x, 7.02, 3.9), (3.6, 0.06, 3.0), r), out['doorm'])
        box('F4F4F0', (x, 6.96, 3.9), (0.12, 0.08, 3.0), r)
        box('F4F4F0', (x, 6.96, 3.9), (3.6, 0.08, 0.12), r)
        for sx in (-1, 1):
            box('9AB8B0', (x + sx * 2.3, 6.9, 3.9), (0.9, 0.1, 3.5), r)
    for j, x in enumerate(BEDS):
        box('B8BCC8', (x, 4.3, 0.55), (2.3, 4.6, 0.5), r, rough=0.4)
        box('F4F4F0', (x, 4.3, 0.95), (2.1, 4.4, 0.3), r)
        box('FFFFFF', (x, 6.0, 1.22), (1.5, 0.9, 0.26), r)
        box('BFD8D0', (x, 3.2, 1.0), (2.16, 2.4, 0.36), r)
        box('B8BCC8', (x, 6.6, 1.4), (2.3, 0.1, 1.6), r, rough=0.4)
        box('E8E4D8', (x + 1.9, 6.3, 0.6), (0.9, 0.9, 1.2), r)
        add('cylinder', ('E0B030', '2F6FB0', 'C8372D', '2E8A5A')[j], (x + 1.9, 6.3, 1.36), radius=0.14, depth=0.3, vertices=7, parent=r)
    out['boys'] = []
    for j, x in enumerate(BEDS):                                                                      # a boy sitting up in each bed, in a pale gown
        e = empty((x, 5.0, 1.1), r, (0, 0, 0.2 * math.sin(j * 2.3)))
        sk = SKINS[j % 3]
        add('cone', 'BFD8D0', (0, 0, 0.5), radius1=0.34, radius2=0.4, depth=1.0, vertices=8, parent=e)
        box('BFD8D0', (0, 0, 1.03), (0.8, 0.36, 0.14), e)
        hd = empty((0, 0, 1.36), e)
        add('ico_sphere', sk, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=hd)
        add('ico_sphere', '17131A', (0, 0.05, 0.1), radius=0.3, subdivisions=1, parent=hd)
        for sx in (-1, 1):
            box('FFFFFF', (sx * 0.105, -0.262, 0.04), (0.1, 0.03, 0.075), hd, emit=0.6)
            box('0E0D14', (sx * 0.105, -0.28, 0.035), (0.04, 0.02, 0.045), hd)
        box('2A1218', (0, -0.27, -0.12), (0.17, 0.03, 0.05), hd)
        add('cylinder', 'BFD8D0', (-0.5, -0.1, 0.72), rot=(0.4, 0, 0), radius=0.085, depth=0.6, vertices=6, parent=e)
        arm = empty((0.5, 0, 1.0), e)
        add('cylinder', 'BFD8D0', (0, 0, -0.25), radius=0.085, depth=0.5, vertices=6, parent=arm)
        add('cylinder', sk, (0, 0, -0.68), radius=0.075, depth=0.4, vertices=6, parent=arm)
        box(sk, (0, 0, -0.95), (0.15, 0.09, 0.2), arm)
        e.scale = (0.78 + 0.05 * j,) * 3
        out['boys'].append((e, hd, arm))
    box('B8BCC8', (-11.4, -4.0, 0.9), (1.2, 2.2, 0.1), r, rough=0.4)                                     # a trolley
    for sx in (-1, 1):
        add('cylinder', 'B8BCC8', (-11.4 + sx * 0.5, -4.0, 0.45), radius=0.04, depth=0.9, vertices=5, parent=r, rough=0.4)
    box('6E7E88', (0, -2.6, 0.011), (26, 2.6, 0.02), r)
    return out


def set_temple(r):
    """A temple hall in the evening: red columns, a long low table of candles and flowers. No image, sign or script."""
    out = {}
    box('8A5A34', (0, 0, -0.15), (40, 26, 0.3), r)
    for j in range(13):
        box('7A4C2A', (-18 + 3 * j, 0, 0.005), (0.06, 26, 0.02), r)
    box('8A2A22', (0, 10.5, 7), (40, 0.4, 14), r)
    box('D8A22A', (0, 10.2, 1.1), (40, 0.1, 0.25), r, rough=0.4)
    box('D8A22A', (0, 10.2, 8.2), (40, 0.1, 0.25), r, rough=0.4)
    for sd in (-1, 1):
        box('6A201A', (sd * 20, 0, 7), (0.4, 26, 14), r)
    for j in range(7):
        x = -15 + 5 * j
        add('cylinder', 'A8322A', (x, 8.2, 5), radius=0.5, depth=10, vertices=10, parent=r)
        for z in (0.5, 8.6):
            add('cylinder', 'D8A22A', (x, 8.2, z), radius=0.62, depth=0.5, vertices=10, parent=r, rough=0.4)
    out['panem'] = newmat('lattice', 'FFC890', 0.5, 2.2)
    for j in range(6):
        x = -12.5 + 5 * j
        wear(box('FFC890', (x, 10.25, 4.6), (2.6, 0.05, 4.4), r), out['panem'])
        for q in range(4):
            box('5A1A14', (x - 0.9 + 0.6 * q, 10.2, 4.6), (0.08, 0.08, 4.4), r)
        for q in range(5):
            box('5A1A14', (x, 10.2, 2.8 + 0.9 * q), (2.6, 0.08, 0.08), r)
    box('D8A22A', (0, 5.6, 0.7), (11, 1.3, 0.16), r, rough=0.4)
    box('8A2A22', (0, 5.6, 0.35), (10.4, 1.0, 0.6), r)
    out['flamem'] = newmat('flame', 'FFD070', 0.4, 14.0)
    out['flames'] = []
    for j in range(13):
        x = -4.8 + 0.8 * j
        hh = 0.5 + 0.25 * rn(j, 250)
        add('cylinder', 'F4EAD0', (x, 5.4, 0.78 + hh / 2), radius=0.07, depth=hh, vertices=6, parent=r)
        out['flames'].append(wear(add('cone', 'FFD070', (x, 5.4, 0.88 + hh), radius1=0.06, radius2=0.0, depth=0.22, vertices=5, parent=r), out['flamem']))
    for j in range(16):
        add('ico_sphere', ('F0B040', 'F4F0E0', 'E87A30')[j % 3], (-5.0 + 0.66 * j, 5.95, 0.92), radius=0.16, subdivisions=1, parent=r)
    for j in range(5):
        box('A8322A', (-4.0 + 2.0 * j, 1.6, 0.03), (1.5, 1.7, 0.06), r)
    out['nov'] = []
    for j in range(5):                                                                                # five novices kneeling, hands together, heads bowed
        sc_ = 0.8 + 0.05 * ((j * 3) % 5)
        e = empty((-4.0 + 2.0 * j, 1.6, 0.06), r, (0, 0, PI + 0.06 * math.sin(j * 2.0)))
        sk = SKINS[j % 3]
        add('cone', 'E08A1E', (0, 0.25, 0.45), radius1=0.72, radius2=0.36, depth=0.9, vertices=8, parent=e, rough=1.0)
        add('cone', 'E08A1E', (0, 0, 1.3), radius1=0.34, radius2=0.4, depth=1.0, vertices=8, parent=e, rough=1.0)
        box('C87414', (0.12, -0.02, 1.4), (0.5, 0.5, 0.9), e, rot=(0, 0.5, 0), rough=1.0)
        for sx in (-1, 1):
            add('cylinder', sk, (sx * 0.24, -0.3, 1.38), rot=(1.0, 0, sx * 0.7), radius=0.07, depth=0.62, vertices=6, parent=e)
        box(sk, (0, -0.5, 1.6), (0.14, 0.1, 0.3), e, rot=(0.3, 0, 0))
        hd = empty((0, -0.06, 2.12), e, (0.34, 0, 0))
        add('ico_sphere', sk, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=hd)
        add('ico_sphere', '7A5A40', (0, 0.04, 0.09), scale=(0.95, 1, 0.95), radius=0.295, subdivisions=1, parent=hd)
        for sx in (-1, 1):
            box('2A1A14', (sx * 0.105, -0.27, 0.03), (0.11, 0.03, 0.025), hd)
        box('5E3822', (0, -0.285, -0.04), (0.05, 0.05, 0.08), hd)
        box('2A1218', (0, -0.265, -0.13), (0.11, 0.03, 0.03), hd)
        e.scale = (sc_,) * 3
        out['nov'].append((e, hd))
    for x in (-8.5, 8.5):
        add('cylinder', 'D8A22A', (x, 5.6, 1.0), radius=0.35, depth=2.0, vertices=8, parent=r, rough=0.4)
        wear(add('ico_sphere', 'FFD070', (x, 5.6, 2.3), radius=0.3, subdivisions=1, parent=r), out['flamem'])
    return out


_build0, _reset0 = build, reset


def build():
    ka, ke = K.add, K.empty                                           # the rigs are made of some 1,300 small parts: build those the quick way too
    K.add, K.empty = add, empty
    _LAST[0] = None
    try:
        return _build_long()
    finally:
        K.add, K.empty = ka, ke


def _build_long():
    S = _build0()
    for name, fn in (('camp', set_camp), ('fields', set_fields), ('ward', set_ward), ('temple', set_temple)):
        S['colls'][name], S[name] = stage(name, fn)
    S['crew'] = []
    for i, (top, hat) in enumerate(CREWC):
        rig = K.Rig(dict(top=top, pants='2A3040', hand=SKINS[i % 3], boot='22262E'), hard_hat(hat))
        rig.sc = 0.96 + 0.03 * (i % 3)
        S['crew'].append(rig)
    S['navy'] = []
    for i, top in enumerate(('2C4A3A', '2C4A3A', '4A5A6A')):                                             # two navy divers and a doctor
        rig = K.Rig(dict(top=top, pants='20362C' if i < 2 else '2A3040', hand=SKINS[i], boot='171A20'), hood_head(SKINS[i], '1B1E26' if i < 2 else '17131A'))
        rig.sc = 1.0
        S['navy'].append(rig)
    S['farmer'] = K.Rig(dict(top='4A6A8A', pants='3A3A44', hand='B88458', boot='B88458', fore='B88458'), straw_head('B88458'))
    S['farmer'].sc = 0.97
    new = S['crew'] + S['navy'] + [S['farmer']]
    S['humans'] += new
    S['cast'] += new
    S['foils'] = [keep(add('ico_sphere', 'C8D0DC', AWAY, radius=1, subdivisions=1, rough=0.2)) for _ in range(4)]
    S['pad'] = pd = keep(empty(AWAY))
    box('F0E8D2', (0, 0, 0), (0.62, 0.8, 0.03), pd)
    S['scrib'] = [box('2A2E38', (0, 0.26 - 0.13 * j, 0.02), (0.46, 0.022, 0.01), pd) for j in range(5)]
    S['pencil'] = keep(add('cylinder', 'D8A22A', AWAY, radius=0.022, depth=0.42, vertices=5, rough=0.5))
    S['pouch'] = keep(add('cylinder', 'E87A1E', AWAY, radius=0.1, depth=0.5, vertices=7, rough=0.4))
    S['case'] = cs = keep(empty(AWAY))
    box('3A3F4C', (0, 0, 0.13), (1.0, 0.66, 0.26), cs)
    S['lid'] = empty((0, 0.33, 0.26), cs)
    box('3A3F4C', (0, -0.33, 0.04), (1.0, 0.66, 0.08), S['lid'])
    for j in range(4):
        add('cylinder', 'F4F4F0' if j % 2 else 'BFEFFF', (-0.3 + 0.2 * j, 0.0, 0.3), radius=0.05, depth=0.2, vertices=6, parent=cs, rough=0.2)
    S['vial'] = keep(add('cylinder', 'BFEFFF', AWAY, radius=0.055, depth=0.24, vertices=6, rough=0.15))
    S['lock'] = keep(add('torus', 'D8DCE4', AWAY, major_radius=0.2, minor_radius=0.035, major_segments=12, minor_segments=4, rough=0.3))
    reset(S)
    return S


def reset(S):
    _reset0(S)
    if 'camp' not in S or 'lid' not in S:
        return
    paint(S['camp']['lampm'], 'FFF2D0', 0.0)
    for b, (px, py) in zip(S['camp']['pumps'], PUMPS):
        b.location, b.rotation_euler = (px, py, 0), (0, 0, 0)
    paint(S['temple']['flamem'], 'FFD070', 14.0)
    for sc_ in S['scrib']:
        sc_.scale = (0.46, 0.022, 0.01)
    S['lid'].rotation_euler = (0, 0, 0)
    for e, hd, arm in S['ward']['boys']:
        e.location.z = 1.1


# ---------------------------------------------------------------- light for the new sets
def camp_env(S, night=0.0):
    A = env(S, 'camp', lerp_hex('5A6CA8', '1C2648', night), sun=lerp(3.2, 1.0, night), sunc='AFC0F4', sdir=(0.4, -0.6, 0.6), fk=2.4, skyk=lerp(3.2, 1.6, night))
    paint(S['camp']['lampm'], 'FFF2D0', 9.0)
    return A


def camp_lamps(S, A, idx=(0, 1, 2), e=26000):
    for i, j in enumerate(idx):
        x, y = S['camp']['poles'][j]
        lampat(S, i, A(x, y - 0.8, 4.9), e, 'FFE8C0')


def fields_env(S, wl=0.0):
    A = env(S, 'fields', 'A8B8C0', sun=3.4, sunc='F4ECD8', sdir=(-0.5, -0.5, 0.7), fk=2.0, skyk=2.2)
    S['fields']['water'].location = (0, 13, lerp(-0.47, -0.13, wl))
    return A


def ward_env(S):
    return env(S, 'ward', 'C8D8E4', sun=1.2, sunc='FFF4E0', sdir=(0.5, -0.4, 0.75), fk=2.0, skyk=0.7)


def temple_env(S):
    return env(S, 'temple', '2A2038', sun=0.5, sunc='FFC890', sdir=(-0.3, -0.6, 0.7), fk=2.2, skyk=1.0)


def night_mouth(S):
    return env(S, 'mouth', '2A3A64', sun=1.4, sunc='9FB4F0', sdir=(-0.3, -0.7, 0.6), fk=2.2, skyk=1.6)


def grey_day(S):
    return env(S, 'mouth', '93A2AC', sun=3.2, sunc='E8E4D8', sdir=(0.4, -0.7, 0.6), fk=2.0, skyk=2.0)


def foil(S, A, i, seat, up=0.95):
    x, y = SEATS[seat]
    o = S['foils'][i]
    o.location = A(*lp(x, y + 0.3, up - 0.12))
    o.scale = (0.5, 0.26, 0.55)
    o.rotation_euler = (0.25, 0, 0.2 * math.sin(i * 2.0))


def kneel(rig, pos, yaw, face='calm', **over):
    rig.place(pos, yaw)
    d = dict(KNEEL, aL=(0.7, 0.05, 0.8), aR=(0.9, 0.05, 0.7), head=(0.25, 0.0))
    d.update(over)
    rig.apply(P('stand', **d))
    rig.face = face


def flyer(S, pos, yaw, lt, pitch=0.25, head=(0.1, 0.0)):
    rk = S['rook']
    fl = math.sin(lt * 21)
    rk.place(pos, yaw, pitch)
    rk.apply(P('stand', aL=(0.2, 1.35 + 0.5 * fl, 0.25), aR=(0.2, 1.35 + 0.5 * fl, 0.25), lL=(0.55, 0.95), lR=(0.35, 0.85), head=head))
    return rk


# ---------------------------------------------------------------- the cold open: he is taken under
def take_under(S, k, t, lt):
    A = chamber(S)
    dn = sm((lt - 1.5) / 1.3)
    d = S['divers'][0]
    dp = (-0.6, -2.6 - 0.8 * dn)
    d.place(A(dp[0], dp[1], -1.5 - 1.1 * dn), look_yaw(dp, (-0.6, -9)) + 0.5)
    hold = sm((lt - 0.5) / 0.6)
    d.apply(P('stand', aL=(lerp(0.5, 1.15, hold), 0.35, 0.6), aR=(lerp(0.5, 1.15, hold), 0.35, 0.6), head=(0.4, 0.0)))
    dlamp(S, d, 4200, True)
    p = S['pat']
    p.place(A(dp[0] + 1.75, dp[1] + 0.25, 0.14 - 0.95 * dn + 0.04 * math.sin(t * 3.5)), -PI / 2 + 0.5, PI / 2)
    p.apply(limp_pose())
    p.face = 'shut'
    wear_mask(S, p)
    for i, o in enumerate(S['rings']):
        u = (lt * 0.7 + i / 3) % 1
        o.location = A(dp[0] + 0.9, dp[1] + 0.1, 0.03)
        o.scale = (0.7 + 2.4 * u, 0.7 + 2.4 * u, 1)
    if dn > 0.5:
        bubbles(S, A(dp[0] + 1.0, dp[1], -0.3), t, 6, 0, 0.5)
    rope(S, 0, A(1.6, 0.9, 0.35), A(1.0, -9.0, -0.6))
    lampat(S, 0, A(2.6, -4.6, 2.6), 900, 'E8F6FF')
    lampat(S, 1, A(-3.5, -1.0, 3.0), 260, 'FFC890')
    shoot(S, A(lerp(3.9, 3.1, k), lerp(-5.6, -4.9, k), lerp(0.75, 0.5, k)), A(0.4, -2.5, lerp(0.45, 0.1, k)), 30, roll=0.03 * math.sin(t * 2), fill=1.3)


def rook_edge(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.15)
    rk = S['rook']
    rp = lp(1.4, 1.0)
    cam = (lerp(-1.6, -1.0, k), lerp(-4.4, -3.8, k), 1.9)
    turn = sm((lt - 1.2) / 0.5)
    rk.place(A(*rp), lerp(look_yaw(rp, (-0.6, -4)), look_yaw(rp, cam), turn))
    rk.apply(blend(P('point', aR=(1.0, 0.1, 0.1), head=(0.3, 0.0)), P('cross', head=(0.05, 0.0)), (lt - 1.2) / 0.5))
    S['rface'] = 'shocked' if lt < 0.5 else 'deadpan'
    bubbles(S, A(-0.2, -3.2, -0.2), t, 6, 0, 0.35)
    for i, o in enumerate(S['rings'][:2]):
        u = (lt * 0.6 + 0.5 * i) % 1
        o.location = A(-0.2, -3.2, 0.03)
        o.scale = (0.5 + 2.0 * u, 0.5 + 2.0 * u, 1)
    rope(S, 0, A(1.6, 0.9, 0.35), A(1.0, -9.0, -0.6))
    lampat(S, 0, A(0.4, -2.2, 3.2), 800, 'E8F6FF')
    lampat(S, 1, A(4.2, -0.6, 3.4), 320, 'FFC890')
    shoot(S, A(*cam), A(rp[0] - 0.5, rp[1], rp[2] + 2.2), 30, fill=1.2)


# ---------------------------------------------------------------- the first day
def arrive(S, k, t, lt):
    A = grey_day(S)
    T = S['team']
    for i, rig in enumerate((T[0], T[4], T[8], T[2], T[10], T[6], T[12])):
        y = -15.0 + 1.9 * (6 - i) + 5.0 * k
        x = (-0.9, 0.8, -0.2, 1.2, -1.2, 0.4, 0.0)[i]
        rig.place(A(x, y, 0.0), PI + 0.12 * math.sin(i * 2.0))
        rig.apply(walk(t + i * 0.31, 1.6))
        rig.face = 'warm'
        rig.jawv = 0.4 if i % 3 == 0 else 0.0
    S['mouth']['wheel'].rotation_euler = (t * 3.0 * max(0.0, 1 - k), 0, 0)
    rk = S['rook']
    rp = (-5.2, -11.0, 1.2)
    rk.place(A(*rp), look_yaw(rp, (0, -15 + 14 * k)))
    rk.apply(P('hips', head=(0.1, 0.0)))
    S['rface'] = 'deadpan'
    shoot(S, A(lerp(8.6, 7.6, k), lerp(-13.5, -11.5, k), lerp(1.7, 2.0, k)), A(-2.6, lerp(-10.0, -7.5, k), 1.9), 24, fill=0.9)


def locked_bikes(S, k, t, lt):
    A = night_mouth(S)
    c0, c1 = S['crew'][0], S['crew'][3]
    p0 = (lerp(-2.0, -5.6, sm(k * 1.3)), lerp(-16.0, -14.2, sm(k * 1.3)))
    c0.place(A(p0[0], p0[1], 0), look_yaw(p0, (-7.3, -12.0)))
    arr = sm((k - 0.6) / 0.25)
    c0.apply(blend(dict(walk(t, 1.5), aR=(1.2, 0.1, 0.3)), P('point', aR=(1.0, 0.1, 0.2), head=(0.35, 0.0), lean=0.2), arr))
    c0.face = 'wide' if arr > 0.5 else 'calm'
    torch(S, 0, c0, 1.0, li=None)
    sweep = lerp(-9.8, -7.3, sm(k * 1.4)) + 0.5 * math.sin(t * 2.2) * (1 - arr)
    lampat(S, 0, A(sweep, -13.4, 1.6), 900, 'FFF2C0')
    p1 = (lerp(1.5, -1.5, k), lerp(-19.0, -17.0, k))
    c1.place(A(p1[0], p1[1], 0), look_yaw(p1, (-7, -12)))
    c1.apply(walk(t + 0.4, 1.5))
    torch(S, 1, c1, 1.0, li=1, watts=260)
    S['lock'].location = A(-9.8 + 1.25 * 2 + 0.03, -12.86, 0.62)
    S['lock'].rotation_euler = (0.3, PI / 2, 0.2)
    lampat(S, 2, A(-9.0, -16.0, 3.4), 900, '8FA8E0')
    lampat(S, 3, A(-7.2, -13.6, 1.2), 300, 'FFF2C0')
    shoot(S, A(lerp(-10.4, -9.6, k), lerp(-17.6, -16.8, k), lerp(2.1, 1.7, k)), A(-6.6, -12.6, 0.9), 30, fill=1.0)


# ---------------------------------------------------------------- outside: the camp, the pumps, the fields
def crew_work(S, A, t, cheer=0.0):
    """The five rescue workers about the camp: three at the map table, one carrying an air tank across, one waving people on."""
    C = S['crew']
    spots = ((-9.7, 6.0, -PI / 2), (-4.3, 6.0, PI / 2), (-8.0, 7.7, 0.0), (0.5, 0.5, 2.6), (8.6, 1.4, 0.8))
    party = ((-4.6, 1.6), (-3.0, 3.6), (1.6, 2.4), (3.2, 4.2), (0.0, 5.4))
    for i, (rig, (x, y, yw)) in enumerate(zip(C, spots)):
        if i == 3 and not cheer:
            u = (t * 0.2) % 1
            rig.place(A(lerp(-3.0, 9.0, u), 0.6, 0), -PI / 2)
            rig.apply(dict(walk(t, 1.5), aL=(0.9, -0.1, 1.2, 0.5), aR=(0.9, -0.1, 1.2, 0.5)))
            tk = S['tanks'][0]
            tk.location = world_of(rig.body, (0.0, -0.5, 0.7))
            tk.rotation_euler = (0, PI / 2 - 0.15, rig.root.rotation_euler[2] + PI)
        else:
            hop = cheer * 0.35 * abs(math.sin(t * 6 + i * 1.3))
            if cheer:
                x, y = party[i]
                yw = 0.25 * math.sin(i * 2.0)
            rig.place(A(x, y, hop), yw)
            base = (P('wash', lean=0.25, head=(0.4, 0.2 * math.sin(t + i))), P('point', aR=(1.2, 0.2, 0.2), lean=0.15, head=(0.3, 0.0)),
                    P('think', head=(0.3, 0.0)), P('stand'), P('point', aR=(1.6 + 0.3 * math.sin(t * 4), 0.4, 0.2), head=(-0.1, 0.4)))[i]
            rig.apply(blend(base, P('up', aL=(2.8, 0.3 + 0.2 * math.sin(t * 7 + i), 0.1), aR=(2.8, 0.3 - 0.2 * math.sin(t * 7 + i), 0.1)), cheer))
        rig.face = 'warm' if cheer > 0.5 else 'calm'
        rig.jawv = cheer * (0.6 + 0.4 * math.sin(t * 9 + i))


def camp_wide(S, k, t, lt):
    A = camp_env(S)
    crew_work(S, A, t)
    camp_lamps(S, A)
    for j, b in enumerate(S['camp']['pumps']):
        b.location = (PUMPS[j][0] + 0.03 * math.sin(t * 47 + j), PUMPS[j][1], 0.02 * abs(math.sin(t * 41 + j)))
    rk = S['rook']
    rp = (-12.0, -4.0, 1.1)
    rk.place(A(*rp), look_yaw(rp, (-4, 8)) + 0.5 * sm((lt - 1.0) / 0.6))
    rk.apply(blend(P('hips', head=(0.0, 0.3)), P('think', head=(0.05, -0.3)), (lt - 1.0) / 0.6))
    S['rface'] = 'calm'
    lampat(S, 3, A(-11.0, -7.0, 3.0), 500, 'FFC890')
    a = lerp(-0.25, 0.15, k)
    shoot(S, A(-9.0 + 18 * math.sin(a), -13.0 + 3 * k, lerp(4.4, 3.4, k)), A(lerp(-3.0, -1.0, k), 7.0, 2.2), 24, fill=1.0, fcol='FFE8D0')


def pumps_row(S, k, t, lt):
    A = camp_env(S)
    crew_work(S, A, t)
    camp_lamps(S, A, (2, 1, 0))
    for j, b in enumerate(S['camp']['pumps']):
        b.location = (PUMPS[j][0] + 0.05 * math.sin(t * 47 + j * 2), PUMPS[j][1] + 0.04 * math.sin(t * 53 + j), 0.03 * abs(math.sin(t * 41 + j)))
        b.rotation_euler = (0, 0.02 * math.sin(t * 39 + j), 0)
        for q in range(3):
            u = (t * 1.4 + q / 3 + j * 0.23) % 1
            o = S['foam'][j * 3 + q]
            o.location = A(PUMPS[j][0] - 0.55 + 0.3 * u, PUMPS[j][1], 2.0 + 1.6 * u)
            o.scale = (0.3 + 0.6 * u,) * 3
    c = S['crew'][4]
    kneel(c, A(PUMPS[2][0] - 0.4, PUMPS[2][1] - 1.5, 0), PI, aR=(1.3, 0.1, 0.4 + 0.2 * math.sin(t * 6)), head=(0.3, 0.0))
    rk = S['rook']
    x = lerp(PUMPS[0][0] - 2.8, PUMPS[0][0] - 1.1, sm(lt / 1.4))
    rp = (x, PUMPS[0][1] - 1.9, 0.0)
    stop = sm((lt - 1.4) / 0.4)
    rk.place(A(*rp), lerp(-PI / 2, look_yaw(rp, PUMPS[0]) , stop))
    rk.apply(blend(walk(t, 1.4), P('tap', head=(0.25, 0.1)), (lt - 1.4) / 0.4))
    S['rface'] = 'deadpan'
    lampat(S, 3, A(8.0, -7.0, 3.0), 900, 'FFC890')
    shoot(S, A(lerp(6.0, 7.0, k), lerp(-8.6, -7.8, k), lerp(1.7, 2.0, k)), A(lerp(11.0, 12.0, k), -2.0, 1.5), 26, fill=1.2, fcol='FFE8D0')


def gush(S, A, t, n=7):
    paint(S['streamm'], 'A89468', 0.25)
    for j, o in enumerate(S['streams'][:n]):
        u = (t * 1.3 + j / n) % 1
        o.location = A(0.5 * math.sin(j * 2.1) * u, 8.6 - 4.6 * u, 1.0 - 1.1 * u * u)
        o.scale = (0.45 + 1.0 * u, 1.1, 0.26)
        o.rotation_euler = (0.9 * u, 0, 0.3 * math.sin(j))
    foam(S, [A(-2.5 + 5 * rn(i, 260), 3.0 + 2.6 * rn(i, 261) - 1.5 * ((t * 0.5 + i * 0.13) % 1), 0.12 + 0.3 * abs(math.sin(t * 7 + i))) for i in range(14)], 1.3)


def pipe_out(S, k, t, lt):
    A = fields_env(S, 0.45 + 0.3 * k)
    gush(S, A, t)
    shoot(S, A(lerp(4.6, 3.6, k), lerp(1.0, 2.2, k), lerp(1.3, 1.0, k)), A(0.0, 7.2, 0.8), 24, roll=0.03 * math.sin(t * 3), fill=1.0)


def fields_flood(S, k, t, lt):
    A = fields_env(S, 0.15 + 0.85 * sm(k * 1.15))
    gush(S, A, t)
    f = S['farmer']
    fp = (-5.0, -1.9, 0.35)
    f.place(A(*fp), look_yaw(fp, (0, 9)))
    f.apply(P('hips', head=(0.1, 0.0)))
    a = lerp(-0.5, -0.25, k)
    shoot(S, A(40 * math.sin(a), 10 - 40 * math.cos(a), lerp(11.0, 8.0, k)), A(0.0, 12.0, 0.0), 26, fill=1.0)


def farmer(S, k, t, lt):
    A = fields_env(S, 1.0)
    gush(S, A, t)
    f = S['farmer']
    fp = (-1.2, -1.9, 0.35)
    cam = (lerp(2.6, 2.0, k), lerp(-8.2, -7.4, k), 2.2)
    nod = sm((lt - 1.0) / 0.4)
    f.place(A(*fp), lerp(look_yaw(fp, (0, 9)), look_yaw(fp, cam), sm((lt - 0.4) / 0.6)) )
    f.apply(blend(P('hips', head=(0.1, 0.0)), P('stand', aR=(0.9, 0.5, 0.9), head=(0.3 * math.sin(lt * 5) * nod + 0.1, 0.0)), nod))
    f.face = 'warm'
    rk = S['rook']
    rp = (1.5, -1.9, 0.35)
    rk.place(A(*rp), look_yaw(rp, ((fp[0] + cam[0]) / 2, (fp[1] + cam[1]) / 2)))
    tip = sm((lt - 1.3) / 0.35)
    rk.apply(blend(P('stand', head=(0.0, 0.0)), P('hat', head=(0.25, 0.0)), tip))
    S['hat_tip'] = 0.6 * tip
    S['rface'] = 'warm'
    shoot(S, A(*cam), A(0.1, -1.9, 2.5), 30, fill=1.2, fcol='FFF0E0')


# ---------------------------------------------------------------- company on the mud, and letters
def doctor_stay(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.15, turn=0.25)
    for i, seat in enumerate((0, 2, 3, 6)):
        foil(S, A, i, seat)
    n0, n1, doc = S['navy']
    p = lp(-2.7, 1.5)
    kneel(n0, A(*p), look_yaw(p, SEATS[0]) , 'warm', aR=(1.2, 0.1, 0.5 + 0.15 * math.sin(t * 3)), head=(0.15, 0.0))
    p = lp(2.8, 1.4)
    kneel(n1, A(*p), look_yaw(p, (5.0, -3.0)) + 0.9, 'warm', aL=(0.9, 0.1, 0.9), aR=(1.1, 0.3, 0.6), head=(0.1, -0.5))
    p = lp(0.9, 3.6)
    kneel(doc, A(*p), look_yaw(p, SEATS[2]) , 'calm', aR=(1.25, 0.2, 0.4), aL=(0.6, 0.0, 1.0), head=(0.3, 0.0))
    torch(S, 0, n1, 1.0, li=0, watts=500)
    lampat(S, 1, A(-3.0, -1.0, 3.2), 900, 'FFE0B8')
    lampat(S, 2, A(3.0, 0.0, 3.6), 700, 'E8F6FF')
    shoot(S, A(lerp(5.2, 4.4, k), lerp(-3.4, -2.8, k), lerp(2.3, 2.6, k)), A(-0.4, 3.0, 2.0), 26, fill=1.2, fcol='FFE8D0')


def write_pad(S, pos, rot, k):
    S['pad'].location, S['pad'].rotation_euler = pos, rot
    for j, o in enumerate(S['scrib']):
        u = max(0.0, min(1.0, k * 5 - j))
        o.scale = (0.46 * u + 0.001, 0.022, 0.01)
        o.location.x = -0.23 + 0.23 * u


def letters(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, nod=0.4)
    pp = A(*lp(-0.9, 3.9, 1.25))
    write_pad(S, pp, (TH + 0.5, 0, 0.15), k * 1.1)
    u = (k * 5.5) % 1
    j = min(4, int(k * 5.5))
    hx = pp[0] - 0.2 + 0.42 * u
    hy = pp[1] + 0.22 - 0.11 * j
    h = S['bhand']
    h.place((hx + 0.3, hy - 0.2, pp[2] + 0.36), (0.75, 0.25, -1.2))
    h.grip(0.85)
    S['pencil'].location = (hx, hy + 0.08, pp[2] + 0.2)
    S['pencil'].rotation_euler = (0.5, 0.3, 0.4)
    torch(S, 0, S['team'][6], 0.9 + 0.1 * math.sin(t * 19), li=None)
    lampat(S, 0, (pp[0] + 0.6, pp[1] - 1.0, pp[2] + 0.9), 160, 'FFF0C8')
    lampat(S, 1, A(-3, 1, 4), 200, 'FFD8A8')
    shoot(S, (pp[0] + lerp(0.9, 0.5, k), pp[1] - lerp(1.9, 1.6, k), pp[2] + lerp(1.3, 1.1, k)), (pp[0], pp[1] + 0.05, pp[2]), 40, fill=1.0, fcol='FFE8D0')


def letter_out(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.1, turn=-0.3, skip=(2,))
    give = sm((lt - 0.5) / 0.6)
    dn = sm((lt - 1.9) / 1.0)
    d = S['divers'][1]
    dp = (0.9, -1.7 - 1.2 * dn)
    d.place(A(dp[0], dp[1], -1.5 - 1.0 * dn), look_yaw(dp, (0.9, 4)) + 2.6 * dn)
    d.apply(P('stand', aR=(lerp(1.3, 0.6, give), 0.1, lerp(0.2, 1.6, give)), aL=(0.4, 0.2, 0.5), head=(-0.1 + 0.4 * dn, 0.0)))
    dlamp(S, d, 2500, False)
    b = S['team'][2]
    bp = lp(0.9, 0.95)
    kneel(b, A(*bp), 0.0, 'warm', aR=(lerp(1.2, 0.4, give), 0.0, 0.3), head=(0.3, 0.0))
    hb, hd = world_of(b.hands[1], (0, -0.2, -0.1)), world_of(d.hands[1], (0, -0.15, -0.05))
    S['pouch'].location = tuple(lerp(hb[i], hd[i], give) for i in range(3))
    S['pouch'].rotation_euler = (PI / 2, 0, 0.4)
    rk = S['rook']
    rp = lp(3.3, 1.2)
    rk.place(A(*rp), look_yaw(rp, dp))
    rk.apply(blend(P('cross', head=(0.2, 0.0)), P('stand', aR=(2.2, 0.5 + 0.25 * math.sin(lt * 9), 0.3), head=(0.1, 0.0)), (lt - 1.9) / 0.5))
    S['rface'] = 'warm'
    for i, o in enumerate(S['rings'][:2]):
        u = (lt * 0.8 + 0.5 * i) % 1
        o.location = A(dp[0], dp[1], 0.03)
        o.scale = (0.8 + 1.8 * u, 0.8 + 1.8 * u, 1)
    rope(S, 0, A(1.6, 0.9, 0.35), A(1.0, -9.0, -0.6))
    lampat(S, 0, A(-1.5, -2.5, 3.0), 900, 'E8F6FF')
    lampat(S, 1, A(5.0, -0.5, 3.2), 400, 'FFC890')
    shoot(S, A(lerp(-4.2, -3.4, k), lerp(-4.0, -3.6, k), lerp(1.2, 1.5, k)), A(1.4, -0.2, 1.3), 28, fill=1.2)


def coach_sorry(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='shut', nod=0.5)
    co = S['team'][12]
    x, y = SEATS[12]
    co.place(A(*lp(x, y)), 0.0)
    co.apply(P('sit', **dict(HUG, aL=(1.0, -0.1, 1.2, 0.5), aR=(1.0 + 0.04 * math.sin(t * 8), -0.2, 1.3, 0.6), head=(0.62, 0.0))))
    co.face = 'sad'
    pp = A(*lp(x, y - 0.75, 1.12))
    write_pad(S, pp, (TH + 0.7, 0, 0.0), 0.3 + 0.7 * k)
    S['pencil'].location = (pp[0] + 0.1 + 0.1 * math.sin(t * 6), pp[1] + 0.02, pp[2] + 0.2)
    S['pencil'].rotation_euler = (0.5, 0.3, 0.4)
    rk = S['rook']
    rp = lp(4.6, 7.2)
    rk.place(A(*rp), look_yaw(rp, (x, y)) - 1.0)
    away = sm((lt - 1.4) / 0.5)
    rk.apply(P('sit', **dict(HUG, head=(0.3, lerp(0.5, -0.5, away)))))
    S['hat_tip'] = 0.7 * away
    S['rface'] = 'sad'
    torch(S, 0, S['team'][9], 0.8 + 0.1 * math.sin(t * 17), li=None)
    lampat(S, 0, (pp[0] - 0.5, pp[1] - 1.2, pp[2] + 1.0), 260, 'FFF0C8')
    lampat(S, 1, A(4.5, 4.5, 5.0), 320, 'FFD8A8')
    c = lp(lerp(-2.2, -1.6, k), 3.4, 1.9)
    shoot(S, A(*c), A(x + 1.5, y + 0.4, lp(x, y)[2] + 1.7), 30, fill=1.2, fcol='FFE0C0')


# ---------------------------------------------------------------- what do you do?
def search_map(S, k, t, lt):
    A = camp_env(S)
    crew_work(S, A, t)
    camp_lamps(S, A)
    rk = S['rook']
    rp = (-6.2, 7.8, 0.0)
    rk.place(A(*rp), 0.15)
    rk.apply(blend(P('cross', head=(0.35, 0.0)), P('tap', head=(0.3, 0.15)), (lt - 0.6) / 0.4))
    S['rface'] = 'calm'
    lampat(S, 3, A(-7.0, 5.0, 3.2), 700, 'FFE8C0')
    lampat(S, 4, A(-3.5, 3.0, 2.6), 300, 'FFC890')
    shoot(S, A(lerp(-5.6, -6.6, k), lerp(0.4, 1.0, k), lerp(2.9, 2.6, k)), A(-7.0, 6.4, 1.9), 28, fill=1.2, fcol='FFE8D0')


def still_water(S, k, t, lt):
    A = passage(S, 0.12)
    tank_row(S, A, 4)
    dim = 1 - sm((k - 0.25) / 0.6)
    obj, m = S['torch'][0]
    obj.location = A(-3.2, 6.0, 0.25)
    obj.rotation_euler = (0, 0, 0)
    fl = dim * (0.75 + 0.25 * math.sin(t * 11) * math.sin(t * 3.3))
    paint(m, 'FFD8A0', 12 * fl)
    lampat(S, 0, A(-3.1, 5.6, 1.0), 900 * fl, 'FFC890')
    lampat(S, 1, A(0, 14, 5), 700, '7FB8D0')
    drips(S, A(-1.0, 4.0, 4.6), t, 6, 2.0, 4.3, 0.8)
    for i, o in enumerate(S['rings']):
        u = (lt * 0.6 + i / 3) % 1
        o.location = A(-1.0 + 2.0 * math.cos(i * 2.4), 4.0 + 1.0 * math.sin(i * 2.4), 0.14)
        o.scale = (0.2 + 1.3 * u, 0.2 + 1.3 * u, 1)
    shoot(S, A(lerp(2.6, 1.8, k), lerp(-3.5, -1.5, k), lerp(2.6, 1.2, k)), A(-2.6, 6.5, 0.7), 26, fill=0.5 + 0.6 * dim)


# ---------------------------------------------------------------- the plan
def doc_kit(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='calm', nod=0.15, skip=(12,))
    bl = S['ledge']['blanket']
    bl.location = lp(0.0, 2.9, 0.06)
    bl.rotation_euler = (TH, 0, 0)
    p = S['pat']
    pp = lp(0.0, 2.6, 0.1)
    p.place(A(*pp), 0.2)
    p.apply(P('sit', aL=(0.6, 0.1, 0.6), aR=(0.6, 0.1, 0.6), head=(0.25, 0.3)))
    p.face = 'calm'
    d = S['divers'][1]
    dp = lp(2.0, 1.9)
    d.place(A(*dp), look_yaw(dp, (0.0, 2.6)))
    open_ = sm((lt - 0.4) / 0.6)
    d.apply(dict(KNEE, aR=(1.1, 0.2, 0.5 + 0.3 * open_), aL=(0.9, 0.0, 0.8), head=(0.45, 0.0)))
    dlamp(S, d, 0, False)
    cs = S['case']
    cs.location = A(*lp(1.3, 1.2, 0.02))
    cs.rotation_euler = (TH, 0, 0.5)
    S['lid'].rotation_euler = (1.9 * open_, 0, 0)
    co = S['team'][12]
    cp = lp(-1.6, 2.9)
    kneel(co, A(*cp), look_yaw(cp, (0.0, 2.6)), 'calm', aR=(1.15, 0.25, 0.6), head=(0.35, 0.0))
    lampat(S, 0, A(1.4, -0.8, 3.0), 900, 'E8F6FF')
    lampat(S, 1, A(-3, 0.5, 3.0), 320, 'FFC890')
    shoot(S, A(lerp(-2.6, -1.8, k), lerp(-2.6, -2.0, k), lerp(2.2, 2.5, k)), A(0.7, 2.0, 1.5), 28, fill=1.2)


def vials(S, k, t, lt):
    A = chamber(S)
    cs = S['case']
    cp = A(*lp(1.3, 1.2, 0.02))
    cs.location = cp
    cs.rotation_euler = (TH, 0, 0.5)
    S['lid'].rotation_euler = (1.9, 0, 0)
    dn, up = sm(lt / 0.7), sm((lt - 0.9) / 0.8)
    hz = cp[2] + 1.3 - 0.75 * dn + 0.7 * up
    h = S['hands'][0]
    h.place((cp[0] + 0.25, cp[1] - 0.05, hz), (1.2, 0.0, -0.9))
    h.grip(lerp(0.3, 0.8, sm((lt - 0.6) / 0.3)))
    v = S['vial']
    v.location = (cp[0] + 0.02, cp[1] - 0.3, hz - 0.38) if lt > 0.75 else (cp[0] + 0.02, cp[1] - 0.3, cp[2] + 0.42)
    v.rotation_euler = (0.2 * up, 0.3 * up, 0)
    lampat(S, 0, (cp[0] - 0.8, cp[1] - 1.6, cp[2] + 1.8), 260, 'E8F6FF')
    lampat(S, 1, (cp[0] + 1.6, cp[1] + 0.6, cp[2] + 1.4), 160, 'FFC890')
    shoot(S, (cp[0] + lerp(-1.3, -0.7, k), cp[1] - lerp(2.3, 1.9, k), cp[2] + lerp(1.3, 1.7, k)), (cp[0] + 0.1, cp[1] - 0.1, cp[2] + 0.55 + 0.25 * up), 36, fill=1.1)


def team_watch(S, k, t, lt):
    A = chamber(S)
    seat_team(S, A, t, face='wide', nod=0.05, turn=-0.15, skip=(3, 12))
    co = S['team'][12]
    cp = lp(-4.6, 1.3)
    co.place(A(*cp), look_yaw(cp, (0, -6)))
    co.apply(P('stand', aL=(0.6, 0.0, 1.6, 1.0), aR=(0.6, 0.0, 1.6, 1.0), head=(0.25, 0.0)))
    co.face = 'sad'
    rk = S['rook']
    rp = lp(3.6, 2.7)
    rk.place(A(*rp), -0.9)
    rk.apply(P('sit', **dict(HUG, head=(0.2, 0.7 - 0.6 * sm((lt - 0.8) / 0.5)))))
    S['rface'] = 'sad'
    torch(S, 0, S['team'][1], 0.9, li=0, watts=420)
    lampat(S, 1, A(-4.0, -1.5, 3.4), 1400, 'E8F6FF')
    lampat(S, 2, A(5.5, 0.0, 3.4), 900, 'FFC890')
    shoot(S, A(lerp(5.0, 4.2, k), lerp(-2.6, -2.0, k), lerp(3.2, 2.9, k)), A(0.8, 4.0, 2.4), 26, fill=1.4)


def relay(S, k, t, lt):
    A = sump(S)
    y = lerp(0.0, 5.5, k)
    d = carried(S, A, y, t, x=-0.6, z=0.1)
    dlamp(S, d, 5200, True)
    bubbles(S, world_of(d.head, (0, 0.2, 0.3)), t, 5)
    d2 = S['divers'][1]
    d2.place(A(1.0, 8.4, -0.6 + 0.08 * math.sin(t * 2)), PI - 0.7, PI / 2 - 0.5)
    d2.apply(P('stand', aL=(1.3, 0.3, 0.6), aR=(2.2, 0.3, 0.2), lL=(0.2, 0.4), lR=(-0.1, 0.3), head=(-0.6, 0.0)))
    dlamp(S, d2, 2600, True)
    bubbles(S, world_of(d2.head, (0, 0.2, 0.3)), t + 0.5, 4, 5, 1.0)
    tk = S['tanks'][0]
    tk.location = A(1.4, 8.8, -1.4)
    tk.rotation_euler = (PI / 2, 0, 0.2)
    lampat(S, 0, A(-1.0, y + 6.5, 1.2), 500, 'DFF6F0')
    shoot(S, A(lerp(-1.3, -1.0, k), lerp(14.6, 13.8, k), lerp(1.3, 1.0, k)), A(0.2, lerp(5.5, 6.5, k), -0.3), 22, roll=-0.05 * math.sin(t * 1.4), fill=1.3, fcol='BFE8D8')


# ---------------------------------------------------------------- out, and the water again
def cheer(S, k, t, lt):
    A = camp_env(S, 0.6)
    up = sm((lt - 0.25) / 0.35)
    crew_work(S, A, t, up)
    camp_lamps(S, A)
    rk = S['rook']
    rp = (-1.6, -1.2, 0.0)
    rk.place(A(*rp), 0.15 * math.sin(t * 2))
    rk.apply(blend(P('cross'), P('up', head=(-0.2, 0.0)), (lt - 0.45) / 0.35))
    S['hat_jump'] = 0.5 * max(0.0, math.sin(min(1.0, max(0.0, lt - 0.45) / 0.5) * PI))
    S['rface'] = 'shocked' if lt < 1.0 else 'warm'
    lampat(S, 3, A(-1.0, -5.0, 3.0), 900, 'FFC890')
    lampat(S, 4, A(2.0, -3.0, 3.4), 900, 'FFE8C0')
    shoot(S, A(lerp(-3.6, -2.8, k), lerp(-6.6, -5.8, k), lerp(1.3, 1.6, k)), A(-0.8, 2.6, 2.3), 26, fill=1.2, fcol='FFE8D0')


def get_out(S, k, t, lt):
    wl = lerp(0.8, 1.9, sm(k))
    A = passage(S, wl)
    rigs = S['crew'][:3] + [S['navy'][0]]
    pts = [(-2.4 + 1.6 * i, 9.0 - 1.9 * (i % 2) - 9.0 * k, 0.0) for i in range(4)]
    wade(S, A, rigs, pts, t, 0.0, 'wide', 0.1)
    torch(S, 0, rigs[0], 1.0, li=0, watts=420)
    torch(S, 1, rigs[2], 1.0, li=1, watts=420)
    foam(S, [A(-4.5 + 9 * rn(i, 270), 15 - 10 * k - 3 * rn(i, 271), wl + 0.15 + 0.4 * abs(math.sin(t * 8 + i))) for i in range(14)], 1.6)
    flyer(S, A(2.6, 5.0 - 9.0 * k, 2.1 + 0.3 * math.sin(lt * 5)), 0.2, lt, head=(0.2, -0.5))
    S['rface'] = 'shocked'
    lampat(S, 2, A(3.0, 2.0 - 9.0 * k, 5.8), 600, 'FFC890')
    lampat(S, 3, A(0, 16, 5.5), 1600, 'A8D8E8')
    lampat(S, 4, A(-1.0, lerp(1.0, -7.0, k), 3.6), 1400, 'FFE8C8')
    shoot(S, A(lerp(1.8, 1.2, k), lerp(-1.5, -9.5, k), lerp(3.6, 3.2, k)), A(-0.6, lerp(7.0, -1.5, k), 2.0), 24, roll=0.03 * math.sin(t * 3), fill=1.3)


def out_mouth(S, k, t, lt):
    A = rescue_dusk(S)
    sky(S, '1A2444', 1.0)
    rigs = [S['crew'][0], S['navy'][0], S['crew'][2], S['navy'][1], S['crew'][1], S['navy'][2]]
    for i, rig in enumerate(rigs):
        y = 10.0 + 2.0 * (i // 2) - 9.0 * k
        x = (-1.3, 1.2)[i % 2] + 0.3 * math.sin(i * 1.7)
        rig.place(A(x, y, mz(y)), 0.1 * math.sin(i * 2.0))
        up = sm((k - 0.45 - 0.08 * i) / 0.2) if i % 3 == 0 else 0.0
        rig.apply(blend(walk(t + i * 0.3, 1.7), dict(walk(t + i * 0.3, 1.7), aR=(2.9, 0.2, 0.1), head=(-0.2, 0.0)), up))
        rig.face = 'warm'
        rig.jawv = 0.5 * up
    flyer(S, A(2.4, 4.0 - 5.0 * k, 1.5 + 0.3 * math.sin(lt * 5)), -0.5, lt, head=(0.2, -0.5))
    S['rface'] = 'warm'
    lampat(S, 0, A(-1.0, 4.0, 3.6), 1800, 'FFC890')
    lampat(S, 1, A(-4.5, 5.0, 5.2), 700, 'FFC890')
    shoot(S, A(lerp(-4.6, -3.8, k), lerp(-4.5, -3.5, k), lerp(1.4, 1.7, k)), A(-0.8, 5.0, 2.3), 32, fill=1.2, fcol='FFE8D0')


# ---------------------------------------------------------------- afterwards
def ward_boys(S, t, lt, wave=True):
    for i, (e, hd, arm) in enumerate(S['ward']['boys']):
        wv = sm((lt - 0.4 - 0.3 * i) / 0.3) if wave else 0.0
        arm.rotation_euler = (0.15 * math.sin(t * 9 + i) * wv, -(0.25 + 2.5 * wv + 0.3 * math.sin(t * 9 + i) * wv), 0)
        hd.rotation_euler = (0.05 * math.sin(t * 1.1 + i), 0, 0.25 * math.sin(t * 0.8 + i * 2.0))


def ward(S, k, t, lt):
    A = ward_env(S)
    ward_boys(S, t, lt)
    rk = S['rook']
    rp = (5.0, 2.0, 1.15)
    rk.place(A(*rp), -0.5)
    rk.apply(blend(P('cross', head=(0.1, 0.4)), P('stand', aR=(2.2, 0.5 + 0.25 * math.sin(lt * 9), 0.3), head=(0.0, 0.3)), (lt - 1.2) / 0.4))
    S['rface'] = 'warm'
    lampat(S, 0, A(-2.0, -1.0, 5.0), 700, 'FFF4E0')
    lampat(S, 1, A(6.0, 0.0, 4.0), 500, 'FFF4E0')
    shoot(S, A(lerp(-4.6, -3.4, k), lerp(-3.6, -3.0, k), lerp(2.6, 2.3, k)), A(1.8, 4.4, 1.9), 26, fill=1.0, fcol='FFF4E8')


def walk_home(S, k, t, lt):
    A = ward_env(S)
    for e, hd, arm in S['ward']['boys']:
        e.location.z = -3000
    T = S['team']
    for i, rig in enumerate((T[1], T[5], T[9], T[3], T[7], T[11], T[12])):
        u = 0.6 * k + 0.1 * (6 - i)
        x, y = lerp(0.0, 12.5, u), -2.3 - 1.0 * (i % 2) - 0.4 * math.sin(i)
        rig.place(A(x, y, 0.0), PI / 2 + 0.1 * math.sin(i * 2.0))
        rig.apply(walk(t + i * 0.31, 1.6))
        rig.face = 'warm'
    rk = S['rook']
    rp = (5.0, 2.0, 1.15)
    rk.place(A(*rp), -1.0 - 0.9 * k)
    rk.apply(P('hat', head=(0.1, 0.0)))
    S['hat_tip'] = 0.4
    S['rface'] = 'warm'
    lampat(S, 0, A(2.0, -5.0, 5.0), 700, 'FFF4E0')
    lampat(S, 1, A(10.0, -3.3, 3.0), 900, 'FFF0D0')
    shoot(S, A(lerp(-3.5, -1.5, k), lerp(-6.4, -5.8, k), lerp(2.0, 2.3, k)), A(7.0, -2.2, 1.9), 28, fill=1.0, fcol='FFF4E8')


def nov_row(S, A, t):
    for i, (e, hd) in enumerate(S['temple']['nov']):
        hd.rotation_euler = (0.34 + 0.04 * math.sin(t * 0.9 + i * 1.3), 0, 0.03 * math.sin(t * 0.6 + i))
        e.rotation_euler = (0.015 * math.sin(t * 0.7 + i * 2.0), 0, PI + 0.06 * math.sin(i * 2.0))
    fm = S['temple']['flamem']
    paint(fm, 'FFD070', 12 + 4 * math.sin(t * 13) * math.sin(t * 4.1))
    for j, f in enumerate(S['temple']['flames']):
        f.scale = (1 + 0.2 * math.sin(t * 9 + j * 1.7), 1, 1 + 0.3 * math.sin(t * 11 + j * 2.3))
    lampat(S, 0, A(-2.5, 4.4, 1.9), 420, 'FFC070')
    lampat(S, 1, A(2.5, 4.4, 1.9), 420, 'FFC070')


def novices(S, k, t, lt):
    A = temple_env(S)
    nov_row(S, A, t)
    lampat(S, 2, A(-7.0, -2.0, 4.0), 900, 'FFD8A8')
    shoot(S, A(lerp(-8.6, -7.4, k), lerp(4.6, 4.2, k), lerp(1.5, 1.8, k)), A(0.0, 2.2, 1.5), 28, fill=1.2, fcol='FFE0C0')


def candles(S, k, t, lt):
    A = temple_env(S)
    nov_row(S, A, t)
    rk = S['rook']
    rp = (6.4, 3.0, 0.0)
    rk.place(A(*rp), look_yaw(rp, (2.0, 5.6)))
    S['hat_off'] = sm((lt - 0.3) / 0.6)
    rk.apply(blend(P('stand', head=(0.15, 0.0)), to_chest(), (lt - 0.3) / 0.6))
    S['rface'] = 'sad'
    lampat(S, 2, A(6.0, 5.0, 2.2), 500, 'FFC070')
    lampat(S, 3, A(8.5, 0.0, 3.5), 500, 'FFD8A8')
    shoot(S, A(lerp(7.4, 6.8, k), lerp(8.6, 8.3, k), lerp(1.7, 2.0, k)), A(4.2, 3.6, 1.6), 28, fill=1.2, fcol='FFE0C0')


# ---------------------------------------------------------------- the thumbnail picture
def photo_thumb(S, k, t, lt):
    A = chamber(S)
    p = lie_pat(S, A, t, 1.0)
    wear_mask(S, p)
    hd = world_of(p.head)
    d = S['divers'][0]
    dp = lp(-1.75, 2.75)
    d.place(A(*dp), look_yaw(dp, (0.0, 3.0)))
    d.apply(dict(KNEE, aR=(1.25, 0.25, 0.5), aL=(1.1, 0.1, 0.6), head=(0.5, 0.0)))
    dlamp(S, d, 0, False)
    lampat(S, 0, (hd[0] + 1.6, hd[1] - 1.2, hd[2] + 2.0), 500, 'E8F6FF')
    lampat(S, 1, (hd[0] - 2.5, hd[1] + 2.5, hd[2] + 2.6), 600, 'FFC890')
    lampat(S, 2, (hd[0] + 0.5, hd[1] + 3.0, hd[2] + 1.5), 300, '8FD8F0')
    shoot(S, (hd[0] + 3.3, hd[1] - 0.6, hd[2] + 1.7), (hd[0] - 0.6, hd[1] - 1.0, hd[2] + 0.35), 34, fill=1.4)


HOST |= {'rook_edge', 'arrive', 'camp_wide', 'pumps_row', 'farmer', 'letter_out', 'coach_sorry', 'search_map', 'team_watch', 'cheer', 'get_out', 'out_mouth',
         'ward', 'walk_home', 'candles'}
SHOTS3D.update({f.__name__: f for f in (
    take_under, rook_edge, arrive, locked_bikes, camp_wide, pumps_row, pipe_out, fields_flood, farmer, doctor_stay, letters, letter_out, coach_sorry,
    search_map, still_water, doc_kit, vials, team_watch, relay, cheer, get_out, out_mouth, ward, walk_home, novices, candles)})
STILLS.update(thumb=photo_thumb)


REFRAME = dict(ledge_wide=(0.0, 0.6), stretcher_out=(0.0, 0.75))      # (lift the aim, distance multiplier): the Short framed these for a tall screen


def _reframed(f, dz, mul):
    def g(S, k, t, lt):
        f(S, k, t, lt)
        c, tg = S['camrig'].location, S['camtgt'].location
        S['camtgt'].location = (tg[0], tg[1], tg[2] + dz)
        S['camrig'].location = (tg[0] + (c[0] - tg[0]) * mul, tg[1] + (c[1] - tg[1]) * mul, tg[2] + (c[2] - tg[2]) * mul + dz)
    g.__name__ = f.__name__
    return g


for _k, (_dz, _mul) in REFRAME.items():
    SHOTS3D[_k] = _reframed(SHOTS3D[_k], _dz, _mul)
