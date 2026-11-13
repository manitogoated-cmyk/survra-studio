"""Case 006 in 3D - Ewa Wisnierska, Manilla (New South Wales), 14 February 2007. Sets built for this story only:
the launch hill above the plains with the storm tower growing behind it, the inside of the storm cloud (a shaft of
scrolling cloud walls), the dark sky above the cloud tops, and the paddock where she lands."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(hill=(0, 0, 0), cloud=(700, 0, 0), high=(1400, 0, 0), field=(0, 900, 0))
FAR = (0, 0, -900)
HOST = {'rook_hill', 'rook_collar', 'takeoff', 'storm_build', 'rook_sock', 'spiral', 'rook_brolly', 'rook_ice', 'top_out',
        'rook_watch', 'descend', 'landing', 'dusk_hill', 'rook_hat', 'ewa_field', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
EWA = dict(top='C83248', pants='2A3040', hand='20242B', boot='3A3A44', fore='A82A3E')
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


def lerp_col(a, b, k):
    k = max(0.0, min(1.0, k))
    ca, cb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


# ---------------------------------------------------------------- props
def wing_pt(u):
    return 6.6 * math.sin(u * 1.15) / math.sin(1.15), 8.6 - 2.4 * (1 - math.cos(u * 1.15)) / (1 - math.cos(1.15))


def make_glider(r):
    """Paraglider. Origin = the pilot's seat; she flies toward local -Y; the wing arcs overhead."""
    wing = empty((0, 0, 0), r)
    ice = []
    for i in range(11):
        u = (i - 5) / 5
        x, z = wing_pt(u)
        col = 'D8324A' if i in (0, 1, 5, 9, 10) else 'EDE8DC'
        add('cube', col, (x, 0.2, z), rot=(0, u * 0.75, 0), scale=(1.42, 2.7 - 0.9 * u * u, 0.3), size=1, parent=wing)
        add('cube', '20242B', (x, -1.12 + 0.45 * u * u, z - 0.02), rot=(0, u * 0.75, 0), scale=(1.44, 0.22, 0.34), size=1, parent=wing)
        if i % 2 == 1:
            ice.append(add('cone', 'DFF4FF', (x, -1.1 + 0.45 * u * u, z - 0.5), rot=(PI, 0, 0), radius1=0.16, radius2=0.0, depth=0.8,
                           vertices=4, parent=wing, emit=0.5))
    for s in (-1, 1):
        top = (s * 0.5, 0, 2.3)
        rod((s * 0.4, 0.05, 0.95), top, 0.04, '20242B', wing)
        for u, y in ((0.36, -0.7), (0.36, 0.9), (0.7, -0.5), (0.7, 0.8), (0.95, 0.1)):
            x, z = wing_pt(u * s)
            rod(top, (x, y, z - 0.15), 0.018, 'B8BCC8', wing)
    add('cube', '20242B', (0, 0.36, 0.42), scale=(0.84, 0.5, 1.15), size=1, parent=r)
    add('cube', '2A2F3A', (0, -0.05, -0.1), scale=(0.8, 1.0, 0.14), size=1, parent=r)
    add('cube', 'D8324A', (0, 0.62, 0.5), scale=(0.5, 0.04, 0.7), size=1, parent=r)
    return wing, ice


def ewa_head(head):
    out = K.human_head('E8B898', '6A4A2A')(head)
    add('ico_sphere', 'EDE8DC', (0, 0.05, 0.11), scale=(1.0, 1.06, 0.95), radius=0.335, subdivisions=1, parent=head, rough=0.4)
    add('cube', 'D8324A', (0, 0.05, 0.3), scale=(0.12, 0.6, 0.12), size=1, parent=head)
    for s in (-1, 1):
        add('cube', '20242B', (s * 0.27, -0.08, -0.12), scale=(0.05, 0.1, 0.3), size=1, parent=head)
    out['ice'] = [add('ico_sphere', 'DFF4FF', (x, y, z), radius=r_, subdivisions=1, parent=head, emit=0.5)
                  for x, y, z, r_ in ((0.14, -0.22, 0.34, 0.06), (-0.16, -0.14, 0.38, 0.05), (0.0, 0.1, 0.44, 0.06), (-0.22, -0.26, 0.2, 0.045), (0.24, -0.2, 0.18, 0.04))]
    return out


def make_brolly(r):
    add('cylinder', '8A90A6', (0, 0, 0.9), radius=0.03, depth=1.8, vertices=5, parent=r, rough=0.4)
    add('torus', '8A6A4A', (0.09, 0, -0.02), rot=(PI / 2, 0, 0), major_radius=0.09, minor_radius=0.03, major_segments=8, minor_segments=4, parent=r)
    can = empty((0, 0, 1.75), r)
    add('cone', '20242B', (0, 0, -0.22), radius1=1.35, radius2=0.04, depth=0.5, vertices=8, parent=can)
    add('cone', 'FF7A1A', (0, 0, 0.1), radius1=0.12, radius2=0.0, depth=0.24, vertices=6, parent=can)
    for i in range(8):
        a = i * PI / 4
        rod((0, 0, 0.0), (math.cos(a) * 1.33, math.sin(a) * 1.33, -0.47), 0.018, '8A90A6', can)
    ice = [add('cone', 'DFF4FF', (math.cos(i * PI / 4) * 1.3, math.sin(i * PI / 4) * 1.3, -0.68), rot=(PI, 0, 0), radius1=0.07, radius2=0.0, depth=0.4,
               vertices=4, parent=can, emit=0.5) for i in range(8)]
    return can, ice


# ---------------------------------------------------------------- sets
def set_hill(r):
    add('plane', '8E8444', (0, 0, -9), size=1600, parent=r)
    cols = ('A89848', '7C8A3E', 'B8A050', '6E7C36', '9A8A40', 'C0AC5C')
    for i in range(34):
        add('cube', cols[i % 6], (-340 + (i * 97) % 680, 30 + (i * 53) % 430, -8.93), rot=(0, 0, (i % 5) * 0.2),
            scale=(40 + i % 4 * 18, 26 + i % 3 * 14, 0.1), size=1, parent=r)
    add('cone', '7C8A3E', (0, 0, -4.5), radius1=46, radius2=15, depth=9, vertices=12, parent=r)
    add('cylinder', '8A9444', (0, 0, -0.03), radius=15, depth=0.1, vertices=12, parent=r)
    add('cube', '3F7A4A', (9, 1, 0.04), scale=(9, 7, 0.06), size=1, parent=r)
    add('cube', '3F7A4A', (15.9, 1, -1.05), rot=(0, 0.4, 0), scale=(5.6, 7, 0.06), size=1, parent=r)
    for sy in (-1, 1):
        add('cube', 'F4EEDF', (9, 1 + sy * 3.4, 0.08), scale=(9, 0.14, 0.04), size=1, parent=r)
    add('cylinder', 'D8D4C8', (-5, 3, 2.6), radius=0.07, depth=5.2, vertices=6, parent=r)
    sock = empty((-5, 3, 5.1), r)
    for j in range(4):
        add('cone', 'FF7A1A' if j % 2 == 0 else 'F4EEDF', (0.3 + j * 0.5, 0, 0), rot=(0, PI / 2, 0), radius1=0.36 - j * 0.06, radius2=0.3 - j * 0.06,
            depth=0.5, vertices=8, parent=sock)
    for i, (x, y) in enumerate(((-10, 7), (-12, 0), (-9, 12.5), (11, 12), (-11, -6))):
        add('cylinder', 'C8C0B0', (x, y, 2.0), radius=0.24, depth=4.0, vertices=6, parent=r)
        for j in range(3):
            add('ico_sphere', ('5E7040', '4E6034', '6A7C48')[(i + j) % 3], (x + (j - 1) * 1.3, y + (j % 2) * 0.8, 4.3 + (j % 2) * 0.9),
                scale=(1, 1, 0.62), radius=1.7 + 0.3 * j, subdivisions=1, parent=r)
    for x in (1.2, 3.0):
        add('cylinder', '6A5238', (x, 7, 0.8), radius=0.08, depth=1.6, vertices=5, parent=r)
    add('cube', '8A6A4A', (2.1, 7, 1.5), scale=(2.4, 0.08, 0.9), size=1, parent=r)
    add('cube', 'F4EEDF', (2.1, 6.95, 1.5), scale=(2.0, 0.04, 0.5), size=1, parent=r)
    for i in range(7):
        add('ico_sphere', '8A8478', (-7 + i * 2.6, -5 - (i % 3) * 2.2, 0.15), scale=(1, 1.2, 0.5), radius=0.35 + 0.15 * (i % 3), subdivisions=1, parent=r)
    for i in range(10):
        hgt = 34 + i % 4 * 16
        add('cone', ('66785E', '5A6C58', '74846A')[i % 3], (-430 + i * 95, 620 + (i % 3) * 30, -9 + hgt / 2), radius1=80 + i % 3 * 20, radius2=6, depth=hgt,
            vertices=6, parent=r)
    tower = empty((60, 300, -9), r)
    for i in range(12):
        a = i * PI / 6
        add('ico_sphere', ('232A3C', '2C3448')[i % 2], (math.cos(a) * 62, math.sin(a) * 30, 44), scale=(1, 1, 0.5), radius=36, subdivisions=2, parent=tower)
    for i in range(9):
        add('cube', '39435A', (-64 + i * 16, 4, 14), rot=(0, 0.16, 0), scale=(5, 3, 34), size=1, parent=tower)
    for i in range(16):
        lvl = i // 2
        add('ico_sphere', ('59647E', '6E7892', '8791AA', 'A3ACC2', 'BEC6D8', 'D4DAE8', 'E4E8F2', 'EEF1F8')[lvl],
            (math.sin(i * 1.9) * (30 - lvl * 1.5), math.cos(i * 2.3) * 12, 62 + i * 8.5), radius=30 - lvl * 1.2, subdivisions=2, parent=tower, emit=0.05 + 0.04 * lvl)
    for i in range(13):
        add('ico_sphere', ('E4E8F2', 'D4DAE8')[i % 2], (-150 + i * 25, math.sin(i * 1.3) * 14, 200 + (i % 2) * 5), scale=(1, 1, 0.36), radius=30, subdivisions=2,
            parent=tower, emit=0.3)
    tfl = add('ico_sphere', 'DCE8FF', (-10, -34, 52), radius=9, subdivisions=1, parent=tower, emit=30)
    minis = []
    for i in range(6):
        g = empty((0, 0, -60), r)
        col = ('E8C23A', '3A8AD8', 'EDE8DC', '48B878', 'B05AD0', 'E8742A')[i]
        for j in (-1, 0, 1):
            add('cube', col, (j * 1.5, 0, -abs(j) * 0.35), rot=(0, j * 0.45, 0), scale=(1.6, 1.1, 0.16), size=1, parent=g)
        add('ico_sphere', '20242B', (0, 0, -2.4), radius=0.3, subdivisions=1, parent=g)
        minis.append(g)
    aim = empty((0, 0, 2), r)
    sun = light((-70, -90, 80), 4.0, 'FFE2B0', kind='SUN', target=aim, parent=r)
    light((7, 6, 5), 2600, 'FF7A1A', 3.0, aim, parent=r)
    light((-6, -9, 3), 500, '9AB8E8', 5.0, aim, parent=r)
    return dict(sock=sock, tower=tower, tfl=tfl, minis=minis, hsun=sun)


def set_cloud(r):
    lumps = []
    cols = ('2A3348', '39445C', '1E2536', '46526C')
    for i in range(60):
        a = i * 2.399
        rad = 7 + (i * 5 % 9)
        d = 27 + rad + (i * 17 % 30)
        z = -150 + (i * 37 % 300)
        o = add('ico_sphere', cols[i % 4], (math.cos(a) * d, math.sin(a) * d, z), scale=(1, 1, 0.75), radius=rad, subdivisions=1, parent=r, emit=0.7)
        lumps.append((o, z))
    add('circle', '9A8A50', (0, 0, -330), radius=46, vertices=16, fill_type='NGON', parent=r, emit=0.4)
    for i in range(5):
        add('cube', ('7C8A3E', 'B8A050', '6E7C36')[i % 3], (-24 + i * 11, math.sin(i * 2) * 16, -329), rot=(0, 0, i * 0.5), scale=(12, 9, 0.2), size=1, parent=r, emit=0.4)
    bolt = empty((0, 0, -400), r)
    pts = ((0, 0, 30), (2.2, 0, 22), (-1.4, 0, 15), (1.6, 0, 8), (-2.0, 0, 0), (0.6, 0, -9), (-1.2, 0, -18), (1.0, 0, -30))
    for p0, p1 in zip(pts, pts[1:]):
        rod(p0, p1, 0.32, 'F0F6FF', bolt, emit=40)
    rod(pts[3], (6.5, 0, 1), 0.2, 'F0F6FF', bolt, emit=40)
    bl = light((0, -2, 0), 0, 'CFE0FF', kind='POINT', parent=bolt)
    aim = empty((0, 0, 3), r)
    key = light((-10, -14, 26), 26000, 'A8C0F8', 10.0, aim, parent=r)
    light((13, -15, -5), 5000, '6A7CB0', 8.0, aim, parent=r)
    light((8, 9, 7), 3500, 'FF7A1A', 4.0, aim, parent=r)
    fl = light((-30, -40, 60), 0.0, 'DCE8FF', kind='SUN', target=aim, parent=r)
    return dict(lumps=lumps, bolt=bolt, boltl=bl, cflash=fl, ckey=key)


def set_high(r):
    for i in range(80):
        a = i * 2.399
        d = 13 + (i * 13 % 170)
        add('ico_sphere', ('8FA3C8', 'A9B8D8', '7688B0')[i % 3], (math.cos(a) * d, math.sin(a) * d, -4 - (i % 5)), scale=(1, 1, 0.45), radius=9 + (i * 7 % 12),
            subdivisions=1, parent=r)
    add('circle', '5A6C98', (0, 0, -9), radius=520, vertices=24, fill_type='NGON', parent=r)
    for i in range(80):
        az, el = i * 2.399, 0.06 + ((i * 0.618) % 1) * 1.35
        add('ico_sphere', 'FFFFFF', (math.cos(az) * math.cos(el) * 340, math.sin(az) * math.cos(el) * 340, math.sin(el) * 340), radius=0.7 + (i % 3) * 0.35,
            subdivisions=1, parent=r, emit=10)
    add('circle', 'FFC878', (150, 470, 4), rot=(PI / 2, 0, 0), radius=26, vertices=20, fill_type='NGON', parent=r, emit=7)
    aim = empty((0, 0, 4), r)
    light((60, 190, 16), 3.2, 'FFC890', kind='SUN', target=aim, parent=r)
    light((-18, -28, 22), 30000, '7A9AF0', 16.0, aim, parent=r)
    light((10, -14, -2), 2500, '9AB0E8', 8.0, aim, parent=r)
    return {}


def set_field(r):
    add('plane', 'C8A850', (0, 0, 0), size=1400, parent=r)
    for i in range(-14, 15):
        add('cube', 'B0903C', (i * 4.2, 40, 0.02), scale=(0.6, 420, 0.04), size=1, parent=r)
    add('cube', '9A7A50', (-15, 60, 0.03), rot=(0, 0, 0.12), scale=(5.5, 520, 0.05), size=1, parent=r)
    for i in range(-16, 17):
        add('cylinder', '6A5238', (i * 3, 9, 0.7), radius=0.09, depth=1.4, vertices=5, parent=r)
    for z in (0.5, 1.1):
        add('cylinder', 'B8BCC8', (0, 9, z), rot=(0, PI / 2, 0), radius=0.02, depth=98, vertices=4, parent=r)
    base = (8, 17, 0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod((base[0] + sx * 1.3, base[1] + sy * 1.3, 0), (base[0] + sx * 0.25, base[1] + sy * 0.25, 9), 0.07, '8A90A6', r)
    for z, w in ((3, 1.9), (6, 1.2)):
        for sy in (-1, 1):
            add('cube', '8A90A6', (base[0], base[1] + sy * w / 2, z), scale=(w, 0.07, 0.07), size=1, parent=r)
        for sx in (-1, 1):
            add('cube', '8A90A6', (base[0] + sx * w / 2, base[1], z), scale=(0.07, w, 0.07), size=1, parent=r)
    mill = empty((8, 16.4, 9.3), r)
    add('cylinder', '6A7088', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.25, depth=0.3, vertices=8, parent=mill)
    for i in range(10):
        a = i * PI / 5
        add('cube', 'C8CCD8', (math.cos(a) * 1.25, 0, math.sin(a) * 1.25), rot=(0.35, -a, 0), scale=(1.6, 0.04, 0.42), size=1, parent=mill)
    add('cube', 'D8324A', (8, 18.6, 9.3), scale=(0.06, 1.6, 0.9), size=1, parent=r)
    add('cylinder', 'A8B0B8', (13, 19, 1.5), radius=2.3, depth=3.0, vertices=12, parent=r)
    add('cone', '8A929C', (13, 19, 3.3), radius1=2.4, radius2=0.2, depth=0.6, vertices=12, parent=r)
    for i in range(18):
        add('ico_sphere', ('4E6034', '5E7040')[i % 2], (-230 + i * 27, 190 + (i % 3) * 22, 7), scale=(1, 1, 0.8), radius=10 + i % 4, subdivisions=1, parent=r)
    far = empty((-150, 560, 0), r)
    for i in range(10):
        add('ico_sphere', ('59647E', '6E7892', '8791AA', 'A3ACC2', 'D4DAE8')[i // 2], (math.sin(i * 2) * 26, 0, 28 + i * 15), radius=40 - i, subdivisions=2, parent=far,
            emit=0.05 + 0.03 * i)
    for i in range(9):
        add('ico_sphere', 'E4E8F2', (-120 + i * 30, 0, 182), scale=(1, 1, 0.36), radius=34, subdivisions=2, parent=far, emit=0.3)
    aim = empty((0, 0, 2), r)
    sun = light((-60, -50, 34), 4.2, 'FFD9A0', kind='SUN', target=aim, parent=r)
    light((7, 7, 5), 2400, 'FF7A1A', 3.0, aim, parent=r)
    light((-6, -9, 3), 400, '9AB8E8', 5.0, aim, parent=r)
    biner = add('torus', 'E8ECF4', (0, 0, -6), major_radius=0.11, minor_radius=0.028, major_segments=10, minor_segments=5, parent=None, rough=0.2, emit=0.9)
    biner.scale = (1, 1.5, 1)
    return dict(mill=mill, biner=biner, fsun=sun)


# ---------------------------------------------------------------- build / reset / finish
def build():
    sc = bpy.context.scene
    S = dict(colls={})
    for name, fn in (('hill', set_hill), ('cloud', set_cloud), ('high', set_high), ('field', set_field)):
        S['colls'][name], out = group(name, fn)
        S.update(out)
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['icicle'] = add('cone', 'DFF4FF', (0, -0.78, -0.3), rot=(PI, 0, 0), radius1=0.06, radius2=0.0, depth=0.42, vertices=4, parent=S['rook'].head, emit=0.6)
    S['ewa'] = K.Rig(EWA, ewa_head)
    S['gl'] = empty()
    S['wing'], wice = make_glider(S['gl'])
    body = S['ewa'].body
    S['ice'] = wice + S['ewa'].extra['ice'] + [add('ico_sphere', 'DFF4FF', p, radius=r_, subdivisions=1, parent=body, emit=0.5) for p, r_ in (
        ((0.4, -0.05, 1.14), 0.11), ((-0.38, 0.02, 1.15), 0.12), ((0.1, -0.33, 0.7), 0.08), ((-0.15, -0.36, 0.35), 0.07), ((0.2, -0.3, 0.1), 0.07))]
    S['hand_e'] = K.Hand('20242B', 'C83248', 1.0)
    S['toggle'] = tg = empty()
    add('cube', 'FF7A1A', (0, 0, 0), scale=(0.6, 0.1, 0.1), size=1, parent=tg, emit=0.4)
    add('cylinder', 'B8BCC8', (0, 0, 2.5), radius=0.02, depth=5, vertices=4, parent=tg)
    S['brolly'] = empty()
    S['brcan'], S['brice'] = make_brolly(S['brolly'])
    S['hail'] = [add('ico_sphere', 'E8F4FF', FAR, radius=0.13, subdivisions=1, emit=0.8) for _ in range(40)]
    S['fea'] = [add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4) for _ in range(9)]
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 1400
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
    S['ewa'].root.parent = None
    for who in ('rook', 'ewa'):
        S[who].place(FAR)
        S[who].apply(P())
        S[who].root.scale = (1, 1, 1)
    S['gl'].location, S['gl'].rotation_euler, S['gl'].scale = FAR, (0, 0, 0), (1, 1, 1)
    S['wing'].rotation_euler, S['wing'].scale, S['wing'].location = (0, 0, 0), (1, 1, 1), (0, 0, 0)
    S['hand_e'].place(FAR)
    S['hand_e'].grip(0.2)
    S['hand_e'].root.scale = (1, 1, 1)
    for o in S['hail'] + S['fea'] + [S['toggle'], S['brolly'], S['biner']]:
        o.location = FAR
        o.scale = (1, 1, 1)
        o.rotation_euler = (0, 0, 0)
    S['biner'].scale = (1, 1.5, 1)
    S['brcan'].scale = (1, 1, 1)
    for g in S['minis']:
        g.location = (0, 0, -60)
    S['bolt'].location = (0, 0, -400)
    S['boltl'].data.energy = 0
    S['cflash'].data.energy = 0
    S['ckey'].data.energy = 26000
    S['tfl'].hide_render = True
    S['tower'].scale = (1, 1, 1)
    S['tower'].location = (60, 300, -9)
    S['sock'].rotation_euler = (0, 1.25, 0)
    S['hsun'].data.energy, S['hsun'].data.color = 4.0, K.hexc('FFE2B0')[:3]
    S['fsun'].data.energy = 4.2
    S['mill'].rotation_euler = (0, 0, 0)
    S['face'] = dict(rook='calm', ewa='calm')
    S['hat_tip'], S['hat_off'], S['iced'], S['frost'], S['brfrost'] = 0.0, False, False, False, False
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
        r['hat'].location, r['hat'].rotation_euler = (0.1, -0.52, -1.12), (0.75, 0.0, 0.2)
    else:
        r['hat'].location = (0, 0, 0.27 + (0.13 if e == 'shocked' else 0.0) + tip * 0.1)
        r['hat'].rotation_euler = (-0.2 + dict(smirk=0.2, deadpan=0.12).get(e, 0.0) + tip * 0.35, 0.07, 0)
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e in ('shocked', 'laugh') else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    S['icicle'].hide_render = not S['frost']
    for o in S['brice']:
        o.hide_render = not S['brfrost']
    for o in S['ice']:
        o.hide_render = not S['iced']
    k = dict(scared=1.25, shock=1.8, calm=1.0, sad=0.6, happy=0.9, closed=0.1).get(S['face']['ewa'], 1.0)
    for ey in S['ewa'].extra['eyes']:
        ey.scale = (ey.scale[0], ey.scale[1], 0.075 * k)


# ---------------------------------------------------------------- helpers
BRAKE = dict(aL=(2.55, 0.35, 0.55), aR=(2.55, 0.35, 0.55), lL=(1.3, 1.2), lR=(1.3, 1.2), lift=-0.5, lean=0.12)
SLUMP = dict(aL=(0.25, 0.25, 0.25), aR=(0.2, 0.3, 0.3), lL=(1.2, 1.35), lR=(1.3, 1.25), lift=-0.5, lean=0.3, head=(0.6, 0.35))


def fly(S, loc, yaw=0.0, pitch=0.0, roll=0.0, pose=None, face='scared', iced=False):
    S['gl'].location, S['gl'].rotation_euler = loc, (pitch, roll, yaw)
    S['ewa'].root.parent = S['gl']
    S['ewa'].place((0, 0.12, -0.55))
    S['ewa'].apply(pose or P('stand', head=(-0.15, 0.0), **BRAKE))
    S['face']['ewa'] = face
    S['iced'] = iced


def clouds(S, t, speed, col='141A28', strength=1.0):
    """Inside the storm: the cloud walls scroll down (speed > 0 = she is rising)."""
    A = show(S, 'cloud')
    for o, z in S['lumps']:
        o.location.z = ((z - speed * t + 150) % 300) - 150
    sky(S, col, strength)
    return A


def hail(S, org, t, n=24, box=(9, 6, 12), speed=26, slant=0.35, size=1.0, start=0):
    for i in range(n):
        b = S['hail'][start + i]
        u = ((i * 0.618) % 1 - t * speed / box[2]) % 1
        x = ((i * 0.37) % 1 - 0.5) * box[0] + (1 - u) * slant * box[2] * 0.3
        b.location = (org[0] + x, org[1] + ((i * 0.73) % 1 - 0.5) * box[1], org[2] + (u - 0.5) * box[2])
        s = size * (0.7 + ((i * 0.29) % 1))
        b.scale = (s, s, s)


def puffs(S, org, k, n=16, r=5.0, size=9.0, start=0):
    for i in range(n):
        b = S['hail'][start + i]
        a, e = i * 2.4, ((i * 0.61) % 1) * 0.9 + 0.1
        d = r * (0.4 + 0.6 * ((i * 0.37) % 1)) * (1 - (1 - k) ** 2)
        b.location = (org[0] + math.cos(a) * math.cos(e) * d, org[1] + math.sin(a) * math.cos(e) * d * 0.6, org[2] + math.sin(e) * d * 0.7 - 1.5 * k * k)
        s = size * (0.6 + ((i * 0.73) % 1)) * (1 - 0.55 * k)
        b.scale = (s, s, s)


def feathers(S, org, t, n=6, down=True):
    for i in range(n):
        f = S['fea'][i]
        u = (t * 0.6 + i * 0.37) % 1
        a = i * 2.3
        f.location = (org[0] + math.cos(a) * (0.5 + u), org[1] - 0.5 + math.sin(a) * 0.4, org[2] + (-u * 3.0 if down else u * 2.0) + 0.2 * math.sin(t * 2 + i))
        f.rotation_euler = (t * 1.3 + i, t * 0.9 + i * 2, i)


def brolly_rook(S, loc, yaw, t, expr='shocked', inverted=True, frost=False, pose=None, kick=6.0, tilt=0.0):
    bob = 0.12 * math.sin(t * 2.3)
    loc = (loc[0], loc[1], loc[2] + bob)
    S['rook'].place(loc, yaw, 0.06 * math.sin(t * 1.7), tilt + 0.07 * math.sin(t * 1.3))
    kk = math.sin(t * kick)
    S['rook'].apply(pose or P('reach', aL=(0.5, 0.9 + 0.2 * kk, 0.6), lL=(0.35 * kk, 0.3 + 0.2 * kk), lR=(-0.35 * kk, 0.3 - 0.2 * kk), head=(-0.2, 0.2)))
    S['brolly'].location = off(loc, yaw, (0.47, -0.2, 2.9))
    S['brolly'].rotation_euler = (0.05 * math.sin(t * 3.1), tilt + 0.06 * math.sin(t * 2.7), yaw)
    S['brcan'].scale = (1, 1, -1 if inverted else 1)
    S['face']['rook'] = expr
    S['frost'], S['brfrost'] = frost, frost


def minis(S, t, spots):
    for g, (x, y, z, ph) in zip(S['minis'], spots):
        g.location = (x + 3.0 * math.sin(t * 0.5 + ph), y + 2.5 * math.cos(t * 0.4 + ph), z + 0.8 * math.sin(t * 0.9 + ph))
        g.rotation_euler = (0, 0.2 * math.sin(t * 0.7 + ph), ph + 0.25 * t)


def hill(S, tower=1.0, sock=1.25, t=0.0, col='B9C6D4', strength=1.0):
    A = show(S, 'hill')
    sky(S, col, strength)
    S['tower'].scale = (tower, tower, tower)
    S['sock'].rotation_euler = (0, sock + (0.08 * math.sin(t * 13) if sock < 0.6 else 0.03 * math.sin(t * 2)), 0.3 + (0.1 * math.sin(t * 9) if sock < 0.6 else 0))
    return A


def flash(lt, at_, d=0.22):
    if not 0 <= lt - at_ < d:
        return 0.0
    f = 1 - (lt - at_) / d
    return f if int((lt - at_) * 30) % 3 != 1 else f * 0.3


# ---------------------------------------------------------------- shots: hook
def suck_up(S, k, t, lt):
    f = flash(lt, 0.0, 0.3)
    A = clouds(S, t, 70, lerp_col('141A28', 'AEC4F0', f), 1 + 3 * f)
    S['cflash'].data.energy = 9 * f
    z = lerp(-9, 2.5, ease(k))
    fly(S, A(0.4 * math.sin(t * 9), 0, z), 0.5 + 0.2 * math.sin(t * 5), 0.25 * math.sin(t * 7), 0.3 * math.sin(t * 6),
        P('stand', head=(-0.4, 0.2 * math.sin(t * 8)), **{**BRAKE, 'aL': (2.7, 0.5, 0.3), 'aR': (2.3, 0.6, 0.8)}), 'shock')
    hail(S, A(0, -2, z + 4), t, 30, (14, 8, 18), 60)
    cam(S, A(6.5, -13.5, -5), A(0, 0, lerp(-2, 6.5, k)), 26, 0.12 * math.sin(t * 6))


def ewa_fight(S, k, t, lt):
    A = clouds(S, t, 55)
    pull = math.sin(t * 9)
    fly(S, A(0.08 * math.sin(t * 31), 0, 0.06 * math.sin(t * 27)), 0.35, 0.1 * math.sin(t * 5), 0.14 * math.sin(t * 6),
        P('stand', head=(-0.25, 0.3 * math.sin(t * 4)), **{**BRAKE, 'aL': (2.2 + 0.5 * pull, 0.4, 0.9 - 0.5 * pull), 'aR': (2.2 - 0.5 * pull, 0.4, 0.9 + 0.5 * pull)}),
        'scared')
    hail(S, A(0, -1, 1.5), t, 26, (7, 4, 8), 34, size=0.8)
    cam(S, A(lerp(2.2, 1.7, k), lerp(-5.6, -4.6, k), 0.6), A(0, 0, 1.25), 48, 0.08 * math.sin(t * 5))


def blackout_cu(S, k, t, lt):
    late = bool(S['prm'].get('late'))
    A = clouds(S, t, 30 if not late else 6, '0E1320' if not late else '1A2236')
    e = ease(k * 1.5) if not late else 1.0
    pose = blend(P('stand', head=(-0.15, 0.1), **BRAKE), P('stand', **SLUMP), e)
    if late:
        pose['head'] = (0.6 + 0.04 * math.sin(t * 1.5), 0.35)
    fly(S, A(0, 0, 0.1 * math.sin(t * 2)), 0.3 if not late else -0.45, 0.05 * math.sin(t * 1.3), 0.1 * math.sin(t * 1.1), pose, 'scared' if e < 0.45 else 'closed', late)
    if late:
        cam(S, A(lerp(-2.6, -2.0, k), lerp(-4.4, -3.9, k), 0.5), A(0, 0, 1.2), 50, -0.05)
    else:
        cam(S, A(lerp(1.5, 1.2, k), lerp(-3.7, -3.1, k), lerp(1.2, 0.75, k)), A(0, -0.1, 1.2), 52, 0.05)
    hail(S, A(0, -0.5, 1.5), t, 14, (6, 4, 7), 9 if late else 22, size=0.6)


# ---------------------------------------------------------------- shots: doubt + launch (the hill)
def rook_hill(S, k, t, lt):
    A = hill(S, 0.9, 0.9, t)
    S['rook'].place(A(0, 0, 0), -0.25)
    S['rook'].apply(P('cross', head=(0.05, 0.1 + 0.24 * math.sin(t * 4.2) * max(0, 1 - lt / 1.0))))
    S['face']['rook'] = 'deadpan'
    minis(S, t, ((-2, 60, 17, 0), (22, 90, 24, 2), (-6, 120, 30, 4)))
    cam(S, A(lerp(-1.5, -1.1, k), lerp(-7.2, -5.6, k), 2.0), A(0.05, 0, 2.05), 40)


def rook_collar(S, k, t, lt):
    A = hill(S, 0.95, 0.7, t)
    x = lerp(0.2, 4.6, ease((k - 0.25) / 0.75))
    pop = math.sin(PI * ease(lt / 0.5)) if lt < 0.5 else 0.0
    S['rook'].place(A(x, -0.3, 0), PI / 2 - 0.25)
    S['rook'].apply(blend(walk(t, 1.9) if k > 0.25 else P('stand'), P('stand', aL=(0.7, 0.35, 2.3, 0.8), aR=(0.7, 0.35, 2.3, 0.8), head=(-0.1, 0)), pop))
    S['face']['rook'] = 'smirk'
    cam(S, A(lerp(4.6, 6.2, k), -7.4, 1.5), A(lerp(1.0, 4.0, k), 0, 2.0), 36)


def hill_wide(S, k, t, lt):
    A = hill(S, 0.72, 1.05, t)
    minis(S, t, ((-6, 34, 15, 0), (12, 52, 24, 1.3), (-20, 70, 19, 2.6), (26, 86, 30, 3.9), (4, 110, 36, 5.2), (-30, 130, 28, 0.7)))
    S['ewa'].place(A(6.5, 1.2, 0), PI / 2)
    S['ewa'].apply(P('hips'))
    cam(S, A(lerp(-9, -7, k), lerp(-30, -26, k), lerp(10.5, 9.0, k)), A(9, 30, 8.5), 28)


def ewa_ready(S, k, t, lt):
    A = hill(S, 0.8, 0.8, t)
    e = ease(k * 1.15)
    S['gl'].location, S['gl'].rotation_euler = A(7.2, 1.0, 1.0), (lerp(1.25, 0.05, e), 0, PI / 2)
    S['ewa'].place(A(7.2, 1.0, 0), PI / 2)
    S['ewa'].apply(P('stand', aL=(lerp(1.0, 2.5, e), 0.4, 0.5), aR=(lerp(1.0, 2.5, e), 0.4, 0.5), lL=(0.35, 0.1), lR=(-0.3, 0.3), lean=lerp(0.3, 0.12, e), head=(-0.1, -0.5)))
    S['face']['ewa'] = 'calm'
    cam(S, A(lerp(19, 17.5, k), lerp(-13, -12, k), 1.3), A(6.6, 1.0, lerp(4.2, 5.2, k)), 22)


def takeoff(S, k, t, lt):
    A = hill(S, 0.9, 0.5, t)
    e = ease(k)
    x = lerp(6.5, 19, e)
    up = max(0.0, (x - 12.5) / 6.5)
    z = 1.9 * up * up - 0.75 * min(1.0, max(0.0, (x - 13.2) / 3.0)) * (1 - up)
    if up < 0.15:
        S['gl'].location, S['gl'].rotation_euler = A(x, 1.0, 1.0 + z), (0.05, 0, PI / 2)
        S['ewa'].place(A(x, 1.0, z), PI / 2)
        w = walk(t, 2.6)
        w.update(aL=(2.5, 0.4, 0.5, 0), aR=(2.5, 0.4, 0.5, 0), lean=0.3)
        S['ewa'].apply(w)
    else:
        fly(S, A(x, 1.0, 0.55 + z), PI / 2, -0.06, 0.05 * math.sin(t * 3), None, 'happy')
    S['rook'].place(A(4.6, -2.4, 0), PI - 0.75)
    S['rook'].apply(P('stand', aL=(0.2, 1.9, 1.6, -1.5), aR=(0.1, 0.25, 0.3), head=(-0.2 - 0.15 * up, lerp(-0.5, 0.35, e))))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(1.5, 2.6, k), -12.5, 2.1), A(lerp(7.5, 11.5, k), 1, lerp(3.6, 4.8, k)), 26)


def storm_build(S, k, t, lt):
    A = hill(S, lerp(0.8, 1.2, ease(k)), 0.45, t, lerp_col('B9C6D4', '8E9CB0', k))
    f = flash(lt, 0.75, 0.2)
    S['tfl'].hide_render = f < 0.05
    S['rook'].place(A(-1.2, 0.5, 0), PI + 0.55)
    S['rook'].apply(blend(P('stand', head=(-0.2, 0)), P('point', aR=(2.1, 0.2, 0.1), head=(-0.45, -0.1)), lt / 0.35))
    S['face']['rook'] = 'calm'
    minis(S, t, ((30, 120, 34, 0), (-12, 150, 44, 2), (50, 170, 52, 4)))
    cam(S, A(lerp(-2.6, -2.2, k), lerp(-6.4, -5.4, k), 1.3), A(5, 40, lerp(14, 18, k)), 24)


def rook_sock(S, k, t, lt):
    snap = ease(lt / 0.35)
    A = hill(S, 1.15, lerp(1.25, 0.12, snap), t, '8E9CB0')
    S['rook'].place(A(-3.0, 2.2, 0), -0.55)
    late = ease((lt - 0.75) / 0.3)
    S['rook'].apply(P('stand', aL=(0.2, 1.9, 1.6, -1.5), aR=(0.1, 0.3, 0.4), head=(lerp(-0.45, 0.1, late), lerp(0.75, 0.0, late)), lean=0.06 * math.sin(t * 8)))
    S['face']['rook'] = 'calm' if late < 0.5 else 'deadpan'
    cam(S, A(lerp(-1.3, -1.6, k), lerp(-6.4, -5.6, k), 2.3), A(-3.6, 2.6, 3.5), 34, 0.03 * math.sin(t * 5))


# ---------------------------------------------------------------- shots: sucked in
def skirt(S, k, t, lt):
    A = hill(S, 1.3, 0.3, t, '8E9CB0')
    x = lerp(-14, 6, k)
    fly(S, A(x, 96, 46 + 1.2 * math.sin(t * 2)), PI / 2 + lerp(0.0, -0.9, ease(k)), 0, lerp(0.05, -0.5, ease(k)) + 0.08 * math.sin(t * 5), None, 'scared')
    cam(S, A(x - 5, lerp(70, 74, k), 44), A(x + 4, 110, 52), 30, 0.05 * math.sin(t * 3))


def cloud_mouth(S, k, t, lt):
    A = clouds(S, t, 26, lerp_col('3A4660', '0B0F1A', ease(k)))
    z = lerp(-3, 9, ease(k))
    fly(S, A(0.5 * math.sin(t * 4), 0, z), -0.4 + 0.5 * k, 0.12 * math.sin(t * 5), 0.25 * math.sin(t * 4), None, 'scared')
    S['ckey'].data.energy = lerp(40000, 14000, k)
    cam(S, A(4.5, -7.5, -13), A(0, 0, lerp(1, 7, k)), 24, 0.06 * math.sin(t * 4))


def spiral(S, k, t, lt):
    A = clouds(S, t, 46)
    a = t * 4.2
    fly(S, A(3.4 * math.cos(a), 3.4 * math.sin(a), 0), a + PI, 0.25, 0.95, P('stand', head=(0.1, -0.5), **{**BRAKE, 'aR': (1.5, 0.3, 1.2)}), 'scared')
    brolly_rook(S, A(-3.5 + 1.2 * math.cos(a * 0.4), -7.0 + 1.2 * math.sin(a * 0.4), 2.5), a * 0.4 + 0.3, t, tilt=0.5)
    cam(S, A(1.5, -9.5, 19), A(0, -1.5, -0.5), 24, 0.25 * math.sin(t * 2))


def rook_brolly(S, k, t, lt):
    A = clouds(S, t, 62)
    brolly_rook(S, A(0.15 * math.sin(t * 11), 0, 0), 0.25, t, 'shocked')
    feathers(S, A(0, 0, 1.2), t, 7)
    hail(S, A(0, 0, 2), t, 20, (8, 5, 10), 40, size=0.7)
    cam(S, A(lerp(2.0, 1.5, k), lerp(-7.8, -6.6, k), 0.4), A(0.25, 0, 2.7), 34, 0.07 * math.sin(t * 4))


# ---------------------------------------------------------------- shots: the climb
def rise_tower(S, k, t, lt):
    A = clouds(S, t, 80, '1A2236')
    z = lerp(-14, 5, ease(k))
    fly(S, A(0.6 * math.sin(t * 5), 0.5 * math.cos(t * 4), z), 0.6 + 0.3 * math.sin(t * 3), 0.15 * math.sin(t * 6), 0.3 * math.sin(t * 5),
        P('stand', head=(-0.6, 0.2), **BRAKE), 'shock')
    cam(S, A(6.5, -9.5, 19), A(0, 0, z + 4), 26, 0.1 * math.sin(t * 3))


def top_out(S, k, t, lt):
    A = show(S, 'high')
    sky(S, '080C26', 1.0)
    e = ease(k * 1.2)
    z = lerp(-9, 5.5, e)
    fly(S, A(0, 0, z), 0.45, lerp(-0.25, 0.0, e), 0.1 * math.sin(t * 5), P('stand', head=(-0.5, 0.3), **BRAKE), 'shock', True)
    puffs(S, A(0, 0, -2), min(1, lt / 0.9), 16, 9, 22)
    puffs(S, A(4.6, -5, -2), min(1, max(0, lt - 0.2) / 0.8), 10, 4, 9, start=16)
    brolly_rook(S, A(4.6, -5, lerp(-10, 1.0, ease(k * 1.5 - 0.15))), -0.4, t, 'shocked', True, True)
    cam(S, A(lerp(6, 5, k), lerp(-27, -24, k), 2.5), A(1.5, 0, 6.0), 26)


def hail_(S, k, t, lt):
    A = clouds(S, t, 40)
    duck = ease(lt / 0.3)
    fly(S, A(0.1 * math.sin(t * 30), 0, 0.08 * math.sin(t * 26)), -0.75, 0.08 * math.sin(t * 7), 0.2 * math.sin(t * 6),
        P('stand', head=(lerp(-0.1, 0.55, duck), 0.2), **{**BRAKE, 'aL': (2.4, 0.2, 1.5), 'aR': (2.4, 0.2, 1.5)}), 'scared', True)
    hail(S, A(0, -1.5, 3), t, 40, (12, 5, 14), 48, 0.6, 2.2)
    cam(S, A(lerp(-4.2, -3.6, k), lerp(-8.5, -7.6, k), 0.2), A(0.3, 0, 3.4), 30, -0.08 + 0.05 * math.sin(t * 6))


def bolt(S, k, t, lt):
    f = max(flash(lt, 0.12, 0.3), flash(lt, 0.7, 0.25))
    A = clouds(S, t, 40, lerp_col('0B0F1A', 'B8CCF4', f), 1 + 4 * f)
    S['cflash'].data.energy = 12 * f
    if f > 0.03:
        S['bolt'].location = (7.5, 9, 4)
        S['bolt'].rotation_euler = (0, 0.12, 0.3 if lt < 0.5 else -0.6)
        S['boltl'].data.energy = 400000 * f
    fly(S, A(-3.2 + 0.2 * math.sin(t * 8), 0, -2.5 + lerp(0, 2.5, k)), 0.5, 0.2 * math.sin(t * 6), 0.35 * math.sin(t * 5), None, 'shock', True)
    cam(S, A(-1, -19.5, -6), A(1.5, 0, 4.5), 26, 0.1 * math.sin(t * 9))


def rook_ice(S, k, t, lt):
    A = clouds(S, t, 18, '26304A')
    j = 0.035 * math.sin(t * 46)
    brolly_rook(S, A(j, 0, 0), 0.2 + j, t, 'deadpan' if lt < 0.6 else 'shocked', False, True,
                P('reach', aL=(0.45, -0.1, 1.8, 1.2), lL=(0.1, 0.2), lR=(-0.1, 0.25), head=(0.1, 3 * j)), tilt=0.0)
    feathers(S, A(0, 0, 1.5), t, 5)
    hail(S, A(0, 0.5, 2), t, 12, (6, 4, 8), 10, size=0.5)
    cam(S, A(lerp(1.3, 1.0, k), lerp(-5.4, -4.6, k), 2.5), A(0.15, 0, 2.6), 46)


# ---------------------------------------------------------------- shots: out cold
def slump_wide(S, k, t, lt):
    A = show(S, 'high')
    sky(S, '080C26', 1.0)
    fly(S, A(lerp(-1.5, 1.0, k), 0, 6 + 0.5 * math.sin(t * 1.2)), -0.6 + 0.25 * k, 0.05 * math.sin(t * 1.1), 0.14 * math.sin(t * 0.9), P('stand', **SLUMP), 'closed', True)
    cam(S, A(lerp(-9.5, -7.5, k), lerp(-17, -15, k), 5.5), A(0, 0, 10.5), 30, 0.03)


def ghost_fly(S, k, t, lt):
    A = clouds(S, t, lerp(-16, 14, ease(k)), '1A2236')
    a = t * 1.1
    fly(S, A(3.0 * math.sin(a), 2.0 * math.sin(a * 2) * 0.5, 1.5 * math.sin(t * 1.7)), PI + 0.5 * math.cos(a), 0.06 * math.sin(t * 2), 0.4 * math.cos(a),
        P('stand', **SLUMP), 'closed', True)
    cam(S, A(lerp(-2, 2, k), -13.5, 8.5), A(0, 0, 4.2), 30, 0.05 * math.sin(t * 1.5))


def rook_watch(S, k, t, lt):
    A = clouds(S, t, 5, '1E2740')
    fly(S, A(-1.9, 0.3, 0.2 * math.sin(t * 1.4)), -0.55, 0.04 * math.sin(t * 1.2), 0.08 * math.sin(t * 1.0), P('stand', **SLUMP), 'closed', True)
    brolly_rook(S, A(1.7, 0.6, -0.7), 0.75, t, 'sad', False, True,
                P('reach', aL=(lerp(0.3, 1.2, ease(lt / 0.5)), 0.3, 0.5), lL=(0.1, 0.2), lR=(-0.1, 0.2), head=(0.1, 0.55)), kick=1.5)
    cam(S, A(lerp(0.9, 0.5, k), lerp(-9.6, -8.6, k), 1.4), A(0.2, 0.5, 2.3), 34)


# ---------------------------------------------------------------- shots: awake
def eyes_open(S, k, t, lt):
    A = clouds(S, t, -10, '2A3550')
    wake = ease((lt - 0.22) / 0.12)
    pose = blend(P('stand', **SLUMP), P('stand', **{**SLUMP, 'lean': 0.12, 'head': (-0.05, 0.0)}), wake)
    fly(S, A(0, 0, 0), 0.0, 0, 0.03 * math.sin(t * 2), pose, 'closed' if wake < 0.5 else 'shock', True)
    cam(S, A(lerp(0.5, 0.35, k), lerp(-2.6, -2.2, k), 1.35), A(0, -0.1, 1.38), 62, 0.04)
    hail(S, A(0, 0.6, 1.5), t, 10, (4, 2, 5), 5, size=0.4)


def ice_hands(S, k, t, lt):
    A = clouds(S, t, -12, '2A3550')
    g = ease(lt / 0.16)
    S['toggle'].location = A(0, 0, 1.5 - 0.5 * ease((lt - 0.2) / 0.3))
    S['hand_e'].place(A(0.02, lerp(0.7, 0.2, g), S['toggle'].location[2] - ORG['cloud'][2] - 0.02), (0.15, 0, 0))
    S['hand_e'].root.scale = (1.9, 1.9, 1.9)
    S['hand_e'].grip(0.1 + 0.85 * g)
    puffs(S, A(0, -0.1, 1.4), min(1, lt / 0.5), 14, 1.3, 0.7)
    cam(S, A(lerp(1.1, 0.8, k), lerp(-3.4, -2.8, k), 1.0), A(0, 0.1, 1.25), 50, 0.06)


def descend(S, k, t, lt):
    A = show(S, 'field')
    sky(S, 'E8C088', 1.0)
    z = lerp(30, 17, k)
    fly(S, A(lerp(-9, -3, k), 0, z), PI / 2 - 0.5, 0.05, 0.12 * math.sin(t * 2), P('stand', head=(0.3, 0.3), **BRAKE), 'scared', True)
    brolly_rook(S, A(lerp(-1, 3.5, k), 2, z + 2.5), -0.9, t, 'calm', False, True, P('reach', aL=(0.3, 0.5, 0.4), lL=(0.2, 0.3), lR=(-0.2, 0.3), head=(0.3, 0.5)), kick=2)
    S['mill'].rotation_euler = (0, t * 3, 0)
    cam(S, A(lerp(4, 6, k), -21, z + 4.5), A(-3, 3, z + 2), 26)


def landing(S, k, t, lt):
    A = show(S, 'field')
    sky(S, 'E8C088', 1.0)
    down = ease(k / 0.45)
    drop = ease((k - 0.45) / 0.4)
    x = lerp(-9, -1.5, ease(k * 1.3))
    z = lerp(3.2, 0, down)
    S['gl'].location, S['gl'].rotation_euler = A(x, 0.5, z + 1.0 - 0.45 * drop), (lerp(0.0, -1.35, drop), 0, PI / 2)
    S['wing'].scale = (1, 1, lerp(1, 0.75, drop))
    S['ewa'].place(A(x, 0.5, z - 0.45 * drop), PI / 2 - 0.5 * drop)
    run = walk(t, 2.2)
    run.update(aL=(2.4, 0.4, 0.6, 0), aR=(2.4, 0.4, 0.6, 0))
    S['ewa'].apply(blend(run, P('stand', aL=(0.5, 0.3, 0.6), aR=(0.5, 0.3, 0.6), lL=(0.9, 1.5), lR=(0.2, 1.3), lift=-0.42, lean=0.35, head=(0.3, 0)), drop))
    S['face']['ewa'], S['iced'] = 'shock', True
    rz = lerp(5, 0, ease(k / 0.6))
    if rz > 0.05:
        brolly_rook(S, A(3.2, 2.6, rz), -0.9, t, 'calm', False, True, P('reach', aL=(0.3, 0.5, 0.4), lL=(0.2, 0.3), lR=(-0.2, 0.3), head=(0.25, 0.5)), kick=2)
    else:
        rx = lerp(3.2, 1.6, ease((k - 0.6) / 0.4))
        S['rook'].place(A(rx, 2.6 - (3.2 - rx) * 0.8, 0), -1.1)
        S['rook'].apply(walk(t, 2.4))
        S['face']['rook'] = 'shocked'
    S['mill'].rotation_euler = (0, t * 3, 0)
    cam(S, A(lerp(3.5, 2.2, k), lerp(-12.5, -11, k), 1.2), A(-1.5, 1, lerp(4.0, 2.6, k)), 26)


# ---------------------------------------------------------------- shots: the one who did not come back, and the end
def dusk(S, t):
    A = hill(S, 0.001, 1.3, t, '4A3E5C', 0.8)
    S['tower'].location = (60, 300, -600)
    S['hsun'].data.energy, S['hsun'].data.color = 1.6, K.hexc('FF9A5A')[:3]
    return A


def dusk_hill(S, k, t, lt):
    A = dusk(S, t)
    S['rook'].place(A(-1.8, 3.2, 0), PI + 0.35)
    S['rook'].apply(P('stand', head=(lerp(-0.25, 0.3, ease(k)), 0)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(1.5, 0.8, k), lerp(-10.5, -9.2, k), 2.6), A(-3.2, 3, 3.6), 32)


def rook_hat(S, k, t, lt):
    A = dusk(S, t)
    S['rook'].place(A(0, 0, 0), 0.35)
    S['rook'].apply(P('stand', aR=(0.75, -0.15, 2.1, 1.0), head=(lerp(0.15, 0.38, ease(k)), -0.1)))
    S['face']['rook'], S['hat_off'] = 'sad', True
    cam(S, A(lerp(1.6, 1.3, k), lerp(-5.6, -4.8, k), 2.2), A(0.0, 0, 2.05), 46)


def ewa_field(S, k, t, lt):
    A = show(S, 'field')
    sky(S, 'E8C088', 1.0)
    S['gl'].location, S['gl'].rotation_euler, S['gl'].scale = A(-5.5, 4.2, 0.5), (-1.45, 0, 0.9), (1, 1, 0.55)
    S['ewa'].place(A(-1.2, 0.4, 0), 0.5)
    wave = ease((lt - 0.5) / 0.3)
    S['ewa'].apply(blend(P('cross', head=(0.1, -0.4)), P('stand', aL=(0.5, -0.05, 1.7, 1.3), aR=(2.3, 0.5, 0.6 + 0.3 * math.sin(t * 9)), head=(0, -0.45)), wave))
    S['face']['ewa'], S['iced'] = 'happy', lt < 0.5
    S['rook'].place(A(1.5, 0.0, 0), -0.7)
    tip = math.sin(PI * ease((lt - 0.3) / 0.9)) if lt > 0.3 else 0
    S['rook'].apply(blend(P('stand', head=(0, 0.2)), P('hat', head=(0.2, 0.2)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'warm'
    S['mill'].rotation_euler = (0, t * 2.5, 0)
    cam(S, A(lerp(0.9, 0.4, k), lerp(-8.2, -7.0, k), 1.8), A(0.1, 0.3, 1.95), 36)


def signoff(S, k, t, lt):
    A = show(S, 'field')
    sky(S, 'E8C088', 1.0)
    S['rook'].place(A(0, 0, 0), 0.15)
    tip = math.sin(PI * ease(lt / 0.8)) if lt < 0.8 else 0
    S['rook'].apply(blend(P('stand', aL=(0.9, 0.25, 1.2), head=(0.05, 0)), P('hat', aL=(0.9, 0.25, 1.2), head=(0.22, 0)), tip))
    S['hat_tip'] = tip
    S['face']['rook'] = 'smirk'
    c = max(0.0, min(1.0, (lt - 0.25) / 0.9))
    S['biner'].location = A(-0.75 - 0.25 * c, -0.75, 1.75 + 2.6 * math.sin(c * PI))
    S['biner'].rotation_euler = (t * 22, t * 9, 0)
    S['mill'].rotation_euler = (0, t * 2.5, 0)
    cam(S, A(lerp(1.1, 0.8, k), lerp(-6.4, -5.2, k), 1.0), A(0, 0, 2.05), 38)


# ---------------------------------------------------------------- photographs for the case board
def photo_storm(S, k, t, lt):
    A = hill(S, 1.2, 0.3, 0.0, '8E9CB0')
    minis(S, 0.0, ((20, 110, 40, 0), (-16, 140, 50, 2)))
    cam(S, A(-6, -30, 6), A(40, 200, 80), 30)


def photo_ewa(S, k, t, lt):
    A = show(S, 'field')
    sky(S, 'E8C088', 1.0)
    S['ewa'].place(A(0, 0, 0), 0.25)
    S['ewa'].apply(P('stand', head=(0, 0.1)))
    S['face']['ewa'] = 'happy'
    cam(S, A(0.6, -3.2, 2.5), A(0, 0, 2.3), 60)


SHOTS3D = {f.__name__.rstrip('_'): f for f in (
    suck_up, ewa_fight, blackout_cu, rook_hill, rook_collar, hill_wide, ewa_ready, takeoff, storm_build, rook_sock, skirt, cloud_mouth,
    spiral, rook_brolly, rise_tower, top_out, hail_, bolt, rook_ice, slump_wide, ghost_fly, rook_watch, eyes_open, ice_hands, descend,
    landing, dusk_hill, rook_hat, ewa_field, signoff)}
STILLS = dict(storm=photo_storm, ewa=photo_ewa)
