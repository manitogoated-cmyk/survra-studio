"""Case 015 in 3D - Lincoln Hall, the Australian climber who reached the top of Everest in May 2006, collapsed on
the way down, was declared dead at dusk, and was found at sunrise sitting cross-legged on the ridge, with no hat
and no gloves, greeting the four climbers who came across him.

Built for this story only: a knife-edge snow crest above a sea of cloud with the summit pyramid behind it (seen
at sunrise, by day, in late gold light, at dusk and under stars), the summit itself with a pole of plain
streamers, a moraine camp with ridge tents and a bell post under the mountain, the inside of a radio tent, a
weatherboard house at night, a rock step with a ladder, and a study with a desk.

Everything is a generic low-poly reconstruction, not a model of the real mountain, camps, house or people. No
emblem, national flag, sign or lettering is shown anywhere in the sets. Nothing graphic is shown: frost and
bandaged fingertips only. Every other climber is an anonymous figure; nobody's likeness is attempted."""
import math

import bpy

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
SETS = dict(crest=(0, 0, 0), top=(4000, 0, 0), camp=(8000, 0, 0), radio=(12000, 0, 0), house=(16000, 0, 0), study=(20000, 0, 0),
            step=(24000, 0, 0))
AWAY = (0, 0, -3000)
HOST = {'sit_close', 'rook_gape', 'rook_bell', 'rook_off', 'hall_climb', 'top_arms', 'down_sway', 'haul', 'sherpa_leave', 'night_alone',
        'hall_talks', 'rook_drop', 'tea', 'carry_down', 'book_desk', 'rook_hatoff', 'signoff'}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN, HAIR = 'D9B79C', '9A8A72'
TEAL, FLEECE = '1F7FA0', '8E97AA'
SNOWC, SNOWL, ROCKC, ROCKD = 'C9D4E8', 'E8EEF8', '4B4F60', '34374A'
HW = 1.9                                    # half the width of the flat top of the crest
SEAT = (0.0, 0.0)                           # where he sits, facing the drop on the +X side
POST = (1.7, 0.7)                           # the bell post in the camp
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
    return (math.sin(i * 91.3458 + j * 47.7231) * 24634.6345) % 1


def seen(objs, on):
    for o in objs:
        o.hide_render = not on


def look_yaw(frm, to):
    """Yaw that turns a rig standing at frm towards to (rigs face -Y at yaw 0)."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def span(o, a, b, w):
    """Stretch a unit cylinder between two points."""
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def cloud_sea(r, z, n=70, reach=520, seed=3, hole=30):
    add('cube', 'B9C4DC', (0, 0, z - 6), scale=(3000, 3000, 1), size=1, parent=r)
    for j in range(n):
        x, y = -reach + 2 * reach * rn(j, seed), -reach + 2 * reach * rn(j, seed + 1)
        if abs(x) < hole and abs(y) < hole * 3:
            continue
        s = 28 + 46 * rn(j, seed + 2)
        add('ico_sphere', 'E4EAF6' if j % 3 else 'CBD5E8', (x, y, z + 3 * rn(j, seed + 3)), scale=(s, s * 0.8, s * 0.16), radius=1, subdivisions=1,
            parent=r)


def far_peaks(r, n=9, z0=-40, seed=9, rmin=260, rmax=460):
    for j in range(n):
        a = 2 * PI * (j + 0.35 * rn(j, seed)) / n
        d = lerp(rmin, rmax, rn(j, seed + 1))
        hh = 40 + 50 * rn(j, seed + 2)
        add('cone', '5A6078', (d * math.cos(a), d * math.sin(a), z0 + hh / 2), rot=(0, 0, rn(j, seed + 3) * 3), radius1=hh * 0.9, radius2=0, depth=hh,
            vertices=5, parent=r)
        add('cone', 'E6ECF8', (d * math.cos(a), d * math.sin(a), z0 + hh * 0.8), rot=(0, 0, rn(j, seed + 3) * 3), radius1=hh * 0.38, radius2=0,
            depth=hh * 0.42, vertices=5, parent=r)


def stars(r, n=70, rad=900, seed=21):
    out = []
    for j in range(n):
        a, e = 2 * PI * rn(j, seed), 0.08 + 1.2 * rn(j, seed + 1)
        s = 2.0 + 3.0 * rn(j, seed + 2)
        out.append(add('cube', 'F4F8FF', (rad * math.cos(a) * math.cos(e), rad * math.sin(a) * math.cos(e), rad * math.sin(e)), rot=(a, e, 0.7),
                       scale=(s, s, s), size=1, parent=r, emit=9.0))
    return out


# ---------------------------------------------------------------- the crest
def set_crest(r):
    out = {}
    L = 190
    add('cube', SNOWC, (0, 10, -0.5), scale=(HW * 2, L, 1), size=1, parent=r)
    th, half = 0.98, 60
    for s, col in ((-1, 'B4C2DC'), (1, 'D6DEEE')):                    # the two faces falling away from the crest
        add('cube', col, (s * (HW + half * math.cos(th)), 10, -half * math.sin(th) - 0.5), rot=(0, s * th, 0), scale=(half * 2, L, 1), size=1,
            parent=r)
    for j in range(34):                                               # rock ribs showing through both faces
        s = -1 if j % 2 else 1
        d = 3 + 40 * rn(j, 1)
        y = -70 + 150 * rn(j, 2)
        sc = 1.2 + 3.2 * rn(j, 3)
        add('ico_sphere', ROCKC if j % 3 else ROCKD, (s * (HW + d * math.cos(th)), y, -d * math.sin(th) - 0.2), rot=(0, s * th, rn(j, 4) * 3),
            scale=(sc * 1.6, sc, sc * 0.5), radius=1, subdivisions=1, parent=r)
    for j in range(40):                                               # wind-packed lumps along both lips of the crest
        s = -1 if j % 2 else 1
        y = -75 + 150 * (j / 40) + 2 * rn(j, 5)
        if abs(y) < 2.6 and s > 0:
            continue
        sc = 0.5 + 0.7 * rn(j, 6)
        add('ico_sphere', SNOWL, (s * (HW - 0.1 + 0.3 * rn(j, 7)), y, -0.12), scale=(sc * 0.9, sc * 1.9, sc * 0.5), radius=1, subdivisions=1, parent=r)
    for j in range(16):                                               # stones on the flat top
        x, y = -HW + 2 * HW * rn(j, 8), -40 + 80 * rn(j, 9)
        if abs(y) < 3.2 and abs(x) < 1.6:
            continue
        sc = 0.18 + 0.3 * rn(j, 10)
        add('ico_sphere', ROCKC, (x, y, 0.02), rot=(0, 0, rn(j, 11) * 3), scale=(sc * 1.3, sc, sc * 0.7), radius=1, subdivisions=1, parent=r)
    add('ico_sphere', ROCKD, (-1.25, 0.9, 0.1), rot=(0, 0, 0.5), scale=(0.75, 0.6, 0.5), radius=1, subdivisions=1, parent=r)      # the rock at his back
    add('ico_sphere', ROCKC, (-1.45, -0.7, 0.05), rot=(0, 0, 1.2), scale=(0.5, 0.4, 0.3), radius=1, subdivisions=1, parent=r)
    for j in range(12):                                               # an old fixed line on stakes along the far lip
        y = -66 + j * 12
        add('cylinder', '8A90A0', (-HW + 0.25, y, 0.4), rot=(0.1 * (rn(j, 12) - 0.5), 0.2 * (rn(j, 13) - 0.5), 0), radius=0.04, depth=1.0, vertices=5,
            parent=r)
        if j < 11:
            ln = add('cylinder', 'FF7A1A', (0, 0, 0), radius=0.5, depth=1, vertices=4, parent=r, rough=0.7)
            span(ln, (-HW + 0.25, y, 0.72), (-HW + 0.25, y + 12, 0.72 - 0.0), 0.022)
    # the summit pyramid at the far end
    add('cone', 'D2DBEC', (0, 92, -22), rot=(0, 0, 0.4), radius1=78, radius2=0, depth=96, vertices=5, parent=r)
    add('cone', ROCKC, (9, 86, -30), rot=(0, 0, 1.0), radius1=74, radius2=0, depth=84, vertices=5, parent=r)
    add('cone', SNOWL, (0, 92, 14), rot=(0, 0, 0.4), radius1=20, radius2=0, depth=24.6, vertices=5, parent=r)
    cloud_sea(r, -62)
    far_peaks(r, 10, -62)
    out['stars'] = stars(r)
    out['sunm'] = newmat('crest_sun', 'FFD9A0', 0.5, 6.0)
    out['sun'] = keep(wear(add('ico_sphere', 'FFD9A0', (760, 120, -30), radius=58, subdivisions=3, parent=r), out['sunm']))
    out['hollow'] = [add('ico_sphere', '9FB0CE', (0.15, 0, -0.1), scale=(1.0, 1.15, 0.22), radius=1, subdivisions=2, parent=r)]
    for j in range(14):                                               # boot prints leading down the crest
        out['hollow'].append(add('cube', '9FB0CE', (0.3 * (-1 if j % 2 else 1) - 0.2, -1.6 - j * 1.0, 0.012), rot=(0, 0, 0.1 * (rn(j, 14) - 0.5)),
                                 scale=(0.26, 0.5, 0.03), size=1, parent=r))
    return out


# ---------------------------------------------------------------- the summit
def set_top(r):
    out = {}
    add('ico_sphere', SNOWC, (0, 0, -3.4), scale=(13, 11, 3.5), radius=1, subdivisions=2, parent=r)
    for j in range(14):
        a = 2 * PI * j / 14
        sc = 0.6 + 0.9 * rn(j, 31)
        add('ico_sphere', SNOWL, (6.5 * math.cos(a), 5.5 * math.sin(a), -0.9), scale=(sc * 1.6, sc, sc * 0.5), radius=1, subdivisions=1, parent=r)
    add('cylinder', 'B8BCC8', (1.5, 1.4, 1.5), rot=(0.06, -0.05, 0), radius=0.05, depth=3.2, vertices=6, parent=r, rough=0.4)   # a survey pole
    add('ico_sphere', 'D9A93A', (1.42, 1.5, 3.1), radius=0.12, subdivisions=1, parent=r, rough=0.3, emit=0.5)
    out['ribbons'] = []
    for j, col in enumerate(('FF7A1A', 'E3C22A', 'F4F2EA', '2FA36B', 'D8362A', '2D6FA8', 'FF7A1A', 'F4F2EA')):   # plain streamers, no symbols
        piv = empty((1.45, 1.45, 2.9 - j * 0.14), r, (0, 0, j * 0.7))
        add('cube', col, (0.75, 0, 0), scale=(1.5, 0.02, 0.11), size=1, parent=piv, rough=0.8)
        out['ribbons'].append((piv, j * 0.7, j * 1.3))
    cloud_sea(r, -90, 80, 600, 41, 0)
    far_peaks(r, 12, -90, 51, 200, 480)
    return out


# ---------------------------------------------------------------- the camp under the mountain
def ridge_tent(r, x, y, col, yaw=0.0, s=1.0):
    t = empty((x, y, 0), r, (0, 0, yaw))
    add('cylinder', col, (0, 0, 0.55 * s), rot=(PI / 2, -PI / 2, 0), scale=(0.62, 1.0, 1.0), radius=1.9 * s, depth=4.2 * s, vertices=3, parent=t, rough=0.75)
    add('cube', '1B1E2A', (0, -2.12 * s, 0.75 * s), scale=(0.9 * s, 0.04, 1.3 * s), size=1, parent=t)
    for sx in (-1, 1):
        add('cylinder', 'E8E4D8', (sx * 2.3 * s, 0, 0.35 * s), rot=(0, sx * 0.9, 0), radius=0.02, depth=1.6 * s, vertices=4, parent=t)
    return t


def set_camp(r):
    out = {}
    add('cube', '77726C', (0, 0, -0.5), scale=(1600, 1600, 1), size=1, parent=r)
    for j in range(70):                                               # moraine rubble and patches of old snow
        x, y = -60 + 120 * rn(j, 61), -30 + 110 * rn(j, 62)
        if abs(x - 0.5) < 3.4 and -4 < y < 9:
            continue
        s = 0.3 + 1.1 * rn(j, 63)
        if j % 4 == 0:
            add('ico_sphere', 'DDE4F0', (x, y, -0.1), scale=(s * 4, s * 2.6, 0.3), radius=1, subdivisions=1, parent=r)
        else:
            add('ico_sphere', '5C5852' if j % 3 else '8C867E', (x, y, 0.05), rot=(0, 0, rn(j, 64) * 3), scale=(s * 1.4, s, s * 0.6), radius=1,
                subdivisions=1, parent=r)
    for x, y, col, yaw, s in ((9, 15, 'E3C22A', 0.5, 1.5), (-10, 19, '2D6FA8', -0.4, 1.4), (15, 30, 'D8362A', 0.2, 1.5), (-18, 33, 'E3C22A', -0.2, 1.6),
                              (-3, 40, 'F4F2EA', 0.1, 2.2)):
        ridge_tent(r, x, y, col, yaw, s)
    for j, (x, y) in enumerate(((5.2, 5.5), (6.1, 6.3), (5.5, 7.2), (-5.5, 6.0))):                    # fuel drums and crates
        add('cylinder', '3E6A8A' if j % 2 else 'A8472E', (x, y, 0.6), radius=0.45, depth=1.2, vertices=8, parent=r, rough=0.5)
    for j, (x, y, s) in enumerate(((-4.6, 4.6, 0.9), (-5.6, 4.9, 0.7), (-4.9, 5.0, 0.6))):
        add('cube', 'A8865A', (x, y, s / 2 + (0.9 if j == 2 else 0)), rot=(0, 0, 0.2 * j), scale=(s * 1.3, s, s), size=1, parent=r)
    for j, (dx, dy, s) in enumerate(((0, 0, 0.7), (0.5, 0.35, 0.45), (-0.45, 0.3, 0.4), (0.1, -0.45, 0.4))):     # stones round the foot of the post
        add('ico_sphere', '5C5852' if j % 2 else '8C867E', (POST[0] + dx, POST[1] + dy, 0.15), rot=(0, 0, j), scale=(s, s * 0.8, s * 0.6), radius=1,
            subdivisions=1, parent=r)
    add('cylinder', '6A4A30', (POST[0], POST[1], 1.75), rot=(0.03, -0.04, 0), radius=0.09, depth=3.5, vertices=6, parent=r)
    add('cylinder', '6A4A30', (POST[0] - 0.5, POST[1], 3.3), rot=(0, PI / 2, 0), radius=0.06, depth=1.5, vertices=6, parent=r)
    add('cylinder', 'E8E4D8', (POST[0] - 1.05, POST[1], 3.1), radius=0.015, depth=0.4, vertices=4, parent=r)
    # the mountain
    add('cone', '454B5E', (0, 470, 150), rot=(0, 0, 0.62), radius1=300, radius2=0, depth=330, vertices=5, parent=r)
    add('cone', 'DDE5F4', (0, 470, 262), rot=(0, 0, 0.62), radius1=98, radius2=0, depth=108, vertices=5, parent=r)
    add('cone', 'C7D2E8', (-18, 452, 180), rot=(0, 0, 1.3), radius1=205, radius2=0, depth=226, vertices=4, parent=r)
    add('cone', '555C72', (-290, 520, 80), rot=(0, 0, 0.2), radius1=210, radius2=0, depth=190, vertices=5, parent=r)
    add('cone', 'DDE5F4', (-290, 520, 150), rot=(0, 0, 0.2), radius1=62, radius2=0, depth=56, vertices=5, parent=r)
    add('cone', '555C72', (300, 540, 70), rot=(0, 0, 0.9), radius1=230, radius2=0, depth=170, vertices=5, parent=r)
    add('cone', 'DDE5F4', (300, 540, 132), rot=(0, 0, 0.9), radius1=66, radius2=0, depth=48, vertices=5, parent=r)
    add('cube', 'CBD6EA', (0, 250, -4), rot=(0.06, 0, 0), scale=(700, 260, 10), size=1, parent=r)                 # the glacier running up to it
    out['plume'] = [keep(add('ico_sphere', 'F4F8FF', (0, 470, 318), scale=(1, 0.6, 0.5), radius=9, subdivisions=1, parent=r, alpha=0.7, emit=0.3))
                    for _ in range(7)]
    return out


# ---------------------------------------------------------------- the radio tent
def set_radio(r):
    out = {}
    add('cube', '5E5A54', (0, 0, -0.5), scale=(14, 14, 1), size=1, parent=r)
    out['fabm'] = newmat('radio_fab', '7E8A4E', 0.9, 0.15)
    wear(add('cube', '7E8A4E', (0, 3.2, 2.4), scale=(12, 0.1, 6), size=1, parent=r), out['fabm'])
    for s in (-1, 1):
        wear(add('cube', '7E8A4E', (s * 3.6, 0, 2.6), rot=(0, s * 0.5, 0), scale=(0.1, 9, 6.6), size=1, parent=r), out['fabm'])
        add('cylinder', 'B8BCC8', (s * 2.6, 3.0, 2.4), radius=0.05, depth=5, vertices=5, parent=r)
    add('cube', '8A6A44', (0, 1.6, 1.3), scale=(4.4, 1.8, 0.14), size=1, parent=r)                               # a trestle table
    for sx in (-1, 1):
        add('cube', '6A4E30', (sx * 1.9, 1.6, 0.62), scale=(0.14, 1.5, 1.24), size=1, parent=r)
    add('cube', '3A4252', (-0.6, 2.0, 1.85), scale=(1.5, 0.8, 0.95), size=1, parent=r, rough=0.5)                  # the radio set
    add('cube', '1B1E2A', (-0.6, 1.585, 1.9), scale=(1.3, 0.03, 0.7), size=1, parent=r)
    out['dials'] = []
    for j in range(5):
        out['dials'].append(add('cylinder', 'FF7A1A' if j % 2 else '3EC46A', (-1.1 + j * 0.25, 1.56, 2.08), rot=(PI / 2, 0, 0), radius=0.05, depth=0.03,
                                vertices=6, parent=r, emit=4.0))
    out['needle'] = add('cube', 'F4F2EA', (-0.6, 1.555, 1.72), scale=(0.03, 0.02, 0.24), size=1, parent=r, emit=2.0)
    add('cylinder', 'B8BCC8', (-1.2, 2.2, 3.2), rot=(0, -0.1, 0), radius=0.02, depth=1.8, vertices=4, parent=r)
    add('cube', 'D8D2C0', (1.2, 1.6, 1.385), rot=(0, 0, 0.2), scale=(1.3, 0.95, 0.02), size=1, parent=r)             # a blank chart
    add('cylinder', 'E8E4D8', (1.9, 2.1, 1.55), radius=0.14, depth=0.34, vertices=8, parent=r)                     # a mug
    out['lampm'] = newmat('radio_lamp', 'FFD08A', 0.4, 7.0)
    wear(add('cylinder', 'FFD08A', (0.9, 2.4, 3.9), radius=0.2, depth=0.42, vertices=8, parent=r), out['lampm'])     # a hanging lantern
    add('cylinder', '3A3F4C', (0.9, 2.4, 4.6), radius=0.012, depth=1.1, vertices=4, parent=r)
    out['lamp'] = light((0.9, 1.9, 3.7), 0, 'FFC27A', kind='POINT', parent=r)
    out['door'] = light((0, -5, 3), 0, '6A78C8', 4.0, parent=r)
    return out


# ---------------------------------------------------------------- the house at night
def set_house(r):
    out = {}
    add('cube', '1E2A26', (0, 0, -0.5), scale=(400, 400, 1), size=1, parent=r)
    add('cube', '8A8478', (0, -6, 0.02), scale=(2.0, 16, 0.04), size=1, parent=r)                                  # the path
    add('cube', 'C9C2AE', (0, 7, 2.3), scale=(13, 7, 4.6), size=1, parent=r)                                       # weatherboard walls
    for j in range(7):
        add('cube', 'A8A290', (0, 3.47, 0.5 + j * 0.62), scale=(13.02, 0.04, 0.05), size=1, parent=r)
    add('cylinder', '7A3A30', (0, 7, 5.9), rot=(0, -PI / 2, 0), scale=(0.52, 1.0, 1.0), radius=4.9, depth=14.4, vertices=3, parent=r, rough=0.5)   # the roof
    add('cube', '7A3A30', (0, 2.2, 4.15), rot=(0.16, 0, 0), scale=(13.6, 3.2, 0.12), size=1, parent=r, rough=0.5)        # the verandah roof
    for x in (-6.2, -2.0, 2.0, 6.2):
        add('cube', 'E8E4D8', (x, 0.9, 1.95), scale=(0.2, 0.2, 3.9), size=1, parent=r)
    add('cube', 'B8B2A0', (0, 2.1, 0.12), scale=(13.4, 3.0, 0.24), size=1, parent=r)
    add('cube', '4A2E22', (-0.2, 3.46, 1.75), scale=(1.5, 0.08, 3.3), size=1, parent=r)                             # the front door
    out['winm'] = newmat('house_win', '1A2238', 0.3, 0.0)
    out['win'] = []
    for x in (-4.2, 3.9):
        add('cube', 'E8E4D8', (x, 3.45, 2.3), scale=(2.7, 0.08, 2.3), size=1, parent=r)
        out['win'].append(wear(add('cube', '1A2238', (x, 3.4, 2.3), scale=(2.4, 0.06, 2.0), size=1, parent=r), out['winm']))
        add('cube', 'E8E4D8', (x, 3.36, 2.3), scale=(0.08, 0.04, 2.0), size=1, parent=r)
        add('cube', 'E8E4D8', (x, 3.36, 2.3), scale=(2.4, 0.04, 0.08), size=1, parent=r)
    wear(out['win'][0], newmat('house_win_dark', '1A2238', 0.3, 0.0))
    out['glow'] = light((3.9, 1.6, 2.3), 0, 'FFC27A', kind='POINT', parent=r)
    add('cylinder', 'B4AC9C', (-10.5, -1, 3.5), rot=(0.05, 0.12, 0), radius=0.4, depth=7.4, vertices=7, parent=r)            # a gum tree
    add('cylinder', 'B4AC9C', (-9.6, -1, 6.6), rot=(0, 0.8, 0), radius=0.2, depth=3.4, vertices=6, parent=r)
    for j in range(9):
        add('ico_sphere', '2E4638' if j % 2 else '3A5644', (-10.5 + 4.4 * (rn(j, 71) - 0.4), -1 + 3 * (rn(j, 72) - 0.5), 7.6 + 2.6 * rn(j, 73)),
            scale=(1.9, 1.6, 1.0), radius=1 + 0.5 * rn(j, 74), subdivisions=1, parent=r)
    for j in range(22):                                                                                          # a low picket fence
        x = -13 + j * 1.25
        if abs(x) < 1.6:
            continue
        add('cube', 'D8D2C0', (x, -5, 0.6), scale=(0.22, 0.08, 1.2), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', 'D8D2C0', (sx * 7.6, -5, 0.75), scale=(12, 0.06, 0.1), size=1, parent=r)
    add('cube', '8A3A2E', (2.6, -5.4, 1.5), scale=(0.5, 0.7, 0.45), size=1, parent=r)                               # a letterbox
    add('cube', '6A4A30', (2.6, -5.4, 0.65), scale=(0.1, 0.1, 1.3), size=1, parent=r)
    add('ico_sphere', 'E8EEF8', (-190, 420, 250), radius=24, subdivisions=2, parent=r, emit=5.0)                   # the moon
    out['stars'] = stars(r, 60, 700, 81)
    return out


# ---------------------------------------------------------------- the rock step
def set_step(r):
    out = {}
    add('cube', ROCKD, (0, 4, 8), scale=(60, 8, 17), size=1, parent=r)
    for j in range(40):                                                                                          # facets on the rock face
        x, z = -22 + 44 * rn(j, 91), 0.5 + 15 * rn(j, 92)
        if abs(x) < 1.3:
            continue
        s = 0.8 + 1.6 * rn(j, 93)
        add('ico_sphere', ROCKC if j % 3 else '5E6378', (x, 0.1, z), rot=(rn(j, 94), 0, rn(j, 95) * 3), scale=(s * 1.5, 0.7, s), radius=1, subdivisions=1,
            parent=r)
    add('cube', SNOWC, (0, -6, -0.5), scale=(60, 12, 1), size=1, parent=r)
    add('cube', 'B4C2DC', (0, -22, -9.6), rot=(-0.85, 0, 0), scale=(60, 30, 1), size=1, parent=r)
    add('cube', SNOWL, (0, 3.6, 16.7), scale=(60, 9, 0.9), size=1, parent=r)
    for j in range(12):
        x = -24 + 48 * rn(j, 96)
        add('ico_sphere', SNOWL, (x, -0.6, 16.4), scale=(2.2, 1.1, 0.7), radius=1, subdivisions=1, parent=r)
        add('ico_sphere', SNOWL, (x * 0.9, -1.0 - 3 * rn(j, 97), 0.0), scale=(2.0, 1.4, 0.45), radius=1, subdivisions=1, parent=r)
    for sx in (-1, 1):                                                                                           # the ladder
        rail = add('cylinder', 'C8CCD8', (0, 0, 0), radius=0.5, depth=1, vertices=5, parent=r, rough=0.3)
        span(rail, (sx * 0.5, -2.2, 0.0), (sx * 0.5, -0.35, 16.6), 0.06)
    for j in range(20):
        u = (j + 0.5) / 20
        add('cylinder', 'C8CCD8', (0, lerp(-2.2, -0.35, u), 16.6 * u), rot=(0, PI / 2, 0), radius=0.045, depth=1.0, vertices=5, parent=r, rough=0.3)
    ln = add('cylinder', 'FF7A1A', (0, 0, 0), radius=0.5, depth=1, vertices=4, parent=r, rough=0.7)                  # a fixed line beside it
    span(ln, (1.2, -1.2, 0.2), (1.5, -0.2, 16.9), 0.03)
    cloud_sea(r, -70, 60, 520, 101, 0)
    far_peaks(r, 8, -70, 111, 240, 440)
    return out


# ---------------------------------------------------------------- the study
def set_study(r):
    out = {}
    add('cube', '6E5038', (0, 0, -0.5), scale=(16, 14, 1), size=1, parent=r)
    add('cube', 'A9B7A6', (0, 4.2, 4), scale=(16, 0.2, 9), size=1, parent=r)                                       # the back wall
    add('cube', 'A9B7A6', (-6.6, 0, 4), scale=(0.2, 14, 9), size=1, parent=r)
    add('cube', '8A9A8A', (0, 4.08, 0.25), scale=(16, 0.06, 0.5), size=1, parent=r)
    out['skym'] = newmat('study_sky', 'A8D4F4', 0.4, 2.6)
    add('cube', 'F2EEE2', (1.6, 4.07, 4.2), scale=(4.6, 0.1, 3.8), size=1, parent=r)                                # a window on a bright day
    wear(add('cube', 'A8D4F4', (1.6, 4.02, 4.2), scale=(4.2, 0.08, 3.4), size=1, parent=r), out['skym'])
    add('cube', 'F2EEE2', (1.6, 3.96, 4.2), scale=(0.1, 0.05, 3.4), size=1, parent=r)
    add('cube', 'F2EEE2', (1.6, 3.96, 4.2), scale=(4.2, 0.05, 0.1), size=1, parent=r)
    for j in range(5):                                                                                           # gum leaves outside
        add('ico_sphere', '4E7A5A', (0.2 + j * 0.75, 3.98, 5.2 + 0.4 * math.sin(j * 2.1)), scale=(0.7, 0.03, 0.45), radius=1, subdivisions=1, parent=r,
            emit=0.6)
    add('cube', '5A4030', (-4.4, 3.7, 3.0), scale=(3.2, 0.8, 6.0), size=1, parent=r)                                # a bookcase of plain spines
    for j in range(24):
        col = ('8A3A2E', '2D6FA8', 'D8D2C0', '3E6E5A', 'E3C22A', '6A4E8A')[j % 6]
        add('cube', col, (-5.7 + (j % 8) * 0.34, 3.26, 1.2 + (j // 8) * 1.75), scale=(0.26, 0.2, 1.1 + 0.25 * rn(j, 121)), size=1, parent=r)
    add('cube', '7A5A3A', (0, -1.1, 1.5), scale=(5.4, 1.9, 0.16), size=1, parent=r)                                 # the desk
    add('cube', '5E442C', (0, -1.95, 0.75), scale=(5.2, 0.1, 1.4), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '5E442C', (sx * 2.5, -1.1, 0.72), scale=(0.16, 1.7, 1.44), size=1, parent=r)
    add('cube', '5E442C', (0, 0.75, 1.3), scale=(1.5, 0.16, 2.6), size=1, parent=r)                                 # the back of his chair
    out['pages'] = []
    for j in range(2):                                                                                           # an open notebook
        out['pages'].append(add('cube', 'F4F0E2', (-0.36 + j * 0.72, -1.1, 1.6), rot=(0, (0.5 - j) * 0.16, 0), scale=(0.7, 0.95, 0.03), size=1, parent=r))
    for j in range(6):
        add('cube', '3A3F4C', (-0.36, -0.82 - j * 0.1, 1.625), scale=(0.5, 0.018, 0.005), size=1, parent=r)
    add('cube', 'F4F0E2', (-1.75, -1.0, 1.66), rot=(0, 0, 0.15), scale=(0.9, 1.2, 0.16), size=1, parent=r)             # a stack of paper
    add('cylinder', 'E8E4D8', (1.7, -0.6, 1.76), radius=0.17, depth=0.36, vertices=8, parent=r)                    # a mug
    add('cylinder', '3A3F4C', (2.2, -0.5, 2.3), radius=0.04, depth=1.5, vertices=5, parent=r)                      # a desk lamp
    out['shadem'] = newmat('study_shade', 'FFD08A', 0.5, 2.5)
    wear(add('cone', 'FFD08A', (2.0, -0.7, 3.05), rot=(0.3, 0.3, 0), radius1=0.42, radius2=0.14, depth=0.42, vertices=8, parent=r), out['shadem'])
    out['pen'] = keep(add('cylinder', 'FF7A1A', (0, 0, -40), radius=0.03, depth=0.5, vertices=5, parent=r, rough=0.4))
    out['key'] = light((1.6, 2.6, 4.4), 0, 'DCEBFF', 3.4, parent=r)
    out['warm'] = light((2.0, -1.0, 2.8), 0, 'FFC27A', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- heads
def climber(skin, suit, hair=HAIR, hood=True):
    """A climber's head. Hood, goggles, breathing mask and frost are separate pieces that shots switch on and off."""
    def fn(head):
        add('ico_sphere', skin, (0, 0, 0.02), scale=(0.9, 0.98, 1.08), radius=0.29, subdivisions=1, parent=head)
        hair_ = [add('ico_sphere', hair, (0, 0.06, 0.11), scale=(0.94, 0.98, 0.96), radius=0.3, subdivisions=1, parent=head)]
        hd = []
        if hood:
            hd.append(add('ico_sphere', suit, (0, 0.08, 0.08), scale=(1.02, 1.0, 1.1), radius=0.34, subdivisions=1, parent=head))
            hd.append(add('cone', suit, (0, 0.1, 0.42), radius1=0.2, radius2=0.0, depth=0.22, vertices=5, parent=head))
        eyes, brows = [], []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.258, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '1A222E', (s * 0.105, -0.276, 0.035), scale=(0.042, 0.02, 0.046), size=1, parent=head)
            brows.append(add('cube', hair, (s * 0.105, -0.266, 0.125), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.026), size=1, parent=head))
        add('cube', 'B98E72', (0, -0.28, -0.04), scale=(0.05, 0.05, 0.08), size=1, parent=head)
        jaw = empty((0, -0.2, -0.13), head)
        add('cube', '6A2A2E', (0, -0.068, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
        gog = [add('cube', '10141C', (0, -0.27, 0.05), scale=(0.44, 0.08, 0.15), size=1, parent=head, rough=0.15),
               add('cube', 'FFB000', (0, -0.312, 0.05), scale=(0.37, 0.02, 0.1), size=1, parent=head, rough=0.2, emit=0.7)]
        mask = [add('cone', '9AA0B0', (0, -0.32, -0.1), rot=(PI / 2, 0, 0), radius1=0.13, radius2=0.07, depth=0.16, vertices=6, parent=head, rough=0.5),
                add('cylinder', '3A3F4C', (0.08, -0.26, -0.27), rot=(0.4, 0, 0), radius=0.03, depth=0.3, vertices=5, parent=head)]
        frost = []
        for x, y, z, sc in ((-0.14, -0.2, 0.25, 0.07), (0.1, -0.22, 0.27, 0.06), (0.0, -0.1, 0.38, 0.09), (-0.22, -0.05, 0.3, 0.07), (0.23, -0.02, 0.28, 0.08),
                            (0.0, -0.285, -0.04, 0.05), (-0.105, -0.275, 0.135, 0.04), (0.105, -0.275, 0.135, 0.04), (0.14, 0.12, 0.36, 0.07),
                            (-0.1, -0.24, -0.15, 0.05), (0.12, -0.24, -0.16, 0.05)):
            frost.append(add('ico_sphere', 'F0F5FC', (x, y, z), scale=(1, 0.7, 0.6), radius=sc * 0.62, subdivisions=1, parent=head, rough=0.25, emit=0.15))
        for g in (gog, mask, frost):
            seen(g, False)
        return dict(jaw=jaw, eyes=eyes, brows=brows, gog=gog, mask=mask, frost=frost, hood=hd, hair=hair_)
    return fn


def pack(rig, col='2A2F3A', bottle=True):
    add('cube', col, (0, 0.3, 0.6), scale=(0.56, 0.3, 0.8), size=1, parent=rig.body)
    if bottle:
        add('cylinder', 'FF7A1A', (0.12, 0.5, 0.72), radius=0.1, depth=0.9, vertices=6, parent=rig.body, rough=0.4)


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = dict(colls={})
    for name, fn in (('crest', set_crest), ('top', set_top), ('camp', set_camp), ('radio', set_radio), ('house', set_house), ('study', set_study),
                     ('step', set_step)):
        S['colls'][name], S[name] = stage(name, fn)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['hall'] = hl = K.Rig(dict(top=TEAL, pants=TEAL, hand='20242C', boot='E3C22A'), climber(SKIN, TEAL))
    pack(hl)
    # the same man as he was found: arms out of the down suit, which hangs round his waist; thin top, bare head, bare hands
    S['found'] = fd = K.Rig(dict(top=FLEECE, pants=TEAL, hand=SKIN, boot='E3C22A'), climber(SKIN, TEAL, hood=False))
    add('torus', TEAL, (0, 0, 0.12), scale=(1.0, 1.0, 1.7), major_radius=0.36, minor_radius=0.13, major_segments=8, minor_segments=4, parent=fd.body)
    add('cube', TEAL, (0, 0.34, 0.0), rot=(0.5, 0, 0), scale=(0.7, 0.16, 0.6), size=1, parent=fd.body)
    S['hat'] = add('ico_sphere', 'FF7A1A', (0, 0.02, 0.16), scale=(1.02, 1.04, 0.8), radius=0.31, subdivisions=1, parent=fd.head)   # a borrowed hat
    S['hat'].hide_render = True
    for nm, col, boot in (('s1', 'E08A2A', '22262E'), ('s2', '7A4EA8', 'D8DCE4'), ('m1', 'D8362A', '22262E'), ('m2', 'E3C22A', '8A2A2A'),
                          ('m3', '2FA36B', 'D8DCE4'), ('m4', 'B8C8E8', '3A3F4C')):
        S[nm] = rg = K.Rig(dict(top=col, pants=col, hand='20242C', boot=boot), climber('C99A78' if nm in ('s1', 's2', 'm4') else 'DDB494', col,
                                                                                         hair='2A2422'))
        pack(rg)
    S['home'] = hm = K.Rig(dict(top='3E6E5A', pants='3A3F4C', hand='F4F2EA', boot='2A2420'), climber(SKIN, '3E6E5A', hood=False))
    S['humans'] = ['hall', 'found', 's1', 's2', 'm1', 'm2', 'm3', 'm4', 'home']
    S['cast'] = [S['rook']] + [S[n] for n in S['humans']]
    S['fea'] = [keep(add('cone', '2F2B4D', AWAY, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(3)]
    S['bell'] = bl = keep(empty(AWAY))                                                                          # the shiny thing: a small brass bell
    add('cone', 'E0B040', (0, 0, -0.12), radius1=0.24, radius2=0.1, depth=0.36, vertices=8, parent=bl, rough=0.18, emit=1.6)
    add('ico_sphere', 'E0B040', (0, 0, 0.08), radius=0.1, subdivisions=1, parent=bl, rough=0.18, emit=1.6)
    add('ico_sphere', '6A4A30', (0, 0, -0.32), radius=0.06, subdivisions=1, parent=bl)
    S['cup'] = keep(add('cylinder', 'FF7A1A', AWAY, radius=0.09, depth=0.2, vertices=7, rough=0.4, emit=0.4))
    S['book'] = bk = keep(empty(AWAY))
    add('cube', '2D6FA8', (0, 0, 0), scale=(0.62, 0.1, 0.84), size=1, parent=bk)
    add('cube', 'F4F0E2', (0, 0.0, 0.0), scale=(0.56, 0.07, 0.86), size=1, parent=bk)
    S['walkie'] = rd = keep(empty(AWAY))                                                                         # a hand radio
    add('cube', '22262E', (0, 0, 0), scale=(0.2, 0.1, 0.42), size=1, parent=rd, rough=0.4)
    add('cylinder', '22262E', (0.06, 0, 0.36), radius=0.015, depth=0.34, vertices=4, parent=rd)
    add('cube', '3EC46A', (0, -0.055, 0.1), scale=(0.1, 0.01, 0.06), size=1, parent=rd, emit=5.0)
    S['handset'] = hs = K.Hand('B98E72', '2D3A5A', 1.0)
    add('cube', '22262E', (0, -0.1, -0.2), scale=(0.3, 0.72, 0.2), size=1, parent=hs.root, rough=0.4)
    add('cylinder', '22262E', (0.1, 0.38, -0.2), rot=(PI / 2, 0, 0), radius=0.02, depth=0.5, vertices=4, parent=hs.root)
    add('cube', '3EC46A', (0, -0.3, -0.31), scale=(0.14, 0.1, 0.02), size=1, parent=hs.root, emit=5.0)
    keep(hs.root)
    S['puff'] = [keep(add('ico_sphere', 'F4F8FF', AWAY, radius=0.11, subdivisions=1, alpha=0.5, emit=0.5)) for _ in range(3)]
    S['line'] = keep(add('cylinder', 'FF7A1A', AWAY, radius=0.5, depth=1, vertices=4, rough=0.7))
    S['lamps'] = [light(AWAY, 0, 'FFF0C8', kind='POINT') for _ in range(4)]
    S['beams'] = [keep(add('ico_sphere', 'FFF4D0', AWAY, radius=0.09, subdivisions=1, emit=14.0)) for _ in range(4)]
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


def mixc(a, b, k):
    k = max(0.0, min(1.0, k))
    return ''.join('%02X' % int(round(lerp(int(a[i:i + 2], 16), int(b[i:i + 2], 16), k))) for i in (0, 2, 4))


def mix3(a, b, c, k):
    return mixc(a, b, k * 2) if k < 0.5 else mixc(b, c, k * 2 - 1)


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
        seen(x['gog'], who in ('s1', 's2', 'm1', 'm2', 'm3', 'm4'))
        seen(x['mask'], False)
        seen(x['frost'], who == 'found')
    S['hat'].hide_render = True
    seen(S['crest']['stars'], False)
    seen(S['crest']['hollow'], False)
    S['crest']['sun'].hide_render = False
    paint(S['crest']['sunm'], 'FFD9A0', 6.0)
    R = S['radio']
    R['lamp'].data.energy = 0
    R['door'].data.energy = 0
    Hs = S['house']
    paint(Hs['winm'], '1A2238', 0.0)
    Hs['glow'].data.energy = 0
    St = S['study']
    St['key'].data.energy = 0
    St['warm'].data.energy = 0
    for l in S['lamps']:
        l.location = AWAY
        l.data.energy = 0
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['face'] = {w: 'calm' for w in ['rook'] + S['humans']}
    S['jaw'] = {w: 0.0 for w in S['humans']}
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
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
    r['hat'].location = (0.0, lerp(0.0, -0.5, off), lerp(0.27 + (0.2 if e == 'shocked' else 0.0) + tip * 0.1, -0.92, off))
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
            br.location.z = 0.125 + (0.03 if f == 'wide' else -0.012 if f in ('sad', 'tired', 'squint') else 0.0)
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


def crest(S, mode='sunrise', k=1.0, sun_at=None):
    """The crest in one of its lights. The sun comes up on the +X side and goes down on the -X side."""
    C = S['crest']
    if mode == 'sunrise':                                             # k: 0 first glow .. 1 sun clear of the horizon
        A = env(S, 'crest', mix3('4A4A8A', 'E8806A', 'F4A468', k), sun=lerp(0.5, 3.0, k), sunc=mixc('FF8A60', 'FFC090', k), sdir=(0.9, 0.12, lerp(0.1, 0.34, k)),
                fk=lerp(1.5, 2.2, k), skyk=lerp(0.7, 1.0, k))
        sx, sy = sun_at or (760, 120)
        C['sun'].location = (sx, sy, lerp(-118, -8, k))
        paint(C['sunm'], mixc('FF7A40', 'FFE2A8', k), lerp(4, 9, k))
    elif mode == 'day':
        A = env(S, 'crest', '6FA6E4', sun=3.2, sunc='FFF4E0', sdir=(0.35, -0.5, 0.8), fk=2.4, skyk=1.0)
        C['sun'].hide_render = True
    elif mode == 'gold':                                              # k: 0 late afternoon .. 1 dusk
        A = env(S, 'crest', mix3('F0B060', 'E0705A', '4A3470', k), sun=lerp(3.0, 0.5, k), sunc=mixc('FFC070', 'FF6A50', k), sdir=(-0.92, -0.1, lerp(0.3, 0.03, k)),
                fk=lerp(2.0, 1.3, k), skyk=lerp(0.95, 0.6, k))
        sx, sy = sun_at or (-760, -60)
        C['sun'].location = (sx, sy, lerp(70, -124, k))
        paint(C['sunm'], mixc('FFE2A8', 'FF5A30', k), lerp(9, 5, k))
    else:                                                             # night
        A = env(S, 'crest', '0A1030', sun=0.5, sunc='9DB8FF', sdir=(-0.3, 0.4, 0.8), fk=1.5, skyk=1.0)
        C['sun'].hide_render = True
        seen(C['stars'], True)
    return A


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
DOWN = P('stand', aR=(0.15, 0.45, 0.3), aL=(0.2, 0.5, 0.5, 0.3), lL=(0.06, 0.08), lR=(-0.04, 0.14), head=(-0.05, 0.1))
KNEE = P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.4, aL=(0.6, 0.1, 0.7), aR=(1.0, 0.0, 0.5), head=(0.3, 0.0))
TRUDGE = dict(lean=0.3, head=(0.25, 0.0))


def cross_sit(rig, lean=0.1, head=(0.0, 0.0), aL=(0.62, 0.3, 0.75, 0.25), aR=(0.62, 0.3, 0.75, 0.25)):
    """Sitting cross-legged on the snow."""
    rig.apply(P('stand', lift=-0.8, lean=lean, head=head, aL=aL, aR=aR))
    for i, s in enumerate((-1, 1)):
        rig.hp[i].rotation_euler = (-1.42, 0, s * 0.78)
        rig.kn[i].rotation_euler = (0.2, s * 1.75, 0)


def seated(S, A, turn=0.0, nod=0.05, lean=0.1, face='tired', aL=None, aR=None, hat=False):
    """Hall as he was found, on the lip of the crest, facing the drop (+X)."""
    f = S['found']
    f.place(A(SEAT[0] + 0.55, SEAT[1], 0), PI / 2)
    kw = {}
    if aL:
        kw['aL'] = aL
    if aR:
        kw['aR'] = aR
    cross_sit(f, lean, (nod, turn), **kw)
    S['face']['found'] = face
    S['hat'].hide_render = not hat
    return f


def lying(S, A, who, pos, yaw=0.0, face='shut', pose=None):
    rig = S[who]
    rig.place(A(pos[0], pos[1], 0.36), yaw, -PI / 2)
    rig.apply(pose or DOWN)
    S['face'][who] = face
    return rig


def lamp(S, i, rig, e=60.0):
    """A head torch: a bright bead on the forehead and a small light in front of it."""
    m = rig.head.matrix_world
    bpy.context.view_layer.update()
    m = rig.head.matrix_world
    p = m @ __import__('mathutils').Vector((0, -0.42, 0.22))
    S['beams'][i].location = p
    q = m @ __import__('mathutils').Vector((0, -1.3, 0.1))
    S['lamps'][i].location = q
    S['lamps'][i].data.energy = e


def gear(S, who, gog=True, mask=True):
    seen(S[who].extra['gog'], gog)
    seen(S[who].extra['mask'], mask)


# ---------------------------------------------------------------- the hook: sunrise on the crest
def sun_ridge(S, k, t, lt):
    A = crest(S, 'sunrise', 0.5 + 0.5 * sm(k), sun_at=(690, 250))
    seated(S, A)
    shoot(S, A(lerp(-12.5, -9.5, k), lerp(-6.0, -4.6, k), lerp(0.8, 1.2, k)), A(0.3, 0.4, lerp(2.4, 1.9, k)), 34, fill=0.5, fcol='FFC8A0')


def sit_wide(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A)
    shoot(S, A(lerp(4.0, 3.0, k), lerp(-11.5, -9.0, k), lerp(5.4, 4.2, k)), A(0.2, 2.5, 1.9), 30, fcol='FFD8B8')


def sit_close(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=0.12 * math.sin(lt * 2.2), nod=0.1)
    y = lerp(6.2, 2.3, sm(lt / 0.9))
    rp = (-0.5, y, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.5, 0.0)))
    peer = sm((lt - 0.9) / 0.3)
    S['rook'].apply(blend(walk(lt, 1.8), P('stand', lean=0.42, head=(0.1, 0.25), aL=(0.3, 0.2, 0.4), aR=(0.9, 0.3, 1.9, 0.6)), peer))
    S['face']['rook'] = 'deadpan'
    shoot(S, A(lerp(7.4, 6.2, k), lerp(-4.2, -3.3, k), lerp(1.7, 1.5, k)), A(0.25, 0.9, 1.55), 36, fcol='FFD8B8')


def bare_head(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=lerp(-0.25, 0.1, k), nod=0.08)
    shoot(S, A(lerp(3.3, 2.9, k), lerp(-1.6, -1.1, k), lerp(1.75, 1.95, k)), A(0.62, 0.0, 1.78), 62, fcol='FFD8B8')


def bare_hands(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    lift = 0.35 * sm(lt / 0.4)
    seated(S, A, nod=0.4, aL=(0.62 + lift, 0.3, 0.75 + lift, 0.25), aR=(0.62 + lift * 0.6, 0.3, 0.75 + lift * 0.6, 0.25))
    shoot(S, A(lerp(4.4, 4.0, k), lerp(-0.9, 0.5, k), lerp(1.9, 1.7, k)), A(1.0, 0.0, 0.8), 44, fcol='FFD8B8')


def rook_gape(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=0.5, nod=0.0, face='calm')
    rp = (-0.5, 2.3, 0.0)
    pop = sm(lt / 0.14)
    S['rook'].place(A(*rp), look_yaw(rp, (4.0, -1.0)))
    S['rook'].apply(blend(P('stand', lean=0.42, head=(0.1, 0.25)), P('stand', **STARTLE), pop))
    S['face']['rook'] = 'shocked' if pop > 0.3 else 'deadpan'
    feather(S, A(rp[0] + 0.3, rp[1] - 0.3, 3.3), lt, 0.08)
    shoot(S, A(lerp(3.4, 2.9, k), lerp(0.6, 0.9, k), 0.9), A(-0.4, 2.2, 2.6), 30, fill=1.6, fcol='FFD8B8')


# ---------------------------------------------------------------- the camp (Rook's start and sign-off)
def camp(S, dawn=False):
    if dawn:
        A = env(S, 'camp', 'E8A888', sun=2.2, sunc='FFC098', sdir=(0.8, -0.4, 0.24), fk=2.4, skyk=0.85)
    else:
        A = env(S, 'camp', '78A0D8', sun=2.4, sunc='FFF0DC', sdir=(-0.5, -0.6, 0.6), fk=2.8, skyk=0.9)
    for j, p in enumerate(S['camp']['plume']):
        p.location = AWAY
    return A


def plume(S, t):
    for j, p in enumerate(S['camp']['plume']):
        u = (t * 0.22 + j / 7) % 1
        p.location = (18 + u * 150, 470 + 10 * math.sin(j), 322 + 16 * u + 5 * math.sin(t * 2 + j))
        s = 0.6 + 2.2 * u
        p.scale = (s * 1.6, s * 0.6, s * 0.55)


def hang_bell(S, A, t, swing=0.2):
    b = S['bell']
    b.location = A(POST[0] - 1.05, POST[1], 2.72)
    b.rotation_euler = (swing * math.sin(t * 5), swing * 0.6 * math.sin(t * 3.7), 0)


def rook_bell(S, k, t, lt):
    A = camp(S)
    plume(S, t)
    hang_bell(S, A, t)
    S['rook'].place(A(-0.7, -0.9, 0), 0.3)
    S['rook'].apply(P('cross', head=(0.05, 0.4 * math.sin(lt * 9))))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.6
    shoot(S, A(lerp(1.9, 1.4, k), lerp(-7.6, -6.6, k), 1.6), A(0.1, -0.4, 2.7), 28, fcol='FFE8D0')


def rook_off(S, k, t, lt):
    A = camp(S)
    plume(S, t)
    hang_bell(S, A, t, 0.35)
    y = lerp(2.4, 7.2, k)
    S['rook'].place(A(-1.3, y, 0), PI)
    pop = sm(lt / 0.18) * (1 - sm((lt - 0.22) / 0.18))
    S['rook'].apply(blend(walk(lt, 1.9), P('stand', aL=(0.9, 0.5, 2.3, 0.6), aR=(0.9, 0.5, 2.3, 0.6)), pop))
    shoot(S, A(lerp(-3.6, -3.0, k), lerp(-4.2, -2.2, k), 1.0), A(-1.2, 14, 5.2), 24, fcol='DCE6FF')


def north_face(S, k, t, lt):
    A = camp(S)
    plume(S, t)
    shoot(S, A(lerp(-30, -22, k), lerp(-70, -60, k), 4), A(0, 470, lerp(120, 215, sm(k))), 30, fill=0.4)


def rook_hatoff(S, k, t, lt):
    A = camp(S, dawn=True)
    hang_bell(S, A, t, 0.12)
    S['rook'].place(A(-0.6, -1.0, 0), -0.1)
    S['hat_off'] = sm(lt / 0.35)
    S['rook'].apply(blend(P('stand'), to_chest(), lt / 0.35))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(1.6, 1.1, k), lerp(-6.6, -5.8, k), 2.2), A(-0.5, -1.0, 2.3), 36, fcol='FFE0D0')


def signoff(S, k, t, lt):
    A = camp(S, dawn=True)
    rp = (0.15, 0.2, 0.0)
    S['rook'].place(A(*rp), 0.5)
    grab = sm((lt - 0.12) / 0.25)
    away = sm((lt - 0.72) / 0.3)
    S['rook'].apply(blend(blend(P('stand'), P('stand', aR=(1.5, 0.6, 0.5), head=(-0.1, 0.5)), grab), P('hat'), away))
    S['hat_tip'] = away
    S['face']['rook'] = 'warm' if away < 0.5 else 'deadpan'
    b = S['bell']
    top = A(POST[0] - 1.05, POST[1], 2.72)
    hand = A(0.75, -0.2, 1.9)
    u = sm((lt - 0.3) / 0.3)
    b.location = tuple(top[i] + (hand[i] - top[i]) * u for i in range(3))
    b.rotation_euler = (0.5 * math.sin(lt * 14) * (1 - u) + u * 0.4, 0.3 * math.sin(lt * 11), lt * 3 * u)
    if lt > 0.72:
        b.location = AWAY
    shoot(S, A(lerp(-0.6, 0.0, k), lerp(-7.4, -6.0, k), 2.3), A(0.5, 0.4, 2.7), 32, fcol='FFE0D0')


# ---------------------------------------------------------------- May 2006: up, and down
def hall_climb(S, k, t, lt):
    A = crest(S, 'day')
    gear(S, 'hall')
    y = lerp(-7.5, -4.6, k)
    S['hall'].place(A(0.3, y, 0), PI)
    w = walk(lt, 1.0)
    w.update(TRUDGE)
    S['hall'].apply(w)
    S['rook'].place(A(-0.7, y - 3.3, 0), PI)
    wr = walk(lt + 0.3, 1.2)
    wr['head'] = (-0.1, 0.0)
    S['rook'].apply(wr)
    shoot(S, A(lerp(3.4, 2.8, k), lerp(1.2, 2.0, k), lerp(4.4, 3.8, k)), A(-0.1, y - 1.2, 1.9), 34)


def ribbons(S, t):
    for piv, yaw, ph in S['top']['ribbons']:
        piv.rotation_euler = (0.3 * math.sin(t * 8 + ph), 0.25 * math.sin(t * 6.5 + ph * 1.3), 0.5 + 0.3 * math.sin(t * 7 + ph) + 0.12 * yaw)


def top_arms(S, k, t, lt):
    A = env(S, 'top', '5E9AE6', sun=3.2, sunc='FFF4E0', sdir=(-0.5, -0.6, 0.6), fk=2.6)
    ribbons(S, t)
    gear(S, 'hall', gog=True, mask=False)
    up = sm(lt / 0.35)
    S['hall'].place(A(-0.3, 0.2, 0), 0.15)
    S['hall'].apply(blend(P('stand'), P('up', lift=0.06 * abs(math.sin(lt * 7))), up))
    S['rook'].place(A(-2.4, 0.9, 0), -0.35)
    S['rook'].apply(blend(P('stand'), P('stand', aL=(0.9, 0.2, 1.6, 0.9), aR=(0.9, 0.2, 1.6 + 0.3 * math.sin(lt * 16), 0.9), head=(0.0, 0.5)), sm(lt / 0.3)))
    S['face']['rook'] = 'warm'
    a = lerp(-0.35, 0.1, k)
    shoot(S, A(-0.6 + 8.2 * math.sin(a), 0.4 - 8.2 * math.cos(a), lerp(0.9, 1.3, k)), A(-0.9, 0.5, 2.7), 28)


def stagger(lt, sp=0.9):
    w = walk(lt, sp)
    w['lean'] = 0.35
    w['head'] = (0.45, 0.25 * math.sin(lt * 3))
    w['aL'] = (0.2, 0.5 + 0.2 * math.sin(lt * 4), 0.4)
    w['aR'] = (0.2, 0.5 - 0.2 * math.sin(lt * 4), 0.4)
    return w


def down_sway(S, k, t, lt):
    A = crest(S, 'gold', 0.15)
    gear(S, 'hall', gog=False, mask=True)
    y = lerp(6.5, 3.8, k)
    S['hall'].place(A(0.25 * math.sin(lt * 3.2), y, 0), 0.0, 0.0, 0.16 * math.sin(lt * 3.2))
    S['hall'].apply(stagger(lt))
    S['face']['hall'] = 'tired'
    S['s1'].place(A(0.9, y - 1.5, 0), 0.5 + PI)
    S['s1'].apply(P('stand', aR=(0.9, 0.3, 0.6), aL=(0.3, 0.2, 0.3), head=(0.0, 0.0), lL=(0.2, 0.1), lR=(-0.2, 0.2)))
    S['s2'].place(A(-0.5, y + 1.7, 0), 0.0)
    w2 = walk(lt + 0.4, 0.9)
    w2['aL'] = (1.1, 0.1, 0.5)
    S['s2'].apply(w2)
    S['rook'].place(A(-1.35, y + 2.9, 0), 0.0)
    S['rook'].apply(walk(lt + 0.2, 1.1))
    shoot(S, A(lerp(-2.6, -2.2, k), lerp(-5.4, -4.4, k), 1.0), A(-0.1, y + 0.8, 2.0), 26, fcol='FFDDB0')


def dizzy_pov(S, k, t, lt):
    A = crest(S, 'gold', 0.3)
    yy = lerp(2.5, 1.2, k)
    S['s1'].place(A(0.4, yy - 4.2, 0), PI + 0.2)
    S['s1'].apply(P('stand', aR=(1.2, 0.3, 0.4), head=(0.0, 0.0)))
    roll = 0.3 * math.sin(lt * 4.4) + 0.25 * k
    shoot(S, A(0.3 * math.sin(lt * 3), yy, 2.3 - 0.9 * sm((k - 0.6) / 0.4)), A(0.6 * math.sin(lt * 2.4), yy - 7, lerp(1.6, 0.6, k)), 24, roll=roll,
          fcol='FFDDB0')


def collapse(S, k, t, lt):
    A = crest(S, 'gold', 0.4)
    gear(S, 'hall', gog=False, mask=True)
    d = sm(lt / 0.5)
    S['hall'].place(A(0.2, 0.6, 0.36 * d), 0.25, -PI / 2 * d * 0.92)
    S['hall'].apply(blend(blend(P('stand', lean=0.3, head=(0.4, 0.0)), KNEE, min(1, d * 2)), DOWN, max(0, d * 2 - 1)))
    S['face']['hall'] = 'shut' if d > 0.6 else 'tired'
    rp = (-1.2, lerp(5.6, 2.2, sm(lt / 0.45)))
    S['s1'].place(A(rp[0], rp[1], 0), look_yaw(rp, (0.2, 1.4)))
    S['s1'].apply(blend(walk(lt, 2.2), KNEE, sm((lt - 0.35) / 0.25)))
    shoot(S, A(lerp(4.4, 3.6, k), lerp(-2.6, -2.0, k), lerp(1.3, 0.8, k)), A(0.3, 0.8, lerp(1.6, 0.6, d)), 34, fcol='FFDDB0')


# ---------------------------------------------------------------- dusk: hours, and the order
def haul(S, k, t, lt):
    A = crest(S, 'gold', 0.55)
    gear(S, 'hall', gog=False, mask=True)
    pull = 0.5 + 0.5 * math.sin(lt * 5.5)
    S['hall'].place(A(0.1, 0.4 - 0.25 * pull, 0.2), 0.0, -0.6 + 0.15 * pull)
    S['hall'].apply(P('sit', lift=-0.75, head=(0.5, 0.2), aL=(1.6, 0.5, 0.2), aR=(1.6, 0.5, 0.2), lL=(1.3, 0.3), lR=(1.2, 0.4)))
    S['face']['hall'] = 'shut'
    for who, x in (('s1', -1.0), ('s2', 1.0)):
        S[who].place(A(x, -1.1 - 0.25 * pull, 0), PI - 0.35 * x)
        S[who].apply(P('stand', lean=-0.25 - 0.2 * pull, aL=(1.0, 0.1, 0.5 + 0.5 * pull), aR=(1.0, 0.1, 0.5 + 0.5 * pull), lL=(0.35, 0.3), lR=(-0.3, 0.2),
                       head=(0.2, 0.0)))
    S['rook'].place(A(-0.2, 2.0 - 0.2 * pull, 0), 0.0)
    S['rook'].apply(P('stand', lean=0.45 + 0.1 * pull, aL=(1.2, 0.15, 0.3), aR=(1.2, 0.15, 0.3), lL=(-0.4, 0.2), lR=(0.35, 0.5), head=(0.2, 0.0)))
    shoot(S, A(lerp(6.6, 5.6, k), lerp(-3.4, -2.2, k), lerp(1.4, 1.8, k)), A(0.0, 0.3, 1.7), 30, fcol='FFD0A0')


def sun_sink(S, k, t, lt):
    A = crest(S, 'gold', lerp(0.3, 0.8, k), sun_at=(-716, 255))
    lying(S, A, 'hall', (0.2, 0.6), 0.25)
    gear(S, 'hall', gog=False, mask=True)
    b = 0.5 + 0.5 * math.sin(lt * 9)
    S['s1'].place(A(1.1, 0.9, 0), look_yaw((1.1, 0.9), (0.2, 1.3)))
    S['s1'].apply(blend(KNEE, P('stand', lift=-0.76, lL=(0.2, 1.5), lR=(1.3, 1.45), lean=0.75, aL=(1.3, 0.0, 0.3), aR=(1.3, 0.0, 0.3)), b))
    S['s2'].place(A(-0.6, -0.4 - 0.5 * math.sin(lt * 2.0), 0), look_yaw((-0.6, -0.4), (0.2, 1.3)))
    S['s2'].apply(P('stand', aR=(0.4, 0.2, 2.2, 0.5), head=(0.25, 0.3 * math.sin(lt * 3))))
    shoot(S, A(lerp(14, 12, k), lerp(-4.4, -3.6, k), lerp(1.0, 1.6, k)), A(0, 0.8, lerp(2.6, 1.9, k)), 40, fill=0.35, fcol='FFB080')


def radio_hand(S, k, t, lt):
    A = env(S, 'radio', '1A1C2A', fk=0.5)
    R = S['radio']
    fl = 1 + 0.12 * math.sin(t * 17) + 0.08 * math.sin(t * 29)
    R['lamp'].data.energy = 420 * fl
    R['door'].data.energy = 60
    R['needle'].rotation_euler = (0, 0.5 * math.sin(t * 13) + 0.3 * math.sin(t * 31), 0)
    up = sm(lt / 0.35)
    hs = S['handset']
    hs.grip(0.72)
    hs.place(A(lerp(1.2, 0.75, up), lerp(0.2, 0.75, up), lerp(1.75, 2.7, up) + 0.03 * math.sin(lt * 9)), (lerp(-0.2, -0.75, up), lerp(0.2, -0.2, up),
                                                                                                    lerp(0.5, 0.25, up)))
    shoot(S, A(lerp(-0.6, -0.2, k), lerp(-3.6, -2.7, k), lerp(2.7, 2.5, k)), A(0.1, 1.6, 2.3), 34, fill=0.3, fcol='FFC890')


def sherpa_leave(S, k, t, lt):
    A = crest(S, 'gold', 1.0)
    lying(S, A, 'hall', (0.2, 0.6), 0.25)
    gear(S, 'hall', gog=False, mask=False)
    go = sm((lt - 0.25) / 0.3)
    for i, (who, x, y0) in enumerate((('s1', 1.0, -2.6), ('s2', -0.7, -4.4))):
        y = y0 - 2.4 * go * max(0.0, lt - 0.25)
        S[who].place(A(x, y, 0), lerp(look_yaw((x, y0), (0.2, 1.0)), 0.0, go))
        S[who].apply(blend(P('stand', head=(0.5, 0.0), aL=(0.1, 0.1, 0.2), aR=(0.1, 0.1, 0.2)), walk(lt, 1.2), go))
        lamp(S, i, S[who], 30)
    rp = (-1.1, 0.9, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.5, -4.0)))
    S['hat_off'] = sm(lt / 0.3)
    S['rook'].apply(blend(P('stand'), to_chest(), lt / 0.3))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(1.7, 1.3, k), lerp(6.6, 7.2, k), lerp(1.6, 2.0, k)), A(-0.3, -1.0, 1.7), 26, fill=2.2, fcol='C8B8F0')


def house_night(S, k, t, lt):
    A = env(S, 'house', '070B1C', sun=0.35, sunc='9DB8FF', sdir=(-0.4, 0.5, 0.75), fk=1.0)
    Hs = S['house']
    on = lt > 0.42
    paint(Hs['winm'], 'FFC27A' if on else '1A2238', 5.0 if on else 0.0)
    Hs['glow'].data.energy = 380 if on else 0
    shoot(S, A(lerp(-3.5, 0.6, sm(k)), lerp(-21, -14.5, sm(k)), lerp(2.4, 2.0, k)), A(lerp(0.5, 2.6, k), 4, 3.3), 32, fill=0.7, fcol='8FA4E8')


# ---------------------------------------------------------------- the night
def night_alone(S, k, t, lt):
    A = crest(S, 'night')
    lying(S, A, 'hall', (0.2, 0.6), 0.25)
    gear(S, 'hall', gog=False, mask=False)
    seen(S['hall'].extra['frost'], True)
    rp = (-0.9, -1.3, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.2, 0.9)))
    S['rook'].apply(P('sit', lift=-0.62, head=(0.25 + 0.1 * math.sin(lt * 2), 0.3 * math.sin(lt * 1.4)), lL=(1.3, 1.2), lR=(1.3, 1.2)))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(5.6, 4.4, k), lerp(-5.6, -4.6, k), lerp(2.4, 1.9, k)), A(-0.2, 0.9, 2.2), 30, fill=1.4, fcol='9DB8FF')


def night_face(S, k, t, lt):
    A = crest(S, 'night')
    lying(S, A, 'hall', (0.2, 0.6), 0.25)
    gear(S, 'hall', gog=False, mask=False)
    seen(S['hall'].extra['frost'], True)
    for i, p in enumerate(S['puff']):
        u = (lt * 0.9 + i * 0.33) % 1
        p.location = A(-0.4 + 0.08 * math.sin(i + u * 4), 2.75 - 0.15 * u, 0.75 + 0.8 * u)
        s = 0.25 + 0.5 * u
        p.scale = (s, s, s)
    shoot(S, A(-0.36, lerp(2.2, 2.35, k), lerp(4.6, 3.9, k)), A(-0.38, lerp(2.4, 2.5, k), 0.5), 50, roll=lerp(-0.12, 0.05, k), fill=1.9, fcol='9DB8FF')


# ---------------------------------------------------------------- dawn: the four climbers
def team(S, A, y0, lt, gap=1.9, sp=0.95, walk_=True):
    for i, who in enumerate(('m1', 'm2', 'm3', 'm4')):
        y = y0 - i * gap
        x = 0.35 * (-1 if i % 2 else 1) - 0.2
        S[who].place(A(x, y, 0), PI)
        if walk_:
            w = walk(lt + i * 0.27, sp)
            w.update(TRUDGE)
            S[who].apply(w)


def team_climb(S, k, t, lt):
    A = crest(S, 'sunrise', lerp(0.0, 0.5, k))
    y0 = lerp(-16.0, -13.4, k)
    team(S, A, y0, lt)
    for i, who in enumerate(('m1', 'm2', 'm3', 'm4')):
        lamp(S, i, S[who], 40)
    shoot(S, A(lerp(4.6, 3.6, k), lerp(-8.5, -7.6, k), lerp(4.6, 3.6, k)), A(-0.2, y0 - 2.6, 2.0), 30, fill=1.0, fcol='C8B8F0')


def find_pov(S, k, t, lt):
    A = crest(S, 'sunrise', 0.75)
    seated(S, A, turn=0.0, nod=0.1)
    S['m1'].place(A(0.3, lerp(-7.6, -7.0, k), 0), PI)
    S['m1'].apply(blend(walk(lt, 1.0), P('stand', aL=(0.3, 0.3, 0.5), aR=(0.3, 0.3, 0.5), lean=-0.1), sm(lt / 0.3)))
    shoot(S, A(lerp(1.8, 1.6, k), lerp(-11.6, -10.8, k), 2.9), A(0.5, 0.0, 1.7), 28, fcol='FFD0B0')


def hall_talks(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    wave = sm((lt - 0.5) / 0.3)
    beat = 0.12 * math.sin(lt * 5.0) * wave                    # the raised hand keeps moving while he talks
    seated(S, A, turn=lerp(-0.2, -1.15, sm(lt / 0.4)), nod=0.06 * math.sin(lt * 3.1) * wave, face='calm',
           aL=(0.62 + 0.5 * wave + beat, 0.3 + 0.5 * wave, 0.75 + 0.9 * wave - beat, 0.25))
    S['jaw']['found'] = 0.28 * abs(math.sin(lt * 11)) if lt > 0.45 else 0.0
    jolt = sm((lt - 0.95) / 0.22)                              # Rook hears him speak: jolts back, hands up...
    peer = sm((lt - 1.6) / 0.5)                                # ...then leans in to check he heard right
    rp = (0.6 + 0.1 * jolt, 2.6 + 0.55 * jolt - 0.35 * peer, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.5, 0.0)))
    still = P('stand', lean=-0.1, aL=(0.3, 0.5, 0.6), aR=(0.3, 0.5, 0.6), head=(0.1, 0.0))
    back = P('stand', lean=-0.2, aL=(0.9, 0.9, 1.3), aR=(0.9, 0.9, 1.3), head=(0.1, 0.0))
    lean_in = P('stand', lean=0.12, aL=(0.2, 0.35, 0.4), aR=(0.5, 0.3, 1.5), head=(0.1, 0.0))
    S['rook'].apply(blend(blend(still, back, jolt), lean_in, peer))
    S['face']['rook'] = 'shocked' if lt > 0.95 else 'deadpan'
    shoot(S, A(lerp(4.4, 2.7, k), lerp(-5.6, -3.9, k), lerp(1.3, 1.9, k)), A(0.3, 0.6, lerp(1.7, 1.55, k)), 40, fcol='FFD8B8')


def team_stare(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    halt = sm(lt / 0.55)                                       # the three behind are still walking in and pile up
    for i, (who, x, y) in enumerate((('m1', -0.3, -4.2), ('m2', 0.75, -5.3), ('m3', -1.1, -5.9), ('m4', 0.3, -6.9))):
        late = sm((lt - 0.12 * i) / 0.55)
        side = 0.45 * sm((lt - 0.6 - 0.12 * i) / 0.4) * (1 if x > 0 else -1) if i else 0.0     # each steps out to see past the leader
        S[who].place(A(x + side, y - (0.9 + 0.3 * i) * (1 - late) if i else y, 0), PI + 0.12 * x)
        stop = P('stand', lean=-0.08 if i == 0 else 0.15 * i, aL=(0.25, 0.4, 0.5), aR=(0.25, 0.4, 0.5), head=(0.0, 0.15 * x - 0.5 * side))
        S[who].apply(blend(walk(lt + i * 0.27, 0.95), stop, late) if i else stop)
    lift = sm((lt - 0.2) / 0.2)
    S['m1'].apply(blend(P('stand', lean=-0.08), P('stand', lean=-0.08, aR=(0.2, 1.7, 1.75, -1.4)), lift))
    seen(S['m1'].extra['gog'], lift < 0.6)
    S['face']['m1'] = 'wide'
    shoot(S, A(lerp(1.7, 0.3, k), lerp(2.6, 0.4, k), lerp(1.4, 2.0, k)), A(-0.1, -5.0, 2.1), 28, fcol='FFD8B8')


def rook_drop(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    rp = (-0.6, 2.4, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (2.5, -1.5)))
    S['hat_off'] = sm(lt / 0.2)
    S['rook'].apply(blend(P('stand'), P('shrug', head=(-0.1, -0.3)), sm(lt / 0.2)))
    S['face']['rook'] = 'shocked'
    feather(S, A(rp[0] + 0.2, rp[1], 3.2), lt, 0.05, 3)
    shoot(S, A(lerp(2.6, 2.2, k), lerp(-1.2, -0.8, k), lerp(1.7, 1.9, k)), A(-0.6, 2.4, 2.3), 34, fill=1.5, fcol='FFD8B8')


# ---------------------------------------------------------------- the choice, and the way down
def summit_near(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    turn = sm((lt - 0.55) / 0.35)
    S['m1'].place(A(-0.4, 6.0, 0), PI)
    S['m1'].apply(P('stand', head=(lerp(-0.45, 0.1, turn), lerp(0.0, 2.2, turn)), aR=(lerp(1.0, 0.1, turn), 0.2, 0.3)))
    seen(S['m1'].extra['gog'], False)
    shoot(S, A(lerp(1.6, 1.0, k), lerp(0.6, 1.8, k), lerp(1.0, 1.4, k)), A(-0.2, 30, lerp(11, 8, turn)), 26, fcol='FFD8B8')


def tea(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=-0.5, nod=0.15, face='calm', aR=(1.0, 0.1, 1.5, 0.3))
    p1 = (1.3, -1.5)
    S['m1'].place(A(p1[0], p1[1], 0), look_yaw(p1, (0.6, 0.0)))
    S['m1'].apply(P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.3, aL=(0.4, 0.1, 0.6), aR=(1.25, 0.0, 0.3), head=(0.1, 0.0)))
    seen(S['m1'].extra['gog'], False)
    S['cup'].location = A(1.0, -0.72 + 0.03 * math.sin(lt * 6), 1.32)
    p2 = (-0.9, -1.6)
    S['m2'].place(A(p2[0], p2[1], 0), look_yaw(p2, (0.5, 0.0)))
    S['m2'].apply(blend(P('stand', lean=0.3, aL=(0.9, 0.2, 0.9), aR=(0.9, 0.2, 0.9)), KNEE, sm(lt / 0.5)))
    p4 = (-1.0, 1.3)
    S['m4'].place(A(p4[0], p4[1], 0), look_yaw(p4, (0.5, 0.0)))
    S['m4'].apply(P('stand', lean=0.35, aL=(1.0, 0.1, 0.7), aR=(1.0, 0.1, 0.7), head=(0.3, 0.0)))
    rp = (0.4, 3.4, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.5, 0.0)))
    S['hat_off'] = 1.0
    S['rook'].apply(to_chest(head=(0.15, 0.0)))
    S['face']['rook'] = 'warm'
    a = lerp(0.95, 0.6, k)
    shoot(S, A(0.3 + 8.6 * math.sin(a), 0.3 - 8.6 * math.cos(a), lerp(2.8, 2.3, k)), A(0.2, 0.5, 1.6), 32, fcol='FFD8B8')


def ladder_up(S, k, t, lt):
    A = env(S, 'step', '6FA6E4', sun=3.0, sunc='FFF0DC', sdir=(-0.5, -0.7, 0.55), fk=2.4)
    for i, who in enumerate(('s1', 's2', 'm4')):
        u = lerp(0.42, 0.56, k) - i * 0.23
        if who == 'm4':
            seen(S[who].extra['gog'], True)
        S[who].place(A(0, lerp(-2.2, -0.35, u) - 0.42, 16.6 * u), PI, 0.1)
        ph = lt * 5 + i * 1.7
        a, b = 0.5 + 0.5 * math.sin(ph), 0.5 - 0.5 * math.sin(ph)
        S[who].apply(P('stand', aL=(1.6 + 1.0 * a, 0.1, 0.6 * b), aR=(1.6 + 1.0 * b, 0.1, 0.6 * a), lL=(0.9 * a, 1.1 * a), lR=(0.9 * b, 1.1 * b),
                       head=(-0.35, 0.0)))
    shoot(S, A(lerp(-7.5, -6.0, k), lerp(-12.5, -11, k), lerp(2.2, 4.6, k)), A(0.3, -0.8, lerp(6.6, 8.4, k)), 28)


def carry_down(S, k, t, lt):
    A = crest(S, 'day')
    y = lerp(-6.0, -9.4, k)
    f = S['found']
    f.place(A(0.0, y, 0), 0.0)
    w = walk(lt, 1.0)
    w['aL'], w['aR'], w['lean'], w['head'] = (0.5, 1.2, 0.3), (0.5, 1.2, 0.3), 0.2, (0.3, 0.0)
    f.apply(w)
    S['face']['found'] = 'tired'
    for who, x, dy, ph in (('s1', -0.95, 0.1, 0.2), ('s2', 0.95, 0.1, 0.5), ('m4', 0.2, -2.6, 0.7)):
        S[who].place(A(x, y + dy, 0), 0.0)
        ww = walk(lt + ph, 1.0)
        if who != 'm4':
            ww['aR' if x < 0 else 'aL'] = (0.6, 0.9, 0.9)
        S[who].apply(ww)
        seen(S[who].extra['gog'], True)
    S['rook'].place(A(-0.3, y + 3.4, 0), 0.0)
    S['rook'].apply(walk(lt + 0.1, 1.3))
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(-7.5, -6.6, k), lerp(-13.5, -15.0, k), lerp(3.2, 2.6, k)), A(0.0, y + 0.8, 1.9), 34)


# ---------------------------------------------------------------- afterwards
def book_desk(S, k, t, lt):
    A = env(S, 'study', '2A2620', fk=1.6)
    St = S['study']
    St['key'].data.energy = 2200
    St['warm'].data.energy = 320
    h_ = S['home']
    h_.place(A(0, 0.0, 0), 0.0)
    wr = 0.12 * math.sin(lt * 9)
    h_.apply(P('sit', lift=-0.15, lean=0.3, head=(0.3, 0.1), aL=(1.05, -0.1 + wr * 0.4, 1.25, 0.5), aR=(0.9, 0.0, 1.3, 0.7), lL=(1.45, 1.5), lR=(1.45, 1.5)))
    S['face']['home'] = 'warm'
    St['pen'].location = (-0.36 + wr * 0.5, -0.86, 1.83)
    St['pen'].rotation_euler = (0.5, 0.3, 0)
    rp = (1.5, 0.55, 0.0)
    S['rook'].place(A(*rp), 0.4)
    S['rook'].apply(P('stand', aL=(1.1, -0.15, 1.3, 0.6), aR=(1.1, -0.15, 1.3, 0.6), head=(0.4, 0.0)))
    S['face']['rook'] = 'warm' if lt > 0.9 else 'calm'
    S['book'].location = A(1.68, 0.1, 2.05)
    S['book'].rotation_euler = (1.0, 0, 0.4)
    a = lerp(-0.1, 0.25, k)
    shoot(S, A(0.7 + 6.0 * math.sin(a), -0.4 - 6.0 * math.cos(a), lerp(3.1, 2.8, k)), A(0.7, -0.2, 2.45), 40, fill=2.2, fcol='FFE8D0')


def empty_crest(S, k, t, lt):
    A = crest(S, 'day')
    seen(S['crest']['hollow'], True)
    shoot(S, A(lerp(2.6, 2.0, k), lerp(4.6, 3.6, k), lerp(2.4, 3.6, k)), A(0.0, lerp(0.0, -7.0, sm(k)), lerp(0.2, 0.6, k)), 28)


# ---------------------------------------------------------------- photographs for the case board
def photo_peak(S, k, t, lt):
    A = camp(S)
    plume(S, 1.0)
    shoot(S, A(-20, -60, 4), A(0, 470, 190), 36, fill=0.4)


def photo_hall(S, k, t, lt):
    A = env(S, 'top', '5E9AE6', sun=3.2, sunc='FFF4E0', sdir=(-0.5, -0.6, 0.6), fk=2.6)
    ribbons(S, 0.4)
    gear(S, 'hall', gog=True, mask=False)
    S['hall'].place(A(-0.3, 0.2, 0), 0.1)
    S['hall'].apply(P('up'))
    shoot(S, A(1.6, -6.4, 1.4), A(0.0, 0.4, 2.6), 34)


def photo_sit(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=-0.9, nod=0.0, face='calm', aL=(1.1, 0.8, 1.6, 0.25))
    shoot(S, A(3.6, -4.6, 1.6), A(0.4, 0.2, 1.5), 40, fcol='FFD8B8')


SHOTS3D = {f.__name__: f for f in (
    sun_ridge, sit_wide, sit_close, bare_head, bare_hands, rook_gape, rook_bell, rook_off, north_face, hall_climb, top_arms, down_sway, dizzy_pov,
    collapse, haul, sun_sink, radio_hand, sherpa_leave, house_night, night_alone, night_face, team_climb, find_pov, hall_talks, team_stare,
    rook_drop, summit_near, tea, ladder_up, carry_down, book_desk, empty_crest, rook_hatoff, signoff)}
STILLS = dict(peak=photo_peak, hall=photo_hall, sit=photo_sit)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it. New sets: a tent ledge on a steep snow face under a summit (1984, the first
# attempt), a high camp of dome tents on a shelf (where the Sherpas start from the next morning), a living room at
# night (the news reaching his family), a rock alcove beside the route at night (the climber who died earlier that
# month; the alcove is shown empty, nobody is depicted in it), and a broad snow slope with a fixed line (the way
# down). New shots on the Short's sets as well. Still generic: no emblem, flag, sign or lettering anywhere; the
# camps, room and slope are not models of real places; the extra people (two teammates of 1984, the expedition
# leader, his wife and sons, a third Sherpa) are stand-ins, not likenesses.
import bmesh  # noqa: E402

SETS.update(ledge=(28000, 0, 0), hicamp=(32000, 0, 0), room=(36000, 0, 0), alcove=(40000, 0, 0), slope=(44000, 0, 0))
SLOPE = math.tan(0.34)
_kit_add = add


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """The kit's primitives made from mesh data instead of operators (operators slow down as the scene fills). The
    Short's set functions look this name up when they run, so every set in the film builds this way."""
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


def dome(r, x, y, col, s=1.0, yaw=0.0):
    """A small dome tent with a dark door on its -Y side."""
    t = empty((x, y, 0), r, (0, 0, yaw))
    add('ico_sphere', col, (0, 0, 0.1 * s), scale=(1.7 * s, 1.5 * s, 1.2 * s), radius=1, subdivisions=2, parent=t, rough=0.75)
    add('ico_sphere', '1B1E2A', (0, -1.18 * s, 0.35 * s), scale=(0.55 * s, 0.4 * s, 0.62 * s), radius=1, subdivisions=1, parent=t)
    for sx in (-1, 1):
        add('cylinder', 'E8E4D8', (sx * 1.9 * s, -0.4 * s, 0.3 * s), rot=(0, sx * 0.95, 0), radius=0.015, depth=1.3 * s, vertices=4, parent=t)
    return t


# ---------------------------------------------------------------- 1984: a tent ledge under the summit
def set_ledge(r):
    out = {}
    th = 0.5
    box('C4D0E6', (0, 45 * math.cos(th), 45 * math.sin(th) - 0.6), (260, 250, 1), r, rot=(th, 0, 0))            # the face
    box(SNOWC, (0, -1.5, -3.0), (15, 7, 6), r)                                                                # the ledge
    for j in range(22):
        x = -7.5 + 15 * rn(j, 141)
        sc = 0.5 + 0.6 * rn(j, 142)
        add('ico_sphere', SNOWL, (x, -4.9 + 0.3 * rn(j, 143), -0.15), scale=(sc * 1.6, sc, sc * 0.5), radius=1, subdivisions=1, parent=r)
    for j in range(46):                                                                                       # rock showing through
        x, u = -70 + 140 * rn(j, 144), -40 + 120 * rn(j, 145)
        if abs(x) < 8 and -8 < u < 6:
            continue
        sc = 1.5 + 4.5 * rn(j, 146)
        add('ico_sphere', ROCKC if j % 3 else ROCKD, (x, u * math.cos(th), u * math.sin(th) - 0.1), rot=(th, 0, rn(j, 147) * 3),
            scale=(sc * 1.5, sc, sc * 0.45), radius=1, subdivisions=1, parent=r)
    dome(r, -3.4, 0.4, 'E3C22A', 1.0, 0.2)
    dome(r, -6.6, -0.8, 'D8362A', 0.8, -0.3)
    box(SNOWL, (0.9, -1.3, 0.25), (1.0, 0.8, 0.5), r, rot=(0, 0, 0.2))                                        # a snow block to sit on
    for j, (x, y) in enumerate(((4.6, 0.6), (5.0, 0.9), (5.4, 0.5))):                                         # ski poles and an axe stuck in the snow
        add('cylinder', 'C8CCD8' if j < 2 else 'FF7A1A', (x, y, 0.9), rot=(0.1 * j - 0.1, 0.08, 0), radius=0.03, depth=1.9, vertices=5, parent=r)
    box('2A2F3A', (3.6, 0.9, 0.4), (0.7, 0.5, 0.9), r, rot=(0.2, 0, 0.3))
    add('cone', 'D2DBEC', (6, 138, 86), rot=(0, 0, 0.4), radius1=62, radius2=0, depth=72, vertices=5, parent=r)           # the summit above
    add('cone', ROCKC, (20, 134, 78), rot=(0, 0, 1.0), radius1=58, radius2=0, depth=62, vertices=5, parent=r)
    add('cone', SNOWL, (6, 138, 111.5), rot=(0, 0, 0.4), radius1=18, radius2=0, depth=21, vertices=5, parent=r)
    out['plume'] = [keep(add('ico_sphere', 'F4F8FF', (6, 138, 124), scale=(1, 0.6, 0.5), radius=5, subdivisions=1, parent=r, alpha=0.7, emit=0.3))
                    for _ in range(5)]
    cloud_sea(r, -80, 60, 520, 151, 0)
    far_peaks(r, 9, -80, 161, 260, 460)
    return out


# ---------------------------------------------------------------- the high camp
def set_hicamp(r):
    out = {}
    th = 0.5
    box('C4D0E6', (0, 0, -0.7), (300, 260, 1), r, rot=(th, 0, 0))
    box(SNOWC, (0, -1.0, -5.0), (30, 11, 10), r)
    for j in range(24):
        x = -15 + 30 * rn(j, 171)
        sc = 0.5 + 0.7 * rn(j, 172)
        add('ico_sphere', SNOWL, (x, -6.4 + 0.3 * rn(j, 173), -0.2), scale=(sc * 1.7, sc, sc * 0.5), radius=1, subdivisions=1, parent=r)
    for j in range(40):
        x, u = -80 + 160 * rn(j, 174), -70 + 160 * rn(j, 175)
        if abs(x) < 16 and -14 < u < 12:
            continue
        sc = 1.2 + 3.6 * rn(j, 176)
        add('ico_sphere', ROCKC if j % 3 else ROCKD, (x, u * math.cos(th), u * math.sin(th) - 0.2), rot=(th, 0, rn(j, 177) * 3),
            scale=(sc * 1.5, sc, sc * 0.45), radius=1, subdivisions=1, parent=r)
    for x, y, col, s, yaw in ((-6.5, 0.2, 'FF7A1A', 1.0, 0.25), (-1.4, 1.5, 'E3C22A', 1.1, -0.1), (5.6, 0.4, '2FA36B', 1.0, -0.3), (10.5, 1.3, 'D8362A', 0.9, 0.1),
                              (-11.5, 1.0, '2D6FA8', 0.9, 0.3)):
        dome(r, x, y, col, s, yaw)
    for j in range(5):                                                                                        # spent and spare bottles
        add('cylinder', 'FF7A1A' if j % 2 else 'E3C22A', (2.2 + 0.3 * j, -2.4 + 0.1 * j, 0.14), rot=(PI / 2, 0, 0.3 * j), radius=0.13, depth=0.9,
            vertices=6, parent=r, rough=0.4)
    for j in range(9):                                                                                        # the fixed line going up
        u = 6 + j * 9
        p = (2.6 + 0.5 * j, u * math.cos(th), u * math.sin(th))
        add('cylinder', '8A90A0', (p[0], p[1], p[2] + 0.4), radius=0.04, depth=1.0, vertices=5, parent=r)
        if j:
            ln = add('cylinder', 'FF7A1A', (0, 0, 0), radius=0.5, depth=1, vertices=4, parent=r, rough=0.7)
            span(ln, (q[0], q[1], q[2] + 0.75), (p[0], p[1], p[2] + 0.75), 0.025)
        q = p
    cloud_sea(r, -90, 60, 540, 181, 0)
    far_peaks(r, 10, -90, 191, 240, 460)
    return out


# ---------------------------------------------------------------- the living room, at night
def set_room(r):
    out = {}
    box('6A4E3A', (0, 0, -0.5), (22, 16, 1), r)
    box('C8B8A0', (0, 4.6, 4.5), (22, 0.2, 9), r)
    for sx in (-1, 1):
        box('BFAE94', (sx * 9.4, 0, 4.5), (0.2, 16, 9), r)
    box('8A7A64', (0, 4.48, 0.25), (22, 0.06, 0.5), r)
    box('A8472E', (0.4, 0.0, 0.012), (9, 5.2, 0.024), r)                                                      # a rug
    box('E8E0CC', (0.4, 0.0, 0.02), (7.8, 4.2, 0.03), r)
    out['winm'] = newmat('room_win', '1A2A58', 0.3, 0.7)
    box('F2EEE2', (-3.6, 4.47, 4.6), (4.2, 0.1, 3.6), r)                                                      # a window on the night
    wear(box('1A2A58', (-3.6, 4.42, 4.6), (3.8, 0.08, 3.2), r), out['winm'])
    box('F2EEE2', (-3.6, 4.36, 4.6), (0.1, 0.05, 3.2), r)
    box('F2EEE2', (-3.6, 4.36, 4.6), (3.8, 0.05, 0.1), r)
    for sx in (-1, 1):
        box('7A3A44', (-3.6 + sx * 2.5, 4.3, 4.4), (0.9, 0.16, 4.6), r)                                       # curtains
    box('3E6E8A', (3.4, 3.0, 0.24), (5.4, 1.9, 0.48), r)                                                      # the sofa
    box('35607A', (3.4, 3.95, 0.95), (5.4, 0.45, 1.5), r)
    for sx in (-1, 1):
        box('35607A', (3.4 + sx * 2.9, 3.0, 0.55), (0.45, 1.9, 1.1), r)
    box('E3C22A', (5.3, 3.4, 0.75), (0.8, 0.3, 0.7), r, rot=(0.3, 0, 0.2))                                    # a cushion
    box('5E442C', (-6.6, 3.6, 0.7), (1.5, 1.2, 1.4), r)                                                       # a side table with a lamp
    add('cylinder', '3A3F4C', (-6.6, 3.6, 1.9), radius=0.05, depth=1.0, vertices=5, parent=r)
    out['shadem'] = newmat('room_shade', 'FFD08A', 0.5, 4.0)
    wear(add('cone', 'FFD08A', (-6.6, 3.6, 2.6), radius1=0.6, radius2=0.3, depth=0.7, vertices=8, parent=r), out['shadem'])
    box('5A4030', (7.6, 4.1, 3.0), (2.8, 0.8, 6.0), r)                                                        # a bookcase of plain spines
    for j in range(21):
        col = ('8A3A2E', '2D6FA8', 'D8D2C0', '3E6E5A', 'E3C22A', '6A4E8A')[j % 6]
        box(col, (6.5 + (j % 7) * 0.34, 3.66, 1.2 + (j // 7) * 1.75), (0.26, 0.2, 1.1 + 0.25 * rn(j, 201)), r)
    for j, (x, z, w_, h_, col) in enumerate(((0.9, 5.4, 1.5, 1.1, '9AB0C0'), (2.9, 5.0, 1.0, 1.3, 'C8A88A'), (4.6, 5.5, 1.3, 0.9, 'A8B89A'))):   # blank frames
        box('5E442C', (x, 4.46, z), (w_ + 0.2, 0.06, h_ + 0.2), r)
        box(col, (x, 4.42, z), (w_, 0.05, h_), r)
    box('5E442C', (-0.6, 1.2, 0.5), (2.4, 1.2, 0.12), r)                                                      # a low table
    for sx in (-1, 1):
        box('4A3422', (-0.6 + sx * 1.0, 1.2, 0.22), (0.12, 1.0, 0.44), r)
    add('cylinder', 'E8E4D8', (-0.1, 1.3, 0.66), radius=0.13, depth=0.2, vertices=8, parent=r)
    out['warm'] = light((-6.0, 2.6, 2.9), 0, 'FFC27A', kind='POINT', parent=r)
    out['moon'] = light((-3.6, 3.4, 4.6), 0, '8FA4E8', 3.0, parent=r)
    out['key'] = light((1.0, -5.0, 5.0), 0, 'FFE0C0', 5.0, parent=r)
    return out


# ---------------------------------------------------------------- the alcove beside the route (shown empty)
def set_alcove(r):
    out = {}
    box(ROCKD, (0, 10, 9), (90, 10, 22), r)
    box(SNOWC, (0, -2.0, -0.5), (90, 10, 1), r)
    th = 0.9
    box('B4C2DC', (0, -7 - 40 * math.cos(th), -40 * math.sin(th) - 0.6), (90, 80, 1), r, rot=(th, 0, 0))
    box('24273A', (0, 4.0, -0.02), (10, 4.0, 0.2), r)                                                         # bare rock floor inside
    box('2A2D3C', (0, 3.3, 3.75), (11.5, 5.6, 1.3), r, rot=(0.1, 0, 0.03))                                    # the overhang
    box(SNOWL, (0, 2.6, 4.5), (11.8, 4.6, 0.35), r, rot=(0.1, 0, 0.03))
    for sx in (-1, 1):
        add('ico_sphere', '34374A', (sx * 5.4, 2.9, 1.5), rot=(0, 0, sx * 0.3), scale=(1.6, 2.9, 2.6), radius=1, subdivisions=1, parent=r)
        add('ico_sphere', SNOWL, (sx * 5.6, 0.6, 0.1), scale=(1.8, 1.2, 0.5), radius=1, subdivisions=1, parent=r)
    for j in range(30):
        x, z = -40 + 80 * rn(j, 211), 1 + 17 * rn(j, 212)
        if abs(x) < 7 and z < 6:
            continue
        s = 1.0 + 2.0 * rn(j, 213)
        add('ico_sphere', ROCKC if j % 3 else '5E6378', (x, 4.9, z), rot=(rn(j, 214), 0, rn(j, 215) * 3), scale=(s * 1.5, 0.7, s), radius=1, subdivisions=1,
            parent=r)
    for j in range(26):
        x = -40 + 80 * rn(j, 216)
        sc = 0.5 + 0.7 * rn(j, 217)
        add('ico_sphere', SNOWL, (x, -6.7 + 0.4 * rn(j, 218), -0.15), scale=(sc * 1.8, sc, sc * 0.5), radius=1, subdivisions=1, parent=r)
    for j in range(11):                                                                                       # the fixed line along the path
        x = -30 + j * 6
        add('cylinder', '8A90A0', (x, -0.4, 0.45), rot=(0.1 * (rn(j, 219) - 0.5), 0.1, 0), radius=0.04, depth=1.1, vertices=5, parent=r)
        if j < 10:
            ln = add('cylinder', 'FF7A1A', (0, 0, 0), radius=0.5, depth=1, vertices=4, parent=r, rough=0.7)
            span(ln, (x, -0.4, 0.8), (x + 6, -0.4, 0.8), 0.022)
    cloud_sea(r, -70, 50, 520, 221, 0)
    far_peaks(r, 9, -70, 231, 240, 440)
    out['stars'] = stars(r, 70, 800, 241)
    return out


# ---------------------------------------------------------------- the snow slope on the way down
def set_slope(r):
    out = {}
    box('D2DCEE', (0, 0, -0.55), (500, 420, 1), r, rot=(0.34, 0, 0))
    for j in range(50):
        x, y = -90 + 150 * rn(j, 251), -110 + 200 * rn(j, 252)
        if abs(x - 1) < 5:
            continue
        sc = 1.0 + 3.4 * rn(j, 253)
        if j % 3 == 0:
            add('ico_sphere', SNOWL, (x, y, y * SLOPE - 0.1), rot=(0.34, 0, 0), scale=(sc * 2.2, sc * 1.4, sc * 0.3), radius=1, subdivisions=1, parent=r)
        else:
            add('ico_sphere', ROCKC if j % 2 else ROCKD, (x, y, y * SLOPE), rot=(0.34, 0, rn(j, 254) * 3), scale=(sc * 1.4, sc, sc * 0.6), radius=1,
                subdivisions=1, parent=r)
    for j in range(16):                                                                                       # stakes and the fixed line
        y = 60 - j * 9
        add('cylinder', '8A90A0', (2.2, y, y * SLOPE + 0.45), radius=0.045, depth=1.1, vertices=5, parent=r)
        if j:
            ln = add('cylinder', 'FF7A1A', (0, 0, 0), radius=0.5, depth=1, vertices=4, parent=r, rough=0.7)
            span(ln, (2.2, y + 9, (y + 9) * SLOPE + 0.8), (2.2, y, y * SLOPE + 0.8), 0.028)
    for x, y, z, rad, dep, col in ((-230, 60, 40, 190, 230, '4A5066'), (-190, -150, 0, 170, 190, '555C72'), (-260, 240, 70, 210, 260, '454B5E')):
        add('cone', col, (x, y, z), rot=(0, 0, 0.5), radius1=rad, radius2=0, depth=dep, vertices=5, parent=r)                # the wall behind
        add('cone', 'DDE5F4', (x, y, z + dep * 0.33), rot=(0, 0, 0.5), radius1=rad * 0.34, radius2=0, depth=dep * 0.34, vertices=5, parent=r)
    box('CBD6EA', (0, -420, -118), (1400, 500, 6), r)                                                         # the glacier far below
    for j in range(7):
        add('cone', ('E3C22A', 'D8362A', '2D6FA8', 'F4F2EA')[j % 4], (-60 + j * 9 + 5 * rn(j, 255), -330 - 12 * rn(j, 256), -113), radius1=2.6, radius2=0,
            depth=3.4, vertices=4, parent=r)
    return out


_build0, _reset0 = build, reset
EXTRA_RIGS = ('young', 't1', 't2', 'boss', 'wife', 'boy1', 'boy2', 's3')


def build():
    S = _build0()
    for name, fn in (('ledge', set_ledge), ('hicamp', set_hicamp), ('room', set_room), ('alcove', set_alcove), ('slope', set_slope)):
        S['colls'][name], S[name] = stage(name, fn)
    S['young'] = K.Rig(dict(top='2A4A8A', pants='2A4A8A', hand='20242C', boot='8A2A2A'), climber(SKIN, '2A4A8A', hair='7A5A3A'))
    pack(S['young'], '5A3A2A', bottle=False)
    for nm, col in (('t1', 'E8E4D8'), ('t2', 'D86A90'), ('s3', '2E8A8A')):
        S[nm] = K.Rig(dict(top=col, pants=col, hand='20242C', boot='22262E'), climber('C99A78' if nm == 's3' else 'DDB494', col, hair='2A2422'))
        pack(S[nm], bottle=nm == 's3')
    S['boss'] = K.Rig(dict(top='3E5A4A', pants='2E323A', hand='DDB090', boot='22262E'), climber('DDB090', '3E5A4A', hair='5A5048', hood=False))
    add('cube', '3E5A4A', (0, 0.1, 1.2), scale=(0.9, 0.5, 0.3), size=1, parent=S['boss'].body)                 # a thick collar
    S['wife'] = K.Rig(dict(top='7A5A8A', pants='3A3F4C', hand='DDB494', boot='2A2420'), climber('DDB494', '7A5A8A', hair='5A3A28', hood=False))
    add('ico_sphere', '5A3A28', (0, 0.16, -0.1), scale=(0.95, 0.7, 1.2), radius=0.27, subdivisions=1, parent=S['wife'].head)
    for nm, col in (('boy1', '2D6FA8'), ('boy2', 'D8862A')):
        S[nm] = K.Rig(dict(top=col, pants='3A4252', hand='DDB494', boot='E8E4D8'), climber('DDB494', col, hair='8A6A44', hood=False))
    S['humans'] += list(EXTRA_RIGS)
    S['cast'] += [S[n] for n in EXTRA_RIGS]
    S['mitts'] = [add('ico_sphere', 'F4F2EA', (0, 0, -0.5), radius=0.14, subdivisions=1, parent=S['found'].hands[i]) for i in (0, 1)]
    S['bottle'] = bt = keep(empty(AWAY))
    add('cylinder', 'FF7A1A', (0, 0, 0.45), radius=0.13, depth=0.9, vertices=7, parent=bt, rough=0.4)
    add('cylinder', 'B8BCC8', (0, 0, 0.97), radius=0.05, depth=0.16, vertices=6, parent=bt, rough=0.3)
    S['crate'] = keep(add('cube', 'A8865A', AWAY, scale=(1.2, 0.9, 0.75), size=1))
    S['blanket'] = keep(add('cone', 'FF7A1A', AWAY, radius1=0.66, radius2=0.4, depth=1.0, vertices=8, rough=0.95))
    S['phone'] = keep(add('cube', 'E8E4D8', AWAY, scale=(0.13, 0.09, 0.36), size=1, rough=0.4))
    S['pad'] = pd = keep(empty(AWAY))
    add('cube', '3A3F4C', (0, 0, 0), scale=(0.4, 0.05, 0.54), size=1, parent=pd)
    add('cube', 'F4F0E2', (0, -0.03, 0), scale=(0.36, 0.03, 0.5), size=1, parent=pd)
    return S


def reset(S):
    _reset0(S)
    seen(S['mitts'], False)
    seen(S['house']['stars'], True)
    seen(S['alcove']['stars'], True)
    R = S['room']
    for nm in ('warm', 'moon', 'key'):
        R[nm].data.energy = 0


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


KNEEL = dict(lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76)


# ---------------------------------------------------------------- 1984
def top_two(S, k, t, lt):
    A = env(S, 'top', 'E89A70', sun=2.6, sunc='FFB070', sdir=(0.85, -0.3, 0.22), fk=2.2, skyk=0.9)
    ribbons(S, t)
    for who, x, ph in (('t1', -1.3, 0.0), ('t2', 0.3, 0.35)):
        gear(S, who, gog=True, mask=False)
        S[who].place(A(x, 0.3, 0), 0.25 * x)
        S[who].apply(blend(P('stand'), P('up', lift=0.06 * abs(math.sin(lt * 6 + ph * 5))), sm((lt - ph) / 0.4)))
    a = lerp(0.75, 0.35, k)
    shoot(S, A(-0.4 + 6.6 * math.sin(a), 0.4 - 6.6 * math.cos(a), lerp(0.8, 1.2, k)), A(-0.2, 0.6, 2.5), 30, fcol='FFD0A0')


def ledge_plume(S, t):
    for j, p in enumerate(S['ledge']['plume']):
        u = (t * 0.2 + j / 5) % 1
        p.location = (14 + u * 90, 138, 124 + 8 * u + 3 * math.sin(t * 2 + j))
        s = 0.6 + 2.0 * u
        p.scale = (s * 1.6, s * 0.6, s * 0.55)


def ledge_look(S, k, t, lt):
    A = env(S, 'ledge', '7FA8DC', sun=2.8, sunc='FFF0DC', sdir=(-0.6, -0.5, 0.55), fk=2.6, skyk=0.95)
    ledge_plume(S, t)
    y_ = S['young']
    gear(S, 'young', gog=False, mask=False)
    y_.place(A(0.9, -1.25, 0), PI)
    y_.apply(P('sit', lift=-0.3, lean=-0.12, head=(lerp(-0.2, -0.62, sm(lt / 0.8)), 0.0), aL=(0.7, 0.1, 1.0, 0.4), aR=(0.7, 0.1, 1.0, 0.4), lL=(1.4, 1.35),
               lR=(1.4, 1.35)))
    S['face']['young'] = 'tired'
    rp = (3.0, -1.9, 0.0)
    S['rook'].place(A(*rp), PI - 0.25)
    turn = sm((lt - 1.5) / 0.5)
    S['rook'].apply(P('cross', head=(lerp(-0.5, 0.05, turn), lerp(0.0, 1.0, turn))))
    S['face']['rook'] = 'calm' if turn < 0.5 else 'sad'
    shoot(S, A(lerp(4.8, 4.0, k), lerp(-8.8, -7.8, k), lerp(1.5, 1.8, k)), A(1.5, 14, lerp(7.6, 8.8, k)), 24, fill=1.3)


# ---------------------------------------------------------------- 2006: back again
def camp_arrive(S, k, t, lt):
    A = camp(S)
    plume(S, t)
    hang_bell(S, A, t, 0.25)
    gear(S, 'hall', gog=False, mask=False)
    y = lerp(-6.5, -3.4, k)
    S['hall'].place(A(-2.6, y, 0), PI + 0.08)
    S['hall'].apply(walk(lt, 1.25))
    rp = (0.7, -1.3, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (-1.5, -9.0)))
    S['rook'].apply(P('cross', head=(0.0, lerp(0.75, -0.3, k))))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.3
    shoot(S, A(lerp(-0.4, -0.9, k), lerp(-10.6, -9.6, k), 1.25), A(-1.0, 6, lerp(4.4, 5.4, k)), 24, fcol='FFE8D0')


def rook_clap(S, k, t, lt):
    A = env(S, 'top', '5E9AE6', sun=3.2, sunc='FFF4E0', sdir=(-0.5, -0.6, 0.6), fk=2.6)
    ribbons(S, t)
    gear(S, 'hall', gog=True, mask=False)
    S['hall'].place(A(1.2, 2.6, 0), 0.5)
    S['hall'].apply(P('up', lift=0.05 * abs(math.sin(lt * 6))))
    rp = (-2.4, 0.2, 0.0)
    cpos = (lerp(-3.4, -3.1, k), lerp(-4.0, -3.3, k))
    S['rook'].place(A(*rp), look_yaw(rp, cpos) + 0.25)
    clap = 0.35 * max(0.0, math.sin(lt * 5.2))
    S['rook'].apply(P('stand', aL=(0.9, 0.22 - clap * 0.5, 1.6, 0.9), aR=(0.9, 0.22 - clap * 0.5, 1.6, 0.9), head=(0.06, -0.25)))
    S['face']['rook'] = 'deadpan' if lt < 1.1 else 'warm'
    S['hat_tip'] = 0.4 * (1 - sm((lt - 1.0) / 0.3))
    shoot(S, A(cpos[0], cpos[1], 2.2), A(-1.6, 0.6, 2.45), 40)


# ---------------------------------------------------------------- the descent goes wrong
def halluc(S, k, t, lt):
    A = crest(S, 'gold', 0.28)
    gear(S, 'hall', gog=False, mask=False)
    S['hall'].place(A(0.7, 1.0, 0), PI / 2 + 0.3 * math.sin(lt * 1.3))
    S['hall'].apply(P('stand', lean=0.12, aR=(1.45 + 0.15 * math.sin(lt * 3), 0.25, 0.2), aL=(0.5, 0.5, 0.9), head=(-0.05, 0.25 * math.sin(lt * 2.2)),
                      lL=(0.1, 0.1), lR=(-0.1, 0.15)))
    S['face']['hall'] = 'wide'
    S['jaw']['hall'] = 0.25 * abs(math.sin(lt * 9))
    sp = (0.0, -0.5)
    S['s1'].place(A(sp[0], sp[1], 0), look_yaw(sp, (0.7, 1.0)))
    S['s1'].apply(P('stand', lean=0.15, aR=(1.2, 0.1, 0.4), aL=(1.0, 0.2, 0.6), head=(0.0, 0.0)))
    rp = (-0.5, 3.9, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (6.0, 1.0)))
    look = sm((lt - 0.5) / 0.4) * (1 - sm((lt - 1.5) / 0.3))
    S['rook'].apply(blend(P('stand', head=(0.0, 0.5)), P('hat', lean=0.3, head=(0.1, -0.7)), look))
    S['face']['rook'] = 'deadpan'
    shoot(S, A(lerp(7.2, 6.4, k), lerp(-3.4, -2.6, k), lerp(1.6, 1.9, k)), A(0.0, 1.0, 1.9), 32, fcol='FFDDB0')


def hall_refuse(S, k, t, lt):
    A = crest(S, 'gold', 0.42)
    gear(S, 'hall', gog=False, mask=False)
    d = sm(lt / 0.6)
    S['hall'].place(A(0.2, 0.9, 0), 0.0)
    S['hall'].apply(blend(P('stand', lean=0.3, head=(0.3, 0.0)), P('sit', lift=-0.72, lean=0.2, head=(0.35, 0.45 * math.sin(lt * 7)), aL=(0.5, -0.1, 1.7, 1.2),
                                                                  aR=(0.5, -0.1, 1.7, 1.2), lL=(1.35, 0.5), lR=(1.3, 0.6)), d))
    S['face']['hall'] = 'tired'
    pull = 0.5 + 0.5 * math.sin(lt * 4.5)
    sp = (0.5, -1.0)
    S['s1'].place(A(sp[0], sp[1] - 0.15 * pull, 0), look_yaw(sp, (0.2, 0.9)))
    S['s1'].apply(P('stand', lean=-0.1 - 0.2 * pull, aL=(1.1, 0.1, 0.4 + 0.4 * pull), aR=(1.1, 0.1, 0.4 + 0.4 * pull), lL=(0.3, 0.3), lR=(-0.25, 0.2)))
    S['s2'].place(A(-1.0, 2.3, 0), look_yaw((-1.0, 2.3), (0.2, 0.9)))
    S['s2'].apply(P('stand', lean=0.3, aL=(1.0, 0.2, 0.3), aR=(1.0, 0.2, 0.3), head=(0.25, 0.0)))
    rp = (-0.9, 4.2, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (3.0, 0.9)))
    S['rook'].apply(P('hips', head=(0.1, 0.2 * math.sin(lt * 1.6))))
    S['face']['rook'] = 'deadpan'
    shoot(S, A(lerp(7.4, 6.6, k), lerp(0.2, 1.2, k), lerp(1.2, 1.5, k)), A(0.0, 1.3, 1.6), 34, fcol='FFDDB0')


def drag_wide(S, k, t, lt):
    A = crest(S, 'gold', lerp(0.55, 0.7, k))
    gear(S, 'hall', gog=False, mask=True)
    pull = 0.5 + 0.5 * math.sin(lt * 5.0)
    y0 = 1.2 - 0.5 * k
    S['hall'].place(A(0.1, y0 - 0.2 * pull, 0.2), 0.0, -0.6 + 0.12 * pull)
    S['hall'].apply(P('sit', lift=-0.75, head=(0.5, 0.2), aL=(1.6, 0.5, 0.2), aR=(1.6, 0.5, 0.2), lL=(1.3, 0.3), lR=(1.2, 0.4)))
    S['face']['hall'] = 'shut'
    for who, x in (('s1', -0.9), ('s2', 0.9)):
        S[who].place(A(x, y0 - 1.5 - 0.2 * pull, 0), PI - 0.35 * x)
        S[who].apply(P('stand', lean=-0.25 - 0.2 * pull, aL=(1.0, 0.1, 0.5 + 0.5 * pull), aR=(1.0, 0.1, 0.5 + 0.5 * pull), lL=(0.35, 0.3), lR=(-0.3, 0.2)))
    S['rook'].place(A(-0.3, y0 + 1.7 - 0.2 * pull, 0), 0.0)
    S['rook'].apply(P('stand', lean=0.45 + 0.1 * pull, aL=(1.2, 0.15, 0.3), aR=(1.2, 0.15, 0.3), lL=(-0.4, 0.2), lR=(0.35, 0.5)))
    shoot(S, A(lerp(5.5, 4.0, k), lerp(-19, -16, k), lerp(11.0, 9.5, k)), A(0.0, 3.0, 0.5), 34, fill=0.6, fcol='FFD0A0')


def sherpa_spent(S, k, t, lt):
    A = crest(S, 'gold', 0.88)
    lying(S, A, 'hall', (0.2, 0.6), 0.25)
    gear(S, 'hall', gog=False, mask=True)
    br = math.sin(lt * 5.5)
    S['s1'].place(A(0.7, -2.3, 0), 0.5)
    S['s1'].apply(P('stand', lean=0.55 + 0.06 * br, aL=(0.75, 0.15, 0.2), aR=(0.75, 0.15, 0.2), head=(0.4, 0.0), **KNEEL))
    sway = 0.1 * math.sin(lt * 2.2)
    S['s2'].place(A(-0.7 + sway, -1.3, 0), -0.4, 0.0, sway)
    S['s2'].apply(P('stand', lean=0.6 + 0.05 * br, aL=(0.55, 0.2, 0.15), aR=(0.55, 0.2, 0.15), head=(0.3, 0.0), lL=(0.5, 0.5), lR=(0.5, 0.5), lift=-0.12))
    for i, who in enumerate(('s1', 's2')):
        lamp(S, i, S[who], 26)
    shoot(S, A(lerp(-2.4, -1.6, k), lerp(-6.8, -6.0, k), lerp(0.9, 1.2, k)), A(0.0, -1.2, 1.5), 34, fill=2.0, fcol='D8B8E0')


def boss_tent(S, lampk=1.0, door=60, skyc='1A1C2A'):
    A = env(S, 'radio', skyc, fk=0.5)
    R = S['radio']
    R['lamp'].data.energy = 420 * lampk
    R['door'].data.energy = door
    return A, R


def leader_order(S, k, t, lt):
    fl = 1 + 0.12 * math.sin(t * 17) + 0.08 * math.sin(t * 29)
    A, R = boss_tent(S, fl)
    R['needle'].rotation_euler = (0, 0.5 * math.sin(t * 13) + 0.3 * math.sin(t * 31), 0)
    b = S['boss']
    b.place(A(0.6, 0.0, 0), PI + 0.35)
    down = sm((lt - 1.2) / 0.5)
    b.apply(P('stand', lean=0.25 + 0.15 * down, aR=(lerp(1.15, 0.3, down), 0.25, lerp(2.0, 0.4, down), 0.5), aL=(1.0, 0.25, 0.25), head=(0.3 + 0.3 * down, 0.0)))
    S['face']['boss'] = 'sad'
    S['jaw']['boss'] = 0.25 * abs(math.sin(lt * 10)) * (1 - down)
    w = S['walkie']
    w.location = A(lerp(0.28, 0.2, down), lerp(0.34, 0.5, down), lerp(2.5, 1.45, down))
    w.rotation_euler = (0.3, 0, 0.5)
    shoot(S, A(lerp(-2.3, -1.9, k), lerp(2.75, 2.6, k), lerp(3.5, 3.3, k)), A(0.5, 0.1, 2.15), 28, fill=1.0, fcol='FFC890')


def leader_hears(S, k, t, lt):
    A, R = boss_tent(S, 0.5, 520, '9AB8E8')
    R['door'].data.color = K.hexc('DCE8FF')[:3]
    R['needle'].rotation_euler = (0, 0.6 * math.sin(t * 15), 0)
    b = S['boss']
    up = sm((lt - 0.35) / 0.3)
    b.place(A(0.3, 0.1, 0), PI - 0.2)
    b.apply(blend(P('sit', lift=-0.3, lean=0.4, head=(0.3, 0.0), aR=(1.2, 0.2, 2.0, 0.5), aL=(0.9, 0.2, 0.3), lL=(1.4, 1.4), lR=(1.4, 1.4)),
                  P('stand', lean=-0.1, head=(-0.15, 0.0), aR=(1.2, 0.25, 2.0, 0.5), aL=(0.3, 1.5, 1.9, -1.3)), up))
    S['face']['boss'] = 'wide' if up > 0.4 else 'tired'
    S['jaw']['boss'] = 0.3 * abs(math.sin(lt * 10)) * up
    S['crate'].location = A(0.3, -0.3, 0.37)
    w = S['walkie']
    w.location = A(-0.06, lerp(0.5, 0.3, up), lerp(2.1, 2.5, up))
    w.rotation_euler = (0.3, 0, -0.3)
    shoot(S, A(lerp(1.9, 1.6, k), 2.8, lerp(3.0, 3.1, k)), A(0.3, 0.1, lerp(2.0, 2.4, up)), 24, fill=1.6, fcol='FFE0C0')


def phone_room(S, k, t, lt):
    A = env(S, 'room', '05070F', fk=0.6)
    R = S['room']
    R['warm'].data.energy = 520
    R['moon'].data.energy = 160
    R['key'].data.energy = 260
    w = S['wife']
    down = sm((lt - 0.5) / 0.6)
    w.place(A(-2.2, 0.9, 0), -0.35)
    w.apply(P('stand', lean=0.08 * down, head=(0.38 * down, -0.2), aR=(lerp(0.9, 0.2, down), 0.2, lerp(2.2, 0.3, down), 0.5), aL=(lerp(0.2, 0.9, down), 0.1,
                                                                                                                         lerp(0.3, 2.1, down), 0.9)))
    S['face']['wife'] = 'sad'
    S['phone'].location = A(lerp(-2.05, -1.72, down), lerp(0.62, 0.72, down), lerp(2.6, 1.1, down))
    S['phone'].rotation_euler = (0.2, 0, -0.35)
    for i, (who, x, sc) in enumerate((('boy1', 2.6, 0.74), ('boy2', 4.2, 0.62))):
        b = S[who]
        b.root.scale = (sc, sc, sc)
        b.place(A(x, 2.75, 0.16), 0.0)
        b.apply(P('sit', lift=-0.42, lean=0.1 + 0.12 * down, head=(0.05, -0.75 - 0.12 * i), aL=(0.6, 0.1, 0.9, 0.5), aR=(0.6, 0.1, 0.9, 0.5), lL=(1.45, 1.5),
                  lR=(1.45, 1.5)))
        S['face'][who] = 'wide'
    shoot(S, A(lerp(0.8, 0.5, k), lerp(-7.4, -6.2, k), lerp(2.5, 2.3, k)), A(0.6, 1.4, 1.9), 36, fill=0.7, fcol='FFD8B0')


# ---------------------------------------------------------------- the night
def night_wide(S, k, t, lt):
    A = crest(S, 'night')
    lying(S, A, 'hall', (0.2, 0.6), 0.25)
    gear(S, 'hall', gog=False, mask=False)
    seen(S['hall'].extra['frost'], True)
    rp = (-0.9, -1.3, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.2, 0.9)))
    S['rook'].apply(P('sit', lift=-0.62, head=(0.3, 0.0), lL=(1.3, 1.2), lR=(1.3, 1.2)))
    S['face']['rook'] = 'sad'
    S['lamps'][0].location = A(0.5, 0.0, 4.0)
    S['lamps'][0].data.energy = 2600
    S['lamps'][0].data.color = K.hexc('9DB8FF')[:3]
    shoot(S, A(lerp(25, 21, k), lerp(-19, -16, k), lerp(4.0, 5.0, k)), A(0, 5, 3.6), 40, fill=0.0)


def rook_watch(S, k, t, lt):
    A = crest(S, 'night')
    lying(S, A, 'hall', (0.2, 0.6), 0.25)
    gear(S, 'hall', gog=False, mask=False)
    seen(S['hall'].extra['frost'], True)
    rp = (-0.9, -1.3, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (2.2, -4.2)))
    up = sm((lt - 1.3) / 0.6)
    S['rook'].apply(P('sit', lift=-0.62, lean=0.2, head=(lerp(0.3, -0.3, up), lerp(-0.55, 0.15, up)), lL=(1.3, 1.2), lR=(1.3, 1.2), aL=(0.7, 0.0, 1.3, 0.8),
                      aR=(0.7, 0.0, 1.3, 0.8)))
    S['face']['rook'] = 'sad'
    S['hat_tip'] = 0.3
    S['lamps'][0].location = A(1.2, -3.2, 2.6)
    S['lamps'][0].data.energy = 220
    S['lamps'][0].data.color = K.hexc('9DB8FF')[:3]
    shoot(S, A(lerp(1.9, 1.5, k), lerp(-4.6, -4.0, k), lerp(1.5, 1.7, k)), A(-0.6, -0.9, 1.75), 42, fill=3.0, fcol='9DB8FF')


def first_light(S, k, t, lt):
    g = sm(k)
    A = crest(S, 'sunrise', lerp(0.0, 0.55, g), sun_at=(700, 150))
    seen(S['crest']['stars'], g < 0.55)
    seated(S, A, nod=lerp(0.6, 0.08, sm((lt - 0.9) / 0.9)), lean=lerp(0.45, 0.12, sm((lt - 0.9) / 0.9)), face='shut' if lt < 1.3 else 'tired')
    rp = (-0.4, -3.0, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.5, 0.0)))
    wake = sm((lt - 1.4) / 0.2)
    S['rook'].apply(blend(P('sit', lift=-0.62, head=(0.55, 0.0), lL=(1.3, 1.2), lR=(1.3, 1.2)),
                          P('sit', lift=-0.5, lean=-0.1, head=(-0.1, 0.0), lL=(1.3, 1.2), lR=(1.3, 1.2), aL=(0.7, 1.0, 1.4, -0.6), aR=(0.7, 1.0, 1.4, -0.6)), wake))
    S['face']['rook'] = 'shocked' if wake > 0.5 else 'shut'
    S['hat_tip'] = 1.0 - wake
    shoot(S, A(lerp(-8.6, -7.4, k), lerp(-4.4, -3.6, k), lerp(1.2, 1.6, k)), A(0.2, -0.4, 1.8), 34, fill=lerp(0.5, 1.0, g), fcol='C8B8F0')


# ---------------------------------------------------------------- the four climbers
def summit_way(S, k, t, lt):
    A = crest(S, 'sunrise', 0.62)
    y0 = lerp(-9.0, -6.6, k)
    team(S, A, y0, lt)
    for i, who in enumerate(('m1', 'm2', 'm3', 'm4')):
        lamp(S, i, S[who], 22)
    shoot(S, A(lerp(1.9, 1.5, k), y0 - 9.5, lerp(2.3, 2.6, k)), A(-0.1, y0 + 6, 3.6), 28, fcol='FFD0B0')


NAME_AT = ((-0.2, -6.0), (0.55, -7.9), (-0.6, -9.8), (0.35, -11.7))


def _name(S, k, t, lt, side):
    A = crest(S, 'sunrise', 0.85)
    i = int(S['prm'].get('who', 0))
    order = [('m1', 'm2', 'm3', 'm4')[i]] + [w for j, w in enumerate(('m1', 'm2', 'm3', 'm4')) if j != i]
    for j, w in enumerate(order):
        x, y = NAME_AT[j]
        S[w].place(A(x, y, 0), PI + 0.12 * side)
        S[w].apply(P('stand', lean=0.1, head=(0.05, 0.25 * math.sin(lt * 1.4 + j * 2)), aL=(0.2, 0.3, 0.4), aR=(0.2, 0.3, 0.4)))
    who = order[0]
    x, y = NAME_AT[0]
    u = sm(lt / 0.5)
    if i == 0:                                                    # the guide pushes his goggles up
        S[who].apply(blend(P('stand'), P('stand', aR=(0.2, 1.7, 1.75, -1.4), head=(-0.05, 0.0)), u))
        seen(S[who].extra['gog'], u < 0.6)
    elif i == 1:                                                  # hands on knees, getting his breath, then looks up
        S[who].apply(blend(P('stand', lean=0.55, aL=(0.6, 0.15, 0.15), aR=(0.6, 0.15, 0.15), head=(0.3, 0.0), lL=(0.4, 0.4), lR=(0.4, 0.4), lift=-0.1),
                           P('stand', lean=0.2, head=(-0.1, 0.0), aL=(0.3, 0.3, 0.5), aR=(0.3, 0.3, 0.5)), sm((lt - 0.5) / 0.5)))
    elif i == 2:                                                  # tightens a pack strap
        S[who].apply(P('stand', aL=(0.6, -0.1, 1.9, 0.9), aR=(0.6, -0.1, 1.9 + 0.2 * math.sin(lt * 9), 0.9), head=(0.2 - 0.25 * u, 0.0)))
    else:                                                         # looks up the ridge and points
        S[who].apply(blend(P('stand'), P('point', aR=(1.9, 0.1, 0.1), head=(-0.2, 0.0)), u))
    seen(S[who].extra['mask'], False)
    S['face'][who] = 'calm'
    shoot(S, A(x + side * lerp(2.9, 2.3, k), y + lerp(3.6, 3.2, k), 2.45), A(x, y, 2.4), 46, fcol='FFD8B8')


def name_a(S, k, t, lt):
    _name(S, k, t, lt, 1)


def name_b(S, k, t, lt):
    _name(S, k, t, lt, -1)


def sit_back(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0, sun_at=(740, 60))
    seated(S, A, turn=0.1 * math.sin(lt * 1.5), nod=0.1)
    rp = (0.9, 2.7, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (6.0, 2.2)))
    peer = sm((lt - 0.4) / 0.5)
    S['rook'].apply(blend(P('stand', head=(0.0, 0.6)), P('stand', lean=0.5, head=(0.35, 0.0), aL=(0.2, 0.5, 0.5), aR=(0.2, 0.5, 0.5), lL=(-0.2, 0.0), lR=(0.3, 0.4)), peer))
    S['face']['rook'] = 'shocked' if peer > 0.8 else 'deadpan'
    shoot(S, A(lerp(-5.2, -4.2, k), lerp(-1.6, -0.6, k), lerp(3.4, 3.0, k)), A(2.6, 0.9, 0.2), 26, fill=1.5, fcol='FFD8B8')


def suit_open(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    fid = 0.2 * math.sin(lt * 3.2)
    seated(S, A, turn=0.2, nod=0.3, aL=(0.75 + fid, 0.2, 1.35, 0.6), aR=(0.75 - fid, 0.2, 1.35, 0.6))
    shoot(S, A(lerp(2.2, 1.5, k), lerp(-4.6, -4.2, k), lerp(1.0, 1.2, k)), A(0.65, 0.0, 1.3), 46, fcol='FFD8B8')


def rook_note(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=-0.9, nod=0.0, face='calm')
    rp = (-1.0, -2.2, 0.0)
    cpos = (lerp(-2.2, -1.8, k), lerp(-5.6, -5.0, k))
    S['rook'].place(A(*rp), look_yaw(rp, cpos) - 0.15)
    tap = sm((lt - 1.5) / 0.3)
    wr = 0.1 * math.sin(lt * 14) * (1 - tap)
    S['rook'].apply(blend(P('stand', aL=(1.0, -0.1, 1.35, 0.7), aR=(0.95 + wr, -0.05, 1.5, 0.75), head=(0.35, 0.0)),
                          P('stand', aL=(1.0, -0.1, 1.35, 0.7), aR=(1.0, 0.1, 2.35, 0.9), head=(-0.05, 0.1 * math.sin(lt * 9))), tap))
    S['face']['rook'] = 'calm' if tap < 0.5 else 'warm'
    pd = S['pad']
    pd.parent = S['rook'].root
    pd.location = (-0.26, -0.5, 1.62)
    pd.rotation_euler = (-0.9, 0, 0.2)
    pd.scale = (0.75, 0.75, 0.75)
    shoot(S, A(cpos[0], cpos[1], 2.1), A(-0.6, -2.0, 2.3), 38, fill=1.5, fcol='FFD8B8')


def hall_dazed(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=-0.4 + 0.5 * math.sin(lt * 1.7), nod=0.15 + 0.15 * math.sin(lt * 2.6), lean=0.1 + 0.08 * math.sin(lt * 1.3), face='tired')
    S['jaw']['found'] = 0.15 * abs(math.sin(lt * 6))
    p1 = (1.2, -1.45)
    S['m1'].place(A(p1[0], p1[1], 0), look_yaw(p1, (0.6, 0.0)))
    S['m1'].apply(P('stand', lean=0.3, aL=(0.4, 0.1, 0.6), aR=(1.2, 0.0, 0.25), head=(0.1, 0.0), **KNEEL))
    seen(S['m1'].extra['gog'], False)
    S['face']['m1'] = 'wide'
    shoot(S, A(lerp(4.2, 3.7, k), lerp(2.2, 1.6, k), lerp(1.9, 1.7, k)), A(0.8, -0.4, 1.7), 50, fcol='FFD8B8')


def boat_look(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0, sun_at=(720, -140))
    rock = math.sin(lt * 1.7)
    seated(S, A, turn=0.25 * rock, nod=0.0, lean=0.1 + 0.06 * rock, face='tired', aR=(0.9, 0.5, 0.6, 0.2))
    rp = (1.25, 2.9, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (8.0, 2.0)))
    back = sm((lt - 1.3) / 0.4)
    S['rook'].apply(blend(P('hat', lean=0.4, head=(0.3, 0.0)), P('shrug', head=(0.0, 1.3)), back))
    S['face']['rook'] = 'deadpan'
    shoot(S, A(-2.6, lerp(-1.4, -0.9, k), 2.7 + 0.12 * rock), A(14, 1.2, -4.5), 26, roll=0.1 * rock, fill=1.4, fcol='FFD8B8')


def four_think(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=-0.6, nod=0.1)
    c = (0.0, -4.4)
    for i, (who, x, y) in enumerate((('m1', -0.7, -3.4), ('m2', 0.9, -3.7), ('m3', -0.9, -5.2), ('m4', 0.75, -5.5))):
        S[who].place(A(x, y, 0), look_yaw((x, y), c))
        S[who].apply(P('stand', lean=0.1, head=(0.1 * math.sin(lt * 1.2 + i), 0.5 * math.sin(lt * 1.5 + i * 1.7)), aL=(0.2, 0.3, 0.4),
                       aR=(0.3 + 0.5 * (i == 1), 0.3, 0.4 + 0.9 * (i == 1))))
        seen(S[who].extra['mask'], False)
    seen(S['m1'].extra['gog'], False)
    a = lerp(1.9, 2.5, k)
    shoot(S, A(c[0] + 6.0 * math.sin(a), c[1] - 6.0 * math.cos(a), lerp(2.3, 2.6, k)), A(0.0, -4.3, 2.1), 30, fcol='FFD8B8')


def look_back(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=1.0, nod=0.05, face='tired')
    turn = sm((lt - 0.3) / 0.6)
    S['m1'].place(A(-1.3, 5.2, 0), lerp(PI, -0.25, turn))
    S['m1'].apply(P('stand', head=(lerp(-0.3, 0.25, turn), 0.0), aL=(0.2, 0.3, 0.4), aR=(0.2, 0.3, 0.4)))
    seen(S['m1'].extra['gog'], False)
    seen(S['m1'].extra['mask'], False)
    for who, (x, y) in (('m2', (1.3, -1.6)), ('m4', (-1.0, -1.5))):
        S[who].place(A(x, y, 0), look_yaw((x, y), (0.5, 0.0)))
        S[who].apply(P('stand', lean=0.3, aL=(0.9, 0.2, 0.6), aR=(0.9, 0.2, 0.6), **KNEEL))
    rp = (-0.9, 1.7, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (-1.3, 5.2)))
    S['hat_off'] = 1.0
    S['rook'].apply(to_chest(head=(-0.1, 0.0)))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(-0.4, 0.0, k), lerp(9.0, 8.4, k), lerp(3.5, 3.3, k)), A(0.3, 0.6, 1.3), 30, fill=1.3, fcol='FFD8B8')


# ---------------------------------------------------------------- earlier that month (the alcove is shown empty)
def alcove(S, pre=0.0):
    A = env(S, 'alcove', mixc('060A1E', '2A3470', pre), sun=lerp(0.35, 0.9, pre), sunc='9DB8FF', sdir=(-0.3, -0.5, 0.8), fk=lerp(1.0, 1.6, pre))
    return A


def alcove_wide(S, k, t, lt):
    A = alcove(S)
    S['lamps'][0].location = A(0, -2.5, 4.5)
    S['lamps'][0].data.energy = 2200
    S['lamps'][0].data.color = K.hexc('8FA4E8')[:3]
    shoot(S, A(lerp(-5.0, -2.0, k), lerp(-13.5, -10.0, k), lerp(2.6, 2.0, k)), A(0, 3.0, 1.8), 30, fill=1.6, fcol='8FA4E8')


def alcove_pass(S, k, t, lt):
    A = alcove(S)
    for i, who in enumerate(('s3', 't1', 't2', 'young')):
        x = lerp(-9.5, -1.5, k) - i * 2.6 + 6.0
        S[who].place(A(x, -1.6 - 0.25 * (i % 2), 0), -PI / 2)
        w = walk(lt + i * 0.3, 0.9)
        w.update(TRUDGE)
        S[who].apply(w)
        gear(S, who)
        lamp(S, i, S[who], 30)
    shoot(S, A(lerp(0.9, 0.3, k), 4.9, lerp(1.5, 1.7, k)), A(0.0, -2.0, 1.9), 22, fill=0.25, fcol='8FA4E8')


def rook_alcove(S, k, t, lt):
    A = alcove(S, 0.7)
    rp = (0.6, -1.3, 0.0)
    S['rook'].place(A(*rp), PI)
    S['hat_off'] = sm(lt / 0.5)
    S['rook'].apply(blend(P('stand'), to_chest(head=(0.3, 0.0)), lt / 0.5))
    S['face']['rook'] = 'sad'
    shoot(S, A(lerp(-1.2, -0.6, k), lerp(4.6, 3.8, k), lerp(1.7, 1.9, k)), A(0.5, -1.3, 2.2), 34, fill=2.2, fcol='A8B8F0')


# ---------------------------------------------------------------- they stay
def kneel_round(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    seated(S, A, turn=-0.5, nod=0.1)
    for i, (who, x, y) in enumerate((('m1', 1.3, -1.5), ('m2', -0.9, -1.6), ('m4', -1.0, 1.3), ('m3', 0.6, -3.2))):
        far = (x * 1.2, y - 2.6) if y < 0 else (x, y + 2.6)
        u = sm((lt - 0.15 * i) / 0.7)
        px, py = lerp(far[0], x, u), lerp(far[1], y, u)
        S[who].place(A(px, py, 0), look_yaw((px, py), (0.5, 0.0)))
        S[who].apply(blend(walk(lt + i * 0.2, 1.6), P('stand', lean=0.3, aL=(0.9, 0.2, 0.7), aR=(0.9, 0.2, 0.7), **(KNEEL if i < 3 else {})), sm((lt - 0.5 - 0.15 * i) / 0.4)))
    rp = (0.3, 3.6, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.5, 0.0)))
    S['hat_off'] = 1.0
    S['rook'].apply(to_chest(head=(0.2, 0.0)))
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(1.6, 1.0, k), lerp(-3.4, -2.6, k), lerp(13.0, 11.0, k)), A(0.4, -0.2, 0.0), 30, roll=lerp(-0.25, 0.1, k), fcol='FFD8B8')


def oxygen(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    f = seated(S, A, turn=0.55, nod=-0.05, face='shut' if (lt * 0.8) % 1 < 0.5 else 'tired')
    seen(f.extra['mask'], True)
    p2 = (1.25, 1.5)
    S['m2'].place(A(p2[0], p2[1], 0), look_yaw(p2, (0.6, 0.1)))
    S['m2'].apply(P('stand', lean=0.3, aL=(1.25, 0.0, 0.3), aR=(0.7, 0.1, 0.7), head=(0.1, 0.0), **KNEEL))
    seen(S['m2'].extra['mask'], False)
    bt = S['bottle']
    bt.location = A(1.45, 0.55, 0.0)
    bt.rotation_euler = (0.0, 0.25, 0.3)
    span(S['line'], A(1.42, 0.55, 1.0), A(0.9, 0.2, 1.72), 0.02)
    p4 = (-1.0, 1.4)
    S['m4'].place(A(p4[0], p4[1], 0), look_yaw(p4, (0.5, 0.0)))
    S['m4'].apply(P('stand', lean=0.35, aL=(1.0, 0.1, 0.7), aR=(1.0, 0.1, 0.7), head=(0.3, 0.0)))
    shoot(S, A(lerp(4.4, 3.9, k), lerp(-2.2, -1.6, k), lerp(1.5, 1.7, k)), A(0.9, 0.5, 1.65), 46, fcol='FFD8B8')


def radio_call(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    m = S['m1']
    m.place(A(-0.5, -3.2, 0), 0.25)
    pt = sm((lt - 0.6) / 0.3)
    m.apply(P('stand', aR=(1.15, 0.25, 2.0, 0.5), aL=(lerp(0.2, -0.9, pt), lerp(0.3, 0.9, pt), 0.2), head=(0.1, -0.2)))
    seen(m.extra['gog'], False)
    seen(m.extra['mask'], False)
    S['jaw']['m1'] = 0.28 * abs(math.sin(lt * 11))
    w = S['walkie']
    w.location = A(-0.42, -3.72, 2.56)
    w.rotation_euler = (0.3, 0, 0.6)
    shoot(S, A(lerp(1.2, 0.7, k), lerp(-7.2, -6.6, k), lerp(1.2, 1.5, k)), A(-0.4, -3.0, 2.5), 34, fcol='FFD8B8')


def wait_four(S, k, t, lt):
    A = crest(S, 'sunrise', 1.0)
    C = S['crest']
    g = sm(k)
    sky(S, mixc('F4A468', '6FA6E4', g), 1.0)
    C['sun'].location = (760 - 260 * g, 120 - 300 * g, lerp(-8, 330, g))
    paint(C['sunm'], mixc('FFE2A8', 'FFF8E8', g), 9)
    S['sun'].location = A(lerp(0.9, 0.5, g) * 400, lerp(0.12, -0.45, g) * 400, lerp(0.34, 0.85, g) * 400)
    S['sun'].data.color = K.hexc(mixc('FFC090', 'FFF4E0', g))[:3]
    seated(S, A, turn=-0.5 + 0.2 * math.sin(lt * 1.2), nod=0.1, face='calm')
    for i, (who, x, y) in enumerate((('m1', 1.3, -1.5), ('m2', -0.9, -1.6), ('m4', -1.0, 1.3), ('m3', 0.6, -3.0))):
        S[who].place(A(x, y, 0), look_yaw((x, y), (0.5, 0.0)))
        S[who].apply(P('sit', lift=-0.66, lean=0.15, head=(0.15, 0.3 * math.sin(lt * 1.1 + i * 2)), lL=(1.3, 1.2), lR=(1.3, 1.2), aL=(0.7, 0.0, 1.3, 0.8),
                       aR=(0.7, 0.0, 1.3, 0.8)))
        seen(S[who].extra['gog'], False)
        seen(S[who].extra['mask'], False)
    S['cup'].location = A(1.0, -0.72, 1.3)
    rp = (0.3, 3.2, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.5, 0.0)))
    S['rook'].apply(P('sit', lift=-0.62, head=(0.2, 0.3 * math.sin(lt * 0.9)), lL=(1.3, 1.2), lR=(1.3, 1.2)))
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(15, 12.5, k), lerp(-13, -11, k), lerp(5.5, 4.6, k)), A(0.0, 0.2, 1.4), 40, fcol='FFE8D0')


# ---------------------------------------------------------------- the way down
def hicamp_ground(y):
    return max(0.0, y * math.tan(0.5) - 0.8)


def hicamp_go(S, k, t, lt):
    A = env(S, 'hicamp', '8EB4EA', sun=3.0, sunc='FFF0DC', sdir=(-0.6, -0.5, 0.5), fk=2.4)
    for i, who in enumerate(('s1', 's2', 's3')):
        u = lerp(0.3, 0.52, k) - i * 0.17
        x, y = lerp(-3.4, 3.6, u), lerp(-3.6, 12.0, u)
        S[who].place(A(x - (i % 2) * 0.5, y, hicamp_ground(y)), look_yaw((0, 0), (7.0, 15.6)))
        w = walk(lt + i * 0.3, 1.35)
        w.update(lean=0.32, head=(-0.1, 0.0))
        S[who].apply(w)
        gear(S, who, gog=True, mask=False)
    shoot(S, A(lerp(-9.5, -8.5, k), lerp(-5.2, -4.6, k), lerp(1.3, 1.6, k)), A(0.6, 2.4, lerp(2.6, 3.2, k)), 28)


def slope_down(S, k, t, lt):
    A = env(S, 'slope', '7FAEE8', sun=3.1, sunc='FFF4E0', sdir=(0.5, -0.5, 0.7), fk=2.4)
    y0 = lerp(9.0, 4.0, k)

    def put(who, x, dy, ph, **over):
        y = y0 + dy
        S[who].place(A(x, y, y * SLOPE), 0.0)
        w = walk(lt + ph, 1.0)
        w.update(over)
        S[who].apply(w)
    put('s3', 0.6, -6.2, 0.4)
    put('found', 0.5, 0.0, 0.0, aL=(0.5, 1.2, 0.3), aR=(0.5, 1.2, 0.3), lean=0.2, head=(0.3, 0.0))
    put('s1', -0.5, 0.1, 0.2, aR=(0.6, 0.9, 0.9))
    put('s2', 1.5, 0.1, 0.5, aL=(0.6, 0.9, 0.9))
    put('m4', 0.4, 4.0, 0.7)
    put('rook', -0.2, 7.6, 0.1)
    S['face']['found'] = 'tired'
    S['face']['rook'] = 'warm'
    for who in ('s1', 's2', 's3', 'm4'):
        gear(S, who, gog=True, mask=False)
    shoot(S, A(lerp(20, 17, k), y0 - 7.5, (y0 - 7.5) * SLOPE + lerp(4.0, 3.2, k)), A(0.3, y0 + 0.5, (y0 + 0.5) * SLOPE + 2.2), 38)


def camp_rest(S, k, t, lt):
    A = camp(S, dawn=True)
    hang_bell(S, A, t, 0.1)
    f = S['found']
    seen(f.extra['frost'], False)
    seen(S['mitts'], True)
    S['crate'].location = A(-2.3, -1.4, 0.37)
    f.place(A(-2.3, -1.25, 0), 0.25)
    f.apply(P('sit', lift=-0.28, lean=0.22, head=(0.2, -0.3 + 0.1 * math.sin(lt * 1.5)), aL=(0.75, 0.0, 1.25, 0.7), aR=(0.75, 0.0, 1.25, 0.7), lL=(1.4, 1.35),
              lR=(1.4, 1.35)))
    S['face']['found'] = 'warm'
    bl = S['blanket']
    bl.parent = f.body
    bl.location = (0, 0.03, 0.62)
    rp = (-0.5, -1.9, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (-2.3, -1.25)))
    give = sm((lt - 0.4) / 0.5)
    S['rook'].apply(P('stand', aR=(lerp(0.3, 1.2, give), 0.1, lerp(0.9, 0.3, give)), aL=(0.1, 0.15, 0.2), head=(0.15, 0.0)))
    S['face']['rook'] = 'warm'
    S['cup'].location = A(lerp(-0.75, -1.35, give), lerp(-2.2, -1.75, give), lerp(1.45, 1.75, give))
    shoot(S, A(lerp(1.0, 0.4, k), lerp(-7.6, -6.6, k), lerp(1.7, 1.9, k)), A(-1.5, -1.3, 1.9), 34, fcol='FFE0D0')


def home_day(S, k, t, lt):
    A = env(S, 'house', '8EC0F0', sun=3.0, sunc='FFF4E0', sdir=(0.4, -0.7, 0.6), fk=2.4)
    Hs = S['house']
    seen(Hs['stars'], False)
    paint(Hs['winm'], 'BFD8F0', 0.6)
    h_ = S['home']
    y = lerp(-11.5, -7.0, k)
    h_.place(A(0.0, y, 0), PI)
    h_.apply(walk(lt, 1.2))
    w = S['wife']
    w.place(A(0.9, 1.4, 0.24), 0.0)
    w.apply(blend(P('stand'), P('stand', aL=(0.9, 0.9, 0.5), aR=(0.9, 0.9, 0.5), head=(-0.05, 0.0)), sm(lt / 0.6)))
    S['face']['wife'] = 'warm'
    for i, (who, sc, y0) in enumerate((('boy1', 0.74, 0.2), ('boy2', 0.62, 1.0))):
        b = S[who]
        b.root.scale = (sc, sc, sc)
        yy = y0 - (2.6 + i * 0.4) * max(0.0, lt - 0.2 - 0.25 * i)
        b.place(A(-0.5 + i * 0.9, max(yy, y + 2.0 + i), 0.24 if yy > 0.6 else 0.0), 0.0)
        b.apply(walk(lt + i * 0.2, 2.3) if yy > y + 2.0 + i else P('up', aL=(1.6, 0.4, 0.3), aR=(1.6, 0.4, 0.3)))
        S['face'][who] = 'wide'
    shoot(S, A(lerp(3.4, 2.6, k), lerp(-16.5, -14.5, k), lerp(2.0, 2.4, k)), A(0.3, -1.0, 2.3), 32, fill=0.8)


def desk_empty(S, k, t, lt):
    A = env(S, 'study', '2A2018', fk=1.2)
    St = S['study']
    St['key'].data.energy = 1500
    St['key'].data.color = K.hexc('FFC890')[:3]
    St['warm'].data.energy = 420
    S['book'].location = A(0.95, -1.15, 1.66)
    S['book'].rotation_euler = (PI / 2, 0, 0.3)
    St['pen'].location = (-0.3, -1.1, 1.64)
    St['pen'].rotation_euler = (PI / 2, 0, 0.9)
    a = lerp(-0.75, -0.35, k)
    shoot(S, A(0.2 + 5.2 * math.sin(a), -0.6 - 5.2 * math.cos(a), lerp(2.9, 2.6, k)), A(0.3, -0.6, 1.8), 36, fill=1.6, fcol='FFE0C0')


# ---------------------------------------------------------------- the end
def rook_ridge(S, k, t, lt):
    A = crest(S, 'sunrise', 0.9, sun_at=(700, 330))
    seen(S['crest']['hollow'], True)
    rp = (-0.8, -1.2, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (0.3, 0.0)))
    up = sm((lt - 1.0) / 0.5)
    S['rook'].apply(blend(P('stand', lean=0.25, head=(0.4, 0.0), aL=(0.1, 0.15, 0.2), aR=(0.1, 0.15, 0.2)), P('hat', head=(-0.05, -0.9)), up))
    S['face']['rook'] = 'calm' if up < 0.5 else 'warm'
    shoot(S, A(lerp(-5.4, -4.6, k), lerp(-5.6, -4.8, k), lerp(1.3, 1.6, k)), A(-0.2, -0.2, 2.0), 30, fill=1.8, fcol='FFD0B0')


def four_down(S, k, t, lt):
    A = crest(S, 'day')
    y0 = lerp(-2.0, -5.0, k)
    for i, who in enumerate(('m1', 'm2', 'm3', 'm4')):
        S[who].place(A(0.35 * (-1 if i % 2 else 1) - 0.2, y0 + i * 2.0, 0), 0.0)
        S[who].apply(walk(lt + i * 0.27, 1.05))
        seen(S[who].extra['mask'], False)
    S['rook'].place(A(-0.9, y0 + 9.0, 0), 0.0)
    wr = walk(lt + 0.15, 1.2)
    wr['head'] = (0.0, 2.4 * sm((lt - 0.8) / 0.4) * (1 - sm((lt - 1.8) / 0.4)))
    S['rook'].apply(wr)
    S['face']['rook'] = 'warm'
    shoot(S, A(lerp(3.6, 3.0, k), y0 - 5.0, lerp(1.2, 1.5, k)), A(-0.2, y0 + 4, 3.2), 26)


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: sunrise, he sits on the lip of the crest with a hand lifted; behind him Rook jumps."""
    A = crest(S, 'sunrise', 1.0, sun_at=(640, 420))
    seated(S, A, turn=-0.95, nod=0.0, face='calm', aL=(1.1, 0.8, 1.6, 0.25))
    rp = (-0.3, 2.6, 0.0)
    S['rook'].place(A(*rp), look_yaw(rp, (3.0, -4.0)))
    S['rook'].apply(P('stand', **STARTLE))
    S['face']['rook'] = 'shocked'
    shoot(S, A(5.4, -5.2, 1.8), A(3.0, -1.5, 1.75), 34, fill=1.4, fcol='FFD8B8')


def sun_ridge(S, k, t, lt):
    """The long version opens on a faster move than the Short: the sun clears the horizon while the camera swings in along the crest."""
    g = sm(lt / 1.3)
    A = crest(S, 'sunrise', 0.15 + 0.85 * g, sun_at=(690, 250))
    seated(S, A)
    shoot(S, A(lerp(-19.0, -9.5, g) - 1.0 * k, lerp(-12.0, -4.6, g), lerp(0.5, 1.3, g)), A(0.3, 0.4, lerp(3.4, 1.9, g)), 34, fill=0.5, fcol='FFC8A0')


SHOTS3D['sun_ridge'] = sun_ridge
HOST |= {'ledge_look', 'camp_arrive', 'rook_clap', 'halluc', 'hall_refuse', 'drag_wide', 'night_wide', 'rook_watch', 'first_light', 'sit_back', 'rook_note',
         'boat_look', 'look_back', 'rook_alcove', 'kneel_round', 'wait_four', 'slope_down', 'camp_rest', 'rook_ridge', 'four_down'}
SHOTS3D.update({f.__name__: f for f in (
    top_two, ledge_look, camp_arrive, rook_clap, halluc, hall_refuse, drag_wide, sherpa_spent, leader_order, leader_hears, phone_room, night_wide,
    rook_watch, first_light, summit_way, name_a, name_b, sit_back, suit_open, rook_note, hall_dazed, boat_look, four_think, look_back, alcove_wide,
    alcove_pass, rook_alcove, kneel_round, oxygen, radio_call, wait_four, hicamp_go, slope_down, camp_rest, home_day, desk_empty, rook_ridge, four_down)})


def _with_orbit(f):
    def g(S, k, t, lt):
        f(S, k, t, lt)
        cam_orbit(S, k)
    g.__name__ = f.__name__
    return g


SHOTS3D = {name: _with_orbit(f) for name, f in SHOTS3D.items()}
STILLS['thumb'] = photo_thumb
