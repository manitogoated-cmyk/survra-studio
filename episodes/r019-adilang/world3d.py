"""Case 019 in 3D - Aldi Novel Adilang, 2018. A 19-year-old lamp keeper lived alone on a rompong, a floating
fish trap shaped like a small hut, moored by a long rope about 125 km off North Sulawesi, Indonesia. On 14 July
2018 the rope parted in high wind and the hut, which had no engine and no paddle, was blown out to sea. He was
picked up on 31 August in waters off Guam by the Panama-flagged bulk carrier MV Arpeggio, after more than ten
other ships had passed without seeing him.

Built for this story only: one open ocean (a wave mesh that is re-shaped every frame, under five skies), the
hut on its raft of planks and drums, and a bulk carrier with a deck, a rail and a rope ladder.

Everything is a generic low-poly reconstruction, not a model of the real rompong or the real ship. The young
man and the crew are simple figures and nobody's likeness is attempted. No flag, name, logo or lettering
appears on the ship, the hut or the clothes."""
import math

import bpy
import numpy as np
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light, walk

PI = math.pi
AWAY = (0, 0, -3000)
HOST = {'boy_face', 'rook_roof', 'no_engine', 'fishing', 'cook', 'wave_cloth', 'sail_past', 'cry', 'call', 'turn', 'jump', 'alive',
        'rook_wrong', 'signoff'}
CAMFILL = {'*': 90, 'snap_wide': 320, 'rope_close': 200, 'drift_off': 500, 'boy_face': 160, 'rook_roof': 220, 'supplies': 220,
           'grab_radio': 160, 'cry': 150, 'cook': 90, 'dawn_empty': 0, 'ship_away': 0, 'turn': 60}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
WOOD, WOODD, WOODL = '8E6B43', '5E4428', 'B08A58'
BAMBOO, THATCH, THATCHD = 'B89E5E', 'C9AB62', '8C6E36'
DRUM, ROPE = '2B6CA8', 'D8C8A0'
SKIN = 'A8704C'
DZ = 0.5                          # the deck's height above the still sea
CLEAT = (2.9, -2.95)              # the mooring post, front right corner of the raft
PERCH = (-2.35, 1.6, 4.5)         # the roof ridge
FIRE = (1.7, 0.3)
SHELF = (-2.4, 2.75, 1.75)
MODES = dict(                      # sky, sky strength, sun watts, sun colour, sun direction, sea colour, wave height, fill
    storm=('1A2C58', 1.5, 1.7, 'A8BCF8', (0.5, -0.5, 0.6), '143A64', 1.0, 2.6),
    night=('16244C', 1.4, 1.5, 'A8BCF8', (-0.4, -0.5, 0.7), '143660', 0.35, 2.4),
    dawn=('F6BC92', 1.3, 3.4, 'FFC896', (0.8, 0.45, 0.2), '23608C', 0.4, 1.6),
    day=('8CC8F0', 2.0, 4.6, 'FFF2D8', (-0.4, -0.6, 0.7), '1C6E94', 0.45, 1.4),
    grey=('9AA8B8', 1.6, 2.4, 'E8ECF4', (-0.3, -0.6, 0.7), '2A5870', 0.9, 1.6),
    dusk=('F2A070', 1.25, 3.2, 'FFA468', (0.75, 0.6, 0.17), '24507E', 0.4, 1.9))
_KEEP = []


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 73.31 + j * 39.77) * 15731.743) % 1


def keep(o):
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


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


def look_yaw(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def paint(m, col, emit=0.0):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)
    b.inputs['Emission Color'].default_value = K.hexc(col)
    b.inputs['Emission Strength'].default_value = emit


def seen(objs, on):
    for o in objs:
        o.hide_render = not on


# ---------------------------------------------------------------- the sea
def wave(x, y, t, a):
    return a * (0.6 * math.sin(0.21 * x + 0.07 * y + 1.0 * t) + 0.35 * math.sin(-0.11 * x + 0.3 * y + 1.3 * t + 1.0)
                + 0.2 * math.sin(0.45 * x - 0.38 * y + 1.9 * t + 2.0))


def make_sea(S):
    n = 96
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=n, y_subdivisions=n, size=2)
    o = bpy.context.object
    me = o.data
    co = np.zeros(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    X = np.sign(co[:, 0]) * np.abs(co[:, 0]) ** 2 * 1700          # fine cells round the hut, huge ones at the horizon
    Y = np.sign(co[:, 1]) * np.abs(co[:, 1]) ** 2 * 1700
    damp = 1.0 / (1.0 + (np.hypot(X, Y) / 260.0) ** 2)
    m = bpy.data.materials.new('sea')
    m.use_nodes = True
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.28
    me.materials.append(m)
    S.update(sea=o, seam=m, seaX=X, seaY=Y, seaD=damp)


def sea_at(S, t, a):
    X, Y = S['seaX'], S['seaY']
    Z = a * S['seaD'] * (0.6 * np.sin(0.21 * X + 0.07 * Y + 1.0 * t) + 0.35 * np.sin(-0.11 * X + 0.3 * Y + 1.3 * t + 1.0)
                         + 0.2 * np.sin(0.45 * X - 0.38 * Y + 1.9 * t + 2.0))
    co = np.stack([X, Y, Z], axis=1).astype(np.float32).ravel()
    S['sea'].data.vertices.foreach_set('co', co)
    S['sea'].data.update()


# ---------------------------------------------------------------- the hut on its raft
def make_raft(S):
    r = keep(empty((0, 0, DZ)))
    add('cube', WOOD, (0, 0, -0.1), scale=(9.0, 6.4, 0.2), size=1, parent=r)
    for j in range(8):                                                        # the seams between the planks
        add('cube', WOODD, (0, -2.8 + 0.8 * j, 0.005), scale=(9.0, 0.05, 0.02), size=1, parent=r)
    for j in range(5):                                                        # bamboo floats under the deck
        add('cylinder', BAMBOO, (0, -2.6 + 1.3 * j, -0.42), rot=(0, PI / 2, 0), radius=0.24, depth=9.6, vertices=7, parent=r)
    for (x, y) in ((-3.6, -2.5), (3.6, -2.5), (-3.6, 2.5), (3.6, 2.5), (0, -2.5), (0, 2.5)):
        add('cylinder', DRUM, (x, y, -0.55), rot=(PI / 2, 0, 0), radius=0.52, depth=1.4, vertices=9, parent=r, rough=0.5)
    # the cabin: bamboo posts, woven walls on three sides, open to the front, a thatched gable roof
    x0, x1, y0, y1, hw = -4.1, -0.6, 0.2, 3.0, 3.0
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        add('cylinder', BAMBOO, (x, y, hw / 2), radius=0.1, depth=hw, vertices=6, parent=r)
    add('cube', 'A48648', ((x0 + x1) / 2, y1, hw / 2), scale=(x1 - x0, 0.08, hw), size=1, parent=r)
    for x in (x0, x1):
        add('cube', '987C42', (x, (y0 + y1) / 2, hw / 2), scale=(0.08, y1 - y0, hw), size=1, parent=r)
    for j in range(5):                                                        # weave lines on the back wall
        add('cube', '7E6434', ((x0 + x1) / 2, y1 - 0.05, 0.4 + 0.55 * j), scale=(x1 - x0, 0.03, 0.05), size=1, parent=r)
    ym, rise, half = (y0 + y1) / 2, 1.45, (y1 - y0) / 2 + 0.45
    ang = math.atan2(rise, half)
    ln = math.hypot(rise, half)
    for s in (-1, 1):
        add('cube', THATCH, ((x0 + x1) / 2, ym + s * half / 2, hw + rise / 2 - 0.02), rot=(-s * ang, 0, 0), scale=(x1 - x0 + 0.9, ln, 0.16), size=1,
            parent=r, rough=1.0)
        for j in range(4):                                                    # rows of thatch
            f = (j + 0.5) / 4
            add('cube', THATCHD, ((x0 + x1) / 2, ym + s * half * (1 - f), hw + rise * f + 0.08), rot=(-s * ang, 0, 0),
                scale=(x1 - x0 + 0.94, 0.07, 0.07), size=1, parent=r, rough=1.0)
    add('cylinder', THATCHD, ((x0 + x1) / 2, ym, hw + rise + 0.02), rot=(0, PI / 2, 0), radius=0.13, depth=x1 - x0 + 1.0, vertices=6, parent=r)
    add('cube', WOODD, ((x0 + x1) / 2, y1 - 0.25, SHELF[2] - 0.32), scale=(x1 - x0 - 0.2, 0.5, 0.06), size=1, parent=r)      # the shelf
    add('cube', '6A7A5A', (-3.3, 1.3, 0.12), scale=(1.3, 2.0, 0.14), size=1, parent=r)                                       # a sleeping mat
    # the fence: posts all round, rails that can be taken out one by one
    pts = [(4.4, -3.1), (4.4, -1.0), (4.4, 1.1), (4.4, 3.1), (2.2, 3.1), (0.0, 3.1), (-2.2, 3.1), (-4.4, 3.1), (-4.4, 1.0), (-4.4, -1.1),
           (-4.4, -3.1), (-2.6, -3.1), (-0.8, -3.1), (1.0, -3.1)]
    rails = []
    for j, (x, y) in enumerate(pts):
        add('cylinder', WOODL, (x, y, 0.62), radius=0.07, depth=1.24, vertices=6, parent=r)
        if j + 1 < len(pts):
            b = pts[j + 1]
            rails.append([tube(r, WOODL, (x, y, z), (b[0], b[1], z), 0.045) for z in (0.5, 1.1)])
    # lamps on poles at the corners, the generator, the mooring post
    bulbs = []
    for (x, y) in ((4.3, -3.0), (-4.3, -3.0), (4.3, 3.0)):
        tube(r, BAMBOO, (x, y, 0), (x, y, 3.7), 0.06)
        add('cone', '3A3F4C', (x, y, 3.86), radius1=0.34, radius2=0.05, depth=0.26, vertices=8, parent=r)
        bulbs.append(add('ico_sphere', 'FFE9A8', (x, y, 3.62), radius=0.17, subdivisions=1, parent=r, emit=9.0))
    add('cube', 'B8402C', (3.2, 2.2, 0.42), scale=(1.3, 0.8, 0.84), size=1, parent=r, rough=0.5)
    add('cylinder', '2A2E38', (3.5, 2.2, 0.96), radius=0.16, depth=0.26, vertices=7, parent=r)
    add('cube', '2A2E38', (2.85, 2.2, 0.9), scale=(0.34, 0.5, 0.12), size=1, parent=r)
    add('cylinder', WOODD, (CLEAT[0], CLEAT[1], 0.3), radius=0.16, depth=0.6, vertices=7, parent=r)
    add('cube', WOODD, (CLEAT[0], CLEAT[1], 0.5), scale=(0.7, 0.14, 0.12), size=1, parent=r)
    S.update(raft=r, rails=rails, bulbs=bulbs)


def hardhat_head(skin, hat='F2F2EC'):
    def fn(head):
        d = K.human_head(skin, '17131A')(head)
        add('ico_sphere', hat, (0, 0.0, 0.2), scale=(1.0, 1.08, 0.62), radius=0.34, subdivisions=2, parent=head, rough=0.35)
        add('cube', hat, (0, -0.3, 0.14), scale=(0.5, 0.26, 0.04), size=1, parent=head, rough=0.35)
        return d
    return fn


def make_ship(S):
    """A bulk carrier, bow towards +x; the side that faces the hut is y = -11. No name, flag or funnel mark."""
    s = keep(empty(AWAY))
    add('cube', '8E2C26', (0, 0, -1.0), scale=(150, 22, 6), size=1, parent=s, rough=0.6)
    add('cube', '1F2A3E', (0, 0, 7.0), scale=(150, 22.1, 10), size=1, parent=s, rough=0.6)
    add('cube', '8E2C26', (75, 0, -1.0), rot=(0, 0, PI / 4), scale=(15.56, 15.56, 6), size=1, parent=s, rough=0.6)
    add('cube', '1F2A3E', (75, 0, 7.0), rot=(0, 0, PI / 4), scale=(15.63, 15.63, 10), size=1, parent=s, rough=0.6)
    add('cube', '6E3A2A', (0, 0, 12.02), scale=(150, 21.6, 0.1), size=1, parent=s)                                    # the deck
    for j in range(5):                                                                                                 # hatch covers
        add('cube', 'B4703A', (-34 + 24 * j, 0, 13.0), scale=(18, 14, 1.9), size=1, parent=s)
        add('cube', '8A5228', (-34 + 24 * j, 0, 14.0), scale=(18.3, 1.0, 0.2), size=1, parent=s)
    add('cube', 'E8E6DE', (-62, 0, 20), scale=(16, 19, 16), size=1, parent=s)                                         # the house
    add('cube', 'E8E6DE', (-60, 0, 29.2), scale=(10, 24, 2.6), size=1, parent=s)
    add('cube', '16202E', (-54.9, 0, 29.5), scale=(0.2, 22, 1.1), size=1, parent=s)
    for z in (17, 21, 25):
        add('cube', '16202E', (-53.9, 0, z), scale=(0.2, 15, 0.8), size=1, parent=s)
        add('cube', '16202E', (-62, -9.55, z), scale=(12, 0.2, 0.8), size=1, parent=s)
    add('cylinder', 'C8B070', (-66, 0, 33.5), radius=2.4, depth=7, vertices=9, parent=s)
    add('cylinder', '20242C', (-66, 0, 37.2), radius=2.5, depth=0.8, vertices=9, parent=s)
    add('cylinder', 'D8D8D0', (-58, 0, 34), radius=0.25, depth=7, vertices=5, parent=s)
    add('cylinder', 'D8D8D0', (66, 0, 16), radius=0.3, depth=8, vertices=5, parent=s)
    for side in (-1, 1):                                                                                               # the rail
        tube(s, 'D8D8D0', (-74, side * 10.7, 13.3), (74, side * 10.7, 13.3), 0.07)
        tube(s, 'D8D8D0', (-74, side * 10.7, 12.7), (74, side * 10.7, 12.7), 0.05)
        for j in range(38):
            tube(s, 'D8D8D0', (-74 + 4 * j, side * 10.7, 12.05), (-74 + 4 * j, side * 10.7, 13.3), 0.05)
    for sd in (-1, 1):                                                                                                 # a rope ladder down the near side
        tube(s, ROPE, (sd * 0.55, -11.2, 12.9), (sd * 0.55, -11.2, 0.4), 0.05)
    for j in range(14):
        add('cube', WOODL, (0, -11.2, 0.9 + 0.85 * j), scale=(1.3, 0.16, 0.08), size=1, parent=s)
    wake = []
    for j in range(16):                                                                                                # foam: bow wave and wake
        along = j < 6
        wake.append(add('ico_sphere', 'EAF4F8', (78 - 7 * j if along else -76 - 9 * (j - 6), (1 if j % 2 else -1) * (4 + (3 * j if along else 2 + 1.2 * (j - 6))), 0.15),
                        scale=(5.5, 2.6, 0.5) if along else (9, 4.5, 0.4), radius=1, subdivisions=1, parent=s, rough=1.0))
    S.update(ship=s, wake=wake)


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_sea(S)
    make_raft(S)
    make_ship(S)
    S['clouds'] = [add('ico_sphere', 'F8F4EE', (1500 * math.cos(j * 0.7 + 0.3), 1500 * math.sin(j * 0.7 + 0.3), 260 + 160 * rn(j, 3)),
                       scale=(170 + 120 * rn(j, 1), 90 + 60 * rn(j, 2), 16 + 10 * rn(j, 4)), radius=1, subdivisions=2, rough=1.0) for j in range(9)]
    S['sunball'] = add('ico_sphere', 'FFE2A8', AWAY, radius=230, subdivisions=3, emit=7.0)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['rook'].sc = 1.0
    S['boy'] = K.Rig(dict(top='24272F', pants='3D4E72', hand=SKIN, boot=SKIN, fore=SKIN), K.human_head(SKIN, '15121A'))
    S['boy'].sc = 0.9
    S['crew'] = []
    for i, sk in enumerate(('B8875C', '9A6A46', 'C89468')):
        rig = K.Rig(dict(top='E07A1E', pants='C86A18', hand=sk, boot='22262E', fore='E07A1E'), hardhat_head(sk))
        rig.sc = 1.0
        S['crew'].append(rig)
    S['humans'] = [S['boy']] + S['crew']
    S['cast'] = [S['rook']] + S['humans']
    R = S['raft']
    S['ropes'] = [keep(add('cylinder', ROPE, AWAY, radius=0.5, depth=1, vertices=5, rough=0.9)) for _ in range(5)]
    S['fray'] = fr = keep(empty(AWAY))
    for j in range(5):
        add('cone', ROPE, (0.05 * math.cos(j * 1.26), 0.05 * math.sin(j * 1.26), 0.16), rot=(0.35 * math.sin(j * 1.26), -0.35 * math.cos(j * 1.26), 0),
            radius1=0.035, radius2=0.0, depth=0.34, vertices=4, parent=fr)
    S['fish'] = f = keep(empty(AWAY))
    add('ico_sphere', 'C8D4E0', (0, 0, 0), scale=(0.34, 0.08, 0.14), radius=1, subdivisions=2, parent=f, rough=0.2, emit=0.15)
    add('cone', 'A8B8C8', (0.4, 0, 0), rot=(0, -PI / 2, 0), scale=(1.0, 0.3, 1.0), radius1=0.16, radius2=0.02, depth=0.22, vertices=4, parent=f, rough=0.2)
    add('ico_sphere', '0E0D14', (-0.22, -0.07, 0.03), radius=0.03, subdivisions=1, parent=f)
    S['line'] = keep(add('cylinder', 'E8E8E8', AWAY, radius=0.5, depth=1, vertices=4))
    S['stick'] = keep(add('cylinder', WOODD, AWAY, radius=0.5, depth=1, vertices=5))
    S['planks'] = [keep(add('cube', WOODL, AWAY, scale=(0.9, 0.1, 0.1), size=1)) for _ in range(2)]
    S['tin'] = tin = keep(empty(AWAY, R))                                                             # the fire, in a cut-down tin
    add('cylinder', '4A4F5C', (0, 0, 0.2), radius=0.42, depth=0.4, vertices=9, parent=tin, rough=0.5)
    for j in range(3):
        add('cube', WOODL, (0, 0, 0.42), rot=(0.3, 0, j * 1.05), scale=(0.95, 0.09, 0.09), size=1, parent=tin)
    S['flames'] = [add('cone', ('FF8A1E', 'FFC83A', 'FF5A1A', 'FFE07A')[j], (0.14 * math.cos(j * 1.6), 0.14 * math.sin(j * 1.6), 0.72), radius1=0.17,
                       radius2=0.0, depth=0.6, vertices=5, parent=tin, emit=9.0) for j in range(4)]
    S['jug'] = jug = keep(empty((SHELF[0] - 0.5, SHELF[1] - 0.25, SHELF[2] - 0.29), R))
    add('cylinder', 'DCEBF2', (0, 0, 0.3), radius=0.26, depth=0.6, vertices=8, parent=jug, rough=0.3)
    add('cylinder', '2B6CA8', (0, 0, 0.66), radius=0.1, depth=0.14, vertices=7, parent=jug)
    S['water'] = add('cylinder', '4A9AD0', (0, 0, 0.07), radius=0.24, depth=0.1, vertices=8, parent=jug, emit=0.3)
    S['sack'] = keep(add('ico_sphere', 'E4DCC4', (SHELF[0] + 0.1, SHELF[1] - 0.25, SHELF[2] - 0.06), scale=(0.4, 0.26, 0.24), radius=1, subdivisions=1, parent=R))
    S['gas'] = g = keep(empty((SHELF[0] + 1.0, SHELF[1] - 0.25, SHELF[2] - 0.29), R))
    add('cylinder', '3E8A5A', (0, 0, 0.26), radius=0.2, depth=0.52, vertices=8, parent=g, rough=0.4)
    add('cylinder', '2A2E38', (0, 0, 0.58), radius=0.07, depth=0.12, vertices=6, parent=g)
    S['radio'] = rd = keep(empty(AWAY))
    add('cube', '1E222A', (0, 0, 0.3), scale=(0.3, 0.16, 0.6), size=1, parent=rd, rough=0.4)
    add('cylinder', '1E222A', (-0.09, 0, 0.84), radius=0.022, depth=0.5, vertices=5, parent=rd)
    add('cube', '5A6068', (0, -0.085, 0.2), scale=(0.2, 0.02, 0.22), size=1, parent=rd)
    S['knob'] = add('cylinder', 'FF7A1A', (0.08, 0, 0.64), radius=0.05, depth=0.09, vertices=6, parent=rd, rough=0.4)
    S['led'] = add('cube', '6AFF8A', (0.08, -0.085, 0.45), scale=(0.05, 0.02, 0.05), size=1, parent=rd, emit=8.0)
    S['hand'] = K.Hand(SKIN, SKIN, 1.0)
    keep(S['hand'].root)
    S['rag'] = keep(add('cube', 'E6E0D0', AWAY, scale=(0.9, 0.03, 0.6), size=1, rough=1.0))
    S['rag2'] = keep(add('cube', 'FF7A1A', AWAY, scale=(0.5, 0.03, 0.4), size=1, rough=1.0))
    S['wet'] = keep(add('ico_sphere', '7E98A8', AWAY, scale=(0.17, 0.11, 0.12), radius=1, subdivisions=1, rough=0.5))
    S['towel'] = keep(add('cone', 'F0EEE6', AWAY, radius1=0.62, radius2=0.42, depth=0.95, vertices=8, rough=1.0))
    S['cup'] = keep(add('cone', 'E8E4D8', AWAY, radius1=0.08, radius2=0.11, depth=0.17, vertices=8))
    S['hook'] = keep(add('torus', 'E8ECF2', AWAY, major_radius=0.1, minor_radius=0.025, major_segments=8, minor_segments=4, rough=0.15, emit=0.5))
    S['fea'] = [keep(add('cone', '2F2B4D', AWAY, radius1=0.07, radius2=0.0, depth=0.34, vertices=4)) for _ in range(2)]
    S['drops'] = [keep(add('ico_sphere', 'EAF6FF', AWAY, radius=0.1, subdivisions=1, rough=0.3, emit=0.3)) for _ in range(14)]
    S['far'] = [keep(add('ico_sphere', 'FFE2A0', AWAY, radius=0.9, subdivisions=1, emit=14.0)) for _ in range(3)]
    S['lamps'] = [light(AWAY, 0, 'FFE2B0', kind='POINT') for _ in range(5)]
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 6000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    S['fill'] = light((0, 0, 0), 0, 'FFFFFF', 3.0, tgt)
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    sc.world = w
    S['bg'] = w.node_tree.nodes['Background']
    reset(S)
    return S


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
    S['hand'].grip(0.2)
    for pair in S['rails']:
        seen(pair, True)
    seen(S['bulbs'], True)
    seen(S['wake'], True)
    S['tin'].location = AWAY
    S['water'].hide_render = False
    S['led'].hide_render = False
    for l in S['lamps']:
        l.location = AWAY
        l.data.energy = 0
        l.data.color = K.hexc('FFE2B0')[:3]
    S['sun'].data.energy = 0
    S['fill'].data.energy = 0
    S.update(fillk=0.0, rface='calm', hat_tip=0.0, hat_jump=0.0, bob=0.0, amp=0.4)
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinking and beak lip sync, after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.43) % 1 < 0.035
    ez = dict(calm=0.07, deadpan=0.05, shocked=0.13, sad=0.055, warm=0.06).get(e, 0.07)
    tilt = dict(deadpan=-0.05, shocked=0.35, sad=0.42, warm=0.2).get(e, -0.25)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip = S['hat_tip']
    r['hat'].rotation_euler = (-0.2 + (0.12 if e == 'deadpan' else 0.0) + tip * 0.35, 0.07, 0)
    r['hat'].location = (0.0, 0.0, 0.27 + S['hat_jump'] + tip * 0.1)
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.7, shut=0.07, tired=0.5, warm=0.85, squint=0.35, sad=0.55).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.035 if f == 'wide' else -0.012 if f in ('sad', 'tired', 'squint') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.3 if f == 'sad' else 0.0), 0)
        x['mouth'].scale = (0.13 if f != 'warm' else 0.18, 0.03, 0.035 + 0.13 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sea(S, mode, t, amp=None, lamps=False):
    """Sky, sun and the sea for this frame; the raft rides the swell at the origin."""
    skyc, skyk, sun, sunc, sdir, seac, a, fk = MODES[mode]
    a = a if amp is None else amp
    S['bg'].inputs[0].default_value = K.hexc(skyc)
    S['bg'].inputs[1].default_value = skyk
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = (sdir[0] * 500, sdir[1] * 500, sdir[2] * 500)
    S['sun'].data.energy = sun
    S['sun'].data.color = K.hexc(sunc)[:3]
    paint(S['seam'], seac)
    sea_at(S, t, a)
    S['fillk'], S['amp'] = fk, a
    seen(S['clouds'], mode not in ('storm', 'night'))
    S['sunball'].location = (sdir[0] * 4200, sdir[1] * 4200, sdir[2] * 4200) if mode in ('dawn', 'dusk') else AWAY
    b = wave(0, 0, t, a)
    S['bob'] = b
    S['raft'].location = (0, 0, DZ + b)
    S['raft'].rotation_euler = (0.07 * a * math.sin(1.3 * t + 0.4), 0.09 * a * math.sin(1.0 * t + 1.9), 0)
    seen(S['bulbs'], lamps)
    if lamps:
        fl = 1.0 + 0.08 * math.sin(t * 19)
        for i, (x, y) in enumerate(((4.3, -3.0), (-4.3, -3.0), (4.3, 3.0))):
            S['lamps'][i].location = (x * 0.92, y * 0.92, DZ + b + 3.4)
            S['lamps'][i].data.energy = 1500 * fl


def D(S, x, y, z):
    """A point given relative to the deck, in world coordinates (the raft sits at the origin)."""
    return (x, y, z + DZ + S['bob'])


def on(S, rig, x, y, yaw=0.0, z=0.0, pitch=0.0):
    rig.root.parent = S['raft']
    rig.place((x, y, z), yaw, pitch)


def aboard(S, rig, x, y, yaw=0.0, z=12.07):
    rig.root.parent = S['ship']
    rig.place((x, y, z), yaw)


def ship_at(S, x, y, yaw=0.0, z=0.0):
    S['ship'].location = (x, y, z)
    S['ship'].rotation_euler = (0, 0, yaw)


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


def lampat(S, i, pos, e, col='FFE2B0'):
    S['lamps'][i].location = pos
    S['lamps'][i].data.energy = e
    S['lamps'][i].data.color = K.hexc(col)[:3]


def rope(S, i, a, b, w=0.08):
    span(S['ropes'][i], a, b, w)


ORDER = (12, 11, 0, 1, 2, 10, 3, 4, 5, 6, 9, 8, 7)


def fence(S, gone):
    """Take out `gone` pairs of rails, in the order he burns them (the front ones first)."""
    for j in ORDER[:gone]:
        seen(S['rails'][j], False)


def splash(S, pos, u, n=10, r=1.6, h=2.2, i0=0, s=1.0):
    """A burst of white water from pos; u is seconds since it started."""
    if u <= 0:
        return
    for i in range(n):
        a = i * 2.4
        q = 0.5 + 0.5 * rn(i, 5)
        S['drops'][i0 + i].location = (pos[0] + r * q * u * math.cos(a), pos[1] + r * q * u * math.sin(a), pos[2] + h * q * u * 2 - 4.5 * u * u)
        z = s * (0.8 + rn(i, 6))
        S['drops'][i0 + i].scale = (z, z, z)


def feather(S, pos, lt, t0=0.0):
    for i in range(2):
        u = max(0.0, lt - t0) * 1.3
        if u <= 0:
            continue
        S['fea'][i].location = (pos[0] + (0.5 + i * 0.5) * u + 0.2 * math.sin(u * 6 + i), pos[1] - 0.3 * u, pos[2] + 0.9 * u - 1.2 * u * u)
        S['fea'][i].rotation_euler = (u * 5 + i, u * 3, i * 2.0)


def fire(S, t, e=1.0):
    S['tin'].location = (FIRE[0], FIRE[1], 0.0)
    for j, f in enumerate(S['flames']):
        q = 0.7 + 0.5 * abs(math.sin(t * (9 + 2 * j) + j * 1.7))
        f.scale = (1, 1, q * e)
        f.location.z = 0.42 + 0.3 * q * e
    lampat(S, 3, D(S, FIRE[0], FIRE[1] - 0.1, 1.5), 900 * e * (1.0 + 0.2 * math.sin(t * 17)), 'FF9A40')


def in_hand(S, o, rig, side=1, off=(0, -0.1, -0.1), rot=(0, 0, 0)):
    o.location = world_of(rig.hands[side], off)
    o.rotation_euler = rot


HUG = dict(lL=(1.75, 2.1), lR=(1.75, 2.1), aL=(1.2, -0.2, 1.2, 0.6), aR=(1.2, -0.2, 1.2, 0.6), lift=-0.62, lean=0.42)
CROUCH = dict(lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.4)


# ---------------------------------------------------------------- the hook: the rope parts
def snap_wide(S, k, t, lt):
    """Night, a hard wind. The hut heaves on its mooring; the rope parts and the hut swings away. Opening and last shot."""
    kk = 1 - k if S['prm'].get('loop') else k
    sea(S, 'storm', t, lamps=True)
    go = sm((kk - 0.42) / 0.1)
    S['raft'].location = (-1.6 * sm((kk - 0.45) / 0.55), 0, DZ + S['bob'])
    S['raft'].rotation_euler = (S['raft'].rotation_euler[0], S['raft'].rotation_euler[1] + 0.16 * math.sin(min(1.0, max(0.0, kk - 0.42) / 0.3) * PI), 0)
    b = S['boy']
    on(S, b, 1.4, -1.9, look_yaw((1.4, -1.9), CLEAT))
    b.apply(blend(P('brace', head=(0.2, 0.0)), P('scream', head=(-0.1, 0.0), lean=-0.1), go))
    b.face, b.jawv = 'wide', 0.3 + 0.5 * go
    c = world_of(S['raft'], (CLEAT[0], CLEAT[1], 0.5))
    far = (15.0, -9.5, -1.2)
    if go < 0.5:
        mid = tuple(c[i] + (far[i] - c[i]) * 0.5 for i in range(3))
        mid = (mid[0], mid[1], mid[2] + 0.12 * math.sin(t * 46))
        rope(S, 0, c, mid, 0.09)
        rope(S, 1, mid, far, 0.09)
    else:
        u = (kk - 0.47) / 0.53
        wh = (c[0] + 1.5 * math.cos(u * 9), c[1] - 0.9 + 0.8 * math.sin(u * 11), c[2] + 0.9 * math.cos(u * 7) * (1 - u))
        rope(S, 0, c, wh, 0.09)
        S['fray'].location = wh
        S['fray'].rotation_euler = (u * 7, u * 5, 0)
        end = (lerp(7.5, 12.0, u), lerp(-5.5, -8.0, u), lerp(1.0, -1.0, sm(u * 2)))
        rope(S, 1, end, far, 0.09)
        splash(S, (9.5, -6.6, 0.0), (kk - 0.55) * 1.6, 8, 2.0, 1.6)
    shoot(S, D(S, lerp(6.6, 5.8, kk), lerp(-10.8, -9.6, kk), lerp(1.8, 2.2, kk)), D(S, 0.0, -0.6, 2.5), 24, fill=1.5, fcol='D8E4FF')


def rope_close(S, k, t, lt):
    """Close on the mooring post: the frayed end whips on it, the rest of the rope slides off into the sea. His hand comes too late."""
    sea(S, 'storm', t, lamps=True)
    c = world_of(S['raft'], (CLEAT[0], CLEAT[1], 0.52))
    wh = (c[0] + 0.7 * math.cos(lt * 15) * (1 - 0.6 * k), c[1] - 0.8, c[2] + 0.25 + 0.5 * abs(math.sin(lt * 12)) * (1 - 0.6 * k))
    rope(S, 0, c, wh, 0.07)
    S['fray'].location = wh
    S['fray'].rotation_euler = (lt * 8, 0.6, lt * 5)
    S['fray'].scale = (1.6, 1.6, 1.6)
    e0 = (lerp(4.2, 7.5, k), lerp(-4.2, -6.5, k), lerp(0.7, -0.8, sm(k * 1.6)))
    rope(S, 1, e0, (e0[0] + 4, e0[1] - 3, e0[2] - 1.6), 0.07)
    splash(S, (5.0, -4.9, 0.1), (lt - 0.25) * 1.5, 8, 1.2, 1.3, s=0.8)
    b = S['boy']
    bx = lerp(0.4, 1.7, sm(lt / 0.5))
    on(S, b, bx, -2.3, look_yaw((bx, -2.3), (CLEAT[0] + 1, CLEAT[1] - 0.6)))
    b.apply(blend(P('brace'), P('stand', aR=(1.5, 0.0, 0.2), aL=(0.9, 0.5, 0.6), lean=0.6, lL=(0.5, 0.6), lR=(-0.3, 0.3), lift=-0.2, head=(-0.2, 0.0)), lt / 0.5))
    b.face, b.jawv = 'wide', 0.6
    shoot(S, D(S, lerp(5.9, 5.5, k), lerp(-7.0, -6.6, k), lerp(1.3, 1.5, k)), D(S, 2.5, -2.7, 1.5), 36, fill=1.5, fcol='D8E4FF')


def drift_off(S, k, t, lt):
    """High and wide: the hut slides away into the dark; the lamps of the other huts fall behind."""
    sea(S, 'storm', t, lamps=True)
    for i, (x, y) in enumerate(((70, 105), (120, 78), (40, 150))):
        S['far'][i].location = (x + 40 * k, y + 50 * k, 2.2 + wave(x, y, t, 0.6))
        S['far'][i].scale = (1 - 0.3 * k,) * 3
    b = S['boy']
    on(S, b, 3.6, 2.4, look_yaw((3.6, 2.4), (70, 105)))
    b.apply(P('up', aL=(2.6 + 0.25 * math.sin(t * 9), -0.5, 0.2), aR=(2.7 - 0.25 * math.sin(t * 9), -0.4, 0.2), head=(-0.2, 0.0)))
    b.face, b.jawv = 'wide', 0.7
    c = world_of(S['raft'], (CLEAT[0], CLEAT[1], 0.5))
    rope(S, 0, c, (c[0] + 1.0, c[1] - 1.2, -0.3), 0.06)
    shoot(S, D(S, lerp(-8.5, -10.5, k), lerp(-10.5, -13.0, k), lerp(6.5, 8.5, k)), D(S, 2.0, 3.0, 1.5), 24, fill=1.6, fcol='D8E4FF')


def boy_face(S, k, t, lt):
    """Close on his face at the rail, eyes wide, the lamp swinging. Behind him, on the roof, a crow in a coat lands."""
    sea(S, 'storm', t, lamps=True)
    b = S['boy']
    on(S, b, 0.1, -2.75, look_yaw((0.1, -2.75), (2.4, -7)))
    b.apply(P('stand', aL=(0.75, 0.25, 0.55), aR=(0.75, 0.25, 0.55), lean=0.12, head=(-0.05, 0.25 * math.sin(lt * 5))))
    b.face, b.jawv = 'wide', 0.35 + 0.2 * math.sin(lt * 9)
    rk = S['rook']
    land = sm(lt / 0.55)
    on(S, rk, PERCH[0], PERCH[1], look_yaw(PERCH, (2.4, -7)), PERCH[2] + 2.2 * (1 - land))
    fl = math.sin(lt * 22)
    rk.apply(blend(P('up', aL=(1.5, 1.2 + 0.4 * fl, 0.2), aR=(1.5, 1.2 + 0.4 * fl, 0.2), lL=(0.3, 0.5), lR=(0.3, 0.5)), P('cross', head=(0.3, 0.0)), (lt - 0.5) / 0.25))
    S['rface'] = 'deadpan'
    hd = world_of(b.head)
    shoot(S, D(S, lerp(2.7, 2.4, k), lerp(-7.2, -6.8, k), 2.2), (hd[0] - 0.25, hd[1], hd[2] + 1.35), 38, fill=1.3, fcol='FFE8D0')


def rook_roof(S, k, t, lt):
    """Rook on the ridge of the roof, arms folded, the black swell heaving behind him: 'A hut isn't a boat.'"""
    sea(S, 'storm', t, lamps=True)
    rk = S['rook']
    cam = (lerp(3.4, 3.0, k), lerp(-5.6, -5.2, k), lerp(8.0, 8.2, k))
    on(S, rk, PERCH[0], PERCH[1], look_yaw(PERCH, cam), PERCH[2])
    rk.apply(blend(P('cross', head=(0.3, 0.0)), P('cross', head=(0.05, 0.0), lean=0.08), lt / 0.25))
    S['rface'] = 'deadpan'
    b = S['boy']
    on(S, b, 0.1, -2.75, look_yaw((0.1, -2.75), (2.4, -7)))
    b.apply(P('stand', aL=(0.75, 0.25, 0.55), aR=(0.75, 0.25, 0.55), lean=0.12))
    b.face = 'wide'
    lampat(S, 4, D(S, 1.0, -2.4, 6.6), 500, 'FFE2B0')
    shoot(S, D(S, *cam), D(S, PERCH[0] + 0.25, PERCH[1], PERCH[2] + 1.9), 36, fill=1.6)


# ---------------------------------------------------------------- nothing to steer with
def no_engine(S, k, t, lt):
    """Grey morning. Rook leans out over the edge of the raft, looks down at bare water, straightens and shrugs at the boy."""
    sea(S, 'grey', t, 0.6)
    rk = S['rook']
    rp = (4.0, -0.9)
    turn = sm((lt - 0.55) / 0.3)
    rk.root.parent = S['raft']
    rk.place((rp[0], rp[1], 0), lerp(look_yaw(rp, (12, -2.5)), look_yaw(rp, (9.5, -7.0)), turn))
    rk.apply(blend(P('point', aR=(0.75, 0.2, 0.1), lean=0.5, head=(0.5, 0.0)), P('shrug', head=(0.0, 0.0)), turn))
    S['rface'] = 'deadpan' if turn > 0.5 else 'calm'
    b = S['boy']
    on(S, b, 1.3, -1.9, look_yaw((1.3, -1.9), (9.5, -5.0)))
    b.apply(P('hips', head=(0.15, 0.0)))
    b.face = 'tired'
    shoot(S, D(S, lerp(10.4, 9.8, k), lerp(-7.4, -6.8, k), lerp(1.9, 2.2, k)), D(S, 3.3, -0.3, 2.2), 36, fill=1.0)


def supplies(S, k, t, lt):
    """Inside the hut: a water jug, a small sack, a gas bottle on the shelf. He tips the jug: almost nothing in it."""
    sea(S, 'grey', t, 0.5)
    b = S['boy']
    bp = (-3.3, 1.7)
    on(S, b, bp[0], bp[1], PI / 2 - 0.35)
    tip = sm((lt - 0.35) / 0.4)
    b.apply(blend(P('stand', aR=(1.25, 0.1, 0.6), aL=(1.0, 0.1, 0.9), head=(0.1, 0.0)), P('stand', aR=(1.5, 0.1, 0.9), aL=(0.9, 0.1, 1.1), head=(0.4, 0.0)), tip))
    b.face = 'sad' if tip > 0.6 else 'calm'
    j = S['jug']
    j.parent = None
    h = world_of(b.hands[1], (0, -0.1, -0.2))
    j.location = (h[0] + 0.1, h[1], h[2] - 0.2)
    j.rotation_euler = (0.0, 1.9 * tip, 0.0)
    for i in range(2):
        u = (lt * 1.3 + i * 0.5) % 1
        S['drops'][i].location = (h[0] + 0.75, h[1], h[2] + 0.2 - 1.6 * u * u) if lt > 0.75 else AWAY
        S['drops'][i].scale = (0.4, 0.4, 0.6)
    lampat(S, 3, D(S, -2.0, -0.8, 2.6), 520, 'FFE8D0')
    shoot(S, D(S, lerp(-1.7, -2.0, k), lerp(-3.6, -3.1, k), 2.3), D(S, -2.5, 2.0, 2.05), 32, fill=1.3)


def dawn_empty(S, k, t, lt):
    """Dawn, from high up: one small hut and nothing else, in any direction."""
    sea(S, 'dawn', t, 0.5)
    b = S['boy']
    on(S, b, 1.5, -2.6, look_yaw((1.5, -2.6), (10, -30)))
    b.apply(P('stand', aL=(0.6, 0.2, 0.6), aR=(0.6, 0.2, 0.6), head=(-0.1, 0.4 * math.sin(lt * 1.5))))
    shoot(S, (lerp(-26, -34, k), lerp(-38, -48, k), lerp(9, 20, k)), (0, 0, 2.0), 32, fill=0.0)


# ---------------------------------------------------------------- how he lived
def fishing(S, k, t, lt):
    """He sits on the edge with a hand line and jerks a silver fish out of the water. Rook, beside him, cannot look away from it."""
    sea(S, 'day', t)
    b = S['boy']
    on(S, b, 2.3, -3.25, 0.15, -0.42)
    up = sm((lt - 0.45) / 0.25)
    b.apply(P('sit', aR=(lerp(1.0, 2.2, up), 0.1, lerp(0.5, 0.9, up)), aL=(0.8, 0.0, 1.0), lean=lerp(0.3, 0.0, up), head=(lerp(0.3, -0.15, up), 0.0)))
    b.face, b.jawv = ('wide' if up > 0.5 else 'squint'), 0.4 * up
    h = world_of(b.hands[1], (0, -0.1, -0.15))
    wig = math.sin(lt * 30) * up
    fp = (h[0] + 0.25 + 0.1 * wig, h[1] - 1.0 + 0.6 * up, lerp(-0.9, h[2] - 1.0, up))
    span(S['line'], h, fp, 0.012)
    S['fish'].location = (fp[0], fp[1], fp[2] - 0.12)
    S['fish'].rotation_euler = (0.3 * wig, PI / 2 + 0.5 * wig, 0.4)
    S['fish'].scale = (0.9, 0.9, 0.9)
    splash(S, (fp[0], fp[1], 0.0), (lt - 0.45) * 1.4, 7, 0.9, 1.1, s=0.6)
    rk = S['rook']
    on(S, rk, 0.4, -2.3, look_yaw((0.4, -2.3), (3.5, -6.5)))
    rk.apply(blend(P('think', head=(0.2, 0.3)), P('stand', aL=(0.5, 0.5, 0.9), aR=(0.5, 0.5, 0.9), lean=0.25, head=(0.1, 0.55)), up))
    S['rface'] = 'shocked' if up > 0.5 else 'calm'
    S['hat_jump'] = 0.22 * math.sin(min(1.0, max(0.0, lt - 0.5) / 0.4) * PI)
    fence(S, 2)
    shoot(S, D(S, lerp(5.0, 4.6, k), lerp(-9.6, -9.0, k), lerp(1.2, 1.5, k)), D(S, 1.7, -2.9, 1.9), 34, fill=0.9)


def fence_break(S, k, t, lt):
    """He pulls a rail out of the fence and breaks it across his knee. The fence already has gaps."""
    sea(S, 'day', t)
    fence(S, 4)
    b = S['boy']
    bp = (3.0, -2.0)
    on(S, b, bp[0], bp[1], look_yaw(bp, (8.6, -4.6)))
    br = sm((lt - 0.5) / 0.12)
    b.apply(blend(P('stand', aL=(1.9, 0.5, 0.4), aR=(1.9, 0.5, 0.4), head=(-0.1, 0.0), lean=-0.1),
                  P('stand', aL=(0.7, 0.45, 0.5), aR=(0.7, 0.45, 0.5), lR=(1.25, 1.5), lean=0.25, head=(0.35, 0.0)), sm((lt - 0.25) / 0.25)))
    b.face, b.jawv = 'squint', 0.3 * br
    hl, hr = world_of(b.hands[0], (0, -0.1, -0.1)), world_of(b.hands[1], (0, -0.1, -0.1))
    mid = tuple((hl[i] + hr[i]) / 2 for i in range(3))
    ang = math.atan2(hr[1] - hl[1], hr[0] - hl[0])
    for i, (hp, s) in enumerate(((hl, -1), (hr, 1))):
        p = S['planks'][i]
        p.location = tuple(lerp(mid[j], hp[j], 0.55) for j in range(3))
        p.location.z -= 0.25 * br
        p.rotation_euler = (0, s * 0.6 * br, ang)
        p.scale = (0.95, 0.1, 0.1)
    splash(S, (mid[0], mid[1], mid[2]), (lt - 0.5) * 0.9 if br > 0 else 0, 5, 0.9, 0.7, s=0.35)
    shoot(S, D(S, lerp(9.0, 8.6, k), lerp(-4.7, -4.4, k), lerp(1.8, 2.0, k)), D(S, 3.0, -2.0, 1.95), 40, fill=1.0)


def cook(S, k, t, lt):
    """Dusk. A small fire of fence wood in a cut-down tin; he holds a fish over it on a stick. Rook warms his wings, then taps his beak."""
    sea(S, 'dusk', t)
    fence(S, 6)
    fire(S, t)
    b = S['boy']
    bp = (0.55, 0.1)
    on(S, b, bp[0], bp[1], look_yaw(bp, (FIRE[0], FIRE[1] - 1.2)))
    b.apply(P('stand', aR=(1.15, -0.1, 0.5), aL=(0.6, 0.1, 1.2), head=(0.3, 0.0), **CROUCH))
    b.face = 'tired'
    h = world_of(b.hands[1], (0, -0.1, -0.1))
    tip = world_of(S['raft'], (FIRE[0] - 0.05, FIRE[1] - 0.05, 1.3 + 0.03 * math.sin(t * 5)))
    span(S['stick'], h, tip, 0.03)
    S['fish'].location = tip
    S['fish'].rotation_euler = (0, 0.2, 0.5 + 0.1 * math.sin(t * 3))
    rk = S['rook']
    rp = (3.25, 0.5)
    on(S, rk, rp[0], rp[1], look_yaw(rp, (FIRE[0], FIRE[1] - 2.2)))
    tap = 0.5 + 0.5 * math.sin(lt * 15)
    rk.apply(blend(P('stand', aL=(1.0, 0.35, 0.5), aR=(1.0, 0.35, 0.5), lean=0.2, head=(0.25, 0.0)),
                   P('tap', aR=(1.25 + 0.12 * tap, -0.25, 2.2, 0.6), head=(0.2, 0.2)), (lt - 0.6) / 0.25))
    S['rface'] = 'calm'
    shoot(S, D(S, lerp(2.1, 1.8, k), lerp(-7.4, -6.8, k), lerp(1.5, 1.7, k)), D(S, 1.75, 0.2, 1.75), 34, fill=1.3, fcol='FFD0A0')


def sip(S, k, t, lt):
    """Close: he lifts a cloth wet with seawater to his mouth and sips from it, eyes shut."""
    sea(S, 'day', t)
    fence(S, 6)
    b = S['boy']
    bp = (2.2, -2.5)
    on(S, b, bp[0], bp[1], 0.1)
    up = sm((lt - 0.15) / 0.4)
    b.apply(blend(P('stand', aL=(0.9, -0.25, 0.9, 0.5), aR=(0.9, -0.25, 0.9, 0.5), head=(0.3, 0.0), **CROUCH),
                  P('stand', aL=(1.05, -0.3, 1.95, 0.6), aR=(1.05, -0.3, 1.95, 0.6), head=(-0.25, 0.0), **dict(CROUCH, lean=0.15)), up))
    b.face = 'shut' if up > 0.7 else 'tired'
    b.jawv = 0.35 * up
    hl, hr = world_of(b.hands[0], (0, -0.1, -0.1)), world_of(b.hands[1], (0, -0.1, -0.1))
    c = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2, (hl[2] + hr[2]) / 2 - 0.12)
    S['wet'].location = c
    S['wet'].rotation_euler = (0.3, 0.2, 0.0)
    for i in range(3):
        u = (lt * 1.5 + i / 3) % 1
        S['drops'][i].location = (c[0] + 0.1 * (i - 1), c[1] - 0.05, c[2] - 0.15 - 1.4 * u * u)
        S['drops'][i].scale = (0.22, 0.22, 0.4)
    hd = world_of(b.head)
    shoot(S, D(S, lerp(3.1, 2.9, k), lerp(-6.2, -5.7, k), lerp(1.5, 1.6, k)), (hd[0], hd[1], hd[2] - 0.25), 50, fill=1.0)


# ---------------------------------------------------------------- ships
def ship_appears(S, k, t, lt):
    """A ship on the horizon. He jumps up at the rail and points."""
    sea(S, 'day', t)
    fence(S, 6)
    ship_at(S, lerp(470, 440, k), lerp(150, 60, k), -PI / 2 - 0.2)
    b = S['boy']
    bp = (3.8, -1.6)
    on(S, b, bp[0], bp[1], look_yaw(bp, (60, 2)), 0.25 * abs(math.sin(lt * 7)) * sm((lt - 0.3) / 0.2))
    b.apply(blend(P('stand', head=(-0.1, 0.0)), P('point', aR=(1.5, -0.1, 0.05), aL=(1.9, 0.5, 0.3), head=(-0.15, 0.0)), (lt - 0.2) / 0.3))
    b.face, b.jawv = 'wide', 0.6
    shoot(S, D(S, lerp(0.2, 0.8, k), lerp(-8.8, -8.2, k), lerp(2.2, 2.4, k)), D(S, 6.6, -0.8, 2.9), 30, fill=1.0)


def wave_cloth(S, k, t, lt):
    """Seen from the sea: he waves a cloth over his head with both arms. Beside him Rook waves a rag of his own."""
    sea(S, 'day', t)
    fence(S, 6)
    b = S['boy']
    bp = (4.0, -1.3)
    cam = (lerp(12.5, 11.8, k), lerp(-4.6, -4.2, k), lerp(1.8, 2.0, k))
    on(S, b, bp[0], bp[1], look_yaw(bp, cam), 0.15 * abs(math.sin(lt * 8)))
    w = math.sin(lt * 11)
    b.apply(P('up', aL=(2.75, 0.3 + 0.35 * w, 0.15), aR=(2.75, 0.3 - 0.35 * w, 0.15), head=(-0.2, 0.0)))
    b.face, b.jawv = 'wide', 0.6 + 0.3 * math.sin(lt * 14)
    hl, hr = world_of(b.hands[0], (0, 0, -0.2)), world_of(b.hands[1], (0, 0, -0.2))
    S['rag'].location = ((hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2, (hl[2] + hr[2]) / 2 + 0.3)
    S['rag'].rotation_euler = (0.2 * w, 0.5 * w, look_yaw(bp, cam))
    rk = S['rook']
    rp = (4.0, 1.0)
    on(S, rk, rp[0], rp[1], look_yaw(rp, cam))
    rk.apply(P('reach', aR=(2.7, 0.2 + 0.4 * math.sin(lt * 11 + 1), 0.2), head=(-0.15, 0.1)))
    S['rface'] = 'calm'
    h = world_of(rk.hands[1], (0, 0, -0.25))
    S['rag2'].location = (h[0], h[1], h[2] + 0.15)
    S['rag2'].rotation_euler = (0.2, 0.6 * math.sin(lt * 11 + 1), look_yaw(rp, cam))
    shoot(S, D(S, *cam), D(S, 4.0, -0.1, 2.75), 34, fill=1.0)


def sail_past(S, k, t, lt):
    """The ship's long hull slides across the horizon and keeps going. His arms come down. Rook pulls his hat brim low."""
    sea(S, 'day', t)
    fence(S, 6)
    ship_at(S, lerp(40, 260, k), lerp(270, 300, k), 0.15)
    b = S['boy']
    bp = (2.6, 2.4)
    on(S, b, bp[0], bp[1], look_yaw(bp, (60, 280)))
    dn = sm((lt - 0.3) / 0.5)
    b.apply(blend(P('up', aL=(2.7, 0.4, 0.15), aR=(2.7, 0.4, 0.15)), P('stand', head=(0.35, 0.0), lean=0.1), dn))
    hl = world_of(b.hands[0], (0, 0, -0.3))
    S['rag'].location = hl
    S['rag'].rotation_euler = (0.2, 1.2 * dn, 0.3)
    rk = S['rook']
    rp = (0.6, 2.2)
    on(S, rk, rp[0], rp[1], lerp(PI, look_yaw(rp, (-1.5, -6)), sm((lt - 0.5) / 0.3)))
    rk.apply(blend(P('reach', aR=(2.6, 0.3, 0.2)), P('hat'), (lt - 0.45) / 0.3))
    S['hat_tip'] = sm((lt - 0.6) / 0.25)
    S['rface'] = 'deadpan'
    shoot(S, D(S, lerp(-1.2, -1.8, k), lerp(-5.6, -6.2, k), lerp(2.7, 2.9, k)), D(S, 2.6, 4.0, 3.2), 28, fill=1.0)


def cry(S, k, t, lt):
    """Night, a quiet sea. He sits with his arms round his knees and his head down. Rook sits beside him and says nothing."""
    sea(S, 'night', t)
    fence(S, 8)
    fire(S, t, 0.45)
    b = S['boy']
    on(S, b, 0.7, -1.2, 0.15)
    sob = 0.03 * math.sin(lt * 9)
    b.apply(P('sit', head=(0.62 + sob, 0.0), **dict(HUG, lean=0.42 + sob)))
    b.face = 'shut'
    rk = S['rook']
    on(S, rk, 2.5, -1.0, -0.2)
    rk.apply(P('sit', head=(0.25, -0.75 * sm((lt - 0.3) / 0.5)), **HUG))
    S['rface'] = 'sad'
    lampat(S, 4, D(S, 1.4, -5.0, 3.0), 260, 'B8CCFF')
    shoot(S, D(S, lerp(1.8, 1.65, k), lerp(-8.0, -7.2, k), lerp(1.6, 1.5, k)), D(S, 1.6, -1.0, 1.45), 34, fill=1.4, fcol='C8D8FF')


# ---------------------------------------------------------------- day forty-nine
def day49(S, k, t, lt):
    """Dawn. Another ship, closer than the others, crossing. He waves the cloth again, slower now."""
    sea(S, 'dawn', t)
    fence(S, 9)
    ship_at(S, lerp(170, 90, k), lerp(200, 205, k), PI + 0.05)
    b = S['boy']
    bp = (3.0, 2.3)
    on(S, b, bp[0], bp[1], look_yaw(bp, (80, 200)))
    w = math.sin(lt * 7)
    b.apply(P('up', aL=(2.5, 0.3 + 0.3 * w, 0.3), aR=(0.3, 0.2, 0.3), head=(-0.1, 0.0), lean=0.1))
    b.face = 'tired'
    h = world_of(b.hands[0], (0, 0, -0.25))
    S['rag'].location = (h[0], h[1], h[2] + 0.3)
    S['rag'].rotation_euler = (0.2 * w, 0.5 * w, 0.8)
    shoot(S, D(S, lerp(-1.4, -1.0, k), lerp(-5.4, -5.0, k), lerp(2.5, 2.7, k)), D(S, 4.2, 4.2, 3.4), 28, fill=1.0, fcol='FFD8B0')


def grab_radio(S, k, t, lt):
    """Close, inside the hut: his hand takes the radio off the shelf and his thumb turns the dial."""
    sea(S, 'dawn', t)
    rd = S['radio']
    base = world_of(S['raft'], (SHELF[0] + 0.3, SHELF[1] - 0.3, SHELF[2] - 0.29))
    take = sm((lt - 0.3) / 0.3)
    rd.location = (base[0], base[1] - 0.3 * take, base[2] + 0.3 * take)
    rd.rotation_euler = (-0.25 * take, 0, 0.15)
    rd.scale = (1.5, 1.5, 1.5)
    S['knob'].rotation_euler = (0, 0, 4.0 * sm((lt - 0.65) / 0.4))
    S['led'].hide_render = not (lt > 0.75 and (lt * 6) % 1 < 0.6)
    hnd = S['hand']
    reach = sm(lt / 0.3)
    hnd.root.location = (rd.location[0] + 0.36 + lerp(0.5, 0.0, reach), rd.location[1] - lerp(1.0, 0.05, reach), rd.location[2] + 0.5)
    hnd.root.rotation_euler = (0.0, -PI / 2, PI - 0.55)
    hnd.root.scale = (1.25, 1.25, 1.25)
    hnd.grip(lerp(0.1, 0.75, sm((lt - 0.2) / 0.15)))
    lampat(S, 3, D(S, -1.2, 0.2, 2.6), 380, 'FFE0C0')
    shoot(S, D(S, lerp(-2.9, -2.8, k), lerp(-1.2, -0.8, k), lerp(2.4, 2.5, k)), D(S, SHELF[0] + 0.45, SHELF[1] - 0.5, SHELF[2] + 0.35), 40, fill=1.2)


def call(S, k, t, lt):
    """Close: the radio at his mouth, he shouts into it. Rook leans in and jabs a wing at the set."""
    sea(S, 'dawn', t)
    fence(S, 9)
    b = S['boy']
    bp = (0.6, -2.3)
    cam = (lerp(1.7, 1.5, k), lerp(-6.6, -6.1, k), 2.45)
    on(S, b, bp[0], bp[1], look_yaw(bp, cam) + 0.25)
    b.apply(P('stand', aR=(0.95, -0.2, 1.9, 0.4), aL=(0.4, 0.3, 0.6), head=(-0.05, -0.2), lean=0.1))
    b.face, b.jawv = 'wide', 0.45 + 0.45 * math.sin(lt * 17)
    h = world_of(b.hands[1], (0, -0.15, -0.1))
    S['radio'].location = (h[0], h[1], h[2] - 0.2)
    S['radio'].rotation_euler = (0.15, 0.2, look_yaw(bp, cam) + 0.6)
    S['radio'].scale = (1.15, 1.15, 1.15)
    rk = S['rook']
    rp = (2.2, -1.8)
    on(S, rk, rp[0], rp[1], look_yaw(rp, (cam[0] - 1.5, cam[1])))
    rk.apply(blend(P('stand', head=(0.1, 0.5), lean=0.15), P('point', aR=(1.3, -0.45, 0.25), head=(0.1, 0.5), lean=0.2), lt / 0.3))
    S['rface'] = 'shocked' if lt > 0.3 else 'calm'
    S['hat_jump'] = 0.18 * math.sin(min(1.0, max(0.0, lt - 0.3) / 0.35) * PI)
    shoot(S, D(S, *cam), D(S, 1.4, -2.1, 2.75), 30, fill=1.1, fcol='FFD8B0')


def wait(S, k, t, lt):
    """The breath before: the radio in his hand, the ship's stern still going away."""
    sea(S, 'dawn', t)
    fence(S, 9)
    ship_at(S, lerp(40, 22, k), lerp(150, 156, k), PI + 0.05)
    b = S['boy']
    bp = (1.6, 2.2)
    on(S, b, bp[0], bp[1], look_yaw(bp, (-6, 60)) + 2.4)
    b.apply(P('stand', aR=(0.75, -0.2, 1.5, 0.4), head=(-0.05, 0.75), lean=0.05))
    b.face = 'wide'
    h = world_of(b.hands[1], (0, -0.15, -0.1))
    S['radio'].location = (h[0], h[1], h[2] - 0.2)
    S['radio'].rotation_euler = (0.1, 0.1, 0.5)
    S['radio'].scale = (1.15, 1.15, 1.15)
    S['led'].hide_render = (lt * 5) % 1 > 0.5
    shoot(S, D(S, lerp(3.6, 3.4, k), lerp(-2.6, -2.2, k), lerp(2.5, 2.6, k)), D(S, 0.8, 4.2, 3.0), 40, fill=1.2, fcol='FFD8B0')


def turn(S, k, t, lt):
    """From above the hut: far off, the ship leans into a turn, its wake curving, until its bow points at us. Rook's hat jumps."""
    sea(S, 'dawn', t)
    fence(S, 9)
    a = lerp(PI + 0.05, PI * 1.5 + 0.3, sm(k * 1.15))
    ship_at(S, 22 + 45 * math.cos(a - PI / 2), 150 + 45 * math.sin(a - PI / 2), a)
    S['ship'].rotation_euler = (0.07 * math.sin(sm(k) * PI), 0, a)
    rk = S['rook']
    on(S, rk, PERCH[0], PERCH[1], look_yaw(PERCH, (1.5, -11)) - 1.0, PERCH[2])
    rk.apply(blend(P('hips', head=(0.0, 0.8)), P('scream', head=(-0.1, 0.5)), (lt - 0.45) / 0.2))
    S['rface'] = 'shocked' if lt > 0.5 else 'calm'
    S['hat_jump'] = 0.45 * math.sin(min(1.0, max(0.0, lt - 0.45) / 0.5) * PI)
    b = S['boy']
    bp = (1.6, 2.6)
    on(S, b, bp[0], bp[1], look_yaw(bp, (10, 80)), 0.3 * abs(math.sin(lt * 8)) * sm((lt - 0.5) / 0.2))
    b.apply(blend(P('stand', aR=(1.0, -0.2, 1.7, 0.4)), P('up'), (lt - 0.5) / 0.25))
    shoot(S, D(S, lerp(2.2, 1.6, k), lerp(-11.5, -10.5, k), lerp(8.6, 9.0, k)), (lerp(2, -1, k), 80, 6.5), 30, fill=1.2, fcol='FFD8B0')


# ---------------------------------------------------------------- the rescue
SHIPY = 26.0


def high_waves(S, k, t, lt):
    """The hull stands over the hut like a wall, and the swell between them heaves. The crew are small figures at the rail."""
    sea(S, 'grey', t, 1.15)
    fence(S, 9)
    ship_at(S, lerp(34, 24, k), SHIPY + 4 + 2.5 * math.sin(t * 0.8), 0.0, 0.5 * math.sin(t * 0.9))
    for j, c in enumerate(S['crew']):
        aboard(S, c, -24 + 3.2 * j, -10.0, 0.0)
        c.apply(P('stand', aR=(1.6 + 0.3 * math.sin(t * 6 + j), 0.3, 0.3), head=(0.4, 0.0), lean=0.3))
    b = S['boy']
    bp = (1.8, 2.6)
    on(S, b, bp[0], bp[1], PI)
    b.apply(P('up', aL=(2.7, 0.4 + 0.3 * math.sin(lt * 10), 0.2), aR=(2.7, 0.4 - 0.3 * math.sin(lt * 10), 0.2), head=(-0.45, 0.0)))
    shoot(S, D(S, lerp(-8.0, -7.0, k), lerp(-13.0, -12.0, k), lerp(0.2, 0.5, k)), (3.0, 9.0, 8.2), 22, fill=1.0, roll=0.05 * math.sin(t * 1.1))


def rope_throw(S, k, t, lt):
    """From the ship's deck: a crewman heaves a line. It uncoils through the air and drops into the water short of the hut."""
    sea(S, 'grey', t, 1.1)
    fence(S, 9)
    sx, sy = 3.0, SHIPY + 4
    ship_at(S, sx, sy)
    c = S['crew'][0]
    aboard(S, c, -4.9, -9.9, 0.15)
    th = sm((lt - 0.15) / 0.2)
    c.apply(blend(P('stand', aR=(-0.8, 0.3, 0.9), lean=-0.15, head=(0.2, 0.0)), P('stand', aR=(1.9, 0.1, 0.1), lean=0.4, head=(0.35, 0.0), lL=(0.4, 0.3)), th))
    c2 = S['crew'][1]
    aboard(S, c2, -0.9, -9.9, -0.2)
    c2.apply(P('stand', aL=(0.9, 0.2, 0.6), aR=(0.9, 0.2, 0.6), lean=0.35, head=(0.4, 0.0)))
    b = S['boy']
    on(S, b, 1.2, 2.7, PI)
    b.apply(P('reach', aR=(2.3, 0.2, 0.2), aL=(1.9, 0.4, 0.3), head=(-0.5, 0.0), lean=-0.05))
    h = world_of(c.hands[1], (0, 0, -0.2))
    fly = sm((lt - 0.3) / 0.45)
    end = (lerp(h[0], 1.5, fly), lerp(h[1], 9.5, fly), lerp(h[2], 0.0, fly) + 5.0 * math.sin(fly * PI) * (1 - 0.4 * fly))
    mid = ((h[0] + end[0]) / 2, (h[1] + end[1]) / 2, (h[2] + end[2]) / 2 + 1.5 * math.sin(fly * PI) - 2.5 * fly)
    if lt > 0.28:
        rope(S, 0, h, mid, 0.06)
        rope(S, 1, mid, end, 0.06)
    splash(S, (1.5, 9.5, 0.0), (lt - 0.78) * 1.5, 9, 1.6, 1.6)
    shoot(S, (sx - 3.0 + lerp(0.6, 0.0, k), sy - lerp(4.6, 5.2, k), lerp(18.2, 17.8, k)), (sx - 3.0, sy - 24.0, 3.0), 24, fill=1.1)


def jump(S, k, t, lt):
    """He goes off the edge of the raft towards the line, arms out. Rook flaps up off the deck and loses a feather."""
    sea(S, 'grey', t, 1.0)
    fence(S, 9)
    ship_at(S, 8.0, SHIPY + 6)
    u = sm((lt - 0.35) / 0.6)
    b = S['boy']
    by = lerp(3.0, 7.6, u)
    bz = DZ + S['bob'] + 2.6 * math.sin(u * PI) - 1.8 * u * u
    b.root.parent = None
    b.place((1.6, by, bz), PI, lerp(0.0, -1.25, u))
    b.apply(blend(P('brace'), P('swim', lL=(-0.2, 0.3), lR=(0.3, 0.6)), (lt - 0.25) / 0.25))
    b.face, b.jawv = 'wide', 0.5
    splash(S, (1.6, 8.1, 0.2), (lt - 0.92) * 1.5, 12, 2.0, 2.0, s=1.2)
    rope(S, 0, (2.2, 9.6, 0.1), (5.0, 22.0, 13.0), 0.05)
    rk = S['rook']
    hop = sm((lt - 0.25) / 0.3)
    on(S, rk, -0.4, 2.0, look_yaw((-0.4, 2.0), (9, -3)), 0.9 * hop * (1 - 0.3 * math.sin(lt * 12)))
    fl = math.sin(lt * 24)
    rk.apply(blend(P('stand', head=(0.0, -0.6)), P('up', aL=(1.5, 1.2 + 0.4 * fl, 0.2), aR=(1.5, 1.2 + 0.4 * fl, 0.2), lL=(0.3, 0.5), lR=(0.3, 0.5), head=(0.0, -0.6)), hop))
    S['rface'] = 'shocked'
    S['hat_jump'] = 0.3 * hop
    feather(S, world_of(rk.head, (0.3, 0, 0.3)), lt, 0.35)
    shoot(S, D(S, lerp(10.5, 9.8, k), lerp(-1.6, -1.0, k), lerp(1.0, 1.3, k)), D(S, 1.0, 4.6, 2.1), 28, fill=1.1)


def haul(S, k, t, lt):
    """At the ship's side: he is on the rope ladder, spray round him; a crewman hangs over the rail and catches his hand."""
    sea(S, 'grey', t, 1.0)
    sx, sy = 0.0, 60.0
    ship_at(S, sx, sy)
    S['raft'].location = (30, 20, -40)
    b = S['boy']
    z = lerp(7.4, 9.9, sm(lt / 0.8))
    b.root.parent = S['ship']
    b.place((0.0, -11.75, z), PI)
    cl = math.sin(lt * 9)
    b.apply(P('reach', aR=(2.75, 0.1, 0.1), aL=(1.6 + 0.3 * cl, 0.1, 0.9), lL=(0.9 + 0.4 * cl, 1.2), lR=(0.5 - 0.4 * cl, 0.9), head=(-0.55, 0.0)))
    b.face, b.jawv = 'tired', 0.3
    c = S['crew'][0]
    aboard(S, c, 0.9, -10.25, 0.0)
    c.apply(P('stand', aR=(1.2, 0.2, 0.2), aL=(1.0, 0.4, 0.5), lean=1.05, head=(0.2, 0.0)))
    c.face, c.jawv = 'wide', 0.5
    c2 = S['crew'][1]
    aboard(S, c2, -1.5, -9.8, 0.25)
    c2.apply(P('stand', aL=(1.1, 0.1, 0.8), aR=(1.1, 0.1, 0.8), lean=0.5, head=(0.3, 0.0)))
    splash(S, (sx + 1.5, sy - 12.5, 0.5), ((lt * 1.2) % 1) * 1.0, 10, 3.0, 4.0, s=1.6)
    shoot(S, (sx + lerp(7.5, 6.5, k), sy - lerp(21.0, 19.5, k), lerp(7.0, 8.2, k)), (sx + 0.2, sy - 11.2, lerp(10.2, 11.4, k)), 34, fill=1.2)


def alive(S, k, t, lt):
    """On deck, in low sun: he sits on a hatch cover with a towel round his shoulders and takes a cup from a crewman. Rook watches from the rail."""
    sea(S, 'dusk', t)
    sx, sy = 0.0, 60.0
    ship_at(S, sx, sy)
    S['raft'].location = (-40, 30, DZ)
    b = S['boy']
    b.root.parent = S['ship']
    b.place((-10.0, -7.35, 13.95 - 0.5 * b.sc), 0.15)
    lift = sm((lt - 0.4) / 0.4)
    b.apply(P('sit', aR=(lerp(0.7, 1.15, lift), -0.1, lerp(1.5, 1.2, lift), 0.6), head=(lerp(0.3, -0.05, lift), 0.25), lean=0.15))
    b.face = 'warm' if lift > 0.6 else 'tired'
    tw = S['towel']
    tw.parent = b.body
    tw.location, tw.rotation_euler, tw.scale = (0, 0.02, 0.7), (0, 0, 0), (1, 1, 1)
    c = S['crew'][1]
    aboard(S, c, -8.4, -9.3, look_yaw((-8.4, -9.3), (-10.0, -7.3)))
    c.apply(P('stand', aR=(1.2, 0.0, 0.6), head=(0.25, 0.0), **dict(CROUCH, lean=0.25)))
    c.face = 'warm'
    h = world_of(c.hands[1], (0, -0.1, -0.12)) if lift < 0.5 else world_of(b.hands[1], (0, -0.1, -0.12))
    S['cup'].location = h
    c3 = S['crew'][2]
    aboard(S, c3, -12.3, -8.3, look_yaw((-12.3, -8.3), (-9.0, -13.0)))
    c3.apply(P('stand', aR=(1.1, -0.5, 0.5), head=(0.35, -0.5)))
    c3.face = 'warm'
    rk = S['rook']
    aboard(S, rk, -7.4, -7.35, 0.25, 13.95 - 0.5)
    rk.apply(P('sit', head=(0.15, 0.6), lL=(1.45, 1.5), lR=(1.45, 1.5), aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), lift=-0.5, lean=0.1))
    S['rface'] = 'warm'
    lampat(S, 3, (sx - 9.0, sy - 12.5, 16.5), 1500, 'FFE8D0')
    shoot(S, (sx + lerp(-8.4, -8.7, k), sy - lerp(14.4, 13.8, k), lerp(15.0, 15.2, k)), (sx - 9.3, sy - 7.6, 15.0), 30, fill=1.5, fcol='FFD8B8')


def ship_away(S, k, t, lt):
    """Dusk, wide: the ship carries him off towards the low sun. The hut is left behind, empty, turning slowly."""
    sea(S, 'dusk', t)
    fence(S, 9)
    S['raft'].rotation_euler = (S['raft'].rotation_euler[0], S['raft'].rotation_euler[1], 0.25 + 0.2 * k)
    ship_at(S, lerp(70, 130, k), lerp(170, 290, k), 1.15)
    shoot(S, D(S, lerp(-9.0, -10.5, k), lerp(-12.0, -13.5, k), lerp(3.0, 4.2, k)), (14, 30, 5.0), 30, fill=0.6)


# ---------------------------------------------------------------- the end
def rook_wrong(S, k, t, lt):
    """Rook alone on the empty raft at dusk. He turns to us and shrugs."""
    sea(S, 'dusk', t)
    fence(S, 9)
    rk = S['rook']
    rp = (1.6, -2.0)
    cam = (lerp(3.6, 3.3, k), lerp(-8.2, -7.6, k), 2.5)
    tn = sm((lt - 0.1) / 0.3)
    on(S, rk, rp[0], rp[1], lerp(PI - 0.6, look_yaw(rp, cam), tn))
    rk.apply(blend(P('hips', head=(-0.1, 0.0)), P('shrug', head=(0.05, 0.0)), tn))
    S['rface'] = 'warm' if tn > 0.5 else 'calm'
    shoot(S, D(S, *cam), D(S, 1.5, -2.0, 2.45), 40, fill=1.0, fcol='FFD0A0')


def signoff(S, k, t, lt):
    """He picks a bright fish hook off the planks, turns it in the last light, pockets it and pulls his hat brim down."""
    sea(S, 'dusk', t)
    fence(S, 9)
    rk = S['rook']
    rp = (-0.6, -2.0)
    on(S, rk, rp[0], rp[1], 0.35)
    grab = sm((lt - 0.05) / 0.22)
    up = sm((lt - 0.3) / 0.22)
    away = sm((lt - 0.58) / 0.22)
    low = P('stand', aR=(0.9, 0.2, 0.2), head=(0.55, 0.3), lean=0.75, lL=(0.5, 0.9), lR=(0.5, 0.9), lift=-0.35)
    hold = P('stand', aR=(1.15, 0.25, 1.3, 0.3), head=(0.25, 0.35))
    rk.apply(blend(blend(blend(P('stand'), low, grab), hold, up), P('hat'), away))
    S['hat_tip'] = away
    S['rface'] = 'warm' if away < 0.5 else 'deadpan'
    ground = world_of(S['raft'], (rp[0] + 0.7, rp[1] - 0.9, 0.08))
    hand = world_of(rk.hands[1], (0, -0.12, -0.08))
    u = sm((lt - 0.2) / 0.12)
    S['hook'].location = tuple(ground[i] + (hand[i] - ground[i]) * u for i in range(3))
    S['hook'].rotation_euler = (lerp(0.0, 2.6, up) + t * 3 * up * (1 - away), 0.3, 0.6)
    S['hook'].scale = (1.6, 1.6, 1.6)
    if lt > 0.66:
        S['hook'].location = AWAY
    shoot(S, D(S, rp[0] + lerp(2.2, 1.8, k), rp[1] + lerp(-6.0, -5.2, k), lerp(1.9, 2.3, k)), D(S, rp[0] + 0.2, rp[1], 2.3), 34, fill=1.0, fcol='FFD0A0')


# ---------------------------------------------------------------- a photograph for the case board
def photo_hut(S, k, t, lt):
    sea(S, 'day', t)
    fence(S, 6)
    ship_at(S, 70, 150, 0.2)
    b = S['boy']
    on(S, b, 3.4, 1.6, look_yaw((3.4, 1.6), (60, 140)))
    b.apply(P('up', aL=(2.75, 0.5, 0.15), aR=(2.75, 0.1, 0.15)))
    hl = world_of(b.hands[0], (0, 0, -0.2))
    S['rag'].location = (hl[0] + 0.3, hl[1], hl[2] + 0.3)
    shoot(S, D(S, -5.0, -10.5, 3.0), D(S, 3.0, 3.0, 3.0), 30, fill=1.0)


SHOTS3D = {f.__name__: f for f in (
    snap_wide, rope_close, drift_off, boy_face, rook_roof, no_engine, supplies, dawn_empty, fishing, fence_break, cook, sip, ship_appears, wave_cloth,
    sail_past, cry, day49, grab_radio, call, wait, turn, high_waves, rope_throw, jump, haul, alive, ship_away, rook_wrong, signoff)}
STILLS = dict(hut=photo_hut)
