"""Case 003 in 3D - Chris Lemons, DSV Bibby Topaz, North Sea, 18 September 2012. Sets built for this story only:
the ship's moonpool bay, the seabed with the yellow well structure, the grey North Sea with the dive support vessel,
the dive control room, and the inside of the diving bell."""
import math

import bpy
import numpy as np
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(seabed=(0, 0, 0), bay=(500, 0, 0), control=(1000, 0, 0), inside=(1500, 0, 0), north=(0, 700, 0))
FAR = (0, 0, -800)
HOST = {'rook_bay', 'rook_helmet', 'bell_down', 'work', 'rook_cable', 'cable_tight', 'rook_flinch', 'rook_sit', 'rov_in', 'rook_low',
        'rook_point', 'haul_up', 'breaths', 'rook_caw', 'sits_up', 'rook_dry', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
LEM = dict(top='2E5FA8', pants='24477E', hand='15181F', boot='15181F')
YUA = dict(top='B8442E', pants='8A3020', hand='15181F', boot='15181F')
DUNC = dict(top='E8701E', pants='3A4048', hand='D8A07A', boot='20242B')
SUP = dict(top='34506A', pants='20242B', hand='C68A5E', boot='15181F')
YEL, STEEL, BRASS = 'E8B020', '4A525E', 'FFC233'
SNAG = (3.0, 1.0, 2.75)          # the corner of the structure where the umbilical catches
TOP = 2.6                        # height of the structure's roof grating


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


def spot(loc, energy, col, aim, parent, angle=0.8):
    bpy.ops.object.light_add(type='SPOT', location=loc)
    l = bpy.context.object
    l.data.energy, l.data.color = energy, K.hexc(col)[:3]
    l.data.spot_size, l.data.spot_blend = angle, 0.5
    con = l.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = aim, 'TRACK_NEGATIVE_Z', 'UP_Y'
    l.parent = parent
    return l


# ---------------------------------------------------------------- cast heads and props
def sat_head(col, lampcol='FFF2C0'):
    """Saturation diver's helmet: shell, dark faceplate with two eye glints, regulator, handle and a hat lamp."""
    def fn(head):
        add('ico_sphere', col, (0, 0, 0.03), scale=(1, 1.05, 1), radius=0.37, subdivisions=2, parent=head, rough=0.45)
        add('cube', '0A1018', (0, -0.3, 0.05), scale=(0.44, 0.16, 0.25), size=1, parent=head, rough=0.2)
        add('cube', 'C8CCD4', (0, -0.31, 0.19), scale=(0.48, 0.15, 0.04), size=1, parent=head, rough=0.4)
        eyes = [add('cube', 'FFFFFF', (s * 0.1, -0.385, 0.06), scale=(0.08, 0.02, 0.085), size=1, parent=head, emit=1.2) for s in (-1, 1)]
        add('cylinder', 'C8CCD4', (0, -0.36, -0.2), rot=(PI / 2, 0, 0), radius=0.12, depth=0.2, vertices=8, parent=head, rough=0.4)
        add('cylinder', '15181F', (0.3, -0.12, -0.16), rot=(0, PI / 2, 0), radius=0.09, depth=0.2, vertices=6, parent=head)
        add('cube', '15181F', (0, 0.02, 0.42), scale=(0.08, 0.4, 0.07), size=1, parent=head)
        add('cylinder', '20242B', (0, 0, -0.34), radius=0.33, depth=0.14, vertices=10, parent=head)
        glow = add('cube', lampcol, (-0.26, -0.22, 0.3), scale=(0.13, 0.1, 0.11), size=1, parent=head, emit=14)
        aim = empty((0, -7, -0.6), head)
        lamp = spot((-0.26, -0.3, 0.3), 0, lampcol, aim, head, 0.95)
        return dict(eyes=eyes, lamp=lamp, glow=glow, eye0=0.085)
    return fn


def person_head(skin, hair):
    base = K.human_head(skin, hair)

    def fn(head):
        d = base(head)
        d['eye0'] = 0.075
        return d
    return fn


def bottles(rig):
    """Twin bail-out cylinders on a diver's back."""
    for s in (-1, 1):
        add('cylinder', 'D8D8D0', (s * 0.15, 0.36, 0.58), radius=0.12, depth=0.74, vertices=8, parent=rig.body, rough=0.4)
        add('cylinder', BRASS, (s * 0.15, 0.36, 0.98), radius=0.05, depth=0.1, vertices=6, parent=rig.body, rough=0.3)
    add('cube', '15181F', (0, 0.3, 0.6), scale=(0.62, 0.08, 0.1), size=1, parent=rig.body)


def make_bell(r, lamp=True):
    """Diving bell: a pale sphere in a yellow cage, orange band, bottom trunk and a floodlit stage."""
    add('ico_sphere', 'E4E0D2', (0, 0, 0), radius=1.7, subdivisions=2, parent=r, rough=0.5)
    add('cylinder', 'FF7A1A', (0, 0, 0.1), radius=1.74, depth=0.36, vertices=14, parent=r, rough=0.6)
    add('cylinder', 'C8C4B4', (0, 0, -1.85), radius=0.82, depth=1.0, vertices=10, parent=r)
    add('cylinder', '06181C', (0, 0, -2.37), radius=0.7, depth=0.04, vertices=10, parent=r, emit=0.4)
    for i in range(4):
        a = i * PI / 2 + PI / 4
        add('cylinder', YEL, (math.cos(a) * 2.1, math.sin(a) * 2.1, -0.8), radius=0.09, depth=5.0, vertices=6, parent=r)
        add('cylinder', '0A1018', (math.cos(a + PI / 4) * 1.66, math.sin(a + PI / 4) * 1.66, 0.75), rot=(PI / 2, 0, a + PI / 4 + PI / 2),
            radius=0.3, depth=0.1, vertices=10, parent=r, rough=0.2)
    for z in (-3.3, -1.2, 1.7):
        add('torus', YEL, (0, 0, z), major_radius=2.1, minor_radius=0.09, major_segments=14, minor_segments=5, parent=r)
    add('cylinder', '2A3038', (0, 0, -3.36), radius=2.1, depth=0.08, vertices=14, parent=r)
    add('cylinder', '8A90A0', (0, 0, 21.6), radius=0.07, depth=40, vertices=5, parent=r)
    add('cylinder', YEL, (0, 0, 1.75), radius=0.5, depth=0.3, vertices=8, parent=r)
    lamps = []
    for i in range(4):
        a = i * PI / 2
        lamps.append(add('ico_sphere', 'FFF2C0', (math.cos(a) * 2.1, math.sin(a) * 2.1, -1.2), radius=0.2, subdivisions=1, parent=r, emit=22))
    out = dict(lamps=lamps)
    if lamp:
        out['lite'] = light((0, 0, -2.9), 2500, 'FFE8B0', kind='POINT', parent=r)
    return out


def make_rov(r):
    """Work-class ROV, front toward -Y: yellow float block, black frame, two lamps, a camera eye and a claw."""
    add('cube', 'F2C230', (0, 0, 0.45), scale=(1.5, 1.9, 0.5), size=1, parent=r, rough=0.5)
    add('cube', '15181F', (0, 0, -0.1), scale=(1.4, 1.8, 0.6), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '20242B', (sx * 0.78, 0, -0.45), scale=(0.1, 2.0, 0.12), size=1, parent=r)
        add('cylinder', '2A3038', (sx * 0.62, 0.7, 0.75), radius=0.2, depth=0.1, vertices=8, parent=r)
        add('cylinder', 'FFF6D8', (sx * 0.45, -0.97, 0.12), rot=(PI / 2, 0, 0), radius=0.17, depth=0.08, vertices=8, parent=r, emit=26)
    add('cylinder', '0A1018', (0, -0.98, -0.12), rot=(PI / 2, 0, 0), radius=0.2, depth=0.12, vertices=10, parent=r, rough=0.15)
    add('cylinder', 'FF4030', (0, -1.0, -0.12), rot=(PI / 2, 0, 0), radius=0.06, depth=0.14, vertices=6, parent=r, emit=10)
    add('cylinder', '8A90A0', (0.5, -1.2, -0.42), rot=(PI / 2 - 0.3, 0, 0), radius=0.05, depth=0.7, vertices=5, parent=r)
    add('cube', '8A90A0', (0.5, -1.56, -0.56), scale=(0.2, 0.12, 0.06), size=1, parent=r)
    add('cube', 'FF7A1A', (0, 0, 0.71), scale=(1.5, 0.3, 0.03), size=1, parent=r, emit=0.5)
    aim = empty((0, -8, -1.5), r)
    return dict(rov=r, rovl=spot((0, -1.1, 0.5), 0, 'EAF6FF', aim, r, 0.9), rovaim=aim)


def make_dsv(r):
    """Dive support vessel, bow toward +X, about 48 long: red hull, white house forward, helideck over the bow, crane and bell hangar aft."""
    add('cube', 'B8322A', (-2, 0, 1.6), scale=(40, 9.4, 4.6), size=1, parent=r)
    s = 9.4 / math.sqrt(2)
    add('cube', 'B8322A', (18, 0, 1.6), rot=(0, 0, PI / 4), scale=(s, s, 4.6), size=1, parent=r)
    add('cube', '15181F', (-2, 0, -0.2), scale=(40.2, 9.5, 1.2), size=1, parent=r)
    add('cube', 'E8E4D8', (-2, 0, 3.96), scale=(40.1, 9.5, 0.14), size=1, parent=r)
    add('cube', '3A6A52', (-9, 0, 3.98), scale=(22, 8.6, 0.1), size=1, parent=r)
    for i, (cx, ln, wd, z, hg) in enumerate(((11, 12, 8.6, 5.5, 3.0), (11.5, 10, 8.0, 8.1, 2.2), (12.5, 7, 7.0, 10.1, 1.8))):
        add('cube', 'ECE8DC', (cx, 0, z), scale=(ln, wd, hg), size=1, parent=r)
        for sy in (-1, 1):
            add('cube', 'FFE7A8', (cx, sy * (wd / 2 + 0.02), z + 0.2), scale=(ln * 0.8, 0.05, hg * 0.3), size=1, parent=r, emit=5)
        add('cube', 'FFE7A8', (cx + ln / 2 + 0.02, 0, z + 0.2), scale=(0.05, wd * 0.8, hg * 0.3), size=1, parent=r, emit=5)
    add('cylinder', '2E6A4A', (21.5, 0, 10.4), radius=6.2, depth=0.3, vertices=8, parent=r)
    add('torus', 'F2C230', (21.5, 0, 10.58), major_radius=3.6, minor_radius=0.22, major_segments=16, minor_segments=4, parent=r, emit=0.6)
    for sy in (-1, 1):
        add('cylinder', 'C8C4B8', (19.5, sy * 2.6, 7.4), rot=(0, -0.5, 0), radius=0.18, depth=7, vertices=5, parent=r)
        add('cylinder', 'FF7A1A', (5.5, sy * 2.2, 12.3), radius=0.9, depth=2.6, vertices=8, parent=r)
        add('cylinder', '15181F', (5.5, sy * 2.2, 13.7), radius=0.94, depth=0.4, vertices=8, parent=r)
    add('cylinder', 'C8C4B8', (12, 0, 13.4), radius=0.14, depth=5.0, vertices=5, parent=r)
    add('ico_sphere', 'FFFFFF', (12, 0, 16.0), radius=0.3, subdivisions=1, parent=r, emit=18)
    add('cube', '8E94A6', (-2.5, 0, 6.2), scale=(8, 7.4, 4.4), size=1, parent=r)
    add('cube', 'FFB060', (-6.52, 0, 5.6), scale=(0.06, 3.6, 2.6), size=1, parent=r, emit=3)
    add('cylinder', YEL, (-11, 3.0, 6.5), radius=0.55, depth=5.0, vertices=8, parent=r)
    add('cube', YEL, (-15.2, 3.0, 10.4), rot=(0, -0.42, 0), scale=(10.5, 0.6, 0.6), size=1, parent=r)
    add('cylinder', '15181F', (-19.9, 3.0, 9.3), radius=0.03, depth=6.0, vertices=4, parent=r)
    for sy in (-1, 1):
        add('cube', YEL, (-20, sy * 3.0, 6.7), rot=(0, 0.3, 0), scale=(0.5, 0.5, 6.0), size=1, parent=r)
    add('cube', YEL, (-20.9, 0, 9.5), scale=(0.5, 6.5, 0.5), size=1, parent=r)
    add('ico_sphere', '3DDC84', (15, -4.6, 9.6), radius=0.22, subdivisions=1, parent=r, emit=16)
    add('ico_sphere', 'FF4030', (15, 4.6, 9.6), radius=0.22, subdivisions=1, parent=r, emit=16)
    return r


# ---------------------------------------------------------------- sets
def set_seabed(r):
    add('plane', '3E4A40', (0, 0, 0), size=420, parent=r, rough=1.0)
    R = np.random.RandomState(7)
    for i in range(26):
        x, y = R.uniform(-22, 22), R.uniform(-9, 26)
        if -5 < x < 5 and -3 < y < 7:
            continue
        sc = R.uniform(0.3, 1.1)
        add('ico_sphere', ('2E3A34', '465248', '37433B')[i % 3], (x, y, sc * 0.2), rot=(R.uniform(0, 3), 0, R.uniform(0, 3)),
            scale=(sc * 1.5, sc, sc * 0.6), radius=1.0, subdivisions=1, parent=r)
    # the well structure: a yellow protection frame over valves and pipework, with a grating roof
    for sx in (-1, 1):
        for y in (1, 5):
            add('cube', YEL, (sx * 3, y, TOP / 2), scale=(0.3, 0.3, TOP), size=1, parent=r)
            add('cube', YEL, (sx * 3.5, y, 0.9), rot=(0, sx * -0.5, 0), scale=(0.2, 0.2, 2.2), size=1, parent=r)
        add('cube', YEL, (sx * 3, 3, TOP), scale=(0.3, 4.3, 0.3), size=1, parent=r)
        add('cube', YEL, (sx * 3, 3, 1.2), rot=(0.55, 0, 0), scale=(0.16, 4.6, 0.16), size=1, parent=r)
    for y in (1, 5):
        add('cube', YEL, (0, y, TOP), scale=(6.3, 0.3, 0.3), size=1, parent=r)
        add('cube', YEL, (0, y, 0.15), scale=(6.3, 0.3, 0.3), size=1, parent=r)
    add('cube', '2A323A', (0, 3, TOP - 0.02), scale=(5.9, 3.9, 0.1), size=1, parent=r)
    for i in range(-5, 6):
        add('cube', '48525E', (i * 0.52, 3, TOP + 0.04), scale=(0.07, 3.9, 0.03), size=1, parent=r)
    add('cube', '2A3038', (3.28, 0.78, TOP + 0.05), rot=(0, 0, PI / 4), scale=(0.75, 0.14, 0.2), size=1, parent=r)      # the lug that catches the line
    add('cube', '15181F', (3.55, 0.52, TOP + 0.05), rot=(0, 0, PI / 4), scale=(0.2, 0.3, 0.34), size=1, parent=r)
    add('cylinder', STEEL, (0, 3.2, 1.0), radius=0.7, depth=2.0, vertices=10, parent=r)
    add('cylinder', '6A7482', (0, 3.2, 2.05), radius=0.85, depth=0.14, vertices=10, parent=r)
    add('cylinder', STEEL, (0, 2.0, 1.15), rot=(0, PI / 2, 0), radius=0.24, depth=5.6, vertices=8, parent=r)
    add('cylinder', '6A7482', (-1.9, 3.6, 0.7), rot=(PI / 2, 0, 0), radius=0.3, depth=2.4, vertices=8, parent=r)
    add('cylinder', STEEL, (1.9, 3.4, 0.8), radius=0.28, depth=1.6, vertices=8, parent=r)
    add('cube', '343C48', (0, 1.06, 1.25), scale=(5.4, 0.1, 1.5), size=1, parent=r)
    wheels = []
    for i, x in enumerate((-1.9, -0.6, 0.7, 2.0)):
        w = empty((x, 0.94, 1.3 + 0.25 * (i % 2)), r)
        add('torus', 'FF7A1A', (0, 0, 0), rot=(PI / 2, 0, 0), major_radius=0.3, minor_radius=0.05, major_segments=10, minor_segments=4, parent=w, emit=0.25)
        for a in (0, PI / 2):
            add('cube', 'FF7A1A', (0, 0, 0), rot=(0, a, 0), scale=(0.56, 0.05, 0.06), size=1, parent=w)
        add('cylinder', 'C8CCD4', (0, 0.06, 0), rot=(PI / 2, 0, 0), radius=0.06, depth=0.2, vertices=6, parent=w)
        add('cylinder', '3DDC84' if i % 2 else 'FF4030', (x + 0.45, 0.99, 1.75), rot=(PI / 2, 0, 0), radius=0.07, depth=0.05, vertices=6, parent=r, emit=5)
        wheels.append(w)
    add('cylinder', '505A54', (-9, 8, 0.35), rot=(0, PI / 2, 0.5), radius=0.35, depth=26, vertices=8, parent=r)
    add('cylinder', '505A54', (10, 9, 0.3), rot=(0, PI / 2, -0.35), radius=0.3, depth=22, vertices=8, parent=r)
    aim = empty((0, 3, 1.6), r)
    keyl = light((3, -5, 10), 9000, '8FE8DC', 9.0, aim, parent=r)
    fill = light((-7, -8, 2.5), 1400, '2E8A9A', 6.0, aim, parent=r)
    rim = light((7, 9, 5), 2600, 'FF8A30', 3.0, aim, parent=r)
    bell = empty((0, 0, -60), r)
    b = make_bell(bell)
    rov = make_rov(empty((0, 0, -90), r))
    spark = add('ico_sphere', 'FFF6D0', (0, 0, -40), radius=0.3, subdivisions=1, parent=r, emit=40)
    return dict(wheels=wheels, sb_key=keyl, sb_fill=fill, sb_rim=rim, xbell=bell, xlite=b['lite'], spark=spark, **rov)


def set_bay(r):
    add('cube', '3A424C', (0, 1, -0.15), scale=(24, 16, 0.3), size=1, parent=r)
    for i in range(-11, 12):
        add('cube', '2A3038', (i * 1.0, 1, 0.005), scale=(0.05, 16, 0.02), size=1, parent=r)
    add('cube', '262C36', (0, 7.2, 5.5), scale=(24, 0.4, 11), size=1, parent=r)
    add('cube', '2E3540', (-9.5, 1, 5.5), scale=(0.4, 16, 11), size=1, parent=r)
    for z, col, rad in ((5.6, 'FF7A1A', 0.16), (6.1, 'C8CCD4', 0.11), (6.5, YEL, 0.13)):
        add('cylinder', col, (0, 6.9, z), rot=(0, PI / 2, 0), radius=rad, depth=24, vertices=6, parent=r)
    for x in (-6, -1.5, 8.5):
        add('cube', 'FFE7B8', (x, 6.96, 8.0), scale=(1.6, 0.08, 0.3), size=1, parent=r, emit=5)
        light((x, 6.2, 7.6), 160, 'FFE2B8', kind='POINT', parent=r)
    # the moonpool: a square of dark water in the deck with a hazard kerb, the bell hanging over it
    px, py = 3.8, 3.4
    add('plane', '0E5A60', (px, py, 0.02), size=3.6, parent=r, rough=0.15, emit=0.9)
    for i in range(8):
        for sx, sy, ln in ((0, -1, 0), (0, 1, 0), (-1, 0, 1), (1, 0, 1)):
            off = -1.75 + i * 0.5
            loc = (px + off, py + sy * 1.9, 0.12) if not ln else (px + sx * 1.9, py + off, 0.12)
            add('cube', YEL if i % 2 else '15181F', loc, scale=(0.5, 0.22, 0.24) if not ln else (0.22, 0.5, 0.24), size=1, parent=r)
    make_bell(empty((px, py, 4.9), r), lamp=False)
    add('cube', YEL, (px, py, 9.4), scale=(9.6, 0.6, 0.6), size=1, parent=r)
    for x in (px - 4.6, px + 4.6):
        add('cube', YEL, (x, py, 4.7), scale=(0.45, 0.45, 9.4), size=1, parent=r)
    add('cube', '2A3038', (px, py, 9.0), scale=(1.2, 1.0, 0.5), size=1, parent=r)
    light((px, py, 0.9), 500, '3ED8D0', kind='POINT', parent=r)
    # gas quads, an umbilical reel and a tool chest
    add('cube', '20242B', (-6.0, 5.4, 1.5), scale=(3.4, 1.5, 0.1), size=1, parent=r)
    for i in range(6):
        add('cylinder', ('2E8A5A', 'D8D8D0')[i % 2], (-7.3 + i * 0.52, 5.4, 1.45), radius=0.23, depth=2.9, vertices=8, parent=r)
        add('cylinder', BRASS, (-7.3 + i * 0.52, 5.4, 2.98), radius=0.08, depth=0.16, vertices=6, parent=r, rough=0.3)
    for x in (-7.7, -4.3):
        add('cube', '20242B', (x, 5.4, 1.6), scale=(0.1, 1.5, 3.2), size=1, parent=r)
    add('cylinder', YEL, (-2.6, 5.2, 1.1), rot=(0, PI / 2, 0), radius=0.9, depth=1.3, vertices=12, parent=r)
    for sx in (-1, 1):
        add('cylinder', '2A3038', (-2.6 + sx * 0.7, 5.2, 1.1), rot=(0, PI / 2, 0), radius=1.15, depth=0.1, vertices=12, parent=r)
    add('cube', '2A3038', (-2.6, 5.2, 0.1), scale=(1.9, 1.4, 0.2), size=1, parent=r)
    add('cube', 'B8322A', (-4.4, 2.9, 0.45), rot=(0, 0, 0.25), scale=(1.3, 0.8, 0.9), size=1, parent=r)
    aim = empty((0, 1, 1.9), r)
    light((4.5, -6, 5), 1300, 'FFE2B8', 3.0, aim, parent=r)
    light((-6, 4.5, 5.6), 2100, 'FF7A1A', 1.6, aim, parent=r)
    light((-5.5, -5, 2), 260, '5E8FD0', 4.0, aim, parent=r)
    pick = empty((0, 0, -5))
    add('torus', BRASS, (0, 0, 0), major_radius=0.17, minor_radius=0.06, major_segments=10, minor_segments=5, parent=pick, rough=0.25, emit=1.2)
    add('cylinder', BRASS, (0, 0, 0), radius=0.1, depth=0.2, vertices=6, parent=pick, rough=0.25, emit=1.0)
    return dict(pick=pick)


def set_control(r):
    add('cube', '20242B', (0, 0, -0.1), scale=(9.4, 9.4, 0.2), size=1, parent=r)
    add('cube', '1A1E28', (0, 0, 4.5), scale=(9.4, 9.4, 0.2), size=1, parent=r)
    add('cube', '1A2030', (0, 4.6, 2.2), scale=(9.4, 0.2, 4.6), size=1, parent=r)
    add('cube', '252C3A', (0, -4.6, 2.2), scale=(9.4, 0.2, 4.6), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '202838', (sx * 4.6, 0, 2.2), scale=(0.2, 9.4, 4.6), size=1, parent=r)
    add('cube', '2A3038', (0, 3.2, 0.55), scale=(7.4, 1.5, 1.1), size=1, parent=r)
    add('cube', '343C48', (0, 2.9, 1.22), rot=(0.4, 0, 0), scale=(7.4, 1.0, 0.12), size=1, parent=r)
    cols = ('3DDC84', 'FFB060', '5EC8F0', 'FF4030', 'FFD866')
    for i in range(16):
        add('cube', cols[(i * 3) % 5], (-3.2 + i * 0.43, 2.75 + 0.2 * (i % 2), 1.27 + 0.085 * (i % 2)), rot=(0.4, 0, 0),
            scale=(0.16, 0.12, 0.05), size=1, parent=r, emit=4)
    screens = [(0.0, 2.95, 2.5, 1.45, '1ED8C0', 2.4), (-2.45, 2.75, 1.5, 0.95, '5EC8F0', 2.2), (2.45, 2.75, 1.5, 0.95, '3DDC84', 2.0),
               (-3.85, 2.3, 0.9, 0.6, 'FFB060', 2.2), (3.85, 2.3, 0.9, 0.6, 'FFB060', 2.2)]
    for x, z, w_, h_, col, e in screens:
        add('cube', '0A0E14', (x, 4.44, z), scale=(w_ + 0.16, 0.08, h_ + 0.16), size=1, parent=r)
        add('cube', col, (x, 4.39, z), scale=(w_, 0.04, h_), size=1, parent=r, emit=e)
    for i in range(5):                                   # a sonar-style sweep of dark bars on the main screen
        add('cube', '0A3A38', (-1.0 + i * 0.5, 4.36, 2.95), scale=(0.04, 0.02, 1.4), size=1, parent=r)
    add('cube', 'D8CDB8', (-2.2, -4.48, 2.5), scale=(2.2, 0.05, 1.4), size=1, parent=r)
    add('cube', '3A4654', (2.4, -4.48, 1.7), scale=(1.5, 0.06, 3.3), size=1, parent=r)
    add('cylinder', 'F4F0E6', (0.4, -4.47, 3.3), rot=(PI / 2, 0, 0), radius=0.4, depth=0.05, vertices=12, parent=r, emit=0.4)
    add('cube', '2A3038', (-4.2, -1.5, 1.4), scale=(0.6, 2.4, 2.8), size=1, parent=r)
    add('cube', 'FF7A1A', (-3.88, -1.5, 2.2), scale=(0.04, 2.0, 0.14), size=1, parent=r, emit=1.5)
    beacon = add('cylinder', 'FF4030', (3.3, 4.2, 3.95), radius=0.2, depth=0.3, vertices=8, parent=r, emit=30)
    red = light((3.0, 3.4, 3.7), 0, 'FF3020', kind='POINT', parent=r)
    aim = empty((0, 1.4, 2.2), r)
    glow = light((0, 4.0, 2.7), 600, '6FE8E0', 3.0, aim, parent=r)
    light((0, -1, 4.2), 60, 'FFE2B8', kind='POINT', parent=r)
    back = light((-3, -3.6, 3.2), 260, 'FF8A40', 2.5, aim, parent=r)
    return dict(beacon=beacon, c_red=red, c_glow=glow, c_back=back)


def set_inside(r):
    """Inside the diving bell (opened up a little for the camera): ring of cream panels, hatch in the floor, pipes and gauges."""
    add('cylinder', '5A6470', (0, 0, -0.06), radius=3.3, depth=0.12, vertices=16, parent=r)
    add('cylinder', 'B4AE9C', (0, 0, 3.56), radius=3.3, depth=0.12, vertices=16, parent=r)
    n = 14
    for i in range(n):
        a = i * 2 * PI / n
        add('cube', ('D8D2C0', 'CCC5B0')[i % 2], (math.cos(a) * 3.1, math.sin(a) * 3.1, 1.75), rot=(0, 0, a + PI / 2), scale=(1.45, 0.14, 3.5), size=1, parent=r)
        if i % 2 == 0 and 1 <= i <= 7:
            add('cylinder', 'F4F0E6', (math.cos(a) * 2.98, math.sin(a) * 2.98, 2.35), rot=(PI / 2, 0, a + PI / 2), radius=0.2, depth=0.06, vertices=10,
                parent=r, emit=0.5)
            add('cylinder', 'FF4030', (math.cos(a + 0.15) * 2.98, math.sin(a + 0.15) * 2.98, 1.8), rot=(PI / 2, 0, a + PI / 2), radius=0.1, depth=0.1,
                vertices=6, parent=r)
    add('torus', 'FF7A1A', (0, 0, 2.9), major_radius=2.92, minor_radius=0.07, major_segments=20, minor_segments=5, parent=r)
    add('torus', 'C8CCD4', (0, 0, 0.5), major_radius=2.95, minor_radius=0.05, major_segments=20, minor_segments=5, parent=r)
    hx, hy = -1.3, -0.5
    add('cylinder', '06262A', (hx, hy, 0.012), radius=0.78, depth=0.02, vertices=14, parent=r, emit=0.5)
    add('torus', YEL, (hx, hy, 0.05), major_radius=0.82, minor_radius=0.08, major_segments=14, minor_segments=5, parent=r)
    add('cylinder', YEL, (hx - 1.0, hy - 0.4, 0.75), rot=(0, 0.5, 0.4), radius=0.8, depth=0.08, vertices=14, parent=r)      # the open hatch lid
    add('ico_sphere', 'FFF2D0', (0, 0, 3.35), radius=0.24, subdivisions=1, parent=r, emit=18)
    light((0, 0, 3.0), 330, 'FFE8C0', kind='POINT', parent=r)
    light((hx, hy, 0.5), 160, '3ED8D0', kind='POINT', parent=r)
    add('cube', '2A3038', (0.2, 2.95, 1.2), scale=(1.8, 0.2, 0.9), size=1, parent=r)
    for i in range(4):
        add('cube', ('3DDC84', 'FFB060')[i % 2], (-0.4 + i * 0.4, 2.83, 1.3), scale=(0.2, 0.04, 0.12), size=1, parent=r, emit=4)
    for z in (0.9, 1.6):
        add('cylinder', YEL, (2.6, 1.3, z), rot=(0, 0, 0), radius=0.22, depth=0.6, vertices=8, parent=r)
    helm = empty((0, 0, -50), r)
    add('ico_sphere', 'F2C230', (0, 0, 0.37), scale=(1, 1.05, 1), radius=0.37, subdivisions=2, parent=helm, rough=0.45)
    add('cube', '0A1018', (0, -0.3, 0.39), scale=(0.44, 0.16, 0.25), size=1, parent=helm, rough=0.2)
    add('cylinder', '20242B', (0, 0, 0.04), radius=0.33, depth=0.1, vertices=10, parent=helm)
    return dict(ihelm=helm)


def set_north(r):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=60, size=280, location=ORG['north'])
    sea = bpy.context.object
    sea.data.materials.append(K.mat('2A4A48', 0.85))
    co = np.zeros(len(sea.data.vertices) * 3)
    sea.data.vertices.foreach_get('co', co)
    xy = co.reshape(-1, 3)[:, :2].copy()
    ship = make_dsv(empty((0, 0, -70), r))
    mark = add('torus', 'FF7A1A', (0, 0, -30), major_radius=7.0, minor_radius=0.35, major_segments=20, minor_segments=4, parent=r, emit=6)
    add('cube', '9AA6A4', (0, 560, 60), scale=(2600, 1, 120), size=1, parent=r, emit=0.9)
    add('cube', 'C8D2CC', (0, 555, 4), scale=(2600, 1, 9), size=1, parent=r, emit=1.4)
    aim = empty((0, 10, 3), r)
    sun = light((-60, 90, 70), 260000, 'DCE8E4', 40.0, aim, parent=r)
    light((30, -60, 20), 30000, '8AA0A8', 30.0, aim, parent=r)
    return dict(sea=sea, xy=xy, ship=ship, mark=mark, n_sun=sun)


# ---------------------------------------------------------------- build / reset / finish
PEOPLE = ('lem', 'yua', 'chris', 'dunc', 'sup')


def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('seabed', set_seabed), ('bay', set_bay), ('control', set_control), ('inside', set_inside), ('north', set_north)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['lem'] = K.Rig(LEM, sat_head('F2C230'))
    S['yua'] = K.Rig(YUA, sat_head('ECECE4', 'DFF2FF'))
    S['chris'] = K.Rig(LEM, person_head('D9B49C', '6A4A2E'))
    S['dunc'] = K.Rig(DUNC, person_head('D8A07A', '8A8A8A'))
    S['sup'] = K.Rig(SUP, person_head('C68A5E', '2A2420'))
    for who in ('lem', 'yua', 'chris'):
        bottles(S[who])
    add('cylinder', '15181F', (0, 0, -0.3), radius=0.2, depth=0.12, vertices=8, parent=S['chris'].head)          # neck dam
    add('cube', '15181F', (0, 0.02, 0.33), scale=(0.5, 0.42, 0.1), size=1, parent=S['sup'].head)                  # headset band
    add('cube', '15181F', (0.3, -0.05, 0.02), scale=(0.08, 0.2, 0.26), size=1, parent=S['sup'].head)
    S['bub'] = [add('ico_sphere', 'D8F6FF', FAR, radius=0.07, subdivisions=1, emit=1.3) for _ in range(44)]
    S['ropes'] = []
    for col in ('FF5A1E', 'FF5A1E', 'B8BCC4'):
        segs = []
        for _ in range(14):
            o = add('cylinder', col, FAR, radius=0.085, depth=1.0, vertices=5, emit=0.25)
            o.rotation_mode = 'QUATERNION'
            segs.append(o)
        S['ropes'].append(segs)
    S['kwa'], S['kca'] = empty(), empty()
    S['kw'] = light((0, 0, 0), 0, 'FFDCB8', 4.0, S['kwa'])
    S['kc'] = light((0, 0, 0), 0, '9ADCE8', 5.0, S['kca'])
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
    """Move one of the two free key lights (kw warm, kc cool) onto this shot's subject."""
    S[which].location, S[which + 'a'].location = pos, look
    S[which].data.energy = energy


def reset(S):
    for who in ('rook',) + PEOPLE:
        S[who].place(FAR)
        S[who].apply(P())
    for who in ('lem', 'yua'):
        S[who].extra['lamp'].data.energy = 0
        S[who].extra['glow'].hide_render = False
    for o in S['bub']:
        o.location, o.scale = FAR, (1, 1, 1)
    for segs in S['ropes']:
        for o in segs:
            o.location = FAR
    S['face'] = dict(rook='calm', lem='calm', yua='calm', chris='calm', dunc='calm', sup='calm')
    S['hat_tip'], S['helm'] = 0.0, False
    for kk in ('kw', 'kc'):
        S[kk].data.energy = 0
    S['xbell'].location = (0, 0, -60)
    S['xlite'].data.energy = 2500
    S['rov'].location, S['rov'].rotation_euler = (0, 0, -90), (0, 0, 0)
    S['rovl'].data.energy = 0
    S['spark'].location = (0, 0, -40)
    for i, w in enumerate(S['wheels']):
        w.rotation_euler = (0, 0, 0)
    S['sb_key'].data.energy, S['sb_fill'].data.energy, S['sb_rim'].data.energy = 9000, 1400, 2600
    S['ship'].location, S['ship'].rotation_euler = (0, 0, -70), (0, 0, 0)
    S['mark'].location = (0, 0, -30)
    S['n_sun'].data.energy = 260000
    S['beacon'].hide_render = True
    S['c_red'].data.energy = 0
    S['c_glow'].data.energy = 600
    S['c_back'].data.energy = 260
    S['ihelm'].location, S['ihelm'].rotation_euler = (0, 0, -50), (0, 0, 0)
    S['pick'].location = FAR
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking, the helmet and beak lip sync after the shot has posed everyone."""
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
    r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.14, sad=0.22).get(e, 0.0) + tip * 0.35, 0.07, 0)
    r['hat'].location.z = 0.27 + (0.11 if e == 'shocked' else 0.0) + tip * 0.1
    for o in r['helmet']:
        o.hide_render = not S['helm']
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e in ('shocked', 'laugh') else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for who in PEOPLE:
        e = S['face'][who]
        x = S[who].extra
        kk = dict(scared=1.3, shock=1.7, calm=1.0, sad=0.6, happy=0.85, closed=0.08, tired=0.45).get(e, 1.0)
        for ey in x['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], x['eye0'] * kk)
        if 'jaw' in x:
            x['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
            x['jaw'].location.z = -0.13 - (0.05 if e == 'shock' else 0.0)


# ---------------------------------------------------------------- helpers: water, lines, bubbles
def deep(S, mode='work'):
    """Shows the seabed. work = lit by the bell's floodlights; dim = the lights are leaving; dark = only helmet lamps."""
    A = show(S, 'seabed')
    if mode == 'work':
        sky(S, '06302F', 1.0)
    elif mode == 'dim':
        sky(S, '041E20', 1.0)
        S['sb_key'].data.energy, S['sb_fill'].data.energy, S['sb_rim'].data.energy = 3500, 900, 900
    else:
        sky(S, '021012', 1.0)
        S['sb_key'].data.energy, S['sb_fill'].data.energy, S['sb_rim'].data.energy = 1100, 500, 0
    return A


def bell_at(S, loc, t, lite=2500):
    S['xbell'].location = (loc[0] + 0.1 * math.sin(t * 0.9), loc[1], loc[2] + 0.12 * math.sin(t * 1.3))
    S['xlite'].data.energy = lite


def lamp(S, who, e):
    S[who].extra['lamp'].data.energy = e


def rope(S, i, p0, p1, sag=0.0, t=0.0, wob=0.0, n=14):
    """Lay line i from p0 to p1 with a hanging belly (sag) and a little current (wob)."""
    pts = []
    for j in range(n + 1):
        u = j / n
        b = 4 * u * (1 - u)
        pts.append(Vector((lerp(p0[0], p1[0], u) + wob * b * math.sin(t * 1.7 + u * 5 + i), lerp(p0[1], p1[1], u) + wob * b * math.cos(t * 1.3 + u * 4),
                           lerp(p0[2], p1[2], u) - sag * b)))
    for j, o in enumerate(S['ropes'][i]):
        if j >= n:
            o.location = FAR
            continue
        a, b = pts[j], pts[j + 1]
        d = b - a
        o.location = (a + b) / 2
        o.rotation_quaternion = d.to_track_quat('Z', 'Y')
        o.scale = (1, 1, d.length * 1.04)


def back_of(S, who, A=None):
    """World position of a diver's back, where the umbilical joins."""
    m = S[who].body.matrix_world
    bpy.context.view_layer.update()
    return tuple(S[who].body.matrix_world @ Vector((0, 0.4, 0.75)))


def bub(S, org, t, n=8, start=0, spread=0.35, height=3.2, speed=1.5, seed=0, size=1.0):
    for i in range(n):
        b = S['bub'][start + i]
        u = (t * speed / height + (i * 0.618 + seed * 0.37) % 1) % 1
        a = i * 2.4 + seed
        rr = spread * (0.3 + 0.7 * ((i * 0.37) % 1)) * (0.4 + u)
        b.location = (org[0] + math.cos(a + t) * rr, org[1] + math.sin(a + t) * rr * 0.7, org[2] + u * height)
        s = size * (0.5 + ((i * 0.73) % 1)) * (0.6 + 0.7 * u)
        b.scale = (s, s, s)


def burst(S, org, k, n=14, start=0, r=1.6, seed=0, size=1.5, up=1.0):
    for i in range(n):
        b = S['bub'][start + i]
        a, e = i * 2.4 + seed, ((i * 0.61) % 1) * 1.4 - 0.2
        d = r * (0.3 + 0.7 * ((i * 0.37) % 1)) * (1 - (1 - k) ** 2)
        b.location = (org[0] + math.cos(a) * math.cos(e) * d, org[1] + math.sin(a) * math.cos(e) * d, org[2] + math.sin(e) * d + 1.6 * k * up)
        s = size * (0.6 + ((i * 0.73) % 1)) * (1 - 0.6 * k)
        b.scale = (s, s, s)


def uw(S, who, loc, yaw, pose, t, pitch=0.0, roll=0.0, face=None, ph=0.0):
    """Place someone under water: a slow bob so nobody stands dead still."""
    S[who].place((loc[0], loc[1], loc[2] + 0.04 * math.sin(t * 1.6 + ph)), yaw, pitch + 0.02 * math.sin(t * 1.2 + ph), roll)
    S[who].apply(pose)
    if face:
        S['face'][who] = face


def rook_uw(S, loc, yaw, pose, expr, t, bubbles=True):
    uw(S, 'rook', loc, yaw, pose, t, ph=1.3)
    S['face']['rook'] = expr
    S['helm'] = True
    if bubbles:
        bub(S, (loc[0], loc[1], loc[2] + 3.3), t, 5, 38, 0.2, 2.6, 1.3, seed=3, size=0.7)


def lying(S, who, A, x0, t, twitch=0.0, face=None, y=3.0, z=TOP + 0.36):
    """Flat on his back on the roof of the structure, head toward +X."""
    S[who].place(A(x0, y, z), -PI / 2, -PI / 2)
    S[who].apply(P('stand', aL=(0.25 + 0.5 * twitch * max(0, math.sin(t * 5.0)), 0.5, 0.9 + 0.5 * twitch * math.sin(t * 5.0)),
                   aR=(0.2, 0.45, 0.7), lL=(0.5, 0.9), lR=(0.25, 0.5), head=(0.1, 0.25)))
    if face:
        S['face'][who] = face


def swell(x, y, t, rough=1.0):
    return rough * (0.9 * math.sin(x * 0.09 + t * 1.1) + 0.5 * math.sin(y * 0.16 + t * 1.6 + x * 0.07) + 0.25 * math.sin((x + y) * 0.33 + t * 2.3))


def north(S, t, rough=1.2, skycol='7C8C8A'):
    A = show(S, 'north')
    xy = S['xy']
    z = rough * (0.9 * np.sin(xy[:, 0] * 0.09 + t * 1.1) + 0.5 * np.sin(xy[:, 1] * 0.16 + t * 1.6 + xy[:, 0] * 0.07)
                 + 0.25 * np.sin((xy[:, 0] + xy[:, 1]) * 0.33 + t * 2.3))
    S['sea'].data.vertices.foreach_set('co', np.column_stack([xy, z]).ravel())
    S['sea'].data.update()
    sky(S, skycol, 1.0)
    return A


def ship_at(S, x, y, yaw, t, rough=1.2, roll=0.05):
    S['ship'].location = (x, y, 0.5 + 0.5 * swell(x, y, t, rough))
    S['ship'].rotation_euler = (roll * math.sin(t * 1.5), 0.035 * math.sin(t * 1.1 + 1), yaw)


# ---------------------------------------------------------------- shots: hook
def snap(S, k, t, lt):
    """The umbilical, bar-tight over the corner of the structure, parts."""
    A = deep(S, 'dim')
    tb = 0.34
    far, low = (17, 6.5, 11), (0.6, -0.9, 1.9)
    if lt < tb:
        j = 0.03 * math.sin(t * 60)
        rope(S, 0, (SNAG[0], SNAG[1], SNAG[2] + j), far, 0.0)
        rope(S, 1, low, (SNAG[0], SNAG[1], SNAG[2] + j), 0.0)
    else:
        e = ease((lt - tb) / 0.5)
        q = min(1.0, (lt - tb) / 0.9)
        rope(S, 0, (lerp(SNAG[0], 9, e), lerp(SNAG[1], 3.4, e), lerp(SNAG[2], 8.5, e) + 0.5 * math.sin(t * 9) * (1 - q)), far, -1.2 * e, t, 0.5)
        rope(S, 1, low, (lerp(SNAG[0], 2.3, e), lerp(SNAG[1], 0.1, e), lerp(SNAG[2], 0.9, e * e)), 0.9 * e, t, 0.2)
        burst(S, A(*SNAG), q, 18, 0, 2.0, seed=2, size=0.75)
        if lt - tb < 0.14:
            S['spark'].location = SNAG
            sc = 1.6 - (lt - tb) * 8
            S['spark'].scale = (sc, sc, sc)
    key(S, 'kc', A(5.5, -3, 5), A(*SNAG), 2600)
    key(S, 'kw', A(1.5, -2.5, 2.0), A(*SNAG), 500 if lt < tb else 1700)
    sh = 0.05 * math.sin(t * 43) if lt > tb else 0
    cam(S, A(lerp(6.6, 6.1, k), lerp(-3.6, -3.0, k), 3.9 + sh), A(3.2, 1.0, 3.3), 40, 0.06 * math.sin(t * 23) * (1 if lt > tb else 0.2))


def fall_back(S, k, t, lt):
    A = deep(S, 'dim')
    e = ease(k)
    uw(S, 'lem', A(lerp(0.9, 0.5, e), lerp(-0.2, -1.9, e), lerp(1.0, 0.5, e)), lerp(0.5, 0.2, e), P('up', aL=(2.2 + 0.4 * math.sin(t * 9), 0.7, 0.4),
       aR=(2.0 - 0.4 * math.sin(t * 9), 0.8, 0.5), lL=(0.9, 0.5), lR=(0.3, 0.9), head=(-0.3, 0.0)), t, pitch=lerp(-0.25, -1.15, e), face='shock')
    lamp(S, 'lem', 5000)
    b = back_of(S, 'lem')
    rope(S, 1, b, (lerp(2.6, 1.8, e), lerp(0.2, -0.6, e), lerp(2.4, 1.5, e) + 0.3 * math.sin(t * 7)), 0.5, t, 0.3)
    burst(S, A(0.8, -0.8, 2.2), min(1, k * 1.2), 12, 0, 1.6, seed=5, size=1.2)
    key(S, 'kc', A(-4, -6, 4), A(0.5, -1, 1.5), 2400)
    key(S, 'kw', A(3.5, -5, 1.2), A(0.5, -1, 1.5), 500)
    cam(S, A(lerp(-2.9, -2.3, k), lerp(-6.2, -5.6, k), 1.1), A(0.5, lerp(-0.4, -1.0, k), lerp(2.0, 1.7, k)), 34, 0.05 * math.sin(t * 17))


def alone_wide(S, k, t, lt):
    A = deep(S, 'dark')
    uw(S, 'lem', A(0.4, -2.0, 0), 0.3 + 0.9 * math.sin(lt * 2.4), P('stand', aL=(0.5, 0.6, 0.6), aR=(0.5, 0.6, 0.6), head=(-0.25, 0.4 * math.sin(lt * 2.4))), t,
       face='scared')
    lamp(S, 'lem', 9000)
    rope(S, 1, back_of(S, 'lem'), A(2.4, -3.2, 0.12), 0.25, t, 0.1, 8)
    bub(S, A(0.4, -2.0, 3.2), t, 6, 0, 0.3, 4.5, 1.6, size=1.4)
    key(S, 'kc', A(-8, -9, 9), A(0, 2, 1.5), 9000)
    key(S, 'kw', A(6, -8, 3), A(0.4, -2, 1.5), 700)
    e = ease(k)
    cam(S, A(lerp(4.5, 7.5, e), lerp(-9, -14.5, e), lerp(3.2, 7.0, e)), A(0.2, 0.6, lerp(2.0, 2.3, e)), lerp(34, 30, e))


def bell_away(S, k, t, lt):
    """Looking up past his reaching arm: the bell and its lights are dragged away."""
    A = deep(S, 'dim')
    e = ease(k)
    bell_at(S, (lerp(-1.5, 7.5, e), lerp(5.5, 9, e), lerp(8.6, 11.5, e)), t, lerp(2500, 900, e))
    rope(S, 0, (lerp(-1.5, 7.5, e), lerp(5.5, 9, e), lerp(5.6, 8.5, e)), (lerp(2.5, 7.0, e), lerp(1.5, 5.5, e), lerp(3.2, 6.5, e)), 0.6, t, 0.4, 8)
    uw(S, 'lem', A(-0.7, -1.3, 0), PI - 0.25, P('reach', aR=(2.75, 0.2, 0.1), aL=(0.4, 0.5, 0.5), head=(-0.5, 0.0)), t, face='scared')
    lamp(S, 'lem', 3000)
    bub(S, A(-0.7, -1.3, 3.2), t, 6, 0, 0.3, 4.0, 1.7, size=1.2)
    key(S, 'kc', A(-3, -5, 3), A(-0.7, -1.3, 2), 1300)
    cam(S, A(0.9, -4.6, 0.6), A(lerp(-0.9, 2.2, e), 2.5, lerp(5.2, 6.4, e)), 26, 0.03 * math.sin(t * 2))


# ---------------------------------------------------------------- shots: Rook takes the case
def rook_bay(S, k, t, lt):
    A = show(S, 'bay')
    sky(S, '05080E')
    S['rook'].place(A(0, 0, 0), 0.3)
    S['rook'].apply(P('cross', head=(0.05, -0.2 + 0.24 * math.sin(t * 4.4) * max(0, 1 - lt / 1.0))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(2.9, 2.1, k), lerp(-6.6, -5.3, k), 1.9), A(0.25, 0, 2.05), 38)


def rook_helmet(S, k, t, lt):
    """Collar up, helmet on, off to the moonpool."""
    A = show(S, 'bay')
    sky(S, '05080E')
    e = ease((lt - 0.45) / 0.9)
    x, y = lerp(0.2, 1.9, e), lerp(0.2, 1.7, e)
    S['rook'].place(A(x, y, 0), math.atan2(1.7, 1.5) + PI / 2 if lt > 0.45 else 0.2)
    pop = math.sin(PI * ease(lt / 0.45)) if lt < 0.45 else 0
    S['rook'].apply(blend(walk(t, 1.9) if lt > 0.45 else P('stand'), P('stand', aL=(0.5, 0.5, 2.3, 0.4), aR=(0.5, 0.5, 2.3, 0.4), head=(0.1, 0)), pop))
    S['face']['rook'] = 'smirk'
    S['helm'] = lt > 0.3
    cam(S, A(lerp(-1.6, -0.8, k), -6.6, 2.0), A(lerp(0.6, 2.0, k), 1.6, 2.3), 32)


# ---------------------------------------------------------------- shots: the job
def ship_wide(S, k, t, lt):
    A = north(S, t, 1.1)
    ship_at(S, lerp(4, -2, k), lerp(24, 28, k), 2.25, t, 1.1)
    cam(S, A(lerp(20, 18, k), lerp(-16, -14, k), lerp(2.6, 3.4, k)), A(2, 24, 7.5), 26, 0.02 * math.sin(t * 0.8))


def bell_down(S, k, t, lt):
    """Mid-water: the bell rides its wire down into the green; Rook hangs on to the cage."""
    A = deep(S, 'work')
    z = lerp(46, 41.5, k)
    bell_at(S, (0, 4, z), t, 4000)
    S['rook'].place(A(2.35 + 0.1 * math.sin(t * 0.9), 3.1, z - 3.3 + 0.12 * math.sin(t * 1.3)), 0.55)
    S['rook'].apply(P('stand', aL=(2.4, 0.25, 0.5), aR=(0.3, 0.9, 1.2), lL=(0.2, 0.3), lR=(-0.2 + 0.2 * math.sin(t * 3), 0.4), head=(0.2, -0.3)))
    S['face']['rook'], S['helm'] = 'calm', True
    bub(S, A(0, 4, z - 1.5), t, 16, 0, 2.2, 9.0, 3.5, size=1.7)
    bub(S, A(2.4, 3.0, z), t, 5, 38, 0.2, 3, 2.0, seed=3, size=0.8)
    key(S, 'kc', A(6, -8, z + 3), A(0, 4, z - 1), 9000)
    key(S, 'kw', A(-5, -6, z - 5), A(1, 4, z - 2), 2200)
    cam(S, A(lerp(5.0, 4.2, k), -7.5, z - lerp(5.2, 3.6, k)), A(0.6, 4, z - 0.9), 30, 0.03 * math.sin(t * 1.1))


def divers_at_work(S, A, t):
    for i, (who, x, ph) in enumerate((('lem', 0.75, 0.0), ('yua', -1.75, 1.4))):
        s = math.sin(t * 3.0 + ph)
        uw(S, who, A(x, -0.05, 0), PI + (0.12 if i else -0.1), P('stand', aL=(1.35 + 0.15 * s, 0.1, 0.5), aR=(1.35 - 0.15 * s, 0.1, 0.5), head=(0.12, 0.1 * s), lean=0.12), t,
           ph=ph)
        lamp(S, who, 2500)
    S['wheels'][2].rotation_euler = (0, t * 1.6, 0)
    S['wheels'][0].rotation_euler = (0, -t * 1.2, 0)
    bub(S, A(0.75, -0.05, 3.2), t, 6, 0, 0.3, 5.0, 1.8, size=1.2)
    bub(S, A(-1.75, -0.05, 3.2), t, 6, 8, 0.3, 5.0, 1.6, seed=4, size=1.2)


def work(S, k, t, lt):
    A = deep(S, 'work')
    bell_at(S, (-4.5, 8.5, 9.5), t)
    divers_at_work(S, A, t)
    rope(S, 0, back_of(S, 'lem'), (-4.2, 8.0, 6.2), 1.4, t, 0.25)
    rope(S, 1, back_of(S, 'yua'), (-4.8, 8.2, 6.2), 1.0, t, 0.25)
    rook_uw(S, A(3.0, -1.6, 0), 0.75, P('stand', aR=(1.9, 0.35, 2.3, 0.6), aL=(0.2, 0.2, 0.4), head=(0.05, -0.35)), 'calm', t)
    key(S, 'kw', A(6, -5, 3), A(3.0, -1.6, 2), 900)
    cam(S, A(lerp(5.6, 4.6, k), lerp(-8.6, -7.6, k), 2.3), A(0.4, 0.8, 2.3), 30)


def valve_cu(S, k, t, lt):
    A = deep(S, 'work')
    divers_at_work(S, A, t)
    rope(S, 0, back_of(S, 'lem'), (-4.2, 8.0, 6.2), 1.4, t, 0.25)
    key(S, 'kw', A(3.5, -1.0, 2.6), A(0.75, 0.4, 2.0), 1600)
    cam(S, A(lerp(4.4, 4.0, k), lerp(-1.6, -1.3, k), 2.3), A(0.8, 0.45, 1.95), 50, 0.02 * math.sin(t * 2))


def rook_cable(S, k, t, lt):
    """Rook follows the yellow line up with one feathered finger."""
    A = deep(S, 'work')
    bell_at(S, (-1.0, 9, 10.5), t)
    rope(S, 0, (2.0, 0.6, 1.2), (-0.8, 8.4, 7.2), 1.2, t, 0.25)
    e = ease((lt - 0.2) / 0.7)
    rook_uw(S, A(3.3, -0.9, 0), -0.35, blend(P('stand', aR=(1.2, 0.2, 0.4), head=(0.05, 0.3)), P('reach', aR=(2.45, 0.75, 0.1), head=(-0.12, 0.3)), e), 'calm', t)
    key(S, 'kw', A(5.5, -5, 2.5), A(3.3, -0.9, 2.2), 1500)
    cam(S, A(lerp(5.2, 4.8, k), lerp(-6.0, -5.4, k), 2.3), A(2.6, 0.4, lerp(2.9, 3.4, k)), 28)


# ---------------------------------------------------------------- shots: the drift
def control(S, mode='calm', t=0.0):
    A = show(S, 'control')
    sky(S, '000000')
    if mode == 'alarm':
        on = (t * 3.0) % 1 < 0.5
        S['beacon'].hide_render = not on
        S['c_red'].data.energy = 1500 if on else 150
    return A


def alarm(S, k, t, lt):
    A = control(S, 'alarm', t)
    j = ease(lt / 0.25)
    S['sup'].place(A(0.2, 1.7, 0), PI + 0.25)
    S['sup'].apply(blend(P('stand', aL=(0.8, 0.1, 0.9), aR=(0.8, 0.1, 0.9), head=(0.15, 0)), P('stand', aL=(1.5, 0.5, 0.3), aR=(2.3, 0.4, 1.2), head=(-0.15, -0.5), lean=0.2), j))
    S['face']['sup'] = 'shock'
    key(S, 'kw', A(-3.5, -2.5, 3.2), A(0.2, 1.7, 2.3), 900)
    cam(S, A(lerp(-2.9, -2.3, k), lerp(-3.4, -2.6, k), 2.5), A(0.6, 2.4, 2.45), 27, 0.03 * math.sin(t * 19))


def ship_drift(S, k, t, lt):
    A = north(S, t, 1.7, '6C7C7C')
    e = ease(k)
    S['mark'].location = (0, 8, 1.4)
    ship_at(S, lerp(-1, 15, e), lerp(8, 1, e), lerp(0.25, 0.85, e), t, 1.7, 0.1)
    cam(S, A(-9, lerp(-26, -22, k), 44), A(lerp(3, 7, e), 6, 0), 30, lerp(-0.05, 0.08, k))


def cable_tight(S, k, t, lt):
    A = deep(S, 'dim')
    e = ease(lt / 0.5)
    x, y = lerp(0.3, 1.3, e), lerp(-1.4, -0.5, e)
    uw(S, 'lem', A(x, y, 0), 0.25, P('stand', aL=(1.5, 0.5, 0.4), aR=(1.3, 0.6, 0.5), lL=(0.5, 0.3), lR=(-0.4, 0.5), head=(-0.1, 0.5), lean=lerp(0.0, -0.3, e)), t,
       face='shock')
    lamp(S, 'lem', 4000)
    j = 0.03 * math.sin(t * 50) * e
    rope(S, 1, back_of(S, 'lem'), (SNAG[0], SNAG[1], SNAG[2] + j), lerp(0.7, 0.0, e), t, 0.1 * (1 - e))
    rope(S, 0, (SNAG[0], SNAG[1], SNAG[2] + j), (15, 8, 12), lerp(0.8, 0.0, e), t, 0.2 * (1 - e))
    rook_uw(S, A(-1.3, -2.0, 0), -0.6, P('point', aR=(1.75, 0.15, 0.05), aL=(0.4, 0.6, 1.0), head=(-0.15, -0.5)), 'shocked', t)
    bub(S, A(x, y, 3.2), t, 6, 0, 0.3, 4.0, 2.4, size=1.2)
    key(S, 'kc', A(-3, -6, 4), A(1, 0, 2), 2400)
    key(S, 'kw', A(5, -3, 4.5), A(*SNAG), 1100)
    cam(S, A(lerp(-0.6, -0.3, k), lerp(-8.6, -8.0, k), 2.0), A(0.5, 0.0, 2.3), 27, 0.02 * math.sin(t * 13))


def rook_flinch(S, k, t, lt):
    A = deep(S, 'dim')
    j = 0.05 * math.sin(t * 40) * max(0, 1 - lt / 0.5)
    rook_uw(S, A(-2.6 + j, -1.2, 0), -0.2, P('up', aL=(2.3, 0.6, 1.3), aR=(2.3, 0.6, 1.3), head=(-0.1, 0.0)), 'shocked', t)
    burst(S, A(-2.6, -1.6, 3.2), min(1, lt / 0.8), 10, 0, 1.2, seed=7, size=0.9)
    key(S, 'kw', A(-0.5, -5, 3.5), A(-2.6, -1.2, 2.5), 1700)
    key(S, 'kc', A(-6, -4, 2), A(-2.6, -1.2, 2.5), 700)
    cam(S, A(lerp(-3.4, -3.2, k), lerp(-5.6, -5.0, k), 2.5), A(-2.6, -1.2, 2.7), 46, 0.05 * math.sin(t * 9))


# ---------------------------------------------------------------- shots: the dark
def climb(S, k, t, lt):
    A = deep(S, 'dark')
    s = math.sin(t * 5.5)
    uw(S, 'lem', A(0.3, 0.72, lerp(0.15, 1.5, k)), PI, P('up', aL=(2.5 + 0.35 * s, 0.25, 0.5 - 0.3 * s), aR=(2.5 - 0.35 * s, 0.25, 0.5 + 0.3 * s),
       lL=(0.7 + 0.5 * s, 1.0 + 0.5 * s), lR=(0.7 - 0.5 * s, 1.0 - 0.5 * s), head=(-0.35, 0.0)), t, pitch=0.12)
    lamp(S, 'lem', 5000)
    rope(S, 1, back_of(S, 'lem'), A(1.8, -1.6, 0.1), 0.2, t, 0.1, 8)
    bub(S, A(0.3, 0.3, lerp(3.3, 4.6, k)), t, 6, 0, 0.3, 4.0, 2.2, size=1.2)
    key(S, 'kc', A(-6, -6, 6), A(0.3, 1, 2), 2600)
    key(S, 'kw', A(4, -4, 1.5), A(0.3, 0.7, 2), 380)
    cam(S, A(lerp(-4.0, -3.2, k), lerp(-6.4, -5.6, k), lerp(2.6, 3.6, k)), A(0.2, 1.2, lerp(2.2, 2.9, k)), 34)


def rook_sit(S, k, t, lt):
    """He lies on the roof of the structure. Rook sits beside him with his head down. No jokes."""
    A = deep(S, 'dark')
    lying(S, 'lem', A, -1.6, t, 0.4, 'tired')
    lamp(S, 'lem', 2600)
    bub(S, A(0.9, 3.0, TOP + 0.8), t, 3, 0, 0.2, 4.0, 0.7, size=0.9)
    S['rook'].place(A(2.05, 1.32, TOP - 0.45), 0.25)
    S['rook'].apply(P('sit', head=(0.22, 0.45), lift=-0.5, lean=0.2))
    S['face']['rook'], S['helm'] = 'sad', True
    key(S, 'kc', A(-5, -5, 7), A(0.5, 2.5, 3), 2400)
    key(S, 'kw', A(5, -3.5, 4.6), A(2.0, 1.3, 4), 600)
    cam(S, A(lerp(4.4, 3.8, k), lerp(-4.6, -4.0, k), 3.9), A(1.0, 2.0, 3.6), 36)


def still_body(S, k, t, lt):
    """From above: his arm moves less and less. The lamp gutters."""
    A = deep(S, 'dark')
    lying(S, 'lem', A, -1.6, t, max(0.0, 0.8 - k * 1.1), 'closed' if k > 0.6 else 'tired')
    lamp(S, 'lem', 2400 * (0.6 + 0.4 * math.sin(t * 23)) if k < 0.7 else 500)
    if k < 0.45:
        bub(S, A(0.9, 3.0, TOP + 0.8), t, 2, 0, 0.2, 3.0, 0.8, size=0.8)
    key(S, 'kc', A(-3, 0, 9), A(0, 3, TOP), 2200)
    key(S, 'kw', A(4, 6, 6), A(0, 3, TOP), 260)
    cam(S, A(0.2, 0.4, lerp(10.5, 8.6, ease(k))), A(0, 3.1, TOP), 34, lerp(-0.18, 0.06, k))


# ---------------------------------------------------------------- shots: watching
def rov_at(S, loc, yaw, t, power=9000, pitch=0.0):
    S['rov'].location = (loc[0] + 0.08 * math.sin(t * 1.7), loc[1] + 0.06 * math.sin(t * 2.1), loc[2] + 0.07 * math.sin(t * 2.6))
    S['rov'].rotation_euler = (pitch + 0.03 * math.sin(t * 1.9), 0.03 * math.sin(t * 1.4), yaw)
    S['rovl'].data.energy = power


def rov_in(S, k, t, lt):
    """The ROV noses in out of the murk; Rook, on the roof, waves it over."""
    A = deep(S, 'dark')
    lying(S, 'lem', A, -1.6, t, 0.25, 'tired')
    lamp(S, 'lem', 700)
    e = ease(k)
    p = (lerp(-2.7, -1.2, e), lerp(-2.6, -0.8, e), lerp(5.7, 4.8, e))
    rov_at(S, p, math.atan2(3 - p[1], -p[0]) - PI / 2 + PI, t, 12000, -0.2)
    rope(S, 2, (p[0], p[1] - 0.6, p[2] + 0.8), (-22, -14, 16), 1.5, t, 0.4)
    s = math.sin(t * 9)
    S['rook'].place(A(1.7, 1.5, TOP), 0.9)
    S['rook'].apply(P('up', aL=(2.7, 0.5 + 0.35 * s, 0.2), aR=(2.7, 0.5 - 0.35 * s, 0.2), head=(-0.15, 0.0)))
    S['face']['rook'], S['helm'] = 'shocked', True
    key(S, 'kc', A(-2, -7, 7), A(0.5, 2.5, 3.5), 1700)
    key(S, 'kw', A(6, -3, 5), A(1.7, 1.5, 4.5), 900)
    cam(S, A(lerp(1.9, 1.5, k), lerp(-10.2, -9.4, k), 4.0), A(-1.5, 1.5, 4.3), 26)


def rov_pov(S, k, t, lt):
    """Through the ROV's camera: the diver on the roof of the structure, moving less and less."""
    A = deep(S, 'dark')
    lying(S, 'lem', A, -1.6, t, max(0.0, 0.9 - k * 1.5), 'closed' if k > 0.6 else 'tired')
    lamp(S, 'lem', 400)
    key(S, 'kc', A(-6.4, -1.4, 5.4), A(0, 3, TOP), 4200)
    key(S, 'kw', A(-3.6, -2.6, 5.4), A(0, 3, TOP), 2600)
    cam(S, A(lerp(-5.4, -4.6, k) + 0.05 * math.sin(t * 2.2), lerp(-1.6, -1.0, k), 5.0 + 0.04 * math.sin(t * 3.1)), A(0, 3.0, TOP + 0.3), lerp(36, 46, k),
        0.03 * math.sin(t * 1.3))


def control_watch(S, k, t, lt):
    """The supervisor's face in the glow of the screen."""
    A = control(S, 'calm', t)
    S['c_glow'].data.energy = 380 + 60 * math.sin(t * 11)
    key(S, 'kw', A(2.6, 4.0, 3.0), A(0, 1.5, 2.4), 260)
    S['sup'].place(A(0, 1.5, 0), PI)
    S['sup'].apply(P('stand', aL=(1.0, 0.25, 0.5), aR=(1.0, 0.25, 0.5), head=(0.1, 0.0), lean=lerp(0.1, 0.24, ease(k))))
    S['face']['sup'] = 'scared' if k < 0.6 else 'sad'
    cam(S, A(lerp(1.5, 1.1, k), lerp(4.1, 3.9, k), 2.35), A(0, 1.5, 2.3), lerp(22, 26, k))


def rook_low(S, k, t, lt):
    A = deep(S, 'dark')
    lying(S, 'lem', A, -1.6, t, 0.0, 'closed')
    lamp(S, 'lem', 300)
    S['rook'].place(A(2.05, 1.32, TOP - 0.45), 0.25)
    S['rook'].apply(P('sit', head=(lerp(0.1, 0.32, ease(k)), lerp(0.5, 0.2, ease(k))), lift=-0.5, lean=0.2, aR=(0.9, 0.3, 2.2, 0.8)))
    S['face']['rook'], S['helm'] = 'sad', True
    key(S, 'kw', A(4.5, -2.5, 5.2), A(2.0, 1.3, 4.2), 900)
    key(S, 'kc', A(-2, -3, 5), A(2.0, 1.3, 4.2), 700)
    cam(S, A(lerp(3.3, 3.1, k), lerp(-2.0, -1.6, k), 3.55), A(2.05, 1.3, 4.0), 44)


# ---------------------------------------------------------------- shots: the rescue
def ship_back(S, k, t, lt):
    A = north(S, t, 1.3, '8A9896')
    x, y = lerp(-22, -9, k), lerp(44, 27, k)
    ship_at(S, x, y, -0.8, t, 1.3, 0.07)
    bx, by = x + 15, y - 15.5
    burst(S, A(bx, by, 0.5), (lt * 1.5) % 1, 22, 0, 6.0, seed=3, size=9.0, up=1.5)
    cam(S, A(lerp(12, 10, k), lerp(-14, -11, k), lerp(2.4, 3.2, k)), A(x + 5, y - 5, 6.5), 30, 0.03 * math.sin(t * 1.4))


def lift(S, k, t, lt):
    """Dave Yuasa gets his arms under him and heaves."""
    A = deep(S, 'dim')
    bell_at(S, (-1, 5.5, 9.4), t)
    e = ease(k)
    S['lem'].place(A(-1.6, lerp(3.0, 3.3, e), lerp(TOP + 0.36, TOP + 0.5, e)), -PI / 2, lerp(-PI / 2, -0.95, e))
    S['lem'].apply(P('stand', aL=(0.2, 0.5, 0.4), aR=(0.2, 0.5, 0.4), lL=(0.3, 0.5), lR=(0.15, 0.3), head=(0.3, 0.3)))
    S['face']['lem'] = 'closed'
    uw(S, 'yua', A(0.35, 4.3, TOP), 0.3, P('stand', aL=(1.0, 0.3, 0.4), aR=(1.0, 0.3, 0.4), lL=(0.5, 0.9), lR=(0.2, 0.6), lean=lerp(0.5, 0.2, e),
       lift=lerp(-0.2, -0.06, e), head=(0.3, 0.2)), t)
    lamp(S, 'yua', 4500)
    rope(S, 1, back_of(S, 'yua'), (-1.3, 5.6, 6.1), 0.7, t, 0.2)
    bub(S, A(0.2, 3.6, TOP + 2.6), t, 8, 0, 0.3, 4.5, 2.4, size=1.3)
    key(S, 'kc', A(-5, -4, 6), A(0, 3.4, 3.4), 2400)
    key(S, 'kw', A(4, -3, 4.5), A(0, 3.4, 3.4), 700)
    cam(S, A(lerp(-2.4, -1.7, k), lerp(-3.6, -2.9, k), 4.4), A(-0.2, 3.5, 3.75), 32, 0.02 * math.sin(t * 6))


def rook_point(S, k, t, lt):
    A = deep(S, 'dim')
    bell_at(S, (-2.6, 8.5, 10.4), t, 4200)
    s = math.sin(t * 8)
    S['rook'].place(A(2.2, 2.0, TOP), 0.4)
    S['rook'].apply(P('reach', aR=(2.5 + 0.12 * s, 0.8, 0.1), aL=(0.6, 0.7, 1.4), head=(-0.15, 0.35)))
    S['face']['rook'], S['helm'] = 'shocked', True
    bub(S, A(2.2, 2.0, TOP + 3.3), t, 5, 38, 0.2, 2.6, 2.2, seed=3, size=0.8)
    key(S, 'kw', A(4.5, -3, 4.5), A(2.2, 2.0, 4.6), 1500)
    key(S, 'kc', A(-3, -3, 4), A(2.2, 2.0, 4.6), 800)
    cam(S, A(lerp(3.9, 3.5, k), lerp(-3.8, -3.2, k), 4.3), A(1.7, 3.2, lerp(5.4, 5.9, k)), 30)


def haul_up(S, k, t, lt):
    """Up the umbilical toward the lit trunk of the bell, the limp diver under one arm; Rook shoves from below."""
    A = deep(S, 'dim')
    bell_at(S, (-0.6, 5.0, 11.2), t, 5200)
    z = lerp(3.4, 4.9, k)
    s = math.sin(t * 6)
    uw(S, 'yua', A(-0.2, 4.2, z), 0.5, P('reach', aR=(2.8, 0.1, 0.2 + 0.3 * s), aL=(0.5, 0.9, 0.9), lL=(0.4 * s, 0.5), lR=(-0.4 * s, 0.5), head=(-0.4, 0.0)), t,
       pitch=0.15)
    lamp(S, 'yua', 3500)
    uw(S, 'lem', A(-1.25, 4.3, z - 0.5), 0.35, P('stand', aL=(0.3, 0.3, 0.2), aR=(0.3, 0.3, 0.2), lL=(0.3, 0.4), lR=(0.1, 0.3), head=(0.6, 0.3)), t, pitch=0.55,
       roll=-0.4, face='closed')
    rope(S, 1, (0.25, 3.9, z + 2.9), (-0.6, 5.0, 8.2), -0.15, t, 0.08, 8)
    S['rook'].place(A(-0.75, 3.7, z - 3.6), 0.3, 0.1)
    S['rook'].apply(P('up', aL=(2.9, 0.2, 0.25 + 0.15 * s), aR=(2.9, 0.2, 0.25 - 0.15 * s), lL=(0.5 * s, 0.6), lR=(-0.5 * s, 0.6), head=(-0.5, 0.0)))
    S['face']['rook'], S['helm'] = 'calm', True
    bub(S, A(-0.4, 4.2, z + 3), t, 10, 0, 0.5, 5.0, 3.0, size=1.4)
    key(S, 'kc', A(-6, -5, z + 2), A(-0.5, 4.2, z + 1.5), 3000)
    key(S, 'kw', A(4, -4, z - 1), A(-0.5, 4, z), 1400)
    cam(S, A(lerp(2.6, 2.2, k), lerp(-2.6, -2.1, k), z - 2.0), A(-0.6, 4.3, z + 2.2), 26, 0.03 * math.sin(t * 5))


# ---------------------------------------------------------------- shots: inside the bell
HATCH = (-1.3, -0.5)


def laid_out(S, A, face='closed'):
    S['chris'].place(A(-1.3, 1.05, 0.36), -PI / 2, -PI / 2)
    S['chris'].apply(P('stand', aL=(0.15, 0.4, 0.3), aR=(0.15, 0.4, 0.3), lL=(0.2, 0.35), lR=(0.05, 0.1), head=(0.05, 0.0)))
    S['face']['chris'] = face
    S['ihelm'].location, S['ihelm'].rotation_euler = (-0.3, 2.25, 0), (0, 0, 2.4)


def kneel(lean=0.5, **over):
    d = dict(lL=(0.25, 1.75), lR=(0.25, 1.75), lift=-0.47, lean=lean, aL=(0.95, 0.15, 0.3), aR=(0.95, 0.15, 0.3), head=(0.35, 0.0))
    d.update(over)
    return P('stand', **d)


def bell_in(S, k, t, lt):
    """Duncan Allcock drags the limp diver up through the hatch."""
    A = show(S, 'inside')
    sky(S, '000000')
    e = ease(k)
    S['lem'].place(A(HATCH[0], HATCH[1], lerp(-2.5, -1.25, e)), 2.2, 0.0, 0.12)
    S['lem'].apply(P('stand', aL=(0.3, 0.5, 0.2), aR=(0.3, 0.5, 0.2), head=(0.55, 0.25)))
    S['face']['lem'] = 'closed'
    S['dunc'].place(A(-0.15, 0.55, 0), -0.85)
    S['dunc'].apply(P('stand', aL=(1.25, 0.2, 0.25), aR=(1.25, 0.2, 0.25), lL=(0.7, 1.2), lR=(0.3, 0.9), lean=lerp(0.75, 0.45, e), lift=-0.3, head=(0.2, 0.0)))
    S['face']['dunc'] = 'scared'
    burst(S, A(HATCH[0], HATCH[1], 0.2), (lt * 1.3) % 1, 10, 0, 0.9, seed=4, size=0.7, up=0.6)
    cam(S, A(lerp(1.9, 1.6, k), lerp(-2.1, -1.8, k), 2.5), A(-0.8, -0.1, 1.2), 22, 0.02 * math.sin(t * 7))


def breaths(S, k, t, lt):
    """Helmet off. Allcock bends to him. Rook, hat back on, watches from the hatch."""
    A = show(S, 'inside')
    sky(S, '000000')
    laid_out(S, A)
    down = 0.5 + 0.5 * math.sin(lt * 4.2 - 0.6)
    S['dunc'].place(A(1.2, 2.05, 0), 0.12)
    S['dunc'].apply(kneel(lerp(0.75, 1.12, down), head=(lerp(0.2, 0.5, down), 0.0), aL=(1.15, 0.3, 0.2), aR=(1.15, -0.05, 0.2)))
    S['face']['dunc'] = 'scared'
    S['rook'].place(A(HATCH[0], HATCH[1], -1.55), 2.0)
    S['rook'].apply(P('hat', head=(0.1, 0.0)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(2.6, 2.4, k), lerp(-1.9, -1.7, k), 1.9), A(-0.25, 0.55, 0.85), 17)


def eyes_open(S, k, t, lt):
    A = show(S, 'inside')
    sky(S, '000000')
    op = lt > 0.5
    laid_out(S, A, 'shock' if op and lt < 0.8 else ('calm' if op else 'closed'))
    S['chris'].apply(P('stand', aL=(0.15, 0.4, 0.3), aR=(0.15 + (0.5 if op else 0), 0.4, 0.3 + (0.6 if op else 0)), lL=(0.2, 0.35), lR=(0.05, 0.1),
                       head=(-0.12 if op else 0.05, 0.0)))
    S['dunc'].place(A(1.2, 2.1, 0), 0.12)
    S['dunc'].apply(kneel(0.1, head=(0.45, 0.0), aL=(0.2, 0.3, 0.4), aR=(0.2, 0.3, 0.4)))
    S['face']['dunc'] = 'shock' if op else 'scared'
    key(S, 'kw', A(0.2, -0.6, 2.6), A(1.1, 1.05, 0.4), 500)
    cam(S, A(lerp(0.1, 0.25, k), lerp(0.7, 0.8, k), lerp(2.25, 1.95, ease(k))), A(1.05, 1.05, 0.42), 40, 0.012 * math.sin(t * 31) if op else 0)


def rook_caw(S, k, t, lt):
    """Rook, shoulders out of the hatch: the hat leaves his head."""
    A = show(S, 'inside')
    sky(S, '000000')
    j = 0.04 * math.sin(t * 38) * max(0, 1 - lt / 0.5)
    S['rook'].place(A(HATCH[0] + j, HATCH[1], -1.25), 0.55)
    S['rook'].apply(P('up', aL=(2.6, 0.55, 0.35), aR=(2.6, 0.55, 0.35), head=(-0.2, 0.0)))
    S['face']['rook'] = 'shocked' if lt < 0.9 else 'laugh'
    S['hat_tip'] = math.sin(PI * min(1, lt / 0.7)) * 1.4
    key(S, 'kw', A(1.5, -2.6, 2.2), A(HATCH[0], HATCH[1], 1.0), 420)
    cam(S, A(lerp(0.9, 0.7, k), lerp(-2.75, -2.6, k), 1.5), A(-1.2, -0.4, 0.8), 22, 0.04 * math.sin(t * 9))


def sits_up(S, k, t, lt):
    """He is sitting up. Allcock's hand is on his shoulder. Rook leans on the hatch rim."""
    A = show(S, 'inside')
    sky(S, '000000')
    S['chris'].place(A(0.75, 1.5, 0), -0.3)
    S['chris'].apply(P('stand', lL=(1.5, 0.35), lR=(1.3, 0.75), lift=-0.93, lean=0.12, aL=(0.5, 0.2, 0.6), aR=(0.9, 0.2, 1.8, 0.3),
                       head=(-0.05 + 0.06 * math.sin(t * 3), -0.3)))
    S['face']['chris'] = 'calm'
    S['ihelm'].location, S['ihelm'].rotation_euler = (-0.6, 2.3, 0), (0, 0, 2.4)
    S['dunc'].place(A(1.9, 2.0, 0), 0.5)
    S['dunc'].apply(kneel(0.25, head=(0.1, 0.3), aL=(0.4, 0.2, 0.4), aR=(1.3, 0.3, 0.2)))
    S['face']['dunc'] = 'happy'
    S['rook'].place(A(HATCH[0], HATCH[1], -1.3), 1.5)
    S['rook'].apply(P('cross', head=(0.0, 0.25)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(1.5, 1.2, k), lerp(-2.6, -2.5, k), 1.9), A(-0.1, 0.6, 1.0), 18)


# ---------------------------------------------------------------- shots: the end
def morning(S):
    A = show(S, 'bay')
    sky(S, '2A3440', 1.0)
    key(S, 'kw', A(9, -7, 6), A(0, 1, 2), 5200)
    return A


def rook_dry(S, k, t, lt):
    """Morning in the bay: Rook tips his hat to the bell."""
    A = morning(S)
    S['rook'].place(A(0.6, 0.6, 0), 1.55)
    e = math.sin(PI * ease((lt - 0.2) / 1.0))
    S['rook'].apply(blend(P('stand', head=(-0.15, -0.2)), P('hat', head=(0.1, 0.2)), e))
    S['face']['rook'] = 'warm'
    S['hat_tip'] = e
    cam(S, A(lerp(4.4, 4.0, k), lerp(-3.9, -3.4, k), 1.3), A(1.3, 1.1, 2.25), 27)


def signoff(S, k, t, lt):
    A = morning(S)
    S['rook'].place(A(0, 0, 0), 0.2)
    c = max(0.0, min(1.0, (lt - 0.2) / 0.9))
    S['rook'].apply(blend(P('stand', aR=(0.9, 0.25, 1.2), head=(0.05, 0)), P('stand', aR=(1.2, 0.2, 1.5), head=(-0.12, 0)), math.sin(c * PI)))
    S['face']['rook'] = 'smirk'
    S['pick'].location = A(-0.75 - 0.2 * c, -0.75, 1.8 + 2.4 * math.sin(c * PI))
    S['pick'].rotation_euler = (t * 19, t * 9, 0)
    S['pick'].scale = (1.25, 1.25, 1.25)
    cam(S, A(lerp(1.7, 1.3, k), lerp(-5.0, -4.2, k), 0.9), A(0, 0, 2.25), 36)


# ---------------------------------------------------------------- stills for the case board
def photo_bell(S, k, t, lt):
    A = show(S, 'bay')
    sky(S, '05080E')
    cam(S, A(0.4, -5.2, 2.4), A(3.6, 3.4, 4.2), 30)


def photo_diver(S, k, t, lt):
    A = deep(S, 'work')
    uw(S, 'lem', A(-6, -6, 0), 0.25, P('stand', aR=(2.2, 0.5, 1.9), head=(-0.05, 0.1)), 0.0)
    key(S, 'kw', A(-4.5, -10, 3.2), A(-6, -6, 2.3), 320)
    key(S, 'kc', A(-9, -8, 3), A(-6, -6, 2.3), 260)
    cam(S, A(-5.5, -10.2, 2.3), A(-6, -6, 2.1), 50)


SHOTS3D = {f.__name__: f for f in (
    snap, fall_back, alone_wide, bell_away, rook_bay, rook_helmet, ship_wide, bell_down, work, valve_cu, rook_cable, alarm, ship_drift,
    cable_tight, rook_flinch, climb, rook_sit, still_body, rov_in, rov_pov, control_watch, rook_low, ship_back, lift, rook_point, haul_up,
    bell_in, breaths, eyes_open, rook_caw, sits_up, rook_dry, signoff)}
STILLS = dict(bell=photo_bell, diver=photo_diver)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it: the saturation chamber, the bridge and its positioning screen, the bell arriving,
# Duncan Allcock tending and then hauling in the torn line, Dave Yuasa dragged off and made to wait, the dark, the robot,
# the return, and the men back at work three weeks later.
ORG.update(chamber=(2000, 0, 0), bridge=(2500, 0, 0))
DAVE = dict(top='B8442E', pants='8A3020', hand='15181F', boot='15181F')
DPO = dict(top='E8E4D8', pants='1C2A4A', hand='C68A5E', boot='15181F')
PORT = (2.2, 2.45)               # the chamber porthole (x, z) in the wall at y = 2.2


def set_chamber(r):
    """The saturation chamber where the divers live under pressure, and the corridor outside its porthole."""
    add('cube', '4A525E', (0, 1.5, -0.1), scale=(12, 9, 0.2), size=1, parent=r)
    add('cube', 'B4AE9C', (0, 0, 3.95), scale=(11.2, 4.6, 0.2), size=1, parent=r)
    px, pz = PORT
    for cx, w_, cz, h_ in ((-1.975, 7.05, 1.95, 3.9), (4.175, 2.65, 1.95, 3.9), (px, 1.3, 0.9, 1.8), (px, 1.3, 3.5, 0.8)):
        add('cube', 'D8D2C0', (cx, 2.2, cz), scale=(w_, 0.2, h_), size=1, parent=r)
    add('torus', YEL, (px, 2.07, pz), rot=(PI / 2, 0, 0), major_radius=0.74, minor_radius=0.1, major_segments=16, minor_segments=5, parent=r)
    add('torus', YEL, (px, 2.33, pz), rot=(PI / 2, 0, 0), major_radius=0.74, minor_radius=0.1, major_segments=16, minor_segments=5, parent=r)
    for sx in (-1, 1):
        add('cube', 'CCC5B0', (sx * 5.5, 0, 1.95), scale=(0.2, 4.6, 3.9), size=1, parent=r)
    add('cylinder', '8A90A0', (5.36, -0.3, 1.75), rot=(0, PI / 2, 0), radius=1.05, depth=0.12, vertices=14, parent=r)
    add('torus', 'FF7A1A', (5.26, -0.3, 1.75), rot=(0, PI / 2, 0), major_radius=0.42, minor_radius=0.06, major_segments=12, minor_segments=4, parent=r, emit=0.3)
    for z, col in ((0.8, 'FF7A1A'), (2.35, '5E8FD0')):                      # bunks along the back wall
        add('cube', '3A4654', (-3.6, 1.45, z), scale=(3.3, 1.25, 0.14), size=1, parent=r)
        add('cube', col, (-3.4, 1.45, z + 0.14), scale=(2.6, 1.1, 0.16), size=1, parent=r, rough=0.9)
        add('cube', 'ECE8DC', (-4.9, 1.45, z + 0.2), scale=(0.6, 0.9, 0.2), size=1, parent=r)
    for x in (-5.2, -2.0):
        add('cube', '3A4654', (x, 0.85, 1.6), scale=(0.1, 0.1, 3.2), size=1, parent=r)
    add('cube', 'C8CCD4', (0.2, 0.4, 1.12), scale=(1.5, 1.2, 0.08), size=1, parent=r)
    add('cylinder', '6A7482', (0.2, 0.4, 0.55), radius=0.12, depth=1.1, vertices=6, parent=r)
    for x, col in ((-0.15, 'FF7A1A'), (0.6, 'F4F0E6')):
        add('cylinder', col, (x, 0.3 + 0.3 * (x > 0), 1.27), radius=0.1, depth=0.22, vertices=8, parent=r, emit=0.3)
    for x in (-1.3, 1.7):
        add('cube', '3A4654', (x, 0.4, 0.36), scale=(0.75, 1.3, 0.14), size=1, parent=r)
        add('cube', '2A3038', (x, 0.4, 0.15), scale=(0.5, 1.0, 0.3), size=1, parent=r)
    for i, (col, rad) in enumerate((('FF7A1A', 0.1), ('C8CCD4', 0.07), (YEL, 0.08))):
        add('cylinder', col, (0, 1.9 - i * 0.3, 3.7 - i * 0.02), rot=(0, PI / 2, 0), radius=rad, depth=11, vertices=6, parent=r)
    for i in range(3):
        add('cylinder', 'F4F0E6', (-0.9 + i * 0.6, 2.07, 2.8), rot=(PI / 2, 0, 0), radius=0.2, depth=0.06, vertices=10, parent=r, emit=0.5)
        add('cube', ('3DDC84', 'FFB060', '5EC8F0')[i], (-0.9 + i * 0.6, 2.07, 2.35), scale=(0.3, 0.05, 0.14), size=1, parent=r, emit=4)
    add('cube', '2A3038', (4.2, 2.05, 1.9), scale=(1.3, 0.14, 1.5), size=1, parent=r)
    for i in range(6):
        add('cube', ('3DDC84', 'FF4030', 'FFD866')[i % 3], (3.8 + (i % 3) * 0.4, 1.96, 2.2 - (i // 3) * 0.5), scale=(0.2, 0.04, 0.2), size=1, parent=r, emit=4)
    for x in (-2.4, 2.4):
        add('cube', 'FFF2D0', (x, 0, 3.83), scale=(1.8, 0.4, 0.04), size=1, parent=r, emit=4)
        light((x, 0, 3.3), 80, 'FFE8C0', kind='POINT', parent=r)
    aim = empty((0, 0.6, 1.8), r)
    light((0, -6.5, 3.2), 380, 'FFE2B8', 5.0, aim, parent=r)
    light((-6, -5, 2.5), 200, '5E8FD0', 4.0, aim, parent=r)
    # the corridor outside
    add('cube', '262C36', (0, 5.6, 3), scale=(12, 0.3, 6.4), size=1, parent=r)
    add('cube', 'FF7A1A', (0, 5.42, 1.5), scale=(12, 0.05, 0.16), size=1, parent=r, emit=1.5)
    for z, col, rad in ((4.4, YEL, 0.14), (4.8, 'C8CCD4', 0.1)):
        add('cylinder', col, (0, 5.2, z), rot=(0, PI / 2, 0), radius=rad, depth=12, vertices=6, parent=r)
    for i in range(4):
        add('cylinder', ('2E8A5A', 'D8D8D0')[i % 2], (-3.4 + i * 0.55, 5.0, 1.45), radius=0.24, depth=2.9, vertices=8, parent=r)
    add('cube', '2A3038', (5.0, 5.3, 2.0), scale=(1.6, 0.2, 1.4), size=1, parent=r)
    add('cube', '1ED8C0', (5.0, 5.18, 2.1), scale=(1.2, 0.04, 0.8), size=1, parent=r, emit=2.2)
    add('cube', 'D8D2C0', (0, 2.33, 4.4), scale=(11.2, 0.06, 1.0), size=1, parent=r)
    for x in (-3, 0, 4.6):
        add('cube', YEL, (x, 2.36, 2.0), scale=(0.25, 0.06, 3.9), size=1, parent=r)
    light((px, 3.6, 4.2), 60, 'FFB060', kind='POINT', parent=r)
    return {}


def set_bridge(r):
    """The ship's bridge: windows onto a grey sea, the positioning desk and its screen."""
    add('cube', '2A3038', (0, 0, -0.1), scale=(14.4, 10, 0.2), size=1, parent=r)
    add('cube', '1A1E28', (0, 0, 4.5), scale=(14.4, 10, 0.2), size=1, parent=r)
    for (cx, cy, sx_, sy_) in ((0, 4.8, 14.4, 0.2), (-7.1, 0, 0.2, 10), (7.1, 0, 0.2, 10)):
        add('cube', '252C3A', (cx, cy, 0.8), scale=(sx_, sy_, 1.6), size=1, parent=r)
        add('cube', '252C3A', (cx, cy, 3.95), scale=(sx_, sy_, 0.9), size=1, parent=r)
    for i in range(-3, 4):
        add('cube', '1A1E28', (i * 2.35, 4.8, 2.5), scale=(0.2, 0.24, 1.9), size=1, parent=r)
    for sx in (-1, 1):
        for y in (-2.5, 0, 2.5):
            add('cube', '1A1E28', (sx * 7.1, y, 2.5), scale=(0.24, 0.2, 1.9), size=1, parent=r)
    add('cube', '202838', (0, -4.9, 2.2), scale=(14.4, 0.2, 4.6), size=1, parent=r)
    add('cube', 'D8CDB8', (-3.4, -4.4, 1.25), scale=(3.2, 1.1, 0.1), size=1, parent=r)
    add('cube', '2A3038', (-3.4, -4.4, 0.6), scale=(3.0, 1.0, 1.2), size=1, parent=r)
    add('cube', '5EC8F0', (-3.4, -4.77, 2.9), scale=(2.4, 0.05, 1.3), size=1, parent=r, emit=1.2)
    add('cube', '3A4654', (3.6, -4.78, 1.8), scale=(1.5, 0.06, 3.4), size=1, parent=r)
    add('cylinder', 'F4F0E6', (0.6, -4.77, 3.4), rot=(PI / 2, 0, 0), radius=0.42, depth=0.05, vertices=12, parent=r, emit=0.5)
    add('cube', 'FF7A1A', (0, -4.77, 1.5), scale=(14, 0.04, 0.14), size=1, parent=r, emit=1.2)
    add('cylinder', 'C8CCD4', (0, -3.4, 1.55), rot=(0, PI / 2, 0), radius=0.06, depth=6.0, vertices=6, parent=r)
    for x in (-2.9, 2.9):
        add('cylinder', 'C8CCD4', (x, -3.4, 0.78), radius=0.06, depth=1.55, vertices=6, parent=r)
    # outside: sea, whitecaps and a pale sky all round
    add('plane', '2A4A48', (0, 160, -7), size=700, parent=r, rough=0.8)
    R = np.random.RandomState(11)
    for i in range(40):
        add('cube', 'C8D2CC', (R.uniform(-90, 90), R.uniform(12, 150), -6.9), scale=(R.uniform(2, 6), 0.8, 0.1), size=1, parent=r, emit=0.6)
    add('cube', '8E9C9A', (0, 330, 40), scale=(1400, 1, 300), size=1, parent=r, emit=1.0)
    for sx in (-1, 1):
        add('cube', '8E9C9A', (sx * 330, 0, 40), scale=(1, 1400, 300), size=1, parent=r, emit=1.0)
    # the positioning desk
    add('cube', '2A3038', (0, 3.5, 0.55), scale=(9, 1.5, 1.1), size=1, parent=r)
    add('cube', '343C48', (0, 3.2, 1.22), rot=(0.4, 0, 0), scale=(9, 1.0, 0.12), size=1, parent=r)
    cols = ('3DDC84', 'FFB060', '5EC8F0', 'FF4030', 'FFD866')
    for i in range(18):
        add('cube', cols[(i * 3) % 5], (-3.9 + i * 0.46, 3.05 + 0.2 * (i % 2), 1.27 + 0.085 * (i % 2)), rot=(0.4, 0, 0), scale=(0.16, 0.12, 0.05), size=1, parent=r, emit=4)
    dp = empty((0, 3.75, 2.25), r, (-0.22, 0, 0))
    add('cube', '0A0E14', (0, 0.05, 0), scale=(3.3, 0.1, 1.95), size=1, parent=dp)
    add('cube', '06282C', (0, 0, 0), scale=(3.1, 0.06, 1.75), size=1, parent=dp, emit=0.9)
    for i in range(-3, 4):
        add('cube', '0E5A60', (i * 0.45, -0.035, 0), scale=(0.015, 0.02, 1.7), size=1, parent=dp, emit=1.5)
    for i in range(-1, 2):
        add('cube', '0E5A60', (0, -0.035, i * 0.5), scale=(3.0, 0.02, 0.015), size=1, parent=dp, emit=1.5)
    ok = add('torus', '3DDC84', (0, -0.05, 0), rot=(PI / 2, 0, 0), major_radius=0.42, minor_radius=0.035, major_segments=20, minor_segments=4, parent=dp, emit=7)
    bad = add('torus', 'FF4030', (0, -0.05, 0), rot=(PI / 2, 0, 0), major_radius=0.42, minor_radius=0.045, major_segments=20, minor_segments=4, parent=dp, emit=9)
    add('cylinder', 'FFD866', (0, -0.05, 0), rot=(PI / 2, 0, 0), radius=0.07, depth=0.03, vertices=8, parent=dp, emit=8)
    mark = add('cube', 'FF7A1A', (0, -0.07, 0), scale=(0.5, 0.03, 0.16), size=1, parent=dp, emit=9)
    for x, col in ((-3.3, '5EC8F0'), (3.3, 'FFB060')):
        add('cube', '0A0E14', (x, 3.8, 2.0), scale=(1.5, 0.1, 1.1), size=1, parent=r)
        add('cube', col, (x, 3.74, 2.0), scale=(1.3, 0.04, 0.9), size=1, parent=r, emit=1.8)
    add('cylinder', '2A3038', (-2.7, 1.6, 0.5), radius=0.12, depth=1.0, vertices=6, parent=r)
    add('cube', '8A1E3A', (-2.7, 1.6, 1.05), scale=(0.9, 0.9, 0.14), size=1, parent=r)
    add('cube', '8A1E3A', (-2.7, 1.15, 1.7), scale=(0.9, 0.14, 1.2), size=1, parent=r)
    beacon = add('cylinder', 'FFB000', (2.2, 3.6, 1.45), radius=0.2, depth=0.3, vertices=8, parent=r, emit=30)
    amb = light((2.0, 2.6, 2.6), 0, 'FFA020', kind='POINT', parent=r)
    aim = empty((0, 1.4, 2.2), r)
    glow = light((0, 3.2, 2.9), 500, '6FE8E0', 3.0, aim, parent=r)
    light((0, 9, 6), 9000, 'C8D8E0', 9.0, aim, parent=r)
    light((0, -1, 4.2), 90, 'FFE2B8', kind='POINT', parent=r)
    light((-4, -3.8, 3.2), 300, 'FF8A40', 2.5, aim, parent=r)
    return dict(dp_ok=ok, dp_bad=bad, dp_mark=mark, b_beacon=beacon, b_amb=amb, b_glow=glow)


def extend(S):
    for name, fn in (('chamber', set_chamber), ('bridge', set_bridge)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    # the moonpool bay gets a right-hand wall and a workbench so the wide frame has an end
    before = set(bpy.data.objects)
    o = empty(ORG['bay'])
    add('cube', '2E3540', (12.5, 1, 5.5), scale=(0.4, 16, 11), size=1, parent=o)
    add('cube', '3A4654', (10.6, 5.6, 0.75), scale=(3.0, 1.4, 1.5), size=1, parent=o)
    add('cube', 'B8322A', (10.2, 5.4, 1.75), scale=(1.0, 0.7, 0.5), size=1, parent=o)
    for i in range(4):
        add('cylinder', ('D8D8D0', '2E8A5A')[i % 2], (11.6, 2.6 - i * 0.55, 1.45), radius=0.23, depth=2.9, vertices=8, parent=o)
    add('cube', YEL, (12.26, -1.5, 2.2), scale=(0.06, 2.2, 0.5), size=1, parent=o, emit=0.4)
    add('cube', 'FFE7B8', (12.26, 3.0, 7.0), scale=(0.08, 1.6, 0.3), size=1, parent=o, emit=5)
    for ob in set(bpy.data.objects) - before:
        for uc in list(ob.users_collection):
            uc.objects.unlink(ob)
        S['colls']['bay'].objects.link(ob)
    S['in_lights'] = [(o, o.data.energy) for o in S['colls']['inside'].objects if o.type == 'LIGHT']
    S['dave'] = K.Rig(DAVE, person_head('C8936C', '2A2420'))
    add('cylinder', '15181F', (0, 0, -0.3), radius=0.2, depth=0.12, vertices=8, parent=S['dave'].head)
    S['dpo'] = K.Rig(DPO, person_head('C68A5E', '5A4632'))
    for sx in (-1, 1):
        add('cube', '15181F', (sx * 0.44, 0, 1.1), scale=(0.2, 0.3, 0.05), size=1, parent=S['dpo'].body)
    S['mug'] = add('cylinder', 'FF7A1A', (0, -0.1, -0.56), radius=0.1, depth=0.22, vertices=8, parent=S['chris'].el[1], emit=0.3)


_build0, _reset0, _finish0 = build, reset, finish
XCAST = ('dave', 'dpo')


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
    S['mug'].hide_render = True
    for l, e0 in S['in_lights']:
        l.data.energy = e0
    S['dp_ok'].hide_render, S['dp_bad'].hide_render = False, True
    S['dp_mark'].location = (0, -0.07, 0)
    S['dp_mark'].rotation_euler = (0, 0, 0)
    S['b_beacon'].hide_render = True
    S['b_amb'].data.energy = 0
    S['b_glow'].data.energy = 500
    S['xbell'].rotation_euler = (0, 0, 0)


def finish(S, t):
    _finish0(S, t)
    for who in XCAST:
        e = S['face'][who]
        x = S[who].extra
        kk = dict(scared=1.3, shock=1.7, calm=1.0, sad=0.6, happy=0.85, closed=0.08, tired=0.45).get(e, 1.0)
        for ey in x['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], x['eye0'] * kk)
        x['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
        x['jaw'].location.z = -0.13 - (0.05 if e == 'shock' else 0.0)


def dark_lamp(fn, boost=1.5):
    """After the line parts his hat lamp is dead too (its power came down the umbilical): the Short's shots, without the lamp."""
    def g(S, k, t, lt):
        fn(S, k, t, lt)
        S['lem'].extra['lamp'].data.energy = 0
        S['lem'].extra['glow'].hide_render = True
        S['kc'].data.energy *= boost
    g.__name__, g.__doc__ = fn.__name__, fn.__doc__
    return g


def lamp_off(S, who='lem'):
    S[who].extra['lamp'].data.energy = 0
    S[who].extra['glow'].hide_render = True


def lying(S, who, A, x0, t, twitch=0.0, face=None, y=3.0, z=TOP + 0.42):
    """Long-form: he lies on his side on the roof, knees drawn up, head toward +X (replaces the Short's flat-on-his-back pose)."""
    S[who].place(A(x0 + 0.3, y - 0.4, z + 0.02 * math.sin(t * 1.4)), 0.0, 0.0, PI / 2)
    S[who].apply(P('stand', aL=(0.9 + 0.5 * twitch * max(0, math.sin(t * 5.0)), 0.2, 1.4 + 0.3 * twitch * math.sin(t * 5.0)), aR=(0.7, 0.2, 1.6), lL=(1.1, 1.4), lR=(0.8, 1.2),
                   head=(0.35, 0.0)))
    if face:
        S['face'][who] = face


# ---------------------------------------------------------------- long shots: the chamber
def chamber(S):
    A = show(S, 'chamber')
    sky(S, '05080E')
    return A


def seated(S, who, A, x, yaw, t, ph=0.0, face='calm', **over):
    d = dict(lL=(1.5, 1.55), lR=(1.5, 1.55), lift=-0.62, lean=0.1, aL=(0.75, 0.1, 1.2, 0.6), aR=(0.75, 0.1, 1.2, 0.6), head=(0.03 * math.sin(t * 2 + ph), 0.2 * math.sin(t * 1.3 + ph)))
    d.update(over)
    S[who].place(A(x, 0.4, 0), yaw)
    S[who].apply(P('stand', **d))
    S['face'][who] = face


def chamber_wide(S, k, t, lt):
    """Three divers at the table in the chamber; Rook's face is at the porthole."""
    A = chamber(S)
    seated(S, 'chris', A, -1.3, PI / 2, t, 0.0, 'happy', aR=(1.1, 0.1, 1.5 + 0.3 * math.sin(t * 2.2), 0.3))
    S['mug'].hide_render = False
    seated(S, 'dave', A, 1.7, -PI / 2, t, 1.7, 'calm', aL=(1.0, 0.3, 0.9 + 0.3 * math.sin(t * 3.1)))
    S['dunc'].place(A(-2.9, -0.3, 0), -1.0)
    S['dunc'].apply(P('cross', head=(0.05, 0.3 + 0.1 * math.sin(t * 1.5))))
    S['face']['dunc'] = 'happy'
    S['rook'].place(A(PORT[0] + 0.05 * math.sin(t * 1.2), 3.05, 0.02), 0.0)
    S['rook'].apply(P('stand', aL=(1.9, 0.5, 1.2), aR=(1.9, 0.5, 1.2), head=(0.05, 0.25 * math.sin(t * 1.4))))
    S['face']['rook'] = 'deadpan'
    key(S, 'kw', A(PORT[0] - 0.6, 2.5, 3.3), A(PORT[0], 2.95, 2.5), 160)
    cam(S, A(lerp(1.2, 0.5, k), lerp(-8.4, -7.4, k), 2.3), A(0.3, 1.0, 1.95), 30)


def chamber_cu(S, k, t, lt):
    """Close on Chris Lemons, mug in hand, mid-sentence."""
    A = chamber(S)
    s = math.sin(t * 6)
    seated(S, 'chris', A, -1.3, PI / 2, t, 0.0, 'happy', aR=(1.25, 0.1, 1.7 + 0.15 * s, 0.3), head=(0.04 * s, -0.5 + 0.1 * math.sin(t * 2)))
    S['mug'].hide_render = False
    seated(S, 'dave', A, 1.7, -PI / 2, t, 1.7, 'happy', head=(-0.05, 0.2))
    S['rook'].place(A(PORT[0], 3.05, 0.02), 0.0)
    S['rook'].apply(P('stand', aL=(1.9, 0.5, 1.2), aR=(1.9, 0.5, 1.2), head=(0.05, -0.3)))
    S['face']['rook'] = 'deadpan'
    key(S, 'kw', A(PORT[0] - 0.6, 2.5, 3.3), A(PORT[0], 2.95, 2.5), 160)
    cam(S, A(lerp(0.9, 0.6, k), lerp(-3.4, -3.0, k), 2.35), A(0.3, 1.2, 2.25), 30)


def rook_ears(S, k, t, lt):
    """Out in the corridor Rook listens at the porthole, then claps his wings over his ears."""
    A = chamber(S)
    e = ease((lt - 0.5) / 0.4)
    S['rook'].place(A(PORT[0] + 0.25, 3.3, 0), -0.55)
    S['rook'].apply(blend(P('stand', aR=(1.3, 0.3, 1.6), head=(0.1, 0.5), lean=0.15), P('stand', aL=(0.2, 1.9, 1.9, -1.5), aR=(0.2, 1.9, 1.9, -1.5), head=(0.18, -0.5), lean=-0.05), e))
    S['face']['rook'] = 'calm' if e < 0.5 else 'deadpan'
    S['hat_tip'] = 0.5 * e
    seated(S, 'chris', A, -1.3, PI / 2, t, 0.0, 'happy')
    seated(S, 'dave', A, 1.7, -PI / 2, t, 1.7, 'happy')
    key(S, 'kw', A(-1.0, 5.0, 3.3), A(PORT[0], 3.4, 2.4), 260)
    key(S, 'kc', A(4.6, 4.8, 2.0), A(PORT[0], 3.2, 2.4), 120)
    cam(S, A(lerp(-1.3, -0.9, k), lerp(4.5, 4.3, k), 2.5), A(PORT[0] - 0.1, 3.1, 2.45), 34)


# ---------------------------------------------------------------- long shots: the bell goes down
def swimmer(t, ph=0.0, **over):
    s = math.sin(t * 4 + ph)
    d = dict(aL=(0.6, 0.5, 0.5), aR=(0.6, 0.5, 0.5), lL=(0.35 * s, 0.4), lR=(-0.35 * s, 0.4), head=(0.2, 0.0))
    d.update(over)
    return P('stand', **d)


def bell_stage(S, k, t, lt):
    """The bell hangs over the structure; two divers drop out of its trunk. Rook rides the cage."""
    A = deep(S, 'work')
    bell_at(S, (-3.2, 6.5, 10.0), t, 5200)
    e = ease(k)
    for i, (who, x, y, z0, z1) in enumerate((('lem', -0.4, 2.6, 5.4, 3.3), ('yua', -2.4, 4.6, 6.4, 4.4))):
        uw(S, who, A(x, y, lerp(z0, z1, e)), 0.4 - 0.5 * i, swimmer(t, i * 1.5), t, pitch=0.25, ph=i)
        lamp(S, who, 2600)
        rope(S, i, back_of(S, who), (-3.2 + 0.3 * i, 6.3, 6.7), 0.6, t, 0.25, 10)
        bub(S, A(x, y, lerp(z0, z1, e) + 3.2), t, 6, i * 8, 0.3, 4.0, 1.8, seed=i * 3, size=1.2)
    S['rook'].place(A(-0.85 + 0.1 * math.sin(t * 0.9), 5.7, 6.75 + 0.12 * math.sin(t * 1.3)), 0.5)
    S['rook'].apply(P('stand', aL=(2.4, 0.25, 0.5), aR=(1.6, 0.3, 0.2), lL=(0.2, 0.3), lR=(-0.2 + 0.2 * math.sin(t * 3), 0.4), head=(0.3, -0.4)))
    S['face']['rook'], S['helm'] = 'calm', True
    key(S, 'kw', A(4, -4, 8), A(-1, 5, 7), 2600)
    cam(S, A(lerp(5.6, 5.0, k), lerp(-6.4, -5.8, k), lerp(1.6, 2.0, k)), A(-1.3, 4.0, 5.6), 30)


def tend_pose(pull=0.0, s=0.0):
    return P('stand', aL=(1.1 + 0.5 * s * pull, 0.15, 0.7 - 0.4 * s * pull), aR=(1.1 - 0.5 * s * pull, 0.15, 0.7 + 0.4 * s * pull), lL=(0.35, 0.5), lR=(-0.1, 0.3),
             lean=0.3 + 0.12 * pull, lift=-0.1, head=(0.35, 0.0))


def hands_of(S, who):
    bpy.context.view_layer.update()
    a, b = (S[who].hands[i].matrix_world.translation for i in (0, 1))
    return tuple((a + b) / 2)


def bell_dim(S, f):
    """Turn the bell's own lamps down for the long shots that look straight at its near wall."""
    for l, e0 in S['in_lights']:
        l.data.energy = e0 * f


def dunc_tend(S, k, t, lt):
    """Inside the bell Duncan Allcock pays the divers' lines out through the hatch."""
    A = show(S, 'inside')
    sky(S, '000000')
    s = math.sin(t * 2.6)
    S['dunc'].place(A(-1.75, -2.0, 0), PI - 0.3)
    S['dunc'].apply(tend_pose(0.5, s))
    S['face']['dunc'] = 'calm'
    hnd = hands_of(S, 'dunc')
    rope(S, 0, hnd, A(HATCH[0] - 0.15, HATCH[1], -0.4), 0.15, t, 0.03, 6)
    rope(S, 1, (hnd[0] + 0.25, hnd[1], hnd[2] - 0.1), A(HATCH[0] + 0.2, HATCH[1], -0.4), 0.2, t, 0.03, 6)
    bell_dim(S, 0.45)
    cam(S, A(lerp(0.5, 0.2, k), lerp(1.5, 1.3, k), 2.3), A(-1.5, -1.3, 1.5), 24)


def rook_line(S, k, t, lt):
    """Rook holds the umbilical in both hands and follows it up with his eyes."""
    A = deep(S, 'work')
    bell_at(S, (-1.0, 9, 10.5), t)
    e = ease((lt - 0.3) / 1.2)
    rook_uw(S, A(3.2, -1.3, 0), 0.5, P('stand', aL=(1.25, 0.05, 0.7), aR=(1.25, 0.05, 0.7), head=(lerp(0.3, -0.25, e), lerp(0.0, 0.35, e))), 'calm', t)
    hnd = hands_of(S, 'rook')
    rope(S, 0, (0.9, 0.2, 1.5), hnd, 0.5, t, 0.1, 7)
    rope(S, 1, hnd, (-0.8, 8.4, 7.2), 0.9, t, 0.25)
    key(S, 'kw', A(5.5, -5, 2.5), A(3.2, -1.3, 2.2), 1700)
    cam(S, A(lerp(4.6, 4.3, k), lerp(-5.6, -5.1, k), 2.1), A(2.9, -0.9, 2.3), 40)


# ---------------------------------------------------------------- long shots: the storm and the bridge
def storm_wide(S, k, t, lt):
    """From astern and low: the ship pitching in a rougher sea, spray over the bow."""
    A = north(S, t, 2.1, '5E6E6E')
    S['n_sun'].data.energy = 170000
    x, y = lerp(6, 3, k), 30
    ship_at(S, x, y, 0.55, t, 2.1, 0.13)
    burst(S, A(x + 16, y + 10, 1.0), (lt * 1.1) % 1, 20, 0, 6.0, seed=5, size=9.0, up=1.6)
    cam(S, A(lerp(-27, -25, k), lerp(0, 1.5, k), lerp(3.2, 3.9, k)), A(x - 3, y - 1, 6.5), 34, 0.05 * math.sin(t * 1.3))


def bridge(S, t, state='ok', off=0.0):
    A = show(S, 'bridge')
    sky(S, '000000')
    if state != 'ok':
        on = (t * 3.0) % 1 < 0.5
        S['b_beacon'].hide_render = not on
        S['b_amb'].data.energy = 900 if on else 80
        S['dp_ok'].hide_render, S['dp_bad'].hide_render = True, not on
    S['dp_mark'].location = (off * 1.25, -0.07, off * 0.42)
    S['dp_mark'].rotation_euler = (0, -0.6 * off, 0)
    return A


def bridge_calm(S, k, t, lt):
    """The positioning officer at the desk, the ship's mark dead centre on the screen; Rook reads over his shoulder."""
    A = bridge(S, t)
    S['dpo'].place(A(-0.5, 1.75, 0), PI + 0.1)
    S['dpo'].apply(P('stand', aL=(0.9, 0.2, 0.8), aR=(0.9, 0.2, 0.8), head=(0.1, 0.12 * math.sin(t * 1.1)), lean=0.08))
    S['rook'].place(A(2.3, 1.4, 0), PI - 0.75)
    S['rook'].apply(P('cross', head=(0.0, 0.35 + 0.1 * math.sin(t * 1.3))))
    S['face']['rook'] = 'deadpan'
    key(S, 'kw', A(4.5, -2.5, 3.2), A(2.3, 1.4, 2.4), 420)
    cam(S, A(lerp(-3.8, -3.2, k), lerp(-3.4, -2.8, k), 2.75), A(0.6, 2.9, 2.15), 30, 0.035 * math.sin(t * 0.9))


def bridge_alarm(S, k, t, lt):
    """Amber light. The ship's mark slides off the ring; the officer lunges for the desk."""
    A = bridge(S, t, 'alarm', ease(k))
    j = ease(lt / 0.3)
    S['dpo'].place(A(-0.3, 1.9, 0), PI - 0.15)
    S['dpo'].apply(blend(P('stand', aL=(0.9, 0.2, 0.8), aR=(0.9, 0.2, 0.8), head=(0.1, 0)), P('stand', aL=(1.5, 0.4, 0.2), aR=(1.7, 0.2, 0.3), head=(-0.1, 0.3), lean=0.3), j))
    S['face']['dpo'] = 'shock'
    key(S, 'kw', A(4.0, -1.5, 3.0), A(0, 2, 2.3), 260)
    cam(S, A(lerp(3.2, 2.6, k), lerp(-1.6, -1.0, k), 2.5), A(0.0, 3.0, 2.15), 30, 0.03 * math.sin(t * 17))


def bridge_fight(S, k, t, lt):
    """The officer's face over the desk, working the controls; behind him Rook hangs on to the rail as the room rolls."""
    A = bridge(S, t, 'alarm', 1.0)
    s = math.sin(t * 5)
    S['dpo'].place(A(0, 1.7, 0), PI)
    S['dpo'].apply(P('stand', aL=(1.2 + 0.2 * s, 0.3, 0.4), aR=(1.2 - 0.2 * s, 0.3, 0.4), head=(0.15, 0.25 * math.sin(t * 2.3)), lean=0.22))
    S['face']['dpo'] = 'scared'
    r = 0.09 * math.sin(t * 1.4)
    S['rook'].place(A(2.2 + 0.25 * math.sin(t * 1.4), -2.9, 0), PI + 0.2, 0, r)
    S['rook'].apply(P('stand', aL=(0.9, 0.9, 0.6), aR=(0.9, 0.9, 0.6), lL=(0.2, 0.2), lR=(-0.2, 0.2), head=(-0.05, 0.2)))
    S['face']['rook'] = 'shocked'
    S['hat_tip'] = 0.4
    key(S, 'kw', A(3.0, 2.0, 3.2), A(2.2, -2.9, 2.4), 520)
    key(S, 'kc', A(-2.6, 3.9, 2.9), A(0, 1.7, 2.4), 240)
    cam(S, A(lerp(-2.9, -2.6, k), lerp(3.1, 2.9, k), 2.45), A(0.5, 0.6, 2.3), 24, r * 1.2)


# ---------------------------------------------------------------- long shots: the drift on the seabed
def bell_drag(S, k, t, lt):
    """The bell is hauled sideways off the structure, both lines trailing; Rook, below, points up at it."""
    A = deep(S, 'dim')
    e = ease(k)
    bx, by, bz = lerp(-3.5, 6.5, e), lerp(7.5, 9.5, e), lerp(9.5, 11.0, e)
    bell_at(S, (bx, by, bz), t, 3600)
    S['xbell'].rotation_euler = (0, -0.22 * math.sin(e * PI), 0)
    for i, (who, x) in enumerate((('lem', 0.75), ('yua', -1.75))):
        uw(S, who, A(x + 0.5 * e, -0.2 - 0.4 * e, 0), PI + 0.9 - 0.4 * i, P('stand', aL=(1.0, 0.6, 0.5), aR=(1.4, 0.5, 0.4), lL=(0.4, 0.3), lR=(-0.3, 0.4), head=(-0.3, 0.6)), t, ph=i)
        lamp(S, who, 3000)
        rope(S, i, back_of(S, who), (bx - 0.3 + 0.6 * i, by, bz - 3.3), lerp(1.3, 0.2, e), t, 0.2)
    rook_uw(S, A(-4.2, -4.6, 0), -0.9, P('reach', aR=(2.3, 0.3, 0.1), aL=(0.5, 0.6, 1.0), head=(-0.35, -0.2)), 'shocked', t)
    key(S, 'kw', A(-6, -8, 3), A(-4.2, -4.6, 2.2), 1500)
    key(S, 'kc', A(-6, -8, 7), A(0, 2, 3), 3000)
    cam(S, A(lerp(-8.6, -8.0, k), lerp(-6.6, -6.0, k), 1.5), A(lerp(-1.5, 0.5, e), 3.5, 5.2), 30, 0.03 * math.sin(t * 9))


def go_back(S, k, t, lt):
    """Both divers leave the valves and make for the bell; one line trails back to the corner of the structure."""
    A = deep(S, 'dim')
    bell_at(S, (8.5, 9, 11.5), t, 2400)
    e = ease(k)
    s = math.sin(t * 6)
    uw(S, 'yua', A(lerp(-1.2, -0.2, e), lerp(2.2, 3.6, e), TOP + lerp(0.3, 1.4, e)), 2.2, P('up', aL=(2.6 + 0.3 * s, 0.3, 0.3), aR=(2.6 - 0.3 * s, 0.3, 0.3), lL=(0.5 * s, 0.6), lR=(-0.5 * s, 0.6),
       head=(-0.4, 0)), t, pitch=0.3)
    lamp(S, 'yua', 3200)
    rope(S, 1, back_of(S, 'yua'), (8.2, 8.8, 8.3), 1.2, t, 0.3)
    uw(S, 'lem', A(lerp(0.2, 0.9, e), lerp(0.2, 1.2, e), lerp(0.9, 2.2, e)), 2.4, P('up', aL=(2.4 - 0.3 * s, 0.3, 0.4), aR=(2.4 + 0.3 * s, 0.3, 0.4), lL=(-0.5 * s, 0.7), lR=(0.5 * s, 0.7),
       head=(-0.3, 0.3)), t, pitch=0.35, face='scared')
    lamp(S, 'lem', 3200)
    rope(S, 0, back_of(S, 'lem'), SNAG, 0.5, t, 0.15, 8)
    rope(S, 2, SNAG, (8.6, 9.0, 8.3), 0.5, t, 0.1)
    bub(S, A(0.5, 1.0, 3.6), t, 8, 0, 0.6, 4.0, 2.6, size=1.2)
    key(S, 'kc', A(3, -7, 8), A(0.5, 2, 3), 3600)
    key(S, 'kw', A(7, -2, 4.5), A(*SNAG), 1500)
    cam(S, A(lerp(7.2, 6.4, k), lerp(-5.2, -4.6, k), lerp(5.6, 5.0, k)), A(0.8, 2.2, 3.1), 28, 0.02 * math.sin(t * 7))


# ---------------------------------------------------------------- long shots: the bell, the torn end, the wait
def dunc_haul(S, k, t, lt):
    """Duncan Allcock hauls the slack line in, hand over hand."""
    A = show(S, 'inside')
    sky(S, '000000')
    s = math.sin(t * 9)
    S['dunc'].place(A(-1.75, -2.0, 0), PI - 0.3)
    S['dunc'].apply(tend_pose(1.0, s))
    S['face']['dunc'] = 'scared'
    hnd = hands_of(S, 'dunc')
    rope(S, 0, hnd, A(HATCH[0], HATCH[1], -0.5), 0.02, t, 0.06, 6)
    rope(S, 2, (hnd[0] + 0.5, hnd[1] + 0.4, hnd[2] - 0.3), A(0.4, -0.9, 0.1), 0.5, t, 0.03, 6)
    burst(S, A(HATCH[0], HATCH[1], 0.1), (lt * 1.6) % 1, 8, 0, 0.7, seed=2, size=0.6, up=0.5)
    bell_dim(S, 0.45)
    cam(S, A(lerp(0.75, 0.55, k), lerp(1.2, 1.0, k), 1.05), A(-1.5, -1.4, 1.9), 24, 0.025 * math.sin(t * 11))


def dunc_end(S, k, t, lt):
    """What comes up through the hatch is a torn end."""
    A = show(S, 'inside')
    sky(S, '000000')
    S['dunc'].place(A(-1.75, -2.0, 0), PI - 0.3)
    S['dunc'].apply(P('stand', aL=(1.3, 0.1, 0.9), aR=(1.3, 0.1, 0.9), lL=(0.3, 0.4), lR=(-0.1, 0.3), lean=0.2, lift=-0.08, head=(lerp(0.45, 0.3, ease(k)), 0.0)))
    S['face']['dunc'] = 'shock' if lt > 0.5 else 'scared'
    hnd = hands_of(S, 'dunc')
    end = (hnd[0] + 0.5 + 0.05 * math.sin(t * 3), hnd[1] + 0.75, hnd[2] - 0.75 + 0.04 * math.sin(t * 2.2))
    rope(S, 0, (hnd[0] - 0.3, hnd[1] - 0.35, hnd[2] - 1.5), hnd, -0.3, t, 0.0, 5)
    rope(S, 1, hnd, end, 0.12, t, 0.02, 4)
    S['spark'].location, S['spark'].scale = end, (0.35, 0.35, 0.35)
    bell_dim(S, 0.4)
    cam(S, A(lerp(0.2, 0.0, k), lerp(0.75, 0.55, k), lerp(2.15, 2.05, k)), A(-1.35, -1.5, 1.95), lerp(36, 42, k))


def rook_hatch(S, k, t, lt):
    """From above: Rook, head and shoulders out of the hatch, looks at the torn line on the bell floor. Hat low."""
    A = show(S, 'inside')
    sky(S, '000000')
    S['rook'].place(A(HATCH[0], HATCH[1], -1.3), PI + 0.5)
    S['rook'].apply(P('stand', aL=(1.3, 0.5, 0.5), aR=(1.3, 0.5, 0.5), head=(lerp(0.1, 0.4, ease(k)), -0.3)))
    S['face']['rook'] = 'sad'
    rope(S, 0, A(-0.3, 0.9, 0.08), A(1.2, 0.3, 0.08), 0.0, t, 0.0, 6)
    rope(S, 1, A(1.2, 0.3, 0.08), A(0.6, 1.7, 0.08), 0.0, t, 0.0, 5)
    S['spark'].location, S['spark'].scale = A(-0.3, 0.9, 0.12), (0.3, 0.3, 0.3)
    S['dunc'].place(A(1.9, 1.6, 0), 0.9)
    S['dunc'].apply(kneel(0.2, head=(0.5, 0.0), aL=(0.3, 0.2, 0.5), aR=(0.3, 0.2, 0.5)))
    S['face']['dunc'] = 'sad'
    bell_dim(S, 0.5)
    cam(S, A(lerp(-0.3, -0.5, k), lerp(2.3, 2.1, k), lerp(1.9, 1.7, k)), A(-1.0, -0.2, 0.75), 22)


def yua_dragged(S, k, t, lt):
    """Dave Yuasa is pulled backwards off the roof of the structure by his own line, one arm still reaching."""
    A = deep(S, 'dim')
    e = ease(k)
    x, y, z = lerp(-0.4, 2.6, e), lerp(3.2, 4.6, e), TOP + lerp(0.2, 2.2, e)
    uw(S, 'yua', A(x, y, z), 1.2, P('reach', aR=(1.9, 0.3, 0.2), aL=(1.2, 0.8, 0.6), lL=(0.9, 0.6), lR=(0.4, 1.0), head=(0.2, 0.0)), t, pitch=lerp(-0.2, -0.75, e), face='shock')
    lamp(S, 'yua', 4200)
    b = back_of(S, 'yua')
    rope(S, 1, b, (12, 9, 12), 0.0, t, 0.05)
    burst(S, A(x, y, z + 2), min(1, k * 1.3), 12, 0, 1.5, seed=6, size=1.1)
    key(S, 'kc', A(-5, -5, 7), A(1, 3.5, 4), 3200)
    key(S, 'kw', A(2, -3, 5.5), A(x, y, z + 1.5), 900)
    cam(S, A(lerp(-3.6, -3.0, k), lerp(-4.4, -3.8, k), 4.3), A(lerp(0.4, 1.4, e), 3.6, lerp(4.0, 5.0, e)), 40, 0.04 * math.sin(t * 13))


def yua_climb(S, k, t, lt):
    """From above: Yuasa on his line under the bell lights, looking back down into the black."""
    A = deep(S, 'dark')
    z = lerp(7.0, 7.8, k)
    s = math.sin(t * 3)
    uw(S, 'yua', A(4.0, 6.0, z), -2.2, P('up', aL=(2.7, 0.2, 0.3 + 0.2 * s), aR=(1.0, 0.7, 0.5), lL=(0.3 * s, 0.5), lR=(-0.3 * s, 0.5), head=(0.5, 0.5)), t, pitch=0.1)
    lamp(S, 'yua', 2600)
    rope(S, 1, (3.8, 6.2, z + 3.0), (4.4, 6.6, z + 9), 0.0, t, 0.05, 6)
    bub(S, A(4.0, 6.0, z + 3.2), t, 8, 0, 0.3, 4.0, 2.0, size=1.2)
    key(S, 'kw', A(5, 7, z + 8), A(4, 6, z + 2), 5200)
    key(S, 'kc', A(-6, -6, 9), A(0, 3, TOP), 2600)
    cam(S, A(lerp(6.6, 6.2, k), lerp(9.2, 8.8, k), z + 6.0), A(3.0, 4.6, z + 0.6), 30, 0.03 * math.sin(t * 1.7))


def yua_wait(S, k, t, lt):
    """In the bell: Yuasa sits by the hatch, helmet still on, Allcock at the panel. Rook sits against the wall, hat low."""
    A = show(S, 'inside')
    sky(S, '000000')
    S['yua'].place(A(0.25, -0.45, 0), -PI / 2)
    S['yua'].apply(P('stand', lL=(1.5, 0.5), lR=(1.3, 1.1), lift=-0.93, lean=0.3, aL=(0.9, 0.2, 1.0), aR=(0.9, 0.2, 1.0), head=(0.45, 0.1 * math.sin(t * 1.1))))
    lamp(S, 'yua', 0)
    S['dunc'].place(A(1.2, -2.4, 0), -2.21)
    S['dunc'].apply(P('stand', aR=(0.3, 0.2, 0.4), aL=(0.3, 0.2, 0.4), head=(0.35, 0.1 * math.sin(t * 0.9)), lean=0.1))
    S['face']['dunc'] = 'scared'
    S['rook'].place(A(2.3, 0.6, 0), -1.74)
    S['rook'].apply(P('stand', lL=(1.4, 0.4), lR=(1.2, 0.9), lift=-0.93, lean=0.2, aL=(0.7, 0.2, 1.1), aR=(0.7, 0.2, 1.1), head=(0.35, 0.2)))
    S['face']['rook'] = 'sad'
    bell_dim(S, 0.5)
    cam(S, A(lerp(-2.3, -2.1, k), lerp(1.3, 1.1, k), lerp(2.3, 2.1, k)), A(0.7, -0.5, 1.15), 20)


# ---------------------------------------------------------------- long shots: alone
def lem_switch(S, k, t, lt):
    """In the dark he reaches back for the valve of his emergency bottles."""
    A = deep(S, 'dark')
    e = ease(lt / 0.8)
    uw(S, 'lem', A(0.4, -2.0, 0), 2.5, blend(P('stand', aL=(0.5, 0.6, 0.6), aR=(0.5, 0.6, 0.6), head=(-0.1, 0.3)), P('stand', aR=(-0.9, 0.5, 2.3, 0.6), aL=(0.9, 0.3, 1.2), head=(0.15, -0.5),
       lean=0.1), e), t, face='scared')
    lamp_off(S)
    rope(S, 1, back_of(S, 'lem'), A(1.8, -3.4, 0.12), 0.3, t, 0.1, 8)
    if lt > 0.9:
        bub(S, A(0.4, -2.0, 3.2), t, 6, 0, 0.3, 4.5, 1.6, size=1.3)
    key(S, 'kc', A(4, -7, 6), A(0.4, -2, 2), 2000)
    key(S, 'kw', A(3.5, -0.5, 2.6), A(0.4, -1.8, 2.2), 420)
    cam(S, A(lerp(2.6, 2.2, k), lerp(-5.0, -4.6, k), 2.2), A(0.4, -1.9, 2.15), 44)


def rook_dark(S, k, t, lt):
    """Rook stands a few steps off in the black water, hat in hand, watching him. He says nothing."""
    A = deep(S, 'dark')
    uw(S, 'lem', A(0.4, 0.2, 0), PI + 0.3, P('stand', aL=(0.5, 0.6, 0.6), aR=(0.5, 0.6, 0.6), head=(-0.25, 0.3 * math.sin(lt * 1.9))), t, face='scared')
    lamp_off(S)
    rook_uw(S, A(-2.9, -3.4, 0), -0.75, P('stand', aL=(0.5, 0.3, 1.5, 0.6), aR=(0.3, 0.2, 0.3), head=(0.12, -0.25)), 'sad', t)
    key(S, 'kw', A(-4.6, -7.5, 3.2), A(-2.9, -3.4, 2.3), 900)
    key(S, 'kc', A(5, -6, 7), A(0.4, 0.2, 2), 2400)
    cam(S, A(lerp(-4.0, -3.7, k), lerp(-8.0, -7.5, k), 2.2), A(-1.9, -2.4, 2.3), 36)


def lem_side(S, k, t, lt):
    """On the roof of the structure he lies on his side, knees drawn up. With prm 'yua' a helmet lamp finds him."""
    A = deep(S, 'dark')
    found = S['prm'].get('yua')
    lying(S, 'lem', A, -1.6, t, 0.0 if found else max(0.0, 0.6 - k), 'closed' if found else 'tired')
    lamp_off(S)
    if not found and k < 0.5:
        bub(S, A(1.1, 2.4, TOP + 0.8), t, 3, 0, 0.2, 4.0, 0.7, size=0.9)
    key(S, 'kc', A(-4, -4, 8), A(0, 2.8, TOP), 2400)
    key(S, 'kw', A(4, -2, 4.2), A(0, 2.8, TOP + 0.4), 300)
    if found:
        bell_at(S, (1.5, 6.5, 10.5), t, 4200)
        e = ease(k)
        uw(S, 'yua', A(lerp(1.9, 1.5, e), lerp(4.9, 4.5, e), TOP + lerp(0.5, 0.0, e)), 0.75, P('stand', aL=(1.1, 0.4, 0.5), aR=(1.3, 0.2, 0.4), lL=(0.5, 0.8), lR=(0.2, 0.5), lean=0.35,
           head=(0.3, 0.0)), t)
        lamp(S, 'yua', 5200)
        rope(S, 1, back_of(S, 'yua'), (1.4, 6.4, 7.3), 0.6, t, 0.2)
        bub(S, A(1.6, 4.6, TOP + 3.4), t, 6, 0, 0.3, 4.0, 2.2, size=1.2)
    cam(S, A(lerp(1.1, 0.7, k), lerp(-1.6, -1.2, k), lerp(5.4, 5.1, k)), A(0.2, 2.7, TOP + 0.4), 34)


def rov_launch(S, k, t, lt):
    """The ROV drives down through mid-water on its tether, lamps cutting the murk."""
    A = deep(S, 'dark')
    z = lerp(36, 30.5, ease(k))
    p = (lerp(-3, 0.5, k), 2.0, z)
    rov_at(S, p, 2.5, t, 16000, -0.38)
    rope(S, 2, (p[0] + 0.3, p[1] + 0.5, p[2] + 0.8), (p[0] - 5, p[1] + 9, p[2] + 22), 1.0, t, 0.5)
    bub(S, A(p[0], p[1] + 0.8, p[2] + 0.9), t, 10, 0, 0.9, 6.0, 3.0, size=1.3)
    key(S, 'kc', A(6, -8, z + 4), A(p[0], p[1], z), 5200)
    key(S, 'kw', A(-5, -6, z - 3), A(p[0], p[1], z), 1300)
    cam(S, A(lerp(4.6, 4.0, k), lerp(-5.6, -5.0, k), z - 2.2), A(p[0], p[1], z + 0.3), 46, 0.04 * math.sin(t * 1.3))


def yua_drop(S, k, t, lt):
    """Low on the roof beside the still diver: Yuasa comes down out of the bell lights, lamp blazing."""
    A = deep(S, 'dim')
    bell_at(S, (1.5, 6.5, 10.8), t, 5200)
    lying(S, 'lem', A, -1.6, t, 0.0, 'closed')
    lamp_off(S)
    e = ease(k)
    z = lerp(6.6, 4.2, e)
    uw(S, 'yua', A(1.3, 5.0, z), 0.5, swimmer(t, 0.5, aL=(1.3, 0.5, 0.3), aR=(1.5, 0.4, 0.3), head=(0.45, 0.0)), t, pitch=0.5)
    lamp(S, 'yua', 6000)
    rope(S, 1, back_of(S, 'yua'), (1.5, 6.4, 7.6), 0.3, t, 0.2, 8)
    bub(S, A(1.3, 5.0, z + 3.2), t, 8, 0, 0.3, 4.5, 2.6, size=1.3)
    key(S, 'kc', A(-6, -3, 6), A(0, 3, 3.5), 2600)
    key(S, 'kw', A(-3, -1, 3.4), A(0.2, 2.6, 3.0), 500)
    cam(S, A(lerp(-3.8, -3.4, k), lerp(-0.6, -0.3, k), 3.2), A(0.5, 3.9, lerp(5.0, 4.5, e)), 24, 0.02 * math.sin(t * 5))


# ---------------------------------------------------------------- long shots: how, and after
def bay_night(S):
    A = show(S, 'bay')
    sky(S, '05080E')
    return A


def rook_quad(S, k, t, lt):
    """Rook raps a knuckle on the rack of gas cylinders: a body does not hold much."""
    A = bay_night(S)
    kn = max(0.0, math.sin(lt * 7.5)) if lt < 1.7 else 0.0
    S['rook'].place(A(-3.9, 4.2, 0), 0.35)
    S['rook'].apply(P('stand', aL=(0.5, 1.25 + 0.2 * kn, 0.5 - 0.3 * kn), aR=(0.2, 0.3, 0.5), head=(0.0, -0.7 + 0.6 * ease((lt - 1.7) / 0.5))))
    S['face']['rook'] = 'calm'
    key(S, 'kw', A(-2.0, -1.0, 3.6), A(-4.4, 4.4, 2.4), 900)
    cam(S, A(lerp(-3.2, -3.5, k), lerp(-1.6, -1.2, k), 2.2), A(-4.9, 4.6, 2.2), 32)


def rook_count(S, k, t, lt):
    """By the umbilical reel Rook counts the reports off on his feathers."""
    A = bay_night(S)
    n = min(3, int(lt / 1.0))
    bob = max(0.0, math.sin((lt % 1.0) * PI * 2)) * 0.25
    S['rook'].place(A(-1.2, 2.6, 0), -0.35)
    S['rook'].apply(P('stand', aR=(1.15 + 0.12 * n, 0.45, 2.0 - bob, -0.4), aL=(0.9, 0.2, 1.7 - bob * 0.6, 0.9), head=(0.18 - 0.2 * bob, -0.25)))
    S['face']['rook'] = 'deadpan'
    key(S, 'kw', A(1.5, -2.0, 3.2), A(-1.2, 2.6, 2.4), 480)
    cam(S, A(lerp(0.4, 0.1, k), lerp(-2.6, -2.2, k), 2.3), A(-1.3, 2.7, 2.3), 34)


def rook_shrug(S, k, t, lt):
    """Morning by the moonpool: Rook shrugs. Nobody can say for sure."""
    A = morning(S)
    e = math.sin(PI * ease(lt / 1.6)) if lt < 1.6 else 0.0
    S['rook'].place(A(0.2, -0.6, 0), -0.25)
    S['rook'].apply(blend(P('stand', head=(0.0, 0.2)), P('shrug', head=(-0.1, -0.15)), e))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(-1.6, -1.2, k), lerp(-6.4, -5.8, k), 2.7), A(0.6, 0.2, 2.2), 40)


def back_work(S, k, t, lt):
    """Three weeks on: the same structure, floodlit. The diver in blue looks up from the valves and waves; Rook sits on the roof."""
    A = deep(S, 'work')
    bell_at(S, (-4.5, 8.5, 9.5), t)
    s = math.sin(t * 3.0)
    uw(S, 'yua', A(-1.75, -0.05, 0), PI + 0.12, P('stand', aL=(1.35 + 0.15 * s, 0.1, 0.5), aR=(1.35 - 0.15 * s, 0.1, 0.5), head=(0.12, 0.1 * s), lean=0.12), t, ph=1.4)
    w = ease((lt - 0.5) / 0.6)
    uw(S, 'lem', A(0.75, -0.25, 0), lerp(PI - 0.1, 0.9, w), blend(P('stand', aL=(1.35, 0.1, 0.5), aR=(1.35, 0.1, 0.5), head=(0.12, 0.0), lean=0.12),
       P('stand', aR=(2.6, 0.5 + 0.25 * math.sin(t * 8), 0.3), aL=(0.3, 0.3, 0.4), head=(-0.35, 0.0)), w), t)
    for i, who in enumerate(('lem', 'yua')):
        lamp(S, who, 2500)
        rope(S, i, back_of(S, who), (-4.2 - 0.6 * i, 8.0, 6.2), 1.2, t, 0.25)
    S['wheels'][0].rotation_euler = (0, -t * 1.2, 0)
    bub(S, A(0.75, -0.2, 3.2), t, 6, 0, 0.3, 5.0, 1.8, size=1.2)
    bub(S, A(-1.75, -0.05, 3.2), t, 6, 8, 0.3, 5.0, 1.6, seed=4, size=1.2)
    S['rook'].place(A(2.35, 0.75, TOP - 0.47), 0.0)
    S['rook'].apply(P('sit', aR=(0.2, 1.9, 1.6, -1.5), head=(0.3, 0.45), lift=-0.5, lean=0.15))
    S['face']['rook'], S['helm'] = 'warm', True
    key(S, 'kw', A(6, -4, 5.5), A(2.3, 0.7, 4.2), 1500)
    cam(S, A(lerp(5.4, 4.8, k), lerp(-6.6, -6.0, k), lerp(5.6, 5.2, k)), A(0.9, 0.5, 2.3), 30)


def two_friends(S, k, t, lt):
    """Morning in the bay: the three divers, helmets off, beside the bell."""
    A = morning(S)
    S['chris'].place(A(0.1, 1.3, 0), 0.15)
    S['chris'].apply(P('stand', aL=(0.1, 0.2, 0.3), aR=(0.2, 0.2, 0.4), head=(-0.02, 0.25 + 0.1 * math.sin(t * 1.3))))
    S['face']['chris'] = 'happy'
    S['dave'].place(A(1.25, 1.45, 0), -0.1)
    S['dave'].apply(P('stand', aL=(0.5, 1.15, 0.5), aR=(0.1, 0.2, 0.3), head=(0.0, -0.3)))
    S['face']['dave'] = 'happy'
    S['dunc'].place(A(-1.2, 1.5, 0), 0.35)
    S['dunc'].apply(P('cross', head=(0.0, 0.3)))
    S['face']['dunc'] = 'happy'
    cam(S, A(lerp(-2.6, -2.0, k), lerp(-5.4, -4.8, k), 2.0), A(0.3, 1.4, 2.25), 34)


HOST |= {'chamber_wide', 'chamber_cu', 'rook_ears', 'bell_stage', 'rook_line', 'bridge_calm', 'bridge_fight', 'bell_drag', 'rook_hatch', 'yua_wait', 'rook_dark',
         'rook_quad', 'rook_count', 'rook_shrug', 'back_work'}
SHOTS3D.update({f.__name__: f for f in (
    chamber_wide, chamber_cu, rook_ears, bell_stage, dunc_tend, rook_line, storm_wide, bridge_calm, bridge_alarm, bridge_fight, bell_drag, go_back,
    dunc_haul, dunc_end, rook_hatch, yua_dragged, yua_climb, yua_wait, lem_switch, rook_dark, lem_side, rov_launch, yua_drop, rook_quad, rook_count,
    rook_shrug, back_work, two_friends)})
for _n in ('fall_back', 'alone_wide', 'bell_away', 'climb', 'rook_sit', 'still_body', 'rov_in', 'rov_pov', 'rook_low'):
    SHOTS3D[_n] = dark_lamp(SHOTS3D[_n])


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: the diver thrown back, the cut line whipping above him, the bell lights leaving; Rook, shocked."""
    A = deep(S, 'dim')
    bell_at(S, (1.6, 9, 8.6), 1.0, 5000)
    uw(S, 'lem', A(-0.6, -1.6, 0.3), 0.3, P('up', aL=(2.4, 0.7, 0.4), aR=(2.0, 0.8, 0.5), lL=(0.9, 0.5), lR=(0.3, 0.9), head=(-0.2, 0.0)), 1.0, pitch=-0.3, face='shock')
    lamp(S, 'lem', 1500)
    rope(S, 1, back_of(S, 'lem'), (1.0, -0.6, 3.6), 0.4, 1.0, 0.3, 8)
    rope(S, 0, (2.2, 3.0, 5.6), (1.8, 8.6, 5.6), -0.6, 1.0, 0.4, 8)
    burst(S, A(1.1, -0.5, 3.7), 0.5, 14, 0, 1.2, seed=5, size=1.0)
    S['spark'].location, S['spark'].scale = (1.0, -0.6, 3.6), (0.8, 0.8, 0.8)
    rook_uw(S, A(-3.6, -2.4, 0), -0.6, P('up', aL=(2.3, 0.6, 1.3), aR=(2.3, 0.6, 1.3), head=(-0.1, 0.2)), 'shocked', 1.0, bubbles=False)
    key(S, 'kc', A(-4, -7, 5), A(-0.6, -1.6, 1.8), 3400)
    key(S, 'kw', A(-5, -7.5, 3), A(-2.4, -2.2, 2.4), 2400)
    cam(S, A(1.6, -9.0, 1.7), A(1.7, -0.6, 2.9), 30)


STILLS['thumb'] = photo_thumb
