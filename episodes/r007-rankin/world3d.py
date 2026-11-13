"""Case 007 in 3D - Lt. Col. William Rankin, 26 July 1959. Sets built for this story only: the dusk sky above the
cloud deck with the thunderhead under it, the cockpit of his jet, the inside of the storm (violet and teal cloud
shelves with blue sheet lightning), the pine woods in North Carolina with a dirt road, and an airfield apron."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(sky=(0, 0, 0), pit=(600, 0, 0), storm=(1200, 0, 0), woods=(0, 800, 0), base=(600, 800, 0))
FAR = (0, 0, -900)
HOST = {'rook_up', 'rook_tarmac', 'rook_walk', 'cockpit_calm', 'rook_gulp', 'rook_fall', 'swell', 'rook_chute', 'rook_zap',
        'rook_watch', 'yo_yo', 'drop_out', 'tree_land', 'road', 'fly_again', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
PILOT = dict(top='A8935A', pants='9A864E', hand='7A5632', boot='2A2420', fore='B49E62')
SKIN = 'D9A27E'
ease = lambda k: (lambda x: x * x * (3 - 2 * x))(max(0.0, min(1.0, k)))


def at(name, x, y, z):
    o = ORG[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def off(loc, yaw, v):
    c, s = math.cos(yaw), math.sin(yaw)
    return (loc[0] + c * v[0] - s * v[1], loc[1] + s * v[0] + c * v[1], loc[2] + v[2])


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


def rod(p0, p1, r, col, parent, **kw):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    rot = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    return add('cylinder', col, tuple((a + b) / 2), rot=tuple(rot), radius=r, depth=d.length, vertices=4, parent=parent, **kw)


def mixc(a, b, k):
    k = max(0.0, min(1.0, k))
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


# ---------------------------------------------------------------- props
def make_jet(r):
    """Single-engine swept-wing jet fighter of the 1950s, no markings. Nose toward local -Y, fuselage centre at the origin."""
    add('cylinder', 'B4B9C4', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.78, depth=9.0, vertices=8, parent=r, rough=0.5)
    add('cone', 'B4B9C4', (0, -5.6, 0), rot=(PI / 2, 0, 0), radius1=0.78, radius2=0.1, depth=2.2, vertices=8, parent=r, rough=0.5)
    add('cylinder', 'FF7A1A', (0, -4.3, 0), rot=(PI / 2, 0, 0), radius=0.8, depth=0.3, vertices=8, parent=r)
    add('cube', '20242B', (0, -4.2, -0.62), scale=(0.95, 1.3, 0.45), size=1, parent=r)
    canopy = add('ico_sphere', '9AD0E8', (0, -2.9, 0.62), scale=(0.5, 1.35, 0.5), radius=1, subdivisions=1, parent=r, rough=0.2, emit=0.5)
    add('cube', '8E94A2', (0, 0.6, 0.86), scale=(1.5, 3.6, 0.16), size=1, parent=r)
    for s in (-1, 1):
        add('cube', 'A9AEBA', (s * 2.7, 1.5, 0.84), rot=(0, 0, s * 0.62), scale=(5.2, 1.9, 0.13), size=1, parent=r)
        add('cube', 'FF7A1A', (s * 4.75, 2.95, 0.84), rot=(0, 0, s * 0.62), scale=(0.7, 1.5, 0.15), size=1, parent=r)
        add('cube', 'A9AEBA', (s * 1.55, 4.6, 0.05), rot=(0, 0, s * 0.55), scale=(2.6, 1.1, 0.1), size=1, parent=r)
    add('cube', 'A9AEBA', (0, 4.2, 1.5), rot=(-0.5, 0, 0), scale=(0.14, 2.2, 2.4), size=1, parent=r)
    add('cylinder', '2A2C34', (0, 4.7, 0), rot=(PI / 2, 0, 0), radius=0.66, depth=0.5, vertices=8, parent=r)
    flame = add('cone', 'FFB060', (0, 6.1, 0), rot=(-PI / 2, 0, 0), radius1=0.5, radius2=0.0, depth=2.4, vertices=6, parent=r, emit=14)
    gear = []
    for x, y in ((0, -3.6), (-1.2, 1.2), (1.2, 1.2)):
        gear.append(add('cylinder', '6A7088', (x, y, -1.25), radius=0.07, depth=1.2, vertices=5, parent=r))
        gear.append(add('cylinder', '191720', (x, y, -1.85), rot=(0, PI / 2, 0), radius=0.34, depth=0.24, vertices=8, parent=r))
    return dict(flame=flame, canopy=canopy, gear=gear)


def make_seat(r):
    add('cube', '3A3F4A', (0, 0.3, 0.95), scale=(0.74, 0.18, 1.6), size=1, parent=r)
    add('cube', '3A3F4A', (0, -0.05, 0.28), scale=(0.74, 0.8, 0.16), size=1, parent=r)
    add('cube', '9A2A20', (0, 0.24, 1.82), scale=(0.5, 0.2, 0.34), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '6A7088', (s * 0.4, 0.42, 0.9), scale=(0.07, 0.07, 2.0), size=1, parent=r)
    add('torus', 'E8C23A', (0, 0.1, 2.08), rot=(PI / 2, 0, 0), major_radius=0.2, minor_radius=0.035, major_segments=8, minor_segments=4, parent=r)
    return add('cone', 'FFC060', (0, 0.3, -0.9), rot=(PI, 0, 0), radius1=0.3, radius2=0.0, depth=2.0, vertices=6, parent=r, emit=20)


def make_chute(r, c1, c2, R, hgt):
    """Round parachute. Origin = the harness point at the shoulders; the canopy sits hgt above it."""
    can = empty((0, 0, hgt), r)
    add('cone', c1, (0, 0, 0), radius1=R, radius2=R * 0.3, depth=R * 0.55, vertices=12, parent=can)
    add('cone', c2, (0, 0, R * 0.275 + R * 0.06), radius1=R * 0.3, radius2=0.0, depth=R * 0.12, vertices=12, parent=can)
    add('cylinder', c2, (0, 0, -R * 0.275 - R * 0.05), radius=R * 1.01, depth=R * 0.1, vertices=12, parent=can)
    for i in range(6):
        a = i * PI / 3 + PI / 12
        add('cube', c2, (math.cos(a) * R * 0.66, math.sin(a) * R * 0.66, 0.02), rot=(0, 0.62, a), scale=(R * 0.8, R * 0.3, 0.06), size=1, parent=can)
    for i in range(8):
        a = i * PI / 4
        rod((math.cos(a) * R, math.sin(a) * R, -R * 0.3), ((1 if math.cos(a) > 0 else -1) * 0.25, 0, -(hgt - 1.0)), 0.02, 'D8D4C8', can)
    for s in (-1, 1):
        rod((s * 0.25, 0, 1.0), (s * 0.4, 0, -0.1), 0.035, 'D8D4C8', r)
    return can


def pilot_head(head):
    out = K.human_head(SKIN, '5A4632')(head)
    add('ico_sphere', 'F0EEE6', (0, 0.05, 0.11), scale=(1.0, 1.06, 0.95), radius=0.335, subdivisions=1, parent=head, rough=0.35)
    add('cube', 'FF7A1A', (0, 0.05, 0.31), scale=(0.1, 0.62, 0.1), size=1, parent=head)
    add('cube', '2A2C34', (0, -0.22, 0.26), rot=(0.5, 0, 0), scale=(0.52, 0.2, 0.1), size=1, parent=head)
    for s in (-1, 1):
        add('cylinder', '2A2C34', (s * 0.31, 0.0, -0.02), rot=(0, PI / 2, 0), radius=0.13, depth=0.08, vertices=8, parent=head)
    mask = [add('cube', '5A6658', (0, -0.3, -0.1), scale=(0.24, 0.16, 0.2), size=1, parent=head),
            add('cylinder', '3A4238', (0.06, -0.33, -0.34), rot=(0.2, 0, 0), radius=0.06, depth=0.36, vertices=6, parent=head)]
    out['mask'] = mask
    return out


def make_watch(parent, loc, s=1.0, rot=(0, 0, 0)):
    w = empty(loc, parent, rot)
    add('cylinder', 'D8DCE8', (0, 0, 0), radius=0.1, depth=0.05, vertices=10, parent=w, rough=0.25)
    add('cylinder', 'F4EEDF', (0, 0, 0.03), radius=0.08, depth=0.02, vertices=10, parent=w, emit=0.6)
    add('cube', '0E0D14', (0, 0.03, 0.045), scale=(0.012, 0.07, 0.01), size=1, parent=w)
    add('cube', '0E0D14', (-0.025, -0.012, 0.045), rot=(0, 0, 1.1), scale=(0.012, 0.055, 0.01), size=1, parent=w)
    add('cube', '5A3A24', (0, 0, -0.01), scale=(0.11, 0.3, 0.03), size=1, parent=w)
    w.scale = (s, s, s)
    return w


def make_lever(r):
    """The emergency power handle: a yellow and black T-grip on a steel stem."""
    add('cylinder', 'C8CCD8', (0, 0, 0.16), radius=0.03, depth=0.32, vertices=6, parent=r, rough=0.25)
    add('cylinder', 'E8C23A', (0, 0, 0.34), rot=(0, PI / 2, 0), radius=0.055, depth=0.34, vertices=8, parent=r, rough=0.4, emit=0.3)
    for s in (-1, 1):
        add('cylinder', '191720', (s * 0.09, 0, 0.34), rot=(0, PI / 2, 0), radius=0.058, depth=0.05, vertices=8, parent=r)


# ---------------------------------------------------------------- sets
def set_sky(r):
    add('circle', '3A2A5A', (0, 0, -48), radius=900, vertices=24, fill_type='NGON', parent=r)
    cols = ('B8789A', '8A5C8E', 'D89A8A', '6E4A80', 'A86A94')
    for i in range(110):
        a = i * 2.399
        d = 24 + (i * 37 % 520)
        add('ico_sphere', cols[i % 5], (math.cos(a) * d, math.sin(a) * d, -38 - (i % 4) * 2), scale=(1, 1, 0.34), radius=16 + (i * 7 % 22),
            subdivisions=1, parent=r, emit=0.12)
    add('cylinder', 'F08A4A', (0, 0, -30), radius=820, depth=60, vertices=24, end_fill_type='NOTHING', parent=r, emit=1.6)
    add('cylinder', 'B0508A', (0, 0, 28), radius=830, depth=60, vertices=24, end_fill_type='NOTHING', parent=r, emit=0.7)
    add('cylinder', '5A3A8A', (0, 0, 92), radius=840, depth=70, vertices=24, end_fill_type='NOTHING', parent=r, emit=0.45)
    add('ico_sphere', 'FFD080', (-520, -560, -6), radius=44, subdivisions=2, parent=r, emit=9)
    for i in range(40):
        az, el = i * 2.399, 0.35 + ((i * 0.618) % 1) * 1.1
        add('ico_sphere', 'FFFFFF', (math.cos(az) * math.cos(el) * 600, math.sin(az) * math.cos(el) * 600, math.sin(el) * 600), radius=1.3 + (i % 3) * 0.6,
            subdivisions=1, parent=r, emit=8)
    anvil = empty((0, -140, -40), r)
    tcols = ('4A3A6A', '5E4878', '7A5A88', 'A0708E', 'C88A8E', 'E8A890')
    for i in range(22):
        lvl = min(5, i // 4)
        add('ico_sphere', tcols[lvl], (math.sin(i * 1.9) * (26 - lvl * 2), math.cos(i * 2.3) * (22 - lvl * 2), 2 + i * 1.25), scale=(1, 1, 0.7),
            radius=17 - lvl * 1.1, subdivisions=2, parent=anvil, emit=0.1 + 0.05 * lvl)
    for i in range(14):
        a = i * PI / 7
        add('ico_sphere', ('E8A890', 'D8949A')[i % 2], (math.cos(a) * (34 + (i % 3) * 9), math.sin(a) * (30 + (i % 2) * 10), 27 + (i % 3)), scale=(1, 1, 0.22),
            radius=22 + (i % 3) * 4, subdivisions=2, parent=anvil, emit=0.3)
    tfl = add('ico_sphere', 'CFE0FF', (4, 6, 22), radius=10, subdivisions=1, parent=anvil, emit=40)
    wisps = [add('ico_sphere', ('E8B8B0', 'C89AB0')[i % 2], FAR, scale=(1, 1, 0.3), radius=2.2 + (i % 3) * 0.8, subdivisions=1, emit=0.25) for i in range(10)]
    aim = empty((0, 0, 0), r)
    sun = light((-520, -560, 40), 3.6, 'FFB070', kind='SUN', target=aim, parent=r)
    light((300, 300, 200), 2.0, '8A7AE0', kind='SUN', target=aim, parent=r)
    sfl = light((0, -100, 300), 0.0, 'FFF0D0', kind='SUN', target=aim, parent=r)
    return dict(anvil=anvil, tfl=tfl, wisps=wisps, ssun=sun, sflash=sfl)


def set_pit(r):
    add('cube', '2A2E36', (0, 0, -0.1), scale=(2.3, 6, 0.2), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '3E444E', (s * 1.1, 0, 0.85), scale=(0.14, 6, 1.7), size=1, parent=r)
        add('cube', '4A5260', (s * 0.86, -0.4, 1.02), scale=(0.42, 2.8, 0.18), size=1, parent=r)
        for j in range(5):
            add('cube', ('E8C23A', 'C8CCD8', '9A2A20')[j % 3], (s * 0.86, -1.3 + j * 0.42, 1.13), scale=(0.1, 0.16, 0.06), size=1, parent=r, emit=0.4)
    add('cube', '20242B', (0, -1.9, 1.7), scale=(2.1, 0.22, 1.25), size=1, parent=r)
    add('cube', '15181E', (0, -1.75, 2.38), rot=(0.3, 0, 0), scale=(2.2, 0.6, 0.08), size=1, parent=r)
    needles = []
    for i, (x, z) in enumerate(((-0.62, 2.0), (-0.2, 2.0), (0.2, 2.0), (-0.62, 1.55), (-0.2, 1.55), (0.2, 1.55), (0.62, 1.55))):
        add('cylinder', '6A7088', (x, -1.77, z), rot=(PI / 2, 0, 0), radius=0.185, depth=0.05, vertices=12, parent=r, rough=0.3)
        add('cylinder', '0B0F18', (x, -1.74, z), rot=(PI / 2, 0, 0), radius=0.155, depth=0.05, vertices=12, parent=r)
        n = empty((x, -1.7, z), r)
        add('cube', 'F4EEDF', (0, 0, 0.065), scale=(0.022, 0.012, 0.13), size=1, parent=n, emit=1.5)
        needles.append(n)
    fire_off = add('cube', 'B02418', (0.62, -1.76, 2.02), scale=(0.36, 0.06, 0.22), size=1, parent=r, emit=2.5)
    fire_on = add('cube', 'FF2A1A', (0.62, -1.75, 2.02), scale=(0.36, 0.07, 0.22), size=1, parent=r, emit=40)
    firel = light((0.4, -1.2, 2.1), 0.0, 'FF3020', kind='POINT', parent=r)
    add('cylinder', '191720', (0, -0.95, 0.75), rot=(-0.2, 0, 0), radius=0.05, depth=1.3, vertices=6, parent=r)
    add('ico_sphere', '2E2E34', (0, -1.08, 1.4), radius=0.1, subdivisions=1, parent=r)
    add('cube', '15181E', (-0.86, -0.7, 1.12), scale=(0.2, 0.2, 0.08), size=1, parent=r)
    for y in (-1.75, 0.6, 1.7):
        pts = ((-1.1, y, 1.7), (-0.8, y, 2.75), (0, y, 3.05), (0.8, y, 2.75), (1.1, y, 1.7))
        for p0, p1 in zip(pts, pts[1:]):
            rod(p0, p1, 0.06, '5A6270', r)
    rod((0, -1.75, 3.05), (0, 1.7, 3.05), 0.05, '5A6270', r)
    add('cube', '3E444E', (0, 2.4, 1.4), scale=(2.3, 0.3, 2.8), size=1, parent=r)
    cols = ('B8789A', '8A5C8E', 'D89A8A', '6E4A80')
    for i in range(46):
        a = i * 2.399
        d = 40 + (i * 29 % 240)
        add('ico_sphere', cols[i % 4], (math.cos(a) * d, math.sin(a) * d, -22 - (i % 4) * 2), scale=(1, 1, 0.35), radius=14 + (i * 5 % 16), subdivisions=1,
            parent=r, emit=0.15)
    for i in range(10):
        add('ico_sphere', ('5E4878', '7A5A88', 'C88A8E')[i % 3], (-10 + math.sin(i * 2.1) * 16, -70 + math.cos(i * 1.7) * 12, -20 + i * 1.6), scale=(1, 1, 0.7),
            radius=12 - i * 0.5, subdivisions=2, parent=r, emit=0.2)
    add('cylinder', 'F08A4A', (0, 0, -18), radius=520, depth=40, vertices=20, end_fill_type='NOTHING', parent=r, emit=1.6)
    add('cylinder', 'B0508A', (0, 0, 22), radius=525, depth=44, vertices=20, end_fill_type='NOTHING', parent=r, emit=0.7)
    aim = empty((0, 0, 2), r)
    key = light((-5, -4, 4.5), 1400, 'FFB070', 3.0, aim, parent=r)
    light((3.5, 1, 5), 420, '9A8AF0', 3.0, aim, parent=r)
    paim = empty((0.2, -1.9, 1.8), r)
    light((0.3, -0.7, 2.5), 45, 'FFD9A0', 0.8, paim, parent=r)
    return dict(needles=needles, fire_on=fire_on, fire_off=fire_off, firel=firel, pkey=key)


def set_storm(r):
    lumps = []
    cols = ('2B2148', '1D3644', '3A2C5E', '16283A', '34224E')
    for i in range(64):
        a = -0.3 + ((i * 0.618) % 1) * (PI + 0.6)
        rad = 9 + (i * 5 % 11)
        d = 36 + rad * 1.5 + (i * 17 % 34)
        z = -150 + (i * 37 % 300)
        o = add('ico_sphere', cols[i % 5], (math.cos(a) * d, math.sin(a) * d + 6, z), scale=(1.5, 1.2, 0.42), radius=rad, subdivisions=1, parent=r, emit=0.55)
        lumps.append((o, z))
    sheets = []
    for i in range(3):
        g = empty((0, 0, -500), r)
        add('cube', '4A9CFF', (0, 0, 0), scale=(11, 0.9, 80), size=1, parent=g, emit=5)
        for j in range(7):
            add('cube', 'CFE8FF', (-5.5 + (j % 2) * 11 + math.sin(j * 2.2) * 1.5, 0, -33 + j * 11), rot=(0, 0.6 * (1 if j % 2 else -1), 0), scale=(4.5, 1.0, 9), size=1,
                parent=g, emit=9)
        l = light((0, -3, 0), 0.0, '7AB8FF', kind='POINT', parent=g)
        sheets.append((g, l))
    aim = empty((0, 0, 3), r)
    key = light((-12, -16, 24), 24000, '9AE8DC', 10.0, aim, parent=r)
    light((14, -14, -6), 6000, '8A6AE0', 8.0, aim, parent=r)
    light((7, 9, 8), 3200, 'FF7A1A', 4.0, aim, parent=r)
    fl = light((30, -40, 50), 0.0, 'BFD8FF', kind='SUN', target=aim, parent=r)
    return dict(lumps=lumps, sheets=sheets, skey=key, stflash=fl)


def set_woods(r):
    add('plane', '16281E', (0, 0, 0), size=700, parent=r)
    add('cube', '4E3E2A', (0, -16, 0.03), scale=(400, 6.5, 0.06), size=1, parent=r)
    for sy in (-1, 1):
        add('cube', '3A2E20', (0, -16 + sy * 1.4, 0.05), scale=(400, 0.7, 0.06), size=1, parent=r)
    tcol = ('1E3A2A', '24443A', '183024', '2A4A34')
    k = 0
    for i in range(120):
        x = -70 + (i * 61.7) % 140
        y = -44 + (i * 37.3) % 120
        if (x * x + (y + 1) ** 2) < 60 or -22 < y < -10 or (abs(x - 2.6) < 3 and abs(y - 3.2) < 3):
            continue
        hgt = 9 + (i * 7 % 8)
        add('cylinder', '3A2A1E', (x, y, hgt * 0.2), radius=0.32, depth=hgt * 0.4, vertices=6, parent=r)
        for j in range(3):
            add('cone', tcol[(i + j) % 4], (x, y, hgt * (0.42 + j * 0.24)), radius1=3.0 - j * 0.75, radius2=0.25, depth=hgt * 0.42, vertices=7, parent=r)
        k += 1
    x, y, hgt = 2.6, 3.2, 15
    add('cylinder', '3A2A1E', (x, y, hgt * 0.25), radius=0.42, depth=hgt * 0.5, vertices=6, parent=r)
    for j in range(4):
        add('cone', tcol[j % 4], (x, y, hgt * (0.4 + j * 0.2)), radius1=3.6 - j * 0.75, radius2=0.25, depth=hgt * 0.36, vertices=7, parent=r)
    for i in range(9):
        add('ico_sphere', '2A3A30', (-6 + i * 1.7 + math.sin(i * 3) * 0.8, -4.5 + math.cos(i * 2) * 3.5, 0.2), scale=(1, 1.2, 0.5), radius=0.4 + 0.15 * (i % 3),
            subdivisions=1, parent=r)
    for i in range(34):
        a = i * 2.399
        d = 10 + (i * 23 % 150)
        add('ico_sphere', ('1C2436', '252E44', '161C2C')[i % 3], (math.cos(a) * d, math.sin(a) * d, 74 + (i % 4) * 4), scale=(1, 1, 0.36), radius=22 + (i * 7 % 18),
            subdivisions=1, parent=r, emit=0.3)
    car = empty((-60, -16, 0), r)
    add('cube', '7A2A2A', (0, 0, 0.8), scale=(4.6, 1.9, 0.75), size=1, parent=car, rough=0.4)
    add('cube', '8E3434', (-0.4, 0, 1.45), scale=(2.3, 1.7, 0.7), size=1, parent=car, rough=0.4)
    add('cube', 'CFE0FF', (-0.4, 0, 1.5), scale=(2.32, 1.5, 0.42), size=1, parent=car, emit=0.3)
    add('cube', 'C8CCD8', (2.33, 0, 0.62), scale=(0.1, 1.95, 0.16), size=1, parent=car, rough=0.2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', '0E0D14', (sx * 1.45, sy * 0.95, 0.42), rot=(PI / 2, 0, 0), radius=0.42, depth=0.26, vertices=10, parent=car)
    for sy in (-1, 1):
        add('ico_sphere', 'FFF0C0', (2.32, sy * 0.66, 0.9), radius=0.19, subdivisions=1, parent=car, emit=60)
    caim = empty((30, 0, 0.8), car)
    light((2.5, 0, 0.95), 26000, 'FFE8B0', kind='SPOT', spot=1.1, target=caim, parent=car)
    aim = empty((0, 0, 2), r)
    light((-80, -60, 90), 2.6, '7AA0E0', kind='SUN', target=aim, parent=r)
    light((6, -7, 6), 1800, 'FF7A1A', 3.0, aim, parent=r)
    light((-7, -10, 5), 1600, '9AC0F0', 5.0, aim, parent=r)
    raim = empty((4.5, -13, 2), r)
    light((10, -10, 5), 1500, 'FF7A1A', 3.0, raim, parent=r)
    light((9, -21, 4), 1100, '9AC0F0', 4.0, raim, parent=r)
    wfl = light((40, 40, 80), 0.0, 'BFD8FF', kind='SUN', target=aim, parent=r)
    return dict(car=car, wflash=wfl)


def set_base(r):
    add('plane', '9A968C', (0, 0, 0), size=900, parent=r)
    add('cube', '4A4A52', (0, -70, 0.02), scale=(800, 30, 0.04), size=1, parent=r)
    for i in range(-12, 13):
        add('cube', 'F4EEDF', (i * 16, -70, 0.05), scale=(8, 0.7, 0.03), size=1, parent=r)
    for i in range(-6, 7):
        add('cube', 'E8C23A', (i * 9, -7, 0.03), scale=(5, 0.3, 0.03), size=1, parent=r)
    add('cylinder', '7E848E', (-30, 44, 0), rot=(0, PI / 2, 0), radius=15, depth=44, vertices=14, parent=r)
    add('cube', '2A2E36', (-30, 28.6, 5), scale=(30, 0.5, 10), size=1, parent=r)
    add('cube', 'FF7A1A', (-30, 28.3, 11.2), scale=(44, 0.4, 0.9), size=1, parent=r)
    add('cube', 'A8ACB4', (26, 40, 9), scale=(6, 6, 18), size=1, parent=r)
    add('cube', '2A2E36', (26, 40, 19.5), scale=(9, 9, 3.2), size=1, parent=r)
    add('cube', 'FFD080', (26, 40, 19.6), scale=(9.1, 9.1, 1.6), size=1, parent=r, emit=2.0)
    add('cube', 'A8ACB4', (26, 40, 21.4), scale=(10, 10, 0.5), size=1, parent=r)
    add('cylinder', '9A2A20', (26, 40, 24), radius=0.12, depth=5, vertices=5, parent=r)
    for i in range(12):
        add('ico_sphere', '3A8AFF', (-44 + i * 8, -52, 0.25), radius=0.25, subdivisions=1, parent=r, emit=12)
    for i in range(22):
        add('ico_sphere', ('4A5A44', '3E4E3C')[i % 2], (-330 + i * 31, 260 + (i % 3) * 20, 8), scale=(1, 1, 0.6), radius=18 + i % 4 * 3, subdivisions=1, parent=r)
    add('cube', '5A6270', (11, 16, 1.2), scale=(5, 2.4, 2.4), size=1, parent=r)
    add('cylinder', 'C8CCD8', (11, 16, 2.9), rot=(0, PI / 2, 0), radius=1.3, depth=5.4, vertices=10, parent=r, rough=0.4)
    aim = empty((0, 0, 2), r)
    sun = light((-90, -70, 40), 3.8, 'FFC890', kind='SUN', target=aim, parent=r)
    light((7, -6, 5), 2400, 'FF7A1A', 3.0, aim, parent=r)
    light((-6, -9, 3), 500, '9AB8E8', 5.0, aim, parent=r)
    return dict(bsun=sun)


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('sky', set_sky), ('pit', set_pit), ('storm', set_storm), ('woods', set_woods), ('base', set_base)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['pilot'] = K.Rig(PILOT, pilot_head)
    pb = S['pilot'].body
    S['belly'] = add('ico_sphere', 'A8935A', (0, -0.16, 0.42), radius=0.36, subdivisions=1, parent=pb)
    for s in (-1, 1):
        add('cube', 'E8E4D8', (s * 0.2, -0.02, 0.62), rot=(0, s * 0.12, 0), scale=(0.09, 0.76, 0.95), size=1, parent=pb)
    add('cube', 'E8E4D8', (0, -0.03, 0.25), scale=(0.72, 0.74, 0.09), size=1, parent=pb)
    S['bare'] = add('ico_sphere', SKIN, (0, 0, -0.5), radius=0.125, subdivisions=1, parent=S['pilot'].el[0])
    S['jets'] = []
    for _ in range(2):
        j = empty()
        S['jets'].append((j, make_jet(j)))
    S['seat'] = empty()
    S['seatfl'] = make_seat(S['seat'])
    S['chute'], S['rchute'] = empty(), empty()
    S['can'] = make_chute(S['chute'], 'F4EEDF', 'E8742A', 4.0, 7.5)
    S['rcan'] = make_chute(S['rchute'], '3E4658', 'FF7A1A', 2.3, 5.0)
    S['glove'] = K.Hand('7A5632', 'A8935A', 1.0)
    S['hand'] = K.Hand(SKIN, 'A8935A', 1.0)
    S['hice'] = [add('cone', 'DFF4FF', (x, y, z), rot=(rx, 0, rz), radius1=0.035, radius2=0.0, depth=0.16, vertices=4, parent=S['hand'].root, emit=0.7)
                 for x, y, z, rx, rz in ((-0.1, -0.3, 0.06, 0.2, 0.3), (0.0, -0.42, 0.06, -0.2, 0), (0.08, -0.26, 0.07, 0.3, -0.4), (-0.05, -0.08, 0.07, 0, 0.5),
                                         (0.1, -0.02, 0.07, 0.4, 0.2), (0.0, 0.1, 0.12, 0.1, -0.3), (-0.11, -0.5, 0.05, -0.5, 0.2), (0.11, -0.47, 0.05, -0.4, -0.2),
                                         (0.03, -0.15, 0.07, 0.3, 0.6), (-0.02, 0.3, 0.13, 0.2, 0.1))]
    S['pocket'] = make_watch(None, FAR, 2.6)
    add('cylinder', 'E8C23A', (0, 0.22, 0), rot=(PI / 2, 0, 0), radius=0.012, depth=0.26, vertices=4, parent=S['pocket'], rough=0.3)
    S['lever'] = empty()
    make_lever(S['lever'])
    S['hail'] = [add('ico_sphere', 'E8F4FF', FAR, radius=0.13, subdivisions=1, emit=0.8) for _ in range(36)]
    S['rain'] = [add('cylinder', 'BFE0FF', FAR, radius=0.022, depth=1.7, vertices=3, emit=1.2) for _ in range(70)]
    S['fea'] = [add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4) for _ in range(9)]
    S['smoke'] = [add('ico_sphere', '3A3A44', FAR, radius=0.6, subdivisions=1) for _ in range(10)]
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 2400
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


def reset(S):
    for who in ('rook', 'pilot'):
        S[who].root.parent = None
        S[who].place(FAR)
        S[who].apply(P())
        S[who].root.scale = (1, 1, 1)
    loose = S['hail'] + S['rain'] + S['fea'] + S['smoke'] + S['wisps'] + [S['seat'], S['chute'], S['rchute'], S['lever'], S['glove'].root, S['hand'].root]
    S['pocket'].location, S['pocket'].rotation_euler = FAR, (0, 0, 0)
    loose += [j for j, _ in S['jets']]
    for o in loose:
        o.location = FAR
        o.scale = (1, 1, 1)
        o.rotation_euler = (0, 0, 0)
    for w in S['wisps']:
        w.scale = (1, 1, 0.3)
    for _, d in S['jets']:
        d['flame'].hide_render = False
        d['canopy'].hide_render = False
        for g in d['gear']:
            g.hide_render = True
    S['seatfl'].hide_render = True
    S['can'].scale, S['rcan'].scale = (1, 1, 1), (1, 1, 1)
    S['can'].rotation_euler, S['rcan'].rotation_euler = (0, 0, 0), (0, 0, 0)
    S['glove'].grip(0.2)
    S['hand'].grip(0.2)
    S['anvil'].location = (0, -140, -40)
    S['tfl'].hide_render = True
    S['sflash'].data.energy = 0
    S['ssun'].data.energy = 3.6
    for n in S['needles']:
        n.rotation_euler = (0, 0.9, 0)
    S['fire'] = False
    S['pkey'].data.energy = 1400
    for g, l in S['sheets']:
        g.location = (0, 0, -500)
        g.rotation_euler = (0, 0, 0)
        l.data.energy = 0
    S['stflash'].data.energy = 0
    S['skey'].data.energy = 24000
    S['car'].location = (-60, -16, 0)
    S['wflash'].data.energy = 0
    S['bsun'].data.energy, S['bsun'].data.color = 3.8, K.hexc('FFC890')[:3]
    S['face'] = dict(rook='calm', pilot='calm')
    S['hat_tip'], S['hat_off'] = 0.0, False
    S['mask'], S['bare_on'], S['swell'], S['frost'] = False, False, 0.0, 0.0
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.41) % 1 < 0.035
    ez = dict(calm=0.07, smirk=0.045, deadpan=0.05, shocked=0.13, laugh=0.03, sad=0.06, warm=0.06).get(e, 0.07)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        tilt = dict(smirk=-0.5, deadpan=-0.05, shocked=0.35, laugh=0.3, sad=0.4, warm=0.2).get(e, -0.25)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + (s * tilt if e != 'smirk' or s > 0 else 0.1), s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip = S['hat_tip']
    if S['hat_off']:
        r['hat'].location, r['hat'].rotation_euler = (0.2, 0.0, 0.8 + 0.12 * math.sin(t * 9)), (0.4, 0.3, t * 5)
    else:
        r['hat'].location = (0, 0, 0.27 + (0.13 if e == 'shocked' else 0.0) + tip * 0.1)
        r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.12).get(e, 0.0) + tip * 0.35, 0.07, 0)
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e in ('shocked', 'laugh') else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    k = dict(scared=1.25, shock=1.8, calm=1.0, sad=0.6, happy=0.9, closed=0.1).get(S['face']['pilot'], 1.0)
    for ey in S['pilot'].extra['eyes']:
        ey.scale = (ey.scale[0], ey.scale[1], 0.075 * k)
    for o in S['pilot'].extra['mask']:
        o.hide_render = not S['mask']
    S['bare'].hide_render = not S['bare_on']
    sw = S['swell']
    S['belly'].hide_render = sw <= 0
    S['belly'].scale = (0.75 + 0.45 * sw, 0.7 + 0.55 * sw, 0.8 + 0.3 * sw)
    for i, o in enumerate(S['hice']):
        f = max(0.0, min(1.0, S['frost'] * 1.6 - i * 0.06))
        o.hide_render = f <= 0
        o.scale = (f * 1.4, f * 1.4, f * 1.4)
    fire = S['fire']
    S['fire_on'].hide_render = not fire
    S['fire_off'].hide_render = fire
    S['firel'].data.energy = 900 if fire else 0


# ---------------------------------------------------------------- helpers
HOLD = dict(aL=(2.75, 0.22, 0.35), aR=(2.75, 0.22, 0.35))


def jet(S, i, loc, yaw=0.0, pitch=0.0, roll=0.0, flame=True, canopy=True, gear=False):
    j, d = S['jets'][i]
    j.location, j.rotation_euler = loc, (pitch, roll, yaw)
    d['flame'].hide_render = not flame or gear
    d['canopy'].hide_render = not canopy
    for g in d['gear']:
        g.hide_render = not gear


def hang(S, who, loc, yaw=0.0, sway=(0.0, 0.0), pose=None, open_=1.0, face=None):
    """Hang a character under a parachute. loc = the harness point at the shoulders."""
    ch, can = (S['chute'], S['can']) if who == 'pilot' else (S['rchute'], S['rcan'])
    ch.location, ch.rotation_euler = loc, (sway[0], sway[1], yaw)
    rig = S[who]
    rig.root.parent = ch
    rig.place((0, 0.05, -2.3))
    rig.apply(pose or P('stand', lL=(0.15, 0.2), lR=(-0.1, 0.25), **HOLD))
    o = max(0.05, open_)
    can.scale = (o, o, 1 + (1 - o) * 0.9)
    if face:
        S['face'][who] = face
    if who == 'pilot':
        S['mask'] = True


def storm(S, t, speed, col='0E0A1E', strength=1.0, key=24000):
    """Inside the thunderstorm: the cloud shelves scroll (speed > 0 = he is rising, < 0 = falling)."""
    A = show(S, 'storm')
    for o, z in S['lumps']:
        o.location.z = ((z - speed * t + 150) % 300) - 150
    sky(S, col, strength)
    S['skey'].data.energy = key
    return A


def sheet(S, i, loc, f, yaw=0.0):
    g, l = S['sheets'][i]
    if f <= 0:
        return
    g.location, g.rotation_euler = loc, (0, 0.08 * math.sin(i * 3.0), yaw)
    l.data.energy = 3e5 * f


def flick(lt, at_, d=0.22):
    if not 0 <= lt - at_ < d:
        return 0.0
    f = 1 - (lt - at_) / d
    return f if int((lt - at_) * 30) % 3 != 1 else f * 0.3


def hail(S, org, t, n=24, box=(9, 6, 12), speed=26, slant=0.35, size=1.0, up=False):
    for i in range(n):
        b = S['hail'][i]
        u = ((i * 0.618) % 1 - t * speed / box[2]) % 1
        if up:
            u = 1 - u
        x = ((i * 0.37) % 1 - 0.5) * box[0] + (1 - u) * slant * box[2] * 0.3
        b.location = (org[0] + x, org[1] + ((i * 0.73) % 1 - 0.5) * box[1], org[2] + (u - 0.5) * box[2])
        s = size * (0.7 + ((i * 0.29) % 1))
        b.scale = (s, s, s)


def rain(S, org, t, n=60, box=(10, 7, 12), speed=38, slant=0.25, size=1.0):
    for i in range(n):
        b = S['rain'][i]
        u = ((i * 0.618) % 1 - t * speed / box[2]) % 1
        x = ((i * 0.37) % 1 - 0.5) * box[0] + (1 - u) * slant * box[2]
        b.location = (org[0] + x, org[1] + ((i * 0.73) % 1 - 0.5) * box[1], org[2] + (u - 0.5) * box[2])
        b.rotation_euler = (0, -slant * 0.9, 0)
        b.scale = (size, size, size * (0.7 + ((i * 0.29) % 1)))


def feathers(S, org, t, n=6, down=True, spread=1.0):
    for i in range(n):
        f = S['fea'][i]
        u = (t * 0.6 + i * 0.37) % 1
        a = i * 2.3
        f.location = (org[0] + math.cos(a) * (0.5 + u) * spread, org[1] - 0.5 + math.sin(a) * 0.4, org[2] + (-u * 3.0 if down else u * 2.0) + 0.2 * math.sin(t * 2 + i))
        f.rotation_euler = (t * 1.3 + i, t * 0.9 + i * 2, i)


def smoke(S, org, d, t, n=10, grow=1.0):
    """A trail of dark puffs from org along direction d."""
    for i in range(n):
        u = (i + (t * 6) % 1) / n
        s = (0.5 + 2.2 * u) * grow
        b = S['smoke'][i]
        b.location = (org[0] + d[0] * u + 0.4 * math.sin(i * 2.1 + t * 3) * u, org[1] + d[1] * u, org[2] + d[2] * u + 0.5 * math.sin(i * 1.3) * u)
        b.scale = (s, s, s * 0.8)


def wisps(S, org, t, speed=30, box=(16, 8, 26), back=2.0):
    """Cloud scraps streaking up past a falling body."""
    for i, w in enumerate(S['wisps']):
        u = ((i * 0.618) % 1 + t * speed / box[2]) % 1
        w.location = (org[0] + ((i * 0.37) % 1 - 0.5) * box[0], org[1] + back + ((i * 0.73) % 1) * box[1], org[2] + (u - 0.5) * box[2])


def dusk_sky(S):
    A = show(S, 'sky')
    sky(S, '241A48', 1.0)
    return A


def tumble(S, who, loc, t, rate=5.0, pose=None):
    S[who].place(loc, 0.6 * t, PI / 2 + 0.5 * math.sin(t * rate * 0.7), rate * t * 0.4)
    S[who].apply(pose or P('stand', aL=(1.4 + 0.5 * math.sin(t * 7), 1.1, 0.4), aR=(1.2 - 0.5 * math.sin(t * 6), 1.2, 0.5),
                           lL=(0.5 + 0.4 * math.sin(t * 8), 0.6), lR=(-0.2 - 0.4 * math.sin(t * 8), 0.9), head=(-0.3, 0.0)))


def seated(S, loc, rot=(0, 0, 0), pose=None, fl=False):
    S['seat'].location, S['seat'].rotation_euler = loc, rot
    S['seatfl'].hide_render = not fl
    S['pilot'].root.parent = S['seat']
    S['pilot'].place((0, 0.0, -0.12))
    S['pilot'].apply(pose or P('sit', lean=0.0, head=(0.0, 0.0), aL=(0.75, 0.1, 0.9), aR=(0.9, -0.1, 0.8), lL=(1.35, 1.3), lR=(1.35, 1.3)))


# ---------------------------------------------------------------- shots: hook
def eject_bang(S, k, t, lt):
    A = dusk_sky(S)
    f = flick(lt, 0.0, 0.3)
    S['sflash'].data.energy = 6 * f
    drop = 3.0 * k
    jet(S, 0, A(0, -1.5 * k, -drop), 0.0, 0.16 + 0.1 * k, 0.1 * math.sin(t * 5), flame=False, canopy=False)
    smoke(S, A(0, 4.6 - 1.5 * k, -drop), (0.5, 9, 2.2), t)
    e = 1 - (1 - min(1.0, k * 1.15)) ** 2
    z = lerp(0.3, 5.5, e)
    seated(S, A(0.2 * math.sin(t * 9), -2.6 + 3.2 * e, z), (-0.25 * e, 0.12 * math.sin(t * 7), 0),
           P('sit', lean=0.0, head=(0.25, 0), aL=(2.5, 0.35, 1.3), aR=(2.5, 0.35, 1.3), lL=(1.35, 1.3), lR=(1.35, 1.3)), fl=True)
    S['mask'], S['face']['pilot'] = True, 'scared'
    cam(S, A(5.6, -8.4, 0.4), A(0, -1.0, lerp(0.6, 3.2, e)), 28, 0.1 * math.sin(t * 6))


def fall_in(S, k, t, lt):
    A = dusk_sky(S)
    S['tfl'].hide_render = int(t * 9) % 4 != 0
    z = lerp(13, -2, k)
    tumble(S, 'pilot', A(0.8 * math.sin(t * 2), -140, z), t, 6.0)
    S['mask'], S['face']['pilot'] = True, 'shock'
    wisps(S, A(0, -143, z), t, 26, (14, 6, 22), 8)
    cam(S, A(lerp(4, 2.5, k), -131, lerp(21, 17, k)), A(0, -140, lerp(6, -8, k)), 30, 0.25 * t)


def chute_yank(S, k, t, lt):
    f = flick(lt, 0.05, 0.3)
    A = storm(S, t, 80, mixc('0E0A1E', '6A8AD0', f), 1 + f)
    S['stflash'].data.energy = 4 * f
    sheet(S, 0, (-26, 46, 10), f, 0.3)
    z = lerp(-10, 3, ease(k))
    hang(S, 'pilot', A(0.3 * math.sin(t * 9), 0, z), 0.5, (0.25 * math.sin(t * 7), 0.3 * math.sin(t * 6)),
         P('stand', aL=(2.6, 0.5, 0.3), aR=(2.2, 0.6, 0.8), lL=(0.7 * math.sin(t * 9), 0.6), lR=(-0.7 * math.sin(t * 9), 0.8), head=(-0.4, 0.2 * math.sin(t * 8))), face='shock')
    hail(S, A(0, -2, z + 2), t, 30, (14, 8, 18), 60)
    cam(S, A(6.5, -14.5, -7), A(0, 0, lerp(-3, 8, k)), 24, 0.12 * math.sin(t * 6))


def rook_up(S, k, t, lt):
    A = storm(S, t, 95, '120E26')
    z = lerp(-3.5, 1.2, ease(k))
    kk = math.sin(t * 14)
    hang(S, 'rook', A(0.15 * math.sin(t * 11), 0, z + 2.3), -0.3, (0.2 * math.sin(t * 8), 0.25 * math.sin(t * 7)),
         P('stand', aL=(2.75, 0.22, 0.35), aR=(2.0, 1.0, 0.9), lL=(0.5 * kk, 0.5 + 0.3 * kk), lR=(-0.5 * kk, 0.5 - 0.3 * kk), head=(-0.25, 0.25)), face='shocked')
    feathers(S, A(0, 0, z + 1.6), t, 7)
    rain(S, A(0, 2.5, z + 2), t, 26, (10, 4, 12), -50, 0.15)
    cam(S, A(lerp(2.6, 2.1, k), lerp(-7.2, -6.2, k), z + 0.8), A(0, 0, z + 2.9), 34, 0.1 * math.sin(t * 6))


# ---------------------------------------------------------------- shots: doubt (the airfield at dusk)
def apron(S, day=False):
    A = show(S, 'base')
    if day:
        sky(S, '8EC4EC', 1.0)
        S['bsun'].data.energy, S['bsun'].data.color = 4.4, K.hexc('FFF4E0')[:3]
    else:
        sky(S, 'E89458', 1.0)
    return A


def rook_tarmac(S, k, t, lt):
    A = apron(S)
    jet(S, 0, A(7.5, 10, 2.19), -0.9, -0.05, gear=True)
    S['rook'].place(A(0, 0, 0), -0.25)
    S['rook'].apply(P('cross', head=(0.05, 0.1 + 0.24 * math.sin(t * 4.2) * max(0, 1 - lt / 1.0))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-1.9, -1.4, k), lerp(-6.8, -5.4, k), 0.8), A(0.2, 0, 2.3), 34)


def rook_walk(S, k, t, lt):
    A = apron(S)
    jet(S, 0, A(11, 2.5, 2.19), 0.35, -0.05, gear=True)
    x = lerp(-2.6, 1.4, k)
    pop = ease(lt / 0.3) * (1 - ease((lt - 0.4) / 0.2))
    S['rook'].place(A(x, 0, 0), PI / 2 - 0.25)
    S['rook'].apply(blend(walk(t, 1.9), P('stand', aL=(0.5, 0.45, 2.4, 0.4), aR=(0.5, 0.45, 2.4, 0.4), head=(-0.1, 0)), pop))
    S['face']['rook'] = 'smirk'
    cam(S, A(x - 0.4, -6.6, 0.7), A(x + 0.5, 0.2, 2.0), 32)


# ---------------------------------------------------------------- shots: the flight
def two_jets(S, k, t, lt):
    A = dusk_sky(S)
    S['anvil'].location = (-16, -150, -46)
    S['tfl'].hide_render = int(t * 7) % 5 != 0
    b = math.sin(t * 2.2)
    jet(S, 0, A(0, 0, 0.3 * b), 0.0, 0.02 * b, 0.06 * math.sin(t * 1.7))
    jet(S, 1, A(6.5, -9, -1.4 - 0.3 * b), 0.0, -0.02 * b, -0.05 * math.sin(t * 1.9))
    cam(S, A(lerp(-4.5, -3.5, k), lerp(15, 12.5, k), 3.6), A(3.5, -22, -5), 28)


def cockpit(S, t, look=0.0, fire=False):
    A = show(S, 'pit')
    sky(S, '241A48', 1.0)
    S['fire'] = fire and int(t * 7) % 2 == 0
    if fire:
        S['pkey'].data.energy = 700
        for i, n in enumerate(S['needles']):
            n.rotation_euler = (0, -1.4 + 0.25 * math.sin(t * 30 + i), 0)
    else:
        for i, n in enumerate(S['needles']):
            n.rotation_euler = (0, 0.9 + 0.05 * math.sin(t * 5 + i), 0)
    S['lever'].location = A(-0.86, -0.7, 1.16)
    S['lever'].rotation_euler = (0.25, 0, 0)
    return A


def cockpit_calm(S, k, t, lt):
    A = cockpit(S, t)
    seated(S, A(0, 0.15, 0.32), (0, 0, 0), P('sit', lean=0.02, head=(0.25, 0.55 * ease(k * 1.6)), aL=(0.6, 0.25, 0.9), aR=(0.95, -0.12, 0.75), lL=(1.35, 1.3), lR=(1.35, 1.3)))
    S['mask'] = True
    S['rook'].place(A(-0.6, 1.15, 0.45), -0.35)
    S['rook'].root.scale = (0.82, 0.82, 0.82)
    S['rook'].apply(P('point', aR=(1.0, -0.5, 0.2), head=(0.2, 0.3)))
    S['face']['rook'] = 'smirk'
    cam(S, A(lerp(-2.4, -2.0, k), lerp(-3.5, -3.1, k), 3.5), A(0.3, 0.5, 2.45), 30)


def over_top(S, k, t, lt):
    A = dusk_sky(S)
    S['anvil'].location = (4, -8, -37)
    S['tfl'].hide_render = int(t * 9) % 3 != 0
    y = lerp(8, -8, k)
    jet(S, 0, A(0, y, 0.25 * math.sin(t * 3)), 0.0, 0.0, 0.05 * math.sin(t * 2))
    cam(S, A(-11, y - 12, 7.5), A(0.5, y + 1, -2.5), 26)


def fire_light(S, k, t, lt):
    A = cockpit(S, t, fire=True)
    seated(S, A(0, 0.15, 0.32))
    S['mask'] = True
    j = 0.03 * math.sin(t * 40)
    cam(S, A(lerp(0.2, 0.35, k) + j, lerp(-0.72, -0.95, k), 2.3), A(0.5, -1.8, 1.95), 30, 0.05 * math.sin(t * 9))


def rook_gulp(S, k, t, lt):
    A = cockpit(S, t, fire=True)
    seated(S, A(0, 0.15, 0.32), (0, 0, 0), P('sit', lean=0.02, head=(0.1, -0.3), aL=(0.75, 0.1, 0.9), aR=(0.9, -0.1, 0.8), lL=(1.35, 1.3), lR=(1.35, 1.3)))
    S['mask'] = True
    S['rook'].place(A(0.45, 1.2, 0.45 + 0.1 * abs(math.sin(t * 12))), 0.1)
    S['rook'].root.scale = (0.82, 0.82, 0.82)
    S['rook'].apply(P('shrug', aL=(0.6, 0.9, 1.9, -0.6), aR=(0.6, 0.9, 1.9, -0.6), head=(-0.1, 0.25 * math.sin(t * 9))))
    S['face']['rook'] = 'shocked'
    feathers(S, A(0.5, 1.0, 3.2), t, 3, True, 0.4)
    cam(S, A(lerp(0.78, 0.7, k), lerp(-1.3, -1.0, k), 2.8), A(0.45, 1.2, 2.5), 30, 0.04 * math.sin(t * 8))


def handle_snap(S, k, t, lt):
    A = cockpit(S, t, fire=True)
    brk = 0.42
    g = S['glove']
    if lt < brk:
        pull = ease(lt / brk)
        g.place(A(-0.86, -0.42 + 0.06 * pull, 1.56 + 0.05 * pull + 0.012 * math.sin(t * 50)), (0.9 - 0.25 * pull, 0, 0.05))
        g.grip(0.95)
        S['lever'].rotation_euler = (0.25 - 0.45 * pull, 0, 0)
    else:
        u = ease((lt - brk) / 0.25)
        w = 0.05 * math.sin(t * 11) * (1 - u * 0.5)
        hp = A(-0.78 + 0.12 * u, -0.36 + 0.14 * u, 1.68 + 0.2 * u + w)
        g.place(hp, (0.75 - 0.5 * u, 0.5 * u, 0.2 + 0.5 * u))
        g.grip(0.95)
        S['lever'].location = (hp[0] - 0.02, hp[1] - 0.3, hp[2] - 0.42 + 0.05 * u)
        S['lever'].rotation_euler = (-0.2 + 0.4 * u, 0.5 * u, 0.3 * u)
    cam(S, A(lerp(0.8, 0.7, k), lerp(0.7, 0.55, k), 2.55), A(-0.7, -0.5, 1.6), 40, 0.03 * math.sin(t * 9))


# ---------------------------------------------------------------- shots: the ejection
def seat_away(S, k, t, lt):
    A = dusk_sky(S)
    jet(S, 0, A(-4.5 - 2 * k, -8 - 5 * k, -4.5 - 5 * k), 0.25, 0.55 + 0.25 * k, 0.5 * t, flame=False, canopy=False)
    j = S['jets'][0][0].location
    smoke(S, (j[0] + 0.5, j[1] + 4, j[2] + 2.5), (-2, 7, 6), t, grow=0.8)
    S['seat'].location, S['seat'].rotation_euler = A(2.0 + k, -1.5, 1.4 - 3.0 * k), (t * 4, t * 2.5, 0.4)
    tumble(S, 'pilot', A(0, 0, 0.8 - 1.2 * k), t, 5.0)
    S['mask'], S['face']['pilot'], S['bare_on'] = True, 'shock', True
    wisps(S, A(0, 0, 0), t, 22, (16, 10, 24), 6)
    cam(S, A(lerp(5.5, 4.6, k), lerp(-10.5, -9.2, k), 2.6), A(-1.0, -2.2, -1.0), 31, 0.1 * math.sin(t * 3))


def rook_fall(S, k, t, lt):
    A = dusk_sky(S)
    S['anvil'].location = (0, -140, -52)
    z = lerp(3, 0, k)
    kk = math.sin(t * 16)
    S['rook'].place(A(0, -140, z), 0.25, 1.05 + 0.1 * math.sin(t * 5), 0.15 * math.sin(t * 6))
    S['rook'].apply(P('stand', aL=(1.6, 1.2 + 0.2 * kk, 0.5), aR=(0.3, 1.7, 1.7, -1.4), lL=(-0.5 + 0.3 * kk, 0.8), lR=(-0.3 - 0.3 * kk, 1.0), head=(-0.75, 0.0)))
    S['face']['rook'] = 'shocked'
    feathers(S, A(0, -138, z + 2), t, 6, False)
    wisps(S, A(0, -141, z), t, 34, (12, 6, 22), 7)
    cam(S, A(lerp(1.6, 1.2, k), -145.4, z - 1.6), A(0, -140.6, z + 0.6), 30, 0.12 * math.sin(t * 5))


def frost_hand(S, k, t, lt):
    A = dusk_sky(S)
    S['anvil'].location = (0, -140, -52)
    S['sflash'].data.energy = 2.2
    h_ = S['hand']
    sh = 0.02 * math.sin(t * 45)
    h_.place(A(0.0 + sh, -139.6, 19.75 + 0.03 * math.sin(t * 6)), (-PI / 2 + 0.2, 0.1, PI - 0.35))
    h_.grip(lerp(0.75, 0.25, ease(k * 1.4)))
    S['frost'] = ease(k * 1.25)
    g = S['glove']
    g.place(A(0.9 + 3.0 * k, -138.8, 19.6 + 5.5 * k), (t * 6, t * 4, 1.0))
    g.root.scale = (0.8, 0.5, 0.8)
    g.grip(0.6)
    wisps(S, A(0, -141, 20), t, 30, (9, 5, 14), 8)
    cam(S, A(lerp(0.5, 0.35, k), lerp(-141.4, -141.15, k), 20.15), A(0.0, -139.6, 20.0), 50, 0.04 * math.sin(t * 5))


def swell(S, k, t, lt):
    A = dusk_sky(S)
    S['anvil'].location = (0, -140, -46)
    S['sflash'].data.energy = 1.4
    S['pilot'].place(A(-0.9, -140, 0.25 * math.sin(t * 3)), 0.45, 0.3 + 0.1 * math.sin(t * 2), 0.15 * math.sin(t * 2.4))
    S['pilot'].apply(P('stand', aL=(0.75, -0.15, 1.5, 1.1), aR=(0.75, -0.15, 1.5, 1.1), lL=(0.9, 1.2), lR=(0.7, 1.4), head=(0.35, 0.1), lean=0.3))
    S['mask'], S['face']['pilot'], S['swell'], S['bare_on'] = True, 'closed' if k > 0.3 else 'scared', ease(k * 1.5), True
    S['rook'].place(A(1.2, -139.6, 0.2 + 0.3 * math.sin(t * 3.4)), -0.6, 0.15, 0.2 * math.sin(t * 3))
    kk = math.sin(t * 12)
    S['rook'].apply(P('hat', aL=(1.3, 0.9, 0.6), lL=(0.4 * kk, 0.6), lR=(-0.4 * kk, 0.8), head=(0.15, -0.5)))
    S['face']['rook'] = 'sad'
    wisps(S, A(0, -141, 0), t, 30, (14, 6, 20), 7)
    cam(S, A(lerp(0.7, 0.4, k), lerp(-148.0, -147.0, k), 1.3), A(0.15, -140, 1.75), 30, 0.05 * math.sin(t * 3))


# ---------------------------------------------------------------- shots: inside the storm
def chute_open(S, k, t, lt):
    A = storm(S, t, -45, '120E26')
    o = min(1.15, 0.12 + 1.3 * ease(k * 1.7)) if k < 0.6 else 1 + 0.15 * math.cos((k - 0.6) * 20) * (1 - k)
    jerk = ease(k * 1.7)
    hang(S, 'pilot', A(0, 0, 0.5 * math.sin(t * 5)), 0.4, (0.3 * (1 - jerk) + 0.08 * math.sin(t * 6), 0.1 * math.sin(t * 5)),
         blend(P('stand', aL=(1.5, 1.0, 0.4), aR=(1.3, 1.1, 0.4), lL=(0.9, 0.8), lR=(-0.5, 1.0), head=(-0.5, 0)),
               P('stand', lL=(0.4, 0.3), lR=(0.1, 0.5), head=(-0.5, 0.0), **HOLD), jerk), o, 'shock')
    S['bare_on'] = True
    rain(S, A(0, -2, 3), t, 50, (16, 8, 16), 40, 0.3)
    cam(S, A(lerp(9.5, 8, k), lerp(-15, -13.5, k), 1.5), A(0, 0, 3.6), 26, 0.06 * math.sin(t * 4))


def storm_wide(S, k, t, lt):
    f = flick(lt, 0.35, 0.25)
    A = storm(S, t, -12, mixc('120E26', '3A4A80', f))
    sheet(S, 1, (30, 60, 8), f, -0.4)
    hang(S, 'pilot', A(1.5 * math.sin(t * 1.2), 20, 1.0 * math.sin(t * 1.6)), 0.3, (0.12 * math.sin(t * 2.2), 0.15 * math.sin(t * 1.8)), face='scared')
    S['bare_on'] = True
    rain(S, A(0, 4, 2), t, 70, (30, 16, 22), 36, 0.35, 1.6)
    cam(S, A(lerp(-5, -3, k), lerp(-22, -19, k), lerp(-6, -4, k)), A(1, 20, 4), 30)


def updraft(S, k, t, lt):
    A = storm(S, t, 120, '120E26')
    z = lerp(-16, 2, ease(k))
    hang(S, 'pilot', A(0.5 * math.sin(t * 5), 0, z), 0.5 + t, (0.15 * math.sin(t * 6), 0.15 * math.sin(t * 7)),
         P('stand', lL=(0.5 * math.sin(t * 9), 0.5), lR=(-0.5 * math.sin(t * 9), 0.6), head=(-0.5, 0), **HOLD), face='shock')
    S['bare_on'] = True
    hail(S, A(0, 0, z + 12), t, 30, (16, 12, 20), 50, 0.0, 1.3, up=True)
    cam(S, A(2.5, -4.5, 23), A(0, 0, lerp(-10, 4, k)), 24, 0.3 * t)


def rook_chute(S, k, t, lt):
    A = storm(S, t, 110, '140F2A')
    z = lerp(-9, 4, ease(k))
    kk = math.sin(t * 13)
    hang(S, 'rook', A(0.2 * math.sin(t * 9), 0, z + 2.3), -0.35, (0.18 * math.sin(t * 7), 0.2 * math.sin(t * 8)),
         P('hat', aL=(2.75, 0.22, 0.35), lL=(0.5 * kk, 0.4 + 0.3 * kk), lR=(-0.5 * kk, 0.4 - 0.3 * kk), head=(0.1, 0.3)), face='shocked')
    hang(S, 'pilot', A(-9, 24, z * 0.6 + 7), 1.0, (0.1 * math.sin(t * 5), 0.1), face='scared')
    feathers(S, A(0, 0, z + 1.0), t, 6)
    hail(S, A(0, -1, z + 3), t, 24, (10, 6, 14), 40, 0.1, 1.0, up=True)
    cam(S, A(-2.6, -6.6, z - 1.0), A(0.3, 0, z + 3.4), 24, -0.08 * math.sin(t * 5))


def hail_hit(S, k, t, lt):
    A = storm(S, t, 20, '120E26')
    hang(S, 'pilot', A(0.1 * math.sin(t * 30), 0, 0.08 * math.sin(t * 26)), -0.5, (0.12 * math.sin(t * 9), 0.12 * math.sin(t * 8)),
         P('stand', aL=(2.5, -0.3, 2.0, 0.6), aR=(2.5, -0.3, 2.0, 0.6), lL=(0.9, 1.1), lR=(0.7, 1.3), head=(0.5, 0.0), lean=0.2), face='closed')
    S['bare_on'] = True
    hail(S, A(0, -0.8, -0.3), t, 36, (6, 3.5, 8), 44, 0.25, 1.5)
    cam(S, A(lerp(-3.4, -3.0, k), lerp(-5.4, -4.9, k), -1.9), A(0, 0, -0.3), 36, 0.1 * math.sin(t * 14))


def blue_sheet(S, k, t, lt):
    f = max(flick(lt, 0.0, 0.35), flick(lt, 0.42, 0.3))
    A = storm(S, t, 10, mixc('0E0A1E', '5A7AD8', f), 1 + 1.5 * f)
    S['stflash'].data.energy = 7 * f
    sheet(S, 0, (13, 12, 6), max(f, 0.25), 0.25)
    sheet(S, 1, (-22, 38, 0), flick(lt, 0.42, 0.3) + 0.2, -0.3)
    sheet(S, 2, (38, 52, 12), flick(lt, 0.2, 0.3) + 0.15, 0.5)
    hang(S, 'pilot', A(-4.5 + 0.4 * math.sin(t * 4), 6, -1.5), 0.6, (0.1 * math.sin(t * 5), 0.12 * math.sin(t * 4)),
         P('stand', aL=(2.6, -0.2, 1.8, 0.5), aR=(2.75, 0.22, 0.35), lL=(0.8, 1.0), lR=(0.5, 1.2), head=(0.3, 0.6)), face='shock')
    S['bare_on'] = True
    cam(S, A(lerp(-7, -6, k), lerp(-27, -24, k), -3), A(2.5, 8, 4.5), 28, 0.07 * math.sin(t * 13))


def rook_zap(S, k, t, lt):
    f = 0.5 + 0.5 * math.sin(t * 38)
    A = storm(S, t, 14, mixc('140F2A', '3A56B0', f), 1.0)
    S['stflash'].data.energy = 2.0 * f
    sheet(S, 2, (-15, 24, 2), 0.12 + 0.2 * f, 0.5)
    kk = math.sin(t * 30)
    hang(S, 'rook', A(0.06 * kk, 0, 2.3 + 0.05 * math.cos(t * 26)), 0.2, (0.05 * kk, 0.05 * math.sin(t * 22)),
         P('stand', aL=(1.3, 1.3, 0.3), aR=(1.3, 1.3, 0.3), lL=(0.5, 0.2 + 0.1 * kk), lR=(-0.5, 0.2 - 0.1 * kk), head=(-0.1, 0.0)), face='shocked')
    S['hat_off'] = True
    for i in range(9):
        a = i * 2 * PI / 9 + t
        S['fea'][i].location = A(math.cos(a) * 1.15, -0.25, 2.5 + math.sin(a) * 1.15)
        S['fea'][i].rotation_euler = (0, -a + PI / 2, 0)
    cam(S, A(lerp(1.5, 1.2, k), lerp(-5.2, -4.5, k), 2.0), A(0, 0, 2.55), 40, 0.05 * kk)


def rain_breath(S, k, t, lt):
    A = storm(S, t, -8, '0C1420')
    hang(S, 'pilot', A(0.04 * math.sin(t * 20), 0, 0.03 * math.sin(t * 17)), -0.35, (0.05 * math.sin(t * 3), 0.05 * math.sin(t * 2.5)),
         P('stand', aL=(2.75, 0.22, 0.35), aR=(1.9, -0.45, 2.3, 0.9), lL=(0.3, 0.3), lR=(0.1, 0.5), head=(0.3 - 0.1 * math.sin(t * 2), 0.2), lean=0.1), face='closed')
    S['bare_on'] = True
    rain(S, A(0, -0.2, 0.2), t, 70, (6.5, 3.4, 7), 30, 0.12, 0.55)
    cam(S, A(lerp(-1.5, -1.1, k), lerp(-4.2, -3.2, k), 0.5), A(0, 0, 0.1), 46, 0.03 * math.sin(t * 5))


# ---------------------------------------------------------------- shots: forty minutes
def rook_watch(S, k, t, lt):
    A = storm(S, t, 6, '141C2C')
    tap = max(0.0, math.sin(t * 13)) if lt > 0.55 else 0.0
    hang(S, 'rook', A(0, 0, 2.3 + 0.1 * math.sin(t * 2)), 0.15, (0.05 * math.sin(t * 2), 0.06 * math.sin(t * 1.7)),
         P('stand', aL=(0.9 + 0.25 * tap, -0.3, 1.5, 0.9), aR=(1.2, 0.0, 0.75), lL=(0.1, 0.1), lR=(-0.1, 0.2), head=(0.4, -0.15)), face='deadpan')
    sw = 0.12 * math.sin(t * 5)
    S['pocket'].location = A(0.42 + sw, -0.85, 2.3 - 0.55 + 0.1 * math.sin(t * 2))
    S['pocket'].rotation_euler = (PI / 2, sw * 1.5, 0)
    rain(S, A(0, 1.2, 3), t, 50, (9, 4, 10), 22, 0.1, 0.6)
    cam(S, A(lerp(-1.5, -1.1, k), lerp(-5.4, -4.6, k), 1.9), A(-0.05, 0, 2.35), 40)


def yo_yo(S, k, t, lt):
    f = flick(lt, 0.3, 0.2)
    A = storm(S, t, 0, mixc('120E26', '3A4A80', f))
    sheet(S, 2, (-34, 70, 0), f, 0.2)
    ph = lt * 5.5
    z1, z2 = 7 * math.sin(ph), 6 * math.sin(ph + 2.2)
    o1, o2 = (1.0 if math.cos(ph) > -0.2 else 0.45), (1.0 if math.cos(ph + 2.2) > -0.2 else 0.45)
    hang(S, 'pilot', A(-4, 6, z1), 0.4, (0.15 * math.sin(t * 5), 0.15 * math.sin(t * 4)), open_=o1, face='scared')
    S['bare_on'] = True
    hang(S, 'rook', A(5, 0, z2 + 1), -0.4, (0.15 * math.sin(t * 6), 0.2 * math.sin(t * 5)),
         P('hat', aL=(2.75, 0.22, 0.35), lL=(0.4 * math.sin(t * 9), 0.4), lR=(-0.4 * math.sin(t * 9), 0.5), head=(0, 0.2)), o2, 'shocked')
    rain(S, A(0, 0, 0), t, 70, (30, 14, 30), 30, 0.3, 1.8)
    cam(S, A(0.5, -33, -2), A(0.5, 3, 2), 28, 0.05 * math.sin(t * 3))


# ---------------------------------------------------------------- shots: the woods
def woods(S, t, f=0.0):
    A = show(S, 'woods')
    sky(S, mixc('0A1420', '5A6A9A', f), 1.0)
    S['wflash'].data.energy = 3 * f
    return A


def drop_out(S, k, t, lt):
    A = woods(S, t, flick(lt, 0.15, 0.25))
    z = lerp(30, 21, k)
    hang(S, 'pilot', A(2.5, 9, z), 0.5, (0.1 * math.sin(t * 2.5), 0.12 * math.sin(t * 2)),
         P('stand', lL=(0.2, 0.3), lR=(0.0, 0.4), head=(0.5, 0.0), **HOLD), face='scared')
    S['bare_on'] = True
    hang(S, 'rook', A(-3.5, 3, z - 8), -0.3, (0.12 * math.sin(t * 3), 0.15 * math.sin(t * 2.6)),
         P('hat', aL=(2.75, 0.22, 0.35), lL=(0.3, 0.3), lR=(-0.2, 0.4), head=(0.45, 0.2)), face='deadpan')
    rain(S, A(-2, 2, 14), t, 70, (26, 12, 26), 34, 0.2, 1.8)
    cam(S, A(-2.5, -6.5, 0.8), A(-0.5, 5, lerp(20, 15, k)), 20)


def tree_land(S, k, t, lt):
    A = woods(S, t)
    s = 0.04 * math.sin(t * 4) * (1 - k)
    S['chute'].location, S['chute'].rotation_euler = A(1.2, 2.2, 3.4), (0.5 + s, 0.45, 0.6)
    S['can'].scale = (0.75, 0.55, 0.9)
    d = ease(k * 2.2)
    S['pilot'].place(A(-0.6, -0.4, 0), 0.5)
    S['pilot'].apply(blend(P('stand', lean=0.55, lift=-0.45, head=(0.5, 0.0), aL=(0.9, 0.3, 0.6), aR=(0.9, 0.3, 0.6), lL=(1.0, 1.5), lR=(0.6, 1.3)),
                           P('stand', lean=0.15, lift=-0.08, head=(-0.2, 0.3), aL=(0.3, 0.5, 0.4), aR=(1.7, -0.2, 1.9, 0.6), lL=(0.35, 0.5), lR=(-0.1, 0.25)), d))
    S['mask'], S['bare_on'], S['face']['pilot'] = False, True, 'closed' if d < 0.5 else 'calm'
    sw = 0.25 * math.sin(t * 3.2)
    hang(S, 'rook', A(2.7, -1.2, 4.3), -0.5, (0.1, sw), P('cross', lL=(0.25 * math.sin(t * 3.2), 0.1), lR=(-0.25 * math.sin(t * 3.2), 0.1), head=(0.1, 0.45)),
         0.6, 'deadpan')
    S['rcan'].rotation_euler = (0.3, -0.5, 0)
    rain(S, A(0, -1, 4), t, 50, (14, 8, 10), 24, 0.15)
    cam(S, A(lerp(-1.6, -1.2, k), lerp(-8.4, -7.6, k), 1.1), A(1.0, 0.0, 2.7), 28)


def road(S, k, t, lt):
    A = woods(S, t)
    cx = lerp(-36, 0.9, 1 - (1 - min(1.0, k * 1.35)) ** 3)
    S['car'].location = (cx, -17.4, 0.05 * math.sin(t * 20) * (1 - k))
    px = lerp(4.2, 3.2, min(1.0, k * 1.6))
    wv = ease((lt - 0.45) / 0.3)
    S['pilot'].place(A(px, -13.2, 0), -0.55)
    S['pilot'].apply(blend(walk(t, 1.3), P('stand', aR=(2.5, 0.5, 0.5 + 0.35 * math.sin(t * 10)), aL=(0.4, -0.1, 1.5, 1.0), head=(0.0, 0.2), lean=0.12), wv))
    S['mask'], S['bare_on'], S['face']['pilot'] = False, True, 'calm'
    S['rook'].place(A(5.5, -12.7, 0), -0.35)
    S['rook'].apply(P('point', aR=(1.35, 0.9, 0.1), aL=(-0.25, 0.75, 1.9, 1.5), head=(0.0, -0.3)))
    S['face']['rook'] = 'calm'
    rain(S, A(0, -14, 4), t, 50, (18, 8, 10), 24, 0.15)
    cam(S, A(lerp(3.8, 3.4, k), lerp(-23.0, -22.2, k), 1.2), A(3.7, -13, 2.5), 26)


# ---------------------------------------------------------------- shots: after
def fly_again(S, k, t, lt):
    A = apron(S, True)
    jet(S, 0, A(-4.5, 9, 2.19), 1.0, -0.05, gear=True)
    S['pilot'].place(A(-1.3, 0.4, 0), 0.35)
    S['pilot'].apply(P('hips', aR=(0.3, 0.2, 0.3), head=(0, -0.4)))
    S['face']['pilot'] = 'happy'
    tip = math.sin(PI * ease((lt - 0.2) / 0.75)) if lt > 0.2 else 0
    S['rook'].place(A(1.5, 0, 0), -0.7)
    S['rook'].apply(blend(P('stand', head=(0, 0.2)), P('hat', head=(0.2, 0.2)), tip))
    S['hat_tip'], S['face']['rook'] = tip, 'warm'
    cam(S, A(lerp(0.9, 0.5, k), lerp(-8.2, -7.2, k), 1.7), A(0.1, 0.3, 2.0), 34)


def signoff(S, k, t, lt):
    A = apron(S)
    jet(S, 0, A(-8, 13, 2.19), 0.9, -0.05, gear=True)
    S['rook'].place(A(0, 0, 0), 0.15)
    tip = math.sin(PI * ease(lt / 0.8)) if lt < 0.8 else 0
    S['rook'].apply(blend(P('stand', aL=(0.9, 0.25, 1.2), head=(0.05, 0)), P('hat', aL=(0.9, 0.25, 1.2), head=(0.22, 0)), tip))
    S['hat_tip'], S['face']['rook'] = tip, 'smirk'
    c = max(0.0, min(1.0, (lt - 0.25) / 0.9))
    S['lever'].location = A(-0.75 - 0.2 * c, -0.75, 1.7 + 2.6 * math.sin(c * PI))
    S['lever'].rotation_euler = (t * 14, t * 6, 0)
    S['lever'].scale = (1.5, 1.5, 1.5)
    cam(S, A(lerp(1.1, 0.8, k), lerp(-6.4, -5.2, k), 1.0), A(0, 0, 2.05), 38)


# ---------------------------------------------------------------- photographs for the case board
def photo_storm(S, k, t, lt):
    A = dusk_sky(S)
    S['anvil'].location = (0, -150, -44)
    S['tfl'].hide_render = False
    jet(S, 0, A(7, -40, 6), 0.3, 0, 0.3)
    cam(S, A(0, 30, 8), A(0, -150, -8), 30)


def photo_rankin(S, k, t, lt):
    A = apron(S, True)
    jet(S, 0, A(-3, 10, 2.19), 0.9, -0.05, gear=True)
    S['pilot'].place(A(0, 0, 0), 0.25)
    S['pilot'].apply(P('hips', head=(0, 0.1)))
    S['face']['pilot'] = 'happy'
    cam(S, A(0.7, -3.6, 2.5), A(0, 0, 2.25), 55)


SHOTS3D = {f.__name__: f for f in (
    eject_bang, fall_in, chute_yank, rook_up, rook_tarmac, rook_walk, two_jets, cockpit_calm, over_top, fire_light, rook_gulp, handle_snap,
    seat_away, rook_fall, frost_hand, swell, chute_open, storm_wide, updraft, rook_chute, hail_hit, blue_sheet, rook_zap, rain_breath,
    rook_watch, yo_yo, drop_out, tree_land, road, fly_again, signoff)}
STILLS = dict(storm=photo_storm, rankin=photo_rankin)
