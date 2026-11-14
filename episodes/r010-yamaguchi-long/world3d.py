"""Case 010 in 3D - Tsutomu Yamaguchi, Hiroshima 6 August 1945 and Nagasaki 9 August 1945. Sets built for this
story only: a shipyard road outside Hiroshima on a summer morning, an air-raid shelter, a country railway
platform with a steam train, a drawing office in Nagasaki and a lecture hall many years later.

Handled soberly: nobody but Yamaguchi, his boss and two draughtsmen is shown, no victims and no injuries are
shown beyond his bandages, and both explosions are shown only as light, wind and a far column of cloud."""
import math

import bpy

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(hiro=(0, 0, 0), shelter=(400, 0, 0), rail=(800, 0, 0), office=(1200, 0, 0), hall=(1600, 0, 0))
FAR = (0, 0, -900)
HOST = {'rook_station', 'rook_walk', 'yama_walk', 'rook_looks', 'flash_road', 'thrown', 'aftermath', 'rook_shelter', 'train_window',
        'office_wide', 'rook_office', 'office_blast', 'yama_stands', 'rook_hall', 'hall_wide', 'rook_wrong', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'D9A878'
YAMA = dict(top='E6E0D0', pants='6A6450', hand=SKIN, boot='3A3028', fore=SKIN)
BOSS = dict(top='39414E', pants='2C323C', hand='C99868', boot='1E1C20')
MEN = [dict(top=c, pants='4E4A40', hand='D0A070', boot='2A2620', fore='D0A070') for c in ('D8D4C4', 'C4CCD0')]
OLD = dict(top='2E3442', pants='262A36', hand='D2A882', boot='18181C')
_MOV = []


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def at(name, x, y, z):
    o = ORG[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def group(name, fn):
    """Build one set under its own origin and collection, so only one set renders per shot."""
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
    """A material of its own whose colour and glow a shot may change."""
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


def mix_col(a, b, k):
    k = max(0.0, min(1.0, k))
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


# ---------------------------------------------------------------- set 1: the road to the shipyard, Hiroshima
def set_hiro(r):
    add('plane', 'A89868', (0, 0, -0.02), size=3000, parent=r)
    add('cube', '8E8474', (0, 120, 0.02), scale=(6.4, 520, 0.06), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '6E7A48', (s * 4.1, 120, 0.06), scale=(1.4, 520, 0.14), size=1, parent=r)
    for i in range(16):                                    # sweet-potato rows on the right, a canal on the left
        add('cube', ('4E7A3A', '5E8A40')[i % 2], (8.5 + i * 2.2, 40, 0.22), scale=(1.3, 220, 0.5), size=1, parent=r)
    add('cube', '4A7A9A', (-16, 120, 0.0), scale=(13, 520, 0.08), size=1, parent=r, rough=0.2)
    add('cube', '7A7060', (-9.2, 120, 0.2), scale=(0.7, 520, 0.5), size=1, parent=r)
    for i in range(-3, 13):                                # telegraph poles and one wire
        y = i * 13.0
        add('cylinder', '4A3A2A', (-5.6, y, 3.6), radius=0.13, depth=7.2, vertices=6, parent=r)
        add('cube', '4A3A2A', (-5.6, y, 6.6), scale=(1.7, 0.12, 0.12), size=1, parent=r)
    add('cube', '2A2A2A', (-6.2, 60, 6.72), scale=(0.03, 200, 0.03), size=1, parent=r)
    add('cube', '2A2A2A', (-5.0, 60, 6.72), scale=(0.03, 200, 0.03), size=1, parent=r)
    yard = empty((26, 118, 0), r)                          # the shipyard he is walking to: slip, hull, two cranes, sheds
    add('cube', '7A7468', (0, 0, 0.6), scale=(70, 46, 1.2), size=1, parent=yard)
    add('cube', '3E4852', (-6, -4, 6.2), scale=(44, 9, 10), size=1, parent=yard)
    add('cube', '3E4852', (-28, -4, 6.2), rot=(0, 0, PI / 4), scale=(6.4, 6.4, 10), size=1, parent=yard)
    add('cube', '7A2E22', (-6, -4, 1.9), scale=(44.2, 9.2, 1.6), size=1, parent=yard)
    for x in (-22, 12):
        for sy in (-11, 3.5):
            add('cube', '5A6068', (x, sy, 13), scale=(0.9, 0.9, 26), size=1, parent=yard)
        add('cube', '5A6068', (x, -3.8, 26), scale=(1.4, 17, 1.4), size=1, parent=yard)
        add('cube', '5A6068', (x + 7, -3.8, 27.2), rot=(0, -0.22, 0), scale=(24, 1.0, 1.0), size=1, parent=yard)
        add('cube', '3A3E44', (x - 2, -3.8, 28.2), scale=(4, 3, 3), size=1, parent=yard)
    for i, (x, w, hh) in enumerate(((30, 18, 8), (-44, 14, 6.5), (44, 10, 11))):
        add('cube', ('8A8272', '9A9080', '7E786A')[i], (x, 14, hh / 2 + 1.2), scale=(w, 16, hh), size=1, parent=yard)
        add('cube', '4E4A44', (x, 14, hh + 1.6), rot=(0.0, 0, 0), scale=(w + 1, 17, 0.8), size=1, parent=yard)
    add('cylinder', '6A645C', (40, 20, 12), radius=1.2, depth=24, vertices=8, parent=yard)
    town = empty((0, 0, 0), r)                             # the city, far up the road: low wooden roofs, a few chimneys
    for i in range(70):
        a = (i * 0.618) % 1
        x = -420 + a * 840
        y = 330 + (i * 37) % 170
        hh = 5 + (i * 7) % 9
        w = 16 + (i * 11) % 22
        add('cube', ('8E8676', '7E786C', '9A9282', '6E6A62')[i % 4], (x, y, hh / 2), scale=(w, 14, hh), size=1, parent=town)
        if i % 3 == 0:
            add('cube', '4A4844', (x, y, hh + 0.8), scale=(w + 2, 15, 1.6), size=1, parent=town)
    for x, y, hh in ((-140, 380, 34), (90, 420, 28), (210, 360, 22)):
        add('cylinder', '6A645C', (x, y, hh / 2), radius=2.4, depth=hh, vertices=7, parent=town)
    for i in range(15):                                    # the hills around the delta
        a = i / 14
        add('cone', ('6A8A9A', '5E7E90', '7A98A6')[i % 3], (-620 + a * 1240, 760 + (i % 3) * 60, 40 + (i * 23) % 50),
            radius1=150 + (i % 4) * 30, radius2=10, depth=110 + (i * 31) % 80, vertices=7, parent=r)
    for i in range(12):                                    # behind him: farmhouses and trees on the plain
        x = -150 + i * 27 + (i * 13) % 9
        add('cube', ('8E8676', '9A9282')[i % 2], (x, -170 - (i % 3) * 25, 3), scale=(14, 10, 6), size=1, parent=r)
        add('cone', '4A4844', (x, -170 - (i % 3) * 25, 7.6), rot=(0, 0, PI / 4), radius1=11, radius2=0, depth=4, vertices=4, parent=r)
        add('ico_sphere', '3E6A3A', (x + 12, -160 - (i % 3) * 25, 6), scale=(1, 1, 1.3), radius=5, subdivisions=1, parent=r)
    tgt = empty((0, 0, 0), r)
    sun = light((120, -160, 220), 3.6, 'FFF4DC', kind='SUN', target=tgt, parent=r)
    return dict(sun=sun)


# ---------------------------------------------------------------- set 2: an air-raid shelter
def set_shelter(r):
    add('cube', '3A2E24', (0, 2, -0.1), scale=(7, 22, 0.2), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '4E3E30', (s * 3.0, 2, 1.9), scale=(0.6, 22, 4.2), size=1, parent=r)
        add('cube', '6E5438', (s * 2.25, 2, 0.5), scale=(0.9, 20, 0.12), size=1, parent=r)
        for y in range(-7, 13, 3):
            add('cube', '5A4530', (s * 2.62, y, 1.9), scale=(0.22, 0.26, 3.8), size=1, parent=r)
            add('cube', '4A3826', (s * 2.25, y + 1.2, 0.24), scale=(0.7, 0.16, 0.48), size=1, parent=r)
    add('cube', '45362A', (0, 2, 3.95), scale=(7, 22, 0.3), size=1, parent=r)
    for y in range(-7, 13, 3):
        add('cube', '5A4530', (0, y, 3.72), scale=(5.6, 0.26, 0.22), size=1, parent=r)
    add('cube', '3A2E24', (0, 11.5, 1.9), scale=(7, 0.6, 4.2), size=1, parent=r)
    for i in range(5):                                     # sandbags at the far end
        add('cube', ('8A7A5A', '7A6C50')[i % 2], (-1.6 + i * 0.8, 10.9, 0.25 + (i % 2) * 0.4), scale=(0.9, 0.5, 0.36), size=1, parent=r)
    add('cube', '6A5A40', (-2.2, 6.0, 0.9), scale=(0.7, 0.9, 0.7), size=1, parent=r)
    add('cylinder', '5E6A72', (2.2, 7.0, 0.95), radius=0.3, depth=0.8, vertices=8, parent=r, rough=0.4)
    lan = empty((0.1, 3.2, 3.6), r)
    add('cylinder', '2A2A2A', (0, 0, -0.3), radius=0.02, depth=0.6, vertices=4, parent=lan)
    add('cylinder', 'FFB45A', (0, 0, -0.78), radius=0.16, depth=0.34, vertices=6, parent=lan, emit=8)
    add('cone', '2A2A2A', (0, 0, -0.55), radius1=0.26, radius2=0.05, depth=0.14, vertices=6, parent=lan)
    add('cylinder', '2A2A2A', (0, 0, -0.98), radius=0.18, depth=0.06, vertices=6, parent=lan)
    lamp = light((0, -0.25, -0.9), 420, 'FFB060', kind='POINT', parent=lan)
    aim = empty((0, 2, 1.6), r)
    light((0, -7, 2.4), 150, '6E8FD8', 3.0, aim, parent=r)
    return dict(lan=mov(lan), lanlight=lamp)


# ---------------------------------------------------------------- set 3: a country railway platform and a steam train
def make_car(tr, cx, body='4E3A2C'):
    add('cube', '2A2622', (cx, 0, 0.55), scale=(11.6, 2.3, 0.7), size=1, parent=tr)
    add('cube', body, (cx, 0, 0.98), scale=(12, 2.7, 0.16), size=1, parent=tr)
    for s in (-1, 1):
        add('cube', body, (cx, s * 1.32, 1.5), scale=(12, 0.08, 0.95), size=1, parent=tr)
        add('cube', 'C8B88E', (cx, s * 1.33, 2.0), scale=(12, 0.07, 0.09), size=1, parent=tr)
        add('cube', body, (cx, s * 1.32, 3.42), scale=(12, 0.08, 0.5), size=1, parent=tr)
        for i in range(9):
            add('cube', body, (cx - 6 + i * 1.5, s * 1.32, 2.6), scale=(0.22, 0.08, 1.3), size=1, parent=tr)
    for e in (-1, 1):
        add('cube', body, (cx + e * 5.96, 0, 2.3), scale=(0.08, 2.7, 2.7), size=1, parent=tr)
        add('cube', '2A2622', (cx + e * 3.8, 0, 0.18), scale=(2.6, 2.0, 0.36), size=1, parent=tr)
    add('cube', '3A3A40', (cx, 0, 3.76), scale=(12.3, 2.9, 0.2), size=1, parent=tr)
    add('cube', '45454C', (cx, 0, 3.92), scale=(12.0, 1.8, 0.16), size=1, parent=tr)
    add('cube', 'FFD9A0', (cx, 0, 3.6), scale=(11, 0.5, 0.05), size=1, parent=tr, emit=4)
    for i in range(7):
        add('cube', '5A6A4A', (cx - 4.5 + i * 1.5, 0.75, 1.5), scale=(0.16, 1.0, 1.0), size=1, parent=tr)


def set_rail(r):
    add('plane', '6E8456', (0, 0, -0.02), size=2400, parent=r)
    add('cube', '8A8478', (0, -1, 0.5), scale=(90, 6, 1.0), size=1, parent=r)
    add('cube', 'C8C0A8', (0, 1.85, 1.01), scale=(90, 0.3, 0.03), size=1, parent=r)
    for i in range(-22, 23):
        add('cube', '6A665C', (i * 2.0, -1, 1.005), scale=(0.05, 6, 0.02), size=1, parent=r)
    add('cube', '6E6456', (0, 5, 0.06), scale=(260, 3.4, 0.14), size=1, parent=r)
    for i in range(-60, 61):
        add('cube', '3E3026', (i * 1.6, 5, 0.15), scale=(0.34, 2.9, 0.12), size=1, parent=r)
    for y in (4.28, 5.72):
        add('cube', '9AA0A8', (0, y, 0.27), scale=(260, 0.1, 0.14), size=1, parent=r, rough=0.3)
    for i in range(-20, 21):                               # the back fence
        add('cube', ('5E4A36', '6A543C')[i % 2], (i * 0.62, -4.05, 2.05), scale=(0.56, 0.1, 2.1), size=1, parent=r)
    add('cube', '4A3A2A', (0, -4.0, 2.7), scale=(26, 0.16, 0.14), size=1, parent=r)
    for x in (-12, -4, 4, 12):                             # canopy
        add('cube', '3E3A36', (x, -2.9, 3.1), scale=(0.24, 0.24, 4.2), size=1, parent=r)
        add('cube', '3E3A36', (x, -1.4, 5.0), rot=(0.5, 0, 0), scale=(0.16, 3.2, 0.16), size=1, parent=r)
    add('cube', '4E4A46', (0, -1.6, 5.45), rot=(0.12, 0, 0), scale=(30, 5.4, 0.16), size=1, parent=r)
    add('cube', '2E2A28', (0, 1.0, 5.1), scale=(30, 0.12, 0.3), size=1, parent=r)
    lamp = empty((1.7, -0.6, 5.3), r)
    add('cylinder', '2A2A2A', (0, 0, -0.35), radius=0.03, depth=0.7, vertices=4, parent=lamp)
    add('cone', '2E3A34', (0, 0, -0.78), radius1=0.5, radius2=0.1, depth=0.26, vertices=8, parent=lamp)
    bulb = add('ico_sphere', 'FFC878', (0, 0, -0.95), radius=0.14, subdivisions=1, parent=lamp)
    bmat = own_mat('bulb', 'FFC878', 0.5, 9)
    use(bulb, bmat)
    lamplight = light((0, 0, -1.15), 0, 'FFB868', kind='POINT', parent=lamp)
    clock = empty((-2.6, -1.0, 4.35), r)                   # the platform clock
    add('cylinder', '2E2A28', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.62, depth=0.2, vertices=12, parent=clock)
    add('cylinder', 'EFE6CC', (0, 0.11, 0), rot=(PI / 2, 0, 0), radius=0.52, depth=0.02, vertices=12, parent=clock, emit=0.6)
    add('cube', '1A1A1A', (0.0, 0.13, 0.16), scale=(0.05, 0.02, 0.34), size=1, parent=clock)
    add('cube', '1A1A1A', (0.13, 0.13, 0.0), scale=(0.26, 0.02, 0.05), size=1, parent=clock)
    add('cylinder', '2A2A2A', (0, 0, 0.8), radius=0.03, depth=0.6, vertices=4, parent=clock)
    bench = empty((-1.9, -3.3, 1.0), r)
    add('cube', '7A5A3A', (0, 0, 0.62), scale=(3.0, 0.8, 0.1), size=1, parent=bench)
    add('cube', '7A5A3A', (0, -0.36, 1.2), rot=(-0.12, 0, 0), scale=(3.0, 0.1, 0.8), size=1, parent=bench)
    for x in (-1.3, 1.3):
        add('cube', '2E2A28', (x, 0, 0.3), scale=(0.12, 0.7, 0.6), size=1, parent=bench)
    board = empty((4.6, -3.9, 3.3), r)                     # the station name board: left blank on purpose
    add('cube', '2E2A28', (0, 0, 0), scale=(3.2, 0.1, 1.3), size=1, parent=board)
    add('cube', 'E8DEC0', (0, 0.06, 0), scale=(2.9, 0.04, 1.0), size=1, parent=board)
    for x in (-1.3, 1.3):
        add('cube', '2E2A28', (x, 0, -1.2), scale=(0.14, 0.12, 1.3), size=1, parent=board)
    for x, s in ((7.5, 1.0), (8.4, 0.7)):                  # luggage left on the platform
        add('cube', '6A4A2E', (x, -3.0, 1.0 + 0.4 * s), scale=(1.1 * s, 0.7 * s, 0.8 * s), size=1, parent=r)
    for i in range(-5, 6):
        add('cylinder', '4A3A2A', (i * 16.0 + 5, 8.6, 3.4), radius=0.13, depth=6.8, vertices=6, parent=r)
        add('cube', '4A3A2A', (i * 16.0 + 5, 8.6, 6.3), scale=(0.12, 1.6, 0.12), size=1, parent=r)
    hillmat = own_mat('hill', '3E5A4A', 0.95)
    for side in (1, -1):
        for i in range(13):
            a = i / 12
            o = add('cone', '000000', (-520 + a * 1040 + (i * 37) % 30, side * (230 + (i % 3) * 70), 34 + (i * 19) % 40),
                    radius1=120 + (i % 4) * 26, radius2=8, depth=90 + (i * 29) % 70, vertices=7, parent=r)
            use(o, hillmat)
    for i in range(9):                                     # paddies and a few farm roofs beyond the line
        add('cube', ('5E7A46', '6A8650')[i % 2], (-80 + i * 20, 40 + (i % 2) * 14, 0.05), scale=(18, 12, 0.1), size=1, parent=r)
    for x, y in ((-30, 60), (26, 74), (58, 52), (-64, -40), (40, -46)):
        add('cube', '8E8676', (x, y, 2.4), scale=(9, 7, 4.8), size=1, parent=r)
        add('cone', '4A4844', (x, y, 6.0), rot=(0, 0, PI / 4), radius1=7.5, radius2=0, depth=3, vertices=4, parent=r)
    train = empty((-300, 5, 0.34), r)
    lo = empty((20, 0, 0), train)                          # a plain black tank engine: no number, no plate
    add('cylinder', '1E2024', (0.8, 0, 2.15), rot=(0, PI / 2, 0), radius=1.12, depth=6.2, vertices=10, parent=lo, rough=0.5)
    add('cylinder', '2A2C30', (4.0, 0, 2.15), rot=(0, PI / 2, 0), radius=1.16, depth=0.3, vertices=10, parent=lo)
    add('cube', '1E2024', (-3.4, 0, 2.4), scale=(2.4, 2.7, 3.0), size=1, parent=lo)
    add('cube', '2E3034', (-3.4, 0, 4.0), scale=(2.8, 2.9, 0.18), size=1, parent=lo)
    add('cube', 'FFC878', (-2.9, 0, 3.0), scale=(1.0, 2.74, 0.7), size=1, parent=lo, emit=1.5)
    add('cylinder', '1E2024', (2.9, 0, 3.75), radius=0.36, depth=1.2, vertices=8, parent=lo)
    add('cylinder', '2E3034', (2.9, 0, 4.4), radius=0.46, depth=0.16, vertices=8, parent=lo)
    add('ico_sphere', '2A2C30', (0.6, 0, 3.3), radius=0.5, subdivisions=1, parent=lo)
    add('cube', '1E2024', (0, 0, 0.75), scale=(8.6, 2.5, 0.5), size=1, parent=lo)
    add('cube', '8A2E22', (4.5, 0, 0.6), scale=(0.3, 2.7, 0.5), size=1, parent=lo)
    add('cylinder', 'FFE0A0', (4.2, 0, 3.0), rot=(0, PI / 2, 0), radius=0.26, depth=0.2, vertices=8, parent=lo, emit=10)
    wheels = []
    for s in (-1, 1):
        for x in (-1.9, 0.2, 2.3):
            w = add('cylinder', '8A2E22', (x, s * 1.05, 0.72), rot=(PI / 2, 0, 0), radius=0.74, depth=0.2, vertices=10, parent=lo)
            add('cube', '1E2024', (0, 0, 0.11 * s), scale=(1.2, 0.16, 0.05), size=1, parent=w)
            wheels.append(w)
        add('cube', '9AA0A8', (0.2, s * 1.2, 0.72), scale=(4.6, 0.08, 0.12), size=1, parent=lo, rough=0.3)
    add('cube', '1E2024', (12.6, 0, 1.9), scale=(4.6, 2.6, 2.6), size=1, parent=train)
    add('cube', '15161A', (12.6, 0, 3.3), scale=(4.2, 2.2, 0.3), size=1, parent=train)
    for cx in (3.5, -9.0, -21.5):
        make_car(train, cx)
    tgt = empty((0, 0, 1.5), r)
    sun = light((0, 0, 100), 2.0, 'FFE0C0', kind='SUN', target=tgt, parent=r)
    moon = add('circle', 'E6EEFF', FAR, rot=(PI / 2, 0, 0), radius=16, vertices=20, fill_type='NGON', parent=r, emit=4)
    return dict(train=mov(train), wheels=wheels, railsun=sun, bulbmat=bmat, lamplight=lamplight, hillmat=hillmat, moon=mov(moon))


# ---------------------------------------------------------------- set 4: the drawing office, Nagasaki
def set_office(r):
    add('cube', '6E5238', (0, 0, -0.1), scale=(16.4, 14.4, 0.2), size=1, parent=r)
    for i in range(-11, 12):
        add('cube', '5A422C', (i * 0.7, 0, 0.005), scale=(0.04, 14, 0.02), size=1, parent=r)
    add('cube', 'A8A08C', (0, 0, 5.7), scale=(16.4, 14.4, 0.2), size=1, parent=r)
    wall = 'B8B09A'
    add('cube', wall, (0, 7.1, 0.65), scale=(16.4, 0.3, 1.3), size=1, parent=r)
    add('cube', wall, (0, 7.1, 5.0), scale=(16.4, 0.3, 1.3), size=1, parent=r)
    for x in (-7.6, -2.6, 2.6, 7.6):
        add('cube', wall, (x, 7.1, 2.85), scale=(1.2 if abs(x) > 3 else 1.4, 0.3, 3.1), size=1, parent=r)
    add('cube', '5A4630', (0, 6.9, 1.32), scale=(16, 0.5, 0.1), size=1, parent=r)
    for s in (-1, 1):
        add('cube', wall, (s * 8.1, 0, 2.8), scale=(0.3, 14.4, 5.8), size=1, parent=r)
    add('cube', wall, (0, -7.1, 2.8), scale=(16.4, 0.3, 5.8), size=1, parent=r)
    add('cube', '5A4630', (0, 0, 0.3), scale=(16.1, 14.1, 0.02), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '5A4630', (s * 7.93, 0, 0.3), scale=(0.06, 14, 0.6), size=1, parent=r)
    add('cube', '5A4630', (0, -6.93, 0.3), scale=(16, 0.06, 0.6), size=1, parent=r)
    add('cube', '4A3826', (5.4, -6.9, 2.2), scale=(2.0, 0.12, 4.2), size=1, parent=r)                 # the door
    add('ico_sphere', 'C8A040', (4.7, -6.8, 2.1), radius=0.09, subdivisions=1, parent=r, rough=0.3)
    panemat = own_mat('pane', 'CFE4F2', 0.4, 2.2)
    panes, mull = [], []
    for x in (-5.1, 0.0, 5.1):
        p = add('plane', '000000', (x, 7.3, 2.85), rot=(PI / 2, 0, 0), size=1, scale=(3.8, 3.2, 1), parent=r)
        panes.append(use(p, panemat))
        for dx in (-1.2, 0.0, 1.2):
            mull.append(mov(add('cube', '4A3E30', (x + dx, 6.98, 2.85), scale=(0.09, 0.09, 3.1), size=1, parent=r)))
        for dz in (-0.75, 0.75):
            mull.append(mov(add('cube', '4A3E30', (x, 6.98, 2.85 + dz), scale=(3.7, 0.09, 0.09), size=1, parent=r)))
    winlight = light((0, 6.2, 3.2), 900, 'E8F2FF', 7.0, empty((0, 0, 1.2), r), parent=r)
    for i, (x, y) in enumerate(((-5.2, 3.4), (-1.6, 3.4), (-5.2, -0.4), (-1.6, -0.4))):   # four drawing tables
        tb = empty((x, y, 0), r)
        add('cube', '8A6A44', (0, 0.1, 1.95), rot=(0.42, 0, 0), scale=(2.7, 1.9, 0.09), size=1, parent=tb)
        add('cube', 'EEF2F4', (0.05, 0.08, 2.0), rot=(0.42, 0, 0), scale=(2.2, 1.5, 0.02), size=1, parent=tb, emit=0.25)
        add('cube', '6A8AA8', (0.05, 0.1, 2.02), rot=(0.42, 0, 0), scale=(1.6, 0.03, 0.02), size=1, parent=tb)
        add('cube', '6A8AA8', (-0.3, 0.2, 2.07), rot=(0.42, 0, 0), scale=(0.03, 0.9, 0.02), size=1, parent=tb)
        add('cube', 'C8A868', (0, -0.45, 1.8), rot=(0.42, 0, 0), scale=(2.5, 0.09, 0.05), size=1, parent=tb)
        for sx in (-1.1, 1.1):
            add('cube', '4A3826', (sx, 0.55, 1.05), scale=(0.1, 0.1, 2.1), size=1, parent=tb)
            add('cube', '4A3826', (sx, -0.5, 0.82), scale=(0.1, 0.1, 1.64), size=1, parent=tb)
        add('cube', '4A3826', (0, 0, 0.5), scale=(2.2, 0.08, 0.08), size=1, parent=tb)
        add('cylinder', '4A3826', (0, -1.25, 0.6), radius=0.34, depth=0.08, vertices=8, parent=tb)
        add('cylinder', '3A2C1E', (0, -1.25, 0.3), radius=0.06, depth=0.6, vertices=5, parent=tb)
    desk = empty((4.9, 3.2, 0), r)                         # the boss's desk
    add('cube', '5A3E28', (0, 0, 1.36), scale=(3.6, 1.7, 0.12), size=1, parent=desk)
    for sx in (-1.3, 1.3):
        add('cube', '4A3220', (sx, 0, 0.66), scale=(0.9, 1.6, 1.3), size=1, parent=desk)
    add('cube', 'EEF2F4', (-0.5, -0.2, 1.43), rot=(0, 0, 0.2), scale=(0.9, 0.65, 0.02), size=1, parent=desk, emit=0.2)
    add('cube', 'D8D0B8', (0.5, 0.2, 1.47), rot=(0, 0, -0.3), scale=(0.7, 0.5, 0.1), size=1, parent=desk)
    add('cylinder', '2A2A2A', (1.35, 0.4, 1.7), radius=0.04, depth=0.6, vertices=5, parent=desk)
    add('cone', 'FF7A1A', (1.35, 0.3, 2.05), radius1=0.34, radius2=0.12, depth=0.3, vertices=8, parent=desk, emit=1.2)
    add('cube', '1E1E22', (-1.3, 0.35, 1.52), scale=(0.5, 0.36, 0.2), size=1, parent=desk)
    for i, x in enumerate((6.6, 7.4)):
        add('cube', ('5E6A62', '56625A')[i], (x, 6.2 - i * 0.02, 1.5), scale=(0.75, 1.0, 2.6), size=1, parent=r)
        for z in (0.7, 1.5, 2.3):
            add('cube', 'C8A040', (x, 5.68, z), scale=(0.3, 0.03, 0.06), size=1, parent=r, rough=0.3)
    for i, (y, z, c) in enumerate(((3.6, 3.1, '3A5E8A'), (1.2, 3.3, '44689A'), (-1.4, 3.0, '3A5E8A'))):   # blueprints on the wall
        add('cube', c, (-7.93, y, z), scale=(0.03, 1.9, 1.3), size=1, parent=r)
        for j in range(3):
            add('cube', 'DCE8F4', (-7.9, y, z - 0.4 + j * 0.36), scale=(0.02, 1.5 - j * 0.3, 0.03), size=1, parent=r, emit=0.3)
    clock = empty((7.93, -0.6, 4.3), r, (0, 0, 0))
    add('cylinder', '3A2C1E', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.6, depth=0.14, vertices=12, parent=clock)
    add('cylinder', 'EFE6CC', (-0.08, 0, 0), rot=(0, PI / 2, 0), radius=0.5, depth=0.02, vertices=12, parent=clock, emit=0.5)
    add('cube', '1A1A1A', (-0.1, 0.04, 0.12), rot=(-0.3, 0, 0), scale=(0.02, 0.05, 0.3), size=1, parent=clock)
    add('cube', '1A1A1A', (-0.1, 0.0, 0.2), scale=(0.02, 0.04, 0.44), size=1, parent=clock)
    add('cube', '4A3826', (-6.9, -5.6, 1.1), scale=(1.6, 2.2, 2.2), size=1, parent=r)                 # plan chest
    for z in (0.5, 1.0, 1.5):
        add('cube', '2E2218', (-6.08, -5.6, z), scale=(0.03, 2.0, 0.04), size=1, parent=r)
    for i in range(4):
        add('cylinder', 'EEF2F4', (-7.0 + i * 0.22, -5.2 - i * 0.2, 2.6), rot=(0.1 * i, 0.12, 0), radius=0.09, depth=0.9, vertices=6, parent=r)
    lamps = []
    for x, y in ((-3.4, 1.4), (3.2, 1.4), (0, -3.6)):
        add('cylinder', '2A2A2A', (x, y, 5.1), radius=0.03, depth=1.0, vertices=4, parent=r)
        add('cone', '3E5A4A', (x, y, 4.55), radius1=0.6, radius2=0.12, depth=0.3, vertices=8, parent=r)
        add('ico_sphere', 'FFE2B0', (x, y, 4.42), radius=0.13, subdivisions=1, parent=r, emit=8)
        lamps.append(light((x, y, 4.2), 260, 'FFDDB0', kind='POINT', parent=r))
    return dict(panemat=panemat, panes=panes, mull=mull, winlight=winlight, olamps=lamps)


# ---------------------------------------------------------------- set 5: a lecture hall, many years later
def set_hall(r):
    add('cube', '2A2230', (0, 0, -0.1), scale=(26, 34, 0.2), size=1, parent=r)
    add('cube', '6A4A30', (0, 9.5, 0.5), scale=(20, 9, 1.0), size=1, parent=r)
    add('cube', '8A6A44', (0, 5.02, 0.5), scale=(20, 0.06, 1.0), size=1, parent=r)
    for i in range(21):
        add('cube', ('1E2A52', '26346A')[i % 2], (-10 + i * 1.0, 13.4 + (i % 2) * 0.25, 4.6), scale=(1.02, 0.3, 9.4), size=1, parent=r)
    for s in (-1, 1):
        add('cube', '241C2A', (s * 12.6, 0, 5), scale=(0.4, 34, 10), size=1, parent=r)
        for i in range(4):
            add('cube', 'FFC070', (s * 12.3, -9 + i * 6, 5.6), scale=(0.1, 0.5, 1.0), size=1, parent=r, emit=3)
    add('cube', '1A1622', (0, 0, 10), scale=(26, 34, 0.3), size=1, parent=r)
    add('cube', '241C2A', (0, -16.8, 5), scale=(26, 0.4, 10), size=1, parent=r)
    lec = empty((0, 6.3, 1.0), r)                          # the lectern and its microphone
    add('cube', '7A5634', (0, 0, 0.8), scale=(1.5, 0.75, 1.6), size=1, parent=lec)
    add('cube', '8E6840', (0, 0.05, 1.66), rot=(0.3, 0, 0), scale=(1.7, 0.95, 0.1), size=1, parent=lec)
    add('cube', 'FF7A1A', (0, -0.385, 1.25), scale=(1.5, 0.02, 0.12), size=1, parent=lec, emit=0.6)
    add('cylinder', '1A1A1E', (0.42, -0.1, 1.98), rot=(0.5, 0, 0), radius=0.022, depth=0.75, vertices=5, parent=lec)
    add('ico_sphere', '2A2A30', (0.42, -0.3, 2.3), radius=0.085, subdivisions=1, parent=lec, rough=0.4)
    add('cube', 'EEF2F4', (-0.2, 0.0, 1.73), rot=(0.3, 0, 0.1), scale=(0.6, 0.45, 0.02), size=1, parent=lec, emit=0.3)
    for i in range(3):                                     # a row of flowers at the stage edge
        add('ico_sphere', ('E8E0D0', 'F0C8A0', 'E8E0D0')[i], (-6 + i * 6.0, 5.5, 1.3), scale=(1.4, 0.6, 0.6), radius=0.6, subdivisions=1, parent=r)
        add('cube', '3A5A3A', (-6 + i * 6.0, 5.5, 1.08), scale=(1.8, 0.5, 0.2), size=1, parent=r)
    for row in range(6):                                   # seats and an audience kept as plain silhouettes
        y = 1.5 - row * 2.4
        for j in range(-6, 7):
            if j == 0:
                continue
            x = j * 1.45 + (0.35 if j > 0 else -0.35)
            add('cube', ('5E2228', '54202A')[(row + j) % 2], (x, y - 0.42, 0.95), scale=(1.2, 0.2, 1.5), size=1, parent=r)
            add('cube', '4A1A20', (x, y, 0.62), scale=(1.2, 0.9, 0.16), size=1, parent=r)
            if (row * 7 + j * 3) % 5 != 0 and not (row == 2 and j == 1):
                c = ('1E2230', '262A3A', '2C2630')[(row + j) % 3]
                add('cube', c, (x, y - 0.05, 1.35), scale=(0.95, 0.42, 1.0), size=1, parent=r)
                add('ico_sphere', ('2A2428', '4A4650', '1A1A20')[(row * 3 + j) % 3], (x, y - 0.02, 2.2), radius=0.3, subdivisions=1, parent=r)
    aim = empty((0, 7.2, 2.8), r)
    spot = light((2.5, 0.5, 9.0), 5200, 'FFF2DC', 2.4, aim, parent=r)
    light((-7, 4, 6), 420, 'FF7A1A', 3.0, aim, parent=r)
    light((0, -8, 7), 500, '6E8FD8', 6.0, empty((0, -2, 1.5), r), parent=r)
    return dict(spot=spot)


# ---------------------------------------------------------------- props
def make_plane():
    """A four-engined aircraft seen from far below: a plain silver shape, no markings."""
    p = empty(FAR)
    add('cylinder', 'D8DEE6', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.6, depth=9, vertices=6, parent=p, emit=2.5, rough=0.2)
    add('cube', 'D8DEE6', (0.6, 0, 0), scale=(1.5, 13, 0.14), size=1, parent=p, emit=2.5, rough=0.2)
    add('cube', 'D8DEE6', (-4.0, 0, 0.1), scale=(0.9, 4.2, 0.1), size=1, parent=p, emit=2.5)
    add('cube', 'D8DEE6', (-4.1, 0, 0.7), scale=(1.1, 0.1, 1.3), size=1, parent=p, emit=2.5)
    for y in (-4, -2, 2, 4):
        add('cylinder', 'AEB6C0', (1.3, y, 0), rot=(0, PI / 2, 0), radius=0.3, depth=1.3, vertices=6, parent=p, emit=1.5)
    return p


def make_chute():
    c = empty(FAR)
    add('ico_sphere', 'F4F4F0', (0, 0, 0), scale=(1, 1, 0.6), radius=1.0, subdivisions=1, parent=c, emit=2.5)
    add('cube', '3A3A3A', (0, 0, -1.6), scale=(0.3, 0.3, 0.8), size=1, parent=c)
    return c


def make_crane():
    """A folded paper crane. Rook leaves it; this is the one case he takes nothing from."""
    c = empty(FAR)
    kw = dict(parent=c, emit=1.6, rough=0.6)
    add('cone', 'FFF4E0', (0, 0, 0.05), rot=(0, PI / 2, 0), scale=(0.5, 1, 1), radius1=0.16, radius2=0.0, depth=0.5, vertices=4, **kw)
    add('cone', 'FFF4E0', (0.22, 0, 0.22), rot=(0, 0.5, 0), scale=(1, 0.35, 1), radius1=0.06, radius2=0.0, depth=0.5, vertices=4, **kw)
    add('cone', 'FF7A1A', (0.36, 0, 0.42), rot=(0, 2.1, 0), scale=(1, 0.35, 1), radius1=0.045, radius2=0.0, depth=0.18, vertices=4, **kw)
    add('cone', 'FFF4E0', (-0.26, 0, 0.2), rot=(0, -0.6, 0), scale=(1, 0.35, 1), radius1=0.06, radius2=0.0, depth=0.46, vertices=4, **kw)
    for s in (-1, 1):
        add('cone', 'FFE8C8', (0, s * 0.24, 0.16), rot=(s * -1.15, 0, 0), scale=(1, 0.12, 1), radius1=0.22, radius2=0.0, depth=0.52, vertices=4, **kw)
    return c


def wrap_yama(rig):
    """Bandages: head, and the left arm and shoulder (his burns were to the left side of his upper body)."""
    out = [add('ico_sphere', 'F4F2EA', (0, 0.04, 0.24), scale=(1, 1, 0.5), radius=0.285, subdivisions=1, parent=rig.head, emit=0.15),
           add('cylinder', 'F4F2EA', (0, 0.01, 0.235), radius=0.3, depth=0.13, vertices=8, parent=rig.head, emit=0.15),
           add('cylinder', 'F4F2EA', (0, 0, -0.23), radius=0.105, depth=0.44, vertices=6, parent=rig.sh[1], emit=0.15),
           add('cylinder', 'F4F2EA', (0, 0, -0.2), radius=0.1, depth=0.42, vertices=6, parent=rig.el[1], emit=0.15),
           add('cube', 'F4F2EA', (0.2, -0.02, 0.86), rot=(0, 0.5, 0), scale=(0.62, 0.74, 0.07), size=1, parent=rig.body, emit=0.15)]
    return out


def hair_head(skin, hair, glasses=False, grey=False):
    base = K.human_head(skin, hair)

    def fn(head):
        out = base(head)
        if glasses:
            for s in (-1, 1):
                add('torus', '1A1A1E', (s * 0.105, -0.3, 0.04), rot=(PI / 2, 0, 0), major_radius=0.075, minor_radius=0.014, major_segments=8,
                    minor_segments=3, parent=head)
            add('cube', '1A1A1E', (0, -0.3, 0.05), scale=(0.07, 0.015, 0.015), size=1, parent=head)
        return out
    return fn


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    _MOV.clear()
    S = dict(colls={})
    for name, fn in (('hiro', set_hiro), ('shelter', set_shelter), ('rail', set_rail), ('office', set_office), ('hall', set_hall)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['yama'] = K.Rig(YAMA, hair_head(SKIN, '17131A'))
    S['wraps'] = wrap_yama(S['yama'])
    S['bag'] = add('cube', '5A4630', (-0.5, 0.05, -0.1), scale=(0.16, 0.5, 0.42), size=1, parent=S['yama'].body)
    S['boss'] = K.Rig(BOSS, hair_head('C99868', '3A3A40', glasses=True))
    add('cube', 'E8E4DA', (0, -0.3, 0.86), scale=(0.2, 0.05, 0.4), size=1, parent=S['boss'].body)
    add('cube', '5A1E22', (0, -0.33, 0.8), scale=(0.07, 0.03, 0.36), size=1, parent=S['boss'].body)
    S['men'] = [K.Rig(c, hair_head('D0A070', '1A1616')) for c in MEN]
    S['old'] = K.Rig(OLD, hair_head('D2A882', 'E4E4E8', glasses=True))
    add('cube', 'E8E4DA', (0, -0.3, 0.86), scale=(0.2, 0.05, 0.4), size=1, parent=S['old'].body)
    add('cube', '3A4A6A', (0, -0.33, 0.8), scale=(0.07, 0.03, 0.36), size=1, parent=S['old'].body)
    S['cast'] = [S['rook'], S['yama'], S['boss'], S['old']] + S['men']
    S['plane'] = mov(make_plane())
    S['chutes'] = [mov(make_chute()) for _ in range(2)]
    S['crane'] = mov(make_crane())
    S['ball'] = mov(add('ico_sphere', 'FFFFFF', FAR, radius=1.0, subdivisions=2, emit=40))
    S['column'] = mov(empty(FAR))
    add('cone', '9C8470', (0, 0, 95), radius1=46, radius2=26, depth=190, vertices=9, parent=S['column'])
    for i, (x, z, rr) in enumerate(((0, 205, 84), (-52, 190, 52), (56, 196, 56), (10, 238, 50))):
        add('ico_sphere', ('A68E78', '9C8470')[i % 2], (x, 0, z), scale=(1, 1, 0.6), radius=rr, subdivisions=2, parent=S['column'])
    add('ico_sphere', '94806C', (0, 0, 10), scale=(1, 1, 0.22), radius=130, subdivisions=2, parent=S['column'])
    S['dust'] = [mov(add('ico_sphere', ('A89474', '98866A', 'B8A486')[i % 3], FAR, radius=1.0, subdivisions=1)) for i in range(12)]
    S['bits'] = [mov(add('cube', ('5A4A38', '3E3A36', '7A6A54')[i % 3], FAR, scale=(0.3 + i % 3 * 0.12, 0.1, 0.04), size=1)) for i in range(14)]
    S['papers'] = [mov(add('cube', 'F2F0E6', FAR, scale=(0.5, 0.36, 0.01), size=1, emit=0.35)) for _ in range(16)]
    S['puffs'] = [mov(add('ico_sphere', 'D8D8DC', FAR, radius=1.0, subdivisions=1, emit=0.15)) for _ in range(8)]
    S['fea'] = [mov(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(3)]
    S['glow'] = light(FAR, 0, 'FFFFFF', kind='POINT')
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 5000
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


def cam(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='FFFFFF'):
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
    for o in S['wraps']:
        o.hide_render = True
    S['bag'].hide_render = True
    S['glow'].location = FAR
    S['glow'].data.energy = 0
    S['glow'].data.color = (1, 1, 1)
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    tint(S['panemat'], 'CFE4F2', 2.2)
    S['winlight'].data.energy = 900
    S['winlight'].data.color = K.hexc('E8F2FF')[:3]
    for l in S['olamps']:
        l.data.energy = 260
    S['lanlight'].data.energy = 420
    S['lamplight'].data.energy = 0
    tint(S['bulbmat'], 'FFC878', 0.0)
    S['sun'].data.energy = 3.6
    S['sun'].data.color = K.hexc('FFF4DC')[:3]
    S['spot'].data.energy = 5200
    S['face'] = dict(rook='calm', yama='calm', boss='calm', old='calm', men='calm')
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
    S['jaw'] = {}
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
    r['hat'].location = (lerp(0.0, 0.0, off), lerp(0.0, -0.5, off), lerp(0.27 + (0.13 if e == 'shocked' else 0.0) + tip * 0.1, -0.92, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for who, rigs in (('yama', [S['yama']]), ('boss', [S['boss']]), ('old', [S['old']]), ('men', S['men'])):
        k = dict(scared=1.3, shock=1.7, calm=1.0, tired=0.5, warm=0.8, shut=0.12).get(S['face'][who], 1.0)
        for rig in rigs:
            for ey in rig.extra['eyes']:
                ey.scale = (ey.scale[0], ey.scale[1], 0.075 * k)
            rig.extra['jaw'].rotation_euler = (S['jaw'].get(who, 0.0), 0, 0)


def hat_hold(**over):
    """Hat held to the chest with both hands."""
    d = dict(aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.22, 0.0))
    d.update(over)
    return P('stand', **d)


def bandaged(S, on=True):
    for o in S['wraps']:
        o.hide_render = not on


def drift_dust(S, A, t, org, n=10, spread=14.0, size=2.2, speed=2.0, dirn=(0.0, -1.0), up=0.3):
    for i in range(n):
        o = S['dust'][i]
        u = (t * speed * 0.11 + i * 0.37) % 1
        side = ((i * 0.618) % 1 - 0.5) * spread
        o.location = A(org[0] + side, org[1] - u * spread * 0.5 + (i % 3) * 4, org[2] + 0.5 + (i % 3) * 0.4 + up * u * 3)
        s = size * (0.5 + 0.5 * u) * (0.7 + (i % 4) * 0.12)
        o.scale = (s * 1.5, s * 1.2, s * 0.6)


def fall_bits(S, A, t, org, n=12, spread=9.0, speed=1.0, hgt=7.0):
    for i in range(n):
        o = S['bits'][i]
        u = (t * speed * 0.22 + i * 0.29) % 1
        o.location = A(org[0] + ((i * 0.618) % 1 - 0.5) * spread + 0.5 * math.sin(t * 2 + i), org[1] + ((i * 0.37) % 1 - 0.5) * spread,
                       org[2] + hgt * (1 - u))
        o.rotation_euler = (t * 3 + i, t * 2.2 + i * 2, i)


# ---------------------------------------------------------------- shots: Hiroshima
def morning(S, f=0.0):
    """Summer morning over the delta; f (0..1) is the flash."""
    A = show(S, 'hiro')
    sky(S, mix_col('8EC4EC', 'FFFFFF', f), 1.0 + 2.2 * f)
    S['sun'].data.energy = 3.6 + 5 * f
    S['fillk'] = 6.0 + 9 * f
    return A


def after(S, t):
    """After the flash: a brown sky, dust on the ground, a far column of cloud."""
    A = show(S, 'hiro')
    sky(S, '8A6E56', 0.75)
    S['sun'].data.energy = 1.5
    S['sun'].data.color = K.hexc('FFB070')[:3]
    S['fillk'] = 9.0
    S['column'].location = A(-70, 620, 0)
    return A


def flash_city(S, k, t, lt):
    f = ease(lt / 0.9) * 0.55
    A = morning(S, f)
    S['ball'].location = A(-70, 430, 170)
    s = lerp(0.5, 120, ease(lt / 1.0))
    S['ball'].scale = (s, s, s)
    S['yama'].place(A(0.6, 10, 0), PI)
    S['yama'].apply(blend(walk(t, 1.5), P('stand', aL=(2.2, 0.3, 1.5), aR=(2.2, 0.3, 1.5), lean=-0.15), f))
    S['bag'].hide_render = False
    cam(S, A(lerp(3.5, 3.0, k), lerp(-12, -9, k), lerp(2.2, 2.6, k)), A(-6, 120, lerp(22, 30, k)), 26)


def yard_wide(S, k, t, lt):
    A = morning(S)
    y = lerp(8, 10.5, k)
    S['yama'].place(A(0.4, y, 0), PI)
    S['yama'].apply(walk(t, 1.5))
    S['bag'].hide_render = False
    cam(S, A(lerp(-3.6, -1.4, ease(k)), lerp(-9, 0.5, ease(k)), lerp(7.0, 3.6, ease(k))), A(lerp(3, 5, k), 60, lerp(4.5, 7.5, k)), 30)


def yama_walk(S, k, t, lt):
    A = morning(S)
    y = lerp(20, 23.4, k)
    S['yama'].place(A(-0.7, y, 0), PI)
    S['yama'].apply(walk(t, 1.5))
    S['bag'].hide_render = False
    S['rook'].place(A(1.3, y - 2.6, 0), PI + 0.1)
    look = 0.5 * math.sin(lt * 2.6)
    S['rook'].apply(dict(walk(t + 0.3, 1.5), head=(-0.05, look)))
    cam(S, A(2.4, y + 7.4, 2.5), A(0.2, y - 0.8, 2.3), 42)


def yama_cu(S, k, t, lt):
    A = morning(S)
    y = lerp(24, 26.4, k)
    S['yama'].place(A(-0.7, y, 0), PI)
    S['yama'].apply(dict(walk(t, 1.5), head=(-0.05, 0.25 * ease(lt / 0.8))))
    S['bag'].hide_render = False
    cam(S, A(lerp(-4.0, -3.4, k), y + 3.4, 2.5), A(-0.6, y + 0.3, 2.35), 46)


def rook_looks(S, k, t, lt):
    A = morning(S)
    up = ease((lt - 0.15) / 0.45)
    S['rook'].place(A(1.4, 27.6, 0), PI + 0.15)
    S['rook'].apply(blend(walk(t, 1.2), P('hat', head=(-0.5, 0.15), lean=-0.1), up))
    S['hat_tip'] = -0.2 * up
    S['yama'].place(A(-1.7, 29.4, 0), PI + 0.25)
    S['yama'].apply(P('stand', aR=(2.5, 0.5, 1.9, 0.3), head=(-0.55, 0.0), lean=-0.12))
    S['bag'].hide_render = False
    cam(S, A(lerp(3.4, 3.0, k), lerp(32.6, 32.0, k), lerp(1.5, 1.7, k)), A(1.45, 27.7, 2.6), 40)


def plane_high(S, k, t, lt):
    A = morning(S)
    S['yama'].place(A(-1.7, 29.4, 0), PI + 0.25)
    up = ease(lt / 0.4)
    S['yama'].apply(blend(P('stand'), P('stand', aR=(2.5, 0.5, 1.9, 0.3), head=(-0.55, 0.0), lean=-0.12), up))
    S['bag'].hide_render = False
    px = lerp(-30, 10, k)
    S['plane'].location = A(px, 150, 128)
    S['plane'].rotation_euler = (0, 0, 0.5)
    S['plane'].scale = (1.6, 1.6, 1.6)
    for i, c in enumerate(S['chutes']):
        c.location = A(px - 26 - i * 7, 138 - i * 5, 108 - 9 * k - i * 5)
        c.scale = (2.0, 2.0, 2.0)
    cam(S, A(lerp(-1.3, -1.0, k), lerp(25.6, 26.0, k), 1.3), A(lerp(-5, -3, k), 64, lerp(30, 34, k)), 30)


def flash_road(S, k, t, lt):
    f = ease(lt / 0.4) * 0.5
    A = morning(S, f)
    S['yama'].place(A(-0.7, 30, 0), PI + 0.15)
    S['yama'].apply(blend(P('stand', head=(-0.3, 0)), P('stand', aL=(2.1, -0.2, 1.7, 0.6), aR=(2.2, -0.2, 1.7, 0.6), head=(0.35, 0.3), lean=-0.2,
                                                         lL=(0.2, 0.3), lR=(-0.3, 0.2)), f))
    S['bag'].hide_render = False
    S['face']['yama'] = 'shut'
    S['rook'].place(A(1.4, 28.0, 0), PI + 0.2)
    S['rook'].apply(blend(P('stand'), P('stand', aR=(2.3, -0.3, 1.5, 0.8), aL=(0.4, 0.5, 0.6), head=(0.3, -0.5), lean=-0.25, lR=(-0.3, 0.2)), f))
    S['face']['rook'] = 'shocked' if lt < 0.35 else 'shut'
    S['glow'].location = A(-3, 44, 9)
    S['glow'].data.energy = 2500 * f
    cam(S, A(lerp(1.6, 1.2, k), lerp(37.5, 36.4, k), 2.3), A(0.3, 29, 2.5), 40)


def thrown(S, k, t, lt):
    A = after(S, t)
    sky(S, mix_col('FFFFFF', '9A7E62', ease(lt / 0.5)), lerp(4.0, 0.85, ease(lt / 0.5)))
    u = ease(lt / 0.7)
    S['yama'].place(A(-0.8, 30 - 3.2 * u, 0.15 + 1.1 * math.sin(u * PI) - 0.1 * u), PI + 0.2, pitch=1.25 * u)
    S['yama'].apply(P('stand', aL=(2.4, 0.5, 0.4), aR=(2.0, 0.6, 0.6), lL=(0.7, 0.9), lR=(0.2, 0.5), head=(0.3, 0)))
    S['bag'].hide_render = False
    S['face']['yama'] = 'shut'
    S['rook'].place(A(1.5, 28 - 2.2 * u, 0), PI + 0.3, pitch=0.3 * u)
    S['rook'].apply(P('stand', aL=(1.6, 0.9, 0.9), aR=(1.9, 0.8, 1.2), lL=(0.5, 0.6), lR=(-0.5, 0.3), lean=-0.2, head=(0.25, 0.2)))
    S['face']['rook'] = 'shocked'
    for i, f in enumerate(S['fea']):
        f.location = A(1.5 + 0.4 * i, 27.5 - 3.5 * u - i * 0.5, 2.6 + 0.7 * math.sin(u * PI) - u)
        f.rotation_euler = (u * 6 + i, u * 4, i)
    for i, o in enumerate(S['dust']):
        a = (i * 0.618) % 1
        o.location = A(3.5 + a * 9, 52 - 30 * ease(lt / 0.9) + (i % 4) * 3.5, 0.8 + (i % 3) * 0.9)
        s = 1.2 + (i % 3) * 0.5 + u
        o.scale = (s * 1.4, s * 1.4, s)
    for i, o in enumerate(S['bits']):
        a = (i * 0.37) % 1
        o.location = A(-3 + a * 9, 42 - 30 * (lt / 0.9) * (0.6 + a * 0.6), 0.6 + 3.0 * abs(math.sin(lt * 5 + i)))
        o.rotation_euler = (t * 9 + i, t * 7, i)
    cam(S, A(lerp(-4.9, -4.5, k), 22.0, 1.8), A(0.2, 29.4 - 2.8 * u, 1.9), 24)


def dust_rise(S, k, t, lt):
    A = after(S, t)
    u = ease((lt - 0.1) / 0.8)
    S['yama'].place(A(-0.3, 26.5, 0), PI - 0.35)
    S['yama'].apply(blend(P('stand', lL=(1.5, 2.2), lR=(0.2, 1.6), lift=-0.62, lean=0.95, aL=(1.1, 0.2, 0.3), aR=(1.1, 0.2, 0.3), head=(-0.5, 0)),
                          P('stand', lean=0.3, aL=(0.2, 0.2, 0.5), aR=(0.5, -0.3, 1.5, 1.0), head=(-0.2, 0.0), lL=(0.15, 0.2), lR=(-0.1, 0.1)), u))
    S['bag'].hide_render = False
    drift_dust(S, A, t, (-1, 44, 0), n=10, spread=22, size=1.8, speed=3.0)
    fall_bits(S, A, t, (-0.5, 30, 0), n=12, spread=8, speed=1.6)
    cam(S, A(lerp(3.4, 2.8, k), lerp(19.6, 20.4, k), lerp(1.4, 1.9, k)), A(-1.6, 30, lerp(3.4, 4.2, k)), 30)


def aftermath(S, k, t, lt):
    A = after(S, t)
    S['yama'].place(A(-0.6, 26.5, 0), PI * 0.5 + 0.5)
    S['yama'].apply(P('sit', lift=-0.92, lean=0.3, aL=(0.5, 0.0, 1.2, 0.5), aR=(0.9, -0.5, 1.6, 1.4), head=(0.4 - 0.1 * math.sin(lt * 3), 0.1)))
    S['face']['yama'] = 'tired'
    S['rook'].place(A(1.6, 26.0, 0), -PI * 0.5 + 0.2)
    S['hat_off'] = ease(lt / 0.5)
    S['rook'].apply(blend(P('stand', lL=(1.3, 2.1), lR=(0.1, 1.55), lift=-0.56, lean=0.25, head=(0.2, 0)),
                          hat_hold(lL=(1.3, 2.1), lR=(0.1, 1.55), lift=-0.56, lean=0.25, head=(0.3, 0.0)), ease(lt / 0.5)))
    S['face']['rook'] = 'sad'
    drift_dust(S, A, t, (0, 46, 0), n=8, spread=22, size=1.7, speed=1.6)
    fall_bits(S, A, t, (0.5, 26.5, 0), n=12, spread=7, speed=0.9, hgt=6)
    cam(S, A(lerp(0.9, 0.6, k), lerp(19.2, 20.4, k), 2.1), A(0.5, 26.3, 1.55), 42)


def yama_hurt(S, k, t, lt):
    A = after(S, t)
    S['yama'].place(A(-0.6, 26.5, 0), PI * 0.5 + 0.5)
    hold = ease(lt / 0.4)
    S['yama'].apply(blend(P('sit', lift=-0.92, lean=0.3, aL=(0.5, 0.0, 1.2, 0.5), aR=(0.9, -0.5, 1.6, 1.4), head=(0.4, 0.1)),
                          P('sit', lift=-0.92, lean=0.35, aL=(1.5, 0.75, 2.5, -0.4), aR=(0.9, -0.5, 1.6, 1.4), head=(0.3, -0.3)), hold))
    S['face']['yama'] = 'shut'
    drift_dust(S, A, t, (0, 46, 0), n=8, spread=22, size=1.7, speed=1.6)
    fall_bits(S, A, t, (0.5, 26.5, 0), n=12, spread=6, speed=1.1, hgt=5)
    cam(S, A(lerp(2.9, 2.5, k), lerp(29.3, 28.9, k), 1.5), A(-0.2, 26.7, 1.3), 44)


# ---------------------------------------------------------------- shots: the shelter
def shelter_base(S, t):
    A = show(S, 'shelter')
    sky(S, '05060A', 1.0)
    S['lan'].rotation_euler = (0.07 * math.sin(t * 2.3), 0.09 * math.sin(t * 1.7), 0)
    S['lanlight'].data.energy = 420 + 90 * math.sin(t * 11) + 50 * math.sin(t * 23)
    S['fillk'] = 0.9
    return A


def shelter_in(S, k, t, lt):
    A = shelter_base(S, t)
    S['yama'].place(A(-2.05, 2.6, 0.0), PI * 0.5)
    S['yama'].apply(P('sit', lift=-0.5, lean=0.42, aL=(0.6, 0.0, 1.3, 0.6), aR=(0.9, -0.45, 1.7, 1.4), head=(0.5 - 0.06 * math.sin(lt * 2.5), -0.2)))
    S['face']['yama'] = 'tired'
    S['wraps'][3].hide_render = False
    cam(S, A(lerp(1.5, 1.1, k), lerp(-2.6, -1.6, k), 2.0), A(-1.7, 2.7, 1.55), 34, fcol='FFC890')


def rook_shelter(S, k, t, lt):
    A = shelter_base(S, t)
    S['rook'].place(A(2.05, 2.2, 0.0), -PI * 0.5)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', lift=-0.5, lean=0.3, aL=(0.8, -0.2, 1.5, 1.0), aR=(0.8, -0.2, 1.5, 1.0), head=(0.32 + 0.05 * math.sin(lt * 2.2), 0.25)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-1.5, -1.2, k), lerp(-1.6, -1.0, k), 2.0), A(1.7, 2.3, 1.75), 40, fill=2.5, fcol='FFC890')


# ---------------------------------------------------------------- shots: the railway
def rail_mood(S, name):
    A = show(S, 'rail')
    if name == 'night':
        sky(S, '0E1630', 1.0)
        S['railsun'].data.energy = 0.25
        S['railsun'].data.color = K.hexc('8EA8E8')[:3]
        S['railsun'].location = (-60, 80, 100)
        tint(S['hillmat'], '1A2438')
        tint(S['bulbmat'], 'FFC878', 12)
        S['lamplight'].data.energy = 1500
        S['moon'].location = (120, -560, 210)
        S['fillk'] = 3.2
    else:
        sky(S, 'F0B090', 1.0)
        S['railsun'].data.energy = 2.6
        S['railsun'].data.color = K.hexc('FFC890')[:3]
        S['railsun'].location = (200, -90, 60)
        tint(S['hillmat'], '4E6E6A')
        S['fillk'] = 7.0
    return A


def steam(S, A, x, t, n=7):
    for i in range(n):
        o = S['puffs'][i]
        u = (t * 0.5 + i / n) % 1
        o.location = A(x + 22.9 - u * 16, 5 - u * 1.5, 5.3 + u * 6)
        s = 0.6 + 2.6 * u
        o.scale = (s, s, s * 0.8)


def roll(S, x):
    for w in S['wheels']:
        w.rotation_euler = (PI / 2, -x / 0.74, 0)


def train_wide(S, k, t, lt):
    A = rail_mood(S, 'dawn')
    x = lerp(-34, -18, k)
    S['train'].location = (x, 5, 0.34)
    roll(S, x)
    steam(S, A, x, t)
    cam(S, A(x + lerp(40, 37, k), lerp(19, 17, k), lerp(3.6, 4.4, k)), A(x + 17, 5, 3.4), 30)


def train_window(S, k, t, lt):
    A = rail_mood(S, 'dawn')
    x = lerp(-4.5, 0.6, k)
    S['train'].location = (x, 5, 0.34)
    roll(S, x)
    steam(S, A, x, t)
    S['yama'].root.parent = S['train']
    S['yama'].place((2.7, -0.72, 0.42), PI * 0.5)
    S['yama'].apply(P('sit', lift=-0.5, lean=0.1, head=(0.25, -0.75)))
    S['face']['yama'] = 'tired'
    bandaged(S)
    S['rook'].place(A(1.5, 0.3, 1.0), PI - 0.25)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.1, 0.3)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(3.3, 3.0, k), lerp(-3.4, -3.0, k), 3.2), A(1.3, 5, 3.0), 36, fill=2.2)


def rook_station(S, k, t, lt):
    A = rail_mood(S, 'night')
    S['rook'].place(A(0.2, -0.4, 1.0), PI + 0.15)
    S['rook'].apply(P('cross', head=(0.06, 0.1 + 0.3 * math.sin(lt * 9.0) * max(0.0, 1 - lt / 0.7))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(1.4, 1.0, k), lerp(6.2, 5.0, k), 3.3), A(0.15, -0.4, 3.45), 40, fcol='FFD0A0')


def rook_walk(S, k, t, lt):
    A = rail_mood(S, 'night')
    u = ease(lt / 0.3)
    x = lerp(0.5, 3.6, max(0.0, lt - 0.2) / 0.8)
    S['rook'].place(A(x, 0.2, 1.0), PI * 0.5)
    S['rook'].apply(blend(P('hat', aL=(0.2, 1.9, 1.6, -1.5)), walk(t, 2.0), ease((lt - 0.2) / 0.2)) if lt > 0.2 else
                    blend(P('stand'), P('hat', aL=(0.2, 1.9, 1.6, -1.5)), u))
    cam(S, A(lerp(-4.6, -3.8, k), lerp(1.2, 0.9, k), 2.0), A(x + 1.2, 0.0, 3.1), 30, fcol='FFD0A0')


def rook_wrong(S, k, t, lt):
    A = rail_mood(S, 'night')
    S['rook'].place(A(-0.6, 0.2, 1.0), PI - 0.2)
    off = ease((lt - 0.1) / 0.45)
    S['hat_off'] = off
    S['rook'].apply(blend(P('hat', head=(0.1, 0)), hat_hold(head=(0.28, 0.0)), off) if lt > 0.1 else blend(P('stand'), P('hat', head=(0.1, 0)), lt / 0.1))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-2.4, -2.0, k), lerp(4.2, 3.6, k), lerp(3.0, 3.2, k)), A(-0.6, 0.1, 3.2), 52, fill=2.2, fcol='FFD0A0')


def signoff(S, k, t, lt):
    A = rail_mood(S, 'night')
    S['rook'].place(A(-0.25, -2.5, 1.0), PI * 0.5 + 0.9)
    put = ease(lt / 0.5)
    tip = math.sin(PI * ease((lt - 0.6) / 0.8)) if lt > 0.6 else 0.0
    down = P('stand', aL=(1.0, 0.2, 0.25), lean=0.45, head=(0.35, 0.3), lL=(0.3, 0.5), lR=(0.3, 0.5), lift=-0.08)
    S['rook'].apply(blend(blend(P('stand', aL=(0.9, 0.2, 1.3)), down, math.sin(put * PI)), P('hat', head=(0.2, 0.25)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    S['crane'].location = A(lerp(-0.75, -1.5, put), lerp(-2.6, -3.25, put), lerp(2.75, 1.72, put))
    S['crane'].rotation_euler = (0, 0, 0.9 + 0.03 * math.sin(t * 3))
    S['crane'].scale = (1.5, 1.5, 1.5)
    S['glow'].location = A(-1.3, -2.6, 2.5)
    S['glow'].data.energy = 120
    S['glow'].data.color = K.hexc('FFD8A0')[:3]
    cam(S, A(lerp(1.3, 1.0, k), lerp(2.6, 1.6, k), 2.9), A(-0.9, -2.9, 2.55), 38, fcol='FFD0A0')


# ---------------------------------------------------------------- shots: the office in Nagasaki
def office_base(S, f=0.0, dusty=0.0):
    """f (0..1) is the white light at the windows; dusty (0..1) is afterwards."""
    A = show(S, 'office')
    sky(S, mix_col('A8C8E0', 'FFFFFF', f), 1.0)
    tint(S['panemat'], mix_col(mix_col('CFE4F2', 'FFFFFF', f), 'C8A078', dusty), 2.2 + 26 * f - 1.0 * dusty)
    S['winlight'].data.energy = 900 + 9000 * f - 300 * dusty
    S['winlight'].data.color = K.hexc(mix_col('E8F2FF', 'FFB070', dusty))[:3]
    for l in S['olamps']:
        l.data.energy = 260 * (1 - dusty) * (1 - 0.8 * f)
    S['fillk'] = 1.3 + 0.5 * dusty
    return A


def desk_cast(S, A, t, lt, tell=0.0, boss='listen'):
    S['yama'].place(A(2.9, 1.5, 0), PI - 0.75)
    g = 0.5 + 0.5 * math.sin(lt * 5.0)
    S['yama'].apply(blend(P('stand', aR=(0.6, 0.3, 1.2), head=(-0.05, 0)), P('stand', aL=(1.5, 0.9, 0.5), aR=(1.9, 1.0, 0.4), head=(-0.15, 0), lean=-0.05),
                          tell * (0.55 + 0.45 * g)))
    bandaged(S)
    S['jaw']['yama'] = 0.25 * tell * (0.5 + 0.5 * math.sin(t * 17))
    S['boss'].place(A(5.4, 4.6, 0), 0.75)
    if boss == 'listen':
        S['boss'].apply(P('cross', head=(0.05, 0.0)))
    else:
        S['boss'].apply(P('stand', aR=(0.9, 0.3, 1.5, 0.3 + 0.8 * math.sin(lt * 9)), aL=(0.2, 0.2, 0.3), head=(0.12, 0.42 * math.sin(lt * 8.0))))


def draughtsmen(S, A, t, look=0.0):
    for i, (x, y) in enumerate(((-5.2, 2.15), (-1.6, -1.65))):
        m = S['men'][i]
        m.place(A(x, y, 0.1), PI)
        m.apply(P('sit', lift=-0.42, lean=0.35 - 0.2 * look, aL=(1.2, 0.1, 0.8), aR=(1.25 + 0.08 * math.sin(t * 4 + i), 0.1, 0.8), head=(0.3 - 0.5 * look, look * (0.9 if i else -0.4))))


def office_wide(S, k, t, lt):
    A = office_base(S)
    y = lerp(-2.6, 0.9, k)
    S['yama'].place(A(lerp(3.6, 3.0, k), y, 0), PI - 0.2)
    S['yama'].apply(walk(t, 1.5))
    bandaged(S)
    S['boss'].place(A(5.4, 4.6, 0), 0.75)
    S['boss'].apply(P('stand', aL=(0.5, 0.1, 1.2), aR=(0.5, 0.1, 1.2), head=(0.3 - 0.4 * ease(lt / 0.6), 0.2)))
    draughtsmen(S, A, t, ease((lt - 0.3) / 0.4))
    S['rook'].place(A(-1.2, -3.0, 0), PI - 0.75)
    S['rook'].apply(P('stand', head=(0.0, lerp(-0.5, 0.2, k))))
    cam(S, A(lerp(-6.4, -5.8, k), lerp(-6.2, -5.8, k), lerp(3.9, 3.6, k)), A(1.5, 1.5, 2.4), 24)


def yama_tells(S, k, t, lt):
    A = office_base(S)
    desk_cast(S, A, t, lt, tell=ease(lt / 0.3))
    draughtsmen(S, A, t, 1.0)
    cam(S, A(lerp(1.5, 1.9, k), lerp(-3.0, -2.5, k), 2.9), A(4.35, 3.3, 2.6), 36)


def boss_no(S, k, t, lt):
    A = office_base(S)
    desk_cast(S, A, t, lt, tell=0.2, boss='no')
    cam(S, A(lerp(3.5, 3.7, k), lerp(0.2, 0.9, k), 2.9), A(5.4, 4.6, 2.72), 52)


def rook_office(S, k, t, lt):
    A = office_base(S)
    S['rook'].place(A(0.6, -1.2, 0), PI - 0.9)
    nod = ease((lt - 0.35) / 0.4)
    S['rook'].apply(blend(P('stand', aR=(0.8, 0.1, 2.0, 0.6), head=(0.0, 0.0)), P('stand', aR=(0.3, 0.2, 0.4), head=(0.3, 0.25)), nod))
    S['face']['rook'] = 'calm' if nod < 0.5 else 'sad'
    draughtsmen(S, A, t, 1.0)
    cam(S, A(lerp(4.4, 3.9, k), lerp(2.6, 2.1, k), 3.0), A(0.55, -1.2, 2.45), 36)


def flash_office(S, k, t, lt):
    f = ease(lt / 0.8)
    A = office_base(S, f)
    desk_cast(S, A, t, lt, tell=1 - f)
    S['yama'].apply(blend(P('stand', aL=(1.5, 0.9, 0.5), aR=(1.9, 1.0, 0.4)), P('stand', head=(0, -0.9), aR=(0.3, 0.2, 0.3)), f))
    S['boss'].apply(blend(P('cross'), P('stand', head=(0.0, 1.0), aL=(0.4, 0.4, 0.5)), f))
    draughtsmen(S, A, t, 1.0 - f)
    if S['prm'].get('v') == 2:
        cam(S, A(lerp(6.4, 5.6, k), lerp(-5.6, -4.6, k), lerp(2.2, 2.6, k)), A(-1.0, 7, 3.0), 24)
    else:
        cam(S, A(lerp(-0.8, -0.2, k), lerp(-5.4, -4.4, k), lerp(3.0, 2.8, k)), A(3.3, 7, 2.8), 24)


def blast_props(S, A, lt, calm=0.0):
    u = ease(lt / 0.8)
    for i, o in enumerate(S['mull']):
        if i % 2 == 0 or calm:
            a = (i * 0.618) % 1
            o.location = (o.location[0] + (a - 0.5) * 3 * u, o.location[1] - (4 + a * 7) * u, max(0.08, o.location[2] + 1.2 * math.sin(u * PI) - 2.8 * u * (0.5 + a)))
            o.rotation_euler = (u * (3 + i), u * 2.2 * (a + 0.3), u * i * 0.6)
    for i, o in enumerate(S['papers']):
        a, b = (i * 0.618) % 1, (i * 0.37) % 1
        if calm:
            v = (lt * 0.25 + b) % 1
            o.location = A(-5 + a * 7.6, -1.2 + b * 6, 0.1 + 3.2 * (1 - v) * (0.3 + 0.7 * a))
            o.rotation_euler = (0.5 * math.sin(lt * 2 + i), 0.4 * math.cos(lt * 2.3 + i), i)
        else:
            o.location = A(-5 + a * 11 + math.sin(lt * 4 + i), 5.5 - (3 + b * 8) * u, 1.6 + 2.6 * math.sin(u * PI * (0.6 + 0.4 * b)) + (i % 3) * 0.3)
            o.rotation_euler = (lt * 9 + i, lt * 7 + i * 2, i)


def office_blast(S, k, t, lt):
    f = max(0.0, 1 - lt / 0.7)
    A = office_base(S, f * 0.8, ease(lt / 0.9) * 0.7)
    u = ease(lt / 0.45)
    S['yama'].place(A(2.9, 1.5 - 0.6 * u, 0), PI - 0.75, pitch=0.2 * u)
    S['yama'].apply(blend(P('stand'), P('stand', lL=(1.5, 2.2), lR=(0.3, 1.6), lift=-0.62, lean=0.9, aL=(2.3, 0.4, 1.9), aR=(2.3, 0.4, 1.9), head=(0.5, 0)), u))
    bandaged(S)
    S['face']['yama'] = 'shut'
    S['boss'].place(A(5.4, 4.6 - 0.2 * u, 0), 0.75)
    S['boss'].apply(blend(P('stand'), P('stand', lL=(1.3, 2.0), lR=(1.3, 2.0), lift=-0.6, lean=0.6, aL=(2.3, 0.4, 1.9), aR=(2.3, 0.4, 1.9), head=(0.5, 0)), u))
    draughtsmen(S, A, t, 0.0)
    for m in S['men']:
        m.apply(P('sit', lift=-0.42, lean=0.9, aL=(2.3, 0.4, 1.9), aR=(2.3, 0.4, 1.9), head=(0.5, 0)))
    S['rook'].place(A(-1.6, -3.2, 0), PI - 0.6)
    S['rook'].apply(blend(P('stand'), P('stand', lL=(1.2, 2.0), lR=(1.2, 2.0), lift=-0.55, lean=0.4, aR=(0.2, 1.9, 1.6, -1.5), aL=(1.9, 0.3, 1.6), head=(0.3, 0)), u))
    S['face']['rook'] = 'shut'
    blast_props(S, A, lt)
    sh = 0.05 * math.sin(t * 43) * max(0.0, 1 - lt / 0.8)
    cam(S, A(-5.6 + sh, -6.0, 2.5 + sh), A(1.2, 1.5, 1.9), 24, roll=sh * 0.5)


def yama_stands(S, k, t, lt):
    A = office_base(S, 0.0, 1.0)
    sky(S, 'B89878', 1.0)
    u = ease((lt - 0.1) / 0.75)
    S['yama'].place(A(2.9, 0.9, 0), 0.35)
    S['yama'].apply(blend(P('stand', lL=(1.5, 2.2), lR=(0.3, 1.6), lift=-0.62, lean=0.8, aL=(1.0, 0.2, 0.4), aR=(1.0, 0.2, 0.4), head=(0.3, 0)),
                          P('stand', lean=0.08, aR=(0.3, 0.2, 0.5), head=(-0.12, -0.3)), u))
    bandaged(S)
    S['rook'].place(A(0.9, 3.3, 0), 0.5)
    S['hat_off'] = ease((lt - 0.3) / 0.5)
    S['rook'].apply(blend(P('stand', lL=(1.2, 2.0), lR=(1.2, 2.0), lift=-0.55, lean=0.4), hat_hold(head=(0.1, 0.0)), ease(lt / 0.6)))
    S['face']['rook'] = 'sad'
    blast_props(S, A, 0.8 + lt, calm=1.0)
    for i, o in enumerate(S['mull']):
        if i % 2 == 0:
            o.location = (o.location[0], o.location[1], 0.08)
    for i, o in enumerate(S['dust'][:5]):
        o.location = A(-6 + i * 3.2 + 0.6 * math.sin(t + i), 5.4, 1.0 + (i % 2) * 1.6 + 0.3 * lt)
        o.scale = (1.5, 0.9, 1.1)
    cam(S, A(lerp(4.6, 4.2, k), lerp(-3.6, -3.0, k), lerp(1.7, 2.2, k)), A(2.2, 1.4, lerp(2.0, 2.5, k)), 34)


# ---------------------------------------------------------------- shots: the hall
def hall_base(S):
    A = show(S, 'hall')
    sky(S, '05050A', 1.0)
    S['fillk'] = 0.5
    return A


def old_at_lectern(S, A, t, lt, hand=0.0):
    S['old'].place(A(0, 7.15, 1.0), 0.0)
    S['old'].root.scale = (0.95, 0.95, 0.95)
    S['old'].apply(blend(P('stand', aL=(0.75, 0.1, 0.9), aR=(0.75, 0.1, 0.9), lean=0.1, head=(0.05, 0.12 * math.sin(lt * 1.9))),
                         P('stand', aL=(0.75, 0.1, 0.9), aR=(1.2, 0.35, 1.5, -0.3), lean=0.1, head=(0.0, 0.1)), hand))
    S['face']['old'] = 'warm'
    S['jaw']['old'] = 0.22 * (0.5 + 0.5 * math.sin(t * 15)) * (0.5 + 0.5 * math.sin(t * 3.1))


def old_yama(S, k, t, lt):
    A = hall_base(S)
    old_at_lectern(S, A, t, lt)
    cam(S, A(lerp(1.5, 1.1, k), lerp(-0.4, 1.0, k), lerp(2.7, 2.9, k)), A(0.0, 7.0, 3.3), 60, fcol='FFE0C0')


def old_speaks(S, k, t, lt):
    A = hall_base(S)
    old_at_lectern(S, A, t, lt, hand=ease(lt / 0.5) * (0.7 + 0.3 * math.sin(lt * 4)))
    cam(S, A(lerp(-3.2, -2.7, k), lerp(4.0, 4.4, k), lerp(2.5, 2.7, k)), A(0.1, 7.0, 3.45), 62, fcol='FFE0C0')


def rook_hall(S, k, t, lt):
    A = hall_base(S)
    old_at_lectern(S, A, t, lt)
    S['rook'].place(A(1.8, -3.25, 0.1), PI)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', lift=-0.42, lean=0.12, aL=(0.8, -0.2, 1.5, 1.0), aR=(0.8, -0.2, 1.5, 1.0), head=(-0.08 + 0.1 * ease(lt / 0.6), 0.15)))
    S['face']['rook'] = 'warm'
    S['glow'].location = A(0.2, -0.6, 3.4)
    S['glow'].data.energy = 260
    S['glow'].data.color = K.hexc('FFE0C0')[:3]
    cam(S, A(lerp(-0.4, 0.0, k), lerp(0.6, 0.0, k), 2.3), A(1.7, -3.2, 1.55), 40, fill=2.0, fcol='FFE0C0')


def hall_wide(S, k, t, lt):
    A = hall_base(S)
    old_at_lectern(S, A, t, lt, hand=0.4)
    S['rook'].place(A(0.1, -6.2, 0), PI)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(-0.05, 0.0)))
    S['glow'].location = A(1.5, -9.5, 4.5)
    S['glow'].data.energy = 700
    S['glow'].data.color = K.hexc('8EA8E8')[:3]
    cam(S, A(lerp(2.6, 2.0, k), lerp(-13.5, -12.0, k), lerp(5.6, 5.0, k)), A(0, 5.0, 2.6), 30)


# ---------------------------------------------------------------- stills for the case board
def photo_yard(S, k, t, lt):
    A = morning(S)
    S['yama'].place(A(0.2, 12, 0), PI + 2.6)
    S['yama'].apply(P('stand', head=(0, 0.2)))
    S['bag'].hide_render = False
    cam(S, A(-2.4, 5.5, 2.3), A(0.3, 12, 2.4), 40)


def photo_old(S, k, t, lt):
    A = hall_base(S)
    old_at_lectern(S, A, 1.0, 0.5)
    cam(S, A(0.9, 1.6, 2.9), A(0.0, 7.0, 3.3), 62, fcol='FFE0C0')


SHOTS3D = {f.__name__: f for f in (
    flash_city, dust_rise, train_wide, flash_office, rook_station, rook_walk, yard_wide, yama_walk, yama_cu, rook_looks, yama_hurt, plane_high, flash_road, thrown,
    aftermath, shelter_in, rook_shelter, train_window, office_wide, yama_tells, rook_office, boss_no, office_blast, yama_stands,
    old_yama, rook_hall, hall_wide, old_speaks, rook_wrong, signoff)}
STILLS = dict(yard=photo_yard, old=photo_old)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it: the lodging street in Hiroshima on the last morning, his street in Nagasaki,
# a room at home (treatment, the fever, the family, the writing), the railway carriage, an occupation office,
# a classroom, a city-office counter, and new shots on the Short's sets. Still sober: nobody is shown hurt beyond
# his bandages, no victims are shown, and the extra people are stand-ins, not likenesses.
ORG.update(dorm=(2000, 0, 0), naga=(2400, 0, 0), room=(2800, 0, 0), car=(3200, 0, 0), hut=(3600, 0, 0), klass=(4000, 0, 0),
           counter=(4400, 0, 0))
PARK = (0, 0, -80)
COLS = [dict(top='C9D2C2', pants='55503F', hand=SKIN, boot='2E2822', fore=SKIN), dict(top='BDB6A2', pants='4A4C52', hand='CF9E70', boot='2A2620', fore='CF9E70')]
HISAKO = dict(top='7C6488', pants='5A4868', hand='E0B890', boot='E8E0D0')
DOCTOR = dict(top='E9EDEE', pants='5C6670', hand='D2A27A', boot='2A2A30')
OFFICER = dict(top='A69A6C', pants='8E8458', hand='D8A888', boot='3A2A1E')
CLERK = dict(top='4C5A6E', pants='30343C', hand='D8AC84', boot='1C1C20', fore='E8E8EC')
KIDS = [dict(top=c, pants='3A4258', hand='E0B890', boot='2A2A30') for c in ('E8E4DA', 'D88A5A', 'A8C4D8')]


# The kit's add() and empty() go through Blender operators, which slow down as the scene fills up; with seven more sets
# the build took many minutes. These build the same primitives straight from mesh data, at a constant cost. From here
# on the whole file (the Short's sets above included, since they look the names up when they run) uses them.
import bmesh  # noqa: E402

_kit_add, _kit_empty = add, empty


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
    elif kind == 'plane':
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=kw.get('size', 2.0) / 2)
    elif kind == 'cylinder':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius', 1.0),
                              radius2=kw.get('radius', 1.0), depth=kw.get('depth', 2.0))
    elif kind == 'cone':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=kw.get('vertices', 32), radius1=kw.get('radius1', 1.0),
                              radius2=kw.get('radius2', 0.0), depth=kw.get('depth', 2.0))
    elif kind == 'ico_sphere':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('subdivisions', 2), radius=kw.get('radius', 1.0))
    else:
        bm.free()
        return _kit_add(kind, col, loc, rot, scale, parent, rough, emit, alpha, **kw)
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


def box(col, loc, scale, parent, rot=(0, 0, 0), **kw):
    return add('cube', col, loc, rot=rot, scale=scale, size=1, parent=parent, **kw)


def bun_head(skin, hair):
    base = K.human_head(skin, hair)

    def fn(head):
        out = base(head)
        add('ico_sphere', hair, (0, 0.27, 0.2), radius=0.17, subdivisions=1, parent=head)
        return out
    return fn


def cap_head(skin, hair, cap):
    base = K.human_head(skin, hair)

    def fn(head):
        out = base(head)
        add('cube', cap, (0, -0.02, 0.34), rot=(-0.1, 0, 0), scale=(0.5, 0.66, 0.13), size=1, parent=head)
        add('cube', cap, (0, -0.34, 0.27), rot=(0.25, 0, 0), scale=(0.44, 0.2, 0.04), size=1, parent=head)
        return out
    return fn


def house(r, x, y, w_, d, hgt, wall, roof, lit=True):
    box(wall, (x, y, hgt / 2), (w_, d, hgt), r)
    box(roof, (x, y - 0.3, hgt + 0.25), (w_ + 1.6, d + 2.0, 0.5), r, rot=(0.09, 0, 0))
    box(roof, (x, y + 0.6, hgt + 0.75), (w_ + 0.4, d * 0.45, 0.5), r)
    for i in range(int(w_ // 3)):
        box('EDE4C8' if lit else '4A4640', (x - w_ / 2 + 1.6 + i * 3, y - d / 2 - 0.03, hgt * 0.55), (1.5, 0.08, hgt * 0.34), r, emit=0.5 if lit else 0.0)


def far_hills(r, y0, cols, n=13, span=1300, side=1):
    for i in range(n):
        a = i / (n - 1)
        add('cone', cols[i % len(cols)], (-span / 2 + a * span + (i * 37) % 40, side * (y0 + (i % 3) * 70), 30 + (i * 19) % 46),
            radius1=130 + (i % 4) * 30, radius2=8, depth=100 + (i * 29) % 80, vertices=7, parent=r)


# ---------------------------------------------------------------- set 6: the lodging street, Hiroshima, last morning
def set_dorm(r):
    add('plane', 'B0A078', (0, 0, -0.02), size=2600, parent=r)
    box('8E8474', (0, 0, 0.02), (420, 7, 0.06), r)
    for s in (-1, 1):
        box('6E7A48', (0, s * 4.3, 0.05), (420, 1.4, 0.12), r)
    box('A08460', (0, 13, 3.7), (26, 9, 7.4), r)                         # the company dormitory
    box('4A4038', (0, 12.4, 3.75), (27.4, 10.6, 0.3), r)
    box('3E3A40', (0, 12.4, 7.65), (28.4, 11.6, 0.6), r, rot=(0.07, 0, 0))
    box('3E3A40', (0, 13.4, 8.3), (27, 4.6, 0.6), r)
    for i in range(-5, 6):
        for z in (2.0, 5.6):
            if i == 0 and z < 3:
                continue
            box('EDE4C8', (i * 2.3, 8.46, z), (1.5, 0.08, 1.7), r, emit=0.45)
            box('4A3826', (i * 2.3, 8.42, z), (0.07, 0.08, 1.7), r)
    box('3A2C1E', (0, 8.44, 1.7), (2.3, 0.1, 3.4), r)
    box('E8DEC0', (0, 8.4, 3.75), (3.4, 0.08, 0.7), r)                  # a name board, left blank
    for i in range(-16, 17):                                            # the front fence and its gate
        if abs(i) < 3:
            continue
        box(('6A543C', '5E4A36')[i % 2], (i * 0.9, 5.3, 1.0), (0.82, 0.1, 2.0), r)
    for s in (-1, 1):
        box('4A3826', (s * 2.5, 5.3, 1.6), (0.36, 0.36, 3.2), r)
    box('4A3826', (0, 5.3, 3.3), (6.2, 0.44, 0.3), r)
    box('3E3A40', (0, 5.3, 3.6), (7.0, 1.2, 0.16), r)
    for i, (x, w_, hgt) in enumerate(((-30, 14, 5), (-50, 12, 4.4), (-70, 16, 6), (30, 13, 4.6), (48, 12, 5.4), (68, 15, 4.4))):
        house(r, x, 13 + (i % 2) * 2, w_, 8, hgt, ('9A9282', '8E8676', 'A69C86')[i % 3], ('4A4844', '3E4248')[i % 2])
        add('ico_sphere', '3E6A3A', (x + w_ / 2 + 2.6, 11, 3.6), scale=(1, 1, 1.3), radius=2.8, subdivisions=1, parent=r)
    for i, x in enumerate(range(-84, 90, 21)):                          # the other side of the street
        house(r, x, -15 - (i % 2) * 2, 13 + (i % 3) * 2, 8, 4.2 + (i % 3) * 0.8, ('8E8676', 'A69C86', '9A9282')[i % 3], '4A4844', lit=False)
    for i in range(-6, 7):
        add('cylinder', '4A3A2A', (i * 14 + 6, 4.6, 3.6), radius=0.13, depth=7.2, vertices=6, parent=r)
        box('4A3A2A', (i * 14 + 6, 4.6, 6.6), (0.12, 1.7, 0.12), r)
    box('2A2A2A', (0, 4.0, 6.72), (200, 0.03, 0.03), r)
    for i in range(40):                                                 # the city beyond
        a = (i * 0.618) % 1
        hgt = 5 + (i * 7) % 8
        box(('8E8676', '7E786C', '9A9282', '6E6A62')[i % 4], (-330 + a * 660, 70 + (i * 37) % 150, hgt / 2), (14 + (i * 11) % 18, 12, hgt), r)
    far_hills(r, 520, ('6A8A9A', '5E7E90', '7A98A6'))
    far_hills(r, 420, ('6A8A9A', '5E7E90'), n=9, side=-1)
    light((90, -140, 200), 3.4, 'FFF2D8', kind='SUN', target=empty((0, 0, 0), r), parent=r)
    return {}


# ---------------------------------------------------------------- set 7: his street in Nagasaki
def set_naga(r):
    add('plane', '7E8A6A', (0, 0, -0.02), size=2600, parent=r)
    box('8A8478', (0, 0, 0.02), (420, 7, 0.06), r)
    box('A8A294', (0, 3.9, 0.12), (420, 0.5, 0.24), r)
    box('A8A294', (0, -3.9, 0.12), (420, 0.5, 0.24), r)
    hx = -10.0                                                          # the house
    box('B8A888', (hx, 9.5, 2.1), (11, 7, 4.2), r)
    box('3A4450', (hx, 9.0, 4.6), (12.8, 9.4, 0.5), r, rot=(0.1, 0, 0))
    box('3A4450', (hx, 10.2, 5.2), (11.6, 3.6, 0.5), r)
    box('2E3640', (hx, 10.2, 5.55), (12.0, 0.5, 0.3), r)
    box('8A6A44', (hx, 5.4, 0.3), (5.0, 1.3, 0.6), r)
    box('7A5C3A', (hx, 4.5, 0.15), (3.4, 0.7, 0.3), r)
    doormat = own_mat('door', 'EDE4C8', 0.6, 0.9)
    use(box('000000', (hx, 5.97, 2.3), (2.8, 0.08, 3.4), r), doormat)
    for dx in (-0.93, 0, 0.93):
        box('4A3826', (hx + dx, 5.92, 2.3), (0.07, 0.06, 3.4), r)
    for dz in (1.3, 2.3, 3.3):
        box('4A3826', (hx, 5.92, dz), (2.8, 0.06, 0.06), r)
    for s in (-1, 1):
        box('4A3826', (hx + s * 1.5, 5.9, 2.2), (0.22, 0.2, 4.0), r)
        box('EDE4C8', (hx + s * 3.7, 5.97, 2.5), (1.7, 0.08, 1.5), r, emit=0.4)
        box('4A3826', (hx + s * 3.7, 5.93, 2.5), (0.06, 0.06, 1.5), r)
    for i in range(-13, 14):                                            # bamboo fence, a gap at the path
        x = hx + i * 0.86
        if abs(i) < 3:
            continue
        box(('B09A5A', 'A08C50')[i % 2], (x, 4.3, 0.85), (0.74, 0.1, 1.7), r)
    add('cylinder', '8E8E86', (hx - 4.4, 5.0, 0.6), radius=0.22, depth=1.2, vertices=6, parent=r)       # a stone lantern, a small pine
    box('8E8E86', (hx - 4.4, 5.0, 1.4), (0.7, 0.7, 0.5), r)
    add('cone', '8E8E86', (hx - 4.4, 5.0, 1.9), radius1=0.6, radius2=0.1, depth=0.5, vertices=4, parent=r)
    add('cylinder', '4A3A2A', (hx + 4.6, 5.2, 1.2), radius=0.14, depth=2.4, vertices=5, parent=r)
    for i, (dz, rr) in enumerate(((2.4, 1.3), (3.2, 1.0), (3.9, 0.7))):
        add('cone', '2E5A3A', (hx + 4.6 + (i % 2) * 0.3, 5.2, dz), radius1=rr, radius2=0.1, depth=0.8, vertices=6, parent=r)
    house(r, -27, 10, 12, 7, 4.4, 'A69C86', '3E4650')
    house(r, 3, 10.5, 9, 7, 4.0, '9A9282', '46424A')
    house(r, -44, 10, 13, 7, 5.0, 'B0A690', '3A4450')
    bx = 22.0                                                           # the company office: brick, no name on it
    box('A0503A', (bx, 12.5, 5.5), (22, 11, 11), r)
    box('C8C0B0', (bx, 12.5, 11.2), (22.8, 11.8, 0.5), r)
    box('C8C0B0', (bx, 6.95, 0.5), (22.2, 0.3, 1.0), r)
    for i in range(-4, 5):
        for z in (3.0, 6.2, 9.0):
            if i == 0 and z < 4:
                continue
            box('D8E4EC', (bx + i * 2.3, 6.96, z), (1.3, 0.1, 1.9), r, emit=0.5)
            box('C8C0B0', (bx + i * 2.3, 6.92, z - 1.05), (1.6, 0.16, 0.16), r)
    box('C8C0B0', (bx, 6.9, 2.3), (3.4, 0.3, 4.6), r)
    box('3A2C1E', (bx, 6.74, 1.9), (2.2, 0.1, 3.8), r)
    for i in range(3):
        box('B8B0A0', (bx, 6.2 - i * 0.5, 0.36 - i * 0.12), (4.4, 0.5, 0.24), r)
    for i, x in enumerate(range(-90, 100, 20)):                         # the far side of the street
        house(r, x + 6, -14 - (i % 2) * 2, 12 + (i % 3) * 2, 8, 4.0 + (i % 3) * 0.9, ('9A9282', 'B0A690', '8E8676')[i % 3], '3E4650', lit=False)
    for i in range(-6, 7):
        add('cylinder', '4A3A2A', (i * 15 + 2, -4.6, 3.6), radius=0.13, depth=7.2, vertices=6, parent=r)
        box('4A3A2A', (i * 15 + 2, -4.6, 6.6), (0.12, 1.7, 0.12), r)
    for i in range(34):                                                 # houses climbing the hills behind
        a = (i * 0.618) % 1
        y = 34 + (i * 29) % 120
        box(('B0A690', '9A9282', 'C0B49C', '8E8676')[i % 4], (-170 + a * 340, y, (y - 20) * 0.22 + 2), (9, 7, 4), r)
        box('3E4650', (-170 + a * 340, y, (y - 20) * 0.22 + 4.3), (10, 8, 0.6), r)
    for i in range(9):
        a = i / 8
        add('cone', ('3E6A56', '4A7A5E', '36604E')[i % 3], (-520 + a * 1040, 150 + (i % 3) * 40, 22 + (i * 17) % 30),
            radius1=170 + (i % 3) * 30, radius2=14, depth=110 + (i * 23) % 60, vertices=7, parent=r)
    far_hills(r, 380, ('5E8A7A', '6A9686', '54806E'), n=11)
    far_hills(r, 300, ('5E8A7A', '54806E'), n=9, side=-1)
    sun = light((120, -150, 180), 3.2, 'FFF0D8', kind='SUN', target=empty((0, 0, 0), r), parent=r)
    lant = light((hx, 4.6, 2.6), 0, 'FFC080', kind='POINT', parent=r)
    return dict(nagasun=sun, doormat=doormat, porchlight=lant)


# ---------------------------------------------------------------- set 8: a room at home
def set_room(r):
    box('B8A870', (0, 0, -0.1), (11.4, 10, 0.2), r)
    for x in (-3.6, 0, 3.6):
        box('6E6238', (x, 0, 0.005), (0.07, 9.6, 0.02), r)
    box('6E6238', (0, 0.4, 0.005), (11, 0.07, 0.02), r)
    box('6A5238', (0, 4.6, 0.3), (11.4, 0.2, 0.6), r)
    box('C8BC9C', (0, 4.66, 4.6), (11.4, 0.2, 1.4), r)
    box('4A3826', (0, 4.5, 3.85), (11.4, 0.24, 0.16), r)
    shoji = own_mat('shoji', 'F4F0E0', 0.6, 3.0)
    use(add('plane', '000000', (0, 4.6, 2.2), rot=(PI / 2, 0, 0), size=1, scale=(11, 3.3, 1), parent=r), shoji)
    for i in range(-9, 10):
        box('4A3826', (i * 0.6, 4.54, 2.2), (0.1 if i % 4 == 0 else 0.04, 0.05, 3.3), r)
    for z in (1.2, 1.9, 2.6, 3.3):
        box('4A3826', (0, 4.54, z), (11, 0.05, 0.04), r)
    box('C8BC9C', (-5.6, 0, 2.55), (0.2, 10, 5.3), r)
    box('C8BC9C', (5.6, 0, 2.55), (0.2, 10, 5.3), r)
    for y in (-1.6, 0.4, 2.4):                                          # sliding doors on the right
        box('D8CCA8', (5.47, y, 1.95), (0.06, 1.9, 3.7), r)
        box('4A3826', (5.44, y + 0.98, 1.95), (0.08, 0.08, 3.7), r)
    box('4A3826', (5.44, 0.4, 3.85), (0.1, 6.2, 0.14), r)
    box('8A7A5A', (0, 0, 5.2), (11.4, 10, 0.2), r)
    for y in (-3, -1, 1, 3):
        box('5A4A30', (0, y, 5.05), (11.2, 0.14, 0.14), r)
    box('5A4630', (-5.1, 1.6, 0.95), (0.8, 2.6, 0.1), r)                # the alcove shelf and a plain scroll
    box('4A3826', (-5.1, 1.6, 0.45), (0.7, 2.4, 0.9), r)
    box('EDE4C8', (-5.46, 1.6, 3.0), (0.03, 1.0, 2.3), r, emit=0.25)
    for i, z in enumerate((3.6, 3.2, 2.8, 2.4)):
        box('3A3A44', (-5.43, 1.6 + (i % 2) * 0.08 - 0.04, z), (0.02, 0.07, 0.26), r)
    box('5A3E28', (4.7, 3.6, 1.3), (1.5, 1.5, 2.6), r)                  # a chest of drawers
    for z in (0.5, 1.1, 1.7, 2.3):
        box('2E2218', (4.7, 2.84, z), (1.3, 0.03, 0.04), r)
        box('C8A040', (4.7, 2.82, z - 0.2), (0.24, 0.03, 0.05), r, rough=0.3)
    box('E8E4DA', (-0.1, 2.0, 0.12), (3.7, 2.4, 0.24), r)               # the futon
    box('F4F2EA', (-1.6, 2.0, 0.3), (0.7, 1.3, 0.2), r)
    blanket = mov(box('6A7A9A', (0.5, 2.0, 0.42), (2.6, 2.5, 0.42), r))
    box('8A94B0', (-0.46, 0, 0.1), (0.1, 1.0, 1.05), blanket)
    tb = empty((2.4, -0.8, 0), r)                                       # the low table
    box('6A4A2E', (0, 0, 0.82), (3.4, 1.9, 0.12), tb)
    for sx in (-1.5, 1.5):
        for sy in (-0.8, 0.8):
            box('4A3220', (sx, sy, 0.4), (0.14, 0.14, 0.8), tb)
    for i, (x, y) in enumerate(((-2.3, 0), (2.3, 0), (0, 1.5), (0, -1.5))):
        box(('7A3A3A', '3A5A6A')[i % 2], (x, y, 0.06), (1.1, 1.1, 0.12), tb)
    lamp = empty((1.4, 0.0, 5.1), r)
    add('cylinder', '2A2A2A', (0, 0, -0.5), radius=0.02, depth=1.0, vertices=4, parent=lamp)
    add('cone', 'D8CCA8', (0, 0, -1.1), radius1=0.6, radius2=0.2, depth=0.34, vertices=8, parent=lamp)
    lampmat = own_mat('roomlamp', 'FFD8A0', 0.5, 0.0)
    use(add('ico_sphere', '000000', (0, 0, -1.26), radius=0.14, subdivisions=1, parent=lamp), lampmat)
    ll = light((0, 0, -1.5), 0, 'FFC888', kind='POINT', parent=lamp)
    key = light((0, 3.6, 3.0), 900, 'FFF4E0', 6.0, empty((0, -1, 1.0), r), parent=r)
    return dict(shoji=shoji, blanket=blanket, roomlamp=mov(lamp), roomlampmat=lampmat, roomlight=ll, roomkey=key)


# ---------------------------------------------------------------- set 9: the railway carriage
def set_car(r):
    box('5A4630', (0, 0, -0.05), (17.4, 3.0, 0.1), r)
    for i in range(-14, 15):
        box('4A3826', (i * 0.6, 0, 0.005), (0.04, 2.9, 0.02), r)
    box('6A4E34', (0, 1.45, 0.75), (17.4, 0.1, 1.5), r)
    box('6A4E34', (0, 1.45, 3.3), (17.4, 0.1, 0.5), r)
    box('8A6A44', (0, 1.38, 1.52), (17.4, 0.16, 0.08), r)
    for i in range(-4, 5):
        box('6A4E34', (i * 2.0, 1.45, 2.3), (0.34, 0.1, 1.6), r)
    box('8A7A5A', (0, 0, 3.6), (17.4, 3.0, 0.1), r)
    for x in (-5, 0, 5):
        add('ico_sphere', 'FFE2B0', (x, 0, 3.46), radius=0.12, subdivisions=1, parent=r, emit=4)
        light((x, -0.2, 3.2), 110, 'FFD8A8', kind='POINT', parent=r)
    for s in (-1, 1):
        box('6A4E34', (s * 8.7, 0, 1.8), (0.1, 3.0, 3.6), r)
        box('3A2C1E', (s * 8.63, -0.2, 1.6), (0.06, 1.2, 3.0), r)
        box('D8E4EC', (s * 8.6, -0.2, 2.3), (0.04, 0.7, 0.9), r, emit=0.6)
    for bx in (-6, -2, 2, 6):                                           # seats back to back, facing one another in bays
        box('7A5A3A', (bx, 0.75, 1.3), (0.14, 1.3, 1.9), r)
        for s in (-1, 1):
            box('8A6A44', (bx + s * 0.45, 0.75, 0.72), (0.76, 1.3, 0.12), r)
            box('5A4630', (bx + s * 0.45, 0.75, 0.36), (0.6, 1.2, 0.6), r)
    box('8A6A44', (0, 1.2, 3.0), (17, 0.5, 0.05), r)                    # the luggage rack and what is on it
    for i, x in enumerate((-6.4, -3.2, 0.8, 4.6, 7.0)):
        box(('6A4A2E', '8A7A5A', '4E5A4A')[i % 3], (x, 1.15, 3.2), (0.9 + (i % 2) * 0.3, 0.42, 0.34), r)
    near = mov(empty((0, 0, 0), r))                                     # what goes by outside
    box('6E8456', (0, 300, -1.3), (1400, 596, 0.1), near)
    for i in range(-14, 15):
        add('cylinder', '4A3A2A', (i * 12.0, 6.0, 2.2), radius=0.13, depth=7.0, vertices=6, parent=near)
        box(('5E7A46', '6A8650')[i % 2], (i * 12.0, 16, -1.2), (11, 9, 0.12), near)
    farg = mov(empty((0, 0, 0), r))
    for i, (x, y) in enumerate(((-40, 46), (-12, 60), (22, 44), (54, 62), (86, 48), (118, 58))):
        box('8E8676', (x, y, 1.2), (9, 7, 4.8), farg)
        add('cone', '4A4844', (x, y, 4.8), rot=(0, 0, PI / 4), radius1=7.5, radius2=0, depth=3, vertices=4, parent=farg)
    for i in range(15):
        add('cone', ('4E6E6A', '5A7A72', '456460')[i % 3], (-520 + i * 80, 190 + (i % 3) * 60, 28 + (i * 19) % 36),
            radius1=120 + (i % 4) * 24, radius2=8, depth=90 + (i * 29) % 60, vertices=7, parent=farg)
    light((160, 200, 90), 2.4, 'FFC890', kind='SUN', target=empty((0, 0, 1), r), parent=r)
    light((0, 1.0, 2.6), 260, 'FFD0A0', 6.0, empty((0, -1, 1.2), r), parent=r)
    return dict(carnear=near, carfar=farg)


# ---------------------------------------------------------------- set 10: an occupation office, after the war
def set_hut(r):
    box('7A6244', (0, 0, -0.1), (13.4, 11, 0.2), r)
    for i in range(-9, 10):
        box('6A5438', (i * 0.7, 0, 0.005), (0.04, 10.6, 0.02), r)
    wall = 'A8B49A'
    box(wall, (0, 5.4, 3.1), (13.4, 0.2, 6.2), r)
    for s in (-1, 1):
        box(wall, (s * 6.7, 0, 3.1), (0.2, 11, 6.2), r)
    box('8A967C', (0, 5.28, 0.7), (13.2, 0.06, 1.4), r)
    box('C8CCB8', (0, 0, 6.2), (13.4, 11, 0.2), r)
    box('DCE8F0', (-2.6, 5.28, 3.5), (3.6, 0.06, 2.4), r, emit=2.4)
    for i in range(7):
        box('C8C8B8', (-2.6, 5.22, 2.5 + i * 0.34), (3.6, 0.1, 0.1), r)
    box('5A4630', (-2.6, 5.24, 2.25), (3.9, 0.14, 0.12), r)
    box('8A6A44', (3.2, 5.28, 3.5), (3.0, 0.06, 2.0), r)                # a notice board with plain sheets
    for i in range(5):
        box(('F2F0E6', 'E0DCCC')[i % 2], (2.2 + (i % 3) * 0.95, 5.22, 3.1 + (i // 3) * 0.9), (0.7, 0.04, 0.7), r, emit=0.2)
    dk = empty((1.6, 1.6, 0), r)                                        # the desk
    box('5A4630', (0, 0, 1.42), (4.4, 2.0, 0.12), dk)
    for sx in (-1.6, 1.6):
        box('4A3826', (sx, 0, 0.7), (1.0, 1.9, 1.4), dk)
    box('2A2A2E', (-1.2, 0.2, 1.68), (1.0, 0.8, 0.4), dk)
    box('C8C8C0', (-1.2, -0.15, 1.72), (0.9, 0.3, 0.1), dk)
    box('F2F0E6', (-1.2, 0.45, 2.05), (0.8, 0.04, 0.5), dk, emit=0.2)
    box('F2F0E6', (0.4, -0.2, 1.5), (0.9, 0.65, 0.04), dk, rot=(0, 0, 0.2), emit=0.2)
    box('8A6A44', (1.5, 0.3, 1.56), (0.8, 0.6, 0.16), dk)
    add('cylinder', '2A2A2A', (1.7, -0.5, 1.8), radius=0.04, depth=0.7, vertices=5, parent=dk)
    add('cone', '3E6A4A', (1.7, -0.6, 2.2), radius1=0.36, radius2=0.12, depth=0.3, vertices=8, parent=dk, emit=0.8)
    box('4A3826', (0, 1.5, 0.75), (1.1, 1.0, 0.14), dk)
    box('4A3826', (0, 2.0, 1.5), (1.1, 0.12, 1.5), dk)
    for i in range(3):                                                  # filing cabinets
        box(('5E6A52', '56624C')[i % 2], (-6.0, 1.2 + i * 1.3, 1.7), (1.0, 1.2, 3.4), r)
        for z in (0.6, 1.4, 2.2, 3.0):
            box('C8A040', (-5.46, 1.2 + i * 1.3, z), (0.04, 0.4, 0.08), r, rough=0.3)
    box('6A4E34', (4.6, -3.2, 0.7), (3.0, 0.9, 0.12), r)                # a waiting bench
    for sx in (3.3, 5.9):
        box('4A3826', (sx, -3.2, 0.35), (0.12, 0.8, 0.7), r)
    add('cylinder', '2A2A2A', (5.8, 4.4, 2.0), radius=0.05, depth=4.0, vertices=5, parent=r)
    box('2A2A2A', (5.8, 4.4, 4.0), (0.9, 0.06, 0.06), r)
    fan = mov(empty((0, 0.8, 5.5), r))
    add('cylinder', '3A3A3E', (0, 0, 0), radius=0.22, depth=0.3, vertices=8, parent=fan)
    for i in range(4):
        box('5A4630', (1.2 * math.cos(i * PI / 2), 1.2 * math.sin(i * PI / 2), -0.05), (2.0, 0.34, 0.04), fan, rot=(0.12, 0, i * PI / 2))
    add('cylinder', '2A2A2A', (0, 0.8, 5.85), radius=0.03, depth=0.6, vertices=4, parent=r)
    for x, y in ((-3.2, -1.5), (3.4, -1.0)):
        add('ico_sphere', 'FFE2B0', (x, y, 5.6), radius=0.14, subdivisions=1, parent=r, emit=6)
        light((x, y, 5.2), 320, 'FFE4C0', kind='POINT', parent=r)
    light((-2.6, 4.6, 3.4), 700, 'E8F2FF', 5.0, empty((0, 0, 1.4), r), parent=r)
    return dict(fan=fan)


# ---------------------------------------------------------------- set 11: a classroom
def set_klass(r):
    box('8A6E4A', (0, 0, -0.1), (15, 14, 0.2), r)
    for i in range(-10, 11):
        box('7A5E3C', (i * 0.7, 0, 0.005), (0.04, 13.6, 0.02), r)
    wall = 'D0C8B0'
    box(wall, (0, 6.9, 3.2), (15, 0.2, 6.4), r)
    box(wall, (7.5, 0, 3.2), (0.2, 14, 6.4), r)
    box(wall, (-7.5, 0, 0.6), (0.2, 14, 1.2), r)
    box(wall, (-7.5, 0, 5.6), (0.2, 14, 1.6), r)
    for y in (-6.4, -2.2, 2.2, 6.4):
        box(wall, (-7.5, y, 3.0), (0.2, 1.0 if abs(y) < 5 else 1.2, 3.6), r)
    for y in (-4.3, 0, 4.3):
        box('DCEAF2', (-7.62, y, 3.0), (0.04, 3.4, 3.4), r, emit=2.6)
        box('5A4630', (-7.44, y, 3.0), (0.08, 0.08, 3.4), r)
        box('5A4630', (-7.44, y, 3.0), (0.08, 3.3, 0.08), r)
    box('E0DACA', (0, 0, 6.4), (15, 14, 0.2), r)
    box('8A6E4A', (0, 5.0, 0.15), (11, 3.4, 0.3), r)
    box('5A4630', (0, 6.74, 3.2), (9.0, 0.12, 3.0), r)                  # the blackboard: plain marks, no words
    box('2E4A3A', (0, 6.66, 3.2), (8.6, 0.08, 2.6), r)
    box('5A4630', (0, 6.5, 1.84), (8.6, 0.3, 0.08), r)
    for i in range(4):
        box('E8ECE4', (-2.2, 6.6, 4.1 - i * 0.42), (2.6 - (i % 2) * 0.8, 0.03, 0.06), r, emit=0.7)
    box('E8ECE4', (1.9, 6.6, 3.0), (2.2, 0.03, 0.05), r, emit=0.7)
    box('E8ECE4', (0.8, 6.6, 3.5), (0.05, 0.03, 1.0), r, emit=0.7)
    box('E8ECE4', (1.9, 6.6, 3.55), (2.5, 0.03, 0.05), r, rot=(0, -0.45, 0), emit=0.7)
    box('6A4E34', (4.6, 4.6, 1.2), (2.2, 1.1, 0.1), r)
    box('5A4630', (4.6, 4.6, 0.75), (2.0, 0.9, 0.9), r)
    box('8A6A44', (6.2, 6.74, 3.4), (1.6, 0.08, 2.0), r)
    box('3A2C1E', (7.38, -4.6, 2.0), (0.08, 1.8, 4.0), r)
    hands = []
    for row, y in enumerate((1.4, -0.9, -3.2)):                         # pupils, kept as plain figures seen from behind
        for col, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
            box('8A6A44', (x, y, 1.1), (1.7, 0.9, 0.08), r)
            for sx in (-0.75, 0.75):
                box('5A4630', (x + sx, y, 0.55), (0.08, 0.8, 1.1), r)
            if row == 2 and col == 3:
                continue
            c = ('2A3050', 'E8E4DA', '2A3050', '3A4060')[(row + col) % 4]
            box(c, (x, y - 0.75, 1.15), (0.74, 0.4, 0.9), r)
            box('4A3826', (x, y - 0.75, 0.6), (0.8, 0.6, 0.1), r)
            add('ico_sphere', '17131A', (x, y - 0.75, 1.88), radius=0.27, subdivisions=1, parent=r)
            add('ico_sphere', 'E0B890', (x, y - 0.8, 1.84), radius=0.22, subdivisions=1, parent=r)
            if (row, col) in ((0, 1), (1, 2)):
                hands.append(mov(box(c, (x + 0.42, y - 0.75, 1.3), (0.14, 0.14, 0.7), r)))
    for x in (-3.5, 3.5):
        add('ico_sphere', 'FFF0D0', (x, 0, 5.9), radius=0.16, subdivisions=1, parent=r, emit=5)
        light((x, 0, 5.4), 380, 'FFF0D8', kind='POINT', parent=r)
    light((-6.6, 0, 3.6), 900, 'F0F6FF', 6.0, empty((2, 0, 1.4), r), parent=r)
    return dict(khands=hands)


# ---------------------------------------------------------------- set 12: a city-office counter, 2009
def set_counter(r):
    box('9A9A90', (0, 0, -0.1), (17, 12, 0.2), r, rough=0.5)
    box('D8D4C4', (0, 5.6, 3.2), (17, 0.2, 6.4), r)
    for s in (-1, 1):
        box('CCC8B8', (s * 8.5, 0, 3.2), (0.2, 12, 6.4), r)
    box('E8E6DC', (0, 0, 6.4), (17, 12, 0.2), r)
    for x in (-4, 2):
        box('FFFFFF', (x, 0.5, 6.26), (3.0, 1.0, 0.06), r, emit=5)
        light((x, 0.5, 5.9), 520, 'F4F8FF', 3.0, empty((x, 0.5, 0), r), parent=r)
    box('6A4A2E', (0, 1.6, 0.95), (15, 1.0, 1.9), r)
    box('C8B890', (0, 1.5, 1.95), (15.4, 1.4, 0.1), r, rough=0.5)
    box('FF7A1A', (0, 1.08, 1.4), (15, 0.03, 0.14), r, emit=0.5)
    for x in (-5.0, 5.0):
        box('8A8A84', (x, 1.6, 2.9), (0.1, 0.8, 1.8), r)
    box('5A6A7A', (0, 1.6, 4.3), (4.2, 0.12, 0.9), r)                   # a hanging sign, left blank
    box('E8ECEE', (0, 1.53, 4.3), (3.8, 0.04, 0.6), r, emit=0.6)
    for x in (-1.9, 1.9):
        add('cylinder', '8A8A84', (x, 1.6, 5.5), radius=0.03, depth=1.6, vertices=4, parent=r)
    for sh_ in range(3):                                                # shelves of files behind
        z = 1.2 + sh_ * 1.5
        box('8A7A5A', (0, 5.2, z - 0.1), (14, 0.7, 0.1), r)
        for i in range(22):
            if (i * 7 + sh_ * 3) % 6 == 0:
                continue
            c = ('3A5E8A', '8A3A3A', '4A7A5A', 'C8A040', '5A5A6A')[(i + sh_ * 2) % 5]
            box(c, (-6.6 + i * 0.62, 5.2, z + 0.5), (0.5, 0.6, 1.0 + ((i * 3) % 3) * 0.1), r)
    add('cylinder', 'EFE6CC', (6.4, 5.46, 4.9), rot=(PI / 2, 0, 0), radius=0.55, depth=0.06, vertices=14, parent=r, emit=0.5)
    box('1A1A1A', (6.4, 5.4, 5.05), (0.05, 0.03, 0.4), r)
    box('1A1A1A', (6.55, 5.4, 4.9), (0.34, 0.03, 0.05), r)
    add('cylinder', '8A5A3A', (7.4, -1.0, 0.5), radius=0.5, depth=1.0, vertices=8, parent=r)
    for i in range(5):
        add('cone', '3E7A4A', (7.4 + 0.3 * math.cos(i * 1.3), -1.0 + 0.3 * math.sin(i * 1.3), 1.9), rot=(0.3 * math.sin(i * 1.3), -0.3 * math.cos(i * 1.3), 0),
            radius1=0.3, radius2=0.0, depth=2.0, vertices=4, parent=r)
    box('3A5E8A', (-6.2, -3.4, 0.75), (3.4, 1.0, 0.14), r)              # waiting seats
    box('3A5E8A', (-6.2, -3.9, 1.3), (3.4, 0.12, 1.0), r)
    box('C84A3A', (1.6, 1.3, 2.03), (0.5, 0.4, 0.06), r)                # the ink pad
    book = mov(empty((-0.2, 1.25, 2.0), r))
    box('D8B878', (0, 0, 0.03), (0.86, 0.6, 0.05), book)
    box('F2F0E6', (0.0, 0, 0.06), (0.8, 0.54, 0.02), book, emit=0.25)
    for i in range(4):
        box('5A5A6A', (-0.06, 0.16 - i * 0.1, 0.075), (0.5 - (i % 2) * 0.14, 0.03, 0.01), book)
    mark = mov(box('D8362A', (0.24, -0.12, 0.078), (0.2, 0.2, 0.012), book, emit=0.6))
    stamp = mov(empty((1.6, 1.3, 2.3), r))
    add('cylinder', '3A2C1E', (0, 0, 0.3), radius=0.07, depth=0.5, vertices=6, parent=stamp)
    box('5A4630', (0, 0, 0.05), (0.24, 0.24, 0.12), stamp)
    return dict(book=book, mark=mark, stamp=stamp)


# ---------------------------------------------------------------- long-form props
def make_screen():
    """A projection screen for the hall: a pale picture of one seated figure, as in a filmed interview."""
    s = empty(FAR)
    box('1A1A1E', (0, 0.1, 0), (11.6, 0.1, 6.6), s)
    m = own_mat('screen', 'DCE4F0', 0.6, 3.0)
    use(add('plane', '000000', (0, 0, 0), rot=(PI / 2, 0, 0), size=1, scale=(11, 6, 1), parent=s), m)
    box('56627A', (-1.2, -0.05, -1.5), (3.0, 0.03, 3.0), s, emit=0.6)
    add('cylinder', '56627A', (-1.2, -0.05, 0.9), rot=(PI / 2, 0, 0), radius=0.95, depth=0.03, vertices=12, parent=s, emit=0.6)
    box('8E9AB0', (3.2, -0.05, -2.3), (3.0, 0.03, 0.22), s, emit=1.2)
    box('8E9AB0', (2.8, -0.05, -1.9), (2.2, 0.03, 0.16), s, emit=1.2)
    return s, m


def make_tanker():
    """A plain model tanker on a stand: no name, no funnel mark."""
    m = empty(FAR)
    box('2E3640', (0, 0, 0.16), (2.6, 0.42, 0.22), m)
    box('8A2E22', (0, 0, 0.04), (2.6, 0.42, 0.1), m)
    box('2E3640', (1.42, 0, 0.16), (0.36, 0.3, 0.22), m, rot=(0, 0, PI / 4))
    box('E8E4DA', (-0.9, 0, 0.42), (0.5, 0.36, 0.3), m)
    box('E8E4DA', (0.2, 0, 0.36), (0.3, 0.3, 0.18), m)
    add('cylinder', '3A3A3E', (-1.0, 0, 0.72), radius=0.07, depth=0.34, vertices=6, parent=m)
    box('6A4A2E', (0, 0, -0.06), (1.8, 0.3, 0.08), m)
    return m


def make_desk_things():
    """Paper, an ink stone and a brush for the low table. The marks on the paper are plain strokes, not writing."""
    d = empty(FAR)
    box('F2F0E6', (0, 0, 0.01), (1.3, 0.9, 0.02), d, emit=0.3)
    box('E8E4D8', (0.9, 0.5, 0.03), (0.9, 0.7, 0.06), d, rot=(0, 0, 0.2), emit=0.2)
    for c in range(5):
        for j in range(4 - (c % 2)):
            box('2A2A34', (0.5 - c * 0.22, 0.3 - j * 0.17, 0.025), (0.035, 0.11, 0.006), d)
    box('2A2A2E', (-1.0, 0.25, 0.04), (0.34, 0.5, 0.08), d)
    brush = mov(empty((0, 0, 0), d))
    add('cylinder', '8A6A44', (0, 0, 0.3), rot=(0.5, 0, 0), radius=0.022, depth=0.6, vertices=5, parent=brush)
    add('cone', '1A1A1E', (0, 0.15, 0.05), rot=(0.5 + PI, 0, 0), radius1=0.03, radius2=0.0, depth=0.12, vertices=5, parent=brush)
    return d, brush


def make_shelf_things():
    """For the alcove shelf: a small frame (left empty of any face) and one stick of incense."""
    d = empty(FAR)
    box('3A2C1E', (0, 0, 0.3), (0.06, 0.5, 0.62), d)
    box('C8C4B8', (0.04, 0, 0.3), (0.02, 0.4, 0.5), d, emit=0.3)
    add('cylinder', '6A6A70', (0.15, 0.65, 0.07), radius=0.12, depth=0.14, vertices=8, parent=d)
    add('cylinder', '5A3A2A', (0.15, 0.65, 0.34), radius=0.012, depth=0.44, vertices=4, parent=d)
    add('ico_sphere', 'FF7A1A', (0.15, 0.65, 0.57), radius=0.025, subdivisions=1, parent=d, emit=14)
    for z in (0.1, 0.24):
        box('F4F2EA', (0.1, -0.6, z), (0.3, 0.3, 0.1), d)
    return d


_build0, _reset0 = build, reset


def build():
    S = _build0()
    for name, fn in (('dorm', set_dorm), ('naga', set_naga), ('room', set_room), ('car', set_car), ('hut', set_hut), ('klass', set_klass),
                     ('counter', set_counter)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    K.add, K.empty = add, empty                                         # the extra cast is built with the fast primitives too
    try:
        _extra_cast(S)
    finally:
        K.add, K.empty = _kit_add, _kit_empty
    _extra_props(S)
    return S


def _extra_cast(S):
    S['cols'] = [K.Rig(COLS[0], hair_head(SKIN, '1A1616', glasses=True)), K.Rig(COLS[1], cap_head('CF9E70', '17131A', '6A6450'))]
    S['cbags'] = [add('cube', c, (0.5, 0.05, -0.1), scale=(0.16, 0.5, 0.42), size=1, parent=rig.body) for rig, c in zip(S['cols'], ('6A5A40', '4E5A4A'))]
    S['hisako'] = K.Rig(HISAKO, bun_head('E0B890', '17131A'))
    add('cube', 'E8E0D0', (0, -0.28, 0.9), rot=(0, 0, 0.5), scale=(0.34, 0.04, 0.09), size=1, parent=S['hisako'].body)
    add('cube', 'E8E0D0', (0, -0.28, 0.9), rot=(0, 0, -0.5), scale=(0.34, 0.04, 0.09), size=1, parent=S['hisako'].body)
    add('cylinder', '4A3A58', (0, 0, 0.36), radius=0.36, depth=0.2, vertices=8, parent=S['hisako'].body)
    add('cone', '5A4868', (0, 0, -0.42), radius1=0.42, radius2=0.31, depth=0.9, vertices=8, parent=S['hisako'].body)
    S['doc'] = K.Rig(DOCTOR, hair_head('D2A27A', '4A4A50', glasses=True))
    add('cone', 'E9EDEE', (0, 0, -0.3), radius1=0.4, radius2=0.31, depth=0.66, vertices=8, parent=S['doc'].body)
    S['officer'] = K.Rig(OFFICER, cap_head('D8A888', '6A4A2E', 'A69A6C'))
    add('cube', '6A5A30', (0, -0.3, 0.84), scale=(0.07, 0.03, 0.4), size=1, parent=S['officer'].body)
    S['clerk'] = K.Rig(CLERK, hair_head('D8AC84', '2A2A30', glasses=True))
    S['kids'] = [K.Rig(c, K.human_head('E0B890', '17131A') if i != 1 else bun_head('E0B890', '17131A')) for i, c in enumerate(KIDS)]
    S['cast'] += S['cols'] + [S['hisako'], S['doc'], S['officer'], S['clerk']] + S['kids']


def _extra_props(S):
    S['screen'], S['screenmat'] = make_screen()
    mov(S['screen'])
    S['tanker'] = mov(make_tanker())
    S['things'], S['brush'] = make_desk_things()
    mov(S['things'])
    S['shelf'] = mov(make_shelf_things())
    S['bowl'] = mov(add('cylinder', 'E8ECEE', FAR, radius=0.2, depth=0.14, vertices=8))
    S['pointer'] = add('cylinder', 'C8A868', (0, 0, -0.95), radius=0.02, depth=1.0, vertices=4, parent=S['yama'].el[1])


def reset(S):
    _reset0(S)
    for o in S['cbags']:
        o.hide_render = True
    S['pointer'].hide_render = True
    S['mark'].hide_render = True
    tint(S['screenmat'], 'DCE4F0', 3.0)


def bags(S, on=True):
    for o in S['cbags']:
        o.hide_render = not on


def swing(lt, a=0.5, f=2.6):
    return a * math.sin(lt * f)


def breathe(lt, f=2.0, a=0.03):
    return a * math.sin(lt * f)


KNEEL = dict(lL=(0.15, 2.5), lR=(0.15, 2.5), lift=-0.5)
FLOOR = dict(lL=(1.5, 2.2), lR=(1.2, 2.0), lift=-0.86)


# ---------------------------------------------------------------- shots: Nagasaki, before
def yama_draws(S, k, t, lt):
    """Before any of it: at his drawing table in Nagasaki. Rook looks over the sheet."""
    A = office_base(S)
    S['yama'].place(A(-1.6, 2.15, 0.1), PI)
    S['yama'].apply(P('sit', lift=-0.42, lean=0.34, aL=(1.2, 0.1, 0.8), aR=(1.25 + 0.1 * math.sin(lt * 5), 0.1 + 0.1 * math.sin(lt * 2.3), 0.8), head=(0.3, swing(lt, 0.1, 1.3))))
    draughtsmen(S, A, t, 0.0)
    S['men'][0].place(A(-5.2, -1.65, 0.1), PI)
    S['boss'].place(A(5.0, 4.9, 0), 0.5)
    S['boss'].apply(P('stand', aL=(0.5, 0.1, 1.2), aR=(0.5, 0.1, 1.2), head=(0.3, 0.0)))
    S['rook'].place(A(-3.4, 4.1, 0), PI / 2 + 0.5)
    S['rook'].apply(P('stand', lean=0.22, aR=(0.9, -0.2, 2.1, 0.8 + 0.25 * math.sin(lt * 6)), head=(0.22, -0.3)))
    cam(S, A(lerp(2.4, 1.6, k), lerp(-0.4, 0.4, k), lerp(3.2, 2.9, k)), A(-2.0, 3.0, 2.15), 34)


def rook_plan(S, k, t, lt):
    A = office_base(S)
    S['yama'].place(A(-1.6, 2.15, 0.1), PI)
    S['yama'].apply(P('sit', lift=-0.42, lean=0.34, aL=(1.2, 0.1, 0.8), aR=(1.25 + 0.1 * math.sin(lt * 5), 0.1, 0.8), head=(0.3, 0.0)))
    S['rook'].place(A(-3.4, 4.1, 0), PI / 2 + 0.5)
    up = ease((lt - 0.5) / 0.5)
    S['rook'].apply(blend(P('stand', lean=0.22, aR=(0.9, -0.2, 2.1, 0.8 + 0.25 * math.sin(lt * 7)), head=(0.22, -0.3)),
                          P('stand', lean=0.05, aR=(0.5, 0.1, 1.2, 0.5), head=(-0.05, 0.35)), up))
    S['face']['rook'] = 'deadpan' if up < 0.5 else 'calm'
    cam(S, A(lerp(-0.4, -0.9, k), lerp(1.2, 1.6, k), 3.0), A(-3.3, 4.0, 2.75), 52)


def naga_base(S, mood='day'):
    A = show(S, 'naga')
    if mood == 'dusk':
        sky(S, 'E89A6A', 1.0)
        S['nagasun'].data.energy = 1.4
        S['nagasun'].data.color = K.hexc('FF9A60')[:3]
        tint(S['doormat'], 'FFD8A0', 3.2)
        S['porchlight'].data.energy = 380
        S['fillk'] = 4.0
    else:
        sky(S, '9CCAEA', 1.0)
        S['nagasun'].data.energy = 3.2
        S['nagasun'].data.color = K.hexc('FFF0D8')[:3]
        tint(S['doormat'], 'EDE4C8', 0.9)
        S['porchlight'].data.energy = 0
        S['fillk'] = 6.0
    return A


def farewell(S, k, t, lt):
    """Dramatised: he leaves for Hiroshima; Hisako sees him off at the door."""
    A = naga_base(S)
    S['hisako'].place(A(-10.0, 5.2, 0.6), 0.0)
    bow = math.sin(PI * ease(lt / 1.4))
    S['hisako'].apply(P('stand', aL=(0.5, -0.2, 0.9, 0.9), aR=(0.5, -0.2, 0.9, 0.9), lean=0.3 * bow, head=(0.15 * bow, 0.0)))
    go = ease((lt - 1.3) / 0.6)
    x = -9.6 + 3.2 * max(0.0, lt - 1.5) * 0.8
    S['yama'].place(A(x, 2.4, 0), lerp(PI, PI / 2, go))
    S['yama'].apply(blend(P('stand', lean=0.4 * bow, head=(0.2 * bow, 0.0)), walk(t, 1.4), go))
    S['bag'].hide_render = False
    cam(S, A(lerp(-3.4, -4.2, k), lerp(-5.2, -4.4, k), lerp(2.9, 2.6, k)), A(-9.0, 4.4, 2.3), 34)


def hisako_door(S, k, t, lt):
    A = naga_base(S)
    S['hisako'].place(A(-10.0, 5.2, 0.6), 0.0)
    up = ease(lt / 0.6)
    S['hisako'].apply(blend(P('stand', aL=(0.5, -0.2, 0.9, 0.9), aR=(0.5, -0.2, 0.9, 0.9)),
                            P('stand', aL=(0.5, -0.2, 0.9, 0.9), aR=(1.3, 0.3, 1.7, 0.0 + 0.3 * math.sin(lt * 5)), head=(-0.05, -0.25)), up))
    cam(S, A(lerp(-7.6, -8.0, k), lerp(0.2, 0.9, k), lerp(3.2, 3.3, k)), A(-10.0, 5.2, 3.2), 56)


def to_work(S, k, t, lt):
    """9 August: bandaged, he walks to the office. Rook follows."""
    A = naga_base(S)
    x = lerp(9.5, 13.5, k)
    S['yama'].place(A(x, -0.4, 0), PI / 2)
    S['yama'].apply(dict(walk(t, 1.1), aL=(0.7, -0.2, 1.5, 0.9)))
    bandaged(S)
    S['rook'].place(A(x - 3.4, -1.5, 0), PI / 2 - 0.1)
    S['rook'].apply(dict(walk(t + 0.4, 1.1), head=(0.1, 0.2)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(4.6, 6.6, k), lerp(-8.4, -7.6, k), lerp(2.6, 3.0, k)), A(x + 2.4, 2.4, 3.6), 30)


def porch(S, k, t, lt):
    """The quiet years: he sits on his step at dusk and says nothing. Rook sits beside him."""
    A = naga_base(S, 'dusk')
    S['yama'].place(A(-10.9, 4.7, 0.08), 0.0)
    S['yama'].apply(P('sit', lean=0.3, aL=(0.75, 0.1, 0.9), aR=(0.75, 0.1, 0.9), head=(0.12 + breathe(lt, 1.4, 0.05), 0.15)))
    S['face']['yama'] = 'tired'
    S['rook'].place(A(-9.1, 4.7, 0.08), 0.0)
    S['rook'].apply(P('sit', lean=0.22, aL=(0.75, 0.1, 0.9), aR=(0.75, 0.1, 0.9), head=(0.1, lerp(0.0, -0.75, ease((lt - 0.6) / 0.8)))))
    S['face']['rook'] = 'sad'
    S['hat_tip'] = 0.4
    for i, o in enumerate(S['fea'][:2]):                               # two moths at the door light
        o.location = A(-10 + 0.9 * math.sin(t * 3.1 + i * 2), 4.9 + 0.3 * math.cos(t * 2.3 + i), 3.4 + 0.3 * math.sin(t * 4 + i))
        o.rotation_euler = (t * 5, t * 3, i)
        o.scale = (0.5, 0.5, 0.5)
    cam(S, A(lerp(-8.8, -9.4, k), lerp(-0.2, 0.6, k), lerp(2.2, 2.4, k)), A(-10.0, 4.7, 1.95), 36, fcol='FFC8A0')


# ---------------------------------------------------------------- shots: the lodging street, 6 August
def dorm_base(S):
    A = show(S, 'dorm')
    sky(S, '8EC4EC', 1.0)
    S['fillk'] = 6.0
    return A


def dorm_wide(S, k, t, lt):
    A = dorm_base(S)
    y = lerp(7.2, 2.6, k)
    for rig, x, ph in ((S['yama'], 0.0, 0.0), (S['cols'][0], -1.5, 0.3), (S['cols'][1], 1.4, 0.6)):
        rig.place(A(x, y + abs(x) * 0.7, 0), 0.0)
        rig.apply(walk(t + ph, 1.4))
    S['bag'].hide_render = False
    bags(S)
    S['rook'].place(A(4.2, 3.6, 0), -0.7)
    S['rook'].apply(P('cross', head=(0.0, lerp(0.6, -0.2, ease(k)))))
    cam(S, A(lerp(7.0, 6.0, k), lerp(-6.4, -5.4, k), lerp(3.8, 3.1, k)), A(0.8, 4.4, 2.6), 36)


def three_go(S, k, t, lt):
    A = dorm_base(S)
    x = lerp(12, 15.4, k)
    for rig, y, ph, dx in ((S['yama'], -1.3, 0.0, 0.0), (S['cols'][0], 0.0, 0.3, 0.5), (S['cols'][1], 1.3, 0.6, -0.3)):
        rig.place(A(x + dx, y, 0), PI / 2)
        rig.apply(walk(t + ph, 1.4))
    S['bag'].hide_render = False
    bags(S)
    cam(S, A(x + 8.6, lerp(-3.0, -2.2, k), 2.6), A(x, 0.0, 2.4), 40)


def forgot(S, k, t, lt):
    """He stops and pats his pocket. What he forgot differs by account (his name seal, or a travel permit)."""
    A = dorm_base(S)
    stop = ease(lt / 0.35)
    back = ease((lt - 1.1) / 0.6)
    S['yama'].place(A(16.0, -1.3, 0), PI / 2 - 1.3 * back)
    S['yama'].apply(blend(walk(t, 1.4), P('stand', aR=(0.75, -0.35, 2.0, 1.1 + 0.3 * math.sin(lt * 9)), aL=(0.3, 0.1, 1.4, 0.8), head=(lerp(0.4, 0.0, back), 0.0)), stop))
    S['bag'].hide_render = False
    bags(S)
    for i, (rig, y) in enumerate(zip(S['cols'], (0.1, 1.4))):
        xx = 18.6 + i * 0.5 + min(lt, 1.0) * 1.0
        turn = ease((lt - 0.8) / 0.5)
        rig.place(A(xx, y, 0), PI / 2 + 2.4 * turn)
        rig.apply(blend(walk(t + i * 0.3, 1.4), P('stand', head=(0.0, 0.2)), turn))
    cam(S, A(lerp(19.8, 19.2, k), lerp(-5.0, -4.4, k), 2.7), A(16.6, -0.9, 2.55), 46)


def goes_back(S, k, t, lt):
    A = dorm_base(S)
    S['yama'].place(A(lerp(13, 8.2, k), -1.2, 0), -PI / 2)
    S['yama'].apply(walk(t, 1.7))
    S['bag'].hide_render = False
    bags(S)
    for i, (rig, y) in enumerate(zip(S['cols'], (0.2, 1.4))):
        rig.place(A(lerp(18, 21.5, k) + i * 0.6, y, 0), PI / 2)
        rig.apply(walk(t + i * 0.3, 1.4))
    S['rook'].place(A(15.2, -2.6, 0), -0.2)
    S['rook'].apply(P('stand', aR=(0.9, -0.2, 2.1, 0.9), head=(0.0, lerp(0.9, -0.9, ease(k)))))
    cam(S, A(lerp(15.5, 14.5, k), lerp(-11.5, -10.5, k), lerp(5.4, 4.6, k)), A(14.6, -0.6, 2.2), 30)


# ---------------------------------------------------------------- shots: afterwards, Hiroshima
def found_three(S, k, t, lt):
    """He finds his two colleagues alive. Shown on the road in the dust; nothing else is shown."""
    A = after(S, t)
    y = lerp(44.5, 47.5, ease(k))
    S['yama'].place(A(-0.6, y, 0), PI)
    S['yama'].apply(dict(walk(t, 1.0), aL=(0.7, -0.2, 1.5, 0.9), lean=0.2))
    S['face']['yama'] = 'tired'
    wave = ease((lt - 0.4) / 0.5)
    S['cols'][0].place(A(1.0, 51.0, 0), 0.2)
    S['cols'][0].apply(blend(P('stand', lean=0.15), P('stand', aR=(2.6, 0.4, 0.3 + 0.3 * math.sin(lt * 7)), head=(-0.1, 0.0)), wave))
    S['cols'][1].place(A(-1.9, 52.2, 0), -0.2)
    S['cols'][1].apply(P('stand', lean=0.2, aL=(0.6, 0.0, 1.4, 0.8), head=(0.1, 0.0)))
    S['rook'].place(A(3.7, 50.6, 0), -PI / 2 - 0.5)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.1, 0.2)))
    S['face']['rook'] = 'sad'
    drift_dust(S, A, t, (-1, 66, 0), n=10, spread=24, size=1.8, speed=1.8)
    fall_bits(S, A, t, (0, 49, 0), n=10, spread=10, speed=0.7, hgt=6)
    cam(S, A(lerp(5.6, 4.8, k), lerp(41.6, 42.4, k), lerp(2.3, 2.6, k)), A(0.2, 50.0, 2.5), 34)


def shelter_three(S, k, t, lt):
    A = shelter_base(S, t)
    S['yama'].place(A(-2.05, 2.6, 0.0), PI * 0.5)
    S['yama'].apply(P('sit', lift=-0.5, lean=0.42, aL=(0.6, 0.0, 1.3, 0.6), aR=(0.9, -0.45, 1.7, 1.4), head=(0.5 - 0.06 * math.sin(lt * 2.5), -0.2)))
    S['face']['yama'] = 'tired'
    S['wraps'][3].hide_render = False
    S['cols'][0].place(A(2.05, 3.6, 0.0), -PI * 0.5)
    S['cols'][0].apply(P('sit', lift=-0.5, lean=0.5, aL=(0.9, 0.1, 1.2), aR=(0.9, 0.1, 1.2), head=(0.55 + breathe(lt, 1.7, 0.05), 0.0)))
    S['cols'][1].place(A(2.05, 5.0, 0.0), -PI * 0.5)
    S['cols'][1].apply(P('sit', lift=-0.5, lean=-0.05, head=(-0.25, 0.3 + breathe(lt, 1.1, 0.1))))
    cam(S, A(lerp(0.5, 0.1, k), lerp(-4.2, -3.0, k), lerp(2.5, 2.2, k)), A(0.0, 4.0, 1.7), 30, fill=2.6, fcol='FFC890')


def platform_wait(S, k, t, lt):
    A = rail_mood(S, 'dawn')
    x = lerp(-52, -24, ease(k))
    S['train'].location = (x, 5, 0.34)
    roll(S, x)
    steam(S, A, x, t)
    for i, (rig, px, py) in enumerate(((S['yama'], 0.4, 1.2), (S['cols'][0], 2.0, 1.0), (S['cols'][1], 3.4, 1.3))):
        rig.place(A(px, py, 1.0), PI + 0.35)
        rig.apply(P('stand', lean=0.12, head=(0.1, 0.5), aL=(0.7, -0.2, 1.5, 0.9) if i == 0 else (0.05, 0.12, 0.15)))
    S['face']['yama'] = 'tired'
    S['wraps'][3].hide_render = False
    S['rook'].place(A(-1.9, -3.05, 1.12), PI)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', lean=0.2, aL=(0.8, -0.2, 1.5, 1.0), aR=(0.8, -0.2, 1.5, 1.0), head=(0.15, lerp(0.0, 0.5, ease(k)))))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(8.4, 7.6, k), lerp(3.2, 3.0, k), lerp(2.7, 2.5, k)), A(0.6, 0.4, 2.7), 32, fill=1.6)


def platform_night(S, k, t, lt):
    """The end: Rook alone on the platform, looking down the line."""
    A = rail_mood(S, 'night')
    S['rook'].place(A(0.6, 0.9, 1.0), PI + 0.25)
    S['rook'].apply(P('stand', aL=(0.3, 0.1, 0.5), aR=(0.3, 0.1, 0.5), head=(lerp(-0.05, 0.3, ease(k)), lerp(0.5, 0.0, ease(k)))))
    S['face']['rook'] = 'sad'
    for i, o in enumerate(S['fea'][:2]):
        o.location = A(1.7 + 0.7 * math.sin(t * 2.7 + i * 2), -0.6 + 0.5 * math.cos(t * 2.1 + i), 4.2 + 0.3 * math.sin(t * 3.7 + i))
        o.rotation_euler = (t * 5, t * 3, i)
        o.scale = (0.5, 0.5, 0.5)
    cam(S, A(lerp(5.0, 3.6, k), lerp(11.5, 10.0, k), lerp(4.4, 3.8, k)), A(0.5, 0.4, 3.0), 46, fill=1.6, fcol='FFD0A0')


# ---------------------------------------------------------------- shots: the carriage
def car_base(S, t, lt):
    A = show(S, 'car')
    sky(S, 'F0B090', 1.0)
    S['carnear'].location = (-((t * 9.0) % 12.0), 0, 0)
    S['carfar'].location = (24 - 2.0 * lt, 0, 0)
    S['fillk'] = 1.6
    return A


def carriage_wide(S, k, t, lt):
    """The train to Nagasaki. He sits at the window with his arm wrapped; Rook stands in the aisle, hat off."""
    A = car_base(S, t, lt)
    S['yama'].place(A(-1.55, 0.85, 0.2), PI / 2)
    S['yama'].apply(P('sit', lean=0.12, aL=(0.6, 0.0, 1.3, 0.6), aR=(0.7, -0.1, 1.5, 1.0), head=(0.3 + breathe(lt, 1.6), -0.55)))
    S['face']['yama'] = 'shut'
    S['wraps'][3].hide_render = False
    S['cols'][0].place(A(1.55, 1.0, 0.2), -PI / 2)
    S['cols'][0].apply(P('sit', lean=0.3, head=(0.45, 0.0)))
    S['cols'][1].place(A(1.55, 0.25, 0.2), -PI / 2)
    S['cols'][1].apply(P('sit', lean=0.05, head=(0.0, -0.5 + breathe(lt, 0.9, 0.1))))
    S['rook'].place(A(-3.5, -0.4, 0), PI / 2 - 0.6)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.12, 0.2), lean=0.03 * math.sin(t * 6)))
    S['face']['rook'] = 'sad'
    sw = 0.012 * math.sin(t * 6.3)
    cam(S, A(lerp(0.4, -0.4, k), -5.8, 2.5 + sw), A(-0.8, 0.8, 1.95), 32, roll=sw, fcol='FFD0A0')


# ---------------------------------------------------------------- shots: the room at home
def room_base(S, mood='day'):
    A = show(S, 'room')
    S['roomlamp'].rotation_euler = (0, 0, 0)
    if mood == 'night':
        sky(S, '05060A', 1.0)
        tint(S['shoji'], '2A3A5E', 0.5)
        S['roomkey'].data.energy = 90
        S['roomkey'].data.color = K.hexc('7A9AE0')[:3]
        tint(S['roomlampmat'], 'FFD8A0', 9)
        S['roomlight'].data.energy = 520
        S['fillk'] = 0.7
    elif mood == 'dusk':
        sky(S, '20141A', 1.0)
        tint(S['shoji'], 'F0A060', 2.2)
        S['roomkey'].data.energy = 700
        S['roomkey'].data.color = K.hexc('FFB070')[:3]
        tint(S['roomlampmat'], 'FFD8A0', 0.0)
        S['roomlight'].data.energy = 0
        S['fillk'] = 0.8
    else:
        sky(S, 'A8C8E0', 1.0)
        tint(S['shoji'], 'F4F0E0', 3.0)
        S['roomkey'].data.energy = 900
        S['roomkey'].data.color = K.hexc('FFF4E0')[:3]
        tint(S['roomlampmat'], 'FFD8A0', 0.0)
        S['roomlight'].data.energy = 0
        S['fillk'] = 1.2
    return A


def treat_cast(S, A, lt, face):
    S['blanket'].location = (0.5, 2.0, -40)
    S['yama'].place(A(-1.5, 0.5, 0), -PI / 2)
    S['yama'].apply(P('sit', lean=0.1, aL=(1.2, 0.3, 0.3), aR=(0.6, 0.0, 1.2, 0.5), head=(0.25 + breathe(lt), 0.35), **FLOOR))
    S['face']['yama'] = face
    bandaged(S)
    S['doc'].place(A(-3.4, 0.0, 0), PI / 2 + 0.25)
    w = math.sin(lt * 5.0)
    S['doc'].apply(P('stand', lean=0.3, aL=(1.1 + 0.18 * w, 0.0, 0.9), aR=(1.1 - 0.18 * w, 0.2, 0.7), head=(0.3, 0.0), **KNEEL))


def treated(S, k, t, lt):
    """Home: his burns are dressed. The doctor is a stand-in; where he was treated differs by account."""
    A = room_base(S)
    treat_cast(S, A, lt, 'tired')
    S['rook'].place(A(3.1, 2.6, 0), -PI / 2 - 0.5)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.15, 0.1)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(0.4, -0.4, k), lerp(-6.6, -5.8, k), lerp(2.9, 2.5, k)), A(-1.4, 0.8, 1.7), 30)


def bandage_cu(S, k, t, lt):
    A = room_base(S)
    treat_cast(S, A, lt, 'shut')
    cam(S, A(lerp(-1.6, -2.0, k), lerp(-2.9, -2.5, k), lerp(2.0, 2.2, k)), A(-2.3, 0.3, 1.75), 54)


def gets_up(S, k, t, lt):
    """9 August: he gets up and goes to work."""
    A = room_base(S)
    S['blanket'].location = (1.3, 2.3, 0.3)
    S['blanket'].rotation_euler = (0, 0, 0.3)
    u = ease((lt - 0.25) / 1.1)
    S['yama'].place(A(-0.2, lerp(1.9, 1.1, u), lerp(0.24, 0.0, u)), 0.15)
    S['yama'].apply(blend(P('sit', lean=0.35, aL=(0.6, 0.1, 1.2, 0.8), aR=(0.9, 0.2, 0.4), head=(0.35, 0.0), **FLOOR),
                          P('stand', lean=0.08, aL=(0.7, -0.2, 1.5, 0.9), head=(-0.05, 0.2)), u))
    bandaged(S)
    cam(S, A(lerp(2.6, 2.0, k), lerp(-4.8, -4.2, k), lerp(1.5, 2.3, k)), A(-0.1, 1.5, lerp(1.5, 2.4, u)), 34)


def in_bed(S, k, t, lt):
    """After Nagasaki: more than a week of fever. Hisako, who also lived through it, is shown beside him (dramatised)."""
    A = room_base(S, 'night')
    S['roomlamp'].rotation_euler = (0.05 * math.sin(t * 1.9), 0.06 * math.sin(t * 1.3), 0)
    S['blanket'].location = (0.85, 2.0, 0.5)
    S['blanket'].scale = (1.9, 2.5, 0.5)
    S['yama'].place(A(1.5, 2.0, 0.52), PI / 2, pitch=-PI / 2)
    S['yama'].apply(P('stand', aL=(0.2, 0.25, 0.3), aR=(0.2, 0.25, 0.3), head=(0.0, 0.25 * math.sin(lt * 0.9))))
    S['face']['yama'] = 'shut'
    S['wraps'][0].hide_render = False
    S['wraps'][1].hide_render = False
    S['hisako'].place(A(-0.5, 3.75, 0), 0.1)
    dab = 0.5 + 0.5 * math.sin(lt * 2.2)
    S['hisako'].apply(P('stand', lean=0.5, aR=(1.1 + 0.25 * dab, 0.3, 0.4), aL=(0.6, 0.0, 1.2, 0.6), head=(0.45, -0.2), **KNEEL))
    S['bowl'].location = A(-1.6, 3.6, 0.08)
    cam(S, A(lerp(-3.4, -2.9, k), lerp(-2.6, -2.2, k), lerp(2.5, 2.2, k)), A(-0.5, 2.3, 0.95), 36, fill=2.0, fcol='FFC890')


def rook_room(S, k, t, lt):
    A = room_base(S, 'dusk' if S['prm'].get('v') == 2 else 'night')
    S['roomlamp'].rotation_euler = (0.05 * math.sin(t * 1.9), 0.06 * math.sin(t * 1.3), 0)
    S['rook'].place(A(3.6, 2.4, 0), -PI / 2 + 0.7)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', lean=0.3, aL=(0.8, -0.2, 1.5, 1.0), aR=(0.8, -0.2, 1.5, 1.0), head=(lerp(0.1, 0.4, ease(k)), 0.2), **FLOOR))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(0.2, 0.7, k), lerp(-2.4, -1.8, k), lerp(1.9, 1.7, k)), A(3.5, 2.4, 1.45), 44, fill=2.6, fcol='FFC890')


def family(S, k, t, lt):
    """The years after: a family at the table. The children are stand-ins; none is a likeness."""
    A = room_base(S)
    S['blanket'].location = (0.5, 2.0, -40)
    S['yama'].place(A(0.3, -0.8, 0), PI / 2)
    S['yama'].apply(P('sit', lean=0.15, aR=(0.9 + 0.2 * math.sin(lt * 3), 0.1, 1.2), aL=(0.7, 0.0, 1.3, 0.5), head=(0.15, swing(lt, 0.3, 1.2)), **FLOOR))
    S['face']['yama'] = 'warm'
    S['hisako'].place(A(4.5, -0.8, 0), -PI / 2)
    S['hisako'].apply(P('stand', lean=0.15, aL=(0.9, 0.1, 1.1), aR=(0.9, 0.1, 1.1), head=(0.15, swing(lt + 1, 0.3, 1.0)), **KNEEL))
    for i, (kid, x, y, yaw) in enumerate(zip(S['kids'], (1.8, 3.0, 2.4), (0.7, 0.7, -2.3), (0.0, 0.0, PI))):
        kid.root.scale = (0.56, 0.56, 0.56) if i else (0.66, 0.66, 0.66)
        kid.place(A(x, y, 0), yaw)
        kid.apply(P('sit', lean=0.1, aL=(0.9 + 0.3 * math.sin(lt * 4 + i), 0.1, 1.2), aR=(0.9 + 0.3 * math.cos(lt * 3.3 + i), 0.1, 1.2),
                    head=(0.1, swing(lt + i, 0.5, 1.7)), **FLOOR))
    S['bowl'].location = A(2.4, -0.8, 0.95)
    cam(S, A(lerp(1.4, 2.4, k), lerp(-7.2, -6.6, k), lerp(3.4, 3.1, k)), A(2.4, -0.4, 1.4), 32)


def old_at_table(S, A, t, lt, write=1.0):
    S['old'].place(A(2.4, 0.5, 0), 0.0)
    S['old'].root.scale = (0.95, 0.95, 0.95)
    S['old'].apply(P('sit', lean=0.3, aL=(0.9, 0.1, 1.0), aR=(1.0 + 0.06 * math.sin(lt * 6) * write, 0.0 + 0.05 * math.sin(lt * 2.1), 0.9), head=(0.4, 0.05), **FLOOR))
    S['things'].location = A(2.4, -0.7, 0.88)
    S['brush'].location = (0.35 + 0.02 * math.sin(lt * 6), 0.32 - 0.5 * ((lt * 0.3) % 1), 0.02)


def writes(S, k, t, lt):
    """In his eighties he writes it down. Rook reads a page."""
    A = room_base(S, 'night')
    S['blanket'].location = (0.5, 2.0, -40)
    old_at_table(S, A, t, lt)
    S['rook'].place(A(4.9, -0.8, 0), -PI / 2 - 0.2)
    S['rook'].apply(P('sit', lean=0.2, aR=(1.3, 0.1, 1.5, 0.3), aL=(0.8, -0.1, 1.4, 0.9), head=(0.25 + breathe(lt, 1.5, 0.05), 0.1), **FLOOR))
    S['face']['rook'] = 'sad'
    S['papers'][0].location = A(4.2, -0.75, 1.75)
    S['papers'][0].rotation_euler = (1.2, 0, PI / 2)
    cam(S, A(lerp(-0.4, 0.4, k), lerp(-5.6, -5.0, k), lerp(2.6, 2.3, k)), A(2.9, -0.2, 1.5), 34, fcol='FFC890')


def poem_cu(S, k, t, lt):
    A = room_base(S, 'night')
    S['blanket'].location = (0.5, 2.0, -40)
    old_at_table(S, A, t, lt)
    cam(S, A(lerp(1.5, 1.9, k), lerp(-2.6, -2.2, k), lerp(2.5, 2.3, k)), A(2.5, -0.5, 0.95), 50, fill=2.0, fcol='FFC890')


def alone(S, k, t, lt):
    """2005: his son dies of cancer. An old man before a small shelf; no face is shown in the frame."""
    A = room_base(S, 'dusk')
    S['blanket'].location = (0.5, 2.0, -40)
    S['old'].place(A(-3.3, 1.6, 0), -PI / 2)
    S['old'].root.scale = (0.95, 0.95, 0.95)
    S['old'].apply(P('stand', lean=0.25, aL=(0.9, -0.3, 1.9, 1.2), aR=(0.9, -0.3, 1.9, 1.2), head=(lerp(0.1, 0.5, ease(lt / 1.2)), 0.0), **KNEEL))
    S['face']['old'] = 'shut'
    S['shelf'].location = A(-5.2, 1.6, 1.0)
    for i, o in enumerate(S['puffs'][:4]):
        u = (t * 0.22 + i / 4) % 1
        o.location = A(-5.05 + 0.12 * math.sin(u * 7 + i), 2.25 + 0.1 * math.sin(u * 5), 1.6 + u * 2.2)
        s = 0.04 + 0.1 * u
        o.scale = (s, s, s * 1.6)
    S['rook'].place(A(-0.9, 3.3, 0), -PI / 2 + 0.5)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(lerp(0.1, 0.35, ease(k)), 0.0)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(1.0, 0.4, k), lerp(-3.9, -3.4, k), lerp(2.5, 2.2, k)), A(-3.2, 1.9, 1.6), 34, fill=2.0, fcol='FFB880')


def old_window(S, k, t, lt):
    """2009: an old man by the paper screens, with the booklet in his hands. Rook sits with him."""
    A = room_base(S)
    S['blanket'].location = (0.0, 1.5, 0.3)
    S['blanket'].scale = (1.9, 1.5, 0.5)
    S['old'].place(A(-0.6, 2.2, 0), 0.5)
    S['old'].root.scale = (0.95, 0.95, 0.95)
    S['old'].apply(P('sit', lean=0.2, aL=(0.95, -0.1, 1.2, 0.6), aR=(0.95, -0.1, 1.2, 0.6), head=(0.1 + breathe(lt, 1.8, 0.06), -0.45), **FLOOR))
    S['face']['old'] = 'warm'
    S['jaw']['old'] = 0.2 * (0.5 + 0.5 * math.sin(t * 13)) * (0.5 + 0.5 * math.sin(t * 2.7))
    S['book'].parent = None
    S['book'].location = A(-0.28, 1.55, 1.28)
    S['book'].rotation_euler = (0.5, 0, 0.5)
    S['rook'].place(A(2.6, 1.0, 0), -PI / 2 + 0.3)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', lean=0.15, aL=(0.8, -0.2, 1.5, 1.0), aR=(0.8, -0.2, 1.5, 1.0), head=(0.0, 0.15 * math.sin(lt * 1.3)), **FLOOR))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(1.6, 0.9, k), lerp(-4.4, -3.8, k), lerp(2.2, 2.0, k)), A(0.9, 1.7, 1.5), 38)


# ---------------------------------------------------------------- shots: after the war
def translator(S, k, t, lt):
    """He works as a translator for the occupation forces. The officer and the townsman are stand-ins; no insignia."""
    A = show(S, 'hut')
    sky(S, 'A8C8E0', 1.0)
    S['fillk'] = 1.2
    S['fan'].rotation_euler = (0, 0, t * 4.0)
    S['officer'].place(A(1.6, 3.0, 0.32), 0.0)
    S['officer'].apply(P('sit', lean=0.1, aR=(1.0, 0.2, 0.9 + 0.3 * math.sin(lt * 4)), aL=(0.9, 0.0, 1.2, 0.6), head=(0.05, 0.3)))
    S['men'][1].place(A(3.9, -0.6, 0), PI + 0.35)
    S['men'][1].apply(P('stand', aL=(0.5, -0.1, 1.3, 1.0), aR=(0.5, -0.1, 1.3, 1.0), lean=0.12, head=(0.1, 0.25)))
    turn = math.sin(lt * 1.9)
    S['yama'].place(A(-1.1, 0.7, 0), PI / 2 + 0.25 * turn)
    g = 0.5 + 0.5 * math.sin(lt * 4.2)
    S['yama'].apply(P('stand', aL=(0.9 + 0.3 * g, 0.5, 0.8), aR=(1.0, 0.4 * g, 1.1), head=(0.0, 0.5 * turn)))
    S['face']['yama'] = 'calm'
    S['jaw']['yama'] = 0.22 * (0.5 + 0.5 * math.sin(t * 15))
    S['rook'].place(A(-4.7, 0.2, 0), PI / 2 - 0.5)
    S['rook'].apply(P('cross', head=(0.0, 0.35 * turn)))
    cam(S, A(lerp(-2.4, -1.4, k), lerp(-8.0, -7.2, k), lerp(3.5, 3.2, k)), A(0.4, 1.4, 2.3), 28)


def classroom(S, k, t, lt):
    """He teaches school. The board carries plain marks; the pupils are plain figures seen from behind."""
    A = show(S, 'klass')
    sky(S, 'A8C8E0', 1.0)
    S['fillk'] = 1.2
    p = ease(lt / 0.6)
    S['yama'].place(A(-0.6, 5.3, 0.3), 0.35)
    S['yama'].apply(blend(P('stand'), P('stand', aR=(1.6, 1.25, 0.1), aL=(0.4, 0.2, 0.9), head=(0.0, 0.5 * math.sin(lt * 1.6))), p))
    S['pointer'].hide_render = False
    S['face']['yama'] = 'warm'
    S['jaw']['yama'] = 0.2 * (0.5 + 0.5 * math.sin(t * 14))
    up = ease((lt - 0.9) / 0.4)
    for o in S['khands']:
        o.location = (o.location[0], o.location[1], 1.3 + 0.95 * up)
    S['rook'].place(A(4.5, -3.95, 0.05), PI - 0.5)
    S['rook'].apply(P('sit', lean=0.1, aL=(0.9, 0.0, 1.2, 0.5), aR=(0.9, 0.0, 1.2, 0.5), head=(-0.05, 0.9)))
    cam(S, A(lerp(3.2, 2.6, k), lerp(-8.8, -8.0, k), lerp(4.7, 4.3, k)), A(1.2, 2.6, 1.7), 34)


def back_at_desk(S, k, t, lt):
    """Back at Mitsubishi, designing tankers again."""
    A = office_base(S)
    S['yama'].place(A(-5.2, 2.15, 0.1), PI)
    S['yama'].apply(P('sit', lift=-0.42, lean=0.34, aL=(1.2, 0.1, 0.8), aR=(1.25 + 0.12 * math.sin(lt * 5), 0.1 + 0.12 * math.sin(lt * 2.1), 0.8), head=(0.32, swing(lt, 0.12, 1.1))))
    S['men'][1].place(A(-1.6, -1.65, 0.1), PI)
    S['men'][1].apply(P('sit', lift=-0.42, lean=0.35, aL=(1.2, 0.1, 0.8), aR=(1.25 + 0.08 * math.sin(t * 4), 0.1, 0.8), head=(0.3, 0.0)))
    S['tanker'].location = A(-5.0, 6.72, 1.5)
    S['tanker'].rotation_euler = (0, 0, lerp(-0.1, 0.1, k))
    cam(S, A(lerp(-1.8, -2.6, k), lerp(-0.6, 0.0, k), lerp(3.6, 3.3, k)), A(-5.0, 3.6, 2.0), 38)


# ---------------------------------------------------------------- shots: the hall and the counter
def screening(S, k, t, lt):
    """2006: the documentary is shown. The picture on the screen is a plain seated figure, nobody's likeness."""
    A = hall_base(S)
    S['spot'].data.energy = 300
    S['screen'].location = A(0, 12.9, 5.6)
    fl = 3.0 + 0.5 * math.sin(t * 9) * math.sin(t * 2.3)
    tint(S['screenmat'], 'DCE4F0', fl)
    S['glow'].location = A(0, 9.5, 5.5)
    S['glow'].data.energy = 2600 + 500 * math.sin(t * 9)
    S['glow'].data.color = K.hexc('C8D8FF')[:3]
    S['old'].place(A(-1.1, -0.95, 0.1), PI)
    S['old'].root.scale = (0.95, 0.95, 0.95)
    S['old'].apply(P('sit', lift=-0.42, lean=0.1, head=(-0.1, 0.0)))
    cam(S, A(lerp(-4.4, -3.2, k), lerp(-12.5, -11.0, k), lerp(5.4, 4.8, k)), A(0, 11.0, 4.6), 30)


def empty_lectern(S, k, t, lt):
    """January 2010. The lectern, and nobody at it."""
    A = hall_base(S)
    for i, o in enumerate(S['puffs']):
        u = (t * 0.08 + i * 0.13) % 1
        o.location = A(-1.2 + ((i * 0.618) % 1) * 2.6, 6.0 + ((i * 0.37) % 1) * 1.4, 5.6 - 3.4 * u)
        o.scale = (0.035, 0.035, 0.035)
    cam(S, A(lerp(0.5, 0.15, k), lerp(-3.4, -0.6, k), lerp(3.7, 3.4, k)), A(0.0, 6.6, 2.9), 46, fcol='FFE0C0')


def counter(S, k, t, lt):
    """March 2009: Hiroshima is added to his record. A clerk and a booklet stand for it; the real booklet is not reproduced."""
    A = show(S, 'counter')
    sky(S, '05060A', 1.0)
    S['fillk'] = 1.0
    press = ease((lt - 0.5) / 0.35) - ease((lt - 1.3) / 0.4)
    S['clerk'].place(A(0.5, 2.7, 0), 0.1)
    S['clerk'].apply(P('stand', lean=0.2 + 0.1 * press, aR=(1.0 + 0.25 * press, 0.25, 0.5), aL=(0.8, 0.1, 0.9), head=(0.35, 0.1)))
    S['stamp'].location = (lerp(0.75, 0.04, press), lerp(1.55, 1.13, press), lerp(2.75, 2.1, press))
    S['mark'].hide_render = lt < 1.25
    S['rook'].place(A(-3.4, 0.0, 0), PI - 0.8)
    S['rook'].apply(P('stand', aL=(1.0, 0.0, 0.6), lean=0.12, head=(0.1, -0.2)) if lt < 1.3 else P('hat', lean=0.05, head=(0.0, -0.2)))
    S['hat_tip'] = -0.25 * ease((lt - 1.3) / 0.3)
    cam(S, A(lerp(2.4, 1.6, k), lerp(-5.4, -4.8, k), lerp(3.2, 3.0, k)), A(-1.0, 1.7, 2.3), 32)


def stamp_cu(S, k, t, lt):
    A = show(S, 'counter')
    sky(S, '05060A', 1.0)
    S['fillk'] = 1.4
    press = ease((lt - 0.25) / 0.3) - ease((lt - 0.9) / 0.4)
    S['clerk'].place(A(0.5, 2.7, 0), 0.1)
    S['clerk'].apply(P('stand', lean=0.2 + 0.1 * press, aR=(1.0 + 0.25 * press, 0.25, 0.5), aL=(0.8, 0.1, 0.9), head=(0.35, 0.1)))
    S['stamp'].location = (lerp(0.75, 0.04, press), lerp(1.55, 1.13, press), lerp(2.75, 2.1, press))
    S['mark'].hide_render = lt < 0.85
    cam(S, A(lerp(-1.0, -0.8, k), lerp(0.0, 0.2, k), lerp(3.6, 3.4, k)), A(-0.15, 1.3, 2.0), 56, fill=1.5)


HOST |= {'yama_draws', 'rook_plan', 'to_work', 'porch', 'dorm_wide', 'goes_back', 'found_three', 'platform_wait', 'platform_night',
         'carriage_wide', 'treated', 'rook_room', 'writes', 'alone', 'old_window', 'translator', 'classroom', 'counter'}
SHOTS3D.update({f.__name__: f for f in (
    yama_draws, rook_plan, farewell, hisako_door, to_work, porch, dorm_wide, three_go, forgot, goes_back, found_three, shelter_three,
    platform_wait, platform_night, carriage_wide, treated, bandage_cu, gets_up, in_bed, rook_room, family, writes, poem_cu, alone,
    old_window, translator, classroom, back_at_desk, screening, empty_lectern, counter, stamp_cu)})


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: the second white light at the office windows, him bandaged in front of it, Rook beside him."""
    A = office_base(S, 0.5)
    S['yama'].place(A(0.1, -2.5, 0), 0.2)
    S['yama'].apply(P('stand', aR=(0.3, 0.2, 0.5), aL=(0.7, -0.2, 1.5, 0.9), head=(-0.05, 0.0)))
    S['face']['yama'] = 'shock'
    bandaged(S)
    S['rook'].place(A(1.25, -2.1, 0), -0.2)
    S['rook'].apply(P('stand', aR=(0.2, 1.9, 1.6, -1.5), aL=(0.5, 0.3, 0.8), head=(-0.05, -0.5)))
    S['face']['rook'] = 'shocked'
    cam(S, A(2.0, -6.6, 2.7), A(2.0, 2.0, 2.75), 26, fill=1.4)


STILLS['thumb'] = photo_thumb
