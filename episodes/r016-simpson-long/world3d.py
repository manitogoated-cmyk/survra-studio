"""Case 016 in 3D - Joe Simpson, who in 1985 broke his leg high on Siula Grande in Peru, was lowered down the
mountain on a rope by his partner Simon Yates, went over a cliff in a storm and hung there until Yates, being
pulled off himself, cut the rope. Simpson fell into a crevasse, lowered himself deeper to find a way out, and
crawled and hopped back to camp over several days.

Built for this story only: an overhanging ice cliff under a snow slope at night in a storm (with a small ice
perch on its lip), the inside of a crevasse with a ledge, the chamber at its bottom with a snow ramp up to a
hole of daylight, a glacier by day under a fluted peak, and a moraine with a two-tent camp by a small lake.

Everything is a generic low-poly reconstruction, not a model of the real mountain, glacier, camp or people. No
emblem, flag, sign, brand or lettering is shown anywhere in the sets. Nothing graphic is shown: the broken leg is
a leg held stiff. Nobody's likeness is attempted."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
SETS = dict(wall=(0, 0, 0), crev=(4000, 0, 0), deep=(8000, 0, 0), glac=(12000, 0, 0), mor=(16000, 0, 0))
AWAY = (0, 0, -3000)
HOST = {'hang_wide', 'rook_lip', 'rope_end', 'ledge_land', 'pebble', 'rook_gulp', 'abseil', 'climb_out', 'crawl_glacier', 'bottle_drop',
        'camp_night', 'bags_packed', 'storm_face', 'slide', 'two_men', 'rook_hatoff', 'rook_turn', 'signoff'}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN, HAIRJ, HAIRS = 'E0B090', '4A3222', 'B08A4A'
RED, GREEN, ROPE = 'C8372D', '2F9A68', 'FF7A1A'
ICE, ICED, ICEL, SNOW, SNOWL, ROCK, ROCKD = '3F6FAE', '21406E', '7FB0E0', 'B8C8E4', 'E6EEFA', '4C4A52', '2E2C36'
SLA = 0.59                                  # the snow slope above the cliff
SA, CA = math.sin(SLA), math.cos(SLA)
OB = 0.28                                   # how far the ice cliff overhangs
SEAT_S = 30.0                               # Yates's seat, measured up the slope from the lip
HANG = (0.0, -0.9, -13.0)                   # Simpson's feet when he hangs under the lip
PERCH = (2.5, 0.7, 0.7)                     # Rook's ice perch on the lip
RA = 0.545                                  # the snow ramp at the bottom of the crevasse
T1, T2 = (1.8, 2.6), (-4.6, 4.6)            # the two tents
HOP = (60.0, -30.0)
_KEEP = []


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def loc(name, x, y, z):
    o = SETS[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def stage(name, fn):
    """Build one set at its own origin and in its own collection, so that only one set renders per shot."""
    before = set(bpy.data.objects)
    out = fn(empty(SETS[name]))
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for o in set(bpy.data.objects) - before:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        coll.objects.link(o)
    return coll, out


def newmat(name, col, rough=0.6, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = rough
    paint(m, col, emit)
    return m


def paint(m, col, emit=0.0):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)
    b.inputs['Emission Color'].default_value = K.hexc(col)
    b.inputs['Emission Strength'].default_value = emit


def wear(o, m):
    o.data.materials[0] = m
    return o


def keep(o):
    """Remember how a movable prop was built so reset() can put it back."""
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def rn(i, j=0):
    return (math.sin(i * 78.233 + j * 37.719) * 43758.5453) % 1


def seen(objs, on):
    for o in objs:
        o.hide_render = not on


def look_yaw(frm, to):
    """Yaw that turns a rig standing at frm towards to (rigs face -Y at yaw 0)."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def span(o, a, b, w):
    """Stretch a unit-long object (built along Z, radius 0.5) between two points."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def slope_pt(s, x=0.0, up=0.0):
    """A point on the snow slope, s units up from the lip of the cliff, `up` above the snow."""
    return (x, s * CA - up * SA, s * SA + up * CA)


def wall_pt(x, dn, out=0.0):
    """A point on the face of the ice cliff, dn below the lip, `out` in front of the ice."""
    return (x, dn * math.sin(OB) - out * math.cos(OB), -dn * math.cos(OB) - out * math.sin(OB))


def ramp_pt(y, x=0.0, up=0.0):
    return (x, y - up * math.sin(RA), (y - 4.0) * math.tan(RA) + up * math.cos(RA))


# ---------------------------------------------------------------- the cliff in the storm
def set_wall(r):
    out = {}
    add('cube', SNOW, slope_pt(55, 0, -1), rot=(SLA, 0, 0), scale=(170, 110, 2), size=1, parent=r)
    add('cube', ICE, (0, 40 * math.sin(OB) + math.cos(OB), -40 * math.cos(OB) + math.sin(OB)), rot=(OB, 0, 0), scale=(170, 2, 80), size=1, parent=r,
        rough=0.35)
    for j in range(46):                                               # flutes and bulges of ice down the face
        x = -50 + 100 * rn(j, 1)
        dn = 3 + 60 * rn(j, 2)
        if abs(x) < 2.2 and dn < 22:
            continue
        s = 0.8 + 1.6 * rn(j, 3)
        add('ico_sphere', ICEL if j % 3 == 0 else ICED, wall_pt(x, dn, 0.1), rot=(OB, 0, 0), scale=(s, 0.5, s * (2.5 + 3 * rn(j, 4))), radius=1,
            subdivisions=1, parent=r, rough=0.3)
    for j in range(40):                                               # icicles under the lip
        x = -40 + 80 * rn(j, 5)
        if abs(x) < 0.7:
            continue
        d = 0.8 + 2.2 * rn(j, 6)
        add('cone', ICEL, (x, 0.05, -d / 2 - 0.1), rot=(PI, 0, 0), radius1=0.16 + 0.2 * rn(j, 7), radius2=0, depth=d, vertices=5, parent=r, rough=0.2)
    for j in range(44):                                               # wind-packed snow along the lip
        x = -44 + 2 * j + rn(j, 8)
        if abs(x) < 1.0 or 1.0 < x < 4.1:
            continue
        s = 0.6 + 0.8 * rn(j, 9)
        add('ico_sphere', SNOWL, (x, 0.5, 0.15), scale=(s * 1.8, s, s * 0.55), radius=1, subdivisions=1, parent=r)
    add('cube', ICEL, (PERCH[0], 0.9, 0.3), scale=(2.6, 2.4, 0.8), size=1, parent=r, rough=0.3)                     # the perch
    add('ico_sphere', SNOWL, (PERCH[0] + 0.9, 1.7, 0.75), scale=(0.9, 0.8, 0.35), radius=1, subdivisions=1, parent=r)
    add('cylinder', 'B8BCC8', (PERCH[0] + 1.0, 1.25, 1.2), rot=(0.1, 0.25, 0), radius=0.05, depth=1.2, vertices=5, parent=r, rough=0.3)  # an old ice peg
    for j in range(60):                                               # rocks and drifts on the slope
        s_, x = 3 + 80 * rn(j, 10), -60 + 120 * rn(j, 11)
        if abs(x) < 3.5 and s_ < 40:
            continue
        sc = 0.5 + 1.6 * rn(j, 12)
        if j % 3:
            add('ico_sphere', SNOWL, slope_pt(s_, x, 0.0), rot=(SLA, 0, 0), scale=(sc * 2.2, sc * 1.5, sc * 0.4), radius=1, subdivisions=1, parent=r)
        else:
            add('ico_sphere', ROCKD, slope_pt(s_, x, 0.2), rot=(SLA, 0, rn(j, 13) * 3), scale=(sc * 1.3, sc, sc * 0.7), radius=1, subdivisions=1, parent=r)
    out['seat'] = []
    for j in range(9):                                                # the bucket seat dug into the snow
        a = PI * (0.1 + 0.8 * j / 8) + PI
        p = slope_pt(SEAT_S + 0.2 + 1.0 * math.sin(a), 1.25 * math.cos(a), 0.12)
        sc = 0.42 + 0.2 * rn(j, 14)
        out['seat'].append(keep(add('ico_sphere', SNOWL, p, rot=(SLA, 0, j), scale=(sc * 1.3, sc, sc * 0.75), radius=1, subdivisions=1, parent=r)))
    add('ico_sphere', '8FA2C4', slope_pt(SEAT_S + 0.25, 0, -0.1), rot=(SLA, 0, 0), scale=(1.1, 1.0, 0.3), radius=1, subdivisions=1, parent=r)
    add('cube', '8FA4C8', (0, -20, -52.5), scale=(600, 600, 1), size=1, parent=r)                                      # the glacier far below
    add('cube', '02030A', (0, -3, -51.9), scale=(220, 13, 0.3), size=1, parent=r)                                      # the crevasse at the foot
    for j in range(40):
        x = -100 + 5 * j + 2 * rn(j, 15)
        sd = -1 if j % 2 else 1
        s = 1.5 + 2 * rn(j, 16)
        add('ico_sphere', 'A8B8D8', (x, -3 + sd * (7 + rn(j, 17)), -51.8), scale=(s * 2, s, s * 0.4), radius=1, subdivisions=1, parent=r)
    for j in range(7):                                                # dim peaks across the valley
        add('cone', '1A2440', (-260 + 90 * j, -420 - 60 * rn(j, 18), -20 + 30 * rn(j, 19)), rot=(0, 0, j), radius1=90, radius2=0, depth=120 + 60 * rn(j, 20),
            vertices=5, parent=r)
    out['rim'] = light((PERCH[0] - 1.2, -1.8, 3.4), 0, 'FFB070', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- inside the crevasse
def set_crev(r):
    out = {}
    th = 0.056
    for sd in (-1, 1):
        add('cube', ICE, (sd * 14.06, 0, -9.4), rot=(0, -sd * th, 0), scale=(20, 170, 190), size=1, parent=r, rough=0.3)
        for j in range(26):                                           # bulges, and darker bands of old ice
            z = -55 + 95 * rn(j, 21 + sd)
            y = -40 + 80 * rn(j, 23 + sd)
            if sd < 0 and abs(y) < 5 and -2 < z < 7:
                continue
            x = sd * (3.5 - th * z)
            s = 0.8 + 1.5 * rn(j, 25 + sd)
            add('ico_sphere', ICEL if j % 3 == 0 else ICED, (x, y, z), scale=(0.45, s * (2 + 3 * rn(j, 27)), s), radius=1, subdivisions=1, parent=r,
                rough=0.25)
        for j in range(6):
            z = -50 + 16 * j
            add('cube', ICED, (sd * (3.52 - th * z), 0, z), rot=(0, -sd * th, 0), scale=(0.1, 170, 1.2 + rn(j, 29)), size=1, parent=r, rough=0.3)
    for sd in (-1, 1):
        add('cube', '0E1C36', (0, sd * 55, -10), scale=(60, 12, 200), size=1, parent=r)
    add('ico_sphere', ICEL, (-3.6, 0.5, 9.5), scale=(2.6, 8, 3.6), radius=1, subdivisions=1, parent=r, rough=0.25)   # the overhang above the ledge
    add('ico_sphere', ICED, (-3.9, -2, 15), scale=(2.2, 6, 3.0), radius=1, subdivisions=1, parent=r, rough=0.25)
    add('cube', ICEL, (-2.0, 0, -0.75), scale=(3.4, 7, 1.5), size=1, parent=r, rough=0.3)                            # the ledge
    add('cube', ICE, (-2.3, 0, -2.6), rot=(0, 0.35, 0), scale=(2.6, 6.2, 3.0), size=1, parent=r, rough=0.3)
    for j in range(8):
        add('ico_sphere', SNOWL, (-3.0 + 2.2 * rn(j, 31), -3.2 + 6.4 * rn(j, 32), 0.0), scale=(0.7, 0.9, 0.16), radius=1, subdivisions=1, parent=r)
    for j in range(22):                                               # the snow roof either side of the slot
        y = -42 + 4 * j
        for sd in (-1, 1):
            add('ico_sphere', SNOWL, (sd * (2.4 + 0.5 * rn(j, 33 + sd)), y, 41.5), scale=(1.6, 2.6, 1.3), radius=1, subdivisions=1, parent=r)
    out['slotm'] = newmat('crev_slot', '2A3A6A', 0.6, 1.5)
    wear(add('cube', '2A3A6A', (0, 0, 46), scale=(7, 110, 0.2), size=1, parent=r), out['slotm'])
    add('cube', '01020A', (0, 0, -90), scale=(60, 170, 1), size=1, parent=r)
    add('cylinder', 'B8BCC8', (-0.55, 0.3, 0.12), rot=(0, 0.5, 0), radius=0.05, depth=0.5, vertices=5, parent=r, rough=0.3)      # an ice screw at the edge
    return out


# ---------------------------------------------------------------- the bottom of the crevasse
def set_deep(r):
    out = {}
    add('cube', 'AFC0DE', (0, 0, -0.5), scale=(15, 90, 1), size=1, parent=r)
    for sd in (-1, 1):
        add('cube', ICED, (sd * 11.5, 10, 14), scale=(10, 100, 40), size=1, parent=r, rough=0.3)
        for j in range(14):
            add('ico_sphere', ICE if j % 2 else ICEL, (sd * 6.4, -10 + 50 * rn(j, 41 + sd), 1 + 18 * rn(j, 43 + sd)),
                scale=(0.5, 1.5 + 3 * rn(j, 45), 1 + 2 * rn(j, 46)), radius=1, subdivisions=1, parent=r, rough=0.25)
    add('cube', ICED, (0, -17, 14), scale=(15, 10, 40), size=1, parent=r, rough=0.3)                                    # the closed end
    add('cube', ICED, (0, 44, 14), scale=(15, 10, 60), size=1, parent=r, rough=0.3)                                     # the wall above the hole
    add('cube', '16284A', (0, 6.5, 24), scale=(15, 37, 4), size=1, parent=r)                                           # the roof
    add('cube', '16284A', (-5.2, 32, 24), scale=(4.6, 14, 4), size=1, parent=r)
    add('cube', '16284A', (5.2, 32, 24), scale=(4.6, 14, 4), size=1, parent=r)
    L = 34 / math.cos(RA)
    add('cube', 'DCE6F6', ramp_pt(4 + 17, 0, -1), rot=(RA, 0, 0), scale=(13, L, 2), size=1, parent=r)                   # the snow ramp
    for j in range(18):
        y = 5 + 26 * rn(j, 47)
        sc = 0.5 + 0.9 * rn(j, 48)
        add('ico_sphere', SNOWL, ramp_pt(y, -5 + 10 * rn(j, 49), 0.0), rot=(RA, 0, 0), scale=(sc * 1.6, sc, sc * 0.4), radius=1, subdivisions=1, parent=r)
    for j in range(10):                                               # fallen blocks of ice on the floor
        x, y = -5.5 + 11 * rn(j, 50), -11 + 13 * rn(j, 51)
        if abs(x) < 1.6 and -5 < y < 1:
            continue
        sc = 0.4 + 0.8 * rn(j, 52)
        add('cube', ICEL if j % 2 else ICE, (x, y, sc * 0.4), rot=(rn(j, 53), rn(j, 54), rn(j, 55) * 3), scale=(sc * 1.4, sc, sc), size=1, parent=r,
            rough=0.25)
    out['beam'] = add('cylinder', 'FFF2C8', (0, 0, 0), radius=0.5, depth=1, vertices=10, parent=r, emit=0.5, alpha=0.07)
    span(out['beam'], (0, 31, 21), (0, 9, 2.5), 2.6)
    keep(out['beam'])
    return out


# ---------------------------------------------------------------- the glacier by day
def peak(r, x, y, base, hgt, rad, seed):
    add('cone', 'EEF3FB', (x, y, base + hgt / 2), rot=(0, 0, seed), radius1=rad, radius2=0, depth=hgt, vertices=6, parent=r)
    add('cone', '6A6470', (x + rad * 0.12, y - rad * 0.05, base + hgt * 0.36), rot=(0, 0, seed + 0.7), radius1=rad * 0.86, radius2=0, depth=hgt * 0.72,
        vertices=5, parent=r)
    for j in range(7):                                                # flutings of ice on the face
        a = -2.4 + 0.42 * j + seed
        add('cone', 'D2DDF0', (x + rad * 0.42 * math.cos(a), y + rad * 0.42 * math.sin(a), base + hgt * 0.46), rot=(0, 0, a), radius1=rad * 0.16,
            radius2=0, depth=hgt * 0.8, vertices=4, parent=r)


def set_glac(r):
    out = {}
    add('cube', 'E2EAF8', (0, 0, -0.5), scale=(2400, 2400, 1), size=1, parent=r)
    for j in range(46):                                               # crevasses
        x, y = -120 + 240 * rn(j, 61), -110 + 200 * rn(j, 62)
        if abs(x) < 9 and -22 < y < 8:
            continue
        add('cube', '1E3A6A', (x, y, 0.02), rot=(0, 0, 0.5 + 0.5 * rn(j, 63)), scale=(18 + 50 * rn(j, 64), 0.8 + 2.4 * rn(j, 65), 0.04), size=1, parent=r)
    for j in range(60):                                               # sun cups and hummocks
        x, y = -90 + 180 * rn(j, 66), -80 + 160 * rn(j, 67)
        if math.hypot(x, y) < 2.6:
            continue
        s = 0.6 + 2.0 * rn(j, 68)
        add('ico_sphere', 'F4F8FF' if j % 2 else 'CFDBEE', (x, y, -0.1), scale=(s * 2, s * 1.4, s * 0.3), radius=1, subdivisions=1, parent=r)
    add('cylinder', '0A1830', (0, 0, 0.03), scale=(1.0, 0.8, 1), radius=1.5, depth=0.05, vertices=9, parent=r)         # the hole he came out of
    for j in range(9):
        a = 2 * PI * j / 9
        if -2.3 < a - 2 * PI < -0.9 or 3.9 < a < 5.4:
            continue
        add('ico_sphere', 'F4F8FF', (1.75 * math.cos(a), 1.4 * math.sin(a), 0.1), scale=(0.8, 0.6, 0.4), radius=1, subdivisions=1, parent=r)
    peak(r, 40, 760, -30, 560, 420, 0.3)
    peak(r, -520, 900, -30, 380, 330, 1.1)
    peak(r, 560, 980, -30, 420, 360, 2.0)
    add('cube', 'D4DFF2', (0, 360, 6), rot=(0.05, 0, 0), scale=(1400, 420, 12), size=1, parent=r)
    out['trail'] = keep(add('cube', 'B4C4E0', AWAY, scale=(0.7, 1, 0.03), size=1, parent=r))
    return out


# ---------------------------------------------------------------- the moraine and the camp
def dome(r, x, y, col, m=None):
    o = add('ico_sphere', col, (x, y, 0.0), scale=(2.7, 2.7, 1.9), radius=1, subdivisions=2, parent=r, rough=0.7)
    if m:
        wear(o, m)
    add('cone', '14161E', (x, y - 2.5, 0.75), rot=(0.42, 0, 0), scale=(1.0, 0.25, 1.0), radius1=0.95, radius2=0, depth=1.6, vertices=3, parent=r)
    for a in (0.6, 2.5, 3.8, 5.6):
        add('cylinder', 'E8E4D8', (x + 3.2 * math.cos(a), y + 3.2 * math.sin(a), 0.35), rot=(0, 0.9, a), radius=0.015, depth=1.5, vertices=4, parent=r)


def set_mor(r):
    out = {}
    add('cube', '77706A', (0, 0, -0.5), scale=(2400, 2400, 1), size=1, parent=r)
    for j in range(150):                                              # boulders and rubble
        x, y = -90 + 190 * rn(j, 71), -75 + 130 * rn(j, 72)
        if (abs(x + 1.5) < 8 and -16 < y < 9) or (abs(x - HOP[0]) < 2.2 and -52 < y < -24) or math.hypot(x - 11, y - 9) < 7:
            continue
        s = 0.3 + 1.7 * rn(j, 73) ** 2
        add('ico_sphere', ('5E5A56', '8A847C', '6E6258', 'A39A8C')[j % 4], (x, y, s * 0.25), rot=(rn(j, 74), rn(j, 75), rn(j, 76) * 3),
            scale=(s * 1.4, s, s * 0.8), radius=1, subdivisions=1, parent=r)
    add('ico_sphere', '8A847C', (HOP[0] + 4.2, -43.0, 0.9), rot=(0.2, 0.1, 0.6), scale=(1.9, 1.5, 1.7), radius=1, subdivisions=1, parent=r)   # the rock he rests on
    add('cylinder', '2E8A9A', (11, 9, 0.02), scale=(1.5, 1.0, 1), radius=5, depth=0.04, vertices=10, parent=r, rough=0.1)   # a small lake
    for j in range(12):                                               # the stream that feeds it
        add('cube', '3E9AAA', (16 + 5 * j, 11 + 3 * math.sin(j * 0.9), 0.02), rot=(0, 0, 0.5 * math.cos(j * 0.9)), scale=(6, 0.9, 0.04), size=1, parent=r,
            rough=0.1)
    out['tentm'] = newmat('tent_lit', 'E0702A', 0.7, 0.0)
    dome(r, T1[0], T1[1], 'E0702A', out['tentm'])
    dome(r, T2[0], T2[1], '5A7AB0')
    for j, (x, y, col) in enumerate(((-2.9, -0.8, '8A3A30'), (-2.0, -0.5, '2F5A8A'))):                               # two packed rucksacks
        add('cube', col, (x, y, 0.62), rot=(0.08, 0, 0.2 * j), scale=(0.8, 0.55, 1.25), size=1, parent=r)
        add('cube', '22262E', (x, y - 0.3, 0.75), rot=(0.08, 0, 0.2 * j), scale=(0.5, 0.1, 0.6), size=1, parent=r)
        add('cylinder', 'D8B030' if j else '7A9A5A', (x, y + 0.05, 1.36), rot=(0, PI / 2, 0.2 * j), radius=0.2, depth=0.9, vertices=8, parent=r)
    add('cylinder', '8A6A44', (-3.5, -0.3, 0.7), rot=(0.25, 0.1, 0), radius=0.03, depth=1.5, vertices=5, parent=r)      # two axes stood against them
    add('cube', 'B8BCC8', (-3.5, -0.48, 1.42), scale=(0.5, 0.05, 0.08), size=1, parent=r, rough=0.3)
    add('ico_sphere', '5E5A56', (-0.9, -1.0, 0.25), scale=(0.6, 0.5, 0.4), radius=1, subdivisions=1, parent=r)
    out['lanm'] = newmat('lantern', 'FFD08A', 0.4, 0.0)
    wear(add('cylinder', 'FFD08A', (-0.9, -1.0, 0.82), radius=0.16, depth=0.36, vertices=8, parent=r), out['lanm'])
    add('cone', '3A3F4C', (-0.9, -1.0, 1.08), radius1=0.2, radius2=0.03, depth=0.16, vertices=8, parent=r)
    for j in range(5):                                                # a ring of stones for the stove
        a = 2 * PI * j / 5
        add('ico_sphere', '4A4642', (0.9 + 0.45 * math.cos(a), -2.2 + 0.45 * math.sin(a), 0.1), radius=0.2, subdivisions=1, parent=r)
    add('cylinder', 'B8BCC8', (0.9, -2.2, 0.3), radius=0.22, depth=0.3, vertices=8, parent=r, rough=0.3)
    peak(r, -60, 980, 10, 520, 380, 0.9)
    peak(r, 420, 1100, 10, 360, 320, 2.2)
    add('cube', 'D8E2F2', (-40, 520, 20), rot=(0.08, 0, 0), scale=(520, 520, 30), size=1, parent=r)                    # the glacier tongue
    for sd in (-1, 1):                                                # moraine ridges either side of the valley
        add('ico_sphere', '5A5650', (sd * 330, 240, -20), scale=(200, 560, 110), radius=1, subdivisions=2, parent=r)
    out['glow'] = light((T1[0], T1[1] - 1.0, 1.4), 0, 'FFB060', kind='POINT', parent=r)
    out['lan'] = light((-0.9, -1.4, 1.2), 0, 'FFC27A', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- heads and gear
def climber(skin, hat, hair):
    """A climber's head: a wool hat, a head torch on a band, and storm goggles that shots switch on and off."""
    def fn(head):
        add('ico_sphere', skin, (0, 0, 0.02), scale=(0.9, 0.98, 1.08), radius=0.29, subdivisions=1, parent=head)
        add('ico_sphere', hair, (0, 0.07, 0.04), scale=(0.96, 0.95, 0.95), radius=0.3, subdivisions=1, parent=head)
        add('ico_sphere', hat, (0, 0.03, 0.15), scale=(1.0, 1.02, 0.78), radius=0.32, subdivisions=1, parent=head)
        add('torus', '22262E', (0, 0.02, 0.1), major_radius=0.3, minor_radius=0.035, major_segments=10, minor_segments=4, parent=head)
        add('cube', '3A3F4C', (0, -0.3, 0.14), scale=(0.13, 0.08, 0.1), size=1, parent=head)
        bead = add('ico_sphere', 'FFF4D0', (0, -0.36, 0.14), radius=0.06, subdivisions=1, parent=head, emit=14.0)
        eyes, brows = [], []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.258, 0.0), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '1A222E', (s * 0.105, -0.276, -0.005), scale=(0.042, 0.02, 0.046), size=1, parent=head)
            brows.append(add('cube', hair, (s * 0.105, -0.266, 0.075), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.026), size=1, parent=head))
        add('cube', 'C08A6C', (0, -0.28, -0.07), scale=(0.05, 0.05, 0.08), size=1, parent=head)
        for x in (-0.09, 0.0, 0.09):                                  # some days of stubble
            add('cube', hair, (x, -0.255, -0.2), scale=(0.07, 0.02, 0.05), size=1, parent=head)
        jaw = empty((0, -0.2, -0.15), head)
        add('cube', '6A2A2E', (0, -0.066, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
        gog = [add('cube', '10141C', (0, -0.27, 0.0), scale=(0.46, 0.08, 0.15), size=1, parent=head, rough=0.15),
               add('cube', 'FFB000', (0, -0.312, 0.0), scale=(0.38, 0.02, 0.1), size=1, parent=head, rough=0.2, emit=0.7)]
        seen(gog, False)
        return dict(jaw=jaw, eyes=eyes, brows=brows, gog=gog, bead=bead)
    return fn


def harness(rig, col='22262E'):
    add('torus', col, (0, 0, 0.1), major_radius=0.34, minor_radius=0.05, major_segments=8, minor_segments=4, parent=rig.body)
    add('torus', 'D8DCE4', (0, -0.36, 0.1), rot=(PI / 2, 0, 0), major_radius=0.07, minor_radius=0.02, major_segments=6, minor_segments=4, parent=rig.body,
        rough=0.2)


def make_axe(parent=None):
    a = empty(AWAY if parent is None else (0, 0, 0), parent)
    add('cylinder', '8A6A44', (0, 0, 0), radius=0.03, depth=1.5, vertices=5, parent=a)
    add('cube', 'C8CCD8', (0, -0.12, 0.72), scale=(0.07, 0.62, 0.07), size=1, parent=a, rough=0.25)
    add('cone', 'C8CCD8', (0, 0, -0.82), rot=(PI, 0, 0), radius1=0.035, radius2=0, depth=0.16, vertices=4, parent=a, rough=0.25)
    return a


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = dict(colls={})
    for name, fn in (('wall', set_wall), ('crev', set_crev), ('deep', set_deep), ('glac', set_glac), ('mor', set_mor)):
        S['colls'][name], S[name] = stage(name, fn)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['joe'] = jo = K.Rig(dict(top=RED, pants='27334F', hand='20242C', boot='D8B030'), climber(SKIN, '2D5FA8', HAIRJ))
    harness(jo)
    S['simon'] = si = K.Rig(dict(top=GREEN, pants='3A3F4C', hand='20242C', boot='B8BCC8'), climber('D9A888', 'D8B030', HAIRS))
    harness(si)
    add('cube', '5A3A7A', (0, 0.3, 0.62), scale=(0.56, 0.3, 0.8), size=1, parent=si.body)                              # his pack
    S['humans'] = ['joe', 'simon']
    S['cast'] = [S['rook'], jo, si]
    # things Simpson carries on his right forearm, switched on per shot
    S['jaxe'] = make_axe(jo.el[1])
    S['jaxe'].location, S['jaxe'].rotation_euler = (0, -0.06, -1.05), (0, 0, 0)
    S['jbottle'] = bt = empty((0, -0.02, -0.72), jo.el[1])
    bt.scale = (1.5, 1.5, 1.5)
    add('cylinder', 'C8CCD8', (0, 0, 0), radius=0.085, depth=0.42, vertices=8, parent=bt, rough=0.25)
    add('cylinder', '22262E', (0, 0, -0.25), radius=0.045, depth=0.1, vertices=6, parent=bt)
    S['carried'] = [o for e in (S['jaxe'], S['jbottle']) for o in e.children]
    seen(S['carried'], False)
    S['fea'] = [keep(add('cone', '2F2B4D', AWAY, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(3)]
    S['chunks'] = [keep(add('ico_sphere', 'F0F5FC', AWAY, radius=0.16, subdivisions=1)) for _ in range(9)]
    S['ropes'] = [keep(add('cylinder', ROPE, AWAY, radius=0.5, depth=1, vertices=5, rough=0.7, emit=0.5)) for _ in range(4)]
    S['fray'] = fr = keep(empty(AWAY))
    for j in range(4):
        add('cone', 'FFC890', (0.03 * math.cos(j * 1.6), 0.03 * math.sin(j * 1.6), -0.09), rot=(PI + 0.35 * math.cos(j * 1.6), 0.35 * math.sin(j * 1.6), 0),
            radius1=0.022, radius2=0, depth=0.2, vertices=4, parent=fr, emit=0.6)
    S['biner'] = bn = keep(empty(AWAY))                                                                                # the shiny thing: a karabiner
    add('torus', 'E0B040', (0, 0, 0), rot=(PI / 2, 0, 0), scale=(0.7, 1.0, 1.0), major_radius=0.2, minor_radius=0.035, major_segments=10, minor_segments=5,
        parent=bn, rough=0.15, emit=1.8)
    S['axe'] = make_axe()
    keep(S['axe'])
    S['mug'] = keep(add('cylinder', 'FF7A1A', AWAY, radius=0.1, depth=0.2, vertices=7, rough=0.4, emit=0.4))
    S['bag'] = keep(add('ico_sphere', '3E63B8', AWAY, scale=(0.62, 1.5, 0.42), radius=1, subdivisions=2, rough=0.8))
    S['glove'] = gl = K.Hand('20242C', RED, 1.0)
    keep(gl.root)
    S['knife'] = kn = K.Hand('20242C', GREEN, 1.0)
    add('cube', 'C8D0DC', (0.42, -0.13, -0.02), scale=(0.46, 0.12, 0.03), size=1, parent=kn.root, rough=0.15, emit=0.25)             # a small blade
    add('cube', 'A8472E', (0.06, -0.13, -0.02), scale=(0.3, 0.16, 0.1), size=1, parent=kn.root)
    keep(kn.root)
    S['lamps'] = [light(AWAY, 0, 'FFF0C8', kind='POINT') for _ in range(3)]
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
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


def only(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: loc(name, x, y, z)


def shoot(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='DCE4F4'):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    dx, dy, dz = look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    hh = math.hypot(dx, dy) + 1e-6
    S['fill'].location = (pos[0] - dy / hh * 0.3 * d, pos[1] + dx / hh * 0.3 * d, pos[2] + 0.3 * d)
    S['fill'].data.energy = S['fillk'] * fill * min(d, 14) ** 2
    S['fill'].data.size = max(2.0, 0.3 * d)
    S['fill'].data.color = K.hexc(fcol)[:3]


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(AWAY)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for who in S['humans']:
        x = S[who].extra
        seen(x['gog'], False)
        x['bead'].hide_render = True
    seen(S['carried'], False)
    S['wall']['rim'].data.energy = 0
    paint(S['crev']['slotm'], '2A3A6A', 1.5)
    S['deep']['beam'].hide_render = True
    M = S['mor']
    paint(M['tentm'], 'E0702A', 0.0)
    paint(M['lanm'], 'FFD08A', 0.0)
    M['glow'].data.energy = 0
    M['lan'].data.energy = 0
    for l in S['lamps']:
        l.location = AWAY
        l.data.energy = 0
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['face'] = dict(rook='calm', joe='calm', simon='calm')
    S['jaw'] = dict(joe=0.0, simon=0.0)
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
    S['hat_jump'] = 0.0
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.43) % 1 < 0.035
    ez = dict(calm=0.07, deadpan=0.05, shocked=0.13, sad=0.055, warm=0.06, shut=0.012).get(e, 0.07)
    tilt = dict(deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], sm(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + (0.12 if e == 'deadpan' else 0.0) + tip * 0.35, 1.35, off), lerp(0.07, 0.0, off), 0)
    r['hat'].location = (0.0, lerp(0.0, -0.5, off), lerp(0.27 + S['hat_jump'] + tip * 0.1, -0.92, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, who in enumerate(S['humans']):
        x = S[who].extra
        f = S['face'][who]
        k = dict(calm=1.0, wide=1.7, shut=0.07, tired=0.45, warm=0.85, squint=0.4, sad=0.6).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for br in x['brows']:
            br.location.z = 0.075 + (0.03 if f == 'wide' else -0.012 if f in ('sad', 'tired', 'squint') else 0.0)
        x['jaw'].rotation_euler = (S['jaw'][who], 0, 0)


# ---------------------------------------------------------------- helpers for the shots
def env(S, name, skyc='000000', sun=0.0, sunc='FFFFFF', sdir=(-0.4, -0.6, 0.7), fk=2.6, skyk=1.0):
    A = only(S, name)
    sky(S, skyc, skyk)
    S['suntgt'].location = A(0, 0, 0)
    S['sun'].location = A(sdir[0] * 400, sdir[1] * 400, sdir[2] * 400)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(sunc)[:3]
    S['fillk'] = fk
    return A


def storm(S):
    """The cliff at night in the storm."""
    return env(S, 'wall', '070B1C', sun=0.8, sunc='8FA8FF', sdir=(0.6, -0.5, 0.5), fk=1.7)


def dawn(S):
    """The same cliff the morning after, the storm gone."""
    return env(S, 'wall', 'E8A084', sun=2.6, sunc='FFC8A0', sdir=(0.5, -0.8, 0.3), fk=2.2, skyk=0.9)


def crevasse(S):
    return env(S, 'crev', '0C1430', sun=1.3, sunc='9DB8FF', sdir=(0.02, 0.05, 1.0), fk=1.9)


def glacier(S):
    return env(S, 'glac', '2F6FD0', sun=3.4, sunc='FFF6E4', sdir=(-0.5, -0.5, 0.7), fk=2.4)


def moraine(S, night=False):
    if night:
        A = env(S, 'mor', '101A40', sun=1.1, sunc='9DB8FF', sdir=(-0.4, -0.3, 0.8), fk=2.2)
        M = S['mor']
        paint(M['tentm'], 'FF9A40', 2.4)
        paint(M['lanm'], 'FFD08A', 7.0)
        M['glow'].data.energy = 900
        M['lan'].data.energy = 160
        return A
    return env(S, 'mor', '5E9AE0', sun=3.0, sunc='FFF2DC', sdir=(0.5, -0.6, 0.6), fk=2.6)


def world_of(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def rope(S, i, a, b, w=0.035):
    span(S['ropes'][i], a, b, w)


def lamp(S, i, rig, e=50.0):
    """Switch a head torch on: the bright bead on the hat band and a small light in front of the face."""
    rig.extra['bead'].hide_render = False
    S['lamps'][i].location = world_of(rig.head, (0, -1.2, 0.2))
    S['lamps'][i].data.energy = e


def feather(S, pos, lt, t0=0.0, n=2):
    for i in range(n):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def to_chest(**over):
    d = dict(aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.22, 0.0))
    d.update(over)
    return P('stand', **d)


STARTLE = dict(aL=(0.7, 1.15, 1.5, -0.7), aR=(0.7, 1.15, 1.5, -0.7), head=(-0.15, 0.0), lean=-0.12, lL=(-0.12, 0.0), lR=(-0.12, 0.0))
KNEE = P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.4, aL=(0.6, 0.1, 0.7), aR=(1.0, 0.0, 0.5), head=(0.3, 0.0))
HANGING = dict(aL=(2.95, 0.12, 0.25), aR=(2.9, 0.1, 0.35), lL=(0.35, 0.7), lR=(-0.12, 0.0), head=(-0.3, 0.0))


def stiff(rig, out=0.28):
    """The broken right leg: held straight and turned a little outward. Nothing more is shown."""
    rig.hp[1].rotation_euler[1] = out


def hang(S, A, t, sway=1.0, drop=0.0, face='wide', head=None):
    """Simpson on the end of the rope under the lip. Returns where his hands hold it."""
    j = S['joe']
    a = 0.1 * sway * math.sin(t * 2.3)
    x, y, z = HANG[0] + 0.5 * sway * math.sin(t * 2.3 - 0.5), HANG[1], HANG[2] - drop
    j.place(A(x, y, z), 0.3 * sway * math.sin(t * 1.1), 0.0, a)
    pose = dict(aL=(2.9, 0.4, 0.3, 0.3), aR=(2.85, 0.44, 0.4, 0.3), lL=(0.45 + 0.25 * math.sin(t * 3.1), 0.9 + 0.3 * math.sin(t * 2.7)), lR=(-0.1, 0.0),
                head=head or (-0.3, 0.0))
    j.apply(P('stand', **pose))
    stiff(j, 0.4)
    S['face']['joe'] = face
    return mid_hands(j)


def prone(rig, pos, heading=0.0, slope=0.0):
    """Face down, head towards the heading (0 = -Y)."""
    rig.place(pos, heading, PI / 2 - slope)


def crawl_pose(lt, sp=1.6, head=(-0.75, 0.0)):
    s = math.sin(lt * sp * 2 * PI)
    return P('stand', aL=(2.3 + 0.5 * s, 0.25, 0.5 - 0.4 * s), aR=(2.3 - 0.5 * s, 0.25, 0.5 + 0.4 * s), lL=(0.3 + 0.3 * s, 0.7 + 0.5 * s), lR=(-0.05, 0.0),
             head=head)


def seated(S, A, s=SEAT_S, strain=0.0, t=0.0, face='squint', gog=True, pay=None):
    """Yates in his bucket seat on the slope. Returns where the rope leaves his hands."""
    si = S['simon']
    sh = 0.03 * strain * math.sin(t * 31)
    si.place(A(*slope_pt(s, sh, 0.05)), 0.0, 0.3)
    aL, aR = (0.62, -0.12, 0.55, 0.3), (0.62, -0.12, 0.55, 0.3)
    if pay is not None:
        u = math.sin(pay * 7)
        aL, aR = (0.62 + 0.3 * u, -0.12, 0.55 - 0.3 * u, 0.3), (0.62 - 0.3 * u, -0.12, 0.55 + 0.3 * u, 0.3)
    si.apply(P('sit', lean=-0.3 - 0.22 * strain + sh, aL=aL, aR=aR, head=(0.35, 0.0), lL=(1.3, 0.5), lR=(1.3, 0.45)))
    seen(si.extra['gog'], gog)
    S['face']['simon'] = face
    return mid_hands(si)


LIP = (0.0, -0.02, 0.06)


# ---------------------------------------------------------------- the hook: the rope goes slack
def grip(S, k, t, lt):
    A = storm(S)
    hands = hang(S, A, t, 1.6, head=(-0.12 + 0.1 * math.sin(t * 3), 0.2 * math.sin(t * 2.1)))
    rope(S, 0, A(*LIP), hands)
    lamp(S, 0, S['joe'], 40)
    j = S['joe'].root.location
    shoot(S, (j[0] + lerp(1.5, 1.1, k), j[1] - lerp(4.9, 3.9, k), j[2] + lerp(2.9, 2.75, k)), (j[0], j[1] - 0.1, j[2] + 2.62), 46, roll=0.05 * math.sin(t * 2),
          fill=1.5)


def leg_hang(S, k, t, lt):
    A = storm(S)
    hands = hang(S, A, t, 1.0, head=(0.45, 0.25))
    rope(S, 0, A(*LIP), hands)
    lamp(S, 0, S['joe'], 30)
    shoot(S, A(lerp(4.4, 3.6, k), lerp(-5.2, -4.6, k), lerp(-13.4, -12.9, k)), A(0.1, -0.9, -11.4), 33, fill=1.4)


def hang_wide(S, k, t, lt):
    A = storm(S)
    hands = hang(S, A, t, 1.0)
    rope(S, 0, A(*LIP), hands)
    rope(S, 1, A(*slope_pt(SEAT_S - 0.5, 0, 0.3)), A(*LIP))
    lamp(S, 0, S['joe'], 60)
    S['rook'].place(A(*PERCH), look_yaw(PERCH, (0, -3)))
    S['rook'].apply(P('stand', lean=0.45, head=(0.35, 0.0), aL=(0.3, 0.3, 0.3), aR=(0.3, 0.3, 0.3)))
    S['face']['rook'] = 'deadpan'
    S['wall']['rim'].data.energy = 500
    shoot(S, A(lerp(-9.5, -8.5, k), lerp(-17.5, -16.0, k), lerp(-10.5, -9.0, k)), A(0.9, 0.0, -5.6), 27, fill=1.3)


def slack(S, k, t, lt):
    A = storm(S)
    t0 = 0.3
    u = max(0.0, lt - t0)
    if u <= 0:
        rope(S, 0, A(*LIP), A(0.1 * math.sin(t * 9), HANG[1] - 0.2, -9.9), 0.05)
        rope(S, 1, A(*slope_pt(SEAT_S - 0.5, 0, 0.3)), A(*LIP), 0.05)
    else:
        s_end = max(0.0, 9 - 34 * u)
        fall = 30 * u * u
        if s_end > 0:
            rope(S, 1, A(*slope_pt(s_end, 0.6 * math.sin(u * 30), 0.25 + 0.5 * abs(math.sin(u * 22)))), A(*LIP), 0.05)
            rope(S, 0, A(*LIP), A(0.4 * math.sin(u * 20), HANG[1] - 0.2, -9.9 - fall), 0.05)
        else:
            v = u - 9 / 34
            rope(S, 0, A(0.3 * math.sin(u * 25), -0.3, -40 * v * v), A(0.5 * math.sin(u * 17), HANG[1], -9.9 - fall), 0.05)
    shoot(S, A(lerp(-4.6, -4.0, k), lerp(-4.4, -3.8, k), lerp(1.6, 1.2, k)), A(0.0, 0.9, lerp(0.2, -0.5, k)), 27, roll=0.06, fill=1.8)


def drop_away(S, k, t, lt):
    A = storm(S)
    u = lt * 1.4
    d = 1.5 + 16 * u * u
    j = S['joe']
    j.place(A(0.3 * math.sin(lt * 5), HANG[1] - 0.5, HANG[2] + 6 - d), lt * 2.2, -0.9 + lt * 1.6, 0.3)
    j.apply(P('stand', aL=(2.2, 0.9, 0.3), aR=(1.6, 1.1, 0.4), lL=(0.6, 0.9), lR=(-0.2, 0.0), head=(-0.3, 0)))
    stiff(j, 0.4)
    S['face']['joe'] = 'wide'
    lamp(S, 0, j, 120)
    p = j.root.location
    rope(S, 0, (p[0] + 0.8 * math.sin(lt * 16), p[1] - 0.3, p[2] + 9), (p[0], p[1], p[2] + 1.6), 0.05)
    shoot(S, A(0.55, lerp(-0.9, -1.2, k), lerp(2.2, 1.6, k)), A(0.0, -1.4, -40), 24, roll=0.15 * k, fill=1.4)


# ---------------------------------------------------------------- Rook on the lip
def rope_in_hand(S, A, lift):
    rk = S['rook']
    h = world_of(rk.hands[1])
    tip = (h[0], h[1] - 0.05, h[2] - 0.75)
    rope(S, 2, (h[0], h[1], h[2] + 0.12), tip, 0.04)
    S['fray'].location = tip
    return tip


def rook_lip(S, k, t, lt):
    A = storm(S)
    cam = (lerp(0.2, 0.6, k), lerp(-4.6, -4.0, k), 2.3)
    S['rook'].place(A(*PERCH), look_yaw(PERCH, cam) + 0.25)
    up = sm(lt / 0.3)
    S['rook'].apply(blend(P('stand', lean=0.3, head=(0.3, 0.3)), P('stand', aR=(1.25, 0.25, 1.1, 0.2), aL=(0.75, 0.5, 0.1), head=(0.0, -0.25)), up))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.6
    rope_in_hand(S, A, up)
    rope(S, 1, A(*slope_pt(7, 0.4, 0.2)), A(0.1, -0.1, 0.05))        # the slack rope lying over the lip
    rope(S, 0, A(0.1, -0.1, 0.05), A(0.2, -0.3, -5.0))
    S['wall']['rim'].data.energy = 260
    shoot(S, A(*cam), A(PERCH[0] - 0.35, PERCH[1], PERCH[2] + 2.3), 33, fill=1.8, fcol='FFE0C8')


def rope_end(S, k, t, lt):
    A = storm(S)
    cam = (1.0, -2.6, 3.3)
    S['rook'].place(A(*PERCH), look_yaw(PERCH, cam) + 0.1)
    S['rook'].apply(P('stand', aR=(1.9, -0.25, 1.75, 0.6), aL=(0.2, 0.2, 0.3), head=(0.1, -0.35)))
    S['face']['rook'] = 'deadpan' if lt < 0.3 else 'calm'
    rope_in_hand(S, A, 1.0)
    S['wall']['rim'].data.energy = 220
    h, hd = world_of(S['rook'].hands[1]), world_of(S['rook'].head)
    look = ((h[0] + hd[0]) / 2, (h[1] + hd[1]) / 2, (h[2] + hd[2]) / 2 - 0.1)
    c = A(lerp(0.9, 1.15, k), lerp(-2.9, -2.5, k), 3.2)
    shoot(S, c, look, 44, fill=2.0, fcol='FFE0C8')


# ---------------------------------------------------------------- into the crevasse
JL = (-1.75, 0.2, 0.0)                                              # where he ends up on the ledge


def dust(S, pts, A):
    for o, p in zip(S['chunks'], pts):
        o.location = A(*p[:3])
        s = p[3] if len(p) > 3 else 1.0
        o.scale = (s, s, s)


def fall_in(S, k, t, lt):
    A = crevasse(S)
    j = S['joe']
    z = lerp(17, 4.5, k ** 1.2)
    j.place(A(-0.6 + 0.3 * math.sin(lt * 4), 0.6, z), 0.6 + lt * 1.5, -0.7 + lt * 2.4, 0.2)
    j.apply(P('stand', aL=(2.2, 0.9, 0.3), aR=(1.4, 1.1, 0.5), lL=(0.7, 1.0), lR=(-0.25, 0.0), head=(-0.2, 0)))
    stiff(j, 0.4)
    S['face']['joe'] = 'wide'
    lamp(S, 0, j, 200)
    paint(S['crev']['slotm'], '5A7AC8', 3.0)
    rope(S, 0, A(-0.6 + 0.7 * math.sin(lt * 15), 0.6, z + 9), A(-0.6, 0.6, z + 1.4), 0.05)
    dust(S, [(-0.6 + 2.6 * (rn(i, 3) - 0.5), 0.6 + 2 * (rn(i, 4) - 0.5), z + 1 + 7 * rn(i, 5) + 5 * lt, 0.7 + rn(i, 6)) for i in range(9)], A)
    shoot(S, A(lerp(2.2, 1.8, k), lerp(-5.0, -4.2, k), lerp(-2.4, -1.4, k)), A(-0.5, 0.6, z + 1.6), 30, roll=0.12 * (k - 0.5), fill=1.7)


def lie(S, A, face='shut', lean=0.0):
    j = S['joe']
    j.place(A(JL[0], -1.9, 0.36), 0.0, -PI / 2)
    j.apply(P('stand', aL=(0.3, 0.7, 0.4), aR=(0.5, 0.6, 0.9), lL=(0.5, 0.9), lR=(0.0, 0.0), head=(0.1 + lean, 0.3)))
    stiff(j)
    S['face']['joe'] = face
    return j


def ledge_land(S, k, t, lt):
    A = crevasse(S)
    hit = 0.26
    j = S['joe']
    if lt < hit:
        z = 9 * (1 - lt / hit) ** 1.0 + 0.4
        j.place(A(JL[0], -1.9, z), 0.0, -PI / 2 + 1.2 * (1 - lt / hit))
        j.apply(P('stand', aL=(2.0, 0.9, 0.3), aR=(1.4, 1.1, 0.5), lL=(0.7, 1.0), lR=(-0.2, 0.0)))
        stiff(j)
        S['face']['joe'] = 'wide'
    else:
        lie(S, A, 'shut' if lt < 0.8 else 'tired')
        u = lt - hit
        dust(S, [(JL[0] + (1.0 + 3.2 * u) * math.cos(i * 0.7), -0.4 + (1.0 + 3.2 * u) * math.sin(i * 0.7) * 1.3, 0.25 + 2.6 * u - 3.4 * u * u + 0.3 * rn(i, 7),
                     0.7 + 0.8 * u) for i in range(9)], A)
    lamp(S, 0, j, 70)
    rp = (-1.3, 2.5, 0.0)
    drop = sm((lt - 0.3) / 0.4)
    S['rook'].place(A(rp[0], rp[1], lerp(6.0, 0.0, drop)), look_yaw(rp, (JL[0] + 0.6, -3.0)))
    S['rook'].apply(blend(P('up', aL=(1.5, 1.3, 0.2), aR=(1.5, 1.3, 0.2), lL=(0.4, 0.7), lR=(0.4, 0.7)), P('stand', lean=0.4, head=(0.35, 0.0)), (lt - 0.7) / 0.25))
    S['face']['rook'] = 'shocked' if lt < 0.9 else 'calm'
    rooklight(S, A(1.6, 0.4, 3.2), 180)
    shoot(S, A(lerp(2.8, 2.5, k), lerp(-6.8, -6.2, k), lerp(1.7, 1.4, k)), A(-1.5, 0.0, lerp(1.7, 1.4, k)), 26, fill=1.6)


def look_up(S, k, t, lt):
    A = crevasse(S)
    paint(S['crev']['slotm'], '7A9AE8', 5.0)
    j = S['joe']
    j.place(A(-1.9, 0.6, 0.0), PI + 0.25)
    reach = sm((lt - 0.25) / 0.5)
    j.apply(P('sit', lR=(1.45, 0.0), lL=(1.3, 1.1), head=(-0.75, 0.0), lean=-0.2, aR=(lerp(0.7, 2.75, reach), 0.15, lerp(1.5, 0.15, reach)), aL=(0.3, 0.4, 0.5)))
    stiff(j, 0.2)
    lamp(S, 0, j, 90)
    shoot(S, A(lerp(-0.2, -0.5, k), lerp(-4.4, -3.8, k), lerp(0.4, 0.6, k)), A(-1.7 + 0.3 * math.sin(lt * 1.3), 1.0, lerp(5.6, 7.4, k)), 19, roll=lerp(-0.08, 0.06, k), fill=1.6)


def ice_try(S, k, t, lt):
    A = crevasse(S)
    j = S['joe']
    pos = (-2.45, 0.9, 0.0)
    swing = sm(lt / 0.35)
    slip = sm((lt - 0.75) / 0.35)
    j.place(A(pos[0], pos[1], 0.0), -PI / 2 + 0.15)
    up = P('stand', aR=(2.7, 0.1, 0.5), aL=(2.2, 0.2, 0.8), lL=(0.25, 0.4), lR=(-0.25, 0.0), head=(-0.45, 0.0), lift=0.12)
    down = P('stand', aR=(1.9, 0.3, 1.2), aL=(1.2, 0.3, 1.2), lL=(0.9, 1.5), lR=(0.9, 0.1), head=(0.25, 0.0), lift=-0.62, lean=0.25)
    j.apply(blend(blend(P('stand', aR=(1.2, 0.2, 1.6), lR=(-0.2, 0.0)), up, swing), down, slip))
    stiff(j)
    seen(S['jaxe'].children, True)
    S['face']['joe'] = 'squint' if slip < 0.5 else 'shut'
    lamp(S, 0, j, 60)
    if 0.35 < lt < 1.2:
        u = lt - 0.35
        dust(S, [(-3.3 + 0.9 * u * (1 + rn(i, 8)), 0.9 + (rn(i, 9) - 0.5) * 1.2, 3.6 - 4.5 * u * u + rn(i, 10) * 0.8, 0.5 + rn(i, 11)) for i in range(7)], A)
    shoot(S, A(lerp(2.6, 2.2, k), lerp(-4.2, -3.6, k), lerp(2.6, 2.1, k)), A(-2.3, 0.6, lerp(2.5, 1.9, slip)), 34, fill=1.6)


RK = (-0.95, -1.7, 0.0)                                             # Rook at the edge of the ledge


def sit_wall(S, A, face='tired', head=(0.25, -0.5)):
    j = S['joe']
    j.place(A(-2.75, 1.2, 0.0), PI / 2 + PI)
    j.apply(P('sit', lR=(1.45, 0.0), head=head))
    stiff(j, 0.2)
    S['face']['joe'] = face
    return j


def pebble(S, k, t, lt):
    A = crevasse(S)
    lamp(S, 0, sit_wall(S, A), 60)
    rk = S['rook']
    rk.place(A(*RK), look_yaw(RK, (4, -1.7)))
    let = sm((lt - 0.28) / 0.1)
    rk.apply(blend(P('stand', lean=0.35, aR=(1.3, 0.1, 0.3), head=(0.5, 0.0)), P('stand', lean=0.6, aR=(1.1, 0.5, 0.2), aL=(0.2, 0.6, 0.4), head=(0.75, 0.0)), let))
    S['face']['rook'] = 'calm'
    h = world_of(rk.hands[1])
    u = max(0.0, lt - 0.28)
    S['chunks'][0].location = (h[0], h[1], h[2] - 0.2 - 26 * u * u)
    S['chunks'][0].scale = (1.3, 1.3, 1.3)
    shoot(S, A(lerp(2.9, 2.6, k), lerp(-3.6, -3.1, k), lerp(-3.4, -2.8, k)), A(-0.6, -1.5, lerp(1.2, 0.6, k)), 27, fill=1.7)


def rook_gulp(S, k, t, lt):
    A = crevasse(S)
    rk = S['rook']
    cam = (2.4, -3.6, 2.5)
    rk.place(A(*RK), look_yaw(RK, cam) - 0.3)
    pop = sm((lt - 0.3) / 0.1)
    rk.apply(blend(P('hat', aR=(0.3, 1.5, 2.2, -1.2), head=(0.2, 0.45), lean=0.25), P('stand', **STARTLE), pop))
    S['face']['rook'] = 'shocked' if pop > 0.3 else 'calm'
    S['hat_jump'] = 0.14 * pop
    feather(S, A(RK[0] + 0.2, RK[1] - 0.3, 3.4), lt, 0.32)
    rooklight(S, A(1.6, -3.2, 3.4), 140)
    shoot(S, A(lerp(2.5, 2.2, k), lerp(-3.8, -3.3, k), 2.5), A(RK[0], RK[1], 2.8), 46, fill=2.2)


def abseil(S, k, t, lt):
    A = crevasse(S)
    j = S['joe']
    z = lerp(-4.2, -9.5, sm(k))
    j.place(A(-0.15, 0.3, z), -PI / 2 + 0.3 * math.sin(t * 1.3), 0.0, 0.12 * math.sin(t * 2))
    j.apply(P('stand', aL=(1.9, 0.0, 1.5, 0.4), aR=(1.2, 0.1, 1.3, 0.4), lL=(1.0, 0.9), lR=(0.35, 0.0), head=(0.5, 0.0)))
    stiff(j)
    S['face']['joe'] = 'squint'
    lamp(S, 0, j, 110)
    rope(S, 0, A(-0.55, 0.3, 0.2), A(-0.3, 0.3, z + 2.4), 0.045)
    rope(S, 1, A(-0.2, 0.25, z + 1.2), A(-0.1 + 0.2 * math.sin(t * 3), 0.3, z - 9), 0.045)
    rk = S['rook']
    rk.place(A(*RK), look_yaw(RK, (4, -1.7)))
    rk.apply(P('stand', lean=0.6, head=(0.7, 0.2), aL=(0.3, 0.5, 0.3), aR=(0.3, 0.5, 0.3)))
    S['face']['rook'] = 'sad'
    rooklight(S, A(1.8, -3.4, 2.6), 260)
    shoot(S, A(lerp(2.9, 2.6, k), lerp(-8.0, -7.0, k), lerp(-3.6, -6.4, sm(k))), A(-0.5, 0.0, lerp(-1.4, -3.9, sm(k))), 24, fill=1.6)


# ---------------------------------------------------------------- the bottom, and the way out
def floor_dark(S, k, t, lt):
    A = env(S, 'deep', '02030A', sun=0.0, fk=1.0)
    j = S['joe']
    z = lerp(4.0, 0.0, sm(lt / 0.4))
    j.place(A(0.0, -3.0, z), 0.5)
    j.apply(blend(P('stand', aL=(1.9, 0.0, 1.5, 0.4), aR=(1.2, 0.1, 1.3, 0.4), lL=(1.0, 0.9), lR=(0.35, 0.0)),
                  P('stand', lL=(0.2, 1.5), lR=(1.2, 0.0), lift=-0.8, lean=0.2, aL=(0.4, 0.4, 0.5), aR=(0.6, 0.3, 0.6), head=(-0.1, 0.6 * math.sin(lt * 4))), (lt - 0.35) / 0.2))
    stiff(j, 0.3)
    S['face']['joe'] = 'tired'
    lamp(S, 0, j, 260)
    rope(S, 0, A(0.0, -3.0, 21), A(0.0, -3.2, z + 1.5))
    shoot(S, A(lerp(3.6, 3.0, k), lerp(3.6, 2.8, k), 1.7), A(0.0, -3.0, 1.5), 28, fill=1.0)


def daylight(S):
    A = env(S, 'deep', 'BFE0FF', sun=5.0, sunc='FFF0D0', sdir=(0.0, 0.77, 0.64), fk=1.5, skyk=1.3)
    S['deep']['beam'].hide_render = False
    return A


def sunbeam(S, k, t, lt):
    A = daylight(S)
    j = S['joe']
    j.place(A(0.9, -1.2, 0.0), PI - 0.15)
    j.apply(P('stand', lL=(0.2, 1.5), lR=(1.2, 0.0), lift=-0.8, lean=0.1, aL=(0.4, 0.4, 0.5), aR=(lerp(0.6, 1.9, sm(lt / 0.5)), 0.3, 0.9, 0.5),
              head=(lerp(0.2, -0.45, sm(lt / 0.4)), 0.0)))
    stiff(j, 0.3)
    rope(S, 0, A(0.0, -3.0, 21), A(0.0, -3.0, 0.0))
    shoot(S, A(lerp(3.0, 2.6, k), lerp(-8.4, -7.2, k), lerp(2.2, 2.6, k)), A(0.0, 14, lerp(7.0, 8.6, k)), 25, fill=0.9, fcol='FFF0D0')


def climb_out(S, k, t, lt):
    A = daylight(S)
    j = S['joe']
    y = lerp(13.0, 14.4, k)
    prone(j, A(*ramp_pt(y, -0.3, 0.38)), PI, RA)
    j.apply(crawl_pose(lt, 1.5, head=(-0.6, 0.0)))
    stiff(j)
    S['face']['joe'] = 'squint'
    rk = S['rook']
    rp = ramp_pt(18.6, 3.0, 0.0)
    rk.place(A(*rp), look_yaw(rp, (0, 12)))
    w = math.sin(lt * 9)
    rk.apply(P('stand', aR=(2.6, 0.5 + 0.3 * w, 0.6), aL=(0.3, 0.3, 0.3), head=(0.3, 0.0), lean=0.2))
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(6.0, 5.6, k), lerp(6.4, 7.4, k), lerp(6.6, 7.2, k)), A(1.0, 15.6, 8.0), 29, fill=1.5, fcol='FFF0D0')


# ---------------------------------------------------------------- days on the glacier and the moraine
def exit_hole(S, k, t, lt):
    A = glacier(S)
    j = S['joe']
    up = sm(lt / 0.5)
    j.place(A(0.0, 0.35, lerp(-2.5, -1.25, up)), 0.1 * math.sin(lt * 3))
    j.apply(P('stand', aL=(1.5 + 0.2 * up, 0.5, 0.25), aR=(1.6, 0.4, 0.3), head=(-0.2 * up, 0.0), lean=0.35))
    S['face']['joe'] = 'squint'
    shoot(S, A(lerp(2.2, 1.7, k), lerp(-6.2, -5.4, k), lerp(0.6, 0.9, k)), A(0.0, 0.2, lerp(1.0, 1.3, k)), 30)


def crawl_glacier(S, k, t, lt):
    A = glacier(S)
    j = S['joe']
    y = lerp(-6.0, -7.3, k)
    prone(j, A(0.0, y, 0.38), 0.0)
    j.apply(crawl_pose(lt, 1.4, head=(-0.5, 0.0)))
    stiff(j)
    S['face']['joe'] = 'tired'
    tr = S['glac']['trail']
    tr.location, tr.scale = (0.0, (y + 2.6) / 2 - 0.4, 0.02), (0.75, abs(y + 2.6) + 2.4, 0.03)
    rk = S['rook']
    rp = (2.3, y + 1.4, 0.0)
    rk.place(A(*rp), 0.0)
    rk.apply(walk(lt, 0.8, 'stand'))
    rk.head.rotation_euler = (0.3, 0, -0.6)
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(-5.6, -5.0, k), lerp(-14.5, -14.0, k), lerp(2.6, 3.0, k)), A(0.8, y + 0.6, 1.2), 30)


def hop_moraine(S, k, t, lt):
    A = moraine(S)
    j = S['joe']
    fall = sm((lt - 1.25) / 0.3)
    y = HOP[1] - 1.9 * min(lt, 1.25)
    hop = abs(math.sin(lt * 7.5))
    j.place(A(HOP[0], y, 0.0), 0.0, lerp(0.0, 1.25, fall))
    j.apply(P('stand', lL=(0.25 * math.sin(lt * 7.5), 0.5 * (1 - hop)), lR=(0.55, 0.0), aR=(0.75, 0.15, 0.25), aL=(0.2 - 0.5 * hop, 0.6, 0.5),
              lift=0.22 * hop - 0.1 - 0.5 * fall, lean=0.3, head=(0.2, 0.0)))
    stiff(j, 0.15)
    seen(S['jaxe'].children, True)
    S['face']['joe'] = 'tired'
    shoot(S, A(HOP[0] + lerp(3.4, 2.8, k), y - lerp(7.5, 6.5, k), lerp(1.2, 1.5, k)), A(HOP[0], y - 0.5, 1.9), 30)


def bottle_drop(S, k, t, lt):
    A = moraine(S)
    j = S['joe']
    jp = (HOP[0] + 4.1, -44.7)
    j.place(A(jp[0], jp[1], 0.0), 0.15)
    shake = 0.22 * math.sin(lt * 15) * (1 - sm((lt - 0.7) / 0.3))
    drop = sm((lt - 0.95) / 0.3)                                    # he gives up and lets the arm fall
    j.apply(P('sit', lR=(1.45, 0.0), lL=(1.3, 1.2), aR=(lerp(2.75, 0.9, drop) + shake, 0.2, lerp(1.75, 0.6, drop), 0.3), aL=(0.4, 0.3, 0.4),
              head=(lerp(-0.75, 0.3, drop), 0.15 * math.sin(lt * 4)), lean=-0.12))
    stiff(j, 0.2)
    seen(S['jbottle'].children, True)
    S['face']['joe'] = 'tired' if drop < 0.5 else 'shut'
    S['jaw']['joe'] = 0.5 * (1 - drop)
    b = world_of(S['jbottle'], (0, 0, -0.32))
    u = (lt - 0.3) / 0.35
    S['chunks'][0].location = (b[0], b[1], b[2] - 0.6 * u * u) if 0 < u < 1 else AWAY
    S['chunks'][0].scale = (0.22, 0.22, 0.34)
    rk = S['rook']
    arrive = sm(lt / 0.55)
    rp = (jp[0] - lerp(5.2, 2.5, arrive), jp[1] + 1.0, 0.0)
    rk.place(A(*rp), look_yaw(rp, jp))
    S['hat_off'] = sm((lt - 0.6) / 0.4)
    rk.apply(blend(blend(walk(lt, 2.0), P('stand', lean=0.25, head=(0.1, 0.0)), (lt - 0.45) / 0.15), to_chest(), (lt - 0.6) / 0.4))
    S['face']['rook'] = 'sad'
    shoot(S, A(jp[0] - lerp(1.6, -1.4, k), jp[1] - lerp(8.8, 6.8, k), lerp(1.6, 2.3, k)), A(jp[0] - lerp(1.5, 1.0, k), jp[1], 2.0), 36)


# ---------------------------------------------------------------- the camp
def camp_night(S, k, t, lt):
    A = moraine(S, night=True)
    j = S['joe']
    jp = (-5.2, -12.6 + 0.5 * k)
    prone(j, A(jp[0], jp[1], 0.38), PI + 0.35)
    j.apply(P('stand', aL=(2.2, 0.3, 0.9), aR=(2.9, 0.5, 0.2 + 0.2 * math.sin(lt * 8)), lL=(0.3, 0.7), lR=(-0.05, 0.0), head=(-0.9, 0.0)))
    stiff(j)
    S['face']['joe'] = 'tired'
    S['jaw']['joe'] = 0.3 + 0.25 * math.sin(lt * 11)
    rk = S['rook']
    rp = (-2.9, -11.2, 0.0)
    rk.place(A(rp[0], rp[1], 0.25 * abs(math.sin(lt * 8))), look_yaw(rp, T1))
    f = math.sin(lt * 16)
    rk.apply(P('up', aL=(2.2, 0.9 + 0.5 * f, 0.2), aR=(2.2, 0.9 + 0.5 * f, 0.2), head=(-0.25, 0.0)))
    S['face']['rook'] = 'shocked'
    shoot(S, A(lerp(-9.6, -8.8, k), lerp(-21.5, -20.0, k), lerp(1.7, 2.1, k)), A(-1.6, -3.0, 1.9), 27, fill=1.5, fcol='C8D4FF')


def tent_open(S, k, t, lt):
    A = moraine(S, night=True)
    si = S['simon']
    out = sm(lt / 0.3)
    sp = (T1[0], lerp(T1[1] - 2.2, T1[1] - 4.0, out), 0.0)
    si.place(A(*sp), 0.35)
    si.apply(blend(P('stand', lean=0.55, lift=-0.4, lL=(0.6, 0.9), lR=(0.2, 0.6), aL=(0.4, 0.3, 0.6), aR=(0.9, 0.3, 0.6)), P('stand', **STARTLE), (lt - 0.28) / 0.15))
    S['face']['simon'] = 'wide'
    S['jaw']['simon'] = 0.45 * sm((lt - 0.3) / 0.1)
    lamp(S, 0, si, 120)
    shoot(S, A(lerp(-1.2, -0.7, k), lerp(-8.6, -7.8, k), lerp(0.9, 1.1, k)), A(T1[0] - 0.2, T1[1] - 3.2, 2.35), 31, fill=1.5, fcol='FFD8B0')


def bags_packed(S, k, t, lt):
    A = moraine(S, night=True)
    rk = S['rook']
    x = lerp(-6.6, -4.9, sm(lt / 0.45))
    rp = (x, -1.2, 0.0)
    rk.place(A(*rp), look_yaw(rp, (-2.5, -0.9)))
    tap = sm((lt - 0.45) / 0.12)
    rk.apply(blend(walk(lt, 1.8), P('stand', lean=0.35, aR=(1.25 + 0.15 * math.sin(lt * 20), 0.1, 0.25), head=(0.3, 0.0)), tap))
    S['face']['rook'] = 'calm' if tap < 0.5 else 'shocked'
    shoot(S, A(lerp(-2.6, -3.0, k), lerp(-8.2, -7.6, k), lerp(1.7, 1.5, k)), A(-3.7, -0.9, 1.6), 32, fill=1.5, fcol='FFD8B0')


# ---------------------------------------------------------------- how it came to that: the storm on the slope
def storm_face(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=0.4, t=t, gog=False, face='squint')
    si = S['simon']
    si.head.rotation_euler = (lerp(0.1, 0.5, sm(lt / 0.8)), 0, 0.25 * math.sin(lt * 2.2))
    lamp(S, 0, si, 40)
    rk = S['rook']
    rp = slope_pt(SEAT_S + 1.2, 0.95, 0.0)
    rk.place(A(*rp), -0.2)
    rk.apply(P('hat', lean=0.3, head=(0.3, 0.1)))
    S['face']['rook'] = 'sad'
    h = world_of(si.head)
    rooklight(S, (h[0] + 2.6, h[1] - 1.0, h[2] + 2.0), 180)
    rope(S, 1, hands, A(*LIP))
    shoot(S, (h[0] + lerp(1.3, 1.0, k), h[1] - lerp(4.9, 4.3, k), h[2] - 0.3), (h[0] + 0.3, h[1], h[2] + 0.5), 32, fill=2.0)


def seated_rope(S, A, s=SEAT_S):
    return A(*slope_pt(s - 0.75, 0, 1.0))


def lowering(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=0.15, t=t, pay=lt)
    js = lerp(21.0, 15.5, k)
    j = S['joe']
    j.place(A(*slope_pt(js, 0.2 * math.sin(lt * 3), 0.42)), 0.0, -(PI / 2 - SLA))
    j.apply(P('stand', aL=(0.4, 0.8, 0.5), aR=(0.5, 0.7, 0.9), lL=(0.5, 0.9), lR=(0.0, 0.0), head=(0.35, 0.0)))
    stiff(j, 0.4)
    lamp(S, 0, j, 60)
    lamp(S, 1, S['simon'], 40)
    rope(S, 0, hands, A(*slope_pt(js + 1.5, 0, 0.6)), 0.045)
    dust(S, [slope_pt(js - 0.5 - 2.5 * ((lt * 1.3 + rn(i, 1)) % 1), 1.4 * (rn(i, 2) - 0.5), 0.3 + 0.8 * rn(i, 3)) + (0.8,) for i in range(8)], A)
    shoot(S, A(*slope_pt(lerp(35.0, 34.4, k), 1.3, lerp(5.2, 4.8, k))), A(*slope_pt(23.5, 0.0, 0.0)), 25, fill=1.8)


def rope_line(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=0.6, t=t)
    hj = hang(S, A, t, 0.8)
    rope(S, 0, A(*LIP), hj, 0.06)
    rope(S, 1, hands, A(*LIP), 0.06)
    lamp(S, 0, S['joe'], 160)
    lamp(S, 1, S['simon'], 160)
    shoot(S, A(lerp(27, 24, k), lerp(-27, -25, k), lerp(-1.0, 1.0, k)), A(0.0, 7.5, 2.5), 23, fill=1.2)


def seat_hold(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=1.0, t=t, face='shut' if (lt * 1.7) % 1 < 0.4 else 'squint')
    rope(S, 1, hands, A(*LIP))
    lamp(S, 0, S['simon'], 40)
    shoot(S, A(*slope_pt(lerp(25.2, 26.0, k), lerp(2.6, 2.1, k), lerp(1.5, 1.7, k))), A(*slope_pt(SEAT_S - 0.3, 0.0, 1.85)), 32, fill=1.9)


def slipping(lt):
    """How far the seat has let him slide: two small jerks."""
    return 0.55 * sm((lt - 0.2) / 0.12) + 0.75 * sm((lt - 0.75) / 0.12)


def seat_crumble(S, k, t, lt):
    A = storm(S)
    ds = slipping(lt)
    hands = seated(S, A, s=SEAT_S - ds, strain=1.0, t=t, face='wide')
    rope(S, 1, hands, A(*LIP))
    for i, o in enumerate(S['wall']['seat']):
        t0 = 0.2 if i % 2 else 0.75
        u = max(0.0, lt - t0 - 0.03 * i)
        if u > 0:
            a = PI * (0.1 + 0.8 * i / 8) + PI
            o.location = slope_pt(SEAT_S + 0.2 + 1.0 * math.sin(a) - 9 * u * u - 2.2 * u, 1.25 * math.cos(a) * (1 + u), 0.12 + 1.6 * u - 2.6 * u * u + 0.5 * abs(math.sin(u * 14)))
            o.rotation_euler = (u * 9, u * 6, i)
    shoot(S, A(*slope_pt(lerp(26.6, 26.2, k), lerp(-6.6, -6.0, k), lerp(1.3, 1.6, k))), A(*slope_pt(SEAT_S - 0.8 - ds * 0.6, 0.0, 1.1)), 30, fill=1.9)


def slide(S, k, t, lt):
    A = storm(S)
    ds = 1.3 + 2.4 * sm(lt / 0.45) + 2.2 * sm((lt - 0.6) / 0.4)
    s = SEAT_S - ds
    hands = seated(S, A, s=s, strain=1.0, t=t, face='wide')
    rope(S, 1, hands, A(*LIP))
    lamp(S, 0, S['simon'], 60)
    rk = S['rook']
    rp = slope_pt(s + 1.55, 0.25, 0.0)
    rk.place(A(*rp), 0.0)
    rk.apply(P('stand', aL=(1.35, 0.1, 0.3), aR=(1.35, 0.1, 0.3), lean=-0.5, lL=(0.5, 0.2), lR=(0.35, 0.1), head=(0.25, 0.0)))
    S['face']['rook'] = 'shocked'
    S['hat_jump'] = 0.1
    rooklight(S, A(*slope_pt(s - 0.5, 3.0, 3.5)), 260)
    dust(S, [slope_pt(s - 1.6 - 1.6 * ((lt * 2.2 + rn(i, 1)) % 1), 1.3 * (rn(i, 2) - 0.5), 0.2 + 1.2 * ((lt * 2.2 + rn(i, 1)) % 1)) + (1.0,) for i in range(9)], A)
    shoot(S, A(*slope_pt(lerp(24.6, 23.2, k), lerp(5.4, 5.0, k), lerp(2.2, 2.0, k))), A(*slope_pt(lerp(29.0, 26.2, k), 0.0, 1.9)), 26, fill=1.9)


def knife(S, k, t, lt):
    A = storm(S)
    a, b = slope_pt(SEAT_S - 0.6, 0.0, 1.0), slope_pt(SEAT_S - 6.0, 0.0, 0.3)
    cut = 0.62
    m = tuple(a[i] + (b[i] - a[i]) * 0.42 for i in range(3))
    h = S['knife']
    saw = 0.08 * math.sin(lt * 26) if lt < cut else 0.0
    lift = 0.35 * sm((lt - cut) / 0.2)
    h.place(A(m[0], m[1] + 0.12 + saw, m[2] + 0.72 + lift), (0.0, PI / 2, -0.35))
    h.grip(0.95)
    if lt < cut:
        rope(S, 1, A(*a), A(*b), 0.05)
    else:
        u = lt - cut
        e = (m[0], m[1] + 0.5 * u, m[2] + 0.5 * u - 0.6 * u * u)
        rope(S, 1, A(*a), A(*e), 0.05)
        S['fray'].location = A(*e)
        S['fray'].rotation_euler = (-(PI / 2 - SLA), 0, 0)
        g = 26 * u
        rope(S, 2, A(*slope_pt(SEAT_S - 3.0 - g, 0.4 * math.sin(u * 30), 0.5 + 0.5 * abs(math.sin(u * 22)))), A(*slope_pt(SEAT_S - 7.0 - g, 0.0, 0.25)), 0.05)
    S['lamps'][0].location = A(m[0] + 1.6, m[1] + 0.6, m[2] + 1.2)
    S['lamps'][0].data.energy = 60
    shoot(S, A(m[0] + lerp(3.4, 3.0, k), m[1] - lerp(0.9, 0.6, k), m[2] + lerp(0.9, 0.8, k)), A(m[0], m[1] + 0.05, m[2] + 0.3), 42, fill=2.2)


# ---------------------------------------------------------------- afterwards
def two_men(S, k, t, lt):
    A = moraine(S)
    j = S['joe']
    jp = (-1.2, -3.2)
    j.place(A(jp[0], jp[1], 0.0), 0.2)
    j.apply(P('sit', lR=(1.45, 0.0), lL=(1.45, 0.25), aL=(0.5, 0.3, 0.5), aR=(0.7 + 0.3 * sm((lt - 0.4) / 0.4), 0.1, 1.2), head=(0.05, -0.55), lean=-0.35))
    stiff(j, 0.1)
    S['face']['joe'] = 'warm'
    bg = S['bag']
    bg.location, bg.rotation_euler, bg.scale = A(jp[0] + 0.28, jp[1] - 1.25, 0.34), (0, 0, 0.2), (0.55, 1.05, 0.3)
    si = S['simon']
    sp = (jp[0] + 2.0, jp[1] - 0.5)
    si.place(A(sp[0], sp[1], 0.0), look_yaw(sp, jp))
    si.apply(dict(KNEE, aR=(1.15, 0.1, 0.6), head=(0.15, 0.0)))
    S['face']['simon'] = 'warm'
    S['mug'].location = world_of(si.hands[1], (0, -0.05, -0.1))
    rk = S['rook']
    rp = (jp[0] - 1.9, jp[1] + 0.9, 0.0)
    rk.place(A(*rp), look_yaw(rp, (jp[0] + 0.5, jp[1] - 5)))
    nod = sm((lt - 0.5) / 0.3)
    rk.apply(blend(P('cross', head=(0.1, -0.3)), P('hat', head=(0.25, -0.3)), nod))
    S['hat_tip'] = nod
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(-2.2, -1.8, k), lerp(-12.0, -11.2, k), lerp(2.6, 2.3, k)), A(-0.7, -3.0, 1.7), 30)


def rook_hatoff(S, k, t, lt):
    A = moraine(S)
    rk = S['rook']
    rp = (-11.0, -8.0, 0.0)
    rk.place(A(*rp), 0.15)
    S['hat_off'] = sm(lt / 0.4)
    rk.apply(blend(P('stand', head=(0.0, 0.3)), to_chest(), lt / 0.4))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(-9.8, -10.2, k), lerp(-13.6, -12.8, k), lerp(1.7, 2.0, k)), A(-11.0, -8.0, 2.45), 38)


def rook_turn(S, k, t, lt):
    A = dawn(S)
    cam = (lerp(5.6, 5.0, k), lerp(-3.6, -3.0, k), 2.4)
    rk = S['rook']
    turn = sm((lt - 0.15) / 0.3)
    rk.place(A(*PERCH), lerp(look_yaw(PERCH, (0, -4)), look_yaw(PERCH, cam), turn))
    rk.apply(blend(P('stand', lean=0.4, head=(0.5, 0.0)), P('shrug', head=(0.05, 0.0)), turn))
    S['face']['rook'] = 'sad' if turn < 0.5 else 'warm'
    rope(S, 1, A(*slope_pt(7, 0.4, 0.2)), A(0.1, -0.1, 0.05))
    rope(S, 0, A(0.1, -0.1, 0.05), A(0.2, -0.3, -5.0))
    shoot(S, A(*cam), A(PERCH[0] - 0.2, PERCH[1], PERCH[2] + 2.35), 34, fill=1.2, fcol='FFE0D0')


def signoff(S, k, t, lt):
    A = dawn(S)
    rk = S['rook']
    rk.place(A(*PERCH), 0.55)
    grab = sm((lt - 0.12) / 0.25)
    away = sm((lt - 0.7) / 0.3)
    rk.apply(blend(blend(P('stand'), P('stand', aR=(1.5, 0.6, 0.5), head=(-0.1, 0.5)), grab), P('hat'), away))
    S['hat_tip'] = away
    S['face']['rook'] = 'warm' if away < 0.5 else 'deadpan'
    b = S['biner']
    top = A(PERCH[0] + 1.02, 1.1, 1.72)
    hand = A(PERCH[0] + 0.6, 0.35, 2.55)
    u = sm((lt - 0.3) / 0.3)
    b.location = tuple(top[i] + (hand[i] - top[i]) * u for i in range(3))
    b.rotation_euler = (0.4 * math.sin(lt * 12) * (1 - u), 0.2, lt * 3 * u + 0.4)
    if lt > 0.7:
        b.location = AWAY
    rope(S, 1, A(*slope_pt(7, 0.4, 0.2)), A(0.1, -0.1, 0.05))
    rope(S, 0, A(0.1, -0.1, 0.05), A(0.2, -0.3, -5.0))
    shoot(S, A(lerp(1.4, 1.9, k), lerp(-5.6, -4.6, k), 2.7), A(PERCH[0] + 0.2, 0.8, 2.75), 31, fcol='FFE0D0')


# ---------------------------------------------------------------- photographs for the case board
def photo_men(S, k, t, lt):
    two_men(S, 1.0, t, 1.2)
    A = only(S, 'mor')
    shoot(S, A(-1.6, -9.0, 2.0), A(-0.4, -3.2, 1.5), 36)


def photo_hang(S, k, t, lt):
    A = storm(S)
    hands = hang(S, A, 1.0, 0.6)
    rope(S, 0, A(*LIP), hands)
    lamp(S, 0, S['joe'], 60)
    shoot(S, A(4.5, -7.5, -9.0), A(0.0, -0.6, -8.0), 30, fill=2.0)


def mid_hands(rig):
    a, b = world_of(rig.hands[0]), world_of(rig.hands[1])
    return tuple((a[i] + b[i]) / 2 for i in range(3))


def rooklight(S, pos, e=200.0):
    """A small warm light on Rook where the scene would leave him black."""
    S['lamps'][2].location = pos
    S['lamps'][2].data.energy = e


SHOTS3D = {f.__name__: f for f in (
    grip, leg_hang, hang_wide, slack, drop_away, rook_lip, rope_end, fall_in, ledge_land, look_up, ice_try, pebble, rook_gulp, abseil, floor_dark,
    sunbeam, climb_out, exit_hole, crawl_glacier, hop_moraine, bottle_drop, camp_night, tent_open, bags_packed, storm_face, lowering, rope_line,
    seat_hold, seat_crumble, slide, knife, two_men, rook_hatoff, rook_turn, signoff)}
STILLS = dict(men=photo_men, hang=photo_hang)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it. New sets: the west face of a big snow mountain seen from the glacier at its
# foot (the start, and the climb), a summit and a knife-edge ridge with an ice step in it (the top, the way down,
# the fall that broke his leg), a snow hole (the last of the gas; Yates's night alone), a hospital room and a
# writing desk (afterwards), and a sunny rock crag (climbing again). New shots on the Short's sets as well: the
# slope at dusk (the knot, the seat, the lowering), the foot of the cliff at dawn, base camp by day and night.
# Still generic: no emblem, flag, sign, brand or lettering anywhere; none of the sets is a model of a real place;
# the extra people (the third man at base camp, a muleteer) are stand-ins and nobody's likeness is attempted.
SETS.update(west=(20000, 0, 0), peak=(24000, 0, 0), cave=(28000, 0, 0), ward=(32000, 0, 0), crag=(36000, 0, 0))
FA = 1.08                                   # how steep the west face is
FP = -120.0                                 # where the three of them stand to look up at it
TOP = (-150.0, 0.0, 14.2)                   # the summit
STEP = 30.0                                 # where the ridge drops over an ice step
DESK = 60.0                                 # the writing desk stands in the same building as the ward
BED = (4.4, 2.5, 1.15)


import bmesh  # noqa: E402

_kit_add = add


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """The kit's primitives made from mesh data instead of operators (operators slow down as the scene fills). The
    Short's set functions look this name up when they run, so every set in the film builds this way. Same bevel."""
    bm = bmesh.new()
    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=kw.get('size', 2.0))
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
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
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


def blob(col, loc, scale, parent, sub=1, **kw):
    return add('ico_sphere', col, loc, scale=scale, radius=1, subdivisions=sub, parent=parent, **kw)


def face_pt(u, x=0.0, up=0.0):
    """A point on the west face, u units up it from its foot, `up` out from the snow."""
    return (x, 40 + u * math.cos(FA) - up * math.sin(FA), u * math.sin(FA) + up * math.cos(FA))


# ---------------------------------------------------------------- the west face
def set_face(r):
    box('E2EAF8', (0, 0, -0.5), (1800, 1800, 1), r)
    box('DCE6F6', face_pt(180, 0, -3), (560, 400, 6), r, rot=(FA, 0, 0))
    for j in range(54):                                               # flutings of snow and ice down the face
        u, x = 14 + 330 * rn(j, 81), -250 + 500 * rn(j, 82)
        if abs(x) < 9 and 132 < u < 168:
            continue
        s = 1 + 2.4 * rn(j, 83)
        blob('F4F8FF' if j % 3 else 'B8C8E4', face_pt(u, x, 0.4), (2 + 2.5 * s, 14 + 26 * rn(j, 84), 1.2 + s), r).rotation_euler = (FA, 0, 0)
    for j in range(18):                                               # bands of rock
        u, x = 30 + 300 * rn(j, 85), -240 + 480 * rn(j, 86)
        if abs(x) < 14 and 125 < u < 175:
            continue
        box(ROCKD if j % 2 else '5A5562', face_pt(u, x, 0.6), (12 + 30 * rn(j, 87), 4 + 7 * rn(j, 88), 2.4), r, rot=(FA, 0.1, rn(j, 89) - 0.5))
    for j in range(9):                                                # ice cliffs
        u, x = 60 + 240 * rn(j, 90), -200 + 400 * rn(j, 91)
        if abs(x) < 14 and 120 < u < 180:
            continue
        box(ICEL if j % 2 else ICE, face_pt(u, x, 1.5), (16 + 20 * rn(j, 92), 5, 5), r, rot=(FA - 0.5, 0, 0), rough=0.3)
    sy, sz = 40 + 380 * math.cos(FA), 380 * math.sin(FA)
    add('cone', 'F4F8FF', (0, sy + 40, sz - 30), radius1=150, radius2=0, depth=150, vertices=6, parent=r)       # the summit
    for sd in (-1, 1):                                                # the ridges either side
        add('cone', 'C9D6EC', (sd * 360, sy - 20, 130), rot=(0, 0, sd), radius1=260, radius2=0, depth=300, vertices=5, parent=r)
        add('cone', '6A6470', (sd * 420, sy + 40, 90), rot=(0, 0, sd * 2), radius1=240, radius2=0, depth=240, vertices=5, parent=r)
        add('cone', 'E6EEFA', (sd * 760, sy + 300, 150), rot=(0, 0, sd * 3), radius1=320, radius2=0, depth=380, vertices=6, parent=r)
    box('1E3A6A', (0, 37, 0.05), (420, 3.2, 0.1), r)                  # the crack at the foot of the face
    for j in range(40):                                               # hummocks on the glacier
        x, y = -110 + 220 * rn(j, 93), -150 + 180 * rn(j, 94)
        if math.hypot(x, y - FP) < 6:
            continue
        s = 0.7 + 2.2 * rn(j, 95)
        blob('F4F8FF' if j % 2 else 'CFDBEE', (x, y, -0.1), (s * 2, s * 1.4, s * 0.32), r)
    for j in range(14):
        x, y = -120 + 240 * rn(j, 96), -50 + 70 * rn(j, 97)
        if abs(x) < 14:
            continue
        box('1E3A6A', (x, y, 0.02), (14 + 40 * rn(j, 98), 0.8 + 2 * rn(j, 99), 0.04), r, rot=(0, 0, 0.3 * rn(j, 100)))
    p = face_pt(150, 4.6, 0.7)
    box(ICEL, (p[0], p[1] - 0.2, p[2]), (2.6, 2.6, 1.4), r, rough=0.3)                                        # a block of ice Rook stands on
    return dict(block=(p[0], p[1] - 0.5, p[2] + 0.7))


# ---------------------------------------------------------------- the summit and the north ridge
def set_peak(r):
    d = 56.57
    for x0, x1, z in ((-190, STEP, 0.0), (STEP, 230, -9.0)):          # the crest, in two levels with a step between
        box('E6EEFA', ((x0 + x1) / 2, 0, z - 40.4), (x1 - x0, d, d), r, rot=(PI / 4, 0, 0))
        box('F4F8FF', ((x0 + x1) / 2, 0.2, z - 0.3), (x1 - x0, 3.0, 0.6), r)
        n = int((x1 - x0) / 3.2)
        for j in range(n):                                            # the cornice, hanging out over one side
            x = x0 + 3.2 * j + rn(j, 101)
            if abs(x - STEP) < 2.4 or abs(x - TOP[0]) < 5:
                continue
            s = 0.8 + 0.7 * rn(j, 102)
            blob('FFFFFF', (x, 1.7, z - 0.25), (2.2 * s, 1.5 * s, 0.6 * s), r)
        for j in range(n // 2):                                       # ribs of snow down both flanks
            x, sd = x0 + 6.4 * j + 3 * rn(j, 103), (-1 if j % 2 else 1)
            dn = 6 + 22 * rn(j, 104)
            blob('CFDBEE' if j % 3 else 'B8C8E4', (x, sd * (dn * 0.72 + 1.0), z - dn * 0.72), (1.2 + rn(j, 105), 2.0, 5 + 6 * rn(j, 106)), r).rotation_euler = (
                -sd * PI / 4, 0, 0)
    box(ICE, (STEP + 0.6, 0, -4.6), (1.6, 8.5, 9.6), r, rough=0.3)                                              # the ice step
    for j in range(12):
        blob(ICEL if j % 2 else ICED, (STEP + 1.45, -3.6 + 7.2 * rn(j, 107), -8.6 + 8 * rn(j, 108)), (0.3, 0.6 + rn(j, 109), 0.8 + 1.4 * rn(j, 110)), r, rough=0.25)
    for j in range(7):                                                # icicles under its top edge
        add('cone', ICEL, (STEP + 1.5, -3.6 + 1.2 * j, -0.7 - 0.3 * rn(j, 111)), rot=(PI, 0, 0), radius1=0.16, radius2=0, depth=1.0 + rn(j, 112), vertices=5,
            parent=r, rough=0.2)
    blob('F4F8FF', (STEP + 5.5, 0, -9.3), (4.5, 2.6, 0.7), r)                                                 # the drift he lands in
    add('cone', 'F4F8FF', (TOP[0], 0, TOP[2] - 26.3), radius1=36, radius2=0, depth=53, vertices=6, parent=r)   # the summit
    blob('FFFFFF', (TOP[0], 0, TOP[2] - 0.5), (3.6, 3.0, 0.8), r)
    box('2B4A82', (0, 0, -460), (5000, 5000, 1), r)
    for j in range(34):                                               # the range all round, far below
        a = 2 * PI * j / 34 + 0.3 * rn(j, 113)
        d2 = 420 + 520 * rn(j, 114)
        hgt = 240 + 260 * rn(j, 115)
        x, y = 20 + d2 * math.cos(a), d2 * math.sin(a)
        add('cone', ('E6EEFA', 'C9D6EC', 'AFC0DE')[j % 3], (x, y, -460 + hgt / 2), rot=(0, 0, j), radius1=110 + 90 * rn(j, 116), radius2=0, depth=hgt, vertices=5,
            parent=r)
        add('cone', '5A5E74', (x + 12, y - 8, -460 + hgt * 0.34), rot=(0, 0, j + 1), radius1=100 + 80 * rn(j, 116), radius2=0, depth=hgt * 0.68, vertices=5, parent=r)
    for j in range(46):                                               # a sea of cloud in the valleys
        a = 2 * PI * rn(j, 117)
        d2 = 150 + 800 * rn(j, 118)
        s = 50 + 90 * rn(j, 119)
        blob('F4F6FC', (d2 * math.cos(a), d2 * math.sin(a), -300 - 40 * rn(j, 120)), (s * 1.6, s, s * 0.16), r, sub=2)
    return {}


# ---------------------------------------------------------------- a hole dug in the snow
def set_cave(r):
    out = {}
    box('C9D6EC', (0, 0, -0.25), (30, 30, 0.5), r)
    for j in range(18):                                               # the walls
        a = 2 * PI * j / 18
        if -2.35 < a - 2 * PI < -0.8 or 3.93 < a < 5.48:
            continue
        s = 2.4 + 0.8 * rn(j, 121)
        blob('DCE6F6' if j % 2 else 'B8C8E4', (6.2 * math.cos(a), 1.2 + 5.2 * math.sin(a), 1.4), (s, s, s * 1.25), r, sub=2)
    for j in range(11):                                               # the roof
        x, y = -6 + 12 * rn(j, 122), -4 + 9 * rn(j, 123)
        blob('CFDBEE' if j % 2 else 'B8C8E4', (x, y, 6.6 + rn(j, 124)), (3.2, 3.2, 2.6), r, sub=2)
    box('0E1830', (0, 9.5, 5), (40, 1, 30), r)
    for sd in (-1, 1):
        box('0E1830', (sd * 10.5, 2, 5), (1, 30, 30), r)
        box('5A6C98', (sd * 2.0, 0.9, 0.06), (1.5, 3.6, 0.12), r, rot=(0, 0, sd * 0.25))                       # two sleeping mats
    add('cylinder', '3A6A9A', (0, -0.4, 0.16), radius=0.24, depth=0.32, vertices=8, parent=r, rough=0.4)       # the stove: a gas canister, a burner, a pan
    add('cylinder', '8A8E98', (0, -0.4, 0.4), radius=0.1, depth=0.16, vertices=6, parent=r, rough=0.3)
    for j in range(3):
        box('8A8E98', (0.2 * math.cos(j * 2.1), -0.4 + 0.2 * math.sin(j * 2.1), 0.56), (0.05, 0.05, 0.2), r, rough=0.3)
    add('cylinder', 'B8BCC8', (0, -0.4, 0.82), radius=0.34, depth=0.34, vertices=10, parent=r, rough=0.25)
    box('3A3F4C', (0.5, -0.4, 0.9), (0.4, 0.06, 0.05), r)
    out['flame'] = keep(add('cone', '6AB0FF', (0, -0.4, 0.57), radius1=0.16, radius2=0.0, depth=0.22, vertices=6, parent=r, emit=9.0))
    out['glow'] = light((0, -1.0, 0.9), 0, '9CC0FF', kind='POINT', parent=r)
    out['warm'] = light((2.5, -4.5, 3.2), 0, 'FFD8B0', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- a hospital room, and a writing desk
def set_ward(r):
    out = {}
    for x0 in (0.0, DESK):
        box('B8BCB0' if x0 == 0 else '6A5444', (x0, 0, -0.25), (26, 20, 0.5), r)
        box('D8DCD0' if x0 == 0 else '4A5868', (x0, 6.4, 6), (26, 0.4, 12), r)
        for sd in (-1, 1):
            box('C8CCC0' if x0 == 0 else '3E4A5A', (x0 + sd * 12.5, 0, 6), (0.4, 20, 12), r)
        box('7A8088' if x0 == 0 else '2E2620', (x0, 6.1, 0.4), (26, 0.3, 0.8), r)
    # the ward
    box('F4F0E2', (-4.4, 6.1, 5.4), (6.4, 0.3, 5.0), r)                                                       # a window
    out['pane'] = wear(box('BFE0FF', (-4.4, 6.0, 5.4), (5.6, 0.2, 4.2), r), newmat('ward_pane', 'BFE0FF', 0.4, 3.0))
    box('F4F0E2', (-4.4, 5.85, 5.4), (0.16, 0.2, 4.2), r)
    box('F4F0E2', (-4.4, 5.85, 5.4), (5.6, 0.2, 0.16), r)
    box('8FB0C8', (-4.4, 5.8, 3.9), (5.6, 0.1, 1.2), r, emit=1.2)                                             # hills outside
    box('F0EEE6', (3.5, 2.5, 1.25), (6.2, 3.6, 0.6), r)                                                       # the bed
    box('8A8E98', (3.5, 2.5, 0.8), (6.4, 3.7, 0.2), r, rough=0.4)
    for x in (0.7, 6.3):
        for y in (0.8, 4.2):
            add('cylinder', '8A8E98', (x, y, 0.4), radius=0.1, depth=0.8, vertices=6, parent=r, rough=0.4)
    for x, hgt in ((6.55, 3.4), (0.4, 2.2)):
        box('8A8E98', (x, 2.5, hgt / 2 + 0.6), (0.14, 3.7, 0.14), r, rough=0.4)
        for y in (0.7, 4.3):
            add('cylinder', '8A8E98', (x, y, hgt / 2 + 0.3), radius=0.07, depth=hgt, vertices=6, parent=r, rough=0.4)
    blob('FFFFFF', (5.5, 2.5, 1.75), (0.8, 1.3, 0.32), r, sub=2)                                                # pillows
    blob('F4F0E2', (6.0, 2.5, 2.3), (0.3, 1.2, 0.6), r, sub=2)
    box('8FB4D0', (2.3, 3.4, 1.72), (3.4, 2.0, 0.42), r)                                                      # the blanket
    box('A8C8E0', (4.3, 2.5, 1.9), (0.5, 3.5, 0.3), r)
    for y in (0.9, 4.1):                                              # a frame over the foot of the bed for the sling
        add('cylinder', 'B8BCC8', (3.0, y, 2.9), radius=0.06, depth=4.4, vertices=6, parent=r, rough=0.3)
    add('cylinder', 'B8BCC8', (3.0, 2.5, 5.05), rot=(PI / 2, 0, 0), radius=0.06, depth=3.3, vertices=6, parent=r, rough=0.3)
    box('E8E4D8', (8.2, 3.6, 0.9), (1.6, 1.6, 1.8), r)                                                        # a locker with a glass and a jug
    add('cylinder', 'BFE0FF', (8.0, 3.3, 2.0), radius=0.14, depth=0.36, vertices=8, parent=r, rough=0.1)
    add('cylinder', 'E8E4D8', (8.5, 3.8, 2.1), radius=0.24, depth=0.6, vertices=8, parent=r, rough=0.3)
    for j in (0, 1):                                                  # crutches against the wall
        add('cylinder', 'A8865A', (9.6 + 0.5 * j, 5.7, 2.2), rot=(0.12, 0, 0), radius=0.06, depth=4.4, vertices=5, parent=r)
        box('3A3F4C', (9.6 + 0.5 * j, 5.42, 4.4), (0.6, 0.16, 0.16), r)
    add('cylinder', 'B8BCC8', (-7.6, 4.6, 3.0), radius=0.06, depth=6.0, vertices=6, parent=r, rough=0.3)       # a drip stand, a chair
    box('B8BCC8', (-7.6, 4.6, 5.9), (0.9, 0.08, 0.08), r, rough=0.3)
    box('6A8A9A', (-8.8, 2.0, 1.0), (1.6, 1.6, 0.2), r)
    box('6A8A9A', (-8.8, 2.75, 1.9), (1.6, 0.16, 1.8), r)
    out['day'] = light((-4.4, 3.0, 5.6), 0, 'DCEBFF', 5.0, kind='AREA', parent=r)
    out['day'].rotation_euler = (-1.1, 0, 0)
    out['key'] = light((0.5, -6.5, 6.5), 0, 'FFE8D0', kind='POINT', parent=r)
    # the desk
    D = DESK
    box('7A5A3A', (D, 1.6, 1.22), (6.4, 2.6, 0.16), r)
    for x in (-2.9, 2.9):
        box('5A4028', (D + x, 1.6, 0.6), (0.2, 2.4, 1.2), r)
    box('2E323A', (D, 2.1, 1.52), (1.7, 1.2, 0.44), r, rough=0.4)                                             # a typewriter
    box('1E2026', (D, 2.6, 1.42), (1.5, 0.5, 0.2), r, rough=0.4)
    add('cylinder', '14161C', (D, 1.6, 1.8), rot=(0, PI / 2, 0), radius=0.13, depth=2.0, vertices=8, parent=r, rough=0.4)
    out['sheet'] = keep(box('F4F0E2', (D, 1.52, 2.05), (1.3, 0.03, 0.7), r, rot=(0.15, 0, 0)))
    for j in range(7):                                                # typed pages, and a mug
        box('F4F0E2' if j % 2 else 'E8E2D0', (D - 2.1, 1.5, 1.33 + 0.045 * j), (1.2, 1.6, 0.04), r, rot=(0, 0, 0.12 * rn(j, 131) - 0.06))
    add('cylinder', 'FF7A1A', (D + 1.7, 1.0, 1.46), radius=0.16, depth=0.32, vertices=8, parent=r, rough=0.4)
    add('cylinder', '3A3F4C', (D + 2.4, 2.4, 1.36), radius=0.3, depth=0.1, vertices=8, parent=r)               # a desk lamp
    add('cylinder', '3A3F4C', (D + 2.4, 2.4, 2.1), rot=(0.25, 0, 0), radius=0.04, depth=1.5, vertices=5, parent=r)
    add('cone', 'C8372D', (D + 2.4, 2.0, 2.85), rot=(0.5, 0, 0), radius1=0.42, radius2=0.14, depth=0.5, vertices=8, parent=r)
    out['bulb'] = wear(blob('FFE0A0', (D + 2.4, 1.95, 2.68), (0.16, 0.16, 0.16), r), newmat('desk_bulb', 'FFE0A0', 0.4, 9.0))
    box('3E2E22', (D - 6.5, 5.8, 4.0), (6.2, 0.9, 8.0), r)                                                    # shelves of books
    for row in range(5):
        box('2A2018', (D - 6.5, 5.3, 0.9 + 1.5 * row), (6.0, 0.9, 0.12), r)
        x = D - 9.3
        j = 0
        while x < D - 3.9:
            wd = 0.22 + 0.3 * rn(j, 132 + row)
            hg = 0.9 + 0.4 * rn(j, 137 + row)
            box(('8A3A30', '2F5A8A', 'D8B030', '3E6A4A', 'E8E2D0', '5A3A7A', 'A8472E')[(j + row * 3) % 7], (x + wd / 2, 5.3, 0.96 + 1.5 * row + hg / 2), (wd, 0.7, hg), r)
            x += wd + 0.03
            j += 1
    box('F4F0E2', (D + 5.4, 6.1, 5.6), (5.0, 0.3, 5.0), r)                                                    # a window on to a wet evening
    out['dusk'] = wear(box('5A7AB8', (D + 5.4, 6.0, 5.6), (4.4, 0.2, 4.4), r), newmat('desk_pane', '5A7AB8', 0.4, 1.6))
    box('F4F0E2', (D + 5.4, 5.85, 5.6), (0.14, 0.2, 4.4), r)
    box('F4F0E2', (D + 5.4, 5.85, 5.6), (4.4, 0.2, 0.14), r)
    box('5A4028', (D, 3.9, 1.0), (1.5, 1.3, 0.16), r)                                                         # his chair
    box('5A4028', (D, 4.55, 2.0), (1.5, 0.14, 2.0), r)
    box('7A2A2A', (D + 7.5, 2.0, 0.03), (6, 9, 0.06), r)                                                      # a rug
    out['lampl'] = light((D + 2.2, 1.2, 2.5), 0, 'FFC27A', kind='POINT', parent=r)
    out['room'] = light((D - 3.0, -5.5, 6.0), 0, 'C8D4FF', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- a rock crag in the sun
def set_crag(r):
    box('5E8A4A', (0, 0, -0.5), (1600, 1600, 1), r)
    box('9A8E7C', (0, 8.2, 24), (150, 10, 60), r, rot=(-0.06, 0, 0))
    for j in range(70):                                               # blocks, flakes and ledges
        x, z = -40 + 80 * rn(j, 141), 0.5 + 44 * rn(j, 142)
        if abs(x - 0.2) < 1.6 and 6 < z < 15:
            continue
        box(('8A7E6C', 'A89C88', '7A7064', 'B4A894')[j % 4], (x, 1.6 + 0.06 * z, z), (2.5 + 5 * rn(j, 143), 1.0 + 1.2 * rn(j, 144), 1.2 + 3.5 * rn(j, 145)), r,
            rot=(-0.06, 0, 0.2 * rn(j, 146) - 0.1))
    for j in range(12):                                               # cracks
        x = -30 + 60 * rn(j, 147)
        box('3E382E', (x, 1.75 + 0.06 * 25, 20 + 10 * rn(j, 148)), (0.25, 0.4, 14 + 16 * rn(j, 149)), r, rot=(-0.06, 0.1 * rn(j, 150) - 0.05, 0))
    box('A89C88', (3.6, 1.5, 11.3), (2.6, 2.4, 0.6), r)                                                       # a ledge for Rook
    for j in range(40):                                               # heather and boulders at the foot
        x, y = -50 + 100 * rn(j, 151), -30 + 30 * rn(j, 152)
        s = 0.5 + 1.2 * rn(j, 153)
        blob(('7A5A8A', '4E7A3E', '8A7E6C')[j % 3], (x, y, s * 0.2), (s * 1.5, s * 1.2, s * 0.6), r)
    for j in range(8):                                                # hills behind the top of the crag
        add('cone', '6E9A5A', (-300 + 90 * j, 400, 10), rot=(0, 0, j), radius1=120, radius2=0, depth=90 + 40 * rn(j, 154), vertices=6, parent=r)
    return {}


# ---------------------------------------------------------------- more people, a mule, more props
def plain(skin, hair, hat=None, brim=False):
    """A head with no head torch: bare-headed, in a wool hat, or in a brimmed hat."""
    def fn(head):
        add('ico_sphere', skin, (0, 0, 0.02), scale=(0.9, 0.98, 1.08), radius=0.29, subdivisions=1, parent=head)
        add('ico_sphere', hair, (0, 0.06, 0.07), scale=(0.97, 0.96, 0.98), radius=0.3, subdivisions=1, parent=head)
        if hat and brim:
            add('cylinder', hat, (0, 0, 0.2), radius=0.6, depth=0.05, vertices=10, parent=head)
            add('cone', hat, (0, 0, 0.36), radius1=0.31, radius2=0.24, depth=0.32, vertices=8, parent=head)
        elif hat:
            add('ico_sphere', hat, (0, 0.03, 0.15), scale=(1.0, 1.02, 0.78), radius=0.32, subdivisions=1, parent=head)
        eyes, brows = [], []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.258, 0.0), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '1A222E', (s * 0.105, -0.276, -0.005), scale=(0.042, 0.02, 0.046), size=1, parent=head)
            brows.append(add('cube', hair, (s * 0.105, -0.266, 0.075), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.026), size=1, parent=head))
        add('cube', 'C08A6C', (0, -0.28, -0.07), scale=(0.05, 0.05, 0.08), size=1, parent=head)
        jaw = empty((0, -0.2, -0.15), head)
        add('cube', '6A2A2E', (0, -0.066, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
        bead = add('ico_sphere', 'FFF4D0', (0, 0, 0.0), radius=0.01, subdivisions=1, parent=head)
        return dict(jaw=jaw, eyes=eyes, brows=brows, gog=[], bead=bead)
    return fn


def make_mule():
    m = keep(empty(AWAY))
    box('6E5A48', (0, 0, 1.75), (0.95, 2.5, 1.0), m)
    box('6E5A48', (0, -1.45, 2.3), (0.5, 0.9, 0.6), m, rot=(0.7, 0, 0))
    box('7A6654', (0, -2.05, 2.75), (0.46, 0.95, 0.5), m, rot=(0.25, 0, 0))
    box('B8A890', (0, -2.5, 2.62), (0.4, 0.3, 0.36), m, rot=(0.25, 0, 0))
    for s in (-1, 1):
        add('cone', '5A4838', (s * 0.17, -1.75, 3.2), rot=(-0.2, s * 0.25, 0), radius1=0.1, radius2=0, depth=0.5, vertices=4, parent=m)
        box('14161C', (s * 0.24, -2.2, 2.85), (0.03, 0.08, 0.08), m)
    add('cone', '3E3228', (0, 1.4, 1.5), rot=(-0.5, 0, 0), radius1=0.09, radius2=0.03, depth=1.0, vertices=4, parent=m)
    box('FF7A1A', (0, 0.1, 2.28), (1.0, 1.3, 0.08), m, rough=0.8)                                             # a plain saddle blanket
    legs = [add('cylinder', '5A4838', (sx * 0.3, sy, 0.65), radius=0.13, depth=1.3, vertices=6, parent=m) for sx in (-1, 1) for sy in (-0.95, 0.95)]
    return m, legs


_build0, _reset0, _finish0 = build, reset, finish
EXTRA = ('rich', 'arr', 'jward', 'jlater')


def build():
    S = _build0()
    for name, fn in (('west', set_face), ('peak', set_peak), ('cave', set_cave), ('ward', set_ward), ('crag', set_crag)):
        S['colls'][name], S[name] = stage(name, fn)
    S['rich'] = K.Rig(dict(top='C8A050', pants='4A5A3A', hand=SKIN, boot='5A4028'), plain(SKIN, '6A4A2A', hat='8A3A30'))
    S['arr'] = K.Rig(dict(top='A8472E', pants='3A3F4C', hand='B08060', boot='2E2620'), plain('B08060', '17131A', hat='D8C8A0', brim=True))
    add('cone', 'A8472E', (0, 0, 0.62), radius1=0.62, radius2=0.3, depth=0.9, vertices=8, parent=S['arr'].body)       # a poncho
    S['jward'] = jw = K.Rig(dict(top='D8E4EC', pants='D8E4EC', hand=SKIN, boot='E8E4D8'), plain(SKIN, HAIRJ))
    for part, z, dp in ((jw.hp[1], -0.25, 0.56), (jw.kn[1], -0.2, 0.62)):                                              # a plaster cast, hip to heel
        add('cylinder', 'F4F2EA', (0, 0, z), radius=0.135, depth=dp, vertices=8, parent=part)
    S['jlater'] = K.Rig(dict(top=RED, pants='27334F', hand=SKIN, boot='3A3F4C'), plain(SKIN, HAIRJ))
    harness(S['jlater'], '2F5A8A')
    S['humans'] += list(EXTRA)
    S['cast'] += [S[n] for n in EXTRA]
    S['saxe'] = make_axe(S['simon'].el[1])
    S['saxe'].location, S['saxe'].rotation_euler = (0, -0.06, -1.05), (0, 0, 0)
    S['carried'] += list(S['saxe'].children)
    seen(S['carried'], False)
    S['mule'], S['mlegs'] = make_mule()
    S['can'] = keep(add('cylinder', '3A6A9A', AWAY, radius=0.24, depth=0.32, vertices=8, rough=0.4))
    S['coin'] = keep(add('cylinder', 'FFC233', AWAY, radius=0.11, depth=0.025, vertices=10, rough=0.2, emit=1.5))
    S['blade'] = keep(add('cube', 'D8E0EC', AWAY, scale=(0.05, 0.36, 0.1), size=1, rough=0.15, emit=0.5))
    S['loop'] = keep(add('torus', 'F4F0E2', AWAY, major_radius=0.16, minor_radius=0.025, major_segments=8, minor_segments=4, emit=0.4))
    S['ropes2'] = [keep(add('cylinder', '4AA8E0', AWAY, radius=0.5, depth=1, vertices=5, rough=0.7, emit=0.4)) for _ in range(2)]
    S['knot'] = keep(empty(AWAY))
    add('torus', ROPE, (0.05, 0, 0), rot=(0, PI / 2, 0.4), major_radius=0.1, minor_radius=0.045, major_segments=8, minor_segments=5, parent=S['knot'], emit=0.5)
    add('torus', '4AA8E0', (-0.05, 0, 0), rot=(0.5, PI / 2, -0.4), major_radius=0.1, minor_radius=0.045, major_segments=8, minor_segments=5, parent=S['knot'],
        emit=0.4)
    S['hk'] = [K.Hand('20242C', GREEN, 1.0) for _ in range(2)]
    for hd in S['hk']:
        hd.root.location = AWAY
        keep(hd.root)
    for nm in ('glove', 'knife'):                                     # the Short parked these two at the lip of the cliff; park them out of sight
        rt = S[nm].root
        for n_, e in enumerate(_KEEP):
            if e[0] is rt:
                _KEEP[n_] = (rt, e[1], AWAY, e[3], e[4])
    S['pad'] = pd = keep(empty(AWAY))
    box('3A3F4C', (0, 0, 0), (0.42, 0.05, 0.56), pd)
    box('F4F0E2', (0, -0.03, -0.02), (0.36, 0.03, 0.48), pd)
    S['page'] = keep(box('F4F0E2', AWAY, (0.42, 0.02, 0.56), None))
    S['lant'] = ln = keep(empty(AWAY))                                                                                # a small lantern Rook carries
    add('cylinder', 'FFD08A', (0, 0, 0), radius=0.1, depth=0.24, vertices=8, parent=ln, emit=8.0)
    add('cone', '3A3F4C', (0, 0, 0.18), radius1=0.14, radius2=0.02, depth=0.12, vertices=8, parent=ln)
    return S


def reset(S):
    _reset0(S)
    for n in EXTRA:
        S['face'][n] = 'calm'
        S['jaw'][n] = 0.0
    C, Wd_ = S['cave'], S['ward']
    C['glow'].data.energy = 0
    C['warm'].data.energy = 0
    for nm in ('day', 'key', 'lampl', 'room'):
        Wd_[nm].data.energy = 0
    for i, lg in enumerate(S['mlegs']):
        lg.rotation_euler = (0, 0, 0)


def finish(S, t):
    _finish0(S, t)
    for who in S['humans']:                                           # brows that say more: worried, and hurt
        f = S['face'][who]
        for i, br in enumerate(S[who].extra['brows']):
            s = -1 if i == 0 else 1
            br.rotation_euler = (0, s * (0.12 + (0.3 if f in ('sad', 'tired', 'shut') else -0.2 if f == 'squint' else 0.0)), 0)


def setface(S, **kw):
    S['face'].update(kw)


def daysky(S, name, col='3F86E0', sun=3.4, sdir=(-0.5, -0.6, 0.6), sunc='FFF6E4', fk=2.4):
    return env(S, name, col, sun=sun, sunc=sunc, sdir=sdir, fk=fk)


def dusk(S):
    """The slope above the cliff late in the day, before the storm and the dark."""
    return env(S, 'wall', 'A8684A', sun=2.6, sunc='FFA070', sdir=(0.75, -0.55, 0.22), fk=2.3, skyk=0.8)


def head_of(rig):
    return world_of(rig.head)


CLIMB = dict(lL=(0.9, 1.1), lR=(0.3, 0.5), head=(-0.45, 0.0), lean=0.0)


def climb_pose(lt, sp=0.9, ph=0.0):
    s = math.sin((lt * sp + ph) * 2 * PI)
    return P('stand', aL=(2.55 + 0.35 * s, 0.25, 0.55 - 0.3 * s), aR=(2.55 - 0.35 * s, 0.25, 0.55 + 0.3 * s), lL=(0.7 + 0.35 * s, 1.0 + 0.3 * s),
             lR=(0.7 - 0.35 * s, 1.0 - 0.3 * s), head=(-0.5, 0.0))


def axes_on(S, joe=True, simon=True):
    if joe:
        seen(S['jaxe'].children, True)
    if simon:
        seen(S['saxe'].children, True)


# ---------------------------------------------------------------- the start: the mountain
def face_people(S, A, lt, up=1.0):
    j, si, rk = S['joe'], S['simon'], S['rook']
    j.place(A(-1.3, FP, 0.0), PI + 0.12)
    j.apply(P('stand', aR=(lerp(0.3, 2.3, sm((lt - 0.5) / 0.5)), 0.2, 0.15), aL=(0.3, 0.3, 0.4), head=(-0.55 * up, 0.0)))
    si.place(A(0.9, FP + 0.7, 0.0), PI - 0.1)
    si.apply(P('hips', head=(-0.6 * up, 0.0)))
    rk.place(A(3.3, FP - 0.3, 0.0), PI - 0.2)
    setface(S, joe='warm', simon='calm', rook='deadpan')
    return j, si, rk


def look_face(S, k, t, lt):
    A = daysky(S, 'west', sdir=(-0.8, -0.4, 0.45))
    j, si, rk = face_people(S, A, lt)
    rk.apply(P('hat', head=(-0.7, 0.0), lean=-0.12))
    shoot(S, A(lerp(4.4, 3.4, k), FP - lerp(10.0, 8.8, k), lerp(0.8, 1.1, k)), A(0.6, FP + 22, lerp(13.5, 15, k)), 26, fill=0.8)


def two_look(S, k, t, lt):
    A = daysky(S, 'west', sdir=(-0.5, 0.5, 0.6))
    j, si, rk = face_people(S, A, lt + 2.0)
    slide_ = sm((lt - 0.6) / 0.5)
    rk.apply(blend(P('stand', head=(-0.75, 0.0), lean=-0.15), P('stand', aL=(0.3, 0.95, 0.5), aR=(0.3, 0.95, 0.5), head=(-0.85, 0.0), lean=-0.3), slide_))
    S['hat_jump'] = 0.05 * slide_
    setface(S, rook='shocked' if slide_ > 0.5 else 'deadpan', joe='warm', simon='warm')
    shoot(S, A(lerp(0.2, 1.0, k), FP + lerp(6.4, 5.6, k), lerp(1.3, 1.5, k)), A(0.9, FP, 2.45), 30, fill=1.6)


def face_wide(S, k, t, lt):
    A = daysky(S, 'west')
    shoot(S, A(lerp(-110, -80, k), lerp(-360, -330, k), 6), A(0, 120, lerp(130, 175, k)), 32, fill=0.0)


def face_climb(S, k, t, lt):
    A = daysky(S, 'west', sdir=(-0.6, -0.6, 0.5))
    j, si, rk = S['joe'], S['simon'], S['rook']
    pit = PI / 2 - FA - 0.1
    uj = 151.0 + 0.5 * lt
    j.place(A(*face_pt(uj, -0.7, 0.42)), PI, pit)
    j.apply(climb_pose(lt, 0.9))
    si.place(A(*face_pt(uj - 7.5, 1.3, 0.42)), PI, pit)
    si.apply(climb_pose(lt, 0.9, 0.5))
    axes_on(S)
    setface(S, joe='squint', simon='squint')
    rope(S, 0, world_of(j.body, (0, -0.4, 0.1)), world_of(si.body, (0, -0.4, 0.3)), 0.05)
    b = S['west']['block']
    rk.place(A(*b), look_yaw(b, (b[0] - 6, b[1] - 3)))
    rk.apply(P('hat', lean=0.3, head=(0.45, 0.3)))
    S['face']['rook'] = 'deadpan'
    for i, o in enumerate(S['chunks'][:6]):                           # chips of ice from the axes
        u = (lt * 1.1 + rn(i, 2)) % 1
        p = face_pt(uj + 2.0 - 9 * u * u, -0.7 + (rn(i, 3) - 0.5) * 1.5, 0.5 + 1.5 * u)
        o.location, o.scale = A(*p), (0.6, 0.6, 0.6)
    c = face_pt(uj - 3, 0, 0)
    shoot(S, A(c[0] - lerp(7.5, 6.5, k), c[1] - lerp(6.5, 5.8, k), c[2] + lerp(3.0, 3.8, k)), A(c[0] + 1.4, c[1], c[2] + 1.2), 30, fill=1.2)


def hawking_wave(S, k, t, lt):
    A = moraine(S)
    rc, j, si = S['rich'], S['joe'], S['simon']
    rp = (-5.5, -5.6)
    y = 2.0 + 1.3 * lt
    turn = sm((lt - 1.0) / 0.4)
    j.place(A(-9.6, y + 1.2, 0.0), lerp(PI, 0.15, turn))
    j.apply(blend(walk(lt, 1.5), P('stand', aR=(2.7, 0.5 + 0.3 * math.sin(lt * 9), 0.3), head=(0.0, 0.0)), turn))
    si.place(A(-7.6, y, 0.0), lerp(PI, -0.15, sm((lt - 1.3) / 0.4)))
    si.apply(blend(walk(lt + 0.3, 1.5), P('stand', aL=(2.6, 0.5, 0.4), head=(0.0, 0.0)), sm((lt - 1.3) / 0.4)))
    axes_on(S)
    rc.place(A(rp[0], rp[1], 0.0), look_yaw(rp, (-8.6, y)))
    rc.apply(P('stand', aR=(2.7, 0.55 + 0.3 * math.sin(lt * 8), 0.35), aL=(0.2, 0.3, 0.3), head=(-0.1, 0.0)))
    setface(S, joe='warm', simon='warm', rich='warm')
    S['jaw']['joe'] = 0.3 * turn
    shoot(S, A(lerp(-2.4, -3.0, k), lerp(-11.5, -10.6, k), lerp(2.3, 2.6, k)), A(-7.4, 0.0, 2.2), 32)


def rook_coin(S, k, t, lt):
    A = moraine(S)
    rc, rk = S['rich'], S['rook']
    rc.place(A(2.6, -3.3, 0.0), 0.35)
    sip = sm((lt - 1.2) / 0.5)
    rc.apply(P('sit', lL=(1.5, 1.5), lR=(1.5, 1.35), aR=(lerp(0.9, 1.5, sip), 0.0, lerp(1.2, 2.2, sip)), aL=(0.6, 0.2, 1.0), head=(0.1, 0.5), lean=0.05))
    S['mug'].location = world_of(rc.hands[1], (0, -0.05, -0.1))
    S['face']['rich'] = 'warm'
    rp = (-0.6, -3.7)
    rk.place(A(rp[0], rp[1], 0.0), look_yaw(rp, (0.4, -10)) + 0.2)
    flip = (lt * 1.3) % 1
    rk.apply(P('stand', aR=(1.0 + 0.25 * max(0, 1 - flip * 5), 0.15, 1.3), aL=(0.4, 0.1, 1.6, 1.2), head=(0.05, -0.45)))
    h = world_of(rk.hands[1])
    S['coin'].location = (h[0], h[1] - 0.05, h[2] + 0.3 + 4.4 * flip * (1 - flip))
    S['coin'].rotation_euler = (flip * 25, 0.3, 0)
    S['hat_tip'] = 0.5
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(0.2, 0.9, k), lerp(-10.2, -9.4, k), lerp(1.9, 2.1, k)), A(0.9, -3.3, 1.95), 34)


# ---------------------------------------------------------------- the top, and the way down
def summit(S, k, t, lt):
    A = daysky(S, 'peak', '2E6FD8', sun=3.6, sdir=(0.3, -0.7, 0.5))
    j, si, rk = S['joe'], S['simon'], S['rook']
    pump = math.sin(lt * 7)
    j.place(A(TOP[0] - 1.0, -0.3, TOP[2]), 0.25)
    j.apply(P('up', aL=(2.8, 0.45 + 0.15 * pump, 0.2), aR=(2.8, 0.45 - 0.15 * pump, 0.2), head=(-0.2, 0.0)))
    si.place(A(TOP[0] + 1.0, 0.1, TOP[2]), -0.3)
    si.apply(P('up', aL=(1.6, 0.3, 0.4), aR=(2.9, 0.3, 0.1 + 0.2 * pump), head=(-0.1, 0.0)))
    axes_on(S)
    setface(S, joe='warm', simon='warm', rook='deadpan' if lt < 1.0 else 'warm')
    S['jaw']['joe'] = 0.35 + 0.2 * pump
    S['jaw']['simon'] = 0.3
    rp = (TOP[0] + 3.3, -1.1, TOP[2] - 0.75)
    rk.place(A(*rp), look_yaw(rp, (TOP[0], -9)))
    clap = math.sin(lt * 5.5)                                         # a slow clap
    rk.apply(P('stand', aL=(1.0, -0.15 - 0.2 * clap, 1.2, 0.5), aR=(1.0, -0.15 - 0.2 * clap, 1.2, 0.5), head=(0.05, 0.4)))
    shoot(S, A(TOP[0] + lerp(-3.5, 1.5, k), lerp(-9.0, -8.2, k), TOP[2] + lerp(0.6, 1.2, k)), A(TOP[0] + 0.9, 0.0, TOP[2] + 1.9), 30, fill=1.2)


def evening(S):
    return env(S, 'peak', 'D8845A', sun=2.6, sunc='FFB080', sdir=(-0.8, -0.45, 0.2), fk=2.2, skyk=0.85)


def ridge_down(S, k, t, lt):
    A = evening(S)
    j, si = S['joe'], S['simon']
    x = -46 + 1.6 * lt
    j.place(A(x + 3.6, 0.0, 0.0), PI / 2)
    j.apply(walk(lt, 1.3))
    si.place(A(x, 0.0, 0.0), PI / 2)
    si.apply(walk(lt + 0.4, 1.3))
    axes_on(S)
    setface(S, joe='tired', simon='tired')
    rope(S, 0, world_of(si.body, (0, -0.4, 0.2)), world_of(j.body, (0, 0.3, 0.2)), 0.04)
    shoot(S, A(x + lerp(7.0, 5.6, k), lerp(-7.6, -6.8, k), lerp(0.9, 1.3, k)), A(x + 1.8, 0.0, 1.8), 32, fill=1.3, fcol='FFD8C0')


def morning(S):
    return daysky(S, 'peak', '4A8AE0', sun=3.2, sdir=(0.7, -0.5, 0.45))


def step_cast(S, A, lt, zj, simk=0.0):
    """The ice step: Simpson on its face, Yates on the crest above holding the rope."""
    j, si = S['joe'], S['simon']
    j.place(A(STEP + 1.75, 0.3, zj), -PI / 2, 0.06)
    si.place(A(STEP - 1.3, 0.2, 0.0), PI / 2)
    si.apply(blend(P('sit', lL=(1.4, 0.5), lR=(1.4, 0.4), aL=(0.9, -0.1, 0.5), aR=(0.9, -0.1, 0.5), head=(0.35, 0.0), lean=-0.15), P('stand', **STARTLE), simk))
    axes_on(S, simon=False)
    return j, si


def ice_step(S, k, t, lt):
    A = morning(S)
    j, si = step_cast(S, A, lt, lerp(-3.3, -4.3, sm(k)))
    j.apply(climb_pose(lt, 0.7))
    setface(S, joe='squint', simon='calm')
    rope(S, 0, world_of(si.hands[1]), world_of(j.body, (0, -0.35, 0.3)), 0.04)
    for i, o in enumerate(S['chunks'][:5]):
        u = (lt * 1.2 + rn(i, 4)) % 1
        o.location, o.scale = A(STEP + 1.9 + 0.8 * u, 0.3 + (rn(i, 5) - 0.5), -1.6 - 7 * u * u), (0.5, 0.5, 0.5)
    shoot(S, A(STEP + lerp(8.0, 7.0, k), lerp(-8.0, -7.0, k), lerp(-2.6, -1.8, k)), A(STEP + 0.4, 0.0, -1.6), 31, fill=1.4)


def step_fall(S, k, t, lt):
    A = morning(S)
    t0, t1 = 0.3, 0.72
    f = max(0.0, min(1.0, (lt - t0) / (t1 - t0)))
    j, si = step_cast(S, A, lt, -4.3 - 4.4 * f * f, simk=sm((lt - t0) / 0.2))
    if lt < t1:
        j.place(A(STEP + 1.75 + 2.2 * f, 0.3, -4.3 - 4.4 * f * f), -PI / 2, -1.1 * f)
        j.apply(blend(climb_pose(lt, 0.7), P('stand', aL=(2.2, 0.9, 0.3), aR=(1.6, 1.1, 0.4), lL=(0.6, 0.9), lR=(0.3, 0.0), head=(-0.3, 0)), f * 3))
        S['face']['joe'] = 'wide'
    else:
        u = lt - t1
        j.place(A(STEP + 4.3, 0.2, -8.5), -PI / 2, -PI / 2 + 0.25)
        j.apply(P('stand', aL=(0.6, 0.8, 0.5), aR=(0.9, 0.5, 1.0), lL=(0.7, 1.1), lR=(0.15, 0.0), head=(0.2, 0.3)))
        stiff(j, 0.35)
        S['face']['joe'] = 'shut'
        S['jaw']['joe'] = 0.5
        dust(S, [(STEP + 4.6 + (0.8 + 3 * u) * math.cos(i * 0.7), 0.2 + (0.8 + 3 * u) * math.sin(i * 0.7) * 0.8, -8.6 + 2.6 * u - 3.4 * u * u + 0.3 * rn(i, 7),
                  0.7 + 0.8 * u) for i in range(9)], A)
    setface(S, simon='wide')
    S['jaw']['simon'] = 0.4 * sm((lt - t0) / 0.2)
    rope(S, 0, world_of(si.hands[1]), world_of(j.body, (0, -0.35, 0.3)), 0.04)
    shoot(S, A(STEP + lerp(10.5, 9.5, k), lerp(-9.5, -8.5, k), lerp(-4.6, -5.6, k)), A(STEP + 1.8, 0.0, lerp(-3.4, -5.8, sm(f))), 30, fill=1.4)


JS = (STEP + 5.2, -0.2, -8.75)                                      # where he sits under the step


def joe_hurt(S, A, lt, look=0.0):
    j = S['joe']
    j.place(A(*JS), 1.05)
    rock = 0.06 * math.sin(lt * 5)
    j.apply(P('sit', lR=(1.45, 0.0), lL=(1.35, 1.2), aR=(1.25, -0.1, 0.45), aL=(1.2, -0.45, 0.6), head=(lerp(0.5, -0.2, look), 0.0), lean=0.3 + rock))
    stiff(j, 0.15)
    return j


def leg_sit(S, k, t, lt):
    A = morning(S)
    up = sm((lt - 1.2) / 0.5)
    joe_hurt(S, A, lt, up)
    S['face']['joe'] = 'shut' if up < 0.5 else 'wide'
    S['jaw']['joe'] = 0.35 * (1 - up) + 0.1
    rk = S['rook']
    rp = (JS[0] + 3.3, JS[1] + 0.4, -9.0)
    land = sm(lt / 0.35)
    rk.place(A(rp[0], rp[1], lerp(-5.0, rp[2], land)), look_yaw(rp, JS))
    S['hat_off'] = sm((lt - 1.3) / 0.5)
    rk.apply(blend(blend(P('up', aL=(1.5, 1.3, 0.2), aR=(1.5, 1.3, 0.2)), P('stand', lean=0.4, head=(0.4, 0.0)), (lt - 0.3) / 0.3), to_chest(), (lt - 1.3) / 0.5))
    S['face']['rook'] = 'shocked' if lt < 1.0 else 'sad'
    shoot(S, A(JS[0] + lerp(1.4, 0.8, k), lerp(-7.0, -6.2, k), JS[2] + lerp(1.2, 1.5, k)), A(JS[0] + 0.7, 0.6, JS[2] + 1.5), 36, fill=1.5)


def yates_sees(S, k, t, lt):
    A = morning(S)
    joe_hurt(S, A, lt, 1.0)
    si = S['simon']
    sp = (STEP + 0.5, -0.6, 0.2)
    si.place(A(*sp), PI / 2 - 0.5)
    drop = sm((lt - 0.9) / 0.5)
    si.apply(blend(P('stand', lean=0.5, head=(0.6, 0.0), aL=(0.5, 0.5, 0.4), aR=(0.5, 0.5, 0.4), lL=(0.3, 0.5), lR=(-0.2, 0.3), lift=-0.1),
                   P('stand', lean=0.4, head=(0.75, 0.0), aL=(0.3, 0.2, 2.3, 0.5), aR=(0.3, 0.2, 2.3, 0.5), lL=(0.3, 0.5), lR=(-0.2, 0.3), lift=-0.1), drop))
    setface(S, simon='wide' if drop < 0.5 else 'sad')
    S['jaw']['simon'] = 0.3 * (1 - drop)
    seen(S['saxe'].children, True)
    shoot(S, A(STEP + lerp(8.6, 7.8, k), lerp(-6.0, -5.4, k), lerp(-4.6, -4.0, k)), A(STEP + 0.6, -0.5, 2.0), 54, fill=1.6)


def ridge_two(S, k, t, lt):
    A = morning(S)
    joe_hurt(S, A, lt, 1.0)
    si = S['simon']
    sp = (JS[0] - 1.9, JS[1] + 0.5, -9.0)
    si.place(A(*sp), look_yaw(sp, JS))
    si.apply(dict(KNEE, aR=(1.1, 0.0, 0.5), head=(0.3, 0.0)))
    setface(S, joe='tired', simon='sad')
    shoot(S, A(STEP + lerp(17, 15, k), lerp(-15, -13, k), lerp(-3, -4, k)), A(STEP + 3.5, 0.0, -8.5), 30, fill=0.9)


# ---------------------------------------------------------------- the snow hole
def cave(S, flame=1.0, t=0.0):
    A = env(S, 'cave', '060A18', sun=0.0, fk=2.0)
    C = S['cave']
    fl = flame * (1 + 0.25 * math.sin(t * 37) + 0.15 * math.sin(t * 23))
    C['flame'].scale = (max(0.001, fl), max(0.001, fl), max(0.001, fl * 1.3))
    C['glow'].data.energy = 260 * fl
    C['warm'].data.energy = 160
    return A


def cave_two(S, A, lt):
    j, si = S['joe'], S['simon']
    jp, sp = (-2.2, 0.5), (2.2, 0.5)
    j.place(A(jp[0], jp[1], 0.0), look_yaw(jp, (0, -0.8)))
    j.apply(P('sit', aL=(1.1, 0.0, 0.5), aR=(1.1, 0.0, 0.5), head=(0.4, 0.0), lean=0.3))
    si.place(A(sp[0], sp[1], 0.0), look_yaw(sp, (0, -0.8)))
    si.apply(P('sit', aL=(0.9, 0.1, 1.2), aR=(1.0, -0.1, 0.9), head=(0.45, 0.0), lean=0.3))
    setface(S, joe='tired', simon='tired')


def bivi_stove(S, k, t, lt):
    A = cave(S, 1.0, t)
    cave_two(S, A, lt)
    rk = S['rook']
    rk.place(A(0.0, 2.7, 0.0), 0.0)
    rk.apply(P('sit', aL=(0.9, 0.0, 0.9), aR=(0.9, 0.0, 0.9), head=(0.3, 0.2 * math.sin(lt * 1.5))))
    S['hat_tip'] = 0.4
    S['face']['rook'] = 'calm'
    shoot(S, A(lerp(1.3, 0.5, k), lerp(-7.4, -6.6, k), lerp(1.9, 1.6, k)), A(0.0, 0.8, 1.35), 28, fill=1.3, fcol='C8D8FF')


def stove_out(S, k, t, lt):
    die = 1 - sm((lt - 0.6) / 0.7)
    A = cave(S, die * (1.0 if lt < 0.5 else 0.5 + 0.5 * abs(math.sin(lt * 19))), t)
    cave_two(S, A, lt)
    S['simon'].head.rotation_euler[0] = 0.6
    setface(S, joe='tired' if die > 0.3 else 'sad', simon='tired')
    shoot(S, A(lerp(1.5, 1.1, k), lerp(-3.4, -2.8, k), lerp(1.0, 0.9, k)), A(0.0, -0.3, 0.7), 40, fill=0.9 + 0.5 * die, fcol='C8D8FF')


def rook_can(S, k, t, lt):
    A = cave(S, 0.0, t)
    cave_two(S, A, lt)
    setface(S, joe='sad', simon='sad')
    rk = S['rook']
    rp = (0.5, 1.5, 0.0)
    rk.place(A(*rp), 0.15)
    tip = sm((lt - 1.1) / 0.3)
    shake = 0.25 * math.sin(lt * 22) * (1 - tip) * sm(lt / 0.2)
    rk.apply(blend(P('stand', aR=(1.6 + shake, 0.55, 2.0, -0.6), aL=(0.3, 0.2, 0.3), head=(0.1, 0.4), lean=0.2),
                   P('stand', aR=(1.3, 0.2, 1.1), aL=(0.3, 0.2, 0.3), head=(0.4, -0.2), lean=0.25), tip))
    cn = S['can']
    cn.location = world_of(rk.hands[1], (0, -0.1, -0.25))
    cn.rotation_euler = (lerp(0.2, PI, tip), shake, 0)
    S['face']['rook'] = 'deadpan' if tip < 0.5 else 'sad'
    S['hat_tip'] = 0.5 * tip
    rooklight(S, A(-1.2, -2.6, 3.0), 200)
    shoot(S, A(lerp(-1.2, -0.8, k), lerp(-4.4, -3.8, k), lerp(2.3, 2.4, k)), A(0.6, 1.2, 2.2), 38, fill=1.6, fcol='E8E0FF')


def snowhole(S, k, t, lt):
    A = cave(S, 0.0, t)
    si, rk = S['simon'], S['rook']
    sp = (-1.7, 0.9)
    si.place(A(sp[0], sp[1], 0.0), 0.5)
    si.apply(P('sit', lL=(1.75, 1.9), lR=(1.75, 1.9), aL=(1.35, -0.25, 1.0), aR=(1.35, -0.25, 1.0), head=(lerp(0.75, 0.35, sm((lt - 1.4) / 0.5)), 0.0), lean=0.45))
    setface(S, simon='shut' if lt < 1.6 else 'sad', rook='sad')
    lamp(S, 0, si, 26)
    rp = (2.1, 1.0)
    rk.place(A(rp[0], rp[1], 0.0), look_yaw(rp, sp) - 0.15)
    S['hat_off'] = 1.0
    rk.apply(dict(P('sit'), aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.3, 0.0)))
    rope(S, 1, A(-0.4, -0.9, 0.06), A(0.7, -0.5, 0.06), 0.045)
    S['fray'].location, S['fray'].rotation_euler = A(0.7, -0.5, 0.06), (0, PI / 2, 0.3)
    shoot(S, A(lerp(1.4, 0.4, k), lerp(-5.4, -4.8, k), lerp(1.8, 1.5, k)), A(0.2, 0.9, 1.3), 30, fill=1.5, fcol='C8D8FF')


# ---------------------------------------------------------------- the plan: one rope, a seat in the snow
def knot(S, k, t, lt):
    A = dusk(S)
    m = slope_pt(SEAT_S - 2.0, 0.0, 2.2)
    pull = sm((lt - 0.7) / 0.5)
    gap = 0.34 + 0.1 * pull
    for i, sd in enumerate((-1, 1)):
        hd = S['hk'][i]
        hd.place(A(m[0] + sd * (gap + 0.35), m[1] + 0.02, m[2] + 0.02 * math.sin(lt * 9 + i)), (0.25, 0.0, -sd * PI / 2))
        hd.grip(0.92)
    kn = S['knot']
    kn.location = A(*m)
    s = lerp(1.9, 1.0, pull)
    kn.scale = (lerp(1.0, 1.5, pull), s, s)
    kn.rotation_euler = (lt * 0.6 * (1 - pull), 0, 0)
    rope(S, 0, A(m[0] - 3.2, m[1] - 0.6, m[2] - 1.5), A(m[0] - 0.06, m[1], m[2]), 0.05)
    span(S['ropes2'][0], A(m[0] + 0.06, m[1], m[2]), A(m[0] + 3.2, m[1] - 0.5, m[2] - 1.6), 0.05)
    S['lamps'][0].location, S['lamps'][0].data.energy = A(m[0] + 0.5, m[1] - 1.6, m[2] + 1.0), 30
    shoot(S, A(m[0] + lerp(0.5, 0.2, k), m[1] - lerp(3.3, 2.7, k), m[2] + lerp(0.9, 0.6, k)), A(m[0], m[1], m[2] - 0.05), 44, fill=1.6, fcol='FFE0C8')


def joe_on_slope(S, A, s, x=0.0, lt=0.0):
    j = S['joe']
    j.place(A(*slope_pt(s, x + 0.15 * math.sin(lt * 3), 0.42)), 0.0, -(PI / 2 - SLA))
    j.apply(P('stand', aL=(0.4, 0.8, 0.5), aR=(0.5, 0.7, 0.9), lL=(0.5, 0.9), lR=(0.0, 0.0), head=(0.35, 0.0)))
    stiff(j, 0.4)
    return j


def seat_dig(S, k, t, lt):
    A = dusk(S)
    si, rk = S['simon'], S['rook']
    si.place(A(*slope_pt(SEAT_S + 1.6, 0.0, 0.0)), 0.0, 0.2)
    chop = (lt * 1.6) % 1
    sw = 1 - abs(2 * min(1.0, chop * 1.6) - 1) if chop < 0.62 else 0.0
    si.apply(dict(KNEE, aR=(lerp(1.0, 2.6, sw), 0.1, lerp(0.5, 1.2, sw)), aL=(0.9, 0.2, 0.6), head=(0.45, 0.0), lean=0.45))
    seen(S['saxe'].children, True)
    setface(S, simon='squint', joe='tired', rook='calm')
    joe_on_slope(S, A, SEAT_S - 4.0, 2.6)
    S['joe'].head.rotation_euler[0] = -0.2
    if chop > 0.32:
        u = chop - 0.32
        dust(S, [slope_pt(SEAT_S + 0.4 - 3.5 * u * (0.5 + rn(i, 1)), 1.6 * (rn(i, 2) - 0.5) * (1 + 2 * u), 0.3 + 3.5 * u - 6 * u * u) + (0.8,) for i in range(7)], A)
    rp = slope_pt(SEAT_S + 2.4, -2.6, 0.0)
    rk.place(A(*rp), -0.2)
    rk.apply(P('cross', lean=0.2, head=(0.35, -0.3)))
    shoot(S, A(*slope_pt(lerp(SEAT_S - 7.0, SEAT_S - 6.2, k), lerp(-4.6, -3.8, k), lerp(2.0, 2.4, k))), A(*slope_pt(SEAT_S - 0.2, 0.4, 1.5)), 30, fill=1.5,
          fcol='FFE0C8')


def lower_side(S, k, t, lt):
    A = dusk(S)
    hands = seated(S, A, strain=0.2, t=t, pay=lt, gog=False)
    js = lerp(21.5, 15.0, k)
    joe_on_slope(S, A, js, 0.0, lt)
    rope(S, 0, hands, A(*slope_pt(js + 1.5, 0, 0.6)), 0.05)
    dust(S, [slope_pt(js - 0.5 - 2.5 * ((lt * 1.3 + rn(i, 1)) % 1), 1.4 * (rn(i, 2) - 0.5), 0.3 + 0.8 * rn(i, 3)) + (0.8,) for i in range(8)], A)
    shoot(S, A(*slope_pt(lerp(23.5, 22.5, k), lerp(11.5, 10.5, k), lerp(2.6, 3.2, k))), A(*slope_pt(25.5, 0.0, 1.2)), 30, fill=1.4, fcol='FFE0C8')


def lower_far(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=0.3, t=t, pay=lt)
    js = lerp(11.0, 4.5, k)
    joe_on_slope(S, A, js, 0.0, lt)
    lamp(S, 0, S['joe'], 220)
    lamp(S, 1, S['simon'], 220)
    rope(S, 0, hands, A(*slope_pt(js + 1.5, 0, 0.6)), 0.07)
    shoot(S, A(lerp(-15, -13, k), lerp(-13, -11.5, k), lerp(7.0, 5.0, k)), A(0.0, 9.0, 6.5), 30, fill=1.5)


def rook_watch(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=0.3, t=t, pay=lt)
    rope(S, 1, hands, A(*LIP))
    lamp(S, 0, S['simon'], 40)
    rk = S['rook']
    rp = slope_pt(SEAT_S - 0.6, 2.7, 0.0)
    rk.place(A(*rp), -0.35)
    brim = sm((lt - 0.8) / 0.4)
    rk.apply(blend(P('cross', lean=0.2, head=(0.3, 0.45)), P('hat', lean=0.25, head=(0.4, 0.1)), brim))
    S['hat_tip'] = brim
    S['face']['rook'] = 'calm' if brim < 0.5 else 'sad'
    h = head_of(rk)
    rooklight(S, (h[0] + 1.5, h[1] - 2.5, h[2] + 1.0), 160)
    shoot(S, (h[0] + lerp(1.5, 1.1, k), h[1] - lerp(4.6, 4.0, k), h[2] - 0.2), (h[0] - 0.7, h[1], h[2] - 0.15), 38, fill=1.9)


# ---------------------------------------------------------------- over the edge
def over_edge(S, k, t, lt):
    A = storm(S)
    t0 = 0.55
    rope(S, 1, A(*slope_pt(SEAT_S - 0.5, 0, 0.3)), A(*LIP), 0.05)
    if lt < t0:
        sj = lerp(4.2, 0.9, lt / t0)
        j = joe_on_slope(S, A, sj, 0.0, lt)
        rope(S, 1, A(*slope_pt(SEAT_S - 0.5, 0, 0.3)), A(*slope_pt(sj + 1.5, 0, 0.6)), 0.05)
        lamp(S, 0, j, 60)
    else:
        u = lt - t0
        g = min(1.0, u / 0.3)
        bob = 0.5 * math.exp(-u * 3.5) * math.sin(u * 17) if g >= 1 else 0.0
        hands = hang(S, A, t, 1.3, drop=-(9.0 - 5.0 * g * g) + bob, face='wide')
        rope(S, 0, A(*LIP), hands, 0.05)
        lamp(S, 0, S['joe'], 80)
        dust(S, [(0.4 * math.cos(i), -0.4 - 1.2 * u * (0.5 + rn(i, 1)), -0.2 - 9 * u * u * (0.4 + rn(i, 2)), 0.8) for i in range(8)], A)
    shoot(S, A(lerp(6.5, 5.6, k), lerp(-8.6, -7.6, k), lerp(-1.0, -4.6, sm((lt - t0) / 0.5))), A(0.2, -0.3, lerp(0.6, -4.6, sm((lt - t0) / 0.5))), 28, fill=1.6)


def hands_slip(S, k, t, lt):
    A = storm(S)
    pull = sm(lt / 0.7) * (1 - sm((lt - 1.1) / 0.2))
    hands = hang(S, A, t, 0.5, drop=-0.5 * pull, face='squint' if lt < 1.1 else 'shut', head=(-0.45, 0.0))
    j = S['joe']
    j.sh[0].rotation_euler[0] += 0.5 * pull
    j.el[0].rotation_euler[0] -= 0.9 * pull
    rope(S, 0, A(*LIP), mid_hands(j))
    lamp(S, 0, j, 46)
    S['jaw']['joe'] = 0.3 * pull
    if lt > 1.15:
        u = lt - 1.15
        h = world_of(j.hands[0])
        S['loop'].location = (h[0] - 0.2 - 0.4 * u, h[1] - 0.2, h[2] - 0.3 - 9 * u * u)
        S['loop'].rotation_euler = (u * 9, u * 5, 0)
    p = j.root.location
    shoot(S, (p[0] + lerp(1.7, 1.3, k), p[1] - lerp(3.6, 3.0, k), p[2] + lerp(3.4, 3.2, k)), (p[0], p[1], p[2] + 2.85), 46, roll=0.04 * math.sin(t * 2), fill=1.7)


def pack_knife(S, k, t, lt):
    A = storm(S)
    seated(S, A, s=SEAT_S - 2.6, strain=1.0, t=t, face='squint', gog=False)
    si = S['simon']
    back = sm(lt / 0.5)
    out = sm((lt - 0.9) / 0.4)
    aR = tuple(lerp(a, b, out) for a, b in zip((lerp(0.62, -0.5, back), lerp(-0.12, 0.7, back), lerp(0.55, 2.4, back), 0.3), (0.95, 0.1, 1.15, 0.3)))
    si.apply(P('sit', lean=-0.5, aL=(0.62, -0.25, 0.55, 0.3), aR=aR, head=(0.35, lerp(0.0, 0.5, back * (1 - out))), lL=(1.3, 0.5), lR=(1.3, 0.45)))
    S['face']['simon'] = 'squint' if out < 0.6 else 'sad'
    lamp(S, 0, si, 40)
    rope(S, 1, world_of(si.hands[0]), A(*LIP))
    if out > 0.05:
        S['blade'].location = world_of(si.hands[1], (0, -0.5, -0.1))
        S['blade'].rotation_euler = (0.3 - SLA, 0, 0.2)
    h = head_of(si)
    shoot(S, (h[0] + lerp(2.6, 2.0, k), h[1] - lerp(4.4, 3.8, k), h[2] - 0.1), (h[0] + 0.1, h[1] - 0.2, h[2] - 0.45), 36, fill=1.9)


def yates_after(S, k, t, lt):
    A = storm(S)
    si, rk = S['simon'], S['rook']
    s = SEAT_S - 5.6
    si.place(A(*slope_pt(s, 0.0, 0.05)), 0.0, 0.3)
    cover = sm((lt - 0.9) / 0.5)
    si.apply(blend(P('sit', lean=-0.75, aL=(0.5, 0.2, 0.4), aR=(0.5, 0.2, 0.4), head=(-0.2, 0.0), lL=(1.3, 0.5), lR=(1.3, 0.45)),
                   P('sit', lean=-0.2, aL=(1.2, -0.2, 2.3, 0.5), aR=(1.2, -0.2, 2.3, 0.5), head=(0.55, 0.0), lL=(1.5, 1.2), lR=(1.5, 1.1)), cover))
    S['face']['simon'] = 'wide' if cover < 0.4 else 'shut'
    lamp(S, 0, si, 40)
    a = slope_pt(s - 1.2, 0.3, 0.12)
    rope(S, 1, A(*slope_pt(s - 0.4, 0.1, 0.5)), A(*a), 0.05)
    S['fray'].location, S['fray'].rotation_euler = A(*a), (-(PI / 2 - SLA), 0, 0)
    for i, o in enumerate(S['wall']['seat']):
        o.location = slope_pt(SEAT_S - 1.0 - 4.0 * rn(i, 5), 2.6 * (rn(i, 6) - 0.5), 0.1)
    rp = slope_pt(s + 1.2, 3.0, 0.0)
    rk.place(A(*rp), -0.3)
    S['hat_off'] = sm((lt - 0.6) / 0.5)
    rk.apply(blend(P('stand', **STARTLE), to_chest(), (lt - 0.5) / 0.5))
    S['face']['rook'] = 'shocked' if lt < 0.6 else 'sad'
    h = head_of(rk)
    rooklight(S, (h[0] + 2.0, h[1] - 2.5, h[2] + 1.0), 200)
    shoot(S, A(*slope_pt(s - lerp(5.0, 4.4, k), lerp(-0.6, 0.2, k), lerp(1.9, 2.2, k))), A(*slope_pt(s + 0.4, 1.3, 1.7)), 31, fill=1.9)


# ---------------------------------------------------------------- the morning after
def dawn_descend(S, k, t, lt):
    A = dawn(S)
    si = S['simon']
    dn = lerp(19.0, 22.5, k)
    p = wall_pt(-5.0, dn, 1.5)
    si.place(A(p[0], p[1], p[2] - 1.3), PI + 0.25 * math.sin(t * 1.2), 0.0, 0.08 * math.sin(t * 2))
    si.apply(P('stand', aL=(1.9, 0.0, 1.5, 0.4), aR=(1.2, 0.1, 1.3, 0.4), lL=(1.0, 0.9), lR=(0.8, 0.6), head=(0.55, 0.3)))
    S['face']['simon'] = 'tired'
    top = wall_pt(-5.0, 0.0, 0.3)
    rope(S, 0, A(*top), mid_hands(si), 0.05)
    rope(S, 1, world_of(si.body, (0, -0.3, 0.1)), A(p[0], p[1] - 0.2, p[2] - 16), 0.05)
    shoot(S, A(lerp(-10.5, -9.5, k), lerp(-5.0, -4.2, k), lerp(-17.5, -21, k)), A(-4.8, 4.2, lerp(-18.6, -22, k)), 30, fill=1.9, fcol='FFE0D0')


FOOT = (-5.0, -17.0, -52.0)


def crev_look(S, k, t, lt):
    A = dawn(S)
    si, rk = S['simon'], S['rook']
    si.place(A(*FOOT), PI + 0.1)
    drop = sm((lt - 1.5) / 0.5)
    scan = math.sin(lt * 2.4) * (1 - drop)
    si.apply(P('stand', lean=lerp(0.3, 0.1, drop), head=(lerp(0.25, 0.6, drop), 0.5 * scan), aL=(0.3, 0.3, 0.4), aR=(0.3, 0.3, 0.4), lL=(0.2, 0.3), lR=(-0.15, 0.2)))
    S['face']['simon'] = 'wide' if drop < 0.5 else 'shut'
    seen(S['saxe'].children, True)
    rp = (FOOT[0] + 2.9, FOOT[1] + 0.3, FOOT[2])
    rk.place(A(*rp), PI - 0.3)
    S['hat_off'] = drop
    rk.apply(blend(P('stand', lean=0.3, head=(0.3, 0.3)), to_chest(), drop))
    S['face']['rook'] = 'sad'
    shoot(S, A(FOOT[0] + lerp(3.6, 2.6, k), FOOT[1] + lerp(8.0, 7.2, k), FOOT[2] + lerp(1.9, 1.6, k)), A(FOOT[0] + 1.4, FOOT[1], FOOT[2] + 2.1), 30, fill=1.6,
          fcol='FFE0D0')


def walk_alone(S, k, t, lt):
    A = glacier(S)
    si, rk = S['simon'], S['rook']
    y = -15.0 - 1.4 * lt
    si.place(A(4.0, y, 0.0), 0.05)
    si.apply(dict(walk(lt, 1.2), head=(0.6, 0.0)))
    S['face']['simon'] = 'tired'
    seen(S['saxe'].children, True)
    rp = (1.9, -2.3, 0.0)
    back = sm((lt - 1.0) / 0.5)
    rk.place(A(*rp), lerp(look_yaw(rp, (0, 0)), look_yaw(rp, (4, y)), back))
    rk.apply(blend(P('stand', lean=0.5, head=(0.6, 0.0)), P('stand', head=(0.1, 0.0)), back))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(6.6, 6.0, k), y - lerp(7.0, 6.0, k), lerp(1.2, 1.5, k)), A(3.4, y + 1.0, 2.0), 30)


def seat_dawn(S, k, t, lt):
    A = dawn(S)
    rk = S['rook']
    a, b = slope_pt(SEAT_S - 0.4, 0.0, 0.14), slope_pt(SEAT_S - 2.6, 0.7, 0.12)
    rope(S, 1, A(*a), A(*b), 0.05)
    S['fray'].location, S['fray'].rotation_euler = A(*b), (-(PI / 2 - SLA), 0, 0.3)
    for i, o in enumerate(S['wall']['seat']):
        if i % 2:
            o.location = slope_pt(SEAT_S - 1.5 - 4.0 * rn(i, 5), 2.8 * (rn(i, 6) - 0.5), 0.1)
    rp = slope_pt(SEAT_S - 1.6, 2.5, 0.0)
    rk.place(A(*rp), look_yaw(rp, b) + 0.3)
    down = sm((lt - 0.4) / 0.5)
    rk.apply(blend(P('stand', lean=0.3, head=(0.45, 0.0)), dict(KNEE, aR=(1.0, 0.2, 0.3), aL=(0.4, 0.1, 0.6), head=(0.4, 0.0), lean=0.5), down))
    S['face']['rook'] = 'sad'
    shoot(S, A(*slope_pt(lerp(SEAT_S - 7.5, SEAT_S - 6.6, k), lerp(-2.4, -1.6, k), lerp(2.2, 1.9, k))), A(*slope_pt(SEAT_S - 1.2, 1.3, 1.2)), 33, fill=1.3,
          fcol='FFE0D0')


def rook_think(S, k, t, lt):
    A = dawn(S)
    rk = S['rook']
    cam = (lerp(5.4, 4.8, k), lerp(-3.4, -2.8, k), 3.1)
    rk.place(A(*PERCH), look_yaw(PERCH, cam) - 0.25)
    tap = 0.5 + 0.5 * math.sin(lt * 9)
    rk.apply(P('tap', aR=(1.25, -0.25, 2.2 - 0.25 * tap, 0.6), head=(0.15, -0.1)))
    S['face']['rook'] = 'calm' if lt < 1.2 else 'warm'
    rope(S, 1, A(*slope_pt(7, 0.4, 0.2)), A(0.1, -0.1, 0.05))
    rope(S, 0, A(0.1, -0.1, 0.05), A(0.2, -0.3, -5.0))
    shoot(S, A(*cam), A(PERCH[0] - 0.1, PERCH[1], PERCH[2] + 2.45), 40, fill=1.2, fcol='FFE0D0')


def rook_go(S, k, t, lt):
    A = storm(S)
    rk = S['rook']
    pop = sm(lt / 0.35)
    go = max(0.0, lt - 0.95)
    z = PERCH[2] + 2.8 * go - 9 * go * go
    rk.place(A(PERCH[0] - 1.6 * go, PERCH[1] - 3.2 * go, z), look_yaw(PERCH, (0, -6)), 0.5 * min(1.0, go * 3))
    fl = math.sin(lt * 20)
    rk.apply(blend(blend(P('stand', head=(0.2, 0.2)), P('stand', aL=(1.0, 0.45, 2.35, 0.7), aR=(1.0, 0.45, 2.35, 0.7), head=(-0.05, 0.0)), pop),
                   P('up', aL=(1.6, 1.2 + 0.4 * fl, 0.2), aR=(1.6, 1.2 + 0.4 * fl, 0.2), lL=(0.4, 0.8), lR=(0.4, 0.8)), go * 5))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.5
    rope(S, 1, A(*slope_pt(7, 0.4, 0.2)), A(0.1, -0.1, 0.05))
    rope(S, 0, A(0.1, -0.1, 0.05), A(0.2, -0.3, -5.0))
    S['wall']['rim'].data.energy = 280
    feather(S, A(PERCH[0], PERCH[1] - 0.4, PERCH[2] + 2.4), lt, 1.0)
    shoot(S, A(lerp(-2.6, -2.0, k), lerp(-7.2, -6.6, k), lerp(1.5, 1.2, k)), A(PERCH[0] - 0.6, PERCH[1] - 0.4, PERCH[2] + 2.1 - 2.0 * min(1.0, go * 2)), 30, fill=1.9,
          fcol='FFE0C8')


# ---------------------------------------------------------------- in the crevasse
def alive(S, k, t, lt):
    A = crevasse(S)
    wake = sm((lt - 0.7) / 0.3)
    j = lie(S, A, 'shut' if wake < 0.5 else 'wide', lean=-0.35 * wake)
    j.sh[1].rotation_euler[0] -= 0.6 * wake
    lamp(S, 0, j, 70)
    S['jaw']['joe'] = 0.35 * wake
    for i in range(3):                                                # his breath
        u = (lt * 0.8 + i * 0.33) % 1
        h = head_of(j)
        S['chunks'][i].location = (h[0] + 0.5 + 0.5 * u, h[1] - 0.3, h[2] + 0.4 + 0.9 * u)
        s = (0.5 + 1.2 * u) * wake
        S['chunks'][i].scale = (s, s, s)
    rk = S['rook']
    rp = (-1.2, 1.9, 0.0)
    rk.place(A(*rp), look_yaw(rp, (JL[0], -2.0)))
    rk.apply(blend(P('stand', lean=0.55, head=(0.6, 0.0), aL=(0.3, 0.4, 0.3), aR=(0.3, 0.4, 0.3)), P('stand', **STARTLE), (lt - 0.75) / 0.15))
    S['hat_jump'] = 0.16 * wake
    S['face']['rook'] = 'sad' if wake < 0.5 else 'shocked'
    rooklight(S, A(1.8, 0.6, 3.2), 200)
    shoot(S, A(lerp(1.9, 1.5, k), lerp(-2.4, -1.9, k), lerp(3.0, 2.7, k)), A(-1.6, 0.7, 1.35), 32, fill=1.8)


def rope_dark(S, k, t, lt):
    A = crevasse(S)
    j = S['joe']
    z = lerp(-9.5, -11.5, k)
    j.place(A(-0.15, 0.3, z), -PI / 2 + 0.6 * math.sin(t * 0.9), 0.0, 0.1 * math.sin(t * 2))
    j.apply(P('stand', aL=(1.9, 0.0, 1.5, 0.4), aR=(1.2, 0.1, 1.3, 0.4), lL=(1.0, 0.9), lR=(0.35, 0.0), head=(0.75, 0.0)))
    stiff(j)
    S['face']['joe'] = 'wide'
    lamp(S, 0, j, 160)
    S['lamps'][1].location, S['lamps'][1].data.energy = A(0.2, 0.3, z - 12), 500
    rope(S, 0, A(-0.55, 0.3, 0.2), A(-0.3, 0.3, z + 2.4), 0.045)
    e = (0.9 * math.sin(t * 1.7), 0.3 + 0.5 * math.cos(t * 1.3), z - 15)
    rope(S, 1, A(-0.2, 0.25, z + 1.2), A(*e), 0.05)
    S['fray'].location, S['fray'].rotation_euler = A(*e), (0, 0, 0)
    shoot(S, A(lerp(1.5, 1.2, k), lerp(-1.6, -1.2, k), z + lerp(7.5, 6.5, k)), A(0.0, 0.4, z - 12), 22, roll=0.1 * k, fill=1.5)


# ---------------------------------------------------------------- the crawl, the camp
def glac_far(S, k, t, lt):
    A = glacier(S)
    j = S['joe']
    y = -30.0 - 0.9 * lt
    prone(j, A(0.0, y, 0.38), 0.0)
    j.apply(crawl_pose(lt, 1.4, head=(-0.5, 0.0)))
    stiff(j)
    tr = S['glac']['trail']
    tr.location, tr.scale = (0.0, (y + 2.6) / 2 - 0.4, 0.02), (0.9, abs(y + 2.6) + 2.4, 0.03)
    shoot(S, A(lerp(-15, -13, k), lerp(-49, -46, k), lerp(8, 7, k)), A(1.0, -20, 1.0), 30, fill=0.0)


def night_rocks(S, k, t, lt):
    A = moraine(S, night=True)
    j, rk = S['joe'], S['rook']
    y = -36.0 - 0.7 * lt
    prone(j, A(HOP[0], y, 0.38), 0.0)
    j.apply(crawl_pose(lt, 1.2, head=(-0.75, 0.0)))
    stiff(j)
    S['face']['joe'] = 'tired'
    rp = (HOP[0] + 1.7, y - 3.4, 0.0)
    rk.place(A(*rp), look_yaw(rp, (HOP[0], y)))
    wv = math.sin(lt * 7)
    rk.apply(dict(walk(-lt, 0.8), aL=(1.3, 0.3 + 0.25 * wv, 1.0), aR=(1.1, 0.1, 0.5), head=(0.35, 0.0)))
    S['face']['rook'] = 'sad'
    S['lant'].location = world_of(rk.hands[1], (0, -0.1, -0.35))
    rooklight(S, world_of(rk.hands[1], (0, -0.6, 0.2)), 260)
    shoot(S, A(HOP[0] - lerp(2.6, 2.0, k), y - lerp(8.6, 7.8, k), lerp(0.9, 1.2, k)), A(HOP[0] + 0.7, y - 1.6, 1.3), 30, fill=1.7, fcol='C8D4FF')


def embrace(S, k, t, lt):
    A = moraine(S, night=True)
    j, si, rc, rk = S['joe'], S['simon'], S['rich'], S['rook']
    jp = (0.6, -5.0)
    j.place(A(jp[0], jp[1], 0.0), 0.3)
    j.apply(P('sit', lR=(1.45, 0.0), lL=(1.4, 0.6), aL=(0.4, 0.3, 0.4), aR=(0.5, 0.2, 0.5), head=(0.35, -0.4), lean=0.1))
    stiff(j, 0.15)
    sp = (jp[0] + 1.7, jp[1] - 0.3)
    si.place(A(sp[0], sp[1], 0.0), look_yaw(sp, jp))
    si.apply(dict(KNEE, aL=(1.3, 0.0, 0.5), aR=(1.3, 0.0, 0.5), head=(0.2, 0.0), lean=0.3))
    lamp(S, 0, si, 90)
    rcp = (jp[0] - 0.4, jp[1] + 2.4)
    rc.place(A(rcp[0], rcp[1], 0.0), look_yaw(rcp, jp))
    rc.apply(P('stand', aL=(0.5, 0.9, 2.5, -0.4), aR=(0.5, 0.9, 2.5, -0.4), head=(0.45, 0.0), lean=0.2))
    setface(S, joe='tired', simon='wide', rich='wide', rook='sad')
    S['jaw']['simon'] = 0.25 + 0.15 * math.sin(lt * 8)
    rp = (jp[0] - 2.6, jp[1] + 0.2, 0.0)
    rk.place(A(*rp), look_yaw(rp, jp))
    S['hat_off'] = sm(lt / 0.5)
    rk.apply(blend(P('stand', head=(0.2, 0.0)), to_chest(), lt / 0.5))
    rooklight(S, A(rp[0], rp[1] - 2.5, 3.2), 200)
    shoot(S, A(lerp(-0.6, 0.4, k), lerp(-12.6, -11.6, k), lerp(1.6, 1.9, k)), A(0.6, -4.6, 1.8), 33, fill=1.7, fcol='FFD8B0')


def mule(S, k, t, lt):
    A = moraine(S)
    j, si, ar, rk = S['joe'], S['simon'], S['arr'], S['rook']
    x, y = -6.0 - 1.3 * lt, -9.0
    m = S['mule']
    bobz = 0.05 * abs(math.sin(lt * 5.2))
    m.location, m.rotation_euler = A(x, y, bobz), (0, 0, -PI / 2)
    for i, lg in enumerate(S['mlegs']):
        lg.rotation_euler = (0.4 * math.sin(lt * 5.2 + (0 if i in (0, 3) else PI)), 0, 0)
    j.place(A(x + 0.2, y, 1.72 + bobz), -PI / 2)
    j.apply(P('stand', lL=(0.5, 0.9), lR=(1.05, 0.0), aL=(0.9, 0.0, 0.8), aR=(0.9, 0.0, 0.8), head=(0.3, 0.0), lean=0.2))
    stiff(j, 0.55)
    ar.place(A(x - 4.0, y - 0.6, 0.0), -PI / 2)
    ar.apply(dict(walk(lt, 1.3), aL=(-0.6, 0.2, 0.4)))
    rope(S, 0, world_of(ar.hands[0]), world_of(m, (0, -2.5, 2.5)), 0.035)
    si.place(A(x + 3.6, y + 0.9, 0.0), -PI / 2)
    si.apply(walk(lt + 0.5, 1.3))
    rk.place(A(x + 1.15, y, 1.75 + bobz), PI / 2)
    rk.apply(P('sit', lL=(1.2, 1.3), lR=(1.2, 1.3), aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), head=(0.1, 0.5), lean=0.0, lift=-0.5))
    setface(S, joe='tired', simon='tired', arr='calm', rook='deadpan')
    shoot(S, A(x - lerp(2.4, 1.4, k), y - lerp(9.6, 8.8, k), lerp(2.0, 2.4, k)), A(x - 0.3, y, 2.5), 32)


# ---------------------------------------------------------------- afterwards
def ward(S):
    A = env(S, 'ward', '9FB8D0', sun=0.0, fk=2.0, skyk=0.6)
    Wd_ = S['ward']
    Wd_['day'].data.energy = 1500
    Wd_['key'].data.energy = 900
    return A


def in_bed(S, A, lt, look=0.0):
    jw = S['jward']
    jw.place(A(*BED), -PI / 2)
    jw.apply(P('stand', lL=(1.5, 0.05), lR=(1.85, 0.0), aL=(0.5, 0.25, 0.7), aR=(0.5, 0.25, 0.8), head=(0.1, lerp(0.0, -0.9, look)), lean=-0.55, lift=-0.5))
    h = world_of(jw.kn[1], (0, 0, -0.45))
    rope(S, 3, (h[0], h[1], h[2]), A(3.0, BED[1] - 0.2, 5.0), 0.02)
    return jw


def hosp_bed(S, k, t, lt):
    A = ward(S)
    in_bed(S, A, lt)
    S['face']['jward'] = 'tired'
    rk = S['rook']
    rp = (-1.5, 2.0, 0.0)
    rk.place(A(*rp), look_yaw(rp, (4.4, 2.5)) - 0.35)
    up = sm((lt - 1.0) / 0.4)
    rk.apply(P('stand', aR=(1.0, 0.0, 1.5, 0.4), aL=(0.9, 0.1, 1.4, 0.5), head=(lerp(0.4, 0.05, up), lerp(0.0, -0.35, up))))
    S['pad'].location = world_of(rk.hands[1], (-0.15, -0.3, -0.1))
    S['pad'].rotation_euler = (0.5, 0, look_yaw(rp, (4.4, 2.5)) - 0.35)
    S['face']['rook'] = 'calm' if up < 0.5 else 'sad'
    shoot(S, A(lerp(0.6, 1.4, k), lerp(-6.2, -5.6, k), lerp(3.4, 3.1, k)), A(2.1, 2.4, 2.4), 30, fill=1.3)


def hosp_close(S, k, t, lt):
    A = ward(S)
    turn = sm((lt - 0.7) / 0.6)
    jw = in_bed(S, A, lt, turn)
    S['face']['jward'] = 'tired' if turn < 0.6 else 'warm'
    h = head_of(jw)
    shoot(S, (h[0] - lerp(2.2, 1.8, k), h[1] - lerp(3.9, 3.4, k), h[2] + 0.5), (h[0] - 0.6, h[1], h[2] - 0.3), 44, fill=1.5)


def crag_climb(S, k, t, lt):
    A = daysky(S, 'crag', '6AA8E8', sun=3.6, sdir=(-0.6, -0.6, 0.5), sunc='FFF2D8', fk=2.4)
    jl, rk = S['jlater'], S['rook']
    z = 8.0 + 0.55 * lt
    jl.place(A(0.2, 1.3 + 0.06 * z, z), PI, 0.1)
    jl.apply(climb_pose(lt, 0.8))
    S['face']['jlater'] = 'warm'
    rope(S, 0, world_of(jl.body, (0, -0.35, 0.1)), A(0.6, 1.2, -0.2), 0.04)
    rope(S, 1, world_of(jl.body, (0, -0.35, 0.3)), A(0.4, 4.3, 46), 0.04)
    rp = (3.6, 1.2, 11.6)
    rk.place(A(*rp), look_yaw(rp, (0.2, 1.0)) - 0.5)
    nod = sm((lt - 1.0) / 0.4)
    rk.apply(blend(P('cross', head=(0.5, 0.3)), P('hat', head=(0.4, 0.3)), nod))
    S['hat_tip'] = nod
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(-4.2, -3.4, k), lerp(-6.4, -5.6, k), z + lerp(1.6, 2.4, k)), A(1.6, 1.6, z + 2.3), 30)


def yates_sit(S, k, t, lt):
    A = moraine(S)
    si, rk = S['simon'], S['rook']
    sp = (-12.0, -8.0)
    si.place(A(sp[0], sp[1], 0.0), 1.0)
    si.apply(P('sit', lL=(1.75, 1.9), lR=(1.75, 1.8), aL=(1.3, -0.2, 0.9), aR=(1.3, -0.2, 0.9), head=(lerp(0.6, 0.2, sm((lt - 1.6) / 0.4)), 0.0), lean=0.4))
    S['face']['simon'] = 'sad'
    arr = sm(lt / 0.7)
    rp = (sp[0] + lerp(6.0, 2.6, arr), sp[1] + 1.2, 0.0)
    down = (lt - 0.75) / 0.35
    rk.place(A(*rp), lerp(-PI / 2, -0.3, sm(down)))
    rk.apply(blend(walk(lt, 1.6), dict(P('sit'), lL=(1.5, 1.5), lR=(1.5, 1.4), aL=(0.7, 0.0, 1.2), aR=(0.7, 0.0, 1.2), head=(0.2, 0.5)), down))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(-9.0, -10.0, k), lerp(-16.0, -15.2, k), lerp(1.5, 1.7, k)), A(-10.8, -8.0, 1.5), 34)


def desk_write(S, k, t, lt):
    A = env(S, 'ward', '1E2C4A', sun=0.0, fk=1.6, skyk=0.5)
    Wd_ = S['ward']
    Wd_['lampl'].data.energy = 420
    Wd_['room'].data.energy = 700
    jl, rk = S['jlater'], S['rook']
    jl.place(A(DESK, 3.5, 0.45), 0.0)
    ty = math.sin(lt * 17)
    stop = sm((lt - 1.5) / 0.4)
    jl.apply(P('sit', lL=(1.5, 1.5), lR=(1.5, 1.5), aL=(1.05 + 0.08 * ty * (1 - stop), -0.1, 0.9), aR=(1.05 - 0.08 * ty * (1 - stop), -0.1, 0.9),
               head=(lerp(0.45, 0.0, stop), 0.0), lean=0.25, lift=-0.5))
    S['face']['jlater'] = 'squint' if stop < 0.5 else 'calm'
    S['ward']['sheet'].location.z = 2.0 + 0.1 * (lt % 1.0)
    rp = (DESK - 3.4, 2.2, 0.0)
    rk.place(A(*rp), look_yaw(rp, (DESK - 9, -8)) + 0.9)
    tap = 0.5 + 0.5 * math.sin(lt * 8)
    rk.apply(P('stand', aR=(1.2, 0.0, 1.5, 0.4), aL=(1.25, -0.25, 2.2 - 0.2 * tap, -0.6), head=(0.4, -0.2)))
    S['page'].location = world_of(rk.hands[1], (-0.1, -0.3, -0.1))
    S['page'].rotation_euler = (0.5, 0, look_yaw(rp, (DESK - 9, -8)) + 0.9)
    S['face']['rook'] = 'calm'
    rooklight(S, A(DESK - 4.5, -1.5, 3.6), 220)
    shoot(S, A(DESK - lerp(3.2, 2.4, k), lerp(-4.4, -3.9, k), lerp(2.9, 2.7, k)), A(DESK - 1.2, 2.6, 2.25), 32, fill=1.5, fcol='FFE0C0')


def photo_two(S, k, t, lt):
    """Case-board picture: the two of them at the foot of the mountain."""
    A = daysky(S, 'west', sdir=(-0.5, 0.5, 0.6))
    j, si, rk = face_people(S, A, 0.0, up=0.0)
    rk.place(AWAY)
    j.place(A(-1.0, FP, 0.0), PI - 0.15)
    si.place(A(1.0, FP + 0.2, 0.0), PI + 0.15)
    j.apply(P('hips'))
    si.apply(P('cross'))
    setface(S, joe='warm', simon='warm')
    shoot(S, A(0.3, FP + 7.2, 1.9), A(0.0, FP, 2.1), 40, fill=1.6)


def photo_simon(S, k, t, lt):
    A = moraine(S)
    si = S['simon']
    si.place(A(-12.0, -8.0, 0.0), 0.2)
    si.apply(P('stand', head=(0.25, 0.3)))
    S['face']['simon'] = 'sad'
    shoot(S, A(-11.0, -14.5, 2.3), A(-12.0, -8.0, 2.2), 44)


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: he hangs on the rope close under the lip in the storm, lamp on, looking up; Rook lies on the lip above and peers down at him."""
    A = storm(S)
    hands = hang(S, A, 0.3, 0.2, drop=-8.6, face='wide', head=(-0.2, 0.45))
    rope(S, 0, A(*LIP), hands, 0.07)
    lamp(S, 0, S['joe'], 90)
    S['jaw']['joe'] = 0.45
    rk = S['rook']
    rk.place(A(1.5, 1.3, 0.5), 0.3, 1.25)
    rk.apply(P('stand', aL=(2.3, 0.5, 0.6), aR=(2.3, 0.5, 0.6), head=(-0.5, 0.0)))
    S['face']['rook'] = 'shocked'
    S['hat_jump'] = 0.1
    S['wall']['rim'].data.energy = 600
    rooklight(S, A(1.0, -3.0, 2.2), 420)
    shoot(S, A(-3.8, -7.6, -1.2), A(-1.1, 0.0, -0.9), 30, fill=2.4)


HOST |= {'look_face', 'two_look', 'face_climb', 'rook_coin', 'summit', 'bivi_stove', 'rook_can', 'snowhole', 'leg_sit', 'seat_dig', 'rook_watch', 'yates_after',
         'crev_look', 'walk_alone', 'seat_dawn', 'rook_think', 'rook_go', 'alive', 'night_rocks', 'embrace', 'mule', 'hosp_bed', 'crag_climb', 'yates_sit',
         'desk_write'}
SHOTS3D.update({f.__name__: f for f in (
    look_face, two_look, face_wide, face_climb, hawking_wave, rook_coin, summit, ridge_down, ice_step, step_fall, leg_sit, yates_sees, ridge_two, bivi_stove,
    stove_out, rook_can, snowhole, knot, seat_dig, lower_side, lower_far, rook_watch, over_edge, hands_slip, pack_knife, yates_after, dawn_descend, crev_look,
    walk_alone, seat_dawn, rook_think, rook_go, alive, rope_dark, glac_far, night_rocks, embrace, mule, hosp_bed, hosp_close, crag_climb, yates_sit, desk_write)})


def cam_orbit(S, k):
    """prm "orb": [degrees, dolly, rise] swings the camera round its own look-at point over the shot."""
    o = S['prm'].get('orb')
    if not o:
        return
    deg, dolly, rise = (list(o) + [0, 0])[:3]
    c, tg = S['camrig'].location, S['camtgt'].location
    a = math.radians(deg) * (k - 0.5)
    m = 1 - dolly * (k - 0.5)
    dx, dy = c[0] - tg[0], c[1] - tg[1]
    S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, c[2] + rise * (k - 0.5))


def _with_orbit(f):
    def g(S, k, t, lt):
        f(S, k, t, lt)
        cam_orbit(S, k)
    g.__name__ = f.__name__
    return g


SHOTS3D = {name: _with_orbit(f) for name, f in SHOTS3D.items()}
STILLS.update(two=photo_two, simon=photo_simon, thumb=photo_thumb)
