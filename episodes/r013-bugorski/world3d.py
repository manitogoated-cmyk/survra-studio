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
    front = lerp(-0.75, -0.02, ease(k) * 0.6 + k * 0.4)
    beam_to(S, A, front, 1.2)
    bug_in_gap(S, A)
    cam(S, A(*arc(lerp(0.105, 0.085, k), 4.4, lerp(1.2, 1.6, k))), A(*arc(-0.05, 0.0, 2.3)), 24, roll=-0.06, fcol='BFD4FF')


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
        C['win'].data.energy = 600
        S['fillk'] = 0.9
        C['win'].data.color = K.hexc('FFD9A0')[:3]
        tint(C['panem'], 'FFE0B0', 3.5)
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
