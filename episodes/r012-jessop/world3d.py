"""Case 012 in 3D - Violet Jessop, the stewardess who was aboard the Olympic when it collided with a warship (1911),
the Titanic when it sank (1912) and the hospital ship Britannic when it struck a mine (1916).

Built for this story only: one four-funnel liner (re-dressed per ship: dark hull by day, lit by night, white with a
green band as a hospital ship), a grey warship, open lifeboats, a moving faceted sea, a harbour quay with a shed and
a gangway, an ice field under stars, an island coast, a grey shoreline and a small crew cabin.

The ships and places are generic low-poly reconstructions, not models of the real vessels or ports. No company flag,
house badge, name plate or emblem is shown anywhere (the hospital ship carries only its green band)."""
import math

import bpy
import numpy as np
from mathutils import Euler, Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(quay=(0, 0, 0), ice=(3000, 0, 0), isle=(6000, 0, 0), shore=(9000, 0, 0), cabin=(12000, 0, 0), deep=(15000, 0, 0))
FAR = (0, 0, -2000)
HOST = {'props_pull', 'boat_pov', 'vi_jump', 'rook_deck', 'rook_quay', 'rook_gangway', 'vi_tray', 'deck_jolt', 'vi_berth', 'boat_lower', 'baby', 'tit_sink',
        'vi_brush', 'rook_brush', 'vi_rescued', 'rook_shock', 'rook_wrong', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'E8BE9C'
DRESS = '27304A'
VI = dict(top=DRESS, pants=DRESS, hand=SKIN, boot='17171C')
CREW = dict(top='1C2434', pants='1C2434', hand='D8A888', boot='121216')
LL, BB, DD, TT = 260.0, 28.0, 16.0, 9.0                    # the liner: length, beam, deck height, draught
BOATDECK = 25.0
_MOV = []


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def at(name, x, y, z):
    o = ORG[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def group(name, fn):
    """Build one backdrop under its own origin and collection, so only one renders per shot."""
    old = set(bpy.data.objects)
    out = fn(empty(ORG[name]))
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for o in set(bpy.data.objects) - old:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        coll.objects.link(o)
    return coll, out


def own_mat(name, col, rough=0.6, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = rough
    tint(m, col, emit)
    return m


def tint(m, col, emit=0.0):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)
    b.inputs['Emission Color'].default_value = K.hexc(col)
    b.inputs['Emission Strength'].default_value = emit


def use(o, m):
    o.data.materials[0] = m
    return o


def mov(o):
    """Register a prop that shots move, so reset() can put it back exactly as it was built."""
    _MOV.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def rnd(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def vis(objs, on):
    for o in objs:
        o.hide_render = not on


def seg(o, a, b, w):
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w, w, max(0.01, d.length))


# ---------------------------------------------------------------- hulls
def half_beam(s, B, fine=0.2):
    if s < fine:
        return max(0.04 * B, B / 2 * (s / fine) ** 0.55)
    if s > 0.82:
        return B / 2 * (1 - 0.6 * ((s - 0.82) / 0.18) ** 2)
    return B / 2


def hull(L, B, D, T, mats, parent, n=30, counter=True):
    """A ship's hull as one faceted mesh, bow toward -Y. mats = (topsides, bottom, deck)."""
    vs, fs, mi = [], [], []
    for i in range(n + 1):
        s = i / n
        b = half_beam(s, B)
        k = -T
        if counter and s > 0.88:
            k = -T + (T + D * 0.45) * ((s - 0.88) / 0.12) ** 1.2
        zm = max(0.0, k + (D - k) * 0.35)
        zl = k + (zm - k) * 0.25
        y = -L / 2 + L * s
        vs += [(-b, y, D), (-b, y, zm), (-0.7 * b, y, zl), (0, y, k), (0.7 * b, y, zl), (b, y, zm), (b, y, D)]
    for i in range(n):
        a, c = i * 7, (i + 1) * 7
        for j in range(6):
            fs.append((a + j, a + j + 1, c + j + 1, c + j))
            mi.append(0 if j in (0, 5) else 1)
        fs.append((a, c, c + 6, a + 6))
        mi.append(2)
    fs.append(tuple(range(7)))
    mi.append(0)
    fs.append(tuple(range(n * 7, n * 7 + 7)))
    mi.append(0)
    me = bpy.data.meshes.new('hull')
    me.from_pydata(vs, [], fs)
    for m in mats:
        me.materials.append(m)
    for p, j in zip(me.polygons, mi):
        p.material_index = j
    me.update()
    o = bpy.data.objects.new('hull', me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    return o


def make_prop(parent, loc, r=5.0):
    h = empty(loc, parent)
    add('cone', '8A6A2A', (0, 0.9, 0), rot=(-PI / 2, 0, 0), radius1=0.9, radius2=0.2, depth=2.4, vertices=6, parent=h, rough=0.3)
    for i in range(3):
        a = i * 2 * PI / 3
        add('cube', 'C89A3A', (math.sin(a) * r * 0.55, 0, math.cos(a) * r * 0.55), rot=(0, a, 0.5), scale=(r * 0.5, 0.3, r * 0.9), size=1,
            parent=h, rough=0.25, emit=0.25)
    return h


def make_liner():
    """A four-funnel liner of no particular company. Bow toward -Y, waterline at z = 0."""
    t = empty(FAR)
    hm, wm, fm = own_mat('linerhull', '17191E', 0.7), own_mat('linerwin', '20262E', 0.4), own_mat('linertop', '15161A', 0.8)
    hull(LL, BB, DD, TT, (hm, K.mat('6A2A24'), K.mat('B8A680')), t)
    white, wood = 'E4E0D4', 'B8A680'
    add('cube', white, (0, 8, 18.25), scale=(25, 140, 4.5), size=1, parent=t)                 # two decks of cabins
    add('cube', white, (0, 7.5, 22.75), scale=(23, 125, 4.5), size=1, parent=t)
    add('cube', wood, (0, 7.5, BOATDECK - 0.04), scale=(23.2, 125.2, 0.1), size=1, parent=t)   # the boat deck
    add('cube', white, (0, 6, 27.0), scale=(9, 112, 4.0), size=1, parent=t)                   # deckhouse
    add('cube', 'CFCABC', (0, 6, 29.1), scale=(9.6, 112.6, 0.2), size=1, parent=t)
    add('cube', white, (0, -54, 27.0), scale=(24, 7, 4.0), size=1, parent=t)                  # the bridge
    use(add('cube', '20262E', (0, -57.55, 27.6), scale=(22, 0.1, 1.3), size=1, parent=t), wm)
    add('cube', white, (0, -105, 17.4), scale=(15, 36, 2.8), size=1, parent=t)                # forecastle
    add('cube', white, (0, 108, 17.2), scale=(17, 26, 2.4), size=1, parent=t)                 # poop
    tops = []
    for i in range(4):
        y = -38 + i * 32
        add('cylinder', 'D8A040', (0, y + 1.1, 38), rot=(-0.12, 0, 0), scale=(1, 1.25, 1), radius=3.5, depth=19, vertices=10, parent=t)
        tops.append(use(add('cylinder', '15161A', (0, y + 2.3, 46.6), rot=(-0.12, 0, 0), scale=(1, 1.25, 1), radius=3.56, depth=4.2, vertices=10,
                            parent=t), fm))
    for y, hgt in ((-96, 46), (96, 40)):
        add('cylinder', '8A6A4A', (0, y + 2.5, 16 + hgt / 2), rot=(-0.1, 0, 0), radius=0.45, depth=hgt, vertices=5, parent=t)
    wins = []
    for sx in (-1, 1):
        for i in range(30):
            wins.append(add('cube', '20262E', (sx * 12.53, -57 + i * 4.5, 18.5), scale=(0.1, 1.7, 1.2), size=1, parent=t))
        for i in range(27):
            wins.append(add('cube', '20262E', (sx * 11.53, -51 + i * 4.5, 23.0), scale=(0.1, 1.7, 1.2), size=1, parent=t))
        for i in range(17):
            wins.append(add('cube', '20262E', (sx * 4.53, -46 + i * 6.5, 27.3), scale=(0.1, 2.2, 1.3), size=1, parent=t))
        for i in range(42):
            y = -102 + i * 5
            wins.append(add('cube', '20262E', (sx * (half_beam((y + LL / 2) / LL, BB) + 0.02), y, 11.2), scale=(0.1, 0.9, 0.9), size=1, parent=t))
        for i in range(25):                                                                  # boat deck rail
            add('cube', white, (sx * 11.45, -52 + i * 5, 25.65), scale=(0.1, 0.1, 1.3), size=1, parent=t)
        add('cube', '6A4A2E', (sx * 11.45, 8, 26.32), scale=(0.16, 122, 0.1), size=1, parent=t)
        for y in (-44, -2, 12, 26, 40, 54):                                                  # boats on their davits
            add('ico_sphere', 'ECE8DC', (sx * 10.2, y, 26.6), scale=(1.15, 4.3, 0.95), radius=1.0, subdivisions=1, parent=t)
            add('cube', '9A7A52', (sx * 10.2, y, 27.55), scale=(2.1, 8.2, 0.1), size=1, parent=t)
            for dy in (-4.4, 4.4):
                add('cube', '3A3A40', (sx * 11.1, y + dy, 26.9), rot=(0, sx * 0.25, 0), scale=(0.16, 0.16, 3.8), size=1, parent=t)
        for dy in (-24.5, -15.5):                                                            # the empty davits where the story happens
            add('cube', '3A3A40', (sx * 11.9, dy, 27.0), rot=(0, sx * 0.45, 0), scale=(0.18, 0.18, 4.4), size=1, parent=t)
    for w in wins:
        use(w, wm)
    stripe = [add('cube', '2E7A4A', (sx * 14.06, 5, 12.8), scale=(0.1, 176, 1.5), size=1, parent=t) for sx in (-1, 1)]
    props = [make_prop(t, (0, 110, -5.8), 5.4), make_prop(t, (-8.6, 103, -4.6), 6.6), make_prop(t, (8.6, 103, -4.6), 6.6)]
    add('cube', '6A2A24', (0, 117.5, -2.4), scale=(0.5, 5.0, 8.5), size=1, parent=t)          # rudder
    for sx in (-1, 1):
        add('cube', '6A2A24', (sx * 4.6, 100, -4.6), rot=(0, sx * 0.5, 0), scale=(6.5, 1.0, 0.8), size=1, parent=t)   # shaft brackets
    gash = [add('ico_sphere', '08090C', (12.6, 84 + i * 3.0, 9.0 + (i % 2) * 2.2), rot=(i, i * 2, 0), scale=(0.5, 2.6, 2.6 + i % 2), radius=1.0,
                subdivisions=1, parent=t) for i in range(3)]
    gash += [add('cube', ('A8AEB6', '8A9098')[i % 2], (13.6 + 0.5 * (i % 2), 81 + i * 2.6, 6.5 + (i * 37 % 7)), rot=(i * 0.9, 0.5 + i * 0.4, i * 0.7),
                 scale=(0.2, 2.4, 1.6), size=1, parent=t) for i in range(6)]
    return dict(liner=mov(t), hullm=hm, winm=wm, funm=fm, stripe=stripe, props=props, gash=gash)


def make_warship():
    """A grey cruiser of the period, generic. Bow toward -Y."""
    t = empty(FAR)
    g = K.mat('6C7884')
    hull(120, 15, 6.5, 5, (g, K.mat('5A2A26'), K.mat('8A8474')), t, n=18)
    add('cube', '788490', (0, -6, 8.4), scale=(9, 44, 3.8), size=1, parent=t)
    add('cube', '86929E', (0, -22, 11.6), scale=(7, 8, 3.2), size=1, parent=t)
    for y in (-10, 2, 14):
        add('cylinder', '5E6872', (0, y, 14.5), radius=1.7, depth=10, vertices=8, parent=t)
    for y, hgt in ((-30, 26), (28, 22)):
        add('cylinder', '4A525A', (0, y, 6.5 + hgt / 2), radius=0.3, depth=hgt, vertices=5, parent=t)
        add('cylinder', '4A525A', (0, y, 6.5 + hgt * 0.7), radius=1.3, depth=0.8, vertices=6, parent=t)
    for y, s in ((-42, 1), (40, -1)):
        add('cylinder', '5E6872', (0, y, 7.6), radius=2.6, depth=2.2, vertices=8, parent=t)
        add('cylinder', '4A525A', (0, y - s * 4.5, 7.9), rot=(PI / 2, 0, 0), radius=0.4, depth=8, vertices=6, parent=t)
    for sx in (-1, 1):
        for y in (-18, 8, 26):
            add('cylinder', '4A525A', (sx * 6.4, y, 6.9), rot=(0, PI / 2, 0), radius=0.3, depth=4, vertices=5, parent=t)
    return mov(t)


def make_boat():
    """An open ship's lifeboat, double-ended, about 10 long. Oars shipped along the thwarts."""
    t = empty(FAR)
    n, L, B = 8, 10.0, 3.5
    vs, fs = [], []
    for i in range(n + 1):
        s = i / n
        b = max(0.06, B / 2 * math.sin(PI * s) ** 0.55)
        k = 0.1 + 1.0 * abs(2 * s - 1) ** 3
        top = 1.35 + 0.35 * abs(2 * s - 1) ** 2
        y = -L / 2 + L * s
        vs += [(-b, y, top), (-0.72 * b, y, k + 0.35), (0, y, k), (0.72 * b, y, k + 0.35), (b, y, top)]
    for i in range(n):
        a, c = i * 5, (i + 1) * 5
        for j in range(4):
            fs.append((a + j, a + j + 1, c + j + 1, c + j))
    me = bpy.data.meshes.new('boat')
    me.from_pydata(vs, [], fs)
    me.materials.append(K.mat('ECE8DC'))
    me.update()
    o = bpy.data.objects.new('boat', me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = t
    add('cube', '9A7A52', (0, 0, 0.5), scale=(2.1, 5.6, 0.12), size=1, parent=t)              # bottom boards
    for y in (-2.8, 0, 2.8):
        add('cube', 'A88458', (0, y, 0.98), scale=(3.1, 0.7, 0.12), size=1, parent=t)         # thwarts
    for sx in (-1, 1):
        add('cube', '7A5A3A', (sx * 1.72, 0, 1.38), scale=(0.14, 7.0, 0.14), size=1, parent=t)
        add('cylinder', 'C8A878', (sx * 0.95, 0.4, 1.12), rot=(PI / 2, 0, 0), radius=0.07, depth=6.6, vertices=5, parent=t)
    return mov(t)


# ---------------------------------------------------------------- backdrops
def set_quay(r):
    stone, dark = '6A6E76', '4A4E58'
    add('cube', stone, (58, 0, 2.0), scale=(84, 520, 8.0), size=1, parent=r)                   # the quay, top at z = 6
    add('cube', dark, (16.6, 0, 5.7), scale=(1.4, 520, 0.9), size=1, parent=r)
    for i in range(34):
        add('cube', '5C606A', (40, -250 + i * 15, 6.02), scale=(46, 0.18, 0.04), size=1, parent=r)   # paving joints
    for i in range(12):                                                                     # bollards
        add('cylinder', '25272C', (19.2, -160 + i * 28, 6.7), radius=0.7, depth=1.4, vertices=8, parent=r)
        add('cylinder', '25272C', (19.2, -160 + i * 28, 7.5), radius=0.95, depth=0.3, vertices=8, parent=r)
    shed = empty((62, 0, 6), r)                                                             # the long transit shed
    add('cube', '7A4A3A', (0, 0, 9), scale=(24, 420, 18), size=1, parent=shed)
    add('cube', '4E3A36', (0, 0, 19.5), rot=(0, 0.35, 0), scale=(14, 424, 0.6), size=1, parent=shed)
    add('cube', '463430', (-6.4, 0, 19.5), rot=(0, -0.35, 0), scale=(14, 424, 0.6), size=1, parent=shed)
    for i in range(14):
        y = -195 + i * 30
        add('cube', '3A2E2C', (-12.05, y, 5.2), scale=(0.2, 11, 10.4), size=1, parent=shed)    # sliding doors
        add('cube', 'FFC070', (-12.1, y + 9.5, 13.5), scale=(0.12, 3.2, 2.2), size=1, parent=shed, emit=3.5)
    lamps = []
    for i in range(7):                                                                      # lamp standards
        y = -150 + i * 50
        add('cylinder', '25272C', (23, y, 11), radius=0.22, depth=10, vertices=6, parent=r)
        add('cube', '25272C', (22.2, y, 15.9), scale=(2.0, 0.2, 0.2), size=1, parent=r)
        add('ico_sphere', 'FFD9A0', (21.4, y, 15.5), radius=0.5, subdivisions=1, parent=r, emit=14.0)
        lamps.append(light((21.4, y, 15.0), 5200, 'FFB868', kind='POINT', parent=r))
    for i in range(16):                                                                     # crates, trunks and barrels
        x, y = 30 + rnd(i, 1) * 15, -90 + rnd(i, 2) * 150
        if 22 < x < 44 and -62 < y < 2:
            continue
        s = 1.6 + rnd(i, 3) * 1.6
        if i % 4 == 0:
            add('cylinder', '6A4A2E', (x, y, 6 + s * 0.7), radius=s * 0.5, depth=s * 1.4, vertices=8, parent=r)
        else:
            add('cube', ('8A6A44', '6E5236', '9A7A4E')[i % 3], (x, y, 6 + s / 2), rot=(0, 0, rnd(i, 4)), scale=(s * 1.3, s, s), size=1, parent=r)
    add('cube', '8A6A44', (27.5, -33.5, 7.0), rot=(0, 0, 0.3), scale=(2.6, 1.8, 2.0), size=1, parent=r)   # the crate with the key
    gw = empty((0, -20, 0), r)                                                              # gangway up to the ship's side
    add('cube', '8A7A5A', (20.2, 0, 11.2), rot=(0, 0.72, 0), scale=(15.4, 3.0, 0.25), size=1, parent=gw)
    for sy in (-1, 1):
        add('cube', 'D8D4C8', (20.2, sy * 1.5, 12.6), rot=(0, 0.72, 0), scale=(15.4, 0.12, 0.12), size=1, parent=gw)
        for j in range(6):
            u = j / 5
            add('cube', 'D8D4C8', (26 - u * 11.6, sy * 1.5, 6.9 + u * 10.0), scale=(0.12, 0.12, 1.6), size=1, parent=gw)
    add('cube', '0E1418', (-300, 0, -0.6), scale=(640, 2000, 0.2), size=1, parent=r)          # far harbour water is the sea grid; this is the bed
    for i in range(9):                                                                      # the far side of the dock: sheds and cranes
        y = -420 + i * 105
        add('cube', ('2A3440', '323C4A')[i % 2], (-330, y, 14 + rnd(i, 5) * 8), scale=(60, 90, 28 + rnd(i, 5) * 16), size=1, parent=r)
        add('cube', '222A34', (-290, y + 30, 40), scale=(2.5, 2.5, 80), size=1, parent=r)
        add('cube', '222A34', (-275, y + 30, 78), rot=(0, -0.35, 0), scale=(46, 2, 2), size=1, parent=r)
    return dict(quay_lamps=lamps)


def set_ice(r):
    def berg(x, y, s, seed):
        for j in range(5):
            a, d = rnd(seed, j) * 2 * PI, s * (0.0 if j == 0 else 0.55 + 0.3 * rnd(seed, j + 9))
            hgt = s * (1.6 if j == 0 else 0.5 + 0.8 * rnd(seed, j + 4))
            add('cone', ('DCEBF4', 'C2DAEA', 'EAF4FA')[j % 3], (x + math.cos(a) * d, y + math.sin(a) * d, hgt / 2 - 1.5), rot=(0, 0, rnd(seed, j + 2) * 3),
                radius1=s * (1.0 if j == 0 else 0.6), radius2=s * 0.08, depth=hgt, vertices=5 + j % 3, parent=r, rough=0.35)
    berg(34, -214, 21, 1)                                                                   # the one in the way
    berg(-210, -420, 30, 2)
    berg(260, -90, 24, 3)
    berg(-320, 120, 34, 4)
    berg(170, 330, 26, 5)
    for i in range(26):                                                                     # growlers and floes
        x, y = (rnd(i, 1) - 0.5) * 700, (rnd(i, 2) - 0.5) * 900
        if abs(x) < 40:
            x += 80
        add('ico_sphere', ('DCEBF4', 'C2DAEA')[i % 2], (x, y, 0.1), scale=(1.5, 1.2, 0.35), radius=2 + rnd(i, 3) * 4, subdivisions=1, parent=r, rough=0.4)
    for i in range(110):                                                                    # stars
        a, e = rnd(i, 11) * 2 * PI, 0.08 + rnd(i, 12) * 1.2
        d = 2600
        add('ico_sphere', 'FFFFFF', (math.cos(a) * math.cos(e) * d, math.sin(a) * math.cos(e) * d, math.sin(e) * d), radius=4 + rnd(i, 13) * 7,
            subdivisions=1, parent=r, emit=6.0 + rnd(i, 14) * 10)
    return {}


def set_isle(r):
    for i in range(16):                                                                     # dry Aegean islands on the horizon
        a = i / 16 * 2 * PI + 0.2
        d = 900 + rnd(i, 1) * 500
        hgt = 60 + rnd(i, 2) * 130
        x, y = math.cos(a) * d, math.sin(a) * d
        for j in range(3):
            add('cone', ('B8A47A', 'A89468', '8E8A5C', 'C4B48A')[(i + j) % 4], (x + (j - 1) * 150 * (0.6 + rnd(i, j)), y + rnd(i, j + 3) * 90, hgt * (0.5 - j * 0.07) - 2),
                radius1=190 + rnd(i, j + 5) * 120, radius2=14, depth=hgt * (1 - j * 0.14), vertices=7, parent=r)
        if i % 3 == 0:
            for j in range(5):
                add('cube', 'F2EEE2', (x * 0.86 + j * 9, y * 0.86 + rnd(i, j + 8) * 20, 4 + j % 2 * 3), scale=(7, 7, 6), size=1, parent=r)
    return {}


def set_shore(r):
    for i in range(22):                                                                     # a low wooded shore and a harbour mouth
        x = -1100 + i * 100
        add('cube', ('4A5A52', '546258', '40504A')[i % 3], (x, 760 + rnd(i, 1) * 60, 9 + rnd(i, 2) * 10), scale=(120, 80, 22 + rnd(i, 2) * 22), size=1, parent=r)
        add('cube', ('4E5C58', '46544E')[i % 2], (-760 - rnd(i, 3) * 60, x * 0.7, 8 + rnd(i, 4) * 8), scale=(80, 110, 18 + rnd(i, 4) * 18), size=1, parent=r)
    for i in range(3):                                                                      # round sea forts
        add('cylinder', '6A6E72', (-380 + i * 330, 560 - i * 60, 9), radius=22, depth=22, vertices=10, parent=r)
        add('cylinder', '5A5E62', (-380 + i * 330, 560 - i * 60, 21), radius=8, depth=6, vertices=8, parent=r)
    return {}


def set_cabin(r):
    wall, trim, floor = 'DCD6C2', '6A4A32', '36584E'
    add('cube', floor, (0, 5, -0.1), scale=(10, 12, 0.2), size=1, parent=r)
    add('cube', 'CFC8B4', (0, 5, 7.7), scale=(10, 12, 0.2), size=1, parent=r)
    add('cube', wall, (-5, 5, 3.8), scale=(0.2, 12, 7.8), size=1, parent=r)
    add('cube', wall, (5, 5, 3.8), scale=(0.2, 12, 7.8), size=1, parent=r)
    add('cube', wall, (0, -1, 3.8), scale=(10, 0.2, 7.8), size=1, parent=r)
    for x, w_ in ((-3.1, 3.8), (3.1, 3.8)):                                                 # back wall around the porthole
        add('cube', wall, (x, 11, 3.8), scale=(w_, 0.2, 7.8), size=1, parent=r)
    add('cube', wall, (0, 11, 1.7), scale=(2.4, 0.2, 3.4), size=1, parent=r)
    add('cube', wall, (0, 11, 6.75), scale=(2.4, 0.2, 1.9), size=1, parent=r)
    panem = own_mat('porthole', '2A3A5A', 1.0)
    use(add('cylinder', '2A3A5A', (0, 11.25, 4.6), rot=(PI / 2, 0, 0), radius=1.75, depth=0.06, vertices=12, parent=r), panem)
    add('torus', 'C89A3A', (0, 10.86, 4.6), rot=(PI / 2, 0, 0), major_radius=1.2, minor_radius=0.14, major_segments=12, minor_segments=5, parent=r, rough=0.3)
    for i in range(1, 6):                                                                   # tongue-and-groove lines
        for sx in (-1, 1):
            add('cube', 'C4BEAA', (sx * 4.88, 5, i * 1.3), scale=(0.03, 12, 0.05), size=1, parent=r)
    for z in (0.25, 7.45):
        add('cube', trim, (0, 10.86, z), scale=(10, 0.1, 0.4), size=1, parent=r)
        for sx in (-1, 1):
            add('cube', trim, (sx * 4.86, 5, z), scale=(0.1, 12, 0.4), size=1, parent=r)
    bk = empty((-3.6, 6.2, 0), r)                                                           # two bunks against the left wall
    for z in (1.5, 4.7):
        add('cube', trim, (0, 0, z), scale=(2.7, 8.6, 0.3), size=1, parent=bk)
        add('cube', 'ECE6D6', (0, 0, z + 0.32), scale=(2.4, 8.2, 0.36), size=1, parent=bk)
        add('cube', 'B8402E', (0, -1.0, z + 0.55), scale=(2.44, 5.6, 0.14), size=1, parent=bk)
        add('cube', 'F6F2E8', (0, 3.3, z + 0.66), scale=(1.9, 1.3, 0.3), size=1, parent=bk)
        add('cube', trim, (1.3, 0, z + 0.5), scale=(0.12, 8.6, 0.7), size=1, parent=bk)
    for y in (-4.25, 4.25):
        add('cube', trim, (1.3, y, 3.4), scale=(0.2, 0.2, 6.8), size=1, parent=bk)
    ws = empty((3.6, 9.6, 0), r)                                                            # washstand, basin, mirror, shelf
    add('cube', trim, (0, 0, 1.4), scale=(2.4, 2.2, 2.8), size=1, parent=ws)
    add('cube', 'F2F0EA', (0, -0.1, 2.9), scale=(2.6, 2.3, 0.22), size=1, parent=ws, rough=0.25)
    add('cylinder', 'D8DCE0', (-0.35, -0.2, 3.02), radius=0.7, depth=0.1, vertices=10, parent=ws, rough=0.2)
    add('cube', 'A8C4D0', (0, 1.28, 5.1), scale=(1.8, 0.05, 2.2), size=1, parent=ws, rough=0.12)
    add('cube', trim, (0, 1.3, 5.1), scale=(2.05, 0.04, 2.45), size=1, parent=ws)
    add('cylinder', 'CFE4EA', (0.85, -0.55, 3.3), radius=0.2, depth=0.56, vertices=8, parent=ws, rough=0.1, alpha=0.5)   # the tumbler
    add('torus', 'F4FAFC', (0.85, -0.55, 3.58), major_radius=0.2, minor_radius=0.025, major_segments=8, minor_segments=3, parent=ws, emit=0.5)
    add('cube', trim, (3.4, 3.0, 0.9), scale=(1.5, 1.5, 0.14), size=1, parent=r)              # a chair
    add('cube', trim, (4.1, 3.0, 2.2), scale=(0.14, 1.5, 2.6), size=1, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cube', '4A3222', (3.4 + sx * 0.62, 3.0 + sy * 0.62, 0.45), scale=(0.14, 0.14, 0.9), size=1, parent=r)
    add('cube', trim, (4.86, 0.9, 3.2), scale=(0.1, 2.6, 6.4), size=1, parent=r)              # the door frame, on the right
    add('cube', '2A2A30', (4.9, 0.9, 3.1), scale=(0.12, 2.2, 6.0), size=1, parent=r)
    add('cube', '9A2E2A', (0.4, 4.2, 0.02), scale=(3.6, 5.0, 0.05), size=1, parent=r)         # a rug
    lampm = own_mat('cabinlamp', 'FFE2B0', 9.0)
    sw = mov(empty((0.3, 4.5, 7.6), r))                                                     # the ceiling lamp swings from here
    add('cylinder', '8A6A2A', (0, 0, -0.5), radius=0.04, depth=1.0, vertices=4, parent=sw)
    use(add('cone', 'FFE2B0', (0, 0, -1.2), radius1=0.55, radius2=0.2, depth=0.5, vertices=8, parent=sw), lampm)
    lamp = light((0, 0, -1.5), 900, 'FFD9A8', kind='POINT', parent=sw)
    day = light((0, 10.6, 4.6), 0, 'DCEBFF', 2.2, parent=r)
    day.rotation_euler = (-PI / 2, 0, 0)
    return dict(cab_lamp=lamp, cab_swing=sw, cab_lampm=lampm, cab_pane=panem, cab_day=day)


# ---------------------------------------------------------------- cast
def vi_head(head):
    """Violet: auburn hair pinned up under a white stewardess cap."""
    add('ico_sphere', SKIN, (0, 0, 0.02), scale=(0.9, 1, 1.08), radius=0.29, subdivisions=1, parent=head)
    add('ico_sphere', '7A3A1E', (0, 0.06, 0.09), scale=(1.0, 1.02, 1.0), radius=0.3, subdivisions=1, parent=head)
    add('ico_sphere', '7A3A1E', (0, 0.3, 0.16), radius=0.17, subdivisions=1, parent=head)       # the bun
    cap = [add('cylinder', 'F6F4EC', (0, 0.0, 0.33), rot=(-0.25, 0, 0), radius=0.25, depth=0.12, vertices=8, parent=head),
           add('cube', 'F6F4EC', (0, -0.2, 0.3), rot=(-0.5, 0, 0), scale=(0.46, 0.05, 0.16), size=1, parent=head)]
    band = [add('cylinder', 'F4F2EA', (0, 0.02, 0.17), rot=(0.12, 0, 0), radius=0.315, depth=0.15, vertices=8, parent=head)]
    eyes = []
    for s in (-1, 1):
        eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
        add('cube', '1A2A3A', (s * 0.105, -0.28, 0.035), scale=(0.042, 0.02, 0.048), size=1, parent=head)
        add('cube', '5A2A16', (s * 0.105, -0.27, 0.125), rot=(0, s * 0.1, 0), scale=(0.12, 0.03, 0.022), size=1, parent=head)
    add('cube', 'C8967A', (0, -0.285, -0.04), scale=(0.045, 0.05, 0.07), size=1, parent=head)
    jaw = empty((0, -0.2, -0.13), head)
    add('cube', '8A2A30', (0, -0.07, 0.0), scale=(0.1, 0.03, 0.028), size=1, parent=jaw)
    return dict(jaw=jaw, eyes=eyes, cap=cap, band=band)


def crew_head(head):
    add('ico_sphere', 'D8A888', (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
    add('cylinder', '1C2434', (0, 0, 0.26), radius=0.33, depth=0.14, vertices=8, parent=head)
    add('cylinder', 'ECE8DC', (0, 0, 0.36), radius=0.36, depth=0.08, vertices=8, parent=head)
    add('cube', '0E0E12', (0, -0.33, 0.21), rot=(0.2, 0, 0), scale=(0.44, 0.22, 0.04), size=1, parent=head)
    for s in (-1, 1):
        add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.09, 0.03, 0.06), size=1, parent=head, emit=0.5)
        add('cube', '0E0D14', (s * 0.105, -0.28, 0.035), scale=(0.04, 0.02, 0.04), size=1, parent=head)
    add('cube', '6A4A32', (0, -0.27, -0.12), scale=(0.24, 0.04, 0.1), size=1, parent=head)      # moustache
    return {}


def build():
    sc = bpy.context.scene
    _MOV.clear()
    S = dict(colls={})
    for name, fn in (('quay', set_quay), ('ice', set_ice), ('isle', set_isle), ('shore', set_shore), ('cabin', set_cabin)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S.update(make_liner())
    S['warship'] = make_warship()
    S['boats'] = [make_boat() for _ in range(3)]
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['vi'] = vi = K.Rig(VI, vi_head)
    S['skirt'] = [add('cone', DRESS, (0, 0, -0.5), radius1=0.62, radius2=0.32, depth=1.15, vertices=8, parent=vi.body)]
    S['lap'] = [add('cube', DRESS, (0, -0.5, -0.02), scale=(0.78, 1.05, 0.36), size=1, parent=vi.body),
                add('cube', DRESS, (0, -1.0, -0.5), scale=(0.76, 0.2, 1.0), size=1, parent=vi.body)]
    S['apron'] = [add('cube', 'F4F2EA', (0, -0.36, 0.42), scale=(0.44, 0.04, 0.62), size=1, parent=vi.body),
                  add('cube', 'F4F2EA', (0, -0.52, -0.5), rot=(0.17, 0, 0), scale=(0.62, 0.04, 0.95), size=1, parent=vi.body),
                  add('cube', 'F4F2EA', (0, -0.33, 1.02), scale=(0.5, 0.06, 0.1), size=1, parent=vi.body)]
    S['vest'] = [add('cube', 'E6DCC0', (0, -0.36, 0.56), scale=(0.66, 0.2, 0.74), size=1, parent=vi.body),
                 add('cube', 'E6DCC0', (0, 0.34, 0.56), scale=(0.66, 0.2, 0.74), size=1, parent=vi.body),
                 add('cube', 'B8AE92', (0, -0.47, 0.56), scale=(0.68, 0.02, 0.06), size=1, parent=vi.body)]
    S['crew'] = [K.Rig(CREW, crew_head) for _ in range(2)]
    S['cast'] = [S['rook'], S['vi']] + S['crew']
    # the sea: one faceted grid that every shot scales, colours and ripples
    n = 72
    me = bpy.data.meshes.new('sea')
    vs = [(i / n - 0.5, j / n - 0.5, 0.0) for j in range(n + 1) for i in range(n + 1)]
    fs = [(j * (n + 1) + i, j * (n + 1) + i + 1, (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i) for j in range(n) for i in range(n)]
    me.from_pydata(vs, [], fs)
    S['seam'] = own_mat('sea', '1E4A5A', 0.3)
    me.materials.append(S['seam'])
    me.update()
    S['sea'] = bpy.data.objects.new('sea', me)
    sc.collection.objects.link(S['sea'])
    S['sea'].location = FAR
    mov(S['sea'])
    S['sea_uv'] = np.array([(v[0], v[1]) for v in vs], dtype=np.float64)
    S['puffs'] = [mov(add('ico_sphere', ('F4F8FA', 'DCE8EE')[i % 2], FAR, radius=1.0, subdivisions=1, emit=0.15)) for i in range(16)]
    S['smoke'] = [mov(add('ico_sphere', ('3A3A42', '4A4A52')[i % 2], FAR, radius=1.0, subdivisions=1)) for i in range(10)]
    S['bits'] = [mov(add('cube', ('FFFFFF', 'DCEBF4', 'FFE8B0')[i % 3], FAR, scale=(0.3, 0.3, 0.3), size=1, emit=1.5)) for i in range(12)]
    S['bub'] = [mov(add('ico_sphere', 'BFEFFF', FAR, radius=0.12, subdivisions=1, emit=1.6, rough=0.1)) for _ in range(14)]
    S['shafts'] = [mov(add('cone', 'BFF4FF', FAR, radius1=7, radius2=0.6, depth=60, vertices=6, emit=0.5, alpha=0.07)) for _ in range(4)]
    S['ropes'] = [mov(add('cylinder', 'C8B890', FAR, radius=0.5, depth=1.0, vertices=4)) for _ in range(2)]
    S['fea'] = [mov(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(2)]
    S['coin'] = mov(add('cylinder', 'FFC233', FAR, radius=0.11, depth=0.03, vertices=8, rough=0.25, emit=1.2))
    S['fprop'] = mov(make_prop(None, FAR, 5.2))
    S['baby'] = b = mov(empty(FAR))                                                          # a wrapped bundle; no face is shown
    add('ico_sphere', 'F2ECDC', (0, 0, 0), scale=(0.75, 1.5, 0.75), radius=0.3, subdivisions=1, parent=b)
    add('ico_sphere', 'E8D8B8', (0, -0.36, 0.08), radius=0.17, subdivisions=1, parent=b)
    S['tray'] = tr = mov(empty(FAR))
    add('cylinder', 'C8CCD4', (0, 0, 0), radius=0.5, depth=0.04, vertices=10, parent=tr, rough=0.2)
    add('cone', 'F4F2EA', (0.1, 0.05, 0.2), radius1=0.2, radius2=0.14, depth=0.34, vertices=8, parent=tr, rough=0.3)
    add('cylinder', 'F4F2EA', (-0.22, -0.1, 0.09), radius=0.1, depth=0.14, vertices=8, parent=tr, rough=0.3)
    S['case'] = cs = mov(empty(FAR))
    add('cube', '7A4A2A', (0, 0, 0), scale=(0.3, 1.0, 0.7), size=1, parent=cs)
    add('cube', '3A2416', (0, 0, 0.4), scale=(0.08, 0.3, 0.08), size=1, parent=cs)
    S['brush'] = br = mov(empty(FAR))                                                        # the toothbrush, handle along local Z
    add('cube', 'F6F0DC', (0, 0, 0.36), scale=(0.07, 0.05, 0.9), size=1, parent=br, rough=0.3, emit=0.25)
    add('cube', 'FF7A1A', (0, -0.06, 0.74), scale=(0.08, 0.1, 0.2), size=1, parent=br, emit=0.6)
    S['key'] = ky = mov(empty(FAR))                                                          # the shiny thing: a brass cabin key
    add('torus', 'FFC233', (0, 0.16, 0), major_radius=0.1, minor_radius=0.03, major_segments=8, minor_segments=4, parent=ky, rough=0.2, emit=2.5)
    add('cube', 'FFC233', (0, -0.1, 0), scale=(0.05, 0.36, 0.04), size=1, parent=ky, rough=0.2, emit=2.5)
    add('cube', 'FFC233', (0.05, -0.24, 0), scale=(0.1, 0.06, 0.04), size=1, parent=ky, rough=0.2, emit=2.5)
    S['hand'] = K.Hand(SKIN, DRESS, 1.5)
    S['hand'].root.location = FAR
    mov(S['hand'].root)
    S['glow'] = light(FAR, 0, 'FFE8C0', kind='POINT')
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 2.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 9000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    S['fill'] = light((0, 0, 0), 0, 'FFFFFF', 3.0, tgt)
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    sc.world = w
    S['bg'] = w.node_tree.nodes['Background']
    S['fillk'] = 0.0
    return S


def sky(S, col, strength=1.0):
    S['bg'].inputs[0].default_value = K.hexc(col)
    S['bg'].inputs[1].default_value = strength


def show(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: at(name, x, y, z)


def cam(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='DCE4F4'):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    dx, dy, dz = look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    h = math.hypot(dx, dy) + 1e-6
    S['fill'].location = (pos[0] - dy / h * 0.3 * d, pos[1] + dx / h * 0.3 * d, pos[2] + 0.3 * d)
    S['fill'].data.energy = S['fillk'] * fill * min(d, 14) ** 2
    S['fill'].data.size = max(2.0, 0.3 * d)
    S['fill'].data.color = K.hexc(fcol)[:3]


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
    for o, par, loc, rot, scl in _MOV:
        o.parent = par
        o.location, o.rotation_euler, o.scale = loc, rot, scl
    for p in S['props']:
        p.rotation_euler = (0, 0, 0)
    vis(S['skirt'], True)
    vis(S['lap'], False)
    vis(S['apron'], True)
    vis(S['vest'], False)
    vis(S['vi'].extra['cap'], True)
    vis(S['vi'].extra['band'], False)
    vis(S['gash'], False)
    vis(S['stripe'], False)
    tint(S['hullm'], '17191E')
    tint(S['funm'], '15161A')
    tint(S['winm'], '20262E')
    tint(S['seam'], '1E4A5A')
    tint(S['cab_lampm'], 'FFE2B0', 9.0)
    tint(S['cab_pane'], '2A3A5A', 1.0)
    S['cab_lamp'].data.energy = 900
    S['cab_day'].data.energy = 0
    for l in S['quay_lamps']:
        l.data.energy = 5200
    S['glow'].location = FAR
    S['glow'].data.energy = 0
    S['glow'].data.color = K.hexc('FFE8C0')[:3]
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['face'] = dict(rook='calm', vi='calm')
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
    S['jaw'] = 0.0
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.41) % 1 < 0.035
    ez = dict(calm=0.07, deadpan=0.05, shocked=0.13, sad=0.055, warm=0.06, shut=0.012).get(e, 0.07)
    tilt = dict(deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], ease(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + (0.12 if e == 'deadpan' else 0.0) + tip * 0.35, 1.35, off), lerp(0.07, 0.0, off), 0)
    r['hat'].location = (0.0, lerp(0.0, -0.5, off), lerp(0.27 + (0.2 if e == 'shocked' else 0.0) + tip * 0.1, -0.92, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    k = dict(scared=1.45, shock=1.8, calm=1.0, tired=0.45, warm=0.8, shut=0.1).get(S['face']['vi'], 1.0)
    vblink = (t * 0.33 + 0.4) % 1 < 0.03
    for ey in S['vi'].extra['eyes']:
        ey.scale = (ey.scale[0], ey.scale[1], 0.075 * (0.1 if vblink else k))
    S['vi'].extra['jaw'].rotation_euler = (S['jaw'], 0, 0)


# ---------------------------------------------------------------- helpers for the shots
def env(S, name, skyc, sun=2.0, sunc='FFFFFF', sdir=(-0.4, -0.6, 0.7), fk=3.0, skyk=1.0):
    A = show(S, name)
    sky(S, skyc, skyk)
    S['suntgt'].location = A(0, 0, 0)
    S['sun'].location = A(sdir[0] * 400, sdir[1] * 400, sdir[2] * 400)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(sunc)[:3]
    S['fillk'] = fk
    return A


def sea(S, A, cx, cy, size, t, amp=0.5, col='1E4A5A', emit=0.0, z=0.0):
    o = S['sea']
    o.location = A(cx, cy, z)
    o.scale = (size, size, 1)
    uv = S['sea_uv']
    x, y = uv[:, 0] * size, uv[:, 1] * size
    q = 2 * PI / (size / 72 * 7)
    zz = amp * (0.55 * np.sin(x * q + y * q * 0.35 + t * 1.7) + 0.45 * np.sin(y * q * 1.37 - x * q * 0.4 - t * 2.3) + 0.25 * np.sin((x + y) * q * 2.3 + t * 3.1))
    o.data.vertices.foreach_set('co', np.column_stack([uv, zz]).ravel())
    o.data.update()
    tint(S['seam'], col, emit)


def ship(S, A, x=0.0, y=0.0, z=0.0, yaw=0.0, pitch=0.0, roll=0.0, look='dark', lit=0.0, spin=0.0):
    """Place the liner; returns a function from ship coordinates to world coordinates."""
    o = S['liner']
    o.location = A(x, y, z)
    o.rotation_euler = (pitch, roll, yaw)
    if look == 'white':
        tint(S['hullm'], 'ECE8DC')
        tint(S['funm'], 'D8A040')
        vis(S['stripe'], True)
    tint(S['winm'], 'FFD890' if lit > 0 else '20262E', 7.0 * lit)
    for i, p in enumerate(S['props']):
        p.rotation_euler = (0, spin * (1 if i != 2 else -1) + i, 0)
    M = Euler((pitch, roll, yaw)).to_matrix()
    base = Vector(A(x, y, z))
    return lambda lx, ly, lz: tuple(base + M @ Vector((lx, ly, lz)))


def funnel_smoke(S, Sp, t, n=9, k=1.0):
    for i in range(n):
        u = (t * 0.22 + i * 0.37) % 1
        yf = -38 + (i % 3) * 32
        S['smoke'][i].location = Sp(1.5 * math.sin(i * 2.1 + t), yf + 3 + 55 * u * k, 49 + 16 * u)
        s = 2.6 + 9 * u
        S['smoke'][i].scale = (s, s * 1.3, s * 0.8)


def puff(S, i, pos, s, sq=0.8):
    S['puffs'][i].location = pos
    S['puffs'][i].scale = (s, s, s * sq)


def boat_at(S, i, pos, yaw, t, bob=1.0):
    b = S['boats'][i]
    b.location = (pos[0], pos[1], pos[2] - 0.3 + 0.1 * bob * math.sin(t * 2.1 + i))
    b.rotation_euler = (0.04 * bob * math.sin(t * 1.7 + i), 0.07 * bob * math.sin(t * 2.3 + i * 2), yaw)
    c, s = math.cos(yaw), math.sin(yaw)
    return b, (lambda x, y, z: (pos[0] + x * c - y * s, pos[1] + x * s + y * c, pos[2] + z))


def seat(rig, parent, x, y, yaw=0.0, pose=None, z=0.38):
    rig.root.parent = parent
    rig.place((x, y, z), yaw)
    rig.apply(pose or P('sit'))


def aboard(S, rig, x, y, z, yaw=0.0):
    rig.root.parent = S['liner']
    rig.place((x, y, z), yaw)


def vi_look(S, vest=False, cap=True, band=False, sit=False, apron=True):
    vis(S['vest'], vest)
    vis(S['vi'].extra['cap'], cap)
    vis(S['vi'].extra['band'], band)
    vis(S['skirt'], not sit)
    vis(S['lap'], sit)
    vis(S['apron'], apron and not vest)
    if sit:
        S['apron'][1].hide_render = True


def feather(S, pos, lt, t0=0.0, n=2):
    for i in range(n):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def hat_hold(**over):
    d = dict(aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.22, 0.0))
    d.update(over)
    return P('stand', **d)


SIT_UP = P('sit', aL=(2.3, 0.5, 0.8), aR=(2.3, 0.5, 0.8), lean=-0.05, head=(-0.25, 0.0))
SIT_HAT = P('sit', aL=(0.2, 1.9, 1.6, -1.5), aR=(0.2, 1.9, 1.6, -1.5), lean=0.1, head=(-0.1, 0.0))
SIT_HOLD = P('sit', aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), lean=0.15, head=(0.1, 0.0))
ROW = P('sit', aL=(1.2, 0.2, 0.6), aR=(1.2, 0.2, 0.6), lean=0.3, head=(0.0, 0.0))
CRADLE = P('sit', aL=(0.7, -0.2, 1.5, 1.2), aR=(0.7, -0.2, 1.5, 1.2), lean=0.12, head=(0.35, 0.0))
LEAP = P('up', lL=(0.5, 1.0), lR=(-0.3, 0.6), lean=0.3)
AEGEAN, NIGHT, GREY, DUSK = '7EC0E8', '050912', '9AA8B4', '26364A'


# ---------------------------------------------------------------- the hospital ship going down by the bow (1916)
def stern_scene(S, t):
    A = env(S, 'isle', AEGEAN, sun=3.2, sunc='FFF0D8', sdir=(0.35, 0.7, 0.6), fk=1.6)
    Sp = ship(S, A, z=-3.5, pitch=0.12, look='white', spin=t * 6.5)
    sea(S, A, 0, 130, 440, t, amp=0.3, col='176E90')
    for i in range(10):                                         # white water thrown up where the blades meet the sea
        u = (t * 1.4 + i * 0.31) % 1
        px = (-8.6, 8.6, 0.0)[i % 3]
        puff(S, i, A(px + (rnd(i, 1) - 0.5) * 9, 106 + rnd(i, 2) * 4 + u * 7, 0.2 + 3.4 * u - 3.4 * u * u), 0.9 + 1.5 * u)
    return A, Sp


def crew_in(S, b, i, x, y, pose, yaw=0.0):
    seat(S['crew'][i], b, x, y, yaw, pose)


def props_pull(S, k, t, lt):
    A, Sp = stern_scene(S, t)
    v2 = S['prm'].get('v') == 2
    y = lerp(149, 141, k) if v2 else lerp(160, 147, k)
    b, B = boat_at(S, 0, A(-19 if v2 else -21, y, 0.25), 0.25, t, 1.6)
    vi_look(S, vest=True, sit=True)
    seat(S['vi'], b, -0.7, 0.2, 0.0, SIT_UP)
    S['face']['vi'] = 'scared'
    seat(S['rook'], b, 0.75, 0.6, 0.0, SIT_HAT)
    S['face']['rook'] = 'shocked'
    crew_in(S, b, 0, 0.0, -2.8, blend(ROW, SIT_UP, 0.5 + 0.5 * math.sin(lt * 9)))
    crew_in(S, b, 1, 0.0, 3.2, SIT_UP)
    if v2:
        cam(S, A(lerp(-27.5, -26.5, k), lerp(160.5, 157.0, k), 2.6), A(-10, 118, 6.5), 30)
    else:
        cam(S, A(lerp(-36, -33, k), lerp(176, 170, k), 1.9), A(-5, 112, 7.0), 30)


def boat_pov(S, k, t, lt):
    A, Sp = stern_scene(S, t)
    v2 = S['prm'].get('v') == 2
    b, B = boat_at(S, 0, A(-6, 137 - 1.5 * k, 0.25), 0.0, t, 1.8)
    rise = ease((lt - 0.25) / 0.4) if not v2 else 1.0
    vi_look(S, vest=True, sit=rise < 0.5)
    seat(S['vi'], b, -0.75, -0.4, 0.15, blend(SIT_UP, P('stand', aL=(1.2, 0.6, 0.6), aR=(1.2, 0.6, 0.6), lean=0.15, head=(-0.2, 0.0)), rise), z=lerp(0.38, 0.5, rise))
    S['face']['vi'] = 'scared'
    pop = ease(lt / 0.15)
    seat(S['rook'], b, 0.8, -0.2, -0.15, blend(P('sit'), SIT_HAT, pop))
    S['face']['rook'] = 'shocked'
    feather(S, B(1.2, -0.6, 3.2), lt, 0.15)
    crew_in(S, b, 0, 0.0, 2.8, SIT_UP)
    f = S['fprop']
    if v2:
        f.location = A(-8.6, 139.0, 6.6)
        cam(S, A(lerp(-4.0, -4.3, k), lerp(131.6, 132.2, k), 2.5), B(0.75, -0.2, 2.2), 45)
    else:
        f.location = A(2.6, 132.0, 8.6)
        cam(S, A(lerp(-3.2, -5.4, k), lerp(125.4, 128.6, k), lerp(2.0, 2.6, k)), B(0.0, -0.3, 2.45), 30)
    f.rotation_euler = (0.12, t * 6.5, 0.35)


def vi_jump(S, k, t, lt):
    A, Sp = stern_scene(S, t)
    v2 = S['prm'].get('v') == 2
    b, B = boat_at(S, 0, A(-10, 141 - 2.0 * k, 0.25), 0.5, t, 2.0)
    u = lerp(0.0, 0.6, k) if not v2 else lerp(0.42, 1.25, k)
    vi_look(S, vest=True)
    p0, p1 = Vector(B(-1.5, 0.0, 1.3)), Vector(B(-6.2, 0.6, -1.2))
    uu = min(1.0, u)
    pos = p0.lerp(p1, uu) + Vector((0, 0, 4.4 * uu * (1 - uu)))
    if u < 1.0:
        S['vi'].place(tuple(pos), PI / 2 + 0.5, pitch=0.0, roll=0.0)
        S['vi'].root.rotation_euler = (lerp(0.0, 1.5, uu), 0, PI / 2 + 0.5)
        S['vi'].apply(blend(P('stand', aL=(1.2, 0.6, 0.6), aR=(1.2, 0.6, 0.6)), LEAP, uu / 0.3))
    S['face']['vi'] = 'scared'
    if u > 0.92:                                                # the splash
        w = (u - 0.92) / 0.33
        for i in range(6):
            a = i * PI / 3
            puff(S, 10 + i, (p1[0] + math.cos(a) * 1.6 * w, p1[1] + math.sin(a) * 1.6 * w, 0.3 + 3.2 * w - 3.0 * w * w), 0.5 + 0.9 * w)
    seat(S['rook'], b, 0.7, 1.2, -1.2, SIT_HAT)
    S['face']['rook'] = 'shocked'
    seat(S['crew'][0], b, 0.4, -2.6, 0.0, P('up', lean=0.2), z=0.5)
    if v2:
        cam(S, A(-19.5, 151.0, 1.0), (p1[0] + 1.2, p1[1], 2.0), 38)
    else:
        cam(S, A(lerp(-18.5, -17.5, k), lerp(153.5, 152, k), 1.2), B(-2.6, 0.0, 3.0), 38)



def stern_up(S, k, t, lt):
    A, Sp = stern_scene(S, t)
    b1, _ = boat_at(S, 1, A(13, lerp(156, 147, k), 0.25), -0.3, t, 1.8)
    seat(S['crew'][0], b1, 0.0, -1.0, 0.0, P('up', lean=-0.1), z=0.5)
    seat(S['crew'][1], b1, 0.0, 2.6, 0.0, SIT_UP)
    boat_at(S, 2, A(-17, lerp(176, 168, k), 0.25), 0.5, t, 1.4)
    cam(S, A(lerp(36, 33, k), lerp(200, 194, k), lerp(2.0, 2.6, k)), A(2, 114, 10), 30)


def under(S, k, t, lt):
    v2 = S['prm'].get('v') == 2
    A = env(S, 'deep', '06303E', sun=1.8, sunc='BFF4FF', sdir=(0.1, -0.2, 1.0), fk=3.2)
    sea(S, A, 0, 0, 320, t, amp=0.8, col='2E9CB4', emit=0.45, z=14.0)
    if v2:
        ship(S, A, 0, -42, 12.5, pitch=0.12, look='white', spin=t * 6.5)
        z = lerp(0.6, 4.3, ease(k))
        S['vi'].place(A(0.4, 0, z), 0.5)
        S['vi'].apply(P('up', aL=(2.6, 0.5, 0.5), aR=(2.9, 0.3, 0.2), lL=(0.2, 0.3 + 0.3 * math.sin(lt * 8)), lR=(-0.1, 0.5 - 0.3 * math.sin(lt * 8)), head=(-0.5, 0.0)))
        cam(S, A(lerp(-4.2, -3.4, k), lerp(-6.8, -6.0, k), lerp(1.2, 2.2, k)), A(0.3, 0, z + 2.5), 28, fill=1.5, fcol='BFF4FF')
    else:
        ship(S, A, 20, -78, 10.5, pitch=0.12, look='white', spin=t * 6.5)
        z = lerp(11.5, 5.0, ease(k))
        S['vi'].place(A(0, 0, z), 0.3)
        S['vi'].root.rotation_euler = (lerp(1.2, 0.2, k), 0.3 * math.sin(lt * 3), 0.3)
        S['vi'].apply(P('up', aL=(2.2, 0.9, 0.4), aR=(2.5, 0.8, 0.5), lL=(0.5 * math.sin(lt * 7), 0.5), lR=(-0.5 * math.sin(lt * 7), 0.5), head=(-0.3, 0.0)))
        cam(S, A(lerp(-5.5, -4.6, k), lerp(-8.2, -7.2, k), lerp(4.4, 3.6, k)), A(0, 0, z + 1.6), 28, fill=1.5, fcol='BFF4FF')
    vi_look(S, vest=True)
    S['face']['vi'] = 'scared'
    for i, o in enumerate(S['bub']):
        u = (t * 0.9 + rnd(i, 1)) % 1
        o.location = A(0.2 + (rnd(i, 2) - 0.5) * 2.4 + 0.2 * math.sin(t * 5 + i), (rnd(i, 3) - 0.5) * 2.0, z + 0.5 + u * 7)
        s = 0.6 + 1.6 * rnd(i, 4)
        o.scale = (s, s, s)
    for i, o in enumerate(S['shafts']):
        o.location = A(-12 + i * 9 + math.sin(t * 0.7 + i) * 1.5, 14 + (i % 2) * 8, -14)
        o.rotation_euler = (0.25, 0.3, i)


# ---------------------------------------------------------------- the quay (Rook's way in, her way back, the sign-off)
def quay_scene(S, t, late=False, day=False):
    if day:
        A = env(S, 'quay', '9CC4E0', sun=3.0, sunc='FFF2DC', sdir=(0.5, -0.6, 0.6), fk=1.6)
    elif late:
        A = env(S, 'quay', 'C08A6E', sun=2.6, sunc='FFB878', sdir=(0.15, -0.85, 0.4), fk=2.4)
    else:
        A = env(S, 'quay', DUSK, sun=0.5, sunc='8FA8D8', sdir=(-0.5, -0.3, 0.8), fk=5.0)
    for l in S['quay_lamps']:
        l.data.energy = 0 if day else (2600 if late else 5200)
    Sp = ship(S, A, lit=0.0 if day else (0.5 if late else 1.0))
    sea(S, A, -170, 0, 760, t, amp=0.3, col='1C5068' if day else ('3A4A58' if late else '12303C'))
    funnel_smoke(S, Sp, t, k=0.15)
    return A, Sp


def rook_quay(S, k, t, lt):
    A, Sp = quay_scene(S, t)
    S['rook'].place(A(31, -44, 6), 0.0)
    S['rook'].apply(P('cross', head=(0.06, 0.32 * math.sin(lt * 10.0) * max(0.0, 1 - lt / 0.7))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(32.6, 32.2, k), lerp(-51.4, -50.4, k), 8.8), A(31, -44, 8.1), 40, fcol='FFD9B0')


def rook_gangway(S, k, t, lt):
    A, Sp = quay_scene(S, t)
    x = 36.5 - 4.0 * max(0.0, lt - 0.16)
    S['rook'].place(A(x, -20, 6), -PI / 2)
    S['rook'].apply(blend(P('hat', aL=(0.2, 1.9, 1.6, -1.5)), walk(t, 2.0), (lt - 0.16) / 0.14) if lt > 0.16 else
                    blend(P('stand'), P('hat', aL=(0.2, 1.9, 1.6, -1.5)), lt / 0.12))
    cam(S, A(lerp(42.5, 41.5, k), -17.4, 6.9), A(27, -20.3, 13.0), 26, fcol='FFD9B0')


def vi_gangway(S, k, t, lt):
    A, Sp = quay_scene(S, t, day=True)
    u = lerp(0.12, 0.5, k)
    vi_look(S)
    S['vi'].place(A(26 - 11.6 * u, -20, 6.25 + 10.2 * u), -PI / 2)
    w = walk(t, 1.9)
    S['vi'].apply(dict(w, aR=(0.1, 0.1, 0.2, 0.0), lean=0.22))
    S['case'].parent = S['vi'].root
    S['case'].location = (0.62, -0.1, 0.72)
    cam(S, A(lerp(30.5, 29.5, k), lerp(-25.6, -24.8, k), 8.0), A(26 - 11.6 * u - 1.5, -20, 6.25 + 10.2 * u + 3.6), 30)


def rook_wrong(S, k, t, lt):
    A, Sp = quay_scene(S, t, late=True)
    S['rook'].place(A(30, -37, 6), 0.3)
    off = ease((lt - 0.1) / 0.4)
    S['hat_off'] = off
    S['rook'].apply(blend(P('hat', head=(0.1, 0)), hat_hold(head=(0.25, 0.0)), off) if lt > 0.1 else blend(P('stand'), P('hat', head=(0.1, 0)), lt / 0.1))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(31.8, 31.4, k), lerp(-42.4, -41.6, k), lerp(8.7, 8.9, k)), A(30, -37, 8.05), 50, fill=1.3, fcol='FFE0C0')


def signoff(S, k, t, lt):
    A, Sp = quay_scene(S, t, late=True)
    pick = ease(lt / 0.4)
    pocket = ease((lt - 0.45) / 0.35)
    look = ease((lt - 1.0) / 0.2)
    pull = ease((lt - 1.3) / 0.25)
    S['rook'].place(A(29.6, -34.6, 6), -1.15)
    down = P('stand', aR=(1.25, 0.1, 0.3), lean=0.3, head=(0.3, -0.2))
    p = blend(P('stand'), down, math.sin(pick * PI * 0.5) * (1 - pocket))
    p = blend(p, P('stand', aR=(0.5, -0.1, 1.5, 1.0), head=(0.0, -0.2)), pocket * (1 - look))
    p = blend(p, P('stand', head=(-0.5, 0.5)), look * (1 - pull))
    p = blend(p, P('hat', head=(0.15, 0.3)), pull)
    S['rook'].apply(p)
    S['hat_tip'] = pull
    S['face']['rook'] = 'warm' if lt < 1.0 else ('shocked' if pull < 0.5 else 'deadpan')
    if pocket < 0.95:
        S['key'].location = A(lerp(27.9, 29.3, pocket), lerp(-33.9, -34.6, pocket), lerp(8.08, 7.6, pocket) + 0.5 * math.sin(pocket * PI))
        S['key'].rotation_euler = (0, lt * 2 * pocket, 0.6 + lt * 3 * pocket)
        S['glow'].location = A(27.0, -35.6, 9.4)
        S['glow'].data.energy = 90
    cam(S, A(lerp(24.4, 26.4, k), lerp(-40.2, -37.6, k), lerp(8.4, 7.8, k)), A(29.25, -34.5, 7.8), 34, fcol='FFE0C0')


# ---------------------------------------------------------------- 1911: the collision
def grey_day(S, t, y=0.0, roll=0.0):
    A = env(S, 'shore', GREY, sun=2.3, sunc='EEF2F6', sdir=(-0.5, -0.5, 0.7), fk=1.8)
    Sp = ship(S, A, y=y, roll=roll)
    sea(S, A, 0, 0, 1700, t, amp=1.1, col='3C5E6A')
    funnel_smoke(S, Sp, t)
    return A, Sp


def war(S, A, s, t):
    """The cruiser on its converging course; s is the distance its bow still has to run to the liner's side."""
    S['warship'].location = A(13.6 + 0.644 * (s + 60), 85 + 0.765 * (s + 60), 0.15 * math.sin(t * 2))
    S['warship'].rotation_euler = (0.01 * math.sin(t * 1.6), 0, -0.7)
    return A(13.6 + 0.644 * s, 85 + 0.765 * s, 5)


def oly_wide(S, k, t, lt):
    A, Sp = grey_day(S, t, y=lerp(34, 0, k))
    war(S, A, 190 - 30 * k, t)
    for i in range(4):
        u = (t * 0.8 + i * 0.25) % 1
        puff(S, i, Sp((1 if i % 2 else -1) * (2 + 7 * u), -124 + 22 * u, 0.6), 2.0 + 3 * u, 0.4)
    cam(S, A(lerp(-46, -40, k), lerp(-232, -218, k), lerp(20, 15, k)), A(0, -40, 22), 35)


def vi_tray(S, k, t, lt):
    A, Sp = grey_day(S, t)
    vi_look(S)
    y = -15.5 - 2.4 * lt
    S['vi'].place(A(-7.3, y, BOATDECK), 0.0)
    w = walk(t, 1.7)
    S['vi'].apply(dict(w, aL=(0.95, 0.0, 0.85, 0.3), aR=(0.95, 0.0, 0.85, 0.3), lean=0.0))
    S['tray'].location = A(-7.3, y - 0.8, BOATDECK + 2.05 + 0.03 * math.sin(t * 10))
    S['face']['vi'] = 'warm'
    S['rook'].place(A(-10.2, -20.2, BOATDECK), 0.55)
    S['rook'].apply(P('stand', aR=(0.8, 0.1, 1.3, 0.2), aL=(0.3, 0.2, 0.4), head=(0.0, -0.3)))
    S['face']['rook'] = 'deadpan'
    u = (lt * 1.5) % 1
    S['coin'].location = A(-9.75, -20.75, BOATDECK + 1.8 + 3.0 * u * (1 - u))
    S['coin'].rotation_euler = (lt * 30, 0, 0)
    cam(S, A(lerp(-10.2, -7.2, k), lerp(-31.5, -28.0, k), lerp(26.9, 27.9, k)), A(-8.6, -20, 27.5), 34)


def hawke_bow(S, k, t, lt):
    A, Sp = grey_day(S, t)
    tip = war(S, A, lerp(105, 62, k), t)
    for i in range(4):
        u = (t * 1.1 + i * 0.25) % 1
        puff(S, i, (tip[0] + (1 if i % 2 else -1) * (1 + 4 * u) + 0.64 * 10 * u, tip[1] + 0.76 * 12 * u, A(0, 0, 0.6)[2]), 1.4 + 2.2 * u, 0.4)
    cam(S, A(lerp(31, 29, k), lerp(52, 58, k), lerp(4.5, 6.0, k)), (tip[0], tip[1], tip[2] + 5), 48)


def hawke_hit(S, k, t, lt):
    hit = max(0.0, lt - 0.42)
    A, Sp = grey_day(S, t, roll=-0.03 * math.sin(min(hit * 5, PI)))
    tip = war(S, A, lerp(16, -2.5, ease(min(1.0, lt / 0.5))), t)
    if hit > 0:
        vis(S['gash'], True)
        for i in range(8):
            u = min(1.0, hit * 1.6)
            a = rnd(i, 1) * 2 * PI
            puff(S, i, A(15 + math.cos(a) * 9 * u, 86 + math.sin(a) * 6 * u, 1 + (10 + 14 * rnd(i, 2)) * (u - 0.75 * u * u)), 1.5 + 3.5 * u)
        for i, o in enumerate(S['bits']):
            u = hit * 1.3
            o.location = A(14.5 + (2 + 9 * rnd(i, 3)) * u, 85 + (rnd(i, 4) - 0.5) * 16 * u, 8 + 12 * rnd(i, 5) * u - 9 * u * u)
            o.rotation_euler = (u * 7 + i, u * 5, i)
            o.scale = (0.9, 0.5, 0.2)
    cam(S, A(lerp(70, 66, k), lerp(30, 34, k), 26), A(17, 86, 8), 30)


def deck_jolt(S, k, t, lt):
    A, Sp = grey_day(S, t)
    j = math.exp(-lt * 2.2) * math.sin(lt * 15)
    vi_look(S)
    S['vi'].place(A(-7.2 + 0.5 * j, -17.5, BOATDECK), PI - 0.2)
    S['vi'].apply(P('stand', aL=(1.3, 0.9, 0.5), aR=(1.0, 1.1, 0.6), lean=-0.18 + 0.2 * j, lL=(0.4, 0.3), lR=(-0.35, 0.2), head=(-0.15, 0.3)))
    S['face']['vi'] = 'scared'
    u = min(1.0, lt / 0.8)
    S['tray'].location = A(-7.6 - 1.2 * u, -16.4 + 1.6 * u, BOATDECK + 2.2 + 5.0 * u - 6.5 * u * u)
    S['tray'].rotation_euler = (u * 6, u * 4, 0)
    S['rook'].place(A(-9.9 - 0.3 * j, -14.4, BOATDECK), PI - 0.75)
    S['rook'].apply(P('hat', aL=(0.6, 1.2, 0.4), lean=-0.1 + 0.25 * j, lL=(0.3, 0.2), lR=(-0.3, 0.3)))
    S['face']['rook'] = 'shocked'
    feather(S, A(-9.6, -14.8, BOATDECK + 3.3), lt, 0.1)
    cam(S, A(-8.7, lerp(-8.6, -9.2, k), 27.4), A(-8.5, -16, 27.4), 30, roll=0.14 * j)


def oly_limp(S, k, t, lt):
    A, Sp = grey_day(S, t, y=-16 * k, roll=0.035 + 0.01 * math.sin(lt * 3))
    vis(S['gash'], True)
    S['warship'].location = A(96, 30, 0)
    S['warship'].rotation_euler = (0.05, 0, 2.5)
    for i in range(4):
        u = (t * 0.5 + i * 0.25) % 1
        puff(S, i, Sp(13.5 + 2 * u, 88 + 10 * u, 0.5), 1.2 + 1.5 * u, 0.4)
    cam(S, A(lerp(58, 38, k), lerp(166, 136, k), lerp(4, 11, k)), A(11, 88 - 12 * k, 12), 38)


# ---------------------------------------------------------------- 1912: the ice
def ice_night(S, t, y=0.0, z=0.0, pitch=0.0, x=7.5):
    A = env(S, 'ice', NIGHT, sun=0.9, sunc='A8C0FF', sdir=(0.35, -0.55, 0.7), fk=1.2)
    Sp = ship(S, A, x=x, y=y, z=z, pitch=pitch, lit=1.0)
    sea(S, A, 0, -120, 1100, t, amp=0.45, col='0A1A2A')
    return A, Sp


def tit_night(S, k, t, lt):
    A, Sp = ice_night(S, t, y=lerp(-30, -62, k))
    funnel_smoke(S, Sp, t)
    for i in range(4):
        u = (t * 0.9 + i * 0.25) % 1
        puff(S, i, Sp((1 if i % 2 else -1) * (2 + 6 * u), -125 + 20 * u, 0.5), 1.6 + 2.6 * u, 0.4)
    cam(S, A(lerp(-22, -8, k), lerp(-262, -228, k), lerp(2.5, 9.0, k)), A(lerp(12, 8, k), lerp(-185, -150, k), 16), 28, fcol='A8C0FF')


def berg_scrape(S, k, t, lt):
    A, Sp = ice_night(S, t, y=lerp(-78, -104, k))
    for i, o in enumerate(S['bits']):
        u = (lt * 1.1 + rnd(i, 1)) % 1
        o.location = A(13.5 + (rnd(i, 2) - 0.3) * 3, -214 + (rnd(i, 3) - 0.5) * 16, 10 * (1 - u) ** 2 + 0.5)
        o.rotation_euler = (u * 9 + i, u * 6, i)
        s = 0.8 + 1.4 * rnd(i, 4)
        o.scale = (s, s, s)
    for i in range(5):
        u = (t * 1.2 + i * 0.2) % 1
        puff(S, i, A(13 + rnd(i, 5) * 2, -214 + (i - 2) * 4, 0.4 + 2 * u), 0.8 + 1.6 * u, 0.5)
    cam(S, A(lerp(19.5, 18.5, k), lerp(-262, -256, k), lerp(26, 22, k)), A(13.5, -212, 5), 32, fcol='A8C0FF')


def cabin(S, day=False):
    A = env(S, 'cabin', '000000', sun=0.0, fk=2.6)
    if day:
        S['cab_day'].data.energy = 420
        S['cab_lamp'].data.energy = 300
        tint(S['cab_pane'], 'CFE8FF', 7.0)
    return A


def vi_berth(S, k, t, lt):
    A = cabin(S)
    hit = ease((lt - 1.05) / 0.15)
    sw = 0.06 * math.sin(lt * 3.0)
    if lt > 1.05:
        sw = 0.5 * math.sin((lt - 1.05) * 9) * math.exp(-(lt - 1.05) * 1.2)
    S['cab_swing'].rotation_euler = (0, sw, 0)
    vi_look(S, sit=True, cap=False)
    S['vi'].place(A(-2.35, 4.4, 1.45), PI / 2)
    S['vi'].apply(blend(P('sit', head=(0.3, 0.2 + 0.15 * math.sin(lt * 2.5))), P('sit', aL=(0.5, 0.5, 0.6), aR=(0.5, 0.5, 0.6), lean=0.0, head=(-0.4, -0.5)), hit))
    S['face']['vi'] = 'scared' if hit > 0.5 else 'tired'
    S['rook'].place(A(-0.5, 8.3, 0), 0.25)
    S['rook'].apply(blend(P('stand', aR=(0.8, 0.1, 1.3, 0.2), aL=(0.3, 0.2, 0.4), head=(0.0, 0.3)), P('stand', aL=(0.5, 1.0, 0.5), aR=(0.5, 1.0, 0.5), head=(-0.55, 0.0)), hit))
    S['face']['rook'] = 'shocked' if hit > 0.5 else 'deadpan'
    if hit < 0.2:
        u = (lt * 1.6) % 1
        S['coin'].location = A(-0.15, 7.75, 1.85 + 2.6 * u * (1 - u))
        S['coin'].rotation_euler = (lt * 30, 0, 0)
    feather(S, A(-0.2, 8.0, 3.3), lt, 1.15)
    cam(S, A(1.7, lerp(-0.6, 0.5, k), 3.4), A(-1.4, 6.5, 3.0), 24, roll=0.05 * hit * math.sin(lt * 12), fcol='FFE0C0')


def davit_scene(S, t, zb, k, xb=16.7):
    A, Sp = ice_night(S, t, y=-110, z=-2.0, pitch=0.035, x=0.0)
    b = S['boats'][0]
    b.parent = S['liner']
    b.location = (xb, -20, zb)
    b.rotation_euler = (0.03 * math.sin(t * 2.2), 0.05 * math.sin(t * 1.7), 0)
    for i, yy in enumerate((-24.5, -15.5)):
        seg(S['ropes'][i], Sp(13.9, yy, 29.0), Sp(xb, yy - (0.3 if i == 0 else -0.3), zb + 1.6), 0.09)
    S['glow'].location = Sp(xb + 5, -20, zb + 5)
    S['glow'].data.energy = 2600
    return A, Sp, b


def boat_lower(S, k, t, lt):
    zb = lerp(22.5, 12.5, k)
    A, Sp, b = davit_scene(S, t, zb, k)
    vi_look(S, vest=True, sit=True)
    seat(S['vi'], b, -0.55, -0.5, 1.0, P('sit', head=(-0.5, 0.0), aL=(0.9, 0.2, 1.0), aR=(0.9, 0.2, 1.0)))
    S['face']['vi'] = 'scared'
    seat(S['rook'], b, 0.6, 1.6, 1.2, P('sit', head=(0.35, 0.5), aR=(0.9, 0.9, 0.4)))
    S['face']['rook'] = 'shocked'
    seat(S['crew'][0], b, 0.0, -3.2, 1.0, P('up', aL=(2.6, 0.2, 0.3), aR=(2.6, 0.2, 0.3)), z=0.5)
    seat(S['crew'][1], b, 0.0, 3.4, 1.0, P('up', aL=(2.6, 0.2, 0.3), aR=(2.6, 0.2, 0.3)), z=0.5)
    cam(S, Sp(lerp(37, 35, k), lerp(-37, -35, k), lerp(17, 13, k)), Sp(16.5, -20, zb + 2.0), 52, fcol='FFD9B0')


def baby(S, k, t, lt):
    A, Sp, b = davit_scene(S, t, 23.55, k, xb=13.8)
    give = ease((lt - 0.2) / 0.5)
    vi_look(S, vest=True, sit=True)
    seat(S['vi'], b, -0.1, -0.2, -PI / 2 + 0.5, blend(P('sit', aL=(1.7, 0.2, 0.5), aR=(1.7, 0.2, 0.5), head=(-0.3, 0.0), lean=0.2), CRADLE, ease((lt - 0.6) / 0.3)))
    S['face']['vi'] = 'shock' if give > 0.6 else 'scared'
    seat(S['rook'], b, 0.45, 1.5, -0.9, blend(P('sit'), P('sit', aL=(0.5, 0.9, 0.6), aR=(0.5, 0.9, 0.6), head=(0.2, 0.55)), give))
    S['face']['rook'] = 'shocked' if give > 0.5 else 'deadpan'
    c = S['crew'][0]
    aboard(S, c, 11.0, -20.5, BOATDECK, PI / 2)
    c.apply(blend(P('stand', aL=(1.3, 0.1, 0.5), aR=(1.3, 0.1, 0.5), lean=0.5, head=(0.2, 0.0)), P('stand', aL=(0.9, 0.3, 0.3), aR=(0.9, 0.3, 0.3), lean=0.3), ease((lt - 0.75) / 0.3)))
    S['baby'].parent = S['liner']
    S['baby'].location = (lerp(12.2, 13.25, give), -20.4, lerp(27.0, 25.8, give) + 0.3 * math.sin(give * PI))
    S['baby'].rotation_euler = (0, 0, PI / 2)
    cam(S, Sp(lerp(16.2, 15.8, k), lerp(-25.2, -24.6, k), lerp(29.9, 29.5, k)), Sp(12.7, -19.3, 26.5), 24, fcol='FFD9B0')


def tit_sink(S, k, t, lt):
    A, Sp = ice_night(S, t, y=0, z=lerp(-8, -10.5, k), pitch=lerp(0.16, 0.19, k), x=0.0)
    b, B = boat_at(S, 0, A(116.7, 225.6, 0.2), -0.594, t, 0.8)
    vi_look(S, vest=True, sit=True)
    seat(S['vi'], b, 0.65, -1.9, 0.0, CRADLE)
    S['baby'].parent = b
    S['baby'].location = (0.65, -2.45, 1.75)
    S['baby'].rotation_euler = (0, 0.2, PI / 2)
    S['hat_off'] = ease(lt / 0.5)
    seat(S['rook'], b, -0.8, 0.3, 0.0, blend(P('sit'), SIT_HOLD, S['hat_off']))
    S['rook'].head.rotation_euler = (0.05, 0, 1.0)
    S['face']['rook'] = 'sad'
    S['face']['vi'] = 'tired'
    S['glow'].location = B(-2.0, 3.0, 3.2)
    S['glow'].data.energy = 900
    S['glow'].data.color = K.hexc('A8C0FF')[:3]
    cam(S, A(lerp(121.0, 120.0, k), lerp(231.2, 230.0, k), lerp(1.5, 1.9, k)), A(5, 60, 26), 35, fill=2.2, fcol='A8C0FF')


# ---------------------------------------------------------------- 1916: the hospital ship
def aegean(S, t, y=0.0, pitch=0.0, z=0.0, cy=0.0):
    A = env(S, 'isle', '86C4EA', sun=3.4, sunc='FFF4E0', sdir=(0.5, -0.6, 0.6), fk=1.4)
    Sp = ship(S, A, y=y, z=z, pitch=pitch, look='white')
    sea(S, A, 0, cy, 1700, t, amp=1.1, col='1878A0')
    return A, Sp


def brit_wide(S, k, t, lt):
    A, Sp = aegean(S, t, y=lerp(30, 0, k))
    funnel_smoke(S, Sp, t)
    for i in range(4):
        u = (t * 0.8 + i * 0.25) % 1
        puff(S, i, Sp((1 if i % 2 else -1) * (2 + 7 * u), -124 + 22 * u, 0.6), 2.0 + 3 * u, 0.4)
    cam(S, A(lerp(84, 34, k), lerp(-250, -196, k), lerp(70, 12, k)), A(0, lerp(-30, -70, k), 18), 32)


def mine_hit(S, k, t, lt):
    A, Sp = aegean(S, t, y=-8 * k)
    funnel_smoke(S, Sp, t)
    hit = max(0.0, lt - 0.12)
    u = min(1.0, hit * 1.5)
    base = Sp(13.5, -92, 0)
    if hit > 0:
        for i in range(14):
            a = rnd(i, 1) * 2 * PI
            hgt = (10 + 52 * (i / 13)) * (u - 0.4 * u * u)
            w = (2.0 + 5.0 * u) * (1 - i / 20)
            puff(S, i, (base[0] + math.cos(a) * w * rnd(i, 3), base[1] + math.sin(a) * w * rnd(i, 4), base[2] + hgt), (1.6 + 2.6 * u) * (1.3 - i / 20), 1.4)
        for i, o in enumerate(S['bits']):
            o.location = (base[0] + (rnd(i, 5) - 0.3) * 30 * u, base[1] + (rnd(i, 6) - 0.5) * 26 * u, base[2] + 30 * rnd(i, 7) * u - 14 * u * u + 3)
            o.scale = (0.9, 0.9, 0.9)
        S['glow'].location = (base[0] + 6, base[1] - 4, base[2] + 8)
        S['glow'].data.energy = 6e5 * max(0.0, 1 - hit / 0.35)
        S['glow'].data.color = K.hexc('FFA040')[:3]
    cam(S, A(lerp(78, 74, k), lerp(-172, -166, k), 5), A(12, -92, 18), 32)


def vi_brush(S, k, t, lt):
    A = cabin(S, day=True)
    reach = ease((lt - 0.15) / 0.35)
    vi_look(S, vest=True)
    S['vi'].place(A(2.2, 8.8, 0), -PI / 2 - 0.15 + PI)
    S['vi'].apply(blend(P('stand', head=(0.0, 0.4)), P('stand', aR=(1.35, 0.0, 0.15), lean=0.12, head=(0.15, 0.0)), reach))
    S['brush'].location = A(4.45, 9.05, 3.12)
    S['brush'].rotation_euler = (0.22, 0.2, 0)
    S['rook'].place(A(-0.9, 9.4, 0), 0.2)
    S['rook'].apply(blend(P('cross'), P('point', aR=(1.3, -0.5, 0.1), head=(0.0, -0.55)), reach))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(1.2, 1.4, k), lerp(1.2, 2.0, k), 3.5), A(1.3, 9, 3.1), 28, roll=0.07, fcol='FFF0DC')


def brush_close(S, k, t, lt):
    A = cabin(S, day=True)
    down = ease(lt / 0.3)
    up = ease((lt - 0.42) / 0.4)
    S['hand'].grip(lerp(0.15, 0.85, ease((lt - 0.25) / 0.15)))
    hz = lerp(6.0, 4.75, down) + 1.1 * up
    S['hand'].place(A(4.45, 8.98, hz), (PI / 2, 0, PI))
    S['brush'].location = A(4.45, 9.05, 3.12 + 1.1 * up)
    S['brush'].rotation_euler = (0.22 * (1 - up), 0.2 * (1 - up), 0)
    S['glow'].location = A(3.2, 7.8, 4.6)
    S['glow'].data.energy = 30
    cam(S, A(lerp(2.7, 2.9, k), lerp(7.2, 7.5, k), 3.9), A(4.4, 9.0, 3.9 + 0.5 * up), 45, roll=0.07, fcol='FFF0DC')


def rook_brush(S, k, t, lt):
    A = cabin(S, day=True)
    S['rook'].place(A(-0.9, 9.4, 0), 0.1)
    sh = ease(lt / 0.12)
    S['rook'].apply(blend(P('point', aR=(1.3, -0.5, 0.1), head=(0.0, -0.4)), P('shrug', head=(0.05, 0.15)), sh))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = ease((lt - 0.2) / 0.15)
    cam(S, A(lerp(0.4, 0.2, k), lerp(4.6, 5.2, k), 3.0), A(-0.9, 9.4, 2.85), 42, roll=0.07, fcol='FFF0DC')


def rook_deck(S, k, t, lt):
    A, Sp = aegean(S, t)
    funnel_smoke(S, Sp, t)
    turn = ease((lt - 0.6) / 0.25)
    S['rook'].place(A(9.6, -20.4, BOATDECK), PI - 0.5)
    S['rook'].apply(blend(P('stand', aR=(0.8, 0.1, 1.3, 0.2), aL=(0.3, 0.2, 0.4), head=(0.0, 0.2)), P('stand', aR=(0.5, -0.1, 1.5, 1.0), aL=(0.3, 0.2, 0.4), head=(0.0, -1.0)), turn))
    S['face']['rook'] = 'deadpan'
    if turn < 0.3:
        u = (lt * 1.7) % 1
        S['coin'].location = A(9.25, -19.85, BOATDECK + 1.8 + 2.8 * u * (1 - u))
        S['coin'].rotation_euler = (lt * 30, 0, 0)
    cam(S, A(lerp(6.6, 8.2, k), lerp(-10.6, -14.4, k), lerp(27.9, 27.3, k)), A(9.0, -20.4, 27.25), 32, fill=3.0, fcol='FFF0DC')


def brit_side(S, k, t, lt):
    A, Sp = aegean(S, t, y=lerp(40, 10, k))
    for i in range(6):
        u = (t * 0.9 + i * 0.17) % 1
        puff(S, i, A(15.5 + 2.5 * u, -70 + i * 22 + 26 * u, 0.5), 1.0 + 1.8 * u, 0.4)
    cam(S, A(lerp(27, 25, k), -78, lerp(2.2, 3.2, k)), A(11, 10, 17), 26)


# ---------------------------------------------------------------- pulled out of the water
def rescue_scene(S, t):
    A = env(S, 'isle', '86C4EA', sun=3.4, sunc='FFF4E0', sdir=(-0.2, -0.7, 0.6), fk=1.8)
    ship(S, A, z=-10, pitch=0.17, look='white')
    sea(S, A, -40, 200, 600, t, amp=0.5, col='1878A0')
    return A


def vi_rescued(S, k, t, lt):
    A = rescue_scene(S, t)
    b, B = boat_at(S, 1, A(-60, 230, 0.2), 0.0, t, 1.2)
    pull = ease(lt / 1.0)
    vi_look(S, vest=True, cap=False)
    S['vi'].place(B(-2.25, -0.4, lerp(-2.0, -1.1, pull)), -PI / 2)
    S['vi'].root.rotation_euler = (0.15, 0, -PI / 2)
    S['vi'].apply(P('up', aL=(2.5, 0.3, 0.3), aR=(2.5, 0.3, 0.3), head=(-0.2, 0.0)))
    S['face']['vi'] = 'tired'
    seat(S['crew'][0], b, -0.9, -0.4, -PI / 2, P('stand', aL=(1.0, 0.1, 0.4), aR=(1.0, 0.1, 0.4), lean=0.75, lL=(1.2, 1.5), lR=(1.2, 1.5), lift=-0.45, head=(0.1, 0)), z=0.55)
    S['hat_off'] = 1.0
    seat(S['rook'], b, -0.5, 1.5, -PI / 2 + 0.45, P('sit', aR=(1.2, 0.0, 0.3), aL=(0.75, -0.25, 1.75, 1.1), lean=0.4, head=(0.15, 0.0)))
    S['face']['rook'] = 'sad'
    for i in range(5):
        u = (t * 1.0 + i * 0.2) % 1
        a = i * 1.3
        puff(S, i, B(-2.5 + math.cos(a) * 1.2 * u, -0.4 + math.sin(a) * 1.2 * u, 0.15), 0.3 + 0.5 * u, 0.3)
    cam(S, A(lerp(-66.6, -66.0, k), lerp(226.0, 226.6, k), 1.1), B(-1.3, 0.3, 1.25), 32)


def vi_alive(S, k, t, lt):
    A = rescue_scene(S, t)
    b, B = boat_at(S, 1, A(-60, 230, 0.2), 0.0, t, 0.8)
    vi_look(S, vest=True, cap=False, band=True, sit=True)
    op = ease((lt - 0.2) / 0.3)
    seat(S['vi'], b, 0.0, -0.3, 0.0, blend(P('sit', head=(0.4, 0.0)), P('sit', head=(-0.05, 0.1), lean=0.1), op))
    S['face']['vi'] = 'warm' if op > 0.5 else 'shut'
    seat(S['crew'][0], b, 0.0, 2.8, PI, blend(ROW, P('sit', aL=(1.2, 0.2, 1.3), aR=(1.2, 0.2, 1.3), lean=-0.1), 0.5 + 0.5 * math.sin(t * 4)))
    cam(S, B(lerp(0.9, 0.6, k), lerp(-4.6, -4.0, k), 2.5), B(0.0, -0.3, 2.2), 50, fcol='FFF0DC')


def rook_shock(S, k, t, lt):
    A = rescue_scene(S, t)
    b, B = boat_at(S, 1, A(-60, 230, 0.2), 0.0, t, 0.8)
    pop = ease(lt / 0.15)
    seat(S['rook'], b, 0.0, 2.7, 0.0, blend(P('sit', aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3)), P('sit', aL=(0.5, 1.1, 0.6), aR=(0.5, 1.1, 0.6), lean=0.0, head=(-0.12, 0.0)), pop))
    S['face']['rook'] = 'shocked' if pop > 0.3 else 'deadpan'
    feather(S, B(0.3, 2.4, 3.1), lt, 0.1)
    cam(S, B(lerp(1.3, 1.0, k), lerp(-1.6, -1.0, k), 2.5), B(0.0, 2.7, 2.1), 45, fcol='FFF0DC')


# ---------------------------------------------------------------- photographs for the case board
def photo_ship(S, k, t, lt):
    A, Sp = quay_scene(S, t, day=True)
    cam(S, A(46, -190, 8), A(4, -60, 26), 26)


def photo_vi(S, k, t, lt):
    A, Sp = grey_day(S, t)
    vi_look(S)
    S['vi'].place(A(-8.0, -18, BOATDECK), 0.15)
    S['vi'].apply(P('stand', aL=(0.6, -0.15, 1.1, 0.8), aR=(0.6, -0.15, 1.1, 0.8)))
    S['face']['vi'] = 'warm'
    cam(S, A(-8.8, -24.2, 27.7), A(-8.0, -18, 27.2), 50)


SHOTS3D = {f.__name__: f for f in (
    props_pull, boat_pov, vi_jump, under, rook_quay, rook_gangway, oly_wide, vi_tray, hawke_bow, hawke_hit, deck_jolt, oly_limp,
    tit_night, berg_scrape, vi_berth, boat_lower, baby, tit_sink, brit_wide, rook_deck, brit_side, mine_hit, vi_brush, brush_close, rook_brush,
    stern_up, vi_rescued, vi_alive, rook_shock, vi_gangway, rook_wrong, signoff)}
STILLS = dict(ship=photo_ship, vi=photo_vi)
