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
