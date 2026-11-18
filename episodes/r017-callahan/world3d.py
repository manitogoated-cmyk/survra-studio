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
