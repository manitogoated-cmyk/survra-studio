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
        hot = rnd(i, seed + 3) < 0.16
        col = ('C8501E' if rnd(i, seed + 4) < 0.5 else 'A83A16') if hot else ('5E544E', '726660', '4A4440', '857870')[i % 4]
        o = add('ico_sphere', col, (0, 0, 0), radius=1.0, subdivisions=2, parent=c, rough=1.0, emit=1.4 if hot else 0.0)
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
    for i in range(6):
        for j in range(5):
            r = 2.5 + 1.6 * j
            add('ico_sphere', ('A8A29C', 'B8B2AA')[j % 2], (-110 + 44 * i + 6 * rnd(i, 9) + 3 * j, 20 + 50 * rnd(i, 8), 10 + 9 * j), radius=r, subdivisions=1, parent=S['smoke'], rough=1.0)
    S['bay'] = b
    S['cloud'] = make_cloud(110, 11)


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
    for x0, x1, y0, y1 in ((-300, -2.4, -300, 300), (2.4, 300, -300, 300), (-2.4, 2.4, -300, -7.0), (-2.4, 2.4, -3.2, 300)):
        S.setdefault('yground', []).append(box(y, EARTH, x0, x1, y0, y1, -2.0, 0.0, rough=1.0))
    box(y, '4A3E2C', -2.4, 2.4, -7.0, -3.2, -2.0, -1.6, rough=1.0)                                       # pit floor
    for i in range(4):                                                                                  # steps down
        box(y, STONE2, -2.2, 2.2, -7.0 + 0.45 * i, -6.55 + 0.45 * i, -1.6, -1.6 + 0.4 * (4 - i), rough=1.0)
    for s in (-1, 1):                                                                                  # pit walls
        box(y, STONE2, s * 2.4 - 0.15, s * 2.4 + 0.15, -7.0, -3.2, -1.6, 0.15, rough=1.0)
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
    S['slitglow'] = add('plane', 'FFFFFF', at(YARD, 0.0, -3.1, 0.55), rot=(PI / 2, 0, 0), size=1, scale=(0.9, 0.4, 1), emit=0.0)
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
    for x0, x1 in ((-24, 1.5), (6.5, 24)):                                                           # the front wall and its gate
        box(yi, 'C8B898', x0, x1, -15.0, -14.0, 0, 6)
    box(yi, 'C8B898', 1.5, 6.5, -15.0, -14.0, 6, 7)
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
    col, e, w = dict(day=('DCEBFF', 3.5, 900), glow=('FF7A2A', 14.0, 2600), dim=('C8C0B0', 2.5, 300), night=('7A90C0', 1.2, 90),
                     dawn=('FFE0B8', 5.0, 700))[mode]
    S['outside'].data.materials[0] = K.mat(col, 0.9, emit=e)
    fl = (0.65 + 0.35 * math.sin(K._T[0] * 23) * math.sin(K._T[0] * 7.3)) if mode == 'glow' else 1.0
    S['slitl'].data.energy, S['slitl'].data.color = w * fl, K.hexc(col)[:3]
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
    bar(s_, '3A2A1C', (-5.5, 30, 3.5), (3.0, 34, 0.1), 0.35)
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
    pose_cloud(S['cloud'], SUMMIT, (0, 150, 50), 0.5 + 0.45 * sm(u / 1.6), t, 2.6, 5.0)
    key(S, BAY, (0, -60, 80), (0, 60, 20), 0)
    q = sm(u / 1.6)
    shoot(S, BAY, (lerp(30, 24, q), lerp(-200, -185, q), lerp(26, 30, q)), (0, 160, lerp(70, 85, q)), 30)


def cloud_town(S, k, t, lt):
    """Low over the harbour wall: the cloud pours down the slope onto the rooftops, glowing from inside; the cathedral towers in front of it."""
    sky(S, 'blast')
    pose_cloud(S['cloud'], (0, 220, 90), (8, 70, 14), 0.5 + 0.45 * k, t, 2.4, 1.6)
    shoot(S, BAY, (lerp(-24, -20, k), lerp(-36, -30, k), lerp(5, 7, k)), (8, 50, lerp(20, 24, k)), 34)


def jail_yard(S, k, t, lt):
    """The prison yard under a burning sky: a stone cell sunk half into the ground, a slit in its door. Rook lands on its roof and looks at the sky."""
    sky(S, 'blast')
    yard(S, 'intact')
    pose_cloud(S['jcloud'], at(YARD, -40, 260, 150), at(YARD, -10, 70, 40), 0.35 + 0.6 * k, t, 1.4, 1.2)
    u = sm(lt / 0.7)
    put(S, S['rook'], YARD, 0.8 + 2.5 * (1 - u), 0.5, 2.3 + 4.0 * (1 - u), facing((0.8, 0.5), (-10, 60)), blend(P('up', head=(-0.2, 0)), P('stand', head=(-0.35, 0.3)), u), 'low')
    S['hat_tip'] = 0.3
    key(S, YARD, (8, -10, 10), (0, 0, 1), 2500, 'FFB080')
    shoot(S, YARD, (lerp(8.0, 4.6, k), lerp(-11.5, -9.0, k), lerp(0.6, 1.6, k)), (0.3, 0, 3.4), 26)


def cell_face(S, k, t, lt):
    """Inside the cell, close on the prisoner's face in the strip of light from the slit. He lifts his head towards it."""
    pre = S['prm'].get('after')
    cell(S, 'dim' if pre else 'glow', ash=0.6 if pre else 0.0)
    m = put(S, S['man'], CELL, -0.4, -0.2, 0, 0.25, P('sit', head=(lerp(0.3, -0.35, sm(lt / 0.8)), 0.2), aL=(0.5, 0.3, 1.6, 0.8)), 'wide' if not pre else 'tired')
    h = head(S, m)
    shoot(S, (0, 0, 0), (h[0] + lerp(0.7, 0.5, k), h[1] - lerp(1.9, 1.6, k), h[2] + 0.1), (h[0], h[1], h[2] - 0.05), 40)


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
    shoot(S, (0, 0, 0), (h[0] - lerp(1.9, 1.2, k), h[1] - lerp(3.4, 2.4, k), h[2] - lerp(0.7, 0.4, k)), (h[0] - 0.1, h[1], h[2] - 0.15), 32)


# ---------------------------------------------------------------- how he came to be in the cell
def led_in(S, k, t, lt):
    """Days earlier, a quiet morning: a guard in a kepi walks him across the yard by the arm towards the prison building."""
    sky(S, 'day')
    yard(S, 'intact')
    x, y_ = lerp(-8, -10.5, k), lerp(-2, 2, k)
    m = put(S, S['man'], YARD, x, y_, 0, facing((0, 0), (-0.55, 1)), K.walk(t, 1.2), 'hard')
    put(S, S['guard'], YARD, x + 1.0, y_ - 0.4, 0, facing((0, 0), (-0.55, 1)), dict(K.walk(t + 0.3, 1.2), aL=(0.9, -0.4, 0.6)), 'hard')
    key(S, YARD, (-3, -8, 6), (x, y_, 1.5), 600)
    shoot(S, YARD, (lerp(-3.5, -4.5, k), lerp(-9, -6, k), 2.3), (x - 0.3, y_, 2.0), 30)


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
    key(S, YARD, (-6, 12, 9), (-9, 22, 6.5), 2200, 'A8C0FF')
    shoot(S, YARD, (lerp(-6.2, -5.8, k), lerp(16.5, 17.2, k), 5.4), (-8.8, 22, 6.8), 32)


def back_gate(S, k, t, lt):
    """Next morning he is back at the prison gate on his own. The gate swings open; the guard stares at him."""
    sky(S, 'dawn')
    yard(S, 'intact')
    S['gate'].rotation_euler = (0, 0, -1.4 * sm(lt / 0.8))
    put(S, S['man'], YARD, 4.2, -17.0, 0, PI, P('shrug', head=(0.0, 0.0)), 'calm')
    put(S, S['guard'], YARD, 5.6, -12.2, 0, -0.5, P('hips', head=(-0.1, 0.0)), 'wide')
    key(S, YARD, (4, -24, 6), (4, -15, 2), 600, 'FFD2A8')
    shoot(S, YARD, (lerp(9, 8, k), lerp(-9, -10, k), 2.8), (3.8, -15.5, 2.2), 34)


def door_shut(S, k, t, lt):
    """Down in the pit: the guard pushes the heavy door shut on him. Through the closing gap his face, then only the slit."""
    sky(S, 'day')
    yard(S, 'intact')
    door(S, 1.0 - sm(lt / 0.9))
    put(S, S['man'], YARD, 0.1, -3.0, PIT, 0.0, P('stand', head=(0.1, 0.0)), 'hard')
    put(S, S['guard'], YARD, -1.3, -4.4, PIT, PI - 0.4, P('point', aR=(1.2, 0.4, 0.2)), 'hard')
    key(S, YARD, (2, -9, 3), (0, -3, 0.4), 900)
    shoot(S, YARD, (lerp(2.0, 1.7, k), lerp(-8.8, -8.2, k), 0.9), (-0.2, -3.2, 0.2), 30)


def rook_tap(S, k, t, lt):
    """Inside the cell with him: Rook raps the stone wall with his knuckles, then measures it with his wingspan, then looks at the tiny slit. He sits on the mat."""
    cell(S, 'day')
    put(S, S['man'], CELL, -1.4, 1.8, 0, PI + 0.4, P('sit', head=(0.2, 0.3)), 'tired')
    s = 0.4 * math.sin(lt * 14) * (1 if lt < 0.6 else 0)
    put(S, S['rook'], CELL, 1.6, -0.6, 0, PI / 2 + 0.1, P('tap', aR=(1.4 + s, 0.3, 1.2)) if lt < 0.7 else P('shrug', head=(-0.2, 0.6)), 'low')
    key(S, CELL, (0, -2, 3), (1.6, -0.6, 2), 260, 'FFE0B8')
    shoot(S, CELL, (lerp(-2.0, -0.9, k), lerp(-2.5, -1.6, k), lerp(3.0, 2.3, k)), (1.4, -0.4, 2.1), 22)


def slit_close(S, k, t, lt):
    """Close on the slit from inside: three bars, a strip of daylight, and dust turning in it."""
    cell(S, 'day')
    shoot(S, CELL, (lerp(0.9, 0.2, k), lerp(-0.4, -1.6, k), lerp(1.7, 2.1, k)), (0, -2.9, 2.15), 40)


# ---------------------------------------------------------------- the cloud hits
def cloud_rush(S, k, t, lt):
    """High over the bay: the cloud runs down the mountain and over the town and the ships in one rush."""
    sky(S, 'blast')
    pose_cloud(S['cloud'], SUMMIT, (0, -60, 10), 0.45 + 0.6 * k, t, 2.4, 4.6)
    shoot(S, BAY, (lerp(-180, -160, k), lerp(-140, -120, k), lerp(90, 80, k)), (0, 60, 20), 30)


def slit_glow(S, k, t, lt):
    """Inside: the slit goes orange and a blast of hot air and ash pours through it. He is thrown back off the ledge, arms up."""
    cell(S, 'glow', ash=sm(k) * 0.5)
    u = sm(lt / 0.5)
    put(S, S['man'], CELL, lerp(-0.2, -0.5, u), lerp(-1.2, 0.6, u), 0, 0.3, blend(P('stand', head=(0.0, 0.0)), P('scream', aL=(2.2, 0.5, 0.8), aR=(2.2, 0.5, 0.8)), u), 'shut')
    S['man'].jawv = 0.6
    key(S, CELL, (0, -2.4, 2.2), (-0.4, 0, 1.6), 300, 'FF7A2A')
    shoot(S, CELL, (1.9, 2.9, 2.6), (-0.2, -1.3, 1.7), 20, roll=0.05 * math.sin(t * 31))


def rook_brace(S, k, t, lt):
    """Rook pressed flat against the back wall, holding his hat on with both hands, eyes shut against the glare. No joke now."""
    cell(S, 'glow', ash=0.5)
    put(S, S['rook'], CELL, -1.6, 2.6, 0, 0.15, P('brace', aL=(2.5, 0.3, 1.9), aR=(2.5, 0.3, 1.9), head=(0.3, 0.0)), 'shocked')
    S['hat_tip'] = 0.9
    h = head(S, S['rook'])
    key(S, CELL, (0, -2.5, 2.2), (-1.6, 2.6, 2), 500, 'FF8A3A')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.9, 0.9, k), h[1] - lerp(3.2, 2.2, k), h[2] - 0.4), (h[0], h[1], h[2] - 0.4), 32, roll=0.04 * math.sin(t * 27))


# ---------------------------------------------------------------- re-hook: he burns, but lives
def shield(S, k, t, lt):
    """He is curled in the back corner with his back to the slit, arms over his head, while the orange light and the ash pour in."""
    cell(S, 'glow', ash=0.7)
    put(S, S['man'], CELL, -1.4, 2.5, 0, 0.3, P('stand', **HUDDLE), 'pain')
    key(S, CELL, (0, -2.6, 2.3), (-1.4, 2.5, 1.0), 420, 'FF7A2A')
    shoot(S, CELL, (lerp(1.2, 0.2, k), lerp(-0.6, 0.6, k), lerp(1.8, 1.2, k)), (-1.4, 2.4, 0.9), 30)


def sleeve_look(S, k, t, lt):
    """The glow dies down. He lifts one arm and stares at his shirt sleeve: whole, not even scorched."""
    cell(S, 'dim', ash=0.8)
    m = put(S, S['man'], CELL, -1.0, 2.0, 0, 0.6, P('sit', aR=(1.2, 0.2, 1.7, 0.6), head=(0.35, -0.3)), 'wide')
    h = head(S, m)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.7, 1.1, k), h[1] - lerp(1.7, 1.1, k), h[2] - lerp(0.4, 0.1, k)), (h[0] + 0.3, h[1] - 0.2, h[2] - 0.45), 34)


def rook_listen(S, k, t, lt):
    """Rook at the slit from inside, head tilted, listening: no sound from outside, only ash drifting down past the bars."""
    cell(S, 'dim', ash=0.8)
    put(S, S['rook'], CELL, 0.1, -2.2, 0, 0.5, P('stand', head=(0.1, -0.5)), 'sad')
    h = head(S, S['rook'])
    key(S, CELL, (1, 0, 3), h, 160)
    shoot(S, (0, 0, 0), (h[0] + lerp(2.4, 1.1, k), h[1] + lerp(2.8, 1.8, k), h[2] + lerp(0.5, 0.0, k)), (h[0] - 0.3, h[1] - 0.6, h[2] - 0.2), 30)


def town_ash(S, k, t, lt):
    """The same bay as at dawn, now grey: roofless walls, smoke rising, the ships gone. Nothing moves but the smoke."""
    sky(S, 'ash')
    town(S, True)
    for s_ in S['ships']:
        s_.location.z = -40
    S['smoke'].location = at(BAY, 4.0 * lt, 0, 6.0 * lt)
    shoot(S, BAY, (lerp(-52, -20, k), lerp(-62, -34, k), lerp(40, 18, k)), (6, 40, 0), 30, roll=lerp(-0.06, 0.04, k))


# ---------------------------------------------------------------- the city
def ruins_street(S, k, t, lt):
    """Down in a street of the town: broken walls in deep ash, a fallen beam, two broken towers at the end. Empty."""
    sky(S, 'ash')
    shoot(S, STREET, (lerp(1.5, 0.8, k), lerp(-12, -8, k), 2.4), (0, 40, 5), 30)


def rook_hatoff(S, k, t, lt):
    """Rook alone in the ash-covered street, hat held to his chest, head bowed."""
    sky(S, 'ash')
    put(S, S['rook'], STREET, 0.5, 10, 0, 0.5, P('stand', aL=(0.6, -0.2, 2.0, 1.0), head=(lerp(0.2, 0.5, sm(k * 1.5)), 0.0)), 'sad')
    S['hat_off'] = 1.0
    key(S, STREET, (3, 4, 5), (0.5, 10, 2), 600, 'E8E0D4')
    shoot(S, STREET, (lerp(3.4, 3.0, k), lerp(4.0, 4.8, k), 2.1), (0.5, 10, 2.1), 34)


# ---------------------------------------------------------------- waiting, found
def dark_wait(S, k, t, lt):
    """He sits against the wall in the near-dark, burned arms across his knees, as the light in the slit goes from day to night and back."""
    ph = k * 2
    cell(S, ('dim', 'night', 'dawn')[min(2, int(ph * 1.5))], ash=0.8)
    put(S, S['man'], CELL, -1.4, 1.8, 0, 0.5, P('sit', head=(0.5 + 0.1 * math.sin(lt), 0.2)), 'tired')
    shoot(S, CELL, (lerp(1.2, 0.9, k), lerp(-1.6, -1.2, k), 2.6), (-1.5, 1.7, 1.2), 28)


def rescuers(S, k, t, lt):
    """Grey daylight in the ruined prison yard: three men in hats pick their way through the ash, one with a shovel. One stops and turns his head."""
    sky(S, 'ash')
    yard(S, 'ruin')
    for i, c in enumerate(S['crew']):
        x, y = lerp(-12, -7, k) - 1.2 * i, lerp(-12, -8, k) + 2.4 * i
        put(S, c, YARD, x, y, 0.05, facing((x, y), (0, -4)), K.walk(t + 0.4 * i, 1.0) if not (i == 0 and lt > 0.8) else P('stand', head=(0.0, 0.7)), 'hard')
    S['shovel'].location = wpos(S['crew'][1].hands[1])
    key(S, YARD, (-4, -20, 8), (-8, -10, 2), 600, 'E8E0D4')
    shoot(S, YARD, (lerp(4, 3, k), lerp(-18, -17, k), 2.4), (-7, -9, 1.8), 32)


def shout(S, k, t, lt):
    """Inside, close: he is up at the slit with both hands on the door, shouting through the bars."""
    cell(S, 'dawn', ash=0.8)
    m = put(S, S['man'], CELL, 0.0, -2.3, 0, 0.1, P('stand', aL=(1.4, 0.4, 1.0), aR=(1.4, 0.4, 1.0), head=(-0.15, 0.0)), 'wide')
    m.jawv = 0.6 + 0.4 * math.sin(lt * 10)
    wraps(S, False)
    h = head(S, m)
    shoot(S, (0, 0, 0), (h[0] + 1.7, h[1] + 0.2, h[2] + 0.05), (h[0] - 0.1, h[1] - 0.2, h[2] - 0.05), 32)


def dig_out(S, k, t, lt):
    """In the pit: the men drag the door open through the ash and light falls in on him. Two of them lift him out by the arms. Rook watches from the edge."""
    sky(S, 'ash')
    yard(S, 'ruin')
    door(S, sm(lt / 1.0))
    slit(S, '0A0806', 0)
    up = sm((lt - 0.8) / 1.0)
    put(S, S['man'], YARD, 0.0, lerp(-3.3, -4.6, up), PIT, 0.0, P('stand', aL=(0.6, 0.6, 0.3), aR=(0.6, 0.6, 0.3), head=(0.3, 0.0), lean=0.2), 'tired')
    wraps(S, False)
    put(S, S['crew'][0], YARD, -1.3, -5.0, PIT, PI - 0.4, P('reach', aR=(1.6, 0.3, 0.3)), 'hard')
    put(S, S['crew'][2], YARD, 1.3, -5.0, PIT, PI + 0.4, P('reach', aR=(1.6, -0.3, 0.3)), 'wide')
    put(S, S['rook'], YARD, 0.9, -3.0, 2.3, -0.3, P('hat', head=(0.5, 0.2)), 'soft')
    key(S, YARD, (0, -8, 3), (0, -3.2, 0), 900, 'E8E0D4')
    shoot(S, YARD, (lerp(1.0, 0.8, k), lerp(-8.6, -8.2, k), 0.3), (-0.1, -3.6, 0.7), 22)


# ---------------------------------------------------------------- the payoff
def rook_wall(S, k, t, lt):
    """Rook lays a wing flat on the cell's thick stone wall, looks at it, then back at us: the punishment was the shelter."""
    sky(S, 'ash')
    yard(S, 'ruin')
    u = sm((lt - 0.45) / 0.35)
    put(S, S['rook'], YARD, -1.7 + 0.5 * u, -3.8 - 0.6 * u, PIT, lerp(PI, 0.4, u), P('stand', aL=(1.5, 0.3, 0.2), head=(0.1, 0.0)) if u < 0.5 else P('point', aR=(1.2, -0.6, 0.1), head=(0.0, 0.0)), 'soft')
    h = head(S, S['rook'])
    key(S, YARD, (1, -8, 3), h, 900, 'E8E0D4')
    shoot(S, (0, 0, 0), (h[0] + lerp(2.4, 0.9, k), h[1] - lerp(3.6, 2.6, k), h[2] - lerp(0.6, 0.0, k)), (h[0] - 0.3, h[1] + 0.3, h[2] - 0.4), 30)


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
    S['spot'].data.energy, S['tentl'].data.energy = 40000, 2500
    S['spotaim'].location = at(RING, 0.8, 0.4, 1.5)
    key(S, RING, (-3, -8, 5), (1, 0.5, 2), 1500, 'FFD8A0')
    put(S, S['man'], RING, 0.8, 0.4, 0.04, -0.35, P('stand', aL=(0.3, 0.6, 0.6), head=(-0.05, 0.0)), 'calm')
    for i, p in enumerate(S['crowd']):
        p.rotation_euler.x = 0.06 * math.sin(t * 2 + i)
    shoot(S, RING, (lerp(-1.6, -1.2, k), lerp(-7.0, -6.4, k), lerp(2.6, 2.4, k)), (1.5, 0.8, 2.0), 30)


def rook_crowd(S, k, t, lt):
    """Rook in the front row of the crowd: his hat leaves his head and a feather comes loose."""
    sky(S, 'tent')
    S['spot'].data.energy, S['tentl'].data.energy = 40000, 2500
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


# ================================================================ long-form extension (16:9 full case file)
# The Short's bay, prison yard, cell, ash street and circus ring stay as they were. New for the full case, each built at
# its own origin and shown only in its own shots: the harbour front of Saint-Pierre before the eruption, a narrow lane, a
# river valley with a factory at its mouth, the room where a commission meets, a courtyard party at night and the edge of
# the ruined town. New things in the bay: steam at the summit, a steamer, fire on the ships, a spine of rock in the
# crater, a mound where a geologist works. New figures: townspeople, two commissioners, the governor's wife, a geologist.
# Everything is generic: no building is a model of a real one, nobody's likeness is attempted, no flag, emblem or
# lettering appears anywhere, and nobody who died is shown dying.
QUAY, LANE, VALLEY, HALL, FETE, EDGE = ((3500.0, 3500.0, 0.0), (-3500.0, 3500.0, 0.0), (3500.0, -3500.0, 0.0), (-3500.0, -3500.0, 0.0),
                                        (0.0, 0.0, 3000.0), (0.0, 0.0, -3000.0))
SKIES.update(haze=('D8C8A8', '8A9AA8', 1.1, 2.4, 'FFE8C8', (0.5, -0.5, 0.6)),
             room=('2A2622', '14120F', 0.5, 0.0, 'FFFFFF', (0, 0, 1)),
             fete=('1C2A48', '060A16', 0.6, 0.5, 'A8C0F0', (-0.4, 0.3, 0.85)))
CAMFILL.update(wall_sneak=800, dark_wait=120, bay_calm=0, quay_life=120, quay_close=160, quay_ash=160, summit_steam=220, snake_lane=200, snake_close=120, mud_valley=0,
               mud_after=260, hall_report=260, hall_window=300, road_in=220, gov_arrive=200, party_night=420, rook_room=160, ships_fire=0,
               roddam_away=0, slit_dark=130, cloth_slit=90, edge_house=220, cell_stands=300, ring_tell=200, geologist=260, spine_rise=260,
               bay_today=0)
HOST |= {'quay_life', 'quay_close', 'quay_ash', 'summit_steam', 'snake_lane', 'mud_after', 'hall_window', 'road_in', 'party_night',
         'rook_room', 'cell_stands', 'geologist', 'spine_rise'}
_MESH = {}


def qadd(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """Same result as kit3d.add, but the mesh comes from one prototype per shape instead of an operator call per object:
    this file adds about two thousand pieces and the operator gets slower with every object in the scene."""
    key = (kind,) + tuple(sorted(kw.items()))
    me = _MESH.get(key)
    if me is None:
        getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(**kw)
        o = bpy.context.object
        me = _MESH[key] = o.data
        me.use_fake_user = True
        bpy.data.objects.remove(o)
    o = bpy.data.objects.new(kind, me.copy())
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    o.data.materials.append(K.mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    if parent:
        o.parent = parent
    return o


def qempty(parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    o = bpy.data.objects.new('e', None)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    return o


def qb(par, col, x0, x1, y0, y1, z0, z1, **kw):
    return qadd('cube', col, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), scale=(x1 - x0, y1 - y0, z1 - z0), size=1, parent=par, **kw)


def qc(par, col, loc, r, d, n=8, rot=(0, 0, 0), **kw):
    return qadd('cylinder', col, loc, rot=rot, scale=(r, r, d), radius=1, depth=1, vertices=n, parent=par, **kw)


def qs(par, col, loc, r, sc=(1, 1, 1), sub=1, **kw):
    return qadd('ico_sphere', col, loc, scale=(r * sc[0], r * sc[1], r * sc[2]), radius=1, subdivisions=sub, parent=par, **kw)


def qcone(par, col, loc, r1, r2, d, n=8, rot=(0, 0, 0), **kw):
    return qadd('cone', col, loc, rot=rot, scale=(r1, r1, d), radius1=1, radius2=round(r2 / r1, 3), depth=1, vertices=n, parent=par, **kw)


def qbar(par, col, a, b, w, **kw):
    o = qadd('cylinder', col, radius=0.5, depth=1, vertices=6, parent=par, **kw)
    span(o, a, b, w)
    return o


def make_puffs(n, seed, cols, hot=0.0, hotcols=('C8501E', 'A83A16')):
    c = keep(qempty(None, FAR))
    puffs = []
    for i in range(n):
        h_ = rnd(i, seed + 3) < hot
        o = qs(c, hotcols[i % 2] if h_ else cols[i % len(cols)], (0, 0, 0), 1.0, sub=2 if n < 30 else 1, rough=1.0, emit=1.4 if h_ else 0.0)
        puffs.append((o, rnd(i, seed), rnd(i, seed + 1), rnd(i, seed + 2)))
    return c, puffs


def house_row(r, x0, n, y0, depth, z0, hmin, hmax, seed, front=-1):
    """A row of plastered house fronts with tiled roofs, doors and shutters, facing -y (front=-1) or +x / -x for a lane."""
    for i in range(n):
        w_ = 7.6
        h_ = hmin + (hmax - hmin) * rnd(i, seed)
        x = x0 + 8 * i
        col = ('E8D8B8', 'E0B890', 'D8C8A0', 'C8D0C0', 'E8C8A8', 'D0B898')[(i + seed) % 6]
        qb(r, col, x, x + w_, y0, y0 + depth, z0, z0 + h_)
        qb(r, ('A8442E', '94402C', 'B85A36')[i % 3], x - 0.3, x + w_ + 0.3, y0 - 0.5, y0 + depth + 0.3, z0 + h_, z0 + h_ + 0.9)
        qb(r, '3A2A1E', x + 1.0, x + 2.4, y0 - 0.06, y0 + 0.1, z0, z0 + 2.9)
        for j in range(2):
            sx = x + 3.4 + 2.0 * j
            qb(r, ('4A6A5A', '6A4A3A', '3E5A7A')[(i + j) % 3], sx, sx + 1.1, y0 - 0.08, y0 + 0.1, z0 + 1.1, z0 + 2.9)
            if h_ > 6.5:
                qb(r, ('4A6A5A', '6A4A3A', '3E5A7A')[(i + j + 1) % 3], sx, sx + 1.1, y0 - 0.08, y0 + 0.1, z0 + 4.3, z0 + 6.0)
        if h_ > 6.5 and i % 2 == 0:
            qb(r, '2A2A2E', x + 0.4, x + w_ - 0.4, y0 - 0.7, y0 - 0.62, z0 + 4.9, z0 + 4.98, rough=0.4)
            qb(r, '8A7A68', x + 0.3, x + w_ - 0.3, y0 - 0.75, y0, z0 + 3.95, z0 + 4.1)


# ---------------------------------------------------------------- the harbour front
def make_quay(r, S):
    qb(r, '2A5878', -400, 400, -500, 0, -1.3, -0.9, rough=0.15)
    qb(r, '8A8478', -400, 400, -0.7, 0, -1.3, 0.22)
    qb(r, 'A89C88', -400, 400, 0, 15.2, -1.0, 0.0, rough=1.0)
    for i in range(18):
        qb(r, '8E8472', -60, 60, 0.8 * i + 0.5, 0.8 * i + 0.56, 0.0, 0.015, rough=1.0)
    house_row(r, -66, 17, 15, 9, 0, 6.0, 10.5, 3)
    house_row(r, -70, 18, 27, 9, 3, 8.0, 12.0, 5)
    qcone(r, '4A5640', (-160, 340, 98), 250, 22, 200, 11, rough=1.0)
    qcone(r, '3E4A36', (60, 330, 50), 190, 30, 104, 9, rough=1.0)
    qcone(r, '52623C', (-330, 300, 40), 170, 30, 84, 9, rough=1.0)
    for i, (x, y) in enumerate(((-26, -42), (34, -64), (-80, -90))):
        s_ = qempty(r, (x, y, -0.9), (0, 0, 0.4 * rnd(i, 3) - 0.2))
        qb(s_, ('2A2A30', '3A2820', '4A3A2C')[i], -2, 2, -11, 11, 0, 3)
        qb(s_, 'D8D2C2', -1.5, 1.5, 2, 7, 3, 5)
        for j in range(2 + i % 2):
            qc(s_, '5A4636', (0, -6 + 7 * j, 12), 0.3, 18, 6)
            qb(s_, 'E8E0CC', -3.5, 3.5, -6.1 + 7 * j, -5.9 + 7 * j, 11, 15.5, rough=1.0)
    for i in range(14):
        qc(r, '3A3A40', (-39 + 6 * i, 0.5, 0.35), 0.24, 0.7, 8, rough=0.5)
    for (x, y) in ((-3.9, 4.0), (-4.6, 4.9), (9.5, 3.0), (10.4, 3.6), (-9, 12.8), (15, 13)):
        qc(r, '6A4A2C', (x, y, 0.55), 0.46, 1.1, 10)
        for z in (0.2, 0.9):
            qc(r, '2A2A2E', (x, y, z), 0.48, 0.07, 10, rough=0.4)
    for (x, y, s) in ((1.9, 7.9, 0.9), (0.9, 10.2, 0.9), (12, 11.5, 1.2), (12.9, 12.2, 0.8), (-12, 3.2, 1.0)):
        qb(r, ('8A6A44', '7A5A38')[int(x) % 2], x - s / 2, x + s / 2, y - s / 2, y + s / 2, 0, s)
    # a market stall: poles, a striped awning, a table of fruit
    for sx in (2.2, 6.2):
        for sy in (10.4, 12.8):
            qc(r, '6A4A2C', (sx, sy, 1.5), 0.06, 3.0, 6)
    for i in range(8):
        qadd('cube', ('E8E0CC', 'D84A3A')[i % 2], (2.45 + 0.5 * i, 11.5, 3.05), rot=(0.2, 0, 0), scale=(0.5, 3.0, 0.05), size=1, parent=r, rough=1.0)
    qb(r, '7A5A38', 2.4, 6.0, 10.7, 11.7, 1.0, 1.12)
    for sx in (2.6, 5.8):
        qb(r, '6A4A2C', sx - 0.06, sx + 0.06, 10.8, 11.6, 0, 1.0)
    for i in range(22):
        qs(r, ('E8902A', 'E8D04A', '6AA83A', 'D84A3A')[i % 4], (2.7 + 3.0 * rnd(i, 1), 10.9 + 0.6 * rnd(i, 2), 1.24 + 0.12 * (i % 2)), 0.13, rough=0.6)
    for x in (-14.0, 17.0):
        qc(r, '2A2A2E', (x, 13.6, 2.4), 0.07, 4.8, 6, rough=0.5)
        qb(r, 'FFE0A0', x - 0.18, x + 0.18, 13.42, 13.78, 4.8, 5.3, emit=1.2)
    S['qash'] = qb(r, 'B4B0A8', -60, 60, 0, 15.2, 0.0, 0.035, rough=1.0)
    # a closed carriage and its horse; parked below the set until the governor's shot
    S['carriage'] = c = qempty(r, (0, 0, -400))
    qb(c, '20342A', -0.85, 0.85, -1.2, 1.2, 0.9, 2.5)
    qb(c, '16241C', -0.95, 0.95, -1.3, 1.3, 2.5, 2.62)
    qb(c, '0E0E12', -0.87, -0.84, -0.5, 0.5, 1.6, 2.3)
    qb(c, '3A2A1E', -0.6, 0.6, -2.0, -1.2, 1.5, 1.65)
    for sx in (-1, 1):
        for sy in (-0.9, 0.9):
            qc(c, '2A1E16', (sx * 0.98, sy, 0.7), 0.7, 0.1, 12, rot=(0, PI / 2, 0))
            qc(c, 'C8A050', (sx * 1.02, sy, 0.7), 0.14, 0.1, 8, rot=(0, PI / 2, 0), rough=0.4)
        qbar(c, '3A2A1E', (sx * 0.5, -2.0, 1.2), (sx * 0.5, -4.6, 1.3), 0.07)
    S['horse'] = hs = qempty(c, (0, -3.6, 0))
    qb(hs, '5A3A26', -0.36, 0.36, -1.0, 1.0, 1.2, 2.05)
    S['hlegs'] = [qempty(hs, (sx * 0.24, sy, 1.25)) for sx in (-1, 1) for sy in (-0.8, 0.8)]
    for l in S['hlegs']:
        qc(l, '4A2E1E', (0, 0, -0.6), 0.1, 1.25, 6)
    qadd('cube', '5A3A26', (0, -1.25, 2.3), rot=(0.9, 0, 0), scale=(0.34, 0.5, 1.1), size=1, parent=hs)
    qadd('cube', '5A3A26', (0, -1.85, 2.72), rot=(-0.4, 0, 0), scale=(0.3, 0.8, 0.36), size=1, parent=hs)
    qadd('cube', '2A1A12', (0, -1.1, 2.6), rot=(0.9, 0, 0), scale=(0.1, 0.2, 0.9), size=1, parent=hs)
    qadd('cube', '2A1A12', (0, 1.1, 1.6), rot=(0.4, 0, 0), scale=(0.12, 0.12, 0.9), size=1, parent=hs)
    return dict(lights=[])


# ---------------------------------------------------------------- a lane in the town
def make_lane(r, S):
    qb(r, '9A8E7A', -4, 4, -30, 60, -0.5, 0.0, rough=1.0)
    for i in range(40):
        qb(r, '857A68', -3.4, 3.4, -20 + 1.1 * i, -19.94 + 1.1 * i, 0.0, 0.015, rough=1.0)
    for side in (-1, 1):
        for i in range(12):
            y0 = -26 + 7 * i
            h_ = 7 + 3 * rnd(i, 4 + side)
            col = ('E8D8B8', 'E0B890', 'D8C8A0', 'C8D0C0', 'E8C8A8')[(i + side) % 5]
            qb(r, col, side * 3.4 if side > 0 else -6.4, 6.4 if side > 0 else -3.4, y0, y0 + 6.9, 0, h_)
            qb(r, ('A8442E', '94402C')[i % 2], side * 3.1 if side > 0 else -6.7, 6.7 if side > 0 else -3.1, y0, y0 + 6.9, h_, h_ + 0.8)
            sx = side * 3.36
            if not (side < 0 and i == 3):
                qb(r, '3A2A1E', sx - 0.05, sx + 0.05, y0 + 0.9, y0 + 2.3, 0, 2.9)
            qb(r, ('4A6A5A', '6A4A3A', '3E5A7A')[i % 3], sx - 0.06, sx + 0.06, y0 + 3.6, y0 + 4.8, 1.2, 2.9)
            qb(r, ('4A6A5A', '6A4A3A', '3E5A7A')[(i + 1) % 3], sx - 0.06, sx + 0.06, y0 + 2.0, y0 + 3.2, 4.4, 6.0)
            qb(r, '8A8478', sx - side * 0.5, sx, y0 + 0.8, y0 + 2.4, 0, 0.22)
    # the open doorway of one house on the left (y -5 .. -3.6) and its door, hinged at the far jamb
    qb(r, '140E0A', -3.5, -3.42, -5.1, -3.7, 0, 2.9)
    S['ldoor'] = dr = qempty(r, (-3.36, -3.7, 0))
    qb(dr, '5A3A26', -0.05, 0.05, -1.4, 0, 0.05, 2.9)
    qb(dr, '2A2A2E', -0.08, 0.08, -1.3, -1.2, 1.3, 1.45, rough=0.4)
    qc(r, '6A4A2C', (2.4, 1.5, 0.58), 0.52, 1.16, 10)
    for z in (0.2, 0.95):
        qc(r, '2A2A2E', (2.4, 1.5, z), 0.54, 0.07, 10, rough=0.4)
    qb(r, '8A6A44', 2.1, 3.1, 3.0, 4.0, 0, 0.9)
    qbar(r, '3A3A3E', (-3.4, 6, 6.2), (3.4, 8, 6.0), 0.03)
    for i in range(5):
        qb(r, ('E8E0CC', 'D84A3A', 'E8D04A', '8AA0B8', 'E8E0CC')[i], -2.6 + 1.1 * i, -1.8 + 1.1 * i, 6.5 + 0.3 * i, 6.56 + 0.3 * i, 4.9, 6.1, rough=1.0)
    qcone(r, '4A5640', (0, 420, 90), 240, 22, 190, 11, rough=1.0)
    S['snakes'] = []
    for i in range(3):
        segs = []
        for j in range(16):
            sc = 0.13 * (1.25 if j == 0 else 1.0 - 0.035 * j)
            segs.append(qs(r, ('6A5A2A', '8A7A3A', '4A3E1E')[j % 3] if j else '7A6A32', (0, 0, -5), sc, (1, 1.3, 0.7), rough=0.5))
        S['snakes'].append(segs)
    return dict(lights=[])


def snake(S, i, x, y, hd, t, amp=0.3):
    """Snake i with its head at set-local (x, y), heading hd (same convention as a rig's yaw), body waving behind it."""
    dx, dy = math.sin(hd), -math.cos(hd)
    for j, o in enumerate(S['snakes'][i]):
        s = j * 0.22
        w = amp * math.sin(t * 8 - j * 0.75 + i * 2.1) * min(1.0, 0.25 + j / 4)
        o.location = (x - dx * s - dy * w, y - dy * s + dx * w, 0.1 + (0.12 * max(0, 1 - j / 3) if j < 3 else 0))
        o.rotation_euler = (0, 0, hd + 0.5 * math.cos(t * 8 - j * 0.75 + i * 2.1))


# ---------------------------------------------------------------- the river valley and the factory at its mouth
def make_valley(r, S):
    qb(r, '2A5878', -500, 500, -500, -22, -1.4, -1.0, rough=0.15)
    qb(r, '4E6A3A', -500, 500, -22, 700, -3.0, 0.0, rough=1.0)
    qb(r, 'C8B48A', -500, 500, -26, -20, -1.2, 0.05, rough=1.0)
    for i in range(8):
        for s in (-1, 1):
            h_ = 46 + 14 * i
            qcone(r, ('3E4A36', '445038', '4A5640')[(i + s) % 3], (s * (78 + 12 * rnd(i, s + 2)), 20 + 62 * i, h_ / 2 - 2), 62 + 4 * i, 8, h_, 9, rough=1.0)
    qcone(r, '4A5640', (0, 620, 118), 300, 24, 240, 11, rough=1.0)
    qb(r, '5A7A8A', -5, 5, -22, 520, 0.0, 0.12, rough=0.2)
    S['fact'] = f = qempty(r)
    qb(f, 'D8C8A8', -30, -8, -10, 8, 0, 8)
    qb(f, 'A8442E', -31, -7, -11, 9, 8, 9.2)
    qb(f, 'A8442E', -27, -11, -11, 9, 9.2, 10.4)
    qb(f, 'C8B898', 8, 26, -12, 2, 0, 6)
    qb(f, '94402C', 7, 27, -13, 3, 6, 7)
    for i in range(6):
        qb(f, '2A2018', -28.5 + 3.6 * i, -27 + 3.6 * i, -10.1, -9.9, 2.5, 5.0)
    for i in range(8):
        qc(f, '6A4A2C', (10 + 1.2 * (i % 4), -15 - 1.2 * (i // 4), 0.6), 0.5, 1.2, 8)
    qb(f, '8A6A44', -34, 30, -18.2, -18, 0, 1.3)
    qc(r, 'A8543A', (-2, 14, 13), 1.7, 26, 10)
    qc(r, '5A2E22', (-2, 14, 26.3), 1.9, 1.0, 10)
    for i in range(40):
        qb(r, ('6A9A3A', '5A8A32')[i % 2], 34 + 1.6 * (i % 20), 34.6 + 1.6 * (i % 20), 6 + 26 * (i // 20), 28 + 26 * (i // 20), 0, 1.6 + 0.5 * rnd(i, 3), rough=1.0)
    S['mudbed'] = qb(r, '8A6E4A', -64, 64, -24, 420, 0.0, 1.0, rough=0.6)
    S['mudbed'].location.z = -80
    qs(r, '6E675E', (12, -8, 0.4), 4.4, (1.7, 1.5, 1.95), rough=1.0)
    for i in range(7):
        qs(r, '6E675E', (-40 + 90 * rnd(i, 5), -14 + 8 * rnd(i, 6), 0.2), 0.8 + rnd(i, 7), (1, 1, 0.6), rough=1.0)
    return dict(lights=[])


# ---------------------------------------------------------------- the commission's room
def make_hall(r, S):
    qb(r, '6A4A30', -7, 7, -9, 5, -0.2, 0.0)
    for i in range(14):
        qb(r, '5A3E28', -7 + i, -6.96 + i, -9, 5, 0.0, 0.012)
    W_ = 'D8CDB0'
    qb(r, W_, -7, 0.5, 5, 5.4, 0, 6.5)
    qb(r, W_, 5.0, 7, 5, 5.4, 0, 6.5)
    qb(r, W_, 0.5, 5.0, 5, 5.4, 0, 1.0)
    qb(r, W_, 0.5, 5.0, 5, 5.4, 5.0, 6.5)
    qb(r, W_, -7.4, -7, -9, 5.4, 0, 6.5)
    qb(r, W_, 7, 7.4, -9, 5.4, 0, 6.5)
    qb(r, 'C8BEA0', -7.4, 7.4, -9, 5.4, 6.5, 6.7)
    qb(r, '6A4A30', -7, 7, 4.9, 5.0, 0, 1.0)
    for x in (0.5, 2.75, 5.0):
        qb(r, '4A3220', x - 0.07, x + 0.07, 4.95, 5.1, 1.0, 5.0)
    for z in (1.0, 3.0, 5.0):
        qb(r, '4A3220', 0.5, 5.0, 4.95, 5.1, z - 0.07, z + 0.07)
    qb(r, '4A3220', -5.6, -2.4, 4.9, 5.0, 2.2, 4.6)
    qb(r, 'D8C8A0', -5.4, -2.6, 4.86, 4.92, 2.4, 4.4, rough=1.0)
    # the table, its cloth, chairs, papers, an inkwell and a lamp
    qb(r, '2E5A3E', -3.4, 3.4, 0.6, 2.6, 1.5, 1.62, rough=1.0)
    qb(r, '2E5A3E', -3.4, 3.4, 0.58, 0.64, 0.7, 1.5, rough=1.0)
    for sx in (-3.1, 3.1):
        for sy in (0.9, 2.3):
            qb(r, '3A2A1E', sx - 0.08, sx + 0.08, sy - 0.08, sy + 0.08, 0, 1.5)
    for cx in (-1.7, 1.7):
        qb(r, '4A3220', cx - 0.45, cx + 0.45, 2.9, 3.8, 0.75, 0.85)
        qb(r, '4A3220', cx - 0.45, cx + 0.45, 3.7, 3.8, 0.85, 2.3)
    for i, (x, y) in enumerate(((-1.6, 1.3), (-0.3, 1.5), (1.4, 1.2), (2.3, 1.7))):
        qadd('cube', 'F2ECD8', (x, y, 1.635), rot=(0, 0, 0.5 * rnd(i, 2) - 0.25), scale=(0.5, 0.7, 0.012), size=1, parent=r, rough=1.0)
    qc(r, '1A1A22', (0.6, 2.2, 1.7), 0.09, 0.16, 8, rough=0.3)
    qc(r, 'C8A050', (-2.6, 2.1, 1.75), 0.12, 0.26, 8, rough=0.4)
    qb(r, 'FFD890', -2.68, -2.52, 2.02, 2.18, 1.88, 2.14, emit=3.0)
    # outside the window: roofs below, the mountain, a column of smoke
    for i in range(12):
        qb(r, ('A8442E', '94402C', 'B85A36')[i % 3], -30 + 7 * i, -24 + 7 * i, 14 + 9 * rnd(i, 3), 22 + 9 * rnd(i, 3), -6, -1.0 + 2.0 * rnd(i, 4))
    qcone(r, '4A5640', (22, 700, 55), 320, 22, 150, 11, rough=1.0)
    S['hsmoke'] = [qs(r, ('8A847C', '9A948C', '7A746C')[i % 3], (22, 700, 140), 14 + 5 * i, rough=1.0) for i in range(8)]
    lamp = K.light(at(HALL, -1.0, -3.5, 5.6), 0, 'FFE8C8', size=5.0)
    lamp.rotation_euler = (0.5, 0, 0)
    lamp.parent = r
    lamp.location = (-1.0, -3.5, 5.6)
    return dict(lights=[lamp])


# ---------------------------------------------------------------- a courtyard party at night
def make_fete(r, S):
    qb(r, '5A4632', -16, 16, -14, 12, -0.3, 0.0, rough=1.0)
    qb(r, 'C8A878', -11, 11, 8, 9, 0, 7)
    qb(r, '94402C', -11.4, 11.4, 7.6, 9.4, 7, 7.9)
    qb(r, 'FFC070', -4.8, -3.2, 7.9, 8.02, 0, 2.7, emit=4.0)
    for x in (0.5, 5.0):
        qb(r, 'FFB860', x, x + 1.3, 7.9, 8.02, 1.4, 3.0, emit=2.5)
        for s in (0, 1):
            qb(r, '4A6A5A', x - 0.7 + 2.0 * s, x + 2.0 * s, 7.86, 7.96, 1.4, 3.0)
    qb(r, 'B89868', 11, 12, -12, 9, 0, 4.2)
    qb(r, 'B89868', -12, -11, -12, 9, 0, 4.2)
    for (x, y) in ((-8.5, 4.5), (9.0, 5.5)):
        qc(r, '5A4632', (x, y, 3.2), 0.28, 6.4, 6)
        for i in range(6):
            a = 2 * PI * i / 6
            qadd('cone', ('3E6A2E', '4E7A36')[i % 2], (x + 1.3 * math.cos(a), y + 1.3 * math.sin(a), 6.3), rot=(0.0, 1.15, a), scale=(0.5, 0.5, 3.2),
                 radius1=1, radius2=0.0, depth=1, vertices=4, parent=r, rough=1.0)
    qbar(r, '2A2018', (-11, 6, 5.6), (11, -5, 5.0), 0.03)
    S['lanterns'] = []
    for i in range(10):
        f = (i + 0.5) / 10
        S['lanterns'].append(qb(r, ('FFB040', 'FF7A3A', 'FFD860', 'F05A4A')[i % 4], -11 + 22 * f - 0.2, -11 + 22 * f + 0.2, 6 - 11 * f - 0.2, 6 - 11 * f + 0.2,
                                4.9 - 0.5 * math.sin(PI * f), 5.4 - 0.5 * math.sin(PI * f), emit=6.0))
    qb(r, '7A5A38', 5.2, 8.2, 2.6, 3.8, 1.2, 1.32)
    for sx in (5.4, 8.0):
        qb(r, '6A4A2C', sx - 0.07, sx + 0.07, 2.8, 3.6, 0, 1.2)
    for i in range(5):
        qc(r, ('2E5A3E', '6A3A20')[i % 2], (5.6 + 0.55 * i, 3.2, 1.55), 0.09, 0.46, 8, rough=0.3)
    qc(r, '8A5A34', (-6.0, 3.4, 0.5), 0.5, 1.0, 10)
    qc(r, 'E8D8B0', (-6.0, 3.4, 1.02), 0.5, 0.04, 10, rough=1.0)
    qb(r, '6A4A2C', -7.4, -6.8, 3.6, 4.6, 0, 0.8)
    l1 = K.light(at(FETE, 0, -1, 5.2), 0, 'FFB060', size=6.0)
    l2 = K.light(at(FETE, -4, 6, 3.0), 0, 'FFC070', size=2.0)
    for l, p in ((l1, (0, -1, 5.2)), (l2, (-4, 6, 3.0))):
        l.parent = r
        l.location = p
    return dict(lights=[l1, l2])


# ---------------------------------------------------------------- the edge of the town, after
def make_edge(r, S):
    qb(r, ASH, -300, 300, -300, 400, -1.0, 0.0, rough=1.0)
    qb(r, 'B8B4AC', -2.2, 2.2, -60, 120, 0.0, 0.03, rough=1.0)
    # a low workshop sunk into the bank: thick walls, a broken roof, steps up from its door
    qb(r, '8C8478', -9.5, -3.0, 2.0, 2.6, 0, 1.9)
    qb(r, '8C8478', -9.5, -9.0, 2.0, 8.0, 0, 2.2)
    qb(r, '8C8478', -3.5, -3.0, 2.0, 8.0, 0, 1.4)
    qb(r, '8C8478', -9.5, -3.0, 7.5, 8.0, 0, 2.6)
    qb(r, '140E0A', -6.6, -5.2, 1.96, 2.04, 0, 1.75)
    qadd('cube', '6E675E', (-7.4, 5.6, 2.3), rot=(0.25, -0.2, 0.1), scale=(4.2, 4.6, 0.25), size=1, parent=r, rough=1.0)
    qadd('cube', EARTH, (-6.2, 9.6, 0.9), rot=(-0.4, 0, 0), scale=(9, 4, 2.2), size=1, parent=r, rough=1.0)
    for i in range(3):
        qb(r, STONE2, -6.7, -5.1, 1.2 - 0.45 * i, 1.65 - 0.45 * i, 0, 0.14 * (3 - i))
    for i in range(16):
        h_ = 0.8 + 3.2 * rnd(i, 3)
        x, y = -40 + 80 * rnd(i, 4), -50 + 40 * rnd(i, 5)
        if abs(x) > 5:
            qb(r, ('8E8A84', '7A766F', '9C9890')[i % 3], x, x + 1.0 + 5 * rnd(i, 6), y, y + 0.9, 0, h_)
    for i in range(9):
        x, y = -24 + 48 * rnd(i, 7), 4 + 40 * rnd(i, 8)
        if abs(x + 6) > 5 and abs(x) > 3:
            qbar(r, '1E1A18', (x, y, 0), (x + 0.8 * (rnd(i, 9) - 0.5), y + 0.5, 3 + 3 * rnd(i, 10)), 0.3, rough=1.0)
    for i in range(10):
        qadd('cube', ('6E6A64', '9A968E', '4A3A2C')[i % 3], (-12 + 24 * rnd(i, 11), -8 + 14 * rnd(i, 12), 0.2), rot=(rnd(i, 13), rnd(i, 14), 3 * rnd(i, 15)),
             scale=(0.5 + 1.2 * rnd(i, 16), 0.4 + 0.6 * rnd(i, 17), 0.35), size=1, parent=r, rough=1.0)
    for i in range(5):
        qcone(r, ('7A7A6E', '6E6E64')[i % 2], (-240 + 120 * i, 300 + 30 * rnd(i, 18), 40), 110, 14, 84, 9, rough=1.0)
    for i in range(4):
        for j in range(5):
            qs(r, ('A8A29C', 'B8B2AA')[j % 2], (-60 + 40 * i + 4 * j, 90 + 30 * rnd(i, 19), 8 + 8 * j), 2.5 + 1.5 * j, rough=1.0)
    return dict(lights=[])


MAKERS = dict(quay=(QUAY, make_quay), lane=(LANE, make_lane), valley=(VALLEY, make_valley), hall=(HALL, make_hall), fete=(FETE, make_fete),
              edge=(EDGE, make_edge))


# ---------------------------------------------------------------- new people and things
def wrap_head(skin, wrap):
    def fn(head):
        d = K.human_head(skin, '17131A')(head)
        qs(head, wrap, (0, 0.03, 0.2), 0.34, (1, 1.05, 0.72), rough=1.0)
        qadd('cone', wrap, (0.1, -0.12, 0.42), rot=(0.4, 0.3, 0), scale=(0.1, 0.1, 0.3), radius1=1, radius2=0.0, depth=1, vertices=4, parent=head, rough=1.0)
        return d
    return fn


def beard_head(skin, hair):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        qb(head, hair, -0.17, 0.17, -0.25, -0.13, -0.3, -0.16)
        return d
    return fn


def sun_hat_head(skin, hair, hat):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        qc(head, hat, (0, 0, 0.27), 0.62, 0.04, 12, rough=1.0)
        qs(head, hat, (0, 0, 0.3), 0.32, (1, 1, 0.75), rough=1.0)
        return d
    return fn


def skirt(rig, col):
    qcone(rig.body, col, (0, 0, -0.46), 0.6, 0.31, 1.1, 8, rough=1.0)


def make_extras(S):
    T_ = []
    for tp, pa, sk, hd in (('E8E0C8', '6A5A48', '6A4630', hat_head('6A4630', '17131A', 'D8C08A')),
                           ('8AA0B8', '3A3A44', '8A5A3C', hat_head('8A5A3C', '17131A', '3A3430')),
                           ('B8A888', '4A4038', '5A3A26', K.human_head('5A3A26', '17131A')),
                           ('D84A3A', 'D84A3A', '7A4E32', wrap_head('7A4E32', 'E8C040')),
                           ('3A8A7A', '3A8A7A', '5A3A26', wrap_head('5A3A26', 'E86A3A')),
                           ('E8E0D0', 'E8E0D0', 'E2B48E', sun_hat_head('E2B48E', '6A4A2C', 'F2EEE4'))):
        T_.append(K.Rig(dict(top=tp, pants=pa, hand=sk, boot='2A2018' if pa != tp else sk, fore=tp if pa == tp else sk), hd))
    for i, col in ((3, 'D84A3A'), (4, '3A8A7A'), (5, 'E8E0D0')):
        skirt(T_[i], col)
    qb(T_[2].body, '6A4A30', -0.26, 0.26, -0.36, -0.3, -0.3, 0.75, rough=1.0)                      # the shoemaker's apron
    S['towns'] = T_
    S['gents'] = [K.Rig(dict(top='2A2A34', pants='22222A', hand='D8AC88', boot='101014', fore='2A2A34'), beard_head('D8AC88', 'B8B6B0')),
                  K.Rig(dict(top='3A3028', pants='2A2420', hand='C8946C', boot='101014', fore='3A3028'), beard_head('C8946C', '3A2A1E'))]
    S['geo'] = K.Rig(dict(top='C8BEA0', pants='A89C80', hand='E2B48E', boot='4A3220', fore='C8BEA0'), sun_hat_head('E2B48E', '5A4632', 'E8E0C8'))
    new = T_ + S['gents'] + [S['geo']]
    S['humans'] += new
    S['cast'] += new
    S['coin'] = keep(qc(None, 'FFC233', FAR, 0.075, 0.016, 10, rough=0.3, emit=1.0))
    S['fruit'] = keep(qs(None, 'E8902A', FAR, 0.13, rough=0.6))
    S['cloth'] = keep(qs(None, 'D8CDB4', FAR, 0.2, (1.25, 0.8, 1.0), rough=1.0))
    S['bundles'] = [keep(qs(None, ('D8CDB4', 'B8A070', '8AA0B8', 'D84A3A')[i], FAR, 0.36, (1.2, 1, 0.75), rough=1.0)) for i in range(4)]
    S['steam'] = make_puffs(18, 71, ('F2F0EC', 'E4E0DA', 'D8D4CE'))
    S['mud'] = make_puffs(60, 83, ('5A4630', '6A5238', '4A3A28', '7A6244'))
    S['fires'] = []
    for n in range(2):
        f = keep(qempty(None, FAR))
        fl = [qs(f, ('FF8A2A', 'FFB040', 'E8501E')[i % 3], (0, 0, 0), 1.0, emit=0.8) for i in range(9)]
        sm_ = [qs(f, ('3A3632', '4A4640')[i % 2], (0, 0, 0), 1.0, rough=1.0) for i in range(7)]
        S['fires'].append((f, fl, sm_))
    S['firel'] = keep(K.light(FAR, 0, 'FF8A3A', size=6.0))
    # a steamer: dark hull, pale upperworks, one funnel, ash on her decks
    S['steamer'] = st = keep(qempty(None, FAR))
    qb(st, '2A2A30', -2.6, 2.6, -17, 17, -0.6, 3.4)
    qadd('cone', '2A2A30', (0, -19.5, 1.4), rot=(PI / 2, 0, 0), scale=(2.6, 2.0, 5.0), radius1=1, radius2=0.0, depth=1, vertices=4, parent=st)
    qb(st, 'A6A29C', -2.5, 2.5, -16.8, 16.8, 3.4, 3.5, rough=1.0)
    qb(st, 'C8C2B4', -2.0, 2.0, -5, 5, 3.5, 6.0)
    qb(st, 'B8B2A4', -1.6, 1.6, -4, -1, 6.0, 7.8)
    qc(st, '8A7A50', (0, 2.0, 9.0), 1.1, 6.5, 10)
    qc(st, '1E1E22', (0, 2.0, 12.0), 1.15, 1.0, 10)
    for y in (-12, 12):
        qc(st, '5A4636', (0, y, 9.5), 0.2, 12, 6)
    S['stsmoke'] = [qs(st, ('4A4640', '5A5650', '6A6660')[i % 3], (0, 2 + 2.6 * i, 14 + 2.2 * i), 1.4 + 0.75 * i, rough=1.0) for i in range(8)]
    # the spine of rock that grew in the crater, and what fell from it
    S['spine'] = sp = keep(qempty(None, FAR))
    qcone(sp, '5A4E48', (0, 0, 45), 15, 4.0, 90, 5, rough=1.0)
    qcone(sp, '6A5E56', (6, -4, 30), 9, 2.0, 60, 4, rot=(0.1, 0.12, 0.7), rough=1.0)
    qcone(sp, '4A403C', (-7, 3, 24), 8, 2.0, 48, 4, rot=(-0.08, -0.1, 0.3), rough=1.0)
    S['rocks'] = [keep(qadd('cube', ('5A4E48', '6A5E56', '4A403C')[i % 3], FAR, scale=(2 + 3 * rnd(i, 2), 2 + 2 * rnd(i, 3), 1.5 + 2 * rnd(i, 4)), size=1, rough=1.0))
                  for i in range(12)]
    S['mound'] = keep(qs(None, '8A8A7A', FAR, 1.0, (10, 10, 3.2), sub=2, rough=1.0))
    S['tripod'] = tp = keep(qempty(None, FAR))
    for i in range(3):
        a = 2 * PI * i / 3
        qbar(tp, '6A4A2C', (0.5 * math.cos(a), 0.5 * math.sin(a), 0), (0, 0, 2.0), 0.05)
    qb(tp, '3A2A1E', -0.25, 0.25, -0.3, 0.3, 2.0, 2.45)
    qc(tp, 'C8A050', (0, -0.36, 2.22), 0.1, 0.14, 8, rot=(PI / 2, 0, 0), rough=0.3)
    S['book'] = keep(qadd('cube', 'F2ECD8', FAR, scale=(0.34, 0.03, 0.44), size=1, rough=1.0))


def ground(S, x, y):
    """Height of the bay's mountain slopes at bay-local (x, y): the cones are faceted, so a formula would float or bury feet."""
    best = 0.0
    dg = bpy.context.evaluated_depsgraph_get()
    for o in S['mount']:
        inv = o.matrix_world.inverted()
        hit, loc, _n, _i = o.ray_cast(inv @ Vector((BAY[0] + x, BAY[1] + y, 900.0)), inv.to_3x3() @ Vector((0, 0, -1)), depsgraph=dg)
        if hit:
            best = max(best, (o.matrix_world @ loc).z)
    return best


_build0, _reset0 = build, reset


def build():
    _MESH.clear()
    S = _build0()
    S['sets'] = {}
    for name, (o, fn) in MAKERS.items():
        root = qempty(None, o)
        d = fn(root, S)
        d.update(root=root, all=list(root.children_recursive))
        S['sets'][name] = d
    make_extras(S)
    bpy.context.view_layer.update()
    S['gz'] = {n: ground(S, x, y) for n, (x, y) in dict(rim=RIM, rimcam=RIMCAM, spcam=SPCAM, road0=(104, 101), road1=(98, 92), roadr=(105.1, 97.1)).items()}
    reset(S)
    return S


def reset(S):
    _reset0(S)
    if 'sets' not in S:
        return
    for d in S['sets'].values():
        for o in d['all']:
            o.hide_render = True
        for l in d['lights']:
            l.data.energy = 0
    for o in S['walls']:
        o.hide_render = False
    for s_ in S['ships']:
        s_.rotation_euler.y = 0.0
    S['firel'].data.energy = 0
    S['carriage'].location = (0, 0, -400)
    S['qash'].location.z = -400
    S['mudbed'].location.z = -80
    S['fact'].location.z = 0
    S['ldoor'].rotation_euler = (0, 0, 0)


def use(S, name):
    d = S['sets'][name]
    for o in d['all']:
        o.hide_render = False
    return d


def tput(S, rig, o, x, y, z, yaw, pose, face=None, jaw=0.0):
    put(S, rig, o, x, y, z, yaw, pose, face)
    rig.jawv = jaw
    return rig


def coinflip(S, rig, t, rate=1.0):
    h = wpos(rig.hands[1])
    u = (t * rate) % 1
    S['coin'].location = (h[0], h[1], h[2] + 0.1 + 1.5 * u * (1 - u))
    S['coin'].rotation_euler = (t * 22, 0.4, 0)


def fire(S, n, pos, t, size=1.0):
    f, fl, sm_ = S['fires'][n]
    f.location = pos
    for i, o in enumerate(fl):
        u = (t * (0.9 + 0.3 * rnd(i, 5)) + rnd(i, 6)) % 1
        o.location = (size * 5 * (rnd(i, 7) - 0.5), size * 9 * (rnd(i, 8) - 0.5), size * 5 * u)
        s = size * (1.8 - 1.2 * u)
        o.scale = (s, s, s * 1.5)
    for i, o in enumerate(sm_):
        u = (t * 0.35 + rnd(i, 9)) % 1
        o.location = (size * (4 * (rnd(i, 10) - 0.5) + 6 * u), size * 8 * (rnd(i, 11) - 0.5), size * (5 + 16 * u))
        s = size * (1.5 + 3.5 * u)
        o.scale = (s, s, s)


RIM, RIMCAM, SPCAM = (-25.0, 304.0), (-27.6, 309.2), (-28.4, 300.0)
COINARM = dict(aR=(0.75, 0.1, 1.5, 0.2), aL=(0.35, -0.05, 1.6, 1.2))


# ---------------------------------------------------------------- the town before
def bay_calm(S, k, t, lt):
    """The bay on a clear day, before any of it: red roofs, the two towers, ships riding at anchor, the green mountain. With
    prm dawn it is the morning of the eighth of May: low sun, and a column of steam standing over the summit."""
    dawn = S['prm'].get('dawn')
    sky(S, 'dawn' if dawn else 'day')
    if dawn:
        pose_cloud(S['steam'], (0, 330, 150), (22, 330, 300), 0.9 + 0.1 * k, t, 1.9, 0.6)
    for i, s_ in enumerate(S['ships']):
        s_.rotation_euler.y = 0.035 * math.sin(t * 0.9 + i)
    if dawn:
        shoot(S, BAY, (lerp(96, 80, k), lerp(-126, -112, k), lerp(9, 12, k)), (0, 110, 62), 30)
    else:
        shoot(S, BAY, (lerp(-120, -96, k), lerp(-150, -132, k), lerp(16, 22, k)), (0, 90, 48), 30)


def quay_life(S, k, t, lt):
    """The harbour front on an ordinary morning: house fronts and shutters, a fruit stall, barrels, people walking past, masts
    over the water. Rook leans by the barrels flipping a coin, watching them go by."""
    use(S, 'quay')
    sky(S, 'day')
    T_ = S['towns']
    tput(S, T_[0], QUAY, lerp(-7.5, -1.5, k), 6.6, 0, PI / 2, K.walk(t, 1.0), 'calm')
    tput(S, T_[4], QUAY, lerp(11.0, 4.0, k), 8.4, 0, -PI / 2, K.walk(t + 0.3, 0.9), 'warm')
    w = math.sin(lt * 2.4)
    tput(S, T_[3], QUAY, 4.3, 12.3, 0, 0.1, P('stand', aR=(0.9 + 0.25 * w, 0.1, 0.9), aL=(0.8 - 0.2 * w, 0.1, 1.0), head=(0.3, 0.2 * w)), 'warm')
    tput(S, T_[1], QUAY, 3.3, 9.6, 0, PI + 0.2, P('point', aR=(1.0, 0.1, 0.5), head=(0.2, 0.0)), 'calm')
    rk = put(S, S['rook'], QUAY, -3.3, 3.2, 0, -PI / 2 + 0.45, P('stand', head=(0.05, lerp(-0.7, 0.2, sm(k))), lean=-0.06, **COINARM), 'low')
    S['hat_tip'] = 0.25
    coinflip(S, rk, t)
    key(S, QUAY, (-9, -3, 5), (-3.3, 3.2, 2), 500, 'FFF2DC')
    shoot(S, QUAY, (lerp(-10.5, -9.0, k), lerp(1.2, 1.9, k), 2.3), (4.5, 8.2, 2.7), 30)


def quay_close(S, k, t, lt):
    """At the fruit stall: the seller hands an orange across to a man in a hat. Behind him Rook sits on a crate flipping his
    coin, and his eyes follow the orange instead."""
    use(S, 'quay')
    sky(S, 'day')
    T_ = S['towns']
    u = sm((lt - 0.5) / 0.9)
    sel = tput(S, T_[3], QUAY, 4.0, 12.2, 0, 0.25, blend(P('stand', aR=(0.6, 0.1, 1.2), head=(0.2, 0.0)), P('stand', aR=(1.35, 0.0, 0.25), head=(0.1, 0.1)), u), 'warm',
               0.25 * abs(math.sin(lt * 5)))
    buy = tput(S, T_[1], QUAY, 3.3, 9.7, 0, PI + 0.15, blend(P('stand', head=(0.1, 0.0)), P('stand', aR=(1.25, 0.05, 0.4), head=(0.15, 0.0)), u), 'calm')
    a, b = wpos(sel.hands[1]), wpos(buy.hands[1])
    g = sm((lt - 1.3) / 0.5)
    S['fruit'].location = (lerp(a[0], b[0], g), lerp(a[1], b[1], g), lerp(a[2], b[2], g) + 0.14)
    rk = put(S, S['rook'], QUAY, 1.9, 7.9, 0.9, PI / 2 + 0.1, P('sit', head=(0.1, lerp(0.0, -0.45, u)), lean=0.1, **COINARM), 'calm')
    coinflip(S, rk, t, 0.9)
    key(S, QUAY, (8, 5, 5), (3, 10.5, 2), 500, 'FFF2DC')
    shoot(S, QUAY, (lerp(8.6, 7.8, k), lerp(7.4, 7.9, k), 2.5), (3.0, 10.9, 2.35), 34)


def quay_ash(S, k, t, lt):
    """The same quay under a yellow-grey sky: ash lies on the stones and drifts down. People stop and look up towards the
    mountain; one holds a hand out to catch it. Rook runs a finger along his hat brim and looks at the grey on it."""
    use(S, 'quay')
    sky(S, 'day', 'ash', 0.75)
    S['qash'].location.z = 0.0175
    T_ = S['towns']
    up = sm(lt / 0.8)
    tput(S, T_[0], QUAY, -0.6, 5.6, 0, facing((-0.6, 5.6), (-40, 60)), blend(P('stand'), P('stand', aR=(1.2, 0.3, 0.5, -1.2), head=(-0.45, 0.0)), up), 'wide')
    tput(S, T_[4], QUAY, 1.6, 4.6, 0, facing((1.6, 4.6), (-40, 60)), blend(P('stand'), P('hat', head=(-0.4, 0.0)), up), 'sad')
    tput(S, T_[1], QUAY, lerp(7.0, 4.2, k), 6.9, 0, -PI / 2 + 0.2, K.walk(t, 1.5) if k < 0.7 else P('stand', head=(-0.35, 0.5)), 'hard')
    u = sm((lt - 0.9) / 0.6)
    put(S, S['rook'], QUAY, -3.0, 7.4, 0, facing((-3.0, 7.4), (-6.5, 10.5)), blend(P('hat', head=(0.0, 0.0)), P('stand', aR=(0.95, 0.05, 1.7, 0.5), head=(0.35, -0.25)), u), 'low')
    S['hat_tip'] = 0.15
    key(S, QUAY, (-8, 12, 5), (-2, 7, 2), 600, 'F0E4D0')
    shoot(S, QUAY, (lerp(-6.6, -6.0, k), lerp(10.9, 10.3, k), 2.5), (-0.4, 5.9, 2.5), 30)


def summit_steam(S, k, t, lt):
    """Up at the summit, on the rim: white steam pushes out of the rock and drifts across. Rook stands in it, taps his beak, and
    looks down past us at the town far below."""
    sky(S, 'day')
    z = S['gz']['rim']
    zc = S['gz']['rimcam']
    pose_cloud(S['steam'], (-31, 311, zc + 2.5), (-17, 299, z + 9), 0.6 + 0.35 * k, t, 0.36, 0.16)
    put(S, S['rook'], BAY, RIM[0], RIM[1], z, facing(RIM, RIMCAM) + 0.3, blend(P('stand', head=(-0.1, 0.3)), P('tap', head=(-0.05, -0.2)), sm((lt - 0.6) / 0.5)), 'low')
    S['hat_tip'] = 0.2
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 5, h[1] + 3, h[2] + 4), h, 900, 'FFF2DC')
    shoot(S, (0, 0, 0), (RIMCAM[0] + lerp(-0.8, 0.0, k), RIMCAM[1] + lerp(0.8, 0.0, k), zc + 3.3), (h[0], h[1], h[2] - 0.5), 30)


def snake_lane(S, k, t, lt):
    """A narrow lane: three snakes come down it over the cobbles. A man flattens himself against the wall. Rook goes straight up
    onto a barrel, hat off his head, a feather coming loose."""
    use(S, 'lane')
    sky(S, 'day', 'ash', 0.5)
    for i in range(3):
        snake(S, i, (-1.3, 0.2, 1.5)[i], lerp(10.5, -2.5, k) + (0, 2.2, 4.0)[i], 0.0, t)
    tput(S, S['towns'][0], LANE, -2.75, 1.2, 0, PI / 2, P('scream', lL=(0.5, 0.9), head=(0.3, 0.2)), 'wide', 0.5)
    u = sm(lt / 0.55)
    put(S, S['rook'], LANE, lerp(1.3, 2.4, u), lerp(0.2, 1.5, u), 1.16 * u + 0.9 * math.sin(PI * u) * (u < 1), facing((2.4, 1.5), (0.5, -5.0)),
        blend(P('stand'), P('shrug', lL=(0.8, 1.3), lR=(0.5, 1.0), head=(0.35, 0.3)), u), 'shocked' if lt > 0.1 else 'calm')
    S['hat_jump'] = 0.5 * math.sin(PI * min(1.0, lt / 0.9))
    h = head(S, S['rook'])
    feather(S, (h[0] - 0.2, h[1] - 0.2, h[2] + 0.3), min(1.0, lt / 1.4))
    key(S, LANE, (0, -8, 5), (0, 2, 1), 700, 'F0E4D0')
    shoot(S, LANE, (lerp(0.3, 0.1, k), lerp(-6.2, -5.4, k), lerp(1.25, 1.5, k)), (0.2, 2.6, 1.35), 28)


def snake_close(S, k, t, lt):
    """Low on the cobbles: a snake slides along the foot of a wall and past a doorstep, and the door is pulled shut from inside."""
    use(S, 'lane')
    sky(S, 'day', 'ash', 0.5)
    sy = lerp(-2.4, -5.4, k)
    snake(S, 0, -2.45, sy, 0.0, t, 0.2)
    snake(S, 1, -1.0, lerp(1.5, -2.5, k), 0.15, t, 0.3)
    snake(S, 2, 40, 40, 0, t)
    S['ldoor'].rotation_euler = (0, 0, 1.25 * (1 - sm(lt / 0.7)))
    key(S, LANE, (2, -8, 3), (-2.5, -4, 0.5), 500, 'F0E4D0')
    shoot(S, LANE, (-1.35, sy - 2.3, 0.34), (-2.6, sy + 0.9, 0.3), 34)


def mud_valley(S, k, t, lt):
    """A green river valley running down to the sea, a factory with a tall chimney at its mouth. A brown wall of mud comes down
    the valley floor towards it."""
    use(S, 'valley')
    sky(S, 'day', 'ash', 0.6)
    pose_cloud(S['mud'], at(VALLEY, 0, 300, 30), at(VALLEY, -8, 2, 3), 0.3 + 0.7 * sm(k), t, 1.0, 0.5)
    shoot(S, VALLEY, (lerp(22, 16, k), lerp(-56, -48, k), lerp(15, 12, k)), (-4, 60, 12), 30)


def mud_after(S, k, t, lt):
    """Afterwards: brown mud lies across the valley mouth, and only the chimney and a roof ridge stand out of it. Rook stands on
    a rock at the edge with his hat off."""
    use(S, 'valley')
    sky(S, 'ash', 'day', 0.55)
    S['mudbed'].location.z = 6.2
    S['fact'].location.z = -0.4
    put(S, S['rook'], VALLEY, 12, -8.3, 8.8, facing((12, -8.3), (20, -15)) - 0.6, P('stand', aL=(0.6, -0.2, 2.0, 1.0), head=(lerp(0.15, 0.45, sm(k * 1.4)), 0.55)), 'sad')
    S['hat_off'] = 1.0
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] + 6, h[1] - 5, h[2] + 3), h, 1200, 'E8E0D4')
    shoot(S, VALLEY, (lerp(18.6, 17.8, k), lerp(-14.2, -13.4, k), 11.6), (7.5, -1.0, 10.9), 30)


# ---------------------------------------------------------------- the town stays
def hall_report(S, k, t, lt):
    """A room with a long table: three men in dark coats, papers, a lamp. The one standing holds up a sheet and reads from it;
    the others nod. In the window behind them the mountain is smoking."""
    d = use(S, 'hall')
    sky(S, 'day', 'ash', 0.5)
    d['lights'][0].data.energy = 900
    for i, o in enumerate(S['hsmoke']):
        o.location = (22 + 9 * i + 3 * math.sin(t * 0.5 + i), 700, 138 + 15 * i + 3 * math.sin(t * 0.7 + i))
    g0, g1 = S['gents']
    rd = tput(S, g0, HALL, 0.0, 3.3, 0, 0.0, P('stand', aR=(1.25, 0.25, 1.0, 0.3), aL=(0.4, 0.2, 1.2, 0.6), head=(0.15 + 0.05 * math.sin(lt * 3), 0.0)), 'calm',
              0.35 * abs(math.sin(lt * 6)))
    tput(S, g1, HALL, -1.7, 3.2, 0.36, 0.1, P('sit', head=(0.25 + 0.12 * math.sin(lt * 4), 0.35)), 'calm')
    tput(S, S['official'], HALL, 1.7, 3.2, 0.36, -0.1, P('sit', head=(0.2 + 0.1 * math.sin(lt * 4 + 1), -0.35)), 'calm')
    hd = wpos(rd.hands[1])
    S['paper'].location = (hd[0], hd[1] - 0.12, hd[2] + 0.3)
    S['paper'].rotation_euler = (0.25, 0, 0.1)
    shoot(S, HALL, (lerp(-1.2, -0.7, k), lerp(-3.6, -2.9, k), 2.5), (0.7, 3.2, 2.75), 30)


def hall_window(S, k, t, lt):
    """Rook by the window of the same room, brim low. He looks at the men, then jerks a thumb over his shoulder at the smoke
    standing over the mountain outside."""
    d = use(S, 'hall')
    sky(S, 'day', 'ash', 0.5)
    d['lights'][0].data.energy = 900
    for i, o in enumerate(S['hsmoke']):
        o.location = (22 + 9 * i + 3 * math.sin(t * 0.5 + i), 700, 138 + 15 * i + 3 * math.sin(t * 0.7 + i))
    tput(S, S['gents'][1], HALL, -1.7, 3.2, 0.36, 0.1, P('sit', head=(0.4, 0.3)), 'calm')
    tput(S, S['official'], HALL, 1.7, 3.2, 0.36, -0.1, P('sit', head=(0.45, -0.2)), 'calm')
    u = sm((lt - 0.7) / 0.45)
    put(S, S['rook'], HALL, 3.7, 3.9, 0, 0.45, blend(P('cross', head=(0.1, 0.45)), P('stand', aR=(0.3, 1.5, 2.3, -0.4), aL=(0.5, -0.05, 1.7, 1.3), head=(0.05, 0.0)), u), 'low')
    S['hat_tip'] = 0.4
    key(S, HALL, (0, -2, 4), (3.7, 3.9, 2.5), 500, 'FFE8C8')
    shoot(S, HALL, (lerp(2.0, 2.4, k), lerp(-1.2, -0.5, k), 2.6), (3.6, 4.3, 2.9), 32)


def road_in(S, k, t, lt):
    """The road down into town from the slopes: villagers with bundles on their heads walk in towards the red roofs and the two
    towers. Rook comes up the road the other way, and turns to look back at them."""
    sky(S, 'day', 'ash', 0.45)
    g = S['gz']
    dx, dy = -0.55, -0.83
    for i, rig in enumerate((S['towns'][3], S['towns'][0], S['towns'][4], S['crew'][1])):
        f = 0.2 + 0.6 * k + 0.2 * i
        x, y = 104.5 + dx * 11 * f + 1.4 * (i % 2), 102.5 + dy * 11 * f
        tput(S, rig, BAY, x, y, lerp(g['road0'], g['road1'], f) + 0.02, facing((0, 0), (dx, dy)), dict(K.walk(t + 0.37 * i, 0.9), aL=(2.7, 0.3, 0.5)), 'tired')
        hp_ = wpos(rig.head)
        S['bundles'][i].location = (hp_[0], hp_[1], hp_[2] + 0.62)
    u = sm((lt - 0.8) / 0.6)
    rx, ry = lerp(104.6, 105.6, k), lerp(96.0, 98.2, k)
    put(S, S['rook'], BAY, rx, ry, g['roadr'] + 0.02, facing((0, 0), (0.55, 0.83)) + 0.5 * u, K.walk(t, 1.0) if u < 0.3 else P('cross', head=(0.0, 0.85)), 'low')
    S['hat_tip'] = 0.3
    key(S, BAY, (110, 100, 9), (102, 94, 3), 1200, 'FFF2DC')
    shoot(S, BAY, (lerp(109.5, 108.7, k), lerp(104.6, 103.4, k), g['road0'] + 3.0), (98.5, 87.0, g['road1'] + 3.0), 30)


def gov_arrive(S, k, t, lt):
    """On the quay a closed carriage has pulled up. A man in a black coat and hat hands a lady in a pale dress down from it, and
    a guard salutes. Behind the houses the mountain is smoking."""
    use(S, 'quay')
    sky(S, 'day', 'ash', 0.6)
    S['qash'].location.z = 0.0175
    pose_cloud(S['steam'], at(QUAY, -160, 340, 198), at(QUAY, -150, 340, 330), 0.9, t, 2.4, 1.6)
    S['carriage'].location = (-3.4, 9.2, 0)
    S['carriage'].rotation_euler = (0, 0, -PI / 2)
    for i, l in enumerate(S['hlegs']):
        l.rotation_euler = (0.12 * math.sin(t * 2 + i * 1.7), 0, 0)
    u = sm((lt - 0.3) / 1.0)
    tput(S, S['official'], QUAY, -0.9, 6.5, 0, facing((-0.9, 6.5), (-2.6, 8.0)) + 0.9, P('stand', aL=(1.2, 0.5, 0.4), head=(0.05, -0.5)), 'calm')
    tput(S, S['towns'][5], QUAY, lerp(-3.2, -2.5, u), lerp(8.2, 7.5, u), lerp(0.55, 0.0, u), facing((-3, 8), (1, 4)), P('stand', aR=(1.0, 0.4, 0.5), head=(0.1, 0.2)), 'warm')
    tput(S, S['guard'], QUAY, 0.8, 8.6, 0, -PI / 2 - 0.2, blend(P('stand'), P('hat', aR=(0.3, 1.7, 2.1, -1.3), head=(0.0, 0.0)), sm(lt / 0.5)), 'hard')
    key(S, QUAY, (4, 1, 5), (-2, 7.5, 2), 700, 'F0E4D0')
    shoot(S, QUAY, (lerp(4.6, 3.8, k), lerp(2.6, 3.2, k), 2.2), (-2.2, 8.0, 2.75), 30)


def party_night(S, k, t, lt):
    """Night, a courtyard hung with lanterns: a drummer, couples dancing, and Ludger in the middle of them, laughing. Rook leans
    against the wall with his coin, brim down, watching the gate."""
    d = use(S, 'fete')
    sky(S, 'fete')
    d['lights'][0].data.energy, d['lights'][1].data.energy = 1500, 500
    b = math.sin(t * 6.3)
    b2 = math.cos(t * 6.3)
    dance = lambda s, ph: P('stand', aL=(1.6 + 0.5 * s * b, 0.7, 1.0), aR=(1.6 - 0.5 * s * b, 0.7, 1.0), lL=(0.25 * max(0, b * s), 0.4 * max(0, b * s)),
                            lR=(0.25 * max(0, -b * s), 0.4 * max(0, -b * s)), lift=-0.06 * abs(b2), head=(-0.05, 0.25 * b), lean=0.05 * b2)
    tput(S, S['man'], FETE, 0.3 + 0.3 * b2, 0.4, 0.02 * abs(b), 0.35 + 0.5 * math.sin(t * 1.6), dance(1, 0), 'warm', 0.3 + 0.2 * b)
    tput(S, S['towns'][3], FETE, 1.9 - 0.3 * b2, 1.2, 0, PI * 0.5 + 0.4 * math.sin(t * 1.6 + 1), dance(-1, 1), 'warm')
    tput(S, S['towns'][0], FETE, -2.8, 2.6 + 0.2 * b, 0, 0.6 + 0.3 * b2, dance(1, 2), 'warm')
    tput(S, S['towns'][4], FETE, -1.5, 3.4 - 0.2 * b, 0, -0.9 - 0.3 * b2, dance(-1, 3), 'warm')
    tput(S, S['towns'][2], FETE, -6.9, 4.1, 0.38, -PI / 2 - 0.5, P('sit', aL=(1.0 + 0.35 * b, 0.1, 1.0), aR=(1.0 - 0.35 * b, 0.1, 1.0), head=(0.2, 0.3 * b2)), 'warm')
    rk = put(S, S['rook'], FETE, 5.5, -3.4, 0, 0.3, P('stand', head=(0.08, lerp(0.5, -0.3, sm(k))), lean=-0.07, **COINARM), 'low')
    S['hat_tip'] = 0.45
    coinflip(S, rk, t, 0.9)
    key(S, FETE, (7, -8, 4), (5.5, -3.4, 2.2), 380, 'FFC890')
    shoot(S, FETE, (lerp(6.4, 5.6, k), lerp(-8.6, -8.0, k), 2.5), (1.2, 0.2, 2.5), 30)


def rook_room(S, k, t, lt):
    """In the cell: Ludger on the mat with his back to the wall, Rook on the stone ledge opposite, arms folded, brim down, looking
    round at the walls. Ludger looks across at him."""
    cell(S, 'day')
    tput(S, S['man'], CELL, -1.45, 1.4, 0, -PI / 2 + 0.5, P('sit', head=(0.15, lerp(0.0, -0.4, sm(lt / 1.2)))), 'tired')
    put(S, S['rook'], CELL, 1.75, 1.0, 0.72, PI / 2 - 0.55, P('sit', aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), head=(lerp(-0.25, 0.1, sm((lt - 0.8) / 0.6)), lerp(0.7, -0.1, sm((lt - 0.8) / 0.6))), lean=0.05), 'low')
    S['hat_tip'] = 0.5
    key(S, CELL, (0, -2.2, 3), (1.7, 1.0, 2.2), 240, 'FFE0B8')
    shoot(S, CELL, (lerp(-0.5, -0.1, k), lerp(-2.45, -2.2, k), 1.9), (0.35, 1.3, 1.75), 22)


# ---------------------------------------------------------------- the eighth of May, from the water
def ships_fire(S, k, t, lt):
    """From the water, among the anchored ships: the cloud is over the town and coming out across the harbour. A ship heels over
    with fire along her deck; another burns behind her."""
    sky(S, 'blast')
    pose_cloud(S['cloud'], (0, 170, 70), (24, -66, 14), 0.72 + 0.25 * k, t, 2.2, 3.4)
    S['ships'][2].rotation_euler.y = 0.3 * sm(k) + 0.03 * math.sin(t * 3)
    S['ships'][1].rotation_euler.y = -0.14 * sm(k)
    fire(S, 0, at(BAY, 40, -45, 5), t, 1.0)
    fire(S, 1, at(BAY, -20, -62, 5), t + 3, 0.9)
    S['firel'].location, S['firel'].data.energy = at(BAY, 46, -56, 12), 3500
    shoot(S, BAY, (lerp(66, 60, k), lerp(-84, -78, k), lerp(3.0, 4.2, k)), (34, -44, 9.5), 30, roll=0.03 * math.sin(t * 2.2))


def roddam_away(S, k, t, lt):
    """One steamer, grey with ash, smoke pouring from her funnel, pulls away out of the bay. Behind her the town and the other
    ships are on fire under the cloud."""
    sky(S, 'blast')
    pose_cloud(S['cloud'], (0, 170, 70), (10, -40, 14), 0.97, t, 2.3, 3.6)
    fire(S, 0, at(BAY, 40, -45, 5), t, 1.1)
    fire(S, 1, at(BAY, -20, -62, 5), t + 3, 1.0)
    x, y = lerp(-34, -44, k), lerp(-128, -152, k)
    S['steamer'].location = at(BAY, x, y, 0.4 + 0.25 * math.sin(t * 1.3))
    S['steamer'].rotation_euler = (0.03 * math.sin(t * 1.1), 0.05 * math.sin(t * 0.8), -0.38)
    for i, o in enumerate(S['stsmoke']):
        o.location = (1.2 * math.sin(t + i), 2 + 2.8 * i + 0.6 * math.sin(t * 0.8 + i), 14 + 2.3 * i)
    S['firel'].location, S['firel'].data.energy = at(BAY, 40, -52, 14), 3500
    key(S, BAY, (x - 16, y - 22, 30), (x, y, 5), 70000, 'FFB888')
    shoot(S, BAY, (x - 15 - 2 * k, y - 31, lerp(4.5, 6, k)), (x + 2, y + 5, 8.5), 34)


# ---------------------------------------------------------------- in the cell
def slit_dark(S, k, t, lt):
    """Inside the cell, low and close: he stands at the door with the strip of daylight from the slit across his face. The strip
    goes grey, then dark. He looks up at it."""
    cell(S, 'day')
    f = 1 - sm(k * 1.15)
    S['outside'].data.materials[0] = K.mat('DCEBFF' if f > 0.3 else '6A5A52', 0.9, emit=round(0.3 + 3.2 * f, 1))
    S['slitl'].data.energy = 60 + 840 * f
    S['celll'].data.energy = 34 + 16 * f
    m = tput(S, S['man'], CELL, -0.15, -1.45, 0, 0.2, P('stand', aL=(0.3, 0.2, 0.5), aR=(lerp(0.3, 1.3, sm(lt / 1.2)), 0.2, 0.9), head=(lerp(0.1, -0.3, sm(lt / 1.0)), 0.0)), 'calm' if f > 0.5 else 'wide')
    h = head(S, m)
    shoot(S, (0, 0, 0), (h[0] - lerp(1.35, 1.1, k), h[1] - 1.3, h[2] - lerp(0.6, 0.4, k)), (h[0] + 0.1, h[1] - 0.45, h[2] - 0.05), 34)


def cloth_slit(S, k, t, lt):
    """Over his shoulder at the door: he rams a wet bundle of cloth into the slit with both hands and leans on it. The orange
    glare shrinks to a line round the edges."""
    cell(S, 'glow', ash=0.6)
    u = sm(lt / 0.7)
    S['slitl'].data.energy *= 1 - 0.8 * u
    S['celll'].data.energy = 150 - 70 * u
    m = tput(S, S['man'], CELL, 0.1, -2.1, 0, 0.1, blend(P('stand', aL=(1.0, 0.3, 1.2), aR=(1.0, 0.3, 1.2), head=(0.0, 0.0)),
                                                         P('stand', aL=(1.75, 0.12, 0.35), aR=(1.75, 0.12, 0.35), head=(0.2, 0.0), lean=0.22), u), 'pain', 0.2)
    a, b = wpos(m.hands[0]), wpos(m.hands[1])
    S['cloth'].location = ((a[0] + b[0]) / 2, min(a[1], b[1]) - 0.1, (a[2] + b[2]) / 2 + 0.05)
    key(S, CELL, (1.5, 0.5, 2.8), (0.1, -2.3, 2.0), 220, 'FF9A5A')
    shoot(S, CELL, (lerp(1.9, 1.5, k), lerp(-0.2, -0.6, k), lerp(2.75, 2.5, k)), (-0.1, -2.75, 2.0), 30, roll=0.02 * math.sin(t * 19))


# ---------------------------------------------------------------- afterwards
def edge_house(S, k, t, lt):
    """The edge of the town, grey with ash, burned trunks, broken walls. Out of a low stone workshop a man in an apron climbs the
    steps into the light, one arm held against his chest."""
    use(S, 'edge')
    sky(S, 'ash')
    u = sm(lt / 2.2)
    tput(S, S['towns'][2], EDGE, lerp(-5.9, -3.6, u), lerp(1.7, -1.0, u), lerp(0.0, 0.03, u), facing((0, 0), (2.3, -2.7)),
         dict(K.walk(t * 0.55, 1.0), aL=(0.7, -0.1, 1.9, 1.0), lean=0.3, head=(0.3, 0.2)), 'pain')
    key(S, EDGE, (3, -8, 5), (-4.5, 0.5, 2), 800, 'E8E0D4')
    shoot(S, EDGE, (lerp(1.6, 1.0, k), lerp(-6.0, -5.2, k), 2.0), (-4.4, 0.6, 2.1), 30)


def cell_stands(S, k, t, lt):
    """From above the ruined prison: walls down, ash over everything, and in the middle of it the squat stone cell, whole. Rook
    stands on its roof and turns right round, looking."""
    sky(S, 'ash')
    yard(S, 'ruin')
    put(S, S['rook'], YARD, 0.4, 0.4, 2.42, lerp(-0.6, 0.9, sm(k)), P('hips', head=(0.05, lerp(0.5, -0.5, sm(k)))), 'soft')
    key(S, YARD, (8, -14, 10), (0.4, 0.4, 4), 2500, 'E8E0D4')
    shoot(S, YARD, (lerp(8.6, 7.0, k), lerp(-13.5, -11.5, k), lerp(7.2, 5.8, k)), (0, 0.4, 3.0), 30)


def ring_tell(S, k, t, lt):
    """Close in the circus ring: he stands in front of the copy of his cell and tells it, one hand showing how high the slit was,
    then both arms over his head. The crowd leans in."""
    sky(S, 'tent')
    S['spot'].data.energy, S['tentl'].data.energy = 40000, 2500
    S['spotaim'].location = at(RING, 0.8, 0.4, 1.8)
    u = sm((lt - 1.0) / 0.5)
    tput(S, S['man'], RING, 0.8, 0.4, 0.04, -0.4, blend(P('stand', aR=(1.5, 0.2, 0.9, 0.2), head=(0.0, 0.1)), P('stand', aL=(2.3, 0.4, 1.3), aR=(2.3, 0.4, 1.3), head=(0.25, 0.0), lean=0.15), u),
         'calm', 0.25 + 0.25 * abs(math.sin(lt * 7)))
    for i, p in enumerate(S['crowd']):
        p.rotation_euler.x = 0.12 * sm(k) + 0.04 * math.sin(t * 2 + i)
    key(S, RING, (-3, -6, 4), (0.8, 0.4, 2.4), 900, 'FFD8A0')
    shoot(S, RING, (lerp(-1.5, -1.1, k), lerp(-3.9, -3.3, k), 2.3), (1.1, 0.6, 2.5), 34)


def geologist(S, k, t, lt):
    """On a rise above the ruined town: a man in a pale suit and sun hat writes in a notebook beside a camera on a tripod. Rook
    stands at his elbow, reads what he has written, and taps his beak."""
    sky(S, 'ash', 'day', 0.35)
    town(S, True)
    for s_ in S['ships']:
        s_.location.z = -40
    S['mound'].location = at(BAY, 140, 50, -0.4)
    S['tripod'].location = at(BAY, 141.9, 48.9, 2.5)
    S['tripod'].rotation_euler = (0, 0, 2.4)
    w = math.sin(lt * 9)
    g = tput(S, S['geo'], BAY, 140.3, 50.2, 2.7, facing((140.3, 50.2), (0, 330)) - 1.0, P('stand', aL=(0.9, 0.0, 1.5, 0.6), aR=(0.9, -0.1 + 0.03 * w, 1.75, 0.8), head=(0.42, 0.0)), 'calm')
    hd = wpos(g.hands[0])
    S['book'].location = (hd[0], hd[1], hd[2] + 0.16)
    S['book'].rotation_euler = (1.1, 0, g.root.rotation_euler[2])
    u = sm((lt - 1.0) / 0.5)
    put(S, S['rook'], BAY, 138.9, 51.4, 2.55, facing((138.9, 51.4), (140.3, 50.2)) - 0.9, blend(P('stand', head=(0.4, 0.7)), P('tap', head=(0.3, 0.6)), u), 'calm')
    key(S, BAY, (148, 56, 9), (140.5, 50.5, 4.5), 1600, 'F2EADA')
    shoot(S, BAY, (lerp(146.6, 145.8, k), lerp(57.4, 56.6, k), 5.0), (140.9, 50.6, 5.0), 34)


def spine_rise(S, k, t, lt):
    """At the summit, months later: out of the crater a spine of dark rock pushes up, taller and taller. Rook on the rim holds his
    hat and leans back to see the top. Then its sides break away and it sinks into its own rubble."""
    sky(S, 'ash', 'day', 0.5)
    town(S, True)
    z = S['gz']['rim']
    up = sm(k / 0.6)
    fall = sm((k - 0.68) / 0.3)
    S['spine'].location = at(BAY, 0, 330, 205 - 82 * (1 - up) - 30 * fall)
    S['spine'].scale = (1 + 0.25 * fall, 1 + 0.25 * fall, 1 - 0.45 * fall)
    S['spine'].rotation_euler = (0.05 * fall, 0.02 * math.sin(t * 20) * (fall > 0) * (fall < 1), 0)
    for i, o in enumerate(S['rocks']):
        f = max(0.0, fall - 0.05 * (i % 4))
        a = 2 * PI * rnd(i, 5)
        r_ = 10 + 46 * f * (0.5 + rnd(i, 6))
        o.location = at(BAY, r_ * math.cos(a), 330 + r_ * math.sin(a), 290 - 60 * rnd(i, 7) - 140 * f * f) if f > 0 else FAR
        o.rotation_euler = (t * 3 + i, t * 2, i)
    pose_cloud(S['steam'], (0, 330, 214), (4, 330, 250), 0.4 + 0.5 * fall, t, 1.0 + 1.6 * fall, 1.2)
    turn = sm((k - 0.82) / 0.14)
    put(S, S['rook'], BAY, RIM[0], RIM[1], z, facing(RIM, (0, 330)) - 0.6 - 2.3 * turn, blend(P('stand', head=(-0.2, 0.3)), P('hat', head=(-0.5 + 0.5 * turn, 0.35), lean=-0.1), up), 'shocked' if up > 0.4 else 'calm')
    S['hat_tip'] = -0.6 * up * (1 - turn)
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 5, h[1] - 6, h[2] + 2), h, 1400, 'F2EADA')
    shoot(S, BAY, (SPCAM[0] - lerp(0.0, 0.5, k), SPCAM[1] - lerp(0.0, 0.6, k), S['gz']['spcam'] + 1.5), (RIM[0] + 6, RIM[1] + 7, z + lerp(6.5, 9.5, up)), 34)


def bay_today(S, k, t, lt):
    """The bay now: a small town of a few roofs among trees where the city stood, the two towers gone, the mountain green again
    under a clear sky."""
    sky(S, 'day')
    for i, o in enumerate(S['walls']):
        o.hide_render = i % 3 != 0 or i >= len(S['walls']) - 3
    for i, o in enumerate(S['roofs']):
        o.hide_render = i % 3 != 0 or i >= len(S['roofs']) - 3
    for i, s_ in enumerate(S['ships']):
        s_.location.z = 0 if i == 1 else -40
    shoot(S, BAY, (lerp(84, 64, k), lerp(-96, -84, k), lerp(14, 19, k)), (-4, 70, 34), 30)


def photo_thumb(S, k, t, lt):
    """The thumbnail picture: his face close in the orange strip of light from the slit, on the right of the frame; the dark of
    the cell on the left for the words."""
    cell(S, 'glow')
    m = put(S, S['man'], CELL, -0.4, -0.2, 0, 0.25, P('sit', head=(-0.3, 0.25), aL=(0.5, 0.3, 1.6, 0.8)), 'wide')
    hh = head(S, m)
    key(S, CELL, (0.4, -2.6, 2.4), hh, 160, 'FF8A3A')
    shoot(S, (0, 0, 0), (hh[0] + 0.25, hh[1] - 1.75, hh[2] + 0.05), (hh[0] - 0.62, hh[1], hh[2] - 0.02), 40)


NEW = (bay_calm, quay_life, quay_close, quay_ash, summit_steam, snake_lane, snake_close, mud_valley, mud_after, hall_report, hall_window,
       road_in, gov_arrive, party_night, rook_room, ships_fire, roddam_away, slit_dark, cloth_slit, edge_house, cell_stands, ring_tell,
       geologist, spine_rise, bay_today)
SHORT_KINDS = set(SHOTS3D)
SHOTS3D.update({f.__name__: f for f in NEW})
STILLS = dict(thumb=photo_thumb)


# The Short's shots were timed for a second or two; here most run about twice as long. Their acting is spread over the shot
# (local time is slowed, never sped up) and the camera keeps easing in towards its subject on a slight arc, so a held frame
# keeps developing. prm "arc": [degrees, push] sets the move for one shot.
def _held(f, name):
    sign = 1 if sum(map(ord, name)) % 2 else -1
    wide = name in ('bay_blast', 'cloud_rush', 'cloud_town', 'town_ash')

    def g(S, k, t, lt):
        f(S, k, t, min(lt, 1.6 * k))
        deg, push = S['prm'].get('arc', (sign * (2.5 if wide else 6.0), 0.04 if wide else 0.1))
        c, tg = S['camrig'].location, S['camtgt'].location
        a = math.radians(deg) * (k - 0.5)
        m = 1 - push * (k - 0.5)
        dx, dy = c[0] - tg[0], c[1] - tg[1]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, c[2])
    g.__name__ = name
    g.__doc__ = f.__doc__
    return g


_dig0 = SHOTS3D['dig_out']


def dig_out(S, k, t, lt):
    """The Short's rescue, re-staged for the wide frame: Rook is not up on the roof (out of a 16:9 frame from down in the pit)
    but sitting on the edge of the pit beside the men, hat in his hand."""
    _dig0(S, k, t, lt)
    put(S, S['rook'], YARD, 2.95, -4.7, -0.38, -PI / 2 - 0.25, P('sit', aL=(0.6, -0.2, 2.0, 1.0), head=(0.3, 0.35)), 'soft')
    S['hat_off'] = 1.0


SHOTS3D['dig_out'] = dig_out
for _n in SHORT_KINDS:
    SHOTS3D[_n] = _held(SHOTS3D[_n], _n)
