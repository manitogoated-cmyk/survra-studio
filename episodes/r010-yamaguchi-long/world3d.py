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
