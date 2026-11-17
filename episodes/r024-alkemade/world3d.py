"""Case 024 in 3D - Nicholas Alkemade, 1944. On the night of 24 March 1944 a Lancaster of No. 115 Squadron,
on its way back from Berlin, was set on fire by a night fighter. The rear gunner found his parachute burning,
chose to jump rather than burn, fell about 18,000 feet, came down through young pine trees into deep snow and
got up with a twisted knee. His interrogators did not believe him until the wood and the wreck were searched.

Built for this story only: a night sky with a four-engined bomber and a twin-engined fighter, a strip of
fuselage interior with the parachute rack, a snowy pine wood (night, day and dawn), a piece of burnt tail
in a snowfield, an interrogation room, and a row of four plain headstones.

Everything is a generic low-poly reconstruction. The aircraft carry no markings, numbers or national
insignia; the men in the room and in the wood wear plain coats, hats and caps with no badges or symbols;
nobody's likeness is attempted."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -3000)
SKYO = (0.0, 0.0, 0.0)              # the bomber
FALL = (0.0, 600.0, -300.0)         # empty air, where the fall is filmed
BAY = (0.0, -4000.0, 0.0)           # a strip of fuselage interior
WOOD = (4000.0, 0.0, 0.0)           # the pine wood
WRECK = (4160.0, 0.0, 0.0)          # the burnt tail, in a snowfield beyond the wood
ROOM = (0.0, 4000.0, 0.0)           # the interrogation room
YARD = (-4000.0, 0.0, 0.0)          # four headstones
HOST = {'rook_fall', 'rook_maths', 'rook_gives_up', 'hole_up', 'rook_measure', 'knee', 'room_wide', 'rook_room', 'he_points',
        'search_wood', 'harness', 'officer_writes', 'rook_hat', 'four_stones', 'signoff'}
CAMFILL = {'*': 160, 'bomber_wide': 900, 'turret_fire': 90, 'chute_burn': 60, 'backflip': 300, 'rook_fall': 320, 'fighter': 2500,
           'wing_fire': 700, 'fall_wide': 500, 'rook_maths': 260, 'fall_close': 220, 'rook_gives_up': 260, 'trees_rush': 0,
           'crash_branches': 500, 'snow_hole': 300, 'hole_up': 260, 'rook_measure': 300, 'limbs': 260, 'knee': 300, 'lantern': 200,
           'room_wide': 120, 'gestapo_laugh': 60, 'rook_room': 160, 'spy_point': 80, 'he_points': 70, 'officer_writes': 80,
           'man_smile': 60, 'rook_hat': 120, 'search_wood': 0, 'harness': 0, 'wreck': 0, 'chute_pack': 40, 'four_stones': 40, 'signoff': 60}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'E2B48C'
JACKET, HELMET = '6E5434', '4A3422'
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    night=('1A3552', '050A18', 0.7, 1.6, 'A8C8F0', (-0.45, -0.35, 0.82)),
    wood=('223E5E', '060C1C', 0.9, 2.2, 'B4D0F4', (-0.35, -0.5, 0.8)),
    day=('D6DEE6', '94A6BC', 1.5, 2.6, 'F6F2EA', (0.35, -0.5, 0.78)),
    dawn=('F4B88E', '4C6E9E', 1.3, 2.6, 'FFC8A0', (0.75, -0.55, 0.22)),
    room=('0C0E14', '06070A', 0.25, 0.0, 'FFFFFF', (0, 0, 1)))
_KEEP = []


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rnd(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def keep(o):
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def at(o, x, y, z):
    return (o[0] + x, o[1] + y, o[2] + z)


def span(o, a, b, w):
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def bar(par, col, a, b, w, **kw):
    o = add('cylinder', col, radius=0.5, depth=1, vertices=6, parent=par, **kw)
    span(o, a, b, w)
    return o


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


# ---------------------------------------------------------------- the two aircraft
def make_bomber(S):
    """A four-engined heavy bomber with twin fins, nose towards -Y. No markings. The rear turret is an open frame:
    its glazing has been shot away."""
    b = keep(empty(SKYO))
    G, U, D = '2F3B2C', '14161A', '1B222A'
    add('cube', G, (0, 0, 0.4), scale=(3.0, 30, 2.6), size=1, parent=b)
    add('cube', U, (0, 0, -1.0), scale=(3.05, 30.05, 1.4), size=1, parent=b)
    add('cube', G, (0, -16.2, 0.1), scale=(2.5, 3.0, 2.6), size=1, parent=b)
    add('cube', D, (0, -18.0, -0.2), scale=(1.9, 1.4, 1.8), size=1, parent=b, rough=0.3)
    add('cube', D, (0, -10.5, 2.1), scale=(2.2, 5.5, 1.1), size=1, parent=b, rough=0.3)
    add('ico_sphere', D, (0, 4, 1.8), radius=1.0, subdivisions=1, parent=b, rough=0.3)
    add('cube', G, (0, -3.5, 0.2), scale=(26, 7.6, 0.55), size=1, parent=b)
    for s in (-1, 1):
        add('cube', G, (s * 19, -3.0, 0.45), rot=(0, s * -0.05, s * 0.07), scale=(13, 5.2, 0.4), size=1, parent=b)
        add('cube', G, (s * 7.5, 14.0, 0.9), scale=(1.0, 3.6, 0.3), size=1, parent=b)
        add('cube', G, (s * 4.0, 13.8, 0.9), scale=(7.5, 3.4, 0.3), size=1, parent=b)
        add('cube', G, (s * 7.9, 14.1, 1.3), scale=(0.3, 4.4, 4.6), size=1, parent=b)
        for x in (7.0, 14.0):
            add('cylinder', U, (s * x, -6.6, 0.0), rot=(PI / 2, 0, 0), radius=1.15, depth=6.4, vertices=8, parent=b)
            add('cone', '50545C', (s * x, -10.3, 0.0), rot=(PI / 2, 0, 0), radius1=0.5, radius2=0.0, depth=1.0, vertices=6, parent=b)
            add('cylinder', 'AAB4C0', (s * x, -10.0, 0.0), rot=(PI / 2, 0, 0), radius=3.1, depth=0.05, vertices=14, parent=b, alpha=0.16)
    # the rear turret: rings, uprights, four guns, a seat
    T = (0, 16.3, 0)
    for z in (-1.25, 1.25):
        add('torus', '50565E', (T[0], T[1], z), major_radius=1.5, minor_radius=0.07, major_segments=12, minor_segments=4, parent=b)
    for i in range(5):
        a = math.radians(-70 + 35 * i)
        if i == 2:
            continue
        x, y = 1.5 * math.sin(a), T[1] + 1.5 * math.cos(a)
        bar(b, '50565E', (x, y, -1.25), (x, y, 1.25), 0.05)
    for sx in (-1, 1):
        for z in (-0.28, 0.2):
            bar(b, '22262C', (sx * 0.55, 17.3, z), (sx * 0.55, 20.0, z), 0.07)
        add('cube', '3A4048', (sx * 0.55, 17.2, -0.04), scale=(0.3, 0.9, 0.75), size=1, parent=b)
    add('cube', '3A3026', (0, 15.75, -1.05), scale=(1.1, 0.9, 0.2), size=1, parent=b)
    add('cube', '0C0D10', (0, 14.95, 0.2), scale=(1.5, 0.12, 2.2), size=1, parent=b)          # the open doors into the fuselage
    S['bomber'] = b


def make_fighter(S):
    """A twin-engined night fighter, nose towards -Y, dark and unmarked."""
    f = keep(empty(FAR))
    C = '20262E'
    add('cube', C, (0, 0, 0), scale=(1.5, 16, 1.7), size=1, parent=f)
    add('cube', '2C3640', (0, -5.5, 0.9), scale=(1.2, 4, 0.8), size=1, parent=f, rough=0.3)
    add('cube', C, (0, -1.5, -0.1), scale=(24, 4.2, 0.35), size=1, parent=f)
    add('cube', C, (0, 7.2, 0.5), scale=(8, 2.0, 0.25), size=1, parent=f)
    add('cube', C, (0, 7.4, 1.6), scale=(0.25, 2.6, 2.6), size=1, parent=f)
    for s in (-1, 1):
        add('cylinder', '15181C', (s * 3.6, -3.4, -0.2), rot=(PI / 2, 0, 0), radius=0.9, depth=5.0, vertices=8, parent=f)
        add('cylinder', 'AAB4C0', (s * 3.6, -6.1, -0.2), rot=(PI / 2, 0, 0), radius=2.4, depth=0.05, vertices=12, parent=f, alpha=0.16)
    S['fighter'] = f


def make_air(S):
    S['clouds'] = [keep(add('ico_sphere', '34465E', FAR, scale=(16 + 22 * rnd(i, 1), 20 + 26 * rnd(i, 2), 3 + 4 * rnd(i, 3)), radius=1,
                            subdivisions=2, rough=1.0)) for i in range(16)]
    ld = keep(empty(FAR))
    add('cube', '0C1719', (0, 0, 0), scale=(9000, 9000, 1), size=1, parent=ld, rough=1.0)
    for i in range(46):
        col = ('2B3B48', '16282A', '3A4A58')[i % 3]
        add('cube', col, ((rnd(i, 4) - 0.5) * 2600, (rnd(i, 5) - 0.5) * 2600, 1), rot=(0, 0, rnd(i, 6) * 3),
            scale=(90 + 260 * rnd(i, 7), 60 + 200 * rnd(i, 8), 1), size=1, parent=ld, rough=1.0)
    S['land'] = ld
    st = keep(empty(FAR))
    for i in range(90):
        z = rnd(i, 9) * 1.7 - 0.7
        r = math.sqrt(max(0.0, 1 - z * z))
        a = rnd(i, 10) * 2 * PI
        s = 3 + 5 * rnd(i, 11)
        add('ico_sphere', 'F4F6FF', (1700 * r * math.cos(a), 1700 * r * math.sin(a), 1700 * z), scale=(s, s, s), radius=1, subdivisions=1,
            parent=st, emit=9.0)
    S['stars'] = st
    S['fl'] = [keep(add('cone', ('FF7A1A', 'FFC040', 'FF4A10')[i % 3], FAR, radius1=0.55, radius2=0.0, depth=2.2, vertices=5,
                        emit=(9.0, 14.0, 7.0)[i % 3])) for i in range(30)]
    S['flamp'] = [light(FAR, 0, 'FF8A30', kind='POINT') for _ in range(3)]
    S['tracers'] = [keep(add('cylinder', 'FFE890', FAR, radius=0.5, depth=1, vertices=5, emit=20.0)) for _ in range(7)]
    S['bits'] = [keep(add('cube', ('2F3B2C', '4A3424', '1F4034', '50565E')[i % 4], FAR, scale=(0.5, 0.16, 0.12), size=1)) for i in range(12)]
    S['snowb'] = [keep(add('ico_sphere', 'F2F6FC', FAR, radius=0.14, subdivisions=1, rough=1.0)) for _ in range(22)]
    S['smoke'] = [keep(add('ico_sphere', '5A5E66', FAR, radius=0.6, subdivisions=1, rough=1.0, alpha=0.5)) for _ in range(7)]


# ---------------------------------------------------------------- the parachute rack inside the fuselage
def make_bay(S):
    r = keep(empty(BAY))
    add('cube', '34463A', (0, 1.0, 2.0), scale=(11, 0.2, 6), size=1, parent=r)
    add('cube', '1E2420', (0, -1.5, -0.1), scale=(11, 6, 0.2), size=1, parent=r)
    for i in range(6):
        add('cube', '4A5E4E', (-5 + 2 * i, 0.82, 2.0), scale=(0.16, 0.2, 6), size=1, parent=r)
    for z in (0.7, 3.4):
        add('cube', '4A5E4E', (0, 0.84, z), scale=(11, 0.14, 0.12), size=1, parent=r)
    for (a, b_) in (((-1.0, 0.6, 0.9), (1.0, 0.6, 0.9)), ((-1.0, 0.6, 2.2), (1.0, 0.6, 2.2)), ((-1.0, 0.6, 0.9), (-1.0, 0.6, 2.2)),
                    ((1.0, 0.6, 0.9), (1.0, 0.6, 2.2)), ((-1.0, 0.0, 0.9), (-1.0, 0.7, 0.9)), ((1.0, 0.0, 0.9), (1.0, 0.7, 0.9))):
        bar(r, '8A929C', a, b_, 0.05)
    add('cube', '8A929C', (0, 0.3, 0.88), scale=(2.0, 0.7, 0.06), size=1, parent=r)
    S['pack'] = pk = empty((0, 0.25, 1.5), r)
    add('cube', 'B49A62', (0, 0, 0), scale=(1.5, 0.55, 1.0), size=1, parent=pk, rough=1.0)
    for x in (-0.45, 0.45):
        add('cube', 'E0D6B8', (x, -0.29, 0), scale=(0.14, 0.03, 1.02), size=1, parent=pk, rough=1.0)
    add('cube', 'C9CED6', (0, -0.31, 0.2), scale=(0.34, 0.04, 0.12), size=1, parent=pk, rough=0.3)                  # the ripcord handle
    add('cube', '3A3A3A', (0, -0.3, -0.25), scale=(0.9, 0.03, 0.3), size=1, parent=pk)
    S['scorch'] = [add('ico_sphere', '15110E', (-0.5 + 0.5 * i, -0.3, 0.3 - 0.25 * (i % 2)), scale=(1, 0.2, 1), radius=0.2, subdivisions=1, parent=pk)
                   for i in range(3)]
    S['bay'] = r
    S['glove'] = K.Hand('5A3E24', JACKET, 1.5)
    keep(S['glove'].root)


# ---------------------------------------------------------------- the wood
def pine(par, x, y, h, s=1.0, snow=True):
    r = empty((x, y, 0), par, (0.04 * (rnd(x, y) - 0.5), 0.04 * (rnd(y, x) - 0.5), 6 * rnd(x, 3)))
    add('cylinder', '4A3424', (0, 0, h * 0.25), radius=0.14 + 0.012 * h, depth=h * 0.5, vertices=6, parent=r)
    for i in range(4):
        z, rad = h * (0.36 + 0.185 * i), s * (2.5 - 0.55 * i)
        add('cone', '1F4034', (0, 0, z), radius1=rad, radius2=0.0, depth=h * 0.32, vertices=7, parent=r, rough=1.0)
        if snow:
            add('cone', 'DDE8F4', (0, 0, z + 0.03 * h), radius1=rad * 0.82, radius2=0.0, depth=h * 0.29, vertices=7, parent=r, rough=1.0)
    return r


RING = (40, 95, 150, 205, 340)


def make_wood(S):
    w = keep(empty(WOOD))
    add('cube', 'CCDAEA', (80, 0, -0.5), scale=(900, 700, 1.0), size=1, parent=w, rough=1.0)
    for i in range(26):                                                   # low drifts, so the ground is not a flat sheet
        a, r = rnd(i, 20) * 2 * PI, 9 + 70 * rnd(i, 21)
        add('ico_sphere', 'DCE8F4', (r * math.cos(a), r * math.sin(a), -0.25), scale=(3 + 5 * rnd(i, 22), 3 + 4 * rnd(i, 23), 0.55), radius=1,
            subdivisions=2, parent=w, rough=1.0)
    for i, deg in enumerate(RING):                                        # the young pines he came down through
        a = math.radians(deg)
        pine(w, 5.6 * math.cos(a), 5.6 * math.sin(a), 13 + 3 * rnd(i, 24), 0.95)
    n = 0
    for i in range(150):
        a, r = rnd(i, 25) * 2 * PI, 10 + 75 * rnd(i, 26) ** 0.8
        deg = math.degrees(a) % 360
        if (225 < deg < 320 and r < 34) or ((deg < 22 or deg > 350) and r < 26):
            continue                                                      # two lanes are kept clear for the camera
        pine(w, r * math.cos(a), r * math.sin(a), 11 + 9 * rnd(i, 27), 0.9 + 0.5 * rnd(i, 28))
        n += 1
        if n >= 62:
            break
    # where he lies: a dent in the snow, a rim of thrown-up snow, broken branches
    add('ico_sphere', '9CB2D0', (0, 0, 0.0), scale=(1.5, 2.6, 0.16), radius=1, subdivisions=2, parent=w, rough=1.0)
    for i in range(12):
        a = i * PI / 6
        add('ico_sphere', 'EEF4FA', (1.8 * math.cos(a), 2.9 * math.sin(a), 0.05), scale=(0.6 + 0.3 * rnd(i, 29), 0.6, 0.3 + 0.15 * rnd(i, 30)), radius=1,
            subdivisions=1, parent=w, rough=1.0)
    for i in range(7):
        a, r = 0.9 * i + 0.4, 2.6 + 1.6 * rnd(i, 31)
        add('cone', '1F4034', (r * math.cos(a), r * math.sin(a), 0.3), rot=(PI / 2 + 0.2 * rnd(i, 32), 0, 6 * rnd(i, 33)), radius1=0.6, radius2=0.0,
            depth=1.8, vertices=6, parent=w, rough=1.0)
        bar(w, '4A3424', (r * math.cos(a), r * math.sin(a), 0.2), (r * math.cos(a) + 1.2 * rnd(i, 34), r * math.sin(a) + 0.9, 0.5), 0.06)
    for i in range(6):                                                    # snapped boughs hanging in the hole above him
        a = i * 1.05 + 0.3
        bar(w, '4A3424', (3.6 * math.cos(a), 3.6 * math.sin(a), 9.5 + rnd(i, 35) * 3), (1.9 * math.cos(a + 0.3), 1.9 * math.sin(a + 0.3), 8.2 + rnd(i, 36) * 3), 0.09)
        add('cone', '1F4034', (2.4 * math.cos(a + 0.2), 2.4 * math.sin(a + 0.2), 8.6 + rnd(i, 36) * 3), rot=(1.9, 0, a), radius1=0.7, radius2=0.0,
            depth=1.9, vertices=6, parent=w, rough=1.0)
    S['twig'] = keep(bar(None, '4A3424', FAR, (FAR[0], FAR[1], FAR[2] + 1.5), 0.05))
    S['wood'] = w
    # the harness he took off
    hn = keep(empty(FAR))
    for (a, b_) in (((-0.7, 0.2, 0.05), (0.6, -0.3, 0.07)), ((-0.6, -0.35, 0.05), (0.7, 0.3, 0.09)), ((-0.75, 0.0, 0.05), (-0.2, 0.55, 0.06)),
                    ((0.2, 0.5, 0.06), (0.8, 0.1, 0.05))):
        o = add('cube', 'D8CCA4', parent=hn, size=1, rough=1.0)
        span(o, a, b_, 0.1)
        o.scale = (0.26, 0.05, o.scale[2])
    for (x, y) in ((-0.25, 0.1), (0.25, -0.08)):                          # the two folded lift webs, still tacked down
        add('cube', 'EDE4C4', (x, y, 0.14), rot=(0, 0, 0.4), scale=(0.3, 0.42, 0.12), size=1, parent=hn, rough=1.0)
        add('cube', 'C9CED6', (x + 0.02, y - 0.24, 0.16), rot=(0, 0, 0.4), scale=(0.2, 0.12, 0.07), size=1, parent=hn, rough=0.3)
    add('cylinder', 'C9CED6', (0, 0, 0.12), radius=0.16, depth=0.07, vertices=8, parent=hn, rough=0.3)
    S['harness'] = hn
    lt = keep(empty(FAR))                                                 # a storm lantern
    add('cylinder', '2A2A2E', (0, 0, -0.22), radius=0.14, depth=0.08, vertices=8, parent=lt)
    add('cylinder', 'FFD890', (0, 0, 0), radius=0.11, depth=0.36, vertices=8, parent=lt, emit=14.0)
    add('cone', '2A2A2E', (0, 0, 0.26), radius1=0.16, radius2=0.03, depth=0.16, vertices=8, parent=lt)
    S['lantern'] = lt
    S['lanlamp'] = light(FAR, 0, 'FFC878', kind='POINT')


def make_wreck(S):
    w = keep(empty(WRECK))
    add('cube', '2F3B2C', (-1.5, 2.5, 1.3), rot=(0.1, 0.12, 0.5), scale=(3.0, 9.0, 3.4), size=1, parent=w)
    add('cube', '14161A', (-1.5, 2.5, 0.3), rot=(0.1, 0.12, 0.5), scale=(3.05, 9.05, 1.4), size=1, parent=w)
    add('cube', '2F3B2C', (-5.5, 5.5, 2.4), rot=(0.5, 0.2, 0.5), scale=(0.3, 4.2, 4.6), size=1, parent=w)
    add('cube', '2F3B2C', (-3.5, 5.0, 1.0), rot=(0.2, -0.3, 0.5), scale=(7.0, 3.2, 0.3), size=1, parent=w)
    for i in range(7):
        add('ico_sphere', '0E0D0C', (-2.5 + 1.1 * i * rnd(i, 40), 0.2 + 0.8 * i, 1.0 + 1.6 * rnd(i, 41)), scale=(1.2, 1.0, 0.9), radius=0.8, subdivisions=1,
            parent=w, rough=1.0)
    for i in range(6):
        bar(w, '50565E', (1.0 + 0.5 * i, -1.5 + rnd(i, 42), 0.1), (1.6 + 0.6 * i, -0.4 + 2 * rnd(i, 43), 0.8 + rnd(i, 44)), 0.06)
    for i in range(9):
        a, r = rnd(i, 45) * 2 * PI, 16 + 30 * rnd(i, 46)
        pine(w, r * math.cos(a), 8 + abs(r * math.sin(a)), 12 + 6 * rnd(i, 47), 1.1)
    # the stowage container, on its side, lid off, the pack still in it
    c = empty((1.6, -1.6, 0.75), w, (0, 0, 0.25))
    add('cylinder', '6A727C', (0, 0.35, 0), rot=(PI / 2, 0, 0), radius=0.95, depth=1.5, vertices=10, parent=c, rough=0.5)
    add('cylinder', '0E0F12', (0, -0.38, 0), rot=(PI / 2, 0, 0), radius=0.86, depth=0.1, vertices=10, parent=c)
    add('cylinder', '6A727C', (1.9, -0.9, -0.62), radius=0.97, depth=0.1, vertices=10, parent=c, rough=0.5)        # the lid in the snow
    add('cube', '2A231C', (0, -0.42, -0.05), scale=(1.15, 0.2, 0.85), size=1, parent=c, rough=1.0)                # the pack, charred
    for x in (-0.35, 0.35):
        add('cube', '4A4034', (x, -0.53, -0.05), scale=(0.12, 0.03, 0.86), size=1, parent=c, rough=1.0)
    S['handle'] = add('cube', 'DDE2EA', (0, -0.56, 0.12), scale=(0.32, 0.05, 0.12), size=1, parent=c, rough=0.2, emit=0.0)
    add('cube', '8A929C', (0.21, -0.56, 0.12), scale=(0.05, 0.05, 0.2), size=1, parent=c, rough=0.3)
    S['wreck'] = w


# ---------------------------------------------------------------- the room and the row of stones
def make_room(S):
    r = keep(empty(ROOM))
    add('cube', '4A3A2C', (0, 0, -0.05), scale=(13, 11, 0.1), size=1, parent=r)
    for i in range(7):
        add('cube', '3A2C20', (-6 + 2 * i, 0, 0.005), scale=(0.06, 11, 0.02), size=1, parent=r)
    add('cube', '6E7466', (0, 5.0, 2.4), scale=(13, 0.15, 5.0), size=1, parent=r)
    add('cube', '6A7062', (-6.2, 0, 2.4), scale=(0.15, 11, 5.0), size=1, parent=r)
    add('cube', '6A7062', (6.2, 0, 2.4), scale=(0.15, 11, 5.0), size=1, parent=r)
    add('cube', '3E4438', (0, 4.9, 0.7), scale=(13, 0.08, 1.4), size=1, parent=r)
    add('cube', '2A2E26', (0, 4.86, 1.42), scale=(13, 0.1, 0.1), size=1, parent=r)
    add('cube', '5A5E52', (0, 0, 4.85), scale=(13, 11, 0.1), size=1, parent=r)
    # a wall map: paper, a grid, a few pins. No place names, no symbols.
    add('cube', 'D8CCA8', (1.4, 4.88, 2.9), scale=(4.2, 0.05, 2.4), size=1, parent=r, rough=1.0)
    for i in range(6):
        add('cube', '9A8E6C', (-0.4 + 0.72 * i, 4.85, 2.9), scale=(0.03, 0.03, 2.3), size=1, parent=r)
    for i in range(4):
        add('cube', '9A8E6C', (1.4, 4.85, 2.0 + 0.6 * i), scale=(4.1, 0.03, 0.03), size=1, parent=r)
    for i in range(5):
        add('ico_sphere', ('C83A2A', '2A5A9A')[i % 2], (0.0 + 0.7 * i, 4.82, 2.3 + 1.1 * rnd(i, 50)), radius=0.07, subdivisions=1, parent=r)
    add('cube', '2E2A26', (-3.6, 4.6, 1.5), scale=(1.4, 0.8, 3.0), size=1, parent=r)                                 # a filing cabinet
    for z in (0.6, 1.5, 2.4):
        add('cube', '8A8A80', (-3.6, 4.18, z), scale=(0.5, 0.04, 0.08), size=1, parent=r, rough=0.3)
    add('cube', '1A2636', (-6.1, 1.5, 2.8), scale=(0.06, 2.2, 1.8), size=1, parent=r, emit=0.6)                      # a night window
    for y in (0.4, 1.5, 2.6):
        add('cube', 'B8B4A4', (-6.05, y, 2.8), scale=(0.08, 0.08, 1.9), size=1, parent=r)
    add('cube', 'B8B4A4', (-6.05, 1.5, 2.8), scale=(0.08, 2.3, 0.08), size=1, parent=r)
    # the desk between them
    add('cube', '5A3E26', (0, 0, 1.3), scale=(1.7, 2.8, 0.1), size=1, parent=r, rough=0.5)
    add('cube', '4A321E', (0, 0, 0.64), scale=(1.45, 2.5, 1.26), size=1, parent=r)
    add('cube', '2A2A2E', (0.35, 0.9, 1.38), scale=(0.3, 0.3, 0.06), size=1, parent=r)                               # lamp foot
    bar(r, '2A2A2E', (0.35, 0.9, 1.4), (0.2, 0.75, 2.0), 0.03)
    add('cone', '2E5A44', (0.1, 0.65, 2.0), rot=(0.35, -0.35, 0), radius1=0.34, radius2=0.1, depth=0.3, vertices=8, parent=r)
    add('ico_sphere', 'FFE2A0', (0.08, 0.63, 1.95), radius=0.09, subdivisions=1, parent=r, emit=20.0)
    add('cube', '2A2420', (-0.3, -0.85, 1.4), scale=(0.5, 0.36, 0.1), size=1, parent=r)                              # a ledger
    add('cylinder', '1E1E22', (0.45, -0.9, 1.4), radius=0.12, depth=0.1, vertices=8, parent=r)                       # an ink pad
    for x in (-1.9, 1.9):
        c = empty((x, 0, 0), r, (0, 0, PI / 2 if x < 0 else -PI / 2))
        add('cube', '3A2A1C', (0, 0.05, 0.5), scale=(0.95, 0.95, 0.1), size=1, parent=c)
        add('cube', '3A2A1C', (0, 0.5, 1.25), scale=(0.95, 0.1, 1.5), size=1, parent=c)
        for (px, py) in ((-0.4, -0.35), (0.4, -0.35), (-0.4, 0.45), (0.4, 0.45)):
            add('cylinder', '2A1E14', (px, py, 0.24), radius=0.045, depth=0.5, vertices=5, parent=c)
    S['paper'] = keep(add('cube', 'F2EAD2', FAR, scale=(0.62, 0.86, 0.015), size=1, rough=1.0))
    S['pen'] = keep(bar(None, '1E1E22', FAR, (FAR[0], FAR[1], FAR[2] + 0.4), 0.025))
    S['stamp'] = keep(add('cylinder', '6A2A22', FAR, radius=0.09, depth=0.3, vertices=8))
    bar(r, '1E1E22', (0, 0.2, 4.8), (0, 0.2, 3.9), 0.02)
    add('cone', '2A2E2A', (0, 0.2, 3.85), radius1=0.6, radius2=0.12, depth=0.3, vertices=10, parent=r)
    S['deskl'] = light(at(ROOM, 0.05, 0.6, 1.85), 0, 'FFD8A0', kind='POINT')
    S['cl'] = light(at(ROOM, 0, 0.2, 3.6), 0, 'FFE4C0', 2.0)
    S['room'] = r


def make_yard(S):
    y = keep(empty(YARD))
    add('cube', '4A7248', (0, 0, -0.5), scale=(400, 400, 1.0), size=1, parent=y, rough=1.0)
    for i in range(16):
        add('cube', '3E6440', ((rnd(i, 60) - 0.5) * 40, (rnd(i, 61) - 0.5) * 30, 0.005), rot=(0, 0, rnd(i, 62)), scale=(5, 3, 0.03), size=1, parent=y, rough=1.0)
    for i in range(4):
        x = -2.4 + 1.6 * i
        add('cube', 'F1EFE8', (x, 0, 0.6), scale=(0.95, 0.2, 1.2), size=1, parent=y, rough=0.8)
        add('cylinder', 'F1EFE8', (x, 0, 1.2), rot=(PI / 2, 0, 0), radius=0.475, depth=0.2, vertices=12, parent=y, rough=0.8)
        add('cube', '6A4E36', (x, -0.5, 0.03), scale=(1.0, 0.8, 0.06), size=1, parent=y, rough=1.0)
    add('cube', '2C4A30', (0, 6, 0.9), scale=(60, 1.4, 1.8), size=1, parent=y, rough=1.0)
    for i in range(7):
        x = -24 + 8 * i + 3 * rnd(i, 63)
        add('cylinder', '4A3424', (x, 9, 2.0), radius=0.3, depth=4, vertices=6, parent=y)
        add('ico_sphere', '34583A', (x, 9, 5.6), scale=(1, 1, 1.15), radius=2.8 + rnd(i, 64), subdivisions=1, parent=y, rough=1.0)
    S['yard'] = y


# ---------------------------------------------------------------- the cast
def airman_head(head):
    d = K.human_head(SKIN, HELMET)(head)
    for s in (-1, 1):
        add('cube', HELMET, (s * 0.25, 0.02, -0.08), scale=(0.08, 0.3, 0.34), size=1, parent=head)        # ear flaps of the flying helmet
        add('cube', '1A1C20', (s * 0.11, -0.25, 0.2), rot=(-0.3, 0, 0), scale=(0.16, 0.05, 0.11), size=1, parent=head, rough=0.2)   # goggles pushed up
    add('cube', '2A2018', (0, -0.22, 0.2), rot=(-0.3, 0, 0), scale=(0.52, 0.04, 0.05), size=1, parent=head)
    return d


def hat_head(skin, hair, hat):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('cylinder', hat, (0, -0.02, 0.24), rot=(-0.08, 0, 0), radius=0.5, depth=0.04, vertices=10, parent=head)
        add('cone', hat, (0, 0.0, 0.4), radius1=0.3, radius2=0.25, depth=0.3, vertices=8, parent=head)
        add('cylinder', '0E0E12', (0, 0.0, 0.29), radius=0.31, depth=0.07, vertices=8, parent=head)
        return d
    return fn


def cap_head(skin, hair, cap):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('cube', cap, (0, 0.03, 0.3), scale=(0.56, 0.62, 0.2), size=1, parent=head)
        add('cube', cap, (0, -0.33, 0.22), rot=(0.25, 0, 0), scale=(0.44, 0.22, 0.04), size=1, parent=head)
        return d
    return fn


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_bomber(S)
    make_fighter(S)
    make_air(S)
    make_bay(S)
    make_wood(S)
    make_wreck(S)
    make_room(S)
    make_yard(S)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['man'] = m = K.Rig(dict(top=JACKET, pants='46526A', hand='5A3E24', boot='2A2018', fore=JACKET), airman_head)
    S['strap'] = []
    for s in (-1, 1):                                                      # the parachute harness over his jacket
        S['strap'].append(add('cube', 'D8CCA4', (s * 0.2, -0.375, 0.6), rot=(0, s * 0.3, 0), scale=(0.1, 0.03, 0.95), size=1, parent=m.body, rough=1.0))
        S['strap'].append(add('cube', 'C9CED6', (s * 0.24, -0.4, 0.62), scale=(0.1, 0.04, 0.12), size=1, parent=m.body, rough=0.3))   # the two chest hooks
    S['strap'].append(add('cube', 'D8CCA4', (0, -0.36, 0.3), scale=(0.72, 0.03, 0.1), size=1, parent=m.body, rough=1.0))
    add('cube', 'C8B890', (0, -0.3, 1.02), scale=(0.5, 0.2, 0.16), size=1, parent=m.body, rough=1.0)                # fleece collar
    S['band'] = add('cube', 'F2F0EA', (0, -0.02, 0.2), scale=(0.62, 0.66, 0.1), size=1, parent=m.head, rough=1.0)   # a dressing, later
    S['agents'] = [K.Rig(dict(top=c, pants='1E1E24', hand='D8B494', boot='121216', fore=c), hat_head('D8B494', h_, '1C1C22'))
                   for c, h_ in (('2A2A32', '5A4630'), ('33302C', '2A2420'))]
    S['men'] = [K.Rig(dict(top='5C6658', pants='4A5246', hand='3A3A36', boot='1A1A1C', fore='5C6658'), cap_head(sk, hr, '4E584A'))
                for sk, hr in (('D0A888', '6A5238'), ('C89C7C', '3A2E24'))]
    S['humans'] = [S['man']] + S['agents'] + S['men']
    S['cast'] = [S['rook']] + S['humans']
    S['pad'] = keep(add('cube', 'F4EED8', FAR, scale=(0.36, 0.03, 0.46), size=1, rough=1.0))
    S['fea'] = [keep(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.36, vertices=4)) for _ in range(2)]
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 9000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w24')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.05, 0.55
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs[2], mr.inputs[0])
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(mx.outputs[2], S['bg'].inputs[0])
    S['skymix'] = mx
    reset(S)
    return S


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for l in S['flamp'] + [S['sun'], S['lanlamp'], S['deskl'], S['cl']]:
        l.data.energy = 0
    for o in S['strap']:
        o.hide_render = False
    S['band'].hide_render = True
    for o in S['scorch']:
        o.hide_render = True
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, starson=False)
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinking and beak lip sync, once the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.43) % 1 < 0.035
    ez = dict(calm=0.07, low=0.042, shocked=0.135, sad=0.055, soft=0.06).get(e, 0.07)
    tilt = dict(low=-0.06, shocked=0.36, sad=0.45, soft=0.22).get(e, -0.22)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], sm(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + tip * 0.38, 0.2, off), lerp(0.07, 1.25, off), 0)
    r['hat'].location = (lerp(0.0, 0.74, off), lerp(0.0, -0.14, off), lerp(0.27 + S['hat_jump'] + tip * 0.1, -1.45, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.36 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.8, shut=0.07, tired=0.45, warm=0.8, sad=0.5, laugh=0.3, hard=0.6).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.045 if f == 'wide' else -0.02 if f in ('hard', 'tired') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide') else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.2 if f in ('warm', 'laugh') else 0.13, 0.03, 0.035 + 0.14 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sky(S, name, stars=False):
    A = SKIES[name]
    S['skymix'].inputs[6].default_value = K.hexc(A[0])
    S['skymix'].inputs[7].default_value = K.hexc(A[1])
    S['bg'].inputs[1].default_value = A[2]
    S['sun'].data.energy = A[3]
    S['sun'].data.color = K.hexc(A[4])[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(v * 500 for v in A[5])
    S['starson'] = stars


def shoot(S, o, pos, look, lens=40, roll=0.0):
    p = at(o, *pos)
    S['camrig'].location, S['camtgt'].location = p, at(o, *look)
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    S['stars'].location = p if S['starson'] else FAR


def air(S, c, t, v, land=-900.0, box=(150.0, 150.0, 110.0)):
    """Cloud layers streaming past the point c with velocity v, and the dark country far below."""
    for i, o in enumerate(S['clouds']):
        p = []
        for j in range(3):
            q = (rnd(i, 70 + j) * box[j] * 2 + v[j] * t) % (box[j] * 2) - box[j]
            p.append(q)
        if abs(p[0]) < 26:
            p[0] = 26 * (1 if i % 2 else -1) + p[0] * 0.5
        o.location = (c[0] + p[0], c[1] + p[1], c[2] + p[2])
    S['land'].location = (c[0], c[1], c[2] + land)
    S['land'].rotation_euler = (0, 0, 0.3)


def fire(S, pts, t, size=1.0, d=(0, 1, 0.3), i0=0, par=None, o=(0, 0, 0)):
    q = Vector(d).normalized().to_track_quat('Z', 'Y').to_euler()
    for j, p in enumerate(pts):
        f = S['fl'][i0 + j]
        if par is not None:
            f.parent = par
        fk = 0.75 + 0.3 * math.sin(t * 23 + j * 1.7) + 0.2 * math.sin(t * 37 + j * 0.9)
        f.location = (o[0] + p[0] + 0.12 * math.sin(t * 19 + j), o[1] + p[1] + 0.1 * math.sin(t * 13 + 2 * j), o[2] + p[2] + 0.1 * math.sin(t * 29 + 2 * j))
        f.rotation_euler = q
        s = size * (0.7 + 0.6 * rnd(j, 2))
        f.scale = (s * fk, s * fk, s * (1.1 + 0.9 * fk))
    return i0 + len(pts)


def glow(S, i, pos, watts, t):
    S['flamp'][i].location = pos
    S['flamp'][i].data.energy = watts * (0.8 + 0.2 * math.sin(t * 21 + i) + 0.12 * math.sin(t * 33))


WINGF = [(-7, -5.5, 0.7), (-8.5, -2.5, 0.7), (-12, -2, 0.6), (-5, -0.5, 0.7), (-15, -2.5, 0.6), (-1.5, 3, 1.6), (-1.3, 8, 1.7), (0.3, 12, 1.7), (-1.0, 14.3, 1.2),
         (1.3, 13, 1.0), (-10, 0, 0.8), (-7, 1.5, 0.8)]


def burning(S, t, size=2.4, n=12, watts=40000):
    b = S['bomber']
    b.location = SKYO
    b.rotation_euler = (0.02 * math.sin(t * 1.3), 0.12 + 0.03 * math.sin(t * 0.9), 0.02 * math.sin(t * 0.7))
    fire(S, WINGF[:n], t, size, (0, 1, 0.22), par=b)
    glow(S, 0, at(SKYO, -8, -1, 4), watts, t)
    glow(S, 1, at(SKYO, 0, 13, 4), watts * 0.4, t)
    return b


FALLP = dict(aL=(2.3, 0.55, 0.4), aR=(2.1, 0.7, 0.5), lL=(0.9, 0.6), lR=(0.5, 0.9), head=(-0.15, 0.0))


def falling(S, o, t, yaw=0.5, spin=0.0, face='wide'):
    """He falls on his back, arms and legs trailing above him."""
    m = S['man']
    w = math.sin(t * 5)
    m.place(o, yaw + spin, -PI / 2 + 0.25 * math.sin(t * 1.7), 0.2 * math.sin(t * 1.1))
    m.apply(P('stand', aL=(2.3 + 0.2 * w, 0.55, 0.4), aR=(2.1 - 0.2 * w, 0.7, 0.5), lL=(0.9 + 0.15 * w, 0.6), lR=(0.5 - 0.15 * w, 0.9), head=(-0.15, 0.0)))
    m.face = face
    return m


def far_bomber(S, o, t, size=3.0):
    b = S['bomber']
    b.location = o
    b.rotation_euler = (0.25, 0.5 + 0.2 * math.sin(t), 0.6 + 0.3 * t)
    fire(S, WINGF[:10], t, size, (0, 1, 0.3), par=b, i0=14)
    glow(S, 2, at(o, -6, 0, 5), 30000, t)


def rook_air(S, o, t, yaw, pose=None, flap=0.15):
    rk = S['rook']
    f = math.sin(t * 9)
    rk.place(at(o, 0, 0, 0.12 * math.sin(t * 3.1)), yaw, 0.06 * math.sin(t * 2.3), 0.05 * math.sin(t * 1.9))
    rk.apply(pose or P('stand', aL=(0.25, 1.35 + flap * f, 0.2), aR=(0.25, 1.35 + flap * f, 0.2), lL=(0.35, 0.6), lR=(-0.15, 0.5), head=(0.05, 0.0)))
    return rk


def snowburst(S, pos, u, n=14, r=3.0, h=4.0, i0=0, g=7.0):
    if u <= 0:
        return
    for i in range(n):
        a = i * 2.4 + 0.5
        q = 0.4 + 0.6 * rnd(i, 80)
        z = pos[2] + h * q * u * 2 - g * u * u
        S['snowb'][i0 + i].location = (pos[0] + r * q * u * math.cos(a), pos[1] + r * q * u * math.sin(a), max(z, pos[2] - 0.05))
        s = 1.0 + 1.6 * rnd(i, 81)
        S['snowb'][i0 + i].scale = (s, s, s)


def snowfall(S, o, t, n=10, i0=12, r=3.0, top=9.0, speed=1.6):
    for i in range(n):
        z = top - ((t * speed * (0.7 + 0.6 * rnd(i, 82)) + rnd(i, 83) * top) % top)
        a = rnd(i, 84) * 2 * PI
        q = r * rnd(i, 85)
        S['snowb'][i0 + i].location = at(o, q * math.cos(a) + 0.2 * math.sin(t * 2 + i), q * math.sin(a), z)
        S['snowb'][i0 + i].scale = (0.5, 0.5, 0.5)


def debris(S, pos, u, n=8, r=4.0, h=3.0, g=6.0, spin=5.0):
    if u <= 0:
        return
    for i in range(n):
        a = i * 1.9 + 0.3
        q = 0.4 + 0.6 * rnd(i, 86)
        S['bits'][i].location = (pos[0] + r * q * u * math.cos(a), pos[1] + r * q * u * math.sin(a), pos[2] + h * q * u * 2 - g * u * u)
        S['bits'][i].rotation_euler = (u * spin * q, u * spin, i)
        s = 1.0 + 1.5 * rnd(i, 87)
        S['bits'][i].scale = (0.5 * s, 0.16 * s, 0.12 * s)


def feather(S, pos, u):
    for i in range(2):
        if u <= 0:
            continue
        v = u * 1.2
        S['fea'][i].location = (pos[0] + (0.3 + i * 0.4) * v + 0.2 * math.sin(v * 6 + i), pos[1] - 0.3 * v, pos[2] + 0.9 * v - 0.8 * v * v)
        S['fea'][i].rotation_euler = (v * 5 + i, v * 3, i * 2.0)


def mhead(S):
    return wpos(S['man'].head)


def rhead(S):
    return wpos(S['rook'].head)


def no_harness(S, band=True):
    for o in S['strap']:
        o.hide_render = True
    S['band'].hide_render = not band


# ---------------------------------------------------------------- the hook: on fire, and he jumps
def bomber_wide(S, k, t, lt):
    """The burning bomber from behind and above its tail; a small figure rolls out of the rear turret and drops away. First and last shot."""
    kk = 1 - k if S['prm'].get('loop') else k
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0))
    burning(S, t, 2.6)
    u = sm(kk / 0.9)
    m = S['man']
    m.place((0.3 * u, 17.4 + 6.5 * u, 0.3 + 1.0 * math.sin(PI * min(1, u * 2)) * (1 - u) - 9.0 * u * u), PI, -2.6 * u, 0.3 * u)
    m.apply(P('stand', aL=(1.6, 0.7, 0.5), aR=(1.9, 0.6, 0.4), lL=(1.2 - 0.6 * u, 1.3 - 0.8 * u), lR=(1.0 - 0.6 * u, 1.4 - 0.6 * u)))
    m.face = 'wide'
    shoot(S, SKYO, (lerp(-8.5, -7.0, kk), lerp(31, 28.5, kk), lerp(4.6, 3.6, kk)), (0.0, 15.5, lerp(0.2, -2.2, kk)), 25)


def turret_fire(S, k, t, lt):
    """Close on the gunner in the open frame of the turret: fire in the fuselage behind him, he looks back at it and then out at the night."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0))
    b = burning(S, t, 2.2, 5)
    fire(S, [(0.7, 14.5, 0.2), (-0.7, 14.4, 0.8), (0.1, 14.3, 1.5), (-1.9, 15.2, 0.6), (1.9, 15.0, 0.9), (0.0, 14.6, -0.6)], t, 1.0, (0, 1, 0.7), i0=12, par=b)
    glow(S, 2, at(SKYO, 0.3, 15.2, 1.2), 2600, t)
    m = S['man']
    m.root.parent = b
    turn = 2.2 * (1 - sm(lt / 0.5))
    m.place((0, 16.2, -1.55), PI)
    m.apply(P('sit', aL=(1.1, 0.25, 0.9), aR=(1.2, 0.3, 0.7), lean=0.05, head=(-0.05, turn), lift=-0.5))
    m.face, m.jawv = 'wide', 0.3 + 0.2 * math.sin(lt * 9)
    shoot(S, SKYO, (lerp(1.5, 1.1, k), lerp(20.9, 20.2, k), lerp(1.3, 1.1, k)), (0.05, 16.2, 0.72), 36)


def chute_burn(S, k, t, lt):
    """The parachute pack in its rack, already burning. A gloved hand reaches for it and is driven back."""
    sky(S, 'room')
    g = sm(k * 1.4)
    for o in S['scorch']:
        o.hide_render = False
        o.scale = (1 + 2 * g, 0.2, 1 + 2 * g)
    fire(S, [(-0.5, -0.25, 2.0), (0.25, -0.3, 2.1), (0.7, -0.15, 1.8), (-0.95, -0.15, 1.5), (0.0, -0.35, 1.5), (-2.4, 0.3, 1.2), (-3.2, 0.2, 2.3),
             (2.6, 0.4, 0.6), (-1.8, 0.2, 0.5)], t, lerp(0.55, 0.95, g), (0.25, 0, 1), o=BAY)
    glow(S, 0, at(BAY, -0.6, -1.2, 2.0), 900, t)
    glow(S, 1, at(BAY, 1.6, -1.6, 1.0), 300, t)
    reach = sm(lt / 0.45) * (1 - sm((lt - 0.6) / 0.18))
    S['glove'].place(at(BAY, lerp(3.4, 1.55, reach), -0.75, 1.55 + 0.1 * math.sin(lt * 30) * reach), (0.2, 0.0, -PI / 2))
    S['glove'].grip(0.1 + 0.5 * (1 - reach))
    shoot(S, BAY, (lerp(1.5, 1.1, k), lerp(-5.2, -4.4, k), lerp(2.2, 1.9, k)), (0.1, 0.2, 1.55), 42)


def backflip(S, k, t, lt):
    """From beside the tail: he lets go and goes backwards out of the turret into the dark."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0))
    b = burning(S, t, 2.4)
    fire(S, [(-1.9, 15.2, 0.6), (1.7, 15.0, 1.0), (0.0, 15.3, 1.9)], t, 1.4, (0, 1, 0.4), i0=12, par=b)
    u = sm((lt - 0.15) / 0.8)
    m = S['man']
    m.place((0.0, 16.6 + 4.6 * u, -1.5 + 2.2 * math.sin(PI * min(1, u * 1.6)) * (1 - 0.5 * u) - 5.0 * u * u), PI, -2.9 * u)
    m.apply(blend(P('sit', aL=(1.1, 0.25, 0.9), aR=(1.2, 0.3, 0.7), lift=-0.5), P('stand', aL=(2.6, 0.5, 0.2), aR=(2.5, 0.6, 0.3), lL=(0.9, 0.9), lR=(0.6, 1.2)), u * 1.6))
    m.face = 'shut' if u > 0.2 else 'wide'
    shoot(S, SKYO, (lerp(-8.5, -7.5, k), lerp(22.5, 23.5, k), lerp(1.8, 0.6, k)), (0.0, 17.6 + 2.6 * u, -0.6 - 2.2 * u), 30)


# ---------------------------------------------------------------- the doubt and the fall
def rook_fall(S, k, t, lt):
    """Rook is falling beside him, wings out, hat brim low, and does not believe it. The man tumbles behind him, the bomber burns above."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 55))
    far_bomber(S, at(FALL, -17, 46, 30 + 9 * lt), t)
    falling(S, at(FALL, -2.5, 3.2, -0.6 + 0.3 * math.sin(t * 2)), t, 0.9)
    rk = rook_air(S, at(FALL, 1.0, -0.5, -0.4), t, 0.2, P('stand', aL=(0.25, 1.3 + 0.12 * math.sin(t * 9), 0.2), aR=(0.3, 1.25 - 0.12 * math.sin(t * 9), 0.3),
                                                        lL=(0.35, 0.6), lR=(-0.15, 0.5), head=(0.05, lerp(-0.9, 0.0, sm(lt / 0.5)))))
    S['rface'], S['hat_tip'] = 'low', 0.55
    shoot(S, FALL, (lerp(0.2, 0.5, k), lerp(-7.0, -6.2, k), 1.0), (0.3, 0.0, 1.75), 32)


def fighter(S, k, t, lt):
    """From below and behind: the dark twin-engined fighter under the bomber's belly, its tracer going up into the wing."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0))
    b = S['bomber']
    b.location = SKYO
    b.rotation_euler = (0, 0.04 * math.sin(t * 2), 0)
    f = S['fighter']
    f.location = at(SKYO, 6 - 2 * k, 30 - 5 * k, -17 + 2 * k)
    f.rotation_euler = (0.3, -0.1, 0.1)
    a, e = Vector(at(SKYO, 5.5 - 2 * k, 22 - 5 * k, -13.5 + 2 * k)), Vector(at(SKYO, -9, -3, 0))
    for i, o in enumerate(S['tracers']):
        p = (lt * 2.6 + i / 7) % 1
        span(o, a + (e - a) * p, a + (e - a) * min(1.0, p + 0.08), 0.1)
    hit = sm((lt - 0.25) / 0.5)
    fire(S, WINGF[:5], t, 0.5 + 2.2 * hit, (0, 1, 0.2), par=b)
    glow(S, 0, at(SKYO, -8, -2, -3), 90000 * hit + 15000 * (math.sin(lt * 40) > 0), t)
    shoot(S, SKYO, (lerp(20, 17, k), lerp(50, 46, k), lerp(-24, -22, k)), (0.0, 10.0, -5.0), 26)


def wing_fire(S, k, t, lt):
    """The wing goes up: fire bursts out of the engine and streams back along the fuselage; torn metal flies off."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0))
    g = sm(lt / 0.5)
    b = burning(S, t, 0.8 + 2.4 * g, 12, 20000 + 60000 * g)
    debris(S, at(SKYO, -8, -3, 1), lt * 1.4, 8, 5.0, 2.0, 2.0)
    for o in S['bits'][:8]:
        o.location.y += 26 * lt
    shoot(S, SKYO, (lerp(-25, -22, k), lerp(-17, -15, k), lerp(7.5, 6.0, k)), (-7.5, -1.5, 0.3), 34)


def fall_wide(S, k, t, lt):
    """From underneath: one small figure on his back in the open sky, the burning bomber turning away high above him."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 70))
    far_bomber(S, at(FALL, -8, 22, 46 + 22 * lt), t, 3.4)
    falling(S, at(FALL, 0, -1.5, 0), t, 0.3, 0.9 * lt)
    shoot(S, FALL, (lerp(5.5, 4.0, k), lerp(-8.0, -6.0, k), lerp(-6.5, -5.0, k)), (-0.4, 1.0, 3.0), 24, roll=0.15 * k)


def pad_at(S, rk, lift=0.0, spin=0.0):
    h = wpos(rk.hands[0], (0, 0, -0.5))
    S['pad'].location = (h[0] + 0.05, h[1] - 0.12, h[2] + 0.2 + lift)
    S['pad'].rotation_euler = (-0.35 + spin, 0.0 + spin * 0.6, rk.root.rotation_euler[2] + 0.2)


def rook_maths(S, k, t, lt):
    """Rook, still falling, has his notepad out and is working it through: height, speed, no parachute. He looks down, and his eyes go wide."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 70))
    falling(S, at(FALL, -3.4, 5.5, 0.5), t, 1.2)
    sc = math.sin(lt * 26)
    look = sm((lt - 0.75) / 0.25)
    rk = rook_air(S, FALL, t, 0.35, P('stand', aL=(0.95, -0.12, 1.75, 0.5), aR=(0.95 + 0.06 * sc, -0.2 + 0.05 * sc, 1.95, 0.75), lL=(0.35, 0.6), lR=(-0.15, 0.5),
                                      head=(lerp(0.5, 0.7, look), lerp(0.1, -0.5, look))))
    pad_at(S, rk)
    S['rface'] = 'shocked' if look > 0.5 else 'calm'
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.6, 1.3, k), h[1] - lerp(4.6, 4.0, k), h[2] + 0.1), (h[0] - 0.1, h[1], h[2] - 0.45), 44)


def fall_close(S, k, t, lt):
    """Close on him, on his back in the air, looking up at the stars; his eyes close."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 70))
    m = falling(S, at(FALL, 0, -1.5, 0), t * 0.5, 0.0, face='wide' if lt < 0.75 else 'tired' if lt < 1.0 else 'shut')
    m.jawv = 0.15
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.3, 0.9, k), h[1] - lerp(1.8, 1.4, k), h[2] + lerp(3.6, 3.0, k)), (h[0], h[1] - 0.15, h[2]), 48, roll=0.1 - 0.2 * k)


def rook_gives_up(S, k, t, lt):
    """Rook throws the notepad over his shoulder (it sails up and away) and pulls his hat brim down over his eyes."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 70))
    u = sm((lt - 0.2) / 0.3)
    v = sm((lt - 0.45) / 0.3)
    hold = P('stand', aL=(0.95, -0.12, 1.75, 0.5), aR=(0.9, -0.2, 1.9, 0.75), lL=(0.35, 0.6), lR=(-0.15, 0.5), head=(0.6, -0.3))
    toss = P('stand', aL=(2.9, 0.4, 0.3), aR=(0.3, 1.3, 0.3), lL=(0.35, 0.6), lR=(-0.15, 0.5), head=(-0.1, 0.0))
    brim = P('hat', aL=(0.3, 1.2, 0.4), lL=(0.35, 0.6), lR=(-0.15, 0.5))
    rk = rook_air(S, FALL, t, -0.3, blend(blend(hold, toss, u), brim, v))
    pad_at(S, rk, 9.0 * max(0.0, lt - 0.3), 9.0 * max(0.0, lt - 0.3))
    S['rface'], S['hat_tip'] = 'low', 1.5 * v
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] - lerp(1.3, 1.0, k), h[1] - lerp(4.4, 3.8, k), h[2] + 0.2), (h[0], h[1], h[2] - 0.3), 46)


def trees_rush(S, k, t, lt):
    """Straight down: a dark pine wood under snow, coming up fast."""
    sky(S, 'wood')
    z = lerp(210, 30, k ** 1.4)
    shoot(S, WOOD, (0.8 + 2 * math.sin(lt * 7), -1.2 + 2 * math.cos(lt * 6), z), (0.0, 0.0, 0.0), 20, roll=0.9 * k)


# ---------------------------------------------------------------- the wood
REST = (0.0, -1.55, 0.42)
LIE = dict(aL=(0.25, 1.15, 0.3), aR=(0.3, 0.9, 0.5), lL=(0.12, 0.2), lR=(-0.08, 0.3), head=(0.0, 0.0))


def lying(S, face='shut', pose=None, dz=0.0):
    m = S['man']
    m.place(at(WOOD, REST[0], REST[1], REST[2] + dz), 0.0, -PI / 2)
    m.apply(P('stand', **(pose or LIE)))
    m.face = face
    return m


def crash_branches(S, k, t, lt):
    """Through the young pines: branches snap and fly, and he goes into the drift in a burst of snow."""
    sky(S, 'wood')
    u = min(1.0, lt / 0.5)
    z = lerp(24.0, 0.0, u ** 1.5)
    m = lying(S, 'shut', dict(aL=(2.0, 0.8, 0.5), aR=(1.7, 0.9, 0.6), lL=(0.8, 0.7), lR=(0.4, 0.9), head=(0, 0)) if u < 1 else None, z)
    m.root.rotation_euler[0] = -PI / 2 + 0.5 * (1 - u) * math.sin(lt * 20)
    debris(S, at(WOOD, 0, 0, lerp(13, 6, min(1, lt / 0.4))), lt - 0.12, 8, 5.0, 2.5, 9.0)
    snowburst(S, at(WOOD, 0, 0, 0.3), lt - 0.5, 20, 4.5, 5.5)
    shoot(S, WOOD, (lerp(2.5, 1.8, k), lerp(-17.0, -14.5, k), lerp(2.6, 2.0, k)), (0.0, 0.0, lerp(9.0, 2.6, sm(lt / 0.55))), 24)


def snow_hole(S, k, t, lt):
    """From above: he lies on his back in a man-sized dent in the snow, broken boughs round him. Snow sifts down. His eyes open."""
    sky(S, 'wood')
    m = lying(S, 'shut' if lt < 0.8 else 'wide')
    m.jawv = 0.3 * sm((lt - 0.8) / 0.2)
    snowfall(S, WOOD, t, 12, 0, 2.8, 8.0, 2.4)
    shoot(S, WOOD, (0.5, lerp(-1.6, -1.1, k), lerp(11.0, 8.2, k)), (0.0, 0.1, 0.4), 30, roll=lerp(0.25, 0.0, k))


def hole_up(S, k, t, lt):
    """What he sees: a ring of pine tops, a ragged hole, stars. Snow drifts down through it. Rook's head comes in over the edge, staring."""
    sky(S, 'wood', True)
    lying(S, 'wide')
    snowfall(S, WOOD, t, 14, 0, 2.6, 12.0, 2.2)
    u = sm((lt - 0.25) / 0.4)
    rk = S['rook']
    rk.place(at(WOOD, 0.25, lerp(5.2, 3.3, u), 0.0), 0.0)
    rk.apply(P('stand', aL=(0.5, 0.3, 0.4), aR=(0.5, 0.3, 0.4), lean=0.75, head=(0.7, 0.0)))
    S['rface'] = 'shocked'
    S['hat_jump'] = 0.25 * max(0.0, math.sin((lt - 0.6) * 9)) if 0.6 < lt < 0.95 else 0.0
    shoot(S, WOOD, (0.3, 0.4, 1.0), (0.3 + 0.3 * math.sin(lt), lerp(0.5, 0.9, k), 30.0), 17)
    S['cam'].rotation_euler = (0, 0, PI)


def rook_measure(S, k, t, lt):
    """Detective work: Rook pushes a stick into the drift beside him, marks the depth with a wingtip, then points up at the hole in the trees."""
    sky(S, 'wood')
    m = lying(S, 'wide', dict(LIE, head=(0.0, -0.5)))
    u = sm(lt / 0.5)
    v = sm((lt - 0.8) / 0.35)
    S['twig'].location = at(WOOD, 2.2, -1.3, lerp(1.5, 0.45, u))
    S['twig'].rotation_euler = (0.08, 0.05, 0)
    rk = S['rook']
    rk.place(at(WOOD, 3.1, -0.7, 0.0), facing((3.1, -0.7), (1.0, -1.6)))
    crouch = P('stand', aR=(1.0, 0.2, 0.5), aL=(0.3, 0.2, 0.6), lL=(1.1, 1.7), lR=(1.1, 1.7), lift=-0.5, lean=0.4, head=(0.35, 0.0))
    up = P('reach', aR=(2.75, 0.2, 0.05), lL=(0.2, 0.3), lR=(0.1, 0.2), lift=-0.05, head=(-0.55, 0.3))
    rk.apply(blend(crouch, up, v))
    S['rface'] = 'shocked' if v > 0.5 else 'calm'
    shoot(S, WOOD, (lerp(4.2, 3.6, k), lerp(-8.5, -7.6, k), lerp(1.7, 1.5, k)), (1.5, -0.8, lerp(1.2, 1.7, v)), 30)


def sat(S, lift=-0.95, pose=None, x=0.0, y=0.5, yaw=0.0):
    m = S['man']
    m.place(at(WOOD, x, y, 0.25), yaw)
    d = dict(lL=(1.45, 0.25), lR=(1.4, 0.4), aL=(0.4, 0.3, 0.6), aR=(0.4, 0.3, 0.6), lift=lift, lean=0.12, head=(0.1, 0.0))
    d.update(pose or {})
    m.apply(P('stand', **d))
    return m


def limbs(S, k, t, lt):
    """He sits up in the dent, holds his hands up in front of his face, opens and shuts them, pats down his legs. Everything works."""
    sky(S, 'wood')
    u = sm(lt / 0.35)
    f = math.sin(lt * 9)
    pat = sm((lt - 0.9) / 0.3)
    m = sat(S, -0.95, dict(aL=(lerp(0.4, 1.25, u) - 0.6 * pat, 0.25, 1.3 + 0.25 * f - 0.9 * pat), aR=(lerp(0.4, 1.3, u) - 0.5 * pat, 0.25, 1.3 - 0.25 * f - 0.9 * pat),
                           lean=lerp(-0.5, 0.15, u) + 0.2 * pat, head=(0.25 + 0.3 * pat, 0.25 * math.sin(lt * 3))))
    m.face, m.jawv = 'wide', 0.35
    snowfall(S, WOOD, t, 10, 0, 3.0, 7.0, 1.6)
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.1, 0.8, k), h[1] - lerp(5.4, 4.6, k), h[2] + 0.25), (h[0], h[1], h[2] - 0.45), 42)


def knee(S, k, t, lt):
    """He gets up; one knee gives and he goes back down into the snow, wincing. Rook, beside him, flinches and half reaches out."""
    sky(S, 'wood')
    up = sm(lt / 0.5)
    dn = sm((lt - 0.6) / 0.22)
    lift = lerp(-0.95, -0.05, up) - 0.62 * dn
    m = sat(S, lift, dict(lL=(lerp(1.45, 0.1, up) + 0.9 * dn, lerp(0.25, 0.1, up) + 1.6 * dn), lR=(lerp(1.4, 0.0, up) + 0.3 * dn, lerp(0.4, 0.05, up) + 0.9 * dn),
                          aL=(0.5 + 0.5 * dn, 0.5, 0.6), aR=(0.5 + 0.7 * dn, 0.5, 0.8), lean=0.1 + 0.3 * dn, head=(0.1 + 0.3 * dn, 0.0)), x=0.3, y=0.3, yaw=0.35)
    m.face = 'shut' if dn > 0.3 else 'calm'
    m.jawv = 0.5 * dn
    snowburst(S, at(WOOD, 0.5, -0.2, 0.2), lt - 0.72, 8, 1.6, 1.4)
    rk = S['rook']
    rk.place(at(WOOD, 2.6, 0.9, 0.0), facing((2.6, 0.9), (0.3, 0.3)))
    rk.apply(blend(P('stand', head=(0.1, 0.0)), P('stand', aL=(1.2, 0.3, 0.5), aR=(1.3, 0.3, 0.4), lean=0.2, lL=(0.3, 0.4), head=(0.2, 0.0)), dn))
    S['rface'] = 'shocked' if dn > 0.3 else 'calm'
    S['hat_jump'] = 0.18 * dn * (1 - sm((lt - 0.95) / 0.3))
    shoot(S, WOOD, (lerp(3.4, 2.9, k), lerp(-8.2, -7.4, k), 1.7), (1.3, 0.4, 1.75), 32)


def lantern(S, k, t, lt):
    """Over his shoulder: two men in caps come through the trees with a lantern, and stop when its light finds him."""
    sky(S, 'wood')
    m = sat(S, -0.95, dict(aR=(2.4 * sm(lt / 0.5), 0.5, 0.3), head=(-0.1, 0.0)), x=0.2, y=0.4)
    m.face = 'tired'
    for i, rig in enumerate(S['men']):
        y = lerp(-17 - 2 * i, -8.5 - 1.5 * i, sm(k * 1.15))
        x = -1.6 + 3.0 * i
        rig.place(at(WOOD, x, y, 0), PI)
        mv = 1 - sm((k - 0.7) / 0.25)
        rig.apply(blend(P('stand', aR=(1.5, 0.2, 0.5) if i == 0 else (0.1, 0.2, 0.2), head=(0.1, 0.0)), K.walk(t, 1.5), mv * 0.999) if i else
                  P('stand', aR=(1.5, 0.25, 0.5), lL=(0.5 * math.sin(t * 9) * mv, 0.4 * mv), lR=(-0.5 * math.sin(t * 9) * mv, 0.4 * mv), head=(0.1, 0.0)))
        rig.face = 'wide'
    h = wpos(S['men'][0].hands[1], (0, 0, -1.6))
    S['lantern'].location = h
    S['lanlamp'].location = (h[0], h[1] + 0.5, h[2] + 0.2)
    S['lanlamp'].data.energy = 2600 + 300 * math.sin(t * 17)
    shoot(S, WOOD, (lerp(1.9, 1.5, k), lerp(5.6, 4.8, k), lerp(2.3, 2.1, k)), (0.2, -4.0, 1.5), 30)


# ---------------------------------------------------------------- the room
def room(S, t, lampk=1.0):
    sky(S, 'room')
    S['deskl'].data.energy = 900 * lampk * (0.97 + 0.03 * math.sin(t * 31))
    S['cl'].data.energy = 420
    S['cl'].rotation_euler = (0, 0, 0)
    no_harness(S)


SIT = dict(lL=(1.45, 1.55), lR=(1.45, 1.55), lift=-0.5)


def man_chair(S, pose=None, face='calm'):
    m = S['man']
    m.place(at(ROOM, -1.95, 0, 0), PI / 2)
    d = dict(SIT, aL=(0.75, -0.05, 1.2, 0.8), aR=(0.75, -0.05, 1.2, 0.8), lean=0.1, head=(0.05, 0.0))
    d.update(pose or {})
    m.apply(P('stand', **d))
    m.face = face
    return m


def agent_chair(S, rig, pose=None, face='hard'):
    rig.place(at(ROOM, 1.95, 0, 0), -PI / 2)
    d = dict(SIT, aL=(0.9, 0.1, 1.0, 0.6), aR=(0.9, 0.1, 1.0, 0.6), lean=0.15, head=(0.05, 0.0))
    d.update(pose or {})
    rig.apply(P('stand', **d))
    rig.face = face
    return rig


def agent_stand(S, pose=None, face='hard'):
    b = S['agents'][1]
    b.place(at(ROOM, 3.1, 1.9, 0), facing((3.1, 1.9), (-1.9, 0)))
    b.apply(pose or P('cross', head=(0.1, 0.0)))
    b.face = face
    return b


RK_ROOM = (-3.9, 2.4)


def rook_corner(S, pose=None, yaw=None):
    rk = S['rook']
    rk.place(at(ROOM, RK_ROOM[0], RK_ROOM[1], 0), facing(RK_ROOM, (0.5, -1.5)) if yaw is None else yaw)
    rk.apply(pose or P('cross', head=(0.08, 0.0)))
    return rk


def room_wide(S, k, t, lt):
    """The room: a desk under a lamp, a man in a hat behind it and another standing, the airman on a chair with a dressing round his head.
    Rook stands in the corner with his arms folded."""
    room(S, t)
    man_chair(S, dict(head=(0.05, 0.15 * math.sin(lt * 2))))
    agent_chair(S, S['agents'][0], dict(aR=(0.9, 0.1, 1.0 + 0.3 * math.sin(lt * 6), 0.6), lean=0.3))
    agent_stand(S, P('cross', head=(0.1, 0.3 * math.sin(lt * 1.8))))
    rook_corner(S, P('cross', head=(0.08, 0.3 * math.sin(lt * 2.2))))
    S['rface'], S['hat_tip'] = 'low', 0.3
    shoot(S, ROOM, (lerp(-2.6, -0.8, k), lerp(-8.6, -7.4, k), lerp(2.7, 2.3, k)), (0.0, 0.6, 1.75), 26)


def gestapo_laugh(S, k, t, lt):
    """Close on the man behind the desk: he throws himself back in his chair and laughs; the one standing behind him laughs too."""
    room(S, t)
    man_chair(S)
    sh = math.sin(lt * 21)
    back = sm(lt / 0.3)
    a = agent_chair(S, S['agents'][0], dict(lean=lerp(0.15, -0.3, back) + 0.04 * sh, aL=(0.6, 0.5, 1.2), aR=(0.9 + 0.5 * back, 0.6, 0.6 + 0.3 * sh), head=(-0.25 * back + 0.06 * sh, 0.5)),
                    'laugh')
    a.jawv = 0.5 + 0.5 * abs(sh)
    b = agent_stand(S, P('hips', lean=-0.1 + 0.04 * sh, head=(-0.15 + 0.06 * sh, 0.1)), 'laugh')
    b.jawv = 0.4 + 0.5 * abs(math.sin(lt * 19 + 1))
    h = wpos(a.head)
    shoot(S, (0, 0, 0), (h[0] - lerp(2.9, 2.4, k), h[1] - lerp(2.6, 2.2, k), h[2] + 0.15), (h[0] + 0.25, h[1] + 0.3, h[2] - 0.05), 40)


def rook_room(S, k, t, lt):
    """Rook in his corner by the cabinet: arms folded, hat brim down, nodding along with them. He does not believe it either."""
    room(S, t)
    man_chair(S)
    nod = 0.16 * math.sin(lt * 8)
    rk = rook_corner(S, P('cross', head=(0.12 + nod, lerp(0.5, -0.35, sm(lt / 0.9)))), yaw=facing(RK_ROOM, (-1.0, -2.5)))
    S['rface'], S['hat_tip'] = 'low', 0.7
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.7, 1.4, k), h[1] - lerp(4.3, 3.7, k), h[2] - 0.2), (h[0] + 0.1, h[1], h[2] - 0.4), 42)


def spy_point(S, k, t, lt):
    """Over the airman's shoulder: the man in the hat is on his feet, bangs the desk and points straight at him."""
    room(S, t)
    man_chair(S, dict(lean=0.05))
    up = sm(lt / 0.25)
    pt = sm((lt - 0.3) / 0.2)
    a = S['agents'][0]
    a.place(at(ROOM, 1.75, 0, 0), -PI / 2)
    a.apply(blend(P('stand', aL=(0.9, 0.2, 0.3), aR=(0.9, 0.2, 0.3), lean=0.45 * up, head=(-0.1, 0.0)),
                  P('point', aR=(1.35, 0.05, 0.05), aL=(0.9, 0.2, 0.3), lean=0.4, head=(-0.1, 0.0)), pt))
    a.face, a.jawv = 'hard', 0.3 + 0.4 * abs(math.sin(lt * 14))
    agent_stand(S, P('hips', head=(0.1, 0.0)))
    shoot(S, ROOM, (lerp(-4.4, -3.9, k), lerp(-1.7, -1.5, k), lerp(2.75, 2.6, k)), (1.2, 0.15, 2.05), 34)


def he_points(S, k, t, lt):
    """Close on the airman: he leans in and points past them, level and sure. Behind him Rook unfolds his arms and tilts his head."""
    room(S, t)
    u = sm(lt / 0.4)
    m = man_chair(S, dict(aR=(lerp(0.75, 1.5, u), lerp(-0.05, 0.1, u), lerp(1.2, 0.1, u), 0.0), lean=lerp(0.1, 0.32, u), head=(0.0, 0.25 * (1 - u))), 'hard' if u < 0.3 else 'calm')
    m.jawv = 0.3 + 0.3 * abs(math.sin(lt * 11))
    v = sm((lt - 0.5) / 0.4)
    rook_corner(S, blend(P('cross', head=(0.1, 0.0)), P('think', head=(0.05, 0.35)), v), yaw=facing(RK_ROOM, (-0.5, -3.0)))
    S['rface'], S['hat_tip'] = ('calm' if v > 0.5 else 'low'), 0.5 * (1 - v)
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(2.6, 2.2, k), h[1] - lerp(3.4, 3.0, k), h[2] + 0.1), (h[0] - 0.25, h[1] + 0.2, h[2] - 0.3), 40)


def officer_writes(S, k, t, lt):
    """Later, at the same desk: a man in a cap writes it out, signs and stamps it. The airman watches; Rook leans in over the desk to read."""
    room(S, t)
    man_chair(S, dict(lean=0.2, head=(0.3, 0.0)))
    st = sm((lt - 1.0) / 0.2)
    w = math.sin(lt * 24) * (1 - st)
    o = agent_chair(S, S['men'][0], dict(aR=(1.05 + 0.03 * w, -0.25 + 0.05 * w, 0.75, 0.3), aL=(0.95, -0.2, 0.8, 0.5), lean=0.42, head=(0.5, 0.0)), 'calm')
    S['paper'].location = at(ROOM, 0.15, -0.1, 1.36)
    S['paper'].rotation_euler = (0, 0, 0.12)
    hp = wpos(o.hands[1], (0, 0, -0.6))
    S['pen'].location = (hp[0], hp[1], hp[2] + 0.22) if st < 0.5 else FAR
    S['pen'].rotation_euler = (0.4, 0.3, 0)
    S['stamp'].location = at(ROOM, 0.2, -0.3, 1.52 + 0.9 * (1 - st) + 0.25 * sm((lt - 1.25) / 0.2)) if lt > 0.85 else FAR
    rk = S['rook']
    rk.place(at(ROOM, -0.3, 2.3, 0), facing((-0.3, 2.3), (0.1, 0)))
    rk.apply(P('stand', aL=(0.6, 0.2, 0.5), aR=(0.6, 0.2, 0.5), lean=0.5, head=(0.55, 0.15 * math.sin(lt * 3))))
    S['rface'] = 'calm' if st < 0.5 else 'shocked'
    shoot(S, ROOM, (lerp(-0.6, -0.2, k), lerp(-4.4, -3.8, k), lerp(3.7, 3.3, k)), (0.1, 0.3, 1.7), 30)


def man_smile(S, k, t, lt):
    """The airman holds the sheet in both hands and reads it, and for the first time something like a smile."""
    room(S, t)
    m = man_chair(S, dict(aL=(1.0, -0.15, 1.35, 0.5), aR=(1.0, -0.15, 1.35, 0.5), head=(lerp(0.45, 0.1, sm((lt - 0.6) / 0.4)), 0.0), lean=0.12), 'calm' if lt < 0.6 else 'warm')
    hl, hr = wpos(m.hands[0], (0, 0, -0.5)), wpos(m.hands[1], (0, 0, -0.5))
    S['paper'].location = ((hl[0] + hr[0]) / 2 + 0.05, (hl[1] + hr[1]) / 2, (hl[2] + hr[2]) / 2 + 0.2)
    S['paper'].rotation_euler = (1.15, 0, PI / 2)
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(3.0, 2.5, k), h[1] - lerp(1.7, 1.4, k), h[2] + 0.2), (h[0] + 0.2, h[1], h[2] - 0.35), 44)


def rook_hat(S, k, t, lt):
    """Rook has the sheet now. He reads down it, and his hat leaves his head; a feather comes loose."""
    room(S, t)
    rk = S['rook']
    rk.place(at(ROOM, -0.3, 2.3, 0), 0.25)
    rk.apply(P('stand', aL=(1.05, -0.15, 1.5, 0.5), aR=(1.05, -0.15, 1.5, 0.5), head=(lerp(0.4, 0.55, sm(lt / 0.5)), 0.0)))
    hl, hr = wpos(rk.hands[0], (0, 0, -0.5)), wpos(rk.hands[1], (0, 0, -0.5))
    S['paper'].location = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2 - 0.05, (hl[2] + hr[2]) / 2 + 0.25)
    S['paper'].rotation_euler = (1.2, 0, 0.25)
    pop = sm((lt - 0.55) / 0.12)
    S['rface'] = 'shocked' if pop > 0.3 else 'calm'
    S['hat_jump'] = 0.55 * pop * (0.6 + 0.4 * abs(math.cos((lt - 0.55) * 7))) * (1 - sm((lt - 1.3) / 0.3))
    h = rhead(S)
    feather(S, (h[0] + 0.3, h[1], h[2] + 0.2), lt - 0.6)
    shoot(S, (0, 0, 0), (h[0] - lerp(1.5, 1.2, k), h[1] - lerp(4.5, 3.8, k), h[2] + 0.1), (h[0], h[1], h[2] - 0.3), 42)


# ---------------------------------------------------------------- the proof
def search_wood(S, k, t, lt):
    """Grey daylight in the same wood: two men in caps wade through the snow towards the dent. Rook is already there, pointing down at it."""
    sky(S, 'day')
    for i, rig in enumerate(S['men']):
        y = lerp(-13 - 2.5 * i, -7.0 - 2.0 * i, k)
        rig.place(at(WOOD, -1.2 + 2.6 * i, y, 0), PI + 0.1 * (1 - 2 * i))
        rig.apply(K.walk(t + i * 0.3, 1.5))
        rig.face = 'calm'
    rk = S['rook']
    rk.place(at(WOOD, 2.7, -0.2, 0.0), facing((2.7, -0.2), (0.5, -6)))
    rk.apply(blend(P('stand', head=(0.0, 0.5)), P('point', aR=(0.75, 0.35, 0.1), head=(0.3, -0.3)), lt / 0.45))
    S['harness'].location = at(WOOD, 1.2, -2.6, 0.06)
    shoot(S, WOOD, (lerp(7.2, 6.4, k), lerp(-2.2, -2.6, k), lerp(1.5, 1.3, k)), (0.2, -3.0, 1.5), 26)


def harness(S, k, t, lt):
    """Close in the snow: the harness he took off. A gloved hand lifts a strap: the two lift webs are still folded and tacked down. Rook
    bends in beside it and taps his beak."""
    sky(S, 'day')
    S['harness'].location = at(WOOD, 1.2, -2.6, 0.06)
    S['harness'].rotation_euler = (0, 0, 0.3)
    u = sm(lt / 0.5)
    S['glove'].root.scale = (1.3, 1.3, 1.3)
    S['glove'].place(at(WOOD, lerp(-1.2, 0.35, u), -2.75, 0.55 + 0.12 * math.sin(lt * 3)), (-0.5, 0.0, PI / 2))
    S['glove'].grip(0.25 + 0.5 * u)
    rk = S['rook']
    rk.place(at(WOOD, 2.9, -1.3, 0.0), facing((2.9, -1.3), (1.4, -3.4)))
    tap = 0.12 * max(0.0, math.sin(lt * 14))
    rk.apply(P('tap', aR=(1.25 + tap, -0.25, 2.2, 0.6), lL=(1.0, 1.6), lR=(1.0, 1.6), lift=-0.48, lean=0.5, head=(0.4, -0.1)))
    S['rface'] = 'calm'
    shoot(S, WOOD, (lerp(1.5, 1.7, k), lerp(-6.6, -5.9, k), lerp(1.7, 1.45, k)), (1.75, -2.3, 0.75), 38)


def at_wreck(S, t):
    sky(S, 'day')
    for i, o in enumerate(S['smoke']):
        z = (t * 0.9 + i * 0.7) % 5.0
        o.location = at(WRECK, -2.5 + 0.9 * i + 0.3 * math.sin(t + i), 2.0 + 0.5 * i, 2.6 + z)
        s = 0.8 + 0.5 * z
        o.scale = (s, s, s)


def wreck(S, k, t, lt):
    """A snowfield, the burnt tail of the bomber, thin smoke. One man kneels at the parachute container lying open in the snow; the other looks on."""
    at_wreck(S, t)
    a, b = S['men']
    a.place(at(WRECK, 1.4, -3.6, 0), 0.15)
    a.apply(P('stand', aL=(1.0, 0.2, 0.7), aR=(1.2 + 0.2 * math.sin(lt * 5), 0.2, 0.5), lL=(1.3, 1.9), lR=(0.2, 1.5), lift=-0.52, lean=0.4, head=(0.3, 0.0)))
    b.place(at(WRECK, 4.2, -3.0, 0), facing((4.2, -3.0), (1.6, -1.8)))
    b.apply(P('hips', head=(0.3, 0.2 * math.sin(lt * 2))))
    shoot(S, WRECK, (lerp(7.5, 6.3, k), lerp(-10.5, -9.0, k), lerp(2.8, 2.3, k)), (0.6, 0.0, 1.5), 28)


def chute_pack(S, k, t, lt):
    """The breath before: inside the container, the parachute pack, charred, never opened, its metal ripcord handle still in its pocket."""
    at_wreck(S, t)
    S['handle'].material_slots[0].material.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0.0
    S['glove'].root.scale = (1.3, 1.3, 1.3)
    S['glove'].place(at(WRECK, lerp(3.4, 2.75, sm(lt / 0.6)), -2.75, 1.0), (0.0, 0.0, -PI / 2 + 0.3))
    S['glove'].grip(0.75)
    shoot(S, WRECK, (lerp(2.5, 2.2, k), lerp(-5.4, -4.6, k), lerp(1.5, 1.25, k)), (1.62, -2.0, 0.78), 46)


# ---------------------------------------------------------------- the ending
def four_stones(S, k, t, lt):
    """Four plain white headstones in a row, early light. Rook stands beside them with his hat off and his head down."""
    sky(S, 'dawn')
    rk = S['rook']
    rk.place(at(YARD, 3.9, -0.9, 0), facing((3.9, -0.9), (0.0, 0.2)))
    rk.apply(P('stand', head=(lerp(0.15, 0.45, sm(lt / 0.8)), 0.0), aR=(0.1, 0.25, 0.3)))
    S['rface'], S['hat_off'] = 'sad', 1.0
    shoot(S, YARD, (lerp(4.6, 3.6, k), lerp(-8.2, -7.6, k), lerp(1.8, 1.6, k)), (0.9, 0.0, 1.35), 30)


def signoff(S, k, t, lt):
    """Dawn in the pine wood, under the hole in the trees. Rook puts his hat back on, pulls the brim down and looks up through it."""
    sky(S, 'dawn')
    snowfall(S, WOOD, t, 10, 0, 4.0, 8.0, 1.2)
    on = sm(lt / 0.5)
    rk = S['rook']
    rk.place(at(WOOD, 1.2, -3.2, 0.0), 0.3)
    rk.apply(blend(P('stand', head=(0.2, 0.0)), blend(P('hat'), P('stand', head=(-0.45, 0.0)), (lt - 0.7) / 0.35), on))
    S['rface'], S['hat_off'] = 'soft', 1.0 - on
    S['hat_tip'] = 0.6 * sm((lt - 0.45) / 0.2) * (1 - sm((lt - 0.75) / 0.3))
    shoot(S, WOOD, (lerp(2.6, 2.1, k), lerp(-9.0, -7.6, k), lerp(1.4, 1.6, k)), (1.1, -3.0, lerp(2.2, 2.6, k)), 34)


def photo_snow(S, k, t, lt):
    """For the case board: the man in the dent in the snow, seen from above."""
    sky(S, 'wood')
    lying(S, 'wide')
    shoot(S, WOOD, (0.5, -1.3, 8.6), (0.0, 0.1, 0.4), 30)


SHOTS3D = {f.__name__: f for f in (
    bomber_wide, turret_fire, chute_burn, backflip, rook_fall, fighter, wing_fire, fall_wide, rook_maths, fall_close, rook_gives_up, trees_rush,
    crash_branches, snow_hole, hole_up, rook_measure, limbs, knee, lantern, room_wide, gestapo_laugh, rook_room, spy_point, he_points, officer_writes,
    man_smile, rook_hat, search_wood, harness, wreck, chute_pack, four_stones, signoff)}
STILLS = dict(snow=photo_snow)
