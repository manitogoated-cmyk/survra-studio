"""Reddit File 001 in 3D - the suitcase on the running trail (a Reddit user's account, not verified).
One set built for this story only: a pine forest with a winding dirt trail, a clearing of tall grass with an
oxblood suitcase, the trailhead sign, and the night dressing for the search (police car, tape, torches)."""
import math

import bpy

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
FAR = (0, 0, -900)
HOST = {'rook_sign', 'runner_jog', 'suitcase_wide', 'rook_crouch', 'case_between', 'rook_lean', 'runner_flee', 'cops_search',
        'runner_points', 'rook_cam', 'rook_tag', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
RUN = dict(top='D8F23A', pants='1E2430', hand='C99A7A', boot='F4F4F4')
MAN = dict(top='39473A', pants='4A3E30', hand='A8846A', boot='1E1610')
COP = dict(top='1E2A4A', pants='141C30', hand='C68A5E', boot='0E0E12')
SUIT, R0, M0 = (5.2, 3.5), (2.2, 1.6), (3.7, 2.6)
PEEK = (-2.4, -0.4)                # the tree Rook hides behind
PEOPLE = ('runner', 'man', 'cop1', 'cop2')


def px(y):
    """x of the trail's centre line at y."""
    return 6 * math.sin(y / 14)


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rnd(i, salt=0):
    x = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - math.floor(x)


def yaw_to(a, b):
    """Yaw that turns a rig standing at a to face b (rigs face -Y at yaw 0)."""
    return math.atan2(b[0] - a[0], -(b[1] - a[1]))


def at(p, z=0.0, dx=0.0, dy=0.0):
    return (p[0] + dx, p[1] + dy, z)


# ---------------------------------------------------------------- the forest
def tree(r, x, y, i):
    h = 14 + 9 * rnd(i, 3)
    add('cylinder', ('3A2C22', '33271F', '41322A')[i % 3], (x, y, h / 2), radius=0.32 + 0.3 * rnd(i, 4), depth=h, vertices=6, parent=r)
    cr = 2.6 + 1.2 * rnd(i, 5)
    for j in range(2):
        add('cone', ('1F3A2A', '24452F', '1A3024')[(i + j) % 3], (x, y, h * (0.62 + 0.3 * j)), radius1=cr * (1 - 0.3 * j), radius2=0,
            depth=h * 0.55, vertices=7, parent=r)
    for j in range(2):                                                                                         # dead lower branches
        a = rnd(i, 6 + j) * 2 * PI
        add('cylinder', '33271F', (x + math.cos(a) * 0.7, y + math.sin(a) * 0.7, 3.2 + 2.2 * j + rnd(i, 8)), rot=(0, 1.2, a),
            radius=0.05, depth=1.5, vertices=4, parent=r)


def blade(parent, x, y, i, hmin=1.0, hmax=1.9):
    h = hmin + (hmax - hmin) * rnd(i, 13)
    add('cone', ('7C8A3A', '5E7A34', '94963F', '4E6A30')[i % 4], (x, y, h / 2), rot=((rnd(i, 14) - 0.5) * 0.5, (rnd(i, 15) - 0.5) * 0.5, 0),
        radius1=0.1, radius2=0.0, depth=h, vertices=4, parent=parent)


def set_woods(r):
    add('cube', '2A3A26', (0, 0, -0.06), scale=(500, 500, 0.1), size=1, parent=r, rough=1.0)
    for y in range(-78, 79, 2):                                                                               # the dirt trail
        slope = 6 / 14 * math.cos(y / 14)
        add('cube', ('6A5A44', '625340')[(y // 2) % 2], (px(y), y, 0.0), rot=(0, 0, -math.atan(slope)), scale=(3.3, 2.5, 0.06), size=1,
            parent=r, rough=1.0)
    n = 0
    for i in range(420):
        x, y = (rnd(i, 1) - 0.5) * 170, (rnd(i, 2) - 0.5) * 180
        if abs(x - px(y)) < 5.2 or math.hypot(x - SUIT[0], y - SUIT[1]) < 7.5 or math.hypot(x - 3.2, y + 52) < 6:
            continue
        tree(r, x, y, i)
        n += 1
        if n >= 150:
            break
    for i, (x, y) in enumerate(((9.8, 5.9), (11.2, 2.6), (8.6, 8.4), PEEK, (-4.8, 1.2), (9.4, -1.4))):
        tree(r, x, y, 900 + i)
    for i in range(60):                                                                                       # dark wall of forest far off
        a = i / 60 * 2 * PI
        d = 105 + 25 * rnd(i, 21)
        add('cone', '0F1C14', (math.cos(a) * d, math.sin(a) * d, 13), radius1=9, radius2=0, depth=26 + 10 * rnd(i, 22), vertices=6, parent=r)
    for i in range(200):                                                                                      # short grass along the trail
        y = -64 + 108 * rnd(i, 30)
        side = 1 if i % 2 else -1
        blade(r, px(y) + side * (2.3 + 3.4 * rnd(i, 31)), y, i, 0.5, 1.2)
    gnear = empty((SUIT[0], SUIT[1], 0), r)                                                                   # the tall grass around the case
    lane = math.atan2(R0[1] - SUIT[1], R0[0] - SUIT[0])
    for i in range(260):
        a, d = rnd(i, 40) * 2 * PI, 1.5 + 3.9 * rnd(i, 41) ** 0.8
        da = abs((a - lane + PI) % (2 * PI) - PI)
        if da < 0.45 and rnd(i, 42) < 0.8:
            continue
        blade(gnear, math.cos(a) * d, math.sin(a) * d, i + 300, 1.0, 1.9)
    # the suitcase: oxblood, dark straps, brass corners, lying on its long edge and leaning a little
    case = empty((SUIT[0], SUIT[1], 0), r, (0.1, 0, 0.5))
    add('cube', '7A2E2A', (0, 0, 0.68), scale=(2.0, 0.8, 1.3), size=1, parent=case, rough=0.55)
    for s in (-1, 1):
        add('cube', '2A1A16', (s * 0.55, 0, 0.68), scale=(0.13, 0.84, 1.34), size=1, parent=case)
        add('cube', 'D4A83A', (s * 0.55, -0.43, 0.95), scale=(0.16, 0.05, 0.12), size=1, parent=case, rough=0.25, emit=0.4)
        add('cylinder', '15120F', (s * 0.75, 0, 0.06), rot=(PI / 2, 0, 0), radius=0.12, depth=0.7, vertices=8, parent=case)
        add('cube', '2A1A16', (s * 0.28, 0, 1.42), scale=(0.07, 0.1, 0.2), size=1, parent=case)
        for sy in (-1, 1):
            for z in (0.1, 1.26):
                add('cube', 'D4A83A', (s * 0.94, sy * 0.36, z), scale=(0.14, 0.1, 0.14), size=1, parent=case, rough=0.25, emit=0.4)
    add('cube', '2A1A16', (0, 0, 1.52), scale=(0.66, 0.1, 0.07), size=1, parent=case)
    add('cube', 'D4A83A', (0.42, -0.44, 1.2), rot=(0, 0.3, 0), scale=(0.2, 0.02, 0.3), size=1, parent=case, rough=0.2, emit=0.8)   # luggage tag
    # the trailhead: a sign with a trail map, and a bench
    th = empty((3.2 + 2.6, -52, 0), r)
    for s in (-1, 1):
        add('cylinder', '4A3828', (s * 1.1, 0, 1.6), radius=0.1, depth=3.2, vertices=6, parent=th)
    add('cube', '5A4632', (0, 0, 2.5), scale=(2.6, 0.12, 1.5), size=1, parent=th)
    add('cube', 'E8DEC0', (0, -0.07, 2.5), scale=(2.3, 0.02, 1.25), size=1, parent=th, emit=0.5)
    for i in range(9):
        add('cube', 'FF7A1A', (-0.9 + i * 0.22, -0.09, 2.3 + 0.28 * math.sin(i * 0.9)), rot=(0, 0.6 * math.cos(i * 0.9), 0),
            scale=(0.24, 0.02, 0.05), size=1, parent=th, emit=1.5)
    add('cube', '2A2420', (0.9, -0.09, 2.85), scale=(0.3, 0.02, 0.12), size=1, parent=th)
    add('cube', '4A3828', (0, 0, 3.4), rot=(0, 0, 0), scale=(3.0, 0.5, 0.1), size=1, parent=th)
    add('cube', '5A4632', (-3.4, 0.6, 0.6), scale=(2.2, 0.6, 0.1), size=1, parent=th)
    for s in (-1, 1):
        add('cube', '4A3828', (-3.4 + s * 0.9, 0.6, 0.3), scale=(0.12, 0.5, 0.6), size=1, parent=th)
    sun = light((0, 0, 80), 2.2, 'FFE6C0', kind='SUN', parent=r)
    sun.rotation_euler = (0.95, 0.0, 0.7)
    return dict(gnear=gnear, case=case, sun=sun)


def dress_night():
    """The search: a patrol car on the trail, tape around the clearing. Parked far away until a night shot needs it."""
    car = empty(FAR)
    add('cube', 'ECECEC', (0, 0, 0.95), scale=(2.3, 4.8, 1.0), size=1, parent=car, rough=0.4)
    add('cube', '1E2A4A', (0, 0.2, 1.75), scale=(2.1, 2.5, 0.8), size=1, parent=car, rough=0.3)
    add('cube', '1E2A4A', (0, 0, 0.8), scale=(2.34, 4.84, 0.3), size=1, parent=car)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', '0E0E12', (sx * 1.15, sy * 1.5, 0.45), rot=(0, PI / 2, 0), radius=0.45, depth=0.3, vertices=10, parent=car)
        add('cube', 'FFF6D0', (sx * 0.75, -2.42, 0.95), scale=(0.4, 0.05, 0.22), size=1, parent=car, emit=14)
    red = add('cube', 'FF2A1E', (-0.5, 0.2, 2.25), scale=(0.9, 0.4, 0.2), size=1, parent=car, emit=30)
    blue = add('cube', '2A6CFF', (0.5, 0.2, 2.25), scale=(0.9, 0.4, 0.2), size=1, parent=car, emit=30)
    lr = light((-0.6, 0, 3.2), 0, 'FF2A1E', kind='POINT', parent=car)
    lb = light((0.6, 0, 3.2), 0, '2A6CFF', kind='POINT', parent=car)
    tape = empty(FAR)
    cs = ((0.4, -1.6), (9.6, -0.6), (9.4, 8.2), (0.6, 7.4))
    for i in range(4):
        a, b = cs[i], cs[(i + 1) % 4]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        add('cube', 'F2D21E', ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 1.3), rot=(0, 0, math.atan2(b[1] - a[1], b[0] - a[0])), scale=(L, 0.03, 0.16),
            size=1, parent=tape, emit=0.9)
        add('cylinder', 'C8CCD4', (a[0], a[1], 0.7), radius=0.06, depth=1.4, vertices=5, parent=tape)
    return dict(car=car, cred=red, cblue=blue, lred=lr, lblue=lb, tape=tape)


# ---------------------------------------------------------------- cast
def runner_head(head):
    d = K.human_head('C99A7A', '3A2A20')(head)
    add('cylinder', 'F4F4F4', (0, 0.02, 0.27), radius=0.31, depth=0.14, vertices=8, parent=head)
    add('cube', 'F4F4F4', (0, -0.36, 0.22), scale=(0.44, 0.3, 0.04), size=1, parent=head)
    d['eye0'] = 0.075
    return d


def man_head(head):
    add('ico_sphere', '2E3A2F', (0, 0.03, 0.04), scale=(1, 1.05, 1.12), radius=0.36, subdivisions=1, parent=head)
    add('cone', '2E3A2F', (0, 0.22, 0.34), rot=(-0.9, 0, 0), radius1=0.2, radius2=0, depth=0.4, vertices=5, parent=head)
    add('cube', '0C0A08', (0, -0.27, 0.0), scale=(0.38, 0.16, 0.36), size=1, parent=head)
    eyes = [add('cube', 'E8E0C8', (s * 0.09, -0.355, 0.04), scale=(0.07, 0.02, 0.035), size=1, parent=head, emit=1.6) for s in (-1, 1)]
    return dict(eyes=eyes, jaw=empty((0, -0.2, -0.13), head), eye0=0.035)


def cop_head(head):
    d = K.human_head('C68A5E', '2A2420')(head)
    add('cylinder', '1E2A4A', (0, 0.0, 0.3), radius=0.33, depth=0.16, vertices=8, parent=head)
    add('cube', '0E0E12', (0, -0.36, 0.24), scale=(0.44, 0.26, 0.04), size=1, parent=head)
    add('cube', 'D4A83A', (0, -0.33, 0.33), scale=(0.1, 0.03, 0.09), size=1, parent=head, rough=0.25, emit=0.6)
    d['eye0'] = 0.075
    return d


def torch(rig):
    """A torch in the right hand: its beam runs along the forearm."""
    el = rig.el[1]
    add('cylinder', '202428', (0, 0, -0.62), radius=0.07, depth=0.4, vertices=6, parent=el)
    add('cylinder', 'FFF6D0', (0, 0, -0.83), radius=0.09, depth=0.03, vertices=8, parent=el, emit=30)
    lamp = light((0, 0, -0.9), 0, 'FFF2D0', kind='SPOT', spot=0.55, parent=el)
    cone = add('cone', 'FFF2D0', (0, 0, -3.6), radius1=1.0, radius2=0.06, depth=5.4, vertices=10, parent=el, emit=0.25, alpha=0.07)
    return lamp, cone


def build():
    sc = bpy.context.scene
    S = dict()
    S.update(set_woods(empty()))
    S.update(dress_night())
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['runner'] = K.Rig(RUN, runner_head)
    S['man'] = K.Rig(MAN, man_head)
    S['cop1'], S['cop2'] = K.Rig(COP, cop_head), K.Rig(COP, cop_head)
    for kn in S['man'].kn:                                                                                    # heavy work boots
        add('cube', '1E1610', (0, -0.1, -0.44), scale=(0.3, 0.54, 0.26), size=1, parent=kn)
        add('cube', '0A0806', (0, -0.1, -0.57), scale=(0.33, 0.6, 0.07), size=1, parent=kn)
        add('cube', '6A4A2A', (0, -0.32, -0.36), scale=(0.2, 0.06, 0.05), size=1, parent=kn)
    S['man'].root.scale = (1.12, 1.12, 1.12)
    S['torches'] = [torch(S['cop1']), torch(S['cop2'])]
    comp = empty(FAR)                                                                                         # Rook's brass trail compass
    add('cylinder', 'D4A83A', (0, 0, 0), radius=0.2, depth=0.07, vertices=12, parent=comp, rough=0.25, emit=0.25)
    add('cylinder', 'F4EEDF', (0, 0, 0.04), radius=0.15, depth=0.02, vertices=12, parent=comp, emit=0.15)
    add('cube', 'D8261E', (0, 0.05, 0.06), scale=(0.04, 0.16, 0.02), size=1, parent=comp, emit=2)
    S['comp'] = comp
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


def cam(S, pos, look, lens=50, roll=0.0):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


def key(S, which, pos, look, energy):
    S[which].location, S[which + 'a'].location = pos, look
    S[which].data.energy = energy


def reset(S):
    for who in ('rook',) + PEOPLE:
        S[who].place(FAR)
        S[who].apply(P())
    S['face'] = dict(rook='calm', runner='calm', man='calm', cop1='calm', cop2='calm')
    S['hat_tip'] = 0.0
    for kk in ('kw', 'kc'):
        S[kk].data.energy = 0
    for lamp, cone in S['torches']:
        lamp.data.energy = 0
        cone.hide_render = True
    S['car'].location, S['tape'].location = FAR, FAR
    S['lred'].data.energy = S['lblue'].data.energy = 0
    S['case'].location = (SUIT[0], SUIT[1], 0)
    S['gnear'].rotation_euler = (0, 0, 0)
    S['comp'].location, S['comp'].rotation_euler, S['comp'].scale = FAR, (0, 0, 0), (1, 1, 1)
    S['sun'].data.energy, S['sun'].data.color = 2.2, K.hexc('FFE6C0')[:3]
    S['sun'].rotation_euler = (0.95, 0.0, 0.7)
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '8FA69A', 0.85)


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
        kk = dict(scared=1.5, shock=1.7, calm=1.0, sad=0.6, narrow=0.5).get(e, 1.0)
        for ey in x['eyes']:
            ey.scale = (ey.scale[0], ey.scale[1], x['eye0'] * kk)
        x['jaw'].rotation_euler = (0.5 if e == 'shock' else 0.0, 0, 0)
        x['jaw'].location.z = -0.13 - (0.05 if e in ('shock', 'scared') else 0.0)


# ---------------------------------------------------------------- helpers
def day(S, t, mode='grey'):
    S['gnear'].rotation_euler = (0.035 * math.sin(t * 2.3), 0.03 * math.sin(t * 1.7 + 1), 0)
    if mode == 'dusk':
        sky(S, 'B8704A', 0.75)
        S['sun'].data.energy, S['sun'].data.color = 2.6, K.hexc('FF9A50')[:3]
        S['sun'].rotation_euler = (1.3, 0.0, 2.3)


def night(S, t):
    sky(S, '070B18', 1.0)
    S['sun'].data.energy, S['sun'].data.color = 0.35, K.hexc('8FA8FF')[:3]
    S['car'].location = (px(-13), -13, 0)
    S['car'].rotation_euler = (0, 0, -math.atan(6 / 14 * math.cos(-13 / 14)) + 0.15)
    S['tape'].location = (0, 0, 0)
    S['case'].location = FAR
    on = (t * 2.6) % 1 < 0.5
    S['cred'].hide_render, S['cblue'].hide_render = not on, on
    S['lred'].data.energy, S['lblue'].data.energy = (60000 if on else 0), (0 if on else 60000)
    S['gnear'].rotation_euler = (0.03 * math.sin(t * 2.3), 0.02 * math.sin(t * 1.7 + 1), 0)


def who(S, name, loc, yaw, pose, face='calm'):
    S[name].place((loc[0], loc[1], loc[2] if len(loc) > 2 else 0.03), yaw)
    S[name].apply(pose)
    S['face'][name] = face


def rook(S, loc, yaw, pose, expr='calm'):
    who(S, 'rook', loc, yaw, pose, expr)


def torch_on(S, i, e=2600):
    lamp, cone = S['torches'][i]
    lamp.data.energy = e
    cone.hide_render = False


def jog(t, speed=2.6):
    w = walk(t, speed)
    w['lean'] = 0.2
    return w


RUNNER_AT_CASE = yaw_to(R0, SUIT)
MAN_FACING = yaw_to(M0, R0)
BLOCK = P('stand', aL=(0.15, 0.55, 0.3), aR=(0.15, 0.55, 0.3), head=(0.08, 0.0))


def standoff(S, t, runner_face='scared'):
    who(S, 'runner', R0, yaw_to(R0, M0), P('stand', aL=(0.3, 0.2, 0.9), aR=(0.3, 0.2, 0.9), lean=-0.08), runner_face)
    who(S, 'man', M0, MAN_FACING, blend(BLOCK, P('stand', aL=(0.1, 0.5, 0.2), aR=(0.1, 0.5, 0.2), head=(0.12, 0.0)), 0.5 + 0.5 * math.sin(t * 1.3)),
        'narrow')


# ---------------------------------------------------------------- hook
def suitcase_cu(S, k, t, lt):
    day(S, t)
    cam(S, at(SUIT, lerp(1.5, 0.9, k), lerp(-5.2, -2.4, ease(k)), lerp(-3.6, -1.8, ease(k))), at(SUIT, 0.7), 28, roll=0.05 * math.sin(t * 11))


def runner_stop(S, k, t, lt):
    day(S, t)
    y = lerp(-7.0, -0.6, 1 - (1 - min(1.0, k * 1.5)) ** 2)
    stop = ease((k - 0.55) / 0.25)
    who(S, 'runner', (px(y) + 0.5 * stop, y), PI - 0.5 * stop, blend(jog(lt), P('stand', head=(0.0, -0.5), lean=-0.1), stop), 'calm' if stop < 0.5 else 'scared')
    key(S, 'kw', (px(y) - 3, y + 6, 4), (px(y), y, 2.0), 500)
    cam(S, (px(7.5) - lerp(1.0, 0.2, k), lerp(7.5, 4.2, k), lerp(0.9, 1.8, k)), (px(y) + 0.3, y, 1.9), 27)


def grass_pov(S, k, t, lt):
    day(S, t)
    e = ease(k)
    cam(S, (lerp(0.6, 3.5, e), lerp(0.3, 2.4, e), 1.9 + 0.07 * math.sin(lt * 9)), at(SUIT, lerp(1.0, 0.75, k)), lerp(22, 30, k),
        roll=0.03 * math.sin(lt * 9))


def man_out(S, k, t, lt):
    day(S, t)
    who(S, 'runner', R0, RUNNER_AT_CASE, P('stand', aR=(0.7, 0.1, 0.4), lean=0.12 - 0.3 * ease((k - 0.3) / 0.3), head=(0.1, 0)), 'scared' if k > 0.3 else 'calm')
    j = ease(min(1.0, k / 0.55))
    src = (9.2, 4.9)
    loc = (lerp(src[0], M0[0], j), lerp(src[1], M0[1], j), 0.03 + 0.9 * math.sin(j * PI))
    who(S, 'man', loc, MAN_FACING, blend(P('up', aL=(1.6, 0.9, 0.6), aR=(1.6, 0.9, 0.6), lL=(0.9, 1.2), lR=(-0.4, 0.6)), BLOCK, ease((k - 0.45) / 0.25)), 'narrow')
    key(S, 'kc', (1.5, -3, 5), (loc[0], loc[1], 2.2), 1300)
    key(S, 'kw', (8, -2, 4), (loc[0], loc[1], 2.2), 700)
    cam(S, (lerp(6.4, 5.2, k), lerp(-4.4, -2.8, k), lerp(2.0, 2.5, k)), (lerp(4.2, 3.2, k), 2.3, 1.9), 22, roll=0.06 * math.sin(t * 13) * (1 - k))


# ---------------------------------------------------------------- doubt
def rook_sign(S, k, t, lt):
    day(S, t)
    sh = math.sin(lt * 9) * 0.3 * max(0.0, 1 - lt / 1.1)
    rook(S, (4.6, -54.2), 0.15, P('cross', head=(0.05, sh)), 'deadpan')
    S['hat_tip'] = 0.4
    key(S, 'kw', (1.5, -59, 4), (4.6, -54.2, 2.3), 700)
    cam(S, (lerp(7.2, 4.6, k), lerp(-61.5, -58.6, k), lerp(1.6, 2.3, k)), (lerp(5.2, 4.8, k), -54, 2.4), 28)


# ---------------------------------------------------------------- trail
def trail_aerial(S, k, t, lt):
    day(S, t)
    y = lerp(-22, -12, k)
    who(S, 'runner', (px(y), y), PI + math.atan(6 / 14 * math.cos(y / 14)), jog(lt), 'calm')
    cam(S, (lerp(-10, -2, k), lerp(-44, -34, k), lerp(62, 48, k)), (px(y) + 2, y + 6, 0), 30, roll=lerp(-0.12, 0.06, k))


def runner_jog(S, k, t, lt):
    day(S, t)
    y = lerp(-13, -6.5, k)
    who(S, 'runner', (px(y), y), PI + math.atan(6 / 14 * math.cos(y / 14)), jog(lt), 'calm')
    y2 = y - 3.4
    wk = jog(lt + 0.2, 2.9)
    wk['aR'] = (0.2, 1.9, 1.6, -1.5)
    wk['head'] = (0.12, 0.0)
    rook(S, (px(y2) + 0.4, y2), PI + math.atan(6 / 14 * math.cos(y2 / 14)), wk, 'deadpan')
    key(S, 'kw', (px(y) - 5, y - 4, 4), (px(y), y - 1.5, 2), 600)
    cam(S, (px(y) - lerp(4.6, 3.9, k), y + lerp(1.8, -0.4, k), lerp(1.2, 1.7, k)), (px(y) + 0.2, y - 1.5, 1.9), 22)


def suitcase_wide(S, k, t, lt):
    day(S, t)
    e = ease(k)
    a = (px(-0.5) + 0.3, -0.5)
    loc = (lerp(a[0], R0[0], e), lerp(a[1], R0[1], e))
    who(S, 'runner', loc, RUNNER_AT_CASE, blend(walk(lt, 1.3), P('stand', head=(0.15, 0), lean=0.1), ease((k - 0.75) / 0.25)), 'calm')
    ry = lerp(-6.5, -3.2, e)
    wk = walk(lt, 1.8)
    wk['aR'] = (0.2, 1.9, 1.6, -1.5)
    rook(S, (px(ry) - 0.5, ry), PI, wk, 'calm')
    cam(S, at(SUIT, lerp(1.3, 1.7, k), lerp(1.8, 0.9, k), lerp(3.9, 3.0, k)), (lerp(1.2, 1.7, k), lerp(-1.0, -0.3, k), 1.2), 21)


def rook_crouch(S, k, t, lt):
    day(S, t)
    p = at(SUIT, 0.03, -0.7, 1.7)
    c0 = at(SUIT, 1.2, -1.3, -3.8)
    tap = 0.5 + 0.5 * math.sin(lt * 10)
    pose = blend(P('sit', aR=(1.0, 0.0, 0.4), lift=-0.42, lean=0.3, head=(0.35, 0.2)), P('sit', aR=(0.5, 0.35, 2.5, 0.6), lift=-0.42, lean=0.25, head=(0.15, -0.1)),
                 ease((k - 0.5) / 0.2) * (0.7 + 0.3 * tap))
    rook(S, p, yaw_to(p, c0), pose, 'smirk')
    key(S, 'kw', at(SUIT, 3, -3.5, -3.5), at(SUIT, 1.4, -0.6, 1.4), 620)
    key(S, 'kc', at(SUIT, 3, 2.5, -1), at(SUIT, 1.4, -0.6, 1.4), 300)
    cam(S, at(SUIT, lerp(0.9, 1.4, k), lerp(-2.4, -1.2, k), lerp(-4.6, -3.1, k)), at(SUIT, 1.25, -0.4, 0.8), 28)


# ---------------------------------------------------------------- man
def man_block(S, k, t, lt):
    day(S, t)
    standoff(S, t)
    d = (R0[0] - M0[0], R0[1] - M0[1])
    cam(S, (R0[0] + d[0] * lerp(1.3, 0.8, k) + 0.9, R0[1] + d[1] * lerp(1.3, 0.8, k) - 0.5, lerp(2.9, 2.6, k)), (M0[0], M0[1], lerp(2.4, 2.7, k)), 30)


def man_cu(S, k, t, lt):
    day(S, t)
    who(S, 'man', M0, MAN_FACING, P('stand', head=(lerp(0.2, 0.0, k), lerp(-0.25, 0.2, ease(k)))), 'narrow')
    d = (R0[0] - M0[0], R0[1] - M0[1])
    key(S, 'kc', (M0[0] + d[0] * 2 + 1.5, M0[1] + d[1] * 2, 4.5), (M0[0], M0[1], 2.9), 160)
    cam(S, (M0[0] + d[0] * lerp(1.5, 1.0, k) + lerp(-0.5, 0.3, k), M0[1] + d[1] * lerp(1.5, 1.0, k), lerp(2.6, 3.0, k)), (M0[0], M0[1], 2.95), 40,
        roll=lerp(0.06, -0.04, k))


def case_between(S, k, t, lt):
    day(S, t)
    standoff(S, t)
    rp = (PEEK[0] + 0.5, PEEK[1] + 0.95)
    rook(S, rp, yaw_to(rp, SUIT), P('stand', aL=(0.9, 0.3, 1.6), lean=0.15, head=(0.1, lerp(0.5, 0.2, k))), 'shocked' if k > 0.5 else 'calm')
    key(S, 'kw', (1.0, 2.5, 4), (rp[0], rp[1], 2.5), 420)
    key(S, 'kc', (7.5, 7.5, 5), (M0[0], M0[1], 2.4), 900)
    cam(S, at(SUIT, lerp(1.3, 1.9, k), lerp(2.9, 1.9, k), lerp(3.2, 2.4, k)), (lerp(2.7, 3.1, k), lerp(1.9, 2.3, k), 1.4), 22)


# ---------------------------------------------------------------- clue
def rook_lean(S, k, t, lt):
    day(S, t)
    e = ease(lt / 0.4)
    p = (-0.2, -2.2)
    rook(S, p, 0.0, blend(P('stand', head=(0.0, 0.1)), P('stand', aR=(0.75, 0.15, 0.15), lean=0.26, head=(0.25, -0.05)), e), 'smirk')
    key(S, 'kw', (-2.4, -6, 3.4), (p[0], p[1], 2.4), 560)
    key(S, 'kc', (2.2, -0.5, 3.0), (p[0], p[1], 2.4), 320)
    cam(S, (lerp(0.9, -0.1, k), lerp(-5.6, -4.3, k), lerp(2.0, 2.5, k)), (p[0], p[1] - 0.2, lerp(2.4, 2.1, k)), 30)


def boots_cu(S, k, t, lt):
    day(S, t)
    who(S, 'man', M0, MAN_FACING, P('stand', lL=(0.12 * math.sin(lt * 3), 0.0)), 'narrow')
    d = (R0[0] - M0[0], R0[1] - M0[1])
    key(S, 'kw', (M0[0] + d[0] * 2 - 1, M0[1] + d[1] * 2 - 1, 1.5), (M0[0], M0[1], 0.4), 520)
    cam(S, (M0[0] + d[0] * lerp(1.35, 0.95, k) + lerp(0.9, -0.5, k), M0[1] + d[1] * lerp(1.35, 0.95, k) + lerp(-0.6, 0.3, k), lerp(0.22, 0.5, k)),
        (M0[0], M0[1], lerp(0.3, 0.9, k)), 26)


# ---------------------------------------------------------------- run
def runner_eyes(S, k, t, lt):
    day(S, t)
    nod = math.sin(min(1.0, lt / 0.7) * PI)
    who(S, 'runner', R0, yaw_to(R0, M0), P('stand', head=(0.45 * nod, 0.0), lean=-0.1 * ease(k)), 'calm' if lt < 0.45 else 'scared')
    d = (M0[0] - R0[0], M0[1] - R0[1])
    key(S, 'kw', (R0[0] + d[0] * 2 - 1.2, R0[1] + d[1] * 2 + 0.6, 3.6), (R0[0], R0[1], 2.6), 380)
    cam(S, (R0[0] + d[0] * lerp(1.25, 0.8, k) + lerp(0.5, -0.2, k), R0[1] + d[1] * lerp(1.25, 0.8, k), lerp(2.3, 2.7, k)), (R0[0], R0[1], 2.6), 38)


def runner_flee(S, k, t, lt):
    day(S, t)
    y = lerp(-3.0, -13.2, k)
    who(S, 'runner', (px(y), y), -math.atan(6 / 14 * math.cos(y / 14)), jog(lt, 3.6), 'scared')
    y2 = y + 3.0
    wk = jog(lt + 0.3, 3.6)
    wk['aR'] = (0.2, 1.9, 1.6, -1.5)
    rook(S, (px(y2) + 0.5, y2), -math.atan(6 / 14 * math.cos(y2 / 14)), wk, 'shocked')
    mp = (px(3.0) + 0.6, 3.0)
    who(S, 'man', mp, yaw_to(mp, (px(-12), -12)), P('stand'), 'narrow')
    key(S, 'kw', (px(-16) + 3, -18, 4), (px(y), y, 2), 700)
    cam(S, (px(-15) + lerp(1.4, 0.4, k), lerp(-15.5, -17.0, k), lerp(0.7, 1.3, k)), (px(y) * 0.6, y + 2, 1.9), 26, roll=0.04 * math.sin(t * 12))


# ---------------------------------------------------------------- twist
def police_lights(S, k, t, lt):
    night(S, t)
    who(S, 'cop2', (px(-9) + 1.4, -9.0), 0.3, P('stand', aR=(0.9, 0.2, 0.3)), 'calm')
    torch_on(S, 1)
    cam(S, (px(-30) + lerp(1.2, 0.2, k), lerp(-31, -24, k), lerp(1.1, 1.9, k)), (px(-13), -13, 1.6), 30, roll=lerp(-0.05, 0.03, k))


def cops_search(S, k, t, lt):
    night(S, t)
    sw = math.sin(lt * 2.4)
    who(S, 'cop1', (2.6, 0.6), yaw_to((2.6, 0.6), SUIT) + 0.5 * sw, P('stand', aR=(0.95, 0.1, 0.25), head=(0.25, 0)), 'calm')
    who(S, 'cop2', (7.6, 6.2), yaw_to((7.6, 6.2), (3, 4)) - 0.5 * sw, P('stand', aR=(0.9, 0.1, 0.3), head=(0.25, 0)), 'calm')
    torch_on(S, 0)
    torch_on(S, 1)
    rp = (-2.7, -3.6)
    rook(S, rp, yaw_to(rp, (-5, -9)), P('stand', aR=(0.2, 1.9, 1.6, -1.5), head=(0.3, 0.0)), 'sad')
    S['hat_tip'] = -0.3
    key(S, 'kc', (-4, -8, 4), (rp[0], rp[1], 2.4), 520)
    cam(S, (lerp(-5.5, -3.2, k), lerp(-8.5, -7.4, k), lerp(1.4, 2.0, k)), (lerp(0.6, 1.6, k), 0.0, 1.9), 23)


# ---------------------------------------------------------------- show
def runner_points(S, k, t, lt):
    night(S, t)
    rp = (1.3, -0.4)
    e = ease(lt / 0.5)
    who(S, 'runner', rp, yaw_to(rp, SUIT), blend(P('stand'), P('point', aR=(1.35, 0.05, 0.05), head=(0.1, 0)), e), 'sad')
    cp = (2.9, -1.6)
    who(S, 'cop1', cp, yaw_to(cp, SUIT), P('stand', aR=(0.8 + 0.1 * math.sin(lt * 3), 0.1, 0.2), head=(0.2, 0)), 'calm')
    torch_on(S, 0, 1800)
    kp = (-0.4, -2.2)
    rook(S, kp, yaw_to(kp, SUIT), P('stand', aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), head=(0.25, 0)), 'sad')
    key(S, 'kc', (-3, 3, 4), (1.3, -0.8, 2.3), 1500)
    cam(S, (lerp(-4.6, -2.6, k), lerp(4.8, 3.4, k), lerp(1.3, 1.9, k)), (lerp(1.2, 1.8, k), -0.9, 2.0), 25)


def grass_reverse(S, k, t, lt):
    night(S, t)
    rp, cp = (3.4, 1.9), (4.3, 1.2)
    who(S, 'runner', rp, yaw_to(rp, SUIT), P('stand', lean=0.3, head=(0.4, 0)), 'sad')
    who(S, 'cop1', cp, yaw_to(cp, SUIT), P('stand', aR=(0.5, 0.3, 0.3), lean=0.25, head=(0.4, 0)), 'calm')
    torch_on(S, 0, 700)
    key(S, 'kw', at(SUIT, 0.4, -0.3, -0.2), (3.8, 1.6, 2.6), 160)
    cam(S, at(SUIT, lerp(0.7, 0.3, k), lerp(0.5, -0.1, k), lerp(0.6, 0.2, k)), (3.8, 1.5, lerp(2.2, 2.6, k)), lerp(20, 24, k), roll=lerp(0.08, -0.04, k))


# ---------------------------------------------------------------- theories / end
def man_watch(S, k, t, lt):
    day(S, t)
    mp = (px(7.0), 7.0)
    who(S, 'man', mp, yaw_to(mp, (px(-6), -6)), P('stand'), 'narrow')
    y = lerp(1.5, -9.0, k)
    cam(S, (px(y) + lerp(0.6, -0.4, k), y, lerp(1.9, 1.4, k)), (mp[0], mp[1], 2.2), lerp(36, 26, k))


def rook_cam(S, k, t, lt):
    day(S, t, 'dusk')
    e = ease(lt / 0.45)
    p = (px(-20) + 0.3, -20)
    rook(S, p, 0.0, blend(P('stand', head=(0.05, 0)), P('shrug', head=(0.0, 0.0), lean=0.08), e), 'smirk')
    key(S, 'kw', (p[0] - 2.4, -24, 3.8), (p[0], -20, 2.4), 800)
    key(S, 'kc', (p[0] + 3.2, -17, 3.0), (p[0], -20, 2.4), 500)
    cam(S, (p[0] + lerp(1.3, -0.2, k), lerp(-25.2, -23.6, k), lerp(2.0, 2.5, k)), (p[0], -20, 2.35), 30)


def trail_dusk(S, k, t, lt):
    day(S, t, 'dusk')
    cam(S, (px(lerp(-8, -16, k)) + 0.4, lerp(-8, -16, k), lerp(1.2, 5.5, k)), (px(4), 4, lerp(1.6, 0.6, k)), 24, roll=lerp(-0.04, 0.04, k))


def rook_tag(S, k, t, lt):
    day(S, t, 'dusk')
    p = (px(-21) + 0.2, -21)
    rook(S, p, 0.35, P('stand', aR=(1.25, 0.45, 0.55, 0.2), head=(0.1, -0.45)), 'warm')
    bpy.context.view_layer.update()
    hand = S['rook'].hands[1].matrix_world.translation
    S['comp'].location = (hand.x, hand.y - 0.05, hand.z + 0.2)
    S['comp'].rotation_euler = (1.35, 0.0, 0.5 * math.sin(t * 3))
    S['comp'].scale = (0.8, 0.8, 0.8)
    key(S, 'kw', (p[0] - 1, -25, 3.4), (p[0] + 0.4, -21.6, 2.2), 800)
    cam(S, (p[0] + lerp(1.9, 0.9, k), lerp(-24.8, -23.7, k), lerp(1.9, 2.4, k)), (p[0] + 0.45, -21.5, 2.15), 32)


def signoff(S, k, t, lt):
    day(S, t, 'dusk')
    p = (px(-20), -20)
    c = max(0.0, min(1.0, (lt - 0.2) / 0.9))
    rook(S, p, 0.2, blend(P('stand', aR=(0.9, 0.25, 1.2), head=(0.05, 0)), P('stand', aR=(1.2, 0.2, 1.5), head=(-0.12, 0)), math.sin(c * PI)), 'smirk')
    S['comp'].location = (p[0] + 0.75 + 0.2 * c, -20.75, 1.8 + 2.4 * math.sin(c * PI))
    S['comp'].rotation_euler = (t * 19, t * 9, 0)
    S['comp'].scale = (1.4, 1.4, 1.4)
    key(S, 'kw', (p[0] - 2, -24, 3.5), (p[0], -20, 2.2), 800)
    key(S, 'kc', (p[0] + 3, -17, 3), (p[0], -20, 2.2), 500)
    cam(S, (p[0] + lerp(1.7, 1.3, k), lerp(-25.0, -24.2, k), 0.9), (p[0], -20, 2.25), 36)


# ---------------------------------------------------------------- still for the theory wall
def photo_case(S, k, t, lt):
    day(S, 0.0)
    cam(S, at(SUIT, 1.3, -3.4, -2.6), at(SUIT, 0.7), 30)


SHOTS3D = {f.__name__: f for f in (
    suitcase_cu, runner_stop, grass_pov, man_out, rook_sign, trail_aerial, runner_jog, suitcase_wide, rook_crouch, man_block, man_cu,
    case_between, rook_lean, boots_cu, runner_eyes, runner_flee, police_lights, cops_search, runner_points, grass_reverse, man_watch,
    rook_cam, trail_dusk, rook_tag, signoff)}
STILLS = dict(case=photo_case)
