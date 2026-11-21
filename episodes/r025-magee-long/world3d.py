"""Case 025 in 3D - Alan Magee, 1943. On 3 January 1943 the B-17 "Snap! Crackle! Pop!" of the 303rd Bomb Group
was hit by flak over Saint-Nazaire in daylight. Its ball turret gunner, Staff Sergeant Alan Magee, climbed out of
his wrecked turret and found his parachute torn to rags. Short of oxygen, he blacked out and was thrown clear of
the aircraft, fell about 22,000 feet and crashed through the glass roof of the Saint-Nazaire railway station,
which broke his fall. Found alive with 28 shrapnel wounds and a badly injured arm, he was treated by a German
military doctor and spent the rest of the war as a prisoner. Seven of the ten men on board were killed; in 1993
the town put up a memorial to the crew.

Built for this story only: a daylight sky over the coast with a four-engined bomber, a formation and flak; the
inside of a ball turret; the waist of the fuselage with the parachute hook and the turret hatch; an arched
railway station of glass and iron in a harbour town; a hospital room; a wire fence in the snow; and a town square
with a plain stone memorial.

Everything is a generic low-poly reconstruction. The aircraft carry no markings, numbers, names or insignia; the
men wear plain greatcoats and caps with no badges or symbols; the memorial stone carries no text; nobody's
likeness is attempted."""
import math

import bmesh
import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -30000)
SKYO = (0.0, 0.0, 0.0)              # the bomber, high over the coast
TUR = (0.0, -4600.0, 0.0)           # the ball turret, alone, for the close-ups
FUS = (0.0, -4000.0, 0.0)           # the waist of the fuselage, inside
FALLZ = (0.0, 700.0, -300.0)        # empty air for the fall
STA = (4000.0, 0.0, 0.0)            # the station and the town round it
HOS = (0.0, 4000.0, 0.0)            # hospital room
CMP = (-4000.0, 0.0, 0.0)           # wire fence in the snow
MEM = (-4000.0, 4000.0, 0.0)        # town square with the memorial
HOST = {'rook_ridge', 'chute_find', 'rook_silk', 'rook_dive', 'rook_look', 'shards', 'found', 'rook_shard', 'rook_bed', 'camp',
        'memorial', 'signoff', 'wreath'}
CAMFILL = {'*': 200, 'turret_close': 140, 'chute_rags': 120, 'bomber_down': 3000, 'roof_rush': 0, 'rook_ridge': 300, 'formation': 0,
           'flak_hit': 2500, 'turret_climb': 260, 'chute_find': 260, 'rook_silk': 160, 'gasp_dim': 180, 'thrown_clear': 2500,
           'fall_wide': 600, 'rook_dive': 320, 'town_below': 0, 'rook_look': 320, 'smash': 0, 'shards': 500, 'hole_up': 0,
           'found': 500, 'rook_shard': 220, 'stretcher': 500, 'doctor': 260, 'rook_bed': 320, 'camp': 500, 'memorial': 500,
           'wreath': 120, 'signoff': 260}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'E4B892'
JACKET, FLEECE, HELM = '6A4A30', 'D8CBA8', '4A3626'
OD, BELLY = '5E6240', '8C9092'              # olive drab, grey underside
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    high=('D4E4F2', '3E76BC', 1.25, 3.6, 'FFF0D8', (0.45, -0.55, 0.62)),
    low=('C8D6E2', '6A92BE', 1.2, 3.2, 'FFEED6', (0.45, -0.55, 0.55)),
    inside=('8A9AA8', '4A5A6A', 0.6, 2.6, 'FFF0D8', (0.45, -0.55, 0.62)),
    hall=('B8C8D4', '7A98B8', 1.0, 3.4, 'FFF2DC', (0.25, -0.35, 0.9)),
    room=('5A5A58', '2E2E30', 0.35, 0.0, 'FFFFFF', (0, 0, 1)),
    snow=('C6CCD4', '8C96A4', 1.3, 1.6, 'E8EEF6', (-0.3, -0.5, 0.5)),
    square=('F0D8BC', '8AA4C4', 1.2, 2.6, 'FFE2C0', (0.7, -0.5, 0.35)))
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


def plus(a, b, s=1.0):
    return (a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s)


def cut_sphere(o, keep_fn):
    """Delete the vertices of a primitive (in its local space) where keep_fn(v) is False: windows and open shells."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    gone = [v for v in bm.verts if not keep_fn(v.co)]
    bmesh.ops.delete(bm, geom=gone, context='VERTS')
    bm.to_mesh(me)
    bm.free()
    return o


# ---------------------------------------------------------------- the sky: bomber, formation, flak, cloud, coast
def bomber_body(par, detail=True, turret=True):
    """A four-engined heavy bomber, single tall fin, nose towards -Y. Olive drab over grey, no markings."""
    add('cylinder', OD, (0, 0, 0), rot=(PI / 2, 0, 0), radius=1.35, depth=24, vertices=10, parent=par)
    add('cylinder', BELLY, (0, 0, -0.55), rot=(PI / 2, 0, 0), radius=1.12, depth=23.6, vertices=10, parent=par)
    add('cone', OD, (0, -14.2, -0.1), rot=(PI / 2, 0, 0), radius1=0.25, radius2=1.35, depth=4.4, vertices=10, parent=par)
    add('ico_sphere', '2A3A4C', (0, -16.0, -0.15), radius=0.55, subdivisions=1, parent=par, rough=0.2)      # glazed nose
    add('cone', OD, (0, 15.5, 0.4), rot=(-PI / 2, 0, 0), radius1=1.35, radius2=0.35, depth=7, vertices=10, parent=par)
    add('cube', OD, (0, 16.2, 3.4), rot=(-0.35, 0, 0), scale=(0.3, 5.5, 5.0), size=1, parent=par)                # the tall fin
    add('cube', OD, (0, 10.5, 1.5), rot=(-0.12, 0, 0), scale=(0.3, 6.0, 1.2), size=1, parent=par)
    add('cube', '2A3A4C', (0, -9.6, 1.2), scale=(1.5, 2.2, 0.7), size=1, parent=par, rough=0.2)                   # cockpit glazing
    for s in (-1, 1):
        add('cube', OD, (s * 4.8, 17.4, 0.4), rot=(0, 0, s * 0.12), scale=(8.0, 2.8, 0.25), size=1, parent=par)
        add('cube', OD, (s * 9.0, -3.0, -0.3), rot=(0, s * -0.06, s * 0.06), scale=(16, 5.6, 0.45), size=1, parent=par)
        add('cube', OD, (s * 20.0, -2.2, 0.35), rot=(0, s * -0.06, s * 0.1), scale=(9, 3.6, 0.32), size=1, parent=par)
        for x in (5.8, 11.4):
            add('cylinder', OD, (s * x, -6.4, -0.3), rot=(PI / 2, 0, 0), radius=0.85, depth=4.6, vertices=8, parent=par)
            add('cylinder', '2A2C2E', (s * x, -8.8, -0.3), rot=(PI / 2, 0, 0), radius=0.9, depth=0.4, vertices=10, parent=par)
            if detail:
                add('cone', '3A3C3E', (s * x, -9.2, -0.3), rot=(PI / 2, 0, 0), radius1=0.3, radius2=0.0, depth=0.5, vertices=6, parent=par)
    if turret:
        add('ico_sphere', '6E7276', (0, 2.6, -1.85), radius=0.95, subdivisions=2, parent=par, rough=0.4)          # the ball turret
        add('cylinder', '1E2630', (0, 1.75, -2.1), rot=(PI / 2 + 0.3, 0, 0), radius=0.42, depth=0.12, vertices=10, parent=par, rough=0.15)
        for sx in (-0.3, 0.3):
            bar(par, '1C1E20', (sx, 2.0, -2.0), (sx, -0.6, -2.4), 0.09)
    if detail:
        for y in (-1.0, 4.0):
            add('cube', '1A1C1E', (1.33, y, 0.2), scale=(0.08, 1.4, 0.8), size=1, parent=par)                    # waist windows
            add('cube', '1A1C1E', (-1.33, y, 0.2), scale=(0.08, 1.4, 0.8), size=1, parent=par)


def make_air(S):
    b = keep(empty(SKYO))
    bomber_body(b)
    S['hole_w'] = add('cube', '0E0F10', (1.3, 6.5, -0.2), scale=(0.2, 2.6, 1.6), size=1, parent=b)              # the ragged hole, later
    S['hole_w'].hide_render = True
    S['bomber'] = b
    S['others'] = []
    for i in range(4):
        o = keep(empty(FAR))
        bomber_body(o, detail=False, turret=False)
        S['others'].append(o)
    S['puffs'] = [keep(add('ico_sphere', ('2A2A2E', '34343A', '232326')[i % 3], FAR, radius=1, subdivisions=1, rough=1.0)) for i in range(18)]
    S['flash'] = [keep(add('ico_sphere', 'FF9A30', FAR, radius=1, subdivisions=1, emit=12.0)) for i in range(18)]
    S['flamp'] = [light(FAR, 0, 'FF9A40', kind='POINT') for _ in range(3)]
    S['clouds'] = [keep(add('ico_sphere', ('F4F6FA', 'E6ECF4', 'FFFFFF')[i % 3], FAR, scale=(18 + 26 * rnd(i, 1), 16 + 22 * rnd(i, 2), 6 + 6 * rnd(i, 3)),
                            radius=1, subdivisions=2, rough=1.0)) for i in range(18)]
    ld = keep(empty(FAR))
    add('cube', '35587A', (0, 0, -1), scale=(9000, 9000, 1), size=1, parent=ld, rough=0.6)                      # the sea
    add('cube', '6A7A4C', (-1300, 0, 0), scale=(2200, 9000, 1), size=1, parent=ld, rough=1.0)                   # the land
    for i in range(40):
        col = ('5E7044', '7A7A50', '4E6038', '8A7E5A')[i % 4]
        add('cube', col, (-300 - 1800 * rnd(i, 4), (rnd(i, 5) - 0.5) * 3400, 1), rot=(0, 0, rnd(i, 6) * 0.6),
            scale=(80 + 220 * rnd(i, 7), 60 + 200 * rnd(i, 8), 1), size=1, parent=ld, rough=1.0)
    add('cube', '35587A', (-120, -200, 0.5), rot=(0, 0, 0.5), scale=(420, 120, 1), size=1, parent=ld, rough=0.6)    # the estuary
    S['land'] = ld
    S['smoke'] = [keep(add('ico_sphere', ('2C2C30', '3A3A40')[i % 2], FAR, radius=1, subdivisions=1, rough=1.0)) for i in range(14)]
    S['fl'] = [keep(add('cone', ('FF5A00', 'FF9A10', 'FF3800')[i % 3], FAR, radius1=0.5, radius2=0.0, depth=2.0, vertices=5,
                        emit=(3.0, 4.0, 2.4)[i % 3])) for i in range(6)]
    S['bits'] = [keep(add('cube', ('6E7276', OD, 'A8ACAE', '3A3C3E')[i % 4], FAR, scale=(0.4, 0.12, 0.3), size=1, rough=0.5)) for i in range(14)]


# ---------------------------------------------------------------- the ball turret, alone, for the close-ups
def make_turret(S):
    r = keep(empty(TUR))
    sh = add('uv_sphere', '6E7276', (0, 0, 0), radius=1.75, segments=24, ring_count=14, parent=r, rough=0.45)
    cut_sphere(sh, lambda v: not (v.y < -0.6 and v.x * v.x + v.z * v.z < 1.05 * 1.05))                      # the round window
    add('torus', '3A3E42', (0, -1.42, 0), rot=(PI / 2, 0, 0), major_radius=1.07, minor_radius=0.09, major_segments=20, minor_segments=5, parent=r, rough=0.35)
    for s in (-1, 1):                                        # the two guns either side of his head
        bar(r, '16181A', (s * 0.62, 0.4, -0.25), (s * 0.62, -3.6, -0.25), 0.12)
        add('cube', '2A2C2E', (s * 0.62, 0.0, -0.25), scale=(0.3, 1.0, 0.35), size=1, parent=r)
        for z in (0.45, -0.95):
            bar(r, '4A4E52', (s * 1.2, -1.2, z), (s * 1.6, 0.9, z * 1.2), 0.05)
    add('cube', '2A2C2E', (0, -0.95, 0.75), scale=(0.3, 0.3, 0.22), size=1, parent=r)                            # the gunsight
    add('cube', 'FFB04A', (0, -1.1, 0.75), scale=(0.12, 0.02, 0.08), size=1, parent=r, emit=2.0)
    S['glass'] = add('cylinder', 'CFE8F4', (0, -1.47, 0), rot=(PI / 2, 0, 0), radius=1.05, depth=0.02, vertices=20, parent=r, rough=0.05, alpha=0.03)
    S['cracks'] = []
    c0 = (0.72, -1.52, 0.55)
    for i in range(7):
        a = i * 0.9 + 0.2
        L = 0.25 + 0.35 * rnd(i, 30)
        o = bar(r, 'E4F2FF', c0, (c0[0] + L * math.cos(a), -1.52, c0[2] + L * math.sin(a)), 0.008, emit=1.2)
        S['cracks'].append((o, tuple(o.scale)))
    S['tlamp'] = light(at(TUR, 0.4, -0.4, 0.9), 0, 'FFD8A0', size=0.5)
    S['turret'] = r


# ---------------------------------------------------------------- the waist of the fuselage, inside
def make_fuse(S):
    r = keep(empty(FUS))
    add('cylinder', '8E987A', (0, 0, 1.3), rot=(PI / 2, 0, 0), radius=2.6, depth=18, vertices=14, parent=r, end_fill_type='NOTHING')
    add('cube', '4A4434', (0, 0, -0.05), scale=(4.4, 18, 0.12), size=1, parent=r)                                  # the floor
    for y in range(-8, 9, 1):
        add('torus', '6E785E', (0, y * 1.0, 1.3), rot=(PI / 2, 0, 0), major_radius=2.52, minor_radius=0.07, major_segments=16, minor_segments=4, parent=r)
    for s in (-1, 1):
        for z in (0.9, 2.4):
            add('cube', '6E785E', (s * 2.4, 0, z), scale=(0.08, 18, 0.08), size=1, parent=r)
    # the turret hatch in the floor and the top of the ball under it
    add('torus', '3A3E42', (0, 1.5, 0.02), major_radius=0.95, minor_radius=0.08, major_segments=16, minor_segments=4, parent=r)
    add('cylinder', '0A0B0C', (0, 1.5, -0.02), radius=0.92, depth=0.06, vertices=16, parent=r)
    bar(r, '4A4E52', (0.95, 1.5, 0.0), (1.2, 1.5, 1.4), 0.06)
    # holes in the skin letting daylight in, and the shafts of light
    S['holes'] = []
    for i, (y, a) in enumerate(((-2.6, 0.5), (-1.2, 0.9), (0.6, 0.3), (2.6, 0.8), (-3.8, 1.0), (3.6, 0.45))):
        x, z = 2.55 * math.cos(a), 1.3 + 2.55 * math.sin(a)
        add('ico_sphere', 'FFF6E4', (x, y, z), radius=0.11 + 0.09 * rnd(i, 40), subdivisions=1, parent=r, emit=14.0)
        bar(r, 'FFF2DC', (x, y, z), (x - 3.6, y + 0.4, z - 2.4), 0.05 + 0.03 * rnd(i, 41), emit=0.5, alpha=0.035)
    for y in (-0.6, 4.6):
        add('cube', 'DCEAF6', (-2.5, y, 1.7), scale=(0.1, 1.5, 0.9), size=1, parent=r, emit=3.0)                   # waist window, open sky
    # the parachute hook and the torn pack
    add('cube', '3A3E42', (2.42, -1.8, 2.35), scale=(0.1, 0.12, 0.3), size=1, parent=r)
    S['pack'] = pk = empty((2.15, -1.8, 1.65), r)
    add('cube', '6E6A48', (0, 0, 0), scale=(0.22, 0.8, 0.95), size=1, parent=pk, rough=1.0)
    add('cube', '4E4A34', (-0.12, 0, 0.0), scale=(0.02, 0.62, 0.8), size=1, parent=pk, rough=1.0)
    for i in range(5):
        add('cylinder', '0E0D0A', (-0.12, -0.25 + 0.12 * i, 0.3 - 0.13 * (i % 3)), rot=(0, PI / 2, 0), radius=0.05 + 0.03 * rnd(i, 42), depth=0.04, vertices=6, parent=pk)
    S['rags'] = []
    for i in range(9):
        o = add('cube', ('F4F2EA', 'E8E4D8', 'FFFFFF')[i % 3], (0, 0, 0), scale=(0.02, 0.07 + 0.08 * rnd(i, 43), 0.5 + 0.6 * rnd(i, 44)), size=1, parent=pk, rough=1.0)
        S['rags'].append(o)
    S['silk'] = keep(add('cube', 'F6F4EE', FAR, scale=(0.04, 0.4, 1.0), size=1, rough=1.0))
    S['silkholes'] = [add('cylinder', '1A1814', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.07 + 0.04 * rnd(i, 45), depth=0.06, vertices=6, parent=S['silk']) for i in range(4)]
    S['fsmoke'] = [keep(add('ico_sphere', '7A7E80', FAR, radius=0.22, subdivisions=1, rough=1.0, alpha=0.3)) for _ in range(6)]
    S['flight'] = light(at(FUS, 0.5, -1.0, 2.4), 0, 'FFF0DC', size=3.0)
    S['fuse'] = r


# ---------------------------------------------------------------- the station and the town
ARC = 9                                  # segments along each roof arch
BAYS = list(range(-26, 27, 4))           # arch positions along the hall


def arch_pt(a):
    return (11.0 * math.cos(a), 6.0 + 7.0 * math.sin(a))


def make_station(S):
    r = keep(empty(STA))
    add('cube', 'A8A094', (0, 0, -0.1), scale=(26, 64, 0.2), size=1, parent=r, rough=1.0)
    for s in (-1, 1):
        add('cube', 'C2B8A6', (s * 4.6, 0, 0.35), scale=(4.4, 58, 0.7), size=1, parent=r, rough=1.0)              # platforms
        add('cube', 'E8DCC0', (s * 2.45, 0, 0.71), scale=(0.15, 58, 0.02), size=1, parent=r)                         # platform edge
        add('cube', '7A4E3A', (s * 11.4, 0, 3.0), scale=(0.8, 58, 6.0), size=1, parent=r, rough=1.0)                 # brick side walls
        for y in range(-24, 25, 6):
            add('cube', '24282C', (s * 10.98, y, 3.4), scale=(0.1, 2.4, 3.2), size=1, parent=r)                      # arched windows
            add('cylinder', '24282C', (s * 10.98, y, 5.0), rot=(0, PI / 2, 0), radius=1.2, depth=0.1, vertices=10, parent=r)
    for x in (0.0, 9.0, -9.0):                                                                                         # three tracks
        for d in (-0.75, 0.75):
            add('cube', '5A5C60', (x + d, 0, 0.08), scale=(0.12, 62, 0.12), size=1, parent=r, rough=0.3)
        for y in range(-30, 31, 2):
            add('cube', '4A3A2C', (x, y, 0.02), scale=(2.2, 0.35, 0.08), size=1, parent=r)
    # the arches, the purlins and the glass
    S['holep'] = []
    for y in BAYS:
        pts = [arch_pt(PI * i / ARC) for i in range(ARC + 1)]
        for i in range(ARC):
            bar(r, '2E3236', (pts[i][0], y, pts[i][1]), (pts[i + 1][0], y, pts[i + 1][1]), 0.28)
    for i in range(1, ARC):
        x, z = arch_pt(PI * i / ARC)
        add('cube', '2E3236', (x, 0, z), scale=(0.16, 56, 0.16), size=1, parent=r)
    for yi, y in enumerate(BAYS[:-1]):
        for i in range(ARC):
            a0, a1 = PI * i / ARC, PI * (i + 1) / ARC
            (x0, z0), (x1, z1) = arch_pt(a0), arch_pt(a1)
            ang = math.atan2(z1 - z0, x1 - x0)
            L = math.hypot(x1 - x0, z1 - z0)
            p = add('cube', 'BFE2EE', ((x0 + x1) / 2, y + 2, (z0 + z1) / 2), rot=(0, -ang, 0), scale=(L * 0.96, 3.8, 0.04), size=1,
                    parent=r, rough=0.05, emit=0.25, alpha=0.32)
            add('cube', '2E3236', ((x0 + x1) / 2, y + 2, (z0 + z1) / 2), rot=(0, -ang, 0), scale=(L, 0.08, 0.07), size=1, parent=r)  # glazing bar
            if y == -2 and i in (3, 4, 5):
                S['holep'].append(p)
    # ragged edges of the hole (shown after the smash)
    S['edge'] = []
    for i in range(12):
        a = PI * (0.33 + 0.34 * rnd(i, 50))
        x, z = arch_pt(a)
        y = (2.1 if i % 2 else -2.1) + 0.3 * (rnd(i, 51) - 0.5)
        o = add('cone', 'CFEAF4', (x, y, z - 0.1), rot=(PI / 2 + 0.6 * (rnd(i, 52) - 0.5), 0, rnd(i, 53) * 6), radius1=0.35, radius2=0.0,
                depth=1.1, vertices=3, parent=r, rough=0.05, emit=0.4, alpha=0.6)
        S['edge'].append(o)
    S['glints'] = [keep(add('cone', ('E4F6FF', 'C4E6F4', 'FFFFFF')[i % 3], FAR, radius1=0.16 + 0.1 * rnd(i, 54), radius2=0.0, depth=0.35 + 0.3 * rnd(i, 55),
                            vertices=3, rough=0.05, emit=1.6)) for i in range(34)]
    S['floorglass'] = []
    for i in range(22):
        a = rnd(i, 56) * 2 * PI
        q = 0.4 + 2.8 * rnd(i, 57)
        S['floorglass'].append(add('cone', 'D8F0FA', (q * math.cos(a), 0.5 + q * math.sin(a), 0.1), rot=(PI / 2, 0, a), radius1=0.12 + 0.1 * rnd(i, 58),
                                   radius2=0.0, depth=0.04, vertices=3, parent=r, rough=0.05, emit=0.8))
    # a locomotive at the far platform, benches, lamps, a clock
    lo = empty((9.0, 9.0, 0), r)
    add('cylinder', '1E2024', (0, 0, 2.3), rot=(PI / 2, 0, 0), radius=1.15, depth=7.0, vertices=12, parent=lo, rough=0.4)
    add('cube', '1E2024', (0, 4.8, 2.6), scale=(2.6, 2.8, 3.2), size=1, parent=lo, rough=0.4)
    add('cube', '24282C', (0, 4.8, 4.35), scale=(3.0, 3.2, 0.3), size=1, parent=lo)
    add('cylinder', '1E2024', (0, -2.6, 3.9), radius=0.32, depth=1.4, vertices=8, parent=lo)
    add('cylinder', 'B23A2A', (0, -3.55, 1.0), rot=(PI / 2, 0, 0), radius=1.2, depth=0.2, vertices=12, parent=lo)
    for y in (-2.0, 0.0, 2.0, 4.6):
        for s in (-1, 1):
            add('cylinder', 'B23A2A', (s * 1.0, y, 0.85), rot=(0, PI / 2, 0), radius=0.75, depth=0.2, vertices=10, parent=lo)
    for y in (-14, 6, 18):
        add('cube', '5A3E2A', (-6.2, y, 1.2), scale=(0.5, 2.4, 0.12), size=1, parent=r)
        add('cube', '5A3E2A', (-6.45, y, 1.55), scale=(0.1, 2.4, 0.6), size=1, parent=r)
    for y in (-18, -8, 12, 22):
        add('cylinder', '2E3236', (-3.0, y, 2.6), radius=0.08, depth=4.0, vertices=6, parent=r)
        add('cube', 'FFE2A0', (-3.0, y, 4.7), scale=(0.4, 0.4, 0.5), size=1, parent=r, emit=3.0)
    add('cylinder', 'F2EEE2', (0.0, -12.0, 8.6), rot=(PI / 2, 0, 0), radius=0.9, depth=0.2, vertices=16, parent=r)
    add('torus', '2E3236', (0.0, -12.12, 8.6), rot=(PI / 2, 0, 0), major_radius=0.9, minor_radius=0.08, major_segments=16, minor_segments=4, parent=r)
    S['hand1'] = add('cube', '1A1A1A', (0.0, -12.15, 8.85), scale=(0.06, 0.02, 0.5), size=1, parent=r)
    bar(r, '2E3236', (0, -12, 9.5), (0, -12, 12.6), 0.08)
    S['dust'] = [keep(add('ico_sphere', 'FFF4E0', FAR, radius=0.05, subdivisions=1, emit=2.0)) for _ in range(16)]
    S['shaft'] = add('cone', 'FFF4DC', (-4.0, 0, 6.6), rot=(0, 0.28, 0), radius1=3.0, radius2=1.4, depth=13.5, vertices=10, parent=r, emit=0.5, alpha=0.06)
    S['shaft'].hide_render = True
    S['hlamp'] = light(at(STA, -2, 0, 9.5), 0, 'FFF0D8', size=6.0)
    # the town round it: blocks of houses with pitched roofs, streets, the harbour
    tw = empty((0, 0, 0), r)
    add('cube', '7A7870', (0, 0, -0.3), scale=(900, 900, 0.4), size=1, parent=tw, rough=1.0)
    add('cube', '35587A', (160, 0, -0.2), scale=(220, 900, 0.4), size=1, parent=tw, rough=0.4)
    for i in range(150):
        x = -130 + 260 * rnd(i, 60)
        y = -160 + 320 * rnd(i, 61)
        if x > 45:
            x -= 60
        if abs(x) < 20 and abs(y) < 40:
            continue
        w, d, hh = 6 + 8 * rnd(i, 62), 6 + 10 * rnd(i, 63), 4 + 7 * rnd(i, 64)
        col = ('D8CCB4', 'C8B8A0', 'E2D8C4', 'B8A890')[i % 4]
        add('cube', col, (x, y, hh / 2), scale=(w, d, hh), size=1, parent=tw, rough=1.0)
        add('cube', ('6A4A3A', '4A4E58', '7A5240')[i % 3], (x, y, hh + 0.9), rot=(0, 0.6 if i % 2 else -0.6, 0), scale=(w * 0.75, d * 1.02, 1.6), size=1, parent=tw, rough=1.0)
    for i in range(6):                                                                                                  # harbour cranes
        bar(tw, '3A3E44', (52, -60 + 24 * i, 0), (52, -60 + 24 * i, 18), 0.6)
        bar(tw, '3A3E44', (52, -60 + 24 * i, 18), (60, -60 + 24 * i, 16), 0.4)
    S['station'] = r


# ---------------------------------------------------------------- hospital room
def make_hosp(S):
    r = keep(empty(HOS))
    add('cube', '8A8478', (0, 0, -0.05), scale=(10, 10, 0.1), size=1, parent=r)
    add('cube', 'DCD4C0', (0, 4.0, 3), scale=(10, 0.2, 6), size=1, parent=r)
    add('cube', '6E8A74', (0, 3.88, 1.0), scale=(10, 0.05, 2.0), size=1, parent=r)
    add('cube', 'DCD4C0', (-4.5, 0, 3), scale=(0.2, 10, 6), size=1, parent=r)
    add('cube', '6E8A74', (-4.38, 0, 1.0), scale=(0.05, 10, 2.0), size=1, parent=r)
    add('cube', 'E8F0F6', (-4.35, 0.5, 3.4), scale=(0.05, 2.4, 2.2), size=1, parent=r, emit=2.2)                   # window
    for z in (3.4,):
        add('cube', '5A5448', (-4.3, 0.5, z), scale=(0.06, 2.5, 0.08), size=1, parent=r)
    add('cube', '5A5448', (-4.3, 0.5, 3.4), scale=(0.06, 0.08, 2.3), size=1, parent=r)
    # the bed: iron frame, mattress, pillow, blanket
    add('cube', 'F2F0EA', (0, 1.2, 1.1), scale=(2.1, 4.6, 0.4), size=1, parent=r, rough=1.0)
    add('cube', 'F6F4EE', (0, 3.1, 1.42), scale=(1.4, 0.7, 0.3), size=1, parent=r, rough=1.0)
    S['blanket'] = add('cube', '8A9AAA', (0, 0.4, 1.38), scale=(2.15, 2.9, 0.22), size=1, parent=r, rough=1.0)
    for x in (-1.05, 1.05):
        for y in (-1.1, 3.5):
            bar(r, 'E8E8E4', (x, y, 0), (x, y, 1.9 if y > 0 else 1.5), 0.08, rough=0.4)
        bar(r, 'E8E8E4', (x, -1.1, 0.9), (x, 3.5, 0.9), 0.06, rough=0.4)
    for y, z in ((3.5, 1.9), (-1.1, 1.5)):
        bar(r, 'E8E8E4', (-1.05, y, z), (1.05, y, z), 0.08, rough=0.4)
    add('cube', 'D8D0BC', (2.0, 2.8, 0.7), scale=(0.9, 0.9, 1.4), size=1, parent=r)
    add('cylinder', 'F2F2EE', (2.0, 2.8, 1.48), radius=0.3, depth=0.14, vertices=10, parent=r, rough=0.3)
    add('cylinder', '3A3A3E', (1.2, 3.6, 5.4), radius=0.04, depth=1.2, vertices=6, parent=r)
    add('cone', 'E8E4D4', (1.2, 3.6, 4.7), radius1=0.5, radius2=0.12, depth=0.4, vertices=10, parent=r)
    S['bulb'] = light(at(HOS, 1.2, 3.3, 4.2), 0, 'FFE4B8', size=1.0)
    S['winl'] = light(at(HOS, -3.0, 0.5, 3.4), 0, 'DDE8F4', size=3.0)
    S['hosp'] = r


# ---------------------------------------------------------------- wire fence in the snow
def make_camp(S):
    r = keep(empty(CMP))
    add('cube', 'E8EEF4', (0, 0, -0.1), scale=(200, 200, 0.2), size=1, parent=r, rough=1.0)
    for i in range(16):
        x = -24 + 3.2 * i
        add('cube', '4A3A2A', (x, 0, 1.6), rot=(0, 0.04 * (rnd(i, 70) - 0.5), 0), scale=(0.18, 0.18, 3.4), size=1, parent=r)
        add('cube', 'F2F6FA', (x, 0, 3.32), scale=(0.24, 0.24, 0.08), size=1, parent=r, rough=1.0)
    for z in (0.5, 1.1, 1.7, 2.3, 2.9):
        add('cube', '3A3C40', (-0.0, 0.02, z), scale=(52, 0.02, 0.025), size=1, parent=r, rough=0.4)
    for i in range(30):                                                                                                 # barbs
        add('cube', '3A3C40', (-24 + 1.7 * i, 0.02, 2.9), rot=(0, 0.8, 0), scale=(0.02, 0.02, 0.14), size=1, parent=r)
    hut = empty((-6.0, -9.0, 0), r)
    add('cube', '6A5A44', (0, 0, 1.5), scale=(16, 5, 3), size=1, parent=hut, rough=1.0)
    for s in (-1, 1):
        add('cube', '3A3430', (0, s * 1.4, 3.6), rot=(s * 0.55, 0, 0), scale=(16.6, 3.4, 0.2), size=1, parent=hut)
        add('cube', 'F2F6FA', (0, s * 1.35, 3.75), rot=(s * 0.55, 0, 0), scale=(16.4, 3.2, 0.12), size=1, parent=hut, rough=1.0)
    for x in (-5, -1, 3, 7):
        add('cube', 'FFD89A', (x, 2.52, 1.7), scale=(1.0, 0.05, 0.8), size=1, parent=hut, emit=1.5)
    tw = empty((14.0, 6.0, 0), r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bar(tw, '4A3A2A', (sx * 1.2, sy * 1.2, 0), (sx * 0.9, sy * 0.9, 7.0), 0.16)
    add('cube', '4A3A2A', (0, 0, 7.6), scale=(2.6, 2.6, 1.4), size=1, parent=tw)
    add('cube', '3A3430', (0, 0, 8.5), scale=(3.2, 3.2, 0.25), size=1, parent=tw)
    for i in range(12):
        add('cone', '2E4A3A', (-30 + 5.5 * i, 22 + 4 * rnd(i, 71), 3.5), radius1=1.8, radius2=0.0, depth=7 + 3 * rnd(i, 72), vertices=6, parent=r, rough=1.0)
    S['flakes'] = [keep(add('ico_sphere', 'FFFFFF', FAR, radius=0.07, subdivisions=1, rough=1.0)) for _ in range(30)]
    S['camp'] = r


# ---------------------------------------------------------------- town square with the memorial
def make_square(S):
    r = keep(empty(MEM))
    add('cube', '9A948A', (0, 0, -0.1), scale=(60, 60, 0.2), size=1, parent=r, rough=1.0)
    for i in range(14):
        for j in range(14):
            if (i + j) % 3 == 0:
                add('cube', '8A847A', (-13 + 2 * i, -13 + 2 * j, 0.01), scale=(1.9, 1.9, 0.02), size=1, parent=r, rough=1.0)
    add('cube', 'B8B2A6', (0, 0, 0.4), scale=(3.6, 3.6, 0.8), size=1, parent=r, rough=0.9)
    add('cube', 'C8C2B6', (0, 0, 0.95), scale=(2.8, 2.8, 0.3), size=1, parent=r, rough=0.9)
    add('cube', 'D2CCC0', (0, 0, 3.6), scale=(1.5, 0.8, 5.0), size=1, parent=r, rough=0.8)
    add('cube', 'C8C2B6', (0, 0, 6.2), scale=(1.8, 1.0, 0.3), size=1, parent=r, rough=0.8)
    add('cube', '5A4A34', (0, -0.42, 3.6), scale=(1.0, 0.04, 1.3), size=1, parent=r, rough=0.4)                        # blank bronze plate
    wr = empty((0, -1.95, 0.95), r, (0.35, 0, 0))
    add('torus', '2E5A34', (0, 0, 0.6), rot=(PI / 2, 0, 0), major_radius=0.7, minor_radius=0.16, major_segments=14, minor_segments=5, parent=wr, rough=1.0)
    S['petals'] = []
    for i in range(12):
        a = i * 2 * PI / 12
        o = add('ico_sphere', ('C82A2A', 'F4F2EC', '2A4E9A')[i % 3], (0.7 * math.cos(a), -0.12, 0.6 + 0.7 * math.sin(a)), radius=0.12, subdivisions=1, parent=wr, rough=0.8)
        S['petals'].append(o)
    S['flower'] = keep(empty(FAR))
    bar(S['flower'], '3A6A3A', (0, 0, 0), (0, 0, 0.9), 0.04)
    add('ico_sphere', 'D8342E', (0, 0, 0.95), radius=0.13, subdivisions=1, parent=S['flower'], rough=0.8)
    for i in range(7):                                                                                                  # house fronts
        x = -18 + 6 * i
        col = ('E2D2B4', 'D4C4A4', 'EADCC2', 'C8B696')[i % 4]
        hh = 8 + 3 * rnd(i, 80)
        add('cube', col, (x, 14, hh / 2), scale=(5.8, 4, hh), size=1, parent=r, rough=1.0)
        add('cube', '4A4E58', (x, 14, hh + 1.0), rot=(0.6, 0, 0), scale=(5.9, 3.0, 0.2), size=1, parent=r)
        for wx in (-1.5, 1.5):
            for wz in (3.0, 6.0):
                add('cube', '3A4450', (x + wx, 11.98, wz), scale=(1.0, 0.05, 1.4), size=1, parent=r)
    add('cylinder', '2E3236', (-5.0, 3.0, 2.2), radius=0.08, depth=4.4, vertices=6, parent=r)
    add('cube', '2E3236', (-5.0, 3.0, 4.5), scale=(0.5, 0.5, 0.6), size=1, parent=r)
    for i in range(3):
        add('ico_sphere', '4A6A3A', (6.0 + 0.6 * i, 6.0, 5.0 + 0.8 * i), radius=2.0, subdivisions=1, parent=r, rough=1.0)
    add('cylinder', '4A3A2A', (6.6, 6.0, 2.2), radius=0.25, depth=4.4, vertices=6, parent=r)
    S['square'] = r


# ---------------------------------------------------------------- people
def gunner_head(head):
    d = K.human_head(SKIN, '7A5434')(head)
    add('ico_sphere', HELM, (0, 0.06, 0.1), scale=(0.98, 1.02, 1.0), radius=0.31, subdivisions=1, parent=head)       # leather flying helmet
    for s in (-1, 1):
        add('cube', HELM, (s * 0.27, 0.0, -0.1), scale=(0.08, 0.26, 0.34), size=1, parent=head)
    d['gog'] = [add('cube', '23272C', (s * 0.11, -0.25, 0.22), rot=(-0.4, 0, 0), scale=(0.15, 0.05, 0.1), size=1, parent=head, rough=0.2) for s in (-1, 1)]
    d['mask'] = add('cube', '4E5A46', (0.18, -0.24, -0.16), rot=(0, 0.6, 0.4), scale=(0.16, 0.1, 0.18), size=1, parent=head, rough=0.7)   # oxygen mask, hanging loose
    return d


def cap_head(skin, hair, cap):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('cube', cap, (0, 0.02, 0.28), scale=(0.6, 0.64, 0.16), size=1, parent=head)
        add('cube', cap, (0, -0.32, 0.22), rot=(0.3, 0, 0), scale=(0.5, 0.2, 0.04), size=1, parent=head)
        return d
    return fn


def doc_head(head):
    d = K.human_head('E2B896', '9A9A96')(head)
    for s in (-1, 1):
        add('torus', '2A2A2C', (s * 0.105, -0.29, 0.04), rot=(PI / 2, 0, 0), major_radius=0.075, minor_radius=0.012, major_segments=10, minor_segments=3, parent=head)
    return d


# ---------------------------------------------------------------- build, reset, faces
def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_air(S)
    make_turret(S)
    make_fuse(S)
    make_station(S)
    make_hosp(S)
    make_camp(S)
    make_square(S)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['man'] = m = K.Rig(dict(top=JACKET, pants='5C5A44', hand='3A2A1E', boot='2A2018', fore=JACKET), gunner_head)
    add('cube', FLEECE, (0, -0.22, 0.98), scale=(0.5, 0.16, 0.1), size=1, parent=m.body, rough=1.0)              # fleece collar
    for s in (-1, 1):
        add('cube', '8A7A4A', (s * 0.2, -0.36, 0.55), rot=(0, s * 0.25, 0), scale=(0.09, 0.03, 0.9), size=1, parent=m.body, rough=1.0)   # harness straps
    S['cast'] = add('cube', 'F4F2EC', (0, 0, -0.24), scale=(0.2, 0.2, 0.5), size=1, parent=m.el[1], rough=1.0)
    S['sling'] = add('cube', 'F0EEE6', (0.12, -0.38, 0.62), rot=(0, 0.5, 0), scale=(0.5, 0.05, 0.16), size=1, parent=m.body, rough=1.0)
    S['men'] = [K.Rig(dict(top=c, pants='3E4038', hand='D4AE8C', boot='1A1A1C', fore=c), cap_head(sk, hr, cp))
                for c, sk, hr, cp in (('6A6E60', 'D6B090', '6A5238', '5A5E52'), ('5E6258', 'C89C7C', '3A2E24', '50544A'))]
    S['doc'] = K.Rig(dict(top='E8E6DE', pants='4A4C50', hand='E2B896', boot='1E1E22', fore='E8E6DE'), doc_head)
    S['humans'] = [S['man']] + S['men'] + [S['doc']]
    S['cast_all'] = [S['rook']] + S['humans']
    S['shard'] = keep(add('cone', 'E8F8FF', FAR, radius1=0.16, radius2=0.0, depth=0.42, vertices=3, rough=0.05, emit=2.0))
    st = keep(empty(FAR))
    add('cube', '8A7E5E', (0, 0, 0), scale=(1.0, 3.6, 0.08), size=1, parent=st, rough=1.0)
    for x in (-0.6, 0.6):
        bar(st, '5A4A34', (x, -2.4, 0.0), (x, 2.4, 0.0), 0.08)
    S['stretch'] = st
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
    w = bpy.data.worlds.new('w25')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.1, 0.6
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs[2], mr.inputs[0])
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(mx.outputs[2], S['bg'].inputs[0])
    S['skymix'] = mx
    reset(S)
    return S


def reset(S):
    for rig in S['cast_all']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for l in S['flamp'] + [S['sun'], S['tlamp'], S['flight'], S['hlamp'], S['bulb'], S['winl']]:
        l.data.energy = 0
    for o in S['holep']:
        o.hide_render = False
    for o in S['edge'] + S['floorglass'] + [S['cast'], S['sling'], S['hole_w'], S['shaft']]:
        o.hide_render = True
    for o, sc_ in S['cracks']:
        o.hide_render = True
    S['bomber'].location, S['bomber'].rotation_euler = SKYO, (0, 0, 0)
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, hat_to=(0.74, -0.14, -1.45))
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
    to = S['hat_to']
    r['hat'].rotation_euler = (lerp(-0.2 + tip * 0.38, 0.2, off), lerp(0.07, 1.25, off), 0)
    r['hat'].location = (lerp(0.0, to[0], off), lerp(0.0, to[1], off), lerp(0.27 + S['hat_jump'] + tip * 0.1, to[2], off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.36 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.8, shut=0.07, tired=0.45, warm=0.8, sad=0.55, pain=0.35, hard=0.6).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.045 if f == 'wide' else -0.02 if f in ('hard', 'tired', 'pain') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide', 'pain') else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.2 if f == 'warm' else 0.13, 0.03, 0.035 + 0.14 * rig.jawv + (0.05 if f in ('wide', 'pain') else 0))
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sky(S, name):
    A = SKIES[name]
    S['skymix'].inputs[6].default_value = K.hexc(A[0])
    S['skymix'].inputs[7].default_value = K.hexc(A[1])
    S['bg'].inputs[1].default_value = A[2]
    S['sun'].data.energy = A[3]
    S['sun'].data.color = K.hexc(A[4])[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(v * 500 for v in A[5])


def cam(S, pos, look, lens=35, roll=0.0):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


def shoot(S, o, pos, look, lens=35, roll=0.0):
    cam(S, at(o, *pos), at(o, *look), lens, roll)


def put(rig, head_at, yaw=0.0, pitch=0.0, roll=0.0, pose=None):
    """Place a rig so that its head ends up at head_at (world): staging by the face, not by the feet."""
    rig.place((0, 0, 0), yaw, pitch, roll)
    rig.apply(pose or P())
    h = wpos(rig.head)
    rig.root.location = (head_at[0] - h[0], head_at[1] - h[1], head_at[2] - h[2])
    return rig


def stand(rig, loc, yaw=0.0, pose=None, face=None):
    rig.place(loc, yaw)
    rig.apply(pose or P())
    if face:
        rig.face = face
    return rig


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def head(rig):
    return wpos(rig.head)


def flak(S, c, t, box=(60, 60, 24), n=12, i0=0, size=3.5, period=1.6, rate=1.0):
    """Black bursts blooming round point c, each born with an orange flash, growing and drifting, then gone."""
    for j in range(n):
        i = i0 + j
        ph = t * rate / period + rnd(i, 90)
        cyc, u = math.floor(ph), ph % 1
        q = (rnd(i + cyc * 13, 91) - 0.5, rnd(i + cyc * 13, 92) - 0.5, rnd(i + cyc * 13, 93) - 0.5)
        p = (c[0] + q[0] * box[0], c[1] + q[1] * box[1], c[2] + q[2] * box[2])
        s = size * (0.6 + 0.5 * rnd(i, 94)) * (0.25 + 0.75 * sm(u * 3)) * (1 + 0.3 * u)
        o = S['puffs'][i]
        o.location = (p[0], p[1] + 2 * u, p[2] + 1.2 * u)
        o.scale = (s, s * 0.9, s * 0.85)
        f = S['flash'][i]
        if u < 0.1:
            fs = size * 0.7 * (1 - u / 0.1)
            f.location, f.scale = p, (fs, fs, fs)
        else:
            f.location = FAR


def boom(S, i, pos, t0, t, size=3.0, watts=60000):
    """One burst at a set moment: flash, light and a puff that grows."""
    u = t - t0
    if u < 0:
        return
    f, o = S['flash'][i], S['puffs'][i]
    if u < 0.16:
        fs = size * (0.6 + 2.5 * u)
        f.location, f.scale = pos, (fs, fs, fs)
        S['flamp'][0].location = pos
        S['flamp'][0].data.energy = watts * (1 - u / 0.16)
    s = size * (0.5 + 1.2 * sm(u * 2.5))
    o.location, o.scale = (pos[0], pos[1] + u, pos[2] + 0.5 * u), (s, s, s)


def clouds(S, c, t, vz=0.0, depth=-70.0, spread=220.0, vy=0.0):
    """A layer of cumulus round c, moving up past the lens at vz (falling) or along at vy (flying)."""
    for i, o in enumerate(S['clouds']):
        x = (rnd(i, 70) - 0.5) * spread
        y = ((rnd(i, 71) * spread + vy * t) % spread) - spread / 2
        z = depth - 25 * rnd(i, 72) + ((vz * t) % 160 if vz else 0)
        if vz and z > 40:
            z -= 160
        if abs(x) < 14 and abs(y) < 14:
            x += 30 if x > 0 else -30
        o.location = (c[0] + x, c[1] + y, c[2] + z)
    S['land'].location = (c[0] + 600, c[1], c[2] - 1600)


def smoke_trail(S, pos, back, t, n=10, i0=0, gap=3.5, size=1.4):
    """A trail of black smoke from pos, laid back along the direction 'back'."""
    for j in range(n):
        u = (j + (t * 4) % 1) / n
        o = S['smoke'][i0 + j]
        o.location = plus(pos, back, gap * n * u)
        s = size * (0.5 + 2.2 * u)
        o.scale = (s, s, s)


def fire(S, pts, t, size=1.0, d=(0, 1, 0.2), i0=0):
    q = Vector(d).normalized().to_track_quat('Z', 'Y').to_euler()
    for j, p in enumerate(pts):
        f = S['fl'][i0 + j]
        fk = 0.75 + 0.3 * math.sin(t * 23 + j * 1.7) + 0.2 * math.sin(t * 37 + j * 0.9)
        f.location = p
        f.rotation_euler = q
        s = size * (0.8 + 0.4 * rnd(j, 2))
        f.scale = (s * fk, s * fk, s * (1.1 + 0.9 * fk))


def debris(S, pos, u, n=10, r=4.0, h=2.0, g=5.0, spin=6.0, dirx=1.0):
    if u <= 0:
        return
    for i in range(n):
        a = i * 1.9 + 0.3
        q = 0.4 + 0.6 * rnd(i, 86)
        S['bits'][i].location = (pos[0] + dirx * abs(r * q * u * math.cos(a)) + r * 0.3 * u, pos[1] + r * q * u * math.sin(a), pos[2] + h * q * u * 2 - g * u * u)
        S['bits'][i].rotation_euler = (u * spin * q, u * spin, i)


def glass_fall(S, top, floor, u, n=34, r=3.5, spin=7.0, seed=0):
    """Shards dropping from the hole to the floor: u is 0 at the burst, 1 when the last has landed."""
    for i in range(n):
        o = S['glints'][i]
        d = 0.15 + 0.85 * rnd(i, 100 + seed)
        k = max(0.0, min(1.0, (u - 0.25 * rnd(i, 101 + seed)) / max(0.2, d)))
        a = rnd(i, 102 + seed) * 2 * PI
        q = r * (0.2 + 0.8 * rnd(i, 103 + seed))
        z = lerp(top[2], floor, k * k)
        o.location = (top[0] + q * math.cos(a) * min(1, k * 3), top[1] + q * math.sin(a) * min(1, k * 3), z)
        o.rotation_euler = (k * spin + i, k * spin * 0.7, i * 1.3)


def broken(S):
    """After the smash: the hole in the glass, ragged edges, glass on the floor, a shaft of light."""
    for o in S['holep']:
        o.hide_render = True
    for o in S['edge'] + S['floorglass']:
        o.hide_render = False


def dust(S, c, t, r=3.0, top=6.0):
    for i, o in enumerate(S['dust']):
        a = rnd(i, 110) * 2 * PI + t * 0.2
        q = r * rnd(i, 111)
        o.location = (c[0] + q * math.cos(a), c[1] + q * math.sin(a), c[2] + ((rnd(i, 112) * top + 0.25 * t) % top))


def feather(S, pos, u):
    for i in range(2):
        if u <= 0:
            continue
        v = u * 1.2
        S['fea'][i].location = (pos[0] + (0.3 + i * 0.4) * v + 0.2 * math.sin(v * 6 + i), pos[1] - 0.3 * v, pos[2] + 0.9 * v - 0.8 * v * v)
        S['fea'][i].rotation_euler = (v * 5 + i, v * 3, i * 2.0)


def limp(t, k=1.0):
    w = math.sin(t * 2.3)
    return P('stand', aL=(1.6 + 0.3 * w, 1.0, 0.5), aR=(1.4 - 0.3 * w, 1.2, 0.6), lL=(0.5, 0.7 + 0.2 * w), lR=(0.2, 0.4 - 0.2 * w), head=(0.3, 0.2))


# ---------------------------------------------------------------- hook
TURP = P('sit', aL=(1.0, 0.35, 1.3, 0.3), aR=(1.0, 0.35, 1.3, -0.3), lL=(1.2, 2.4), lR=(1.2, 2.4), lean=0.3, head=(0.05, 0.0))


def in_turret(S, flinch=0.0, look=0.0):
    m = S['man']
    pose = dict(TURP)
    pose['head'] = (0.05 - 0.25 * flinch, look)
    put(m, at(TUR, 0.0, -0.45, 0.2), 0.0, -0.2, 0.0, pose)
    return m


def turret_close(S, k, t, lt):
    """Close on the gunner curled inside the ball turret, seen through its round window: a flak flash outside, the
    glass cracks across, he flinches. First and last shot."""
    kk = 1 - k if S['prm'].get('loop') else k
    sky(S, 'high')
    S['tlamp'].data.energy = 60
    flak(S, at(TUR, 0, 30, 6), t, (40, 10, 18), n=6, size=3.0)
    S['flamp'][0].location = at(TUR, 1.6, -4.0, 1.4)
    S['flamp'][0].data.energy = 2200 * math.exp(-kk * 8) + 200 * (0.5 + 0.5 * math.sin(t * 17))
    u = sm((kk - 0.05) / 0.35)
    for o, sc in S['cracks']:
        o.hide_render = u < 0.02
        o.scale = (sc[0], sc[1], sc[2] * max(0.02, u))
    fl = math.exp(-kk * 6)
    m = in_turret(S, fl, 0.15 * math.sin(lt * 2.0) * (1 - fl))
    m.face = 'wide' if kk < 0.6 else 'hard'
    m.jawv = 0.2 * fl
    h = head(m)
    cam(S, plus(h, (0.3, -3.3 + 0.3 * kk, 0.35)), plus(h, (0.05, 0, -0.35)), 36)


def chute_rags(S, k, t, lt):
    """His parachute pack on its hook, torn open, silk spilling out in rags; daylight through flak holes behind it."""
    sky(S, 'inside')
    S['flight'].data.energy = 220
    for i, o in enumerate(S['rags']):
        sw = 0.08 * math.sin(t * 3 + i)
        o.location = (-0.14 - 0.03 * i, -0.3 + 0.075 * i, -0.45 - 0.35 * rnd(i, 46) - 0.12 * k)
        o.rotation_euler = (0.25 * math.sin(t * 2.1 + i) + sw, 0.15 * i, 0.3 * rnd(i, 47))
    for i, o in enumerate(S['fsmoke']):
        u = (t * 0.3 + i / 6) % 1
        o.location = at(FUS, 1.2 - 2.0 * u, -3.0 + 2.5 * rnd(i, 48), 2.6 + 0.3 * math.sin(u * 5))
        o.scale = (1 + u, 1 + u, 1 + u)
    shoot(S, FUS, (lerp(0.55, 0.85, k), lerp(-3.6, -3.1, k), 1.95), (2.05, -1.8, 1.35), 30)


def bomber_down(S, k, t, lt):
    """High over the cloud: the bomber rolls over and goes down trailing smoke, an engine on fire, a tiny figure falling away."""
    sky(S, 'high')
    b = S['bomber']
    b.location = at(SKYO, 0, -8 * k, -10 * k)
    b.rotation_euler = (-0.25 - 0.25 * k, 0.6 + 0.7 * k, 0.1)
    clouds(S, SKYO, t, depth=-60, spread=260)
    eng = wpos(b, (-5.8, -6.4, -0.3))
    fire(S, [plus(eng, (0.3 * j, 1.2 * j, 0.4 * j)) for j in range(4)], t, 1.1, (0, 1, 0.5))
    S['flamp'][1].location, S['flamp'][1].data.energy = eng, 20000
    smoke_trail(S, eng, (0.1, 1.0, 0.65), t, n=12, gap=2.8, size=1.5)
    flak(S, at(SKYO, 0, 10, 4), t, (60, 60, 30), n=10, i0=6, size=3.5)
    m = S['man']
    m.root.scale = (1.4, 1.4, 1.4)
    u = sm(k / 0.9)
    tb = wpos(b, (0, 2.6, -2.2))
    m.place(plus(tb, (1.5 * u, 1.0 * u, -1.5 - 9 * u)), 0.4 + 2 * u, -1.2 - 1.5 * u, 0.6 * u)
    m.apply(limp(t))
    shoot(S, SKYO, (lerp(34, 30, k), lerp(-26, -22, k), lerp(-22, -26, k)), (0, 2, lerp(-2, -10, k)), 30, roll=0.12 * k)


def roof_rush(S, k, t, lt):
    """Straight down at the station's arched glass roof among the town roofs, rushing up."""
    sky(S, 'low')
    S['hlamp'].data.energy = 2500
    z = lerp(260, 46, k ** 1.4)
    cam(S, at(STA, 2.0, -4.0, z), at(STA, 0.0, 0.0, 0.0), 24, roll=0.9 * k)


def roof_rook(S, t, look_up, talk=True):
    rk = S['rook']
    p = at(STA, 0.0, 6.0, 13.0)
    pose = blend(P('stand', head=(-0.45, 0.0), aL=(0.2, 0.3, 0.3), aR=(0.2, 0.3, 0.3)), P('hips', head=(0.1, 0.0)), 1 - look_up)
    stand(rk, p, 0.15, pose)
    return rk


def rook_ridge(S, k, t, lt):
    """Rook on the iron ridge of the station roof, looking up at a tiny figure falling out of the sky, then at us: 'Through glass? No chance.'"""
    sky(S, 'low')
    S['hlamp'].data.energy = 2500
    up = 1 - sm((k - 0.2) / 0.3)
    rk = roof_rook(S, t, up)
    S['rface'] = 'low'
    S['hat_tip'] = 0.8 * (1 - up)
    m = S['man']
    m.root.scale = (1.6, 1.6, 1.6)
    m.place(at(STA, -4.0, 46.0, 50.0 - 6 * k), 0.5 * t, -1.6, 0.4 * math.sin(t))
    m.apply(limp(t))
    h = head(rk)
    cam(S, at(STA, 1.2, 2.2, 13.7), plus(h, (-0.2, 0.4, 0.9)), 24)


# ---------------------------------------------------------------- flak
FORM = [(0, 0, 0), (-24, 20, 6), (26, 16, -5), (-46, 40, 2), (50, 36, 8)]


def formation(S, k, t, lt):
    """A formation of bombers in daylight with black flak bursts blooming all round them."""
    sky(S, 'high')
    S['bomber'].location = SKYO
    S['bomber'].rotation_euler = (0.02 * math.sin(t), 0.03 * math.sin(t * 0.7), 0)
    for i, o in enumerate(S['others']):
        p = FORM[i + 1]
        o.location = at(SKYO, p[0], p[1], p[2] + 0.6 * math.sin(t * 0.9 + i))
        o.rotation_euler = (0, 0.03 * math.sin(t + i), 0)
    clouds(S, SKYO, t, depth=-50, spread=320, vy=-30)
    flak(S, at(SKYO, -20, 30, 6), t, (120, 80, 34), n=18, size=2.6, period=1.3)
    shoot(S, SKYO, (lerp(70, 64, k), lerp(-40, -30, k), lerp(6, 4, k)), (-6, 14, 0), 28)


def flak_hit(S, k, t, lt):
    """Right under the belly: a burst beside the ball turret; the plane jolts and fragments fly."""
    sky(S, 'high')
    b = S['bomber']
    j = max(0.0, 1 - abs(k - 0.32) * 5)
    b.rotation_euler = (0.05 * j * math.sin(t * 40), 0.08 * j * math.sin(t * 33), 0)
    clouds(S, SKYO, t, depth=-60, spread=260, vy=-30)
    flak(S, at(SKYO, 0, 20, -10), t, (60, 60, 20), n=6, i0=8, size=3.0)
    bp = at(SKYO, 3.4, 5.0, -4.6)
    u = (k - 0.28)
    if u > 0:
        f, o = S['flash'][0], S['puffs'][0]
        if u < 0.12:
            fs = 2.6 * (0.6 + 4 * u)
            f.location, f.scale = bp, (fs, fs, fs)
            S['flamp'][0].location, S['flamp'][0].data.energy = bp, 50000 * (1 - u / 0.12)
        s = 0.8 + 1.8 * sm(u * 2)
        o.location, o.scale = plus(bp, (0.5 * u, 2 * u, 0)), (s, s, s)
        debris(S, wpos(b, (0.6, 2.6, -2.0)), u * 2.2, n=12, r=5.0, h=1.0, g=4.0, dirx=-1.0)
    smoke_trail(S, wpos(b, (0.3, 2.9, -2.2)), (0.0, 1.0, -0.1), t, n=6, i0=0, gap=1.2, size=0.5 * (k > 0.3))
    shoot(S, SKYO, (7.5, -7.5, -9.0), (0.6, 2.8, -1.6), 28)


def turret_climb(S, k, t, lt):
    """Inside the fuselage: he hauls himself up out of the turret hatch in the floor, smoke drifting past."""
    sky(S, 'inside')
    S['flight'].data.energy = 220
    u = act(k)
    m = S['man']
    pose = P('stand', aL=(1.3 - 0.6 * u, 0.55, 0.6 + 0.8 * (1 - u)), aR=(1.3 - 0.6 * u, 0.55, 0.6 + 0.8 * (1 - u)), lean=0.5 - 0.2 * u, head=(-0.25, 0.0))
    m.place(at(FUS, 0.0, 1.6, lerp(-2.1, -0.4, u)), facing((0.0, 1.6), (1.5, -1.3)), 0, 0)
    m.apply(pose)
    m.face = 'hard'
    m.jawv = 0.25 + 0.15 * math.sin(lt * 8)
    for i, o in enumerate(S['fsmoke']):
        v = (t * 0.35 + i / 6) % 1
        o.location = at(FUS, -1.0 + 2.0 * v, 1.0 + 2.5 * rnd(i, 48), 0.5 + 1.8 * v)
        o.scale = (0.8 + v, 0.8 + v, 0.8 + v)
    shoot(S, FUS, (1.5, -1.3, lerp(0.7, 1.4, k)), (0.0, 1.6, lerp(0.6, 1.5, k)), 26)


def act(k):
    return K.act(k)


def chute_find(S, k, t, lt):
    """He pulls the pack off its hook; it falls open and the silk drops out in rags. Behind him, Rook flinches."""
    sky(S, 'inside')
    S['flight'].data.energy = 220
    m = S['man']
    stand(m, at(FUS, 0.6, -2.6, 0), facing((0.6, -2.6), (-0.6, -5.6)), P('stand', aL=(0.75, -0.05, 1.0, 0.3), aR=(0.75, -0.05, 1.0, -0.3), head=(0.25 + 0.15 * sm((k - 0.4) / 0.3), 0.0)))
    m.face = 'wide' if k < 0.5 else 'sad'
    m.jawv = 0.3 if 0.35 < k < 0.6 else 0.05
    hl, hr = wpos(m.hands[0]), wpos(m.hands[1])
    pk = S['pack']
    pk.parent = None
    pk.location = plus(((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2, (hl[2] + hr[2]) / 2), (0, 0, -0.25))
    pk.rotation_euler = (0, 0, facing((0.6, -2.6), (-0.6, -5.6)) + PI / 2)
    u = sm((k - 0.3) / 0.6)
    for i, o in enumerate(S['rags']):
        o.location = (-0.15 - 0.1 * i * u, -0.3 + 0.075 * i, -0.4 - (0.5 + 1.0 * rnd(i, 46)) * u)
        o.rotation_euler = (0.4 * math.sin(t * 2.1 + i) * u, 0.3 * i * u, 0.3 * rnd(i, 47))
    rk = S['rook']
    jump = max(0.0, 1 - abs(k - 0.55) * 6)
    stand(rk, at(FUS, -0.7, -0.4, 0), facing((-0.7, -0.4), (-0.9, -5.8)) + 0.2, blend(P('stand'), P('scream'), jump))
    S['rface'] = 'shocked' if k > 0.45 else 'calm'
    S['hat_jump'] = 0.35 * jump
    h = head(m)
    hr_ = head(rk)
    cam(S, at(FUS, -0.9, -5.8, 2.3), ((h[0] + hr_[0]) / 2, (h[1] + hr_[1]) / 2, (h[2] + hr_[2]) / 2 - 0.5), 26)


def rook_silk(S, k, t, lt):
    """Rook holds a strip of the torn silk up to a shaft of daylight, pokes a wingtip through one of its holes, then taps his beak."""
    sky(S, 'inside')
    S['flight'].data.energy = 160
    rk = S['rook']
    poke = sm(k / 0.35) * (1 - sm((k - 0.55) / 0.15))
    tap = sm((k - 0.6) / 0.2)
    pose = P('stand', aL=(1.3, 1.1, 0.3), aR=(lerp(0.3, 1.6, poke), -0.1, lerp(0.4, 1.0, poke)), head=(-0.1, -0.35))
    pose = blend(pose, P('tap', aL=(1.3, 1.1, 0.3), head=(0.1, -0.2)), tap)
    stand(rk, at(FUS, 0.4, -2.4, 0), -1.0, pose)
    S['rface'] = 'low' if tap > 0.5 else 'calm'
    S['hat_tip'] = 0.3
    hl = wpos(rk.hands[0])
    s = S['silk']
    s.location = plus(hl, (0.0, -0.1, -0.55))
    s.rotation_euler = (0.1 * math.sin(t * 2), 0.0, -1.0 + 0.1 * math.sin(t * 1.3))
    for i, o in enumerate(S['silkholes']):
        o.location = (-0.03, -0.25 + 0.17 * i, 0.4 - 0.3 * i)
    h = head(rk)
    cam(S, plus(h, (-2.3, -1.6, -0.1)), plus(h, (0.15, 0.0, 0.0)), 34)


# ---------------------------------------------------------------- fall
def gasp_dim(S, k, t, lt):
    """Short of oxygen: he sways, mask hanging loose, gropes for a rib, his eyes drift shut and he slumps."""
    sky(S, 'inside')
    S['flight'].data.energy = lerp(220, 60, k)
    m = S['man']
    u = sm(k)
    pose = P('stand', aL=(1.6, 0.9, 0.3), aR=(0.3 + 0.3 * math.sin(t * 3), 0.4, 0.6), lean=0.1 + 0.35 * u, lift=-0.4 * u, lL=(0.3 * u, 0.6 * u), lR=(0.2 * u, 0.5 * u), head=(0.2 + 0.4 * u, 0.2))
    stand(m, at(FUS, -1.2, -0.5, 0), -0.6 + 0.12 * math.sin(t * 2.2), pose)
    m.root.rotation_euler = (0.08 * math.sin(t * 2.0), 0.15 * u + 0.06 * math.sin(t * 1.7), m.root.rotation_euler[2])
    m.face = 'tired' if k < 0.55 else 'shut'
    m.jawv = 0.35 * (1 - u)
    h = head(m)
    cam(S, plus(h, (0.9, -2.6, 0.1)), plus(h, (0.0, 0.0, -0.2)), 34, roll=0.15 * math.sin(t * 1.5) + 0.2 * u)


def thrown_clear(S, k, t, lt):
    """The bomber's broken waist: a limp figure is flung out among scraps of metal as the plane rolls away above him."""
    sky(S, 'high')
    b = S['bomber']
    S['hole_w'].hide_render = False
    b.location = at(SKYO, 0, -2 * k, 3.5 * k * k)
    b.rotation_euler = (0.1 * k, -0.6 * k, 0.05)
    clouds(S, SKYO, t, depth=-70, spread=260)
    hp = wpos(b, (1.5, 6.5, -0.2))
    u = sm(k / 0.8)
    m = S['man']
    m.place(plus(at(SKYO, 1.5, 6.5, -1.8), (4.5 * u, 0.5 * u, -3.0 * u * u)), 1.6 + 1.5 * u, -0.6 - 1.2 * u, 0.8 * u)
    m.apply(limp(t))
    m.face = 'shut'
    debris(S, hp, k * 1.6, n=12, r=6.0, h=1.0, g=5.0)
    smoke_trail(S, hp, (0.2, 1.0, 0.2), t, n=8, gap=1.6, size=0.8)
    shoot(S, SKYO, (16, -4, -5), (4, 5, -2.5), 28)


def falling_man(S, o, t, spin=0.3):
    m = S['man']
    m.place(o, spin * t, -PI / 2 + 0.3 * math.sin(t * 0.9), 0.3 * math.sin(t * 0.7))
    m.apply(limp(t))
    m.face = 'shut'
    return m


def fall_wide(S, k, t, lt):
    """From above: one limp figure turning slowly in open sky, cloud far below, the coast beyond."""
    sky(S, 'high')
    clouds(S, FALLZ, t, vz=8, depth=-90, spread=150)
    falling_man(S, FALLZ, t, 0.5)
    cam(S, at(FALLZ, 3.0, 4.0, lerp(30, 24, k)), FALLZ, 26, roll=0.4 * t)


def rook_dive(S, k, t, lt):
    """Rook dives beside him, one wingtip clamping his hat on, eyes wide, looking across at the man and then down."""
    sky(S, 'high')
    clouds(S, FALLZ, t, vz=22, depth=-30, spread=160)
    falling_man(S, at(FALLZ, 3.5, 5.0, -1.0), t, 0.6)
    rk = S['rook']
    lk = sm((k - 0.45) / 0.3)
    pose = P('hat', aL=(0.3, 0.8, 0.6), lL=(0.4, 0.5), lR=(-0.2, 0.3), head=(lerp(0.0, 0.22, lk), lerp(0.55, 0.0, lk)))
    rk.place(at(FALLZ, 0.0, 0.0, 0.15 * math.sin(t * 3)), -0.5, 0.35 + 0.05 * math.sin(t * 2.3), 0.06 * math.sin(t * 1.9))
    rk.apply(pose)
    S['rface'] = 'shocked'
    h = head(rk)
    cam(S, plus(h, (-1.6, -3.0, -0.2)), plus(h, (0.6, 0.6, -0.4)), 30)


# ---------------------------------------------------------------- re-hook
def town_below(S, k, t, lt):
    """Straight down past his boots: the town, the harbour and the long glass roof of the station growing."""
    sky(S, 'low')
    S['hlamp'].data.energy = 2500
    z = lerp(150, 90, k)
    m = S['man']
    m.place(at(STA, 0.8, -1.2, z), 0.4, PI / 2 - 0.2, 0.1 * math.sin(t))
    m.apply(limp(t))
    cam(S, at(STA, 0.0, -2.6, z + 6.0), at(STA, 0.0, 2.0, 0.0), 22, roll=0.25 * t)


def rook_look(S, k, t, lt):
    """On the station roof: Rook looks up, his hat jumps off his head, and he backs off down the glass, wings up."""
    sky(S, 'low')
    S['hlamp'].data.energy = 2500
    rk = S['rook']
    u = sm((k - 0.3) / 0.5)
    pose = blend(P('stand', head=(-0.1, 0.0)), P('scream', head=(-0.05, 0.0)), sm(k / 0.3))
    yw = facing((0.0, 6.0), (2.6, 3.4))
    stand(rk, at(STA, 0.0, 6.0 + 1.8 * u, 13.0 - 0.6 * u), yw, pose)
    rk.root.rotation_euler = (-0.2 * u, 0, yw)
    S['rface'] = 'shocked'
    jp = sm(k / 0.25) * (1 - sm((k - 0.6) / 0.4))
    S['hat_jump'] = 0.9 * jp
    m = S['man']
    m.root.scale = (1.6, 1.6, 1.6)
    m.place(at(STA, -2.0, 18.0, lerp(44, 30, k)), 0.5 * t, -1.6, 0.4 * math.sin(t))
    m.apply(limp(t))
    h = head(rk)
    cam(S, at(STA, 3.4, 3.4, 14.6), plus(h, (-0.6, 1.2, 0.5)), 24)


# ---------------------------------------------------------------- the smash
HOLE = (0.0, 0.0, 12.6)


def smash(S, k, t, lt):
    """From the platform, straight up at the arched glass roof: a section bursts inward as he comes through."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 3000
    u = (k - 0.22)
    if u > 0:
        for o in S['holep']:
            o.hide_render = True
        for o in S['edge']:
            o.hide_render = False
        glass_fall(S, at(STA, *HOLE), STA[2] + 0.1, u * 0.9, r=4.0)
        S['flamp'][0].location = at(STA, 0, 0, 10.0)
        S['flamp'][0].data.energy = 40000 * max(0, 1 - u * 5)
        m = S['man']
        m.place(at(STA, 0.6, 1.5, lerp(14.5, 8.0, u * 5)), 0.6, -1.3, 0.4)
        m.apply(limp(t))
        if u > 0.2:
            m.place(FAR)
    else:
        m = S['man']
        m.place(at(STA, 0.3, 0.6, 30 - 70 * (k)), 0.6, -1.3, 0.4)
        m.apply(limp(t))
    cam(S, at(STA, -1.5, -7.0, 1.6), at(STA, 0.0, 0.5, 12.0), 22, roll=0.3)


def shards(S, k, t, lt):
    """Glass pours down through the sunbeams; Rook at the platform edge has both wings over his head, peeking out."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 3000
    broken(S)
    glass_fall(S, at(STA, *HOLE), STA[2] + 0.1, 0.35 + 0.65 * k, r=4.0)
    dust(S, at(STA, 0, 0.5, 0.2), t, 3.0, 8.0)
    lying(S)
    rk = S['rook']
    peek = 0.5 + 0.5 * math.sin(lt * 5)
    stand(rk, at(STA, -3.0, -4.0, 0.7), facing((-3.0, -4.0), (1.6, -10.5)),
          P('stand', aL=(2.6, 0.5, 1.9, 0.3), aR=(2.6, 0.5, 1.9 - 0.4 * peek, -0.3), lift=-0.2, lean=0.2, head=(0.15, 0.0)))
    S['rface'] = 'shocked'
    cam(S, at(STA, 1.6, -10.5, 1.5), at(STA, -1.4, -1.8, 2.6), 24)


def hole_up(S, k, t, lt):
    """The hush: straight up at the ragged hole in the roof, iron ribs round it, daylight pouring through, a few last glints falling."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 2400
    broken(S)
    S['shaft'].hide_render = True
    glass_fall(S, at(STA, *HOLE), STA[2] + 0.4, 0.55 + 0.4 * k, n=10, r=2.0, seed=5)
    dust(S, at(STA, 0, 0.5, 2.0), t, 2.0, 9.0)
    cam(S, at(STA, 0.2, 0.4, 1.2), at(STA, 0.0, 0.2, 13.0), 22, roll=0.25 * t)


# ---------------------------------------------------------------- found
LIEP = P('stand', aL=(0.25, 1.0, 0.4), aR=(0.4, 0.7, 0.8), lL=(0.15, 0.3), lR=(-0.05, 0.4), head=(0.0, 0.4))


def lying(S, hand=0.0, face='shut'):
    m = S['man']
    m.place(at(STA, -0.4, -1.4, 0.38), 0.2, -PI / 2, 0.15)
    pose = dict(LIEP)
    pose['aR'] = (0.4 + 0.9 * hand, 0.7, 0.8 - 0.4 * hand, 0.0)
    m.apply(pose)
    m.face = face
    return m


def kneel(rig, loc, yaw, reach=0.0):
    rig.place(loc, yaw)
    rig.apply(P('stand', lL=(1.5, 2.3), lR=(-0.2, 1.9), lift=-0.75, lean=0.45, aL=(0.4 + 0.6 * reach, 0.2, 0.6), aR=(0.9 + 0.5 * reach, 0.1, 0.4), head=(0.4, 0.0)))
    rig.face = 'hard'


def found(S, k, t, lt):
    """Men in plain greatcoats run in and kneel beside him on the track bed among the glass; his hand moves. Rook stands back, hat to his chest."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 3000
    broken(S)
    S['shaft'].hide_render = True
    dust(S, at(STA, 0, 0.5, 0.2), t, 3.0, 8.0)
    mv = sm((k - 0.6) / 0.25)
    m = lying(S, mv * (0.6 + 0.4 * math.sin(lt * 3)), 'pain' if k > 0.6 else 'shut')
    arrive = sm(k / 0.45)
    for j, (rig, kp, yw) in enumerate(zip(S['men'], ((-1.3, -0.2), (1.0, 0.4)), (-1.4, 1.6))):
        start = (kp[0] + 0.5 - 1.5 * j, kp[1] + 7.0 + 2 * j)
        if arrive < 1:
            p = (lerp(start[0], kp[0], arrive), lerp(start[1], kp[1], arrive))
            stand(rig, at(STA, p[0], p[1], 0), facing(start, kp), K.walk(t + j * 0.3, 2.2))
            rig.face = 'hard'
        else:
            kneel(rig, at(STA, kp[0], kp[1], 0), yw, 0.5 + 0.5 * math.sin(lt * 2 + j))
    rk = S['rook']
    stand(rk, at(STA, -3.4, 0.6, 0.7), facing((-3.4, 0.6), (-0.4, -1.0)) - 0.9,
          P('stand', aR=(0.9, -0.25, 1.9, 0.6), head=(0.3, -0.3)))
    S['hat_off'], S['hat_to'] = 1.0, (0.15, -0.55, -1.0)
    S['rface'] = 'sad'
    cam(S, at(STA, -2.6, lerp(-7.5, -6.0, k), 1.7), at(STA, -1.4, -0.4, 1.1), 26)


def rook_shard(S, k, t, lt):
    """Rook picks a shard of glass off the floor, turns it in the light, looks up at the hole, then holds his wings apart to measure it."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 3000
    broken(S)
    dust(S, at(STA, -1.0, -3.0, 0.5), t, 2.0, 6.0)
    rk = S['rook']
    a = sm(k / 0.35)
    look = sm((k - 0.35) / 0.2)
    meas = sm((k - 0.62) / 0.2)
    pose = P('stand', aR=(lerp(0.5, 1.5, a), 0.1, lerp(0.3, 1.2, a), 0.4), aL=(0.2, 0.2, 0.3), lift=lerp(-0.35, 0.0, a), lean=lerp(0.4, 0.0, a), head=(lerp(0.4, -0.7, look), 0.0))
    pose = blend(pose, P('stand', aL=(1.6, 1.3, 0.1), aR=(1.6, 1.3, 0.1), head=(-0.6, 0.0)), meas)
    stand(rk, at(STA, -1.6, -4.0, 0.0), 0.35, pose)
    S['rface'] = 'shocked' if look > 0.5 else 'calm'
    hr = wpos(rk.hands[1])
    S['shard'].location = plus(hr, (0.3, -0.25, 0.1)) if meas < 0.5 else FAR
    S['shard'].rotation_euler = (t * 2, 0.5, t)
    h = head(rk)
    cam(S, plus(h, (0.9, -2.8, lerp(-0.9, -1.3, look))), plus(h, (0.0, 0.0, lerp(-0.2, 1.2, look))), 26)


def stretcher(S, k, t, lt):
    """Two of the men carry him on a stretcher along the far platform, past the locomotive, dust still in the light."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 3000
    broken(S)
    y = lerp(4.0, -2.0, k)
    st = S['stretch']
    st.location = at(STA, 4.6, y, 2.2)
    st.rotation_euler = (0, 0, 0)
    for j, rig in enumerate(S['men']):
        yy = y + (2.6 if j == 0 else -2.6)
        stand(rig, at(STA, 4.6, yy, 0.7), PI if j == 0 else 0.0, K.walk(t + 0.5 * j, 1.6))
        rig.apply(dict(K.walk(t + 0.5 * j, 1.6), aL=(0.3, 0.45, 0.2), aR=(0.3, 0.45, 0.2)))
        rig.face = 'hard'
        rig.place(at(STA, 4.6, yy, 0.7), 0.0 if j == 0 else PI)
    m = S['man']
    m.place(at(STA, 4.6, y - 1.3, 2.45), 0.0, -PI / 2, 0.0)
    m.apply(LIEP)
    m.face = 'shut'
    dust(S, at(STA, 3.0, y, 1.0), t, 3.0, 6.0)
    cam(S, at(STA, -1.2, y - 2.0, 4.4), at(STA, 4.6, y, 2.0), 24)


# ---------------------------------------------------------------- payoff
def in_bed(S, face='tired'):
    m = S['man']
    m.place(at(HOS, 0.0, 0.62, 1.32), 0.0, -PI / 2, 0.0)
    m.apply(P('stand', aL=(0.15, 0.25, 0.3), aR=(0.9, 0.2, 1.5, 0.8), head=(0.0, 0.1)))
    S['cast'].hide_render = False
    m.face = face
    return m


def room_lights(S):
    sky(S, 'room')
    S['bulb'].data.energy = 260
    S['winl'].data.energy = 500


def doctor(S, k, t, lt):
    """A plain hospital room: the gunner in bed, arm in a white cast; a doctor in a white coat bends over him, then straightens and nods."""
    room_lights(S)
    in_bed(S, 'tired' if k < 0.6 else 'calm')
    d = S['doc']
    b = sm(k / 0.3) * (1 - sm((k - 0.55) / 0.25))
    nod = max(0.0, math.sin((k - 0.8) / 0.2 * PI)) if k > 0.8 else 0.0
    stand(d, at(HOS, -1.7, 1.9, 0), facing((-1.7, 1.9), (0.0, 1.6)), P('stand', aR=(0.9 * b + 0.2, 0.1, 0.6), aL=(0.3, 0.1, 0.4), lean=0.55 * b, head=(0.3 * b + 0.35 * nod, 0.0)))
    d.face = 'calm'
    cam(S, at(HOS, 1.4, lerp(-2.6, -2.1, k), 3.1), at(HOS, -0.4, 2.2, 2.0), 26)


def rook_bed(S, k, t, lt):
    """Rook at the foot of the bed lifts his hat brim, looks at the man, and gives one slow nod."""
    room_lights(S)
    in_bed(S, 'calm')
    rk = S['rook']
    lift = sm(k / 0.4)
    nod = max(0.0, math.sin((k - 0.5) / 0.4 * PI)) if 0.5 < k < 0.9 else 0.0
    stand(rk, at(HOS, 0.6, -2.0, 0), PI + 0.15, blend(P('stand', head=(0.15, 0.0)), P('hat', head=(-0.05 + 0.4 * nod, 0.0)), lift))
    S['hat_tip'] = lerp(0.6, -0.3, lift)
    S['rface'] = 'soft'
    h = head(rk)
    cam(S, plus(h, (1.4, 2.6, 0.2)), plus(h, (0.0, 0.0, -0.1)), 34)


def camp(S, k, t, lt):
    """Snow, a wire fence, a wooden hut: the gunner at the wire, arm in a sling; Rook perched on a fence post beside him."""
    sky(S, 'snow')
    m = S['man']
    stand(m, at(CMP, 0.6, -1.0, 0), PI, P('stand', aR=(0.9, 0.2, 1.5, 0.8), aL=(0.1, 0.15, 0.2), head=(-0.05 + 0.1 * sm((k - 0.5) / 0.3), -0.6 * sm((k - 0.3) / 0.3))))
    S['cast'].hide_render = S['sling'].hide_render = False
    m.face = 'sad'
    rk = S['rook']
    rk.place(at(CMP, -1.8, 0.0, 3.36 - 0.55), PI - 0.4)
    rk.apply(P('sit', lL=(1.3, 1.8), lR=(1.2, 1.7), aL=(0.4, 0.3, 1.2), aR=(0.4 + 0.5 * sm((k - 0.55) / 0.3), 0.3, 1.2 + 0.6 * sm((k - 0.55) / 0.3)), head=(0.15 + 0.2 * sm((k - 0.6) / 0.3), -0.2 + 0.5 * sm((k - 0.4) / 0.3))))
    S['rface'] = 'sad'
    S['hat_tip'] = 0.5
    for i, o in enumerate(S['flakes']):
        z = 6 - ((t * 1.6 * (0.7 + 0.6 * rnd(i, 120)) + rnd(i, 121) * 6) % 6)
        o.location = at(CMP, -4 + 9 * rnd(i, 122) + 0.3 * math.sin(t + i), 0.5 + 6 * rnd(i, 123), z)
    cam(S, at(CMP, lerp(3.2, -1.6, k), lerp(8.0, 5.6, k), lerp(3.2, 2.4, k)), at(CMP, -0.5, -0.4, 2.3), 30)


# ---------------------------------------------------------------- end
def memorial(S, k, t, lt):
    """A quiet town square: a plain stone memorial, a wreath at its foot; Rook beside it, hat off, head lowered."""
    sky(S, 'square')
    rk = S['rook']
    bow = sm((k - 0.3) / 0.4)
    stand(rk, at(MEM, 2.1, -2.0, 0), facing((2.1, -2.0), (0, 0)) - 0.4, blend(P('stand', aR=(0.1, 0.2, 0.2), head=(0.15, 0.25)), P('stand', aR=(0.9, -0.25, 1.9, 0.6), head=(0.5, 0.25)), bow))
    S['hat_off'], S['hat_to'] = 1.0, (lerp(0.74, 0.15, bow), lerp(-0.14, -0.55, bow), lerp(-1.45, -1.0, bow))
    S['rface'] = 'sad'
    cam(S, at(MEM, lerp(5.6, 3.0, k), lerp(-14.0, -7.6, k), lerp(4.2, 2.6, k)), at(MEM, 1.0, -0.8, lerp(3.0, 2.4, k)), 30)


def wreath(S, k, t, lt):
    """Close on the wreath at the foot of the stone; Rook, crouched beside it, lays one more flower on it."""
    sky(S, 'square')
    rk = S['rook']
    u = sm(k / 0.7)
    rk.place(at(MEM, 1.1, -2.9, 0), facing((1.1, -2.9), (0, -1.95)))
    rk.apply(P('stand', lL=(1.4, 2.2), lR=(0.2, 1.8), lift=-0.75, lean=0.5, aR=(lerp(1.2, 0.8, u), 0.1, 0.3), aL=(0.3, 0.2, 0.6), head=(0.4, 0.0)))
    S['hat_off'] = 1.0
    S['rface'] = 'sad'
    hr = wpos(rk.hands[1])
    fl = S['flower']
    fl.location = plus(hr, (0, 0, -0.1))
    fl.rotation_euler = (lerp(0.0, 1.2, u), 0, 0.6)
    for i, o in enumerate(S['petals']):
        a = i * 2 * PI / 12
        o.location = (0.7 * math.cos(a) + 0.02 * math.sin(t * 3 + i), -0.12, 0.6 + 0.7 * math.sin(a))
    cam(S, at(MEM, -1.4, lerp(-6.6, -6.0, k), 1.6), at(MEM, 0.6, -2.3, 1.4), 28)


def signoff(S, k, t, lt):
    """Back under the hole in the station roof: Rook puts his hat back on, tugs the brim, holds up the glass shard so it glints, and pockets it."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 3000
    broken(S)
    dust(S, at(STA, -1.0, -1.2, 0.5), t, 2.5, 7.0)
    rk = S['rook']
    on = sm(k / 0.3)
    show = sm((k - 0.3) / 0.2) * (1 - sm((k - 0.72) / 0.18))
    pose = blend(P('hat'), P('stand', aR=(1.9, 0.0, 0.6, 0.4), head=(-0.2, 0.0)), show)
    if k > 0.75:
        pose = blend(pose, P('stand', aR=(0.1, 0.35, 0.6, 0.8), head=(0.0, 0.0)), sm((k - 0.75) / 0.2))
    stand(rk, at(STA, -1.0, -1.2, 0.0), 0.3, pose)
    S['hat_off'] = 1 - on
    S['hat_to'] = (0.0, 0.0, 0.9)
    S['hat_tip'] = 0.4
    S['rface'] = 'low'
    hr = wpos(rk.hands[1])
    S['shard'].location = plus(hr, (0, -0.15, 0.25)) if k < 0.9 else FAR
    S['shard'].rotation_euler = (t * 1.5, 0.6, t)
    S['flamp'][0].location = plus(hr, (0.2, -0.6, 0.4))
    S['flamp'][0].data.energy = 300 * show
    h = head(rk)
    cam(S, at(STA, -1.8, lerp(-6.2, -5.0, k), 1.5), plus(h, (0.0, 0.0, -0.3)), 30)


def photo_hole(S, k, t, lt):
    """For the case board: the ragged hole in the station roof, from the floor."""
    sky(S, 'hall')
    S['hlamp'].data.energy = 2400
    broken(S)
    S['shaft'].hide_render = True
    cam(S, at(STA, 0.2, -3.0, 1.2), at(STA, 0.0, 0.4, 13.0), 24)


SHOTS3D = {f.__name__: f for f in (
    turret_close, chute_rags, bomber_down, roof_rush, rook_ridge, formation, flak_hit, turret_climb, chute_find, rook_silk,
    gasp_dim, thrown_clear, fall_wide, rook_dive, town_below, rook_look, smash, shards, hole_up, found, rook_shard, stretcher,
    doctor, rook_bed, camp, memorial, wreath, signoff)}
STILLS = dict(hole=photo_hole)


# ================================================================ long-form extension (16:9 full case file)
# The Short's sky, turret, fuselage, station, hospital room, camp fence and square stay as they were. New for the full
# case, each built at its own origin and shown only in its own shots: an airfield in England at dawn with the bomber
# parked on it, the harbour of Saint-Nazaire seen from the bombers, a grass airfield at home after the war with a small
# high-wing aeroplane, and a table with two medals. New things in the old sets: a wall, a door and a plaster cast in the
# hospital room, a gate in the camp fence, steam at the station, a piece of wing that breaks away. New figures: the
# gunner as an older man, and his wife.
# Everything is generic: the aircraft carry no markings, names or nose art, the medals are plain shapes with no portrait
# or lettering, the harbour is a sketch and not a plan, nobody's likeness is attempted, no flag or emblem appears, and
# nobody who died is shown dying.
BASE, PORT, HOME, DESK = (9000.0, 9000.0, 0.0), (9000.0, -9000.0, 0.0), (-9000.0, -9000.0, 0.0), (-9000.0, 9000.0, 0.0)
GX = 40.0                                                    # the camp gate, along the fence line
SKIES.update(dawn=('F4C8A0', '6A86B4', 1.0, 2.8, 'FFD0A0', (0.75, -0.45, 0.24)),
             port=('C8D6E2', '5A86BC', 1.2, 3.4, 'FFF0D8', (0.45, -0.55, 0.62)),
             spring=('D8E6F0', '6A9AD0', 1.2, 3.2, 'FFF4DC', (0.4, 0.5, 0.6)),
             gold=('FFD8A0', '6A8CC0', 1.1, 3.4, 'FFC880', (0.6, -0.6, 0.3)),
             den=('4A4038', '2A241E', 0.3, 0.0, 'FFFFFF', (0, 0, 1)),
             dusk=('F2A870', '3A4A7A', 0.9, 2.4, 'FFB070', (0.5, -0.7, 0.22)),
             ward=('3A3C44', '1E2028', 0.3, 0.0, 'FFFFFF', (0, 0, 1)))
CAMFILL.update(field_dawn=500, turret_under=260, rook_measure=260, turret_side=40, pack_hook=260, nose_fly=0, pens=0, wing_hit=0,
               spin_down=0, fuse_spin=200, fall_close=260, station_out=0, girders=900, bed_leg=160, arm_close=140, doc_talk=260,
               arm_wrap=240, bed_sit=260, camp_three=500, gate_open=400, medals=160, hangar_walk=400, cub_fly=300, mem_visit=420,
               rook_verdict=300)
HOST |= {'field_dawn', 'turret_under', 'rook_measure', 'girders', 'arm_wrap', 'bed_sit', 'gate_open', 'medals', 'hangar_walk',
         'mem_visit', 'rook_verdict'}
_MESH = {}


def qadd(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """Like kit3d.add, but each shape's mesh is made once and copied: the operator gets slower with every object."""
    key = (kind,) + tuple(sorted(kw.items()))
    me = _MESH.get(key)
    if me is None:
        getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(**kw)
        o = bpy.context.object
        me = _MESH[key] = o.data
        me.use_fake_user = True
        bpy.data.objects.remove(o)
    o = bpy.data.objects.new(kind, me.copy())
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    o.data.materials.append(K.mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    if parent:
        o.parent = parent
    return o


def qe(parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    o = bpy.data.objects.new('e', None)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    return o


def qb(par, col, x0, x1, y0, y1, z0, z1, **kw):
    return qadd('cube', col, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), scale=(x1 - x0, y1 - y0, z1 - z0), size=1, parent=par, **kw)


def qc(par, col, loc, r, d, n=8, rot=(0, 0, 0), **kw):
    return qadd('cylinder', col, loc, rot=rot, scale=(r, r, d), radius=1, depth=1, vertices=n, parent=par, **kw)


def qs(par, col, loc, r, sc=(1, 1, 1), sub=1, **kw):
    return qadd('ico_sphere', col, loc, scale=(r * sc[0], r * sc[1], r * sc[2]), radius=1, subdivisions=sub, parent=par, **kw)


def qcone(par, col, loc, r1, r2, d, n=8, rot=(0, 0, 0), **kw):
    return qadd('cone', col, loc, rot=rot, scale=(r1, r1, d), radius1=1, radius2=round(r2 / r1, 3), depth=1, vertices=n, parent=par, **kw)


def qbar(par, col, a, b, w, **kw):
    o = qadd('cylinder', col, radius=0.5, depth=1, vertices=6, parent=par, **kw)
    span(o, a, b, w)
    return o


def bump(k, a, b, e=0.12):
    """0 outside a..b, 1 inside, eased over e at both ends."""
    return sm((k - a) / e) * (1 - sm((k - b) / e))


# ---------------------------------------------------------------- airfield in England, dawn
def make_base(r, S):
    qb(r, '5E7A48', -500, 500, -500, 500, -0.3, 0.0, rough=1.0)
    qb(r, '8E8E86', -34, 34, -40, 30, 0.0, 0.05, rough=1.0)                       # the hardstand
    qb(r, '7E7E78', -500, 500, -78, -56, 0.0, 0.04, rough=1.0)                    # perimeter track
    for i in range(26):                                                            # worn patches and tufts
        qb(r, ('6E8A52', '56703E', '7A8E58')[i % 3], -200 + 400 * rnd(i, 201), -190 + 400 * rnd(i, 201) + 30 * rnd(i, 202),
           -200 + 400 * rnd(i, 203), -170 + 400 * rnd(i, 203) + 30 * rnd(i, 204), 0.0, 0.02 + 0.002 * i, rough=1.0)
    b = qe(r, (0, 0, 3.9), (-0.13, 0, 0))                                          # the bomber, tail down on its wheels
    bomber_body(b)
    for s in (-1, 1):
        qbar(b, '2A2C2E', (s * 5.8, -5.2, -0.8), (s * 5.8, -4.6, -3.5), 0.26)
        qc(b, '17181A', (s * 5.8, -4.6, -3.5), 1.0, 0.7, 12, rot=(0, PI / 2, 0), rough=0.8)
        qc(b, '6E7276', (s * 5.8, -4.6, -3.5), 0.4, 0.74, 8, rot=(0, PI / 2, 0))
    qbar(b, '2A2C2E', (0, 13.6, -0.5), (0, 14.0, -1.63), 0.16)
    qc(b, '17181A', (0, 14.0, -1.63), 0.45, 0.3, 10, rot=(0, PI / 2, 0), rough=0.8)
    for s in (-1, 1):                                                               # wheel chocks
        qb(r, 'C8A030', s * 5.8 - 0.5, s * 5.8 + 0.5, -6.1, -5.7, 0.05, 0.4)
    # control tower, huts, trees, drums, a windsock
    qb(r, 'B8B4A4', -92, -76, 52, 66, 0, 9.0, rough=1.0)
    qb(r, '2E3A44', -91, -77, 51.6, 52.0, 6.0, 8.4, rough=0.2)
    qb(r, 'A8A494', -93, -75, 51, 67, 9.0, 9.4)
    qb(r, 'C8C4B4', -88, -80, 55, 63, 9.4, 12.4, rough=1.0)
    qb(r, 'DCEAF2', -88.2, -79.8, 54.8, 63.2, 10.2, 11.8, emit=1.2)
    for i, (x, y) in enumerate(((-40, 70), (-10, 74), (30, 72), (64, 66))):
        qc(r, ('5A5E4A', '4E5444')[i % 2], (x, y, 0), 5.0, 22, 12, rot=(0, PI / 2, 0), rough=0.8)
        qb(r, 'FFD89A', x - 11.05, x - 10.95, y - 0.8, y + 0.8, 1.4, 3.0, emit=1.2)
    for i in range(34):
        x = -260 + 16 * i + 6 * rnd(i, 205)
        hh = 9 + 7 * rnd(i, 206)
        qc(r, '4A3A2A', (x, 120 + 8 * rnd(i, 207), hh * 0.25), 0.5, hh * 0.5, 6)
        qs(r, ('3E5A36', '34502E', '4A6A3E')[i % 3], (x, 120 + 8 * rnd(i, 207), hh * 0.75), hh * 0.42, (1, 1, 1.2), rough=1.0)
    for i, (x, y) in enumerate(((7.4, -30.3), (6.1, -29.9), (6.9, -29.0))):
        qc(r, ('7A3A2A', '5E6240', '6A6A64')[i], (x, y, 0.85), 0.6, 1.7, 10, rough=0.6)
        qc(r, '2A2C2E', (x, y, 1.705), 0.56, 0.02, 10)
    qbar(r, 'D8D8D0', (46, -30, 0), (46, -30, 9), 0.2)
    qcone(r, 'F06A20', (47.8, -30, 8.6), 0.7, 0.25, 3.6, 8, rot=(0, -PI / 2, 0), rough=1.0)
    for i in range(7):                                                              # dawn mist lying on the grass
        qs(r, 'FFE6CC', (-180 + 60 * i, 60 + 20 * rnd(i, 208), 2.0), 30, (1.6, 0.8, 0.12), 2, emit=0.15, alpha=0.12)
    return dict(lights=[])


# ---------------------------------------------------------------- the harbour from the bombers
def make_port(r, S):
    qb(r, '2E5070', -3000, 3000, -3000, 3000, -2.0, 0.0, rough=0.45)
    qb(r, '7C7A6E', -3000, -40, -3000, 3000, 0.0, 1.0, rough=1.0)                  # the land
    qb(r, '2E5070', -262, -39, -120, 120, 0.9, 1.3, rough=0.45)                    # the basin
    for s in (-1, 1):
        qb(r, '8A8880', -60, 90, s * 132 - 6, s * 132 + 6, 0.0, 2.0, rough=1.0)   # the moles
    qb(r, 'B4B0A4', -430, -262, -112, 112, 1.0, 19.0, rough=1.0)                   # the concrete pens
    qb(r, 'C2BEB2', -426, -266, -108, 108, 19.0, 19.6, rough=1.0)
    for i in range(14):
        y = -104 + 15.2 * i
        qb(r, '12161A', -264.5, -261.5, y, y + 11.0, 1.4, 12.5, rough=0.6)
        qb(r, '9A968A', -426, -266, y - 2.1, y - 1.7, 19.6, 19.9)
    for i in range(190):                                                            # the town: blocks and roofs
        x = -1500 + 1420 * rnd(i, 211)
        y = -1300 + 2600 * rnd(i, 212)
        if -450 < x < -250 and abs(y) < 130:
            continue
        w, d, hh = 26 + 40 * rnd(i, 213), 22 + 46 * rnd(i, 214), 8 + 12 * rnd(i, 215)
        qb(r, ('D8CCB4', 'C8B8A0', 'E2D8C4', 'B8A890')[i % 4], x - w / 2, x + w / 2, y - d / 2, y + d / 2, 1.0, 1.0 + hh, rough=1.0)
        qb(r, ('7A5240', '5A5E68', '6A4A3A')[i % 3], x - w * 0.42, x + w * 0.42, y - d * 0.42, y + d * 0.42, 1.0 + hh, 2.6 + hh, rough=1.0)
    for i in range(60):                                                             # fields behind the town
        x = -2900 + 1300 * rnd(i, 216)
        y = -2800 + 5600 * rnd(i, 217)
        qb(r, ('5E7044', '7A7A50', '4E6038', '8A7E5A')[i % 4], x - 90 - 120 * rnd(i, 218), x + 90, y - 80 - 120 * rnd(i, 219), y + 80, 0.9, 1.1 + 0.004 * i, rough=1.0)
    qb(r, '3A3C40', -1500, -560, 236, 244, 1.0, 1.6)                                # the railway, and the station's long roof
    qb(r, 'BFE2EE', -570, -500, 222, 258, 1.0, 14.0, rough=0.1, emit=0.5)
    for i in range(8):
        qb(r, '2E3236', -570 + 10 * i - 0.6, -570 + 10 * i + 0.6, 221, 259, 1.0, 14.4)
    for i in range(7):                                                              # cranes on the quay
        qbar(r, '3A3E44', (-250 + 30 * i, 128, 1), (-250 + 30 * i, 128, 24), 1.6)
        qbar(r, '3A3E44', (-250 + 30 * i, 128, 24), (-250 + 30 * i, 112, 20), 1.0)
    for i, (x, y, a) in enumerate(((-150, 40, 0.1), (-110, -60, 1.5), (60, 240, 0.6), (220, -180, 0.3), (400, 60, 1.2))):
        h = qe(r, (x, y, 1.3), (0, 0, a))
        qb(h, '6E7276', -22, 22, -5, 5, 0, 5, rough=0.6)
        qb(h, '8E9296', -8, 6, -3.5, 3.5, 5, 9, rough=0.6)
    return dict(lights=[])


# ---------------------------------------------------------------- a grass airfield at home, years later
def make_home(r, S):
    qb(r, '86A052', -3000, 3000, -3000, 3000, -0.3, 0.0, rough=1.0)
    for i in range(110):                                                            # the quilt of fields
        x = -2400 + 4800 * rnd(i, 221)
        y = -2400 + 4800 * rnd(i, 222)
        if abs(x) < 190 and abs(y) < 130:
            continue
        qb(r, ('D8B45A', '6E9048', '9A7A4A', 'C8C27A', '7EA050')[i % 5], x - 80 - 170 * rnd(i, 223), x + 80 + 100 * rnd(i, 224),
           y - 70 - 160 * rnd(i, 225), y + 70 + 90 * rnd(i, 226), 0.0, 0.05 + 0.004 * i, rough=1.0)
    qb(r, '98B060', -260, 260, -52, -28, 0.0, 0.05, rough=1.0)                     # the mown strip
    h = qe(r, (-30, 26, 0))                                                         # the hangar
    qb(h, 'B8B0A0', -13, 13, -9, 9, 0, 7.5, rough=1.0)
    qc(h, '8A8E92', (0, 0, 7.5), 13.0, 18.4, 14, rot=(PI / 2, 0, 0), rough=0.5)
    qb(h, '1E2226', -10, 10, -9.2, -8.9, 0, 6.6, rough=0.8)
    qb(h, '8A6A48', -10.4, -3.0, -9.5, -9.3, 0, 6.8)
    for i in range(22):                                                             # a fence and a line of trees
        qb(r, '7A6A54', -66 + 6 * i - 0.12, -66 + 6 * i + 0.12, 43.9, 44.1, 0, 1.4)
    qb(r, '7A6A54', -66, 66, 43.95, 44.05, 1.0, 1.12)
    for i in range(26):
        x = -200 + 16 * i + 6 * rnd(i, 227)
        hh = 8 + 6 * rnd(i, 228)
        qc(r, '4A3A2A', (x, 64 + 10 * rnd(i, 229), hh * 0.25), 0.5, hh * 0.5, 6)
        qs(r, ('5A7A3A', '6A8A40', '4E6E34')[i % 3], (x, 64 + 10 * rnd(i, 229), hh * 0.78), hh * 0.44, (1, 1, 1.1), rough=1.0)
    qb(r, '9A3A2E', 60, 78, 70, 84, 0, 9, rough=1.0)                               # a barn
    qb(r, '5A3A30', 59, 79, 69, 85, 9, 9.6)
    qbar(r, 'D8D8D0', (24, 20, 0), (24, 20, 8), 0.18)
    qcone(r, 'F06A20', (25.6, 20, 7.6), 0.6, 0.22, 3.2, 8, rot=(0, -PI / 2, 0), rough=1.0)
    for i in range(3):
        qc(r, ('7A3A2A', '3A5A7A', '6A6A64')[i], (-12.5 + 1.3 * i, 15.0 - 0.4 * i, 0.85), 0.6, 1.7, 10, rough=0.6)
    return dict(lights=[])


def make_cub(S):
    """A small high-wing aeroplane with an open-sided cabin, nose towards -Y, main wheels on the ground at the origin."""
    c = keep(qe(None, FAR))
    Y = 'F2C230'
    qb(c, Y, -0.62, 0.62, -2.3, 1.5, 0.95, 1.75)                                   # cabin, lower half
    qb(c, '2A2C2E', -0.6, 0.6, -2.2, 1.4, 0.9, 1.0)
    for sx in (-0.6, 0.6):
        for y in (-2.25, -0.3, 1.45):
            qbar(c, Y, (sx, y, 1.75), (sx, y, 2.72), 0.07)
    qb(c, Y, -0.55, 0.55, -3.5, -2.3, 1.0, 1.8)                                     # the cowling
    qc(c, '2A2C2E', (0, -3.52, 1.4), 0.36, 0.08, 10, rot=(PI / 2, 0, 0))
    qcone(c, 'D8D8D0', (0, -3.72, 1.4), 0.14, 0.02, 0.36, 8, rot=(PI / 2, 0, 0), rough=0.3)
    S['cubblade'] = qb(c, '3A2A1E', -1.35, 1.35, -3.62, -3.56, 1.32, 1.48)
    S['cubdisc'] = qc(c, 'C8C4B8', (0, -3.6, 1.4), 1.4, 0.02, 20, rot=(PI / 2, 0, 0), alpha=0.16)
    qcone(c, Y, (0, 3.8, 1.5), 0.62, 0.16, 4.7, 6, rot=(-PI / 2, 0, 0))             # tail boom
    qb(c, Y, -6.6, 6.6, -2.0, -0.3, 2.72, 2.9)                                      # the wing
    qb(c, 'E0B020', -6.6, 6.6, -2.06, -1.98, 2.74, 2.88)
    for s in (-1, 1):
        qbar(c, Y, (s * 0.62, -1.9, 1.0), (s * 3.4, -1.6, 2.72), 0.07)
        qbar(c, Y, (s * 0.62, -0.5, 1.0), (s * 3.4, -0.8, 2.72), 0.07)
        qbar(c, '2A2C2E', (s * 0.55, -1.7, 1.0), (s * 1.15, -1.9, 0.45), 0.09)
        qc(c, '17181A', (s * 1.2, -1.9, 0.45), 0.45, 0.28, 12, rot=(0, PI / 2, 0), rough=0.8)
        qc(c, Y, (s * 1.36, -1.9, 0.45), 0.2, 0.04, 8, rot=(0, PI / 2, 0))
    qb(c, Y, -1.9, 1.9, 5.3, 6.3, 1.5, 1.6)
    qb(c, Y, -0.05, 0.05, 5.1, 6.3, 1.55, 2.9)
    qbar(c, '2A2C2E', (0, 5.8, 1.3), (0, 6.0, 0.95), 0.06)
    qc(c, '17181A', (0, 6.0, 0.95), 0.16, 0.1, 8, rot=(0, PI / 2, 0))
    qb(c, '5A4A3A', -0.4, 0.4, -1.3, -0.7, 1.0, 1.2)                                # the seat
    S['cub'] = c


# ---------------------------------------------------------------- a table with two medals
def make_desk(r, S):
    qb(r, '4A3A2C', -8, 8, -8, 6, -0.1, 0.0)
    qb(r, '6A5644', -8, 8, 3.0, 3.2, 0, 7, rough=1.0)                               # panelled wall
    for i in range(9):
        qb(r, '5A4838', -8 + 2 * i - 0.05, -8 + 2 * i + 0.05, 2.95, 3.0, 0, 7)
    qb(r, '5A4838', -8, 8, 2.94, 3.0, 2.6, 2.75)
    qb(r, 'FFD8A0', 3.4, 6.2, 2.9, 3.0, 2.9, 5.6, emit=1.6)                          # window, evening
    qb(r, '4A3828', 3.3, 6.3, 2.88, 2.98, 4.2, 4.3)
    qb(r, '4A3828', 4.75, 4.85, 2.88, 2.98, 2.8, 5.7)
    qb(r, '3A2A1E', -5.6, -3.4, 2.9, 3.0, 3.2, 5.0)                                  # a frame with nothing in it
    qb(r, 'C8BEA8', -5.4, -3.6, 2.88, 2.92, 3.4, 4.8, rough=1.0)
    qb(r, '6A4A30', -3.2, 3.2, -1.2, 1.0, 1.45, 1.6, rough=0.5)                      # the table
    for sx in (-2.9, 2.9):
        for sy in (-0.95, 0.75):
            qb(r, '5A3E28', sx - 0.1, sx + 0.1, sy - 0.1, sy + 0.1, 0, 1.45)
    qc(r, '3A3A3E', (2.4, 0.4, 1.66), 0.3, 0.1, 10)                                  # a lamp
    qbar(r, '3A3A3E', (2.4, 0.4, 1.7), (2.4, 0.4, 2.7), 0.06)
    qcone(r, 'D8B070', (2.4, 0.4, 2.9), 0.55, 0.25, 0.6, 10, emit=1.2)
    t = qe(r, (-0.5, -0.15, 1.62), (0.75, 0, 0.06))                                  # the open case, tilted towards us
    qb(t, '1E2A4A', -1.25, 1.25, -0.75, 0.75, 0.0, 0.1, rough=1.0)
    qb(t, '2A3A66', -1.15, 1.15, -0.65, 0.65, 0.1, 0.14, rough=1.0)
    # a heart-shaped medal on a purple ribbon (plain: no portrait, no lettering)
    qb(t, '6A2A8A', -0.78, -0.42, -0.02, 0.56, 0.14, 0.18, rough=0.7)
    for sx in (-0.79, -0.43):
        qb(t, 'F2F0EA', sx - 0.02, sx + 0.02, -0.02, 0.56, 0.14, 0.185, rough=0.7)
    for sx in (-0.7, -0.5):
        qs(t, 'D8A838', (sx, -0.2, 0.17), 0.15, (1, 1, 0.25), 2, rough=0.25)
        qs(t, '6A2A8A', (sx, -0.2, 0.19), 0.105, (1, 1, 0.25), 2, rough=0.4)
    qcone(t, 'D8A838', (-0.6, -0.38, 0.17), 0.21, 0.01, 0.3, 4, rot=(PI / 2, 0, 0), rough=0.25).scale = (0.21, 0.04, 0.3)
    # a round bronze medal on a blue ribbon with two orange stripes
    qb(t, '2A4A9A', 0.42, 0.78, -0.02, 0.56, 0.14, 0.18, rough=0.7)
    for sx in (0.51, 0.69):
        qb(t, 'F08A20', sx - 0.035, sx + 0.035, -0.02, 0.56, 0.14, 0.185, rough=0.7)
    qc(t, 'A8703A', (0.6, -0.26, 0.17), 0.24, 0.04, 16, rough=0.25)
    for i in range(8):
        a = i * PI / 4
        qcone(t, 'C88A4A', (0.6 + 0.13 * math.cos(a), -0.26 + 0.13 * math.sin(a), 0.195), 0.05, 0.005, 0.16, 3, rot=(PI / 2, 0, a - PI / 2), rough=0.25)
    S['desk_case'] = t
    l = light(at(DESK, 1.6, -0.6, 3.6), 0, 'FFD8A0', size=1.5)
    return dict(lights=[l])


MAKERS = dict(base=(BASE, make_base), port=(PORT, make_port), home=(HOME, make_home), desk=(DESK, make_desk))


# ---------------------------------------------------------------- new things in the Short's sets
def make_extras(S):
    X = S['x'] = {}
    # hospital: a right-hand wall with a door, a second bed, a leg in plaster on a frame, a chart, a roll of bandage
    r = S['hosp']
    hx = [qb(r, 'DCD4C0', 5.0, 5.2, -6, 4, 0, 6, rough=1.0), qb(r, '6E8A74', 4.95, 5.0, -6, 4, 0, 2.0), qb(r, '8A8478', -6, 6, -9, -5, -0.1, 0.0),
          qb(r, '7A5A3C', 4.92, 5.0, -3.6, -1.6, 0, 4.4), qb(r, 'C8A040', 4.86, 4.92, -1.95, -1.8, 2.1, 2.3, rough=0.3),
          qb(r, 'F2F0EA', 2.9, 4.7, -0.9, 3.4, 0.9, 1.3, rough=1.0), qb(r, '8A9AAA', 2.88, 4.72, -0.92, 1.9, 1.3, 1.44, rough=1.0),
          qb(r, 'F6F4EE', 3.2, 4.4, 2.6, 3.3, 1.3, 1.6, rough=1.0), qb(r, 'DCD4C0', -4.5, 5.2, -6.2, -6.0, 0, 6, rough=1.0)]
    for x in (2.95, 4.65):
        for y in (-0.85, 3.35):
            hx.append(qbar(r, 'E8E8E4', (x, y, 0), (x, y, 1.7), 0.08, rough=0.4))
    hx.append(qb(r, 'C8B890', -0.35, 0.35, -1.2, -1.14, 0.9, 1.75, rough=1.0))                              # the chart at the foot of the bed
    hx.append(qb(r, 'F2EEE0', -0.28, 0.28, -1.22, -1.2, 1.0, 1.65, rough=1.0))
    X['hosp'] = hx
    lg = [qc(r, 'F4F2EC', (-0.45, 0.2, 1.95), 0.2, 1.7, 8, rot=(PI / 2 - 0.25, 0, 0), rough=1.0)]
    for y in (-1.0, 1.0):
        lg.append(qbar(r, 'B8B8B4', (-1.0, y, 1.5), (-1.0, y, 3.4), 0.05, rough=0.4))
    lg.append(qbar(r, 'B8B8B4', (-1.0, -1.0, 3.4), (-1.0, 1.0, 3.4), 0.05, rough=0.4))
    lg.append(qbar(r, 'B8B8B4', (-1.0, -0.3, 3.4), (-0.45, -0.3, 3.4), 0.05, rough=0.4))
    lg.append(qbar(r, 'D8D4C8', (-0.45, -0.3, 3.4), (-0.45, -0.35, 2.2), 0.025, rough=1.0))
    X['leg'] = lg
    S['roll'] = keep(qc(None, 'F4F2EC', FAR, 0.11, 0.2, 8, rough=1.0))
    # camp: a gate in the wire, a road through it, huts with bare roofs, and the same ground without the snow
    r = S['camp']
    gx = [qb(r, '7E9A56', -100, 100, -100, 100, 0.0, 0.03, rough=1.0), qb(r, '8A7A60', GX - 2.3, GX + 2.3, -60, 40, 0.03, 0.05, rough=1.0)]
    for i in range(9):
        x = 26 + 3.2 * i
        if abs(x - GX) < 3:
            continue
        gx.append(qb(r, '4A3A2A', x - 0.09, x + 0.09, -0.09, 0.09, 0, 3.4))
    for z in (0.5, 1.1, 1.7, 2.3, 2.9):
        gx.append(qb(r, '3A3C40', 26, GX - 2.7, 0.01, 0.03, z - 0.012, z + 0.012, rough=0.4))
        gx.append(qb(r, '3A3C40', GX + 2.7, 56, 0.01, 0.03, z - 0.012, z + 0.012, rough=0.4))
    for s in (-1, 1):
        gx.append(qb(r, '4A3A2A', GX + s * 2.7 - 0.2, GX + s * 2.7 + 0.2, -0.2, 0.2, 0, 4.2))
    gx.append(qb(r, '4A3A2A', GX - 2.9, GX + 2.9, -0.15, 0.15, 4.2, 4.5))
    S['gleaf'] = []
    for s in (-1, 1):
        lf = qe(r, (GX + s * 2.5, 0, 0))
        gx.append(lf)
        for z in (0.3, 3.3):
            gx.append(qb(lf, '5A4A34', -s * 2.4 if s > 0 else 0, 0 if s > 0 else 2.4, -0.05, 0.05, z - 0.06, z + 0.06))
        for q in (0.05, 1.2, 2.35):
            gx.append(qb(lf, '5A4A34', -s * q - 0.05, -s * q + 0.05, -0.05, 0.05, 0.3, 3.3))
        for z in (0.9, 1.5, 2.1, 2.7):
            gx.append(qb(lf, '3A3C40', -s * 2.4 if s > 0 else 0, 0 if s > 0 else 2.4, -0.012, 0.012, z - 0.012, z + 0.012))
        gx.append(qbar(lf, '5A4A34', (-s * 0.05, 0, 0.3), (-s * 2.35, 0, 3.3), 0.06))
        S['gleaf'].append(lf)
    for i, (x, y) in enumerate(((GX - 15, -24), (GX + 13, -27), (GX - 4, -44))):
        gx.append(qb(r, ('6A5A44', '625240', '6E5E48')[i], x - 8, x + 8, y - 2.5, y + 2.5, 0, 3.0, rough=1.0))
        for s in (-1, 1):
            o = qb(r, '3A3430', x - 8.3, x + 8.3, y + s * 1.4 - 1.7, y + s * 1.4 + 1.7, 3.5, 3.7)
            o.rotation_euler = (s * 0.55, 0, 0)
            gx.append(o)
        for wx in (-5, -1, 3):
            gx.append(qb(r, '2E3A44', x + wx, x + wx + 1.0, y + 2.5, y + 2.56, 1.3, 2.1, rough=0.3))
    X['gate'] = gx
    # station: steam from the locomotive, and a forecourt where the nearest houses stood
    S['steam'] = [keep(qs(None, ('F2F2F0', 'E4E6E8')[i % 2], FAR, 1.0, sub=1, rough=1.0, alpha=0.5)) for i in range(8)]
    tw = max((c for c in S['station'].children if c.type == 'EMPTY'), key=lambda c: len(c.children))
    S['fronts'] = [o for o in tw.children if abs(o.location.x) < 34 and -125 < o.location.y < -34 and o.scale.x < 100]
    X['court'] = [qb(S['station'], '8E8A80', -34, 34, -125, -29, -0.1, 0.02, rough=1.0)]
    for x in (-9.0, 0.0, 9.0):
        for d in (-0.75, 0.75):
            X['court'].append(qb(S['station'], '5A5C60', x + d - 0.06, x + d + 0.06, -125, -31, 0.02, 0.14, rough=0.3))
    for i in range(8):
        y = -44 - 10 * i
        for sx in (-17, 17):
            X['court'].append(qbar(S['station'], '2E3236', (sx, y, 0), (sx, y, 4.6), 0.12))
            X['court'].append(qb(S['station'], 'FFE2A0', sx - 0.25, sx + 0.25, y - 0.25, y + 0.25, 4.6, 5.1, emit=2.0))
    # the fuselage: the holes in the pack, so that it can hang whole before the flak
    S['pkholes'] = [c for c in S['pack'].children if c.name.lower().startswith('cylinder')]
    # the sky: the outer right wing as its own piece, and the piece that breaks away
    S['rwing'] = min((c for c in S['bomber'].children if c.type == 'MESH'), key=lambda c: c.location.x)
    wb = keep(qe(None, FAR))
    qb(wb, OD, -4.5, 4.5, -1.8, 1.8, -0.16, 0.16)
    qb(wb, '2A2C2E', 4.3, 4.6, -1.6, 1.6, -0.2, 0.2)
    S['wingbit'] = wb
    S['coin'] = keep(qc(None, 'FFC233', FAR, 0.09, 0.02, 10, rough=0.2, emit=1.5))
    pk = keep(qe(None, FAR))                                                         # a whole parachute pack, on the grass
    qb(pk, '6E6A48', -0.4, 0.4, -0.5, 0.5, 0, 0.3, rough=1.0)
    qb(pk, '4E4A34', -0.3, 0.3, -0.4, 0.4, 0.3, 0.33, rough=1.0)
    for sx in (-0.2, 0.2):
        qb(pk, '8A7A4A', sx - 0.05, sx + 0.05, -0.6, 0.6, 0.02, 0.36, rough=1.0)
    qb(pk, 'B0B4B8', -0.08, 0.08, -0.56, -0.5, 0.12, 0.22, rough=0.3)
    S['pack2'] = pk
    make_cub(S)
    # two more people: the gunner fifty years on, and his wife
    S['old'] = o = K.Rig(dict(top='8A6A48', pants='5A5A52', hand='E0B490', boot='3A2A20', fore='8A6A48'), K.human_head('E0B490', 'C8C8C4'))
    add('cube', 'E8E4D8', (0, -0.2, 0.98), scale=(0.44, 0.14, 0.1), size=1, parent=o.body, rough=1.0)
    S['wife'] = w = K.Rig(dict(top='7A4A5A', pants='4A4048', hand='E4BC9C', boot='2A2228', fore='7A4A5A'), K.human_head('E4BC9C', 'D8D4CC'))
    add('cone', '7A4A5A', (0, 0, -0.32), radius1=0.5, radius2=0.31, depth=0.8, vertices=8, parent=w.body)
    add('ico_sphere', 'D8D4CC', (0, 0.3, 0.05), radius=0.17, subdivisions=1, parent=w.head)
    add('cube', 'C8B8D0', (0, -0.2, 0.98), scale=(0.5, 0.16, 0.12), size=1, parent=w.body, rough=1.0)
    S['humans'] += [o, w]
    S['cast_all'] += [o, w]


_build0, _reset0 = build, reset


def build():
    _MESH.clear()
    S = _build0()
    S['sets'] = {}
    for name, (o, fn) in MAKERS.items():
        root = qe(None, o)
        d = fn(root, S)
        d.update(root=root, all=list(root.children_recursive))
        S['sets'][name] = d
    make_extras(S)
    for i, o in enumerate(S['land'].children):               # the Short's field patches overlap at one height: black where they cross
        if abs(o.location.z - 1.0) < 1e-6:
            o.location.z = 1.0 + 0.5 * i
    bpy.context.view_layer.update()
    reset(S)
    return S


def reset(S):
    _reset0(S)
    if 'sets' not in S:
        return
    for d in S['sets'].values():
        for o in d['all']:
            o.hide_render = True
        for l in d['lights']:
            l.data.energy = 0
    for grp in S['x'].values():
        for o in grp:
            o.hide_render = True
    for o in S['fronts'] + S['rags'] + S['pkholes'] + [S['rwing'], S['blanket'], S['cubblade']]:
        o.hide_render = False
    S['cubdisc'].hide_render = True
    S['winl'].data.color = K.hexc('DDE8F4')[:3]
    S['pack'].parent = S['fuse']
    S['pack'].location, S['pack'].rotation_euler = (2.15, -1.8, 1.65), (0, 0, 0)
    S['blanket'].location, S['blanket'].scale = (0, 0.4, 1.38), (2.15, 2.9, 0.22)
    for lf in S['gleaf']:
        lf.rotation_euler = (0, 0, 0)


def use(S, name):
    d = S['sets'][name]
    for o in d['all']:
        o.hide_render = False
    return d


def xshow(S, *names):
    for n in names:
        for o in S['x'][n]:
            o.hide_render = False


def coin(S, hand, lt, rate=3.2, hgt=0.8):
    u = (lt * rate) % 2
    S['coin'].location = plus(hand, (0.0, -0.1, 0.25 + hgt * max(0.0, 1 - (u - 1) ** 2) if u < 2 else 0.25))
    S['coin'].rotation_euler = (lt * 14, 0.4, 0)


# ---------------------------------------------------------------- how it began
def field_dawn(S, k, t, lt):
    """An airfield in England at dawn: the bomber parked on its hardstand, mist on the grass; the gunner walks out to it.
    Rook sits on a fuel drum in the foreground, flipping a coin, and turns to watch him go."""
    use(S, 'base')
    sky(S, 'dawn')
    for i, (x, y, yw) in enumerate(((-82, -30, 0.5), (-160, 6, 0.3))):
        S['others'][i].location = at(BASE, x, y, 3.3)
        S['others'][i].rotation_euler = (-0.13, 0, yw)
    m = S['man']
    p0, p1 = (17.5, -25.0), (10.5, -16.5)
    p = (lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k))
    stand(m, at(BASE, p[0], p[1], 0), facing(p0, p1), K.walk(t, 1.3), 'calm')
    rk = S['rook']
    turn = sm((k - 0.35) / 0.3)
    rk.place(at(BASE, 7.4, -30.3, 1.72 - 0.55), facing((7.4, -30.3), (17.0, -36.0)) - 0.25)
    rk.apply(P('sit', lL=(1.3, 1.8), lR=(1.2, 1.7), aR=(0.9, 0.1, 1.5), aL=(0.4, 0.3, 1.2), head=(0.05, -0.9 * turn)))
    S['hat_tip'] = 0.5 * (1 - turn)
    coin(S, wpos(rk.hands[1]), lt)
    cam(S, at(BASE, lerp(17.5, 15.5, k), lerp(-37.0, -34.0, k), 2.1), at(BASE, 2.0, -6.0, 3.9), 28)


def turret_under(S, k, t, lt):
    """Under the belly of the parked bomber: the ball turret hangs just above the grass. The gunner kneels by it and slaps
    its side; Rook, outside the fuselage, bends to look at how small it is."""
    use(S, 'base')
    sky(S, 'dawn')
    m = S['man']
    pat = 0.5 + 0.5 * math.sin(lt * 5.0)
    kneel(m, at(BASE, 0.25, 0.75, 0), facing((0.25, 0.75), (0.0, 2.6)), 0.3 + 0.7 * pat * bump(k, 0.15, 0.7))
    m.face = 'calm' if k < 0.6 else 'warm'
    rk = S['rook']
    lean = sm(k / 0.4)
    stand(rk, at(BASE, 1.9, 5.3, 0), facing((1.9, 5.3), (0.2, 2.6)), blend(P('stand', head=(0.1, 0.0)), P('hips', lean=0.4, head=(0.3, 0.25 * math.sin(lt * 1.5))), lean))
    S['rface'] = 'low'
    S['hat_tip'] = 0.4
    cam(S, at(BASE, 7.2, lerp(1.4, 2.4, k), 1.45), at(BASE, 0.0, 2.7, 1.9), 30)


def rook_measure(S, k, t, lt):
    """Rook's test: he holds his wings apart across the ball turret, keeps them that far apart, turns to a parachute pack
    on the grass and shows that the two will not go in together. He shrugs."""
    use(S, 'base')
    sky(S, 'dawn')
    rk = S['rook']
    a = bump(k, 0.05, 0.42)
    b_ = sm((k - 0.45) / 0.2)
    sh = sm((k - 0.78) / 0.15)
    meas = P('stand', aL=(1.5, 0.75, 0.2), aR=(1.5, 0.75, 0.2), head=(0.2, lerp(0.5, -0.6, b_)))
    pose = blend(P('stand', head=(0.1, 0.5)), meas, max(a, b_ * (1 - sh)))
    pose = blend(pose, P('shrug', head=(-0.05, -0.2)), sh)
    stand(rk, at(BASE, 2.3, 3.2, 0), facing((2.3, 3.2), (0.0, 2.6)) + lerp(0.0, 1.3, b_), pose)
    S['rface'] = 'low' if sh > 0.5 else 'calm'
    S['hat_tip'] = 0.5 * sh
    S['pack2'].location = at(BASE, 3.3, 1.2, 0.02)
    S['pack2'].rotation_euler = (0, 0, 0.5)
    h = head(rk)
    cam(S, at(BASE, 6.4, lerp(-0.6, 0.2, k), 1.9), plus(h, (-0.9, -0.3, -0.7)), 30)


def turret_side(S, k, t, lt):
    """Inside the ball, from beside him: curled between the two guns with his knees up, the round window and the sky in
    front of him, flak bursting out there. No room for anything else."""
    sky(S, 'high')
    S['tlamp'].data.energy = 90
    flak(S, at(TUR, -8, -46, -6), t, (50, 14, 26), n=8, size=3.2)
    S['flamp'][0].location = at(TUR, -1.0, -5.0, 0.6)
    S['flamp'][0].data.energy = 260 * max(0.0, math.sin(t * 7.0)) ** 6
    m = in_turret(S, 0.25 * max(0.0, math.sin(t * 7.0)) ** 6, 0.5 * math.sin(lt * 1.6))
    m.face = 'hard'
    cam(S, at(TUR, lerp(1.2, 1.05, k), lerp(-1.0, -1.15, k), 0.55), at(TUR, 0.0, -0.3, 0.15), 22)


def pack_hook(S, k, t, lt):
    """Before the raid, inside the fuselage: his parachute pack, whole, hangs on its hook on the wall. He reaches up, pats
    it, and turns away towards the hatch in the floor."""
    sky(S, 'inside')
    S['flight'].data.energy = 240
    for o in S['rags'] + S['pkholes']:
        o.hide_render = True
    m = S['man']
    up = bump(k, 0.0, 0.5, 0.2)
    turn = sm((k - 0.55) / 0.3)
    yw = facing((1.0, -0.5), (2.2, -1.7))
    stand(m, at(FUS, 1.0 - 0.5 * turn, -0.5 + 0.9 * turn, 0), yw + 2.0 * turn,
          blend(P('stand', head=(-0.1, 0.0)), P('stand', aL=(1.9, 0.1, 0.5), aR=(0.3, 0.2, 0.4), head=(-0.25, 0.0)), up), 'calm')
    shoot(S, FUS, (lerp(-1.5, -1.1, k), -4.4, 2.0), (1.7, -1.3, 1.75), 28)


# ---------------------------------------------------------------- the raid
def nose_fly(S, k, t, lt):
    """The bomber in the air, close on its nose and cockpit from ahead and to one side, the rest of the formation strung
    out behind it over the cloud. No name and no picture is painted on it."""
    sky(S, 'high')
    b = S['bomber']
    b.location = at(SKYO, 0, 0, 0.5 * math.sin(t * 1.1))
    b.rotation_euler = (0.02 * math.sin(t), 0.04 * math.sin(t * 0.7), 0)
    for i, o in enumerate(S['others']):
        p = FORM[i + 1]
        o.location = at(SKYO, p[0] * 0.8, p[1] * 1.2 + 14, p[2] + 0.8 * math.sin(t * 0.9 + i))
        o.rotation_euler = (0, 0.03 * math.sin(t + i), 0)
    clouds(S, SKYO, t, depth=-50, spread=320, vy=-34)
    shoot(S, SKYO, (lerp(12.5, 9.5, k), lerp(-29.0, -25.0, k), lerp(3.6, 2.6, k)), (0.0, -8.0, 0.4), 30)


def pens(S, k, t, lt):
    """From above the formation: the harbour of Saint-Nazaire below, the long concrete block of the U-boat pens on the
    basin with its row of dark mouths, the town round it, and flak coming up."""
    use(S, 'port')
    sky(S, 'port')
    y = lerp(330, 230, k)
    b = S['bomber']
    b.location = at(PORT, -300, y, 300 + 1.5 * math.sin(t))
    b.rotation_euler = (0, 0.03 * math.sin(t * 0.8), 0)
    for i, o in enumerate(S['others']):
        p = FORM[i + 1]
        o.location = at(PORT, -300 + p[0] * 1.3, y + p[1] * 1.3, 300 + p[2])
        o.rotation_euler = (0, 0, 0)
    flak(S, at(PORT, -300, y - 60, 292), t, (220, 200, 50), n=16, size=5.0, period=1.2)
    cam(S, at(PORT, -236, y + 104, 372), at(PORT, -335, y - 190, 0), 30)


def wing_hit(S, k, t, lt):
    """The second hit: a burst on the right wing, and the outer part of it breaks away and tumbles back. Fire runs along
    what is left and the bomber starts to drop that side."""
    sky(S, 'high')
    b = S['bomber']
    u = k - 0.22
    v = max(0.0, u)
    b.location = at(SKYO, 0, 0, -3.0 * v * v)
    b.rotation_euler = (-0.12 * v, -0.75 * sm(v / 0.78), 0.3 * v)
    clouds(S, SKYO, t, depth=-60, spread=260, vy=-30)
    flak(S, at(SKYO, 10, 20, -8), t, (70, 60, 24), n=8, i0=6, size=3.0)
    tip = wpos(b, (-18.0, -2.2, 0.35))
    stub = wpos(b, (-14.5, -1.6, 0.3))
    if u > 0:
        S['rwing'].hide_render = True
        f, o = S['flash'][0], S['puffs'][0]
        if u < 0.1:
            fs = 3.4 * (0.6 + 5 * u)
            f.location, f.scale = tip, (fs, fs, fs)
            S['flamp'][0].location, S['flamp'][0].data.energy = tip, 60000 * (1 - u / 0.1)
        s = 1.2 + 3.0 * sm(u * 2.5)
        o.location, o.scale = plus(tip, (-1.0 * u, 10 * u, 2 * u)), (s, s, s)
        wb = S['wingbit']
        wb.location = plus(tip, (-5.0 * u, 24 * u, 4.0 * u - 14 * u * u))
        wb.rotation_euler = (5 * u, 7 * u, 2 * u)
        fire(S, [plus(stub, (0.5 * j, 0.9 * j, 0.25 * j)) for j in range(4)], t, 1.2, (0.2, 1, 0.45))
        S['flamp'][1].location, S['flamp'][1].data.energy = stub, 14000
        smoke_trail(S, stub, (0.1, 1.0, 0.4), t, n=10, gap=2.0, size=0.7)
        debris(S, tip, u * 1.6, n=10, r=7.0, h=1.5, g=5.0, dirx=-1.0)
    shoot(S, SKYO, (-33.0, lerp(25.0, 21.0, k), lerp(15.0, 12.0, k)), (-11.0, -2.0, -1.0 - 2.0 * v), 30, roll=-0.1 * v)


def spin_down(S, k, t, lt):
    """Wide, from the side: the bomber going down in a flat spin with part of one wing gone, fire on the stub, its smoke
    winding up behind it in a corkscrew."""
    sky(S, 'high')
    b = S['bomber']
    S['rwing'].hide_render = True
    S['hole_w'].hide_render = False
    b.location = at(SKYO, 0, 0, -26 * k)
    b.rotation_euler = (-0.55, -0.45, 2.6 * lt + 0.6)
    clouds(S, at(SKYO, 0, 0, -26 * k), t, vz=16, depth=-70, spread=240)
    stub = wpos(b, (-14.5, -1.6, 0.3))
    fire(S, [plus(stub, (0, 0, 0.8 * j)) for j in range(4)], t, 1.4, (0, 0.1, 1))
    S['flamp'][1].location, S['flamp'][1].data.energy = stub, 16000
    for j in range(14):                                                    # the corkscrew of smoke it leaves above itself
        a = 2.6 * (lt - 0.11 * j) + 0.6
        o = S['smoke'][j]
        o.location = at(SKYO, -14.5 * math.cos(a) * 0.9, -14.5 * math.sin(a) * 0.9, -26 * k + 2.2 * j + 1.0)
        s = 1.2 + 0.32 * j
        o.scale = (s, s, s)
    shoot(S, SKYO, (44.0, -38.0, 12.0 - 22 * k), (0.0, 0.0, -26 * k + 3.0), 30, roll=0.12 * math.sin(lt * 1.2))


def fuse_spin(S, k, t, lt):
    """Inside the spinning fuselage: the floor tilts, fire flickers at the far end, smoke runs along the roof. The gunner
    is on his hands and knees, dragging himself forward, his eyes going heavy."""
    sky(S, 'inside')
    S['flight'].data.energy = lerp(170, 90, k)
    S['flamp'][1].location = at(FUS, -1.6, 5.5, 2.2)
    S['flamp'][1].data.energy = 2600 * (0.7 + 0.3 * math.sin(t * 19) + 0.2 * math.sin(t * 31))
    fire(S, [at(FUS, -2.0 + 0.5 * j, 7.6, 0.6 + 0.5 * j) for j in range(4)], t, 0.9, (0, -0.3, 1))
    m = S['man']
    y = lerp(1.2, -1.6, k)
    w = math.sin(lt * 6.0)
    m.place(at(FUS, 0.2 + 0.25 * math.sin(lt * 2.3), y, 0.2), 0.12 * w, 1.18, 0.1 * w)
    m.apply(P('stand', aL=(2.3 + 0.4 * w, 0.3, 0.9), aR=(2.3 - 0.4 * w, 0.3, 0.9), lL=(0.9 + 0.4 * w, 1.6), lR=(0.9 - 0.4 * w, 1.6), head=(-1.0, 0.0)))
    m.face = 'hard' if k < 0.5 else 'tired'
    m.jawv = 0.3
    for i, o in enumerate(S['fsmoke']):
        v = (t * 0.5 + i / 6) % 1
        o.location = at(FUS, -1.2 + 2.4 * rnd(i, 48), 5.0 - 9.0 * v, 2.9 + 0.3 * math.sin(v * 7))
        o.scale = (1.5 + v, 1.5 + v, 1.0 + v)
    shoot(S, FUS, (0.5, lerp(-6.4, -5.6, k), 1.0), (0.1, y - 2.2, 1.0), 26, roll=0.35 * math.sin(lt * 1.9) + 0.45 * k)


def fall_close(S, k, t, lt):
    """Close on him from above as he falls on his back, out cold: eyes shut, arms drifting up, the mask blown loose, the
    cloud far below him coming up."""
    sky(S, 'high')
    clouds(S, FALLZ, t, vz=30, depth=-46, spread=150)
    m = S['man']
    put(m, at(FALLZ, 0, 0, 0), 0.25 * math.sin(lt * 0.9), -PI / 2 + 0.12 * math.sin(lt * 1.3), 0.15 * math.sin(lt * 1.1), limp(t))
    m.face = 'shut'
    h = head(m)
    cam(S, plus(h, (0.8, -1.4, lerp(3.3, 2.7, k))), plus(h, (0.0, -0.7, 0.0)), 36, roll=0.25 * lt)


# ---------------------------------------------------------------- the station
def station_out(S, k, t, lt):
    """Outside the station, from the tracks: the open end of the long hall with its arched roof of glass and iron, steam
    from a locomotive inside, lamps along the approach. High above it, very small, a figure is falling."""
    sky(S, 'low')
    S['hlamp'].data.energy = 2500
    xshow(S, 'court')
    for o in S['fronts']:
        o.hide_render = True
    for i, o in enumerate(S['steam']):
        u = (t * 0.22 + i / 8) % 1
        o.location = at(STA, 9.0 + 1.5 * math.sin(i * 2.1) + 2 * u, 5.0 - 4.0 * u, 5.5 + 7.0 * u)
        s = 0.9 + 2.6 * u
        o.scale = (s, s, s * 0.8)
    m = S['man']
    m.root.scale = (2.2, 2.2, 2.2)
    m.place(at(STA, -1.0, -6.0, lerp(46, 36, k)), 0.5 * t, -1.6, 0.4 * math.sin(t))
    m.apply(limp(t))
    cam(S, at(STA, lerp(-8.0, -6.5, k), lerp(-53.0, -47.0, k), 2.2), at(STA, 0.0, -24.0, lerp(12.0, 10.5, k)), 26)


def girders(S, k, t, lt):
    """From the platform, up at the hole: Rook crouches on the roof at its edge and weighs the two accounts, pointing down
    at the floor, then along at the steel ribs beside him, then turning up one wing: which?"""
    sky(S, 'hall')
    S['hlamp'].data.energy = 3000
    broken(S)
    S['shaft'].hide_render = True
    glass_fall(S, at(STA, *HOLE), STA[2] + 0.4, 0.6 + 0.35 * k, n=8, r=2.0, seed=7)
    dust(S, at(STA, 0, 0.5, 4.0), t, 2.5, 8.0)
    rk = S['rook']
    a = bump(k, 0.05, 0.4)
    b_ = bump(k, 0.45, 0.75)
    c_ = sm((k - 0.8) / 0.15)
    pose = P('stand', lL=(1.4, 2.2), lR=(0.3, 1.9), lift=-0.75, lean=0.55, aL=(0.4, 0.3, 0.8), aR=(0.5, 0.2, 0.9), head=(0.5, 0.0))
    pose = blend(pose, dict(pose, aR=_arm4((1.0, 0.0, 0.1)), head=(0.75, 0.0)), a)
    pose = blend(pose, dict(pose, aR=_arm4((1.3, 1.25, 0.1)), head=(0.3, -0.7)), b_)
    pose = blend(pose, dict(pose, aR=_arm4((0.6, 0.8, 1.6, -0.9)), aL=_arm4((0.6, 0.8, 1.6, -0.9)), head=(0.45, 0.0)), c_)
    stand(rk, at(STA, 4.3, 0.4, 12.5), facing((4.3, 0.4), (0.0, -0.4)), pose)
    S['rface'] = 'calm' if c_ < 0.5 else 'low'
    cam(S, at(STA, lerp(-0.6, 0.0, k), -2.6, 8.6), at(STA, 3.3, 0.2, 12.9), 30)


def _arm4(v):
    return tuple(v) + (0.0,) * (4 - len(v))


# ---------------------------------------------------------------- the hospital
def ward(S, night=False, leg=True):
    if night:
        sky(S, 'ward')
        S['bulb'].data.energy = 150
        S['winl'].data.energy = 90
        S['winl'].data.color = K.hexc('8AA4E0')[:3]
    else:
        room_lights(S)
        S['winl'].data.color = K.hexc('DDE8F4')[:3]
    xshow(S, 'hosp')
    if leg:
        xshow(S, 'leg')
    S['blanket'].location, S['blanket'].scale = (0, 0.4, 1.5), (2.15, 2.9, 0.52)      # deep enough to cover his boots


def bed_leg(S, k, t, lt):
    """Night in the hospital room, from above the foot of the bed: he lies still under the lamp, one leg in plaster slung
    from a frame, his arm bound across his chest, a chart hooked on the bed rail."""
    ward(S, night=True)
    in_bed(S, 'shut')
    cam(S, at(HOS, lerp(1.9, 1.3, k), lerp(-4.6, -4.0, k), lerp(4.6, 4.2, k)), at(HOS, -0.1, 1.3, 1.6), 28)


def arm_close(S, k, t, lt):
    """Close on him asleep: the bound right arm lying across the blanket, his face turned to the lamp, breathing."""
    ward(S, night=True)
    S['bulb'].data.energy = 220
    m = in_bed(S, 'shut')
    m.jawv = 0.1 + 0.08 * math.sin(lt * 1.9)
    cam(S, at(HOS, lerp(2.1, 1.7, k), lerp(1.5, 1.9, k), 3.7), at(HOS, 0.1, 2.5, 1.55), 36)


def doc_talk(S, k, t, lt):
    """The doctor at the bedside, talking: a hand on his own chest, then a finger towards the bound arm. The gunner has
    turned his head on the pillow to listen. Nothing he says is put on screen."""
    ward(S)
    m = in_bed(S, 'tired')
    m.apply(P('stand', aL=(0.15, 0.25, 0.3), aR=(0.9, 0.2, 1.5, 0.8), head=(0.0, 0.55)))
    d = S['doc']
    g1 = bump(k, 0.12, 0.45)
    g2 = sm((k - 0.55) / 0.2)
    stand(d, at(HOS, -1.8, 1.5, 0), facing((-1.8, 1.5), (0.0, 2.4)),
          P('stand', aR=(0.8 * g1 + 1.0 * g2, 0.05 - 0.25 * g1, 1.9 * g1 + 0.25 * g2, 0.6 * g1), aL=(0.3, 0.1, 0.5), lean=0.22 + 0.1 * g2, head=(0.25, 0.0)), 'calm')
    d.jawv = (0.25 + 0.3 * abs(math.sin(lt * 8.5))) * (1 if k < 0.9 else 0.2)
    cam(S, at(HOS, 1.9, lerp(0.7, 1.1, k), 3.4), at(HOS, -1.0, 2.1, 2.3), 34)


def arm_wrap(S, k, t, lt):
    """The doctor bends over the arm and winds a bandage round it, turn after turn. Rook, on the near side of the bed,
    leans in to watch the hands, and his brim comes up."""
    ward(S)
    m = in_bed(S, 'tired')
    d = S['doc']
    w = lt * 4.2
    stand(d, at(HOS, -1.45, 2.1, 0), facing((-1.45, 2.1), (0.1, 2.2)),
          P('stand', aL=(1.05, -0.15, 0.75), aR=(1.1 + 0.12 * math.sin(w), -0.1 + 0.1 * math.cos(w), 0.75), lean=0.62, head=(0.5, 0.0)), 'calm')
    hr = wpos(d.hands[1])
    S['roll'].location = plus(hr, (0.12, 0.0, -0.08 + 0.1 * math.sin(w)))
    S['roll'].rotation_euler = (w, PI / 2, 0)
    rk = S['rook']
    lean = sm(k / 0.4)
    stand(rk, at(HOS, 1.75, 1.2, 0), facing((1.75, 1.2), (0.0, 2.2)), blend(P('stand', head=(0.15, 0.0)), P('think', lean=0.3, head=(0.3, 0.0)), lean))
    S['hat_tip'] = lerp(0.6, -0.2, sm((k - 0.4) / 0.4))
    S['rface'] = 'soft' if k > 0.5 else 'calm'
    cam(S, at(HOS, lerp(0.7, 1.1, k), lerp(-2.4, -1.9, k), 3.3), at(HOS, -0.1, 2.0, 1.9), 34)


def bed_sit(S, k, t, lt):
    """Weeks on, daylight: he sits up against the pillow and lifts the mended arm, opening and closing the hand. Beside
    the bed Rook copies him with one wing, then nods."""
    ward(S, leg=False)
    S['winl'].data.energy = 1100
    S['bulb'].data.energy = 120
    m = S['man']
    f = sm((k - 0.12) / 0.3)
    m.place(at(HOS, 0.0, 2.45, 0.78), 0.0)
    m.apply(P('sit', lL=(1.5, 0.1), lR=(1.5, 0.1), lean=-0.12, aL=(0.4, 0.2, 0.7), aR=(0.5 + 0.9 * f, 0.35, 1.0 + 0.5 * f + 0.35 * math.sin(lt * 4.5) * f), head=(0.1, 0.25 * f)))
    S['cast'].hide_render = False
    m.face = 'calm' if k < 0.45 else 'warm'
    rk = S['rook']
    g = sm((k - 0.45) / 0.25)
    nod = max(0.0, math.sin((k - 0.8) / 0.2 * PI)) if k > 0.8 else 0.0
    stand(rk, at(HOS, 2.1, 2.3, 0), facing((2.1, 2.3), (0.0, 2.4)) + 0.5,
          blend(P('stand', head=(0.1, 0.0)), P('stand', aL=(1.4, 0.35, 1.0 + 0.4 * math.sin(lt * 4.5)), head=(0.05 + 0.35 * nod, 0.3)), g))
    S['rface'] = 'soft'
    S['hat_tip'] = -0.2
    cam(S, at(HOS, lerp(1.6, 1.2, k), lerp(-3.2, -2.6, k), 3.0), at(HOS, 0.9, 2.3, 2.5), 30)


# ---------------------------------------------------------------- the camp
def snowfall(S, t, cx=0.0):
    for i, o in enumerate(S['flakes']):
        z = 6 - ((t * 1.6 * (0.7 + 0.6 * rnd(i, 120)) + rnd(i, 121) * 6) % 6)
        o.location = at(CMP, cx - 6 + 13 * rnd(i, 122) + 0.3 * math.sin(t + i), 0.5 + 6 * rnd(i, 123), z)


def camp_three(S, k, t, lt):
    """Snow and wire: the three survivors of the crew stand together inside the fence, the gunner in the middle with his
    arm in a sling, the long hut behind them. Nobody speaks."""
    sky(S, 'snow')
    m = S['man']
    stand(m, at(CMP, 0.6, -1.3, 0), PI, P('stand', aR=(0.9, 0.2, 1.5, 0.8), aL=(0.1, 0.15, 0.2), head=(0.05, 0.3 * math.sin(lt * 0.8))), 'sad')
    S['cast'].hide_render = S['sling'].hide_render = False
    a, b_ = S['men']
    stand(a, at(CMP, -1.6, -1.7 + 0.02 * math.sin(lt * 9), 0), PI + 0.25, P('cross', head=(0.2, -0.2)), 'tired')
    stand(b_, at(CMP, 2.7, -1.9, 0), PI - 0.3, P('stand', aL=(0.3, 0.1, 1.2, 0.8), aR=(0.3, 0.1, 1.2, 0.8), head=(0.1, 0.35 * sm((k - 0.4) / 0.3))), 'sad')
    snowfall(S, t)
    cam(S, at(CMP, lerp(7.5, 3.0, k), lerp(5.0, 6.6, k), lerp(1.7, 2.3, k)), at(CMP, 0.5, -1.4, 2.35), 30)


def gate_open(S, k, t, lt):
    """Spring: the snow is gone and the gate in the wire swings open. The gunner walks out through it, both arms his own,
    the other two behind him. Rook sits on the gatepost with his coin and lifts his hat as they pass."""
    sky(S, 'spring')
    xshow(S, 'gate')
    u = sm(k / 0.4)
    S['gleaf'][0].rotation_euler = (0, 0, -1.35 * u)
    S['gleaf'][1].rotation_euler = (0, 0, 1.35 * u)
    v = sm((k - 0.15) / 0.85)
    m = S['man']
    stand(m, at(CMP, GX + 0.1, lerp(-5.0, 3.2, v), 0), PI, K.walk(t, 1.3), 'warm')
    for j, rig in enumerate(S['men']):
        stand(rig, at(CMP, GX + (-1.2, 1.3)[j], lerp(-8.5 - j, -0.6 - j, v), 0), PI, K.walk(t + 0.4 * j, 1.3), 'calm')
    rk = S['rook']
    lift = sm((k - 0.55) / 0.2)
    rk.place(at(CMP, GX - 2.7, 0.0, 4.5 - 0.55), PI + 0.5)
    rk.apply(blend(P('sit', lL=(1.3, 1.8), lR=(1.2, 1.7), aR=(0.9, 0.1, 1.5), aL=(0.4, 0.3, 1.2), head=(0.2, 0.5)),
                   P('sit', lL=(1.3, 1.8), lR=(1.2, 1.7), aR=(0.2, 1.9, 1.6, -1.5), aL=(0.4, 0.3, 1.2), head=(0.25, 0.3)), lift))
    S['hat_jump'] = 0.22 * lift
    S['rface'] = 'soft'
    if lift < 0.3:
        coin(S, wpos(rk.hands[1]), lt)
    cam(S, at(CMP, GX + lerp(3.6, 2.8, k), lerp(8.6, 7.2, k), 2.0), at(CMP, GX - 0.7, -0.5, 2.9), 28)


# ---------------------------------------------------------------- home
def medals(S, k, t, lt):
    """An open case on a table under a lamp: a heart-shaped medal on a purple ribbon and a round bronze one on a blue
    ribbon. Rook's wing creeps towards the shine, stops, and goes behind his back."""
    use(S, 'desk')
    sky(S, 'den')
    S['sets']['desk']['lights'][0].data.energy = 520
    rk = S['rook']
    reach = bump(k, 0.12, 0.5)
    back = sm((k - 0.55) / 0.2)
    pose = blend(P('stand', lean=0.2, head=(0.35, 0.3)), P('stand', lean=0.42, aL=(1.25, 0.2, 0.5), head=(0.5, 0.35)), reach)
    pose = blend(pose, P('stand', aL=(-0.5, 0.25, 0.9), aR=(-0.5, 0.25, 0.9), head=(0.05, 0.0)), back)
    stand(rk, at(DESK, 1.15, 1.75, 0), 0.25, pose)
    S['rface'] = 'shocked' if reach > 0.5 else ('low' if back > 0.5 else 'calm')
    S['hat_tip'] = 0.55 * back
    S['flamp'][0].location = at(DESK, -0.5, -0.9, 2.5)
    S['flamp'][0].data.energy = 40 + 60 * max(0.0, math.sin(lt * 3.0)) ** 4
    cam(S, at(DESK, lerp(-1.3, -0.5, k), -3.9, lerp(3.2, 3.0, k)), at(DESK, 0.15, 0.5, 2.0), 40)


def hangar_walk(S, k, t, lt):
    """A grass airfield at home, late sun: a small yellow aeroplane outside its hangar. An older man walks up to it and
    lays his hand on the wing strut. Rook sits out on the wing, legs swinging."""
    use(S, 'home')
    sky(S, 'gold')
    c = S['cub']
    c.location, c.rotation_euler = at(HOME, 0, 0, 0.0), (-0.125, 0, 0.55)
    o = S['old']
    p0, p1 = (8.6, -7.4), (3.9, -3.3)
    u = sm(k / 0.62)
    p = (lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u))
    touch = sm((k - 0.62) / 0.2)
    stand(o, at(HOME, p[0], p[1], 0), facing(p0, (1.5, -1.0)), blend(K.walk(t, 1.2), P('stand', aL=(1.7, 0.1, 0.4), head=(-0.3, 0.0)), touch), 'warm' if touch > 0.5 else 'calm')
    rk = S['rook']
    seat = wpos(c, (4.7, -1.1, 2.93))
    sw = math.sin(lt * 3.0)
    rk.place(plus(seat, (0, 0, -0.55)), 0.55 - 0.3)
    rk.apply(P('sit', lL=(1.2 + 0.25 * sw, 1.6), lR=(1.2 - 0.25 * sw, 1.6), aL=(0.3, 0.4, 0.6), aR=(0.3, 0.4, 0.6), head=(0.3, 0.5 * sm((k - 0.3) / 0.3)), lean=0.1))
    S['rface'] = 'soft'
    cam(S, at(HOME, lerp(9.6, 8.2, k), lerp(-9.4, -8.0, k), 1.8), at(HOME, 2.2, -1.4, 2.5), 28)


def cub_fly(S, k, t, lt):
    """The same yellow aeroplane in the air, banking over a quilt of fields in low sun, the older man at the controls,
    looking out and down."""
    use(S, 'home')
    sky(S, 'gold')
    c = S['cub']
    S['cubblade'].hide_render = True
    S['cubdisc'].hide_render = False
    y = 60 - 26 * lt
    bank = 0.32 + 0.06 * math.sin(lt * 1.3)
    c.location, c.rotation_euler = at(HOME, -30 + 4.0 * lt, y, 118 + 1.2 * math.sin(lt * 1.7)), (0.03 * math.sin(lt * 2.1), bank, -0.18 - 0.05 * lt)
    o = S['old']
    o.root.parent = c
    o.place((0.0, -0.75, 0.52), 0.0)
    o.apply(P('sit', lL=(1.4, 1.0), lR=(1.4, 1.0), aL=(0.9, 0.0, 0.9), aR=(0.9, 0.0, 0.9), lean=0.05, head=(0.1, -0.5 * sm((k - 0.3) / 0.3))))
    o.face = 'warm'
    cl = tuple(c.location)
    cam(S, plus(cl, (lerp(8.5, 6.5, k), -10.5, lerp(2.2, 3.4, k))), plus(cl, (0.0, -0.6, 1.9)), 34, roll=-0.06)


# ---------------------------------------------------------------- the memorial, and the verdict
def mem_visit(S, k, t, lt):
    """The square, past the edge of the stone: the older man and his wife stand in front of the memorial. He looks up at
    it for a long moment; she takes his arm. Rook stands a little apart, hat in his hand, head down."""
    sky(S, 'square')
    o, w = S['old'], S['wife']
    look = sm((k - 0.5) / 0.3)
    stand(o, at(MEM, 0.4, -4.0, 0), PI - 0.1, P('stand', aL=(0.1, 0.15, 0.3), aR=(0.15, 0.15, 0.4), head=(-0.3 + 0.2 * look, 0.0)), 'sad')
    stand(w, at(MEM, 1.35, -4.15, 0), PI - 0.25, P('stand', aL=(0.5 * look, -0.15, 1.3 * look, 0.9 * look), aR=(0.1, 0.15, 0.3), head=(-0.15 + 0.15 * look, 0.45 * look)), 'warm' if look > 0.5 else 'sad')
    for j, (rig, p) in enumerate(zip(S['men'], ((-0.8, -8.6), (2.6, -9.2)))):
        stand(rig, at(MEM, p[0], p[1], 0), facing(p, (0, 0)), P('stand', aL=(0.3, -0.1, 1.2, 0.9), aR=(0.3, -0.1, 1.2, 0.9), head=(0.15, 0.0)), 'sad')
    rk = S['rook']
    stand(rk, at(MEM, 4.0, -3.1, 0), facing((4.0, -3.1), (0, 0)) + 0.3, P('stand', aR=(0.9, -0.25, 1.9, 0.6), head=(0.45, 0.2)))
    S['hat_off'], S['hat_to'] = 1.0, (0.15, -0.55, -1.0)
    S['rface'] = 'sad'
    cam(S, at(MEM, lerp(3.7, 3.0, k), lerp(2.2, 1.8, k), 3.7), at(MEM, 1.0, -3.9, 2.6), 30)


def rook_verdict(S, k, t, lt):
    """Dusk on the station roof, beside the hole: Rook looks down through it, then at us, pushes his brim up with one
    wingtip so that his eyes show, and nods. He was wrong."""
    sky(S, 'dusk')
    S['hlamp'].data.energy = 500
    broken(S)
    S['shaft'].hide_render = True
    rk = S['rook']
    a = sm((k - 0.3) / 0.2)
    b_ = sm((k - 0.5) / 0.2)
    nod = max(0.0, math.sin((k - 0.78) / 0.22 * PI)) if k > 0.78 else 0.0
    pose = blend(P('hips', head=(0.6, 0.0)), P('stand', head=(0.0, 0.0)), a)
    pose = blend(pose, P('hat', head=(-0.05 + 0.4 * nod, 0.0)), b_)
    stand(rk, at(STA, 0.3, 3.6, 12.95), 0.25, pose)
    S['hat_tip'] = lerp(0.8, -0.35, b_)
    S['rface'] = 'low' if b_ < 0.5 else 'soft'
    h = head(rk)
    cam(S, at(STA, lerp(3.4, 2.6, k), lerp(-2.6, -1.8, k), 14.3), plus(h, (0.0, 0.0, -0.35)), 30)


def photo_thumb(S, k, t, lt):
    """The thumbnail picture: the gunner falling on his back, close, on the right of the frame, the long glass roof of
    the station far below him on the left."""
    sky(S, 'low')
    S['hlamp'].data.energy = 2500
    m = S['man']
    put(m, at(STA, 5.0, -6.0, 96.0), 2.3, -PI / 2 + 0.25, 0.2, limp(0.7))
    m.face = 'shut'
    h = head(m)
    cam(S, plus(h, (-1.7, -0.5, 5.4)), at(STA, -10.0, 5.0, 0.0), 30)
    S['camfill'].data.energy = 900


NEW = (field_dawn, turret_under, rook_measure, turret_side, pack_hook, nose_fly, pens, wing_hit, spin_down, fuse_spin, fall_close,
       station_out, girders, bed_leg, arm_close, doc_talk, arm_wrap, bed_sit, camp_three, gate_open, medals, hangar_walk, cub_fly,
       mem_visit, rook_verdict)
SHORT_KINDS = set(SHOTS3D)
STILLS = dict(hole=photo_hole, thumb=photo_thumb)

# Every shot, old and new, gets a slight arc and push towards its subject, so that no frame of a held shot stands still.
# prm "arc": [degrees, push] sets the move for one use of a shot.
ARCS = dict(bomber_down=(8, 0.3), roof_rush=(0, 0.0), town_below=(0, 0.0), fall_wide=(0, 0.25), smash=(4, 0.0), hole_up=(0, 0.0),
            formation=(5, 0.12), pens=(0, 0.0), spin_down=(0, 0.0), cub_fly=(0, 0.0), turret_side=(0, 0.0), turret_close=(0, 0.0),
            fall_close=(0, 0.0), nose_fly=(0, 0.0), wing_hit=(0, 0.0), fuse_spin=(0, 0.0), station_out=(3, 0.05), girders=(6, 0.08),
            medals=(6, 0.1), bed_leg=(8, 0.1), arm_close=(8, 0.12), field_dawn=(4, 0.06))


def _alive(f, name):
    sign = 1 if sum(map(ord, name)) % 2 else -1
    d0 = ARCS.get(name, (8, 0.12))

    def g(S, k, t, lt):
        f(S, k, t, lt)
        deg, push = S['prm'].get('arc', (sign * d0[0], d0[1]))
        S['camtgt'].location.z -= S['prm'].get('drop', 0.0)      # the Short framed some shots for a tall frame: look lower
        c, tg = S['camrig'].location, S['camtgt'].location
        a = math.radians(deg) * (k - 0.5)
        m = 1 - push * (k - 0.5)
        dx, dy, dz = c[0] - tg[0], c[1] - tg[1], c[2] - tg[2]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, tg[2] + dz * m)
    g.__name__ = name
    g.__doc__ = f.__doc__
    return g


def _warded(f):
    def g(S, k, t, lt):
        f(S, k, t, lt)
        xshow(S, 'hosp')
        S['blanket'].location, S['blanket'].scale = (0, 0.4, 1.5), (2.15, 2.9, 0.52)
        if not S['prm'].get('noleg'):
            xshow(S, 'leg')
    g.__doc__ = f.__doc__
    return g


SHOTS3D.update({f.__name__: f for f in NEW})
for _n in ('doctor', 'rook_bed'):
    SHOTS3D[_n] = _warded(SHOTS3D[_n])
for _n in list(SHOTS3D):
    SHOTS3D[_n] = _alive(SHOTS3D[_n], _n)
