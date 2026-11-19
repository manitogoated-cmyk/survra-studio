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
           'calm_face': 220, 'rook_vigil': 280, 'officer_trees': 160, 'officer_ghost': 180, 'rook_brim': 240,
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
        if math.hypot(x - SPOT[0], y - SPOT[1]) < 1.8 or math.hypot(x - WROOT[0], y - WROOT[1]) < 2.0 or math.hypot(x - FUS[0], y - FUS[1]) < 4.5:
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
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=120, size=1400, location=RANGE)
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
        add('ico_sphere', LEAF[i % 5], at(RANGE, px, py, co[k, 2] + 2), scale=(1, 1, 0.6), radius=7 + 5 * rnd(i, 103), subdivisions=1, parent=r, rough=0.8)
    S['lookout_crown'] = keep(add('ico_sphere', LEAF[1], FAR, scale=(1, 1, 0.5), radius=2.2, subdivisions=1, rough=0.8))
    S['clouds'] = []
    for i in range(10):
        S['clouds'].append(add('ico_sphere', 'F4F6F6', at(RANGE, -200 + 400 * rnd(i, 111), -40 + 300 * rnd(i, 112), 95 + 30 * rnd(i, 113)),
                               scale=(2.2, 1.2, 0.6), radius=22 + 14 * rnd(i, 114), subdivisions=2, parent=r, rough=1.0, alpha=0.75))
    S['range'] = r


# ---------------------------------------------------------------- people
def herfkens_head(head):
    d = K.human_head(SKIN, HAIR)(head)
    add('ico_sphere', HAIR, (0, 0.14, -0.2), scale=(1.0, 0.6, 1.0), radius=0.3, subdivisions=1, parent=head)        # shoulder-length hair
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
    p = at(RIDGE, lerp(-34, -6, u / 1.6), lerp(26, 19, u / 1.6), lerp(20.0, 15.5, u / 1.6))
    j.location = p
    j.rotation_euler = (0.32 + 0.1 * math.sin(u * 5), 0.12, -0.35)
    for i, dbr in enumerate(S['debris']):                                                                        # leaves and branches torn out
        ph = (u * 1.2 + rnd(i, 1)) % 1.0
        dbr.location = (p[0] + 4 + 6 * rnd(i, 2) - 8 * ph * rnd(i, 3), p[1] - 6 + 8 * rnd(i, 4), p[2] - 3 + 6 * ph - 6 * ph * ph + 2 * rnd(i, 5))
        dbr.rotation_euler = (u * 7 * rnd(i, 6), u * 5, u * 3 * rnd(i, 7))
    key(S, RIDGE, (-30, -10, 30), (p[0], p[1], p[2]), 40000, 'A8C0E0')
    shoot(S, RIDGE, (lerp(-3.0, -2.6, u / 1.6), lerp(-8.0, -7.4, u / 1.6), 3.0), (lerp(-16, -10, u / 1.6), 20, 15.0), 24, roll=-0.06)


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
    shoot(S, (0, 0, 0), (h[0] + 0.6, h[1] + lerp(1.3, 1.0, k), h[2] + 0.5), (w0[0] - 0.4, w0[1], w0[2] + 0.6), 30)


# ---------------------------------------------------------------- sponge
def rook_squeeze(S, k, t, lt):
    """Rook at the wing root pulls out a tuft of insulation and squeezes it; it springs back; he looks over at her."""
    ridge(S, 'day', t, 0.2)
    p = on_wing(-0.6, 0.1)
    sq = math.sin(min(lt, 1.2) * 7) * 0.5 + 0.5 if lt > 0.35 else 0.0
    look = sm((lt - 1.0) / 0.3)
    put(S, S['rook'], 0, 0, 0, -1.2 + 0.9 * look, P('stand', aR=(1.3, -0.2, 1.3, 0.3), aL=(1.2, 0.2, 1.4, 0.3), head=(0.35 - 0.3 * look, 0.0)),
        'shocked' if look > 0.5 else 'calm', o=p)
    hd = wpos(S['rook'].hands[1])
    S['tuft'].location = (hd[0], hd[1] - 0.15, hd[2] + 0.05)
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
        c.location = at(RANGE, -200 + 400 * rnd(i, 111) + 4 * t, -40 + 300 * rnd(i, 112), 95 + 30 * rnd(i, 113))
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
    lie(S, S['her'], SPOT[0], SPOT[1] - 0.6, 0.1, face='shut')
    flies(S, t, SPOT[0] + 1, SPOT[1], g(*SPOT) + 0.6)
    key(S, RIDGE, (-4, -6, 6), (SPOT[0], SPOT[1], 1), 900, '8AA8D8')
    shoot(S, RIDGE, (lerp(-5.5, -4.6, k), lerp(-8.0, -7.0, k), lerp(3.0, 2.6, k)), (1.0, 1.8, 1.6), 26)


def calm_face(S, k, t, lt):
    """Close on her face at night: eyes closed, breathing slowly and deliberately, the fear going out of it."""
    ridge(S, 'night', t, 0.2)
    lie(S, S['her'], SPOT[0], SPOT[1] - 0.6, 0.1, face='shut')
    br = 0.5 + 0.5 * math.sin(lt * 2.4)
    S['her'].body.scale = (1 + 0.03 * br, 1 + 0.05 * br, 1)
    flies(S, t, SPOT[0], SPOT[1] - 0.6, g(*SPOT) + 0.8, 6)
    h = head(S, S['her'])
    key(S, (0, 0, 0), (h[0] - 1, h[1] - 1, h[2] + 2.5), h, 160, '9AB8E8')
    shoot(S, (0, 0, 0), (h[0] + 0.2, h[1] - lerp(0.9, 0.8, k), h[2] + lerp(1.35, 1.2, k)), (h[0], h[1], h[2]), 40, roll=0.3)


def rook_vigil(S, k, t, lt):
    """Rook sits quietly beside her on a root, hat in his lap, keeping watch while she rests."""
    ridge(S, 'night', t, 0.2)
    lie(S, S['her'], SPOT[0], SPOT[1] - 0.6, 0.1, face='shut')
    sit(S, S['rook'], SPOT[0] - 1.0, SPOT[1] + 0.6, PI + 0.9, P('sit', aR=(0.7, -0.1, 1.2), aL=(0.7, -0.1, 1.2), head=(0.3, lerp(-0.2, 0.3, k))), 'soft', dz=0.2)
    S['hat_off'] = 1.0
    flies(S, t, SPOT[0] - 0.5, SPOT[1], g(*SPOT) + 1.0, 8)
    h = head(S, S['rook'])
    key(S, (0, 0, 0), (h[0] - 1, h[1] - 3, h[2] + 2), h, 400, '9AB8E8')
    shoot(S, (0, 0, 0), (h[0] - lerp(2.6, 2.2, k), h[1] - lerp(3.6, 3.1, k), h[2] - 0.2), (h[0] + 0.5, h[1] - 0.3, h[2] - 0.9), 30)


# ---------------------------------------------------------------- found
def officer_trees(S, k, t, lt):
    """Dawn mist in the trees: a man in a khaki uniform and cap pushes through the leaves and stops dead."""
    ridge(S, 'dawn', t, 0.2)
    u = sm(lt / 0.9)
    x, y = lerp(-6.4, -4.4, u), lerp(6.6, 3.8, u)
    pose = walk(lt) if u < 0.95 else P('stand', aL=(0.6, 0.6, 0.4), aR=(0.6, 0.6, 0.4), lean=-0.15)
    put(S, S['officer'], x, y, 0.0, -2.3, pose, 'wide' if u > 0.8 else 'calm')
    lie(S, S['her'], SPOT[0], SPOT[1] - 0.6, 0.1, face='tired')
    h = head(S, S['officer'])
    key(S, (0, 0, 0), (h[0] + 3, h[1] - 2, h[2] + 2), h, 700, 'FFC890')
    shoot(S, (0, 0, 0), (SPOT[0] + lerp(1.2, 1.0, k), SPOT[1] - lerp(1.6, 1.3, k), g(*SPOT) + 1.0), (h[0], h[1], h[2] - 0.6), 26)


def walk(lt):
    return K.walk(lt)


def officer_ghost(S, k, t, lt):
    """Close on the officer's face: eyes wide, he steps back, then points and shouts down the hill."""
    ridge(S, 'dawn', t, 0.2)
    back = sm(lt / 0.4)
    pt = sm((lt - 0.5) / 0.3)
    o = put(S, S['officer'], -4.4 - 0.3 * back, 3.8 + 0.3 * back, 0.0, -2.3,
            blend(P('stand', aL=(0.6, 0.6, 0.4), aR=(0.6, 0.6, 0.4), lean=-0.2), P('point', aR=(1.45, 0.6, 0.05), head=(0.0, 0.8)), pt), 'wide')
    o.jawv = 0.7 * pt
    h = head(S, o)
    key(S, (0, 0, 0), (h[0] + 2, h[1] - 2, h[2] + 1), h, 500, 'FFC890')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.0, 0.8, k), h[1] - lerp(1.9, 1.5, k), h[2] + 0.05), (h[0], h[1], h[2] - 0.05), 38)


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
    shoot(S, (0, 0, 0), (p[0] + 4.2, p[1] - 3.8, p[2] + 0.6), (p[0], p[1], p[2] - 0.3), 26)


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
