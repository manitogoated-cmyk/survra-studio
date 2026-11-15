"""Case 011 in 3D - Roy Sullivan, the Shenandoah park ranger struck by lightning seven times (1942 to 1977).
Sets built for this story only: a mountain ridge with a wooden fire lookout tower, a park road with a ranger's
pickup and a timber gate, a front yard with a power pole, the inside of a ranger station, a fishing pond with a
jetty, and a small exhibit hall with two hats in a case.

Nothing here is a model of a real place: the tower, road, house, station, pond and hall are generic. No badge,
logo or agency marking is shown anywhere."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(ridge=(0, 0, 0), road=(500, 0, 0), yard=(1000, 0, 0), station=(1500, 0, 0), pond=(2000, 0, 0), hall=(2500, 0, 0))
FAR = (0, 0, -900)
HOST = {'rook_gate', 'rook_collar', 'roy_tower', 'tower_hit', 'roy_runs', 'rook_truck', 'yard_hit', 'station_in', 'rook_desk',
        'station_hit', 'patrol_hit', 'rook_can', 'roy_hop', 'pond_wide', 'pond_hit', 'roy_burns', 'rook_tally', 'rook_shock',
        'hats_case', 'rook_hats', 'rook_wrong', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'E2B48C'
ROY = dict(top='A7A88C', pants='44563C', hand=SKIN, boot='2A2420')
HATC, BAND = '8A7450', '3A2E22'
_MOV = []


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


def mix_col(a, b, k):
    k = max(0.0, min(1.0, k))
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


def rnd(i, j=0):
    """Repeatable pseudo-random number 0..1."""
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def pine(r, x, y, s=1.0, col=0):
    c = ('1F3A2C', '274634', '1A3226')[col % 3]
    add('cylinder', '3A2A1E', (x, y, 1.2 * s), radius=0.28 * s, depth=2.4 * s, vertices=5, parent=r)
    for j in range(3):
        add('cone', c, (x, y, (3.2 + j * 2.1) * s), radius1=(2.4 - j * 0.6) * s, radius2=0.0, depth=3.4 * s, vertices=6, parent=r)


def ridges(r, y0, cols, n=11, span=700, hgt=70):
    for row, c in enumerate(cols):
        for i in range(n):
            x = -span / 2 + span * i / (n - 1) + rnd(i, row) * 30
            hh = hgt * (0.6 + 0.6 * rnd(i, row + 5)) * (1 + row * 0.35)
            add('cone', c, (x, y0 + row * 110, hh / 2 - 6), radius1=85 + 40 * rnd(i, row + 9), radius2=6, depth=hh, vertices=6, parent=r)


# ---------------------------------------------------------------- set 1: the ridge and the fire lookout tower
def set_ridge(r):
    add('plane', '24382A', (0, 0, -0.02), size=3000, parent=r)
    add('cube', '5A4E3A', (-3, -4, 0.02), scale=(2.2, 60, 0.05), size=1, parent=r)          # the trail
    for i in range(46):
        x = (rnd(i, 1) - 0.5) * 110
        y = -24 + rnd(i, 2) * 110
        if (abs(x + 1) < 7.5 and y < 24) or (4 < x < 20 and y < 4):
            continue
        pine(r, x, y, 0.8 + rnd(i, 3) * 0.9, i)
    for i in range(9):
        add('ico_sphere', ('4A4A48', '5A5852')[i % 2], ((rnd(i, 7) - 0.5) * 30, -6 + rnd(i, 8) * 30, 0.2), scale=(1.4, 1, 0.6),
            radius=0.5 + rnd(i, 9), subdivisions=1, parent=r)
    ridges(r, 170, ('2A3E4E', '34485A', '40566A'))
    tw = empty((0, 14, 0), r)                                                               # the tower
    wood, dark = '6A5236', '4A3826'
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', wood, (sx * 2.3, sy * 2.3, 4.6), rot=(sy * 0.035, -sx * 0.035, 0), radius=0.2, depth=9.3, vertices=6, parent=tw)
        for j in range(3):
            z = 1.6 + j * 2.9
            add('cube', dark, (sx * 2.3, 0, z), rot=(0.55 if j % 2 else -0.55, 0, 0), scale=(0.12, 5.4, 0.12), size=1, parent=tw)
            add('cube', dark, (0, sx * 2.3, z), rot=(0, 0.55 if j % 2 else -0.55, 0), scale=(5.4, 0.12, 0.12), size=1, parent=tw)
    add('cube', wood, (0, 0, 9.15), scale=(6.6, 6.6, 0.3), size=1, parent=tw)                # cab floor
    for sx in (-1, 1):
        add('cube', wood, (sx * 3.15, 0, 9.95), scale=(0.16, 6.4, 1.3), size=1, parent=tw)    # low walls
        add('cube', wood, (0, sx * 3.15, 9.95), scale=(6.4, 0.16, 1.3), size=1, parent=tw)
        for sy in (-1, 1):
            add('cube', dark, (sx * 3.15, sy * 3.15, 11.5), scale=(0.24, 0.24, 4.4), size=1, parent=tw)
        add('cube', dark, (sx * 3.15, 0, 13.6), scale=(0.2, 6.5, 0.2), size=1, parent=tw)
        add('cube', dark, (0, sx * 3.15, 13.6), scale=(6.5, 0.2, 0.2), size=1, parent=tw)
    add('cone', '3E4A44', (0, 0, 14.6), rot=(0, 0, PI / 4), radius1=5.4, radius2=0.0, depth=2.2, vertices=4, parent=tw)
    add('cube', dark, (0.9, 1.6, 9.9), scale=(1.5, 1.0, 1.2), size=1, parent=tw)              # map table inside
    for j in range(13):                                                                     # the stair on the east side
        u = j / 12
        add('cube', wood, (4.0, -5.6 + u * 7.4, 0.35 + u * 8.9), scale=(1.5, 0.75, 0.14), size=1, parent=tw)
    add('cube', dark, (4.75, -1.9, 5.7), rot=(math.atan2(8.9, 7.4), 0, 0), scale=(0.1, 11.6, 0.12), size=1, parent=tw)
    add('cube', dark, (3.25, -1.9, 4.8), rot=(math.atan2(8.9, 7.4), 0, 0), scale=(0.1, 11.6, 0.2), size=1, parent=tw)
    lampm = own_mat('cablamp', 'FFC070', 6.0)
    use(add('ico_sphere', 'FFC070', (0, 0, 13.25), radius=0.2, subdivisions=1, parent=tw), lampm)
    cab = light((0, 0, 12.9), 500, 'FFB868', kind='POINT', parent=tw)
    tgt = empty((0, 14, 4), r)
    moon = light((-60, -80, 120), 1.1, '8FA8D8', kind='SUN', target=tgt, parent=r)
    return dict(ridge_sun=moon, cablight=cab, cablampm=lampm)


# ---------------------------------------------------------------- set 2: the park road and the gate
def set_road(r):
    add('plane', '2A3A2C', (0, 0, -0.03), size=3000, parent=r)
    add('cube', '3C3C42', (0, 80, 0.02), scale=(9.0, 420, 0.06), size=1, parent=r)
    for i in range(40):                                                                     # worn centre line
        add('cube', '8A8468', (0, -40 + i * 7.0, 0.06), scale=(0.16, 2.6, 0.02), size=1, parent=r)
    for i in range(34):                                                                     # stone guard wall on the drop side
        y = -44 + i * 5.2
        add('cube', ('6A6860', '5C5A54')[i % 2], (5.4, y, 0.55), scale=(0.9, 3.4, 1.1), size=1, parent=r)
    add('cube', '1E2A24', (30, 80, -6), scale=(48, 420, 12), size=1, parent=r)               # the drop: dark valley floor
    for i in range(26):                                                                     # rock bank and pines on the hill side
        y = -46 + i * 7.2 + rnd(i, 4) * 3
        add('cube', ('4E4A44', '5A564E', '46423C')[i % 3], (-7.6 - rnd(i, 1) * 2, y, 1.4 + rnd(i, 2) * 1.5),
            rot=(rnd(i, 3) * 0.4, rnd(i, 5) * 0.4, rnd(i, 6)), scale=(4.5, 6.5, 3.6 + rnd(i, 2) * 2), size=1, parent=r)
        pine(r, -12.5 - rnd(i, 7) * 14, y + 2, 1.2 + rnd(i, 8) * 0.9, i)
        if i % 2:
            pine(r, 9.5 + rnd(i, 9) * 10, y, 0.9 + rnd(i, 10) * 0.5, i + 1)
    pine(r, 7.6, 12.5, 1.25, 1)                                                             # the tree the bolt comes through
    ridges(r, 190, ('2E4250', '3A4E5E', '485E70'), span=800)
    g = empty((0, -14, 0), r)                                                               # the timber gate
    for sx in (-1, 1):
        add('cylinder', '5A4630', (sx * 5.6, 0, 3.6), radius=0.42, depth=7.2, vertices=7, parent=g)
        add('cube', '6A6860', (sx * 5.6, 0, 0.5), scale=(1.5, 1.5, 1.0), size=1, parent=g)
    add('cube', '5A4630', (0, 0, 7.0), scale=(13.2, 0.55, 0.55), size=1, parent=g)
    add('cube', '6E5638', (0, 0, 5.75), scale=(5.4, 0.22, 1.5), size=1, parent=g)             # a blank sign board
    add('cube', 'FF7A1A', (0, -0.13, 5.2), scale=(5.0, 0.04, 0.16), size=1, parent=g, emit=0.4)
    for sx in (-1, 1):
        add('cube', '2A2A2A', (sx * 2.2, 0, 6.65), scale=(0.05, 0.05, 0.5), size=1, parent=g)
    tgt = empty((0, 6, 2), r)
    sun = light((-70, -60, 130), 1.6, '9AB0D0', kind='SUN', target=tgt, parent=r)
    return dict(road_sun=sun)


def make_truck():
    """A ranger's pickup of no particular make, nose toward -Y. No markings."""
    t = empty(FAR)
    body, dark, glassy = '2E5040', '1C2A24', '22262C'
    add('cube', body, (0, -2.75, 1.55), scale=(3.0, 2.7, 1.25), size=1, parent=t)             # hood
    add('cube', dark, (0, -4.15, 1.3), scale=(2.8, 0.14, 0.7), size=1, parent=t)              # grille
    add('cube', 'B8B8B0', (0, -4.25, 0.85), scale=(3.2, 0.2, 0.24), size=1, parent=t, rough=0.4)
    add('cube', body, (0, 0.5, 1.05), scale=(3.0, 9.0, 0.3), size=1, parent=t)                # floor
    for sx in (-1, 1):
        add('cube', body, (sx * 1.44, -0.2, 1.75), scale=(0.12, 2.4, 1.2), size=1, parent=t)  # doors (lower half)
        add('cube', body, (sx * 1.44, -1.34, 3.05), rot=(-0.22, 0, 0), scale=(0.14, 0.14, 1.6), size=1, parent=t)   # pillars
        add('cube', body, (sx * 1.44, 0.95, 3.1), scale=(0.14, 0.14, 1.5), size=1, parent=t)
        add('cube', body, (sx * 1.44, 2.6, 1.6), scale=(0.12, 3.2, 0.9), size=1, parent=t)    # bed sides
        add('cube', body, (sx * 1.5, -2.9, 1.0), scale=(0.4, 1.9, 0.6), size=1, parent=t)     # wings
        for y in (-2.9, 2.7):
            add('cylinder', '141416', (sx * 1.5, y, 0.72), rot=(0, PI / 2, 0), radius=0.72, depth=0.5, vertices=10, parent=t)
            add('cylinder', '8A8A84', (sx * 1.77, y, 0.72), rot=(0, PI / 2, 0), radius=0.3, depth=0.06, vertices=8, parent=t)
        add('ico_sphere', 'FFE8B0', (sx * 1.05, -4.2, 1.6), radius=0.26, subdivisions=1, parent=t, emit=8.0)
    add('cube', body, (0, 0.95, 2.0), scale=(3.0, 0.12, 1.7), size=1, parent=t)               # cab back wall
    add('cube', glassy, (0, 0.9, 3.0), scale=(2.4, 0.06, 0.8), size=1, parent=t)
    add('cube', body, (0, -0.2, 3.88), scale=(3.1, 2.6, 0.16), size=1, parent=t)              # roof
    add('cube', body, (0, 4.2, 1.6), scale=(3.0, 0.12, 0.9), size=1, parent=t)                # tailgate
    add('cube', dark, (0, 0.35, 1.4), scale=(2.6, 1.0, 0.4), size=1, parent=t)                # bench seat
    add('cube', dark, (0, 0.8, 2.1), scale=(2.6, 0.2, 1.1), size=1, parent=t)
    add('torus', dark, (0.65, -0.95, 2.35), rot=(1.1, 0, 0), major_radius=0.36, minor_radius=0.05, major_segments=10, minor_segments=4, parent=t)
    lamp = light((0, -0.2, 3.6), 0, 'FFE0B0', kind='POINT', parent=t)
    return t, lamp


# ---------------------------------------------------------------- set 3: his front yard
def set_yard(r):
    add('plane', '2E4A30', (0, 0, -0.02), size=3000, parent=r)
    add('cube', '8A8270', (1.5, 4.5, 0.02), rot=(0, 0, -0.62), scale=(1.5, 13.5, 0.05), size=1, parent=r)   # path to the mailbox
    add('cube', '4A4844', (8, -8, 0.02), scale=(120, 6, 0.05), size=1, parent=r)                          # the lane
    hs = empty((-4, 17, 0), r)
    add('cube', 'CFC8B2', (0, 0, 3.0), scale=(15, 9, 6), size=1, parent=hs)
    add('cube', '5A3A30', (0, -1.2, 7.3), rot=(0.62, 0, 0), scale=(16.4, 7.4, 0.3), size=1, parent=hs)
    add('cube', '4E322A', (0, 3.4, 7.0), rot=(-0.62, 0, 0), scale=(16.4, 7.4, 0.3), size=1, parent=hs)
    add('cube', 'CFC8B2', (0, 1.0, 6.6), scale=(14.8, 4.0, 1.6), size=1, parent=hs)
    add('cube', '8A4A3A', (5.2, 2.0, 8.2), scale=(1.3, 1.3, 3.2), size=1, parent=hs)          # chimney
    add('cube', '8E8676', (0, -6.0, 0.35), scale=(9, 3.2, 0.7), size=1, parent=hs)            # porch
    add('cube', '5A3A30', (0, -6.0, 4.9), rot=(0.25, 0, 0), scale=(9.6, 3.8, 0.2), size=1, parent=hs)
    for sx in (-1, 1):
        add('cube', 'E8E2D0', (sx * 4.2, -7.3, 2.7), scale=(0.3, 0.3, 4.2), size=1, parent=hs)
    add('cube', '4A3226', (0, -4.56, 2.3), scale=(1.9, 0.1, 3.3), size=1, parent=hs)          # door
    winm = own_mat('yardwin', 'FFD890', 3.0)
    for x in (-4.6, 4.6):
        use(add('cube', 'FFD890', (x, -4.56, 3.2), scale=(2.4, 0.1, 2.0), size=1, parent=hs), winm)
        add('cube', 'E8E2D0', (x, -4.62, 3.2), scale=(0.12, 0.06, 2.0), size=1, parent=hs)
        add('cube', 'E8E2D0', (x, -4.62, 3.2), scale=(2.4, 0.06, 0.12), size=1, parent=hs)
    for i in range(15):                                                                     # picket fence along the lane
        x = -22 + i * 1.5
        add('cube', 'E0DACA', (x, -3.4, 0.9), scale=(0.34, 0.1, 1.8), size=1, parent=r)
    add('cube', 'E0DACA', (-11.5, -3.45, 1.2), scale=(22.5, 0.08, 0.16), size=1, parent=r)
    add('cube', '5A4630', (5.6, -2.6, 1.1), scale=(0.22, 0.22, 2.2), size=1, parent=r)        # the mailbox
    add('cube', 'B8B8B0', (5.6, -2.75, 2.35), scale=(0.6, 1.1, 0.55), size=1, parent=r, rough=0.4)
    add('cube', 'D8362A', (5.95, -2.5, 2.65), scale=(0.05, 0.08, 0.5), size=1, parent=r)
    pole = empty((9.5, 7, 0), r)                                                            # power pole with a transformer
    add('cylinder', '4A3A2A', (0, 0, 6.2), radius=0.3, depth=12.4, vertices=7, parent=pole)
    add('cube', '4A3A2A', (0, 0, 11.4), scale=(4.4, 0.24, 0.24), size=1, parent=pole)
    for x in (-1.9, 0, 1.9):
        add('cylinder', 'D8D8D0', (x, 0, 11.75), radius=0.14, depth=0.4, vertices=6, parent=pole)
    add('cylinder', '7E8690', (-0.75, -0.2, 9.0), radius=0.62, depth=1.7, vertices=8, parent=pole, rough=0.5)
    add('cylinder', '5E666E', (-0.75, -0.2, 9.95), radius=0.66, depth=0.14, vertices=8, parent=pole)
    for x in (-1.9, 0, 1.9):
        add('cube', '161616', (x, 60, 11.9), scale=(0.04, 240, 0.04), size=1, parent=pole)
    add('cube', '161616', (-6.6, 4.4, 9.5), rot=(0.0, -0.3, -0.62), scale=(13.2, 0.04, 0.04), size=1, parent=pole)   # service drop to the house
    for i in range(14):
        a = i / 13
        x = -70 + a * 150
        if abs(x + 4) < 14:
            continue
        add('ico_sphere', ('2A4A2E', '32563A', '264228')[i % 3], (x, 34 + rnd(i, 1) * 16, 6), scale=(1, 1, 1.25), radius=5.5 + rnd(i, 2) * 2,
            subdivisions=1, parent=r)
        add('cylinder', '3A2A1E', (x, 34 + rnd(i, 1) * 16, 1.5), radius=0.6, depth=3, vertices=6, parent=r)
    ridges(r, 200, ('34485A', '40566A'), span=800, hgt=55)
    tgt = empty((2, 4, 2), r)
    sun = light((-60, -90, 120), 1.8, 'A8B8D0', kind='SUN', target=tgt, parent=r)
    return dict(yard_sun=sun)


# ---------------------------------------------------------------- set 4: inside the ranger station
def set_station(r):
    add('cube', '5E4830', (0, 5, -0.1), scale=(17, 16, 0.2), size=1, parent=r)                # floor
    for i in range(9):
        add('cube', '4E3C28', (-8 + i * 2.0, 5, 0.005), scale=(0.06, 16, 0.02), size=1, parent=r)
    add('cube', '4A3A2A', (0, 5, 7.6), scale=(17, 16, 0.2), size=1, parent=r)                 # ceiling
    for i in range(4):
        add('cube', '3A2C20', (0, 0.5 + i * 3.6, 7.3), scale=(17, 0.4, 0.5), size=1, parent=r)
    wall = '7A6244'
    add('cube', wall, (-6.75, 12.1, 3.75), scale=(3.5, 0.2, 7.5), size=1, parent=r)           # back wall, around the window
    add('cube', wall, (3.5, 12.1, 3.75), scale=(10, 0.2, 7.5), size=1, parent=r)
    add('cube', wall, (-3.25, 12.1, 1.15), scale=(3.5, 0.2, 2.3), size=1, parent=r)
    add('cube', wall, (-3.25, 12.1, 6.35), scale=(3.5, 0.2, 2.3), size=1, parent=r)
    add('cube', wall, (-8.5, 5, 3.75), scale=(0.2, 16, 7.5), size=1, parent=r)
    add('cube', wall, (0, -3.1, 3.75), scale=(17, 0.2, 7.5), size=1, parent=r)                # front wall with the way in
    add('cube', '3A2C20', (-4.5, -2.98, 2.8), scale=(2.6, 0.12, 5.6), size=1, parent=r)
    add('cube', 'C8BE9A', (3.0, -2.98, 4.2), scale=(2.2, 0.06, 1.6), size=1, parent=r)
    add('cube', wall, (8.5, 5, 3.75), scale=(0.2, 16, 7.5), size=1, parent=r)
    for i in range(1, 7):
        add('cube', '6A5438', (3.5, 11.98, i * 1.07), scale=(10, 0.03, 0.05), size=1, parent=r)
        add('cube', '6A5438', (8.38, 5, i * 1.07), scale=(0.03, 16, 0.05), size=1, parent=r)
        add('cube', '6A5438', (-8.38, 5, i * 1.07), scale=(0.03, 16, 0.05), size=1, parent=r)
    panem = own_mat('stpane', '3A4A66', 1.2)
    use(add('cube', '3A4A66', (-3.25, 12.3, 3.75), scale=(3.5, 0.05, 2.9), size=1, parent=r), panem)
    for x in (-5.0, -3.25, -1.5):
        add('cube', '3A2C20', (x, 12.0, 3.75), scale=(0.16, 0.3, 2.9), size=1, parent=r)
    for z in (2.3, 3.75, 5.2):
        add('cube', '3A2C20', (-3.25, 12.0, z), scale=(3.6, 0.3, 0.16), size=1, parent=r)
    add('cube', 'C8BE9A', (1.6, 11.95, 4.1), scale=(3.4, 0.06, 2.4), size=1, parent=r)        # a wall map (blank contours)
    add('cube', '3A2C20', (1.6, 11.93, 4.1), scale=(3.6, 0.04, 2.6), size=1, parent=r)
    for i in range(5):
        add('torus', '7A8A5A', (1.2 + i * 0.12, 11.9, 4.0 + i * 0.05), rot=(PI / 2, 0, 0), scale=(1.4, 1, 1), major_radius=0.25 + i * 0.16,
            minor_radius=0.014, major_segments=10, minor_segments=3, parent=r)
    sk = empty((5.6, 11.4, 0), r)                                                           # the sink
    add('cube', 'E8E8E4', (0, 0, 2.0), scale=(1.9, 1.2, 0.5), size=1, parent=sk, rough=0.3)
    add('cube', '9A9A98', (0, -0.05, 2.22), scale=(1.5, 0.85, 0.1), size=1, parent=sk, rough=0.3)
    add('cylinder', '8A8A88', (0, 0.3, 1.0), radius=0.14, depth=2.0, vertices=6, parent=sk)
    add('cylinder', 'C8C8C4', (0, 0.4, 2.6), radius=0.07, depth=0.7, vertices=6, parent=sk, rough=0.3)
    add('cylinder', 'C8C8C4', (0, 0.18, 2.92), rot=(PI / 2, 0, 0), radius=0.07, depth=0.5, vertices=6, parent=sk, rough=0.3)
    add('cube', 'A8C0CC', (0, 0.62, 4.4), scale=(1.5, 0.05, 1.7), size=1, parent=sk, rough=0.15)
    add('cube', '3A2C20', (0, 0.64, 4.4), scale=(1.7, 0.04, 1.9), size=1, parent=sk)
    dk = empty((-2.4, 6.6, 0), r)                                                           # the desk
    add('cube', '5A4028', (0, 0, 1.55), scale=(5.6, 2.3, 0.2), size=1, parent=dk)
    for sx in (-1, 1):
        add('cube', '4A3420', (sx * 2.3, 0, 0.75), scale=(0.9, 2.1, 1.5), size=1, parent=dk)
    add('cube', '4A3420', (-8.0, 9.6, 3.0), scale=(0.9, 2.2, 0.1), size=1, parent=r)             # a radio set on a wall shelf
    add('cube', '2A2A2E', (-7.95, 9.6, 3.4), scale=(0.8, 1.3, 0.7), size=1, parent=r)
    add('cube', 'FFB000', (-7.53, 9.6, 3.45), scale=(0.03, 0.5, 0.2), size=1, parent=r, emit=2.0)
    add('cube', 'E8E2D0', (-0.6, -0.2, 1.67), rot=(0, 0, 0.2), scale=(1.1, 0.8, 0.03), size=1, parent=dk)
    add('cylinder', '2E4A3A', (-2.1, 0.3, 1.75), radius=0.3, depth=0.2, vertices=8, parent=dk)   # desk lamp
    add('cylinder', '2E4A3A', (-2.1, 0.3, 2.3), radius=0.05, depth=1.0, vertices=5, parent=dk)
    add('cone', '2E4A3A', (-2.1, 0.1, 2.85), rot=(0.5, 0, 0), radius1=0.5, radius2=0.15, depth=0.5, vertices=8, parent=dk)
    dlamp = light((-2.1, -0.1, 2.6), 260, 'FFC070', kind='POINT', parent=dk)
    add('cube', '4A3420', (0, 1.75, 0.4), scale=(1.5, 1.3, 0.1), size=1, parent=dk)            # his chair
    add('cube', '4A3420', (0, 2.4, 1.6), scale=(1.5, 0.12, 2.4), size=1, parent=dk)
    add('cube', '4A3420', (4.0, -1.3, 0.4), scale=(1.4, 1.4, 0.1), size=1, parent=dk)          # the visitor's chair
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cube', '3A2818', (4.0 + sx * 0.6, -1.3 + sy * 0.6, 0.2), scale=(0.12, 0.12, 0.4), size=1, parent=dk)
    add('cube', '1E2A22', (8.34, 5.4, 3.7), scale=(0.08, 3.6, 2.4), size=1, parent=r)         # the chalkboard on the east wall
    add('cube', '5A4028', (8.3, 5.4, 3.7), scale=(0.06, 3.9, 2.7), size=1, parent=r)
    add('cube', '5A4028', (8.2, 5.4, 2.45), scale=(0.3, 3.6, 0.08), size=1, parent=r)
    marks = []
    for i in range(7):                                                                      # chalk tally: four, a slash, two more
        j = i if i < 4 else i + 1
        if i == 4:
            m = add('cube', 'F0F0E8', (8.27, 6.18, 3.8), rot=(-1.05, 0, 0), scale=(0.03, 0.07, 1.7), size=1, parent=r, emit=0.6)
        else:
            m = add('cube', 'F0F0E8', (8.27, 6.75 - (j if i < 4 else j - 0.2) * 0.38, 3.8), rot=(0.08 * (i % 2), 0, 0), scale=(0.03, 0.07, 0.9), size=1,
                    parent=r, emit=0.6)
        marks.append(m)
    add('cube', '3A2C20', (-8.3, 3.0, 2.8), scale=(0.12, 2.6, 5.6), size=1, parent=r)         # the door
    for i, z in enumerate((4.4, 4.9)):                                                      # coat hooks and a spare hat
        add('cube', '2A2A2A', (-8.3, 7.5 + i * 0.9, z), scale=(0.3, 0.08, 0.08), size=1, parent=r)
    top = light((0, 4.5, 6.9), 620, 'FFD8A8', 3.0, parent=r)
    top.rotation_euler = (0, 0, 0)
    winl = light((-3.25, 11.4, 3.75), 60, '8AA0D0', 2.5, parent=r)
    winl.rotation_euler = (-PI / 2, 0, 0)
    return dict(st_top=top, st_win=winl, st_pane=panem, st_desk=dlamp, marks=marks)


# ---------------------------------------------------------------- set 5: the fishing pond
def set_pond(r):
    add('plane', '34502F', (0, 0, -0.06), size=3000, parent=r)
    add('cylinder', '2C4858', (0, 34, 0.0), scale=(1.25, 1, 1), radius=30, depth=0.08, vertices=22, parent=r, rough=0.12)
    add('cylinder', '4A4A38', (0, 34, -0.02), scale=(1.25, 1, 1), radius=31.2, depth=0.06, vertices=22, parent=r)
    for i in range(7):                                                                      # the jetty
        add('cube', ('7A6040', '6E5638')[i % 2], (0, 2.2 + i * 1.3, 0.55), scale=(2.6, 1.2, 0.14), size=1, parent=r)
    for sx in (-1, 1):
        for y in (4.0, 7.2, 10.4):
            add('cylinder', '4A3826', (sx * 1.25, y, 0.3), radius=0.16, depth=1.4, vertices=6, parent=r)
    for i in range(38):                                                                     # reeds
        a = rnd(i, 1) * 2 * PI
        x, y = math.cos(a) * 37 * (0.96 + rnd(i, 2) * 0.05), 34 + math.sin(a) * 29.6 * (0.96 + rnd(i, 2) * 0.05)
        if abs(x) < 3 and y < 12:
            continue
        add('cone', ('5A7A3A', '6A8A44')[i % 2], (x, y, 1.0), rot=(rnd(i, 3) * 0.2 - 0.1, rnd(i, 4) * 0.2 - 0.1, 0), radius1=0.16, radius2=0.0,
            depth=2.0 + rnd(i, 5), vertices=4, parent=r)
    for i in range(44):                                                                     # trees all round
        a = i / 44 * 2 * PI
        d = 1.18 + rnd(i, 6) * 0.5
        x, y = math.cos(a) * 37 * d, 34 + math.sin(a) * 30 * d
        if abs(x) < 9 and y < 6:
            continue
        if i % 3:
            pine(r, x, y, 1.2 + rnd(i, 7), i)
        else:
            add('cylinder', '3A2A1E', (x, y, 2.0), radius=0.5, depth=4, vertices=6, parent=r)
            add('ico_sphere', ('2E5234', '3A6240')[i % 2], (x, y, 6.5), scale=(1, 1, 1.2), radius=4.2 + rnd(i, 8) * 1.5, subdivisions=1, parent=r)
    for i in range(8):                                                                      # trees and a boulder behind the bank
        x = -40 + i * 11.5 + rnd(i, 9) * 4
        if abs(x) < 7:
            continue
        pine(r, x, -22 - rnd(i, 10) * 14, 1.5 + rnd(i, 11) * 0.8, i)
    add('ico_sphere', '5A5852', (-4.2, -0.6, 0.35), scale=(1.5, 1.1, 0.8), radius=1.0, subdivisions=1, parent=r)
    add('cube', '4E6A8A', (2.3, 1.0, 0.3), scale=(0.9, 0.6, 0.6), size=1, parent=r)           # a tackle box
    add('cube', 'B8B8B0', (2.3, 0.69, 0.42), scale=(0.2, 0.03, 0.12), size=1, parent=r, rough=0.3)
    ridges(r, 230, ('3A4E60', '4A6074'), span=800, hgt=60)
    ridges(r, -260, ('3A4E60',), span=800, hgt=60)
    tgt = empty((0, 8, 2), r)
    sun = light((90, 60, 80), 1.8, 'B0C0D8', kind='SUN', target=tgt, parent=r)
    return dict(pond_sun=sun)


# ---------------------------------------------------------------- set 6: the exhibit hall
def make_hat(parent, loc=(0, 0, 0), burnt=False, s=1.0):
    """A flat-brimmed ranger hat. burnt adds scorch marks to the crown."""
    h = empty(loc, parent)
    parts = [add('cylinder', HATC, (0, 0, 0), radius=0.62, depth=0.04, vertices=12, parent=h),
             add('cone', HATC, (0, 0, 0.2), radius1=0.31, radius2=0.25, depth=0.4, vertices=8, parent=h),
             add('cylinder', BAND, (0, 0, 0.06), radius=0.325, depth=0.08, vertices=8, parent=h)]
    for sx in (-1, 1):
        parts.append(add('cube', '7A6444', (sx * 0.1, 0, 0.4), rot=(0, sx * 0.5, 0), scale=(0.2, 0.36, 0.03), size=1, parent=h))
    if burnt:
        parts.append(add('ico_sphere', '141210', (0.12, -0.16, 0.3), scale=(1, 0.7, 1), radius=0.15, subdivisions=1, parent=h))
        parts.append(add('ico_sphere', '141210', (-0.3, 0.3, 0.02), scale=(1, 1, 0.3), radius=0.14, subdivisions=1, parent=h))
    h.scale = (s, s, s)
    return h, parts


def set_hall(r):
    add('cube', '2A2630', (0, 2, -0.1), scale=(40, 30, 0.2), size=1, parent=r, rough=0.4)
    add('cube', '3A1E26', (0, 9, 6), scale=(40, 0.4, 12), size=1, parent=r)
    for i in range(14):
        add('cube', ('4A2630', '421F2A')[i % 2], (-19 + i * 3, 8.7, 6), scale=(1.5, 0.3, 12), size=1, parent=r)
    add('cube', '1E1C22', (0, 2, 11), scale=(40, 30, 0.2), size=1, parent=r)
    add('cube', '2E2A34', (0, 0, 1.0), scale=(3.4, 2.0, 2.0), size=1, parent=r)               # plinth
    add('cube', 'FF7A1A', (0, -1.02, 1.6), scale=(3.0, 0.04, 0.12), size=1, parent=r, emit=1.0)
    for sx in (-1, 1):                                                                      # the case, as a brass frame
        for sy in (-1, 1):
            add('cube', 'C89A3A', (sx * 1.6, sy * 0.9, 3.0), scale=(0.07, 0.07, 2.0), size=1, parent=r, rough=0.3)
        add('cube', 'C89A3A', (sx * 1.6, 0, 4.0), scale=(0.07, 1.87, 0.07), size=1, parent=r, rough=0.3)
        add('cube', 'C89A3A', (0, sx * 0.9, 4.0), scale=(3.27, 0.07, 0.07), size=1, parent=r, rough=0.3)
    for x, yaw in ((-0.78, 0.3), (0.78, -0.4)):
        add('cylinder', '1A1A1E', (x, 0, 2.3), radius=0.08, depth=0.6, vertices=6, parent=r)
        add('cylinder', '1A1A1E', (x, 0, 2.03), radius=0.3, depth=0.06, vertices=8, parent=r)
        hh, _ = make_hat(r, (x, 0, 2.62), burnt=True, s=1.0)
        hh.rotation_euler = (0.22, 0, yaw)
    for x in (-5.2, 5.2):                                                                   # rope posts
        add('cylinder', 'C89A3A', (x, -3.2, 1.0), radius=0.1, depth=2.0, vertices=6, parent=r, rough=0.3)
        add('ico_sphere', 'C89A3A', (x, -3.2, 2.1), radius=0.2, subdivisions=1, parent=r, rough=0.3)
        add('cylinder', 'C89A3A', (x, -3.2, 0.05), radius=0.4, depth=0.1, vertices=8, parent=r, rough=0.3)
    add('cube', 'FF7A1A', (0, -3.2, 1.75), scale=(10.4, 0.07, 0.1), size=1, parent=r)
    tgt = empty((0, 0, 2.6), r)
    sp = light((0, -3.5, 9.5), 5200, 'FFE8C8', kind='SPOT', spot=0.55, target=tgt, parent=r)
    light((-8, -6, 6), 220, '6A7AB0', 4.0, tgt, parent=r)
    return dict(hall_spot=sp)


# ---------------------------------------------------------------- cast and props
def roy_head(head):
    """Roy: a plain low-poly face. Hair has its own material (it greys over 35 years) and the brows can be hidden."""
    hairm = own_mat('royhair', '5A3A22', 0.9)
    add('ico_sphere', SKIN, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
    use(add('ico_sphere', '5A3A22', (0, 0.05, 0.1), scale=(0.95, 1, 1.0), radius=0.3, subdivisions=1, parent=head), hairm)
    eyes, brows = [], []
    for s in (-1, 1):
        eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
        add('cube', '0E0D14', (s * 0.105, -0.28, 0.035), scale=(0.04, 0.02, 0.045), size=1, parent=head)
        brows.append(use(add('cube', '5A3A22', (s * 0.105, -0.27, 0.125), rot=(0, s * 0.12, 0), scale=(0.14, 0.03, 0.035), size=1, parent=head), hairm))
    add('cube', 'B88A68', (0, -0.285, -0.04), scale=(0.05, 0.05, 0.08), size=1, parent=head)
    jaw = empty((0, -0.2, -0.13), head)
    add('cube', '2A1218', (0, -0.07, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
    return dict(jaw=jaw, eyes=eyes, brows=brows, hairm=hairm)


def make_rod():
    r = empty(FAR)
    add('cylinder', '3A2A1E', (0, -2.6, 0), rot=(PI / 2, 0, 0), radius=0.035, depth=5.2, vertices=5, parent=r)
    add('cylinder', '8A6A40', (0, -0.2, 0), rot=(PI / 2, 0, 0), radius=0.06, depth=0.8, vertices=6, parent=r)
    return r


def make_can():
    c = empty(FAR)
    add('cylinder', '6A7E8A', (0, 0, 0), radius=0.26, depth=0.56, vertices=8, parent=c, rough=0.4)
    add('cylinder', '54646E', (0, 0, 0.3), radius=0.2, depth=0.06, vertices=8, parent=c, rough=0.4)
    add('cone', '6A7E8A', (0, -0.36, 0.14), rot=(1.0, 0, 0), radius1=0.07, radius2=0.04, depth=0.5, vertices=6, parent=c, rough=0.4)
    add('torus', '54646E', (0, 0.28, 0.02), rot=(0, PI / 2, 0), major_radius=0.17, minor_radius=0.03, major_segments=8, minor_segments=4, parent=c)
    return c


def build():
    sc = bpy.context.scene
    _MOV.clear()
    S = dict(colls={})
    for name, fn in (('ridge', set_ridge), ('road', set_road), ('yard', set_yard), ('station', set_station), ('pond', set_pond), ('hall', set_hall)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['roy'] = roy = K.Rig(ROY, roy_head)
    add('cube', '2E3A2A', (0, -0.33, 0.8), scale=(0.07, 0.03, 0.4), size=1, parent=roy.body)             # tie
    add('cube', '2A2420', (0, 0, 0.05), scale=(0.66, 0.66, 0.08), size=1, parent=roy.body)                # belt
    S['scorch'] = [add('ico_sphere', '1A1612', (0.08, -0.3, 0.62), scale=(1.3, 0.25, 1.0), radius=0.2, subdivisions=1, parent=roy.body),
                   add('ico_sphere', '1A1612', (-0.12, -0.33, 0.3), scale=(1.0, 0.25, 0.8), radius=0.17, subdivisions=1, parent=roy.body)]
    S['rhat'], S['rhat_parts'] = make_hat(roy.head, (0, 0.0, 0.3))
    S['rhat'].rotation_euler = (-0.08, 0, 0)
    S['flames'] = [add('cone', ('FF9A1A', 'FFD040', 'FF5A10')[i % 3], ((i - 2) * 0.11, 0.05 * (i % 2), 0.42), radius1=0.12, radius2=0.0, depth=0.5,
                       vertices=4, parent=roy.head, emit=9.0) for i in range(5)]
    S['flamelight'] = light((0, 0, 0.9), 0, 'FF9A30', kind='POINT', parent=roy.head)
    S['cast'] = [S['rook'], S['roy']]
    S['truck'], S['cablamp'] = make_truck()
    mov(S['truck'])
    S['rod'] = mov(make_rod())
    S['can'] = mov(make_can())
    S['lhat'] = mov(make_hat(None, FAR)[0])
    S['bhat'] = mov(make_hat(None, FAR, burnt=True)[0])
    S['bolt'] = [mov(add('cylinder', 'F0F4FF', FAR, radius=0.5, depth=1.0, vertices=5, emit=60.0)) for _ in range(22)]
    S['sparks'] = [mov(add('cube', ('FFE080', 'FFFFFF', 'FFB040')[i % 3], FAR, scale=(0.12, 0.12, 0.3), size=1, emit=25.0)) for i in range(14)]
    S['puffs'] = [mov(add('ico_sphere', ('B8B8BC', 'D0D0D4')[i % 2], FAR, radius=1.0, subdivisions=1, emit=0.12)) for i in range(10)]
    S['drops'] = [mov(add('ico_sphere', '9AD0F0', FAR, scale=(1, 1, 1.6), radius=0.07, subdivisions=1, emit=1.2, rough=0.2)) for _ in range(10)]
    S['fea'] = [mov(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(3)]
    S['coin'] = mov(add('cylinder', 'FFC233', FAR, radius=0.11, depth=0.03, vertices=8, rough=0.25, emit=1.2))
    S['lure'] = mov(empty(FAR))
    add('ico_sphere', 'D8E4F0', (0, 0, 0), scale=(0.6, 1.7, 0.4), radius=0.12, subdivisions=1, parent=S['lure'], rough=0.15, emit=2.5)
    add('ico_sphere', 'FF7A1A', (0, -0.18, 0.02), radius=0.05, subdivisions=1, parent=S['lure'], emit=3.0)
    S['towel'] = mov(add('cube', 'F2F0E8', FAR, scale=(0.75, 0.6, 0.16), size=1, emit=0.1))
    S['glow'] = light(FAR, 0, 'DCE6FF', kind='POINT')
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
    S['suns'] = {k: S[k].data.energy for k in ('ridge_sun', 'road_sun', 'yard_sun', 'pond_sun')}
    return S


def sky(S, col, strength=1.0):
    S['bg'].inputs[0].default_value = K.hexc(col)
    S['bg'].inputs[1].default_value = strength


def show(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: at(name, x, y, z)


def cam(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='C8D4F0'):
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


def vis(objs, on):
    for o in objs:
        o.hide_render = not on


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
    for o, par, loc, rot, scl in _MOV:
        o.parent = par
        o.location, o.rotation_euler, o.scale = loc, rot, scl
    vis(S['flames'], False)
    vis(S['scorch'], False)
    vis(S['rhat_parts'], True)
    vis(S['roy'].extra['brows'], True)
    vis(S['marks'], False)
    S['rhat'].rotation_euler = (-0.08, 0, 0)
    S['rhat'].location = (0, 0, 0.3)
    tint(S['roy'].extra['hairm'], '5A3A22')
    S['flamelight'].data.energy = 0
    S['glow'].location = FAR
    S['glow'].data.energy = 0
    S['glow'].data.color = K.hexc('DCE6FF')[:3]
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['cablamp'].data.energy = 0
    S['cablight'].data.energy = 500
    tint(S['cablampm'], 'FFC070', 6.0)
    tint(S['st_pane'], '3A4A66', 1.2)
    S['st_win'].data.energy = 60
    S['st_top'].data.energy = 620
    S['st_desk'].data.energy = 260
    for k, e in S['suns'].items():
        S[k].data.energy = e
        S[k].data.color = K.hexc('9AB0D0')[:3]
    S['hall_spot'].data.energy = 5200
    S['face'] = dict(rook='calm', roy='calm')
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
    S['jaw'] = 0.0
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
    k = dict(scared=1.4, shock=1.8, calm=1.0, tired=0.5, warm=0.8, shut=0.12).get(S['face']['roy'], 1.0)
    for ey in S['roy'].extra['eyes']:
        ey.scale = (ey.scale[0], ey.scale[1], 0.075 * k)
    S['roy'].extra['jaw'].rotation_euler = (S['jaw'], 0, 0)


# ---------------------------------------------------------------- effects
def flick(lt, t0):
    """Brightness of a lightning stroke that starts at t0: two pulses and a short afterglow."""
    x = lt - t0
    if x < 0:
        return 0.0
    if x < 0.14:
        return 1.0
    if x < 0.21:
        return 0.3
    if x < 0.38:
        return 0.9
    return max(0.0, 0.9 * (1 - (x - 0.38) / 0.3))


def seg(o, a, b, w):
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w, w, max(0.01, d.length))


def strike(S, a, b, seed=1, i0=0, n=8, w=0.22, jit=1.0):
    """A zigzag bolt from a to b made of n glowing segments (taken from the pool starting at i0)."""
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    pts = [a]
    for i in range(1, n):
        u = i / n
        p = a.lerp(b, u)
        j = L * 0.07 * jit
        pts.append(p + Vector(((rnd(seed, i) - 0.5) * 2 * j, (rnd(seed, i + 20) - 0.5) * 2 * j, (rnd(seed, i + 40) - 0.5) * j)))
    pts.append(b)
    for i in range(n):
        seg(S['bolt'][i0 + i], pts[i], pts[i + 1], w)
    return pts


def branch(S, p, seed, i0, n=3, w=0.1, L=6.0):
    q = Vector(p)
    for i in range(n):
        nq = q + Vector(((rnd(seed, i) - 0.5) * L, (rnd(seed, i + 7) - 0.5) * L * 0.5, -L * (0.3 + 0.4 * rnd(seed, i + 3))))
        seg(S['bolt'][i0 + i], q, nq, w)
        q = nq


def flash(S, pos, f, energy=16000.0):
    S['glow'].location = pos
    S['glow'].data.energy = energy * f * 0.3


def sparks(S, pos, t, n=10, r=2.2, speed=2.4, up=1.0):
    for i in range(n):
        u = (t * speed + rnd(i, 3)) % 1
        a = rnd(i, 1) * 2 * PI
        d = r * u * (0.5 + rnd(i, 2))
        S['sparks'][i].location = (pos[0] + math.cos(a) * d, pos[1] + math.sin(a) * d, pos[2] + up * (u * 2.2 - 3.2 * u * u) * (0.6 + rnd(i, 4)))
        S['sparks'][i].rotation_euler = (t * 9 + i, i, t * 5)
        s = 1.0 - 0.7 * u
        S['sparks'][i].scale = (0.12 * s, 0.12 * s, 0.34 * s)


def smoke(S, pos, t, n=4, rise=1.8, size=0.22, i0=0, speed=0.7):
    for i in range(n):
        u = (t * speed + i / n) % 1
        o = S['puffs'][i0 + i]
        o.location = (pos[0] + 0.25 * math.sin(t * 2 + i * 2.1) * u, pos[1] + 0.2 * math.cos(t * 1.7 + i), pos[2] + rise * u)
        s = size * (0.5 + 1.3 * u)
        o.scale = (s, s, s * 0.8)


def burn(S, t, k=1.0):
    """Hair on fire: small flames on Roy's head."""
    vis(S['flames'], k > 0.02)
    for i, o in enumerate(S['flames']):
        s = k * (0.75 + 0.35 * math.sin(t * 23 + i * 1.9))
        o.scale = (s, s, s * (1.0 + 0.4 * math.sin(t * 17 + i)))
        o.rotation_euler = (0.25 * math.sin(t * 13 + i), 0.25 * math.cos(t * 11 + i * 2), 0)
    S['flamelight'].data.energy = 160 * k * (0.8 + 0.2 * math.sin(t * 19))


def feather(S, pos, lt, t0=0.0, n=2):
    for i in range(n):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def age(S, grey=True, hat=True, brows=True):
    tint(S['roy'].extra['hairm'], 'A6A6A2' if grey else '5A3A22')
    vis(S['rhat_parts'], hat)
    vis(S['roy'].extra['brows'], brows)


def mood(S, name, col, f=0.0, fk=4.0, sunk=None, sunc=None):
    """Show one set under a sky colour; f (0..1) is how much a lightning flash lights it."""
    A = show(S, name)
    sky(S, mix_col(col, 'A8BCEC', 0.5 * f), 1.0 + 0.7 * f)
    S['fillk'] = fk * (1 + 0.7 * f)
    key = name + '_sun'
    if key in S['suns']:
        S[key].data.energy = S['suns'][key] * (sunk if sunk is not None else 1.0) * (1 + 1.6 * f)
        if sunc:
            S[key].data.color = K.hexc(sunc)[:3]
    return A


COVER = P('stand', aL=(2.4, 0.35, 1.7), aR=(2.4, 0.35, 1.7), lean=0.3, head=(0.35, 0.0), lL=(0.35, 0.6), lR=(0.35, 0.6), lift=-0.12)
DUCK = P('hat', aL=(0.2, 1.9, 1.6, -1.5), lean=0.4, head=(0.3, 0.0), lL=(0.45, 0.8), lR=(0.45, 0.8), lift=-0.2)
JOLT = P('stand', aL=(0.6, 1.3, 0.5), aR=(0.6, 1.3, 0.5), lean=-0.22, head=(-0.3, 0.0), lL=(0.15, 0.1), lR=(-0.2, 0.3))
THINK = P('stand', aR=(1.0, 0.1, 2.3, 0.6), aL=(0.45, -0.05, 1.6, 1.2), head=(0.08, 0.15))
KNEEL = P('stand', lR=(1.45, 1.5), lL=(-0.15, 1.5), lift=-0.5, lean=0.12)


def hat_hold(**over):
    d = dict(aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.22, 0.0))
    d.update(over)
    return P('stand', **d)


def run_pose(t, speed=2.6):
    w = walk(t, speed)
    return dict(w, lean=0.3, aL=(w['aL'][0] * 1.7, 0.15, 1.3, 0.0), aR=(w['aR'][0] * 1.7, 0.15, 1.3, 0.0))


# ---------------------------------------------------------------- shots: the ridge (strike 1, 1942, and strike 6, 1976)
NIGHT, GREY, DUSK = '121A2A', '465262', '2E3550'
TOP = (0, 14, 15.7)                                         # the tip of the tower roof


def bolt_tower(S, k, t, lt):
    f = flick(lt, 0.0)
    A = mood(S, 'ridge', NIGHT, f, fk=3.5)
    if f > 0.5:
        pts = strike(S, A(6, 30, 70), A(*TOP), 3, n=9, w=0.38)
        branch(S, pts[4], 5, 9, w=0.16, L=9)
        branch(S, pts[6], 6, 12, w=0.12, L=7)
    flash(S, A(0, 12, 17), f, 30000)
    if lt >= 0.0:
        sparks(S, A(0, 14, 15.2), t, 14, r=4.5, up=1.8)
    age(S, grey=False)
    S['roy'].place(A(-2.0, lerp(6.5, 3.6, k), 0), 0.1)
    S['roy'].apply(run_pose(t))
    S['face']['roy'] = 'scared'
    cam(S, A(lerp(-5.2, -4.6, k), lerp(-4.2, -3.0, k), 1.2), A(-0.5, 12, lerp(8.6, 9.6, k)), 22)


def tower_wide(S, k, t, lt):
    f = 0.55 * flick(lt, 0.55)
    A = mood(S, 'ridge', NIGHT, f, fk=3.0)
    if f > 0.25:
        strike(S, A(-120, 260, 150), A(-95, 250, 20), 8, n=7, w=1.6)
    age(S, grey=False)
    S['roy'].place(A(-0.5, 11.6, 9.3), 0.2)
    S['roy'].apply(P('stand', aR=(2.3, 0.45, 2.0, 0.4), head=(-0.1, 0.2)))
    e = ease(k)
    cam(S, A(lerp(13, 10.5, e), lerp(-15, -12, e), lerp(8.5, 6.6, e)), A(0, 14, lerp(8.0, 9.4, k)), 28)


def roy_tower(S, k, t, lt):
    f = 0.6 * flick(lt, 0.8)
    A = mood(S, 'ridge', NIGHT, f, fk=3.5)
    age(S, grey=False)
    S['roy'].place(A(-0.9, 11.7, 9.3), 0.15)
    S['roy'].apply(P('stand', aR=(2.3, 0.45, 2.0, 0.4), head=(-0.15, 0.25 * math.sin(lt * 2.2))))
    up = ease((lt - 0.8) / 0.3)
    S['rook'].place(A(1.1, 11.9, 9.3), -0.2)
    S['rook'].apply(P('cross', head=(0.06 - 0.5 * up, 0.25 - 0.25 * up)))
    S['face']['rook'] = 'deadpan' if up < 0.5 else 'calm'
    cam(S, A(lerp(-0.7, -0.2, k), lerp(5.0, 5.9, k), 11.2), A(0.1, 11.8, 11.6), 36, fcol='FFD0A0')


def tower_hit(S, k, t, lt):
    f = flick(lt, 0.12)
    A = mood(S, 'ridge', NIGHT, f, fk=3.5)
    if f > 0.5:
        strike(S, A(5, 22, 70), A(*TOP), 11, n=9, w=0.32)
    flash(S, A(1.5, 9.5, 14.5), f, 9000)
    tint(S['cablampm'], mix_col('FFC070', 'FFFFFF', f), 6 + 40 * f)
    hit = ease((lt - 0.12) / 0.15)
    if lt > 0.12:
        sparks(S, A(0.2, 12.6, 11.4), t, 14, r=2.8, speed=3.0, up=0.9)
    age(S, grey=False)
    S['roy'].place(A(-0.9, 11.7, 9.3), 0.15)
    S['roy'].apply(blend(P('stand', aR=(2.3, 0.45, 2.0, 0.4)), COVER, hit))
    S['face']['roy'] = 'scared' if hit > 0.3 else 'calm'
    S['jaw'] = 0.3 * hit
    S['rook'].place(A(1.1, 11.9, 9.3), -0.2)
    S['rook'].apply(blend(P('cross', head=(-0.44, 0.0)), DUCK, hit))
    S['face']['rook'] = 'shocked' if hit > 0.2 else 'calm'
    feather(S, A(1.3, 11.5, 12.4), lt, 0.2)
    cam(S, A(lerp(5.4, 4.8, k), lerp(4.6, 5.4, k), 12.3), A(0.0, 12.3, 11.2), 30, roll=0.05 * math.sin(lt * 30) * hit, fcol='FFD0A0')


def roy_runs(S, k, t, lt):
    f = flick(lt, 0.45)
    A = mood(S, 'ridge', NIGHT, f, fk=3.5)
    y = lerp(7.5, 2.5, k)
    if f > 0.5:
        strike(S, A(1, 14, 60), A(-2.8, y - 0.3, 0.15), 14, n=9, w=0.2)
        sparks(S, A(-2.8, y - 0.3, 0.3), t, 8, r=1.2, speed=4.0)
    flash(S, A(-2.0, y - 2.0, 2.5), f, 7000)
    hit = ease((lt - 0.45) / 0.12)
    age(S, grey=False)
    S['roy'].place(A(-3, y, 0), 0.0)
    S['roy'].apply(blend(run_pose(t), JOLT, hit * (1 - ease((lt - 0.8) / 0.3))))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'scared'
    S['jaw'] = 0.35 * hit
    S['rook'].place(A(-1.5, y + 3.6, 0), 0.05)
    S['rook'].apply(dict(run_pose(t + 0.2), aR=(0.2, 1.9, 1.6, -1.5)))
    S['face']['rook'] = 'shocked' if hit > 0.3 else 'calm'
    cam(S, A(-1.0, lerp(-3.2, -4.6, k), 1.15), A(-2.6, y + 0.6, lerp(2.3, 2.1, k)), 30)


def trail_hit(S, k, t, lt):
    f = flick(lt, 0.62)
    A = mood(S, 'ridge', GREY, f, fk=5.0, sunk=2.2)
    S['cablight'].data.energy = 0
    tint(S['cablampm'], '6A6050', 0.0)
    y = lerp(-3.0, -5.6, min(1.0, lt / 0.62) * 0.8 + 0.2 * k)
    if f > 0.5:
        strike(S, A(-8, 6, 60), A(-3.25, y - 0.15, 0.15), 71, n=9, w=0.2)
        sparks(S, A(-3.25, y - 0.15, 0.3), t, 8, r=1.2, speed=4.0)
    flash(S, A(-2.2, y - 2.0, 2.2), f, 6000)
    hit = ease((lt - 0.62) / 0.12)
    age(S)
    S['roy'].place(A(-3, y, 0), 0.25)
    S['roy'].apply(blend(walk(t, 1.5), JOLT, hit))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'calm'
    S['jaw'] = 0.35 * hit
    cam(S, A(lerp(3.8, 3.2, k), lerp(-12.5, -11.6, k), 1.5), A(-2.6, y + 0.6, 2.6), 32)


def roy_hop(S, k, t, lt):
    A = mood(S, 'ridge', GREY, 0.0, fk=5.0, sunk=2.2)
    S['cablight'].data.energy = 0
    tint(S['cablampm'], '6A6050', 0.0)
    age(S)
    hop = abs(math.sin(lt * 8.0))
    S['roy'].place(A(-3.0, -6.0, 0.28 * hop), 0.3)
    S['roy'].apply(P('stand', lL=(1.25, 1.9), aL=(1.3, 0.1, 0.7), aR=(1.3, 0.1, 0.7), lean=0.5, head=(-0.1, 0.0), lR=(0.0, 0.25 * (1 - hop))))
    S['face']['roy'] = 'scared'
    S['jaw'] = 0.3
    smoke(S, A(-3.25, -6.75, 1.0 + 0.28 * hop), t, 3, rise=1.3, size=0.16, speed=1.3)
    S['rook'].place(A(-0.7, -6.7, 0), -0.55)
    S['rook'].apply(P('hat', head=(0.12, -0.45)))
    S['hat_tip'] = 0.7 * ease(lt / 0.3)
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(0.3, -0.1, k), lerp(-13.6, -12.8, k), 2.0), A(-1.9, -6.2, 2.3), 42)


# ---------------------------------------------------------------- shots: the park road (the gate, strike 2 in 1969, strike 5 in 1973)
DRIVE = P('sit', aL=(1.15, 0.0, 0.5), aR=(1.15, 0.0, 0.5), lean=0.05, head=(0.0, 0.0))
SLUMP = P('sit', aL=(0.5, 0.25, 1.0), aR=(0.5, 0.25, 1.0), lean=-0.08, head=(-0.12, 0.0))


def truck_at(S, A, x, y, lamp=60.0):
    S['truck'].location = A(x, y, 0)
    S['cablamp'].data.energy = lamp
    return A(x + 0.65, y + 0.45, 1.15), A(x - 0.65, y + 0.45, 1.15)


def rook_gate(S, k, t, lt):
    f = 0.5 * flick(lt, 0.42)
    A = mood(S, 'road', '2A3548', f, fk=11.0)
    S['rook'].place(A(0.6, -15.4, 0), 0.0)
    S['rook'].apply(P('cross', head=(0.06, 0.32 * math.sin(lt * 9.0) * max(0.0, 1 - lt / 0.75))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(1.7, 1.3, k), lerp(-22.2, -21.2, k), 3.0), A(0.6, -15.4, 3.15), 40)


def rook_collar(S, k, t, lt):
    f = 0.7 * flick(lt, 0.2)
    A = mood(S, 'road', '26303F', f, fk=4.5)
    if f > 0.3:
        strike(S, A(-40, 190, 130), A(-30, 180, 25), 9, n=7, w=1.2)
    y = -15.4 + 3.4 * max(0.0, lt - 0.2)
    S['rook'].place(A(0.6, y, 0), PI)
    S['rook'].apply(blend(P('hat', aL=(0.2, 1.9, 1.6, -1.5)), walk(t, 2.0), (lt - 0.2) / 0.15) if lt > 0.2 else
                    blend(P('stand'), P('hat', aL=(0.2, 1.9, 1.6, -1.5)), lt / 0.14))
    cam(S, A(-2.2, lerp(-21.6, -20.8, k), 1.1), A(0.5, y + 0.8, 3.1), 28)


def truck_drive(S, k, t, lt):
    f = 0.5 * flick(lt, 0.7)
    A = mood(S, 'road', '3C4656', f, fk=5.0, sunk=1.6)
    if f > 0.25:
        strike(S, A(60, 230, 140), A(70, 220, 25), 12, n=7, w=1.4)
    y = lerp(42, 22, k)
    drv, _ = truck_at(S, A, -1.0, y)
    age(S)
    S['roy'].place((drv[0], drv[1], drv[2] + 0.03 * math.sin(t * 21)), 0.0)
    S['roy'].apply(DRIVE)
    cam(S, A(lerp(3.7, 3.1, k), lerp(8.5, 7.0, k), lerp(3.4, 2.8, k)), A(-0.9, y - 2.5, 2.6), 30)


def bolt_truck(S, k, t, lt):
    v = S['prm'].get('v', 1)
    t0 = 0.4 if v == 1 else 0.22
    f = flick(lt, t0)
    A = mood(S, 'road', '3C4656', f, fk=5.0, sunk=1.6)
    drv, _ = truck_at(S, A, -1.0, 10, 60 + 200 * f)
    win = A(0.5, 9.85, 3.05)
    if f > 0.5:
        if v == 1:
            strike(S, A(16, 26, 70), A(7.6, 12.5, 11.6), 21, n=7, w=0.3)
            strike(S, A(7.6, 12.5, 9.2), win, 22, i0=7, n=5, w=0.16, jit=0.9)
        else:
            strike(S, A(7.6, 12.5, 9.2), A(0.5, 9.5, 3.7), 22, n=6, w=0.09, jit=0.9)
        sparks(S, win, t, 8, r=1.0, speed=4.0, up=0.5)
    flash(S, A(2.4, 8.4, 3.8), f, 9000 if v == 1 else 3500)
    hit = ease((lt - t0) / 0.1)
    age(S, brows=hit < 0.5)
    S['rhat'].rotation_euler = (-0.08 + 0.33 * hit, 0.3 * hit, 0)
    S['roy'].place(drv, 0.0)
    S['roy'].apply(blend(DRIVE, P('sit', aL=(1.3, 0.9, 0.9), aR=(1.3, 0.9, 0.9), lean=-0.1, head=(-0.3, 0.0)) if v == 1 else
                          P('sit', aL=(1.15, 0.25, 0.6), aR=(1.15, 0.25, 0.6), lean=-0.16, head=(-0.38, 0.0)), hit))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'calm'
    S['jaw'] = 0.35 * hit
    if v == 1:
        cam(S, A(lerp(4.3, 4.0, k), lerp(-3.2, -2.2, k), 1.5), A(1.9, 10, 4.8), 24)
    else:
        cam(S, A(lerp(4.3, 3.9, k), lerp(6.2, 6.7, k), 3.3), A(-0.5, 10.3, 3.05), 36, roll=0.04 * math.sin(lt * 31) * hit)


def rook_truck(S, k, t, lt):
    A = mood(S, 'road', '3C4656', 0.0, fk=6.0, sunk=1.6)
    drv, pas = truck_at(S, A, -1.0, 10, 140)
    age(S, brows=False)
    S['rhat'].rotation_euler = (-0.38, 0.35, 0)
    S['roy'].place(drv, 0.0)
    S['roy'].apply(SLUMP)
    S['face']['roy'] = 'shock' if (lt * 2.2) % 1 > 0.25 else 'shut'
    S['jaw'] = 0.2
    smoke(S, (drv[0], drv[1] - 0.2, drv[2] + 2.5), t, 4, rise=0.9, size=0.14, speed=1.2)
    turn = ease(lt / 0.3)
    S['rook'].place(pas, 0.0)
    S['rook'].apply(P('sit', aL=(0.9, 0.5, 1.4), aR=(0.9, 0.5, 1.4), head=(0.0, 0.95 * turn), lean=0.1))
    S['face']['rook'] = 'shocked'
    feather(S, (pas[0], pas[1] - 0.4, pas[2] + 2.6), lt, 0.05, 1)
    cam(S, A(-1.0, lerp(2.9, 3.5, k), lerp(3.6, 3.5, k)), A(-1.0, 10.4, 3.1), 42, fill=1.6)


def patrol_hit(S, k, t, lt):
    f = flick(lt, 0.48)
    A = mood(S, 'road', '424C5A', f, fk=5.0, sunk=1.6)
    truck_at(S, A, -1.5, 11.5, 0)
    hit = ease((lt - 0.48) / 0.1)
    if f > 0.5:
        strike(S, A(5, 16, 70), A(1.9, 7.2, 3.25), 31, n=9, w=0.24)
    flash(S, A(3.0, 5.6, 4.2), f, 8000)
    age(S, hat=hit < 0.5)
    S['roy'].place(A(1.9, 7.2, 0), 0.3)
    S['roy'].apply(blend(P('stand', head=(-0.45, 0.0), aR=(0.3, 0.3, 0.4)), JOLT, hit))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'calm'
    S['jaw'] = 0.35 * hit
    if hit > 0.5:
        u = lt - 0.53
        S['lhat'].location = A(1.9 + 2.2 * u, 7.0 - 1.0 * u, 3.4 + 5.0 * u - 6.0 * u * u)
        S['lhat'].rotation_euler = (u * 7, u * 4, 0)
        burn(S, t, ease((lt - 0.56) / 0.2))
    S['rook'].place(A(3.9, 7.7, 0), 0.25)
    S['rook'].apply(blend(P('cross'), DUCK, hit))
    S['face']['rook'] = 'shocked' if hit > 0.3 else 'deadpan'
    cam(S, A(lerp(6.6, 6.0, k), lerp(0.4, 1.2, k), 1.9), A(1.1, 8.8, 3.1), 30)


def water_can(S, k, t, lt):
    A = mood(S, 'road', '424C5A', 0.0, fk=6.0, sunk=1.6)
    truck_at(S, A, -1.5, 11.5, 0)
    age(S, hat=False)
    S['roy'].place(A(1.9, 7.2, 0), 0.3)
    S['roy'].apply(P('stand', aR=(2.75, 0.25, 0.9, 0.3), aL=(0.4, 0.3, 0.6), head=(0.3, 0.0), lean=0.12))
    S['face']['roy'] = 'shut'
    c = A(2.2, 6.8, 3.75)
    S['can'].location = c
    S['can'].rotation_euler = (-2.0, 0.0, 0.3)
    for i, o in enumerate(S['drops'][:8]):
        u = (lt * 2.6 + i / 8) % 1
        o.location = (c[0] - 0.1 + 0.12 * math.sin(i * 2.3), c[1] - 0.1 + 0.1 * math.cos(i * 1.7), c[2] - 0.25 - 0.75 * u)
    burn(S, t, 1 - ease(lt / 0.45))
    smoke(S, A(1.9, 7.1, 3.0), t, 6, rise=2.4, size=0.3 * ease(lt / 0.5) + 0.02, speed=0.9)
    cam(S, A(lerp(3.9, 3.6, k), lerp(0.6, 1.4, k), 2.5), A(1.95, 7.2, 2.45), 40)


def rook_can(S, k, t, lt):
    A = mood(S, 'road', '424C5A', 0.0, fk=6.0, sunk=1.6)
    truck_at(S, A, -1.5, 11.5, 0)
    age(S, hat=False)
    S['roy'].place(A(0.9, 9.6, 0), -0.35)
    S['roy'].apply(P('hips', head=(0.1, -0.3)))
    S['face']['roy'] = 'tired'
    smoke(S, A(0.9, 9.6, 3.0), t, 4, rise=2.0, size=0.26, speed=0.6)
    sh = ease((lt - 0.6) / 0.22)
    S['rook'].place(A(3.3, 5.6, 0), -0.25)
    S['rook'].apply(blend(P('point', aR=(1.35, 0.1, 0.05), head=(0.25, -0.15)), P('shrug', head=(-0.05, 0.1)), sh))
    S['face']['rook'] = 'deadpan'
    if sh < 0.05:
        S['can'].location = A(3.52, 4.5, 1.62 + (0.12 * math.sin(lt * 30) if lt < 0.45 else 0.0))
        S['can'].rotation_euler = (PI, 0.0, 0.3 + (0.2 * math.sin(lt * 23) if lt < 0.45 else 0.0))
    else:
        u = lt - 0.6
        S['can'].location = A(3.52, 4.3, max(0.3, 1.62 - 5.0 * u * u))
        S['can'].rotation_euler = (PI + u * 6, 0.3, 0.3)
    if 0.12 < lt < 0.6:
        u = (lt - 0.12) / 0.48
        S['drops'][0].location = A(3.52, 4.5, 1.3 - 1.25 * u * u)
    cam(S, A(lerp(1.8, 2.5, k), lerp(-0.2, 1.2, k), lerp(2.3, 2.5, k)), A(3.1, 5.6, 2.55), 44)


def roy_steam(S, k, t, lt):
    """Doused: wet, steaming, he looks up at the sky again."""
    A = mood(S, 'road', '424C5A', 0.0, fk=6.0, sunk=1.6)
    truck_at(S, A, -1.5, 11.5, 0)
    age(S, hat=False)
    up = ease((lt - 0.2) / 0.35)
    S['roy'].place(A(1.9, 7.2, 0), 0.3)
    S['roy'].apply(P('stand', aL=(0.25, 0.3, 0.4), aR=(0.25, 0.3, 0.4), head=(0.2 - 0.6 * up, 0.25 * math.sin(lt * 5) * up)))
    S['face']['roy'] = 'shut' if up < 0.4 else 'scared'
    smoke(S, A(1.9, 7.1, 2.95), t, 6, rise=2.2, size=0.2, speed=1.1)
    for i, o in enumerate(S['drops'][:6]):
        u = (lt * 1.8 + i / 6) % 1
        o.location = A(1.9 + 0.4 * math.sin(i * 2.4), 7.0 + 0.2 * math.cos(i * 1.3), 2.5 - 1.6 * u)
    cam(S, A(lerp(3.3, 2.9, k), lerp(3.0, 3.8, k), lerp(2.5, 2.7, k)), A(1.95, 7.2, 2.6), 52)


# ---------------------------------------------------------------- shots: his front yard (strike 3, 1970)
def yard_wide(S, k, t, lt):
    f = 0.5 * flick(lt, 0.7)
    A = mood(S, 'yard', '525E6E', f, fk=5.0)
    if f > 0.25:
        strike(S, A(70, 260, 150), A(60, 250, 25), 16, n=7, w=1.4)
    age(S)
    S['roy'].place(A(lerp(-1.6, 1.0, k), lerp(6.6, 3.2, k), 0), 0.66)
    S['roy'].apply(walk(t, 1.5))
    e = ease(k)
    cam(S, A(lerp(-8.6, -7.2, e), lerp(-12.6, -11.4, e), lerp(5.4, 4.3, e)), A(2.6, 5, 4.4), 26)


def yard_hit(S, k, t, lt):
    f = flick(lt, 0.33)
    A = mood(S, 'yard', '525E6E', f, fk=5.0)
    tx = A(8.75, 6.8, 9.0)
    hit = ease((lt - 0.33) / 0.1)
    if f > 0.5:
        strike(S, A(15, 18, 70), A(8.75, 6.8, 10.1), 41, n=8, w=0.3)
        strike(S, tx, A(3.95, 0.7, 2.15), 42, i0=8, n=6, w=0.15, jit=1.0)
        sparks(S, tx, t, 12, r=2.2, speed=3.5)
    flash(S, A(4.8, -0.6, 3.4), f, 8000)
    age(S)
    S['roy'].place(A(3.4, 0.6, 0), 0.5)
    S['roy'].apply(blend(walk(t, 1.5), dict(JOLT, aR=(0.2, 0.4, 0.6, 0.0), aL=(0.9, 1.4, 0.6, 0.0), head=(-0.2, 0.5)), hit))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'calm'
    S['jaw'] = 0.35 * hit
    if lt > 0.5:
        smoke(S, A(3.95, 0.7, 2.3), t, 3, rise=1.2, size=0.15, speed=1.4)
    S['rook'].place(A(0.5, -1.0, 0), PI * 0.5 - 0.35)
    S['rook'].apply(blend(P('hips', head=(-0.2, 0.0)), DUCK, hit))
    S['face']['rook'] = 'shocked' if hit > 0.3 else 'deadpan'
    feather(S, A(0.6, -1.2, 3.2), lt, 0.4)
    cam(S, A(lerp(-0.7, -0.3, k), lerp(-7.4, -6.6, k), 2.0), A(4.7, 3.2, 4.7), 28)


# ---------------------------------------------------------------- shots: the ranger station (strike 4, 1972)
def room(S, f=0.0):
    A = mood(S, 'station', '0A0E18', 0.0, fk=3.4)
    S['st_top'].data.energy = 1100
    tint(S['st_pane'], mix_col('3A4A66', 'FFFFFF', f), 1.2 + 14 * f)
    S['st_win'].data.energy = 60 + 2600 * f
    return A


def rook_seat(S, A, t, lt, look=0.0):
    S['rook'].place(A(1.6, 5.4, 0), -PI / 4)
    S['rook'].apply(P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.9, 0.2, 1.2, 0.0), head=(-0.05 * look, -0.85 * look)))
    u = (lt * 1.5) % 1
    S['coin'].location = A(1.55, 4.45, 1.5 + 0.6 * 4 * u * (1 - u))
    S['coin'].rotation_euler = (lt * 30, 0.4, 0)


def roy_desk(S, A, t):
    age(S, hat=False)
    S['roy'].place(A(-2.4, 8.3, 0), 0.0)
    S['roy'].apply(P('sit', aL=(0.95, -0.1, 1.2, 0.8), aR=(0.95 + 0.05 * math.sin(t * 9), -0.1, 1.2, 0.8), head=(0.32, 0.0)))
    S['lhat'].location = A(-0.3, 6.5, 1.7)
    S['lhat'].rotation_euler = (0, 0, 0.4)


def station_in(S, k, t, lt):
    f = 0.45 * flick(lt, 0.75)
    A = room(S, f)
    roy_desk(S, A, t)
    rook_seat(S, A, t, lt)
    S['face']['rook'] = 'deadpan'
    e = ease(k)
    cam(S, A(lerp(5.6, 4.6, e), lerp(-2.6, -2.2, e), lerp(4.3, 3.8, e)), A(-0.8, 7.0, 2.3), 22, fcol='FFD8B0')


def rook_desk(S, k, t, lt):
    f = 0.5 * flick(lt, 0.8)
    A = room(S, f)
    roy_desk(S, A, t)
    rook_seat(S, A, t, lt, ease((lt - 0.85) / 0.25))
    S['face']['rook'] = 'deadpan' if lt < 0.85 else 'calm'
    cam(S, A(lerp(-1.7, -1.2, k), lerp(1.3, 1.9, k), 2.35), A(1.5, 5.3, 2.3), 46, fcol='FFD8B0')


def station_hit(S, k, t, lt):
    f = flick(lt, 0.2)
    A = room(S, f)
    hit = ease((lt - 0.2) / 0.1)
    if f > 0.5:
        strike(S, A(-3.25, 12.2, 4.7), A(-2.4, 8.5, 2.95), 51, n=5, w=0.16, jit=1.6)
    flash(S, A(-2.0, 7.0, 4.6), f, 1800)
    age(S, hat=False)
    S['lhat'].location = A(-0.3, 6.5, 1.7)
    S['lhat'].rotation_euler = (0, 0, 0.4)
    S['roy'].place(A(-2.4, 8.5, 0), 0.0)
    S['roy'].apply(blend(P('sit', aL=(0.95, -0.1, 1.2, 0.8), aR=(0.95, -0.1, 1.2, 0.8), head=(0.32, 0.0)), JOLT, hit))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'calm'
    S['jaw'] = 0.35 * hit
    burn(S, t, ease((lt - 0.28) / 0.2))
    S['rook'].place(A(lerp(1.6, 2.7, hit), lerp(5.4, 4.5, hit), 0), lerp(-PI / 4, 0.3, hit))
    S['rook'].apply(blend(P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.9, 0.2, 1.2, 0.0)),
                          P('up', aL=(1.2, 1.2, 1.0), aR=(1.2, 1.2, 1.0), lean=-0.2, head=(-0.05, -1.0)), hit))
    S['face']['rook'] = 'shocked' if hit > 0.2 else 'deadpan'
    u = max(0.0, lt - 0.2)
    S['coin'].location = A(1.0 + 1.5 * u, 4.6, 2.2 + 3.5 * u - 5.0 * u * u)
    S['coin'].rotation_euler = (lt * 40, 0.4, 0)
    feather(S, A(1.9, 5.3, 3.3), lt, 0.25)
    cam(S, A(lerp(4.3, 3.8, k), lerp(0.2, 0.9, k), 2.9), A(-0.5, 7.6, 3.05), 30, roll=0.04 * math.sin(lt * 33) * hit, fcol='FFD8B0')


def roy_sink(S, k, t, lt):
    A = room(S, 0.0)
    S['fillk'] = 4.0
    age(S, hat=False)
    S['roy'].place(A(5.5, 9.9, 0), PI)
    press = 0.06 * math.sin(lt * 14)
    S['roy'].apply(P('hat', aL=(0.2, 1.9, 1.6, -1.5), lean=0.28, head=(0.3 + press, 0.0)))
    S['face']['roy'] = 'shut'
    S['towel'].scale = (0.62, 0.5, 0.14)
    S['towel'].location = A(5.5, 10.45, 2.86 + 0.03 * math.sin(lt * 14))
    S['towel'].rotation_euler = (-0.4, 0.0, 0.08)
    burn(S, t, 0.5 * (1 - ease(lt / 0.3)))
    smoke(S, A(5.5, 10.4, 3.05), t, 6, rise=2.0, size=0.17, speed=1.0)
    for i, o in enumerate(S['drops'][:5]):
        u = (lt * 2.4 + i / 5) % 1
        o.location = A(5.5 + 0.3 * math.sin(i * 2.2), 10.5 + 0.1 * math.cos(i), 2.6 - 0.5 * u)
    cam(S, A(lerp(0.3, 0.9, k), lerp(9.2, 9.4, k), 2.7), A(5.5, 10.6, 2.45), 34, fill=1.6, fcol='FFE0C0')


def rook_tally(S, k, t, lt):
    A = room(S, 0.0)
    S['fillk'] = 3.5
    draw = ease((lt - 0.15) / 0.3)
    done = ease((lt - 0.55) / 0.25)
    vis(S['marks'][:6], True)
    vis(S['marks'][6:], lt > 0.42)
    S['rook'].place(A(7.1, 4.1, 0), PI / 2)
    S['rook'].apply(blend(blend(P('stand'), P('reach', aR=(2.05, 0.05, 0.25), head=(-0.2, 0.0)), draw), P('hips', head=(0.0, -1.15)), done))
    S['face']['rook'] = 'calm' if done < 0.5 else 'shocked'
    cam(S, A(lerp(3.3, 3.6, k), lerp(0.7, 1.2, k), 3.3), A(8.2, 5.6, 3.5), 30, fill=1.4, fcol='FFE0C0')


# ---------------------------------------------------------------- shots: the pond (strike 7, 1977) and afterwards
FISH = P('stand', aL=(1.0, 0.15, 0.9), aR=(1.1, 0.1, 0.7), head=(-0.05, 0.0))
END = (0.0, 9.6, 0.62)                                    # where he stands at the end of the jetty


def rod_at(S, A, x, y, z, tilt=-0.45, yaw=PI):
    S['rod'].location = A(x, y, z)
    S['rod'].rotation_euler = (tilt, 0, yaw)


def bolt_pond(S, k, t, lt):
    f = flick(lt, 0.35)
    A = mood(S, 'pond', DUSK, f, fk=4.0)
    hit = ease((lt - 0.35) / 0.1)
    if f > 0.5:
        pts = strike(S, A(-5, 26, 70), A(0, 9.6, 3.55), 61, n=9, w=0.28)
        branch(S, pts[3], 4, 9, w=0.12, L=8)
    flash(S, A(-1.2, 7.6, 4.4), f, 12000)
    age(S, hat=hit < 0.5)
    S['roy'].place(A(*END), PI)
    S['roy'].apply(blend(FISH, JOLT, hit))
    rod_at(S, A, 0.1, 10.3, 2.25 - 0.2 * hit, -0.45 + 0.9 * hit)
    if hit > 0.5:
        u = lt - 0.4
        S['lhat'].location = A(-1.6 * u, 9.6 - 0.5 * u, 3.5 + 5.0 * u - 6.0 * u * u)
        S['lhat'].rotation_euler = (u * 6, u * 5, 0)
        burn(S, t, ease((lt - 0.45) / 0.2))
    cam(S, A(lerp(-2.7, -2.2, k), lerp(0.4, 1.5, k), 1.25), A(0, 9.4, lerp(3.6, 3.9, k)), 26)


def pond_wide(S, k, t, lt):
    f = 0.5 * flick(lt, 0.72)
    A = mood(S, 'pond', '5A6488', f, fk=8.5)
    if f > 0.25:
        strike(S, A(50, 280, 150), A(40, 270, 25), 17, n=7, w=1.5)
    age(S)
    S['roy'].place(A(*END), PI)
    S['roy'].apply(dict(FISH, aR=(1.1 + 0.15 * math.sin(lt * 5), 0.1, 0.7, 0.0)))
    rod_at(S, A, 0.1, 10.3, 2.25, -0.45 - 0.12 * math.sin(lt * 5))
    S['rook'].place(A(-4.2, -0.4, 0.72), PI + 0.35)
    S['rook'].apply(P('sit', head=(-0.45 * ease((lt - 0.7) / 0.3), 0.2), aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3)))
    e = ease(k)
    cam(S, A(lerp(-2.6, -2.2, e), lerp(-7.2, -6.4, e), lerp(3.8, 3.3, e)), A(-2.2, 6, 2.3), 24)


def pond_hit(S, k, t, lt):
    f = flick(lt, 0.16)
    A = mood(S, 'pond', DUSK, f, fk=4.5)
    hit = ease((lt - 0.16) / 0.1)
    if f > 0.5:
        strike(S, A(4, 0, 70), A(0, 9.6, 3.5), 62, n=9, w=0.22)
    flash(S, A(1.0, 11.4, 4.2), f, 7000)
    age(S, hat=hit < 0.5)
    S['roy'].place(A(*END), PI)
    S['roy'].apply(blend(FISH, JOLT, hit))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'calm'
    S['jaw'] = 0.35 * hit
    rod_at(S, A, 0.1, 10.3, 2.25 - 1.0 * hit, -0.45 + 1.1 * hit)
    if hit > 0.5:
        u = lt - 0.21
        S['lhat'].location = A(1.5 * u, 9.9 + 0.6 * u, 3.5 + 5.0 * u - 6.0 * u * u)
        S['lhat'].rotation_euler = (u * 6, u * 5, 0)
        burn(S, t, ease((lt - 0.24) / 0.2))
    S['rook'].place(A(-0.85, 7.7, 0.62), PI + 0.3)
    S['rook'].apply(blend(P('stand', head=(-0.3, 0.0)), DUCK, hit))
    S['face']['rook'] = 'shocked' if hit > 0.3 else 'calm'
    feather(S, A(-0.9, 8.0, 3.6), lt, 0.25)
    cam(S, A(lerp(2.7, 2.3, k), lerp(15.6, 14.9, k), 1.7), A(-0.3, 9.2, 3.1), 32, roll=0.04 * math.sin(lt * 31) * hit)


def roy_burns(S, k, t, lt):
    A = mood(S, 'pond', '3A4058', 0.0, fk=6.0)
    age(S, hat=False)
    vis(S['scorch'], True)
    S['roy'].place(A(1.05, 8.5, 0.17), PI / 2)
    S['roy'].apply(P('sit', aR=(0.95, -0.25, 1.95, 1.2), aL=(0.3, 0.3, 0.4), head=(0.35 - 0.12 * ease(lt / 1.2), 0.0), lean=0.22))
    S['face']['roy'] = 'tired'
    smoke(S, A(1.2, 8.5, 2.3), t, 3, rise=1.4, size=0.11, speed=0.5)
    S['bhat'].location = A(0.7, 7.0, 0.66)
    S['bhat'].rotation_euler = (0, 0, 0.7)
    S['rook'].place(A(0.1, 10.1, 0.62), 1.2)
    S['rook'].apply(dict(KNEEL, aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.15, -0.45)))
    S['hat_off'] = ease(lt / 0.5)
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(7.0, 6.4, k), lerp(11.9, 11.6, k), lerp(2.2, 2.1, k)), A(0.6, 9.2, 1.95), 40, fill=1.5)


def golden(S):
    A = mood(S, 'pond', 'D8A070', 0.0, fk=7.0, sunk=2.4, sunc='FFD0A0')
    return A


def roy_hat(S, k, t, lt):
    A = golden(S)
    age(S, hat=False)
    S['roy'].place(A(3.4, -1.6, 0), 0.0)
    S['roy'].apply(P('stand', aL=(0.6, -0.15, 1.1, 0.8), aR=(0.6, -0.15, 1.1, 0.8), head=(0.05 - 0.12 * ease(lt / 0.8), 0.0)))
    S['face']['roy'] = 'warm'
    S['bhat'].location = A(3.4, -2.2, 1.52)
    S['bhat'].rotation_euler = (0.9, 0, 0.0)
    cam(S, A(lerp(4.6, 4.2, k), lerp(-8.8, -7.6, k), 2.5), A(3.4, -1.6, 2.4), 50, fcol='FFE0C0')


def rook_shock(S, k, t, lt):
    A = golden(S)
    pop = ease(lt / 0.15)
    S['rook'].place(A(-2.2, -1.2, 0), 0.15)
    S['rook'].apply(blend(P('cross'), P('stand', aL=(0.5, 1.1, 0.6), aR=(0.5, 1.1, 0.6), lean=-0.15, head=(-0.12, 0.0)), pop))
    S['face']['rook'] = 'shocked' if pop > 0.3 else 'deadpan'
    feather(S, A(-2.0, -1.5, 3.3), lt, 0.1)
    cam(S, A(lerp(-1.4, -1.7, k), lerp(-7.0, -6.0, k), 2.8), A(-2.2, -1.2, 3.1), 50, fcol='FFE0C0')


def rook_wrong(S, k, t, lt):
    A = mood(S, 'pond', '8A7890', 0.0, fk=6.0, sunk=1.6, sunc='FFD0A0')
    S['rook'].place(A(0, 9.6, 0.62), PI - 0.2)
    off = ease((lt - 0.1) / 0.4)
    S['hat_off'] = off
    S['rook'].apply(blend(P('hat', head=(0.1, 0)), hat_hold(head=(0.25, 0.0)), off) if lt > 0.1 else blend(P('stand'), P('hat', head=(0.1, 0)), lt / 0.1))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-1.5, -1.1, k), lerp(14.8, 14.0, k), lerp(3.0, 3.2, k)), A(0, 9.6, 3.25), 50, fill=1.4, fcol='FFE0C0')


def signoff(S, k, t, lt):
    f = 0.35 * flick(lt, 1.0)
    A = mood(S, 'pond', '8A7890', f, fk=6.0, sunk=1.6, sunc='FFD0A0')
    pick = ease(lt / 0.4)
    pocket = ease((lt - 0.45) / 0.35)
    look = ease((lt - 1.0) / 0.2)
    pull = ease((lt - 1.25) / 0.25)
    S['rook'].place(A(0.3, 8.3, 0.62), PI + 0.45)
    down = P('stand', aR=(1.0, 0.2, 0.25), lean=0.5, head=(0.35, -0.3), lL=(0.3, 0.5), lR=(0.3, 0.5), lift=-0.1)
    p = blend(P('stand'), down, math.sin(pick * PI * 0.5) * (1 - pocket))
    p = blend(p, P('stand', aR=(0.5, -0.1, 1.5, 1.0), head=(0.0, -0.2)), pocket * (1 - look))
    p = blend(p, P('stand', head=(-0.55, 0.0)), look * (1 - pull))
    p = blend(p, P('hat', head=(0.2, -0.25)), pull)
    S['rook'].apply(p)
    S['hat_tip'] = pull
    S['face']['rook'] = 'warm' if lt < 1.0 else ('shocked' if pull < 0.5 else 'deadpan')
    if pocket < 0.95:
        S['lure'].location = A(lerp(-0.25, 0.05, pocket), lerp(9.45, 8.75, pocket), lerp(0.72, 1.9, pocket) + 0.3 * math.sin(pocket * PI))
        S['lure'].rotation_euler = (0, 0, 0.6 + lt * 3)
        S['glow'].location = A(-0.2, 9.9, 1.4)
        S['glow'].data.energy = 60
        S['glow'].data.color = K.hexc('FFE8C0')[:3]
    cam(S, A(lerp(2.7, 2.2, k), lerp(13.8, 12.8, k), 2.6), A(0.3, 8.6, 2.65), 38, fcol='FFE0C0')


# ---------------------------------------------------------------- shots: the exhibit hall (two of his hats went on display)
def hats_case(S, k, t, lt):
    A = mood(S, 'hall', '15131C', 0.0, fk=3.2)
    S['rook'].place(A(-1.0, -3.5, 0), 2.85)
    S['rook'].apply(dict(THINK, head=(0.1, 0.1 * math.sin(lt * 3))))
    e = ease(k)
    cam(S, A(lerp(3.6, 2.5, e), lerp(-9.6, -8.3, e), lerp(3.7, 3.3, e)), A(-0.9, 0, 3.0), 32, fill=1.8, fcol='FFE0C0')


def rook_hats(S, k, t, lt):
    A = mood(S, 'hall', '15131C', 0.0, fk=3.6)
    S['rook'].place(A(-0.2, -2.7, 0), PI)
    S['rook'].apply(dict(THINK, lean=0.28, head=(-0.1, 0.25 * math.sin(lt * 4.5))))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(1.0, 0.6, k), lerp(4.6, 4.1, k), 3.9), A(-0.2, -2.2, 3.05), 42, fcol='FFE0C0')


# ---------------------------------------------------------------- photographs for the case board
def photo_tower(S, k, t, lt):
    A = mood(S, 'ridge', '2A3850', 0.0, fk=5.0, sunk=2.0)
    age(S, grey=False)
    S['roy'].place(A(-3.0, 3.0, 0), -0.3)
    S['roy'].apply(P('hips'))
    cam(S, A(-5.6, -5.5, 1.6), A(-1.2, 9, 6.6), 24)


def photo_roy(S, k, t, lt):
    A = golden(S)
    age(S, hat=False)
    S['roy'].place(A(1.6, -1.6, 0), 0.0)
    S['roy'].apply(P('stand', aL=(0.6, -0.15, 1.1, 0.8), aR=(0.6, -0.15, 1.1, 0.8)))
    S['face']['roy'] = 'warm'
    S['bhat'].location = A(1.6, -2.2, 1.52)
    S['bhat'].rotation_euler = (0.9, 0, 0.0)
    cam(S, A(1.9, -7.4, 2.5), A(1.6, -1.6, 2.35), 50, fcol='FFE0C0')


SHOTS3D = {f.__name__: f for f in (
    bolt_tower, bolt_truck, bolt_pond, rook_gate, rook_collar, tower_wide, roy_tower, tower_hit, roy_runs, truck_drive, rook_truck,
    yard_wide, yard_hit, station_in, rook_desk, station_hit, roy_sink, patrol_hit, water_can, roy_steam, rook_can, trail_hit, roy_hop,
    pond_wide, pond_hit, roy_burns, rook_tally, roy_hat, rook_shock, hats_case, rook_hats, rook_wrong, signoff)}
STILLS = dict(tower=photo_tower, roy=photo_roy)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it: a stone overlook on the ridge (who he was, the 27 quiet years, the people who
# kept their distance, the last six years), the back yard with the washing line (the day his wife was hit), an
# office where the strikes were written up, and new shots on the Short's sets (the new tower by daylight, the tower
# on fire, the burned leg, the cab before and after the 1969 strike, the water can going into the truck, the cloud
# over the patrol, the front yard afterwards, the fourth chalk mark, the empty jetty). Still generic: no badge, logo
# or agency marking anywhere, and the extra people (his wife, two rangers, the man at the typewriter) are stand-ins,
# not likenesses.
import bmesh  # noqa: E402

ORG.update(look=(3000, 0, 0), wash=(3500, 0, 0), office=(4000, 0, 0))
WIFE = dict(top='7E9AB0', pants='6A86A0', hand='E8C0A0', boot='E8E0D0')
SUP = dict(top='4A4E58', pants='3A3E48', hand='D8AC84', boot='1C1C20', fore='E8E8EC')
_kit_add = add


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """The kit's add() goes through Blender operators, which get slower as the scene fills up. This builds the same
    primitives straight from mesh data. From here on the whole file uses it (the Short's sets look the name up when
    they run), so the nine sets build in seconds."""
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'plane':
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=kw.get('size', 2.0) / 2)
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


def leafy(r, x, y, s=1.0, i=0):
    add('cylinder', '3A2A1E', (x, y, 1.6 * s), radius=0.45 * s, depth=3.2 * s, vertices=6, parent=r)
    add('ico_sphere', ('2E5234', '3A6240', '28482E')[i % 3], (x, y, 5.6 * s), scale=(1, 1, 1.15), radius=3.6 * s, subdivisions=1, parent=r)


# ---------------------------------------------------------------- set 7: the overlook
def set_look(r):
    add('plane', '2C4630', (0, 0, -0.02), size=3000, parent=r)
    box('6E6A60', (0, 0, 0.03), (34, 13, 0.06), r)                                         # the paved terrace
    for i in range(11):
        box('625E56', (-15 + i * 3.0, 0, 0.065), (0.05, 13, 0.01), r)
    for i in range(23):                                                                    # the stone wall at the edge
        box(('7A766C', '6A665E', '86827A')[i % 3], (-16.5 + i * 1.5, 6.3, 0.5 + 0.06 * (i % 2)), (1.44, 0.8, 1.0 + 0.12 * (i % 2)), r)
    box('1C2C26', (0, 90, -9), (700, 160, 14), r)                                          # the drop beyond it
    for row, (y0, c) in enumerate(((60, '2A4636'), (95, '2E4E46'), (135, '345660'))):       # wooded slopes below
        for i in range(15):
            x = -330 + i * 47 + rnd(i, row) * 20
            add('cone', c, (x, y0 + rnd(i, row + 3) * 14, -8 + row * 3), radius1=34 + 12 * rnd(i, row + 5), radius2=3,
                depth=16 + 10 * rnd(i, row + 7), vertices=6, parent=r)
    ridges(r, 230, ('3E566C', '4E667C', '60788C'), n=13, span=1100, hgt=60)
    bn = empty((2.6, 2.0, 0), r)                                                           # the bench, facing the view
    box('6A5236', (0, 0, 0.5), (4.4, 0.95, 0.12), bn)
    for z in (0.95, 1.3):
        box('6A5236', (0, -0.52, z), (4.4, 0.1, 0.26), bn)
    for sx in (-1, 1):
        box('3A3A3E', (sx * 1.9, -0.1, 0.25), (0.14, 0.9, 0.5), bn)
        box('3A3A3E', (sx * 1.9, -0.52, 0.85), (0.14, 0.12, 1.1), bn)
    sc_ = empty((-6.5, 5.3, 0), r)                                                         # a viewing scope on a post
    add('cylinder', '4A4A50', (0, 0, 1.0), radius=0.14, depth=2.0, vertices=6, parent=sc_)
    add('cylinder', '8A8E96', (0, 0.1, 2.2), rot=(PI / 2 - 0.15, 0, 0), radius=0.26, depth=0.9, vertices=8, parent=sc_, rough=0.4)
    sg = empty((-11, -3.5, 0), r)                                                          # a blank trail sign
    for sx in (-1, 1):
        add('cylinder', '5A4630', (sx * 1.3, 0, 1.5), radius=0.14, depth=3.0, vertices=6, parent=sg)
    box('6E5638', (0, 0, 2.3), (3.2, 0.16, 1.3), sg)
    box('FF7A1A', (0, 0.1, 1.85), (2.8, 0.03, 0.12), sg, emit=0.4)
    box('5A4E3A', (0, -45, 0.02), (3.4, 78, 0.05), r)                                      # the path back into the woods
    for i in range(70):
        x = (rnd(i, 21) - 0.5) * 170
        y = -9 - rnd(i, 22) * 70
        if abs(x) < 4.2:
            continue
        pine(r, x, y, 1.0 + rnd(i, 23) * 1.0, i)
    for i in range(16):
        sx = -1 if i % 2 else 1
        pine(r, sx * (21 + rnd(i, 24) * 30), -6 + rnd(i, 25) * 11, 1.0 + rnd(i, 26) * 0.8, i)
    for i in range(7):
        add('ico_sphere', ('4A4A48', '5A5852')[i % 2], (-15 + rnd(i, 27) * 30, -5.4 - rnd(i, 28) * 2, 0.25), scale=(1.4, 1, 0.7),
            radius=0.5 + rnd(i, 29) * 0.6, subdivisions=1, parent=r)
    tgt = empty((0, 2, 2), r)
    sun = light((70, 60, 120), 2.0, 'FFF0D8', kind='SUN', target=tgt, parent=r)
    return dict(look_sun=sun)


# ---------------------------------------------------------------- set 8: the back yard and the washing line
def set_wash(r):
    add('plane', '2E4A30', (0, 0, -0.02), size=3000, parent=r)
    hs = empty((0, 14, 0), r)                                                              # the back of the house
    box('CFC8B2', (0, 0, 3.4), (22, 0.6, 6.8), hs)
    box('5A3A30', (0, 0.9, 7.6), (23.4, 6.0, 0.3), hs, rot=(-0.5, 0, 0))
    box('4A3226', (-5.0, -0.34, 2.0), (1.9, 0.1, 3.6), hs)                                 # back door and step
    box('8E8676', (-5.0, -1.2, 0.2), (3.0, 1.8, 0.4), hs)
    winm = own_mat('washwin', 'FFD890', 2.2)
    for x in (2.5, 7.5):
        use(box('FFD890', (x, -0.34, 3.5), (2.4, 0.1, 2.0), hs), winm)
        box('E8E2D0', (x, -0.4, 3.5), (0.12, 0.06, 2.0), hs)
        box('E8E2D0', (x, -0.4, 3.5), (2.4, 0.06, 0.12), hs)
    box('8A4A3A', (-8.5, 1.5, 8.6), (1.3, 1.3, 3.0), hs)
    for sx in (-1, 1):                                                                     # the line: two T posts, three wires
        add('cylinder', '5A4630', (sx * 6.2, 2.0, 1.9), radius=0.14, depth=3.8, vertices=6, parent=r)
        box('5A4630', (sx * 6.2, 2.0, 3.72), (0.14, 2.0, 0.14), r)
    for y in (1.3, 2.0, 2.7):
        box('1E1E1E', (0, y, 3.74), (12.4, 0.03, 0.03), r)
    for x, w_, hgt, c, y in ((-4.6, 2.3, 2.0, 'F2F0E8', 2.0), (-2.9, 0.9, 1.1, 'B8CCE0', 1.3), (3.4, 1.0, 1.2, 'E8C8B0', 2.7),
                             (4.7, 2.0, 2.0, 'E8E4D8', 2.0), (-5.3, 0.8, 1.0, 'D8B0A0', 2.7)):
        box(c, (x, y, 3.7 - hgt / 2), (w_, 0.05, hgt), r, rot=(0.04, 0, 0))
    bk = empty((2.2, 3.6, 0), r)                                                           # the basket
    add('cone', 'B89A60', (0, 0, 0.32), rot=(PI, 0, 0), radius1=0.5, radius2=0.66, depth=0.64, vertices=8, parent=bk)
    add('ico_sphere', 'F2F0E8', (0, 0, 0.62), scale=(1, 1, 0.5), radius=0.55, subdivisions=1, parent=bk)
    for sx in (-1, 1):                                                                     # side fences
        for i in range(16):
            box('E0DACA', (sx * 12.5, -9 + i * 1.5, 0.9), (0.1, 0.34, 1.8), r)
        box('E0DACA', (sx * 12.5, 2.2, 1.2), (0.08, 23, 0.16), r)
    sh = empty((-9.2, 8.6, 0), r)                                                          # a garden shed
    box('7A4A38', (0, 0, 1.8), (3.6, 3.2, 3.6), sh)
    box('3E322C', (0, 0, 3.85), (4.2, 3.8, 0.3), sh, rot=(0, 0.14, 0))
    box('4A2E24', (0.6, -1.62, 1.5), (1.3, 0.06, 2.8), sh)
    wb = empty((8.6, 5.6, 0), r)                                                           # a wheelbarrow
    box('5A7A5A', (0, 0, 0.9), (1.3, 1.9, 0.6), wb, rot=(0.12, 0, 0))
    add('cylinder', '1A1A1C', (0, -1.2, 0.4), rot=(0, PI / 2, 0), radius=0.4, depth=0.16, vertices=10, parent=wb)
    for sx in (-1, 1):
        box('3A2A1E', (sx * 0.5, 1.5, 0.9), (0.08, 1.4, 0.08), wb, rot=(0.2, 0, 0))
        box('3A2A1E', (sx * 0.5, 0.8, 0.3), (0.08, 0.08, 0.6), wb)
    for i in range(12):
        sx = -1 if i % 2 else 1
        leafy(r, sx * (17 + rnd(i, 31) * 16), -6 + rnd(i, 32) * 30, 1.0 + rnd(i, 33) * 0.5, i)
    for i in range(9):
        leafy(r, -44 + i * 11 + rnd(i, 34) * 4, 30 + rnd(i, 35) * 12, 1.3 + rnd(i, 36) * 0.5, i + 1)
    ridges(r, 210, ('34485A', '40566A'), span=900, hgt=55)
    tgt = empty((0, 3, 2), r)
    sun = light((-60, -90, 120), 1.8, 'A8B8D0', kind='SUN', target=tgt, parent=r)
    return dict(wash_sun=sun)


# ---------------------------------------------------------------- set 9: the office where it was written up
def set_office(r):
    box('4A3A2C', (0, 4, -0.1), (18, 14, 0.2), r)
    box('6A3E36', (0.4, 4.6, 0.01), (8.4, 5.4, 0.02), r)                                   # a rug
    box('3E3830', (0, 4, 7.6), (18, 14, 0.2), r)
    wall = '6C7462'
    box(wall, (-6.25, 10.1, 3.75), (5.5, 0.2, 7.5), r)                                     # back wall round the window
    box(wall, (4.5, 10.1, 3.75), (9, 0.2, 7.5), r)
    box(wall, (-1.75, 10.1, 1.15), (3.5, 0.2, 2.3), r)
    box(wall, (-1.75, 10.1, 6.35), (3.5, 0.2, 2.3), r)
    box(wall, (-9.0, 4, 3.75), (0.2, 14, 7.5), r)
    box(wall, (9.0, 4, 3.75), (0.2, 14, 7.5), r)
    box('4A5244', (0, 10.0, 0.4), (18, 0.1, 0.8), r)
    for sx in (-1, 1):
        box('4A5244', (sx * 8.9, 4, 0.4), (0.1, 14, 0.8), r)
    panem = own_mat('offpane', '5A6E9A', 1.6)
    use(box('5A6E9A', (-1.75, 10.3, 3.75), (3.5, 0.05, 2.9), r), panem)
    for x in (-3.5, -1.75, 0.0):
        box('2E2A24', (x, 10.0, 3.75), (0.16, 0.3, 2.9), r)
    for z in (2.3, 3.75, 5.2):
        box('2E2A24', (-1.75, 10.0, z), (3.6, 0.3, 0.16), r)
    for i, x in enumerate((3.0, 4.7, 6.4)):                                                # filing cabinets
        box(('5A6A5E', '52625A')[i % 2], (x, 9.3, 2.3), (1.6, 1.3, 4.6), r, rough=0.5)
        for j in range(4):
            box('3A463E', (x, 8.63, 0.75 + j * 1.1), (1.4, 0.03, 0.04), r)
            box('C8C8C0', (x, 8.6, 1.2 + j * 1.1), (0.5, 0.06, 0.1), r, rough=0.3)
    box('2E2A24', (-6.0, 9.95, 4.4), (2.6, 0.08, 2.0), r)                                   # a framed sketch of ridgelines
    box('C8BE9A', (-6.0, 9.9, 4.4), (2.3, 0.06, 1.7), r)
    for i in range(3):
        box('6A7A5A', (-6.0 + (i - 1) * 0.3, 9.86, 4.0 + i * 0.3), (1.9 - i * 0.4, 0.02, 0.05), r, rot=(0, 0.12 * (i - 1), 0))
    add('cylinder', 'E8E4D8', (7.4, 9.92, 5.6), rot=(PI / 2, 0, 0), radius=0.6, depth=0.1, vertices=12, parent=r)   # wall clock
    add('cylinder', '2E2A24', (7.4, 9.95, 5.6), rot=(PI / 2, 0, 0), radius=0.68, depth=0.08, vertices=12, parent=r)
    box('1A1A1A', (7.4, 9.85, 5.8), (0.05, 0.02, 0.42), r)
    box('1A1A1A', (7.55, 9.85, 5.6), (0.3, 0.02, 0.05), r)
    cs = empty((-7.6, 8.4, 0), r)                                                          # coat stand
    add('cylinder', '3A2C20', (0, 0, 2.6), radius=0.09, depth=5.2, vertices=6, parent=cs)
    add('cylinder', '3A2C20', (0, 0, 0.06), radius=0.6, depth=0.12, vertices=8, parent=cs)
    for a in range(4):
        box('3A2C20', (0.25 * math.cos(a * PI / 2), 0.25 * math.sin(a * PI / 2), 5.0), (0.5, 0.06, 0.06), cs, rot=(0, -0.5, a * PI / 2))
    box('5A6050', (0.3, -0.1, 3.9), (0.9, 0.5, 2.0), cs)                                    # a coat on it
    dk = empty((0.4, 5.0, 0), r)                                                           # the desk
    box('5A4028', (0, 0, 1.55), (5.4, 2.4, 0.2), dk)
    for sx in (-1, 1):
        box('4A3420', (sx * 2.2, 0, 0.75), (0.9, 2.2, 1.5), dk)
    box('4A3420', (0, 0.9, 0.9), (3.4, 0.1, 1.1), dk)
    tw = empty((-0.3, 0.25, 1.65), dk)                                                     # the typewriter
    box('26262A', (0, 0, 0.2), (1.3, 1.0, 0.4), tw, rough=0.4)
    box('34343A', (0, -0.42, 0.12), (1.2, 0.5, 0.2), tw, rot=(0.3, 0, 0))
    for j in range(3):
        for i in range(8):
            box('D8D4C8', (-0.49 + i * 0.14, -0.58 + j * 0.13, 0.23 + j * 0.045), (0.09, 0.08, 0.04), tw)
    add('cylinder', '1A1A1C', (0, 0.42, 0.5), rot=(0, PI / 2, 0), radius=0.13, depth=1.5, vertices=8, parent=tw)
    box('F0EEE4', (0, 0.5, 0.95), (0.95, 0.03, 0.9), tw, rot=(-0.15, 0, 0))
    for j in range(5):
        box('6A6A66', (-0.3 + (j % 2) * 0.1, 0.48, 0.75 + j * 0.13), (0.5 - (j % 2) * 0.15, 0.01, 0.03), tw, rot=(-0.15, 0, 0))
    for i in range(7):                                                                     # seven reports in a pile
        box(('D8B870', 'C8A860', 'E0C078')[i % 3], (1.7 + 0.04 * (i % 2), -0.1, 1.68 + i * 0.07), (1.2, 0.9, 0.06), dk, rot=(0, 0, 0.12 * (i % 3) - 0.1))
    add('cylinder', '2E4A3A', (-2.1, 0.5, 1.75), radius=0.3, depth=0.2, vertices=8, parent=dk)   # desk lamp
    add('cylinder', '2E4A3A', (-2.1, 0.5, 2.3), radius=0.05, depth=1.0, vertices=5, parent=dk)
    add('cone', '2E4A3A', (-2.1, 0.3, 2.85), rot=(0.5, 0, 0), radius1=0.5, radius2=0.15, depth=0.5, vertices=8, parent=dk)
    dlamp = light((-2.1, 0.1, 2.6), 300, 'FFC070', kind='POINT', parent=dk)
    box('4A3420', (0, 1.7, 0.42), (1.5, 1.3, 0.1), dk)                                      # his chair
    box('4A3420', (0, 2.35, 1.5), (1.5, 0.12, 2.2), dk)
    box('4A3420', (5.6, 2.6, 0.42), (1.4, 1.4, 0.1), r)                                     # a spare chair
    box('4A3420', (6.25, 2.6, 1.3), (0.12, 1.4, 1.8), r)
    top = light((0, 4.0, 6.9), 900, 'FFD8A8', 3.0, parent=r)
    top.rotation_euler = (0, 0, 0)
    winl = light((-1.75, 9.4, 3.75), 90, '8AA0D0', 2.5, parent=r)
    winl.rotation_euler = (-PI / 2, 0, 0)
    return dict(off_top=top, off_desk=dlamp)


# ---------------------------------------------------------------- extra cast and props
def bun_head(skin, hair):
    base = K.human_head(skin, hair)

    def fn(head):
        out = base(head)
        add('ico_sphere', hair, (0, 0.3, 0.2), radius=0.17, subdivisions=1, parent=head)
        return out
    return fn


_build0, _reset0 = build, reset


def build():
    S = _build0()
    for name, fn in (('look', set_look), ('wash', set_wash), ('office', set_office)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['suns'].update(look_sun=S['look_sun'].data.energy, wash_sun=S['wash_sun'].data.energy)
    S['wife'] = K.Rig(WIFE, bun_head('E8C0A0', '6A4A30'))
    add('cone', '6A86A0', (0, 0, -0.42), radius1=0.62, radius2=0.33, depth=0.95, vertices=8, parent=S['wife'].body)      # her skirt
    add('cube', 'E8E4D8', (0, -0.3, 0.25), scale=(0.5, 0.04, 0.7), size=1, parent=S['wife'].body)                          # an apron
    S['r2'] = K.Rig(ROY, K.human_head('C89A70', '2A2018'))
    S['r3'] = K.Rig(ROY, K.human_head('E0B890', '8A6A40'))
    for rg in (S['r2'], S['r3']):
        make_hat(rg.head, (0, 0.0, 0.3))[0].rotation_euler = (-0.08, 0, 0)
        add('cube', '2A2420', (0, 0, 0.05), scale=(0.66, 0.66, 0.08), size=1, parent=rg.body)
    S['sup'] = K.Rig(SUP, K.human_head('D8AC84', 'B4B4B0'))
    add('cube', '2A3040', (0, -0.33, 0.8), scale=(0.07, 0.03, 0.4), size=1, parent=S['sup'].body)
    S['cast'] += [S['wife'], S['r2'], S['r3'], S['sup']]
    roy = S['roy']                                                    # 1942: the burn down his right leg, the hole in his shoe
    S['legmark'] = [add('cube', '16110E', (0, -0.1, -0.25), scale=(0.05, 0.03, 0.5), size=1, parent=roy.hp[0]),
                    add('cube', '16110E', (0, -0.09, -0.2), scale=(0.05, 0.03, 0.42), size=1, parent=roy.kn[0]),
                    add('ico_sphere', 'FF7A1A', (0.0, -0.3, -0.43), radius=0.07, subdivisions=1, parent=roy.kn[0], emit=3.0),
                    add('ico_sphere', '0E0A08', (0.0, -0.29, -0.44), radius=0.1, subdivisions=1, parent=roy.kn[0])]
    S['tfire'] = [mov(add('cone', ('FF9A1A', 'FFD040', 'FF5A10')[i % 3], FAR, radius1=0.55, radius2=0.0, depth=1.9, vertices=5, emit=10.0))
                  for i in range(10)]
    S['firel'] = light(FAR, 0, 'FF8A30', kind='POINT')
    S['cloud'] = mov(empty(FAR))
    for i in range(7):
        add('ico_sphere', ('2A303C', '343A48', '22262E')[i % 3], ((i - 3) * 3.4, rnd(i, 41) * 3, rnd(i, 42) * 2.4), scale=(1.5, 1, 0.75),
            radius=3.0 + rnd(i, 43) * 1.6, subdivisions=1, parent=S['cloud'])
    S['tail'] = mov(empty(FAR))
    for sx in (-1, 1):
        add('ico_sphere', 'FF2A1A', (sx * 0.9, 0, 0), radius=0.2, subdivisions=1, parent=S['tail'], emit=14.0)
    S['sunball'] = mov(add('ico_sphere', 'FFE8B0', FAR, radius=15, subdivisions=2, emit=9.0))
    S['cloth'] = mov(add('cube', 'F2E8C8', FAR, scale=(0.7, 0.05, 0.9), size=1))
    S['folder'] = mov(empty(FAR))
    box('D8B870', (0, 0, 0), (1.1, 0.8, 0.05), S['folder'])
    box('F0EEE4', (0, 0, 0.04), (0.95, 0.7, 0.03), S['folder'])
    return S


def reset(S):
    _reset0(S)
    vis(S['legmark'], False)
    S['firel'].location = FAR
    S['firel'].data.energy = 0
    S['off_top'].data.energy = 900
    S['face'].update(wife='calm')


GROUND = P('stand', lL=(1.45, 0.3), lR=(1.3, 0.55), lift=-0.8, lean=-0.3, aL=(-0.7, 0.3, 0.25), aR=(-0.7, 0.3, 0.25), head=(0.4, 0.0))
SIT = P('sit', aL=(0.5, 0.0, 0.9), aR=(0.5, 0.0, 0.9), head=(0.2, 0.0))
BENCH = (2.6, 1.95)


# ---------------------------------------------------------------- new shots: the ridge (1942)
def day_ridge(S, col='5A6E8C'):
    A = mood(S, 'ridge', col, 0.0, fk=6.0, sunk=3.0, sunc='E8D8C0')
    S['cablight'].data.energy = 0
    tint(S['cablampm'], '6A6050', 0.0)
    return A


def tower_new(S, k, t, lt):
    """Before the storm: the new tower. v=2 looks at its bare roof: by the usual account it had no lightning rod."""
    A = day_ridge(S)
    age(S, grey=False)
    if S['prm'].get('v', 1) == 1:
        S['roy'].place(A(-3.0, lerp(-3.0, 3.0, k), 0), PI)
        S['roy'].apply(walk(t, 1.5))
        S['rook'].place(A(-5.4, 7.5, 0), 2.5)
        S['rook'].apply(P('hat', head=(-0.5, 0.15 * math.sin(lt * 2.5))))
        cam(S, A(lerp(-7.6, -6.6, k), 22, 2.0), A(-0.8, 11, lerp(6.0, 7.2, k)), 24)
    else:
        S['roy'].place(A(-0.9, 11.7, 9.3), 0.15)
        S['roy'].apply(P('stand', aR=(2.3, 0.45, 2.0, 0.4), head=(-0.1, 0.2)))
        S['rook'].place(A(3.95, 15.3, 9.3), -PI / 2)
        up = ease((lt - 0.3) / 0.5)
        S['rook'].apply(blend(P('stand'), P('reach', aR=(2.7, 0.05, 0.05), head=(-0.5, 0.25 * math.sin(lt * 6) * up)), up))
        S['face']['rook'] = 'deadpan'
        cam(S, A(lerp(10.0, 9.2, k), lerp(5.5, 6.3, k), lerp(10.2, 10.8, k)), A(0.8, 13.6, 12.6), 30)


def tower_fire(S, k, t, lt):
    f = 0.4 * flick(lt, 1.0)
    A = mood(S, 'ridge', NIGHT, f, fk=3.5)
    for i, o in enumerate(S['tfire']):
        s = 0.8 + 0.4 * math.sin(t * 19 + i * 1.7)
        o.location = A(-2.3 + (i % 5) * 1.15, 12.4 + (i // 5) * 3.0 + 0.3 * math.sin(i), 10.9 + 0.5 * s + (i % 3) * 0.5)
        o.scale = (s, s, s * (1.1 + 0.4 * math.sin(t * 13 + i)))
        o.rotation_euler = (0.2 * math.sin(t * 11 + i), 0.2 * math.cos(t * 9 + i), 0)
    S['firel'].location = A(0, 12.5, 11.6)
    S['firel'].data.energy = 5200 * (0.8 + 0.2 * math.sin(t * 17))
    tint(S['cablampm'], 'FFB050', 30.0)
    smoke(S, A(0, 14, 15.4), t, 8, rise=7.0, size=1.3, speed=0.5)
    u = lerp(0.9, 0.3, k)
    age(S, grey=False)
    S['roy'].place(A(4.0, 8.4 + 7.4 * u, 0.42 + 8.9 * u), 0.0)
    S['roy'].apply(run_pose(t, 2.2))
    S['face']['roy'] = 'scared'
    S['jaw'] = 0.3
    u2 = min(1.0, u + 0.17)
    S['rook'].place(A(4.0, 8.4 + 7.4 * u2, 0.42 + 8.9 * u2), 0.0)
    S['rook'].apply(dict(run_pose(t + 0.2, 2.2), aR=(0.2, 1.9, 1.6, -1.5)))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(12.5, 11.5, k), lerp(1.0, 2.2, k), 3.0), A(2.2, 12.8, 7.6), 26, roll=0.02 * math.sin(lt * 23))


def leg_cu(S, k, t, lt):
    """Afterwards, on the trail: the burn down his right leg and the hole in his shoe."""
    f = 0.3 * flick(lt, 1.6)
    A = mood(S, 'ridge', '1A2436', f, fk=6.5)
    S['firel'].location = A(0, 12.5, 11.6)
    S['firel'].data.energy = 3000 * (0.8 + 0.2 * math.sin(t * 17))
    age(S, grey=False)
    vis(S['legmark'], True)
    S['roy'].place(A(-3.0, -2.0, 0), 0.5)
    S['roy'].apply(dict(GROUND, head=(0.45 - 0.1 * math.sin(lt * 2), 0.0)))
    S['face']['roy'] = 'scared' if lt < 0.8 else 'tired'
    S['jaw'] = 0.2
    smoke(S, A(-2.5, -3.2, 0.5), t, 4, rise=1.6, size=0.14, speed=0.9)
    S['rook'].place(A(-0.7, -2.9, 0), -1.3)
    S['rook'].apply(dict(KNEEL, aR=(1.0, 0.1, 0.5), head=(0.42, 0.1 * math.sin(lt * 3))))
    S['face']['rook'] = 'shocked' if lt < 0.7 else 'calm'
    cam(S, A(lerp(-1.4, -1.9, k), lerp(-7.9, -7.3, k), 1.5), A(-2.1, -2.7, 1.0), 36)


# ---------------------------------------------------------------- new shots: the road (1969, the can, 1973)
def cab_ride(S, k, t, lt):
    """1969, before the strike: through the windscreen. Rook raps on the door pillar: a closed vehicle."""
    f = 0.3 * flick(lt, 1.5)
    A = mood(S, 'road', '3C4656', f, fk=6.0, sunk=1.6)
    y = lerp(34, 24, k)
    drv, pas = truck_at(S, A, -1.0, y, 140)
    age(S)
    S['roy'].place((drv[0], drv[1], drv[2] + 0.03 * math.sin(t * 21)), 0.0)
    S['roy'].apply(dict(DRIVE, head=(0.0, 0.1 * math.sin(lt * 1.7))))
    S['rook'].place((pas[0], pas[1], pas[2] + 0.03 * math.sin(t * 21 + 1)), 0.0)
    S['rook'].apply(P('sit', aL=(1.5 + 0.25 * math.sin(lt * 15), 0.75, 1.3), aR=(0.7, -0.1, 1.5, 1.0), head=(0.0, 0.5 * ease((lt - 0.5) / 0.4)), lean=0.1))
    S['face']['rook'] = 'deadpan'
    cam(S, A(-1.0, y - 7.4, 3.5), A(-1.0, y + 0.4, 3.1), 42, fill=1.6)


def truck_out(S, k, t, lt):
    """1969, after: the truck has stopped. He is out cold over the wheel; Rook is at the door."""
    A = mood(S, 'road', '3C4656', 0.0, fk=6.0, sunk=1.6)
    drv, pas = truck_at(S, A, -1.0, 10, 140)
    age(S, brows=False)
    S['rhat'].rotation_euler = (-0.5, 0.35, 0)
    S['roy'].place(drv, 0.0)
    S['roy'].apply(P('sit', aL=(0.9, 0.1, 0.4), aR=(0.9, 0.1, 0.4), lean=0.5, head=(0.65, 0.25)))
    S['face']['roy'] = 'shut'
    smoke(S, (drv[0], drv[1] - 0.2, drv[2] + 2.4), t, 4, rise=1.0, size=0.15, speed=0.9)
    S['rook'].place(A(1.75, 10.35, 0), -PI / 2)
    S['rook'].apply(P('stand', aR=(1.45 + 0.12 * math.sin(lt * 12), 0.0, 0.25), aL=(0.3, 0.3, 0.6), lean=0.22, head=(0.1, 0.0)))
    S['face']['rook'] = 'shocked' if lt < 1.0 else 'sad'
    cam(S, A(lerp(4.5, 4.0, k), lerp(4.4, 5.2, k), 2.9), A(0.3, 10.2, 2.9), 34)


def can_load(S, k, t, lt):
    """After the fourth strike he keeps a can of water in the truck."""
    A = mood(S, 'road', '5A6878', 0.0, fk=6.5, sunk=2.0)
    truck_at(S, A, -1.5, 2.0, 0)
    age(S)
    put = ease((lt - 0.5) / 0.7)
    S['roy'].place(A(1.1, 4.6, 0), -PI / 2)
    S['roy'].apply(P('stand', aL=(1.2 - 0.25 * put, 0.0, 0.5), aR=(1.2 - 0.25 * put, 0.0, 0.5), lean=0.25 * put, head=(0.2, 0.0)))
    S['can'].location = A(lerp(0.45, 0.2, put), 4.6, lerp(2.3, 2.0, put))
    S['can'].rotation_euler = (0, 0, PI / 2)
    look = ease((lt - 1.5) / 0.3)
    S['rook'].place(A(2.9, 2.2, 0), PI + 0.7)
    S['rook'].apply(P('cross', head=(0.05, -1.3 * look)))
    S['face']['rook'] = 'deadpan' if look < 0.5 else 'calm'
    cam(S, A(lerp(4.4, 4.0, k), lerp(-2.2, -1.4, k), 2.6), A(1.3, 3.6, 2.35), 34)


def patrol_watch(S, k, t, lt):
    """1973: on patrol, out of the truck, watching a cloud. Rook, in the truck bed, points at it."""
    f = 0.25 * flick(lt, 1.6)
    A = mood(S, 'road', '424C5A', f, fk=5.5, sunk=1.6)
    truck_at(S, A, -1.5, 11.5, 0)
    S['cloud'].location = A(lerp(-16, -5, k), 36, 21)
    age(S)
    S['roy'].place(A(1.9, 7.2, 0), 0.3)
    S['roy'].apply(P('stand', aR=(2.3, 0.45, 2.0, 0.4), head=(-0.5, 0.2)))
    S['rook'].place(A(-1.5, 14.0, 1.2), 0.25)
    S['rook'].apply(P('stand', aR=(2.3, 0.3, 0.05), head=(-0.4, 0.0), aL=(0.2, 1.9, 1.6, -1.5)))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(4.4, 3.9, k), lerp(0.4, 1.2, k), 1.5), A(0.2, 9.6, 4.7), 24)


# ---------------------------------------------------------------- new shots: the front yard (1970), the station (the count)
def yard_after(S, k, t, lt):
    A = mood(S, 'yard', '525E6E', 0.0, fk=5.5)
    sparks(S, A(8.75, 6.8, 9.0), t, 8, r=1.6, speed=2.2)
    smoke(S, A(3.85, 0.85, 2.3), t, 4, rise=1.5, size=0.15, speed=1.0)
    smoke(S, A(8.75, 6.8, 10.0), t, 4, rise=3.0, size=0.5, i0=4, speed=0.6)
    age(S)
    S['roy'].place(A(3.4, 0.6, 0), 0.5)
    S['roy'].apply(P('stand', aL=(0.9, -0.55, 2.1, 1.0), head=(-0.25, -0.5 + 0.1 * math.sin(lt * 3)), lean=0.12, lL=(0.1, 0.25), lR=(0.1, 0.25)))
    S['face']['roy'] = 'scared'
    S['jaw'] = 0.2
    S['rook'].place(A(1.2, -0.9, 0), 2.3)
    S['rook'].apply(P('stand', aR=(2.1, 0.15, 0.05), head=(-0.4, 0.5 * math.sin(lt * 2.4))))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(8.4, 7.7, k), lerp(-6.4, -5.8, k), 2.2), A(3.3, 1.6, 3.7), 30)


def rook_four(S, k, t, lt):
    A = room(S, 0.0)
    S['fillk'] = 3.5
    draw = ease((lt - 0.1) / 0.3)
    done = ease((lt - 0.6) / 0.3)
    vis(S['marks'][:3], True)
    vis(S['marks'][3:4], lt > 0.4)
    S['rook'].place(A(7.1, 4.9, 0), PI / 2)
    S['rook'].apply(blend(blend(P('stand'), P('reach', aR=(2.05, 0.05, 0.25), head=(-0.2, 0.0)), draw), P('hips', head=(0.0, 1.15)), done))
    S['face']['rook'] = 'calm' if done < 0.5 else 'deadpan'
    cam(S, A(lerp(4.0, 4.4, k), lerp(9.6, 9.2, k), 3.4), A(8.2, 5.7, 3.5), 34, fill=1.4, fcol='FFE0C0')


# ---------------------------------------------------------------- new shots: the pond, after the seventh
def pond_gone(S, k, t, lt):
    """He has been taken to hospital. The jetty is empty: his rod, his hat. Far off, tail lights."""
    A = mood(S, 'pond', '2A3048', 0.0, fk=5.5)
    rod_at(S, A, 0.5, 9.3, 0.68, 0.0, 0.5)
    S['bhat'].location = A(-0.5, 8.0, 0.66)
    S['bhat'].rotation_euler = (0, 0, 0.7)
    S['tail'].location = A(lerp(9, 16, k), lerp(-26, -44, k), 1.3)
    S['rook'].place(A(0.2, 6.0, 0.62), 0.25)
    S['rook'].apply(hat_hold(head=(0.1, 0.0)))
    S['hat_off'] = 1.0
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-6.6, -5.6, k), lerp(10.4, 9.8, k), 2.0), A(0.9, 4.2, 2.3), 30, fill=1.4)


# ---------------------------------------------------------------- new shots: the overlook
def look_day(S, k, t, lt):
    """Who he was: a ranger at the edge of the Blue Ridge. Rook walks up beside him."""
    A = mood(S, 'look', '7FA2C8', 0.0, fk=6.0, sunk=1.5, sunc='FFF0D8')
    age(S, grey=False)
    S['roy'].place(A(-1.4, 4.7, 0), PI)
    S['roy'].apply(P('hips', head=(-0.05, 0.25 * math.sin(lt * 0.9))))
    S['face']['roy'] = 'warm'
    w = min(1.0, k / 0.7)
    S['rook'].place(A(lerp(2.6, 1.0, w), lerp(-1.0, 4.3, w), 0), PI + 0.29)
    S['rook'].apply(blend(walk(t, 1.7), P('hat', head=(-0.15, 0.3)), (k - 0.7) / 0.15))
    cam(S, A(lerp(3.8, 3.0, k), 11.6, 3.4), A(-0.3, 4.4, 2.7), 30)


def look_years(S, k, t, lt):
    """Twenty-seven years go by: the sun crosses again and again, his hair greys. Rook waits on the bench."""
    u = (lt * 0.62) % 1
    day = math.sin(PI * u)
    A = mood(S, 'look', mix_col('1A2238', '7FA2C8', day), 0.0, fk=2.5 + 4.0 * day, sunk=0.25 + 1.4 * day, sunc=mix_col('FF9A60', 'FFF0D8', day))
    S['sunball'].location = A(170 - 340 * u, -430, 20 + 150 * day)
    age(S, grey=k > 0.55)
    S['roy'].place(A(-1.4, 4.7, 0), PI)
    S['roy'].apply(P('hips', head=(-0.05, 0.3 * math.sin(lt * 1.3))))
    S['rook'].place(A(BENCH[0] + 0.6, BENCH[1], 0), PI)
    S['rook'].apply(P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.9, 0.2, 1.2, 0.0), head=(0.1, 0.4 * math.sin(lt * 1.1))))
    S['face']['rook'] = 'deadpan'
    cu = (lt * 1.5) % 1
    S['coin'].location = A(BENCH[0] + 0.25, BENCH[1] + 0.75, 1.5 + 0.6 * 4 * cu * (1 - cu))
    S['coin'].rotation_euler = (lt * 30, 0.4, 0)
    cam(S, A(lerp(9.0, 8.0, k), 11.6, 3.4), A(0.6, 3.2, 2.9), 26)


def stormy_look(S, lt, t0=1.2):
    f = 0.5 * flick(lt, t0)
    A = mood(S, 'look', '323C50', f, fk=4.5, sunk=0.6)
    if f > 0.25:
        strike(S, A(-90, -330, 160), A(-80, -320, 25), 19, n=7, w=1.8)
    return A


def roy_bench(S, A, lt, turn=0.0):
    age(S)
    S['roy'].place(A(BENCH[0] - 0.5, BENCH[1], 0), PI)
    S['roy'].apply(dict(SIT, head=(0.25, turn)))
    S['face']['roy'] = 'tired'


def look_alone(S, k, t, lt):
    """The sky turns dark and the others walk away. v=2: from behind, later, two figures on one bench."""
    v = S['prm'].get('v', 1)
    A = stormy_look(S, lt, 1.2 if v == 1 else 0.9)
    roy_bench(S, A, lt)
    if v == 1:
        for i, rg in enumerate((S['r2'], S['r3'])):
            y = lerp(-0.6, -5.2, k) - i * 1.5
            rg.place(A(-1.0 + i * 1.7, y, 0), 0.0)
            rg.apply(dict(walk(t + i * 0.3, 1.8), head=(-0.3 * ease((lt - 1.2) / 0.3) * (1 - i), 0.0)))
        S['rook'].place(A(6.4, 3.4, 0), PI - 0.5)
        S['rook'].apply(P('cross', head=(0.0, lerp(0.9, -0.2, ease((lt - 1.4) / 0.6)))))
        S['face']['rook'] = 'calm' if lt < 1.6 else 'sad'
        cam(S, A(lerp(0.6, 1.4, k), 12.2, 3.0), A(1.9, 1.2, 2.2), 28)
    else:
        S['rook'].place(A(BENCH[0] + 1.0, BENCH[1], 0), PI)
        S['rook'].apply(dict(SIT, aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.2, 0.25)))
        S['hat_off'] = 1.0
        S['face']['rook'] = 'sad'
        cam(S, A(lerp(1.0, 2.0, k), lerp(-8.4, -7.4, k), lerp(5.2, 4.6, k)), A(2.8, 4.0, 1.8), 26)


def rook_sits(S, k, t, lt):
    """Rook sits down next to him and takes his hat off. No joke."""
    A = stormy_look(S, lt, 2.2)
    roy_bench(S, A, lt, 0.4 * ease((lt - 1.3) / 0.6))
    sit = ease(lt / 0.8)
    S['rook'].place(A(BENCH[0] + 1.0, lerp(BENCH[1] + 0.9, BENCH[1], sit), 0), PI)
    S['rook'].apply(blend(P('stand'), dict(SIT, aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.15, -0.3)), sit))
    S['hat_off'] = ease((lt - 0.9) / 0.6)
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(4.2, 3.6, k), lerp(8.2, 7.6, k), 2.4), A(2.8, 1.9, 2.05), 36, fill=1.5)


def look_odds(S, k, t, lt):
    """Rook does the arithmetic at the wall. v=2: from behind, he sweeps an arm at the ridges."""
    A = mood(S, 'look', '8A9CB0', 0.0, fk=6.0, sunk=1.3)
    if S['prm'].get('v', 1) == 1:
        S['rook'].place(A(-0.5, 4.5, 0), PI + 0.25)
        n = int(lt * 2.5) % 3
        S['rook'].apply(P('stand', aR=(1.25 + 0.12 * n, 0.25, 1.9, 0.3), aL=(0.9, 0.1, 1.7, 0.6), head=(0.2 - 0.1 * n, 0.15 * math.sin(lt * 3))))
        S['face']['rook'] = 'calm'
        u = (lt * 1.4) % 1
        S['coin'].location = A(-0.95, 5.25, 2.2 + 0.7 * 4 * u * (1 - u))
        S['coin'].rotation_euler = (lt * 30, 0.4, 0)
        cam(S, A(lerp(2.8, 2.2, k), 10.6, 2.9), A(-0.2, 4.5, 2.75), 40)
    else:
        sweep = ease((lt - 0.3) / 0.8)
        S['rook'].place(A(-0.5, 4.5, 0), PI + lerp(-0.5, 0.5, sweep))
        S['rook'].apply(P('point', aR=(1.5, 0.3, 0.05), head=(-0.05, 0.3)))
        cam(S, A(lerp(-5.0, -4.0, k), lerp(-2.0, -1.2, k), 3.5), A(1.5, 9, 2.7), 26)


def golden_look(S):
    return mood(S, 'look', 'E0A878', 0.0, fk=6.0, sunk=2.2, sunc='FFD0A0')


def bench_empty(S, k, t, lt):
    """1983. An empty bench and a clear evening sky. Rook, hat in his hands."""
    A = golden_look(S)
    S['rook'].place(A(-1.6, 3.2, 0), PI - 0.9)
    S['rook'].apply(hat_hold(head=(0.3, 0.0)))
    S['hat_off'] = 1.0
    S['face']['rook'] = 'sad'
    S['fea'][0].location = A(BENCH[0] + 0.4 - 0.5 * lt, BENCH[1] + 0.2 * math.sin(lt * 2), 2.6 - 0.55 * lt + 0.1 * math.sin(lt * 5))
    S['fea'][0].rotation_euler = (lt * 2.5, lt * 1.5, 0.4)
    cam(S, A(lerp(7.0, 5.6, k), lerp(10.2, 9.4, k), lerp(3.0, 2.6, k)), A(1.6, 2.0, 1.6), 34)


def rook_sky(S, k, t, lt):
    """He looks up. Nothing comes. He puts his hat back on."""
    A = golden_look(S)
    on = ease((lt - 1.3) / 0.5)
    S['rook'].place(A(-1.2, 4.5, 0), PI)
    S['rook'].apply(blend(hat_hold(head=(-0.5, 0.2 * math.sin(lt * 1.5))), P('hat', head=(-0.2, 0.0)), on))
    S['hat_off'] = 1.0 - on
    S['face']['rook'] = 'sad' if on < 0.5 else 'warm'
    cam(S, A(lerp(0.4, -0.2, k), lerp(10.4, 9.6, k), 2.5), A(-1.2, 4.5, 3.05), 44)


# ---------------------------------------------------------------- new shots: the back yard
PEG = P('stand', aL=(2.35, 0.12, 0.45), aR=(2.35, 0.12, 0.45), head=(-0.25, 0.0))


def wash_wide(S, k, t, lt):
    f = 0.3 * flick(lt, 1.7)
    A = mood(S, 'wash', '6A7890', f, fk=6.0, sunk=1.4)
    age(S, hat=False)
    S['wife'].place(A(0.6, 3.0, 0), 0.0)
    S['wife'].apply(dict(PEG, aR=(2.35 + 0.1 * math.sin(lt * 6), 0.12, 0.45, 0.0)))
    S['cloth'].location = A(1.45, 2.0, 3.22)
    S['cloth'].rotation_euler = (0.06 * math.sin(lt * 3), 0, 0)
    S['roy'].place(A(-1.5, 3.3, 0), -0.25)
    S['roy'].apply(P('stand', aL=(0.95, 0.1, 1.0), aR=(0.95, 0.1, 1.0), head=(0.0, -0.3 - 0.3 * ease((lt - 1.7) / 0.3))))
    S['towel'].scale = (0.7, 0.5, 0.1)
    S['towel'].location = A(-1.5, 2.6, 2.05)
    S['rook'].place(A(4.6, 0.3, 0), PI - 0.7)
    S['rook'].apply(P('cross', head=(-0.3 * ease((lt - 1.7) / 0.3), 0.2)))
    S['face']['rook'] = 'deadpan' if lt < 1.7 else 'calm'
    cam(S, A(lerp(-2.6, -1.4, k), lerp(-8.0, -7.2, k), 2.7), A(0.6, 2.8, 2.6), 28)


def wash_hit(S, k, t, lt):
    f = flick(lt, 0.3)
    A = mood(S, 'wash', '4A566A', f, fk=5.0)
    hit = ease((lt - 0.3) / 0.1)
    if f > 0.5:
        strike(S, A(9, 22, 70), A(6.2, 2.0, 3.9), 81, n=8, w=0.3)
        strike(S, A(6.2, 2.0, 3.75), A(1.3, 2.3, 3.4), 82, i0=8, n=6, w=0.12, jit=0.5)
        sparks(S, A(6.2, 2.0, 3.8), t, 10, r=1.8, speed=3.5)
    flash(S, A(2.5, -0.5, 4.0), f, 9000)
    age(S, hat=False)
    S['wife'].place(A(0.6, 3.0 + 0.5 * hit, 0), 0.0)
    S['wife'].apply(blend(PEG, JOLT, hit))
    S['cloth'].location = A(1.45 - 1.2 * max(0.0, lt - 0.3), 2.0 - 0.8 * max(0.0, lt - 0.3), 3.22 + 1.5 * max(0.0, lt - 0.3))
    S['cloth'].rotation_euler = (lt * 4, lt * 3, 0)
    S['roy'].place(A(-1.5, 3.3, 0), -0.25)
    S['roy'].apply(blend(P('stand', aL=(0.95, 0.1, 1.0), aR=(0.95, 0.1, 1.0), head=(-0.3, -0.6)), COVER, hit))
    S['face']['roy'] = 'shock' if hit > 0.3 else 'calm'
    S['jaw'] = 0.35 * hit
    S['rook'].place(A(4.6, 0.3, 0), PI - 0.7)
    S['rook'].apply(blend(P('cross', head=(-0.3, 0.2)), DUCK, hit))
    S['face']['rook'] = 'shocked' if hit > 0.3 else 'calm'
    feather(S, A(4.5, 0.2, 3.3), lt, 0.4)
    cam(S, A(lerp(-3.4, -2.8, k), lerp(-6.4, -5.8, k), 1.7), A(1.6, 2.6, 3.0), 26, roll=0.04 * math.sin(lt * 31) * hit)


def wash_after(S, k, t, lt):
    """Afterwards: she is sitting on the grass, he is beside her. He was not touched. Rook takes his hat off."""
    A = mood(S, 'wash', '566278', 0.0, fk=6.0)
    age(S, hat=False)
    S['wife'].place(A(0.9, 3.5, 0), 0.25)
    S['wife'].apply(dict(GROUND, lean=-0.1, aL=(0.3, 0.2, 1.2), aR=(-0.5, 0.3, 0.3), head=(0.3, 0.35)))
    S['roy'].place(A(-0.35, 3.3, 0), -0.6)
    S['roy'].apply(dict(KNEEL, aR=(1.15, 0.45, 0.5), aL=(0.8, 0.0, 0.9), head=(0.2 - 0.5 * ease((lt - 1.4) / 0.6), -0.45 + 0.45 * ease((lt - 1.4) / 0.6))))
    S['face']['roy'] = 'scared'
    smoke(S, A(6.2, 2.0, 3.9), t, 5, rise=2.6, size=0.3, speed=0.6)
    S['cloth'].location = A(-0.9, 1.2, 0.05)
    S['cloth'].rotation_euler = (PI / 2, 0, 0.5)
    S['rook'].place(A(3.3, 1.9, 0), PI - 1.0)
    S['rook'].apply(hat_hold(head=(0.2, 0.0)))
    S['hat_off'] = ease(lt / 0.6)
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(2.6, 1.8, k), lerp(-4.6, -4.0, k), 1.7), A(1.0, 3.0, 1.7), 34, fill=1.4)


# ---------------------------------------------------------------- new shots: the office
def office_base(S, t):
    A = mood(S, 'office', '0C1018', 0.0, fk=3.6)
    S['sup'].place(A(0.4, 6.7, 0), 0.0)
    S['sup'].apply(P('sit', aL=(0.95 + 0.07 * math.sin(t * 13), -0.1, 1.2, 0.8), aR=(0.95 + 0.07 * math.cos(t * 11), -0.1, 1.2, 0.8),
                     head=(0.32, 0.06 * math.sin(t * 2))))
    return A


def office_wide(S, k, t, lt):
    """The strikes are put on record. v=2: across the typewriter."""
    A = office_base(S, t)
    S['rook'].place(A(4.9, 7.3, 0), 0.75)
    S['rook'].apply(P('cross', head=(0.08, 0.5 + 0.2 * math.sin(lt * 1.6))))
    S['face']['rook'] = 'deadpan'
    if S['prm'].get('v', 1) == 1:
        cam(S, A(lerp(4.4, 3.4, k), lerp(-3.8, -3.2, k), lerp(3.9, 3.5, k)), A(1.2, 6.2, 2.4), 26, fcol='FFD8B0')
    else:
        cam(S, A(lerp(-4.4, -3.8, k), lerp(1.6, 2.0, k), 2.5), A(1.2, 6.3, 2.35), 34, fcol='FFD8B0')


def rook_file(S, k, t, lt):
    """Rook reads a report, then looks at the man who wrote it. He was not standing next to him at the time."""
    A = office_base(S, t)
    look = ease((lt - 1.2) / 0.4)
    S['rook'].place(A(4.0, 4.9, 0), -PI / 2 + 0.5)
    S['rook'].apply(P('stand', aL=(0.95, -0.15, 1.25, 0.6), aR=(0.95, -0.15, 1.25, 0.6), head=(0.35 - 0.3 * look, -0.75 * look)))
    S['face']['rook'] = 'calm' if look < 0.5 else 'deadpan'
    S['hat_tip'] = 0.4 * look
    S['folder'].location = A(3.35, 4.55, 1.95)
    S['folder'].rotation_euler = (0.5, 0, -PI / 2 + 0.5)
    cam(S, A(lerp(5.6, 5.1, k), lerp(0.4, 1.0, k), 2.9), A(2.3, 5.6, 2.45), 38, fcol='FFD8B0')


HOST |= {'tower_new', 'tower_fire', 'leg_cu', 'cab_ride', 'truck_out', 'can_load', 'patrol_watch', 'yard_after', 'rook_four', 'pond_gone',
         'look_day', 'look_years', 'look_alone', 'rook_sits', 'look_odds', 'bench_empty', 'rook_sky', 'wash_wide', 'wash_hit', 'wash_after',
         'office_wide', 'rook_file'}
SHOTS3D.update({f.__name__: f for f in (
    tower_new, tower_fire, leg_cu, cab_ride, truck_out, can_load, patrol_watch, yard_after, rook_four, pond_gone, look_day, look_years,
    look_alone, rook_sits, look_odds, bench_empty, rook_sky, wash_wide, wash_hit, wash_after, office_wide, rook_file)})


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: the bolt on his hat on the ridge trail, the tower behind, Rook ducking beside him."""
    A = mood(S, 'ridge', '1E2A44', 0.55, fk=5.0)
    pts = strike(S, A(-9, 16, 60), A(-3.6, -3.5, 3.45), 23, n=9, w=0.3)
    branch(S, pts[4], 5, 9, w=0.13, L=7)
    flash(S, A(-2.4, -6.0, 4.0), 0.8, 9000)
    sparks(S, A(-3.6, -3.5, 3.4), 0.3, 10, r=1.6, speed=1.0)
    age(S)
    S['roy'].place(A(-3.6, -3.5, 0), 0.25)
    S['roy'].apply(JOLT)
    S['face']['roy'] = 'shock'
    S['jaw'] = 0.35
    S['rook'].place(A(-1.5, -3.2, 0), -0.2)
    S['rook'].apply(DUCK)
    S['face']['rook'] = 'shocked'
    cam(S, A(0.6, -11.4, 1.7), A(0.4, -2.0, 3.0), 30, fill=1.3)


STILLS['thumb'] = photo_thumb
