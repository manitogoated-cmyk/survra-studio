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
CAMFILL = {'*': 200, 'bomber_wide': 6000, 'turret_fire': 110, 'chute_burn': 70, 'backflip': 500, 'rook_fall': 420, 'fighter': 9000,
           'wing_fire': 5000, 'fall_wide': 500, 'rook_maths': 320, 'fall_close': 260, 'rook_gives_up': 320, 'trees_rush': 0,
           'crash_branches': 900, 'snow_hole': 400, 'hole_up': 500, 'rook_measure': 700, 'limbs': 320, 'knee': 600, 'lantern': 260,
           'room_wide': 500, 'gestapo_laugh': 120, 'rook_room': 220, 'spy_point': 260, 'he_points': 160, 'officer_writes': 320,
           'man_smile': 120, 'rook_hat': 200, 'search_wood': 0, 'harness': 60, 'wreck': 0, 'chute_pack': 40, 'four_stones': 500, 'signoff': 80}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'E2B48C'
JACKET, HELMET = '6E5434', '4A3422'
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    night=('1E3C5E', '060C1C', 0.9, 4.0, 'A8C8F0', (-0.45, -0.35, 0.82)),
    wood=('2A4A70', '0A1428', 1.1, 3.0, 'B4D0F4', (-0.35, -0.5, 0.8)),
    day=('D6DEE6', '94A6BC', 1.5, 2.6, 'F6F2EA', (0.35, -0.5, 0.78)),
    dawn=('F4B88E', '4C6E9E', 1.3, 2.6, 'FFC8A0', (0.75, -0.55, 0.22)),
    up=('3A5E8C', '14284A', 1.4, 3.0, 'B4D0F4', (-0.35, -0.5, 0.8)),
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
    G, U, D = '4A5A44', '1E2228', '26323E'
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
            for j in range(3):
                add('cube', '15171B', (s * x, -10.05, 0.0), rot=(0, j * PI / 3, 0), scale=(5.4, 0.08, 0.34), size=1, parent=b)
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
    C = '3A4654'
    add('cube', C, (0, 0, 0), scale=(1.5, 16, 1.7), size=1, parent=f)
    add('cube', '2C3640', (0, -5.5, 0.9), scale=(1.2, 4, 0.8), size=1, parent=f, rough=0.3)
    add('cube', C, (0, -1.5, -0.1), scale=(24, 4.2, 0.35), size=1, parent=f)
    add('cube', C, (0, 7.2, 0.5), scale=(8, 2.0, 0.25), size=1, parent=f)
    add('cube', C, (0, 7.4, 1.6), scale=(0.25, 2.6, 2.6), size=1, parent=f)
    for s in (-1, 1):
        add('cylinder', '15181C', (s * 3.6, -3.4, -0.2), rot=(PI / 2, 0, 0), radius=0.9, depth=5.0, vertices=8, parent=f)
        for j in range(3):
            add('cube', '15171B', (s * 3.6, -6.1, -0.2), rot=(0, j * PI / 3, 0), scale=(4.4, 0.08, 0.3), size=1, parent=f)
    S['fighter'] = f


def make_air(S):
    S['clouds'] = [keep(add('ico_sphere', '34465E', FAR, scale=(16 + 22 * rnd(i, 1), 20 + 26 * rnd(i, 2), 3 + 4 * rnd(i, 3)), radius=1,
                            subdivisions=2, rough=1.0)) for i in range(16)]
    ld = keep(empty(FAR))
    add('cube', '0C1719', (0, 0, 0), scale=(9000, 9000, 1), size=1, parent=ld, rough=1.0)
    for i in range(46):
        col = ('16262C', '0F1E1E', '1B2C34')[i % 3]
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
    S['fl'] = [keep(add('cone', ('FF5A00', 'FF9A10', 'FF3800')[i % 3], FAR, radius1=0.55, radius2=0.0, depth=2.2, vertices=5,
                        emit=(2.4, 3.2, 2.0)[i % 3])) for i in range(30)]
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
            add('cone', 'DDE8F4', (0, 0, z + 0.075 * h), radius1=rad * 0.84, radius2=0.0, depth=h * 0.3, vertices=7, parent=r, rough=1.0)
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
    S['paper'] = keep(add('cube', 'F2EAD2', FAR, scale=(0.5, 0.7, 0.015), size=1, rough=1.0))
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
        add('cube', 'F1EFE8', (x, 0, 1.27), scale=(0.7, 0.2, 0.16), size=1, parent=y, rough=0.8)
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
    S['band'] = add('cube', 'F2F0EA', (0, 0.0, 0.215), scale=(0.6, 0.64, 0.07), size=1, parent=m.head, rough=1.0)   # a dressing, later
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


def air(S, c, t, v, land=-900.0, box=(150.0, 150.0, 110.0), top=None):
    """Cloud layers streaming past the point c with velocity v, and the dark country far below."""
    for i, o in enumerate(S['clouds']):
        p = []
        for j in range(3):
            q = (rnd(i, 70 + j) * box[j] * 2 + v[j] * t) % (box[j] * 2) - box[j]
            p.append(q)
        if abs(p[0]) < 26:
            p[0] = 26 * (1 if i % 2 else -1) + p[0] * 0.5
        if top is not None:
            p[2] = top - 8 - abs(p[2]) * 0.6
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


def no_harness(S, band=False):
    for o in S['strap']:
        o.hide_render = True
    S['band'].hide_render = not band


# ---------------------------------------------------------------- the hook: on fire, and he jumps
def bomber_wide(S, k, t, lt):
    """The burning bomber from behind and above its tail; a small figure rolls out of the rear turret and drops away. First and last shot."""
    kk = 1 - k if S['prm'].get('loop') else k
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0), top=-6)
    burning(S, t, 2.4)
    u = sm(kk / 0.9)
    m = S['man']
    m.root.scale = (1.5, 1.5, 1.5)
    m.place((0.3 * u, 17.6 + 5.0 * u, 0.6 + 1.6 * math.sin(PI * min(1, u * 2)) * (1 - u) - 6.0 * u * u), PI, -2.6 * u, 0.3 * u)
    m.apply(P('stand', aL=(1.6, 0.9, 0.5), aR=(1.9, 0.8, 0.4), lL=(1.2 - 0.6 * u, 1.3 - 0.8 * u), lR=(1.0 - 0.9 * u, 1.4 - 0.6 * u)))
    m.face = 'wide'
    shoot(S, SKYO, (lerp(-6.0, -5.0, kk), lerp(31, 29, kk), lerp(9.5, 8.2, kk)), (-0.6, 8.0, lerp(3.4, 2.2, kk)), 25)


def turret_fire(S, k, t, lt):
    """Close on the gunner in the open frame of the turret: fire in the fuselage behind him, he looks back at it and then out at the night."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0), top=-6)
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
        o.scale = (1 + 0.7 * g, 0.2, 1 + 0.7 * g)
    fire(S, [(-0.62, -0.1, 2.25), (0.1, -0.05, 2.3), (0.66, -0.1, 2.2), (-0.9, -0.2, 1.75), (0.85, -0.25, 1.3), (-3.0, 0.2, 1.0), (-3.6, 0.2, 2.6),
             (4.2, 0.6, 2.6), (-2.3, 0.1, 0.4)], t, lerp(0.3, 0.5, g), (0.2, 0, 1), o=BAY)
    for i in (5, 6, 8):
        S['fl'][i].scale = tuple(v * 2.2 for v in S['fl'][i].scale)
    glow(S, 0, at(BAY, -0.8, -1.4, 2.4), 500, t)
    glow(S, 1, at(BAY, 1.8, -1.8, 1.0), 200, t)
    reach = sm(lt / 0.45) * (1 - sm((lt - 0.62) / 0.16))
    S['glove'].place(at(BAY, lerp(3.6, 1.75, reach), -0.7, 1.35 + 0.06 * math.sin(lt * 30) * reach), (0.15, 0.0, -PI / 2))
    S['glove'].grip(0.1 + 0.6 * (1 - reach))
    shoot(S, BAY, (lerp(1.3, 1.0, k), lerp(-5.6, -4.8, k), lerp(2.1, 1.9, k)), (0.5, 0.2, 1.5), 40)


def backflip(S, k, t, lt):
    """From beside the tail: he lets go and goes backwards out of the turret into the dark."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0), top=-6)
    b = burning(S, t, 2.0)
    fire(S, [(-1.9, 15.2, 0.6), (1.7, 15.0, 1.0), (0.0, 15.3, 1.9)], t, 1.2, (0, 1, 0.4), i0=12, par=b)
    glow(S, 2, at(SKYO, -3.0, 19.5, 1.5), 1500, t)
    u = sm((lt - 0.1) / 0.6)
    m = S['man']
    m.place((0.0, 16.6 + 3.6 * u, -1.5 + 2.6 * math.sin(PI * min(1, u * 1.5)) * (1 - 0.5 * u) - 3.2 * u * u), PI, -2.9 * u)
    m.apply(blend(P('sit', aL=(1.1, 0.25, 0.9), aR=(1.2, 0.3, 0.7), lift=-0.5), P('stand', aL=(2.6, 0.7, 0.2), aR=(2.5, 0.8, 0.3), lL=(0.9, 0.9), lR=(0.6, 1.2)), u * 1.6))
    m.face = 'shut' if u > 0.2 else 'wide'
    shoot(S, SKYO, (lerp(-7.5, -6.5, k), lerp(23.5, 24.5, k), lerp(1.2, 0.2, k)), (0.0, 17.6 + 2.4 * u, 0.2 - 1.6 * u), 38)


# ---------------------------------------------------------------- the doubt and the fall
def rook_fall(S, k, t, lt):
    """Rook is falling beside him, wings out, hat brim low, and does not believe it. The man tumbles behind him, the bomber burns above."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 55))
    far_bomber(S, at(FALL, -9, 34, 17 + 5 * lt), t)
    falling(S, at(FALL, -1.5, 4.5, 1.2 + 0.3 * math.sin(t * 2)), t, 0.9)
    f = math.sin(t * 10)
    rk = rook_air(S, at(FALL, 1.2, -0.5, -0.4), t, 0.3, P('stand', aL=(0.35, 1.15 + 0.2 * f, 0.95 - 0.35 * f), aR=(0.35, 1.1 + 0.2 * f, 1.0 - 0.35 * f),
                                                        lL=(0.7, 1.2), lR=(0.1, 0.9), lean=0.12, head=(0.05, lerp(-0.9, 0.0, sm(lt / 0.45)))))
    S['rface'], S['hat_tip'] = 'low', 0.45
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(-0.2, 0.1, k), h[1] - lerp(4.9, 4.4, k), h[2] - 0.6), (h[0] - 0.9, h[1], h[2] - 0.5), 34)


def fighter(S, k, t, lt):
    """From behind and below: the dark twin-engined fighter under the bomber's tail, its tracer going up in a line into the wing."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0), top=-30)
    b = S['bomber']
    b.location = SKYO
    b.rotation_euler = (0, 0.04 * math.sin(t * 2), 0)
    f = S['fighter']
    fp = (7 - 2 * k, 34 - 5 * k, -13 + 2 * k)
    f.location = at(SKYO, *fp)
    f.rotation_euler = (0.32, -0.12 + 0.05 * math.sin(t * 3), 0.2)
    a, e = Vector(at(SKYO, fp[0] - 1.2, fp[1] - 8.5, fp[2] + 3.0)), Vector(at(SKYO, -9, -3, 0))
    for i, o in enumerate(S['tracers']):
        p = (lt * 2.6 + i / 7) % 1
        span(o, a + (e - a) * p, a + (e - a) * min(1.0, p + 0.07), 0.14)
    hit = sm((lt - 0.25) / 0.5)
    fire(S, WINGF[:5], t, 0.4 + 2.0 * hit, (0, 1, 0.2), par=b)
    glow(S, 0, at(SKYO, -8, -2, -3), 60000 * hit + 12000 * (math.sin(lt * 40) > 0), t)
    shoot(S, SKYO, (lerp(30, 26, k), lerp(64, 58, k), lerp(-5, -6, k)), (1.5, 15.0, -6.5), 38)


def wing_fire(S, k, t, lt):
    """The wing goes up: fire bursts out of the engine and streams back along the fuselage; torn metal flies off."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0), top=-6)
    g = sm(lt / 0.5)
    b = burning(S, t, 0.6 + 1.9 * g, 12, 15000 + 40000 * g)
    debris(S, at(SKYO, -8, -3, 1), lt * 1.4, 8, 5.0, 2.0, 2.0)
    for o in S['bits'][:8]:
        o.location.y += 26 * lt
    shoot(S, SKYO, (lerp(-34, -30, k), lerp(-30, -27, k), lerp(11, 9, k)), (-5.0, 1.0, 0.0), 30)


def fall_wide(S, k, t, lt):
    """From above: he drops away on his back, arms and legs trailing, turning slowly, the dark country a long way under him."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 70), top=-10)
    falling(S, at(FALL, 0, -1.5, 0), t, 0.3, 1.3 * lt)
    shoot(S, FALL, (lerp(0.8, 0.4, k), lerp(-3.0, -2.2, k), lerp(6.5, 10.5, k)), (0.0, 0.0, 0.0), 24, roll=0.5 * k)


def pad_at(S, rk, lift=0.0, spin=0.0):
    h = wpos(rk.hands[0], (0, 0, -0.5))
    S['pad'].location = (h[0] + 0.05, h[1] - 0.1, h[2] + 0.02 + lift)
    S['pad'].rotation_euler = (-0.75 + spin, 0.0 + spin * 0.6, rk.root.rotation_euler[2] + 0.2)


def rook_maths(S, k, t, lt):
    """Rook, still falling, has his notepad out and is working it through: height, speed, no parachute. He looks down, and his eyes go wide."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 70))
    falling(S, at(FALL, -3.0, 4.5, 0.5), t, 1.2)
    sc = math.sin(lt * 26)
    look = sm((lt - 0.75) / 0.25)
    rk = rook_air(S, FALL, t, 0.35, P('stand', aL=(0.7, -0.12, 1.45, 0.5), aR=(0.75 + 0.06 * sc, -0.2 + 0.05 * sc, 1.6, 0.75), lL=(0.35, 0.6), lR=(-0.15, 0.5),
                                      head=(lerp(0.5, 0.25, look), lerp(0.1, 0.0, look))))
    pad_at(S, rk)
    S['rface'] = 'shocked' if look > 0.5 else 'calm'
    S['hat_jump'] = 0.2 * look
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.6, 1.3, k), h[1] - lerp(4.6, 4.0, k), h[2] + 0.1), (h[0] - 0.1, h[1], h[2] - 0.45), 44)


def fall_close(S, k, t, lt):
    """Close on him, on his back in the air, arms wide, looking straight up at the stars; his eyes close."""
    sky(S, 'night', True)
    air(S, FALL, t, (0, 0, 70))
    m = S['man']
    w = math.sin(t * 4)
    m.place(at(FALL, 0, -1.5, 0), 0.0, -PI / 2 + 0.08 * math.sin(t * 1.3), 0.1 * math.sin(t * 0.9))
    m.apply(P('stand', aL=(0.7 + 0.12 * w, 1.25, 0.5), aR=(0.8 - 0.12 * w, 1.2, 0.6), lL=(0.9, 0.6), lR=(0.5, 0.9), head=(-0.05, 0.0)))
    m.face = 'wide' if lt < 0.7 else 'tired' if lt < 0.95 else 'shut'
    m.jawv = 0.15
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + 0.3 - 0.3 * k, h[1] - lerp(1.5, 1.2, k), h[2] + lerp(3.4, 2.8, k)), (h[0], h[1] - 0.2, h[2]), 46, roll=0.12 - 0.24 * k)


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
    z = lerp(120, 17, k ** 1.3)
    shoot(S, WOOD, (0.8 + 1.5 * math.sin(lt * 7), -1.2 + 1.5 * math.cos(lt * 6), z), (0.0, 0.0, 0.0), 20, roll=0.9 * k)


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
    z = lerp(22.0, 0.0, u ** 1.5)
    m = lying(S, 'shut', dict(aL=(2.0, 0.8, 0.5), aR=(1.7, 0.9, 0.6), lL=(0.8, 0.7), lR=(0.4, 0.9), head=(0, 0)) if u < 1 else None, z)
    m.root.rotation_euler[0] = -PI / 2 + 0.5 * (1 - u) * math.sin(lt * 20)
    debris(S, at(WOOD, 0, 0, lerp(13, 6, min(1, lt / 0.4))), lt - 0.12, 8, 5.0, 2.5, 9.0)
    snowburst(S, at(WOOD, 0, 0, 0.3), lt - 0.5, 20, 4.0, 5.0)
    shoot(S, WOOD, (lerp(3.0, 2.4, k), lerp(-10.5, -9.0, k), lerp(1.6, 1.3, k)), (0.0, 0.0, lerp(9.0, 1.6, sm(lt / 0.5))), 24)


def snow_hole(S, k, t, lt):
    """From above: he lies on his back in a man-sized dent in the snow, broken boughs round him. Snow sifts down. His eyes open."""
    sky(S, 'wood')
    m = lying(S, 'shut' if lt < 0.8 else 'wide')
    m.jawv = 0.3 * sm((lt - 0.8) / 0.2)
    snowfall(S, WOOD, t, 12, 0, 2.8, 8.0, 2.4)
    shoot(S, WOOD, (0.5, lerp(-1.6, -1.1, k), lerp(11.0, 8.2, k)), (0.0, 0.1, 0.4), 30, roll=lerp(0.25, 0.0, k))


def hole_up(S, k, t, lt):
    """What he sees: a ring of pine tops, a ragged hole, stars. Snow drifts down through it. Rook's head comes in over the edge, staring."""
    sky(S, 'up', True)
    snowfall(S, WOOD, t, 14, 0, 2.2, 12.0, 2.2)
    u = sm((lt - 0.2) / 0.35)
    rk = S['rook']
    rk.place(at(WOOD, 0.3, lerp(-5.2, -2.1, u), 0.0), PI)
    rk.apply(P('stand', aL=(0.5, 0.3, 0.4), aR=(0.5, 0.3, 0.4), lean=0.55, head=(0.5, 0.0)))
    S['rface'] = 'shocked'
    S['hat_jump'] = 0.25 * max(0.0, math.sin((lt - 0.55) * 9)) if 0.55 < lt < 0.9 else 0.0
    shoot(S, WOOD, (0.3, 0.7, 0.45), (0.3 + 0.2 * math.sin(lt), lerp(-3.6, -4.4, k), 8.0), 16)


def rook_measure(S, k, t, lt):
    """Detective work: Rook pushes a stick into the drift beside him, marks the depth with a wingtip, then points up at the hole in the trees."""
    sky(S, 'wood')
    m = lying(S, 'wide', dict(LIE, head=(0.0, -0.5)))
    u = sm(lt / 0.5)
    v = sm((lt - 0.8) / 0.35)
    S['twig'].location = at(WOOD, 2.0, -2.2, lerp(1.5, 0.45, u))
    S['twig'].rotation_euler = (0.08, 0.05, 0)
    rk = S['rook']
    rk.place(at(WOOD, 2.9, -2.0, 0.0), facing((2.9, -2.0), (1.0, -3.2)))
    crouch = P('stand', aR=(1.0, 0.2, 0.5), aL=(0.3, 0.2, 0.6), lL=(1.1, 1.7), lR=(1.1, 1.7), lift=-0.5, lean=0.4, head=(0.35, 0.0))
    up = P('reach', aR=(2.75, 0.2, 0.05), lL=(0.2, 0.3), lR=(0.1, 0.2), lift=-0.05, head=(-0.55, 0.3))
    rk.apply(blend(crouch, up, v))
    S['rface'] = 'shocked' if v > 0.5 else 'calm'
    shoot(S, WOOD, (lerp(1.2, 1.0, k), lerp(-8.0, -7.2, k), lerp(1.9, 1.7, k)), (1.7, -1.2, lerp(1.0, 1.6, v)), 30)


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
    S['deskl'].data.energy = 700 * lampk * (0.97 + 0.03 * math.sin(t * 31))
    S['cl'].data.energy = 1800
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


RK_ROOM = (-0.9, 3.5)


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
    """Rook by the wall map: arms folded, hat brim down, nodding along with them. He does not believe it either."""
    room(S, t)
    man_chair(S)
    nod = 0.16 * math.sin(lt * 8)
    rk = rook_corner(S, P('cross', head=(0.12 + nod, lerp(-0.5, 0.35, sm(lt / 0.9)))), yaw=facing(RK_ROOM, (-2.2, -1.5)))
    S['rface'], S['hat_tip'] = 'low', 0.7
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] - lerp(2.3, 2.0, k), h[1] - lerp(3.9, 3.4, k), h[2] - 0.2), (h[0] - 0.05, h[1], h[2] - 0.4), 42)


def spy_point(S, k, t, lt):
    """Over the airman's shoulder: the man in the hat is on his feet, bangs the desk and points straight at him."""
    room(S, t)
    man_chair(S, dict(lean=0.05))
    up = sm(lt / 0.25)
    pt = sm((lt - 0.3) / 0.2)
    a = S['agents'][0]
    a.place(at(ROOM, 1.75, 0, 0), -PI / 2)
    a.apply(blend(P('stand', aL=(0.9, 0.2, 0.3), aR=(0.9, 0.2, 0.3), lean=0.45 * up, head=(-0.1, 0.0)),
                  P('point', aR=(1.2, 0.55, 0.05), aL=(0.9, 0.2, 0.3), lean=0.4, head=(-0.1, 0.0)), pt))
    a.face, a.jawv = 'hard', 0.3 + 0.4 * abs(math.sin(lt * 14))
    agent_stand(S, P('hips', head=(0.1, 0.0)))
    shoot(S, ROOM, (lerp(-4.6, -4.1, k), lerp(-2.3, -2.0, k), lerp(2.9, 2.75, k)), (1.0, 0.25, 2.0), 36)


def he_points(S, k, t, lt):
    """Close on the airman: he leans in and points past them, level and sure. Behind him Rook unfolds his arms and tilts his head."""
    room(S, t)
    u = sm(lt / 0.4)
    m = man_chair(S, dict(aR=(lerp(0.75, 1.5, u), lerp(-0.05, 0.1, u), lerp(1.2, 0.1, u), 0.0), lean=lerp(0.1, 0.32, u), head=(0.0, -0.45)), 'hard' if u < 0.3 else 'calm')
    m.jawv = 0.3 + 0.3 * abs(math.sin(lt * 11))
    v = sm((lt - 0.5) / 0.4)
    rk = S['rook']
    rk.place(at(ROOM, -3.9, 1.5, 0), facing((-3.9, 1.5), (1.5, -3.0)))
    rk.apply(blend(P('cross', head=(0.1, 0.0)), P('think', head=(0.05, 0.35)), v))
    S['rface'], S['hat_tip'] = ('calm' if v > 0.5 else 'low'), 0.5 * (1 - v)
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(3.3, 2.9, k), h[1] - lerp(2.9, 2.5, k), h[2] + 0.1), (h[0] - 0.2, h[1] + 0.5, h[2] - 0.1), 36)


def officer_writes(S, k, t, lt):
    """Later, at the same desk: a man in a cap writes it out, signs and stamps it. The airman watches; Rook leans in over the desk to read."""
    room(S, t)
    man_chair(S, dict(lean=0.2 + 0.1 * sm((lt - 1.0) / 0.3), head=(0.3, 0.2 * math.sin(lt * 2.5))))
    st = sm((lt - 1.0) / 0.2)
    w = math.sin(lt * 24) * (1 - st)
    o = agent_chair(S, S['men'][0], dict(aR=(1.05 + 0.06 * w, -0.25 + 0.1 * w, 0.75, 0.3), aL=(0.95, -0.2, 0.8, 0.5), lean=0.42, head=(0.5, 0.1 * w)), 'calm')
    S['paper'].location = at(ROOM, 0.15, -0.1, 1.36)
    S['paper'].rotation_euler = (0, 0, 0.12)
    hp = wpos(o.hands[1], (0, 0, -0.6))
    S['pen'].location = (hp[0], hp[1], hp[2] + 0.22) if st < 0.5 else FAR
    S['pen'].rotation_euler = (0.4, 0.3, 0)
    S['stamp'].location = at(ROOM, 0.2, -0.3, 1.52 + 0.9 * (1 - st) + 0.25 * sm((lt - 1.25) / 0.2)) if lt > 0.85 else FAR
    rk = S['rook']
    rk.place(at(ROOM, lerp(-1.6, -0.6, sm(lt / 0.8)), 2.4, 0), facing((-0.6, 2.4), (0.1, -3)))
    rk.apply(blend(K.walk(t, 1.4), P('stand', aL=(0.6, 0.2, 0.5), aR=(0.6, 0.2, 0.5), lean=0.35, head=(0.4, 0.15 * math.sin(lt * 3))), (lt - 0.5) / 0.4))
    S['rface'] = 'calm' if st < 0.5 else 'shocked'
    shoot(S, ROOM, (lerp(-2.2, 0.6, k), lerp(-7.2, -4.6, k), lerp(3.3, 2.5, k)), (0.0, 0.4, 1.75), 27)


def man_smile(S, k, t, lt):
    """The airman holds the sheet in both hands and reads it, and for the first time something like a smile."""
    room(S, t)
    v = sm((lt - 0.5) / 0.35)
    m = man_chair(S, dict(aL=(0.75, -0.15, 1.1, 0.5), aR=(0.75, -0.15, 1.1, 0.5), head=(lerp(0.4, 0.0, v), lerp(-0.2, -0.6, v)), lean=0.12), 'calm' if lt < 0.5 else 'warm')
    hl, hr = wpos(m.hands[0], (0, 0, -0.5)), wpos(m.hands[1], (0, 0, -0.5))
    S['paper'].location = ((hl[0] + hr[0]) / 2 + 0.1, (hl[1] + hr[1]) / 2, (hl[2] + hr[2]) / 2 + 0.05)
    S['paper'].rotation_euler = (0.6, 0, PI / 2)
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(3.2, 2.8, k), h[1] - lerp(1.9, 1.6, k), h[2] + 0.15), (h[0] + 0.15, h[1], h[2] - 0.35), 44)


def rook_hat(S, k, t, lt):
    """Rook has the sheet now. He reads down it, and his hat leaves his head; a feather comes loose."""
    room(S, t)
    rk = S['rook']
    rk.place(at(ROOM, -0.2, 2.5, 0), 0.25)
    rk.apply(P('stand', aL=(0.7, -0.15, 1.2, 0.5), aR=(0.7, -0.15, 1.2, 0.5), head=(lerp(0.45, 0.6, sm(lt / 0.5)) - 0.5 * sm((lt - 0.6) / 0.2), 0.0)))
    hl, hr = wpos(rk.hands[0], (0, 0, -0.5)), wpos(rk.hands[1], (0, 0, -0.5))
    S['paper'].location = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2 - 0.05, (hl[2] + hr[2]) / 2 + 0.05)
    S['paper'].rotation_euler = (0.7, 0, 0.25)
    pop = sm((lt - 0.55) / 0.12)
    S['rface'] = 'shocked' if pop > 0.3 else 'calm'
    S['hat_jump'] = 0.55 * pop * (0.6 + 0.4 * abs(math.cos((lt - 0.55) * 7))) * (1 - sm((lt - 1.3) / 0.3))
    h = rhead(S)
    feather(S, (h[0] + 0.3, h[1], h[2] + 0.2), lt - 0.6)
    shoot(S, (0, 0, 0), (h[0] - lerp(1.5, 1.2, k), h[1] - lerp(4.5, 3.8, k), h[2] + 0.1), (h[0], h[1], h[2] - 0.45), 40)


# ---------------------------------------------------------------- the proof
def search_wood(S, k, t, lt):
    """Grey daylight in the same wood: two men in caps wade through the snow towards the dent. Rook is already there, pointing down at it."""
    sky(S, 'day')
    for i, rig in enumerate(S['men']):
        x = lerp(11 + 2.5 * i, 6.2 + 2.2 * i, k)
        rig.place(at(WOOD, x, 0.2 - 1.8 * i, 0), -PI / 2 - 0.3)
        rig.apply(K.walk(t + i * 0.3, 1.5))
        rig.face = 'calm'
    rk = S['rook']
    rk.place(at(WOOD, 3.6, -4.2, 0.0), facing((3.6, -4.2), (1.5, -9.0)))
    rk.apply(blend(P('stand', head=(0.0, 0.9)), P('point', aR=(0.8, 0.5, 0.1), head=(0.3, -0.2)), lt / 0.45))
    S['harness'].location = at(WOOD, 2.2, -5.2, 0.06)
    S['harness'].scale = (1.6, 1.6, 1.6)
    shoot(S, WOOD, (lerp(0.0, 0.5, k), lerp(-11.5, -10.5, k), lerp(1.6, 1.45, k)), (3.6, -2.4, 1.5), 26)


def harness(S, k, t, lt):
    """The harness he took off, found in the snow. Rook lifts it by one strap and turns it over: the two lifting straps are still folded
    flat against it, never pulled out. He taps his beak."""
    sky(S, 'day')
    u = sm(lt / 0.55)
    rk = S['rook']
    rk.place(at(WOOD, 2.6, -4.6, 0.0), facing((2.6, -4.6), (2.2, -9.0)))
    tap = 0.14 * max(0.0, math.sin((lt - 0.8) * 14)) if lt > 0.8 else 0.0
    low = P('stand', aL=(0.9, 0.1, 0.3), aR=(0.3, 0.2, 0.4), lL=(1.0, 1.6), lR=(1.0, 1.6), lift=-0.48, lean=0.5, head=(0.5, 0.0))
    high = P('tap', aR=(1.25 + tap, -0.25, 2.2, 0.6), aL=(1.15, 0.0, 0.9, 0.2), head=(0.3, 0.1))
    rk.apply(blend(low, high, u))
    yw = rk.root.rotation_euler[2]
    S['harness'].location = at(WOOD, 2.6 + 0.62 * math.sin(yw) - 0.35 * math.cos(yw), -4.6 - 0.62 * math.cos(yw) - 0.35 * math.sin(yw), lerp(0.1, 1.25, u))
    S['harness'].rotation_euler = (lerp(0.0, 1.25, u), 0.0, yw + 0.12 * math.sin(lt * 2.5) * u)
    S['harness'].scale = (0.62, 0.62, 0.62)
    S['rface'] = 'calm' if lt < 1.1 else 'shocked'
    snowburst(S, at(WOOD, 2.5, -5.4, 0.1), lt - 0.1, 8, 1.2, 1.0, 12)
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] - lerp(1.6, 0.9, k), h[1] - lerp(5.6, 4.4, k), lerp(0.9, 1.9, k) + WOOD[2]), (h[0] - 0.1, h[1], lerp(1.2, h[2] - WOOD[2] - 0.75, sm(k * 1.3)) + WOOD[2]), 36)


def at_wreck(S, t):
    sky(S, 'day')


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
    S['glove'].root.scale = (1.0, 1.0, 1.0)
    S['glove'].place(at(WRECK, lerp(3.1, 2.45, sm(lt / 0.6)), -2.6, 0.95), (0.0, 0.0, -PI / 2 + 0.3))
    S['glove'].grip(0.75)
    S['glove'].f[0][0].rotation_euler = (0.0, 0, 0)
    S['glove'].f[0][1].rotation_euler = (0.0, 0, 0)
    shoot(S, WRECK, (lerp(2.5, 2.2, k), lerp(-5.4, -4.6, k), lerp(1.5, 1.25, k)), (1.75, -2.0, 0.78), 44)


# ---------------------------------------------------------------- the ending
def four_stones(S, k, t, lt):
    """Four plain white headstones in a row, early light. Rook stands beside them with his hat off and his head down."""
    sky(S, 'dawn')
    S['sun'].data.energy = 4.5
    rk = S['rook']
    rk.place(at(YARD, 3.1, -1.2, 0), facing((3.1, -1.2), (-1.5, -3.6)))
    rk.apply(P('stand', head=(lerp(0.0, 0.5, sm(lt / 0.9)), 0.25), aR=(0.1, 0.25, 0.3)))
    S['rface'], S['hat_off'] = 'sad', 1.0
    shoot(S, YARD, (lerp(5.6, 1.6, k), lerp(-8.0, -6.6, k), lerp(2.2, 1.5, k)), (1.6, -0.5, 1.5), 28)


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


# ================================================================ long-form extension (16:9 full case file)
# The Short's sky, bomber, rack, wood, room, wreck and headstones stay as they were. New for the full case, each built at its
# own origin high above the Short's sets and shown only in its own shots: a market garden's glasshouse in Loughborough before
# the war, an airfield at dusk with two parked bombers, a stream of bombers in the night sky, a hospital room, a hut where
# captured airmen are held, a prison camp in winter with a road leading west, a lane in May, a chemical works, a television
# studio of the 1980s and a plain modern squadron building. New figures: Nicholas before the war and in later life, the six
# other men of his crew, British prisoners, a guard. All of it is generic: no markings, roundels, flags, insignia, badges,
# emblems, logos or lettering anywhere, none of the places is a model of the real one, and nobody's likeness is attempted.
# Building with bpy.ops gets slower with every object already in the scene (the Short alone took over two minutes to build,
# and this file more than doubles the object count). The same primitives are made here by copying one prototype mesh per
# shape, which gives identical geometry, materials and bevels in a fraction of the time. The new object is selected and made
# active, exactly as the operator leaves it, so code that follows an add (shade_smooth) behaves the same.
from mathutils import Matrix  # noqa: E402

_PROTO, _LAST = {}, [None]
_ops_add, _ops_empty = K.add, K.empty


def _select(o):
    if _LAST[0] is not None:
        try:
            _LAST[0].select_set(False)
        except (ReferenceError, RuntimeError):
            pass
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    _LAST[0] = o


def _unit(kind, kw):
    """The prototype is made at unit size and the mesh scaled to the asked size afterwards, so pines of every height share one."""
    if kind in ('cube', 'plane'):
        v = kw.pop('size', 2.0)
        kw['size'] = 1.0
        return kw, (v, v, v)
    if kind == 'ico_sphere':
        r = kw.pop('radius', 1.0)
        kw['radius'] = 1.0
        return kw, (r, r, r)
    if kind == 'cylinder':
        r, d = kw.pop('radius', 1.0), kw.pop('depth', 2.0)
        kw.update(radius=1.0, depth=1.0)
        return kw, (r, r, d)
    if kind == 'cone':
        r1, r2, d = kw.pop('radius1', 1.0), kw.pop('radius2', 0.0), kw.pop('depth', 2.0)
        if r1 <= 0:
            kw.update(radius1=r1, radius2=r2, depth=d)
            return kw, (1.0, 1.0, 1.0)
        kw.update(radius1=1.0, radius2=round(r2 / r1, 5), depth=1.0)
        return kw, (r1, r1, d)
    return kw, (1.0, 1.0, 1.0)


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    kw, sc = _unit(kind, dict(kw))
    key = (kind, tuple(sorted(kw.items())))
    if key not in _PROTO:
        getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=(0, 0, 0), **kw)
        o = bpy.context.object
        _PROTO[key] = o.data
        bpy.data.objects.remove(o)
    me = _PROTO[key].copy()
    if sc != (1.0, 1.0, 1.0):
        me.transform(Matrix.Diagonal((sc[0], sc[1], sc[2], 1.0)))
    o = bpy.data.objects.new(kind, me)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    me.materials.append(K.mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    if parent:
        o.parent = parent
    _select(o)
    return o


def empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new('Empty', None)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    _select(o)
    return o


K.add, K.empty = add, empty      # the rigs and hands in kit3d use the same fast path


SETPOS = dict(garden=(0.0, 0.0, 5000.0), field=(600.0, 0.0, 5000.0), stream=(1200.0, 0.0, 5600.0), hosp=(1800.0, 0.0, 5000.0),
              hut=(2400.0, 0.0, 5000.0), camp=(3000.0, 0.0, 5000.0), lane=(3600.0, 0.0, 5000.0), works=(4200.0, 0.0, 5000.0),
              studio=(4800.0, 0.0, 5000.0), bldg=(5400.0, 0.0, 5000.0))
SKIES.update(
    dusk=('F0A070', '2E4470', 1.6, 3.6, 'FFC090', (0.8, -0.5, 0.3)),
    garden=('E8F0E0', 'A8C4D8', 1.4, 3.2, 'FFF0D8', (0.4, -0.6, 0.7)),
    winter=('C8D0DA', '8C9AAE', 1.3, 2.0, 'E8EEF6', (0.3, -0.5, 0.6)),
    spring=('F0F4E0', '8EB4DC', 1.5, 3.4, 'FFF4DC', (0.5, -0.6, 0.65)),
    inside=('101216', '08090C', 0.3, 0.0, 'FFFFFF', (0, 0, 1)))
CAMFILL.update(garden_wide=220, garden_close=160, field_dusk=260, crew_seven=320, takeoff=600, stream=4000, turret_calm=300, rack_calm=160,
               gunner_face=140, cigarette=420, whistle=520, hospital=200, witnesses=220, camp_famous=200, camp_wire=300, long_march=360,
               home_may=200, works=240, tv_studio=160, plaque=220, dawn_wood=200)
HOST |= {'garden_wide', 'field_dusk', 'crew_seven', 'turret_calm', 'rack_calm', 'whistle', 'hospital', 'witnesses', 'camp_famous',
         'long_march', 'home_may', 'tv_studio', 'plaque'}
CREWC = ('4E5A6E', '56606E', '4A5466', '525C6A', '4C566A', '58627A')
POWC = dict(top='5A6478', pants='4A5262', hand=SKIN, boot='1E1C22', fore='5A6478')


def box(col, loc, scale, parent=None, rot=(0, 0, 0), **kw):
    return add('cube', col, loc, rot=rot, scale=scale, size=1, parent=parent, **kw)


def SP(name, x, y, z):
    o = SETPOS[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def kids(root):
    return [root] + list(root.children_recursive)


def vis(objs, on):
    for o in objs:
        o.hide_render = not on


def lanc(par, loc, yaw=0.0, s=1.0, ground=True):
    """A plain four-engined bomber like the Short's, nose towards -Y, on its wheels. No markings, no numbers, no names."""
    o = empty(loc, par, (0, 0, yaw))
    G, U, D = '4A5A44', '1E2228', '26323E'
    z0 = 3.4 * s if ground else 0.0
    box(G, (0, 0, z0 + 0.4 * s), (3.0 * s, 30 * s, 2.6 * s), o)
    box(U, (0, 0, z0 - 1.0 * s), (3.05 * s, 30.05 * s, 1.4 * s), o)
    box(G, (0, -16.2 * s, z0 + 0.1 * s), (2.5 * s, 3.0 * s, 2.6 * s), o)
    box(D, (0, -18.0 * s, z0 - 0.2 * s), (1.9 * s, 1.4 * s, 1.8 * s), o, rough=0.3)
    box(D, (0, -10.5 * s, z0 + 2.1 * s), (2.2 * s, 5.5 * s, 1.1 * s), o, rough=0.3)
    box(G, (0, -3.5 * s, z0 + 0.2 * s), (26 * s, 7.6 * s, 0.55 * s), o)
    for sd in (-1, 1):
        box(G, (sd * 19 * s, -3.0 * s, z0 + 0.45 * s), (13 * s, 5.2 * s, 0.4 * s), o, rot=(0, sd * -0.05, sd * 0.07))
        box(G, (sd * 4.0 * s, 13.8 * s, z0 + 0.9 * s), (7.5 * s, 3.4 * s, 0.3 * s), o)
        box(G, (sd * 7.9 * s, 14.1 * s, z0 + 1.3 * s), (0.3 * s, 4.4 * s, 4.6 * s), o)
        for x in (7.0, 14.0):
            add('cylinder', U, (sd * x * s, -6.6 * s, z0), rot=(PI / 2, 0, 0), radius=1.15 * s, depth=6.4 * s, vertices=8, parent=o)
            for j in range(3):
                box('15171B', (sd * x * s, -10.05 * s, z0), (5.4 * s, 0.08 * s, 0.34 * s), o, rot=(0, j * PI / 3, 0))
        if ground:
            add('cylinder', '15171B', (sd * 7.0 * s, -5.0 * s, 1.0 * s), rot=(0, PI / 2, 0), radius=1.0 * s, depth=0.6 * s, vertices=10, parent=o)
            bar(o, '3A3F46', (sd * 7.0 * s, -5.0 * s, 1.0 * s), (sd * 7.0 * s, -5.6 * s, z0 - 0.6 * s), 0.18 * s)
    if ground:
        add('cylinder', '15171B', (0, 14.5 * s, 0.45 * s), rot=(0, PI / 2, 0), radius=0.45 * s, depth=0.3 * s, vertices=8, parent=o)
        bar(o, '3A3F46', (0, 14.5 * s, 0.45 * s), (0, 14.2 * s, z0 - 1.2 * s), 0.1 * s)
    for zz in (-1.25, 1.25):                                               # the rear turret, glazed this time
        add('torus', '50565E', (0, 16.3 * s, z0 + zz * s), major_radius=1.5 * s, minor_radius=0.07 * s, major_segments=12, minor_segments=4, parent=o)
    add('ico_sphere', '1A2A3A', (0, 16.4 * s, z0), radius=1.45 * s, subdivisions=2, parent=o, rough=0.15)
    for sd in (-1, 1):
        bar(o, '22262C', (sd * 0.4 * s, 17.4 * s, z0), (sd * 0.4 * s, 19.6 * s, z0), 0.06 * s)
    return o


# ---------------------------------------------------------------- the new sets
def make_garden(r):
    """A market garden's glasshouse in spring: a frame of white glazing bars, benches of seedlings, rows of lettuces outside."""
    box('5A4632', (0, 0, -0.05), (60, 60, 0.1), r, rough=1.0)
    for i in range(9):                                                     # rows of lettuces outside the glass
        for j in range(14):
            add('ico_sphere', ('5E9A4A', '6EAA54')[(i + j) % 2], (-24 + 2.0 * j + 0.3 * rnd(i, j), 9 + 2.2 * i, 0.25), scale=(1, 1, 0.6), radius=0.45,
                subdivisions=1, parent=r, rough=1.0)
    for x in (-5.0, 5.0):                                                  # the glasshouse: bars and a pale floor
        for j in range(8):
            bar(r, 'F2F2EA', (x, -7 + 2 * j, 0), (x, -7 + 2 * j, 3.0), 0.07)
        bar(r, 'F2F2EA', (x, -7, 3.0), (x, 7, 3.0), 0.07)
    for j in range(8):
        bar(r, 'F2F2EA', (-5.0, -7 + 2 * j, 3.0), (0, -7 + 2 * j, 5.2), 0.07)
        bar(r, 'F2F2EA', (5.0, -7 + 2 * j, 3.0), (0, -7 + 2 * j, 5.2), 0.07)
    bar(r, 'F2F2EA', (0, -7, 5.2), (0, 7, 5.2), 0.08)
    for x in (-5.0, 5.0):
        box('D8EEF0', (x, 0, 1.6), (0.04, 14, 3.0), r, alpha=0.12, rough=0.05)
    box('8A7A62', (0, 0, 0.0), (9.6, 14, 0.04), r, rough=1.0)
    for x in (-3.4, 3.4):                                                  # benches of seedling trays
        box('6A5038', (x, 0, 1.0), (2.2, 12, 0.12), r)
        for y in (-5.5, 5.5):
            for sx in (-0.9, 0.9):
                box('5A4430', (x + sx, y, 0.5), (0.12, 0.12, 1.0), r)
        for j in range(10):
            box('7A5A3A', (x, -5.4 + 1.2 * j, 1.14), (1.9, 1.0, 0.14), r)
            for q in range(6):
                add('cone', '78C060', (x - 0.7 + 0.28 * q, -5.4 + 1.2 * j + 0.25 * (q % 2), 1.32), radius1=0.12, radius2=0.0, depth=0.28, vertices=4, parent=r)
    for i in range(5):                                                     # pots by the door
        add('cylinder', 'B4643A', (-1.0 + 0.6 * i, -6.4, 0.25), radius=0.24, depth=0.5, vertices=8, parent=r)
    can = empty((0.8, -2.0, 0.0), r)                                       # a watering can
    add('cylinder', '7A8A8E', (0, 0, 0.35), radius=0.28, depth=0.6, vertices=10, parent=can, rough=0.4)
    bar(can, '7A8A8E', (0.2, 0, 0.3), (0.7, 0, 0.75), 0.05)
    barrow = empty((-1.4, 3.6, 0.0), r, (0, 0, 0.4))                       # a wheelbarrow for Rook to lean on
    box('3E6A8A', (0, 0, 0.75), (1.0, 1.4, 0.45), barrow)
    add('cylinder', '1E1E22', (0, -0.9, 0.3), rot=(0, PI / 2, 0), radius=0.3, depth=0.12, vertices=10, parent=barrow)
    for sx in (-0.4, 0.4):
        bar(barrow, '6A5038', (sx, 0.6, 0.7), (sx, 1.5, 0.9), 0.05)
    sun = light((6, -10, 9), 0, 'FFF0D0', 8.0, parent=r)
    sun.rotation_euler = (0.9, 0, 0.5)
    return dict(lights=[sun], sun=sun, can=can)


def make_field(r):
    """An airfield at dusk: grass, a concrete hardstanding, a long runway, a black hangar, two parked bombers, a fuel bowser."""
    add('plane', '465A3A', (0, 0, -0.02), size=1600, parent=r, rough=1.0)
    box('8A8A84', (0, 0, 0.0), (34, 34, 0.04), r, rough=0.9)
    box('6E6E6A', (-120, 60, 0.0), (500, 24, 0.04), r, rough=0.9)
    for i in range(20):
        box('D8D8C8', (-300 + 30 * i, 60, 0.03), (12, 0.6, 0.02), r)
    lanc(r, (0, 0, 0), 0.25)
    lanc(r, (-70, 30, 0), 0.6, 0.9)
    hg = empty((60, 70, 0), r)
    box('1E2226', (0, 0, 8), (60, 40, 16), hg)
    add('cylinder', '1E2226', (0, 0, 16), rot=(0, PI / 2, 0), radius=20, depth=60, vertices=12, parent=hg)
    box('2A2E32', (-31, 0, 6), (0.4, 26, 12), hg)
    bw = empty((14, -12, 0), r, (0, 0, -0.6))                              # a fuel bowser
    box('3A4A34', (0, 0, 1.6), (2.6, 6.4, 2.2), bw)
    box('3A4A34', (0, -4.0, 1.4), (2.6, 2.2, 2.0), bw)
    box('101418', (0, -5.05, 1.9), (2.2, 0.1, 0.8), bw, rough=0.2)
    for (y, sx) in ((-3.5, -1), (-3.5, 1), (2.0, -1), (2.0, 1)):
        add('cylinder', '15171B', (sx * 1.3, y, 0.5), rot=(0, PI / 2, 0), radius=0.5, depth=0.3, vertices=8, parent=bw)
    for i in range(14):                                                    # far trees on the horizon
        add('ico_sphere', '2A3A2A', (-400 + 60 * i + 20 * rnd(i, 90), 420, 6), scale=(2.2, 1, 1), radius=10, subdivisions=1, parent=r, rough=1.0)
    sun = light((-20, -50, 40), 0, 'FFB070', kind='SUN', parent=r)
    sun.rotation_euler = (1.0, 0, -0.6)
    return dict(lights=[sun], sun=sun)


def make_stream(r):
    """Night sky over cloud: a loose line of bombers flying towards -Y, small exhaust glows on their engines."""
    ps = []
    for i in range(7):
        p = lanc(r, (-34 + 20 * i + 10 * rnd(i, 91), 40 * i - 60 + 12 * rnd(i, 92), 10 * rnd(i, 93) - 5), 0.0, 1.0, False)
        for sd in (-1, 1):
            for x in (7.0, 14.0):
                add('ico_sphere', 'FF9A40', (sd * x, -3.2, -0.6), radius=0.35, subdivisions=1, parent=p, emit=12.0)
        ps.append(p)
    moon = light((0, 0, 200), 0, 'A8C0E8', kind='SUN', parent=r)
    moon.rotation_euler = (0.6, 0.3, 0.0)
    return dict(lights=[moon], moon=moon, planes=ps)


def make_hosp(r):
    """A small hospital room: whitewashed walls, an iron bed, a window, a chair by the door, a ceiling lamp."""
    box('8A8478', (0, 0, -0.05), (12, 12, 0.1), r)
    box('E4E0D4', (0, 5.0, 2.5), (12, 0.15, 5.0), r)
    box('DCD8CA', (-5.0, 0, 2.5), (0.15, 12, 5.0), r)
    box('DCD8CA', (5.0, 0, 2.5), (0.15, 12, 5.0), r)
    box('B4C4CC', (0, 4.92, 0.6), (12, 0.08, 1.2), r)
    box('A8C4E0', (2.6, 4.95, 2.9), (2.2, 0.06, 2.0), r, emit=0.9)          # the window, daylight
    for x in (1.5, 2.6, 3.7):
        box('F2F2EA', (x, 4.9, 2.9), (0.08, 0.1, 2.1), r)
    box('F2F2EA', (2.6, 4.9, 2.9), (2.3, 0.1, 0.08), r)
    bed = empty((-1.2, 1.6, 0), r)                                         # the bed, head against the back wall
    for (x, y) in ((-0.8, -1.9), (0.8, -1.9), (-0.8, 1.9), (0.8, 1.9)):
        bar(bed, '3A3E44', (x, y, 0), (x, y, 1.0 if y > 0 else 0.75), 0.05)
    box('3A3E44', (0, 1.95, 0.95), (1.7, 0.06, 0.6), bed)
    box('F2F0EA', (0, 0, 0.62), (1.6, 3.8, 0.3), bed, rough=1.0)
    box('E6E2D8', (0, 1.5, 0.84), (1.2, 0.6, 0.18), bed, rough=1.0)
    blanket = box('8A9A86', (0, -0.6, 0.82), (1.66, 2.5, 0.12), bed, rough=1.0)
    box('6A5038', (1.6, 2.4, 0.6), (0.7, 0.7, 1.2), r)                     # a bedside cupboard
    add('cylinder', 'D8E4EC', (1.6, 2.4, 1.32), radius=0.1, depth=0.25, vertices=8, parent=r, alpha=0.5)
    box('5A4A3A', (3.2, -2.2, 0.5), (0.9, 0.9, 0.08), r)                   # the guard's chair
    lamp = light((0, 0.5, 4.8), 0, 'FFF0D8', 3.0, parent=r)
    win = light((2.6, 8.0, 3.0), 0, 'C8DCF0', 3.0, parent=r)
    win.rotation_euler = (-PI / 2, 0, 0)
    return dict(lights=[lamp, win], lamp=lamp, win=win, bed=bed, blanket=blanket)


def make_hut(r):
    """A wooden hut where captured airmen are held: plank walls, a stove, bunks, a table under a hanging lamp."""
    box('5A4434', (0, 0, -0.05), (14, 12, 0.1), r)
    for i in range(14):
        box(('7A5E44', '6E543C')[i % 2], (-6.5 + i, 5.0, 2.4), (1.0, 0.15, 4.8), r)
    box('6E543C', (-6.5, 0, 2.4), (0.15, 12, 4.8), r)
    box('6E543C', (6.5, 0, 2.4), (0.15, 12, 4.8), r)
    box('4A3A2C', (0, 0, 4.85), (14, 12, 0.1), r)
    for x in (-5.4, 5.4):                                                  # two-tier bunks along the side walls
        for z in (0.6, 2.0):
            box('5A4430', (x, 1.0, z), (1.6, 4.4, 0.14), r)
            box('8A8470', (x, 1.0, z + 0.14), (1.4, 4.2, 0.16), r, rough=1.0)
        for y in (-1.2, 3.2):
            bar(r, '4A3826', (x - 0.75, y, 0), (x - 0.75, y, 2.6), 0.06)
    box('2A2A2E', (4.6, -3.6, 0.7), (0.9, 0.9, 1.4), r)                    # the stove
    bar(r, '2A2A2E', (4.6, -3.6, 1.4), (4.6, -3.6, 4.8), 0.1)
    glow_ = box('FF7A30', (4.6, -4.06, 0.6), (0.4, 0.04, 0.25), r, emit=6.0)
    box('6A5038', (0, 0.6, 1.0), (3.6, 1.8, 0.1), r)                       # the table
    for (x, y) in ((-1.6, -0.1), (1.6, -0.1), (-1.6, 1.3), (1.6, 1.3)):
        bar(r, '4A3826', (x, y, 0), (x, y, 1.0), 0.06)
    for x in (-1.6, 1.6):
        box('5A4430', (x, -0.6, 0.55), (1.2, 0.5, 0.08), r)
    bar(r, '1E1E22', (0, 0.6, 4.8), (0, 0.6, 3.6), 0.02)
    add('cone', '2A2E2A', (0, 0.6, 3.55), radius1=0.5, radius2=0.1, depth=0.25, vertices=10, parent=r)
    box('2A3A50', (-6.42, -2.6, 2.6), (0.06, 1.6, 1.2), r, emit=0.5)       # a small window
    lamp = light((0, 0.6, 3.3), 0, 'FFD8A0', 1.2, kind='POINT', parent=r)
    fill = light((0, -6, 4), 0, 'D8E0F0', 6.0, parent=r)
    fill.rotation_euler = (1.1, 0, 0)
    return dict(lights=[lamp, fill], lamp=lamp, fill=fill, glow=glow_)


def make_camp(r):
    """A prison camp in winter: snow, rows of long huts, a double wire fence on posts, a watchtower, a road running west past pines."""
    add('plane', 'DDE4EC', (0, 0, -0.02), size=1600, parent=r, rough=1.0)
    for i in range(4):                                                     # long huts behind the wire
        h = empty((-30 + 16 * i, 26, 0), r)
        box('5A4A3A', (0, 0, 1.6), (12, 5, 3.2), h)
        box('DCE4EE', (0, 0, 3.6), (12.6, 5.6, 0.8), h, rot=(0, 0, 0), rough=1.0)
        for j in range(4):
            box('2A3040', (-4.5 + 3 * j, -2.52, 1.8), (1.0, 0.06, 0.8), h, emit=0.3)
    for row in (14.0, 16.0):                                               # the double fence
        for i in range(30):
            x = -60 + 4 * i
            bar(r, '4A3A2A', (x, row, 0), (x, row, 3.2), 0.1)
        for z in (0.6, 1.2, 1.8, 2.4, 3.0):
            bar(r, '8A8A90', (-60, row, z), (56, row, z), 0.02)
    for i in range(10):
        bar(r, '8A8A90', (-60 + 12 * i, 14.0, 0.3), (-54 + 12 * i, 16.0, 3.0), 0.02)
    tw = empty((24, 15, 0), r)                                             # a watchtower
    for (x, y) in ((-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)):
        bar(tw, '4A3A2A', (x, y, 0), (x * 0.8, y * 0.8, 7.0), 0.12)
    box('5A4A3A', (0, 0, 7.6), (3.0, 3.0, 1.2), tw)
    add('cone', '3A2E24', (0, 0, 8.8), radius1=2.4, radius2=0.0, depth=1.4, vertices=4, parent=tw, rot=(0, 0, PI / 4))
    box('DDE4EC', (0, -30, 0.01), (5, 160, 0.03), r, rough=1.0)            # the road west: trodden snow
    box('B8C0CC', (0, -30, 0.02), (3.4, 160, 0.03), r, rough=1.0)
    for i in range(30):
        sd = -1 if i % 2 else 1
        pine(r, sd * (6 + 12 * rnd(i, 94)), -100 + 6 * i, 10 + 5 * rnd(i, 95), 0.9)
    sun = light((30, -40, 30), 0, 'E8EEF6', 10.0, parent=r)
    sun.rotation_euler = (0.9, 0, 0.6)
    return dict(lights=[sun], sun=sun)


def make_lane(r):
    """An English lane in May: green verges, a hedge, a five-bar gate, a cottage, blossom on the trees."""
    add('plane', '6E9A4E', (0, 0, -0.02), size=1600, parent=r, rough=1.0)
    box('A8987A', (0, 0, 0.01), (4, 200, 0.03), r, rough=1.0)
    for sd in (-1, 1):
        for i in range(24):
            add('ico_sphere', ('3E6A34', '4A7A3A')[i % 2], (sd * 3.6, -60 + 5 * i, 1.0), scale=(0.8, 1.6, 1.0), radius=1.4, subdivisions=1, parent=r, rough=1.0)
    gate = empty((4.2, 4.0, 0), r)
    for x in (0.0, 3.0):
        box('6A5038', (x, 0, 0.9), (0.2, 0.2, 1.8), gate)
    for z in (0.3, 0.65, 1.0, 1.35):
        box('B8A88A', (1.5, 0, z), (3.0, 0.1, 0.12), gate)
    bar(gate, 'B8A88A', (0.1, 0, 0.3), (2.9, 0, 1.35), 0.05)
    for i in range(6):                                                     # trees in blossom
        x = (-1 if i % 2 else 1) * (9 + 4 * rnd(i, 96))
        y = -20 + 9 * i
        add('cylinder', '5A4232', (x, y, 2.0), radius=0.3, depth=4.0, vertices=6, parent=r)
        add('ico_sphere', ('F2D4DC', 'F6E6EA')[i % 2], (x, y, 5.4), scale=(1, 1, 0.85), radius=2.8, subdivisions=1, parent=r, rough=1.0)
    ct = empty((-14, 22, 0), r, (0, 0, 0.3))                               # a cottage
    box('E8DCC4', (0, 0, 2.0), (8, 5, 4), ct)
    add('cone', '6A4A3A', (0, 0, 5.2), radius1=5.4, radius2=0.0, depth=2.6, vertices=4, rot=(0, 0, PI / 4), parent=ct, scale=(1.05, 0.7, 1))
    for x in (-2.2, 2.2):
        box('2A3A4A', (x, -2.52, 2.4), (1.0, 0.06, 1.0), ct, emit=0.2)
    box('4A3A2A', (0, -2.52, 1.1), (1.0, 0.06, 2.2), ct)
    sun = light((20, -30, 30), 0, 'FFF4DC', 12.0, parent=r)
    sun.rotation_euler = (0.8, 0, 0.6)
    return dict(lights=[sun], sun=sun)


def make_works(r):
    """A chemical works: a yard of tanks, pipework on gantries, a brick shed wall, steam from a vent."""
    box('6A6A68', (0, 0, -0.05), (120, 120, 0.1), r)
    box('8A4A3A', (0, 14, 6), (60, 1.0, 12), r)                           # brick wall behind
    for i in range(12):
        box('7A4232', (-27 + 5 * i, 13.4, 3 + 3 * (i % 3)), (4.6, 0.1, 0.14), r)
    for j, x in enumerate((-12, -4, 4, 12)):                               # four tanks
        add('cylinder', ('A8B0B4', '98A0A4')[j % 2], (x, 6, 4.0), radius=3.0, depth=8.0, vertices=14, parent=r, rough=0.5)
        add('cone', 'A8B0B4', (x, 6, 8.6), radius1=3.0, radius2=0.6, depth=1.2, vertices=14, parent=r, rough=0.5)
        bar(r, '5A6066', (x + 3.0, 6, 0), (x + 3.0, 6, 8.0), 0.06)
    for z in (2.0, 3.0):                                                   # pipework
        bar(r, 'C87A3A' if z < 2.5 else '4A7A9A', (-20, 1.6, z), (20, 1.6, z), 0.18)
    for x in (-16, -8, 0, 8, 16):
        bar(r, '3A3E44', (x, 1.6, 0), (x, 1.6, 3.4), 0.1)
        box('3A3E44', (x, 1.6, 3.4), (0.3, 1.2, 0.2), r)
    for i in range(4):
        add('cylinder', '2A4A6A', (-6 + 1.0 * i, -4.5, 0.55), radius=0.45, depth=1.1, vertices=10, parent=r, rough=0.6)    # drums
    steam = [add('ico_sphere', 'E8ECF0', (16, 6, 9.5 + 1.2 * i), radius=1.0, subdivisions=1, parent=r, rough=1.0, alpha=0.5) for i in range(4)]
    sun = light((20, -40, 30), 0, 'F0EEE8', 12.0, parent=r)
    sun.rotation_euler = (0.9, 0, 0.5)
    return dict(lights=[sun], sun=sun, steam=steam)


def make_studio(r):
    """A television studio of the 1980s: a dark floor, a low set with two armchairs and a coffee table, a big camera on a pedestal,
    lights on a grid. Nothing written anywhere."""
    box('1A1C22', (0, 0, -0.05), (30, 30, 0.1), r)
    box('2A4A6E', (0, 3.0, 0.15), (10, 6, 0.3), r)                         # the low stage
    box('3A6A9A', (0, 6.0, 3.0), (12, 0.2, 6.0), r)                        # backdrop
    for i in range(6):
        box('FF7A1A' if i % 2 else 'FFB000', (-5 + 2 * i, 5.88, 3.5), (0.9, 0.05, 3.6), r, emit=1.2)
    for x, yaw in ((-1.6, 0.5), (1.6, -0.5)):
        c = empty((x, 2.6, 0.3), r, (0, 0, yaw))
        box('B8604A', (0, 0, 0.45), (1.3, 1.2, 0.5), c)
        box('B8604A', (0, 0.55, 1.1), (1.3, 0.25, 1.0), c)
        for sx in (-0.6, 0.6):
            box('A8503A', (sx, 0, 0.8), (0.2, 1.2, 0.5), c)
    box('C8C8D0', (0, 1.6, 0.6), (1.2, 0.8, 0.08), r)
    add('cylinder', 'F2F2F0', (0.2, 1.6, 0.75), radius=0.08, depth=0.2, vertices=8, parent=r)
    cam_ = empty((0.6, -5.5, 0), r, (0, 0, 0.1))                           # the studio camera on its pedestal
    add('cylinder', '2A2A30', (0, 0, 0.1), radius=0.8, depth=0.2, vertices=10, parent=cam_)
    bar(cam_, '4A4A50', (0, 0, 0.1), (0, 0, 1.6), 0.12)
    box('3A3A42', (0, 0, 1.9), (0.8, 1.6, 0.8), cam_)
    add('cylinder', '15151A', (0, -1.0, 1.9), rot=(PI / 2, 0, 0), radius=0.28, depth=0.6, vertices=10, parent=cam_)
    tally = add('cube', 'FF2A1A', (0, -0.82, 2.35), scale=(0.12, 0.04, 0.08), size=1, parent=cam_, emit=8.0)
    for x in (-6, -2, 2, 6):                                               # lights on the grid
        add('cylinder', '2A2A30', (x, -2, 7.5), rot=(0.8, 0, 0), radius=0.4, depth=0.8, vertices=8, parent=r)
    key = light((-3, -3, 6), 0, 'FFF0DC', 4.0, parent=r, target=None)
    key.rotation_euler = (0.7, 0, -0.4)
    rim = light((3, 6, 5), 0, 'FFB070', 3.0, parent=r)
    rim.rotation_euler = (-0.9, 0, 0.4)
    return dict(lights=[key, rim], key=key, rim=rim, tally=tally)


def make_bldg(r):
    """A plain modern squadron building: pale brick, glass doors, a flagless pole, a bronze plaque under a cover by the door."""
    add('plane', '6E8A5A', (0, 0, -0.02), size=1600, parent=r, rough=1.0)
    box('9A9690', (0, -6, 0.0), (40, 8, 0.06), r, rough=0.9)
    box('C8B49A', (0, 4, 4.0), (30, 8, 8), r)
    box('3A4450', (0, -0.05, 1.6), (3.6, 0.1, 3.2), r, rough=0.1)          # glass doors
    box('E8E8E4', (0, -0.1, 3.3), (4.0, 0.1, 0.2), r)
    for i in range(6):
        box('4A5A6A', (-12 + 4.8 * i if i < 3 else -12 + 4.8 * i + 4.8, -0.03, 4.6), (2.6, 0.06, 1.6), r, rough=0.1)
    box('B8A488', (0, 4, 8.2), (31, 9, 0.4), r)
    plaque = box('8A6A3A', (3.4, -0.08, 2.0), (1.0, 0.06, 0.7), r, rough=0.35)
    cover = box('FF7A1A', (3.4, -0.14, 2.0), (1.1, 0.04, 0.8), r, rough=1.0)
    for i in range(6):                                                     # shrubs
        add('ico_sphere', '3E6A34', (-14 + 5.6 * i, -1.4, 0.6), scale=(1.4, 0.8, 0.7), radius=1.0, subdivisions=1, parent=r, rough=1.0)
    sun = light((20, -30, 25), 0, 'FFF4E0', 10.0, parent=r)
    sun.rotation_euler = (0.9, 0, 0.6)
    return dict(lights=[sun], sun=sun, plaque=plaque, cover=cover)


MAKERS = dict(garden=make_garden, field=make_field, stream=make_stream, hosp=make_hosp, hut=make_hut, camp=make_camp, lane=make_lane,
              works=make_works, studio=make_studio, bldg=make_bldg)
_build0, _reset0 = build, reset


def build():
    S = _build0()
    S['sets'] = {}
    for name, fn in MAKERS.items():
        root = empty(SETPOS[name])
        d = fn(root)
        d.update(root=root, all=kids(root))
        S['sets'][name] = d
    S['nick'] = K.Rig(dict(top='7A8A5A', pants='4A4036', hand=SKIN, boot='2A2018', fore='E2B48C'), K.human_head(SKIN, '5A3E24'))
    S['old'] = K.Rig(dict(top='6A5A4A', pants='3A3A40', hand=SKIN, boot='1E1C22', fore='6A5A4A'), K.human_head(SKIN, 'B8B6B0'))
    S['crew'] = [K.Rig(dict(top=c, pants='3E4658', hand='5A3E24', boot='2A2018', fore=c), airman_head) for c in CREWC]
    S['pows'] = [K.Rig(dict(POWC, top=c, fore=c), K.human_head(sk, hr)) for c, sk, hr in
                 (('5A6478', 'D8AC88', '3A2A1E'), ('54607A', 'C89C7C', '6A5238'), ('606A7C', 'E0B494', '2A2420'))]
    new = [S['nick'], S['old']] + S['crew'] + S['pows']
    S['humans'] += new
    S['cast'] += new
    S['cig'] = keep(add('cube', 'F4F0E4', FAR, scale=(0.03, 0.18, 0.03), size=1))
    S['ember'] = keep(add('ico_sphere', 'FF6A1A', FAR, radius=0.04, subdivisions=1, emit=40.0))
    S['whistle'] = keep(add('cylinder', 'C9CED6', FAR, rot=(PI / 2, 0, 0), radius=0.05, depth=0.2, vertices=8, rough=0.2))
    S['sheet2'] = keep(add('cube', 'F2EAD2', FAR, scale=(0.5, 0.7, 0.015), size=1, rough=1.0))
    S['kitbag'] = keep(add('cylinder', '7A7458', FAR, rot=(0, PI / 2, 0), radius=0.3, depth=1.1, vertices=8, rough=1.0))
    reset(S)
    return S


def reset(S):
    _reset0(S)
    if 'sets' not in S:
        return
    for d in S['sets'].values():
        vis(d['all'], False)
        for l in d['lights']:
            l.data.energy = 0


def inside(S, name, skyname, stars=False):
    sky(S, skyname, stars)
    d = S['sets'][name]
    vis(d['all'], True)
    for l in d['lights']:
        l.data.energy = 0
    return d


def put(S, rig, name, x, y, z, yaw, pitch=0.0):
    rig.place(SP(name, x, y, z), yaw, pitch)
    return rig


def look(S, name, pos, tgt, lens=35, roll=0.0):
    shoot(S, SETPOS[name], pos, tgt, lens, roll)


def talk(rig, lt, rate=4.0, amt=0.35):
    rig.jawv = amt * abs(math.sin(lt * rate))


# ---------------------------------------------------------------- before the war
def garden_wide(S, k, t, lt):
    """Inside the glasshouse: young Nicholas works along a bench of seedlings, pricking them out into a tray. Rook leans on the
    wheelbarrow by the door, arms folded, unimpressed."""
    d = inside(S, 'garden', 'garden')
    d['sun'].data.energy = 1400
    n = put(S, S['nick'], 'garden', -2.0, lerp(-2.6, -1.4, sm(lt / 3.0)), 0.0, -PI / 2 + 0.2)
    w = math.sin(lt * 3.2)
    n.apply(P('stand', aR=(1.0 + 0.2 * w, 0.0, 0.9), aL=(0.9, 0.05, 1.1), lean=0.3, head=(0.45, 0.1)))
    n.face = 'calm'
    rk = put(S, S['rook'], 'garden', -0.9, 4.6, 0.0, facing((-0.9, 4.6), (-2.0, -1.8)))
    rk.apply(blend(P('cross', head=(0.1, 0.0)), P('tap', head=(0.15, -0.1)), sm((lt - 1.6) / 0.5)))
    S['rface'] = 'low'
    S['hat_tip'] = 0.3
    look(S, 'garden', (lerp(2.8, 2.2, k), lerp(-8.5, -7.6, k), lerp(2.6, 2.4, k)), (-1.2, 0.8, 1.4), 26)


def garden_close(S, k, t, lt):
    """Close on him at the bench: he firms a seedling into its pot with both thumbs and looks up, out through the glass."""
    d = inside(S, 'garden', 'garden')
    d['sun'].data.energy = 1400
    n = put(S, S['nick'], 'garden', 2.0, 0.6, 0.0, PI / 2 - 0.1)
    up = sm((lt - 1.5) / 0.6)
    n.apply(P('stand', aR=(0.7, -0.1, 0.9 + 0.15 * math.sin(lt * 6) * (1 - up)), aL=(0.65, -0.1, 1.0), lean=0.35 * (1 - up) + 0.05,
              head=(lerp(0.5, -0.15, up), lerp(0.0, 0.5, up))))
    n.face = 'calm' if up < 0.5 else 'warm'
    h = wpos(n.head)
    shoot(S, (0, 0, 0), (h[0] + 1.9, h[1] - lerp(2.4, 2.0, k), h[2] + 0.15), (h[0] + 0.2, h[1], h[2] - 0.35), 40)


# ---------------------------------------------------------------- the airfield
def field_dusk(S, k, t, lt):
    """An airfield at dusk. He walks out towards the parked bomber in his flying kit, carrying his helmet's weight on his shoulders;
    Rook strides beside him and pops his coat collar."""
    d = inside(S, 'field', 'dusk')
    d['sun'].data.energy = 2.5
    u = lt * 0.9
    m = put(S, S['man'], 'field', lerp(8.0, 5.5, k), lerp(-26.0, -20.0, k), 0.0, PI * 0.9)
    m.apply(K.walk(t, 1.1))
    m.face = 'calm'
    rk = put(S, S['rook'], 'field', lerp(10.2, 7.7, k), lerp(-25.0, -19.0, k), 0.0, PI * 0.9)
    pop = sm((lt - 0.8) / 0.4) * (1 - sm((lt - 1.8) / 0.4))
    rk.apply(blend(K.walk(t + 0.3, 1.1), P('hat', aL=(0.2, 1.9, 1.6, -1.5)), pop))
    S['rface'] = 'calm'
    look(S, 'field', (lerp(13.0, 11.5, k), lerp(-33.0, -30.0, k), lerp(2.4, 2.6, k)), (lerp(7.0, 5.5, k), -18.0, 2.4), 28)


def crew_seven(S, k, t, lt):
    """Seven men in flying kit by the tail of their bomber, at dusk: they wait, talk, one laughs. He stands at the end of the line,
    by his turret. Rook counts them along the line with a wingtip."""
    d = inside(S, 'field', 'dusk')
    d['sun'].data.energy = 2.5
    rigs = S['crew'][:3] + [S['man']] + S['crew'][3:]
    for i, rg in enumerate(rigs):
        x = -6.0 + 2.0 * i
        put(S, rg, 'field', x, -27.0 + 0.4 * rnd(i, 97), 0.0, 0.15 * (rnd(i, 98) - 0.5))
        rg.apply(P('stand', aR=(0.2 + 0.3 * rnd(i, 99), 0.15, 0.4), head=(0.05, 0.4 * math.sin(lt * 0.8 + i))))
        rg.face = 'warm' if i % 3 == 0 else 'calm'
        talk(rg, lt + i, 3.0, 0.25 if i in (1, 4) else 0.0)
    cnt = min(6, int(lt / 0.45))
    rk = put(S, S['rook'], 'field', lerp(-7.0, 7.0, sm(lt / 3.0)), -30.0, 0.0, facing((0, -30), (0, -27)))
    rk.apply(blend(K.walk(t, 1.2), P('point', aR=(1.2, 0.1, 0.1), head=(0.2, 0.0)), 0.6))
    S['rface'] = 'calm'
    look(S, 'field', (lerp(-3.0, 1.0, k), -39.0, 2.4), (0.0, -27.0, 2.4), 30)


def takeoff(S, k, t, lt):
    """Dusk over the airfield: a bomber lifts off the far end of the runway and climbs away, another taxies behind it."""
    d = inside(S, 'field', 'dusk')
    d['sun'].data.energy = 2.5
    look(S, 'field', (lerp(-40.0, -46.0, k), -40.0, 3.0), (-120.0, 60.0, 12.0 + 10 * k), 30)
    S['bomber'].location = SP('field', lerp(-60.0, -260.0, k), 60.0, lerp(4.0, 34.0, sm(k * 1.2)))
    S['bomber'].rotation_euler = (lerp(0.0, 0.12, sm(k * 2)), 0.0, PI / 2)


# ---------------------------------------------------------------- in the air
def stream(S, k, t, lt):
    """Night: a loose line of bombers flying above the cloud, small engine glows, stars. The camera drifts alongside the nearest."""
    d = inside(S, 'stream', 'night', True)
    d['moon'].data.energy = 3.0
    o = SETPOS['stream']
    air(S, o, t, (0, 60, 0), top=-12)
    for i, p in enumerate(d['planes']):
        p.rotation_euler = (0.02 * math.sin(t + i), 0.04 * math.sin(t * 0.7 + i), 0.0)
    shoot(S, o, (lerp(-62.0, -56.0, k), lerp(-92.0, -84.0, k), lerp(9.0, 8.0, k)), (-20.0, -40.0, 0.0), 32)


def turret_calm(S, k, t, lt):
    """In the rear turret before anything happens: he sits hunched between the guns, scanning the dark, his breath fogging. Rook
    has squeezed in behind him on the tail, knees up, hat brim bent against the frame."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0), top=-6)
    b = S['bomber']
    b.location = SKYO
    b.rotation_euler = (0.01 * math.sin(t * 1.3), 0.03 * math.sin(t * 0.9), 0.0)
    m = S['man']
    m.root.parent = b
    m.place((0, 16.2, -1.55), PI)
    scan = math.sin(lt * 0.9)
    m.apply(P('sit', aL=(1.1, 0.25, 0.9), aR=(1.2, 0.3, 0.7), lean=0.08, head=(-0.05, 0.6 * scan), lift=-0.5))
    m.face = 'calm'
    rk = S['rook']
    rk.root.parent = b
    rk.place((1.25, 14.9, 1.25), PI - 0.6)
    rk.apply(P('sit', aL=(0.9, 0.4, 1.4), aR=(0.9, 0.4, 1.4), head=(0.35, -0.3)))
    S['rface'], S['hat_tip'] = 'low', 0.6
    glow(S, 0, at(SKYO, 0.6, 18.8, 1.0), 900, 0.0)
    shoot(S, SKYO, (lerp(3.4, 2.9, k), lerp(23.0, 22.0, k), lerp(1.9, 1.7, k)), (0.6, 15.8, 1.2), 30)


def rack_calm(S, k, t, lt):
    """Inside the fuselage, just behind the turret doors: the parachute pack in its rack, dim blue light. Rook steps in, raps the pack
    with a knuckle and points from it back towards the turret: there, and he's here."""
    sky(S, 'room')
    glow(S, 0, at(BAY, -0.4, -2.0, 2.6), 160, 0.0)
    S['flamp'][0].data.color = (0.6, 0.75, 1.0)
    glow(S, 1, at(BAY, 2.5, -2.4, 1.0), 90, 0.0)
    S['flamp'][1].data.color = (0.6, 0.75, 1.0)
    rk = S['rook']
    rk.place(at(BAY, lerp(4.2, 2.3, sm(lt / 0.8)), -1.3, -0.0), facing((2.3, -1.3), (0.0, 0.3)))
    tap = sm((lt - 0.8) / 0.3) * (1 - sm((lt - 1.6) / 0.3))
    pt = sm((lt - 1.8) / 0.4)
    rk.apply(blend(blend(K.walk(t, 1.3), P('point', aR=(1.2, 0.1, 0.4)), sm((lt - 0.6) / 0.3)), P('point', aR=(1.5, -0.9, 0.05), head=(0.0, 0.8)), pt))
    S['rface'] = 'calm'
    shoot(S, BAY, (lerp(-1.6, -1.2, k), lerp(-6.2, -5.4, k), lerp(2.0, 1.8, k)), (1.0, 0.0, 1.6), 30)


def gunner_face(S, k, t, lt):
    """Close on his face in the turret, lit orange by the fire behind him. He looks back at it, then out at the dark, and his jaw sets."""
    sky(S, 'night', True)
    air(S, SKYO, t, (0, 85, 0), top=-6)
    b = burning(S, t, 2.2, 6)
    fire(S, [(0.7, 14.5, 0.2), (-0.7, 14.4, 0.8), (0.1, 14.3, 1.5), (-1.9, 15.2, 0.6)], t, 1.0, (0, 1, 0.7), i0=12, par=b)
    glow(S, 2, at(SKYO, 0.3, 15.0, 1.0), 2200, t)
    m = S['man']
    m.root.parent = b
    turn = lerp(2.0, 0.0, sm((lt - 0.8) / 0.6))
    m.place((0, 16.2, -1.55), PI)
    m.apply(P('sit', aL=(1.1, 0.25, 0.9), aR=(1.2, 0.3, 0.7), lean=0.05, head=(lerp(0.0, 0.2, sm((lt - 1.6) / 0.5)), turn), lift=-0.5))
    m.face = 'wide' if lt < 1.6 else 'shut'
    h = mhead(S)
    shoot(S, (0, 0, 0), (h[0] + 0.5, h[1] + 2.1, h[2] + 0.15), (h[0], h[1], h[2] - 0.05), 44)


# ---------------------------------------------------------------- the wood, night
def wake_sit(S, pose=None):
    m = sat(S, -0.95, pose, x=0.2, y=0.4)
    for o in S['strap']:
        o.hide_render = True
    return m


def cigarette(S, k, t, lt):
    """Night under the pines, stars through the hole above: sitting in the snow in his socks, he strikes a match, lights a cigarette,
    and the ember glows. His breath and the smoke go up together."""
    sky(S, 'wood', True)
    S['sun'].data.energy = 1.4
    m = wake_sit(S, dict(aR=(1.25, -0.25, 2.1, 0.4), aL=(1.2, -0.2, 2.0, 0.6), head=(0.1, 0.0)))
    m.face = 'tired'
    h = mhead(S)
    lit = sm((lt - 0.9) / 0.2)
    S['cig'].location = (h[0], h[1] - 0.4, h[2] - 0.12)
    S['ember'].location = (h[0], h[1] - 0.5, h[2] - 0.12)
    S['ember'].scale = (1 + 1.5 * lit, 1 + 1.5 * lit, 1 + 1.5 * lit)
    S['lanlamp'].location = (h[0] + 0.1, h[1] - 0.7, h[2])
    S['lanlamp'].data.energy = 30 + 160 * lit * (0.85 + 0.15 * math.sin(t * 9))
    S['lanlamp'].data.color = (1.0, 0.55, 0.25)
    snowfall(S, WOOD, t, 10, 0, 2.6, 7.0, 0.9)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.6, 1.3, k), h[1] - lerp(3.2, 2.6, k), h[2] + 0.2), (h[0], h[1], h[2] - 0.3), 40)


def whistle(S, k, t, lt):
    """Wider: he blows his whistle, cheeks full, into the dark wood. Rook, crouched in the snow beside him, flinches and holds his hat."""
    sky(S, 'wood', True)
    S['sun'].data.energy = 1.6
    blow = 0.5 + 0.5 * math.sin(lt * 4.0)
    m = wake_sit(S, dict(aR=(1.3, -0.2, 2.2, 0.4), aL=(0.4, 0.4, 0.6), head=(-0.2, 0.2)))
    m.face, m.jawv = 'shut', 0.2
    h = mhead(S)
    S['whistle'].location = (h[0], h[1] - 0.38, h[2] - 0.1)
    rk = S['rook']
    rk.place(at(WOOD, 2.2, -0.4, 0.0), facing((2.2, -0.4), (0.2, 0.4)))
    crouch = P('stand', lL=(1.1, 1.7), lR=(1.1, 1.7), lift=-0.5, lean=0.3, head=(0.1, 0.0))
    rk.apply(blend(crouch, P('hat', lL=(1.1, 1.7), lR=(1.1, 1.7), lift=-0.5, lean=0.15), sm((lt - 0.3) / 0.3)))
    S['rface'] = 'shocked' if lt > 0.3 else 'calm'
    S['hat_jump'] = 0.06 * blow
    snowfall(S, WOOD, t, 10, 0, 3.0, 7.0, 1.0)
    shoot(S, WOOD, (lerp(1.6, 2.0, k), lerp(-4.6, -4.2, k), 1.5), (1.2, 0.1, 1.2), 32)


# ---------------------------------------------------------------- hospital, the hut, the camp
def hospital(S, k, t, lt):
    """A hospital bed: he lies propped up with a dressing round his head, burns on his hands bandaged. A guard in a cap sits by the
    door. Rook, at the window, looks from one to the other and lowers his hat brim."""
    d = inside(S, 'hosp', 'inside')
    d['lamp'].data.energy, d['win'].data.energy = 120, 220
    no_harness(S, True)
    m = put(S, S['man'], 'hosp', -1.2, 0.15, 0.24, 0.0, -0.95)
    m.apply(P('stand', aL=(0.3, 0.2, 0.5), aR=(0.3, 0.2, 0.5), lL=(0.95, 0.0), lR=(0.95, 0.0), head=(0.75, 0.15 * math.sin(lt * 0.6))))
    m.face = 'tired'
    g = put(S, S['men'][0], 'hosp', -3.6, -0.6, 0.0, facing((-3.6, -0.6), (-1.2, 1.6)))
    g.apply(P('hips', head=(0.1, 0.2 * math.sin(lt * 0.7))))
    rk = put(S, S['rook'], 'hosp', 2.4, 3.6, 0.0, facing((2.4, 3.6), (0.0, -1.5)))
    rk.apply(blend(P('stand', head=(0.0, 0.6 * math.sin(lt * 0.9))), P('hat'), sm((lt - 1.8) / 0.4)))
    S['rface'] = 'low'
    look(S, 'hosp', (lerp(3.6, 3.0, k), lerp(-4.8, -4.2, k), lerp(3.0, 2.8, k)), (0.2, 1.8, 1.4), 26)


def witnesses(S, k, t, lt):
    """In a wooden hut, under a hanging lamp: three British prisoners lean over a sheet on the table and sign it one after another,
    while he stands at the end of the table. Rook reads over their shoulders."""
    d = inside(S, 'hut', 'inside')
    d['lamp'].data.energy, d['fill'].data.energy = 420, 420
    no_harness(S, False)
    S['band'].hide_render = True
    S['sheet2'].location = SP('hut', 0.0, 0.6, 1.07)
    S['sheet2'].rotation_euler = (0, 0, 0.1)
    who = min(2, int(lt / 0.9))
    for i, rg in enumerate(S['pows']):
        x = -1.0 + 1.0 * i
        lean = 0.55 if i == who else 0.1
        put(S, rg, 'hut', x, 1.9, 0.0, 0.0)
        rg.apply(P('stand', aR=(1.0 + 0.15 * math.sin(lt * 8) if i == who else 0.3, 0.0, 0.6), lean=lean, head=(0.5 if i == who else 0.2, 0.0)))
        rg.face = 'calm'
    m = put(S, S['man'], 'hut', 2.7, 0.8, 0.0, facing((2.7, 0.8), (0.0, 0.6)))
    m.apply(P('stand', head=(0.15, 0.0)))
    m.face = 'warm'
    rk = put(S, S['rook'], 'hut', -2.4, lerp(2.4, 2.2, k), 0.0, facing((-2.4, 2.3), (-0.6, 0.6)))
    rk.apply(P('tap', head=(0.35, 0.0)))
    S['rface'] = 'calm'
    look(S, 'hut', (lerp(1.2, 0.6, k), lerp(-5.0, -4.4, k), lerp(3.2, 3.0, k)), (0.4, 1.4, 1.8), 28)


def camp_famous(S, k, t, lt):
    """Inside the hut, evening, stove glowing: prisoners crowd round him at the table as he tells it again, hands showing the drop.
    Rook sits on the top bunk, legs dangling, listening for once."""
    d = inside(S, 'hut', 'inside')
    d['lamp'].data.energy, d['fill'].data.energy = 480, 260
    no_harness(S, False)
    m = put(S, S['man'], 'hut', 0.0, 1.6, 0.0, PI)
    drop = math.sin(lt * 2.0)
    m.apply(P('stand', aR=(1.4 + 0.5 * drop, 0.2, 0.3), aL=(1.0, 0.3, 0.9), head=(0.0, 0.2 * drop)))
    m.face = 'warm'
    talk(m, lt, 4.5, 0.4)
    for i, (x, y) in enumerate(((-1.6, -0.4), (0.0, -0.9), (1.6, -0.4))):
        rg = put(S, S['pows'][i], 'hut', x, y, 0.0, facing((x, y), (0.0, 1.6)))
        rg.apply(P('stand', lean=0.15, head=(-0.05, 0.0), aL=(0.4, 0.1, 1.2), aR=(0.4, 0.1, 1.2)))
        rg.face = 'laugh' if (i == 1 and lt > 1.4) else 'wide'
        talk(rg, lt + i, 3, 0.3 if lt > 1.4 else 0.0)
    rk = put(S, S['rook'], 'hut', -5.2, 0.4, 2.2 - 0.55, facing((-5.2, 0.4), (0.0, 1.0)))
    rk.apply(P('sit', head=(0.2, 0.0)))
    S['rface'] = 'soft'
    look(S, 'hut', (lerp(2.2, 1.8, k), lerp(-4.6, -4.0, k), lerp(2.6, 2.5, k)), (-1.0, 0.8, 1.9), 28)


def camp_wire(S, k, t, lt):
    """Winter outside: the double wire fence, the watchtower, long huts under snow. Snow falls; the camera tracks slowly along the wire."""
    d = inside(S, 'camp', 'winter')
    d['sun'].data.energy = 3.0
    snowfall(S, SETPOS['camp'], t, 18, 0, 8.0, 9.0, 1.2)
    for i in range(18):
        S['snowb'][i].location = (S['snowb'][i].location[0] + lerp(-14, 6, k), S['snowb'][i].location[1] + 6.0, S['snowb'][i].location[2])
    look(S, 'camp', (lerp(-16.0, 4.0, k), 4.0, 2.6), (lerp(-6.0, 14.0, k), 22.0, 3.0), 28)


def long_march(S, k, t, lt):
    """The march west: a line of prisoners trudging through snow on a road between pines, heads down, collars up. He is among them,
    limping a little. Rook trudges at the side of the column, hunched, wings tucked."""
    d = inside(S, 'camp', 'winter')
    d['sun'].data.energy = 2.4
    no_harness(S, False)
    rigs = [S['pows'][0], S['man'], S['pows'][1], S['pows'][2]] + S['crew'][:3]
    for i, rg in enumerate(rigs):
        y = -20.0 - 3.0 * i + 2.2 * lt
        put(S, rg, 'camp', 0.5 * math.sin(i * 1.7), y, 0.0, PI)
        rg.apply(blend(K.walk(t + i * 0.37, 0.8), P('stand', head=(0.45, 0.0), aL=(0.4, -0.1, 1.6, 1.2), aR=(0.4, -0.1, 1.6, 1.2)), 0.45))
        rg.face = 'tired'
    rk = put(S, S['rook'], 'camp', -2.0, -21.5 + 2.2 * lt, 0.0, PI)
    rk.apply(blend(K.walk(t + 0.2, 0.8), P('cross', head=(0.4, 0.0)), 0.5))
    S['rface'], S['hat_tip'] = 'sad', 0.5
    snowfall(S, SP('camp', 0.0, -18.0 + 2.2 * lt, 0.0), t, 20, 0, 6.0, 7.0, 1.4)
    look(S, 'camp', (lerp(5.0, 4.2, k), -12.5 + 2.2 * lt, 2.3), (0.8, -24.0 + 2.2 * lt, 1.8), 30)


def home_may(S, k, t, lt):
    """May: a green lane in blossom. He walks home with a kitbag on his shoulder, and stops at a gate to look at it all. Rook sits
    on the top bar of the gate and, for once, says nothing."""
    d = inside(S, 'lane', 'spring')
    d['sun'].data.energy = 4.0
    no_harness(S, False)
    stop = sm((lt - 2.0) / 0.6)
    m = put(S, S['man'], 'lane', 1.0, lerp(-6.0, 2.0, sm(lt / 2.6)), 0.0, PI + 0.6 * stop)
    pose = blend(K.walk(t, 1.1), P('stand', head=(-0.1, 0.0)), stop * 0.999)
    pose['aR'] = (2.6, 0.3, 1.9, 0.0)
    m.apply(pose)
    m.face = 'warm'
    sh_ = wpos(S['man'].sh[1])
    S['kitbag'].location = (sh_[0], sh_[1] + 0.15, sh_[2] + 0.28)
    S['kitbag'].rotation_euler = (PI / 2, 0, m.root.rotation_euler[2])
    rk = put(S, S['rook'], 'lane', 5.6, 4.0, 1.35 - 0.55, PI + 0.5)
    rk.apply(P('sit', head=(0.1, -0.4)))
    S['rface'] = 'soft'
    look(S, 'lane', (lerp(-1.6, -1.2, k), lerp(8.0, 7.2, k), 2.0), (2.4, 1.6, 1.8), 30)


# ---------------------------------------------------------------- after the war
def works(S, k, t, lt):
    """A chemical works on a grey day: tanks, pipework, steam from a vent. He walks along the pipe run in work clothes with a clipboard."""
    d = inside(S, 'works', 'winter')
    d['sun'].data.energy = 3.2
    for i, s_ in enumerate(d['steam']):
        z = (lt * 0.8 + i * 0.6) % 2.4
        s_.location = (16 + 0.4 * z, 6, 9.0 + z * 1.6)
        s_.scale = (1 + 0.5 * z, 1 + 0.5 * z, 1 + 0.5 * z)
    n = put(S, S['nick'], 'works', lerp(-4.0, 2.0, k), -1.0, 0.0, -PI / 2)
    n.apply(blend(K.walk(t, 1.0), P('stand', aL=(1.0, 0.0, 1.4, 0.6)), 0.4))
    n.face = 'calm'
    S['pad'].location = wpos(n.hands[0], (0, -0.2, -0.1))
    S['pad'].rotation_euler = (1.2, 0, -PI / 2)
    look(S, 'works', (lerp(-10.0, -6.0, k), -12.0, 2.6), (lerp(-2.0, 2.0, k), 2.0, 2.4), 28)


def tv_studio(S, k, t, lt):
    """A television studio of the 1980s, older Nicholas in an armchair under the lights, telling it with his hands: the fall, the
    trees. Behind the big camera, its red light on, Rook watches from the dark with his arms folded, then gives one slow nod."""
    d = inside(S, 'studio', 'inside')
    d['key'].data.energy, d['rim'].data.energy = 900, 500
    o = put(S, S['old'], 'studio', 1.6, 2.6, 0.45, -0.5)
    o.apply(P('stand', **SIT, aR=(1.1 + 0.4 * math.sin(lt * 2.2), 0.3, 0.6), aL=(0.8, 0.1, 1.2), head=(0.0, 0.3)))
    o.face = 'warm'
    talk(o, lt, 4.2, 0.4)
    ho = put(S, S['pows'][2], 'studio', -1.6, 2.6, 0.45, 0.5)
    ho.apply(P('stand', **SIT, aL=(0.75, -0.05, 1.2, 0.8), aR=(0.75, -0.05, 1.2, 0.8), head=(0.0, -0.3)))
    ho.face = 'wide'
    rk = put(S, S['rook'], 'studio', 2.6, -4.2, 0.0, facing((2.6, -4.2), (1.0, 2.6)))
    rk.apply(P('cross', head=(0.25 * sm((lt - 1.4) / 0.3) * (1 - sm((lt - 1.9) / 0.3)), 0.0)))
    S['rface'] = 'calm'
    look(S, 'studio', (lerp(-2.4, -1.8, k), lerp(-7.6, -7.0, k), lerp(2.8, 2.6, k)), (0.8, 0.4, 1.8), 30)


def plaque(S, k, t, lt):
    """A plain modern squadron building in sunshine. Rook pulls the orange cover off a small bronze plaque by the door (nothing
    legible on it) and steps back, takes his hat off and holds it to his chest."""
    d = inside(S, 'bldg', 'spring')
    d['sun'].data.energy = 4.0
    u = sm((lt - 0.4) / 0.5)
    d['cover'].location = (3.4, -0.14 - 0.4 * u, 2.0 - 2.0 * u)
    d['cover'].rotation_euler = (0.8 * u, 0, 0.3 * u)
    rk = put(S, S['rook'], 'bldg', lerp(4.2, 4.6, u), lerp(-1.4, -2.6, sm((lt - 1.0) / 0.5)), 0.0, facing((4.4, -2.0), (3.4, 0.0)))
    rk.apply(blend(P('reach', aR=(1.6, -0.2, 0.3), head=(0.0, 0.0)), P('stand', aR=(0.9, -0.3, 1.8, 1.0), head=(0.25, 0.0)), sm((lt - 1.0) / 0.5)))
    S['rface'] = 'soft'
    S['hat_off'] = sm((lt - 1.4) / 0.4)
    look(S, 'bldg', (lerp(0.6, 1.2, k), lerp(-7.4, -6.4, k), lerp(2.2, 2.1, k)), (3.6, -0.8, 2.0), 30)


def dawn_wood(S, k, t, lt):
    """The pine wood at dawn, nobody in it: the dent in the snow, the broken boughs, the hole in the trees above. The camera
    rises slowly towards the light."""
    sky(S, 'dawn')
    snowfall(S, WOOD, t, 12, 0, 4.0, 9.0, 0.8)
    shoot(S, WOOD, (lerp(-3.0, -2.2, k), lerp(-9.0, -8.0, k), lerp(1.2, 3.2, k)), (0.0, 0.0, lerp(1.0, 6.0, k)), 26)


def photo_thumb(S, k, t, lt):
    """The thumbnail picture: the gunner in the open turret, his face lit orange by the fire behind him, on the right of the
    frame; the dark night on the left for the words."""
    sky(S, 'night', True)
    air(S, SKYO, 1.0, (0, 85, 0), top=-6)
    b = burning(S, 1.0, 2.2, 6)
    fire(S, [(0.7, 14.5, 0.2), (-0.7, 14.4, 0.8), (0.1, 14.3, 1.5), (-1.9, 15.2, 0.6), (1.6, 14.6, 1.2)], 1.0, 1.1, (0, 1, 0.7), i0=12, par=b)
    glow(S, 2, at(SKYO, 0.3, 15.0, 1.0), 2600, 1.0)
    m = S['man']
    m.root.parent = b
    m.place((0, 16.2, -1.55), PI)
    m.apply(P('sit', aL=(1.1, 0.25, 0.9), aR=(1.2, 0.3, 0.7), lean=0.05, head=(-0.1, 0.45), lift=-0.5))
    m.face, m.jawv = 'wide', 0.35
    h = mhead(S)
    S['lanlamp'].location = (h[0] + 0.6, h[1] + 1.6, h[2] + 0.4)
    S['lanlamp'].data.energy, S['lanlamp'].data.color = 260, (1.0, 0.62, 0.32)
    shoot(S, (0, 0, 0), (h[0] + 1.3, h[1] + 4.6, h[2] + 0.9), (h[0] + 2.0, h[1] - 0.6, h[2] - 0.5), 30)


NEW = (garden_wide, garden_close, field_dusk, crew_seven, takeoff, stream, turret_calm, rack_calm, gunner_face, cigarette, whistle, hospital,
       witnesses, camp_famous, camp_wire, long_march, home_may, works, tv_studio, plaque, dawn_wood)
SHOTS3D.update({f.__name__: f for f in NEW})
STILLS.update(thumb=photo_thumb)

# The Short's shots were timed for about a second each; here they run two to three times as long. Their acting is spread over
# the first 1.4 s of a shot (lt is slowed, never sped up) and every shot also swings a little round its own subject, so a held
# frame keeps moving. prm "orb": [degrees, dolly, rise] sets the swing for one shot.
SHORT_KINDS = set(SHOTS3D) - {f.__name__ for f in NEW}
SWING = dict(stream=3.0, takeoff=2.0, camp_wire=2.0, gunner_face=4.0, cigarette=4.0)


def _slowed(f):
    def g(S, k, t, lt):
        f(S, k, t, min(lt, 1.4 * k))
    g.__name__ = f.__name__
    return g


def _swung(f, name):
    sign = 1 if sum(map(ord, name)) % 2 else -1
    rate = SWING.get(name, 7.0)

    def g(S, k, t, lt):
        f(S, k, t, lt)
        d = lt / k if k > 0.02 else 3.0
        o = S['prm'].get('orb')
        deg, dolly, rise = (list(o) + [0, 0])[:3] if o else (sign * rate * d, min(0.25, 0.05 * d), 0.0)
        c, tg = S['camrig'].location, S['camtgt'].location
        a = math.radians(deg) * (k - 0.5)
        m = 1 - dolly * (k - 0.5)
        dx, dy = c[0] - tg[0], c[1] - tg[1]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, c[2] + rise * (k - 0.5))
    g.__name__ = f.__name__
    return g


for _n in SHORT_KINDS:
    SHOTS3D[_n] = _slowed(SHOTS3D[_n])
_bf = SHOTS3D['backflip']
SHOTS3D['backflip'] = lambda S, k, t, lt: _bf(S, k, t, 0.75 * k)    # the drop takes the whole shot, so he stays in the wider frame
SHOTS3D['backflip'].__name__ = 'backflip'
SHOTS3D = {name: _swung(f, name) for name, f in SHOTS3D.items()}
