"""Case 001 in 3D - Harrison Okene, Jascon-4, May 2013. Sets built for this story only:
Rook's office, a wreck corridor, the cabin that becomes the air pocket, the open deep, the night sea, a deck at sunrise."""
import math

import bpy
import numpy as np

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(office=(0, 0, 0), corr=(300, 0, 0), cabin=(600, 0, 0), deep=(900, 0, 0), sea=(0, 400, 0), deck=(300, 400, 0))
FAR = (0, 0, -500)
HOST = {'rook_office', 'rook_cu', 'door_go', 'rook_buoy', 'capsize', 'sinking', 'pocket_wide', 'rook_shrug', 'rook_feathers', 'rook_fair',
        'bell_up', 'sunrise', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
OKENE = dict(top='D9D4C8', pants='232936', hand='7A4A2E', boot='7A4A2E', fore='7A4A2E')
DIVER = dict(top='20242B', pants='17191F', hand='F2B531', boot='F2B531')
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


# ---------------------------------------------------------------- props
def make_tug(r, lit=True):
    add('cube', '7A2424', (0, 0, 0.2), scale=(5.2, 2.0, 1.0), size=1, parent=r)
    add('cube', '20242B', (0, 0, 0.82), scale=(5.4, 2.1, 0.3), size=1, parent=r)
    add('cylinder', '7A2424', (3.15, 0, 0.2), rot=(0, 0, PI), scale=(1.1, 1.0, 1.0), radius=1.16, depth=1.0, vertices=3, parent=r)
    add('cylinder', '20242B', (3.2, 0, 0.82), rot=(0, 0, PI), scale=(1.1, 1.0, 1.0), radius=1.22, depth=0.3, vertices=3, parent=r)
    add('cube', 'E8E4D8', (0.5, 0, 1.75), scale=(2.0, 1.5, 1.5), size=1, parent=r)
    add('cube', 'C8C4B8', (0.3, 0, 2.75), scale=(1.3, 1.2, 0.55), size=1, parent=r)
    for i in range(3):
        add('cube', 'FFD27A' if lit else '1A2A30', (0.0 + i * 0.5, -0.76, 1.95), scale=(0.3, 0.03, 0.34), size=1, parent=r, emit=5.0 if lit else 0)
    add('cube', 'FFD27A' if lit else '1A2A30', (1.51, 0, 1.95), scale=(0.03, 1.1, 0.34), size=1, parent=r, emit=5.0 if lit else 0)
    add('cylinder', '20242B', (-0.9, 0, 2.1), radius=0.36, depth=2.0, vertices=8, parent=r)
    add('cylinder', 'FF7A1A', (-0.9, 0, 2.75), radius=0.38, depth=0.3, vertices=8, parent=r)
    add('cylinder', '9AA0B4', (0.5, 0, 3.7), radius=0.05, depth=1.6, vertices=5, parent=r)
    add('cube', '20242B', (-2.0, 0, 1.15), scale=(0.9, 1.3, 0.5), size=1, parent=r)
    add('cube', '5A1A1A', (0.2, 0, -0.42), scale=(5.6, 0.22, 0.3), size=1, parent=r)
    add('cube', '20242B', (-2.75, 0, -0.5), scale=(0.5, 0.1, 0.8), size=1, parent=r)
    add('cone', 'C89A3A', (-2.3, 0, -0.62), rot=(0, PI / 2, 0), radius1=0.34, radius2=0.05, depth=0.3, vertices=5, parent=r, rough=0.4)
    if lit:
        add('ico_sphere', 'FF4030', (0.5, 0, 4.5), radius=0.12, subdivisions=1, parent=r, emit=12)
    return r


def make_bell(r):
    add('cylinder', 'E8E4D8', (0, 0, 0), radius=1.1, depth=2.0, vertices=10, parent=r)
    add('cone', 'F2B531', (0, 0, 1.4), radius1=1.1, radius2=0.35, depth=0.8, vertices=10, parent=r)
    add('cylinder', 'F2B531', (0, 0, -1.1), radius=1.2, depth=0.25, vertices=10, parent=r)
    for a in range(3):
        add('cylinder', 'FFE7A8', (math.sin(a * 2.1 - 0.6) * 1.08, -math.cos(a * 2.1 - 0.6) * 1.08, 0.2), rot=(PI / 2, 0, a * 2.1 - 0.6),
            radius=0.3, depth=0.1, vertices=8, parent=r, emit=6)
    add('cylinder', '9AA0B4', (0, 0, 22), radius=0.06, depth=40, vertices=5, parent=r)
    light((0, 0, -1.6), 400, 'FFE7A8', kind='POINT', parent=r)


def make_bottle(r):
    add('cylinder', '3A1E14', (0, 0, 0), radius=0.13, depth=0.5, vertices=8, parent=r, rough=0.25)
    add('cone', '3A1E14', (0, 0, 0.37), radius1=0.13, radius2=0.05, depth=0.24, vertices=8, parent=r, rough=0.25)
    add('cylinder', '3A1E14', (0, 0, 0.55), radius=0.05, depth=0.14, vertices=8, parent=r, rough=0.25)
    add('cylinder', 'E5392F', (0, 0, 0.02), radius=0.136, depth=0.2, vertices=8, parent=r, rough=0.5, emit=0.25)
    add('cylinder', 'B9C2CC', (0, 0, 0.64), radius=0.06, depth=0.05, vertices=8, parent=r, rough=0.3)


# ---------------------------------------------------------------- sets
def set_office(r):
    add('plane', '2A2230', (0, 0, 0), size=22, parent=r)
    add('cube', '222840', (0, 4, 3.5), scale=(22, 0.2, 7), size=1, parent=r)
    add('cube', '1B2034', (-6, 0, 3.5), scale=(0.2, 12, 7), size=1, parent=r)
    add('cube', '5E8FD0', (-2.2, 3.86, 3.4), scale=(2.8, 0.05, 2.3), size=1, parent=r, emit=2.6)
    for i in range(8):
        add('cube', '10121C', (-2.2, 3.8, 2.38 + i * 0.29), rot=(0.5, 0, 0), scale=(2.9, 0.05, 0.15), size=1, parent=r)
    add('cube', '10121C', (-2.2, 3.82, 3.4), scale=(0.08, 0.08, 2.4), size=1, parent=r)
    add('cube', '8A6A4A', (2.0, 3.86, 3.1), scale=(2.7, 0.08, 1.9), size=1, parent=r)
    add('cube', '4A2F1A', (2.0, 3.88, 3.1), scale=(2.9, 0.04, 2.1), size=1, parent=r)
    for x, z, c, rz in ((1.2, 3.5, 'F4EEDF', 0.08), (2.0, 2.8, 'FFD866', -0.1), (2.75, 3.45, 'F4EEDF', -0.05), (1.3, 2.6, 'BFE0EC', 0.12)):
        add('cube', c, (x, 3.8, z), rot=(0, rz, 0), scale=(0.55, 0.02, 0.45), size=1, parent=r)
        add('ico_sphere', 'E5392F', (x, 3.76, z + 0.17), radius=0.04, subdivisions=1, parent=r)
    add('cube', 'E5392F', (1.6, 3.77, 3.15), rot=(0, 0.72, 0), scale=(1.1, 0.012, 0.015), size=1, parent=r)
    add('cube', 'E5392F', (2.38, 3.77, 3.12), rot=(0, -0.72, 0), scale=(1.0, 0.012, 0.015), size=1, parent=r)
    add('cube', '3A2A22', (-3.2, 1.4, 0.95), scale=(2.6, 1.3, 0.12), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '2A1E18', (-3.2 + sx * 1.15, 1.4, 0.45), scale=(0.14, 1.1, 0.9), size=1, parent=r)
    add('cylinder', '20242B', (-3.6, 1.4, 1.3), radius=0.05, depth=0.6, vertices=6, parent=r)
    add('cone', 'FFB000', (-3.6, 1.4, 1.72), radius1=0.34, radius2=0.14, depth=0.32, vertices=8, parent=r, emit=2.5)
    light((-3.6, 1.4, 1.5), 260, 'FFB868', kind='POINT', parent=r)
    add('cube', 'F4EEDF', (-2.7, 1.25, 1.03), rot=(0, 0, 0.3), scale=(0.5, 0.36, 0.02), size=1, parent=r)
    add('cube', 'FFB060', (4.7, 3.86, 1.95), scale=(1.7, 0.06, 3.7), size=1, parent=r, emit=7)
    for sx in (-1, 1):
        add('cube', '10121C', (4.7 + sx * 0.93, 3.8, 1.95), scale=(0.16, 0.14, 3.9), size=1, parent=r)
    add('cube', '10121C', (4.7, 3.8, 3.88), scale=(2.0, 0.14, 0.16), size=1, parent=r)
    light((4.7, 3.0, 2.2), 500, 'FF9A3A', kind='POINT', parent=r)
    aim = empty((0, 0, 1.9), r)
    light((-4.5, -5.5, 5.0), 1500, 'FFE2B8', 3.0, aim, parent=r)
    light((3.5, 3.0, 4.6), 2200, 'FF7A1A', 1.5, aim, parent=r)
    light((4.5, -5, 1.6), 160, '5E8FD0', 4.0, aim, parent=r)
    cap = add('cylinder', 'FFD866', (0, 0, -5), radius=0.09, depth=0.03, vertices=8, parent=None, rough=0.3, emit=1.0)
    return dict(cap=cap)


def set_corr(r):
    add('cube', '1B3038', (0, 2, -0.1), scale=(3.4, 30, 0.2), size=1, parent=r)
    add('cube', '15262C', (0, 2, 3.1), scale=(3.4, 30, 0.2), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '1F3840', (sx * 1.7, 2, 1.5), scale=(0.2, 30, 3.2), size=1, parent=r)
    for y in range(-10, 17, 4):
        for sx in (-1, 1):
            add('cube', '2A4C56', (sx * 1.55, y, 1.5), scale=(0.16, 0.3, 3.0), size=1, parent=r)
        add('cube', '2A4C56', (0, y, 2.92), scale=(3.2, 0.3, 0.16), size=1, parent=r)
    for y in (4, -4, 12):
        add('cube', '04080A', (-1.62, y + 2, 1.2), scale=(0.12, 1.3, 2.4), size=1, parent=r)
        add('cube', '356470', (-1.58, y + 2 + 0.72, 1.2), scale=(0.14, 0.12, 2.5), size=1, parent=r)
        add('cube', '356470', (-1.58, y + 2 - 0.72, 1.2), scale=(0.14, 0.12, 2.5), size=1, parent=r)
    add('cylinder', '8A3A2A', (1.45, 3, 2.5), rot=(PI / 2, 0, 0), radius=0.1, depth=30, vertices=6, parent=r)
    add('cube', '2A4C56', (1.1, 7.5, 0.25), rot=(0, 0.3, 0.5), scale=(0.7, 0.5, 0.5), size=1, parent=r)
    add('cube', '8FA3B8', (-0.9, -1.5, 0.12), rot=(0, 0, 0.8), scale=(0.9, 0.5, 0.14), size=1, parent=r)
    for y in (-6, 2, 10):
        light((0, y, 2.6), 150, '2A9AAA', kind='POINT', parent=r)
    far = add('ico_sphere', 'FFF2C0', (0, 0, -5), radius=0.3, subdivisions=1, parent=None, emit=14)
    farl = light((0, 0, 0), 600, 'FFF2C0', kind='POINT', parent=far)
    return dict(far=far, farl=farl)


def set_cabin(r):
    room = empty((0, 0, 1.6), r)
    add('cube', '26404A', (0, 0, -1.7), scale=(4.8, 4.4, 0.2), size=1, parent=room)
    add('cube', '3A5C66', (0, 0, 1.7), scale=(4.8, 4.4, 0.2), size=1, parent=room)
    add('cube', '2E4A54', (0, 1.9, 0), scale=(4.8, 0.2, 3.4), size=1, parent=room)
    for sx in (-1, 1):
        add('cube', '294650', (sx * 2.4, 0, 0), scale=(0.2, 4.4, 3.4), size=1, parent=room)
    for z in (-0.9, 0.9):
        add('cube', '3E6470', (0, 1.78, z), scale=(4.6, 0.06, 0.08), size=1, parent=room)
    add('cylinder', 'E8E8E0', (-1.5, 1.2, -1.25), radius=0.33, depth=0.7, vertices=8, parent=room)
    add('cube', 'E8E8E0', (-1.5, 1.62, -0.75), scale=(0.7, 0.26, 0.9), size=1, parent=room)
    add('cylinder', 'C8C8C0', (-1.5, 1.2, -0.88), radius=0.36, depth=0.06, vertices=8, parent=room)
    add('cube', 'E8E8E0', (1.2, 1.5, -0.6), scale=(1.0, 0.6, 0.22), size=1, parent=room)
    add('cube', 'C8C8C0', (1.2, 1.55, -1.15), scale=(0.25, 0.3, 1.0), size=1, parent=room)
    add('cube', 'BFE0EC', (1.2, 1.78, 0.35), scale=(0.9, 0.04, 1.0), size=1, parent=room, rough=0.1, emit=0.25)
    add('cylinder', '9AA0B4', (0.2, 1.74, 0.0), rot=(0, PI / 2, 0), radius=0.03, depth=0.8, vertices=5, parent=room)
    add('cube', 'C8452E', (0.2, 1.7, -0.3), scale=(0.6, 0.05, 0.6), size=1, parent=room)
    add('cube', '14262C', (2.28, -0.7, -0.45), scale=(0.06, 1.15, 2.4), size=1, parent=room)
    add('cube', '3E6470', (2.26, -0.7, 0.8), scale=(0.08, 1.35, 0.12), size=1, parent=room)
    add('cylinder', 'FFF2C0', (0, 0.2, 1.56), radius=0.4, depth=0.08, vertices=10, parent=room, emit=2)
    lamp = light((0, 0.2, 1.25), 300, 'FFF2C0', kind='POINT', parent=room)
    water = add('plane', '0E4A66', (0, -0.4, -5), size=1, scale=(4.7, 5.2, 1), parent=r, rough=0.12, alpha=0.8)
    aim = empty((0, 0.3, 1.6), r)
    fill = light((1.5, -6, 3.4), 200, '6AB8D0', 4.0, aim, parent=r)
    matt = empty((0, 0, -5), r)
    add('cube', '8FA3B8', (0, 0, 0), scale=(1.9, 1.1, 0.26), size=1, parent=matt)
    add('cube', 'B8C8D8', (0, 0, 0.14), scale=(1.8, 1.0, 0.04), size=1, parent=matt)
    beam = empty((0, 0, -5), r)
    baim = empty((0, -8, 0), beam)
    bl = light((0, 0, 0), 40000, 'FFF2C0', kind='SPOT', spot=0.5, target=baim, parent=beam)
    add('cone', 'FFF2C0', (0, -3.6, 0), rot=(-PI / 2, 0, 0), radius1=1.3, radius2=0.08, depth=7, vertices=10, parent=beam, emit=0.3, alpha=0.06)
    add('ico_sphere', 'FFF8E0', (0, 0, 0), radius=0.14, subdivisions=1, parent=beam, emit=30)
    bottle = empty((0, 0, -5), r)
    make_bottle(bottle)
    return dict(room=room, lamp=lamp, water=water, fill=fill, matt=matt, beam=beam, beaml=bl, bottle=bottle)


def set_deep(r):
    add('plane', '0E2030', (0, 0, 0), size=220, parent=r)
    for i in range(22):
        a = i * 2.4
        d = 5 + (i * 7 % 23)
        add('ico_sphere', '0A1824', (math.sin(a) * d, math.cos(a) * d + 6, 0.1), scale=(1, 1.2, 0.55), radius=0.6 + (i % 4) * 0.4, subdivisions=1, parent=r)
    aim = empty((0, 0, 2), r)
    top = light((2, -3, 30), 60000, '3A9AD0', 14.0, aim, parent=r)
    light((-8, -10, 4), 500, '2A6A9A', 5.0, aim, parent=r)
    tug = make_tug(empty((0, 0, -30), r), lit=False)
    glow = add('cube', 'FFD9A0', (0.2, 1.03, 0.3), scale=(1.1, 0.06, 0.7), size=1, parent=tug, emit=8)
    add('cube', '1A1210', (0.2, 1.06, 0.2), scale=(0.16, 0.05, 0.36), size=1, parent=glow.parent)
    add('ico_sphere', '1A1210', (0.2, 1.06, 0.46), radius=0.11, subdivisions=1, parent=tug)
    gl = light((0.2, 1.9, 0.3), 500, 'FFD9A0', kind='POINT', parent=tug)
    bell = empty((0, 0, -90), r)
    make_bell(bell)
    surf = add('circle', '6EC6EE', (0, 0, 46), radius=90, vertices=24, fill_type='NGON', parent=r, emit=0.55)
    return dict(tug2=tug, glow=glow, glowl=gl, bell=bell, surf=surf, top=top)


def set_sea(r):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=56, y_subdivisions=56, size=170, location=ORG['sea'])
    sea = bpy.context.object
    sea.data.materials.append(K.mat('0C3148', 0.5))
    co = np.zeros(len(sea.data.vertices) * 3)
    sea.data.vertices.foreach_get('co', co)
    xy = co.reshape(-1, 3)[:, :2].copy()
    tug = make_tug(empty((0, 0, 0), r))
    tug.scale = (2.6, 2.6, 2.6)
    light((1.2, 0, 4.2), 2500, 'FFD27A', kind='POINT', parent=tug)
    plat = empty((-16, 60, 0), r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', '1A222C', (sx * 6, sy * 4, 5), radius=0.9, depth=16, vertices=6, parent=plat)
    add('cube', '222C38', (0, 0, 12), scale=(17, 12, 1.6), size=1, parent=plat)
    add('cube', '2A3644', (-3, 0, 14.5), scale=(7, 8, 3.5), size=1, parent=plat)
    add('cone', '1A222C', (4, 0, 20), radius1=2.6, radius2=0.4, depth=14, vertices=4, parent=plat)
    add('cylinder', '1A222C', (11, 0, 15), rot=(0, 1.0, 0), radius=0.25, depth=9, vertices=5, parent=plat)
    add('cone', 'FF9A3A', (14.6, 0, 18.6), radius1=1.0, radius2=0.0, depth=3.2, vertices=5, parent=plat, emit=14)
    light((14.6, -1, 19), 60000, 'FF9A3A', kind='POINT', parent=plat)
    for i in range(6):
        add('cube', 'FFD27A', (-5.5 + i * 1.0, -4.05, 14.8), scale=(0.45, 0.05, 0.6), size=1, parent=plat, emit=7)
    buoy = empty((0, 0, -30), r)
    add('cylinder', 'C8452E', (0, 0, 0.1), radius=1.25, depth=0.9, vertices=8, parent=buoy)
    add('cylinder', 'E8E4D8', (0, 0, 0.6), radius=1.0, depth=0.12, vertices=8, parent=buoy)
    add('cylinder', '9AA0B4', (0.55, 0.3, 2.4), radius=0.06, depth=3.6, vertices=5, parent=buoy)
    add('ico_sphere', '3DDC84', (0.55, 0.3, 4.3), radius=0.2, subdivisions=1, parent=buoy, emit=16)
    light((0.55, 0.0, 4.3), 220, '3DDC84', kind='POINT', parent=buoy)
    wave = add('cylinder', '0C3148', (0, 0, -40), rot=(0, PI / 2, 0), radius=13, depth=150, vertices=14, parent=r, rough=0.22)
    aim = empty((0, 0, 3), r)
    light((-30, 30, 35), 60000, '9AB8E8', 12.0, aim, parent=r)
    key = light((14, -34, 14), 3000, 'C8D8F8', 8.0, aim, parent=r)
    return dict(sea=sea, xy=xy, tug=tug, buoy=buoy, wave=wave, seakey=key)


def set_deck(r):
    add('cube', 'B88A5A', (0, 2, -0.15), scale=(30, 14, 0.3), size=1, parent=r)
    for i in range(-10, 11):
        add('cube', '8A6238', (i * 1.5, 2, 0.005), scale=(0.05, 14, 0.02), size=1, parent=r)
    for i in range(-8, 9):
        add('cylinder', 'E8E4D8', (i * 1.8, 6.5, 0.6), radius=0.05, depth=1.2, vertices=5, parent=r)
    for z in (0.65, 1.2):
        add('cylinder', 'E8E4D8', (0, 6.5, z), rot=(0, PI / 2, 0), radius=0.045, depth=32, vertices=5, parent=r)
    add('plane', 'D8703A', (0, 150, -2.5), size=420, parent=r, rough=0.18)
    add('circle', 'FFE3A0', (2.5, 330, 14), rot=(PI / 2, 0, 0), radius=26, vertices=20, fill_type='NGON', parent=r, emit=9)
    add('cube', '7A5A3A', (-0.9, 3.2, 0.42), scale=(1.5, 1.1, 0.84), size=1, parent=r)
    add('cube', '5A4028', (-0.9, 3.2, 0.42), scale=(1.54, 0.2, 0.88), size=1, parent=r)
    blanket = add('cone', 'C8452E', (0, 0, -5), radius1=0.78, radius2=0.42, depth=1.3, vertices=7, parent=None)
    add('cone', 'A83422', (0, -0.05, -0.64), radius1=0.86, radius2=0.78, depth=0.1, vertices=7, parent=blanket)
    add('cylinder', 'F2B531', (-3.6, 4.6, 0.5), radius=0.5, depth=1.0, vertices=8, parent=r)
    add('cylinder', 'F2B531', (-4.5, 5.2, 0.5), radius=0.5, depth=1.0, vertices=8, parent=r)
    add('cylinder', 'E8E4D8', (4.2, 5.4, 1.6), radius=0.14, depth=3.2, vertices=6, parent=r)
    add('cylinder', 'C8452E', (4.2, 5.4, 3.3), radius=0.55, depth=0.16, vertices=10, rot=(PI / 2, 0, 0), parent=r)
    gulls = []
    for i in range(4):
        g = empty((0, 0, -5), r)
        for sx in (-1, 1):
            add('cube', 'FFFFFF', (sx * 0.28, 0, 0.07), rot=(0, sx * -0.35, 0), scale=(0.6, 0.16, 0.03), size=1, parent=g, emit=0.6)
        gulls.append(g)
    aim = empty((0, 2, 1.6), r)
    light((6, 40, 9), 70000, 'FFB060', 10.0, aim, parent=r)
    light((-6, -9, 5), 2600, 'FFD8B0', 6.0, aim, parent=r)
    light((7, -6, 2), 700, '9AB8E8', 5.0, aim, parent=r)
    return dict(blanket=blanket, gulls=gulls)


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('office', set_office), ('corr', set_corr), ('cabin', set_cabin), ('deep', set_deep), ('sea', set_sea), ('deck', set_deck)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['okene'] = K.Rig(OKENE, K.human_head())
    S['diver'] = K.Rig(DIVER, K.diver_head)
    S['hand_o'] = K.Hand('7A4A2E', '7A4A2E', 1.0)
    S['hand_d'] = K.Hand('F2B531', '20242B', 1.0)
    S['bub'] = [add('ico_sphere', 'CFEFFF', FAR, radius=0.07, subdivisions=1, emit=1.2) for _ in range(34)]
    S['fea'] = [add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4) for _ in range(9)]
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam = bpy.context.object
    cam.parent = rigc
    cam.data.clip_start, cam.data.clip_end = 0.05, 900
    sc.camera = cam
    S.update(cam=cam, camrig=rigc, camtgt=tgt)
    S['pov'] = light((0, 0, 0), 0, 'FFF2C0', kind='SPOT', spot=0.7, target=tgt, parent=rigc)
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
    for who in ('rook', 'okene', 'diver'):
        S[who].place(FAR)
        S[who].apply(P())
        S[who].root.scale = (1, 1, 1)
    for hnd in ('hand_o', 'hand_d'):
        S[hnd].place(FAR)
        S[hnd].grip(0.2)
    for o in S['bub'] + S['fea'] + S['gulls']:
        o.location = FAR
        o.scale = (1, 1, 1)
    for o in S['rook'].extra['helmet']:
        o.hide_render = True
    S['diver'].extra['cone'].hide_render = False
    S['face'] = dict(rook='calm', okene='scared', diver='calm')
    S['hat_tip'] = 0.0
    S['pov'].data.energy = 0
    S['diver'].extra['lamp'].data.energy = 9000
    S['room'].rotation_euler = (0, 0, 0)
    S['lamp'].data.energy = 300
    S['fill'].data.energy = 200
    S['water'].location.z = -5
    for k in ('matt', 'beam', 'bottle'):
        S[k].location = (0, 0, -5)
        S[k].rotation_euler = (0, 0, 0)
    S['tug2'].location, S['tug2'].rotation_euler = (0, 0, -30), (0, 0, 0)
    S['glow'].hide_render = True
    S['glowl'].data.energy = 0
    S['bell'].location = (0, 0, -90)
    S['buoy'].location = (0, 0, -30)
    S['wave'].location = (0, 0, -40)
    S['tug'].location, S['tug'].rotation_euler = (0, 0, 0), (0, 0, 0)
    S['far'].location = FAR
    S['cap'].location = FAR
    S['blanket'].location = FAR
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
    r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.12).get(e, 0.0) + tip * 0.35, 0.07, 0)
    r['hat'].location.z = 0.27 + (0.13 if e == 'shocked' else 0.0) + tip * 0.1
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e in ('shocked', 'laugh') else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0) - (0.25 if e == 'laugh' else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for who in ('okene', 'diver'):
        e = S['face'][who]
        k = dict(scared=1.25, shock=1.8, calm=1.0, sad=0.6, happy=0.9, closed=0.12).get(e, 1.0)
        for ey in S[who].extra['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], (0.075 if who == 'okene' else 0.09) * k)


def bubbles(S, org, t, n=14, spread=0.6, rise=4.0, speed=1.5, seed=0, size=1.0, start=0):
    for i in range(n):
        b = S['bub'][start + i]
        ph = (i * 0.618 + seed * 0.37) % 1
        u = (t * speed / rise + ph) % 1
        a = i * 2.4 + seed
        rr = spread * (0.3 + 0.7 * ((i * 0.37) % 1)) * (0.4 + u)
        b.location = (org[0] + math.cos(a) * rr + 0.1 * math.sin(t * 3 + i), org[1] + math.sin(a) * rr * 0.6, org[2] + u * rise)
        s = size * (0.5 + ((i * 0.73) % 1)) * (0.6 + 0.6 * u)
        b.scale = (s, s, s)


def burst(S, org, k, n=20, r=3.0, seed=0, size=1.6, start=0, up=1.0):
    for i in range(n):
        b = S['bub'][start + i]
        a, e = i * 2.4 + seed, ((i * 0.61) % 1) * 1.3 + 0.15
        d = r * (0.35 + 0.65 * ((i * 0.37) % 1)) * (1 - (1 - k) ** 2)
        b.location = (org[0] + math.cos(a) * math.cos(e) * d, org[1] + math.sin(a) * math.cos(e) * d * 0.5, org[2] + math.sin(e) * d * up - 2.2 * k * k * up)
        s = size * (0.6 + ((i * 0.73) % 1)) * (1 - 0.6 * k)
        b.scale = (s, s, s)


def wave_h(x, y, t, rough=1.0):
    return rough * (0.55 * math.sin(x * 0.16 + t * 1.5) + 0.4 * math.sin(y * 0.22 + t * 1.9 + x * 0.07) + 0.2 * math.sin((x + y) * 0.45 + t * 2.8))


def seas(S, t, rough=1.0):
    xy = S['xy']
    z = rough * (0.55 * np.sin(xy[:, 0] * 0.16 + t * 1.5) + 0.4 * np.sin(xy[:, 1] * 0.22 + t * 1.9 + xy[:, 0] * 0.07) + 0.2 * np.sin((xy[:, 0] + xy[:, 1]) * 0.45 + t * 2.8))
    S['sea'].data.vertices.foreach_set('co', np.column_stack([xy, z]).ravel())
    S['sea'].data.update()


def storm(S, t, lt, flash_at=None):
    A = show(S, 'sea')
    seas(S, t, 1.5)
    f = 0.0
    if flash_at is not None and 0 <= lt - flash_at < 0.22:
        f = 1 - (lt - flash_at) / 0.22
        f = f if int((lt - flash_at) * 30) % 3 != 1 else f * 0.3
    sky(S, lerp_col('0A1422', '9AB0E0', f), 0.9 + 5 * f)
    S['seakey'].data.energy = 3000 + 60000 * f
    return A


def lerp_col(a, b, k):
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


def tug_ride(S, t, x=0.0, y=0.0, roll=0.0, rough=1.5):
    S['tug'].location = (x, y, wave_h(x, y, t, rough) * 0.7 + 0.4)
    S['tug'].rotation_euler = (roll + 0.07 * math.sin(t * 1.7), 0.06 * math.sin(t * 1.3 + 1), 0.25)


def bowl_rook(S, loc, yaw, pose, expr, t, pitch=0.0):
    S['rook'].place((loc[0], loc[1], loc[2] + 0.12 * math.sin(t * 1.6)), yaw, pitch, 0.04 * math.sin(t * 1.1))
    S['rook'].apply(pose)
    for o in S['rook'].extra['helmet']:
        o.hide_render = False
    S['face']['rook'] = expr
    bubbles(S, (loc[0] + 0.3, loc[1], loc[2] + 3.3), t, 5, 0.25, 3.0, 1.2, seed=7, size=0.7, start=28)


def cabin(S, flipped=True, wl=1.5, lamp=22, fill=30):
    A = show(S, 'cabin')
    S['room'].rotation_euler = (0, PI if flipped else 0, 0)
    S['lamp'].data.energy = lamp
    S['fill'].data.energy = fill
    S['water'].location.z = wl
    sky(S, '020608', 1.0)
    return A


# ---------------------------------------------------------------- shots
def dive_search(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    y = lerp(9.5, 5.0, k)
    S['diver'].place(A(-0.55, y, 1.55 + 0.06 * math.sin(t * 2)), -0.06, PI / 2, 0.05 * math.sin(t * 2.2))
    kick = math.sin(t * 7)
    S['diver'].apply(P('swim', lL=(0.35 * kick, 0.25 + 0.2 * kick), lR=(-0.35 * kick, 0.25 - 0.2 * kick), head=(-1.0, 0.35 * math.sin(t * 1.4))))
    cam(S, A(1.25, y - lerp(5.6, 4.6, k), 1.0), A(-0.3, y - 1.6, 1.6), 30, 0.04)
    S['pov'].data.energy = 900
    bubbles(S, A(-0.55, y - 0.5, 2.0), t, 10, 0.3, 1.2, 1.0)


def hand_float(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    cam(S, A(0.75, lerp(2.6, 4.0, k), 1.65), A(-1.2, 6.0, 1.3), lerp(45, 60, k))
    S['pov'].data.energy = 5200
    S['hand_o'].place(A(lerp(-2.0, -1.1, ease(k * 1.3)), 6.0, 1.3 + 0.06 * math.sin(t * 2.2)), (0.25 + 0.1 * math.sin(t * 1.7), 0.5, PI / 2))
    S['hand_o'].grip(0.3 + 0.08 * math.sin(t * 3))
    bubbles(S, A(-1.2, 6.0, 0.6), t, 6, 0.4, 2.4, 0.6, seed=3, size=0.6)


def hand_grab(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    cam(S, A(0.3, -0.8, 1.8), A(0.1, 3.0, 1.65), 55, 0.12)
    S['pov'].data.energy = 3400
    for hnd in ('hand_d', 'hand_o'):
        S[hnd].root.scale = (1.5, 1.5, 1.5)
    S['hand_d'].place(A(-0.45, 3.0, 1.45), (0.2, 0, -PI / 2))
    S['hand_d'].grip(0.25 + 0.5 * ease(lt / 0.2))
    j = ease(lt / 0.09)
    S['hand_o'].place(A(0.2, 2.98, lerp(2.9, 1.93, j)), (PI / 2, 0, 0))
    S['hand_o'].grip(0.1 + 0.85 * ease((lt - 0.05) / 0.1))
    burst(S, A(0.2, 2.8, 1.5), min(1, lt / 0.7), 14, 1.4, size=0.9)


def diver_shock(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    f = -1 if S['prm'].get('flip') else 1
    S['diver'].place(A(0, 5, 0.2 + 0.05 * math.sin(t * 40)), 0.25 * f + 0.05 * math.sin(t * 31), -0.12, 0)
    S['diver'].apply(P('stand', aL=(0.5, 1.5 + 0.2 * math.sin(t * 30), 0.9), aR=(0.5, 1.5 - 0.2 * math.sin(t * 30), 0.9), head=(-0.05, 0.05 * math.sin(t * 37))))
    S['diver'].extra['cone'].hide_render = True
    S['face']['diver'] = 'shock'
    S['diver'].extra['lamp'].data.energy = 300
    S['pov'].data.energy = 1100
    cam(S, A(0.6 * f, lerp(2.2, 2.6, k), 2.75), A(0, 5, 2.5), 50, 0.1 * f)
    burst(S, A(0, 4.7, 2.1), (lt * 1.2) % 1, 12, 1.8, seed=2, size=0.8, up=-0.6)
    bubbles(S, A(0.5 * f, 4.6, 2.9), t, 10, 0.5, 2.4, 3.2, start=16)


def rook_office(S, k, t, lt):
    A = show(S, 'office')
    sky(S, '05060C')
    S['rook'].place(A(0, 0, 0), 0.3)
    S['rook'].apply(P('cross', head=(0.05, -0.25 + 0.22 * math.sin(t * 4.0) * max(0, 1 - lt / 0.9))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(2.2, 1.6, k), lerp(-6.9, -5.3, k), 2.3), A(0.05, 0, 1.85), 42)


def rook_cu(S, k, t, lt):
    e = S['prm'].get('expr', 'smirk')
    if S['prm'].get('sea'):
        A = show(S, 'deep')
        sky(S, '031220')
        bowl_rook(S, A(0, 0, 1.2), 0.2, P('cross', head=(0.12, -0.1)), e, t)
        cam(S, A(lerp(1.0, 0.8, k), lerp(-4.6, -4.0, k), 3.5), A(0.0, 0, 3.2), 55)
        return
    A = show(S, 'office')
    sky(S, '05060C')
    S['rook'].place(A(0, 0, 0), 0.3)
    S['rook'].apply(P('cross', head=(0.12, -0.15 + 0.1 * ease(k))))
    S['face']['rook'] = e
    cam(S, A(lerp(1.5, 1.2, k), lerp(-4.2, -3.6, k), 2.25), A(0.02, 0, 2.2), 55)


def door_go(S, k, t, lt):
    A = show(S, 'office')
    sky(S, '05060C')
    x, y = lerp(0.3, 4.3, k), lerp(0.2, 2.9, k)
    S['rook'].place(A(x, y, 0), math.atan2(4.0, -2.7))
    S['rook'].apply(walk(t, 1.9))
    cam(S, A(lerp(-1.8, -0.8, k), -6.6, 2.0), A(lerp(1.0, 3.3, k), 1.2, 1.9), 38)


def tug_storm(S, k, t, lt):
    A = storm(S, t, lt, 0.08)
    tug_ride(S, t, 0, 0)
    cam(S, A(lerp(15, 12, k), -44, lerp(5.5, 4.5, k)), A(-2, 0, 6.5), 40, 0.05 * math.sin(t * 1.4))


def rook_buoy(S, k, t, lt):
    A = storm(S, t, lt)
    tug_ride(S, t, 7, 16)
    bz = wave_h(0, -30, t, 1.5) * 0.7
    S['buoy'].location = (0, -30, bz)
    S['buoy'].rotation_euler = (0.09 * math.sin(t * 1.9), 0.07 * math.sin(t * 1.5), 0)
    S['rook'].place(A(-0.2, -30.2, bz + 0.66), -0.35, 0.09 * math.sin(t * 1.9))
    S['rook'].apply(P('stand', aL=(0.5, 1.35, 0.15), aR=(0.3, 0.3, 0.9), head=(0.05, 0.5 - 0.5 * ease((lt - 0.5) / 0.3)), lean=0.05))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(-2.4, -1.6, k), -39.5, 3.6), A(0.6, -30, 2.9 + bz * 0.6), 40, 0.04 * math.sin(t * 1.6))


def big_wave(S, k, t, lt):
    A = storm(S, t, lt, 0.75)
    tug_ride(S, t, 0, 0)
    e = ease(k)
    S['wave'].location = (0, lerp(34, 15, e), lerp(-13, 0.5, e))
    cam(S, A(9, -34, 1.6), A(0, 0, lerp(3.5, 11, e)), 26, lerp(0, -0.08, e))


def capsize(S, k, t, lt):
    A = storm(S, t, lt, 0.02)
    e = ease(k * 1.25)
    S['wave'].location = (0, lerp(15, -14, min(1, k * 1.8)), lerp(0.5, -17, min(1, k * 1.8)))
    S['tug'].location = (0, lerp(0, -3, e), 0.6 - 1.2 * e)
    S['tug'].rotation_euler = (lerp(0.2, -2.95, e), 0.1 * math.sin(t * 5), 0.25)
    burst(S, A(0, -4, 1), min(1, lt / 1.1), 34, 16, size=9, up=1.3)
    bz = wave_h(5.5, -29, t, 1.5) * 0.7
    S['buoy'].location = (5.5, -29, bz)
    S['buoy'].rotation_euler = (0.12 * math.sin(t * 2.3), 0.1 * math.sin(t * 1.9), 0)
    S['rook'].place(A(5.3, -29.2, bz + 0.66), PI - 0.35, 0.12 * math.sin(t * 2.3))
    S['rook'].apply(P('up', aL=(2.4, 0.7, 0.5), aR=(2.4, 0.7, 0.5), lL=(0.2, 0.3), lR=(-0.2, 0.2), head=(-0.2, 0.3), lean=-0.15))
    S['face']['rook'] = 'shocked'
    cam(S, A(10, -40, 6), A(1.5, -6, 3), 34, 0.1 - 0.16 * k)


def bathroom(S, k, t, lt):
    A = cabin(S, False, -5, 300, 200)
    tilt = 0.32 * ease(k)
    S['room'].rotation_euler = (0, tilt, 0)
    S['okene'].place(A(0.3 + 0.5 * tilt, 0.3, 0.02 - 0.3 * tilt), 0.25, 0, tilt * 0.5)
    S['okene'].apply(blend(P('stand', aR=(1.2, 0.2, 1.6), head=(0.15, 0.2)), P('stand', aL=(0.5, 1.2, 0.3), aR=(0.5, 1.2, 0.3), lL=(0.25, 0.3), lR=(-0.3, 0.1), head=(-0.15, -0.4)), k * 1.6))
    S['face']['okene'] = 'calm' if k < 0.35 else 'shock'
    cam(S, A(0.5, -6.3, 2.0), A(0.1, 0.3, 1.7), 38, -0.04 * k)


def flip(S, k, t, lt):
    e = ease(k)
    A = cabin(S, False, lerp(-0.6, 1.2, e), 300 if int(t * 12) % 3 else 60, 200)
    S['room'].rotation_euler = (0, lerp(0.32, PI, e), 0)
    S['okene'].place(A(lerp(0.5, -0.3, e), 0.2, 0.9 + 0.9 * math.sin(e * PI)), 0.3, lerp(0, -2 * PI, e) * 0.5, lerp(0, 2 * PI, e))
    S['okene'].apply(P('up', aL=(2.2, 1.0, 0.5), aR=(1.4, 1.2, 0.8), lL=(0.7, 0.9), lR=(-0.3, 0.5)))
    S['face']['okene'] = 'shock'
    burst(S, A(2.0, -0.6, 0.6), k, 30, 4.2, size=2.6)
    cam(S, A(0.3, -7.4, 1.8), A(0, 0.3, 1.6), 36, 0.12 * math.sin(k * 9))


def sinking(S, k, t, lt):
    A = show(S, 'deep')
    z = lerp(27, 5.5, k)
    sky(S, lerp_col('0C3A5C', '020C16', k))
    S['tug2'].location = (1.8, 0, z)
    S['tug2'].rotation_euler = (PI + 0.12 * math.sin(t * 1.4), 0.1 * math.sin(t * 1.1), 0.5)
    S['tug2'].scale = (1.5, 1.5, 1.5)
    bubbles(S, A(1.8, 0, z + 0.5), t, 26, 2.6, 9, 7, size=2.4)
    bowl_rook(S, A(-1.5, -7.5, z - 3.6), 0.7, P('point', aR=(2.2, 0.3, 0.1), head=(-0.35, 0.5)), 'shocked', t)
    cam(S, A(0, -17, z - 0.5), A(0.3, 0, z - 0.6), 34)


def pocket_wide(S, k, t, lt):
    A = show(S, 'deep')
    sky(S, '031220')
    S['tug2'].location, S['tug2'].rotation_euler, S['tug2'].scale = (2.5, 2, 2.1), (PI, 0.06, 0.35), (1.5, 1.5, 1.5)
    S['glow'].hide_render = False
    S['glowl'].data.energy = 500
    bowl_rook(S, A(-1.3, -5.0, 0.9), PI - 0.75, P('stand', aR=(1.3, 0.2, 0.3), head=(0, 0.0)), 'calm', t)
    e = ease(k * 1.4)
    cam(S, A(lerp(1.6, -1.5, e), lerp(-4.5, -17, e), lerp(2.2, 3.4, e)), A(lerp(2.2, 0.6, e), 0, lerp(1.9, 2.6, e)), lerp(50, 34, e))


def chest_water(S, k, t, lt):
    A = cabin(S, True, 1.52, lerp(90, 30, k), lerp(260, 110, k))
    sh = 0.012 * math.sin(t * 43)
    S['okene'].place(A(0.1 + sh, 0.2, 0.0), 0.25)
    S['okene'].apply(P('cross', head=(0.2, 0.15 * math.sin(t * 0.9)), lean=0.06))
    S['face']['okene'] = 'scared'
    cam(S, A(lerp(1.0, 0.7, k), lerp(-6.2, -4.2, k), 2.5), A(0.1, 0.2, 2.2), 45)


def rook_shrug(S, k, t, lt):
    A = show(S, 'deep')
    sky(S, '031220')
    S['tug2'].location, S['tug2'].rotation_euler, S['tug2'].scale = (4.5, 5.5, 2.1), (PI, 0.06, 0.2), (1.5, 1.5, 1.5)
    S['glow'].hide_render = False
    S['glowl'].data.energy = 300
    up = ease(lt / 0.35) - 0.3 * ease((lt - 0.9) / 0.4)
    bowl_rook(S, A(-0.4, 0, 1.0), 0.25, blend(P('stand'), P('shrug'), up), 'deadpan', t)
    cam(S, A(lerp(1.3, 1.0, k), lerp(-8.2, -7.2, k), 2.6), A(0.1, 0, 2.5), 42)


def coke(S, k, t, lt):
    A = cabin(S, True, 1.52, 40, 120)
    z = 1.5 + 0.55 * ease(lt / 0.3) + 0.03 * math.sin(t * 3)
    S['bottle'].location, S['bottle'].rotation_euler = (0.0, -0.9, z), (0.1, 0.12 * math.sin(t * 2), 0.3)
    S['hand_o'].place(A(0.02, -0.72, z - 0.22), (-PI / 2 + 0.25, 0, 0.3))
    S['hand_o'].root.scale = (1.15, 1.15, 1.15)
    S['hand_o'].grip(0.85)
    S['pov'].data.energy = 700
    cam(S, A(lerp(0.9, 0.6, k), lerp(-3.6, -3.1, k), 2.3), A(0, -0.9, 2.05), 55)


def day_stamp(S, k, t, lt):
    A = cabin(S, True, 1.3, 40, 150)
    mz = 1.32 + 0.05 * math.sin(t * 1.8)
    S['matt'].location, S['matt'].rotation_euler = (0.1, 0.2, mz), (0.03 * math.sin(t * 1.5), 0.04 * math.sin(t * 1.2), 0.15)
    S['okene'].place(A(0.1, 0.55, mz - 0.38), 0.3)
    S['okene'].apply(P('sit', head=(0.42, 0.0)))
    S['face']['okene'] = 'sad'
    cam(S, A(lerp(-1.2, -0.6, k), -6.6, 2.9), A(0.1, 0.2, 1.9), 36)


def rook_feathers(S, k, t, lt):
    A = show(S, 'deep')
    sky(S, '020E1A')
    j = 0.03 * math.sin(t * 47)
    bowl_rook(S, A(j, 0, 1.0), 0.15 + j, P('cross', head=(0.1, 3 * j), lean=0.05), 'shocked', t)
    for i, f in enumerate(S['fea']):
        u = ((t * 0.5 + i * 0.37) % 1)
        a = i * 2.3
        f.location = A(math.cos(a) * (0.5 + u * 1.5), -0.6 + math.sin(a) * 0.5, 1.6 + u * 2.0 + 0.2 * math.sin(t * 2 + i))
        f.rotation_euler = (t * 1.3 + i, t * 0.9 + i * 2, i)
    cam(S, A(lerp(0.9, 0.6, k), lerp(-8.4, -7.0, k), 2.5), A(0, 0, 2.45), 42)


def light_beam(S, k, t, lt):
    A = cabin(S, True, 1.52, 14, 90)
    S['beam'].location = (2.6, lerp(-3.4, -1.2, k), 0.75)
    S['beam'].rotation_euler = (0.12, 0, lerp(-1.1, -1.9, ease(k)))
    S['okene'].place(A(-0.5, 0.5, 0.0), lerp(-0.2, 0.9, ease(k * 1.5)))
    S['okene'].apply(blend(P('cross', head=(0.25, 0)), P('stand', aL=(0.6, 0.5, 0.6), aR=(0.9, 0.4, 0.7), head=(0.2, 0.3)), k * 1.6))
    S['face']['okene'] = 'shock'
    cam(S, A(-1.4, -7.2, 2.7), A(0.2, 0.2, 1.7), 36)


def bang_wall(S, k, t, lt):
    A = cabin(S, True, 1.52, 30, 170)
    S['beam'].location, S['beam'].rotation_euler = (1.5, -3.6, 0.7), (0.2, 0, -1.0)
    ph = (lt / 0.32) % 1
    hit = 1 - ease(ph / 0.35) if ph < 0.35 else ease((ph - 0.35) / 0.65)
    arm = int(lt / 0.32) % 2
    S['okene'].place(A(-1.45, 0.1, 0.0), -PI / 2 + 0.1, 0, 0)
    up, dn = (2.5, 0.2, 1.2), (1.75, 0.1, 0.25)
    mix = tuple(lerp(dn[i], up[i], hit) for i in range(3))
    S['okene'].apply(P('stand', aL=mix if arm == 0 else (2.3, 0.2, 1.3), aR=mix if arm == 1 else (2.3, 0.2, 1.3), lean=-0.12, head=(-0.1, 0)))
    S['face']['okene'] = 'shock'
    if hit < 0.25:
        burst(S, A(-2.2, 0.0, 2.3), 0.3, 6, 0.6, size=0.5)
    cam(S, A(1.9, -5.6, 2.5), A(-1.5, 0.1, 2.15), 45, 0.05)


def light_leaves(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    y = lerp(3.0, 15.5, ease(k))
    S['far'].location = A(0.2 * math.sin(t * 2), y, 1.5)
    S['farl'].data.energy = lerp(700, 150, k)
    S['hand_o'].place(A(0.42, lerp(-5.9, -5.2, ease(k * 2)), 1.22 + 0.03 * math.sin(t * 5)), (-0.2, -0.5, PI + 0.3))
    S['hand_o'].grip(0.05)
    S['hand_o'].root.scale = (1.3, 1.3, 1.3)
    S['pov'].data.energy = 160
    cam(S, A(0.1, -7.4, 1.75), A(0, 6, 1.45), lerp(34, 42, k))


def light_back(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    y = lerp(8.5, 2.6, k)
    kick = math.sin(t * 8)
    S['diver'].place(A(0.55, y, 1.95), 0.08, PI / 2, 0.06 * math.sin(t * 2.6))
    S['diver'].apply(P('swim', lL=(0.4 * kick, 0.3 + 0.2 * kick), lR=(-0.4 * kick, 0.3 - 0.2 * kick), head=(-1.05, 0)))
    cam(S, A(-1.2, y - lerp(5.6, 4.4, k), 0.6), A(0.55, y - 1.5, 1.9), 28, -0.06)
    S['pov'].data.energy = 800
    bubbles(S, A(0.55, y, 2.3), t, 12, 0.35, 0.9, 1.4)


def reach(S, k, t, lt):
    A = cabin(S, True, 1.52, 10, 60)
    S['beam'].location, S['beam'].rotation_euler = (1.6, -1.6, 0.25), (0.35, 0, -0.75)
    e = ease(k)
    S['hand_o'].place(A(0.12, 0.0, lerp(2.15, 1.3, e)), (PI / 2 - 0.15, 0, 0.35))
    S['hand_o'].grip(0.1)
    S['hand_d'].place(A(-0.12, 0.05, lerp(0.15, 0.68, e) + 0.02 * math.sin(t * 4)), (-PI / 2 - 0.1, 0, 0.3))
    S['hand_d'].grip(0.15)
    bubbles(S, A(-0.3, 0, 0.3), t, 8, 0.5, 1.2, 0.7, size=0.6)
    cam(S, A(lerp(0.5, 0.35, k), lerp(-3.2, -2.7, k), 0.9), A(0, 0, 1.0), 50)


def the_grab(S, k, t, lt):
    A = cabin(S, True, 1.52, 10, 60)
    S['beam'].location, S['beam'].rotation_euler = (1.6, -1.6, 0.25), (0.35, 0, -0.75)
    j = ease(lt / 0.08)
    sh = 0.03 * math.sin(t * 50) * max(0, 1 - lt / 0.5)
    S['hand_o'].place(A(0.1 + sh, 0.0, lerp(1.3, 1.02, j)), (PI / 2 - 0.1, 0, 0.35))
    S['hand_o'].grip(0.1 + 0.85 * j)
    S['hand_d'].place(A(-0.02 + sh, 0.1, lerp(0.68, 0.74, j)), (-PI / 2 - 0.05, 0, 0.3))
    S['hand_d'].grip(0.15 + 0.5 * j)
    burst(S, A(0.05, -0.1, 0.9), min(1, lt / 0.6), 18, 1.3, size=0.8)
    cam(S, A(0.3, -2.3, 0.85), A(0.04, 0, 0.92), 60, 0.1)


def rook_fair(S, k, t, lt):
    A = show(S, 'deep')
    sky(S, '04182A')
    bowl_rook(S, A(-1.0, 0, 0.9), 0.5, P('stand', aL=(0.5, 0.6, 1.5), aR=(0.5, 0.6, 1.5), head=(0, 0.3), lean=-0.1 + 0.05 * math.sin(t * 14)), 'laugh', t)
    z = lerp(-1.5, 15, k * k)
    S['diver'].place(A(1.9, 2.5, z), -0.3)
    S['diver'].apply(P('up', lL=(0.3 * math.sin(t * 16), 0.4), lR=(-0.3 * math.sin(t * 16), 0.4)))
    S['face']['diver'] = 'shock'
    bubbles(S, A(1.9, 2.5, z - 2.5), t, 22, 0.7, 3.5, 5, size=1.5)
    cam(S, A(0.9, -9.6, 2.3), A(0.2, 0, 2.8), 38)


def bell_up(S, k, t, lt):
    A = show(S, 'deep')
    sky(S, lerp_col('06223A', '2A7AA8', k))
    z = lerp(5, 17, ease(k))
    S['bell'].location = (0, 0, z)
    S['bell'].rotation_euler = (0, 0, 0.3 + 0.2 * k)
    bubbles(S, A(0, 0, z - 1.5), t, 22, 1.3, 7, 4, size=2.2)
    bowl_rook(S, A(2.7, -1.2, z - 2.9), -0.55, P('point', aR=(2.6, 0.4, 0.15), aL=(0.3, 0.5, 0.6), head=(-0.45, -0.4)), 'warm', t)
    cam(S, A(2.6, -8.5, z - lerp(4.5, 3.0, k)), A(0.6, 0, z + 0.3), 30)


def sunrise(S, k, t, lt):
    A = show(S, 'deck')
    sky(S, 'F0965A', 1.0)
    S['okene'].place(A(-0.9, 3.1, 0.84 - 0.5 + 0.02), 0.45)
    S['okene'].apply(P('sit', aL=(0.9, -0.2, 1.5), aR=(0.9, -0.2, 1.5), head=(0.05, 0.5 * ease((lt - 0.4) / 0.4)), lean=0.12))
    S['face']['okene'] = 'happy'
    S['blanket'].location = A(-0.9, 3.2, 1.55)
    S['blanket'].rotation_euler = (0.12, 0, 0.45)
    S['rook'].place(A(1.5, 2.6, 0), -0.75)
    tip = math.sin(PI * ease((lt - 0.35) / 0.9)) if lt > 0.35 else 0
    S['rook'].apply(blend(P('stand', head=(0, 0.2)), P('hat', head=(0.2, 0.2)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    for i, g in enumerate(S['gulls']):
        g.location = (-6 + i * 2.3 + t * 1.2, 20 + i * 6, 6.5 + i * 0.8 + 0.4 * math.sin(t * 2 + i))
        g.rotation_euler = (0, 0.25 * math.sin(t * 9 + i * 2), 0.3)
        g.scale = (2.2, 2.2, 2.2)
    cam(S, A(lerp(0.7, 0.3, k), lerp(-5.2, -4.2, k), 1.9), A(0.3, 2.8, 1.55), 38)


def signoff(S, k, t, lt):
    A = show(S, 'office')
    sky(S, '05060C')
    S['rook'].place(A(0, 0, 0), 0.15)
    tip = math.sin(PI * ease(lt / 0.8)) if lt < 0.8 else 0
    S['rook'].apply(blend(P('stand', aL=(0.9, 0.25, 1.2), head=(0.05, 0)), P('hat', aL=(0.9, 0.25, 1.2), head=(0.22, 0)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'smirk'
    c = max(0.0, min(1.0, (lt - 0.25) / 0.9))
    S['cap'].location = A(-0.75 - 0.25 * c, -0.75, 1.75 + 2.6 * math.sin(c * PI))
    S['cap'].rotation_euler = (t * 22, t * 9, 0)
    cam(S, A(lerp(1.1, 0.8, k), lerp(-6.4, -5.2, k), 1.0), A(0, 0, 2.05), 38)


def photo_tug(S, k, t, lt):
    A = show(S, 'sea')
    seas(S, 2.0, 0.6)
    sky(S, '9AB8D0', 1.6)
    S['seakey'].data.energy = 30000
    S['tug'].location, S['tug'].rotation_euler = (0, 0, 1.2), (PI - 0.1, 0.05, 0.4)
    cam(S, A(7, -19, 7), A(0, 0, 0.6), 42)


def photo_okene(S, k, t, lt):
    A = show(S, 'deck')
    sky(S, 'F0C89A', 1.2)
    S['okene'].place(A(0, 2, 0), 0.25)
    S['okene'].apply(P('stand', head=(0, 0.1)))
    S['face']['okene'] = 'happy'
    cam(S, A(0.5, -2.2, 2.5), A(0, 2, 2.3), 60)


SHOTS3D = {f.__name__: f for f in (
    dive_search, hand_float, hand_grab, diver_shock, rook_office, rook_cu, door_go, tug_storm, rook_buoy, big_wave, capsize, bathroom,
    flip, sinking, pocket_wide, chest_water, rook_shrug, coke, day_stamp, rook_feathers, light_beam, bang_wall, light_leaves,
    light_back, reach, the_grab, rook_fair, bell_up, sunrise, signoff)}
STILLS = dict(tug=photo_tug, okene=photo_okene)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it: the working night before the wave, the locked cabins, the inventory, the
# mattress, the noises, the hammer, the helmet, the decompression chamber and the stars.
ORG.update(chamber=(600, 400, 0), night=(900, 400, 0))


def set_chamber(r):
    add('cube', '9AA89E', (0, 0, -0.1), scale=(6.4, 4.0, 0.2), size=1, parent=r)
    add('cube', 'B4C2B8', (0, 0, 2.7), scale=(6.4, 4.0, 0.2), size=1, parent=r)
    add('cube', 'A8B6AC', (0, 1.9, 1.3), scale=(6.4, 0.2, 2.8), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '9CAAA0', (sx * 3.2, 0, 1.3), scale=(0.2, 4.0, 2.8), size=1, parent=r)
    for x in (-2.2, -0.8, 0.6, 2.0):
        add('cube', '8A988E', (x, 1.78, 1.3), scale=(0.1, 0.06, 2.7), size=1, parent=r)
    add('cube', '5A6A72', (-0.6, 1.3, 0.55), scale=(3.4, 0.8, 0.14), size=1, parent=r)
    add('cube', '48565E', (-0.6, 1.3, 0.25), scale=(3.2, 0.6, 0.5), size=1, parent=r)
    add('cylinder', '20242B', (2.2, 1.76, 1.7), rot=(PI / 2, 0, 0), radius=0.5, depth=0.1, vertices=12, parent=r)
    add('cylinder', '0A2A44', (2.2, 1.72, 1.7), rot=(PI / 2, 0, 0), radius=0.4, depth=0.1, vertices=12, parent=r, emit=0.6)
    add('cylinder', 'E8E4D8', (-2.4, 1.76, 2.0), rot=(PI / 2, 0, 0), radius=0.3, depth=0.08, vertices=12, parent=r)
    add('cube', 'E5392F', (-2.4, 1.7, 2.08), rot=(0, 0.6, 0), scale=(0.03, 0.03, 0.24), size=1, parent=r)
    add('cylinder', 'F2B531', (2.9, 0.4, 1.3), radius=0.16, depth=1.3, vertices=8, parent=r)
    add('cylinder', 'FFF2C0', (0, 0.4, 2.56), radius=0.35, depth=0.06, vertices=10, parent=r, emit=3)
    light((0, 0.4, 2.2), 120, 'FFF2C0', kind='POINT', parent=r)
    aim = empty((0, 0.8, 1.4), r)
    light((-2, -5, 3), 420, 'FFE2B8', 3.0, aim, parent=r)
    light((3, -4, 1.5), 200, '6AB8D0', 3.0, aim, parent=r)
    return {}


def set_night(r):
    add('cube', '3A3040', (0, 2, -0.15), scale=(40, 14, 0.3), size=1, parent=r)
    for i in range(-11, 12):
        add('cylinder', '9AA0B4', (i * 1.8, 6.5, 0.6), radius=0.05, depth=1.2, vertices=5, parent=r)
    for z in (0.65, 1.2):
        add('cylinder', '9AA0B4', (0, 6.5, z), rot=(0, PI / 2, 0), radius=0.045, depth=42, vertices=5, parent=r)
    add('plane', '0A1A2E', (0, 150, -2.5), size=420, parent=r, rough=0.2)
    for i in range(46):
        a, e = (i * 7.77) % 3.1, 0.12 + ((i * 0.6180339) % 1) * 1.1
        add('ico_sphere', 'FFFFFF', (math.cos(a) * math.cos(e) * 170, 90 + math.sin(a) * math.cos(e) * 150, math.sin(e) * 160),
            radius=0.5 + (i % 3) * 0.3, subdivisions=1, parent=r, emit=14)
    add('ico_sphere', 'FFF6D8', (-38, 200, 70), radius=7, subdivisions=2, parent=r, emit=5)
    add('cube', 'F2B531', (5.4, 4.6, 0.6), scale=(1.6, 1.2, 1.2), size=1, parent=r)
    aim = empty((0, 2, 1.8), r)
    light((-8, 20, 14), 9000, 'BFD4FF', 8.0, aim, parent=r)
    light((-4, -8, 4), 1500, 'FFD8A0', 5.0, aim, parent=r)
    return {}


def extend(S):
    for name, fn in (('chamber', set_chamber), ('night', set_night)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    # office: a right wall and a filing cabinet so the wider frame has no void
    before = set(bpy.data.objects)
    o = empty(ORG['office'])
    add('cube', '1B2034', (8.6, 0, 3.5), scale=(0.2, 12, 7), size=1, parent=o)
    add('cube', '3A4252', (7.2, 3.1, 1.2), scale=(1.4, 1.0, 2.4), size=1, parent=o)
    for z in (0.5, 1.2, 1.9):
        add('cube', 'C89A3A', (7.2, 2.58, z), scale=(0.5, 0.04, 0.08), size=1, parent=o)
    add('cube', '222840', (-12, 4, 3.5), scale=(12, 0.2, 7), size=1, parent=o)
    for ob in set(bpy.data.objects) - before:
        for uc in list(ob.users_collection):
            uc.objects.unlink(ob)
        S['colls']['office'].objects.link(ob)
    # props that live outside the sets (parked far away until a shot places them)
    S['helmet2'] = [add('ico_sphere', 'F2B531', (0, 0, 0.02), radius=0.4, subdivisions=1, parent=S['okene'].head, rough=0.5),
                    add('cube', '0B1220', (0, -0.32, 0.03), scale=(0.5, 0.14, 0.28), size=1, parent=S['okene'].head, rough=0.2)]
    S['vest'] = empty(FAR)
    add('cube', 'FF7A1A', (0, 0, 0), scale=(0.9, 0.6, 0.16), size=1, parent=S['vest'])
    add('cube', 'E8E4D8', (0, 0, 0.09), scale=(0.2, 0.62, 0.02), size=1, parent=S['vest'])
    for sx in (-1, 1):
        add('ico_sphere', 'FFF6D8', (sx * 0.3, -0.2, 0.12), radius=0.07, subdivisions=1, parent=S['vest'], emit=40)
    S['vestl'] = light((0, -0.2, 0.5), 60, 'FFF6D8', kind='POINT', parent=S['vest'])
    S['plank'] = add('cube', '8A6238', FAR, scale=(0.14, 1.9, 0.07), size=1)
    S['hammer'] = empty(FAR)
    add('cube', '8A6238', (0, -0.45, 0), scale=(0.07, 0.9, 0.07), size=1, parent=S['hammer'])
    add('cube', '5A6472', (0, -0.95, 0), scale=(0.34, 0.16, 0.16), size=1, parent=S['hammer'], rough=0.4)
    S['fish'] = empty(FAR)
    add('ico_sphere', '0A161C', (0, 0, 0), scale=(0.55, 2.4, 0.8), radius=1.0, subdivisions=1, parent=S['fish'])
    S['tail'] = empty((0, 2.2, 0), S['fish'])
    add('cone', '0A161C', (0, 0.6, 0), rot=(PI / 2, 0, 0), scale=(0.25, 1, 1), radius1=0.9, radius2=0.1, depth=1.4, vertices=4, parent=S['tail'])
    add('cone', '0A161C', (0, -0.2, 0.9), rot=(-0.6, 0, 0), scale=(0.2, 1, 1), radius1=0.5, radius2=0.0, depth=1.0, vertices=4, parent=S['fish'])
    S['locks'] = [add('ico_sphere', 'E5392F', FAR, radius=0.07, subdivisions=1, emit=25) for _ in range(3)]
    S['doors'] = [add('cube', '6A7A84', FAR, scale=(0.1, 1.3, 2.4), size=1) for _ in range(3)]
    S['warm'] = light(FAR, 0, 'FFD9A0', kind='POINT')
    S['boat'] = empty(FAR)
    add('cube', '0A1018', (0, 0, 0), scale=(14, 4.2, 2.0), size=1, parent=S['boat'])
    add('cylinder', '0A1018', (7.6, 0, 0), rot=(0, 0, PI), scale=(1.2, 1, 1), radius=2.4, depth=2.0, vertices=3, parent=S['boat'])
    add('cylinder', '5A6472', (4, 0, -22), radius=0.07, depth=44, vertices=5, parent=S['boat'])
    S['tanker'] = empty(FAR)
    add('cube', '5A1A1A', (0, 0, 1.5), scale=(46, 8, 5), size=1, parent=S['tanker'])
    add('cube', '20242B', (0, 0, 4.4), scale=(46.4, 8.2, 0.8), size=1, parent=S['tanker'])
    add('cube', 'E8E4D8', (-16, 0, 8), scale=(7, 6.4, 6.4), size=1, parent=S['tanker'])
    for i in range(5):
        add('cube', 'FFD27A', (-12.45, -2.4 + i * 1.2, 9.2), scale=(0.06, 0.6, 0.7), size=1, parent=S['tanker'], emit=7)
    add('cylinder', '20242B', (-17, 0, 12.6), radius=1.0, depth=3.0, vertices=8, parent=S['tanker'])


_build0, _reset0, _finish0 = build, reset, finish


def build():
    S = _build0()
    extend(S)
    return S


def reset(S):
    _reset0(S)
    for o in S['helmet2']:
        o.hide_render = True
    for k in ('vest', 'plank', 'hammer', 'fish', 'boat', 'tanker', 'warm'):
        S[k].location = FAR
        S[k].rotation_euler = (0, 0, 0)
    for o in S['locks'] + S['doors']:
        o.location = FAR
    S['warm'].data.energy = 0
    S['vestl'].data.energy = 60


def corridor_dry(S):
    A = show(S, 'corr')
    sky(S, '05080C')
    S['warm'].location, S['warm'].data.energy = A(0, 1, 2.6), 900
    for i, y in enumerate((6, -2, 14)):
        S['doors'][i].location = A(-1.56, y, 1.2)
        S['locks'][i].location = A(-1.46, y + 0.45, 1.3)
    return A


def platform_work(S, k, t, lt):
    A = show(S, 'sea')
    seas(S, t, 0.9)
    sky(S, '101E36', 1.4)
    S['seakey'].data.energy = 9000
    tug_ride(S, t, 0, 0, rough=0.9)
    S['tanker'].location, S['tanker'].rotation_euler = A(-44, 30, 0.6 + 0.2 * math.sin(t)), (0, 0, 0.25)
    cam(S, A(lerp(26, 16, k), -44, lerp(10, 7, k)), A(-10, 14, 6), 32)


def locked_doors(S, k, t, lt):
    A = corridor_dry(S)
    cam(S, A(0.9, lerp(-7, -1.5, k), 1.6), A(-1.4, lerp(1, 6.5, k), 1.35), 30)


def rook_corridor(S, k, t, lt):
    A = corridor_dry(S)
    y = lerp(9, 4.5, k)
    S['rook'].place(A(0.35, y, 0), 0.0)
    S['rook'].apply(walk(t, 1.5))
    S['rook'].head.rotation_euler = (0.05, 0, -0.8 * math.sin(PI * ease((lt - 0.3) / 1.2)))
    S['face']['rook'] = 'calm'
    cam(S, A(-0.6, y - lerp(6.6, 5.6, k), 1.9), A(0.2, y, 1.8), 34)


def feel_walls(S, k, t, lt):
    A = cabin(S, True, lerp(0.8, 1.35, k), 10, 120)
    y = lerp(-1.2, 0.9, k)
    S['okene'].place(A(1.45, y, 0.0), PI / 2 + 0.1)
    S['okene'].apply(P('stand', aL=(2.0 + 0.3 * math.sin(t * 3), 0.5, 0.5), aR=(1.6 - 0.3 * math.sin(t * 3), 0.4, 0.6), lL=(0.3 * math.sin(t * 2.4), 0.2), lR=(-0.3 * math.sin(t * 2.4), 0.2), head=(-0.1, 0.5)))
    S['face']['okene'] = 'shock'
    S['pov'].data.energy = 90
    cam(S, A(lerp(-1.9, -1.3, k), -6.6, 2.5), A(1.1, y * 0.5, 1.9), 40)


def flashlights(S, k, t, lt):
    A = cabin(S, True, 1.4, 14, 150)
    S['vest'].location = A(0.3 + 0.1 * math.sin(t * 0.8), -0.8, 1.5 + 0.04 * math.sin(t * 2))
    S['vest'].rotation_euler = (0.05 * math.sin(t * 1.7), 0.06 * math.sin(t * 1.3), 0.4)
    S['vestl'].data.energy = 420
    S['hand_o'].place(A(lerp(1.9, 0.95, ease(k * 1.4)), -0.9, 1.75), (0.3, 0, PI / 2 + 0.2))
    S['hand_o'].grip(0.15 + 0.5 * ease((k - 0.6) / 0.3))
    cam(S, A(lerp(0.2, 0.0, k), lerp(-4.4, -3.6, k), 2.5), A(0.4, -0.8, 1.6), 50)


def mattress_build(S, k, t, lt):
    A = cabin(S, True, 1.4, 26, 230)
    e = ease(k)
    mx = lerp(1.5, 0.2, e)
    S['matt'].location, S['matt'].rotation_euler = (mx, 0.2, 1.42 + 0.04 * math.sin(t * 2.5)), (0.05 * math.sin(t * 2), 0.06 * math.sin(t * 1.6), 0.15)
    S['okene'].place(A(mx - 1.25, 0.15, 0.0 + 0.02 * math.sin(t * 30)), PI / 2 - 0.15)
    S['okene'].apply(P('stand', aL=(1.25, 0.2, 0.35), aR=(1.35, 0.2, 0.3), lL=(0.4 * math.sin(t * 3), 0.3), lR=(-0.4 * math.sin(t * 3), 0.3), lean=0.3, head=(-0.1, 0)))
    S['face']['okene'] = 'scared'
    cam(S, A(lerp(-0.2, 0.3, k), -6.6, 2.7), A(0.3, 0.2, 1.75), 38)


def plank_wait(S, k, t, lt):
    A = cabin(S, True, 1.3, 10, 110)
    mz = 1.32 + 0.04 * math.sin(t * 1.8)
    S['matt'].location, S['matt'].rotation_euler = (0.0, 0.3, mz), (0.03 * math.sin(t * 1.5), 0.03 * math.sin(t * 1.2), 0.1)
    S['okene'].place(A(0.0, 0.6, mz - 0.38), 0.5)
    S['okene'].apply(P('sit', aL=(1.1, 0.1, 0.9), aR=(1.1, 0.1, 0.9), head=(0.1, 0.55 + 0.1 * math.sin(t * 2.2))))
    S['face']['okene'] = 'shock'
    S['plank'].location = A(0.55 + 0.02 * math.sin(t * 23), -0.15, mz + 0.95)
    S['plank'].rotation_euler = (0.15, 0, 0.55)
    bubbles(S, A(2.0, -0.8, 1.2), t, 7, 0.4, 0.5, 0.5, seed=5, size=0.8)
    cam(S, A(lerp(-2.0, -1.6, k), -5.9, 2.7), A(0.5, 0.1, 2.0), 42)


def shadow_pass(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    y = lerp(15, -3, k)
    S['fish'].location = A(-0.35 + 0.25 * math.sin(t * 1.3), y, 1.75 + 0.15 * math.sin(t * 0.9))
    S['fish'].rotation_euler = (0, 0, 0.12 * math.sin(t * 3.2))
    S['tail'].rotation_euler = (0, 0, 0.5 * math.sin(t * 6))
    bubbles(S, A(0.6, 2, 0.4), t, 8, 0.6, 2.4, 0.5, seed=9, size=0.6)
    S['pov'].data.energy = 420
    cam(S, A(1.1, -6.5, 1.0), A(0.0, 5, 1.6), 30, 0.05)


def pray(S, k, t, lt):
    A = cabin(S, True, 1.3, 9, 70)
    mz = 1.32 + 0.04 * math.sin(t * 1.6)
    S['matt'].location, S['matt'].rotation_euler = (0.0, 0.3, mz), (0.03 * math.sin(t * 1.5), 0.03 * math.sin(t * 1.2), 0.1)
    S['okene'].place(A(0.0, 0.6, mz - 0.38), 0.2)
    S['okene'].apply(P('sit', aL=(1.2, -0.28, 1.95, 0.5), aR=(1.2, -0.28, 1.95, 0.5), head=(0.6, 0), lean=0.3))
    S['face']['okene'] = 'closed'
    S['bottle'].location, S['bottle'].rotation_euler = (1.3, -0.6, 1.36 + 0.03 * math.sin(t * 2)), (1.3, 0, 0.8)
    cam(S, A(lerp(1.0, 0.6, k), lerp(-5.0, -3.9, k), 2.6), A(0.0, 0.5, 2.15), 48)


def divers_down(S, k, t, lt):
    A = show(S, 'deep')
    sky(S, lerp_col('0A3050', '04182A', k))
    S['boat'].location, S['boat'].rotation_euler = A(3, 6, 43.5), (0, 0, 0.3)
    S['tug2'].location, S['tug2'].rotation_euler, S['tug2'].scale = (2.5, 2, 2.1), (PI, 0.06, 0.35), (1.5, 1.5, 1.5)
    z = lerp(24, 9, k)
    kick = math.sin(t * 6)
    S['diver'].place(A(4.6, 3.5, z), -0.6, PI / 2 + 0.85, 0.05 * math.sin(t * 2))
    S['diver'].apply(P('swim', lL=(0.35 * kick, 0.3), lR=(-0.35 * kick, 0.3), head=(-0.6, 0)))
    bubbles(S, A(4.6, 3.5, z + 1.0), t, 16, 0.4, 5, 3.5, size=1.3)
    cam(S, A(lerp(-4, -2, k), -13, z + 3.5), A(3.8, 3, z - 1.5), 32)


def hammer(S, k, t, lt):
    A = cabin(S, True, 1.52, 6, 80)
    ph = (lt / 0.42) % 1
    sw = 1 - ease(ph / 0.3) if ph < 0.3 else ease((ph - 0.3) / 0.7)
    S['hand_o'].place(A(-0.95 + 0.12 * sw, -0.3, 2.25 + 0.1 * sw), (0.1, 0.2, -PI / 2 - 0.15))
    S['hand_o'].root.scale = (1.3, 1.3, 1.3)
    S['hand_o'].grip(0.95)
    S['hammer'].location = A(-1.42 + 0.12 * sw, -0.3, 2.27 + 0.1 * sw)
    S['hammer'].rotation_euler = (-PI / 2, -1.3 + 1.15 * sw, 0)
    S['hammer'].scale = (1.5, 1.5, 1.5)
    S['pov'].data.energy = 380
    if sw < 0.2:
        burst(S, A(-2.25, -0.3, 2.4), 0.35, 8, 0.7, size=0.6)
    cam(S, A(0.2, -3.0, 2.5), A(-1.7, -0.3, 2.35), 50, 0.06)


def helmet_on(S, k, t, lt):
    A = cabin(S, True, 1.52, 24, 260)
    S['okene'].place(A(0.35, 0.2, 0.0), -0.5)
    S['okene'].apply(P('stand', aL=(0.5, 0.3, 0.6), aR=(0.5, 0.3, 0.6), head=(-0.1, 0)))
    S['face']['okene'] = 'happy'
    on = k > 0.55
    for o in S['helmet2']:
        o.hide_render = not on
    S['diver'].place(A(-0.95, 0.15, 0.0), PI / 2 - 0.2)
    lift = 1 - ease((k - 0.15) / 0.4)
    S['diver'].apply(P('up', aL=(2.2 - 0.5 * (1 - lift), 0.15, 0.5), aR=(2.2 - 0.5 * (1 - lift), 0.15, 0.5), head=(-0.2, 0)))
    S['diver'].extra['cone'].hide_render = True
    S['diver'].extra['lamp'].data.energy = 1200
    bubbles(S, A(-0.9, 0.0, 1.5), t, 8, 0.5, 0.8, 0.8, size=0.7)
    cam(S, A(lerp(1.4, 1.0, k), -5.6, 2.8), A(-0.3, 0.2, 2.35), 45)


def walk_out(S, k, t, lt):
    A = show(S, 'corr')
    sky(S, '010507')
    y = lerp(10, 5, k)
    kick = math.sin(t * 6)
    S['diver'].place(A(-0.45, y, 1.6), -0.05, PI / 2, 0.05 * math.sin(t * 2.2))
    S['diver'].apply(P('swim', aL=(2.9, 0.15, 0.1), aR=(0.4, 0.3, 0.4), lL=(0.35 * kick, 0.3), lR=(-0.35 * kick, 0.3), head=(-1.0, 0)))
    S['okene'].place(A(0.45, y + 2.3, 1.45), 0.05, PI / 2, -0.05 * math.sin(t * 2.2))
    S['okene'].apply(P('swim', aL=(2.8, 0.2, 0.2), aR=(2.5, 0.2, 0.3), lL=(-0.4 * kick, 0.35), lR=(0.4 * kick, 0.35), head=(-0.9, 0)))
    for o in S['helmet2']:
        o.hide_render = False
    S['pov'].data.energy = 1000
    bubbles(S, A(0.2, y + 0.5, 2.0), t, 14, 0.5, 1.0, 1.2)
    cam(S, A(1.3, y - lerp(5.6, 4.6, k), 1.0), A(-0.1, y - 0.6, 1.6), 28, 0.04)


def chamber(S, k, t, lt):
    A = show(S, 'chamber')
    sky(S, '020406')
    S['okene'].place(A(-0.9, 1.25, 0.62 - 0.5), 0.3)
    S['okene'].apply(P('sit', aL=(0.9, -0.2, 1.5, 0.8), aR=(0.9, -0.2, 1.5, 0.8), head=(0.15, 0.4 * ease((lt - 0.6) / 0.6)), lean=0.15))
    S['face']['okene'] = 'sad' if k < 0.5 else 'happy'
    S['rook'].place(A(1.2, 0.9, 0), -0.6)
    S['rook'].apply(P('cross', head=(0.1, 0.25)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(1.0, 0.4, k), lerp(-6.0, -5.0, k), 1.9), A(0.1, 1.0, 1.55), 40)


def stars(S, k, t, lt):
    A = show(S, 'night')
    sky(S, '060C1C', 1.0)
    S['okene'].place(A(-0.8, 2.6, 0), 0.25)
    S['okene'].apply(P('stand', aL=(0.3, 0.5, 0.3), aR=(0.3, 0.5, 0.3), head=(-0.55 * ease(lt / 0.8), 0.1)))
    S['face']['okene'] = 'happy'
    S['rook'].place(A(1.1, 2.9, 0), -0.4)
    S['rook'].apply(P('stand', aR=(0.3, 0.3, 0.9), head=(-0.4 * ease((lt - 0.4) / 0.8), 0.2)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(0.9, 0.5, k), lerp(-4.6, -3.8, k), 1.1), A(0.1, 2.8, 2.9), 30)


def rook_desk(S, k, t, lt):
    A = show(S, 'office')
    sky(S, '05060C')
    S['rook'].place(A(-1.7, 0.9, 0), -PI / 2 + 0.5)
    S['rook'].apply(P('stand', aL=(0.9, 0.1, 1.3), aR=(0.5, 0.3, 1.6, 0.6), head=(0.35 - 0.3 * ease((lt - 0.8) / 0.5), 0.5 * ease((lt - 0.8) / 0.5)), lean=0.12))
    S['face']['rook'] = S['prm'].get('expr', 'deadpan')
    cam(S, A(lerp(0.2, -0.2, k), lerp(-5.2, -4.4, k), 2.3), A(-2.0, 1.0, 1.9), 42)


def rook_board(S, k, t, lt):
    A = show(S, 'office')
    sky(S, '05060C')
    tap = max(0, math.sin(lt * 5)) * 0.25
    S['rook'].place(A(1.1, 2.3, 0), PI - 0.5)
    S['rook'].apply(P('stand', aR=(2.0 + tap, 0.35, 0.25), head=(0, 1.1 * ease((lt - 0.7) / 0.5))))
    S['face']['rook'] = S['prm'].get('expr', 'calm')
    cam(S, A(lerp(-1.6, -1.0, k), lerp(-4.4, -3.6, k), 2.5), A(1.6, 3.2, 2.6), 40)


def rook_window(S, k, t, lt):
    A = show(S, 'office')
    sky(S, '05060C')
    S['rook'].place(A(-2.0, 2.2, 0), lerp(PI + 0.3, 0.35, ease((k - 0.25) / 0.5)))
    S['rook'].apply(P('cross', head=(0.08, 0)))
    S['face']['rook'] = S['prm'].get('expr', 'deadpan')
    cam(S, A(lerp(0.4, -0.2, k), lerp(-4.6, -3.8, k), 2.3), A(-2.0, 2.2, 2.25), 45)


def rook_pocket(S, k, t, lt):
    A = cabin(S, True, 1.3, 16, 150)
    mz = 1.32 + 0.04 * math.sin(t * 1.8)
    S['matt'].location = (-0.9, 0.5, mz)
    S['okene'].place(A(-0.9, 0.8, mz - 0.38), 0.4)
    S['okene'].apply(P('sit', head=(0.3, -0.4)))
    S['face']['okene'] = 'scared'
    S['bottle'].location, S['bottle'].rotation_euler = (0.2, -0.9, 1.36 + 0.03 * math.sin(t * 2)), (1.3, 0, 0.5)
    S['vest'].location, S['vest'].rotation_euler = A(-0.2, -1.5, 1.4 + 0.03 * math.sin(t * 2.3)), (0, 0, 1.0)
    n = min(3, int(lt / 0.9))
    S['rook'].place(A(1.25, -0.5, 0.0), -0.35, 0, 0)
    S['rook'].apply(P('stand', aR=(1.7 + 0.15 * math.sin(lt * 7), 0.25, 1.5 - 0.3 * n, 0.2), aL=(0.4, 0.3, 0.6), head=(0.05, -0.2)))
    for o in S['rook'].extra['helmet']:
        o.hide_render = False
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(0.9, 0.6, k), lerp(-6.2, -5.4, k), 2.8), A(0.4, 0, 2.3), 40)


HOST |= {'rook_corridor', 'chamber', 'stars', 'rook_desk', 'rook_board', 'rook_window', 'rook_pocket'}
SHOTS3D.update({f.__name__: f for f in (
    platform_work, locked_doors, rook_corridor, feel_walls, flashlights, mattress_build, plank_wait, shadow_pass, pray, divers_down,
    hammer, helmet_on, walk_out, chamber, stars, rook_desk, rook_board, rook_window, rook_pocket)})


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: the hand coming down through the water toward the diver's glove, Rook watching."""
    A = cabin(S, True, 1.52, 30, 260)
    S['beam'].location, S['beam'].rotation_euler = (1.6, -1.6, 0.25), (0.35, 0, -0.75)
    S['hand_o'].place(A(0.2, 0.0, 1.7), (PI / 2 - 0.15, 0, 0.35))
    S['hand_o'].root.scale = (1.5, 1.5, 1.5)
    S['hand_o'].grip(0.1)
    S['hand_d'].place(A(0.05, 0.05, 0.75), (-PI / 2 - 0.1, 0, 0.3))
    S['hand_d'].root.scale = (1.5, 1.5, 1.5)
    S['hand_d'].grip(0.15)
    S['rook'].place(A(-1.75, 0.4, -1.55), 0.5)
    S['rook'].apply(P('stand', aL=(0.5, 0.9, 1.5, -0.9), aR=(0.5, 0.9, 1.5, -0.9), head=(0.05, 0.35)))
    for o in S['rook'].extra['helmet']:
        o.hide_render = False
    S['rook'].extra['helmet'][0].hide_render = True          # no glass in the thumbnail: it doubles his face
    S['face']['rook'] = 'shocked'
    S['pov'].data.energy = 500
    bubbles(S, A(0.1, 0, 0.5), 1.0, 10, 0.7, 1.2, 0.7, size=0.8)
    cam(S, A(0.2, -4.4, 1.35), A(-0.1, 0, 1.45), 34)


STILLS['thumb'] = photo_thumb
