"""Case 044 - the children sent by parcel post, 1913 to 1915 (May Pierstorff, Grangeville to Lewiston, Idaho,
19 February 1914). The whole story in 3D, built from code for this case only: a country post office with a platform
scale, a mail train in snowy hills, the inside of the railway mail car, an Ohio farm lane at dusk, a house door in
Lewiston and an office in Washington. Every figure is a generic low-poly shape: nobody's likeness is attempted and no
real stamp, badge, seal, sign or logo is reproduced. Rook is the only recurring element."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, blend, lerp, light

PI = math.pi
FAR = (0, 0, -30000)
POST = (0.0, 0.0, 0.0)              # the Grangeville post office
CAR = (1000.0, 0.0, 0.0)            # inside the railway mail car
RAIL = (2000.0, 0.0, 0.0)           # the line through the hills
OHIO = (3000.0, 0.0, 0.0)           # a farm lane in Ohio
LEW = (4000.0, 0.0, 0.0)            # the grandmother's door in Lewiston
BAN = (5000.0, 0.0, 0.0)            # an office of the Post Office Department
HOST = {'rook_counter', 'rook_ticket', 'rook_scale', 'rook_sack', 'rook_hatjump', 'rook_follow', 'rook_sackcheck', 'car_window',
        'rook_delivered', 'rook_notice', 'rook_laugh', 'signoff'}
CAMFILL = {'*': 170, 'train_wide': 0, 'wheels': 60, 'car_inside': 260, 'rook_sack': 280, 'rook_sackcheck': 280, 'cousin': 260,
           'car_window': 240, 'baby_bundle': 200, 'rook_hatjump': 420, 'rook_follow': 520, 'carrier_lane': 700, 'ohio_door': 160,
           'door': 320, 'rook_delivered': 300, 'ban_desk': 240, 'rook_notice': 220}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
OAK, OAKD, PLANK, PLASTER, BRASS, IRON, SNOW, CANVAS = '8A5A30', '5A3A20', '9A7448', 'D8CDB4', 'D8A83A', '34363E', 'E8EEF4', 'C9B88E'
MAYCOAT, STAMP1, STAMP2 = '2E8C86', 'C8402E', '3E6FB8'
AMB = dict(                         # horizon, zenith, strength, sun watts, sun colour, sun direction
    post=('5A4A3A', '2A2630', 0.4, 0.0, 'FFFFFF', (0, 0, 1)),
    car=('4A4038', '26242C', 0.4, 0.0, 'FFFFFF', (0, 0, 1)),
    rail=('F2DCC8', '6E9AD0', 1.1, 3.4, 'FFE8C8', (-0.5, -0.6, 0.45)),
    ohio=('F0A060', '3A3E78', 1.0, 3.2, 'FF9A50', (-0.6, -0.6, 0.25)),
    lew=('CFE0F4', '6E90C8', 1.0, 2.6, 'FFF0DC', (0.5, -0.7, 0.5)),
    ban=('4A4038', '26222C', 0.4, 0.0, 'FFFFFF', (0, 0, 1)))
_KEEP = []


# ---------------------------------------------------------------- small tools
def box(col, loc, size, par=None, rot=(0, 0, 0), **kw):
    return K.add('cube', col, loc, rot=rot, scale=size, size=1, parent=par, **kw)


def cyl(col, loc, r, d, par=None, rot=(0, 0, 0), v=8, **kw):
    return K.add('cylinder', col, loc, rot=rot, radius=r, depth=d, vertices=v, parent=par, **kw)


def ball(col, loc, r, par=None, scale=(1, 1, 1), **kw):
    return K.add('ico_sphere', col, loc, scale=scale, radius=r, subdivisions=1, parent=par, **kw)


def cone(col, loc, r1, r2, d, par=None, rot=(0, 0, 0), v=8, **kw):
    return K.add('cone', col, loc, rot=rot, radius1=r1, radius2=r2, depth=d, vertices=v, parent=par, **kw)


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rnd(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def keep(o):
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def at(o, x, y, z=0.0):
    return (o[0] + x, o[1] + y, o[2] + z)


def plus(a, b, s=1.0):
    return (a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s)


def mix(a, b, k):
    return tuple(lerp(x, y, k) for x, y in zip(a, b))


def off(loc, yaw, v, s=1.0):
    """A point in a character's own frame (x to his left hand side of the screen, -y forward) as a world point."""
    c, sn = math.cos(yaw), math.sin(yaw)
    return (loc[0] + (v[0] * c - v[1] * sn) * s, loc[1] + (v[0] * sn + v[1] * c) * s, loc[2] + v[2] * s)


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def room(o, w, d, h, wall, floor, ceil='3A3028', front=False):
    """Floor, ceiling, back wall (+y) and side walls; the camera side stays open."""
    box(floor, at(o, 0, 0, -0.1), (w, d, 0.2))
    box(ceil, at(o, 0, 0, h + 0.1), (w, d, 0.2))
    box(wall, at(o, 0, d / 2, h / 2), (w, 0.2, h))
    for s in (-1, 1):
        box(wall, at(o, s * w / 2, 0, h / 2), (0.2, d, h))
        box(OAKD, at(o, s * (w / 2 - 0.12), 0, 0.25), (0.06, d, 0.5))
    box(OAKD, at(o, 0, d / 2 - 0.12, 0.25), (w, 0.06, 0.5))
    if front:
        box(wall, at(o, 0, -d / 2, h / 2), (w, 0.2, h))


def head_of(skin, hair, hat=None, tache=None, bun=False, braids=None, bald=False, glasses=False, beard=None, smile=False):
    def fn(head):
        d = K.human_head(skin, skin if bald else hair)(head)
        if bald:
            for s in (-1, 1):
                ball(hair, (s * 0.24, 0.08, 0.02), 0.16, head, scale=(0.5, 0.9, 0.8))
        if smile:                                                     # upturned corners and round cheeks
            for s in (-1, 1):
                box('2A1218', (s * 0.105, -0.012, 0.005), (0.035, 0.03, 0.075), d['jaw'], rot=(0, s * 0.5, 0))
                ball('F0A090', (s * 0.2, -0.2, -0.05), 0.07, head)
        if tache:
            for s in (-1, 1):
                box(tache, (s * 0.085, -0.3, -0.065), (0.17, 0.06, 0.06), head, rot=(0, s * 0.3, s * 0.25))
        if beard:
            ball(beard, (0, -0.17, -0.25), 0.2, head, scale=(0.95, 0.75, 0.75))
        if bun:
            ball(hair, (0, 0.2, 0.3), 0.15, head)
        if braids:
            for s in (-1, 1):
                cyl(hair, (s * 0.3, 0.02, -0.2), 0.07, 0.42, head, v=6)
                ball(braids, (s * 0.3, 0.02, -0.42), 0.08, head)
        if glasses:
            for s in (-1, 1):
                K.add('torus', BRASS, (s * 0.105, -0.3, 0.04), rot=(PI / 2, 0, 0), major_radius=0.065, minor_radius=0.012, major_segments=10,
                      minor_segments=4, parent=head, rough=0.3)
        if hat == 'cap':                                              # a plain peaked cap
            cyl('2A3040', (0, 0.0, 0.3), 0.31, 0.16, head)
            box('15171E', (0, -0.3, 0.24), (0.42, 0.26, 0.04), head, rot=(0.15, 0, 0))
        elif hat == 'visor':                                          # a clerk's green eyeshade
            box('2E7A4A', (0, -0.3, 0.2), (0.5, 0.3, 0.03), head, rot=(0.3, 0, 0), rough=0.4)
            cyl('2E7A4A', (0, 0, 0.2), 0.3, 0.05, head)
        elif hat == 'bonnet':                                         # a knitted winter hat with a bobble
            ball(STAMP1, (0, 0.03, 0.17), 0.31, head, scale=(1, 1, 0.75))
            ball('F2E8D8', (0, 0.03, 0.42), 0.1, head)
        elif hat == 'brim':
            cyl('3A3028', (0, 0, 0.24), 0.48, 0.04, head, v=10)
            cyl('3A3028', (0, 0, 0.36), 0.28, 0.22, head)
        elif hat == 'flat':
            cyl('6A5A48', (0, -0.04, 0.27), 0.34, 0.1, head, v=10)
            box('6A5A48', (0, -0.32, 0.23), (0.36, 0.2, 0.04), head)
        return d
    return fn


def person(S, name, cols, headfn, scale=1.0, skirt=None):
    r = K.Rig(cols, headfn)
    r.s, r.face, r.jawv = scale, 'calm', 0.0
    if skirt:
        cone(skirt, (0, 0, -0.4), 0.52, 0.3, 0.9, r.body, v=8)
    S[name] = r
    S['humans'].append(r)
    return r


# ---------------------------------------------------------------- the sets
def make_post(S):
    o = POST
    room(o, 13, 10, 6.2, PLASTER, PLANK)
    box(PLANK, at(o, 0, -6.0, -0.1), (13, 2.0, 0.2))
    box('3A3028', at(o, 0, -6.0, 6.3), (13, 2.0, 0.2))
    box(PLASTER, at(o, 0, -7.0, 3.1), (13, 0.2, 6.2))
    for s in (-1, 1):
        box(PLASTER, at(o, s * 6.5, -6.0, 3.1), (0.2, 2.0, 6.2))
    box(OAKD, at(o, 3.2, -6.86, 2.0), (2.2, 0.1, 4.0))                 # the street door
    box('BFE0FF', at(o, 3.2, -6.8, 3.0), (1.4, 0.06, 1.2), emit=2.2)
    box('BFE0FF', at(o, -1.6, -6.86, 3.3), (3.0, 0.06, 2.4), emit=2.4)
    box(OAKD, at(o, -1.6, -6.82, 3.3), (3.2, 0.1, 0.12))
    box(OAKD, at(o, -1.6, -6.82, 3.3), (0.12, 0.1, 2.6))
    box(OAK, at(o, 2.6, 1.5, 0.95), (7.4, 0.9, 1.9))                 # the counter
    box(OAKD, at(o, 2.6, 1.45, 1.94), (7.7, 1.2, 0.1))
    for i in range(4):
        box(OAKD, at(o, -0.4 + i * 2.0, 1.03, 0.95), (0.08, 0.04, 1.6))
    for ix in range(9):                                               # pigeonholes on the back wall
        for iz in range(4):
            x, z = -0.8 + ix * 0.85, 2.5 + iz * 0.75
            box(OAKD, at(o, x, 4.8, z), (0.78, 0.3, 0.68))
            box('2A1E16', at(o, x, 4.66, z), (0.66, 0.06, 0.56))
            if rnd(ix, iz) > 0.35:
                box('F0E8D8', at(o, x - 0.1 + 0.2 * rnd(iz, ix), 4.62, z - 0.12), (0.3, 0.05, 0.22), rot=(0, 0.3 * rnd(ix, 7) - 0.15, 0))
    box('BFE0FF', at(o, -6.38, -1.0, 3.3), (0.06, 2.6, 2.6), emit=2.6)   # the window in the left wall
    for dz in (-1.3, 0, 1.3):
        box(OAKD, at(o, -6.34, -1.0, 3.3 + dz), (0.12, 2.8, 0.14))
    for dy in (-1.3, 0, 1.3):
        box(OAKD, at(o, -6.34, -1.0 + dy, 3.3), (0.12, 0.14, 2.8))
    light(at(o, -5.6, -1.0, 3.6), 900, 'CFE4FF', size=2.6, target=K.empty(at(o, 0, 0, 1.5)))
    light(at(o, 2.5, -1.5, 5.6), 700, 'FFD9A0', size=3.0, target=K.empty(at(o, 1.5, 1.0, 1.0)))
    cyl(IRON, at(o, 2.5, 0.0, 5.7), 0.03, 1.0)
    cone('2E7A4A', at(o, 2.5, 0.0, 5.1), 0.6, 0.1, 0.4, v=10)
    ball('FFE8B0', at(o, 2.5, 0.0, 4.95), 0.16, emit=8.0)
    # the platform scale
    sx, sy = -2.6, 0.6
    box(IRON, at(o, sx, sy, 0.1), (1.9, 1.7, 0.2))
    box('7A2E22', at(o, sx, sy, 0.24), (1.6, 1.4, 0.1))
    box('7A2E22', at(o, sx, sy + 0.95, 1.7), (0.22, 0.2, 3.2))
    cyl('F4EEDC', at(o, sx, sy + 0.8, 3.5), 0.78, 0.08, rot=(PI / 2, 0, 0), v=20, rough=0.5)
    K.add('torus', BRASS, at(o, sx, sy + 0.76, 3.5), rot=(PI / 2, 0, 0), major_radius=0.78, minor_radius=0.05, major_segments=20, minor_segments=5,
          rough=0.3)
    for i in range(11):
        a = -2.2 + i * 0.44
        box('2A2420', at(o, sx + 0.62 * math.sin(a), sy + 0.74, 3.5 + 0.62 * math.cos(a)), (0.04, 0.02, 0.14 if i % 5 == 0 else 0.08), rot=(0, a, 0))
    box(STAMP1, at(o, sx + 0.62 * math.sin(2.0), sy + 0.735, 3.5 + 0.62 * math.cos(2.0)), (0.07, 0.02, 0.2), rot=(0, 2.0, 0), emit=0.6)   # the limit mark
    S['needle'] = K.empty(at(o, sx, sy + 0.72, 3.5))
    box('1A1A20', (0, 0, 0.3), (0.05, 0.02, 0.66), S['needle'])
    cyl(BRASS, at(o, sx, sy + 0.71, 3.5), 0.07, 0.04, rot=(PI / 2, 0, 0), rough=0.3)
    box(OAKD, at(o, sx + 1.25, sy + 0.9, 1.0), (0.7, 0.5, 0.08))     # a shelf of brass weights beside the column
    for i in range(3):
        cyl(BRASS, at(o, sx + 1.05 + i * 0.2, sy + 0.9, 1.12 + 0.02 * i), 0.07 + 0.015 * i, 0.16, rough=0.25)
    S['scale_at'] = at(o, sx, sy - 0.1, 0.29)
    S['dial_at'] = at(o, sx, sy + 0.7, 3.5)
    # parcels, sacks, the notice board
    for i, (x, y, w) in enumerate(((5.2, -2.6, 1.0), (4.3, -3.1, 0.8), (5.0, -2.7, 0.7), (-5.2, 3.6, 1.1), (-4.4, 3.9, 0.7))):
        z = 0.5 * w if i != 2 else 1.35
        box(('B08A58', 'A47A48', 'C09A68')[i % 3], at(o, x, y, z), (w, w * 0.9, w), rot=(0, 0, 0.4 * i))
        box('E8DCC0', at(o, x, y, z), (w * 1.02, 0.06, w * 1.02), rot=(0, 0, 0.4 * i))
    box(OAKD, at(o, -3.9, 4.86, 3.4), (2.0, 0.08, 2.4))
    box('F2EAD6', at(o, -3.9, 4.8, 3.4), (1.5, 0.04, 1.9))
    for i in range(6):
        box('3A3430', at(o, -3.9, 4.77, 4.1 - i * 0.26), (1.2 - 0.25 * rnd(i, 3), 0.02, 0.07))
    box(STAMP1, at(o, -3.9, 4.77, 2.7), (0.9, 0.02, 0.16), emit=0.4)
    box(BRASS, at(o, 0.2, 1.4, 2.06), (0.5, 0.3, 0.14), rough=0.3)   # a little counter scale and an ink pad
    box('2A2420', at(o, 4.6, 1.3, 2.02), (0.5, 0.36, 0.06))


def make_car(S):
    o = CAR
    room(o, 13, 5.4, 5.0, '7A5A3A', '6A4A2C', ceil='5A4030')
    for i in (0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13):                   # tongue-and-groove boards
        box('5E4428', at(o, -6.0 + i * 0.93, 2.58, 2.5), (0.05, 0.04, 5.0))
    for ix in range(6):                                               # the letter case
        for iz in range(5):
            x, z = 2.0 + ix * 0.62, 1.9 + iz * 0.56
            box(OAKD, at(o, x, 2.4, z), (0.58, 0.4, 0.52))
            box('1E1612', at(o, x, 2.22, z), (0.48, 0.06, 0.42))
            if rnd(ix, iz + 9) > 0.3:
                box('F0E8D8', at(o, x, 2.18, z - 0.08), (0.3, 0.05, 0.2))
    box(OAK, at(o, 3.6, 1.9, 1.5), (4.0, 1.0, 0.1))
    box(OAK, at(o, 3.6, 2.2, 0.75), (4.0, 0.4, 1.5))
    # the sliding door, open: daylight and the country going by
    box('CFE6FF', at(o, -2.6, 2.62, 2.5), (2.6, 0.04, 3.6), emit=3.2)
    for s in (-1, 1):
        box(OAKD, at(o, -2.6 + s * 1.38, 2.52, 2.5), (0.16, 0.14, 3.9))
    box(OAKD, at(o, -2.6, 2.52, 4.4), (2.9, 0.14, 0.16))
    box('8A6A44', at(o, -4.7, 2.5, 2.5), (1.4, 0.1, 3.7))
    S['poles'] = [keep(box('5A6A80', FAR, (0.14, 0.03, 3.6), emit=0.3)) for _ in range(1)]
    light(at(o, -2.6, 1.6, 3.2), 700, 'D8E8FF', size=2.4, target=K.empty(at(o, -1.5, -0.5, 1.0)))
    S['carlamp'] = K.empty(at(o, 1.0, 0.0, 4.9))
    cyl(IRON, (0, 0, -0.4), 0.025, 0.8, S['carlamp'])
    cone(BRASS, (0, 0, -0.85), 0.4, 0.08, 0.3, S['carlamp'], v=8, rough=0.3)
    ball('FFE0A0', (0, 0, -1.0), 0.14, S['carlamp'], emit=9.0)
    light((0, 0, -1.1), 420, 'FFC880', size=1.2, parent=S['carlamp'])
    cyl(IRON, at(o, 5.6, -1.2, 0.8), 0.5, 1.6, v=10)                  # the stove
    cyl(IRON, at(o, 5.6, -1.2, 3.3), 0.12, 3.4)
    box('FF8A30', at(o, 5.6, -1.72, 0.7), (0.3, 0.04, 0.24), emit=5.0)
    for i, (x, y, r) in enumerate(((-5.0, 0.6, 0.75), (-4.2, 1.5, 0.65), (-5.3, 1.7, 0.6), (-0.2, 1.7, 0.7), (0.9, 1.5, 0.6))):
        ball(CANVAS, at(o, x, y, r * 0.75), r, scale=(1, 0.9, 0.85))
        cyl('8A7A58', at(o, x, y, r * 1.5), r * 0.25, 0.3)
    S['seat_at'] = at(o, -1.2, 0.3, 0.0)
    ball(CANVAS, at(o, -1.2, 0.75, 0.55), 0.85, scale=(1.1, 0.9, 0.7))          # the sack she sits on
    for i in range(4):
        box(('B08A58', 'A47A48')[i % 2], at(o, -5.9 + 0.8 * (i % 2), -1.5 + 0.2 * i, 0.4 + 0.75 * (i // 2)), (0.9, 0.8, 0.75), rot=(0, 0, 0.3 * i))


def make_rail(S):
    o = RAIL
    box(SNOW, at(o, 0, 30, -0.5), (400, 300, 1.0))
    box('B8A894', at(o, 0, 0, 0.06), (400, 3.4, 0.14))               # the ballast
    for s in (-1, 1):
        box('5A5E6A', at(o, 0, s * 0.9, 0.3), (400, 0.12, 0.16), rough=0.4)
    for i in range(90):
        box(OAKD, at(o, -90 + i * 2.0, 0, 0.18), (0.4, 2.6, 0.14))
    for i in range(9):
        x = -80 + i * 20
        box(OAKD, at(o, x, 4.0, 3.5), (0.22, 0.22, 7.0))
        box(OAKD, at(o, x, 4.0, 6.4), (0.16, 1.8, 0.16))
    for i in range(16):                                               # hills and pines
        x = -110 + i * 15 + 6 * rnd(i, 1)
        r = 16 + 14 * rnd(i, 2)
        cone(('DCE6F0', 'C8D6E6', 'EEF2F6')[i % 3], at(o, x, 46 + 26 * rnd(i, 3), r * 0.42), r, 1.5, r * 0.9, v=6)
    for i in range(46):
        x, y = -100 + 200 * rnd(i, 5), 9 + 26 * rnd(i, 6)
        h = 3 + 3 * rnd(i, 7)
        cyl(OAKD, at(o, x, y, 0.5), 0.18, 1.0, v=5)
        cone('2E5A46', at(o, x, y, 1.0 + h / 2), 1.2 + 0.4 * rnd(i, 8), 0.0, h, v=6)
        cone(SNOW, at(o, x, y, 1.0 + h * 0.86), 0.5, 0.0, h * 0.34, v=6)
    for i in range(10):
        x, y = -90 + 60 * rnd(i, 11), -6 - 10 * rnd(i, 12)
        cone('2E5A46', at(o, x, y, 2.2), 1.3, 0.0, 4.4, v=6)
    tr = S['train'] = keep(K.empty(FAR))                              # origin on the rails under the engine's cab
    cyl('22252C', (3.4, 0, 2.3), 1.05, 5.6, tr, rot=(0, PI / 2, 0), v=12, rough=0.5)        # boiler
    cyl('22252C', (5.0, 0, 3.9), 0.34, 1.6, tr, v=8)
    cone('22252C', (5.0, 0, 4.8), 0.34, 0.52, 0.5, tr, v=8)
    cyl(BRASS, (3.0, 0, 3.5), 0.36, 0.5, tr, v=8, rough=0.3)
    box('8A2A22', (-0.2, 0, 2.7), (2.2, 2.5, 3.0), tr)
    box('22252C', (-0.2, 0, 4.3), (2.6, 2.8, 0.16), tr)
    box('FFE0A0', (-0.2, -1.27, 3.3), (1.0, 0.04, 0.8), tr, emit=3.0)
    cone('8A2A22', (6.9, 0, 0.9), 1.3, 0.2, 1.2, tr, rot=(0, PI / 2, 0), v=4)               # the pilot
    ball('FFF0C0', (6.3, 0, 3.0), 0.3, tr, emit=10.0)
    S['wheels'] = []
    for x, r in ((0.2, 0.95), (2.2, 0.95), (4.2, 0.95), (5.8, 0.55)):
        for s in (-1, 1):
            w = K.empty((x, s * 1.0, r + 0.36), tr)
            cyl('8A2A22', (0, 0, 0), r, 0.2, w, rot=(PI / 2, 0, 0), v=12)
            box(IRON, (0, s * 0.12, 0), (r * 1.7, 0.06, 0.16), w)
            box(IRON, (0, s * 0.12, 0), (0.16, 0.06, r * 1.7), w)
            S['wheels'].append((w, r))
    S['rod'] = box('C8CCD6', (2.2, -1.2, 1.3), (4.3, 0.08, 0.16), tr, rough=0.3)
    box('3A2A22', (-3.6, 0, 2.4), (3.2, 2.4, 2.6), tr)                # tender
    box('15161A', (-3.6, 0, 3.75), (2.8, 2.0, 0.3), tr)
    box('2E5A46', (-11.5, 0, 2.9), (11.0, 2.6, 3.4), tr)             # the mail car
    box('22252C', (-11.5, 0, 4.7), (11.4, 2.9, 0.22), tr)
    box('F4D48A', (-11.5, -1.32, 3.9), (9.6, 0.04, 0.5), tr)
    for i in range(4):
        box('FFE0A0', (-15.0 + i * 1.5, -1.33, 3.0), (0.8, 0.04, 0.9), tr, emit=2.5)
    box('15161A', (-9.0, -1.33, 2.6), (1.8, 0.04, 2.6), tr)           # the open door
    for x in (-15.0, -8.0, -4.6, -2.6):
        for s in (-1, 1):
            cyl('22252C', (x, s * 1.0, 0.82), 0.46, 0.2, tr, rot=(PI / 2, 0, 0), v=10)
    S['smoke'] = [keep(ball('F4F4F8', FAR, 1.0, emit=0.25)) for _ in range(9)]


def make_ohio(S):
    o = OHIO
    box('7A6A48', at(o, 0, 20, -0.5), (300, 200, 1.0))
    box('9A8460', at(o, 0, 0, 0.03), (300, 3.0, 0.08))               # the lane
    for i in range(30):                                               # last snow in the ruts and the field
        box(SNOW, at(o, -40 + 80 * rnd(i, 1), 3 + 22 * rnd(i, 2), 0.03), (2 + 3 * rnd(i, 3), 1 + 2 * rnd(i, 4), 0.08))
    for i in range(26):                                               # the fence
        x = -39 + i * 3.0
        box('E8E0D0', at(o, x, 2.2, 0.8), (0.16, 0.16, 1.6))
        for z in (0.6, 1.2):
            box('E8E0D0', at(o, x + 1.5, 2.2, z), (3.0, 0.08, 0.14))
    box(OAKD, at(o, -3.2, -1.9, 1.1), (0.16, 0.16, 2.2))             # the mailbox
    cyl('8A8E9A', at(o, -3.2, -1.9, 2.4), 0.3, 0.9, rot=(PI / 2, 0, 0), v=10, rough=0.4)
    box(STAMP1, at(o, -2.86, -1.9, 2.7), (0.04, 0.3, 0.3))
    hx, hy = 9.0, 8.0                                                 # the farmhouse
    box('D8D0BC', at(o, hx, hy + 3, 3.0), (9.0, 6.0, 6.0))
    cone('6A3A30', at(o, hx, hy + 3, 7.3), 7.2, 0.3, 2.8, rot=(0, 0, PI / 4), v=4)
    box('8A8474', at(o, hx, hy - 1.0, 0.3), (5.0, 2.2, 0.6))         # the porch
    for s in (-1, 1):
        box('E8E0D0', at(o, hx + s * 2.3, hy - 1.9, 2.0), (0.2, 0.2, 3.4))
    box('6A3A30', at(o, hx, hy - 1.1, 3.8), (5.4, 2.6, 0.2), rot=(0.12, 0, 0))
    box('3A2418', at(o, hx, hy - 0.03, 2.1), (1.5, 0.1, 3.0))
    S['odoor'] = K.empty(at(o, hx - 0.7, hy - 0.1, 0.6))
    box('7A2E22', (0.7, 0, 1.45), (1.4, 0.1, 2.9), S['odoor'])
    for s in (-1, 1):
        box('FFD080', at(o, hx + s * 2.9, hy - 0.03, 3.2), (1.3, 0.06, 1.6), emit=4.0)
    light(at(o, hx, hy - 3.0, 3.2), 160, 'FFC070', size=2.0, target=K.empty(at(o, hx, hy - 0.5, 2.0)))
    box(OAKD, at(o, -9, 7, 3.0), (0.5, 0.5, 6.0))                     # a bare tree
    for i in range(7):
        a = i * 0.9
        cyl(OAKD, at(o, -9 + 1.2 * math.cos(a), 7 + 1.2 * math.sin(a), 6.3 + 0.3 * i), 0.1, 3.0, rot=(0.7 * math.sin(a), 0.7 * math.cos(a), 0), v=5)
    cone('5A4A60', at(o, -40, 70, 9), 40, 4, 20, v=6)
    cone('6A5A70', at(o, 30, 80, 7), 44, 4, 16, v=6)
    S['odoor_at'] = at(o, hx, hy - 1.2, 0.6)


def make_lew(S):
    o = LEW
    box(SNOW, at(o, 0, 0, -0.5), (200, 120, 1.0))
    box('B8B0A4', at(o, 0, -1.5, 0.03), (200, 3.0, 0.08))            # a shovelled path
    box('B8B0A4', at(o, 0, 2.2, 0.03), (2.6, 4.6, 0.08))
    box('5E7A9A', at(o, 0, 8.5, 4.0), (12.0, 7.0, 8.0))              # the house
    for i in range(10):
        box('506A88', at(o, 0, 4.96, 0.6 + i * 0.75), (12.0, 0.06, 0.08))
    cone('3A3440', at(o, 0, 8.5, 9.6), 9.4, 0.3, 3.4, rot=(0, 0, PI / 4), v=4)
    box(SNOW, at(o, 0, 5.4, 8.25), (12.6, 1.4, 0.18), rot=(0.25, 0, 0))
    box('9A9084', at(o, 0, 4.0, 0.35), (4.4, 2.2, 0.7))              # the porch and steps
    box('9A9084', at(o, 0, 2.6, 0.17), (3.0, 0.7, 0.34))
    for s in (-1, 1):
        box('F0EADC', at(o, s * 2.0, 3.1, 2.4), (0.22, 0.22, 3.6))
        box('FFD890', at(o, s * 3.9, 4.94, 3.3), (1.8, 0.06, 2.2), emit=3.6)
        box('F0EADC', at(o, s * 3.9, 4.92, 3.3), (2.0, 0.05, 0.1))
        box('F0EADC', at(o, s * 3.9, 4.92, 3.3), (0.1, 0.05, 2.4))
    box('4A5A70', at(o, 0, 3.9, 4.3), (4.8, 2.6, 0.2), rot=(0.14, 0, 0))
    box(SNOW, at(o, 0, 3.7, 4.45), (4.8, 2.0, 0.12), rot=(0.14, 0, 0))
    box('FFD890', at(o, 0, 4.98, 2.3), (1.5, 0.06, 3.1), emit=3.0)   # the lit hall behind the door
    S['ldoor'] = K.empty(at(o, -0.75, 4.9, 0.7))
    box('8A3A28', (0.75, 0, 1.55), (1.5, 0.1, 3.1), S['ldoor'])
    ball(BRASS, (1.3, -0.1, 1.5), 0.07, S['ldoor'], rough=0.3)
    light(at(o, 0, 1.6, 3.6), 380, 'FFD8A0', size=2.0, target=K.empty(at(o, 0, 4.0, 1.8)))
    for i in range(12):                                               # a fence, bushes under snow, a far street
        box('F0EADC', at(o, -16 + i * 2.6 + (5.0 if i > 5 else 0), 0.6, 0.7), (0.14, 0.14, 1.4))
        ball(SNOW, at(o, -15 + i * 2.7 + (4.0 if i > 5 else 0), 4.0 + rnd(i, 2), 0.5), 0.9 + 0.4 * rnd(i, 1), scale=(1, 1, 0.7))
    for i, x in enumerate((-22, 20)):
        box(('9A6A5A', 'A8A08C')[i], at(o, x, 10, 3.5), (11, 7, 7))
        cone('3A3440', at(o, x, 10, 8.4), 8.6, 0.3, 3.0, rot=(0, 0, PI / 4), v=4)
        box('FFD890', at(o, x - 2, 6.46, 3.2), (1.6, 0.06, 2.0), emit=3.0)
    cyl(IRON, at(o, -5.0, -0.2, 2.6), 0.08, 5.2)
    ball('FFF0C0', at(o, -5.0, -0.2, 5.3), 0.26, emit=6.0)
    S['ldoor_at'] = at(o, 0, 4.2, 0.7)


def make_ban(S):
    o = BAN
    room(o, 12, 8, 6.4, '4E5E52', '5A3E28')
    for i in range(7):
        box('44524A', at(o, -5.4 + i * 1.8, 3.86, 3.9), (0.08, 0.06, 4.6))
    box('3E5038', at(o, 0, 3.86, 1.0), (12, 0.08, 2.0))
    box('BFD8F0', at(o, 4.2, 3.88, 3.9), (2.2, 0.06, 3.0), emit=2.4)  # a tall window
    box(OAKD, at(o, 4.2, 3.84, 3.9), (0.12, 0.08, 3.2))
    box(OAKD, at(o, 4.2, 3.84, 3.9), (2.4, 0.08, 0.12))
    light(at(o, 4.0, 3.0, 4.2), 800, 'D0E4FF', size=2.4, target=K.empty(at(o, 0, 0.5, 1.6)))
    light(at(o, -2.5, -2.5, 5.6), 500, 'FFD0A0', size=3.0, target=K.empty(at(o, 0, 1.0, 1.6)))
    for iz in range(4):                                               # a bookcase of ledgers
        box(OAKD, at(o, -3.8, 3.6, 1.0 + iz * 1.25), (3.6, 0.5, 0.1))
        for ix in range(9):
            if rnd(ix, iz + 20) > 0.15:
                h = 0.8 + 0.3 * rnd(ix, iz)
                box(('6A2E26', '2E4A6A', '3E5A3A', '8A6A3A')[(ix + iz) % 4], at(o, -5.3 + ix * 0.37, 3.6, 1.07 + iz * 1.25 + h / 2), (0.3, 0.4, h))
    box(OAK, at(o, 0, 1.2, 1.75), (6.4, 2.6, 0.16))                   # the desk
    box(OAKD, at(o, 0, 0.0, 0.9), (6.2, 0.14, 1.7))
    for s in (-1, 1):
        box(OAKD, at(o, s * 2.9, 1.2, 0.85), (0.4, 2.4, 1.7))
    box('2E5A46', at(o, 0, 1.0, 1.84), (3.2, 1.7, 0.03))
    for i in range(5):
        box('F2EAD6', at(o, -2.3, 1.2, 1.87 + i * 0.05), (1.0, 1.3, 0.04), rot=(0, 0, 0.1 * rnd(i, 4)))
    cyl(BRASS, at(o, 2.3, 1.7, 2.3), 0.05, 0.9, rough=0.3)            # a desk lamp
    cone('2E7A4A', at(o, 2.3, 1.7, 2.85), 0.5, 0.12, 0.34, v=10)
    ball('FFE8B0', at(o, 2.3, 1.7, 2.72), 0.13, emit=7.0)
    S['paper_at'] = at(o, 0.55, 1.95, 1.87)
    box('F2EAD6', S['paper_at'], (1.5, 1.1, 0.03))
    for i in range(4):
        box('3A3430', plus(S['paper_at'], (0, 0.35 - i * 0.16, 0.02)), (1.1 - 0.2 * rnd(i, 9), 0.05, 0.01))
    S['inkmark'] = keep(box(STAMP1, FAR, (0.9, 0.34, 0.01), emit=0.5))


def make_cast(S):
    S['humans'] = []
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    m = person(S, 'may', dict(top=MAYCOAT, pants='3A3A4A', hand='E8B890', boot='5A3A28'), head_of('E8B890', '7A4A22', hat='bonnet', braids=STAMP1, smile=True), 0.62, skirt=MAYCOAT)
    m.head.scale = (1.32, 1.32, 1.32)
    S['stamps'] = []
    for i, (x, z, c) in enumerate(((-0.14, 0.82, STAMP1), (0.0, 0.82, STAMP2), (0.14, 0.82, STAMP1), (-0.07, 0.64, STAMP2), (0.07, 0.64, '4A9A5A'))):
        st = K.empty((x, -0.375, z), m.body, (0.07, 0, 0))
        box('F4EEDC', (0, 0, 0), (0.125, 0.012, 0.15), st)
        box(c, (0, -0.008, 0), (0.095, 0.012, 0.12), st, emit=0.3)
        S['stamps'].append(st)
    box('F2E2B8', (0.2, -0.36, 0.4), (0.2, 0.012, 0.13), m.body, rot=(0, 0.2, 0))        # an address tag on a string
    person(S, 'clerk', dict(top='E8E0D0', fore='E8E0D0', pants='3A3A44', hand='E0A880', boot='2A2420'), head_of('E0A880', '5A4030', hat='visor', tache='5A4030'))
    box('3A4A3A', (0, -0.02, 0.5), (0.66, 0.5, 0.9), S['clerk'].body)                      # a waistcoat
    person(S, 'father', dict(top='5A4A3A', pants='3A3028', hand='D8A078', boot='2A2420'), head_of('D8A078', '3A2A1E', hat='brim', tache='3A2A1E'))
    person(S, 'mother', dict(top='7A3A4A', pants='7A3A4A', hand='E8B890', boot='2A2420'), head_of('E8B890', '6A3E20', bun=True), skirt='7A3A4A')
    person(S, 'mochel', dict(top='2A3A5A', pants='222A40', hand='E0A880', boot='1A1A20'), head_of('E0A880', '4A3020', hat='cap'))
    for i in range(4):
        ball(BRASS, (0, -0.35, 0.3 + i * 0.2), 0.035, S['mochel'].body, rough=0.3)
    person(S, 'carrier', dict(top='6A7078', pants='5A6068', hand='D8A078', boot='2A2420'), head_of('D8A078', '8A8A8A', hat='cap', tache='8A8A8A'))
    box('8A5A30', (-0.4, 0.0, 0.15), (0.22, 0.5, 0.55), S['carrier'].body)                   # his mail satchel
    box('5A3A20', (0, 0, 0.75), (0.9, 0.08, 0.1), S['carrier'].body, rot=(0, 0.7, 0))
    person(S, 'gran', dict(top='6A5A7A', pants='4A4458', hand='E8C0A0', boot='2A2420'), head_of('E8C0A0', 'D8D8DC', bun=True, glasses=True), 0.92, skirt='4A4458')
    box('F2EAD6', (0, -0.3, 0.2), (0.5, 0.06, 0.7), S['gran'].body)                        # an apron
    person(S, 'gran2', dict(top='8A5A3A', pants='5A4030', hand='E0B090', boot='2A2420'), head_of('E0B090', 'B8B0A8', bun=True), 0.95, skirt='5A4030')
    person(S, 'boss', dict(top='2A2A32', pants='2A2A32', hand='E0A880', boot='1A1A20'), head_of('E0A880', 'B0B0B0', bald=True, glasses=True, tache='B0B0B0'))
    box('F2EAD6', (0, -0.3, 0.75), (0.2, 0.06, 0.4), S['boss'].body)
    person(S, 'kid2', dict(top='B8862E', pants='4A3A2A', hand='D8A078', boot='2A2420'), head_of('D8A078', '2A1E16', hat='flat', smile=True), 0.58)
    S['kid2'].head.scale = (1.3, 1.3, 1.3)
    box('F2E2B8', (0.0, -0.37, 0.7), (0.26, 0.012, 0.17), S['kid2'].body)
    box(STAMP1, (-0.06, -0.38, 0.72), (0.08, 0.012, 0.1), S['kid2'].body, emit=0.3)
    person(S, 'mum2', dict(top='3A5A6A', pants='3A5A6A', hand='D8A078', boot='2A2420'), head_of('D8A078', '2A1E16', bun=True), skirt='3A5A6A')
    S['cast_all'] = [S['rook']] + S['humans']
    S['rook'].s = 1.0


def make_props(S):
    S['hand'] = K.Hand('E0A880', 'E8E0D0', 0.62)
    S['hand'].root.location = FAR
    keep(S['hand'].root)
    S['hstamp'] = keep(K.empty(FAR))
    box('F4EEDC', (0, 0, 0), (0.16, 0.014, 0.19), S['hstamp'])
    box(STAMP2, (0, -0.008, 0), (0.12, 0.014, 0.15), S['hstamp'], emit=0.3)
    S['coins'] = [keep(cyl(('C8CCD6', 'C08A4A')[i % 2], FAR, 0.09, 0.025, v=10, rough=0.25)) for i in range(6)]
    S['ticket'] = keep(box('FF7A1A', FAR, (0.34, 0.02, 0.2), emit=0.5))
    S['rstamp'] = keep(K.empty(FAR))
    box('F4EEDC', (0, 0, 0), (0.17, 0.014, 0.2), S['rstamp'])
    box(STAMP1, (0, -0.008, 0), (0.13, 0.014, 0.16), S['rstamp'], emit=0.4)
    g = S['glass'] = keep(K.empty(FAR))                               # Rook's magnifying glass (ring in the x-z plane)
    K.add('torus', BRASS, (0, 0, 0), rot=(PI / 2, 0, 0), major_radius=0.3, minor_radius=0.035, major_segments=16, minor_segments=5, parent=g, rough=0.3)
    cyl('BFEFFF', (0, 0, 0), 0.29, 0.01, g, rot=(PI / 2, 0, 0), v=16, rough=0.05, alpha=0.18)
    cyl(OAKD, (0, 0, -0.55), 0.04, 0.5, g)
    S['weight'] = keep(cyl(BRASS, FAR, 0.1, 0.2, rough=0.2))
    cyl(BRASS, (0, 0, 0.14), 0.045, 0.1, S['weight'], rough=0.2)
    S['glint'] = keep(light(FAR, 0, 'FFE8A0', size=0.5))
    b = S['baby'] = keep(K.empty(FAR))                                # a baby in a blanket (lies along x)
    ball('F0E4C8', (0, 0, 0), 0.34, b, scale=(1.5, 0.85, 0.8))
    ball('F0C8A8', (0.42, -0.02, 0.1), 0.2, b)
    ball('F0E4C8', (0.46, 0.05, 0.17), 0.21, b, scale=(1, 1, 0.8))
    for s in (-1, 1):
        box('2A1E16', (0.44 + s * 0.07, -0.2, 0.12), (0.035, 0.02, 0.02), b)
    box('F4EEDC', (-0.1, -0.29, 0.06), (0.15, 0.012, 0.18), b, rot=(0.2, 0, 0))
    box(STAMP2, (-0.1, -0.3, 0.06), (0.11, 0.012, 0.14), b, rot=(0.2, 0, 0), emit=0.3)
    S['sack'] = keep(K.empty(FAR))                                    # an empty mail sack Rook can hold (mouth at local -z)
    cone(CANVAS, (0, 0, 0.6), 0.36, 0.5, 1.2, S['sack'], v=8)
    S['letters'] = [keep(box('F4EEDC', FAR, (0.3, 0.2, 0.015))) for _ in range(8)]
    S['rsack'] = keep(K.empty(FAR))                                   # the sack Rook sits in
    cone(CANVAS, (0, 0, 0.6), 0.75, 0.6, 1.2, S['rsack'], v=8)
    K.add('torus', '8A7A58', (0, 0, 1.2), major_radius=0.6, minor_radius=0.06, major_segments=10, minor_segments=4, parent=S['rsack'])
    S['case'] = keep(box('8A5A30', FAR, (0.5, 0.2, 0.36)))            # her small suitcase
    box('5A3A20', (0, 0, 0.6), (0.4, 0.1, 0.12), S['case'])
    S['rubber'] = keep(K.empty(FAR))                                  # a rubber stamp
    box(OAKD, (0, 0, 0.06), (0.5, 0.26, 0.12), S['rubber'])
    cyl(OAKD, (0, 0, 0.3), 0.06, 0.4, S['rubber'])
    ball(OAKD, (0, 0, 0.52), 0.1, S['rubber'])
    S['feather'] = keep(box('2F2B4D', FAR, (0.07, 0.02, 0.32)))
    S['htag'] = keep(box('F2E2B8', FAR, (0.22, 0.012, 0.14)))         # the tag tied to Rook's hat in the sack


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    for fn in (make_post, make_car, make_rail, make_ohio, make_lew, make_ban, make_cast, make_props):
        fn(S)
    S['suntgt'] = K.empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    S['sun'].data.angle = 0.06
    tgt, rigc = K.empty(), K.empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 4000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w44')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.05, 0.6
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs[2], mr.inputs[0])
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(mx.outputs[2], S['bg'].inputs[0])
    S['skymix'] = mx
    reset(S)
    return S


def reset(S):
    for rig in S['cast_all']:
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (rig.s, rig.s, rig.s)
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for st in S['stamps']:
        st.scale = (1, 1, 1)
    S['needle'].rotation_euler = (0, -2.2, 0)
    S['carlamp'].rotation_euler = (0, 0, 0)
    S['odoor'].rotation_euler = (0, 0, 0)
    S['ldoor'].rotation_euler = (0, 0, 0)
    S['sun'].data.energy = 0
    S['glint'].data.energy = 0
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, laugh=0.0)
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinks and Rook's beak, after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.41) % 1 < 0.035
    lg = S['laugh']
    ez = dict(calm=0.07, low=0.04, shocked=0.135, soft=0.06, squint=0.034).get(e, 0.07)
    tilt = dict(low=-0.06, shocked=0.36, soft=0.22, squint=-0.3).get(e, -0.22)
    if lg > 0.3:
        ez, tilt = 0.02, 0.3
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip = S['hat_tip']
    r['hat'].rotation_euler = (-0.2 + tip * 0.38, 0.07, 0)
    r['hat'].location = (0, 0, 0.27 + S['hat_jump'] + tip * 0.1)
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.36 if e == 'shocked' else 0.0) + lg * (0.42 + 0.16 * math.sin(t * 26)), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0) + lg * 0.12 * math.sin(t * 26), hd[1],
                                     hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.8, happy=0.7, warm=0.75, hard=0.6).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.05 if f in ('wide', 'happy') else -0.022 if f == 'hard' else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f == 'wide' else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.17 if f in ('warm', 'happy') else 0.13, 0.03, (0.035 + 0.05 * rig.jawv) if f in ('warm', 'happy') else 0.035 + 0.13 * rig.jawv + (0.05 if f == 'wide' else 0))
        x['mouth'].location.z = -0.02 - 0.03 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def amb(S, name):
    A = AMB[name]
    S['skymix'].inputs[6].default_value = K.hexc(A[0])
    S['skymix'].inputs[7].default_value = K.hexc(A[1])
    S['bg'].inputs[1].default_value = A[2]
    S['sun'].data.energy = A[3]
    S['sun'].data.color = K.hexc(A[4])[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(v * 500 for v in A[5])


def cam(S, pos, look, lens=35):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens


def orbit(S, k, yaw=20.0, push=0.15, rise=0.0):
    """Swing round the look-at point by `yaw` degrees across the shot, close in by `push` of the distance, rise by `rise`.
    Zero at the middle of the shot, so framings are written for k = 0.5."""
    c, tg = S['camrig'].location, S['camtgt'].location
    a = math.radians(yaw) * (k - 0.5)
    dx, dy = c[0] - tg[0], c[1] - tg[1]
    m = 1.0 + push * (0.5 - k)
    S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m,
                            tg[2] + (c[2] - tg[2]) * m + rise * (k - 0.5))


def stand(rig, loc, yaw=0.0, pose=None, face_=None, jaw=None):
    rig.place(loc, yaw)
    rig.apply(pose or P())
    if face_:
        rig.face = face_
    if jaw is not None:
        rig.jawv = jaw
    return rig


def head(rig):
    return wpos(rig.head)


def hand(rig, i=1):
    return wpos(rig.el[i], (0, -0.06, -0.6))


def step(t, speed=1.6, **over):
    p = K.walk(t, speed)
    p.update(over)
    for a in ('aL', 'aR'):
        p[a] = tuple(p[a]) + (0.0,) * (4 - len(p[a]))
    return p


def chat(t, on=True):
    return (0.45 + 0.45 * math.sin(t * 19)) if on else 0.0


def needle(S, k, to=1.72, wob=0.25):
    """The dial's needle swings up from rest, overshoots and settles a little short of the red limit mark (2.0)."""
    a = lerp(-2.2, to, K.act(k)) + wob * math.sin(k * 30) * max(0.0, 1 - k) * (1 if k > 0.05 else 0)
    S['needle'].rotation_euler = (0, a, 0)


def may_on_scale(S, t, pose=None, face_='happy', yaw=0.0, hop=0.0):
    p = S['scale_at']
    return stand(S['may'], (p[0], p[1], p[2] + hop), yaw, pose or P('stand', aL=(0.0, 0.25, 0.2), aR=(0.0, 0.25, 0.2), head=(-0.12, 0.1 * math.sin(t * 2))), face_)


def clerk_behind(S, t, pose=None, face_='calm', x=1.2, yaw=None):
    loc = at(POST, x, 2.7, 0)
    return stand(S['clerk'], loc, 0.0 if yaw is None else yaw, pose or P('stand', aL=(0.6, 0.1, 1.2), aR=(0.6, 0.1, 1.2)), face_)


def sway(S, t, amt=1.0):
    """The mail car rocks: the lamp swings, the camera rolls a little, the country goes past the open door."""
    S['carlamp'].rotation_euler = (0.1 * amt * math.sin(t * 2.3), 0.16 * amt * math.sin(t * 2.9), 0)
    S['cam'].rotation_euler = (0, 0, 0.018 * amt * math.sin(t * 2.9 + 0.5))
    for i, p in enumerate(S['poles']):
        x = ((t * 9.0 + i * 1.3) % 3.4) - 1.7
        p.location = at(CAR, -2.6 - x * 0.8, 2.59, 2.5)


def train_at(S, x, t, speed=14.0):
    S['train'].location = at(RAIL, x, 0, 0.36)
    for w, r in S['wheels']:
        w.rotation_euler = (0, x / r, 0)
    S['rod'].location = (2.2 + 0.5 * math.cos(x / 0.95), -1.2, 1.3 + 0.5 * math.sin(-x / 0.95))
    for i, sm_ in enumerate(S['smoke']):
        age = (t * 1.3 + i / 9.0 * 2.2) % 2.2
        sm_.location = at(RAIL, x + 5.0 - age * speed * 0.55, 0.3 * math.sin(i * 2.1), 5.4 + 2.6 * age ** 0.7)
        s = 0.5 + 1.1 * age
        sm_.scale = (s, s, s * 0.8)


def carry_baby(S, rig, loc, yaw, lift=0.0):
    S['baby'].location = off(loc, yaw, (0.05, -0.52, 1.95 + lift))
    S['baby'].rotation_euler = (0.1, 0, yaw)


CRADLE = dict(aL=(0.75, -0.2, 1.5, 0.9), aR=(0.75, -0.2, 1.5, 0.9))


# ---------------------------------------------------------------- the post office
def scale_girl(S, k, t, lt):
    """The opening and closing frame: May, close, hops onto the platform scale with stamps on her coat; the clerk's
    hand comes in from the right with one more stamp. With prm "loop" the camera closes in on the moment before."""
    amb(S, 'post')
    loop = S['prm'].get('loop')
    ka = 0.0 if loop else k
    crouch = math.sin(sm((k - 0.55) / 0.3) * PI) * 0.12 if loop else 0.0
    hop = 0.45 * sm((k - 0.75) / 0.18) if loop else 0.45 * max(0.0, 1 - k / 0.1) ** 2
    land = 0.0 if loop else math.exp(-max(0.0, k - 0.1) * 9) * math.sin(max(0.0, k - 0.1) * 40) * 0.06
    m = may_on_scale(S, t, P('stand', aL=(0.1, 0.5 - 0.3 * sm(ka / 0.2), 0.3), aR=(0.1, 0.5 - 0.3 * sm(ka / 0.2), 0.3), head=(-0.15, 0.25 - 0.3 * sm(ka)),
                                 lift=-crouch, lL=(crouch * 2, crouch * 4), lR=(crouch * 2, crouch * 4)), 'happy', 0.08, hop + land)
    m.jawv = 0.5
    needle(S, 0.0 if loop else max(0.0, (k - 0.1) / 0.9), wob=0.5)
    clerk_behind(S, t, P('stand', aL=(0.5, 0.2, 1.5), aR=(0.7, 0.1, 1.3), head=(0.2, 0.5)), 'calm', 0.3)
    h = head(m)
    reach = 0.0 if loop else sm((k - 0.35) / 0.45)
    S['hand'].place(mix(plus(h, (2.2, -0.9, -0.3)), plus(h, (0.62, -0.42, -0.62)), reach), (0.0, 0.0, -PI / 2 + 0.15))
    S['hand'].grip(0.55)
    hl = S['hand'].root.location
    S['hstamp'].location = (hl[0] - 0.24, hl[1] - 0.04, hl[2] - 0.03)
    S['hstamp'].rotation_euler = (0.1, 0, 0.3)
    c0, l0 = plus(h, (-0.4, -2.5, 0.2)), plus(h, (0.12, 0, -0.1))
    if loop:
        kk = sm(k / 0.8)
        hb = plus(S['scale_at'], (0, 0, h[2] - m.root.location[2]))
        c0, l0 = plus(hb, (-0.4, -2.5, 0.2 + hop)), plus(hb, (0.12, 0, -0.1 + hop))
        cam(S, mix(plus(hb, (2.6, -7.5, 1.6)), c0, kk), mix(plus(hb, (0.6, 0, 0.6)), l0, kk), lerp(26, 36, kk))
    else:
        cam(S, mix(c0, plus(h, (-0.15, -1.9, 0.2)), sm(k)), mix(l0, plus(h, (0.2, 0, -0.18)), sm(k)), 36)


def dial(S, k, t, lt):
    """Looking up past May's bobble hat at the big dial: the needle swings round and stops just short of the red mark."""
    amb(S, 'post')
    m = may_on_scale(S, t, P('stand', aL=(0.0, 0.3, 0.2), aR=(0.0, 0.3, 0.2), head=(-0.5, 0.0)), 'wide', PI)
    needle(S, 0.15 + 0.85 * k, wob=0.6)
    d = S['dial_at']
    cam(S, plus(d, (0.9, -3.4, -2.2)), plus(d, (0.0, 0, -0.5)), 34)
    orbit(S, k, -22, 0.3, 0.6)


def stamp_on(S, k, t, lt):
    """Close on her coat: a hand presses a stamp on beside the others and thumps it flat; she looks down at it, delighted."""
    amb(S, 'post')
    m = may_on_scale(S, t, P('stand', aL=(0.0, 0.5, 0.3), aR=(0.0, 0.5, 0.3), head=(0.35 * sm(k / 0.4), 0.0)), 'happy', 0.05)
    m.jawv = 0.3 + 0.4 * sm((k - 0.5) / 0.2)
    needle(S, 1.0)
    st = wpos(S['stamps'][4])
    press = sm(k / 0.4)
    thump = 0.12 * math.exp(-max(0, k - 0.4) * 10) * math.sin(max(0, k - 0.4) * 30)
    S['stamps'][4].scale = (1, 1, 1) if k > 0.38 else (0, 0, 0)
    hp = mix(plus(st, (1.3, -0.8, -0.3)), plus(st, (0.25, -0.08 - thump, -0.02)), press)
    if k > 0.7:
        hp = mix(hp, plus(st, (1.6, -0.6, -0.4)), sm((k - 0.7) / 0.3))
    S['hand'].place(hp, (0.0, 0.0, -PI / 2 + 0.2))
    S['hand'].grip(0.25)
    if k <= 0.38:
        S['hstamp'].location = (hp[0] - 0.25, hp[1] - 0.03, hp[2] + 0.02)
    cam(S, plus(st, (-0.35, -2.0, 0.5)), plus(st, (0.05, 0, 0.3)), 40)
    orbit(S, k, 16, 0.25, 0.0)


def rook_counter(S, k, t, lt):
    """Rook is already there, leaning on the counter with his arms crossed and his brim low, the girl on the scale
    behind him: "You can't post a child." He jerks his head at her on the last word."""
    amb(S, 'post')
    rk = S['rook']
    turn = lerp(-0.1, 0.55, sm((k - 0.5) / 0.3))
    stand(rk, at(POST, -0.3, 0.3, 0), -0.2, P('cross', lean=-0.08, head=(0.05, turn), lL=(0.15, 0.1)))
    S['rface'], S['hat_tip'] = 'low', 0.55
    m = may_on_scale(S, t, P('stand', aL=(0.0, 0.3, 0.2), aR=(1.6 + 0.3 * math.sin(lt * 9), 0.5, 0.4), head=(-0.15, -0.4)), 'happy', -0.3)   # she waves at him
    m.jawv = 0.4
    needle(S, 1.0)
    clerk_behind(S, t, P('stand', aL=(0.6, 0.1, 1.2), aR=(0.9, 0.0, 1.6), head=(0.3, 0.2)), 'calm', 2.4)
    h = head(rk)
    cam(S, plus(h, (0.2, -5.2, -0.2)), plus(h, (-1.0, 0.0, -0.5)), 30)
    orbit(S, k, 16, 0.22, 0.0)


def parents(S, k, t, lt):
    """Her father counts coins out onto the counter one by one, her mother beside him; the clerk slides stamps across."""
    amb(S, 'post')
    fl = at(POST, 2.3, 0.45, 0)
    stand(S['father'], fl, PI, P('stand', aR=(1.0 + 0.12 * math.sin(lt * 10), 0.0, 0.9), aL=(0.2, 0.1, 0.3), head=(0.15, 0.0), lean=0.1), 'calm')
    stand(S['mother'], at(POST, 3.6, 0.3, 0), PI - 0.25, P('stand', aL=(0.7, -0.1, 1.5, 0.8), aR=(0.7, -0.1, 1.5, 0.8), head=(0.2, 0.3)), 'warm')
    clerk_behind(S, t, P('stand', aR=(1.0, 0.0, 0.8), aL=(0.5, 0.1, 1.2), head=(0.4, 0.0), lean=0.15), 'calm', 3.3)
    n = int(min(6, k * 7.5))
    for i, c in enumerate(S['coins']):
        if i < n:
            c.location = at(POST, 2.0 + 0.24 * (i % 3), 1.05 + 0.24 * (i // 3), 2.0)
        elif i == n:
            c.location = plus(hand(S['father'], 1), (0, 0, -0.05))
    S['rstamp'].location = at(POST, 2.9, 1.5 - 0.3 * sm(k), 2.0)
    S['rstamp'].rotation_euler = (PI / 2, 0, 0.2)
    may_on_scale(S, t, None, 'happy', -0.4)
    needle(S, 1.0)
    cam(S, at(POST, 0.9, 3.9, 2.95), at(POST, 2.8, 0.5, 2.5), 26)
    orbit(S, k, 18, 0.2, -0.3)


def coat_close(S, k, t, lt):
    """Low and close in front of May: she pulls her coat straight, chin up, proud of her row of stamps."""
    amb(S, 'post')
    tug = math.sin(min(1.0, k / 0.5) * PI)
    m = may_on_scale(S, t, P('stand', aL=(0.5, -0.1, 1.3 + 0.3 * tug, 0.5), aR=(0.5, -0.1, 1.3 + 0.3 * tug, 0.5), head=(-0.2 * sm(k / 0.6), 0.15 * math.sin(lt * 3))),
                     'happy', -0.1)
    m.jawv = 0.6
    needle(S, 1.0)
    clerk_behind(S, t, None, 'warm', -0.4)
    h = head(m)
    cam(S, plus(h, (0.7, -2.5, -0.75)), plus(h, (0.0, 0, -0.42)), 38)
    orbit(S, k, -26, 0.2, 0.5)


def rook_ticket(S, k, t, lt):
    """Rook by the window holds a railway ticket up in one hand and a stamp in the other, looks from one to the other,
    and lets the ticket drop."""
    amb(S, 'post')
    rk = S['rook']
    look = math.sin(lt * 4.5) * (1 - sm((k - 0.6) / 0.2))
    drop = sm((k - 0.62) / 0.3)
    loc = at(POST, -3.9, -2.2, 0)
    stand(rk, loc, 0.35, P('stand', aR=(0.75, 0.7, 1.35, 0.0), aL=(0.75 - 0.5 * drop, 0.7, 1.35, 0.0), head=(0.1, 0.5 * look)))
    S['rface'] = 'squint' if k < 0.6 else 'low'
    S['hat_tip'] = 0.3 * drop
    S['rstamp'].location = plus(hand(rk, 1), (0, -0.08, 0.14))
    S['rstamp'].rotation_euler = (0, 0, 0.35)
    hl = plus(hand(rk, 0), (0, -0.08, 0.14))
    S['ticket'].location = (hl[0], hl[1], hl[2] - 2.6 * drop * drop) if drop < 0.99 else FAR
    S['ticket'].rotation_euler = (drop * 5, drop * 3, 0.35)
    h = head(rk)
    cam(S, plus(h, (1.4, -3.6, -0.1)), plus(h, (0.05, 0, -0.3)), 34)
    orbit(S, k, 22, 0.2, 0.0)


def rook_scale(S, k, t, lt):
    """Rook's detective moment: up on his toes beside the scale with his magnifying glass on the dial, reading the
    needle; May looks up at him."""
    amb(S, 'post')
    rk = S['rook']
    d = S['dial_at']
    loc = at(POST, -1.2, 0.35, 0)
    up = sm(k / 0.3)
    stand(rk, loc, facing(loc, d) * 0.45, P('stand', aR=(2.3 * up + 0.3, 0.1, 0.5), aL=(0.3, 0.1, 0.8), head=(-0.45 * up, 0.0), lift=0.12 * up, lL=(0, 0), lean=-0.05))
    S['rface'] = 'squint'
    hr = hand(rk, 1)
    S['glass'].location = plus(hr, (-0.25, -0.05, 0.3))
    S['glass'].rotation_euler = (0, 0.25 + 0.1 * math.sin(lt * 3), 0.5)
    may_on_scale(S, t, P('stand', aL=(0.0, 0.3, 0.2), aR=(0.0, 0.3, 0.2), head=(-0.45, -0.6)), 'wide', 0.2)
    needle(S, 1.0, 1.72 + 0.03 * math.sin(lt * 7))
    cam(S, plus(d, (-0.9, -5.0, -1.2)), plus(d, (0.6, 0, -0.8)), 32)
    orbit(S, k, 24, 0.28, 0.4)


def weigh_wide(S, k, t, lt):
    """The whole post office: the girl on the scale, the clerk leaning over the counter to read the dial and writing
    the weight down, parcels and pigeonholes around them."""
    amb(S, 'post')
    may_on_scale(S, t, P('stand', aL=(0.0, 0.3, 0.2), aR=(0.0, 0.3, 0.2), head=(-0.3, 0.0), lift=0.05 * abs(math.sin(lt * 6))), 'happy', PI)
    needle(S, 1.0, 1.72 + 0.04 * math.sin(lt * 8))
    cl = at(POST, -0.9, 0.9, 0)
    stand(S['clerk'], cl, facing(cl, S['dial_at']), P('stand', aR=(1.0, 0.1, 1.6 + 0.2 * math.sin(lt * 14)), aL=(0.9, 0.0, 1.5), head=(-0.3 + 0.5 * sm((k - 0.5) / 0.2), 0.0)), 'calm')
    stand(S['father'], at(POST, 0.7, -0.3, 0), 2.2, P('hips'), 'calm')
    stand(S['mother'], at(POST, 1.7, 0.2, 0), 2.4, P('stand', aL=(0.7, -0.1, 1.5, 0.8), aR=(0.7, -0.1, 1.5, 0.8)), 'warm')
    cam(S, at(POST, 1.0, -5.0, 2.8), at(POST, -1.2, 1.0, 2.3), 28)
    orbit(S, k, 26, 0.3, 0.5)


def limit(S, k, t, lt):
    """Very close on the dial: the needle trembles a hair under the red limit mark; the clerk's finger taps the mark."""
    amb(S, 'post')
    may_on_scale(S, t, None, 'happy', PI)
    needle(S, 1.0, 1.72 + 0.05 * math.sin(lt * 9) * (1 - k))
    d = S['dial_at']
    a = 2.0
    tip = plus(d, (0.66 * math.sin(a), -0.12, 0.66 * math.cos(a)))
    tap = abs(math.sin(lt * 7))
    S['hand'].place(plus(tip, (0.25 + 0.06 * tap, -0.12, -0.03 - 0.03 * tap)), (0.0, 0.5, -PI / 2))
    S['hand'].grip(0.75)
    S['hand'].f[0][0].rotation_euler = (0, 0, 0)
    S['hand'].f[0][1].rotation_euler = (0, 0, 0)
    cam(S, plus(d, (-0.3, -2.4, -0.25)), plus(d, (0.5, 0, -0.12)), 42)
    orbit(S, k, 18, 0.25, 0.0)


# ---------------------------------------------------------------- the mail train
def train_wide(S, k, t, lt):
    """The mail train comes round through the snowy hills towards us, smoke streaming back, pines and poles going by."""
    amb(S, 'rail')
    x = lerp(-22, 6, k)
    train_at(S, x, t)
    cam(S, at(RAIL, 15 - 4 * k, -8.5, 1.8 + 1.6 * k), at(RAIL, x + 1, 0, 3.2), 24)


def wheels(S, k, t, lt):
    """Low beside the rails: the red driving wheels and the rod pounding round, snow dust flying."""
    amb(S, 'rail')
    x = lerp(-6, 9, k)
    train_at(S, x, t)
    cam(S, at(RAIL, x + 4.6, -5.2, 1.0), at(RAIL, x + 1.4, 0, 1.7), 30)
    orbit(S, k, -14, 0.2, 0.6)


def may_seat(S, t, pose=None, face_='happy', yaw=0.2):
    p = S['seat_at']
    return stand(S['may'], (p[0], p[1], p[2] + 1.2 + 0.03 * math.sin(t * 5.8)), yaw,
                 pose or P('sit', lL=(1.45, 1.2 + 0.4 * math.sin(t * 5)), lR=(1.45, 1.2 - 0.4 * math.sin(t * 5)), lift=-0.9, lean=0.0, head=(0.0, 0.2 * math.sin(t * 1.5)),
                           aL=(0.2, 0.4, 0.3), aR=(0.2, 0.4, 0.3)), face_)


def sorter(S, t, x=3.4, look=0.0, face_='calm'):
    """Leonard Mochel at the letter case, flicking letters into the pigeonholes."""
    loc = at(CAR, x, 0.9, 0)
    return stand(S['mochel'], loc, PI + 0.35, P('stand', aR=(1.6 + 0.4 * math.sin(t * 7), 0.0, 0.7), aL=(0.9, 0.0, 1.5), head=(0.0, look)), face_)


def car_inside(S, k, t, lt):
    """Inside the mail car: May sits on a mail sack swinging her legs, her little suitcase beside her, the clerk
    sorting letters at the case, the open door flashing daylight, the lamp swinging."""
    amb(S, 'car')
    sway(S, t)
    may_seat(S, t)
    S['case'].location = at(CAR, 0.1, 0.0, 0.2)
    S['case'].rotation_euler = (0, 0, 0.3)
    sorter(S, t, 2.1, look=-0.5 * sm((k - 0.5) / 0.3))
    cam(S, at(CAR, 0.5, -5.2, 2.5), at(CAR, 0.45, 0.8, 1.9), 28)
    orbit(S, k, -22, 0.25, 0.0)


def rook_sack(S, k, t, lt):
    """Rook rides as a parcel too: he pops up out of a mail sack beside her with a tag tied to his hat, arms crossed,
    unimpressed; she laughs at him."""
    amb(S, 'car')
    sway(S, t)
    m = may_seat(S, t, None, 'happy', -0.5)
    m.jawv = chat(t)
    rk = S['rook']
    up = K.act(sm(k / 0.3))
    base = at(CAR, 0.5, -0.5, 0)
    S['rsack'].location = base
    stand(rk, plus(base, (0, 0, -1.9 + 1.2 * up)), -0.25, P('cross', head=(0.05, 0.35 * sm((k - 0.5) / 0.3))))
    S['rface'], S['hat_tip'] = 'low', 0.4
    S['htag'].location = plus(head(rk), (0.62, -0.1, 0.1 + 0.05 * math.sin(lt * 6)))
    S['htag'].rotation_euler = (0, 0.4 + 0.3 * math.sin(lt * 6), 0.2)
    h = plus(base, (0, 0, 2.6))
    cam(S, plus(h, (0.9, -4.6, 0.0)), plus(h, (-0.6, 0, -0.5)), 32)
    orbit(S, k, 20, 0.22, 0.0)


def rook_sackcheck(S, k, t, lt):
    """Rook tests the idea: he holds a mail sack upside down and shakes it. Only letters fall out. He peers into it."""
    amb(S, 'car')
    sway(S, t, 0.7)
    rk = S['rook']
    loc = at(CAR, 0.6, -0.6, 0)
    shake = math.sin(lt * 16) * (1 - sm((k - 0.6) / 0.15))
    peer = sm((k - 0.65) / 0.25)
    stand(rk, loc, -0.2, P('stand', aL=(2.2 - 0.6 * peer, 0.25, 0.5 + 0.9 * peer), aR=(2.2 - 0.6 * peer, 0.25, 0.5 + 0.9 * peer), head=(-0.35 * peer, 0.0)))
    S['rface'] = 'squint' if peer > 0.5 else 'calm'
    hl, hr = hand(rk, 0), hand(rk, 1)
    mid = mix(hl, hr, 0.5)
    S['sack'].location = plus(mid, (0, -0.1, 0.05 + 0.5 * peer + 0.08 * shake))
    S['sack'].rotation_euler = (-0.5 * peer, 0.12 * shake, 0)
    for i, l in enumerate(S['letters']):
        a = max(0.0, lt * 1.3 - 0.08 * i)
        z = mid[2] - 0.2 - 4.5 * a * a
        l.location = (mid[0] + 0.9 * (rnd(i, 1) - 0.5) * a * 2, mid[1] - 0.3 + 0.8 * (rnd(i, 2) - 0.5) * a, max(CAR[2] + 0.03 + 0.02 * i, z))
        l.rotation_euler = (a * 7 * rnd(i, 3), a * 5 * rnd(i, 4), i) if z > CAR[2] + 0.2 else (0, 0, i * 1.1)
    m = may_seat(S, t, None, 'happy', -0.6)
    m.jawv = chat(t)
    h = head(rk)
    cam(S, plus(h, (-0.5, -5.0, 0.2)), plus(h, (-0.5, 0, -0.9)), 28)
    orbit(S, k, -20, 0.22, 0.0)


def cousin(S, k, t, lt):
    """The mail clerk leaves his letters, crouches down in front of May and buttons the top of her coat; she beams at him."""
    amb(S, 'car')
    sway(S, t, 0.7)
    m = may_seat(S, t, None, 'happy', 0.9)
    m.jawv = 0.5
    p = S['seat_at']
    loc = (p[0] + 1.45, p[1] - 0.25, p[2])
    fuss = 0.15 * math.sin(lt * 9)
    stand(S['mochel'], loc, facing(loc, p) , P('stand', lL=(1.3, 1.9), lR=(0.3, 1.5), lift=-0.75, lean=0.2, aR=(1.2 + fuss, 0.0, 0.7), aL=(1.2 - fuss, 0.0, 0.7), head=(-0.1, 0.0)), 'warm', 0.3)
    hm = head(m)
    cam(S, plus(hm, (1.1, -4.4, 0.3)), plus(hm, (0.7, 0, -0.1)), 34)
    orbit(S, k, 22, 0.22, 0.0)


def car_window(S, k, t, lt):
    """At the open door: May holds on and watches the hills go by, the clerk's hand on her shoulder, Rook beside them
    holding his hat on in the wind."""
    amb(S, 'car')
    sway(S, t, 1.2)
    dz = at(CAR, -2.6, 1.6, 0)
    m = stand(S['may'], plus(dz, (-0.2, 0, 0)), PI + 0.2, P('stand', aR=(1.9 + 0.2 * math.sin(lt * 8), 0.3, 0.3), aL=(0.3, 0.2, 0.3), head=(-0.2, 0.5 * math.sin(lt * 1.8))), 'wide')
    stand(S['mochel'], plus(dz, (0.75, -0.55, 0)), PI - 0.3, P('stand', aL=(0.8, 0.3, 0.9), aR=(0.2, 0.1, 0.3), head=(0.25, -0.3)), 'warm')
    rk = S['rook']
    stand(rk, plus(dz, (-1.25, -0.5, 0)), 0.8, P('hat', head=(0.0, -0.5 + 0.2 * math.sin(lt * 2)), lean=-0.1))
    S['rface'], S['hat_tip'] = 'calm', 0.2 + 0.2 * abs(math.sin(lt * 6))
    S['hat_jump'] = 0.03 * abs(math.sin(lt * 11))
    cam(S, plus(dz, (0.4, -4.6, 2.5)), plus(dz, (-0.3, 0, 1.9)), 30)
    orbit(S, k, -24, 0.25, 0.0)


# ---------------------------------------------------------------- Ohio, a year earlier
def baby_bundle(S, k, t, lt):
    """Close on a baby in a blanket in the rural carrier's arms, a stamp on the blanket; the carrier looks down at him
    and rocks him."""
    amb(S, 'ohio')
    loc = at(OHIO, -1.0, -0.6, 0)
    rock = 0.06 * math.sin(lt * 4)
    c = stand(S['carrier'], loc, 0.25, P('stand', head=(0.4, 0.0), lean=0.05 + rock * 0.5, **CRADLE), 'warm')
    carry_baby(S, c, loc, 0.25, rock)
    b = S['baby'].location
    cam(S, plus(b, (0.5, -2.6, 0.45)), plus(b, (0.1, 0, 0.2)), 40)
    orbit(S, k, -26, 0.25, 0.0)


def rook_hatjump(S, k, t, lt):
    """Rook by the farm mailbox sees the carrier walk past with the baby: his beak drops, his hat hops off his head and
    a feather comes loose."""
    amb(S, 'ohio')
    rk = S['rook']
    loc = at(OHIO, -1.4, -2.8, 0)
    cx = lerp(-2.4, 1.2, k)
    cl = at(OHIO, cx, 0.2, 0)
    c = stand(S['carrier'], cl, PI / 2, step(t, 1.5, head=(0.2, 0.0), **CRADLE), 'warm')
    carry_baby(S, c, cl, PI / 2, 0.02 * math.sin(t * 9))
    shock = sm((k - 0.15) / 0.15)
    stand(rk, loc, 0.45, blend(P('stand', head=(0.0, 0.5)), P('scream', head=(-0.1, 0.35)), shock))
    S['rface'] = 'shocked' if shock > 0.3 else 'calm'
    S['hat_jump'] = 0.5 * math.sin(min(1.0, max(0.0, (k - 0.15) / 0.5)) * PI)
    h = head(rk)
    f = max(0.0, k - 0.3)
    S['feather'].location = plus(h, (0.5 + 0.3 * math.sin(f * 14), -0.2, 0.2 - 1.6 * f))
    S['feather'].rotation_euler = (f * 6, 0.5, f * 9)
    cam(S, plus(h, (-0.2, -4.4, -0.3)), plus(h, (0.3, 0, -0.1)), 30)
    orbit(S, k, 18, 0.22, 0.0)


def carrier_lane(S, k, t, lt):
    """Wide, at dusk: the carrier walks up the lane along the white fence towards the lit farmhouse, the baby in his arms."""
    amb(S, 'ohio')
    cx = lerp(-1.0, 4.5, k)
    cl = at(OHIO, cx, 0.3, 0)
    c = stand(S['carrier'], cl, PI / 2 + 0.2, step(t, 1.5, head=(0.15, 0.0), **CRADLE), 'warm')
    carry_baby(S, c, cl, PI / 2 + 0.2, 0.02 * math.sin(t * 9))
    cam(S, at(OHIO, cx - 3.2, -4.6, 1.5), at(OHIO, cx + 1.6, 1.6, 2.5), 26)
    orbit(S, k, 12, 0.2, 1.2)


def rook_follow(S, k, t, lt):
    """Rook trots along beside the carrier, craning over his arm to look at the baby, and taps his beak."""
    amb(S, 'ohio')
    cx = lerp(3.0, 6.0, k)
    cl = at(OHIO, cx, 0.4, 0)
    c = stand(S['carrier'], cl, PI / 2, step(t, 1.5, head=(0.3, -0.3), **CRADLE), 'warm')
    carry_baby(S, c, cl, PI / 2, 0.02 * math.sin(t * 9))
    rk = S['rook']
    rl = at(OHIO, cx - 1.35, -0.7, 0)
    stand(rk, rl, PI / 2 - 0.55, step(t + 0.3, 1.9, aR=(1.25, -0.25, 2.2, 0.6), lean=0.3, head=(0.3, 0.2)))
    S['rface'] = 'soft'
    cam(S, at(OHIO, cx + 3.6, -4.6, 2.3), at(OHIO, cx - 0.4, -0.3, 2.25), 32)
    orbit(S, k, -14, 0.15, 0.0)


def ohio_door(S, k, t, lt):
    """The farmhouse porch: the door swings open, the grandmother throws up her hands, and the carrier holds the baby out to her."""
    amb(S, 'ohio')
    d = S['odoor_at']
    op = sm(k / 0.3)
    S['odoor'].rotation_euler = (0, 0, 1.7 * op)
    give = sm((k - 0.4) / 0.4)
    cl = plus(d, (1.15, -0.1, 0))
    cy = facing(cl, plus(d, (-0.2, 0.6, 0)))
    c = stand(S['carrier'], cl, cy, P('stand', aL=(0.75 + 0.5 * give, -0.2, 1.5 - 0.9 * give, 0.9), aR=(0.75 + 0.5 * give, -0.2, 1.5 - 0.9 * give, 0.9), head=(0.1, 0.0)), 'warm')
    S['baby'].location = off(cl, cy, (0.05, -0.52 - 0.4 * give, 1.95 + 0.1 * give))
    S['baby'].rotation_euler = (0.1, 0, cy + PI)
    g = stand(S['gran2'], plus(d, (-0.25, 1.5 - 0.9 * op, 0)), 0.35, blend(P('stand'), P('scream', head=(0.1, 0.0)), sm((k - 0.25) / 0.2)), 'wide', 0.7)
    cam(S, plus(d, (-2.4, -5.6, 1.7)), plus(d, (0.35, 0.2, 1.75)), 32)
    orbit(S, k, 22, 0.25, 0.0)


# ---------------------------------------------------------------- Lewiston
def door(S, k, t, lt):
    """Snowy morning in Lewiston: the mail clerk walks May up the steps by the hand, the door flies open and her
    grandmother comes out with her arms wide; May runs the last step into them."""
    amb(S, 'lew')
    d = S['ldoor_at']
    wk = sm(k / 0.55)
    op = sm((k - 0.35) / 0.25)
    hug = sm((k - 0.6) / 0.3)
    S['ldoor'].rotation_euler = (0, 0, 1.8 * op)
    ml = mix(plus(d, (-0.3, -4.4, -0.7)), plus(d, (-0.3, -1.5, 0)), wk)
    ml = mix(ml, plus(d, (0.05, -0.75, 0)), hug)
    ml = (ml[0], ml[1], d[2] - 0.7 + 0.7 * sm((wk - 0.45) / 0.3))
    stand(S['may'], ml, PI + 0.1, step(t, 2.4, aR=(1.3 + 1.2 * hug, 0.4, 0.3), aL=(0.3 + 2.2 * hug, 0.4, 0.3), head=(-0.3, 0.0)) if hug < 0.95 else P('up'), 'happy', 0.6)
    cl = mix(plus(d, (1.4, -5.0, -0.7)), plus(d, (2.1, -3.0, -0.7)), wk)
    stand(S['mochel'], cl, PI - 0.15, step(t, 1.5, aL=(0.9 * (1 - hug), 0.5, 0.4)) if wk < 0.98 else P('hips'), 'warm')
    S['case'].location = plus(hand(S['mochel'], 1), (0, 0, -0.35))
    S['case'].rotation_euler = (0, 0, PI / 2 - 0.15)
    stand(S['gran'], plus(d, (0.1, 1.0 - 1.0 * op, 0)), 0.0, blend(P('stand'), P('stand', aL=(1.2, 0.9, 0.5), aR=(1.2, 0.9, 0.5), lean=0.25, head=(0.3, 0.0)), sm((k - 0.4) / 0.25)), 'happy', 0.7)
    cam(S, plus(d, (2.4, -8.0, 1.3)), plus(d, (0.2, -0.8, 1.4)), 32)
    orbit(S, k, -24, 0.35, 0.6)


def rook_delivered(S, k, t, lt):
    """Rook at the foot of the steps watches the hug in the doorway, touches his hat brim and looks back at us."""
    amb(S, 'lew')
    d = S['ldoor_at']
    S['ldoor'].rotation_euler = (0, 0, 1.8)
    gl = plus(d, (0.1, 0.0, 0))
    stand(S['gran'], gl, 0.0, P('stand', aL=(1.0, -0.3, 1.2, 0.6), aR=(1.0, -0.3, 1.2, 0.6), lean=0.35, head=(0.4, 0.0)), 'happy', 0.4)
    stand(S['may'], plus(d, (0.05, -0.7, 0)), PI, P('up', aL=(2.0, 0.5, 0.6), aR=(2.0, 0.5, 0.6), lift=0.05 * abs(math.sin(lt * 7))), 'happy')
    stand(S['mochel'], plus(d, (1.9, -2.6, -0.7)), PI - 0.5, P('hips'), 'warm')
    rk = S['rook']
    rl = plus(d, (-2.2, -3.5, -0.7))
    turn = sm((k - 0.3) / 0.3)
    stand(rk, rl, lerp(2.6, 0.3, turn), blend(P('stand', head=(-0.1, 0.0)), P('hat', head=(0.1, 0.0)), sm((k - 0.3) / 0.3)))
    S['rface'], S['hat_tip'] = 'soft', 0.3 * turn
    h = head(rk)
    cam(S, plus(h, (-0.2, -4.6, -0.4)), plus(h, (1.0, 0.6, -0.25)), 30)
    orbit(S, k, 20, 0.2, 0.0)


# ---------------------------------------------------------------- the ban
def ban_desk(S, k, t, lt):
    """An office in Washington: a bald official in a dark suit reads a newspaper cutting, scowls, lifts a rubber stamp
    high and brings it down on an order; the red mark is left on the paper."""
    amb(S, 'ban')
    b = S['boss']
    loc = at(BAN, 0.3, 3.05, 0)
    hit = 0.55
    up = sm(k / 0.4)
    dn = sm((k - 0.45) / (hit - 0.45))
    arm = lerp(lerp(1.0, 2.5, up), 0.95, dn)
    stand(b, loc, 0.0, P('stand', aR=(arm, 0.0, 0.5), aL=(0.8, 0.0, 1.4), lean=0.15 + 0.15 * dn, head=(0.35, 0.0)), 'hard', 0.2)
    pa = S['paper_at']
    hr = hand(b, 1)
    after = sm((k - hit - 0.1) / 0.2)
    S['rubber'].location = (hr[0], hr[1] - 0.05, max(pa[2] + 0.02, hr[2] - 0.3)) if k < hit + 0.1 else mix(plus(pa, (0, 0, 0.02)), plus(pa, (1.1, 0.2, 0.0)), after)
    if k >= hit:
        S['inkmark'].location = plus(pa, (0, -0.25, 0.022))
    S['cam'].rotation_euler = (0, 0, 0.03 * math.exp(-max(0, k - hit) * 14) * math.sin((k - hit) * 80) if k > hit else 0)
    cam(S, at(BAN, -1.0, -0.7, 3.2), at(BAN, 0.4, 2.7, 2.1), 37)
    orbit(S, k, 26, 0.3, -0.4)


def rook_notice(S, k, t, lt):
    """Back in the post office: Rook reads the new notice pinned to the board, taps his beak, and looks round at us."""
    amb(S, 'post')
    rk = S['rook']
    loc = at(POST, -3.5, 3.4, 0)
    turn = sm((k - 0.4) / 0.3)
    tapk = 0.25 * abs(math.sin(lt * 7)) * (1 - turn)
    stand(rk, loc, lerp(PI + 0.3, -0.45, turn), P('tap', aR=(1.25 + tapk, -0.25, 2.2, 0.6), head=(-0.2 * (1 - turn), 0.0)))
    S['rface'] = 'squint' if turn < 0.5 else 'low'
    S['hat_tip'] = 0.4 * turn
    clerk_behind(S, t, None, 'calm', 2.0)
    cam(S, at(POST, -5.0, 0.4, 2.8), at(POST, -3.6, 4.2, 2.7), 30)
    orbit(S, k, -22, 0.25, 0.0)


def anyway_counter(S, k, t, lt):
    """A year on, the same counter from the other end: a mother pushes a small boy with a tag on his coat up to it; the
    clerk glances at the notice on the wall, then at the boy, and shrugs."""
    amb(S, 'post')
    push = sm(k / 0.4)
    kl = at(POST, 1.4, lerp(-0.9, 0.5, push), 0)
    tk = sm((k - 0.6) / 0.25)
    stand(S['kid2'], kl, lerp(2.3, 0.5, tk), step(t, 2.0, head=(-0.3, 0.0)) if push < 0.98 else P('stand', head=(-0.3 + 0.2 * tk, 0.0), aL=(0.0, 0.3, 0.2), aR=(0.0, 0.3, 0.2)), 'happy')
    stand(S['mum2'], plus(kl, (0.95, -0.55, 0)), 2.3, P('stand', aR=(1.0, 0.0, 0.5), aL=(1.0, 0.0, 0.5), lean=0.15, head=(0.2, 0.0)), 'warm', 0.4)
    look = sm((k - 0.3) / 0.15) * (1 - sm((k - 0.55) / 0.15))
    sh = sm((k - 0.65) / 0.2)
    clerk_behind(S, t, blend(P('stand', aL=(0.6, 0.1, 1.2), aR=(0.6, 0.1, 1.2), head=(0.2, 1.0 * look)), P('shrug', head=(0.2, 0.0)), sh), 'calm', 1.6)
    cam(S, at(POST, -0.3, -2.3, 1.9), at(POST, 1.6, 1.0, 1.75), 27)
    orbit(S, k, -20, 0.25, 0.0)


def rook_laugh(S, k, t, lt):
    """Rook, with his elbow on the counter, watches the clerk stamp the boy's tag, throws his head back and caws."""
    amb(S, 'post')
    kl = at(POST, 2.0, 0.5, 0)
    stand(S['kid2'], kl, PI + 0.6, P('stand', head=(-0.3, 0.4), aL=(0.0, 0.3, 0.2), aR=(0.0, 0.3, 0.2), lift=0.04 * abs(math.sin(lt * 8))), 'happy')
    stand(S['mum2'], plus(kl, (0.6, -1.3, 0)), PI + 0.2, P('stand', aL=(0.7, -0.1, 1.5, 0.8), aR=(0.7, -0.1, 1.5, 0.8)), 'warm')
    thump = abs(math.sin(lt * 6))
    clerk_behind(S, t, P('stand', aR=(1.1 - 0.3 * thump, 0.0, 0.8 + 0.5 * thump), aL=(0.6, 0.1, 1.2), lean=0.1, head=(0.3, 0.0)), 'warm', 2.0)
    rk = S['rook']
    lg = sm((k - 0.25) / 0.2)
    stand(rk, at(POST, 3.9, 0.35, 0), 0.75, P('stand', aL=(0.9, 0.5, 1.6, 0.4), aR=(0.3 + 0.5 * lg, 0.5 * lg, 1.2 * lg), lean=-0.12 * lg, head=(-0.3 * lg, -0.3 * (1 - lg))))
    S['laugh'] = lg
    h = head(rk)
    cam(S, plus(h, (1.6, -4.0, -0.2)), plus(h, (-0.6, 0.3, -0.35)), 32)
    orbit(S, k, -20, 0.22, 0.0)


def signoff(S, k, t, lt):
    """Rook alone by the empty scale: he lifts a small brass weight off its shelf, turns it so it glints, pockets it and
    tugs his brim. "Case closed." """
    amb(S, 'post')
    rk = S['rook']
    loc = at(POST, -1.1, 0.4, 0)
    pick = sm(k / 0.28)
    show_ = sm((k - 0.3) / 0.2) * (1 - sm((k - 0.7) / 0.15))
    pose = blend(P('stand', aR=(0.9, 0.3, 0.6), lean=0.2, head=(0.4, 0.3)), P('stand', aR=(1.9, 0.0, 0.6, 0.4), head=(-0.15, 0.0)), pick)
    if k > 0.72:
        pose = blend(pose, P('hat'), sm((k - 0.72) / 0.2))
    stand(rk, loc, 0.15, pose)
    S['rface'] = 'low' if k > 0.72 else 'calm'
    S['hat_tip'] = 0.25 + 0.35 * sm((k - 0.8) / 0.15)
    needle(S, 0.0)
    hr = hand(rk, 1)
    S['weight'].location = plus(hr, (0, -0.1, 0.1)) if k < 0.78 else FAR
    S['weight'].rotation_euler = (0.3, 0.2, 2 * t)
    S['glint'].location = plus(hr, (0.3, -0.7, 0.4))
    S['glint'].data.energy = 240 * show_
    h = head(rk)
    cam(S, plus(h, (0.9, -4.8, -0.4)), plus(h, (-0.1, 0.0, -0.45)), 30)
    orbit(S, k, 32, 0.3, 0.0)


SHOTS3D = dict(scale_girl=scale_girl, dial=dial, stamp_on=stamp_on, rook_counter=rook_counter, parents=parents, coat_close=coat_close,
               rook_ticket=rook_ticket, rook_scale=rook_scale, weigh_wide=weigh_wide, limit=limit, train_wide=train_wide, wheels=wheels,
               car_inside=car_inside, rook_sack=rook_sack, baby_bundle=baby_bundle, rook_hatjump=rook_hatjump, carrier_lane=carrier_lane,
               rook_follow=rook_follow, ohio_door=ohio_door, rook_sackcheck=rook_sackcheck, cousin=cousin, car_window=car_window, door=door,
               rook_delivered=rook_delivered, ban_desk=ban_desk, rook_notice=rook_notice, anyway_counter=anyway_counter, rook_laugh=rook_laugh,
               signoff=signoff)
