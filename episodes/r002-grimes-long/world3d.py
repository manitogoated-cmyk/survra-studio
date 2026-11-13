"""Case 002 in 3D - James Michael Grimes, Carnival Valor, November 2022. Sets built for this story only:
a harbour pier beside the liner, the sun deck, the lounge stage, a cabin corridor, the open Gulf (night, dawn, sunset),
the water under his feet, and a bulk carrier's bridge wing."""
import math

import bpy
import numpy as np

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(pier=(0, 0, 0), deck=(400, 0, 0), lounge=(800, 0, 0), hall=(1200, 0, 0), gulf=(0, 600, 0), under=(600, 600, 0),
           wing=(1200, 600, 0))
FAR = (0, 0, -700)
HOST = {'rook_pier', 'rook_go', 'rook_rail', 'lounge_wide', 'rook_clap', 'rook_peek', 'ship_leaves', 'rook_ring', 'fin_circle',
        'rook_wince', 'rook_socks', 'carrier_big', 'rook_hat', 'hoist_up', 'rook_dawn', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
JAMES = dict(top='B8442E', pants='2A3348', hand='E0A882', boot='E0A882', fore='E0A882')
CREW = dict(top='E8701E', pants='C85A14', hand='C68A5E', boot='20242B')
SWIM = dict(top='E8541E', pants='15181F', hand='15181F', boot='F2B531')
CONF = ('FF7A1A', 'FFD866', '3DDC84', '5EC8F0', 'F05A8C', 'FFFFFF')


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


# ---------------------------------------------------------------- vessels and props
def diamond(col, x, z, w, hgt, parent, **kw):
    """A square prism turned 45 degrees: the pointed end of a hull."""
    s = w / math.sqrt(2)
    return add('cube', col, (x, 0, z), rot=(0, 0, PI / 4), scale=(s, s, hgt), size=1, parent=parent, **kw)


def make_liner(r):
    """Cruise liner, bow toward +X, about 64 long. Generic livery: white, navy boot, orange stripe."""
    add('cube', 'F2EEE4', (0, 0, 2.6), scale=(52, 9, 4.4), size=1, parent=r)
    diamond('F2EEE4', 26, 2.6, 9, 4.4, r)
    add('cube', '1C2A4A', (0, 0, 0.2), scale=(52.2, 9.1, 1.4), size=1, parent=r)
    diamond('1C2A4A', 26, 0.2, 9.1, 1.4, r)
    add('cube', 'FF7A1A', (0, 0, 4.2), scale=(52.3, 9.15, 0.22), size=1, parent=r, emit=0.4)
    tiers = ((-2, 44, 8.4, 5.8, 2.0), (-4, 36, 7.6, 7.6, 1.6), (-6, 24, 6.6, 9.1, 1.4))
    for cx, ln, wd, z, hg in tiers:
        add('cube', 'E6E2D8', (cx, 0, z), scale=(ln, wd, hg), size=1, parent=r)
        n = int(ln / 4)
        for i in range(n):
            x = cx - ln / 2 + (i + 0.5) * ln / n
            for sy in (-1, 1):
                add('cube', 'FFD27A', (x, sy * (wd / 2 + 0.02), z + 0.1), scale=(ln / n * 0.72, 0.05, hg * 0.42), size=1, parent=r, emit=6)
        add('cube', 'FFD27A', (cx - ln / 2 - 0.02, 0, z + 0.1), scale=(0.05, wd * 0.8, hg * 0.42), size=1, parent=r, emit=6)
    for i in range(13):
        for sy in (-1, 1):
            add('cube', 'FFE7A8', (-24 + i * 4, sy * 4.53, 3.0), scale=(0.7, 0.05, 0.5), size=1, parent=r, emit=5)
    for i in range(3):
        add('cube', 'FFE7A8', (-26.03, -2.6 + i * 2.6, 3.0), scale=(0.05, 1.4, 0.6), size=1, parent=r, emit=5)
    add('cylinder', '20242B', (-10, 0, 11.3), scale=(1.5, 1, 1), radius=1.5, depth=3.2, vertices=8, parent=r)
    add('cylinder', 'FF7A1A', (-10, 0, 12.6), scale=(1.5, 1, 1), radius=1.56, depth=0.5, vertices=8, parent=r, emit=0.6)
    add('cylinder', 'C8C4B8', (10, 0, 10.6), radius=0.12, depth=3.4, vertices=5, parent=r)
    add('ico_sphere', 'FF4030', (10, 0, 12.4), radius=0.22, subdivisions=1, parent=r, emit=14)
    for i in range(8):
        add('ico_sphere', CONF[i % 5], (-2 + i * 1.8, (-1) ** i * 2.2, 10.2), radius=0.2, subdivisions=1, parent=r, emit=9)
    return r


def make_carrier(r):
    """Bulk carrier, bow toward +X, about 76 long."""
    add('cube', '7E2A22', (0, 0, 1.4), scale=(64, 10, 3.6), size=1, parent=r)
    diamond('7E2A22', 32, 1.4, 10, 3.6, r)
    add('cube', '1A1E26', (0, 0, 3.7), scale=(64.2, 10.1, 1.2), size=1, parent=r)
    diamond('1A1E26', 32, 3.7, 10.1, 1.2, r)
    add('cube', '4A4038', (0, 0, 4.35), scale=(63, 9.4, 0.12), size=1, parent=r)
    for i in range(5):
        add('cube', 'A8662E', (-14 + i * 9.5, 0, 4.9), scale=(7.2, 7.4, 1.0), size=1, parent=r)
        add('cube', '6A3E1E', (-14 + i * 9.5, 0, 5.44), scale=(7.4, 0.5, 0.1), size=1, parent=r)
    add('cube', 'E4E0D4', (-26, 0, 8.4), scale=(8, 8.6, 8), size=1, parent=r)
    add('cube', 'E4E0D4', (-25.5, 0, 12.0), scale=(5, 13, 0.4), size=1, parent=r)
    add('cube', 'FFE7A8', (-21.97, 0, 11.0), scale=(0.06, 7.6, 1.0), size=1, parent=r, emit=7)
    for sy in (-1, 1):
        add('cube', 'FFE7A8', (-25, sy * 4.33, 11.0), scale=(4.6, 0.06, 1.0), size=1, parent=r, emit=7)
        for z in (6.2, 8.4):
            add('cube', 'FFD27A', (-25.5, sy * 4.33, z), scale=(5.5, 0.06, 0.6), size=1, parent=r, emit=5)
    for z in (6.2, 8.4):
        add('cube', 'FFD27A', (-21.97, 0, z), scale=(0.06, 6.4, 0.6), size=1, parent=r, emit=5)
    add('cylinder', '1A1E26', (-28.5, 0, 14.0), radius=1.3, depth=4.0, vertices=6, parent=r)
    add('cylinder', 'F2B531', (-28.5, 0, 15.6), radius=1.36, depth=0.6, vertices=6, parent=r)
    add('cylinder', 'C8C4B8', (-24.5, 0, 14.6), radius=0.14, depth=5.0, vertices=5, parent=r)
    add('ico_sphere', 'FFFFFF', (-24.5, 0, 17.2), radius=0.3, subdivisions=1, parent=r, emit=20)
    add('cylinder', 'C8C4B8', (30, 0, 6.6), radius=0.14, depth=4.6, vertices=5, parent=r)
    add('ico_sphere', 'FFFFFF', (30, 0, 9.0), radius=0.26, subdivisions=1, parent=r, emit=18)
    add('ico_sphere', '3DDC84', (-22.5, -6.4, 12.4), radius=0.24, subdivisions=1, parent=r, emit=16)
    add('ico_sphere', 'FF4030', (-22.5, 6.4, 12.4), radius=0.24, subdivisions=1, parent=r, emit=16)
    return r


def make_helo(r):
    """Rescue helicopter, nose toward +X. Generic white and orange."""
    add('ico_sphere', 'F2F2EE', (0, 0, 0), scale=(2.7, 1.15, 1.2), radius=1.0, subdivisions=2, parent=r)
    add('cube', 'E8541E', (-0.4, 0, 0.1), scale=(1.1, 2.36, 1.9), size=1, parent=r)
    add('cube', '0E1520', (1.9, 0, 0.25), scale=(1.2, 1.7, 0.8), size=1, parent=r, rough=0.2)
    add('cylinder', 'F2F2EE', (-4.2, 0, 0.45), rot=(0, PI / 2, 0), radius=0.3, depth=4.6, vertices=6, parent=r)
    add('cube', 'E8541E', (-6.5, 0, 1.2), rot=(0, -0.5, 0), scale=(1.0, 0.14, 1.9), size=1, parent=r)
    add('cube', '15181F', (0, -1.2, -0.1), scale=(1.3, 0.08, 1.3), size=1, parent=r)
    add('cylinder', '20242B', (0, 0, 1.3), radius=0.3, depth=0.5, vertices=6, parent=r)
    rotor = empty((0, 0, 1.6), r)
    for a in (0, PI / 2):
        add('cube', '20242B', (0, 0, 0), rot=(0, 0, a), scale=(11.5, 0.42, 0.06), size=1, parent=rotor)
    tail = empty((-6.7, -0.25, 1.9), r)
    for a in (0, PI / 2):
        add('cube', '20242B', (0, 0, 0), rot=(0, a, 0), scale=(2.0, 0.05, 0.2), size=1, parent=tail)
    for sx in (1.2, -1.4):
        for sy in (-1, 1):
            add('cylinder', '15181F', (sx, sy * 0.95, -1.25), rot=(PI / 2, 0, 0), radius=0.3, depth=0.25, vertices=8, parent=r)
    add('ico_sphere', 'FF4030', (-6.8, 0, 2.3), radius=0.14, subdivisions=1, parent=r, emit=20)
    add('ico_sphere', 'FFF8E0', (1.2, 0, -1.15), radius=0.3, subdivisions=1, parent=r, emit=30)
    aim = empty((3.5, 0, -20), r)
    spot = light((1.2, 0, -1.3), 0, 'FFF4D0', kind='SPOT', spot=0.5, target=aim, parent=r)
    cone = add('cone', 'FFF4D0', (2.2, 0, -7.5), rot=(0, -0.17, 0), radius1=3.0, radius2=0.2, depth=12.5, vertices=10, parent=r, emit=0.3, alpha=0.07)
    cable = add('cylinder', 'D8D8D8', (0, -1.5, -0.5), radius=0.035, depth=1.0, vertices=5, parent=r, emit=0.5)
    return dict(helo=r, rotor=rotor, trotor=tail, hspot=spot, hcone=cone, haim=aim, cable=cable)


def make_ring(r):
    add('torus', 'F2621E', (0, 0, 0), major_radius=0.66, minor_radius=0.19, major_segments=12, minor_segments=5, parent=r, rough=0.6)
    for i in range(4):
        a = i * PI / 2 + PI / 4
        add('cube', 'F4F0E6', (math.cos(a) * 0.66, math.sin(a) * 0.66, 0), rot=(0, 0, a), scale=(0.42, 0.3, 0.42), size=1, parent=r)


# ---------------------------------------------------------------- sets
def set_pier(r):
    add('cube', '4A3A2E', (0, -1, -0.2), scale=(26, 14, 0.4), size=1, parent=r)
    for i in range(-12, 13):
        add('cube', '2E241C', (i * 1.05, -1, 0.005), scale=(0.06, 14, 0.02), size=1, parent=r)
    add('plane', '0A2238', (0, 0, -2.4), size=500, parent=r, rough=0.2)
    # the liner's side towering over the quay
    add('cube', '8E94A6', (0, 10.5, 9.0), scale=(70, 4, 15), size=1, parent=r)
    add('cube', '1C2A4A', (0, 10.45, 0.6), scale=(70.2, 4.1, 3.4), size=1, parent=r)
    add('cube', 'FF7A1A', (0, 8.46, 2.5), scale=(70, 0.06, 0.3), size=1, parent=r, emit=0.6)
    for row in range(5):
        add('cube', '6E7488', (0, 8.47, 5.25 + row * 2.2), scale=(70, 0.05, 0.12), size=1, parent=r)
        for i in range(-12, 13):
            add('cube', 'FFD27A', (i * 1.7, 8.47, 4.4 + row * 2.2), scale=(0.9, 0.06, 0.6), size=1, parent=r,
                emit=2.0 if (i * 7 + row * 3) % 4 else 0.15)
    # gangway on the left
    add('cube', '9AA0B4', (-4.6, 5.2, 1.55), rot=(0.43, 0, 0), scale=(1.7, 7.4, 0.12), size=1, parent=r)
    for sx in (-1, 1):
        add('cylinder', 'E8E4D8', (-4.6 + sx * 0.85, 5.2, 2.65), rot=(PI / 2 + 0.43, 0, 0), radius=0.05, depth=7.4, vertices=5, parent=r)
        for j in range(4):
            add('cylinder', 'E8E4D8', (-4.6 + sx * 0.85, 2.6 + j * 1.8, 0.95 + j * 0.82), radius=0.04, depth=1.1, vertices=5, parent=r)
    add('cube', '15181F', (-4.6, 8.44, 4.3), scale=(1.9, 0.08, 2.6), size=1, parent=r)
    add('cube', 'FFB060', (-4.6, 8.42, 4.3), scale=(1.5, 0.08, 2.2), size=1, parent=r, emit=2.2)
    light((-4.6, 7.2, 4.2), 220, 'FF9A3A', kind='POINT', parent=r)
    # quay furniture
    add('cylinder', '20242B', (3.6, 2.2, 2.4), radius=0.09, depth=4.8, vertices=6, parent=r)
    add('cube', '20242B', (3.2, 2.2, 4.75), scale=(1.0, 0.12, 0.1), size=1, parent=r)
    add('cone', 'FFD9A0', (2.8, 2.2, 4.55), radius1=0.34, radius2=0.12, depth=0.3, vertices=8, parent=r, emit=4)
    light((2.8, 2.2, 4.2), 300, 'FFD9A0', kind='POINT', parent=r)
    for x, y in ((-1.8, 3.4), (5.4, 3.4)):
        add('cylinder', '15181F', (x, y, 0.4), radius=0.3, depth=0.8, vertices=8, parent=r)
        add('cylinder', 'FF7A1A', (x, y, 0.86), radius=0.4, depth=0.14, vertices=8, parent=r)
    add('cube', '6A4A2E', (2.4, 3.6, 0.5), scale=(1.3, 1.0, 1.0), size=1, parent=r)
    add('cube', '8A6238', (2.7, 3.5, 1.35), rot=(0, 0, 0.3), scale=(0.9, 0.7, 0.7), size=1, parent=r)
    add('cube', '2E6A78', (1.3, 3.3, 0.36), rot=(0, 0, -0.2), scale=(0.9, 0.4, 0.72), size=1, parent=r)
    add('cylinder', 'C8B48A', (-1.8, 3.4, 0.2), rot=(0, 0, 0), radius=0.5, depth=0.16, vertices=10, parent=r)
    aim = empty((0, 0, 1.9), r)
    light((4.6, -5.5, 4.6), 1300, 'FFE2B8', 3.0, aim, parent=r)
    light((-5.0, 4.0, 5.2), 2000, 'FF7A1A', 1.5, aim, parent=r)
    light((-5.0, -5, 1.8), 220, '5E8FD0', 4.0, aim, parent=r)
    pick = add('cone', 'FFC233', (0, 0, -5), radius1=0.13, radius2=0.0, depth=0.03, vertices=3, parent=None, rough=0.25, emit=1.6)
    return dict(pick=pick)


def set_deck(r):
    add('cube', '2E5A62', (0, 2, -0.15), scale=(34, 16, 0.3), size=1, parent=r)
    for i in range(-11, 12):
        add('cube', 'D8D4C8', (i * 1.5, 2, 0.005), scale=(0.05, 16, 0.02), size=1, parent=r)
    for i in range(-9, 10):
        add('cylinder', 'F2EEE4', (i * 1.7, 5.6, 0.7), radius=0.055, depth=1.4, vertices=5, parent=r)
    for z in (0.75, 1.4):
        add('cylinder', 'F2EEE4', (0, 5.6, z), rot=(0, PI / 2, 0), radius=0.05, depth=34, vertices=5, parent=r)
    add('cube', '8A5A34', (0, 5.6, 1.46), scale=(34, 0.2, 0.08), size=1, parent=r)
    add('plane', '5A3A6A', (0, 220, -9), size=640, parent=r, rough=0.2)
    add('circle', 'FFB060', (-3.5, 420, 6), rot=(PI / 2, 0, 0), radius=30, vertices=20, fill_type='NGON', parent=r, emit=7)
    add('cube', 'E0522E', (0, 470, 12), scale=(1400, 1, 40), size=1, parent=r, emit=1.6)
    # loungers and a striped parasol
    for x in (-3.4, 3.2):
        add('cube', 'F2EEE4', (x, 3.4, 0.45), rot=(0, 0, 0.2), scale=(0.9, 2.2, 0.12), size=1, parent=r)
        add('cube', 'FF7A1A', (x - 0.2, 4.3, 0.75), rot=(0.6, 0, 0.2), scale=(0.9, 0.9, 0.1), size=1, parent=r)
    add('cylinder', 'C8C4B8', (-5.2, 4.0, 1.6), radius=0.05, depth=3.2, vertices=5, parent=r)
    add('cone', 'F05A8C', (-5.2, 4.0, 3.3), radius1=1.7, radius2=0.05, depth=0.7, vertices=8, parent=r)
    bulbs = []
    for i in range(12):
        x = -8 + i * 1.45
        bulbs.append(add('ico_sphere', CONF[i % 5], (x, 3.2, 4.2 - 0.5 * math.sin((i + 0.5) / 12 * PI)), radius=0.13, subdivisions=1, parent=r, emit=10))
    add('cylinder', '20242B', (-8.6, 3.2, 2.2), radius=0.06, depth=4.4, vertices=5, parent=r)
    add('cylinder', '20242B', (8.6, 3.2, 2.2), radius=0.06, depth=4.4, vertices=5, parent=r)
    aim = empty((0, 2, 1.8), r)
    light((6, 60, 10), 90000, 'FF9A50', 10.0, aim, parent=r)
    light((-5, -8, 5), 2200, 'FFD8C0', 6.0, aim, parent=r)
    light((7, -6, 2), 700, '9A8AE8', 5.0, aim, parent=r)
    return dict(bulbs=bulbs)


def set_lounge(r):
    add('plane', '1E1430', (0, 0, 0), size=40, parent=r)
    add('cube', '2A1A44', (0, 6.5, 5), scale=(30, 0.3, 10), size=1, parent=r)
    for i in range(-9, 10):
        add('cube', '8A1E3A' if i % 2 else '6A1630', (i * 0.95, 6.2, 4.2), scale=(0.9, 0.2, 7.0), size=1, parent=r)
    add('cube', '3A2A22', (0, 3.2, 0.3), scale=(11, 6, 0.6), size=1, parent=r)
    add('cube', 'FF7A1A', (0, 0.18, 0.5), scale=(11, 0.06, 0.16), size=1, parent=r, emit=6)
    add('cube', 'FFD866', (0, 6.0, 7.3), scale=(8.5, 0.1, 1.3), size=1, parent=r, emit=1.6)
    for sx in (-1, 1):
        add('cube', '15181F', (sx * 4.6, 3.6, 1.5), scale=(1.1, 0.9, 1.8), size=1, parent=r)
        add('cylinder', '2A2E38', (sx * 4.6, 3.12, 1.7), rot=(PI / 2, 0, 0), radius=0.36, depth=0.06, vertices=10, parent=r)
        add('cylinder', '2A2E38', (sx * 4.6, 3.12, 1.0), rot=(PI / 2, 0, 0), radius=0.22, depth=0.06, vertices=10, parent=r)
    add('cylinder', '9AA0B4', (1.6, 3.4, 1.35), radius=0.03, depth=1.5, vertices=5, parent=r)
    add('ico_sphere', '20242B', (1.6, 3.4, 2.15), radius=0.09, subdivisions=1, parent=r)
    add('cube', '15181F', (0, 2.6, 9.2), scale=(12, 0.2, 0.2), size=1, parent=r)
    spots = []
    for i, (x, col) in enumerate(((-3.6, 'F05A8C'), (0.0, 'FFD27A'), (3.6, '5EC8F0'))):
        add('cylinder', '20242B', (x, 2.6, 8.9), rot=(0.5, 0, 0), radius=0.26, depth=0.5, vertices=8, parent=r)
        aim = empty((x * 0.25, 2.6, 1.6), r)
        spots.append((light((x, 2.4, 8.6), 5200, col, kind='SPOT', spot=0.55, target=aim, parent=r), aim))
    add('ico_sphere', 'E8E8F0', (0, -1.0, 8.6), radius=0.5, subdivisions=2, parent=r, rough=0.1, emit=0.5)
    crowd = []
    k = 0
    for row, y in enumerate((-3.2, -5.0, -6.8)):
        for i in range(-4, 5):
            if i in (0, 1):
                continue
            c = empty((i * 1.25 + (row % 2) * 0.6, y, 0), r)
            col = ('2A2244', '34264E', '221C3A')[k % 3]
            add('cone', col, (0, 0, 1.1), radius1=0.5, radius2=0.3, depth=2.2, vertices=6, parent=c)
            add('ico_sphere', col, (0, 0, 2.5), radius=0.3, subdivisions=1, parent=c)
            for sx in (-1, 1):
                add('cylinder', col, (sx * 0.42, 0, 2.5), rot=(0, sx * 0.35, 0), radius=0.08, depth=1.0, vertices=5, parent=c)
            crowd.append(c)
            k += 1
    aim = empty((0, 1.5, 2.2), r)
    fill = light((3.5, -7.5, 4.0), 700, 'B8A0FF', 5.0, aim, parent=r)
    light((-6, 4, 6), 900, 'FF7A1A', 3.0, aim, parent=r)
    return dict(spots=spots, crowd=crowd, lfill=fill)


def set_hall(r):
    add('cube', '7A2434', (0, 6, -0.1), scale=(4.4, 40, 0.2), size=1, parent=r)
    add('cube', 'C8A44A', (0, 6, 0.005), scale=(0.5, 40, 0.02), size=1, parent=r)
    add('cube', 'CFC4AE', (0, 6, 3.7), scale=(4.4, 40, 0.2), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', 'D8CDB8', (sx * 2.2, 6, 1.8), scale=(0.2, 40, 3.8), size=1, parent=r)
        add('cube', '6A4226', (sx * 2.08, 6, 0.55), scale=(0.06, 40, 1.1), size=1, parent=r)
        add('cylinder', 'C8A44A', (sx * 2.02, 6, 1.15), rot=(PI / 2, 0, 0), radius=0.05, depth=40, vertices=5, parent=r, rough=0.35)
        for j, y in enumerate(range(-8, 21, 5)):
            yy = y + (2.5 if sx > 0 else 0)
            add('cube', '2E6A78', (sx * 2.07, yy, 1.35), scale=(0.08, 1.3, 2.7), size=1, parent=r)
            add('cube', 'C8A44A', (sx * 2.02, yy, 2.2), scale=(0.04, 0.36, 0.2), size=1, parent=r, rough=0.3)
            add('ico_sphere', 'C8A44A', (sx * 1.98, yy + 0.45, 1.3), radius=0.07, subdivisions=1, parent=r, rough=0.3)
    lamps = []
    for y in (-6, 0, 6, 12, 18):
        add('cylinder', 'FFE7B8', (0, y, 3.56), radius=0.34, depth=0.08, vertices=10, parent=r, emit=4)
        lamps.append(light((0, y, 3.2), 170, 'FFD9A0', kind='POINT', parent=r))
    # the end wall with the restroom door
    add('cube', 'C8BCA4', (0, 22, 1.8), scale=(4.4, 0.2, 3.8), size=1, parent=r)
    add('cube', '0A0C10', (0, 21.88, 1.4), scale=(1.5, 0.06, 2.8), size=1, parent=r)
    add('cube', '5EC8F0', (0, 21.86, 3.1), scale=(1.0, 0.06, 0.4), size=1, parent=r, emit=5)
    hinge = empty((-0.75, 21.8, 0), r)
    add('cube', 'E4E0D4', (0.75, 0, 1.4), scale=(1.5, 0.08, 2.8), size=1, parent=hinge)
    add('cube', 'C8A44A', (1.3, -0.07, 1.4), scale=(0.08, 0.06, 0.5), size=1, parent=hinge, rough=0.3)
    aim = empty((0, 4, 1.8), r)
    fill = light((1.2, -9, 2.4), 300, 'FFE2C8', 3.0, aim, parent=r)
    return dict(hinge=hinge, lamps=lamps, hfill=fill, haimp=aim)


def set_gulf(r):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=64, y_subdivisions=64, size=260, location=ORG['gulf'])
    sea = bpy.context.object
    sea.data.materials.append(K.mat('0B2C46', 0.42))
    co = np.zeros(len(sea.data.vertices) * 3)
    sea.data.vertices.foreach_get('co', co)
    xy = co.reshape(-1, 3)[:, :2].copy()
    liner = make_liner(empty((0, 0, -60), r))
    carrier = make_carrier(empty((0, 0, -90), r))
    h = make_helo(empty((0, 0, -120), r))
    ring = empty((0, 0, -30), r)
    make_ring(ring)
    fin = empty((0, 0, -30), r)
    add('cone', '39424E', (0, 0, 0.45), scale=(1.0, 0.22, 1.0), radius1=0.55, radius2=0.0, depth=1.1, vertices=4, parent=fin)
    add('cube', '39424E', (-0.3, 0, 0.3), rot=(0, 0.5, 0), scale=(0.5, 0.1, 0.5), size=1, parent=fin)
    stick = empty((0, 0, -30), r)
    add('cylinder', 'C8B46A', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.06, depth=1.5, vertices=6, parent=stick)
    for x in (-0.45, 0.0, 0.42):
        add('cylinder', '8A7A3A', (x, 0, 0), rot=(0, PI / 2, 0), radius=0.075, depth=0.05, vertices=6, parent=stick)
    moon = add('circle', 'E8F0FF', (-60, 380, 150), rot=(PI / 2 - 0.35, 0, 0), radius=20, vertices=20, fill_type='NGON', parent=r, emit=7)
    sun = add('circle', 'FFC070', (0, 480, -100), rot=(PI / 2, 0, 0), radius=38, vertices=22, fill_type='NGON', parent=r, emit=8)
    band = add('cube', 'E0522E', (0, 520, -200), scale=(2400, 1, 46), size=1, parent=r, emit=1.5)
    aim = empty((0, 0, 2), r)
    moonl = light((-30, 70, 50), 60000, '9AB8E8', 12.0, aim, parent=r)
    sunl = light((0, 130, 14), 0, 'FF9A50', 30.0, aim, parent=r)
    return dict(sea=sea, xy=xy, liner=liner, carrier=carrier, ring=ring, fin=fin, stick=stick, moon=moon, sun=sun, band=band,
                moonl=moonl, sunl=sunl, **h)


def set_under(r):
    top = add('plane', '5AA8B8', (0, 0, 6), rot=(PI, 0, 0), size=400, parent=r, emit=0.7)
    aim = empty((0, 0, 3.5), r)
    light((3, -2, 5.6), 5000, '8ADCE8', 8.0, aim, parent=r)
    light((-6, -9, 1), 900, '3A8AA8', 5.0, aim, parent=r)
    thing = empty((0, 0, -40), r)
    add('ico_sphere', '2A3640', (0, 0, 0), scale=(2.6, 0.9, 0.62), radius=1.0, subdivisions=2, parent=thing)
    add('cube', '34424E', (2.35, 0, -0.08), scale=(0.9, 1.5, 0.34), size=1, parent=thing)
    add('cone', '2A3640', (-0.2, 0, 0.85), rot=(0, -0.45, 0), scale=(1.0, 0.2, 1.0), radius1=0.6, radius2=0.0, depth=1.2, vertices=4, parent=thing)
    tail = empty((-2.5, 0, 0), thing)
    add('cone', '2A3640', (-0.7, 0, 0), rot=(0, PI / 2, 0), scale=(1.0, 0.25, 1.0), radius1=0.9, radius2=0.1, depth=1.5, vertices=4, parent=tail)
    for sy in (-1, 1):
        add('cube', '2A3640', (0.6, sy * 1.0, -0.2), rot=(0.3 * sy, 0, sy * -0.5), scale=(1.1, 0.9, 0.1), size=1, parent=thing)
        add('ico_sphere', 'D8E8F0', (2.3, sy * 0.62, 0.16), radius=0.08, subdivisions=1, parent=thing, emit=2)
    return dict(thing=thing, ttail=tail, utop=top)


def set_wing(r):
    add('cube', '3A4048', (0, 0, -0.1), scale=(9, 5, 0.2), size=1, parent=r)
    for i in range(-4, 5):
        add('cube', '20242B', (i * 1.0, 0, 0.005), scale=(0.06, 5, 0.02), size=1, parent=r)
    add('cube', '7E8492', (0, 2.6, 2.4), scale=(9, 0.3, 5), size=1, parent=r)
    add('cube', 'FFE7A8', (-1.5, 2.42, 2.9), scale=(3.4, 0.06, 1.3), size=1, parent=r, emit=1.1)
    add('cube', '20242B', (-1.5, 2.4, 2.9), scale=(0.1, 0.08, 1.4), size=1, parent=r)
    add('cube', '8A2A22', (2.6, 2.42, 1.6), scale=(1.3, 0.1, 3.0), size=1, parent=r)
    add('cylinder', '20242B', (2.6, 2.34, 2.3), rot=(PI / 2, 0, 0), radius=0.3, depth=0.08, vertices=10, parent=r)
    for i in range(-4, 5):
        add('cylinder', 'F2EEE4', (i * 1.1, -2.3, 0.7), radius=0.05, depth=1.4, vertices=5, parent=r)
    for z in (0.75, 1.4):
        add('cylinder', 'F2EEE4', (0, -2.3, z), rot=(0, PI / 2, 0), radius=0.05, depth=9.4, vertices=5, parent=r)
    add('ico_sphere', 'F2621E', (-3.6, 2.3, 1.7), scale=(1, 0.3, 1), radius=0.6, subdivisions=1, parent=r)
    lamp = empty((3.4, -1.9, 2.3), r, (0, 0, 0))
    add('cylinder', '20242B', (0, 0, -1.1), radius=0.07, depth=2.3, vertices=5, parent=lamp)
    add('cylinder', '2A2E38', (0, -0.1, 0.1), rot=(PI / 2 - 0.5, 0, 0), radius=0.38, depth=0.5, vertices=8, parent=lamp)
    add('cylinder', 'FFF8E0', (0, -0.33, -0.03), rot=(PI / 2 - 0.5, 0, 0), radius=0.32, depth=0.06, vertices=8, parent=lamp, emit=25)
    add('plane', '06182A', (0, -60, -22), size=400, parent=r, rough=0.25)
    aim = empty((0, 0, 2.2), r)
    light((-3, -6, 4.5), 700, 'FFE2C8', 4.0, aim, parent=r)
    light((4, 1.5, 5), 900, 'FF7A1A', 2.0, aim, parent=r)
    light((5, -6, 1.5), 300, '5E8FD0', 4.0, aim, parent=r)
    return dict(wlamp=lamp)


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('pier', set_pier), ('deck', set_deck), ('lounge', set_lounge), ('hall', set_hall), ('gulf', set_gulf),
                     ('under', set_under), ('wing', set_wing)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['james'] = K.Rig(JAMES, K.human_head('E0A882', '5A3A22'))
    S['crew'] = K.Rig(CREW, K.human_head('C68A5E', 'F2B531'))
    S['swimmer'] = K.Rig(SWIM, K.human_head('D8A07A', 'F2F2EE'))
    socks = empty((0, 0, -0.1), S['james'].hands[1])
    for dx in (-0.07, 0.08):
        add('cube', 'F8F8F4', (dx, 0, -0.26), rot=(0, dx * 3, 0), scale=(0.12, 0.1, 0.5), size=1, parent=socks, emit=0.8)
        add('cube', 'F8F8F4', (dx, -0.1, -0.5), scale=(0.12, 0.3, 0.12), size=1, parent=socks, emit=0.8)
    S['socks'] = [socks] + list(socks.children)
    bino = add('cube', '15181F', (0, -0.36, 0.05), scale=(0.34, 0.26, 0.14), size=1, parent=S['crew'].head)
    S['bino'] = bino
    S['spray'] = [add('ico_sphere', 'E8F4FF', FAR, radius=0.08, subdivisions=1, emit=1.0) for _ in range(30)]
    S['conf'] = [add('cube', CONF[i % 6], FAR, scale=(0.14, 0.02, 0.2), size=1, emit=2.0) for i in range(30)]
    S['kw'], S['kwa'] = None, empty()
    S['kc'], S['kca'] = None, empty()
    S['kw'] = light((0, 0, 0), 0, 'FFDCB8', 4.0, S['kwa'])
    S['kc'] = light((0, 0, 0), 0, 'A8C4F0', 5.0, S['kca'])
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
    """Move one of the two free key lights (kw warm, kc cool) to light this shot's subject."""
    S[which].location, S[which + 'a'].location = pos, look
    S[which].data.energy = energy


def reset(S):
    for who in ('rook', 'james', 'crew', 'swimmer'):
        S[who].place(FAR)
        S[who].apply(P())
        S[who].root.scale = (1, 1, 1)
    for o in S['spray'] + S['conf']:
        o.location = FAR
        o.scale = (1, 1, 1)
    for o in S['socks']:
        o.hide_render = True
    S['face'] = dict(rook='calm', james='calm', crew='calm', swimmer='calm')
    S['hat_tip'] = 0.0
    S['chew'] = 0.0
    for kk in ('kw', 'kc'):
        S[kk].data.energy = 0
    S['liner'].location, S['liner'].rotation_euler, S['liner'].scale = (0, 0, -60), (0, 0, 0), (1, 1, 1)
    S['carrier'].location, S['carrier'].rotation_euler, S['carrier'].scale = (0, 0, -90), (0, 0, 0), (1, 1, 1)
    S['helo'].location, S['helo'].rotation_euler, S['helo'].scale = (0, 0, -120), (0, 0, 0), (2.0, 2.0, 2.0)
    S['hspot'].data.energy = 0
    S['hcone'].hide_render = True
    S['cable'].scale = (1, 1, 0.01)
    S['cable'].location = (0, -1.5, -0.5)
    for kk in ('ring', 'fin', 'stick'):
        S[kk].location, S[kk].rotation_euler = (0, 0, -30), (0, 0, 0)
    S['moon'].hide_render = False
    S['sun'].location = (0, 480, -100)
    S['band'].location = (0, 520, -200)
    S['moonl'].data.energy = 60000
    S['sunl'].data.energy = 0
    S['thing'].location, S['thing'].rotation_euler = (0, 0, -40), (0, 0, 0)
    S['hinge'].rotation_euler = (0, 0, 0)
    for l in S['lamps']:
        l.data.energy = 170
    S['hfill'].data.energy = 300
    S['pick'].location = FAR
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
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
    r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.14).get(e, 0.0) + tip * 0.35, 0.07, 0)
    r['hat'].location.z = 0.27 + (0.11 if e == 'shocked' else 0.0) + tip * 0.1
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e in ('shocked', 'laugh') else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for who in ('james', 'crew', 'swimmer'):
        e = S['face'][who]
        kk = dict(scared=1.3, shock=1.8, calm=1.0, sad=0.6, happy=0.85, closed=0.1, tired=0.5).get(e, 1.0)
        for ey in S[who].extra['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], 0.075 * kk)
        S[who].extra['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
        S[who].extra['jaw'].location.z = -0.13 - (0.05 if e == 'shock' else 0.0)
    if S['chew']:
        S['james'].extra['jaw'].location.z = -0.13 - 0.04 * (0.5 + 0.5 * math.sin(t * 16))


# ---------------------------------------------------------------- the Gulf
def swell(x, y, t, rough=1.0):
    return rough * (0.5 * math.sin(x * 0.13 + t * 1.3) + 0.36 * math.sin(y * 0.19 + t * 1.7 + x * 0.05) + 0.17 * math.sin((x - y) * 0.4 + t * 2.6))


def gulf(S, t, mode='night', rough=1.0):
    """Shows the open water. mode: night | dawn | dusk | sunset | dark (last light)."""
    A = show(S, 'gulf')
    xy = S['xy']
    z = rough * (0.5 * np.sin(xy[:, 0] * 0.13 + t * 1.3) + 0.36 * np.sin(xy[:, 1] * 0.19 + t * 1.7 + xy[:, 0] * 0.05)
                 + 0.17 * np.sin((xy[:, 0] - xy[:, 1]) * 0.4 + t * 2.6))
    S['sea'].data.vertices.foreach_set('co', np.column_stack([xy, z]).ravel())
    S['sea'].data.update()
    if mode == 'night':
        sky(S, '071226', 1.0)
    elif mode == 'dawn':
        sky(S, '5E7088', 1.0)
        S['moon'].hide_render = True
        S['moonl'].data.energy = 160000
    else:
        S['moon'].hide_render = True
        S['sun'].location = (0, 480, 14 if mode != 'dark' else -8)
        S['band'].location = (0, 520, 10)
        sky(S, dict(dusk='3A2A5E', sunset='5A2E4E', dark='1A1838')[mode], 1.0)
        S['sunl'].data.energy = dict(dusk=260000, sunset=300000, dark=90000)[mode]
        S['moonl'].data.energy = 20000
    return A


def afloat(S, who, A, x, y, t, yaw, pose, sink=1.75, rough=1.0, face=None):
    """Chest-deep in the swell. Returns the water height there."""
    h = swell(x, y, t, rough)
    S[who].place(A(x, y, h - sink + 0.05 * math.sin(t * 2.3)), yaw, 0.05 * math.sin(t * 1.3), 0.06 * math.sin(t * 1.7))
    S[who].apply(pose)
    if face:
        S['face'][who] = face
    return h


def tread(t, head=(0.0, 0.0), amp=1.0):
    s = math.sin(t * 5.0)
    return P('stand', aL=(0.35 + 0.25 * s * amp, 1.15 + 0.2 * s * amp, 0.5), aR=(0.35 - 0.25 * s * amp, 1.15 - 0.2 * s * amp, 0.5), head=head)


def rook_float(S, A, x, y, t, yaw, pose, expr, rough=1.0):
    """Rook rides the swell in a life ring he brought along."""
    h = swell(x, y, t, rough)
    S['ring'].location = (x, y, h + 0.12)
    S['ring'].rotation_euler = (0.07 * math.sin(t * 1.7), 0.06 * math.sin(t * 1.4), yaw)
    S['rook'].place(A(x, y, h - 1.3), yaw, 0.07 * math.sin(t * 1.7), 0.06 * math.sin(t * 1.4))
    S['rook'].apply(pose)
    S['face']['rook'] = expr
    return h


RING_ARMS = dict(aL=(0.25, 0.95, 0.5), aR=(0.25, 0.95, 0.5))


def spray(S, org, k, n=14, r=1.6, seed=0, size=1.4, start=0, up=1.0):
    for i in range(n):
        b = S['spray'][start + i]
        a, e = i * 2.4 + seed, ((i * 0.61) % 1) * 1.2 + 0.2
        d = r * (0.35 + 0.65 * ((i * 0.37) % 1)) * (1 - (1 - k) ** 2)
        b.location = (org[0] + math.cos(a) * math.cos(e) * d, org[1] + math.sin(a) * math.cos(e) * d * 0.6, org[2] + math.sin(e) * d * up - 1.8 * k * k * up)
        s = size * (0.6 + ((i * 0.73) % 1)) * (1 - 0.7 * k)
        b.scale = (s, s, s)


def rise(S, org, t, n=12, spread=0.5, height=3.0, speed=1.4, seed=0, size=1.0, start=0):
    for i in range(n):
        b = S['spray'][start + i]
        u = (t * speed / height + (i * 0.618 + seed * 0.37) % 1) % 1
        a = i * 2.4 + seed
        rr = spread * (0.3 + 0.7 * ((i * 0.37) % 1)) * (0.4 + u)
        b.location = (org[0] + math.cos(a) * rr, org[1] + math.sin(a) * rr * 0.6, org[2] + u * height)
        s = size * (0.5 + ((i * 0.73) % 1)) * (0.6 + 0.6 * u)
        b.scale = (s, s, s)


def helo_at(S, loc, yaw, t, spot=0, cone=False, cable=0.0):
    S['helo'].location = (loc[0] + 0.15 * math.sin(t * 2.1), loc[1] + 0.12 * math.sin(t * 1.7), loc[2] + 0.12 * math.sin(t * 2.6))
    S['helo'].rotation_euler = (0.05 * math.sin(t * 1.9), 0.06 + 0.03 * math.sin(t * 1.5), yaw)
    S['rotor'].rotation_euler = (0, 0, t * 23.0)
    S['trotor'].rotation_euler = (0, t * 31.0, 0)
    S['hspot'].data.energy = spot
    S['hcone'].hide_render = not cone
    if cable > 0:
        L = cable / 2.0                       # the helicopter is drawn at scale 2
        S['cable'].scale = (1, 1, L)
        S['cable'].location = (0, -1.5, -0.5 - L / 2)


# ---------------------------------------------------------------- shots: hook
def wake_eyes(S, k, t, lt):
    A = gulf(S, t, 'night', 0.7)
    h = afloat(S, 'james', A, 0, 0, t, 0.12, tread(t, (-0.12 + 0.3 * ease((lt - 0.35) / 0.2), 0.0), 0.3 + 0.7 * ease((lt - 0.4) / 0.3)), rough=0.7)
    S['face']['james'] = 'closed' if lt < 0.4 else 'shock'
    if lt > 0.4:
        spray(S, A(0, -0.3, h + 0.2), min(1, (lt - 0.4) / 0.6), 12, 1.3, size=0.9)
    key(S, 'kc', A(-2.5, -4.5, h + 2.6), A(0, 0, h + 0.7), 700)
    key(S, 'kw', A(3, -2, h + 1.2), A(0, 0, h + 0.7), 120)
    cam(S, A(lerp(0.5, 0.25, k), lerp(-3.3, -2.5, k), h + 0.95), A(0, 0, h + 0.62), 58, 0.05 * math.sin(t * 1.3))


def wake_wide(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    h = afloat(S, 'james', A, 0, 0, t, 0.1, tread(t, (-0.1, 0.5 * math.sin(t * 2.2))), rough=0.9, face='shock')
    key(S, 'kc', A(-5, -9, 9), A(0, 0, 0.5), 5000)
    e = ease(k)
    cam(S, A(lerp(1.5, 5.5, e), lerp(-6, -21, e), lerp(2.2, 11, e)), A(0, lerp(0, 3, e), 0.5), lerp(40, 30, e))


def no_ship(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    a = lerp(-1.1, 1.0, k)
    h = afloat(S, 'james', A, 0, 0, t, a * 0.8, tread(t, (-0.05, 0.6 * math.sin(lt * 5.0))), rough=0.9, face='scared')
    key(S, 'kc', A(math.sin(a) * 5 - 2, -math.cos(a) * 5, 4), A(0, 0, 0.6), 1500)
    key(S, 'kw', A(math.sin(a) * 4 + 2.5, -math.cos(a) * 4, 1.4), A(0, 0, 0.6), 200)
    cam(S, A(math.sin(a) * 7.5, -math.cos(a) * 7.5, 1.5), A(0, 0, 1.0), 26, 0.03 * math.sin(t * 1.2))


def top_down(S, k, t, lt):
    A = gulf(S, t, 'night', 0.8)
    h = afloat(S, 'james', A, 0, 0, t, 0.0, tread(t, (-0.75, 0.0)), rough=0.8, face='scared')
    key(S, 'kc', A(-3, -2, 9), A(0, 0, 0.5), 3800)
    key(S, 'kw', A(2, -3, 5), A(0, 0, 0.5), 500)
    cam(S, A(0.3, -2.6, lerp(15, 8.5, ease(k))), A(0, 0.5, 0.4), 34, lerp(-0.25, 0.1, k))


# ---------------------------------------------------------------- shots: Rook takes the case
def rook_pier(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, '060A18')
    S['rook'].place(A(0, 0, 0), -0.32)
    S['rook'].apply(P('cross', head=(0.05, 0.25 - 0.24 * math.sin(t * 4.2) * max(0, 1 - lt / 1.0))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-2.4, -1.7, k), lerp(-6.8, -5.4, k), 2.2), A(-0.05, 0, 1.9), 40)


def rook_go(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, '060A18')
    e = ease((lt - 0.35) / 1.0)
    x, y = lerp(-0.2, -3.5, e), lerp(0.2, 1.3, e)
    S['rook'].place(A(x, y, 0), math.atan2(-3.3, -1.1))
    pop = math.sin(PI * ease(lt / 0.4)) if lt < 0.4 else 0
    S['rook'].apply(blend(walk(t, 1.9) if lt > 0.35 else P('stand'), P('stand', aL=(0.5, 0.5, 2.3, 0.4), aR=(0.5, 0.5, 2.3, 0.4), head=(0.1, 0)), pop))
    S['face']['rook'] = 'smirk'
    cam(S, A(lerp(1.9, 0.9, k), -6.8, 2.1), A(lerp(-0.8, -3.2, k), 1.4, 2.0), 36)


# ---------------------------------------------------------------- shots: the party
def ship_sail(S, k, t, lt):
    A = gulf(S, t, 'dusk', 0.6)
    S['liner'].location = (lerp(-9, 2, k), 28, 0.3 + 0.2 * math.sin(t * 0.9))
    S['liner'].rotation_euler = (0.012 * math.sin(t * 1.1), 0, 0.42)
    cam(S, A(lerp(44, 40, k), lerp(-30, -26, k), lerp(3.0, 4.2, k)), A(-3, 28, 7.5), 24, 0.02 * math.sin(t * 0.8))


def rook_rail(S, k, t, lt):
    A = show(S, 'deck')
    sky(S, '3A2A5E', 1.2)
    S['rook'].place(A(0.2, 3.6, 0), 0.25)
    j = ease((lt - 0.25) / 0.35)
    S['rook'].apply(blend(P('stand', aL=(0.3, 0.3, 0.9), head=(0.0, -0.3)), P('stand', aR=(2.3, 0.9, 1.7, -0.6), aL=(0.3, 0.3, 0.9), head=(0.04, 0.2)), j))
    S['face']['rook'] = 'smirk'
    for i, b in enumerate(S['bulbs']):
        s = 1.0 + 0.5 * math.sin(t * 6 + i * 1.3)
        b.scale = (s, s, s)
    key(S, 'kw', A(-3, -2, 3), A(0.2, 3.6, 2.3), 700)
    cam(S, A(lerp(-1.4, -0.8, k), lerp(-3.6, -2.6, k), 2.0), A(0.15, 3.6, 2.05), 38)


def stage(S, t):
    A = show(S, 'lounge')
    sky(S, '08040F')
    for i, (l, aim) in enumerate(S['spots']):
        aim.location = ((i - 1) * 0.9 + 1.4 * math.sin(t * 2.6 + i * 2.1), 2.6 + 0.6 * math.cos(t * 2.1 + i), 1.8)
        l.data.energy = 5200 + 2600 * math.sin(t * 7 + i * 2)
    for i, c in enumerate(S['crowd']):
        c.location.z = 0.14 * abs(math.sin(t * 5.2 + i * 0.9))
        c.rotation_euler = (0, 0.06 * math.sin(t * 5.2 + i), 0)
    return A


def riff(t, lt):
    """Air guitar: left hand on an invisible neck, right arm windmilling."""
    w = t * 9.0
    return P('stand', aL=(1.0, 0.75, 0.5, 0.3), aR=(0.9 + 1.1 * math.sin(w), 0.25, 1.1 + 0.5 * math.cos(w), 0.9),
             lL=(0.35, 0.25), lR=(-0.3, 0.1), head=(-0.25 + 0.2 * math.sin(t * 9), 0.2 * math.sin(t * 4.5)), lean=-0.18 + 0.08 * math.sin(t * 9))


def lounge_wide(S, k, t, lt):
    A = stage(S, t)
    S['james'].place(A(0.3 * math.sin(t * 2), 2.4, 0.6 + 0.12 * abs(math.sin(t * 4.5))), 0.15 * math.sin(t * 2.2))
    S['james'].apply(riff(t, lt))
    S['face']['james'] = 'happy'
    S['rook'].place(A(1.75, -9.2, 0), -0.6)
    S['rook'].apply(P('cross', head=(0.06, 0.6 - 0.55 * ease((lt - 0.5) / 0.3))))
    S['face']['rook'] = 'deadpan'
    key(S, 'kw', A(3.5, -13, 3.4), A(1.75, -9.2, 2.3), 420)
    cam(S, A(lerp(0.9, 0.7, k), lerp(-14.6, -13.4, k), 2.7), A(0.75, 0, 2.55), 30)


def guitar_cu(S, k, t, lt):
    A = stage(S, t)
    S['james'].place(A(0, 2.2, 0.6), 0.3 + 0.12 * math.sin(t * 2.2))
    S['james'].apply(riff(t, lt))
    S['face']['james'] = 'shock' if int(t * 3) % 2 else 'happy'
    key(S, 'kw', A(-3, -3.5, 2.2), A(0, 2.2, 2.6), 380)
    cam(S, A(lerp(-1.6, -1.1, k), lerp(-2.6, -2.0, k), 1.5), A(0.1, 2.2, 2.75), 34, 0.08)


def rook_clap(S, k, t, lt):
    A = stage(S, t)
    S['rook'].place(A(1.75, -9.2, 0), 0.2)
    c = 0.5 + 0.5 * math.sin(t * 5.5)
    S['rook'].apply(P('stand', aL=(0.95, -0.12 - 0.22 * c, 1.35, 0.8), aR=(0.95, -0.12 - 0.22 * c, 1.35, 0.8), head=(0.08, -0.2)))
    S['face']['rook'] = 'deadpan' if lt < 0.6 else 'smirk'
    key(S, 'kw', A(3.6, -13.5, 3.4), A(1.75, -9.2, 2.3), 520)
    key(S, 'kc', A(-1.5, -12.5, 2.0), A(1.75, -9.2, 2.3), 160)
    cam(S, A(lerp(2.8, 2.5, k), lerp(-13.8, -13.1, k), 2.35), A(1.7, -9.2, 2.3), 50)


def winner(S, k, t, lt):
    A = stage(S, t)
    hop = abs(math.sin(lt * 6.5)) * 0.5
    S['james'].place(A(0, 2.0, 0.6 + hop), 0.1)
    S['james'].apply(P('up', aL=(2.7, -0.5, 0.25), aR=(2.7, -0.5, 0.25), lL=(0.2 * hop, 0.5 * hop), lR=(0.2 * hop, 0.5 * hop), head=(-0.2, 0)))
    S['face']['james'] = 'happy'
    for i, c in enumerate(S['conf']):
        u = (lt * 0.55 + i * 0.137) % 1
        c.location = A(-3.2 + (i * 0.618 % 1) * 6.4 + 0.3 * math.sin(t * 3 + i), 1.4 + (i * 0.37 % 1) * 3.0, 6.6 - u * 5.6)
        c.rotation_euler = (t * 5 + i, t * 3.1 + i * 2, i)
        c.scale = (0.6, 0.6, 0.6)
    key(S, 'kw', A(2.5, -2.4, 2.0), A(0, 2, 2.8), 300)
    cam(S, A(lerp(1.2, 0.8, k), lerp(-2.6, -2.1, k), 1.2), A(0, 2.0, 2.9), 28, -0.05)


# ---------------------------------------------------------------- shots: gone
def hall_walk(S, k, t, lt):
    A = show(S, 'hall')
    sky(S, '020203')
    y = lerp(-1.5, 3.2, k)
    S['james'].place(A(0.25 * math.sin(t * 2.4), y, 0), PI + 0.1 * math.sin(t * 2.4), 0, 0.07 * math.sin(t * 2.4))
    S['james'].apply(walk(t, 1.5))
    cam(S, A(0.9, y - lerp(6.2, 5.4, k), 2.0), A(0, y + 3, 1.9), 30, 0.035 * math.sin(t * 1.6))


def rook_peek(S, k, t, lt):
    A = show(S, 'hall')
    sky(S, '020203')
    e = ease(lt / 0.3)
    S['rook'].place(A(lerp(-2.4, -1.05, e), 0.4, 0), 0.3, 0, lerp(0.0, -0.2, e))
    tap = 0.5 + 0.5 * math.sin(t * 9)
    S['rook'].apply(P('stand', aR=(1.25, 0.1, 2.25 + 0.12 * tap, 0.75), head=(0.02, 0.7 - 0.75 * ease((lt - 0.6) / 0.3))))
    S['face']['rook'] = 'calm'
    S['james'].place(A(0.1, lerp(12, 16.5, k), 0), PI)
    S['james'].apply(walk(t, 1.5))
    key(S, 'kw', A(1.6, -3.4, 2.6), A(-1.2, 0.4, 2.3), 320)
    cam(S, A(lerp(0.9, 0.6, k), lerp(-4.2, -3.6, k), 2.35), A(-0.75, 0.6, 2.3), 40)


def door_swing(S, k, t, lt):
    A = show(S, 'hall')
    sky(S, '020203')
    S['hinge'].rotation_euler = (0, 0, -0.95 * math.exp(-lt * 1.3) * math.cos(lt * 6.5))
    fl = 1.0 if int(t * 11) % 4 else 0.25
    for l in S['lamps']:
        l.data.energy = 170 * fl
    S['hfill'].data.energy = 0
    key(S, 'kw', A(1.2, lerp(9, 12, k), 2.6), A(0, 21, 1.6), 700 * fl)
    cam(S, A(0.35, lerp(11.0, 15.5, ease(k)), 1.9), A(0, 22, 1.85), 34, 0.04)


# ---------------------------------------------------------------- shots: the water
def ship_leaves(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    S['liner'].location = (5.5, lerp(34, 62, k), 0.2)
    S['liner'].rotation_euler = (0, 0, PI / 2)
    S['liner'].scale = (1.5, 1.5, 1.5)
    h = afloat(S, 'james', A, 1.7, 1.8, t, PI - 0.2, tread(t, (-0.1, 0.0)), rough=0.9, face='scared')
    rook_float(S, A, -0.9, 0.9, t, PI + 0.5, P('stand', head=(-0.08, -0.7 + 0.5 * math.sin(lt * 2.0)), **RING_ARMS), 'sad', 0.9)
    key(S, 'kc', A(-4, -6, 5), A(0, 0, 0.8), 1500)
    key(S, 'kw', A(4, -5, 2.5), A(0, 0, 0.8), 380)
    cam(S, A(lerp(-0.4, -0.1, k), lerp(-6.4, -5.6, k), 1.9), A(1.4, 14, lerp(3.2, 4.0, k)), 30)


def tread_cu(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    h = afloat(S, 'james', A, 0, 0, t, -0.1, tread(t, (-0.1, 0.45 * math.sin(lt * 3.2))), rough=0.9, face='scared')
    key(S, 'kc', A(-3, -4.5, 3.2), A(0, 0, h + 0.6), 900)
    key(S, 'kw', A(3, -3, 1.2), A(0, 0, h + 0.6), 130)
    cam(S, A(lerp(1.3, 0.8, k), lerp(-4.9, -4.0, k), h + 1.5), A(0, 0, h + 0.55), 44, 0.03 * math.sin(t * 1.5))


def rook_ring(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    h = rook_float(S, A, 0, 0, t, -0.25, P('stand', head=(0.2 * ease((lt - 0.5) / 0.4), 0.35), **RING_ARMS), 'sad', 0.9)
    afloat(S, 'james', A, 4.0, 6.5, t, -0.4, tread(t, (-0.1, 0.0)), rough=0.9, face='tired')
    key(S, 'kc', A(-3.5, -5, 4.2), A(0, 0, h + 1.2), 1300)
    key(S, 'kw', A(3.5, -3.5, 1.6), A(0, 0, h + 1.2), 300)
    cam(S, A(lerp(-1.1, -0.7, k), lerp(-5.6, -4.8, k), h + 1.9), A(0.35, 0, h + 1.15), 40)


# ---------------------------------------------------------------- shots: the fin
def fin_circle(S, k, t, lt):
    A = gulf(S, t, 'dawn', 0.8)
    h = afloat(S, 'james', A, 0.6, 1.0, t, 0.5, tread(t, (0.0, 0.7), 1.3), rough=0.8, face='shock')
    a = lerp(-0.25, 1.25, k)
    fx, fy = 0.6 + math.cos(a) * lerp(8, 2.6, k), 1.0 + math.sin(a) * lerp(8, 2.6, k)
    S['fin'].location = (fx, fy, swell(fx, fy, t, 0.8) - 0.15)
    S['fin'].rotation_euler = (0.08 * math.sin(t * 3), 0, a + PI / 2 + 0.3)
    S['fin'].scale = (1.5, 1.5, 1.5)
    rook_float(S, A, -1.9, -3.2, t, -0.55, P('up', aL=(2.5, -0.6, 0.5), aR=(2.5, -0.6, 0.5), head=(-0.05, 0.75 - 0.7 * ease((lt - 0.9) / 0.3))), 'shocked', 0.8)
    key(S, 'kw', A(-4, -8, 3), A(-1, -1, 1), 1400)
    cam(S, A(lerp(-2.6, -2.2, k), lerp(-9.2, -8.4, k), 2.7), A(0.2, 0, 1.0), 32)


def under_bump(S, k, t, lt):
    A = show(S, 'under')
    sky(S, '2A7482', 1.0)
    kick = math.sin(t * 9)
    hit = 1 - min(1.0, abs(k - 0.5) / 0.12)
    S['james'].place(A(0.25 * max(0, hit), 0, 4.2), 0.3, 0, 0.12 * max(0, hit))
    S['james'].apply(P('stand', lL=(0.5 * kick, 0.5 + 0.3 * kick), lR=(-0.5 * kick, 0.5 - 0.3 * kick), aL=(0.4, 1.2, 0.4), aR=(0.4, 1.2, 0.4)))
    x = lerp(-9.5, 0.2, ease(k / 0.5)) if k < 0.5 else lerp(0.2, 4.5, ease((k - 0.5) / 0.5))
    y = 0.9 if k < 0.5 else lerp(0.9, 9.0, ease((k - 0.5) / 0.5))
    S['thing'].location = (x - 2.6, y, 4.0 + 0.15 * math.sin(t * 2))
    S['thing'].rotation_euler = (0.1 * math.sin(t * 4), 0, 0.0 if k < 0.5 else lerp(0, 1.1, (k - 0.5) * 2))
    S['ttail'].rotation_euler = (0, 0, 0.5 * math.sin(t * 8))
    rise(S, A(0, 0, 3.4), t, 12, 0.7, 2.6, 2.2, size=0.9)
    if hit > 0:
        spray(S, A(0.2, 0.4, 4.4), 1 - hit * 0.6, 10, 1.2, size=0.8, start=14)
    cam(S, A(lerp(-1.5, -0.8, k), lerp(-8.5, -7.5, k), 2.3), A(-0.4, 0.4, 4.3), 30, 0.05 * math.sin(t * 2))


def stick_chew(S, k, t, lt):
    A = gulf(S, t, 'dawn', 0.6)
    h = afloat(S, 'james', A, 0, 0, t, 0.2, P('stand', aR=(1.15, 0.05, 2.3, 0.55), aL=(0.35, 1.15, 0.5), head=(0.05, 0.1)), rough=0.6, face='tired')
    S['chew'] = 1.0
    r = S['james'].root
    S['stick'].location = (0.16, -0.36 + 0.02 * math.sin(t * 16), r.location.z - ORG['gulf'][2] + 2.26)
    S['stick'].rotation_euler = (0, 0.15, 0.2 + 0.25)
    S['stick'].scale = (0.8, 0.8, 0.8)
    key(S, 'kw', A(-2.5, -4, 2.4), A(0, 0, h + 0.6), 700)
    cam(S, A(lerp(0.9, 0.55, k), lerp(-3.6, -2.9, k), h + 1.05), A(0.08, 0, h + 0.58), 52)


def rook_wince(S, k, t, lt):
    A = gulf(S, t, 'dawn', 0.7)
    j = ease(lt / 0.4)
    h = rook_float(S, A, 0, 0, t, 0.35, blend(P('stand', **RING_ARMS), P('stand', aL=(0.25, 0.95, 0.5), aR=(1.3, 0.15, 2.3, 0.7), head=(0.12, -0.5)), j), 'sad', 0.7)
    key(S, 'kw', A(3, -5, 3.4), A(0, 0, h + 1.3), 1100)
    cam(S, A(lerp(1.7, 1.3, k), lerp(-4.6, -4.0, k), h + 2.2), A(-0.1, 0, h + 1.4), 46)


# ---------------------------------------------------------------- shots: lights
def lights_far(S, k, t, lt):
    A = gulf(S, t, 'sunset', 0.7)
    S['carrier'].location = (lerp(-9, -3, k), 95, 0)
    S['carrier'].scale = (0.5, 0.5, 0.5)
    h = afloat(S, 'james', A, 0.3, 0, t, PI + 0.15, tread(t, (-0.08, 0.0)), sink=1.6, rough=0.7)
    key(S, 'kc', A(3, -6, 3.5), A(0.3, 0, h + 0.8), 1500)
    cam(S, A(lerp(0.9, 0.6, k), lerp(-5.2, -4.2, k), h + 1.5), A(-0.2, 30, lerp(4.4, 5.0, k)), 40)


def swim_for(S, k, t, lt):
    A = gulf(S, t, 'sunset', 0.6)
    y = lerp(-2.0, 2.6, k)
    h = swell(0, y, t, 0.6)
    w = t * 7.5
    S['james'].place(A(0, y, h - 0.3), PI, 1.36, 0.3 * math.sin(w))
    S['james'].apply(P('swim', aL=(1.6 + 1.5 * math.sin(w), 0.25, 0.5), aR=(1.6 - 1.5 * math.sin(w), 0.25, 0.5),
                       lL=(0.35 * math.sin(w * 2), 0.25), lR=(-0.35 * math.sin(w * 2), 0.25), head=(-0.75, 0.5 * math.sin(w))))
    S['face']['james'] = 'scared'
    spray(S, A(0, y + 0.2, h + 0.1), (lt * 2.2) % 1, 12, 1.3, seed=int(lt * 2.2), size=1.3)
    spray(S, A(0, y + 3.2, h + 0.1), (lt * 2.2 + 0.5) % 1, 10, 0.9, seed=3, size=1.1, start=14)
    key(S, 'kw', A(5, y - 2, 3.5), A(0, y + 2, 0.3), 2600)
    key(S, 'kc', A(4, y + 6, 2), A(0, y + 2, 0.3), 900)
    cam(S, A(4.4, y + 0.6, 1.3), A(0, y + 2.1, 0.45), 32, 0.04 * math.sin(t * 1.7))


def socks_wave(S, k, t, lt):
    A = gulf(S, t, 'dark', 0.8)
    wv = math.sin(t * 9)
    h = afloat(S, 'james', A, 0, 0, t, 0.15, P('stand', aR=(2.75, 0.35 + 0.4 * wv, 0.25 + 0.15 * wv), aL=(0.35, 1.2, 0.5), head=(-0.3, 0.1)),
               sink=1.55, rough=0.8, face='shock')
    for o in S['socks']:
        o.hide_render = False
    key(S, 'kw', A(-3, -5, 2.6), A(0, 0, h + 1.6), 900)
    key(S, 'kc', A(3, -3.5, 1.0), A(0, 0, h + 1.6), 250)
    cam(S, A(lerp(1.1, 0.7, k), lerp(-5.8, -5.0, k), h + 0.9), A(0.25, 0, h + 1.75), 38, -0.04)


def rook_socks(S, k, t, lt):
    A = gulf(S, t, 'dark', 0.8)
    up = ease(lt / 0.3) - ease((lt - 0.9) / 0.3)
    h = rook_float(S, A, 0, 0, t, -0.2, blend(P('stand', **RING_ARMS), P('shrug', head=(-0.02, 0.25 * math.sin(t * 5))), up), 'deadpan', 0.8)
    key(S, 'kw', A(-3.2, -5, 3.2), A(0, 0, h + 1.3), 1000)
    key(S, 'kc', A(3.4, -3, 1.5), A(0, 0, h + 1.3), 260)
    cam(S, A(lerp(-0.6, -0.3, k), lerp(-5.4, -4.7, k), h + 1.8), A(0, 0, h + 1.3), 42)


def carrier_big(S, k, t, lt):
    A = gulf(S, t, 'dark', 0.8)
    S['carrier'].location = (lerp(30, 54, k), 30, 0.2)
    S['carrier'].scale = (1.6, 1.6, 1.6)
    h = afloat(S, 'james', A, 2.8, 6.0, t, PI - 0.3, P('stand', aR=(2.8, 0.35 + 0.4 * math.sin(t * 9), 0.3), aL=(0.35, 1.2, 0.5), head=(-0.4, 0)),
               sink=1.55, rough=0.8)
    for o in S['socks']:
        o.hide_render = False
    rook_float(S, A, -2.0, -2.6, t, -0.5, P('stand', head=(-0.1, 0.75 - 0.7 * ease((lt - 0.8) / 0.4)), **RING_ARMS), 'deadpan', 0.8)
    key(S, 'kw', A(-5, -9, 3), A(-2, -2.6, 1.4), 1500)
    key(S, 'kc', A(6, 0, 5), A(2.8, 6.0, 1.0), 1800)
    cam(S, A(lerp(-0.4, -0.7, k), lerp(-9.0, -8.4, k), 1.6), A(1.6, 16, lerp(5.0, 6.0, k)), 22, 0.03 * math.sin(t))


# ---------------------------------------------------------------- shots: rescue
def bridge_spot(S, k, t, lt):
    A = show(S, 'wing')
    sky(S, '0A1430')
    j = ease((lt - 0.15) / 0.25)
    S['crew'].place(A(-0.4, -1.5, 0), 0.5, 0, 0)
    S['crew'].apply(blend(P('stand', aL=(1.2, 0.3, 2.0, 0.6), aR=(1.2, 0.3, 2.0, 0.6), head=(0.12, 0.2)),
                          P('point', aR=(1.25, 0.25, 0.1), aL=(1.2, 0.3, 2.0, 0.6), head=(0.2, 0.0), lean=0.14), j))
    S['face']['crew'] = 'shock'
    S['wlamp'].rotation_euler = (0, 0, 0.5 * math.sin(t * 2.5) - 0.3)
    cam(S, A(lerp(1.2, 0.8, k), lerp(-6.6, -5.6, k), 1.7), A(-0.2, -1.2, 2.25), 36, 0.04)


def heli_in(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    e = ease(k)
    helo_at(S, (lerp(-30, -3.5, e), lerp(60, 8, e), lerp(22, 10.5, e)), -0.9 + 0.5 * e, t, spot=250000, cone=True)
    S['haim'].location = (3.5 + 2.5 * math.sin(t * 2.2), 1.5 * math.cos(t * 1.8), -20)
    h = afloat(S, 'james', A, 1.5, 1.0, t, PI + 0.5, P('up', aL=(2.7, -0.4 + 0.3 * math.sin(t * 8), 0.2), aR=(2.7, -0.4 - 0.3 * math.sin(t * 8), 0.2), head=(-0.45, 0)),
               sink=1.6, rough=0.9)
    key(S, 'kc', A(4, -6, 4), A(1.5, 1, 1), 1600)
    cam(S, A(lerp(4.6, 4.0, k), lerp(-9.5, -8.6, k), 1.3), A(-0.5, 5, lerp(5.2, 6.4, k)), 26, -0.04)


def swimmer_down(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    helo_at(S, (-1.0, 3.0, 12.5), 0.35, t, spot=200000, cone=False, cable=lerp(3.5, 8.6, ease(k)) + 0.9)
    hz = S['helo'].location.z
    cz = hz - 1.0 - lerp(3.5, 8.6, ease(k)) - 0.9 + 0.7
    hx, hy = S['helo'].location.x, S['helo'].location.y
    cx, cy = hx + 3.0 * math.sin(0.35), hy - 3.0 * math.cos(0.35)
    S['swimmer'].place(A(cx, cy, cz - 2.9), 0.3 + 0.25 * math.sin(t * 1.4), 0, 0.08 * math.sin(t * 2))
    S['swimmer'].apply(P('reach', aR=(2.95, 0.05, 0.1), aL=(0.9, 0.3, 0.9), lL=(0.2, 0.5), lR=(-0.1, 0.25), head=(0.35, 0.0)))
    h = afloat(S, 'james', A, cx - 1.6, cy - 0.6, t, 1.2, P('reach', aR=(2.8, 0.2, 0.15), aL=(2.4, 0.4, 0.3), head=(-0.5, 0)), sink=1.6, rough=0.9, face='tired')
    spray(S, A(cx - 0.6, cy - 0.3, 0.3), (lt * 1.6) % 1, 16, 3.4, seed=2, size=1.1)
    key(S, 'kw', A(cx + 4, cy - 7, 4), A(cx, cy, 3), 2600)
    key(S, 'kc', A(cx - 5, cy - 5, 2), A(cx - 1, cy, 1.5), 900)
    cam(S, A(cx + lerp(4.8, 4.0, k), cy - lerp(10.5, 9.4, k), 2.4), A(cx - 0.4, cy, lerp(5.6, 4.4, k)), 30)


def rook_hat(S, k, t, lt):
    A = gulf(S, t, 'night', 1.0)
    j = 0.03 * math.sin(t * 40)
    h = rook_float(S, A, j, 0, t, 0.15, P('up', aL=(2.6, -0.55, 0.3), aR=(2.6, -0.55, 0.3), head=(-0.3, 0.1)), 'shocked', 1.0)
    spray(S, A(0, -0.4, h + 0.3), (lt * 1.4) % 1, 16, 2.6, seed=5, size=1.0)
    key(S, 'kw', A(-1.5, -4, 6), A(0, 0, h + 1.5), 2600)
    key(S, 'kc', A(3.5, -4, 1.5), A(0, 0, h + 1.5), 500)
    cam(S, A(lerp(0.9, 0.6, k), lerp(-6.0, -5.3, k), h + 1.2), A(0, 0, h + 1.95), 38, 0.05 * math.sin(t * 9))


def hoist_up(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    L = lerp(8.2, 3.2, ease(k))
    helo_at(S, (0.5, 5.0, 12.5), 0.35, t, spot=0, cone=False, cable=L)
    hx, hy, hz = S['helo'].location
    cx, cy = hx + 3.0 * math.sin(0.35), hy - 3.0 * math.cos(0.35)
    z = hz - 1.0 - L - 2.9
    sw = 0.12 * math.sin(t * 1.6)
    S['swimmer'].place(A(cx + 0.35, cy, z), 0.9 + sw, 0, 0.05)
    S['swimmer'].apply(P('reach', aR=(2.95, 0.05, 0.1), aL=(1.1, -0.3, 1.2), lL=(0.15, 0.3), lR=(-0.1, 0.2), head=(0.3, -0.4)))
    S['james'].place(A(cx - 0.45, cy - 0.1, z - 0.15), -0.7 + sw, 0, -0.05)
    S['james'].apply(P('stand', aL=(1.3, -0.2, 1.2), aR=(1.3, -0.2, 1.2), lL=(0.25, 0.4), lR=(0.1, 0.3), head=(0.2, 0.3)))
    S['face']['james'] = 'tired'
    rook_float(S, A, -1.6, -2.4, t, PI - 0.55, P('reach', aR=(2.7, 0.25, 0.1), aL=(0.25, 0.95, 0.5), head=(-0.5, -0.2)), 'warm', 0.9)
    key(S, 'kw', A(cx + 3, cy - 7, z + 1), A(cx, cy, z + 2), 2600)
    key(S, 'kc', A(-5, -8, 3), A(-1.6, -2.4, 1.5), 1600)
    cam(S, A(lerp(-3.4, -3.0, k), lerp(-9.6, -9.0, k), 1.6), A(0.4, 1.0, lerp(4.6, 6.2, k)), 26)


# ---------------------------------------------------------------- shots: case closed
def rook_dawn(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, 'C8785A', 0.7)
    S['rook'].place(A(1.2, 0.4, 0), 0.55)
    tip = math.sin(PI * ease((lt - 0.2) / 0.9)) if lt > 0.2 else 0
    S['rook'].apply(blend(P('stand', head=(0, -0.25)), P('hat', head=(0.2, -0.25)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    key(S, 'kw', A(7, -8, 6), A(1.2, 0.4, 2), 2200)
    cam(S, A(lerp(4.6, 3.9, k), lerp(-6.0, -5.2, k), 1.5), A(0.6, 0.6, 2.1), 34)


def signoff(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, 'B86E58', 0.6)
    S['rook'].place(A(0, 0, 0), -0.15)
    c = max(0.0, min(1.0, (lt - 0.2) / 0.9))
    S['rook'].apply(blend(P('stand', aR=(0.9, 0.25, 1.2), head=(0.05, 0)), P('stand', aR=(1.2, 0.2, 1.5), head=(-0.12, 0)), math.sin(c * PI)))
    S['face']['rook'] = 'smirk'
    S['pick'].location = A(0.75 + 0.2 * c, -0.75, 1.8 + 2.4 * math.sin(c * PI))
    S['pick'].rotation_euler = (t * 21, t * 8, 0)
    S['pick'].scale = (1.3, 1.3, 1.3)
    key(S, 'kw', A(-5, -7, 5), A(0, 0, 2), 1500)
    cam(S, A(lerp(-1.6, -1.2, k), lerp(-5.0, -4.1, k), 0.9), A(0, 0, 2.25), 36)


# ---------------------------------------------------------------- stills for the case board
def photo_liner(S, k, t, lt):
    A = gulf(S, 2.0, 'dusk', 0.5)
    S['liner'].location, S['liner'].rotation_euler = (0, 30, 0.3), (0, 0, 0.5)
    cam(S, A(40, -24, 6), A(4, 30, 6), 30)


def photo_james(S, k, t, lt):
    A = show(S, 'deck')
    sky(S, '6A4A7E', 1.4)
    S['james'].place(A(0, 2, 0), 0.25)
    S['james'].apply(P('stand', head=(0, 0.1)))
    S['face']['james'] = 'happy'
    key(S, 'kw', A(-2, -3, 3.5), A(0, 2, 2.4), 900)
    cam(S, A(1.6, -1.6, 2.5), A(0, 2, 2.3), 50)


SHOTS3D = {f.__name__: f for f in (
    wake_eyes, wake_wide, no_ship, top_down, rook_pier, rook_go, ship_sail, rook_rail, lounge_wide, guitar_cu, rook_clap, winner,
    hall_walk, rook_peek, door_swing, ship_leaves, tread_cu, rook_ring, fin_circle, under_bump, stick_chew, rook_wince, lights_far,
    swim_for, socks_wave, rook_socks, carrier_big, bridge_spot, heli_in, swimmer_down, rook_hat, hoist_up, rook_dawn, signoff)}
STILLS = dict(liner=photo_liner, james=photo_james)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it: the family boarding, the bar and the empty stool, the night swim, the jellyfish,
# the sunrise, the search of the ship, the turn, the Coast Guard search, the sling, the hospital and the rail.
ORG.update(bar=(1600, 0, 0), ops=(2000, 0, 0), ward=(2400, 0, 0))
SIS = dict(top='2E8A8A', pants='2A2742', hand='E0A882', boot='20242B')
GUARD = dict(top='F2EEE4', pants='1C2A4A', hand='B8805A', boot='15181F')
OFFICER = dict(top='27406A', pants='1C2A4A', hand='D8A07A', boot='15181F')
FAMC = ('E8B43A', '5EC8F0', 'F05A8C', '8ACB5A', 'E8701E', 'B48AE8', 'F2EEE4', '3DA0A0')


def lerp_col(a, b, k):
    k = max(0.0, min(1.0, k))
    return ''.join('%02X' % int(int(a[i:i + 2], 16) + (int(b[i:i + 2], 16) - int(a[i:i + 2], 16)) * k) for i in (0, 2, 4))


def set_bar(r):
    add('cube', '3A2418', (0, 0, -0.1), scale=(18, 14, 0.2), size=1, parent=r)
    for i in range(-8, 9):
        add('cube', '2A1810', (i * 1.05, 0, 0.005), scale=(0.05, 14, 0.02), size=1, parent=r)
    add('cube', '1E2A3E', (0, 4.6, 3), scale=(18, 0.3, 6.4), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '243248', (sx * 9, 0, 3), scale=(0.3, 14, 6.4), size=1, parent=r)
    add('cube', '5A3420', (0, 2.2, 0.8), scale=(11, 0.9, 1.6), size=1, parent=r)
    add('cube', 'C8A44A', (0, 2.2, 1.63), scale=(11.3, 1.2, 0.08), size=1, parent=r, rough=0.3)
    add('cube', 'FF7A1A', (0, 1.73, 0.35), scale=(11, 0.04, 0.1), size=1, parent=r, emit=5)
    for z in (2.6, 3.5, 4.4):
        add('cube', '6A4226', (0, 4.35, z), scale=(9.6, 0.4, 0.08), size=1, parent=r)
        for i in range(15):
            col = CONF[(i + int(z * 3)) % 5]
            add('cylinder', col, (-4.4 + i * 0.63, 4.3, z + 0.34), radius=0.1, depth=0.6, vertices=6, parent=r, emit=1.8, rough=0.3)
    add('cube', 'FFD27A', (0, 4.42, 3.5), scale=(9.8, 0.05, 2.9), size=1, parent=r, emit=0.5)
    for x in (-3.3, -0.9, 0.9, 3.3):
        add('cylinder', '9AA0B4', (x, 0.9, 0.5), radius=0.06, depth=1.0, vertices=6, parent=r)
        add('cylinder', '8A1E3A', (x, 0.9, 1.0), radius=0.36, depth=0.14, vertices=8, parent=r)
        add('cylinder', '9AA0B4', (x, 0.9, 0.03), radius=0.3, depth=0.06, vertices=8, parent=r)
    for x in (-4.5, 0, 4.5):
        add('cylinder', '20242B', (x, 1.6, 5.3), radius=0.03, depth=1.6, vertices=5, parent=r)
        add('cone', 'FFB060', (x, 1.6, 4.4), radius1=0.5, radius2=0.12, depth=0.45, vertices=8, parent=r, emit=3)
    # exit on the left wall, clock on the right
    add('cube', '0A0C10', (-8.82, 0.2, 1.5), scale=(0.06, 1.7, 3.0), size=1, parent=r)
    add('cube', '5EC8F0', (-8.8, 0.2, 3.3), scale=(0.06, 1.1, 0.36), size=1, parent=r, emit=5)
    add('cylinder', 'F4EEDF', (6.2, 4.4, 4.6), rot=(PI / 2, 0, 0), radius=0.62, depth=0.08, vertices=14, parent=r, emit=0.7)
    add('cube', '15181F', (6.2, 4.34, 4.84), scale=(0.07, 0.04, 0.5), size=1, parent=r)
    add('cube', '15181F', (6.08, 4.34, 4.78), rot=(0, 0.52, 0), scale=(0.07, 0.04, 0.4), size=1, parent=r)
    # a porthole row and two tables so the wide frame is full
    for x in (-7.2, 7.4):
        add('cylinder', '4A2A1C', (x, -1.6, 0.6), radius=0.08, depth=1.2, vertices=6, parent=r)
        add('cylinder', '6A4226', (x, -1.6, 1.22), radius=0.8, depth=0.08, vertices=10, parent=r)
        add('ico_sphere', 'FFD866', (x, -1.6, 1.42), radius=0.13, subdivisions=1, parent=r, emit=8)
    glass = empty((0, 0, -20), r)
    add('cylinder', 'BFEFFF', (0, 0, 0.18), radius=0.11, depth=0.36, vertices=8, parent=glass, rough=0.1, emit=0.3)
    add('cylinder', 'FF9A3A', (0, 0, 0.12), radius=0.09, depth=0.2, vertices=8, parent=glass, emit=1.0)
    aim = empty((0, 1, 2.0), r)
    blf = light((-3, -6, 4), 900, 'FFD8B0', 5.0, aim, parent=r)
    light((5, -4, 2.5), 320, '8A7AE8', 4.0, aim, parent=r)
    light((0, 3.2, 4.6), 260, 'FF9A3A', kind='POINT', parent=r)
    return dict(glass=glass, blf=blf)


def set_ops(r):
    add('cube', '2A3038', (0, 0, -0.1), scale=(18, 12, 0.2), size=1, parent=r)
    add('cube', '1A2230', (0, 4.2, 3), scale=(18, 0.3, 6.4), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '202A3A', (sx * 9, 0, 3), scale=(0.3, 12, 6.4), size=1, parent=r)
    # wall chart: the Gulf south of Louisiana, with the search box
    add('cube', '0E3A5C', (0, 4.0, 2.9), scale=(9.6, 0.08, 4.4), size=1, parent=r, emit=0.5)
    for x, w_, hgt in ((-4.0, 1.6, 1.0), (-2.6, 1.4, 0.7), (-1.3, 1.5, 1.2), (0.0, 1.3, 0.8), (1.2, 1.4, 1.5), (2.5, 1.5, 0.9), (3.9, 1.6, 0.6)):
        add('cube', '8A9A6A', (x, 3.95, 5.1 - hgt / 2), scale=(w_, 0.06, hgt), size=1, parent=r, emit=0.35)
    add('cube', '8A9A6A', (1.5, 3.95, 3.5), rot=(0, 0.5, 0), scale=(0.28, 0.06, 1.0), size=1, parent=r, emit=0.35)
    for i in range(12):
        add('cube', 'FFFFFF', (-4.4 + i * 0.8, 3.94, 1.5 + (i % 2) * 0.0), scale=(0.02, 0.04, 2.6), size=1, parent=r, emit=0.15)
    box = []
    for (x, z, w_, hgt) in ((0.6, 3.3, 5.4, 0.07), (0.6, 1.1, 5.4, 0.07), (-2.1, 2.2, 0.07, 2.2), (3.3, 2.2, 0.07, 2.2)):
        box.append(add('cube', 'FF7A1A', (x, 3.92, z), scale=(w_, 0.05, hgt), size=1, parent=r, emit=6))
    for i in range(9):
        add('cube', 'FFFFFF', (1.5 - i * 0.02, 3.92, 3.1 - i * 0.24), scale=(0.07, 0.05, 0.12), size=1, parent=r, emit=3)
    blip = add('ico_sphere', 'E5392F', (1.4, 3.88, 2.5), radius=0.09, subdivisions=1, parent=r, emit=20)
    for sx in (-1, 1):
        add('cube', '3A4252', (sx * 6.4, 2.6, 0.8), scale=(3.2, 1.3, 1.6), size=1, parent=r)
        for j in range(2):
            add('cube', '15181F', (sx * 6.4 - 0.7 + j * 1.4, 2.7, 2.2), rot=(-0.2, 0, 0), scale=(1.1, 0.1, 0.9), size=1, parent=r)
            add('cube', '3DDC84' if j else '5EC8F0', (sx * 6.4 - 0.7 + j * 1.4, 2.63, 2.2), rot=(-0.2, 0, 0), scale=(0.95, 0.04, 0.72), size=1, parent=r, emit=2.2)
        add('cylinder', 'FFE7B8', (sx * 4.5, 0.5, 5.9), radius=0.5, depth=0.08, vertices=10, parent=r, emit=3)
    add('cube', 'E5392F', (-7.6, 4.0, 4.9), scale=(0.9, 0.08, 0.4), size=1, parent=r, emit=4)
    aim = empty((0, 2.5, 2.3), r)
    light((-3, -6, 4.2), 1000, 'FFE2C8', 5.0, aim, parent=r)
    light((6, -3, 2), 420, '5E8FD0', 4.0, aim, parent=r)
    light((0, 1.5, 5.4), 200, 'FF7A1A', kind='POINT', parent=r)
    return dict(blip=blip, sbox=box)


def set_ward(r):
    add('cube', 'B8C4C0', (0, 0, -0.1), scale=(16, 12, 0.2), size=1, parent=r)
    add('cube', 'CFE0DC', (0, 4.2, 3), scale=(16, 0.3, 6.4), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', 'BFD2CE', (sx * 8, 0, 3), scale=(0.3, 12, 6.4), size=1, parent=r)
    add('cube', '8ABAC0', (0, 4.02, 0.6), scale=(16, 0.06, 1.2), size=1, parent=r)
    # window with morning light
    add('cube', 'F2EEE4', (4.2, 4.02, 3.4), scale=(3.6, 0.1, 2.8), size=1, parent=r)
    add('cube', 'FFD9A0', (4.2, 3.98, 3.4), scale=(3.3, 0.1, 2.5), size=1, parent=r, emit=3.5)
    add('cube', 'F2EEE4', (4.2, 3.94, 3.4), scale=(0.1, 0.1, 2.5), size=1, parent=r)
    add('cube', 'F2EEE4', (4.2, 3.94, 3.4), scale=(3.3, 0.1, 0.1), size=1, parent=r)
    # bed along Y, head at the wall
    add('cube', '9AA0B4', (0, 1.4, 0.55), scale=(2.7, 5.2, 0.3), size=1, parent=r)
    add('cube', 'F4F4F0', (0, 1.4, 0.85), scale=(2.6, 5.1, 0.34), size=1, parent=r)
    add('cube', '9AA0B4', (0, 3.9, 1.5), scale=(2.8, 0.14, 2.0), size=1, parent=r)
    add('cube', 'FFFFFF', (0, 3.3, 1.25), rot=(0.5, 0, 0), scale=(1.9, 0.9, 0.36), size=1, parent=r)
    add('cube', '5EA8C8', (0, 0.2, 1.12), scale=(2.66, 2.9, 0.3), size=1, parent=r)
    for sx in (-1, 1):
        for y in (-1.0, 3.7):
            add('cylinder', '9AA0B4', (sx * 1.25, y, 0.25), radius=0.07, depth=0.5, vertices=6, parent=r)
    # drip stand and a heart monitor
    add('cylinder', 'C8C4B8', (-2.1, 3.2, 2.2), radius=0.04, depth=4.4, vertices=5, parent=r)
    add('cube', 'C8C4B8', (-2.1, 3.2, 4.35), scale=(0.7, 0.05, 0.05), size=1, parent=r)
    add('cube', 'BFEFFF', (-2.35, 3.2, 3.85), scale=(0.3, 0.12, 0.6), size=1, parent=r, emit=0.6, rough=0.2)
    add('cube', '3A4252', (-3.4, 3.5, 1.0), scale=(1.2, 0.9, 2.0), size=1, parent=r)
    add('cube', '15181F', (-3.4, 3.3, 2.6), rot=(-0.15, 0, 0), scale=(1.3, 0.12, 1.0), size=1, parent=r)
    add('cube', '0A2A1C', (-3.4, 3.22, 2.6), rot=(-0.15, 0, 0), scale=(1.15, 0.04, 0.85), size=1, parent=r, emit=1.0)
    beat = [add('cube', '3DDC84', (-3.9 + i * 0.11, 3.18, 2.6), rot=(-0.15, 0, 0), scale=(0.07, 0.03, 0.08), size=1, parent=r, emit=12) for i in range(10)]
    add('cube', '8A6238', (3.2, 3.3, 0.7), scale=(1.3, 1.0, 1.4), size=1, parent=r)
    add('cylinder', 'F05A8C', (3.2, 3.3, 1.7), radius=0.2, depth=0.6, vertices=6, parent=r)
    add('cube', '6A7A84', (6.6, 1.5, 0.9), scale=(1.4, 1.4, 0.2), size=1, parent=r)
    add('cube', '6A7A84', (6.6, 2.15, 1.7), scale=(1.4, 0.16, 1.6), size=1, parent=r)
    add('cylinder', 'FFF8E8', (0, 0.5, 5.9), radius=0.6, depth=0.08, vertices=10, parent=r, emit=3)
    aim = empty((0, 1.6, 2.2), r)
    light((-3, -6, 4.4), 1100, 'FFF0E0', 5.0, aim, parent=r)
    light((5.5, 1.5, 3.4), 700, 'FFC070', 3.0, aim, parent=r)
    light((4, -5, 1.5), 260, '8AB8E8', 4.0, aim, parent=r)
    return dict(beat=beat)


def make_plane(r):
    """Patrol plane, nose toward +X. Generic white and orange, twin props, high wing."""
    add('cylinder', 'F2F2EE', (0, 0, 0), rot=(0, PI / 2, 0), radius=1.0, depth=10, vertices=8, parent=r)
    add('cone', 'F2F2EE', (5.9, 0, 0), rot=(0, PI / 2, 0), radius1=1.0, radius2=0.2, depth=1.8, vertices=8, parent=r)
    add('cone', 'F2F2EE', (-6.4, 0, 0.3), rot=(0, -PI / 2, 0), radius1=1.0, radius2=0.25, depth=3.0, vertices=8, parent=r)
    add('cube', 'E8541E', (2.6, 0, 0), scale=(1.0, 2.04, 2.04), size=1, parent=r)
    add('cube', 'F2F2EE', (0, 0, 1.05), scale=(2.4, 19, 0.24), size=1, parent=r)
    add('cube', 'E8541E', (-7.4, 0, 1.6), rot=(0, -0.4, 0), scale=(1.6, 0.16, 2.6), size=1, parent=r)
    add('cube', 'F2F2EE', (-7.5, 0, 0.8), scale=(1.4, 5.6, 0.14), size=1, parent=r)
    props = []
    for sy in (-1, 1):
        add('cylinder', 'D8D8D8', (0.6, sy * 3.4, 0.75), rot=(0, PI / 2, 0), radius=0.5, depth=2.6, vertices=6, parent=r)
        p = empty((2.0, sy * 3.4, 0.75), r)
        for a in (0, PI / 2):
            add('cube', '20242B', (0, 0, 0), rot=(a, 0, 0), scale=(0.08, 3.2, 0.26), size=1, parent=p)
        props.append(p)
    return props


def make_boat(r):
    """Response boat, bow toward +X: grey hull, orange collar, small cabin."""
    add('cube', '8A929E', (0, 0, 0.5), scale=(7.2, 2.6, 1.0), size=1, parent=r)
    diamond('8A929E', 3.6, 0.5, 2.6, 1.0, r)
    add('cube', 'E8541E', (0, 0, 1.05), scale=(7.5, 3.0, 0.4), size=1, parent=r)
    diamond('E8541E', 3.7, 1.05, 3.0, 0.4, r)
    add('cube', 'F2F2EE', (-0.4, 0, 1.9), scale=(3.0, 2.1, 1.5), size=1, parent=r)
    add('cube', '0E1520', (1.12, 0, 2.1), scale=(0.06, 1.8, 0.7), size=1, parent=r, rough=0.2)
    for sy in (-1, 1):
        add('cube', '0E1520', (-0.3, sy * 1.06, 2.1), scale=(2.2, 0.04, 0.6), size=1, parent=r, rough=0.2)
        add('cube', '20242B', (-3.9, sy * 0.7, 0.9), scale=(0.7, 0.7, 1.3), size=1, parent=r)
    add('cylinder', 'C8C4B8', (-0.8, 0, 3.3), radius=0.05, depth=1.4, vertices=5, parent=r)
    add('ico_sphere', '5EC8F0', (-0.8, 0, 4.05), radius=0.16, subdivisions=1, parent=r, emit=30)
    add('ico_sphere', 'FFF8E0', (0.9, 0, 2.8), radius=0.16, subdivisions=1, parent=r, emit=20)


def extend(S):
    for name, fn in (('bar', set_bar), ('ops', set_ops), ('ward', set_ward)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    # the sun deck by day: find the evening sky pieces so day shots can swap them for a blue sea
    dk = S['colls']['deck']
    S['deck_eve'] = [o for o in dk.objects if (o.type == 'MESH' and o.data.materials and o.data.materials[0].name.split('.')[0] in ('5A3A6A', 'FFB060', 'E0522E'))
                     or (o.type == 'LIGHT' and o.data.energy > 50000)]
    before = set(bpy.data.objects)
    o = empty(ORG['deck'])
    S['deck_day'] = [add('plane', '1E6A9A', (0, 220, -9), size=640, parent=o, rough=0.25)]
    # a deck house on the left and a lifeboat on the right so the wide frame has ends
    add('cube', 'E6E2D8', (-13.5, 1.5, 2.6), scale=(6, 9, 5.2), size=1, parent=o)
    for z in (1.6, 3.6):
        add('cube', 'FFD27A', (-10.48, 1.5, z), scale=(0.06, 6.5, 0.9), size=1, parent=o, emit=1.5)
    add('cube', 'FF7A1A', (-10.47, 1.5, 4.9), scale=(0.06, 9, 0.25), size=1, parent=o, emit=0.6)
    add('cube', 'E8541E', (12.5, 4.2, 1.5), scale=(5.5, 1.9, 1.5), size=1, parent=o)
    add('cube', 'F2EEE4', (12.5, 4.2, 2.45), scale=(5.0, 1.7, 0.5), size=1, parent=o)
    for x in (10.3, 14.7):
        add('cylinder', '9AA0B4', (x, 4.2, 2.2), radius=0.09, depth=4.4, vertices=5, parent=o)
    for ob in set(bpy.data.objects) - before:
        for uc in list(ob.users_collection):
            uc.objects.unlink(ob)
        dk.objects.link(ob)
    # cast
    S['sister'] = K.Rig(SIS, K.human_head('E0A882', '8A4A2A'))
    add('ico_sphere', '8A4A2A', (0, 0.16, -0.12), scale=(1.0, 0.7, 1.5), radius=0.26, subdivisions=1, parent=S['sister'].head)
    S['guard'] = K.Rig(GUARD, K.human_head('B8805A', '15181F'))
    add('cylinder', '1C2A4A', (0, 0, 0.3), radius=0.33, depth=0.12, vertices=8, parent=S['guard'].head)
    add('cube', '1C2A4A', (0, -0.3, 0.26), scale=(0.5, 0.3, 0.04), size=1, parent=S['guard'].head)
    S['gphoto'] = add('cube', 'F4EEDF', (0, -0.1, -0.62), rot=(0.3, 0, 0), scale=(0.42, 0.03, 0.5), size=1, parent=S['guard'].el[0])
    S['officer'] = K.Rig(OFFICER, K.human_head('D8A07A', '3A2A1C'))
    add('cylinder', 'F2F2EE', (0, 0, 0.3), radius=0.33, depth=0.12, vertices=8, parent=S['officer'].head)
    add('cube', '15181F', (0, -0.3, 0.26), scale=(0.5, 0.3, 0.04), size=1, parent=S['officer'].head)
    S['fam'] = []
    for i in range(8):
        f = empty(FAR)
        hgt = 1.9 + 0.5 * ((i * 0.37) % 1) if i % 4 != 3 else 1.3
        add('cone', FAMC[i], (0, 0, hgt / 2), radius1=0.5, radius2=0.3, depth=hgt, vertices=6, parent=f)
        add('ico_sphere', ('E0A882', 'C68A5E', 'D8A07A')[i % 3], (0, 0, hgt + 0.3), radius=0.3, subdivisions=1, parent=f)
        add('ico_sphere', ('5A3A22', '15181F', 'C8C4B8', '8A4A2A')[i % 4], (0, 0.06, hgt + 0.4), radius=0.3, subdivisions=1, parent=f)
        for sx in (-1, 1):
            add('cylinder', FAMC[i], (sx * 0.42, 0, hgt * 0.72), rot=(0, sx * 0.3, 0), radius=0.08, depth=0.9, vertices=5, parent=f)
        S['fam'].append(f)
    S['jelly'] = []
    for i in range(12):
        j = empty(FAR)
        col = ('F05A8C', '8AD8F0', 'C89AF0')[i % 3]
        add('ico_sphere', col, (0, 0, 0), scale=(1, 1, 0.62), radius=0.42, subdivisions=1, parent=j, emit=3.2)
        for q in range(4):
            a = q * PI / 2 + i
            add('cylinder', col, (math.cos(a) * 0.2, math.sin(a) * 0.2, -0.6), radius=0.03, depth=1.0, vertices=4, parent=j, emit=1.6)
        S['jelly'].append(j)
    S['plane'] = empty(FAR)
    S['pprops'] = make_plane(S['plane'])
    S['boat'] = empty(FAR)
    make_boat(S['boat'])
    S['sling'] = add('torus', 'F2B531', FAR, major_radius=0.52, minor_radius=0.11, major_segments=10, minor_segments=5, rough=0.6)
    S['wk'] = [add('cube', 'DFF0FF', FAR, scale=(3.0, 1.6, 0.06), size=1, emit=0.5) for _ in range(18)]
    S['dayl'] = light((0, 0, 50), 0, 'FFF4E0', kind='SUN')
    S['dayl'].rotation_euler = (0.85, 0.0, 0.7)
    S['blanket'] = add('cube', '5EA8C8', FAR, scale=(1.5, 2.6, 0.5), size=1)


_build0, _reset0, _finish0 = build, reset, finish
XCAST = ('sister', 'guard', 'officer')


def build():
    S = _build0()
    extend(S)
    return S


def reset(S):
    _reset0(S)
    for who in XCAST:
        S[who].place(FAR)
        S[who].apply(P())
        S['face'][who] = 'calm'
    for o in S['fam'] + S['jelly'] + S['wk']:
        o.location, o.rotation_euler, o.scale = FAR, (0, 0, 0), (1, 1, 1)
    for kk in ('plane', 'boat', 'sling', 'blanket'):
        S[kk].location, S[kk].rotation_euler = FAR, (0, 0, 0)
    S['glass'].location = (0, 0, -20)
    S['gphoto'].hide_render = True
    S['dayl'].data.energy = 0
    S['utop'].hide_render = False
    S['blf'].data.energy = 900
    for o in S['deck_eve']:
        o.hide_render = False
    for o in S['deck_day']:
        o.hide_render = True
    S['blip'].scale = (1, 1, 1)
    S['moonl'].data.color = K.hexc('9AB8E8')[:3]
    S['sunl'].data.color = K.hexc('FF9A50')[:3]


def finish(S, t):
    _finish0(S, t)
    for who in XCAST:
        e = S['face'][who]
        kk = dict(scared=1.3, shock=1.8, calm=1.0, sad=0.6, happy=0.85, closed=0.1, tired=0.5).get(e, 1.0)
        for ey in S[who].extra['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], 0.075 * kk)
        S[who].extra['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)


def gulf_day(S, t, rough=0.8):
    A = gulf(S, t, 'dawn', rough)
    sky(S, '7FB4E0', 1.0)
    S['moonl'].data.energy = 60000
    S['moonl'].data.color = (1.0, 0.97, 0.9)
    S['dayl'].data.energy = 3.2
    return A


def gulf_rise(S, t, k, rough=0.7):
    A = gulf(S, t, 'dawn', rough)
    S['sun'].location = (-30, 480, lerp(-34, 12, k))
    S['band'].location = (0, 520, 6)
    sky(S, lerp_col('2A2A4E', '8A5A6E', k), 1.0)
    S['sunl'].data.energy = lerp(40000, 240000, k)
    S['moonl'].data.energy = 50000
    return A


def deck_day(S):
    A = show(S, 'deck')
    sky(S, '8FC4EA', 1.0)
    for o in S['deck_eve']:
        o.hide_render = True
    for o in S['deck_day']:
        o.hide_render = False
    S['dayl'].data.energy = 3.6
    return A


# ---------------------------------------------------------------- long-form shots: boarding and the family
def family_board(S, k, t, lt):
    A = show(S, 'pier')
    sky(S, '2A2248', 1.0)

    def on_way(u):
        y = lerp(-1.2, 8.0, u)
        if y < 1.8:
            return A(lerp(0.6, -4.6, (y + 1.2) / 3.0), y, 0)
        return A(-4.6, y, (y - 1.8) * 0.459 + 0.12)
    for i, f in enumerate(S['fam'][:6]):
        u = (k * 0.35 + i * 0.13 + 0.12) % 1
        f.location = on_way(u)
        f.location.z += 0.08 * abs(math.sin(t * 6 + i))
    S['james'].place(on_way(0.03 + k * 0.35), -2.2 if k < 0.6 else -2.6)
    S['james'].apply(blend(walk(t, 1.6), P('stand', aR=(2.7, 0.3 + 0.3 * math.sin(t * 9), 0.2), head=(-0.1, 0.4)), 0.6))
    S['face']['james'] = 'happy'
    S['rook'].place(A(3.6, -1.2, 0), -1.0)
    S['rook'].apply(P('cross', head=(0.04, -0.45 + 0.4 * ease((lt - 0.8) / 0.5))))
    S['face']['rook'] = 'deadpan'
    key(S, 'kw', A(4, -7, 4), A(1, 0, 2), 900)
    cam(S, A(lerp(5.4, 4.6, k), lerp(-8.4, -7.4, k), 2.3), A(-0.6, 2.4, 2.3), 30)


def james_deck(S, k, t, lt):
    A = show(S, 'deck')
    sky(S, '3A2A5E', 1.2)
    S['james'].place(A(-0.4, 4.2, 0), 0.3)
    S['james'].apply(P('hips', head=(-0.05, 0.3 * math.sin(t * 1.4))))
    S['face']['james'] = 'happy'
    for i, (x, y) in enumerate(((-3.3, 4.6), (-2.2, 3.9), (1.6, 4.5), (2.7, 3.8), (3.9, 4.6), (-4.6, 3.7), (5.2, 3.9), (0.9, 3.4))):
        S['fam'][i].location = A(x, y, 0.08 * abs(math.sin(t * 4 + i * 1.7)))
        S['fam'][i].rotation_euler = (0, 0, 0.3 * math.sin(t * 1.3 + i))
    for i, b in enumerate(S['bulbs']):
        s = 1.0 + 0.5 * math.sin(t * 6 + i * 1.3)
        b.scale = (s, s, s)
    key(S, 'kw', A(-3, -4, 3.5), A(0, 4, 2.2), 1500)
    key(S, 'kc', A(5, -3, 2), A(0, 4, 2.2), 400)
    cam(S, A(lerp(2.6, 1.4, k), lerp(-4.6, -3.6, k), 2.4), A(-0.1, 4.2, 2.15), 32)


# ---------------------------------------------------------------- long-form shots: the bar
def bar(S, dim=1.0):
    A = show(S, 'bar')
    sky(S, '06040A')
    S['blf'].data.energy = 900 * dim
    return A


def sit(**over):
    d = dict(lL=(1.45, 1.5), lR=(1.45, 1.5), aL=(0.55, 0.1, 1.2, 0.6), aR=(0.55, 0.1, 1.2, 0.6), lift=0.0, lean=0.05)
    d.update(over)
    return P('stand', **d)


def bar_two(S, k, t, lt):
    A = bar(S)
    g = 0.5 + 0.5 * math.sin(t * 7)
    S['james'].place(A(-0.9, 0.9, 0.05), 0.55)
    S['james'].apply(sit(aL=(1.0, 0.7, 0.5, 0.3), aR=(0.9 + 0.5 * g, 0.25, 1.2, 0.9), head=(-0.05, 0.35 + 0.1 * math.sin(t * 3))))
    S['face']['james'] = 'happy'
    S['sister'].place(A(0.9, 0.9, 0.05), -0.55)
    S['sister'].apply(sit(aR=(1.3, 0.2, 1.9, 0.4), head=(-0.05 + 0.06 * math.sin(t * 8), -0.4)))
    S['face']['sister'] = 'happy'
    S['glass'].location = (0.1, 2.0, 1.67)
    cam(S, A(lerp(-2.6, -1.4, k), lerp(-5.6, -4.8, k), 2.6), A(0, 0.9, 2.3), 38)


def bar_leave(S, k, t, lt):
    A = bar(S)
    e = ease((lt - 0.2) / 2.2)
    x = lerp(-1.3, -6.6, e)
    S['james'].place(A(x, lerp(0.5, 0.2, e), 0), -PI / 2 + 0.25 * (1 - e))
    S['james'].apply(walk(t, 1.5) if lt > 0.2 else P('stand'))
    S['sister'].place(A(0.9, 0.9, 0.05), -0.75)
    S['sister'].apply(sit(aR=(2.4, 0.5 + 0.25 * math.sin(t * 8), 0.4), head=(-0.05, -0.75)))
    S['face']['sister'] = 'happy'
    S['glass'].location = (0.1, 2.0, 1.67)
    cam(S, A(lerp(3.4, 2.6, k), lerp(-6.4, -5.8, k), 2.5), A(lerp(-1.0, -2.6, k), 0.9, 2.3), 30)


def bar_empty(S, k, t, lt):
    A = bar(S, 0.55)
    S['sister'].place(A(0.9, 0.9, 0.05), -0.3)
    look = ease((lt - 0.5) / 0.5) - ease((lt - 1.8) / 0.5)
    S['sister'].apply(sit(head=(0.12, lerp(-0.2, -1.0, look))))
    S['face']['sister'] = 'sad'
    S['glass'].location = (-0.9, 2.0, 1.67)
    key(S, 'kw', A(-2.4, -1.5, 4.5), A(-0.9, 0.9, 1.1), 420)
    cam(S, A(lerp(-3.6, -2.6, k), lerp(-4.6, -3.9, k), 2.5), A(-0.2, 0.9, 2.2), 36)


def rook_bar(S, k, t, lt):
    A = bar(S, 0.6)
    tap = 0.5 + 0.5 * math.sin(t * 9)
    S['rook'].place(A(-1.0, 0.0, 0), 0.5)
    S['rook'].apply(P('stand', aR=(1.25, 0.1, 2.25 + 0.12 * tap, 0.75), head=(0.25 - 0.25 * ease((lt - 0.9) / 0.4), 0.5 - 0.6 * ease((lt - 0.9) / 0.4))))
    S['face']['rook'] = S['prm'].get('expr', 'sad')
    S['glass'].location = (-0.9, 2.0, 1.67)
    key(S, 'kw', A(-3.5, -4, 3.4), A(-1, 0, 2.3), 600)
    cam(S, A(lerp(1.6, 1.1, k), lerp(-4.8, -4.2, k), 2.5), A(-0.6, 0.4, 2.35), 40)


# ---------------------------------------------------------------- long-form shots: the night
def ship_night(S, k, t, lt):
    A = gulf(S, t, 'night', 0.8)
    S['liner'].location = (4, lerp(46, 70, k), 0.2)
    S['liner'].rotation_euler = (0, 0, PI / 2 + 0.12)
    for i, w in enumerate(S['wk'][:10]):
        y = S['liner'].location.y - 30 - i * 5.5
        w.location = A(4 - 0.65 * i * 0.4 + 0.5 * math.sin(t * 2 + i), y, swell(4, y, t, 0.8) + 0.12)
        w.scale = (0.5 + i * 0.08, 1.0, 1)
    h = afloat(S, 'james', A, -1.5, 2, t, PI, tread(t, (-0.1, 0.0)), rough=0.8, face='scared')
    key(S, 'kc', A(-6, -6, 6), A(-1.5, 2, 1), 2400)
    cam(S, A(lerp(-10, -8, k), lerp(-12, -10, k), lerp(7.5, 6.0, k)), A(2.5, 34, 4.5), 28)


def swim_night(S, k, t, lt):
    A = gulf(S, t, 'night', 0.8)
    y = lerp(3.0, -1.0, k)
    h = swell(0, y, t, 0.8)
    w = t * 6.0
    S['james'].place(A(0, y, h - 0.3), 0.0, 1.36, 0.3 * math.sin(w))
    S['james'].apply(P('swim', aL=(1.6 + 1.5 * math.sin(w), 0.25, 0.5), aR=(1.6 - 1.5 * math.sin(w), 0.25, 0.5),
                       lL=(0.35 * math.sin(w * 2), 0.25), lR=(-0.35 * math.sin(w * 2), 0.25), head=(-0.75, 0.5 * math.sin(w))))
    S['face']['james'] = 'scared'
    spray(S, A(0, y - 0.2, h + 0.1), (lt * 1.8) % 1, 12, 1.2, seed=int(lt * 1.8), size=1.1)
    key(S, 'kc', A(-4, y - 6, 5), A(0, y, 0.4), 2600)
    key(S, 'kw', A(4, y - 4, 2), A(0, y, 0.4), 420)
    cam(S, A(lerp(2.8, 2.2, k), y - lerp(6.6, 5.6, k), 3.0), A(0, y - 0.4, 0.5), 36, 0.03 * math.sin(t * 1.4))


def jelly(S, k, t, lt):
    A = show(S, 'under')
    sky(S, '0A2440', 1.0)
    S['utop'].hide_render = True
    kick = math.sin(t * 7)
    S['james'].place(A(0, 0, 4.2), 0.3 + 0.3 * math.sin(t * 0.8), 0, 0.1 * math.sin(t * 1.3))
    S['james'].apply(P('stand', lL=(0.5 * kick, 0.5 + 0.3 * kick), lR=(-0.5 * kick, 0.5 - 0.3 * kick), aL=(0.4, 1.2, 0.4), aR=(0.4, 1.2, 0.4)))
    for i, j in enumerate(S['jelly']):
        a = i * 0.9 + t * 0.12
        rr = 1.6 + (i * 0.618 % 1) * 3.4
        z = 2.2 + (i * 0.37 % 1) * 3.4 + 0.25 * math.sin(t * 1.1 + i)
        j.location = A(math.cos(a) * rr, math.sin(a) * rr * 0.7 - 0.6, z)
        p = 0.5 + 0.5 * math.sin(t * 3.2 + i * 1.7)
        s = 0.9 + 0.5 * (i % 3) * 0.4
        j.scale = (s * (1.15 - 0.3 * p), s * (1.15 - 0.3 * p), s * (0.8 + 0.4 * p))
        j.rotation_euler = (0.2 * math.sin(t + i), 0.2 * math.cos(t * 0.8 + i), 0)
    rise(S, A(0, 0, 3.4), t, 10, 0.7, 2.6, 2.0, size=0.8)
    key(S, 'kc', A(-3, -6, 5), A(0, 0, 4.2), 1200)
    cam(S, A(lerp(-2.6, -1.2, k), lerp(-8.6, -7.6, k), lerp(2.6, 3.2, k)), A(0, 0, 4.2), 30, 0.04 * math.sin(t * 1.5))


def sunrise(S, k, t, lt):
    A = gulf_rise(S, t, k)
    h = afloat(S, 'james', A, 0.5, 3, t, PI - 0.1, tread(t, (-0.15, 0.0)), rough=0.7, face='tired')
    key(S, 'kc', A(4, -4, 3), A(0.5, 3, 0.8), 500)
    cam(S, A(lerp(2.8, 1.8, k), lerp(-6.5, -5.5, k), h + 1.6), A(-1.5, 30, lerp(3.4, 4.2, k)), 34)


def rook_sun(S, k, t, lt):
    A = gulf_rise(S, t, 1.0)
    turn = ease((lt - 0.7) / 0.6)
    h = rook_float(S, A, 0, 0, t, lerp(PI - 0.7, 0.3, turn), P('stand', head=(0.05, 0.3 * (1 - turn)), **RING_ARMS), S['prm'].get('expr', 'sad'), 0.7)
    afloat(S, 'james', A, -4.2, 7.0, t, 0.6, tread(t, (-0.1, 0.0)), rough=0.7, face='tired')
    key(S, 'kw', A(-3, -5, 3.2), A(0, 0, h + 1.3), 1800)
    cam(S, A(lerp(1.9, 1.3, k), lerp(-5.6, -4.8, k), h + 1.9), A(-0.4, 0.4, h + 1.3), 38)


# ---------------------------------------------------------------- long-form shots: the alarm
def deck_search(S, k, t, lt):
    A = deck_day(S)
    x = lerp(-3.4, 0.6, k)
    S['guard'].place(A(x, 2.6, 0), PI / 2 - 0.5)
    S['guard'].apply(blend(walk(t, 1.5), P('stand', aL=(1.5, 0.15, 0.5), head=(0.0, 0.6 * math.sin(t * 2.0))), 0.55))
    S['gphoto'].hide_render = False
    S['face']['guard'] = 'scared'
    S['rook'].place(A(x - 2.4, 4.4, 0), PI / 2 - 0.9)
    S['rook'].apply(blend(walk(t + 0.2, 1.5), P('stand', head=(0.05, -0.6 * math.sin(t * 2.0))), 0.4))
    S['face']['rook'] = 'calm'
    S['fam'][1].location, S['fam'][4].location = A(4.4, 4.6, 0), A(5.4, 4.3, 0)
    cam(S, A(lerp(2.6, 3.4, k), lerp(-3.2, -2.6, k), 2.3), A(x - 1.0, 3.4, 2.1), 34)


def hall_search(S, k, t, lt):
    A = show(S, 'hall')
    sky(S, '020203')
    y = lerp(11, 6.5, k)
    S['guard'].place(A(0.7, y, 0), 0.15)
    kn = max(0, math.sin(lt * 9))
    S['guard'].apply(blend(walk(t, 1.4), P('stand', aL=(1.4, 0.2, 0.5), aR=(1.5, 0.9, 1.2 + 0.5 * kn), head=(0.0, 0.7 * math.sin(t * 1.8))), 0.6))
    S['gphoto'].hide_render = False
    S['face']['guard'] = 'scared'
    key(S, 'kw', A(-1.2, y - 5, 2.6), A(0.7, y, 2.2), 500)
    cam(S, A(-0.9, lerp(0.5, 2.0, k), 1.9), A(0.4, y, 2.15), 36, 0.03 * math.sin(t * 1.3))


def ship_turn(S, k, t, lt):
    A = gulf_day(S, t, 0.6)
    R_ = 26
    ang = lerp(-0.9, 0.95, k)
    S['liner'].location = (-R_ + R_ * math.cos(ang) + 6, 46 + R_ * math.sin(ang), 0.2)
    S['liner'].rotation_euler = (0, 0.03, ang + PI / 2)
    for i, w in enumerate(S['wk']):
        a = ang - 0.085 * (i + 4.6)
        x, y = -R_ + R_ * math.cos(a) + 6, 46 + R_ * math.sin(a)
        w.location = A(x, y, swell(x, y, t, 0.6) + 0.15)
        w.rotation_euler = (0, 0, a + PI / 2)
        w.scale = (1.0, 1.4 + i * 0.22, 1)
    cam(S, A(lerp(34, 30, k), lerp(-14, -10, k), lerp(24, 20, k)), A(-4, 44, 3), 30)


# ---------------------------------------------------------------- long-form shots: the search
def search_air(S, k, t, lt):
    A = gulf_day(S, t, 0.8)
    helo_at(S, (lerp(-16, 9, k), 12, 9.5), 0.0, t)
    h = rook_float(S, A, -2.2, -1.0, t, PI + 0.6, P('stand', head=(-0.45, lerp(0.7, -0.5, k)), **RING_ARMS), 'calm', 0.8)
    spray(S, A(lerp(-16, 9, k), 12, 0.5), (lt * 1.5) % 1, 16, 3.6, seed=1, size=1.0)
    key(S, 'kw', A(-5, -6, 3), A(-2.2, -1, 1.4), 2000)
    cam(S, A(lerp(1.6, 1.0, k), lerp(-8.0, -7.2, k), 1.5), A(lerp(-4, 0, k), 6, 5.6), 26)


def search_boat(S, k, t, lt):
    A = gulf_day(S, t, 1.0)
    x, y = lerp(-6, 0.5, k), lerp(26, 9, k)
    hz = swell(x, y, t, 1.0)
    S['boat'].location = A(x, y, hz + 0.25)
    S['boat'].rotation_euler = (0.08 * math.sin(t * 3.1), -0.1 + 0.14 * math.sin(t * 4.3), -PI / 2 + 0.33)
    S['boat'].scale = (1.9, 1.9, 1.9)
    spray(S, A(x + 1.0, y - 4.6, hz + 0.4), (lt * 2.4) % 1, 16, 3.0, seed=int(lt * 2.4), size=1.5)
    spray(S, A(x - 1.2, y + 5, hz + 0.3), (lt * 2.4 + 0.5) % 1, 12, 2.4, seed=3, size=1.2, start=16)
    cam(S, A(lerp(5.5, 4.5, k), lerp(-5, -3.5, k), 2.4), A(x, y, 2.4), 34, 0.03 * math.sin(t * 2))


def search_plane(S, k, t, lt):
    A = gulf_day(S, t, 0.7)
    x = lerp(-26, 22, k)
    S['plane'].location = A(x, 34, 15 + 0.8 * math.sin(t * 0.9))
    S['plane'].scale = (1.5, 1.5, 1.5)
    S['plane'].rotation_euler = (0.32, -0.04, 0.05)
    for p in S['pprops']:
        p.rotation_euler = (t * 29, 0, 0)
    cam(S, A(lerp(-2, 2, k), -8, 1.4), A(x * 0.6, 34, 10.5), 34)


def ops(S):
    A = show(S, 'ops')
    sky(S, '020306')
    return A


def ops_room(S, k, t, lt):
    A = ops(S)
    p = 1.0 + 0.7 * abs(math.sin(t * 4))
    S['blip'].scale = (p, p, p)
    key(S, 'kw', A(-1, -4, 4.5), A(0, 2.5, 2.4), 1500)
    key(S, 'kc', A(5, -2, 3), A(3, 1.4, 2.4), 500)
    S['officer'].place(A(-2.9, 2.6, 0), PI - 0.95)
    S['officer'].apply(P('point', aR=(1.75 + 0.1 * math.sin(lt * 5), 0.2, 0.1), aL=(0.4, 0.2, 1.3, 0.8), head=(-0.05, -0.2)))
    S['rook'].place(A(3.0, 1.4, 0), -0.55)
    S['rook'].apply(P('cross', head=(0.03, -0.9 + 0.95 * ease((lt - 1.0) / 0.5))))
    S['face']['rook'] = S['prm'].get('expr', 'deadpan')
    cam(S, A(lerp(-1.4, -0.6, k), lerp(-5.6, -4.8, k), 2.6), A(0.2, 3.0, 2.5), 34)


def rook_chart(S, k, t, lt):
    A = ops(S)
    p = 1.0 + 0.7 * abs(math.sin(t * 4))
    S['blip'].scale = (p, p, p)
    tap = max(0, math.sin(lt * 5)) * 0.25
    S['rook'].place(A(2.9, 2.9, 0), PI - 1.0)
    S['rook'].apply(P('stand', aR=(2.0 + tap, -0.5, 0.25), head=(0, -1.3 * ease((lt - 0.7) / 0.5))))
    S['face']['rook'] = S['prm'].get('expr', 'deadpan')
    key(S, 'kw', A(0, -3, 3.4), A(2.9, 2.9, 2.4), 1300)
    cam(S, A(lerp(-0.4, 0.3, k), lerp(-3.4, -2.6, k), 2.6), A(2.2, 3.4, 2.6), 38)


# ---------------------------------------------------------------- long-form shots: the sling, the ward, the rail
def sling(S, k, t, lt):
    A = gulf(S, t, 'night', 0.9)
    helo_at(S, (-1.0, 3.0, 12.5), 0.35, t, spot=200000, cone=False, cable=10.6)
    hx, hy = S['helo'].location.x, S['helo'].location.y
    cx, cy = hx + 3.0 * math.sin(0.35), hy - 3.0 * math.cos(0.35)
    drop = ease((lt - 0.5) / 0.7)
    h = afloat(S, 'swimmer', A, cx + 0.75, cy + 0.1, t, 1.0, P('stand', aL=(1.3, -0.3, 0.9), aR=(1.3, 0.3, 0.9), head=(0.2, 0.3)), sink=1.45, rough=0.9, face='calm')
    afloat(S, 'james', A, cx - 0.1, cy, t, -0.35, blend(P('reach', aR=(2.6, 0.2, 0.2), aL=(2.3, 0.3, 0.3), head=(-0.4, 0)),
                                                       P('stand', aL=(0.9, 0.5, 0.6), aR=(0.9, 0.5, 0.6), head=(0.55, 0.2), lean=0.25), drop),
           sink=1.5, rough=0.9, face='tired' if drop < 0.6 else 'closed')
    jr = S['james'].root.location
    S['sling'].location = (jr[0], jr[1], jr[2] + 1.85)
    S['sling'].rotation_euler = (0.1 * math.sin(t * 2), 0.12, 0)
    spray(S, A(cx, cy - 0.3, h + 0.2), (lt * 1.6) % 1, 16, 3.0, seed=2, size=1.0)
    key(S, 'kw', A(cx + 3, cy - 6, 4), A(cx, cy, h + 1), 2600)
    key(S, 'kc', A(cx - 4, cy - 4, 2), A(cx, cy, h + 1), 900)
    cam(S, A(cx + lerp(1.9, 1.3, k), cy - lerp(5.4, 4.6, k), h + 1.9), A(cx + 0.25, cy, h + 0.95), 40, 0.04 * math.sin(t * 6))


def bed(S, A, t, face):
    S['james'].place(A(0, 1.9, 0.1), 0.0)
    S['james'].apply(P('stand', lL=(1.5, 0.05), lR=(1.5, 0.05), aL=(0.5, 0.2, 0.5), aR=(0.5, 0.2, 0.5), lean=-0.32, head=(0.25, 0.0)))
    S['face']['james'] = face
    S['blanket'].location = A(0, 0.55, 1.2)
    S['blanket'].scale = (2.5, 2.9, 0.62)
    for i, b in enumerate(S['beat']):
        u = (t * 1.3 - i * 0.1) % 1
        b.location.z = 2.6 + (0.3 if u < 0.08 else -0.14 if u < 0.16 else 0.0)


def ward(S, k, t, lt):
    A = show(S, 'ward')
    sky(S, '0A0C10')
    bed(S, A, t, 'tired' if lt < 1.2 else 'happy')
    S['james'].head.rotation_euler = (0.2, 0, 0.6 * ease((lt - 1.0) / 0.5))
    tip = math.sin(PI * ease((lt - 0.4) / 1.2)) if lt > 0.4 else 0
    S['rook'].place(A(2.7, 0.9, 0), -0.75)
    S['rook'].apply(blend(P('stand', head=(0.1, -0.2)), P('hat', head=(0.2, -0.2)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(-2.2, -1.2, k), lerp(-6.6, -5.8, k), 2.9), A(0.9, 1.4, 2.2), 34)


def ward_cu(S, k, t, lt):
    A = show(S, 'ward')
    sky(S, '0A0C10')
    bed(S, A, t, 'closed' if (lt % 2.4) < 1.0 else 'tired')
    S['james'].head.rotation_euler = (0.3 + 0.04 * math.sin(t * 1.6), 0, -0.3)
    cam(S, A(lerp(-2.6, -1.9, k), lerp(-1.6, -1.2, k), 2.9), A(-0.4, 2.2, 2.35), 42)


def ten_feet(S, k, t, lt):
    A = deck_day(S)
    S['rook'].place(A(0.4, 4.7, 0), 0.25)
    b = 0.5 + 0.5 * math.sin(lt * 6)
    S['rook'].apply(P('stand', aR=(1.4, 0.2, 1.2 + 0.9 * b, 0.2), aL=(0.3, 0.3, 0.9), head=(0.0, 0.1)))
    S['face']['rook'] = S['prm'].get('expr', 'smirk')
    S['james'].place(A(0.2, 0.3, 0), PI + 0.2)
    S['james'].apply(P('cross', head=(0.0, 0.35 * math.sin(lt * 5.5)), lean=-0.08))
    S['face']['james'] = 'happy'
    cam(S, A(lerp(8.6, 7.6, k), lerp(1.0, 1.6, k), 2.4), A(0, 2.7, 1.9), 30)


HOST |= {'family_board', 'rook_bar', 'rook_sun', 'deck_search', 'search_air', 'ops_room', 'rook_chart', 'ward', 'ten_feet'}
SHOTS3D.update({f.__name__: f for f in (
    family_board, james_deck, bar_two, bar_leave, bar_empty, rook_bar, ship_night, swim_night, jelly, sunrise, rook_sun, deck_search,
    hall_search, ship_turn, search_air, search_boat, search_plane, ops_room, rook_chart, sling, ward, ward_cu, ten_feet)})


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: James alone in the night swell, the lit ship sailing away, Rook in his ring, shocked."""
    A = gulf(S, 1.0, 'night', 0.9)
    S['liner'].location, S['liner'].rotation_euler, S['liner'].scale = (-12, 88, 0.2), (0, 0, PI / 2 + 0.4), (1.0, 1.0, 1.0)
    h = afloat(S, 'james', A, -0.3, 0.6, 1.0, 0.2, P('up', aL=(2.7, -0.5, 0.2), aR=(2.7, -0.3, 0.2), head=(-0.15, 0.1)), sink=1.45, rough=0.9, face='shock')
    spray(S, A(-0.3, -0.5, h - 0.1), 0.3, 14, 2.2, size=1.2, up=0.5)
    rook_float(S, A, -2.3, -0.2, 1.0, 0.35, P('up', aL=(2.5, -0.6, 0.5), aR=(2.5, -0.6, 0.5), head=(0.0, 0.3)), 'shocked', 0.9)
    key(S, 'kw', A(-5, -7, 3.5), A(-2, 0, 1.5), 1000)
    key(S, 'kc', A(3, -5, 4), A(-0.3, 0.6, 1.2), 1500)
    cam(S, A(0.6, -7.0, 1.7), A(0.6, 0.5, 2.5), 32)


STILLS['thumb'] = photo_thumb
