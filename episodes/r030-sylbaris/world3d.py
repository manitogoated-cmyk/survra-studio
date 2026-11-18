"""Case 030 in 3D - Ludger Sylbaris (also recorded as Louis-Auguste Cyparis), Saint-Pierre, Martinique, 8 May 1902.
He was in the town's prison after a fight; for slipping out overnight to a party and coming back, he was put in
solitary: a stone cell built partly underground, no window, only a narrow grating in the door. Just before eight in
the morning a burning cloud from Mount Pelee swept over the city; around 28,000 people died. Hot air and ash came
in through the grating and burned his back, arms and legs, but he lived. Days later men from outside the city heard
him shouting and dug him out. He was pardoned and toured with a circus as "the man who lived through Doomsday".

Built for this story only: the bay of Saint-Pierre under the mountain (town, cathedral towers, ships, the burning
cloud), the same town as grey ruins, an ash-covered street, the prison yard with the half-buried cell (intact, in
ash and as it stands today), the inside of the cell with its slit of light, and a circus ring with a replica cell.

Everything is a generic low-poly reconstruction: no person's likeness is attempted, no building is copied from a
photograph, and the dead are never shown."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -6000)
BAY = (0.0, 0.0, 0.0)               # the bay, the town and the mountain
YARD = (0.0, 5000.0, 0.0)           # the prison yard and the half-buried cell
CELL = (5000.0, 0.0, 0.0)           # inside the cell
STREET = (0.0, -5000.0, 0.0)        # a street of the town after the cloud
RING = (-5000.0, 0.0, 0.0)          # the circus ring
HOST = {'jail_yard', 'rook_slit', 'wall_sneak', 'rook_tap', 'rook_brace', 'rook_listen', 'rook_hatoff', 'dig_out', 'rook_wall',
        'pardon', 'rook_crowd', 'rook_question', 'signoff'}
CAMFILL = {'*': 140, 'bay_blast': 0, 'cloud_town': 0, 'cloud_rush': 0, 'town_ash': 0, 'jail_yard': 200, 'cell_face': 70, 'rook_slit': 260,
           'led_in': 160, 'wall_sneak': 320, 'back_gate': 160, 'door_shut': 200, 'rook_tap': 120, 'slit_close': 30, 'slit_glow': 40,
           'rook_brace': 90, 'shield': 50, 'sleeve_look': 60, 'rook_listen': 160, 'ruins_street': 120, 'rook_hatoff': 200, 'dark_wait': 40,
           'rescuers': 160, 'shout': 60, 'dig_out': 160, 'rook_wall': 200, 'pardon': 160, 'circus_ring': 120, 'rook_crowd': 220,
           'rook_question': 160, 'signoff': 220}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN, HAIR = '5A3A26', '17131A'
STONE, STONE2, EARTH, ASH = '8C8478', '6E675E', '6A5A40', 'A6A29C'
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    dawn=('F6B088', '4A6AA0', 1.15, 2.6, 'FFD2A8', (0.75, -0.55, 0.32)),
    blast=('E07A3A', '3A2A30', 1.0, 1.6, 'FFB070', (0.6, -0.5, 0.45)),
    ash=('9A9690', '4E4C4A', 0.9, 0.9, 'E8E0D4', (0.4, -0.5, 0.75)),
    night=('243858', '070C1A', 0.7, 0.9, 'A8C4F0', (-0.4, 0.3, 0.85)),
    day=('B8D8F0', '3C78B8', 1.2, 3.4, 'FFF2DC', (0.5, -0.55, 0.7)),
    dusk=('F09A68', '2C3A6A', 1.0, 2.0, 'FFAE78', (-0.85, -0.3, 0.2)),
    dark=('140F0C', '060404', 0.2, 0.0, 'FFFFFF', (0, 0, 1)),
    tent=('2A1810', '0C0806', 0.3, 0.0, 'FFFFFF', (0, 0, 1)))
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


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def box(par, col, x0, x1, y0, y1, z0, z1, **kw):
    return add('cube', col, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), scale=(x1 - x0, y1 - y0, z1 - z0), size=1, parent=par, **kw)


# ---------------------------------------------------------------- the burning cloud
def make_cloud(n, seed):
    """A heap of puffs; the dark ones are ash, a few glow from inside."""
    c = keep(empty(FAR))
    puffs = []
    for i in range(n):
        hot = rnd(i, seed + 3) < 0.22
        col = ('E8692A' if rnd(i, seed + 4) < 0.5 else 'C8481E') if hot else ('5E544E', '726660', '4A4440', '857870')[i % 4]
        o = add('ico_sphere', col, (0, 0, 0), radius=1.0, subdivisions=1, parent=c, rough=1.0, emit=3.5 if hot else 0.0)
        puffs.append((o, rnd(i, seed), rnd(i, seed + 1), rnd(i, seed + 2)))
    return c, puffs


def pose_cloud(cl, a, b, f, t, size=1.0, spread=1.0):
    """The front of the cloud runs from a towards b as f goes 0 to 1; puffs behind the front swell and boil."""
    root, puffs = cl
    root.location = (0, 0, 0)
    a, b = Vector(a), Vector(b)
    d = b - a
    side = Vector((-d.y, d.x, 0)).normalized() if d.length > 0 else Vector((1, 0, 0))
    for o, u, v, w in puffs:
        g = max(0.0, min(1.0, f - u * 0.55))
        p = a + d * g
        p += side * ((v - 0.5) * (6 + 30 * g) * spread) + Vector((0, 0, (w * 0.8 + 0.2) * (4 + 18 * g) * spread))
        p += Vector((0.8 * math.sin(t * 1.3 + u * 20), 0.8 * math.cos(t * 1.1 + v * 20), 0.6 * math.sin(t * 1.7 + w * 20))) * spread
        o.location = p
        r = (2.5 + 9 * g * (0.6 + w)) * size * (1 if f > u * 0.55 else 0.25)
        o.scale = (r, r, r * 0.85)
        o.rotation_euler = (t * 0.3 + u * 6, t * 0.2 + v * 6, w * 6)


# ---------------------------------------------------------------- the bay of Saint-Pierre
def make_bay(S):
    b = empty(BAY)
    add('plane', '2A5878', (0, -400, 0), size=1, scale=(2400, 800, 1), parent=b, rough=0.15)            # the sea
    add('cube', '4E6A3A', (0, 520, -2), scale=(2400, 1000, 4), size=1, parent=b, rough=1.0)              # the land
    add('cube', 'C8B48A', (0, 6, 0.1), scale=(2400, 12, 0.6), size=1, parent=b, rough=1.0)              # the shore
    S['mount'] = []
    for (x, y, r, h, col) in ((0, 330, 260, 210, '4A5640'), (-260, 380, 180, 110, '3E4A36'), (240, 420, 200, 120, '445038'),
                              (-120, 200, 120, 60, '56663E'), (150, 210, 110, 55, '52623C')):
        S['mount'].append(add('cone', col, (x, y, h / 2 - 2), radius1=r, radius2=r * 0.09, depth=h, vertices=11, parent=b, rough=1.0))
    add('cone', '6A6058', (0, 330, 208), radius1=26, radius2=8, depth=16, vertices=11, parent=b, rough=1.0)  # the summit dome
    # the town: rows of houses up from the shore, red roofs, the two towers of the cathedral
    S['walls'], S['roofs'] = [], []
    for i in range(150):
        x = -150 + 300 * rnd(i, 1)
        y = 12 + 70 * rnd(i, 2) ** 1.3
        if abs(x) > 150 - y * 0.4:
            continue
        w_, d_, h_ = 6 + 6 * rnd(i, 3), 6 + 5 * rnd(i, 4), 5 + 7 * rnd(i, 5)
        col = ('E8D8B8', 'D8C098', 'E4CCA8', 'C8B090')[i % 4]
        S['walls'].append(add('cube', col, (x, y, h_ / 2), scale=(w_, d_, h_), size=1, parent=b))
        S['roofs'].append(add('cube', ('A8442E', '94402C', 'B85A36')[i % 3], (x, y, h_ + 0.9), rot=(0, 0, 0), scale=(w_ + 0.6, d_ + 0.6, 1.8), size=1, parent=b))
    for s in (-1, 1):
        S['walls'].append(add('cube', 'ECE2CC', (10 + s * 5, 34, 13), scale=(5, 5, 26), size=1, parent=b))
        S['roofs'].append(add('cone', '5A6A72', (10 + s * 5, 34, 28.5), radius1=3.6, radius2=0, depth=5, vertices=4, parent=b))
    S['walls'].append(add('cube', 'ECE2CC', (10, 44, 8), scale=(14, 18, 16), size=1, parent=b))
    S['roofs'].append(add('cube', 'A8442E', (10, 44, 17), scale=(14.6, 18.6, 2), size=1, parent=b))
    S['wallmats'] = [o.data.materials[0] for o in S['walls']]
    S['wallsz'] = [tuple(o.scale) + (o.location.z,) for o in S['walls']]
    S['ashmat'] = K.mat('7E7A74')
    # ships at anchor
    S['ships'] = []
    for i, (x, y) in enumerate(((-70, -40), (-20, -62), (40, -45), (95, -70), (-120, -80))):
        s_ = empty((x, y, 0), b, (0, 0, 0.3 * rnd(i, 7)))
        add('cube', ('2A2A30', '3A2820', 'E8E2D2')[i % 3], (0, 0, 1.2), scale=(4, 22, 3), size=1, parent=s_)
        add('cube', 'D8D2C2', (0, 4, 3.6), scale=(3, 5, 2), size=1, parent=s_)
        for j in range(2 + i % 2):
            add('cylinder', '5A4636', (0, -6 + 7 * j, 11), radius=0.3, depth=18, vertices=6, parent=s_)
        S['ships'].append(s_)
    # smoke columns over the ruined town
    S['smoke'] = keep(empty(FAR))
    for i in range(10):
        for j in range(4):
            r = 5 + 3 * j
            add('ico_sphere', ('5A5450', '6E6862')[j % 2], (-120 + 26 * i + 6 * rnd(i, 9), 20 + 50 * rnd(i, 8), 8 + 11 * j), radius=r, subdivisions=1, parent=S['smoke'], rough=1.0)
    S['bay'] = b
    S['cloud'] = make_cloud(70, 11)


def town(S, ruin=False):
    for o, m in zip(S['walls'], S['wallmats']):
        o.data.materials[0] = S['ashmat'] if ruin else m
    for o in S['roofs']:
        o.hide_render = ruin
    for i, (o, sz) in enumerate(zip(S['walls'], S['wallsz'])):
        f = (0.35 + 0.4 * rnd(i, 12)) if ruin else 1.0
        o.scale = (sz[0], sz[1], sz[2] * f)
        o.location.z = sz[3] * f
    S['smoke'].location = BAY if ruin else FAR


# ---------------------------------------------------------------- the prison yard and the half-buried cell
def make_yard(S):
    y = empty(YARD)
    # ground with a pit in front of the cell door (the cell front wall is at y = -3.2, its floor 1.6 below the yard)
    for x0, x1, y0, y1 in ((-300, -1.4, -300, 300), (1.4, 300, -300, 300), (-1.4, 1.4, -300, -7.0), (-1.4, 1.4, -3.2, 300)):
        S.setdefault('yground', []).append(box(y, EARTH, x0, x1, y0, y1, -2.0, 0.0, rough=1.0))
    box(y, '4A3E2C', -1.4, 1.4, -7.0, -3.2, -2.0, -1.6, rough=1.0)                                       # pit floor
    for i in range(4):                                                                                  # steps down
        box(y, STONE2, -1.2, 1.2, -7.0 + 0.45 * i, -6.55 + 0.45 * i, -1.6, -1.6 + 0.4 * (4 - i), rough=1.0)
    for s in (-1, 1):                                                                                  # pit walls
        box(y, STONE2, s * 1.4 - 0.15, s * 1.4 + 0.15, -7.0, -3.2, -1.6, 0.15, rough=1.0)
    # the cell block: stone, its roof just above the yard, earth banked against it
    box(y, STONE, -3.0, 3.0, -3.2, 3.8, -1.6, 1.9)
    box(y, '76706A', -3.3, 3.3, -3.5, 4.1, 1.9, 2.3)
    for i in range(6):
        for j in range(3):
            add('cube', STONE2, (-2.4 + 0.96 * i + 0.3 * (j % 2), -3.22, -1.1 + 1.0 * j), scale=(0.9, 0.04, 0.05), size=1, parent=y)
    for s in (-1, 1):
        add('cube', EARTH, (s * 4.6, 0.3, 0.2), rot=(0, s * 0.45, 0), scale=(3.2, 7.6, 2.4), size=1, parent=y, rough=1.0)
    add('cube', EARTH, (0, 5.4, 0.2), rot=(-0.45, 0, 0), scale=(7.6, 3.2, 2.4), size=1, parent=y, rough=1.0)
    # the door: wood and iron, hinged on the left, a narrow grated slit at eye height
    S['door'] = d = empty(at(YARD, -0.8, -3.24, -1.6))
    box(d, '4A3220', 0.0, 1.6, -0.08, 0.08, 0.0, 1.95)
    box(d, '4A3220', 0.0, 0.35, -0.08, 0.08, 1.95, 2.35)
    box(d, '4A3220', 1.25, 1.6, -0.08, 0.08, 1.95, 2.35)
    box(d, '4A3220', 0.0, 1.6, -0.08, 0.08, 2.35, 2.6)
    for j in range(3):
        box(d, '2A2A2E', 0.42 + 0.27 * j, 0.47 + 0.27 * j, -0.1, 0.1, 1.95, 2.35, rough=0.4)
        box(d, '2A2A2E', 0.0, 1.6, -0.11, -0.08, 0.3 + 0.7 * j, 0.42 + 0.7 * j, rough=0.4)
    S['slitglow'] = add('plane', 'FFFFFF', at(YARD, 0.0, -3.0, 0.55), rot=(PI / 2, 0, 0), size=1, scale=(0.9, 0.4, 1), emit=0.0)
    box(y, '120C08', -0.82, 0.82, -3.2, -3.0, -1.6, 1.0)                                                 # the dark doorway behind it
    # the prison: high walls, a gate, a building with a tiled roof; and the mountain beyond
    S['yintact'] = yi = keep(empty(YARD))
    S['yruin'] = yr = keep(empty(FAR))
    for par, ruin in ((yi, False), (yr, True)):
        col = ASH if ruin else 'C8B898'
        for i in range(9):
            h_ = (1.5 + 2.8 * rnd(i, 3)) if ruin else 6.0
            add('cube', col, (-24 + 6 * i, 22, h_ / 2), scale=(6.05, 1.0, h_), size=1, parent=par)
        for s in (-1, 1):
            for i in range(6):
                h_ = (1.2 + 3.0 * rnd(i, 4 + s)) if ruin else 6.0
                add('cube', col, (s * 24, -14 + 6 * i, h_ / 2), scale=(1.0, 6.05, h_), size=1, parent=par)
        add('cube', col, (-13, 10, 2.5 if ruin else 4), scale=(12, 7, 5 if ruin else 8), size=1, parent=par)
        if not ruin:
            add('cube', 'A8442E', (-13, 10, 8.6), scale=(12.8, 7.8, 1.4), size=1, parent=par)
            for i in range(4):
                add('cube', '2A2018', (-17.5 + 3 * i, 6.45, 4.5), scale=(1.0, 0.1, 1.6), size=1, parent=par)
        else:
            for i in range(14):
                add('cube', ('8A8680', '6E6A64', 'B4B0A8')[i % 3], (-20 + 40 * rnd(i, 20), -10 + 30 * rnd(i, 21), 0.3), rot=(rnd(i, 22), rnd(i, 23), rnd(i, 24)),
                    scale=(1 + 2 * rnd(i, 25), 0.8 + rnd(i, 26), 0.6), size=1, parent=par, rough=1.0)
            add('cube', ASH, (0, 0, 0.04), scale=(46, 70, 0.08), size=1, parent=par, rough=1.0)
            add('cube', 'B8B4AE', (0, 0.3, 2.34), scale=(6.6, 7.6, 0.12), size=1, parent=par, rough=1.0)  # ash on the cell roof
    add('cube', '3A2A1C', (4, -14.5, 3), scale=(5, 0.6, 6), size=1, parent=yi)                         # the gate in the wall
    S['gate'] = gt = empty(at(YARD, 1.5, -14.6, 0), yi)
    box(gt, '4A3220', 0, 5, -0.15, 0.15, 0, 6)
    S['ygreen'] = keep(empty(FAR))                                                                     # today: grass and a hedge over the old ruins
    add('cube', '5E8A3E', (0, 0, 0.05), scale=(46, 70, 0.1), size=1, parent=S['ygreen'], rough=1.0)
    for i in range(30):
        add('ico_sphere', ('3E6A2E', '4E7A36')[i % 2], (-22 + 44 * rnd(i, 30), 18 + 4 * rnd(i, 31), 1), radius=1.6 + rnd(i, 32), subdivisions=1, parent=S['ygreen'], rough=1.0)
    add('cone', '4A5640', (-40, 260, 70), radius1=190, radius2=18, depth=150, vertices=11, parent=y, rough=1.0)
    S['jcloud'] = make_cloud(40, 41)
    S['lantern'] = keep(light(FAR, 0, 'FFB060', size=0.4))
    S['yard'] = y


def yard(S, state='intact'):
    S['yintact'].location = YARD if state == 'intact' else FAR
    S['yruin'].location = YARD if state in ('ruin', 'today') else FAR
    S['ygreen'].location = at(YARD, 0, 0, 0.04) if state == 'today' else FAR
    for o in S['yground']:
        o.data.materials[0] = K.mat(ASH if state == 'ruin' else '5E8A3E' if state == 'today' else EARTH, 1.0)


def door(S, a):
    S['door'].rotation_euler = (0, 0, -a * 1.9)


# ---------------------------------------------------------------- inside the cell
def make_cell(S):
    c = empty(CELL)
    box(c, '3E3630', -2.6, 2.6, -3.0, 3.4, -0.2, 0.0, rough=1.0)                                       # floor
    for s in (-1, 1):
        box(c, STONE, s * 2.4, s * 2.8, -3.0, 3.4, 0, 3.6)
    box(c, STONE, -2.8, 2.8, 3.2, 3.6, 0, 3.6)
    for i in range(7):                                                                                  # a low barrel vault
        a = PI * i / 6
        add('cube', STONE2, (2.4 * math.cos(a), 0.2, 3.4 + 0.7 * math.sin(a)), rot=(0, -a + PI / 2, 0), scale=(0.3, 6.4, 1.3), size=1, parent=c)
    # the front wall with the door, the door with its slit (z 1.95 to 2.35)
    box(c, STONE, -2.8, -0.8, -3.2, -2.8, 0, 3.6)
    box(c, STONE, 0.8, 2.8, -3.2, -2.8, 0, 3.6)
    box(c, STONE, -0.8, 0.8, -3.2, -2.8, 2.6, 3.6)
    box(c, '4A3220', -0.8, 0.8, -2.98, -2.82, 0.0, 1.95)
    box(c, '4A3220', -0.8, -0.45, -2.98, -2.82, 1.95, 2.35)
    box(c, '4A3220', 0.45, 0.8, -2.98, -2.82, 1.95, 2.35)
    box(c, '4A3220', -0.8, 0.8, -2.98, -2.82, 2.35, 2.6)
    for j in range(3):
        box(c, '1E1E22', -0.38 + 0.27 * j, -0.33 + 0.27 * j, -2.99, -2.81, 1.95, 2.35, rough=0.4)
    for i in range(30):                                                                                 # block joints
        sgn = -1 if i < 15 else 1
        add('cube', '5A544C', (sgn * 2.38, -2.4 + 5.4 * rnd(i, 1), 0.4 + 3.0 * rnd(i, 2)), scale=(0.03, 0.9, 0.05), size=1, parent=c)
    S['outside'] = add('plane', 'FFFFFF', at(CELL, 0, -3.6, 2.15), rot=(PI / 2, 0, 0), size=1, scale=(2.0, 1.2, 1), emit=0.0)
    S['slitl'] = light(at(CELL, 0, -3.9, 2.25), 0, 'FFFFFF', size=0.5)
    S['slitl'].rotation_euler = (-1.25, 0, 0)
    S['celll'] = light(at(CELL, 1.2, 1.5, 3.2), 0, 'FFB880', size=1.5)
    # what is in the cell: a mat, a jug, a stone ledge
    add('cube', 'A88A50', (-1.5, 1.6, 0.05), scale=(1.4, 2.6, 0.1), size=1, parent=c, rough=1.0)
    add('cube', STONE2, (1.7, 1.0, 0.35), scale=(1.2, 3.2, 0.7), size=1, parent=c)
    add('cylinder', '9A5A34', (1.8, 2.6, 0.95), radius=0.18, depth=0.5, vertices=8, parent=c)
    S['ashheap'] = keep(empty(FAR))
    for i in range(9):
        add('ico_sphere', ('8C8780', 'A6A29C')[i % 2], (-0.9 + 1.8 * rnd(i, 5), -2.6 + 1.5 * rnd(i, 6), 0.0), scale=(1, 1, 0.25), radius=0.4 + 0.4 * rnd(i, 7),
            subdivisions=1, parent=S['ashheap'], rough=1.0)
    S['cell'] = c


def cell(S, mode='day', k=0.0, ash=0.0):
    """Light through the slit: day (pale), glow (the cloud), dim, night; the cell has no other window."""
    sky(S, 'dark')
    col, e, w = dict(day=('DCEBFF', 6.0, 900), glow=('FF7A2A', 14.0, 2600), dim=('C8C0B0', 2.5, 300), night=('7A90C0', 1.2, 90),
                     dawn=('FFE0B8', 5.0, 700))[mode]
    S['outside'].data.materials[0] = K.mat(col, 0.9, emit=e)
    S['slitl'].data.energy, S['slitl'].data.color = w, K.hexc(col)[:3]
    S['celll'].data.energy = 40 if mode != 'glow' else 140
    S['celll'].data.color = K.hexc('FFB880' if mode != 'night' else '8090C0')[:3]
    S['ashheap'].location = CELL if ash > 0 else FAR
    S['ashheap'].scale = (1, 1, max(0.01, ash))


# ---------------------------------------------------------------- the street after the cloud
def make_street(S):
    s_ = empty(STREET)
    add('cube', ASH, (0, 60, -0.5), scale=(400, 400, 1.0), size=1, parent=s_, rough=1.0)
    for side in (-1, 1):
        for i in range(10):
            h_ = 1.2 + 4.5 * rnd(i, side + 5)
            add('cube', ('8E8A84', '7A766F', '9C9890')[i % 3], (side * (6 + 0.6 * rnd(i, 2)), -6 + 7 * i, h_ / 2), rot=(0, 0, 0.05 * (rnd(i, 3) - 0.5)),
                scale=(1.0, 6.4, h_), size=1, parent=s_)
            if rnd(i, side + 9) < 0.5:
                add('cube', '2A2420', (side * 5.45, -6 + 7 * i, 1.3), scale=(0.1, 1.4, 2.4), size=1, parent=s_)
    for i in range(12):
        add('cube', ('6E6A64', '9A968E', '4A3A2C')[i % 3], (-4 + 8 * rnd(i, 11), -4 + 60 * rnd(i, 12), 0.25), rot=(rnd(i, 13), rnd(i, 14), rnd(i, 15) * 3),
            scale=(0.6 + 1.6 * rnd(i, 16), 0.5 + 0.8 * rnd(i, 17), 0.4), size=1, parent=s_, rough=1.0)
    bar(s_, '3A2A1C', (-5.5, 18, 3.5), (3.0, 22, 0.1), 0.35)
    for side in (-1, 1):                                                                                # two broken towers at the end of the street
        add('cube', 'B8B2A8', (side * 5, 75, 8), scale=(4.6, 4.6, 16 - 4 * (side > 0)), size=1, parent=s_)
    add('cube', '9C968C', (0, 80, 4), scale=(12, 9, 8), size=1, parent=s_)
    add('cone', '6A6660', (-30, 320, 60), radius1=170, radius2=16, depth=130, vertices=11, parent=s_, rough=1.0)
    S['street'] = s_


# ---------------------------------------------------------------- the circus ring
def make_ring(S):
    r = empty(RING)
    add('cylinder', 'C8A060', (0, 0, 0.02), radius=7, depth=0.04, vertices=24, parent=r, rough=1.0)
    add('torus', 'C8322A', (0, 0, 0.25), major_radius=7.2, minor_radius=0.3, major_segments=24, minor_segments=4, parent=r)
    add('cylinder', '3A2416', (0, 0, -0.05), radius=30, depth=0.1, vertices=24, parent=r, rough=1.0)
    for i in range(20):                                                                                 # tent wall, striped
        a = 2 * PI * i / 20
        add('cube', ('C8322A', 'EFE6CC')[i % 2], (17 * math.cos(a), 17 * math.sin(a), 6), rot=(0, 0, a + PI / 2), scale=(5.5, 0.2, 12), size=1, parent=r)
    add('cone', 'B8302A', (0, 0, 17), radius1=18, radius2=0.5, depth=10, vertices=20, parent=r)
    for s in (-1, 1):
        add('cylinder', 'D8C8A0', (s * 3, 6, 9), radius=0.25, depth=18, vertices=6, parent=r)
    S['crowd'] = []
    for row in range(3):                                                                                # tiers of benches and a quiet crowd
        rad = 10 + 2.2 * row
        add('torus', '4A3020', (0, 0, 0.6 + 1.0 * row), major_radius=rad, minor_radius=0.5, major_segments=28, minor_segments=4, parent=r)
        for i in range(26):
            a = 2 * PI * (i + 0.5 * row) / 26
            if abs(math.sin(a)) < 0.25 and math.cos(a) < 0:
                continue
            col = ('3A3046', '4A3A2C', '2E3A4A', '5A4636', '6A3A30')[(i + row) % 5]
            p = empty((rad * math.cos(a), rad * math.sin(a), 1.1 + 1.0 * row), r, (0, 0, a + PI / 2))
            add('cone', col, (0, 0, 0.55), radius1=0.45, radius2=0.25, depth=1.1, vertices=6, parent=p)
            add('ico_sphere', ('6A4632', 'C89A78', '4A3022', '8A5A3E')[i % 4], (0, 0, 1.35), radius=0.3, subdivisions=1, parent=p)
            S['crowd'].append(p)
    rc = empty((2.6, 1.2, 0), r, (0, 0, -0.5))                                                        # the replica cell
    box(rc, STONE, -1.4, 1.4, -1.4, 1.4, 0, 3.0)
    box(rc, '4A3220', -0.6, 0.6, -1.45, -1.38, 0, 2.3)
    box(rc, '0E0A08', -0.35, 0.35, -1.48, -1.44, 1.75, 1.95)
    S['spotaim'] = empty(at(RING, 0, 0, 1.5))
    S['spot'] = light(at(RING, -2, -6, 15), 0, 'FFF0D0', kind='SPOT', spot=0.35, target=S['spotaim'])
    S['tentl'] = light(at(RING, 0, 0, 13), 0, 'FFB070', size=10)
    S['ring'] = r


# ---------------------------------------------------------------- people
def man_head(head):
    d = K.human_head(SKIN, HAIR)(head)
    add('cube', HAIR, (0, -0.18, -0.2), scale=(0.34, 0.12, 0.1), size=1, parent=head)                   # a short beard
    return d


def guard_head(head):
    d = K.human_head('C8946C', '2A1E18')(head)
    add('cylinder', '232C44', (0, 0.02, 0.33), radius=0.27, depth=0.26, vertices=10, parent=head)        # a kepi
    add('cube', '15182A', (0, -0.27, 0.22), rot=(0.3, 0, 0), scale=(0.36, 0.16, 0.03), size=1, parent=head)
    return d


def hat_head(skin, hair, hat):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('cylinder', hat, (0, 0, 0.25), radius=0.52, depth=0.04, vertices=10, parent=head, rough=1.0)
        add('cylinder', hat, (0, 0, 0.38), radius=0.28, depth=0.26, vertices=10, parent=head, rough=1.0)
        return d
    return fn


def make_things(S):
    S['paper'] = keep(add('cube', 'F2ECD8', FAR, scale=(0.5, 0.04, 0.68), size=1, rough=1.0))
    S['seal'] = keep(add('cylinder', 'B8322A', FAR, rot=(PI / 2, 0, 0), radius=0.09, depth=0.03, vertices=8))
    S['lamp'] = keep(empty(FAR))
    add('cube', '3A3A3E', (0, 0, 0), scale=(0.3, 0.3, 0.42), size=1, parent=S['lamp'], rough=0.4)
    add('cube', 'FFC070', (0, 0, 0), scale=(0.22, 0.32, 0.3), size=1, parent=S['lamp'], emit=8.0)
    S['shovel'] = keep(empty(FAR))
    add('cylinder', '6A4A2C', (0, 0, 0.7), radius=0.04, depth=1.4, vertices=6, parent=S['shovel'])
    add('cube', '5A5A60', (0, 0, -0.05), scale=(0.32, 0.04, 0.4), size=1, parent=S['shovel'], rough=0.4)
    S['fea'] = [keep(add('cone', '2F2B4D', FAR, radius1=0.08, radius2=0, depth=0.5, vertices=4)) for _ in range(2)]
    S['wraps'] = []


def wraps(S, on):
    for o in S['wraps']:
        o.hide_render = not on


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_bay(S)
    make_yard(S)
    make_cell(S)
    make_street(S)
    make_ring(S)
    make_things(S)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['man'] = m = K.Rig(dict(top='D8CDB4', pants='4A4038', hand=SKIN, boot=SKIN, fore='D8CDB4'), man_head)
    for el in m.el:                                                                                     # bandages for after the rescue
        S['wraps'].append(add('cylinder', 'F2EEE4', (0, 0, -0.25), radius=0.1, depth=0.34, vertices=6, parent=el, rough=1.0))
    S['guard'] = K.Rig(dict(top='2E3A5A', pants='2A2A36', hand='C8946C', boot='15151A', fore='2E3A5A'), guard_head)
    S['crew'] = [K.Rig(dict(top=tp, pants=pa, hand=sk, boot='2A2018', fore=sk), hat_head(sk, '17131A', ht))
                 for tp, pa, sk, ht in (('D8D0BC', '5A4A38', '7A4E32', 'D8C08A'), ('8A9A70', '3A3430', 'C8946C', 'B8A070'), ('B8A890', '4A4038', '5A3A26', 'E0CC98'))]
    S['official'] = K.Rig(dict(top='1E1E26', pants='1E1E26', hand='E2B48E', boot='101014', fore='1E1E26'), hat_head('E2B48E', '3A2A1E', '15151A'))
    S['humans'] = [S['man'], S['guard'], S['official']] + S['crew']
    S['cast'] = [S['rook']] + S['humans']
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    S['keyl'] = light((0, 0, 0), 0, 'FFE8D0', size=3.0)
    S['keytgt'] = empty()
    S['keyl'].constraints.new('TRACK_TO').target = S['keytgt']
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 2600
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w30')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.02, 0.6
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
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for l in (S['sun'], S['keyl'], S['slitl'], S['celll'], S['spot'], S['tentl'], S['lantern']):
        l.data.energy = 0
    town(S, False)
    for s_ in S['ships']:
        s_.location.z = 0
    yard(S, 'intact')
    door(S, 0.0)
    S['gate'].rotation_euler = (0, 0, 0)
    S['slitglow'].data.materials[0] = K.mat('0A0806', 0.9)
    wraps(S, False)
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0)
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinking and beak lip sync, once the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.43) % 1 < 0.035
    ez = dict(calm=0.07, low=0.042, shocked=0.135, sad=0.055, soft=0.06).get(e, 0.07)
    tilt = dict(low=-0.06, shocked=0.36, sad=0.45, soft=0.22).get(e, -0.22)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
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


def feather(S, pos, u):
    for i, f in enumerate(S['fea']):
        f.location = (pos[0] + (0.5 + 0.4 * i) * u * (1 if i else -1), pos[1] - 0.3 * u, pos[2] - 1.6 * u * u + 0.5 * u + 0.2 * math.sin(u * 9 + i))
        f.rotation_euler = (u * 5 + i, u * 3, u * 4)


def slit(S, col, e):
    S['slitglow'].data.materials[0] = K.mat(col, 0.9, emit=e)


SUMMIT, TOWN = (0, 330, 215), (10, 30, 10)
PIT = -1.6                                     # the cell's floor, below the yard
CROUCH = dict(lL=(1.25, 1.9), lR=(1.25, 1.9), lift=-0.75, lean=0.55)
HUDDLE = dict(lL=(1.5, 2.2), lR=(1.4, 2.1), aL=(0.9, -0.1, 1.9, 1.1), aR=(0.9, -0.1, 1.9, 1.1), lift=-1.15, lean=0.7, head=(0.6, 0.0))


# ---------------------------------------------------------------- the hook
def bay_blast(S, k, t, lt):
    """Wide, dawn, from out over the bay: the mountain blows a burning cloud that rolls down towards the red roofs. First and last shot."""
    d = lt / k if k > 1e-3 else 1.5
    u = (1 - k) * d if S['prm'].get('loop') else lt
    sky(S, 'dawn', 'blast', sm(u / 1.5) * 0.6)
    pose_cloud(S['cloud'], SUMMIT, (0, 180, 60), 0.25 + 0.5 * sm(u / 1.6), t, 1.4, 1.6)
    key(S, BAY, (0, -60, 80), (0, 60, 20), 0)
    q = sm(u / 1.6)
    shoot(S, BAY, (lerp(30, 24, q), lerp(-200, -185, q), lerp(26, 30, q)), (0, 160, lerp(70, 85, q)), 30)


def cloud_town(S, k, t, lt):
    """Low over the harbour wall: the cloud pours down the slope onto the rooftops, glowing from inside; the cathedral towers in front of it."""
    sky(S, 'blast')
    pose_cloud(S['cloud'], (0, 200, 70), (8, 60, 12), 0.45 + 0.45 * k, t, 1.1, 1.0)
    shoot(S, BAY, (lerp(-24, -20, k), lerp(-36, -30, k), lerp(5, 7, k)), (8, 50, lerp(20, 24, k)), 34)


def jail_yard(S, k, t, lt):
    """The prison yard under a burning sky: a stone cell sunk half into the ground, a slit in its door. Rook lands on its roof and looks at the sky."""
    sky(S, 'blast')
    yard(S, 'intact')
    pose_cloud(S['jcloud'], at(YARD, -40, 260, 150), at(YARD, -10, 70, 40), 0.55 + 0.25 * k, t, 1.4, 1.2)
    u = sm(lt / 0.5)
    put(S, S['rook'], YARD, 0.8, 0.5, 2.3 + 1.5 * (1 - u), facing((0.8, 0.5), (-10, 60)), blend(P('up', head=(-0.2, 0)), P('stand', head=(-0.35, 0.3)), u), 'low')
    S['hat_tip'] = 0.3
    key(S, YARD, (8, -10, 10), (0, 0, 1), 2500, 'FFB080')
    shoot(S, YARD, (lerp(9, 7.5, k), lerp(-16, -14, k), lerp(2.0, 2.6, k)), (0, 0, 1.6), 28)


def cell_face(S, k, t, lt):
    """Inside the cell, close on the prisoner's face in the strip of light from the slit. He lifts his head towards it."""
    pre = S['prm'].get('after')
    cell(S, 'dim' if pre else 'glow', ash=0.6 if pre else 0.0)
    m = put(S, S['man'], CELL, -0.4, -0.6, 0, PI + 0.2, P('sit', head=(lerp(0.3, -0.35, sm(lt / 0.8)), 0.2), aL=(0.5, 0.3, 1.6, 0.8)), 'wide' if not pre else 'tired')
    h = head(S, m)
    shoot(S, (0, 0, 0), (h[0] + lerp(0.8, 0.6, k), h[1] - lerp(1.9, 1.6, k), h[2] + 0.15), (h[0], h[1], h[2] - 0.05), 40)


# ---------------------------------------------------------------- doubt
def rook_slit(S, k, t, lt):
    """In the pit at the cell door: Rook peers through the slit, then turns to us with one line of doubt. Above the wall behind him the cloud glows."""
    sky(S, 'blast')
    yard(S, 'intact')
    slit(S, '1A1410', 0.0)
    pose_cloud(S['jcloud'], at(YARD, -40, 260, 150), at(YARD, -20, 40, 30), 0.75, t, 1.4, 1.2)
    turn = sm((lt - 0.45) / 0.4)
    put(S, S['rook'], YARD, 0.35, -4.0, PIT, lerp(PI, PI - 2.4, turn), P('cross', head=(lerp(0.15, 0.0, turn), 0.0)) if turn > 0.5 else P('stand', aR=(0.6, 0.2, 1.6), head=(0.15, 0.0)), 'low')
    S['hat_tip'] = 0.4 * turn
    h = head(S, S['rook'])
    key(S, YARD, (-3, -9, 2), (0.3, -4, 0.8), 1600, 'FFB080')
    shoot(S, (0, 0, 0), (h[0] - 1.8, h[1] - 3.2, h[2] - 0.6), (h[0] - 0.1, h[1], h[2] - 0.15), 32)


# ---------------------------------------------------------------- how he came to be in the cell
def led_in(S, k, t, lt):
    """Days earlier, a quiet morning: a guard in a kepi walks him across the yard by the arm towards the prison building."""
    sky(S, 'day')
    yard(S, 'intact')
    x = lerp(-4, -9, k)
    m = put(S, S['man'], YARD, x, 2.0, 0, facing((0, 0), (-1, 0.6)), K.walk(t, 1.2), 'hard')
    put(S, S['guard'], YARD, x + 1.0, 1.6, 0, facing((0, 0), (-1, 0.6)), dict(K.walk(t + 0.3, 1.2), aL=(0.9, -0.4, 0.6)), 'hard')
    key(S, YARD, (2, -6, 6), (-6, 2, 1.5), 400)
    shoot(S, YARD, (lerp(2, 0, k), lerp(-6, -5, k), 2.4), (x - 0.5, 1.8, 2.0), 34)


def wall_sneak(S, k, t, lt):
    """Night. He is up on top of the prison wall, one leg over, lantern light from a party beyond. Rook sits on the wall next to him, one brow up."""
    sky(S, 'night')
    yard(S, 'intact')
    u = sm(lt / 1.0)
    put(S, S['man'], YARD, -10, 22.2, lerp(5.2, 5.9, u), PI, P('stand', lL=(1.3, 1.5), lR=(-0.3, 0.6), aL=(2.0, 0.6, 0.4), aR=(0.4, 0.8, 0.6), head=(-0.1, 0.5)), 'warm')
    put(S, S['rook'], YARD, -7.6, 22.2, 4.9, PI - 0.4, P('sit', head=(0.0, -0.6)), 'low')
    S['hat_tip'] = 0.2
    S['lamp'].location = at(YARD, -14, 30, 3.0)
    S['lantern'].location, S['lantern'].data.energy = at(YARD, -14, 28, 4.0), 700
    key(S, YARD, (-6, 12, 9), (-9, 22, 6.5), 900, 'A8C0FF')
    shoot(S, YARD, (lerp(-6, -5.4, k), lerp(14, 15, k), 6.0), (-9, 22, 7.2), 30)


def back_gate(S, k, t, lt):
    """Next morning he is back at the prison gate on his own. The gate swings open; the guard stares at him."""
    sky(S, 'dawn')
    yard(S, 'intact')
    S['gate'].rotation_euler = (0, 0, -1.4 * sm(lt / 0.8))
    put(S, S['man'], YARD, 4.2, -17.0, 0, 0.0, P('shrug', head=(0.0, 0.0)), 'calm')
    put(S, S['guard'], YARD, 3.2, -12.5, 0, PI, P('hips', head=(-0.1, 0.0)), 'wide')
    key(S, YARD, (4, -24, 6), (4, -15, 2), 600, 'FFD2A8')
    shoot(S, YARD, (lerp(9, 8, k), lerp(-9, -10, k), 2.8), (3.8, -15.5, 2.2), 34)


def door_shut(S, k, t, lt):
    """Down in the pit: the guard pushes the heavy door shut on him. Through the closing gap his face, then only the slit."""
    sky(S, 'day')
    yard(S, 'intact')
    door(S, 1.0 - sm(lt / 0.9))
    put(S, S['man'], YARD, 0.0, -2.0, PIT, PI, P('stand', head=(0.1, 0.0)), 'hard')
    put(S, S['guard'], YARD, -1.0, -4.6, PIT, -0.5, P('point', aR=(1.2, 0.4, 0.2)), 'hard')
    key(S, YARD, (2, -9, 3), (0, -3, 0.4), 900)
    shoot(S, YARD, (lerp(1.6, 1.3, k), lerp(-7.6, -7.0, k), 0.6), (0, -3.2, 0.2), 30)


def rook_tap(S, k, t, lt):
    """Inside the cell with him: Rook raps the stone wall with his knuckles, then measures it with his wingspan, then looks at the tiny slit. He sits on the mat."""
    cell(S, 'day')
    put(S, S['man'], CELL, -1.4, 1.8, 0, PI + 0.4, P('sit', head=(0.2, 0.3)), 'tired')
    s = 0.4 * math.sin(lt * 14) * (1 if lt < 0.6 else 0)
    put(S, S['rook'], CELL, 1.6, -0.6, 0, PI / 2 + 0.1, P('tap', aR=(1.4 + s, 0.3, 1.2)) if lt < 0.7 else P('shrug', head=(-0.2, 0.6)), 'low')
    key(S, CELL, (0, -2, 3), (1.6, -0.6, 2), 260, 'FFE0B8')
    shoot(S, CELL, (lerp(-1.8, -1.5, k), lerp(-2.2, -2.5, k), 2.6), (1.4, -0.4, 2.1), 22)


def slit_close(S, k, t, lt):
    """Close on the slit from inside: three bars, a strip of daylight, and dust turning in it."""
    cell(S, 'day')
    shoot(S, CELL, (lerp(0.5, 0.3, k), lerp(-1.0, -1.4, k), 2.0), (0, -2.9, 2.15), 40)


# ---------------------------------------------------------------- the cloud hits
def cloud_rush(S, k, t, lt):
    """High over the bay: the cloud runs down the mountain and over the town and the ships in one rush."""
    sky(S, 'blast')
    pose_cloud(S['cloud'], SUMMIT, (0, -60, 10), 0.35 + 0.7 * k, t, 1.6, 1.8)
    shoot(S, BAY, (lerp(-180, -160, k), lerp(-140, -120, k), lerp(90, 80, k)), (0, 60, 20), 30)


def slit_glow(S, k, t, lt):
    """Inside: the slit goes orange and a blast of hot air and ash pours through it. He is thrown back off the ledge, arms up."""
    cell(S, 'glow', ash=sm(k) * 0.5)
    u = sm(lt / 0.5)
    put(S, S['man'], CELL, lerp(0.2, 1.0, u), lerp(-1.0, 1.0, u), 0, PI + 0.3, blend(P('stand', head=(0.0, 0.0)), P('scream', aL=(2.2, 0.5, 0.8), aR=(2.2, 0.5, 0.8)), u), 'shut')
    S['man'].jawv = 0.6
    shoot(S, CELL, (-1.6, 2.6, 2.6), (0.3, -1.4, 1.9), 26)


def rook_brace(S, k, t, lt):
    """Rook pressed flat against the back wall, holding his hat on with both hands, eyes shut against the glare. No joke now."""
    cell(S, 'glow', ash=0.5)
    put(S, S['rook'], CELL, -1.6, 2.6, 0, PI + 0.15, P('brace', aL=(2.5, 0.3, 1.9), aR=(2.5, 0.3, 1.9), head=(0.3, 0.0)), 'shocked')
    S['hat_tip'] = 0.9
    h = head(S, S['rook'])
    key(S, CELL, (0, -2.5, 2.2), (-1.6, 2.6, 2), 500, 'FF8A3A')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.5, 1.2, k), h[1] - lerp(2.8, 2.4, k), h[2] - 0.4), (h[0], h[1], h[2] - 0.4), 32)


# ---------------------------------------------------------------- re-hook: he burns, but lives
def shield(S, k, t, lt):
    """He is curled in the back corner with his back to the slit, arms over his head, while the orange light and the ash pour in."""
    cell(S, 'glow', ash=0.7)
    put(S, S['man'], CELL, -1.4, 2.5, 0, 0.3, P('stand', **HUDDLE), 'pain')
    key(S, CELL, (0, -2.6, 2.3), (-1.4, 2.5, 1.0), 420, 'FF7A2A')
    shoot(S, CELL, (lerp(0.8, 0.5, k), lerp(0.0, 0.4, k), 1.4), (-1.4, 2.4, 0.9), 30)


def sleeve_look(S, k, t, lt):
    """The glow dies down. He lifts one arm and stares at his shirt sleeve: whole, not even scorched."""
    cell(S, 'dim', ash=0.8)
    m = put(S, S['man'], CELL, -1.0, 2.0, 0, PI + 0.5, P('sit', aR=(1.2, 0.2, 1.7, 0.6), head=(0.35, -0.3)), 'wide')
    h = head(S, m)
    shoot(S, (0, 0, 0), (h[0] + 1.6, h[1] - 1.6, h[2] - 0.2), (h[0] + 0.3, h[1] - 0.2, h[2] - 0.45), 34)


def rook_listen(S, k, t, lt):
    """Rook at the slit from inside, head tilted, listening: no sound from outside, only ash drifting down past the bars."""
    cell(S, 'dim', ash=0.8)
    put(S, S['rook'], CELL, 0.1, -2.2, 0, PI - 0.6, P('stand', head=(0.1, 0.6)), 'sad')
    h = head(S, S['rook'])
    key(S, CELL, (1, 0, 3), h, 160)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.6, 1.3, k), h[1] + lerp(1.4, 1.1, k), h[2] - 0.1), (h[0] - 0.2, h[1] - 0.3, h[2] - 0.2), 32)


def town_ash(S, k, t, lt):
    """The same bay as at dawn, now grey: roofless walls, smoke rising, the ships gone. Nothing moves but the smoke."""
    sky(S, 'ash')
    town(S, True)
    for s_ in S['ships']:
        s_.location.z = -40
    S['smoke'].location = at(BAY, 0.6 * math.sin(t * 0.4), 0, 2.0 * lt)
    shoot(S, BAY, (lerp(-60, -52, k), lerp(-120, -110, k), lerp(30, 28, k)), (10, 40, 10), 32)


# ---------------------------------------------------------------- the city
def ruins_street(S, k, t, lt):
    """Down in a street of the town: broken walls in deep ash, a fallen beam, two broken towers at the end. Empty."""
    sky(S, 'ash')
    shoot(S, STREET, (lerp(1.5, 0.8, k), lerp(-12, -8, k), 2.4), (0, 40, 5), 30)


def rook_hatoff(S, k, t, lt):
    """Rook alone in the ash-covered street, hat held to his chest, head bowed."""
    sky(S, 'ash')
    put(S, S['rook'], STREET, 0.5, 10, 0, PI + 0.2, P('stand', aL=(0.6, -0.2, 2.0, 1.0), head=(lerp(0.2, 0.5, sm(k * 1.5)), 0.0)), 'sad')
    S['hat_off'] = 1.0
    key(S, STREET, (3, 4, 5), (0.5, 10, 2), 600, 'E8E0D4')
    shoot(S, STREET, (lerp(3.4, 3.0, k), lerp(4.0, 4.8, k), 2.1), (0.5, 10, 2.1), 34)


# ---------------------------------------------------------------- waiting, found
def dark_wait(S, k, t, lt):
    """He sits against the wall in the near-dark, burned arms across his knees, as the light in the slit goes from day to night and back."""
    ph = k * 2
    cell(S, ('dim', 'night', 'dawn')[min(2, int(ph * 1.5))], ash=0.8)
    put(S, S['man'], CELL, -1.6, 1.8, 0, PI + 0.6, P('sit', head=(0.5 + 0.1 * math.sin(lt), 0.2)), 'tired')
    shoot(S, CELL, (lerp(1.2, 0.9, k), lerp(-1.6, -1.2, k), 2.6), (-1.5, 1.7, 1.2), 28)


def rescuers(S, k, t, lt):
    """Grey daylight in the ruined prison yard: three men in hats pick their way through the ash, one with a shovel. One stops and turns his head."""
    sky(S, 'ash')
    yard(S, 'ruin')
    for i, c in enumerate(S['crew']):
        x, y = lerp(-12 + 2.2 * i, -6 + 2.2 * i, k), lerp(-12, -8, k) - 1.4 * i
        put(S, c, YARD, x, y, 0.05, facing((x, y), (0, -4)), K.walk(t + 0.4 * i, 1.0) if not (i == 0 and lt > 0.8) else P('stand', head=(0.0, 0.7)), 'hard')
    S['shovel'].location = wpos(S['crew'][1].hands[1])
    key(S, YARD, (-4, -20, 8), (-8, -10, 2), 600, 'E8E0D4')
    shoot(S, YARD, (lerp(4, 3, k), lerp(-18, -17, k), 2.4), (-7, -9, 1.8), 32)


def shout(S, k, t, lt):
    """Inside, close: he is up at the slit with both hands on the door, shouting through the bars."""
    cell(S, 'dawn', ash=0.8)
    m = put(S, S['man'], CELL, 0.0, -2.2, 0, PI + 0.15, P('stand', aL=(1.9, 0.2, 0.8), aR=(1.9, 0.2, 0.8), head=(-0.15, 0.0)), 'wide')
    m.jawv = 0.6 + 0.4 * math.sin(lt * 10)
    wraps(S, False)
    h = head(S, m)
    shoot(S, (0, 0, 0), (h[0] + 1.3, h[1] + 1.4, h[2] + 0.1), (h[0] - 0.1, h[1] - 0.3, h[2] - 0.05), 34)


def dig_out(S, k, t, lt):
    """In the pit: the men drag the door open through the ash and light falls in on him. Two of them lift him out by the arms. Rook watches from the edge."""
    sky(S, 'ash')
    yard(S, 'ruin')
    door(S, sm(lt / 1.0))
    slit(S, '0A0806', 0)
    up = sm((lt - 0.8) / 1.0)
    put(S, S['man'], YARD, 0.0, lerp(-2.4, -4.0, up), PIT, PI, P('stand', aL=(0.6, 0.6, 0.3), aR=(0.6, 0.6, 0.3), head=(0.3, 0.0), lean=0.2), 'tired')
    wraps(S, False)
    put(S, S['crew'][0], YARD, -0.9, -4.8, PIT, -0.3, P('reach', aR=(1.6, 0.3, 0.3)), 'hard')
    put(S, S['crew'][2], YARD, 0.9, -4.8, PIT, 0.3, P('reach', aR=(1.6, -0.3, 0.3)), 'wide')
    put(S, S['rook'], YARD, 2.2, -6.0, 0, 2.6, P('hat', head=(0.4, 0.0)), 'soft')
    key(S, YARD, (0, -8, 3), (0, -3.2, 0), 900, 'E8E0D4')
    shoot(S, YARD, (lerp(-2.6, -2.2, k), lerp(-9.5, -8.8, k), 1.6), (0.3, -4.0, 0.0), 26)


# ---------------------------------------------------------------- the payoff
def rook_wall(S, k, t, lt):
    """Rook lays a wing flat on the cell's thick stone wall, looks at it, then back at us: the punishment was the shelter."""
    sky(S, 'ash')
    yard(S, 'ruin')
    u = sm((lt - 0.5) / 0.4)
    put(S, S['rook'], YARD, 3.6, -1.0, 0, facing((3.6, -1.0), (3.0, -1.0)) * (1 - u) + u * 0.35, P('stand', aR=(1.5, 0.6, 0.2), head=(0.1, 0.4)) if u < 0.5 else P('point', head=(0.0, 0.0)), 'soft')
    h = head(S, S['rook'])
    key(S, YARD, (6, -6, 4), h, 900, 'E8E0D4')
    shoot(S, (0, 0, 0), (h[0] + 1.0, h[1] - 3.6, h[2] - 0.4), (h[0] - 0.6, h[1], h[2] - 0.5), 30)


def pardon(S, k, t, lt):
    """In the grey yard, a man in a black coat hands him a sealed paper. He looks at it; his arms are bandaged. Rook reads over his shoulder."""
    sky(S, 'ash')
    yard(S, 'ruin')
    m = put(S, S['man'], YARD, -3.0, -6.0, 0.05, 0.6, P('stand', aR=(1.0, 0.1, 1.2), head=(0.35, 0.0)), 'wide')
    wraps(S, True)
    put(S, S['official'], YARD, -4.3, -7.6, 0.05, facing((-4.3, -7.6), (-3, -6)), P('point', aR=(1.0, 0.2, 0.6)), 'calm')
    put(S, S['rook'], YARD, -2.0, -5.2, 0.05, 0.6, P('think', head=(0.4, -0.3)), 'calm')
    hd = wpos(S['man'].hands[1])
    S['paper'].location = (hd[0], hd[1] - 0.2, hd[2] + 0.2)
    S['paper'].rotation_euler = (0.4, 0, 0.6)
    S['seal'].location = (hd[0] + 0.05, hd[1] - 0.25, hd[2] + 0.05)
    key(S, YARD, (-6, -12, 5), (-3, -6, 2), 900, 'F2EADA')
    shoot(S, YARD, (lerp(-0.4, -0.9, k), lerp(-11.5, -11, k), 2.6), (-3.0, -6.4, 2.2), 34)


def circus_ring(S, k, t, lt):
    """Under a striped tent: he stands in the spotlight in the ring beside a stone cell built for the show, the crowd in the dark around him."""
    sky(S, 'tent')
    S['spot'].data.energy, S['tentl'].data.energy = 9000, 260
    S['spotaim'].location = at(RING, 0.8, 0.4, 1.5)
    put(S, S['man'], RING, 0.8, 0.4, 0.04, -0.35, P('stand', aL=(0.3, 0.6, 0.6), head=(-0.05, 0.0)), 'calm')
    for i, p in enumerate(S['crowd']):
        p.rotation_euler.x = 0.06 * math.sin(t * 2 + i)
    shoot(S, RING, (lerp(-3, -2.4, k), lerp(-10.5, -9.5, k), lerp(3.2, 2.9, k)), (1.4, 0.8, 2.0), 30)


def rook_crowd(S, k, t, lt):
    """Rook in the front row of the crowd: his hat leaves his head and a feather comes loose."""
    sky(S, 'tent')
    S['spot'].data.energy, S['tentl'].data.energy = 9000, 260
    u = max(0.0, min(1.0, (lt - 0.25) / 0.55))
    put(S, S['rook'], RING, -10.0 * math.cos(0.3), -10.0 * math.sin(0.3), 0.2, facing((-9.55, -2.96), (0, 0)), blend(P('sit', head=(0.0, 0.0)), P('shrug', lift=-0.4), u * 2), 'shocked' if u > 0.05 else 'calm')
    S['hat_jump'] = 0.55 * math.sin(PI * u)
    h = head(S, S['rook'])
    feather(S, (h[0] + 0.2, h[1] + 0.3, h[2] + 0.2), u)
    key(S, RING, (-5, -1, 4), h, 700, 'FFD8A0')
    shoot(S, (0, 0, 0), (h[0] + 2.6, h[1] - 1.6, h[2] - 0.2), (h[0], h[1], h[2] - 0.3), 36)


# ---------------------------------------------------------------- the end
def rook_question(S, k, t, lt):
    """Today, late sun: the cell still stands, grass where the prison was. Rook sits on its roof and asks us straight out."""
    sky(S, 'dusk')
    yard(S, 'today')
    put(S, S['rook'], YARD, 0.3, -1.6, 2.3, -0.35, P('sit', aR=(0.9, 0.2, 1.2), head=(0.0, 0.0)), 'calm')
    h = head(S, S['rook'])
    key(S, YARD, (2, -8, 5), h, 900, 'FFC890')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.2, 1.0, k), h[1] - lerp(3.4, 3.0, k), h[2] - 0.2), (h[0], h[1], h[2] - 0.3), 40)


def signoff(S, k, t, lt):
    """Wide: the little stone cell in the grass at dusk, the mountain quiet behind it, Rook on its roof tipping his hat."""
    sky(S, 'dusk')
    yard(S, 'today')
    put(S, S['rook'], YARD, 0.3, -1.6, 2.3, -0.35, P('hat', head=(0.1, 0.0)) if lt < 0.7 else P('sit'), 'soft')
    S['hat_tip'] = 0.4
    key(S, YARD, (2, -8, 5), (0.3, -1.6, 4), 900, 'FFC890')
    shoot(S, YARD, (lerp(6, 7, k), lerp(-13, -14, k), lerp(2.2, 2.8, k)), (-1, 2, 4.5), 30)


SHOTS3D = {f.__name__: f for f in (
    bay_blast, cloud_town, jail_yard, cell_face, rook_slit, led_in, wall_sneak, back_gate, door_shut, rook_tap, slit_close,
    cloud_rush, slit_glow, rook_brace, shield, sleeve_look, rook_listen, town_ash, ruins_street, rook_hatoff, dark_wait,
    rescuers, shout, dig_out, rook_wall, pardon, circus_ring, rook_crowd, rook_question, signoff)}
