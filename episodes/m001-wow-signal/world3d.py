"""Open Case 001 in 3D - the Wow! signal, Big Ear radio telescope, Ohio, 15 August 1977. Sets built for this story only:
the Big Ear (a flat tilting reflector, a curved reflector and an aluminium ground plane the size of a car park),
the 1977 computer room with its line printer and Jerry Ehman's desk, and deep space with a cold hydrogen cloud
and a flaring dead star (the 2024 hypothesis)."""
import math

import bpy

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(ear=(0, 0, 0), lab=(600, 0, 0), space=(1200, 0, 0))
FAR = (0, 0, -900)
HOST = {'rook_plane', 'rook_walk', 'printer', 'rook_peek', 'rook_lean', 'rook_chart', 'ear_search', 'rook_listen', 'rook_space',
        'rook_cam', 'rook_comment', 'rook_pen', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
EHM = dict(top='C9B07A', pants='4A3A2A', hand='E0B08A', boot='2A2420')
ALU, ALU2, PAPER, BAR = '9AA6B4', '6E7A88', 'F2F0E4', 'BFE3C0'


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


def rnd(i, salt=0):
    """Deterministic pseudo-random 0..1 (no global random state, so every render job places things identically)."""
    x = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - math.floor(x)


def stars(r, n, radius, zmin, salt=0, size=0.5):
    out = []
    for i in range(n):
        a = rnd(i, salt) * 2 * PI
        e = math.asin(zmin + (1 - zmin) * rnd(i, salt + 1))
        s = size * (0.6 + 0.8 * rnd(i, salt + 2))
        col = ('FFFFFF', 'CFE0FF', 'FFE6C0')[i % 3]
        out.append(add('ico_sphere', col, (math.cos(a) * math.cos(e) * radius, math.sin(a) * math.cos(e) * radius, math.sin(e) * radius),
                       radius=s, subdivisions=1, parent=r, emit=6 + 6 * rnd(i, salt + 3)))
    return out


# ---------------------------------------------------------------- set 1: the Big Ear at night
def set_ear(r):
    add('cube', '16211A', (0, 0, -0.12), scale=(700, 700, 0.1), size=1, parent=r, rough=1.0)                 # Ohio fields
    add('cube', ALU, (0, 0, 0), scale=(84, 124, 0.1), size=1, parent=r, rough=0.32)                           # aluminium ground plane
    for i in range(-5, 6):
        add('cube', ALU2, (i * 8, 0, 0.06), scale=(0.12, 124, 0.02), size=1, parent=r, rough=0.5)
    for j in range(-7, 8):
        add('cube', ALU2, (0, j * 8, 0.06), scale=(84, 0.12, 0.02), size=1, parent=r, rough=0.5)
    for x in range(-42, 43, 6):                                                                               # fence posts
        for y in (-63, 63):
            add('cylinder', '4A4E56', (x, y, 0.8), radius=0.08, depth=1.6, vertices=5, parent=r)
    # flat reflector: a huge tilting wall on a truss at the north end
    flat = empty((0, 64, 0), r)
    add('cube', 'B8C2CE', (0, 0, 15), scale=(86, 0.6, 30), size=1, parent=flat, rough=0.3)
    for i in range(-6, 7):
        add('cube', '7E8896', (i * 7, -0.35, 15), scale=(0.25, 0.2, 30), size=1, parent=flat, rough=0.4)
    for z in range(3, 30, 6):
        add('cube', '7E8896', (0, -0.35, z), scale=(86, 0.2, 0.25), size=1, parent=flat, rough=0.4)
    for i in range(-6, 7):                                                                                     # back truss
        add('cylinder', '3A3F48', (i * 7, 8, 9), rot=(-0.85, 0, 0), radius=0.25, depth=22, vertices=5, parent=r)
        add('cylinder', '3A3F48', (i * 7, 9, 3), radius=0.3, depth=6, vertices=5, parent=r)
    # curved (parabolic) reflector at the south end, concave toward the plane
    for i in range(15):
        x = -42 + i * 6
        y = -66 + x * x / 220
        add('cube', 'A8B2BE', (x, y, 11), rot=(0.12, 0, math.atan(x / 110)), scale=(6.1, 0.5, 22), size=1, parent=r, rough=0.3)
        add('cube', '6E7886', (x, y - 0.4, 11), rot=(0.12, 0, math.atan(x / 110)), scale=(0.25, 0.3, 22), size=1, parent=r)
        add('cylinder', '3A3F48', (x, y - 5, 9), rot=(0.7, 0, 0), radius=0.25, depth=20, vertices=5, parent=r)
    # feed horn hut near the focus, horns facing north toward the flat reflector
    hut = empty((0, -40, 0), r)
    add('cube', '6E6A58', (0, 0, 1.6), scale=(7, 4.5, 3.2), size=1, parent=hut)
    add('cube', '4A463C', (0, 0, 3.3), scale=(7.6, 5.0, 0.3), size=1, parent=hut)
    win = add('cube', 'FFD08A', (2.2, 2.27, 1.9), scale=(1.4, 0.05, 0.9), size=1, parent=hut, emit=6)
    horns = []
    for s in (-1, 1):
        hn = add('cone', 'C8CCD4', (s * 1.8, 3.7, 2.6), rot=(-PI / 2, 0, PI / 4), radius1=1.4, radius2=0.35, depth=2.6, vertices=4,
                 parent=hut, rough=0.35)
        horns.append(hn)
        add('cube', '20242B', (s * 1.8, 2.45, 2.6), scale=(0.5, 0.2, 0.5), size=1, parent=hut)
    beacon = add('ico_sphere', 'FF3A2A', (0, 0, 3.8), radius=0.28, subdivisions=1, parent=hut, emit=18)
    glow = light((0, 4.2, 3.2), 3500, 'FF9A3A', kind='POINT', parent=hut)
    # control building and tree line
    add('cube', '5E5A4C', (-56, -56, 3), scale=(14, 9, 6), size=1, parent=r)
    for i in range(5):
        add('cube', 'FFD890', (-62 + i * 3, -51.45, 3.4), scale=(1.4, 0.05, 1.3), size=1, parent=r, emit=5)
    for i in range(70):
        a = i / 70 * 2 * PI
        d = 150 + 40 * rnd(i, 5)
        h = 10 + 9 * rnd(i, 6)
        add('cone', '0C1712', (math.cos(a) * d, math.sin(a) * d, h / 2), radius1=4 + 3 * rnd(i, 7), radius2=0, depth=h, vertices=6, parent=r)
    moon = add('ico_sphere', 'F4F0DC', (-160, 260, 120), radius=10, subdivisions=2, parent=r, emit=4)
    st = stars(r, 170, 420, 0.12, salt=1, size=0.7)
    moonl = light((0, 0, 60), 2.2, 'AFC0FF', kind='SUN', parent=r)
    moonl.rotation_euler = (0.6, 0.0, -0.5)
    sun = light((0, 0, 60), 0.0, 'FFB070', kind='SUN', parent=r)
    sun.rotation_euler = (1.25, 0.0, 2.6)
    return dict(flat=flat, hut_glow=glow, beacon=beacon, hutwin=win, moon=moon, ear_stars=st, moonl=moonl, dawnsun=sun)


# ---------------------------------------------------------------- set 2: the 1977 computer room
def set_lab(r):
    add('cube', '3A3430', (0, 0, -0.05), scale=(14, 12, 0.1), size=1, parent=r)                               # floor
    add('cube', '8A8268', (0, 6, 3), scale=(14, 0.2, 6), size=1, parent=r)                                   # back wall
    add('cube', '7A7258', (-7, 0, 3), scale=(0.2, 12, 6), size=1, parent=r)                                  # left wall
    add('cube', '6A624C', (7, 0, 3), scale=(0.2, 12, 6), size=1, parent=r)                                   # right wall
    add('cube', '2A2622', (0, 5.85, 0.3), scale=(14, 0.2, 0.6), size=1, parent=r)
    for i in range(3):                                                                                        # ceiling tubes
        add('cube', 'EAF6E8', (-3 + i * 3, 1.5, 5.9), scale=(0.3, 3.2, 0.1), size=1, parent=r, emit=5)
    blinks, reels = [], []
    for i in range(4):                                                                                        # mainframe cabinets
        x = -5.6 + i * 1.6
        add('cube', 'A4ACA6', (x, 5.1, 1.8), scale=(1.5, 1.2, 3.6), size=1, parent=r, rough=0.6)
        add('cube', '2A2E30', (x, 4.49, 3.2), scale=(1.2, 0.02, 0.6), size=1, parent=r)
        for j in range(10):
            col = ('FF4030', 'FFB000', '6CFF8A')[(i + j) % 3]
            blinks.append(add('cube', col, (x - 0.5 + j * 0.11, 4.47, 3.2 + 0.12 * ((j % 2) * 2 - 1)), scale=(0.06, 0.02, 0.06), size=1,
                              parent=r, emit=12))
        if i % 2 == 0:
            for s in (-1, 1):
                rl = empty((x + s * 0.35, 4.46, 1.9), r, (PI / 2, 0, 0))
                add('cylinder', '1A1C20', (0, 0, 0), radius=0.38, depth=0.06, vertices=10, parent=rl)
                add('cube', 'C8CCD4', (0, 0, 0.04), scale=(0.62, 0.08, 0.02), size=1, parent=rl)
                add('cylinder', 'C8CCD4', (0, 0, 0.05), radius=0.1, depth=0.04, vertices=8, parent=rl)
                reels.append(rl)
        else:
            add('cube', '30343A', (x, 4.48, 1.6), scale=(1.2, 0.02, 1.8), size=1, parent=r)
    # line printer with fanfold paper
    pr = empty((2.6, 2.4, 0), r)
    add('cube', 'B8B4A2', (0, 0, 0.55), scale=(2.0, 1.1, 1.1), size=1, parent=pr, rough=0.6)
    add('cube', '7A7666', (0, 0, 1.15), scale=(2.1, 1.2, 0.12), size=1, parent=pr)
    add('cube', '15181F', (0, -0.2, 1.22), scale=(1.4, 0.08, 0.04), size=1, parent=pr)
    add('cube', 'FFB000', (0.8, -0.56, 0.9), scale=(0.1, 0.02, 0.06), size=1, parent=pr, emit=10)
    feed = empty((0, -0.2, 1.2), pr)
    for i in range(9):
        add('cube', PAPER if i % 2 == 0 else BAR, (0, 0, 0.07 + i * 0.14), scale=(1.3, 0.012, 0.14), size=1, parent=feed, rough=0.8)
    for i in range(7):                                                                                        # pile on the floor
        add('cube', PAPER if i % 2 == 0 else BAR, (0, -1.0, 0.03 + i * 0.03), rot=(0, 0, 0.04 * ((i % 3) - 1)), scale=(1.3, 0.62, 0.03),
            size=1, parent=pr, rough=0.8)
    # Ehman's desk, lamp and stack of printouts
    add('cube', '6A4A30', (-1.6, -0.3, 1.12), scale=(2.6, 1.3, 0.1), size=1, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cube', '4A3420', (-1.6 + sx * 1.15, -0.3 + sy * 0.5, 0.55), scale=(0.1, 0.1, 1.1), size=1, parent=r)
    for i in range(5):
        add('cube', PAPER if i % 2 == 0 else BAR, (-2.4, -0.3, 1.2 + i * 0.03), rot=(0, 0, 0.05 * (i % 2)), scale=(0.9, 0.6, 0.03), size=1, parent=r)
    sheet = add('cube', PAPER, (-1.3, -0.45, 1.185), rot=(0, 0, -0.15), scale=(0.95, 0.7, 0.01), size=1, parent=r, rough=0.8)
    add('cylinder', '2A2622', (-0.4, 0.1, 1.2), radius=0.14, depth=0.06, vertices=8, parent=r)
    add('cylinder', '2A2622', (-0.4, 0.1, 1.6), radius=0.025, depth=0.8, vertices=5, parent=r)
    add('cone', '2E6A50', (-0.55, -0.05, 1.95), rot=(0.5, 0, 0.5), radius1=0.28, radius2=0.08, depth=0.36, vertices=8, parent=r)
    lampl = light((-0.75, -0.25, 1.8), 220, 'FFD9A0', kind='POINT', parent=r)
    add('cube', '3A3A40', (-1.6, 0.75, 0.55), scale=(0.9, 0.8, 0.1), size=1, parent=r)                      # chair
    add('cube', '3A3A40', (-1.6, 1.15, 1.05), scale=(0.9, 0.1, 1.0), size=1, parent=r)
    # wall chart: signal strength across the receiver's channels, one tall bar at the hydrogen line
    chart = empty((4.2, 5.85, 2.6), r)
    add('cube', 'F2F0E4', (0, 0, 0), scale=(3.0, 0.05, 2.0), size=1, parent=chart)
    add('cube', '2A2622', (0, 0.02, 0), scale=(3.2, 0.04, 2.2), size=1, parent=chart)
    bars = []
    for i in range(15):
        hgt = 0.12 + 0.1 * rnd(i, 9) if i != 8 else 1.55
        bars.append(add('cube', 'FF7A1A' if i == 8 else '4A5A6A', (-1.3 + i * 0.185, -0.05, -0.85 + hgt / 2), scale=(0.12, 0.03, hgt),
                        size=1, parent=chart, emit=2.5 if i == 8 else 0.0))
    add('cube', '2A2622', (0, -0.05, -0.86), scale=(2.8, 0.03, 0.03), size=1, parent=chart)
    room = light((0, -2, 5.4), 900, 'E8F0E0', 9.0, kind='AREA', parent=r)
    return dict(blinks=blinks, reels=reels, feed=feed, lampl=lampl, chart=chart, labroom=room, desk_sheet=sheet)


# ---------------------------------------------------------------- set 3: deep space
def set_space(r):
    st = stars(r, 260, 300, -1.0, salt=11, size=0.45)
    cloudm = K.mat('2EC4B6', 0.9, 0.6, 0.22)
    cloud = []
    for i in range(18):
        loc = ((rnd(i, 20) - 0.5) * 14, (rnd(i, 21) - 0.5) * 8, (rnd(i, 22) - 0.5) * 7)
        o = add('ico_sphere', '2EC4B6', loc, radius=2.2 + 2.2 * rnd(i, 23), subdivisions=2, parent=r, emit=0.6, alpha=0.22)
        o.data.materials[0] = cloudm
        bpy.ops.object.shade_smooth()
        cloud.append(o)
    star = empty((-18, 26, 5), r)
    add('ico_sphere', 'EAF2FF', (0, 0, 0), radius=0.7, subdivisions=2, parent=star, emit=12)
    beams = empty((0, 0, 0), star)
    for s in (-1, 1):
        add('cone', 'BFE6FF', (0, 0, s * 5), rot=(0 if s > 0 else PI, 0, 0), radius1=0.0, radius2=1.4, depth=10, vertices=8, parent=beams,
            emit=3, alpha=0.25)
    shell = add('ico_sphere', 'FFFFFF', (0, 0, 0), radius=1.0, subdivisions=2, parent=star, emit=5, alpha=0.3)
    starl = light((0, 0, 0), 0, 'CFE8FF', kind='POINT', parent=star)
    earth = empty((10, -70, -6), r)
    add('ico_sphere', '2860C8', (0, 0, 0), radius=3.2, subdivisions=3, parent=earth, rough=0.6)
    for i in range(7):
        a, e = rnd(i, 30) * 2 * PI, (rnd(i, 31) - 0.5) * 1.6
        add('ico_sphere', '3E8A4A', (math.cos(a) * math.cos(e) * 2.95, math.sin(a) * math.cos(e) * 2.95, math.sin(e) * 2.95),
            scale=(1, 1, 0.45), radius=0.9 + 0.5 * rnd(i, 32), subdivisions=1, parent=earth)
    add('ico_sphere', 'FF7A1A', (-1.2, 2.6, 1.3), radius=0.16, subdivisions=1, parent=earth, emit=20)       # Ohio
    ring = add('torus', 'FF7A1A', FAR, major_radius=1.0, minor_radius=0.06, major_segments=24, minor_segments=4, emit=8)
    fill = light((0, -14, 6), 2500, '9ADCE8', 12.0, kind='AREA', parent=r)
    light((22, -58, 6), 9000, 'FFF2DA', kind='POINT', parent=r)                                               # sunlight on Earth
    return dict(sp_stars=st, cloud=cloud, cloudm=cloudm, magnetar=star, beams=beams, shell=shell, starl=starl, earth=earth, ring=ring,
                sp_fill=fill)


# ---------------------------------------------------------------- build / reset / finish
PEOPLE = ('ehman',)


def ehman_head(head):
    d = K.human_head('E0B08A', '5A3A22')(head)
    for s in (-1, 1):
        add('cube', '1A1A20', (s * 0.105, -0.29, 0.04), scale=(0.15, 0.015, 0.12), size=1, parent=head, rough=0.3)
        add('cube', 'DFF2FF', (s * 0.105, -0.297, 0.04), scale=(0.12, 0.01, 0.09), size=1, parent=head, rough=0.05, alpha=0.25)
    add('cube', '1A1A20', (0, -0.29, 0.06), scale=(0.08, 0.015, 0.02), size=1, parent=head)
    d['eye0'] = 0.075
    return d


def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('ear', set_ear), ('lab', set_lab), ('space', set_space)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['ehman'] = K.Rig(EHM, ehman_head)
    for s in (-1, 1):                                                                                          # rolled-up sleeves
        add('cylinder', 'E0B08A', (0, 0, -0.32), radius=0.075, depth=0.3, vertices=6, parent=S['ehman'].el[(s + 1) // 2])
    ph = [add('torus', '1A1C20', (0, 0.02, 0.08), rot=(0, PI / 2, 0), major_radius=0.42, minor_radius=0.035, major_segments=12,
              minor_segments=4, parent=S['rook'].head)]
    for s in (-1, 1):
        ph.append(add('cylinder', '1A1C20', (s * 0.37, 0, -0.02), rot=(0, PI / 2, 0), radius=0.15, depth=0.1, vertices=10, parent=S['rook'].head))
        ph.append(add('cylinder', 'FF7A1A', (s * 0.43, 0, -0.02), rot=(0, PI / 2, 0), radius=0.08, depth=0.04, vertices=8, parent=S['rook'].head,
                      emit=4))
    S['phones'] = ph
    pen = empty(FAR)
    add('cylinder', 'D8261E', (0, 0, 0), radius=0.06, depth=0.7, vertices=8, parent=pen, rough=0.3)
    add('cone', 'F4EEDF', (0, 0, -0.42), radius1=0.06, radius2=0.0, depth=0.14, vertices=8, parent=pen)
    add('cylinder', 'FFC233', (0, 0, 0.3), radius=0.065, depth=0.12, vertices=8, parent=pen, rough=0.2, emit=1.5)
    add('cube', 'FFC233', (0.07, 0, 0.18), scale=(0.02, 0.03, 0.3), size=1, parent=pen, rough=0.2, emit=1.5)
    S['pen'] = pen
    S['kwa'], S['kca'] = empty(), empty()
    S['kw'] = light((0, 0, 0), 0, 'FFDCB8', 4.0, S['kwa'])
    S['kc'] = light((0, 0, 0), 0, '9ADCE8', 5.0, S['kca'])
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 2500
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
    S[which].location, S[which + 'a'].location = pos, look
    S[which].data.energy = energy


def emit(m, v):
    m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = v


def reset(S):
    for who in ('rook',) + PEOPLE:
        S[who].place(FAR)
        S[who].apply(P())
    S['face'] = dict(rook='calm', ehman='calm')
    S['hat_tip'] = 0.0
    for o in S['phones']:
        o.hide_render = True
    S['pen'].location, S['pen'].rotation_euler, S['pen'].scale = FAR, (0, 0, 0), (1, 1, 1)
    for kk in ('kw', 'kc'):
        S[kk].data.energy = 0
    S['flat'].rotation_euler = (-0.35, 0, 0)
    S['hut_glow'].data.energy = 3500
    S['beacon'].hide_render = False
    S['hutwin'].hide_render = False
    S['moonl'].data.energy, S['dawnsun'].data.energy = 2.2, 0.0
    S['moon'].hide_render = False
    for o in S['ear_stars']:
        o.hide_render = False
    S['feed'].location.z = 1.2
    S['lampl'].data.energy = 220
    S['labroom'].data.energy = 900
    emit(S['cloudm'], 0.6)
    S['shell'].scale = (0.01, 0.01, 0.01)
    S['starl'].data.energy = 0
    S['ring'].location, S['ring'].scale, S['ring'].rotation_euler = FAR, (1, 1, 1), (0, 0, 0)
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
    r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.14, sad=0.22).get(e, 0.0) + tip * 0.35, 0.07, 0)
    r['hat'].location.z = 0.27 + (0.11 if e == 'shocked' else 0.0) + tip * 0.1
    for o in r['helmet']:
        o.hide_render = True
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
        x['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
        x['jaw'].location.z = -0.13 - (0.05 if e == 'shock' else 0.0)


# ---------------------------------------------------------------- helpers
def ear(S, mode='night'):
    A = show(S, 'ear')
    if mode == 'night':
        sky(S, '0A1236', 1.0)
    elif mode == 'dark':
        sky(S, '060A1E', 1.0)
        S['moonl'].data.energy = 1.2
    else:                                                       # dawn
        sky(S, 'C8865A', 1.0)
        S['moonl'].data.energy, S['dawnsun'].data.energy = 0.6, 3.2
        S['moon'].hide_render = True
        S['hut_glow'].data.energy = 600
        for o in S['ear_stars']:
            o.hide_render = True
    return A


def lab(S, t):
    A = show(S, 'lab')
    sky(S, '000000')
    for i, b in enumerate(S['blinks']):
        b.hide_render = rnd(i + int(t * 6), 40) < 0.4
    for i, rl in enumerate(S['reels']):
        rl.rotation_euler = (PI / 2, (t * (2.2 + 0.4 * i)) % (2 * PI), 0)
    return A


def space(S):
    A = show(S, 'space')
    sky(S, '05040E', 1.0)
    return A


def feed(S, t, speed=0.9):
    S['feed'].location.z = 1.2 + ((t * speed) % 0.28) - 0.28


def rook(S, loc, yaw, pose, expr='calm'):
    S['rook'].place(loc, yaw)
    S['rook'].apply(pose)
    S['face']['rook'] = expr


def ehman_sit(S, A, pose=None, face='calm', yaw=0.0):
    S['ehman'].place(A(-1.6, 0.55, 0.1), yaw)
    S['ehman'].apply(pose or P('sit', aL=(0.9, -0.05, 1.3, 0.6), aR=(0.95, -0.05, 1.2, 0.6), head=(0.45, 0.0)))
    S['face']['ehman'] = face


def ring_at(S, loc, scale, rot=(PI / 2, 0, 0)):
    S['ring'].location, S['ring'].scale, S['ring'].rotation_euler = loc, (scale, scale, scale), rot


# ---------------------------------------------------------------- hook
def beam_hit(S, k, t, lt):
    A = space(S)
    y = lerp(10, -36.5, ease(k * 1.1))
    ring_at(S, A(34, y, 9.6), lerp(1.2, 5.5, k * k))
    S['ring'].rotation_euler = (PI / 2, 0, t * 2)
    S['starl'].data.energy = 0
    cam(S, A(34.4, -42, 9.8), A(34, 0, 9.6), 26, roll=0.05 * math.sin(t * 9))


def ear_night(S, k, t, lt):
    A = ear(S)
    S['beacon'].hide_render = (t * 1.6) % 1 < 0.5
    cam(S, A(lerp(-36, -32, k), lerp(-58, -54, k), lerp(4.0, 5.0, k)), A(0, 18, 7), 21)


def ear_sweep(S, k, t, lt):
    A = ear(S)
    S['flat'].rotation_euler = (lerp(-0.25, -0.5, ease(k)), 0, 0)
    cam(S, A(lerp(30, 24, k), lerp(26, 30, k), lerp(6, 14, ease(k))), A(0, 62, lerp(14, 12, k)), 24)


def ear_dark(S, k, t, lt):
    A = ear(S, 'dark')
    S['hut_glow'].data.energy = lerp(3500, 0, ease(k * 1.6))
    S['beacon'].hide_render = k > 0.35
    S['hutwin'].hide_render = k > 0.5
    cam(S, A(lerp(9, 13, k), lerp(-22, -18, k), lerp(2.5, 4.0, k)), A(0, -40, 2.4), 24)


# ---------------------------------------------------------------- doubt
def rook_plane(S, k, t, lt):
    A = ear(S)
    sh = math.sin(lt * 9) * 0.32 * max(0.0, 1 - lt / 1.2)
    rook(S, A(0, -20, 0.05), 0.12, P('cross', head=(0.05, sh)), 'deadpan')
    S['hat_tip'] = 0.4
    key(S, 'kw', A(-3, -25, 4), A(0, -20, 2.2), 900)
    key(S, 'kc', A(4, -17, 3.5), A(0, -20, 2.2), 700)
    cam(S, A(lerp(1.6, 1.1, k), lerp(-27.2, -25.6, k), 2.1), A(0, -20, 2.35), 31)


def rook_walk(S, k, t, lt):
    A = ear(S)
    if lt < 0.45:
        pose = blend(P('stand'), P('hat', head=(0.1, 0)), lt / 0.3)
        y = -21
    else:
        pose = walk(lt - 0.45)
        y = -21 + (lt - 0.45) * 2.2
    rook(S, A(0, y, 0.05), PI, pose, 'smirk')
    key(S, 'kw', A(-4, y - 3, 4), A(0, y, 2.0), 800)
    key(S, 'kc', A(3, y + 4, 3), A(0, y, 2.0), 700)
    cam(S, A(1.9, y - 6.0, 1.7), A(0.2, y + 6, 3.2), 24)


# ---------------------------------------------------------------- scope
def ear_aerial(S, k, t, lt):
    A = ear(S)
    S['beacon'].hide_render = (t * 1.6) % 1 < 0.5
    cam(S, A(lerp(-70, -62, k), lerp(-108, -98, k), lerp(78, 70, k)), A(0, 2, 0), 24, roll=lerp(-0.04, 0.02, k))


def horn_cu(S, k, t, lt):
    A = ear(S)
    S['beacon'].hide_render = (t * 1.6) % 1 < 0.5
    S['hut_glow'].data.energy = 900
    key(S, 'kc', A(-6, -30, 7), A(0, -36.5, 2.6), 260)
    cam(S, A(lerp(6.5, 5.0, k), lerp(-26.5, -27.8, k), lerp(4.0, 3.4, k)), A(0, -36.4, 2.6), 30)


def printer(S, k, t, lt):
    A = lab(S, t)
    feed(S, t)
    pull = math.sin(min(1.0, lt / 0.6) * PI / 2)
    rook(S, A(3.7, 1.0 - 0.5 * ease(k), 0), 0.75 - 0.6 * ease(k),
         blend(P('stand', head=(0.2, -0.4)), P('stand', aL=(1.1, 0.1, 1.1), aR=(1.0, 0.0, 1.2), lean=0.12 * k, head=(0.35, 0.3 * k)), pull),
         'calm' if k < 0.6 else 'smirk')
    key(S, 'kw', A(1.5, -1.5, 3.2), A(3.3, 1.4, 1.8), 520)
    cam(S, A(lerp(0.2, 2.0, ease(k)), lerp(-3.8, -2.7, ease(k)), lerp(1.6, 2.5, k)), A(2.9, 1.5, 1.6), 26)


# ---------------------------------------------------------------- wow
def ehman_desk(S, k, t, lt):
    A = lab(S, t)
    ehman_sit(S, A, face='tired')
    S['lampl'].data.energy = 260
    key(S, 'kw', A(-1.0, -2.5, 2.6), A(-1.6, 0.4, 1.8), 260)
    cam(S, A(lerp(-1.2, -1.45, k), lerp(-4.4, -3.4, k), lerp(2.6, 2.3, k)), A(-1.6, 0.3, 1.55), 30)


def rook_peek(S, k, t, lt):
    A = lab(S, t)
    ehman_sit(S, A)
    lean = lerp(0.05, 0.42, ease(k * 1.4))
    rook(S, A(-0.55, 1.45, 0), 0.35, P('stand', aL=(0.3, 0.3, 1.4, -0.6), aR=(0.25, -0.1, 1.6, 1.2), lean=lean, head=(0.35, 0.2)), 'smirk')
    key(S, 'kw', A(0.8, -1.4, 3.4), A(-0.8, 1.2, 2.2), 420)
    key(S, 'kc', A(-3.0, 2.5, 3), A(-0.8, 1.2, 2.2), 260)
    cam(S, A(lerp(0.2, -0.1, k), lerp(-2.6, -2.2, k), 2.5), A(-1.05, 0.85, 1.95), 27)


def ehman_shock(S, k, t, lt):
    A = lab(S, t)
    e = ease(lt / 0.35)
    ehman_sit(S, A, blend(P('sit', aL=(0.9, -0.05, 1.3, 0.6), aR=(0.95, -0.05, 1.2, 0.6), head=(0.45, 0)),
                          P('sit', aL=(0.6, 0.3, 1.4, 0.4), aR=(1.9, 0.2, 1.3, 0.2), lean=-0.1, head=(-0.1, 0.05)), e), 'shock')
    bpy.context.view_layer.update()
    hand = S['ehman'].hands[1].matrix_world.translation
    S['pen'].location = (hand.x, hand.y - 0.05, hand.z + 0.2)
    S['pen'].rotation_euler = (0.3, 0.2, 0)
    key(S, 'kw', A(-0.8, -2.2, 2.4), A(-1.6, 0.5, 1.7), 320)
    cam(S, A(lerp(-0.9, -1.1, k), lerp(-2.6, -2.2, k), 1.35), A(-1.55, 0.5, 1.75), 28)


# ---------------------------------------------------------------- clue
def rook_lean(S, k, t, lt):
    A = lab(S, t)
    feed(S, t)
    e = ease(lt / 0.4)
    rook(S, A(1.6, 0.3, 0), 0.0, blend(P('stand', head=(0.0, 0.1)), P('stand', aR=(2.5, 0.15, 0.5, 0.3), lean=0.22, head=(0.1, -0.05)), e), 'smirk')
    key(S, 'kw', A(0.0, -2.0, 3.2), A(1.6, 0.3, 2.4), 520)
    key(S, 'kc', A(3.5, 2.0, 3.0), A(1.6, 0.3, 2.4), 360)
    cam(S, A(lerp(1.75, 1.7, k), lerp(-2.6, -2.0, k), 2.5), A(1.6, 0.0, 2.35), 30)


def rook_chart(S, k, t, lt):
    A = lab(S, t)
    e = ease(lt / 0.35)
    rook(S, A(2.85, 5.0, 0), PI / 2, blend(P('stand', head=(0, 0.5)), P('point', aR=(1.65, 0.0, 0.05), head=(-0.1, 0.0)), e), 'shocked' if k > 0.5 else 'calm')
    S['hat_tip'] = 0.5 if k > 0.5 else 0.0
    key(S, 'kw', A(2.0, 1.5, 3.6), A(3.6, 4.8, 2.4), 520)
    cam(S, A(lerp(5.3, 5.0, k), lerp(1.4, 1.9, k), 2.6), A(3.6, 5.2, 2.3), 26)


# ---------------------------------------------------------------- gone
def ear_search(S, k, t, lt):
    A = ear(S)
    S['flat'].rotation_euler = (-0.35 + 0.18 * math.sin(lt * 2.2), 0, 0)
    S['beacon'].hide_render = (t * 1.6) % 1 < 0.5
    rook(S, A(0.9, -10, 0.05), PI + 0.2, P('stand', aR=(0.2, 0.9, 1.6, -1.3), head=(-0.45, 0.0)), 'calm')
    key(S, 'kw', A(-2, -14, 4), A(0.9, -10, 2), 700)
    cam(S, A(lerp(1.5, 2.2, k), lerp(-17.5, -16.5, k), 1.0), A(-1, 30, 13), 22)


def rook_listen(S, k, t, lt):
    A = ear(S, 'dark')
    for o in S['phones']:
        o.hide_render = False
    e = ease((lt - 0.5) / 0.4)
    rook(S, A(0, -24, 0.05), 0.1, blend(P('stand', aR=(0.5, 0.95, 2.4, -1.4), head=(0.1, -0.35)), P('shrug', head=(0.12, 0)), e),
         'deadpan' if e < 0.5 else 'sad')
    key(S, 'kw', A(-2.6, -28, 3.6), A(0, -24, 2.4), 820)
    key(S, 'kc', A(3, -21, 3), A(0, -24, 2.4), 600)
    cam(S, A(lerp(0.8, 0.6, k), lerp(-28.6, -28.0, k), 2.45), A(0, -24, 2.45), 34)


# ---------------------------------------------------------------- twist
def cloud(S, k, t, lt):
    A = space(S)
    emit(S['cloudm'], 0.8)
    cam(S, A(lerp(-3, 5, k), lerp(-22, -18, k), lerp(4, 2, k)), A(0, 0, 0), 26, roll=lerp(-0.08, 0.05, k))


def flare(S, k, t, lt):
    A = space(S)
    f = ease((k - 0.2) / 0.5)
    S['beams'].rotation_euler = (0.6, 0, t * 4)
    s = 0.6 + 4.5 * f
    S['shell'].scale = (s, s, s)
    S['starl'].data.energy = 60000 * f
    emit(S['cloudm'], lerp(0.6, 7.0, ease((k - 0.45) / 0.4)))
    cam(S, A(lerp(-30, -27, k), lerp(-16, -14, k), lerp(14, 12, k)), A(-8, 12, 2), 22)


def rook_space(S, k, t, lt):
    A = space(S)
    emit(S['cloudm'], 6.0 + 1.5 * math.sin(t * 8))
    sh = ease(lt / 0.3)
    rook(S, A(-2, -11, -1.6 + 0.12 * math.sin(t * 1.4)), 0.25, P('up', head=(-0.2, -0.2), lift=0.1), 'shocked')
    S['rook'].root.rotation_euler = (0.12 * math.sin(t * 0.8), 0.08, 0.25 + 0.1 * math.sin(t * 0.6))
    S['hat_tip'] = sh
    key(S, 'kw', A(-4, -15, 2), A(-2, -11, 0.8), 900)
    key(S, 'kc', A(1, -7, 1), A(-2, -11, 0.8), 1600)
    cam(S, A(lerp(-0.4, -0.9, k), lerp(-17.0, -16.0, k), lerp(0.4, 0.8, k)), A(-1.8, -11, 0.7), 30)


def wave_earth(S, k, t, lt):
    A = space(S)
    emit(S['cloudm'], 5.0)
    p = ease(k)
    loc = (lerp(2, 9.5, p), lerp(-20, -64, p), lerp(0, -5, p))
    ring_at(S, A(*loc), lerp(4.0, 0.8, p), (PI / 2, 0, t * 3))
    S['earth'].rotation_euler = (0.3, 0, t * 0.8)
    cam(S, A(lerp(24, 14, ease(k)), lerp(-38, -52, ease(k)), lerp(5, -1, k)), A(9, -64, -5), lerp(26, 34, k))


# ---------------------------------------------------------------- question
def rook_cam(S, k, t, lt):
    A = ear(S)
    e = ease(lt / 0.45)
    rook(S, A(0.5, -18, 0.05), 0.0, blend(P('stand', head=(0.05, 0)), P('shrug', head=(0.0, 0.0), lean=0.08), e), 'smirk')
    key(S, 'kw', A(-2.4, -22, 3.8), A(0.5, -18, 2.4), 900)
    key(S, 'kc', A(3.4, -15, 3.0), A(0.5, -18, 2.4), 700)
    cam(S, A(0.5, lerp(-22.6, -22.0, k), 2.45), A(0.5, -18, 2.35), 30)


# ---------------------------------------------------------------- end
def ear_dawn(S, k, t, lt):
    A = ear(S, 'dawn')
    cam(S, A(lerp(-30, -26, k), lerp(-40, -38, k), lerp(5, 7, k)), A(0, 40, 10), 22)


def rook_comment(S, k, t, lt):
    A = ear(S, 'dawn')
    e = ease(lt / 0.35)
    rook(S, A(0, -22, 0.05), 0.0, blend(P('stand', head=(0.1, 0)), P('stand', aR=(0.55, 0.25, 0.1), head=(0.35, -0.1), lean=0.1), e), 'smirk')
    key(S, 'kw', A(-3, -26, 4), A(0, -22, 2.2), 700)
    cam(S, A(lerp(1.4, 1.0, k), lerp(-27.0, -26.2, k), lerp(2.9, 2.7, k)), A(0, -22, 1.9), 30)


def rook_pen(S, k, t, lt):
    A = ear(S, 'dawn')
    rook(S, A(0, -21, 0.05), 0.35, P('stand', aR=(1.25, 0.45, 0.55, 0.2), head=(0.1, -0.45)), 'warm')
    bpy.context.view_layer.update()
    hand = S['rook'].hands[1].matrix_world.translation
    S['pen'].location = (hand.x, hand.y, hand.z + 0.26)
    S['pen'].rotation_euler = (0.2, 0.3, t * 3)
    key(S, 'kw', A(-1, -25, 3.4), A(0.4, -21.6, 2.2), 800)
    cam(S, A(lerp(1.5, 1.2, k), lerp(-24.4, -23.9, k), 2.3), A(0.45, -21.5, 2.15), 32)


def signoff(S, k, t, lt):
    A = ear(S, 'dawn')
    rook(S, A(0, -20, 0.05), 0.2, P('stand'), 'smirk')
    c = max(0.0, min(1.0, (lt - 0.2) / 0.9))
    S['rook'].apply(blend(P('stand', aR=(0.9, 0.25, 1.2), head=(0.05, 0)), P('stand', aR=(1.2, 0.2, 1.5), head=(-0.12, 0)), math.sin(c * PI)))
    S['pen'].location = A(0.75 + 0.2 * c, -20.75, 1.8 + 2.4 * math.sin(c * PI))
    S['pen'].rotation_euler = (t * 19, t * 9, 0)
    S['pen'].scale = (1.25, 1.25, 1.25)
    key(S, 'kw', A(-2, -24, 3.5), A(0, -20, 2.2), 800)
    key(S, 'kc', A(3, -17, 3), A(0, -20, 2.2), 500)
    cam(S, A(lerp(1.7, 1.3, k), lerp(-25.0, -24.2, k), 0.9), A(0, -20, 2.25), 36)


# ---------------------------------------------------------------- stills for the case board
def photo_ear(S, k, t, lt):
    A = ear(S)
    cam(S, A(-30, -54, 5), A(0, 30, 9), 22)


def photo_cloud(S, k, t, lt):
    A = space(S)
    emit(S['cloudm'], 4.0)
    cam(S, A(4, -20, 3), A(0, 0, 0), 26)


SHOTS3D = {f.__name__: f for f in (
    beam_hit, ear_night, ear_sweep, ear_dark, rook_plane, rook_walk, ear_aerial, horn_cu, printer, ehman_desk, rook_peek, ehman_shock,
    rook_lean, rook_chart, ear_search, rook_listen, cloud, flare, rook_space, wave_earth, rook_cam, ear_dawn, rook_comment, rook_pen,
    signoff)}
STILLS = dict(ear=photo_ear, cloud=photo_cloud)
