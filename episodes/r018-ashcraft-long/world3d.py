"""Case 018 in 3D - Tami Oldham (later Ashcraft), 1983. She and her fiance Richard Sharp were delivering the yacht
Hazana from Tahiti to San Diego when Hurricane Raymond caught them on 12 October 1983. He sent her below; the yacht
went over; she was knocked out for about 27 hours. She woke in a flooded cabin with the masts gone and Richard gone,
his safety line still made fast. She pumped the cabin out, set a storm jib on a broken spinnaker pole and steered for
Hawaii by sextant and watch. Forty-one days after the storm a Japanese research ship found her off Hilo.

Built for this story only: a two-masted yacht with both masts snapped (deck, cockpit, coachroof), her flooded
cabin, an open ocean (day, storm, dusk, night, dawn), a light aircraft, two far-off ships, a research ship with a
searchlight, a breakwater with harbour lights under a dark island, and a small sloop for the last line.

Everything is a generic low-poly reconstruction. No vessel or aircraft carries a name, a flag, a number or a marking;
nobody's likeness is attempted; Richard Sharp is never shown."""
import math

import bpy
import numpy as np
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -3000)
SEA = (0.0, 0.0, 0.0)               # the yacht on the open ocean
CAB = (0.0, 3000.0, 0.0)            # her cabin
D = 1.3                             # deck height above the waterline (boat-local)
R = 2.25                            # top of the coachroof
HOST = {'rook_mast', 'rook_ring', 'stern_alone', 'pole_up', 'wide_sail', 'wave_up', 'rook_glass', 'rook_sun', 'helm_days',
        'ship_light', 'tow_in', 'rook_hatjump', 'line_dawn', 'rook_wrong', 'signoff'}
CAMFILL = {'*': 120, 'wake': 60, 'hatch_out': 140, 'helm_empty': 160, 'rook_mast': 200, 'storm_wave': 3000, 'storm_roll': 2500,
           'out_cold': 50, 'cleat_line': 80, 'rook_ring': 160, 'stern_alone': 400, 'engine_dead': 120, 'pump': 80, 'pole_up': 200,
           'sail_fill': 120, 'wide_sail': 0, 'plane_over': 200, 'wave_up': 300, 'plane_gone': 200, 'rook_glass': 320, 'sextant': 100,
           'rook_sun': 160, 'bilge_watch': 40, 'helm_days': 260, 'ship_light': 3000, 'her_light': 60,
           'tow_in': 2500, 'rook_hatjump': 240, 'line_dawn': 160, 'sloop': 0, 'rook_wrong': 160, 'signoff': 300}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN, HAIR = 'E6B48E', 'E2BC62'
SKIES = dict(                       # horizon, zenith, strength, sun watts, sun colour, sun direction
    day=('A8D2F0', '2C6CB4', 1.25, 3.6, 'FFF2DC', (0.5, 0.35, 0.78)),
    grey=('B4C2CC', '5E7488', 1.0, 2.0, 'F2F0EA', (0.4, 0.4, 0.8)),
    storm=('6A7A84', '1E262E', 0.95, 0.8, 'C8D4E0', (-0.3, -0.4, 0.85)),
    dusk=('F4A268', '2C3E72', 1.0, 2.2, 'FFAE78', (-0.85, -0.3, 0.16)),
    night=('24406A', '070C1A', 0.8, 1.1, 'A8C4F0', (-0.4, 0.3, 0.85)),
    dawn=('F8C49C', '5C82B4', 1.2, 2.6, 'FFD2A8', (0.8, -0.45, 0.2)),
    cabin=('1A2A30', '080C10', 0.35, 0.0, 'FFFFFF', (0, 0, 1)))
SEACOL = dict(day='1C5E96', grey='3A6078', storm='2C4C56', dusk='2A4470', night='0E1E38', dawn='3E6A94')
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


def tri(name, col, pts, par=None, rough=0.9):
    """A flat panel from three or four points (a sail)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in pts], [], [tuple(range(len(pts)))])
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(K.mat(col, rough))
    if par:
        o.parent = par
    return o


# ---------------------------------------------------------------- the ocean
def make_sea(S):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=72, y_subdivisions=72, size=300, location=SEA)
    g = bpy.context.object
    S['seamat'] = m = bpy.data.materials.new('sea18')
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.22
    g.data.materials.append(S['seamat'])
    n = len(g.data.vertices)
    co = np.zeros(n * 3, dtype=np.float32)
    g.data.vertices.foreach_get('co', co)
    S['sea'], S['seaco'] = g, co.reshape(n, 3).copy()
    deep = add('plane', '1C5E96', at(SEA, 0, 0, -1.2), size=9000)
    deep.data.materials[0] = S['seamat']
    S['deep'] = deep
    # one very large swell for the storm
    w = keep(empty(FAR))
    add('cube', '3A6C78', (0, 0, 0), rot=(0, PI / 4, 0), scale=(38, 260, 38), size=1, parent=w, rough=0.3)
    for i in range(44):
        add('cube', 'DCE8EC', (rnd(i, 1) * 5 - 2.5, -120 + 5.5 * i + rnd(i, 2) * 4, 26.2 + rnd(i, 3) * 1.4), rot=(rnd(i, 4), rnd(i, 5), rnd(i, 6)),
            scale=(2.5 + 3 * rnd(i, 7), 5 + 3 * rnd(i, 8), 1.4), size=1, parent=w, rough=1.0)
    S['swell'] = w
    S['spray'] = [keep(add('ico_sphere', 'E8F0F4', FAR, radius=0.5, subdivisions=1, rough=1.0)) for _ in range(18)]


def sea(S, t, amp=1.0, flow=0.0, col='day'):
    c = S['seaco']
    x, y = c[:, 0], c[:, 1] + flow * t
    z = amp * (0.34 * np.sin(0.11 * x + 0.07 * y + 1.3 * t) + 0.22 * np.sin(-0.06 * x + 0.16 * y + 1.9 * t + 1.0) + 0.09 * np.sin(0.31 * x + 0.23 * y + 2.6 * t))
    out = c.copy()
    out[:, 2] = z - 0.25 * amp
    S['sea'].data.vertices.foreach_set('co', out.ravel())
    S['sea'].data.update()
    S['seamat'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = K.hexc(SEACOL[col])


# ---------------------------------------------------------------- the yacht
def make_yacht(S):
    """Bow towards -Y. Both masts are snapped off; the main lies over the port side in a tangle of wire."""
    b = keep(empty(SEA))
    W_, T_, DK = 'ECE8DC', '2E5E8E', 'B48C5C'
    add('cube', W_, (0, 1, 0.35), scale=(7.0, 16, 1.9), size=1, parent=b)
    add('cylinder', W_, (0, -9, 0.35), rot=(0, 0, PI), radius=4.04, depth=1.9, vertices=3, parent=b)
    add('cube', T_, (0, 1, 0.95), scale=(7.06, 16.04, 0.3), size=1, parent=b)
    add('cylinder', T_, (0, -9, 0.95), rot=(0, 0, PI), radius=4.09, depth=0.3, vertices=3, parent=b)
    add('cube', '7A2E26', (0, 1, -0.9), scale=(6.2, 15, 0.7), size=1, parent=b)                       # bottom paint
    add('cube', '7A2E26', (0, 0.5, -2.4), scale=(0.5, 7, 2.6), size=1, parent=b)                      # keel
    add('cube', DK, (0, 1, D - 0.04), scale=(6.8, 15.9, 0.08), size=1, parent=b, rough=1.0)
    add('cylinder', DK, (0, -9, D - 0.04), rot=(0, 0, PI), radius=3.9, depth=0.08, vertices=3, parent=b, rough=1.0)
    for i in range(9):                                                                               # deck planking lines
        add('cube', '8E6A40', (-3.0 + 0.75 * i, 1, D + 0.01), scale=(0.04, 15.8, 0.02), size=1, parent=b)
    add('cube', W_, (0, -1.4, (D + R) / 2), scale=(4.4, 9.6, R - D), size=1, parent=b)               # coachroof
    add('cube', 'D8D2C2', (0, -1.4, R + 0.03), scale=(4.0, 9.2, 0.06), size=1, parent=b, rough=1.0)
    for s in (-1, 1):
        for j in range(4):
            add('cube', '1A2630', (s * 2.21, -4.6 + 2.0 * j, D + 0.5), scale=(0.04, 1.2, 0.36), size=1, parent=b, rough=0.2)
        add('cube', W_, (s * 2.75, 6.4, D + 0.3), scale=(0.35, 5.2, 0.6), size=1, parent=b)             # cockpit coamings
        add('cube', DK, (s * 1.9, 6.4, D + 0.38), scale=(1.2, 5.0, 0.2), size=1, parent=b, rough=1.0)   # cockpit seats
    add('cube', '2A2018', (0, 3.42, D + 0.45), scale=(1.5, 0.06, 1.3), size=1, parent=b)             # the companionway, a dark doorway
    add('cube', '8E6A40', (0, 0.9, R + 0.1), scale=(1.7, 1.6, 0.1), size=1, parent=b)                # its sliding hatch, pushed forward
    add('cube', '120C08', (0, 2.6, R + 0.045), scale=(1.6, 1.7, 0.06), size=1, parent=b)             # the open hatchway
    # wheel on a pedestal
    add('cube', 'D8D2C2', (0, 7.5, D + 0.7), scale=(0.34, 0.34, 1.4), size=1, parent=b)
    wh = empty((0, 7.72, D + 1.45), b, (PI / 2, 0, 0))
    add('torus', 'C8CED6', (0, 0, 0), major_radius=0.72, minor_radius=0.05, major_segments=14, minor_segments=4, parent=wh, rough=0.3)
    for i in range(3):
        add('cube', 'C8CED6', (0, 0, 0), rot=(0, 0, i * PI / 3), scale=(1.44, 0.06, 0.05), size=1, parent=wh, rough=0.3)
    S['wheel'] = wh
    # mast stumps, splintered
    for (x, y, z0, h_) in ((0, -3.6, R, 1.7), (0, 9.4, D, 1.0)):
        add('cylinder', 'D6D8DC', (x, y, z0 + h_ / 2), radius=0.3 if h_ > 1.2 else 0.22, depth=h_, vertices=8, parent=b, rough=0.4)
        for i in range(4):
            a = i * PI / 2 + 0.4
            add('cone', 'D6D8DC', (x + 0.16 * math.cos(a), y + 0.16 * math.sin(a), z0 + h_ + 0.2), rot=(0.3 * math.sin(a), -0.3 * math.cos(a), 0),
                radius1=0.12, radius2=0.0, depth=0.5 + 0.3 * rnd(i, 3), vertices=3, parent=b, rough=0.4)
    # the fallen mainmast over the port side, boom on the roof, wire everywhere
    bar(b, 'D6D8DC', (-0.6, -2.6, R + 0.35), (-7.5, 1.5, -0.6), 0.26, rough=0.4)
    bar(b, 'D6D8DC', (0.4, -2.0, R + 0.2), (1.6, 2.6, R + 0.25), 0.16, rough=0.4)
    for i, (p, q) in enumerate((((-3.4, -6, D + 0.9), (-5.5, 0.6, 0.3)), ((-0.4, -3.2, R + 1.2), (-3.4, 2.5, D + 0.1)), ((0.2, -3.3, R + 1.0), (3.3, -7.0, D + 0.9)),
                                ((-6.5, 1.0, 0.0), (-3.4, 4.5, D + 0.9)), ((1.8, 2.4, R + 0.3), (3.4, 5.5, D + 0.9)))):
        bar(b, '9AA2AC', p, q, 0.035, rough=0.3)
    tri('rag', 'DAD6C8', [(-1.0, -2.2, R + 0.2), (-5.6, 0.4, 0.2), (-3.6, 2.6, D + 0.2), (-0.2, 0.8, R + 0.1)], b)
    # lifelines: stanchions and two wires, some bent
    for s in (-1, 1):
        prev = None
        for j in range(7):
            y = -6.5 + 2.55 * j
            bent = (s < 0 and j in (2, 3)) or (s > 0 and j == 1)
            top = (s * 3.35 + (s * 0.5 if bent else 0), y + (0.4 if bent else 0), D + (0.45 if bent else 0.95))
            bar(b, 'C8CED6', (s * 3.35, y, D), top, 0.035, rough=0.3)
            if prev:
                bar(b, 'C8CED6', prev, top, 0.018, rough=0.3)
            prev = top
    bar(b, 'C8CED6', (-3.35, 8.8, D + 0.95), (3.35, 8.8, D + 0.95), 0.03, rough=0.3)                   # the stern rail
    for s in (-1, 1):
        bar(b, 'C8CED6', (s * 3.35, 8.8, D), (s * 3.35, 8.8, D + 0.95), 0.035, rough=0.3)
    # the cleat his safety line is made fast to
    S['cleat'] = CL = (-2.75, 5.3, D + 0.66)
    add('cube', 'C8CED6', (CL[0], CL[1], CL[2] + 0.05), scale=(0.14, 0.62, 0.08), size=1, parent=b, rough=0.25)
    add('cube', 'C8CED6', (CL[0], CL[1], CL[2] - 0.02), scale=(0.1, 0.22, 0.1), size=1, parent=b, rough=0.25)
    S['teth'] = [keep(add('cylinder', 'FF7A1A', FAR, radius=0.5, depth=1, vertices=6, parent=b, rough=0.8)) for _ in range(5)]
    S['ring'] = keep(empty(FAR, b))
    for i in range(7):                                                                               # a steel ring, sprung open
        a0, a1 = 0.5 + i * 0.75, 0.5 + (i + 1) * 0.75
        bar(S['ring'], 'D0D6DE', (0.2 * math.cos(a0), 0, 0.2 * math.sin(a0)), (0.2 * math.cos(a1), 0, 0.2 * math.sin(a1)), 0.045, rough=0.2)
    # the engine under a hatch in the cockpit floor
    S['ehatch'] = keep(empty((0, 5.0, D + 0.02), b))
    add('cube', '8E6A40', (0, 0.55, 0.03), scale=(1.4, 1.1, 0.07), size=1, parent=S['ehatch'])
    S['engine'] = keep(empty(FAR, b))
    add('cube', '14161A', (0, 0, -0.2), scale=(1.36, 1.06, 0.5), size=1, parent=S['engine'])
    add('cube', '8A2E22', (0, 0, 0.0), scale=(0.9, 0.7, 0.36), size=1, parent=S['engine'], rough=0.5)
    for i in range(4):
        add('cylinder', '50545C', (-0.3 + 0.2 * i, 0, 0.22), radius=0.07, depth=0.16, vertices=6, parent=S['engine'], rough=0.4)
    S['smoke'] = [keep(add('ico_sphere', 'A4A8B0', FAR, radius=0.3, subdivisions=1, parent=b, rough=1.0)) for _ in range(4)]
    # the jury rig: half a spinnaker pole and the storm jib
    S['pole'] = keep(empty(FAR, b))
    add('cylinder', 'C8CED6', (0, 0, 2.4), radius=0.1, depth=4.8, vertices=8, parent=S['pole'], rough=0.35)
    add('cube', '8A9098', (0, 0, 4.75), scale=(0.24, 0.24, 0.22), size=1, parent=S['pole'], rough=0.3)
    S['jib'] = keep(empty(FAR, b))
    tri('jib', 'F0E4C4', [(0, 0, 0), (0, 0, 4.3), (0.5, 3.6, 0.3)], S['jib'], 1.0)
    tri('jibtab', 'FF7A1A', [(0, 0, 3.4), (0, 0, 4.3), (0.1, 0.75, 3.46)], S['jib'], 1.0)
    S['stays'] = [keep(add('cylinder', '9AA2AC', FAR, radius=0.5, depth=1, vertices=6, parent=b, rough=0.3)) for _ in range(3)]
    S['tally'] = [keep(add('cube', 'F4F0E4', FAR, scale=(0.035, 0.012, 0.22), size=1, parent=b, rough=1.0)) for _ in range(12)]
    S['towl'] = keep(add('cylinder', 'D8CCA0', FAR, radius=0.5, depth=1, vertices=6, rough=1.0))
    S['boat'] = b


def make_cabin(S):
    """Her cabin, looking aft to the companionway: settees, a chart table, lockers burst open, half full of sea water."""
    c = empty(CAB)
    WD, WL = '7A5232', 'D8CDB8'
    add('cube', '4A3220', (0, -2, -0.05), scale=(6.6, 15, 0.1), size=1, parent=c)
    add('cube', WL, (0, -2, 4.3), scale=(6.6, 15, 0.1), size=1, parent=c)
    for s in (-1, 1):
        add('cube', WL, (s * 3.3, -2, 2.1), scale=(0.1, 15, 4.4), size=1, parent=c)
        add('cube', WD, (s * 2.5, -2.5, 0.55), scale=(1.5, 9, 1.1), size=1, parent=c)                  # settee base
        add('cube', '9E3C30', (s * 2.5, -2.5, 1.2), scale=(1.45, 8.8, 0.24), size=1, parent=c, rough=1.0)
        add('cube', '9E3C30', (s * 3.12, -2.5, 1.9), scale=(0.22, 8.8, 1.1), size=1, parent=c, rough=1.0)
        add('cube', WD, (s * 2.9, -2.5, 3.5), scale=(0.75, 9, 0.8), size=1, parent=c)                  # lockers above
        for j in range(3):
            add('cylinder', 'BFE4F4', (s * 3.24, -5.5 + 3.0 * j, 2.75), rot=(0, PI / 2, 0), radius=0.34, depth=0.05, vertices=10, parent=c, emit=2.2)
            add('torus', 'C89A3A', (s * 3.22, -5.5 + 3.0 * j, 2.75), rot=(0, PI / 2, 0), major_radius=0.37, minor_radius=0.045, major_segments=10,
                minor_segments=4, parent=c, rough=0.3)
    add('cube', WD, (0, -9.5, 2.1), scale=(6.6, 0.1, 4.4), size=1, parent=c)                          # forward bulkhead and its doorway
    add('cube', '1A120C', (0, -9.42, 1.6), scale=(1.5, 0.06, 3.2), size=1, parent=c)
    add('cube', WD, (-2.0, 5.5, 2.1), scale=(2.6, 0.1, 4.4), size=1, parent=c)                        # aft bulkhead, the companionway between
    add('cube', WD, (2.0, 5.5, 2.1), scale=(2.6, 0.1, 4.4), size=1, parent=c)
    add('cube', WD, (0, 5.5, 0.8), scale=(1.4, 0.1, 1.6), size=1, parent=c)
    for i in range(4):
        add('cube', '9A7248', (0, 5.2 - 0.32 * (3 - i), 0.5 + 0.75 * i), scale=(1.3, 0.34, 0.08), size=1, parent=c)
    S['hatchglow'] = add('plane', 'DCEBFF', (0, 5.9, 3.0), rot=(PI / 2, 0, 0), size=1, scale=(1.5, 2.7, 1), parent=c, emit=4.0)
    S['hatchl'] = light(at(CAB, 0, 5.0, 3.9), 0, 'E8F2FF', size=1.6, parent=None)
    S['hatchl'].rotation_euler = (-0.95, 0, 0)
    S['portl'] = [light(at(CAB, s * 2.9, -2.5, 2.8), 0, 'CFE8FF', size=1.2) for s in (-1, 1)]
    for l, s in zip(S['portl'], (-1, 1)):
        l.rotation_euler = (0, s * -1.2, 0)
    add('cube', WD, (2.35, 3.4, 1.5), scale=(1.8, 2.6, 0.12), size=1, parent=c)                       # chart table
    add('cube', 'EDE6D0', (2.3, 3.3, 1.58), rot=(0, 0, 0.2), scale=(1.2, 1.6, 0.02), size=1, parent=c, rough=1.0)
    add('cube', '2A2E34', (3.1, 3.4, 2.6), scale=(0.3, 1.9, 1.0), size=1, parent=c)                   # the dead radio and instruments
    for i in range(3):
        add('cube', '0C0E10', (2.93, 2.8 + 0.6 * i, 2.7), scale=(0.03, 0.42, 0.3), size=1, parent=c, rough=0.2)
    # the water and what floats in it
    S['cwater'] = add('plane', '2C6672', at(CAB, 0, -2, 0.9), size=1, scale=(6.5, 14.9, 1), rough=0.16)
    S['flot'] = []
    for i, (kind, col, sc) in enumerate((('cylinder', 'C8CED6', (0.36, 0.36, 0.5)), ('cylinder', 'D8B24A', (0.36, 0.36, 0.5)), ('cube', 'EDE6D0', (0.9, 0.65, 0.12)),
                                         ('cube', '9E3C30', (1.3, 1.0, 0.26)), ('cylinder', 'B8443A', (0.3, 0.3, 0.44)), ('cube', '3A6A9A', (0.7, 0.5, 0.14)),
                                         ('cube', 'E8E2D2', (0.55, 0.8, 0.05)), ('cylinder', 'C8CED6', (0.34, 0.34, 0.5)))):
        kw = dict(radius=0.5, depth=1, vertices=8) if kind == 'cylinder' else dict(size=1)
        S['flot'].append(add(kind, col, at(CAB, 0, 0, 0), scale=sc, rough=0.5, **kw))
    # the bilge pump lever beside the steps, and a lifted floorboard
    S['lever'] = empty(at(CAB, -1.25, 4.0, 0.9))
    add('cylinder', 'C8CED6', (0, 0, 0.9), radius=0.06, depth=1.8, vertices=6, parent=S['lever'], rough=0.3)
    add('cylinder', '1A1A1E', (0, 0, 1.8), rot=(0, PI / 2, 0), radius=0.09, depth=0.5, vertices=6, parent=S['lever'])
    S['bilge'] = keep(empty(FAR))
    add('cube', '0A1418', (0, 0, -0.02), scale=(1.6, 1.3, 0.04), size=1, parent=S['bilge'], rough=0.1)
    for s in (-1, 1):
        add('cube', '4A3220', (s * 0.85, 0, 0.06), scale=(0.1, 1.5, 0.16), size=1, parent=S['bilge'])
        add('cube', '4A3220', (0, s * 0.7, 0.06), scale=(1.8, 0.1, 0.16), size=1, parent=S['bilge'])
    add('cube', '6A4A2C', (-1.5, 0.2, 0.35), rot=(0, -0.7, 0.1), scale=(1.5, 1.25, 0.08), size=1, parent=S['bilge'])
    S['hand'] = K.Hand(SKIN, SKIN, 1.6)
    S['watch'] = keep(empty(FAR))
    add('cylinder', 'D0D6DE', (0, 0, 0), radius=0.22, depth=0.07, vertices=12, parent=S['watch'], rough=0.2)
    add('cylinder', 'F4F0E4', (0, 0, 0.04), radius=0.18, depth=0.02, vertices=12, parent=S['watch'], emit=0.8)
    add('cube', '14161A', (0, 0.05, 0.06), scale=(0.02, 0.13, 0.01), size=1, parent=S['watch'])
    add('cube', '14161A', (0.04, 0, 0.06), scale=(0.09, 0.02, 0.01), size=1, parent=S['watch'])
    for s in (-1, 1):
        add('cube', '4A3220', (0, s * 0.42, -0.02), rot=(s * 0.25, 0, 0), scale=(0.17, 0.46, 0.035), size=1, parent=S['watch'])
    S['cabin'] = c


def make_others(S):
    # a light twin-engined aircraft, nose towards -Y, plain grey
    p = keep(empty(FAR))
    add('cube', 'B8BEC6', (0, 0, 0), scale=(1.6, 13, 1.8), size=1, parent=p, rough=0.5)
    add('cube', '1A2630', (0, -4.6, 0.75), scale=(1.3, 2.2, 0.6), size=1, parent=p, rough=0.2)
    add('cube', 'B8BEC6', (0, -1.5, 1.0), scale=(21, 3.0, 0.3), size=1, parent=p, rough=0.5)
    add('cube', 'B8BEC6', (0, 6.0, 0.4), scale=(7, 1.8, 0.2), size=1, parent=p, rough=0.5)
    add('cube', 'B8BEC6', (0, 6.0, 1.6), scale=(0.25, 2.2, 2.6), size=1, parent=p, rough=0.5)
    S['props'] = []
    for s in (-1, 1):
        add('cylinder', '8A9098', (s * 4.2, -2.2, 0.6), rot=(PI / 2, 0, 0), radius=0.7, depth=3.2, vertices=8, parent=p, rough=0.5)
        e = empty((s * 4.2, -4.0, 0.6), p)
        for j in range(3):
            add('cube', '15171B', (0, 0, 0), rot=(0, j * PI / 3, 0), scale=(3.4, 0.06, 0.26), size=1, parent=e)
        S['props'].append(e)
    S['plane'] = p
    S['pshadow'] = keep(add('cube', '0A2440', FAR, scale=(21, 13, 0.02), size=1, rough=1.0, alpha=0.5))
    # two far-off ships
    S['far'] = []
    for i in range(2):
        f = keep(empty(FAR))
        add('cube', '2A3038', (0, 0, 1.5), scale=(5, 44, 3), size=1, parent=f)
        add('cube', 'C8CCD0', (0, 14, 5), scale=(4, 7, 4), size=1, parent=f)
        add('cylinder', '8A3A2A', (0, 15, 8.5), radius=1.0, depth=3, vertices=8, parent=f)
        S['far'].append(f)
    # the research ship: dark hull, white upperworks, a searchlight; no name, no flag
    r = keep(empty(FAR))
    add('cube', '1E3048', (0, 0, 3.0), scale=(13, 62, 7), size=1, parent=r)
    add('cylinder', '1E3048', (0, -31, 3.0), rot=(0, 0, PI), radius=7.5, depth=7, vertices=3, parent=r)
    add('cube', '8A2E26', (0, 0, -0.4), scale=(12.6, 61, 1.0), size=1, parent=r)
    add('cube', 'E8E6E0', (0, 8, 9.5), scale=(11, 22, 6), size=1, parent=r)
    add('cube', 'E8E6E0', (0, 3, 14.0), scale=(9, 9, 3.4), size=1, parent=r)
    for i in range(7):
        add('cube', 'FFE6A8', (-3.6 + 1.2 * i, -1.55, 14.3), scale=(0.8, 0.05, 1.0), size=1, parent=r, emit=5.0)
    for s in (-1, 1):
        for i in range(6):
            add('cylinder', 'FFE6A8', (s * 5.52, 0 + 3.0 * i, 9.6), rot=(0, PI / 2, 0), radius=0.4, depth=0.05, vertices=8, parent=r, emit=5.0)
    add('cylinder', 'D8D2C2', (0, 12, 19), radius=0.3, depth=8, vertices=6, parent=r)
    add('cube', 'FF4A3A', (0, 12, 23.2), scale=(0.5, 0.5, 0.5), size=1, parent=r, emit=12.0)
    add('cylinder', 'E8B030', (0, 17, 15.5), radius=1.6, depth=5.5, vertices=8, parent=r)
    bar(r, 'E8B030', (3, -18, 6.6), (5.5, -27, 15), 0.3)
    S['beamaim'] = empty(FAR)
    S['slamp'] = light((5.2, 1.5, 16.2), 0, 'F2F6FF', kind='SPOT', spot=0.2, target=S['beamaim'], parent=r)
    S['slens'] = add('cylinder', 'FFFFFF', (5.2, 1.3, 16.2), rot=(PI / 2, 0, 0), radius=0.6, depth=0.5, vertices=10, parent=r, emit=30.0)
    S['beam'] = keep(add('cone', 'F2F6FF', FAR, radius1=0.4, radius2=3.4, depth=1, vertices=10, emit=0.5, alpha=0.07))
    S['rship'] = r
    # Hilo: a dark island, the lights of a town, a breakwater with a light on its end
    h = keep(empty(FAR))
    for i, (x, y, rr, hh) in enumerate(((-260, -520, 420, 150), (160, -560, 520, 230), (520, -500, 380, 120), (-620, -480, 360, 90))):
        add('cone', '14242E', (x, y, hh / 2 - 2), radius1=rr, radius2=rr * 0.12, depth=hh, vertices=9, parent=h, rough=1.0)
    S['town'] = []
    for i in range(46):
        x = -330 + 660 * rnd(i, 21)
        S['town'].append(add('cube', ('FFD890', 'FFF0C8', 'FFB060')[i % 3], (x, -300 - 30 * rnd(i, 22), 2 + 16 * rnd(i, 23) ** 2), scale=(1.6, 1.6, 1.6), size=1, parent=h, emit=14.0))
    for i in range(16):
        add('cube', ('4A4E54', '3E4248', '565A60')[i % 3], (26 + 3 * rnd(i, 31), -30 - 9 * i, 0.4 + rnd(i, 32)), rot=(0.25 * rnd(i, 33), 0.25 * rnd(i, 34), 0.5 * rnd(i, 35)),
            scale=(8 + 3 * rnd(i, 36), 9, 4.5), size=1, parent=h, rough=1.0)
    add('cylinder', 'E8E6E0', (26, -28, 6.5), radius=1.0, depth=8, vertices=8, parent=h)
    S['bwlamp'] = add('cube', '3AF08A', (26, -28, 11.2), scale=(1.3, 1.3, 1.3), size=1, parent=h, emit=20.0)
    S['port'] = h
    # the sloop of the last line: one mast standing, two white sails
    s_ = keep(empty(FAR))
    add('cube', 'F2EEE4', (0, 0.6, 0.5), scale=(4.4, 10, 1.6), size=1, parent=s_)
    add('cylinder', 'F2EEE4', (0, -5.9, 0.5), rot=(0, 0, PI), radius=2.54, depth=1.6, vertices=3, parent=s_)
    add('cube', 'FF7A1A', (0, 0.6, 1.0), scale=(4.46, 10.04, 0.2), size=1, parent=s_)
    add('cube', 'B48C5C', (0, 0.6, 1.32), scale=(4.2, 9.8, 0.06), size=1, parent=s_, rough=1.0)
    add('cube', 'F2EEE4', (0, -1.0, 1.75), scale=(2.6, 4.6, 0.8), size=1, parent=s_)
    add('cylinder', 'D6D8DC', (0, -1.6, 8.6), radius=0.14, depth=14.6, vertices=8, parent=s_, rough=0.4)
    bar(s_, 'D6D8DC', (0, -1.5, 3.0), (0, 5.0, 3.0), 0.1, rough=0.4)
    tri('main', 'FBF8F0', [(0.05, -1.5, 3.2), (0.05, -1.5, 15.4), (0.6, 4.9, 3.2)], s_, 1.0)
    tri('fore', 'FBF8F0', [(-0.05, -1.8, 14.6), (-0.5, -8.2, 1.5), (-0.7, -2.2, 2.2)], s_, 1.0)
    S['sloop'] = s_
    S['stars'] = keep(empty(FAR))
    for i in range(70):
        a, e = rnd(i, 41) * 2 * PI, 0.1 + rnd(i, 42) * 1.3
        add('ico_sphere', 'FFFFFF', (800 * math.cos(a) * math.cos(e), 800 * math.sin(a) * math.cos(e), 800 * math.sin(e)), radius=1.6 + 2.2 * rnd(i, 43),
            subdivisions=1, parent=S['stars'], emit=9.0)


def make_things(S):
    # the sextant: a brass frame, an arc, an index arm, a small telescope
    x = keep(empty(FAR))
    B_ = 'C89A3A'
    A_, L_ = (0, 0, 0.42), 0.62
    ends = []
    for a in (-0.5, 0.5):
        e = (L_ * math.sin(a), 0, 0.42 - L_ * math.cos(a))
        bar(x, B_, A_, e, 0.03, rough=0.3)
        ends.append(e)
    for i in range(6):
        a0, a1 = -0.5 + i / 6, -0.5 + (i + 1) / 6
        bar(x, B_, (L_ * math.sin(a0), 0, 0.42 - L_ * math.cos(a0)), (L_ * math.sin(a1), 0, 0.42 - L_ * math.cos(a1)), 0.045, rough=0.3)
    S['index'] = empty(A_, x)
    add('cube', 'E8D08A', (0, -0.02, -0.31), scale=(0.05, 0.02, 0.66), size=1, parent=S['index'], rough=0.3)
    add('cube', 'DCEBFF', (0, -0.03, 0.0), scale=(0.14, 0.03, 0.12), size=1, parent=S['index'], rough=0.05)
    add('cylinder', '2A2E34', (0.2, 0.0, 0.12), rot=(0, PI / 2, 0), radius=0.045, depth=0.34, vertices=8, parent=x)
    add('cube', 'DCEBFF', (-0.22, -0.01, 0.12), scale=(0.03, 0.1, 0.12), size=1, parent=x, rough=0.05)
    add('cube', '4A3220', (0.05, 0.06, -0.02), scale=(0.07, 0.07, 0.3), size=1, parent=x)
    S['sext'] = x
    S['glint'] = keep(add('ico_sphere', 'FFF6D8', FAR, radius=0.035, subdivisions=1, emit=40.0))
    # Rook's small brass telescope
    g = keep(empty(FAR))
    add('cylinder', B_, (0, -0.3, 0), rot=(PI / 2, 0, 0), radius=0.07, depth=0.6, vertices=8, parent=g, rough=0.3)
    add('cylinder', 'E8D08A', (0, -0.8, 0), rot=(PI / 2, 0, 0), radius=0.095, depth=0.5, vertices=8, parent=g, rough=0.3)
    S['glass'] = g
    S['fea'] = [keep(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.36, vertices=4)) for _ in range(2)]


def tami_head(head):
    d = K.human_head(SKIN, HAIR)(head)
    add('cone', HAIR, (0, 0.36, -0.12), rot=(-0.5, 0, 0), radius1=0.15, radius2=0.03, depth=0.7, vertices=5, parent=head)        # a ponytail
    d['cut'] = add('cube', '8E2A26', (0.1, -0.268, 0.195), rot=(0, 0.35, 0), scale=(0.11, 0.03, 0.035), size=1, parent=head)       # the gash, kept small
    return d


def crew_head(skin, hair):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('ico_sphere', 'F2B531', (0, 0.0, 0.17), scale=(1, 1.05, 0.62), radius=0.34, subdivisions=1, parent=head, rough=0.5)
        add('cube', 'F2B531', (0, -0.3, 0.13), scale=(0.44, 0.2, 0.04), size=1, parent=head, rough=0.5)
        return d
    return fn


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_sea(S)
    make_yacht(S)
    make_cabin(S)
    make_others(S)
    make_things(S)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['tami'] = K.Rig(dict(top='E0684E', pants='2E4A70', hand=SKIN, boot='E4DCCC', fore=SKIN), tami_head)
    S['crew'] = [K.Rig(dict(top='E06A1E', pants='E06A1E', hand='D8B494', boot='1A1A1E', fore='E06A1E'), crew_head(sk, hr)) for sk, hr in (('D8B494', '17131A'), ('CFA680', '17131A'))]
    S['humans'] = [S['tami']] + S['crew']
    S['cast'] = [S['rook']] + S['humans']
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
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 9000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w18')
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
        rig.root.scale = (1, 1, 1)
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    for l in [S['sun'], S['keyl'], S['hatchl'], S['slamp']] + S['portl']:
        l.data.energy = 0
    S['hand'].place(FAR)
    S['sea'].location = SEA
    S['deep'].location = at(SEA, 0, 0, -1.2)
    S['cwater'].location = at(CAB, 0, -2, 0.9)
    S['cwater'].rotation_euler = (0, 0, 0)
    S['tami'].extra['cut'].hide_render = False
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
        k = dict(calm=1.0, wide=1.8, shut=0.07, tired=0.5, warm=0.8, sad=0.55, hard=0.6, squint=0.3).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.045 if f == 'wide' else -0.02 if f in ('hard', 'tired', 'squint') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide', 'tired') else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.2 if f == 'warm' else 0.13, 0.03, 0.035 + 0.14 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sky(S, a, b=None, k=0.0, stars=False):
    A, B = SKIES[a], SKIES[b or a]
    mixc = lambda i: tuple(lerp(x, y, k) for x, y in zip(K.hexc(A[i]), K.hexc(B[i])))
    S['skymix'].inputs[6].default_value = mixc(0)
    S['skymix'].inputs[7].default_value = mixc(1)
    S['bg'].inputs[1].default_value = lerp(A[2], B[2], k)
    S['sun'].data.energy = lerp(A[3], B[3], k)
    S['sun'].data.color = mixc(4)[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(lerp(u, v, k) * 500 for u, v in zip(A[5], B[5]))
    S['starson'] = stars


def shoot(S, o, pos, look, lens=40, roll=0.0):
    p = at(o, *pos)
    S['camrig'].location, S['camtgt'].location = p, at(o, *look)
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    S['stars'].location = p if S['starson'] else FAR


def key(S, o, pos, look, watts, col='FFE8D0'):
    S['keyl'].location, S['keytgt'].location = at(o, *pos), at(o, *look)
    S['keyl'].data.energy, S['keyl'].data.color = watts, K.hexc(col)[:3]


def afloat(S, t, amp=1.0, col='day', flow=0.0, roll=0.0, pitch=0.0, lift=0.0, yaw=0.0):
    """The yacht on the swell."""
    sea(S, t, amp, flow, col)
    S['boat'].location = at(SEA, 0, 0, 0.12 * amp * math.sin(1.3 * t) + lift)
    S['boat'].rotation_euler = (0.035 * amp * math.sin(1.1 * t + 1) + pitch, 0.05 * amp * math.sin(0.9 * t) + roll, yaw)
    S['wheel'].rotation_euler = (PI / 2, 0.5 * math.sin(t * 1.7), 0)


def aboard(S, rig, x, y, z=D, yaw=0.0, pose=None, face=None, pitch=0.0):
    rig.root.parent = S['boat']
    rig.place((x, y, z), yaw, pitch)
    rig.apply(pose or P())
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def tether(S, pts, ring=True):
    """His safety line: from the cleat through the given points (boat-local)."""
    pts = [S['cleat']] + list(pts)
    for i, o in enumerate(S['teth']):
        if i + 1 < len(pts):
            span(o, pts[i], pts[i + 1], 0.085)
        else:
            o.location = FAR
    if ring:
        S['ring'].location = pts[-1]
        S['ring'].rotation_euler = (0.3, 0.2, 0.6)
        S['ring'].scale = (1.25, 1.25, 1.25)


def slack_line(S, t):
    """The line as she finds it: off the cleat, along the cockpit seat and away over the stern."""
    sw = 0.2 * math.sin(t * 1.6)
    tether(S, [(-2.3, 6.0, D + 0.52), (-2.25, 7.7, D + 0.52), (-2.6, 8.85, D + 0.3), (-2.7 + sw, 9.25, 0.1)], ring=False)


def jury(S, t, up=1.0, fill=1.0):
    """Half a spinnaker pole stepped ahead of the stump, the storm jib set on it."""
    base = (0.0, -5.4, R)
    S['pole'].location = base
    S['pole'].rotation_euler = (lerp(-1.35, -0.08, sm(up)), 0, 0)
    if up >= 1.0:
        for o, q in zip(S['stays'], ((-3.3, -3.9, D + 0.9), (3.3, -3.9, D + 0.9), (0, -11.5, D + 0.3))):
            span(o, (base[0], base[1] + 0.38, base[2] + 4.75), q, 0.025)
    if fill > 0:
        S['jib'].location = (base[0], base[1] + 0.3, base[2] + 0.35)
        S['jib'].rotation_euler = (-0.08, 0, 0)
        fl = 0.12 * math.sin(t * 9) * (1.3 - fill) + 0.04 * math.sin(t * 5)
        S['jib'].scale = (2.2 * fill + 6 * fl, lerp(0.25, 1.0, fill), lerp(0.2, 1.0, sm(fill * 1.4)))


def cabin(S, t, level=0.9, hatch=900, ports=160, slosh=1.0):
    sky(S, 'cabin')
    S['hatchl'].data.energy = hatch
    for l in S['portl']:
        l.data.energy = ports
    S['cwater'].location = at(CAB, 0, -2, level + 0.03 * math.sin(t * 2.2))
    S['cwater'].rotation_euler = (0.012 * slosh * math.sin(t * 1.7), 0.03 * slosh * math.sin(t * 1.3), 0)
    spots = ((-0.6, -4.2), (0.9, -1.6), (-0.2, 0.6), (0.5, -6.4), (-1.1, 2.4), (1.1, 1.5), (0.2, -3.0), (-0.9, -7.2))
    for i, o in enumerate(S['flot']):
        x, y = spots[i]
        o.location = at(CAB, x + 0.25 * math.sin(t * 0.9 + i * 2), y + 0.3 * math.sin(t * 0.7 + i), level - 0.08 + 0.05 * math.sin(t * 2.4 + i * 1.3))
        o.rotation_euler = (PI / 2 if i in (0, 4) else 0.06 * math.sin(t * 2 + i), 0.1 * math.sin(t * 1.6 + i), i * 1.1 + 0.3 * math.sin(t * 0.8 + i))
    S['lever'].rotation_euler = (0.0, 0, 0)


COUCH = dict(aL=(0.05, 0.45, 0.3), aR=(0.25, 0.2, 1.4, 0.8), lL=(0.35, 0.5), lR=(0.1, 0.3), head=(0.0, 0.3))


def on_settee(S, t, wake=0.0):
    """She lies where the sea left her, across the port settee, the water lapping at the cushion."""
    m = S['tami']
    m.place(at(CAB, -1.95, -5.3, 1.62 + 0.25 * sm(wake)), 0.0, -PI / 2 + 0.45 * sm(wake))
    m.apply(blend(P('stand', **COUCH), P('stand', aL=(-0.5, 0.5, 0.4), aR=(-0.4, 0.4, 0.5), lL=(0.5, 0.7), lR=(0.2, 0.4), head=(0.3, -0.25)), wake))
    return m


def thead(S):
    return wpos(S['tami'].head)


def rhead(S):
    return wpos(S['rook'].head)


def port(S, y=0.0, x=0.0, lamps=1.0, t=0.0):
    S['port'].location = at(SEA, x, y, 0)
    for i, o in enumerate(S['town']):
        o.scale = tuple(1.6 * (1 if rnd(i, 5) < lamps else 0.01) * (0.8 + 0.3 * math.sin(t * (3 + 4 * rnd(i, 6)) + i)) for _ in range(3))


def beam_on(S, src, aim, watts=250000):
    S['beamaim'].location = aim
    S['slamp'].data.energy = watts
    a, b = Vector(src), Vector(aim)
    d = b - a
    S['beam'].location = (a + b) / 2
    S['beam'].rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    S['beam'].scale = (1, 1, d.length)


def feather(S, pos, u):
    for i, f in enumerate(S['fea']):
        f.location = (pos[0] + (0.5 + 0.4 * i) * u * (1 if i else -1), pos[1] - 0.3 * u, pos[2] - 1.6 * u * u + 0.5 * u + 0.2 * math.sin(u * 9 + i))
        f.rotation_euler = (u * 5 + i, u * 3, u * 4)


STEER = dict(aL=(1.15, 0.15, 0.5), aR=(1.15, 0.15, 0.5), lL=(0.1, 0.1), lR=(-0.1, 0.1))
KNEEL = dict(lL=(0.25, 1.55), lR=(1.35, 1.45), lift=-0.72)


def helm(S, t, face='tired', turn=0.0, nod=0.0):
    s = 0.12 * math.sin(t * 1.7)
    return aboard(S, S['tami'], 0, 8.35, D, 0.0, P('stand', **dict(STEER, aL=(1.15 + s, 0.15, 0.5), aR=(1.15 - s, 0.15, 0.5), head=(nod, turn))), face)


def bloc(S, w):
    bpy.context.view_layer.update()
    return tuple(S['boat'].matrix_world.inverted() @ Vector(w))


CROUCH = dict(lL=(1.1, 1.7), lR=(1.1, 1.7), lift=-0.5, lean=0.4)
INHATCH = R - 1.25


# ---------------------------------------------------------------- the hook: she wakes, the masts are gone, so is he
def wake(S, k, t, lt):
    """Close on her face as she lies across the settee in the flooded cabin, a gash on her forehead. Her eyes open. First and last shot."""
    d = lt / k if k > 1e-3 else 1.2
    u = (1 - k) * d if S['prm'].get('loop') else lt
    cabin(S, t, 1.2, 1100, 220, 1.6)
    w = sm((u - 0.5) / 0.6)
    m = on_settee(S, t, w * 0.55)
    m.face = 'shut' if u < 0.28 else 'wide'
    m.jawv = 0.5 * w
    h = thead(S)
    q = sm(u / 1.2)
    shoot(S, (0, 0, 0), (h[0] + lerp(0.55, 0.9, q), h[1] - lerp(1.0, 1.5, q), h[2] + lerp(1.75, 1.6, q)), (h[0] + 0.12, h[1] - 0.1, h[2]), 38)


def hatch_out(S, k, t, lt):
    """She comes up through the hatch into daylight and stops: the mainmast is a splintered stump, the rest of it over the side in a tangle of wire."""
    sky(S, 'grey')
    afloat(S, t, 1.2, 'grey')
    slack_line(S, t)
    u = sm(lt / 0.6)
    aboard(S, S['tami'], 0, 2.6, lerp(INHATCH - 1.2, INHATCH, u), 0.0,
           P('stand', aL=(1.1, 0.5, 0.9), aR=(1.1, 0.5, 0.9), head=(-0.15, lerp(0.5, -0.5, sm((lt - 0.5) / 0.6)))), 'wide')
    S['tami'].jawv = 0.4
    shoot(S, SEA, (lerp(2.4, 2.0, k), lerp(-5.9, -5.2, k), R + lerp(1.3, 1.7, k)), (-0.3, 1.0, R + 1.25), 30)


def helm_empty(S, k, t, lt):
    """From the stern: the wheel turns by itself, the cockpit is empty. She twists round in the hatch and calls out."""
    sky(S, 'grey')
    afloat(S, t, 1.2, 'grey')
    slack_line(S, t)
    S['wheel'].rotation_euler = (PI / 2, 1.4 * math.sin(t * 2.4), 0)
    aboard(S, S['tami'], 0, 2.6, INHATCH, PI + 0.5 * math.sin(lt * 3.5), P('stand', aL=(0.9, 0.7, 0.8), aR=(1.2, 0.6, 0.7), head=(-0.05, 0.3 * math.sin(lt * 3.5 + 1))), 'wide')
    S['tami'].jawv = 0.5 + 0.4 * math.sin(lt * 9)
    shoot(S, SEA, (lerp(1.9, 1.2, k), lerp(10.6, 9.9, k), D + lerp(2.3, 2.0, k)), (0.0, 4.6, D + 1.7), 30)


def rook_mast(S, k, t, lt):
    """Rook is standing on the stump of the mainmast, arms folded, brim low. Behind and below him she turns in the hatch, looking for someone."""
    sky(S, 'grey')
    afloat(S, t, 1.2, 'grey')
    slack_line(S, t)
    aboard(S, S['tami'], 0, 2.6, INHATCH, PI * sm(lt / 0.9), P('stand', aL=(0.9, 0.7, 0.8), aR=(0.9, 0.7, 0.8), head=(0.0, 0.4)), 'wide')
    aboard(S, S['rook'], 0, -3.6, R + 1.9, 0.25, blend(P('cross'), P('cross', head=(0.25, -0.3)), (lt - 0.5) / 0.4), 'low')
    S['hat_tip'] = 0.5
    shoot(S, SEA, (lerp(2.6, 2.0, k), lerp(-8.4, -7.6, k), R + lerp(3.3, 3.6, k)), (0.2, -3.0, R + 3.5), 30)


# ---------------------------------------------------------------- what happened: the hurricane, 27 hours, the line
def storm_wave(S, k, t, lt):
    """Two days earlier: a black sky, and a wall of water coming at the small yacht from the side."""
    sky(S, 'storm')
    afloat(S, t * 1.6, 3.0, 'storm', roll=lerp(0.1, 0.45, k), lift=lerp(0.5, 3.0, k))
    S['swell'].location = at(SEA, lerp(-64, -34, k), 0, -9)
    fl = 1.0 if (t * 3.1) % 1 < 0.12 else 0.0
    key(S, SEA, (10, 20, 40), (0, 0, 0), 60000 * fl + 9000, 'C8D8F0')
    shoot(S, SEA, (lerp(27, 24, k), lerp(13, 11, k), 2.2), (-8, 0, lerp(7, 9, k)), 22)


def storm_roll(S, k, t, lt):
    """The wave takes her: the yacht is thrown onto her side and on over, keel to the sky, in a burst of white water."""
    sky(S, 'storm')
    u = sm(k * 1.1)
    afloat(S, t * 1.6, 3.0, 'storm', roll=lerp(0.5, 2.9, u), lift=lerp(3.0, 7.0, math.sin(PI * u)) - 2.0 * u)
    S['swell'].location = at(SEA, lerp(-34, -17, k), 0, lerp(-9, -13, k))
    for i, o in enumerate(S['spray']):
        a = rnd(i, 51) * 2 * PI
        r_ = (3 + 9 * rnd(i, 52)) * u
        o.location = at(SEA, r_ * math.cos(a) - 2, r_ * math.sin(a) * 1.6, 3 + 9 * rnd(i, 53) * math.sin(PI * min(1, u * 1.2)) + 3 * u)
        o.scale = tuple(0.8 + 2.2 * rnd(i, 54) for _ in range(3))
    key(S, SEA, (10, -20, 40), (0, 0, 0), 14000, 'C8D8F0')
    shoot(S, SEA, (lerp(19, 16, k), lerp(-17, -15, k), 3.0), (0, 0, lerp(4, 6, u)), 24)


def out_cold(S, k, t, lt):
    """From high in the cabin: she lies where she was thrown, not moving, while the light in the portholes goes from day to night and back to day."""
    day = 0.5 + 0.5 * math.cos(2 * PI * k * 1.15)
    cabin(S, t, 1.2, 150 + 1000 * day, 30 + 260 * day, 2.2)
    S['hatchglow'].scale = (1.5, 2.7 * (0.25 + 0.75 * day), 1)
    m = on_settee(S, t, 0.0)
    m.face = 'shut'
    shoot(S, CAB, (lerp(1.0, 0.5, k), lerp(0.6, -0.9, k), lerp(3.8, 3.5, k)), (-1.8, -4.9, 1.6), 24)


def cleat_line(S, k, t, lt):
    """Close on a cleat on the cockpit coaming: an orange safety line is still made fast to it and runs away over the side. Her hand closes on it."""
    sky(S, 'grey')
    afloat(S, t, 1.2, 'grey')
    slack_line(S, t)
    u = sm((lt - 0.25) / 0.6)
    aboard(S, S['tami'], -1.35, 6.75, D, facing((-1.35, 6.75), (-3.2, 6.3)),
           blend(P('stand', **KNEEL), P('stand', **dict(KNEEL, aR=(1.25, 0.1, 0.35), lean=0.45, head=(0.3, 0.0))), u), 'sad')
    shoot(S, SEA, (lerp(-1.4, -1.7, k), lerp(3.6, 4.2, k), D + lerp(1.45, 1.25, k)), (lerp(-2.8, -3.0, k), lerp(5.5, 6.3, k), D + 0.6), 40)


def rook_ring(S, k, t, lt):
    """Detective work, done quietly: Rook, at the stern, lifts the free end of the line into view. The steel ring on it has been pulled open. He lowers his head."""
    sky(S, 'grey')
    afloat(S, t, 1.2, 'grey')
    u, v = sm(lt / 0.5), sm((lt - 1.0) / 0.4)
    rk = aboard(S, S['rook'], -2.1, 8.1, D, facing((-2.1, 8.1), (0.3, 5.9)),
                blend(P('stand', aR=(0.5, 0.2, 0.5)), P('stand', aR=(0.85, 0.8, 0.9, 0.2), aL=(0.3, 0.15, 0.4), head=(lerp(0.05, 0.45, v), -0.45)), u), 'sad')
    hw = bloc(S, wpos(rk.hands[1], (0, 0, -0.25)))
    tether(S, [(-2.3, 6.0, D + 0.52), (-2.3, 7.0, D + 0.5), hw])
    shoot(S, SEA, (lerp(0.5, 0.2, k), lerp(5.5, 5.9, k), D + lerp(1.3, 1.6, k)), (-1.9, 8.1, D + 1.75), 32)


def stern_alone(S, k, t, lt):
    """She stands at the stern rail and looks back down the empty sea. Behind her Rook has his hat off. The camera pulls away and up: nothing but water."""
    sky(S, 'grey')
    afloat(S, t, 1.2, 'grey')
    slack_line(S, t)
    aboard(S, S['tami'], -1.3, 8.4, D, PI, P('stand', aL=(0.75, 0.25, 0.3), aR=(0.75, 0.25, 0.3), head=(lerp(-0.05, 0.4, sm(k * 1.3)), 0.0)), 'sad')
    aboard(S, S['rook'], 1.4, 6.3, D, PI - 0.3, P('stand', aL=(0.6, -0.2, 2.0, 1.0), head=(0.4, 0.0)), 'sad')
    S['hat_off'] = 1.0
    shoot(S, SEA, (lerp(0.6, 1.6, k), lerp(12.5, 18.5, k), D + lerp(1.9, 5.0, k)), (-0.3, 7.4, D + 2.0), 34)


# ---------------------------------------------------------------- the work: pump, pole, sail
def engine_dead(S, k, t, lt):
    """Cockpit: the engine hatch is up. She turns the key; the engine coughs a puff of smoke and stops. Her head drops."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day')
    slack_line(S, t)
    S['ehatch'].rotation_euler = (1.15, 0, 0)
    S['engine'].location = (0, 5.55, D - 0.02 + 0.03 * math.sin(lt * 40) * (1 - sm(lt / 0.6)))
    for i, o in enumerate(S['smoke']):
        u = max(0.0, min(1.0, (lt - 0.12 * i) / 0.9))
        o.location = (0.2 * math.sin(i * 2.0) + 0.3 * u, 5.55, D + 0.3 + 2.6 * u) if u > 0 else FAR
        o.scale = tuple(0.35 + 0.75 * u for _ in range(3))
    v = sm((lt - 0.55) / 0.35)
    aboard(S, S['tami'], 1.45, 6.0, D, facing((1.45, 6.0), (0.0, 5.6)),
           blend(P('stand', **dict(KNEEL, aR=(1.2, 0.1, 0.5), lean=0.3)), P('stand', **dict(KNEEL, aR=(0.5, 0.1, 1.2), aL=(0.4, 0.1, 1.0), lean=0.45, head=(0.5, 0.0))), v),
           'tired' if v > 0.5 else 'hard')
    shoot(S, SEA, (lerp(-2.9, -2.5, k), lerp(8.2, 7.9, k), D + lerp(2.4, 2.1, k)), (0.5, 5.7, D + 1.0), 34)


def pump(S, k, t, lt):
    """Below: she throws her weight on the bilge pump lever, back and forth, jaw set. The water in the cabin is going down."""
    cabin(S, t, lerp(1.05, 0.5, k), 1100, 200, 1.0)
    a = math.sin(t * 8)
    S['lever'].rotation_euler = (0.5 * a, 0, 0.75)
    m = S['tami']
    m.place(at(CAB, -0.35, 2.75, 0.0), facing((-0.35, 2.75), (-1.25, 4.0)))
    m.apply(P('stand', aL=(1.15 + 0.3 * a, 0.05, 0.5 - 0.3 * a), aR=(1.15 + 0.3 * a, 0.05, 0.5 - 0.3 * a), lean=0.22 + 0.2 * a, lL=(0.3, 0.3), lR=(-0.3, 0.2), head=(-0.1, 0.0)))
    m.face, m.jawv = 'hard', 0.3
    shoot(S, CAB, (lerp(-0.95, -0.85, k), lerp(5.3, 5.25, k), lerp(3.0, 2.7, k)), (-0.45, 2.8, 2.3), 26)


def pole_up(S, k, t, lt):
    """On the coachroof: she walks the broken spinnaker pole upright, hand over hand. Rook is down on one knee, holding its foot against the stump."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day')
    u = sm(k * 1.15)
    jury(S, t, u, 0.0)
    aboard(S, S['tami'], 1.1, -3.4 - 0.9 * u, R, facing((1.1, -3.6), (0.0, -5.6)),
           blend(P('stand', aL=(0.8, 0.2, 0.6), aR=(0.9, 0.2, 0.6), lean=0.45, lL=(0.5, 0.4), lR=(-0.3, 0.2)),
                 P('up', aL=(2.3, 0.1, 0.5), aR=(2.5, 0.1, 0.4), lean=0.1, head=(-0.45, 0.0)), u), 'hard')
    aboard(S, S['rook'], -1.25, -5.5, R, facing((-1.25, -5.5), (0.0, -5.4)), P('stand', **dict(CROUCH, aL=(1.1, 0.0, 0.5), aR=(1.1, 0.0, 0.5), head=(-0.3 * u, 0.0))), 'calm')
    shoot(S, SEA, (lerp(5.6, 4.8, k), lerp(-10.5, -9.6, k), R + lerp(0.9, 1.5, k)), (0.0, -4.7, R + lerp(1.6, 2.5, k)), 28)


def sail_fill(S, k, t, lt):
    """The storm jib goes up the pole, shakes, and fills. She hauls on the halyard and looks up at it."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day', flow=3 * k)
    f = sm(k * 1.3)
    jury(S, t, 1.0, max(0.05, f))
    a = math.sin(t * 9) * (1 - f)
    aboard(S, S['tami'], 1.5, -2.6, R, facing((1.5, -2.6), (5.0, -7.5)),
           P('up', aL=(2.2 + 0.5 * a, 0.15, 0.6), aR=(2.2 - 0.5 * a, 0.15, 0.6), lean=-0.1, head=(-0.45, 0.7)), 'warm' if f > 0.8 else 'hard')
    shoot(S, SEA, (lerp(7.2, 6.4, k), lerp(-7.4, -6.6, k), R + lerp(0.5, 0.9, k)), (0.3, -3.9, R + lerp(1.9, 2.5, k)), 28)


def wide_sail(S, k, t, lt):
    """Wide, from the side: the dismasted yacht under one small sail, moving. She is at the wheel; Rook stands on the roof, a wing shading his eyes."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day', flow=7)
    jury(S, t, 1.0, 1.0)
    helm(S, t)
    aboard(S, S['rook'], 0.9, -0.6, R, 0.2, P('hat', head=(-0.05, 0.3 * math.sin(t * 0.9))), 'calm')
    shoot(S, SEA, (lerp(34, 30, k), lerp(-6, -10, k), lerp(4.2, 3.4, k)), (0, 0.5, 3.6), 30)


# ---------------------------------------------------------------- the re-hook: nobody sees her
def fly(S, pos, yaw=0.0, t=0.0, bank=0.0):
    S['plane'].location, S['plane'].rotation_euler = at(SEA, *pos), (0.04, bank, yaw)
    for e in S['props']:
        e.rotation_euler = (0, t * 40, 0)


def plane_over(S, k, t, lt):
    """From the roof, looking aft and up: an aircraft comes in low over the stern, straight at us, growing fast. At the wheel she throws her head back."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day', flow=7)
    slack_line(S, t)
    u = sm((lt - 0.2) / 0.4)
    aboard(S, S['tami'], 0, 8.35, D, 0.0, blend(P('stand', **STEER), P('up', aL=(2.6, 0.5, 0.2), aR=(2.6, 0.5, 0.2), head=(-0.55, 0.0)), u), 'wide')
    S['tami'].jawv = 0.7 * u
    fly(S, (2.5, lerp(170, 2, k), lerp(30, 17, k)), 0.0, t)
    shoot(S, SEA, (lerp(1.7, 1.4, k), lerp(4.4, 4.9, k), D + 1.0), (0.3, 9.0, lerp(5.2, 6.4, k)), 22)


def wave_up(S, k, t, lt):
    """From the aircraft: a small white hull on a very large sea. Two figures on the roof, jumping, arms going: her, and Rook waving his hat."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day', flow=7)
    jury(S, t, 1.0, 1.0)
    a = math.sin(t * 11)
    hop = 0.25 * abs(math.sin(t * 6))
    aboard(S, S['tami'], 0.7, 0.4, R + hop, facing((0.7, 0.4), (5, 9)), P('up', aL=(2.7, 0.5 + 0.4 * a, 0.2), aR=(2.7, 0.5 - 0.4 * a, 0.2), head=(-0.75, 0.0)), 'wide')
    S['tami'].jawv = 0.9
    aboard(S, S['rook'], -1.0, -1.1, R + 0.25 * abs(math.sin(t * 6 + 1)), facing((-1.0, -1.1), (5, 9)),
           P('up', aL=(2.7, 0.4 - 0.4 * a, 0.2), aR=(2.8, 0.5 + 0.5 * a, 0.3), head=(-0.75, 0.0)), 'shocked')
    shoot(S, SEA, (lerp(5, 9, k), lerp(8, 15, k), lerp(15, 27, k)), (0, -1.0, 2.0), 32, lerp(0.0, 0.18, k))


def plane_gone(S, k, t, lt):
    """Over her shoulder: the aircraft is already small, and getting smaller. Her arms come down. She turns her head; she is not shouting any more."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day', flow=7)
    jury(S, t, 1.0, 1.0)
    u = sm(k * 1.3)
    aboard(S, S['tami'], 2.1, -0.3, R, 0.15, blend(P('up', aL=(2.7, 0.5, 0.2), aR=(2.7, 0.5, 0.2), head=(-0.5, 0.0)), P('stand', head=(0.15, 1.25)), u), 'sad')
    fly(S, (lerp(-12, -44, k), lerp(-55, -200, k), lerp(17, 30, k)), 0.1, t, -0.15)
    shoot(S, SEA, (lerp(2.6, 2.2, k), lerp(3.8, 3.2, k), R + lerp(2.5, 2.8, k)), (-3.0, -30, lerp(8.5, 10, k)), 34)


def rook_glass(S, k, t, lt):
    """At the bow, over his shoulder: Rook has a small brass telescope to his eye. On the horizon two ships cross, a long way off, and keep going.
    He lowers the glass and turns his head back to us; his brows have dropped."""
    sky(S, 'grey')
    afloat(S, t, 1.0, 'grey', flow=7)
    jury(S, t, 1.0, 1.0)
    v = sm((lt - 0.8) / 0.35)
    rk = aboard(S, S['rook'], 1.3, -8.4, D, facing((1.3, -8.4), (-196, -2.4)),
                blend(P('stand', aR=(1.45, 0.35, 1.9, 0.5), aL=(0.3, 0.2, 0.5), head=(-0.05, 0.0)), P('stand', aR=(0.4, 0.2, 0.5), head=(0.2, -1.1)), v), 'sad' if v > 0.5 else 'calm')
    g = S['glass']
    g.parent = rk.head
    g.location = (lerp(0.16, 0.5, v), lerp(-0.32, -0.3, v), lerp(0.07, -1.5, v))
    g.rotation_euler = (lerp(0.0, -1.2, v), 0, 0)
    for i, (x, y) in enumerate(((-196, -2.4), (-235, -30))):
        S['far'][i].location = at(SEA, x, y - 7 * lt, 0)
    shoot(S, SEA, (lerp(4.5, 4.3, k), lerp(-9.7, -9.5, k), D + lerp(1.9, 2.1, k)), (-40.1, -1.6, lerp(4.2, 3.8, k)), 24)


# ---------------------------------------------------------------- steering for Hawaii
SUNDIR = (0.82, 0.57)


def with_sextant(S, t, x, y, nod=-0.1):
    m = aboard(S, S['tami'], x, y, R, facing((0, 0), SUNDIR), P('stand', aR=(1.35, 0.35, 1.75, 0.5), aL=(1.2, -0.1, 1.5, 0.6), head=(nod, 0.0)), 'squint')
    sx = S['sext']
    sx.parent = m.head
    sx.location = (0.105, -0.74, 0.03)
    sx.rotation_euler = (0, 0, PI / 2)
    S['index'].rotation_euler = (0, 0.25 + 0.2 * math.sin(t * 2.2), 0)
    gp = wpos(sx, (-0.22, 0.02, 0.12))
    S['glint'].location = gp
    S['glint'].scale = tuple(0.6 + 0.9 * abs(math.sin(t * 5.3)) for _ in range(3))
    return m


def sextant(S, k, t, lt):
    """Close on her face: a brass sextant at her eye, the arm moving a hair at a time, the sun flashing in its mirror."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day', flow=7)
    jury(S, t, 1.0, 1.0)
    with_sextant(S, t, 0.5, 1.4)
    h = thead(S)
    a = math.atan2(SUNDIR[1], SUNDIR[0]) - lerp(1.0, 0.8, k)
    shoot(S, (0, 0, 0), (h[0] + 2.7 * math.cos(a), h[1] + 2.7 * math.sin(a), h[2] + 0.25), (h[0] + 0.3 * SUNDIR[0], h[1] + 0.3 * SUNDIR[1], h[2]), 48)


def rook_sun(S, k, t, lt):
    """Two-shot: she takes the sight; beside her Rook taps his beak, follows the line of the telescope up to the sun, then looks at her and nods once."""
    sky(S, 'day')
    afloat(S, t, 1.0, 'day', flow=7)
    jury(S, t, 1.0, 1.0)
    with_sextant(S, t, 0.5, 1.4)
    v = sm((lt - 0.6) / 0.3)
    aboard(S, S['rook'], -0.55, 0.15, R, facing((0, 0), SUNDIR) + 0.25, blend(P('tap', head=(-0.3, -0.25)), P('tap', head=(0.12 + 0.1 * math.sin(lt * 9), 0.7)), v), 'soft' if v > 0.5 else 'calm')
    a = math.atan2(SUNDIR[1], SUNDIR[0]) - lerp(0.55, 0.4, k)
    shoot(S, SEA, (0.1 + 7.2 * math.cos(a), 0.8 + 7.2 * math.sin(a), R + 2.5), (0.1, 0.75, R + 2.2), 34)


def bilge_watch(S, k, t, lt):
    """Below, a floorboard up: her hand comes out of the black bilge water with a wristwatch, dripping. It is still going."""
    cabin(S, t, 0.2, 900, 160, 0.5)
    S['bilge'].location = at(CAB, 0.2, -1.2, 0.22)
    u = sm(lt / 0.7)
    hp = at(CAB, 0.25, -1.15, lerp(0.75, 1.75, u))
    S['hand'].place(hp, (0.0, -0.25, -PI / 2 - 0.3))
    S['hand'].grip(0.75)
    S['watch'].location = (hp[0] - 0.55, hp[1] + 0.1, hp[2] - 0.55 + 0.03 * math.sin(t * 6))
    S['watch'].rotation_euler = (PI / 2 - 0.25, 0.15 * math.sin(t * 3), 0.2)
    S['watch'].scale = (1.5, 1.5, 1.5)
    key(S, CAB, (1.5, -3.5, 3.0), (0.2, -1.2, 1.2), 260)
    shoot(S, CAB, (lerp(1.9, 1.5, k), lerp(-3.9, -3.5, k), lerp(1.5, 1.9, k)), (0.25, -1.2, lerp(0.8, 1.35, u)), 40)


PHASES = ('day', 'dusk', 'night', 'dawn', 'day')


def helm_days(S, k, t, lt):
    """She steers. The sky behind her runs through day, dusk, night and dawn again and again; Rook scratches one more mark on the coaming for each."""
    x = (k * 2.0) % 1 * 4
    i = min(3, int(x))
    sky(S, PHASES[i], PHASES[i + 1], x - i, stars=PHASES[i] == 'night' or (PHASES[i + 1] == 'night' and x - i > 0.5))
    afloat(S, t, 1.0, PHASES[i] if x - i < 0.5 else PHASES[i + 1], flow=7)
    jury(S, t, 1.0, 1.0)
    helm(S, t, 'tired', 0.0, 0.05)
    n = int(1 + k * 11.99)
    for j, o in enumerate(S['tally'][:n]):
        o.location = (-0.3 + 0.15 * j + (0.07 if j % 5 == 4 else 0), 5.0, D + 0.02)
        o.rotation_euler = (PI / 2, 0, 0.6 if j % 5 == 4 else 0.0)
    a = math.sin(t * 14)
    aboard(S, S['rook'], -0.5, 5.9, D, facing((-0.5, 5.9), (1.6, 4.4)), P('stand', **dict(CROUCH, lean=0.22, aR=(1.0 + 0.15 * a, 0.0, 0.7), head=(0.05, 0.0))), 'calm')
    shoot(S, SEA, (lerp(3.0, 2.5, k), lerp(3.6, 4.1, k), D + lerp(2.8, 2.5, k)), (-0.3, 7.4, D + 1.7), 28)


# ---------------------------------------------------------------- day 41: Hilo
def evening(S, t, k=0.6, lamps=1.0, py=0.0, flow=5):
    sky(S, 'dusk', 'night', k, stars=True)
    afloat(S, t, 0.8, 'night' if k > 0.5 else 'dusk', flow=flow)
    jury(S, t, 1.0, 1.0)
    port(S, py, 0.0, lamps, t)


def ship_at(S, x, y):
    S['rship'].location = at(SEA, x, y, 0)
    return at(SEA, x + 5.2, y + 1.5, 16.2)


def ship_light(S, k, t, lt):
    """Night. A ship's searchlight swings across the water and stops on the wreck. At the bow Rook is waving both wings; she turns to the light."""
    evening(S, t, 0.85, 1.0, -30)
    src = ship_at(S, lerp(-64, -50, k), -8)
    u = sm(k * 1.5)
    beam_on(S, src, at(SEA, lerp(-22, 0.0, u), lerp(26, 3.0, u), 1.5))
    a = math.sin(t * 10)
    helm(S, t, 'wide', lerp(0.0, -1.0, u), -0.1)
    aboard(S, S['rook'], -0.9, 0.4, R, facing((-0.9, 0.4), (-50, -8)), P('up', aL=(2.7, 0.4 - 0.4 * a, 0.2), aR=(2.7, 0.4 + 0.4 * a, 0.2), head=(-0.2, 0.0)), 'shocked')
    shoot(S, SEA, (lerp(17, 14, k), lerp(15, 12, k), lerp(5.0, 4.2, k)), (-16, -4, 7), 26)


def her_light(S, k, t, lt):
    """Close on her at the wheel: the beam hits her face, white. Her eyes go wide, then screw shut; a hand comes up against the glare. Her mouth opens."""
    evening(S, t, 0.85, 1.0, -30)
    ship_at(S, -50, -8)
    u, v = sm(lt / 0.35), sm((lt - 0.55) / 0.35)
    m = aboard(S, S['tami'], 0, 8.35, D, -0.35, blend(P('stand', **STEER), P('stand', aL=(1.75, 0.5, 1.7, -0.4), aR=(1.15, 0.15, 0.5), head=(-0.1, -0.2)), v), 'squint' if v > 0.5 else 'wide')
    m.jawv = 0.6 * v
    key(S, SEA, (-9, 5, 5.5), (0, 8.35, D + 2.6), 5000 * u, 'F2F6FF')
    h = thead(S)
    shoot(S, (0, 0, 0), (h[0] - lerp(1.9, 1.5, k), h[1] - lerp(2.9, 2.5, k), h[2] + 0.15), (h[0], h[1], h[2] - 0.05), 50)


def tow_in(S, k, t, lt):
    """From above and behind: the ship ahead, a towline down to the yacht's bow where Rook stands pointing, the breakwater light sliding past, the town beyond."""
    evening(S, t, 0.8, 1.0, lerp(60, 44, k), flow=4)
    ship_at(S, 0, -62)
    S['slamp'].data.energy = 0
    span(S['towl'], at(SEA, 0, -31, 5.5), wpos(S['boat'], (0, -12.6, D + 0.2)), 0.07)
    helm(S, t, 'warm', 0.0, -0.1)
    aboard(S, S['rook'], 0.0, -9.8, D, 0.0, P('point', head=(-0.1, 0.0)), 'calm')
    key(S, SEA, (-6, 12, 14), (0, 0, 2), 9000, 'FFE2B8')
    shoot(S, SEA, (lerp(-11, -8, k), lerp(23, 19, k), lerp(11, 9, k)), (5, -32, 6), 28)


def rook_hatjump(S, k, t, lt):
    """Rook on the roof, the harbour lights behind him. He looks back at her at the wheel; his hat leaves his head and a feather comes loose."""
    evening(S, t, 0.8, 1.0, 44, flow=4)
    ship_at(S, 0, -62)
    S['slamp'].data.energy = 0
    u = max(0.0, min(1.0, (lt - 0.3) / 0.55))
    aboard(S, S['rook'], 0.0, 0.2, R, PI + 0.2, blend(P('stand', head=(0.0, 0.3)), P('shrug', head=(-0.1, 0.0)), u * 2), 'shocked' if u > 0.05 else 'calm')
    S['hat_jump'] = 0.55 * math.sin(PI * u)
    h = rhead(S)
    feather(S, (h[0] + 0.2, h[1] + 0.3, h[2] + 0.2), u)
    key(S, SEA, (4, 9, 7), (0, 0.2, R + 2), 1500, 'FFE2B8')
    shoot(S, (0, 0, 0), (h[0] + lerp(1.3, 0.9, k), h[1] + lerp(4.6, 3.9, k), h[2] - 0.3), (h[0], h[1], h[2] - 0.35), 40)


# ---------------------------------------------------------------- the ending
def morning(S, t, py=44):
    sky(S, 'dawn')
    afloat(S, t, 0.3, 'dawn')
    jury(S, t, 1.0, 0.25)
    port(S, py, 0.0, 0.25, t)


def line_dawn(S, k, t, lt):
    """Dawn, in harbour. Low on the side deck: the orange line still on its cleat. Rook stands over it with his hat held to his chest, head down."""
    morning(S, t)
    slack_line(S, t * 0.3)
    aboard(S, S['rook'], -1.25, 6.5, D, facing((-1.25, 6.5), (-3.2, 5.6)), P('stand', aL=(0.6, -0.2, 2.0, 1.0), head=(lerp(0.2, 0.5, sm(k * 1.5)), 0.0)), 'sad')
    S['hat_off'] = 1.0
    shoot(S, SEA, (lerp(-5.6, -5.0, k), lerp(3.3, 3.9, k), D + lerp(0.75, 1.0, k)), (-1.8, 6.1, D + lerp(1.2, 1.7, k)), 36)


def sloop(S, k, t, lt):
    """Another year, another boat: a small sloop with her mast standing and both sails full, heeling to a clean breeze. She is at the tiller, hair flying."""
    sky(S, 'day')
    sea(S, t, 0.9, 10, 'day')
    S['boat'].location = FAR
    b = S['sloop']
    b.location = at(SEA, 0, 0, 0.1 * math.sin(t * 1.5))
    b.rotation_euler = (0.03 * math.sin(t * 1.2), -0.2 + 0.03 * math.sin(t), 0)
    m = S['tami']
    m.root.parent = b
    m.place((0.9, 4.4, 1.35), 0.15)
    m.apply(P('stand', aL=(0.9, 0.3, 0.6), aR=(0.4, 0.3, 0.5), lL=(0.2, 0.2), lR=(-0.1, 0.1), head=(-0.1, 0.4)))
    m.face = 'warm'
    m.extra['cut'].hide_render = True
    shoot(S, SEA, (lerp(15, 12, k), lerp(-8, -6, k), lerp(2.6, 3.2, k)), (0.3, 1.6, 5.4), 34)


def rook_wrong(S, k, t, lt):
    """Close on Rook at dawn: he puts his hat back on, settles the brim, and looks straight at us. No joke."""
    morning(S, t)
    on = sm(lt / 0.55)
    aboard(S, S['rook'], 0.0, 1.6, R, 0.25, blend(P('stand', head=(0.25, 0.0)), blend(P('hat'), P('stand', head=(0.0, 0.0)), (lt - 0.65) / 0.3), on), 'soft')
    S['hat_off'] = 1.0 - on
    h = rhead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.4, 1.1, k), h[1] - lerp(3.5, 3.0, k), h[2] - 0.2), (h[0], h[1], h[2] - 0.3), 44)


def signoff(S, k, t, lt):
    """Rook on the end of the breakwater at dawn, the wreck lying quiet in the harbour behind him. He pulls his brim down and looks out to sea."""
    morning(S, t, 44)
    rk = S['rook']
    rk.place(at(SEA, 24.2, 10.5, 2.9), facing((24.2, 10.5), (0, -40)))
    rk.apply(blend(P('hat', head=(0.15, 0.0)), P('stand', head=(-0.12, -0.3)), (lt - 0.5) / 0.35))
    S['rface'] = 'soft'
    S['hat_tip'] = 0.6 * (1 - sm((lt - 0.5) / 0.35))
    shoot(S, SEA, (lerp(19.5, 20.3, k), lerp(4.0, 4.8, k), lerp(4.6, 5.0, k)), (23.8, 10.3, 5.2), 44)


def photo_wreck(S, k, t, lt):
    """For the case board: the dismasted yacht under her one small sail, seen from the side."""
    sky(S, 'day')
    afloat(S, 0.4, 1.0, 'day')
    jury(S, 0.4, 1.0, 1.0)
    helm(S, 0.4)
    shoot(S, SEA, (20, -13, 5.5), (0, -1.5, 3.2), 34)


SHOTS3D = {f.__name__: f for f in (
    wake, hatch_out, helm_empty, rook_mast, storm_wave, storm_roll, out_cold, cleat_line, rook_ring, stern_alone, engine_dead, pump, pole_up,
    sail_fill, wide_sail, plane_over, wave_up, plane_gone, rook_glass, sextant, rook_sun, bilge_watch, helm_days, ship_light,
    her_light, tow_in, rook_hatjump, line_dawn, sloop, rook_wrong, signoff)}
STILLS = dict(wreck=photo_wreck)


# ================================================================ long-form extension (Case 018, the full case file)
# Everything above is the Short's code, untouched. Below: the yacht as she was before the storm (both masts standing),
# the quay at Papeete, a far-off wall of storm cloud, the quay at Hilo, and a study years later; new props (a radio
# microphone, an emergency beacon, a crate and rows of tins, a log book and an oil lamp, a folded shirt, a harness strap,
# a typewriter, a plain book, a small sextant pendant); and the new shots. Richard Sharp is still never shown: before
# the storm the film shows the yacht, Tami and his absence from frame, never a figure in his place.
QUAY = (6000.0, 0.0, 0.0)          # Papeete: a stone quay, the yacht alongside, green mountains behind
HILOQ = (-6000.0, 0.0, 0.0)        # Hilo: a quay in the morning, the wreck tied up
DESK = (0.0, -6000.0, 0.0)         # a study, years later
CLOUD = (0.0, 0.0, 0.0)            # the storm wall is placed relative to the open sea


def _hull(b, W_='ECE8DC', T_='2E5E8E', DK='B48C5C'):
    """The same hull as the Short's wreck (same deck height D and roof R), but nothing broken."""
    add('cube', W_, (0, 1, 0.35), scale=(7.0, 16, 1.9), size=1, parent=b)
    add('cylinder', W_, (0, -9, 0.35), rot=(0, 0, PI), radius=4.04, depth=1.9, vertices=3, parent=b)
    add('cube', T_, (0, 1, 0.95), scale=(7.06, 16.04, 0.3), size=1, parent=b)
    add('cylinder', T_, (0, -9, 0.95), rot=(0, 0, PI), radius=4.09, depth=0.3, vertices=3, parent=b)
    add('cube', '7A2E26', (0, 1, -0.9), scale=(6.2, 15, 0.7), size=1, parent=b)
    add('cube', DK, (0, 1, D - 0.04), scale=(6.8, 15.9, 0.08), size=1, parent=b, rough=1.0)
    add('cylinder', DK, (0, -9, D - 0.04), rot=(0, 0, PI), radius=3.9, depth=0.08, vertices=3, parent=b, rough=1.0)
    for i in range(9):
        add('cube', '8E6A40', (-3.0 + 0.75 * i, 1, D + 0.01), scale=(0.04, 15.8, 0.02), size=1, parent=b)
    add('cube', W_, (0, -1.4, (D + R) / 2), scale=(4.4, 9.6, R - D), size=1, parent=b)
    add('cube', 'D8D2C2', (0, -1.4, R + 0.03), scale=(4.0, 9.2, 0.06), size=1, parent=b, rough=1.0)
    for s in (-1, 1):
        for j in range(4):
            add('cube', '1A2630', (s * 2.21, -4.6 + 2.0 * j, D + 0.5), scale=(0.04, 1.2, 0.36), size=1, parent=b, rough=0.2)
        add('cube', W_, (s * 2.75, 6.4, D + 0.3), scale=(0.35, 5.2, 0.6), size=1, parent=b)
        add('cube', DK, (s * 1.9, 6.4, D + 0.38), scale=(1.2, 5.0, 0.2), size=1, parent=b, rough=1.0)
        prev = None
        for j in range(7):
            top = (s * 3.35, -6.5 + 2.55 * j, D + 0.95)
            bar(b, 'C8CED6', (s * 3.35, top[1], D), top, 0.035, rough=0.3)
            if prev:
                bar(b, 'C8CED6', prev, top, 0.018, rough=0.3)
            prev = top
    add('cube', '2A2018', (0, 3.42, D + 0.45), scale=(1.5, 0.06, 1.3), size=1, parent=b)
    add('cube', '8E6A40', (0, 2.2, R + 0.1), scale=(1.7, 1.6, 0.1), size=1, parent=b)
    add('cube', 'D8D2C2', (0, 7.5, D + 0.7), scale=(0.34, 0.34, 1.4), size=1, parent=b)
    wh = empty((0, 7.72, D + 1.45), b, (PI / 2, 0, 0))
    add('torus', 'C8CED6', (0, 0, 0), major_radius=0.72, minor_radius=0.05, major_segments=14, minor_segments=4, parent=wh, rough=0.3)
    for i in range(3):
        add('cube', 'C8CED6', (0, 0, 0), rot=(0, 0, i * PI / 3), scale=(1.44, 0.06, 0.05), size=1, parent=wh, rough=0.3)
    bar(b, 'C8CED6', (-3.35, 8.8, D + 0.95), (3.35, 8.8, D + 0.95), 0.03, rough=0.3)
    return wh


def make_whole(S):
    """The ketch as she left Tahiti: main and mizzen masts standing, mainsail, mizzen and jib set. Bow towards -Y."""
    b = keep(empty(FAR))
    S['wwheel'] = _hull(b)
    add('cylinder', 'D6D8DC', (0, -3.6, R + 6.5), radius=0.24, depth=13, vertices=8, parent=b, rough=0.4)          # mainmast
    add('cylinder', 'D6D8DC', (0, 9.4, D + 4.2), radius=0.17, depth=8.4, vertices=8, parent=b, rough=0.4)          # mizzen
    bar(b, 'D6D8DC', (0, -3.5, R + 1.3), (0, 3.6, R + 1.3), 0.16, rough=0.4)                                      # main boom
    bar(b, 'D6D8DC', (0, 9.5, D + 1.6), (0, 13.2, D + 1.6), 0.12, rough=0.4)                                      # mizzen boom
    for p, q in (((0, -3.6, R + 13), (0, -13.0, D + 0.4)), ((0, -3.6, R + 12.5), (-3.3, 1.5, D + 0.9)), ((0, -3.6, R + 12.5), (3.3, 1.5, D + 0.9)),
                 ((0, 9.4, D + 8.4), (0, -3.6, R + 9.0)), ((0, 9.4, D + 8.2), (0, 13.6, D + 0.9))):
        bar(b, '9AA2AC', p, q, 0.03, rough=0.3)
    S['wmain'] = empty((0, 0, 0), b)
    tri('wmain', 'FBF8F0', [(0.04, -3.45, R + 1.45), (0.04, -3.45, R + 12.6), (0.04, 3.5, R + 1.45)], S['wmain'], 1.0)
    S['wmiz'] = empty((0, 0, 0), b)
    tri('wmiz', 'FBF8F0', [(0.04, 9.55, D + 1.75), (0.04, 9.55, D + 8.0), (0.04, 13.0, D + 1.75)], S['wmiz'], 1.0)
    S['wjib'] = empty((0, 0, 0), b)
    tri('wjib', 'F4EEDC', [(-0.05, -3.8, R + 11.8), (-0.05, -12.6, D + 0.6), (-0.6, -4.4, R + 0.6)], S['wjib'], 1.0)
    tri('wtab', 'FF7A1A', [(-0.06, -3.8, R + 11.8), (-0.06, -5.2, R + 9.9), (-0.2, -4.0, R + 9.6)], S['wjib'], 1.0)
    S['wharn'] = keep(add('torus', 'FF7A1A', FAR, major_radius=0.42, minor_radius=0.06, major_segments=10, minor_segments=4, rough=0.8))
    S['whole'] = b


def make_cloudwall(S):
    w = keep(empty(FAR))
    for i in range(26):
        add('ico_sphere', ('7A848E', '8A949E', '6A747E')[i % 3], (-260 + 21 * i + 9 * rnd(i, 61), 40 * rnd(i, 62), 55 + 55 * rnd(i, 63)),
            scale=(1.8, 1.0, 0.8 + 0.4 * rnd(i, 64)), radius=34 + 24 * rnd(i, 65), subdivisions=2, parent=w, rough=1.0)
    add('cube', '1A2228', (0, 30, 8), scale=(560, 40, 16), size=1, parent=w, rough=1.0)                          # the rain curtain under it
    S['bolt'] = [add('cube', 'E8F0FF', (-120 + 90 * i, -5, 40), rot=(0, 0.3 - 0.25 * i, 0), scale=(0.9, 0.9, 40), size=1, parent=w, emit=30.0) for i in range(3)]
    S['cloudwall'] = w


def make_quay(r):
    """Papeete in the morning: a stone quay with bollards, moored yachts, palms, green peaks behind. No names, no flags."""
    add('plane', '2E8A9A', (0, 0, -0.05), size=600, parent=r, rough=0.15)
    box = lambda col, loc, sc, **kw: add('cube', col, loc, scale=sc, size=1, parent=r, **kw)
    box('B8B0A0', (0, 12.0, 0.6), (120, 10, 2.4))                                                              # the quay, the boat lies along y = 6
    box('8E8678', (0, 7.02, 0.6), (120, 0.1, 2.4), rough=1.0)
    for i in range(14):
        box('A8A090', (-60 + 9 * i, 9.0, 1.81), (0.08, 6, 0.02))
    bol = []
    for x in (-14, -4, 6, 16, 26):
        o = add('cylinder', '2A2E34', (x, 8.0, 2.2), radius=0.35, depth=0.8, vertices=8, parent=r)
        add('cylinder', '2A2E34', (x, 8.0, 2.65), radius=0.5, depth=0.15, vertices=8, parent=r)
        bol.append(o)
    crates = []
    for i in range(3):
        crates.append(box('9A7248', (-7.5 + 1.3 * i, 10.5, 2.25), (1.1, 0.9, 0.9)))
    add('cylinder', 'E8D8A0', (-10.5, 10.2, 2.4), radius=0.6, depth=1.2, vertices=10, parent=r, rough=1.0)       # a duffel bag on its end
    for j in range(5):                                                                                       # other yachts moored along the quay
        x = (-48, -30, 36, 54, 72)[j]
        o = empty((x, 1.5, 0), r)
        add('cube', ('F2EEE4', 'E8E4D8', 'D8DCE4')[j % 3], (0, 0, 0.4), scale=(4.4, 11, 1.4), size=1, parent=o)
        add('cylinder', ('F2EEE4', 'E8E4D8', 'D8DCE4')[j % 3], (0, -6.5, 0.4), rot=(0, 0, PI), radius=2.54, depth=1.4, vertices=3, parent=o)
        add('cube', ('2E5E8E', 'C8322A', '3E7A4A')[j % 3], (0, 0, 0.9), scale=(4.46, 11.04, 0.2), size=1, parent=o)
        add('cylinder', 'D6D8DC', (0, -1, 7), radius=0.12, depth=12 + 3 * rnd(j, 3), vertices=6, parent=o)
    palms = []
    for j, (x, y) in enumerate(((-22, 15), (-2, 16), (18, 15.5), (38, 16), (-40, 16))):
        p = empty((x, y, 1.8), r)
        for k in range(6):
            add('cylinder', '6A5038', (0.15 * k * k * 0.1, 0, 0.75 + 1.5 * k), radius=0.24 - 0.02 * k, depth=1.6, vertices=6, parent=p)
        cr = empty((0.4, 0, 9.2), p)
        for i in range(7):
            add('cone', '3E8A3A', (0, 0, 0), rot=(1.25, 0, i * 2 * PI / 7), radius1=0.5, radius2=0.0, depth=4.4, vertices=3, parent=cr, scale=(1, 0.3, 1))
        palms.append(cr)
    for i, (x, y, rr, hh) in enumerate(((-80, 140, 90, 110), (10, 170, 120, 150), (110, 150, 80, 95), (190, 190, 110, 120), (-170, 180, 100, 90))):
        add('cone', ('3E7A3A', '336A32', '4A8A44')[i % 3], (x, y, hh / 2 - 2), radius1=rr, radius2=rr * 0.1, depth=hh, vertices=9, parent=r, rough=1.0)
    for i in range(10):                                                                                       # low white houses along the shore
        box(('F2EEE4', 'F0D8B0', 'E8E0D0')[i % 3], (-70 + 15 * i + 4 * rnd(i, 71), 26 + 6 * rnd(i, 72), 3), (6 + 3 * rnd(i, 73), 5, 4 + 3 * rnd(i, 74)))
        box('C8503A', (-70 + 15 * i + 4 * rnd(i, 71), 26 + 6 * rnd(i, 72), 5.4), (6.4 + 3 * rnd(i, 73), 5.4, 0.6))
    sun = light((0, -30, 60), 0, 'FFF0D8', 120.0, parent=r)
    return dict(lights=[sun], sun=sun, palms=palms, crates=crates, bol=bol)


def make_hiloq(r):
    """Hilo, the morning after: a concrete quay, the wreck tied alongside, a dark green island rising behind, a breakwater light."""
    add('plane', '2A5E70', (0, 0, -0.05), size=600, parent=r, rough=0.15)
    add('cube', '9A9890', (0, 12.0, 0.6), scale=(90, 10, 2.4), size=1, parent=r)
    add('cube', '6E6C66', (0, 7.02, 0.6), scale=(90, 0.1, 2.4), size=1, parent=r, rough=1.0)
    bol = add('cylinder', '2A2E34', (-2.0, 8.2, 2.1), radius=0.38, depth=0.6, vertices=8, parent=r)
    add('cylinder', '2A2E34', (-2.0, 8.2, 2.45), radius=0.5, depth=0.12, vertices=8, parent=r)
    add('cube', 'D8D4C8', (9, 13, 3.6), scale=(8, 5, 3.2), size=1, parent=r)                                     # a small harbour shed
    add('cube', '5A6A78', (9, 13, 5.3), scale=(8.6, 5.6, 0.3), size=1, parent=r)
    for i, (x, y, rr, hh) in enumerate(((-60, 150, 140, 120), (80, 190, 170, 160), (-200, 200, 120, 80))):
        add('cone', ('2E5A36', '28502E', '345E3A')[i % 3], (x, y, hh / 2 - 2), radius1=rr, radius2=rr * 0.12, depth=hh, vertices=9, parent=r, rough=1.0)
    add('cylinder', 'E8E6E0', (-40, -30, 4.0), radius=0.9, depth=8, vertices=8, parent=r)
    add('cube', '3AF08A', (-40, -30, 8.6), scale=(1.2, 1.2, 1.2), size=1, parent=r, emit=6.0)
    blanket = add('cube', '8A8E96', FAR, scale=(1.3, 1.0, 1.6), size=1, rough=1.0)
    sun = light((-20, -40, 40), 0, 'FFE0C0', 90.0, parent=r)
    return dict(lights=[sun], sun=sun, blanket=keep(blanket), bol=bol)


def make_desk(r):
    """A study, years later, at night: a wall of books, a window on the dark sea, a desk with a typewriter, a lamp, a stack of pages, a plain book."""
    add('cube', '5A4030', (0, 0, -0.05), scale=(16, 14, 0.1), size=1, parent=r)
    add('cube', 'D8CFC0', (0, 5.5, 3), scale=(16, 0.15, 6), size=1, parent=r)
    add('cube', 'C8BCA8', (-6.0, 0, 3), scale=(0.15, 14, 6), size=1, parent=r)
    add('cube', '0E1E38', (2.6, 5.6, 3.4), scale=(4.6, 0.05, 2.8), size=1, parent=r, emit=0.6)                    # the window: night sea and a moon
    add('ico_sphere', 'F4F0E0', (3.8, 5.55, 4.2), radius=0.32, subdivisions=2, parent=r, emit=6.0)
    for (x, z, sx, sz) in ((2.6, 4.85, 4.9, 0.15), (2.6, 1.95, 4.9, 0.15), (0.25, 3.4, 0.15, 3.0), (4.95, 3.4, 0.15, 3.0)):
        add('cube', 'F2EEE4', (x, 5.5, z), scale=(sx, 0.2, sz), size=1, parent=r)
    for i in range(5):                                                                                       # shelves of books, plain spines
        add('cube', '6A4A30', (-5.85, -2.0, 0.8 + 1.1 * i), scale=(0.5, 6, 0.08), size=1, parent=r)
        for j in range(16):
            add('cube', ('8A2E26', '2E4A6E', 'C89A3A', '3E6A4A', 'D8D0C0', '5A3A6A')[(i * 7 + j) % 6], (-5.8, -4.7 + 0.36 * j, 1.22 + 1.1 * i),
                scale=(0.4, 0.3, 0.7 + 0.18 * rnd(i * 16 + j, 3)), size=1, parent=r)
    add('cube', '7A5232', (0.6, 2.6, 1.6), scale=(4.4, 2.0, 0.12), size=1, parent=r)                               # the desk
    for sx in (-1, 1):
        add('cube', '6A4428', (0.6 + sx * 2.0, 2.6, 0.78), scale=(0.15, 1.8, 1.56), size=1, parent=r)
    tw = empty((0.6, 2.75, 1.66), r)                                                                         # the typewriter
    add('cube', '2A3A34', (0, 0, 0.18), scale=(1.3, 0.9, 0.36), size=1, parent=tw)
    add('cylinder', '1A1A1E', (0, 0.35, 0.42), rot=(0, PI / 2, 0), radius=0.12, depth=1.5, vertices=8, parent=tw)
    add('cube', 'F4F0E4', (0, 0.42, 0.75), rot=(-0.25, 0, 0), scale=(0.75, 0.02, 0.7), size=1, parent=tw, rough=1.0)
    for j in range(3):
        for i in range(8):
            add('cube', 'D8D2C2', (-0.5 + 0.14 * i, -0.3 + 0.13 * j, 0.38 + 0.03 * j), scale=(0.1, 0.1, 0.04), size=1, parent=tw)
    pages = empty((2.1, 2.4, 1.66), r)
    for i in range(10):
        add('cube', 'F4F0E4', (0.02 * rnd(i, 81), 0.02 * rnd(i, 82), 0.03 * i), rot=(0, 0, 0.05 * rnd(i, 83)), scale=(0.75, 1.0, 0.03), size=1, parent=pages, rough=1.0)
    book = empty((-0.9, 2.3, 1.66), r)
    add('cube', 'B8402E', (0, 0, 0.09), scale=(0.8, 1.1, 0.18), size=1, parent=book)                              # a plain hardback, no lettering
    add('cube', 'F2EEE4', (0.03, 0, 0.09), scale=(0.76, 1.06, 0.14), size=1, parent=book, rough=1.0)
    add('cylinder', '2A2E34', (-1.4, 3.2, 1.9), radius=0.25, depth=0.5, vertices=8, parent=r)                        # the lamp
    add('cylinder', '2A2E34', (-1.4, 3.0, 2.6), rot=(0.4, 0, 0), radius=0.04, depth=1.4, vertices=6, parent=r)
    add('cone', 'FF7A1A', (-1.4, 2.7, 3.2), rot=(0.6, 0, 0), radius1=0.45, radius2=0.15, depth=0.5, vertices=10, parent=r)
    seat_ = empty((0.6, 0.9, 0), r)
    add('cube', '4A3428', (0, 0, 1.0), scale=(1.2, 1.1, 0.15), size=1, parent=seat_)
    add('cube', '4A3428', (0, -0.6, 1.8), scale=(1.2, 0.15, 1.5), size=1, parent=seat_)
    lamp = light((-1.2, 2.4, 2.9), 0, 'FFD8A0', 1.2, parent=r)
    room = light((1.0, -3.0, 5.5), 0, 'C8D4E8', 4.0, parent=r)
    return dict(lights=[lamp, room], lamp=lamp, room=room, book=book, pages=pages, tw=tw)


def make_props(S):
    S['mic'] = keep(empty(FAR))
    add('cube', '1A1A1E', (0, 0, 0), scale=(0.16, 0.08, 0.26), size=1, parent=S['mic'])
    add('cube', '50545C', (0, -0.045, 0.06), scale=(0.1, 0.02, 0.08), size=1, parent=S['mic'])
    S['cord'] = keep(add('cylinder', '1A1A1E', FAR, radius=0.5, depth=1, vertices=5))
    S['rled'] = [keep(add('cube', 'FF4A3A', FAR, scale=(0.06, 0.03, 0.06), size=1, emit=8.0)) for _ in range(3)]
    S['beacon'] = keep(empty(FAR))
    add('cylinder', 'F2B531', (0, 0, 0), radius=0.14, depth=0.55, vertices=10, parent=S['beacon'], rough=0.5)
    add('cylinder', '2A2E34', (0, 0, 0.32), radius=0.1, depth=0.1, vertices=10, parent=S['beacon'])
    S['blamp'] = add('ico_sphere', '6A6A6A', (0, 0, 0.4), radius=0.08, subdivisions=1, parent=S['beacon'], rough=0.3)
    add('cylinder', '2A2E34', (0.07, 0, 0.75), radius=0.012, depth=0.6, vertices=4, parent=S['beacon'])
    S['crate'] = keep(empty(FAR))
    add('cube', '9A7248', (0, 0, 0.0), scale=(0.9, 0.6, 0.35), size=1, parent=S['crate'])
    for i in range(6):
        add('cylinder', ('C8CED6', 'D8B24A', 'B8443A')[i % 3], (-0.3 + 0.3 * (i % 3), -0.12 + 0.24 * (i // 3), 0.25), radius=0.1, depth=0.22, vertices=8, parent=S['crate'])
    S['tins'] = [keep(add('cylinder', ('C8CED6', 'D8B24A', 'B8443A', 'E8E2D2')[i % 4], FAR, radius=0.13, depth=0.26, vertices=8, rough=0.4)) for i in range(15)]
    S['logb'] = keep(empty(FAR))
    add('cube', '2E4A2E', (0, 0, 0), scale=(0.9, 0.62, 0.05), size=1, parent=S['logb'])
    add('cube', 'F4F0E4', (0, 0, 0.03), scale=(0.84, 0.58, 0.03), size=1, parent=S['logb'], rough=1.0)
    for i in range(5):
        add('cube', '3A3A50', (-0.15 - 0.0 * i, 0.18 - 0.08 * i, 0.05), scale=(0.3 + 0.08 * rnd(i, 91), 0.012, 0.005), size=1, parent=S['logb'])
    S['pencil'] = keep(add('cylinder', 'F2B531', FAR, radius=0.025, depth=0.4, vertices=6))
    S['olamp'] = keep(empty(FAR))
    add('cylinder', 'C89A3A', (0, 0, 0), radius=0.14, depth=0.16, vertices=8, parent=S['olamp'], rough=0.3)
    add('ico_sphere', 'FFD080', (0, 0, 0.2), radius=0.12, subdivisions=1, parent=S['olamp'], emit=14.0)
    S['olight'] = light(FAR, 0, 'FFC070', 0.6)
    S['shirt'] = keep(empty(FAR))
    add('cube', '5A7AA8', (0, 0, 0), scale=(0.75, 0.55, 0.12), size=1, parent=S['shirt'], rough=1.0)
    add('cube', '4A6A98', (0, -0.22, 0.07), scale=(0.3, 0.1, 0.05), size=1, parent=S['shirt'], rough=1.0)
    S['pend'] = keep(empty(FAR))
    for a in (-0.5, 0.5):
        bar(S['pend'], 'E8C060', (0, 0, 0.0), (0.09 * math.sin(a), 0, -0.13 * math.cos(a)), 0.012, rough=0.2)
    for i in range(4):
        a0, a1 = -0.5 + i / 4, -0.5 + (i + 1) / 4
        bar(S['pend'], 'E8C060', (0.13 * math.sin(a0), 0, -0.13 * math.cos(a0)), (0.13 * math.sin(a1), 0, -0.13 * math.cos(a1)), 0.016, rough=0.2)
    S['pglint'] = add('ico_sphere', 'FFFFFF', (0.04, -0.01, -0.05), radius=0.01, subdivisions=1, parent=S['pend'], emit=20.0)
    S['chain'] = keep(add('torus', 'E8C060', FAR, major_radius=0.3, minor_radius=0.008, major_segments=16, minor_segments=3, rough=0.2))
    S['shed'] = keep(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.36, vertices=4))


_build0, _reset0 = build, reset


def build():
    S = _build0()
    make_whole(S)
    make_cloudwall(S)
    make_props(S)
    S['sets'] = {}
    for name, org, fn in (('quay', QUAY, make_quay), ('hiloq', HILOQ, make_hiloq), ('desk', DESK, make_desk)):
        root = keep(empty(org))
        d = fn(root)
        d.update(root=root, all=[o for o in bpy.data.objects if _under(o, root)])
        S['sets'][name] = d
    reset(S)
    return S


def _under(o, root):
    p = o.parent
    while p:
        if p is root:
            return True
        p = p.parent
    return False


def reset(S):
    _reset0(S)
    if 'sets' not in S:
        return
    for d in S['sets'].values():
        for o in d['all']:
            o.hide_render = True
        for l in d['lights']:
            l.data.energy = 0
    S['olight'].data.energy = 0
    S['olight'].location = FAR
    S['cloudwall'].location = FAR
    for o in S['bolt']:
        o.hide_render = True
    S['whole'].rotation_euler = (0, 0, 0)
    S['blamp'].scale = (1, 1, 1)


def setin(S, name):
    d = S['sets'][name]
    for o in d['all']:
        o.hide_render = False
    S['sea'].location = FAR
    S['deep'].location = FAR
    S['boat'].location = FAR
    return d


def SP(name, x, y, z):
    o = {'quay': QUAY, 'hiloq': HILOQ, 'desk': DESK}[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def onset(S, rig, name, x, y, z, yaw, pose, face=None):
    rig.root.parent = None
    rig.place(SP(name, x, y, z), yaw)
    rig.apply(pose)
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def whole(S, t, amp=1.0, col='day', flow=0.0, roll=0.0, pitch=0.0, lift=0.0, at_=None):
    """The intact yacht on the open sea (or alongside a quay when at_ is given)."""
    S['boat'].location = FAR
    if at_ is None:
        sea(S, t, amp, flow, col)
        S['whole'].location = at(SEA, 0, 0, 0.12 * amp * math.sin(1.3 * t) + lift)
    else:
        S['whole'].location = at_
        for o in (S['wmain'], S['wmiz'], S['wjib']):                     # alongside the quay the sails are down
            o.scale = (0.01, 0.01, 0.01)
    S['whole'].rotation_euler = (0.035 * amp * math.sin(1.1 * t + 1) + pitch, 0.05 * amp * math.sin(0.9 * t) + roll, 0)
    S['wwheel'].rotation_euler = (PI / 2, 0.3 * math.sin(t * 1.3), 0)
    fl = 0.04 * math.sin(t * 6) * amp
    if at_ is None:
        for s in (S['wmain'], S['wmiz'], S['wjib']):
            s.scale = (1 + 4 * fl, 1, 1)


def wboard(S, rig, x, y, z=D, yaw=0.0, pose=None, face=None):
    rig.root.parent = S['whole']
    rig.place((x, y, z), yaw)
    rig.apply(pose or P())
    if face:
        if rig is S['rook']:
            S['rface'] = face
        else:
            rig.face = face
    return rig


def nocut(S):
    S['tami'].extra['cut'].hide_render = True


def to_hand(S, o, rig, i, loc, rot=(0, 0, 0), sc=None):
    o.parent = rig.hands[i]
    o.location, o.rotation_euler = loc, rot
    if sc:
        o.scale = sc


def dry_cabin(S, t, hatch=500, ports=120):
    """The cabin before the storm: no water, things in their places."""
    cabin(S, t, -1.5, hatch, ports, 0.0)
    for o in S['flot']:
        o.location = FAR


# ---------------------------------------------------------------- how it began: Papeete
def harbour_wide(S, k, t, lt):
    """Morning in Papeete: the stone quay, a row of moored yachts, palms, white houses and steep green peaks. Alongside, the ketch with both masts up;
    a small figure on her deck coiling a line."""
    sky(S, 'day')
    S['sun'].data.energy = 2.4
    d = setin(S, 'quay')
    d['sun'].data.energy = 0
    whole(S, t, 0.15, at_=SP('quay', 0, -2.6, 0))
    nocut(S)
    wboard(S, S['tami'], 1.2, -6.0, D, PI * 0.7, P('stand', aL=(0.9, 0.3, 1.2 + 0.4 * math.sin(lt * 4)), aR=(0.9, 0.3, 1.2 - 0.4 * math.sin(lt * 4)), head=(0.3, 0.0)), 'calm')
    for i, cr in enumerate(d['palms']):
        cr.rotation_euler = (0.05 * math.sin(t * 1.3 + i), 0.05 * math.sin(t * 1.1 + i), 0)
    shoot(S, QUAY, (lerp(-34, -28, k), lerp(-34, -30, k), lerp(9, 8, k)), (lerp(2, 4, k), 6, 4.5), 30)


def quay(S, k, t, lt):
    """On the quay: Tami on the side deck, coiling a line, smiling; behind her the mast goes up out of frame. Rook sits on a bollard with an open case file
    on his knee, looks up from it at her, and taps his beak."""
    sky(S, 'day')
    S['sun'].data.energy = 2.4
    d = setin(S, 'quay')
    whole(S, t, 0.15, at_=SP('quay', 0, -2.6, 0))
    nocut(S)
    c = math.sin(lt * 4)
    wboard(S, S['tami'], 1.3, 6.6, D, PI * 0.75, P('stand', aL=(0.9, 0.3, 1.2 + 0.4 * c), aR=(0.9, 0.3, 1.2 - 0.4 * c), head=(0.15, 0.3)), 'warm')
    S['tami'].jawv = 0.15
    v = sm((lt - 0.9) / 0.4)
    rk = onset(S, S['rook'], 'quay', -4.0, 8.0, 2.65 - 0.55, facing((-4.0, 8.0), (1.3, 4.0)),
               blend(P('sit', aL=(0.9, -0.1, 1.6, 1.0), head=(0.45, 0.0)), P('tap', lL=(1.45, 1.6), lR=(1.45, 1.6), lift=-0.5, head=(0.0, -0.3)), v), 'calm')
    S['logb'].parent = rk.hands[0]
    S['logb'].location, S['logb'].rotation_euler = (0.25, -0.3, -0.6), (1.0, 0, 0.3)
    shoot(S, QUAY, (lerp(9.5, 8.6, k), lerp(12.5, 12.0, k), lerp(4.6, 4.3, k)), (-1.2, 5.6, 3.2), 30)


def quay_load(S, k, t, lt):
    """Along the quay: she carries a crate of tins towards the yacht, past a duffel bag and crates; Rook walks beside her, hat tipped, carrying
    nothing. He glances at the tins."""
    sky(S, 'day')
    S['sun'].data.energy = 2.4
    d = setin(S, 'quay')
    whole(S, t, 0.15, at_=SP('quay', 0, -2.6, 0))
    nocut(S)
    x = lerp(-11.0, -5.5, k)
    m = onset(S, S['tami'], 'quay', x, 9.6, 1.8, PI / 2, blend(K.walk(t, 1.1), P('stand', aL=(1.0, 0.25, 1.2), aR=(1.0, 0.25, 1.2), head=(0.1, 0.4)), 0.65), 'warm')
    S['crate'].parent = m.body
    S['crate'].location, S['crate'].rotation_euler = (0, -0.75, 0.6), (0, 0, 0)
    rk = onset(S, S['rook'], 'quay', x - 0.6, 11.4, 1.8, PI / 2 + 0.25 * sm((lt - 1.0) / 0.4), blend(K.walk(t + 0.3, 1.1), P('hat', head=(0.1, 0.0)), 0.5), 'calm')
    S['hat_tip'] = 0.4
    shoot(S, QUAY, (x + lerp(5.5, 4.8, k), lerp(4.6, 4.9, k), 4.0), (x + 0.6, 10.4, 3.6), 30)


# ---------------------------------------------------------------- the voyage, before the storm
def sail_out(S, k, t, lt):
    """Open water, bright sun: the ketch under full sail, heeling, a bow wave; the green peaks of the island falling astern."""
    sky(S, 'day')
    whole(S, t, 0.8, 'day', flow=8, roll=-0.12)
    nocut(S)
    S['cloudwall'].location = FAR
    S['sets']['quay']['root'].location = at(SEA, 60, 330, -1.0)             # Tahiti, falling astern
    for o in S['sets']['quay']['all']:
        o.hide_render = False
    wboard(S, S['tami'], 0, 8.35, D, 0.0, P('stand', **STEER), 'warm')
    shoot(S, SEA, (lerp(-30, -24, k), lerp(-26, -22, k), lerp(5.0, 4.4, k)), (0, 2, 7.5), 30)


def easy_sail(S, k, t, lt):
    """Easy days: she sits on the coachroof in the sun, knees up, face to the wind, hair moving. Rook lies on the deck beside the mast, hat over his face,
    one leg crossed; he lifts the brim and peeks out at the sea."""
    sky(S, 'day')
    whole(S, t, 0.6, 'day', flow=6, roll=-0.08)
    nocut(S)
    wboard(S, S['tami'], 1.4, -1.5, R - 0.5, -0.9, P('sit', aL=(0.8, 0.2, 1.4, 1.0), aR=(0.8, 0.2, 1.4, 1.0), head=(-0.25, 0.35 + 0.1 * math.sin(lt))), 'warm')
    v = sm((lt - 1.2) / 0.4)
    rk = wboard(S, S['rook'], 1.6, -6.4, R + 0.3, 0.0, P('stand', lL=(0.0, 0.0), lR=(0.3, 0.6), aL=(0.2, 0.9, 1.6, -1.2), aR=(0.2, 0.9, 1.6, -1.2), head=(-0.2 + 0.4 * v, 0.0)), 'low')
    rk.place((1.6, -6.4, R + 0.35), 0.0, -PI / 2)
    S['hat_tip'] = 1.6 * (1 - v)
    shoot(S, SEA, (lerp(8.6, 8.0, k), lerp(-10.0, -9.4, k), R + lerp(2.6, 2.4, k)), (1.2, -3.8, R + 0.9), 28)


def radio_chart(S, k, t, lt):
    """Below, at the chart table, in lamplight: the radio's lights glow; she listens, pencil in hand, and marks a cross on the chart. Rook leans on the
    companionway steps behind her and taps his beak."""
    dry_cabin(S, t, 260, 60)
    nocut(S)
    m = S['tami']
    m.place(at(CAB, 1.25, 3.0, 0.0), facing((1.25, 3.0), (2.4, 3.4)))
    m.apply(P('stand', aR=(1.0 + 0.1 * math.sin(lt * 5), 0.1, 0.8), aL=(0.6, 0.1, 1.9, 0.6), lean=0.25, head=(0.25, 0.25 * math.sin(lt * 0.8))))
    m.face = 'hard'
    for i, o in enumerate(S['rled']):
        o.location = at(CAB, 2.94, 2.8 + 0.6 * i, 2.85)
        o.hide_render = (t * 2.0 + i * 0.3) % 1 > 0.7
    S['pencil'].parent = m.hands[1]
    S['pencil'].location, S['pencil'].rotation_euler = (0, -0.1, -0.6), (0.4, 0, 0)
    S['olamp'].location = at(CAB, 2.6, 4.3, 1.6)
    S['olight'].location, S['olight'].data.energy = at(CAB, 2.0, 4.0, 2.6), 180
    rk = S['rook']
    rk.place(at(CAB, -0.3, 4.6, 0.85), facing((-0.3, 4.6), (1.4, 3.1)))
    rk.apply(P('tap', head=(0.2, -0.1)))
    S['rface'] = 'calm'
    shoot(S, CAB, (lerp(2.3, 2.0, k), lerp(0.2, 0.5, k), lerp(3.1, 3.0, k)), (1.0, 3.6, 2.4), 26)


def clouds_build(S, k, t, lt):
    """Wide, from far off: the small ketch running with the wind behind her; on the horizon beyond, a black wall of cloud with a grey curtain of rain
    under it, lightning flicking inside."""
    sky(S, 'grey', 'storm', k * 0.6)
    whole(S, t, 1.4, 'grey', flow=9, roll=-0.1)
    S['cloudwall'].location = at(SEA, lerp(-60, -40, k), 380, 0)
    for i, o in enumerate(S['bolt']):
        o.hide_render = not ((t * 1.7 + 0.37 * i) % 1 < 0.08)
    shoot(S, SEA, (lerp(24, 20, k), lerp(-46, -40, k), lerp(4.5, 4.0, k)), (lerp(-6, -10, k), 60, 14), 30)


def reef_run(S, k, t, lt):
    """Storm, rain driving sideways: the ketch heeling hard under a scrap of mainsail; she hauls on the reef line at the mast, soaked. Rook clings to the
    mast with one wing and holds his hat on with the other, coat flapping."""
    sky(S, 'storm')
    whole(S, t * 1.4, 2.2, 'storm', flow=10, roll=-0.28)
    S['wmain'].scale = (1, 1, 0.45)
    S['wmiz'].scale = (0.01, 0.01, 0.01)
    S['wjib'].scale = (1, 0.4, 0.4)
    nocut(S)
    a = math.sin(t * 6)
    wboard(S, S['tami'], 0.9, -3.0, R, PI * 0.5, P('stand', aL=(1.6 + 0.4 * a, 0.2, 0.6), aR=(1.3 - 0.4 * a, 0.2, 0.6), lean=-0.2 + 0.1 * a, lL=(0.4, 0.4), lR=(-0.3, 0.2),
                                                       head=(-0.3, 0.0)), 'hard')
    S['tami'].jawv = 0.3
    wboard(S, S['rook'], -0.6, -4.2, R, 0.6, P('hat', aL=(1.5, 0.5, 0.8), lean=-0.15, head=(0.1, 0.3)), 'low')
    fl = 1.0 if (t * 2.3) % 1 < 0.08 else 0.0
    key(S, SEA, (12, -18, 30), (0, -3, 4), 30000 * fl + 6000, 'C8D8F0')
    shoot(S, SEA, (lerp(9.5, 8.5, k), lerp(-10.0, -9.0, k), R + lerp(3.4, 3.0, k)), (0.2, -3.6, R + 2.4), 28, 0.08 * math.sin(t * 1.4))


# ---------------------------------------------------------------- the storm: below, the shout, the tumble
def _harness(S, rig):
    S['wharn'].parent = rig.body
    S['wharn'].location, S['wharn'].rotation_euler, S['wharn'].scale = (0, 0, 0.75), (0, 0, 0), (1.0, 0.85, 1.0)


def hatch_below(S, k, t, lt):
    """From the cabin floor, looking up the companionway: grey storm light and rain in the hatch; she comes down the steps backwards, soaked, fumbling
    with the buckle of her orange harness. Lightning whites out the hatch."""
    dry_cabin(S, t, 900, 40)
    S['cwater'].location = at(CAB, 0, -2, 0.12)
    nocut(S)
    fl = 1.0 if (t * 1.9) % 1 < 0.07 else 0.0
    S['hatchl'].data.energy = 600 + 6000 * fl
    u = sm(lt / 1.4)
    m = S['tami']
    m.place(at(CAB, 0.0, lerp(4.4, 3.6, u), lerp(1.4, 0.0, u)), 0.0)
    m.apply(P('stand', aL=(1.1, 0.0, 1.8, 0.8), aR=(1.0, 0.0, 1.9, 0.8), lean=0.25, lL=(lerp(0.6, 0.1, u), 0.4), lR=(0.1, 0.3), head=(0.4, 0.0)))
    m.face = 'hard'
    _harness(S, m)
    S['cam'].rotation_euler = (0, 0, 0.06 * math.sin(t * 1.8))
    shoot(S, CAB, (lerp(0.6, 0.5, k), lerp(-1.6, -1.0, k), lerp(1.3, 1.4, k)), (0.0, 4.3, lerp(3.4, 2.6, k)), 24, 0.06 * math.sin(t * 1.8))


def hear_shout(S, k, t, lt):
    """Close on her face at the foot of the steps, the harness half done up: a sound from the cockpit. Her head snaps up to the hatch, eyes wide, mouth
    open. The hatch light flickers."""
    dry_cabin(S, t, 900, 40)
    S['cwater'].location = at(CAB, 0, -2, 0.12)
    nocut(S)
    fl = 1.0 if (t * 2.6) % 1 < 0.06 else 0.0
    S['hatchl'].data.energy = 500 + 5000 * fl
    v = sm((lt - 0.5) / 0.25)
    m = S['tami']
    m.place(at(CAB, 0.0, 3.5, 0.0), PI)
    m.apply(P('stand', aL=(1.0, 0.0, 1.8, 0.8), aR=(lerp(1.0, 0.6, v), lerp(0.0, 0.5, v), lerp(1.9, 1.0, v), 0.8), lean=lerp(0.2, -0.15, v), head=(lerp(0.3, -0.55, v), lerp(0.0, 0.15, v))))
    m.face = 'wide' if v > 0.5 else 'hard'
    m.jawv = 0.7 * v
    _harness(S, m)
    h = thead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.9, 1.6, k), h[1] + lerp(0.7, 0.5, k), h[2] - 0.4), (h[0], h[1] - 0.05, h[2] + 0.05), 36)


def tumble(S, k, t, lt):
    """Inside the cabin as the yacht goes over: the whole room turns over the camera, tins, books and cushions fly through the air, she is thrown
    across it, and the light goes out."""
    dry_cabin(S, t, 900, 200)
    nocut(S)
    u = sm(k * 1.05)
    roll = lerp(0.0, 2 * PI, u)
    for i, o in enumerate(S['flot']):
        a = rnd(i, 101) * 2 * PI
        o.location = at(CAB, 2.2 * math.cos(a + 3 * u), -2 + 4 * (rnd(i, 102) - 0.5) - 2 * u, 2.1 + 1.6 * math.sin(a + 4 * u))
        o.rotation_euler = (u * 7 + i, u * 5, u * 3 + i)
    m = S['tami']
    m.place(at(CAB, lerp(1.6, -1.8, u), -2.0, 2.0 + 0.8 * math.sin(PI * u)), 0.5, lerp(0.0, -PI * 1.4, u))
    m.apply(P('scream', lL=(0.6, 0.8), lR=(-0.2, 0.6)))
    m.face = 'shut'
    out = 1 - sm((k - 0.8) / 0.18)
    S['hatchl'].data.energy = 900 * out
    for l in S['portl']:
        l.data.energy = 200 * out
    S['bg'].inputs[1].default_value = 0.35 * out
    shoot(S, CAB, (0.0, 3.6, 2.4), (0.0, -4.0, 2.2), 20, roll)


# ---------------------------------------------------------------- alone: what is broken, what she has
def radio_dead(S, k, t, lt):
    """The wet chart table, water slopping on the floor: she holds the radio microphone to her mouth and calls, again; the set is dark. Rook stands in
    the water by the steps and slowly shakes his head."""
    cabin(S, t, 0.55, 700, 160, 0.8)
    m = S['tami']
    m.place(at(CAB, 1.25, 3.0, 0.0), facing((1.25, 3.0), (2.6, 2.0)))
    m.apply(P('stand', aR=(1.2, -0.2, 2.2, 0.6), aL=(0.9, 0.1, 0.9), lean=0.1, head=(0.0 + 0.1 * math.sin(lt * 2), 0.3)))
    m.face, m.jawv = 'hard', 0.5 * abs(math.sin(lt * 6))
    S['mic'].parent = m.hands[1]
    S['mic'].location, S['mic'].rotation_euler = (0, -0.2, -0.55), (0.3, 0, 0)
    span(S['cord'], wpos(m.hands[1], (0, -0.2, -0.6)), at(CAB, 2.95, 3.0, 2.4), 0.02)
    rk = S['rook']
    rk.place(at(CAB, -0.6, 3.4, 0.0), facing((-0.6, 3.4), (0.9, 2.0)))
    rk.apply(P('stand', aL=(0.3, 0.2, 0.4), head=(0.2, 0.35 * math.sin(lt * 4))))
    S['rface'] = 'sad'
    shoot(S, CAB, (lerp(2.95, 2.85, k), lerp(1.1, 1.4, k), lerp(3.0, 2.9, k)), (1.1, 3.4, 2.4), 22)


def beacon(S, k, t, lt):
    """She sits on the settee step with the yellow emergency beacon in both hands, turns it over, presses, shakes it: the lamp on top stays dead. Rook
    bends down beside her and peers at the dead lamp."""
    cabin(S, t, 0.45, 800, 200, 0.6)
    m = S['tami']
    m.place(at(CAB, -1.4, -0.5, 1.3 - 0.75), PI / 2)
    m.apply(P('sit', aL=(1.0, -0.2, 1.4, 0.6), aR=(1.0, -0.2, 1.4, 0.6), head=(0.45, 0.0)))
    m.face = 'tired'
    S['beacon'].parent = m.hands[1]
    sh = 0.25 * math.sin(lt * 14) * sm((lt - 1.0) / 0.3)
    S['beacon'].location, S['beacon'].rotation_euler = (0.3, -0.2, -0.5), (0.4 + sh, 0.0, 0.3)
    S['beacon'].scale = (1.3, 1.3, 1.3)
    rk = S['rook']
    rk.place(at(CAB, -0.2, 1.0, 0.0), facing((-0.2, 1.0), (-1.0, -0.4)))
    rk.apply(P('stand', lean=0.5, aL=(0.4, 0.1, 1.2), aR=(0.2, 0.3, 0.8), head=(0.5, 0.0)))
    S['rface'] = 'low'
    shoot(S, CAB, (lerp(1.7, 1.4, k), lerp(-2.6, -2.3, k), lerp(2.6, 2.5, k)), (-0.7, -0.2, 1.8), 28)


# ---------------------------------------------------------------- tins, the log, his shirt
def tins_count(S, k, t, lt):
    """On the dried-out settee: she sets out tins in rows, counting them under her breath; Rook, standing across from her, counts along with a wing
    feather, one tin at a time."""
    cabin(S, t, -1.5, 900, 220, 0.0)
    for o in S['flot']:
        o.location = FAR
    m = S['tami']
    m.place(at(CAB, -0.4, -2.2, 0.0), -PI / 2)
    reach = math.sin(lt * 3.2)
    m.apply(P('stand', aR=(1.2 + 0.2 * reach, 0.1, 0.5), aL=(0.5, 0.1, 1.4, 0.8), lean=0.45, head=(0.45, 0.0)))
    m.face, m.jawv = 'tired', 0.2 * abs(math.sin(lt * 7))
    n = 4 + int(11 * sm(k * 1.1))
    for i, o in enumerate(S['tins']):
        o.location = at(CAB, -1.95 + 0.3 * (i // 5), -3.2 + 0.32 * (i % 5) * 2, 1.45) if i < n else FAR
    rk = S['rook']
    rk.place(at(CAB, -1.0, -5.0, 0.0), facing((-1.0, -5.0), (-1.8, -2.8)))
    rk.apply(P('point', aR=(1.0, 0.0, 0.1), head=(0.45, 0.1 * math.sin(lt * 3.2))))
    S['rface'] = 'calm'
    shoot(S, CAB, (lerp(1.8, 1.5, k), lerp(-6.0, -5.6, k), lerp(3.3, 3.2, k)), (-1.3, -2.6, 1.6), 26)


def log_write(S, k, t, lt):
    """Night, the oil lamp lit on the chart table: she writes in the log, her pencil moving line by line. Rook sits on the companionway steps, hat in
    his lap, watching her write."""
    cabin(S, t, -1.5, 0, 0, 0.0)
    for o in S['flot']:
        o.location = FAR
    m = S['tami']
    m.place(at(CAB, 1.25, 3.0, 0.0), facing((1.25, 3.0), (2.6, 2.4)))
    w_ = math.sin(lt * 7)
    m.apply(P('stand', aR=(0.95, 0.1 + 0.08 * w_, 1.0), aL=(0.7, 0.1, 1.3), lean=0.35, head=(0.45, 0.0)))
    m.face = 'tired'
    S['logb'].location, S['logb'].rotation_euler = at(CAB, 2.2, 3.3, 1.6), (0, 0, 0.2)
    S['pencil'].parent = m.hands[1]
    S['pencil'].location, S['pencil'].rotation_euler = (0, -0.1, -0.6), (0.4, 0, 0)
    S['olamp'].location = at(CAB, 2.6, 4.3, 1.6)
    S['olight'].location, S['olight'].data.energy = at(CAB, 2.2, 4.1, 2.4), 260
    rk = S['rook']
    rk.place(at(CAB, 0.0, 4.9, 1.6 - 0.55), facing((0.0, 4.9), (1.6, 3.0)))
    rk.apply(P('sit', head=(0.3, 0.0)))
    S['hat_off'] = 1.0
    S['rface'] = 'soft'
    shoot(S, CAB, (lerp(2.95, 2.85, k), lerp(1.1, 1.4, k), lerp(3.0, 2.9, k)), (1.0, 3.6, 2.3), 22)


def shirt_night(S, k, t, lt):
    """Night: she lies curled on the settee, a man's folded blue shirt held against her chest; moonlight from the portholes. Her eyes are open."""
    cabin(S, t, -1.5, 0, 90, 0.0)
    for o in S['flot']:
        o.location = FAR
    for l in S['portl']:
        l.data.color = K.hexc('9CB8E8')[:3]
    m = on_settee(S, t, 0.0)
    m.apply(P('stand', aL=(1.3, -0.2, 1.8, 1.0), aR=(1.2, -0.2, 1.8, 1.0), lL=(0.9, 1.2), lR=(0.8, 1.3), head=(0.25, 0.3)))
    m.face = 'sad'
    S['shirt'].parent = m.body
    S['shirt'].location, S['shirt'].rotation_euler = (0, -0.38, 0.75), (1.4, 0, 0)
    h = thead(S)
    shoot(S, (0, 0, 0), (h[0] + lerp(1.9, 1.6, k), h[1] + lerp(1.2, 1.0, k), h[2] + lerp(1.6, 1.4, k)), (h[0], h[1] + 0.5, h[2] - 0.2), 32)


def voice_helm(S, k, t, lt):
    """Night at sea, stars out: she steers the wreck under its one small sail. Her head turns, slowly, towards the empty cockpit seat beside her, as if
    someone had spoken. Rook stands at the stern rail, hat held to his chest. The hush before the payoff."""
    sky(S, 'night', stars=True)
    afloat(S, t, 0.8, 'night', flow=5)
    jury(S, t, 1.0, 1.0)
    helm(S, t, 'soft', lerp(0.0, 0.9, sm((lt - 0.8) / 1.4)), 0.1)
    S['tami'].face = 'sad'
    aboard(S, S['rook'], -1.9, 7.6, D, PI - 0.6, P('stand', aL=(0.6, -0.2, 2.0, 1.0), head=(0.35, 0.0)), 'sad')
    S['hat_off'] = 1.0
    key(S, SEA, (-6, 4, 10), (0, 8, D + 2), 900, 'A8C4F0')
    shoot(S, SEA, (lerp(3.9, 3.5, k), lerp(4.0, 4.5, k), D + lerp(2.6, 2.4, k)), (-0.6, 8.0, D + 2.2), 30)


# ---------------------------------------------------------------- Hilo, and after
def hilo_quay(S, k, t, lt):
    """Hilo in the morning: the wreck tied up alongside the quay, her stump of a pole and the small sail; Tami sits on a bollard on the quay with a grey
    blanket round her shoulders, very thin, looking back at the yacht. Rook stands a little way off, hat in hand."""
    sky(S, 'dawn')
    d = setin(S, 'hiloq')
    d['sun'].data.energy = 60
    S['boat'].location = SP('hiloq', 0.0, -2.7, 0.0)
    S['boat'].rotation_euler = (0, 0.02 * math.sin(t), 0)
    jury(S, t, 1.0, 0.25)
    slack_line(S, t * 0.3)
    m = onset(S, S['tami'], 'hiloq', -2.0, 8.2, 2.5 - 0.55, facing((-2.0, 8.2), (0.5, -2.0)), P('sit', aL=(1.0, -0.2, 1.6, 1.0), aR=(1.0, -0.2, 1.6, 1.0), head=(0.2, 0.35)), 'tired')
    d['blanket'].parent = m.body
    d['blanket'].location, d['blanket'].rotation_euler, d['blanket'].scale = (0, 0.02, 0.5), (0, 0, 0), (1.05, 0.8, 0.95)
    onset(S, S['rook'], 'hiloq', 2.4, 10.0, 1.8, facing((2.4, 10.0), (-2.0, 8.2)), P('stand', aL=(0.6, -0.2, 2.0, 1.0), head=(0.25, 0.0)), 'soft')
    S['hat_off'] = 1.0
    shoot(S, HILOQ, (lerp(5.2, 4.6, k), lerp(2.6, 3.2, k), lerp(4.0, 3.8, k)), (-1.0, 8.6, 2.8), 30)


def desk_write(S, k, t, lt):
    """Years later, a study at night: she sits at a typewriter, typing, a stack of typed pages beside it, the dark sea in the window. Rook stands behind her
    chair reading a page he has picked up, and nods."""
    d = setin(S, 'desk')
    sky(S, 'cabin')
    d['lamp'].data.energy, d['room'].data.energy = 220, 300
    nocut(S)
    m = onset(S, S['tami'], 'desk', 0.6, 0.95, 1.08 - 0.55, PI, P('sit', aL=(1.15, 0.1, 1.0 + 0.2 * math.sin(lt * 11)), aR=(1.15, 0.1, 1.0 + 0.2 * math.sin(lt * 13 + 1)),
                                                               head=(0.35, 0.0)), 'hard')
    rk = onset(S, S['rook'], 'desk', -1.6, -0.6, 0.0, facing((-1.6, -0.6), (0.6, 2.6)) + 0.4, P('stand', aR=(1.2, 0.1, 1.5, 0.3), head=(0.35 + 0.1 * math.sin(lt * 3), 0.0)), 'calm')
    S['logb'].parent = rk.hands[1]
    S['logb'].location, S['logb'].rotation_euler, S['logb'].scale = (0.0, -0.3, -0.6), (1.2, 0, 0.0), (0.7, 1.0, 0.3)
    shoot(S, DESK, (lerp(4.4, 4.0, k), lerp(-2.6, -2.2, k), lerp(3.5, 3.4, k)), (0.2, 1.6, 2.6), 28)


def book_close(S, k, t, lt):
    """Close on the desk under the lamp: her hands square the stack of typed pages and lay them beside a plain red book; the typewriter in the edge
    of frame."""
    d = setin(S, 'desk')
    sky(S, 'cabin')
    d['lamp'].data.energy, d['room'].data.energy = 260, 120
    nocut(S)
    u = sm(lt / 1.2)
    m = onset(S, S['tami'], 'desk', 1.4, 1.0, 1.08 - 0.55, PI + 0.4, P('sit', aL=(lerp(1.1, 1.3, u), 0.1, 0.8), aR=(lerp(1.1, 1.3, u), 0.3, 0.8), lean=0.45, head=(0.55, 0.0)), 'warm')
    d['pages'].location = (lerp(2.1, 1.3, u), 2.4, 1.66)
    shoot(S, DESK, (lerp(2.6, 2.4, k), lerp(4.4, 4.2, k), lerp(3.0, 2.9, k)), (0.9, 2.0, 1.9), 28)


def pendant(S, k, t, lt):
    """Close on her at the tiller of a small sloop in bright sun, years on: at her neck, on a fine chain, a tiny gold sextant catches the light."""
    sky(S, 'day')
    sea(S, t, 0.9, 10, 'day')
    S['boat'].location = FAR
    b = S['sloop']
    b.location = at(SEA, 0, 0, 0.1 * math.sin(t * 1.5))
    b.rotation_euler = (0.03 * math.sin(t * 1.2), -0.2 + 0.03 * math.sin(t), 0)
    m = S['tami']
    m.root.parent = b
    m.place((0.9, 4.4, 1.35), 0.15)
    m.apply(P('stand', aL=(0.9, 0.3, 0.6), aR=(0.4, 0.3, 0.5), lL=(0.2, 0.2), lR=(-0.1, 0.1), head=(-0.15, 0.2 * math.sin(lt * 0.7))))
    m.face = 'warm'
    nocut(S)
    S['chain'].parent = m.body
    S['chain'].location, S['chain'].rotation_euler = (0, -0.06, 1.2), (0.5, 0, 0)
    S['pend'].parent = m.body
    S['pend'].location, S['pend'].rotation_euler = (0, -0.36, 1.02), (0.0, 0.25 * math.sin(lt * 2), 0)
    S['pend'].scale = (1.4, 1.4, 1.4)
    S['pglint'].scale = tuple(0.5 + 1.5 * abs(math.sin(t * 4.3)) for _ in range(3))
    p = wpos(S['pend'])
    a = 0.15 + 0.15 * k
    shoot(S, (0, 0, 0), (p[0] + 1.8 * math.sin(a) - 0.2, p[1] - 1.8 * math.cos(a), p[2] + 0.45), (p[0], p[1], p[2] + 0.35), 40)


def photo_thumb(S, k, t, lt):
    """Thumbnail: the dismasted yacht under its one small sail on a big grey sea, her at the wheel, seen from low and close at the stern quarter,
    placed right of frame; open sea and sky to the left for the words."""
    sky(S, 'grey')
    afloat(S, 0.6, 1.3, 'grey')
    jury(S, 0.6, 1.0, 1.0)
    helm(S, 0.6, 'hard', -0.5, -0.05)
    shoot(S, SEA, (13.0, 19.0, 3.4), (-6.5, 1.5, 4.2), 30)


def photo_quay(S, k, t, lt):
    sky(S, 'day')
    S['sun'].data.energy = 2.4
    setin(S, 'quay')
    whole(S, 0.5, 0.15, at_=SP('quay', 0, -2.6, 0))
    nocut(S)
    shoot(S, QUAY, (-22, -24, 8), (0, 2, 7), 34)


NEW = (harbour_wide, quay, quay_load, sail_out, easy_sail, radio_chart, clouds_build, reef_run, hatch_below, hear_shout, tumble, radio_dead, beacon,
       tins_count, log_write, shirt_night, voice_helm, hilo_quay, desk_write, book_close, pendant)
SHOTS3D.update({f.__name__: f for f in NEW})
STILLS = dict(STILLS, thumb=photo_thumb, quay=photo_quay)
HOST |= {'quay', 'quay_load', 'easy_sail', 'radio_chart', 'reef_run', 'radio_dead', 'beacon', 'tins_count', 'log_write', 'voice_helm', 'hilo_quay', 'desk_write'}
CAMFILL.update(harbour_wide=0, quay=80, quay_load=80, sail_out=0, easy_sail=80, radio_chart=200, clouds_build=0, reef_run=1500, hatch_below=200,
               hear_shout=160, tumble=120, radio_dead=200, beacon=200, tins_count=160, log_write=160, shirt_night=120, voice_helm=500, hilo_quay=120,
               desk_write=160, book_close=120, pendant=60)

# The Short's shots were timed for about a second each; here they run two to three times as long. Their acting is spread over the
# first 1.4 s of a shot (lt is slowed, never sped up) and every shot also swings a little round its own subject, so a held frame
# keeps moving. prm "orb": [degrees, dolly, rise] sets the swing for one shot.
SHORT_KINDS = set(SHOTS3D) - {f.__name__ for f in NEW}
SWING = dict(harbour_wide=3.0, clouds_build=2.0, tumble=0.0, sail_out=4.0, storm_wave=3.0, storm_roll=3.0, pendant=4.0)


def _slowed(f):
    def g(S, k, t, lt):
        f(S, k, t, min(lt, 1.4 * k))
    g.__name__ = f.__name__
    return g


def _swung(f, name):
    sign = 1 if sum(map(ord, name)) % 2 else -1
    rate = SWING.get(name, 6.0)

    def g(S, k, t, lt):
        f(S, k, t, lt)
        d = lt / k if k > 0.02 else 3.0
        o = S['prm'].get('orb')
        deg, dolly, rise = (list(o) + [0, 0])[:3] if o else (sign * rate * d, min(0.2, 0.04 * d), 0.0)
        c, tg = S['camrig'].location, S['camtgt'].location
        a = math.radians(deg) * (k - 0.5)
        m = 1 - dolly * (k - 0.5)
        dx, dy = c[0] - tg[0], c[1] - tg[1]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, c[2] + rise * (k - 0.5))
    g.__name__ = f.__name__
    return g


for _n in SHORT_KINDS:
    if _n != 'wake':
        SHOTS3D[_n] = _slowed(SHOTS3D[_n])
SHOTS3D = {name: _swung(f, name) for name, f in SHOTS3D.items()}
