"""Case 022 in 3D - Bahia Bakari, 2009. On 30 June 2009 Yemenia Flight 626, an Airbus A310 flying from Sana'a
to Moroni, came down in the sea off Grande Comore in the night. A twelve-year-old girl travelling with her
mother found herself in the water, held on to a piece of the wreckage through the night and the morning, and
was picked up by the crew of the boat Sima Com 2. She was the only survivor: 152 people died.

Built for this story only: an open sea under four skies with a field of floating debris, a torn piece of
fuselage skin with a row of window holes, a small white passenger boat, and a
hospital room.

Everything is a generic low-poly reconstruction. The wreckage is a plain white panel with no livery, name or
logo; the boat is not a model of the real Sima Com 2 and carries no name or flag; the girl, the crew and the
woman at the bedside are simple figures and nobody's likeness is attempted. The crash itself is not shown."""
import math

import bpy
import numpy as np
from mathutils import Vector

from engine4 import kit3d as K
from engine4.kit3d import P, add, blend, empty, lerp, light

PI = math.pi
FAR = (0, 0, -2500)
HOST = {'rook_lands', 'rook_doubt', 'dark_look', 'rook_quiet', 'climb_try', 'hold_on', 'dawn_break', 'morning', 'boat_far', 'reach_fail',
        'sailor_swim', 'blanket', 'look_back', 'her_face', 'rook_wrong', 'signoff'}
CAMFILL = {'*': 140, 'wide_night': 650, 'girl_close': 200, 'hands_grip': 160, 'plane_piece': 240, 'rook_lands': 260, 'rook_doubt': 240,
           'in_water': 380, 'voices': 180, 'dark_look': 300, 'rook_quiet': 200, 'big_wave': 300, 'climb_try': 260, 'hold_on': 420,
           'face_tired': 160, 'dawn_break': 160, 'sea_after': 0, 'debris_close': 60, 'boat_far': 120, 'hospital_wait': 120, 'hospital_tell': 120,
           'her_face': 100, 'empty_chair': 100, 'rook_wrong': 120}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
SKIN, HAIR = '8A5A3C', '15121A'
SKINW = 'E6E8EC'                   # the wreckage skin
GP = (0.3, -1.78)                  # where she hangs on, in the wreckage's own coordinates
RP = (2.6, -3.6)                   # Rook's own bit of floor panel, in the world
RW = (-1.0, -0.7)                  # Rook's place on the wreckage beside her
BOAT = (0.5, 9.8)                  # the boat when it has stopped beside her (its near side is y = 7.3)
DECK = 1.45
ROOM = (0.0, 0.0, 600.0)           # the hospital room hangs far above the sea
SKIES = dict(                      # horizon, zenith, strength, sun watts, sun colour, sun direction, sea colour, swell, fill
    night=('1F4A58', '04121A', 1.0, 1.5, '9CD8E8', (-0.5, 0.45, 0.72), '0D3440', 0.55, 2.6),
    dawn=('F0B48A', '3E6E9A', 1.4, 2.8, 'FFC8A0', (0.82, 0.52, 0.16), '1A5670', 0.6, 2.2),
    grey=('C2CCD2', '7E8C98', 1.7, 2.6, 'EEF0F4', (0.35, -0.55, 0.75), '2C6272', 0.95, 1.5),
    dusk=('F09A62', '3C4C8A', 1.4, 2.6, 'FFA872', (0.86, 0.46, 0.13), '1C4A6C', 0.5, 2.4))
_KEEP = []


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rnd(i, j=0):
    return (math.sin(i * 51.37 + j * 87.13) * 24634.63) % 1


def keep(o):
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def stretch(o, a, b, w):
    a, b = Vector(a), Vector(b)
    d = b - a
    o.location = (a + b) / 2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (w / 0.5, w / 0.5, max(0.01, d.length))


def bar(par, col, a, b, w, **kw):
    o = add('cylinder', col, radius=0.5, depth=1, vertices=6, parent=par, **kw)
    stretch(o, a, b, w)
    return o


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def tint(m, col):
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = K.hexc(col)


def vis(objs, on):
    for o in objs:
        o.hide_render = not on


def kids(o):
    out = [o]
    for c in o.children:
        out += kids(c)
    return out


# ---------------------------------------------------------------- the sea
def swell(x, y, t, a):
    return a * (0.55 * math.sin(0.17 * x + 0.11 * y + 0.9 * t) + 0.3 * math.sin(-0.23 * x + 0.19 * y + 1.4 * t + 0.7)
                + 0.18 * math.sin(0.5 * x + 0.41 * y + 2.1 * t + 2.3))


def make_sea(S):
    n = 110
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=n, y_subdivisions=n, size=2)
    o = bpy.context.object
    co = np.zeros(len(o.data.vertices) * 3, dtype=np.float32)
    o.data.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    X = co[:, 0] * np.abs(co[:, 0]) ** 1.6 * 2400         # small cells near the wreckage, very large ones far out
    Y = co[:, 1] * np.abs(co[:, 1]) ** 1.6 * 2400
    m = bpy.data.materials.new('sea22')
    m.use_nodes = True
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.22
    o.data.materials.append(m)
    S.update(sea=o, seam=m, sx=X, sy=Y, sfade=1.0 / (1.0 + (np.hypot(X, Y) / 300.0) ** 2))


def shape_sea(S, t, a):
    X, Y = S['sx'], S['sy']
    Z = a * S['sfade'] * (0.55 * np.sin(0.17 * X + 0.11 * Y + 0.9 * t) + 0.3 * np.sin(-0.23 * X + 0.19 * Y + 1.4 * t + 0.7)
                          + 0.18 * np.sin(0.5 * X + 0.41 * Y + 2.1 * t + 2.3))
    S['sea'].data.vertices.foreach_set('co', np.stack([X, Y, Z], axis=1).astype(np.float32).ravel())
    S['sea'].data.update()


# ---------------------------------------------------------------- the wreckage and the debris field
def make_wreck(S):
    """A torn piece of fuselage skin, floating outer side up: five curved strips, ribs underneath, a row of window holes."""
    w = keep(empty((0, 0, 0)))
    for j in range(-2, 3):
        add('cube', SKINW, (0, j * 0.5, 0.36 - 0.07 * j * j), rot=(j * 0.14, 0, 0), scale=(5.2 - 0.3 * abs(j), 0.54, 0.09), size=1, parent=w, rough=0.45)
    for i in range(6):                                                     # frames under the skin, sticking out at the torn ends
        x = -2.5 + i * 1.0
        add('cube', '8E97A6', (x, 0, 0.18), scale=(0.08, 2.5, 0.16), size=1, parent=w, rough=0.5)
    for j in (-1, 1):                                                      # stringers poking out past the tear
        for sx in (-1, 1):
            add('cube', '8E97A6', (sx * 2.75, j * 0.62, 0.24), rot=(0, sx * 0.25, j * 0.2), scale=(0.75, 0.06, 0.06), size=1, parent=w, rough=0.5)
    for i in range(6):                                                     # the window holes, in the strip nearest her
        add('cube', '141C28', (-2.0 + i * 0.8, -0.5, 0.345), rot=(-0.14, 0, 0), scale=(0.3, 0.38, 0.03), size=1, parent=w, rough=0.25)
        add('cube', 'B8BEC8', (-2.0 + i * 0.8, -0.5, 0.338), rot=(-0.14, 0, 0), scale=(0.37, 0.45, 0.03), size=1, parent=w, rough=0.4)
    for sx in (-1, 1):                                                     # jagged torn metal at both ends
        for j in range(5):
            y = -1.0 + 0.5 * j
            add('cone', 'D0D4DA', (sx * (2.62 + 0.1 * rnd(j, sx)), y + 0.1 * rnd(j, 3), 0.36 - 0.07 * (y / 0.5) ** 2), rot=(0, sx * PI / 2, 0),
                scale=(0.25, 1.0, 1.0), radius1=0.22, radius2=0.0, depth=0.3 + 0.35 * rnd(j, sx + 5), vertices=3, parent=w, rough=0.4)
        add('cube', 'D8C070', (sx * 2.5, 0.3 * sx, 0.2), rot=(0.3, 0.2, sx), scale=(0.5, 0.36, 0.12), size=1, parent=w, rough=1.0)   # insulation
    S['wreck'] = w
    # Rook's bit of cabin floor
    p = keep(empty((RP[0], RP[1], 0)))
    add('cube', 'B4BAC4', (0, 0, 0.08), rot=(0, 0, 0.3), scale=(2.3, 1.7, 0.14), size=1, parent=p, rough=0.6)
    for j in (-1, 0, 1):
        add('cube', '6E7684', (0.36 * -j, 0.55 * j, 0.16), rot=(0, 0, 0.3), scale=(2.2, 0.07, 0.05), size=1, parent=p, rough=0.5)
    S['panel'] = p
    # the debris field: cushions, panels, a case, bottles; nothing that could be taken for a body
    deb = []
    spec = [('cube', '2E5A8C', (0.9, 0.8, 0.22)), ('cube', 'D8DCE2', (1.8, 1.1, 0.08)), ('cube', '9A2E2A', (0.9, 0.6, 0.3)), ('cube', '2E5A8C', (0.9, 0.8, 0.22)),
            ('cube', 'C8CCD4', (2.4, 0.7, 0.07)), ('cylinder', 'E8ECF0', (0.24, 0.24, 0.5)), ('cube', 'D8DCE2', (1.3, 1.5, 0.08)), ('cube', '3A6A4A', (0.8, 0.5, 0.28)),
            ('cube', 'E8D8A0', (1.0, 0.7, 0.14)), ('cube', 'C8CCD4', (3.0, 1.2, 0.08))]
    spots = [(-6.5, -4.0), (5.5, 4.5), (-4.0, 5.5), (8.0, -6.5), (-9.0, 2.0), (4.5, -8.5), (11.0, 2.5), (-2.5, -9.5), (-12.0, -7.0), (2.0, 12.0)]
    for i, ((kind, col, sc), (x, y)) in enumerate(zip(spec, spots)):
        kw = dict(size=1) if kind == 'cube' else dict(radius=0.5, depth=1, vertices=7)
        o = keep(add(kind, col, (x, y, 0.05), rot=(0.1 * rnd(i, 1), 0.12 * rnd(i, 2), 6 * rnd(i, 3)), scale=sc, rough=0.6, **kw))
        deb.append((o, x, y))
    S['debris'] = deb


def make_boat(S):
    """A small white passenger boat, bow towards +x, 18 long and 5 wide. No name, number or flag."""
    b = keep(empty(FAR))
    add('cube', 'ECEAE2', (-1, 0, 0.55), scale=(14, 5, 1.8), size=1, parent=b, rough=0.5)
    add('cube', '2A5E8E', (-1, 0, -0.2), scale=(14.05, 5.05, 0.7), size=1, parent=b, rough=0.5)
    add('cube', 'ECEAE2', (6, 0, 0.55), rot=(0, 0, PI / 4), scale=(3.54, 3.54, 1.8), size=1, parent=b, rough=0.5)
    add('cube', '2A5E8E', (6, 0, -0.2), rot=(0, 0, PI / 4), scale=(3.58, 3.58, 0.7), size=1, parent=b, rough=0.5)
    add('cube', '8A6A48', (-1, 0, DECK - 0.02), scale=(13.8, 4.8, 0.06), size=1, parent=b)
    add('cube', 'F2F0EA', (-3.6, 0, DECK + 1.25), scale=(5.6, 3.4, 2.5), size=1, parent=b, rough=0.5)               # the cabin
    add('cube', '2A5E8E', (-3.6, 0, DECK + 2.6), scale=(6.2, 3.9, 0.16), size=1, parent=b, rough=0.5)
    for sy in (-1, 1):
        add('cube', '1A2634', (-3.6, sy * 1.71, DECK + 1.6), scale=(4.6, 0.04, 0.7), size=1, parent=b, rough=0.2)
    add('cube', '1A2634', (-0.79, 0, DECK + 1.6), scale=(0.04, 2.6, 0.7), size=1, parent=b, rough=0.2)
    add('cylinder', 'D8D8D0', (-3.0, 0, DECK + 3.8), radius=0.06, depth=2.4, vertices=5, parent=b)
    add('cube', 'B8703A', (2.6, 0.9, DECK + 0.3), scale=(1.6, 1.0, 0.6), size=1, parent=b)                          # a locker to sit on
    rails = []
    for sy in (-1, 1):
        for z in (0.5, 0.95):
            rails.append(bar(b, 'D8D8D0', (-7.8, sy * 2.38, DECK + z), (6.0, sy * 2.38, DECK + z), 0.05))
        for i in range(10):
            rails.append(bar(b, 'D8D8D0', (-7.8 + 1.53 * i, sy * 2.38, DECK), (-7.8 + 1.53 * i, sy * 2.38, DECK + 0.95), 0.045))
    foam = [add('ico_sphere', 'EAF4F8', (7.2 - 2.4 * i, (1 if i % 2 else -1) * (1.2 + 0.5 * i), -0.5), scale=(1.5, 0.8, 0.22), radius=1, subdivisions=1,
                parent=b, rough=1.0) for i in range(6)]
    S.update(boat=b, rails=rails, foam=foam)


def make_room(S):
    r = keep(empty(ROOM))
    add('cube', '5C7478', (0, 0, -0.05), scale=(9, 8, 0.1), size=1, parent=r)                                        # floor
    add('cube', 'E4E8E6', (0, 0, 4.15), scale=(9, 8, 0.1), size=1, parent=r)                                         # ceiling
    add('cube', 'C9D6D2', (0, 3.6, 2.0), scale=(9, 0.12, 4.2), size=1, parent=r)                                     # back wall
    add('cube', '4E7E84', (0, 3.52, 0.7), scale=(9, 0.06, 1.4), size=1, parent=r)                                    # painted lower band
    add('cube', '4E7E84', (4.32, 0, 0.7), scale=(0.06, 8, 1.4), size=1, parent=r)
    add('cube', '2E4E54', (0, 3.5, 1.42), scale=(9, 0.08, 0.08), size=1, parent=r)
    add('cube', '3A4E58', (3.0, 3.5, 2.7), scale=(1.1, 0.06, 1.4), size=1, parent=r)                                 # a notice board
    add('cube', 'BFCDCB', (4.4, 0, 2.0), scale=(0.12, 8, 4.2), size=1, parent=r)                                     # right wall
    for (y, sy, z, sz) in ((-2.2, 3.6, 2.0, 4.2), (3.0, 1.2, 2.0, 4.2), (1.2, 2.6, 0.5, 1.0), (1.2, 2.6, 3.6, 1.0)):   # left wall with a window gap
        add('cube', 'BFCDCB', (-4.4, y, z), scale=(0.12, sy, sz), size=1, parent=r)
    for (a, b_) in (((-4.38, -0.1, 1.0), (-4.38, -0.1, 3.1)), ((-4.38, 2.4, 1.0), (-4.38, 2.4, 3.1)), ((-4.38, 1.15, 1.0), (-4.38, 1.15, 3.1)),
                    ((-4.38, -0.1, 2.05), (-4.38, 2.4, 2.05))):
        bar(r, 'F2F2EE', a, b_, 0.05)
    S['pane'] = add('cube', 'FFC890', (-4.6, 1.15, 2.05), scale=(0.02, 2.5, 2.1), size=1, parent=r, emit=3.0)
    S['curtain'] = add('cube', '7FB0B4', (-4.2, 2.75, 2.2), scale=(0.06, 0.8, 2.6), size=1, parent=r, rough=1.0)
    # the bed: head against the back wall, foot towards the camera
    add('cube', 'E8ECEC', (0.6, 1.7, 0.72), scale=(2.1, 3.6, 0.3), size=1, parent=r, rough=1.0)
    add('cube', '9AA4AC', (0.6, 1.7, 0.42), scale=(2.2, 3.7, 0.12), size=1, parent=r)
    add('cube', '9AA4AC', (0.6, 3.48, 1.25), scale=(2.3, 0.1, 1.5), size=1, parent=r)
    add('cube', '9AA4AC', (0.6, -0.1, 0.85), scale=(2.3, 0.1, 0.7), size=1, parent=r)
    for (x, y) in ((-0.4, 3.4), (1.6, 3.4), (-0.4, 0.0), (1.6, 0.0)):
        add('cylinder', '7A848C', (x, y, 0.2), radius=0.06, depth=0.4, vertices=6, parent=r)
    add('cube', 'FFFFFF', (0.6, 3.05, 1.35), rot=(-0.5, 0, 0), scale=(1.5, 0.3, 1.0), size=1, parent=r, rough=1.0)   # pillows propped up
    S['cover'] = add('cube', '6FA8B0', (0.6, 1.2, 1.04), scale=(2.0, 2.7, 0.56), size=1, parent=r, rough=1.0)
    add('cylinder', 'A8B0B8', (2.5, 3.0, 1.3), radius=0.035, depth=2.6, vertices=5, parent=r)                         # drip stand
    add('cube', 'DCEBF2', (2.5, 2.9, 2.4), scale=(0.3, 0.1, 0.5), size=1, parent=r, rough=0.3)
    add('cube', 'D8D4C8', (2.6, 3.2, 0.6), scale=(1.0, 0.7, 1.2), size=1, parent=r)                                  # bedside cabinet
    add('cube', '20242C', (2.6, 3.2, 1.55), scale=(0.7, 0.3, 0.6), size=1, parent=r)
    S['blip'] = add('cube', '6AFF8A', (2.5, 3.04, 1.6), scale=(0.1, 0.02, 0.06), size=1, parent=r, emit=8.0)
    # a chair on the window side of the bed
    c = empty((-1.25, 1.9, 0), r)
    add('cube', '4E6E8E', (0, 0, 0.75), scale=(0.9, 0.9, 0.12), size=1, parent=c)
    add('cube', '4E6E8E', (-0.4, 0, 1.4), scale=(0.1, 0.9, 1.2), size=1, parent=c)
    for (x, y) in ((-0.38, -0.38), (0.38, -0.38), (-0.38, 0.38), (0.38, 0.38)):
        add('cylinder', '2E3440', (x, y, 0.36), radius=0.04, depth=0.72, vertices=5, parent=c)
    S['roomlamp'] = light((0.4, 0.6, 3.8), 0, 'FFE8D0', 4.0, parent=r)
    S['roomlamp'].rotation_euler = (0, 0, 0)
    S['winlamp'] = light((-3.6, 1.15, 2.2), 0, 'FFB070', 2.2, parent=r)
    S['winlamp'].rotation_euler = (0, -PI / 2, 0)
    S['room'] = r
    S['roomall'] = kids(r)


def girl_head(head):
    d = K.human_head(SKIN, HAIR)(head)
    for s in (-1, 1):                                                      # two small bunches of hair
        add('ico_sphere', HAIR, (s * 0.27, 0.12, 0.16), radius=0.13, subdivisions=1, parent=head)
    return d


def woman_head(head):
    d = K.human_head('C89A78', '4A3424')(head)
    add('ico_sphere', '4A3424', (0, 0.2, 0.0), scale=(1.0, 0.8, 1.2), radius=0.26, subdivisions=1, parent=head)
    return d


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    S = {}
    make_sea(S)
    make_wreck(S)
    make_boat(S)
    make_room(S)
    S['sunball'] = add('ico_sphere', 'FFDCA0', FAR, radius=130, subdivisions=3, emit=7.0)
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    S['rook'].sc = 1.0
    S['girl'] = K.Rig(dict(top='E0705A', pants='2E3E66', hand=SKIN, boot=SKIN, fore=SKIN), girl_head)
    S['girl'].sc = 0.72
    S['crew'] = []
    for i, (sk, top) in enumerate((('6E4630', '2E7A8E'), ('8A5A3C', 'E8E4D4'), ('5E3A28', 'C8A23A'))):
        rig = K.Rig(dict(top=top, pants='2A2E3A', hand=sk, boot='1E2028', fore=sk), K.human_head(sk, '120F14'))
        rig.sc = 1.0
        S['crew'].append(rig)
    S['woman'] = K.Rig(dict(top='F0F2F4', pants='3E5A78', hand='C89A78', boot='2A2E3A', fore='F0F2F4'), woman_head)
    S['woman'].sc = 0.98
    S['humans'] = [S['girl']] + S['crew'] + [S['woman']]
    S['cast'] = [S['rook']] + S['humans']
    S['ring'] = rg = keep(empty(FAR))
    add('torus', 'FF5A1E', (0, 0, 0), major_radius=0.42, minor_radius=0.13, major_segments=12, minor_segments=5, parent=rg, rough=0.6)
    for i in range(4):
        add('cube', 'F4F4F0', (0.42 * math.cos(i * PI / 2), 0.42 * math.sin(i * PI / 2), 0), rot=(0, 0, i * PI / 2), scale=(0.3, 0.2, 0.29), size=1, parent=rg)
    S['lines'] = [keep(add('cylinder', 'F0E8D0', FAR, radius=0.5, depth=1, vertices=5, rough=0.9)) for _ in range(4)]
    S['wrap'] = keep(add('cone', 'D8C8A4', FAR, radius1=0.78, radius2=0.4, depth=1.25, vertices=8, rough=1.0))          # the bed covers round her
    S['wrap2'] = keep(add('cube', 'B89E78', FAR, scale=(1.3, 0.5, 0.2), size=1, rough=1.0))
    S['cup'] = keep(add('cone', 'F0F0EC', FAR, radius1=0.07, radius2=0.1, depth=0.16, vertices=8))
    S['fea'] = [keep(add('cone', '2F2B4D', FAR, radius1=0.07, radius2=0.0, depth=0.36, vertices=4)) for _ in range(2)]
    S['drops'] = [keep(add('ico_sphere', 'E6F4FA', FAR, radius=0.09, subdivisions=1, rough=0.3, emit=0.25)) for _ in range(16)]
    S['lamps'] = [light(FAR, 0, 'FFE2B0', kind='POINT') for _ in range(2)]
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
    w = bpy.data.worlds.new('w22')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = 0.0, 0.5
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
        rig.root.scale = (rig.sc,) * 3
        rig.face, rig.jawv = 'calm', 0.0
    for o, par, lc, rot, scl in _KEEP:
        o.parent = par
        o.location, o.rotation_euler, o.scale = lc, rot, scl
    S['sea'].hide_render = False
    vis(S['roomall'], False)
    vis(S['foam'], True)
    for l in S['lamps'] + [S['roomlamp'], S['winlamp'], S['sun'], S['fill']]:
        l.data.energy = 0
    for l in S['lamps']:
        l.location = FAR
    S.update(fillk=0.0, rface='calm', hat_tip=0.0, hat_jump=0.0, hat_off=0.0, amp=0.5, mode='night')
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinking and beak lip sync, once the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.41) % 1 < 0.035
    ez = dict(calm=0.07, low=0.045, shocked=0.13, sad=0.055, soft=0.06).get(e, 0.07)
    tilt = dict(low=-0.05, shocked=0.35, sad=0.45, soft=0.22).get(e, -0.22)
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip, off = S['hat_tip'], sm(S['hat_off'])
    r['hat'].rotation_euler = (lerp(-0.2 + tip * 0.35, 0.15, off), lerp(0.07, 1.3, off), 0)
    r['hat'].location = (lerp(0.0, 0.72, off), lerp(0.0, -0.12, off), lerp(0.27 + S['hat_jump'] + tip * 0.1, -1.5, off))
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.35 if e == 'shocked' else 0.0), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0), hd[1], hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.75, shut=0.07, tired=0.45, warm=0.85, sad=0.5).get(f, 1.0)
        bl = (t * 0.33 + 0.21 * j + 0.5) % 1 < 0.03 and k > 0.3
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.04 if f == 'wide' else -0.012 if f in ('sad', 'tired') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide') else 0.0), 0)
        x['mouth'].scale = (0.13 if f != 'warm' else 0.17, 0.03, 0.035 + 0.13 * rig.jawv)
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def sky(S, a, b=None, k=0.0):
    """Blend two skies (b, k) for the one shot in which the night turns into morning."""
    A = SKIES[a]
    B = SKIES[b] if b else A
    mixc = lambda i: tuple(lerp(x, y, k) for x, y in zip(K.hexc(A[i]), K.hexc(B[i])))
    S['skymix'].inputs[6].default_value = mixc(0)
    S['skymix'].inputs[7].default_value = mixc(1)
    S['bg'].inputs[1].default_value = lerp(A[2], B[2], k)
    S['sun'].data.energy = lerp(A[3], B[3], k)
    S['sun'].data.color = mixc(4)[:3]
    d = tuple(lerp(x, y, k) for x, y in zip(A[5], B[5]))
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = (d[0] * 500, d[1] * 500, d[2] * 500)
    b_ = S['seam'].node_tree.nodes.get('Principled BSDF')
    b_.inputs['Base Color'].default_value = mixc(6)
    S['fillk'] = lerp(A[8], B[8], k)
    return d


def sea(S, mode, t, amp=None, to=None, k=0.0, rook=None):
    """Sky and sea for this frame. The wreckage, Rook's panel and the debris ride the swell; she hangs on to the wreckage."""
    d = sky(S, mode, to, k)
    a = lerp(SKIES[mode][7], SKIES[to][7] if to else SKIES[mode][7], k) if amp is None else amp
    shape_sea(S, t, a)
    S['amp'], S['mode'] = a, mode
    low = mode in ('dawn', 'dusk') or to == 'dawn'
    sd = SKIES[to][5] if to else d
    S['sunball'].location = (sd[0] * 4200, sd[1] * 4200, sd[2] * 4200 - 560 - (1 - k) * 420 * (1 if to else 0)) if low else FAR
    S['wreck'].location = (0, 0, swell(0, 0, t, a))
    S['wreck'].rotation_euler = (0.09 * a * math.sin(1.25 * t + 0.6), 0.07 * a * math.sin(0.95 * t + 2.1), 0.04 * math.sin(0.3 * t))
    S['panel'].location = (RP[0], RP[1], swell(RP[0], RP[1], t, a))
    S['panel'].rotation_euler = (0.1 * a * math.sin(1.4 * t + 1.6), 0.09 * a * math.sin(1.1 * t + 0.3), 0)
    for i, (o, x, y) in enumerate(S['debris']):
        o.location = (x, y, swell(x, y, t, a) + 0.03)
        o.rotation_euler = (0.1 * math.sin(t * 1.2 + i), 0.1 * math.sin(t * 0.9 + 2 * i), 6 * rnd(i, 3) + 0.05 * t)


def hang(S, pose=None, x=GP[0], rise=0.0, yaw=PI, y=GP[1]):
    """She is in the water up to her chest, at the wreckage's near edge, both arms over it."""
    g = S['girl']
    g.root.parent = S['wreck']
    g.place((x, y, -1.12 + rise), yaw)
    g.apply(pose or HOLD())
    return g


def HOLD(slip=0.0, nod=-0.15, turn=0.0, **kw):
    d = dict(aL=(1.62 - 0.25 * slip, 0.12, 0.2 + 0.5 * slip), aR=(1.62 - 0.2 * slip, 0.12, 0.2 + 0.4 * slip), lean=0.24, head=(nod, turn),
             lL=(0.3, 0.5), lR=(-0.2, 0.3))
    d.update(kw)
    return P('stand', **d)


PERCH = dict(lL=(1.25, 1.95), lR=(1.25, 1.95), lift=-0.58, lean=0.3)       # Rook, crouched on a floating panel


def rook_on_panel(S, pose, yaw):
    rk = S['rook']
    rk.root.parent = S['panel']
    rk.place((0, 0, 0.16), yaw)
    rk.apply(pose)
    return rk


def rook_on_wreck(S, pose, yaw, x=RW[0], y=RW[1]):
    rk = S['rook']
    rk.root.parent = S['wreck']
    rk.place((x, y, 0.38), yaw)
    rk.apply(pose)
    return rk


def boat_at(S, x, y, yaw, t, roll=1.0):
    a = S['amp']
    S['boat'].location = (x, y, 0.5 * swell(x, y, t, a))
    S['boat'].rotation_euler = (0.06 * a * roll * math.sin(1.1 * t + 0.9), 0.04 * a * roll * math.sin(0.8 * t), yaw)


def aboard(S, rig, x, y, yaw=0.0, z=DECK):
    rig.root.parent = S['boat']
    rig.place((x, y, z), yaw)


def afloat(S, rig, x, y, yaw, depth, t, pitch=0.0):
    rig.place((x, y, swell(x, y, t, S['amp']) - depth), yaw, pitch)


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


def burst(S, pos, u, n=8, r=1.4, h=1.8, i0=0, s=1.0):
    """White water thrown up from pos; u is seconds since it began."""
    if u <= 0:
        return
    for i in range(n):
        a = i * 2.4 + 0.7
        q = 0.5 + 0.5 * rnd(i, 9)
        S['drops'][i0 + i].location = (pos[0] + r * q * u * math.cos(a), pos[1] + r * q * u * math.sin(a), pos[2] + h * q * u * 2 - 4.5 * u * u)
        z = s * (0.8 + rnd(i, 8))
        S['drops'][i0 + i].scale = (z, z, z)


def feather(S, pos, u):
    for i in range(2):
        if u <= 0:
            continue
        v = u * 1.2
        S['fea'][i].location = (pos[0] + (0.4 + i * 0.4) * v + 0.2 * math.sin(v * 6 + i), pos[1] - 0.3 * v, pos[2] + 0.7 * v - 1.0 * v * v)
        S['fea'][i].rotation_euler = (v * 5 + i, v * 3, i * 2.0)


def line(S, i, a, b, w=0.04):
    stretch(S['lines'][i], a, b, w)


def ghead(S):
    return wpos(S['girl'].head)


NIGHTC = 'CFE8F0'


# ---------------------------------------------------------------- the hook: alone in the sea at night
def girl_close(S, k, t, lt):
    """Close on her at the edge of the wreckage: both arms over it, eyes wide, a wave slapping the panel. First and last shot."""
    kk = 1 - k if S['prm'].get('loop') else k
    sea(S, 'night', t)
    slip = 0.5 + 0.5 * math.sin(kk * 7.0)
    g = hang(S, HOLD(slip=0.6 * slip, nod=-0.2, turn=0.25 * math.sin(kk * 4)), rise=0.1 * math.sin(kk * 6))
    g.face, g.jawv = 'wide', 0.25 + 0.25 * abs(math.sin(kk * 9))
    burst(S, (1.9, -1.5, 0.2), kk * 0.9 + 0.05, 8, 1.3, 1.5)
    hd = ghead(S)
    shoot(S, (lerp(1.75, 1.5, kk), lerp(0.1, -0.05, kk), lerp(0.95, 0.88, kk)), (hd[0] + 0.05, hd[1] + 0.2, hd[2] - 0.12), 52, fill=1.4, fcol=NIGHTC)


def hands_grip(S, k, t, lt):
    """Her hands on the torn edge: they slide back, then clamp down again. Her face behind them, out of focus."""
    sea(S, 'night', t)
    slip = sm(lt / 0.35) * (1 - sm((lt - 0.5) / 0.25))
    g = hang(S, HOLD(slip=slip, nod=0.05), rise=-0.12 * slip)
    g.face, g.jawv = 'wide', 0.5 * slip
    burst(S, (-0.6, -1.5, 0.15), lt - 0.3, 6, 0.9, 1.1, s=0.7)
    h = wpos(g.hands[1], (0, 0, -0.5))
    shoot(S, (lerp(2.0, 1.75, k), lerp(-2.5, -2.3, k), lerp(0.75, 0.65, k)), (h[0], h[1] - 0.15, h[2] + 0.12), 52, fill=1.3, fcol=NIGHTC)


def wide_night(S, k, t, lt):
    """From high up: one small figure at a piece of wreckage, debris scattered round it, black water in every direction."""
    sea(S, 'night', t)
    g = hang(S, HOLD(nod=-0.3, turn=0.5 * math.sin(lt * 2.5)))
    g.face = 'wide'
    shoot(S, (lerp(-4.8, -7.8, k), lerp(-7.2, -10.8, k), lerp(5.2, 8.8, k)), (0.5, -0.5, 0.0), 26, fill=2.2, fcol=NIGHTC)


def plane_piece(S, k, t, lt):
    """Along the wreckage: torn metal, ribs, a row of window holes. It is a piece of an airliner. She is at the far end of it."""
    sea(S, 'night', t)
    g = hang(S, HOLD(nod=-0.1, turn=-0.5), x=1.3)
    g.face = 'wide'
    shoot(S, (lerp(-5.4, -4.2, k), lerp(-3.4, -3.1, k), lerp(2.7, 2.4, k)), (lerp(-1.0, 0.2, k), -0.7, 0.2), 34, fill=1.6, fcol=NIGHTC)


def rook_lands(S, k, t, lt):
    """Behind her, a crow in a long coat flaps down onto a floating floor panel and sheds a feather."""
    sea(S, 'night', t)
    g = hang(S, HOLD(nod=-0.1, turn=1.1 * sm(lt / 0.4)), x=-0.3)
    g.face = 'wide'
    land = sm(lt / 0.6)
    fl = math.sin(lt * 24)
    rk = rook_on_panel(S, blend(P('up', aL=(1.5, 1.2 + 0.45 * fl, 0.2), aR=(1.5, 1.2 + 0.45 * fl, 0.2), lL=(0.4, 0.6), lR=(0.4, 0.6)),
                                P('stand', head=(0.25, 0.0), **PERCH), (lt - 0.5) / 0.3), facing(RP, (0.3, -1.6)))
    rk.root.location.z = 0.16 + 2.4 * (1 - land)
    S['rface'] = 'shocked' if lt < 0.75 else 'calm'
    feather(S, (RP[0] + 0.3, RP[1], 2.4), lt - 0.45)
    shoot(S, (lerp(-2.6, -2.2, k), lerp(-0.2, -0.4, k), lerp(1.5, 1.35, k)), (1.6, -3.0, 1.25), 30, fill=1.5, fcol=NIGHTC)


def rook_doubt(S, k, t, lt):
    """Rook crouched on his panel, low on the black water, the girl at the wreckage behind him: 'All night? At twelve?'"""
    sea(S, 'night', t)
    cam = (lerp(6.0, 5.6, k), lerp(-2.5, -2.7, k), lerp(1.7, 1.8, k))
    rk = rook_on_panel(S, blend(P('stand', head=(0.25, 0.0), **PERCH), P('cross', head=(0.0, 0.0), **PERCH), lt / 0.3), facing(RP, cam))
    S['rface'] = 'low'
    S['hat_tip'] = 0.5
    g = hang(S, HOLD(nod=-0.2, turn=0.3))
    g.face = 'wide'
    shoot(S, cam, (RP[0] - 0.3, RP[1] + 0.7, 1.6), 32, fill=1.5)


# ---------------------------------------------------------------- voices in the dark
def in_water(S, k, t, lt):
    """Straight down: she is a small shape at the edge of the panel, turning her head one way and the other; nothing else moves but the water."""
    sea(S, 'night', t)
    g = hang(S, HOLD(nod=-0.75, turn=0.7 * math.sin(lt * 4.0), slip=0.3))
    g.face, g.jawv = 'wide', 0.4
    shoot(S, (lerp(0.6, 0.3, k), lerp(-3.4, -3.0, k), lerp(6.5, 5.6, k)), (0.3, -1.2, 0.2), 30, roll=lerp(-0.25, 0.0, k), fill=1.8, fcol=NIGHTC)


def voices(S, k, t, lt):
    """Close: she lifts her chin and calls out, turning her head left, then right. Eyes wide."""
    sea(S, 'night', t)
    turn = 0.75 * math.sin(lt * 3.6)
    g = hang(S, HOLD(nod=-0.42, turn=turn, slip=0.2))
    g.face, g.jawv = 'wide', 0.55 + 0.4 * math.sin(lt * 7) ** 2
    hd = ghead(S)
    shoot(S, (lerp(-1.75, -1.45, k), lerp(-0.2, -0.45, k), lerp(1.0, 0.9, k)), (hd[0], hd[1] + 0.1, hd[2] - 0.1), 48, fill=1.4, fcol=NIGHTC)


def dark_look(S, k, t, lt):
    """Over her head, out into the dark: dim shapes of debris, no one. On his panel Rook cups a wing to the side of his head, listening."""
    sea(S, 'night', t)
    g = hang(S, HOLD(nod=-0.2, turn=PI * 0.8 + 0.4 * math.sin(lt * 3)))
    g.face = 'wide'
    rk = rook_on_panel(S, blend(P('stand', **PERCH), P('hat', aR=(0.3, 1.7, 1.9, -1.2), head=(-0.1, 0.5), **PERCH), lt / 0.4), facing(RP, (6, -12)) + 0.5)
    S['rface'] = 'calm'
    shoot(S, (lerp(-0.7, -0.3, k), lerp(1.9, 1.5, k), lerp(1.9, 1.75, k)), (1.7, -5.0, 0.7), 28, fill=1.7, fcol=NIGHTC)


def rook_quiet(S, k, t, lt):
    """Close on Rook: he lowers the wing, looks across at her, and his hat brim comes down. He says nothing."""
    sea(S, 'night', t)
    cam = (lerp(5.2, 4.8, k), lerp(-6.0, -5.6, k), lerp(1.35, 1.45, k))
    drop = sm((lt - 0.2) / 0.4)
    rk = rook_on_panel(S, blend(P('hat', aR=(0.3, 1.7, 1.9, -1.2), head=(-0.1, 0.5), **PERCH), P('stand', head=(0.3, 0.55), **PERCH), drop), facing(RP, cam))
    S['rface'] = 'sad'
    S['hat_tip'] = 0.7 * drop
    shoot(S, cam, (RP[0], RP[1], 1.95), 50, fill=1.4)


# ---------------------------------------------------------------- holding on
def big_wave(S, k, t, lt):
    """Low on the water: a black swell rises behind the wreckage and lifts it, and her with it; white water breaks over the edge."""
    sea(S, 'night', t, 1.5)
    g = hang(S, HOLD(nod=0.1, slip=0.5 * math.sin(lt * 4) ** 2), rise=0.1)
    g.face, g.jawv = 'shut', 0.0
    burst(S, (0.2, -0.9, 0.5 + S['wreck'].location.z), lt - 0.35, 12, 1.8, 2.2, s=1.2)
    shoot(S, (lerp(3.4, 2.9, k), lerp(-6.4, -5.8, k), lerp(0.7, 1.1, k)), (0.2, -1.0, 1.0), 26, roll=0.1 * math.sin(lt * 2.2), fill=1.5, fcol=NIGHTC)


def climb_try(S, k, t, lt):
    """She heaves herself up on straight arms; the panel tips towards her and she slides back into the water. Rook half rises on his panel."""
    sea(S, 'night', t, 0.8)
    up = sm(lt / 0.5) * (1 - sm((lt - 0.7) / 0.3))
    g = hang(S, blend(HOLD(), P('stand', aL=(0.95, 0.2, 0.1), aR=(0.95, 0.2, 0.1), lean=0.5, head=(-0.1, 0.0), lL=(0.9, 1.0), lR=(0.1, 0.4)), up), rise=0.75 * up)
    g.face, g.jawv = ('shut', 0.3) if up > 0.3 else ('wide', 0.5)
    S['wreck'].rotation_euler = (S['wreck'].rotation_euler[0] + 0.3 * up, S['wreck'].rotation_euler[1], 0)
    burst(S, (0.3, -1.9, 0.0), lt - 0.85, 8, 1.2, 1.4)
    rk = rook_on_panel(S, blend(P('stand', head=(0.1, 0.0), **PERCH), P('stand', aL=(0.9, 0.5, 0.4), aR=(0.9, 0.5, 0.4), lL=(0.9, 1.3), lR=(0.9, 1.3), lift=-0.35, lean=0.5), up),
                       facing(RP, (0.3, -1.7)))
    S['rface'] = 'shocked' if up > 0.4 else 'calm'
    shoot(S, (lerp(-2.9, -2.5, k), lerp(-4.3, -3.9, k), lerp(1.0, 1.25, k)), (1.0, -2.4, 0.95), 25, fill=1.6, fcol=NIGHTC)


def hold_on(S, k, t, lt):
    """Her cheek goes down on her arm. Rook has crossed to the wreckage: he crouches at the edge beside her and puts a wing on it, next to her hands."""
    sea(S, 'night', t)
    g = hang(S, HOLD(nod=lerp(-0.1, 0.3, sm(lt / 0.6)), turn=0.35, slip=0.1), rise=0.12)
    g.face = 'tired'
    rk = rook_on_wreck(S, blend(P('stand', head=(0.3, 0.3), **PERCH), P('stand', aL=(1.05, 0.25, 0.3), head=(0.35, -0.3), **PERCH), (lt - 0.2) / 0.4), facing(RW, (0.3, -2.4)))
    S['rface'] = 'sad'
    hd = ghead(S)
    shoot(S, (lerp(0.9, 0.7, k), lerp(3.4, 3.0, k), lerp(1.05, 1.15, k)), (hd[0] - 0.6, hd[1] + 0.5, hd[2] + 0.6), 33, fill=1.5, fcol=NIGHTC)


def face_tired(S, k, t, lt):
    """Very close: her eyes close, open, close; her head sinks and jerks back up. Hour after hour."""
    sea(S, 'night', t, 0.45)
    nod = 0.3 * sm(lt / 0.5) * (1 - sm((lt - 0.62) / 0.12))
    g = hang(S, HOLD(nod=nod, turn=0.15, slip=0.15))
    g.face = 'shut' if 0.3 < lt < 0.66 or lt > 1.0 else 'tired'
    hd = ghead(S)
    shoot(S, (lerp(0.9, 0.75, k), lerp(0.3, 0.1, k), lerp(0.95, 0.85, k)), (hd[0], hd[1] + 0.12, hd[2] - 0.3), 58, fill=1.3, fcol=NIGHTC)


def dawn_break(S, k, t, lt):
    """Wide and low: the sky behind them goes from black to orange and the sun comes up out of the sea. Two small shapes at the wreckage."""
    sea(S, 'night', t, to='dawn', k=sm(k * 1.15))
    g = hang(S, HOLD(nod=0.2, slip=0.1))
    g.face = 'tired'
    rk = rook_on_wreck(S, P('stand', aL=(1.05, 0.25, 0.3), head=(0.2, -0.2), **PERCH), facing(RW, (0.3, -2.4)))
    S['rface'] = 'sad'
    shoot(S, (lerp(-6.6, -5.6, k), lerp(-5.6, -5.0, k), lerp(0.9, 1.2, k)), (0.6, -0.8, 1.0), 30, fill=1.2)


def morning(S, k, t, lt):
    """Grey morning, a bigger sea. She is still there, arms over the edge, head up now, looking round. Rook still has his wing on the panel."""
    sea(S, 'grey', t)
    g = hang(S, HOLD(nod=-0.2, turn=0.9 - 1.2 * sm(lt / 0.8)))
    g.face = 'tired'
    rk = rook_on_wreck(S, P('stand', aL=(1.05, 0.25, 0.3), head=(0.1, 0.9 - 0.9 * sm(lt / 0.7)), **PERCH), facing(RW, (4.4, -0.6)))
    S['rface'] = 'soft'
    shoot(S, (lerp(4.4, 3.9, k), lerp(0.9, 0.6, k), lerp(1.7, 1.5, k)), (0.6, -1.3, 1.05), 33, fill=1.0)


# ---------------------------------------------------------------- the re-hook: a boat, and a life ring she cannot reach
def boat_far(S, k, t, lt):
    """From behind her: across the wreckage, on the horizon, a white boat. Rook jumps to his feet and points at it with his whole wing."""
    sea(S, 'grey', t)
    boat_at(S, lerp(-22, -14, k), 62, -0.5, t)
    g = hang(S, HOLD(nod=-0.35, turn=0.1), rise=0.12 * sm(lt / 0.4))
    g.face = 'wide'
    up = sm(lt / 0.35)
    rk = rook_on_wreck(S, blend(P('stand', **PERCH), P('point', aR=(1.5, 0.15, 0.05), head=(-0.1, 0.0)), up), facing(RW, (-18, 62)))
    S['rface'] = 'shocked'
    S['hat_jump'] = 0.18 * math.sin(min(1.0, lt / 0.4) * PI)
    shoot(S, (lerp(1.6, 1.3, k), lerp(-5.6, -5.0, k), lerp(1.5, 1.7, k)), (-1.0, 3.0, 1.9), 30, fill=1.1)


def boat_near(S, k, t, lt):
    """The boat comes on, bow up, foam at the stem. Two crewmen at the rail lean out and point down at her."""
    sea(S, 'grey', t)
    bx, by = lerp(-6, -3.5, k), lerp(17, 12.5, k)
    boat_at(S, bx, by, -1.05, t, 1.6)
    for i, (x, y) in enumerate(((4.6, -2.0), (3.2, -2.05))):
        c = S['crew'][i]
        aboard(S, c, x, y, 0.5)
        c.apply(P('point', aR=(1.15, 0.2, 0.1), aL=(0.9, 0.5, 0.6), lean=0.3, head=(0.25, 0.0)))
        c.face, c.jawv = 'wide', 0.5 + 0.3 * math.sin(lt * 9 + i)
    g = hang(S, HOLD(nod=-0.4))
    g.face = 'wide'
    shoot(S, (lerp(2.6, 2.2, k), lerp(4.2, 4.6, k), lerp(1.5, 1.7, k)), (bx + 1.5, by - 2.0, 2.0), 28, roll=0.06 * math.sin(lt * 2), fill=1.0)


def crew_at_rail(S, t, lean=0.3):
    for i, x in enumerate((-2.2, 0.4, 2.6)):
        c = S['crew'][i]
        aboard(S, c, x, -2.0, 0.0)
        c.apply(P('stand', aL=(0.7, 0.3, 0.5), aR=(0.7, 0.3, 0.5), lean=lean, head=(0.3, 0.0)))
        c.face = 'wide'


def ring_throw(S, k, t, lt):
    """From the deck, over the crew's shoulders: one of them swings back and throws an orange life ring; it sails out on its line towards her."""
    sea(S, 'grey', t)
    boat_at(S, BOAT[0], BOAT[1], 0.0, t)
    crew_at_rail(S, t)
    c = S['crew'][1]
    thr = sm((lt - 0.25) / 0.2)
    c.apply(blend(P('stand', aR=(-0.9, 0.3, 0.9), aL=(0.9, 0.3, 0.3), lean=-0.1, head=(0.1, 0.0)), P('stand', aR=(1.7, 0.1, 0.1), aL=(0.3, 0.4, 0.4), lean=0.45, head=(0.3, 0.0)), thr))
    c.jawv = 0.6
    hnd = wpos(c.hands[1], (0, 0, -0.6))
    fly = sm((lt - 0.35) / 0.65)
    end = (0.9, 2.9, swell(0.9, 2.9, t, S['amp']) + 0.1)
    pos = hnd if lt < 0.38 else (lerp(hnd[0], end[0], fly), lerp(hnd[1], end[1], fly), lerp(hnd[2], end[2], fly) + 2.6 * math.sin(fly * PI))
    S['ring'].location = pos
    S['ring'].rotation_euler = (lt * 5, lt * 3, 0)
    if lt >= 0.38:
        line(S, 0, wpos(c.hands[0], (0, 0, -0.5)), pos)
    g = hang(S, HOLD(nod=-0.5, slip=0.2), yaw=PI)
    g.face = 'wide'
    rook_on_wreck(S, P('stand', head=(-0.1, 0.0), **PERCH), facing(RW, BOAT))
    shoot(S, (BOAT[0] + lerp(0.2, 0.5, k), BOAT[1] + lerp(1.1, 0.7, k), DECK + lerp(3.3, 3.0, k)), (0.6, 2.2, 0.6), 24, fill=0.9)


def ring_miss(S, k, t, lt):
    """Water level: the ring slaps down between the boat and the wreckage, and the next swell carries it off sideways. Her arm comes out towards it."""
    sea(S, 'grey', t, 1.25)
    boat_at(S, BOAT[0], BOAT[1], 0.0, t)
    crew_at_rail(S, t)
    x, y = lerp(0.9, 4.2, sm(k)), lerp(2.9, 3.6, k)
    pos = (x, y, swell(x, y, t, S['amp']) + 0.1)
    S['ring'].location = pos
    S['ring'].rotation_euler = (0.2 * math.sin(lt * 5), 0.2 * math.cos(lt * 4), lt)
    line(S, 0, wpos(S['crew'][1].hands[1], (0, 0, -0.5)), pos)
    burst(S, (0.9, 2.9, 0.1), lt + 0.05, 8, 1.3, 1.4)
    g = hang(S, HOLD(nod=-0.3, aR=(1.75, -0.2, 0.05)), y=-1.55, rise=0.2)
    g.face, g.jawv = 'wide', 0.4
    shoot(S, (lerp(-4.2, -3.7, k), lerp(0.7, 1.0, k), lerp(1.9, 1.7, k)), (lerp(1.2, 2.2, k), 3.2, 0.3), 28, roll=0.12 * math.sin(lt * 2.5), fill=1.0)


def reach_fail(S, k, t, lt):
    """Close: her arm at full stretch across the panel, fingers open; the ring slides away past the camera. Beside her Rook stretches a wing after it too."""
    sea(S, 'grey', t, 1.1)
    st = sm(lt / 0.35)
    g = hang(S, blend(HOLD(), HOLD(aR=(1.85, -0.15, 0.0), nod=-0.45, lean=0.5), st), y=-1.5, rise=0.25 * st)
    g.face, g.jawv = 'wide', 0.5
    rk = rook_on_wreck(S, blend(P('stand', **PERCH), P('stand', aR=(1.6, 0.0, 0.0), head=(-0.15, 0.0), lL=(1.25, 1.95), lR=(1.25, 1.95), lift=-0.58, lean=0.75), st), PI, x=1.9, y=-0.8)
    S['rface'] = 'shocked'
    x, y = lerp(0.5, 1.7, k), lerp(1.75, 2.3, k)
    S['ring'].location = (x, y, swell(x, y, t, S['amp']) + 0.12)
    S['ring'].rotation_euler = (0.15 * math.sin(lt * 5), 0.1, lt)
    line(S, 0, (x, y, 0.2), (x + 0.5, y + 5.2, 2.6))
    hd = ghead(S)
    shoot(S, (lerp(0.4, 0.6, k), lerp(4.3, 4.0, k), lerp(2.3, 2.15, k)), (hd[0] + 0.45, hd[1] + 1.1, hd[2] + 0.1), 34, fill=1.1)


# ---------------------------------------------------------------- the rescue
def sailor_jump(S, k, t, lt):
    """From the water: one sailor goes over the rail and drops feet first into the swell in a burst of white water. The others lean out after him."""
    sea(S, 'grey', t, 1.1)
    boat_at(S, BOAT[0], BOAT[1], 0.0, t)
    crew_at_rail(S, t, 0.45)
    s = S['crew'][0]
    j = sm(lt / 0.55)
    s.root.parent = None
    z0 = DECK + 1.3
    x, y = -1.7, lerp(7.3, 5.6, j)
    z = lerp(z0, -1.6, j * j) + 1.2 * math.sin(min(1.0, j * 1.6) * PI) * (1 - j)
    s.place((x, y, z + 0.5 * swell(x, y, t, S['amp'])), 0.0, -0.3 * (1 - j))
    s.apply(blend(P('up', lL=(0.9, 1.2), lR=(0.3, 0.6)), P('up', aL=(2.4, 0.6, 0.2), aR=(2.4, 0.6, 0.2)), j))
    s.face, s.jawv = 'wide', 0.6
    burst(S, (x, 5.6, 0.1), lt - 0.5, 14, 2.2, 2.4, s=1.3)
    shoot(S, (lerp(3.6, 3.1, k), lerp(2.4, 2.8, k), lerp(0.6, 0.8, k)), (-0.9, 6.9, lerp(2.4, 1.6, k)), 26, roll=0.08 * math.sin(lt * 3), fill=1.0)


def sailor_swim(S, k, t, lt):
    """From above: he comes round the end of the wreckage, gets an arm round her, and her hands let go of the panel. Rook leans down, watching."""
    sea(S, 'grey', t, 0.9)
    s = S['crew'][0]
    a = sm(lt / 0.6)
    x, y = lerp(3.6, 1.25, a), lerp(-0.9, -1.95, a)
    afloat(S, s, x, y, facing((x, y), (0.3, -1.8)), 1.55, t)
    st = math.sin(lt * 9)
    s.apply(blend(P('swim', aL=(2.2 + 0.6 * st, 0.3, 0.3), aR=(2.2 - 0.6 * st, 0.3, 0.3), lean=0.4, head=(-0.5, 0.0)),
                  P('stand', aR=(1.3, -0.5, 0.6), aL=(1.2, 0.4, 0.4), lean=0.2, head=(0.1, 0.0)), (lt - 0.5) / 0.3))
    s.face = 'calm'
    go = sm((lt - 0.7) / 0.3)
    g = hang(S, blend(HOLD(nod=-0.3, turn=-0.7), P('stand', aL=(1.2, 0.3, 0.5), aR=(0.9, 0.5, 0.8), head=(-0.2, -0.9), lean=0.1), go))
    g.face = 'wide'
    burst(S, (x + 0.5, y, 0.0), lt * 0.7, 8, 1.0, 0.9, s=0.8)
    rk = rook_on_wreck(S, P('stand', head=(0.45, 0.0), aL=(0.6, 0.4, 0.5), aR=(0.6, 0.4, 0.5), lL=(1.25, 1.95), lR=(1.25, 1.95), lift=-0.58, lean=0.55), PI + 0.5, x=-1.7, y=-0.3)
    S['rface'] = 'soft'
    shoot(S, (lerp(2.4, 2.0, k), lerp(-5.4, -5.0, k), lerp(4.4, 3.8, k)), (0.8, -1.5, 0.4), 32, fill=1.1)


def lift_aboard(S, k, t, lt):
    """At the boat's side: the sailor in the water pushes her up; two crewmen hang over the rail and take her under the arms."""
    sea(S, 'grey', t, 0.8)
    boat_at(S, BOAT[0], BOAT[1], 0.0, t, 0.5)
    up = sm(lt / 0.8)
    for i, x in enumerate((0.0, 1.5)):
        c = S['crew'][i + 1]
        aboard(S, c, x, -2.05, 0.0)
        c.apply(P('stand', aL=(0.5, 0.2, 0.2), aR=(0.5, 0.2, 0.2), lean=1.15, head=(-0.6, 0.0), lift=-0.15))
        c.face = 'calm'
    g = S['girl']
    gx, gy = BOAT[0] + 0.75, 6.95
    g.place((gx, gy, lerp(-1.2, 0.35, up) + 0.5 * swell(gx, gy, t, S['amp'])), PI)
    g.apply(P('up', aL=(2.7, 0.2, 0.15), aR=(2.7, 0.2, 0.15), head=(-0.5, 0.0)))
    g.face = 'tired'
    s = S['crew'][0]
    afloat(S, s, gx + 0.2, 6.1, PI, 1.5 - 0.3 * up, t)
    s.apply(P('up', aL=(2.3, 0.1, 0.2), aR=(2.3, 0.1, 0.2), head=(-0.5, 0.0)))
    burst(S, (gx, 6.6, 0.0), lt * 0.8, 8, 1.0, 1.0, s=0.8)
    shoot(S, (lerp(4.2, 3.7, k), lerp(3.6, 3.9, k), lerp(0.7, 1.1, k)), (gx, 7.1, lerp(1.3, 1.9, k)), 30, roll=0.05 * math.sin(lt * 3), fill=1.1)


def on_deck(S, t, sip=0.0, turn=0.0, sea_mode='grey'):
    """She sits on the locker wrapped in bed covers; a crewman crouches in front of her with a cup."""
    sea(S, sea_mode, t, 0.6)
    boat_at(S, 0, 40, 0.0, t, 0.6)
    g = S['girl']
    aboard(S, g, 2.6, 0.75, PI / 2 - 0.3, DECK + 0.62 - 0.55 * 0.72)
    g.apply(P('sit', aL=(0.6, -0.1, 1.4, 0.8), aR=(lerp(0.6, 1.0, sip), -0.15, lerp(1.4, 2.0, sip), 0.6), head=(lerp(0.2, -0.05, sip), turn), lean=0.15, lift=-0.5))
    S['wrap'].parent = g.body
    S['wrap'].location, S['wrap'].rotation_euler, S['wrap'].scale = (0, 0.02, 0.55), (0, 0, 0), (1.25, 1.25, 1.25)
    S['wrap2'].parent = g.body
    S['wrap2'].location, S['wrap2'].rotation_euler, S['wrap2'].scale = (0, -0.05, 1.13), (0.1, 0, 0), (1.3, 0.75, 0.24)
    c = S['crew'][1]
    aboard(S, c, 3.7, -0.75, facing((3.7, -0.75), (2.6, 0.75)))
    c.apply(P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.76, lean=0.3, aR=(1.2, 0.0, 0.5), aL=(0.4, 0.2, 0.6), head=(-0.1, 0.0)))
    c.face = 'warm'
    return g, c


def blanket(S, k, t, lt):
    """On deck: she is wrapped in bed covers on a locker; a crewman crouches and holds out a cup; she takes it in both hands. Rook sits on the rail, brows soft."""
    take = sm((lt - 0.4) / 0.4)
    g, c = on_deck(S, t, sip=0.5 * take)
    g.face = 'tired'
    S['cup'].location = wpos(g.hands[1], (0, -0.5, -0.9)) if take > 0.5 else wpos(c.hands[1], (0, -0.4, -0.9))
    c2 = S['crew'][2]
    aboard(S, c2, 0.7, 1.4, facing((0.7, 1.4), (2.6, 0.75)))
    c2.apply(P('hips', head=(0.2, 0.0)))
    rk = S['rook']
    aboard(S, rk, 1.2, -2.38, facing((1.2, -2.38), (2.6, 0.75)), DECK + 0.95 - 0.5)
    rk.apply(P('sit', head=(0.15, 0.0)))
    S['rface'] = 'soft'
    b = S['boat'].location
    shoot(S, (b[0] + lerp(6.9, 6.3, k), b[1] + lerp(1.9, 1.6, k), DECK + lerp(1.8, 1.65, k)), (b[0] + 2.5, b[1] + 0.1, DECK + 1.15), 28, fill=1.6, fcol='FFE0C0')


def alive(S, k, t, lt):
    """Close on her face above the covers: she drinks from the cup, lowers it, and her eyes open. She's alive."""
    sip = math.sin(min(1.0, lt / 0.9) * PI)
    g, c = on_deck(S, t, sip=sip)
    g.face = 'shut' if sip > 0.6 else 'warm'
    S['cup'].location = wpos(g.hands[1], (0, -0.5, -0.9))
    S['cup'].rotation_euler = (0.7 * sip, 0, 0)
    hd = ghead(S)
    shoot(S, (hd[0] + lerp(2.7, 2.3, k), hd[1] + lerp(0.5, 0.35, k), hd[2] + 0.25), (hd[0], hd[1], hd[2] - 0.42), 46, fill=1.5, fcol='FFE0C0')


# ---------------------------------------------------------------- what she believed
def look_back(S, k, t, lt):
    """Seen from the sea: she sits at the rail in her covers and looks back over the water. Rook sits on the rail beside her and looks the same way."""
    sea(S, 'grey', t, 0.6)
    boat_at(S, 0, 40, 0.0, t, 0.6)
    g = S['girl']
    aboard(S, g, 2.2, -1.5, 0.0, DECK + 0.35)
    g.apply(P('sit', aL=(0.6, -0.1, 1.4, 0.8), aR=(0.6, -0.1, 1.4, 0.8), head=(0.05, 0.5 * math.sin(lt * 1.2)), lean=0.1, lift=-0.5))
    g.face = 'sad'
    S['wrap'].parent = g.body
    S['wrap'].location, S['wrap'].rotation_euler, S['wrap'].scale = (0, 0.02, 0.55), (0, 0, 0), (1.25, 1.25, 1.25)
    S['wrap2'].parent = g.body
    S['wrap2'].location, S['wrap2'].rotation_euler, S['wrap2'].scale = (0, -0.05, 1.13), (0.1, 0, 0), (1.3, 0.75, 0.24)
    vis(S['rails'][0:2], False)
    rk = S['rook']
    aboard(S, rk, 3.7, -2.38, 0.3, DECK + 0.95 - 0.5)
    rk.apply(P('sit', head=(0.1, 0.45)))
    S['rface'] = 'sad'
    b = S['boat'].location
    shoot(S, (b[0] + lerp(4.4, 4.0, k), b[1] - lerp(6.6, 6.0, k), lerp(2.2, 2.5, k)), (b[0] + 2.8, b[1] - 1.8, DECK + 1.55), 40, fill=1.3)


def room(S, t, sit=0.25):
    """The hospital room in evening light; she sits up in the bed against the pillows."""
    sky(S, 'dusk')
    S['sea'].hide_render = True
    S['sun'].data.energy = 0
    vis(S['roomall'], True)
    S['roomlamp'].data.energy = 700
    S['winlamp'].data.energy = 900
    S['fillk'] = 1.0
    S['blip'].hide_render = (t * 1.6) % 1 > 0.5
    S['curtain'].rotation_euler = (0, 0.05 * math.sin(t * 1.3), 0.04 * math.sin(t * 0.9))
    g = S['girl']
    g.root.parent = S['room']
    g.place((0.6, 2.55, 1.0 - 0.55 * 0.72), 0.0)
    g.face = 'sad'
    return g


def RM(x, y, z):
    return (ROOM[0] + x, ROOM[1] + y, ROOM[2] + z)


BED = dict(lL=(1.45, 0.1), lR=(1.45, 0.1), lift=-0.5, lean=-0.25, aL=(0.5, 0.15, 0.5), aR=(0.5, 0.15, 0.5))


def hospital_wait(S, k, t, lt):
    """The breath before: a quiet room, evening in the window, the curtain moving. She sits up in the bed and looks at the door."""
    g = room(S, t)
    g.apply(P('stand', head=(0.0, lerp(0.7, -0.5, sm(lt / 0.8))), **BED))
    g.face = 'calm'
    shoot(S, RM(lerp(2.6, 2.1, k), lerp(-3.3, -2.9, k), lerp(2.3, 2.1, k)), RM(0.1, 2.2, 1.45), 26, fill=0.7)


def hospital_tell(S, k, t, lt):
    """A woman in a white coat sits by the bed, leans in and puts a hand on the girl's hand. The girl looks at her, eyes wide."""
    g = room(S, t)
    g.apply(P('stand', head=(0.05, lerp(0.3, -0.8, sm(lt / 0.7))), **dict(BED, aL=(0.5, 0.15, 0.5 + 0.3 * sm((lt - 0.9) / 0.4)))))
    g.face = 'wide' if lt > 0.9 else 'calm'
    w = S['woman']
    w.root.parent = S['room']
    w.place((-1.25, 1.9, 0.81 - 0.5), -PI / 2 - 0.25)
    lean = sm((lt - 0.2) / 0.6) * (0.85 + 0.15 * math.sin(lt * 5))
    w.apply(P('sit', aR=(lerp(0.7, 1.35, lean), 0.0, lerp(1.4, 0.35, lean)), lean=lerp(0.15, 0.5, lean), head=(lerp(0.1, -0.15, lean), 0.0)))
    w.face, w.jawv = 'sad', 0.25 + 0.25 * math.sin(lt * 8) ** 2
    shoot(S, RM(lerp(-2.6, 0.2, k), lerp(-2.6, -1.5, k), lerp(2.3, 1.7, k)), RM(-0.8, 2.2, 1.35), 30, fill=0.8)


def her_face(S, k, t, lt):
    """Close on her: her eyes go from wide to shut and her head goes down. At the window behind her Rook takes his hat off and holds it at his side."""
    g = room(S, t)
    dn = sm((lt - 0.45) / 0.5)
    g.apply(P('stand', head=(lerp(0.0, 0.5, dn), lerp(0.6, 0.1, dn)), **BED))
    g.face = 'shut' if dn > 0.6 else 'wide'
    rk = S['rook']
    rk.root.parent = S['room']
    rk.place((-1.5, 3.1, 0.0), facing((-1.5, 3.1), (1.6, -2.0)))
    off = sm((lt - 0.3) / 0.5)
    rk.apply(blend(P('stand'), P('stand', aR=(0.15, 0.3, 0.25), head=(0.35, 0.0)), off))
    S['rface'] = 'sad'
    S['hat_off'] = off
    hd = ghead(S)
    shoot(S, (hd[0] + lerp(1.5, 1.25, k), hd[1] - lerp(2.6, 2.3, k), hd[2] + 0.2), (hd[0] - 0.6, hd[1], hd[2] + 0.25), 34, fill=0.8)


def empty_chair(S, k, t, lt):
    """Her hand on the cover; beyond it, the chair by the bed, empty now, the evening light across its seat."""
    g = room(S, t)
    g.apply(P('stand', head=(0.5, 0.3), **BED))
    g.face = 'shut'
    shoot(S, RM(lerp(1.3, 0.9, k), lerp(-2.0, -1.7, k), lerp(2.2, 2.0, k)), RM(-0.9, 1.9, 1.0), 34, fill=0.6)


def rook_wrong(S, k, t, lt):
    """Rook at the window, hat held at his side, head bowed, the evening behind him: 'I was wrong.'"""
    g = room(S, t)
    g.apply(P('stand', head=(0.5, 0.1), **BED))
    g.face = 'shut'
    rk = S['rook']
    rk.root.parent = S['room']
    cam = RM(lerp(-0.5, -0.8, k), lerp(-1.9, -1.6, k), lerp(1.9, 1.95, k))
    rk.place((-3.3, 0.6, 0.0), facing((-3.3, 0.6), (-0.5, -1.9)))
    rk.apply(P('stand', aR=(0.15, 0.3, 0.25), head=(lerp(0.4, 0.15, sm(lt / 0.5)), 0.0)))
    S['rface'] = 'sad'
    S['hat_off'] = 1.0
    shoot(S, cam, RM(-3.2, 0.6, 1.95), 40, fill=0.9)


# ---------------------------------------------------------------- the sea afterwards, and the sign-off
def sea_after(S, k, t, lt):
    """Morning, from high up: the piece of wreckage alone on a wide, empty sea, small pieces of debris round it. No one."""
    sea(S, 'grey', t, 1.0)
    shoot(S, (lerp(-5.0, -12.5, k), lerp(-8.0, -17.0, k), lerp(5.0, 14.0, k)), (lerp(0.3, 1.0, k), lerp(0.0, 2.0, k), 0.0), 24, fill=1.0)


def debris_close(S, k, t, lt):
    """Low on the grey water: a seat cushion and a small case ride the swell past the camera. Nothing else."""
    sea(S, 'grey', t, 1.1)
    shoot(S, (lerp(-3.6, -4.6, k), lerp(-6.4, -5.2, k), lerp(0.9, 1.3, k)), (-6.5, -4.0, 0.2), 30, roll=0.1 * math.sin(lt * 2.4), fill=1.0)


def signoff(S, k, t, lt):
    """Dusk. Rook on his floating panel, the hat in his hand at his side; he puts it back on and pulls the brim down."""
    sea(S, 'dusk', t)
    cam = (lerp(5.3, 4.9, k), lerp(-6.4, -6.0, k), lerp(2.0, 2.1, k))
    on_ = sm((lt - 0.25) / 0.4)
    rk = rook_on_panel(S, blend(P('stand', aR=(0.15, 0.3, 0.25), head=(0.3, 0.0)), P('hat', head=(0.2, 0.0)), on_), facing(RP, cam))
    rk.apply(blend(P('stand', aR=(0.15, 0.3, 0.25), head=(0.3, 0.0)), blend(P('hat', head=(0.2, 0.0)), P('stand', head=(0.25, 0.0)), (lt - 0.75) / 0.3), on_))
    S['rface'] = 'sad'
    S['hat_off'] = 1 - on_
    S['hat_tip'] = 0.8 * sm((lt - 0.6) / 0.3)
    shoot(S, cam, (RP[0], RP[1], 3.0), 36, fill=1.3)


def photo_girl(S, k, t, lt):
    """The photograph on Rook's board: the wreckage on the night sea, the girl at its edge."""
    sea(S, 'night', 3.0)
    g = hang(S, HOLD(nod=-0.2, turn=0.2))
    g.face = 'wide'
    shoot(S, (1.9, 1.0, 1.35), (0.35, -1.5, 0.5), 46, fill=2.2, fcol=NIGHTC)


SHOTS3D = {f.__name__: f for f in (
    girl_close, hands_grip, wide_night, plane_piece, rook_lands, rook_doubt, in_water, voices, dark_look, rook_quiet, big_wave, climb_try, hold_on,
    face_tired, dawn_break, morning, boat_far, boat_near, ring_throw, ring_miss, reach_fail, sailor_jump, sailor_swim, lift_aboard, blanket, alive,
    look_back, hospital_wait, hospital_tell, her_face, empty_chair, rook_wrong, sea_after, debris_close, signoff)}
STILLS = dict(girl=photo_girl)


# ================================================================ long-form extension (16:9 full case file)
# The Short's sea, wreckage, boat and hospital room stay as they were. New for the full case, each built at its own
# origin and shown only in its own shots: a small Paris flat on the evening before they leave, a departure lounge at
# night with a plain airliner outside the glass, the cabin of an airliner at night (the crash itself is never shown:
# the film cuts to a drawn card before anything happens), the dark coast of an island in a strong wind, an airport
# apron on an overcast day with a small government jet, and a Paris courtroom in 2022. New figures: her mother, her
# father, her two brothers and her sister, Bahia at twenty-five, and seated passengers, judges and families made of a
# few blocks each. All of it is generic: no airline livery, name, number, flag, emblem, logo or lettering anywhere,
# none of the places is a model of the real one, and nobody's likeness is attempted.
SETPOS = dict(flat=(80.0, 0.0, 600.0), lounge=(160.0, 0.0, 600.0), cabin=(240.0, 0.0, 600.0), court=(320.0, 0.0, 600.0), apron=(520.0, 0.0, 600.0))
ISLE = (0.0, 330.0, 0.0)           # the island's coast, out on the sea far beyond the debris
CAMFILL.update(flat_pack=160, doorway=160, lounge=200, cabin_seats=200, cabin_shake=220, bahia_look=200, window_dark=60, island_night=420,
               jet_arrive=60, stairs=120, father_hug=140, court_wide=140, testify=160, families=150, verdict=150, court_rook=170)
HOST |= {'flat_pack', 'doorway', 'lounge', 'cabin_seats', 'island_night', 'stairs', 'court_wide', 'court_rook'}
MOMC = dict(top='B8486A', pants='3A2E48', hand=SKIN, boot='2A2228', fore='B8486A')
DADC = dict(top='4E6A8A', pants='2A2E3A', hand='6E4630', boot='1E2028', fore='4E6A8A')
ADULTC = dict(top='2E3E5C', pants='22262E', hand=SKIN, boot='1A1C22', fore='2E3E5C')
KIDS = (('3E8E5A', '2A3448', 0.56), ('E0A030', '2A3448', 0.5), ('7A5AB0', '3A2E48', 0.46))   # two brothers and a sister


def box(col, loc, scale, parent=None, rot=(0, 0, 0), **kw):
    return add('cube', col, loc, rot=rot, scale=scale, size=1, parent=parent, **kw)


def bun_head(skin, hair, wrap=None):
    def fn(head):
        d = K.human_head(skin, hair)(head)
        add('ico_sphere', wrap or hair, (0, 0.24, 0.2), scale=(1.0, 0.9, 0.9), radius=0.2, subdivisions=1, parent=head)
        if wrap:                                                   # a plain scarf over the hair
            add('ico_sphere', wrap, (0, 0.06, 0.13), scale=(1.0, 1.02, 0.98), radius=0.31, subdivisions=1, parent=head)
        return d
    return fn


def sitter(par, loc, top, skin, hair, yaw=0.0, s=1.0):
    """A seated figure from a few blocks (passengers, families, judges): body, shoulders, head with eyes. No face of anyone."""
    o = empty(loc, par, (0, 0, yaw))
    add('cone', top, (0, 0, 0.75 * s), radius1=0.42 * s, radius2=0.34 * s, depth=1.3 * s, vertices=8, parent=o)
    box(top, (0, 0, 1.38 * s), (0.86 * s, 0.4 * s, 0.14 * s), o)
    hd = empty((0, 0, 1.78 * s), o)
    add('ico_sphere', skin, (0, 0, 0), scale=(0.92 * s, s, 1.1 * s), radius=0.29, subdivisions=1, parent=hd)
    add('ico_sphere', hair, (0, 0.05 * s, 0.09 * s), scale=(0.95 * s, s, s), radius=0.3, subdivisions=1, parent=hd)
    for sx in (-1, 1):
        add('cube', '0E0D14', (sx * 0.1 * s, -0.27 * s, 0.03 * s), scale=(0.05 * s, 0.02, 0.05 * s), size=1, parent=hd)
    return hd


def seat(par, loc, col, yaw=0.0, back=2.0):
    o = empty(loc, par, (0, 0, yaw))
    box(col, (0, 0, 0.62), (1.05, 1.0, 0.24), o)
    box(col, (0, 0.5, 0.62 + back / 2), (1.05, 0.22, back), o)
    box('2A2E38', (0, 0, 0.25), (0.8, 0.8, 0.5), o)
    for sx in (-0.55, 0.55):
        box('3A3F4C', (sx, 0.05, 1.05), (0.1, 0.9, 0.08), o)
    return o


def plane_shape(par, loc, s=1.0, yaw=0.0, lights=True):
    """A plain white airliner, nose towards +x. No livery, no name, no number."""
    o = empty(loc, par, (0, 0, yaw))
    add('cylinder', 'E8ECF0', (0, 0, 3.2 * s), rot=(0, PI / 2, 0), radius=2.6 * s, depth=44 * s, vertices=14, parent=o, rough=0.4)
    add('ico_sphere', 'E8ECF0', (22 * s, 0, 3.0 * s), scale=(2.6, 1.0, 0.95), radius=2.6 * s, subdivisions=2, parent=o, rough=0.4)
    add('cone', 'E8ECF0', (-26 * s, 0, 3.8 * s), rot=(0, -PI / 2, 0), radius1=2.6 * s, radius2=0.6 * s, depth=8 * s, vertices=14, parent=o, rough=0.4)
    box('D8DCE2', (-28 * s, 0, 8.6 * s), (5.0 * s, 0.4 * s, 8.0 * s), o, rot=(0, -0.45, 0))
    for sy in (-1, 1):
        box('D8DCE2', (-1 * s, sy * 12 * s, 2.0 * s), (8 * s, 20 * s, 0.4 * s), o, rot=(0, 0, sy * -0.45))
        add('cylinder', 'B8BEC8', (2 * s, sy * 7.5 * s, 0.9 * s), rot=(0, PI / 2, 0), radius=1.2 * s, depth=5 * s, vertices=10, parent=o)
        box('D8DCE2', (-27 * s, sy * 4.5 * s, 4.2 * s), (3.5 * s, 7 * s, 0.3 * s), o, rot=(0, 0, sy * -0.35))
        for i in range(16):
            box('141C28', (14 * s - 2.0 * i * s, sy * 2.57 * s, 3.9 * s), (0.6 * s, 0.05, 0.75 * s), o, emit=1.2 if lights else 0.0)
    box('1C2430', (21.5 * s, 0, 4.1 * s), (2.0 * s, 4.4 * s, 0.9 * s), o, rot=(0, 0.35, 0))
    for (x, y) in ((17, 0), (0, 2), (0, -2)):
        add('cylinder', '2A2E38', (x * s, y * s, 0.6 * s), radius=0.18 * s, depth=1.4 * s, vertices=6, parent=o)
    return o


def make_flat(r):
    """A small Paris flat, evening: floor, two walls, a window over rooftops, a sofa, a bed with an open suitcase, a door."""
    box('6E5A48', (0, 0, -0.05), (16, 14, 0.1), r)
    box('D8CBB4', (0, 6.0, 2.6), (16, 0.15, 5.2), r)
    box('C8B89C', (-6.5, 0, 2.6), (0.15, 14, 5.2), r)
    box('8A6A4A', (0, 5.9, 0.25), (16, 0.08, 0.5), r)
    for (x, sx) in ((-4.3, 3.4), (4.6, 2.8)):                             # the wall around the window
        box('D8CBB4', (x, 5.95, 2.6), (sx, 0.16, 5.2), r)
    box('F2EEE4', (0.15, 5.9, 1.05), (5.6, 0.3, 0.12), r)
    out = add('cube', 'F0A070', (0.15, 6.6, 2.9), scale=(5.4, 0.05, 3.6), size=1, parent=r, emit=1.6)   # the evening sky behind the window
    for i in range(7):                                                    # rooftops and chimney pots against it
        x = -2.4 + 0.8 * i
        box('3A3448', (x, 6.4, 1.5 + 0.5 * rnd(i, 3)), (0.85, 0.1, 1.2 + rnd(i, 4)), r)
        box('5A4A50', (x + 0.2, 6.38, 2.4 + 0.6 * rnd(i, 5)), (0.16, 0.1, 0.5), r)
    for x in (-2.55, 2.85):
        box('F2EEE4', (x, 5.9, 2.9), (0.14, 0.2, 3.8), r)
    box('F2EEE4', (0.15, 5.9, 4.8), (5.6, 0.2, 0.14), r)
    box('C8504A', (-3.4, 5.75, 2.9), (0.9, 0.08, 3.9), r, rough=1.0)       # curtains
    box('C8504A', (3.7, 5.75, 2.9), (0.9, 0.08, 3.9), r, rough=1.0)
    # the sofa on the left, the bed on the right with the suitcase open on it
    box('4E6E8E', (-4.2, 1.2, 0.5), (3.6, 1.6, 1.0), r)
    box('4E6E8E', (-4.2, 1.95, 1.3), (3.6, 0.3, 1.4), r)
    for sx in (-1, 1):
        box('3E5A78', (-4.2 + sx * 1.8, 1.2, 1.1), (0.3, 1.6, 0.8), r)
    box('E8E0D0', (3.4, 2.4, 0.55), (3.4, 4.2, 0.5), r, rough=1.0)
    box('9A7A5A', (3.4, 2.4, 0.2), (3.5, 4.3, 0.3), r)
    box('9A7A5A', (3.4, 4.45, 1.2), (3.5, 0.15, 1.6), r)
    case = empty((3.0, 1.6, 0.8), r)
    box('2E5A8C', (0, 0, 0.18), (1.8, 1.2, 0.36), case)
    lid = empty((0, 0.6, 0.36), case, (-1.9, 0, 0))
    box('2E5A8C', (0, 0.6, 0.0), (1.8, 1.2, 0.12), lid)
    for i, col in enumerate(('E0705A', 'F0E8D0', '7A5AB0', '3E8E5A')):
        box(col, (-0.55 + 0.36 * i, -0.05, 0.38), (0.32, 0.9, 0.1 + 0.05 * (i % 2)), case, rough=1.0)
    box('E8D8A0', (3.2, 3.5, 0.85), (0.9, 0.6, 0.12), r, rough=1.0)       # folded clothes beside it
    # the front door on the left wall, with a lit landing beyond
    box('5A3E2A', (-6.45, -3.5, 2.0), (0.2, 2.2, 4.0), r)
    door = empty((-6.4, -4.6, 0.0), r, (0, 0, 0.0))
    box('8A5A3A', (0, 1.1, 2.0), (0.12, 2.2, 4.0), door)
    box('FFE0A0', (-6.9, -3.5, 2.0), (0.4, 2.0, 3.9), r, emit=1.2)
    box('B89070', (1.5, -2.5, 0.0), (4.0, 3.0, 0.02), r, rough=1.0)       # a rug
    lamp = light((0.5, 0.5, 4.8), 0, 'FFD8A8', 5.0, parent=r)
    win = light((0.15, 7.5, 2.9), 0, 'FFB070', 4.0, parent=r)
    win.rotation_euler = (-PI / 2, 0, 0)
    return dict(lamp=lamp, win=win, door=door, lid=lid, case=case, sky=out, lights=[lamp, win])


def make_lounge(r):
    """A departure lounge at night: a wall of glass with a plain airliner outside under floodlights, rows of seats, a board of amber rows with no words."""
    box('3A4250', (0, 0, -0.05), (30, 18, 0.1), r)
    box('2A3038', (0, 0, 6.5), (30, 18, 0.1), r)
    for i in range(9):                                                    # glass wall mullions at y = 6
        box('1A2028', (-14 + 3.5 * i, 6.0, 3.2), (0.2, 0.25, 6.6), r)
    box('1A2028', (0, 6.0, 0.25), (30, 0.3, 0.5), r)
    box('1A2028', (0, 6.0, 6.3), (30, 0.3, 0.4), r)
    box('5E6672', (-15, 0, 3.2), (0.2, 18, 6.6), r)
    box('5E6672', (15, 0, 3.2), (0.2, 18, 6.6), r)
    brd = empty((-9.0, -3.0, 3.4), r, (0, 0, 0.9))                         # the departures board: amber rows, no text
    box('101418', (0, 0, 0), (0.2, 4.2, 2.6), brd)
    rows = [box('FFB000', (-0.12, -1.2 + 0.0, 0.9 - 0.42 * j), (0.04, 1.6 + 0.6 * rnd(j, 2), 0.18), brd, emit=2.5) for j in range(5)]
    for row in range(3):
        for i in range(7):
            seat(r, (-6.0 + 1.25 * i, -1.0 - 2.6 * row, 0), '4A6A8A', PI)
    ap = add('plane', '20262E', (0, 30, -0.4), size=120, parent=r)          # the apron outside
    for j in range(5):
        box('E8D060', (-20 + 10 * j, 20, -0.35), (6, 0.25, 0.02), r, emit=0.8)
    pl = plane_shape(r, (4.0, 26.0, -0.4), 0.9, -0.12)
    for (x, y) in ((-16, 22), (22, 18)):
        add('cylinder', '3A3F4C', (x, y, 5), radius=0.2, depth=10.8, vertices=6, parent=r)
        box('FFF2D0', (x, y - 0.3, 10.2), (1.4, 0.3, 0.6), r, emit=8.0)
    flood = light((4, 16, 14), 0, 'FFE8C0', 14.0, parent=r, target=pl)
    lamp = light((0, -2, 6.3), 0, 'D8E4F0', 10.0, parent=r)
    return dict(lights=[flood, lamp], flood=flood, lamp=lamp, rows=rows, plane=pl)


def make_cabin(r):
    """The cabin of an airliner at night, seen down the aisle: rows of seats, small windows, closed bins, dim lights. Nose towards +y."""
    n = 16
    shell = []
    for i in range(n):                                                    # the curved shell as a closed ring of panels
        a = (i + 0.5) * 2 * PI / n
        shell.append(add('cube', 'D8D8D0', (5.4 * math.cos(a), 0, 3.0 + 4.6 * math.sin(a)), rot=(0, -a - PI / 2, 0),
                         scale=(2.3, 26, 0.12), size=1, parent=r, rough=0.6))
    box('3A4250', (0, 0, -0.05), (10.4, 26, 0.1), r)
    box('5E2E3A', (0, 0, 0.0), (1.4, 26, 0.02), r, rough=1.0)              # the aisle carpet
    box('E4E4DC', (0, 0, 6.6), (6.0, 26, 0.1), r)
    wins = []
    for sx in (-1, 1):
        box('C8C8C0', (sx * 3.9, 0, 5.6), (1.9, 26, 1.0), r, rot=(0, sx * 0.5, 0))          # the bins
        box('FFE8C0', (sx * 3.1, 0, 5.05), (0.25, 26, 0.06), r, emit=0.8)
        for j in range(8):
            y = -11 + 3.0 * j
            wins.append(box('060A12', (sx * 4.95, y, 3.1), (0.1, 0.62, 0.85), r, rot=(0, sx * -0.15, 0)))
            box('B8B8B0', (sx * 4.97, y, 3.1), (0.1, 0.8, 1.05), r, rot=(0, sx * -0.15, 0))
    rows = []
    for j in range(8):                                                    # seats in pairs either side of the aisle, backs towards -y
        y = -10 + 2.6 * j
        for x in (-3.6, -2.45, 2.45, 3.6):
            rows.append(seat(r, (x, y, 0), '2E4A6E', PI))
    sign = [box('FFC860', (sx * 1.6, -9.0 + 2.6 * j, 5.9), (0.5, 0.06, 0.25), r, emit=6.0) for sx in (-1, 1) for j in range(7)]
    port = empty((-4.7, -0.5, 3.1), r)                                     # the wall round one window, for the shot out of it
    for (y, z, sy, sz) in ((0.0, 2.6, 6, 4.0), (0.0, -2.6, 6, 4.0), (-1.9, 0.0, 2.6, 1.6), (1.9, 0.0, 2.6, 1.6)):
        box('D8D8D0', (0, y, z), (0.12, sy, sz), port)
    add('torus', 'B8B8B0', (0.05, 0, 0), rot=(0, PI / 2, 0), scale=(1.25, 0.95, 1), major_radius=0.6, minor_radius=0.1, major_segments=16,
        minor_segments=4, parent=port)
    pax = []
    cols = ('3A4E78', '8A3A4A', '2E5A4A', 'C8A23A', '5A4A7A', 'D8D0C0', '6E4630', 'A84A2A')
    skins = ('8A5A3C', '6E4630', 'C89A78', '5E3A28')
    for j in range(8):
        y = -10 + 2.6 * j
        for i, x in enumerate((-3.6, -2.45, 2.45, 3.6)):
            if (j == 4 and i < 3) or (j == 5 and i < 3) or rnd(j, i) < 0.25:                    # her row: her, her mother, and the seat across for Rook
                continue
            n_ = j * 4 + i
            pax.append((sitter(r, (x, y, 0.15), cols[n_ % 8], skins[n_ % 4], ('15121A', '2A2018')[n_ % 2], PI), n_))
    for sx in (-1, 1):                                                    # a wingtip with a light, out beyond the windows
        box('C8CCD4', (sx * 14.0, 2.0, 1.8), (16, 5.0, 0.25), r, rot=(0, sx * 0.08, 0))
    tip = [add('ico_sphere', 'FF3020', (sx * 21.5, 1.0, 2.4), radius=0.25, subdivisions=1, parent=r, emit=0.0) for sx in (-1, 1)]
    lamp = light((0, 0, 6.4), 0, 'FFE0B0', 8.0, parent=r)
    lamp.scale = (1.0, 8.0, 1.0)
    lamp2 = light((0, -6, 3.5), 0, 'C8D8F0', 3.0, parent=r)
    lamp2.rotation_euler = (-PI / 2, 0, 0)
    return dict(lights=[lamp, lamp2], lamp=lamp, lamp2=lamp2, sign=sign, tip=tip, wins=wins, shell=shell, port=port, pax=pax)


def make_court(r):
    """A courtroom: panelled walls, a raised bench at the back, a bar in the middle where a witness stands, rows of benches full of families."""
    box('6A4A32', (0, 0, -0.05), (26, 24, 0.1), r)
    box('C8B898', (0, 0, 9.5), (26, 24, 0.1), r)
    box('8A6A48', (0, 10.5, 4.75), (26, 0.2, 9.5), r)
    box('8A6A48', (0, -12.5, 4.75), (26, 0.2, 9.5), r)
    for j in range(2):
        box('5A3A26', (-4 + 8 * j, -12.35, 2.4), (2.4, 0.1, 4.6), r)               # doors at the back
    for sx in (-1, 1):
        box('9A7A58', (sx * 12.5, 0, 4.75), (0.2, 24, 9.5), r)
        for j in range(5):
            box('7A5A3E', (sx * 12.38, -9 + 4.5 * j, 3.0), (0.06, 2.6, 4.2), r)
            box('E8D8B0', (sx * 12.38, -9 + 4.5 * j, 7.6), (0.06, 2.2, 2.4), r, emit=0.6)       # tall windows of frosted glass
    for j in range(9):
        box('6A4A32', (-12 + 3 * j, 10.38, 2.6), (2.6, 0.06, 4.6), r)
    box('5A3A26', (0, 8.2, 0.9), (14, 2.6, 1.8), r)                        # the raised bench
    box('6E4A30', (0, 7.0, 2.1), (14.4, 0.3, 1.2), r)
    judges = [sitter(r, (x, 8.6, 1.6), '1A1A22', ('C89A78', '6E4630', 'E0B898')[i], ('4A4A4A', '15121A', '8A6A4A')[i], 0.0)
              for i, x in enumerate((-3.2, 0.0, 3.2))]
    for x in (-3.2, 0, 3.2):
        box('F0F0EC', (x, 8.4, 3.0), (0.6, 0.06, 0.6), r)                  # white bands on the robes
    for x in (-3.2, 0.0, 3.2):
        seat(r, (x, 9.1, 1.6), '7A2A2A', 0.0, 2.8)
    bar_ = empty((0, 3.0, 0), r)
    box('5A3A26', (0, 0, 1.0), (2.4, 0.5, 2.0), bar_)
    box('6E4A30', (0, 0, 2.05), (2.6, 0.7, 0.12), bar_)
    add('cylinder', '2A2E38', (0.7, 0.1, 2.5), rot=(0.5, 0, 0), radius=0.04, depth=0.8, vertices=5, parent=bar_)        # a microphone
    fam, heads = [], []
    cols = ('3A4E78', '8A3A4A', '2E5A4A', 'C8A23A', '5A4A7A', 'D8D0C0', '6E4630', '2A2E38', 'A84A2A', '4E6A8A')
    skins = ('8A5A3C', '6E4630', 'C89A78', '5E3A28', 'A0704E')
    for row in range(5):                                                   # benches, backs towards -y, families facing the bench
        y = -1.0 - 2.5 * row
        for sx in (-1, 1):
            box('7A5A3E', (sx * 5.5, y - 0.6, 1.1), (7.4, 0.2, 1.6), r)
            box('7A5A3E', (sx * 5.5, y, 0.6), (7.4, 1.0, 0.2), r)
            for i in range(5):
                if (row, sx, i) in ((0, -1, 4), (4, 1, 4)):                # two places left free: her father's and Rook's
                    continue
                j = row * 10 + (sx + 1) * 2 + i
                hd = sitter(r, (sx * (2.6 + 1.45 * i), y, 0.15), cols[j % 10], skins[j % 5], ('15121A', '2A2018', '4A3424')[j % 3], PI, 0.92 + 0.08 * rnd(j, 1))
                heads.append(hd)
    lamps = [light((x, 0, 9.3), 0, 'FFE8C8', 8.0, parent=r) for x in (-6, 6)]
    side = light((-11, 4, 7), 0, 'F0E8D8', 6.0, parent=r, target=bar_)
    return dict(lights=lamps + [side], lamps=lamps, side=side, judges=judges, heads=heads, bar=bar_)


def make_apron(r):
    """An airport apron on an overcast day: wet concrete, a hangar far off, a small white jet with its stairs down, an ambulance."""
    add('plane', '50555C', (0, 0, 0), size=400, parent=r, rough=0.5)
    for j in range(8):
        box('E8D060', (-40 + 12 * j, -6, 0.01), (7, 0.3, 0.02), r)
    hg = empty((0, 90, 0), r)
    box('9AA0A8', (0, 0, 9), (80, 30, 18), hg)
    box('6E747C', (0, -15.1, 7), (60, 0.2, 14), hg)
    for j in range(10):
        box('5E646C', (-27 + 6 * j, -15.2, 7), (0.3, 0.2, 14), hg)
    for x in (-120, -70, 70, 120):
        box('8A9098', (x, 110, 4), (30, 12, 8), r)
    jet = empty((0, 0, 0), r)                                              # a small business jet, nose towards -x, door on the -y side
    add('cylinder', 'F0F2F4', (0, 0, 3.0), rot=(0, PI / 2, 0), radius=1.5, depth=20, vertices=12, parent=jet, rough=0.35)
    add('ico_sphere', 'F0F2F4', (-10, 0, 2.9), scale=(2.2, 1.0, 0.9), radius=1.5, subdivisions=2, parent=jet, rough=0.35)
    add('cone', 'F0F2F4', (12, 0, 3.4), rot=(0, PI / 2, 0), radius1=1.5, radius2=0.4, depth=5, vertices=12, parent=jet, rough=0.35)
    box('E0E4E8', (13.5, 0, 6.0), (2.6, 0.3, 4.2), jet, rot=(0, 0.5, 0))
    box('E0E4E8', (15.2, 0, 8.0), (2.2, 6.0, 0.25), jet)
    for sy in (-1, 1):
        box('E0E4E8', (1.0, sy * 6.5, 2.0), (4.2, 11, 0.3), jet, rot=(0, 0, sy * -0.4))
        add('cylinder', 'D0D4D8', (10.5, sy * 2.2, 4.0), rot=(0, PI / 2, 0), radius=0.75, depth=3.6, vertices=10, parent=jet)
        for i in range(6):
            box('1A2634', (-6 + 2.2 * i, sy * 1.47, 3.4), (0.7, 0.05, 0.6), jet)
    box('1A2634', (-11.0, 0, 3.6), (1.6, 2.6, 0.6), jet, rot=(0, 0.45, 0))
    box('2A5E8E', (0, 0, 1.9), (20, 3.04, 0.25), jet)                     # a plain blue stripe, no name
    for (x, y) in ((-8, 0), (1, 1.3), (1, -1.3)):
        add('cylinder', '2A2E38', (x, y, 0.75), radius=0.12, depth=1.5, vertices=6, parent=jet)
        add('cylinder', '16181E', (x, y, 0.4), rot=(PI / 2, 0, 0), radius=0.4, depth=0.3, vertices=10, parent=jet)
    box('2A2E38', (-6.5, -1.52, 3.1), (1.1, 0.05, 2.2), jet)              # the open door
    stairs = empty((-6.5, -1.6, 2.0), jet)
    for j in range(7):
        box('E8ECF0', (0, -0.42 * j, -0.29 * j), (1.0, 0.42, 0.12), stairs)
    for sx in (-0.55, 0.55):
        bar(stairs, 'C8CCD4', (sx, 0, 1.0), (sx, -2.9, -1.0), 0.06)
    amb = empty((-22, -15, 0), r, (0, 0, 0.2))                            # a white ambulance with an orange band; no lettering
    box('F0F0EC', (0, 0, 1.6), (5.5, 2.4, 2.4), amb)
    box('F0F0EC', (3.2, 0, 1.2), (1.6, 2.3, 1.6), amb)
    box('FF7A1A', (0, 0, 1.4), (5.6, 2.45, 0.3), amb)
    box('1A2634', (3.5, 0, 1.75), (1.0, 2.35, 0.5), amb)
    blue = [box('3A7AFF', (1.0 + 1.2 * sx, 0, 2.9), (0.4, 0.4, 0.2), amb, emit=0.0) for sx in (-1, 1)]
    for (x, y) in ((-1.8, 1.2), (-1.8, -1.2), (2.8, 1.2), (2.8, -1.2)):
        add('cylinder', '16181E', (x, y, 0.45), rot=(PI / 2, 0, 0), radius=0.45, depth=0.3, vertices=10, parent=amb)
    sun = light((0, 0, 60), 0, 'E8ECF0', 120.0, parent=r)
    return dict(lights=[sun], sun=sun, jet=jet, stairs=stairs, amb=amb, blue=blue)


def make_isle(S):
    """The island at night, seen from its own shore: a dark volcano, a few lights along the coast, palms bent by the wind."""
    r = keep(empty(ISLE))
    add('cone', '0E1A16', (0, 160, -10), radius1=220, radius2=18, depth=150, vertices=16, parent=r, rough=1.0)
    add('cone', '12201A', (-120, 90, -6), radius1=90, radius2=10, depth=60, vertices=12, parent=r, rough=1.0)
    for j in range(16):                                                   # black rocks along the shore, near the camera
        add('ico_sphere', ('1A1C20', '24262C', '16181C')[j % 3], (-14 + 2.0 * j + rnd(j, 1), -2.0 + 2.2 * rnd(j, 2), -0.3), scale=(1.4, 1.1, 0.8),
            radius=0.9 + 0.7 * rnd(j, 3), subdivisions=1, parent=r, rough=0.9)
    add('cube', '1A1C20', (0, 30, 0.6), scale=(80, 60, 1.2), size=1, parent=r)
    palms = []
    for j, (x, y) in enumerate(((-7.5, 3.0), (6.5, 4.0), (-12, 8), (11, 10))):
        p = empty((x, y, 0), r)
        trunk = empty((0, 0, 0), p)
        for k in range(6):
            add('cylinder', '3A2E24', (0.12 * k * k * 0.1, 0, 0.75 + 1.5 * k), radius=0.22 - 0.02 * k, depth=1.6, vertices=6, parent=trunk)
        crown = empty((0.4, 0, 9.2), trunk)
        for i in range(7):
            add('cone', '1E3A2A', (0, 0, 0), rot=(1.25, 0, i * 2 * PI / 7), radius1=0.5, radius2=0.0, depth=4.2, vertices=3, parent=crown, scale=(1, 0.3, 1))
        palms.append((trunk, crown, j))
    lights_ = []
    for j in range(22):                                                   # village lights scattered along the coast and up the slope
        a = -1.1 + 2.2 * rnd(j, 7)
        d = 40 + 140 * rnd(j, 8)
        lights_.append(add('ico_sphere', 'FFD080', (d * math.sin(a) * 1.6, 20 + d * math.cos(a) * 0.6, 1.5 + 12 * rnd(j, 9) * (d / 180)),
                           radius=0.35 + 0.3 * rnd(j, 10), subdivisions=1, parent=r, emit=12.0))
    S.update(isle=r, palms=palms)


_build0, _reset0 = build, reset


def build():
    S = _build0()
    S['sets'] = {}
    for name, fn in (('flat', make_flat), ('lounge', make_lounge), ('cabin', make_cabin), ('court', make_court), ('apron', make_apron)):
        root = keep(empty(SETPOS[name]))
        d = fn(root)
        d.update(root=root, all=kids(root))
        S['sets'][name] = d
    make_isle(S)
    S['isleall'] = kids(S['isle'])
    S['mom'] = K.Rig(MOMC, bun_head(SKIN, HAIR, 'D88A3A'))
    S['mom'].sc = 0.98
    S['dad'] = K.Rig(DADC, K.human_head('6E4630', '15121A'))
    S['dad'].sc = 1.02
    S['kids'] = []
    for top, pants, sc in KIDS:
        k_ = K.Rig(dict(top=top, pants=pants, hand=SKIN, boot='1E2028', fore=SKIN), K.human_head(SKIN, HAIR))
        k_.sc = sc
        S['kids'].append(k_)
    S['bahia'] = K.Rig(ADULTC, bun_head(SKIN, HAIR))
    S['bahia'].sc = 0.95
    new = [S['mom'], S['dad'], S['bahia']] + S['kids']
    S['humans'] += new
    S['cast'] += new
    S['sling'] = keep(add('cube', 'F0F0EC', FAR, scale=(0.5, 0.35, 0.9), size=1, rough=1.0))
    S['report'] = keep(add('cube', 'F4EEDC', FAR, scale=(0.6, 0.8, 0.06), size=1))
    reset(S)
    return S


def reset(S):
    _reset0(S)
    if 'sets' not in S:
        return
    for d in S['sets'].values():
        vis(d['all'], False)
        for l in d['lights']:
            l.data.energy = 0
    vis(S['isleall'], False)
    S['hat_off'] = 0.0


def inside(S, name, mode='night', fill=1.0):
    """Show one of the long-form sets (and only it): no sea, no sun; its own lights on."""
    sky(S, mode)
    S['sea'].hide_render = True
    S['sun'].data.energy = 0
    d = S['sets'][name]
    vis(d['all'], True)
    S['fillk'] = fill
    return d


def SP(name, x, y, z):
    o = SETPOS[name]
    return (o[0] + x, o[1] + y, o[2] + z)


def put(S, rig, name, x, y, z, yaw):
    rig.root.parent = S['sets'][name]['root']
    rig.place((x, y, z), yaw)
    return rig


def seat_z(rig, top=0.74):
    return top - 0.55 * rig.sc


# ---------------------------------------------------------------- the family, Paris, the night before
def flat_pack(S, k, t, lt):
    """The flat in the evening: Bahia lays a folded top in the open suitcase on the bed; her mother kneels beside her, smoothing it flat.
    Her brothers and sister watch from the sofa. Rook leans in the window bay with his arms folded."""
    d = inside(S, 'flat', 'dusk')
    d['lamp'].data.energy, d['win'].data.energy = 520, 900
    g = put(S, S['girl'], 'flat', 2.3, 0.7, 0.0, PI * 0.85)
    lay = sm(lt / 1.2)
    g.apply(P('stand', aR=(lerp(0.9, 0.5, lay), 0.0, lerp(1.0, 0.3, lay)), aL=(lerp(0.8, 0.45, lay), 0.0, lerp(1.1, 0.3, lay)), lean=0.25 * lay + 0.15,
              head=(0.35, 0.2)))
    g.face, g.jawv = 'warm', 0.2 * abs(math.sin(lt * 5))
    m = put(S, S['mom'], 'flat', 3.9, 0.55, 0.0, PI * 1.15)
    m.apply(P('stand', aL=(0.7, 0.1, 0.6), aR=(0.75, 0.05, 0.4 + 0.2 * math.sin(lt * 3)), lean=0.45, head=(0.3, -0.25)))
    m.face, m.jawv = 'warm', 0.3 * abs(math.sin(lt * 4.4))
    for i, (x, kd) in enumerate(zip((-5.2, -4.2, -3.2), S['kids'])):
        put(S, kd, 'flat', x, 1.1, seat_z(kd, 1.0), PI)
        kd.apply(P('sit', head=(0.05, -0.5 + 0.15 * math.sin(lt * 1.3 + i))))
        kd.face = 'calm'
    rk = put(S, S['rook'], 'flat', 0.6, 5.0, 0.0, facing((0.6, 5.0), (2.6, 0.6)))
    rk.apply(P('cross', head=(0.15, 0.0)))
    S['rface'] = 'soft'
    shoot(S, SP('flat', lerp(1.2, 0.6, k), lerp(-4.6, -4.0, k), lerp(3.0, 2.8, k)), SP('flat', 0.4, 1.6, 1.4), 26, fill=0.9, fcol='FFE0C0')


def doorway(S, k, t, lt):
    """At the open front door: Bahia and her mother go out with the suitcase; her father, with the three younger ones, waves them off.
    Rook holds the door, hat brim tipped to them."""
    d = inside(S, 'flat', 'dusk')
    d['lamp'].data.energy, d['win'].data.energy = 520, 700
    d['door'].rotation_euler = (0, 0, -1.4)
    go = sm(lt / 3.6)
    m = put(S, S['mom'], 'flat', lerp(-4.6, -6.0, go), -3.6, 0.0, PI / 2 - 0.4)
    m.apply(blend(K.walk(t, 1.2), P('stand', aR=(-0.2, 0.3, 0.2), head=(0.0, 0.5)), 0.4))
    m.face, m.jawv = 'warm', 0.25 * abs(math.sin(lt * 4))
    g = put(S, S['girl'], 'flat', lerp(-3.4, -5.0, go), -2.7, 0.0, PI / 2 - 0.6 + 0.8 * sm((lt - 1.4) / 0.4))
    g.apply(blend(K.walk(t + 0.3, 1.3), P('stand', aL=(1.6 + 0.3 * math.sin(lt * 9), 0.3, 0.3), head=(-0.1, 0.6)), sm((lt - 1.3) / 0.4)))
    g.face = 'warm'
    dd = put(S, S['dad'], 'flat', -1.2, -1.2, 0.0, facing((-1.2, -1.2), (-5.0, -3.2)))
    dd.apply(P('stand', aR=(2.5, 0.4, 0.4 + 0.4 * math.sin(lt * 7)), head=(0.0, 0.0)))
    dd.face, dd.jawv = 'warm', 0.3 * abs(math.sin(lt * 3))
    for i, (x, y, kd) in enumerate(zip((-2.2, -0.4, 0.4), (-0.4, -0.2, -1.6), S['kids'])):
        put(S, kd, 'flat', x, y, 0.0, facing((x, y), (-5.0, -3.2)))
        kd.apply(P('stand', aR=(2.3 + 0.2 * i, 0.3, 0.4 + 0.5 * math.sin(lt * 8 + i)), head=(-0.1, 0.0)))
        kd.face = 'warm'
    rk = put(S, S['rook'], 'flat', -5.9, -5.6, 0.0, facing((-5.9, -5.6), (-1.0, -1.2)))
    rk.apply(P('stand', aL=(0.9, 0.6, 0.4), head=(0.2, 0.2)))
    S['rface'] = 'soft'
    S['hat_tip'] = 0.4
    shoot(S, SP('flat', lerp(1.6, 1.1, k), lerp(-6.2, -5.8, k), lerp(2.7, 2.6, k)), SP('flat', -3.4, -2.6, 1.5), 28, fill=0.9, fcol='FFE0C0')


# ---------------------------------------------------------------- the journey
def lounge(S, k, t, lt):
    """Night, the departure lounge: Bahia and her mother stand at the glass, looking out at a plain white airliner under the floodlights.
    Rook sits behind them on a row of seats, turning a boarding card over in his wing."""
    d = inside(S, 'lounge', 'night')
    d['flood'].data.energy, d['lamp'].data.energy = 9000, 700
    for j, rw in enumerate(d['rows']):
        rw.hide_render = math.sin(t * 3 + j * 1.7) > 0.85
    m = put(S, S['mom'], 'lounge', 0.4, 4.6, 0.0, PI)
    m.apply(P('stand', aR=(0.4, 0.6, 0.5), head=(-0.05, 0.25 + 0.1 * math.sin(lt * 0.8))))
    m.face = 'calm'
    g = put(S, S['girl'], 'lounge', 1.5, 4.7, 0.0, PI)
    g.apply(P('stand', aL=(1.3, 0.2, 1.0), aR=(1.2, 0.1, 0.9), head=(-0.15, -0.2 + 0.4 * sm(lt / 2.0))))
    g.face = 'wide'
    rk = put(S, S['rook'], 'lounge', -3.2, 3.1, 0.0, facing((-1.6, 3.4), (-5.0, -1.0)) + 0.5)
    rk.apply(P('think', head=(0.1, -0.5 + 0.3 * math.sin(lt * 0.9))))
    S['rface'] = 'calm'
    shoot(S, SP('lounge', lerp(-5.6, -4.8, k), lerp(-1.4, -0.8, k), lerp(3.0, 2.9, k)), SP('lounge', 0.2, 5.2, 2.2), 26, fill=0.9, fcol='D8E4F0')


def cabin_seats(S, k, t, lt):
    """In the cabin, at night: Bahia in the window seat, her mother beside her with an arm round her. Across the aisle Rook sits upright,
    reading the safety card. Other passengers' heads above the seat backs; a few reading lights."""
    d = inside(S, 'cabin', 'night')
    d['lamp'].data.energy, d['lamp2'].data.energy = 260, 120
    _passengers(S, t)
    g = put(S, S['girl'], 'cabin', -3.6, 0.4, seat_z(S['girl'], 0.74), PI)
    g.apply(P('sit', head=(0.05, 0.4 + 0.2 * math.sin(lt * 0.9))))
    g.face = 'calm'
    m = put(S, S['mom'], 'cabin', -2.45, 0.4, seat_z(S['mom'], 0.74), PI)
    m.apply(P('sit', aR=(0.6, -0.9, 0.6), head=(0.15, 0.35)))
    m.face = 'warm'
    rk = put(S, S['rook'], 'cabin', 2.45, 0.4, seat_z(S['rook'], 0.74), PI)
    rk.apply(P('sit', aL=(1.0, -0.1, 1.9, 0.6), aR=(1.0, -0.1, 1.9, 0.6), head=(0.45, 0.0)))
    S['report'].parent = rk.hands[1]
    S['report'].location, S['report'].rotation_euler, S['report'].scale = (0.2, -0.3, -0.6), (1.2, 0, 0.3), (0.55, 0.7, 0.04)
    S['rface'] = 'calm'
    shoot(S, SP('cabin', lerp(0.4, 0.0, k), lerp(4.6, 4.2, k), lerp(4.6, 4.4, k)), SP('cabin', -0.6, 0.4, 1.4), 22, fill=1.0, fcol='FFE0B0')
    S['report'].hide_render = False


def _passengers(S, t):
    d = S['sets']['cabin']
    vis(kids(d['port']), False)
    vis(d['sign'], False)
    for hd, n in d['pax']:
        hd.rotation_euler = (0.1 * math.sin(t * 0.7 + n), 0, 0.2 * math.sin(t * 0.4 + n * 1.3))


def window_dark(S, k, t, lt):
    """Out of the window: black. The wing, a red light blinking at its tip, and far below a handful of lights on a coast."""
    d = inside(S, 'cabin', 'night')
    d['lamp'].data.energy = 60
    vis(d['shell'][6:10] + d['wins'][:8] + d['sign'], False)
    S['bg'].inputs[1].default_value = 0.35
    on = (t * 1.1) % 1 < 0.25
    for tp in d['tip']:
        tp.hide_render = not on
    S['isle'].location = SP('cabin', -90, 120, -60)
    vis(S['isleall'], True)
    for tr, cr, j in S['palms']:
        tr.hide_render = True
    shoot(S, SP('cabin', lerp(-3.3, -3.6, k), -0.5, 3.4), SP('cabin', -20.0, -1.6, 1.0), 30, roll=0.1 + 0.03 * math.sin(lt * 1.6), fill=0.4)


def island_night(S, k, t, lt):
    """The island at night, from its shore: the black cone of a volcano, a scatter of lights, the palms thrashing in the wind.
    Rook on a rock at the water's edge holds his hat on with one wing, coat flapping."""
    sea(S, 'night', t, 0.9)
    vis(S['isleall'], True)
    for tr, cr, j in S['palms']:
        g_ = 0.5 + 0.5 * math.sin(t * 3.1 + j)
        tr.rotation_euler = (0, -0.12 - 0.08 * g_, 0)
        cr.rotation_euler = (0.15 * math.sin(t * 7 + j), -0.4 - 0.25 * g_, 0.1 * math.sin(t * 5 + j))
    rk = S['rook']
    rk.root.parent = S['isle']
    rk.place((1.5, -1.6, 0.4), facing((1.5, -1.6), (-8, -14)))
    rk.apply(P('hat', aL=(0.6, 0.5 + 0.2 * math.sin(t * 9), 0.4), lean=0.15, head=(0.1, 0.4)))
    S['rface'] = 'low'
    o = ISLE
    shoot(S, (o[0] + lerp(5.0, 6.0, k), o[1] - lerp(7.0, 7.8, k), 1.9), (o[0] - 1.5, o[1] + 6.0, 3.4), 24, roll=0.04 * math.sin(lt * 1.3), fill=2.4, fcol=NIGHTC)


def cabin_shake(S, k, t, lt):
    """Down the aisle: the whole cabin jolts and shudders, the bins rattle, the seat-belt signs are lit. The heads above the seats barely move."""
    d = inside(S, 'cabin', 'night')
    d['lamp'].data.energy, d['lamp2'].data.energy = 220, 100
    _passengers(S, t)
    vis(d['sign'], True)
    jolt = 0.04 * math.sin(t * 23) + 0.03 * math.sin(t * 37 + 1) + (0.08 if (lt % 0.9) < 0.1 else 0.0)
    d['root'].rotation_euler = (jolt * 0.6, jolt, 0)
    g = put(S, S['girl'], 'cabin', -3.6, 0.4, seat_z(S['girl'], 0.74), PI)
    g.apply(P('sit', head=(-0.05, 0.8 * math.sin(lt * 1.5))))
    g.face = 'wide'
    m = put(S, S['mom'], 'cabin', -2.45, 0.4, seat_z(S['mom'], 0.74), PI)
    m.apply(P('sit', head=(0.1, 0.1)))
    m.face = 'calm'
    shoot(S, SP('cabin', lerp(0.5, 0.2, k), lerp(14.0, 13.0, k), lerp(4.4, 4.2, k)), SP('cabin', 0.0, -4.0, 1.8), 22, roll=jolt * 2, fill=1.0, fcol='FFE0B0')


def bahia_look(S, k, t, lt):
    """Close in her seat: she grips the armrest and looks round at the faces near her; her mother's face is calm. Across the aisle Rook's grip
    tightens on his own armrest and his eyes go to the window."""
    d = inside(S, 'cabin', 'night')
    d['lamp'].data.energy, d['lamp2'].data.energy = 220, 100
    _passengers(S, t)
    jolt = 0.03 * math.sin(t * 23) + 0.02 * math.sin(t * 31 + 1)
    d['root'].rotation_euler = (jolt * 0.5, jolt, 0)
    g = put(S, S['girl'], 'cabin', -3.6, 0.4, seat_z(S['girl'], 0.74), PI)
    g.apply(P('sit', aR=(0.6, 0.5, 0.9), head=(-0.05, lerp(0.7, -0.6, sm(lt / 1.6)))))
    g.face = 'wide' if lt < 1.8 else 'calm'
    m = put(S, S['mom'], 'cabin', -2.45, 0.4, seat_z(S['mom'], 0.74), PI)
    m.apply(P('sit', head=(0.1, 0.25)))
    m.face = 'calm'
    shoot(S, SP('cabin', lerp(-2.5, -2.7, k), lerp(2.5, 2.3, k), 2.5), SP('cabin', -3.4, 0.4, 1.6), 32, roll=jolt * 1.5, fill=1.2, fcol='FFE0B0')


# ---------------------------------------------------------------- home
def jet_arrive(S, k, t, lt):
    """Overcast morning on an apron: a small white jet rolls in and stops; an ambulance waits with its blue lights turning."""
    d = inside(S, 'apron', 'grey', 1.0)
    S['sun'].data.energy = 2.6
    roll_ = sm(k * 1.3)
    d['jet'].location = (lerp(-26, 0, roll_), 0, 0)
    for i, b in enumerate(d['blue']):
        b.hide_render = ((t * 2.2 + 0.5 * i) % 1) > 0.5
    d['stairs'].hide_render = True
    for o in kids(d['stairs'])[1:]:
        o.hide_render = True
    shoot(S, SP('apron', lerp(-22, -18, k), lerp(-34, -30, k), lerp(4.0, 3.6, k)), SP('apron', lerp(-12, -2, k), 0.0, 3.0), 26, fill=0.6, fcol='E8ECF0')


def stairs(S, k, t, lt):
    """The jet's door: a medic helps Bahia down the steps, her arm in a sling. Rook stands back by the wing, watching her down."""
    d = inside(S, 'apron', 'grey', 1.0)
    S['sun'].data.energy = 2.6
    for i, b in enumerate(d['blue']):
        b.hide_render = ((t * 2.2 + 0.5 * i) % 1) > 0.5
    down = sm(lt / 2.4)
    j = down * 6.0
    g = S['girl']
    g.root.parent = d['stairs']
    g.place((0.0, -0.42 * j + 0.1, -0.29 * j + 0.06), 0.0)
    g.apply(blend(K.walk(t, 0.9), P('stand', head=(0.2, 0.0)), 0.5))
    g.face = 'tired'
    S['sling'].parent = g.body
    S['sling'].location, S['sling'].rotation_euler, S['sling'].scale = (-0.32, -0.3, 0.78), (0.0, 0.0, 0.2), (0.38, 0.3, 0.6)
    w = S['woman']
    w.root.parent = d['stairs']
    jj = max(0.0, j - 1.2)
    w.place((0.35, -0.42 * jj + 0.5, -0.29 * jj + 0.06), 0.0)
    w.apply(P('stand', aR=(0.8, -0.6, 0.6), head=(0.35, 0.0)))
    w.face = 'calm'
    rk = put(S, S['rook'], 'apron', -9.4, -6.2, 0.0, facing((-9.4, -6.2), (-6.5, -3.0)))
    rk.apply(P('stand', head=(-0.1, 0.0)))
    S['rface'] = 'soft'
    shoot(S, SP('apron', lerp(-11.5, -11.0, k), lerp(-11.0, -10.4, k), lerp(2.0, 1.8, k)), SP('apron', -6.8, -3.6, lerp(2.9, 2.1, k)), 34, fill=0.9, fcol='E8ECF0')


def father_hug(S, k, t, lt):
    """At the foot of the steps her father kneels and holds her, carefully, one arm round her shoulders, away from the sling."""
    d = inside(S, 'apron', 'grey', 1.0)
    S['sun'].data.energy = 2.6
    for i, b in enumerate(d['blue']):
        b.hide_render = ((t * 2.2 + 0.5 * i) % 1) > 0.5
    g = put(S, S['girl'], 'apron', -6.5, -5.6, 0.0, 0.1)
    g.apply(P('stand', aR=(0.7, 0.3, 0.9), head=(lerp(-0.1, 0.25, sm(lt / 1.5)), 0.0)))
    g.face = 'shut' if lt > 1.2 else 'tired'
    S['sling'].parent = g.body
    S['sling'].location, S['sling'].rotation_euler, S['sling'].scale = (-0.32, -0.3, 0.78), (0.0, 0.0, 0.2), (0.38, 0.3, 0.6)
    dd = put(S, S['dad'], 'apron', -6.4, -6.5, 0.0, PI)
    hold = sm(lt / 1.0)
    dd.apply(P('stand', lL=(0.2, 1.5), lR=(1.3, 1.45), lift=-0.7, lean=0.2, aR=(lerp(0.3, 1.25, hold), lerp(0.2, -0.45, hold), 0.9), aL=(0.4, 0.3, 0.6),
               head=(0.15, 0.2)))
    dd.face = 'shut' if lt > 0.8 else 'sad'
    shoot(S, SP('apron', lerp(-9.6, -9.2, k), lerp(-3.2, -3.5, k), lerp(2.2, 2.1, k)), SP('apron', -6.45, -6.2, 1.5), 36, fill=1.0, fcol='E8ECF0')


# ---------------------------------------------------------------- the trial, Paris, 2022
def court(S, t):
    d = inside(S, 'court', 'grey', 0.8)
    for l in d['lamps']:
        l.data.energy = 900
    d['side'].data.energy = 1400
    for j, hd in enumerate(d['heads']):
        hd.rotation_euler = (0.08 * math.sin(t * 0.5 + j), 0, 0.12 * math.sin(t * 0.3 + 1.7 * j))
    return d


def _witness(S, lt, speak=True):
    b = put(S, S['bahia'], 'court', 0.0, 2.4, 0.0, PI)
    b.apply(P('stand', aL=(0.55, 0.1, 0.9), aR=(0.55 + 0.15 * math.sin(lt * 1.7), 0.1, 0.9), head=(0.0 + 0.05 * math.sin(lt * 1.2), 0.05 * math.sin(lt * 0.8))))
    b.face, b.jawv = ('sad', 0.2 + 0.25 * abs(math.sin(lt * 6.3))) if speak else ('sad', 0.0)
    return b


def court_wide(S, k, t, lt):
    """The courtroom from the back: benches full, the bench at the far end, a young woman standing alone at the bar. Rook in the last row."""
    court(S, t)
    _witness(S, lt)
    dd = put(S, S['dad'], 'court', -2.6 - 1.45 * 4, -1.0, seat_z(S['dad'], 0.7), PI)
    dd.apply(P('sit', head=(0.0, 0.0)))
    rk = put(S, S['rook'], 'court', 2.6 + 1.45 * 4, -11.0, seat_z(S['rook'], 0.7), PI)
    rk.apply(P('sit', head=(0.1, -0.2)))
    S['rface'] = 'calm'
    shoot(S, SP('court', lerp(5.4, 4.2, k), lerp(-10.8, -10.3, k), lerp(6.2, 5.9, k)), SP('court', 0.0, 3.0, 2.2), 22, fill=0.8, fcol='FFE8C8')


def testify(S, k, t, lt):
    """From the side of the bar: Bahia, twenty-five, both hands on the rail, speaks towards the bench. Her voice is steady, then her head goes down."""
    court(S, t)
    b = _witness(S, lt)
    hand = sm((lt - 0.6) / 0.6) * (1 - sm((lt - 1.9) / 0.4))
    b.apply(P('stand', aL=(0.55, 0.1, 0.9), aR=(lerp(0.55, 1.0, hand), lerp(0.1, -0.5, hand), lerp(0.9, 2.0, hand)), head=(0.05 * math.sin(lt * 1.2), 0.3 * math.sin(lt * 0.9))))
    if lt > 2.0:
        b.apply(P('stand', aL=(0.55, 0.1, 0.9), aR=(0.55, 0.1, 0.9), head=(lerp(0.0, 0.35, sm((lt - 2.0) / 0.6)), 0.0)))
        b.face = 'shut'
    shoot(S, SP('court', lerp(-3.6, -3.2, k), lerp(0.2, 0.5, k), lerp(2.9, 2.8, k)), SP('court', 0.0, 2.6, 2.3), 40, fill=1.0, fcol='FFE8C8')


def families(S, k, t, lt):
    """Along a bench: the families listen. Heads turn to each other, a hand goes to a shoulder. In the front row, her father."""
    court(S, t)
    _witness(S, lt)
    dd = put(S, S['dad'], 'court', -2.6 - 1.45 * 4, -1.0, seat_z(S['dad'], 0.7), PI)
    dd.apply(P('sit', aL=(0.7, -0.1, 1.5, 1.0), head=(0.25 + 0.1 * math.sin(lt), 0.15)))
    dd.face = 'sad'
    shoot(S, SP('court', lerp(-11.2, -10.6, k), lerp(3.6, 3.2, k), lerp(3.6, 3.4, k)), SP('court', -6.5, -3.5, 1.8), 30, fill=0.9, fcol='FFE8C8')


def verdict(S, k, t, lt):
    """The bench: the presiding judge rises with a sheet of paper and reads; the two either side look down at the room."""
    d = court(S, t)
    up = sm(lt / 1.0)
    jd = d['judges'][1].parent
    jd.location = (0.0, 8.6, 1.6 + 0.9 * up)
    for j, hd in enumerate(d['judges']):
        hd.rotation_euler = (0.25 if j == 1 else 0.15, 0, 0.1 * math.sin(t * 0.6 + j))
    S['report'].parent = d['root']
    S['report'].location, S['report'].rotation_euler, S['report'].scale = (0.0, 7.95, 2.6 + 0.9 * up), (-0.3, 0, 0), (0.7, 0.05, 0.9)
    shoot(S, SP('court', lerp(-1.6, -0.8, k), lerp(-1.5, -0.6, k), lerp(2.6, 2.8, k)), SP('court', 0.0, 8.6, 3.6), 30, fill=0.9, fcol='FFE8C8')


def court_rook(S, k, t, lt):
    """The back row: Rook sits with his hat in his lap; at the words, he puts it back on and looks down the room to the woman at the bar."""
    court(S, t)
    _witness(S, lt, False)
    rk = put(S, S['rook'], 'court', 2.6 + 1.45 * 4, -11.0, seat_z(S['rook'], 0.7), PI)
    on_ = sm((lt - 0.6) / 0.8)
    rk.apply(blend(P('sit', head=(0.35, 0.0)), P('sit', aR=(0.2, 1.9, 1.6, -1.5), head=(0.1, 0.25)), on_))
    S['hat_off'] = 1 - on_
    S['rface'] = 'sad'
    shoot(S, SP('court', lerp(10.6, 10.2, k), lerp(-7.6, -7.9, k), lerp(3.0, 2.9, k)), SP('court', 8.2, -10.9, 2.2), 34, fill=1.0, fcol='FFE8C8')


def photo_thumb(S, k, t, lt):
    """The thumbnail picture: the girl at the wreckage edge at night, close and to the right of frame, black sea to the left for the words."""
    sea(S, 'night', 3.0)
    g = hang(S, HOLD(nod=-0.25, turn=0.35))
    g.face = 'wide'
    hd = ghead(S)
    shoot(S, (hd[0] + 1.9, hd[1] + 2.1, hd[2] + 0.35), (hd[0] + 0.75, hd[1] - 0.55, hd[2] - 0.2), 36, fill=3.2, fcol=NIGHTC)


def photo_court(S, k, t, lt):
    court(S, 2.0)
    _witness(S, 0.5, False)
    shoot(S, SP('court', -2.4, -0.4, 3.6), SP('court', 0.0, 2.6, 3.4), 40, fill=1.0, fcol='FFE8C8')


NEW = (flat_pack, doorway, lounge, cabin_seats, window_dark, island_night, cabin_shake, bahia_look, jet_arrive, stairs, father_hug,
       court_wide, testify, families, verdict, court_rook)
SHOTS3D.update({f.__name__: f for f in NEW})
STILLS.update(thumb=photo_thumb, court=photo_court)

# The Short's shots were timed for about a second each; here they run two to three times as long. Their acting is spread over
# the first 1.4 s of a shot (lt is slowed, never sped up) and every shot also swings a little round its own subject, so a held
# frame keeps moving. prm "orb": [degrees, dolly, rise] sets the swing for one shot.
SHORT_KINDS = set(SHOTS3D) - {f.__name__ for f in NEW}
SWING = dict(window_dark=2.0, cabin_shake=3.0, jet_arrive=4.0, island_night=5.0, verdict=6.0, court_rook=5.0, court_wide=3.0, families=3.0)


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
        m = 1 - dolly * (k - 0.5)
        dx, dy = c[0] - tg[0], c[1] - tg[1]
        S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m, c[2] + rise * (k - 0.5))
    g.__name__ = f.__name__
    return g


for _n in SHORT_KINDS:
    SHOTS3D[_n] = _slowed(SHOTS3D[_n])
SHOTS3D = {name: _swung(f, name) for name, f in SHOTS3D.items()}
