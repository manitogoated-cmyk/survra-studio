"""Case 014 in 3D - Beck Weathers, the Dallas pathologist who was left for dead twice in the Everest storm of
May 1996, woke after about fifteen hours in the snow, stood up and walked into camp.

Built for this story only: a wind-scoured snow saddle with a cluster of dome tents (the high camp), a snow ridge
with a ledge above a sea of cloud, the inside of a storm-beaten tent, a glacier valley with ice towers where a
helicopter lands, a living room with a telephone and an armchair, the front of a house at dusk, and a stone cairn
with strings of flags at the foot of the mountain.

Everything is a generic low-poly reconstruction, not a model of the real mountain, camps, aircraft or home. No
emblem, flag of a country, sign or lettering is shown anywhere. Nothing graphic is shown: frost, ice and bandages
only. The other climbers are anonymous figures; nobody else's likeness is attempted."""
import math

import bpy

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(col=(0, 0, 0), ridge=(3000, 0, 0), tent=(6000, 0, 0), cwm=(9000, 0, 0), home=(12000, 0, 0), room=(15000, 0, 0),
           base=(18000, 0, 0))
FAR = (0, 0, -2000)
HOST = {'col_wide', 'rook_jolt', 'rook_cairn', 'rook_go', 'beck_climb', 'beck_blind', 'beck_wait', 'blizzard_hit', 'rescuer_no',
        'doctor_kneel', 'beck_rise', 'beck_walks', 'tent_night', 'tent_dawn', 'heli_land', 'heli_away', 'beck_bandaged',
        'rook_wrong', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'DDB092'
RED, BLUE, YEL, GRN = 'C8322C', '2F6FB8', 'E3B02A', '3E9A5C'
SNOW, ROCK = 'C4D2E6', '4A5266'
RA = 0.49                                   # the ridge's angle of climb
RC, RS = math.cos(RA), math.sin(RA)
CAMP = (26.0, 34.0)                         # the tents on the saddle
SPOT = (0.0, 0.0)                           # where he lies (feet here, head towards +Y)
_MOV = []


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def at(name, x, y, z):
    o = ORG[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def group(name, fn):
    """Build one set under its own origin and collection, so only one renders per shot."""
    old = set(bpy.data.objects)
    out = fn(empty(ORG[name]))
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for o in set(bpy.data.objects) - old:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        coll.objects.link(o)
    return coll, out


def own_mat(name, col, rough=0.6, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = rough
    tint(m, col, emit)
    return m


def tint(m, col, emit=0.0):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)
    b.inputs['Emission Color'].default_value = K.hexc(col)
    b.inputs['Emission Strength'].default_value = emit


def use(o, m):
    o.data.materials[0] = m
    return o


def mov(o):
    """Register a prop that shots move, so reset() can put it back exactly as it was built."""
    _MOV.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def rnd(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def vis(objs, on):
    for o in objs:
        o.hide_render = not on


def facing(frm, to):
    """Yaw that turns a rig standing at frm to look at to (rigs face -Y at yaw 0)."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def seg(o, a, b, w):
    """Stretch a unit cylinder between two points (a rope)."""
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def peak(r, x, y, rad, h, z0=0.0, cap=0.45, rock=ROCK, spin=0.0):
    add('cone', rock, (x, y, z0 + h / 2), rot=(0, 0, spin), radius1=rad, radius2=0, depth=h, vertices=5, parent=r)
    add('cone', 'E6EEF8', (x, y, z0 + h * (1 - cap) + h * cap / 2 + 0.4), rot=(0, 0, spin), radius1=rad * cap * 1.06, radius2=0, depth=h * cap,
        vertices=5, parent=r)


def dome(r, x, y, col, yaw=0.0, s=1.0):
    """A dome tent, half sunk in the snow, with a dark doorway."""
    t = empty((x, y, 0), r, (0, 0, yaw))
    add('ico_sphere', col, (0, 0, 0), scale=(2.6 * s, 2.2 * s, 1.7 * s), radius=1, subdivisions=2, parent=t, rough=0.7)
    add('cone', '1A1E2A', (0, -1.75 * s, 0.5 * s), rot=(-0.5, 0, 0), radius1=0.95 * s, radius2=0, depth=1.5 * s, vertices=3, parent=t)
    add('cube', 'E6EEF8', (0, 0.6 * s, 0.05), scale=(5.6 * s, 3.4 * s, 0.5 * s), size=1, parent=t)            # drifted snow round the skirt
    return t


# ---------------------------------------------------------------- the saddle (high camp)
def set_col(r):
    out = {}
    add('cube', SNOW, (0, 0, -0.5), scale=(1400, 1400, 1), size=1, parent=r)
    for j in range(46):                                                                                # wind-scoured rock showing through
        x, y = -70 + 140 * rnd(j, 1), -50 + 130 * rnd(j, 2)
        if abs(x) < 4 and -3 < y < 6:
            continue
        s = 0.5 + 1.3 * rnd(j, 3)
        add('ico_sphere', '3C4250' if j % 3 else '565C6C', (x, y, 0.05), rot=(0, 0, rnd(j, 4) * 6), scale=(s * 1.4, s, s * 0.45), radius=1,
            subdivisions=1, parent=r)
    for j in range(40):                                                                                # sastrugi: ridges of blown snow
        x, y = -70 + 140 * rnd(j, 5), -50 + 130 * rnd(j, 6)
        add('ico_sphere', 'DCE6F4', (x, y, -0.05), rot=(0, 0, 0.5 + 0.3 * rnd(j, 7)), scale=(3.5 + 3 * rnd(j, 8), 0.9, 0.32), radius=1,
            subdivisions=1, parent=r)
    add('ico_sphere', 'DCE6F4', (0.1, 1.3, -0.12), scale=(2.3, 3.6, 0.42), radius=1, subdivisions=2, parent=r)       # the drift he lies on
    peak(r, -90, 330, 210, 250, cap=0.5, spin=0.4)                                                    # the summit pyramid, far above the saddle
    peak(r, 150, 300, 150, 120, cap=0.4, spin=1.0)
    peak(r, -330, 120, 170, 150, cap=0.4, spin=0.2)
    peak(r, 330, 60, 160, 130, cap=0.5, spin=0.9)
    peak(r, 190, -330, 200, 210, cap=0.45, spin=0.5)
    peak(r, -200, -300, 170, 140, cap=0.4, spin=1.3)
    tents = [(0, 0, YEL, 0.3), (5.5, 2.5, 'FF7A1A', -0.4), (-5.0, 3.5, BLUE, 0.9), (2.0, 7.5, RED, 0.1), (-3.5, 9.5, YEL, -0.7),
             (8.5, 8.0, GRN, 0.5)]
    for dx, dy, c, yw in tents:
        dome(r, CAMP[0] + dx, CAMP[1] + dy, c, yw)
    for j in range(9):                                                                                # a pile of spent oxygen bottles
        add('cylinder', 'FF7A1A' if j % 2 else 'D8DCE4', (CAMP[0] - 3.4 + 0.42 * j, CAMP[1] - 3.2 + 0.2 * rnd(j, 9), 0.25),
            rot=(PI / 2, 0, 0.3 * rnd(j, 10)), radius=0.2, depth=1.3, vertices=6, parent=r, rough=0.4)
    out['camp'] = light((CAMP[0], CAMP[1] - 1, 3.5), 0, 'FFC27A', kind='POINT', parent=r)
    out['hollow'] = hw = mov(empty(FAR, r))                                                           # the empty shape he leaves in the snow
    add('ico_sphere', '7088B4', (0, 1.35, 0.26), scale=(0.95, 2.1, 0.07), radius=1, subdivisions=2, parent=hw)
    add('ico_sphere', '7088B4', (0, 3.0, 0.2), scale=(0.5, 0.5, 0.07), radius=1, subdivisions=2, parent=hw)
    for j in range(9):                                                                                # boot prints leading to the tents
        u = 0.07 + j * 0.035
        add('cube', '8FA2C4', (1.6 + CAMP[0] * u + (0.35 if j % 2 else -0.35), 2.5 + CAMP[1] * u, 0.06),
            rot=(0, 0, -math.atan2(CAMP[0], CAMP[1])), scale=(0.34, 0.8, 0.05), size=1, parent=hw)
    return out


# ---------------------------------------------------------------- the ridge and its ledge
def rp(d, x=0.0):
    """A point on the ridge crest: d along the ridge from the ledge (up is positive)."""
    return (x, d * RC, d * RS if (d > 0 or d < -7.0) else 0.0)


def set_ridge(r):
    out = {}
    rr = empty((0, 0, 0), r, (RA, 0, 0))
    add('cube', 'D6E0F0', (0, 0, -3), scale=(8, 300, 6), size=1, parent=rr)                             # the snow crest
    for s in (-1, 1):
        add('cube', ROCK, (s * 14, 0, -9.5), rot=(0, s * 0.62, 0), scale=(30, 300, 5), size=1, parent=rr)     # rock flanks falling away
        for j in range(14):
            add('cube', 'D6E0F0', (s * (7 + 5 * rnd(j, 1)), -120 + j * 19, -4.6 - 3.4 * rnd(j, 1)), rot=(0, s * 0.62, 0.3 * s),
                scale=(5 + 4 * rnd(j, 2), 9, 0.5), size=1, parent=rr)
    add('cube', 'DCE6F4', (0, -1.0, -1.5), scale=(15, 13, 3), size=1, parent=r)                         # the ledge
    for x, y, s in ((-1.3, 1.5, 0.75), (1.5, 1.6, 0.7), (5.2, 2.5, 1.1), (-5.6, -2.0, 0.9)):
        add('ico_sphere', '565C6C', (x, y, 0.2), scale=(s * 1.3, s, s * 0.85), radius=1, subdivisions=1, parent=r)
    add('cone', ROCK, (0, 190, 80), rot=(0, 0, 0.6), radius1=120, radius2=0, depth=170, vertices=5, parent=r)     # the summit, still far above
    add('cone', 'E6EEF8', (0, 190, 121), rot=(0, 0, 0.6), radius1=60, radius2=0, depth=90, vertices=5, parent=r)
    add('cube', 'A8B8D4', (0, 0, -64), scale=(4000, 4000, 2), size=1, parent=r, emit=0.15)               # the sea of cloud below
    for j in range(60):
        a, d = rnd(j, 3) * 6.28, 90 + 700 * rnd(j, 4)
        add('ico_sphere', 'C2D0E6', (d * math.cos(a), d * math.sin(a), -62), scale=(1, 1, 0.3), radius=18 + 40 * rnd(j, 5), subdivisions=1,
            parent=r, emit=0.1)
    for j, (x, y, rad, h) in enumerate(((-330, 420, 150, 190), (360, 330, 170, 170), (-460, -80, 140, 150), (420, -220, 160, 180),
                                        (-180, -520, 170, 170), (170, 620, 130, 200))):
        peak(r, x, y, rad, h, z0=-64, cap=0.55, spin=j * 0.7)
    out['storm'] = st = mov(empty((0, -420, -260), r))                                                # the storm cloud that climbs the ridge
    for j in range(16):
        add('ico_sphere', '56607A' if j % 2 else '6E7890', (-170 + 340 * rnd(j, 6), -60 + 120 * rnd(j, 7), -40 + 80 * rnd(j, 8)),
            radius=60 + 50 * rnd(j, 9), subdivisions=1, parent=st)
    return out


# ---------------------------------------------------------------- inside the tent
def set_tent(r):
    out = dict(walls=[])
    out['fabm'] = fm = own_mat('fabric', 'D9772A', 0.8, 0.3)
    add('cube', '2E2622', (0, 0, -0.1), scale=(10, 14, 0.2), size=1, parent=r)
    add('cube', '4E5A6E', (0.2, 0, 0.06), scale=(3.4, 9.5, 0.14), size=1, parent=r)                     # sleeping mat
    for s in (-1, 1):
        w = empty((s * 4.4, 0, 0), r, (0, -s * 0.72, 0))
        use(add('cube', 'D9772A', (0, 0, 3.35), scale=(0.08, 13.4, 6.9), size=1, parent=w), fm)
        for j in range(4):                                                                             # stitched seams
            add('cube', '8A4418', (-s * 0.06, -5 + j * 3.3, 3.35), scale=(0.05, 0.1, 6.8), size=1, parent=w)
        out['walls'].append((s, w))
    use(add('cube', 'D9772A', (0, 6.6, 2.6), scale=(9, 0.1, 5.4), size=1, parent=r), fm)
    add('cube', '8A4418', (0, 0, 4.98), scale=(0.16, 13.4, 0.16), size=1, parent=r)                     # ridge seam
    add('cylinder', 'B9C0CA', (0, 6.3, 2.5), radius=0.07, depth=5, vertices=6, parent=r, rough=0.3)
    add('cylinder', '2F5FA8', (0.2, -1.3, 0.5), rot=(PI / 2, 0, 0), scale=(1.25, 0.85, 1.0), radius=0.62, depth=2.5, vertices=8, parent=r)   # sleeping bag
    add('ico_sphere', '2F5FA8', (0.2, -2.55, 0.5), scale=(1.25, 0.8, 0.85), radius=0.62, subdivisions=1, parent=r)
    add('cube', '3A6FC0', (0.2, 0.6, 0.3), scale=(1.5, 1.1, 0.3), size=1, parent=r)                     # the bag's hood, under his head
    add('ico_sphere', '6A2A2A', (2.9, 4.6, 0.8), scale=(1.0, 0.8, 1.2), radius=0.8, subdivisions=1, parent=r)   # a rucksack
    add('cylinder', 'FF7A1A', (-2.9, 4.8, 0.7), radius=0.24, depth=1.4, vertices=6, parent=r, rough=0.4)      # an oxygen bottle
    add('cylinder', 'D8DCE4', (-3.4, 4.5, 0.7), radius=0.24, depth=1.4, vertices=6, parent=r, rough=0.4)
    add('cylinder', '3A3F4C', (2.6, 2.2, 0.25), radius=0.3, depth=0.5, vertices=8, parent=r)                  # a small lantern
    out['lampm'] = lm = own_mat('lantern', 'FFD08A', 0.5, 6.0)
    use(add('cylinder', 'FFD08A', (2.6, 2.2, 0.62), radius=0.2, depth=0.3, vertices=8, parent=r), lm)
    out['lamp'] = light((2.6, 2.0, 1.2), 120, 'FFC27A', kind='POINT', parent=r)
    out['day'] = light((0, -1, 4.3), 0, 'FFB070', 4.0, kind='AREA', parent=r)
    return out


# ---------------------------------------------------------------- the glacier valley
def set_cwm(r):
    out = {}
    add('cube', 'CAD8EA', (0, 0, -0.5), scale=(1400, 1400, 1), size=1, parent=r)
    for j in range(7):                                                                                # the valley walls
        for s in (-1, 1):
            peak(r, s * (120 + 30 * rnd(j, s + 2)), -160 + j * 85, 95, 150 + 70 * rnd(j, s + 5), cap=0.35 + 0.2 * rnd(j, 3), spin=j + s)
    peak(r, 0, 520, 220, 260, cap=0.5, spin=0.3)                                                      # the head of the valley
    for j in range(44):                                                                                # ice towers
        a = rnd(j, 1) * 6.28
        d = 15 + 42 * rnd(j, 2)
        x, y = d * math.cos(a), 10 + d * math.sin(a) * 0.9
        if abs(x) < 9 and -14 < y < 30:
            continue
        hgt = 3 + 9 * rnd(j, 3)
        add('cube', 'A9D4EE' if j % 2 else 'D4E8F6', (x, y, hgt / 2 - 0.3), rot=(0.25 * (rnd(j, 4) - 0.5), 0.25 * (rnd(j, 5) - 0.5), rnd(j, 6) * 3),
            scale=(2 + 3 * rnd(j, 7), 2 + 3 * rnd(j, 8), hgt), size=1, parent=r, rough=0.35)
    for j, (y, w) in enumerate(((-17, 3.0), (44, 2.2))):                                               # crevasses
        add('cube', '24406A', (4 * j, y, 0.02), rot=(0, 0, 0.12 - 0.3 * j), scale=(90, w, 0.05), size=1, parent=r)
    for j in range(4):                                                                                # marker wands round the landing place
        x, y = (-5.5, 5.5)[j % 2], (7.0, 19.0)[j // 2]
        add('cylinder', '2A2F3A', (x, y, 1.0), radius=0.05, depth=2.0, vertices=5, parent=r)
        add('cube', 'FF7A1A', (x + 0.3, y, 1.8), scale=(0.6, 0.03, 0.4), size=1, parent=r, emit=0.6)
    out['heli'] = h = mov(empty(FAR, r))                                                              # a generic small helicopter, nose to -Y
    OL = '56633A'
    add('ico_sphere', OL, (0, 0.3, 2.3), scale=(1.5, 2.7, 1.5), radius=1, subdivisions=2, parent=h, rough=0.6)
    add('ico_sphere', '16202C', (0, -1.25, 2.45), scale=(1.32, 1.6, 1.2), radius=1, subdivisions=2, parent=h, rough=0.15)
    add('cylinder', OL, (0, 5.2, 2.75), rot=(PI / 2, 0, 0), radius=0.3, depth=6.0, vertices=6, parent=h)
    add('cylinder', 'FF7A1A', (0, 4.0, 2.75), rot=(PI / 2, 0, 0), radius=0.33, depth=0.4, vertices=6, parent=h)
    add('cube', OL, (0, 8.0, 3.5), rot=(0.45, 0, 0), scale=(0.12, 1.1, 2.2), size=1, parent=h)
    add('cube', OL, (0, 7.6, 2.75), scale=(2.4, 0.7, 0.08), size=1, parent=h)
    add('cylinder', '2A2F3A', (0, 0.3, 4.0), radius=0.16, depth=0.9, vertices=6, parent=h)
    for s in (-1, 1):
        add('cylinder', '22262E', (s * 1.35, 0.1, 0.12), rot=(PI / 2, 0, 0), radius=0.09, depth=5.0, vertices=5, parent=h)
        for y in (-1.0, 1.4):
            add('cube', '22262E', (s * 1.1, y, 0.7), rot=(0, s * 0.45, 0), scale=(0.1, 0.1, 1.4), size=1, parent=h)
    out['rotor'] = ro = mov(empty((0, 0.3, 4.5), h))
    for j in range(3):
        a = j * 2 * PI / 3
        add('cube', '1E2228', (3.0 * math.cos(a), 3.0 * math.sin(a), 0), rot=(0, 0, a), scale=(6.0, 0.42, 0.06), size=1, parent=ro)
    add('cylinder', 'C8D0DC', (0, 0, 0.02), radius=6.1, depth=0.02, vertices=20, parent=ro, alpha=0.1)
    out['trotor'] = tr = mov(empty((0.22, 8.25, 3.9), h))
    for j in range(2):
        add('cube', '1E2228', (0, 0, 0), rot=(j * PI / 2, 0, 0), scale=(0.05, 0.16, 2.0), size=1, parent=tr)
    return out


# ---------------------------------------------------------------- the house at dusk
def set_home(r):
    out = {}
    add('cube', '2E4A34', (0, 0, -0.2), scale=(500, 500, 0.4), size=1, parent=r)
    add('cube', 'B8AFA0', (0, -9, 0.02), scale=(3.0, 21, 0.06), size=1, parent=r)                       # the path to the door
    add('cube', '2A2C34', (0, -24, 0.02), scale=(500, 9, 0.06), size=1, parent=r)                       # the street
    add('cube', '9A5A44', (0, 9, 5), scale=(34, 12, 10), size=1, parent=r)                              # the house
    add('cube', '3E3436', (0, 8.4, 10.4), scale=(37, 14.5, 0.8), size=1, parent=r)
    add('cube', '5A4246', (0, 9, 12.2), scale=(24, 9, 3.0), size=1, parent=r)
    add('cube', '3E3436', (0, 9, 13.9), scale=(26, 10.5, 0.6), size=1, parent=r)
    add('cube', 'C8BFB0', (0, 1.6, 0.25), scale=(8, 3.0, 0.5), size=1, parent=r)                        # the porch
    add('cube', '3E3436', (0, 1.6, 7.0), scale=(9, 3.6, 0.4), size=1, parent=r)
    for s in (-1, 1):
        add('cube', 'E8E0D0', (s * 3.7, 0.4, 3.6), scale=(0.4, 0.4, 6.4), size=1, parent=r)
        add('cube', 'E8E0D0', (s * 1.55, 2.96, 3.0), scale=(0.3, 0.14, 5.4), size=1, parent=r)          # door frame
        for j in range(2):                                                                             # lit windows, two each side
            x = s * (7.5 + j * 6.5)
            add('cube', 'FFD890', (x, 2.97, 4.6), scale=(4.0, 0.1, 3.6), size=1, parent=r, emit=2.4)
            add('cube', 'E8E0D0', (x, 2.92, 4.6), scale=(0.16, 0.1, 3.6), size=1, parent=r)
            add('cube', 'E8E0D0', (x, 2.92, 4.6), scale=(4.0, 0.1, 0.16), size=1, parent=r)
            add('ico_sphere', '2A5236', (x, 1.9, 0.9), scale=(2.4, 1.0, 1.1), radius=1, subdivisions=1, parent=r)     # shrubs
    add('cube', 'E8E0D0', (0, 2.96, 5.75), scale=(3.4, 0.14, 0.3), size=1, parent=r)
    add('cube', 'FFDDA8', (0, 2.99, 3.0), scale=(2.8, 0.06, 5.2), size=1, parent=r, emit=1.8)           # the lit hall behind the door
    out['door'] = hinge = mov(empty((-1.4, 2.9, 0.5), r))
    add('cube', '6A3E2E', (1.4, 0, 2.55), scale=(2.8, 0.14, 5.1), size=1, parent=hinge)
    add('ico_sphere', 'FFC233', (2.5, -0.12, 2.5), radius=0.12, subdivisions=1, parent=hinge, rough=0.3)
    out['doorl'] = light((0, 1.4, 4.2), 0, 'FFD9A8', kind='POINT', parent=r)
    add('cube', 'FFE2B0', (2.6, 2.8, 5.6), scale=(0.4, 0.3, 0.6), size=1, parent=r, emit=10.0)          # porch lamp
    light((2.4, 1.6, 5.4), 350, 'FFD9A8', kind='POINT', parent=r)
    for x, y, hgt in ((-13, -7, 11), (15, -11, 9)):                                                    # two trees
        add('cylinder', '4A3828', (x, y, hgt / 2), radius=0.5, depth=hgt, vertices=6, parent=r)
        for j in range(3):
            add('ico_sphere', '2F5A3A' if j % 2 else '356A44', (x + 1.6 * (j - 1), y + 0.8 * (j % 2), hgt + 1.2 * j), radius=3.4 - 0.4 * j,
                subdivisions=1, parent=r)
    add('cube', '4A3828', (5.5, -18.5, 1.3), scale=(0.25, 0.25, 2.6), size=1, parent=r)                 # mailbox, no lettering
    add('cube', '8E96A4', (5.5, -18.5, 2.8), scale=(0.7, 1.3, 0.7), size=1, parent=r, rough=0.4)
    for j in range(7):                                                                                # a low hedge along the street
        add('ico_sphere', '2A5236', (-30 + j * 4.4 + (10 if j > 3 else 0), -18.5, 0.7), scale=(2.3, 1.0, 0.9), radius=1, subdivisions=1, parent=r)
    return out


# ---------------------------------------------------------------- the living room
def set_room(r):
    out = {}
    add('cube', '6A4A34', (0, 0, -0.1), scale=(18, 16, 0.2), size=1, parent=r)
    add('cube', '8A7C6C', (0, 8, 4.5), scale=(18, 0.3, 9), size=1, parent=r)
    add('cube', '7E7062', (-9, 0, 4.5), scale=(0.3, 16, 9), size=1, parent=r)
    add('cube', '7E7062', (9, 0, 4.5), scale=(0.3, 16, 9), size=1, parent=r)
    add('cube', '4A4038', (0, 0, 9.1), scale=(18, 16, 0.2), size=1, parent=r)
    add('cube', '5A4034', (0, 7.8, 0.35), scale=(18, 0.2, 0.7), size=1, parent=r)                       # skirting
    add('cube', '7A3E34', (1.5, 2.0, 0.02), scale=(9, 7, 0.06), size=1, parent=r)                       # rug
    out['panem'] = pm = own_mat('pane', 'CFE0FF', 0.5, 3.0)
    use(add('cube', 'CFE0FF', (3.6, 7.82, 4.6), scale=(4.6, 0.1, 4.6), size=1, parent=r), pm)           # the window
    for dx, dz, sx, sz in ((0, 0, 0.18, 4.6), (0, 0, 4.6, 0.18), (-2.4, 0, 0.3, 5.0), (2.4, 0, 0.3, 5.0), (0, 2.45, 5.1, 0.3), (0, -2.45, 5.4, 0.4)):
        add('cube', 'E8E0D0', (3.6 + dx, 7.72, 4.6 + dz), scale=(sx, 0.14, sz), size=1, parent=r)
    for s in (-1, 1):
        add('cube', 'B8683A', (3.6 + s * 3.1, 7.6, 4.5), scale=(1.1, 0.2, 6.0), size=1, parent=r)        # curtains
    out['win'] = light((3.6, 6.6, 4.8), 0, 'FFE2B8', 4.0, kind='AREA', parent=r)
    out['win'].rotation_euler = (-PI / 2, 0, 0)
    ch = empty((3.3, 4.2, 0), r, (0, 0, -0.35))                                                       # the armchair by the window
    add('cube', '5E6E58', (0, 0, 0.75), scale=(2.6, 2.4, 1.0), size=1, parent=ch)
    add('cube', '5E6E58', (0, 1.25, 2.3), scale=(2.6, 0.7, 3.0), size=1, parent=ch)
    for s in (-1, 1):
        add('cube', '4E5E4A', (s * 1.45, 0.1, 1.45), scale=(0.5, 2.4, 1.3), size=1, parent=ch)
    add('cube', '5A3E2C', (-7.6, 3.0, 1.1), scale=(2.0, 2.6, 2.2), size=1, parent=r)                    # the telephone table
    add('cube', 'E4DCCC', (-7.5, 3.0, 2.35), scale=(1.0, 1.3, 0.3), size=1, parent=r, rough=0.5)        # the telephone
    out['handset'] = mov(add('cube', 'E4DCCC', (-7.5, 3.0, 2.62), scale=(0.24, 0.8, 0.2), size=1, parent=r, rough=0.5))
    add('cylinder', '8E7A4A', (-7.8, 4.9, 1.0), radius=0.14, depth=2.0, vertices=6, parent=r)           # a floor lamp behind the table
    add('cylinder', '8E7A4A', (-7.8, 4.9, 3.2), radius=0.08, depth=6.0, vertices=6, parent=r)
    out['shadem'] = sm = own_mat('shade', 'FFD9A0', 0.6, 1.6)
    use(add('cone', 'FFD9A0', (-7.8, 4.9, 6.3), radius1=0.8, radius2=0.45, depth=0.9, vertices=8, parent=r), sm)
    out['lamp'] = light((-7.2, 4.4, 5.6), 0, 'FFC98A', kind='POINT', parent=r)
    out['top'] = light((0, 0, 8.2), 0, 'FFE8D0', kind='POINT', parent=r)
    add('cube', '5A3E2C', (8.3, 1.0, 3.5), scale=(1.2, 6.0, 7.0), size=1, parent=r)                     # bookshelf
    for row in range(4):
        for j in range(9):
            add('cube', ('7A3E34', '2F5FA8', 'C9A227', '3E6A4A', 'B8B0A0')[(j + row * 2) % 5], (7.75, -1.5 + j * 0.6, 1.25 + row * 1.55),
                scale=(0.5, 0.42, 1.0 + 0.25 * rnd(j, row)), size=1, parent=r)
    for j, (x, z, w, hh, c) in enumerate(((-3.2, 5.6, 2.2, 1.7, '6E8AA8'), (-0.6, 5.2, 1.5, 2.0, 'A88A6E'), (-3.0, 3.4, 1.4, 1.1, '8AA088'))):
        add('cube', '3A2E28', (x, 7.78, z), scale=(w + 0.3, 0.12, hh + 0.3), size=1, parent=r)          # framed pictures, blank colour fields
        add('cube', c, (x, 7.72, z), scale=(w, 0.1, hh), size=1, parent=r)
    return out


# ---------------------------------------------------------------- the cairn at the foot of the mountain
CAIRN = (2.6, 1.6)


def set_base(r):
    out = dict(flags=[])
    add('cube', '6E7482', (0, 0, -0.5), scale=(1400, 1400, 1), size=1, parent=r)
    for j in range(70):
        x, y = -40 + 80 * rnd(j, 1), -18 + 80 * rnd(j, 2)
        if abs(x + 1) < 2.2 and y < 30 or (abs(x - CAIRN[0]) < 2.5 and abs(y - CAIRN[1]) < 2.5):
            continue
        s = 0.3 + 1.2 * rnd(j, 3)
        add('ico_sphere', ('5A6070', '8A90A0', '474C5A')[j % 3], (x, y, 0.1), rot=(0, 0, rnd(j, 4) * 6), scale=(s * 1.3, s, s * 0.6), radius=1,
            subdivisions=1, parent=r)
    for j in range(12):
        add('ico_sphere', 'D6E0F0', (-36 + 72 * rnd(j, 5), -6 + 70 * rnd(j, 6), -0.1), scale=(3 + 4 * rnd(j, 7), 2 + 2 * rnd(j, 8), 0.3), radius=1,
            subdivisions=1, parent=r)
    add('cube', '8E949E', (-1, 16, 0.03), rot=(0, 0, 0.03), scale=(2.4, 44, 0.06), size=1, parent=r)     # the trail
    add('cube', 'C4D6EA', (-14, 190, 0.2), rot=(0, 0, 0.08), scale=(70, 300, 0.5), size=1, parent=r)     # the glacier
    peak(r, -20, 420, 260, 300, cap=0.5, spin=0.5)                                                    # the mountain
    peak(r, -300, 330, 200, 190, cap=0.4, spin=1.2)
    peak(r, 280, 350, 210, 210, cap=0.45, spin=0.1)
    peak(r, 430, 120, 180, 150, cap=0.4, spin=0.8)
    peak(r, -430, 90, 170, 140, cap=0.4, spin=1.7)
    for j, (x, y, c) in enumerate(((-17, 30, YEL), (-22, 36, BLUE), (-12, 39, 'FF7A1A'), (14, 44, GRN))):
        dome(r, x, y, c, 0.4 * j, 0.9)
    cx, cy = CAIRN
    for j in range(9):                                                                                # the cairn: flat stones stacked
        s = 1.7 - 0.13 * j
        add('ico_sphere', ('5A6070', '747A8A', '474C5A')[j % 3], (cx + 0.12 * (rnd(j, 9) - 0.5), cy + 0.12 * (rnd(j, 10) - 0.5), 0.3 + 0.48 * j),
            rot=(0, 0, rnd(j, 11) * 6), scale=(s, s * 0.85, 0.33), radius=1, subdivisions=1, parent=r)
    add('cylinder', '4A3828', (cx, cy, 6.3), radius=0.07, depth=4.2, vertices=5, parent=r)
    top = (cx, cy, 8.3)
    cols = (BLUE, 'F4F2EA', RED, GRN, YEL)
    for si, (ex, ey) in enumerate(((-13, 6), (12, 13), (-6, 18), (10, -7))):                            # strings of plain coloured flags
        for j in range(13):
            u = (j + 1) / 14
            x, y = lerp(top[0], ex, u), lerp(top[1], ey, u)
            z = lerp(top[2], 0.6, u) - 1.4 * math.sin(PI * u)
            yaw = math.atan2(ey - top[1], ex - top[0])
            f = add('cube', cols[(j + si) % 5], (x, y, z - 0.3), rot=(0, 0, yaw), scale=(0.62, 0.03, 0.5), size=1, parent=r, emit=0.15)
            out['flags'].append((f, yaw, j * 0.7 + si))
        line = add('cylinder', '22262E', (0, 0, 0), radius=0.5, depth=1, vertices=4, parent=r)
        seg(line, top, (ex, ey, 0.5), 0.02)
    return out


# ---------------------------------------------------------------- cast
def climber_head(skin, suit, hair='3A2E28'):
    """A climber's head in a down hood. Goggles, oxygen mask, ice and frost are separate pieces that shots switch on."""
    def fn(head):
        add('ico_sphere', skin, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
        add('ico_sphere', suit, (0, 0.07, 0.07), scale=(1.0, 1.0, 1.08), radius=0.335, subdivisions=1, parent=head)
        add('torus', suit, (0, -0.1, 0.03), rot=(PI / 2, 0, 0), major_radius=0.3, minor_radius=0.07, major_segments=8, minor_segments=4, parent=head)
        eyes, brows = [], []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '1A222E', (s * 0.105, -0.28, 0.035), scale=(0.042, 0.02, 0.046), size=1, parent=head)
            brows.append(add('cube', hair, (s * 0.105, -0.27, 0.125), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.026), size=1, parent=head))
        add('cube', 'C08E6E', (0, -0.285, -0.04), scale=(0.05, 0.05, 0.08), size=1, parent=head)
        jaw = empty((0, -0.2, -0.13), head)
        add('cube', '6A2A2E', (0, -0.07, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
        gog = [add('cube', '10141C', (0, -0.275, 0.05), scale=(0.44, 0.07, 0.16), size=1, parent=head, rough=0.15),
               add('cube', 'FF7A1A', (0, -0.31, 0.05), scale=(0.36, 0.02, 0.1), size=1, parent=head, rough=0.2, emit=0.5),
               add('torus', '22262E', (0, 0.02, 0.06), major_radius=0.34, minor_radius=0.025, major_segments=8, minor_segments=3, parent=head)]
        mask = [add('cube', '8A90A0', (0, -0.3, -0.1), scale=(0.2, 0.14, 0.17), size=1, parent=head, rough=0.5),
                add('cylinder', '3A3F4C', (0.1, -0.26, -0.26), rot=(0.4, 0, 0), radius=0.035, depth=0.3, vertices=5, parent=head)]
        ice = []
        for j, (x, y, z, sc) in enumerate(((-0.13, -0.25, 0.2, 0.07), (0.12, -0.25, 0.21, 0.06), (0, -0.2, 0.3, 0.12), (-0.24, -0.16, 0.2, 0.1),
                                           (0.25, -0.15, 0.17, 0.09), (-0.2, -0.2, -0.12, 0.08), (0.2, -0.2, -0.14, 0.09), (0.02, -0.26, -0.2, 0.09),
                                           (-0.28, -0.1, 0.0, 0.08), (0.29, -0.1, 0.02, 0.07))):
            ice.append(add('ico_sphere', 'EEF4FC', (x, y, z), scale=(1, 0.6, 0.8), radius=sc * 0.7, subdivisions=1, parent=head, rough=0.25))
        frost = [add('cube', 'D8E2F2', (0, -0.292, -0.04), scale=(0.062, 0.05, 0.09), size=1, parent=head),
                 add('cube', 'D8E2F2', (-0.17, -0.24, -0.05), scale=(0.1, 0.03, 0.08), size=1, parent=head),
                 add('cube', 'D8E2F2', (0.17, -0.24, -0.05), scale=(0.1, 0.03, 0.08), size=1, parent=head)]
        for grp_ in (gog, mask, ice, frost):
            vis(grp_, False)
        return dict(jaw=jaw, eyes=eyes, brows=brows, gog=gog, mask=mask, ice=ice, frost=frost)
    return fn


def home_head(skin, hair, kind):
    def fn(head):
        add('ico_sphere', skin, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
        add('ico_sphere', hair, (0, 0.05, 0.1), scale=(0.96, 1, 1.0), radius=0.3, subdivisions=1, parent=head)
        eyes, brows = [], []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '1A222E', (s * 0.105, -0.28, 0.035), scale=(0.042, 0.02, 0.046), size=1, parent=head)
            brows.append(add('cube', hair, (s * 0.105, -0.27, 0.125), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.026), size=1, parent=head))
        jaw = empty((0, -0.2, -0.13), head)
        add('cube', '6A2A2E', (0, -0.07, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
        if kind == 'wife':
            add('ico_sphere', hair, (0, 0.12, -0.12), scale=(1.05, 0.8, 1.3), radius=0.3, subdivisions=1, parent=head)       # shoulder-length hair
            add('cube', 'C08E6E', (0, -0.285, -0.04), scale=(0.045, 0.045, 0.07), size=1, parent=head)
        else:
            add('cube', 'F4F2EA', (0, -0.285, -0.03), scale=(0.16, 0.06, 0.14), size=1, parent=head)                         # a dressing over the nose
            add('cube', 'F4F2EA', (0, -0.275, 0.0), scale=(0.5, 0.03, 0.035), size=1, parent=head)
        return dict(jaw=jaw, eyes=eyes, brows=brows)
    return fn


def build():
    sc = bpy.context.scene
    _MOV.clear()
    S = dict(colls={})
    for name, fn in (('col', set_col), ('ridge', set_ridge), ('tent', set_tent), ('cwm', set_cwm), ('home', set_home), ('room', set_room),
                     ('base', set_base)):
        S['colls'][name], out = group(name, fn)
        S[name] = out
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['beck'] = bk = K.Rig(dict(top=RED, pants=RED, hand='1E2026', boot='E3B02A'), climber_head(SKIN, RED))
    S['rhm'] = own_mat('righthand', '1E2026', 0.8)
    use(bk.hands[0], S['rhm'])                 # his own right hand: a rig facing -Y has its right at -x (index 0, pose key aL)
    add('cube', '1E2026', (0, 0.3, 0.6), scale=(0.56, 0.3, 0.8), size=1, parent=bk.body)                             # his pack
    add('cylinder', 'FF7A1A', (0.12, 0.48, 0.7), radius=0.1, depth=0.9, vertices=6, parent=bk.body, rough=0.4)
    S['crust'] = []
    for j in range(16):                                                                                            # the crust of ice over him
        S['crust'].append(add('ico_sphere', 'EEF4FC', (-0.34 + 0.68 * rnd(j, 1), -0.36 - 0.03 * rnd(j, 2), -0.1 + 1.25 * rnd(j, 3)),
                              scale=(1.2, 0.35, 1.0), radius=0.1 + 0.09 * rnd(j, 4), subdivisions=1, parent=bk.body, rough=0.25))
    for i in (0, 1):
        for j in range(3):
            S['crust'].append(add('ico_sphere', 'EEF4FC', (0, -0.1, -0.1 - 0.16 * j), scale=(1.1, 0.5, 1.0), radius=0.09, subdivisions=1,
                                  parent=bk.kn[i], rough=0.25))
    for nm, col, boot in (('c1', BLUE, '22262E'), ('c2', YEL, '8A2A2A'), ('c3', GRN, 'D8DCE4')):
        S[nm] = rg = K.Rig(dict(top=col, pants=col, hand='1E2026', boot=boot), climber_head('D6A888', col))
        add('cube', '2A2F3A', (0, 0.3, 0.6), scale=(0.56, 0.3, 0.8), size=1, parent=rg.body)
    S['wife'] = wf = K.Rig(dict(top='7A4E8A', pants='7A4E8A', hand='E2B694', boot='3A2E34'), home_head('E2B694', '6A4A32', 'wife'))
    add('cone', '7A4E8A', (0, 0, -0.45), radius1=0.5, radius2=0.32, depth=1.1, vertices=8, parent=wf.body)             # her skirt
    S['beckh'] = bh = K.Rig(dict(top='4E6A8A', fore='F4F2EA', pants='3A3F4C', hand='F4F2EA', boot='2A2420'), home_head(SKIN, '6E6258', 'beck'))
    bh.el[0].scale = (1, 1, 0.5)                                                                                    # his right arm now ends below the elbow
    S['cast'] = [S['rook'], bk, S['c1'], S['c2'], S['c3'], wf, bh]
    S['fea'] = [mov(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(3)]
    S['coin'] = mov(add('cylinder', 'FFC233', FAR, radius=0.11, depth=0.03, vertices=8, rough=0.25, emit=1.2))
    S['biner'] = bn = mov(empty(FAR))                                                                              # the shiny thing: a climber's snap-link
    add('torus', 'E8ECF4', (0, 0, 0), scale=(0.7, 1.15, 1), major_radius=0.16, minor_radius=0.035, major_segments=10, minor_segments=4, parent=bn,
        rough=0.12, emit=2.2)
    S['rope'] = mov(add('cylinder', 'FF7A1A', FAR, radius=0.5, depth=1, vertices=5))
    S['puff'] = mov(add('ico_sphere', 'F4F8FF', FAR, radius=0.14, subdivisions=1, alpha=0.55, emit=0.4))
    S['hand'] = K.Hand('C2CEE2', RED, 1.0)                                                                          # his frozen right hand, close up
    for j, (x, y, sc_) in enumerate(((-0.1, -0.42, 0.05), (0.04, -0.47, 0.045), (0.1, -0.3, 0.05), (-0.05, -0.12, 0.07), (0.1, 0.0, 0.06),
                                     (-0.11, -0.28, 0.04), (0.0, 0.1, 0.05))):
        add('ico_sphere', 'F4F8FF', (x, y, 0.06), scale=(1, 1, 0.5), radius=sc_, subdivisions=1, parent=S['hand'].root, rough=0.15, emit=0.3)
    mov(S['hand'].root)
    S['glow'] = light(FAR, 0, 'FFE2B0', kind='POINT')
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
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


def cam(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='DCE4F4'):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    dx, dy, dz = look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    h = math.hypot(dx, dy) + 1e-6
    S['fill'].location = (pos[0] - dy / h * 0.3 * d, pos[1] + dx / h * 0.3 * d, pos[2] + 0.3 * d)
    S['fill'].data.energy = S['fillk'] * fill * min(d, 14) ** 2
    S['fill'].data.size = max(2.0, 0.3 * d)
    S['fill'].data.color = K.hexc(fcol)[:3]


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
    for o, par, loc, rot, scl in _MOV:
        o.parent = par
        o.location, o.rotation_euler, o.scale = loc, rot, scl
    for who in ('beck', 'c1', 'c2', 'c3'):
        x = S[who].extra
        vis(x['gog'], who != 'beck')
        vis(x['mask'], False)
        vis(x['ice'], False)
        vis(x['frost'], False)
    vis(S['crust'], False)
    tint(S['rhm'], '1E2026', 0.0)
    S['col']['camp'].data.energy = 0
    T = S['tent']
    tint(T['fabm'], 'D9772A', 0.3)
    tint(T['lampm'], 'FFD08A', 6.0)
    T['lamp'].data.energy = 120
    T['day'].data.energy = 0
    for s, w in T['walls']:
        w.rotation_euler = (0, -s * 0.72, 0)
    S['home']['doorl'].data.energy = 0
    R = S['room']
    tint(R['panem'], 'CFE0FF', 3.0)
    tint(R['shadem'], 'FFD9A0', 1.6)
    R['win'].data.energy = 0
    R['lamp'].data.energy = 0
    R['top'].data.energy = 0
    S['glow'].location = FAR
    S['glow'].data.energy = 0
    S['glow'].data.color = K.hexc('FFE2B0')[:3]
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['face'] = dict(rook='calm', beck='calm', c1='calm', c2='calm', c3='calm', wife='calm', beckh='calm')
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
    S['jaw'] = dict(beck=0.0, c1=0.0, c2=0.0, c3=0.0, wife=0.0, beckh=0.0)
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.41) % 1 < 0.035
    ez = dict(calm=0.07, deadpan=0.05, shocked=0.13, sad=0.055, warm=0.06, shut=0.012).get(e, 0.07)
    tilt = dict(deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], ease(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + (0.12 if e == 'deadpan' else 0.0) + tip * 0.35, 1.35, off), lerp(0.07, 0.0, off), 0)
    r['hat'].location = (0.0, lerp(0.0, -0.5, off), lerp(0.27 + (0.2 if e == 'shocked' else 0.0) + tip * 0.1, -0.92, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, who in enumerate(('beck', 'c1', 'c2', 'c3', 'wife', 'beckh')):
        x = S[who].extra
        k = dict(calm=1.0, wide=1.7, shut=0.07, tired=0.45, warm=0.85, squint=0.4, sad=0.6).get(S['face'][who], 1.0)
        bl = (t * 0.33 + 0.27 * j) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for br in x['brows']:
            br.location.z = 0.125 + (0.03 if S['face'][who] == 'wide' else -0.012 if S['face'][who] in ('sad', 'tired', 'squint') else 0.0)
        x['jaw'].rotation_euler = (S['jaw'][who], 0, 0)


# ---------------------------------------------------------------- helpers for the shots
def env(S, name, skyc='000000', sun=0.0, sunc='FFFFFF', sdir=(-0.4, -0.6, 0.7), fk=2.6, skyk=1.0):
    A = show(S, name)
    sky(S, skyc, skyk)
    S['suntgt'].location = A(0, 0, 0)
    S['sun'].location = A(sdir[0] * 400, sdir[1] * 400, sdir[2] * 400)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(sunc)[:3]
    S['fillk'] = fk
    return A


def feather(S, pos, lt, t0=0.0, n=2):
    for i in range(n):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def hat_hold(**over):
    d = dict(aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.22, 0.0))
    d.update(over)
    return P('stand', **d)


ALARM = dict(aL=(0.7, 1.15, 1.5, -0.7), aR=(0.7, 1.15, 1.5, -0.7), head=(-0.15, 0.0), lean=-0.12, lL=(-0.12, 0.0), lR=(-0.12, 0.0))
LYING = P('stand', aR=(0.12, 0.4, 0.25), aL=(0.95, 0.15, 1.25, 0.4), lL=(0.05, 0.05), lR=(-0.03, 0.12), head=(-0.05, -0.12))
LOW = P('stand', aR=(0.12, 0.4, 0.25), aL=(0.3, 0.55, 0.7, 0.3), lL=(0.05, 0.05), lR=(-0.03, 0.12), head=(-0.05, 0.0))
KNEEL = P('stand', lL=(0.25, 1.55), lR=(1.35, 1.5), lift=-0.78, lean=0.45, aL=(0.5, 0.1, 0.6), aR=(1.0, 0.0, 0.5), head=(0.35, 0.0))
BRACE = P('stand', lean=0.38, aL=(0.9, 0.25, 1.5, 0.6), aR=(0.9, 0.25, 1.5, 0.6), head=(0.3, 0.0), lL=(0.3, 0.2), lR=(-0.25, 0.3))


def wind_walk(t, sp=1.2):
    """Bent double into the wind."""
    w = walk(t, sp)
    w['lean'] = 0.42
    w['head'] = (0.3, 0.0)
    w['aL'] = (0.8, 0.3, 1.5, 0.6)
    return w


def col(S, mode):
    """The saddle at different hours."""
    if mode == 'grey':        # daylight, wind, flying snow
        A = env(S, 'col', '93A6C6', sun=1.5, sunc='E8F0FF', sdir=(-0.5, -0.5, 0.6), fk=1.6, skyk=0.9)
    elif mode == 'dusk':      # the storm arriving
        A = env(S, 'col', '465474', sun=0.5, sunc='AFC0E8', sdir=(-0.6, -0.3, 0.5), fk=3.2, skyk=0.8)
    elif mode == 'night':
        A = env(S, 'col', '0C1430', sun=0.35, sunc='8FA8F0', sdir=(0.5, -0.3, 0.8), fk=5.0, skyk=1.0)
        S['col']['camp'].data.energy = 9000
    elif mode == 'dawn':
        A = env(S, 'col', 'C79AA6', sun=2.0, sunc='FFB890', sdir=(0.85, -0.35, 0.16), fk=1.5, skyk=0.75)
    else:                     # afternoon
        A = env(S, 'col', '6F9CDC', sun=2.4, sunc='FFF0D8', sdir=(-0.7, -0.45, 0.45), fk=1.3, skyk=1.0)
    return A


def lie(S, A, who='beck', crust=1.0, face='shut', pose=None, bare=True, yaw=0.0, pos=SPOT):
    """Lay a climber on his back in the snow, feet at pos, head towards +Y."""
    rig = S[who]
    rig.place(A(pos[0], pos[1], 0.4), yaw, -PI / 2)
    rig.apply(pose or LYING)
    S['face'][who] = face
    x = rig.extra
    vis(x['gog'], False)
    if who == 'beck':
        vis(x['ice'], crust > 0.3)
        vis(x['frost'], True)
        n = int(len(S['crust']) * crust)
        vis(S['crust'][:n], True)
        if bare:
            tint(S['rhm'], 'C2CEE2', 0.05)


def headpos(pos=SPOT):
    return (pos[0], pos[1] + 2.42, 0.42)


# ---------------------------------------------------------------- the hook: fifteen hours in the snow
def ice_body(S, k, t, lt):
    A = col(S, 'grey')
    lie(S, A)
    e = ease(k)
    cam(S, A(lerp(2.3, 1.4, e), lerp(-3.8, -1.5, e), lerp(1.0, 1.9, e)), A(0.0, 1.5, 0.55), 26, fcol='E4ECFF')


def col_wide(S, k, t, lt):
    A = col(S, 'grey')
    lie(S, A)
    rp_ = (2.0, 1.2, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (0, 2.0, 0)))
    S['rook'].apply(P('hat', lean=0.22, head=(0.3, 0.0), lL=(0.25, 0.1), lR=(-0.2, 0.2)))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-9.5, -7.5, k), lerp(-15, -12.5, k), lerp(8.5, 7.0, k)), A(1.0, 3.0, 1.2), 24, fcol='E4ECFF')


def left_walk(S, k, t, lt):
    A = col(S, 'grey')
    lie(S, A)
    d = math.hypot(*CAMP)
    ux, uy = CAMP[0] / d, CAMP[1] / d
    for j, who in enumerate(('c1', 'c2', 'c3')):
        s = 5.0 + j * 2.3 + lt * 1.5
        p = (1.5 + ux * s + (j - 1) * 0.5 * uy, 2.0 + uy * s - (j - 1) * 0.5 * ux, 0)
        S[who].place(A(*p), facing(p, (p[0] + ux, p[1] + uy, 0)))
        S[who].apply(wind_walk(lt + j * 0.3, 1.3))
    cam(S, A(lerp(-2.6, -2.2, k), lerp(-3.8, -3.2, k), lerp(1.3, 1.6, k)), A(3.0, 5.0, 1.6), 24, fcol='E4ECFF')


def eyes_open(S, k, t, lt):
    v2 = S['prm'].get('v') == 2
    A = col(S, 'day' if v2 else 'grey')
    op = k > (0.4 if v2 else 0.5)
    arm = P('stand', aR=(0.12, 0.4, 0.25), aL=(1.25, 0.25, 1.35, 0.3), lL=(0.05, 0.05), lR=(-0.03, 0.12), head=(0.2, -0.1))
    lie(S, A, face='calm' if op else 'shut', pose=blend(LOW, arm, (k - 0.45) * 2.5) if v2 else LOW)
    hp = headpos()
    if v2:
        cam(S, A(lerp(1.9, 1.5, k), lerp(0.5, 0.8, k), lerp(2.2, 1.9, k)), A(hp[0] - 0.15, hp[1] - 0.45, hp[2] + 0.1), 40, fcol='FFF0DC')
    else:
        cam(S, A(lerp(0.45, 0.3, k), lerp(0.9, 1.25, k), lerp(3.1, 2.6, k)), A(hp[0], hp[1] - 0.05, hp[2]), 50, fcol='E4ECFF')


def rook_jolt(S, k, t, lt):
    A = col(S, 'grey')
    lie(S, A, face='wide')
    rp_ = (2.1, 1.6, 0.0)
    pop = ease(lt / 0.14)
    S['rook'].place(A(*rp_), facing(rp_, (-0.4, -1.2, 0)))
    S['rook'].apply(blend(P('hat', lean=0.2), P('stand', **ALARM), pop))
    S['face']['rook'] = 'shocked' if pop > 0.3 else 'deadpan'
    feather(S, A(rp_[0] + 0.3, rp_[1] - 0.3, 3.3), lt, 0.08)
    cam(S, A(lerp(-0.9, -0.5, k), lerp(-2.4, -1.9, k), 1.0), A(1.7, 1.5, 2.55), 28, fcol='E4ECFF')


# ---------------------------------------------------------------- the cairn (Rook's start and sign-off)
def base(S, dawn=False):
    if dawn:
        A = env(S, 'base', 'D8A890', sun=2.0, sunc='FFC098', sdir=(0.8, -0.4, 0.22), fk=2.4, skyk=0.8)
    else:
        A = env(S, 'base', '6E86B8', sun=1.4, sunc='DCE6FF', sdir=(-0.6, -0.5, 0.5), fk=3.2, skyk=0.8)
    return A


def flutter(S, t):
    for f, yaw, ph in S['base']['flags']:
        f.rotation_euler = (0.25 * math.sin(t * 9 + ph), 0.2 * math.sin(t * 7 + ph * 1.3), yaw + 0.3 * math.sin(t * 8 + ph))


def rook_cairn(S, k, t, lt):
    A = base(S)
    flutter(S, t)
    S['rook'].place(A(-0.8, -1.5, 0), 0.3)
    S['rook'].apply(P('cross', head=(0.05, 0.4 * math.sin(lt * 9))))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.6
    cam(S, A(lerp(1.6, 1.1, k), lerp(-7.4, -6.4, k), 1.7), A(0.2, -1.0, 2.75), 28, fcol='FFE4C8')


def rook_go(S, k, t, lt):
    A = base(S)
    flutter(S, t)
    y = lerp(3.0, 7.5, k)
    S['rook'].place(A(-1.0, y, 0), PI)
    pop = ease(lt / 0.18) * (1 - ease((lt - 0.22) / 0.18))
    S['rook'].apply(blend(walk(lt, 1.9), P('stand', aL=(0.9, 0.5, 2.3, 0.6), aR=(0.9, 0.5, 2.3, 0.6)), pop))
    cam(S, A(lerp(-3.4, -2.8, k), lerp(-3.6, -1.6, k), 1.1), A(-1.2, 12, 4.4), 24, fcol='DCE6FF')


def rook_wrong(S, k, t, lt):
    A = base(S, dawn=True)
    flutter(S, t)
    S['rook'].place(A(-0.6, -1.6, 0), -0.15)
    S['hat_off'] = ease(lt / 0.35)
    S['rook'].apply(blend(P('stand'), hat_hold(), lt / 0.35))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(1.3, 0.8, k), lerp(-6.4, -5.6, k), 2.7), A(-0.5, -1.6, 2.55), 42, fcol='FFE0D0')


def signoff(S, k, t, lt):
    A = base(S, dawn=True)
    flutter(S, t)
    rp_ = (0.5, 0.7, 0.0)
    S['rook'].place(A(*rp_), 0.45)
    grab = ease((lt - 0.12) / 0.25)
    away = ease((lt - 0.72) / 0.3)
    S['rook'].apply(blend(blend(P('stand'), P('stand', aR=(0.9, 1.0, 0.4), head=(0.1, 0.5)), grab), P('hat'), away))
    S['hat_tip'] = away
    S['face']['rook'] = 'warm' if away < 0.5 else 'deadpan'
    n = S['biner']
    top = A(CAIRN[0] - 1.25, CAIRN[1] - 0.75, 3.45)
    hand = A(1.2, 0.35, 2.7)
    u = ease((lt - 0.28) / 0.3)
    n.location = tuple(top[i] + (hand[i] - top[i]) * u for i in range(3))
    n.location.z += 0.45 * math.sin(PI * u)
    n.rotation_euler = (PI / 2 + lt * 5 * u, lt * 4 * u, 0.4)
    if lt > 0.72:
        n.location = FAR
    cam(S, A(lerp(-0.2, 0.4, k), lerp(-7.4, -6.0, k), 2.3), A(1.3, 0.9, 2.75), 32, fcol='FFE0D0')


# ---------------------------------------------------------------- 10 May 1996, the ridge
def ridge(S, mode='dawn'):
    if mode == 'dawn':
        A = env(S, 'ridge', '8FA6D8', sun=2.2, sunc='FFD0A0', sdir=(0.8, -0.4, 0.25), fk=1.5, skyk=0.9)
    elif mode == 'noon':
        A = env(S, 'ridge', '5C8ADC', sun=2.6, sunc='FFFFFF', sdir=(-0.3, -0.5, 0.8), fk=1.3, skyk=1.0)
    else:                      # the weather turning
        A = env(S, 'ridge', '6A7896', sun=1.2, sunc='D8E0F4', sdir=(-0.7, -0.3, 0.4), fk=2.2, skyk=0.8)
    return A


def climbers_up(S, A, lt, d0, who=('c1', 'c2', 'c3'), gap=4.0, x=0.0, sp=0.9):
    for j, w in enumerate(who):
        d = d0 + j * gap + lt * sp
        S[w].place(A(*rp(d, x + 0.4 * math.sin(j * 2.1))), PI)
        S[w].apply(walk(lt + j * 0.37, 1.2))
        vis(S[w].extra['mask'], True)


def peak_wide(S, k, t, lt):
    A = ridge(S, 'dawn')
    climbers_up(S, A, lt, 34, gap=5.0)
    S['beck'].place(A(*rp(26 + lt * 0.9)), PI)
    S['beck'].apply(walk(lt, 1.2))
    cam(S, A(lerp(40, 34, k), lerp(-22, -14, k), lerp(26, 32, k)), A(0, lerp(50, 66, k), lerp(34, 50, k)), 26, fcol='FFE8D0')


def beck_climb(S, k, t, lt):
    A = ridge(S, 'dawn')
    d = 30 + lt * 0.9
    S['beck'].place(A(*rp(d)), PI)
    S['beck'].apply(walk(lt, 1.2))
    vis(S['beck'].extra['gog'], True)
    S['rook'].place(A(*rp(d - 2.6, -2.0)), PI)
    S['rook'].apply(walk(lt + 0.4, 1.2))
    S['face']['rook'] = 'deadpan'
    c = rp(d + 6.5, 1.6)
    b = rp(d - 0.6, -0.8)
    cam(S, A(c[0], c[1] - 0.6 * k, c[2] + 2.9), A(b[0], b[1], b[2] + 1.9), 30, fcol='FFE8D0')


def blur_pov(S, k, t, lt):
    A = ridge(S, 'dawn')
    climbers_up(S, A, lt, 9, gap=4.5, sp=1.3)
    cam(S, A(0.3 * math.sin(lt * 2.2), 1.5 + 0.5 * k, 2.6 + 0.1 * math.sin(lt * 5)), A(0, 26, 15), 26, fcol='FFE8D0')


def beck_blind(S, k, t, lt):
    A = ridge(S, 'dawn')
    S['beck'].place(A(-0.7, 0.0, 0), 0.1)
    w = 0.35 * math.sin(lt * 11)
    S['beck'].apply(P('stand', aR=(1.75, 0.15 + w, 1.45, 0.3), head=(0.0, 0.0)))
    S['face']['beck'] = 'squint'
    rp_ = (1.5, 0.4, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (-0.7, 0.0, 0)) - 0.5)
    S['rook'].apply(P('stand', aR=(1.6, -0.5 + 0.3 * math.sin(lt * 9), 0.5), head=(0.0, -0.5), lean=0.15))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(1.0, 0.5, k), lerp(-6.6, -5.9, k), 2.5), A(0.3, 0.0, 2.2), 32, fcol='FFE8D0')


def beck_wait(S, k, t, lt):
    A = env(S, 'ridge', '5C8ADC', sun=2.5, sunc='FFF4E0', sdir=(lerp(0.7, -0.7, k), -0.45, lerp(0.45, 0.75, math.sin(PI * k))), fk=1.4, skyk=1.0)
    S['beck'].place(A(-1.3, 1.0, 0.45), 0.0)
    S['beck'].apply(P('sit', head=(0.25, 0.25 * math.sin(lt * 2.5))))
    S['face']['beck'] = 'squint'
    S['rook'].place(A(1.5, 1.1, 0.4), -0.25)
    flip = (lt * 1.6) % 1
    S['rook'].apply(P('sit', aR=(0.9, 0.1, 1.2 + 0.4 * math.sin(PI * flip), 0.2), head=(0.1 - 0.25 * math.sin(PI * flip), 0.3)))
    S['face']['rook'] = 'deadpan'
    S['coin'].location = A(1.75, 0.35, 2.2 + 1.5 * math.sin(PI * flip))
    S['coin'].rotation_euler = (lt * 22, 0.3, 0)
    for j, w in enumerate(('c1', 'c3')):                                 # others pass on their way up, then down again
        d = 5.0 + ((lt * 2.4 + j * 5.5) % 12)
        S[w].place(A(*rp(d, 2.9 - j * 5.6)), PI)
        S[w].apply(walk(lt + j * 0.4, 1.4))
        vis(S[w].extra['mask'], True)
    cam(S, A(lerp(0.9, -0.5, k), lerp(-7.6, -7.0, k), 2.3), A(0.1, 1.0, 1.9), 30, fcol='FFF0DC')


# ---------------------------------------------------------------- the storm
def descend(S, k, t, lt):
    A = ridge(S, 'turn')
    S['ridge']['storm'].location = (lerp(-330, -250, k), 40, lerp(-110, -60, k))
    d = -44.0 - lt * 1.1
    g, b = rp(d - 3.0, 0.3), rp(d, -0.2)
    S['c3'].place(A(*g), 0.0)
    S['c3'].apply(walk(lt, 1.3))
    vis(S['c3'].extra['mask'], True)
    S['beck'].place(A(*b), 0.0)
    S['beck'].apply(blend(walk(lt + 0.3, 1.3), P('stand', aL=(0.9, 0.5, 0.6), aR=(0.9, 0.5, 0.6), lean=0.1), 0.5))
    S['face']['beck'] = 'squint'
    seg(S['rope'], A(g[0], g[1] + 0.3, g[2] + 1.45), A(b[0], b[1] - 0.35, b[2] + 1.45), 0.035)
    c = rp(d - 10.5, 2.6)
    cam(S, A(c[0], c[1], c[2] + 2.2 + 0.5 * k), A(b[0], b[1] - 1.2, b[2] + 2.0), 28, fcol='DCE4F4')


def blizzard_hit(S, k, t, lt):
    A = col(S, 'dusk')
    ox, oy = 40.0, -24.0                                               # out on the saddle, away from where he will fall
    for j, who in enumerate(('c3', 'beck', 'c1')):
        p = (ox - 1.5 + j * 0.8, oy + j * 2.1 - lt * 1.0, 0)
        S[who].place(A(*p), 0.1 * math.sin(lt * 3 + j))
        S[who].apply(wind_walk(lt + j * 0.3, 1.1))
    S['face']['beck'] = 'squint'
    rp_ = (ox + 2.5, oy - 0.4 - lt * 0.8, 0)
    grab = ease(lt / 0.25)
    S['rook'].place(A(*rp_), 0.25)
    S['rook'].apply(blend(walk(lt, 1.2), P('hat', lean=0.35, head=(0.3, 0.2), lL=(0.35, 0.1), lR=(-0.3, 0.3)), grab))
    S['hat_tip'] = 0.8 * grab
    S['face']['rook'] = 'shocked' if lt < 0.35 else 'deadpan'
    feather(S, A(rp_[0] + 0.3, rp_[1] - 0.3, 3.3), lt, 0.1, 3)
    cam(S, A(ox + lerp(3.4, 2.6, k), oy - lerp(8.5, 7.0, k), 1.5), A(ox + 0.6, oy + 1.0, 2.1), 26, fcol='C8D4F0')


def lost_group(S, k, t, lt):
    A = col(S, 'night')
    cx, cy = -16.0, -12.0
    for j, who in enumerate(('c1', 'c2', 'c3', 'beck')):
        a = j * 1.57 + lt * 0.5 * (1 if j % 2 else -1) + 0.4 * math.sin(lt * 1.3 + j)
        rr = 2.2 + 1.0 * math.sin(lt * 0.9 + j * 2)
        p = (cx + rr * math.cos(a), cy + rr * math.sin(a), 0)
        S[who].place(A(*p), a + (PI if j % 2 else 0) + 0.6 * math.sin(lt * 2 + j))
        S[who].apply(wind_walk(lt + j * 0.3, 1.0))
    S['glow'].location = A(cx, cy, 3.2)
    S['glow'].data.energy = 1500 + 500 * math.sin(lt * 9)
    S['glow'].data.color = K.hexc('CFE0FF')[:3]
    cam(S, A(cx + lerp(-3.0, 1.0, k), cy - lerp(13, 11, k), lerp(15, 12, k)), A(cx + 0.8, cy + 1.5, 0.5), 32, fcol='9FB4F0')


def rescuer(S, k, t, lt):
    A = col(S, 'night')
    lie(S, A, crust=0.4, bare=True)
    a_, b_ = (3.4, 2.6, 0.0), (2.4, 4.0, 0.0)
    up = ease((lt - 0.2) / 0.7)
    S['c2'].place(A(*b_), facing(b_, a_))
    S['c2'].apply(blend(P('sit', head=(0.4, 0.0)), P('stand', lean=0.3, aL=(1.0, 0.2, 0.5), head=(0.3, 0)), up))
    S['c2'].root.location.z += lerp(0.3, 0.0, up)
    S['c1'].place(A(*a_), facing(a_, b_))
    S['c1'].apply(blend(P('stand', lean=0.5, aL=(1.3, 0.1, 0.4), aR=(1.3, 0.1, 0.4), head=(-0.2, 0)), P('stand', lean=0.15, aR=(1.0, 0.1, 0.9)), up))
    S['glow'].location = A(a_[0] - 0.3, a_[1] - 0.5, 3.0)
    S['glow'].data.energy = 2600
    cam(S, A(lerp(-3.6, -2.8, k), lerp(-4.6, -4.0, k), lerp(1.2, 1.5, k)), A(1.6, 2.6, 1.5), 26, fcol='9FB4F0')


def rescuer_no(S, k, t, lt):
    A = col(S, 'night')
    lie(S, A, crust=0.5)
    d = math.hypot(*CAMP)
    ux, uy = CAMP[0] / d, CAMP[1] / d
    s = 4.0 + lt * 2.2
    for j, who in enumerate(('c1', 'c2')):
        p = (2.6 + ux * s + (j - 0.5) * 0.9 * uy, 3.2 + uy * s - (j - 0.5) * 0.9 * ux, 0)
        S[who].place(A(*p), facing(p, (p[0] + ux, p[1] + uy, 0)))
        S[who].apply(wind_walk(lt + j * 0.5, 1.2))
    S['glow'].location = A(2.6 + ux * (s + 1.5), 3.2 + uy * (s + 1.5), 2.8)
    S['glow'].data.energy = 2400
    rp_ = (-1.9, 1.6, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (CAMP[0], CAMP[1], 0)))
    S['rook'].apply(blend(P('stand'), P('stand', aR=(1.45, 0.1, 0.1), lean=0.2, lL=(0.4, 0.1), lR=(-0.3, 0.2), head=(-0.1, 0.0)), lt / 0.3))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-3.8, -4.4, k), lerp(-4.6, -5.2, k), lerp(2.0, 2.4, k)), A(1.2, 4.0, 1.7), 26, fcol='9FB4F0')


# ---------------------------------------------------------------- the morning after
def dawn_col(S, k, t, lt):
    A = col(S, 'dawn')
    lie(S, A)
    cam(S, A(lerp(6.5, 5.2, k), lerp(-8.5, -7.0, k), lerp(1.1, 2.3, k)), A(0.0, 1.6, 0.9), 28, fcol='FFD8C8')


def breath(S, A, lt):
    u = (lt * 0.9) % 1
    hp = headpos()
    S['puff'].location = A(hp[0] + 0.1 * u, hp[1] - 0.25, hp[2] + 0.35 + 0.8 * u)
    sc = 0.5 + 1.6 * u
    S['puff'].scale = (sc, sc, sc * (1 - 0.5 * u))


def doctor_kneel(S, k, t, lt):
    A = col(S, 'dawn')
    lie(S, A)
    breath(S, A, lt)
    dp_ = (1.7, 2.3, 0.0)
    dn = ease(lt / 0.5)
    S['c2'].place(A(*dp_), facing(dp_, (0, 2.5, 0)))
    S['c2'].apply(blend(P('stand', lean=0.3, head=(0.4, 0)), KNEEL, dn))
    vis(S['c2'].extra['gog'], False)
    S['face']['c2'] = 'sad'
    rp_ = (-2.0, 3.0, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (0, 2.2, 0)))
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.3, 0.0)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(2.2, -0.6, k), lerp(-5.6, -3.4, k), lerp(3.3, 2.0, k)), A(-0.1, 2.4, lerp(1.7, 1.4, k)), 30, fcol='FFD8C8')


def doctor_leave(S, k, t, lt):
    A = col(S, 'dawn')
    lie(S, A)
    go = ease((lt - 0.45) / 0.3)
    d = math.hypot(*CAMP)
    ux, uy = CAMP[0] / d, CAMP[1] / d
    s = max(0.0, lt - 0.5) * 1.5
    p = (1.9 + ux * s, 2.8 + uy * s, 0)
    yaw = lerp(facing(p, (0, 2.5, 0)), facing(p, (p[0] + ux, p[1] + uy, 0)), go)
    S['c2'].place(A(*p), yaw)
    S['c2'].apply(blend(P('stand', head=(0.5, 0.0), aL=(0.1, 0.1, 0.2), aR=(0.1, 0.1, 0.2)), walk(lt, 1.0), go * 0.8))
    S['c2'].head.rotation_euler = (0.45, 0, 0)
    vis(S['c2'].extra['gog'], False)
    S['face']['c2'] = 'sad'
    cam(S, A(lerp(-2.3, -2.8, k), lerp(-1.6, -2.2, k), lerp(1.3, 1.7, k)), A(1.6, 3.4, 1.9), 26, fcol='FFD8C8')


def room(S, night=True):
    R = S['room']
    A = env(S, 'room', '000000', fk=2.6 if night else 1.8)
    if night:
        tint(R['panem'], '1A2A50', 0.6)
        R['lamp'].data.energy = 900
        R['top'].data.energy = 60
    else:
        tint(R['panem'], 'FFE8C0', 2.6)
        tint(R['shadem'], 'C8B890', 0.0)
        R['win'].data.energy = 2600
        R['top'].data.energy = 500
    return A


def phone(S, k, t, lt):
    """The call: she crosses the room, lifts the receiver, listens, and her hand goes to her mouth."""
    A = room(S, True)
    wp = (-5.6, 3.0, 0.0)
    come = ease(lt / 0.4)
    lift = ease((lt - 0.4) / 0.25)
    drop = ease((lt - 1.05) / 0.4)
    S['wife'].place(A(lerp(-3.6, wp[0], come), lerp(1.8, wp[1], come), 0), lerp(facing(wp, (-7.6, 3.0, 0)), facing(wp, (-3.0, -2.0, 0)), 0.55 * lift + 0.35 * drop))
    listen = P('stand', aR=(0.5, 0.25, 2.35, 0.2), head=(0.05, 0.0))
    S['wife'].apply(blend(blend(blend(walk(lt, 1.6), P('stand', aR=(1.0, 0.0, 0.4)), come), listen, lift),
                          P('stand', aR=(0.25, 0.15, 0.5), aL=(0.85, -0.2, 2.2, 0.9), head=(0.4, 0.0)), drop))
    S['face']['wife'] = 'calm' if drop < 0.2 else 'sad' if drop < 0.8 else 'shut'
    hs = S['room']['handset']
    if lift <= 0:
        hs.rotation_euler = (0, 0.12 * math.sin(lt * 60), 0.05 * math.sin(lt * 47))            # ringing
    else:
        a, b, c = (-7.5, 3.0, 2.62), (-6.0, 3.14, 2.45), (-5.25, 2.55, 1.25)
        hs.location = tuple(lerp(lerp(a[i], b[i], lift), c[i], drop) for i in range(3))
        hs.rotation_euler = (lerp(lerp(0, 1.45, lift), 0.3, drop), 0, lerp(0.2, 2.0, drop))
    cam(S, A(lerp(-2.4, -3.3, k), lerp(-2.6, -1.4, k), lerp(3.0, 2.85, k)), A(lerp(-6.3, -5.7, k), 3.1, 2.5), lerp(32, 38, k), fcol='FFE4C8')


# ---------------------------------------------------------------- that afternoon
def frozen_hand(S, k, t, lt):
    A = col(S, 'day')
    lie(S, A, face='wide')
    h = S['hand']
    sh = 0.012 * math.sin(lt * 31)
    rise = ease(lt / 0.5)
    h.place(A(0.05 + sh, lerp(1.9, 1.45, rise), lerp(0.9, 1.72, rise)), (-2.29 + 0.15 * math.sin(lt * 2.0), 0.25 * (1 - rise), 0.12))
    h.grip(0.12)
    cam(S, A(0.0, lerp(2.5, 2.6, k), lerp(0.75, 0.7, k)), A(0.0, -3.0, 5.4), 30, fcol='FFF4E4')


def beck_rise(S, k, t, lt):
    A = col(S, 'day')
    up = ease(k * 1.15)
    bp = (0.0, 1.2, 0.0)
    S['beck'].place(A(*bp), facing(bp, (4.2, -5.0, 0)) + 0.15 * math.sin(lt * 5) * up, lerp(-0.25, 0.0, up))
    S['beck'].apply(blend(P('stand', lL=(0.3, 1.55), lR=(1.3, 1.5), lift=-0.8, lean=0.7, aR=(1.0, 0.3, 0.3), aL=(0.5, 0.2, 1.2), head=(0.3, 0)),
                          P('stand', lean=0.18, aR=(0.3, 0.5, 0.4), aL=(0.5, 0.2, 1.2), lL=(0.2, 0.2), lR=(-0.15, 0.15), head=(-0.1, 0.0)), up))
    x = S['beck'].extra
    vis(x['gog'], False)
    vis(x['frost'], True)
    vis(x['ice'][:5], True)
    vis(S['crust'][:5], True)
    tint(S['rhm'], 'C2CEE2', 0.05)
    S['face']['beck'] = 'tired'
    rp_ = (-2.7, 0.0, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (3.0, -4.0, 0)))
    S['rook'].apply(P('stand', **ALARM))
    S['face']['rook'] = 'shocked'
    feather(S, A(rp_[0] + 0.3, rp_[1] - 0.3, 3.3), lt, 0.15)
    cam(S, A(lerp(3.4, 2.8, k), lerp(-4.4, -3.8, k), lerp(1.2, 1.6, k)), A(-0.9, 0.9, lerp(1.5, 2.0, k)), 28, fcol='FFF0DC')


def beck_walks(S, k, t, lt):
    A = col(S, 'day')
    cx, cy = CAMP
    bp = (lerp(cx - 9.5, cx - 7.6, k), lerp(cy - 12.0, cy - 9.4, k), 0)
    to = (cx - 3.0, cy - 3.0, 0)
    S['beck'].place(A(*bp), facing(bp, to) + 0.12 * math.sin(lt * 4))
    w = walk(lt, 0.9)
    w.update(aL=(0.5, 0.2, 1.2, 0.0), aR=(0.25, 0.45, 0.4, 0.0), lean=0.2)
    S['beck'].apply(w)
    x = S['beck'].extra
    vis(x['gog'], False)
    vis(x['frost'], True)
    vis(x['ice'][:4], True)
    tint(S['rhm'], 'C2CEE2', 0.05)
    S['face']['beck'] = 'tired'
    rp_ = (bp[0] - 2.0, bp[1] - 1.2, 0)
    S['rook'].place(A(*rp_), facing(rp_, to) - 0.5)
    rw = walk(lt + 0.3, 0.9)
    rw.update(head=(-0.1, -0.6), aR=(1.3, 0.4, 0.4))
    S['rook'].apply(rw)
    S['face']['rook'] = 'shocked'
    for j, (who, p) in enumerate((('c1', (cx - 6.3, cy - 4.9, 0)), ('c3', (cx - 2.6, cy - 7.3, 0)))):
        S[who].place(A(*p), facing(p, bp))
        S[who].apply(P('point', aR=(1.45, 0.1, 0.05)) if j == 0 else P('stand', **ALARM))
        vis(S[who].extra['gog'], False)
        S['face'][who] = 'wide'
    cam(S, A(cx + lerp(0.9, 0.3, k), cy + lerp(1.3, 0.8, k), lerp(3.6, 3.2, k)), A(cx - 6.4, cy - 8.2, 1.7), 30, fcol='FFF0DC')


# ---------------------------------------------------------------- the night in the tent
def tent(S, t, dawn=False):
    T = S['tent']
    A = env(S, 'tent', '000000', fk=0.9 if dawn else 2.2)
    for s, w in T['walls']:
        w.rotation_euler = (0, -s * 0.72 + (0.012 if dawn else 0.05) * math.sin(t * (9 if dawn else 13) + s), 0)
    if dawn:
        tint(T['fabm'], 'FF9A3A', 1.6)
        tint(T['lampm'], '6A5A40', 0.0)
        T['lamp'].data.energy = 0
        T['day'].data.energy = 900
    else:
        tint(T['fabm'], '8A4A22', 0.08)
        T['lamp'].data.energy = 700 + 120 * math.sin(t * 17)
    return A


def in_bag(S, A, face='shut', lift=0.0):
    b = S['beck']
    b.place(A(0.2, -1.75, 0.5), 0.0, -PI / 2)
    b.apply(P('stand', aL=(0.1, 0.1, 0.1), aR=(0.1, 0.1, 0.1), head=(lift, 0.15)))
    x = b.extra
    vis(x['gog'], False)
    vis(x['frost'], True)
    S['face']['beck'] = face


def tent_night(S, k, t, lt):
    A = tent(S, t)
    in_bag(S, A)
    rp_ = (-1.7, 0.5, 0.0)
    S['rook'].place(A(rp_[0], rp_[1], 0.35), facing(rp_, (2.6, -0.4, 0)))
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.35, 0.0)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(2.7, 2.5, k), lerp(-1.3, -0.5, k), lerp(1.5, 1.7, k)), A(-1.0, 0.55, 1.3), 20, fcol='FFC890')


def tent_dawn(S, k, t, lt):
    A = tent(S, t, dawn=True)
    wake = ease((lt - 0.2) / 0.3)
    in_bag(S, A, 'calm' if wake > 0.4 else 'shut', 0.55 * wake)
    rp_ = (-1.7, 0.5, 0.0)
    pop = ease((lt - 0.35) / 0.15)
    S['rook'].place(A(rp_[0], rp_[1], 0.35), facing(rp_, (2.6, -0.4, 0)))
    S['hat_off'] = 1.0 - pop
    S['rook'].apply(blend(P('sit', aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.35, 0.0)),
                          P('sit', aL=(0.7, 1.15, 1.5, -0.7), aR=(0.7, 1.15, 1.5, -0.7), head=(-0.1, 0.0), lean=0.0), pop))
    S['face']['rook'] = 'shocked' if pop > 0.3 else 'sad'
    feather(S, A(rp_[0] + 0.2, rp_[1] - 0.3, 3.0), lt, 0.4)
    cam(S, A(lerp(2.3, 2.5, k), lerp(-2.0, -1.5, k), lerp(2.3, 2.1, k)), A(-0.9, 0.6, 1.25), 20, fcol='FFD8A8')


# ---------------------------------------------------------------- the helicopter
def cwm(S):
    return env(S, 'cwm', '6F9CDC', sun=2.4, sunc='FFF4E4', sdir=(0.6, -0.5, 0.55), fk=1.4, skyk=1.0)


def heli(S, A, pos, t, yaw=0.0, pitch=0.0, roll=0.0):
    C = S['cwm']
    C['heli'].location = (pos[0], pos[1], pos[2])              # set-local: the helicopter is parented to the set
    C['heli'].rotation_euler = (pitch, roll, yaw)
    C['heli'].scale = (1.35, 1.35, 1.35)
    C['rotor'].rotation_euler = (0, 0, t * 23)
    C['trotor'].rotation_euler = (t * 31, 0, 0)


def heli_climb(S, k, t, lt):
    A = cwm(S)
    e = ease(k)
    p = (lerp(-22, -4, e), lerp(120, 36, e), lerp(20, 13, e))
    heli(S, A, p, t, yaw=-0.15, pitch=0.1, roll=0.12 * math.sin(lt * 3))
    cam(S, A(lerp(5, 3, k), -12, 1.6), A(p[0] * 0.8, p[1] * 0.9, p[2] - 2.5), lerp(36, 44, k), fcol='FFF4E4')


def heli_land(S, k, t, lt):
    A = cwm(S)
    e = ease(k)
    heli(S, A, (0.0, 13.5, lerp(7.0, 0.3, e)), t, yaw=0.5, roll=0.05 * math.sin(lt * 5) * (1 - e))
    for j, who in enumerate(('c1', 'beck', 'c3')):
        p = (-1.1 + j * 1.1, -2.2 + lt * 0.9, 0)
        S[who].place(A(*p), PI)
        S[who].apply(walk(lt + j * 0.2, 0.8) if who != 'beck' else blend(walk(lt, 0.8), P('stand', aL=(0.2, 1.3, 0.2), aR=(0.2, 1.3, 0.2), lean=0.15), 0.7))
    vis(S['beck'].extra['gog'], False)
    rp_ = (3.4, -1.0, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (0, 13, 0)) + 0.3)
    S['rook'].apply(P('hat', lean=0.25, head=(0.2, 0.3), lL=(0.3, 0.1), lR=(-0.25, 0.25)))
    S['hat_tip'] = 0.7
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(3.2, 2.4, k), lerp(-10.5, -9.5, k), lerp(2.2, 2.6, k)), A(0.6, 8, lerp(4.6, 3.0, e)), 24, fcol='FFF4E4')


def heli_away(S, k, t, lt):
    A = cwm(S)
    e = ease(k)
    p = (lerp(0, -9, e), lerp(13.5, 30, e), lerp(1.5, 19, e))
    heli(S, A, p, t, yaw=lerp(0.5, 2.6, e), pitch=-0.18 * e, roll=0.15 * math.sin(lt * 2.5))
    rp_ = (1.6, 0.5, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (p[0], p[1], 0)))
    S['rook'].apply(P('reach', aR=(2.7, 0.2 + 0.4 * math.sin(lt * 9), 0.2), head=(-0.5, 0.0)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(4.2, 4.8, k), lerp(-5.6, -6.4, k), 1.0), A(lerp(1.2, -1.5, e), lerp(5, 10, e), lerp(3.4, 8.5, e)), 22, fcol='FFF4E4')


# ---------------------------------------------------------------- home
def beck_bandaged(S, k, t, lt):
    A = room(S, False)
    b = S['beckh']
    b.place(A(3.15, 3.75, 0.72), -0.35 + PI * 0 + 0.0)
    b.apply(P('sit', aL=(0.55, 0.0, 1.3, 0.5), aR=(0.55, 0.0, 1.3, 0.5), head=(0.1, 0.5 * ease(lt / 0.8)), lean=0.05))
    S['face']['beckh'] = 'warm'
    rp_ = (0.2, 3.0, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (3.2, 3.6, 0)) + 0.9)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.1, -0.7)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(0.6, 1.3, k), lerp(-3.6, -3.1, k), lerp(3.0, 2.85, k)), A(1.75, 3.3, 2.3), 28, fcol='FFE8D0')


def home_door(S, k, t, lt):
    A = env(S, 'home', '5A4A7A', sun=0.7, sunc='FFA878', sdir=(-0.8, -0.5, 0.15), fk=3.0, skyk=0.8)
    op = ease(lt / 0.5)
    S['home']['door'].rotation_euler = (0, 0, 1.5 * op)
    S['home']['doorl'].data.energy = 1100 * op
    b = S['beckh']
    b.place(A(0.6, lerp(-5.0, -2.4, k), 0), PI)
    wk = walk(lt, 1.0)
    wk.update(aL=(0.4, 0.1, 1.0), aR=(0.4, 0.1, 1.0))
    b.apply(wk)
    out_ = ease((lt - 0.08) / 0.35)
    S['wife'].place(A(-0.5, lerp(3.2, 0.9, out_), 0.5), 0.0)
    S['wife'].apply(blend(walk(lt, 1.6), P('stand', aL=(1.1, 0.7, 0.3), aR=(1.1, 0.7, 0.3)), out_))
    S['face']['wife'] = 'warm'
    cam(S, A(lerp(-2.8, -2.2, k), lerp(-10.5, -9.0, k), lerp(1.8, 2.2, k)), A(0.0, 0.5, 2.9), 28, fcol='FFD8B8')


def hollow(S, k, t, lt):
    A = env(S, 'col', '7FA0DC', sun=2.2, sunc='FFD8A8', sdir=(-0.8, -0.3, 0.22), fk=1.4, skyk=0.9)
    S['col']['hollow'].location = (0, 0, 0)
    e = ease(k)
    cam(S, A(lerp(2.6, 1.6, e), lerp(-4.6, -3.2, e), lerp(3.6, 2.8, e)), A(lerp(0.2, 2.5, e), lerp(1.4, 6.0, e), lerp(0.0, 0.6, e)), 24, fcol='FFE8D0')


# ---------------------------------------------------------------- photographs for the case board
def photo_peak(S, k, t, lt):
    A = ridge(S, 'noon')
    cam(S, A(-50, -46, 6), A(0, 70, 48), 30)


def photo_beck(S, k, t, lt):
    A = ridge(S, 'noon')
    S['beck'].place(A(0.0, 0.0, 0), 0.2)
    S['beck'].apply(P('stand', aR=(2.6, 0.5, 0.3), aL=(0.2, 0.5, 1.2)))
    S['face']['beck'] = 'warm'
    cam(S, A(1.0, -5.6, 2.6), A(0.0, 0.0, 2.3), 44)


def photo_walk(S, k, t, lt):
    beck_walks(S, 0.6, 3.0, 0.9)


SHOTS3D = {f.__name__: f for f in (
    ice_body, col_wide, left_walk, eyes_open, rook_jolt, rook_cairn, rook_go, rook_wrong, signoff, peak_wide, beck_climb, blur_pov, beck_blind,
    beck_wait, descend, blizzard_hit, lost_group, rescuer, rescuer_no, dawn_col, doctor_kneel, doctor_leave, phone, frozen_hand, beck_rise,
    beck_walks, tent_night, tent_dawn, heli_climb, heli_land, heli_away, beck_bandaged, home_door, hollow)}
STILLS = dict(peak=photo_peak, beck=photo_beck, walk=photo_walk)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it. New sets: a radio tent at the foot of the mountain (how the news went down),
# a steep ice face with a fixed rope (the descent on foot), a lower camp on the moraine (the wait for the
# helicopter), the inside of a helicopter cabin (the flight), a hospital room (the cost) and a study with a desk
# (the book). New shots on the Short's sets as well. Still generic: no emblem, flag of a country, sign or lettering
# anywhere; the camps, aircraft and rooms are not models of real ones; and the extra people (an expedition leader,
# a radio operator, a pilot) are stand-ins, not likenesses. The climber who lay beside him and died is named in
# the narration and never shown.
import bmesh  # noqa: E402

ORG.update(radio=(21000, 0, 0), face=(24000, 0, 0), low=(27000, 0, 0), pit=(30000, 0, 0), ward=(33000, 0, 0), study=(36000, 0, 0))
PUR = '7A4EA8'
FA = 0.6                                    # the ice face's angle
FC, FS = math.cos(FA), math.sin(FA)
_kit_add = add


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """The kit's primitives made from mesh data instead of operators (operators slow down as the scene fills). The
    Short's set functions look this name up when they run, so every set in the film is built this way."""
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'cylinder':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius', 1.0),
                              radius2=kw.get('radius', 1.0), depth=kw.get('depth', 2.0))
    elif kind == 'cone':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius1', 1.0),
                              radius2=kw.get('radius2', 0.0), depth=kw.get('depth', 2.0))
    elif kind == 'ico_sphere':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('subdivisions', 2), radius=kw.get('radius', 1.0))
    else:
        bm.free()
        return _kit_add(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
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


def box(col, loc, scale, parent, rot=(0, 0, 0), **kw):
    return add('cube', col, loc, rot=rot, scale=scale, size=1, parent=parent, **kw)


def cyl(col, loc, rad, dep, parent, rot=(0, 0, 0), n=6, **kw):
    return add('cylinder', col, loc, rot=rot, radius=rad, depth=dep, vertices=n, parent=parent, **kw)


# ---------------------------------------------------------------- the radio tent at the foot of the mountain
def set_radio(r):
    out = {}
    box('4A4438', (0, 0, -0.1), (18, 16, 0.2), r)
    box('3A5A7A', (0.5, 0.5, 0.02), (11, 9, 0.05), r)                                                  # groundsheet
    out['canm'] = cm = own_mat('canvas', 'A8B078', 0.9, 0.35)
    use(box('A8B078', (0, 7, 3.0), (18, 0.12, 6.0), r), cm)                                            # back wall
    for s in (-1, 1):
        use(box('A8B078', (s * 8.6, 0, 3.0), (0.12, 16, 6.0), r, rot=(0, s * 0.12, 0)), cm)
        use(box('A8B078', (s * 4.3, 0, 7.0), (9.4, 16, 0.12), r, rot=(0, s * 0.42, 0)), cm)            # the pitched roof
        for y in (-5, 0, 5):
            cyl('6A5A3A', (s * 8.2, y, 3.0), 0.1, 6.0, r)
    cyl('6A5A3A', (0, 6.7, 4.4), 0.12, 8.8, r)
    cyl('6A5A3A', (0, 0, 8.7), 0.1, 16, r, rot=(PI / 2, 0, 0))                                          # ridge pole
    box('DCE8FF', (-4.6, 6.9, 2.7), (2.4, 0.1, 5.2), r, emit=3.0)                                       # the doorway: daylight outside
    for s in (-1, 1):
        box('8A9460', (-4.6 + s * 1.5, 6.82, 2.9), (0.9, 0.12, 5.6), r, rot=(0, 0, s * 0.12))           # the door flaps, tied back
    box('8A7A5A', (5.6, 1.5, 1.5), (2.4, 5.4, 0.16), r)                                                # the table along the side wall
    for dx, dy in ((-1.0, -2.5), (1.0, -2.5), (-1.0, 2.5), (1.0, 2.5)):
        box('5A4E3A', (5.6 + dx, 1.5 + dy, 0.75), (0.14, 0.14, 1.5), r)
    box('2A2F3A', (6.1, 2.6, 2.15), (1.2, 2.0, 1.15), r, rough=0.5)                                    # the radio: a plain dark box
    box('3A4250', (5.48, 2.6, 2.15), (0.06, 1.7, 0.9), r)
    out['dialm'] = dm = own_mat('dial', 'FF7A1A', 0.4, 5.0)
    for j in range(3):
        use(cyl('FF7A1A', (5.43, 2.0 + j * 0.6, 2.4), 0.13, 0.05, r, rot=(0, PI / 2, 0), n=8), dm)
    for j in range(4):
        cyl('B9C0CA', (5.43, 1.95 + j * 0.42, 1.95), 0.08, 0.1, r, rot=(0, PI / 2, 0), rough=0.3)
    cyl('B9C0CA', (6.4, 3.4, 4.2), 0.03, 3.0, r, n=4, rough=0.3)                                        # aerial
    out['handset'] = mov(box('14161C', (5.2, 1.3, 1.68), (0.26, 0.75, 0.2), r, rough=0.4))
    cyl('3A3F4C', (5.9, -0.4, 1.75), 0.26, 0.4, r, n=8)                                                # a lantern on the table
    out['lampm'] = lm = own_mat('rlantern', 'FFD08A', 0.5, 7.0)
    use(cyl('FFD08A', (5.9, -0.4, 2.1), 0.2, 0.34, r, n=8), lm)
    out['lamp'] = light((5.0, -0.2, 3.0), 500, 'FFC27A', kind='POINT', parent=r)
    out['door'] = light((-4.4, 5.6, 3.2), 700, 'DCE8FF', kind='POINT', parent=r)
    box('F0E8D2', (5.4, 0.5, 1.6), (1.1, 0.8, 0.03), r, rot=(0, 0, 0.2))                                # a blank pad
    cyl('6A5A3A', (3.6, 1.5, 0.45), 0.5, 0.9, r, n=8)                                                  # the operator's stool
    for j, (x, y) in enumerate(((-6.6, 3.5), (-6.9, 1.6), (-5.5, 2.6))):                               # blue barrels
        cyl('2F5FA8', (x, y, 1.0), 0.75, 2.0, r, n=10)
        cyl('1E3E70', (x, y, 2.02), 0.78, 0.1, r, n=10)
    for j, (x, y, z, c) in enumerate(((1.5, 6.0, 0.6, '8A6A3A'), (2.9, 6.1, 0.5, '6E5A3A'), (1.9, 6.0, 1.6, '7A5E36'))):   # crates
        box(c, (x, y, z), (1.3, 1.1, 1.0 - 0.1 * j), r)
    for j in range(4):                                                                                # oxygen bottles leaning in the corner
        cyl('FF7A1A' if j % 2 else 'D8DCE4', (7.4, 5.2 + 0.45 * j, 1.0), 0.2, 2.0, r, rot=(0.25, 0, 0), rough=0.4)
    box('5E6E58', (-5.6, -3.0, 0.7), (2.6, 6.0, 0.3), r)                                               # a camp bed
    box('C8322C', (-5.6, -3.4, 0.95), (2.4, 4.4, 0.25), r)
    return out


# ---------------------------------------------------------------- the ice face
def fp(d, x=0.0):
    """A point on the ice face: d along the fall line (up is positive), x across it."""
    return (x, d * FC, d * FS)


def set_face(r):
    out = {}
    rr = empty((0, 0, 0), r, (FA, 0, 0))
    box('D2DFF0', (0, 0, -3), (150, 420, 6), rr)
    for j in range(46):                                                                                # blue ice showing through
        x, y = -60 + 120 * rnd(j, 21), -150 + 300 * rnd(j, 22)
        if abs(x) < 4.5:
            continue
        box('A9D4EE' if j % 2 else 'BFDDF2', (x, y, 0.1), (3 + 6 * rnd(j, 23), 2 + 4 * rnd(j, 24), 0.7 + 1.2 * rnd(j, 25)), rr,
            rot=(0.2 * (rnd(j, 26) - 0.5), 0.2 * (rnd(j, 27) - 0.5), rnd(j, 28) * 3), rough=0.35)
    for j in range(16):                                                                                # ribs of rock
        s = -1 if j % 2 else 1
        box(ROCK if j % 3 else '5E667A', (s * (30 + 34 * rnd(j, 29)), -170 + j * 22, 1.5), (6 + 8 * rnd(j, 30), 10 + 9 * rnd(j, 31), 4 + 5 * rnd(j, 32)), rr,
            rot=(0.3 * rnd(j, 33), 0.3 * rnd(j, 34), rnd(j, 35) * 3))
    cyl('FF7A1A', (-0.9, 0, 0.16), 0.045, 400, rr, rot=(PI / 2, 0, 0), n=5)                              # the fixed rope
    for j in range(34):
        cyl('2A2F3A', (-0.9, -198 + j * 12, 0.35), 0.06, 0.8, rr, n=5)                                  # its anchors
        box('FF7A1A', (-0.9, -198 + j * 12, 0.75), (0.3, 0.03, 0.2), rr, emit=0.4)
    for j in range(26):                                                                                # steps kicked into the snow
        box('9FB2D2', (0.3 + 0.5 * (j % 2), -40 + j * 3.0, 0.03), (0.7, 0.45, 0.06), rr)
    box('B4C8E4', (0, -420, -150), (3000, 1600, 2), r)                                                 # the glacier far below
    for j in range(9):
        box('3E5E90', (-500 + j * 130, -330 - 40 * rnd(j, 36), -148.8), (90, 3.5, 0.2), r, rot=(0, 0, 0.3 * (rnd(j, 37) - 0.5)))
    for j, (x, y, rad, h) in enumerate(((-420, -700, 220, 300), (60, -900, 260, 360), (520, -640, 230, 280), (-800, -300, 200, 260),
                                        (860, -260, 210, 250), (-260, -1100, 240, 300))):
        peak(r, x, y, rad, h, z0=-150, cap=0.5, spin=j * 0.9)
    return out


# ---------------------------------------------------------------- the lower camp on the moraine
def set_low(r):
    out = {}
    box('8E96A6', (0, 0, -0.5), (1400, 1400, 1), r)
    for j in range(60):
        x, y = -45 + 90 * rnd(j, 41), -22 + 70 * rnd(j, 42)
        if abs(x) < 3.2 and abs(y) < 3.2:
            continue
        s = 0.3 + 1.1 * rnd(j, 43)
        add('ico_sphere', ('5A6070', '747A8A', '474C5A')[j % 3], (x, y, 0.1), rot=(0, 0, rnd(j, 44) * 6), scale=(s * 1.3, s, s * 0.6), radius=1,
            subdivisions=1, parent=r)
    for j in range(14):
        add('ico_sphere', 'DCE6F4', (-40 + 80 * rnd(j, 45), -12 + 60 * rnd(j, 46), -0.12), scale=(4 + 5 * rnd(j, 47), 2.5 + 2 * rnd(j, 48), 0.3),
            radius=1, subdivisions=1, parent=r)
    for j in range(9):                                                                                # a wall of dark rock behind the camp
        box(ROCK if j % 2 else '3E4558', (-52 + j * 13, 30 + 5 * rnd(j, 49), 9 + 5 * rnd(j, 50)), (15, 10, 22 + 12 * rnd(j, 51)), r,
            rot=(0.12 * rnd(j, 52), 0.1 * rnd(j, 53), 0.4 * (rnd(j, 54) - 0.5)))
        box('E6EEF8', (-52 + j * 13, 30 + 5 * rnd(j, 49), 21 + 11 * rnd(j, 50)), (11, 9, 1.2), r, rot=(0.1, 0.1 * rnd(j, 53), 0.3 * (rnd(j, 54) - 0.5)))
    peak(r, -60, 330, 230, 300, cap=0.5, spin=0.7)
    peak(r, 260, 280, 200, 230, cap=0.45, spin=1.4)
    peak(r, -330, 160, 180, 190, cap=0.4, spin=0.2)
    for j, (x, y, c, yw) in enumerate(((-8.5, 9.5, 'FF7A1A', 0.5), (-2.5, 13, YEL, -0.2), (5.5, 11.5, BLUE, 0.3), (11.5, 7.5, GRN, -0.6))):
        dome(r, x, y, c, yw, 1.05)
    for j in range(11):                                                                                # a ring of stones round the stove
        a = j * 2 * PI / 11
        add('ico_sphere', ('5A6070', '747A8A')[j % 2], (7.0 + 1.5 * math.cos(a), 1.2 + 1.5 * math.sin(a), 0.3), scale=(0.6, 0.5, 0.5), radius=1,
            subdivisions=1, parent=r)
    cyl('B9C0CA', (7.0, 1.2, 0.75), 0.5, 0.6, r, n=8, rough=0.3)                                        # a pot on the stove
    box('49C8FF', (7.0, 1.2, 0.36), (0.5, 0.5, 0.12), r, emit=4.0)
    box('B08A4A', (0, 0.4, 0.45), (1.9, 1.2, 0.9), r)                                                  # the crate he sits on
    for j, (x, y) in enumerate(((-4.2, 3.4), (-5.3, 2.3))):
        cyl('2F5FA8', (x, y, 0.85), 0.65, 1.7, r, n=10)
    box('C8322C', (-3.6, -1.6, 0.2), (1.4, 5.0, 0.3), r, rot=(0, 0, 0.5))                              # a rolled sleeping mat
    for j in range(5):
        cyl('2A2F3A', (-9 + j * 4.6, 5.5 + 1.5 * rnd(j, 55), 1.0), 0.05, 2.0, r, n=5)                   # wands with plain orange tags
        box('FF7A1A', (-8.7 + j * 4.6, 5.5 + 1.5 * rnd(j, 55), 1.8), (0.6, 0.03, 0.4), r, emit=0.5)
    return out


# ---------------------------------------------------------------- inside the helicopter
def set_pit(r):
    out = {}
    OL, DK = '56633A', '22262E'
    box(DK, (0, 1.2, 0.0), (4.6, 6.4, 0.2), r)
    box(OL, (0, 1.2, 4.3), (4.8, 6.6, 0.2), r)                                                         # roof
    box(OL, (0, 4.4, 1.1), (4.6, 0.2, 2.2), r)                                                         # rear bulkhead, open above
    for s in (-1, 1):
        box(OL, (s * 2.3, 1.2, 0.55), (0.14, 6.4, 1.1), r)                                              # low door sills
        for y in (-1.9, 1.3, 4.4):
            box(OL, (s * 2.3, y, 2.2), (0.16, 0.16, 4.2), r)                                            # door posts
        box('3A4250', (s * 1.05, 0.6, 0.95), (1.3, 1.3, 0.3), r)                                        # the two front seats
        box('3A4250', (s * 1.05, 1.3, 2.0), (1.3, 0.25, 2.2), r)
        box('2A2F3A', (s * 1.05, 1.32, 3.2), (0.7, 0.2, 0.5), r)
    box(OL, (0, -1.9, 2.2), (0.12, 0.12, 4.2), r)                                                      # windscreen centre strut
    box(OL, (0, -1.9, 0.35), (4.6, 0.3, 0.7), r)                                                        # the nose below the glass
    box('14181E', (0, -1.3, 0.95), (3.6, 0.6, 0.7), r)                                                 # instrument panel, seen from behind
    box('14181E', (0, -1.05, 1.35), (3.9, 1.0, 0.1), r)
    for s in (-1, 1):
        cyl('B9C0CA', (s * 1.05, -0.2, 1.0), 0.05, 1.3, r, rot=(0.25, 0, 0), n=5, rough=0.3)            # control sticks
        add('ico_sphere', DK, (s * 1.05, -0.36, 1.66), radius=0.11, subdivisions=1, parent=r)
    out['warnm'] = wm = own_mat('warn', 'FFB000', 0.4, 4.0)
    use(box('FFB000', (0.0, -0.74, 1.5), (0.5, 0.06, 0.16), r), wm)                                     # one amber lamp on the coaming
    out['in'] = light((0, 0.2, 3.6), 250, 'FFE8D0', kind='POINT', parent=r)
    out['world'] = w = mov(empty((0, 0, 0), r))                                                       # what slides past outside
    box('C4D2E6', (0, 300, -120), (3000, 3000, 2), w)
    for j in range(22):
        s = -1 if j % 2 else 1
        x, y = s * (70 + 190 * rnd(j, 61)), -260 + j * 62
        hgt = 130 + 150 * rnd(j, 62)
        peak(w, x, y, 60 + 60 * rnd(j, 63), hgt, z0=-120, cap=0.4 + 0.2 * rnd(j, 64), spin=j * 1.3)
    for j in range(30):                                                                                # ice towers far below
        box('A9D4EE' if j % 2 else 'D4E8F6', (-60 + 120 * rnd(j, 65), -200 + 900 * rnd(j, 66), -112), (8 + 9 * rnd(j, 67), 8 + 9 * rnd(j, 68), 14), w,
            rot=(0, 0, rnd(j, 69) * 3))
    return out


# ---------------------------------------------------------------- the hospital room
def set_ward(r):
    out = {}
    box('A8B4AE', (0, 0, -0.1), (18, 16, 0.2), r)
    box('C8D6DA', (0, 7.5, 4.5), (18, 0.3, 9), r)
    box('BCCCD2', (-9, 0, 4.5), (0.3, 16, 9), r)
    box('BCCCD2', (9, 0, 4.5), (0.3, 16, 9), r)
    box('8E9C9E', (0, 0, 9.1), (18, 16, 0.2), r)
    box('7E9A9E', (0, 7.3, 1.2), (18, 0.14, 0.3), r)                                                   # a rail along the wall
    out['blindm'] = bm_ = own_mat('blind', 'FFF0D0', 0.6, 1.2)
    for j in range(9):                                                                                # the window: slats of a blind
        use(box('FFF0D0', (4.8, 7.3, 2.9 + j * 0.42), (4.2, 0.08, 0.3), r, rot=(0.35, 0, 0)), bm_)
    for dx, dz, sx, sz in ((-2.25, 1.75, 0.3, 4.6), (2.25, 1.75, 0.3, 4.6), (0, 4.1, 4.8, 0.3), (0, -0.55, 4.8, 0.3)):
        box('E8ECEC', (4.8 + dx, 7.26, 2.9 + dz), (sx, 0.14, sz), r)
    out['win'] = light((4.8, 6.2, 4.8), 1100, 'FFE8C8', 4.0, kind='AREA', parent=r)
    out['win'].rotation_euler = (-PI / 2, 0, 0)
    out['top'] = light((0, 0, 8.2), 420, 'F0F6FF', kind='POINT', parent=r)
    box('D8DCE4', (-1.5, 4.4, 1.0), (2.7, 5.4, 0.3), r, rough=0.4)                                     # the bed
    for dx, dy in ((-1.2, -2.5), (1.2, -2.5), (-1.2, 2.5), (1.2, 2.5)):
        cyl('B9C0CA', (-1.5 + dx, 4.4 + dy, 0.5), 0.09, 1.0, r, rough=0.3)
    box('F4F2EA', (-1.5, 4.4, 1.35), (2.5, 5.2, 0.4), r)
    box('D8DCE4', (-1.5, 7.1, 2.2), (2.9, 0.2, 2.6), r, rough=0.4)
    box('FFFFFF', (-1.5, 6.3, 1.72), (2.0, 1.2, 0.36), r)                                              # pillow
    box('A8C4D8', (-1.5, 3.3, 1.86), (2.6, 2.9, 0.62), r)                                              # blanket
    box('F4F2EA', (-1.5, 4.85, 1.88), (2.6, 0.4, 0.58), r)
    cyl('B9C0CA', (1.4, 6.6, 3.0), 0.05, 6.0, r, n=5, rough=0.3)                                        # a drip stand
    box('B9C0CA', (1.4, 6.6, 0.1), (1.2, 1.2, 0.1), r, rough=0.3)
    box('B9C0CA', (1.4, 6.6, 5.9), (1.0, 0.06, 0.06), r, rough=0.3)
    box('DCEEFF', (1.8, 6.6, 5.2), (0.5, 0.2, 0.9), r, rough=0.2, emit=0.4)
    box('E8ECEC', (-4.6, 6.4, 1.2), (1.8, 1.6, 2.4), r)                                                # bedside cabinet
    cyl('3E9A5C', (-4.6, 6.3, 2.75), 0.2, 0.6, r, n=8)                                                 # a plant in a pot
    for j in range(5):
        box('3E9A5C', (-4.6 + 0.2 * math.cos(j * 1.3), 6.3 + 0.2 * math.sin(j * 1.3), 3.4), (0.1, 0.36, 0.9), r, rot=(0.3 * math.sin(j), 0.3 * math.cos(j), j))
    box('5E6E8A', (1.1, 3.9, 0.75), (1.7, 1.7, 0.25), r)                                               # the visitor's chair
    box('5E6E8A', (1.9, 3.9, 1.9), (0.22, 1.7, 2.3), r)
    for dx, dy in ((-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)):
        cyl('B9C0CA', (1.1 + dx, 3.9 + dy, 0.35), 0.06, 0.7, r, n=5, rough=0.3)
    box('1A222E', (-6.6, 7.2, 5.2), (2.2, 0.3, 1.5), r, rough=0.3)                                     # a monitor on the wall: one plain line
    out['tracem'] = tm = own_mat('trace', '3EC46A', 0.4, 5.0)
    out['trace'] = []
    for j in range(8):
        out['trace'].append(use(box('3EC46A', (-7.4 + j * 0.23, 7.02, 5.2), (0.2, 0.05, 0.07), r), tm))
    for j in range(7):                                                                                # a curtain on a rail
        box('9FC0B0' if j % 2 else '8EB0A0', (-8.6, -6.5 + j * 0.9, 4.2), (0.25, 0.9, 7.0), r)
    box('B9C0CA', (-8.5, -3.0, 7.8), (0.1, 9.0, 0.1), r, rough=0.3)
    return out


# ---------------------------------------------------------------- the study
def set_study(r):
    out = {}
    box('5A4630', (0, 0, -0.1), (20, 16, 0.2), r)
    box('2E4A52', (0, 7, 4.5), (20, 0.3, 9), r)
    box('284248', (-10, 0, 4.5), (0.3, 16, 9), r)
    box('284248', (10, 0, 4.5), (0.3, 16, 9), r)
    box('1E2E32', (0, 0, 9.1), (20, 16, 0.2), r)
    box('3A2E26', (0, 6.8, 0.4), (20, 0.2, 0.8), r)
    box('6E3A46', (0, 0.6, 0.02), (11, 8, 0.06), r)                                                    # rug
    box('1A2A50', (5.2, 6.82, 4.8), (4.2, 0.1, 4.6), r, emit=0.8)                                      # the window at night
    for dx, dz, sx, sz in ((0, 0, 0.16, 4.6), (0, 0, 4.2, 0.16), (-2.2, 0, 0.3, 5.0), (2.2, 0, 0.3, 5.0), (0, 2.45, 4.7, 0.3), (0, -2.45, 5.0, 0.4)):
        box('D8D0C0', (5.2 + dx, 6.74, 4.8 + dz), (sx, 0.14, sz), r)
    box('4A3426', (-5.5, 6.3, 4.0), (6.0, 1.2, 8.0), r)                                                # bookshelves
    for row in range(5):
        box('3A2A1E', (-5.5, 5.7, 0.9 + row * 1.5), (5.8, 0.2, 0.12), r)
        for j in range(12):
            box(('7A3E34', '2F5FA8', 'C9A227', '3E6A4A', 'B8B0A0', '5A3E6A')[(j + row * 3) % 6], (-8.1 + j * 0.46, 5.75, 1.5 + row * 1.5),
                (0.36, 0.5, 0.9 + 0.3 * rnd(j, row + 70)), r)
    box('6A4A30', (0, 0.2, 1.6), (7.4, 2.8, 0.16), r)                                                  # the desk, standing free
    for s in (-1, 1):
        box('5A3E28', (s * 3.3, 0.2, 0.8), (0.5, 2.6, 1.6), r)
    box('5A3E28', (0, 1.5, 1.0), (6.2, 0.12, 1.1), r)
    mo = empty((2.5, 0.5, 1.7), r, (0, 0, -0.55))                                                     # a monitor, its screen turned to him
    box('C8C4B8', (0, 0, 0.95), (1.9, 1.3, 1.5), mo)
    box('C8C4B8', (0, 0, 0.15), (0.8, 0.8, 0.3), mo)
    out['screenm'] = sm = own_mat('screen', 'CFE8FF', 0.4, 2.2)
    use(box('CFE8FF', (0, 0.66, 0.98), (1.6, 0.04, 1.2), mo), sm)
    box('B8B4A8', (0.9, 0.9, 1.72), (2.0, 0.7, 0.08), r, rot=(0, 0, -0.2))                              # keyboard
    box('F4F2EA', (-1.5, 0.1, 1.86), (1.2, 1.6, 0.36), r, rot=(0, 0, 0.1))                              # a stack of pages
    box('F4F2EA', (-1.4, 0.15, 2.05), (1.2, 1.6, 0.02), r, rot=(0, 0, -0.15))
    cyl('3A3F4C', (-3.0, 1.0, 1.75), 0.35, 0.12, r, n=8)                                               # desk lamp
    cyl('3A3F4C', (-3.0, 1.0, 2.5), 0.05, 1.5, r, n=5, rot=(0.2, 0, 0))
    out['shadem'] = shm = own_mat('dshade', 'FFD9A0', 0.6, 4.0)
    use(add('cone', 'FFD9A0', (-2.9, 0.6, 3.25), rot=(0.5, 0, 0), radius1=0.6, radius2=0.25, depth=0.6, vertices=8, parent=r), shm)
    out['lamp'] = light((-2.6, 0.2, 3.0), 700, 'FFC98A', kind='POINT', parent=r)
    out['top'] = light((0, -1, 8.0), 260, 'DCE8FF', kind='POINT', parent=r)
    box('4A3E36', (0.3, 2.3, 0.75), (1.9, 1.7, 0.3), r)                                                # his chair
    box('4A3E36', (0.3, 3.1, 2.1), (1.9, 0.3, 2.6), r)
    for j, (x, z, w_, hh, c) in enumerate(((1.0, 5.4, 1.6, 2.0, '6E8AA8'), (-1.2, 5.9, 1.3, 1.3, 'A88A6E'))):
        box('D8D0C0', (x, 6.78, z), (w_ + 0.3, 0.12, hh + 0.3), r)                                      # framed pictures, blank colour fields
        box(c, (x, 6.72, z), (w_, 0.1, hh), r)
    return out


def pilot_head(head):
    """A stand-in pilot: a plain flying helmet, visor pushed up, a boom microphone. No badge, no markings."""
    add('ico_sphere', 'B88A64', (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
    add('ico_sphere', 'D8DCE4', (0, 0.06, 0.1), scale=(1.06, 1.08, 1.05), radius=0.33, subdivisions=1, parent=head, rough=0.4)
    box('1A222E', (0, -0.2, 0.26), (0.5, 0.2, 0.12), head, rough=0.2)
    for s in (-1, 1):
        add('ico_sphere', '3A3F4C', (s * 0.31, 0.02, 0.0), scale=(0.5, 1, 1.2), radius=0.14, subdivisions=1, parent=head)
    box('2A2F3A', (0.2, -0.25, -0.14), (0.22, 0.04, 0.04), head, rot=(0, 0, 0.5))
    eyes, brows = [], []
    for s in (-1, 1):
        eyes.append(box('FFFFFF', (s * 0.105, -0.262, 0.04), (0.1, 0.03, 0.075), head, emit=0.6))
        box('1A222E', (s * 0.105, -0.28, 0.035), (0.042, 0.02, 0.046), head)
        brows.append(box('2A1E18', (s * 0.105, -0.27, 0.125), (0.13, 0.03, 0.026), head, rot=(0, s * 0.12, 0)))
    box('9E7250', (0, -0.285, -0.04), (0.05, 0.05, 0.08), head)
    jaw = empty((0, -0.2, -0.13), head)
    box('5A2A2E', (0, -0.07, 0.0), (0.11, 0.03, 0.03), jaw)
    return dict(jaw=jaw, eyes=eyes, brows=brows)


_build0, _reset0, _finish0 = build, reset, finish
XCAST = ('lead', 'pilot')


def build():
    S = _build0()
    for name, fn in (('radio', set_radio), ('face', set_face), ('low', set_low), ('pit', set_pit), ('ward', set_ward), ('study', set_study)):
        S['colls'][name], S[name] = group(name, fn)
    S['lead'] = ld = K.Rig(dict(top=PUR, pants=PUR, hand='1E2026', boot='2A2F3A'), climber_head('D2A482', PUR, '5A4030'))
    add('cube', '2A2F3A', (0, 0.3, 0.6), scale=(0.56, 0.3, 0.8), size=1, parent=ld.body)
    S['pilot'] = K.Rig(dict(top='5A6340', pants='5A6340', hand='2A2F3A', boot='1A1A20'), pilot_head)
    S['cast'] += [ld, S['pilot']]
    S['wand'] = wd = mov(empty(FAR))                                                                 # a marker wand with a plain orange tag
    cyl('2A2F3A', (0, 0, 1.3), 0.045, 2.6, wd, n=5)
    box('FF7A1A', (0.32, 0, 2.4), (0.6, 0.03, 0.4), wd, emit=0.5)
    S['stone'] = mov(add('ico_sphere', '8A90A0', FAR, scale=(1.5, 1.2, 0.4), radius=0.3, subdivisions=1))
    S['mug'] = mov(cyl('D8DCE4', FAR, 0.12, 0.26, None, n=8, rough=0.3))
    S['book'] = bk_ = mov(empty(FAR))                                                                # a finished book: plain cover, no lettering
    box('FF7A1A', (0, 0, 0), (0.95, 1.3, 0.2), bk_)
    box('F4F2EA', (0.03, 0, 0), (0.93, 1.22, 0.15), bk_)
    return S


def reset(S):
    _reset0(S)
    x = S['lead'].extra
    vis(x['gog'], True)
    for nm in ('mask', 'ice', 'frost'):
        vis(x[nm], False)
    Rd = S['radio']
    tint(Rd['dialm'], 'FF7A1A', 5.0)
    Rd['lamp'].data.energy = 500
    Rd['door'].data.energy = 700
    tint(S['pit']['warnm'], 'FFB000', 4.0)
    tint(S['ward']['tracem'], '3EC46A', 5.0)
    for j, o in enumerate(S['ward']['trace']):
        o.location.z = 5.2
    S['face'].update(lead='calm', pilot='calm')
    S['jaw'].update(lead=0.0, pilot=0.0)


def finish(S, t):
    _finish0(S, t)
    for j, who in enumerate(XCAST):
        x = S[who].extra
        k = dict(calm=1.0, wide=1.7, shut=0.07, tired=0.45, warm=0.85, squint=0.4, sad=0.6).get(S['face'][who], 1.0)
        bl = (t * 0.29 + 0.41 * j + 0.6) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        x['jaw'].rotation_euler = (S['jaw'][who], 0, 0)


def bare(S, who, face=None, mask=False):
    """Goggles off, so the face reads."""
    x = S[who].extra
    vis(x['gog'], False)
    vis(x['mask'], mask)
    if face:
        S['face'][who] = face


def frosted(S, n=4):
    x = S['beck'].extra
    vis(x['gog'], False)
    vis(x['frost'], True)
    vis(x['ice'][:n], True)
    tint(S['rhm'], 'C2CEE2', 0.05)


# ---------------------------------------------------------------- new shots: the expedition
def team_base(S, k, t, lt):
    """Below the mountain the leader points the way up; the team listens; Rook is not impressed."""
    A = env(S, 'base', '7FA8E0', sun=2.6, sunc='FFF0DC', sdir=(0.55, -0.6, 0.5), fk=2.0, skyk=1.0)
    flutter(S, t)
    S['lead'].place(A(-5.2, 4.6, 0), PI / 2)
    S['lead'].apply(P('stand', aR=(0.2, 2.1 + 0.12 * math.sin(lt * 3), 0.15), aL=(0.5, 0.1, 1.2, 0.4), head=(-0.1, 0.35 * math.sin(lt * 1.6))))
    bare(S, 'lead', 'warm')
    S['jaw']['lead'] = 0.12 + 0.1 * math.sin(lt * 11)
    for j, (who, p) in enumerate((('beck', (-1.6, 4.4, 0)), ('c1', (-0.3, 6.0, 0)), ('c2', (0.6, 3.6, 0)))):
        S[who].place(A(*p), -PI / 2 + 0.15 * (j - 1))
        S[who].apply(P('stand', head=(-0.2, -0.45 + 0.15 * math.sin(lt * 1.3 + j)), aL=(0.3, 0.1, 0.9, 0.5) if j == 0 else (0.05, 0.12, 0.15)))
        bare(S, who, 'warm' if j == 0 else 'calm')
    S['rook'].place(A(-2.9, 1.4, 0), 0.25)
    S['rook'].apply(P('cross', head=(-0.1, -0.5 + 0.2 * math.sin(lt * 1.1))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-1.2, -2.2, k), lerp(-6.4, -5.6, k), 2.3), A(-2.2, 4.0, 2.4), 28, fcol='FFF0DC')


def eye_cu(S, k, t, lt):
    """His face: he blinks, squints, and puts a glove out in front of him as if the air had thickened."""
    A = ridge(S, 'dawn')
    S['beck'].place(A(-0.3, 0.0, 0), 0.25)
    S['beck'].apply(P('stand', aL=(1.15 + 0.15 * math.sin(lt * 4), 0.55, 0.35, 0.2), aR=(0.3, 0.3, 0.8), head=(0.05, 0.3 * math.sin(lt * 2.4))))
    S['face']['beck'] = 'squint' if (lt * 1.7) % 1 > 0.25 else 'shut'
    cam(S, A(lerp(1.5, 1.1, k), lerp(-3.2, -2.7, k), 2.75), A(-0.25, 0.0, 2.45), 44, fcol='FFE8D0')


def lead_tells(S, k, t, lt):
    """On the ledge the leader and Weathers talk it over. Accounts differ on who decided; the picture takes no side."""
    A = ridge(S, 'dawn')
    lp, bp = (1.6, 0.9, 0), (-0.9, 0.5, 0)
    S['lead'].place(A(*lp), facing(lp, bp) - 0.35)
    S['lead'].apply(P('stand', aL=(0.9 + 0.2 * math.sin(lt * 5), 0.2, 0.9, 0.3), aR=(0.3, 0.2, 0.5), head=(0.05, 0.3)))
    bare(S, 'lead')
    S['jaw']['lead'] = 0.1 + 0.1 * math.sin(lt * 12)
    S['beck'].place(A(*bp), facing(bp, lp) + 0.35)
    nod = 0.12 * math.sin(lt * 6)
    S['beck'].apply(P('stand', aR=(0.5, 0.2, 1.1, 0.4), aL=(0.2, 0.2, 0.4), head=(0.1 + nod, -0.3)))
    S['face']['beck'] = 'squint'
    rp_ = (-4.2, -1.6, 0.0)
    S['rook'].place(A(rp_[0], rp_[1], 0.35), 0.75)
    tap = 0.5 + 0.5 * math.sin(lt * 7)
    S['rook'].apply(P('sit', aR=(1.2, 0.0, 2.2 + 0.25 * tap, 0.5), aL=(0.6, 0.0, 1.3, 0.8), head=(0.0, 0.25)))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(-1.4, -0.6, k), lerp(-8.2, -7.4, k), 2.5), A(-0.6, 0.3, 2.1), 30, fcol='FFE8D0')


def wait_dusk(S, k, t, lt):
    """Late light. He is on his feet, looking up the ridge for someone who is not coming; cloud climbs behind him."""
    A = env(S, 'ridge', '7A86A8', sun=1.7, sunc='FFB080', sdir=(-0.85, -0.2, 0.2), fk=2.0, skyk=0.85)
    S['ridge']['storm'].location = (lerp(60, 20, k), lerp(-330, -240, k), lerp(-150, -110, k))
    S['beck'].place(A(-1.0, 0.8, 0), PI - 0.2)
    S['beck'].apply(P('stand', aL=(0.6, 0.3, 1.6, 0.6), aR=(0.2, 0.3, 0.5), head=(-0.3, 0.25 * math.sin(lt * 1.4))))
    S['face']['beck'] = 'squint'
    S['rook'].place(A(1.5, 0.3, 0), PI + 0.35)
    S['rook'].apply(P('hat', head=(-0.32, -0.2), lean=-0.05))
    S['face']['rook'] = 'calm'
    c = rp(lerp(8.5, 7.5, k), 2.2)
    cam(S, A(c[0], c[1], c[2] + 2.4), A(0.1, 0.4, 2.2), 30, fcol='FFD0B0')


def lead_high(S, k, t, lt):
    """Far up the ridge one small figure, alone, and the cloud closing over him. Seen from a long way off."""
    A = env(S, 'ridge', lerp_col('8A98BC', '56607E', k), sun=lerp(1.5, 0.7, k), sunc='D8E0F4', sdir=(-0.7, -0.3, 0.4), fk=2.4, skyk=0.8)
    d = 62.0 - lt * 0.5
    S['lead'].place(A(*rp(d)), 0.0)
    S['lead'].apply(blend(wind_walk(lt, 0.7), BRACE, 0.5 + 0.5 * k))
    vis(S['lead'].extra['mask'], True)
    p = rp(d)
    S['ridge']['storm'].location = (lerp(-440, -340, ease(k)), p[1] + lerp(40, 10, ease(k)), p[2] + lerp(30, 10, ease(k)))
    c = rp(lerp(36, 40, k), lerp(19, 16, k))
    cam(S, A(c[0], c[1], c[2] + lerp(7.0, 9.0, k)), A(p[0], p[1] - 1.0, p[2] + 2.2), lerp(50, 62, k), fcol='C8D4F0')


def lerp_col(a, b, k):
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(lerp(x, y, k)):02X}' for x, y in zip(ca, cb))


def rook_up(S, k, t, lt):
    """Rook on the empty ledge, hat to his chest, looking up at where the leader went."""
    A = env(S, 'ridge', '465270', sun=0.7, sunc='C0CCF0', sdir=(-0.6, -0.3, 0.45), fk=3.0, skyk=0.8)
    S['ridge']['storm'].location = (0, lerp(-460, -420, k), -170)
    S['rook'].place(A(0.4, 0.6, 0), 0.3)
    S['hat_off'] = ease(lt / 0.5)
    S['rook'].apply(blend(P('stand', head=(-0.3, 0.0)), hat_hold(head=(-0.36, 0.25)), lt / 0.5))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(2.6, 1.9, k), lerp(-5.2, -4.6, k), lerp(1.9, 2.2, k)), A(0.3, 0.6, 2.5), 40, fcol='C8D4F0')


# ---------------------------------------------------------------- new shots: the night on the saddle
HUD_ = (-16.0, -12.0)                       # where the group goes round in circles (same place as lost_group)


def tents_near(S, k, t, lt):
    """From among the tents: the camp light in front, and out in the dark the small glow of the lost group."""
    A = col(S, 'night')
    cx, cy = CAMP[0] - 21.0, CAMP[1] - 23.0
    for j, who in enumerate(('c1', 'c2', 'c3', 'beck')):
        a = j * 1.57 + lt * 0.4
        p = (cx + 2.0 * math.cos(a), cy + 2.0 * math.sin(a), 0)
        S[who].place(A(*p), a + PI / 2)
        S[who].apply(wind_walk(lt + j * 0.3, 1.0))
    S['glow'].location = A(cx, cy, 3.2)
    S['glow'].data.energy = 3200 + 900 * math.sin(lt * 9)
    S['glow'].data.color = K.hexc('CFE0FF')[:3]
    rp_ = (CAMP[0] - 5.0, CAMP[1] - 4.2, 0)
    S['rook'].place(A(*rp_), facing(rp_, (CAMP[0] - 1.5, CAMP[1] + 4.5, 0)) + 0.45)
    jerk = 0.5 + 0.5 * math.sin(lt * 5)
    S['rook'].apply(P('stand', aL=(2.5, 0.35, 2.0 - 0.6 * jerk, 0.3), aR=(0.2, 1.9, 1.6, -1.5), head=(0.05, 0.45), lean=0.18, lL=(0.3, 0.1), lR=(-0.25, 0.25)))
    S['hat_tip'] = 0.5
    S['face']['rook'] = 'deadpan'
    cam(S, A(CAMP[0] - lerp(0.6, 1.4, k), CAMP[1] + lerp(4.6, 3.8, k), lerp(3.6, 3.3, k)), A(CAMP[0] - 7.5, CAMP[1] - 8.0, 1.9), 30, fcol='9FB4F0')


def huddle(S, k, t, lt):
    """The group gives up circling and crouches together with their backs to the wind."""
    A = col(S, 'night')
    cx, cy = HUD_
    for j, (who, dx, dy, yw) in enumerate((('c1', -1.3, 0.5, 0.5), ('c2', 0.0, 0.9, 0.0), ('c3', 1.3, 0.5, -0.5))):
        S[who].place(A(cx + dx, cy + dy, 0.3), yw + 0.05 * math.sin(lt * 7 + j))
        S[who].apply(P('sit', lean=0.5 + 0.05 * math.sin(lt * 8 + j), head=(0.55, 0.0), aL=(0.9, -0.1, 1.9, 1.2), aR=(0.9, -0.1, 1.9, 1.2)))
    S['beck'].place(A(cx + 0.2, cy - 1.0, 0.3), 0.15)
    S['beck'].apply(P('sit', lean=0.6, head=(0.6, 0.0), aL=(0.9, -0.1, 1.9, 1.2), aR=(0.9, -0.1, 1.9, 1.2)))
    S['face']['beck'] = 'shut'
    vis(S['beck'].extra['frost'], True)
    S['glow'].location = A(cx + 2.5, cy - 3.0, 3.0)
    S['glow'].data.energy = 2300 + 500 * math.sin(lt * 9)
    S['glow'].data.color = K.hexc('CFE0FF')[:3]
    cam(S, A(cx + lerp(4.2, 3.2, k), cy - lerp(6.2, 5.2, k), lerp(1.5, 1.9, k)), A(cx + 0.1, cy, 1.25), 30, fcol='9FB4F0')


def rook_hat(S, k, t, lt):
    """The wind gets under Rook's hat; he clamps it down with both hands and is pushed back a step."""
    A = col(S, 'night')
    cx, cy = HUD_
    x0 = cx + 7.0 + 1.2 * ease(lt / 1.2)
    rp_ = (x0, cy - 2.0, 0)
    grab = ease((lt - 0.25) / 0.2)
    S['rook'].place(A(*rp_), 0.35, 0.0, -0.12 * grab)
    S['rook'].apply(blend(P('stand', **ALARM), P('stand', aL=(0.2, 1.9, 1.7, -1.5), aR=(0.2, 1.9, 1.7, -1.5), lean=0.4, head=(0.25, 0.0), lL=(0.45, 0.2), lR=(-0.35, 0.35)),
                          grab))
    S['hat_tip'] = lerp(-1.6, 0.9, grab)
    S['face']['rook'] = 'shocked' if grab < 0.6 else 'deadpan'
    feather(S, A(rp_[0] + 0.3, rp_[1] - 0.3, 3.3), lt, 0.05, 3)
    S['glow'].location = A(x0 - 1.5, cy - 4.5, 3.0)
    S['glow'].data.energy = 2600
    S['glow'].data.color = K.hexc('CFE0FF')[:3]
    cam(S, A(x0 + lerp(-1.6, -1.0, k), cy - lerp(7.0, 6.2, k), 1.5), A(x0 + 0.1, cy - 2.0, 2.45), 32, fcol='9FB4F0')


def wander(S, k, t, lt):
    """The other account of that night: he gets to his feet and walks off alone into the storm, arms out in front of him."""
    A = col(S, 'night')
    cx, cy = HUD_
    p = (cx + 6.0 + lt * 0.9, cy + 5.0 + lt * 0.5, 0)
    S['beck'].place(A(*p), facing(p, (p[0] + 1.0, p[1] + 0.55, 0)) + 0.25 * math.sin(lt * 2.2))
    w = walk(lt, 0.8)
    w.update(aL=(1.2, 0.4, 0.4), aR=(1.0, 0.5, 0.5), lean=0.3, head=(0.2, 0.3 * math.sin(lt * 1.7)))
    S['beck'].apply(w)
    vis(S['beck'].extra['frost'], True)
    S['face']['beck'] = 'squint'
    S['glow'].location = A(p[0] - 3.0, p[1] - 4.0, 3.0)
    S['glow'].data.energy = 2000
    S['glow'].data.color = K.hexc('CFE0FF')[:3]
    cam(S, A(p[0] + lerp(5.5, 4.5, k), p[1] - lerp(4.5, 3.6, k), lerp(1.4, 1.8, k)), A(p[0] + 0.5, p[1] + 0.3, 2.0), 30, fcol='9FB4F0')


def breath_cu(S, k, t, lt):
    """Close on his iced face in the dawn light: a small cloud of breath, and another."""
    A = col(S, 'dawn')
    lie(S, A, pose=LOW)
    breath(S, A, lt * 1.3)
    S['puff'].scale = tuple(0.55 * v for v in S['puff'].scale)
    hp = headpos()
    cam(S, A(lerp(1.5, 1.1, k), lerp(3.9, 3.6, k), lerp(1.9, 1.7, k)), A(hp[0], hp[1] - 0.25, hp[2] + 0.1), 46, fcol='FFD8C8')


def rook_two(S, k, t, lt):
    """Rook alone at dawn, hat to his chest, head bowed. Nothing else is shown."""
    A = col(S, 'dawn')
    rp_ = (-14.0, 9.0, 0.0)
    S['rook'].place(A(*rp_), 0.5)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.42 + 0.03 * math.sin(lt * 1.5), 0.0)))
    S['face']['rook'] = 'sad' if (lt * 0.35) % 1 > 0.2 else 'shut'
    cam(S, A(rp_[0] + lerp(2.6, 1.9, k), rp_[1] - lerp(5.0, 4.4, k), lerp(1.6, 1.9, k)), A(rp_[0] - 0.3, rp_[1], 2.3), 40, fcol='FFD8C8')


# ---------------------------------------------------------------- new shots: the news
def radio_tent(S, k, t, lt):
    """The radio tent below the mountain: the operator listens, lowers the handset, and his head goes down."""
    A = env(S, 'radio', '6E7A4E', fk=2.2, skyk=0.6)
    Rd = S['radio']
    tint(Rd['dialm'], 'FF7A1A', 5.0 if (lt * 3) % 1 < 0.6 else 0.6)
    drop = ease((lt - 0.9) / 0.5)
    op = S['c1']
    op.place(A(3.6, 1.5, 0.42), PI / 2)
    listen = P('sit', aL=(0.6, 0.25, 2.3, 0.2), aR=(0.9, 0.0, 0.8, 0.3), head=(0.1, 0.0), lean=0.2)
    done = P('sit', aL=(0.9, 0.1, 0.7, 0.2), aR=(0.9, 0.0, 0.8, 0.3), head=(0.5, 0.0), lean=0.32)
    op.apply(blend(listen, done, drop))
    bare(S, 'c1', 'calm' if drop < 0.4 else 'sad')
    hs = Rd['handset']
    hs.parent = op.el[0]
    hs.location, hs.rotation_euler = (0, -0.05, -0.52), (0.3, 0, 0)
    rp_ = (0.2, 4.2, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (1.5, -3.0, 0)))
    off = ease((lt - 1.0) / 0.4)
    S['hat_off'] = off
    S['rook'].apply(blend(P('stand', head=(0.05, -0.6)), hat_hold(head=(0.25, -0.5)), off))
    S['face']['rook'] = 'calm' if off < 0.5 else 'sad'
    cam(S, A(lerp(-2.4, -1.4, k), lerp(-6.2, -5.4, k), lerp(2.7, 2.5, k)), A(2.9, 1.9, 2.1), 30, fcol='FFE4C8')


def room_after(S, k, t, lt):
    """After the call: she sits in the armchair by the dark window, the lamp on, her hands in her lap."""
    A = room(S, True)
    w = S['wife']
    w.place(A(3.25, 3.95, 0.72), -0.35)
    w.apply(P('sit', aL=(0.75, -0.1, 1.5, 1.0), aR=(0.75, -0.1, 1.5, 1.0), head=(0.5 + 0.03 * math.sin(lt * 2), 0.25), lean=0.34))
    S['face']['wife'] = 'shut' if (lt * 0.4) % 1 < 0.6 else 'sad'
    hs = S['room']['handset']
    hs.location = (-7.5, 3.0, 2.62)
    S['room']['lamp'].data.energy = 600
    cam(S, A(lerp(-1.6, -0.2, k), lerp(-3.4, -2.8, k), lerp(2.9, 2.7, k)), A(2.6, 3.9, 2.3), 32, fcol='FFE4C8')


# ---------------------------------------------------------------- new shots: the hours
def sundial(S, k, t, lt):
    """Rook plants a marker wand beside him and watches its shadow swing round: the morning going by."""
    A = env(S, 'col', '7FA6E0', sun=2.5, sunc='FFF4E0', sdir=(lerp(0.85, -0.85, k), -0.35, lerp(0.3, 0.6, math.sin(PI * k))), fk=1.4, skyk=1.0)
    lie(S, A)
    S['wand'].location = A(2.4, 2.2, 0)
    rp_ = (3.9, 0.9, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (1.0, 2.2, 0)) + 0.3)
    look = 0.5 + 0.5 * math.sin(lt * 2.2)
    S['rook'].apply(P('stand', aR=(1.0, 0.0, 1.5, 0.4), aL=(0.3, 0.2, 0.5), head=(lerp(0.35, -0.1, look), lerp(0.1, -0.5, look)), lean=0.1))
    S['face']['rook'] = 'deadpan'
    S['coin'].location = A(rp_[0] - 0.55, rp_[1] - 0.2, 2.25)
    S['coin'].rotation_euler = (1.2, 0.3, lt * 2)
    cam(S, A(lerp(4.6, 3.6, k), lerp(-6.6, -5.8, k), lerp(6.2, 5.4, k)), A(1.4, 1.6, 0.9), 28, fcol='FFF0DC')


def hand_look(S, k, t, lt):
    """He sits up in the snow and holds his bare right hand in front of his face. Rook points at it."""
    A = col(S, 'day')
    b = S['beck']
    b.place(A(0.0, 1.3, 0.25), 0.55)
    sh_ = 0.04 * math.sin(lt * 23)
    b.apply(P('sit', aL=(1.55 + sh_, 0.1, 1.15, 0.5), aR=(0.5, 0.3, 0.9, 0.3), head=(0.05, 0.3), lean=0.1, lL=(1.2, 1.0), lR=(1.35, 1.3)))
    frosted(S, 6)
    vis(S['crust'][:7], True)
    S['face']['beck'] = 'wide' if lt > 0.5 else 'tired'
    rp_ = (2.7, 0.2, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (0.0, 1.0, 0)) - 0.55)
    S['rook'].apply(P('point', aR=(1.25, -0.45, 0.1), head=(0.1, -0.45), lean=0.3, lL=(0.4, 0.5), lR=(-0.2, 0.5), lift=-0.2))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(-0.2, 0.4, k), lerp(-4.9, -4.3, k), lerp(1.5, 1.8, k)), A(1.2, 1.0, 1.75), 30, fcol='FFF0DC')


def camp_see(S, k, t, lt):
    """Over his shoulder: the tents ahead, and three climbers who have stopped what they were doing."""
    A = col(S, 'day')
    cx, cy = CAMP
    bp = (lerp(cx - 13.0, cx - 11.5, k), lerp(cy - 15.5, cy - 13.6, k), 0)
    to = (cx - 3.0, cy - 3.0, 0)
    S['beck'].place(A(*bp), facing(bp, to) + 0.1 * math.sin(lt * 4))
    w = walk(lt, 0.9)
    w.update(aL=(0.5, 0.2, 1.2, 0.0), aR=(0.25, 0.45, 0.4, 0.0), lean=0.2)
    S['beck'].apply(w)
    frosted(S)
    for j, (who, p) in enumerate((('c1', (cx - 6.0, cy - 6.5, 0)), ('c3', (cx - 2.0, cy - 8.0, 0)), ('c2', (cx - 9.0, cy - 4.0, 0)))):
        run_ = ease((lt - 0.5 - 0.2 * j) / 0.4)
        q = (lerp(p[0], lerp(p[0], bp[0], 0.25), run_), lerp(p[1], lerp(p[1], bp[1], 0.25), run_), 0)
        S[who].place(A(*q), facing(q, bp))
        S[who].apply(blend(P('stand', **ALARM), walk(lt + j * 0.3, 1.8), run_ * 0.8))
        bare(S, who, 'wide')
    cam(S, A(bp[0] - 2.4, bp[1] - 3.6, lerp(3.0, 3.3, k)), A(cx - 5.0, cy - 6.0, 1.8), 30, fcol='FFF0DC')


# ---------------------------------------------------------------- new shots: the night nobody expected him to survive
def tent_in(S, k, t, lt):
    """Two climbers, one at each arm, walk him to a tent. Rook holds the way open."""
    A = env(S, 'col', '6A86C0', sun=1.6, sunc='FFC89A', sdir=(-0.85, -0.3, 0.2), fk=2.0, skyk=0.9)
    cx, cy = CAMP
    y = lerp(cy - 7.0, cy - 4.4, k)
    for j, (who, dx) in enumerate((('c1', -1.0), ('beck', 0.0), ('c3', 1.0))):
        p = (cx + 0.6 + dx, y - (0.0 if who == 'beck' else 0.25), 0)
        S[who].place(A(*p), PI + 0.5 - 0.25 * dx)
        if who == 'beck':
            w = walk(lt, 0.8)
            w.update(aL=(0.9, 0.5, 0.6), aR=(0.9, 0.5, 0.6), lean=0.22, head=(0.25, 0.0))
            S[who].apply(w)
        else:
            w = walk(lt + 0.2 * j, 0.8)
            w.update(aL=(0.9, 0.3, 0.5) if dx > 0 else w['aL'], aR=(0.9, 0.3, 0.5) if dx < 0 else w['aR'], head=(0.1, 0.5 * dx))
            S[who].apply(w)
            bare(S, who)
    frosted(S)
    S['face']['beck'] = 'tired'
    rp_ = (cx - 2.8, cy - 4.4, 0)
    S['rook'].place(A(*rp_), facing(rp_, (cx - 7, cy - 9, 0)) + 0.3)
    S['rook'].apply(P('stand', aR=(0.5, 1.3 + 0.1 * math.sin(lt * 4), 0.2), aL=(0.2, 0.2, 0.4), head=(0.05, -0.5), lean=0.1))
    S['face']['rook'] = 'calm'
    cam(S, A(cx - lerp(7.4, 6.4, k), cy - lerp(9.2, 8.4, k), 2.0), A(cx + 0.9, cy - 4.2, 1.9), 30, fcol='FFE0C8')


def tent_out(S, k, t, lt):
    """Night. One tent glows from inside among the dark ones; Rook sits outside it in the wind, hat in his lap."""
    A = col(S, 'night')
    S['col']['camp'].data.energy = 2500
    cx, cy = CAMP
    S['glow'].location = A(cx, cy - 2.6, 1.3)
    S['glow'].data.energy = 2600 + 400 * math.sin(lt * 6)
    S['glow'].data.color = K.hexc('FFB060')[:3]
    rp_ = (cx - 3.2, cy - 4.2, 0.0)
    S['rook'].place(A(rp_[0], rp_[1], 0.3), facing(rp_, (cx - 9, cy - 11, 0)) - 0.2)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.3, 0.5 * ease((lt - 0.6) / 0.6))))
    S['face']['rook'] = 'sad'
    cam(S, A(cx - lerp(9.5, 8.0, k), cy - lerp(11.5, 10.2, k), lerp(1.5, 1.9, k)), A(cx - 1.4, cy - 2.6, 1.7), 30, fcol='9FB4F0')


def dawn_camp(S, k, t, lt):
    """Morning. A climber bends to the tent door, looks in, and spins round with his arms out. Rook jerks a thumb at the tent."""
    A = col(S, 'dawn')
    cx, cy = CAMP
    turn = ease((lt - 0.7) / 0.3)
    p = (cx + 0.5, cy - 3.3, 0)
    S['c1'].place(A(*p), lerp(PI, 0.45, turn))
    S['c1'].apply(blend(P('stand', lean=0.6, head=(-0.1, 0.0), aL=(0.9, 0.2, 0.6), lL=(0.3, 0.5), lR=(0.2, 0.5), lift=-0.2), P('stand', **ALARM), turn))
    bare(S, 'c1', 'calm' if turn < 0.5 else 'wide')
    S['jaw']['c1'] = 0.3 * turn
    q = (cx + 6.4, cy - 6.6, 0)
    S['c3'].place(A(*q), facing(q, p))
    S['c3'].apply(blend(P('stand'), walk(lt, 1.7), ease((lt - 1.0) / 0.3)))
    bare(S, 'c3', 'wide' if turn > 0.6 else 'calm')
    rp_ = (cx + 3.3, cy - 4.4, 0)
    S['rook'].place(A(*rp_), facing(rp_, (cx - 6, cy - 9, 0)) + 0.15)
    th = ease((lt - 0.9) / 0.25)
    S['rook'].apply(blend(P('cross'), P('stand', aL=(2.4, 0.5, 2.1 - 0.5 * math.sin(lt * 9) ** 2, 0.3), aR=(0.3, 0.3, 0.9), head=(-0.05, 0.3)), th))
    S['face']['rook'] = 'warm' if th > 0.5 else 'deadpan'
    cam(S, A(cx - lerp(5.6, 4.8, k), cy - lerp(9.6, 8.8, k), 1.9), A(cx + 0.9, cy - 3.6, 2.0), 30, fcol='FFD8C8')


# ---------------------------------------------------------------- new shots: the descent on foot
def face(S):
    return env(S, 'face', '6FA0E0', sun=2.6, sunc='FFF4E4', sdir=(0.55, -0.6, 0.5), fk=1.4, skyk=1.0)


def party(S, A, d, lt, low=True):
    """Three on the fixed rope coming down the fall line: a helper above, Weathers, a helper below."""
    for j, (who, dd, x) in enumerate((('c1', 2.3, 0.2), ('beck', 0.0, 0.4), ('c3', -2.5, 0.1))):
        if who == 'c3' and not low:
            continue
        p = fp(d + dd, x)
        S[who].place(A(*p), 0.0)
        w = walk(lt + 0.33 * j, 0.75)
        if who == 'beck':
            w.update(aL=(0.9, 0.35, 0.7), aR=(0.9, 0.35, 0.7), lean=-0.05, head=(0.2, 0.0))
        elif dd > 0:
            w.update(aR=(1.2, 0.0, 0.3), aL=(1.2, 0.0, 0.3), lean=0.1, head=(0.3, 0.0))
        else:
            w.update(head=(-0.2, 0.9 * math.sin(lt * 1.5) ** 2), lean=-0.1)
            S[who].place(A(*p), 0.5)
        S[who].apply(w)
        if who != 'beck':
            bare(S, who)
    frosted(S)
    S['face']['beck'] = 'tired'
    a, b = fp(d + 2.3, 0.2), fp(d, 0.4)
    seg(S['rope'], A(a[0], a[1] - 0.35, a[2] + 1.5), A(b[0], b[1] + 0.3, b[2] + 1.5), 0.035)


def face_down(S, k, t, lt):
    """Wide: the ice face, the orange line of the rope, and three small figures picking their way down it."""
    A = face(S)
    d = 6.0 - lt * 0.9
    party(S, A, d, lt)
    c, m = fp(d - 9, lerp(17, 14, k)), fp(d + 0.5, 0)
    cam(S, A(c[0], c[1], c[2] + 5.0), A(m[0], m[1], m[2] + 2.4), 28, fcol='E4ECFF')


def face_cu(S, k, t, lt):
    """Close, from below: his frozen arms held out in front of him, a hand on his pack, and Rook coming down beside him."""
    A = face(S)
    d = -12.0 - lt * 0.9
    party(S, A, d, lt, low=False)
    rp_ = fp(d - 0.6, 2.6)
    S['rook'].place(A(*rp_), 0.3)
    w = walk(lt + 0.5, 0.75)
    w.update(aR=(0.2, 1.9, 1.6, -1.5), head=(0.1, 0.75), lean=-0.05)
    S['rook'].apply(w)
    S['face']['rook'] = 'calm'
    c, m = fp(d - 6.2, lerp(2.4, 1.6, k)), fp(d, 1.2)
    cam(S, A(c[0], c[1], c[2] + 1.3), A(m[0], m[1], m[2] + 2.0), 30, fcol='E4ECFF')


def lowcamp(S, k, t, lt):
    """The lower camp: he sits on a crate with his arms in his lap, someone holds a mug to his mouth, Rook scans the sky."""
    A = env(S, 'low', '6F9CDC', sun=2.5, sunc='FFF4E4', sdir=(-0.5, -0.6, 0.55), fk=1.5, skyk=1.0)
    b = S['beck']
    b.place(A(0.0, 0.3, 0.42), 0.15)
    b.apply(P('sit', aL=(0.7, 0.0, 1.2, 0.6), aR=(0.7, 0.0, 1.2, 0.6), head=(0.1, 0.3), lean=0.15))
    frosted(S, 0)
    S['face']['beck'] = 'tired'
    hp_ = (-2.0, -0.2, 0)
    S['c3'].place(A(*hp_), facing(hp_, (0, 0.3, 0)))
    S['c3'].apply(blend(KNEEL, P('stand', lL=(0.25, 1.55), lR=(1.35, 1.5), lift=-0.78, lean=0.25, aR=(1.25, -0.2, 0.7, 0.2), aL=(0.4, 0.1, 0.6), head=(-0.05, 0.0)), 1.0))
    bare(S, 'c3')
    S['mug'].location = A(-0.75, -0.3, 2.05 + 0.04 * math.sin(lt * 3))
    rp_ = (3.2, 1.0, 0)
    S['rook'].place(A(*rp_), 0.5)
    scan = math.sin(lt * 1.4)
    S['rook'].apply(P('hat', head=(-0.4, 0.5 * scan), lean=-0.08))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(1.6, 0.6, k), lerp(-7.6, -6.8, k), lerp(2.2, 2.5, k)), A(0.5, 0.4, 2.0), 30, fcol='FFF4E4')


# ---------------------------------------------------------------- new shots: the helicopter
def cockpit(S, k, t, lt):
    """Inside the cabin, looking back from the nose: the pilot at the stick, peaks sliding by, Rook in the other seat
    holding his hat on with both hands."""
    A = env(S, 'pit', '79A8E8', sun=2.6, sunc='FFF4E4', sdir=(0.5, -0.55, 0.6), fk=2.4, skyk=1.0)
    Pt = S['pit']
    Pt['world'].location = (4 * math.sin(lt * 0.8), 40 + lt * 34, 6 * math.sin(lt * 0.6))
    Pt['world'].rotation_euler = (0.03 * math.sin(lt * 1.7), 0.05 * math.sin(lt * 1.3), 0)
    tint(Pt['warnm'], 'FFB000', 6.0 if (lt * 2.5) % 1 < 0.5 else 0.3)
    pl = S['pilot']
    pl.place(A(-1.05, 0.75, 0.55), 0.0)
    pl.apply(P('sit', aL=(0.95, 0.05, 0.75 + 0.06 * math.sin(lt * 5), 0.3), aR=(0.75, 0.2, 0.9, 0.2), head=(0.02, 0.3 * math.sin(lt * 1.1)), lean=0.12))
    S['face']['pilot'] = 'squint'
    S['rook'].place(A(1.05, 0.75, 0.55), 0.0)
    S['rook'].apply(P('sit', aL=(0.2, 1.9, 1.7, -1.5), aR=(0.2, 1.9, 1.7, -1.5), head=(0.05, -0.35 + 0.3 * math.sin(lt * 2.3)), lean=0.1))
    S['hat_tip'] = 0.6
    S['face']['rook'] = 'shocked'
    sway = 0.08 * math.sin(lt * 2.1)
    cam(S, A(lerp(0.9, 0.3, k) + sway, lerp(-5.4, -4.8, k), 2.95 + 0.05 * math.sin(lt * 3.3)), A(0.0, 0.8, 2.25), 30, roll=0.03 * math.sin(lt * 1.9), fcol='FFF0DC')


def heli_skid(S, k, t, lt):
    """Low on the snow: the skids come down between the marker wands, and the air fills with blown snow."""
    A = cwm(S)
    e = ease(k)
    heli(S, A, (0.0, 13.5, lerp(3.4, 0.3, e)), t, yaw=0.5, roll=0.06 * math.sin(lt * 6) * (1 - e))
    rp_ = (-6.4, 7.6, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (-9.0, 1.5, 0)) - 0.45)
    S['rook'].apply(P('stand', aL=(0.2, 1.9, 1.7, -1.5), aR=(0.2, 1.9, 1.7, -1.5), lean=0.35, head=(0.1, -0.7), lL=(0.4, 0.3), lR=(-0.3, 0.4)))
    S['hat_tip'] = 0.8
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-9.5, -8.5, k), lerp(1.0, 2.0, k), lerp(0.9, 1.2, k)), A(-1.5, 12.0, lerp(3.4, 2.4, e)), 26, fcol='FFF4E4')


def heli_load(S, k, t, lt):
    """Two climbers walk him to the helicopter's side under the turning rotor."""
    A = cwm(S)
    heli(S, A, (0.0, 13.5, 0.3), t, yaw=0.5)
    for j, (who, dx) in enumerate((('c1', -1.0), ('beck', 0.0), ('c3', 1.0))):
        u = lerp(0.0, 3.0, k)
        p = (-6.5 + u + dx * 0.55, 8.0 + u * 0.75 - abs(dx) * 0.3 + dx * 0.5, 0)
        S[who].place(A(*p), facing(p, (-1.5, 12.5, 0)))
        w = walk(lt + 0.2 * j, 0.9)
        w['lean'] = 0.3
        if who == 'beck':
            w.update(aL=(0.9, 0.4, 0.6), aR=(0.9, 0.4, 0.6), head=(0.3, 0.0))
        else:
            bare(S, who)
        S[who].apply(w)
    frosted(S, 0)
    S['face']['beck'] = 'tired'
    cam(S, A(lerp(-12.5, -11.5, k), lerp(3.2, 4.0, k), lerp(2.0, 2.3, k)), A(-2.6, 11.0, 2.3), 28, fcol='FFF4E4')


# ---------------------------------------------------------------- new shots: afterwards
def ward(S, k, t, lt):
    """A hospital room: he lies bandaged, she sits beside the bed, Rook stands at its foot with his hat off."""
    A = env(S, 'ward', '000000', fk=1.8)
    W_ = S['ward']
    for j, o in enumerate(W_['trace']):
        ph = (j / 8 - t * 0.9) % 1
        o.location.z = 5.2 + (0.42 if 0.4 < ph < 0.5 else -0.2 if 0.5 <= ph < 0.58 else 0.0)
    b = S['beckh']
    b.place(A(-1.5, 2.7, 1.95), 0.0, -PI / 2 + 0.42)
    b.apply(P('stand', aL=(0.55, 0.25, 0.5, 0.3), aR=(0.55, 0.25, 0.5, 0.3), head=(0.35, -0.5 * ease(lt / 1.0))))
    S['face']['beckh'] = 'tired' if lt < 0.9 else 'warm'
    w = S['wife']
    w.place(A(1.0, 3.9, 0.72), -PI / 2 + 0.3)
    w.apply(P('sit', aL=(1.0, 0.1, 0.5, 0.2), aR=(0.75, -0.1, 1.5, 1.0), head=(0.2, 0.0), lean=0.4))
    S['face']['wife'] = 'warm'
    rp_ = (-4.0, 2.6, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (1.5, -3.0, 0)) - 0.2)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.15, -0.75)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(2.4, 1.8, k), lerp(-0.6, 0.0, k), lerp(3.7, 3.4, k)), A(-1.5, 4.7, 2.2), 28, fcol='F0F6FF')


def desk_write(S, k, t, lt):
    """Night in a study. He sits at a desk in the light of a screen; Rook lifts the finished book off the pile and looks at it."""
    A = env(S, 'study', '000000', fk=2.0)
    St = S['study']
    tint(St['screenm'], 'CFE8FF', 2.0 + 0.5 * math.sin(lt * 13))
    b = S['beckh']
    b.place(A(0.3, 2.05, 0.72), 0.0)
    b.apply(P('sit', aL=(0.95, 0.15, 0.9, 0.5), aR=(0.95, 0.1, 0.9 + 0.1 * math.sin(lt * 9), 0.4), head=(0.2, -0.4 + 0.25 * ease((lt - 0.9) / 0.5)), lean=0.2))
    S['face']['beckh'] = 'warm'
    rp_ = (-4.6, -0.9, 0.0)
    S['rook'].place(A(*rp_), 0.75)
    up = ease((lt - 0.3) / 0.5)
    S['rook'].apply(blend(P('stand', aR=(0.9, 0.2, 0.3), head=(0.25, -0.4)), P('stand', aR=(0.75, -0.1, 1.2, 0.3), aL=(0.4, 0.2, 0.6), head=(0.35, -0.3)), up))
    S['face']['rook'] = 'warm'
    a, c = (-2.6, -0.3, 1.82), (-3.55, -1.25, 1.95)
    bk_ = S['book']
    bk_.location = A(*[lerp(a[i], c[i], up) for i in range(3)])
    bk_.location.z += 0.3 * math.sin(PI * up)
    bk_.rotation_euler = (lerp(0, 0.75, up), 0, lerp(0.2, 0.9, up))
    cam(S, A(lerp(-1.0, -1.9, k), lerp(-6.8, -6.0, k), lerp(3.0, 2.8, k)), A(-1.3, 0.8, 2.25), 30, fcol='FFE8D0')


def cairn_stone(S, k, t, lt):
    """Dusk at the cairn. Rook sets one flat stone on top of the pile and takes his hat off."""
    A = env(S, 'base', '56609A', sun=1.2, sunc='FFA070', sdir=(0.6, 0.6, 0.22), fk=4.2, skyk=0.85)
    flutter(S, t)
    rp_ = (4.3, -0.9, 0.0)
    S['rook'].place(A(*rp_), facing(rp_, (CAIRN[0], CAIRN[1], 0)) + 0.45)
    put = ease(lt / 0.9)
    off = ease((lt - 1.1) / 0.5)
    S['hat_off'] = off
    S['rook'].apply(blend(blend(P('stand', aL=(0.7, 0.2, 1.2), head=(0.2, -0.3)), P('stand', aL=(1.9, 0.1, 0.25), head=(-0.1, -0.3)), put), hat_hold(head=(0.35, -0.3)), off))
    S['face']['rook'] = 'sad'
    a, b = (3.9, -0.3, 2.2), (CAIRN[0] + 0.1, CAIRN[1] - 0.15, 4.72)
    S['stone'].location = A(*[lerp(a[i], b[i], put) for i in range(3)])
    S['stone'].rotation_euler = (0, 0, 0.8)
    cam(S, A(lerp(9.0, 8.0, k), lerp(5.6, 4.8, k), lerp(2.2, 2.6, k)), A(3.0, 0.2, 2.7), 30, fcol='FFD8C8')


def flags_cu(S, k, t, lt):
    """Up along a string of plain coloured flags to the mountain, the last light on its top."""
    A = env(S, 'base', '6A6EA8', sun=1.5, sunc='FFA878', sdir=(-0.8, -0.45, 0.14), fk=2.2, skyk=0.85)
    flutter(S, t)
    cam(S, A(lerp(7.5, 6.0, k), lerp(-6.5, -5.2, k), lerp(1.1, 1.6, k)), A(-3.0, 30, lerp(11, 14, k)), 34, fcol='FFD8C8')


HOST |= {'team_base', 'lead_tells', 'wait_dusk', 'rook_up', 'tents_near', 'rook_hat', 'rook_two', 'radio_tent', 'sundial', 'hand_look',
         'tent_in', 'tent_out', 'dawn_camp', 'face_cu', 'lowcamp', 'cockpit', 'heli_skid', 'ward', 'desk_write', 'cairn_stone'}
SHOTS3D.update({f.__name__: f for f in (
    team_base, eye_cu, lead_tells, wait_dusk, lead_high, rook_up, tents_near, huddle, rook_hat, wander, breath_cu, rook_two, radio_tent, room_after,
    sundial, hand_look, camp_see, tent_in, tent_out, dawn_camp, face_down, face_cu, lowcamp, cockpit, heli_skid, heli_load, ward, desk_write,
    cairn_stone, flags_cu)})


def _orbit(f):
    """prm "orb": [degrees, dolly, rise] swings the camera round its own look-at point over the length of the shot,
    so a held shot is never a still picture."""
    def g(S, k, t, lt):
        f(S, k, t, lt)
        o = S['prm'].get('orb')
        if o:
            deg, dolly, rise = (list(o) + [0, 0])[:3]
            c, tg = S['camrig'].location, S['camtgt'].location
            a = math.radians(deg) * (k - 0.5)
            m = 1 - dolly * (k - 0.5)
            dx, dy = c[0] - tg[0], c[1] - tg[1]
            S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m,
                                    c[2] + rise * (k - 0.5))
    g.__name__ = f.__name__
    return g


SHOTS3D = {name: _orbit(f) for name, f in SHOTS3D.items()}


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: on the left of the frame he gets up out of the snow, iced over, his frozen hand raised; Rook
    beside him throws his arms out. The right of the frame is left to the sky for the words."""
    A = col(S, 'day')
    bp = (0.0, 1.2, 0.0)
    S['beck'].place(A(*bp), 0.35, -0.1)
    S['beck'].apply(P('stand', lean=0.2, aL=(1.9, 0.35, 0.9, 0.2), aR=(0.4, 0.4, 0.8), lL=(0.35, 0.5), lR=(-0.1, 0.35), head=(-0.05, 0.2), lift=-0.12))
    frosted(S, 8)
    vis(S['crust'][:9], True)
    S['face']['beck'] = 'wide'
    rp_ = (-2.5, 2.0, 0.0)
    S['rook'].place(A(*rp_), -0.15)
    S['rook'].apply(P('stand', **{**ALARM, 'head': (-0.05, -0.45)}))
    S['face']['rook'] = 'shocked'
    cam(S, A(2.3, -3.6, 1.7), A(0.3, 1.4, 2.35), 30, fill=1.3, fcol='FFF0DC')


STILLS['thumb'] = photo_thumb
