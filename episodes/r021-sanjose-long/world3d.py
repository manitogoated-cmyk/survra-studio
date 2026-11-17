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
        add('cube', RED, (0.207, -0.087, z - 0.02), rot=(0, 0, -0.5), scale=(0.24, 0.012, 0.035), size=1, parent=note, emit=0.6)
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
    hl, hr = world_of(m.hands[0]), world_of(m.hands[1])
    px, py, pz = (hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2, (hl[2] + hr[2]) / 2 - 1.25
    S['drill'].location = (px, py, pz + rise + 0.012 * math.sin(t * 40))
    S['drill'].rotation_euler = (0, 0, -1.6)
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


# ================================================================ long-form extension (16:9 full case file)
# Same mine, same desert, more of the 69 days. New sets, each at its own origin: the mine's access road sealed by one
# huge block of rock, and a ventilation raise whose ladder stops part-way up. New on the Short's sets: the vote, the
# truck batteries, the water drum, the drills heard going past, the hammering on the bit, the supply tubes, the
# letters, the three rigs, the capsule on trestles, the rescuer who rode down first, the dark glasses, the bag of
# rocks, the empty gallery and the capped shaft. Still generic: no name, flag, logo or lettering anywhere, none of
# the sets or machines is a model of the real ones, and nobody's likeness is attempted.
SETS.update(ramp=(15000, 0, 0), chim=(20000, 0, 0))
RIGA, RIGC = (-7.0, 9.0), (33.0, 11.0)
CAMFILL.update(shift=220, cave_in=200, dust_blind=260, block_wall=240, chimney=260, ladder_end=260, vote=380, battery=200, heat=260, listen=300, bang_bit=300,
               vigil=160, three_rigs=30, dove=40, dove_arrive=300, letter=260, muck=300, workshop=40, first_down=180, greet=300, shades=160,
               gift=200, lights_out=120, sealed=50)


def box(col, loc, scale, parent=None, rot=(0, 0, 0), **kw):
    return add('cube', col, loc, rot=rot, scale=scale, size=1, parent=parent, **kw)


def set_ramp(r):
    """The access road, a tunnel in ore rock. Its far (+x) end is shut by one grey block as big as the tunnel."""
    add('plane', ORED, (0, 0, 0), size=70, parent=r)
    box(ORED, (0, 0, 6.9), (70, 13, 1.2), r)
    for sy in (-1, 1):
        box(ORE, (0, sy * 6.0, 3.4), (70, 1.2, 8), r)
        chunks(r, 26, 41 + sy, lambda j, sy=sy: (-22 + j * 1.5, sy * (5.2 + 0.3 * rn(j, 43)), 0.5 + 5.6 * rn(j, 44 + sy)), (ORE, OREL, ORED, OREG), 0.8, 1.7)
    chunks(r, 18, 47, lambda j: (-20 + j * 2.0 + rn(j, 48), -4.5 + 9 * rn(j, 49), 6.45), (ORE, ORED, OREL), 0.6, 1.4, 0.45)
    chunks(r, 20, 51, lambda j: (-18 + 34 * rn(j, 52), -4.6 + 9.2 * rn(j, 53), 0.03), (ORED, '2A201C', ORE), 0.1, 0.3, 0.5)
    box('8E877C', (15.6, 0, 3.3), (7.5, 13, 8.0), r, rot=(0.04, 0.1, 0.14))
    box('7A746A', (13.0, -2.6, 1.6), (3.0, 4.0, 3.6), r, rot=(0.3, 0.2, 0.5))
    chunks(r, 14, 55, lambda j: (10.4 + 1.6 * rn(j, 56), -4.6 + 9.2 * j / 13, 0.35), ('8E877C', '6E685E', ORE), 0.5, 1.1, 0.7)
    tube(r, '3A6A8A', (-30, 5.2, 4.6), (11.6, 5.2, 4.6), 0.12)
    for x in (-12, -4, 4):
        box(YEL, (x, -5.0, 0.6), (0.12, 0.12, 1.2), r)
        box('FFE8B0', (x, -5.0, 1.25), (0.16, 0.16, 0.12), r, emit=2.0)
    return {}


def set_chim(r):
    """A ventilation raise, cut away on the near side. The ladder on its back wall stops at a ledge; above it there are only brackets."""
    add('plane', ORED, (0, 0, 0), size=14, parent=r)
    for lv in range(18):
        z = -1.5 + lv * 3.0
        for i in range(8):
            a = (i + 0.5) / 8 * PI
            col = (ORE, OREL, ORED, OREG, '5A4438')[int(rn(lv + 40, i) * 5)]
            add('cube', col, (3.0 * math.cos(a), 3.0 * math.sin(a), z), rot=(0, 0, a + PI / 2), scale=(1.3, 0.6 + 0.3 * rn(lv, i + 50), 3.02), size=1, parent=r)
    chunks(r, 10, 61, lambda j: (-2.2 + 4.4 * rn(j, 62), 0.3 + 1.8 * rn(j, 63), 0.2), (ORED, ORE, OREL), 0.3, 0.7, 0.6)
    for sx in (-0.38, 0.38):
        tube(r, YEL, (sx, 2.3, 0), (sx, 2.3, 15.3), 0.05)
    for j in range(30):
        tube(r, STEEL, (-0.38, 2.3, 0.5 + 0.5 * j), (0.38, 2.3, 0.5 + 0.5 * j), 0.035)
    tube(r, YEL, (0.38, 2.3, 15.3), (0.95, 1.7, 16.2), 0.05)
    tube(r, YEL, (-0.38, 2.3, 15.3), (-0.5, 2.0, 15.9), 0.05)
    for j in range(7):
        box('2A201C', (0, 2.45, 17.5 + 3 * j), (1.0, 0.1, 0.14), r)
    box(ORE, (-1.9, 1.5, 13.0), (1.7, 1.9, 0.35), r)
    chunks(r, 4, 65, lambda j: (-2.5 + 0.4 * j, 1.9 + 0.2 * rn(j, 66), 12.75), (ORED, OREL), 0.4, 0.7, 0.6)
    add('cylinder', 'BFD4FF', (0, 1.0, 50.5), radius=2.6, depth=0.1, vertices=12, parent=r, emit=2.5)
    return {}


def make_rig(pos, h, w, col, cabin):
    """Another drilling rig: a lattice mast over a turning pipe, a cabin beside it."""
    r = empty((pos[0], pos[1], 0))
    box(STEELD, (0, 0, 0.2), (2 * w + 1.6, 2 * w + 1.6, 0.4), r)
    cs = [(sx * w, sy * w) for sx in (-1, 1) for sy in (-1, 1)]
    for (x, y) in cs:
        tube(r, col, (x, y, 0), (x * 0.3, y * 0.3, h), 0.09)
    for lv in range(int(h // 3)):
        z0, z1 = 1.5 + lv * 3.0, 4.5 + lv * 3.0
        f0, f1 = 1 - 0.7 * z0 / h, 1 - 0.7 * min(z1, h) / h
        for i in range(4):
            a, b = cs[(0, 1, 3, 2)[i]], cs[(1, 3, 2, 0)[i]]
            tube(r, col, (a[0] * f0, a[1] * f0, z0), (b[0] * f0, b[1] * f0, z0), 0.04)
            tube(r, col, (a[0] * f0, a[1] * f0, z0), (b[0] * f1, b[1] * f1, min(z1, h)), 0.04)
    box(YEL, (0, 0, h + 0.4), (w * 0.9, w * 0.9, 0.8), r)
    box('FFE8B0', (0, 0, h - 0.2), (0.5, 0.5, 0.12), r, emit=5.0)
    pipe = add('cylinder', STEEL, (0, 0, h / 2), radius=0.22, depth=h, vertices=8, parent=r, rough=0.35)
    for j in range(4):
        box(YEL, (0.2, 0, 2.0 + j * h / 5), (0.2, 0.34, 0.5), pipe)
    box(cabin, (w + 2.4, 0.6, 1.3), (3.4, 2.6, 2.6), r)
    box('2A2E38', (w + 2.0, -0.72, 1.5), (1.6, 0.05, 0.9), r)
    add('cylinder', '3A3F4C', (-w - 1.6, 0.4, 1.0), radius=0.7, depth=2.0, vertices=8, parent=r)
    return r, pipe


def make_truck():
    """A mine pickup, facing local -Y. The bonnet opens on the battery."""
    tr = keep(empty(AWAY))
    box('D8D4C8', (0, 0.2, 1.35), (2.0, 1.7, 1.1), tr, rough=0.5)
    box('1C222C', (0, -0.66, 1.52), (1.8, 0.05, 0.6), tr, rough=0.3)
    box('D8D4C8', (0, -1.4, 0.95), (2.0, 1.5, 0.55), tr, rough=0.5)
    box('B8B4A8', (0, 2.1, 0.95), (2.0, 2.2, 0.5), tr)
    box('2A2E38', (0, 0.3, 0.55), (1.9, 4.9, 0.3), tr)
    for sx in (-1, 1):
        for y in (-1.5, 1.9):
            add('cylinder', '16181E', (sx * 1.02, y, 0.45), rot=(0, PI / 2, 0), radius=0.45, depth=0.34, vertices=10, parent=tr)
        box('FFF4D0', (sx * 0.68, -2.16, 0.98), (0.36, 0.04, 0.22), tr, emit=9.0)
    box('E07A1E', (0, 0.2, 1.97), (0.5, 0.3, 0.14), tr, emit=3.0)
    box('2A2E38', (0.52, -1.3, 1.34), (0.5, 0.36, 0.26), tr)
    for sx in (-0.14, 0.14):
        box('C8CCD4', (0.52 + sx, -1.3, 1.5), (0.08, 0.08, 0.08), tr, rough=0.2)
    hood = empty((0, -0.68, 1.26), tr)
    box('D8D4C8', (0, -0.74, 0.02), (1.96, 1.48, 0.06), hood, rough=0.5)
    return tr, hood


_build0, _reset0 = build, reset


def build():
    S = _build0()
    for name, fn in (('ramp', set_ramp), ('chim', set_chim)):
        S['colls'][name], S[name] = stage(name, fn)
    S['rigA'], S['pipeA'] = make_rig(RIGA, 17.0, 1.5, 'C8CCD4', 'D8DCE4')
    S['rigC'], S['pipeC'] = make_rig(RIGC, 24.0, 2.3, 'B8322E', '6E84A0')
    S['truck'], S['hood'] = make_truck()
    S['clouds'] = [keep(add('ico_sphere', ('C2A888', 'B09878', 'D0B898')[j % 3], AWAY, radius=1, subdivisions=1, rough=1.0)) for j in range(12)]
    S['bouls'] = [keep(add('ico_sphere', (ORE, OREL, ORED)[j % 3], AWAY, radius=0.5, subdivisions=1)) for j in range(8)]
    S['hammer'] = hm = keep(empty(AWAY))
    tube(hm, '7A5A3A', (0, 0, 0), (0, 0, 0.7), 0.04)
    box(STEELD, (0, 0, 0.72), (0.34, 0.14, 0.14), hm)
    S['candles'] = []
    for j in range(4):
        c = keep(add('cylinder', 'F4EEDC', AWAY, radius=0.05, depth=0.22, vertices=6))
        add('ico_sphere', 'FFC860', (0, 0, 0.17), scale=(0.8, 0.8, 1.5), radius=0.06, subdivisions=1, parent=c, emit=16.0)
        S['candles'].append(c)
    S['dove'] = dv = keep(empty(AWAY))
    add('cylinder', 'E8E8E4', (0, 0, 1.2), radius=0.1, depth=2.4, vertices=8, parent=dv, rough=0.4)
    for z in (0.07, 2.33):
        add('cylinder', '2A4EA0', (0, 0, z), radius=0.115, depth=0.16, vertices=8, parent=dv, rough=0.4)
    add('torus', STEELD, (0, 0, 2.48), rot=(PI / 2, 0, 0), major_radius=0.07, minor_radius=0.02, major_segments=8, minor_segments=4, parent=dv)
    S['bottle'] = keep(add('cylinder', '9AD0F0', AWAY, radius=0.07, depth=0.3, vertices=7, rough=0.2, emit=0.3))
    S['shovels'] = []
    for j in range(4):
        s = keep(empty(AWAY))
        tube(s, '7A5A3A', (0, 0, -0.3), (0, 0, 1.0), 0.035)
        box(STEEL, (0, 0, -0.5), (0.3, 0.04, 0.42), s, rough=0.4)
        S['shovels'].append(s)
    S['barrow'] = bw = keep(empty(AWAY))
    box('C8372D', (0, 0, 0.72), (0.9, 1.4, 0.4), bw)
    add('cylinder', '16181E', (0, -0.95, 0.3), rot=(0, PI / 2, 0), radius=0.3, depth=0.14, vertices=9, parent=bw)
    for sx in (-0.4, 0.4):
        tube(bw, STEELD, (sx, 0.5, 0.6), (sx, 1.5, 0.85), 0.03)
        tube(bw, STEELD, (sx, 0.5, 0.55), (sx, 0.5, 0.0), 0.03)
    for j in range(4):
        add('ico_sphere', (ORE, OREL)[j % 2], (0.25 * (j % 2) - 0.12, -0.4 + 0.3 * j, 1.0), radius=0.22, subdivisions=1, parent=bw)
    S['trestles'] = []
    for j in range(2):
        tr = keep(empty(AWAY))
        box('7A5A3A', (0, 0, 0.98), (0.2, 1.9, 0.14), tr)
        for sy in (-0.8, 0.8):
            box('5A4230', (0, sy, 0.48), (0.14, 0.14, 0.96), tr, rot=(0.25 * (1 if sy > 0 else -1), 0, 0))
        S['trestles'].append(tr)
    S['glasses'] = {i: box('0A0A0E', (0, -0.3, 0.042), (0.34, 0.04, 0.09), S['men'][i].head, rough=0.2) for i in (4, 6)}
    S['sack'] = keep(add('ico_sphere', 'C8B070', AWAY, scale=(0.3, 0.25, 0.38), radius=1, subdivisions=1, rough=1.0))
    S['rocks'] = [keep(add('ico_sphere', 'D8B040', AWAY, radius=0.11, subdivisions=1, rough=0.2, emit=0.6)) for _ in range(3)]
    S['lid'] = ld = keep(empty(AWAY))
    add('cylinder', 'C8CCD4', (0, 0, 0.16), radius=1.15, depth=0.32, vertices=14, parent=ld)
    add('cylinder', '8A909C', (0, 0, 0.37), radius=1.3, depth=0.12, vertices=14, parent=ld, rough=0.4)
    for j in range(6):
        add('cylinder', '3A3F4C', (1.12 * math.cos(j * PI / 3), 1.12 * math.sin(j * PI / 3), 0.46), radius=0.08, depth=0.08, vertices=6, parent=ld)
    S['vcam'] = vc = keep(empty(AWAY))
    box('22262E', (0, 0, 0), (0.24, 0.4, 0.2), vc)
    add('cylinder', '0A0A0E', (0, -0.24, 0), rot=(PI / 2, 0, 0), radius=0.07, depth=0.1, vertices=8, parent=vc)
    box('FF3020', (0.08, -0.2, 0.08), (0.03, 0.02, 0.03), vc, emit=10.0)
    reset(S)
    return S


def reset(S):
    _reset0(S)
    if 'rigA' not in S:
        return
    for rr in (S['rigA'], S['rigC']):
        seen(tree_of(rr), False)
    seen(tree_of(S['note']), True)
    S['hood'].rotation_euler = (0, 0, 0)
    for g in S['glasses'].values():
        g.hide_render = True
    for o in S['grit'] + S['clouds'] + S['bouls']:
        o.scale = (1, 1, 1)


# ---------------------------------------------------------------- helpers for the new shots
def truck_at(S, pos, yaw, hood=0.0):
    S['truck'].location = pos
    S['truck'].rotation_euler = (0, 0, yaw)
    S['hood'].rotation_euler = (-hood, 0, 0)


def roll_dust(S, A, x0, x1, t, k, n=12, grow=(1.4, 3.4), y=4.2, z=(0.8, 5.0)):
    """A wall of dust that rolls along the tunnel from x0 to x1."""
    for i in range(n):
        o = S['clouds'][i]
        u = max(0.0, min(1.0, k * 1.25 - 0.25 * rn(i, 81)))
        o.location = A(lerp(x0, x1, u) + 2.0 * rn(i, 82), (rn(i, 83) - 0.5) * 2 * y, lerp(z[0], z[1], rn(i, 84)) + 0.3 * math.sin(t * 2 + i))
        q = lerp(grow[0], grow[1], u) * (0.7 + 0.6 * rn(i, 85))
        o.scale = (q, q, q * 0.8)
        o.rotation_euler = (t * 0.6 + i, i, t * 0.4)


def hang_dust(S, A, cx, cy, t, n=12, rx=7.0, ry=3.6):
    """Dust that hangs in the air and turns slowly."""
    for i in range(n):
        o = S['clouds'][i]
        a = i * 2.4 + 0.12 * t
        o.location = A(cx + rx * (rn(i, 86) - 0.5) * 2 + 0.5 * math.sin(a), cy + ry * (rn(i, 87) - 0.5) * 2, 0.6 + 4.6 * rn(i, 88) + 0.25 * math.sin(t * 0.9 + i))
        q = 1.0 + 1.4 * rn(i, 89)
        o.scale = (q, q, q * 0.75)
        o.rotation_euler = (0.2 * t + i, i, 0.15 * t)


def facing(yaw):
    return (math.sin(yaw), -math.cos(yaw))


def hold(S, o, rig, hand=1, off=(0, -0.14, -0.04), rot=None):
    o.location = world_of(rig.hands[hand], off)
    if rot is not None:
        o.rotation_euler = rot


# ---------------------------------------------------------------- 5 August: the mountain gives way
def cave_in(S, k, t, lt):
    """The access road. The lamps along the wall flicker, rock comes off the roof, and a wall of dust rolls down the tunnel at three men and a pickup."""
    A = env(S, 'ramp', '000000', fk=2.3)
    go = sm((lt - 0.35) / 0.5)
    truck_at(S, A(lerp(4.0, 1.2, sm(k)), 1.9 + 0.03 * math.sin(t * 31), 0.03 * abs(math.sin(t * 23))), -PI / 2)
    for j, (rig, x, y) in enumerate(((S['men'][1], 6.2, -1.0), (S['men'][5], 7.6, -3.0), (S['men'][9], 9.4, -0.4))):
        xx = x - 5.5 * go * k - 0.6 * j * go * k
        rig.place(A(xx, y, 0), lerp(PI / 2, -PI / 2, sm((lt - 0.2 - 0.1 * j) / 0.25)))
        rig.apply(blend(P('stand', head=(-0.35, 0.0), aR=(1.4, 0.3, 0.6)), walk(t + j * 0.3, 2.6), go))
        rig.face, rig.jawv = 'wide', 0.7 * go
    roll_dust(S, A, 14.0, 4.5, t, sm((lt - 0.2) / 2.0), grow=(1.6, 3.0), y=4.6)
    for i, o in enumerate(S['bouls']):
        u = max(0.0, (lt - 0.15 - 0.16 * i) * 0.9) % 1.4
        o.location = A(7.5 + 5.0 * rn(i, 91), (rn(i, 92) - 0.5) * 7, max(0.3, 6.3 - 9.0 * u * u))
        s = 0.6 + 1.2 * rn(i, 93)
        o.scale = (s, s, s * 0.8)
        o.rotation_euler = (u * 6, i, u * 4)
    grit(S, A(5.0, 0.0, 6.2), t, 10, 3.0, 6.0, 1.6)
    fl = 0.5 + 0.5 * math.sin(t * 37) * math.sin(t * 13)
    lampat(S, 0, A(-1.5, 1.9, 1.6), 1600, 'FFF4D0')
    lampat(S, 1, A(5.0, -2.0, 4.6), 1500 * (1 - 0.8 * go) * (0.4 + 0.6 * fl), 'FFE2B0')
    lampat(S, 2, A(6.0, -3.5, 3.4), 3000, 'FFC890')
    shoot(S, A(lerp(-5.2, -4.2, k), -3.0, lerp(1.3, 1.6, k)), A(4.0, 0.4, 2.4), 30, fill=1.3)


def dust_blind(S, k, t, lt):
    """Afterwards: dust so thick the lamps are only glows. Three men feel their way with their arms out; Rook has a wing over his beak."""
    A = env(S, 'ramp', '2A2018', fk=1.6, skyk=0.6)
    hang_dust(S, A, 7.0, 0.5, t, rx=5.0)
    for j, (rig, x, y) in enumerate(((S['men'][1], 1.6, 0.6), (S['men'][5], -0.6, 2.2), (S['men'][9], 3.4, 2.6))):
        rig.place(A(x - 0.5 * k, y, 0), -PI / 2 + 0.5 * math.sin(t * 0.7 + j * 2))
        w = walk(t * 0.35 + j, 1.0)
        w.update(aL=_arm_((1.3 + 0.15 * math.sin(t * 2 + j), 0.5, 0.2)), aR=_arm_((1.4, -0.1 + 0.3 * math.sin(t * 1.6 + j), 0.2)), head=(0.15, 0.4 * math.sin(t * 1.1 + j)))
        rig.apply(w)
        rig.face = 'squint'
    rk = S['rook']
    rp = (-2.2, -1.3)
    cough = max(0.0, math.sin(lt * 7)) ** 4
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (-7.5, -4.5)))
    rk.apply(P('tap', aR=(1.3, -0.3, 2.3, 0.6), head=(0.25 + 0.2 * cough, 0.15), lean=0.2 + 0.2 * cough))
    S['rface'] = 'sad'
    S['hat_tip'] = 0.3
    lampat(S, 0, A(-3.5, -3.0, 2.6), 500, 'E8B880')
    lampat(S, 1, A(2.0, 1.5, 3.0), 600, 'FFC890')
    lampat(S, 2, A(6.0, 0.0, 2.5), 900, 'C89A60')
    shoot(S, A(lerp(-7.6, -6.8, k), lerp(-4.4, -4.0, k), 1.9), A(-0.6, 0.0, 2.1), 32, fill=1.0, fcol='E8C8A0')


def block_wall(S, k, t, lt):
    """The way out: one block of rock from wall to wall and floor to roof. Three lamps move over it. Rook raps on it, puts the side of his head to it, and hears nothing."""
    A = env(S, 'ramp', '000000', fk=2.3)
    M = S['men']
    for j, (rig, x, y) in enumerate(((M[0], 8.6, 1.6), (M[1], 9.6, -0.3), (M[5], 10.6, 2.9))):
        rig.place(A(x, y, 0), PI / 2 + 0.15 * (j - 1))
        rig.apply(P('stand', aR=(1.5, 0.0, 0.1) if j == 2 else (0.05, 0.12, 0.15), head=(-0.45 + 0.15 * math.sin(t * 0.8 + j * 2), 0.3 * math.sin(t * 0.5 + j))))
        rig.face = 'wide' if j == 1 else 'tired'
    rk = S['rook']
    rp = (10.3, -2.6)
    knock = (1 - sm((lt - 0.9) / 0.2)) * abs(math.sin(lt * 14))
    ear = sm((lt - 1.0) / 0.4)
    turn = sm((lt - 2.2) / 0.4)
    rk.place(A(rp[0], rp[1], 0), lerp(PI / 2, look_yaw(rp, (3.5, -3.6)), 0.75 * turn))
    rk.apply(blend(blend(P('stand', aR=(1.35 + 0.3 * knock, 0.0, 0.5 + 0.5 * knock), head=(-0.1, 0.0)), P('stand', aR=(1.2, 0.3, 0.3), head=(0.1, 0.95), lean=0.32), ear),
                   P('stand', head=(0.3, 0.0), aL=(0.05, 0.3, 0.2), aR=(0.05, 0.3, 0.2)), turn))
    S['rface'] = 'sad' if ear > 0.5 else 'calm'
    S['hat_tip'] = 0.5 * turn
    sw = math.sin(t * 0.9)
    lampat(S, 0, A(8.0, 1.0 + 2.5 * sw, 3.6), 2600, 'FFE2B0')
    lampat(S, 1, A(8.5, -3.6, 1.6), 500, 'B8D0FF')
    lampat(S, 2, A(10.5, -1.0, 5.4), 500, 'FFF0D0')
    shoot(S, A(lerp(5.2, 6.0, k), lerp(-4.4, -4.1, k), lerp(1.2, 1.4, k)), A(10.6, -0.6, lerp(2.9, 3.2, k)), 26, fill=1.3)


def _arm_(v):
    return tuple(v) + (0.0,) * (4 - len(v))


def climber(S, A, z, t, reach=0.0, nod=-0.5):
    m = S['men'][2]
    m.place(A(0.0, 1.78, z), PI)
    s = math.sin(t * 5)
    m.apply(blend(P('stand', aL=(2.3 + 0.5 * s, 0.05, 0.7 - 0.4 * s), aR=(2.3 - 0.5 * s, 0.05, 0.7 + 0.4 * s), lL=(0.8 + 0.5 * s, 1.1 + 0.4 * s), lR=(0.8 - 0.5 * s, 1.1 - 0.4 * s),
                          head=(nod, 0.0), lean=0.1),
                  P('stand', aL=(2.0, 0.05, 0.9), aR=(3.0, 0.1, 0.05), lL=(0.9, 1.3), lR=(0.3, 0.4), head=(nod, 0.0), lean=0.05), reach))
    return m


def chimney(S, k, t, lt):
    """The escape route: a ventilation raise with a ladder up its wall. One man climbs; two below light his way."""
    A = env(S, 'chim', '000000', fk=2.2)
    z = lerp(1.6, 7.4, k)
    m = climber(S, A, z, t)
    m.face = 'squint'
    M = S['men']
    for j, (rig, x, y, pose) in enumerate(((M[0], -1.5, 0.5, P('point', aR=(2.3, 0.2, 0.1), head=(-0.6, 0.0))), (M[5], 1.5, 0.9, P('stand', aL=(1.4, 0.2, 0.3), head=(-0.6, 0.0))))):
        rig.place(A(x, y, 0), look_yaw((x, y), (0, 2.3)))
        rig.apply(pose)
        rig.face = 'wide'
    grit(S, A(0.3, 1.6, z + 6.0), t, 8, 0.8, 7.0, 0.9)
    lampat(S, 0, A(-1.6, -1.6, z + 1.0), 900, 'FFE2B0')
    lampat(S, 1, A(0.2, 0.6, z + 7.0), 400, 'BFD4FF')
    lampat(S, 2, A(1.2, -1.2, 2.2), 600, 'FFE8C8')
    shoot(S, A(lerp(-1.8, -1.4, k), lerp(-3.4, -3.0, k), z - 0.9), A(0.0, 1.8, z + 2.4), 24, fill=1.3)


def ladder_end(S, k, t, lt):
    """Part-way up, the ladder stops. He reaches for a rung that is not there. On the ledge beside him, Rook looks up the bare wall, then at us."""
    A = env(S, 'chim', '000000', fk=2.3)
    give = sm((lt - 1.3) / 0.4)
    m = climber(S, A, 12.9, t * 0.15, 1.0 - 0.7 * give, lerp(-0.6, 0.35, give))
    m.face = 'tired' if give > 0.5 else 'wide'
    rk = S['rook']
    rp = (-1.85, 1.3)
    look = sm((lt - 1.5) / 0.35)
    rk.place(A(rp[0], rp[1], 13.18), lerp(look_yaw(rp, (0.4, -2.0)), look_yaw(rp, (1.4, -4.2)), look))
    rk.apply(blend(P('hips', head=(-0.7, -0.5)), P('cross', head=(0.1, 0.0)), look))
    S['rface'] = 'deadpan' if look > 0.5 else 'calm'
    S['hat_tip'] = 0.45 * look
    grit(S, A(0.2, 1.7, 21.0), t, 8, 0.8, 9.0, 0.7)
    lampat(S, 0, A(-0.6, -1.9, 15.0), 800, 'FFE2B0')
    lampat(S, 1, A(0.3, 0.6, 20.0), 500, 'BFD4FF')
    lampat(S, 2, A(-2.4, -0.6, 14.0), 260, 'FFE8C8')
    shoot(S, A(lerp(1.9, 1.5, k), lerp(-4.4, -4.0, k), lerp(13.4, 14.0, k)), A(-0.6, 1.8, lerp(15.0, 15.4, k)), 28, fill=1.3)


# ---------------------------------------------------------------- seventeen days in the shelter
def vote(S, k, t, lt):
    """The shelter. The foreman stands in front of the men and puts it to a vote; hands go up along the bench, one after another. At the end of the row Rook looks about him and raises a wing."""
    A = mine(S)
    M = S['men']
    fp = (8.7, 0.3)
    for i in range(6):
        x, y = BENCH[i]
        up = sm((lt - 0.35 - 0.14 * i) / 0.3)
        tr = max(-0.7, min(0.7, look_yaw((x, y), fp)))
        sit(M[i + 1], A, x, y, 0.0, 0.05, tr)
        M[i + 1].apply(blend(P('sit', head=(0.05, tr), lean=0.2), P('sit', aR=(2.7, 0.15, 0.25), head=(-0.08, tr), lean=0.14), up))
        M[i + 1].face = 'calm'
    for j, (x, y) in enumerate(((6.4, 2.0), (10.9, 2.2))):
        up = sm((lt - 0.7 - 0.2 * j) / 0.3)
        rig = M[7 + j]
        rig.place(A(x, y, 0.0), 0.2 * (1 - 2 * j))
        rig.apply(P('sit', lL=(1.75, 2.1), lR=(1.75, 2.1), aL=(1.2, -0.2, 1.2, 0.6), aR=_arm_((lerp(1.2, 2.6, up), lerp(-0.2, 0.1, up), lerp(1.2, 0.2, up))), lift=-0.62, lean=0.36, head=(0.0, 0.0)))
        rig.face = 'calm'
    f = M[0]
    f.place(A(fp[0], fp[1], 0), PI + 0.35 * math.sin(lt * 1.3))
    f.apply(P('point', aR=(1.45, 0.25 * math.sin(lt * 2.6), 0.1), aL=(0.9, 0.1, 1.5), head=(0.0, 0.0)))
    f.jawv = 0.3 + 0.3 * math.sin(lt * 9)
    rk = S['rook']
    rp = (13.0, 2.9)
    up = sm((lt - 1.5) / 0.3)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (9.5, -3.5)))
    rk.apply(blend(P('cross', head=(0.1, lerp(0.9, -0.6, sm((lt - 0.6) / 0.6)))), P('reach', aR=(2.7, 0.1, 0.2), head=(0.0, 0.2)), up))
    S['rface'] = 'calm'
    shelter_light(S, A)
    lampat(S, 3, A(8.0, -2.5, 3.2), 700, 'FFE8C8')
    shoot(S, A(lerp(6.2, 7.0, k), lerp(-6.6, -6.0, k), lerp(3.1, 2.8, k)), A(9.3, 2.6, 1.9), 35, fill=1.3)


def battery(S, k, t, lt):
    """A pickup stands in the gallery with its bonnet up and its lamps burning. A miner holds his helmet lamp to a cable from the battery. Rook touches the other clamp: a spark, and his hat jumps."""
    A = mine(S)
    tp = (-3.2, 2.9)
    yaw = look_yaw(tp, (-7.5, -2.5))
    truck_at(S, A(tp[0], tp[1], 0), yaw, 0.95)
    fx, fy = facing(yaw)
    front = (tp[0] + fx * 2.4, tp[1] + fy * 2.4)
    side = (-fy, fx)
    bat = A(tp[0] + fx * 1.3 - side[0] * 0.52, tp[1] + fy * 1.3 - side[1] * 0.52, 1.5)
    m = S['men'][7]
    mp = (front[0] - side[0] * 1.5 + fx * 0.2, front[1] - side[1] * 1.5 + fy * 0.2)
    m.place(A(mp[0], mp[1], 0), look_yaw(mp, (tp[0] + fx * 1.3, tp[1] + fy * 1.3)))
    m.apply(P('stand', aR=(1.1, 0.0, 0.9), aL=(1.0, 0.1, 1.1), head=(0.4, 0.0), lean=0.2))
    m.face = 'squint'
    hand = world_of(m.hands[1], (0, -0.12, -0.05))
    rope(S, 0, bat, hand, 0.02)
    glow = 0.6 + 0.4 * math.sin(t * 5)
    lampat(S, 3, (hand[0], hand[1], hand[2] + 0.3), 50 * glow, 'FFF2C0')
    m2 = S['men'][9]
    p2 = (front[0] + side[0] * 0.2 + fx * 1.6, front[1] + side[1] * 0.2 + fy * 1.6)
    m2.place(A(p2[0], p2[1], 0), look_yaw(p2, front) + 0.3)
    m2.apply(KNEEL)
    m2.face = 'tired'
    rk = S['rook']
    rp = (front[0] + side[0] * 1.55 + fx * 0.1, front[1] + side[1] * 1.55 + fy * 0.1)
    zap = sm((lt - 1.3) / 0.08)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (tp[0] + fx * 1.3, tp[1] + fy * 1.3)))
    rk.apply(blend(P('stand', aR=(1.2, -0.1, 0.5), head=(0.45, 0.0), lean=0.35), P('scream', head=(-0.1, 0.5), lean=-0.2), zap))
    S['rface'] = 'shocked' if zap > 0.5 else 'calm'
    S['hat_jump'] = 0.45 * max(0.0, math.sin(min(1.0, max(0.0, lt - 1.3) / 0.5) * PI))
    if 1.3 < lt < 1.75:
        for i, sp in enumerate(S['sparks']):
            u = (lt - 1.3) / 0.45
            a = i * 0.8
            sp.location = (bat[0] + 0.9 * u * math.cos(a), bat[1] + 0.9 * u * math.sin(a), bat[2] + 0.1 + 0.9 * u - 1.6 * u * u)
            sp.scale = (1.6 * (1 - u),) * 3
        feather(S, world_of(rk.head, (0.3, 0, 0.3)), lt, 1.35)
    lampat(S, 0, A(front[0] + fx * 3.2, front[1] + fy * 3.2, 1.2), 600, 'FFF4D0')
    lampat(S, 1, A(tp[0] - 2.0, tp[1] - 3.5, 3.6), 900, 'FFE2B0')
    lampat(S, 2, A(4.6, -1.5, 3.4), 400, 'B8D0FF')
    shoot(S, A(lerp(-9.2, -8.4, k), lerp(-4.6, -4.0, k), lerp(1.7, 2.0, k)), A(front[0] + 0.5, front[1] + 0.6, 1.7), 30, fill=1.2)


def heat(S, k, t, lt):
    """By the water drum: one man fills a cup and drinks, pulling a face; another sits against the wall and drags a forearm across his brow. Rook pants with his beak open and wipes his own."""
    A = mine(S)
    m = S['men'][8]
    mp = (5.7, 3.6)
    m.place(A(mp[0], mp[1], 0), look_yaw(mp, (6.3, 5.0)) - 0.9 * sm((lt - 0.9) / 0.4))
    drink = sm((lt - 0.9) / 0.4)
    m.apply(blend(P('stand', aR=(1.2, -0.1, 0.4), head=(0.35, 0.0), lean=0.2), P('stand', aR=(1.1, -0.2, 2.2, 0.4), head=(-0.25, 0.0)), drink))
    m.face = 'squint' if drink > 0.6 else 'tired'
    hold(S, S['cups'][0], m, 1, (0, -0.14, -0.02))
    m2 = S['men'][10]
    m2.place(A(4.4, 4.2, 0), 0.5)
    wipe = 0.5 + 0.5 * math.sin(lt * 2.4)
    m2.apply(P('sit', lL=(1.5, 1.9), lR=(1.2, 1.5), aL=_arm_((1.6, -0.4 + 0.3 * wipe, 2.1)), aR=(0.5, 0.1, 0.6), lift=-0.62, lean=0.3, head=(0.1, 0.1)))
    m2.face = 'shut' if wipe > 0.5 else 'tired'
    rk = S['rook']
    rp = (7.9, 3.3)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (7.0, -1.5)))
    pant = 0.5 + 0.5 * math.sin(lt * 9)
    rk.apply(P('hat', aR=_arm_((0.3, 1.7, 1.75 + 0.2 * math.sin(lt * 3), -1.4)), head=(0.15 + 0.05 * pant, 0.25), lean=0.12))
    S['rface'] = 'shocked'
    S['hat_tip'] = 0.25
    shelter_light(S, A, 0.9)
    lampat(S, 3, A(6.6, 1.2, 2.6), 500, 'FFA860')
    shoot(S, A(lerp(6.2, 6.8, k), lerp(-1.6, -1.0, k), lerp(1.9, 2.0, k)), A(6.4, 4.0, 1.9), 34, fill=1.2, fcol='FFD0A0')


def listen(S, k, t, lt):
    """The gallery. Four men stand with their faces turned up as grit trickles from the roof in a line that travels across and away: a drill, passing them in the rock. Rook listens with the side of his head to the wall. The sound fades; the heads go down."""
    A = mine(S)
    sx = lerp(-7.0, 9.0, k)
    gone = sm((k - 0.72) / 0.2)
    M = S['men']
    for j, (rig, x, y) in enumerate(((M[1], -2.0, 1.8), (M[4], 0.5, 2.8), (M[6], 2.2, 0.8), (M[9], -0.5, -0.3))):
        yw = look_yaw((x, y), (sx, 6.0))
        rig.place(A(x, y, 0), lerp(yw, yw * 0.6, gone))
        rig.apply(blend(P('stand', aR=(1.3, 0.5, 2.4) if j == 1 else (0.05, 0.12, 0.15), head=(-0.5, 0.0)), P('stand', head=(0.4, 0.0), lean=0.1), gone))
        rig.face = 'sad' if gone > 0.5 else 'wide'
    rk = S['rook']
    rp = (4.0, 3.9)
    rk.place(A(rp[0], rp[1], 0), PI * 0.75)
    rk.apply(blend(P('stand', aR=(1.2, 0.5, 2.3), head=(-0.2, -0.6), lean=0.1), P('stand', head=(0.4, -0.2)), gone))
    S['rface'] = 'sad' if gone > 0.5 else 'calm'
    S['hat_tip'] = 0.4 * gone
    grit(S, A(sx, 3.6, 6.7), t, 10, 0.5, 6.5, 1.5)
    lampat(S, 0, A(-2.5, -2.6, 3.2), 1500 * (1 - 0.35 * gone), 'FFE2B0')
    lampat(S, 1, A(sx, 3.2, 5.6), 420, 'BFD4FF')
    lampat(S, 2, A(4.2, 1.6, 3.0), 320, 'FFE8C8')
    shoot(S, A(lerp(-1.2, 0.2, k), lerp(-7.2, -6.6, k), lerp(1.4, 1.7, k)), A(0.9, 2.2, 2.7), 31, fill=1.3)


def bang_bit(S, k, t, lt):
    """Day seventeen. A drill bit comes down through the gallery roof in a shower of grit. Men run to it; one beats on the steel with a hammer, sparks flying, while the others shout up the hole."""
    A = mine(S)
    seen(tree_of(S['note']), False)
    z = lerp(6.6, 3.0, sm(lt / 0.7))
    drill_at(S, A, z + 0.02 * math.sin(t * 40), spin=t * 4 * (1 - sm(lt / 0.9)))
    M = S['men']
    run = sm((lt - 0.3) / 0.6)
    m = M[3]
    mp = (lerp(3.4, 0.75, run), lerp(2.4, 1.5, run))
    m.place(A(mp[0], mp[1], 0), look_yaw(mp, PROBE))
    hit = abs(math.sin(lt * 9)) if lt > 1.0 else 0.0
    m.apply(blend(walk(t, 2.4), P('stand', aR=(2.1 - 0.9 * hit, -0.1, 0.9 - 0.5 * hit), aL=(0.6, 0.2, 0.8), head=(-0.3, 0.0), lean=0.1), run))
    m.face, m.jawv = 'wide', 0.6
    hold(S, S['hammer'], m, 1, (0, -0.1, -0.1), (1.9 - 1.2 * hit, 0, look_yaw(mp, PROBE)))
    for j, (rig, x0, y0, x1, y1) in enumerate(((M[5], -5.0, 3.0, -1.5, 2.3), (M[2], 2.0, 5.0, 0.2, 3.2), (M[0], 6.5, 1.0, 2.2, 0.4))):
        r2 = sm((lt - 0.2 - 0.2 * j) / 0.8)
        p = (lerp(x0, x1, r2), lerp(y0, y1, r2))
        rig.place(A(p[0], p[1], 0.18 * r2 * abs(math.sin(t * 7 + j))), look_yaw(p, PROBE))
        rig.apply(blend(walk(t + j, 2.4), P('up', aL=(2.6 + 0.2 * math.sin(t * 9 + j), -0.4, 0.2), aR=(2.7, -0.4, 0.2), head=(-0.55, 0.0)), r2))
        rig.face, rig.jawv = 'wide', 0.7
    if hit > 0.8:
        c = A(PROBE[0], PROBE[1] - 0.1, z + 1.0)
        for i, sp in enumerate(S['sparks']):
            sp.location = (c[0] + 0.4 * math.cos(i * 0.8 + t * 30), c[1] - 0.2 + 0.3 * math.sin(i * 2.1), c[2] + 0.3 * math.sin(i + t * 20))
    grit(S, A(0, 1, 6.7), t, 10, 0.7, 6.0, 1.4)
    lampat(S, 0, A(2.6, -2.0, 3.0), 1700, 'FFE2B0')
    lampat(S, 1, A(0.2, 0.2, 6.0), 600, 'FFF4D8')
    lampat(S, 2, A(-3.0, 1.0, 2.6), 400, 'B8D0FF')
    shoot(S, A(lerp(2.6, 1.9, k), lerp(-5.2, -4.6, k), lerp(1.5, 1.8, k)), A(0.1, 1.3, lerp(3.6, 3.3, k)), 24, fill=1.3)


# ---------------------------------------------------------------- the camp, the lifeline, the three drills
def vigil(S, k, t, lt):
    """Night at the camp by the mine gate: three people stand close together with candles, the light on their faces, the tents behind. Rook stands a little apart with his head down and his hat brim low."""
    A = night(S)
    cx, cy = CAMP
    for j, (rig, x, y) in enumerate(((S['civ'][0], -1.5, -3.0), (S['civ'][1], -0.3, -2.7), (S['civ'][2], 0.9, -3.1))):
        rig.place(A(cx + x, cy + y, 0), 0.12 * (j - 1))
        rig.apply(P('stand', aL=(0.8, -0.28, 1.7, 1.0), aR=(0.8, -0.28, 1.7, 1.0), head=(0.3 + 0.05 * math.sin(t * 0.8 + j), 0.15 * (1 - j))))
        rig.face = 'sad'
        hl, hr = world_of(rig.hands[0]), world_of(rig.hands[1])
        c = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2 - 0.1, (hl[2] + hr[2]) / 2 + 0.12)
        S['candles'][j].location = c
        lampat(S, j, (c[0], c[1] - 0.3, c[2] + 0.35), 55 * (1 + 0.2 * math.sin(t * 11 + j * 2)), 'FFC070')
    rk = S['rook']
    rp = (cx + 2.9, cy - 2.6)
    rk.place(A(rp[0], rp[1], 0), -0.25)
    rk.apply(P('stand', aL=(0.6, -0.2, 1.4, 0.9), aR=(0.6, -0.2, 1.4, 0.9), head=(0.38, 0.2)))
    S['rface'] = 'sad'
    S['hat_tip'] = 0.5
    S['candles'][3].location = world_of(rk.hands[1], (-0.15, -0.16, 0.05))
    lampat(S, 3, A(cx + 2.9, cy - 3.3, 1.9), 50, 'FFC070')
    lampat(S, 4, A(cx - 6.0, cy + 1.0, 5.0), 2500, 'DCE8FF')
    shoot(S, A(cx + lerp(-2.4, -1.4, k), cy + lerp(-8.2, -7.6, k), lerp(2.0, 2.15, k)), A(cx + 0.5, cy - 2.9, 2.3), 44, fill=1.0, fcol='FFD8B0')


def three_rigs(S, k, t, lt):
    """Daylight. Three drilling rigs stand across the hillside, each over its own hole, each in its own dust. In front, Rook looks from one to the next to the next, then at us."""
    A = day(S)
    seen(tree_of(S['rigA']), True)
    seen(tree_of(S['rigC']), True)
    S['pipeA'].rotation_euler = (0, 0, t * 4)
    S['pipeC'].rotation_euler = (0, 0, -t * 3)
    sx, sy = SITE
    S['bigbit'].location = A(sx, sy, -3.0)
    S['bigbit'].rotation_euler = (0, 0, t * 5)
    S['surf']['wheel'].rotation_euler = (t * 2, PI / 2, 0)
    drill_at(S, A, -80, HOLE[0], HOLE[1])
    puffs(S, A(RIGA[0], RIGA[1], 0.3), t, 5, 3.0, 2.4, 1.6, 0)
    puffs(S, A(sx, sy, 0.3), t + 0.4, 5, 3.0, 2.4, 1.6, 5)
    puffs(S, A(RIGC[0], RIGC[1], 0.3), t + 0.8, 4, 3.4, 2.8, 2.0, 10)
    rk = S['rook']
    rp = (10.6, -17.0)
    cam = (lerp(9.4, 8.4, k), lerp(-24.5, -23.5, k), lerp(2.3, 2.7, k))
    u = lt / 0.7
    hd = 1.2 if u < 1 else 0.0 if u < 2 else -1.2 if u < 3 else 0.0
    hd2 = (1.2, 0.0, -1.2, 0.0)[min(3, int(u) + 1)] if u < 3 else 0.0
    turn = lerp(hd, hd2, sm((u % 1 - 0.7) / 0.3)) if u < 3 else 0.0
    done = sm((lt - 2.2) / 0.3)
    rk.place(A(rp[0], rp[1], 0), lerp(look_yaw(rp, (14, 5)), look_yaw(rp, cam), done))
    rk.apply(blend(P('hips', head=(-0.15, turn)), P('shrug', head=(0.0, 0.0)), done))
    S['rface'] = 'calm'
    c = S['crew'][2]
    c.place(A(4.5, -10.0, 0), look_yaw((4.5, -10.0), SITE))
    c.apply(P('point', aR=(1.5, 0.2, 0.1), head=(-0.2, 0.0)))
    shoot(S, A(*cam), A(12.5, 2.0, 7.0), 22, fill=0.6)


def dove(S, k, t, lt):
    """Daylight at the narrow borehole: two rescuers lower a long thin tube into it on a cable, hand over hand. Rook, on one knee at the collar, bends to watch it go down."""
    A = day(S, False)
    drill_at(S, A, -80, HOLE[0], HOLE[1])
    z = lerp(3.4, 0.3, sm(k))
    S['dove'].location = A(HOLE[0], HOLE[1], z)
    S['dove'].rotation_euler = (0, 0, t * 0.8)
    rope(S, 0, A(HOLE[0], HOLE[1], z + 2.5), A(HOLE[0], HOLE[1], 12.6), 0.02)
    c = S['crew'][0]
    cp = (-1.2, -3.2)
    c.place(A(cp[0], cp[1], 0), look_yaw(cp, HOLE))
    pay = math.sin(lt * 5)
    c.apply(P('stand', aR=(1.5 + 0.25 * pay, -0.15, 0.4), aL=(1.3 - 0.25 * pay, 0.05, 0.6), head=(lerp(-0.1, 0.4, k), 0.0), lean=0.15))
    c2 = S['crew'][2]
    c2.place(A(1.9, -1.5, 0.4), look_yaw((1.9, -1.5), HOLE))
    c2.apply(P('stand', aR=(1.2, 0.2, 0.5), head=(lerp(0.0, 0.35, k), 0.0)))
    rk = S['rook']
    rp = (1.7, -4.3)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (-0.9, -3.2)))
    peer = sm((lt - 0.8) / 0.5)
    rk.apply(blend(KNEEL, P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.3, aR=(1.0, 0.4, 0.3), aL=(0.9, 0.3, 0.4), head=(0.3, 0.6)), peer))
    S['rface'] = 'calm'
    shoot(S, A(lerp(-2.9, -2.3, k), lerp(-7.6, -7.0, k), lerp(1.3, 1.6, k)), A(0.1, -2.6, lerp(2.2, 1.6, k)), 34, fill=0.9)


def dove_arrive(S, k, t, lt):
    """Below: the tube comes down out of the roof on its cable. Two miners reach up and take it; one pulls out a bottle and holds it up, and the others close in."""
    A = mine(S)
    drill_at(S, A, 80)
    z = lerp(6.9, 2.0, sm(lt / 1.1))
    S['dove'].location = A(PROBE[0], PROBE[1], z)
    S['dove'].rotation_euler = (0, 0, 0.6 * math.sin(t * 1.5))
    rope(S, 0, A(PROBE[0], PROBE[1], z + 2.5), A(PROBE[0], PROBE[1], ROOF + 0.3), 0.02)
    M = S['men']
    got = sm((lt - 1.3) / 0.4)
    a = M[7]
    ap = (-0.85, 0.5)
    a.place(A(ap[0], ap[1], 0), look_yaw(ap, PROBE))
    a.apply(blend(P('up', aL=(2.4, -0.2, 0.3), aR=(2.5, -0.2, 0.3), head=(-0.5, 0.0)), P('reach', aR=(2.7, 0.2, 0.2), aL=(1.2, 0.0, 0.8), head=(-0.3, 0.3)), got))
    a.face, a.jawv = 'warm', 0.5 * got
    if got > 0.3:
        hold(S, S['bottle'], a, 1, (0, -0.1, -0.2))
    b = M[11]
    bp = (0.9, 0.35)
    b.place(A(bp[0], bp[1], 0), look_yaw(bp, PROBE))
    b.apply(P('stand', aL=(1.5, -0.1, 0.5), aR=(1.4, -0.2, 0.6), head=(lerp(-0.5, 0.0, got), 0.0)))
    b.face = 'warm'
    for j, (rig, x0, y0, x1, y1) in enumerate(((M[1], -5.5, 2.6, -2.2, 1.9), (M[2], 4.6, 3.4, 2.0, 2.2), (M[6], 2.0, 5.5, 0.2, 3.1))):
        r2 = sm((lt - 0.4 - 0.2 * j) / 1.0)
        p = (lerp(x0, x1, r2), lerp(y0, y1, r2))
        rig.place(A(p[0], p[1], 0), look_yaw(p, PROBE))
        rig.apply(blend(walk(t + j, 1.8), P('stand', aR=(1.2, 0.3, 0.9), head=(-0.2, 0.0)), r2))
        rig.face = 'warm'
    lampat(S, 0, A(-2.6, -2.2, 3.2), 1700, 'FFE2B0')
    lampat(S, 1, A(0.3, 0.2, 6.0), 700, 'FFF4D8')
    lampat(S, 2, A(3.4, 0.0, 2.6), 400, 'B8D0FF')
    shoot(S, A(lerp(-3.6, -2.9, k), lerp(-4.4, -3.9, k), lerp(1.6, 1.9, k)), A(0.0, 1.0, lerp(3.4, 2.7, k)), 30, fill=1.3)


def letter(S, k, t, lt):
    """On the bench: a miner reads a sheet of paper held in both hands, and wipes an eye with the back of his wrist. The men either side lean in. A fourth holds up a small camera; a fifth waves into it."""
    A = mine(S)
    crowd(S, A, t, face='calm', nod=0.2, row_only=True)
    M = S['men']
    x, y = BENCH[2]
    wipe = sm((lt - 1.4) / 0.3) * (1 - sm((lt - 2.3) / 0.3))
    sit(M[3], A, x, y, 0.0, 0.45, 0.0)
    M[3].apply(P('sit', aL=_arm_((lerp(0.9, 1.5, wipe), -0.2, lerp(1.2, 2.2, wipe), 0.3)), aR=(0.9, -0.2, 1.2, 0.3), head=(0.45 - 0.2 * wipe, 0.0), lean=0.22))
    M[3].face = 'warm'
    S['sheet'].location = world_of(M[3].hands[1], (-0.2, -0.2, 0.06))
    S['sheet'].rotation_euler = (-0.6, 0, 0.04 * math.sin(t * 4))
    S['sheet'].scale = (0.36, 0.36, 0.36)
    for i, tr in ((2, -0.7), (4, 0.7)):
        xx, yy = BENCH[i - 1]
        sit(M[i], A, xx, yy, 0.0, 0.3, tr)
        M[i].face = 'warm'
    c = M[9]
    cp = (10.6, 1.9)
    c.place(A(cp[0], cp[1], 0), look_yaw(cp, (9.6, 3.9)))
    c.apply(P('stand', aR=(1.5, 0.0, 0.9), aL=(1.4, 0.2, 1.0), head=(0.1, 0.0)))
    hold(S, S['vcam'], c, 1, (0, -0.2, 0.0), (0, 0, look_yaw(cp, (9.6, 3.9))))
    w = M[5]
    sit(w, A, BENCH[4][0], BENCH[4][1], 0.0, 0.0, 0.5)
    w.apply(P('sit', aR=_arm_((2.5, 0.3 + 0.35 * math.sin(lt * 8), 0.4)), head=(0.0, 0.5), lean=0.15))
    w.face, w.jawv = 'warm', 0.5
    shelter_light(S, A, 0.9)
    lampat(S, 3, A(7.4, 1.4, 2.6), 380, 'FFE8C8')
    shoot(S, A(lerp(6.6, 7.3, k), lerp(-1.0, -0.5, k), lerp(1.9, 2.0, k)), A(x + 0.6, 3.6, 1.8), 36, fill=1.3)


def muck(S, k, t, lt):
    """Under the new shaft, rock rattles down out of the roof onto a growing heap. Three miners shovel it into a barrow. Rook has a shovel too, until a stone bounces off his hat."""
    A = mine(S)
    seen(S['mine']['drop'], True)
    seen(S['mine']['pile'], True)
    dx, dy = DROP
    for i, o in enumerate(S['grit']):
        u = (t * 1.3 + rn(i, 71)) % 1
        o.location = A(dx + 0.8 * (rn(i, 72) - 0.5) * 2, dy + 0.8 * (rn(i, 73) - 0.5) * 2, 6.8 - 6.4 * u * u)
        s = 1.2 + 1.6 * rn(i, 74)
        o.scale = (s, s, s)
    puffs(S, A(dx, dy, 0.3), t, 6, 2.0, 1.2, 0.8)
    M = S['men']
    for j, (rig, x, y) in enumerate(((M[1], -4.6, 1.9), (M[6], -5.3, -2.0), (M[8], -6.4, 3.0))):
        yw = look_yaw((x, y), DROP)
        dig = 0.5 + 0.5 * math.sin(t * 4 + j * 2.1)
        rig.place(A(x, y, 0), yw)
        rig.apply(P('stand', aL=(0.9 + 0.5 * dig, -0.2, 0.5), aR=(1.2 + 0.5 * dig, -0.3, 0.4), lean=0.55 - 0.3 * dig, lL=(0.3, 0.4), lR=(-0.1, 0.2), lift=-0.08, head=(0.2, 0.0)))
        rig.face = 'squint'
        hold(S, S['shovels'][j], rig, 1, (0, -0.1, 0.0), (2.0 - 0.7 * dig, 0, yw))
    S['barrow'].location = A(-3.9, -0.2, 0)
    S['barrow'].rotation_euler = (0, 0, 2.2)
    rk = S['rook']
    rp = (-9.2, 1.5)
    bonk = sm((lt - 1.5) / 0.08)
    yw = look_yaw(rp, DROP)
    dig = (0.5 + 0.5 * math.sin(t * 4)) * (1 - bonk)
    rk.place(A(rp[0], rp[1], 0), lerp(yw, look_yaw(rp, (-11.6, -6.4)), sm((lt - 1.8) / 0.3)))
    rk.apply(blend(P('stand', aL=(0.9 + 0.5 * dig, -0.2, 0.5), aR=(1.2 + 0.5 * dig, -0.3, 0.4), lean=0.5 - 0.3 * dig, head=(0.2, 0.0)), P('stand', aR=(0.6, 0.2, 0.8), head=(0.05, 0.0)), bonk))
    hold(S, S['shovels'][3], rk, 1, (0, -0.1, 0.0), (lerp(2.0 - 0.7 * dig, 0.5, bonk), 0, yw))
    S['rface'] = 'deadpan' if bonk > 0.5 else 'calm'
    S['hat_sq'] = bonk * (1 - sm((lt - 2.6) / 0.3))
    hd = world_of(rk.head, (0, 0, 0.75))
    u = max(0.0, lt - 1.1)
    S['bouls'][0].location = (hd[0] + (1.4 - 3.5 * u if u < 0.4 else 1.3 * (u - 0.4)), hd[1], hd[2] + (3.2 - 20 * u * u if u < 0.4 else 1.5 * (u - 0.4) - 6 * (u - 0.4) ** 2))
    S['bouls'][0].scale = (0.45,) * 3
    gallery_light(S, A)
    shoot(S, A(lerp(-12.4, -11.6, k), lerp(-6.8, -6.2, k), lerp(1.7, 1.9, k)), A(-7.3, -0.3, 2.5), 26, fill=1.3)


def workshop(S, k, t, lt):
    """Daylight: the capsule lies on two trestles. One rescuer tightens something at its head, sparks at his hands; another kneels at the wheels. Rook holds his orange rule across the end of it, reads it, and looks at us."""
    A = day(S)
    sx, sy = SITE[0] - 9.0, SITE[1] - 7.0
    S['cap'].location = A(sx - 2.35, sy, 1.83)
    S['cap'].rotation_euler = (0, PI / 2, 0)
    for j, tr in enumerate(S['trestles']):
        tr.location = A(sx - 1.4 + 2.8 * j, sy, 0)
    c = S['crew'][0]
    cp = (sx + 2.9, sy + 0.5)
    c.place(A(cp[0], cp[1], 0), look_yaw(cp, (sx + 2.0, sy)))
    wr = math.sin(lt * 8)
    c.apply(P('stand', aR=(1.3 + 0.15 * wr, -0.1, 0.6), aL=(1.2, 0.1, 0.7), head=(0.3, 0.0), lean=0.2))
    for i, sp in enumerate(S['sparks']):
        u = (t * 2.4 + i / 8) % 1
        sp.location = A(sx + 2.4 + 0.7 * u * math.cos(i * 0.9), sy - 0.2 - 0.5 * u, 2.3 + 0.5 * u - 1.6 * u * u)
        sp.scale = (1.5 * (1 - u),) * 3
    c1 = S['crew'][1]
    kp = (sx + 0.3, sy + 1.6)
    c1.place(A(kp[0], kp[1], 0), look_yaw(kp, (sx + 0.3, sy)))
    c1.apply(KNEEL)
    rk = S['rook']
    rp = (sx - 3.7, sy - 0.9)
    cam = (sx + lerp(1.6, 2.4, k), sy + lerp(-7.0, -6.4, k), lerp(1.9, 2.1, k))
    lay = sm((lt - 0.2) / 0.4)
    look = sm((lt - 1.4) / 0.3)
    rk.place(A(rp[0], rp[1], 0), lerp(look_yaw(rp, (sx - 2.0, sy - 0.5)), look_yaw(rp, cam), 0.6 * look))
    rk.apply(blend(P('stand', aR=(0.6, 0.1, 0.9), head=(0.2, 0.0)), P('stand', aR=(1.45, -0.05, 0.2), head=(0.3 - 0.3 * look, 0.0), lean=0.15), lay))
    S['ruler'].location = A(sx - 2.5, sy - lerp(1.2, 0.0, lay), lerp(1.4, 1.83, lay))
    S['ruler'].rotation_euler = (0, 0, PI / 2)
    S['rface'] = 'deadpan' if look > 0.5 else 'calm'
    S['hat_tip'] = 0.3 * look
    shoot(S, A(*cam), A(sx - 0.6, sy, 1.75), 32, fill=0.8)


def first_down(S, k, t, lt):
    """Night at the shaft. A rescuer stands in the cage, raises one hand to the men round him, and the capsule sinks out of the floodlights. Rook touches his brim to him."""
    A = night(S, True)
    sx, sy = SITE
    z = lerp(0.4, -4.2, sm((lt - 1.1) / 1.6))
    c = S['crew'][1]
    wave = sm((lt - 0.2) / 0.3)
    cap_at(S, A, sx, sy, z, c, 0.25, P('stand', aL=(0.05, 0.02, 0.2), aR=_arm_((lerp(0.1, 1.5, wave), 0.5, lerp(0.2, 1.9, wave))), head=(0.0, 0.2)))
    c.face = 'calm'
    cable_top(S, A, sx, sy, z)
    S['surf']['wheel'].rotation_euler = (z * 1.2, PI / 2, 0)
    for j, (rig, x, y) in enumerate(((S['crew'][0], -2.5, -1.2), (S['crew'][2], -1.7, 2.0), (S['civ'][2], -3.9, -2.4))):
        rig.place(A(sx + x, sy + y, 0), look_yaw((x, y), (0, 0)))
        cp = 0.5 + 0.5 * math.sin(t * 13 + j)
        rig.apply(P('stand', aL=(1.1, -0.1 - 0.25 * cp, 1.3, 0.5), aR=(1.1, -0.1 - 0.25 * cp, 1.3, 0.5), head=(lerp(-0.1, 0.35, sm((lt - 1.1) / 1.4)), 0.0)))
        rig.face = 'calm'
    rk = S['rook']
    rp = (sx + 2.5, sy - 0.2)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (sx + 0.6, sy - 3.0)))
    rk.apply(P('hat', head=(lerp(0.0, 0.35, sm((lt - 1.1) / 1.4)), 0.7)))
    S['rface'] = 'calm'
    S['hat_tip'] = 0.3
    rig_floods(S, A, 1.0, True)
    lampat(S, 0, A(sx + 1.0, sy - 5.5, 3.0), 1700, 'FFF0D8')
    shoot(S, A(sx + lerp(3.4, 2.6, k), sy + lerp(-8.0, -7.4, k), lerp(2.1, 2.4, k)), A(sx + 0.2, sy - 0.2, lerp(2.8, 2.0, k)), 32, fill=1.1, fcol='DCE4FF')


def greet(S, k, t, lt):
    """Below: the capsule stands in the rubble and the rescuer steps out of it. The miners close round him; one takes him by both shoulders, the others have their arms in the air. Rook lifts his hat."""
    A = mine(S)
    seen(S['mine']['drop'], True)
    seen(S['mine']['pile'], True)
    dx, dy = DROP
    cap_at(S, A, dx, dy, 0.25)
    rope(S, 0, A(dx, dy, 4.85), A(dx, dy, ROOF + 0.4), 0.03)
    out = sm(lt / 0.7)
    c = S['crew'][1]
    cp = (lerp(dx, dx + 1.5, out), lerp(dy, dy - 1.5, out))
    c.root.scale = (lerp(0.84, 1.0, out),) * 3
    c.place(A(cp[0], cp[1], 0.7 * (1 - out)), look_yaw(cp, (dx + 4, dy - 4)))
    c.apply(blend(P('stand'), P('stand', aL=(1.1, 0.5, 0.5), aR=(1.1, 0.5, 0.5), head=(0.0, 0.0)), out))
    c.face, c.jawv = 'warm', 0.4
    M = S['men']
    hugp = (dx + 2.3, dy - 2.2)
    h = M[1]
    hx = lerp(dx + 4.5, hugp[0], out)
    h.place(A(hx, lerp(dy - 3.4, hugp[1], out), 0), look_yaw((hx, hugp[1]), cp))
    h.apply(blend(walk(t, 2.2), P('stand', aL=(1.4, -0.2, 0.5), aR=(1.4, -0.2, 0.5), head=(-0.1, 0.0), lean=0.15), out))
    h.face, h.jawv = 'warm', 0.6
    for j, (rig, x, y) in enumerate(((M[4], -4.4, 2.2), (M[6], -9.4, 1.9), (M[0], -8.6, -1.9), (M[8], -3.6, -2.9))):
        rig.place(A(x, y, 0.22 * abs(math.sin(t * 6 + j * 1.4))), look_yaw((x, y), cp))
        rig.apply(P('up', aL=(2.6 + 0.2 * math.sin(t * 10 + j), -0.4, 0.2), aR=(2.7, -0.4, 0.2), head=(-0.15, 0.0)))
        rig.face, rig.jawv = 'warm', 0.7
    rk = S['rook']
    rp = (dx + 4.3, dy + 1.4)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (dx + 2.0, dy - 6.0)))
    rk.apply(P('hat', head=(0.05, 0.5)))
    S['rface'] = 'warm'
    S['hat_jump'] = 0.3 * sm((lt - 0.8) / 0.3)
    gallery_light(S, A)
    shoot(S, A(dx + lerp(5.6, 4.8, k), lerp(-7.4, -6.8, k), lerp(1.6, 1.9, k)), A(dx + 0.9, -0.6, 2.4), 28, fill=1.3)


# ---------------------------------------------------------------- 13 October
def shades(S, k, t, lt):
    """Close: the first man up, in dark glasses against the floodlights, the cage behind him. He turns his face up to the night sky, breathes out, and his fists go up."""
    A = night(S, True)
    sx, sy = SITE
    cap_at(S, A, sx, sy, 0.35)
    cable_top(S, A, sx, sy, 0.35)
    m = S['men'][4]
    S['glasses'][4].hide_render = False
    mp = (sx - 0.5, sy - 2.2)
    m.place(A(mp[0], mp[1], 0), look_yaw(mp, (sx - 1.6, sy - 9.0)))
    up = sm((lt - 0.9) / 0.35)
    m.apply(blend(P('stand', head=(lerp(0.1, -0.45, sm(lt / 0.6)), 0.0)), P('up', aL=(2.5, 0.3, 0.6), aR=(2.5, 0.3, 0.6), head=(-0.3, 0.0)), up))
    m.face, m.jawv = 'warm', 0.3 + 0.4 * up
    welcome(S, A, t, 1.0)
    S['crew'][0].place(A(sx - 3.4, sy - 0.6, 0), 0.4)
    rig_floods(S, A, 1.0, True)
    lampat(S, 0, A(sx - 1.4, sy - 5.6, 3.2), 1200, 'FFF0D8')
    hd = world_of(m.head)
    shoot(S, A(sx + lerp(-2.0, -1.5, k), sy + lerp(-6.0, -5.4, k), lerp(2.3, 2.5, k)), (hd[0] + 0.5, hd[1], hd[2] + 0.15), 50, fill=1.2, fcol='FFE8D0')


def gift(S, k, t, lt):
    """The second man up, in dark glasses, has a sack with him. He takes out a lump of rock and presses it into a rescuer's hands, then one into Rook's. Rook holds it up to the floodlight: it glitters."""
    A = night(S, True)
    sx, sy = SITE
    cap_at(S, A, sx, sy, 0.35)
    cable_top(S, A, sx, sy, 0.35)
    m = S['men'][6]
    S['glasses'][6].hide_render = False
    mp = (sx - 0.3, sy - 2.9)
    c = S['crew'][0]
    cp = (sx - 1.9, sy - 3.4)
    rk = S['rook']
    rp = (sx + 1.35, sy - 3.5)
    g1 = sm((lt - 0.3) / 0.3)
    g2 = sm((lt - 1.2) / 0.3)
    m.place(A(mp[0], mp[1], 0), lerp(look_yaw(mp, cp), look_yaw(mp, rp), g2))
    m.apply(P('stand', aR=_arm_((1.35, -0.1, 0.4 + 0.3 * math.sin(lt * 6))), aL=(0.4, 0.2, 0.9), head=(0.05, 0.0)))
    m.face, m.jawv = 'warm', 0.6
    S['sack'].location = world_of(m.hands[0], (0, -0.1, -0.35))
    c.place(A(cp[0], cp[1], 0), look_yaw(cp, mp))
    c.apply(blend(P('stand'), P('stand', aL=(1.1, -0.2, 0.9), aR=(1.1, -0.2, 0.9), head=(0.35, 0.0)), g1))
    c.face = 'warm'
    if g1 > 0.6:
        hold(S, S['rocks'][0], c, 1, (-0.15, -0.16, 0.02))
    up = sm((lt - 1.8) / 0.35)
    rk.place(A(rp[0], rp[1], 0), lerp(look_yaw(rp, mp), look_yaw(rp, (sx + 0.4, sy - 9.5)), 0.7 * up))
    rk.apply(blend(blend(P('stand', head=(0.1, 0.0)), P('stand', aR=(1.2, -0.1, 0.8), head=(0.3, 0.0)), g2), P('reach', aR=(2.5, 0.15, 0.5), head=(-0.4, -0.15)), up))
    S['rface'] = 'shocked' if up > 0.4 else 'calm'
    S['hat_jump'] = 0.2 * up
    if g2 > 0.6:
        hold(S, S['rocks'][1], rk, 1, (0, -0.14, -0.06))
        S['rocks'][1].scale = (1.3,) * 3
        hp = world_of(rk.hands[1])
        lampat(S, 3, (hp[0], hp[1] - 0.5, hp[2] + 0.2), 40 * up * (1 + 0.5 * math.sin(t * 14)), 'FFE080')
    else:
        hold(S, S['rocks'][1], m, 1, (0, -0.14, -0.06))
    for j, (rig, x, y) in enumerate(((S['crew'][2], 3.4, -1.2), (S['civ'][1], -3.6, -1.4))):
        rig.place(A(sx + x, sy + y, 0), look_yaw((x, y), (-0.3, -2.9)))
        cl = 0.5 + 0.5 * math.sin(t * 13 + j)
        rig.apply(P('stand', aL=(1.1, -0.1 - 0.25 * cl, 1.3, 0.5), aR=(1.1, -0.1 - 0.25 * cl, 1.3, 0.5)))
        rig.face = 'warm'
    rig_floods(S, A, 1.0, True)
    lampat(S, 0, A(sx - 0.6, sy - 7.5, 3.0), 1800, 'FFF0D8')
    shoot(S, A(sx + lerp(0.2, -0.2, k), sy + lerp(-9.4, -8.8, k), lerp(1.9, 2.1, k)), A(sx - 0.2, sy - 3.1, 2.3), 36, fill=1.2, fcol='FFE8D0')


def lights_out(S, k, t, lt):
    """The gallery from the shelter end: a table with cups left on it, the bench bare. Far down the tunnel the capsule rises into the roof with the last rescuer in it, and the lamps go down behind him."""
    A = mine(S)
    seen(S['mine']['drop'], True)
    seen(S['mine']['pile'], True)
    dx, dy = DROP
    z = lerp(0.25, 7.6, sm((lt - 0.4) / 2.4))
    c = S['crew'][1]
    cap_at(S, A, dx, dy, z, c, -0.6)
    rope(S, 0, A(dx, dy, z + 4.6), A(dx, dy, ROOF + 0.4), 0.03)
    for j in range(5):
        S['cups'][j].location = A(10.0 + 0.3 * j, 0.45 + 0.2 * (j % 2), 1.14)
    S['tins'][0].location = A(11.2, 0.8, 1.13)
    dim = 1 - 0.7 * sm((lt - 1.6) / 2.0)
    lampat(S, 0, A(-4.0, -3.4, 3.6), 2400 * dim, 'FFE2B0')
    lampat(S, 1, A(dx, dy - 1.0, 5.6), 2600, 'FFF8E8')
    lampat(S, 2, A(9.0, 0.6, 4.6), 900 * dim, 'FFD8A0')
    shoot(S, A(lerp(12.8, 12.0, k), lerp(-3.6, -3.3, k), lerp(2.1, 2.4, k)), A(-5.0, 0.4, 3.0), 36, fill=1.3)


def sealed(S, k, t, lt):
    """Day. The rigs and the tower are gone; a steel lid is bolted over the shaft. Dust blows across it. Rook stands over it with his hat brim down, then looks up at the hills."""
    A = day(S, False)
    drill_at(S, A, -80, HOLE[0], HOLE[1])
    sx, sy = SITE
    S['lid'].location = A(sx, sy, 0)
    S['lid'].scale = (1.3, 1.3, 1.3)
    puffs(S, A(sx - 6.0 + 9.0 * ((t * 0.25) % 1), sy - 1.0, 0.3), t, 6, 2.0, 0.5, 0.7)
    rk = S['rook']
    rp = (sx - 1.9, sy - 2.3)
    look = sm((lt - 1.6) / 0.5)
    rk.place(A(rp[0], rp[1], 0), look_yaw(rp, (sx - 3.0, sy - 9.0)))
    rk.apply(blend(P('hat', head=(0.45, -0.45)), P('stand', aL=(0.3, 0.1, 0.4), aR=(0.3, 0.1, 0.4), head=(-0.2, 0.5)), look))
    S['rface'] = 'calm'
    S['hat_tip'] = 0.5 * (1 - look)
    shoot(S, A(sx + lerp(-5.6, -4.8, k), sy + lerp(-7.2, -6.6, k), lerp(1.5, 1.9, k)), A(sx - 0.9, sy - 1.0, 1.6), 34, fill=0.8)


# ---------------------------------------------------------------- the thumbnail picture
def photo_thumb(S, k, t, lt):
    """Close in the lamp light: a miner's hands on the note tied to the drill, his face behind it, eyes wide."""
    S['prm'] = {}
    tie_note(S, 0.55, 1.0, 0.5)
    m = S['men'][3]
    m.face, m.jawv = 'wide', 0.5
    d = S['drill'].location
    lampat(S, 3, (d[0] + 0.2, d[1] - 2.2, d[2] + 2.4), 420, 'FFE8C8')
    shoot(S, (d[0] + 1.7, d[1] - 3.0, d[2] + 1.85), (d[0] - 0.75, d[1] + 0.3, d[2] + 1.45), 40, fill=1.8)


def shift(S, k, t, lt):
    """An ordinary shift: the pickup rolls down the access road with its lamps on, two miners walking beside it. Rook rides in the back with his arms folded, looking about him."""
    A = env(S, 'ramp', '000000', fk=2.3)
    x = lerp(-6.0, -1.0, k)
    truck_at(S, A(x, 1.2, 0.02 * abs(math.sin(t * 19))), PI / 2)
    for j, (rig, dx_, y) in enumerate(((S['men'][1], 4.4, -0.7), (S['men'][5], 6.0, 0.9))):
        rig.place(A(x + dx_, y, 0), PI / 2)
        rig.apply(walk(t + j * 0.4, 1.5))
        rig.face = 'calm'
    rk = S['rook']
    rk.place(A(x - 2.1, 1.2, 1.2), look_yaw((0, 0), (0.3, -1)))
    rk.apply(P('cross', head=(-0.1 + 0.1 * math.sin(lt * 2), 0.7 * math.sin(lt * 1.6))))
    S['rface'] = 'deadpan'
    lampat(S, 0, A(x + 4.5, 1.2, 1.4), 1700, 'FFF4D0')
    lampat(S, 1, A(x - 1.0, -3.0, 4.4), 1500, 'FFE2B0')
    lampat(S, 2, A(x - 8.0, 0.0, 3.5), 500, 'B8D0FF')
    shoot(S, A(lerp(-9.5, -5.5, k), lerp(-4.3, -4.0, k), lerp(1.7, 2.0, k)), A(x - 0.6, 0.6, 2.1), 30, fill=1.2)


HOST |= {'shift', 'dust_blind', 'block_wall', 'ladder_end', 'vote', 'battery', 'heat', 'listen', 'vigil', 'three_rigs', 'dove', 'muck', 'workshop', 'first_down',
         'greet', 'gift', 'sealed'}
SHOTS3D.update({f.__name__: f for f in (
    shift, cave_in, dust_blind, block_wall, chimney, ladder_end, vote, battery, heat, listen, bang_bit, vigil, three_rigs, dove, dove_arrive, letter, muck,
    workshop, first_down, greet, shades, gift, lights_out, sealed)})
STILLS.update(thumb=photo_thumb)


def _shaded(f, who):
    """The men wore dark glasses when they came up into the light: put them on in the Short's shots at the surface too."""
    def g(S, k, t, lt):
        f(S, k, t, lt)
        S['glasses'][who].hide_render = False
    g.__name__ = f.__name__
    return g


for _k in ('emerge', 'hug'):
    SHOTS3D[_k] = _shaded(SHOTS3D[_k], 4)

# A wide frame held for three or four seconds needs more than a slow push: every shot also swings a little round its own subject.
# The rate is degrees per second; prm "orb": [degrees, dolly, rise] sets it for one shot.
SWING = dict(three_rigs=6.0, lights_out=6.0, vigil=7.0, shaft_ride=0.0, ride_face=0.0, tie_note=4.0, spoon=6.0, sealed=11.0, rook_wrong=10.0, signoff=9.0, rig_night=12.0,
             big_drill=10.0, tents=10.0, refuge_wide=10.0, capsule_top=10.0, cabinet=9.0, hole_measure=9.0, heat=9.0, letter=9.0)


def _swung(f, name):
    sign = 1 if sum(map(ord, name)) % 2 else -1
    rate = SWING.get(name, 8.0)

    def g(S, k, t, lt):
        f(S, k, t, lt)
        d = lt / k if k > 0.02 else 3.0
        o = S['prm'].get('orb')
        deg, dolly, rise = (list(o) + [0, 0])[:3] if o else (sign * rate * d, min(0.3, 0.05 * d) if rate else 0.0, 0.0)
        c, tg = S['camrig'].location, S['camtgt'].location
        a = math.radians(deg) * (k - 0.5)
        m = 1 - dolly * (k - 0.5)
        dx, dy = c[0] - tg[0], c[1] - tg[1]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, c[2] + rise * (k - 0.5))
    g.__name__ = f.__name__
    return g


def _closer(f, mul, dz=0.0):
    def g(S, k, t, lt):
        f(S, k, t, lt)
        c, tg = S['camrig'].location, S['camtgt'].location
        S['camrig'].location = (tg[0] + (c[0] - tg[0]) * mul, tg[1] + (c[1] - tg[1]) * mul, c[2] + dz)
    g.__name__ = f.__name__
    return g


SHOTS3D['shaft_ride'] = _closer(SHOTS3D['shaft_ride'], 0.6)


def _lower(f, dz, mul):
    """The Short's portrait close-up puts the faces where the wide frame carries the opening words: aim higher and stand back."""
    def g(S, k, t, lt):
        f(S, k, t, lt)
        c, tg = S['camrig'].location, S['camtgt'].location
        S['camtgt'].location = (tg[0], tg[1], tg[2] + dz)
        S['camrig'].location = (tg[0] + (c[0] - tg[0]) * mul, tg[1] + (c[1] - tg[1]) * mul, c[2] + 0.4 * dz)
    g.__name__ = f.__name__
    return g


SHOTS3D['tie_note'] = _lower(SHOTS3D['tie_note'], 0.95, 1.25)
SHOTS3D = {name: _swung(f, name) for name, f in SHOTS3D.items()}
