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
        'camp_night', 'bags_packed', 'storm_face', 'rope_line', 'slide', 'two_men', 'rook_hatoff', 'rook_turn', 'signoff'}
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
    add('cube', 'E8EEF8', (0.02, -0.02, -0.3), rot=(0.25, 0, 0), scale=(0.03, 0.16, 0.5), size=1, parent=kn.root, rough=0.1, emit=1.2)   # a small blade
    add('cube', 'A8472E', (0.02, -0.06, -0.02), scale=(0.07, 0.2, 0.3), size=1, parent=kn.root)
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
        A = env(S, 'mor', '0A1230', sun=0.6, sunc='9DB8FF', sdir=(-0.4, 0.3, 0.8), fk=1.6)
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
    pose = dict(HANGING)
    pose['lL'] = (0.35 + 0.2 * math.sin(t * 3.1), 0.7 + 0.3 * math.sin(t * 2.7))
    if head:
        pose['head'] = head
    j.apply(P('stand', **pose))
    stiff(j)
    S['face']['joe'] = face
    return A(x - 3.1 * math.sin(a), y - 0.22, z + 3.1)


def prone(rig, pos, heading=0.0, slope=0.0):
    """Face down, head towards the heading (0 = -Y)."""
    rig.place(pos, heading, PI / 2 - slope)


def crawl_pose(lt, sp=1.6, head=(-0.75, 0.0)):
    s = math.sin(lt * sp * 2 * PI)
    return P('stand', aL=(2.3 + 0.5 * s, 0.25, 0.5 - 0.4 * s), aR=(2.3 - 0.5 * s, 0.25, 0.5 + 0.4 * s), lL=(0.3 + 0.3 * s, 0.7 + 0.5 * s), lR=(-0.05, 0.0),
             head=head)


def seated(S, A, s=SEAT_S, strain=0.0, t=0.0, face='squint', gog=True, pay=None):
    """Yates in his bucket seat on the slope, the rope running from his waist down to the lip."""
    si = S['simon']
    sh = 0.03 * strain * math.sin(t * 31)
    si.place(A(*slope_pt(s, sh, 0.05)), 0.0, 0.3)
    aL, aR = (1.0, -0.1, 0.9, 0.3), (1.0, -0.1, 0.9, 0.3)
    if pay is not None:
        u = math.sin(pay * 7)
        aL, aR = (1.0 + 0.3 * u, -0.1, 0.9 - 0.3 * u, 0.3), (1.0 - 0.3 * u, -0.1, 0.9 + 0.3 * u, 0.3)
    si.apply(P('sit', lean=-0.3 - 0.22 * strain + sh, aL=aL, aR=aR, head=(0.35, 0.0), lL=(1.3, 0.5), lR=(1.3, 0.45)))
    seen(si.extra['gog'], gog)
    S['face']['simon'] = face
    return A(*slope_pt(s - 0.55, 0, 0.95))                          # where the rope leaves his hands


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
    S['rook'].place(A(*PERCH), look_yaw(PERCH, (0, 0)))             # only his boots and coat edge are in frame
    S['rook'].apply(P('stand', lean=0.3))
    if u <= 0:
        rope(S, 0, A(*LIP), A(0.1 * math.sin(t * 9), HANG[1] - 0.2, -9.9))
        rope(S, 1, A(*slope_pt(SEAT_S - 0.5, 0, 0.3)), A(*LIP))
    else:
        s_end = max(0.0, 12 - 60 * u)
        fall = 34 * u * u
        if s_end > 0:
            rope(S, 1, A(*slope_pt(s_end, 0.5 * math.sin(u * 30), 0.25)), A(*LIP))
            rope(S, 0, A(*LIP), A(0.4 * math.sin(u * 20), HANG[1] - 0.2, -9.9 - fall))
        else:
            v = u - 0.2
            rope(S, 0, A(0.3 * math.sin(u * 25), -0.3, -40 * v * v), A(0.5 * math.sin(u * 17), HANG[1], -9.9 - fall))
    shoot(S, A(lerp(1.3, 1.0, k), lerp(-2.9, -2.4, k), lerp(1.7, 1.2, k)), A(0.0, 0.3, lerp(0.2, -0.8, k)), 26, roll=-0.08, fill=1.8)


def drop_away(S, k, t, lt):
    A = storm(S)
    u = lt * 1.4
    d = 4 + 26 * u * u
    j = S['joe']
    j.place(A(0.3 * math.sin(lt * 5), HANG[1] - 0.3, HANG[2] - d), lt * 2.2, lt * 2.6, 0.3)
    j.apply(P('stand', aL=(2.2, 0.9, 0.3), aR=(1.6, 1.1, 0.4), lL=(0.6, 0.9), lR=(-0.2, 0.0), head=(-0.3, 0)))
    stiff(j)
    S['face']['joe'] = 'wide'
    lamp(S, 0, j, 120)
    p = j.root.location
    rope(S, 0, (p[0] + 0.8 * math.sin(lt * 16), p[1] - 0.3, p[2] + 9), (p[0], p[1], p[2] + 1.6))
    shoot(S, A(0.55, lerp(-0.9, -1.2, k), lerp(2.2, 1.6, k)), A(0.0, -1.2, -40), 22, roll=0.15 * k, fill=1.2)


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
    cam = (1.3, -2.3, 3.5)
    S['rook'].place(A(*PERCH), look_yaw(PERCH, cam) + 0.15)
    S['rook'].apply(P('stand', aR=(1.55, 0.05, 1.5, 0.5), aL=(0.2, 0.2, 0.3), head=(0.12, -0.3)))
    S['face']['rook'] = 'deadpan' if lt < 0.3 else 'calm'
    tip = rope_in_hand(S, A, 1.0)
    S['wall']['rim'].data.energy = 220
    shoot(S, A(lerp(1.2, 1.45, k), lerp(-2.5, -2.1, k), 3.45), A(PERCH[0] - 0.3, PERCH[1] - 0.15, PERCH[2] + 2.55), 58, fill=2.0, fcol='FFE0C8')


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
    z = lerp(40, 7, k ** 1.25)
    j.place(A(-0.9 + 0.3 * math.sin(lt * 4), 0.6, z), lt * 2.5, lt * 4.4, 0.2)
    j.apply(P('stand', aL=(2.2, 0.9, 0.3), aR=(1.4, 1.1, 0.5), lL=(0.7, 1.0), lR=(-0.25, 0.0), head=(-0.2, 0)))
    stiff(j)
    S['face']['joe'] = 'wide'
    lamp(S, 0, j, 160)
    rope(S, 0, A(-0.9 + 0.7 * math.sin(lt * 15), 0.6, z + 8), A(-0.9, 0.6, z + 1.4))
    dust(S, [(-0.9 + 2.2 * (rn(i, 3) - 0.5), 0.6 + 2 * (rn(i, 4) - 0.5), z + 2 + 9 * rn(i, 5) + 6 * lt, 0.6 + rn(i, 6)) for i in range(9)], A)
    shoot(S, A(lerp(2.0, 1.6, k), lerp(-3.6, -3.0, k), lerp(-2.6, -1.6, k)), A(-0.7, 0.6, lerp(34, 16, sm(k))), 21, roll=0.2 * (k - 0.5), fill=1.5)


def lie(S, A, face='shut', lean=0.0):
    j = S['joe']
    j.place(A(JL[0], JL[1] + 1.0, 0.36), 0.0, -PI / 2)
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
        j.place(A(JL[0], JL[1] + 1.0, z), 0.0, -PI / 2 + 1.2 * (1 - lt / hit))
        j.apply(P('stand', aL=(2.0, 0.9, 0.3), aR=(1.4, 1.1, 0.5), lL=(0.7, 1.0), lR=(-0.2, 0.0)))
        stiff(j)
        S['face']['joe'] = 'wide'
    else:
        lie(S, A, 'shut' if lt < 0.8 else 'tired')
        u = lt - hit
        dust(S, [(JL[0] + (1.2 + 2.6 * u) * math.cos(i * 0.7), JL[1] + 0.5 + (1.2 + 2.6 * u) * math.sin(i * 0.7) * 1.4, 0.2 + 2.2 * u - 3.2 * u * u + 0.3 * rn(i, 7),
                     1.6 + 3 * u) for i in range(9)], A)
    lamp(S, 0, j, 70)
    rp = (-1.0, -2.6, 0.0)
    drop = sm((lt - 0.45) / 0.5)
    S['rook'].place(A(rp[0], rp[1], lerp(7.5, 0.0, drop)), look_yaw(rp, (JL[0], 1.0)))
    S['rook'].apply(blend(P('up', aL=(1.5, 1.3, 0.2), aR=(1.5, 1.3, 0.2), lL=(0.4, 0.7), lR=(0.4, 0.7)), P('stand', lean=0.35, head=(0.3, 0.0)), (lt - 0.85) / 0.25))
    S['face']['rook'] = 'shocked' if lt < 1.0 else 'calm'
    shoot(S, A(lerp(2.9, 2.5, k), lerp(-7.4, -6.6, k), lerp(1.7, 1.4, k)), A(-1.5, -0.3, lerp(1.6, 1.1, k)), 26, fill=1.5)


def look_up(S, k, t, lt):
    A = crevasse(S)
    g = S['glove']
    reach = sm(lt / 0.5)
    g.place(A(-1.45 + 0.05 * math.sin(t * 5), lerp(0.2, 0.75, reach), lerp(2.2, 3.5, reach)), (-1.05, 0.25, 0.35))
    g.grip(lerp(0.1, 0.55, sm((lt - 0.6) / 0.4)))
    S['lamps'][0].location = A(-1.6, 0.6, 4.5)
    S['lamps'][0].data.energy = 90
    shoot(S, A(-1.75, lerp(-0.4, -0.1, k), 1.5), A(-0.2 + 0.5 * math.sin(lt * 1.3), 1.4, 42), 17, roll=lerp(-0.1, 0.08, k), fill=1.4)


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
    shoot(S, A(lerp(2.6, 2.2, k), lerp(-4.6, -4.0, k), lerp(2.6, 2.1, k)), A(-2.4, 0.6, lerp(2.6, 2.0, slip)), 30, fill=1.5)


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
    S['hat_jump'] = 0.28 * pop
    feather(S, A(RK[0] + 0.2, RK[1] - 0.3, 3.4), lt, 0.32)
    shoot(S, A(lerp(2.5, 2.2, k), lerp(-3.8, -3.3, k), 2.5), A(RK[0], RK[1], 2.75), 50, fill=2.0)


def abseil(S, k, t, lt):
    A = crevasse(S)
    j = S['joe']
    z = lerp(-4.2, -9.5, sm(k))
    j.place(A(-0.15, 0.3, z), -PI / 2 + 0.3 * math.sin(t * 1.3), 0.0, 0.12 * math.sin(t * 2))
    j.apply(P('stand', aL=(1.9, 0.0, 1.5, 0.4), aR=(1.2, 0.1, 1.3, 0.4), lL=(1.0, 0.9), lR=(0.35, 0.0), head=(0.5, 0.0)))
    stiff(j)
    S['face']['joe'] = 'squint'
    lamp(S, 0, j, 110)
    rope(S, 0, A(-0.55, 0.3, 0.2), A(-0.3, 0.3, z + 2.4))
    rope(S, 1, A(-0.2, 0.25, z + 1.2), A(-0.1 + 0.2 * math.sin(t * 3), 0.3, z - 9))
    rk = S['rook']
    rk.place(A(*RK), look_yaw(RK, (4, -1.7)))
    rk.apply(P('stand', lean=0.6, head=(0.7, 0.2), aL=(0.3, 0.5, 0.3), aR=(0.3, 0.5, 0.3)))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(2.9, 2.6, k), lerp(-8.6, -7.6, k), lerp(-4.0, -7.2, sm(k))), A(-0.5, 0.0, lerp(-1.6, -4.2, sm(k))), 23, fill=1.5)


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
    y = lerp(12.2, 13.6, k)
    prone(j, A(*ramp_pt(y, -0.4, 0.38)), PI, RA)
    j.apply(crawl_pose(lt, 1.5, head=(-0.6, 0.0)))
    stiff(j)
    S['face']['joe'] = 'squint'
    rk = S['rook']
    rp = ramp_pt(20.5, 1.6, 0.0)
    rk.place(A(*rp), look_yaw(rp, (0, 12)))
    w = math.sin(lt * 9)
    rk.apply(P('stand', aR=(2.6, 0.5 + 0.3 * w, 0.6), aL=(0.3, 0.3, 0.3), head=(0.3, 0.0), lean=0.2))
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(5.2, 4.6, k), lerp(7.4, 8.6, k), lerp(6.2, 6.8, k)), A(0.3, 17.0, 9.6), 27, fill=1.4, fcol='FFF0D0')


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
    j.apply(P('sit', lR=(1.45, 0.0), lL=(1.3, 1.2), aR=(2.35, 0.25, 1.35, 0.4), aL=(0.4, 0.3, 0.4), head=(-0.5, 0.0), lean=-0.12))
    stiff(j, 0.2)
    seen(S['jbottle'].children, True)
    S['face']['joe'] = 'tired'
    S['jaw']['joe'] = 0.5
    b = world_of(S['jbottle'], (0, 0, -0.32))
    u = (lt * 0.9) % 1.0
    S['chunks'][0].location = (b[0], b[1], b[2] - 0.9 * u * u) if lt > 0.25 else AWAY
    S['chunks'][0].scale = (0.22, 0.22, 0.34)
    rk = S['rook']
    rp = (jp[0] - 2.3, jp[1] + 0.5, 0.0)
    rk.place(A(*rp), look_yaw(rp, jp))
    S['hat_off'] = sm((lt - 0.5) / 0.4)
    rk.apply(blend(P('stand', lean=0.25, head=(0.1, 0.0)), to_chest(), (lt - 0.5) / 0.4))
    S['face']['rook'] = 'sad'
    shoot(S, A(jp[0] - lerp(1.6, 1.2, k), jp[1] - lerp(6.6, 5.8, k), lerp(1.9, 2.1, k)), A(jp[0] - 0.9, jp[1], 1.95), 36)


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
    x = lerp(-6.2, -4.5, sm(lt / 0.45))
    rp = (x, -1.4, 0.0)
    rk.place(A(*rp), look_yaw(rp, (-2.5, -0.7)))
    tap = sm((lt - 0.45) / 0.12)
    rk.apply(blend(walk(lt, 1.8), P('stand', lean=0.35, aR=(1.25 + 0.15 * math.sin(lt * 20), 0.1, 0.25), head=(0.3, 0.0)), tap))
    S['face']['rook'] = 'calm' if tap < 0.5 else 'shocked'
    shoot(S, A(lerp(-1.5, -1.9, k), lerp(-6.4, -5.8, k), lerp(1.5, 1.3, k)), A(-3.2, -0.8, 1.35), 34, fill=1.5, fcol='FFD8B0')


# ---------------------------------------------------------------- how it came to that: the storm on the slope
def storm_face(S, k, t, lt):
    A = storm(S)
    seated(S, A, strain=0.4, t=t, gog=False, face='squint')
    si = S['simon']
    si.head.rotation_euler = (lerp(0.1, 0.5, sm(lt / 0.8)), 0, 0.25 * math.sin(lt * 2.2))
    lamp(S, 0, si, 40)
    rk = S['rook']
    rp = slope_pt(SEAT_S + 1.7, 1.5, 0.0)
    rk.place(A(*rp), -0.25)
    rk.apply(P('hat', lean=0.3, head=(0.3, 0.1)))
    S['face']['rook'] = 'sad'
    S['wall']['rim'].data.energy = 0
    h = world_of(si.head)
    rope(S, 1, seated_rope(S, A), A(*LIP))
    shoot(S, (h[0] + lerp(1.3, 1.0, k), h[1] - lerp(3.6, 3.0, k), h[2] + 0.15), (h[0] + 0.35, h[1], h[2] + 0.25), 48, fill=2.0)


def seated_rope(S, A, s=SEAT_S):
    return A(*slope_pt(s - 0.75, 0, 1.0))


def lowering(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=0.15, t=t, pay=lt)
    js = lerp(17.0, 11.0, k)
    j = S['joe']
    j.place(A(*slope_pt(js, 0.2 * math.sin(lt * 3), 0.42)), 0.0, -(PI / 2 - SLA))
    j.apply(P('stand', aL=(0.4, 0.8, 0.5), aR=(0.5, 0.7, 0.9), lL=(0.5, 0.9), lR=(0.0, 0.0), head=(0.35, 0.0)))
    stiff(j)
    lamp(S, 0, j, 60)
    lamp(S, 1, S['simon'], 40)
    rope(S, 0, hands, A(*slope_pt(js + 1.5, 0, 0.6)))
    dust(S, [slope_pt(js - 0.5 - 2.5 * ((lt * 1.3 + rn(i, 1)) % 1), 1.4 * (rn(i, 2) - 0.5), 0.3 + 0.8 * rn(i, 3)) + (0.8,) for i in range(8)], A)
    shoot(S, A(*slope_pt(lerp(35.5, 34.6, k), 2.1, lerp(4.2, 3.8, k))), A(*slope_pt(19.0, 0.0, 0.0)), 27, fill=1.8)


def rope_line(S, k, t, lt):
    A = storm(S)
    hands = seated(S, A, strain=0.6, t=t)
    hj = hang(S, A, t, 0.8)
    rope(S, 0, A(*LIP), hj, 0.06)
    rope(S, 1, hands, A(*LIP), 0.06)
    lamp(S, 0, S['joe'], 160)
    lamp(S, 1, S['simon'], 160)
    rk = S['rook']
    rp = slope_pt(SEAT_S + 0.6, 2.6, 0.0)
    rk.place(A(*rp), look_yaw(rp, (0, -10)))
    rk.apply(P('hat', lean=0.3, head=(0.4, 0.0)))
    S['face']['rook'] = 'sad'
    S['wall']['rim'].data.energy = 0
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
    shoot(S, A(*slope_pt(lerp(27.6, 27.2, k), lerp(4.4, 3.8, k), lerp(1.0, 1.3, k))), A(*slope_pt(SEAT_S - 1.0 - ds * 0.6, 0.0, 0.9)), 29, fill=1.9)


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
    S['hat_jump'] = 0.12
    dust(S, [slope_pt(s - 1.6 - 1.6 * ((lt * 2.2 + rn(i, 1)) % 1), 1.3 * (rn(i, 2) - 0.5), 0.2 + 1.2 * ((lt * 2.2 + rn(i, 1)) % 1)) + (1.0,) for i in range(9)], A)
    shoot(S, A(*slope_pt(lerp(21.0, 19.5, k), lerp(11.0, 10.0, k), lerp(4.5, 4.0, k))), A(*slope_pt(lerp(27.5, 24.5, k), 0.0, 1.6)), 28, fill=1.7)


def knife(S, k, t, lt):
    A = storm(S)
    a, b = slope_pt(SEAT_S - 0.6, 0.0, 1.05), slope_pt(SEAT_S - 5.0, 0.0, 0.25)
    cut = 0.62
    m = tuple(a[i] + (b[i] - a[i]) * 0.3 for i in range(3))
    h = S['knife']
    saw = 0.07 * math.sin(lt * 26) if lt < cut else 0.0
    h.place(A(m[0] + 0.28 + saw, m[1] + 0.12, m[2] + 0.5 + 0.25 * sm((lt - cut) / 0.2)), (0.25, -0.5, 0.5))
    h.grip(0.92)
    if lt < cut:
        rope(S, 1, A(*a), A(*b), 0.045)
    else:
        u = lt - cut
        rope(S, 1, A(*a), A(m[0] + 0.05, m[1] + 0.25 * u, m[2] + 0.3 * u - 0.5 * u * u), 0.045)
        g = 30 * u
        rope(S, 2, A(*slope_pt(SEAT_S - 2.0 - g, 0.5 * math.sin(u * 30), 0.6 + 0.6 * math.sin(u * 22))), A(*slope_pt(SEAT_S - 6.0 - g, 0.0, 0.25)), 0.045)
        S['fray'].location = A(m[0] + 0.05, m[1] + 0.25 * u, m[2] + 0.3 * u - 0.5 * u * u)
        S['fray'].rotation_euler = (SLA + 0.5, 0, 0)
    S['lamps'][0].location = A(m[0] + 0.5, m[1] + 1.0, m[2] + 1.5)
    S['lamps'][0].data.energy = 45
    shoot(S, A(m[0] + lerp(2.0, 1.7, k), m[1] - lerp(1.9, 1.6, k), m[2] + lerp(1.0, 0.9, k)), A(m[0] + 0.1, m[1], m[2] + 0.15), 44, fill=2.2)


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
    bg.location, bg.rotation_euler = A(jp[0] + 0.35, jp[1] - 1.55, 0.42), (0, 0, 0.2)
    si = S['simon']
    sp = (jp[0] + 2.0, jp[1] - 0.5)
    si.place(A(sp[0], sp[1], 0.0), look_yaw(sp, jp))
    si.apply(dict(KNEE, aR=(1.15, 0.1, 0.6), head=(0.15, 0.0)))
    S['face']['simon'] = 'warm'
    S['mug'].location = world_of(si.hands[1], (0, -0.05, -0.1))
    rk = S['rook']
    rp = (jp[0] - 2.5, jp[1] + 0.6, 0.0)
    rk.place(A(*rp), look_yaw(rp, (jp[0], jp[1] - 3)))
    nod = sm((lt - 0.5) / 0.3)
    rk.apply(blend(P('cross', head=(0.1, -0.3)), P('hat', head=(0.25, -0.3)), nod))
    S['hat_tip'] = nod
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(-3.4, -2.8, k), lerp(-11.4, -10.6, k), lerp(2.5, 2.2, k)), A(-0.9, -3.0, 1.55), 30)


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


SHOTS3D = {f.__name__: f for f in (
    grip, leg_hang, hang_wide, slack, drop_away, rook_lip, rope_end, fall_in, ledge_land, look_up, ice_try, pebble, rook_gulp, abseil, floor_dark,
    sunbeam, climb_out, exit_hole, crawl_glacier, hop_moraine, bottle_drop, camp_night, tent_open, bags_packed, storm_face, lowering, rope_line,
    seat_hold, seat_crumble, slide, knife, two_men, rook_hatoff, rook_turn, signoff)}
STILLS = dict(men=photo_men, hang=photo_hang)
