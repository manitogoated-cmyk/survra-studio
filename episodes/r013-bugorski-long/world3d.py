"""Case 013 in 3D - Anatoli Bugorski, the physicist whose head was crossed by the proton beam of the largest
particle accelerator in the Soviet Union in 1978, and who lived, finished his doctorate and went back to work there.

Built for this story only: a curved accelerator tunnel (magnets on plinths, a beam pipe with one open gap, an
instrument stand, a warning lamp on a post), a control room (console, dials, a ring diagram, a wall clock), a clinic
room, a small study with a blackboard, a snowy institute yard at night, and a schematic wire-frame head for the
beam's path.

Everything is a generic low-poly reconstruction, not a model of the real institute, machine or hospital. No emblem,
flag, sign or lettering is shown anywhere. A real proton beam is invisible inside its pipe; here it is drawn as a
line of light so the story can be followed. Nothing graphic is shown: no wound, only a bandage and a swollen cheek."""
import math

import bpy

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
ORG = dict(ring=(0, 0, 0), ctrl=(3000, 0, 0), clinic=(6000, 0, 0), yard=(9000, 0, 0), study=(12000, 0, 0), xray=(15000, 0, 0))
FAR = (0, 0, -2000)
HOST = {'bug_flash', 'rook_flinch', 'rook_gate', 'rook_door', 'bug_walk', 'ctrl_room', 'bug_lean', 'lamp_off', 'bug_work', 'bug_swell',
        'doctor', 'rook_bed', 'rook_shock', 'face_half', 'bug_back', 'rook_wrong', 'signoff'}
ROOK = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN = 'E2B694'
COAT = 'DDE0DA'
BUG = dict(top=COAT, pants='39404E', hand=SKIN, boot='1A1A20')
PAT = dict(top='9DB4C4', pants='9DB4C4', hand=SKIN, boot=SKIN)
DOC = dict(top='EEF0EA', pants='EEF0EA', hand='D9AE8E', boot='20222A')
OPR = dict(top='44566E', pants='2C3442', hand='D6A888', boot='16161C')
RR, DA, NSEG, BZ = 90.0, 0.07, 13, 2.0          # the tunnel: beam-line radius, angle per segment, segments each way, beam height
_MOV = []


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def at(name, x, y, z):
    o = ORG[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def arc(a, off=0.0, z=0.0):
    """A point of the tunnel: angle a along the ring, off metres outward from the beam line (the aisle side)."""
    return ((RR + off) * math.sin(a), RR - (RR + off) * math.cos(a), z)


def group(name, fn):
    """Build one set under its own origin and collection, so only one renders per shot."""
    old = set(bpy.data.objects)
    out = fn(empty(ORG[name]))
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for o in set(bpy.data.objects) - old:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        coll.objects.link(o)
    return coll, out


def own_mat(name, col, rough=0.6, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = rough
    tint(m, col, emit)
    return m


def tint(m, col, emit=0.0):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)
    b.inputs['Emission Color'].default_value = K.hexc(col)
    b.inputs['Emission Strength'].default_value = emit


def use(o, m):
    o.data.materials[0] = m
    return o


def mov(o):
    """Register a prop that shots move, so reset() can put it back exactly as it was built."""
    _MOV.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def rnd(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def vis(objs, on):
    for o in objs:
        o.hide_render = not on


def facing(frm, to):
    """Yaw that turns a rig standing at frm to look at to (rigs face -Y at yaw 0)."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


# ---------------------------------------------------------------- the accelerator tunnel
def set_ring(r):
    out = dict(beam=[], ring_lights=[])
    beamm = own_mat('beam', 'D6E6FF', 0.4, 60.0)
    L = (RR + 9.5) * DA + 0.25
    for i in range(-NSEG, NSEG + 1):
        a = i * DA
        rz = (0, 0, a)
        add('cube', '3B4048', arc(a, 2.5, -0.1), rot=rz, scale=(L, 15, 0.2), size=1, parent=r)                    # floor
        add('cube', '6E5A28', arc(a, 1.75, 0.01), rot=rz, scale=(L, 0.14, 0.02), size=1, parent=r, rough=0.6)     # a painted line along the aisle
        add('cube', '23262E', arc(a, 2.5, 8.1), rot=rz, scale=(L, 15, 0.2), size=1, parent=r)                     # ceiling
        for off in (-4.6, 9.6):                                                                                   # walls: dark green dado, pale above
            add('cube', '8A8E84', arc(a, off, 5.4), rot=rz, scale=(L, 0.3, 5.4), size=1, parent=r)
            add('cube', '2C5A50', arc(a, off, 1.35), rot=rz, scale=(L, 0.34, 2.7), size=1, parent=r)
        add('cube', '22252C', arc(a, -4.2, 6.3), rot=rz, scale=(L, 0.6, 0.12), size=1, parent=r)                  # cable tray
        add('cube', 'FF7A1A', arc(a, -4.1, 6.42), rot=rz, scale=(L, 0.1, 0.1), size=1, parent=r, rough=0.5)
        add('cube', '15171C', arc(a, -4.3, 6.42), rot=rz, scale=(L, 0.14, 0.12), size=1, parent=r)
        add('cube', 'FFF0D2', arc(a, 3.4, 7.95), rot=rz, scale=(3.2, 0.5, 0.1), size=1, parent=r, emit=7.0)       # ceiling strip lamp
        if i % 3 == 0:
            out['ring_lights'].append(light(arc(a, 3.0, 7.3), 1500, 'FFE8C8', kind='POINT', parent=r))
        b = add('cylinder', 'D6E6FF', arc(a, 0, BZ), rot=(0, PI / 2, a), radius=0.3, depth=RR * DA + 0.05, vertices=6, parent=r)
        out['beam'].append((a, use(b, beamm)))
        b.hide_render = True
        if i == 0:
            continue
        yel = i % 3 == 0
        ln = 3.4 if yel else 5.2
        col = 'C9A227' if yel else '2B5FA8'
        add('cube', '555B66', arc(a, 0, 0.45), rot=rz, scale=(ln - 0.6, 2.4, 0.9), size=1, parent=r)               # plinth
        for z in (1.25, 2.75):                                                                                    # a C-shaped magnet, open to the aisle
            add('cube', col, arc(a, 0, z), rot=rz, scale=(ln, 3.0, 0.7), size=1, parent=r, rough=0.55)
        add('cube', col, arc(a, -1.0, 2.0), rot=rz, scale=(ln, 1.0, 2.2), size=1, parent=r, rough=0.55)
        add('cube', 'E8E4D4', arc(a, 1.53, 2.95), rot=rz, scale=(ln * 0.5, 0.05, 0.12), size=1, parent=r)
        for z in (1.68, 2.32):                                                                                    # copper coils above and below the pipe
            add('cube', 'B8683A', arc(a, 0.1, z), rot=rz, scale=(ln + 0.5, 2.5, 0.16), size=1, parent=r, rough=0.4)
        add('cylinder', 'B9C0CA', arc(a, 0, BZ), rot=(0, PI / 2, a), radius=0.2, depth=RR * DA + 0.02, vertices=8, parent=r, rough=0.3)   # beam pipe
    for s in (-1, 1):                                                                                             # the open gap in the pipe
        add('cylinder', 'B9C0CA', (s * 2.9, 0, BZ), rot=(0, PI / 2, 0), radius=0.2, depth=0.62, vertices=8, parent=r, rough=0.3)
        add('cylinder', '8E96A4', (s * 2.6, 0, BZ), rot=(0, PI / 2, 0), radius=0.5, depth=0.14, vertices=10, parent=r, rough=0.3)
        add('cylinder', '07080B', (s * 2.52, 0, BZ), rot=(0, PI / 2, 0), radius=0.17, depth=0.02, vertices=10, parent=r)
        add('cube', '555B66', (s * 2.75, 0, 0.9), scale=(0.3, 0.3, 1.8), size=1, parent=r)
    add('cube', '3C424E', (1.5, 0, 0.7), scale=(1.5, 1.3, 1.4), size=1, parent=r)                                  # the instrument stand
    add('cube', '2A2E38', (1.5, -0.66, 0.9), scale=(1.2, 0.04, 0.8), size=1, parent=r)
    add('cylinder', 'E8E4D4', (1.15, -0.69, 1.0), rot=(PI / 2, 0, 0), radius=0.24, depth=0.03, vertices=12, parent=r, rough=0.3)
    out['fneedle'] = n = mov(empty((1.15, -0.72, 1.0), r))
    add('cube', 'D8362A', (0, 0, 0.1), scale=(0.03, 0.02, 0.22), size=1, parent=n)
    out['faultm'] = fm = own_mat('fault', '3EC46A', 0.4, 6.0)
    use(add('cylinder', '3EC46A', (1.85, -0.69, 1.0), rot=(PI / 2, 0, 0), radius=0.12, depth=0.05, vertices=8, parent=r), fm)
    add('cube', '555B66', (1.7, 0, 1.55), scale=(0.12, 0.12, 0.4), size=1, parent=r)
    add('torus', 'C89A3A', (1.7, 0, BZ), rot=(0, PI / 2, 0), major_radius=0.36, minor_radius=0.05, major_segments=12, minor_segments=4, parent=r, rough=0.3)
    gb = add('cylinder', 'D6E6FF', (0, 0, BZ), rot=(0, PI / 2, 0), radius=0.13, depth=5.2, vertices=6, parent=r)
    out['gapbeam'] = use(gb, beamm)
    gb.hide_render = True
    add('cube', '555B66', (4.7, -2.6, 1.8), scale=(0.16, 0.16, 3.6), size=1, parent=r)                             # the warning lamp on its post
    add('cube', '22252C', (4.7, -2.6, 3.9), scale=(0.9, 0.5, 0.9), size=1, parent=r)
    for j in range(4):
        add('cube', 'FF7A1A' if j % 2 else '15171C', (4.7 - 0.36 + j * 0.24, -2.86, 3.38), scale=(0.24, 0.03, 0.12), size=1, parent=r)
    out['warnm'] = wm = own_mat('warn', '3A1412', 0.3, 0.0)
    use(add('cylinder', '3A1412', (4.7, -2.88, 3.95), rot=(PI / 2, 0, 0), radius=0.3, depth=0.1, vertices=10, parent=r), wm)
    add('torus', '8E96A4', (4.7, -2.92, 3.95), rot=(PI / 2, 0, 0), major_radius=0.31, minor_radius=0.04, major_segments=10, minor_segments=4, parent=r, rough=0.3)
    for j in range(5):                                                                                            # a tool cart and drums against the outer wall
        add('cylinder', ('4A5A6E', '6E3A2A', '4A5A6E', '2C5A50', '6E3A2A')[j], (-9 + j * 4.6, -8.5 + 0.3 * (j % 2), 0.9), radius=0.62, depth=1.8, vertices=8, parent=r)
    out['smoke'] = [mov(add('ico_sphere', '8A8E96', (1.6, -0.4, -30 - j), radius=0.22, subdivisions=1, parent=r, alpha=0.8)) for j in range(4)]
    out['spark'] = [mov(add('cube', 'FFD060', (1.6, -0.4, -40 - j), scale=(0.07, 0.07, 0.07), size=1, parent=r, emit=30.0)) for j in range(4)]
    return out


# ---------------------------------------------------------------- the control room
def set_ctrl(r):
    out = dict(needles=[])
    add('cube', '2E3238', (0, 0, -0.1), scale=(20, 18, 0.2), size=1, parent=r)
    add('cube', '202228', (0, 0, 7.6), scale=(20, 18, 0.2), size=1, parent=r)
    add('cube', '56605E', (0, 8, 3.8), scale=(20, 0.3, 7.8), size=1, parent=r)
    add('cube', '4C5654', (0, -9, 3.8), scale=(20, 0.3, 7.8), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '4C5654', (sx * 10, 0, 3.8), scale=(0.3, 18, 7.8), size=1, parent=r)
    add('cube', '39424C', (0, 6.6, 1.1), scale=(15, 2.2, 2.2), size=1, parent=r)                                   # console
    add('cube', '2B323A', (0, 6.1, 2.5), rot=(0.5, 0, 0), scale=(15, 1.9, 0.2), size=1, parent=r)
    add('cube', '2B323A', (0, 7.5, 4.3), scale=(15, 0.5, 3.6), size=1, parent=r)                                   # instrument wall
    cols = ('3EC46A', 'FFB000', 'D8362A', 'E8ECF0', '3A9AE8')
    for j in range(22):
        for row in range(3):
            c = cols[int(rnd(j, row) * 5)]
            add('cube', c, (-6.8 + j * 0.65, 5.75 + row * 0.42, 2.34 + row * 0.23), rot=(0.5, 0, 0), scale=(0.24, 0.2, 0.1), size=1, parent=r,
                emit=3.5 if rnd(j, row + 9) > 0.45 else 0.3)
    for j, x in enumerate((-5.6, -3.6, -1.6)):                                                                    # three dials
        add('cylinder', 'E8E4D4', (x, 7.2, 3.6), rot=(PI / 2, 0, 0), radius=0.75, depth=0.08, vertices=14, parent=r, rough=0.3, emit=0.5)
        add('torus', '15171C', (x, 7.14, 3.6), rot=(PI / 2, 0, 0), major_radius=0.76, minor_radius=0.06, major_segments=14, minor_segments=4, parent=r)
        n = mov(empty((x, 7.1, 3.25), r))
        add('cube', 'D8362A', (0, 0, 0.32), scale=(0.06, 0.03, 0.66), size=1, parent=n, emit=1.0)
        out['needles'].append(n)
    add('torus', '2E8A5A', (3.4, 7.2, 4.3), rot=(PI / 2, 0, 0), major_radius=1.7, minor_radius=0.09, major_segments=24, minor_segments=4, parent=r, emit=2.5)   # ring diagram
    out['dotpiv'] = dp = mov(empty((3.4, 7.1, 4.3), r))
    add('ico_sphere', 'D6E6FF', (1.7, 0, 0), radius=0.2, subdivisions=1, parent=dp, emit=40.0)
    out['onm'] = om = own_mat('beamon', '3EC46A', 0.4, 14.0)
    use(add('cylinder', '3EC46A', (6.3, 7.2, 4.9), rot=(PI / 2, 0, 0), radius=0.42, depth=0.08, vertices=10, parent=r), om)
    add('cube', '15171C', (6.3, 7.22, 3.7), scale=(1.1, 0.06, 1.0), size=1, parent=r)
    for j in range(3):
        add('cube', '3A9AE8', (6.3, 7.17, 3.4 + j * 0.3), scale=(0.3 + 0.25 * rnd(j, 4), 0.03, 0.14), size=1, parent=r, emit=3.0)
    add('cylinder', 'F0ECDC', (-8.2, 7.82, 5.6), rot=(PI / 2, 0, 0), radius=0.95, depth=0.08, vertices=16, parent=r, rough=0.4, emit=0.6)   # wall clock
    add('torus', '15171C', (-8.2, 7.76, 5.6), rot=(PI / 2, 0, 0), major_radius=0.96, minor_radius=0.07, major_segments=16, minor_segments=4, parent=r)
    for j in range(12):
        a = j * PI / 6
        add('cube', '15171C', (-8.2 + 0.8 * math.sin(a), 7.75, 5.6 + 0.8 * math.cos(a)), rot=(0, -a, 0), scale=(0.05, 0.03, 0.14), size=1, parent=r)
    out['hands'] = []
    for ln, w in ((0.5, 0.09), (0.74, 0.06)):
        hd = mov(empty((-8.2, 7.72, 5.6), r))
        add('cube', '15171C', (0, 0, ln / 2), scale=(w, 0.03, ln), size=1, parent=hd)
        out['hands'].append(hd)
    for x in (-3.6, 3.0):                                                                                         # chairs
        add('cube', '6A3A2A', (x, 3.6, 1.0), scale=(1.5, 1.5, 0.2), size=1, parent=r)
        add('cube', '6A3A2A', (x, 2.9, 2.0), scale=(1.5, 0.16, 1.8), size=1, parent=r)
        add('cylinder', '22252C', (x, 3.6, 0.45), radius=0.14, depth=0.9, vertices=6, parent=r)
    add('cube', '39424C', (8.4, 0, 2.6), scale=(2.4, 6, 5.2), size=1, parent=r)                                    # a relay cabinet with reels
    for j in range(2):
        add('cylinder', 'B9C0CA', (7.18, -1.3 + j * 2.6, 4.0), rot=(0, PI / 2, 0), radius=0.8, depth=0.06, vertices=12, parent=r, rough=0.3)
    add('cube', 'FFF0D2', (0, 2, 7.45), scale=(6, 0.8, 0.1), size=1, parent=r, emit=5.0)
    light((0, 2, 6.9), 1500, 'FFE8C8', kind='POINT', parent=r)
    light((-3, 4.8, 3.6), 250, '9AD8FF', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- the clinic room
def set_clinic(r):
    out = {}
    add('cube', '7E8E88', (0, 0, -0.1), scale=(16, 16, 0.2), size=1, parent=r)
    add('cube', 'D8DCD4', (0, 0, 7.6), scale=(16, 16, 0.2), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '9FB0AA', (sx * 8, 0, 3.8), scale=(0.3, 16, 7.8), size=1, parent=r)
    add('cube', '9FB0AA', (0, -8, 3.8), scale=(16, 0.3, 7.8), size=1, parent=r)
    for x, w in ((-5.4, 5.2), (5.4, 5.2)):                                                                        # back wall around the window
        add('cube', '9FB0AA', (x, 8, 3.8), scale=(w, 0.3, 7.8), size=1, parent=r)
    add('cube', '9FB0AA', (0, 8, 1.2), scale=(5.6, 0.3, 2.4), size=1, parent=r)
    add('cube', '9FB0AA', (0, 8, 6.9), scale=(5.6, 0.3, 1.6), size=1, parent=r)
    out['panem'] = pm = own_mat('clinicpane', 'BFD8FF', 1.0, 3.0)
    use(add('cube', 'BFD8FF', (0, 8.3, 4.25), scale=(5.6, 0.05, 3.7), size=1, parent=r), pm)
    for x in (-2.8, 0, 2.8):
        add('cube', 'F0F0EA', (x, 7.86, 4.25), scale=(0.16, 0.12, 3.7), size=1, parent=r)
    for z in (2.4, 4.25, 6.1):
        add('cube', 'F0F0EA', (0, 7.86, z), scale=(5.7, 0.12, 0.16), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '9DB4A8', (sx * 3.5, 7.7, 4.4), scale=(1.1, 0.12, 4.4), size=1, parent=r)                      # curtains
    add('cube', '7A8A84', (0, 0, 1.3), scale=(16.2, 16.2, 0.12), size=1, parent=r, alpha=1.0) if False else None
    for sx in (-1, 1):                                                                                            # the bed
        for y in (-1.3, 3.7):
            add('cylinder', 'E8ECEC', (sx * 1.6, y, 0.9), radius=0.09, depth=1.8, vertices=6, parent=r, rough=0.3)
    add('cube', 'E8ECEC', (0, 1.2, 1.25), scale=(3.4, 5.2, 0.14), size=1, parent=r, rough=0.4)
    add('cube', 'F4F2EA', (0, 1.2, 1.5), scale=(3.2, 5.0, 0.36), size=1, parent=r)
    add('cube', 'FBFAF4', (0, 2.75, 1.78), scale=(2.3, 1.5, 0.32), size=1, parent=r)                               # pillow
    add('cube', '6E8A80', (0, -0.1, 2.0), scale=(3.3, 2.4, 0.75), size=1, parent=r)                                # blanket
    add('cube', 'F4F2EA', (0, 1.0, 2.26), scale=(3.3, 0.5, 0.24), size=1, parent=r)                                # the sheet folded over it
    for x in (-1.6, 1.6):
        add('cylinder', 'E8ECEC', (x, 3.82, 2.3), radius=0.07, depth=2.6, vertices=6, parent=r, rough=0.3)
    for z in (2.4, 3.0, 3.55):
        add('cylinder', 'E8ECEC', (0, 3.82, z), rot=(0, PI / 2, 0), radius=0.06, depth=3.2, vertices=6, parent=r, rough=0.3)
    add('cylinder', 'B9C0CA', (2.6, 3.0, 2.6), radius=0.06, depth=5.2, vertices=6, parent=r, rough=0.3)             # drip stand
    add('cylinder', 'B9C0CA', (2.6, 3.0, 0.08), radius=0.6, depth=0.1, vertices=8, parent=r, rough=0.3)
    add('cube', 'B9C0CA', (2.3, 3.0, 5.1), scale=(0.8, 0.06, 0.06), size=1, parent=r)
    add('cube', 'CFE8F4', (2.05, 3.0, 4.55), scale=(0.5, 0.2, 0.9), size=1, parent=r, rough=0.2, emit=0.6)
    out['drop'] = mov(add('ico_sphere', 'CFE8F4', (2.05, 3.0, 4.0), radius=0.06, subdivisions=1, parent=r, emit=3.0))
    add('cube', 'E8E4D4', (-2.9, 3.0, 1.0), scale=(1.5, 1.5, 2.0), size=1, parent=r)                               # bedside table
    add('cylinder', 'CFE4EA', (-2.9, 2.8, 2.25), radius=0.18, depth=0.5, vertices=8, parent=r, rough=0.1, emit=0.3)
    add('cube', '8A5A3A', (0, -1.42, 1.9), rot=(0.25, 0, 0), scale=(1.1, 0.06, 1.4), size=1, parent=r)             # the chart at the foot
    add('cube', 'F4F2EA', (0, -1.47, 1.92), rot=(0.25, 0, 0), scale=(0.9, 0.04, 1.1), size=1, parent=r)
    add('cube', '5A6A66', (5.6, 5.2, 1.0), scale=(1.5, 1.5, 0.18), size=1, parent=r)                               # a chair
    add('cube', '5A6A66', (5.6, 5.9, 2.0), scale=(1.5, 0.16, 1.8), size=1, parent=r)
    out['win'] = w = light((0, 7.2, 4.4), 650, 'CFE0FF', 3.4, parent=r)
    w.rotation_euler = (PI / 2, 0, 0)
    out['top'] = light((0, 0, 7.0), 380, 'F0F4FF', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- the institute yard at night, in snow
def birch(r, x, y, h, lean):
    t = empty((x, y, 0), r, (lean, lean * 0.6, 0))
    add('cylinder', 'E4E6E0', (0, 0, h / 2), radius=0.22, depth=h, vertices=6, parent=t)
    for j in range(int(h / 1.4)):
        add('cylinder', '22242A', (0, 0, 0.9 + j * 1.4 + 0.3 * rnd(j, x)), radius=0.235, depth=0.14, vertices=6, parent=t)
    for j in range(5):
        a = rnd(j, y) * 6.28
        add('cylinder', '3A3C44', (0.9 * math.cos(a), 0.9 * math.sin(a), h * (0.55 + 0.1 * j)), rot=(0.9 * math.sin(a), -0.9 * math.cos(a), 0),
            radius=0.06, depth=2.6, vertices=4, parent=t)


def set_yard(r):
    out = {}
    add('cube', 'B8C6DC', (0, 40, -0.2), scale=(400, 400, 0.4), size=1, parent=r)                                  # snow
    add('cube', '4A5262', (0, 12, 0.02), scale=(4.2, 26, 0.05), size=1, parent=r)                                  # the trodden path
    add('cube', '343A46', (0, 32, 6), scale=(90, 12, 12), size=1, parent=r)                                        # the long institute block
    add('cube', 'D4DEEE', (0, 32, 12.2), scale=(91, 12.6, 0.5), size=1, parent=r)                                  # snow on its roof
    for j in range(20):
        for row in range(2):
            lit = rnd(j, row) > 0.62
            add('cube', 'FFD890' if lit else '1A2030', (-42 + j * 4.4, 25.95, 4.2 + row * 4.2), scale=(2.2, 0.1, 2.2), size=1, parent=r,
                emit=2.2 if lit else 0.0)
    add('cube', '2A2F3A', (0, 25.4, 3.3), scale=(7.0, 1.6, 6.6), size=1, parent=r)                                 # the entrance block
    add('cube', 'D4DEEE', (0, 25.2, 6.75), scale=(7.6, 2.2, 0.35), size=1, parent=r)
    for j in range(9):                                                                                            # striped frame round the steel door
        c = 'FF7A1A' if j % 2 else '15171C'
        add('cube', c, (-2.05, 24.56, 0.3 + j * 0.56), scale=(0.3, 0.1, 0.56), size=1, parent=r)
        add('cube', c, (2.05, 24.56, 0.3 + j * 0.56), scale=(0.3, 0.1, 0.56), size=1, parent=r)
    for j in range(8):
        add('cube', 'FF7A1A' if j % 2 else '15171C', (-1.75 + j * 0.5, 24.56, 5.2), scale=(0.5, 0.1, 0.3), size=1, parent=r)
    add('cube', 'FFE2B0', (0, 25.0, 2.5), scale=(3.8, 0.1, 5.0), size=1, parent=r, emit=6.0)                       # the lit hall behind the door
    out['doors'] = []
    for s in (-1, 1):
        hinge = mov(empty((s * 1.9, 24.6, 0), r))
        add('cube', '5A6470', (-s * 0.95, 0, 2.5), scale=(1.9, 0.14, 5.0), size=1, parent=hinge, rough=0.4)
        add('cube', 'B9C0CA', (-s * 1.6, -0.1, 2.5), scale=(0.1, 0.1, 0.8), size=1, parent=hinge, rough=0.3)
        out['doors'].append((s, hinge))
    out['doorl'] = light((0, 23.4, 4.6), 0, 'FFD9A8', kind='POINT', parent=r)
    add('cube', '6E7686', (0, 26.6, 5.8), scale=(0.9, 0.5, 0.5), size=1, parent=r)                                 # the lamp over the door
    light((0, 23.9, 5.6), 700, 'FFD9A8', kind='POINT', parent=r)
    for s in (-1, 1):                                                                                             # gate posts and a fence
        add('cube', '4E5664', (s * 4.6, 1.0, 2.0), scale=(1.0, 1.0, 4.0), size=1, parent=r)
        add('cube', 'D4DEEE', (s * 4.6, 1.0, 4.1), scale=(1.2, 1.2, 0.25), size=1, parent=r)
        for j in range(16):
            add('cube', '2A2F3A', (s * (5.6 + j * 1.1), 1.0, 1.6), scale=(0.12, 0.12, 3.2), size=1, parent=r)
        add('cube', '2A2F3A', (s * 14, 1.0, 2.9), scale=(17.5, 0.12, 0.14), size=1, parent=r)
        add('cube', '2A2F3A', (s * 14, 1.0, 0.7), scale=(17.5, 0.12, 0.14), size=1, parent=r)
    add('cylinder', '2A2F3A', (-6.4, 7, 3.4), radius=0.14, depth=6.8, vertices=6, parent=r)                         # lamp post
    add('cube', '2A2F3A', (-5.8, 7, 6.7), scale=(1.4, 0.14, 0.14), size=1, parent=r)
    add('cone', 'FFE2B0', (-5.2, 7, 6.5), radius1=0.5, radius2=0.2, depth=0.4, vertices=8, parent=r, emit=14.0)
    out['lamp'] = light((-5.2, 7, 6.1), 2600, 'FFD9A8', kind='POINT', parent=r)
    for j, (x, y) in enumerate(((9, 6), (13, 14), (-11, 12), (-15, 4), (8, 19), (-9, 20), (18, 8), (-20, 15), (22, 20), (11, -4), (-12, -5))):
        birch(r, x, y, 9 + 4 * rnd(j, 3), 0.08 * (rnd(j, 5) - 0.5))
    for j in range(7):                                                                                            # drifts
        add('ico_sphere', 'C8D4E8', (-24 + j * 8 + 3 * rnd(j, 1), 3 + 14 * rnd(j, 2), -0.3), scale=(3.5, 2.5, 0.8), radius=1, subdivisions=1, parent=r)
    return out


# ---------------------------------------------------------------- the study
def set_study(r):
    out = {}
    add('cube', '5A4030', (0, 0, -0.1), scale=(16, 16, 0.2), size=1, parent=r)
    add('cube', 'CFC8B4', (0, 0, 7.6), scale=(16, 16, 0.2), size=1, parent=r)
    add('cube', 'A8A08A', (0, 4.2, 3.8), scale=(16, 0.3, 7.8), size=1, parent=r)
    add('cube', 'A8A08A', (0, -8, 3.8), scale=(16, 0.3, 7.8), size=1, parent=r)
    for sx in (-1, 1):
        add('cube', '9A927C', (sx * 8, 0, 3.8), scale=(0.3, 16, 7.8), size=1, parent=r)
    add('cube', '6A4A32', (0, 4.0, 4.3), scale=(8.4, 0.12, 4.0), size=1, parent=r)                                 # blackboard: chalk strokes, no legible writing
    add('cube', '1F3A32', (0, 3.93, 4.3), scale=(8.0, 0.06, 3.6), size=1, parent=r)
    for row in range(5):
        x = -3.5
        j = 0
        while x < 3.3:
            w = 0.25 + 0.7 * rnd(row, j)
            add('cube', 'E8ECE4', (x + w / 2, 3.88, 5.7 - row * 0.62), rot=(0, 0.12 * (rnd(j, row) - 0.5), 0), scale=(w, 0.02, 0.06 + 0.1 * rnd(j, row + 3)),
                size=1, parent=r, emit=0.5)
            x += w + 0.16 + 0.3 * rnd(row + 7, j)
            j += 1
    add('torus', 'E8ECE4', (2.3, 3.88, 3.3), rot=(PI / 2, 0, 0), major_radius=0.6, minor_radius=0.03, major_segments=20, minor_segments=3, parent=r, emit=0.5)
    add('cube', 'E8ECE4', (2.3, 3.88, 3.3), rot=(0, 0.5, 0), scale=(1.7, 0.02, 0.04), size=1, parent=r, emit=0.5)
    add('cube', '6A4A32', (0, -1.6, 1.5), scale=(6.4, 2.6, 0.2), size=1, parent=r)                                 # desk
    for sx in (-1, 1):
        add('cube', '5A3E2A', (sx * 2.9, -1.6, 0.7), scale=(0.3, 2.3, 1.4), size=1, parent=r)
    add('cube', '5A3E2A', (0, -2.7, 0.9), scale=(5.8, 0.1, 1.0), size=1, parent=r)
    add('cube', '6A3A2A', (0, 0.1, 1.0), scale=(1.5, 1.5, 0.2), size=1, parent=r)                                  # chair
    add('cube', '6A3A2A', (0, 0.8, 2.1), scale=(1.5, 0.16, 2.0), size=1, parent=r)
    add('cylinder', '22252C', (-2.3, -1.1, 1.65), radius=0.4, depth=0.1, vertices=8, parent=r)                      # desk lamp
    add('cylinder', '22252C', (-2.3, -1.1, 2.3), radius=0.05, depth=1.3, vertices=6, parent=r)
    add('cone', '2E8A5A', (-2.1, -1.2, 3.0), rot=(0.3, 0.3, 0), radius1=0.55, radius2=0.2, depth=0.45, vertices=8, parent=r, emit=1.0)
    out['lamp'] = light((-2.0, -1.3, 2.7), 500, 'FFE0B0', kind='POINT', parent=r)
    for j in range(5):                                                                                            # a pile of paper
        add('cube', 'F4F0E2', (1.6 + 0.05 * rnd(j, 1), -1.5 + 0.05 * rnd(j, 2), 1.63 + j * 0.05), rot=(0, 0, 0.2 * (rnd(j, 3) - 0.5)), scale=(1.2, 1.6, 0.04),
            size=1, parent=r)
    add('cube', 'F4F0E2', (0, -1.7, 1.62), scale=(1.1, 1.5, 0.03), size=1, parent=r)                               # the page he is writing on
    out['thesis'] = th = mov(empty((1.6, -1.5, -40), r))
    add('cube', '7A2A2E', (0, 0, 0.16), scale=(1.25, 1.65, 0.32), size=1, parent=th, rough=0.5)
    add('cube', 'F4F0E2', (0.02, 0, 0.16), scale=(1.24, 1.55, 0.24), size=1, parent=th)
    add('cube', 'C89A3A', (0, 0, 0.325), scale=(0.7, 0.3, 0.01), size=1, parent=th, rough=0.3, emit=0.8)
    add('cube', '4A3222', (6.6, 2.6, 3.4), scale=(2.4, 2.6, 6.8), size=1, parent=r)                                # bookshelf
    for row in range(4):
        x = 0.0
        j = 0
        while x < 2.3:
            w = 0.16 + 0.2 * rnd(row, j + 11)
            add('cube', ('7A2A2E', '2B5FA8', '2C5A50', 'C9A227', '39404E', 'B8683A')[int(rnd(j, row) * 6)], (5.38, 1.45 + x + w / 2, 1.5 + row * 1.5),
                scale=(0.1, w, 0.95 + 0.25 * rnd(j, row + 2)), size=1, parent=r)
            x += w + 0.02
            j += 1
    out['paneL'] = w = light((-7.2, -2, 4.6), 0, 'DCEBFF', 3.6, parent=r)                                          # daylight from a window on the left wall
    w.rotation_euler = (0, -PI / 2, 0)
    add('cube', 'CFE4FF', (-7.82, -2, 4.6), scale=(0.06, 4.4, 3.6), size=1, parent=r, emit=2.0)
    add('cube', 'F0F0EA', (-7.78, -2, 4.6), scale=(0.1, 0.14, 3.6), size=1, parent=r)
    add('cube', 'F0F0EA', (-7.78, -2, 4.6), scale=(0.1, 4.4, 0.14), size=1, parent=r)
    out['top'] = light((0, -1, 7.0), 0, 'FFF0DC', kind='POINT', parent=r)
    return out


# ---------------------------------------------------------------- a schematic head for the beam's path
def set_xray(r):
    out = {}
    wire = []
    wire.append(add('ico_sphere', '49C8FF', (0, 0.3, 4.6), scale=(2.6, 3.05, 3.2), radius=1, subdivisions=2, parent=r, emit=5.0))
    wire.append(add('ico_sphere', '49C8FF', (0, -0.9, 2.55), scale=(1.9, 2.05, 1.6), radius=1, subdivisions=2, parent=r, emit=5.0))     # jaw
    wire.append(add('cone', '49C8FF', (0, -3.5, 4.0), rot=(PI / 2 + 0.3, 0, 0), radius1=0.85, radius2=0.1, depth=1.9, vertices=5, parent=r, emit=5.0))   # nose
    wire.append(add('cylinder', '49C8FF', (0, 0.5, 0.7), radius=1.2, depth=2.2, vertices=8, parent=r, emit=5.0))
    wire.append(add('cube', '49C8FF', (0, 0.5, -1.0), scale=(9.0, 3.2, 1.8), size=1, parent=r, emit=5.0))                              # shoulders                     # neck
    for sx in (-1, 1):
        wire.append(add('ico_sphere', '49C8FF', (sx * 2.85, 0.5, 4.3), scale=(0.3, 0.6, 0.9), radius=1, subdivisions=1, parent=r, emit=5.0))   # ears
    for o in wire:
        m = o.modifiers.new('wire', 'WIREFRAME')
        m.thickness = 0.022
    for s in (-1, 1):
        add('cube', 'CFF0FF', (s * 1.05, -2.98, 4.9), scale=(0.8, 0.05, 0.24), size=1, parent=r, emit=6.0)                           # eyes, as two bars
    add('ico_sphere', '2A4E86', (0, 0.9, 5.4), scale=(1.8, 2.2, 1.6), radius=1, subdivisions=1, parent=r, emit=0.35)                   # the brain, as a plain solid
    p0, p1, p2, p3 = (-0.25, 13.0, 5.05), (-0.25, 3.35, 5.05), (0.55, -2.95, 4.05), (1.6, -11.0, 2.8)
    out['pts'] = (p0, p1, p2, p3)
    out['line'] = []
    for j, (a, b) in enumerate(((p0, p1), (p1, p2), (p2, p3))):
        m = own_mat('xline%d' % j, 'FFE2B0' if j == 1 else 'D6E6FF', 0.4, 40.0)
        o = use(add('cylinder', 'D6E6FF', (0, 0, 0), radius=0.5, depth=1.0, vertices=6, parent=r), m)
        seg(o, a, b, 0.11 if j != 1 else 0.14)
        out['line'].append((mov(o), m, a, b))
    out['dot'] = mov(add('ico_sphere', 'FFFFFF', (0, 0, -50), radius=0.34, subdivisions=1, parent=r, emit=80.0))
    out['dotl'] = light((0, 0, -50), 0, 'CFE0FF', kind='POINT', parent=r)
    for j in range(-8, 9):                                                                                        # a faint floor grid
        add('cube', '1E4A7A', (j * 2.5, 0, -1.95), scale=(0.04, 44, 0.04), size=1, parent=r, emit=1.6)
        add('cube', '1E4A7A', (0, j * 2.5, -1.95), scale=(44, 0.04, 0.04), size=1, parent=r, emit=1.6)
    light((6, -8, 9), 500, '9AD8FF', kind='POINT', parent=r)
    return out


def seg(o, a, b, w):
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


# ---------------------------------------------------------------- cast
def man_head(skin, hair, kind):
    """A plain low-poly head. His own left is +x (the right of the picture when he faces the camera)."""
    def fn(head):
        add('ico_sphere', skin, (0, 0, 0.02), scale=(0.92, 1, 1.1), radius=0.29, subdivisions=1, parent=head)
        hairo = [add('ico_sphere', hair, (0, 0.05, 0.1), scale=(0.96, 1, 1.0), radius=0.3, subdivisions=1, parent=head)]
        if kind in ('bug', 'pat'):
            hairo.append(add('cube', hair, (-0.08, -0.2, 0.26), rot=(0.3, 0, 0.25), scale=(0.4, 0.14, 0.08), size=1, parent=head))    # a side parting
        eyes, brows = [], []
        for s in (-1, 1):
            eyes.append(add('cube', 'FFFFFF', (s * 0.105, -0.262, 0.04), scale=(0.1, 0.03, 0.075), size=1, parent=head, emit=0.6))
            add('cube', '1A222E', (s * 0.105, -0.28, 0.035), scale=(0.042, 0.02, 0.046), size=1, parent=head)
            brows.append(add('cube', hair, (s * 0.105, -0.27, 0.125), rot=(0, s * 0.12, 0), scale=(0.13, 0.03, 0.026), size=1, parent=head))
        add('cube', 'C08E6E', (0, -0.285, -0.04), scale=(0.05, 0.05, 0.08), size=1, parent=head)
        jaw = empty((0, -0.2, -0.13), head)
        add('cube', '6A2A2E', (0, -0.07, 0.0), scale=(0.11, 0.03, 0.03), size=1, parent=jaw)
        out = dict(jaw=jaw, eyes=eyes, brows=brows)
        if kind in ('bug', 'pat'):
            out['swell'] = [add('ico_sphere', 'D4826E', (0.2, -0.13, -0.05), scale=(0.9, 1.0, 1.2), radius=0.24, subdivisions=1, parent=head)]
            out['band'] = [add('cylinder', 'F4F2EA', (0, 0.02, 0.15), rot=(0.1, 0, 0), radius=0.315, depth=0.2, vertices=8, parent=head),
                           add('cube', 'F4F2EA', (0.02, 0.3, 0.1), scale=(0.2, 0.06, 0.2), size=1, parent=head)]
            vis(out['swell'], False)
            vis(out['band'], kind == 'pat')
        if kind == 'doc':
            add('cylinder', 'F4F2EA', (0, 0.02, 0.27), radius=0.3, depth=0.22, vertices=8, parent=head)
            for s in (-1, 1):
                add('torus', '22252C', (s * 0.105, -0.3, 0.04), rot=(PI / 2, 0, 0), major_radius=0.085, minor_radius=0.012, major_segments=8, minor_segments=3, parent=head)
            add('cube', '8A8E96', (0, -0.27, -0.14), scale=(0.2, 0.04, 0.08), size=1, parent=head)                 # grey moustache
        if kind == 'op':
            add('cube', '22252C', (0, 0.02, 0.33), scale=(0.66, 0.08, 0.05), size=1, parent=head)                  # a headset band
            for s in (-1, 1):
                add('cylinder', '22252C', (s * 0.29, 0.02, 0.03), rot=(0, PI / 2, 0), radius=0.1, depth=0.06, vertices=8, parent=head)
        return out
    return fn


def build():
    sc = bpy.context.scene
    _MOV.clear()
    S = dict(colls={})
    for name, fn in (('ring', set_ring), ('ctrl', set_ctrl), ('clinic', set_clinic), ('yard', set_yard), ('study', set_study), ('xray', set_xray)):
        S['colls'][name], out = group(name, fn)
        S[name] = out
    S['rook'] = K.Rig(ROOK, K.rook_head, coat=True)
    S['bug'] = K.Rig(BUG, man_head(SKIN, '2A2420', 'bug'))
    add('cone', COAT, (0, 0, -0.3), radius1=0.4, radius2=0.33, depth=0.75, vertices=8, parent=S['bug'].body)       # the hem of his lab coat
    add('cube', '8A96A8', (0, -0.3, 0.75), scale=(0.3, 0.04, 0.5), size=1, parent=S['bug'].body)                   # shirt and tie under it
    add('cube', '39404E', (0, -0.32, 0.7), scale=(0.08, 0.03, 0.44), size=1, parent=S['bug'].body)
    S['pat'] = K.Rig(PAT, man_head(SKIN, '2A2420', 'pat'))
    S['doc'] = K.Rig(DOC, man_head('D9AE8E', '8A8E96', 'doc'))
    add('cone', 'EEF0EA', (0, 0, -0.3), radius1=0.42, radius2=0.33, depth=0.8, vertices=8, parent=S['doc'].body)
    S['op'] = K.Rig(OPR, man_head('D6A888', '6A4A32', 'op'))
    S['cast'] = [S['rook'], S['bug'], S['pat'], S['doc'], S['op']]
    S['fea'] = [mov(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(3)]
    S['coin'] = mov(add('cylinder', 'FFC233', FAR, radius=0.11, depth=0.03, vertices=8, rough=0.25, emit=1.2))
    S['clip'] = cb = mov(empty(FAR))                                                                               # a clipboard
    add('cube', '8A5A3A', (0, 0, 0), scale=(0.5, 0.04, 0.7), size=1, parent=cb)
    add('cube', 'F4F2EA', (0, -0.03, -0.02), scale=(0.42, 0.02, 0.58), size=1, parent=cb)
    S['nut'] = nt = mov(empty(FAR))                                                                                # the shiny thing: a steel nut from the tunnel
    add('torus', 'E8ECF4', (0, 0, 0), major_radius=0.13, minor_radius=0.06, major_segments=6, minor_segments=4, parent=nt, rough=0.15, emit=2.2)
    S['glow'] = light(FAR, 0, 'CFE0FF', kind='POINT')
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 2000
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


def show(S, name):
    for n, c in S['colls'].items():
        c.hide_render = n != name
    return lambda x, y, z: at(name, x, y, z)


def cam(S, pos, look, lens=50, roll=0.0, fill=1.0, fcol='DCE4F4'):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens
    S['cam'].rotation_euler = (0, 0, roll)
    dx, dy, dz = look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]
    d = math.sqrt(dx * dx + dy * dy + dz * dz)
    h = math.hypot(dx, dy) + 1e-6
    S['fill'].location = (pos[0] - dy / h * 0.3 * d, pos[1] + dx / h * 0.3 * d, pos[2] + 0.3 * d)
    S['fill'].data.energy = S['fillk'] * fill * min(d, 14) ** 2
    S['fill'].data.size = max(2.0, 0.3 * d)
    S['fill'].data.color = K.hexc(fcol)[:3]


def reset(S):
    for rig in S['cast']:
        rig.root.parent = None
        rig.place(FAR)
        rig.apply(P())
        rig.root.scale = (1, 1, 1)
    for o, par, loc, rot, scl in _MOV:
        o.parent = par
        o.location, o.rotation_euler, o.scale = loc, rot, scl
    R = S['ring']
    for a, b in R['beam']:
        b.hide_render = True
    R['gapbeam'].hide_render = True
    for l in R['ring_lights']:
        l.data.energy = 1500
    tint(R['faultm'], '3EC46A', 6.0)
    tint(R['warnm'], '3A1412', 0.0)
    tint(S['ctrl']['onm'], '3EC46A', 14.0)
    tint(S['clinic']['panem'], 'BFD8FF', 3.0)
    S['clinic']['win'].data.energy = 650
    S['clinic']['win'].data.color = K.hexc('CFE0FF')[:3]
    S['clinic']['top'].data.energy = 380
    S['yard']['doorl'].data.energy = 0
    S['yard']['lamp'].data.energy = 2600
    S['study']['lamp'].data.energy = 500
    S['study']['paneL'].data.energy = 0
    S['study']['top'].data.energy = 0
    for o, m, a, b in S['xray']['line']:
        tint(m, 'FFE2B0' if m.name.endswith('1') else 'D6E6FF', 40.0)
    S['xray']['dotl'].data.energy = 0
    for who in ('bug', 'pat'):
        vis(S[who].extra['swell'], False)
    vis(S['bug'].extra['band'], False)
    vis(S['pat'].extra['band'], True)
    S['glow'].location = FAR
    S['glow'].data.energy = 0
    S['glow'].data.color = K.hexc('CFE0FF')[:3]
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S['fillk'] = 0.0
    S['face'] = dict(rook='calm', bug='calm', pat='calm', doc='calm', op='calm')
    S['left'] = dict(bug='ok', pat='ok')
    S['hat_tip'] = 0.0
    S['hat_off'] = 0.0
    S['jaw'] = dict(bug=0.0, pat=0.0, doc=0.0, op=0.0)
    S['cam'].rotation_euler = (0, 0, 0)
    sky(S, '000000', 1.0)


def finish(S, t):
    """Faces, blinking and beak lip sync after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['face']['rook']
    blink = (t * 0.41) % 1 < 0.035
    ez = dict(calm=0.07, deadpan=0.05, shocked=0.13, sad=0.055, warm=0.06, shut=0.012).get(e, 0.07)
    tilt = dict(deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], ease(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + (0.12 if e == 'deadpan' else 0.0) + tip * 0.35, 1.35, off), lerp(0.07, 0.0, off), 0)
    r['hat'].location = (0.0, lerp(0.0, -0.5, off), lerp(0.27 + (0.2 if e == 'shocked' else 0.0) + tip * 0.1, -0.92, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, who in enumerate(('bug', 'pat', 'doc', 'op')):
        x = S[who].extra
        k = dict(calm=1.0, wide=1.7, shut=0.08, tired=0.5, warm=0.85, squint=0.6).get(S['face'][who], 1.0)
        bl = (t * 0.33 + 0.27 * j) % 1 < 0.03
        left = S['left'].get(who, 'ok')
        for i, ey in enumerate(x['eyes']):
            kk = 0.1 if bl else k
            if i == 1 and left == 'swollen':
                kk = 0.12
            if i == 1 and left == 'still':                 # the paralysed side does not blink or widen
                kk = 0.8
            ey.scale = (0.1, 0.03, 0.075 * kk)
        for i, s in enumerate((-1, 1)):
            lift = 0.03 if S['face'][who] == 'wide' else 0.0
            if i == 1 and left != 'ok':
                lift = -0.012
            x['brows'][i].location.z = 0.125 + lift
        x['jaw'].rotation_euler = (S['jaw'][who], 0, 0)


# ---------------------------------------------------------------- helpers for the shots
def env(S, name, skyc='000000', sun=0.0, sunc='FFFFFF', sdir=(-0.4, -0.6, 0.7), fk=2.6, skyk=1.0):
    A = show(S, name)
    sky(S, skyc, skyk)
    S['suntgt'].location = A(0, 0, 0)
    S['sun'].location = A(sdir[0] * 400, sdir[1] * 400, sdir[2] * 400)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(sunc)[:3]
    S['fillk'] = fk
    return A


def feather(S, pos, lt, t0=0.0, n=2):
    for i in range(n):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def hat_hold(**over):
    d = dict(aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.22, 0.0))
    d.update(over)
    return P('stand', **d)


LEAN = P('stand', lean=0.75, aL=(1.25, 0.15, 0.5), aR=(1.4, 0.15, 0.35), head=(-0.6, 0.0), lL=(0.95, 0.15), lR=(0.5, 0.05))
WORK = P('stand', lean=0.5, aL=(1.3, 0.05, 0.6), aR=(1.4, 0.05, 0.5), head=(-0.15, 0.0), lL=(0.5, 0.0), lR=(0.5, 0.0))
ALARM = P('stand', aL=(0.7, 1.15, 1.5, -0.7), aR=(0.7, 1.15, 1.5, -0.7), head=(-0.15, 0.0), lean=-0.12, lL=(-0.12, 0.0), lR=(-0.12, 0.0))
BUGPOS = (-1.1, 0.0, 0.0)                              # where he stands in the gap, facing down the beam line


def ring(S, dim=1.0, fk=2.2):
    A = env(S, 'ring', fk=fk)
    for l in S['ring']['ring_lights']:
        l.data.energy = 1500 * dim
    return A


def beam_to(S, A, front, power=1.0):
    """Light the beam up to the angle front (the gap is at 0) and carry a glow with its head."""
    R = S['ring']
    for a, b in R['beam']:
        b.hide_render = not (a < front and abs(a) > 0.01)
    R['gapbeam'].hide_render = front < 0.02
    S['glow'].location = A(*arc(front, 0.8, BZ + 0.9))
    S['glow'].data.energy = 9000 * power


def bug_in_gap(S, A, k=1.0, face='calm', nod=0.0):
    S['bug'].place(A(*BUGPOS), PI / 2)
    S['bug'].apply(blend(P('stand', lean=0.25, aL=(0.4, 0.1, 0.4), aR=(0.5, 0.1, 0.4)), P('stand', **{**LEAN, 'head': (-0.6 + nod, 0.0)}), k))
    S['face']['bug'] = face


# ---------------------------------------------------------------- the beam
def beam_fire(S, k, t, lt):
    A = ring(S, 0.4, fk=1.4)
    if S['prm'].get('v') == 2:                                   # riding just above the pipe behind the beam's head
        front = lerp(-0.62, 0.0, k)
        beam_to(S, A, front, 1.4)
        bug_in_gap(S, A)
        cam(S, A(*arc(front - 0.3, 2.4, 3.7)), A(*arc(front + 0.03, 0.0, 2.0)), 24, roll=0.04 * math.sin(lt * 20), fcol='BFD4FF')
        return
    front = lerp(-0.5, 0.0, min(1.0, k / 0.8))
    beam_to(S, A, front, 1.2)
    bug_in_gap(S, A)
    cam(S, A(*arc(lerp(0.05, 0.04, k), lerp(3.6, 3.2, k), lerp(1.3, 1.6, k))), A(*arc(-0.06, 0.0, 2.2)), 22, roll=-0.06, fcol='BFD4FF')


def flash_side(S, k, t, lt):
    A = ring(S, 0.3, fk=1.6)
    hit = ease((lt - 0.22) / 0.1)
    beam_to(S, A, lerp(-0.4, 0.5, min(1.0, lt / 0.3)), 0.4 + 3.0 * hit)
    S['glow'].location = A(0.4, -1.8, 3.2)
    S['glow'].data.energy = 1200 + 4000 * hit * (0.6 + 0.4 * math.sin(lt * 30))
    bug_in_gap(S, A, face='wide' if hit > 0.3 else 'calm', nod=0.12 * hit)
    cam(S, A(lerp(1.4, 0.6, k), lerp(-8.0, -6.6, k), 2.5), A(-0.2, 0, 2.0), 38, roll=0.03 * hit * math.sin(lt * 25), fcol='E8F0FF')


def bug_flash(S, k, t, lt):
    A = ring(S, 0.3, fk=2.0)
    v2 = S['prm'].get('v') == 2
    hit = 1.0 if v2 else ease((lt - 0.12) / 0.1)
    beam_to(S, A, 0.5, 1.0)
    S['glow'].location = A(1.3, -1.1, 2.7)
    S['glow'].data.energy = 400 + 1100 * hit * (0.7 + 0.3 * math.sin(lt * 34))
    S['glow'].data.color = K.hexc('FFFFFF')[:3]
    bug_in_gap(S, A, face='wide' if hit > 0.3 else 'calm', nod=0.1 * hit)
    rp = (-2.7, 1.7, 0.0) if not v2 else (-2.3, 2.1, 0.0)
    S['rook'].place(A(*rp), facing(rp, (3.0, -1.8, 0)))
    S['rook'].apply(blend(P('stand', aL=(0.3, 0.2, 0.4), aR=(0.3, 0.2, 0.4)), P('stand', **{**ALARM, 'head': (0.1, 0.0)}), hit))
    S['face']['rook'] = 'shocked' if hit > 0.3 else 'deadpan'
    feather(S, A(rp[0] + 0.3, rp[1] - 0.3, 3.3), lt, 0.2)
    if v2:
        cam(S, A(lerp(1.7, 2.0, k), lerp(-1.5, -1.3, k), lerp(3.3, 3.0, k)), A(-0.7, 0.4, 2.5), 30, roll=0.05 * math.sin(lt * 22), fcol='FFFFFF')
    else:
        cam(S, A(lerp(3.2, 2.7, k), lerp(-2.0, -1.7, k), 2.2), A(-0.7, 0.4, 2.55), 30, roll=0.04 * hit * math.sin(lt * 22), fcol='FFFFFF')


def rook_flinch(S, k, t, lt):
    A = ring(S, 0.35, fk=2.6)
    beam_to(S, A, 0.5, 0.0)
    S['glow'].location = A(0.5, -1.2, 3.0)
    S['glow'].data.energy = 5000 * (0.4 + 0.6 * math.exp(-lt * 2.5))
    bug_in_gap(S, A, face='wide')
    rp = (1.2, -4.8, 0.0)
    S['rook'].place(A(rp[0] + 0.5 * ease(lt / 0.3), rp[1] - 0.6 * ease(lt / 0.3), 0), 0.35, pitch=-0.14 * ease(lt / 0.25))
    S['rook'].apply(blend(P('stand'), ALARM, lt / 0.12))
    S['face']['rook'] = 'shocked'
    feather(S, A(rp[0] + 0.4, rp[1] - 0.4, 3.4), lt, 0.05, 3)
    cam(S, A(lerp(2.6, 2.9, k), lerp(-9.0, -8.6, k), 2.3), A(1.5, -5.0, 2.75), 34, fcol='E0E8FF')


def head_xray(S, k, t, lt):
    A = env(S, 'xray', '02040A', fk=0.0)
    X = S['xray']
    p0, p1, p2, p3 = X['pts']
    v2 = S['prm'].get('v') == 2
    u = 1.0 if v2 else min(1.0, lt / 0.75)
    path = ((p0, p1, 0.0, 0.45), (p1, p2, 0.45, 0.7), (p2, p3, 0.7, 1.0))
    pos = p3
    for (o, m, a, b), (_, _, u0, u1) in zip(X['line'], path):
        f = max(0.0, min(1.0, (u - u0) / (u1 - u0)))
        if f <= 0:
            o.location = (0, 0, -60)
            continue
        e = tuple(a[i] + (b[i] - a[i]) * f for i in range(3))
        seg(o, a, e, 0.11 if m.name.endswith('1') is False else 0.15)
        if f < 1:
            pos = e
        tint(m, 'FFE2B0' if m.name.endswith('1') else 'D6E6FF', 40.0 * (1.0 if not v2 else 0.55 + 0.45 * math.sin(lt * 9)))
    if u < 1:
        X['dot'].location = pos
        X['dotl'].location = pos
        X['dotl'].data.energy = 9000
    if v2:
        a = lerp(-0.9, -0.3, k)
        cam(S, A(19 * math.sin(a), -19 * math.cos(a), lerp(8.5, 7.0, k)), A(0.2, 0, 3.6), 30)
    else:
        a = lerp(2.3, 1.45, k)
        cam(S, A(21 * math.sin(a), -21 * math.cos(a), lerp(6.5, 5.0, k)), A(0, 0.2, 3.6), 30)


# ---------------------------------------------------------------- the yard
def yard(S, dawn=False):
    if dawn:
        A = env(S, 'yard', '8A7A98', sun=1.6, sunc='FFC8A0', sdir=(0.7, -0.5, 0.25), fk=2.2, skyk=0.8)
        S['yard']['lamp'].data.energy = 600
    else:
        A = env(S, 'yard', '101A36', sun=0.9, sunc='9AB4FF', sdir=(0.5, -0.3, 0.8), fk=5.0, skyk=1.0)
    return A


def rook_gate(S, k, t, lt):
    A = yard(S)
    S['rook'].place(A(0.3, -2.0, 0), -0.15)
    S['rook'].apply(P('cross', head=(0.05, 0.4 * math.sin(lt * 9))))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.6
    cam(S, A(lerp(1.9, 1.4, k), lerp(-7.4, -6.2, k), 2.1), A(0.25, -2.0, 2.75), 30, fcol='FFE4C8')


def rook_door(S, k, t, lt):
    A = yard(S)
    y = lerp(13.5, 18.5, k)
    S['rook'].place(A(0, y, 0), PI)
    pop = ease(lt / 0.2) * (1 - ease((lt - 0.25) / 0.2))
    S['rook'].apply(blend(walk(lt, 1.9), P('stand', aL=(0.9, 0.5, 2.3, 0.6), aR=(0.9, 0.5, 2.3, 0.6)), pop))
    op = ease(k * 1.4)
    for s, hinge in S['yard']['doors']:
        hinge.rotation_euler = (0, 0, s * 1.35 * op)
    S['yard']['doorl'].data.energy = 5000 * op
    cam(S, A(lerp(-1.6, -1.1, k), lerp(9.6, 12.6, k), 1.0), A(0, 21, 3.3), 24, fcol='BFD0FF')


def rook_wrong(S, k, t, lt):
    A = yard(S, dawn=True)
    S['rook'].place(A(0.2, -2.0, 0), 0.2)
    S['hat_off'] = ease(lt / 0.35)
    S['rook'].apply(blend(P('stand'), hat_hold(), lt / 0.35))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-1.6, -1.1, k), lerp(-6.6, -5.9, k), 2.7), A(0.2, -2.0, 2.55), 45, fcol='FFE0D0')


def signoff(S, k, t, lt):
    A = yard(S, dawn=True)
    S['rook'].place(A(3.0, -0.2, 0), -0.75)
    grab = ease((lt - 0.15) / 0.25)
    away = ease((lt - 0.75) / 0.3)
    S['rook'].apply(blend(blend(P('stand'), P('stand', aR=(1.5, 0.1, 0.5), head=(0.2, -0.3)), grab), P('hat'), away))
    S['hat_tip'] = away
    S['face']['rook'] = 'warm' if away < 0.5 else 'deadpan'
    n = S['nut']
    top = A(4.2, 0.55, 4.32)
    hand = A(3.5, 0.2, 3.2)
    u = ease((lt - 0.3) / 0.3)
    n.location = tuple(top[i] + (hand[i] - top[i]) * u for i in range(3))
    n.location.z += 0.5 * math.sin(PI * u)
    n.rotation_euler = (lt * 6, lt * 4, 0)
    if lt > 0.75:
        n.location = FAR
    cam(S, A(lerp(1.2, 1.9, k), lerp(-7.5, -5.8, k), 2.3), A(3.3, 0.1, 3.0), 36, fcol='FFE0D0')


# ---------------------------------------------------------------- 1978, the tunnel
def ring_wide(S, k, t, lt):
    A = ring(S, 1.0, fk=1.2)
    a = lerp(-0.2, -0.1, k)
    bp = arc(a, 3.2, 0)
    yaw = math.atan2(math.cos(a), -math.sin(a))
    S['bug'].place(A(*bp), yaw)
    S['bug'].apply(walk(lt, 1.7))
    rp = arc(a - 0.045, 4.0, 0)
    S['rook'].place(A(*rp), yaw)
    S['rook'].apply(walk(lt + 0.3, 1.7))
    if S['prm'].get('v') == 2:                                   # down the long curve of magnets from above the pipe
        cam(S, A(*arc(lerp(0.5, 0.4, k), 2.6, lerp(6.9, 6.0, k))), A(*arc(-0.1, 0.8, 1.2)), 20, fcol='FFF0DC')
    else:
        cam(S, A(*arc(lerp(-0.6, -0.5, k), 7.6, lerp(6.8, 5.4, k))), A(*arc(-0.12, 0.5, 2.0)), 20, fcol='FFF0DC')


def bug_walk(S, k, t, lt):
    A = ring(S, 1.0, fk=3.4)
    a = lerp(-0.2, -0.13, k)
    yaw = math.atan2(math.cos(a), -math.sin(a))
    bp = arc(a, 3.0, 0)
    S['bug'].place(A(*bp), yaw - 0.5)
    S['bug'].apply({**walk(lt, 1.7), 'aL': (0.75, 0.1, 1.5, 0.6), 'head': (0.25, 0.25)})
    S['clip'].parent = S['bug'].el[0]
    S['clip'].location = (0.0, -0.12, -0.55)
    S['clip'].rotation_euler = (0.9, 0, 0)
    rp = arc(a - 0.035, 4.6, 0)
    S['rook'].place(A(*rp), yaw - 0.7)
    S['rook'].apply({**walk(lt + 0.3, 1.7), 'aR': (0.8, 0.1, 1.3, 0.2)})
    S['face']['rook'] = 'deadpan'
    u = (lt * 1.6) % 1
    S['coin'].location = A(rp[0] + 0.45, rp[1] - 0.55, 1.9 + 2.2 * u * (1 - u))
    S['coin'].rotation_euler = (lt * 30, 0, 0)
    cam(S, A(*arc(a + 0.035, 8.6, 2.6)), A(*arc(a - 0.014, 3.6, 2.5)), 28, fcol='FFF0DC')


def ctrl(S, fk=2.6):
    A = env(S, 'ctrl', fk=fk)
    C = S['ctrl']
    return A, C


def dials(S, t, hi=0.0):
    C = S['ctrl']
    for j, n in enumerate(C['needles']):
        n.rotation_euler = (0, lerp(-0.5, 0.75, hi) + 0.25 * math.sin(t * (2.3 + j)) + 0.1 * math.sin(t * 7.1 + j), 0)
    C['dotpiv'].rotation_euler = (0, t * 7.0, 0)


def ctrl_room(S, k, t, lt):
    A, C = ctrl(S)
    dials(S, t)
    S['op'].place(A(-3.6, 3.6, 0.5), PI)
    S['op'].apply(P('sit', aL=(1.25, 0.1, 0.5), aR=(1.1 + 0.25 * math.sin(lt * 5), 0.25, 0.6), lean=0.3, head=(0.1, 0.3 * math.sin(lt * 2))))
    arrive = ease(lt / 0.9)
    S['rook'].place(A(lerp(3.4, 0.2, arrive), lerp(2.4, 3.3, arrive), 0), lerp(1.9, 2.45, arrive))
    tap = 0.5 + 0.5 * math.sin(lt * 11)
    S['rook'].apply(blend(walk(lt, 2.0), P('stand', aR=(1.1, 0.25, 2.25 + 0.2 * tap, 0.5), aL=(0.3, 0.2, 0.5), head=(-0.2, 0.25)), (lt - 0.7) / 0.25))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(7.4, 3.0, k), lerp(-4.4, -1.6, k), lerp(3.8, 3.0, k)), A(lerp(0.4, -1.6, k), 4.8, 3.2), 24, fill=1.5, fcol='FFE8D0')


def ctrl_on(S, k, t, lt):
    A, C = ctrl(S, fk=1.6)
    dials(S, t, 1.0)
    tint(C['onm'], '3EC46A', 14.0 + 16.0 * (0.5 + 0.5 * math.sin(lt * 14)))
    S['op'].place(A(3.0, 3.6, 0.5), PI)
    S['op'].apply(P('sit', aL=(0.9, 0.1, 1.2), aR=(0.9, 0.1, 1.2), lean=0.2, head=(0.25, 0.0)))
    cam(S, A(lerp(0.6, 2.6, k), lerp(0.4, 1.4, k), 3.9), A(lerp(3.2, 4.2, k), 7.4, 4.4), 30, fcol='DCE8FF')


def clock(S, k, t, lt):
    A, C = ctrl(S, fk=2.0)
    dials(S, t, 0.2)
    C['hands'][0].rotation_euler = (0, 2.6 + k * 3.4, 0)
    C['hands'][1].rotation_euler = (0, k * 40.0, 0)
    cam(S, A(lerp(-6.0, -7.0, k), lerp(1.5, 3.4, k), 4.6), A(-8.2, 7.8, 5.55), 40, roll=0.08, fcol='FFE8D0')


def bug_ctrl(S, k, t, lt):
    A, C = ctrl(S)
    dials(S, t, 0.5)
    S['bug'].place(A(-3.6, 3.6, 0.5), PI)
    S['left']['bug'] = 'still'
    S['bug'].apply(P('sit', aL=(1.2, 0.1, 0.5), aR=(1.35 + 0.2 * math.sin(lt * 6), 0.3, 0.3), lean=0.3, head=(0.0, -0.6 + 0.2 * math.sin(lt * 2.2))))
    cam(S, A(lerp(-7.6, -6.9, k), lerp(5.6, 6.0, k), lerp(2.9, 2.6, k)), A(-3.5, 4.4, 2.6), 32, fcol='FFE8D0')


def fault(S, k, t, lt):
    A = ring(S, 0.85, fk=2.0)
    R = S['ring']
    dead = lt > 0.45
    blink = math.sin(lt * 40) > 0
    tint(R['faultm'], 'D8362A' if not dead else '2A1414', (14.0 if blink else 1.0) if not dead else 0.0)
    R['fneedle'].rotation_euler = (0, lerp(0.9, -1.2, ease((lt - 0.4) / 0.2)) + (0.2 * math.sin(lt * 50) if not dead else 0), 0)
    for j, sp in enumerate(R['spark']):
        u = lt - 0.36 - j * 0.03
        if 0 < u < 0.4:
            sp.location = (1.85 + (rnd(j, 1) - 0.5) * 3 * u, -0.75 - 2.2 * u, 1.0 + (1.5 + rnd(j, 2)) * u - 6 * u * u)
    for j, sm in enumerate(R['smoke']):
        u = lt - 0.45 - j * 0.12
        if u > 0:
            sm.location = (1.85 + 0.2 * math.sin(u * 5 + j), -0.8 - 0.1 * j, 1.2 + 1.3 * u)
            sm.scale = (1 + 2 * u,) * 3
    cam(S, A(lerp(3.3, 2.7, k), lerp(-4.6, -3.7, k), lerp(2.2, 1.9, k)), A(1.5, -0.5, 1.15), 40, fcol='FFF0DC')


def bug_lean(S, k, t, lt):
    A = ring(S, 0.9, fk=2.4)
    tint(S['ring']['faultm'], '2A1414', 0.0)
    bug_in_gap(S, A, ease(k * 1.25))
    rp = (1.75, -4.7, 0.0)
    S['rook'].place(A(*rp), facing(rp, (-1.5, 0.5, 0)))
    S['rook'].apply(blend(P('stand', aR=(0.8, 0.1, 1.3, 0.2)), P('point', aR=(1.5, 0.1, 0.05), head=(-0.05, 0.0)), (lt - 0.25) / 0.2))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(1.4, 0.8, k), lerp(-8.9, -8.0, k), 2.6), A(0.4, -1.0, 2.2), 26, fcol='FFF0DC')


def lean_close(S, k, t, lt):
    A = ring(S, 0.9, fk=2.6)
    tint(S['ring']['faultm'], '2A1414', 0.0)
    bug_in_gap(S, A, lerp(0.6, 1.0, ease(k)), face='squint')
    cam(S, A(lerp(2.6, 2.0, k), lerp(-1.3, -1.0, k), lerp(2.3, 2.15, k)), A(-0.5, -0.05, 2.0), 40, fcol='FFF0DC')


def lamp_off(S, k, t, lt):
    A = ring(S, 0.9, fk=2.6)
    tint(S['ring']['faultm'], '2A1414', 0.0)
    bug_in_gap(S, A)
    rp = (5.6, -3.2, 0.0)
    step = ease(lt / 0.45)
    S['rook'].place(A(rp[0] + 1.5 * (1 - step), rp[1] - 0.5 * (1 - step), 0), facing(rp, (4.6, -9.0, 0)))
    tap = max(0.0, math.sin(lt * 9.5))
    look = ease((lt - 1.2) / 0.25)
    S['rook'].apply(blend(blend(walk(lt, 2.2), P('stand', aL=(2.15 + 0.15 * tap, 0.55, 0.5 + 0.3 * (1 - tap)), head=(-0.3, 0.75)), (lt - 0.3) / 0.2),
                          P('shrug', head=(0.0, -0.1 + 0.3 * math.sin(lt * 8))), look))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(7.4, 4.6, k), lerp(-10.6, -6.6, k), lerp(2.1, 2.9, k)), A(5.15, -3.0, lerp(3.0, 3.3, k)), 30, fcol='FFF0DC')


def bug_work(S, k, t, lt):
    A = ring(S, 0.9, fk=2.6)
    tint(S['ring']['faultm'], '3EC46A' if k > 0.75 else '2A1414', 6.0 if k > 0.75 else 0.0)
    bp = (1.6, -1.75, 0.0)
    S['bug'].place(A(*bp), PI)
    w = math.sin(lt * 9)
    S['bug'].apply(P('stand', **{**WORK, 'aR': (1.35 + 0.1 * w, 0.05, 0.5 - 0.15 * w)}))
    S['face']['bug'] = 'squint'
    rp = (0.0, -3.7, 0.0)
    S['rook'].place(A(*rp), facing(rp, (0.3, 4.0, 0)))
    sh = ease((lt - 0.35) / 0.25)
    S['rook'].apply(blend(P('stand', head=(0.0, -0.5)), P('shrug', head=(-0.05, 0.25 * math.sin(lt * 7))), sh))
    S['face']['rook'] = 'shocked' if sh < 0.5 else 'deadpan'
    S['hat_tip'] = sh
    cam(S, A(lerp(0.0, 0.5, k), lerp(3.7, 4.0, k), lerp(3.3, 3.0, k)), A(0.8, -2.4, 2.35), 28, fcol='FFF0DC')


# ---------------------------------------------------------------- that night, and Moscow
def study(S, night=True):
    A = env(S, 'study', fk=2.2 if night else 2.8)
    D = S['study']
    if night:
        D['lamp'].data.energy = 900
    else:
        D['lamp'].data.energy = 150
        D['paneL'].data.energy = 1100
        D['top'].data.energy = 500
    return A


def bug_swell(S, k, t, lt):
    A = study(S)
    S['bug'].place(A(-0.5, 0.1, 0.5), 0.0)
    vis(S['bug'].extra['swell'], True)
    S['left']['bug'] = 'swollen'
    up = ease(lt / 0.5)
    S['bug'].apply(blend(P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.7, -0.1, 1.5, 1.0)),
                         P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.6, 0.95, 2.3, 0.1), lean=0.12, head=(0.1, -0.2)), up))
    S['face']['bug'] = 'tired'
    S['rook'].place(A(1.7, 1.0, 0), -0.6)
    S['hat_off'] = ease((lt - 0.3) / 0.4)
    S['rook'].apply(blend(P('stand', lean=0.12, head=(0.1, 0.0)), hat_hold(lean=0.15), (lt - 0.3) / 0.4))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(0.0, 0.4, k), lerp(-6.4, -5.5, k), 3.3), A(0.45, 0.3, 2.6), 40, fcol='FFE0C0')


def clinic(S, warm=False):
    A = env(S, 'clinic', fk=1.6)
    C = S['clinic']
    if warm:
        C['win'].data.energy = 380
        C['top'].data.energy = 200
        S['fillk'] = 0.9
        C['win'].data.color = K.hexc('FFD9A0')[:3]
        tint(C['panem'], 'FFE0B0', 2.4)
    u = (S['time'] * 0.9) % 1
    C['drop'].location = (2.05, 3.0, 4.05 - 0.9 * u * u)
    return A


def patient(S, A, face='shut'):
    S['pat'].place(A(0, -0.55, 1.98), 0.0, pitch=-PI / 2)
    S['pat'].apply(P('stand', aL=(0.25, 0.3, 0.3), aR=(0.25, 0.3, 0.3)))
    vis(S['pat'].extra['swell'], True)
    S['left']['pat'] = 'swollen'
    S['face']['pat'] = face


def clinic_wide(S, k, t, lt):
    S['time'] = t
    A = clinic(S)
    patient(S, A)
    dp = (3.4, 0.6, 0.0)
    S['doc'].place(A(*dp), facing(dp, (0, 1.6, 0)))
    S['doc'].apply(P('stand', aL=(0.8, 0.0, 1.3, 0.7), aR=(0.9, 0.1, 1.5, 0.4), head=(0.3, 0.0)))
    S['clip'].parent = S['doc'].el[0]
    S['clip'].location = (0.0, -0.12, -0.55)
    S['clip'].rotation_euler = (1.0, 0, 0)
    cam(S, A(lerp(-4.6, -3.8, k), lerp(-5.6, -5.0, k), lerp(4.8, 4.4, k)), A(0.7, 1.3, 2.3), 28, fcol='E8F0FF')


def doctor(S, k, t, lt):
    S['time'] = t
    A = clinic(S)
    patient(S, A)
    dp = (3.4, 0.6, 0.0)
    S['doc'].place(A(*dp), facing(dp, (-2.0, -3.0, 0)))
    S['doc'].apply(P('stand', aL=(0.8, 0.0, 1.3, 0.7), aR=(0.2, 0.1, 0.3), head=(0.15, 0.45 * math.sin(lt * 6.5))))
    S['clip'].parent = S['doc'].el[0]
    S['clip'].location = (0.0, -0.12, -0.55)
    S['clip'].rotation_euler = (1.0, 0, 0)
    S['face']['doc'] = 'tired'
    rp = (5.6, 1.6, 0.0)
    S['rook'].place(A(*rp), facing(rp, (-1.0, -3.0, 0)))
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.1, 0.45)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(0.6, 1.2, k), lerp(-4.6, -4.0, k), 3.0), A(4.3, 1.0, 2.75), 32, fcol='E8F0FF')


def rook_bed(S, k, t, lt):
    S['time'] = t
    A = clinic(S)
    patient(S, A)
    rp = (-2.9, 1.5, 0.0)
    S['rook'].place(A(*rp), facing(rp, (1.5, -1.5, 0)))
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(lerp(0.2, 0.42, k), -0.35)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(2.9, 2.4, k), lerp(-2.6, -2.2, k), lerp(4.5, 4.2, k)), A(-1.6, 1.5, 2.5), 28, fcol='E8F0FF')


def pat_still(S, k, t, lt):
    S['time'] = t
    A = clinic(S)
    S['clinic']['win'].data.energy = 500
    S['clinic']['top'].data.energy = 250
    patient(S, A)
    cam(S, A(lerp(3.6, 2.9, k), lerp(-0.6, 0.2, k), lerp(4.4, 4.9, k)), A(0.6, 2.0, 2.6), 34, fcol='CFE0FF')


def bug_wakes(S, k, t, lt):
    S['time'] = t
    A = clinic(S, warm=True)
    patient(S, A, 'calm' if lt > 0.25 else 'shut')
    cam(S, A(lerp(-2.3, -1.8, k), lerp(-0.1, 0.4, k), lerp(4.6, 4.2, k)), A(0.0, 1.75, 2.05), 48, fcol='FFE8C8')


def rook_shock(S, k, t, lt):
    S['time'] = t
    A = clinic(S, warm=True)
    patient(S, A, 'calm')
    rp = (-3.0, 0.4, 0.0)
    pop = ease(lt / 0.15)
    S['rook'].place(A(*rp), facing(rp, (0.5, -1.4, 0)))
    S['rook'].apply(blend(hat_hold(), P('stand', **ALARM), pop))
    S['face']['rook'] = 'shocked' if pop > 0.3 else 'sad'
    feather(S, A(rp[0] + 0.3, rp[1] - 0.3, 3.3), lt, 0.1)
    cam(S, A(lerp(-0.7, -1.0, k), lerp(-3.4, -2.9, k), 2.6), A(-2.9, 0.3, 2.7), 36, fcol='FFE8C8')


# ---------------------------------------------------------------- afterwards
def bug_ear(S, k, t, lt):
    A = study(S, night=False)
    bp = (-4.6, 0.6, 0.0)
    S['bug'].place(A(*bp), 0.25)
    S['left']['bug'] = 'still'
    cup = ease((lt - 0.25) / 0.35)
    S['bug'].apply(blend(P('stand'), P('stand', aR=(0.2, 1.65, 2.3, -1.3), head=(0.05, 0.3), lean=0.05), cup))
    S['face']['bug'] = 'tired'
    cam(S, A(lerp(-1.3, -1.7, k), lerp(0.2, 0.5, k), 2.75), A(-4.45, 0.55, 2.5), 40, fcol='FFF0DC')


def face_half(S, k, t, lt):
    A = study(S, night=False)
    bp = (-4.4, 1.2, 0.0)
    S['bug'].place(A(*bp), 0.0)
    S['left']['bug'] = 'still'
    S['face']['bug'] = 'wide' if (lt * 1.5) % 1 > 0.45 else 'calm'
    S['bug'].apply(P('stand', head=(0.0, 0.1 * math.sin(lt * 2.5))))
    rp = (-2.5, 0.6, 0.0)
    S['rook'].place(A(*rp), facing(rp, (-5.6, -2.6, 0)))
    tap = 0.5 + 0.5 * math.sin(lt * 9)
    S['rook'].apply(P('stand', aR=(1.1, 0.25, 2.25 + 0.2 * tap, 0.5), aL=(0.3, 0.2, 0.5), head=(-0.05, 0.65), lean=0.1))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(-4.4, -3.6, k), lerp(-4.6, -4.0, k), 2.6), A(-3.55, 1.0, 2.6), 45, fcol='FFF0DC')


def thesis(S, k, t, lt):
    A = study(S, night=False)
    S['bug'].place(A(0, 0.1, 0.5), 0.0)
    S['left']['bug'] = 'still'
    w = math.sin(lt * 12)
    S['bug'].apply(P('sit', aL=(0.9, 0.1, 1.15, 0.6), aR=(0.95 + 0.04 * w, 0.0, 1.2, 0.7 + 0.15 * w), lean=0.35, head=(0.45, 0.1)))
    S['face']['bug'] = 'squint'
    th = S['study']['thesis']
    drop = ease((lt - 0.55) / 0.18)
    th.location = (1.6, -1.5, lerp(5.0, 1.88, drop)) if lt > 0.35 else (1.6, -1.5, -40)
    th.rotation_euler = (0, 0, lerp(0.6, 0.1, drop))
    cam(S, A(lerp(-3.4, -2.7, k), lerp(-6.4, -5.8, k), lerp(4.6, 4.1, k)), A(0.5, -0.7, 2.1), 30, fcol='FFF0DC')


def bug_back(S, k, t, lt):
    A = ring(S, 1.0, fk=2.6)
    a = lerp(-0.075, -0.02, k)
    yaw = math.atan2(math.cos(a), -math.sin(a))
    S['bug'].place(A(*arc(a, 3.2, 0)), yaw)
    S['left']['bug'] = 'still'
    S['bug'].apply(walk(lt, 1.6))
    rp = arc(-0.105, 5.4, 0)
    S['rook'].place(A(*rp), yaw - 2.0)
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.0, 0.9)))
    S['face']['rook'] = 'warm'
    cam(S, A(*arc(lerp(-0.2, -0.175, k), 6.4, 2.5)), A(*arc(-0.03, 3.0, 2.7)), 30, fcol='FFF0DC')


# ---------------------------------------------------------------- photographs for the case board
def photo_ring(S, k, t, lt):
    A = ring(S, 1.0, fk=1.4)
    cam(S, A(*arc(-0.3, 6.5, 4.4)), A(*arc(0.0, 0.5, 2.0)), 22)


def photo_bug(S, k, t, lt):
    A = ring(S, 1.0, fk=3.0)
    bp = arc(-0.16, 3.4, 0)
    S['bug'].place(A(*bp), 0.25)
    S['bug'].apply(P('stand', aL=(0.6, -0.15, 1.1, 0.8), aR=(0.6, -0.15, 1.1, 0.8)))
    S['face']['bug'] = 'warm'
    cam(S, A(bp[0] + 1.2, bp[1] - 5.6, 2.7), A(bp[0], bp[1], 2.45), 50)


SHOTS3D = {f.__name__: f for f in (
    beam_fire, flash_side, bug_flash, rook_flinch, head_xray, rook_gate, rook_door, rook_wrong, signoff, ring_wide, bug_walk, ctrl_room, ctrl_on,
    clock, bug_ctrl, fault, bug_lean, lean_close, lamp_off, bug_work, bug_swell, clinic_wide, doctor, rook_bed, pat_still, bug_wakes, rook_shock,
    bug_ear, face_half, thesis, bug_back)}
STILLS = dict(ring=photo_ring, bug=photo_bug)


# ================================================================ long-form extension (16:9 full case file)
# Same story, same world, more of it. New sets: a road through pines to an institute gate by day (where it happened),
# the ring seen from the air as a grassed bank in a forest (how big the machine is), an access corridor ending in a
# shielding door with a panel of warning lamps over it (the safety failure), a night road with a plain van heading
# for a city (the journey to Moscow), a clinic corridor with a bench (the wait), and an office with a counter and a
# filing cabinet (the decade of secrecy, the 1996 application). New shots on the Short's sets as well. Still generic:
# no emblem, flag, sign or lettering anywhere, the buildings, van and rooms are not models of real ones, and the
# extra people (a second doctor, a clerk) are stand-ins, not likenesses.
import bmesh  # noqa: E402

ORG.update(town=(18000, 0, 0), air=(21000, 0, 0), corr=(24000, 0, 0), road=(27000, 0, 0), wcor=(30000, 0, 0), office=(33000, 0, 0))
DOC2 = dict(top='E4E8E2', pants='E4E8E2', hand='E0B898', boot='2A2420')
CLK = dict(top='5A4A6A', pants='2E2E38', hand='DDB090', boot='1A1A20')
B96 = dict(top='4A4E58', pants='2E323A', hand=SKIN, boot='1A1A20')
_kit_add = add


def add(kind, col, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, rough=0.9, emit=0.0, alpha=1.0, **kw):
    """Same primitives as the kit's add(), made from mesh data instead of operators, which slow down as the scene
    fills. The Short's set functions look the name up when they run, so every set in the film builds this way."""
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


def pine(r, x, y, s=1.0, i=0, snow=False):
    add('cylinder', '3A2A1E', (x, y, 1.2 * s), radius=0.3 * s, depth=2.4 * s, vertices=5, parent=r)
    g = ('24483A', '2C5444', '1E3E32')[i % 3] if not snow else ('1E2E34', '24363C', '1A282E')[i % 3]
    for j in range(3):
        add('cone', g, (x, y, (3.2 + j * 2.2) * s), radius1=(2.4 - j * 0.6) * s, radius2=0.0, depth=3.4 * s, vertices=6, parent=r)
        if snow:
            add('cone', 'C8D4E8', (x, y, (4.3 + j * 2.2) * s), radius1=(1.0 - j * 0.22) * s, radius2=0.0, depth=1.3 * s, vertices=6, parent=r)


# ---------------------------------------------------------------- the road to the institute, by day
def set_town(r):
    out = {}
    box('5E7A52', (0, 20, -0.2), (400, 400, 0.4), r)
    box('3A3E46', (0, 10, 0.02), (8, 150, 0.06), r)
    for j in range(24):
        box('D8D8CC', (0, -50 + j * 5.5, 0.07), (0.25, 2.4, 0.02), r)
    for sx in (-1, 1):
        box('9A9A90', (sx * 5.2, 10, 0.08), (2.2, 150, 0.16), r)
    n = 0
    for i in range(120):
        x = (9.5 + 46 * rnd(i, 61)) * (1 if i % 2 else -1)
        y = -48 + 96 * rnd(i, 62)
        if 12 < y < 24 and abs(x) < 16:
            continue
        pine(r, x, y, 1.1 + 0.9 * rnd(i, 63), i)
        n += 1
    box('B8B4A8', (0, 64, 8), (120, 14, 16), r)                                             # the long institute block
    box('8E8A80', (0, 64, 16.3), (121, 14.6, 0.6), r)
    for j in range(26):
        for row in range(3):
            box('2A3A50', (-56 + j * 4.5, 56.95, 3.6 + row * 4.4), (2.6, 0.1, 2.4), r, rough=0.3)
    box('A8A498', (0, 55.5, 4.0), (12, 3, 8.0), r)                                          # entrance block
    box('3A4250', (0, 53.95, 2.6), (5.0, 0.1, 5.2), r, rough=0.3)
    box('9A968A', (38, 66, 16), (6, 6, 32), r)                                              # a plain tower at one end
    for sx in (-1, 1):                                                                      # gate posts, fence, a small gatehouse
        box('6E7278', (sx * 4.9, 18, 1.6), (0.8, 0.8, 3.2), r)
        for j in range(22):
            box('3A3E46', (sx * (6.2 + j * 1.3), 18, 1.5), (0.12, 0.12, 3.0), r)
        box('3A3E46', (sx * 20, 18, 2.8), (29, 0.12, 0.14), r)
        box('3A3E46', (sx * 20, 18, 0.6), (29, 0.12, 0.14), r)
    box('C8C4B4', (-9.0, 15.5, 1.9), (4.4, 4.4, 3.8), r)
    box('8E8A80', (-9.0, 15.5, 3.95), (5.0, 5.0, 0.3), r)
    box('2A3A50', (-6.78, 15.5, 2.4), (0.06, 2.4, 1.4), r, rough=0.3)
    out['boom'] = bm_ = mov(empty((-4.4, 18, 2.0), r))
    for j in range(9):
        box('FF7A1A' if j % 2 else 'F0F0E8', (0.5 + j * 1.0, 0, 0), (1.0, 0.22, 0.22), bm_)
    box('3A3E46', (-0.6, 0, 0), (1.0, 0.5, 0.6), bm_)
    for j, y in enumerate((-30, -6, 30)):                                                   # street lamps
        add('cylinder', '4A4E56', (-6.6, y, 4.0), radius=0.14, depth=8.0, vertices=6, parent=r)
        box('4A4E56', (-5.8, y, 7.9), (1.8, 0.16, 0.16), r)
        box('E8E4D0', (-5.0, y, 7.78), (0.8, 0.4, 0.14), r)
    for j, (x, y, hh) in enumerate(((-62, 30, 24), (-70, 4, 18), (66, 22, 22), (72, -6, 26))):   # housing blocks behind the trees
        box(('C8BCA8', 'B4B8B0', 'C0B8AC', 'B0B4B8')[j], (x, y, hh / 2), (14, 30, hh), r)
        for row in range(int(hh / 4)):
            for k in range(7):
                box('3A4658', (x - (7.02 if x > 0 else -7.02), y - 12 + k * 4, 2.6 + row * 4), (0.06, 1.8, 1.8), r)
    return out


# ---------------------------------------------------------------- the ring from the air
def set_air(r):
    out = {}
    box('35523A', (0, 0, -0.3), (900, 900, 0.6), r)
    add('cylinder', '587A4E', (0, 0, 0.05), radius=62, depth=0.2, vertices=40, parent=r)
    RA, N = 70.0, 72
    for i in range(N):
        a = i * 2 * PI / N
        L = 2 * PI * RA / N + 0.3
        p = (RA * math.sin(a), -RA * math.cos(a), 0)
        box('6E8A5A', (p[0], p[1], 1.6), (L, 11, 3.2), r, rot=(0, 0, a))
        box('C8C8BC', (p[0], p[1], 3.35), (L, 3.4, 0.5), r, rot=(0, 0, a))
        if i % 6 == 0:
            box('A8A498', (RA * 0.9 * math.sin(a), -RA * 0.9 * math.cos(a), 2.2), (5, 6, 4.4), r, rot=(0, 0, a))
    box('B8B4A8', (0, -84, 6), (44, 20, 12), r)                                             # a big hall on the ring
    box('8E8A80', (0, -84, 12.2), (45, 21, 0.5), r)
    box('A8A498', (-70, -80, 3.5), (96, 8, 7), r)                                           # a long straight building feeding it
    box('B8B4A8', (-124, -80, 5), (16, 16, 10), r)
    for (x, y, w_, d_, hh) in ((78, -30, 30, 18, 10), (60, 62, 24, 30, 9), (-74, 50, 26, 20, 9), (20, 20, 16, 10, 6), (-18, -6, 10, 14, 5)):
        box('B4B0A4', (x, y, hh / 2), (w_, d_, hh), r)
        box('8E8A80', (x, y, hh + 0.2), (w_ + 1, d_ + 1, 0.4), r)
    box('4A4E56', (0, -150, 0.06), (7, 120, 0.1), r)                                        # roads
    box('4A4E56', (60, -100, 0.06), (130, 7, 0.1), r)
    box('4A4E56', (0, 0, 0.12), (5, 120, 0.1), r)
    for i in range(520):
        d = 84 + 220 * rnd(i, 71) ** 0.8
        a = rnd(i, 72) * 2 * PI
        x, y = d * math.sin(a), -d * math.cos(a)
        if (abs(x) < 8 and y < -80) or (y < -66 and y > -96 and x < 30 and x > -140) or (abs(y + 100) < 8 and x > 0):
            continue
        s = 2.0 + 1.6 * rnd(i, 73)
        add('cone', ('24483A', '2C5444', '1E3E32', '30583E')[i % 4], (x, y, 2.6 * s), radius1=1.5 * s, radius2=0.0, depth=5.2 * s, vertices=5, parent=r)
    for i in range(40):
        d = 12 + 44 * rnd(i, 74)
        a = rnd(i, 75) * 2 * PI
        add('cone', '2C5444', (d * math.sin(a), -d * math.cos(a), 4.0), radius1=2.6, radius2=0.0, depth=8.0, vertices=5, parent=r)
    out['mark'] = mov(add('ico_sphere', 'D6E6FF', (0, -RA, 4.6), radius=3.2, subdivisions=1, parent=r, emit=30.0))
    return out


# ---------------------------------------------------------------- the access corridor and the shielding door
def set_corr(r):
    out = {}
    box('4A4E56', (0, 2, -0.1), (8.4, 34, 0.2), r)
    box('2A2C32', (0, 2, 7.1), (8.4, 34, 0.2), r)
    for sx in (-1, 1):
        box('C8B878', (sx * 4.1, 2, 4.6), (0.3, 34, 5.0), r)
        box('6A5A3A', (sx * 4.08, 2, 1.05), (0.34, 34, 2.1), r)
        box('3A3E46', (sx * 3.9, 2, 2.14), (0.1, 34, 0.1), r)
    box('C8B878', (0, -15, 3.5), (8.4, 0.3, 7.2), r)
    for j, (x, c) in enumerate(((-3.2, 'FF7A1A'), (-2.7, '8E96A4'), (3.3, '2B5FA8'))):       # pipes under the ceiling
        add('cylinder', c, (x, 2, 6.5), rot=(PI / 2, 0, 0), radius=0.2, depth=34, vertices=6, parent=r, rough=0.5)
    for j, y in enumerate((-10, -2, 6, 13)):
        box('FFF0D2', (0, y, 6.9), (0.6, 2.6, 0.1), r, emit=6.0)
        if j % 2:
            light((0, y, 6.3), 900, 'FFE8C8', kind='POINT', parent=r)
    for (x, w_) in ((-3.0, 2.4), (3.0, 2.4)):                                               # the end wall around the door
        box('8A8E84', (x, 18, 3.5), (w_, 0.6, 7.2), r)
    box('8A8E84', (0, 18, 6.25), (3.8, 0.6, 1.7), r)
    for j in range(10):                                                                     # striped frame
        c = 'FF7A1A' if j % 2 else '15171C'
        for sx in (-1, 1):
            box(c, (sx * 1.85, 17.66, 0.27 + j * 0.54), (0.3, 0.1, 0.54), r)
    out['hinge'] = hg = mov(empty((-1.7, 17.75, 0), r))
    box('6E7686', (1.7, 0, 2.7), (3.4, 0.5, 5.4), hg, rough=0.4)
    box('59616E', (1.7, -0.27, 2.7), (2.8, 0.06, 4.8), hg, rough=0.4)
    add('torus', 'B9C0CA', (1.9, -0.36, 2.7), rot=(PI / 2, 0, 0), major_radius=0.55, minor_radius=0.07, major_segments=10, minor_segments=4, parent=hg, rough=0.3)
    for j in range(4):
        box('B9C0CA', (1.9, -0.36, 2.7), (1.1, 0.06, 0.08), hg, rot=(0, j * PI / 4, 0), rough=0.3)
    box('FFF0D2', (0, 20.5, 3.0), (5, 0.1, 6), r, emit=7.0)                                 # the lit tunnel beyond
    out['tunl'] = light((0, 16.6, 3.2), 0, 'FFE8C8', kind='POINT', parent=r)
    box('22252C', (0, 17.6, 6.1), (3.4, 0.3, 1.1), r)                                       # the panel of warning lamps over the door
    out['lampm'] = []
    for j in range(3):
        m = own_mat('corrlamp%d' % j, '3A1412', 0.3, 0.0)
        use(add('cylinder', '3A1412', (-1.05 + j * 1.05, 17.4, 6.1), rot=(PI / 2, 0, 0), radius=0.36, depth=0.12, vertices=10, parent=r), m)
        add('torus', '8E96A4', (-1.05 + j * 1.05, 17.36, 6.1), rot=(PI / 2, 0, 0), major_radius=0.37, minor_radius=0.04, major_segments=10, minor_segments=4, parent=r, rough=0.3)
        out['lampm'].append(m)
    box('39424C', (3.8, 12.5, 3.0), (0.4, 1.6, 2.2), r)                                     # a switch box by the door
    box('D8362A', (3.56, 12.5, 3.3), (0.1, 0.3, 0.5), r)
    for j in range(3):                                                                      # crates and a bench against the wall
        box(('6A5A3A', '4A5A6E', '6A5A3A')[j], (-3.2, -6 + j * 1.9, 0.7 + 0.15 * (j % 2)), (1.4, 1.6, 1.4 + 0.3 * (j % 2)), r)
    box('5A3E2A', (3.3, 0, 1.0), (1.2, 4.0, 0.16), r)
    for y in (-1.7, 1.7):
        box('3A3E46', (3.3, y, 0.5), (1.0, 0.14, 1.0), r)
    box('2C5A50', (-3.85, 8, 3.6), (0.14, 2.4, 1.8), r)                                     # a blank notice board (nothing written on it)
    return out


# ---------------------------------------------------------------- the night road to the city
def set_road(r):
    out = {}
    box('B8C6DC', (40, 0, -0.2), (600, 400, 0.4), r)
    box('2E323A', (40, 0, 0.02), (600, 9, 0.06), r)
    for j in range(60):
        box('C8C8BC', (-120 + j * 6.0, 0, 0.07), (2.6, 0.22, 0.02), r)
    for i in range(150):
        x = -110 + 250 * rnd(i, 81)
        y = (8.5 + 40 * rnd(i, 82)) * (1 if i % 2 else -1)
        if -20 < y < 0:
            y -= 12
        pine(r, x, y, 1.0 + 0.9 * rnd(i, 83), i, snow=True)
    for j in range(9):
        x = -70 + j * 24
        add('cylinder', '2A2F3A', (x, 6.2, 4.2), radius=0.14, depth=8.4, vertices=6, parent=r)
        box('2A2F3A', (x, 5.4, 8.3), (0.16, 1.8, 0.16), r)
        box('FFE2B0', (x, 4.7, 8.15), (0.5, 0.9, 0.14), r, emit=12.0)
        if j in (2, 3, 4, 5):
            light((x, 4.7, 7.6), 1800, 'FFD9A8', kind='POINT', parent=r)
    for j in range(22):                                                                     # the city far ahead
        hh = 14 + 34 * rnd(j, 84)
        x, y = 190 + 50 * rnd(j, 85), -110 + j * 10.5
        box(('2A3040', '323848', '262C3A')[j % 3], (x, y, hh / 2), (12, 9, hh), r)
        for k in range(int(hh / 3.2)):
            for q in range(3):
                if rnd(j * 7 + k, q + 86) > 0.5:
                    box('FFD890', (x - 6.05, y - 2.8 + q * 2.8, 2.4 + k * 3.2), (0.1, 1.5, 1.5), r, emit=4.0)
    out['van'] = v = mov(empty((0, 0, -60), r))                                             # a plain van, no markings
    box('C4CCC0', (-0.4, 0, 1.75), (4.4, 2.2, 2.3), v)
    box('C4CCC0', (2.5, 0, 1.3), (1.5, 2.1, 1.4), v)
    box('1E2630', (2.0, 0, 2.3), (0.5, 1.9, 0.9), v, rot=(0, -0.35, 0), rough=0.2)
    for sy in (-1, 1):
        box('1E2630', (0.6, sy * 1.11, 2.25), (1.3, 0.04, 0.8), v, rough=0.2)
        box('FFE9B8', (-1.4, sy * 1.11, 2.25), (1.4, 0.05, 0.7), v, emit=1.6)
        for x in (-1.7, 2.3):
            add('cylinder', '15171C', (x, sy * 1.0, 0.5), rot=(PI / 2, 0, 0), radius=0.5, depth=0.34, vertices=10, parent=v)
        box('FFF4D0', (3.27, sy * 0.7, 1.05), (0.06, 0.4, 0.26), v, emit=30.0)
        box('FF2A1A', (-2.62, sy * 0.8, 1.2), (0.06, 0.3, 0.3), v, emit=12.0)
    box('2A2F3A', (0.2, 0, 0.75), (5.6, 2.0, 0.4), v)
    light((5.5, 0, 1.4), 2500, 'FFF0D0', kind='POINT', parent=v)
    return out


# ---------------------------------------------------------------- the clinic corridor
def set_wcor(r):
    out = dict(tops=[])
    box('8FA89A', (0, 0, -0.1), (40, 7.4, 0.2), r)
    box('6E8A7C', (0, 0, 0.01), (40, 1.6, 0.02), r)
    box('E4E8E0', (0, 0, 7.1), (40, 7.4, 0.2), r)
    for sy in (-1, 1):
        box('E8ECE4', (0, sy * 3.7, 4.9), (40, 0.3, 4.6), r)
        box('7FA0B0', (0, sy * 3.68, 1.3), (40, 0.34, 2.6), r)
        box('5A7A8A', (0, sy * 3.5, 2.64), (40, 0.08, 0.1), r)
    for sx in (-1, 1):
        box('E8ECE4', (sx * 20, 0, 3.5), (0.3, 7.4, 7.2), r)
    for j, x in enumerate((-10, 0, 10)):                                                    # doors along one side
        box('C8C2B0', (x, 3.5, 2.8), (3.2, 0.12, 5.7), r)
        if j != 1:
            box('D8D2C0', (x, 3.42, 2.65), (2.7, 0.12, 5.3), r)
            box('B9C0CA', (x + 1.0, 3.34, 2.6), (0.1, 0.1, 0.5), r, rough=0.3)
    out['hinge'] = hg = mov(empty((-1.35, 3.42, 0), r))
    box('D8D2C0', (1.35, 0, 2.65), (2.7, 0.12, 5.3), hg)
    box('B9C0CA', (2.35, -0.08, 2.6), (0.1, 0.1, 0.5), hg, rough=0.3)
    box('FFE9C8', (0, 3.9, 2.7), (2.6, 0.06, 5.2), r, emit=2.5)
    out['panem'] = pm = own_mat('wcorpane', '1A2A4A', 1.0, 0.6)
    for x in (-12, -4, 4, 12):                                                              # windows along the other side
        use(box('1A2A4A', (x, -3.6, 4.5), (3.4, 0.08, 2.8), r), pm)
        box('F0F0EA', (x, -3.52, 4.5), (0.14, 0.1, 2.8), r)
        box('F0F0EA', (x, -3.52, 4.5), (3.5, 0.1, 0.14), r)
        box('F0F0EA', (x, -3.5, 3.05), (3.8, 0.3, 0.14), r)
    out['winl'] = w = light((4, -3.0, 4.6), 0, 'FFD9A0', 3.0, parent=r)
    w.rotation_euler = (-PI / 2, 0, 0)
    for x in (-9, 3, 13):
        box('FFF6E0', (x, 0, 6.95), (2.4, 0.6, 0.1), r, emit=4.0)
        out['tops'].append(light((x, 0, 6.3), 300, 'F0F4FF', kind='POINT', parent=r))
    box('8A6A4A', (4, -2.85, 1.02), (5.4, 1.2, 0.16), r)                                    # the bench
    box('8A6A4A', (4, -3.38, 1.9), (5.4, 0.14, 1.2), r)
    for x in (1.6, 6.4):
        box('3A3E46', (x, -2.85, 0.5), (0.14, 1.1, 1.0), r)
    add('cylinder', 'F0ECDC', (-5, 3.5, 5.6), rot=(PI / 2, 0, 0), radius=0.8, depth=0.08, vertices=14, parent=r, rough=0.4, emit=0.5)   # a clock
    out['hand'] = hd = mov(empty((-5, 3.42, 5.6), r))
    box('15171C', (0, 0, 0.3), (0.07, 0.03, 0.62), hd)
    box('15171C', (-5, 3.42, 5.8), (0.09, 0.03, 0.4), r)
    box('D8DCD8', (-13, -2.4, 1.6), (2.6, 1.4, 0.12), r, rough=0.4)                         # a trolley
    box('D8DCD8', (-13, -2.4, 0.6), (2.6, 1.4, 0.1), r, rough=0.4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('cylinder', 'B9C0CA', (-13 + sx * 1.2, -2.4 + sy * 0.6, 0.85), radius=0.05, depth=1.7, vertices=5, parent=r, rough=0.3)
    box('CFE4EA', (-13.4, -2.4, 1.9), (0.5, 0.5, 0.5), r, rough=0.2)
    return out


# ---------------------------------------------------------------- the office
def set_office(r):
    out = {}
    box('6A5A48', (0, 0, -0.1), (20, 16, 0.2), r)
    box('D0D0C8', (0, 0, 7.1), (20, 16, 0.2), r)
    for sx in (-1, 1):
        box('A8B0B4', (sx * 10, 0, 4.7), (0.3, 16, 4.8), r)
        box('5A6670', (sx * 9.98, 0, 1.2), (0.34, 16, 2.4), r)
    for sy in (-1, 1):
        box('A8B0B4', (0, sy * 8, 4.7), (20, 0.3, 4.8), r)
        box('5A6670', (0, sy * 7.98, 1.2), (20, 0.34, 2.4), r)
    box('7A5A3A', (0, 0.6, 0.75), (10, 1.5, 1.5), r)                                        # the counter
    box('5A3E2A', (0, 0.5, 1.56), (10.4, 1.9, 0.14), r)
    for x in (-5.0, 5.0):
        box('5A3E2A', (x, 0.6, 3.85), (0.24, 0.24, 4.5), r)
    box('5A3E2A', (0, 0.6, 6.1), (10.3, 0.3, 0.3), r)
    for j in range(12):                                                                     # pigeonholes on the back wall
        for row in range(4):
            box('3A2E24', (-6.05 + j * 1.1, 7.7, 2.2 + row * 1.05), (0.95, 0.4, 0.9), r)
            if rnd(j, row + 91) > 0.3:
                box(('D8B870', 'C8C0A8', 'B88A5A', 'D0C8B0')[int(rnd(j, row + 92) * 4)], (-6.05 + j * 1.1, 7.52, 2.1 + row * 1.05),
                    (0.6 + 0.3 * rnd(j, row), 0.1, 0.62), r)
    box('5E6A72', (-7.4, 3.6, 2.6), (2.2, 2.4, 5.2), r)                                     # the filing cabinet
    for j in range(3):
        box('6E7A82', (-7.4, 2.38, 0.95 + j * 1.6), (1.9, 0.06, 1.3), r) if j != 2 else None
    out['drawer'] = dr = mov(empty((-7.4, 3.5, 4.15), r))
    box('6E7A82', (0, -1.12, 0), (1.9, 0.08, 1.3), dr)
    box('B9C0CA', (0, -1.2, 0.1), (0.7, 0.08, 0.12), dr, rough=0.3)
    box('4E5A62', (0, 0, -0.55), (1.8, 2.2, 0.08), dr)
    for sx in (-1, 1):
        box('4E5A62', (sx * 0.9, 0, -0.1), (0.06, 2.2, 0.9), dr)
    box('D8B870', (0, -0.3, 0.0), (1.5, 0.12, 0.95), dr)
    box('F0EEE4', (0, -0.42, 0.02), (1.4, 0.06, 0.9), dr)
    box('D8B870', (0.1, 0.1, -0.02), (1.5, 0.1, 0.9), dr)
    box('E4F0FF', (9.8, -2, 4.5), (0.06, 5.0, 3.2), r, emit=2.4)                             # a window with blind slats
    for j in range(9):
        box('C8C4B4', (9.72, -2, 3.05 + j * 0.37), (0.1, 5.1, 0.16), r)
    out['winl'] = w = light((9.0, -2, 4.5), 700, 'E4F0FF', 3.2, parent=r)
    w.rotation_euler = (0, PI / 2, 0)
    for j in range(3):                                                                      # waiting chairs
        box('5A6670', (-6 + j * 1.9, -7.0, 1.0), (1.5, 1.4, 0.16), r)
        box('5A6670', (-6 + j * 1.9, -7.62, 1.9), (1.5, 0.14, 1.7), r)
    box('FFF6E0', (0, -1, 6.95), (4, 0.7, 0.1), r, emit=4.0)
    out['top'] = light((0, -1.5, 6.3), 900, 'FFF0DC', kind='POINT', parent=r)
    add('cylinder', '22252C', (3.6, 0.6, 1.7), radius=0.34, depth=0.1, vertices=8, parent=r)   # a lamp on the counter
    add('cylinder', '22252C', (3.6, 0.6, 2.2), radius=0.05, depth=1.0, vertices=6, parent=r)
    add('cone', 'C89A3A', (3.5, 0.4, 2.8), rot=(0.3, 0, 0), radius1=0.5, radius2=0.2, depth=0.4, vertices=8, parent=r, emit=1.2)
    out['lampl'] = light((3.4, 0.0, 2.5), 350, 'FFD9A0', kind='POINT', parent=r)
    box('2A2E38', (-3.4, 0.7, 1.75), (1.3, 0.9, 0.24), r)                                    # a stamp pad and a stack of forms
    for j in range(4):
        box('F0EEE4', (-1.6, 0.9, 1.66 + j * 0.04), (1.0, 1.3, 0.03), r, rot=(0, 0, 0.1 * (rnd(j, 93) - 0.5)))
    return out


def extend(S, name, fn):
    """Add props to one of the Short's sets without touching its code: built at the set's origin, linked to its collection."""
    old = set(bpy.data.objects)
    out = fn(empty(ORG[name]))
    for o in set(bpy.data.objects) - old:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        S['colls'][name].objects.link(o)
    return out


def ext_ctrl(r):
    """A panel on the control-room wall: three lamps and the lever that switches them."""
    out = dict(swm=[])
    box('39424C', (-9.55, -2.0, 3.3), (0.6, 3.6, 3.8), r)
    for j in range(7):
        box('FF7A1A' if j % 2 else '15171C', (-9.23, -3.56 + j * 0.52, 5.0), (0.04, 0.52, 0.22), r)
    for j in range(3):
        m = own_mat('swlamp%d' % j, 'FFB000', 0.3, 12.0)
        use(add('cylinder', 'FFB000', (-9.22, -3.0 + j * 1.0, 4.3), rot=(0, PI / 2, 0), radius=0.3, depth=0.1, vertices=10, parent=r), m)
        out['swm'].append(m)
    box('22252C', (-9.22, -2.0, 2.7), (0.06, 0.5, 1.3), r)
    out['lever'] = lv = mov(empty((-9.2, -2.0, 2.7), r))
    box('B9C0CA', (0.3, 0, 0), (0.6, 0.12, 0.12), lv, rough=0.3)
    add('ico_sphere', 'D8362A', (0.62, 0, 0), radius=0.16, subdivisions=1, parent=lv)
    return out


def ext_xray(r):
    """A plinth beside the schematic head, so Rook can stand level with the line."""
    pl = mov(empty((0, 0, -300), r))                                                        # parked below the set until a shot wants it
    box('14283E', (6.4, -6.6, -0.35), (2.6, 2.6, 3.2), pl, emit=0.15)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('49C8FF', (6.4 + sx * 1.3, -6.6 + sy * 1.3, -0.35), (0.05, 0.05, 3.2), pl, emit=4.0)
    for sx in (-1, 1):
        box('49C8FF', (6.4 + sx * 1.3, -6.6, 1.25), (0.05, 2.6, 0.05), pl, emit=4.0)
        box('49C8FF', (6.4, -6.6 + sx * 1.3, 1.25), (2.6, 0.05, 0.05), pl, emit=4.0)
    return dict(plinth=pl)


_build0, _reset0, _finish0 = build, reset, finish


def build():
    S = _build0()
    for name, fn in (('town', set_town), ('air', set_air), ('corr', set_corr), ('road', set_road), ('wcor', set_wcor), ('office', set_office)):
        S['colls'][name], S[name] = group(name, fn)
    S['ctrlx'] = extend(S, 'ctrl', ext_ctrl)
    mov(S['ring']['gapbeam'])                                                               # so the thumbnail can thin it and reset() puts it back
    S['xrayx'] = extend(S, 'xray', ext_xray)
    S['doc2'] = K.Rig(DOC2, man_head('E0B898', '3A2A20', 'x'))
    add('cone', 'E4E8E2', (0, 0, -0.3), radius1=0.42, radius2=0.33, depth=0.8, vertices=8, parent=S['doc2'].body)
    S['clk'] = K.Rig(CLK, man_head('DDB090', '5A4030', 'x'))
    add('cube', 'E8E4D8', (0, -0.31, 0.8), scale=(0.26, 0.04, 0.4), size=1, parent=S['clk'].body)
    S['b96'] = K.Rig(B96, man_head(SKIN, '8E8E92', 'x'))                                    # 1996: the same man, older, in a jacket
    add('cube', 'C8CCD4', (0, -0.31, 0.8), scale=(0.22, 0.04, 0.44), size=1, parent=S['b96'].body)
    S['cast'] += [S['doc2'], S['clk'], S['b96']]
    S['dossier'] = ds = mov(empty(FAR))
    box('D8B870', (0, 0, 0), (1.1, 1.4, 0.06), ds)
    box('F0EEE4', (0.03, 0, 0.04), (0.95, 1.25, 0.04), ds)
    S['case'] = cs = mov(empty(FAR))                                                        # his tool case
    box('5A3E2A', (0, 0, 0), (0.9, 0.3, 0.6), cs)
    box('B9C0CA', (0, 0, 0.36), (0.4, 0.08, 0.1), cs, rough=0.3)
    return S


def reset(S):
    _reset0(S)
    tint(S['ring']['gapbeam'].data.materials[0], 'D6E6FF', 60.0)
    for m in S['corr']['lampm']:
        tint(m, '3A1412', 0.0)
    S['corr']['tunl'].data.energy = 0
    for m in S['ctrlx']['swm']:
        tint(m, 'FFB000', 12.0)
    W_ = S['wcor']
    tint(W_['panem'], '1A2A4A', 0.6)
    W_['winl'].data.energy = 0
    for l in W_['tops']:
        l.data.energy = 300
    O = S['office']
    O['top'].data.energy = 900
    O['lampl'].data.energy = 350
    O['winl'].data.energy = 700
    S['face'].update(doc2='calm', clk='calm', b96='calm')
    S['jaw'].update(doc2=0.0, clk=0.0, b96=0.0)


def finish(S, t):
    _finish0(S, t)
    for j, who in enumerate(('doc2', 'clk', 'b96')):
        x = S[who].extra
        k = dict(calm=1.0, wide=1.7, shut=0.08, tired=0.5, warm=0.85, squint=0.6).get(S['face'][who], 1.0)
        bl = (t * 0.31 + 0.19 * j + 0.5) % 1 < 0.03
        for i, ey in enumerate(x['eyes']):
            kk = 0.1 if bl else k
            if who == 'b96' and i == 1:
                kk = 0.8
            ey.scale = (0.1, 0.03, 0.075 * kk)
        x['jaw'].rotation_euler = (S['jaw'][who], 0, 0)


def hold(S, prop, rig, side=0, loc=(0.0, -0.12, -0.55), rot=(1.0, 0, 0)):
    prop.parent = rig.el[side]
    prop.location, prop.rotation_euler = loc, rot


def day(S, name, skyc='8FB0D0', sun=3.2, fk=2.4, sdir=(-0.45, -0.55, 0.7), sunc='FFF0DC'):
    return env(S, name, skyc, sun=sun, sunc=sunc, sdir=sdir, fk=fk, skyk=1.0)


# ---------------------------------------------------------------- new shots: where it happened
def town_wide(S, k, t, lt):
    A = day(S, 'town')
    y = lerp(-13.0, -8.5, k)
    S['rook'].place(A(1.4, y, 0), PI)
    S['rook'].apply(walk(lt, 1.5))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(5.2, 4.2, k), lerp(-23.0, -20.5, k), lerp(3.4, 2.8, k)), A(0.4, 6.0, 4.6), 30, fcol='FFF0DC')


def town_gate(S, k, t, lt):
    A = day(S, 'town')
    rp = (1.6, 13.2, 0.0)
    turn = ease((lt - 0.9) / 0.4)
    S['rook'].place(A(*rp), lerp(PI - 0.2, 0.55, turn))
    pop = ease(lt / 0.25) * (1 - ease((lt - 0.45) / 0.25))
    S['rook'].apply(blend(blend(P('stand', head=(-0.35, 0.0)), P('stand', aL=(0.9, 0.5, 2.3, 0.6), aR=(0.9, 0.5, 2.3, 0.6), head=(-0.3, 0.0)), pop),
                          P('point', aR=(1.2, 1.3, 0.2), head=(0.0, -0.5)), turn))
    S['face']['rook'] = 'deadpan'
    S['town']['boom'].rotation_euler = (0, -1.15 * ease((lt - 0.3) / 0.9), 0)
    cam(S, A(lerp(5.4, 4.6, k), lerp(7.6, 8.6, k), 2.3), A(0.6, 15.5, 3.4), 30, fcol='FFF0DC')


def ring_air(S, k, t, lt):
    """The whole ring from the air: a grassed bank in the forest. A bright dot goes round to show what it is for."""
    A = day(S, 'air', sun=3.6, fk=0.0)
    a0 = -0.5 + 0.5 * k if S['prm'].get('v') != 2 else 1.6 - 0.4 * k
    d, hgt = (150, 84) if S['prm'].get('v') != 2 else (130, 55)
    a = lt * 2.4
    S['air']['mark'].location = (70 * math.sin(a), -70 * math.cos(a), 4.6)
    cam(S, A(d * math.sin(a0), -d * math.cos(a0), lerp(hgt, hgt - 14, k)), A(0, -6, 0), 28)


def corr(S, lit=0.0):
    A = env(S, 'corr', fk=2.2)
    cols = ('D8362A', 'FFB000', 'D8362A')
    for j, m in enumerate(S['corr']['lampm']):
        tint(m, cols[j] if lit > 0 else '3A1412', 16.0 * lit)
    return A


def corr_walk(S, k, t, lt):
    A = corr(S)
    y = lerp(-7.0, 0.5, k)
    S['bug'].place(A(-0.6, y, 0), PI)
    S['bug'].apply({**walk(lt, 1.8), 'aR': (0.15, 0.1, 0.2)})
    hold(S, S['case'], S['bug'], 1, (0.0, 0.0, -0.95), (0, 0, PI / 2))
    S['rook'].place(A(1.5, y - 3.2, 0), PI)
    S['rook'].apply(walk(lt + 0.3, 1.8))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(3.0, 2.6, k), y - 8.4, lerp(3.3, 2.9, k)), A(0.0, y + 6.0, 3.3), 26, fcol='FFF0DC')


def door_open(S, k, t, lt):
    A = corr(S)
    op = ease((lt - 0.3) / 0.9)
    S['corr']['hinge'].rotation_euler = (0, 0, -1.25 * op)
    S['corr']['tunl'].data.energy = 2500 * op
    bp = (1.0 - 0.5 * op, 15.6 - 0.9 * op, 0.0)
    S['bug'].place(A(*bp), PI + 0.25)
    S['bug'].apply(blend(P('stand', aL=(1.3, 0.1, 0.4), aR=(0.15, 0.1, 0.2), lean=0.15), P('stand', aL=(0.9, 0.3, 1.2), aR=(0.15, 0.1, 0.2), lean=-0.05), op))
    hold(S, S['case'], S['bug'], 1, (0.0, 0.0, -0.95), (0, 0, PI / 2))
    cam(S, A(lerp(3.1, 2.6, k), lerp(8.2, 9.4, k), lerp(2.2, 2.6, k)), A(0.0, 17.0, 3.6), 26, fcol='FFF0DC')


def door_lamps(S, k, t, lt):
    """The panel of warning lamps over the door, dark. v=2: Rook raps on one of them with a knuckle."""
    A = corr(S)
    v2 = S['prm'].get('v') == 2
    rp = (2.3, 14.6, 0.0)
    S['rook'].place(A(*rp), facing(rp, (0.6, 9.0, 0)) if not v2 else PI - 0.5)
    look = ease((lt - 1.0) / 0.3)
    tap = max(0.0, math.sin(lt * 10))
    if v2:
        S['rook'].apply(P('stand', aR=(2.75 + 0.1 * tap, 0.2, 0.25 + 0.3 * (1 - tap)), head=(-0.5, 0.2)))
    else:
        S['rook'].apply(blend(P('reach', aR=(2.7, 0.35, 0.05), head=(-0.5, 0.5)), P('shrug', head=(0.0, 0.25 * math.sin(lt * 7))), look))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-1.6, -0.8, k), lerp(8.6, 9.8, k), lerp(1.7, 2.0, k)), A(0.9, 17.0, lerp(4.4, 4.7, k)), 26, fcol='FFF0DC')


def switch_off(S, k, t, lt):
    """Earlier, by one account: the warning lamps are switched off for another experiment."""
    A, C = ctrl(S)
    dials(S, t, 0.3)
    X = S['ctrlx']
    flip = ease((lt - 0.8) / 0.18)
    for j, m in enumerate(X['swm']):
        on = lt < 0.86 + j * 0.12
        tint(m, 'FFB000' if on else '3A2A10', 12.0 if on else 0.0)
    X['lever'].rotation_euler = (0, lerp(-0.6, 0.6, flip), 0)
    op = (-7.9, -2.0, 0.0)
    S['op'].place(A(*op), -PI / 2)
    S['op'].apply(blend(P('stand', aR=(0.4, 0.1, 0.5)), P('stand', aR=(lerp(1.5, 1.2, flip), 0.0, 0.25), head=(0.0, 0.0)), (lt - 0.2) / 0.4))
    rp = (-8.2, 1.5, 0.0)
    S['rook'].place(A(*rp), facing(rp, (-7.0, -3.0, 0)))
    S['rook'].apply(P('cross', head=(0.0, 0.3 * ease((lt - 1.3) / 0.3))))
    S['face']['rook'] = 'deadpan'
    S['hat_tip'] = 0.5 * ease((lt - 1.3) / 0.3)
    cam(S, A(lerp(-3.2, -4.2, k), lerp(2.6, 1.6, k), lerp(3.6, 3.3, k)), A(-8.8, -2.6, 3.4), 28, fill=1.5, fcol='FFE8D0')


# ---------------------------------------------------------------- new shots in the tunnel
def pipe_cu(S, k, t, lt):
    """Rook peers into the gap in the pipe. Nothing to see: the beam is invisible."""
    A = ring(S, 1.0, fk=2.6)
    rp = (-0.2, -1.7, 0.0)
    S['rook'].place(A(*rp), PI)
    S['rook'].apply(P('stand', lean=0.45, aL=(0.5, 0.2, 0.6), aR=(1.2, 0.3, 1.9, 0.5), head=(-0.3, 0.55 * math.sin(lt * 2.2))))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-1.3, -0.5, k), lerp(2.3, 1.9, k), lerp(2.2, 2.4, k)), A(-0.1, -1.3, 2.75), 30, fcol='FFF0DC')


def rook_draw(S, k, t, lt):
    """'I have drawn it in for you': Rook sweeps an arm along the pipe and the line of light follows."""
    A = ring(S, 0.75, fk=2.4)
    front = lerp(-0.62, 0.62, ease((lt - 0.5) / 1.6))
    beam_to(S, A, front, 0.25)
    rp = (5.0, -4.4, 0.0)
    sw = ease((lt - 0.4) / 1.5)
    S['rook'].place(A(*rp), PI + lerp(0.9, -0.9, sw))
    S['rook'].apply(P('point', aR=(1.5, 0.15, 0.05), head=(-0.05, 0.0)))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(9.6, 9.0, k), lerp(-8.6, -8.0, k), lerp(3.4, 3.0, k)), A(1.6, -0.8, 2.5), 24, fcol='FFF0DC')


def bug_tools(S, k, t, lt):
    """He crouches at the dead instrument with his tool case open beside him."""
    A = ring(S, 0.9, fk=2.6)
    tint(S['ring']['faultm'], '2A1414', 0.0)
    bp = (1.5, -2.0, 0.0)
    S['bug'].place(A(*bp), PI)
    w = math.sin(lt * 8)
    S['bug'].apply(P('stand', lL=(1.5, 2.0), lR=(0.35, 1.75), lift=-0.72, lean=0.35, aL=(1.1, 0.1, 0.7), aR=(1.25 + 0.08 * w, 0.0, 0.6 - 0.1 * w), head=(-0.1, 0.0)))
    S['face']['bug'] = 'squint'
    S['case'].location = A(2.9, -1.9, 0.3)
    S['case'].rotation_euler = (0, 0, 0.4)
    rp = (-1.0, -4.3, 0.0)
    S['rook'].place(A(*rp), facing(rp, (1.5, -1.0, 0)))
    S['rook'].apply(P('cross', head=(0.15, 0.0)))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(5.4, 4.6, k), lerp(-4.6, -4.0, k), lerp(1.5, 1.8, k)), A(0.9, -2.2, 1.9), 30, fcol='FFF0DC')


def bug_rise(S, k, t, lt):
    """Afterwards: he straightens up and puts a hand to the back of his head. No pain."""
    A = ring(S, 0.8, fk=2.6)
    tint(S['ring']['faultm'], '2A1414', 0.0)
    up = ease(lt / 0.7)
    S['bug'].place(A(*BUGPOS), PI / 2 - 0.9 * ease((lt - 0.5) / 0.6))
    S['bug'].apply(blend(P('stand', **LEAN), P('stand', aR=(0.25, 1.6, 2.35, -1.2), head=(0.1, -0.2)), up))
    S['face']['bug'] = 'squint' if lt < 0.6 else 'calm'
    cam(S, A(lerp(1.2, 0.6, k), lerp(-5.6, -4.8, k), lerp(2.5, 2.8, k)), A(-0.9, 0.0, 2.6), 34, fcol='FFF0DC')


def rook_yell(S, k, t, lt):
    """'I would have been heard in Moscow.'"""
    A = ring(S, 0.9, fk=2.6)
    tint(S['ring']['faultm'], '2A1414', 0.0)
    S['bug'].place(A(*BUGPOS), -0.3)
    S['bug'].apply(P('stand', head=(0.0, 0.3)))
    rp = (1.6, -4.6, 0.0)
    hop = abs(math.sin(lt * 9)) * 0.35
    S['rook'].place(A(rp[0], rp[1], hop), 0.3 + 0.2 * math.sin(lt * 6))
    S['rook'].apply(P('stand', aL=(2.5, 0.7, 1.7, 0.4), aR=(2.5, 0.7, 1.7, 0.4), head=(-0.35, 0.3 * math.sin(lt * 12)), lL=(0.3, 0.6), lR=(-0.2, 0.3)))
    S['face']['rook'] = 'shocked'
    feather(S, A(rp[0] + 0.4, rp[1] - 0.4, 3.4), lt, 0.1, 3)
    cam(S, A(lerp(3.6, 3.2, k), lerp(-9.2, -8.4, k), 2.2), A(0.9, -3.6, 2.9), 32, fcol='FFF0DC')


def ctrl_pass(S, k, t, lt):
    """He walks out past the operator and says nothing. Rook, behind him, cannot believe it."""
    A, C = ctrl(S)
    dials(S, t, 0.4)
    S['op'].place(A(-3.6, 3.6, 0.5), PI)
    S['op'].apply(P('sit', aL=(1.25, 0.1, 0.5), aR=(1.1 + 0.25 * math.sin(lt * 5), 0.25, 0.6), lean=0.3, head=(0.1, 0.2 * math.sin(lt * 2))))
    x = lerp(6.0, -2.5, k)
    S['bug'].place(A(x, -0.6, 0), -PI / 2)
    S['bug'].apply({**walk(lt, 1.6), 'aR': (0.15, 0.1, 0.2)})
    hold(S, S['case'], S['bug'], 1, (0.0, 0.0, -0.95), (0, 0, PI / 2))
    rp = (x + 3.4, -1.6, 0.0)
    S['rook'].place(A(*rp), -PI / 2 + 0.2)
    S['rook'].apply({**walk(lt + 0.4, 1.6), 'aL': (0.3, 0.75, 1.5, -0.9), 'aR': (0.3, 0.75, 1.5, -0.9), 'head': (0.0, -0.9 * (0.5 + 0.5 * math.sin(lt * 3.5)))})
    S['face']['rook'] = 'shocked'
    cam(S, A(lerp(-5.6, -6.6, k), lerp(-6.6, -6.0, k), lerp(3.4, 3.0, k)), A(lerp(2.0, 0.0, k), 1.6, 2.7), 31, fill=1.5, fcol='FFE8D0')


def bug_coord(S, k, t, lt):
    """Years on: he stands at the ring diagram directing the work. The left side of his face is still."""
    A, C = ctrl(S)
    dials(S, t, 0.6)
    S['op'].place(A(-3.6, 3.6, 0.5), PI)
    S['op'].apply(P('sit', aL=(1.25, 0.1, 0.5), aR=(1.2, 0.2, 0.5), lean=0.2, head=(0.0, -0.75)))
    bp = (1.2, 4.0, 0.0)
    S['bug'].place(A(*bp), PI - 0.5 + 0.9 * ease((lt - 1.0) / 0.5))
    S['left']['bug'] = 'still'
    S['bug'].apply(P('stand', aR=(1.9, 0.2, 0.15), aL=(0.8, 0.0, 1.3, 0.7), head=(-0.1, 0.0)))
    hold(S, S['clip'], S['bug'], 0)
    rp = (5.6, 1.4, 0.0)
    S['rook'].place(A(*rp), facing(rp, (-1.0, -4.0, 0)))
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.0, 0.5)))
    S['face']['rook'] = 'warm'
    cam(S, A(lerp(-1.0, 0.4, k), lerp(-4.4, -3.6, k), lerp(3.6, 3.2, k)), A(2.6, 4.6, 3.3), 33, fill=1.5, fcol='FFE8D0')


# ---------------------------------------------------------------- new shots: that night, the road, the wait
def swell_cu(S, k, t, lt):
    A = study(S)
    S['bug'].place(A(-0.5, 0.1, 0.5), 0.0)
    vis(S['bug'].extra['swell'], True)
    S['left']['bug'] = 'swollen'
    S['bug'].apply(P('sit', aL=(0.7, -0.1, 1.5, 1.0), aR=(0.6, 0.95, 2.3, 0.1), lean=0.12, head=(0.1, -0.25 + 0.1 * math.sin(lt * 1.5))))
    S['face']['bug'] = 'tired'
    cam(S, A(lerp(1.0, 0.5, k), lerp(-3.4, -2.9, k), lerp(2.6, 2.5, k)), A(-0.4, 0.0, 2.42), 55, fcol='FFE0C0')


def road(S):
    A = env(S, 'road', '0E1730', sun=0.8, sunc='9AB4FF', sdir=(0.3, -0.5, 0.8), fk=5.0, skyk=1.0)
    return A


def road_van(S, k, t, lt):
    A = road(S)
    vx = lerp(-34.0, -14.0, k)
    v = S['road']['van']
    v.location = (vx, -1.6, 0.0 + 0.03 * math.sin(lt * 23))
    cam(S, A(vx + lerp(7.5, 5.5, k), -11.5, lerp(2.2, 2.8, k)), A(vx + 0.5, -1.6, 1.9), 30, fcol='BFD0FF')


def rook_road(S, k, t, lt):
    A = road(S)
    v = S['road']['van']
    v.location = (lerp(34.0, 70.0, k), -1.6, 0.0)
    rp = (30.0, -7.0, 0.0)
    S['rook'].place(A(*rp), PI / 2 + 0.5)
    S['hat_off'] = ease(lt / 0.5)
    S['rook'].apply(blend(P('stand'), hat_hold(head=(0.05, -0.3)), lt / 0.5))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(25.0, 26.0, k), lerp(-11.6, -11.0, k), 2.7), A(48.0, -3.0, 3.2), 30, fcol='BFD0FF')


def wcor(S, dawn=0.0):
    A = env(S, 'wcor', fk=1.0)
    W_ = S['wcor']
    tint(W_['panem'], '1A2A4A' if dawn < 0.5 else 'FFD9A0', lerp(0.6, 2.0, dawn))
    W_['winl'].data.energy = 320 * dawn
    for l in W_['tops']:
        l.data.energy = lerp(300, 150, dawn)
    W_['hand'].rotation_euler = (0, S['time'] * 0.8, 0)
    return A


def wcor_docs(S, k, t, lt):
    """Two doctors outside his door. One shows the chart; the other spreads his hands."""
    S['time'] = t
    A = wcor(S)
    S['doc'].place(A(-1.5, 0.8, 0), -PI / 2 - 0.2)
    S['doc'].apply(P('stand', aL=(0.8, 0.0, 1.3, 0.7), aR=(0.9, 0.3, 0.9), head=(0.15, 0.3 * math.sin(lt * 5.5))))
    hold(S, S['clip'], S['doc'], 0)
    S['face']['doc'] = 'tired'
    S['doc2'].place(A(1.0, 0.6, 0), PI / 2 + 0.2)
    S['doc2'].apply(blend(P('stand', aL=(0.4, 0.1, 0.9), aR=(0.4, 0.1, 0.9)), P('shrug', head=(0.1, 0.0)), (lt - 0.5) / 0.4))
    rp = (4.6, -2.75, 0.5)
    S['rook'].place(A(*rp), PI)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(0.1, 0.55)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-6.4, -5.6, k), lerp(-2.6, -2.2, k), lerp(3.1, 2.8, k)), A(1.2, 0.0, 2.7), 26, fill=1.4, fcol='E8F0FF')


def rook_waits(S, k, t, lt):
    """Rook on the bench, hat in his hands, while the windows go from night to morning."""
    S['time'] = t
    A = wcor(S, dawn=ease(k * 1.2))
    rp = (4.6, -2.75, 0.5)
    S['rook'].place(A(*rp), PI)
    S['hat_off'] = 1.0
    S['rook'].apply(P('sit', aL=(0.75, -0.25, 1.75, 1.1), aR=(0.75, -0.25, 1.75, 1.1), head=(lerp(0.45, 0.1, ease((k - 0.6) / 0.3)), 0.0)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(1.6, 2.6, k), lerp(2.2, 1.6, k), lerp(2.3, 2.6, k)), A(4.5, -2.6, 2.6), 28, fill=1.0, fcol='E8F0FF')


def bug_sits(S, k, t, lt):
    """Alive: propped up in bed while the doctor, astonished, checks the chart again."""
    S['time'] = t
    A = clinic(S, warm=True)
    S['pat'].place(A(0, 2.0, 1.2), 0.0)
    S['pat'].apply(P('sit', lL=(1.5, 0.05), lR=(1.5, 0.05), aL=(0.5, 0.2, 0.6), aR=(0.5, 0.2, 0.6), lean=-0.1, head=(0.0, 0.5 * ease((lt - 0.8) / 0.4))))
    vis(S['pat'].extra['swell'], True)
    S['left']['pat'] = 'swollen'
    S['face']['pat'] = 'calm'
    dp = (3.3, 1.2, 0.0)
    S['doc'].place(A(*dp), facing(dp, (0, 2.0, 0)))
    S['doc'].apply(P('stand', aL=(0.8, 0.0, 1.3, 0.7), aR=(0.8, 0.2, 1.9, 0.3), head=(0.25 - 0.3 * ease((lt - 0.6) / 0.3), 0.0)))
    hold(S, S['clip'], S['doc'], 0)
    S['face']['doc'] = 'wide'
    rp = (-3.0, 0.2, 0.0)
    S['rook'].place(A(*rp), facing(rp, (0.5, 2.0, 0)))
    S['rook'].apply(P('stand', aR=(1.1, 0.25, 2.3, 0.5), aL=(0.3, 0.2, 0.5), head=(-0.1, 0.0)))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(-3.4, -2.6, k), lerp(-4.8, -4.2, k), lerp(4.9, 4.5, k)), A(0.3, 1.7, 2.9), 28, fcol='FFE8C8')


# ---------------------------------------------------------------- new shots: why he lived, and what it cost
def xr(S, fk=1.6):
    A = env(S, 'xray', '02040A', fk=fk)
    for (o, m, a, b) in S['xray']['line']:
        seg(o, a, b, 0.11 if not m.name.endswith('1') else 0.15)
        tint(m, 'FFE2B0' if m.name.endswith('1') else 'D6E6FF', 40.0 * (0.7 + 0.3 * math.sin(S['time'] * 9)))
    return A


def beam_thin(S, k, t, lt):
    """From straight above: one thin line across the head."""
    S['time'] = t
    A = xr(S, 0.0)
    a = lerp(-0.25, 0.25, k)
    cam(S, A(0.6 + 3.0 * math.sin(a), -1.0 - 3.0 * math.cos(a), lerp(34, 27, k)), A(0.4, 0.0, 4.0), 30)


def rook_xray(S, k, t, lt):
    """Rook on a plinth beside the schematic head, pointing along the line where it comes out."""
    S['time'] = t
    A = xr(S, 6.0)
    S['xrayx']['plinth'].location = (0, 0, 0)
    rp = (6.4, -6.6, 1.25)
    S['rook'].place(A(*rp), facing(rp, (1.0, -7.5, 0)) + 0.5 * ease((lt - 1.2) / 0.4))
    tap = 0.5 + 0.5 * math.sin(lt * 9)
    S['rook'].apply(blend(P('point', aR=(1.5, 0.1, 0.05), head=(0.0, 0.0)), P('stand', aR=(1.1, 0.25, 2.25 + 0.2 * tap, 0.5), aL=(0.3, 0.2, 0.5), head=(-0.1, 0.3)),
                          (lt - 1.2) / 0.4))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(12.0, 10.8, k), lerp(-13.6, -12.6, k), lerp(4.2, 3.9, k)), A(4.2, -5.0, 3.6), 30, fill=1.5, fcol='DCEBFF')


def bug_rest(S, k, t, lt):
    """The seizures, shown only as this: he has had to sit down, a hand on the desk, and Rook stays with him."""
    A = study(S, night=False)
    S['bug'].place(A(0, 0.1, 0.5), 0.0)
    S['left']['bug'] = 'still'
    S['bug'].apply(P('sit', aL=(1.0, 0.2, 0.9), aR=(0.5, 0.6, 2.2, 0.2), lean=0.3, head=(0.5, -0.15)))
    S['face']['bug'] = 'shut'
    rp = (2.0, 0.9, 0.0)
    S['rook'].place(A(*rp), facing(rp, (0.0, -1.5, 0)))
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.25, 0.35), lean=0.12))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(-2.6, -2.0, k), lerp(-3.9, -3.4, k), lerp(3.2, 3.0, k)), A(0.9, 0.4, 2.5), 36, fcol='FFF0DC')


# ---------------------------------------------------------------- new shots: the office
def office(S, dim=False):
    A = env(S, 'office', fk=2.2 if not dim else 1.2)
    O = S['office']
    if dim:
        O['top'].data.energy = 300
        O['winl'].data.energy = 90
        O['lampl'].data.energy = 700
    return A


def file_shut(S, k, t, lt):
    """The decade of secrecy: a folder goes into the cabinet and the drawer shuts. Rook tries the handle."""
    A = office(S, dim=True)
    shut = ease((lt - 0.35) / 0.35)
    S['office']['drawer'].location = (-7.4, lerp(1.9, 3.5, shut), 4.15)
    rp = (-6.6, 0.7, 0.0)
    S['rook'].place(A(*rp), facing(rp, (-7.4, 3.0, 0)))
    pull = max(0.0, math.sin((lt - 0.9) * 7)) if lt > 0.9 else 0.0
    S['rook'].apply(blend(P('stand', head=(-0.2, 0.0)), P('stand', aR=(1.75, 0.0, 0.5 + 0.5 * pull), head=(-0.15, 0.0), lean=0.1 - 0.15 * pull), (lt - 0.7) / 0.25))
    S['face']['rook'] = 'deadpan'
    cam(S, A(lerp(-4.2, -4.8, k), lerp(-5.4, -4.6, k), lerp(3.2, 3.5, k)), A(-7.0, 2.2, 3.3), 30, fill=1.6, fcol='FFE8D0')


def office_claim(S, k, t, lt):
    """1996: older now, in a jacket, he slides his papers across a counter."""
    A = office(S)
    bp = (-0.4, -1.3, 0.0)
    S['b96'].place(A(*bp), PI)
    push = ease((lt - 0.5) / 0.6)
    S['b96'].apply(blend(P('stand', aR=(0.7, 0.0, 1.0)), P('stand', aR=(0.95, 0.0, 0.3), lean=0.2), push))
    S['dossier'].location = A(0.1, lerp(-0.1, 0.75, push), 1.67)
    S['dossier'].rotation_euler = (0, 0, 0.1)
    S['clk'].place(A(0.6, 2.5, 0), 0.0)
    S['clk'].apply(P('stand', aL=(0.7, 0.0, 1.2), aR=(0.7, 0.0, 1.2), head=(0.3, 0.0)))
    rp = (3.6, -3.0, 0.0)
    S['rook'].place(A(*rp), facing(rp, (0.0, 1.0, 0)))
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(0.0, 0.3)))
    S['face']['rook'] = 'calm'
    cam(S, A(lerp(-5.6, -4.8, k), lerp(-5.8, -5.2, k), lerp(3.6, 3.3, k)), A(0.6, 0.4, 2.8), 28, fcol='FFF0DC')


def clerk_no(S, k, t, lt):
    """Over his shoulder: the clerk shakes his head and slides the papers back."""
    A = office(S)
    bp = (-0.4, -1.3, 0.0)
    S['b96'].place(A(*bp), PI)
    S['b96'].apply(P('stand', aR=(0.6, 0.0, 0.6), head=(0.1, 0.0)))
    back = ease((lt - 0.9) / 0.6)
    S['dossier'].location = A(0.1, lerp(0.75, -0.1, back), 1.67)
    S['dossier'].rotation_euler = (0, 0, 0.1)
    S['clk'].place(A(0.6, 2.5, 0), 0.0)
    S['clk'].apply(blend(P('stand', aL=(0.7, 0.0, 1.2), aR=(0.7, 0.0, 1.2), head=(0.25, 0.4 * math.sin(lt * 6.5))), P('stand', aR=(0.95, 0.0, 0.3), aL=(0.7, 0.0, 1.2), lean=0.2,
                         head=(0.2, 0.0)), back))
    S['face']['clk'] = 'tired'
    cam(S, A(lerp(-2.8, -2.4, k), lerp(-4.6, -4.1, k), lerp(3.7, 3.5, k)), A(0.5, 2.2, 2.6), 34, fcol='FFF0DC')


def rook_office(S, k, t, lt):
    """'I have no joke for that.' Rook alone at the counter with the returned papers, hat in hand."""
    A = office(S)
    S['dossier'].location = A(0.1, -0.1, 1.67)
    S['dossier'].rotation_euler = (0, 0, 0.1)
    S['clk'].place(A(-3.4, 4.6, 0), PI)
    S['clk'].apply(P('stand', aL=(1.0, 0.0, 0.8), aR=(1.0, 0.0, 0.8)))
    rp = (1.0, -1.5, 0.0)
    S['rook'].place(A(*rp), lerp(PI - 0.6, 0.55, ease((lt - 0.7) / 0.6)))
    S['hat_off'] = 1.0
    S['rook'].apply(hat_hold(head=(lerp(0.4, 0.1, ease((lt - 0.7) / 0.5)), 0.0)))
    S['face']['rook'] = 'sad'
    cam(S, A(lerp(4.4, 3.6, k), lerp(-5.4, -4.8, k), lerp(2.3, 2.5, k)), A(0.6, -0.9, 2.15), 34, fcol='FFF0DC')


HOST |= {'town_wide', 'town_gate', 'corr_walk', 'door_lamps', 'switch_off', 'pipe_cu', 'rook_draw', 'bug_tools', 'rook_yell', 'ctrl_pass', 'bug_coord',
         'rook_road', 'wcor_docs', 'rook_waits', 'bug_sits', 'rook_xray', 'bug_rest', 'file_shut', 'office_claim', 'rook_office'}
SHOTS3D.update({f.__name__: f for f in (
    town_wide, town_gate, ring_air, corr_walk, door_open, door_lamps, switch_off, pipe_cu, rook_draw, bug_tools, bug_rise, rook_yell, ctrl_pass,
    bug_coord, swell_cu, road_van, rook_road, wcor_docs, rook_waits, bug_sits, beam_thin, rook_xray, bug_rest, file_shut, office_claim, clerk_no,
    rook_office)})


def _orbit(f):
    """prm "orb": [degrees, dolly, rise] swings the camera round its own look-at point over the length of the shot,
    so a quiet shot is never a still picture."""
    def g(S, k, t, lt):
        f(S, k, t, lt)
        o = S['prm'].get('orb')
        if o:
            deg, dolly, rise = (list(o) + [0, 0])[:3]
            c, tg = S['camrig'].location, S['camtgt'].location
            a = math.radians(deg) * (k - 0.5)
            m = 1 - dolly * (k - 0.5)
            dx, dy = c[0] - tg[0], c[1] - tg[1]
            S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m,
                                    c[2] + rise * (k - 0.5))
    g.__name__ = f.__name__
    return g


SHOTS3D = {name: _orbit(f) for name, f in SHOTS3D.items()}


def photo_thumb(S, k, t, lt):
    """Thumbnail picture: side on in the tunnel, the drawn beam crossing the gap at his head, Rook throwing his arms up."""
    A = ring(S, 0.3, fk=3.0)
    beam_to(S, A, 0.5, 0.1)
    g = S['ring']['gapbeam']
    g.scale = (0.45, 0.45, 1.0)
    tint(g.data.materials[0], 'D6E6FF', 14.0)
    S['glow'].location = A(0.9, -1.4, 2.6)
    bug_in_gap(S, A, face='wide', nod=0.1)
    rp = (-1.7, -2.6, 0.0)
    S['rook'].place(A(*rp), 0.45)
    S['rook'].apply(P('stand', **{**ALARM, 'head': (0.0, -0.5)}))
    S['face']['rook'] = 'shocked'
    S['hat_off'] = 0.0
    cam(S, A(1.3, -8.6, 2.5), A(1.3, 0, 2.3), 30, fill=1.3, fcol='FFF0DC')


STILLS['thumb'] = photo_thumb
