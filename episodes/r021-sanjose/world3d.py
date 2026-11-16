"""Case 021 in 3D - the San Jose mine, Chile, 2010. On 5 August 2010 the mine near Copiapo in the Atacama
desert collapsed and 33 men were trapped about 700 metres underground. Seventeen days later, on 22 August,
a probe drill broke through near their shelter and came back up with a note tied to it, written in red ink.
A wider shaft was then drilled, and on 13 October all 33 were lifted out, one at a time, in a steel capsule.

Built for this story only: a drill site in a desert at night and by day (a lattice derrick over a narrow
borehole, a camp of tents, later a winch tower over a wide shaft), a mine gallery in brown rock with a
shelter at one end (bench, food cabinet, table), and a cut-away rescue shaft.

Everything is a generic low-poly reconstruction, not a model of the real site, rigs or capsule. The miners,
rescuers and families are simple figures and nobody's likeness is attempted. No flag, emblem, company name,
logo or lettering appears in the sets. The capsule is drawn as an open cage so that the man inside can be
seen; the real one was closed. Its white, blue and red bands follow the sources' description of its paint."""
import math

import bpy
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
SETS = dict(surf=(0, 0, 0), mine=(5000, 0, 0), shaft=(10000, 0, 0))
AWAY = (0, 0, -4000)
HOST = {'bit_out', 'rook_rig', 'rook_peer', 'unfold', 'cheer', 'faces', 'tents', 'line_up', 'hole_measure', 'big_drill', 'rook_stuck',
        'capsule_arrive', 'emerge', 'hug', 'rook_wrong', 'signoff'}
CAMFILL = {'*': 150, 'tie_note': 240, 'drill_up': 260, 'rig_night': 80, 'refuge_wide': 380, 'faces': 220, 'cabinet': 240, 'spoon': 200,
           'line_up': 260, 'break_through': 300, 'capsule_arrive': 320, 'step_in': 260, 'shaft_ride': 260, 'ride_face': 160, 'last_up': 300,
           'hole_measure': 40, 'big_drill': 40, 'rook_stuck': 60, 'rook_wrong': 50, 'signoff': 60, 'tents': 200, 'emerge': 200, 'hug': 200}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SAND, SANDD, SANDL = 'B4875A', '8A6240', 'D2A878'
ORE, ORED, OREL, OREG = '6A5244', '3E2F28', '8C7260', '4E6A5E'
STEEL, STEELD, YEL = '8A90A0', '4A4F5C', 'E0B020'
PAPER, RED = 'F4EEDC', 'D8261E'
SKINS = ('B8805A', 'A8704C', 'C89468')
OVERALL = ('7A5230', '5A5E48', '6A6A74', '8A4A2C')
HELM = ('F2F2EC', 'E0B020', 'C8372D', 'E07A1E')
HOLE = (0.0, -2.6)            # the narrow borehole at the surface
SITE = (16.0, 0.0)            # the wide rescue shaft at the surface
CAMP = (-16.0, 5.0)           # the tents
PROBE = (0.0, 1.0)            # where the probe drill comes through the gallery roof
DROP = (-7.0, 0.0)            # where the rescue shaft comes through the gallery roof
ROOF = 7.0
BENCH = [(5.6 + 1.25 * i, 3.75) for i in range(6)]
_KEEP = []


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def loc(name, x, y, z):
    o = SETS[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def stage(name, fn):
    """One set per collection at its own origin, so that only the set in use is rendered."""
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
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def rn(i, j=0):
    return (math.sin(i * 91.17 + j * 47.33) * 24634.6345) % 1


def seen(objs, on):
    for o in objs:
        o.hide_render = not on


def tree_of(o):
    return [o] + [c for ch in o.children for c in tree_of(ch)]


def look_yaw(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def span(o, a, b, w):
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def tube(r, col, a, b, w, **kw):
    o = add('cylinder', col, radius=0.5, depth=1, vertices=6, parent=r, **kw)
    span(o, a, b, w)
    return o


def world_of(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def lerp_hex(a, b, k):
    k = max(0.0, min(1.0, k))
    pa, pb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join(f'{int(x + (y - x) * k):02X}' for x, y in zip(pa, pb))


def chunks(r, n, seed, fn, cols, s0=0.8, s1=1.8, flat=1.0):
    """Faceted rocks scattered by fn(j) -> (x, y, z)."""
    for j in range(n):
        s = lerp(s0, s1, rn(j, seed))
        add('ico_sphere', cols[j % len(cols)], fn(j), rot=(rn(j, seed + 1) * 3, rn(j, seed + 2) * 3, rn(j, seed + 3) * 3),
            scale=(s, s * lerp(0.7, 1.2, rn(j, seed + 4)), s * flat), radius=1, subdivisions=1, parent=r)


# ---------------------------------------------------------------- the sets
def set_surf(r):
    """A drill site in a stony desert: derrick over the narrow borehole, tents to one side, the rescue shaft to the other."""
    add('plane', SAND, (0, 0, 0), size=600, parent=r)
    for j in range(16):                                                       # bare hills all round
        a = j / 16 * 2 * PI + 0.2 * rn(j, 1)
        d = 70 + 50 * rn(j, 2)
        add('cone', (SANDD, SAND, '9A7450')[j % 3], (d * math.cos(a), d * math.sin(a), 0), radius1=26 + 22 * rn(j, 3), radius2=2, depth=14 + 22 * rn(j, 4),
            vertices=7, parent=r)
    chunks(r, 46, 5, lambda j: ((rn(j, 6) - 0.5) * 70, -8 + rn(j, 7) * 50 if j % 3 else -12 - rn(j, 7) * 14, 0.05), (SANDD, '6E5038', SANDL), 0.15, 0.6, 0.6)
    # the probe rig: a deck with a motor house behind, a lattice derrick straddling the borehole in front
    add('cube', STEELD, (0, 0.8, 0.2), scale=(5.2, 4.2, 0.4), size=1, parent=r)
    add('cube', 'C8A030', (0.4, 1.6, 1.5), scale=(3.0, 2.4, 2.2), size=1, parent=r)
    add('cube', '2A2E38', (0.4, 0.38, 1.8), scale=(2.2, 0.06, 0.9), size=1, parent=r)
    add('cylinder', '3A3F4C', (-1.6, 1.6, 1.2), radius=0.5, depth=1.6, vertices=8, parent=r)
    add('cylinder', '2A2E38', (-1.6, 1.6, 2.6), radius=0.09, depth=1.4, vertices=5, parent=r)
    hx, hy = HOLE
    add('cylinder', STEELD, (hx, hy, 0.12), radius=0.42, depth=0.24, vertices=10, parent=r)
    add('cylinder', '050505', (hx, hy, 0.245), radius=0.24, depth=0.02, vertices=10, parent=r)
    posts = [(hx + sx * 1.0, hy + sy * 1.0) for sx in (-1, 1) for sy in (-1, 1)]
    top = 13.0
    for (px, py) in posts:
        tube(r, STEEL, (px, py, 0), (hx + (px - hx) * 0.45, hy + (py - hy) * 0.45, top), 0.07)
    for lv in range(5):
        z0, z1 = 2.0 + lv * 2.2, 4.2 + lv * 2.2
        f0, f1 = 1 - 0.55 * z0 / top, 1 - 0.55 * z1 / top
        for i in range(4):
            a, b = posts[(0, 1, 3, 2)[i]], posts[(1, 3, 2, 0)[i]]
            tube(r, STEEL, (hx + (a[0] - hx) * f0, hy + (a[1] - hy) * f0, z0), (hx + (b[0] - hx) * f1, hy + (b[1] - hy) * f1, z1), 0.035)
            tube(r, STEEL, (hx + (a[0] - hx) * f0, hy + (a[1] - hy) * f0, z0), (hx + (b[0] - hx) * f0, hy + (b[1] - hy) * f0, z0), 0.035)
    add('cube', YEL, (hx, hy, top + 0.3), scale=(1.3, 1.3, 0.6), size=1, parent=r)
    crown = add('cube', 'FFE8B0', (hx, hy, top - 0.1), scale=(0.6, 0.6, 0.12), size=1, parent=r, emit=6.0)
    # floodlight masts
    floods = []
    for (fx, fy, fz) in ((-6.5, -5.0, 6.5), (7.5, 3.0, 7.5), (SITE[0] + 7.0, -5.0, 7.5), (CAMP[0] + 2.0, CAMP[1] - 6.0, 5.0)):
        tube(r, STEELD, (fx, fy, 0), (fx, fy, fz), 0.08)
        floods.append(add('cube', 'FFF2D0', (fx, fy, fz + 0.3), scale=(1.3, 0.3, 0.7), size=1, parent=r, emit=7.0))
    # the camp: three tents and a line of small lamps
    cx, cy = CAMP
    for j, (tx, ty, tc) in enumerate(((-3.6, 3.0, 'D8D0B8'), (0.8, 4.2, '6E84A0'), (5.0, 2.6, 'C87850'))):
        add('cone', tc, (cx + tx, cy + ty, 1.4), rot=(0, 0, 0.6 + j), radius1=2.6, radius2=0.0, depth=2.8, vertices=4, parent=r)
        add('cube', '2A2420', (cx + tx - 0.2, cy + ty - 1.75, 0.8), rot=(0, 0, 0.1), scale=(0.9, 0.05, 1.5), size=1, parent=r)
    lamps = [add('ico_sphere', 'FFD890', (cx - 5.0 + 2.0 * j, cy - 1.4 - 0.5 * (j % 2), 0.22), radius=0.16, subdivisions=1, parent=r, emit=9.0) for j in range(6)]
    # the rescue site: collar of the wide shaft, winch tower with a sheave wheel
    sx, sy = SITE
    kit = [add('cylinder', 'C8CCD4', (sx, sy, 0.16), radius=1.15, depth=0.32, vertices=14, parent=r),
           add('cylinder', '050505', (sx, sy, 0.33), radius=0.86, depth=0.02, vertices=14, parent=r)]
    for (lx, ly) in ((-3.2, 2.6), (3.2, 2.6), (-2.4, -2.6), (2.4, -2.6)):
        kit.append(tube(r, YEL, (sx + lx, sy + ly, 0), (sx + lx * 0.16, sy + 0.5, 11.2), 0.1))
    for z in (3.6, 7.2):
        f = 1 - 0.84 * z / 11.2
        kit.append(tube(r, YEL, (sx - 3.2 * f, sy + 0.5 + 2.1 * f, z), (sx + 3.2 * f, sy + 0.5 + 2.1 * f, z), 0.05))
    kit.append(add('cube', YEL, (sx, sy + 0.5, 11.3), scale=(1.5, 1.0, 0.35), size=1, parent=r))
    wheel = add('torus', STEELD, (sx, sy + 0.05, 11.0), rot=(0, PI / 2, 0), major_radius=0.85, minor_radius=0.09, major_segments=14, minor_segments=5, parent=r)
    for j in range(3):
        add('cube', STEEL, (0, 0, 0), rot=(0, 0, j * PI / 3), scale=(1.6, 0.07, 0.07), size=1, parent=wheel)
    kit.append(wheel)
    kit.append(add('cube', 'D8DCE4', (sx + 5.0, sy + 6.0, 1.3), scale=(4.4, 2.4, 2.6), size=1, parent=r))             # a site cabin
    kit.append(add('cube', '2A2E38', (sx + 4.2, sy + 4.78, 1.2), scale=(0.9, 0.05, 1.9), size=1, parent=r))
    kit += [c for o in kit for c in o.children]
    return dict(floods=floods, lamps=lamps, crown=crown, kit=kit, wheel=wheel)


def set_mine(r):
    """A gallery in brown ore rock. The shelter is the far (+x) end: bench, food cabinet, table."""
    add('plane', ORED, (0, 0, 0), size=90, parent=r)
    add('cube', ORED, (0, -3, ROOF + 0.6), scale=(60, 30, 1.2), size=1, parent=r)                                     # the roof
    add('cube', ORE, (0, 6.6, 4), scale=(60, 1.2, 9), size=1, parent=r)                                               # back wall
    for sx in (-1, 1):
        add('cube', ORE, (sx * 16.5, -3, 4), scale=(1.2, 30, 9), size=1, parent=r)
    chunks(r, 30, 11, lambda j: (-15.5 + j * 1.07, 5.6 + 0.5 * rn(j, 12), 0.6 + 6.0 * rn(j, 13)), (ORE, OREL, ORED, OREG), 0.9, 1.9)
    chunks(r, 16, 15, lambda j: (-15 + j * 2.0, 5.2 + 0.5 * rn(j, 16), 0.2), (ORED, ORE), 0.7, 1.3, 0.7)
    chunks(r, 20, 17, lambda j: (-15 + j * 1.6 + rn(j, 18), -6 + 9.0 * rn(j, 19), ROOF + 0.25), (ORE, ORED, OREL), 0.6, 1.5, 0.45)
    chunks(r, 12, 21, lambda j: ((1 if j % 2 else -1) * (15.4 + 0.4 * rn(j, 22)), -5 + 10 * rn(j, 23), 0.5 + 6.0 * rn(j, 24)), (ORE, OREL, ORED), 1.0, 1.9)
    chunks(r, 22, 25, lambda j: (-14 + 28 * rn(j, 26), -5.5 + 9.5 * rn(j, 27), 0.03), (ORED, '2A201C', ORE), 0.1, 0.34, 0.5)
    # two steel arches mark the way into the shelter
    for ax in (4.2, 4.9):
        for ay in (-3.6, 5.0):
            tube(r, YEL, (ax, ay, 0), (ax, ay, 5.2), 0.09)
        tube(r, YEL, (ax, -3.6, 5.2), (ax, 5.0, 5.2), 0.09)
    add('cube', '7A5A3A', (8.7, 4.25, 0.72), scale=(8.0, 0.9, 0.14), size=1, parent=r)                                # the bench
    for bx in (5.2, 8.7, 12.2):
        add('cube', '4A3626', (bx, 4.25, 0.33), scale=(0.16, 0.8, 0.66), size=1, parent=r)
    # the food cabinet: open-fronted locker on the right wall
    cab = empty((13.6, 1.2, 0), r)
    add('cube', 'B8BEC6', (0.0, 0.52, 1.5), scale=(1.9, 0.06, 3.0), size=1, parent=cab)
    for sx in (-0.93, 0.93):
        add('cube', 'A4AAB4', (sx, 0.12, 1.5), scale=(0.06, 0.86, 3.0), size=1, parent=cab)
    for z in (0.5, 1.4, 2.3, 2.98):
        add('cube', 'A4AAB4', (0, 0.12, z), scale=(1.9, 0.86, 0.06), size=1, parent=cab)
    add('cube', '6E7480', (1.15, -0.72, 1.5), rot=(0, 0, 1.1), scale=(0.9, 0.05, 2.9), size=1, parent=cab)             # its door, standing open
    add('cube', '8A8E96', (10.6, 0.6, 1.0), scale=(1.9, 1.1, 0.1), size=1, parent=r)                                  # a steel table
    for (lx, ly) in ((-0.85, -0.45), (0.85, -0.45), (-0.85, 0.45), (0.85, 0.45)):
        add('cube', '5A5E66', (10.6 + lx, 0.6 + ly, 0.5), scale=(0.08, 0.08, 1.0), size=1, parent=r)
    add('cylinder', '3A6A8A', (6.3, 5.0, 0.9), radius=0.5, depth=1.8, vertices=8, parent=r)                           # a water drum
    # where the probe came through, and where the rescue shaft will
    add('torus', '120E0C', (PROBE[0], PROBE[1], ROOF - 0.02), major_radius=0.3, minor_radius=0.12, major_segments=10, minor_segments=4, parent=r)
    drop = [add('cylinder', '050404', (DROP[0], DROP[1], ROOF - 0.03), radius=1.05, depth=0.1, vertices=14, parent=r)]
    for j in range(9):
        a = j / 9 * 2 * PI
        drop.append(add('ico_sphere', (OREL, ORE)[j % 2], (DROP[0] + 1.25 * math.cos(a), DROP[1] + 1.25 * math.sin(a), ROOF - 0.05),
                        scale=(0.45, 0.45, 0.3), radius=1, subdivisions=1, parent=r))
    pile = [add('ico_sphere', (ORE, OREL, ORED)[j % 3], (DROP[0] + 1.7 * math.cos(j * 2.4) * (0.5 + 0.5 * rn(j, 31)), DROP[1] + 1.4 * math.sin(j * 2.4), 0.2),
                rot=(j, j * 2, 0), scale=(0.45, 0.4, 0.3), radius=1, subdivisions=1, parent=r) for j in range(9)]
    return dict(drop=drop, pile=pile, cab=cab)


def set_shaft(r):
    """A cut-away of the rescue shaft: only the far half of the bore is built, so the camera can ride beside the capsule."""
    for lv in range(26):
        z = -9 + lv * 3.0
        for i in range(7):
            a = (i + 0.5) / 7 * PI
            col = (ORE, OREL, ORED, OREG, '5A4438')[int(rn(lv, i) * 5)]
            add('cube', col, (1.75 * math.cos(a), 1.75 * math.sin(a), z), rot=(0, 0, a + PI / 2), scale=(0.86, 0.45 + 0.25 * rn(lv, i + 9), 3.02), size=1, parent=r)
        for j in range(2):
            a = (0.15 + 0.7 * rn(lv, j + 20)) * PI
            add('ico_sphere', (OREL, 'B89A6A')[j], (1.45 * math.cos(a), 1.45 * math.sin(a), z + 1.5 * rn(lv, j + 30)), scale=(0.22, 0.2, 0.3), radius=1,
                subdivisions=1, parent=r)
    return {}


# ---------------------------------------------------------------- the cast and the props
def miner_head(skin, helm, hair='1A1614'):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('cylinder', helm, (0, -0.02, 0.2), radius=0.4, depth=0.05, vertices=10, parent=head, rough=0.4)
        add('cone', helm, (0, 0.02, 0.33), radius1=0.34, radius2=0.2, depth=0.24, vertices=9, parent=head, rough=0.4)
        add('cube', '2A2E38', (0, -0.3, 0.33), scale=(0.16, 0.1, 0.13), size=1, parent=head)
        d['lamp'] = add('cube', 'FFF2C0', (0, -0.36, 0.33), scale=(0.11, 0.03, 0.09), size=1, parent=head, emit=8.0)
        return d
    return fn


def make_drill():
    """The end of the probe string: pipe, bit, and the note tied on above the bit."""
    d = keep(empty(AWAY))
    add('cylinder', STEEL, (0, 0, 20.5), radius=0.1, depth=40, vertices=8, parent=d, rough=0.35)
    add('cylinder', STEELD, (0, 0, 0.42), radius=0.19, depth=0.5, vertices=8, parent=d, rough=0.4)
    for j in range(3):
        a = j * 2 * PI / 3
        add('cone', 'B8BCC8', (0.1 * math.cos(a), 0.1 * math.sin(a), 0.1), rot=(PI, 0, 0), radius1=0.12, radius2=0.03, depth=0.26, vertices=6, parent=d, rough=0.3)
    note = empty((0, 0, 1.25), d)
    add('cylinder', PAPER, (0, 0, 0), radius=0.15, depth=0.55, vertices=8, parent=note, rough=0.8)                    # paper wrapped round the pipe
    add('cube', PAPER, (0.2, -0.1, -0.02), rot=(0, 0, -0.5), scale=(0.34, 0.02, 0.44), size=1, parent=note, rough=0.8)   # its loose corner
    for z in (-0.12, 0.0, 0.12):
        add('cube', RED, (0.2, -0.115, z - 0.02), rot=(0, 0, -0.5), scale=(0.24, 0.012, 0.035), size=1, parent=note, emit=0.6)
    bands = [add('torus', 'E07A1E', (0, 0, z), major_radius=0.16, minor_radius=0.025, major_segments=10, minor_segments=4, parent=note) for z in (-0.2, 0.2)]
    return d, note, bands


def make_capsule():
    c = keep(empty(AWAY))
    add('cylinder', '2A4EA0', (0, 0, 0.35), radius=0.74, depth=0.7, vertices=12, parent=c, rough=0.4)
    add('cylinder', 'C8322E', (0, 0, 3.85), radius=0.74, depth=0.7, vertices=12, parent=c, rough=0.4)
    add('cone', 'E8E8E4', (0, 0, 4.45), radius1=0.74, radius2=0.2, depth=0.5, vertices=12, parent=c, rough=0.4)
    for j in range(6):
        a = (j + 0.5) / 6 * 2 * PI
        tube(c, 'E8E8E4', (0.72 * math.cos(a), 0.72 * math.sin(a), 0.7), (0.72 * math.cos(a), 0.72 * math.sin(a), 3.5), 0.03)
    for z in (0.72, 2.1, 3.48):
        add('torus', 'E8E8E4', (0, 0, z), major_radius=0.72, minor_radius=0.035, major_segments=14, minor_segments=4, parent=c)
    for z in (0.35, 3.85):
        for j in range(3):
            a = j * 2 * PI / 3 + 0.5
            add('cylinder', '2A2E38', (0.8 * math.cos(a), 0.8 * math.sin(a), z), rot=(PI / 2, 0, a), radius=0.14, depth=0.1, vertices=8, parent=c)
    return c


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = dict(colls={})
    for name, fn in (('surf', set_surf), ('mine', set_mine), ('shaft', set_shaft)):
        S['colls'][name], S[name] = stage(name, fn)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['rook'].sc = 1.0
    S['men'] = []
    for i in range(12):
        sk = SKINS[i % 3]
        rig = K.Rig(dict(top=OVERALL[i % 4], pants=OVERALL[(i + 1) % 4], hand=sk, boot='2A2420', fore=OVERALL[i % 4]),
                    miner_head(sk, HELM[0] if i == 0 else HELM[1 + i % 3]))
        rig.sc = 0.94 + 0.03 * (i % 3)
        S['men'].append(rig)
    S['crew'] = []
    for i in range(3):
        rig = K.Rig(dict(top='B8322E', pants='8A2622', hand=SKINS[(i + 1) % 3], boot='22262E', fore='B8322E'), miner_head(SKINS[(i + 1) % 3], 'F2F2EC'))
        rig.sc = 1.0
        S['crew'].append(rig)
    S['civ'] = []
    for i, (top, hair) in enumerate((('4A7A9A', '2A1C14'), ('A8506A', '17131A'), ('D8C8A0', '5A4A3A'))):
        rig = K.Rig(dict(top=top, pants='2E3444', hand=SKINS[i], boot='3A3028', fore=top), K.human_head(SKINS[i], hair))
        rig.sc = (0.96, 0.9, 0.98)[i]
        S['civ'].append(rig)
    S['humans'] = S['men'] + S['crew'] + S['civ']
    S['cast'] = [S['rook']] + S['humans']
    S['drill'], S['note'], S['bands'] = make_drill()
    S['cap'] = make_capsule()
    S['bigbit'] = bb = keep(empty(AWAY))                                                              # the wide shaft's drill head
    add('cylinder', STEEL, (0, 0, 20.9), radius=0.42, depth=40, vertices=10, parent=bb, rough=0.35)
    add('cylinder', STEELD, (0, 0, 0.55), radius=0.82, depth=0.7, vertices=10, parent=bb, rough=0.4)
    for j in range(6):
        a = j * PI / 3
        add('cone', 'C8CCD4', (0.5 * math.cos(a), 0.5 * math.sin(a), 0.08), rot=(PI, 0, 0), radius1=0.24, radius2=0.05, depth=0.36, vertices=6, parent=bb, rough=0.3)
        add('cube', YEL, (0.43 * math.cos(a), 0.43 * math.sin(a), 6.0 + j * 2.2), rot=(0, 0, a), scale=(0.16, 0.3, 0.5), size=1, parent=bb)
    S['sheet'] = sh = keep(empty(AWAY))                                                                # the note, unfolded
    add('cube', PAPER, (0, 0, 0), scale=(1.15, 0.02, 0.8), size=1, parent=sh, rough=0.8)
    for j, wd in enumerate((0.9, 0.95, 0.6)):
        add('cube', RED, (-(0.95 - wd) / 2, -0.016, 0.22 - 0.2 * j), scale=(wd, 0.012, 0.07), size=1, parent=sh, emit=0.5)
    for x in (-0.19, 0.19):
        add('cube', 'D8D0BC', (x, -0.014, 0), scale=(0.012, 0.012, 0.8), size=1, parent=sh)
    S['tins'] = [keep(add('cylinder', ('B8BCC8', 'C8A040')[j % 2], AWAY, radius=0.17, depth=0.16, vertices=9, rough=0.3)) for j in range(5)]
    S['carton'] = keep(add('cube', 'E8E8E0', AWAY, scale=(0.2, 0.2, 0.42), size=1))
    S['tuna'] = keep(add('cylinder', 'E0A088', AWAY, radius=0.145, depth=0.03, vertices=9))
    S['spoon'] = sp = keep(empty(AWAY))
    add('cube', 'D8DCE4', (0.32, 0, 0), scale=(0.62, 0.05, 0.02), size=1, parent=sp, rough=0.25)
    add('ico_sphere', 'D8DCE4', (-0.08, 0, -0.01), scale=(0.16, 0.11, 0.04), radius=1, subdivisions=2, parent=sp, rough=0.25)
    S['bite'] = add('ico_sphere', 'E0A088', (-0.08, 0, 0.035), scale=(0.11, 0.08, 0.05), radius=1, subdivisions=1, parent=sp)
    S['cups'] = [keep(add('cone', 'E8E4D8', AWAY, radius1=0.09, radius2=0.12, depth=0.18, vertices=8)) for _ in range(6)]
    S['hand'] = K.Hand(SKINS[0], OVERALL[0], 1.0)
    keep(S['hand'].root)
    S['ruler'] = keep(add('cube', 'FF7A1A', AWAY, scale=(1.3, 0.09, 0.03), size=1))
    S['coin'] = keep(add('cylinder', 'FFC233', AWAY, radius=0.11, depth=0.025, vertices=10, rough=0.25, emit=0.4))
    S['tooth'] = keep(add('cone', 'D8DCE4', AWAY, radius1=0.12, radius2=0.03, depth=0.26, vertices=6, rough=0.15, emit=0.25))
    S['fea'] = [keep(add('cone', '2F2B4D', AWAY, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(2)]
    S['dust'] = [keep(add('ico_sphere', 'E8D4B4', AWAY, radius=0.2, subdivisions=1, rough=1.0)) for _ in range(14)]
    S['grit'] = [keep(add('ico_sphere', ORE, AWAY, radius=0.12, subdivisions=1)) for _ in range(10)]
    S['sparks'] = [keep(add('ico_sphere', 'FFD070', AWAY, radius=0.045, subdivisions=1, emit=14.0)) for _ in range(8)]
    S['ropes'] = [keep(add('cylinder', '2A2E38', AWAY, radius=0.5, depth=1, vertices=5, rough=0.5)) for _ in range(2)]
    S['topm'] = newmat('daylight', 'FFF2D8', 0.4, 0.0)
    S['top'] = keep(wear(add('cylinder', 'FFF2D8', AWAY, radius=1.6, depth=0.1, vertices=14), S['topm']))
    S['lamps'] = [light(AWAY, 0, 'FFF0C8', kind='POINT') for _ in range(6)]
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
    reset(S)
    return S


def sky(S, col, strength=1.0):
    S['bg'].inputs[0].default_value = K.hexc(col)
    S['bg'].inputs[1].default_value = strength


def only(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: loc(name, x, y, z)


def shoot(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='FFE8D0'):
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
        rig.root.scale = (rig.sc,) * 3
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    S['hand'].root.location = AWAY
    S['hand'].grip(0.2)
    U = S['surf']
    seen(U['kit'], False)
    for f in U['floods']:
        f.hide_render = False
    M = S['mine']
    seen(M['drop'], False)
    seen(M['pile'], False)
    S['bite'].hide_render = False
    paint(S['topm'], 'FFF2D8', 0.0)
    for l in S['lamps']:
        l.location = AWAY
        l.data.energy = 0
        l.data.color = K.hexc('FFF0C8')[:3]
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['rface'] = 'calm'
    S['hat_tip'] = 0.0
    S['hat_jump'] = 0.0
    S['hat_sq'] = 0.0
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync, after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.41) % 1 < 0.035
    ez = dict(calm=0.07, deadpan=0.05, shocked=0.13, sad=0.055, warm=0.06).get(e, 0.07)
    tilt = dict(deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, sq = S['hat_tip'], S['hat_sq']
    r['hat'].rotation_euler = (-0.2 + (0.12 if e == 'deadpan' else 0.0) + tip * 0.35 + sq * 0.25, 0.07 + sq * 0.3, 0)
    r['hat'].location = (0.0, 0.0, 0.27 + S['hat_jump'] + tip * 0.1 - sq * 0.06)
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.7, shut=0.07, tired=0.5, warm=0.85, squint=0.35, sad=0.6).get(f, 1.0)
        bl = (t * 0.29 + 0.21 * j) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for br in x['brows']:
            br.location.z = 0.125 + (0.03 if f == 'wide' else -0.012 if f in ('sad', 'tired', 'squint') else 0.0)
        x['mouth'].scale = (0.13 if f != 'warm' else 0.18, 0.03, 0.035 + 0.12 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- places and helpers for the shots
def env(S, name, skyc='000000', sun=0.0, sunc='FFFFFF', sdir=(-0.4, -0.6, 0.7), fk=2.4, skyk=1.0):
    A = only(S, name)
    sky(S, skyc, skyk)
    S['suntgt'].location = A(0, 0, 0)
    S['sun'].location = A(sdir[0] * 400, sdir[1] * 400, sdir[2] * 400)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(sunc)[:3]
    S['fillk'] = fk
    return A


def night(S, rescue=False):
    A = env(S, 'surf', '10183A', sun=0.9, sunc='9FB0F0', sdir=(0.5, -0.5, 0.7), fk=2.4, skyk=1.3)
    seen(S['surf']['kit'], rescue)
    return A


def day(S, rescue=True):
    A = env(S, 'surf', '8EC0E8', sun=5.0, sunc='FFEED0', sdir=(-0.5, -0.6, 0.6), fk=1.6, skyk=2.2)
    seen(S['surf']['kit'], rescue)
    return A


def dawn(S):
    A = env(S, 'surf', 'E8A070', sun=3.6, sunc='FFC890', sdir=(0.7, -0.5, 0.3), fk=1.8, skyk=1.8)
    seen(S['surf']['kit'], True)
    return A


def mine(S):
    return env(S, 'mine', '000000', fk=2.3)


def lampat(S, i, pos, e, col='FFF0C8'):
    S['lamps'][i].location = pos
    S['lamps'][i].data.energy = e
    S['lamps'][i].data.color = K.hexc(col)[:3]


def rope(S, i, a, b, w=0.03):
    span(S['ropes'][i], a, b, w)


def feather(S, pos, lt, t0=0.0, n=2):
    for i in range(n):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def grit(S, pos, t, n=8, spread=0.5, fall=4.0, rate=0.9):
    """Grit and small stones falling from the roof."""
    for i in range(n):
        u = (t * rate + rn(i, 71)) % 1
        S['grit'][i].location = (pos[0] + spread * (rn(i, 72) - 0.5) * 2, pos[1] + spread * (rn(i, 73) - 0.5) * 2, pos[2] - fall * u * u)
        s = 0.3 + 0.9 * rn(i, 74)
        S['grit'][i].scale = (s, s, s)
        S['grit'][i].rotation_euler = (u * 9, i, u * 5)


def puffs(S, pos, t, n=8, spread=1.2, rise=2.0, s=1.0, i0=0):
    """Dust boiling up from a point."""
    for i in range(n):
        u = (t * 0.6 + i / n) % 1
        o = S['dust'][i0 + i]
        a = i * 2.4
        o.location = (pos[0] + spread * u * math.cos(a), pos[1] + spread * u * math.sin(a), pos[2] + rise * u)
        q = s * (0.5 + 1.6 * u)
        o.scale = (q, q, q * 0.8)


def sit(rig, A, x, y, yaw=0.0, nod=0.3, turn=0.0, z=0.78, hug=False):
    """Sit a figure on the bench (or, with hug, on the floor hugging his knees)."""
    if hug:
        rig.place(A(x, y, 0.0), yaw)
        rig.apply(P('sit', lL=(1.75, 2.1), lR=(1.75, 2.1), aL=(1.2, -0.2, 1.2, 0.6), aR=(1.2, -0.2, 1.2, 0.6), lift=-0.62, lean=0.42, head=(nod, turn)))
    else:
        rig.place(A(x, y, z - 0.52 * rig.sc), yaw)
        rig.apply(P('sit', head=(nod, turn), lean=0.2))


def crowd(S, A, t, face='tired', nod=0.32, look=None, row_only=False):
    """The men in the shelter: six on the bench, three on the floor in front, three standing."""
    M = S['men']
    for i in range(6):
        x, y = BENCH[i]
        tr = 0.0 if look is None else max(-0.9, min(0.9, look_yaw((x, y), look)))
        sit(M[i + 1], A, x, y, 0.0, nod + 0.06 * math.sin(t * 0.8 + i), tr)
    for rig in M[1:]:
        rig.face = face
    if row_only:
        return
    for j, (x, y) in enumerate(((6.4, 2.0), (8.4, 1.7), (10.0, 2.3))):
        tr = 0.0 if look is None else max(-0.9, min(0.9, look_yaw((x, y), look)))
        sit(M[7 + j], A, x, y, 0.15 * (j - 1), nod, tr, hug=True)
    for j, (x, y, yw) in enumerate(((12.6, 3.0, -0.5), (5.0, 2.6, 0.5))):
        rig = (M[10], M[11])[j]
        rig.place(A(x, y, 0), yw if look is None else look_yaw((x, y), look))
        rig.apply(P('cross', head=(0.15, 0.0)))


def drill_at(S, A, z, x=PROBE[0], y=PROBE[1], spin=0.0):
    S['drill'].location = A(x, y, z)
    S['drill'].rotation_euler = (0, 0, spin)


def cap_at(S, A, x, y, z, rider=None, yaw=0.0, pose=None, spin=0.0):
    S['cap'].location = A(x, y, z)
    S['cap'].rotation_euler = (0, 0, spin)
    if rider is not None:
        rider.root.scale = (0.84,) * 3
        rider.place(A(x, y, z + 0.7), yaw)
        rider.apply(pose or P('stand', aL=(0.05, 0.02, 0.2), aR=(0.05, 0.02, 0.2)))


KNEEL = P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.45, aL=(0.7, 0.1, 0.7), aR=(1.0, 0.0, 0.5), head=(0.35, 0.0))


# ---------------------------------------------------------------- the hook: a note goes up
def tie_note(S, k, t, lt):
    """Close: a miner's hands tie the note on above the bit, his face behind it in the lamp. The opening and the last shot."""
    loop = S['prm'].get('loop')
    kk = 1 - k if loop else k
    A = mine(S)
    rise = 0.5 * sm((kk - 0.72) / 0.28)
    S['bands'][1].location.z = lerp(0.42, 0.2, sm(kk / 0.5))
    m = S['men'][3]
    mp = (0.42, 1.78)
    m.place(A(mp[0], mp[1], 0), look_yaw(mp, (0.3, -2.0)))
    wind = math.sin(lt * 13)
    go = sm((kk - 0.7) / 0.2)
    tying = P('stand', aL=(1.3, -0.3, 0.8, 0.5), aR=(1.3, -0.3, 0.8, 0.5), head=(0.26, 0.0), lean=0.12)
    m.apply(tying)
    hl, hr = world_of(m.hands[0], (0, -0.1, -0.1)), world_of(m.hands[1], (0, -0.1, -0.1))
    px, py, pz = (hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2 - 0.12, (hl[2] + hr[2]) / 2 - 1.25
    S['drill'].location = (px, py, pz + rise + 0.012 * math.sin(t * 40))
    S['drill'].rotation_euler = (0, 0, 2.5)
    m.apply(blend(P('stand', aL=(1.3 + 0.07 * wind, -0.3, 0.8, 0.5), aR=(1.3 - 0.07 * wind, -0.3, 0.8, 0.5), head=(0.26, 0.0), lean=0.12),
                  P('stand', aL=(1.0, 0.3, 0.5), aR=(1.0, 0.3, 0.5), head=(-0.3, 0.0)), go))
    m.face = 'wide' if go > 0.4 else 'squint'
    m.jawv = 0.5 * go
    o = S['men'][5]
    o.place(A(-1.5, 3.3, 0), look_yaw((-1.5, 3.3), (0.4, 0.8)))
    o.apply(P('stand', aR=(1.5, -0.2, 0.3), head=(-0.1, 0.0)))
    o.face = 'wide'
    grit(S, A(0.1, 0.9, 6.4), t, 8, 0.7, 5.5, 0.8)
    fl = 1.0 + 0.12 * math.sin(t * 23)
    lampat(S, 0, A(1.6, -0.8, 3.3), 520 * fl, 'FFE2B0')
    lampat(S, 1, A(2.2, 3.4, 4.4), 380, 'FFB870')
    lampat(S, 2, A(0.3, 0.3, 1.4), 60, 'FFE8C0')
    shoot(S, A(lerp(1.5, 1.25, kk), lerp(-2.2, -1.8, kk), lerp(2.3, 2.4, kk)), (px + 0.05, py + 0.3, pz + 1.3 + 0.5 * rise), 48, fill=1.3)


def drill_up(S, k, t, lt):
    """The pipe goes back up into the roof with the note on it; three men watch it go."""
    A = mine(S)
    drill_at(S, A, lerp(2.3, 5.4, k * k), spin=t * 0.6)
    M = S['men']
    for j, (rig, x, y) in enumerate(((M[3], 0.9, 1.9), (M[5], -1.5, 2.4), (M[2], 0.2, 3.3))):
        rig.place(A(x, y, 0.15 * abs(math.sin(t * 6 + j * 2))), look_yaw((x, y), (0, -1.5)))
        rig.apply(P('up', aL=(2.6 + 0.2 * math.sin(t * 9 + j), -0.45, 0.2), aR=(2.7, -0.4, 0.2), head=(-0.5, 0.0)))
        rig.face, rig.jawv = 'wide', 0.6
    grit(S, A(0, 1, 6.6), t, 10, 0.6, 6.0, 1.1)
    lampat(S, 0, A(-2.0, -1.5, 3.0), 1500, 'FFE2B0')
    lampat(S, 1, A(0.4, 0.2, 6.2), 500, 'FFF4D8')
    shoot(S, A(lerp(-2.2, -1.7, k), lerp(-4.6, -4.1, k), lerp(1.3, 1.5, k)), A(0.0, 1.4, lerp(3.2, 4.0, k)), 24, fill=1.3)


def rig_floods(S, A, e=1.0, site=False):
    lampat(S, 4, A(-5.6, -4.6, 6.4), 9000 * e, 'FFF0D0')
    lampat(S, 5, A(6.8, 2.2, 7.2), 6000 * e, 'DCE8FF')
    if site:
        lampat(S, 4, A(SITE[0] + 6.0, -4.4, 7.2), 12000 * e, 'FFF0D0')
        lampat(S, 5, A(SITE[0] - 5.0, 4.0, 6.0), 5000 * e, 'DCE8FF')


def rig_night(S, k, t, lt):
    """The surface: a derrick in the desert at night, the pipe coming up out of the ground."""
    A = night(S)
    drill_at(S, A, lerp(-7.0, -3.5, k), HOLE[0], HOLE[1], spin=t * 0.5)
    C = S['crew']
    C[0].place(A(-1.9, -3.4, 0), look_yaw((-1.9, -3.4), HOLE))
    C[0].apply(P('stand', aR=(1.2, 0.1, 0.5), head=(-0.3, 0.0)))
    C[1].place(A(2.0, -2.2, 0), look_yaw((2.0, -2.2), HOLE))
    C[1].apply(P('hips', head=(-0.35, 0.0)))
    rig_floods(S, A)
    shoot(S, A(lerp(-6.4, -5.6, k), lerp(-10.6, -9.8, k), lerp(1.3, 1.7, k)), A(0.2, -2.2, 4.6), 22, fill=0.9, fcol='C8D8FF')


def bit_out(S, k, t, lt):
    """The bit clears the hole, the note on the pipe above it. A rescuer reaches for it; Rook watches from the deck."""
    A = night(S)
    z = lerp(-1.6, 1.45, sm(k / 0.75))
    drill_at(S, A, z, HOLE[0], HOLE[1])
    c = S['crew'][0]
    cp = (-1.25, -3.1)
    c.place(A(cp[0], cp[1], 0), look_yaw(cp, HOLE))
    c.apply(blend(P('stand', head=(0.3, 0.0), aR=(0.4, 0.1, 0.6)), P('stand', aR=(1.55, -0.15, 0.25), aL=(0.9, 0.1, 0.9), head=(-0.05, 0.0), lean=0.2), (k - 0.35) / 0.4))
    c.face = 'wide' if k > 0.5 else 'calm'
    c.jawv = 0.5 * sm((k - 0.5) / 0.2)
    rk = S['rook']
    rp = (1.5, -1.2)
    rk.place(A(rp[0], rp[1], 0.4), look_yaw(rp, (HOLE[0], HOLE[1] - 1.0)))
    rk.apply(blend(P('cross', head=(0.1, 0.0)), P('cross', head=(0.3, 0.25), lean=0.22), (k - 0.4) / 0.3))
    S['rface'] = 'deadpan'
    puffs(S, A(HOLE[0], HOLE[1], 0.2), t, 6, 0.9, 0.9, 0.5)
    rig_floods(S, A, 0.7)
    lampat(S, 0, A(0.4, -5.0, 2.6), 380, 'FFE2B0')
    shoot(S, A(lerp(0.9, 0.6, k), lerp(-7.6, -7.0, k), lerp(1.4, 1.9, k)), A(0.15, -2.3, lerp(1.6, 2.2, k)), 32, fill=1.0)


def rook_rig(S, k, t, lt):
    """Rook on the deck beside the dripping bit, arms folded: he does not buy it."""
    A = night(S)
    drill_at(S, A, 1.45 + 0.02 * math.sin(t * 5), HOLE[0], HOLE[1], spin=0.25 * math.sin(t * 1.5))
    rk = S['rook']
    rp = (1.75, -3.9)
    rk.place(A(rp[0], rp[1], 0.0), look_yaw(rp, (-0.2, -8.5)))
    rk.apply(blend(P('cross', head=(0.3, 0.25), lean=0.22), P('point', aR=(1.25, 0.55, 0.3), head=(0.0, -0.1)), (lt - 0.1) / 0.3))
    S['rface'] = 'deadpan'
    c = S['crew'][0]
    c.place(A(-1.3, -3.0, 0), look_yaw((-1.3, -3.0), HOLE))
    c.apply(P('stand', aR=(1.5, -0.15, 0.3), aL=(1.3, 0.0, 0.5), head=(0.0, 0.0), lean=0.15))
    c.face = 'wide'
    rig_floods(S, A, 0.6)
    lampat(S, 0, A(0.4, -6.6, 3.2), 620, 'FFE2B0')
    shoot(S, A(lerp(-0.5, -0.2, k), lerp(-9.0, -8.5, k), lerp(2.3, 2.5, k)), A(0.9, -3.2, 2.45), 40, fill=1.2)


def rook_peer(S, k, t, lt):
    """Close: he leans in to the note and taps his beak."""
    A = night(S)
    drill_at(S, A, 1.45, HOLE[0], HOLE[1])
    rk = S['rook']
    rp = (1.15, -3.2)
    rk.place(A(rp[0], rp[1], 0.0), look_yaw(rp, (-0.3, -5.6)))
    tap = 0.5 + 0.5 * math.sin(lt * 16)
    rk.apply(blend(P('cross', head=(0.2, 0.5), lean=0.3), P('tap', aR=(1.25 + 0.12 * tap, -0.25, 2.2, 0.6), head=(0.22, 0.55), lean=0.32), lt / 0.2))
    S['rface'] = 'deadpan'
    S['hat_tip'] = 0.15
    rig_floods(S, A, 0.4)
    lampat(S, 0, A(-0.3, -5.4, 3.2), 300, 'FFE2B0')
    hd = world_of(rk.head, (0, -0.2, 0.05))
    shoot(S, A(lerp(-0.85, -0.7, k), lerp(-6.3, -6.0, k), 2.05), ((hd[0] + A(0.1, 0, 0)[0]) / 2 + 0.1, hd[1], hd[2] - 0.1), 50, fill=1.3)


# ---------------------------------------------------------------- what it says
def unfold(S, k, t, lt):
    """A rescuer holds the unfolded note up to the light; Rook reads over his shoulder."""
    A = night(S)
    c = S['crew'][1]
    cp = (-0.2, -5.2)
    c.place(A(cp[0], cp[1], 0), 0.0)
    op = sm(lt / 0.35)
    c.apply(P('stand', aL=(0.75, lerp(-0.2, 0.1, op), 1.2, 0.2), aR=(0.75, lerp(-0.2, 0.1, op), 1.2, -0.2), head=(0.45, 0.0)))
    c.face = 'wide'
    c.jawv = 0.6 * sm((lt - 0.4) / 0.2)
    S['sheet'].location = A(cp[0], cp[1] - 0.74, 1.72 + 0.01 * math.sin(t * 9))
    S['sheet'].rotation_euler = (-0.45, 0, 0.03 * math.sin(t * 5))
    S['sheet'].scale = (lerp(0.25, 0.68, op), 0.68, 0.68)
    rk = S['rook']
    rp = (1.25, -4.55)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (0.0, -6.4)))
    rk.apply(P('think', head=(0.3, 0.3), lean=0.2))
    S['rface'] = 'shocked' if lt > 0.75 else 'calm'
    S['hat_jump'] = 0.25 * sm((lt - 0.75) / 0.1)
    drill_at(S, A, 1.45, HOLE[0], HOLE[1])
    rig_floods(S, A, 0.5)
    lampat(S, 0, A(-0.6, -8.0, 3.2), 700, 'FFF0D8')
    shoot(S, A(lerp(-0.5, -0.3, k), lerp(-9.1, -8.5, k), lerp(2.2, 2.3, k)), A(0.3, -5.2, 2.3), 42, fill=1.2)


def cheer(S, k, t, lt):
    """The men at the rig throw their arms up. Rook's hat leaves his head."""
    A = night(S)
    drill_at(S, A, 1.45, HOLE[0], HOLE[1])
    for j, (rig, x, y) in enumerate(((S['crew'][0], -1.7, -5.2), (S['crew'][1], -0.2, -4.3), (S['crew'][2], 1.0, -5.4))):
        hop = abs(math.sin(t * 7 + j * 1.3))
        rig.place(A(x, y, 0.35 * hop), 0.25 * (1 - j))
        rig.apply(P('up', aL=(2.6 + 0.2 * math.sin(t * 11 + j), -0.45, 0.2), aR=(2.7, -0.4, 0.2), head=(-0.2, 0.0)))
        rig.face, rig.jawv = 'warm', 0.8
    rk = S['rook']
    rp = (2.3, -7.2)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (1.0, -12)))
    rk.apply(blend(P('cross', head=(0.0, -0.4)), P('scream', head=(-0.15, -0.2)), lt / 0.2))
    S['rface'] = 'shocked'
    S['hat_jump'] = 0.5 * max(0.0, math.sin(min(1.0, lt / 0.5) * PI))
    feather(S, world_of(rk.head, (0.3, 0, 0.3)), lt, 0.1)
    rig_floods(S, A, 0.8)
    lampat(S, 0, A(1.0, -10.0, 3.0), 1500, 'FFF0D8')
    shoot(S, A(lerp(1.0, 0.7, k), lerp(-12.6, -12.0, k), lerp(1.2, 1.4, k)), A(0.4, -5.6, 2.6), 24, fill=1.2)


# ---------------------------------------------------------------- seven hundred metres down
def shelter_light(S, A, e=1.0):
    lampat(S, 0, A(8.6, 0.6, 5.6), 2600 * e, 'FFD8A0')
    lampat(S, 1, A(12.4, -1.0, 3.0), 700 * e, 'FFE8C8')
    lampat(S, 2, A(4.6, -1.5, 3.4), 500 * e, 'B8D0FF')


def refuge_wide(S, k, t, lt):
    """The shelter: men on a bench and on the floor under one lamp, the gallery black behind."""
    A = mine(S)
    crowd(S, A, t)
    shelter_light(S, A)
    shoot(S, A(lerp(6.6, 7.6, k), lerp(-9.6, -8.8, k), lerp(4.2, 3.6, k)), A(8.9, 3.2, 1.7), 30, fill=1.3)


def faces(S, k, t, lt):
    """Along the bench: tired faces under helmet lamps. Rook sits at the end and looks along the row."""
    A = mine(S)
    crowd(S, A, t, nod=0.36, row_only=True)
    rk = S['rook']
    sit(rk, A, 4.5, 3.3, -0.25, 0.2, lerp(0.1, 0.8, sm((k - 0.2) / 0.4)), hug=True)
    S['rface'] = 'sad'
    shelter_light(S, A, 0.8)
    lampat(S, 3, A(4.6, 0.6, 2.4), 260, 'FFE8C8')
    shoot(S, A(lerp(2.9, 3.5, k), lerp(0.5, 0.9, k), 1.7), A(7.4, 3.9, 1.75), 30, fill=1.3)


def tents(S, k, t, lt):
    """The camp above: families by their lamps, looking towards the rig. Rook flips a coin and waits."""
    A = night(S)
    cx, cy = CAMP
    for j, (rig, x, y) in enumerate(((S['civ'][0], -1.3, -2.6), (S['civ'][1], -0.1, -2.2), (S['civ'][2], 1.1, -2.8))):
        rig.place(A(cx + x, cy + y, 0), look_yaw((x, y), (0.5, -12)) + 0.15 * (j - 1))
        rig.apply(P('stand', aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.22 + 0.05 * math.sin(t + j), 0.2 * (1 - j))))
        rig.face = 'sad'
    rk = S['rook']
    rp = (cx + 1.7, cy - 4.2)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (cx + 0.6, cy - 12)))
    u = (lt * 1.5) % 1
    rk.apply(P('stand', aR=(0.9 + 0.3 * max(0, math.sin(u * PI)), 0.1, 1.2, 0.2), head=(lerp(-0.1, 0.25, u), 0.35)))
    hand = world_of(rk.hands[1], (0, -0.1, -0.05))
    S['coin'].location = (hand[0], hand[1], hand[2] + 0.15 + 1.5 * math.sin(u * PI))
    S['coin'].rotation_euler = (u * 4 * PI, 0.3, 0)
    S['rface'] = 'calm'
    lampat(S, 0, A(cx - 1.4, cy - 5.6, 1.8), 2600, 'FFC880')
    lampat(S, 1, A(cx + 2.4, cy - 7.4, 2.8), 1500, 'FFE2C0')
    lampat(S, 4, A(-5.6, -4.6, 6.4), 9000, 'FFF0D0')
    shoot(S, A(cx + lerp(-0.1, 0.4, k), cy + lerp(-11.0, -10.4, k), lerp(1.7, 1.9, k)), A(cx + 0.3, cy - 2.6, 2.2), 34, fill=1.3, fcol='FFD8B0')


# ---------------------------------------------------------------- two spoonfuls
def stock(S, A, n=4):
    c = (13.6, 1.2)
    for j in range(n):
        S['tins'][j].location = A(c[0] - 0.55 + 0.42 * j, c[1] + 0.05, 1.51 if j < 3 else 0.61)
    S['carton'].location = A(c[0] + 0.55, c[1] + 0.1, 0.74)


def cabinet(S, k, t, lt):
    """The food locker: three tins and a carton on bare shelves. A hand takes one tin."""
    A = mine(S)
    stock(S, A)
    m = S['men'][0]
    mp = (12.25, 0.75)
    m.place(A(mp[0], mp[1], 0), look_yaw(mp, (13.6, 0.45)))
    r = sm((lt - 0.1) / 0.4)
    back = sm((lt - 0.65) / 0.35)
    m.apply(blend(blend(P('stand', head=(0.1, 0.0)), P('stand', aR=(1.5, -0.1, 0.1), head=(0.1, 0.0), lean=0.12), r), P('stand', aR=(1.0, 0.0, 1.3), head=(0.4, 0.0)), back))
    m.face = 'tired'
    if lt > 0.55:
        S['tins'][0].location = world_of(m.hands[1], (0, -0.14, -0.08))
    lampat(S, 0, A(12.0, -1.6, 3.6), 900, 'FFE2B0')
    lampat(S, 1, A(13.6, 0.2, 2.6), 160, 'FFF4E0')
    shoot(S, A(lerp(12.5, 12.8, k), lerp(-3.6, -3.1, k), lerp(2.2, 2.0, k)), A(13.1, 1.1, 1.75), 34, fill=1.2)


def spoon(S, k, t, lt):
    """Close: one spoonful of tuna leaves the tin."""
    A = mine(S)
    tb = (10.6, 0.6, 1.05)
    S['tins'][0].location = A(tb[0] - 0.25, tb[1] - 0.1, tb[2] + 0.08)
    S['tins'][0].scale = (1.2, 1.2, 1.5)
    S['tuna'].location = A(tb[0] - 0.25, tb[1] - 0.1, tb[2] + 0.205)
    S['tuna'].scale = (1.2, 1.2, 1.0)
    for j in range(3):
        S['cups'][j].location = A(tb[0] + 0.3 + 0.3 * j, tb[1] + 0.05 + 0.12 * (j % 2), tb[2] + 0.09)
    dip = sm(lt / 0.3) * (1 - sm((lt - 0.35) / 0.25))
    over = sm((lt - 0.5) / 0.35)
    tipk = sm((lt - 0.9) / 0.25)
    sx = lerp(tb[0] - 0.12, tb[0] + 0.42, over)
    sz = tb[2] + 0.62 - 0.3 * dip - 0.12 * tipk
    S['spoon'].location = A(sx, tb[1] - 0.1, sz)
    S['spoon'].rotation_euler = (tipk * 1.5, -0.25 + 0.2 * dip, 0)
    S['bite'].hide_render = lt < 0.3 or tipk > 0.6
    S['hand'].place(A(sx + 0.78, tb[1] - 0.1, sz + 0.16), (0, -0.25, -PI / 2))
    S['hand'].grip(0.85)
    lampat(S, 0, A(9.6, -1.2, 3.0), 420, 'FFE2B0')
    lampat(S, 1, A(11.6, 1.6, 2.4), 120, 'B8D0FF')
    shoot(S, A(lerp(10.3, 10.5, k), lerp(-2.0, -1.8, k), lerp(1.95, 1.85, k)), A(tb[0] + 0.4, tb[1], tb[2] + 0.3), 34, fill=1.2)


def line_up(S, k, t, lt):
    """A queue with small cups. Rook is last in it, looks into his cup and then at us."""
    A = mine(S)
    M = S['men']
    srv = M[0]
    srv.place(A(11.4, 1.9, 0), look_yaw((11.4, 1.9), (9.0, 1.2)))
    srv.apply(P('stand', aR=(1.0 + 0.2 * math.sin(lt * 6), -0.1, 0.9), head=(0.3, 0.0)))
    srv.face = 'tired'
    step = 0.25 * sm((lt - 0.2) / 0.5)
    for j in range(4):
        rig = M[1 + j]
        x = 9.9 - 1.25 * j + step
        rig.place(A(x, 1.2 - 0.12 * (j % 2), 0), look_yaw((0, 0), (1, -0.25)))
        rig.apply(P('stand', aR=(0.95, 0.0, 1.25, 0.2), head=(0.3 if j else 0.15, 0.0), lean=0.08))
        rig.face = 'tired'
        S['cups'][j].location = world_of(rig.hands[1], (0, -0.14, -0.02))
    rk = S['rook']
    rx = 9.9 - 1.25 * 4 + step
    look = sm((lt - 0.7) / 0.3)
    rk.place(A(rx, 1.15, 0), lerp(look_yaw((0, 0), (1, -0.25)), look_yaw((rx, 1.15), (6.4, -6.0)), look))
    rk.apply(P('stand', aR=(0.95, 0.0, 1.25, 0.2), head=(lerp(0.5, 0.05, look), 0.0)))
    S['cups'][4].location = world_of(rk.hands[1], (0, -0.14, -0.02))
    S['rface'] = 'deadpan' if look > 0.5 else 'calm'
    S['hat_tip'] = 0.4 * look
    shelter_light(S, A, 0.9)
    lampat(S, 3, A(6.0, -3.0, 3.0), 500, 'FFE8C8')
    shoot(S, A(lerp(6.2, 5.8, k), lerp(-6.6, -6.0, k), lerp(2.2, 2.4, k)), A(7.0, 1.2, 2.2), 30, fill=1.3)


# ---------------------------------------------------------------- a note is not a way out
def hole_measure(S, k, t, lt):
    """Daylight at the borehole. Rook kneels and lays his rule across it: a hand's width."""
    A = day(S, False)
    drill_at(S, A, -80, HOLE[0], HOLE[1])
    rk = S['rook']
    rp = (0.3, -1.75)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (-0.2, -6.0)))
    lay = sm((lt - 0.15) / 0.35)
    up = sm((lt - 1.0) / 0.3)
    rk.apply(blend(blend(KNEEL, P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.42, aR=(1.25, 0.1, 0.2), aL=(0.7, 0.1, 0.7), head=(0.4, 0.0)), lay),
                   P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.2, aL=(0.3, 0.75, 1.5, -0.9), aR=(0.3, 0.75, 1.5, -0.9), head=(-0.05, 0.1)), up))
    S['rface'] = 'deadpan' if up > 0.5 else 'calm'
    S['ruler'].location = A(HOLE[0] + lerp(0.7, 0.05, lay), HOLE[1] + lerp(0.5, 0.0, lay), lerp(0.9, 0.27, lay))
    S['ruler'].rotation_euler = (0, 0, lerp(0.9, 0.15, lay))
    rope(S, 0, A(HOLE[0], HOLE[1], 0.2), A(HOLE[0] - 0.2, HOLE[1] + 1.0, 4.0), 0.025)
    shoot(S, A(lerp(-0.9, -0.6, k), lerp(-6.9, -6.3, k), lerp(1.0, 1.2, k)), A(0.15, -2.3, 1.2), 36, fill=0.9)


def big_drill(S, k, t, lt):
    """A far bigger rig turns at the second site, dust boiling off the collar. Rook stands with his arms folded."""
    A = day(S)
    sx, sy = SITE
    S['bigbit'].location = A(sx, sy, -3.0 - 0.5 * k)
    S['bigbit'].rotation_euler = (0, 0, t * 5)
    S['surf']['wheel'].rotation_euler = (t * 2, PI / 2, 0)
    puffs(S, A(sx, sy, 0.2), t, 12, 2.6, 2.0, 1.3)
    c = S['crew'][2]
    c.place(A(sx - 3.4, sy - 2.2, 0), look_yaw((sx - 3.4, sy - 2.2), SITE))
    c.apply(P('hips', head=(-0.2, 0.0)))
    rk = S['rook']
    rp = (sx - 2.8, sy - 8.4)
    turn = sm((lt - 0.6) / 0.3)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (sx - 7.5, sy - 14)))
    rk.apply(P('cross', head=(-0.1 * (1 - turn), lerp(-1.0, 0.25, turn))))
    S['rface'] = 'deadpan'
    shoot(S, A(sx + lerp(-5.4, -4.8, k), sy + lerp(-12.6, -11.9, k), lerp(1.5, 1.8, k)), A(sx - 0.8, sy - 1.0, 4.4), 22, fill=0.7)


def break_through(S, k, t, lt):
    """The wide drill head comes through the gallery roof in a fall of rock. The men shield their faces, then cheer."""
    A = mine(S)
    seen(S['mine']['drop'], True)
    seen(S['mine']['pile'], lt > 0.3)
    dx, dy = DROP
    S['bigbit'].location = A(dx, dy, lerp(7.4, 5.3, sm(k / 0.6)))
    S['bigbit'].rotation_euler = (0, 0, t * 6)
    grit(S, A(dx, dy, 6.6), t, 10, 1.3, 6.5, 1.4)
    puffs(S, A(dx, dy, 0.2), t, 8, 2.6, 1.6, 1.0)
    M = S['men']
    ch = sm((lt - 0.55) / 0.25)
    for j, (rig, x, y) in enumerate(((M[1], -3.4, 1.2), (M[4], -2.6, -1.4), (M[6], -4.4, 3.0), (M[0], -1.6, 0.4))):
        rig.place(A(x, y, 0.2 * ch * abs(math.sin(t * 7 + j))), look_yaw((x, y), DROP))
        rig.apply(blend(P('stand', aL=(1.9, -0.3, 1.3), aR=(1.9, -0.3, 1.3), head=(0.3, 0.0), lean=-0.1), P('up', head=(-0.4, 0.0)), ch))
        rig.face, rig.jawv = ('warm', 0.7) if ch > 0.5 else ('squint', 0.0)
    lampat(S, 0, A(-3.0, -3.0, 3.4), 2200, 'FFE2B0')
    lampat(S, 1, A(dx, dy - 0.5, 4.0), 600, 'FFF4E0')
    shoot(S, A(lerp(0.4, 0.9, k), lerp(-6.4, -5.8, k), lerp(1.4, 1.7, k)), A(-4.6, 0.4, lerp(3.4, 3.9, k)), 22, fill=1.3)


# ---------------------------------------------------------------- the capsule
def cable_top(S, A, x, y, z, top=11.0):
    rope(S, 0, A(x, y, z + 4.6), A(x, y, top), 0.03)


def capsule_top(S, k, t, lt):
    """Night at the winch tower: the capsule hangs over the shaft, then goes down into it."""
    A = night(S, True)
    sx, sy = SITE
    z = lerp(2.2, -3.4, sm((k - 0.15) / 0.85))
    cap_at(S, A, sx, sy, z, spin=0.1 * math.sin(t * 2))
    cable_top(S, A, sx, sy, z)
    S['surf']['wheel'].rotation_euler = (z * 1.2, PI / 2, 0)
    for j, (rig, x, y) in enumerate(((S['crew'][0], -2.4, -1.6), (S['crew'][1], 2.3, -1.2))):
        rig.place(A(sx + x, sy + y, 0), look_yaw((x, y), (0, 0)))
        rig.apply(P('stand', aR=(1.3 - 0.4 * k, 0.3, 0.4), head=(lerp(-0.3, 0.3, k), 0.0)))
    rig_floods(S, A, 1.0, True)
    lampat(S, 0, A(sx - 1.0, sy - 5.0, 3.2), 1500, 'FFF0D8')
    shoot(S, A(sx + lerp(-3.4, -2.6, k), sy + lerp(-10.5, -9.5, k), lerp(1.3, 1.6, k)), A(sx, sy, lerp(4.4, 3.2, k)), 24, fill=1.0, fcol='DCE4FF')


def rook_stuck(S, k, t, lt):
    """Rook tries the capsule for size. It is barely wider than his shoulders, and his hat does not fit at all."""
    A = day(S)
    sx, sy = SITE[0] - 6.0, SITE[1] - 5.0
    wob = 0.06 * math.sin(lt * 21) * (1 - sm((lt - 0.9) / 0.3))
    cap_at(S, A, sx, sy, 0.0, spin=0.35 + wob)
    rk = S['rook']
    rk.root.scale = (0.86,) * 3
    rk.place(A(sx, sy, 0.7), 0.35 + wob * 2, 0.0, wob)
    rk.apply(P('stand', aL=(0.1 + 0.25 * abs(math.sin(lt * 10)), 0.02, 0.5, 0.6), aR=(0.1 + 0.25 * abs(math.cos(lt * 10)), 0.02, 0.5, 0.6), head=(0.12, 0.3 * math.sin(lt * 5))))
    S['rface'] = 'shocked' if lt > 0.5 else 'deadpan'
    S['hat_sq'] = 1.0
    feather(S, A(sx + 0.3, sy - 0.8, 3.0), lt, 0.5)
    c = S['crew'][2]
    c.place(A(sx + 2.6, sy + 0.6, 0), look_yaw((sx + 2.6, sy + 0.6), (sx, sy - 2)))
    c.apply(P('hips', head=(0.0, 0.3)))
    c.face = 'warm'
    shoot(S, A(sx + lerp(-1.3, -1.0, k), sy + lerp(-6.4, -5.8, k), lerp(2.3, 2.5, k)), A(sx + 0.2, sy, 2.45), 34, fill=0.8)


def gallery_light(S, A, e=1.0):
    lampat(S, 0, A(-4.0, -3.4, 3.6), 2400 * e, 'FFE2B0')
    lampat(S, 1, A(DROP[0], DROP[1], 6.0), 900 * e, 'FFF8E8')
    lampat(S, 2, A(-10.5, -1.0, 2.6), 500 * e, 'B8D0FF')


def capsule_arrive(S, k, t, lt):
    """Below: the capsule comes down out of the roof. The men and Rook stand round the rubble and watch it land."""
    A = mine(S)
    seen(S['mine']['drop'], True)
    seen(S['mine']['pile'], True)
    dx, dy = DROP
    z = lerp(6.6, 0.25, sm(k / 0.85))
    cap_at(S, A, dx, dy, z, spin=0.2 * math.sin(t * 1.5))
    rope(S, 0, A(dx, dy, z + 4.6), A(dx, dy, ROOF + 0.4), 0.03)
    M = S['men']
    for j, (rig, x, y) in enumerate(((M[1], -2.6, 2.8), (M[4], -2.7, -1.0), (M[6], -5.2, 3.4), (M[0], -10.4, 1.6), (M[8], -9.6, 3.0))):
        rig.place(A(x, y, 0), look_yaw((x, y), DROP))
        rig.apply(P('stand', aR=(0.9, 0.3, 1.6, 0.4) if j % 2 else (0.05, 0.12, 0.15), head=(lerp(-0.6, -0.1, k), 0.0)))
        rig.face = 'wide'
    rk = S['rook']
    rp = (-4.3, 1.1)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (dx + 0.6, dy - 2.5)))
    rk.apply(P('hat', head=(lerp(-0.45, -0.1, k), 0.5)))
    S['rface'] = 'shocked'
    grit(S, A(dx, dy, 6.5), t, 6, 1.0, 6.0, 0.8)
    gallery_light(S, A)
    shoot(S, A(lerp(-2.4, -2.9, k), lerp(-8.0, -7.4, k), lerp(1.5, 1.8, k)), A(-6.2, 0.2, lerp(4.0, 2.7, k)), 22, fill=1.3)


def step_in(S, k, t, lt):
    """One man stands in the cage; a rescuer checks him, raises a thumb and the capsule starts to lift."""
    A = mine(S)
    seen(S['mine']['drop'], True)
    seen(S['mine']['pile'], True)
    dx, dy = DROP
    z = 0.25 + 1.3 * sm((lt - 0.85) / 0.6)
    m = S['men'][4]
    cap_at(S, A, dx, dy, z, m, -0.1, P('stand', aL=(0.05, 0.02, 0.2), aR=(lerp(0.1, 1.1, sm((lt - 0.3) / 0.3)), 0.02, 1.6), head=(lerp(0.1, -0.3, sm(lt / 0.8)), 0.0)))
    m.face = 'warm'
    rope(S, 0, A(dx, dy, z + 4.6), A(dx, dy, ROOF + 0.4), 0.03)
    c = S['crew'][1]
    cp = (dx + 1.55, dy - 0.9)
    c.place(A(cp[0], cp[1], 0), look_yaw(cp, DROP))
    c.apply(blend(P('stand', aR=(1.3, -0.2, 0.4), aL=(1.2, 0.2, 0.5), head=(0.0, 0.0)), P('stand', aR=(2.2, 0.3, 0.6), head=(-0.3, 0.0)), (lt - 0.45) / 0.3))
    c.face = 'warm'
    q = S['men'][1]
    q.place(A(dx - 2.3, dy + 1.4, 0), look_yaw((dx - 2.3, dy + 1.4), DROP))
    q.apply(P('stand', aR=(2.4, 0.4, 0.3 + 0.3 * math.sin(t * 8)), head=(-0.3, 0.0)))
    q.face = 'warm'
    gallery_light(S, A, 0.9)
    shoot(S, A(lerp(-5.6, -5.9, k), lerp(-6.2, -5.7, k), lerp(2.2, 2.6, k)), A(dx + 0.2, dy, 2.5 + 0.6 * (z - 0.25)), 32, fill=1.3)


def ride(S, t, m, yaw=0.0):
    """The capsule in the cut-away shaft, climbing. Returns the set's coordinates and the capsule height."""
    A = env(S, 'shaft', '000000', fk=2.2)
    z = (t * 5.0) % 30.0 + 4.0
    cap_at(S, A, 0, 0.25, z, m, yaw, P('stand', aL=(0.3, 0.02, 1.0, 0.5), aR=(0.3, 0.02, 1.0, 0.5), head=(-0.42, 0.0)), spin=0.05 * math.sin(t * 9))
    rope(S, 0, A(0, 0.25, z + 4.6), A(0, 0.25, z + 60), 0.03)
    for i in range(8):
        u = (t * 2.2 + i / 8) % 1
        a = (0.1 + 0.8 * (i % 4) / 3) * PI
        S['sparks'][i].location = A(0.95 * math.cos(a), 0.25 + 0.95 * math.sin(a), z + (0.35 if i < 4 else 3.85) - 1.4 * u)
        q = 1.0 - u
        S['sparks'][i].scale = (q, q, q)
    return A, z


def shaft_ride(S, k, t, lt):
    """Cut-away: the capsule climbs the bore, rock sliding past, sparks at the wheels."""
    m = S['men'][4]
    A, z = ride(S, t, m)
    m.face = 'squint'
    lampat(S, 0, A(-1.6, -2.4, z + 2.4), 700, 'FFE2B0')
    lampat(S, 1, A(0.2, 0.3, z + 9.0), 1500 + 1500 * k, 'FFF8E8')
    lampat(S, 2, A(1.2, -1.0, z - 3.0), 240, 'B8D0FF')
    shoot(S, A(lerp(-0.5, -0.1, k), lerp(-8.2, -7.2, k), z + lerp(-1.6, 0.2, k)), A(0.0, 0.3, z + 2.6), 30, roll=0.05, fill=1.2)


def ride_face(S, k, t, lt):
    """Close through the bars: his face turned up, the light from above growing on it."""
    m = S['men'][4]
    A, z = ride(S, t, m, 0.15)
    m.face = 'squint' if k > 0.5 else 'wide'
    m.jawv = 0.3
    lampat(S, 0, A(-0.9, -2.0, z + 2.4), 220, 'FFE2B0')
    lampat(S, 1, A(0.1, -0.5, z + 5.2), lerp(200, 2600, k * k), 'FFF8E8')
    shoot(S, A(lerp(-0.75, -0.45, k), lerp(-2.9, -2.5, k), z + lerp(2.15, 2.3, k)), A(0.0, 0.2, z + 2.5), 50, fill=1.2)


# ---------------------------------------------------------------- out
def welcome(S, A, t, k=1.0):
    sx, sy = SITE
    for j, (rig, x, y) in enumerate(((S['crew'][0], -2.6, -1.4), (S['crew'][2], 3.4, 0.6), (S['civ'][1], 4.2, -2.6), (S['civ'][2], -3.8, -2.6))):
        hop = abs(math.sin(t * 6 + j * 1.7)) * k
        rig.place(A(sx + x, sy + y, 0.3 * hop), look_yaw((x, y), (0, 0)))
        rig.apply(blend(P('stand', head=(0.2, 0.0)), P('up', aL=(2.6 + 0.2 * math.sin(t * 10 + j), -0.45, 0.2), aR=(2.7, -0.4, 0.2), head=(-0.2, 0.0)), k))
        rig.face, rig.jawv = 'warm', 0.7 * k


def emerge(S, k, t, lt):
    """The capsule rises out of the collar under the floodlights. Arms go up all round; Rook flaps."""
    A = night(S, True)
    sx, sy = SITE
    z = lerp(-4.2, 0.35, sm(k / 0.8))
    m = S['men'][4]
    cap_at(S, A, sx, sy, z, m, 0.0)
    m.face = 'squint'
    cable_top(S, A, sx, sy, z)
    S['surf']['wheel'].rotation_euler = (z * 1.2, PI / 2, 0)
    welcome(S, A, t, sm((k - 0.3) / 0.3))
    rk = S['rook']
    rp = (sx + 2.6, sy - 2.2)
    fl = math.sin(t * 16)
    rk.place(A(rp[0], rp[1], 0.3 + 0.25 * abs(fl)), look_yaw(rp, (sx - 1, sy - 10)))
    rk.apply(P('stand', aL=(0.2, 1.3 + 0.5 * fl, 0.3), aR=(0.2, 1.3 + 0.5 * fl, 0.3), head=(-0.2, -0.6), lL=(0.3, 0.5), lR=(0.1, 0.4)))
    S['rface'] = 'shocked'
    rig_floods(S, A, 1.0, True)
    lampat(S, 0, A(sx - 0.5, sy - 6.0, 3.0), 2200, 'FFF0D8')
    shoot(S, A(sx + lerp(0.6, 0.2, k), sy + lerp(-9.6, -8.8, k), lerp(1.2, 1.5, k)), A(sx + 0.3, sy - 0.4, lerp(2.4, 3.0, k)), 26, fill=1.1, fcol='DCE4FF')


def hug(S, k, t, lt):
    """He steps out and someone runs into his arms. Rook, beside them, has his hat in the air."""
    A = night(S, True)
    sx, sy = SITE
    cap_at(S, A, sx, sy, 0.35)
    cable_top(S, A, sx, sy, 0.35)
    m = S['men'][4]
    mp = (sx - 0.4, sy - 2.3)
    m.place(A(mp[0], mp[1], 0), look_yaw(mp, (sx - 2.4, sy - 3.4)))
    cl = sm((lt - 0.3) / 0.3)
    m.apply(blend(P('up', head=(-0.3, 0.0)), P('stand', aL=(1.2, -0.35, 0.9, 0.6), aR=(1.2, -0.35, 0.9, 0.6), head=(0.2, 0.3), lean=0.12), cl))
    m.face, m.jawv = 'warm', 0.5
    f = S['civ'][0]
    fx = lerp(sx - 4.4, sx - 1.25, sm(lt / 0.4))
    fp = (fx, sy - 2.75)
    f.place(A(fp[0], fp[1], 0), look_yaw(fp, mp))
    f.apply(blend(walk(t, 2.2), P('stand', aL=(1.25, -0.35, 0.8, 0.6), aR=(1.25, -0.35, 0.8, 0.6), head=(-0.1, -0.2), lean=0.15), cl))
    f.face, f.jawv = 'warm', 0.4
    for j, (rig, x, y) in enumerate(((S['crew'][0], 2.4, -1.6), (S['crew'][2], 3.6, -3.4))):
        rig.place(A(sx + x, sy + y, 0), look_yaw((x, y), (-0.6, -2.4)))
        cp = 0.5 + 0.5 * math.sin(t * 14 + j)
        rig.apply(P('stand', aL=(1.1, -0.1 - 0.25 * cp, 1.3, 0.5), aR=(1.1, -0.1 - 0.25 * cp, 1.3, 0.5), head=(0.0, 0.0)))
        rig.face = 'warm'
    rk = S['rook']
    rp = (sx + 1.25, sy - 3.3)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (sx - 0.6, sy - 10)))
    rk.apply(blend(P('stand', head=(0.0, 0.6)), P('reach', aR=(2.6, 0.3, 0.2), head=(-0.15, 0.4)), lt / 0.3))
    S['rface'] = 'warm'
    S['hat_jump'] = 0.45 * abs(math.sin(min(1.0, lt / 0.8) * PI))
    rig_floods(S, A, 1.0, True)
    lampat(S, 0, A(sx - 1.0, sy - 7.5, 3.0), 1800, 'FFF0D8')
    shoot(S, A(sx + lerp(-0.4, 0.0, k), sy + lerp(-9.6, -9.0, k), lerp(1.9, 2.1, k)), A(sx + 0.15, sy - 2.6, 2.3), 34, fill=1.2, fcol='FFE8D0')


# ---------------------------------------------------------------- the end
def rook_wrong(S, k, t, lt):
    """Dawn over the site. Rook turns to us and shrugs."""
    A = dawn(S)
    sx, sy = SITE
    cap_at(S, A, sx, sy, 0.35)
    cable_top(S, A, sx, sy, 0.35)
    rk = S['rook']
    rp = (sx - 3.2, sy - 5.4, 0.0)
    cam = (sx + lerp(-5.6, -5.2, k), sy + lerp(-10.6, -10.0, k), 2.3)
    turn = sm((lt - 0.1) / 0.3)
    rk.place(A(*rp), lerp(PI - 0.4, look_yaw(rp, cam), turn))
    rk.apply(blend(P('hips', head=(-0.2, 0.0)), P('shrug', head=(0.05, 0.0)), turn))
    S['rface'] = 'warm' if turn > 0.5 else 'calm'
    shoot(S, A(*cam), A(sx - 2.9, sy - 5.0, 2.35), 40, fill=0.9)


def last_up(S, k, t, lt):
    """The gallery, empty. The foreman, last of them, looks back at the dark shelter, then stands into the cage."""
    A = mine(S)
    seen(S['mine']['drop'], True)
    seen(S['mine']['pile'], True)
    dx, dy = DROP
    z = 0.25 + 2.0 * sm((lt - 1.0) / 0.7)
    cap_at(S, A, dx, dy, z)
    rope(S, 0, A(dx, dy, z + 4.6), A(dx, dy, ROOF + 0.4), 0.03)
    m = S['men'][0]
    inn = sm((lt - 0.55) / 0.35)
    if inn < 1:
        mp = (lerp(dx + 2.2, dx, inn), lerp(dy - 0.6, dy, inn))
        m.place(A(mp[0], mp[1], 0.7 * inn), lerp(look_yaw(mp, (12, 2)), -0.3, sm(lt / 0.45)))
        m.apply(blend(P('stand', aR=(0.6, 0.2, 0.9), head=(0.05, 0.0)), walk(t, 1.6), sm(lt / 0.45)))
    else:
        cap_at(S, A, dx, dy, z, m, -0.3)
    m.face = 'calm'
    lampat(S, 0, A(-4.6, -3.0, 3.4), 1500, 'FFE2B0')
    lampat(S, 1, A(dx, dy, 6.0), 1200, 'FFF8E8')
    lampat(S, 2, A(9.0, 1.0, 4.0), 260 * (1 - sm(lt / 0.6)), 'FFD8A0')
    shoot(S, A(lerp(-12.4, -11.6, k), lerp(-5.6, -5.0, k), lerp(2.0, 2.4, k)), A(-5.8, 0.2, 2.6 + 0.4 * (z - 0.25)), 34, fill=1.3)


def signoff(S, k, t, lt):
    """He picks a steel drill tooth out of the dust, turns it in the light, pockets it and pulls his brim down."""
    A = dawn(S)
    sx, sy = SITE
    cap_at(S, A, sx, sy, 0.35)
    rk = S['rook']
    rp = (sx - 8.5, sy - 9.0, 0.0)
    rk.place(A(*rp), 0.4)
    grab = sm((lt - 0.05) / 0.22)
    up = sm((lt - 0.3) / 0.22)
    away = sm((lt - 0.58) / 0.22)
    low = P('stand', aR=(0.9, 0.2, 0.2), head=(0.55, 0.3), lean=0.75, lL=(0.5, 0.9), lR=(0.5, 0.9), lift=-0.35)
    hold = P('stand', aR=(1.15, 0.25, 1.3, 0.3), head=(0.25, 0.35))
    rk.apply(blend(blend(blend(P('stand'), low, grab), hold, up), P('hat'), away))
    S['hat_tip'] = away
    S['rface'] = 'warm' if away < 0.5 else 'deadpan'
    ground = A(rp[0] + 0.75, rp[1] - 1.0, 0.14)
    hand = world_of(rk.hands[1], (0, -0.12, -0.08))
    u = sm((lt - 0.2) / 0.12)
    S['tooth'].location = tuple(ground[i] + (hand[i] - ground[i]) * u for i in range(3))
    S['tooth'].rotation_euler = (lerp(0.0, 2.6, up) + t * 3 * up * (1 - away), 0.3, 0.6)
    S['tooth'].scale = (1.5, 1.5, 1.5)
    if lt > 0.66:
        S['tooth'].location = AWAY
    shoot(S, A(rp[0] + lerp(1.9, 1.5, k), rp[1] + lerp(-5.6, -4.8, k), lerp(1.9, 2.3, k)), A(rp[0] + 0.2, rp[1], 2.3), 32, fill=0.9)


# ---------------------------------------------------------------- a photograph for the case board
def photo_capsule(S, k, t, lt):
    A = night(S, True)
    sx, sy = SITE
    m = S['men'][4]
    cap_at(S, A, sx, sy, 0.35, m, 0.0, P('up', head=(-0.2, 0.0)))
    m.face, m.jawv = 'warm', 0.6
    cable_top(S, A, sx, sy, 0.35)
    welcome(S, A, 0.3, 1.0)
    rig_floods(S, A, 1.0, True)
    lampat(S, 0, A(sx - 0.5, sy - 6.0, 3.0), 2400, 'FFF0D8')
    shoot(S, A(sx + 0.6, sy - 9.0, 2.0), A(sx, sy - 0.3, 2.9), 30, fill=1.2)


SHOTS3D = {f.__name__: f for f in (
    tie_note, drill_up, rig_night, bit_out, rook_rig, rook_peer, unfold, cheer, refuge_wide, faces, tents, cabinet, spoon, line_up, hole_measure, big_drill,
    break_through, capsule_top, rook_stuck, capsule_arrive, step_in, shaft_ride, ride_face, emerge, hug, rook_wrong, last_up, signoff)}
STILLS = dict(capsule=photo_capsule)
