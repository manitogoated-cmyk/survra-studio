"""Case 005 in 3D - Vesna Vulovic, JAT Flight 367, 26 January 1972. Sets built for this story only:
an airport apron at dusk, the cabin of a 1970s twin-jet, the sky above the clouds, a snowy wooded hillside, a hospital ward."""
import math

import bpy

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(apron=(0, 0, 0), cabin=(400, 0, 0), sky=(0, 700, 0), hill=(800, 0, 0), ward=(1200, 0, 0))
FAR = (0, 0, -600)
SL = 0.2                                    # the hillside falls away toward +x
HOST = {'rook_apron', 'rook_stairs', 'greet', 'rook_seat', 'trolley', 'rook_brace', 'rook_hat', 'hill_wide', 'rook_lantern',
        'rescuers', 'ward_bed', 'walks', 'rook_caw', 'rook_paper', 'rook_wrong', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
VESNA = dict(top='24408A', pants='1B2F66', hand='E2B48C', boot='15151C', fore='24408A')
GOWN = dict(top='DDE8EC', pants='C4D4DA', hand='E2B48C', boot='E2B48C', fore='E2B48C')
BRUNO = dict(top='6A5236', pants='2E2A26', hand='D9AC8A', boot='1E1A16')
PAXA = dict(top='7A6A52', pants='3A342E', hand='D9AC8A', boot='1E1A16')
PAXB = dict(top='5E3A44', pants='2A2630', hand='C99A78', boot='1E1A16')
PEOPLE = ('vesna', 'patient', 'bruno', 'paxa', 'paxb')
WHITE, NAVY = 'ECE8DE', '24408A'


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def hz(x):
    return -math.tan(SL) * x


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


def aimed(loc, energy, col, size, aim, parent, kind='AREA', spot=0.8):
    l = light(loc, energy, col, size, None, kind, spot, parent)
    c = l.constraints.new('TRACK_TO')
    c.target, c.track_axis, c.up_axis = aim, 'TRACK_NEGATIVE_Z', 'UP_Y'
    return l


# ---------------------------------------------------------------- heads
def face(head, skin, hair, nose):
    add('ico_sphere', skin, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
    eyes = []
    for s in (-1, 1):
        eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.5))
        add('cube', '14121A', (s * 0.105, -0.28, 0.035), scale=(0.04, 0.02, 0.045), size=1, parent=head)
        add('cube', hair, (s * 0.105, -0.27, 0.13), rot=(0, s * 0.1, 0), scale=(0.13, 0.03, 0.022), size=1, parent=head)
    add('cube', nose, (0, -0.29, -0.04), scale=(0.05, 0.05, 0.08), size=1, parent=head)
    jaw = empty((0, -0.2, -0.13), head)
    add('cube', '7A2A30', (0, -0.075, 0.0), scale=(0.1, 0.03, 0.028), size=1, parent=jaw)
    return dict(jaw=jaw, eyes=eyes, eye0=0.075)


def attendant_head(cap=True):
    def fn(head):
        x = face(head, 'E2B48C', '5A3620', 'C99670')
        add('ico_sphere', '5A3620', (0, 0.06, 0.1), scale=(1.02, 1.0, 1.0), radius=0.31, subdivisions=1, parent=head)
        for s in (-1, 1):
            add('cube', '5A3620', (s * 0.25, 0.02, -0.12), scale=(0.1, 0.34, 0.36), size=1, parent=head)
        if cap:
            add('cylinder', NAVY, (0, -0.02, 0.4), rot=(-0.15, 0, 0), radius=0.2, depth=0.13, vertices=8, parent=head)
            add('cube', 'FFC233', (0, -0.21, 0.4), scale=(0.07, 0.02, 0.05), size=1, parent=head, rough=0.4)
        return x
    return fn


def man_head(skin, hair, cap=None, tash=False):
    def fn(head):
        x = face(head, skin, hair, 'B8866A')
        add('ico_sphere', hair, (0, 0.07, 0.08), scale=(0.96, 1.0, 0.95), radius=0.3, subdivisions=1, parent=head)
        if cap:
            add('cylinder', cap, (0, 0.0, 0.3), rot=(-0.1, 0, 0), radius=0.33, depth=0.1, vertices=8, parent=head)
            add('cube', cap, (0, -0.3, 0.26), rot=(-0.2, 0, 0), scale=(0.4, 0.26, 0.04), size=1, parent=head)
        if tash:
            add('cube', hair, (0, -0.3, -0.1), scale=(0.2, 0.04, 0.05), size=1, parent=head)
        return x
    return fn


# ---------------------------------------------------------------- props
def tube(col, x0, x1, parent, r=2.4, open_=False):
    return add('cylinder', col, ((x0 + x1) / 2, 0, 0), rot=(0, PI / 2, 0), radius=r, depth=abs(x1 - x0), vertices=10, parent=parent,
               end_fill_type='NOTHING' if open_ else 'NGON')


def trim(parent, x0, x1, r=2.4):
    """Navy cheat line and a row of windows down both sides of a fuselage piece."""
    for s in (-1, 1):
        add('cube', NAVY, ((x0 + x1) / 2, s * (r - 0.06), 0.15), scale=(abs(x1 - x0), 0.12, 0.26), size=1, parent=parent)
        x = min(x0, x1) + 1.0
        while x < max(x0, x1) - 0.6:
            add('cube', '1A2030', (x, s * (r - 0.1), 0.85), scale=(0.5, 0.14, 0.42), size=1, parent=parent, rough=0.3)
            x += 1.35


def shards(parent, x, d, col=WHITE, n=7, r=2.3):
    for i in range(n):
        a = i * 2 * PI / n + 0.3
        add('cone', col if i % 3 else '3A3A44', (x + d * (0.5 + 0.35 * (i % 3)), r * math.cos(a), r * math.sin(a)), rot=(0, d * PI / 2, a),
            scale=(0.25, 1, 1), radius1=0.75, radius2=0.0, depth=1.2 + 0.7 * (i % 3), vertices=3, parent=parent)


def make_jet(r, gear=False):
    """A 1970s rear-engined twin-jet with a T-tail, nose toward +x, in two halves that can part at x = 0."""
    front, rear = empty((0, 0, 0), r), empty((0, 0, 0), r)
    tube(WHITE, 0, 20, front)
    add('cone', WHITE, (22.5, 0, 0), rot=(0, PI / 2, 0), radius1=2.4, radius2=0.5, depth=5, vertices=10, parent=front)
    add('cube', '1A2030', (21.6, 0, 0.9), rot=(0, 0.42, 0), scale=(1.6, 2.6, 0.5), size=1, parent=front, rough=0.3)
    trim(front, 0, 19)
    for s in (-1, 1):
        add('cube', 'D4D0C6', (0.5, s * 9.6, -1.1), rot=(0, 0, s * -0.36), scale=(5.2, 16, 0.32), size=1, parent=front)
        add('cube', NAVY, (-2.9, s * 16.8, -1.1), rot=(0, 0, s * -0.36), scale=(1.4, 1.6, 0.36), size=1, parent=front)
    tube(WHITE, -20, 0, rear)
    add('cone', WHITE, (-22.5, 0, 0), rot=(0, -PI / 2, 0), radius1=2.4, radius2=0.5, depth=5, vertices=10, parent=rear)
    trim(rear, -19, -8)
    for s in (-1, 1):
        add('cylinder', 'B8BCC6', (-12.5, s * 3.5, 0.9), rot=(0, PI / 2, 0), radius=1.1, depth=6, vertices=8, parent=rear)
        add('cylinder', '1A1C24', (-9.45, s * 3.5, 0.9), rot=(0, PI / 2, 0), radius=0.85, depth=0.1, vertices=8, parent=rear)
    add('cube', WHITE, (-19, 0, 5.2), rot=(0, -0.3, 0), scale=(5.2, 0.32, 6.6), size=1, parent=rear)
    add('cube', NAVY, (-19.9, 0, 7.4), rot=(0, -0.3, 0), scale=(4.2, 0.36, 1.8), size=1, parent=rear)
    add('cube', 'D4D0C6', (-21, 0, 8.5), scale=(3.6, 11.5, 0.28), size=1, parent=rear)
    for h, d in ((front, 1), (rear, -1)):
        add('cylinder', '17151C', (d * 0.06, 0, 0), rot=(0, PI / 2, 0), radius=2.32, depth=0.1, vertices=10, parent=h)
    if gear:
        for x, y in ((17, 0), (-1.5, 2.6), (-1.5, -2.6)):
            add('cylinder', '8A90A0', (x, y, -3.0), radius=0.16, depth=1.6, vertices=6, parent=r)
            add('cylinder', '15151C', (x, y, -3.7), rot=(PI / 2, 0, 0), radius=0.55, depth=0.7, vertices=8, parent=r)
        add('ico_sphere', 'FF3020', (-2, 0, 2.5), radius=0.18, subdivisions=1, parent=r, emit=14)
    return front, rear


def make_wreck(r):
    """A torn-off length of fuselage, open at both ends, axis along x."""
    tube(WHITE, -4.5, 4.5, r, open_=True)
    trim(r, -4.5, 4.5)
    add('cube', '3A4668', (0, 0, -1.15), scale=(9, 4.1, 0.14), size=1, parent=r)
    shards(r, 4.5, 1)
    shards(r, -4.5, -1, n=6)
    for x in (-2.6, -0.8):
        for s in (-1, 1):
            add('cube', '7A2E2E', (x, s * 1.35, -0.6), scale=(0.8, 1.3, 0.5), size=1, parent=r)
            add('cube', '7A2E2E', (x - 0.4, s * 1.35, 0.15), scale=(0.2, 1.3, 1.3), size=1, parent=r)
    return r


def make_trolley(r):
    add('cube', 'A8AEB8', (0, 0, 0.78), scale=(0.78, 1.15, 1.2), size=1, parent=r, rough=0.4)
    add('cube', 'D8DCE4', (0, 0, 1.4), scale=(0.86, 1.25, 0.06), size=1, parent=r, rough=0.3)
    for z in (0.5, 0.85, 1.15):
        add('cube', '5A6070', (0, -0.58, z), scale=(0.66, 0.02, 0.04), size=1, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', '15151C', (sx * 0.3, sy * 0.45, 0.09), rot=(0, PI / 2, 0), radius=0.09, depth=0.07, vertices=6, parent=r)
    add('cylinder', 'FF7A1A', (0.15, -0.2, 1.62), radius=0.13, depth=0.38, vertices=7, parent=r, rough=0.5)
    add('cone', 'FF7A1A', (0.15, -0.2, 1.86), radius1=0.13, radius2=0.05, depth=0.1, vertices=7, parent=r)
    for i in range(3):
        add('cylinder', 'F4F0E6', (-0.2, -0.35 + i * 0.3, 1.5), radius=0.07, depth=0.14, vertices=6, parent=r)


def make_lantern(r):
    add('cube', 'FFC060', (0, 0, 0), scale=(0.2, 0.2, 0.3), size=1, parent=r, emit=14)
    add('cube', '2A2420', (0, 0, 0.19), scale=(0.26, 0.26, 0.06), size=1, parent=r)
    add('cube', '2A2420', (0, 0, -0.18), scale=(0.26, 0.26, 0.06), size=1, parent=r)
    add('torus', '2A2420', (0, 0, 0.32), rot=(PI / 2, 0, 0), major_radius=0.12, minor_radius=0.02, major_segments=8, minor_segments=3, parent=r)
    return light((0, -0.25, 0.05), 420, 'FFB050', kind='POINT', parent=r)


def pine(r, x, y, h, snow=True):
    z = hz(x)
    add('cylinder', '3A2A20', (x, y, z + 0.7), radius=0.24, depth=1.8, vertices=5, parent=r)
    for i in range(3):
        rad, zz = (2.1 - i * 0.55) * h / 7, z + 1.4 + (1.0 + i * 1.55) * h / 7
        add('cone', '1E3D36' if i % 2 else '24483E', (x, y, zz), radius1=rad, radius2=0.0, depth=2.7 * h / 7, vertices=6, parent=r)
        if snow:
            add('cone', 'DCE6F4', (x, y, zz + 0.5 * h / 7), radius1=rad * 0.6, radius2=0.0, depth=1.75 * h / 7, vertices=6, parent=r)


# ---------------------------------------------------------------- sets
def set_apron(r):
    add('plane', '262A34', (0, 0, 0), size=500, parent=r)
    for x in range(-60, 61, 12):
        add('cube', 'E0B030', (x, -3, 0.01), scale=(6, 0.3, 0.02), size=1, parent=r)
    add('cube', 'E0B030', (0, 4, 0.01), scale=(140, 0.25, 0.02), size=1, parent=r)
    jet = empty((4, 14, 4.2), r)
    make_jet(jet, gear=True)
    # mobile stairs up to the door aft of the wing
    for i in range(11):
        add('cube', '9AA0AE', (-3, 4.3 + i * 0.66, 0.3 + i * 0.3), scale=(1.9, 0.68, 0.14), size=1, parent=r)
    for s in (-1, 1):
        add('cube', 'FF7A1A', (-3 + s * 0.95, 7.6, 2.75), rot=(0.427, 0, 0), scale=(0.07, 8.0, 0.09), size=1, parent=r)
        for i in (0, 5, 10):
            add('cylinder', '6A7080', (-3 + s * 0.95, 4.3 + i * 0.66, 0.85 + i * 0.3), radius=0.04, depth=1.2, vertices=5, parent=r)
        add('cube', '4A5060', (-3 + s * 0.9, 9.6, 1.5), scale=(0.12, 2.6, 3.0), size=1, parent=r)
        add('cylinder', '15151C', (-3 + s * 0.9, 9.6, 0.3), rot=(0, PI / 2, 0), radius=0.3, depth=0.2, vertices=8, parent=r)
    add('cube', 'FFD9A0', (-3, 11.62, 5.1), scale=(1.5, 0.12, 2.9), size=1, parent=r, emit=5)
    light((-3, 10.6, 5.0), 500, 'FFC880', kind='POINT', parent=r)
    # terminal, tower, taxiway lights
    add('cube', '2E3444', (-10, 78, 5), scale=(150, 12, 10), size=1, parent=r)
    for i in range(26):
        add('cube', 'FFD27A', (-80 + i * 5.6, 71.9, 5.5), scale=(3.4, 0.1, 2.2), size=1, parent=r, emit=3.5)
    add('cylinder', '2E3444', (-44, 76, 16), radius=2.4, depth=32, vertices=8, parent=r)
    add('cylinder', '9FE0FF', (-44, 76, 33.5), radius=4.2, depth=3.2, vertices=8, parent=r, emit=2.5)
    add('cylinder', '2E3444', (-44, 76, 35.6), radius=4.8, depth=1.0, vertices=8, parent=r)
    for i in range(18):
        add('ico_sphere', '4A8AFF', (-70 + i * 8, -9, 0.16), radius=0.16, subdivisions=1, parent=r, emit=18)
    for x in (-24, 30):
        add('cylinder', '4A5060', (x, 24, 6), radius=0.18, depth=12, vertices=5, parent=r)
        add('cube', 'FFF2C0', (x, 23.4, 12), scale=(1.6, 1.2, 0.25), size=1, parent=r, emit=10)
        light((x, 22, 11.4), 9000, 'FFE2B0', kind='POINT', parent=r)
    add('cube', 'FF8A4A', (0, 260, 9), scale=(900, 1, 20), size=1, parent=r, emit=2.2)
    add('cube', 'B04A6A', (0, 262, 34), scale=(900, 1, 30), size=1, parent=r, emit=0.9)
    aim = empty((0, 0, 2), r)
    key = aimed((-8, -10, 7), 2600, 'FFD8B0', 5.0, aim, r)
    aimed((20, -16, 14), 14000, 'C0B0E0', 20.0, empty((4, 14, 4), r), r)
    aimed((10, 20, 9), 3000, 'FF7A1A', 3.0, aim, r)
    aimed((12, -8, 2), 400, '6A8AD0', 5.0, aim, r)
    return dict(akey=key, aaim=aim)


def set_cabin(r):
    add('cube', '2A3550', (0, 1, -0.1), scale=(4.8, 26, 0.2), size=1, parent=r)
    add('cube', '4A5884', (0, 1, 0.005), scale=(1.1, 26, 0.02), size=1, parent=r)
    add('cube', 'DAD4C6', (0, 1, 3.62), scale=(2.9, 26, 0.14), size=1, parent=r)
    for s in (-1, 1):
        add('cube', 'CFC8B8', (s * 2.42, 1, 1.1), scale=(0.2, 26, 2.3), size=1, parent=r)
        add('cube', 'DAD4C6', (s * 1.98, 1, 2.92), rot=(0, s * 0.72, 0), scale=(0.16, 26, 1.5), size=1, parent=r)
        add('cube', 'B8B0A0', (s * 1.72, 1, 2.98), scale=(0.95, 26, 0.34), size=1, parent=r)
        for y in range(-10, 13, 2):
            add('cube', 'FFC890', (s * 2.3, y + 0.1, 1.85), scale=(0.06, 0.7, 0.52), size=1, parent=r, emit=3.2)
        for y in range(-8, 11, 2):
            add('cube', '7A2E2E', (s * 1.45, y, 0.55), scale=(1.5, 0.9, 0.5), size=1, parent=r)
            add('cube', '8A3434', (s * 1.45, y + 0.48, 1.3), scale=(1.5, 0.2, 1.45), size=1, parent=r)
            add('cube', 'E8E0D0', (s * 1.45, y + 0.36, 1.86), scale=(1.3, 0.06, 0.3), size=1, parent=r)
            add('cube', '5A2020', (s * 0.66, y, 0.92), scale=(0.1, 0.8, 0.12), size=1, parent=r)
    # passengers, seated facing the nose (the camera end)
    cols = ('7A6A52', '4A5A6A', '5E3A44', '3E5A4A', '8A7A3A', '54466A')
    for i, (sx, off, y) in enumerate(((-1, -0.34, -4), (-1, 0.36, -4), (1, 0.36, -6), (-1, 0.3, 0), (1, -0.34, 2), (1, 0.36, 2), (-1, -0.3, 4),
                                     (1, 0.3, -2), (-1, 0.36, -8), (1, -0.3, -8))):
        x = sx * 1.45 + off
        add('cone', cols[i % 6], (x, y, 1.3), radius1=0.34, radius2=0.3, depth=1.0, vertices=7, parent=r)
        add('ico_sphere', ('E2B48C', 'C99A78', 'D9AC8A')[i % 3], (x, y - 0.03, 2.05), radius=0.26, subdivisions=1, parent=r)
        add('ico_sphere', ('3A2A20', '17131A', 'B8B8B8', '6A4A2A')[i % 4], (x, y + 0.06, 2.13), radius=0.27, subdivisions=1, parent=r)
    end = empty((0, 12, 0), r)
    add('cube', '9A927F', (0, 0, 1.8), scale=(4.8, 0.2, 3.7), size=1, parent=end)
    add('cube', 'FF7A1A', (0, -0.12, 1.5), scale=(1.2, 0.06, 3.0), size=1, parent=end)
    add('cube', 'E8E0D0', (1.5, -0.12, 2.3), scale=(1.0, 0.05, 0.7), size=1, parent=end)
    for y in (-7, -1, 5, 10):
        add('cube', 'FFF2D0', (0, y, 3.52), scale=(0.5, 1.6, 0.05), size=1, parent=r, emit=5)
    lamps = [light((0, y, 3.1), 260, 'FFE8C0', kind='POINT', parent=r) for y in (-7, -1, 5, 10)]
    rip = light((0, 11, 2.0), 0, 'FFB060', kind='POINT', parent=r)
    aim = empty((0, 1, 1.8), r)
    fill = aimed((0.4, -9, 2.6), 500, 'FFE2C8', 3.0, aim, r)
    return dict(end=end, lamps=lamps, rip=rip, cfill=fill)


def set_sky(r):
    cl = empty((0, 0, -16), r)
    for i in range(54):
        x, y = -130 + (i * 61) % 260, -60 + (i * 37) % 190
        s = 9 + (i * 7) % 12
        add('ico_sphere', 'F4F6FC', (x, y, ((i * 13) % 7) - 3), scale=(s, s * 0.8, s * 0.3), radius=1, subdivisions=1, parent=cl, emit=0.12)
    jet = empty((0, 0, 0), r)
    front, rear = make_jet(jet)
    aim = empty((0, 0, 0), r)
    sun = aimed((30, -60, 70), 4.0, 'FFF4E0', 1.0, aim, r, kind='SUN')
    aimed((-20, -40, -30), 9000, '9AB8F0', 30.0, aim, r)
    flash = add('ico_sphere', 'FFB040', (0, 0, -400), radius=1, subdivisions=2, parent=r, emit=7)
    fl = light((0, 0, 0), 0, 'FFB050', kind='POINT', parent=flash)
    return dict(cl=cl, jet=jet, front=front, rear=rear, sun=sun, flash=flash, flashl=fl, skyaim=aim)


def set_hill(r):
    add('plane', 'C4D2EA', (0, 0, 0), rot=(0, SL, 0), size=600, parent=r)
    k = 0
    for i in range(150):
        x, y = -75 + (i * 47) % 130, -34 + (i * 29) % 100
        if abs(y) < 6.5 or (y < 0 and x > -6) or (x > 2 and y < 16 and y > 0 and x < 22):
            continue
        pine(r, x, y, 6 + (i * 5) % 5)
        k += 1
    for i in range(26):
        pine(r, -90 + i * 7.5, 74 + (i % 3) * 4, 12 + (i % 4) * 2, snow=False)
    for i in range(9):
        x, y = -30 + (i * 17) % 60, 20 + (i * 11) % 30
        add('ico_sphere', 'D4E0F2', (x, y, hz(x)), scale=(3 + i % 3, 2.5, 0.8), radius=1, subdivisions=1, parent=r)
    for i, (x, y) in enumerate(((-58, 52), (-49, 58), (-66, 60))):
        add('cube', '3A3038', (x, y, hz(x) + 1.6), scale=(5, 4, 3.2), size=1, parent=r)
        add('cylinder', 'D4E0F2', (x, y, hz(x) + 4.2), rot=(0, PI / 2, PI / 2), scale=(1, 0.75, 1), radius=3.1, depth=5.4, vertices=3, parent=r)
        add('cube', 'FFC060', (x + 0.8, y - 2.02, hz(x) + 1.7), scale=(1.0, 0.06, 0.9), size=1, parent=r, emit=7)
    furrow = empty((0, 0, -40), r)
    for i in range(7):
        x = -13 + i * 2.6
        add('cube', '6A7890', (x, 0.3 * math.sin(i), hz(x) + 40.04), rot=(0, SL, 0.1 * math.sin(i * 2)), scale=(2.8, 3.4 - 0.2 * i, 0.1), size=1, parent=furrow)
        for s in (-1, 1):
            add('ico_sphere', 'E4ECF8', (x, s * (2.3 - 0.1 * i), hz(x) + 40.2), scale=(1.5, 0.7, 0.5), radius=1, subdivisions=1, parent=furrow)
    aim = empty((4, 0, 1), r)
    moon = aimed((-30, -40, 60), 90000, '8AA8E8', 20.0, aim, r)
    fill = aimed((30, -30, 8), 2500, '6A80C0', 12.0, aim, r)
    glow = aimed((-60, 60, 12), 30000, 'FF9A5A', 14.0, aim, r)
    return dict(furrow=furrow, moon=moon, hfill=fill, hglow=glow, haim=aim)


def set_ward(r):
    add('plane', '9FB0A0', (0, 0, 0), size=30, parent=r)
    for i in range(-6, 7):
        add('cube', '8FA090', (i * 1.6, 1, 0.004), scale=(0.04, 16, 0.01), size=1, parent=r)
    add('cube', 'D8DCC8', (0, 5, 3.5), scale=(22, 0.2, 7), size=1, parent=r)
    add('cube', 'A8C0B0', (0, 4.88, 0.9), scale=(22, 0.06, 1.8), size=1, parent=r)
    add('cube', 'CCD2BE', (-7, 0, 3.5), scale=(0.2, 14, 7), size=1, parent=r)
    add('cube', 'CCD2BE', (7, 0, 3.5), scale=(0.2, 14, 7), size=1, parent=r)
    win = add('cube', 'DCEEFF', (-1.2, 4.86, 3.6), scale=(4.2, 0.06, 3.0), size=1, parent=r, emit=2.2)
    for x in (-3.3, -1.2, 0.9):
        add('cube', 'F4F0E6', (x, 4.8, 3.6), scale=(0.14, 0.1, 3.2), size=1, parent=r)
    for z in (2.05, 3.6, 5.15):
        add('cube', 'F4F0E6', (-1.2, 4.8, z), scale=(4.4, 0.1, 0.14), size=1, parent=r)
    for s in (-1, 1):
        add('cube', 'E08A4A', (-1.2 + s * 2.55, 4.7, 3.5), scale=(0.7, 0.1, 3.6), size=1, parent=r)
    # the bed: head at +x
    bed = empty((1.0, 2.6, 0), r)
    add('cube', 'F4F0E6', (0, 0, 0.95), scale=(5.0, 2.1, 0.3), size=1, parent=bed)
    add('cube', 'B8CCE0', (-0.8, 0, 1.2), scale=(3.4, 2.16, 0.34), size=1, parent=bed)
    add('cube', 'FFFFFF', (1.95, 0, 1.25), rot=(0, -0.3, 0), scale=(1.0, 1.5, 0.3), size=1, parent=bed)
    for x in (-2.5, 2.5):
        for y in (-1.0, 1.0):
            add('cylinder', 'E8ECF0', (x, y, 0.8 if x < 0 else 1.15), radius=0.06, depth=1.6 if x < 0 else 2.3, vertices=6, parent=bed, rough=0.3)
        add('cylinder', 'E8ECF0', (x, 0, 1.55 if x < 0 else 2.25), rot=(PI / 2, 0, 0), radius=0.06, depth=2.0, vertices=6, parent=bed, rough=0.3)
    add('cube', 'F4F0E6', (4.6, 3.6, 0.7), scale=(1.1, 1.0, 1.4), size=1, parent=r)
    add('cylinder', '4A8AB0', (4.6, 3.6, 1.6), radius=0.2, depth=0.4, vertices=7, parent=r)
    for i in range(5):
        a = i * 1.26
        add('ico_sphere', 'FF7A1A' if i % 2 else 'FFC233', (4.6 + 0.2 * math.cos(a), 3.6 + 0.2 * math.sin(a), 2.05 + 0.06 * (i % 2)), radius=0.14,
            subdivisions=1, parent=r, emit=0.4)
    add('cylinder', 'C8CCD4', (3.6, 1.0, 2.0), radius=0.04, depth=4.0, vertices=5, parent=r, rough=0.3)
    add('cube', 'DCEEFF', (3.6, 1.0, 3.7), scale=(0.3, 0.12, 0.5), size=1, parent=r, emit=0.6)
    add('cube', 'F4F0E6', (-5.2, 3.4, 0.95), scale=(2.4, 2.1, 0.3), size=1, parent=r)
    add('cube', 'D0B8C8', (-5.2, 3.4, 1.2), scale=(2.4, 2.16, 0.3), size=1, parent=r)
    aim = empty((0, 1, 1.8), r)
    aimed((-1.2, 3.6, 4.2), 320, 'DCEEFF', 4.0, aim, r)
    key = aimed((-3, -7, 4.5), 330, 'FFF0DC', 5.0, aim, r)
    aimed((5, -5, 2), 90, 'FFD0A0', 4.0, aim, r)
    return dict(bed=bed, wkey=key)


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('apron', set_apron), ('cabin', set_cabin), ('sky', set_sky), ('hill', set_hill), ('ward', set_ward)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['vesna'] = K.Rig(VESNA, attendant_head())
    S['patient'] = K.Rig(GOWN, attendant_head(cap=False))
    S['bruno'] = K.Rig(BRUNO, man_head('D9AC8A', 'A8A8A8', cap='3A3A40', tash=True))
    S['paxa'] = K.Rig(PAXA, man_head('D9AC8A', '3A2A20', cap='4A4036'))
    S['paxb'] = K.Rig(PAXB, man_head('C99A78', '17131A'))
    S['wreck'] = make_wreck(empty(FAR))
    S['trolley'] = empty(FAR)
    make_trolley(S['trolley'])
    S['lantern'] = empty(FAR)
    S['lanl'] = make_lantern(S['lantern'])
    S['resc'] = []
    for i in range(5):
        o = add('ico_sphere', 'FFC060', FAR, radius=0.22, subdivisions=1, emit=16)
        light((0, 0, 0), 300, 'FFB050', kind='POINT', parent=o)
        S['resc'].append(o)
    S['deb'] = [add('cube', (WHITE, 'B8BCC6', NAVY, '3A3A44')[i % 4], FAR, scale=(0.9 + 0.5 * (i % 3), 0.5 + 0.3 * (i % 2), 0.08), size=1) for i in range(22)]
    S['deb0'] = [tuple(o.scale) for o in S['deb']]
    S['snow'] = [add('ico_sphere', 'F0F4FC', FAR, radius=0.5, subdivisions=1, emit=0.25) for _ in range(30)]
    S['smoke'] = [add('ico_sphere', '34343E', FAR, radius=1.0, subdivisions=1) for _ in range(12)]
    S['streak'] = [add('cube', 'F4F6FC', FAR, scale=(0.12, 0.12, 9), size=1, emit=0.8) for _ in range(12)]
    S['fea'] = [add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4) for _ in range(7)]
    S['paper'] = empty(FAR)
    add('cube', 'E8E2D2', (0, 0, 0), scale=(1.0, 0.03, 0.72), size=1, parent=S['paper'])
    add('cube', '2A2630', (0, -0.02, 0.24), scale=(0.84, 0.01, 0.1), size=1, parent=S['paper'])
    for i in range(4):
        add('cube', '8A8478', (-0.2 + 0.42 * (i % 2), -0.02, 0.04 - 0.14 * (i // 2)), scale=(0.36, 0.01, 0.07), size=1, parent=S['paper'])
    S['cane'] = add('cylinder', '6A4A2A', FAR, radius=0.04, depth=1.9, vertices=6)
    S['pin'] = empty(FAR)
    add('cylinder', 'FFD866', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.07, depth=0.03, vertices=8, parent=S['pin'], rough=0.25, emit=1.2)
    for s in (-1, 1):
        add('cube', 'FFD866', (s * 0.14, 0, 0.01), rot=(0, s * -0.25, 0), scale=(0.2, 0.025, 0.06), size=1, parent=S['pin'], rough=0.25, emit=1.2)
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 1200
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    S['pov'] = light((0, 0, 0), 0, 'FFF2E0', kind='POINT', parent=rigc)
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
    for who in ('rook',) + PEOPLE:
        S[who].place(FAR)
        S[who].apply(P())
        S[who].root.scale = (1, 1, 1)
    for o in S['deb'] + S['snow'] + S['smoke'] + S['streak'] + S['fea'] + S['resc']:
        o.location = FAR
        o.rotation_euler = (0, 0, 0)
    for o in S['snow'] + S['smoke']:
        o.scale = (1, 1, 1)
    for o, sc0 in zip(S['deb'], S['deb0']):
        o.scale = sc0
    for k in ('wreck', 'trolley', 'lantern', 'paper', 'pin', 'cane'):
        S[k].location, S[k].rotation_euler, S[k].scale = FAR, (0, 0, 0), (1, 1, 1)
    S['lanl'].data.energy = 420
    S['face'] = dict(rook='calm', vesna='calm', patient='calm', bruno='calm', paxa='calm', paxb='calm')
    S['hat_tip'], S['hat_off'], S['hat_up'] = 0.0, False, 0.0
    S['pov'].data.energy = 0
    S['end'].location = (0, 12, 0)
    S['rip'].data.energy = 0
    for l in S['lamps']:
        l.data.energy = 260
    S['cfill'].data.energy = 500
    S['cl'].location, S['cl'].scale = (0, 0, -16), (1, 1, 1)
    S['jet'].location, S['jet'].rotation_euler = (0, 0, 0), (0, 0, 0)
    for h in ('front', 'rear'):
        S[h].location, S[h].rotation_euler = (0, 0, 0), (0, 0, 0)
    S['flash'].location, S['flash'].scale = (0, 0, -400), (1, 1, 1)
    S['flashl'].data.energy = 0
    S['sun'].data.energy = 4.0
    S['sun'].data.color = K.hexc('FFF4E0')[:3]
    S['furrow'].location = (0, 0, -40)
    S['moon'].data.energy, S['hfill'].data.energy, S['hglow'].data.energy = 90000, 2500, 30000
    S['akey'].data.energy = 2600
    S['wkey'].data.energy = 330
    sky(S, '000000', 1.0)


def finish(S, t):
    """Rook's face, hat and beak, then the people's eyes, once the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.39) % 1 < 0.035
    ez = dict(calm=0.07, smirk=0.045, deadpan=0.045, shocked=0.13, sad=0.05, warm=0.06).get(e, 0.07)
    tilt = dict(smirk=-0.5, deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + (s * tilt if e != 'smirk' or s > 0 else 0.1), s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    if S['hat_off']:                              # hat held against the chest
        r['hat'].location = (0.14, -0.47, -0.92)
        r['hat'].rotation_euler = (1.0, 0.15, 0.45)
        r['hat'].scale = (0.82, 0.82, 0.82)
    else:
        r['hat'].scale = (1, 1, 1)
        tip = S['hat_tip']
        r['hat'].location = (0, 0, 0.27 + (0.11 if e == 'shocked' else 0.0) + tip * 0.1 + S['hat_up'])
        r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.14, sad=0.22).get(e, 0.0) + tip * 0.35 - S['hat_up'] * 0.6, 0.07, S['hat_up'] * 0.8)
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for who in PEOPLE:
        e = S['face'][who]
        x = S[who].extra
        kk = dict(scared=1.3, shock=1.7, calm=1.0, sad=0.6, happy=0.8, closed=0.08, tired=0.5).get(e, 1.0)
        for ey in x['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], x['eye0'] * kk)
        x['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
        x['jaw'].location.z = -0.13 - (0.05 if e == 'shock' else 0.0)
        x['jaw'].scale = (1.5, 1, 1.6) if e == 'happy' else (1, 1, 1)


# ---------------------------------------------------------------- helpers for the shots
def lerp_col(a, b, k):
    k = max(0.0, min(1.0, k))
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


def scatter(pool, org, k, n, r, seed=0.0, size=None, grav=0.0, spin=0.0, start=0, flat=1.0):
    """Throw n pool objects outward from org; k 0..1. size=None keeps each object's own shape."""
    k = max(0.0, min(1.0, k))
    for i in range(n):
        o = pool[start + i]
        a, e = i * 2.4 + seed, ((i * 0.61) % 1) * 2.2 - 0.8
        d = r * (0.3 + 0.7 * ((i * 0.37) % 1)) * (1 - (1 - k) ** 2)
        o.location = (org[0] + math.cos(a) * math.cos(e) * d, org[1] + math.sin(a) * math.cos(e) * d * flat, org[2] + math.sin(e) * d - grav * k * k)
        o.rotation_euler = (spin * k * (1 + i % 3) + i, spin * k * 0.7 + i * 2, i)
        if size is not None:
            s = size * (0.6 + ((i * 0.73) % 1))
            o.scale = (s, s, s)


def drift(pool, org, t, n, box, speed, seed=0.0, start=0, spin=1.0):
    """n pool objects streaming past (dx, dy, dz box) with velocity `speed` (x, y, z), wrapping."""
    for i in range(n):
        o = pool[start + i]
        p = []
        for j in range(3):
            u = ((i * (0.37, 0.61, 0.83)[j] + seed * 0.21 + t * speed[j] / max(1e-3, box[j])) % 1) - 0.5
            p.append(org[j] + u * box[j])
        o.location = p
        o.rotation_euler = (t * spin * (1 + i % 3) + i, t * spin * 0.6 + i * 1.7, i)


def high(S, col='2E62B8', strength=1.0, clz=-16, cx=0.0, sun=4.0, suncol='FFF4E0'):
    A = show(S, 'sky')
    sky(S, col, strength)
    S['cl'].location = (cx, 0, clz)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(suncol)[:3]
    return A


def cabin(S, t=0.0, torn=False, shake=0.0):
    A = show(S, 'cabin')
    sky(S, '9AB8E8' if torn else '05060A', 1.6 if torn else 1.0)
    if torn:
        S['end'].location = (0, 12, -40)
        S['rip'].data.energy = 2600 + 1500 * math.sin(t * 31)
        for i, l in enumerate(S['lamps']):
            l.data.energy = 260 if int(t * 14 + i) % 3 else 20
    return A


def hill(S, mode='dusk'):
    A = show(S, 'hill')
    sky(S, dict(dusk='2A3458', night='0A1022', sad='3A4468').get(mode, '2A3458'), 1.0)
    if mode == 'night':
        S['moon'].data.energy, S['hglow'].data.energy, S['hfill'].data.energy = 45000, 6000, 1500
    return A


def wreck_rest(S, A):
    """Where the fuselage section comes to rest on the slope."""
    S['wreck'].location = A(6, 0, hz(6) + 1.75)
    S['wreck'].rotation_euler = (0.3, SL + 0.05, 0.22)
    S['furrow'].location = (0, 0, 0)


def lantern_at(S, loc, e=420):
    S['lantern'].location = loc
    S['lanl'].data.energy = e


def seat_rook(S, A, pose, expr, y=0.0):
    S['rook'].place(A(1.45, y + 0.05, 0.36), 0.0)
    S['rook'].apply(pose)
    S['face']['rook'] = expr


def hand(S, who, i=1):
    """World position of a rig's hand (0 = left, 1 = right) after it has been placed and posed."""
    bpy.context.view_layer.update()
    return S[who].hands[i].matrix_world.translation.copy()


def kneel(**over):
    d = dict(lL=(1.45, 1.55), lR=(0.15, 1.6), lift=-0.82, lean=0.45, aL=(1.1, 0.15, 0.5), aR=(1.0, 0.1, 0.7), head=(0.3, 0.0))
    d.update(over)
    return P('stand', **d)


# ---------------------------------------------------------------- shots: the sky
def blast(S, k, t, lt):
    A = high(S, cx=-((t * 60) % 60))
    e = ease((lt - 0.12) / 0.9)
    S['front'].location, S['front'].rotation_euler = (5 * e, -1.5 * e, -2.5 * e), (0.5 * e, 0.35 * e, -0.2 * e)
    S['rear'].location, S['rear'].rotation_euler = (-7 * e, 2 * e, 3 * e), (-0.7 * e, -0.5 * e, 0.3 * e)
    f = max(0.0, 1 - abs(lt - 0.16) / 0.3)
    S['flash'].location, S['flash'].scale = (2, 0, -1.5), (0.5 + 9 * f,) * 3
    S['flashl'].data.energy = 400000 * f
    if lt > 0.1:
        scatter(S['deb'], A(1, 0, -1), (lt - 0.1) / 1.0, 22, 24, grav=5, spin=9)
        scatter(S['smoke'], A(0, 0, 0), (lt - 0.1) / 1.2, 10, 12, seed=2, size=1.5)
    cam(S, A(lerp(42, 38, k), -32, 9), A(-1, 0, 0), 34, 0.05 * math.sin(t * 40) * max(0, 1 - lt))


def tail_fall(S, k, t, lt):
    A = high(S, '3A72C8', clz=-70)
    z = lerp(6, -3, k)
    S['wreck'].location = A(0, 0, z)
    S['wreck'].rotation_euler = (0.6 + t * 1.3, 0.9 + t * 0.8, t * 0.5)
    for i in range(10):
        u = (i + 1) / 10
        o = S['smoke'][i]
        o.location = A(1.0 * math.sin(i * 1.7 + t) - 3 * u, 0.8 * math.cos(i), z + 3 + u * 24)
        sc_ = 0.9 + 1.6 * u
        o.scale = (sc_, sc_, sc_)
    drift(S['deb'], A(-3, 3, 6), t, 14, (16, 4, 40), (0, 0, 9), spin=3)
    cam(S, A(lerp(13, 11, k), -22, -12), A(-1, 0, lerp(8, 5, k)), 32, lerp(-0.15, 0.1, k))


def fall_top(S, k, t, lt):
    A = high(S, '4A82D0', clz=lerp(-150, -95, k))
    S['cl'].scale = (1.6, 1.6, 1)
    S['wreck'].location = A(0, 0, 0)
    S['wreck'].rotation_euler = (t * 0.9, 0.5 + t * 0.6, 0.7 + t * 0.4)
    drift(S['deb'], A(0, 0, 6), t, 16, (24, 30, 30), (0, 0, 7), seed=3, spin=2.5)
    drift(S['streak'], A(0, 0, 0), t, 10, (26, 34, 60), (0, 0, 90))
    for o in S['streak'][:10]:
        o.rotation_euler = (0, 0, 0)
    cam(S, A(lerp(5, 3, k), -6, lerp(30, 22, k)), A(0, 0, 0), 30, lerp(0.0, 0.5, k))


def takeoff(S, k, t, lt):
    A = high(S, 'C8785A', 1.0, clz=lerp(-22, -28, k), cx=-((t * 40) % 60), sun=3.0, suncol='FFB070')
    S['jet'].rotation_euler = (0.04 * math.sin(t * 2), -0.3, 0)
    cam(S, A(lerp(36, 32, k), -34, -5), A(0, 0, 2), 32)


def cruise(S, k, t, lt):
    A = high(S, '2E62B8', clz=-17, cx=-((t * 50) % 60))
    S['jet'].location = (lerp(-4, 2, k), 0, 0.4 * math.sin(t * 1.3))
    S['jet'].rotation_euler = (0.03 * math.sin(t * 1.1), 0, 0)
    cam(S, A(lerp(16, 10, k), -66, lerp(13, 11, k)), A(0, 0, -2), 30)


def hold_flash(S, k, t, lt):
    A = high(S, '2E62B8', clz=-40)
    f = ease(lt / 0.25)
    e = ease((lt - 0.2) / 0.8)
    S['front'].location, S['front'].rotation_euler = (3 * e, 0, -1.5 * e), (0.25 * e, 0.2 * e, 0)
    S['rear'].location, S['rear'].rotation_euler = (-4 * e, 0, 2 * e), (-0.35 * e, -0.3 * e, 0)
    S['flash'].location = (2, 0, -1.8)
    S['flash'].scale = (0.3 + 5.5 * f * (1 - 0.5 * e),) * 3
    S['flashl'].data.energy = 300000 * f * (1 - 0.6 * e)
    scatter(S['deb'], A(2, 0, -2), lt / 0.9, 20, 16, seed=1, grav=6, spin=10)
    scatter(S['smoke'], A(1, 0, -1), lt / 1.1, 8, 7, seed=4, size=2.0)
    cam(S, A(lerp(20, 17, k), -11, -8), A(3, 0, -0.5), 28, 0.08 * math.sin(t * 37))


def debris_sky(S, k, t, lt):
    A = high(S, '5A78A8', 0.8, clz=lerp(-22, -14, k), sun=2.0)
    drift(S['deb'], A(0, 0, 0), t, 22, (44, 26, 40), (1.5, 0, -5), spin=0.8)
    S['wreck'].location = A(6, 14, lerp(4, -3, k))
    S['wreck'].rotation_euler = (t * 0.5, 0.8 + t * 0.4, 0.3)
    cam(S, A(lerp(-3, 0, k), -34, lerp(2, 0, k)), A(2, 0, -2), 32)


def plunge(S, k, t, lt):
    A = high(S, lerp_col('4A82D0', '5A6C98', k), clz=lerp(-75, -9, k * k))
    S['cl'].scale = (1.3, 1.3, 1.6)
    S['wreck'].location = A(0, 0, 0)
    S['wreck'].rotation_euler = (0.5 + t * 0.7, 0.75 + 0.2 * math.sin(t * 2), 0.5 + t * 0.35)
    drift(S['streak'], A(0, 0, 0), t, 12, (30, 24, 70), (0, 0, 130))
    for o in S['streak']:
        o.rotation_euler = (0, 0, 0)
    drift(S['snow'], A(0, 0, 0), t, 14, (26, 20, 50), (0, 0, 60), seed=2)
    for o in S['snow'][:14]:
        o.scale = (1.6, 1.6, 0.5)
    cam(S, A(11, lerp(-19, -15, k), 4), A(0, 0, 0.5), 32, 0.2 + 0.05 * math.sin(t * 23))


# ---------------------------------------------------------------- shots: the apron
def apron(S, mode='dusk'):
    A = show(S, 'apron')
    sky(S, dict(dusk='3A2E58', dawn='E8A070').get(mode), 1.0 if mode == 'dusk' else 1.1)
    if mode == 'dawn':
        S['akey'].data.energy = 5000
    return A


def rook_apron(S, k, t, lt):
    A = apron(S)
    S['rook'].place(A(2.5, 0, 0), 0.3)
    S['rook'].apply(P('cross', head=(0.05, -0.25 + 0.24 * math.sin(t * 4.2) * max(0, 1 - lt / 1.0))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(5.0, 4.3, k), lerp(-7.4, -5.8, k), 1.9), A(2.6, 0, 2.0), 40)


def rook_stairs(S, k, t, lt):
    A = apron(S)
    y = lerp(3.2, 9.2, k)
    z = max(0.0, (y - 4.0) / 0.66 * 0.3 + 0.37)
    S['rook'].place(A(-3, y, z), PI)
    w = walk(t, 2.1)
    S['rook'].apply(blend(w, P('hat', lL=w['lL'], lR=w['lR']), 1 - lt / 0.5))
    cam(S, A(lerp(-10.5, -9.5, k), lerp(0.5, 1.5, k), 1.3), A(-3, lerp(6, 8.5, k), 3.2), 34)


def jet_apron(S, k, t, lt):
    A = apron(S)
    cam(S, A(lerp(36, 32, k), lerp(-22, -19, k), 2.6), A(6, 14, 5.2), 30)


def rook_paper(S, k, t, lt):
    A = apron(S)
    S['rook'].place(A(-22, -4, 0), 0.25)
    up = ease((lt - 0.55) / 0.3)
    S['rook'].apply(P('stand', aL=(1.0, -0.05, 1.2, 0.5), aR=(1.0, -0.05, 1.2, 0.5), head=(lerp(0.4, 0.0, up), lerp(0.0, -0.2, up))))
    S['face']['rook'] = 'deadpan' if up < 0.5 else 'smirk'
    S['paper'].location = A(-22.2, -4.8, 1.62 - 0.25 * up)
    S['paper'].rotation_euler = (-0.6, 0, 0.25 + 0.03 * math.sin(t * 9))
    S['pov'].data.energy = 260
    cam(S, A(lerp(-20.4, -20.8, k), lerp(-9.4, -8.6, k), 2.3), A(-22, -4, 2.15), 48)


def rook_wrong(S, k, t, lt):
    A = apron(S, 'dawn')
    S['rook'].place(A(18, -6, 0), -0.45)
    tip = math.sin(PI * ease(lt / 1.0)) if lt < 1.0 else 0
    S['rook'].apply(blend(P('stand', head=(0, -0.2)), P('hat', head=(0.25, -0.2)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(15.2, 15.8, k), lerp(-11.6, -10.6, k), 1.2), A(18, -6, 2.2), 40)


def signoff(S, k, t, lt):
    A = apron(S, 'dawn')
    S['rook'].place(A(-8, -2, 0), 0.15)
    S['rook'].apply(P('stand', aL=(0.9, 0.25, 1.2), head=(0.05, 0)))
    S['face']['rook'] = 'smirk'
    c = max(0.0, min(1.0, (lt - 0.2) / 0.9))
    S['pin'].location = A(-8.75 - 0.2 * c, -2.75, 1.75 + 2.5 * math.sin(c * PI))
    S['pin'].rotation_euler = (t * 20, t * 8, 0)
    S['pin'].scale = (1.6, 1.6, 1.6)
    cam(S, A(lerp(-6.8, -7.1, k), lerp(-8.4, -7.2, k), 1.0), A(-8, -2, 2.05), 38)


# ---------------------------------------------------------------- shots: the cabin
def cabin_rip(S, k, t, lt):
    A = cabin(S, t, torn=True)
    j = 0.05 * math.sin(t * 43)
    S['vesna'].place(A(0.1 + j, 1.4 - 1.2 * k, 0.2 * math.sin(k * PI)), 0.15, -0.35 * k, 0.3 * k)
    S['vesna'].apply(P('up', aL=(2.0, 0.9, 0.5), aR=(1.5, 1.1, 0.7), lL=(0.4, 0.5), lR=(-0.2, 0.3), head=(-0.2, 0.3)))
    S['face']['vesna'] = 'shock'
    S['trolley'].location = A(0.2 + 0.6 * k, -0.4 - 1.6 * k, 0.3 * k)
    S['trolley'].rotation_euler = (0.5 * k, 0.3 * k, 0.6 * k)
    drift(S['deb'], A(0, 2, 2), t, 18, (4.2, 22, 3.0), (0, -30, 0), spin=6)
    for o in S['deb'][:18]:
        o.scale = (0.35, 0.25, 0.04)
    cam(S, A(0.2, -6.8, 2.0), A(0, 3, 1.9), 26, 0.12 * math.sin(t * 19) + 0.1 * k)


def greet(S, k, t, lt):
    A = cabin(S)
    S['vesna'].place(A(-0.55, -2.2, 0), 0.5)
    wave = 0.25 * math.sin(t * 9)
    S['vesna'].apply(P('stand', aR=(0.6, 0.9 + wave, 2.0, -0.6), head=(0.0, -0.35)))
    S['face']['vesna'] = 'happy'
    S['paxa'].place(A(0.25, lerp(-0.5, 1.6, k), 0), PI)
    S['paxa'].apply(walk(t, 1.4))
    S['paxb'].place(A(0.0, lerp(3.2, 5.0, k), 0), PI)
    S['paxb'].apply(walk(t + 0.3, 1.4))
    seat_rook(S, A, P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.7, -0.1, 1.5, 1.0), head=(0.0, 0.5), lean=0.1), 'deadpan', y=-4)
    cam(S, A(lerp(-0.2, 0.1, k), lerp(-9.2, -8.2, k), 2.2), A(0.3, -2.5, 1.9), 30)


def rook_seat(S, k, t, lt):
    A = cabin(S)
    tap = 0.25 * max(0.0, math.sin(t * 11))
    seat_rook(S, A, P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(1.25 + tap * 0.3, -0.15, 2.25, 0.75), head=(0.05, lerp(0.45, 0.1, ease(k * 1.5))), lean=0.1),
              'smirk', y=-4)
    S['vesna'].place(A(-0.2, lerp(1.5, 0.2, k), 0), 0.2)
    S['vesna'].apply(walk(t, 1.2))
    S['face']['vesna'] = 'happy'
    cam(S, A(lerp(0.1, 0.3, k), lerp(-7.9, -7.4, k), 2.35), A(1.35, -4, 2.3), 50)


def trolley(S, k, t, lt):
    A = cabin(S)
    y = lerp(2.6, 0.9, k)
    S['vesna'].place(A(0, y, 0), 0.0)
    w = walk(t, 1.3)
    S['vesna'].apply(P('stand', aL=(1.0, 0.05, 0.55), aR=(1.0, 0.05, 0.55), lL=w['lL'], lR=w['lR'], lean=0.12, head=(0.05, 0.2)))
    S['face']['vesna'] = 'happy'
    S['trolley'].location = A(0, y - 1.05, 0)
    seat_rook(S, A, P('sit', aL=(1.5, 0.75, 0.3, 0.0), aR=(0.7, -0.1, 1.5, 1.0), head=(0.0, -0.45), lean=0.05), 'calm', y=-2)
    cam(S, A(lerp(-0.1, 0.1, k), lerp(-6.2, -5.6, k), 2.5), A(0.45, -0.8, 1.8), 30)


def rook_brace(S, k, t, lt):
    A = cabin(S, t, torn=True)
    j = 0.06 * math.sin(t * 47)
    S['rook'].place(A(0.5 + j, -1.4 - 1.0 * k, 0.5 + 0.5 * math.sin(k * PI)), 0.2, -0.3, 0.35 + j)
    S['rook'].apply(P('up', aL=(2.4, 0.8, 0.5), aR=(2.2, 0.9, 0.6), lL=(0.5, 0.6), lR=(-0.2, 0.3), head=(-0.15, 0.2), lean=-0.15))
    S['face']['rook'] = 'shocked'
    S['hat_up'] = 0.5 * ease(lt / 0.3)
    for i, f in enumerate(S['fea']):
        u = (t * 0.9 + i * 0.37) % 1
        f.location = A(0.5 + math.cos(i * 2.3) * (0.5 + u), -1.6 - u * 3, 2.2 + math.sin(i * 1.7) * 0.8 + 0.5 * u)
        f.rotation_euler = (t * 3 + i, t * 2 + i * 2, i)
    drift(S['deb'], A(0, 2, 2), t, 16, (4.2, 20, 3.0), (0, -34, 0), seed=5, spin=6)
    for o in S['deb'][:16]:
        o.scale = (0.3, 0.22, 0.04)
    cam(S, A(-0.6, lerp(-6.6, -6.0, k), 1.5), A(0.5, -1.6, 2.5), 34, -0.15 + 0.1 * math.sin(t * 17))


def pinned(S, k, t, lt):
    A = cabin(S, t, torn=True)
    S['rip'].data.energy = 250
    sky(S, '6A80A8', 0.8)
    for l in S['lamps']:
        l.data.energy = 30
    S['cfill'].data.energy = 260
    S['vesna'].place(A(-0.3, 8.0, -0.42), -0.15, 0, 0.12)
    S['vesna'].apply(P('sit', lL=(1.5, 0.25), lR=(1.45, 0.4), aL=(0.3, 0.5, 0.4), aR=(0.4, 0.4, 0.6), head=(0.5, 0.35), lean=-0.1))
    S['face']['vesna'] = 'closed'
    S['trolley'].location = A(0.8, 7.5, 0.3)
    S['trolley'].rotation_euler = (-0.35, 0.5, 0.7)
    drift(S['snow'], A(0, 9, 2), t, 16, (5, 10, 4), (0, 0, 22), seed=1)
    for o in S['snow'][:16]:
        o.scale = (0.16, 0.16, 0.5)
    cam(S, A(-0.45, lerp(3.9, 4.6, k), 1.3), A(0.1, 7.9, 1.15), 30, 0.22 + 0.03 * math.sin(t * 21))


# ---------------------------------------------------------------- shots: the hillside
def rook_hat(S, k, t, lt):
    A = hill(S, 'sad')
    x = -20
    S['rook'].place(A(x, -9, hz(x)), 0.25)
    S['rook'].apply(P('stand', aR=(0.75, -0.2, 2.0, 1.1), head=(lerp(-0.3, 0.3, ease(k * 1.4)), 0.1)))
    S['hat_off'] = True
    S['face']['rook'] = 'sad'
    cam(S, A(x + lerp(1.8, 1.4, k), lerp(-15.0, -14.2, k), hz(x) + 1.7), A(x, -9, hz(x) + 2.15), 45)


def hill_wide(S, k, t, lt):
    A = hill(S)
    px, py, pz = lerp(-62, -15, k), lerp(14, 0, k), lerp(46, hz(-15) + 3.0, k)
    S['wreck'].location = A(px, py, pz)
    S['wreck'].rotation_euler = (0.4 + t * 1.2, 0.5, 0.2)
    S['wreck'].scale = (1.4, 1.4, 1.4)
    for i in range(8):
        o = S['smoke'][i]
        u = (i + 1) * 2.2
        o.location = A(px - u * 1.0, py + u * 0.3, pz + u * 0.95)
        o.scale = (1.2 + i * 0.3,) * 3
    rx, ry = 20.5, -23.0
    S['pov'].data.energy = 500
    S['rook'].place(A(rx, ry, hz(rx)), PI - 1.7)
    S['rook'].apply(blend(P('point', aR=(2.3, 0.2, 0.1), head=(-0.4, 0.0)), P('up', aL=(2.3, 0.5, 1.4), aR=(2.3, 0.5, 1.4), lean=0.3, lL=(0.4, 0.6), lR=(0.3, 0.6), lift=-0.2), (k - 0.6) * 4))
    S['face']['rook'] = 'shocked'
    cam(S, A(23.2, -27.4, hz(23) + 1.3), A(lerp(3, 6, k), -8, hz(5) + 9), 26, 0.03)


def impact(S, k, t, lt):
    A = hill(S)
    e = 1 - (1 - k) ** 2
    x = lerp(-15, 6, e)
    S['wreck'].location = A(x, 0, hz(x) + 1.75 + 1.2 * (1 - e))
    S['wreck'].rotation_euler = (0.3 + 0.5 * (1 - e) * math.sin(t * 20), SL + 0.05, 0.22 * e)
    S['furrow'].location = (0, 0, 0)
    scatter(S['snow'], A(x + 3, 0, hz(x) + 0.5), (lt * 1.6) % 1, 30, 8, size=1.5, grav=5, flat=0.8)
    scatter(S['deb'], A(x, 0, hz(x) + 2), lt / 1.0, 12, 9, seed=3, grav=4, spin=8)
    cam(S, A(lerp(20, 18, k), -15, hz(18) + 2.2), A(x * 0.5 + 3, 0, hz(3) + 2.5), 28, 0.07 * math.sin(t * 41))


def villager(S, k, t, lt):
    A = hill(S, 'night')
    wreck_rest(S, A)
    x, y = lerp(19, 15.5, k), lerp(-12, -8.5, k)
    S['bruno'].place(A(x, y, hz(x)), PI + 0.75)
    w = walk(t, 1.5)
    S['bruno'].apply(P('stand', lL=w['lL'], lR=w['lR'], aL=w['aL'], aR=(1.2, 0.3, 0.9), lean=0.12, head=(-0.05, 0)))
    S['face']['bruno'] = 'scared'
    hp = hand(S, 'bruno')
    lantern_at(S, (hp[0], hp[1], hp[2] - 0.4), 700)
    cam(S, A(lerp(23.5, 22.5, k), lerp(-18.5, -17, k), hz(22) + 2.4), A(10, -3, hz(10) + 2.4), 32)


def in_wreck(S, A):
    """Vesna at the open end of the fuselage, the trolley across her; Bruno kneels beside her."""
    wreck_rest(S, A)
    S['wreck'].rotation_euler = (0.3, SL + 0.05, 0.22)
    S['vesna'].place(A(12.0, 1.3, hz(12) + 0.42), -PI / 2 - 0.2, -PI / 2 + 0.12, 0)
    S['vesna'].apply(P('stand', aL=(0.3, 0.7, 0.3), aR=(0.2, 0.5, 0.5), head=(0.1, 0.3)))
    S['trolley'].location = A(10.4, 1.25, hz(10.4) + 0.5)
    S['trolley'].rotation_euler = (1.2, 0.1, 1.3)
    S['bruno'].place(A(13.3, -0.9, hz(13.3)), PI + 0.5)
    S['face']['bruno'] = 'calm'


def wreck_in(S, k, t, lt):
    A = hill(S, 'night')
    in_wreck(S, A)
    S['bruno'].apply(kneel(aR=(1.15 + 0.1 * math.sin(t * 5), 0.1, 0.6), head=(0.35, 0.1)))
    S['face']['vesna'] = 'closed' if (t * 1.3) % 1 < 0.6 else 'tired'
    lantern_at(S, A(13.2, 1.9, hz(13.2) + 0.3), 900)
    S['pov'].data.energy = 300
    cam(S, A(lerp(16.6, 16.0, k), lerp(4.0, 3.4, k), hz(16.3) + 1.5), A(12.6, 0.3, hz(12.6) + 1.0), 34)


def rook_lantern(S, k, t, lt):
    A = hill(S, 'night')
    in_wreck(S, A)
    S['bruno'].apply(kneel(head=(0.4, 0.0)))
    rx, ry = 15.2, -2.2
    S['rook'].place(A(rx, ry, hz(rx)), 0.95)
    S['rook'].apply(P('stand', aR=(2.0, 1.15, 0.2), aL=(0.3, 0.3, 0.6), head=(0.15, 0.7)))
    S['face']['rook'] = 'sad'
    hp = hand(S, 'rook')
    lantern_at(S, (hp[0], hp[1], hp[2] - 0.42), 320)
    S['pov'].data.energy = 250
    cam(S, A(lerp(18.4, 17.8, k), lerp(-6.6, -6.0, k), hz(18) + 1.3), A(14.6, -1.5, hz(14.6) + 2.5), 36)


def rescuers(S, k, t, lt):
    A = hill(S, 'night')
    wreck_rest(S, A)
    for i, o in enumerate(S['resc']):
        x, y = 4 + i * 2.6 + lerp(0, 1.0, k), lerp(30, 21, k) + (i % 2) * 4 + (i % 3) * 2
        o.location = A(x, y, hz(x) + 2.2 + 0.25 * math.sin(t * 7 + i * 2))
    S['bruno'].place(A(13.5, 6.5, hz(13.5)), PI + 0.2)
    wv = math.sin(t * 10)
    S['bruno'].apply(P('up', aL=(2.7, 0.5 + 0.3 * wv, 0.2), aR=(2.7, 0.5 - 0.3 * wv, 0.2), head=(-0.2, 0)))
    S['rook'].place(A(16.6, 4.6, hz(16.6)), PI - 0.6)
    S['rook'].apply(P('point', aR=(1.6, 0.4, 0.1), aL=(2.6, 0.6 + 0.3 * wv, 0.3), head=(-0.1, 0.5)))
    S['face']['rook'] = 'shocked'
    lantern_at(S, A(14.8, 5.4, hz(14.8) + 0.3), 800)
    cam(S, A(lerp(19.5, 18.8, k), lerp(-3.5, -2.5, k), hz(19) + 2.0), A(11, 16, hz(11) + 3.6), 30)


# ---------------------------------------------------------------- shots: the ward
def ward(S):
    A = show(S, 'ward')
    sky(S, '10141A', 1.0)
    return A


def ward_bed(S, k, t, lt):
    A = ward(S)
    S['patient'].place(A(-0.3, 2.6, 1.32), -PI / 2, -PI / 2 + 0.3, 0)
    S['patient'].apply(P('stand', aL=(0.3, 0.3, 0.3), aR=(0.3, 0.3, 0.3), head=(0.25, lerp(0.0, 0.5, ease(k * 1.5)))))
    S['face']['patient'] = 'tired' if k < 0.35 else 'calm'
    S['rook'].place(A(-2.1, 0.7, 0), PI / 2 + 0.5)
    S['rook'].apply(P('stand', aR=(0.75, -0.2, 2.0, 1.1), head=(0.15, -0.3)))
    S['hat_off'] = True
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(-1.6, -1.2, k), lerp(-7.8, -7.2, k), 2.7), A(-0.5, 2.0, 1.7), 30)


def walks(S, k, t, lt):
    A = ward(S)
    x, y = lerp(2.4, 0.6, k), lerp(0.6, -1.6, k)
    w = walk(t, 0.9)
    S['patient'].place(A(x, y, 0), -0.6)
    S['patient'].apply(P('stand', lL=(w['lL'][0] * 0.6, w['lL'][1] * 0.6), lR=(w['lR'][0] * 0.6, w['lR'][1] * 0.6), aR=(0.5, 0.25, 0.5), aL=(0.2, 0.5, 0.4),
                         lean=0.08, head=(0.0, 0.1)))
    S['face']['patient'] = 'happy'
    hp = hand(S, 'patient')
    S['cane'].location = (hp[0], hp[1], hp[2] - 0.9)
    S['cane'].rotation_euler = (0.08 * w['lL'][0], 0.05, 0)
    S['rook'].place(A(x + 1.9, y + 1.2, 0), -0.75)
    S['rook'].apply(P('stand', aL=(1.1, 0.5, 0.5), aR=(1.1, 0.5, 0.5), lL=w['lR'], lR=w['lL'], head=(0.1, 0.2), lean=0.15))
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(-2.2, -1.8, k), lerp(-7.4, -7.0, k), 1.7), A(lerp(2.4, 1.4, k), 0, 1.85), 32)


def rook_caw(S, k, t, lt):
    A = ward(S)
    j = 0.02 * math.sin(t * 45) * max(0, 1 - lt / 0.6)
    S['rook'].place(A(-2.2 + j, -1.0, 0), 0.25)
    S['rook'].apply(P('stand', aL=(0.5, 1.2, 0.4), aR=(0.5, 1.2, 0.4), head=(-0.1, 0.0), lean=-0.1))
    S['face']['rook'] = 'shocked'
    S['hat_up'] = 0.24 * math.sin(PI * min(1, lt / 0.9))
    cam(S, A(lerp(-1.5, -1.6, k), lerp(-5.2, -4.6, k), 2.5), A(-2.2, -1.0, 2.55), 50)


# ---------------------------------------------------------------- stills for the case board
def photo_vesna(S, k, t, lt):
    A = apron(S, 'dawn')
    S['vesna'].place(A(-3, 2.0, 0), 0.2)
    S['vesna'].apply(P('stand', aR=(0.6, 0.9, 2.0, -0.6), head=(0, 0.1)))
    S['face']['vesna'] = 'happy'
    cam(S, A(-2.4, -2.6, 2.5), A(-3, 2.0, 2.3), 55)


def photo_jet(S, k, t, lt):
    A = high(S, '2E62B8', clz=-17)
    cam(S, A(34, -44, 8), A(0, 0, 0), 34)


SHOTS3D = {f.__name__: f for f in (
    blast, cabin_rip, tail_fall, fall_top, rook_apron, rook_stairs, jet_apron, greet, rook_seat, takeoff, cruise, trolley, hold_flash,
    rook_brace, debris_sky, rook_hat, pinned, plunge, hill_wide, impact, villager, wreck_in, rook_lantern, rescuers, ward_bed, walks,
    rook_caw, rook_paper, rook_wrong, signoff)}
STILLS = dict(vesna=photo_vesna, jet=photo_jet)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it: Belgrade in 1971, the airline medical, the crew office, boarding in Copenhagen,
# the villager who heard her, the stretcher, the ward step by step, the flight home, the desk job, the 1985 ceremony,
# the phone call and the 2009 dispute.
ORG.update(street=(1600, 0, 0), clinic=(2000, 0, 0), office=(2400, 0, 0), stage=(2800, 0, 0))
CIVIL = dict(top='C8503A', pants='3A3050', hand='E2B48C', boot='2A2026', fore='E2B48C')
FRIEND = dict(top='24408A', pants='1B2F66', hand='D9AC8A', boot='15151C', fore='24408A')
DOCTOR = dict(top='E8ECEE', pants='5A6470', hand='D9AC8A', boot='2A2A30')
CLERK = dict(top='8A8468', pants='3A3A34', hand='C99A78', boot='1E1A16')
MC = dict(top='20222C', pants='20222C', hand='E2B48C', boot='101014')
XCAST = ('civil', 'friend', 'doctor', 'clerk', 'mc')


def woman_head(hair, cap=False):
    def fn(head):
        x = face(head, 'D9AC8A', hair, 'C09070')
        add('ico_sphere', hair, (0, 0.06, 0.1), scale=(1.02, 1.0, 1.0), radius=0.31, subdivisions=1, parent=head)
        add('cube', hair, (0, 0.24, -0.16), scale=(0.5, 0.14, 0.4), size=1, parent=head)
        if cap:
            add('cylinder', NAVY, (0, -0.02, 0.4), rot=(-0.15, 0, 0), radius=0.2, depth=0.13, vertices=8, parent=head)
            add('cube', 'FFC233', (0, -0.21, 0.4), scale=(0.07, 0.02, 0.05), size=1, parent=head, rough=0.4)
        return x
    return fn


def room(r, w_, d, floor, wall, side, dado=None, hgt=7.0):
    add('cube', floor, (0, 0, -0.1), scale=(w_, d + 4, 0.2), size=1, parent=r)
    add('cube', wall, (0, d / 2 - 1, hgt / 2), scale=(w_, 0.2, hgt), size=1, parent=r)
    for s in (-1, 1):
        add('cube', side, (s * w_ / 2, 0, hgt / 2), scale=(0.2, d + 4, hgt), size=1, parent=r)
    if dado:
        add('cube', dado, (0, d / 2 - 1.12, 0.8), scale=(w_, 0.06, 1.6), size=1, parent=r)
    return d / 2 - 1


def set_street(r):
    add('plane', '3A3642', (0, 0, 0), size=200, parent=r)
    add('cube', '6A6672', (0, 3.4, 0.08), scale=(110, 5.0, 0.16), size=1, parent=r)
    for i in range(-18, 19):
        add('cube', '4E4A56', (i * 3, 0.95, 0.09), scale=(2.6, 0.12, 0.18), size=1, parent=r)
    cols = ('8A6A54', '6A7088', '9A8468', '5E5A70', '7A5A4A', '80785E')
    for i, cx in enumerate(range(-50, 51, 10)):
        hgt = (11, 14, 10, 13, 12, 15, 11, 13, 10, 14, 12)[i]
        add('cube', cols[i % 6] if cx else '7A6248', (cx, 10, hgt / 2), scale=(9.8, 8, hgt), size=1, parent=r)
        add('cube', '3A3038', (cx, 10, hgt + 0.3), scale=(10.2, 8.4, 0.6), size=1, parent=r)
        for z in (5.6, 8.8, 12.0):
            if z > hgt - 1.6:
                continue
            for j, wx in enumerate((-3, 0, 3)):
                lit = (i * 3 + j + int(z)) % 3 != 0
                add('cube', 'FFD890' if lit else '2A3040', (cx + wx, 5.95, z), scale=(1.5, 0.1, 2.0), size=1, parent=r, emit=2.2 if lit else 0.0)
        if cx:
            add('cube', '2A2630', (cx + 2.6, 5.95, 1.7), scale=(1.7, 0.1, 3.4), size=1, parent=r)
            add('cube', 'C8B890', (cx - 1.6, 5.95, 2.2), scale=(4.0, 0.1, 2.4), size=1, parent=r, emit=0.7)
    # the record shop
    add('cube', 'FFE2B0', (-1.2, 5.9, 2.2), scale=(5.6, 0.1, 2.8), size=1, parent=r, emit=3.0)
    add('cube', '2A2026', (3.3, 5.9, 1.7), scale=(1.7, 0.1, 3.4), size=1, parent=r)
    add('cube', 'FF7A1A', (0, 5.0, 3.9), rot=(0.35, 0, 0), scale=(9.6, 2.2, 0.1), size=1, parent=r)
    for i in range(5):
        add('cube', 'F4EEDF', (-3.8 + i * 1.9, 4.98, 3.93), rot=(0.35, 0, 0), scale=(0.7, 2.2, 0.1), size=1, parent=r)
    for i, x in enumerate((-3.2, -1.3, 0.6)):
        add('cylinder', '15151C', (x, 5.74, 2.3), rot=(PI / 2, 0, 0), radius=0.72, depth=0.05, vertices=14, parent=r)
        add('cylinder', ('FF7A1A', 'E5392F', 'FFC233')[i], (x, 5.7, 2.3), rot=(PI / 2, 0, 0), radius=0.24, depth=0.05, vertices=10, parent=r, emit=0.6)
    add('cube', '6A4A2A', (-2.4, 3.6, 0.6), scale=(1.0, 1.0, 0.9), size=1, parent=r)
    add('cube', '3A2A20', (-2.4, 3.6, 1.15), scale=(1.1, 0.9, 0.2), size=1, parent=r)
    add('cone', 'C89A3A', (-2.9, 3.95, 1.75), rot=(-0.5, -0.5, 0), radius1=0.5, radius2=0.06, depth=0.9, vertices=8, parent=r, rough=0.35)
    disc = empty((-2.25, 3.55, 1.28), r)
    add('cylinder', '15151C', (0, 0, 0), radius=0.4, depth=0.03, vertices=14, parent=disc)
    add('cylinder', 'FF7A1A', (0, 0, 0.02), radius=0.13, depth=0.03, vertices=8, parent=disc, emit=0.8)
    add('cube', 'F4EEDF', (0.26, 0, 0.02), scale=(0.12, 0.05, 0.02), size=1, parent=disc)
    for x in (-7.5, 8.5):
        add('cylinder', '2A2630', (x, 1.6, 3.0), radius=0.1, depth=6, vertices=6, parent=r)
        add('ico_sphere', 'FFE2B0', (x, 1.6, 6.2), radius=0.36, subdivisions=1, parent=r, emit=9)
        light((x, 1.2, 5.6), 700, 'FFD8A0', kind='POINT', parent=r)
    add('cube', 'A03A2A', (-13, -2.6, 0.8), scale=(4.6, 1.9, 0.9), size=1, parent=r)
    add('cube', 'C8D8E8', (-13.2, -2.6, 1.6), scale=(2.3, 1.7, 0.8), size=1, parent=r, rough=0.3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', '15151C', (-13 + sx * 1.5, -2.6 + sy * 0.95, 0.42), rot=(PI / 2, 0, 0), radius=0.42, depth=0.3, vertices=8, parent=r)
    for x in (13.5, -20):
        add('cylinder', '3A2A20', (x, 2.2, 1.6), radius=0.2, depth=3.2, vertices=5, parent=r)
        add('ico_sphere', '6A5A3A', (x, 2.2, 4.4), scale=(1, 1, 1.2), radius=1.9, subdivisions=1, parent=r)
    aim = empty((0, 2.5, 2), r)
    aimed((-9, -10, 8), 3600, 'FFD8A8', 6.0, aim, r)
    aimed((10, -8, 3), 900, '8A7AD0', 5.0, aim, r)
    aimed((5, 4.5, 7), 1200, 'FF7A1A', 3.0, aim, r)
    aimed((-20, -30, 30), 1.6, 'FFC890', 1.0, aim, r, kind='SUN')
    return dict(disc=disc)


def set_clinic(r):
    back = room(r, 18, 12, 'A89878', 'D8D0B8', 'CCC4AC', '6A8A7A')
    add('cylinder', 'F4F0E6', (3.6, back - 0.12, 3.7), rot=(PI / 2, 0, 0), radius=1.35, depth=0.12, vertices=16, parent=r, emit=0.5)
    add('torus', '3A3A44', (3.6, back - 0.18, 3.7), rot=(PI / 2, 0, 0), major_radius=1.38, minor_radius=0.07, major_segments=16, minor_segments=4, parent=r)
    for i in range(9):
        a = -1.25 + i * 2.5 / 8
        add('cube', 'E5392F' if i < 3 else '2A2630', (3.6 + math.sin(a) * 1.08, back - 0.2, 3.7 + math.cos(a) * 1.08), rot=(0, a, 0),
            scale=(0.07, 0.04, 0.24), size=1, parent=r)
    needle = empty((3.6, back - 0.24, 3.7), r)
    add('cube', 'E5392F', (0, 0, 0.5), scale=(0.08, 0.04, 1.0), size=1, parent=needle, emit=0.6)
    add('cylinder', '2A2630', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.13, depth=0.08, vertices=8, parent=needle)
    add('cube', 'F4EEDF', (-5.6, back - 0.12, 3.7), scale=(1.9, 0.06, 2.7), size=1, parent=r)
    for j in range(5):
        for i in range(2 + j):
            sz = 0.34 - j * 0.05
            add('cube', '2A2630', (-5.6 + (i - (1 + j) / 2) * (sz + 0.14), back - 0.17, 4.7 - j * 0.5), scale=(sz, 0.03, sz), size=1, parent=r)
    add('cube', 'E0B030', (-2.4, back - 0.12, 2.7), scale=(0.34, 0.06, 5.2), size=1, parent=r)
    for i in range(10):
        add('cube', '2A2630', (-2.4, back - 0.17, 0.5 + i * 0.5), scale=(0.34 if i % 2 else 0.2, 0.03, 0.04), size=1, parent=r)
    add('cube', 'DCEEFF', (-0.3, back - 0.1, 4.6), scale=(2.6, 0.06, 2.0), size=1, parent=r, emit=1.6)
    add('cube', 'F4F0E6', (-0.3, back - 0.14, 4.6), scale=(0.1, 0.08, 2.1), size=1, parent=r)
    add('cube', 'F4F0E6', (-7.0, 2.6, 1.0), scale=(2.2, 4.4, 0.3), size=1, parent=r)
    add('cube', '8A9AA0', (-7.0, 2.6, 0.45), scale=(1.9, 4.0, 0.9), size=1, parent=r)
    add('cube', 'E8ECEE', (7.6, 3.6, 2.3), scale=(2.2, 1.7, 4.6), size=1, parent=r)
    add('cube', 'E5392F', (7.6, 2.72, 3.4), scale=(0.9, 0.05, 0.26), size=1, parent=r)
    add('cube', 'E5392F', (7.6, 2.72, 3.4), scale=(0.26, 0.05, 0.9), size=1, parent=r)
    add('cube', '8A6A4A', (-1.5, 0.6, 1.5), scale=(3.6, 1.6, 0.12), size=1, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cube', '6A4A2A', (-1.5 + sx * 1.6, 0.6 + sy * 0.65, 0.74), scale=(0.14, 0.14, 1.48), size=1, parent=r)
    add('cylinder', 'FF7A1A', (-2.9, 0.75, 1.86), radius=0.24, depth=0.6, vertices=8, parent=r, rough=0.5)
    add('cone', 'FF7A1A', (-2.9, 0.75, 2.24), radius1=0.24, radius2=0.06, depth=0.18, vertices=8, parent=r)
    add('cube', '2A2630', (-3.22, 0.75, 1.9), scale=(0.3, 0.08, 0.34), size=1, parent=r)
    add('cylinder', '8A9AA0', (2.6, 1.4, 0.4), radius=0.1, depth=0.8, vertices=6, parent=r)
    add('cylinder', '5A6A70', (2.6, 1.4, 0.82), radius=0.5, depth=0.1, vertices=10, parent=r)
    add('cube', 'FFF8E8', (0, 1, 6.9), scale=(4, 1.2, 0.1), size=1, parent=r, emit=3)
    aim = empty((0.5, 1.5, 2.0), r)
    aimed((-4, -8, 5), 800, 'FFF0DC', 5.0, aim, r)
    aimed((7, -6, 3), 300, 'A0C0FF', 4.0, aim, r)
    light((0, 1, 6.2), 500, 'FFF2DC', kind='POINT', parent=r)
    return dict(needle=needle)


def set_office(r):
    back = room(r, 18, 12, '5A4A3A', '6A7A70', '5E6C64', '4A3A2A')
    add('cube', 'E8E2D2', (-4.2, back - 0.12, 3.6), scale=(5.6, 0.08, 3.4), size=1, parent=r)
    add('cube', '4A3222', (-4.2, back - 0.1, 3.6), scale=(5.9, 0.05, 3.7), size=1, parent=r)
    for j in range(4):
        add('cube', '8A8478', (-4.2, back - 0.18, 2.5 + j * 0.75), scale=(5.4, 0.03, 0.04), size=1, parent=r)
        for i in range(5):
            if (i + j * 2) % 3 == 0:
                continue
            add('cube', ('5EC8F0', '8ACB5A', 'E8B43A', 'B48AE8')[(i + j) % 4], (-6.2 + i * 1.0, back - 0.2, 2.86 + j * 0.75), scale=(0.8, 0.04, 0.4),
                size=1, parent=r)
    otag = add('cube', 'FF7A1A', (-2.2, back - 0.24, 4.36), scale=(0.86, 0.05, 0.44), size=1, parent=r, emit=1.0)
    wday = add('cube', 'CFE4FF', (4.6, back - 0.1, 3.8), scale=(4.4, 0.06, 3.0), size=1, parent=r, emit=2.4)
    wnight = add('cube', '1A2A50', (4.6, back - 0.1, 3.8), scale=(4.4, 0.06, 3.0), size=1, parent=r, emit=0.6)
    for x in (2.4, 4.6, 6.8):
        add('cube', '3A2A20', (x, back - 0.16, 3.8), scale=(0.14, 0.1, 3.2), size=1, parent=r)
    for z in (2.25, 3.8, 5.35):
        add('cube', '3A2A20', (4.6, back - 0.16, z), scale=(4.6, 0.1, 0.14), size=1, parent=r)
    ojet = empty((0, 0, -30), r)
    add('cube', 'FFFFFF', (0, 0, 0), scale=(0.9, 0.03, 0.14), size=1, parent=ojet, emit=1.5)
    add('cube', 'FFFFFF', (-0.05, 0, 0), rot=(0, 0, 0), scale=(0.2, 0.03, 0.7), size=1, parent=ojet, emit=1.5)
    add('cube', 'FFFFFF', (-0.4, 0, 0.14), scale=(0.14, 0.03, 0.26), size=1, parent=ojet, emit=1.5)
    add('cube', '4A3222', (0.5, 1.2, 1.5), scale=(5.4, 2.2, 0.14), size=1, parent=r)
    add('cube', '3E2A1C', (0.5, 0.2, 0.75), scale=(5.4, 0.12, 1.5), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '3E2A1C', (0.5 + s * 2.64, 1.2, 0.75), scale=(0.12, 2.2, 1.5), size=1, parent=r)
    add('cube', '15151C', (-1.3, 0.9, 1.67), scale=(0.66, 0.5, 0.2), size=1, parent=r)
    add('cylinder', 'D8D4C8', (-1.3, 0.86, 1.78), radius=0.16, depth=0.03, vertices=10, parent=r)
    handset = add('cube', '15151C', (-1.3, 1.02, 1.84), scale=(0.8, 0.16, 0.13), size=1, parent=r)
    add('cube', '3A4A5A', (1.7, 1.1, 1.76), scale=(1.0, 0.75, 0.38), size=1, parent=r)
    add('cube', 'F4EEDF', (1.7, 1.42, 2.15), rot=(-0.2, 0, 0), scale=(0.8, 0.03, 0.6), size=1, parent=r)
    for i, (x, n) in enumerate(((0.1, 5), (2.75, 3), (-2.3, 2))):
        for j in range(n):
            add('cube', 'E8E2D2' if j % 2 else 'D8D0BC', (x + 0.03 * (j % 2), 1.85, 1.6 + j * 0.07), rot=(0, 0, 0.05 * j), scale=(0.6, 0.8, 0.06), size=1, parent=r)
    add('cylinder', '2A2630', (-2.6, 1.3, 1.9), radius=0.04, depth=0.7, vertices=5, parent=r)
    add('cone', 'FF7A1A', (-2.6, 1.3, 2.34), radius1=0.34, radius2=0.12, depth=0.3, vertices=8, parent=r, emit=2.0)
    olamp = light((-2.6, 1.1, 2.1), 160, 'FFC070', kind='POINT', parent=r)
    add('cube', '6A4A2A', (0.5, 2.7, 0.75), scale=(1.1, 1.0, 0.14), size=1, parent=r)
    add('cube', '6A4A2A', (0.5, 3.2, 1.6), scale=(1.1, 0.12, 1.7), size=1, parent=r)
    add('cube', '5A6470', (7.8, 3.6, 2.0), scale=(1.7, 1.7, 4.0), size=1, parent=r)
    add('cube', '5A6470', (6.2, 3.2, 0.95), scale=(1.5, 1.5, 1.9), size=1, parent=r)
    for z in (0.5, 1.4, 2.4, 3.3):
        add('cube', 'C8CCD4', (7.8 if z > 2 else 6.2, 2.72 if z > 2 else 2.42, z), scale=(0.6, 0.05, 0.1), size=1, parent=r, rough=0.3)
    add('cylinder', '3A2A20', (-7.8, 3.4, 2.6), radius=0.08, depth=5.2, vertices=6, parent=r)
    add('cone', '6A5236', (-7.8, 3.4, 5.3), radius1=0.5, radius2=0.3, depth=0.4, vertices=8, parent=r)
    add('cube', '2E3444', (-7.5, 3.3, 4.0), scale=(0.5, 0.4, 1.8), size=1, parent=r)
    add('cube', 'C8B890', (-8.85, 0.6, 3.6), scale=(0.06, 2.6, 2.0), size=1, parent=r)
    add('cube', 'FFF8E8', (0, 1, 6.9), scale=(5, 1.2, 0.1), size=1, parent=r, emit=2.5)
    aim = empty((0.5, 1.8, 2.2), r)
    okey = aimed((-5, -8, 5), 800, 'FFE8C8', 5.0, aim, r)
    ofill = aimed((7, -6, 3), 280, '8A9AD0', 4.0, aim, r)
    otop = light((0, 1, 6.2), 420, 'FFF2DC', kind='POINT', parent=r)
    return dict(otag=otag, wday=wday, wnight=wnight, ojet=ojet, handset=handset, olamp=olamp, okey=okey, ofill=ofill, otop=otop)


def set_stage(r):
    add('plane', '1E1A26', (0, 0, 0), size=80, parent=r)
    add('cube', '5A3A2A', (0, 5.5, 0.4), scale=(24, 7, 0.8), size=1, parent=r)
    add('cube', 'C89A3A', (0, 1.98, 0.74), scale=(24, 0.06, 0.12), size=1, parent=r, emit=1.0, rough=0.4)
    for i in range(24):
        add('cube', '8A2A4A' if i % 2 else '6A1E3A', (-11.5 + i, 9 + 0.12 * (i % 2), 5.2), scale=(1.02, 0.3, 9.6), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '3A1020', (s * 12.2, 5, 5), scale=(1.4, 9, 10), size=1, parent=r)
        add('cube', '4A1428', (s * 10.4, 2.6, 5), rot=(0, 0, s * 0.25), scale=(2.6, 0.3, 10), size=1, parent=r)
        add('cone', 'FFD866', (s * 5.0, 8.74, 6.9), rot=(PI / 2, 0, 0), radius1=0.5, radius2=0.0, depth=0.1, vertices=5, parent=r, emit=2.5)
    add('cube', '4A1428', (0, 2.4, 9.6), scale=(26, 1.0, 1.6), size=1, parent=r)
    add('cube', 'C89A3A', (0, 2.3, 8.75), scale=(26, 1.0, 0.16), size=1, parent=r, emit=0.8, rough=0.4)
    add('cube', 'C89A3A', (0, 8.74, 6.9), scale=(7.6, 0.1, 1.7), size=1, parent=r, emit=1.4, rough=0.4)
    add('cube', '3A1020', (0, 8.68, 6.9), scale=(7.0, 0.1, 1.2), size=1, parent=r)
    for i in range(9):
        add('ico_sphere', 'FFE2B0', (-10 + i * 2.5, 2.1, 0.92), radius=0.14, subdivisions=1, parent=r, emit=10)
    add('cube', '3A2A20', (4.6, 4.2, 1.75), scale=(1.3, 0.9, 1.9), size=1, parent=r)
    add('cube', 'C89A3A', (4.6, 3.74, 2.0), scale=(0.7, 0.04, 0.7), size=1, parent=r, emit=0.8, rough=0.4)
    add('cylinder', '8A90A0', (4.6, 4.0, 3.0), rot=(0.3, 0, 0), radius=0.03, depth=0.7, vertices=5, parent=r)
    add('ico_sphere', '2A2630', (4.6, 3.88, 3.36), radius=0.1, subdivisions=1, parent=r)
    k = 0
    for row, y in enumerate((-1.5, -3.5, -5.5)):
        for i in range(15):
            x = -10.5 + i * 1.5 + 0.75 * (row % 2)
            if row == 1 and abs(x - 3) < 1.3:
                continue
            add('cone', ('17141E', '1E1A28', '14121A')[k % 3], (x, y, 0.9), radius1=0.52, radius2=0.36, depth=1.5, vertices=6, parent=r)
            add('ico_sphere', ('221E2C', '1A1722', '2A2434')[k % 3], (x, y, 1.95), radius=0.3, subdivisions=1, parent=r)
            k += 1
    aim = empty((0, 5, 2.6), r)
    spot = light((0, -3, 12), 9000, 'FFF2D8', kind='SPOT', spot=0.62, target=aim, parent=r)
    aimed((-9, 6, 5), 900, 'FF7A1A', 3.0, aim, r)
    aimed((9, 0, 6), 700, 'B080FF', 4.0, aim, r)
    sfill = aimed((0, -9, 3.4), 500, '8A7AD8', 6.0, empty((0, -2, 2), r), r)
    return dict(spot=spot, sfill=sfill)


def extend(S):
    for name, fn in (('street', set_street), ('clinic', set_clinic), ('office', set_office), ('stage', set_stage)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['civil'] = K.Rig(CIVIL, attendant_head(cap=False))
    S['friend'] = K.Rig(FRIEND, woman_head('C8A050', cap=True))
    S['doctor'] = K.Rig(DOCTOR, man_head('D9AC8A', '9A9A9A', tash=True))
    S['clerk'] = K.Rig(CLERK, man_head('C99A78', '3A2A20'))
    S['mc'] = K.Rig(MC, man_head('E2B48C', '2A2018'))
    S['notes'] = []
    for i in range(6):
        o = add('ico_sphere', 'FF7A1A' if i % 2 else 'FFC233', FAR, radius=0.11, subdivisions=1, emit=3)
        add('cube', '2A2630', (0.09, 0, 0.17), scale=(0.03, 0.03, 0.34), size=1, parent=o)
        S['notes'].append(o)
    S['cups'] = [add('cylinder', 'F4F0E6', FAR, radius=0.11, depth=0.2, vertices=7) for _ in range(8)]
    S['stretch'] = empty(FAR)
    for s in (-1, 1):
        add('cylinder', '6A4A2A', (s * 0.5, 0, 0), rot=(PI / 2, 0, 0), radius=0.045, depth=4.0, vertices=5, parent=S['stretch'])
    add('cube', 'D8D4C8', (0, 0, 0.0), scale=(0.96, 2.9, 0.06), size=1, parent=S['stretch'])
    add('cube', '8A7A5A', (0, 0.3, 0.2), scale=(0.9, 2.1, 0.34), size=1, parent=S['stretch'])
    add('cube', 'F4F0E6', (0, -1.15, 0.12), scale=(0.7, 0.5, 0.16), size=1, parent=S['stretch'])
    add('ico_sphere', 'E2B48C', (0, -1.1, 0.34), radius=0.24, subdivisions=1, parent=S['stretch'])
    add('ico_sphere', '5A3620', (0, -1.2, 0.36), scale=(1.05, 1, 0.9), radius=0.26, subdivisions=1, parent=S['stretch'])
    S['clip'] = empty(FAR)
    add('cube', '6A4A2A', (0, 0, 0), scale=(0.44, 0.04, 0.6), size=1, parent=S['clip'])
    add('cube', 'F4EEDF', (0, -0.03, -0.02), scale=(0.38, 0.02, 0.5), size=1, parent=S['clip'])
    S['medal'] = empty(FAR)
    add('cylinder', 'FFD866', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.17, depth=0.04, vertices=10, parent=S['medal'], rough=0.25, emit=2.0)
    add('cube', 'E5392F', (0, 0, 0.3), scale=(0.12, 0.02, 0.36), size=1, parent=S['medal'])
    S['toes'] = [add('cube', 'B8CCE0', FAR, scale=(0.3, 0.26, 0.34), size=1) for _ in range(2)]
    S['xl'] = light((0, 0, 0), 0, 'FFE8D0', 4.0, None, 'AREA', parent=None)
    S['xaim'] = empty()
    c = S['xl'].constraints.new('TRACK_TO')
    c.target, c.track_axis, c.up_axis = S['xaim'], 'TRACK_NEGATIVE_Z', 'UP_Y'


_build0, _reset0, _finish0 = build, reset, finish


def build():
    S = _build0()
    extend(S)
    return S


def reset(S):
    _reset0(S)
    for who in XCAST:
        S[who].place(FAR)
        S[who].apply(P())
        S[who].root.scale = (1, 1, 1)
        S['face'][who] = 'calm'
    for o in S['notes'] + S['cups'] + S['toes']:
        o.location, o.rotation_euler = FAR, (0, 0, 0)
    for o in S['toes']:
        o.scale = (0.3, 0.26, 0.34)
    for kk in ('stretch', 'clip', 'medal'):
        S[kk].location, S[kk].rotation_euler, S[kk].scale = FAR, (0, 0, 0), (1, 1, 1)
    S['disc'].rotation_euler = (0, 0, 0)
    S['needle'].rotation_euler = (0, -1.0, 0)
    S['otag'].location = (-2.2, 4.76, 4.36)
    S['ojet'].location = (0, 0, -30)
    S['handset'].location, S['handset'].rotation_euler = (-1.3, 1.02, 1.84), (0, 0, 0)
    S['wday'].hide_render, S['wnight'].hide_render = False, True
    S['olamp'].data.energy, S['okey'].data.energy, S['ofill'].data.energy, S['otop'].data.energy = 160, 800, 280, 420
    S['spot'].data.energy, S['sfill'].data.energy = 9000, 500
    S['xl'].data.energy = 0


def finish(S, t):
    _finish0(S, t)
    for who in XCAST:
        e = S['face'][who]
        x = S[who].extra
        kk = dict(scared=1.3, shock=1.7, calm=1.0, sad=0.6, happy=0.8, closed=0.08, tired=0.5).get(e, 1.0)
        for ey in x['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], x['eye0'] * kk)
        x['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
        x['jaw'].scale = (1.5, 1, 1.6) if e == 'happy' else (1, 1, 1)


def xlight(S, pos, look, e, col='FFE8D0'):
    """A free fill light for close shots."""
    S['xl'].location, S['xaim'].location = pos, look
    S['xl'].data.energy = e
    S['xl'].data.color = K.hexc(col)[:3]


def face_to(frm, to):
    """Yaw that turns a rig standing at `frm` toward `to` (x, y)."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


# ---------------------------------------------------------------- long shots: Belgrade, 1971
def street(S):
    A = show(S, 'street')
    sky(S, 'E8A878', 1.0)
    return A


def belgrade(S, k, t, lt):
    A = street(S)
    x = lerp(-9.5, -4.0, k)
    w = walk(t + 0.2, 1.3)
    if S['prm'].get('alone'):                    # years later: Rook walks the street by himself, hat in hand
        sky(S, '6A5A88', 0.8)
        S['rook'].place(A(lerp(-3.0, -0.5, k), 2.2, 0.16), 1.15)
        S['rook'].apply(P('stand', lL=w['lL'], lR=w['lR'], aR=(0.75, -0.2, 2.0, 1.1), head=(0.25, 0.0), lean=0.08))
        S['hat_off'] = True
        S['face']['rook'] = 'sad'
    else:
        S['civil'].place(A(x, 2.6, 0.16), 1.15)
        S['civil'].apply(walk(t, 1.3))
        S['face']['civil'] = 'happy'
        S['rook'].place(A(x - 4.6, 2.0, 0.16), 1.25)
        S['rook'].apply(blend(w, P('hat', lL=w['lL'], lR=w['lR']), 1 - lt / 0.8))
        S['face']['rook'] = 'deadpan'
    S['disc'].rotation_euler = (0, 0, t * 5)
    if S['prm'].get('alone'):
        cam(S, A(lerp(3.0, 2.0, k), -5.6, 1.9), A(-1.4, 2.4, 2.4), 36)
    else:
        cam(S, A(x + 2.2, -5.4, 1.9), A(x - 2.0, 2.6, 2.35), 38)


def vinyl(S, k, t, lt):
    A = street(S)
    sw = math.sin(t * 6)
    S['civil'].place(A(-0.7, 3.2, 0.16), -0.45, 0, 0.07 * sw)
    S['civil'].apply(P('stand', aL=(0.5, 0.7 + 0.3 * sw, 1.3), aR=(0.5, 0.7 - 0.3 * sw, 1.3), head=(0.0, 0.2 * sw), lL=(0.12 * sw, 0.2 * max(0, sw)), lR=(-0.12 * sw, 0.2 * max(0, -sw))))
    S['face']['civil'] = 'happy'
    S['disc'].rotation_euler = (0, 0, t * 5)
    for i, o in enumerate(S['notes']):
        u = (t * 0.55 + i * 0.17) % 1
        o.location = A(-2.6 + 0.6 * math.sin(i * 2 + t * 2) + u * 0.8, 3.4, 2.0 + u * 3.0)
        o.rotation_euler = (0, 0.3 * math.sin(t * 3 + i), 0)
    tap = 0.25 * max(0.0, math.sin(t * 12))
    S['rook'].place(A(2.3, 2.5, 0.16), -0.35)
    S['rook'].apply(P('cross', head=(0.05, 0.35), lR=(0.2 + tap, 0.3 + tap)))
    S['face']['rook'] = 'deadpan'
    xlight(S, A(1, -4, 3), A(0, 3, 2), 500)
    cam(S, A(lerp(1.2, 0.7, k), lerp(-4.6, -4.0, k), 2.0), A(0.1, 3.2, 2.15), 34)


def friend(S, k, t, lt):
    A = street(S)
    e = ease(k * 1.6)
    fx = lerp(7.0, 2.4, e)
    S['friend'].place(A(fx, 2.7, 0.16), -PI / 2 + 0.35)
    S['friend'].apply(walk(t, 1.3) if e < 1 else P('stand', aR=(0.6, 0.9 + 0.25 * math.sin(t * 9), 2.0, -0.6)))
    S['face']['friend'] = 'happy'
    S['civil'].place(A(0.0, 2.7, 0.16), PI / 2 - 0.35)
    S['civil'].apply(blend(P('stand', head=(0, -0.2)), P('up', aL=(1.6, 0.8, 1.2), aR=(1.6, 0.8, 1.2), head=(-0.1, 0)), (k - 0.45) * 4))
    S['face']['civil'] = 'calm' if k < 0.45 else 'shock'
    tap = 0.25 * max(0.0, math.sin(t * 11))
    S['rook'].place(A(-3.6, 1.9, 0.16), 0.75)
    S['rook'].apply(P('stand', aR=(1.25 + tap * 0.3, -0.15, 2.25, 0.75), head=(0.05, -0.2)))
    S['face']['rook'] = 'smirk'
    xlight(S, A(0, -5, 3), A(1, 2.7, 2), 500)
    cam(S, A(lerp(0.6, 0.9, k), lerp(-7.2, -6.4, k), 2.1), A(0.6, 2.7, 2.2), 36)


# ---------------------------------------------------------------- long shots: the airline medical
def clinic(S):
    A = show(S, 'clinic')
    sky(S, '1A1E24', 1.0)
    return A


def cups_row(S, A, n, x0=-2.3):
    for i in range(n):
        o = S['cups'][1 + i]
        o.location = A(x0 + i * 0.36, 0.25 + 0.1 * (i % 2), 1.66 if i % 3 else 1.62)
        o.rotation_euler = (0, 0 if i % 3 else PI / 2, i)


def coffee(S, k, t, lt):
    A = clinic(S)
    u = 0.5 + 0.5 * math.sin(t * 5.5)
    S['civil'].place(A(-1.3, 1.75, 0), 0.1)
    S['civil'].apply(P('stand', aR=(lerp(1.0, 1.75, u), 0.1, lerp(1.3, 2.3, u)), aL=(0.6, 0.2, 1.0), head=(lerp(0.1, -0.35, u), 0.0)))
    S['face']['civil'] = 'scared'
    hp = hand(S, 'civil')
    S['cups'][0].location = (hp[0], hp[1] - 0.05, hp[2] + 0.12)
    S['cups'][0].rotation_euler = (lerp(0, -0.9, u), 0, 0)
    cups_row(S, A, 2 + int(k * 5.5))
    S['rook'].place(A(1.9, 0.5, 0), -0.75)
    S['rook'].apply(P('stand', aL=(1.3, 0.2, 1.7, 0.3), aR=(1.2, 0.1, 1.9, 0.5), head=(0.1, 0.45)))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = ease((k - 0.5) * 3)
    cam(S, A(lerp(1.1, 0.7, k), lerp(-6.2, -5.6, k), 2.3), A(0.0, 1.1, 2.05), 34)


def medical(S, k, t, lt):
    A = clinic(S)
    e = 0.0 if S['prm'].get('pre') else ease((k - 0.2) / 0.5)
    S['needle'].rotation_euler = (0, lerp(-1.05, 0.25, e) + 0.05 * math.sin(t * 21), 0)
    S['civil'].place(A(2.6, 1.4, 0.36), -0.3)
    S['civil'].apply(P('sit', aR=(1.2, 0.5, 0.4), aL=(0.7, -0.1, 1.5, 1.0), head=(-0.1, -0.5), lean=0.05))
    S['face']['civil'] = 'scared' if e < 0.9 else 'happy'
    S['doctor'].place(A(5.4, 2.4, 0), -0.55)
    S['doctor'].apply(P('stand', aL=(2.2, 0.5, 0.3), aR=(0.8, 0.1, 1.4), head=(-0.15, 0.5)))
    S['clip'].location = hand(S, 'doctor')
    S['clip'].rotation_euler = (-0.5, 0, -0.55)
    cups_row(S, A, 7)
    S['rook'].place(A(-0.4, 2.3, 0), 0.75)
    S['rook'].apply(P('cross', head=(-0.05, -0.3)))
    S['face']['rook'] = 'deadpan' if e < 0.9 else 'shocked'
    cam(S, A(lerp(2.0, 2.5, k), lerp(-6.6, -6.0, k), 2.5), A(2.7, 3.2, 2.75), 32)


def rook_cup(S, k, t, lt):
    A = clinic(S)
    S['rook'].place(A(0.9, 0.3, 0), -0.2)
    look = ease((k - 0.5) * 4)
    S['rook'].apply(P('stand', aR=(1.45, 0.15, 1.5, 0.3), aL=(0.3, 0.2, 0.5), head=(lerp(0.3, 0.0, look), lerp(-0.25, 0.0, look))))
    S['face']['rook'] = 'deadpan' if look < 0.5 else 'smirk'
    hp = hand(S, 'rook')
    S['cups'][0].location = (hp[0], hp[1] - 0.05, hp[2] + 0.16 + 0.03 * math.sin(t * 16))
    S['cups'][0].rotation_euler = (PI + 0.2 * math.sin(t * 16), 0, 0)
    cups_row(S, A, 7)
    xlight(S, A(-1, -4, 3), A(0.9, 0.3, 2.3), 300)
    cam(S, A(lerp(1.5, 1.2, k), lerp(-3.9, -3.3, k), 2.3), A(0.8, 0.3, 2.3), 50)


# ---------------------------------------------------------------- long shots: the office (crew desk, freight desk, newsrooms)
def office(S, mode='day'):
    A = show(S, 'office')
    sky(S, '14161C' if mode == 'day' else '05060A', 1.0)
    if mode == 'night':
        S['wday'].hide_render, S['wnight'].hide_render = True, False
        S['okey'].data.energy, S['ofill'].data.energy, S['otop'].data.energy, S['olamp'].data.energy = 110, 420, 40, 900
    elif mode == 'cool':
        S['okey'].data.energy, S['ofill'].data.energy = 450, 700
    return A


def dispatch(S, k, t, lt):
    A = office(S)
    e = ease((k - 0.35) / 0.3)
    S['otag'].location = (-2.2, 4.76, lerp(4.36, 3.61, e))
    S['clerk'].place(A(0.5, 2.55, 0.85), 0.25)
    S['clerk'].apply(P('sit', aR=(1.3, 0.25, 2.3, 0.6), aL=(0.9, 0.0, 1.0, 0.6), head=(0.1, 0.4), lean=0.1))
    hp = hand(S, 'clerk')
    S['handset'].location = (hp[0] - 2400, hp[1], hp[2] + 0.1)
    S['handset'].rotation_euler = (0, PI / 2 - 0.3, 0)
    S['rook'].place(A(-6.6, 2.4, 0), 0.5)
    S['rook'].apply(blend(P('point', aR=(2.0, -0.5, 0.2), head=(-0.1, -0.5)), P('hat', head=(0.25, 0.0)), (k - 0.7) * 5))
    S['face']['rook'] = 'shocked' if 0.35 < k < 0.7 else 'deadpan'
    S['hat_tip'] = ease((k - 0.72) * 5)
    cam(S, A(lerp(-1.6, -2.2, k), lerp(-7.0, -6.4, k), 2.5), A(-2.4, 3.4, 2.9), 30)


def desk_job(S, k, t, lt):
    A = office(S)
    st = max(0.0, math.sin(t * 7))
    turn = ease((k - 0.45) * 3)
    S['civil'].place(A(0.5, 2.55, 0.85), 0.0)
    S['civil'].apply(P('sit', aR=(0.9 + 0.5 * st * (1 - turn), 0.0, 1.0), aL=(0.8, 0.0, 1.1, 0.5), head=(lerp(0.3, -0.1, turn), lerp(0.0, -0.8, turn)), lean=0.15))
    S['face']['civil'] = 'calm' if turn < 0.5 else 'sad'
    if S['prm'].get('empty'):                    # the desk after she was dismissed
        S['civil'].place(FAR)
    S['ojet'].location = (lerp(2.4, 7.2, k), 4.6, lerp(3.2, 4.9, k))
    S['ojet'].rotation_euler = (0, -0.35, 0)
    S['rook'].place(A(6.2, 3.1, 1.45), -0.6)
    S['rook'].apply(P('sit', aL=(0.9, 0.25, 1.2), aR=(0.7, -0.1, 1.5, 1.0), head=(0.1, 0.55), lean=0.1))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(1.2, 1.8, k), lerp(-7.0, -6.4, k), 2.7), A(2.7, 2.6, 2.6), 30)


def phone_call(S, k, t, lt):
    A = office(S, 'night')
    up = ease((k - 0.5) * 4)
    S['paxb'].place(A(0.5, 2.55, 0.85), 0.3)
    S['paxb'].apply(blend(P('sit', aR=(1.0, 0.4, 0.6), aL=(0.9, 0.0, 1.0, 0.6), head=(0.3, 0.5), lean=0.2),
                          P('sit', aR=(1.3, 0.25, 2.3, 0.6), aL=(0.9, 0.0, 1.0, 0.6), head=(0.0, 0.3), lean=0.05), up))
    S['face']['paxb'] = 'calm' if up < 0.5 else 'scared'
    if up < 0.5:
        j = abs(math.sin(t * 38))
        S['handset'].location = (-1.3 + 0.03 * math.sin(t * 60), 1.02, 1.84 + 0.07 * j)
        S['handset'].rotation_euler = (0, 0.12 * math.sin(t * 38), 0.1 * math.sin(t * 50))
    else:
        hp = hand(S, 'paxb')
        S['handset'].location = (hp[0] - 2400, hp[1], hp[2] + 0.1)
        S['handset'].rotation_euler = (0, PI / 2 - 0.3, 0)
    cam(S, A(lerp(-2.9, -2.3, k), lerp(-3.9, -3.3, k), 2.5), A(-0.5, 1.6, 2.0), 40)


def reporters(S, k, t, lt):
    A = office(S, 'cool')
    ty = 0.25 * math.sin(t * 15)
    S['paxb'].place(A(0.5, 2.55, 0.85), -0.2)
    S['paxb'].apply(P('sit', aL=(1.0, -0.2, 0.9 + ty, 0.5), aR=(1.0, -0.2, 0.9 - ty, 0.5), head=(0.3, -0.3), lean=0.2))
    S['paxa'].place(A(-2.9, 2.3, 0), 0.55)
    S['paxa'].apply(P('stand', aL=(1.0, -0.05, 1.2, 0.5), aR=(1.0, -0.05, 1.2, 0.5), head=(0.35, 0.0)))
    S['paper'].location = A(-2.55, 1.62, 1.75)
    S['paper'].rotation_euler = (-0.6, 0, 0.55 + 0.03 * math.sin(t * 9))
    S['rook'].place(A(3.9, 3.2, 0), -0.5)
    S['rook'].apply(P('cross', head=(0.1, 0.45)))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.6
    cam(S, A(lerp(-0.2, 0.6, k), lerp(-6.8, -6.2, k), 2.6), A(0.4, 2.5, 2.5), 32)


# ---------------------------------------------------------------- long shots: London, 1985
def stage(S):
    A = show(S, 'stage')
    sky(S, '07060C', 1.0)
    return A


def on_stage(S, A, k, t):
    give = ease((k - 0.35) / 0.3)
    S['civil'].place(A(-0.7, 4.6, 0.8), 0.3)
    S['civil'].apply(blend(P('stand', head=(0, 0.3)), P('stand', aR=(1.7, 0.3, 1.2), aL=(0.4, 0.3, 0.6), head=(-0.1, 0.0)), (k - 0.55) * 4))
    S['face']['civil'] = 'happy'
    S['mc'].place(A(1.7, 4.5, 0.8), -0.75)
    cl = 0.25 * math.sin(t * 14)
    S['mc'].apply(blend(P('point', aR=(1.35, 0.25, 0.25), head=(0.0, -0.3)), P('stand', aL=(1.2, -0.1 + cl, 1.1, 0.6), aR=(1.2, -0.1 - cl, 1.1, 0.6)), (k - 0.6) * 4))
    S['face']['mc'] = 'happy'
    a, b = hand(S, 'mc'), hand(S, 'civil')
    S['medal'].location = [a[i] + (b[i] - a[i]) * give for i in range(3)]
    S['medal'].location.z += 0.1
    S['medal'].rotation_euler = (0, 0, 0.5 * math.sin(t * 5))
    S['medal'].scale = (1.5, 1.5, 1.5)


def stage_wide(S, k, t, lt):
    A = stage(S)
    on_stage(S, A, k, t)
    cl = 0.3 * math.sin(t * 13)
    S['rook'].place(A(3.0, -3.5, 0), PI + 0.15)
    S['rook'].apply(P('stand', aL=(1.3, -0.1 + cl, 1.2, 0.6), aR=(1.3, -0.1 - cl, 1.2, 0.6), head=(-0.1, 0.0)))
    cam(S, A(lerp(-1.6, -0.6, k), lerp(-10.5, -9.5, k), 3.3), A(0.6, 5, 3.3), 30)


def medal_cu(S, k, t, lt):
    A = stage(S)
    on_stage(S, A, 0.6 + 0.4 * k, t)
    S['rook'].place(A(-2.9, 6.2, 0.8), 0.45, 0, -0.22)
    S['rook'].apply(P('stand', aL=(0.4, 0.5, 0.8), aR=(1.0, 0.5, 1.2), head=(0.0, -0.35)))
    S['face']['rook'] = 'shocked'
    S['hat_up'] = 0.15 * math.sin(PI * min(1, lt / 0.8))
    cam(S, A(lerp(-1.2, -0.9, k), lerp(-0.4, 0.2, k), 2.9), A(-0.6, 5.0, 3.15), 34)


def rook_clap(S, k, t, lt):
    A = stage(S)
    S['sfill'].data.energy = 1500
    cl = 0.3 * math.sin(t * 13)
    tip = math.sin(PI * ease((lt - 1.0) / 1.0)) if lt > 1.0 else 0
    S['rook'].place(A(3.0, -3.5, 0), PI - 0.1)
    S['rook'].apply(blend(P('stand', aL=(1.3, -0.1 + cl, 1.2, 0.6), aR=(1.3, -0.1 - cl, 1.2, 0.6)), P('hat', head=(0.2, 0)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    xlight(S, A(1.0, 0.5, 3.4), A(3, -3.5, 2.3), 900, 'FFE2B0')
    cam(S, A(lerp(1.6, 2.0, k), lerp(1.6, 1.0, k), 2.5), A(3.0, -3.5, 2.35), 44)


# ---------------------------------------------------------------- long shots: Copenhagen, the hillside, the ward, the flight home
def crew_board(S, k, t, lt):
    A = apron(S, 'dawn')
    sky(S, 'B8C4DC', 1.0)
    x = lerp(9.5, 3.5, k)
    for i, who in enumerate(('paxa', 'friend', 'vesna')):
        S[who].place(A(x + i * 2.3 - 5.5, 1.6 - 0.25 * i, 0), -PI / 2 + 0.35)
        S[who].apply(walk(t + i * 0.3, 1.4))
    S['face']['vesna'] = 'happy'
    w = walk(t + 0.5, 1.4)
    S['rook'].place(A(x + 1.6, 0.7, 0), -PI / 2 + 0.3)
    S['rook'].apply(blend(w, P('hat', lL=w['lL'], lR=w['lR']), 1 - lt / 0.9))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(5.4, 4.2, k), -7.4, 1.6), A(x - 1.6, 2.5, 2.7), 30)


def honke_hears(S, k, t, lt):
    A = hill(S, 'night')
    wreck_rest(S, A)
    x, y = 10.0, -7.0
    turn = ease((k - 0.3) * 3)
    S['bruno'].place(A(x, y, hz(x)), lerp(0.2, -0.5, turn))
    S['bruno'].apply(P('stand', aL=(0.3, 1.5, 2.3, -1.2), aR=(1.1, 0.3, 0.9), head=(-0.1, lerp(0.0, 0.9, turn)), lean=0.08))
    S['face']['bruno'] = 'scared'
    hp = hand(S, 'bruno')
    lantern_at(S, (hp[0], hp[1], hp[2] - 0.4), 900)
    S['pov'].data.energy = 250
    cam(S, A(lerp(11.6, 11.0, k), lerp(-12.6, -11.8, k), hz(11) + 1.5), A(8.6, -4.5, hz(9) + 2.7), 36)


def rook_snow(S, k, t, lt):
    A = hill(S, 'sad')
    wreck_rest(S, A)
    x, y = -4.0, -3.4
    poke = 0.5 + 0.5 * math.sin(t * 4)
    S['rook'].place(A(x, y, hz(x)), 0.5)
    S['rook'].apply(kneel(aR=(lerp(0.9, 1.3, poke), 0.2, 0.5), aL=(0.4, 0.3, 0.9), head=(lerp(0.35, 0.0, ease((k - 0.6) * 4)), -0.3)))
    S['face']['rook'] = 'calm' if k < 0.6 else 'shocked'
    hp = hand(S, 'rook')
    S['cane'].location = (hp[0], hp[1] - 0.1, hp[2] - 0.5 - 0.25 * poke)
    S['cane'].rotation_euler = (0.25, 0.1, 0)
    S['pov'].data.energy = 400
    cam(S, A(lerp(-1.2, -1.8, k), lerp(-9.0, -8.2, k), hz(-2) + 1.3), A(-3.0, -2.0, hz(-3) + 1.7), 34)


def stretcher(S, k, t, lt):
    A = hill(S, 'night')
    wreck_rest(S, A)
    x, y = 15.0, lerp(5.0, 1.0, k)
    z = hz(x)
    bob = 0.04 * math.sin(t * 9)
    S['stretch'].location = A(x, y, z + 1.12 + bob)
    w = walk(t, 1.3)
    S['bruno'].place(A(x, y - 2.5, z), 0.0)
    S['bruno'].apply(P('stand', lL=w['lL'], lR=w['lR'], aL=(-0.35, 0.25, 0.15), aR=(-0.35, 0.25, 0.15), lean=0.1))
    S['paxa'].place(A(x, y + 2.5, z), 0.0)
    S['paxa'].apply(P('stand', lL=w['lR'], lR=w['lL'], aL=(0.45, 0.25, 0.2), aR=(0.45, 0.25, 0.2), lean=0.12, head=(0.2, 0)))
    S['rook'].place(A(x + 2.3, y - 0.4, hz(x + 2.3)), -0.15)
    S['rook'].apply(P('stand', lL=w['lR'], lR=w['lL'], aR=(2.0, 1.0, 0.25), aL=(0.3, 0.3, 0.6), head=(0.15, 0.5)))
    S['face']['rook'] = 'sad'
    hp = hand(S, 'rook')
    lantern_at(S, (hp[0], hp[1], hp[2] - 0.42), 700)
    for i, o in enumerate(S['resc']):
        xx, yy = 6 + i * 3.2, 17 + (i % 2) * 5 + (i % 3) * 2
        o.location = A(xx, yy, hz(xx) + 2.2 + 0.25 * math.sin(t * 7 + i * 2))
    S['pov'].data.energy = 300
    cam(S, A(lerp(19.6, 19.0, k), lerp(-9.5, -8.5, k), hz(19) + 1.6), A(15.4, 1.5, z + 2.1), 42)


def wake(S, k, t, lt):
    A = ward(S)
    op = ease((k - 0.3) * 4)
    S['patient'].place(A(-0.3, 2.6, 1.32), -PI / 2, -PI / 2 + 0.3, 0)
    S['patient'].apply(P('stand', aL=(0.3, 0.3, 0.3), aR=(0.3 + 0.15 * op, 0.3, 0.3 + 0.3 * op), head=(0.25, lerp(0.0, 0.45, op))))
    S['face']['patient'] = 'closed' if op < 0.2 else ('tired' if op < 0.8 else 'calm')
    S['rook'].place(A(2.1, 4.25, 0), 0.25)
    S['rook'].apply(P('stand', aL=(0.5, 0.9, 0.5), aR=(0.5, 0.9, 0.5), head=(0.3, -0.2), lean=0.3))
    S['face']['rook'] = 'calm' if op < 0.5 else 'shocked'
    S['hat_up'] = 0.2 * math.sin(PI * min(1.0, max(0.0, (k - 0.4) * 2.5)))
    xlight(S, A(1, -3, 3.5), A(1.8, 2.8, 2.0), 250)
    cam(S, A(lerp(0.9, 1.3, k), lerp(-2.4, -1.8, k), 2.9), A(1.7, 2.9, 2.25), 44)


def ward_doctor(S, k, t, lt):
    A = ward(S)
    S['patient'].place(A(-0.3, 2.6, 1.32), -PI / 2, -PI / 2 + 0.3, 0)
    S['patient'].apply(P('stand', aL=(0.3, 0.3, 0.3), aR=(0.3, 0.3, 0.3), head=(0.25, 0.0)))
    S['face']['patient'] = 'closed'
    S['doctor'].place(A(-2.5, 0.7, 0), 0.9)
    S['doctor'].apply(P('stand', aR=(1.25, 0.3, 0.3 + 0.2 * math.sin(t * 4)), aL=(0.8, 0.1, 1.4), head=(0.2, -0.3)))
    hp = hand(S, 'doctor', 0)
    S['clip'].location = (hp[0], hp[1] - 0.05, hp[2] + 0.2)
    S['clip'].rotation_euler = (-0.5, 0, 0.9)
    S['rook'].place(A(-1.9, 4.15, 0), 0.35)
    S['rook'].apply(P('stand', aR=(0.75, -0.2, 2.0, 1.1), head=(0.2, 0.0)))
    S['hat_off'] = True
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(4.9, 4.4, k), lerp(-5.4, -4.8, k), 1.9), A(-0.9, 2.0, 2.1), 34)


def legs(S, k, t, lt):
    A = ward(S)
    S['patient'].place(A(-0.3, 2.6, 1.32), -PI / 2, -PI / 2 + 0.3, 0)
    S['patient'].apply(P('stand', aL=(0.3, 0.3, 0.3), aR=(0.3, 0.3, 0.3), head=(0.1, 0.3)))
    S['face']['patient'] = 'happy'
    for i, o in enumerate(S['toes']):
        wg = max(0.0, math.sin(t * 9 + i * 1.6)) * ease(k * 3)
        o.location = A(-1.15, 2.6 + (i - 0.5) * 0.5, 1.5 + 0.08 * wg)
        o.rotation_euler = (0, 0.45 * wg, 0)
    S['rook'].place(A(-3.3, 1.5, 0), 1.25)
    S['rook'].apply(P('stand', aL=(0.5, 1.0, 0.5), aR=(0.5, 1.0, 0.5), head=(0.25, -0.5), lean=0.35))
    S['face']['rook'] = 'shocked'
    S['hat_up'] = 0.22 * math.sin(PI * min(1, lt / 0.9))
    xlight(S, A(-2, -3, 3), A(-1.5, 2.4, 1.8), 200)
    cam(S, A(lerp(-1.0, -1.3, k), lerp(-2.6, -2.0, k), 2.5), A(-1.9, 2.3, 2.0), 40)


def fly_home(S, k, t, lt):
    A = cabin(S)
    sky(S, '9AC0F0', 1.0)
    S['patient'].place(A(1.06, -3.95, 0.36), 0.0)
    S['patient'].apply(P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.7, -0.1, 1.5, 1.0), head=(0.0, lerp(0.0, -0.6, ease((k - 0.5) * 3))), lean=0.1))
    S['face']['patient'] = 'happy'
    j = 0.03 * math.sin(t * 40)
    S['rook'].place(A(1.88, -3.95, 0.36), 0.0)
    S['rook'].apply(P('sit', aL=(0.9, 0.5, 1.4), aR=(0.9, 0.2, 1.4), head=(-0.1, 0.4 * math.sin(t * 5)), lean=0.0 + j))
    S['face']['rook'] = 'shocked'
    for i, f in enumerate(S['fea'][:5]):
        u = (t * 0.6 + i * 0.23) % 1
        f.location = A(1.9 + math.cos(i * 2.3) * (0.4 + 0.5 * u), -4.2 - 0.3 * u, 2.7 + 0.5 * math.sin(i * 1.7) - 1.2 * u)
        f.rotation_euler = (t * 3 + i, t * 2 + i * 2, i)
    cam(S, A(lerp(0.1, 0.4, k), lerp(-7.2, -6.8, k), 2.85), A(1.45, -4.0, 2.2), 44)


HOST |= {'belgrade', 'vinyl', 'friend', 'coffee', 'medical', 'rook_cup', 'dispatch', 'desk_job', 'reporters', 'stage_wide', 'medal_cu',
         'rook_clap', 'crew_board', 'rook_snow', 'stretcher', 'wake', 'ward_doctor', 'legs', 'fly_home'}
SHOTS3D.update({f.__name__: f for f in (
    belgrade, vinyl, friend, coffee, medical, rook_cup, dispatch, desk_job, phone_call, reporters, stage_wide, medal_cu, rook_clap,
    crew_board, honke_hears, rook_snow, stretcher, wake, ward_doctor, legs, fly_home)})


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: the torn fuselage section falling through open sky, Rook falling beside it, hat gone."""
    A = high(S, '3A72C8', clz=-60)
    S['cl'].scale = (1.5, 1.5, 1)
    S['wreck'].location = A(-7.5, 3, 1.5)
    S['wreck'].rotation_euler = (0.5, 0.75, 0.6)
    S['wreck'].scale = (1.25, 1.25, 1.25)
    for i in range(8):
        u = (i + 1) / 8
        o = S['smoke'][i]
        o.location = A(-8.5 - 2.5 * u, 3.5, 5 + u * 14)
        o.scale = (1.0 + 1.6 * u,) * 3
    drift(S['deb'], A(-4, 2, 3), 1.0, 14, (22, 6, 22), (0, 0, 9), spin=3)
    drift(S['streak'], A(0, 4, 0), 1.0, 10, (34, 8, 40), (0, 0, 90))
    for o in S['streak'][:10]:
        o.rotation_euler = (0, 0, 0)
    S['rook'].place(A(0.2, -2.5, -1.2), 0.25, -0.35, 0.3)
    S['rook'].apply(P('up', aL=(2.4, 0.9, 0.5), aR=(2.2, 1.0, 0.6), lL=(0.5, 0.7), lR=(-0.3, 0.4), head=(-0.1, 0.15), lean=-0.15))
    S['face']['rook'] = 'shocked'
    S['hat_up'] = 0.55
    for i, f in enumerate(S['fea']):
        f.location = A(0.2 + math.cos(i * 2.3) * 1.3, -2.6, 1.6 + math.sin(i * 1.7) * 0.9 + 0.3 * i)
        f.rotation_euler = (i, i * 2, i)
    S['pov'].data.energy = 1500
    cam(S, A(3.5, -15, -3.2), A(-0.6, 0, 1.2), 34)


def _no_jet(f):
    """The falling-section shots: only the torn section is in the sky, not the intact aircraft."""
    def g(S, k, t, lt):
        f(S, k, t, lt)
        S['jet'].location = (0, 0, -900)
    g.__name__ = f.__name__
    return g


SHOTS3D.update({f.__name__: _no_jet(f) for f in (tail_fall, fall_top, plunge, debris_sky)})
STILLS['thumb'] = _no_jet(photo_thumb)
