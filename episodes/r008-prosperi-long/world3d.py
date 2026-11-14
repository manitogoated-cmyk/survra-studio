"""Case 008 in 3D - Mauro Prosperi, April 1994. Sets built for this story only: the race course in the Moroccan
dunes with its start arch and marker flags, the open desert where he is lost (a wall of sand, a hero dune, far
mountains), the abandoned shrine with its tower, the inside of that tower with the bats, and a nomad camp with a
tent, palms and goats. The sky is a rig of its own (day, dusk, dawn) that follows whichever set is on screen."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(erg=(0, 0, 0), wild=(2000, 0, 0), shrine=(0, 2000, 0), tower=(2000, 2000, 0), camp=(4000, 0, 0))
FAR = (0, 0, -900)
HOST = {'rook_bat', 'rook_start', 'rook_off', 'run_close', 'rook_jog', 'rook_sand', 'clear_empty', 'rook_wave', 'shrine_wide', 'bats_up',
        'rook_gag', 'lizard', 'goats', 'tent', 'run_again', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'C98F6A'
RUNNER = dict(top='F2EEE4', pants=SKIN, hand=SKIN, boot='E8E4D8', fore=SKIN)
EXTRA = (dict(top='3A8AC8', pants='B07850', hand='B07850', boot='F2EEE4', fore='B07850'),
         dict(top='E8C23A', pants='E0B090', hand='E0B090', boot='2A3550', fore='E0B090'),
         dict(top='B03A4A', pants='8A5A3C', hand='8A5A3C', boot='F2EEE4', fore='8A5A3C'))
GIRL = dict(top='2C3E8C', pants='2C3E8C', hand='8A5A3C', boot='5A3A24')
ELDER = dict(top='1E2A5E', pants='1E2A5E', hand='7A4E34', boot='5A3A24')
SAND = ('E2B06A', 'CF974E', 'EBC07C', 'C48A44')
ease = lambda k: (lambda x: x * x * (3 - 2 * x))(max(0.0, min(1.0, k)))


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


def mixc(a, b, k):
    k = max(0.0, min(1.0, k))
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


def aim(l, d):
    l.rotation_euler = Vector((0, 0, -1)).rotation_difference(Vector(d).normalized()).to_euler()


# ---------------------------------------------------------------- scenery pieces
def dunes(r, n, clear, dmin=26, span=420, seed=0.0, r0=14, rv=30, far=0.05):
    """Low crescent dunes scattered round the set origin. clear(x, y) -> True keeps that spot flat."""
    for i in range(n):
        a = i * 2.399 + seed
        d = dmin + (i * 37 % span)
        x, y = math.cos(a) * d, math.sin(a) * d
        rad = r0 + (i * 7 % rv) + d * far
        if clear(x, y, rad * 1.9):
            continue
        add('ico_sphere', SAND[i % 4], (x, y, -rad * 0.05), rot=(0, 0, 0.5 * math.sin(i * 1.7)), scale=(1.0, 1.7, 0.2 + 0.05 * (i % 3)), radius=rad,
            subdivisions=2, parent=r)


def ripples(r, n, box, seed=0.0):
    for i in range(n):
        x = ((i * 0.618 + seed) % 1 - 0.5) * box[0]
        y = ((i * 0.377 + seed) % 1 - 0.5) * box[1]
        add('ico_sphere', SAND[(i + 1) % 4], (x, y, -0.28), rot=(0, 0, 0.3 * math.sin(i)), scale=(2.6, 0.7, 0.14), radius=2.6, subdivisions=1, parent=r)


def mountains(r, y0=540, cols=('7A5A8A', '8A6A90', '6A4E80', '9A7A96')):
    for i in range(26):
        x = -620 + i * 50 + 18 * math.sin(i * 2.1)
        hgt = 70 + (i * 53 % 90)
        add('cone', cols[i % 4], (x, y0 + (i % 3) * 30, hgt / 2 - 6), radius1=70 + (i * 17 % 40), radius2=4, depth=hgt, vertices=5, parent=r, rot=(0, 0, i * 0.7))


def flag(parent, loc, hgt=2.2, col='FF7A1A'):
    f = empty(loc, parent)
    add('cylinder', 'F4EEDF', (0, 0, hgt / 2), radius=0.04, depth=hgt, vertices=5, parent=f)
    add('cube', col, (0.34, 0, hgt - 0.24), scale=(0.66, 0.03, 0.42), size=1, parent=f)
    return f


def make_sky(low, mid, top, sun_col, sun_at, sun_r=38):
    s = empty(FAR)
    add('cylinder', low, (0, 0, 20), radius=900, depth=90, vertices=28, end_fill_type='NOTHING', parent=s, emit=1.0)
    add('cylinder', mid, (0, 0, 120), radius=905, depth=120, vertices=28, end_fill_type='NOTHING', parent=s, emit=1.0)
    add('cone', top, (0, 0, 330), radius1=910, radius2=40, depth=300, vertices=28, end_fill_type='NOTHING', parent=s, emit=1.0)
    add('ico_sphere', sun_col, sun_at, radius=sun_r, subdivisions=2, parent=s, emit=10)
    for o in s.children:
        o.visible_shadow = o.visible_diffuse = o.visible_glossy = False
    return s


def make_wall(r):
    """The front of the sandstorm: a rolling wall of brown dust about 240 wide and 70 high. Front face toward local -Y."""
    lumps = []
    cols = ('A8703A', '8A5A2E', 'C08A4A', '9A6632', 'B47C40')
    for i in range(70):
        u, v = (i * 0.618) % 1, (i * 0.377) % 1
        x = (u - 0.5) * 240
        z = 4 + v * v * 62
        y = 6 * math.sin(i * 1.3) + z * 0.35
        rad = 11 + (i * 5 % 9) - v * 4
        o = add('ico_sphere', cols[i % 5], (x, y, z), scale=(1.25, 1.0, 0.85), radius=rad, subdivisions=1, parent=r, emit=0.22)
        lumps.append((o, (x, y, z), i))
    add('cube', '8A5A2E', (0, 40, 34), scale=(260, 30, 72), size=1, parent=r, emit=0.18)
    return lumps


def make_bat(parent=None):
    b = empty(FAR, parent)
    add('ico_sphere', '3A2A30', (0, 0, 0), scale=(0.75, 0.7, 1.15), radius=0.2, subdivisions=1, parent=b)
    add('ico_sphere', '4A363C', (0, -0.03, -0.27), radius=0.13, subdivisions=1, parent=b)
    for s in (-1, 1):
        add('cone', '4A363C', (s * 0.08, 0, -0.41), rot=(PI, 0, s * 0.3), radius1=0.05, radius2=0.0, depth=0.16, vertices=4, parent=b)
        add('cube', 'FFB060', (s * 0.05, -0.135, -0.27), scale=(0.035, 0.02, 0.03), size=1, parent=b, emit=4)
    wings = []
    for s in (-1, 1):
        w = empty((s * 0.1, 0, 0.08), b)
        add('cube', '241A20', (s * 0.3, 0, -0.12), rot=(0, s * 0.25, 0), scale=(0.6, 0.03, 0.5), size=1, parent=w)
        add('cone', '241A20', (s * 0.62, 0, -0.34), rot=(PI, 0, 0), radius1=0.12, radius2=0.0, depth=0.3, vertices=3, parent=w)
        wings.append(w)
    return dict(root=b, wings=wings)


def make_goat(col, head_col):
    g = empty(FAR)
    add('cube', col, (0, 0, 0.82), scale=(0.52, 1.15, 0.56), size=1, parent=g)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', head_col, (sx * 0.17, sy * 0.42, 0.28), radius=0.055, depth=0.56, vertices=5, parent=g)
    add('cone', col, (0, 0.62, 1.05), rot=(-0.9, 0, 0), radius1=0.07, radius2=0.0, depth=0.26, vertices=4, parent=g)
    neck = empty((0, -0.52, 1.0), g)
    add('cube', col, (0, -0.1, 0.12), rot=(0.6, 0, 0), scale=(0.24, 0.3, 0.44), size=1, parent=neck)
    add('cube', head_col, (0, -0.32, 0.34), scale=(0.24, 0.44, 0.24), size=1, parent=neck)
    add('cone', head_col, (0, -0.42, 0.14), rot=(PI, 0, 0), radius1=0.05, radius2=0.0, depth=0.2, vertices=4, parent=neck)
    for s in (-1, 1):
        add('cone', 'E8DCC4', (s * 0.08, -0.2, 0.54), rot=(-0.5, s * 0.2, 0), radius1=0.045, radius2=0.0, depth=0.3, vertices=4, parent=neck)
        add('cube', '0E0D14', (s * 0.125, -0.42, 0.38), scale=(0.02, 0.06, 0.05), size=1, parent=neck)
        add('cube', head_col, (s * 0.17, -0.22, 0.36), rot=(0, s * 0.6, 0), scale=(0.16, 0.08, 0.04), size=1, parent=neck)
    return dict(root=g, neck=neck)


def make_heli():
    hl = empty(FAR)
    add('ico_sphere', 'E8E4D8', (0, 0, 0), scale=(1.15, 2.1, 1.2), radius=1.0, subdivisions=1, parent=hl, rough=0.5)
    add('ico_sphere', '26364E', (0, -1.05, 0.2), scale=(0.95, 1.2, 0.85), radius=0.95, subdivisions=1, parent=hl, rough=0.2)
    add('cube', 'C8402A', (0, 0.3, -0.25), scale=(2.36, 2.6, 0.3), size=1, parent=hl)
    add('cube', 'E8E4D8', (0, 3.6, 0.35), scale=(0.3, 4.6, 0.4), size=1, parent=hl)
    add('cube', 'C8402A', (0, 5.7, 0.95), rot=(-0.4, 0, 0), scale=(0.1, 0.9, 1.5), size=1, parent=hl)
    add('cylinder', '3A3F4A', (0, 0, 1.35), radius=0.12, depth=0.5, vertices=6, parent=hl)
    rotor = empty((0, 0, 1.62), hl)
    for a in (0, PI / 2):
        add('cube', '2A2E36', (0, 0, 0), rot=(0, 0, a), scale=(10.5, 0.34, 0.05), size=1, parent=rotor)
    trot = empty((0.24, 5.75, 1.3), hl)
    add('cube', '2A2E36', (0, 0, 0), scale=(0.04, 0.2, 1.7), size=1, parent=trot)
    for s in (-1, 1):
        add('cube', '3A3F4A', (s * 0.95, 0, -1.45), scale=(0.1, 3.4, 0.1), size=1, parent=hl)
        for y in (-0.9, 0.9):
            add('cube', '3A3F4A', (s * 0.85, y, -1.1), rot=(0, s * 0.3, 0), scale=(0.07, 0.07, 0.8), size=1, parent=hl)
    return dict(root=hl, rotor=rotor, trot=trot)


def make_lizard():
    z = empty(FAR)
    add('cube', '7AA050', (0, 0, 0.07), scale=(0.16, 0.5, 0.1), size=1, parent=z)
    head = empty((0, -0.27, 0.08), z)
    add('cube', '8AB45A', (0, -0.1, 0.02), scale=(0.15, 0.22, 0.1), size=1, parent=head)
    for s in (-1, 1):
        add('cube', '0E0D14', (s * 0.07, -0.13, 0.07), scale=(0.03, 0.04, 0.03), size=1, parent=head)
        for y in (-0.16, 0.16):
            add('cube', '6A9044', (s * 0.14, y, 0.03), rot=(0, 0, s * 0.5), scale=(0.2, 0.05, 0.04), size=1, parent=z)
    tail = empty((0, 0.25, 0.07), z)
    add('cone', '6A9044', (0, 0.3, 0), rot=(-PI / 2, 0, 0), radius1=0.07, radius2=0.0, depth=0.6, vertices=4, parent=tail)
    return dict(root=z, head=head, tail=tail)


def make_beetle():
    b = empty(FAR)
    add('ico_sphere', '14121C', (0, 0, 0.09), scale=(0.8, 1.15, 0.6), radius=0.14, subdivisions=1, parent=b, rough=0.25)
    add('ico_sphere', '201C2C', (0, -0.17, 0.07), radius=0.07, subdivisions=1, parent=b, rough=0.3)
    legs = []
    for s in (-1, 1):
        for j in range(3):
            l = empty((s * 0.1, -0.1 + j * 0.1, 0.06), b)
            add('cube', '14121C', (s * 0.09, 0, -0.02), rot=(0, s * 0.5, 0), scale=(0.2, 0.025, 0.025), size=1, parent=l)
            legs.append(l)
    return dict(root=b, legs=legs)


def make_flask():
    f = empty(FAR)
    add('cylinder', 'C8CCD8', (0, 0, 0), radius=0.13, depth=0.44, vertices=10, parent=f, rough=0.18)
    add('cone', 'C8CCD8', (0, 0, 0.28), radius1=0.13, radius2=0.06, depth=0.12, vertices=10, parent=f, rough=0.18)
    add('cylinder', 'FF7A1A', (0, 0, 0.38), radius=0.07, depth=0.1, vertices=8, parent=f, rough=0.4)
    add('cylinder', 'FF7A1A', (0, 0, -0.05), radius=0.135, depth=0.07, vertices=10, parent=f, rough=0.4)
    return f


def palm(r, x, y, hgt=7.0, tilt=0.12):
    p = empty((x, y, 0), r, (tilt, tilt * 0.6, 0))
    add('cylinder', '7A5A3A', (0, 0, hgt / 2), radius=0.26, depth=hgt, vertices=6, parent=p)
    for i in range(7):
        a = i * 2 * PI / 7
        fr = empty((0, 0, hgt), p, (0, 0, a))
        add('cube', ('3E7A3A', '4E8A40')[i % 2], (1.5, 0, 0.1), rot=(0, 0.5, 0), scale=(3.2, 0.7, 0.06), size=1, parent=fr)
        add('cube', ('3E7A3A', '4E8A40')[i % 2], (3.1, 0, -1.0), rot=(0, 1.1, 0), scale=(1.6, 0.5, 0.06), size=1, parent=fr)


# ---------------------------------------------------------------- heads
def runner_head(head):
    out = K.human_head(SKIN, '2A2018')(head)
    cap = [add('cylinder', 'F4F0E6', (0, 0.03, 0.22), radius=0.315, depth=0.2, vertices=8, parent=head),
           add('cube', 'F4F0E6', (0, -0.36, 0.15), rot=(0.12, 0, 0), scale=(0.44, 0.3, 0.04), size=1, parent=head),
           add('cube', 'F4F0E6', (0, 0.3, -0.06), rot=(-0.12, 0, 0), scale=(0.56, 0.05, 0.42), size=1, parent=head),
           add('cylinder', 'FF7A1A', (0, 0.03, 0.14), radius=0.32, depth=0.05, vertices=8, parent=head)]
    beard = [add('cube', '3A2A20', (0, -0.235, -0.15), scale=(0.36, 0.12, 0.17), size=1, parent=head),
             add('cube', '3A2A20', (0, -0.1, -0.2), scale=(0.5, 0.3, 0.1), size=1, parent=head)]
    out.update(cap=cap, beard=beard)
    return out


def veiled(skin, cloth):
    def fn(head):
        out = K.human_head(skin, cloth)(head)
        add('ico_sphere', cloth, (0, 0.08, 0.02), scale=(1.08, 1.0, 1.2), radius=0.33, subdivisions=1, parent=head)
        add('cube', cloth, (0, -0.2, 0.27), rot=(0.25, 0, 0), scale=(0.58, 0.2, 0.1), size=1, parent=head)
        add('cone', cloth, (0, 0.06, -0.34), radius1=0.52, radius2=0.26, depth=0.4, vertices=8, parent=head)
        return out
    return fn


# ---------------------------------------------------------------- sets
def set_erg(r):
    """The race course: a flat track between dunes, marker flags, the start arch (plain orange, no lettering)."""
    add('plane', 'D8A45A', (0, 0, 0), size=1900, parent=r)
    dunes(r, 120, lambda x, y, m: abs(x) < 16 + m and -90 - m < y < 90 + m, span=520)
    dunes(r, 60, lambda x, y, m: abs(x) < 12 + m and -90 - m < y < 90 + m, dmin=20, span=110, seed=0.7, r0=4, rv=6, far=0.0)
    ripples(r, 26, (60, 120))
    add('cube', 'CC9A52', (0, 0, 0.01), scale=(9, 400, 0.02), size=1, parent=r)
    for i in range(-6, 7):
        for s in (-1, 1):
            flag(r, (s * 6.2, i * 13 + 4, 0))
    for s in (-1, 1):
        add('cylinder', 'F4EEDF', (s * 5.2, 9, 3.3), radius=0.2, depth=6.6, vertices=6, parent=r)
        add('cube', '2A3550', (s * 5.2, 9, 0.2), scale=(0.9, 0.9, 0.4), size=1, parent=r)
        flag(r, (s * 8.5, 9, 0), 5.0, 'F4EEDF')
    add('cube', 'FF7A1A', (0, 9, 6.3), scale=(11.2, 0.3, 1.5), size=1, parent=r)
    for i in range(-4, 5):
        add('cube', 'F4EEDF', (i * 1.2, 8.83, 6.3), rot=(0, 0.5, 0), scale=(0.3, 0.06, 1.5), size=1, parent=r)
    for i in range(5):
        add('cube', ('F4EEDF', 'C8402A', '3A8AC8')[i % 3], (-22 - (i % 2) * 5, 26 + i * 7, 1.4), rot=(0, 0, 0.4 * i), scale=(4.5, 4.5, 2.8), size=1, parent=r)
        add('cone', ('F4EEDF', 'C8402A', '3A8AC8')[i % 3], (-22 - (i % 2) * 5, 26 + i * 7, 3.7), rot=(0, 0, 0.4 * i + PI / 4), radius1=3.6, radius2=0.2, depth=1.8,
            vertices=4, parent=r)
    return {}


HY = 60


def hero(A):
    """Coordinates on the hero dune: the same as the set's, moved HY north, so (0, 16) is its top."""
    return lambda x, y, z: A(x, y + HY, z)


def hero_z(x, y):
    """Height of the hero dune (in hero() coordinates: centre (0, 16), top about 4.2)."""
    q = 1 - (x / 22.0) ** 2 - ((y - 16) / 26.0) ** 2
    return -0.3 + 4.5 * math.sqrt(q) if q > 0 else 0.0


def set_wild(r):
    """Open desert: where the storm hits and where he is lost. A hero dune north of the origin, mountains far beyond."""
    add('plane', 'D6A058', (0, 0, 0), size=1900, parent=r)
    cl = lambda x, y, m: (x * x + y * y) < (16 + m) ** 2 or (abs(x) < 24 + m and -10 - m < y < 104 + m)
    dunes(r, 130, cl, dmin=40, span=560, seed=1.3)
    dunes(r, 70, cl, dmin=24, span=120, seed=0.4, r0=4, rv=7, far=0.0)
    add('ico_sphere', 'E2B06A', (0, 16 + HY, -0.3), scale=(22, 26, 4.5), radius=1, subdivisions=3, parent=r)
    ripples(r, 34, (70, 30), 0.21)
    for i in range(7):
        add('ico_sphere', ('8A6A54', '7A5C4A')[i % 2], (-9 + i * 3.1 + math.sin(i * 2.2), -3.5 + 2.2 * math.cos(i * 1.7), 0.1), scale=(1, 1.3, 0.6),
            radius=0.3 + 0.12 * (i % 3), subdivisions=1, parent=r)
    mountains(r)
    return {}


def set_shrine(r):
    """The abandoned shrine: a whitewashed cube with a dome, a square tower beside it, a broken wall, a dead tree."""
    add('plane', 'D2A058', (0, 0, 0), size=1900, parent=r)
    cl = lambda x, y, m: (x * x + (y - 2) ** 2) < (28 + m) ** 2
    dunes(r, 120, cl, dmin=36, span=520, seed=2.6)
    dunes(r, 60, cl, dmin=30, span=110, seed=0.9, r0=4, rv=7, far=0.0)
    ripples(r, 24, (60, 40), 0.47)
    b = empty((0, 12, 0), r)
    add('cube', 'E8DCC4', (0, 0, 2.3), scale=(7.4, 7.0, 4.6), size=1, parent=b)
    add('cube', 'D8C8A8', (0, 0, 4.7), scale=(7.9, 7.5, 0.3), size=1, parent=b)
    add('ico_sphere', 'F0E6D0', (0, 0, 4.7), scale=(1, 1, 0.82), radius=2.9, subdivisions=2, parent=b)
    add('cone', 'C89A3A', (0, 0, 7.4), radius1=0.16, radius2=0.0, depth=0.9, vertices=5, parent=b, rough=0.4)
    add('cube', '1A1410', (0, -3.52, 1.4), scale=(1.5, 0.1, 2.8), size=1, parent=b)
    add('cylinder', '1A1410', (0, -3.52, 2.8), rot=(PI / 2, 0, 0), radius=0.75, depth=0.1, vertices=10, parent=b)
    for s in (-1, 1):
        add('cube', '1A1410', (s * 2.4, -3.52, 3.0), scale=(0.5, 0.1, 0.9), size=1, parent=b)
    add('cube', 'E0D2B6', (-5.4, 0.8, 4.6), scale=(2.8, 2.8, 9.2), size=1, parent=b)
    add('cone', 'D8C8A8', (-5.4, 0.8, 9.9), rot=(0, 0, PI / 4), radius1=2.3, radius2=0.2, depth=1.6, vertices=4, parent=b)
    for z in (3.4, 5.6, 7.6):
        add('cube', '1A1410', (-5.4, -0.62, z), scale=(0.5, 0.1, 1.0), size=1, parent=b)
    for i in range(5):
        add('cube', 'D8C8A8', (5.2 + i * 1.5, -3.0 - 0.3 * i, 0.5 - 0.07 * i), rot=(0, 0, -0.2), scale=(1.5, 0.5, 1.1 - 0.15 * i), size=1, parent=b)
    t = empty((8.5, 3, 0), r, (0.1, 0.15, 0))
    add('cylinder', '4A3A2E', (0, 0, 1.6), radius=0.2, depth=3.2, vertices=5, parent=t)
    for i in range(4):
        add('cylinder', '4A3A2E', (0.5 * math.cos(i * 1.7), 0.5 * math.sin(i * 1.7), 3.4), rot=(0.7 * math.sin(i * 1.7), 0.7 * math.cos(i * 1.7), 0), radius=0.07,
            depth=1.8, vertices=4, parent=t)
    mountains(r, 560, ('6A4E80', '7A5A8A', '5A4274', '8A6A90'))
    return {}


def set_tower(r):
    """Inside the tower: three mud walls (the fourth is the camera's), roof beams, a slit window, a doorway full of light."""
    add('plane', '6A5238', (0, 0, 0), size=40, parent=r)
    for x, y, sx, sy in ((0, 3.6, 7.6, 0.4), (-3.6, 0, 0.4, 7.6), (3.6, 0, 0.4, 7.6)):
        add('cube', '8A7458', (x, y, 5.5), scale=(sx, sy, 11), size=1, parent=r)
    add('cube', '2A2018', (0, 0, 11.2), scale=(8, 8, 0.4), size=1, parent=r)
    for i in range(14):
        add('cube', ('7A664C', '9A8466')[i % 2], (-3.2 + (i * 0.618 % 1) * 6.4, 3.38, 0.6 + (i * 0.377 % 1) * 9), scale=(1.1 + 0.4 * (i % 3), 0.08, 0.5), size=1, parent=r)
    for y, z in ((0.9, 6.6), (-0.5, 6.9), (2.2, 7.3)):
        add('cylinder', '4A3626', (0, y, z), rot=(0, PI / 2, 0), radius=0.14, depth=7.4, vertices=6, parent=r)
    add('cube', 'FFE2A8', (-3.38, 0.6, 5.0), scale=(0.06, 0.5, 1.5), size=1, parent=r, emit=14)
    add('cube', 'FFD9A0', (3.38, -1.4, 1.5), scale=(0.06, 1.5, 3.0), size=1, parent=r, emit=5)
    add('cylinder', 'FFD9A0', (3.38, -1.4, 3.0), rot=(0, PI / 2, 0), radius=0.75, depth=0.06, vertices=10, parent=r, emit=5)
    for i in range(6):
        add('ico_sphere', '5A4630', (-2.6 + i * 0.9 + 0.3 * math.sin(i * 2), 2.6 + 0.4 * math.cos(i), 0.12), scale=(1, 1, 0.5), radius=0.3 + 0.1 * (i % 3),
            subdivisions=1, parent=r)
    add('cube', '4A3A2A', (-2.2, 2.3, 0.35), rot=(0, 0, 0.2), scale=(1.6, 1.0, 0.7), size=1, parent=r)
    a1, a2 = empty((0.5, 0.5, 1.0), r), empty((0, 0.8, 5.5), r)
    beam = light((-3.2, 0.6, 5.0), 5200, 'FFE0A8', kind='SPOT', spot=0.9, target=a1, parent=r)
    door = light((3.0, -1.4, 1.8), 520, 'FFC890', 2.5, a1, parent=r)
    cold = light((-1.5, -5.5, 5.5), 420, '7A8AE0', 5.0, a2, parent=r)
    orange = light((2.6, -4.5, 2.2), 380, 'FF7A1A', 3.0, a1, parent=r)
    for l in (beam, door, cold, orange):
        c = l.constraints[0]
        c.track_axis, c.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
    return {}


def set_camp(r):
    """The nomad camp on a gravel plain: a low tent open to the south, rugs, palms by a waterhole, mountains beyond."""
    add('plane', 'C8A470', (0, 0, 0), size=1900, parent=r)
    dunes(r, 100, lambda x, y, m: (x * x + y * y) < (62 + m) ** 2, dmin=70, span=520, seed=4.1)
    for i in range(40):
        a, d = i * 2.399, 4 + (i * 13 % 34)
        add('ico_sphere', ('9A7E5A', '8A6E4E', 'B0946A')[i % 3], (math.cos(a) * d, math.sin(a) * d - 4, 0.05), scale=(1, 1.2, 0.5), radius=0.18 + 0.1 * (i % 3),
            subdivisions=1, parent=r)
    tn = empty((0, 9, 0), r)
    add('cone', '6A2A2A', (0, 0, 3.0), rot=(0, 0, PI / 4), scale=(1.5, 1.0, 1.0), radius1=5.2, radius2=0.5, depth=1.7, vertices=4, parent=tn)
    add('cone', '8A3A30', (0, 0, 3.02), rot=(0, 0, PI / 4), scale=(1.5, 1.0, 1.0), radius1=3.4, radius2=0.5, depth=1.72, vertices=4, parent=tn)
    add('cube', '5A2424', (0, 3.4, 1.1), scale=(10.6, 0.15, 2.3), size=1, parent=tn)
    for s in (-1, 1):
        add('cube', '5A2424', (s * 5.3, 1.3, 1.1), scale=(0.15, 4.2, 2.3), size=1, parent=tn)
        for y in (-3.5, 3.4):
            add('cylinder', '7A5A3A', (s * 5.3, y, 1.2), radius=0.09, depth=2.4, vertices=5, parent=tn)
        add('cylinder', '7A5A3A', (s * 1.8, -3.6, 1.25), radius=0.09, depth=2.5, vertices=5, parent=tn)
    for i, (x, y, c) in enumerate(((-2.4, -1.2, 'A8402A'), (0.6, -0.6, '2C3E8C'), (2.9, -1.6, 'D8A83A'), (-0.6, 1.6, '7A2A3A'))):
        add('cube', c, (x, y, 0.04), rot=(0, 0, 0.15 * (i - 1.5)), scale=(2.8, 2.2, 0.06), size=1, parent=tn)
        add('cube', 'F4EEDF', (x, y, 0.06), rot=(0, 0, 0.15 * (i - 1.5)), scale=(2.2, 0.16, 0.06), size=1, parent=tn)
    for x, y, c in ((-3.6, 1.8, 'D8A83A'), (3.8, 2.0, 'A8402A'), (2.6, 2.6, '2C3E8C')):
        add('ico_sphere', c, (x, y, 0.3), scale=(1, 0.8, 0.45), radius=0.6, subdivisions=1, parent=tn)
    add('cylinder', '3A8AA8', (16, 22, 0.03), radius=5.5, depth=0.06, vertices=12, parent=r, rough=0.15)
    for x, y, hh, tl in ((12, 18, 8, 0.12), (19, 25, 9.5, -0.1), (22, 19, 7, 0.16), (-13, 20, 8.5, -0.14), (10, 27, 6.5, 0.05)):
        palm(r, x, y, hh, tl)
    add('cylinder', '4A3A2E', (-6.8, 3.4, 0.5), radius=0.5, depth=1.0, vertices=8, parent=r)
    mountains(r, 520, ('8A6A7A', '9A7A86', '7A5A70', 'A88A92'))
    return {}


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('erg', set_erg), ('wild', set_wild), ('shrine', set_shrine), ('tower', set_tower), ('camp', set_camp)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['skies'] = dict(day=make_sky('F2DCB0', 'A6D0EC', '5A9FE0', 'FFF6D8', (-300, 620, 420), 30),
                      dusk=make_sky('F28A3C', 'C8507A', '3E3078', 'FFB060', (-560, 640, 46), 46),
                      dawn=make_sky('F8C090', 'E896A8', '6478C4', 'FFE0B0', (520, 660, 40), 44))
    S['sun'] = light((0, 0, 50), 4.0, 'FFF2D8', kind='SUN')
    S['fill'] = light((0, 0, 50), 1.0, '9AC0FF', kind='SUN')
    S['laim'] = empty()
    S['rim'] = light(FAR, 0.0, 'FF7A1A', 3.0, S['laim'])
    S['key'] = light(FAR, 0.0, 'FFF0DC', 4.0, S['laim'])
    for l in (S['rim'], S['key']):
        c = l.constraints[0]
        c.track_axis, c.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['man'] = m = K.Rig(RUNNER, runner_head)
    add('cylinder', '2A3550', (0, 0, -0.04), radius=0.33, depth=0.3, vertices=8, parent=m.body)
    for hp in m.hp:
        add('cylinder', '2A3550', (0, 0, -0.16), radius=0.115, depth=0.34, vertices=6, parent=hp)
    for kn in m.kn:
        add('cylinder', 'F2EEE4', (0, 0, -0.34), radius=0.092, depth=0.2, vertices=6, parent=kn)
    S['pack'] = [add('cube', 'C8402A', (0, 0.3, 0.62), scale=(0.56, 0.3, 0.78), size=1, parent=m.body),
                 add('cube', 'A83222', (0, 0.47, 0.5), scale=(0.4, 0.08, 0.4), size=1, parent=m.body),
                 add('cylinder', 'C8CCD8', (0.34, 0.3, 0.5), radius=0.08, depth=0.42, vertices=6, parent=m.body, rough=0.25)]
    for s in (-1, 1):
        S['pack'].append(add('cube', 'A83222', (s * 0.2, -0.06, 0.72), rot=(0, s * 0.1, 0), scale=(0.09, 0.72, 0.7), size=1, parent=m.body))
    add('cube', 'FF7A1A', (0, -0.345, 0.5), scale=(0.4, 0.03, 0.3), size=1, parent=m.body)
    S['extras'] = []
    for i, c in enumerate(EXTRA):
        e = K.Rig(c, K.human_head(c['hand'], ('17131A', '6A4A2A', '17131A')[i]))
        add('cylinder', ('2A3550', '2A2420', '2A3550')[i], (0, 0, -0.04), radius=0.33, depth=0.3, vertices=8, parent=e.body)
        add('cube', ('E8C23A', 'C8402A', '3A8AC8')[i], (0, 0.3, 0.62), scale=(0.52, 0.28, 0.7), size=1, parent=e.body)
        add('cylinder', 'F4F0E6', (0, 0.03, 0.22), radius=0.315, depth=0.2, vertices=8, parent=e.head)
        add('cube', 'F4F0E6', (0, -0.36, 0.15), rot=(0.12, 0, 0), scale=(0.44, 0.3, 0.04), size=1, parent=e.head)
        S['extras'].append(e)
    S['girl'] = g = K.Rig(GIRL, veiled('8A5A3C', '3E56B0'))
    add('cone', '2C3E8C', (0, 0, -0.38), radius1=0.5, radius2=0.33, depth=1.1, vertices=8, parent=g.body)
    add('cube', 'E8C23A', (0, -0.31, 0.72), scale=(0.3, 0.03, 0.08), size=1, parent=g.body)
    S['staff'] = add('cylinder', '7A5A3A', (0, -0.1, -0.5), rot=(0.25, 0, 0), radius=0.035, depth=3.6, vertices=5, parent=g.el[1])
    S['elder'] = e = K.Rig(ELDER, veiled('7A4E34', '14204A'))
    add('cone', '1E2A5E', (0, 0, -0.38), radius1=0.56, radius2=0.33, depth=1.1, vertices=8, parent=e.body)
    add('cube', 'C8CCD8', (0, -0.31, 0.75), scale=(0.34, 0.03, 0.1), size=1, parent=e.body, rough=0.3)
    S['wall'] = empty(FAR)
    S['lumps'] = make_wall(S['wall'])
    S['sand'] = [add('ico_sphere', ('E8C080', 'D8A860', 'F0D098')[i % 3], FAR, scale=(6, 0.3, 0.3), radius=0.09, subdivisions=1, emit=0.12) for i in range(90)]
    S['dust'] = [add('ico_sphere', ('D8B078', 'C89C60')[i % 2], FAR, radius=0.5, subdivisions=1, emit=0.15) for i in range(14)]
    S['prints'] = [add('cylinder', '9A6E38', FAR, scale=(1, 1.9, 1), radius=0.13, depth=0.02, vertices=8) for _ in range(18)]
    S['fea'] = [add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4) for _ in range(9)]
    S['bats'] = [make_bat() for _ in range(9)]
    S['goats'] = [make_goat(c, hc) for c, hc in (('F0E8D8', 'D8CCB4'), ('5A4636', '3A2C22'), ('E8DCC4', '5A4636'), ('2A2420', '2A2420'), ('C8B490', 'F0E8D8'),
                                                 ('F0E8D8', '2A2420'))]
    S['heli'] = make_heli()
    S['lizard'], S['beetle'] = make_lizard(), make_beetle()
    S['flask'] = make_flask()
    S['mflag'] = flag(None, FAR)
    S['rock'] = empty(FAR)
    add('ico_sphere', '8A6A54', (0, 0, 0.25), scale=(1.5, 1.1, 0.65), radius=0.8, subdivisions=1, parent=S['rock'])
    add('ico_sphere', '7A5C4A', (0.9, 0.5, 0.1), scale=(1, 1, 0.6), radius=0.5, subdivisions=1, parent=S['rock'])
    S['hand'] = K.Hand(SKIN, SKIN, 1.0)
    S['flare'] = empty(FAR)
    add('ico_sphere', 'FF5030', (0, 0, 0), radius=0.22, subdivisions=1, parent=S['flare'], emit=40)
    S['flarel'] = light((0, 0, 0), 0.0, 'FF4028', kind='POINT', parent=S['flare'])
    S['gun'] = add('cube', 'FF7A1A', (0, -0.08, -0.56), scale=(0.08, 0.3, 0.1), size=1, parent=S['man'].el[1])
    S['bowl'] = empty(FAR)
    add('cone', 'E8DCC4', (0, 0, 0), rot=(PI, 0, 0), radius1=0.26, radius2=0.12, depth=0.18, vertices=8, parent=S['bowl'])
    add('cylinder', 'FFFFFF', (0, 0, 0.07), radius=0.22, depth=0.03, vertices=8, parent=S['bowl'], emit=0.4)
    S['glass'] = add('cylinder', 'FFB060', FAR, radius=0.07, depth=0.16, vertices=6, emit=1.2)
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 2600
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


def cam(S, pos, look, lens=50, roll=0.0):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


TOD = dict(   # sky rig, ambient (colour, strength), sun (energy, colour, direction), fill (energy, colour, direction)
    day=('day', ('C8C4C0', 0.75), (4.4, 'FFF2D8', (-0.35, 0.55, -0.75)), (0.9, 'B0C8FF', (0.6, 0.4, -0.5))),
    dusk=('dusk', ('8A5A80', 0.55), (3.6, 'FF9A50', (0.75, 0.55, -0.3)), (1.0, '7A6AE0', (-0.5, 0.6, -0.6))),
    dawn=('dawn', ('B098B8', 0.6), (3.4, 'FFB890', (-0.75, 0.5, -0.3)), (1.0, '8AA0F0', (0.5, 0.6, -0.6))),
    back=('dawn', ('B098B8', 0.6), (3.6, 'FFC090', (-0.5, -0.8, -0.22)), (1.4, '8AA0F0', (0.3, 0.8, -0.4))),
    storm=(None, ('A87840', 1.0), (1.5, 'FFB060', (-0.3, 0.5, -0.8)), (1.3, 'D09A58', (0.5, 0.5, -0.4))),
    tower=(None, ('07060C', 1.0), (0.0, 'FFFFFF', (0, 0, -1)), (0.0, 'FFFFFF', (0, 0, -1))))


def stage(S, name, tod='day', dim=0.0):
    """Show one set, put the sky rig round it and set the sun for the time of day. dim 0..1 fades day toward storm."""
    for n, c in S['colls'].items():
        c.hide_render = n != name
    rig_, bg, sun, fill = TOD[tod]
    if dim > 0:
        st = TOD['storm']
        bg = (mixc(bg[0], st[1][0], dim), lerp(bg[1], st[1][1], dim))
        sun = (lerp(sun[0], st[2][0], dim), mixc(sun[1], st[2][1], dim), sun[2])
    if rig_:
        S['skies'][rig_].location = ORG[name]
    sky(S, *bg)
    for l, (e, c, d) in ((S['sun'], sun), (S['fill'], fill)):
        l.data.energy, l.data.color = e, K.hexc(c)[:3]
        aim(l, d)
    return lambda x, y, z: at(name, x, y, z)


def lamp(S, A, look, rim=(4, 3, 4), key=None, re=900, ke=500):
    """Survra orange rim light (and an optional soft key) near the cast; positions are set-local."""
    S['laim'].location = A(*look)
    S['rim'].location, S['rim'].data.energy = A(*rim), re
    if key:
        S['key'].location, S['key'].data.energy = A(*key), ke


def reset(S):
    for who in ('rook', 'man', 'girl', 'elder'):
        S[who].root.parent = None
        S[who].place(FAR)
        S[who].apply(P())
    S['rook'].root.scale, S['man'].root.scale = (1, 1, 1), (1, 1, 1)
    S['girl'].root.scale, S['elder'].root.scale = (0.62, 0.62, 0.62), (0.92, 0.92, 0.92)
    for e in S['extras']:
        e.place(FAR)
        e.apply(P())
    loose = S['sand'] + S['dust'] + S['prints'] + S['fea'] + [b['root'] for b in S['bats']] + [g['root'] for g in S['goats']]
    loose += [S['wall'], S['heli']['root'], S['lizard']['root'], S['beetle']['root'], S['flask'], S['mflag'], S['rock'], S['hand'].root, S['flare'],
              S['bowl'], S['glass'], S['rim'], S['key']]
    loose += list(S['skies'].values())
    for o in loose:
        o.location = FAR
        o.rotation_euler = (0, 0, 0)
    for o in S['dust'] + S['fea'] + [S['flask'], S['mflag'], S['rock'], S['bowl'], S['glass'], S['wall'], S['heli']['root'], S['lizard']['root'], S['beetle']['root']]:
        o.scale = (1, 1, 1)
    for o in S['sand']:
        o.scale = (6, 0.3, 0.3)
    for o in S['prints']:
        o.scale = (1, 1.9, 1)
    for b in S['bats']:
        b['root'].scale = (1, 1, 1)
        for i, w in enumerate(b['wings']):
            w.rotation_euler = (0, (-1, 1)[i] * 1.25, 0)
    for g in S['goats']:
        g['neck'].rotation_euler = (0, 0, 0)
    for o, (x, y, z), i in S['lumps']:
        o.location = (x, y, z)
    S['hand'].grip(0.2)
    S['rim'].data.energy, S['key'].data.energy, S['flarel'].data.energy = 0, 0, 0
    S['face'] = dict(rook='calm', man='calm', girl='calm', elder='calm')
    S['hat_tip'], S['hat_off'] = 0.0, False
    S['gaunt'], S['pack_on'], S['gun_on'] = False, True, False
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.41) % 1 < 0.035
    ez = dict(calm=0.07, smirk=0.045, deadpan=0.05, shocked=0.13, laugh=0.03, sad=0.06, warm=0.06, sick=0.02).get(e, 0.07)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        tilt = dict(smirk=-0.5, deadpan=-0.05, shocked=0.35, laugh=0.3, sad=0.4, warm=0.2, sick=0.45).get(e, -0.25)
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
    for who in ('man', 'girl', 'elder'):
        k = dict(scared=1.3, shock=1.8, calm=1.0, tired=0.45, happy=0.9, closed=0.1).get(S['face'][who], 1.0)
        for ey in S[who].extra['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], 0.075 * k)
    x = S['man'].extra
    for o in x['cap']:
        o.hide_render = S['gaunt']
    for o in x['beard']:
        o.hide_render = not S['gaunt']
    for o in S['pack']:
        o.hide_render = not S['pack_on']
    S['gun'].hide_render = not S['gun_on']


# ---------------------------------------------------------------- helpers
def run(t, speed=2.6, lean=0.28, amp=1.0):
    s, c = math.sin(t * speed * 2 * PI), math.cos(t * speed * 2 * PI)
    return P('stand', lL=(0.95 * s * amp, max(0, -c) * 1.5 * amp), lR=(-0.95 * s * amp, max(0, c) * 1.5 * amp), aL=(-0.9 * s * amp, 0.15, 1.5),
             aR=(0.9 * s * amp, 0.15, 1.5), lift=0.1 * abs(c) * amp - 0.05, lean=lean, head=(-0.12, 0.0))


def trudge(t, speed=0.9, lean=0.32):
    s, c = math.sin(t * speed * 2 * PI), math.cos(t * speed * 2 * PI)
    return P('stand', lL=(0.4 * s, max(0, -c) * 0.6), lR=(-0.4 * s, max(0, c) * 0.6), aL=(-0.25 * s, 0.1, 0.25), aR=(0.25 * s, 0.1, 0.25),
             lift=-0.06 - 0.03 * abs(s), lean=lean, head=(0.3, 0.06 * s))


def sandblast(S, org, t, n=70, box=(26, 12, 8), speed=60, rise=0.12, size=1.0):
    """Streaks of sand tearing across the frame from +X to -X."""
    for i in range(n):
        b = S['sand'][i]
        u = ((i * 0.618) % 1 + t * speed / box[0] * (0.7 + 0.6 * ((i * 0.29) % 1))) % 1
        b.location = (org[0] + (0.5 - u) * box[0], org[1] + ((i * 0.73) % 1 - 0.5) * box[1],
                      org[2] + ((i * 0.37) % 1) * box[2] + rise * u * box[0] * math.sin(i))
        b.rotation_euler = (0, 0.1 * math.sin(i * 2.0), 0)
        s = size * (0.6 + ((i * 0.41) % 1))
        b.scale = (6 * s, 0.3 * s, 0.3 * s)


def puffs(S, org, t, n=8, spread=1.6, grow=1.0, back=(0, 1, 0)):
    for i in range(n):
        u = (t * 1.4 + i / n) % 1
        d = S['dust'][i]
        d.location = (org[0] + back[0] * u * 4 + math.sin(i * 2.4) * spread * u, org[1] + back[1] * u * 4 + math.cos(i * 1.9) * 0.5, org[2] + 0.2 + 0.9 * u)
        s = (0.35 + 1.3 * u) * grow
        d.scale = (s, s, s * 0.7)


def wall(S, loc, t, sx=1.0):
    S['wall'].location = loc
    S['wall'].scale = (sx, 1, 1)
    for o, (x, y, z), i in S['lumps']:
        o.location = (x, y + 2.5 * math.sin(t * 1.6 + i), z + 2.0 * math.sin(t * 2.1 + i * 1.7))


def feathers(S, org, t, n=6, wind=0.0):
    for i in range(n):
        f = S['fea'][i]
        u = (t * 0.7 + i * 0.37) % 1
        a = i * 2.3
        f.location = (org[0] + math.cos(a) * (0.4 + u) - wind * u * 6, org[1] - 0.4 + math.sin(a) * 0.4, org[2] - u * 2.2 * (1 - min(1, abs(wind))) + 0.3 * math.sin(t * 3 + i))
        f.rotation_euler = (t * 1.3 + i, t * 0.9 + i * 2, i)


def bat(S, i, loc, flap=None, yaw=0.0, hang=True, s=1.0):
    b = S['bats'][i]
    b['root'].location = loc
    b['root'].rotation_euler = (0, 0, yaw) if hang else (PI, 0, yaw)
    b['root'].scale = (s, s, s)
    for j, w in enumerate(b['wings']):
        sg = (-1, 1)[j]
        w.rotation_euler = (0, sg * 1.25, 0) if flap is None else (0, sg * (0.2 + 0.75 * math.sin(flap)), 0)


def goat(S, i, loc, yaw=0.0, nod=0.0):
    g = S['goats'][i]
    g['root'].location, g['root'].rotation_euler = loc, (0, 0, yaw)
    g['neck'].rotation_euler = (nod, 0, 0)


def heli(S, loc, yaw, t, pitch=-0.12, s=1.0):
    hl = S['heli']
    hl['root'].location, hl['root'].rotation_euler = loc, (pitch, 0.05 * math.sin(t * 3), yaw)
    hl['root'].scale = (s, s, s)
    hl['rotor'].rotation_euler = (0, 0, t * 31)
    hl['trot'].rotation_euler = (t * 40, 0, 0)


def footprints(S, A, pts, fade=1.0, s=1.0):
    for i, (x, y, z, yaw) in enumerate(pts):
        p = S['prints'][i]
        p.location, p.rotation_euler = A(x, y, z + 0.015), (0, 0, yaw)
        p.scale = (s * fade, 1.9 * s * fade, 1)


# ---------------------------------------------------------------- shots: hook
def storm_hit(S, k, t, lt):
    """The wall of sand catches him from behind."""
    A = stage(S, 'wild', 'day', 0.75 * ease(k * 1.3))
    wall(S, A(0, lerp(48, 22, k), 0), t)
    y = lerp(3.0, -1.0, k)
    S['man'].place(A(0.3, y, 0), 0.25)
    S['man'].apply(blend(run(t), run(t, lean=0.4), k) | dict(head=(-0.05, lerp(0.2, 1.15, ease(k * 2)))))
    S['face']['man'] = 'scared'
    sandblast(S, A(0, y + 1, 0.2), t, int(20 + 50 * k), (26, 14, 7), 70)
    puffs(S, A(0.3, y + 0.6, 0), t)
    lamp(S, A, (0, y, 2), (5, y - 2, 3), (-4, y - 6, 3), 1200, 900)
    cam(S, A(lerp(2.6, 2.0, k), y - 6.4, 0.75), A(0.1, y + 1.2, lerp(3.4, 2.7, k)), 24, 0.05 * math.sin(t * 9))


def vanish(S, k, t, lt):
    """From above: the brown-out closes over him and he is gone."""
    A = stage(S, 'wild', 'storm')
    wall(S, A(0, lerp(52, 30, ease(k)), -6), t)
    S['man'].place(A(0.2 * math.sin(t * 5), -1.0 - 1.2 * k, 0), 0.5 * math.sin(t * 2.0))
    S['man'].apply(blend(run(t, 1.6, 0.42, 0.6), P('stand', aL=(1.7, -0.5, 1.9, 0.6), aR=(1.2, 0.5, 1.2), lean=0.5, lift=-0.2, lL=(0.5, 0.7), lR=(-0.3, 0.6), head=(0.4, 0)), 0.6))
    S['face']['man'] = 'closed'
    sandblast(S, A(0, -1, 0.3), t, 90, (30, 16, 6), 85, 0.05, 1.4)
    footprints(S, A, [(0.25 * (-1) ** i, 0.6 + i * 1.1, 0, 0.1) for i in range(8)], 1 - k)
    lamp(S, A, (0, -1, 1.5), (4, -4, 5), (-3, -6, 6), 900, 300)
    cam(S, A(lerp(1.5, 0.5, k), lerp(-10.5, -8.5, k), lerp(8.5, 10.5, k)), A(0, lerp(1.5, 0.5, k), 1.2), 26, 0.12 * math.sin(t * 2.2))


def walk_out(S, k, t, lt):
    """Nine days later: a thin figure comes over the crest against the dawn."""
    A = hero(stage(S, 'wild', 'back'))
    y = lerp(19.0, 15.5, k)
    S['man'].place(A(0.4, y, hero_z(0.4, y)), 0.1 * math.sin(t * 1.6), 0.0, 0.06 * math.sin(t * 2.0))
    S['man'].apply(trudge(t, 1.0))
    S['gaunt'], S['pack_on'], S['face']['man'] = True, False, 'tired'
    footprints(S, A, [(0.4 + 0.22 * (-1) ** i, y + 0.7 + i * 0.9, hero_z(0.4, y + 0.7 + i * 0.9), 0.0) for i in range(6)])
    lamp(S, A, (0.4, y, 6.0), (-3, y - 3.5, 7.5), (3.0, y - 7, 5.5), 1500, 1900)
    cz = hero_z(-2.2, 6.0) + 0.5
    cam(S, A(lerp(-2.6, -2.0, k), lerp(5.6, 6.4, k), cz), A(0.4, y, hero_z(0.4, y) + lerp(2.5, 2.1, k)), 40)


def rook_bat(S, k, t, lt):
    """Rook in the tower holds a bat at arm's length and does not like it."""
    A = stage(S, 'tower', 'tower')
    S['rook'].place(A(-0.5, 0.2, 0), -0.35)
    j = 0.05 * math.sin(t * 17)
    S['rook'].apply(P('stand', aR=(1.5 + j, 0.75, 0.1), aL=(0.3, 0.6, 1.3, -0.6), head=(0.05, 0.75), lean=-0.12))
    S['face']['rook'] = 'sick'
    bat(S, 0, A(0.98, -0.72, 2.05 + j * 0.5), t * 30, 0.4, s=1.15)
    for i in range(1, 6):
        bat(S, i, A(-2.2 + i * 0.9, 0.9, 6.25), yaw=0.4 * math.sin(i * 2.0))
    feathers(S, A(-0.5, 0, 2.6), t, 3)
    cam(S, A(lerp(1.7, 1.4, k), lerp(-5.6, -5.0, k), 1.9), A(0.15, 0, 2.5), 34)


# ---------------------------------------------------------------- shots: doubt (the start line)
def rook_start(S, k, t, lt):
    A = stage(S, 'erg', 'dawn')
    S['rook'].place(A(0, 0, 0), 0.25)
    S['rook'].apply(P('cross', head=(0.05, -0.1 + 0.24 * math.sin(t * 4.2) * max(0, 1 - lt / 1.0))))
    S['face']['rook'] = 'deadpan'
    lamp(S, A, (0, 0, 2.4), (4, 3, 4), (-3, -6, 3), 900, 500)
    cam(S, A(lerp(2.1, 1.6, k), lerp(-6.6, -5.4, k), 0.8), A(-0.2, 0, 2.3), 32)


def rook_off(S, k, t, lt):
    """He pops his collar and walks out under the arch into the dunes."""
    A = stage(S, 'erg', 'dawn')
    y = lerp(1.0, 4.6, k)
    pop = ease(lt / 0.3) * (1 - ease((lt - 0.4) / 0.2))
    S['rook'].place(A(-0.6, y, 0), PI - 0.12)
    S['rook'].apply(blend(walk(t, 1.9), P('stand', aL=(0.5, 0.45, 2.4, 0.4), aR=(0.5, 0.45, 2.4, 0.4), head=(-0.1, 0)), pop))
    S['face']['rook'] = 'smirk'
    footprints(S, A, [(-0.6 + 0.2 * (-1) ** i, y - 0.6 - i * 0.8, 0, 0.0) for i in range(5)])
    lamp(S, A, (-0.6, y, 2.2), (-4.5, y - 1, 3.5), (3, y - 5, 4), 1100, 700)
    cam(S, A(1.6, -5.2, 0.6), A(-0.5, lerp(3.0, 5.0, k), 2.5), 28)


# ---------------------------------------------------------------- shots: the race
def race_wide(S, k, t, lt):
    """A string of runners on the marked track under the midday sun."""
    A = stage(S, 'erg', 'day')
    lead = lerp(-22, -30, k)
    for i, (rg, dx, dy, ph) in enumerate(((S['extras'][0], -1.2, 0, 0.0), (S['man'], 1.0, 7, 0.3), (S['extras'][1], -0.6, 15, 0.55), (S['extras'][2], 1.6, 26, 0.8))):
        rg.place(A(dx, lead + dy, 0), 0.0)
        rg.apply(run(t + ph, 2.3))
    for i in range(14):
        u = (t * 1.2 + i / 14) % 1
        j = i % 4
        d = S['dust'][i]
        d.location = A((-1.2, 1.0, -0.6, 1.6)[j] + 0.6 * math.sin(i * 2.0), lead + (0, 7, 15, 26)[j] + 0.6 + 3.5 * u, 0.2 + 0.7 * u)
        d.scale = (0.4 + 1.2 * u,) * 3
    cam(S, A(lerp(7, 6, k), lerp(-44, -42, k), lerp(4.6, 3.8, k)), A(0, lead + 9, 2.2), 30)


def run_close(S, k, t, lt):
    """Tracking beside him; Rook keeps up, one hand on his hat."""
    A = stage(S, 'erg', 'day')
    y = lerp(-34, -41, k)
    S['man'].place(A(-0.5, y, 0), 0.0)
    S['man'].apply(run(t, 2.5))
    S['face']['man'] = 'calm'
    S['rook'].place(A(1.9, y + 0.9, 0), 0.0)
    S['rook'].apply(run(t + 0.2, 2.9, 0.34) | dict(aR=(0.2, 1.9, 1.6, -1.5), head=(0.0, 0.25)))
    S['face']['rook'] = 'shocked'
    puffs(S, A(0.6, y + 1.6, 0), t, 10, 2.2)
    feathers(S, A(1.9, y + 2.2, 2.2), t, 3)
    lamp(S, A, (0, y, 2), (4.5, y + 3, 3.5), None, 900)
    cam(S, A(-2.6, y - 7.6, 1.3), A(0.7, y + 0.4, 2.2), 30)


def rook_jog(S, k, t, lt):
    """Rook, done in, plods along as a runner breezes past him."""
    A = stage(S, 'erg', 'day')
    y = lerp(-52, -53.2, k)
    S['rook'].place(A(-0.9, y, 0), 0.12)
    S['rook'].apply(trudge(t, 1.3, 0.5) | dict(aL=(0.15, 0.2, 0.2), aR=(0.15, 0.2, 0.2), head=(0.35, 0.2)))
    S['face']['rook'] = 'sad'
    e = S['extras'][1]
    ey = lerp(-44, -58, k)
    e.place(A(1.7, ey, 0), 0.0)
    e.apply(run(t, 2.4))
    puffs(S, A(1.7, ey + 1.0, 0), t, 8, 1.4)
    feathers(S, A(-0.9, y + 0.6, 2.4), t, 4)
    lamp(S, A, (-0.9, y, 2.2), (-5, y + 2, 3.5), (2, y - 6, 3), 900, 600)
    cam(S, A(lerp(0.9, 0.5, k), y - 6.4, 1.0), A(-0.2, y, 2.15), 32)


def wall_come(S, k, t, lt):
    """Day four: the horizon stands up and comes at him."""
    A = stage(S, 'wild', 'day', 0.35 * k)
    wall(S, A(0, lerp(110, 72, k), 0), t)
    S['wall'].scale = (1.3, 1, 1.5)
    x = lerp(-5, 2, k)
    S['man'].place(A(x, -2, 0), PI / 2 - 0.1)
    S['man'].apply(blend(run(t, 2.4), P('stand', head=(-0.15, 0.9), aR=(0.9, 0.2, 1.4), lean=0.05), ease((k - 0.45) * 3)))
    S['face']['man'] = 'scared'
    S['mflag'].location = A(6.5, -1.2, 0)
    S['mflag'].rotation_euler = (0, 0.12 * math.sin(t * 9), 0.2)
    sandblast(S, A(0, 6, 0.2), t, 24, (50, 20, 4), 40, 0.02, 1.3)
    cam(S, A(lerp(-3, -1.5, k), -15, 1.4), A(0.5, 30, lerp(11, 13, k)), 24)


def rook_sand(S, k, t, lt):
    """The blast hits Rook: hat clamped down, coat and feathers streaming."""
    A = stage(S, 'wild', 'storm')
    wall(S, A(0, 34, -4), t)
    S['rook'].place(A(0.25 * math.sin(t * 6), 0, 0), -0.55, 0.0, 0.14 + 0.05 * math.sin(t * 11))
    S['rook'].apply(P('hat', aL=(1.3, 0.5, 1.4, 0.5), lean=0.3, lL=(0.5, 0.4), lR=(-0.45, 0.2), head=(0.2, -0.35)))
    S['face']['rook'] = 'shocked'
    sandblast(S, A(0, -1.0, 0.4), t, 80, (18, 9, 5.5), 80, 0.06, 1.2)
    feathers(S, A(-0.2, 0, 2.6), t * 2.2, 8, 1.0)
    lamp(S, A, (0, 0, 2.4), (4.5, 2, 4), (-2.5, -5.5, 3), 1700, 1300)
    cam(S, A(lerp(1.4, 1.0, k), lerp(-5.8, -5.0, k), 1.5), A(-0.1, 0, 2.45), 32, 0.07 * math.sin(t * 8))


def trail_gone(S, k, t, lt):
    """A marker flag tears out of the sand and the footprints fill in."""
    A = stage(S, 'wild', 'storm')
    wall(S, A(0, 36, -4), t)
    g = ease((k - 0.35) * 2.2)
    S['mflag'].location = A(0.3 - 9 * g * g, 0.6, 0.0 + 2.8 * g)
    S['mflag'].rotation_euler = (0.6 * g * math.sin(t * 9), -0.3 - 1.6 * g + 0.12 * math.sin(t * 22), 0.3 + 2.0 * g)
    S['mflag'].scale = (1.3, 1.3, 1.3)
    footprints(S, A, [(1.3 + 0.24 * (-1) ** i, -1.6 + i * 0.95, 0, 0.15) for i in range(7)], 1 - 0.9 * ease(k * 1.4), 1.25)
    sandblast(S, A(0, 0, 0.1), t, 80, (16, 8, 3.2), 75, 0.03, 1.0)
    lamp(S, A, (0, 0, 1), (4, 1.5, 3), (-2, -4, 3.5), 1500, 1500)
    cam(S, A(lerp(-1.0, -0.4, k), -5.0, 0.7), A(0.2, 0.6, lerp(1.3, 1.6, k)), 30, 0.08 * math.sin(t * 7))


# ---------------------------------------------------------------- shots: lost
def run_blind(S, k, t, lt):
    """He keeps going, head down, an arm across his face."""
    A = stage(S, 'wild', 'storm')
    wall(S, A(0, 30, -4), t)
    y = lerp(1.2, -0.6, k)
    S['man'].place(A(0.15 * math.sin(t * 4), y, 0), -0.2 + 0.1 * math.sin(t * 3))
    S['man'].apply(run(t, 1.9, 0.5, 0.75) | dict(aR=(1.75, -0.55, 1.9, 0.7), head=(0.35, -0.2)))
    S['face']['man'] = 'closed'
    sandblast(S, A(0, y - 1.2, 0.5), t, 90, (20, 10, 5.5), 90, 0.05, 1.3)
    lamp(S, A, (0, y, 2.2), (-4.5, y + 2, 4), (2.5, y - 5.5, 2.5), 1600, 1300)
    cam(S, A(lerp(-2.4, -1.9, k), y - 5.6, 2.3), A(0.2, y, 2.25), 34, -0.06 + 0.05 * math.sin(t * 7))


def clear_empty(S, k, t, lt):
    """When it clears: one man and one crow on a dune, and nothing else to the horizon."""
    A = hero(stage(S, 'wild', 'dusk'))
    z = hero_z(0, 16)
    S['man'].place(A(-1.1, 16, z), lerp(0.9, -1.0, ease(k)))
    S['man'].apply(P('stand', aR=(1.9, 0.9, 2.2, -1.0), head=(-0.05, 0.3 * math.sin(t * 2.4))))
    S['face']['man'] = 'scared'
    S['rook'].place(A(1.3, 15.6, hero_z(1.3, 15.6)), -0.5)
    S['rook'].apply(blend(P('stand', head=(0, 0.9)), P('shrug', head=(-0.05, -0.3)), ease((k - 0.3) * 2.5)))
    S['face']['rook'] = 'deadpan'
    lamp(S, A, (0, 16, z + 2), (5, 19, z + 4), (-3, 9, z + 3), 1300, 500)
    cam(S, A(lerp(4.5, 6.5, k), lerp(4.0, 1.0, k), lerp(z + 2.4, z + 5.5, k)), A(0, 16, z + 2.2), 36)


def heli_pass(S, k, t, lt):
    """A search helicopter passes right over him."""
    A = hero(stage(S, 'wild', 'dusk'))
    z = hero_z(0, 16)
    S['man'].place(A(0, 16, z), PI + 0.5 - 1.0 * k)
    wv = math.sin(t * 13)
    S['man'].apply(P('up', aL=(2.7, 0.5 + 0.3 * wv, 0.2), aR=(2.7, 0.5 - 0.3 * wv, 0.2), head=(-0.5, 0), lift=0.08 * abs(wv)))
    heli(S, A(lerp(-17, 15, k), lerp(27, 22, k), z + 10.5), -PI / 2 - 0.15, t)
    lamp(S, A, (0, 16, z + 2), (4, 14, z + 4), (-3, 10, z + 2), 1500, 900)
    cam(S, A(lerp(-1.8, -1.2, k), 9.4, z + 0.5), A(lerp(-2.5, 3.0, k), 20, z + 6.2), 22)


def flare_up(S, k, t, lt):
    """He fires his flare. The helicopter does not turn."""
    A = hero(stage(S, 'wild', 'dusk'))
    z = hero_z(0, 16)
    S['man'].place(A(0, 16, z), 2.1)
    S['man'].apply(P('reach', aR=(2.95, 0.1, 0.05), aL=(0.3, 0.5, 0.4), head=(-0.45, 0.2)))
    S['gun_on'] = True
    e = 1 - (1 - min(1.0, k * 1.2)) ** 2
    fz = z + 3.6 + 13 * e
    S['flare'].location = A(0.5 + 1.6 * e, 16.2, fz)
    S['flarel'].data.energy = 9000
    for i in range(10):
        u = i / 10
        d = S['dust'][i]
        d.location = A(0.5 + 1.6 * e * u + 0.25 * math.sin(i * 2 + t * 4), 16.2, z + 3.6 + (fz - z - 3.6) * u)
        d.scale = (0.16 + 0.3 * (1 - u),) * 3
    heli(S, A(lerp(26, 44, k), lerp(52, 70, k), z + 13), -PI / 2 - 0.5, t)
    lamp(S, A, (0, 16, z + 2), (-4, 18, z + 3), (2, 9, z + 2), 900, 500)
    cam(S, A(lerp(-5.5, -5.0, k), 7.6, z + 0.9), A(1.2, 17, z + lerp(4.6, 8.0, e)), 22)


def rook_wave(S, k, t, lt):
    """Rook jumps and flaps at the shrinking helicopter, then gives up."""
    A = hero(stage(S, 'wild', 'dusk'))
    z = hero_z(0, 16)
    g = ease((k - 0.55) * 3.5)
    wv = math.sin(t * 15)
    S['rook'].place(A(0, 16, z + 0.45 * abs(math.sin(t * 8)) * (1 - g)), PI - 0.9)
    S['rook'].apply(blend(P('up', aL=(2.8, 0.45 + 0.35 * wv, 0.1), aR=(2.8, 0.45 - 0.35 * wv, 0.1), head=(-0.4, 0.1)),
                          P('stand', aL=(0.0, 0.2, 0.1), aR=(0.0, 0.2, 0.1), head=(0.3, 0.75), lean=0.12), g))
    S['face']['rook'] = 'shocked' if g < 0.5 else 'deadpan'
    heli(S, A(lerp(-9, -15, k), lerp(46, 70, k), z + lerp(9, 11, k)), -PI / 2 + 1.2, t, s=1.0)
    feathers(S, A(0, 15.6, z + 2.6), t, 4)
    lamp(S, A, (0, 16, z + 2.4), (4.5, 14, z + 4), (-3, 10.5, z + 2.5), 1500, 1100)
    cam(S, A(lerp(3.4, 3.0, k), lerp(10.6, 11.2, k), z + 1.0), A(-0.9, 17.5, z + 3.1), 30)


# ---------------------------------------------------------------- shots: the shrine
def shrine_wide(S, k, t, lt):
    """At sunset, a small white shrine with a tower, and nobody home."""
    A = stage(S, 'shrine', 'dusk')
    y = lerp(-1.5, 1.0, k)
    S['man'].place(A(-1.2, y, 0), PI + 0.15)
    S['man'].apply(trudge(t, 1.1, 0.3))
    S['rook'].place(A(2.3, -2.6, 0), PI + 0.75)
    S['rook'].apply(P('point', aR=(1.5, -0.15, 0.05), head=(-0.1, -0.9)))
    S['face']['rook'] = 'calm'
    footprints(S, A, [(-1.2 + 0.2 * (-1) ** i, y - 0.7 - i * 0.9, 0, 0.0) for i in range(7)])
    lamp(S, A, (1, -1, 2.2), (7, -2, 4), (-3, -8, 4), 1400, 900)
    cam(S, A(lerp(1.6, 1.2, k), lerp(-10.5, -9.4, k), 1.3), A(-0.4, 6, 4.6), 26)


def bats_up(S, k, t, lt):
    """Inside the tower Rook looks up: the beams are hung with bats."""
    A = stage(S, 'tower', 'tower')
    S['rook'].place(A(-0.9, 0.9, 0), -0.5)
    S['rook'].apply(P('hat', head=(-0.62, 0.15), lean=-0.1))
    S['face']['rook'] = 'shocked'
    for i in range(9):
        y, z = ((0.9, 6.42), (-0.5, 6.72), (2.2, 7.12))[i % 3]
        wr = 0.5 + 0.5 * math.sin(t * 5 + i * 2.1)
        bat(S, i, A(-2.6 + i * 0.66, y, z - 0.42), (t * 16 + i) if (i + int(t * 2.5)) % 4 == 0 else None, 0.5 * math.sin(i * 2.3), s=1.0 + 0.12 * wr)
    cam(S, A(lerp(2.4, 2.0, k), lerp(-4.6, -4.0, k), 0.7), A(-0.5, 0.9, lerp(3.9, 4.5, k)), 22)


def bat_grab(S, k, t, lt):
    """A hand closes round one of them."""
    A = stage(S, 'tower', 'tower')
    g = ease(k * 1.7)
    hz = lerp(4.4, 5.55, g)
    S['hand'].place(A(0.05, 0.7, hz), (-PI / 2 + 0.12, 0.25, 0.1))
    S['hand'].root.scale = (1.5, 1.5, 1.5)
    S['hand'].grip(lerp(0.45, 0.95, ease((k - 0.45) * 3)))
    for i in range(5):
        fl = (t * 34) if i == 2 and k > 0.5 else ((t * 20 + i) if i in (1, 3) and k > 0.55 else None)
        bat(S, i, A(-1.5 + i * 0.75, 0.9, 6.0), fl, 0.3 * math.sin(i * 2.3), s=1.25)
    lamp(S, A, (0, 0.9, 5.6), (2.5, -1.5, 5.0), (-1.5, -3, 4.2), 300, 160)
    cam(S, A(lerp(1.3, 1.0, k), lerp(-3.2, -2.7, k), 4.3), A(0, 0.9, 5.5), 36, 0.03 * math.sin(t * 9))


def rook_gag(S, k, t, lt):
    """Rook turns away, a wing over his beak. Behind him the runner sits against the wall with his back to us."""
    A = stage(S, 'tower', 'tower')
    S['rook'].place(A(0.5, -0.4, 0), 0.5)
    S['rook'].apply(P('stand', aR=(1.25, -0.35, 2.3, 0.9), aL=(0.2, 0.3, 0.4), head=(0.22, -0.55 - 0.1 * ease(k * 2)), lean=0.1))
    S['face']['rook'] = 'sick'
    S['man'].place(A(-1.5, 2.0, 0), PI - 0.5)
    S['man'].apply(P('sit', head=(-0.45, 0), aL=(1.5, 0.2, 2.2), aR=(1.5, 0.2, 2.2), lean=0.1))
    S['pack_on'] = False
    for i in range(1, 5):
        bat(S, i, A(-1.8 + i * 0.9, 0.9, 6.0), yaw=0.3 * i)
    feathers(S, A(0.5, -0.5, 2.6), t, 4)
    lamp(S, A, (0.5, -0.4, 2.4), (3.0, -2.5, 3.2), (-1.5, -4.5, 2.6), 520, 300)
    cam(S, A(lerp(-0.9, -0.6, k), lerp(-5.6, -5.0, k), 1.7), A(0.1, 0.2, 2.35), 32)


# ---------------------------------------------------------------- shots: the walk
def to_mountains(S, k, t, lt):
    """He leaves the shrine behind and walks for the mountains on the horizon."""
    A = stage(S, 'shrine', 'dawn')
    y = lerp(-3.0, 0.5, k)
    S['man'].place(A(9.0, y, 0), PI - 0.1)
    S['man'].apply(trudge(t, 1.15, 0.22) | dict(head=(0.1, 0.0)))
    S['gaunt'], S['face']['man'] = True, 'tired'
    footprints(S, A, [(9.0 - 0.1 * i + 0.2 * (-1) ** i, y - 0.8 - i * 0.95, 0, 0.1) for i in range(9)])
    lamp(S, A, (9, y, 2.2), (13, y - 2, 3.5), (6, y - 6, 3), 1200, 900)
    cam(S, A(lerp(7.4, 7.8, k), lerp(-11.5, -10.5, k), 1.2), A(8.0, y + 8, 3.6), 30)


def lizard(S, k, t, lt):
    """Rook, nose to nose with a lizard on a rock. A hand comes in and takes it."""
    A = stage(S, 'wild', 'day')
    S['rock'].location = A(0.9, -7, 0)
    g = ease((k - 0.55) * 4)
    lz = S['lizard']
    lz['root'].location = A(0.75, -7.1, 0.82 + 1.4 * g)
    lz['root'].rotation_euler = (0.5 * g, 0, PI / 2 + 0.2)
    lz['root'].scale = (2.2, 2.2, 2.2)
    lz['head'].rotation_euler = (0, 0, 0.5 * math.sin(t * 7))
    lz['tail'].rotation_euler = (0, 0, 0.6 * math.sin(t * 9 + 1))
    S['rook'].place(A(-1.25, -7, 0), PI / 2 - 0.25)
    S['rook'].apply(P('hips', lean=0.62, lift=-0.5, lL=(1.3, 1.9), lR=(1.3, 1.9), head=(-0.35 - 0.3 * g, 0.2)))
    S['face']['rook'] = 'smirk' if g < 0.4 else 'shocked'
    S['hand'].place(A(lerp(4.6, 1.3, ease(k * 2.2)), -7.15, lerp(1.9, 1.05, ease(k * 2.2)) + 1.4 * g), (0.0, -0.3, -PI / 2))
    S['hand'].root.scale = (2.2, 2.2, 2.2)
    S['hand'].grip(lerp(0.0, 0.75, g + ease((k - 0.45) * 5) * 0.6))
    lamp(S, A, (0, -7, 1.4), (3.5, -5, 3), None, 900)
    cam(S, A(lerp(0.4, 0.1, k), lerp(-12.4, -11.8, k), 1.0), A(-0.05, -7, 1.55), 34)


def beetle(S, k, t, lt):
    """A beetle crosses the ripples; his shoes come down beside it."""
    A = stage(S, 'wild', 'day')
    b = S['beetle']
    bx = lerp(-0.7, 0.25, k)
    b['root'].location, b['root'].rotation_euler, b['root'].scale = A(bx + 9, -8, 0.0), (0, 0, PI / 2), (2.4, 2.4, 2.4)
    for i, l in enumerate(b['legs']):
        l.rotation_euler = (0, 0, 0.5 * math.sin(t * 30 + i * 2.1))
    footprints(S, A, [(bx + 9 - 0.5 - i * 0.42, -8 + 0.1 * (-1) ** i, 0, PI / 2) for i in range(8)], 1.0, 0.22)
    S['man'].place(A(lerp(7.4, 8.4, k), -7.25, 0), PI / 2 - 0.2)
    S['man'].apply(trudge(t, 1.2, 0.25))
    S['gaunt'] = True
    g = ease((k - 0.5) * 3)
    S['hand'].place(A(lerp(11.6, 9.75, g), -8.05, lerp(1.4, 0.5, g)), (0.5, -0.5, -PI / 2))
    S['hand'].root.scale = (1.7, 1.7, 1.7)
    S['hand'].grip(0.25)
    lamp(S, A, (9, -8, 0.3), (11.5, -6, 2), None, 600)
    cam(S, A(lerp(9.5, 9.2, k), -10.6, 0.42), A(8.9, -7.6, 0.5), 30)


# ---------------------------------------------------------------- shots: found
def tracks(S, k, t, lt):
    """Day nine: hoof prints in the sand. He goes down on his knees beside them."""
    A = stage(S, 'camp', 'dawn')
    pts = []
    for i in range(9):
        for s in (-1, 1):
            pts.append((-52 + s * 0.14 + 0.25 * math.sin(i), -31.5 + i * 0.55, 0, 0.0))
    footprints(S, A, pts, 1.0, 0.45)
    d = ease(k * 1.8)
    S['man'].place(A(-53.3, -29.6, 0), PI / 2 + 0.5)
    S['man'].apply(blend(trudge(t, 1.0), P('stand', lean=0.45, lift=-0.58, lL=(0.35, 2.0), lR=(0.5, 2.1), aR=(0.95, -0.1, 0.2), aL=(0.3, 0.3, 0.6), head=(0.3, 0.0)), d))
    S['gaunt'], S['pack_on'], S['face']['man'] = True, False, 'shock'
    lamp(S, A, (-52.6, -30, 1), (-49, -27, 3), (-55, -34, 3), 1200, 800)
    cam(S, A(lerp(-51.2, -51.5, k), lerp(-34.6, -34.0, k), 0.5), A(-52.6, -29.8, lerp(1.0, 1.25, k)), 30)


def goats(S, k, t, lt):
    """Goats. One of them starts on Rook's coat."""
    A = stage(S, 'camp', 'dawn')
    S['rook'].place(A(-30, -20, 0), 0.2)
    S['rook'].apply(blend(P('stand', head=(0, -0.5)), P('shrug', head=(0.45, -0.75)), ease((k - 0.25) * 3)))
    S['face']['rook'] = 'deadpan'
    ch = 0.25 * math.sin(t * 16)
    goat(S, 0, A(-28.55, -20.25, 0), -PI / 2 + 0.2, 0.2 + ch)
    goat(S, 1, A(-32.2, -18.6, 0), 0.5, -0.5 + 0.2 * math.sin(t * 3))
    goat(S, 2, A(-31.6, -21.9, 0), -0.6, 0.9 + 0.1 * math.sin(t * 7))
    goat(S, 3, A(-27.4, -17.5, 0), 0.2 + 0.2 * math.sin(t * 2), -0.3)
    goat(S, 4, A(-34.5, -16, 0), -0.9, 0.9)
    goat(S, 5, A(-25.5, -20.6 - 1.2 * k, 0), 0.1, -0.2 + 0.2 * math.sin(t * 9))
    lamp(S, A, (-30, -20, 2), (-26, -17, 4), (-33, -26, 3), 1300, 800)
    cam(S, A(lerp(-30.6, -30.3, k), lerp(-27.2, -26.4, k), 1.15), A(-29.8, -20, 2.0), 32)


def girl(S, k, t, lt):
    """A girl minding the herd sees the stranger come out of the desert."""
    A = stage(S, 'camp', 'dawn')
    back = ease((k - 0.45) * 3)
    S['girl'].place(A(-20.0 - 0.5 * back, -13.6 - 0.3 * back, 0), -PI / 2 + 0.75)
    S['girl'].apply(blend(P('stand', aR=(0.9, 0.25, 0.9), head=(0, -0.35)), P('stand', aR=(1.0, 0.3, 1.0), aL=(0.7, 0.6, 1.6), lean=-0.12, head=(-0.05, -0.5), lL=(0.3, 0.1), lR=(-0.3, 0.1)), back))
    S['face']['girl'] = 'shock' if back > 0.3 else 'calm'
    mx = lerp(-12.5, -14.2, k)
    S['man'].place(A(mx, -9.5, 0), PI / 2 + PI - 0.25)
    S['man'].apply(trudge(t, 0.9, 0.34) | dict(aR=(1.2, 0.3, 0.5)))
    S['gaunt'], S['pack_on'], S['face']['man'] = True, False, 'tired'
    goat(S, 0, A(-17.2, -14.6, 0), 2.4, 0.8 + 0.1 * math.sin(t * 6))
    goat(S, 1, A(-21.9, -9.2, 0), -1.4, -0.3)
    goat(S, 3, A(-17.6, -8.2, 0), 1.2, -0.4 + 0.3 * ease(k * 2))
    goat(S, 4, A(-15.5, -12.6, 0), 1.9, 0.85)
    lamp(S, A, (-19, -11.5, 1.6), (-16, -8, 3.5), (-22.5, -16.5, 2.5), 1300, 1000)
    cam(S, A(lerp(-22.0, -21.6, k), lerp(-19.0, -18.4, k), 1.2), A(-17.6, -11.4, 1.5), 32)


def tent(S, k, t, lt):
    """In the tent: a bowl of goat's milk in both hands. Rook raises a glass of tea."""
    A = stage(S, 'camp', 'day')
    S['man'].place(A(-0.5, 7.9, 0.05), 0.15)
    sip = ease(math.sin(PI * min(1, k * 1.3)))
    S['man'].apply(P('sit', aL=(1.0 + 0.5 * sip, -0.25, 1.5 + 0.3 * sip, 0.6), aR=(1.0 + 0.5 * sip, -0.25, 1.5 + 0.3 * sip, 0.6), head=(0.25 - 0.4 * sip, 0), lean=0.12))
    S['gaunt'], S['pack_on'], S['face']['man'] = True, False, 'tired' if sip > 0.5 else 'calm'
    S['bowl'].location = A(-0.42, 7.3 - 0.05 * sip, 1.42 + 0.42 * sip)
    S['bowl'].scale = (1.25, 1.25, 1.25)
    S['elder'].place(A(-2.1, 8.3, 0.05), -0.75)
    S['elder'].apply(P('sit', aR=(0.9, 0.1, 0.7), aL=(0.6, 0.0, 1.4, 0.8), head=(0.1, -0.2), lean=0.2))
    S['girl'].place(A(-2.9, 9.6, 0), -0.6)
    S['girl'].apply(P('stand', head=(0.1, -0.3), aL=(0.3, 0.2, 1.2, 0.8)))
    S['rook'].place(A(1.45, 7.7, 0.05), 0.6)
    tip = math.sin(PI * ease((lt - 0.25) / 0.9)) if lt > 0.25 else 0
    S['rook'].apply(P('sit', aR=(1.25 + 0.3 * tip, 0.25, 1.2), aL=(0.7, -0.1, 1.5, 1.0), head=(0.1, 0.55), lean=0.1))
    S['hat_tip'], S['face']['rook'] = tip * 0.6, 'warm'
    S['glass'].location = A(0.87 + 0.04 * tip, 6.92 - 0.05 * tip, 1.42 + 0.34 * tip)
    S['glass'].scale = (1.3, 1.3, 1.3)
    goat(S, 2, A(4.9, 4.2, 0), 1.1, 0.2 + 0.2 * math.sin(t * 5))
    lamp(S, A, (0, 7.8, 1.5), (4.5, 5, 3), (-2, 2.5, 2.6), 1200, 1500)
    cam(S, A(lerp(0.9, 0.6, k), lerp(0.6, 1.4, k), 1.35), A(-0.1, 8, 1.55), 30)


# ---------------------------------------------------------------- shots: after
def run_again(S, k, t, lt):
    """Years later he is back on the same start line. Rook tips his hat as he goes by."""
    A = stage(S, 'erg', 'day')
    y = lerp(9.5, 2.2, k)
    S['man'].place(A(-0.9, y, 0), 0.0)
    S['man'].apply(run(t, 2.5, 0.22))
    S['face']['man'] = 'happy'
    for i, e in enumerate(S['extras']):
        e.place(A((2.6, -3.2, 0.9)[i], y + (7, 10.5, 15)[i], 0), 0.0)
        e.apply(run(t + 0.3 * i, 2.3))
    tip = math.sin(PI * ease((lt - 0.2) / 0.9)) if lt > 0.2 else 0
    S['rook'].place(A(2.0, 0.6, 0), 0.75)
    S['rook'].apply(blend(P('stand', head=(0, -0.55)), P('hat', head=(0.15, -0.6 + 0.5 * k)), tip))
    S['hat_tip'], S['face']['rook'] = tip, 'warm'
    puffs(S, A(-0.9, y + 0.8, 0), t, 8, 1.2)
    lamp(S, A, (1.6, 0.6, 2.2), (6, 2, 4), (1, -5, 2.5), 1000, 900)
    cam(S, A(lerp(-0.6, -0.2, k), lerp(-7.6, -6.8, k), 0.9), A(0.9, 2.0, 2.5), 28)


def signoff(S, k, t, lt):
    """He flips the runner's steel flask, catches it. Case closed."""
    A = stage(S, 'erg', 'dusk')
    S['rook'].place(A(0, -14, 0), 0.15)
    tip = math.sin(PI * ease(lt / 0.8)) if lt < 0.8 else 0
    S['rook'].apply(blend(P('stand', aL=(0.9, 0.25, 1.2), head=(0.05, 0)), P('hat', aL=(0.9, 0.25, 1.2), head=(0.22, 0)), tip))
    S['hat_tip'], S['face']['rook'] = tip, 'smirk'
    c = max(0.0, min(1.0, (lt - 0.25) / 0.9))
    S['flask'].location = A(-0.75 - 0.2 * c, -14.75, 1.75 + 2.5 * math.sin(c * PI))
    S['flask'].rotation_euler = (t * 13, t * 5, 0)
    S['flask'].scale = (1.5, 1.5, 1.5)
    lamp(S, A, (0, -14, 2.2), (4, -11, 4), (-3, -20, 3), 1300, 700)
    cam(S, A(lerp(1.1, 0.8, k), lerp(-20.4, -19.2, k), 1.0), A(0, -14, 2.05), 38)


# ---------------------------------------------------------------- photographs for the case board
def photo_desert(S, k, t, lt):
    A = hero(stage(S, 'wild', 'day'))
    S['man'].place(A(3, 30, hero_z(3, 30)), PI + 0.4)
    S['man'].apply(trudge(0.3))
    footprints(S, A, [(3 - 0.5 * i + 0.2 * (-1) ** i, 29 - i * 1.0, hero_z(3 - 0.5 * i, 29 - i * 1.0), 0.4) for i in range(16)], 1.0, 1.5)
    cam(S, A(-6, 2, 9), A(2, 34, 3), 34)


def photo_mauro(S, k, t, lt):
    A = stage(S, 'erg', 'day')
    S['man'].place(A(0, 0, 0), 0.2)
    S['man'].apply(P('hips', head=(0, 0.1)))
    S['face']['man'] = 'happy'
    lamp(S, A, (0, 0, 2.4), (3, 2, 4), None, 700)
    cam(S, A(0.7, -3.8, 2.5), A(0, 0, 2.3), 55)


SHOTS3D = {f.__name__: f for f in (
    storm_hit, vanish, walk_out, rook_bat, rook_start, rook_off, race_wide, run_close, rook_jog, wall_come, rook_sand, trail_gone,
    run_blind, clear_empty, heli_pass, flare_up, rook_wave, shrine_wide, bats_up, bat_grab, rook_gag, to_mountains, lizard, beetle,
    tracks, goats, girl, tent, run_again, signoff)}
STILLS = dict(desert=photo_desert, mauro=photo_mauro)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it: the bivouac and the kit every runner carries, a checkpoint on the long stage,
# the night of the storm and the morning after, the spare bottle, the wait on the dune, the inside of the shrine and the
# flag on its roof, the aeroplane, the dry riverbed and its shade, the oasis, the camel ride to a village, the drive to
# hospital, the ward, the dispute (the race's founder, the film crew, the doctor's review) and the returns to the race.
ORG.update(biv=(4000, 2000, 0), hall=(0, 4000, 0), wadi=(6000, 0, 0), oasis=(6000, 2000, 0), post=(8000, 0, 0), ward=(8000, 2000, 0))
DOC = dict(top='ECEFF2', pants='4A5464', hand='D8A888', boot='2A2A30')
BOSS = dict(top='2E3A4E', pants='3A3A44', hand='E0B090', boot='2A2026')
KNEEL = dict(lift=-0.58, lL=(0.35, 2.0), lR=(0.5, 2.1))
TOD.update(
    night=('night', ('2A3260', 0.55), (1.1, 'A8B8FF', (0.45, 0.5, -0.6)), (0.6, '6A7AD0', (-0.5, 0.6, -0.5))),
    hall=(None, ('0C0A08', 1.0), (0.0, 'FFFFFF', (0, 0, -1)), (0.0, 'FFFFFF', (0, 0, -1))),
    room=(None, ('1A1E22', 1.0), (0.0, 'FFFFFF', (0, 0, -1)), (0.0, 'FFFFFF', (0, 0, -1))))


# The kit's add() goes through Blender operators, which get slower with every object already in the scene (this world
# has several thousand). The same primitives built straight from mesh data cost the same however big the scene is, and
# come out identical: the operators call these very bmesh routines. From here on the whole file uses the fast versions,
# and build() lends them to the kit while the rigs are made.
import bmesh  # noqa: E402

_add0, _empty0 = add, empty


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'plane':
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=kw.get('size', 2.0) / 2)
    elif kind in ('cylinder', 'cone'):
        r1, r2 = (kw.get('radius', 1.0),) * 2 if kind == 'cylinder' else (kw.get('radius1', 1.0), kw.get('radius2', 0.0))
        fill = kw.get('end_fill_type', 'NGON')
        bmesh.ops.create_cone(bm, cap_ends=fill != 'NOTHING', cap_tris=fill == 'TRIFAN', segments=kw.get('vertices', 32), radius1=r1, radius2=r2,
                              depth=kw.get('depth', 2.0))
    elif kind == 'ico_sphere':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('subdivisions', 2), radius=kw.get('radius', 1.0))
    else:
        bm.free()
        return _add0(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
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


def face_to(frm, to):
    """Yaw that turns a figure standing at `frm` toward `to` (x, y)."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def rel(loc, yaw, lx, ly, lz=0.0):
    """A point given in a prop's own frame (it faces -Y) moved to where the prop stands."""
    c, s = math.cos(yaw), math.sin(yaw)
    return (loc[0] + lx * c - ly * s, loc[1] + lx * s + ly * c, loc[2] + lz)


def ingroup(S, name, fn):
    """Add more objects to a set that already exists (they hide and show with it)."""
    before = set(bpy.data.objects)
    out = fn(empty(ORG[name]))
    c = S['colls'][name]
    for o in set(bpy.data.objects) - before:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        c.objects.link(o)
    return out


def track(l):
    c = l.constraints[0]
    c.track_axis, c.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
    return l


def figure(parent, loc, yaw, top, legs='3A3A44', skin='C98F6A', hat=None, robe=False, s=1.0):
    """A bystander: blocky, no joints, as tall as a rig. Faces -Y at yaw 0."""
    e = empty(loc, parent, (0, 0, yaw))
    e.scale = (s, s, s)
    if robe:
        add('cone', top, (0, 0, 1.02), radius1=0.56, radius2=0.3, depth=2.04, vertices=7, parent=e)
    else:
        for sx in (-1, 1):
            add('cube', legs, (sx * 0.17, 0, 0.52), scale=(0.2, 0.24, 1.04), size=1, parent=e)
        add('cube', top, (0, 0, 1.56), scale=(0.72, 0.36, 1.05), size=1, parent=e)
    for sx in (-1, 1):
        add('cube', top, (sx * 0.47, 0, 1.52), rot=(0, sx * 0.1, 0), scale=(0.17, 0.2, 0.95), size=1, parent=e)
    add('ico_sphere', skin, (0, 0, 2.42), radius=0.3, subdivisions=1, parent=e)
    if hat:
        add('cylinder', hat, (0, 0.02, 2.64), radius=0.33, depth=0.22, vertices=8, parent=e)
        if not robe:
            add('cube', hat, (0, -0.34, 2.57), scale=(0.44, 0.3, 0.04), size=1, parent=e)
    return e


def shrub(parent, loc, s=1.0):
    e = empty(loc, parent)
    e.scale = (s, s, s)
    for i in range(6):
        a = i * 1.05
        add('cylinder', '6A5238', (0.25 * math.cos(a), 0.25 * math.sin(a), 0.45), rot=(0.55 * math.sin(a), -0.55 * math.cos(a), 0), radius=0.035, depth=1.0,
            vertices=4, parent=e)
    for i in range(4):
        a = i * 1.7 + 0.4
        add('ico_sphere', ('7A8A4A', '8A9656')[i % 2], (0.4 * math.cos(a), 0.4 * math.sin(a), 0.8 + 0.1 * (i % 2)), scale=(1, 1, 0.6), radius=0.3, subdivisions=1,
            parent=e)
    return e


def make_camel(col='C8A070', dark='A8845A', cloth='A8402A'):
    c = empty(FAR)
    add('ico_sphere', col, (0, 0.2, 2.5), scale=(0.75, 1.7, 0.85), radius=1.0, subdivisions=1, parent=c)
    add('ico_sphere', col, (0, 0.35, 3.3), scale=(0.6, 0.85, 0.7), radius=0.8, subdivisions=1, parent=c)
    add('cube', cloth, (0, 0.3, 3.0), scale=(1.64, 1.6, 0.5), size=1, parent=c)
    add('cube', 'E8C23A', (0, 0.3, 2.78), scale=(1.68, 1.66, 0.08), size=1, parent=c)
    legs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            l = empty((sx * 0.45, 0.2 + sy * 1.15, 2.1), c)
            add('cylinder', dark, (0, 0, -1.05), radius=0.13, depth=2.1, vertices=5, parent=l)
            add('cube', dark, (0, -0.05, -2.05), scale=(0.34, 0.42, 0.14), size=1, parent=l)
            legs.append(l)
    neck = empty((0, -1.2, 2.8), c)
    add('cylinder', col, (0, -0.55, 0.75), rot=(0.65, 0, 0), radius=0.24, depth=2.0, vertices=6, parent=neck)
    add('cube', col, (0, -1.4, 1.7), rot=(-0.12, 0, 0), scale=(0.44, 1.0, 0.44), size=1, parent=neck)
    add('cube', dark, (0, -1.92, 1.6), scale=(0.36, 0.14, 0.3), size=1, parent=neck)
    for sx in (-1, 1):
        add('cube', '0E0D14', (sx * 0.23, -1.5, 1.8), scale=(0.03, 0.1, 0.08), size=1, parent=neck)
        add('cone', col, (sx * 0.17, -1.0, 2.0), radius1=0.07, radius2=0.0, depth=0.24, vertices=4, parent=neck)
    add('cylinder', dark, (0, 1.95, 2.2), rot=(-0.35, 0, 0), radius=0.05, depth=1.1, vertices=4, parent=c)
    return dict(root=c, legs=legs, neck=neck)


def make_plane():
    p = empty(FAR)
    add('cylinder', 'F2EEE4', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.62, depth=6.4, vertices=8, parent=p)
    add('cone', 'C8402A', (0, -3.7, 0), rot=(PI / 2, 0, 0), radius1=0.62, radius2=0.12, depth=1.0, vertices=8, parent=p)
    add('cube', 'F2EEE4', (0, -0.6, 0.62), scale=(11.5, 1.5, 0.14), size=1, parent=p)
    add('cube', 'C8402A', (0, -0.6, 0.71), scale=(11.5, 0.4, 0.04), size=1, parent=p)
    add('cube', 'F2EEE4', (0, 3.0, 0.2), scale=(3.8, 0.9, 0.1), size=1, parent=p)
    add('cube', 'C8402A', (0, 3.1, 0.9), rot=(-0.3, 0, 0), scale=(0.1, 1.0, 1.5), size=1, parent=p)
    add('cube', '26364E', (0, -1.9, 0.5), scale=(0.9, 1.1, 0.4), size=1, parent=p, rough=0.2)
    prop = empty((0, -4.25, 0), p)
    add('cube', '2A2E36', (0, 0, 0), scale=(0.2, 0.05, 2.6), size=1, parent=prop)
    return dict(root=p, prop=prop)


def make_jeep():
    j = empty(FAR)
    add('cube', '6A7248', (0, 0, 0.95), scale=(2.1, 4.6, 0.8), size=1, parent=j)
    add('cube', '5A6240', (0, -1.75, 1.45), scale=(2.0, 1.3, 0.35), size=1, parent=j)
    add('cube', '4A5236', (0, -2.36, 0.8), scale=(2.2, 0.16, 0.36), size=1, parent=j)
    for sx in (-1, 1):
        add('cube', 'FFF2C0', (sx * 0.72, -2.33, 1.2), scale=(0.3, 0.06, 0.24), size=1, parent=j, emit=1.5)
        add('cube', '4A5236', (sx * 0.98, -1.1, 2.0), scale=(0.08, 0.08, 1.0), size=1, parent=j)
        add('cube', '3A3A30', (sx * 0.5, 0.0, 1.5), scale=(0.75, 0.2, 0.9), size=1, parent=j)
    add('cube', '4A5236', (0, -1.1, 2.48), scale=(2.04, 0.08, 0.08), size=1, parent=j)
    add('cube', '3A3A30', (0, 1.55, 1.5), scale=(1.8, 0.2, 0.9), size=1, parent=j)
    add('cylinder', '2A2A26', (0, 2.42, 1.3), rot=(PI / 2, 0, 0), radius=0.5, depth=0.26, vertices=10, parent=j)
    wheels = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            wh = empty((sx * 1.1, sy * 1.5, 0.55), j)
            add('cylinder', '1E1E1C', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.55, depth=0.36, vertices=10, parent=wh)
            add('cube', '8A8A7A', (sx * 0.19, 0, 0), scale=(0.03, 0.7, 0.16), size=1, parent=wh)
            wheels.append(wh)
    d = empty((0.5, -0.25, 1.0), j)      # the driver, a soldier in olive
    add('cube', '4E5A3A', (0, 0, 0.75), scale=(0.7, 0.36, 0.95), size=1, parent=d)
    add('ico_sphere', 'B07850', (0, 0, 1.5), radius=0.29, subdivisions=1, parent=d)
    add('cylinder', '3E4830', (0, 0.02, 1.72), radius=0.32, depth=0.18, vertices=8, parent=d)
    for sx in (-1, 1):
        add('cube', '4E5A3A', (sx * 0.4, -0.35, 0.95), rot=(1.1, 0, 0), scale=(0.16, 0.18, 0.8), size=1, parent=d)
    add('cylinder', '1E1E1C', (0.5, -0.95, 1.85), rot=(1.1, 0, 0), radius=0.3, depth=0.06, vertices=10, parent=j)
    return dict(root=j, wheels=wheels)


def make_bottle(level):
    b = empty(FAR)
    add('cylinder', 'D8ECF2', (0, 0, 0.25), radius=0.1, depth=0.5, vertices=8, parent=b, rough=0.15)
    add('cone', 'D8ECF2', (0, 0, 0.56), radius1=0.1, radius2=0.04, depth=0.12, vertices=8, parent=b, rough=0.15)
    add('cylinder', 'FF7A1A', (0, 0, 0.66), radius=0.05, depth=0.08, vertices=6, parent=b)
    if level > 0:
        add('cylinder', '3A8AC8', (0, 0, 0.02 + level * 0.25), radius=0.105, depth=level * 0.5, vertices=8, parent=b, emit=0.3)
    return b


def make_itflag():
    f = empty(FAR)
    add('cylinder', 'C8B48A', (0, 0, 0.45), radius=0.025, depth=0.9, vertices=5, parent=f)
    for i, c in enumerate(('2E9A4A', 'F6F2E8', 'D8362A')):
        add('cube', c, (0.1 + i * 0.16, 0, 0.74), scale=(0.16, 0.02, 0.3), size=1, parent=f, emit=0.25)
    return f


# ---------------------------------------------------------------- new sets
def set_biv(r):
    """The bivouac before a stage: a row of low open tents, a fire, and the kit table. Plain cloth, no lettering."""
    add('plane', 'D2A260', (0, 0, 0), size=1900, parent=r)
    dunes(r, 110, lambda x, y, m: (x * x + y * y) < (46 + m) ** 2, dmin=56, span=520, seed=3.3)
    ripples(r, 22, (70, 40), 0.33)
    for i in range(6):
        t = empty((-30 + i * 12, 13 + (i % 2) * 2.5, 0), r, (0, 0, 0.08 * math.sin(i * 2.0)))
        add('cube', ('2E2622', '3A2E26')[i % 2], (0, 0, 2.5), rot=(0.12, 0, 0), scale=(9.5, 6.5, 0.14), size=1, parent=t)
        add('cube', '241E1A', (0, 3.2, 1.2), scale=(9.5, 0.12, 2.4), size=1, parent=t)
        for sx in (-1, 1):
            for sy in (-1, 1):
                add('cylinder', '7A5A3A', (sx * 4.5, sy * 3.0, 1.25 - sy * 0.18), radius=0.08, depth=2.5, vertices=5, parent=t)
        add('cube', ('A8402A', '2C5E8C', 'D8A83A')[i % 3], (0.5 * math.sin(i), 0.6, 0.04), scale=(7.5, 4.5, 0.06), size=1, parent=t)
        for j in range(3):
            add('cube', ('C8402A', '3A8AC8', 'E8C23A', '4E8A40')[(i + j) % 4], (-3 + j * 2.6, 1.5 + 0.5 * ((i + j) % 2), 0.4), rot=(0, 0, 0.4 * j),
                scale=(0.6, 0.4, 0.8), size=1, parent=t)
    for i in range(6):
        add('cube', '4A3626', (-9 + 0.5 * math.cos(i * 1.05), -1 + 0.5 * math.sin(i * 1.05), 0.12), rot=(0, 0.5, i * 1.05), scale=(0.9, 0.14, 0.14), size=1, parent=r)
    add('cone', 'FF8A2A', (-9, -1, 0.5), radius1=0.34, radius2=0.0, depth=0.9, vertices=5, parent=r, emit=6)
    light((-9, -1, 1.2), 900, 'FF8A2A', kind='POINT', parent=r)
    add('cube', '8A6A44', (0, 0, 0.5), scale=(3.4, 1.5, 1.0), size=1, parent=r)
    add('cube', 'A88458', (0, 0, 1.02), scale=(3.6, 1.7, 0.06), size=1, parent=r)
    for i in range(6):
        add('cube', ('E8C23A', 'C8402A', '4E8A40', 'F2EEE4', '3A8AC8', 'E88A3A')[i], (-1.5 + (i % 3) * 0.42, -0.3 + (i // 3) * 0.5, 1.22), rot=(0, 0, 0.2 * math.sin(i * 2)),
            scale=(0.32, 0.22, 0.36), size=1, parent=r)
    add('cylinder', '3A6AA8', (-0.1, 0.35, 1.22), rot=(0, PI / 2, 0.3), radius=0.17, depth=0.7, vertices=8, parent=r)
    for x in (0.25, 0.55):
        add('cylinder', 'D8ECF2', (x, -0.3, 1.3), radius=0.1, depth=0.5, vertices=8, parent=r, rough=0.15)
        add('cylinder', 'FF7A1A', (x, -0.3, 1.6), radius=0.05, depth=0.1, vertices=6, parent=r)
    add('cylinder', 'FF5A1A', (1.45, -0.3, 1.13), rot=(PI / 2, 0, 0.5), radius=0.07, depth=0.6, vertices=6, parent=r, emit=0.6)
    add('cylinder', 'D8362A', (1.6, -0.03, 1.13), rot=(PI / 2, 0, 0.5), radius=0.075, depth=0.12, vertices=6, parent=r, emit=0.6)
    for i, (x, y, yw, c, hc) in enumerate(((-13, 7, 0.4, '3A8AC8', 'F4F0E6'), (-11.5, 8, -0.6, 'E8C23A', 'F4F0E6'), (-10.2, 1.6, 2.6, 'B03A4A', None),
                                           (9, 8, 0.2, '4E8A40', 'F4F0E6'), (11, 6.5, -0.5, 'F2EEE4', 'C8402A'), (13.5, 9, 0.9, 'E88A3A', None),
                                           (-20, 9, 0.2, 'F2EEE4', 'F4F0E6'), (20, 10, -0.3, '3A8AC8', None))):
        figure(r, (x, y, 0), yw, c, '2A3550', ('C98F6A', 'B07850', 'E0B090')[i % 3], hc)
    for s in (-1, 1):
        flag(r, (s * 17, 2, 0), 5.0, 'F4EEDF')
    for i in range(4):
        add('cube', ('3A8AC8', '2C5E8C')[i % 2], (6.5 + (i % 2) * 0.8, -1.5 + (i // 2) * 0.8, 0.4), scale=(0.6, 0.5, 0.8), size=1, parent=r)
    mountains(r, 560, ('8A6A90', '7A5A8A', '9A7A96', '6A4E80'))
    return {}


def add_checkpoint(r):
    """A checkpoint beside the track on the erg set, well south of everything the other shots look at."""
    c = empty((-5.2, -70, 0), r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', 'F4EEDF', (sx * 2.2, sy * 1.6, 1.5), radius=0.07, depth=3.0, vertices=5, parent=c)
    add('cube', 'F4EEDF', (0, 0, 3.05), scale=(5.0, 3.8, 0.1), size=1, parent=c)
    add('cube', 'FF7A1A', (0, -1.9, 2.85), scale=(5.0, 0.06, 0.4), size=1, parent=c)
    add('cube', '8A6A44', (1.2, 0, 0.55), scale=(1.2, 3.0, 1.1), size=1, parent=c)
    for i in range(8):
        add('cylinder', 'D8ECF2', (1.0 + (i % 2) * 0.36, -1.1 + (i // 2) * 0.62, 1.38), radius=0.1, depth=0.5, vertices=8, parent=c, rough=0.15)
        add('cylinder', '3A8AC8', (1.0 + (i % 2) * 0.36, -1.1 + (i // 2) * 0.62, 1.32), radius=0.105, depth=0.36, vertices=8, parent=c, emit=0.3)
    for i in range(5):
        add('cube', '3A6AA8', (-1.0 - (i % 2) * 0.7, -1.0 + i * 0.5, 0.35), scale=(0.6, 0.45, 0.7), size=1, parent=c)
    figure(c, (0.0, -0.4, 0), PI / 2, 'F2EEE4', '2A3550', 'B07850', 'FF7A1A')
    figure(c, (-0.6, 1.0, 0), PI / 2 + 0.5, 'F2EEE4', '2A3550', 'E0B090', 'FF7A1A')
    flag(r, (-8.6, -66.5, 0), 5.0, 'F4EEDF')
    flag(r, (-8.6, -73.5, 0), 5.0, 'FF7A1A')
    return {}


def set_hall(r):
    """Inside the shrine: one bare whitewashed room, two pillars, a niche in the far wall, a doorway full of daylight."""
    add('plane', '8A7252', (0, 0, 0), size=40, parent=r)
    wl = 'D8C8A6'
    add('cube', wl, (0, 4.7, 3), scale=(11.4, 0.4, 6), size=1, parent=r)
    add('cube', wl, (-5.7, 0, 3), scale=(0.4, 9.8, 6), size=1, parent=r)
    add('cube', wl, (5.7, -2.6, 3), scale=(0.4, 4.6, 6), size=1, parent=r)
    add('cube', wl, (5.7, 3.4, 3), scale=(0.4, 2.8, 6), size=1, parent=r)
    add('cube', wl, (5.7, 0.85, 4.9), scale=(0.4, 2.3, 2.2), size=1, parent=r)
    add('cube', '3A2E22', (0, 0, 6.2), scale=(11.8, 10.2, 0.4), size=1, parent=r)
    for i in range(5):
        add('cylinder', '4A3626', (0, -3.6 + i * 1.9, 5.85), rot=(0, PI / 2, 0), radius=0.16, depth=11.2, vertices=6, parent=r)
    add('cube', '5A4630', (0, 4.46, 1.7), scale=(1.7, 0.1, 3.4), size=1, parent=r)
    add('cylinder', '5A4630', (0, 4.46, 3.4), rot=(PI / 2, 0, 0), radius=0.85, depth=0.1, vertices=10, parent=r)
    for sx in (-1, 1):
        add('cylinder', 'C8B892', (sx * 2.7, 1.9, 3), radius=0.36, depth=6, vertices=7, parent=r)
        add('cube', 'B8A882', (sx * 2.7, 1.9, 0.2), scale=(1.0, 1.0, 0.4), size=1, parent=r)
    door = add('cube', 'FFE2B0', (6.0, 0.85, 1.9), scale=(0.06, 2.3, 3.8), size=1, parent=r, emit=7)
    add('cube', 'FFE8C0', (-5.48, -1.2, 4.2), scale=(0.06, 0.5, 1.2), size=1, parent=r, emit=9)
    for i, (x, y, c) in enumerate(((-1.6, 0.4, '8A4A3A'), (1.4, -1.2, '4A5A7A'), (-3.3, 3.0, '9A7A3A'))):
        add('cube', c, (x, y, 0.03), rot=(0, 0, 0.2 * (i - 1)), scale=(2.6, 1.7, 0.05), size=1, parent=r)
    for i in range(7):
        add('ico_sphere', ('B8A882', 'A89872')[i % 2], (-4.6 + 0.5 * math.sin(i * 2), -3.6 + i * 0.5, 0.12), scale=(1, 1, 0.5), radius=0.2 + 0.08 * (i % 3), subdivisions=1,
            parent=r)
    for x, y, s in ((4.4, 3.7, 1.0), (3.6, 4.0, 0.7), (-4.7, 3.9, 0.85)):
        add('ico_sphere', '9A6A44', (x, y, 0.42 * s), scale=(s, s, s * 1.15), radius=0.42, subdivisions=1, parent=r)
    a1, a2 = empty((0, 0.8, 1.2), r), empty((0, 1.5, 3.0), r)
    ld = track(light((5.0, 0.85, 2.4), 1500, 'FFD9A0', 2.4, a1, parent=r))
    lf = track(light((-1.5, -6.5, 4.0), 260, '8A9AE0', 5.0, a2, parent=r))
    lo = track(light((-4.2, -3.6, 2.4), 200, 'FF7A1A', 2.5, a1, parent=r))
    return dict(hl_door=ld, hl_fill=lf, hl_orange=lo, hl_emit=door)


def set_wadi(r):
    """A dry riverbed with a wall of rock and one overhang: the only shade for a long way."""
    add('plane', 'C9A46C', (0, 0, 0), size=1900, parent=r)
    for i in range(30):
        add('cube', ('B8905A', 'AE8650', 'C09A62')[i % 3], (-34 + i * 2.4 + 0.6 * math.sin(i * 1.9), -2 + 1.6 * math.sin(i * 0.7), 0.02),
            rot=(0, 0, 0.3 * math.sin(i * 2.3)), scale=(2.2, 1.9 + 0.5 * (i % 2), 0.04), size=1, parent=r)
    for i in range(16):
        add('ico_sphere', ('8A6248', '7A563E', '96704F')[i % 3], (-30 + i * 4 + math.sin(i * 1.3), 9.5 + 1.5 * math.cos(i * 2.1), 2.2),
            scale=(1.2, 0.9, 1.0 + 0.25 * (i % 3)), radius=3.2, subdivisions=1, parent=r)
    for i in range(10):
        add('ico_sphere', ('7A563E', '8A6248')[i % 2], (-27 + i * 6 + 2 * math.sin(i * 1.9), 15 + 2 * math.cos(i), 4.5), scale=(1.4, 1.0, 1.2), radius=4.5,
            subdivisions=1, parent=r)
    add('cube', '7A563E', (0.5, 5.4, 3.75), rot=(0.1, 0.04, 0.06), scale=(9.0, 5.4, 0.9), size=1, parent=r)
    add('cube', '6A4A36', (-4.4, 6.6, 1.7), scale=(1.4, 2.6, 3.4), size=1, parent=r)
    add('cube', '6A4A36', (5.3, 6.8, 1.7), rot=(0, 0, 0.2), scale=(1.5, 2.4, 3.4), size=1, parent=r)
    add('cube', '5A3E2E', (0.5, 7.6, 1.7), scale=(9.0, 0.6, 3.4), size=1, parent=r)
    for x, y, s in ((-6, -1, 1.3), (-9.5, 3.5, 1.0), (9, 2.5, 1.2), (12.5, -1.5, 0.9), (3.5, -6.5, 0.8), (-13, -4, 1.1), (16, 4, 1.0), (-17, 2, 1.2)):
        shrub(r, (x, y, 0), s)
    for i in range(12):
        a = i * 2.399
        d = 9 + (i * 5 % 12)
        add('ico_sphere', ('8A6A54', '7A5C4A', '96765C')[i % 3], (math.cos(a) * d * 1.6, -6 + math.sin(a) * 4 - 2, 0.2), scale=(1.2, 1, 0.7), radius=0.4 + 0.25 * (i % 3),
            subdivisions=1, parent=r)
    dunes(r, 80, lambda x, y, m: abs(y) < 40 + m and abs(x) < 60 + m, dmin=60, span=520, seed=5.2)
    mountains(r, 330, ('7A5A70', '8A6A7A', '6A4E66', '9A7A86'))
    return {}


def set_oasis(r):
    """A pool in a hollow, reeds and palms round it, dunes all round."""
    add('plane', 'D4A45E', (0, 0, 0), size=1900, parent=r)
    dunes(r, 110, lambda x, y, m: (x * x + (y - 6) ** 2) < (44 + m) ** 2, dmin=52, span=520, seed=6.1)
    add('cylinder', 'B88A50', (0, 8, 0.01), scale=(1.3, 0.8, 1), radius=8.3, depth=0.03, vertices=18, parent=r)
    add('cylinder', '2E8A9A', (0, 8, 0.04), scale=(1.3, 0.8, 1), radius=7.0, depth=0.05, vertices=18, parent=r, rough=0.08)
    add('cylinder', '4AB0B8', (0.8, 8.6, 0.06), scale=(1.3, 0.8, 1), radius=4.0, depth=0.05, vertices=14, parent=r, rough=0.08)
    for i in range(40):
        a = 0.3 + i * (PI - 0.6) / 39 + 0.03 * math.sin(i * 3)
        rr = 7.3 + 0.5 * math.sin(i * 1.7)
        hh = 1.4 + 0.9 * ((i * 0.618) % 1)
        add('cylinder', ('4E8A40', '6A9A48', '3E7A3A')[i % 3], (1.3 * rr * math.cos(a), 8 + 0.8 * rr * math.sin(a), hh / 2), rot=(0.12 * math.sin(i), 0.12 * math.cos(i * 2), 0),
            radius=0.05, depth=hh, vertices=4, parent=r)
    for x, y, hh, tl in ((-10, 13, 9, 0.1), (-6.5, 16.5, 10.5, -0.08), (-2, 18, 8.5, 0.12), (3.5, 17.5, 10, -0.1), (8.5, 15, 9, 0.14), (12, 11, 7.5, -0.12),
                         (-13.5, 8, 7.5, 0.16), (15, 5, 8, 0.1), (-16, 2, 6.5, -0.1)):
        palm(r, x, y, hh, tl)
    for i in range(10):
        a = PI + 0.3 + i * (PI - 0.6) / 9
        add('ico_sphere', ('8A6A54', '7A5C4A')[i % 2], (1.3 * 8.6 * math.cos(a), 8 + 0.8 * 8.6 * math.sin(a), 0.15), scale=(1.2, 1, 0.6), radius=0.35 + 0.15 * (i % 3),
            subdivisions=1, parent=r)
    for i in range(14):
        a = i * 2.399
        add('cone', ('6A9A48', '4E8A40')[i % 2], (12 * math.cos(a) * 1.2, 8 + 9 * math.sin(a), 0.25), radius1=0.3, radius2=0.0, depth=0.5, vertices=5, parent=r)
    glints = [add('cube', 'FFFFFF', (-5 + (i * 0.618 % 1) * 10, 4.2 + (i * 0.377 % 1) * 7, 0.09), scale=(0.7, 0.07, 0.01), size=1, parent=r, emit=5) for i in range(12)]
    mountains(r, 540, ('7A5A8A', '8A6A90', '6A4E80', '9A7A96'))
    return dict(glints=glints)


def set_post(r):
    """A desert village: flat-roofed mud houses round a square, a well, a bare flagpole."""
    add('plane', 'CDA874', (0, 0, 0), size=1900, parent=r)
    for i, (x, y, w_, d_, hh) in enumerate(((-15, 13, 9, 7, 4.5), (-3.5, 17, 10, 7, 5.6), (8.5, 14, 8, 7, 4.2), (19, 8, 7, 8, 4.0), (-25, 5, 7, 8, 3.8), (29, 16, 8, 7, 4.6),
                                            (-34, 14, 8, 7, 4.2))):
        c = ('C89A62', 'B88A56', 'D2A66E')[i % 3]
        add('cube', c, (x, y, hh / 2), scale=(w_, d_, hh), size=1, parent=r)
        add('cube', mixc(c, '000000', 0.15), (x, y, hh + 0.2), scale=(w_ + 0.4, d_ + 0.4, 0.4), size=1, parent=r)
        add('cube', '2A1E14', (x - w_ * 0.2, y - d_ / 2 - 0.03, 1.3), scale=(1.3, 0.1, 2.6), size=1, parent=r)
        add('cube', '2A1E14', (x + w_ * 0.25, y - d_ / 2 - 0.03, 2.6), scale=(0.8, 0.1, 0.8), size=1, parent=r)
        for j in range(4):
            add('cylinder', '5A4630', (x - w_ / 2 + 1 + j * (w_ - 2) / 3, y - d_ / 2 - 0.3, hh - 0.5), rot=(PI / 2, 0, 0), radius=0.09, depth=0.8, vertices=5, parent=r)
    for i in range(6):
        add('cube', 'B88A56', (-21 + i * 2.2, -6.5 - 0.2 * math.sin(i), 0.55 - 0.05 * (i % 3)), rot=(0, 0, 0.05 * math.sin(i * 2)), scale=(2.2, 0.5, 1.1), size=1, parent=r)
    add('cylinder', '9A7A56', (5, 5, 0.5), radius=1.1, depth=1.0, vertices=10, parent=r)
    add('cylinder', '1E3A46', (5, 5, 1.0), radius=0.9, depth=0.04, vertices=10, parent=r)
    for sx in (-1, 1):
        add('cylinder', '5A4630', (5 + sx * 1.0, 5, 1.6), radius=0.07, depth=2.2, vertices=5, parent=r)
    add('cylinder', '5A4630', (5, 5, 2.7), rot=(0, PI / 2, 0), radius=0.07, depth=2.3, vertices=5, parent=r)
    add('cylinder', 'D8D2C0', (-8, 7, 4.0), radius=0.09, depth=8.0, vertices=6, parent=r)
    palm(r, 14, 3, 7.5, 0.1)
    palm(r, -19, 9.5, 8.5, -0.12)
    for i, (x, y, yw, c, rb, hc) in enumerate(((-6, 4.5, 0.3, '2C3E8C', True, '2C3E8C'), (-4.4, 5.2, -0.2, 'E8E0CC', True, 'E8E0CC'), (1.5, 7.5, 0.1, '6A4A3A', True, None),
                                               (9.5, 6.5, -0.5, '2C5E8C', True, 'F2EEE4'), (12.5, -1.2, -1.2, '4E5A3A', False, '3E4830'),
                                               (-12, 6.2, 0.6, 'E8E0CC', True, '8A3A30'), (17, 2.5, -0.7, '1E2A5E', True, '1E2A5E'))):
        figure(r, (x, y, 0), yw, c, '3E4830', ('8A5A3C', 'B07850', '7A4E34')[i % 3], hc, rb, (1.0, 0.95, 0.6, 1.0, 1.0, 0.9, 1.0)[i])
    dunes(r, 100, lambda x, y, m: (x * x + y * y) < (62 + m) ** 2, dmin=70, span=520, seed=7.7)
    mountains(r, 560, ('8A6A7A', '9A7A86', '7A5A70', 'A88A92'))
    return {}


def set_ward(r):
    """A hospital room (bed, drip, window) and, well off to one side, a doctor's study (desk, lamp, shelves)."""
    add('plane', 'B4BEB6', (0, 0, 0), size=30, parent=r)
    wl = 'C8D8CE'
    add('cube', wl, (0, 5.2, 3.5), scale=(17, 0.3, 7), size=1, parent=r)
    add('cube', wl, (-8.4, 0, 3.5), scale=(0.3, 11, 7), size=1, parent=r)
    add('cube', wl, (8.4, 0, 3.5), scale=(0.3, 11, 7), size=1, parent=r)
    add('cube', '8AA89A', (0, 5.02, 0.9), scale=(17, 0.06, 1.8), size=1, parent=r)
    add('cube', 'E6F4FF', (4.2, 5.0, 3.9), scale=(3.4, 0.1, 2.6), size=1, parent=r, emit=5)
    for x in (2.5, 4.2, 5.9):
        add('cube', 'F2EEE4', (x, 4.92, 3.9), scale=(0.12, 0.1, 2.7), size=1, parent=r)
    add('cube', 'F2EEE4', (4.2, 4.92, 3.9), scale=(3.5, 0.1, 0.12), size=1, parent=r)
    for bx in (0, -5.6):
        add('cube', 'E8ECEE', (bx, 1.6, 0.9), scale=(2.7, 6.2, 0.3), size=1, parent=r)
        add('cube', 'F6F6F2', (bx, 1.6, 1.17), scale=(2.5, 6.0, 0.26), size=1, parent=r)
        add('cube', 'D8DEE2', (bx, 4.75, 1.8), scale=(2.8, 0.14, 1.9), size=1, parent=r)
        add('cube', 'D8DEE2', (bx, -1.52, 1.1), scale=(2.8, 0.14, 0.9), size=1, parent=r)
        add('cube', 'FFFFFF', (bx, 3.9, 1.5), rot=(-0.5, 0, 0), scale=(1.9, 1.2, 0.4), size=1, parent=r)
        for sx in (-1, 1):
            for y in (-1.3, 4.5):
                add('cylinder', '9AA4AA', (bx + sx * 1.25, y, 0.4), radius=0.06, depth=0.8, vertices=5, parent=r)
    add('cube', '3A9A9A', (0, 0.4, 1.68), scale=(2.56, 3.7, 0.76), size=1, parent=r)
    add('cube', 'F6F6F2', (0, 2.2, 1.7), scale=(2.6, 0.5, 0.8), size=1, parent=r)
    add('cube', '6AA8C8', (-5.6, 1.2, 1.4), scale=(2.56, 5.2, 0.24), size=1, parent=r)
    add('cylinder', 'B8C0C6', (-2.1, 3.6, 2.4), radius=0.045, depth=4.8, vertices=5, parent=r)
    add('cube', 'B8C0C6', (-2.1, 3.6, 0.06), scale=(1.0, 1.0, 0.1), size=1, parent=r)
    add('cube', 'B8C0C6', (-2.1, 3.6, 4.75), scale=(0.7, 0.05, 0.05), size=1, parent=r)
    add('cube', 'E8F6FF', (-1.85, 3.6, 4.25), scale=(0.34, 0.12, 0.7), size=1, parent=r, emit=0.6)
    add('cube', 'D8D2C0', (2.5, 3.9, 0.75), scale=(1.2, 1.2, 1.5), size=1, parent=r)
    add('cylinder', 'FF7A1A', (2.3, 3.7, 1.66), radius=0.14, depth=0.3, vertices=8, parent=r)
    add('cube', 'F6F2E8', (-3.0, 5.0, 4.4), scale=(1.9, 0.06, 1.4), size=1, parent=r)
    for i in range(4):
        add('cube', '8AA89A', (-3.0, 4.95, 4.85 - i * 0.3), scale=(1.5 - 0.3 * (i % 2), 0.06, 0.08), size=1, parent=r)
    add('cylinder', 'F6F2E8', (7.2, 5.0, 5.2), rot=(PI / 2, 0, 0), radius=0.55, depth=0.08, vertices=14, parent=r)
    add('cube', 'B8D0C4', (7.6, 2.4, 2.8), scale=(0.1, 3.6, 5.2), size=1, parent=r)
    figure(r, (-2.9, 0.9, 0), PI / 2 + 0.25, 'ECEFF2', '4A5464', 'B07850')
    a1 = empty((0, 2, 1.8), r)
    track(light((0, -1.5, 6.4), 1500, 'FFF4E0', 5.0, a1, parent=r))
    track(light((4.2, 3.6, 4.0), 700, 'DCEBFF', 2.5, a1, parent=r))
    track(light((-4.5, -4.5, 2.6), 260, 'FF7A1A', 2.5, a1, parent=r))
    # the study, 40 units east
    o = empty((40, 0, 0), r)
    add('plane', '5A4636', (0, 0, 0.01), size=26, parent=o)
    add('cube', '3E4A44', (0, 5.2, 3.5), scale=(17, 0.3, 7), size=1, parent=o)
    add('cube', '36423C', (-8.4, 0, 3.5), scale=(0.3, 11, 7), size=1, parent=o)
    add('cube', '36423C', (8.4, 0, 3.5), scale=(0.3, 11, 7), size=1, parent=o)
    add('cube', '6A4A30', (0, 1.0, 0.8), scale=(5.0, 2.0, 1.6), size=1, parent=o)
    add('cube', '7A5838', (0, 1.0, 1.63), scale=(5.3, 2.3, 0.08), size=1, parent=o)
    for i, (x, y, a) in enumerate(((-0.4, 0.9, 0.1), (0.5, 1.1, -0.2), (-1.5, 0.7, 0.3), (1.6, 0.8, 0.15))):
        add('cube', ('F6F2E8', 'EFE8D8')[i % 2], (x, y, 1.69 + 0.012 * i), rot=(0, 0, a), scale=(0.75, 1.0, 0.02), size=1, parent=o)
    add('cylinder', '2A2E36', (-2.1, 1.5, 1.72), radius=0.22, depth=0.06, vertices=8, parent=o)
    add('cylinder', '2A2E36', (-2.1, 1.5, 2.2), radius=0.035, depth=1.0, vertices=5, parent=o)
    add('cone', 'FFB060', (-2.0, 1.3, 2.7), rot=(0.5, 0, 0), radius1=0.34, radius2=0.1, depth=0.4, vertices=8, parent=o, emit=3)
    light((-2.0, 1.2, 2.5), 300, 'FFB060', kind='POINT', parent=o)
    for sh in range(4):
        add('cube', '4A3626', (-3.5, 4.9, 1.2 + sh * 1.25), scale=(7.5, 0.7, 0.1), size=1, parent=o)
        for i in range(16):
            hh = 0.75 + 0.25 * ((i * 7 + sh * 3) % 3) / 2
            add('cube', ('8A3A30', '2C5E8C', 'D8A83A', '3E6A4A', 'E8E0CC', '5A3A6A')[(i + sh * 2) % 6], (-7.0 + i * 0.45, 4.85, 1.25 + sh * 1.25 + hh / 2),
                rot=(0, 0.08 * math.sin(i * 3 + sh), 0), scale=(0.3 + 0.1 * (i % 2), 0.5, hh), size=1, parent=o)
    add('cube', 'DCEBFF', (4.6, 5.0, 3.9), scale=(3.0, 0.1, 2.6), size=1, parent=o, emit=2.5)
    add('cube', '2A2E36', (4.6, 4.92, 3.9), scale=(0.1, 0.1, 2.7), size=1, parent=o)
    add('cube', '8A2A2A', (0, 2.6, 1.0), scale=(1.5, 1.3, 0.2), size=1, parent=o)
    add('cube', '8A2A2A', (0, 3.2, 2.2), scale=(1.5, 0.2, 2.4), size=1, parent=o)
    add('cube', '6A4A30', (3.3, 0.2, 0.9), scale=(1.3, 1.3, 0.2), size=1, parent=o)
    add('cube', '6A4A30', (3.9, 0.2, 1.9), scale=(0.2, 1.3, 2.0), size=1, parent=o)
    a2 = empty((0.5, 1.2, 1.8), o)
    track(light((1.0, -3.5, 5.5), 700, 'FFE8C8', 4.0, a2, parent=o))
    track(light((4.4, 3.4, 4.0), 500, 'CFE0FF', 2.5, a2, parent=o))
    track(light((-4.5, -3.5, 2.4), 260, 'FF7A1A', 2.5, a2, parent=o))
    return {}


def extend(S):
    for name, fn in (('biv', set_biv), ('hall', set_hall), ('wadi', set_wadi), ('oasis', set_oasis), ('post', set_post), ('ward', set_ward)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    ingroup(S, 'erg', add_checkpoint)
    ns = make_sky('2A2E5A', '161A3C', '0A0C20', 'E8ECFF', (300, 620, 330), 20)
    for i in range(70):
        a, e = i * 2.399, 0.12 + 0.9 * ((i * 0.618) % 1)
        st = add('ico_sphere', 'FFFFFF', (860 * math.cos(a) * math.cos(e), 860 * math.sin(a) * math.cos(e), 30 + 700 * math.sin(e)), radius=2.2 + 1.6 * (i % 3),
                 subdivisions=1, parent=ns, emit=12)
        st.visible_shadow = st.visible_diffuse = st.visible_glossy = False
    S['skies']['night'] = ns
    S['doc'] = d = K.Rig(DOC, K.human_head('D8A888', 'B8B8B8'))
    add('cube', '20242B', (0, -0.3, 0.06), scale=(0.5, 0.04, 0.08), size=1, parent=d.head)
    S['boss'] = K.Rig(BOSS, K.human_head('E0B090', '5A4630'))
    add('cube', 'FF7A1A', (0, -0.345, 0.62), scale=(0.2, 0.03, 0.26), size=1, parent=S['boss'].body)
    S['camels'] = [make_camel(), make_camel('B89462', '98764A', '2C3E8C')]
    S['plane'] = make_plane()
    S['jeep'] = make_jeep()
    S['bot'] = make_bottle(0.12)
    S['bot2'] = add('cylinder', 'D8ECF2', (0, -0.12, -0.66), rot=(0.2, 0, 0), radius=0.085, depth=0.46, vertices=8, parent=S['man'].el[1], rough=0.15)
    S['cloth'] = add('cube', 'F4EEDF', (0, -0.06, -0.95), rot=(0.2, 0, 0.3), scale=(0.9, 0.04, 0.8), size=1, parent=S['man'].el[1])
    S['itflag'] = make_itflag()
    S['snake'] = [add('ico_sphere', ('B89A4A', '8A6E32')[i % 2], FAR, scale=(1.3, 1, 0.8), radius=0.12 if i else 0.16, subdivisions=1) for i in range(16)]
    S['rpack'] = empty(FAR)
    add('cube', 'C8402A', (0, 0, 0.5), scale=(0.9, 0.6, 1.0), size=1, parent=S['rpack'])
    add('cube', 'A83222', (0, -0.33, 0.4), scale=(0.6, 0.1, 0.5), size=1, parent=S['rpack'])
    add('cylinder', '3A6AA8', (0, 0, 1.1), rot=(0, PI / 2, 0), radius=0.17, depth=0.85, vertices=8, parent=S['rpack'])
    S['coin'] = add('cylinder', 'FFC233', FAR, radius=0.09, depth=0.02, vertices=10, emit=2.5, rough=0.3)
    S['tally'] = [add('cube', 'F6F2E8', FAR, rot=(0, 0.06 * math.sin(i * 2), 0), scale=(0.07, 0.03, 0.62), size=1, emit=0.5) for i in range(6)]
    S['root'] = empty(FAR)
    add('cylinder', '6A5238', (0, 0, 0), rot=(0, 0.3, 0), radius=0.06, depth=1.1, vertices=5, parent=S['root'])
    add('cylinder', '7A6244', (0.1, 0, -0.5), rot=(0, -0.5, 0), radius=0.035, depth=0.5, vertices=4, parent=S['root'])
    add('ico_sphere', '7A8A4A', (0.15, 0, 0.6), scale=(1, 1, 0.6), radius=0.26, subdivisions=1, parent=S['root'])
    S['drops'] = [add('ico_sphere', 'BFE8FF', FAR, scale=(1, 1, 1.5), radius=0.05, subdivisions=1, emit=4) for _ in range(4)]
    S['mag'] = empty(FAR)
    add('torus', 'C8CCD8', (0, 0, 0), major_radius=0.24, minor_radius=0.03, major_segments=12, minor_segments=5, parent=S['mag'], rough=0.2)
    add('cylinder', '4A3626', (0, -0.48, 0), rot=(PI / 2, 0, 0), radius=0.035, depth=0.48, vertices=5, parent=S['mag'])
    S['bones'] = empty(FAR)
    add('ico_sphere', 'EFE8D8', (0, -0.16, 0.03), radius=0.06, subdivisions=1, parent=S['bones'], emit=0.4)
    add('cylinder', 'EFE8D8', (0, 0, 0.02), rot=(PI / 2, 0, 0), radius=0.014, depth=0.3, vertices=4, parent=S['bones'], emit=0.4)
    for sx in (-1, 1):
        for j in range(3):
            add('cylinder', 'EFE8D8', (sx * (0.1 + j * 0.07), -0.02 + j * 0.05, 0.02), rot=(PI / 2, 0, sx * (1.2 - j * 0.3)), radius=0.01, depth=0.26 + j * 0.05, vertices=4,
                parent=S['bones'], emit=0.4)
    S['crew'] = cr = empty(FAR)
    figure(cr, (-0.9, 0.3, 0), PI + 0.2, '3A4A5A', '2A2E36', 'E0B090', '2A2E36')
    figure(cr, (1.5, 0.9, 0), PI - 0.4, '7A3A30', '3A3A44', 'C98F6A', None)
    for i in range(3):
        a = i * 2 * PI / 3
        add('cylinder', '2A2E36', (0.35 * math.cos(a), -0.4 + 0.35 * math.sin(a), 0.85), rot=(0.4 * math.sin(a), -0.4 * math.cos(a), 0), radius=0.03, depth=1.8, vertices=4,
            parent=cr)
    add('cube', '2A2E36', (0, -0.4, 1.9), scale=(0.34, 0.7, 0.36), size=1, parent=cr)
    add('cylinder', '15171C', (0, 0.05, 1.9), rot=(PI / 2, 0, 0), radius=0.13, depth=0.3, vertices=8, parent=cr)
    S['rec'] = add('ico_sphere', 'FF2A1A', (0.2, -0.76, 2.0), radius=0.045, subdivisions=1, parent=cr, emit=12)
    add('cylinder', '2A2E36', (2.0, 1.0, 3.0), rot=(0.5, 0, 0.3), radius=0.025, depth=3.2, vertices=4, parent=cr)
    add('ico_sphere', '6A6A6A', (1.75, 1.75, 4.35), scale=(1, 1, 1.7), radius=0.14, subdivisions=1, parent=cr)
    S['desk2'] = dk = empty(FAR)
    add('cube', 'FF7A1A', (0, 0, 0.6), scale=(3.4, 1.1, 1.2), size=1, parent=dk)
    add('cube', 'F4EEDF', (0, 0, 1.22), scale=(3.5, 1.2, 0.05), size=1, parent=dk)
    for i in range(3):
        add('cube', 'F6F2E8', (-0.9 + i * 0.8, 0.0, 1.26), rot=(0, 0, 0.2 * (i - 1)), scale=(0.5, 0.7, 0.02), size=1, parent=dk)
    add('cylinder', '2A2E36', (1.3, -0.1, 1.45), radius=0.03, depth=0.4, vertices=5, parent=dk)
    add('ico_sphere', '3A3F4A', (1.3, -0.1, 1.7), radius=0.09, subdivisions=1, parent=dk)
    S['spoon'] = sp = empty(FAR)
    add('cylinder', 'E8ECF2', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.022, depth=0.5, vertices=5, parent=sp, rough=0.1, emit=0.8)
    add('ico_sphere', 'E8ECF2', (0, -0.3, 0), scale=(1, 1.4, 0.3), radius=0.08, subdivisions=1, parent=sp, rough=0.1, emit=0.8)


_build0, _reset0, _finish0 = build, reset, finish


def build():
    keep = K.add, K.empty
    K.add, K.empty = add, empty
    try:
        S = _build0()
        extend(S)
    finally:
        K.add, K.empty = keep
    return S


def reset(S):
    _reset0(S)
    for who in ('doc', 'boss'):
        S[who].place(FAR)
        S[who].apply(P())
        S[who].root.scale = (1, 1, 1)
    loose = [c['root'] for c in S['camels']] + [S['plane']['root'], S['jeep']['root'], S['bot'], S['itflag'], S['rpack'], S['coin'], S['root'], S['mag'], S['bones'],
                                                S['crew'], S['desk2'], S['spoon']] + S['snake'] + S['drops']
    for o in loose:
        o.location, o.rotation_euler, o.scale = FAR, (0, 0, 0), (1, 1, 1)
    for o in S['snake']:
        o.scale = (1.3, 1, 0.8)
    for o in S['drops']:
        o.scale = (1, 1, 1.5)
    for i, o in enumerate(S['tally']):
        o.location = FAR
    for c in S['camels']:
        c['neck'].rotation_euler = (0, 0, 0)
        for l in c['legs']:
            l.rotation_euler = (0, 0, 0)
    S['rec'].scale = (1, 1, 1)
    S['hl_door'].data.energy, S['hl_fill'].data.energy, S['hl_orange'].data.energy = 1500, 260, 200
    S['hl_door'].data.color, S['hl_fill'].data.color = K.hexc('FFD9A0')[:3], K.hexc('8A9AE0')[:3]
    for g in S['glints']:
        g.scale = (0.7, 0.07, 0.01)
    S['bot2_on'], S['cloth_on'] = False, False
    S['key'].data.color = K.hexc('FFF0DC')[:3]


def finish(S, t):
    _finish0(S, t)
    S['bot2'].hide_render = not S['bot2_on']
    S['cloth'].hide_render = not S['cloth_on']


def camel(S, i, loc, yaw, t, step=1.0):
    c = S['camels'][i]
    c['root'].location, c['root'].rotation_euler = loc, (0, 0.02 * math.sin(t * 5), yaw)
    for j, l in enumerate(c['legs']):
        l.rotation_euler = (0.3 * step * math.sin(t * 5 + (0, PI, PI, 0)[j]), 0, 0)
    c['neck'].rotation_euler = (0.06 * math.sin(t * 5), 0, 0)
    return rel(loc, yaw, 0, 0.35, 3.28 + 0.05 * math.sin(t * 10))


def glitter(S, t):
    for i, g in enumerate(S['glints']):
        s = max(0.05, math.sin(t * 3.1 + i * 1.9))
        g.scale = (0.7 * s, 0.07, 0.01)


# ---------------------------------------------------------------- new shots: the race
def bivouac(S, k, t, lt):
    """Before the stage: he swings his pack on. Rook tries to lift one like it and cannot."""
    A = stage(S, 'biv', 'dawn')
    hv = ease(k * 1.6)
    S['man'].place(A(-2.6, -2.8, 0), 0.35)
    S['man'].apply(blend(P('stand', aL=(0.9, 0.3, 1.8), aR=(0.9, 0.3, 1.8), lean=0.3, head=(0.2, 0)), P('hips', head=(-0.05, -0.5), lift=0.04 * math.sin(t * 6)), hv))
    S['face']['man'] = 'happy'
    st = 0.5 + 0.5 * math.sin(t * 7)
    up = ease((k - 0.3) * 3) * (1 - ease((k - 0.75) * 5))
    S['rook'].place(A(2.7, -2.6, 0), -0.45)
    S['rook'].apply(P('stand', lean=0.75 - 0.25 * up, aL=(1.0, 0.2, 0.3), aR=(1.0, 0.2, 0.3), lL=(0.5, 0.9), lR=(0.5, 0.9), lift=-0.3 + 0.1 * up, head=(-0.5, 0.2 + 0.05 * st)))
    S['face']['rook'] = 'shocked' if up > 0.3 else 'deadpan'
    S['rpack'].location, S['rpack'].rotation_euler = A(2.35, -3.5, 0.45 * up), (0.1 * up * st, 0, -0.45)
    feathers(S, A(2.7, -2.8, 2.4), t, 3)
    for i, e in enumerate(S['extras'][:2]):
        e.place(A((-7.5, 7.2)[i], (3.5, 2.6)[i], 0), (0.5, -0.6)[i])
        e.apply(P('up', aL=(2.6, 0.4 + 0.2 * math.sin(t * 2 + i), 0.3), aR=(2.6, 0.4 - 0.2 * math.sin(t * 2 + i), 0.3)) if i == 0 else walk(t, 1.2))
    lamp(S, A, (0, -2.6, 2.0), (6, -1, 4), (-4, -9, 3.5), 1200, 800)
    cam(S, A(lerp(1.4, 0.4, k), lerp(-11.5, -10.5, k), 1.5), A(0.1, -1.5, 2.0), 30)


def kit(S, k, t, lt):
    """What every runner carries: food for six days, bottles, a flare. Rook has seen the flare."""
    A = stage(S, 'biv', 'dawn')
    g = ease(k * 1.8)
    S['hand'].place(A(lerp(-3.4, -1.9, g), -0.75, lerp(2.2, 1.62, g)), (0.0, 0.5, PI / 2))
    S['hand'].root.scale = (1.7, 1.7, 1.7)
    S['hand'].grip(lerp(0.2, 0.8, g))
    S['itflag'].location, S['itflag'].rotation_euler = A(0.95, 0.3, 1.05), (0, 0.06 * math.sin(t * 5), 0.3)
    rc = ease((k - 0.35) * 2.4) * (1 - ease((k - 0.85) * 7))
    S['rook'].place(A(1.75, 1.75, 0), 0.25)
    S['rook'].apply(P('stand', lean=0.42, aR=(1.0 + 0.45 * rc, -0.15, 0.5 - 0.2 * rc), aL=(0.2, 0.3, 0.6), head=(0.3, 0.15)))
    S['face']['rook'] = 'smirk' if rc < 0.9 else 'shocked'
    lamp(S, A, (0, 0, 1.4), (4, 2.5, 3.2), (-2.5, -4, 3.2), 900, 900)
    cam(S, A(lerp(-0.7, 0.3, k), lerp(-4.6, -4.0, k), 2.5), A(0.2, 0.3, 1.45), 36)


def checkpoint(S, k, t, lt):
    """The long stage: he takes a bottle on the run and keeps going."""
    A = stage(S, 'erg', 'day')
    y = lerp(-63, -77, k)
    grab = math.exp(-((y + 70) / 1.6) ** 2)
    S['man'].place(A(-1.6, y, 0), 0.0)
    S['man'].apply(run(t, 2.5) | (dict(aR=(1.3, 0.9 * grab + 0.15, 1.5 - 1.0 * grab)) if grab > 0.1 else {}))
    S['face']['man'] = 'calm'
    S['bot2_on'] = y < -70
    for i, e in enumerate(S['extras']):
        e.place(A((0.9, -0.6, 1.8)[i], y + (9, 17, 24)[i], 0), 0.0)
        e.apply(run(t + 0.3 * i, 2.3))
    puffs(S, A(-1.6, y + 1.2, 0), t, 8, 1.4)
    lamp(S, A, (-1.6, y, 2), (3, y + 3, 3.5), None, 800)
    cam(S, A(lerp(4.6, 3.8, k), -80.5, 1.5), A(-2.4, lerp(-68, -71, k), 2.1), 30)


# ---------------------------------------------------------------- new shots: the storm and the morning after
def storm_night(S, k, t, lt):
    """Hours later it is dark, the sand is still flying, and he is still on his feet."""
    A = stage(S, 'wild', 'night')
    sky(S, '3A3046', 0.7)
    wall(S, A(0, 30, -8), t)
    x = lerp(3.0, -1.5, k)
    S['man'].place(A(x, 0.2 * math.sin(t * 3), 0), -PI / 2 + 0.25 + 0.1 * math.sin(t * 2.2))
    S['man'].apply(trudge(t, 1.3, 0.55) | dict(aR=(1.75, -0.55, 1.9, 0.7), head=(0.45, -0.2)))
    S['face']['man'] = 'closed'
    sandblast(S, A(0, -0.8, 0.4), t, 90, (24, 10, 5.5), 70, 0.05, 1.2)
    footprints(S, A, [(x + 0.8 + i * 0.85, 0.2 * (-1) ** i, 0, PI / 2) for i in range(7)], 1.0)
    lamp(S, A, (x, 0, 2.2), (x + 4, 3, 4), (x - 3, -5.5, 3), 1500, 700)
    S['key'].data.color = K.hexc('9AB0FF')[:3]
    cam(S, A(lerp(-0.5, -1.2, k), -7.2, 1.2), A(x * 0.6, 0, 2.2), 30, 0.05 * math.sin(t * 6))


def dawn_dune(S, k, t, lt):
    """Morning. He sits up out of the sand on a dune he has never seen."""
    A = hero(stage(S, 'wild', 'dawn'))
    z = hero_z(0.5, 15)
    up = ease(k * 1.5)
    S['man'].place(A(0.5, 15, z - 0.12), 0.35)
    S['man'].apply(blend(P('sit', lean=1.05, head=(0.6, 0), aL=(0.4, 0.3, 0.4), aR=(0.4, 0.3, 0.4), lL=(1.5, 0.5), lR=(1.45, 0.9)),
                         P('sit', lean=0.2, head=(-0.1, 0.85 * math.sin(t * 2.2)), aL=(0.5, 0.5, 0.6), aR=(0.9, 0.3, 1.5), lL=(1.5, 0.5), lR=(1.3, 1.5)), up))
    S['face']['man'] = 'closed' if up < 0.5 else 'scared'
    for i in range(8):
        d = S['dust'][i]
        f = max(0.0, 1 - up * 1.4)
        d.location = A(0.5 + 0.5 * math.sin(i * 2.1), 14.4 - 0.25 * i + 0.4 * math.cos(i), z + 0.25 - 0.4 * (1 - f))
        d.scale = (0.75 * f + 0.01, 0.75 * f + 0.01, 0.4 * f + 0.01)
    lamp(S, A, (0.5, 15, z + 1.5), (-4, 17, z + 4), (4, 9, z + 2.5), 1500, 900)
    cam(S, A(lerp(4.2, 3.0, k), lerp(8.4, 9.2, k), z + lerp(0.5, 1.1, k)), A(0.2, 15, z + 1.35), 32)


def rook_buried(S, k, t, lt):
    """A hat on the sand. Then the rest of Rook comes up under it."""
    A = hero(stage(S, 'wild', 'dawn'))
    x, y = -4.0, 12.0
    z = hero_z(x, y)
    up = ease((k - 0.2) * 2.4)
    shake = math.sin(t * 22) * ease((k - 0.55) * 4) * (1 - ease((k - 0.9) * 8))
    S['rook'].place(A(x, y, z - 2.25 * (1 - up)), 0.3 + 0.12 * shake)
    S['rook'].apply(blend(P('stand', head=(0.1, 0)), P('shrug', head=(-0.05, 0.5 * shake)), up))
    S['face']['rook'] = 'deadpan' if up > 0.8 else 'shocked'
    for i in range(10):
        d = S['dust'][i]
        a = i * 0.63
        f = 1 - 0.6 * up
        d.location = A(x + 0.75 * math.cos(a), y + 0.75 * math.sin(a) - 0.1, z + 0.1)
        d.scale = (0.75 * f, 0.75 * f, 0.38 * f)
    feathers(S, A(x, y - 0.3, z + 2.4), t, 5)
    lamp(S, A, (x, y, z + 2), (x - 4, y + 2, z + 4), (x + 3, y - 6, z + 2.5), 1400, 1000)
    cam(S, A(lerp(x + 2.4, x + 1.6, k), lerp(y - 6.6, y - 5.8, k), z + 0.9), A(x, y, z + lerp(1.0, 1.9, up)), 34)


def bottles(S, k, t, lt):
    """The water is nearly gone; the spare bottle comes out. Rook pulls his hat down and looks elsewhere."""
    A = stage(S, 'wild', 'day')
    S['man'].place(A(3.4, 4.2, 0), PI - 0.75)
    S['man'].apply(P('stand', **KNEEL, lean=0.2, aR=(1.25 + 0.15 * math.sin(t * 2), 0.25, 1.5), aL=(0.4, 0.2, 0.9), head=(0.25, -0.3)))
    S['face']['man'] = 'tired'
    S['bot2_on'] = True
    S['bot'].location, S['bot'].rotation_euler, S['bot'].scale = A(1.5, -0.4, 0.0), (0, 0.05 * math.sin(t * 3), 0), (2.6, 2.6, 2.6)
    tip = ease((k - 0.2) * 3)
    S['rook'].place(A(-0.6, 2.6, 0), 0.3)
    S['rook'].apply(blend(P('stand', head=(0, 0.75)), P('hat', head=(0.2, -0.7), aL=(0.3, 0.2, 0.5)), tip))
    S['hat_tip'], S['face']['rook'] = tip, 'deadpan'
    lamp(S, A, (1, 3, 2), (5, 5, 4), (-3, -4, 3), 1000, 500)
    cam(S, A(lerp(0.2, 0.9, k), lerp(-5.4, -4.8, k), 1.3), A(1.2, 3.0, 1.7), 32)


def wait_dune(S, k, t, lt):
    """He does what the rule says: he stays put. Rook keeps him company and flips a coin."""
    A = hero(stage(S, 'wild', 'dusk'))
    z = hero_z(0, 16)
    S['man'].place(A(-1.1, 16, z - 0.1), 0.3)
    S['man'].apply(P('sit', aL=(1.25, -0.2, 0.9), aR=(1.25, -0.2, 0.9), lL=(1.9, 1.9), lR=(1.9, 1.9), head=(0.05, 0.7 * math.sin(t * 1.3)), lean=0.3))
    S['face']['man'] = 'tired'
    S['rook'].place(A(1.7, 15.7, hero_z(1.7, 15.7) - 0.1), -0.35)
    c = (t * 1.3) % 1
    S['rook'].apply(P('sit', aR=(1.0 + 0.5 * math.sin(c * PI), 0.2, 1.5), aL=(0.6, 0.0, 1.3), lL=(1.9, 1.9), lR=(1.9, 1.9), head=(-0.1 - 0.25 * math.sin(c * PI), 0.3), lean=0.25))
    S['face']['rook'] = 'deadpan'
    S['coin'].location = A(1.42, 14.95, z + 1.4 + 1.5 * math.sin(c * PI))
    S['coin'].rotation_euler = (t * 25, 0.4, 0)
    S['coin'].scale = (1.5, 1.5, 1.5)
    lamp(S, A, (0.3, 16, z + 1.6), (5, 18, z + 4), (-3, 9.5, z + 2.5), 1300, 700)
    cam(S, A(lerp(-4.6, -3.2, k), lerp(7.4, 8.2, k), z + lerp(0.4, 1.0, k)), A(0.3, 16, z + 1.5), 30)


# ---------------------------------------------------------------- new shots: the shrine
def flag_roof(S, k, t, lt):
    """He climbs onto the roof and plants a small Italian flag where a pilot might see it. Rook salutes."""
    A = stage(S, 'shrine', 'dusk')
    g = ease(k * 2)
    S['man'].place(A(2.5, 9.3, 4.85), 0.35)
    S['man'].apply(blend(P('stand', lean=0.45, aR=(1.2, 0.1, 0.4), aL=(1.0, 0.1, 0.5), head=(0.35, 0)), P('hips', head=(-0.35, 0.5 * math.sin(t * 1.6))), ease((k - 0.5) * 3)))
    S['pack_on'], S['face']['man'] = False, 'tired'
    S['itflag'].location = A(3.35, 8.85, lerp(5.6, 4.85, g))
    S['itflag'].rotation_euler, S['itflag'].scale = (0, 0.1 * math.sin(t * 7), 0.4 + 0.25 * math.sin(t * 3)), (2.4, 2.4, 2.4)
    S['rook'].place(A(5.6, 2.2, 0), PI - 0.45)
    sal = ease((k - 0.45) * 3.5)
    S['rook'].apply(blend(P('stand', head=(-0.45, 0.25)), P('hat', head=(-0.5, 0.25), aR=(0.3, 1.75, 1.9, -1.5)), sal))
    S['face']['rook'] = 'calm'
    lamp(S, A, (3, 7, 4), (9, 6, 6), (0, -3, 4), 1800, 1200)
    cam(S, A(lerp(8.2, 7.2, k), lerp(-5.5, -4.6, k), 1.1), A(2.6, 9.0, 4.6), 30)


def hall_shade(S, k, t, lt):
    """Inside: bare walls, and out of the sun for the first time in days."""
    A = stage(S, 'hall', 'hall')
    br = 0.04 * math.sin(t * 2.2)
    S['man'].place(A(-2.9, 3.55, 0.03), 0.3)
    S['man'].apply(P('sit', lean=-0.2, head=(0.5 + br, 0.35), aL=(0.25, 0.15, 0.3), aR=(0.3, 0.2, 0.5), lL=(1.5, 0.25), lR=(1.3, 0.8), lift=-0.5 + br * 0.5))
    S['pack_on'], S['face']['man'] = False, 'closed'
    S['rpack'].location, S['rpack'].rotation_euler = A(-4.3, 2.6, 0), (0, 0, 0.7)
    S['hl_door'].data.energy = 1500 + 500 * math.sin(t * 1.7)
    cam(S, A(lerp(2.6, 1.0, k), -4.4, lerp(1.2, 1.6, k)), A(-1.2, 3.0, 1.5), 30)


def hall_days(S, k, t, lt):
    """Rook keeps count of the days on the wall."""
    A = stage(S, 'hall', 'hall')
    n = min(6, int(k * 5.2) + 2)
    for i in range(n):
        S['tally'][i].location = A(1.0 + i * 0.3, 4.46, 2.5)
    x = 1.0 + (n - 1) * 0.3 + 0.75
    S['rook'].place(A(x, 3.55, 0), PI - 0.85 + 1.4 * ease((k - 0.7) * 4))
    S['rook'].apply(P('stand', aR=(1.75 + 0.2 * math.sin(t * 14), 0.5, 0.25), aL=(0.2, 0.2, 0.4), head=(0.0, -0.4)))
    S['face']['rook'] = 'sad'
    S['man'].place(A(-3.2, 3.55, 0.03), 0.4)
    S['man'].apply(P('sit', lean=-0.2, head=(0.55, 0.3), aL=(0.25, 0.15, 0.3), aR=(0.3, 0.2, 0.5), lL=(1.5, 0.25), lR=(1.3, 0.8)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'closed'
    cam(S, A(lerp(-0.9, -0.2, k), lerp(-4.0, -3.2, k), 1.9), A(1.4, 4.2, 2.2), 34)


def plane_over(S, k, t, lt):
    """An aeroplane crosses high over the shrine. He waves a cloth. It keeps its course."""
    A = stage(S, 'shrine', 'day')
    p = S['plane']
    p['root'].location = A(lerp(-34, 30, k), lerp(34, 24, k), lerp(24, 26, k))
    p['root'].rotation_euler = (0, 0.06, PI / 2 + 0.15)
    p['prop'].rotation_euler = (0, t * 40, 0)
    wv = math.sin(t * 11)
    S['man'].place(A(1.8, 4.0, 0), PI - 0.5 + 0.7 * k)
    S['man'].apply(P('up', aL=(2.6, 0.4, 0.3), aR=(2.75, 0.3 + 0.35 * wv, 0.25), head=(-0.55, 0), lift=0.06 * abs(wv)))
    S['cloth_on'], S['pack_on'], S['gaunt'] = True, False, True
    S['itflag'].location, S['itflag'].scale = A(3.35, 8.85, 4.85), (2.4, 2.4, 2.4)
    S['itflag'].rotation_euler = (0, 0.1 * math.sin(t * 7), 0.5)
    lamp(S, A, (1.8, 4, 2), (6, 2, 4), (-2, -3, 3), 1000, 600)
    cam(S, A(lerp(-2.2, -1.2, k), -3.6, 0.7), A(lerp(-1, 3, k), 14, 8.5), 24)


def hall_low(S, k, t, lt):
    """The lowest point. No jokes: he sits with his head down, and Rook stands by the door with nothing to say."""
    A = stage(S, 'hall', 'hall')
    S['hl_door'].data.energy, S['hl_fill'].data.energy, S['hl_orange'].data.energy = 240 + 60 * math.sin(t * 0.9), 520, 60
    S['hl_door'].data.color = K.hexc('8AA0E8')[:3]
    S['man'].place(A(-1.3, 1.5, 0.03), PI - 0.7)
    S['man'].apply(P('sit', lean=0.5, head=(0.75, 0), aL=(1.2, -0.2, 0.9), aR=(1.2, -0.2, 0.9), lL=(1.9, 1.9), lR=(1.9, 1.9), lift=-0.5 + 0.02 * math.sin(t * 1.8)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'closed'
    for i in range(3):
        S['tally'][i].location = A(1.0 + i * 0.3, 4.46, 2.5)
    S['rook'].place(A(3.9, -0.9, 0), face_to((3.9, -0.9), (-1.3, 1.5)) + 0.25)
    S['rook'].apply(P('stand', aR=(0.75, -0.3, 2.1, 0.9), aL=(0.1, 0.1, 0.2), head=(0.35 + 0.03 * math.sin(t * 1.5), 0.0), lean=0.08))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(1.6, 0.2, k), lerp(-4.5, -4.1, k), lerp(1.9, 1.5, k)), A(0.6, 1.2, 1.5), 32)


def hall_dawn(S, k, t, lt):
    """Morning in the doorway. He gets up and goes out."""
    A = stage(S, 'hall', 'hall')
    S['hl_door'].data.energy = lerp(900, 3200, k)
    S['hl_door'].data.color = K.hexc('FFC890')[:3]
    if S['prm'].get('in'):                      # the first evening: he comes in out of the sun, pack still on
        S['hl_door'].data.energy = 2600 + 300 * math.sin(t * 2)
        x = lerp(5.0, 2.6, ease(k))
        S['man'].place(A(x, 0.85, 0), -PI / 2)
        S['man'].apply(trudge(t, 1.0, 0.3) | dict(head=(-0.15, 0.6 * math.sin(t * 1.7))))
        S['face']['man'] = 'tired'
        cam(S, A(lerp(-3.6, -2.6, k), lerp(-3.4, -2.8, k), 1.4), A(4.6, 0.9, 2.0), 30)
        return
    x = lerp(2.2, 4.9, ease(k))
    S['man'].place(A(x, 0.85, 0), PI / 2)
    S['man'].apply(trudge(t, 1.0, 0.18) | dict(head=(0.0, 0.0)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'tired'
    for i in range(4):
        S['tally'][i].location = A(1.0 + i * 0.3, 4.46, 2.5)
    cam(S, A(lerp(-4.4, -3.2, k), lerp(-2.6, -1.8, k), 1.5), A(5.0, 0.9, 1.9), 30)


def shrine_night(S, k, t, lt):
    """Night over the shrine: stars, the flag on the roof, nobody coming."""
    A = stage(S, 'shrine', 'night')
    S['itflag'].location, S['itflag'].scale = A(3.35, 8.85, 4.85), (2.4, 2.4, 2.4)
    S['itflag'].rotation_euler = (0, 0.1 * math.sin(t * 5), 0.5 + 0.3 * math.sin(t * 2))
    lamp(S, A, (0, 8, 3), (9, 4, 6), (-6, -4, 5), 700, 500)
    S['key'].data.color = K.hexc('8AA0FF')[:3]
    cam(S, A(lerp(-7.5, -5.0, k), lerp(-13, -11.5, k), lerp(1.0, 1.6, k)), A(0, 10, 4.6), 28)


# ---------------------------------------------------------------- new shots: the walk
def wadi_shade(S, k, t, lt):
    """Midday: he lies up under a ledge. Rook fans himself."""
    A = stage(S, 'wadi', 'day')
    br = 0.04 * math.sin(t * 2.4)
    S['man'].place(A(-1.2, 5.9, 0.03), 0.25)
    S['man'].apply(P('sit', lean=-0.25, head=(0.5 + br, 0.3), aL=(0.25, 0.15, 0.3), aR=(0.3, 0.2, 0.5), lL=(1.5, 0.25), lR=(1.3, 0.8)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'closed'
    S['rook'].place(A(2.3, 4.7, 0.03), -0.5)
    S['rook'].apply(P('sit', aR=(1.5, 0.2 + 0.5 * math.sin(t * 9), 1.7), aL=(0.4, 0.2, 0.6), head=(-0.2, 0.2), lean=0.0, lL=(1.5, 0.4), lR=(1.4, 1.0)))
    S['face']['rook'] = 'sick'
    feathers(S, A(2.3, 4.2, 2.3), t, 2)
    lamp(S, A, (0.5, 5, 1.5), (6, 2, 3), (-3, -2, 2.6), 900, 1400)
    cam(S, A(lerp(1.9, 0.9, k), lerp(-5.4, -4.6, k), 1.25), A(0.6, 5.2, 1.6), 30)


def roots(S, k, t, lt):
    """A root wrung out over his mouth for a few drops."""
    A = stage(S, 'wadi', 'day')
    S['man'].place(A(-5.3, -1.0, 0), -0.55)
    S['man'].apply(P('stand', **KNEEL, lean=-0.15, head=(-0.75, 0.1), aR=(2.3, 0.3, 1.2), aL=(0.4, 0.3, 0.8)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'closed'
    sq = 0.5 + 0.5 * math.sin(t * 6)
    S['hand'].place(A(-5.6, -1.75, 3.05), (0.3, 0.2, PI / 2 + 0.6))
    S['hand'].root.scale = (1.5, 1.5, 1.5)
    S['hand'].grip(0.75 + 0.2 * sq)
    S['root'].location, S['root'].rotation_euler, S['root'].scale = A(-5.62, -1.8, 3.0), (0.2, 0.5 + 0.2 * sq, 0.4), (1.3, 1.3, 1.3)
    for i, d in enumerate(S['drops'][:3]):
        u = (t * 1.5 + i / 3) % 1
        d.location = A(-5.6, -1.82, 2.72 - 0.45 * u * u)
        d.scale = (1.2 * (1 - 0.4 * u),) * 2 + (1.9,)
    lamp(S, A, (-5.4, -1.2, 2.2), (-2, 0.5, 4), (-8, -5, 3), 900, 900)
    cam(S, A(lerp(-7.9, -7.5, k), lerp(-5.4, -4.9, k), 1.7), A(-5.4, -1.3, 2.35), 36)


def snake(S, k, t, lt):
    """A snake comes side-winding through. Rook leaves the ground."""
    A = stage(S, 'wadi', 'day')
    hx = lerp(9.2, 5.2, k)
    for i, o in enumerate(S['snake']):
        u = i * 0.2
        o.location = A(hx + u + 0.0, -3.0 + 0.32 * math.sin(t * 9 - i * 0.75), 0.1 + (0.06 if i == 0 else 0))
        o.scale = (2.0, 1.5, 1.2) if i == 0 else (1.7 - 0.05 * i, 1.3 - 0.04 * i, 1.0 - 0.03 * i)
    j = ease((k - 0.35) * 5)
    hop = abs(math.sin(max(0.0, k - 0.35) * 9)) * j
    S['rook'].place(A(4.0 - 0.9 * j, -2.4, 1.3 * hop), PI / 2 - 0.5)
    S['rook'].apply(blend(P('stand', head=(0.35, 0.3), lean=0.2), P('up', lL=(0.9, 1.5), lR=(0.6, 1.2), head=(0.3, 0.3)), j))
    S['face']['rook'] = 'shocked' if j > 0.2 else 'calm'
    S['hat_off'] = j > 0.3
    feathers(S, A(3.6, -2.6, 2.6), t, 6 if j > 0.2 else 0)
    lamp(S, A, (5, -2.6, 1.4), (9, 0, 3.4), (1, -7, 3), 1000, 700)
    cam(S, A(lerp(6.4, 5.6, k), lerp(-9.6, -9.0, k), 0.6), A(5.2, -2.7, 1.55), 32)


def oasis(S, k, t, lt):
    """The eighth day: palms, reeds, and water between them."""
    A = stage(S, 'oasis', 'dusk')
    glitter(S, t)
    y = lerp(-10.0, -3.0, k)
    d = ease((k - 0.7) * 3.4)
    S['man'].place(A(-0.8 + 0.25 * math.sin(t * 2.2), y, 0), PI + 0.1 * math.sin(t * 1.8))
    S['man'].apply(blend(trudge(t, 1.25, 0.4) | dict(aR=(1.3, 0.2, 0.4), aL=(0.9, 0.2, 0.3), head=(-0.1, 0)),
                         P('stand', **KNEEL, lean=0.4, aR=(1.4, 0.3, 0.4), aL=(1.4, 0.3, 0.4), head=(-0.2, 0)), d))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'shock'
    footprints(S, A, [(-0.8 + 0.25 * (-1) ** i, y - 0.8 - i * 0.9, 0, 0.1 * (-1) ** i) for i in range(10)])
    lamp(S, A, (-0.8, y, 2), (4, y + 3, 4), (-4, y - 6, 3), 1400, 900)
    cam(S, A(lerp(3.4, 2.2, k), lerp(-17.5, -13.5, k), lerp(1.0, 1.6, k)), A(0, 3, 2.7), 28)


def oasis_drink(S, k, t, lt):
    """He drinks. Rook, beside him, drinks out of his hands like a civilised bird."""
    A = stage(S, 'oasis', 'dusk')
    glitter(S, t)
    sip = 0.5 + 0.5 * math.sin(t * 3.2)
    S['man'].place(A(-1.5, -0.9, 0.42), PI, PI / 2 - 0.12)
    S['man'].apply(P('stand', aL=(2.5, 0.5, 0.9), aR=(2.5, 0.5, 0.9), head=(-0.55 + 0.25 * sip, 0), lL=(0.0, 0.25), lR=(-0.05, 0.1)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'closed'
    S['rook'].place(A(1.6, 0.9, 0), PI - 0.3)
    S['rook'].apply(P('stand', **KNEEL, lean=0.35 + 0.2 * sip, aL=(1.3 + 0.3 * sip, -0.2, 1.6), aR=(1.3 + 0.3 * sip, -0.2, 1.6), head=(0.2 - 0.3 * sip, 0.25)))
    S['face']['rook'] = 'warm'
    for i, d in enumerate(S['drops']):
        u = (t * 1.2 + i / 4) % 1
        d.location = A(1.45 + 0.2 * math.sin(i * 2), 1.75, 1.7 - 1.5 * u)
    lamp(S, A, (0, 1, 1.4), (5, 4, 3.4), (-4, 6, 2.6), 1200, 900)
    S['key'].data.color = K.hexc('FFE0C0')[:3]
    cam(S, A(lerp(0.9, 0.3, k), lerp(8.6, 7.6, k), lerp(0.75, 1.0, k)), A(0.1, 1.2, 1.15), 32)


# ---------------------------------------------------------------- new shots: found, and after
def caravan(S, k, t, lt):
    """By camel to the nearest village: he rides, the girl's grandmother leads. Rook's camel has opinions."""
    A = stage(S, 'camp', 'day')
    x0 = lerp(-46, -40, k)
    yy = -24
    S['elder'].place(A(x0 + 6.2, yy - 0.3, 0), PI / 2)
    S['elder'].apply(walk(t, 1.1) | dict(aL=(0.9, 0.2, 0.6)))
    S['girl'].place(A(x0 + 4.0, yy - 2.2, 0), PI / 2 + 0.2)
    S['girl'].apply(walk(t + 0.3, 1.5))
    seat = camel(S, 0, A(x0 + 1.6, yy, 0), PI / 2, t)
    S['man'].place(seat, PI / 2)
    S['man'].apply(P('sit', lean=0.5, head=(0.45, 0), aL=(0.9, 0.1, 0.7), aR=(0.9, 0.1, 0.7), lL=(1.2, 1.3), lR=(1.2, 1.3)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'tired'
    seat2 = camel(S, 1, A(x0 - 4.6, yy + 0.4, 0), PI / 2 - 0.05, t + 0.4)
    sw = math.sin(t * 5 + 0.4)
    S['rook'].place(seat2, PI / 2 - 0.5, 0, 0.12 * sw)
    S['rook'].apply(P('hat', lL=(1.2, 1.3), lR=(1.2, 1.3), lift=-0.5, lean=0.1, aL=(1.0, 0.3, 0.6), head=(0.1, 0.2 + 0.2 * sw)))
    S['face']['rook'] = 'sick'
    goat(S, 0, A(x0 - 8.5, yy - 2.0, 0), PI / 2, 0.1 * math.sin(t * 6))
    goat(S, 3, A(x0 + 8.6, yy + 1.8, 0), PI / 2 + 0.2, -0.2)
    puffs(S, A(x0 - 1, yy + 0.4, 0), t, 8, 2.5, 0.8, (-1, 0, 0))
    lamp(S, A, (x0, yy, 3), (x0 + 5, yy + 4, 6), (x0 - 4, yy - 8, 4), 1500, 1200)
    cam(S, A(x0 + lerp(2.5, 1.0, k), yy - 13.5, 1.5), A(x0 + 0.2, yy, 2.9), 30)


def village(S, k, t, lt):
    """The village: people come out to look at the man on the camel."""
    A = stage(S, 'post', 'day')
    x0 = lerp(-12, -6.5, k)
    S['elder'].place(A(x0 + 4.4, -1.2, 0), PI / 2)
    S['elder'].apply(walk(t, 1.1) | dict(aL=(0.9, 0.2, 0.6)))
    seat = camel(S, 0, A(x0, -1.0, 0), PI / 2, t)
    S['man'].place(seat, PI / 2)
    S['man'].apply(P('sit', lean=0.5, head=(0.4, 0.3 * math.sin(t * 1.2)), aL=(0.9, 0.1, 0.7), aR=(0.9, 0.1, 0.7), lL=(1.2, 1.3), lR=(1.2, 1.3)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'tired'
    S['jeep']['root'].location, S['jeep']['root'].rotation_euler = A(11.5, -3.5, 0), (0, 0, PI / 2 + 0.5)
    puffs(S, A(x0 - 2.5, -0.8, 0), t, 6, 2.0, 0.7, (-1, 0, 0))
    lamp(S, A, (x0, -1, 3), (x0 + 5, 3, 6), (x0 - 3, -9, 4), 1400, 1000)
    cam(S, A(lerp(3.5, 2.0, k), lerp(-17, -15.5, k), 1.7), A(0.5, 2.5, 3.1), 28)


def jeep(S, k, t, lt):
    """Driven to hospital. Rook rides in the back, holding on to his hat."""
    A = stage(S, 'post', 'day')
    x = lerp(-9, 5, k)
    loc, yw = A(x, -8 + 0.05 * math.sin(t * 20), 0.05 * abs(math.sin(t * 13))), PI / 2
    j = S['jeep']
    j['root'].location, j['root'].rotation_euler = loc, (0.012 * math.sin(t * 17), 0, yw)
    for wh in j['wheels']:
        wh.rotation_euler = (t * 14, 0, 0)
    S['man'].place(rel(loc, yw, -0.5, 0.25, 1.05), yw)
    S['man'].apply(P('sit', lean=-0.05, head=(0.35, 0.2 * math.sin(t * 1.4)), aL=(0.6, 0.0, 0.9), aR=(0.6, 0.0, 0.9)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'tired'
    S['rook'].place(rel(loc, yw, -0.25, 1.9, 1.35), yw - 0.5)
    S['rook'].apply(P('hat', lL=(1.4, 1.5), lR=(1.4, 1.5), lift=-0.5, lean=0.05, aL=(1.1, 0.5, 0.5), head=(0.05, 0.35 + 0.1 * math.sin(t * 9))))
    S['face']['rook'] = 'calm'
    puffs(S, rel(loc, yw, 0, 3.0, 0), t, 12, 2.4, 1.3, (-1, 0, 0))
    feathers(S, rel(loc, yw, 0, 2.8, 3.0), t, 3, 0.6)
    lamp(S, A, (x, -8, 2.2), (x + 5, -4, 5), (x - 2, -15, 3.5), 1500, 1100)
    cam(S, A(x + lerp(3.2, 2.2, k), -16.4, 1.35), A(x - 0.4, -8, 2.0), 30)


def ward(S, k, t, lt):
    """Hospital. He is alive, fifteen kilos lighter, and on a drip."""
    A = stage(S, 'ward', 'room')
    br = 0.03 * math.sin(t * 2.0)
    S['man'].place(A(0, 2.75, 1.3), 0.0)
    S['man'].apply(P('sit', lean=-0.32, head=(0.3 + br, 0.25 + 0.15 * math.sin(t * 0.9)), aL=(0.55, 0.15, 0.5), aR=(0.55, 0.15, 0.5), lL=(1.5, 0.1), lR=(1.5, 0.1)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'tired'
    tip = math.sin(PI * ease((lt - 0.3) / 1.0)) if lt > 0.3 else 0
    S['rook'].place(A(2.9, 0.4, 0), -PI / 2 + 0.7)
    S['rook'].apply(blend(P('stand', head=(0.15, 0.3)), P('hat', head=(0.3, 0.3)), tip))
    S['hat_tip'], S['face']['rook'] = tip * 0.7, 'warm'
    cam(S, A(lerp(1.6, 0.4, k), lerp(-7.4, -6.6, k), 2.5), A(0.1, 2.0, 2.3), 30)


def ward_soup(S, k, t, lt):
    """Months of soup. Rook has noticed the spoon."""
    A = stage(S, 'ward', 'room')
    sip = ease(math.sin(PI * min(1, k * 1.25)))
    S['man'].place(A(0, 2.75, 1.3), 0.0)
    S['man'].apply(P('sit', lean=-0.25, aL=(1.0 + 0.45 * sip, -0.25, 1.5 + 0.3 * sip, 0.6), aR=(1.0 + 0.45 * sip, -0.25, 1.5 + 0.3 * sip, 0.6), head=(0.25 - 0.3 * sip, 0),
                     lL=(1.5, 0.1), lR=(1.5, 0.1)))
    S['pack_on'], S['gaunt'], S['face']['man'] = False, True, 'calm'
    S['bowl'].location, S['bowl'].scale = A(0.0, 2.12 - 0.04 * sip, 2.78 + 0.4 * sip), (1.3, 1.3, 1.3)
    S['spoon'].location, S['spoon'].rotation_euler, S['spoon'].scale = A(0.95, 0.9, 2.1), (0, 0, 0.6), (1.6, 1.6, 1.6)
    rc = ease((k - 0.3) * 2.5) * (1 - ease((k - 0.8) * 6))
    S['rook'].place(A(2.35, 1.2, 0), -PI / 2 + 0.55)
    S['rook'].apply(P('stand', lean=0.4, aR=(0.9 + 0.5 * rc, -0.1, 0.6 - 0.3 * rc), aL=(0.2, 0.2, 0.5), head=(0.35, 0.1)))
    S['face']['rook'] = 'smirk'
    cam(S, A(lerp(0.2, 0.8, k), lerp(-3.6, -3.1, k), 2.9), A(0.7, 2.0, 2.45), 36)


def founder(S, k, t, lt):
    """The race's founder is not persuaded. (A stand-in figure: no likeness is intended.)"""
    A = stage(S, 'erg', 'day')
    S['desk2'].location, S['desk2'].rotation_euler = A(-9, 28.4, 0), (0, 0, 0.05)
    S['boss'].place(A(-9, 29.6, 0), 0.05)
    S['boss'].apply(P('cross', head=(0.05, 0.3 * math.sin(t * 4.5))))
    turn = ease((k - 0.55) * 3)
    S['rook'].place(A(-6.2, 26.2, 0), lerp(PI - 0.9, 0.35, turn))
    S['rook'].apply(blend(P('stand', aR=(1.2, 0.3, 1.2), aL=(0.3, 0.2, 0.5), head=(0.0, 0.3)), P('shrug', head=(0.0, -0.2)), turn))
    S['face']['rook'] = 'deadpan'
    lamp(S, A, (-7.5, 28, 2.2), (-3, 30, 4), (-10, 21, 3.5), 1100, 800)
    cam(S, A(lerp(-4.6, -5.4, k), lerp(19.6, 20.6, k), 1.5), A(-7.9, 28.6, 2.2), 32)


def film_crew(S, k, t, lt):
    """Later, a film crew goes back along his route and finds the shrine."""
    A = stage(S, 'shrine', 'day')
    S['crew'].location, S['crew'].rotation_euler = A(3.5, -3.5, 0), (0, 0, 0.25)
    S['rec'].scale = (1.6,) * 3 if (t * 1.6) % 1 < 0.55 else (0.01,) * 3
    S['itflag'].location, S['itflag'].scale = A(3.35, 8.85, 4.85), (2.4, 2.4, 2.4)
    S['itflag'].rotation_euler = (0.9, 0.2, 0.5)
    lamp(S, A, (3.5, -3, 2), (8, -1, 4), (0, -9, 3.5), 900, 600)
    cam(S, A(lerp(8.0, 6.2, k), lerp(-10.5, -9.2, k), lerp(1.4, 1.9, k)), A(1.0, 6.5, 3.6), 28)


def rook_bones(S, k, t, lt):
    """In the tower Rook finds what the film crew reported: small bones."""
    A = stage(S, 'tower', 'tower')
    S['bones'].location, S['bones'].scale, S['bones'].rotation_euler = A(0.75, -0.7, 0.03), (2.6, 2.6, 2.6), (0, 0, 0.5)
    dn = ease(k * 1.6)
    S['rook'].place(A(-0.55, 0.1, 0), -0.55)
    S['rook'].apply(P('stand', **KNEEL, lean=0.3 + 0.2 * dn, aR=(1.1, -0.1, 0.7), aL=(0.3, 0.3, 0.9), head=(0.45, -0.2)))
    S['face']['rook'] = 'calm' if k < 0.6 else 'shocked'
    S['mag'].location = A(0.55 + 0.12 * math.sin(t * 2.5), -0.9, lerp(1.4, 0.95, dn))
    S['mag'].rotation_euler, S['mag'].scale = (1.0, 0, 0.5), (1.6, 1.6, 1.6)
    for i in range(1, 4):
        bat(S, i, A(-1.8 + i * 0.9, 0.9, 6.0), yaw=0.3 * i)
    lamp(S, A, (0.2, -0.4, 1.2), (3.0, -2.5, 3.0), (-1.5, -4.5, 2.4), 520, 380)
    cam(S, A(lerp(2.2, 1.6, k), lerp(-4.9, -4.2, k), lerp(1.3, 0.95, k)), A(0.15, -0.3, 1.2), 34)


def office(S, k, t, lt):
    """A doctor who studies survival goes through the account, page by page. (A stand-in figure: no likeness is intended.)"""
    A0 = stage(S, 'ward', 'room')
    A = lambda x, y, z: A0(40 + x, y, z)
    nod = ease((k - 0.5) * 3)
    S['doc'].place(A(0, 2.6, 1.1), 0.0)
    S['doc'].apply(P('sit', lean=0.3 - 0.2 * nod, head=(0.55 - 0.5 * nod + 0.12 * nod * math.sin(t * 7), -0.3 * nod), aL=(1.2, -0.1, 0.9), aR=(1.2, -0.1, 0.9 + 0.3 * math.sin(t * 3)),
                     lL=(1.45, 1.6), lR=(1.45, 1.6)))
    S['rook'].place(A(3.3, 0.2, 1.0), -PI / 2 + 0.35)
    S['rook'].apply(P('sit', lean=0.3, aR=(1.1, 0.1, 1.3), aL=(0.7, -0.1, 1.5, 1.0), head=(0.1, 0.25 - 0.2 * nod)))
    S['face']['rook'] = 'calm' if nod < 0.5 else 'warm'
    cam(S, A(lerp(-2.4, -1.2, k), lerp(-6.4, -5.6, k), 2.4), A(1.2, 1.5, 2.1), 32)


def toe(S, k, t, lt):
    """Four years on, back in the race, and a toe ends it. Rook has a look and wishes he had not."""
    A = stage(S, 'erg', 'day')
    S['man'].place(A(5.2, -20, 0.03), 0.5)
    S['man'].apply(P('sit', lean=0.55, head=(0.6, 0.15), aR=(1.3, -0.2, 0.5), aL=(1.2, 0.1, 0.6), lL=(1.5, 0.3), lR=(1.9, 1.5)))
    S['face']['man'] = 'tired'
    w = ease((k - 0.5) * 4)
    S['rook'].place(A(3.1, -21.6, 0), PI / 2 + 0.9)
    S['rook'].apply(P('stand', **KNEEL, lean=0.45 - 0.5 * w, aR=(0.9, 0.2, 0.8), aL=(0.4, 0.3, 0.9 + 0.8 * w), head=(0.4 - 0.4 * w, -1.0 * w)))
    S['face']['rook'] = 'calm' if w < 0.4 else 'sick'
    for i, e in enumerate(S['extras']):
        e.place(A((-1.6, 0.6, -0.4)[i], lerp(-4, -34, k) + (0, 9, 17)[i], 0), 0.0)
        e.apply(run(t + 0.3 * i, 2.4))
    lamp(S, A, (4.2, -20.6, 1.6), (8, -18, 3.6), (2, -27, 3), 1000, 700)
    cam(S, A(lerp(6.8, 6.0, k), lerp(-27.5, -26.6, k), 1.0), A(3.6, -20.4, 1.55), 32)


def finish_line(S, k, t, lt):
    """He comes back again and gets to the end of it. Rook is on the line."""
    A = stage(S, 'erg', 'dusk')
    y = lerp(3.5, 13.5, k)
    S['man'].place(A(-0.8, y, 0), PI)
    S['man'].apply(run(t, 2.3, 0.1) | dict(aL=(2.8, 0.45, 0.2), aR=(2.8, 0.45, 0.2), head=(-0.3, 0)))
    S['face']['man'] = 'happy'
    for i, e in enumerate(S['extras'][:2]):
        e.place(A((2.4, -3.0)[i], y - (8, 13)[i], 0), PI)
        e.apply(run(t + 0.4 * i, 2.2))
    cl = math.sin(t * 16)
    S['rook'].place(A(3.6, 13.6, 0.5 * abs(math.sin(t * 7))), PI - 0.5)
    S['rook'].apply(P('stand', aL=(1.6, -0.25 + 0.3 * cl, 1.3), aR=(1.6, -0.25 + 0.3 * cl, 1.3), head=(-0.1, 0.4)))
    S['face']['rook'] = 'laugh'
    puffs(S, A(-0.8, y - 1.0, 0), t, 8, 1.2, 1.0, (0, -1, 0))
    lamp(S, A, (1, 12, 2.4), (6, 16, 4), (-3, 21, 3), 1400, 1100)
    cam(S, A(lerp(-0.2, 0.8, k), lerp(22.5, 21.0, k), 1.1), A(0.9, 10.5, 2.9), 28)


HOST |= {'bivouac', 'kit', 'rook_buried', 'bottles', 'wait_dune', 'flag_roof', 'hall_days', 'hall_low', 'wadi_shade', 'snake', 'oasis_drink', 'caravan', 'jeep',
         'ward', 'ward_soup', 'founder', 'rook_bones', 'office', 'toe', 'finish_line'}
SHOTS3D.update({f.__name__: f for f in (
    bivouac, kit, checkpoint, storm_night, dawn_dune, rook_buried, bottles, wait_dune, flag_roof, hall_shade, hall_days, plane_over, hall_low, hall_dawn,
    shrine_night,
    wadi_shade, roots, snake, oasis, oasis_drink, caravan, village, jeep, ward, ward_soup, founder, film_crew, rook_bones, office, toe, finish_line)})


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: the thin, bearded runner coming over a dune at sunset; Rook beside him, hat in the air."""
    A = hero(stage(S, 'wild', 'dusk'))
    z = hero_z(0, 16)
    S['man'].place(A(-2.6, 16.4, hero_z(-2.6, 16.4)), 0.2, 0, 0.05)
    S['man'].apply(trudge(0.3, 1.0, 0.3) | dict(aR=(1.3, 0.3, 0.5), head=(0.1, 0.1)))
    S['gaunt'], S['pack_on'], S['face']['man'] = True, False, 'tired'
    S['rook'].place(A(0.3, 14.6, hero_z(0.3, 14.6)), -0.55)
    S['rook'].apply(P('shrug', head=(-0.05, 0.6), lean=-0.1))
    S['face']['rook'], S['hat_off'] = 'shocked', True
    feathers(S, A(0.3, 14.2, z + 2.6), 1.0, 5)
    footprints(S, A, [(-2.6 + 0.22 * (-1) ** i, 17.2 + i * 0.9, hero_z(-2.6, 17.2 + i * 0.9), 0.0) for i in range(6)])
    lamp(S, A, (-1, 15.5, z + 2), (4, 18, z + 4), (-4, 9, z + 2.5), 1800, 1500)
    cam(S, A(2.2, 8.2, z + 0.9), A(1.6, 15.5, z + 1.9), 34)


STILLS['thumb'] = photo_thumb
