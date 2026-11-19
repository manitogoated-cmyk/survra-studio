"""Case 017 in 3D - Steven Callahan, adrift in the Atlantic for 76 days, February to April 1982.
At night, about a week out of the Canary Islands, something hit his small sloop Napoleon Solo (he believes a whale)
and it went down. He got away in a six-man inflatable raft with an emergency bag: a short spear gun, solar stills.
Stills and rain gave him a little over a pint of water a day. Dorado gathered under the raft and he speared them to
eat. Ships passed; none saw him. A speared dorado drove the spear point into the raft's bottom tube and tore a hole;
patches failed until he forced a fork through the fabric around the hole and folded it shut. He lost about a third of
his weight. On the night of day 75 he saw lights; next day fishermen, drawn by the birds circling over the fish under
the raft, picked him up near Marie-Galante, Guadeloupe.

Built for this story only: the cabin of a small sloop flooding at night, the sloop going down on a night swell, a
round black raft with an orange half canopy riding a live low-poly ocean, an underwater set below the raft (the
raft's belly, light from the surface, a school of dorado), a freighter, the island's lights, frigate birds and a
small open fishing boat.

Everything is a generic low-poly reconstruction: no person's likeness is attempted and no boat is copied from a
photograph."""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -6000)
SEA = (0.0, 0.0, 0.0)               # the open ocean: the sloop, the raft, the ship, the island, the fishing boat
UNDER = (0.0, 5000.0, 0.0)          # below the raft
CABIN = (5000.0, 0.0, 0.0)          # inside the sloop
HOST = {'raft_alone', 'rook_raft', 'rook_still', 'spear_aim', 'rook_wave', 'rook_sink', 'rook_feather', 'thin_man',
        'rook_lights', 'boat_reach', 'rook_point', 'rook_question', 'signoff'}
CAMFILL = {'*': 140, 'cabin_flood': 120, 'boat_sink': 60, 'raft_jump': 220, 'raft_alone': 200, 'rook_raft': 260,
           'dawn_wide': 40, 'still_close': 120, 'rook_still': 200, 'under_fish': 30, 'spear_aim': 180, 'fish_catch': 30,
           'ship_pass': 60, 'rook_wave': 200, 'spear_hole': 40, 'raft_soft': 180, 'rook_sink': 200, 'patch_fail': 120,
           'rook_feather': 200, 'fork_fix': 120, 'thin_man': 160, 'night_lights': 160, 'rook_lights': 300,
           'birds_circle': 60, 'fishing_boat': 80, 'boat_reach': 180, 'rook_point': 200, 'fish_hull': 30,
           'rook_question': 200, 'signoff': 160}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN, HAIR = 'D29A74', '8A5A32'
TUBE, TUBE2, CANOPY = '2C2C33', '3A3A44', 'E8681E'
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction, sea colour
    storm=('1E2A3C', '05080F', 0.55, 0.5, '9AB4E0', (-0.3, 0.5, 0.8), '0A1A28'),
    dawn=('F2A27A', '3A5A90', 1.1, 2.4, 'FFC8A0', (0.8, 0.5, 0.25), '1E4A66'),
    day=('BEE0F2', '2F7AC0', 1.25, 3.6, 'FFF4E0', (0.4, -0.5, 0.75), '1A6A8E'),
    hot=('E8EEDC', '4A90C8', 1.35, 4.6, 'FFF8E8', (0.1, -0.2, 0.98), '207896'),
    dusk=('F08A5A', '2A3468', 1.0, 2.0, 'FFA070', (-0.85, 0.4, 0.18), '22405E'),
    night=('1A2A48', '060A16', 0.6, 0.7, 'A8C0F0', (-0.4, 0.3, 0.85), '0C2034'),
    morning=('F4D2A8', '5A8AC0', 1.2, 3.0, 'FFE4C0', (0.7, 0.4, 0.4), '1C628A'),
    under=('2A8AA8', '0A2A44', 0.9, 0.0, 'FFFFFF', (0, 0, 1), '1A6A8E'),
    cabin=('0A0A10', '040406', 0.15, 0.0, 'FFFFFF', (0, 0, 1), '0A1A28'))
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


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def box(par, col, x0, x1, y0, y1, z0, z1, **kw):
    return add('cube', col, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), scale=(x1 - x0, y1 - y0, z1 - z0), size=1, parent=par, **kw)


def bar(par, col, a, b, w, **kw):
    o = add('cylinder', col, radius=0.5, depth=1, vertices=6, parent=par, **kw)
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))
    return o


def half_dome(par, col, loc, r, keep_y=1, **kw):
    """An ico sphere with the half facing -keep_y cut away: the raft's half canopy, open towards the camera side."""
    o = add('ico_sphere', col, loc, radius=r, subdivisions=2, parent=par, **kw)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y * keep_y < -0.05 * r or v.co.z < -0.05 * r], context='VERTS')
    bm.to_mesh(o.data)
    bm.free()
    return o


# ---------------------------------------------------------------- the ocean
def wave(x, y, t, r):
    return r * (0.55 * np.sin(x * 0.19 + t * 1.1) + 0.36 * np.sin(y * 0.23 - t * 1.5 + x * 0.07) + 0.18 * np.sin((x + y) * 0.53 + t * 2.4))


def make_sea(S):
    s = empty(SEA)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=110, y_subdivisions=110, size=180, location=SEA)
    sea = bpy.context.object
    sea.parent = s
    sea.data.materials.append(K.mat('1A6A8E', 0.22))
    co = np.zeros(len(sea.data.vertices) * 3)
    sea.data.vertices.foreach_get('co', co)
    S['xy'] = co.reshape(-1, 3)[:, :2].copy()
    S['fade'] = np.clip((90 - np.maximum(np.abs(S['xy'][:, 0]), np.abs(S['xy'][:, 1]))) / 26, 0, 1)
    S['sea'] = sea
    S['farsea'] = add('plane', '1A6A8E', (0, 0, -0.4), size=6000, parent=s, rough=0.22)
    S['sea_root'] = s


def seas(S, t, rough, col):
    x, y = S['xy'][:, 0], S['xy'][:, 1]
    z = S['fade'] * wave(x, y, t, rough)
    S['sea'].data.vertices.foreach_set('co', np.column_stack([S['xy'], z]).ravel())
    S['sea'].data.update()
    m = K.mat(col, 0.2)
    S['sea'].data.materials[0] = m
    S['farsea'].data.materials[0] = m
    S['rough'] = rough


def wave_at(S, x, y, t):
    f = max(0.0, min(1.0, (90 - max(abs(x), abs(y))) / 26))
    return float(f * wave(np.array(x), np.array(y), t, S['rough']))


def ride(S, obj, t, x, y, yaw=0.0, lift=0.0, tilt=1.0, sink=0.0):
    h = wave_at(S, x, y, t)
    px = (wave_at(S, x, y + 1.2, t) - wave_at(S, x, y - 1.2, t)) / 2.4
    py = (wave_at(S, x + 1.2, y, t) - wave_at(S, x - 1.2, y, t)) / 2.4
    obj.location = (SEA[0] + x, SEA[1] + y, SEA[2] + h + lift - sink)
    obj.rotation_euler = (px * 0.7 * tilt, -py * 0.7 * tilt, yaw)


# ---------------------------------------------------------------- the raft
def make_raft(S):
    r = keep(empty(FAR))
    add('cylinder', '23232A', (0, 0, 0.02), radius=1.3, depth=0.06, vertices=16, parent=r, rough=0.8)            # floor
    S['tubes'] = []
    for z, col in ((0.2, TUBE), (0.52, TUBE2)):                                                                   # two stacked tubes
        S['tubes'].append(add('torus', col, (0, 0, z), major_radius=1.3, minor_radius=0.17, major_segments=20, minor_segments=6, parent=r, rough=0.5))
    for i in range(10):                                                                                           # lifeline loops round the outside
        a = 2 * PI * i / 10
        add('torus', 'D8D2C0', (1.5 * math.cos(a), 1.5 * math.sin(a), 0.36), rot=(PI / 2, 0, a + PI / 2), major_radius=0.12, minor_radius=0.02,
            major_segments=8, minor_segments=3, parent=r)
    add('torus', 'F0A030', (0, 0, 0.53), major_radius=1.3, minor_radius=0.03, major_segments=20, minor_segments=3, parent=r, rough=0.4)
    S['arch'] = add('torus', TUBE2, (0, 0.15, 0.6), rot=(0, PI / 2, 0), major_radius=1.35, minor_radius=0.09, major_segments=16, minor_segments=5, parent=r)
    S['canopy'] = half_dome(r, CANOPY, (0, 0.15, 0.6), 1.42, keep_y=1, rough=0.7)
    S['canopy'].scale = (1.0, 0.95, 1.12)
    add('cube', 'F2E8C8', (0, 1.5, 1.6), rot=(0.4, 0, 0), scale=(0.5, 0.04, 0.3), size=1, parent=r, rough=1.0)     # a reflective patch on the canopy
    # the solar still on its tether: a clear balloon with a black base and rings, drops inside
    st = S['still'] = keep(empty(FAR))
    add('cylinder', '1A1A20', (0, 0, 0.05), radius=0.42, depth=0.12, vertices=10, parent=st)
    add('ico_sphere', 'C8F0FF', (0, 0, 0.5), radius=0.48, subdivisions=2, parent=st, rough=0.05, alpha=0.25)
    for z, rr in ((0.25, 0.44), (0.55, 0.48), (0.85, 0.36)):
        add('torus', 'E8F8FF', (0, 0, z), major_radius=rr, minor_radius=0.018, major_segments=14, minor_segments=3, parent=st, rough=0.2)
    add('cone', '8AA8B8', (0, 0, 0.62), radius1=0.32, radius2=0.04, depth=0.5, vertices=8, parent=st, rough=0.3, alpha=0.5)
    S['drops'] = [add('ico_sphere', '7AD8FF', (0, 0, 0), radius=0.035, subdivisions=1, parent=st, rough=0.05, emit=0.6) for _ in range(5)]
    S['raft'] = r
    # the hole in the bottom tube, the patch, the fork
    S['hole'] = add('cube', '0A0A0C', (0.0, -1.46, 0.2), scale=(0.34, 0.06, 0.13), size=1, parent=r)
    S['hole'].hide_render = True
    S['patch'] = keep(add('cube', '7A7A82', FAR, scale=(0.32, 0.03, 0.2), size=1, rough=0.6))
    S['fork'] = f = keep(empty(FAR))
    add('cube', 'C8CCD4', (0, 0, 0.12), scale=(0.035, 0.02, 0.24), size=1, parent=f, rough=0.2)
    for i in range(3):
        add('cube', 'C8CCD4', (-0.04 + 0.04 * i, 0, -0.06), scale=(0.012, 0.015, 0.14), size=1, parent=f, rough=0.2)
    S['cup'] = keep(add('cylinder', 'D8D8D8', FAR, radius=0.08, depth=0.16, vertices=8, rough=0.3))
    S['cloth'] = keep(add('cube', 'FF7A1A', FAR, scale=(0.5, 0.02, 0.35), size=1, rough=1.0))
    # the spear gun: a short stock and a long spear
    S['gun'] = g = keep(empty(FAR))
    add('cube', '3A2A20', (0, 0, 0), scale=(0.08, 0.6, 0.1), size=1, parent=g)
    add('cube', '1A1A1E', (0, 0.12, -0.12), scale=(0.06, 0.08, 0.2), size=1, parent=g)
    S['spear'] = sp = keep(empty(FAR))
    add('cylinder', 'B8BCC4', (0, 0.6, 0), rot=(PI / 2, 0, 0), radius=0.018, depth=1.4, vertices=6, parent=sp, rough=0.2)
    add('cone', 'D8DCE4', (0, 1.36, 0), rot=(-PI / 2, 0, 0), radius1=0.04, radius2=0.0, depth=0.14, vertices=4, parent=sp, rough=0.2)


# ---------------------------------------------------------------- the sloop
def make_sloop(S):
    b = keep(empty(FAR))
    add('cube', 'E8E4DA', (0, 0, 0.4), scale=(2.2, 6.4, 1.2), size=1, parent=b)                                 # hull
    add('cube', 'E8E4DA', (0, 3.6, 0.5), rot=(0, 0, PI / 4), scale=(1.56, 1.56, 1.0), size=1, parent=b)          # bow
    add('cube', '2A4A7A', (0, 0.4, -0.05), scale=(2.24, 7.6, 0.18), size=1, parent=b)                             # boot stripe
    add('cube', 'B8AE98', (0, -0.8, 1.25), scale=(1.5, 2.6, 0.5), size=1, parent=b)                               # cabin top
    for i in range(3):
        add('cube', '1A2A3A', (0.76, -1.6 + 0.8 * i, 1.28), scale=(0.02, 0.4, 0.16), size=1, parent=b, emit=0.0)
    S['portglow'] = [add('cube', 'FFC070', (-0.76, -1.6 + 0.8 * i, 1.28), scale=(0.02, 0.4, 0.16), size=1, parent=b, emit=3.0) for i in range(3)]
    add('cylinder', 'C8C8CC', (0, 0.6, 5.5), radius=0.07, depth=9.0, vertices=6, parent=b, rough=0.3)            # mast
    bar(b, 'C8C8CC', (0, 0.6, 1.9), (0, -2.8, 1.9), 0.06, rough=0.3)                                              # boom
    add('cube', 'F2EEE2', (0, -1.1, 2.15), scale=(0.3, 3.2, 0.4), size=1, parent=b, rough=1.0)                    # furled sail
    bar(b, '9A9AA0', (0, 0.6, 9.9), (0, 3.8, 0.9), 0.02)                                                          # forestay
    S['sloop'] = b


# ---------------------------------------------------------------- the freighter, the island, the birds, the fishing boat
def make_far(S):
    sh = keep(empty(FAR))
    add('cube', '3A2420', (0, 0, 2.5), scale=(9, 80, 7), size=1, parent=sh)
    add('cube', '8A2A22', (0, 0, -0.4), scale=(9.1, 80.2, 1.4), size=1, parent=sh)
    add('cube', 'E8E4DC', (0, -30, 10), scale=(8, 10, 9), size=1, parent=sh)
    add('cube', 'E8E4DC', (0, -30, 15.5), scale=(9.5, 4, 2), size=1, parent=sh)
    add('cylinder', '2A2A30', (0, -36, 17), radius=1.6, depth=6, vertices=8, parent=sh)
    for i in range(4):
        add('cube', ('C84A2A', '2A6A9A', 'D8A830', '4A7A4A')[i], (0, 14 - 13 * i, 7.5), scale=(8, 11, 3), size=1, parent=sh)
        add('cylinder', 'D8B040', (3, 20 - 13 * i, 11), radius=0.3, depth=10, vertices=6, parent=sh)
    S['ship'] = sh
    il = keep(empty(FAR))
    add('cone', '0E141C', (0, 0, 12), radius1=260, radius2=60, depth=26, vertices=12, parent=il, rough=1.0)
    add('cone', '121A24', (-90, 30, 28), radius1=120, radius2=10, depth=56, vertices=10, parent=il, rough=1.0)
    S['lights'] = []
    for i in range(26):
        x = -200 + 400 * i / 25 + 8 * rnd(i, 3)
        S['lights'].append(add('ico_sphere', ('FFD890', 'FFF2D8', 'FFB860')[i % 3], (x * 0.8, -268 + 6 * rnd(i, 4), 0.8 + 2.5 * rnd(i, 5)), radius=1.3 + 0.8 * rnd(i, 6),
                               subdivisions=1, parent=il, emit=12.0))
    S['island'] = il
    S['birds'] = []
    for i in range(7):
        bd = keep(empty(FAR))
        add('cone', '1A1A22', (0, 0.15, 0), rot=(PI / 2, 0, 0), radius1=0.12, radius2=0.0, depth=0.9, vertices=4, parent=bd)
        wings = []
        for s_ in (-1, 1):
            w = empty((s_ * 0.05, 0, 0), bd)
            add('cube', '1E1E26', (s_ * 0.45, 0, 0), rot=(0, 0, s_ * 0.35), scale=(0.9, 0.26, 0.03), size=1, parent=w)
            add('cube', '1E1E26', (s_ * 1.1, -0.18, 0), rot=(0, 0, s_ * -0.5), scale=(0.7, 0.18, 0.03), size=1, parent=w)
            wings.append(w)
        add('cone', '1A1A22', (0, -0.6, 0), rot=(-PI / 2, 0, 0), radius1=0.18, radius2=0.0, depth=0.5, vertices=3, parent=bd)
        S['birds'].append((bd, wings))
    fb = keep(empty(FAR))                                                                                         # small open fishing boat
    add('cube', '2E6AA8', (0, 0, 0.35), scale=(2.0, 6.0, 0.9), size=1, parent=fb)
    add('cube', '2E6AA8', (0, 3.3, 0.45), rot=(0, 0, PI / 4), scale=(1.4, 1.4, 0.9), size=1, parent=fb)
    add('cube', 'F2C832', (0, 0.3, 0.86), scale=(2.06, 7.2, 0.14), size=1, parent=fb)
    add('cube', 'E8E2D4', (0, 0, 0.5), scale=(1.7, 5.6, 0.1), size=1, parent=fb)
    add('cube', '3A3A40', (0, -3.1, 0.9), scale=(0.4, 0.5, 0.8), size=1, parent=fb)                                # outboard
    for i in range(2):
        add('cube', '8A6A48', (0, -1.2 + 2.2 * i, 0.75), scale=(1.8, 0.3, 0.08), size=1, parent=fb)
    S['fboat'] = fb


# ---------------------------------------------------------------- under the raft
def make_under(S):
    u = empty(UNDER)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=60, size=120, location=at(UNDER, 0, 0, 0))
    sf = bpy.context.object
    sf.parent = u
    sf.data.materials.append(K.mat('8AE0F0', 0.1, emit=1.4))
    co = np.zeros(len(sf.data.vertices) * 3)
    sf.data.vertices.foreach_get('co', co)
    S['uxy'] = co.reshape(-1, 3)[:, :2].copy()
    S['usurf'] = sf
    S['ubelly'] = ub = keep(empty(FAR))                                                                           # the raft from below
    add('cylinder', '15151A', (0, 0, -0.05), radius=1.3, depth=0.08, vertices=16, parent=ub)
    add('torus', TUBE, (0, 0, 0.0), major_radius=1.3, minor_radius=0.2, major_segments=20, minor_segments=6, parent=ub, rough=0.5)
    for i in range(4):                                                                                            # ballast pockets
        a = 2 * PI * i / 4 + 0.4
        add('cone', 'C8641E', (0.8 * math.cos(a), 0.8 * math.sin(a), -0.45), rot=(PI, 0, 0), radius1=0.32, radius2=0.12, depth=0.7, vertices=6, parent=ub)
    S['uhole'] = add('cube', '050506', (0.0, -1.48, -0.02), scale=(0.24, 0.06, 0.1), size=1, parent=ub)
    S['ubar'] = add('torus', 'F0A030', (0, 0, 0.12), major_radius=1.3, minor_radius=0.03, major_segments=20, minor_segments=3, parent=ub)
    S['uhull'] = uh = keep(empty(FAR))                                                                            # the fishing boat's hull from below
    add('cube', '1E3A5A', (0, 0, -0.25), scale=(2.0, 6.0, 0.6), size=1, parent=uh)
    add('cube', '1E3A5A', (0, 3.3, -0.2), rot=(0, 0, PI / 4), scale=(1.4, 1.4, 0.5), size=1, parent=uh)
    for i in range(9):                                                                                            # shafts of light from the surface
        add('cone', 'BFF4FF', (-24 + 6 * i + 3 * rnd(i, 1), 6 + 10 * rnd(i, 2), -14), rot=(0.2 * (rnd(i, 3) - 0.5), 0.25 * (rnd(i, 4) - 0.5), 0),
            radius1=1.6 + 1.2 * rnd(i, 5), radius2=0.4, depth=30, vertices=6, parent=u, emit=0.6, alpha=0.08)
    add('plane', '0A3A52', (0, 0, -40), size=400, parent=u, rough=1.0)                                            # the deep below
    S['fish'] = []
    for i in range(16):
        f = keep(empty(FAR))
        body = add('ico_sphere', ('4AB88A', '3AA878', '58C090')[i % 3], (0, 0, 0), scale=(0.24, 1.0, 0.42), radius=0.62, subdivisions=1, parent=f, rough=0.3)
        add('ico_sphere', 'E8D040', (0, 0.05, -0.12), scale=(0.2, 0.9, 0.24), radius=0.55, subdivisions=1, parent=f, rough=0.3)
        add('cube', '2A7AA8', (0, 0.1, 0.3), scale=(0.04, 1.1, 0.16), size=1, parent=f, rough=0.3)                 # long dorsal fin
        tail = empty((0, -0.62, 0), f)
        add('cone', 'D8C030', (0, -0.18, 0), rot=(PI / 2, 0, 0), scale=(0.15, 1, 1.6), radius1=0.2, radius2=0.0, depth=0.3, vertices=4, parent=tail)
        for s_ in (-1, 1):
            add('cube', '0E0E14', (s_ * 0.13, 0.48, 0.06), scale=(0.02, 0.08, 0.08), size=1, parent=f)
        S['fish'].append((f, tail, body))
    S['bubbles'] = [keep(add('ico_sphere', 'D8F8FF', FAR, radius=0.05 + 0.04 * rnd(i, 9), subdivisions=1, rough=0.05, emit=0.8)) for i in range(18)]
    S['uspear'] = sp = keep(empty(FAR))
    add('cylinder', 'B8BCC4', (0, 0.6, 0), rot=(PI / 2, 0, 0), radius=0.022, depth=1.4, vertices=6, parent=sp, rough=0.2)
    add('cone', 'D8DCE4', (0, 1.36, 0), rot=(-PI / 2, 0, 0), radius1=0.05, radius2=0.0, depth=0.16, vertices=4, parent=sp, rough=0.2)
    S['uline'] = keep(add('cylinder', 'E8E8E8', FAR, radius=0.008, depth=1, vertices=4))
    S['under'] = u


def usurf(S, t):
    x, y = S['uxy'][:, 0], S['uxy'][:, 1]
    z = 0.35 * np.sin(x * 0.4 + t * 1.3) + 0.25 * np.sin(y * 0.5 - t * 1.6)
    S['usurf'].data.vertices.foreach_set('co', np.column_stack([S['uxy'], z]).ravel())
    S['usurf'].data.update()


def school(S, t, cx, cy, cz, spread=1.0, n=16, skip=()):
    """The dorado school circling under the raft, each on its own orbit, tails beating."""
    for i, (f, tail, body) in enumerate(S['fish']):
        if i >= n or i in skip:
            f.location = FAR
            continue
        a = t * (0.35 + 0.25 * rnd(i, 1)) * (1 if i % 2 else -1) + 2 * PI * rnd(i, 2)
        rr = (1.6 + 3.2 * rnd(i, 3)) * spread
        z = cz - (0.6 + 3.5 * rnd(i, 4)) * spread + 0.3 * math.sin(t * 0.9 + i)
        f.location = at(UNDER, cx + rr * math.cos(a), cy + rr * math.sin(a), z)
        f.rotation_euler = (0.1 * math.sin(t + i), 0, a + (PI if i % 2 else 0))
        s = 1.0 + 0.35 * rnd(i, 5)
        f.scale = (s, s, s)
        tail.rotation_euler = (0, 0, 0.45 * math.sin(t * 9 + i))


def bubble(S, t, x, y, z, n=18, rise=1.4, spread=0.25):
    for i, b in enumerate(S['bubbles']):
        if i >= n:
            b.location = FAR
            continue
        ph = (t * rise * (0.8 + 0.4 * rnd(i, 1)) + rnd(i, 2)) % 1.0
        b.location = (x + spread * (ph * 3.0 - 0.3) + 0.08 * math.sin(i * 2.1 + t * 3), y + 0.1 * math.cos(i * 1.7 + t * 2), z - 0.5 + 0.48 * ph)


# ---------------------------------------------------------------- the cabin
def make_cabin(S):
    c = empty(CABIN)
    box(c, '6A4A30', -1.6, 1.6, -3.2, 3.2, -0.1, 0.0)                                                             # sole
    for s_ in (-1, 1):
        for i in range(5):                                                                                        # curved hull sides in planks
            add('cube', ('7A5636', '6A4A2E')[i % 2], (s_ * (1.55 + 0.12 * i), 0, 0.25 + 0.48 * i), rot=(0, s_ * -0.18, 0), scale=(0.08, 6.4, 0.46), size=1, parent=c)
        box(c, '8A6A48', s_ * 1.0 - 0.45, s_ * 1.0 + 0.45, 0.2, 2.8, 0.0, 0.7)                                      # bunks
        add('cube', '3A5A8A', (s_ * 1.0, 1.5, 0.78), scale=(0.85, 2.4, 0.16), size=1, parent=c, rough=1.0)
    box(c, '5A3E28', -1.9, 1.9, -0.2, 3.2, 2.5, 2.62)                                                            # deckhead
    box(c, '4A3220', -1.9, 1.9, 3.1, 3.3, 0, 2.6)
    box(c, '4A3220', -1.9, -0.45, -3.3, -3.1, 0, 2.6)
    box(c, '4A3220', 0.45, 1.9, -3.3, -3.1, 0, 2.6)
    for i in range(4):                                                                                            # companionway steps
        box(c, '8A6A48', -0.42, 0.42, -3.05 + 0.25 * i, -2.85 + 0.25 * i, 0.4 + 0.5 * i, 0.48 + 0.5 * i)
    S['clamp'] = cl = keep(empty(at(CABIN, 0.6, 1.0, 2.5)))                                                       # hanging lamp
    add('cylinder', '2A2A2E', (0, 0, -0.25), radius=0.01, depth=0.5, vertices=4, parent=cl)
    add('cylinder', 'FFC070', (0, 0, -0.6), radius=0.1, depth=0.22, vertices=8, parent=cl, emit=6.0)
    S['clampl'] = light(at(CABIN, 0.6, 1.0, 1.7), 0, 'FFB060', size=0.3)
    add('cube', 'C8B898', (-1.2, -2.2, 1.6), scale=(0.5, 0.6, 0.04), size=1, parent=c, rough=1.0)                 # a chart pinned up
    for i in range(6):                                                                                            # things on the shelf
        add('cube', ('C8322A', 'E8E2D4', '2A6A9A')[i % 3], (1.45, -2.4 + 0.3 * i, 1.55), scale=(0.15, 0.2, 0.3), size=1, parent=c)
    S['flood'] = keep(add('plane', '1A4A60', FAR, size=1, scale=(3.4, 6.8, 1), rough=0.1))
    S['spray'] = [keep(add('ico_sphere', 'B8E8F8', FAR, radius=0.06, subdivisions=1, rough=0.05, emit=0.5)) for _ in range(12)]
    S['torch'] = tr = keep(empty(FAR))
    add('cylinder', 'D8B830', (0, 0, 0), rot=(PI / 2, 0, 0), radius=0.06, depth=0.34, vertices=8, parent=tr)
    add('cylinder', 'FFF2C8', (0, -0.18, 0), rot=(PI / 2, 0, 0), radius=0.07, depth=0.02, vertices=8, parent=tr, emit=12.0)
    S['torchaim'] = keep(empty(FAR))
    S['torchl'] = light(FAR, 0, 'FFF2D0', kind='SPOT', spot=0.7, target=S['torchaim'])
    S['cabin'] = c


# ---------------------------------------------------------------- people
def callahan_head(head):
    d = K.human_head(SKIN, HAIR)(head)
    S_ = d
    S_['beard'] = add('ico_sphere', HAIR, (0, -0.12, -0.17), scale=(0.9, 0.7, 0.55), radius=0.27, subdivisions=1, parent=head)
    return d


def fisher_head(skin, hat):
    def fn(head):
        d = K.human_head(skin, '17131A')(head)
        add('cylinder', hat, (0, 0, 0.24), radius=0.48, depth=0.04, vertices=10, parent=head, rough=1.0)
        add('cone', hat, (0, 0, 0.38), radius1=0.3, radius2=0.08, depth=0.3, vertices=10, parent=head, rough=1.0)
        return d
    return fn


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_sea(S)
    make_raft(S)
    make_sloop(S)
    make_far(S)
    make_under(S)
    make_cabin(S)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['man'] = K.Rig(dict(top='6A8EB0', pants='3A4A5A', hand=SKIN, boot=SKIN, fore=SKIN), callahan_head)
    S['fishers'] = [K.Rig(dict(top=tp, pants=pa, hand=sk, boot='2A2018', fore=sk), fisher_head(sk, ht))
                    for tp, pa, sk, ht in (('E8D8A8', '3A3A48', '6A4430', 'D8C08A'), ('C84A3A', '2A2A36', '5A3A26', 'E8D8B0'), ('F2F0E8', '4A4038', '7A4E32', 'C8A870'))]
    S['humans'] = [S['man']] + S['fishers']
    S['cast'] = [S['rook']] + S['humans']
    S['rfea'] = keep(add('cone', '3A3466', FAR, radius1=0.12, radius2=0, depth=0.8, vertices=4))
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    S['keyl'] = light((0, 0, 0), 0, 'FFE8D0', size=3.0)
    S['keytgt'] = empty()
    S['keyl'].constraints.new('TRACK_TO').target = S['keytgt']
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 3000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w17')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.02, 0.6
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
        rig.face, rig.jawv = 'calm', 0.0
        rig.body.scale = (1, 1, 1)
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for l in (S['sun'], S['keyl'], S['clampl'], S['torchl']):
        l.data.energy = 0
    S['torchl'].location = FAR
    S['hole'].hide_render = True
    S['canopy'].scale = (1.0, 0.95, 1.12)
    for tb in S['tubes']:
        tb.scale = (1, 1, 1)
    S['man'].extra['beard'].scale = (0.9, 0.7, 0.55)
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, rough=0.6)
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
        k = dict(calm=1.0, wide=1.8, shut=0.07, tired=0.5, warm=0.8, sad=0.55, hard=0.6, squint=0.3, pain=0.25).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.045 if f == 'wide' else -0.02 if f in ('hard', 'tired', 'squint', 'pain') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide', 'tired', 'pain') else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.2 if f == 'warm' else 0.13, 0.03, 0.035 + 0.14 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sky(S, a, b=None, k=0.0, rough=0.6, t=0.0):
    A, B = SKIES[a], SKIES[b or a]
    mixc = lambda i: tuple(lerp(x, y, k) for x, y in zip(K.hexc(A[i]), K.hexc(B[i])))
    S['skymix'].inputs[6].default_value = mixc(0)
    S['skymix'].inputs[7].default_value = mixc(1)
    S['bg'].inputs[1].default_value = lerp(A[2], B[2], k)
    S['sun'].data.energy = lerp(A[3], B[3], k)
    S['sun'].data.color = mixc(4)[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(lerp(u, v, k) * 500 for u, v in zip(A[5], B[5]))
    if a not in ('under', 'cabin'):
        seas(S, t, rough, A[6] if k < 0.5 else B[6])
    else:
        S['sea_root'].location = FAR
        S['sea'].location = (0, 0, 0)


def ocean(S, mood, t, rough=0.6, b=None, k=0.0):
    S['sea_root'].location = SEA
    sky(S, mood, b, k, rough, t)


def shoot(S, o, pos, look, lens=40, roll=0.0):
    S['camrig'].location, S['camtgt'].location = at(o, *pos), at(o, *look)
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)


def key(S, o, pos, look, watts, col='FFE8D0'):
    S['keyl'].location, S['keytgt'].location = at(o, *pos), at(o, *look)
    S['keyl'].data.energy, S['keyl'].data.color = watts, K.hexc(col)[:3]


def put(S, rig, o, x, y, z=0.0, yaw=0.0, pose=None, face=None, pitch=0.0):
    rig.root.parent = None
    rig.place(at(o, x, y, z), yaw, pitch)
    rig.apply(pose or P())
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def aboard(S, rig, x, y, z=0.04, yaw=0.0, pose=None, face=None, par=None):
    """Seat a rig on the raft (or another floating thing), so it rides the swell with it."""
    rig.root.parent = par or S['raft']
    rig.place((x, y, z), yaw)
    rig.apply(pose or P())
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def head(S, rig):
    return wpos(rig.head)


def raft_at(S, t, x=0.0, y=0.0, yaw=0.0, sink=0.0, tilt=1.0):
    ride(S, S['raft'], t, x, y, yaw, 0.08, tilt, sink)
    return S['raft']


def thin(S, k):
    """The weight he lost: his body narrows, his face hollows under the beard."""
    S['man'].body.scale = (1 - 0.22 * k, 1 - 0.22 * k, 1)
    S['man'].extra['beard'].scale = (0.9 + 0.15 * k, 0.7 + 0.15 * k, 0.55 + 0.35 * k)


def still_at(S, t, x, y):
    ride(S, S['still'], t, x, y, 0.3, 0.02, 1.4)
    for i, d in enumerate(S['drops']):
        ph = (t * 0.6 + i * 0.2) % 1.0
        a = i * 1.3
        d.location = (0.36 * math.cos(a) * (1 - 0.3 * ph), 0.36 * math.sin(a) * (1 - 0.3 * ph), 0.85 - 0.62 * ph)


def birds(S, t, cx, cy, cz, rad=8.0, n=7):
    for i, (bd, wings) in enumerate(S['birds']):
        if i >= n:
            bd.location = FAR
            continue
        a = t * (0.5 + 0.12 * i) + 2 * PI * i / n
        r = rad * (0.7 + 0.5 * rnd(i, 1))
        bd.location = (cx + r * math.cos(a), cy + r * math.sin(a), cz + 3 * rnd(i, 2) + 0.6 * math.sin(t + i))
        bd.rotation_euler = (0, -0.3, a)
        f = 0.5 * math.sin(t * 6 + i)
        for s_, w in zip((-1, 1), wings):
            w.rotation_euler = (0, s_ * (f - 0.25), 0)
        bd.scale = (0.9, 0.9, 0.9)


# ---------------------------------------------------------------- the hook: the night the sloop went down
def cabin_flood(S, k, t, lt):
    """Inside the sloop at night, close on his face lit by his own torch: sea water spurting in and rising round him,
    the lamp swinging hard. First and last shot."""
    d = lt / k if k > 1e-3 else 1.5
    u = (1 - k) * d if S['prm'].get('loop') else lt
    sky(S, 'cabin')
    rl = 0.18 * math.sin(t * 2.3) + 0.06
    S['cabin'].rotation_euler = (0.05 * math.sin(t * 1.7), rl, 0)
    S['clamp'].rotation_euler = (0.5 * math.sin(t * 3.0), -rl * 2.5, 0)
    S['clampl'].data.energy = 60
    lvl = 0.25 + 0.35 * sm(u / 1.6)
    S['flood'].location, S['flood'].rotation_euler = at(CABIN, 0, 0, lvl), (0, 0.05 * math.sin(t * 3), 0)
    m = put(S, S['man'], CABIN, 0.0, 0.6, -0.15, 0.2, P('stand', aR=(1.3, 0.1, 1.5, 0.3), aL=(0.4, 0.5, 0.4), head=(lerp(-0.1, 0.12, sm(u / 1.2)), -0.15), lean=0.1), 'wide')
    m.jawv = 0.35
    hd = wpos(m.hands[1])
    S['torch'].location, S['torch'].rotation_euler = hd, (0.25, 0, 0.6)
    h = head(S, m)
    S['torchl'].location, S['torchaim'].location = (hd[0] - 0.3, hd[1] - 0.6, hd[2] + 0.2), (h[0], h[1], h[2] - 0.6)
    S['torchl'].data.energy = 260
    for i, sp in enumerate(S['spray']):                                                                           # a jet of water through the planks
        ph = (t * 1.8 + i / 12) % 1.0
        sp.location = at(CABIN, -1.5 + 1.6 * ph, -0.6 + 0.4 * rnd(i, 3), 0.7 + 0.6 * ph - 1.6 * ph * ph)
    key(S, CABIN, (-1.2, -1.6, 1.8), h, 220, '7AA8E0')
    shoot(S, (0, 0, 0), (h[0] + lerp(-0.7, -0.5, sm(u / 1.5)), h[1] - lerp(2.6, 2.1, sm(u / 1.5)), h[2] + 0.1), (h[0], h[1], h[2] - 0.45), 30, roll=0.6 * rl)


def boat_sink(S, k, t, lt):
    """Night, out on the black swell: the little white sloop down by the bow, cabin lights still on, going under; the
    black raft has burst open on the water beside it."""
    ocean(S, 'storm', t, 1.0)
    b = S['sloop']
    ride(S, b, t, 0, 0, 0.5, 0.2, 0.6, sink=0.3 + 0.8 * k)
    b.rotation_euler = (b.rotation_euler[0] + 0.32 + 0.12 * k, b.rotation_euler[1] + 0.1, b.rotation_euler[2])
    raft_at(S, t, -4.5, -2.0, 0.4)
    key(S, SEA, (-8, -12, 9), (-1, 0, 1), 9000, '9AB4E0')
    shoot(S, SEA, (lerp(-9, -8, k), lerp(-20, -17, k), lerp(2.6, 2.2, k)), (-1.4, 0, 1.4), 32)


def raft_jump(S, k, t, lt):
    """Close on the raft as he tumbles in over the tube from the sinking deck, the emergency bag in his arms, the sloop's
    rail going under behind him."""
    ocean(S, 'storm', t, 0.9)
    r = raft_at(S, t, 0, 0, 0.3)
    ride(S, S['sloop'], t, 1.0, 4.2, 0.9, 0.2, 0.6, sink=2.6 + 0.6 * k)
    u = sm(lt / 0.8)
    aboard(S, S['man'], lerp(0.6, 0.1, u), lerp(1.4, 0.3, u), lerp(0.8, 0.05, u), 0.2,
           blend(P('reach', aL=(2.4, 0.4, 0.3), lean=0.7), P('sit', aL=(1.0, -0.2, 1.8, 1.0), aR=(1.0, -0.2, 1.8, 1.0), head=(-0.15, 0.0)), u), 'wide')
    h = head(S, S['man'])
    key(S, SEA, (h[0] - 3, h[1] - 4, h[2] + 3), h, 1800, 'A8C0F0')
    shoot(S, (0, 0, 0), (h[0] + lerp(-1.6, -1.2, k), h[1] - lerp(4.2, 3.6, k), h[2] + lerp(0.6, 0.3, k)), (h[0], h[1], h[2] - 0.3), 30)


def raft_alone(S, k, t, lt):
    """Wide and high, night: the tiny raft alone on the black swell where the sloop was, a few bubbles; Rook drops onto
    the canopy and folds his wings."""
    ocean(S, 'storm', t, 1.1)
    r = raft_at(S, t, 0, 0, 0.6 + 0.5 * k)
    aboard(S, S['man'], -0.2, -0.3, 0.04, 0.6, P('sit', head=(lerp(0.3, -0.4, k), 0.3)), 'wide')
    u = sm(lt / 1.3)
    fl = math.sin(lt * 14) * (1 - u)
    aboard(S, S['rook'], 0.0, 0.5, lerp(6.0, 2.1, u), 0.6 + 1.2 * (1 - u), blend(P('up', aL=(2.6, 0.9 + 0.5 * fl, 0.1), aR=(2.6, 0.9 + 0.5 * fl, 0.1)), P('cross'), u), 'low')
    S['sloop'].location = at(SEA, 3.0, 3.5, -3.0 - 2.0 * k)
    S['sloop'].rotation_euler = (0.9, 0.2, 0.4)
    bubble(S, t, 3.0, 3.5, wave_at(S, 3.0, 3.5, t) + 0.3, 18, 1.6, 0.8)
    key(S, SEA, (-4, -6, 7), (0, 0, 1), 7000, 'A8C0F0')
    shoot(S, SEA, (lerp(-8, -3.5, k), lerp(-12, -8.5, k), lerp(10, 5, k)), (0.5, 0.8, lerp(1.2, 1.8, k)), 30, roll=lerp(-0.08, 0.05, k))


# ---------------------------------------------------------------- doubt
def rook_raft(S, k, t, lt):
    """Rook on the raft's tube in the dark, poking the rubber with one finger; it gives. He turns to us, unimpressed."""
    ocean(S, 'storm', t, 0.9)
    raft_at(S, t, 0, 0, 0.2)
    aboard(S, S['man'], 0.2, 0.5, 0.04, PI + 0.3, P('sit', head=(0.35, 0.2)), 'tired')
    poke = 0.5 + 0.5 * math.sin(lt * 12) if lt < 0.6 else 0.0
    turn = sm((lt - 0.55) / 0.35)
    aboard(S, S['rook'], -0.9, -0.95, 0.66, lerp(PI * 0.75, 0.15, turn),
           P('point', aR=(lerp(0.9, 1.1, poke), 0.1, 0.5), lean=0.25, head=(0.3, 0.0)) if turn < 0.5 else P('cross', head=(0.0, 0.0)), 'low')
    S['tubes'][1].scale = (1, 1, 1 - 0.05 * poke)
    S['hat_tip'] = 0.4 * turn
    h = head(S, S['rook'])
    key(S, SEA, (h[0] - 2, h[1] - 4, h[2] + 2), h, 1100, 'A8C0F0')
    shoot(S, (0, 0, 0), (h[0] - lerp(0.9, 0.5, k), h[1] - lerp(3.4, 2.8, k), h[2] - 0.15), (h[0] + 0.1, h[1], h[2] - 0.35), 34)


# ---------------------------------------------------------------- water
def dawn_wide(S, k, t, lt):
    """Dawn: the raft and its orange canopy a speck in an endless ocean, the sun just up."""
    ocean(S, 'dawn', t, 0.9)
    raft_at(S, t, 0, 0, 0.9)
    aboard(S, S['man'], 0.0, 0.3, 0.04, PI + 0.9, P('sit', head=(-0.1, 0.4)), 'tired')
    still_at(S, t, -2.6, -1.0)
    shoot(S, SEA, (lerp(20, 16, k), lerp(-30, -26, k), lerp(5, 4.4, k)), (0, 0, 0.8), 34)


def still_close(S, k, t, lt):
    """Close on the solar still riding on its tether beside the raft: drops of fresh water run down inside its clear skin."""
    ocean(S, 'day', t, 0.5)
    raft_at(S, t, 0, 0, 0.2)
    still_at(S, t, -1.7, -1.9)
    p = wpos(S['still'], (0, 0, 0.5))
    key(S, SEA, (p[0] - 2, p[1] - 3, p[2] + 2), p, 400, 'FFF4E0')
    shoot(S, (0, 0, 0), (p[0] + lerp(1.4, 0.9, k), p[1] - lerp(2.4, 1.8, k), p[2] + lerp(0.6, 0.3, k)), (p[0], p[1], p[2] - 0.05), 38)


def rook_still(S, k, t, lt):
    """In the raft: he tips a little cup of water from the still to his lips; Rook holds the still up and taps it, then
    squints at how little is in the cup."""
    ocean(S, 'hot', t, 0.4)
    raft_at(S, t, 0, 0, 0.1)
    m = aboard(S, S['man'], -0.65, 0.4, 0.04, 0.45, P('sit', aR=(1.4, 0.0, 2.1, 0.4), head=(-0.2, 0.0)), 'tired')
    hd = wpos(m.hands[1])
    S['cup'].location = (hd[0], hd[1] - 0.06, hd[2] + 0.12)
    S['cup'].rotation_euler = (-0.6, 0, 0)
    tap = 0.25 * math.sin(lt * 14) if lt < 0.7 else 0.0
    aboard(S, S['rook'], 0.75, -0.05, 0.04, -0.5, P('sit', aR=(1.2 + tap, 0.2, 0.7), aL=(0.9, -0.2, 1.4, 0.6), head=(0.15, -0.3)), 'low' if lt > 0.7 else 'calm')
    S['hat_tip'] = 0.25
    h = head(S, S['rook'])
    key(S, SEA, (h[0] - 1, h[1] - 4, h[2] + 3), h, 500, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] - lerp(0.4, 0.2, k), h[1] - lerp(4.6, 4.0, k), h[2] + 0.5), (h[0] - 0.5, h[1] + 0.2, h[2] - 0.4), 28)


# ---------------------------------------------------------------- the fish
def under_fish(S, k, t, lt):
    """Underwater, looking up: the raft is a dark disc against the bright surface, and a school of gold-green dorado
    circles below it in shafts of light."""
    sky(S, 'under')
    usurf(S, t)
    S['ubelly'].location = at(UNDER, 0, 0, -0.05)
    school(S, t, 0, 0, -0.6, 1.0)
    shoot(S, UNDER, (lerp(3.5, 2.5, k), lerp(-9.5, -8.0, k), lerp(-7.5, -6.8, k)), (0, 0, -1.4), 24)


def spear_aim(S, k, t, lt):
    """Over the tube, close: he leans out with the short spear gun, aiming down into the water; Rook leans out beside him
    and peers down too."""
    ocean(S, 'day', t, 0.45)
    raft_at(S, t, 0, 0, 0.0)
    m = aboard(S, S['man'], 0.0, -0.55, 0.04, 0.0, P('sit', aR=(1.0, 0.0, 0.4), aL=(1.0, 0.1, 0.6), lean=0.75, head=(0.6, 0.0)), 'squint')
    hd = wpos(m.hands[1])
    hl = wpos(m.hands[0])
    S['gun'].location = ((hd[0] + hl[0]) / 2, (hd[1] + hl[1]) / 2 - 0.2, (hd[2] + hl[2]) / 2)
    S['gun'].rotation_euler = (-0.8, 0, 0)
    S['spear'].location, S['spear'].rotation_euler = S['gun'].location, (-0.8, 0, 0)
    aboard(S, S['rook'], 0.95, -0.4, 0.66, 0.15, P('stand', lean=0.6, aL=(0.3, 0.6, 0.4), head=(0.6, 0.0)), 'calm')
    h = head(S, m)
    key(S, SEA, (h[0] + 2, h[1] - 4, h[2] + 3), h, 600, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.1, 0.6, k), h[1] - lerp(3.6, 3.0, k), h[2] - lerp(0.8, 1.0, k)), (h[0] + 0.3, h[1] - 0.2, h[2] - 0.5), 28)


def fish_catch(S, k, t, lt):
    """Underwater: the spear shoots down on its line and one dorado jerks away with it; the rest of the school scatters."""
    sky(S, 'under')
    usurf(S, t)
    S['ubelly'].location = at(UNDER, 0, 0, -0.05)
    u = sm(lt / 0.35)
    school(S, t, 0, 0, -0.6, 0.8 + 0.4 * sm((lt - 0.3) / 0.6), skip=(3,))
    f, tail, body = S['fish'][3]
    fx, fy, fz = 0.6 + 0.8 * sm((lt - 0.35) / 0.8), -1.2, -2.6 - 0.4 * sm((lt - 0.35) / 0.8)
    f.location = at(UNDER, fx, fy, fz)
    f.rotation_euler = (0.2 * math.sin(lt * 30) * (lt > 0.35), 0, 1.2 + 0.4 * math.sin(lt * 22) * (lt > 0.35))
    f.scale = (1.3, 1.3, 1.3)
    tail.rotation_euler = (0, 0, 0.7 * math.sin(t * 20))
    tip = Vector(at(UNDER, fx, fy, fz))
    start = Vector(at(UNDER, 0.2, -1.4, 0.3))
    sp = start.lerp(tip, u)
    S['uspear'].location = sp
    S['uspear'].rotation_euler = (tip - start).to_track_quat('Y', 'Z').to_euler()
    S['uspear'].location = sp - (tip - start).normalized() * 1.4 * 0.95
    shoot(S, UNDER, (lerp(3.4, 2.8, k), lerp(-6.0, -5.4, k), lerp(-3.4, -3.0, k)), (0.6, -1.0, -1.8), 26)


# ---------------------------------------------------------------- ships pass
def ship_pass(S, k, t, lt):
    """From low beside the raft: a big freighter crosses the horizon close enough to count its containers. He stands in
    the raft and waves an orange cloth over his head. It keeps going."""
    ocean(S, 'day', t, 0.6)
    raft_at(S, t, 0, 0, 0.0)
    S['ship'].location = at(SEA, lerp(-40, -10, k), 180, -0.5)
    S['ship'].rotation_euler = (0, 0, PI / 2)
    w = math.sin(lt * 8)
    m = aboard(S, S['man'], 0.0, 0.2, 0.04, PI, P('up', aL=(2.8, 0.4 + 0.3 * w, 0.2), aR=(2.6, 0.2 - 0.3 * w, 0.4), head=(-0.15, 0.0)), 'wide')
    hd = wpos(m.hands[0])
    S['cloth'].location, S['cloth'].rotation_euler = (hd[0], hd[1], hd[2] + 0.2), (0, 0.4 * w, 0)
    key(S, SEA, (0, -6, 4), (0, 0, 2.5), 600, 'FFF4E0')
    shoot(S, SEA, (lerp(1.5, 1.8, k), lerp(-6.5, -6.0, k), 1.0), (-2.0, 30, 4.5), 30)


def rook_wave(S, k, t, lt):
    """Rook on the canopy, waving his hat in big arcs at the ship; it does not turn. His arm drops, and so does his brim."""
    ocean(S, 'day', t, 0.6)
    raft_at(S, t, 0, 0, 0.0)
    S['ship'].location = at(SEA, lerp(-6, 10, k), 180, -0.5)
    S['ship'].rotation_euler = (0, 0, PI / 2)
    give = sm((lt - 0.65) / 0.35)
    w = math.sin(lt * 9) * (1 - give)
    aboard(S, S['rook'], 0.0, 0.6, 2.08, PI - 0.6, blend(P('up', aR=(2.7, 0.3 + 0.5 * w, 0.2), aL=(0.4, 0.3, 0.3)), P('stand', head=(0.3, 0.0)), give), 'calm' if give < 0.5 else 'low')
    S['hat_tip'] = 0.8 * give
    h = head(S, S['rook'])
    key(S, SEA, (h[0] + 2, h[1] - 4, h[2] + 2), h, 800, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] + lerp(4.8, 4.2, k), h[1] - lerp(2.6, 2.0, k), h[2] - lerp(0.6, 0.4, k)), (h[0] - 0.6, h[1] + 0.8, h[2] - 1.1), 28)


# ---------------------------------------------------------------- re-hook: the hole
def spear_hole(S, k, t, lt):
    """Underwater, close on the raft's belly: a speared dorado thrashes, the spear point rakes up into the bottom tube
    and rips it; a stream of air bubbles pours out."""
    sky(S, 'under')
    usurf(S, t)
    S['ubelly'].location = at(UNDER, 0, 0, -0.05)
    school(S, t, 0, 0, -1.0, 1.6, n=8)
    f, tail, body = S['fish'][0]
    th = math.sin(lt * 26)
    f.location = at(UNDER, -0.3 + 0.1 * th, -1.9, -1.1 + 0.08 * th)
    f.rotation_euler = (0.15 * th, 0, PI / 2 + 0.3 * th)
    f.scale = (1.3, 1.3, 1.3)
    tail.rotation_euler = (0, 0, 0.8 * math.sin(t * 24))
    rip = sm((lt - 0.25) / 0.3)
    tipz = lerp(-0.6, -0.05, rip)
    S['uspear'].location = at(UNDER, -0.3 + 0.1 * th, -1.75, tipz - 1.3)
    S['uspear'].rotation_euler = (PI / 2 - 0.1, 0, 0.1 * th)
    S['uhole'].hide_render = rip < 0.6
    if rip > 0.6:
        bubble(S, t, UNDER[0], UNDER[1] - 1.5, UNDER[2], 18, 2.0, 0.4)
    shoot(S, UNDER, (lerp(1.8, 1.4, k), lerp(-5.6, -5.0, k), lerp(-1.3, -1.1, k)), (-0.1, -1.6, -0.6), 30)


def raft_soft(S, k, t, lt):
    """In the raft: the bottom tube sags, water slops over the floor and he grabs at the soft rubber with both hands."""
    ocean(S, 'day', t, 0.7)
    raft_at(S, t, 0, 0, 0.0, sink=0.12 * k, tilt=1.6)
    S['tubes'][0].scale = (1, 1, 1 - 0.5 * sm(k))
    S['canopy'].scale = (1.0, 0.95, 1.12 - 0.15 * sm(k))
    m = aboard(S, S['man'], 0.0, -0.3, 0.04, 0.2, P('sit', aR=(1.2, 0.2, 0.6), aL=(1.2, 0.2, 0.6), lean=0.6, head=(0.5, 0.0)), 'wide')
    h = head(S, m)
    key(S, SEA, (h[0] + 2, h[1] - 3, h[2] + 3), h, 700, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] - lerp(1.2, 0.8, k), h[1] - lerp(3.0, 2.4, k), h[2] + lerp(0.8, 0.5, k)), (h[0], h[1] - 0.5, h[2] - 0.6), 28)


def rook_sink(S, k, t, lt):
    """Rook standing on the tube as it goes soft: it folds under his boots, he drops to his knees and his hat jumps off."""
    ocean(S, 'day', t, 0.7)
    raft_at(S, t, 0, 0, 0.3, sink=0.12, tilt=1.6)
    S['tubes'][0].scale = (1, 1, 0.5)
    u = sm(lt / 0.5)
    aboard(S, S['rook'], 0.2, -1.1, lerp(0.66, 0.25, u), 0.2, blend(P('stand'), P('up', lL=(0.6, 1.4), lR=(0.6, 1.4), lift=-0.4), u), 'shocked' if u > 0.3 else 'calm')
    S['hat_jump'] = 0.6 * math.sin(PI * sm((lt - 0.2) / 0.6))
    h = head(S, S['rook'])
    key(S, SEA, (h[0] + 2, h[1] - 4, h[2] + 2), h, 900, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] + lerp(0.6, 0.4, k), h[1] - lerp(3.2, 2.8, k), h[2] - 0.2), (h[0], h[1], h[2] - 0.2), 32)


# ---------------------------------------------------------------- repair
def patch_fail(S, k, t, lt):
    """Close on the hole in the tube: his hands press a grey patch over it; it bubbles and peels away again."""
    ocean(S, 'hot', t, 0.4)
    r = raft_at(S, t, 0, 0, 0.0, sink=0.1, tilt=0.6)
    S['tubes'][0].scale = (1, 1, 0.6)
    S['hole'].hide_render = False
    m = aboard(S, S['man'], 0.0, -0.6, 0.04, 0.0, P('sit', aR=(1.25, 0.05, 0.4), aL=(1.25, 0.05, 0.4), lean=0.9, head=(0.8, 0.0)), 'hard')
    hp = wpos(r, (0, -1.47, 0.2))
    peel = sm((lt - 0.6) / 0.4)
    S['patch'].location = (hp[0], hp[1] - 0.04 - 0.3 * peel, hp[2] - 0.2 * peel)
    S['patch'].rotation_euler = (0.6 * peel, 0, 0.2)
    shoot(S, (0, 0, 0), (hp[0] + lerp(1.5, 1.2, k), hp[1] - lerp(1.5, 1.2, k), hp[2] + lerp(0.5, 0.4, k)), (hp[0], hp[1], hp[2] + 0.15), 36)


def rook_feather(S, k, t, lt):
    """Rook tries his own fix: he plucks a feather and holds it over the hole; the escaping air blows it straight off."""
    ocean(S, 'hot', t, 0.4)
    r = raft_at(S, t, 0, 0, 0.0, sink=0.1, tilt=0.6)
    S['tubes'][0].scale = (1, 1, 0.6)
    S['hole'].hide_render = False
    aboard(S, S['rook'], 0.5, -0.85, 0.04, 0.3, P('sit', aR=(1.2, -0.1, 0.4), lean=0.5, head=(0.5, 0.2)), 'calm' if lt < 0.5 else 'low')
    hp = wpos(r, (0, -1.47, 0.2))
    off = sm((lt - 0.45) / 0.5)
    S['rfea'].location = (hp[0] + 0.3 * off, hp[1] - 0.1 - 0.9 * off, hp[2] + 1.2 * off)
    S['rfea'].rotation_euler = (1.4 + 4 * off, 2 * off, 0.3)
    S['hat_tip'] = 0.5 * off
    h = head(S, S['rook'])
    key(S, SEA, (h[0] - 1, h[1] - 4, h[2] + 2), h, 700, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] - lerp(1.9, 1.6, k), h[1] - lerp(3.2, 2.8, k), h[2] - 0.5), ((h[0] + hp[0]) / 2, (h[1] + hp[1]) / 2, (h[2] + hp[2]) / 2 + 0.2), 28)


def fork_fix(S, k, t, lt):
    """Close: his hands push a fork through the rubber around the hole and fold it shut. The bubbling stops."""
    ocean(S, 'hot', t, 0.4)
    r = raft_at(S, t, 0, 0, 0.0, sink=0.1, tilt=0.6)
    S['tubes'][0].scale = (1, 1, 0.6)
    m = aboard(S, S['man'], 0.0, -0.6, 0.04, 0.0, P('sit', aR=(1.25, 0.05, 0.4), aL=(1.25, 0.05, 0.4), lean=0.9, head=(0.8, 0.0)), 'hard')
    hp = wpos(r, (0, -1.47, 0.2))
    push = sm(lt / 0.5)
    fold = sm((lt - 0.5) / 0.4)
    S['hole'].hide_render = fold > 0.7
    S['hole'].scale = (0.34, 0.06, 0.13 * (1 - fold))
    S['fork'].location = (hp[0], hp[1] - 0.25 + 0.2 * push, hp[2] + 0.1 - 0.05 * fold)
    S['fork'].rotation_euler = (lerp(-0.9, 0.0, push) + 1.3 * fold, 0, 0.15)
    shoot(S, (0, 0, 0), (hp[0] - lerp(0.35, 0.25, k), hp[1] - lerp(1.1, 0.85, k), hp[2] + lerp(0.35, 0.28, k)), (hp[0], hp[1] - 0.1, hp[2] + 0.08), 40)


# ---------------------------------------------------------------- weeks
def thin_man(S, k, t, lt):
    """Weeks later under a white sun: he sits hunched and thin, his beard long; Rook
    sits beside him with his hat off, quiet."""
    ocean(S, 'hot', t, 0.35)
    raft_at(S, t, 0, 0, 0.4)
    m = aboard(S, S['man'], -0.35, 0.3, 0.04, 0.3, P('sit', head=(0.45, 0.1), lean=0.4), 'tired')
    thin(S, 1.0)
    aboard(S, S['rook'], 0.65, -0.1, 0.04, -0.4, P('sit', aL=(1.2, 0.3, 1.2 + 0.4 * math.sin(lt * 9), 0.3), head=(0.2, 0.5)), 'sad')
    S['hat_off'] = 1.0
    h = head(S, m)
    key(S, SEA, (h[0] - 2, h[1] - 4, h[2] + 3), h, 500, 'FFF8E8')
    shoot(S, (0, 0, 0), (h[0] + lerp(0.8, 0.6, k), h[1] - lerp(4.6, 4.0, k), h[2] + 0.3), (h[0] + 0.5, h[1], h[2] - 0.5), 30)


def night_lights(S, k, t, lt):
    """Night, day 75: from behind him in the raft, a low dark island on the horizon with a string of lights. He pulls
    himself up on the arch to look."""
    ocean(S, 'night', t, 0.5)
    raft_at(S, t, 0, 0, PI)
    S['island'].location = at(SEA, 0, 420, 0)
    for i, o in enumerate(S['lights']):
        o.scale = (1, 1, 1) if (t * 2 + i) % 3 > 0.3 else (0.6, 0.6, 0.6)
    u = sm(lt / 0.8)
    aboard(S, S['man'], 0.0, 0.2, 0.04, PI + PI, blend(P('sit', head=(0.3, 0.0)), P('stand', aR=(2.4, 0.3, 0.6), head=(-0.1, 0.0), lean=0.1), u), 'wide')
    thin(S, 1.0)
    h = head(S, S['man'])
    key(S, SEA, (h[0] + 2, h[1] - 2, h[2] + 2), h, 260, 'A8C0F0')
    shoot(S, (0, 0, 0), (h[0] + 0.9, h[1] - lerp(4.0, 3.4, k), h[2] + 0.4), (h[0] - 0.8, h[1] + 20, h[2] + 0.2), 30)


def rook_lights(S, k, t, lt):
    """Rook on the canopy at night, the island's lights in his eyes: he lifts the brim of his hat with one finger."""
    ocean(S, 'night', t, 0.5)
    raft_at(S, t, 0, 0, PI)
    S['island'].location = at(SEA, 0, 420, 0)
    lift = sm(lt / 0.6)
    aboard(S, S['rook'], 0.0, 0.5, 2.1, PI + PI, P('hat', head=(-0.1, 0.0)) if lift < 0.9 else P('stand', head=(-0.1, 0.0)), 'shocked' if lift > 0.6 else 'low')
    S['hat_tip'] = lerp(0.6, -0.4, lift)
    h = head(S, S['rook'])
    key(S, SEA, (h[0], h[1] + 4, h[2] + 1), h, 500, 'FFD890')
    shoot(S, (0, 0, 0), (h[0] - lerp(0.9, 0.7, k), h[1] + lerp(3.4, 2.8, k), h[2] - 0.3), (h[0], h[1], h[2] - 0.15), 34)


# ---------------------------------------------------------------- found
def birds_circle(S, k, t, lt):
    """Morning, from high above: dark frigate birds wheel in a ring over the little raft; under the surface around it
    the gold flashes of the school."""
    ocean(S, 'morning', t, 0.5)
    raft_at(S, t, 0, 0, 0.4)
    aboard(S, S['man'], 0.0, 0.3, 0.04, PI, P('sit', head=(-0.3, 0.0)), 'tired')
    thin(S, 1.0)
    birds(S, t, 0, 0, 7.5, 6.0)
    for i, (f, tail, body) in enumerate(S['fish'][:8]):
        a = t * 0.4 + 2 * PI * i / 8
        f.location = at(SEA, 3.0 * math.cos(a), 3.0 * math.sin(a), wave_at(S, 3.0 * math.cos(a), 3.0 * math.sin(a), t) - 0.08)
        f.rotation_euler = (0, 0, a + PI / 2)
        tail.rotation_euler = (0, 0, 0.4 * math.sin(t * 9 + i))
    shoot(S, SEA, (lerp(5, 4, k), lerp(-14, -12, k), lerp(22, 19, k)), (0, 0, 2.5), 28)


def fishing_boat(S, k, t, lt):
    """Low on the water: a small blue and yellow fishing boat with three men turns towards the circling birds."""
    ocean(S, 'morning', t, 0.5)
    raft_at(S, t, 0, 0, 0.4)
    birds(S, t, 0, 0, 7.5, 6.0)
    fb = S['fboat']
    bx, by = lerp(16, 11, k), lerp(26, 18, k)
    ride(S, fb, t, bx, by, lerp(2.2, 2.6, k), 0.1, 0.8)
    for i, rg in enumerate(S['fishers']):
        aboard(S, rg, 0.0, -1.8 + 1.8 * i, 0.55, PI if i < 2 else 0.0, P('point', head=(-0.2, 0.0)) if i == 1 else P('stand', aR=(0.6, 0.3, 0.8)), 'hard', par=fb)
    key(S, SEA, (bx - 6, by - 10, 6), (bx, by, 2), 800, 'FFE4C0')
    shoot(S, SEA, (lerp(3.5, 4.5, k), lerp(4, 5, k), 1.6), (lerp(10, 8, k), 16, 2.0), 45)


def boat_reach(S, k, t, lt):
    """Alongside: the fishermen lean over and take him by the arms, lifting him out of the raft. Rook steadies the raft
    with both hands, hat off."""
    ocean(S, 'morning', t, 0.4)
    raft_at(S, t, 0, 0, 0.0)
    fb = S['fboat']
    ride(S, fb, t, 0, 3.6, PI / 2, 0.1, 0.8)
    up = sm((lt - 0.3) / 1.2)
    m = aboard(S, S['man'], 0.0, lerp(0.6, 1.4, up), lerp(0.04, 0.9, up), 0.0 + PI, P('stand', aL=(2.0, 0.4, 0.3), aR=(2.0, 0.4, 0.3), head=(-0.2, 0.0)), 'wide')
    thin(S, 1.0)
    for i, rg in enumerate(S['fishers'][:2]):
        aboard(S, rg, -0.6, -0.6 + 1.2 * i, 0.55, -PI / 2, P('reach', aR=(1.9, 0.1, 0.4), aL=(1.6, 0.2, 0.4), lean=0.55, head=(0.5, 0.0)), 'warm', par=fb)
    aboard(S, S['rook'], 0.9, -0.8, 0.66, 0.3, P('stand', aL=(1.0, 0.2, 0.6), aR=(1.0, 0.2, 0.6), lean=0.3, head=(-0.1, 0.0)), 'soft')
    S['hat_off'] = 1.0
    h = head(S, m)
    key(S, SEA, (h[0] - 3, h[1] - 4, h[2] + 2), h, 800, 'FFE4C0')
    shoot(S, (0, 0, 0), (h[0] + lerp(5.0, 4.4, k), h[1] - lerp(2.4, 1.8, k), h[2] + 0.2), (h[0], h[1] + 0.6, h[2] - 0.5), 28)


def rook_point(S, k, t, lt):
    """Rook alone on the canopy, under the circling birds: he points up at the birds, then straight down at the fish
    under the raft, and nods."""
    ocean(S, 'morning', t, 0.4)
    raft_at(S, t, 0, 0, 0.3)
    birds(S, t, 0, 0, 11.0, 6.0)
    for i, (f, tail, body) in enumerate(S['fish'][:6]):
        a = t * 0.5 + 2 * PI * i / 6
        f.location = at(SEA, 2.4 * math.cos(a), 2.4 * math.sin(a), wave_at(S, 2.4 * math.cos(a), 2.4 * math.sin(a), t) - 0.08)
        f.rotation_euler = (0, 0, a + PI / 2)
    dn = sm((lt - 0.55) / 0.3)
    aboard(S, S['rook'], 0.0, 0.5, 2.1, 0.3, P('point', aR=(lerp(2.6, 0.6, dn), 0.1, 0.05), head=(lerp(-0.45, 0.4, dn), 0.0)), 'calm' if dn < 0.5 else 'soft')
    h = head(S, S['rook'])
    key(S, SEA, (h[0] - 2, h[1] - 4, h[2] + 2), h, 900, 'FFE4C0')
    shoot(S, (0, 0, 0), (h[0] + lerp(2.0, 1.6, k), h[1] - lerp(5.6, 4.8, k), h[2] - lerp(1.0, 0.8, k)), (h[0], h[1], h[2] - 0.4), 24)


def fish_hull(S, k, t, lt):
    """Underwater: the empty raft above, the fishing boat's hull sliding in beside it, and the school still circling,
    gold in the light."""
    sky(S, 'under')
    usurf(S, t)
    S['ubelly'].location = at(UNDER, 0, 0, -0.05)
    S['uhull'].location = at(UNDER, lerp(4.0, 3.0, k), lerp(-1.5, -0.5, k), 0.0)
    S['uhull'].rotation_euler = (0, 0, 0.2)
    school(S, t, 0.8, -0.2, -0.8, 1.2)
    shoot(S, UNDER, (lerp(-3.5, -2.6, k), lerp(-8.5, -7.5, k), lerp(-6.0, -5.4, k)), (1.0, 0, -1.2), 24)


# ---------------------------------------------------------------- the end
def rook_question(S, k, t, lt):
    """Sunset, the empty raft drifting: Rook sits on its tube, a fork from the case in his hand, and asks us straight out."""
    ocean(S, 'dusk', t, 0.4)
    raft_at(S, t, 0, 0, 0.3)
    aboard(S, S['rook'], 0.6, -1.0, 0.66, 0.2, P('sit', aR=(1.0, 0.1, 1.3), head=(0.0, 0.0)), 'calm')
    hd = wpos(S['rook'].hands[1])
    S['fork'].location, S['fork'].rotation_euler = (hd[0], hd[1] - 0.1, hd[2] + 0.15), (0, 0.4, 0)
    h = head(S, S['rook'])
    key(S, SEA, (h[0] + 2, h[1] - 5, h[2] + 2), h, 900, 'FFB080')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.1, 0.9, k), h[1] - lerp(3.4, 3.0, k), h[2] - 0.2), (h[0], h[1], h[2] - 0.3), 38)


def signoff(S, k, t, lt):
    """Wide at sunset: the little raft and its orange canopy on a gold sea, Rook on top tipping his hat, then pocketing
    the fork."""
    ocean(S, 'dusk', t, 0.5)
    raft_at(S, t, 0, 0, 0.6)
    aboard(S, S['rook'], 0.0, 0.5, 2.1, 0.4, P('hat') if lt < 0.7 else P('stand', aR=(0.2, 0.1, 0.4)), 'soft')
    S['hat_tip'] = 0.4
    key(S, SEA, (4, -8, 5), (0, 0.5, 3), 900, 'FFB080')
    shoot(S, SEA, (lerp(5, 6, k), lerp(-11, -12, k), lerp(2.2, 2.8, k)), (0, 0.5, 3.0), 30)


SHOTS3D = {f.__name__: f for f in (
    cabin_flood, boat_sink, raft_jump, raft_alone, rook_raft, dawn_wide, still_close, rook_still, under_fish, spear_aim,
    fish_catch, ship_pass, rook_wave, spear_hole, raft_soft, rook_sink, patch_fail, rook_feather, fork_fix, thin_man,
    night_lights, rook_lights, birds_circle, fishing_boat, boat_reach, rook_point, fish_hull, rook_question, signoff)}


# ================================================================ long-form extension (16:9 full case file)
# The Short's sea, raft, sloop, cabin, freighter, island, birds, fishing boat and underwater set stay exactly as they were.
# New for the full case, each built at its own origin far from the Short's sets: a boat shed where he builds the sloop,
# a study where the book is written, a film studio's water tank, and an evening jetty on the island. New props on the
# open sea: sails for the sloop, a volcanic island at dusk, the moon, a ship's lights at night, a flare and its pistol,
# the emergency bag, the kit (water tins, food, flares, a radio beacon, a sleeping bag, a cushion), three pencils lashed
# into a sextant, a log book, a mess tin and its fork, a hand pump, barnacles and triggerfish under the raft, and a
# hammerhead. New figures: Callahan in later life and two film-crew members. All of it is generic: no lettering, logos,
# flags or markings anywhere, no place is modelled on the real one and nobody's likeness is attempted. Nothing from any
# film appears: the studio tank is a plain tank with the story's own raft in it.
# Building with bpy.ops gets slower with every object already in the scene, so the same primitives are made by copying
# one prototype mesh per shape (identical geometry, materials and bevels, a fraction of the time).
from mathutils import Matrix  # noqa: E402

_PROTO, _LAST = {}, [None]


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
    key_ = (kind, tuple(sorted(kw.items())))
    if key_ not in _PROTO:
        getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=(0, 0, 0), **kw)
        o = bpy.context.object
        _PROTO[key_] = o.data
        bpy.data.objects.remove(o)
    me = _PROTO[key_].copy()
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


K.add, K.empty = add, empty


def tri(par, col, pts, rough=0.9, emit=0.0, alpha=1.0):
    """One flat polygon from its corner points (sails)."""
    me = bpy.data.meshes.new('tri')
    me.from_pydata([tuple(p) for p in pts], [], [list(range(len(pts)))])
    me.materials.append(K.mat(col, rough, emit, alpha))
    o = bpy.data.objects.new('tri', me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = par
    return o


SHED = (-5000.0, 0.0, 0.0)          # the boat shed
DESK = (0.0, -5000.0, 0.0)          # the study
TANK = (-5000.0, -5000.0, 0.0)      # the film studio's tank
JETTY = (5000.0, -5000.0, 0.0)      # the island's jetty at evening
SKIES.update(
    shed=('F2E2C0', 'A8C8E0', 1.3, 2.0, 'FFF0D8', (0.3, -0.6, 0.75), '1A6A8E'),
    study=('2A3A50', '101820', 0.4, 0.0, 'FFFFFF', (0, 0, 1), '1A6A8E'),
    studio=('0A0C10', '040506', 0.1, 0.0, 'FFFFFF', (0, 0, 1), '1A6A8E'),
    harbour=('F09A6A', '34407A', 1.1, 2.2, 'FFB080', (-0.8, 0.5, 0.2), '24486A'),
    sail=('CFE8F6', '3A86C8', 1.3, 3.8, 'FFF6E4', (0.5, -0.6, 0.7), '1E72A0'),
    rainy=('8A96A4', '4A5462', 0.9, 1.0, 'D8E0EA', (0.2, -0.3, 0.9), '35505E'),
    moon=('1E3050', '060A16', 0.65, 1.1, 'B8CCF4', (-0.5, 0.6, 0.6), '0E2438'))
PARKED = {'shed', 'study', 'studio', 'harbour'}
_sky0 = sky


def sky(S, a, b=None, k=0.0, rough=0.6, t=0.0):
    """As the Short's sky, but the new indoor and harbour sets park the open sea as the cabin does."""
    if a not in PARKED:
        return _sky0(S, a, b, k, rough, t)
    _sky0(S, 'cabin')
    A = SKIES[a]
    S['skymix'].inputs[6].default_value = K.hexc(A[0])
    S['skymix'].inputs[7].default_value = K.hexc(A[1])
    S['bg'].inputs[1].default_value = A[2]
    S['sun'].data.energy = A[3]
    S['sun'].data.color = K.hexc(A[4])[:3]
    S['sun'].location = tuple(v * 500 for v in A[5])


CAMFILL.update(night_alone=120, rook_deck=300, shed_build=160, sail_calm=120, canary_leave=160, deck_swamped=260, rook_hatch=380,
               dive_cabin=140, rook_ducky=220, kit_spread=160, still_open=200, rain_catch=220, reef_under=40, school_follow=160,
               gun_snap=140, shark_under=40, raft_bump=220, flare_night=200, pump_night=420, fork_find=180, pencil_sextant=320,
               sun_beat=60, jetty_eve=200, desk_book=160, film_tank=200, thumbshot=160)
HOST |= {'rook_deck', 'shed_build', 'sail_calm', 'deck_swamped', 'rook_hatch', 'rook_ducky', 'kit_spread', 'still_open', 'rain_catch',
         'school_follow', 'raft_bump', 'pump_night', 'fork_find', 'pencil_sextant', 'jetty_eve', 'desk_book'}
OLD_SKIN, OLD_HAIR = 'C8906C', 'B8B4AC'


def older_head(head):
    d = K.human_head(OLD_SKIN, OLD_HAIR)(head)
    d['beard'] = add('ico_sphere', OLD_HAIR, (0, -0.12, -0.17), scale=(0.88, 0.66, 0.42), radius=0.27, subdivisions=1, parent=head)
    return d


def make_props(S):
    # sails for the sloop (parented to it in the sailing shots)
    sl = S['sails'] = keep(empty(FAR))
    tri(sl, 'F4F0E6', [(0, 0.55, 1.95), (0, 0.55, 9.6), (0, -2.9, 1.95)], rough=1.0)
    tri(sl, 'ECE6D8', [(0, 0.75, 1.3), (0, 0.75, 8.8), (0, 3.75, 1.0)], rough=1.0)
    tri(sl, 'FF7A1A', [(0.02, 0.56, 9.0), (0.02, 0.56, 9.6), (0.02, 0.2, 9.0)], rough=1.0)                   # a little pennant
    # a volcanic island at dusk with a few white houses
    cn = S['canary'] = keep(empty(FAR))
    add('cone', '4A3A34', (0, 0, 30), radius1=170, radius2=24, depth=60, vertices=11, parent=cn, rough=1.0)
    add('cone', '5A463C', (70, -40, 18), radius1=90, radius2=10, depth=36, vertices=9, parent=cn, rough=1.0)
    add('cone', '6A8A4A', (-40, -60, 6), radius1=80, radius2=50, depth=12, vertices=9, parent=cn, rough=1.0)
    for i in range(14):
        a = -2.0 + 1.6 * rnd(i, 21)
        r_ = 105 + 30 * rnd(i, 22)
        add('cube', ('F4EEE2', 'E8DCC8')[i % 2], (r_ * math.cos(a), r_ * math.sin(a), 4 + 6 * rnd(i, 23)), scale=(6, 5, 4), size=1, parent=cn)
        if i % 3 == 0:
            add('ico_sphere', 'FFD890', (r_ * math.cos(a) * 0.99, r_ * math.sin(a) * 0.99, 4 + 6 * rnd(i, 23)), radius=1.0, subdivisions=1, parent=cn, emit=8.0)
    S['moon'] = keep(add('ico_sphere', 'F4F0DC', FAR, radius=26, subdivisions=2, emit=6.0))
    S['star'] = keep(add('ico_sphere', 'FFFFFF', FAR, radius=5, subdivisions=1, emit=30.0))
    # a ship at night: only its lights and a dark shape
    sn = S['shipnight'] = keep(empty(FAR))
    add('cube', '0C0E14', (0, 0, 2), scale=(70, 8, 5), size=1, parent=sn)
    add('cube', '0C0E14', (-26, 0, 8), scale=(8, 7, 8), size=1, parent=sn)
    for x, z, c in ((-30, 16, 'FFFFFF'), (20, 12, 'FFFFFF'), (34, 4, '40FF60'), (-26, 9, 'FFE0A0'), (-22, 9, 'FFE0A0'), (-18, 9, 'FFE0A0')):
        add('ico_sphere', c, (x, -4.2, z), radius=0.9, subdivisions=1, parent=sn, emit=40.0)
    # the flare and its pistol
    S['flare'] = keep(add('ico_sphere', 'FF4A2A', FAR, radius=0.6, subdivisions=2, emit=80.0))
    S['flarel'] = light(FAR, 0, 'FF5A3A', size=1.0)
    S['trail'] = [keep(add('ico_sphere', 'FFB080', FAR, radius=0.09, subdivisions=1, emit=12.0)) for _ in range(8)]
    pi_ = S['pistol'] = keep(empty(FAR))
    add('cube', 'FF7A1A', (0, 0, 0), scale=(0.1, 0.36, 0.12), size=1, parent=pi_)
    add('cylinder', 'FF7A1A', (0, -0.3, 0.02), rot=(PI / 2, 0, 0), radius=0.07, depth=0.36, vertices=8, parent=pi_)
    add('cube', '2A2A30', (0, 0.12, -0.14), rot=(0.3, 0, 0), scale=(0.08, 0.1, 0.22), size=1, parent=pi_)
    # the kit
    eb = S['ebag'] = keep(empty(FAR))
    add('cylinder', 'F2B030', (0, 0, 0), rot=(0, PI / 2, 0), radius=0.26, depth=0.9, vertices=8, parent=eb, rough=0.8)
    add('torus', '2A2A30', (0, 0, 0.2), rot=(PI / 2, 0, PI / 2), major_radius=0.18, minor_radius=0.025, major_segments=10, minor_segments=3, parent=eb)
    for x in (-0.3, 0.3):
        add('cylinder', 'D08A20', (x, 0, 0), rot=(0, PI / 2, 0), radius=0.27, depth=0.05, vertices=8, parent=eb)
    S['tins'] = [keep(add('cylinder', ('B8BCC4', 'A8AEB8', 'C4C8D0')[i], FAR, radius=0.13, depth=0.3, vertices=10, rough=0.3)) for i in range(3)]
    S['food'] = keep(add('cube', 'C8A060', FAR, scale=(0.36, 0.24, 0.12), size=1, rough=0.8))
    fl = S['flares'] = keep(empty(FAR))
    for i in range(3):
        add('cylinder', 'D8322A', (0.11 * i, 0, 0), rot=(PI / 2, 0, 0.2), radius=0.04, depth=0.4, vertices=6, parent=fl, rough=0.6)
    bc = S['beacon'] = keep(empty(FAR))
    add('cube', 'F2C832', (0, 0, 0.18), scale=(0.2, 0.14, 0.36), size=1, parent=bc, rough=0.5)
    add('cylinder', '2A2A30', (0, 0, 0.66), radius=0.012, depth=0.6, vertices=4, parent=bc)
    S['blink'] = add('ico_sphere', 'FF3A2A', (0, 0, 0.4), radius=0.045, subdivisions=1, parent=bc, emit=0.0)
    S['sbag'] = keep(add('cylinder', '3A5A9A', FAR, rot=(0, PI / 2, 0), radius=0.22, depth=0.95, vertices=8, rough=1.0))
    S['cushion'] = keep(add('cube', '8A3A3A', FAR, scale=(0.5, 0.5, 0.1), size=1, rough=1.0))
    pc = S['pencils'] = keep(empty(FAR))
    for i, (a, b) in enumerate((((-0.2, 0, 0), (0.2, 0, 0)), ((-0.2, 0, 0), (0.0, 0, 0.36)), ((0.2, 0, 0), (0.0, 0, 0.36)))):
        bar(pc, 'F2C030', (a[0] - 0.04 * (b[0] - a[0]), a[1], a[2] - 0.04 * (b[2] - a[2])), (b[0] + 0.04 * (b[0] - a[0]), b[1], b[2] + 0.04 * (b[2] - a[2])), 0.016, rough=0.6)
    for p in ((-0.2, 0, 0), (0.2, 0, 0), (0.0, 0, 0.36)):
        add('ico_sphere', 'E8E2D0', p, radius=0.03, subdivisions=1, parent=pc)
    S['logbook'] = keep(add('cube', 'EDE6D0', FAR, scale=(0.2, 0.28, 0.03), size=1, rough=1.0))
    mt = S['mess'] = keep(empty(FAR))
    add('cylinder', '9AA0A8', (0, 0, 0.04), radius=0.2, depth=0.08, vertices=10, parent=mt, rough=0.3)
    add('cylinder', '7A8088', (0.26, 0, 0.06), radius=0.17, depth=0.04, vertices=10, parent=mt, rough=0.3)
    pm = S['pump'] = keep(empty(FAR))
    add('cylinder', '2A4A7A', (0, 0, 0.25), radius=0.08, depth=0.5, vertices=8, parent=pm, rough=0.5)
    S['pumprod'] = add('cylinder', 'B8BCC4', (0, 0, 0.6), radius=0.02, depth=0.4, vertices=6, parent=pm, rough=0.3)
    S['pumphandle'] = add('cube', '2A2A30', (0, 0, 0.82), scale=(0.3, 0.05, 0.05), size=1, parent=pm)
    add('cylinder', '1A1A1E', (0.2, -0.1, 0.05), rot=(0, PI / 2, -0.4), radius=0.02, depth=0.6, vertices=6, parent=pm)
    S['rdrops'] = [keep(add('ico_sphere', '9ADCFF', FAR, radius=0.03, subdivisions=1, rough=0.05, emit=0.4)) for _ in range(10)]
    S['cord'] = keep(add('torus', 'E8E2C8', FAR, major_radius=0.06, minor_radius=0.015, major_segments=10, minor_segments=3))
    # barnacles on the raft's belly (grown in by scale), triggerfish, a hammerhead
    S['barn'] = []
    for i in range(30):
        a = 2 * PI * rnd(i, 31)
        r_ = 1.25 * math.sqrt(rnd(i, 32))
        S['barn'].append(add('cone', ('D8D0C0', 'C8BCA8', 'E8E0D0')[i % 3], (r_ * math.cos(a), r_ * math.sin(a), -0.12), rot=(PI, 0, 0),
                             radius1=0.11 + 0.05 * rnd(i, 33), radius2=0.03, depth=0.17, vertices=6, parent=S['ubelly'], rough=0.9))
    S['trig'] = []
    for i in range(5):
        f = keep(empty(FAR))
        add('ico_sphere', ('6A7A8A', '5A6A7C', '7A8898')[i % 3], (0, 0, 0), scale=(0.18, 0.5, 0.5), radius=0.6, subdivisions=1, parent=f, rough=0.4)
        add('cone', '4A5A6A', (0, -0.42, 0), rot=(PI / 2, 0, 0), scale=(0.15, 1, 1.4), radius1=0.18, radius2=0.0, depth=0.24, vertices=4, parent=f)
        for s_ in (-1, 1):
            add('cube', '0E0E14', (s_ * 0.1, 0.18, 0.08), scale=(0.02, 0.06, 0.06), size=1, parent=f)
        S['trig'].append(f)
    sk = S['shark'] = keep(empty(FAR))
    add('ico_sphere', '6E7C88', (0, 0, 0), scale=(0.55, 2.6, 0.55), radius=1.0, subdivisions=2, parent=sk, rough=0.5)
    add('ico_sphere', 'C8CCD0', (0, 0.1, -0.2), scale=(0.45, 2.2, 0.3), radius=1.0, subdivisions=1, parent=sk, rough=0.5)
    add('cube', '6E7C88', (0, 2.55, 0.05), scale=(2.2, 0.36, 0.16), size=1, parent=sk, rough=0.5)              # the hammer
    for s_ in (-1, 1):
        add('ico_sphere', '0A0A0E', (s_ * 1.1, 2.6, 0.08), radius=0.09, subdivisions=1, parent=sk)
        add('cube', '5E6C78', (s_ * 0.8, 0.6, -0.15), rot=(0, s_ * 0.3, s_ * -0.5), scale=(1.1, 0.5, 0.06), size=1, parent=sk)
    add('cone', '5E6C78', (0, 0.2, 0.75), rot=(-0.4, 0, 0), radius1=0.45, radius2=0.0, depth=1.0, vertices=3, parent=sk)
    S['stail'] = st = empty((0, -2.4, 0), sk)
    add('cone', '5E6C78', (0, -0.5, 0.25), rot=(PI / 2 + 0.6, 0, 0), scale=(0.12, 1, 1), radius1=0.5, radius2=0.0, depth=1.1, vertices=3, parent=st)
    add('cone', '5E6C78', (0, -0.3, -0.2), rot=(PI / 2 - 0.5, 0, 0), scale=(0.12, 1, 1), radius1=0.3, radius2=0.0, depth=0.6, vertices=3, parent=st)


def make_shed(S):
    """A timber boat shed by day: big doors open on a bright yard, a bare white hull on a cradle, a bench, sawhorses."""
    c = empty(SHED)
    box(c, '8A7458', -8, 8, -6, 10, -0.1, 0.0)                                                                    # floor
    for i in range(16):                                                                                           # plank walls
        box(c, ('6A5038', '5E4632')[i % 2], -8.2 + i, -7.2 + i, 9.8, 10.2, 0, 7.5)
    for s_ in (-1, 1):
        for i in range(16):
            box(c, ('6A5038', '5E4632')[i % 2], s_ * 8 - 0.2, s_ * 8 + 0.2, -6 + i, -5 + i, 0, 7.5)
        box(c, '4A3828', s_ * 3.4 - 0.25, s_ * 3.4 + 0.25, -6.2, -5.8, 0, 7.5)                                      # door posts
        box(c, '6A5038', min(s_ * 3.6, s_ * 8.2), max(s_ * 3.6, s_ * 8.2), -6.2, -5.8, 0, 7.5)                    # front wall beside the doors
    box(c, '4A3828', -8, 8, -6.3, -5.7, 6.0, 7.5)                                                                 # lintel
    for i in range(6):                                                                                            # roof beams
        box(c, '4A3828', -8, 8, -5 + 3 * i, -4.7 + 3 * i, 7.0, 7.3)
    add('plane', 'D8D2B8', (0, -24, 0), size=60, parent=c, rough=1.0)                                             # the sunlit yard
    for i in range(5):
        add('cone', '4A7A3A', (-10 + 5 * i, -18 - 3 * rnd(i, 41), 3), radius1=1.6, radius2=0, depth=6, vertices=7, parent=c)
    # the bare hull on its cradle: white, no mast yet
    h_ = S['hull2'] = empty((0.0, 3.0, 0.9), c)
    add('cube', 'F0ECE2', (0, 0, 0.4), scale=(2.2, 6.4, 1.2), size=1, parent=h_)
    add('cube', 'F0ECE2', (0, 3.6, 0.5), rot=(0, 0, PI / 4), scale=(1.56, 1.56, 1.0), size=1, parent=h_)
    add('cube', '2A4A7A', (0, 0.4, -0.05), scale=(2.24, 7.6, 0.18), size=1, parent=h_)
    add('cube', 'C8BEA8', (0, -0.8, 1.25), scale=(1.5, 2.6, 0.5), size=1, parent=h_)
    for y in (-2.0, 0.5, 3.0):                                                                                    # cradle
        box(c, '7A5A3A', -1.4, 1.4, 2.9 + y, 3.1 + y, 0, 0.5)
    box(c, '7A5A3A', -1.8, 1.8, -3.0, -1.6, 0, 1.0)                                                               # workbench
    box(c, '5A4028', -1.8, 1.8, -3.0, -1.6, 1.0, 1.12)
    for i in range(5):
        add('cube', ('C8322A', '2A6A9A', 'D8A830', '8A8A90', 'E8E2D4')[i], (-1.4 + 0.6 * i, -2.3, 1.22), scale=(0.3, 0.2, 0.18), size=1, parent=c)
    for x in (2.8, 4.2):                                                                                          # sawhorse
        bar(c, '9A7A52', (x, 3.5, 0.0), (x, 3.9, 1.0), 0.06)
        bar(c, '9A7A52', (x, 4.3, 0.0), (x, 3.9, 1.0), 0.06)
    box(c, '9A7A52', 2.6, 4.4, 3.82, 3.98, 1.0, 1.1)
    add('cube', 'D8C8A8', (3.5, 3.9, 1.16), scale=(1.4, 0.12, 0.05), size=1, parent=c)                            # a plank on it
    S['plane'] = keep(add('cube', 'B87A3A', FAR, scale=(0.14, 0.32, 0.12), size=1))                               # his hand plane
    S['shavings'] = [keep(add('cube', 'F0D8A8', FAR, scale=(0.08, 0.02, 0.04), size=1, rough=1.0)) for _ in range(8)]
    S['shedl'] = [light(at(SHED, 0, -12, 6), 0, 'FFF0D8', size=8.0), light(at(SHED, -4, 6, 6.5), 0, 'FFE0B0', size=3.0)]
    S['shedl'][0].rotation_euler = (1.1, 0, 0)


def make_desk(S):
    """A study: a desk by a window on the sea, a typewriter, stacks of typed pages, a lamp, shelves."""
    c = empty(DESK)
    box(c, '5A4636', -5, 5, -3, 5, -0.1, 0.0)
    box(c, '3A4A5A', -5, 5, 3.9, 4.1, 0, 5)                                                                       # back wall
    box(c, '34424F', -5.1, -4.9, -3, 5, 0, 5)
    box(c, '34424F', 4.9, 5.1, -3, 5, 0, 5)
    box(c, '9AB8D0', -1.6, 1.6, 3.85, 3.95, 1.6, 3.8, emit=1.6)                                                   # window on the sea
    box(c, '2A3440', -1.7, 1.7, 3.8, 3.9, 2.66, 2.74)
    box(c, '2A3440', -0.04, 0.04, 3.8, 3.9, 1.5, 3.9)
    box(c, '7A5638', -1.6, 1.6, 1.6, 2.6, 1.0, 1.12)                                                              # desk top
    for x in (-1.5, 1.5):
        box(c, '6A4A30', x - 0.08, x + 0.08, 1.7, 2.5, 0, 1.0)
    tw = empty((0, 2.0, 1.12), c)                                                                                 # typewriter
    add('cube', '2A2E34', (0, 0, 0.12), scale=(0.9, 0.6, 0.24), size=1, parent=tw, rough=0.4)
    add('cube', '2A2E34', (0, 0.22, 0.3), scale=(1.1, 0.16, 0.16), size=1, parent=tw, rough=0.4)
    add('cube', 'F4F0E4', (0, 0.26, 0.5), rot=(-0.2, 0, 0), scale=(0.5, 0.02, 0.5), size=1, parent=tw, rough=1.0)
    for i in range(3):
        add('cube', 'E8E2CC', (-1.1 + 0.05 * i, 1.9, 1.15 + 0.08 * i), rot=(0, 0, 0.1 * i), scale=(0.5, 0.66, 0.08), size=1, parent=c, rough=1.0)
    add('cube', 'F2EEE0', (1.1, 1.9, 1.24), scale=(0.5, 0.66, 0.24), size=1, parent=c, rough=1.0)
    add('cylinder', '2A2A30', (1.3, 2.4, 1.6), radius=0.02, depth=0.9, vertices=4, parent=c)
    add('cone', 'FF7A1A', (1.3, 2.3, 2.0), rot=(0.5, 0, 0), radius1=0.22, radius2=0.08, depth=0.24, vertices=8, parent=c)
    for i in range(4):                                                                                            # shelves of books
        box(c, '6A4A30', -4.8, -4.3, -1 + 0, 3, 0.8 + 0.9 * i, 0.86 + 0.9 * i)
        for j in range(7):
            add('cube', ('8A3A3A', '3A5A8A', 'C8A040', '4A7A4A')[(i + j) % 4], (-4.55, -0.7 + 0.5 * j + 0.1 * rnd(i, j), 1.1 + 0.9 * i),
                scale=(0.4, 0.14, 0.5), size=1, parent=c)
    box(c, '7A5638', -0.5, 0.5, 0.7, 1.1, 0, 0.7)                                                                 # chair
    S['book'] = keep(empty(FAR))                                                                                  # the finished book, plain cover
    add('cube', 'E8E0C8', (0, 0, 0), scale=(0.34, 0.5, 0.08), size=1, parent=S['book'], rough=1.0)
    add('cube', 'FF7A1A', (0, 0, 0.042), scale=(0.34, 0.5, 0.002), size=1, parent=S['book'], rough=1.0)
    S['deskl'] = [light(at(DESK, 1.3, 2.2, 2.2), 0, 'FFC890', size=0.5), light(at(DESK, 0, 3.6, 3), 0, 'A8C8F0', size=3.0)]


def make_tank(S):
    """A dark film studio: a big tank of lit blue water with the story's raft in it, lamps on stands, a camera on legs."""
    c = empty(TANK)
    box(c, '1A1C22', -14, 14, -10, 14, -0.1, 0.0)
    box(c, '14161C', -14, 14, 13.8, 14.2, 0, 10)
    for s_ in (-1, 1):
        box(c, '2A3038', s_ * 6 - 0.25, s_ * 6 + 0.25, -1, 9, 0, 1.6)                                               # tank walls
    box(c, '2A3038', -6.25, 6.25, 8.75, 9.25, 0, 1.6)
    box(c, '2A3038', -6.25, 6.25, -1.25, -0.75, 0, 1.6)
    S['tankwater'] = add('plane', '2A8AC0', (0, 4, 1.25), size=1, scale=(11.8, 9.8, 1), parent=c, rough=0.15, emit=0.5)
    for i, (x, y) in enumerate(((-11, 0.5), (11, 0.5), (-8, 11), (8, 11))):                                       # lamps on stands
        bar(c, '2A2A30', (x, y, 0), (x, y, 5), 0.05)
        add('cylinder', '3A3A40', (x, y, 5.3), rot=(1.0 if y < 0 else -1.0, 0, 0), radius=0.5, depth=0.7, vertices=10, parent=c)
        add('cylinder', 'FFF2D8', (x, y + (0.35 if y < 0 else -0.35), 5.1), rot=(1.0 if y < 0 else -1.0, 0, 0), radius=0.42, depth=0.05, vertices=10, parent=c, emit=8.0)
    cm = empty((3.4, -4.4, 0), c)                                                                                 # a film camera on legs
    for a in (0.3, 2.4, 4.4):
        bar(cm, '2A2A30', (0, 0, 2.0), (0.6 * math.cos(a), 0.6 * math.sin(a), 0), 0.04)
    add('cube', '1E1E24', (0, 0, 2.3), scale=(0.5, 0.9, 0.5), size=1, parent=cm)
    add('cylinder', '1E1E24', (0, 0.6, 2.3), rot=(PI / 2, 0, 0), radius=0.16, depth=0.4, vertices=8, parent=cm)
    S['tankl'] = [light(at(TANK, -6, -3, 6), 0, 'FFF2D8', size=4.0), light(at(TANK, 6, 10, 6), 0, 'BFE4FF', size=4.0),
                  light(at(TANK, 0, 4, 0.8), 0, '7AC8FF', size=6.0)]


def make_jetty(S):
    """The island's little harbour at evening: a timber jetty on calm water, a moored open boat, palms, low houses."""
    c = empty(JETTY)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=50, y_subdivisions=50, size=160, location=at(JETTY, 0, 40, 0))
    w = bpy.context.object
    w.parent = c
    w.location = (0, 40, 0)
    w.data.materials.append(K.mat('24486A', 0.15))
    co = np.zeros(len(w.data.vertices) * 3)
    w.data.vertices.foreach_get('co', co)
    S['jxy'] = co.reshape(-1, 3)[:, :2].copy()
    S['jwater'] = w
    box(c, 'C8B88A', -60, 60, -40, -2, -0.6, 0.6)                                                                 # the shore
    for i in range(12):                                                                                           # jetty planks and posts
        box(c, ('8A6A48', '7A5C3E')[i % 2], -1.0, 1.0, -2 + 1.2 * i, -0.9 + 1.2 * i, 0.9, 1.05)
    for i in range(7):
        for s_ in (-1, 1):
            add('cylinder', '4A3828', (s_ * 1.0, -1.5 + 2.4 * i, 0.4), radius=0.12, depth=1.6, vertices=6, parent=c)
    S['bollard'] = (1.5, 3.4, 1.3)
    add('cylinder', '2A2A30', (1.5, 3.4, 1.15), radius=0.18, depth=0.3, vertices=8, parent=c)
    for i in range(6):                                                                                            # palms
        x, y = -14 + 6 * i + 2 * rnd(i, 51), -8 - 6 * rnd(i, 52)
        bar(c, '6A5A40', (x, y, 0.6), (x + 0.8, y, 7.5), 0.18)
        for j in range(6):
            a = 2 * PI * j / 6
            add('cube', '3A6A3A', (x + 0.8 + 1.4 * math.cos(a), y + 1.4 * math.sin(a), 7.3), rot=(0, 0.5, a), scale=(2.6, 0.5, 0.06), size=1, parent=c)
    S['jlit'] = []
    for i in range(7):                                                                                            # low houses with lit windows
        x, y = -22 + 7 * i, -18 - 4 * rnd(i, 53)
        box(c, ('E8D8B8', 'D8B898', 'C8D8D0', 'E8C8A8')[i % 4], x - 2.4, x + 2.4, y - 2, y + 2, 0.6, 3.6)
        add('cone', ('9A4A3A', '7A3A2E')[i % 2], (x, y, 4.4), rot=(0, 0, PI / 4), radius1=3.6, radius2=0.2, depth=1.6, vertices=4, parent=c)
        S['jlit'].append(add('cube', 'FFC870', (x, y + 2.02, 2.0), scale=(0.9, 0.04, 0.8), size=1, parent=c, emit=4.0))
    S['jboat'] = jb = empty((4.2, 6.0, 0.0), c, (0, 0, 0.1))                                                      # a moored open boat
    add('cube', 'D8E0E8', (0, 0, 0.35), scale=(1.8, 5.4, 0.8), size=1, parent=jb)
    add('cube', 'D8E0E8', (0, 3.0, 0.45), rot=(0, 0, PI / 4), scale=(1.27, 1.27, 0.8), size=1, parent=jb)
    add('cube', '2A6AA8', (0, 0.3, 0.78), scale=(1.86, 6.5, 0.12), size=1, parent=jb)
    S['jettyl'] = [light(at(JETTY, -6, -14, 6), 0, 'FFB070', size=6.0), light(at(JETTY, 3, 4, 5), 0, 'FFD8A0', size=2.0)]


_build1, _reset1 = build, reset


def build():
    S = _build1()
    make_props(S)
    make_shed(S)
    make_desk(S)
    make_tank(S)
    make_jetty(S)
    S['older'] = K.Rig(dict(top='4A5A6A', pants='3A3A44', hand=OLD_SKIN, boot='2A2420', fore='4A5A6A'), older_head)
    S['crew'] = [K.Rig(dict(top=tp, pants='2A2A30', hand=sk, boot='1E1C22', fore=tp), K.human_head(sk, hr)) for tp, sk, hr in
                 (('3A3A44', 'C89A78', '2A2420'), ('6A3A3A', '8A5A40', '17131A'))]
    new = [S['older']] + S['crew']
    S['humans'] += new
    S['cast'] += new
    reset(S)
    return S


def reset(S):
    _reset1(S)
    if 'shedl' not in S:
        return
    for l in S['shedl'] + S['deskl'] + S['tankl'] + S['jettyl'] + [S['flarel']]:
        l.data.energy = 0
    S['flarel'].location = FAR
    for b in S['barn']:
        b.scale = (1, 1, 1)
        b.hide_render = True
    S['uhole'].hide_render = True
    S['ubelly'].rotation_euler = (0, 0, 0)
    S['blink'].data.materials[0] = K.mat('FF3A2A', 0.5, 0.0)
    S['older'].extra['beard'].scale = (0.88, 0.66, 0.42)


def fill(S, o, pos, look, watts, col='FFE8D0'):
    key(S, o, pos, look, watts, col)


def hand_pos(S, rig, i=1, dz=0.0):
    p = wpos(rig.hands[i])
    return (p[0], p[1], p[2] + dz)


def jw(S, t):
    x, y = S['jxy'][:, 0], S['jxy'][:, 1]
    z = 0.08 * np.sin(x * 0.3 + t * 0.9) + 0.06 * np.sin(y * 0.4 - t * 1.2)
    S['jwater'].data.vertices.foreach_set('co', np.column_stack([S['jxy'], z]).ravel())
    S['jwater'].data.update()


# ---------------------------------------------------------------- the hook and the doubt
def night_alone(S, k, t, lt):
    """Very wide, moonlit: the swamped sloop's cabin glow a speck on a huge black ocean, the moon low, a path of light."""
    ocean(S, 'moon', t, 1.0)
    b = S['sloop']
    ride(S, b, t, 0, 0, 0.5, 0.2, 0.6, sink=1.0)
    b.rotation_euler = (b.rotation_euler[0] + 0.3, b.rotation_euler[1] + 0.1, b.rotation_euler[2])
    raft_at(S, t, -4.5, -2.0, 0.4)
    S['moon'].location = at(SEA, -380, 900, 120)
    key(S, SEA, (-10, -14, 10), (0, 0, 1), 5000, '9AB4E0')
    shoot(S, SEA, (lerp(15, 12, k), lerp(-34, -29, k), lerp(8, 6.5, k)), (lerp(-4, -2, k), 8, 1.5), 30)


def rook_deck(S, k, t, lt):
    """Rook stands on the swamped sloop's cabin top, sea washing round his boots, the raft bobbing at its line behind him.
    Brim down, arms folded: 'Out here, alone? No chance.' Then he turns his head to the dark."""
    ocean(S, 'storm', t, 0.9)
    b = S['sloop']
    ride(S, b, t, 0, 0, 0.0, 0.2, 0.5, sink=1.05)
    raft_at(S, t, -3.2, -6.5, 0.4)
    aboard(S, S['man'], 0.0, 0.3, 0.04, 0.5, P('sit', aR=(1.2, 0.2, 0.8), head=(-0.1, 0.5)), 'wide')
    turn = sm((lt - 1.2) / 0.5)
    aboard(S, S['rook'], 0.0, -0.9, 1.45, PI * 0.1, P('cross', head=(0.05, lerp(0.0, -0.6, turn))), 'low', par=b)
    S['hat_tip'] = 0.5 - 0.3 * turn
    bubble(S, t, *wpos(b, (0.9, -1.4, 1.3)), n=10, rise=1.2, spread=0.4)
    h = head(S, S['rook'])
    key(S, SEA, (h[0] - 3, h[1] - 4, h[2] + 3), h, 1500, 'A8C0F0')
    shoot(S, (0, 0, 0), (h[0] - lerp(2.4, 1.9, k), h[1] - lerp(6.4, 5.6, k), h[2] - 0.7), (h[0] + 0.7, h[1], h[2] - 0.9), 30)


# ---------------------------------------------------------------- who he is
def shed_build(S, k, t, lt):
    """The boat shed by day: he planes the sheer of a bare white hull, shavings curling off; Rook leans on a sawhorse,
    arms folded, then taps his beak, eyeing the hull."""
    sky(S, 'shed')
    for l, w in zip(S['shedl'], (2600, 500)):
        l.data.energy = w
    hb = wpos(S['hull2'])
    st = math.sin(lt * 3.2)
    m = put(S, S['man'], SHED, 1.8, 1.4, 0.0, -1.4, P('stand', aR=(1.25 + 0.25 * st, -0.1, 0.5), aL=(1.1 + 0.25 * st, 0.1, 0.6), lean=0.25, head=(0.35, 0.0)), 'hard')
    hd = hand_pos(S, m, 1)
    S['plane'].location, S['plane'].rotation_euler = hd, (0, 0, 1.35)
    for i, s in enumerate(S['shavings']):
        ph = (t * 1.4 + i / 8) % 1.0
        s.location = (hd[0] - 0.2 - 0.3 * ph, hd[1] + 0.3 * rnd(i, 61) - 0.15, hd[2] - 1.2 * ph * ph)
        s.rotation_euler = (ph * 6, ph * 4, 0)
    tap = lt > 1.4
    put(S, S['rook'], SHED, 3.5, 3.2, 0.0, 0.35, P('tap', head=(0.15, 0.3)) if tap else P('cross', lean=-0.1, head=(0.0, 0.5)), 'low' if not tap else 'calm')
    S['hat_tip'] = 0.2
    h = head(S, m)
    key(S, SHED, (5, -5, 5), (2, 1, 2), 900, 'FFE8C8')
    shoot(S, SHED, (lerp(6.0, 5.3, k), lerp(-4.8, -4.2, k), lerp(3.2, 2.9, k)), (lerp(2.4, 2.2, k), lerp(0.4, 0.6, k), 2.1), 30)


def sail_calm(S, k, t, lt):
    """Fair weather: the little sloop under full sail, heeled, a wake behind her; he sits at the tiller, Rook stands on
    the bow with his coat flapping, one hand on the forestay."""
    ocean(S, 'sail', t, 0.45)
    b = S['sloop']
    x, y = 0.0, lerp(-3, 3, k)
    ride(S, b, t, x, y, 0.0, 0.25, 0.6)
    b.rotation_euler = (b.rotation_euler[0], b.rotation_euler[1] - 0.18, b.rotation_euler[2])
    S['sails'].parent, S['sails'].location, S['sails'].rotation_euler = b, (0, 0, 0), (0, 0, 0)
    aboard(S, S['man'], 0.35, -2.6, 0.95, 0.2, P('sit', aR=(0.9, 0.3, 0.5), head=(-0.1, 0.3)), 'calm', par=b)
    aboard(S, S['rook'], 0.0, 3.0, 1.0, PI + 0.4, P('stand', aR=(2.2, 0.2, 0.4), aL=(0.3, 0.4, 0.4), head=(-0.1, -0.4)), 'calm', par=b)
    for i, sp in enumerate(S['spray']):
        ph = (t * 1.5 + i / 12) % 1.0
        sp.location = wpos(b, (1.2 + 0.4 * ph, 4.0 - 2.5 * ph, 0.5 + 0.6 * ph - 1.0 * ph * ph))
    key(S, SEA, (x + 10, y - 10, 8), (x, y, 2), 3000, 'FFF4E0')
    shoot(S, SEA, (lerp(10, 8.5, k), y + lerp(-7, -5, k), lerp(2.9, 2.6, k)), (x, y + 0.5, 2.8), 30)


def canary_leave(S, k, t, lt):
    """Dusk: the sloop under sail heads away from a dark volcanic island with a few lit houses; the sun going down ahead."""
    ocean(S, 'dusk', t, 0.5)
    b = S['sloop']
    y = lerp(10, 4, k)
    ride(S, b, t, 0, y, PI, 0.25, 0.6)
    b.rotation_euler = (b.rotation_euler[0], b.rotation_euler[1] + 0.12, b.rotation_euler[2])
    S['sails'].parent, S['sails'].location, S['sails'].rotation_euler = b, (0, 0, 0), (0, 0, 0)
    aboard(S, S['man'], 0.35, -2.6, 0.95, 0.2, P('sit', head=(-0.1, 0.6)), 'calm', par=b)
    S['canary'].location = at(SEA, 60, 420, -2)
    key(S, SEA, (-8, y - 12, 6), (0, y, 3), 2500, 'FFB080')
    shoot(S, SEA, (lerp(-9, -7, k), y - lerp(18, 14, k), lerp(2.4, 2.8, k)), (4, y + 40, 6), 34)


# ---------------------------------------------------------------- the dive
def deck_swamped(S, k, t, lt):
    """Night: the sloop low and swamped, waves running over the deck; he hauls himself back aboard from the raft over the
    rail; Rook clings to the mast, hat jammed down."""
    ocean(S, 'storm', t, 1.0)
    b = S['sloop']
    ride(S, b, t, 0, 0, 0.6, 0.2, 0.6, sink=0.95)
    raft_at(S, t, -2.8, -1.2, 0.4)
    u = sm((lt - 0.2) / 1.6)
    m = aboard(S, S['man'], lerp(-1.6, -0.6, u), lerp(-0.4, -0.2, u), lerp(0.2, 1.0, u), -PI / 2 + 0.3,
               blend(P('reach', aL=(2.6, 0.3, 0.2), aR=(2.2, 0.2, 0.4), lean=0.6, head=(-0.2, 0.0)), P('stand', aR=(1.4, 0.2, 0.6), lean=0.4, head=(0.4, 0.0)), u), 'hard', par=b)
    aboard(S, S['rook'], 0.25, 0.85, 1.4, PI + 0.6, P('brace', aL=(2.4, 0.2, 0.6), head=(0.1, 0.4)), 'shocked' if lt > 0.8 else 'calm', par=b)
    S['hat_tip'] = 0.6
    for i, sp in enumerate(S['spray']):
        ph = (t * 1.6 + i / 12) % 1.0
        sp.location = wpos(b, (-1.4 + 2.6 * ph, -1.0 + 0.5 * rnd(i, 7), 1.0 + 0.9 * ph - 1.6 * ph * ph))
    h = head(S, m)
    key(S, SEA, (h[0] - 4, h[1] - 5, h[2] + 4), h, 2200, 'A8C0F0')
    shoot(S, (0, 0, 0), (h[0] - lerp(4.4, 3.8, k), h[1] - lerp(4.6, 4.0, k), h[2] + lerp(1.2, 0.8, k)), (h[0] + 0.6, h[1] + 0.6, h[2] - 0.4), 28)


def rook_hatch(S, k, t, lt):
    """From inside the flooded cabin, looking up the companionway: Rook crouches on the top step holding a torch, its beam
    on black water; he leans in and peers down."""
    sky(S, 'cabin')
    rl = 0.14 * math.sin(t * 2.1)
    S['cabin'].rotation_euler = (0.04 * math.sin(t * 1.6), rl, 0)
    S['flood'].location, S['flood'].rotation_euler = at(CABIN, 0, 0, 1.55 + 0.05 * math.sin(t * 2)), (0, 0.04 * math.sin(t * 3), 0)
    lean = sm((lt - 0.4) / 0.8)
    r = put(S, S['rook'], CABIN, 0.0, -2.6, 0.9, PI, P('sit', aR=(1.6, 0.0, 0.3), lean=lerp(0.2, 0.6, lean), head=(lerp(0.1, 0.3, lean), 0.0)), 'calm' if lean < 0.6 else 'shocked')
    hd = hand_pos(S, r, 1)
    S['torch'].location, S['torch'].rotation_euler = hd, (0.9, 0, 0)
    S['torchl'].location, S['torchaim'].location = (hd[0], hd[1] + 0.1, hd[2]), at(CABIN, 0.3, 0.8, 1.5)
    S['torchl'].data.energy = 300
    S['clampl'].data.energy = 15
    for i, sp in enumerate(S['bubbles'][:10]):
        ph = (t * 0.8 + i / 10) % 1.0
        sp.location = at(CABIN, -0.8 + 1.6 * rnd(i, 3), 0.5 + 1.5 * rnd(i, 4), 1.56 + 0.02 * math.sin(t * 4 + i))
    h = head(S, r)
    key(S, CABIN, (0.6, -0.6, 1.8), h, 520, '7AA8E0')
    shoot(S, CABIN, (lerp(0.7, 0.55, k), lerp(0.9, 0.5, k), 1.72), (h[0] - CABIN[0], h[1] - CABIN[1], h[2] - CABIN[2] - 0.35), 30)


def dive_cabin(S, k, t, lt):
    """Under the water inside the cabin: he swims down head first from the companionway past the bunks, the torch beam
    swinging, and closes his hand on the yellow emergency bag lashed by the bunk; bubbles stream from his mouth."""
    sky(S, 'cabin')
    S['cabin'].rotation_euler = (0, 0.06 * math.sin(t * 1.5), 0)
    S['flood'].location = at(CABIN, 0, 0, 2.42)
    u = sm(lt / 1.8)
    m = put(S, S['man'], CABIN, lerp(0.1, 0.35, u), lerp(-2.8, -1.85, u), lerp(2.15, 1.95, u), PI - 0.1,
            P('swim', aR=(lerp(2.9, 2.5, u), 0.15, 0.2), aL=(lerp(2.7, 2.2, u), 0.2, 0.4), head=(-0.5, 0.0)), 'shut', pitch=lerp(1.75, 1.95, u))
    S['ebag'].location, S['ebag'].rotation_euler = at(CABIN, 1.0, 1.2, 0.95), (0, 0, 0.2)
    S['sbag'].location = at(CABIN, -1.0, 1.4, 0.95)
    S['cushion'].location, S['cushion'].rotation_euler = at(CABIN, -0.5, 0.2, 2.2 + 0.05 * math.sin(t * 2)), (0.2, 0.1, 0.5)
    hd = hand_pos(S, m, 1)
    S['torch'].location, S['torch'].rotation_euler = hd, (-0.6, 0, 0.3)
    S['torchl'].location, S['torchaim'].location = hd, at(CABIN, 1.0, 1.2, 0.9)
    S['torchl'].data.energy = 300
    hh = head(S, m)
    bubble(S, t, hh[0], hh[1], hh[2] + 0.2, 14, 1.2, 0.3)
    key(S, CABIN, (-1.2, 2.2, 2.0), hh, 420, '4A9AC8')
    shoot(S, CABIN, (lerp(-1.25, -1.1, k), lerp(2.9, 2.6, k), lerp(1.75, 1.6, k)), (lerp(0.3, 0.5, k), lerp(0.0, 0.4, k), 1.15), 22)


# ---------------------------------------------------------------- the raft and its kit
def rook_ducky(S, k, t, lt):
    """Grey dawn, low at the water: the round black raft fills the frame; Rook sits on the canopy arch, legs dangling, and
    squeezes the tube. 'Rubber Ducky.' His hat brim slides down over his eyes."""
    ocean(S, 'dawn', t, 0.6)
    r = raft_at(S, t, 0, 0, 0.3)
    aboard(S, S['man'], 0.2, 0.3, 0.04, PI + 0.4, P('sit', head=(0.4, 0.3)), 'tired')
    sq = 0.5 + 0.5 * math.sin(lt * 10) if lt < 0.9 else 0.0
    aboard(S, S['rook'], -0.95, -0.7, 0.66, -0.7, P('sit', aR=(1.0, 0.3, 0.3), aL=(0.6, 0.2, 1.2), head=(0.1, 0.1)), 'low')
    S['tubes'][1].scale = (1, 1, 1 - 0.06 * sq)
    S['hat_tip'] = lerp(0.1, 1.0, sm((lt - 1.0) / 0.6))
    h = head(S, S['rook'])
    key(S, SEA, (h[0] - 2, h[1] - 4, h[2] + 2), h, 900, 'FFC8A0')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.2, 0.9, k), h[1] - lerp(3.6, 3.0, k), h[2] - lerp(0.8, 0.7, k)), (h[0] - 0.3, h[1] + 0.3, h[2] - 0.35), 30)


def kit_spread(S, k, t, lt):
    """From above the open side of the raft: the kit laid out on the floor (three water tins, a little food, red flares, a
    yellow radio beacon, the short spear gun, the folded still, the sleeping bag); Rook kneels and taps each with a pencil,
    counting."""
    ocean(S, 'day', t, 0.35)
    r = raft_at(S, t, 0, 0, 0.0, tilt=0.4)
    L = lambda x, y, z=0.1: wpos(r, (x, y, z))
    for i, tn in enumerate(S['tins']):
        tn.location = L(-0.7 + 0.28 * i, -0.75, 0.2)
    S['food'].location, S['food'].rotation_euler = L(0.25, -0.85, 0.1), (0, 0, 0.3)
    S['flares'].location, S['flares'].rotation_euler = L(0.55, -0.35, 0.1), (0, 0, 0.6)
    S['beacon'].location = L(-0.35, -0.15, 0.05)
    S['blink'].data.materials[0] = K.mat('FF3A2A', 0.5, 30.0 if (t * 1.5) % 1 < 0.3 else 0.0)
    S['gun'].location, S['gun'].rotation_euler = L(0.1, -0.35, 0.12), (0, 0, 1.4)
    S['spear'].location, S['spear'].rotation_euler = L(0.1, -0.35, 0.16), (0, 0, 1.4)
    S['still'].location, S['still'].scale = L(-0.1, 0.45, 0.05), (0.6, 0.6, 0.3)
    S['sbag'].location = L(0.0, 0.85, 0.25)
    n = int(lt / 0.55) % 5
    tgt = [S['tins'][1].location, S['food'].location, S['flares'].location, S['beacon'].location, S['gun'].location][n]
    rk = aboard(S, S['rook'], -1.0, -0.2, 0.04, PI / 2 + 0.3, P('sit', aR=(1.3, 0.1, 0.3 + 0.2 * math.sin(lt * 11)), lean=0.35, head=(0.35, 0.0)), 'calm')
    S['hat_tip'] = 0.2
    h = head(S, rk)
    key(S, SEA, (h[0], h[1] - 3, h[2] + 4), L(0, -0.3), 700, 'FFF4E0')
    shoot(S, (0, 0, 0), (lerp(2.5, 2.1, k) + r.location[0], r.location[1] - lerp(3.1, 2.7, k), r.location[2] + lerp(3.0, 2.8, k)), (r.location[0] - 0.35, r.location[1] - 0.2, r.location[2] + 0.75), 28)


def still_open(S, k, t, lt):
    """Under the canopy: he holds a solar still open on his knees, working on it; Rook holds its clear skin up against
    the light and peers through it, then looks at us and nods: so that's how it works."""
    ocean(S, 'hot', t, 0.35)
    r = raft_at(S, t, 0, 0, 0.2)
    m = aboard(S, S['man'], -0.4, 0.25, 0.04, 0.6, P('sit', aR=(1.3, 0.1, 1.3, 0.4), aL=(1.3, 0.1, 1.3, 0.4), lean=0.45, head=(0.55, 0.2)), 'hard')
    hd, hl = hand_pos(S, m, 1), hand_pos(S, m, 0)
    S['still'].location = ((hd[0] + hl[0]) / 2, (hd[1] + hl[1]) / 2, (hd[2] + hl[2]) / 2 - 0.25)
    S['still'].scale = (0.7, 0.7, 0.55)
    look = sm((lt - 1.3) / 0.4)
    rk = aboard(S, S['rook'], 0.6, -0.35, 0.04, lerp(1.2, 0.3, look), P('sit', aR=(2.2, 0.2, 0.6), aL=(2.0, -0.1, 0.8), head=(lerp(-0.3, 0.05, look), 0.0)), 'calm' if look < 0.5 else 'soft')
    p = hand_pos(S, rk, 1)
    S['cup'].location, S['cup'].rotation_euler = (p[0], p[1], p[2] + 0.12), (0.3, 0, 0)
    h = head(S, rk)
    key(S, SEA, (h[0] + 1, h[1] - 4, h[2] + 3), h, 700, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] - lerp(1.6, 1.2, k), h[1] - lerp(3.6, 3.0, k), h[2] + 0.1), (h[0] - 0.5, h[1] + 0.3, h[2] - 0.45), 28)


def rain_catch(S, k, t, lt):
    """A grey squall: rain sheeting down; he tips his face up and holds a tin under the canopy's edge where the water
    runs off in a stream; Rook huddles under the canopy and shakes the rain off his hat."""
    ocean(S, 'rainy', t, 0.8)
    r = raft_at(S, t, 0, 0, 0.5)
    m = aboard(S, S['man'], 0.0, -0.4, 0.04, 0.0, P('sit', aR=(1.9, 0.1, 0.4), head=(-0.5, 0.0)), 'shut')
    hd = hand_pos(S, m, 1)
    S['tins'][0].location = (hd[0], hd[1] - 0.05, hd[2] + 0.12)
    edge = wpos(r, (0.2, -0.05, 1.95))
    for i, d in enumerate(S['rdrops']):
        ph = (t * 2.4 + i / 10) % 1.0
        d.location = (lerp(edge[0], hd[0], ph), lerp(edge[1], hd[1] - 0.05, ph), lerp(edge[2], hd[2] + 0.25, ph))
    sh = math.sin(lt * 18) * (lt > 1.0)
    aboard(S, S['rook'], -0.5, 0.6, 0.04, -0.6, P('sit', aR=(2.2, 0.6, 1.0, 0.2 * sh), head=(0.2, 0.1 * sh)), 'low')
    S['hat_jump'] = 0.08 * abs(sh)
    h = head(S, m)
    key(S, SEA, (h[0] - 2, h[1] - 4, h[2] + 3), h, 900, 'D8E0EA')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.4, 1.0, k), h[1] - lerp(3.6, 3.0, k), h[2] + lerp(0.1, 0.2, k)), (h[0] - 0.3, h[1] + 0.4, h[2] - 0.2), 28)


# ---------------------------------------------------------------- the reef under the raft
def reef_under(S, k, t, lt):
    """Underwater, close under the raft's floor: barnacles bud and grow across the black rubber; small grey triggerfish
    nose in and peck at them."""
    sky(S, 'under')
    usurf(S, t)
    S['ubelly'].location = at(UNDER, 0, 0, -0.05)
    g = sm(lt / 2.0)
    for i, b_ in enumerate(S['barn']):
        b_.hide_render = False
        s = max(0.05, min(1.0, g * 1.6 - 0.6 * rnd(i, 34)))
        b_.scale = (s, s, s)
    for i, f in enumerate(S['trig']):
        a = t * 0.6 * (1 if i % 2 else -1) + 2 * PI * i / 5
        rr = 0.9 + 0.3 * rnd(i, 35)
        peck = 0.15 * max(0.0, math.sin(t * 5 + i))
        f.location = at(UNDER, rr * math.cos(a), rr * math.sin(a), -0.75 + peck)
        f.rotation_euler = (-0.5, 0, a + (PI if i % 2 else 0))
    key(S, UNDER, (1.5, -2.5, -2.6), (0, 0, -0.2), 500, '9AE8F8')
    shoot(S, UNDER, (lerp(1.3, 1.0, k), lerp(-2.4, -2.0, k), lerp(-1.7, -1.5, k)), (0, -0.2, -0.25), 26)


def school_follow(S, k, t, lt):
    """At water level behind the raft as it drifts: the dorado school's fins and backs flash gold-green in its wake, keeping
    pace; Rook on the canopy turns, sees them and lifts his brim."""
    ocean(S, 'day', t, 0.45)
    y = lerp(0, 2.0, k)
    r = raft_at(S, t, 0, y, 0.0)
    aboard(S, S['man'], 0.1, -0.2, 0.04, PI, P('sit', head=(0.3, 0.2)), 'squint')
    for i, (f, tail, body) in enumerate(S['fish'][:10]):
        a = 2 * PI * i / 10 + 0.3 * math.sin(t * 0.7 + i)
        x_, y_ = 2.4 * math.cos(a) * (0.8 + 0.4 * rnd(i, 1)), y - 2.0 + 1.6 * math.sin(a) - 1.2 * rnd(i, 2)
        f.location = at(SEA, x_, y_, wave_at(S, x_, y_, t) - 0.18 + 0.12 * math.sin(t * 3 + i))
        f.rotation_euler = (0, 0, 0.2 * math.sin(t + i))
        tail.rotation_euler = (0, 0, 0.5 * math.sin(t * 10 + i))
    turn = sm((lt - 0.6) / 0.6)
    aboard(S, S['rook'], 0.0, 0.5, 2.1, lerp(PI, 0.2, turn), P('hat', head=(0.2, 0.0)) if turn > 0.7 else P('stand', head=(0.0, 0.0)), 'shocked' if turn > 0.7 else 'calm')
    S['hat_tip'] = lerp(0.4, -0.3, turn)
    key(S, SEA, (4, y - 10, 6), (0, y, 1.5), 2500, 'FFF4E0')
    shoot(S, SEA, (lerp(2.5, 2.0, k), y - lerp(8.5, 7.5, k), lerp(0.9, 1.1, k)), (0, y - 0.5, 1.2), 30)


def gun_snap(S, k, t, lt):
    """Close on his hands over the tube: the line jerks taut into the water, the gun's tip snaps and the spear springs
    loose; then he lashes the broken gun back together with cord, jaw set."""
    ocean(S, 'day', t, 0.5)
    r = raft_at(S, t, 0, 0, 0.0)
    snap = lt > 0.7
    m = aboard(S, S['man'], 0.0, -0.55, 0.04, 0.0, P('sit', aR=(1.2, 0.0, 0.5), aL=(1.2, 0.1, 0.7), lean=0.6, head=(0.6, 0.0)), 'hard' if snap else 'squint')
    hd, hl = hand_pos(S, m, 1), hand_pos(S, m, 0)
    yank = 0.15 * math.sin(lt * 30) if 0.3 < lt < 0.75 else 0.0
    g = ((hd[0] + hl[0]) / 2, (hd[1] + hl[1]) / 2 - 0.15 + yank, (hd[2] + hl[2]) / 2)
    S['gun'].location, S['gun'].rotation_euler = g, (-0.6 - (0.0 if not snap else 0.3), 0, 0)
    if not snap:
        S['spear'].location, S['spear'].rotation_euler = g, (-0.6, 0, 0)
    else:
        u = sm((lt - 0.7) / 0.3)
        S['spear'].location, S['spear'].rotation_euler = (g[0] + 0.3 * u, g[1] - 0.9 * u, g[2] - 0.5 * u), (-1.2, 0.4 * u, 0.3)
        wrap = sm((lt - 1.2) / 1.0)
        S['cord'].location, S['cord'].rotation_euler = (g[0], g[1] - 0.1, g[2]), (PI / 2, 0, 6 * wrap)
        S['cord'].scale = (1 + 0.5 * wrap, 1 + 0.5 * wrap, 1)
    h = head(S, m)
    key(S, SEA, (h[0] + 2, h[1] - 3, h[2] + 3), g, 700, 'FFF4E0')
    shoot(S, (0, 0, 0), (g[0] + lerp(1.1, 0.8, k), g[1] - lerp(1.6, 1.3, k), g[2] + lerp(0.7, 0.5, k)), (g[0], g[1] + 0.1, g[2] + 0.15), 30)


# ---------------------------------------------------------------- sharks
def shark_under(S, k, t, lt):
    """Underwater: a hammerhead rises out of the blue, sweeps under the raft and rams the floor; the raft jolts up and
    the dorado scatter."""
    sky(S, 'under')
    usurf(S, t)
    hit = sm((lt - 1.1) / 0.25) * (1 - sm((lt - 1.5) / 0.6))
    S['ubelly'].location = at(UNDER, 0, 0, -0.05 + 0.35 * hit)
    S['ubelly'].rotation_euler = (0.12 * hit, 0, 0)
    school(S, t, 0, 0, -1.0, 1.0 + 1.2 * sm((lt - 1.0) / 0.5), n=10)
    u = sm(lt / 1.3)
    sk = S['shark']
    sk.location = at(UNDER, lerp(-1.0, 0.0, u), lerp(-9, -0.6, u), lerp(-8, -1.0, u))
    sk.rotation_euler = (lerp(0.7, 0.25, u), 0, lerp(0.3, 0.0, u))
    S['stail'].rotation_euler = (0, 0, 0.35 * math.sin(t * 5))
    key(S, UNDER, (5, -6, -1), (0, -1.5, -2.0), 2500, '9AE8F8')
    shoot(S, UNDER, (lerp(3.8, 3.2, k), lerp(3.4, 2.8, k), lerp(-4.6, -4.2, k)), (0, -1.8, -1.8), 24)


def raft_bump(S, k, t, lt):
    """In the raft: a blow from below kicks the floor up under them; he braces against the tube, Rook pops into the air,
    a feather sheds from him and drifts down."""
    ocean(S, 'day', t, 0.5)
    hit = math.exp(-((lt - 0.5) / 0.14) ** 2)
    r = raft_at(S, t, 0, 0, 0.3, sink=-0.3 * hit, tilt=1.0 + 2.0 * hit)
    m = aboard(S, S['man'], -0.2, -0.2, 0.04 + 0.2 * hit, 0.5, P('brace', lL=(1.3, 1.5), lR=(1.3, 1.5), lift=-0.5, head=(0.2, 0.3)), 'wide' if lt > 0.45 else 'tired')
    aboard(S, S['rook'], 0.7, -0.6, 0.04 + 0.9 * hit, -0.3, P('scream', lL=(0.9, 1.2), lR=(0.9, 1.2)) if lt > 0.4 else P('sit'), 'shocked' if lt > 0.42 else 'calm')
    S['hat_jump'] = 0.5 * hit
    f = sm((lt - 0.55) / 1.6)
    p = wpos(r, (0.7, -0.6, 2.4))
    S['rfea'].location, S['rfea'].rotation_euler = (p[0] + 0.5 * f + 0.15 * math.sin(lt * 5), p[1] - 0.4 * f, p[2] + 0.6 - 1.8 * f), (1.2 + 3 * f, 0.6 * math.sin(lt * 4), 0.3)
    h = head(S, m)
    key(S, SEA, (h[0] + 2, h[1] - 4, h[2] + 3), h, 800, 'FFF4E0')
    shoot(S, (0, 0, 0), (h[0] + lerp(2.2, 1.8, k), h[1] - lerp(4.6, 4.0, k), h[2] + 0.3), (h[0] + 0.4, h[1], h[2] - 0.3), 26)


# ---------------------------------------------------------------- ships
def flare_night(S, k, t, lt):
    """Night: a ship's lights far off on the horizon; he stands in the raft and fires a flare; it climbs red into the dark
    and hangs there, lighting the sea red. The ship's lights keep going."""
    ocean(S, 'night', t, 0.5)
    r = raft_at(S, t, 0, 0, PI)
    S['shipnight'].location = at(SEA, lerp(-60, -20, k), 260, 0)
    S['shipnight'].rotation_euler = (0, 0, 0)
    m = aboard(S, S['man'], 0.0, 0.3, 0.04, PI + PI, P('stand', aR=(2.7, 0.2, 0.1), aL=(0.4, 0.3, 0.4), head=(-0.4, 0.0)), 'wide')
    hd = hand_pos(S, m, 1)
    S['pistol'].location, S['pistol'].rotation_euler = hd, (-1.3, 0, 0)
    u = sm((lt - 0.25) / 1.2)
    if lt > 0.25:
        fp = (hd[0] - 4 * u, hd[1] + 30 * u, hd[2] + 22 * u - 6 * u * u)
        S['flare'].location = fp
        S['flarel'].location = (fp[0], fp[1], fp[2] - 1)
        S['flarel'].data.energy = 30000 * min(1.0, lt * 2)
        for i, tr_ in enumerate(S['trail']):
            v = max(0.0, u - 0.04 * (i + 1))
            tr_.location = (hd[0] - 4 * v, hd[1] + 30 * v, hd[2] + 22 * v - 6 * v * v)
    blink = (t * 1.5) % 1 < 0.3
    S['beacon'].location = wpos(r, (0.6, 0.6, 0.1))
    S['blink'].data.materials[0] = K.mat('FF3A2A', 0.5, 40.0 if blink else 0.0)
    h = head(S, m)
    key(S, SEA, (h[0] + 3, h[1] - 1, h[2] + 1), h, 700, 'FF9A7A')
    shoot(S, (0, 0, 0), (h[0] + lerp(4.6, 4.0, k), h[1] - lerp(2.4, 2.0, k), h[2] - 0.6), (h[0] - 0.6, h[1] + 5, h[2] + lerp(1.6, 3.0, k)), 26)


# ---------------------------------------------------------------- the patch, the fork
def pump_night(S, k, t, lt):
    """Night under a few stars: he works a hand pump into the soft bottom tube, stroke after stroke, head down; Rook,
    dozing against the canopy, jolts awake and puts his wing on the handle too."""
    ocean(S, 'moon', t, 0.45)
    r = raft_at(S, t, 0, 0, 0.6, sink=0.08, tilt=0.8)
    S['tubes'][0].scale = (1, 1, 0.75 + 0.1 * math.sin(lt * 4))
    st = 0.5 + 0.5 * math.sin(lt * 4.5)
    m = aboard(S, S['man'], -0.15, -0.35, 0.04, 0.2, P('sit', aR=(0.9 + 0.5 * st, 0.0, 0.9 - 0.6 * st), aL=(0.9 + 0.5 * st, 0.15, 0.9 - 0.6 * st), lean=0.5, head=(0.7, 0.0)), 'tired')
    thin(S, 0.5)
    pp = wpos(r, (0.15, -0.95, 0.05))
    S['pump'].location, S['pump'].rotation_euler = pp, (0, 0, 0.3)
    S['pumprod'].location.z = 0.45 + 0.25 * st
    S['pumphandle'].location.z = 0.67 + 0.25 * st
    wake = sm((lt - 1.0) / 0.3)
    aboard(S, S['rook'], 0.75, 0.15, 0.04, -0.9 + 0.4 * wake, P('sit', head=(lerp(0.7, 0.1, wake), 0.2), aR=(lerp(0.4, 1.3 + 0.3 * st, wake), 0.0, 0.6)), 'shocked' if 0.2 < wake < 0.9 else ('low' if wake < 0.2 else 'calm'))
    S['hat_tip'] = lerp(0.9, 0.2, wake)
    h = head(S, m)
    key(S, SEA, (h[0] + 2, h[1] - 3, h[2] + 3), h, 1400, 'B8CCF4')
    shoot(S, (0, 0, 0), (h[0] + lerp(2.2, 1.8, k), h[1] - lerp(3.6, 3.0, k), h[2] + 0.6), (h[0] + 0.5, h[1] - 0.5, h[2] - 0.9), 28)


def fork_find(S, k, t, lt):
    """Close over the open mess tin: his fingers lift out a fork, and it catches the sun; behind it Rook's eyes go wide
    at the shiny thing and he reaches for it; the man pulls it away."""
    ocean(S, 'hot', t, 0.35)
    r = raft_at(S, t, 0, 0, 0.0, sink=0.1, tilt=0.6)
    m = aboard(S, S['man'], -0.3, -0.35, 0.04, 0.3, P('sit', aR=(lerp(1.1, 1.6, sm(lt / 0.8)), 0.0, lerp(1.0, 1.6, sm(lt / 0.8))), lean=0.5, head=(0.4, 0.2)), 'squint')
    S['mess'].location = wpos(r, (0.1, -0.75, 0.06))
    hd = hand_pos(S, m, 1)
    S['fork'].location, S['fork'].rotation_euler = (hd[0], hd[1] - 0.08, hd[2] + 0.15), (0.2, 0.3 * math.sin(lt * 3), 0.6)
    reach = sm((lt - 1.0) / 0.4) * (1 - sm((lt - 1.7) / 0.3))
    aboard(S, S['rook'], 0.65, -0.6, 0.04, 0.9, P('sit', aR=(lerp(0.6, 1.6, reach), 0.2, 0.3), lean=0.3 + 0.3 * reach, head=(0.3, -0.2)), 'shocked' if lt > 0.7 else 'calm')
    S['hat_jump'] = 0.12 * reach
    key(S, SEA, (hd[0] + 1, hd[1] - 2, hd[2] + 2), hd, 500, 'FFF8E8')
    shoot(S, (0, 0, 0), (hd[0] - lerp(0.9, 0.7, k), hd[1] - lerp(2.4, 2.0, k), hd[2] + lerp(0.25, 0.15, k)), (hd[0] + 0.35, hd[1] + 0.1, hd[2] + 0.2), 30)


def pencil_sextant(S, k, t, lt):
    """Night, a sky full of stars: he holds three pencils lashed into a triangle up to one bright star and sights along
    them; Rook leans in cheek to cheek, squints along the same line, then taps his beak and writes in the log."""
    ocean(S, 'night', t, 0.4)
    r = raft_at(S, t, 0, 0, PI * 0.8)
    m = aboard(S, S['man'], -0.2, -0.2, 0.04, PI * 0.2, P('sit', aR=(2.2, 0.1, 0.5), aL=(2.0, 0.2, 0.7), head=(-0.45, 0.0)), 'squint')
    thin(S, 0.4)
    hd, hl = hand_pos(S, m, 1), hand_pos(S, m, 0)
    S['pencils'].location = ((hd[0] + hl[0]) / 2, (hd[1] + hl[1]) / 2, (hd[2] + hl[2]) / 2 + 0.1)
    S['pencils'].rotation_euler = (0.5, 0.1 * math.sin(lt * 1.3), PI * 0.2 + PI)
    S['star'].location = at(SEA, -300, 700, 380)
    tapping = lt > 1.4
    aboard(S, S['rook'], -0.55, 0.1, 0.04, PI * 0.2 - 0.2, P('tap', head=(-0.3, 0.0)) if tapping else P('sit', aL=(0.7, 0.2, 1.4), head=(-0.45, -0.1)), 'calm' if tapping else 'low')
    S['hat_tip'] = -0.2
    h = head(S, m)
    key(S, SEA, (h[0] - 1.0, h[1] + 2.5, h[2] + 1), h, 420, 'B8CCF4')
    shoot(S, (0, 0, 0), (h[0] - lerp(1.5, 1.2, k), h[1] + lerp(2.6, 2.2, k), h[2] - lerp(0.45, 0.35, k)), (h[0] - 0.25, h[1], h[2] + 0.3), 28)


def sun_beat(S, k, t, lt):
    """High and wide under a white sun: the raft a small dark ring on a glaring sea, the canopy faded, nothing moving but
    the swell and the slow circle of fish."""
    ocean(S, 'hot', t, 0.3)
    raft_at(S, t, 0, 0, 0.2 + 0.2 * k)
    aboard(S, S['man'], 0.0, 0.2, 0.04, PI, P('sit', lean=0.6, head=(0.7, 0.0)), 'tired')
    thin(S, 1.0)
    for i, (f, tail, body) in enumerate(S['fish'][:7]):
        a = t * 0.25 + 2 * PI * i / 7
        f.location = at(SEA, 3.0 * math.cos(a), 3.0 * math.sin(a), wave_at(S, 3.0 * math.cos(a), 3.0 * math.sin(a), t) - 0.25)
        f.rotation_euler = (0, 0, a + PI / 2)
    shoot(S, SEA, (lerp(3.5, 2, k), lerp(-8, -7, k), lerp(10, 9, k)), (0, 0, 0.8), 30)


# ---------------------------------------------------------------- ashore and after
def jetty_eve(S, k, t, lt):
    """Evening at the island's harbour: thin and bearded, he walks slowly up the jetty, a fisherman's hand under his arm,
    lit windows behind the palms; Rook sits on a bollard and takes his hat off as they pass."""
    sky(S, 'harbour')
    jw(S, t)
    for l, w in zip(S['jettyl'], (1600, 300)):
        l.data.energy = w
    y = lerp(5.6, 2.0, k)
    wk = K.walk(lt * 0.55, 1.0)
    m = put(S, S['man'], JETTY, -0.3, y, 1.05, 0.0, wk, 'tired')
    thin(S, 1.0)
    f = S['fishers'][0]
    put(S, f, JETTY, 0.4, y + 0.1, 1.05, 0.0, blend(K.walk(lt * 0.55 + 0.3, 1.0), P('stand', aL=(0.6, -0.5, 0.8)), 0.5), 'warm')
    bx, by, bz = S['bollard']
    off = sm((lt - 1.2) / 0.5)
    put(S, S['rook'], JETTY, bx + 0.1, by, bz - 0.55, -0.9, P('sit', head=(0.1, -0.3)), 'soft')
    S['hat_off'] = off
    h = head(S, m)
    key(S, JETTY, (3, y - 6, 4), (0, y, 2.5), 900, 'FFC890')
    shoot(S, JETTY, (lerp(4.2, 3.6, k), lerp(-3.4, -3.0, k) + y * 0.3, lerp(2.6, 2.4, k)), (0.0, y + 1.0, 2.3), 30)


def desk_book(S, k, t, lt):
    """A study by a window on the sea: older now, he types at a desk beside stacks of pages; Rook stands at the end of the
    desk and leafs through the finished book, nodding."""
    sky(S, 'study')
    for l, w in zip(S['deskl'], (260, 900)):
        l.data.energy = w
    ty = 0.5 + 0.5 * math.sin(lt * 14)
    m = put(S, S['older'], DESK, 0.0, 1.0, 0.0, PI, P('sit', aR=(1.2, 0.0, 1.3 - 0.1 * ty), aL=(1.2, 0.0, 1.3 - 0.1 * (1 - ty)), lean=0.2, head=(0.3, 0.0), lift=-0.35), 'calm')
    flip = (lt * 1.6) % 1.0
    rk = put(S, S['rook'], DESK, 2.2, 1.3, 0.0, PI + 1.2, P('stand', aR=(1.3, 0.0, 1.2, 0.5), aL=(1.1, 0.1, 1.3), head=(0.5, 0.0)), 'calm')
    p = hand_pos(S, rk, 0)
    S['book'].location, S['book'].rotation_euler = (p[0], p[1], p[2] + 0.1), (0.5, 0, PI + 1.2 + 0.2 * math.sin(flip * PI))
    S['hat_tip'] = 0.1
    h = head(S, m)
    shoot(S, DESK, (lerp(-2.6, -2.2, k), lerp(-2.4, -2.0, k), lerp(2.6, 2.4, k)), (0.6, 1.7, 1.6), 30)


def film_tank(S, k, t, lt):
    """A dark film studio: the story's own round raft floats in a lit tank; Callahan, older, stands at the tank's edge and
    shows two crew members how a man sits and braces in it."""
    sky(S, 'studio')
    for l, w in zip(S['tankl'], (1600, 900, 600)):
        l.data.energy = w
    r = S['raft']
    r.location, r.rotation_euler = at(TANK, 0.3 * math.sin(t * 0.7), 4 + 0.2 * math.sin(t * 0.5), 1.27 + 0.04 * math.sin(t * 1.3)), (0.03 * math.sin(t), 0.03 * math.cos(t * 1.2), 0.3)
    S['tankwater'].location.z = 1.25 + 0.01 * math.sin(t * 2)
    g = math.sin(lt * 2.4)
    m = put(S, S['older'], TANK, -2.0, -1.4, 1.6, -0.5, P('point', aR=(1.6, 0.1, 0.1 + 0.2 * g), aL=(0.6, 0.6, 0.8), head=(0.15, 0.4)), 'warm')
    m.jawv = 0.3 * abs(g)
    for i, c in enumerate(S['crew']):
        put(S, c, TANK, -3.6 - 1.0 * i, -2.6 - 0.6 * i, 0.0, -0.9 - 0.2 * i, P('cross' if i else 'think', head=(-0.05, -0.2)), 'calm')
    h = head(S, m)
    key(S, TANK, (h[0] - 4, h[1] - 4, h[2] + 2), h, 700, 'FFE8D0')
    shoot(S, TANK, (lerp(-8.4, -7.4, k), lerp(-8.6, -7.6, k), lerp(4.4, 4.0, k)), (lerp(-1.6, -1.2, k), 1.0, 1.8), 30)


def photo_thumb(S, k, t, lt):
    """The thumbnail picture: close on him in the raft, thin and bearded, squinting into a hard sun, the orange canopy
    behind him and Rook sitting on the far tube, brim low; open sea and sky on the left for the words."""
    ocean(S, 'day', 1.0, 0.5)
    yaw = 0.6
    r = raft_at(S, 1.0, 0, 0, yaw)
    m = aboard(S, S['man'], 0.6, -0.45, 0.04, 0.0, P('sit', aR=(1.55, -0.15, 2.45, 0.4), aL=(0.45, 0.1, 1.1), lean=0.1, head=(-0.25, 0.2)), 'squint')
    thin(S, 0.7)
    h = head(S, m)
    d = (math.sin(yaw), -math.cos(yaw))
    rv = (math.cos(yaw), math.sin(yaw))
    cam = (h[0] + 4.2 * d[0] + 0.6 * rv[0], h[1] + 4.2 * d[1] + 0.6 * rv[1], h[2] + 0.1)
    tgt = (h[0] - 1.1 * rv[0], h[1] - 1.1 * rv[1], h[2] - 0.25)
    key(S, SEA, (cam[0] + 2 * rv[0], cam[1] + 2 * rv[1], h[2] + 2.5), h, 1300, 'FFF0DC')
    S['camfill'].data.energy = 120
    shoot(S, (0, 0, 0), cam, tgt, 34)


NEW = (night_alone, rook_deck, shed_build, sail_calm, canary_leave, deck_swamped, rook_hatch, dive_cabin, rook_ducky, kit_spread, still_open,
       rain_catch, reef_under, school_follow, gun_snap, shark_under, raft_bump, flare_night, pump_night, fork_find, pencil_sextant, sun_beat,
       jetty_eve, desk_book, film_tank)
SHOTS3D.update({f.__name__: f for f in NEW})
STILLS = dict(thumb=photo_thumb)

# The Short's shots were timed for about a second each; here they run two to three times as long. Their acting is spread
# over the first 1.4 s of a shot (lt is slowed, never sped up) and every shot also swings a little round its own subject,
# so a held frame keeps moving. prm "orb": [degrees, dolly, rise] sets the swing for one shot.
SHORT_KINDS = set(SHOTS3D) - {f.__name__ for f in NEW}
SWING = dict(night_alone=3.0, sun_beat=3.0, canary_leave=2.0, reef_under=5.0, fork_find=4.0)


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
        mm = 1 - dolly * (k - 0.5)
        dx, dy = c[0] - tg[0], c[1] - tg[1]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * mm, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * mm, c[2] + rise * (k - 0.5))
    g.__name__ = f.__name__
    return g


for _n in SHORT_KINDS:
    SHOTS3D[_n] = _slowed(SHOTS3D[_n])


def _ship_aside(f, x0, x1, y):
    """In the wider 16:9 frame the Short's freighter sat straight behind the raft (or off the edge): move it to one side
    of the frame, crossing, so it reads beside him."""
    def g(S, k, t, lt):
        f(S, k, t, lt)
        S['ship'].location = at(SEA, lerp(x0, x1, k), y, -0.5)
    g.__name__ = f.__name__
    return g


SHOTS3D['ship_pass'] = _ship_aside(SHOTS3D['ship_pass'], -140, -95, 170)
SHOTS3D['rook_wave'] = _ship_aside(SHOTS3D['rook_wave'], -115, -85, 170)
SHOTS3D = {name: _swung(f, name) for name, f in SHOTS3D.items()}
