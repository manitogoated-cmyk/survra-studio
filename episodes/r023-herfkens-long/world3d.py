"""Case 023 in 3D - Annette Herfkens, eight days beside the wreck of Vietnam Airlines Flight 474, November 1992.
On 14 November 1992 a Yakovlev Yak-40 flying from Ho Chi Minh City to Nha Trang came down in bad weather and hit
trees on a jungle mountain ridge. Of the 31 people aboard, 30 died. Annette Herfkens woke pinned under a seat with a
broken jaw, a collapsed lung and a shattered hip; her fiance, Willem van der Pas, had died in the crash, and a man
near her who had survived the impact died soon after. She pulled herself to the broken wing, took tufts of its
insulation, and used them as sponges to catch rain. The wreck was not found for eight days. On day eight a local
police officer found her; rescuers carried her down the mountain.

Built for this story only: a steep jungle slope in the rain with giant trees, ferns and broken trunks, the broken
fuselage of a small three-engine jet and its torn-off wing, the inside of the broken cabin, the intact jet in the
storm over the ridge, and a range of green ridges under cloud seen from far above.

Everything is a generic low-poly reconstruction: no person's likeness is attempted, the aircraft is a generic
three-engine jet rather than a copy of the real one, and no injury is shown beyond a bruise."""
import math

import bpy
import numpy as np
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -6000)
RIDGE = (0.0, 0.0, 0.0)             # the slope where the wreck lies
CABIN = (6000.0, 0.0, 0.0)          # inside the broken cabin
RANGE = (0.0, 9000.0, 0.0)          # the ridges from far above
HOST = {'wing_torn', 'rook_doubt', 'rook_hatoff', 'wing_pov', 'rook_squeeze', 'rook_nod', 'rain_arrives',
        'rook_lookout', 'rook_vigil', 'rook_brim', 'rook_wreck', 'signoff'}
CAMFILL = {'*': 160, 'crash_ridge': 60, 'seat_pin': 160, 'wreck_wide': 90, 'wing_torn': 160, 'rook_doubt': 260,
           'hands_hold': 120, 'rook_hatoff': 240, 'man_beside': 200, 'her_alone': 160, 'thirst_face': 140,
           'wing_pov': 120, 'rook_squeeze': 240, 'elbow_crawl': 200, 'tuft_pull': 120, 'rook_nod': 240,
           'rain_arrives': 120, 'tuft_drink': 180, 'aerial_canopy': 0, 'rook_lookout': 240, 'night_wreck': 200,
           'calm_face': 110, 'rook_vigil': 280, 'officer_trees': 160, 'officer_ghost': 180, 'rook_brim': 240,
           'carry_down': 140, 'rook_wreck': 200, 'carry_light': 80, 'signoff': 200}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN, HAIR = 'E6BC9A', '7A5634'
LEAF = ('2E6A32', '3A7A3A', '24582C', '4A8A3E', '1E4A28')
FUSE, FUSE2, TRIM = 'DCDDE0', 'B4B8BE', '2A5A9A'
INSUL = 'E8D890'
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    storm=('34444A', '0C1418', 0.55, 0.5, 'A0B4C8', (-0.4, 0.3, 0.85)),
    rain=('62786E', '24342E', 0.75, 1.2, 'C8D8D0', (-0.3, -0.4, 0.85)),
    day=('D2E0B4', '5C9080', 1.05, 3.6, 'FFF0C8', (0.35, -0.45, 0.82)),
    night=('16222C', '04080C', 0.3, 0.35, '8AA8D8', (-0.5, 0.2, 0.8)),
    dawn=('F2C08E', '7090A6', 0.95, 2.4, 'FFC890', (0.6, -0.6, 0.35)),
    morning=('E6E8C4', '6C9CA8', 1.1, 3.2, 'FFE8C0', (0.5, -0.5, 0.6)),
    high=('CFE0E4', '5C8CB8', 1.2, 3.4, 'FFF4E0', (0.4, -0.3, 0.8)),
    cabin=('18201A', '060806', 0.25, 0.0, 'FFFFFF', (0, 0, 1)))
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


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def bar(par, col, a, b, w, **kw):
    o = add('cylinder', col, radius=0.5, depth=1, vertices=6, parent=par, **kw)
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))
    return o


# ---------------------------------------------------------------- the slope
def g(x, y):
    """Ground height on the slope: rising steeply uphill (+y), with folds."""
    return 0.3 * y + 0.55 * math.sin(0.23 * x + 0.4) * math.cos(0.17 * y) + 0.18 * math.sin(0.6 * x + 1.1 * y)


def gp(x, y, dz=0.0):
    return at(RIDGE, x, y, g(x, y) + dz)


FUS = (3.4, 3.2)                    # fuselage centre (set-local x, y)
SPOT = (-0.6, 0.4)                  # where she sits, against a root beside the broken end
WROOT = (-2.9, -1.4)                # the wing's torn root
MAN = (1.0, 1.4)                    # the man who survived the impact
LIE = (-1.4, -1.6)                  # where she lies through the nights


def tree(par, i, x, y, big=1.0):
    h = (9 + 8 * rnd(i, 1)) * big
    z = g(x, y)
    tr = '4A3A2C' if i % 3 else '5C4A36'
    add('cylinder', tr, (x, y, z + h / 2), radius=(0.35 + 0.3 * rnd(i, 2)) * big, depth=h, vertices=7, parent=par, rough=1.0)
    for b in range(2):                                                                                           # buttress roots
        a = 2 * PI * b / 2 + rnd(i, 3)
        add('cone', tr, (x + 0.45 * big * math.cos(a), y + 0.45 * big * math.sin(a), z + 0.5), rot=(0.5 * math.sin(a), -0.5 * math.cos(a), 0),
            radius1=0.35 * big, radius2=0.05, depth=1.4 * big, vertices=4, parent=par, rough=1.0)
    crowns = []
    for c in range(2):
        cr = add('ico_sphere', LEAF[(i + c) % 5], (x + 1.6 * (rnd(i, 4 + c) - 0.5) * big, y + 1.6 * (rnd(i, 7 + c) - 0.5) * big, z + h - 0.4 + 1.2 * c * big),
                 scale=(1.0, 1.0, 0.55), radius=(3.0 + 1.8 * rnd(i, 10 + c)) * big, subdivisions=1, parent=par, rough=0.8)
        crowns.append(cr)
    return crowns


def palm(par, i, x, y, s=1.0):
    z = g(x, y)
    fr = []
    for b in range(5):
        a = 2 * PI * b / 5 + rnd(i, 1)
        o = add('cone', LEAF[(i + b) % 5], (x + 0.9 * s * math.cos(a), y + 0.9 * s * math.sin(a), z + 0.5 * s), rot=(1.0 * math.sin(a), -1.0 * math.cos(a), 0),
                scale=(1, 0.25, 1), radius1=0.5 * s, radius2=0.0, depth=2.4 * s, vertices=4, parent=par, rough=0.8)
        fr.append(o)
    return fr


def make_ridge(S):
    r = empty(RIDGE)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=90, y_subdivisions=90, size=110, location=RIDGE)
    gr = bpy.context.object
    gr.parent = r
    co = np.zeros(len(gr.data.vertices) * 3)
    gr.data.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    co[:, 2] = [g(x, y) for x, y in co[:, :2]]
    gr.data.vertices.foreach_set('co', co.ravel())
    gr.data.update()
    gr.data.materials.append(K.mat('34401E', 1.0))
    S['sway'] = []
    n = 0
    for i in range(75):                                                                                         # the forest round the clearing
        a = 2 * PI * rnd(i, 21)
        d = 8.5 + 36 * rnd(i, 22) ** 1.3
        x, y = 1.5 + d * math.cos(a), 2.0 + d * math.sin(a)
        if abs(x) > 54 or abs(y) > 54 or (-17 < x < 13 and -16 < y < 8):                                         # the swath the jet cut
            continue
        S['sway'] += tree(r, i, x, y, 0.8 + 0.6 * rnd(i, 23))
        n += 1
    for i in range(30):                                                                                          # palms and ferns on the ground
        a = 2 * PI * rnd(i, 31)
        d = 3.0 + 18 * rnd(i, 32)
        x, y = 0.5 + d * math.cos(a), 1.5 + d * math.sin(a)
        tq = max(0.0, min(1.0, ((x - SPOT[0]) * (WROOT[0] - SPOT[0]) + (y - SPOT[1]) * (WROOT[1] - SPOT[1])) / ((WROOT[0] - SPOT[0]) ** 2 + (WROOT[1] - SPOT[1]) ** 2)))
        if math.hypot(x - SPOT[0] - tq * (WROOT[0] - SPOT[0]), y - SPOT[1] - tq * (WROOT[1] - SPOT[1])) < 2.2 or math.hypot(x - SPOT[0], y - SPOT[1]) < 1.8 or math.hypot(x - WROOT[0], y - WROOT[1]) < 2.0 or math.hypot(x - FUS[0], y - FUS[1]) < 4.5:
            continue
        S['sway'] += palm(r, i, x, y, 0.6 + 0.8 * rnd(i, 33))
    for i, (x, y) in enumerate(((-8.5, 7.5), (-4.0, 9.0), (-11.0, 4.0), (-14.0, -3.0), (9.5, -6.0), (12.0, 1.0))):       # trees at the clearing's edge
        S['sway'] += tree(r, 300 + i, x, y, 0.9)
    for i in range(7):                                                                                           # trees the jet snapped off
        x, y = 5 + 3.2 * i + 2 * rnd(i, 41), 7 + 1.2 * i
        z = g(x, y)
        hh = 2.5 + 2 * rnd(i, 42)
        add('cylinder', '6A5640', (x, y, z + hh / 2), rot=(0.2 * rnd(i, 43), 0.3 * rnd(i, 44), 0), radius=0.4, depth=hh, vertices=7, parent=r, rough=1.0)
        add('cone', 'C8B48A', (x, y, z + hh + 0.3), radius1=0.42, radius2=0.05, depth=0.7, vertices=5, parent=r, rough=1.0)
    for i in range(10):                                                                                          # roots across the ground
        x0, y0 = -4 + 1.2 * i + rnd(i, 51), -3 + 3.5 * rnd(i, 52)
        a = rnd(i, 53) * PI
        x1, y1 = x0 + 2.2 * math.cos(a), y0 + 2.2 * math.sin(a)
        bar(r, '4A3A2A', gp(x0, y0, 0.05), gp(x1, y1, 0.08), 0.12, rough=1.0)
    bar(r, '4A3A2A', gp(SPOT[0] - 1.2, SPOT[1] + 0.9, 0.2), gp(SPOT[0] + 1.0, SPOT[1] + 1.0, 0.35), 0.28, rough=1.0)    # the root she leans on
    for i in range(30):                                                                                          # leaf litter
        x, y = -6 + 12 * rnd(i, 61), -5 + 10 * rnd(i, 62)
        add('cube', ('6A5A2A', '4A5A2A', '7A6A3A')[i % 3], gp(x, y, 0.03), rot=(0, 0, rnd(i, 63) * PI), scale=(0.3, 0.16, 0.02), size=1, parent=r)
    add('plane', '1E2A1E', (0, 0, -2), size=900, parent=r, rough=1.0)                                            # far ground
    for i in range(9):                                                                                           # far ridges in the haze
        a = -1.2 + 2.4 * i / 8
        add('cone', ('2E4440', '3A524C', '26383A')[i % 3], (110 * math.sin(a) + 20, 120 * math.cos(a) + 40, 10), radius1=60 + 20 * rnd(i, 71),
            radius2=4, depth=55 + 30 * rnd(i, 72), vertices=6, parent=r, rough=1.0)
    S['ridge'] = r
    # the broken fuselage, nose gone, lying along the slope
    fu = empty(gp(FUS[0], FUS[1], 1.25), r, (0.05, -0.32, 0.35))
    add('cylinder', FUSE, (1.0, 0, 0), rot=(0, PI / 2, 0), radius=1.3, depth=11, vertices=12, parent=fu, rough=0.45)
    add('cylinder', '1A1C1E', (-4.45, 0, 0), rot=(0, PI / 2, 0), radius=1.18, depth=0.2, vertices=12, parent=fu, rough=1.0)   # dark open end
    for i in range(9):                                                                                           # jagged torn skin at the open end
        a = 2 * PI * i / 9
        add('cone', FUSE2, (-4.6, 1.25 * math.cos(a), 1.25 * math.sin(a)), rot=(0, -PI / 2 + 0.3 * rnd(i, 81), 0), radius1=0.32, radius2=0.0,
            depth=0.5 + 0.5 * rnd(i, 82), vertices=3, parent=fu, rough=0.5)
    add('cube', TRIM, (1.0, 0, -0.35), scale=(11, 2.64, 0.16), size=1, parent=fu, rough=0.5)                    # cheat line
    for i in range(10):
        for s_ in (-1, 1):
            add('cube', '1A2430', (-3.0 + 0.85 * i, s_ * 1.27, 0.25), scale=(0.3, 0.04, 0.26), size=1, parent=fu, rough=0.2)
    add('cone', FUSE, (7.2, 0, 0.25), rot=(0, PI / 2, 0), radius1=1.2, radius2=0.4, depth=2.6, vertices=12, parent=fu, rough=0.45)   # tail cone
    add('cube', FUSE, (7.0, 0, 2.2), rot=(0, -0.45, 0), scale=(2.2, 0.22, 3.2), size=1, parent=fu, rough=0.45)                       # fin
    add('cube', FUSE, (7.9, 0, 3.7), scale=(1.4, 4.6, 0.16), size=1, parent=fu, rough=0.45)                                            # T-tail
    for s_ in (-1, 1):                                                                                           # side engines
        add('cylinder', FUSE2, (5.6, s_ * 1.7, 0.6), rot=(0, PI / 2, 0), radius=0.5, depth=2.4, vertices=10, parent=fu, rough=0.4)
        add('cylinder', '1A1A1C', (4.39, s_ * 1.7, 0.6), rot=(0, PI / 2, 0), radius=0.42, depth=0.04, vertices=10, parent=fu)
    add('cylinder', FUSE2, (5.8, 0, 1.55), rot=(0, PI / 2, 0), radius=0.45, depth=2.2, vertices=10, parent=fu, rough=0.4)
    add('cube', FUSE2, (2.0, 1.4, -1.0), rot=(0.3, 0, 0), scale=(1.6, 0.5, 0.12), size=1, parent=fu)            # stub of the wing
    S['fuse'] = fu
    # the torn-off wing, lying in the ferns, its root torn open and full of insulation
    wg = empty(gp(WROOT[0], WROOT[1], 0.35), r, (0.12, 0.06, -0.38))
    add('cube', FUSE, (-3.6, 0, 0), scale=(7.4, 2.3, 0.26), size=1, parent=wg, rough=0.45)
    add('cube', FUSE, (-7.6, 0.3, 0), rot=(0, 0, 0.2), scale=(1.4, 1.5, 0.18), size=1, parent=wg, rough=0.45)
    add('cube', TRIM, (-3.6, 1.1, 0.06), scale=(7.4, 0.08, 0.2), size=1, parent=wg, rough=0.5)
    add('cube', FUSE2, (-3.6, -1.05, 0.0), rot=(0.25, 0, 0), scale=(7.0, 0.6, 0.1), size=1, parent=wg, rough=0.4)   # flap, bent
    for i in range(7):                                                                                           # torn skin at the root
        add('cone', FUSE2, (0.35, -1.0 + 0.33 * i, 0.15 * (rnd(i, 91) - 0.5)), rot=(0, PI / 2 + 0.6 * (rnd(i, 92) - 0.5), 0.4 * (rnd(i, 93) - 0.5)),
            radius1=0.2, radius2=0.0, depth=0.5 + 0.4 * rnd(i, 94), vertices=3, parent=wg, rough=0.5)
    S['insul'] = []
    for i in range(12):                                                                                          # the insulation, bulging from the root
        S['insul'].append(add('ico_sphere', INSUL, (0.15 + 0.25 * rnd(i, 95), -0.95 + 0.17 * i, 0.12 * (rnd(i, 96) - 0.3)),
                              radius=0.17 + 0.07 * rnd(i, 97), subdivisions=1, parent=wg, rough=1.0))
    S['wing'] = wg
    S['rivet'] = keep(add('cylinder', 'E8ECF2', FAR, radius=0.06, depth=0.05, vertices=8, rough=0.15))
    S['balls'] = [keep(add('ico_sphere', INSUL, FAR, radius=0.13, subdivisions=1, rough=1.0)) for _ in range(4)]
    S['tuft'] = keep(add('ico_sphere', INSUL, FAR, radius=0.2, subdivisions=1, rough=1.0))
    S['drips'] = [keep(add('ico_sphere', 'BFEFFF', FAR, radius=0.025, subdivisions=1, rough=0.05, emit=0.4)) for _ in range(6)]
    S['flies'] = [keep(add('ico_sphere', 'E8FF90', FAR, radius=0.04, subdivisions=1, emit=12.0)) for _ in range(14)]
    # the hammock on its pole, for the carry
    hm = S['hammock'] = keep(empty(FAR))                                                                         # canvas slung between two sticks
    for s_ in (-1, 1):
        bar(hm, '6A5030', (-2.7, s_ * 0.42, 1.3), (2.7, s_ * 0.42, 1.3), 0.06, rough=1.0)
    add('cube', 'A89A70', (0, 0, 1.2), scale=(3.0, 0.84, 0.08), size=1, parent=hm, rough=1.0)


# ---------------------------------------------------------------- the jet in the storm
def make_jet(S):
    j = keep(empty(FAR))
    add('cylinder', FUSE, (0, 0, 0), rot=(0, PI / 2, 0), radius=1.3, depth=13, vertices=12, parent=j, rough=0.45)
    add('cone', FUSE, (-7.6, 0, -0.1), rot=(0, -PI / 2, 0), radius1=1.3, radius2=0.3, depth=2.4, vertices=12, parent=j, rough=0.45)
    add('cube', '1A2430', (-7.4, 0, 0.45), rot=(0, 0.4, 0), scale=(0.7, 1.6, 0.35), size=1, parent=j, rough=0.2)
    add('cube', TRIM, (0, 0, -0.35), scale=(13, 2.64, 0.16), size=1, parent=j, rough=0.5)
    add('cone', FUSE, (7.6, 0, 0.25), rot=(0, PI / 2, 0), radius1=1.2, radius2=0.4, depth=2.6, vertices=12, parent=j, rough=0.45)
    add('cube', FUSE, (7.4, 0, 2.2), rot=(0, -0.45, 0), scale=(2.2, 0.22, 3.2), size=1, parent=j, rough=0.45)
    add('cube', FUSE, (8.3, 0, 3.7), scale=(1.4, 4.6, 0.16), size=1, parent=j, rough=0.45)
    for s_ in (-1, 1):
        add('cube', FUSE, (0.6, s_ * 6.5, -0.6), rot=(s_ * -0.06, 0, s_ * 0.1), scale=(2.2, 11, 0.24), size=1, parent=j, rough=0.45)
        add('cylinder', FUSE2, (6.0, s_ * 1.7, 0.6), rot=(0, PI / 2, 0), radius=0.5, depth=2.4, vertices=10, parent=j, rough=0.4)
        S.setdefault('navl', []).append(add('ico_sphere', 'FF3030' if s_ < 0 else '30FF60', (0.6, s_ * 12.0, -0.5), radius=0.18, subdivisions=1, parent=j, emit=20))
    add('cylinder', FUSE2, (6.2, 0, 1.55), rot=(0, PI / 2, 0), radius=0.45, depth=2.2, vertices=10, parent=j, rough=0.4)
    for i in range(12):
        for s_ in (-1, 1):
            add('cube', 'FFE0A0', (-4.5 + 0.85 * i, s_ * 1.27, 0.25), scale=(0.3, 0.04, 0.24), size=1, parent=j, emit=2.0)
    S['jet'] = j
    S['debris'] = [keep(add('cube', LEAF[i % 5] if i % 3 else '5A4632', FAR, scale=(0.5, 0.3, 0.06), size=1, rough=0.9)) for i in range(26)]


# ---------------------------------------------------------------- inside the broken cabin
def make_cabin(S):
    c = empty(CABIN)
    add('cube', '3A3A40', (0, 0, -0.05), scale=(3.0, 9, 0.1), size=1, parent=c, rough=0.8)                       # floor
    add('cube', '5A6A5A', (0, 0, -0.02), scale=(0.7, 9, 0.02), size=1, parent=c, rough=1.0)                      # aisle carpet
    for s_ in (-1, 1):
        add('cube', 'C8C4BA', (s_ * 1.5, 0, 1.2), rot=(0, s_ * 0.18, 0), scale=(0.1, 9, 2.6), size=1, parent=c, rough=0.6)
        for i in range(6):
            add('cube', 'A8D8A0', (s_ * 1.43, -3.5 + 1.4 * i, 1.45), rot=(0, s_ * 0.18, 0), scale=(0.04, 0.4, 0.35), size=1, parent=c, emit=1.2)
    add('cube', 'C8C4BA', (-0.6, -2.0, 2.55), rot=(0, 0.1, 0), scale=(1.8, 5, 0.1), size=1, parent=c, rough=0.6)     # what is left of the roof
    for i in range(8):                                                                                           # torn edge of the roof
        add('cone', 'A8A49A', (0.4 + 0.2 * rnd(i, 1), 0.6 + 0.45 * i, 2.5), rot=(0, 1.2 + 0.5 * rnd(i, 2), 0), radius1=0.18, radius2=0, depth=0.6,
            vertices=3, parent=c, rough=0.6)
    for i in range(8):                                                                                           # leaves and branches poking in
        add('ico_sphere', LEAF[i % 5], (0.6 + 1.2 * rnd(i, 3), 1.0 + 3.0 * rnd(i, 4), 2.8 + 0.6 * rnd(i, 5)), scale=(1, 1, 0.5), radius=0.9,
            subdivisions=1, parent=c, rough=0.8)
    S['seats'] = []
    for i in range(5):                                                                                           # rows of seats, knocked askew
        for s_ in (-1, 1):
            st = empty((s_ * 0.85, -3.4 + 1.3 * i, 0), c, (0, 0, 0.15 * (rnd(i, s_ + 7) - 0.5)))
            add('cube', '3E5A86', (0, 0, 0.45), scale=(0.9, 0.8, 0.18), size=1, parent=st, rough=0.9)
            add('cube', '3E5A86', (0, 0.38, 0.95), rot=(-0.15, 0, 0), scale=(0.9, 0.16, 1.0), size=1, parent=st, rough=0.9)
            add('cube', 'E8E4D8', (0, 0.42, 1.38), scale=(0.7, 0.14, 0.2), size=1, parent=st, rough=1.0)
            for a in (-1, 1):
                add('cube', '5A5A60', (a * 0.46, 0.05, 0.62), scale=(0.08, 0.7, 0.06), size=1, parent=st, rough=0.5)
            add('cube', '2A2A2E', (0, 0, 0.18), scale=(0.7, 0.6, 0.36), size=1, parent=st, rough=0.6)
    S['fallen'] = fs = keep(empty(FAR))                                                                         # the seat that came down on her
    add('cube', '3E5A86', (0, 0, 0), scale=(0.9, 0.8, 0.2), size=1, parent=fs, rough=0.9)
    add('cube', '3E5A86', (0, 0.48, 0.38), rot=(-1.0, 0, 0), scale=(0.9, 0.18, 1.0), size=1, parent=fs, rough=0.9)
    for a in (-1, 1):
        add('cube', '5A5A60', (a * 0.46, 0.0, 0.12), scale=(0.08, 0.7, 0.06), size=1, parent=fs, rough=0.5)
    S['hand_her'] = K.Hand(SKIN, 'D8C8A8', 0.9)
    S['hand_him'] = K.Hand('E2B48E', '2A3448', 1.0)
    for hd in (S['hand_her'], S['hand_him']):
        keep(hd.root)
    S['cabl'] = light(FAR, 0, 'B8F0B0', size=2.0)
    S['cabin'] = c


# ---------------------------------------------------------------- the ridges from far above
def make_range(S):
    r = empty(RANGE)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=120, size=1400, location=(0, 0, 0))
    gr = bpy.context.object
    gr.parent = r
    co = np.zeros(len(gr.data.vertices) * 3)
    gr.data.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    x, y = co[:, 0], co[:, 1]
    co[:, 2] = 70 * np.abs(np.sin(0.006 * x + 0.5 * np.sin(0.004 * y))) + 30 * np.abs(np.sin(0.011 * y + 0.3 * np.sin(0.009 * x))) + 6 * np.sin(0.05 * x + 0.04 * y)
    gr.data.vertices.foreach_set('co', co.ravel())
    gr.data.update()
    gr.data.materials.append(K.mat('2E5A30', 0.9))
    S['rco'] = co
    for i in range(60):                                                                                          # tree crowns on the near slopes
        px, py = -160 + 320 * rnd(i, 101), -60 + 260 * rnd(i, 102)
        k = np.argmin((co[:, 0] - px) ** 2 + (co[:, 1] - py) ** 2)
        add('ico_sphere', LEAF[i % 5], (px, py, co[k, 2] + 2), scale=(1, 1, 0.6), radius=7 + 5 * rnd(i, 103), subdivisions=1, parent=r, rough=0.8)
    S['lookout_crown'] = keep(add('ico_sphere', LEAF[1], FAR, scale=(1, 1, 0.5), radius=2.2, subdivisions=1, rough=0.8))
    S['clouds'] = []
    for i in range(10):
        S['clouds'].append(add('ico_sphere', 'F4F6F6', (-200 + 400 * rnd(i, 111), 160 + 200 * rnd(i, 112), 95 + 30 * rnd(i, 113)),
                               scale=(2.2, 1.2, 0.6), radius=22 + 14 * rnd(i, 114), subdivisions=2, parent=r, rough=1.0, alpha=0.75))
    S['range'] = r


# ---------------------------------------------------------------- people
def herfkens_head(head):
    d = K.human_head(SKIN, HAIR)(head)
    add('ico_sphere', HAIR, (0, 0.18, -0.12), scale=(0.9, 0.55, 0.8), radius=0.3, subdivisions=1, parent=head)        # shoulder-length hair
    add('ico_sphere', '9A6A6A', (0.06, -0.24, -0.2), scale=(1, 0.5, 0.7), radius=0.07, subdivisions=1, parent=head)  # the bruise on her jaw
    return d


def officer_head(head):
    d = K.human_head('B8865E', '17131A')(head)
    add('cylinder', '6A6A3A', (0, 0, 0.27), radius=0.32, depth=0.14, vertices=10, parent=head, rough=0.8)
    add('cube', '4A4A2A', (0, -0.36, 0.25), rot=(-0.2, 0, 0), scale=(0.4, 0.16, 0.03), size=1, parent=head)
    add('cylinder', 'D8B040', (0, -0.31, 0.3), radius=0.05, depth=0.02, vertices=8, rot=(PI / 2, 0, 0), parent=head, emit=0.5)
    return d


def rescuer_head(skin, hat):
    def fn(head):
        d = K.human_head(skin, '17131A')(head)
        if hat:
            add('cylinder', hat, (0, 0, 0.24), radius=0.42, depth=0.04, vertices=10, parent=head, rough=1.0)
            add('cone', hat, (0, 0, 0.36), radius1=0.28, radius2=0.1, depth=0.26, vertices=10, parent=head, rough=1.0)
        return d
    return fn


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_ridge(S)
    S_['wing'] = S['wing']
    make_jet(S)
    make_cabin(S)
    make_range(S)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['her'] = K.Rig(dict(top='D8C8A8', pants='4A4A5A', hand=SKIN, boot='3A3030', fore=SKIN), herfkens_head)
    S['man'] = K.Rig(dict(top='8A9AAA', pants='3A3A40', hand='C89A74', boot='2A2420', fore='8A9AAA'), K.human_head('C89A74', '1A1614'))
    S['officer'] = K.Rig(dict(top='8A8A50', pants='6A6A3A', hand='B8865E', boot='2A2018', fore='8A8A50'), officer_head)
    S['crew'] = [K.Rig(dict(top=tp, pants=pa, hand=sk, boot='2A2018', fore=sk), rescuer_head(sk, ht))
                 for tp, pa, sk, ht in (('4A6A4A', '3A3A30', 'A87A54', 'C8B080'), ('D8D0B8', '3A3A48', '9A6A48', None),
                                        ('6A5A3A', '2A2A30', 'B07E58', 'B8A070'), ('3A5A7A', '3A3A40', '9C6C4A', None))]
    S['humans'] = [S['her'], S['man'], S['officer']] + S['crew']
    S['cast'] = [S['rook']] + S['humans']
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    S['keyl'] = light((0, 0, 0), 0, 'FFE8D0', size=3.0)
    S['keytgt'] = empty()
    S['keyl'].constraints.new('TRACK_TO').target = S['keytgt']
    S['flash'] = light(FAR, 0, 'D8E8FF', size=40.0)
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 4000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w23')
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
    for l in (S['sun'], S['keyl'], S['flash'], S['cabl']):
        l.data.energy = 0
    for o in S['insul']:
        o.scale = (1, 1, 1)
    S['ridge'].location, S['cabin'].location, S['range'].location = FAR, FAR, FAR
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, talk_on=True)
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
    talk = S['beak'] if S['talk_on'] else 0.0
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


def ridge(S, mood, t, wind=0.3, b=None, k=0.0):
    S['ridge'].location = RIDGE
    sky(S, mood, b, k)
    for i, o in enumerate(S['sway']):                                                                            # leaves moving in the wind and rain
        o.rotation_euler = (wind * 0.06 * math.sin(t * 2.3 + i * 0.7), wind * 0.06 * math.sin(t * 1.9 + i * 1.3), 0)


def lightning(S, t, period=2.6, ph=0.0):
    u = (t + ph) % period
    f = 1.0 if u < 0.06 or 0.14 < u < 0.2 else 0.0
    S['flash'].location = at(RIDGE, -30, -10, 60)
    S['flash'].rotation_euler = (0.6, -0.4, 0)
    S['flash'].data.energy = 90000 * f
    S['bg'].inputs[1].default_value += 1.4 * f


def shoot(S, o, pos, look, lens=40, roll=0.0):
    S['camrig'].location, S['camtgt'].location = at(o, *pos), at(o, *look)
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


def key(S, o, pos, look, watts, col='FFE8D0'):
    S['keyl'].location, S['keytgt'].location = at(o, *pos), at(o, *look)
    S['keyl'].data.energy, S['keyl'].data.color = watts, K.hexc(col)[:3]


def put(S, rig, x, y, dz=0.0, yaw=0.0, pose=None, face=None, pitch=0.0, roll=0.0, o=None):
    """Stand a rig on the slope at set-local (x, y) (or at a fixed point in another set when o is given)."""
    rig.root.parent = None
    rig.place(at(o, x, y, dz) if o else gp(x, y, dz), yaw, pitch, roll)
    rig.apply(pose or P())
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def head(S, rig):
    return wpos(rig.head)


def on_wing(x, y=0.0):
    """A point on the wing's top surface, set-local x along the wing from its root."""
    bpy.context.view_layer.update()
    return tuple(S_['wing'].matrix_world @ Vector((x, y, 0.14)))


S_ = {}


def lie(S, rig, x, y, yaw, pose=None, face=None, dz=0.28):
    """On her back on the slope, head uphill."""
    return put(S, rig, x, y, dz, yaw, pose or P('stand', aL=(0.2, 0.3, 0.6), aR=(0.3, 0.2, 0.8), head=(0.2, 0.3)), face, pitch=-PI / 2 + 0.35)


def sit(S, rig, x, y, yaw, pose=None, face=None, dz=0.0):
    return put(S, rig, x, y, dz + 0.35, yaw, pose or P('sit', lean=-0.25, head=(0.1, 0.0)), face)


def her_spot(S, face='tired', pose=None):
    return sit(S, S['her'], SPOT[0], SPOT[1], 0.25, pose, face)


def flies(S, t, cx, cy, cz, n=14):
    for i, f in enumerate(S['flies']):
        if i >= n:
            continue
        a = t * (0.3 + 0.2 * rnd(i, 1)) + 2 * PI * rnd(i, 2)
        f.location = (cx + 3.5 * rnd(i, 3) * math.cos(a), cy + 3.5 * rnd(i, 4) * math.sin(a), cz + 1.5 * rnd(i, 5) + 0.4 * math.sin(t * 1.3 + i))
        f.scale = (1, 1, 1) if (t * 0.7 + rnd(i, 6)) % 1 < 0.6 else (0.3, 0.3, 0.3)


# ---------------------------------------------------------------- the hook
def crash_ridge(S, k, t, lt):
    """Storm over the ridge: the jet comes in low under the cloud from the left, its wing tearing through the treetops,
    leaves and branches bursting out. First and last shot."""
    d = lt / k if k > 1e-3 else 1.4
    u = (1 - k) * d if S['prm'].get('loop') else lt
    ridge(S, 'storm', t, 1.6)
    lightning(S, u, 2.2, 0.25)
    j = S['jet']
    p = at(RIDGE, lerp(-30, -4, u / 1.6), lerp(17, 13, u / 1.6), lerp(28.0, 24.0, u / 1.6))
    j.location = p
    j.rotation_euler = (-0.3 + 0.1 * math.sin(u * 5), -0.1, PI - 0.35)
    for i, dbr in enumerate(S['debris']):                                                                        # leaves and branches torn out
        ph = (u * 1.2 + rnd(i, 1)) % 1.0
        dbr.location = (p[0] + 4 + 6 * rnd(i, 2) - 8 * ph * rnd(i, 3), p[1] - 6 + 8 * rnd(i, 4), p[2] - 3 + 6 * ph - 6 * ph * ph + 2 * rnd(i, 5))
        dbr.rotation_euler = (u * 7 * rnd(i, 6), u * 5, u * 3 * rnd(i, 7))
    key(S, RIDGE, (0, -6, 26), (p[0], p[1], p[2]), 30000, 'B8C8E0')
    shoot(S, RIDGE, (lerp(6.0, 5.0, u / 1.6), lerp(-9.0, -8.0, u / 1.6), lerp(17.0, 16.0, u / 1.6)), (lerp(-15, -8, u / 1.6), 15, 22.5), 30, roll=-0.08)


def seat_pin(S, k, t, lt):
    """Inside the broken cabin: her face from above, eyes snapping open under a toppled seat, green light and rain
    through the torn roof. She pushes at the seat."""
    S['cabin'].location = CABIN
    sky(S, 'cabin')
    wake = sm((lt - 0.25) / 0.3)
    h = put(S, S['her'], 0.0, -0.4, 0.3, 0.0, P('stand', aR=(lerp(0.3, 1.6, wake), 0.3, lerp(0.5, 1.4, wake)), aL=(0.2, 0.4, 0.6),
                                                head=(0.1, lerp(0.4, 0.15, wake))), 'shut' if wake < 0.5 else 'wide', pitch=-PI / 2, o=CABIN)
    h.jawv = 0.25 * wake
    S['fallen'].location = at(CABIN, 0.1, -0.4 + 0.9, 0.95 + 0.04 * math.sin(lt * 14) * wake)
    S['fallen'].rotation_euler = (0.5, 0.2, 0.3)
    hp = head(S, S['her'])
    S['cabl'].location = at(CABIN, 0.6, 2.0, 3.6)
    S['cabl'].rotation_euler = (0.6, 0.2, 0)
    S['cabl'].data.energy = 600
    key(S, (0, 0, 0), (hp[0] + 1.0, hp[1] + 1.4, hp[2] + 2.4), hp, 160, 'C8F0C0')
    shoot(S, (0, 0, 0), (hp[0] - 0.25, hp[1] - lerp(0.9, 0.75, k), hp[2] + lerp(1.6, 1.35, k)), (hp[0], hp[1] + 0.05, hp[2]), 30, roll=0.2)


def wreck_wide(S, k, t, lt):
    """The broken fuselage in the trees on the slope in the rain, its nose gone; she lowers herself out of the open end."""
    ridge(S, 'rain', t, 1.0)
    u = sm(lt / 1.2)
    put(S, S['her'], lerp(-0.4, -0.9, u), lerp(1.9, 1.3, u), lerp(1.0, 0.3, u), PI + 0.6,
        blend(P('reach', aL=(2.2, 0.4, 0.3), lean=0.4), P('sit', aR=(1.2, -0.1, 2.2, 0.5), lean=0.2), u), 'pain')
    key(S, RIDGE, (-8, -10, 9), (0, 2, 2), 3000, 'C8D8D0')
    shoot(S, RIDGE, (lerp(-9.5, -8.5, k), lerp(-12, -11, k), lerp(2.4, 3.2, k)), (0.8, 2.4, 2.4), 24)


def wing_torn(S, k, t, lt):
    """Low along the torn wing in the ferns, metal bent, insulation hanging from its root; Rook drops onto it out of the
    rain and folds his wings."""
    ridge(S, 'rain', t, 0.8)
    u = sm(lt / 1.0)
    p = on_wing(-2.4, 0.0)
    fl = math.sin(lt * 14) * (1 - u)
    put(S, S['rook'], 0, 0, 0, 0.4 + 0.8 * (1 - u), blend(P('up', aL=(2.6, 0.9 + 0.5 * fl, 0.1), aR=(2.6, 0.9 + 0.5 * fl, 0.1)), P('cross'), u), 'low',
        o=(p[0], p[1], p[2] + lerp(4.0, 0.0, u)))
    key(S, RIDGE, (-8, -9, 6), (WROOT[0] - 2, WROOT[1], 2), 2400, 'C8D8D0')
    w0 = on_wing(0.4, 0.0)
    shoot(S, (0, 0, 0), (w0[0] + lerp(1.8, 1.4, k), w0[1] - lerp(4.4, 3.8, k), w0[2] + 0.5), (p[0] - 0.3, p[1], p[2] + 1.6), 24)


# ---------------------------------------------------------------- doubt
def rook_doubt(S, k, t, lt):
    """Rook on the wing in the rain, the broken fuselage behind him; his brim drops over his eyes."""
    ridge(S, 'rain', t, 0.8)
    p = on_wing(-2.4, 0.0)
    drop = sm((lt - 0.7) / 0.3)
    put(S, S['rook'], 0, 0, 0, 0.6, P('cross', head=(0.1 + 0.15 * drop, 0.15)), 'low', o=p)
    S['hat_tip'] = 0.9 * drop
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 2, h[1] - 3, h[2] + 2), h, 700, 'C8D8D0')
    shoot(S, (0, 0, 0), (h[0] - lerp(1.6, 1.3, k), h[1] - lerp(3.6, 3.1, k), h[2] - 0.1), (h[0] + 0.2, h[1], h[2] - 0.35), 34)


# ---------------------------------------------------------------- alone
def hands_hold(S, k, t, lt):
    """Close on two hands on a seat's armrest in the dim cabin: his is still, hers closes round it and holds on."""
    S['cabin'].location = CABIN
    sky(S, 'cabin')
    S['cabin'].rotation_euler = (0, 0, 0)
    arm = at(CABIN, 0.85 - 0.46, -3.4 + 1.3 * 2 + 0.05, 0.68)
    S['hand_him'].place((arm[0], arm[1] - 0.05, arm[2] + 0.05), (0, 0, PI / 2 + 0.1))
    S['hand_him'].grip(0.25)
    g_ = sm(lt / 1.1)
    S['hand_her'].place((arm[0] - lerp(0.55, 0.12, g_), arm[1] - 0.05, arm[2] + 0.12), (0.15, 0, -PI / 2 + 0.2))
    S['hand_her'].grip(lerp(0.1, 0.75, g_))
    S['cabl'].location = at(CABIN, -0.3, -1.0, 2.2)
    S['cabl'].rotation_euler = (0.5, 0, 0)
    S['cabl'].data.energy = 120
    key(S, (0, 0, 0), (arm[0] - 1.0, arm[1] - 1.4, arm[2] + 1.2), arm, 90, 'FFD0A0')
    shoot(S, (0, 0, 0), (arm[0] - lerp(0.9, 0.7, k), arm[1] - lerp(1.8, 1.5, k), arm[2] + 0.55), (arm[0] - 0.15, arm[1], arm[2] + 0.05), 40)


def rook_hatoff(S, k, t, lt):
    """Rook beside the fuselage in the rain takes off his hat and holds it to his chest, head bowed."""
    ridge(S, 'rain', t, 0.6)
    u = sm(lt / 0.8)
    put(S, S['rook'], 0.2, -0.6, 0.0, -0.2, blend(P('hat'), P('stand', aR=(0.9, -0.2, 1.6, 0.8), head=(0.45, 0.0)), u), 'sad')
    S['hat_off'] = u
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 2, h[1] - 3, h[2] + 2), h, 600, 'C8D8D0')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.4, 1.2, k), h[1] - lerp(4.4, 3.8, k), h[2] - 0.4), (h[0], h[1], h[2] - 0.7), 34)


def man_beside(S, k, t, lt):
    """Under the wreck's edge she lies propped on one elbow, turned to the man lying near her; she reaches out, he does
    not move, and she lowers her hand."""
    ridge(S, 'rain', t, 0.5)
    lie(S, S['man'], MAN[0], MAN[1], PI * 0.6, P('stand', aL=(0.1, 0.3, 0.3), aR=(0.1, 0.3, 0.2), head=(0.1, 0.6)), 'shut')
    reach = sm(lt / 0.6) * (1 - sm((lt - 1.0) / 0.4))
    put(S, S['her'], MAN[0] - 1.6, MAN[1] - 0.4, 0.42, PI * 0.42, P('sit', aR=(lerp(0.6, 1.6, reach), 0.1, lerp(1.4, 0.2, reach)), aL=(0.8, 0.5, 1.6), lean=0.35,
                                                                    lL=(1.3, 1.2), lR=(1.2, 0.9), head=(0.3, 0.0)), 'sad')
    h = head(S, S['her'])
    m = head(S, S['man'])
    mid = ((h[0] + m[0]) / 2, (h[1] + m[1]) / 2, (h[2] + m[2]) / 2)
    key(S, (0, 0, 0), (mid[0] - 2, mid[1] - 3, mid[2] + 3), mid, 500, 'C8D8D0')
    shoot(S, (0, 0, 0), (mid[0] + lerp(1.2, 0.9, k), mid[1] - lerp(4.0, 3.4, k), mid[2] + 1.4), (mid[0], mid[1], mid[2] - 0.3), 26)


def her_alone(S, k, t, lt):
    """She sits alone against a root by the fuselage in the rain, knees up; the camera pulls back to show how alone."""
    ridge(S, 'rain', t, 0.6)
    her_spot(S, 'sad', P('sit', aL=(0.9, -0.1, 1.7, 1.0), aR=(0.9, -0.1, 1.7, 1.0), lL=(1.0, 2.1), lR=(1.0, 2.1), lean=0.05, head=(0.25, 0.1)))
    h = head(S, S['her'])
    key(S, (0, 0, 0), (h[0] - 2, h[1] - 3, h[2] + 3), h, 500, 'C8D8D0')
    shoot(S, (0, 0, 0), (h[0] - lerp(1.0, 2.2, k), h[1] - lerp(3.2, 6.0, k), h[2] + lerp(0.3, 1.2, k)), (h[0], h[1], h[2] - 0.4), 30)


# ---------------------------------------------------------------- thirst
def thirst_face(S, k, t, lt):
    """Sun through the canopy: close on her face, squinting, wiping her dry lips with a fingertip."""
    ridge(S, 'day', t, 0.2)
    wipe = 0.5 + 0.5 * math.sin(lt * 5) if lt > 0.4 else 0.0
    her_spot(S, 'squint', P('sit', aR=(lerp(1.0, 1.25, wipe), -0.3, 2.3, 0.6), lean=-0.2, head=(-0.15, 0.1)))
    h = head(S, S['her'])
    key(S, (0, 0, 0), (h[0] + 1.5, h[1] - 2, h[2] + 3), h, 400, 'FFF0C8')
    shoot(S, (0, 0, 0), (h[0] - 0.25, h[1] - lerp(1.9, 1.6, k), h[2] + 0.05), (h[0], h[1], h[2] - 0.02), 40)


def wing_pov(S, k, t, lt):
    """Over her shoulder, down the slope: the broken wing, its torn root stuffed with pale insulation; Rook on the wing
    points at it."""
    ridge(S, 'day', t, 0.2)
    her_spot(S, 'tired', P('sit', head=(0.3, -0.45)))
    p = on_wing(-1.6, 0.2)
    put(S, S['rook'], 0, 0, 0, -1.3, P('point', aR=(lerp(0.4, 1.2, sm(lt / 0.6)), 0.4, 0.1), head=(0.3, -0.3)), 'calm', o=p)
    h = head(S, S['her'])
    w0 = on_wing(0.3, 0.0)
    key(S, (0, 0, 0), (w0[0] + 1, w0[1] - 3, w0[2] + 3), w0, 500, 'FFF0C8')
    shoot(S, (0, 0, 0), (h[0] + 0.9, h[1] + lerp(2.4, 2.0, k), h[2] + 1.3), (w0[0] - 0.8, w0[1], w0[2] + 0.4), 26)


# ---------------------------------------------------------------- sponge
def rook_squeeze(S, k, t, lt):
    """Rook at the wing root pulls out a tuft of insulation and squeezes it; it springs back; he looks over at her."""
    ridge(S, 'day', t, 0.2)
    p = on_wing(-0.6, 0.1)
    sq = math.sin(min(lt, 1.2) * 7) * 0.5 + 0.5 if lt > 0.35 else 0.0
    look = sm((lt - 1.0) / 0.3)
    put(S, S['rook'], 0, 0, 0, -1.2 + 0.9 * look, P('stand', aR=(1.0, -0.2, 1.0, 0.3), aL=(0.9, 0.2, 1.1, 0.3), head=(0.35 - 0.3 * look, 0.0)),
        'shocked' if look > 0.5 else 'calm', o=p)
    hd = wpos(S['rook'].hands[1])
    S['tuft'].location = (hd[0], hd[1] - 0.25, hd[2] - 0.15)
    s = 1.0 - 0.45 * sq
    S['tuft'].scale = (s, s, s)
    S['insul'][5].scale = (0.4, 0.4, 0.4)
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] + 1, h[1] - 3, h[2] + 2), h, 500, 'FFF0C8')
    shoot(S, (0, 0, 0), (h[0] - lerp(1.6, 1.3, k), h[1] - lerp(3.0, 2.6, k), h[2] - 0.4), (h[0] + 0.1, h[1] - 0.2, h[2] - 0.65), 32)


def elbow_crawl(S, k, t, lt):
    """She drags herself on her elbows over roots and leaves toward the wing, legs trailing, face set."""
    ridge(S, 'day', t, 0.2)
    pull = (lt * 1.4) % 1.0
    x = lerp(SPOT[0] - 0.6, WROOT[0] + 1.2, k)
    y = lerp(SPOT[1] - 0.3, WROOT[1] + 0.4, k)
    dr = math.atan2(WROOT[1] - SPOT[1], WROOT[0] - SPOT[0])
    yaw = dr + PI / 2
    a = math.sin(pull * 2 * PI)
    put(S, S['her'], x, y, 0.42, yaw, P('stand', aL=(2.4 + 0.4 * a, 0.3, 1.2 - 0.6 * a), aR=(2.4 - 0.4 * a, 0.3, 1.2 + 0.6 * a), head=(-0.9, 0.0),
                                       lL=(0.0, 0.2), lR=(0.0, 0.1)), 'hard', pitch=PI / 2 - 0.25)
    h = head(S, S['her'])
    fw = (math.cos(dr), math.sin(dr))
    key(S, (0, 0, 0), (h[0] + 2.0 * fw[0], h[1] + 2.0 * fw[1] - 1.0, h[2] + 2), h, 400, 'FFF0C8')
    shoot(S, (0, 0, 0), (h[0] + lerp(2.4, 2.0, k) * fw[0] + 0.6 * fw[1], h[1] + lerp(2.4, 2.0, k) * fw[1] - 0.6 * fw[0], h[2] + 0.3),
          (h[0], h[1], h[2] - 0.15), 30)


def tuft_pull(S, k, t, lt):
    """Close on her hand pulling tufts of insulation out of the torn wing root and rolling them into little balls."""
    ridge(S, 'day', t, 0.2)
    w0 = on_wing(0.25, -0.2)
    pull = sm((lt % 0.9) / 0.6)
    S['hand_her'].place((w0[0] + 0.25 + 0.3 * pull, w0[1] - 0.25, w0[2] + 0.1), (0.2, 0.2, PI / 2 + 0.9))
    S['hand_her'].grip(lerp(0.3, 0.85, pull))
    hd = S['hand_her'].root.location
    S['tuft'].location = (hd[0] - 0.12, hd[1] - 0.05, hd[2] - 0.04)
    S['tuft'].scale = (0.7, 0.7, 0.7)
    for i, b in enumerate(S['balls'][:3]):
        b.location = (w0[0] + 0.7 + 0.25 * i, w0[1] - 0.6, w0[2] - 0.1)
    S['insul'][3].scale = S['insul'][4].scale = (1 - 0.4 * pull,) * 3
    key(S, (0, 0, 0), (w0[0] + 1.5, w0[1] - 2, w0[2] + 2), w0, 260, 'FFF0C8')
    shoot(S, (0, 0, 0), (w0[0] + lerp(1.1, 0.9, k), w0[1] - lerp(1.6, 1.3, k), w0[2] + 0.75), (w0[0] + 0.3, w0[1] - 0.2, w0[2] + 0.05), 34)


def rook_nod(S, k, t, lt):
    """Rook on the wing taps his beak, then nods slowly toward her: she worked it out first."""
    ridge(S, 'day', t, 0.2)
    p = on_wing(-1.4, 0.1)
    tap = lt < 0.8
    nod = 0.25 * math.sin((lt - 0.8) * 6) if not tap else 0.0
    put(S, S['rook'], 0, 0, 0, 0.9, P('tap', aR=(1.25, -0.25, 2.2 + 0.15 * math.sin(lt * 18), 0.6)) if tap else P('cross', head=(0.15 + nod, 0.4)), 'soft', o=p)
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] + 1, h[1] - 3, h[2] + 1), h, 500, 'FFF0C8')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.0, 0.8, k), h[1] - lerp(3.0, 2.6, k), h[2] - 0.9), (h[0], h[1], h[2] - 0.3), 30)


# ---------------------------------------------------------------- rain
def rain_arrives(S, k, t, lt):
    """Rain sweeps over the ridge, the trees thrash; Rook hunches on the fuselage roof; she holds the balls of
    insulation up into the rain."""
    ridge(S, 'rain', t, 2.0)
    lightning(S, t, 3.0, 0.4)
    put(S, S['her'], WROOT[0] + 1.0, WROOT[1] + 0.7, 0.35, 0.4, P('sit', aR=(2.3, 0.2, 0.4), aL=(2.1, 0.3, 0.5), head=(-0.5, 0.0), lean=-0.2), 'squint')
    for i, b in enumerate(S['balls'][:2]):
        hd = wpos(S['her'].hands[i])
        b.location = (hd[0], hd[1] - 0.1, hd[2] + 0.12)
    roof = wpos(S['fuse'], (-1.0, 0, 1.3))
    put(S, S['rook'], 0, 0, 0, 0.3, P('cross', head=(0.35, 0.0), lean=0.3), 'low', o=roof)
    S['hat_tip'] = 0.6
    key(S, RIDGE, (-6, -9, 8), (-1, 0, 1.5), 1800, 'C8D8D0')
    shoot(S, RIDGE, (lerp(-7.5, -6.5, k), lerp(-9.5, -8.5, k), lerp(6.0, 5.4, k)), (0.0, 0.8, 1.6), 24)


def tuft_drink(S, k, t, lt):
    """Close on her face as she lifts a soaked ball of insulation to her lips and takes one sip, water dripping."""
    ridge(S, 'rain', t, 0.6)
    lift = sm(lt / 0.6)
    put(S, S['her'], WROOT[0] + 1.0, WROOT[1] + 0.7, 0.35, 0.4, P('sit', aR=(lerp(0.9, 1.3, lift), -0.3, lerp(1.4, 2.35, lift), 0.6), head=(0.05, 0.0), lean=-0.1),
        'shut' if lt > 0.7 else 'tired')
    hd = wpos(S['her'].hands[1])
    b = S['balls'][0]
    b.location = (hd[0], hd[1] - 0.12, hd[2] + 0.08)
    for i, d in enumerate(S['drips']):
        ph = (t * 1.5 + i / 6) % 1.0
        d.location = (hd[0] + 0.04 * (i % 3 - 1), hd[1] - 0.12, hd[2] - 0.02 - 0.7 * ph)
    h = head(S, S['her'])
    key(S, (0, 0, 0), (h[0] - 1, h[1] - 2, h[2] + 2), h, 300, 'D0E0D8')
    shoot(S, (0, 0, 0), (h[0] + 0.3, h[1] - lerp(1.8, 1.65, k), h[2] + 0.05), (h[0], h[1], h[2] - 0.12), 42)


# ---------------------------------------------------------------- nobody finds the wreck
def aerial_canopy(S, k, t, lt):
    """Very high above: endless green ridges under drifting cloud; nothing shows of the wreck under the canopy."""
    S['range'].location = RANGE
    sky(S, 'high')
    for i, c in enumerate(S['clouds']):
        c.location = (-200 + 400 * rnd(i, 111) + 4 * t, 160 + 200 * rnd(i, 112), 95 + 30 * rnd(i, 113))
    shoot(S, RANGE, (lerp(-40, -20, k), -200, 240), (lerp(0, 15, k), 60, 30), 26, roll=0.04)


def rook_lookout(S, k, t, lt):
    """Rook on the top of the tallest tree, a wing over his eyes, scanning the ridges; nothing; his shoulders drop."""
    S['range'].location = RANGE
    sky(S, 'high')
    co = S['rco']
    i = np.argmin((co[:, 0] - 0) ** 2 + (co[:, 1] + 60) ** 2)
    p = at(RANGE, 0, -60, co[i, 2] + 9)
    S['lookout_crown'].location = (p[0], p[1], p[2] - 0.9)
    drop = sm((lt - 0.8) / 0.4)
    scan = 0.5 * math.sin(lt * 2.0)
    put(S, S['rook'], 0, 0, 0, 0.0, P('stand', aR=(2.4, -0.4, 2.0, 0.4), head=(-0.05, scan)) if drop < 0.5 else P('stand', head=(0.35, 0.0), lean=0.15), 'calm' if drop < 0.5 else 'sad', o=p)
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] + 2, h[1] - 3, h[2] + 1), h, 500, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.6, 1.3, k), h[1] - lerp(4.2, 3.6, k), h[2] + 0.9), (h[0], h[1], h[2] - 1.1), 30)


# ---------------------------------------------------------------- calm
def night_wreck(S, k, t, lt):
    """Night: the wreck a dark shape in the trees, fireflies drifting, she lies small by the fuselage."""
    ridge(S, 'night', t, 0.2)
    lie(S, S['her'], LIE[0], LIE[1], 0.1, face='shut')
    flies(S, t, LIE[0] + 1, LIE[1] + 1, g(*LIE) + 0.6)
    key(S, RIDGE, (-4, -6, 6), (LIE[0], LIE[1], 1), 900, '8AA8D8')
    shoot(S, RIDGE, (lerp(-5.5, -4.6, k), lerp(-8.0, -7.0, k), lerp(3.0, 2.6, k)), (1.0, 1.8, 1.6), 26)


def calm_face(S, k, t, lt):
    """Close on her face at night: eyes closed, breathing slowly and deliberately, the fear going out of it."""
    ridge(S, 'night', t, 0.2)
    lie(S, S['her'], LIE[0], LIE[1], 0.1, face='shut')
    br = 0.5 + 0.5 * math.sin(lt * 2.4)
    S['her'].body.scale = (1 + 0.03 * br, 1 + 0.05 * br, 1)
    h = head(S, S['her'])
    key(S, (0, 0, 0), (h[0] - 1, h[1] - 1, h[2] + 2.5), h, 220, '7A98D8')
    shoot(S, (0, 0, 0), (h[0] + 0.2, h[1] - lerp(0.9, 0.8, k), h[2] + lerp(1.35, 1.2, k)), (h[0], h[1], h[2]), 40, roll=0.3)


def rook_vigil(S, k, t, lt):
    """Rook sits quietly beside her on a root, hat in his lap, keeping watch while she rests."""
    ridge(S, 'night', t, 0.2)
    lie(S, S['her'], LIE[0], LIE[1], 0.1, face='shut')
    sit(S, S['rook'], LIE[0] - 1.4, LIE[1] + 1.0, -0.6, P('sit', aR=(0.7, -0.1, 1.2), aL=(0.7, -0.1, 1.2), head=(0.35, lerp(-0.5, -0.2, k))), 'soft', dz=0.2)
    S['hat_tip'] = 0.5
    flies(S, t, LIE[0] - 0.5, LIE[1] + 3, g(*LIE) + 1.0, 8)
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 1, h[1] - 3, h[2] + 2), h, 400, '9AB8E8')
    shoot(S, (0, 0, 0), (h[0] + lerp(0.6, 0.4, k), h[1] - lerp(5.6, 5.0, k), h[2] + 0.4), (h[0] + 0.8, h[1] + 0.2, h[2] - 1.2), 28)


# ---------------------------------------------------------------- found
def officer_trees(S, k, t, lt):
    """Dawn mist in the trees: a man in a khaki uniform and cap pushes through the leaves and stops dead."""
    ridge(S, 'dawn', t, 0.2)
    u = sm(lt / 0.9)
    x, y = lerp(-6.4, -4.4, u), lerp(6.6, 3.8, u)
    pose = walk(lt) if u < 0.95 else P('stand', aL=(0.6, 0.6, 0.4), aR=(0.6, 0.6, 0.4), lean=-0.15)
    put(S, S['officer'], x, y, 0.0, 0.84, pose, 'wide' if u > 0.8 else 'calm')
    lie(S, S['her'], LIE[0], LIE[1], 0.1, face='tired')
    h = head(S, S['officer'])
    key(S, (0, 0, 0), (h[0] + 3, h[1] - 2, h[2] + 2), h, 700, 'FFC890')
    shoot(S, (0, 0, 0), (LIE[0] + lerp(1.2, 1.0, k), LIE[1] - lerp(1.6, 1.3, k), g(*LIE) + 1.0), (h[0], h[1], h[2] - 0.6), 26)


def walk(lt):
    return K.walk(lt)


def officer_ghost(S, k, t, lt):
    """Close on the officer's face: eyes wide, he steps back, then points and shouts down the hill."""
    ridge(S, 'dawn', t, 0.2)
    back = sm(lt / 0.4)
    pt = sm((lt - 0.5) / 0.3)
    o = put(S, S['officer'], -4.4 - 0.3 * back, 3.8 + 0.3 * back, 0.0, 0.84,
            blend(P('stand', aL=(0.6, 0.6, 0.4), aR=(0.6, 0.6, 0.4), lean=-0.2), P('point', aR=(1.45, 0.6, 0.05), head=(0.0, 0.8)), pt), 'wide')
    o.jawv = 0.7 * pt
    h = head(S, o)
    key(S, (0, 0, 0), (h[0] + 2, h[1] - 2, h[2] + 1), h, 500, 'FFC890')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.5, 1.2, k) + 0.4, h[1] - lerp(1.3, 1.1, k) + 0.3, h[2] + 0.05), (h[0], h[1], h[2] - 0.05), 38)


def rook_brim(S, k, t, lt):
    """Rook lifts his brim with one finger, eyes wide, then lets out a breath."""
    ridge(S, 'dawn', t, 0.2)
    p = on_wing(-2.0, 0.0)
    up = sm(lt / 0.5)
    put(S, S['rook'], 0, 0, 0, 0.5, P('hat', head=(-0.1, 0.0)) if up < 0.9 else P('stand', aR=(0.3, 0.1, 0.5), head=(0.0, 0.2)), 'shocked' if lt < 1.0 else 'soft', o=p)
    S['hat_tip'] = -0.5 * up
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] + 2, h[1] - 3, h[2] + 1), h, 600, 'FFC890')
    shoot(S, (0, 0, 0), (h[0] + lerp(0.5, 0.4, k), h[1] - lerp(2.8, 2.4, k), h[2] - 0.1), (h[0], h[1], h[2] - 0.15), 36)


def carry(S, x, y, yaw, lt, n=4):
    """Rescuers carrying her on canvas slung between two sticks, one at each corner."""
    c, s = math.cos(yaw), math.sin(yaw)
    hm = S['hammock']
    hm.location = gp(x, y, 0.35)
    hm.rotation_euler = (0, 0, yaw)
    for i, rig in enumerate(S['crew'][:n]):
        e = -1 if i < 2 else 1
        off = 2.4 * e
        side = (0.42 if i % 2 else -0.42)
        px, py = x + off * c - side * s, y + off * s + side * c
        pose = K.walk(lt + 0.3 * i, 1.2)
        pose['aL'], pose['aR'] = (0.5, 0.05, 0.9, 0.0), (0.5, 0.05, 0.9, 0.0)
        put(S, rig, px, py, 0.0, yaw + PI / 2, pose, 'hard')
    her = put(S, S['her'], x - 1.4 * c, y - 1.4 * s, 1.85, yaw - PI / 2, P('stand', aL=(0.2, 0.2, 0.6), aR=(0.3, 0.2, 0.9), head=(0.3, 0.5)), 'tired',
              pitch=-PI / 2)


def carry_down(S, k, t, lt):
    """Rescuers carry her down the slope in the morning light; she turns her head to the sky."""
    ridge(S, 'morning', t, 0.3)
    x, y = lerp(-1.0, -3.4, k), lerp(-1.0, -5.0, k)
    carry(S, x, y, 0.9, lt)
    p = gp(x, y, 1.6)
    key(S, (0, 0, 0), (p[0] + 3, p[1] - 4, p[2] + 4), p, 1200, 'FFE8C0')
    shoot(S, (0, 0, 0), (p[0] + 5.6, p[1] - 5.2, p[2] + 1.0), (p[0], p[1], p[2] - 0.5), 24)


# ---------------------------------------------------------------- the end
def rook_wreck(S, k, t, lt):
    """Rook alone by the empty fuselage puts his hat back on and looks at the wreck a long moment."""
    ridge(S, 'morning', t, 0.3)
    on = sm(lt / 0.7)
    put(S, S['rook'], 0.0, -0.8, 0.0, -2.4, P('hat') if on < 0.95 else P('stand', head=(0.15, 0.0)), 'sad')
    S['hat_off'] = 1 - on
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 2, h[1] - 4, h[2] + 3), h, 700, 'FFE8C0')
    shoot(S, (0, 0, 0), (h[0] - lerp(2.2, 3.4, k), h[1] - lerp(4.0, 6.0, k), h[2] + lerp(0.2, 0.8, k)), (h[0] + 1.5, h[1] + 1.5, h[2] - 0.2), 30)


def carry_light(S, k, t, lt):
    """The carry party goes down the jungle path into sunlight, small among the giant trees."""
    ridge(S, 'morning', t, 0.3)
    x, y = lerp(-4.5, -6.5, k), lerp(-7.0, -11.0, k)
    carry(S, x, y, 1.1, lt)
    p = gp(x, y, 1.5)
    key(S, RIDGE, (x - 4, y - 8, 8), (x, y, 1), 2000, 'FFE8C0')
    shoot(S, (0, 0, 0), (p[0] + 3.0, p[1] + lerp(9.0, 8.0, k), p[2] + lerp(4.0, 5.0, k)), (p[0] - 1, p[1] - 3, p[2] - 0.6), 26)


def signoff(S, k, t, lt):
    """Rook on the wing picks up a loose rivet, turns it in the light, pockets it and tips his hat."""
    ridge(S, 'morning', t, 0.3)
    p = on_wing(-2.0, 0.0)
    ph = lt
    if ph < 0.6:
        pose = P('stand', aR=(1.2, -0.2, 1.3, 0.4), head=(0.3, 0.0))
    elif ph < 1.0:
        pose = P('stand', aR=(0.2, 0.3, 0.6), head=(0.0, 0.0))
    else:
        pose = P('hat')
    put(S, S['rook'], 0, 0, 0, 0.4, pose, 'soft', o=p)
    hd = wpos(S['rook'].hands[1])
    if ph < 0.6:
        S['rivet'].location, S['rivet'].rotation_euler = (hd[0], hd[1] - 0.12, hd[2] + 0.06), (lt * 6, 0.4, 0)
    S['hat_tip'] = 0.4 if ph > 1.0 else 0.0
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] + 2, h[1] - 4, h[2] + 2), h, 700, 'FFE8C0')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.5, 1.2, k), h[1] - lerp(4.6, 4.0, k), h[2] - 0.4), (h[0], h[1], h[2] - 0.55), 30)


SHOTS3D = {f.__name__: f for f in (
    crash_ridge, seat_pin, wreck_wide, wing_torn, rook_doubt, hands_hold, rook_hatoff, man_beside, her_alone, thirst_face,
    wing_pov, rook_squeeze, elbow_crawl, tuft_pull, rook_nod, rain_arrives, tuft_drink, aerial_canopy, rook_lookout,
    night_wreck, calm_face, rook_vigil, officer_trees, officer_ghost, rook_brim, carry_down, rook_wreck, carry_light,
    signoff)}


# ================================================================ long-form extension (16:9 full case file)
# The Short's slope, wreck, broken cabin, jet and ridges stay exactly as they were. New for the full case, each set built at
# its own origin far from the Short's and shown only in its own shots: a trading floor in Madrid, an office in Vietnam with a
# ceiling fan, a small airport apron with palms where the little jet waits, the inside of the jet in flight, a hospital room,
# a plain funeral hall, a city park in autumn and a writing desk at a window. New figures: Willem, a colleague, a man in an
# orange jacket, two bearers, two children. New shots on the Short's slope as well: the suitcase and the trousers, her rules,
# the long wait between sips, the insects, the move away from the wreck, the sky through the gap in the trees, the man in
# orange, the men with the list. Everything is generic: no airline, bank or hospital markings, no flags, logos or lettering,
# no real building or room is modelled, the skyline is plain boxes, and nobody's likeness is attempted. The dead are shown
# only as a still hand, the back of a head and a closed coffin under flowers.
STILLS = {}


# Building with bpy.ops gets slower with every object already in the scene (the Short alone takes over a minute to build and
# this file more than doubles the object count). The new objects are made straight from bmesh with the same shapes, materials
# and bevels the kit gives them. The Short's own sets are still built by the kit's operators, exactly as before.
import bmesh  # noqa: E402

_ops_add, _ops_empty = K.add, K.empty


def _link(o, loc, rot, parent):
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    return o


def fast_add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'plane':
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=kw.get('size', 2.0) / 2)
    elif kind == 'ico_sphere':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('subdivisions', 2), radius=kw.get('radius', 1.0))
    elif kind == 'cylinder':
        r = kw.get('radius', 1.0)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=r, radius2=r, depth=kw.get('depth', 2.0))
    elif kind == 'cone':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius1', 1.0),
                              radius2=kw.get('radius2', 0.0), depth=kw.get('depth', 2.0))
    else:
        bm.free()
        return _ops_add(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
    me = bpy.data.meshes.new(kind)
    bm.to_mesh(me)
    bm.free()
    o = _link(bpy.data.objects.new(kind, me), loc, rot, parent)
    o.scale = scale
    me.materials.append(K.mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    return o


def fast_empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    return _link(bpy.data.objects.new('empty', None), loc, rot, parent)


SETPOS = dict(office=(0.0, -3000.0, 0.0), saigon=(400.0, -3000.0, 0.0), study=(800.0, -3000.0, 0.0), apron=(1400.0, -3000.0, 0.0),
              flight=(2200.0, -3000.0, 0.0), ward=(2600.0, -3000.0, 0.0), chapel=(3000.0, -3000.0, 0.0), park=(3600.0, -3000.0, 0.0))
SKIES.update(
    office=('C8D4E0', '6A7C94', 0.9, 0.0, 'FFFFFF', (0, 0, 1)),
    saigon=('F0D8A8', 'A89060', 0.9, 0.0, 'FFFFFF', (0, 0, 1)),
    apron=('F0E8CC', '74AED2', 1.25, 3.6, 'FFF0D0', (0.35, -0.55, 0.75)),
    flight=('8A949C', '50585E', 0.7, 0.0, 'FFFFFF', (0, 0, 1)),
    ward=('DCE8F0', '8AA4B8', 0.85, 0.0, 'FFFFFF', (0, 0, 1)),
    wardnight=('141C2C', '05070E', 0.35, 0.0, 'FFFFFF', (0, 0, 1)),
    chapel=('5A5448', '2A2620', 0.45, 0.0, 'FFFFFF', (0, 0, 1)),
    park=('F2E6CC', '78B0DC', 1.25, 3.4, 'FFE8C0', (0.45, -0.5, 0.6)),
    study=('F0A878', '3A4670', 0.6, 0.0, 'FFFFFF', (0, 0, 1)),
    dusk=('E89A6A', '3C4E78', 0.7, 1.4, 'FFB080', (-0.7, -0.4, 0.3)))
CAMFILL.update(desk_trade=140, pasje_desk=140, apron_wide=120, apron_meet=160, apron_stairs=160, rook_apron=220, cabin_flight=200,
               cabin_drop=180, hands_grab=120, belt_empty=140, her_looks=170, trousers=220, man_talks=200, her_resolve=160, sip_wait=200,
               swat=180, move_away=200, sky_gap=0, orange_man=200, orange_gone=180, men_arrive=220, list_point=120, ward_bed=160,
               jaime_phone=160, funeral_aisle=260, funeral_close=160, funeral_rook=260, walk_again=200, desk_back=160, family_walk=140,
               return_ridge=220, writing=150)
HOST |= {'desk_trade', 'apron_wide', 'rook_apron', 'cabin_flight', 'sip_wait', 'men_arrive', 'ward_bed', 'funeral_rook', 'family_walk',
         'return_ridge', 'desk_back'}


def box(col, loc, scale, par=None, rot=(0, 0, 0), **kw):
    return add('cube', col, loc, rot=rot, scale=scale, size=1, parent=par, **kw)


def SP(name, x, y, z=0.0):
    o = SETPOS[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def facing(dx, dy):
    """Yaw that turns a rig (which faces -Y at yaw 0) to look along (dx, dy)."""
    return math.atan2(dx, -dy)


def room(r, w, d, hh, wall, floor):
    box(floor, (0, 0, -0.1), (w, d, 0.2), r, rough=0.7)
    box(wall, (0, d / 2, hh / 2), (w, 0.2, hh), r)
    for s in (-1, 1):
        box(wall, (s * w / 2, 0, hh / 2), (0.2, d, hh), r)
    box('2A2A30', (0, d / 2 - 0.12, 0.2), (w, 0.06, 0.4), r)                                 # skirting


def chair(r, x, y, col='2E3440', yaw=0.0):
    c = empty((x, y, 0), r, (0, 0, yaw))
    box(col, (0, 0, 0.5), (0.9, 0.9, 0.14), c)
    box(col, (0, 0.45, 1.2), (0.9, 0.14, 1.3), c, rot=(-0.1, 0, 0))
    add('cylinder', '8A8E96', (0, 0, 0.25), radius=0.07, depth=0.5, vertices=6, parent=c, rough=0.4)
    add('cylinder', '8A8E96', (0, 0, 0.04), radius=0.42, depth=0.06, vertices=5, parent=c, rough=0.4)
    return c


def monitor(r, x, y, z, yaw, glow='7CE8A0', bars=True):
    m = empty((x, y, z), r, (0, 0, yaw))
    box('D8D2C4', (0, 0.25, 0.42), (0.95, 0.7, 0.8), m, rough=0.6)                             # a chunky tube monitor of the early nineties
    box('10161C', (0, -0.11, 0.44), (0.78, 0.03, 0.6), m, rough=0.2)
    box(glow, (0, -0.13, 0.44), (0.7, 0.02, 0.52), m, emit=1.6)
    if bars:
        for i in range(5):
            hh = 0.1 + 0.3 * rnd(i, int(x * 7 + y * 3) + 5)
            box('FFB000', (-0.26 + 0.13 * i, -0.15, 0.22 + hh / 2), (0.07, 0.01, hh), m, emit=2.5)
    box('C8C2B4', (0, 0.1, 0.02), (0.5, 0.4, 0.06), m, rough=0.6)
    return m


def desk(r, x, y, col='6A5238', w=3.4):
    box(col, (x, y, 1.05), (w, 1.3, 0.12), r, rough=0.5)
    box(col, (x, y - 0.5, 0.5), (w - 0.2, 0.08, 1.0), r, rough=0.6)
    for s in (-1, 1):
        box(col, (x + s * (w / 2 - 0.1), y, 0.5), (0.1, 1.2, 1.0), r, rough=0.6)


def bust(r, x, y, z, top, skin, hair, yaw=0.0):
    b = empty((x, y, z), r, (0, 0, yaw))
    box(top, (0, 0, 0.5), (0.7, 0.42, 1.0), b)
    add('ico_sphere', skin, (0, 0, 1.36), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=b)
    add('ico_sphere', hair, (0, 0.06, 1.45), radius=0.3, subdivisions=1, parent=b)
    return b


def tub(r, x, y, s=1.0):
    add('cylinder', '8A5A3A', (x, y, 0.35 * s), radius=0.4 * s, depth=0.7 * s, vertices=8, parent=r)
    for b in range(6):
        a = 2 * PI * b / 6
        add('cone', LEAF[b % 5], (x + 0.5 * s * math.cos(a), y + 0.5 * s * math.sin(a), 1.5 * s), rot=(0.7 * math.sin(a), -0.7 * math.cos(a), 0),
            scale=(1, 0.3, 1), radius1=0.4 * s, radius2=0.0, depth=2.0 * s, vertices=4, parent=r, rough=0.8)


# ---------------------------------------------------------------- new sets
def make_office(r):
    """A bank's trading floor in Madrid: rows of desks with tube monitors, tall windows, strip lights."""
    room(r, 22, 10, 6, 'B8BEC8', '4A5060')
    for i in range(5):
        x = -8 + 4 * i
        box('DCEBFA', (x, 4.86, 3.3), (3.0, 0.05, 3.4), r, emit=1.5)
        box('6A7080', (x, 4.84, 3.3), (0.1, 0.08, 3.4), r)
        box('6A7080', (x, 4.84, 3.3), (3.0, 0.08, 0.1), r)
    for x in (-6, 0, 6):
        box('F4F6FF', (x, 0, 5.9), (3.6, 0.5, 0.08), r, emit=3.0)
    desk(r, 0, 0.6)
    chair(r, 0, 1.75)
    monitor(r, -1.15, 0.75, 1.11, 0.55)
    monitor(r, 1.15, 0.75, 1.11, -0.55, 'F0D890')
    box('2A2A30', (0.1, 0.25, 1.14), (0.9, 0.3, 0.05), r)                                    # keyboard
    box('2A2A30', (-0.2, 0.75, 1.16), (0.4, 0.3, 0.1), r)                                    # telephone base
    for sx in (-6.2, 6.2):                                                                    # the neighbours' desks
        desk(r, sx, 1.4)
        chair(r, sx, 2.55)
        monitor(r, sx - 0.9, 1.5, 1.11, 0.4, 'F0D890')
        monitor(r, sx + 0.9, 1.5, 1.11, -0.4)
        box('E8E4D8', (sx, 1.0, 1.13), (0.5, 0.7, 0.04), r, rot=(0, 0, 0.3))
    bust(r, 6.2, 2.5, 0.35, 'E8E8E0', 'D8A880', '3A2A1E')
    for i in range(4):                                                                        # filing cabinets on the left wall
        box('7A8494', (-10.5, -3 + 1.3 * i, 1.4), (0.9, 1.2, 2.8), r, rough=0.4)
        for z in (0.6, 1.4, 2.2):
            box('C8CCD4', (-10.02, -3 + 1.3 * i, z), (0.03, 0.5, 0.08), r, rough=0.3)
    tub(r, 9.6, 3.6, 1.3)
    add('cylinder', 'F4F0E4', (3.0, 4.84, 4.9), rot=(PI / 2, 0, 0), radius=0.5, depth=0.08, vertices=14, parent=r)      # a plain wall clock
    box('1A1A1E', (3.0, 4.78, 5.05), (0.04, 0.03, 0.34), r)
    return {}


def make_saigon(r):
    """An office in Vietnam: warm walls, shuttered windows, a ceiling fan, a desk with a telephone."""
    room(r, 13, 9, 5.2, 'E0CC9C', '8A6A48')
    for x in (-3.4, 3.4):
        box('FFE6A8', (x, 4.36, 2.9), (2.2, 0.05, 2.8), r, emit=2.2)
        for i in range(9):
            box('3A6A4A', (x, 4.3, 1.7 + 0.3 * i), (2.3, 0.08, 0.14), r, rot=(0.5, 0, 0))
        for s in (-1, 1):
            box('2E5A3E', (x + s * 1.2, 4.3, 2.9), (0.14, 0.1, 3.0), r)
    hub = empty((0, 0.6, 4.7), r)
    add('cylinder', '5A4630', (0, 0, 0.25), radius=0.06, depth=0.5, vertices=6, parent=hub)
    add('cylinder', '5A4630', (0, 0, 0), radius=0.22, depth=0.16, vertices=8, parent=hub)
    for b in range(4):
        a = PI / 2 * b
        box('7A6040', (1.1 * math.cos(a), 1.1 * math.sin(a), -0.03), (1.8, 0.34, 0.04), hub, rot=(0.12, 0, a))
    desk(r, 0, 0.5, '5A3E28', 3.6)
    chair(r, 0, 1.65, '6A4A30')
    monitor(r, 1.2, 0.7, 1.11, -0.5, 'A8E8B0', False)
    box('2A2A30', (-0.9, 0.5, 1.16), (0.4, 0.3, 0.1), r)
    box('F2EAD2', (0.0, 0.3, 1.12), (0.6, 0.8, 0.03), r, rot=(0, 0, 0.2))
    box('F2EAD2', (-0.3, 0.6, 1.14), (0.6, 0.8, 0.03), r, rot=(0, 0, -0.3))
    tub(r, -5.2, 3.2, 1.5)
    tub(r, 5.4, 3.0, 1.2)
    for i in range(3):                                                                        # shelves of files
        box('6A4A30', (-6.2, -1.5 + 1.6 * i, 1.6), (0.6, 1.5, 3.2), r)
        for j in range(5):
            box(('B84A3A', '3A6A8A', 'D8B050', '4A7A5A', 'E8E0D0')[(i + j) % 5], (-5.95, -2.0 + 1.6 * i + 0.24 * j, 1.2 + 1.0 * (j % 2)), (0.3, 0.2, 0.8), r)
    box('7A5A3A', (5.3, -1.0, 0.5), (1.3, 3.0, 1.0), r)                                       # a low cane sofa
    box('C8B890', (5.3, -1.0, 1.05), (1.2, 2.8, 0.2), r, rough=1.0)
    box('7A5A3A', (5.9, -1.0, 1.4), (0.2, 3.0, 1.0), r)
    return dict(fan=hub)


def make_study(r):
    """A writing desk in front of a tall window at dusk, a city of plain towers outside, shelves of books."""
    room(r, 12, 7, 5.4, '4A4E66', '5A4636')
    box('F4B888', (0, 3.38, 3.1), (5.4, 0.05, 3.6), r, emit=1.6)
    for i in range(9):                                                                        # plain towers against the evening sky
        hh = 0.8 + 2.2 * rnd(i, 201)
        box('1E2438', (-2.4 + 0.6 * i, 3.33, 1.3 + hh / 2), (0.5, 0.05, hh), r)
        for j in range(int(hh / 0.4)):
            if rnd(i, 210 + j) > 0.5:
                box('FFE8A0', (-2.4 + 0.6 * i + 0.1 * (j % 3 - 1), 3.3, 1.5 + 0.38 * j), (0.08, 0.02, 0.1), r, emit=4.0)
    for s in (-1, 1):
        box('2A2E40', (s * 2.75, 3.3, 3.1), (0.14, 0.1, 3.7), r)
        box('8A3A3A', (s * 3.3, 3.2, 3.0), (0.9, 0.2, 4.2), r, rough=1.0)                    # curtains
    box('2A2E40', (0, 3.3, 3.1), (0.1, 0.1, 3.7), r)
    desk(r, 0, 0.4, '6A4A30', 3.8)
    chair(r, 0, 1.55, '5A3A2A')
    for i in range(6):                                                                        # the growing pile of pages
        box('F2EAD2', (-1.2, 0.5, 1.13 + 0.035 * i), (0.6, 0.8, 0.03), r, rot=(0, 0, 0.1 * (rnd(i, 221) - 0.5)))
    box('F2EAD2', (0.25, 0.25, 1.12), (0.6, 0.8, 0.02), r, rot=(0, 0, 0.12))
    add('cylinder', '2A2A30', (1.5, 0.7, 1.4), radius=0.05, depth=0.6, vertices=6, parent=r)   # desk lamp
    add('cone', 'D8A040', (1.5, 0.7, 1.8), radius1=0.34, radius2=0.14, depth=0.34, vertices=8, parent=r, emit=1.2)
    lamp = light((1.3, 0.5, 1.7), 0, 'FFD8A0', kind='POINT', parent=r)
    for s in (-1, 1):                                                                        # bookshelves
        box('3A2E28', (s * 5.2, 2.6, 2.4), (1.4, 0.7, 4.8), r)
        for j in range(4):
            for i in range(6):
                box(('B84A3A', '3A6A8A', 'D8B050', '4A7A5A', 'E8E0D0', '7A4A8A')[(i + j) % 6], (s * 5.2 - 0.5 + 0.2 * i, 2.22, 0.8 + 1.1 * j),
                    (0.16, 0.1, 0.7 + 0.2 * rnd(i, 230 + j)), r)
    box('8A4A3A', (0, -0.6, 0.01), (6.0, 3.6, 0.03), r, rough=1.0)                            # rug
    return dict(lamps=[lamp])


def make_apron(r):
    """A small airport apron in the tropics: tarmac, a low terminal with a tower, palms, a baggage cart, hills in the haze."""
    add('plane', '50545A', (0, 20, 0), size=260, parent=r, rough=0.9)
    for i in range(12):
        box('E8C83A', (-44 + 8 * i, 2.0, 0.02), (4.0, 0.3, 0.02), r)
    box('E8E4D8', (4, -6, 0.02), (60, 0.25, 0.02), r)
    box('DCD2B8', (-10, 46, 3.5), (44, 9, 7), r)                                               # terminal
    box('C8BEA4', (-10, 46, 7.3), (46, 10, 0.6), r)
    for i in range(12):
        box('5A8CA8', (-30 + 3.6 * i, 41.45, 3.6), (2.6, 0.1, 2.4), r, rough=0.2)
    add('cylinder', 'D0C6AC', (24, 48, 9), radius=2.2, depth=18, vertices=8, parent=r)          # tower
    add('cylinder', '5A8CA8', (24, 48, 19.5), radius=3.4, depth=3.0, vertices=8, parent=r, rough=0.2)
    add('cone', 'C8BEA4', (24, 48, 21.8), radius1=3.8, radius2=1.0, depth=1.6, vertices=8, parent=r)
    for i in range(11):                                                                       # palms along the fence
        x, y = -46 + 9.5 * i + 3 * rnd(i, 301), 36 + 3 * rnd(i, 302) - (14 if i in (0, 10) else 0)
        hh = 7 + 4 * rnd(i, 303)
        add('cylinder', '7A6248', (x, y, hh / 2), radius=0.32, depth=hh, vertices=6, parent=r, rot=(0.06 * (rnd(i, 304) - 0.5), 0.08, 0))
        for b in range(7):
            a = 2 * PI * b / 7 + rnd(i, 305)
            add('cone', LEAF[(i + b) % 5], (x + 1.7 * math.cos(a), y + 1.7 * math.sin(a), hh - 0.3), rot=(1.25 * math.sin(a), -1.25 * math.cos(a), 0),
                scale=(1, 0.22, 1), radius1=0.7, radius2=0.0, depth=4.2, vertices=4, parent=r, rough=0.8)
    for i in range(16):                                                                       # fence
        add('cylinder', '8A8E96', (-48 + 6.4 * i, 33, 1.0), radius=0.06, depth=2.0, vertices=5, parent=r)
    box('8A8E96', (0, 33, 1.9), (100, 0.05, 0.06), r)
    box('8A8E96', (0, 33, 1.0), (100, 0.05, 0.06), r)
    for j, (cx, cy) in enumerate(((15.5, 9.0), (18.3, 9.6))):                                  # baggage cart with cases
        box('3A6A8A', (cx, cy, 0.7), (2.4, 1.4, 0.16), r)
        for wx in (-0.9, 0.9):
            add('cylinder', '1A1A1E', (cx + wx, cy - 0.7, 0.32), rot=(PI / 2, 0, 0), radius=0.32, depth=0.16, vertices=8, parent=r)
        for i in range(3):
            box(('8A4A3A', '3A5A4A', 'B89A5A', '4A4A6A')[(i + j) % 4], (cx - 0.7 + 0.7 * i, cy, 1.15 + 0.1 * (i % 2)), (0.6, 1.0, 0.7 + 0.2 * (i % 2)), r)
    for i in range(4):
        add('cone', 'FF7A1A', (9 + 1.6 * i, -2.5 + 0.4 * (i % 2), 0.35), radius1=0.26, radius2=0.05, depth=0.7, vertices=6, parent=r)
    for i in range(3):
        add('cylinder', ('B84A3A', '3A6A8A', 'B84A3A')[i], (-22 - 1.3 * i, 12, 0.65), radius=0.5, depth=1.3, vertices=8, parent=r, rough=0.5)
    for i in range(8):                                                                        # hills in the haze
        a = -1.3 + 2.6 * i / 7
        add('cone', ('8AA89A', '9AB4A6', '7E9C90')[i % 3], (230 * math.sin(a), 210 * math.cos(a) + 40, 14), radius1=70 + 30 * rnd(i, 311), radius2=6,
            depth=50 + 40 * rnd(i, 312), vertices=6, parent=r, rough=1.0)
    for i in range(6):                                                                        # heavy cloud building over the hills
        add('ico_sphere', 'E8E4E0', (-150 + 60 * i, 190, 70 + 14 * rnd(i, 321)), scale=(2.4, 1.2, 0.8), radius=20 + 8 * rnd(i, 322), subdivisions=2, parent=r,
            rough=1.0)
    return {}


def cabin_seat(par, x, y, col='3E5A86'):
    st = empty((x, y, 0), par)
    box(col, (0, 0, 0.45), (0.74, 0.78, 0.2), st, rough=0.9)
    box(col, (0, 0.42, 1.1), (0.74, 0.16, 1.3), st, rot=(-0.12, 0, 0), rough=0.9)
    box('E8E4D8', (0, 0.4, 1.62), (0.6, 0.14, 0.24), st, rough=1.0)
    box('2A2A2E', (0, 0, 0.18), (0.6, 0.6, 0.36), st, rough=0.6)
    for a in (-1, 1):
        box('5A5A60', (a * 0.4, 0.0, 0.72), (0.07, 0.7, 0.06), st, rough=0.5)


FROWS = (-2.8, -1.2, 0.4, 2.0, 3.6, 5.2)
FCOLS = (-1.6, -0.78, 0.78, 1.6)


def make_flight(r):
    """Inside the small jet in flight: a narrow tube, two seats each side of the aisle, grey cloud at the windows."""
    box('3A3A40', (0, 1, -0.05), (4.8, 19, 0.1), r, rough=0.8)
    box('5A6A5A', (0, 1, 0.0), (0.74, 19, 0.02), r, rough=1.0)
    for s in (-1, 1):
        box('D4D0C4', (s * 2.3, 1, 1.3), (0.12, 19, 2.6), r, rot=(0, s * -0.1, 0), rough=0.6)
        box('CCC8BC', (s * 1.75, 1, 3.35), (1.3, 19, 0.12), r, rot=(0, s * 0.75, 0), rough=0.6)
        box('BEBAAE', (s * 1.55, 1, 2.75), (0.8, 19, 0.35), r, rough=0.6)                      # hat racks
        for i in range(9):
            box('D8DEE2', (s * 2.2, -5.2 + 1.6 * i, 1.75), (0.05, 0.55, 0.5), r, rot=(0, s * -0.1, 0), emit=1.6)
    box('CCC8BC', (0, 1, 3.75), (1.6, 19, 0.1), r, rough=0.6)
    for i in range(5):
        box('FFF4D8', (0, -4 + 3.2 * i, 3.68), (0.3, 1.2, 0.04), r, emit=2.4)
    box('C0BCB0', (0, 8.2, 1.9), (4.6, 0.15, 3.8), r)                                          # rear bulkhead
    box('6A7A8A', (0, 8.1, 1.5), (0.9, 0.06, 3.0), r, rough=1.0)                               # curtain
    for y in FROWS:
        for x in FCOLS:
            cabin_seat(r, x, y)
    people = (('8A4A4A', 'C89A74', '1A1614'), ('4A6A8A', 'D8B090', '2A2018'), ('B8A070', 'B8865E', '17131A'), ('5A7A5A', 'C89A74', '1A1614'),
              ('7A6A9A', 'D8B090', '3A2A1E'), ('C8C0B0', 'B8865E', '17131A'), ('3A5A6A', 'C89A74', '2A2018'))
    spots = ((-1.6, -2.8), (-1.6, 0.4), (0.78, 0.4), (1.6, 2.0), (-0.78, 2.0), (-1.6, 3.6), (0.78, 3.6))
    out = [bust(r, x, y + 0.05, 0.55, *c) for (x, y), c in zip(spots, people)]
    return dict(busts=out)


def make_ward(r):
    """A plain hospital room: two beds, a window in the far wall, a drip stand, flowers on a locker."""
    box('A8B8B0', (0, 0, -0.1), (13, 9, 0.2), r, rough=0.5)
    for s in (-1, 1):
        box('DCE4E0', (s * 6.5, 0, 2.5), (0.2, 9, 5.0), r)
    box('DCE4E0', (-3.25, 4.5, 2.5), (6.5, 0.2, 5.0), r)                                       # far wall, with an opening for the window
    box('DCE4E0', (5.0, 4.5, 2.5), (3.0, 0.2, 5.0), r)
    box('DCE4E0', (1.75, 4.5, 0.7), (3.5, 0.2, 1.4), r)
    box('DCE4E0', (1.75, 4.5, 4.5), (3.5, 0.2, 1.0), r)
    for x in (0.0, 1.75, 3.5):
        box('F4F6F6', (x, 4.42, 2.7), (0.1, 0.12, 2.7), r)
    box('F4F6F6', (1.75, 4.42, 1.42), (3.6, 0.3, 0.1), r)
    pane = box('EAF4FF', (1.75, 4.56, 2.7), (3.5, 0.04, 2.6), r, emit=2.0)
    for bx in (-3.4, 4.6):                                                                    # beds, heads to the far wall
        box('C8CCD0', (bx, 2.2, 0.55), (2.1, 4.3, 0.5), r, rough=0.4)
        box('F4F4F0', (bx, 2.2, 0.95), (2.0, 4.2, 0.3), r, rough=1.0)
        box('FFFFFF', (bx, 3.7, 1.2), (1.5, 0.9, 0.25), r, rough=1.0)
        box('C8CCD0', (bx, 4.25, 1.5), (2.1, 0.1, 1.6), r, rough=0.4)
    box('9CC0D0', (-3.4, 1.1, 1.32), (2.05, 2.2, 0.5), r, rough=1.0)                           # her blanket
    box('9CC0D0', (4.6, 1.9, 1.15), (2.05, 3.6, 0.14), r, rough=1.0)
    add('cylinder', 'C8CCD0', (-5.3, 3.6, 1.9), radius=0.04, depth=3.8, vertices=6, parent=r, rough=0.3)     # drip stand
    box('D8F0F8', (-5.3, 3.6, 3.5), (0.3, 0.12, 0.5), r, rough=0.2)
    box('E8E4D8', (-1.6, 3.9, 0.75), (1.0, 0.8, 1.5), r)                                        # locker with flowers
    add('cylinder', '6A9AB8', (-1.6, 3.9, 1.75), radius=0.16, depth=0.5, vertices=8, parent=r, rough=0.3)
    for i in range(7):
        add('ico_sphere', ('F0D040', 'F08A6A', 'FFFFFF', 'E86A8A')[i % 4], (-1.6 + 0.3 * (rnd(i, 401) - 0.5), 3.9 + 0.3 * (rnd(i, 402) - 0.5), 2.15 + 0.2 * rnd(i, 403)),
            radius=0.13, subdivisions=1, parent=r)
    chair(r, -1.2, 1.9, '6A7A8A', -0.9)
    box('B8C4C0', (-6.38, -2.0, 2.0), (0.06, 1.8, 4.0), r)                                      # door
    box('F4F6F6', (0, -0.2, 4.9), (9, 0.5, 0.1), r, emit=1.4)
    ceil = box('E4EAE8', (0, 0, 5.1), (13, 9, 0.2), r)
    return dict(pane=pane, ceil=ceil)


def make_chapel(r):
    """A plain funeral hall: an aisle between benches, tall windows, candles, a closed coffin under white flowers."""
    box('8A8478', (0, 0, -0.1), (16, 30, 0.2), r, rough=0.6)
    box('5A2A2A', (0, -1, 0.0), (2.6, 26, 0.03), r, rough=1.0)
    for s in (-1, 1):
        box('B8B0A0', (s * 8, 0, 5), (0.3, 30, 10), r)
        for i in range(5):
            box('A8C4E4', (s * 7.8, -10 + 5 * i, 5.4), (0.05, 1.6, 5.0), r, emit=1.3)
            add('cylinder', 'A8A090', (s * 6.6, -12.5 + 5 * i, 5), radius=0.38, depth=10, vertices=8, parent=r)
    box('B8B0A0', (0, 15, 5), (16, 0.3, 10), r)
    for x in (-3.4, 0, 3.4):
        box('F6DCA0', (x, 14.8, 5.6), (1.7, 0.05, 6.4), r, emit=1.8)
    box('B8B0A0', (0, -15, 5), (16, 0.3, 10), r)                                               # the wall behind, with the doors
    box('5A4230', (0, -14.8, 2.4), (3.2, 0.12, 4.8), r)
    box('2A2018', (0, -14.72, 2.4), (0.06, 0.1, 4.8), r)
    for x in (-5, 5):
        box('A8C4E4', (x, -14.8, 5.6), (1.5, 0.05, 4.4), r, emit=0.9)
    for i in range(8):                                                                        # benches
        y = -11 + 2.3 * i
        for s in (-1, 1):
            box('6A4A30', (s * 4.1, y, 0.55), (4.6, 0.75, 0.16), r)
            box('6A4A30', (s * 4.1, y - 0.36, 1.05), (4.6, 0.12, 1.3), r)
            for e in (-1, 1):
                box('5A3E28', (s * 4.1 + e * 2.3, y - 0.1, 0.75), (0.12, 0.9, 1.5), r)
    tops = ('1E2028', '2A2A34', '24262E', '30303A', '1C1E26')
    for i in range(14):                                                                       # mourners, seen from behind
        row = 2 + i % 5
        s = -1 if i % 2 else 1
        bust(r, s * (2.6 + 1.0 * (i // 5) + 0.5 * rnd(i, 501)), -11 + 2.3 * row + 0.1, 0.6, tops[i % 5], ('E0B898', 'D8AC88', 'E8C4A4')[i % 3],
             ('8A6A48', 'C8B078', '4A3A2A', 'B8B4AC')[i % 4], PI)
    box('9A9488', (0, 11.5, 0.2), (9, 6, 0.4), r)                                              # low step at the front
    box('3A2A20', (0, 10.5, 0.95), (1.2, 3.0, 1.1), r)                                         # stand
    box('8A5A34', (0, 10.5, 1.95), (1.25, 3.6, 0.9), r, rough=0.35)                            # the coffin, closed
    box('7A4E2C', (0, 10.5, 2.44), (1.35, 3.7, 0.1), r, rough=0.35)
    for i in range(22):
        add('ico_sphere', ('FFFFFF', 'F4F0E0', 'E8F0E0')[i % 3], (0.9 * (rnd(i, 511) - 0.5), 10.5 + 2.8 * (rnd(i, 512) - 0.5), 2.58 + 0.12 * rnd(i, 513)),
            radius=0.17 + 0.08 * rnd(i, 514), subdivisions=1, parent=r)
    lamps = []
    for i, (x, y) in enumerate(((-1.8, 9.2), (1.8, 9.2), (-1.8, 11.8), (1.8, 11.8))):          # candles
        add('cylinder', 'B89A5A', (x, y, 1.3), radius=0.07, depth=1.8, vertices=6, parent=r, rough=0.4)
        add('cylinder', 'F4F0E4', (x, y, 2.5), radius=0.06, depth=0.6, vertices=6, parent=r)
        add('cone', 'FFC860', (x, y, 2.95), radius1=0.07, radius2=0.0, depth=0.26, vertices=5, parent=r, emit=14.0)
        lamps.append(light((x, y - 0.3, 3.1), 0, 'FFC070', kind='POINT', parent=r))
    for s in (-1, 1):
        for i in range(6):
            add('ico_sphere', ('FFFFFF', 'F0E0A0', 'E8C0C8')[i % 3], (s * 3.2 + 0.5 * rnd(i, 521), 11 + 0.6 * rnd(i, 522), 0.9 + 0.5 * rnd(i, 523)), radius=0.3,
                subdivisions=1, parent=r)
        add('cylinder', '4A6A4A', (s * 3.2, 11.2, 0.55), radius=0.4, depth=0.5, vertices=8, parent=r)
    return dict(lamps=lamps)


def make_park(r):
    """A city park in autumn: a path, round trees turning gold, benches, lamp posts, plain towers beyond."""
    add('plane', '6A9450', (0, 30, 0), size=320, parent=r, rough=1.0)
    box('D0C4A0', (0, 0, 0.02), (90, 4.2, 0.04), r, rough=1.0)
    box('D0C4A0', (-9, 14, 0.02), (4.0, 28, 0.04), r, rough=1.0)
    cols = ('E0A030', 'C85A2A', 'E8C048', '7A9A3A', 'D87A2A')
    for i in range(22):
        x = -40 + 3.9 * i + 2 * rnd(i, 601)
        y = (5.5 + 7 * rnd(i, 602)) if i % 3 else (-4.5 - 4 * rnd(i, 603))
        if abs(x + 9) < 3 and y > 0:
            continue
        hh = 3.4 + 2 * rnd(i, 604)
        add('cylinder', '5A4636', (x, y, hh / 2), radius=0.26, depth=hh, vertices=6, parent=r)
        add('ico_sphere', cols[i % 5], (x, y, hh + 1.6), scale=(1, 1, 0.85), radius=2.3 + 0.9 * rnd(i, 605), subdivisions=1, parent=r, rough=0.9)
    for i in range(30):                                                                       # fallen leaves
        box(cols[i % 5], (-12 + 24 * rnd(i, 611), -2.4 + 4.8 * rnd(i, 612), 0.05), (0.3, 0.18, 0.02), r, rot=(0, 0, rnd(i, 613) * PI))
    for bx in (-2.0, 9.0):                                                                    # benches
        box('6A4A30', (bx, 2.9, 0.6), (2.6, 0.7, 0.12), r)
        box('6A4A30', (bx, 3.25, 1.2), (2.6, 0.1, 0.9), r, rot=(-0.15, 0, 0))
        for e in (-1, 1):
            box('2A2A30', (bx + e * 1.2, 3.0, 0.3), (0.1, 0.7, 0.6), r)
    for lx in (-14, 4, 20):
        add('cylinder', '2A2A30', (lx, -2.6, 2.4), radius=0.08, depth=4.8, vertices=6, parent=r)
        add('ico_sphere', 'FFF4D0', (lx, -2.6, 4.9), radius=0.3, subdivisions=1, parent=r, emit=1.5)
    add('cylinder', '5A86A8', (14, 24, 0.03), radius=9, depth=0.04, vertices=14, parent=r, rough=0.15)       # a pond
    for i in range(20):                                                                       # plain towers, no real skyline
        hh = 24 + 50 * rnd(i, 621)
        box(('8A94A8', '9AA4B4', '7A8698', 'A8AEBC')[i % 4], (-95 + 10 * i + 3 * rnd(i, 622), 95 + 14 * rnd(i, 623), hh / 2), (7 + 3 * rnd(i, 624), 7, hh), r,
            rough=0.5)
    return {}


MAKERS = dict(office=make_office, saigon=make_saigon, study=make_study, apron=make_apron, flight=make_flight, ward=make_ward, chapel=make_chapel,
              park=make_park)


# ---------------------------------------------------------------- new people and props
def hood_head(skin, hood):
    def fn(head):
        d = K.human_head(skin, '17131A')(head)
        add('ico_sphere', hood, (0, 0.1, 0.06), scale=(1.0, 1.0, 1.1), radius=0.36, subdivisions=1, parent=head, rough=1.0)
        return d
    return fn


_build0, _reset0 = build, reset


def build():
    global add, empty
    S = _build0()
    add, empty = fast_add, fast_empty
    K.add, K.empty = fast_add, fast_empty
    S['sets'] = {}
    for name, fn in MAKERS.items():
        root = empty(SETPOS[name])
        d = fn(root)
        d.setdefault('lamps', [])
        d.update(root=root, all=[root] + list(root.children_recursive))
        S['sets'][name] = d
    S['will'] = K.Rig(dict(top='E8E8E0', pants='3A4458', hand='E8C0A0', boot='2A2018', fore='E8E8E0'), K.human_head('E8C0A0', 'C8A868'))
    S['jaime'] = K.Rig(dict(top='2A3A5A', pants='2A2A34', hand='D8A880', boot='1A1A1E', fore='2A3A5A'), K.human_head('D8A880', '2A2018'))
    S['orange'] = K.Rig(dict(top='F07A1A', pants='4A4A3A', hand='B8865E', boot='2A2018', fore='F07A1A'), hood_head('B8865E', 'F07A1A'))
    S['bearers'] = [K.Rig(dict(top=c, pants='1E1E24', hand='E0B898', boot='121216', fore=c), K.human_head('E0B898', hr))
                    for c, hr in (('22242C', '6A5238'), ('2A2C36', '2A2420'))]
    S['kids'] = [K.Rig(dict(top=c, pants='4A5A7A', hand='E6BC9A', boot='3A3030', fore=c), K.human_head('E6BC9A', hr))
                 for c, hr in (('E86A5A', '8A6238'), ('5AA0D8', '6A4A2A'))]
    new = [S['will'], S['jaime'], S['orange']] + S['bearers'] + S['kids']
    S['humans'] += new
    S['cast'] += new
    # props that live outside the sets (parked far away until a shot places them)
    gear = S['gear'] = keep(empty(FAR))                                                       # the little jet's wheels and its rear stairs
    for gx, gy in ((-8.6, 0), (1.6, -2.6), (1.6, 2.6)):
        add('cylinder', '8A8E96', (gx, gy, -1.9), radius=0.12, depth=1.6, vertices=6, parent=gear, rough=0.4)
        add('cylinder', '1A1A1E', (gx, gy, -2.55), rot=(PI / 2, 0, 0), radius=0.45, depth=0.3, vertices=10, parent=gear)
    for i in range(6):
        box('B4B8BE', (7.6 + 0.55 * i, 0, -1.55 - 0.3 * i), (0.6, 1.5, 0.1), gear, rough=0.4)
    for s in (-1, 1):
        bar(gear, '8A8E96', (7.4, s * 0.8, -0.5), (10.6, s * 0.8, -2.1), 0.05, rough=0.4)
    S['case'] = sc_ = keep(empty(FAR))                                                        # a suitcase, open
    box('7A4A3A', (0, 0, 0.12), (1.1, 0.75, 0.24), sc_)
    box('7A4A3A', (0, 0.42, 0.5), (1.1, 0.1, 0.75), sc_, rot=(-0.25, 0, 0))
    box('E8E0D0', (-0.15, 0, 0.26), (0.6, 0.5, 0.08), sc_, rough=1.0)
    box('4A6A8A', (0.3, 0.05, 0.27), (0.3, 0.45, 0.1), sc_, rough=1.0)
    S['bag'] = bg = keep(empty(FAR))                                                          # her travel bag
    box('8A5A3A', (0, 0, 0.3), (0.5, 0.9, 0.6), bg)
    box('5A3A2A', (0, 0, 0.66), (0.08, 0.5, 0.12), bg)
    S['cloth'] = keep(box('3A4A6A', FAR, (0.5, 0.36, 0.12), rough=1.0))                       # the folded trousers
    S['belts'] = [keep(box('E8E0C0', FAR, (0.62, 0.12, 0.04), rough=1.0)), keep(box('E8E0C0', FAR, (0.12, 0.05, 0.6), rough=1.0)),
                  keep(box('F0F4FA', FAR, (0.2, 0.16, 0.07), rough=0.1, emit=0.4))]
    S['bugs'] = [keep(add('ico_sphere', '14140E', FAR, radius=0.022, subdivisions=1)) for _ in range(9)]
    cb = S['clip'] = keep(empty(FAR))                                                         # a clipboard with a list: lines only, no lettering
    box('6A5238', (0, 0, 0), (0.78, 0.03, 1.02), cb)
    box('F4F0E4', (0, -0.02, -0.02), (0.68, 0.02, 0.9), cb, rough=1.0)
    box('8A8E96', (0, -0.04, 0.46), (0.3, 0.03, 0.08), cb, rough=0.3)
    for i in range(9):
        box('3A3A44', (-0.04 - 0.05 * rnd(i, 701), -0.034, 0.3 - 0.085 * i), (0.5 - 0.1 * rnd(i, 702), 0.008, 0.022), cb)
    S['mark'] = keep(box('FF7A1A', (0, -0.036, 0.3 - 0.085 * 5), (0.62, 0.008, 0.06), cb, emit=1.2))
    S['bundle'] = keep(box('20242A', FAR, (0.9, 0.5, 0.22), rough=0.6))                       # folded bags
    S['stick'] = keep(add('cylinder', '6A4A30', FAR, radius=0.04, depth=1.5, vertices=6))
    S['phone'] = keep(box('1E1E24', FAR, (0.1, 0.12, 0.4)))
    S['phone2'] = keep(box('1E1E24', FAR, (0.1, 0.12, 0.4)))
    S['pen'] = keep(add('cylinder', '1E2A5A', FAR, radius=0.02, depth=0.3, vertices=5))
    S['sparks'] = [keep(add('ico_sphere', ('FFD060', 'FF7A5A', 'A0E0FF', 'FFFFFF')[i % 4], FAR, radius=0.16, subdivisions=1, emit=30.0)) for i in range(24)]
    lt_ = S['litter'] = keep(empty(FAR))                                                      # a stretcher
    for s in (-1, 1):
        bar(lt_, '8A8E96', (s * 0.5, -2.4, 0), (s * 0.5, 2.4, 0), 0.05, rough=0.3)
    box('F4F4F0', (0, 0, 0.0), (1.0, 3.7, 0.06), lt_, rough=1.0)
    box('9AA8B8', (0, 0.9, 0.26), (1.0, 1.8, 0.42), lt_, rough=1.0)                             # blanket
    S['outcrop'] = keep(add('cylinder', '6A7060', FAR, radius=3.4, depth=1.4, vertices=7, rough=1.0))
    S['loose'] = [keep(box(('F4F0E4', 'B84A3A', '3A6A8A', 'E8D890', 'F4F0E4', '5A4632')[i], FAR, (0.16 + 0.1 * (i % 3), 0.14, 0.12 + 0.08 * (i % 2)))) for i in range(6)]
    K.add, K.empty = _ops_add, _ops_empty
    add, empty = _ops_add, _ops_empty
    reset(S)
    return S


def reset(S):
    _reset0(S)
    if 'sets' not in S:
        return
    for rig in S['cast']:
        rig.root.scale = (1, 1, 1)
    S['her'].body.scale = (1, 1, 1)
    for d in S['sets'].values():
        for o in d['all']:
            o.hide_render = True
        for l in d['lamps']:
            l.data.energy = 0
    S['mark'].scale = (0.001, 0.001, 0.001)


def use(S, name, skyname):
    sky(S, skyname)
    d = S['sets'][name]
    for o in d['all']:
        o.hide_render = False
    return d


def stand(S, rig, name, x, y, z=0.0, yaw=0.0, pose=None, face=None, pitch=0.0):
    rig.root.parent = None
    rig.place(SP(name, x, y, z), yaw, pitch)
    rig.apply(pose or P())
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def cam(S, name, pos, look, lens=32, roll=0.0):
    shoot(S, SETPOS[name], pos, look, lens, roll)


def lamp(S, name, pos, look, watts, col='FFE8D0'):
    key(S, SETPOS[name], pos, look, watts, col)


def talk(rig, lt, rate=7.0, amt=0.4):
    rig.jawv = amt * (0.5 + 0.5 * math.sin(lt * rate)) * (0.6 + 0.4 * math.sin(lt * 2.3 + 1))


def hold(S, prop, rig, i=1, d=(0, -0.1, 0.0), rot=None):
    h = wpos(rig.hands[i])
    prop.location = (h[0] + d[0], h[1] + d[1], h[2] + d[2])
    if rot is not None:
        prop.rotation_euler = rot
    return h


def ear(S, prop, rig, side=1):
    h = head(S, rig)
    yaw = rig.root.rotation_euler[2]
    prop.location = (h[0] + side * 0.36 * math.cos(yaw), h[1] + side * 0.36 * math.sin(yaw), h[2] - 0.05)
    prop.rotation_euler = (0.2, 0, yaw)


SEAT = dict(lL=(1.45, 1.5), lR=(1.45, 1.5))


# ---------------------------------------------------------------- how it began
def desk_trade(S, k, t, lt):
    """The trading floor in Madrid: she sits at her desk between two monitors, telephone at her ear, talking and smiling;
    Rook leans by the window, arms folded. With prm "empty" her chair stands empty and Rook looks down at it."""
    use(S, 'office', 'office')
    gone = S['prm'].get('empty')
    if not gone:
        h = stand(S, S['her'], 'office', 0, 1.72, 0, 0.0, P('sit', aR=(0.9, -0.1, 2.3, 0.9), aL=(0.9, 0.1, 1.2, 0.3), lean=0.1,
                                                           head=(0.02, 0.25 * math.sin(lt * 1.3)), **SEAT), 'warm')
        ear(S, S['phone'], h)
        talk(h, lt)
        stand(S, S['rook'], 'office', -4.4, 2.6, 0, facing(4.4, -2.4), P('cross', head=(0.05, 0.2)), 'low')
        S['hat_tip'] = 0.5 * sm((lt - 1.2) / 0.4)
    else:
        u = sm((lt - 0.5) / 0.6)
        stand(S, S['rook'], 'office', -1.9, 2.3, 0, facing(1.9, -1.6), blend(P('cross'), P('stand', head=(0.4, 0.0)), u), 'sad')
        S['phone'].location = SP('office', -0.2, 0.75, 1.3)
        S['phone'].rotation_euler = (0, PI / 2, 0.3)
    lamp(S, 'office', (-3, -5, 5), (0, 1.5, 1.6), 900, 'FFF0E0')
    cam(S, 'office', (lerp(-2.4, -1.9, k), lerp(-4.6, -4.0, k), 2.4), (-1.1, 1.6, 1.95), 30)


def pasje_desk(S, k, t, lt):
    """An office in Vietnam, the fan turning: Willem at his desk on the telephone, laughing, leaning back."""
    d = use(S, 'saigon', 'saigon')
    d['fan'].rotation_euler = (0, 0, t * 5.0)
    w = stand(S, S['will'], 'saigon', 0, 1.62, 0, 0.0, P('sit', aL=(0.9, -0.1, 2.3, 0.9), aR=(0.8, 0.2, 1.1, 0.3), lean=lerp(0.15, -0.05, sm(lt / 1.5)),
                                                        head=(0.02, -0.2 + 0.15 * math.sin(lt * 1.1)), **SEAT), 'warm')
    ear(S, S['phone2'], w, -1)
    talk(w, lt, 6.0)
    lamp(S, 'saigon', (3, -5, 4), (0, 1.5, 1.8), 700, 'FFE0B0')
    cam(S, 'saigon', (lerp(2.3, 1.8, k), lerp(-4.4, -3.8, k), 2.4), (0.3, 1.5, 1.95), 30)


def apron_base(S):
    use(S, 'apron', 'apron')
    for o in (S['jet'], S['gear']):
        o.location, o.rotation_euler, o.scale = SP('apron', -6, 16, 3.76), (0, 0, 0), (1.6, 1.6, 1.6)
    lamp(S, 'apron', (14, 4, 8), (8, 14, 2), 2500, 'FFF0D0')


def apron_wide(S, k, t, lt):
    """The apron: the little jet waits with its rear stairs down; Willem waves by the steps; she crosses the tarmac with
    her bag; Rook follows and pops his collar."""
    apron_base(S)
    hx, hy = lerp(12.4, 9.6, k), lerp(9.8, 13.0, k)
    yw = facing(-3.8, 4.4)
    pose = K.walk(lt, 1.3)
    pose['aR'] = (0.1, 0.15, 0.2, 0.0)
    h = stand(S, S['her'], 'apron', hx, hy, 0, yw, pose, 'warm')
    hd = hold(S, S['bag'], h, 1, (0, 0, -0.75), (0, 0, yw))
    wv = 0.5 + 0.5 * math.sin(lt * 8)
    stand(S, S['will'], 'apron', 5.6, 13.6, 0, facing(5.6, -3.4), P('stand', aR=(2.6, 0.5 + 0.3 * wv, 0.4), head=(-0.05, 0.0)), 'warm')
    pop = sm((k - 0.3) / 0.15) * (1 - sm((k - 0.6) / 0.15))
    rp = K.walk(lt + 0.4, 1.3)
    rp = blend(rp, P('stand', aL=(0.7, 0.3, 2.4, 0.5), aR=(0.7, 0.3, 2.4, 0.5), lL=rp['lL'], lR=rp['lR']), pop)
    stand(S, S['rook'], 'apron', hx + 2.6, hy + 1.4, 0, yw, rp, 'low')
    cam(S, 'apron', (lerp(15.4, 14.6, k), lerp(5.6, 6.2, k), 1.9), (6.4, 14.2, 2.7), 28)


def apron_meet(S, k, t, lt):
    """Close on the two of them at the foot of the steps: they take each other's hands, both smiling."""
    apron_base(S)
    u = sm(lt / 0.8)
    stand(S, S['her'], 'apron', 9.3, 13.6, 0, facing(-1.0, 1.4), P('stand', aR=(lerp(0.2, 1.0, u), 0.1, 0.5), aL=(lerp(0.2, 1.0, u), 0.1, 0.5), head=(-0.08, 0.0)), 'warm')
    w = stand(S, S['will'], 'apron', 8.3, 15.0, 0, facing(1.0, -1.4), P('stand', aR=(lerp(0.2, 1.0, u), 0.1, 0.5), aL=(lerp(0.2, 1.0, u), 0.1, 0.5), head=(0.05, 0.0)), 'warm')
    talk(w, lt, 5.0, 0.25)
    S['bag'].location, S['bag'].rotation_euler = SP('apron', 10.1, 13.0, 0), (0, 0, 0.6)
    cam(S, 'apron', (lerp(12.6, 12.0, k), lerp(16.6, 16.2, k), 2.5), (8.8, 14.3, 2.3), 40)


def apron_stairs(S, k, t, lt):
    """At the stairs under the tail: she stops, arms tight across herself, shakes her head and steps back; he holds out a
    hand and talks her round."""
    apron_base(S)
    b = sm((lt - 0.4) / 0.6)
    h = stand(S, S['her'], 'apron', 9.0 + 0.6 * b, 14.6 - 0.6 * b, 0, facing(-1.6, 1.2), P('cross', head=(0.08, 0.35 * math.sin(lt * 5.5) * b), lean=-0.08 * b), 'wide')
    w = stand(S, S['will'], 'apron', 7.3, 15.7, 0, facing(1.7, -1.1), P('stand', aR=(1.2, 0.3, 0.3), aL=(0.3, 0.4, 0.6), head=(0.02, 0.0)), 'warm')
    talk(w, lt, 6.0, 0.35)
    S['bag'].location, S['bag'].rotation_euler = SP('apron', 10.3, 13.6, 0), (0, 0, 0.4)
    cam(S, 'apron', (lerp(5.6, 6.0, k), lerp(12.2, 12.6, k), 2.1), (8.9, 14.7, 2.4), 32)


def rook_apron(S, k, t, lt):
    """Rook on the tarmac looks the little jet up and down; his brim drops."""
    apron_base(S)
    d = sm((lt - 1.0) / 0.35)
    stand(S, S['rook'], 'apron', 10.4, 11.6, 0, facing(2.4, -3.0), P('cross', head=(lerp(-0.2, 0.2, d), lerp(-1.1, 0.0, d))), 'low')
    S['hat_tip'] = 0.9 * d
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] + 3, h[1] - 3, h[2] + 2), h, 500, 'FFF0D0')
    shoot(S, (0, 0, 0), (h[0] + lerp(2.3, 1.9, k), h[1] - lerp(3.0, 2.6, k), h[2] - 0.3), (h[0] - 0.5, h[1] + 0.4, h[2] - 0.1), 30)


# ---------------------------------------------------------------- in the air
def flight_base(S, lt, drop=0.0):
    use(S, 'flight', 'flight')
    jz = 0.1 * drop * math.sin(lt * 23) * (0.5 + 0.5 * math.sin(lt * 5))
    turn = sm((lt - 0.5) / 0.4) if drop else 0.0
    h = stand(S, S['her'], 'flight', 1.6, -2.78, jz, 0.0, P('sit', aL=(0.7, 0.0, 1.3, 0.6), aR=(0.7, 0.0, 1.3, 0.6), lean=0.12,
                                                             head=(0.08, lerp(0.55, -0.6, turn)), **SEAT), 'wide' if drop > 1 else 'calm')
    w = stand(S, S['will'], 'flight', 0.78, -2.78, jz * 1.2, 0.0, P('sit', aL=(0.7, 0.0, 1.3, 0.6), aR=(0.7 + 0.2 * turn, 0.0, 1.3, 0.6), lean=0.12,
                                                                   head=(0.05, lerp(-0.3, 0.75, turn)), **SEAT), 'wide' if drop else 'calm')
    r = stand(S, S['rook'], 'flight', -0.78, -1.18, jz * 0.8, 0.2, P('cross', lL=(1.45, 1.5), lR=(1.45, 1.5), lift=-0.5, lean=0.1, head=(0.1, 0.3)),
              'shocked' if drop > 1 else 'low')
    if drop > 1:
        S['hat_jump'] = 0.35 * abs(math.sin(lt * 6))
        for i, o in enumerate(S['loose']):
            ph = (lt * 0.8 + rnd(i, 801)) % 1.0
            o.location = SP('flight', -1.4 + 2.8 * rnd(i, 802), -4.0 + 5 * rnd(i, 803), 1.0 + 2.2 * ph)
            o.rotation_euler = (lt * 5 * rnd(i, 804), lt * 4, lt * 3 * rnd(i, 805))
    fl = 1.0 if drop < 2 else (0.35 + 0.65 * (math.sin(lt * 27) > 0))
    lamp(S, 'flight', (-0.4, -6.5, 3.0), (0.9, -2.8, 1.8), 420 * fl, 'FFF4E0')
    S['bg'].inputs[1].default_value *= fl
    return h, w, r


def cabin_flight(S, k, t, lt):
    """Down the aisle of the small jet: the two of them side by side on the right, Rook a row behind across the aisle, arms
    folded, grey cloud at the windows. With prm "drop" the cabin lurches: lights flicker, cups and bags leave the floor."""
    dr = S['prm'].get('drop', 0)
    flight_base(S, lt, dr)
    cam(S, 'flight', (-0.3 + 0.03 * dr * math.sin(lt * 17), lerp(-7.6, -6.9, k), 2.5 + 0.04 * dr * math.sin(lt * 21)), (0.45, -1.6, 1.85), 24,
        roll=0.05 * dr * math.sin(lt * 7))


def cabin_drop(S, k, t, lt):
    """Close on the two of them as the plane drops: he turns to her, eyes wide; she tells him it is only an air pocket."""
    h, w, r = flight_base(S, lt, 1)
    h.face = 'warm' if lt > 1.0 else 'wide'
    if lt > 1.0:
        talk(h, lt, 6.5, 0.35)
    cam(S, 'flight', (1.0, lerp(-5.5, -5.1, k), 2.2 + 0.03 * math.sin(lt * 19)), (1.2, -2.8, 1.95), 36, roll=0.03 * math.sin(lt * 9))


def hands_grab(S, k, t, lt):
    """Close on the armrest between them: his hand comes down on hers and holds on; the light goes."""
    flight_base(S, lt, 2)
    for rig in (S['her'], S['will'], S['rook']):
        rig.place(FAR)
    for o in S['loose']:
        o.location = FAR
    a = SP('flight', 1.19, -2.85, 0.8)
    g_ = sm(lt / 0.7)
    S['hand_her'].place((a[0] + 0.12, a[1] - 0.05, a[2] + 0.02 * math.sin(lt * 23)), (0.05, 0, 0.25))
    S['hand_her'].grip(lerp(0.15, 0.6, g_))
    S['hand_him'].place((a[0] - lerp(0.7, 0.16, g_), a[1] + 0.16, a[2] + lerp(0.45, 0.09, g_)), (0.1, 0.25, -0.95))
    S['hand_him'].grip(lerp(0.1, 0.85, g_))
    dark = sm((k - 0.72) / 0.25)
    S['keyl'].data.energy *= (1 - dark)
    S['bg'].inputs[1].default_value *= (1 - 0.95 * dark)
    S['camfill'].data.energy = 120 * (1 - dark)
    cam(S, 'flight', (lerp(0.6, 0.75, k), lerp(-4.5, -4.2, k), 1.7), (1.19, -2.85, 0.85), 44, roll=0.06 * math.sin(lt * 8))


def cabin_base(S, watts=300):
    S['cabin'].location = CABIN
    S['cabin'].rotation_euler = (0, 0, 0)
    sky(S, 'cabin')
    S['cabl'].location = at(CABIN, 0.3, 0.6, 3.4)
    S['cabl'].rotation_euler = (0.4, 0.1, 0)
    S['cabl'].data.energy = watts


def belt_empty(S, k, t, lt):
    """In the broken cabin: an empty seat, its belt lying open, one strap still swinging, rain dripping through the roof."""
    cabin_base(S, 420)
    x, y = 0.85, 0.5
    a, b, c = S['belts']
    a.location, a.rotation_euler = at(CABIN, x - 0.18, y - 0.12, 0.57), (0, 0.1, 0.25)
    sw = 0.5 * math.sin(lt * 3.2) * math.exp(-0.25 * lt)
    b.location, b.rotation_euler = at(CABIN, x + 0.46 + 0.14 * math.sin(sw), y - 0.2, 0.36), (0, -sw, 0)
    c.location, c.rotation_euler = at(CABIN, x + 0.12, y - 0.06, 0.61), (0, 0.1, 0.25)
    for i, d in enumerate(S['drips']):
        ph = (t * 1.1 + i / 6) % 1.0
        d.location = at(CABIN, x - 0.5 + 0.25 * i, y - 0.3 + 0.2 * (i % 2), 2.6 - 2.2 * ph)
    key(S, CABIN, (x - 1.4, y - 0.8, 2.6), (x, y, 0.6), 260, 'C8F0C0')
    shoot(S, CABIN, (x - lerp(1.45, 1.25, k), y - lerp(0.75, 0.55, k), lerp(1.75, 1.6, k)), (x + 0.05, y - 0.05, 0.62), 32)


def her_looks(S, k, t, lt):
    """In the broken cabin, past the back of a seat: she has pulled herself up in the aisle and looks at the man in it. Of
    him only the back of his head and one still hand on the armrest are seen. Her face falls."""
    cabin_base(S, 380)
    put(S, S['will'], 0.85, -0.8, 0.0, 0.0, P('sit', aL=(0.6, 0.0, 1.2, 0.5), aR=(0.6, 0.0, 1.2, 0.5), lean=0.05, head=(0.3, 0.12), **SEAT), 'shut', o=CABIN)
    S['hand_him'].place(at(CABIN, 0.85 - 0.46, -0.8, 0.74), (0, 0, 0.05))
    S['hand_him'].grip(0.25)
    u = sm((lt - 0.8) / 0.6)
    h = put(S, S['her'], -0.25, -2.5, 0.0, PI - 0.35, P('sit', aL=(0.5, 0.5, 0.5), aR=(0.9, 0.3, 0.7), lean=0.1, lL=(1.3, 0.9), lR=(1.2, 0.6),
                                                   head=(lerp(-0.25, 0.15, u), 0.2)), 'wide' if u < 0.5 else 'sad', o=CABIN)
    hp = head(S, h)
    key(S, (0, 0, 0), (hp[0] + 1.0, hp[1] + 2.0, hp[2] + 1.6), hp, 260, 'C8F0C0')
    shoot(S, CABIN, (lerp(0.05, 0.2, k), lerp(0.5, 0.3, k), 2.35), (hp[0] - CABIN[0] + 0.55, hp[1] - CABIN[1], hp[2] - 0.15), 30)


# ---------------------------------------------------------------- on the slope
def man_pair(S, give=0.0, face='tired'):
    m = put(S, S['man'], MAN[0] - 1.0, MAN[1] - 1.3, 0.42, -0.9, P('sit', aR=(lerp(0.5, 1.35, give), 0.15, lerp(1.5, 0.4, give)), aL=(0.5, 0.3, 1.0), lean=-0.25,
                                                      lL=(1.3, 0.9), lR=(1.25, 0.7), head=(0.15, -0.35)), face)
    h = put(S, S['her'], MAN[0] - 2.9, MAN[1] - 1.8, 0.42, PI * 0.42, P('sit', aR=(lerp(0.6, 1.5, give), 0.1, lerp(1.4, 0.3, give)), aL=(0.8, 0.5, 1.6), lean=0.3,
                                                                       lL=(1.3, 1.2), lR=(1.2, 0.9), head=(0.2, 0.0)), 'tired')
    S['case'].location, S['case'].rotation_euler = gp(MAN[0] + 0.1, MAN[1] - 2.3, 0.12), (0.25, 0.0, -0.5)
    return m, h


def trousers(S, k, t, lt):
    """By the wreck in the rain: the man who lived through the crash sits propped beside his open suitcase and holds out
    a folded pair of trousers; she reaches and takes them."""
    ridge(S, 'rain', t, 0.6)
    u = sm((lt - 0.3) / 0.8)
    v = sm((lt - 1.3) / 0.7)
    m, h = man_pair(S, u)
    a, b = wpos(m.hands[1]), wpos(h.hands[1])
    S['cloth'].location = tuple(lerp(a[i], b[i], v) + (0.12 if i == 2 else 0) for i in range(3))
    S['cloth'].rotation_euler = (0, 0, 0.5)
    mid = tuple((a[i] + b[i]) / 2 for i in range(3))
    key(S, (0, 0, 0), (mid[0] - 2, mid[1] - 3, mid[2] + 3), mid, 700, 'C8D8D0')
    shoot(S, (0, 0, 0), (mid[0] - lerp(1.4, 1.0, k), mid[1] - lerp(5.2, 4.6, k), mid[2] + 1.3), (mid[0] + 0.2, mid[1], mid[2] + 0.2), 28)


def man_talks(S, k, t, lt):
    """Close on the man: grey, tired, but talking, and he lifts a hand towards the sky: they will come."""
    ridge(S, 'rain', t, 0.6)
    m, h = man_pair(S, 0.0, 'tired')
    u = 0.0 if S['prm'].get('quiet') else sm((lt - 0.6) / 0.6)
    m.apply(P('sit', aL=(lerp(0.5, 2.1, u), 0.35, lerp(1.0, 0.25, u)), aR=(0.5, 0.15, 1.5), lean=-0.25, lL=(1.3, 0.9), lR=(1.25, 0.7), head=(lerp(0.15, -0.1, u), -0.3)))
    talk(m, lt, 6.0, 0.35)
    hp = head(S, m)
    key(S, (0, 0, 0), (hp[0] - 2, hp[1] - 2, hp[2] + 2), hp, 420, 'C8D8D0')
    shoot(S, (0, 0, 0), (hp[0] - lerp(1.5, 1.2, k), hp[1] - lerp(2.6, 2.3, k), hp[2] + 0.25), (hp[0] + 0.1, hp[1], hp[2] + 0.1), 38)


def her_resolve(S, k, t, lt):
    """Close on her against the root as the rain thins: she wipes her eyes with the back of her hand, then lifts her head and
    sets her face."""
    ridge(S, 'rain', t, 0.4, 'day', sm(k * 1.2))
    u = sm((k - 0.45) / 0.2)
    wipe = 0.5 + 0.5 * math.sin(lt * 4.5)
    her_spot(S, 'sad' if u < 0.5 else 'hard', blend(P('sit', aR=(1.05 + 0.15 * wipe, -0.3, 2.35, 0.6), lean=-0.1, head=(0.42, 0.12)),
                                                   P('sit', aR=(0.7, -0.1, 1.5, 1.0), lean=-0.22, head=(-0.08, -0.05)), u))
    h = head(S, S['her'])
    key(S, (0, 0, 0), (h[0] + 1.5, h[1] - 2, h[2] + 3), h, 420, 'E8F0E0')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.0, 0.8, k), h[1] - lerp(2.2, 1.9, k), h[2] + 0.1), (h[0], h[1], h[2] - 0.05), 42)


def sip_wait(S, k, t, lt):
    """At the wing as the day goes: the balls of insulation in a row on the metal, she sits beside them and waits, then
    takes one; Rook, further along the wing, flips a coin to pass the time."""
    ridge(S, 'day', t, 0.3, 'dusk', sm(k * 1.1))
    u = sm((k - 0.7) / 0.2)
    h = put(S, S['her'], WROOT[0] + 1.0, WROOT[1] + 0.7, -0.12, 0.4, P('sit', aR=(lerp(0.7, 1.25, u), 0.0, lerp(1.4, 0.7, u)), aL=(0.7, 0.2, 1.4), lL=(1.5, 0.25), lR=(1.42, 0.1), head=(0.2, -0.35), lean=-0.25), 'tired')
    hd = wpos(h.hands[1])
    for i, b in enumerate(S['balls']):
        p = on_wing(-0.5 - 0.42 * i, -0.75)
        b.location = (lerp(p[0], hd[0], u), lerp(p[1], hd[1] - 0.1, u), lerp(p[2] + 0.1, hd[2] + 0.1, u)) if i == 0 else (p[0], p[1], p[2] + 0.1)
        b.scale = (1.5, 1.5, 1.5)
    p = on_wing(-3.4, 0.25)
    r = put(S, S['rook'], 0, 0, 0, 0.7, P('stand', aR=(1.0, -0.1, 1.3, 0.3), head=(0.2, 0.3)), 'calm', o=p)
    rh = wpos(r.hands[1])
    fl = (lt * 1.1) % 1.0
    S['rivet'].location, S['rivet'].rotation_euler = (rh[0], rh[1] - 0.12, rh[2] + 0.1 + 2.4 * fl * (1 - fl)), (lt * 14, 0.3, 0)
    S['rivet'].scale = (1.6, 1.6, 1.6)
    w0 = on_wing(-1.4, 0.0)
    key(S, (0, 0, 0), (w0[0] + 2, w0[1] - 4, w0[2] + 3), w0, 700, 'FFE0C0')
    shoot(S, (0, 0, 0), (w0[0] + lerp(3.0, 2.6, k), w0[1] - lerp(5.6, 5.0, k), w0[2] + 1.5), (w0[0] - 0.2, w0[1] + 0.3, w0[2] + 0.9), 28)


def swat(S, k, t, lt):
    """Close: she brushes at her forearm again and again, insects circling, her mouth tight."""
    ridge(S, 'day', t, 0.2)
    br = math.sin(lt * 9)
    h = her_spot(S, 'pain', P('sit', aL=(0.85, -0.35, 1.45, 0.9), aR=(0.8 + 0.12 * br, -0.45, 1.5 + 0.12 * br, 0.9), lean=-0.2, head=(0.22, 0.3)))
    a = wpos(h.hands[0])
    for i, b in enumerate(S['bugs']):
        an = t * (3 + 2 * rnd(i, 811)) + 2 * PI * rnd(i, 812)
        b.location = (a[0] + (0.25 + 0.3 * rnd(i, 813)) * math.cos(an), a[1] - 0.15 + 0.2 * math.sin(an * 1.3), a[2] + 0.1 + (0.2 + 0.25 * rnd(i, 814)) * math.sin(an))
    hp = head(S, h)
    key(S, (0, 0, 0), (hp[0] - 1.5, hp[1] - 2, hp[2] + 2), hp, 420, 'FFF0C8')
    shoot(S, (0, 0, 0), (hp[0] - lerp(1.0, 0.8, k), hp[1] - lerp(2.7, 2.4, k), hp[2] - 0.35), (hp[0] - 0.05, hp[1] - 0.2, hp[2] - 0.3), 38)


def move_away(S, k, t, lt):
    """From up by the torn end of the fuselage, at dusk: she drags herself away from the wreck, down the slope, on her
    elbows."""
    ridge(S, 'day', t, 0.3, 'dusk', 0.8)
    x0, y0 = SPOT[0] - 0.4, SPOT[1] - 0.7
    x, y = lerp(x0, LIE[0], k), lerp(y0, LIE[1] + 0.6, k)
    dr = math.atan2(LIE[1] + 0.6 - y0, LIE[0] - x0)
    a = math.sin(lt * 1.3 * 2 * PI)
    put(S, S['her'], x, y, 0.42, dr + PI / 2, P('stand', aL=(2.4 + 0.4 * a, 0.3, 1.2 - 0.6 * a), aR=(2.4 - 0.4 * a, 0.3, 1.2 + 0.6 * a), head=(-0.9, 0.5),
                                               lL=(0.0, 0.2), lR=(0.0, 0.1)), 'hard', pitch=PI / 2 - 0.25)
    key(S, RIDGE, (-5, -6, 6), (x, y, 1), 4000, 'FFC8A0')
    shoot(S, RIDGE, (lerp(1.6, 1.2, k), lerp(-0.2, -0.6, k), g(1.4, -0.4) + lerp(3.4, 3.0, k)), (x - 0.4, y + 0.2, g(x, y) + 0.5), 30)


def sky_gap(S, k, t, lt):
    """Flat on her back, what she sees: the hole the jet cut in the trees, crowns swaying round it, first light, leaves
    coming slowly down."""
    ridge(S, 'day' if S['prm'].get('day') else 'dawn', t, 1.2)
    c = gp(LIE[0], LIE[1], 0.7)
    for i, d in enumerate(S['debris']):
        ph = (t * (0.1 + 0.08 * rnd(i, 821)) + rnd(i, 822)) % 1.0
        an = 2 * PI * rnd(i, 823) + 0.6 * math.sin(t * 0.7 + i)
        rr = 2.0 + 7.0 * rnd(i, 824)
        d.location = (c[0] + rr * math.cos(an), c[1] + rr * math.sin(an), c[2] + 16 - 13 * ph)
        d.rotation_euler = (t * 1.5 * rnd(i, 825), t * 1.1, t * rnd(i, 826))
    shoot(S, (0, 0, 0), c, (c[0] + 0.6, c[1] + 2.6, c[2] + 20), 18, roll=lerp(-0.25, 0.2, k))


def orange_xy(k):
    return lerp(6.4, 3.6, sm(k)), lerp(-5.6, -3.4, sm(k))


def orange_man(S, k, t, lt):
    """Morning mist: past her, lying where she has lain for days, a man in an orange jacket comes out of the trees below,
    sees her and stops dead. She lifts a hand."""
    ridge(S, 'morning', t, 0.3)
    u = sm(lt / 1.3)
    x, y = orange_xy(u)
    yw = facing(LIE[0] - x, LIE[1] + 1.0 - y)
    put(S, S['orange'], x, y, 0.0, yw, K.walk(lt, 1.2) if u < 0.97 else P('stand', aL=(0.3, 0.5, 0.4), aR=(0.3, 0.5, 0.4), lean=-0.12), 'wide' if u > 0.8 else 'calm')
    r = sm((lt - 1.2) / 0.6)
    lie(S, S['her'], LIE[0], LIE[1], 0.1, P('stand', aL=(0.2, 0.3, 0.6), aR=(lerp(0.3, 1.5, r), 0.2, lerp(0.8, 0.3, r)), head=(0.25, -0.4)), 'tired')
    o = head(S, S['orange'])
    key(S, (0, 0, 0), (o[0] - 3, o[1] - 2, o[2] + 3), o, 900, 'FFE8C0')
    shoot(S, RIDGE, (LIE[0] - lerp(1.9, 1.6, k), LIE[1] + lerp(3.3, 3.0, k), g(*LIE) + 2.2), (o[0] - 1.6, o[1] + 1.0, o[2] - 1.3), 32)


def orange_gone(S, k, t, lt):
    """Close on the man in orange: he stares, takes a step back, then turns and goes back into the trees."""
    ridge(S, 'morning', t, 0.3)
    x, y = orange_xy(1.0)
    yw = facing(LIE[0] - x, LIE[1] + 1.0 - y)
    u = sm((k - 0.62) / 0.2)
    w = sm((k - 0.7) / 0.3)
    o = put(S, S['orange'], x + 0.3 * u + 3.2 * w, y - 0.2 * u - 2.4 * w, 0.0, yw + 2.7 * u, K.walk(lt, 1.3) if u > 0.5 else P('stand', aL=(0.3, 0.5, 0.4), aR=(0.3, 0.5, 0.4), lean=-0.15),
            'wide')
    h = gp(x, y, 2.5)
    key(S, (0, 0, 0), (h[0] - 3, h[1] + 1, h[2] + 2), h, 600, 'FFE8C0')
    shoot(S, (0, 0, 0), (h[0] - lerp(2.6, 2.2, k), h[1] + lerp(1.3, 1.0, k), h[2] + 0.35), (h[0] + 1.2 * w, h[1] - 0.9 * w, h[2] + 0.2), 38)


def men_arrive(S, k, t, lt):
    """Day eight: men come down through the trees to the wreck, the police officer first, one with a clipboard, one with a
    dark bundle under his arm; she raises her arm; Rook stands up on the roof of the fuselage."""
    ridge(S, 'morning', t, 0.3)
    u = sm(k * 1.15)
    men = [S['officer']] + S['crew'][:3]
    for i, rig in enumerate(men):
        x = lerp(-6.6 - 0.9 * i, -3.2 - 0.75 * (i % 2) - 0.5 * i, u)
        y = lerp(7.4 + 0.9 * i, 0.9 + 1.25 * i, u)
        pose = K.walk(lt + 0.27 * i, 1.25) if u < 0.97 else P('stand', head=(0.3, 0.0))
        if i == 1:
            pose['aR'] = (0.9, 0.0, 1.5, 0.6)
        if i == 2:
            pose['aL'] = (0.3, 0.3, 1.2, 0.8)
        put(S, rig, x, y, 0.0, facing(LIE[0] - x, LIE[1] - y), pose, 'wide' if i == 0 else 'hard')
    hold(S, S['clip'], men[1], 1, (0, -0.2, 0.2), (0.5, 0, men[1].root.rotation_euler[2]))
    hold(S, S['bundle'], men[2], 0, (0, 0, 0.25), (0, 0, men[2].root.rotation_euler[2]))
    r = sm((lt - 0.5) / 0.6)
    lie(S, S['her'], LIE[0], LIE[1], 0.1, P('stand', aL=(0.2, 0.3, 0.6), aR=(lerp(0.3, 1.6, r), 0.2, 0.3), head=(0.1, 0.4)), 'wide')
    roof = wpos(S['fuse'], (-1.0, 0, 1.3))
    put(S, S['rook'], 0, 0, 0, 0.5, blend(P('sit', lean=0.2), P('stand', head=(0.1, 0.4)), sm((lt - 0.4) / 0.5)), 'shocked', o=roof)
    S['hat_jump'] = 0.25 * sm((lt - 0.4) / 0.2) * (1 - sm((lt - 0.9) / 0.3))
    key(S, RIDGE, (2, -8, 7), (-2, 1.5, 1.5), 2400, 'FFE8C0')
    shoot(S, RIDGE, (lerp(2.8, 2.4, k), lerp(-6.6, -6.0, k), lerp(2.6, 3.0, k)), (-1.2, 1.6, 2.9), 24)


def list_point(S, k, t, lt):
    """Close on the clipboard: a list of lines; her finger comes in and stops on one of them, and that line lights."""
    ridge(S, 'morning', t, 0.3)
    b = gp(LIE[0] + 0.4, LIE[1] - 0.4, 1.25)
    S['clip'].location, S['clip'].rotation_euler = b, (-0.45, 0, 0.12 + 0.02 * math.sin(lt * 2))
    S['hand_him'].place((b[0] - 0.62, b[1] - 0.08, b[2] - 0.25), (0.0, 0.0, PI / 2 + 0.5))
    S['hand_him'].grip(0.7)
    u = sm(lt / 1.0)
    tr = 0.012 * math.sin(lt * 21)
    S['hand_her'].place((b[0] + lerp(1.5, 0.62, u), b[1] - lerp(0.5, 0.2, u), b[2] - lerp(0.75, 0.3, u) + tr), (0.25, 0.0, -PI / 2 + 0.45))
    S['hand_her'].grip(0.25)
    on = sm((lt - 1.0) / 0.15)
    S['mark'].scale = (0.62 * max(0.001, on), 0.008, 0.06)
    key(S, (0, 0, 0), (b[0] + 1.5, b[1] - 2, b[2] + 2), b, 300, 'FFE8C0')
    shoot(S, (0, 0, 0), (b[0] + lerp(0.5, 0.35, k), b[1] - lerp(2.1, 1.8, k), b[2] + 0.75), (b[0] + 0.12, b[1], b[2] - 0.05), 38)


# ---------------------------------------------------------------- afterwards
def ward_bed(S, k, t, lt):
    """A hospital room, daylight in the window: she lies in bed, turns her head; Rook on the chair beside her nods."""
    use(S, 'ward', 'ward')['ceil'].hide_render = True
    u = sm((lt - 0.5) / 0.7)
    stand(S, S['her'], 'ward', -3.4, 0.95, 1.22, 0.0, P('stand', aL=(0.1, 0.3, 0.3), aR=(0.1, 0.3, 0.3), head=(0.45, lerp(-0.1, 0.6, u))), 'tired' if u < 0.6 else 'warm',
          pitch=-PI / 2 + 0.3)
    stand(S, S['rook'], 'ward', -1.2, 1.85, 0.05, -0.9, P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.7, -0.1, 1.5, 1.0), head=(0.2 + 0.2 * math.sin(lt * 3) * u, -0.3), lean=0.2), 'soft')
    lamp(S, 'ward', (-4, -3, 4), (-3, 2.5, 1.5), 700, 'FFF4E8')
    cam(S, 'ward', (lerp(-5.2, -4.9, k), lerp(-0.2, 0.2, k), 3.0), (-2.7, 3.0, 1.75), 32)


def walk_again(S, k, t, lt):
    """The same room on New Year's Eve: she walks, slowly, on a stick, across the floor; fireworks open in the window."""
    d = use(S, 'ward', 'wardnight')
    d['pane'].hide_render = True
    x = lerp(-1.4, 1.6, k)
    pose = K.walk(lt, 0.6)
    pose['aR'] = (0.35, 0.15, 0.5, 0.0)
    h = stand(S, S['her'], 'ward', x, -0.8, 0, PI / 2 - 0.55, pose, 'hard' if k < 0.6 else 'warm')
    hd = wpos(h.hands[1])
    S['stick'].location, S['stick'].rotation_euler = (hd[0] + 0.1, hd[1] - 0.05, hd[2] - 0.7), (0.05, 0.1, 0)
    for i, s in enumerate(S['sparks']):
        b = i % 3
        ph = (t * 0.55 + b / 3) % 1.0
        an = 2 * PI * (i // 3) / 8
        c = SP('ward', 0.5 + 1.3 * b, 16, 3.4 + 0.5 * (b % 2))
        rr = 2.6 * ph ** 0.6
        s.location = (c[0] + rr * math.cos(an), c[1], c[2] + rr * math.sin(an) - 1.2 * ph * ph)
        sc_ = max(0.02, 1.4 * (1 - ph))
        s.scale = (sc_, sc_, sc_)
    lamp(S, 'ward', (-1, -5, 4), (x, -0.8, 1.8), 800, 'FFF0E0')
    cam(S, 'ward', (lerp(0.2, 0.6, k), lerp(-7.0, -6.4, k), 2.0), (0.9, 1.0, 2.3), 30)


def jaime_phone(S, k, t, lt):
    """The trading floor: a colleague on his feet at his desk, telephone at his ear, shaking his head, his free hand
    coming down flat on the desk."""
    use(S, 'office', 'office')
    sl = sm((lt - 1.2) / 0.15)
    j = stand(S, S['jaime'], 'office', -4.6, 2.3, 0, facing(1.2, -3.0), P('stand', aR=(0.9, -0.1, 2.3, 0.9), aL=(lerp(1.3, 0.75, sl), 0.2, lerp(1.0, 0.35, sl)), lean=0.12 * sl,
                                                                       head=(0.05, 0.3 * math.sin(lt * 6.5))), 'hard')
    ear(S, S['phone'], j)
    talk(j, lt, 8.0, 0.4)
    lamp(S, 'office', (-2, -4, 5), (-4.6, 2.3, 2.2), 800, 'FFF0E0')
    cam(S, 'office', (lerp(-2.4, -2.8, k), lerp(-3.4, -2.8, k), 2.7), (-4.9, 2.2, 2.35), 34)


def party(S, y, lt):
    S['litter'].location, S['litter'].rotation_euler = SP('chapel', 0, y, 1.38 + 0.02 * math.sin(lt * 5)), (0, 0, 0)
    h = stand(S, S['her'], 'chapel', 0, y + 1.55, 1.48, PI, P('stand', aL=(0.1, 0.2, 0.3), aR=(0.1, 0.2, 0.3), head=(-0.15, 0.0)), 'sad', pitch=-PI / 2)
    for i, b in enumerate(S['bearers']):
        pose = K.walk(lt + 0.5 * i, 0.7)
        pose['aL'], pose['aR'] = (0.1, 0.3, 0.25, 0.0), (0.1, 0.3, 0.25, 0.0)
        stand(S, b, 'chapel', 0, y + (3.0 if i == 0 else -3.0), 0, PI, pose, 'hard')
    return h


def chapel_base(S):
    d = use(S, 'chapel', 'chapel')
    for i, l in enumerate(d['lamps']):
        l.data.energy = 90 + 20 * math.sin(S['T'] * 9 + i * 2)
    lamp(S, 'chapel', (0, 2, 8.5), (0, 9, 2), 3000, 'FFD8A0')
    return d


def funeral_aisle(S, k, t, lt):
    """A funeral hall in December, from high at the back: two bearers carry her on a stretcher up the aisle, between the
    mourners, towards a closed coffin under white flowers."""
    S['T'] = t
    chapel_base(S)
    party(S, lerp(-7.5, -2.5, k), lt)
    cam(S, 'chapel', (lerp(1.2, 0.8, k), lerp(-13.6, -12.6, k), lerp(6.2, 5.6, k)), (0, 5, 2.2), 28)


def funeral_close(S, k, t, lt):
    """Close on her face on the stretcher, moving past the benches, eyes on what is ahead of her."""
    S['T'] = t
    chapel_base(S)
    h = party(S, lerp(-2.5, 0.5, k), lt)
    hp = head(S, h)
    key(S, (0, 0, 0), (hp[0] + 1.0, hp[1] + 3.0, hp[2] + 2.5), hp, 300, 'FFD8A0')
    shoot(S, (0, 0, 0), (hp[0] + lerp(1.7, 1.5, k), hp[1] - 0.9, hp[2] + 0.8), (hp[0], hp[1] + 0.25, hp[2] + 0.05), 40)


def funeral_rook(S, k, t, lt):
    """Rook at the back of the hall, standing: he takes off his hat, holds it to his chest and bows his head."""
    S['T'] = t
    chapel_base(S)
    u = sm(lt / 1.0)
    stand(S, S['rook'], 'chapel', 2.9, -13.2, 0, PI + 0.3, blend(P('hat'), P('stand', aR=(0.9, -0.2, 1.6, 0.8), head=(0.45, 0.0)), u), 'sad')
    S['hat_off'] = u
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 2, h[1] + 4, h[2] + 2), h, 600, 'FFD8A0')
    shoot(S, (0, 0, 0), (h[0] - lerp(2.4, 2.1, k), h[1] + lerp(3.4, 3.0, k), h[2] + 0.1), (h[0] - 0.1, h[1], h[2] - 0.45), 34)


def desk_back(S, k, t, lt):
    """February: she is back at her desk, typing, her stick leaning against it; she looks up; Rook by the window tips his
    hat to her."""
    use(S, 'office', 'office')
    ty = math.sin(lt * 11)
    u = sm((lt - 1.0) / 0.5)
    stand(S, S['her'], 'office', 0, 1.72, 0, 0.0, P('sit', aR=(0.95, 0.0, 1.0 + 0.08 * ty, 0.3), aL=(0.95, 0.0, 1.0 - 0.08 * ty, 0.3), lean=0.2, head=(lerp(0.3, 0.0, u), lerp(0.0, 0.45, u)), **SEAT),
          'hard' if u < 0.5 else 'warm')
    S['stick'].location, S['stick'].rotation_euler = SP('office', 2.0, -0.12, 0.78), (0.0, 0.22, 0)
    S['phone'].location, S['phone'].rotation_euler = SP('office', -0.2, 0.75, 1.3), (0, PI / 2, 0.3)
    stand(S, S['rook'], 'office', 4.2, 2.8, 0, facing(-4.2, -2.6), P('hat') if u > 0.5 else P('cross'), 'soft')
    S['hat_tip'] = 0.4 * u
    lamp(S, 'office', (3, -5, 5), (0, 1.5, 1.6), 900, 'FFF4E0')
    cam(S, 'office', (lerp(3.6, 3.0, k), lerp(-5.4, -4.8, k), 2.4), (0.9, 1.7, 1.9), 32)


def family_walk(S, k, t, lt):
    """A city park in autumn, plain towers beyond the trees: she walks the path with her husband and their two children,
    the small one skipping; Rook on a bench flips his coin and watches them go by."""
    use(S, 'park', 'park')
    x0 = lerp(3.4, -1.6, k)
    yw = -PI / 2 + 0.35
    stand(S, S['her'], 'park', x0, 0.6, 0, yw, K.walk(lt, 1.1), 'warm')
    stand(S, S['jaime'], 'park', x0 + 0.5, -1.0, 0, yw, K.walk(lt + 0.3, 1.1), 'warm')
    for i, (kd, dx, dy, sc_) in enumerate(((S['kids'][0], -0.5, -0.2, 0.58), (S['kids'][1], 0.1, 1.7, 0.46))):
        kd.root.scale = (sc_, sc_, sc_)
        hop = 0.25 * abs(math.sin(lt * 5.5)) if i else 0.0
        stand(S, kd, 'park', x0 + dx, dy, hop, yw, K.walk(lt + 0.2 * i, 2.0 + 0.4 * i) if not i else P('up', aL=(2.2, 0.6, 0.3), aR=(2.2, 0.6, 0.3), lL=(0.5 * math.sin(lt * 11), 0.4), lR=(-0.5 * math.sin(lt * 11), 0.4)), 'warm')
    r = stand(S, S['rook'], 'park', -2.0, 2.85, 0.12, 0.25, P('sit', aR=(1.0, -0.1, 1.3, 0.3), head=(0.1, lerp(0.6, -0.1, k))), 'soft')
    rh = wpos(r.hands[1])
    fl = (lt * 1.0) % 1.0
    S['rivet'].location, S['rivet'].rotation_euler = (rh[0], rh[1] - 0.12, rh[2] + 0.1 + 2.2 * fl * (1 - fl)), (lt * 14, 0.3, 0)
    S['rivet'].scale = (1.6, 1.6, 1.6)
    lamp(S, 'park', (-6, -6, 6), (2, 0.5, 1.6), 1500, 'FFE8C0')
    cam(S, 'park', (lerp(-7.6, -7.0, k), lerp(-5.0, -4.4, k), 1.9), (0.2, 0.9, 1.75), 36)


def return_ridge(S, k, t, lt):
    """2006: she stands on a rock above the green ridges, looking out over them; Rook beside her takes off his hat; she
    turns her head to him."""
    S['range'].location = RANGE
    sky(S, 'high')
    co = S['rco']
    i = np.argmin((co[:, 0] - 30) ** 2 + (co[:, 1] + 40) ** 2)
    p = at(RANGE, 30, -40, co[i, 2] + 1.6)
    S['outcrop'].location = (p[0], p[1], p[2] - 0.7)
    for j, c in enumerate(S['clouds']):
        c.location = (-200 + 400 * rnd(j, 111) + 4 * t, 160 + 200 * rnd(j, 112), 95 + 30 * rnd(j, 113))
    u = sm((k - 0.45) / 0.3)
    put(S, S['her'], -0.8, 0.0, 0.0, PI + 0.2, P('stand', aL=(0.1, 0.2, 0.3), aR=(0.1, 0.2, 0.3), head=(lerp(-0.1, 0.0, u), lerp(0.0, -0.95, u))), 'calm' if u < 0.5 else 'warm', o=p)
    put(S, S['rook'], 1.0, 0.3, 0.0, PI - 0.5, blend(P('hat'), P('stand', aR=(0.9, -0.2, 1.6, 0.8), head=(0.1, 0.5)), u), 'soft', o=p)
    S['hat_off'] = u
    key(S, (0, 0, 0), (p[0] + 4, p[1] - 6, p[2] + 6), (p[0], p[1], p[2] + 2), 1500, 'FFF4E0')
    shoot(S, (0, 0, 0), (p[0] + lerp(3.4, 2.6, k), p[1] - lerp(6.6, 6.0, k), p[2] + lerp(3.4, 3.0, k)), (p[0] - 0.6, p[1] + 14, p[2] + 0.6), 30)


def writing(S, k, t, lt):
    """Evening at a desk by a tall window: she writes, page after page, the lamp on; then she stops and looks up."""
    d = use(S, 'study', 'study')
    d['lamps'][0].data.energy = 140
    u = sm((k - 0.72) / 0.18)
    wr = math.sin(lt * 9)
    h = stand(S, S['her'], 'study', 0.1, 1.5, 0, 0.0, P('sit', aR=(0.98 + 0.04 * wr, -0.22, 1.2 + 0.08 * math.sin(lt * 6.3), 0.3), aL=(0.85, 0.15, 1.15, 0.3), lean=lerp(0.32, 0.12, u),
                                                       head=(lerp(0.42, 0.0, u), lerp(0.1, -0.15, u)), **SEAT), 'calm' if u < 0.5 else 'warm')
    hold(S, S['pen'], h, 1, (0, -0.06, 0.02), (0.5, 0.2, 0))
    lamp(S, 'study', (2.5, -3, 4), (0.1, 1.4, 1.8), 520, 'FFD8B0')
    cam(S, 'study', (lerp(-2.4, -1.9, k), lerp(-4.8, -4.2, k), 2.5), (0.2, 1.3, 1.85), 34)


# ---------------------------------------------------------------- stills
def photo_thumb(S, k, t, lt):
    """The thumbnail picture: she sits against the root in the rain on the right of the frame, knees up, looking out;
    the broken fuselage behind her; the dark trees on the left for the words."""
    ridge(S, 'rain', t, 0.6, 'day', 0.45)
    her_spot(S, 'tired', P('sit', aL=(0.9, -0.1, 1.7, 1.0), aR=(0.9, -0.1, 1.7, 1.0), lL=(1.0, 2.1), lR=(1.0, 2.1), lean=0.0, head=(0.0, -0.35)))
    h = head(S, S['her'])
    key(S, (0, 0, 0), (h[0] - 2.5, h[1] - 3, h[2] + 2), h, 2600, 'F4F8F0')
    if 'camfill' in S:
        S['camfill'].data.energy = 260
    shoot(S, (0, 0, 0), (h[0] - 1.3, h[1] - 3.9, h[2] + 0.15), (h[0] - 1.25, h[1] + 0.6, h[2] - 0.35), 34)


def photo_wing(S, k, t, lt):
    """For the case board: the balls of insulation in a row on the wet wing."""
    ridge(S, 'rain', t, 0.4)
    w0 = on_wing(-0.9, -0.4)
    for i, b in enumerate(S['balls']):
        p = on_wing(-0.4 - 0.35 * i, -0.5 + 0.1 * (i % 2))
        b.location = (p[0], p[1], p[2] + 0.06)
    for i, d in enumerate(S['drips']):
        p = on_wing(-0.4 - 0.2 * i, -1.1)
        d.location = (p[0], p[1], p[2] - 0.2 - 0.1 * i)
    key(S, (0, 0, 0), (w0[0] + 1.5, w0[1] - 2, w0[2] + 2), w0, 360, 'E8F0E8')
    shoot(S, (0, 0, 0), (w0[0] + 0.9, w0[1] - 2.0, w0[2] + 1.0), (w0[0], w0[1], w0[2] + 0.05), 34)


NEW = (desk_trade, pasje_desk, apron_wide, apron_meet, apron_stairs, rook_apron, cabin_flight, cabin_drop, hands_grab, belt_empty, her_looks,
       trousers, man_talks, her_resolve, sip_wait, swat, move_away, sky_gap, orange_man, orange_gone, men_arrive, list_point, ward_bed, walk_again,
       jaime_phone, funeral_aisle, funeral_close, funeral_rook, desk_back, family_walk, return_ridge, writing)
SHOTS3D.update({f.__name__: f for f in NEW})
STILLS.update(thumb=photo_thumb, wing=photo_wing)

# The Short's shots were timed for about 1.4 s each; here they run about twice as long. Their acting is stretched over the
# whole shot, and every shot (old and new) also drifts a few degrees round its own subject and eases in, so a held frame
# keeps moving. prm "orb": [degrees, dolly, rise] sets the drift for one shot.
SHORT_KINDS = set(SHOTS3D) - {f.__name__ for f in NEW}
DRIFT = dict(aerial_canopy=12.0, sky_gap=0.0, hands_grab=3.0, list_point=4.0, belt_empty=14.0, cabin_flight=3.0, cabin_drop=3.0, crash_ridge=3.0, rook_lookout=22.0,
             night_wreck=18.0, rook_vigil=18.0, calm_face=16.0, apron_meet=18.0, jaime_phone=18.0, funeral_rook=18.0, wing_pov=16.0, desk_trade=16.0,
             pasje_desk=20.0, ward_bed=16.0, rook_apron=16.0, writing=20.0, man_beside=16.0, apron_stairs=14.0, seat_pin=12.0, move_away=14.0,
             desk_back=14.0, funeral_aisle=10.0, rook_wreck=12.0, her_looks=12.0)


def _stretched(f):
    def fn(S, k, t, lt):
        f(S, k, t, 1.5 * k)
    fn.__name__ = f.__name__
    return fn


def _drifting(f, name):
    sign = 1 if sum(map(ord, name)) % 2 else -1
    rate = DRIFT.get(name, 6.0)

    def fn(S, k, t, lt):
        f(S, k, t, lt)
        o = S['prm'].get('orb')
        deg, dolly, rise = (list(o) + [0, 0])[:3] if o else (sign * rate, 0.06 + 0.008 * rate, 0.0)
        c, tg = S['camrig'].location, S['camtgt'].location
        a = math.radians(deg) * (k - 0.5)
        m = 1 - dolly * (k - 0.5)
        dx, dy = c[0] - tg[0], c[1] - tg[1]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, c[2] + rise * (k - 0.5))
    fn.__name__ = f.__name__
    return fn


for _n in SHORT_KINDS:
    SHOTS3D[_n] = _stretched(SHOTS3D[_n])
SHOTS3D = {name: _drifting(f, name) for name, f in SHOTS3D.items()}
