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
