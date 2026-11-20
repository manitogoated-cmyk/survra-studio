"""Case 043 in 3D - the Captain of Koepenick, October 1906. Wilhelm Voigt, an out-of-work shoemaker with a prison
record, put on a second-hand captain's uniform, ordered ten passing soldiers to follow him, led them to the town hall
of Koepenick near Berlin, had the mayor and the treasurer arrested, took over 4,000 marks from the town treasury and
vanished. He was caught ten days later and sentenced to four years; the Kaiser, reportedly amused, pardoned him after
less than two, and Voigt went on tour playing the captain on stage.

Built for this story only: the mayor's office, the treasury with its safe, the brick town hall and its square, a
Berlin street, a back alley, a cobbler's room, a second-hand shop with the uniform on a tailor's dummy, a prison cell,
a palace study and a variety theatre.

Everything is a generic low-poly reconstruction. Nobody's likeness is attempted; uniforms are simplified and carry no
real insignia; no words, crests or flags appear in the 3D world."""
import math

import bpy
from mathutils import Matrix, Vector

from engine4 import kit3d as K
from engine4.kit3d import P, blend, lerp, light

PI = math.pi
FAR = (0, 0, -40000)
OFF = (0.0, 0.0, 0.0)               # the mayor's office
TRE = (1000.0, 0.0, 0.0)            # the treasury
SHP = (2000.0, 0.0, 0.0)            # the second-hand shop
COB = (3000.0, 0.0, 0.0)            # the cobbler's room
CEL = (4000.0, 0.0, 0.0)            # the prison cell
PAL = (5000.0, 0.0, 0.0)            # the palace study
THE = (6000.0, 0.0, 0.0)            # the variety theatre
EXT = (0.0, 3000.0, 0.0)            # the town hall and its square
STR = (1500.0, 3000.0, 0.0)         # a Berlin street
ALY = (3000.0, 3000.0, 0.0)         # a back alley
HOST = {'rook_desk', 'rook_coins', 'rook_peer', 'rook_gone', 'rook_shoe', 'rook_mag', 'rook_follow', 'rook_cell',
        'rook_free', 'rook_seat', 'rook_wings', 'signoff'}
CAMFILL = {'*': 160, 'rook_gone': 420, 'caught': 340, 'rook_free': 340, 'rook_seat': 300, 'rook_wings': 260, 'rook_cell': 220, 'rook_shoe': 220,
           'cap_off': 200, 'walk_out': 0, 'stage': 0}
ROOKC = dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6')
BLUE, BLUE2, RED, BRASS, STEEL = '2A3C6E', '222F58', 'B8322E', 'D8A83A', 'C8CCD6'
BRICK, STONE, WOOD, WOODD = '8E4232', 'B4A894', '6A4428', '4A2E1E'
AMB = dict(                         # horizon, zenith, strength, sun watts, sun colour, sun direction
    office=('3A3430', '22262E', 0.35, 0.0, 'FFFFFF', (0, 0, 1)),
    vault=('342C26', '1E1E26', 0.3, 0.0, 'FFFFFF', (0, 0, 1)),
    square=('DCD2C0', '7E90AC', 1.0, 2.6, 'FFE2B8', (-0.45, -0.7, 0.5)),
    street=('D6CCBC', '8494AE', 1.35, 3.2, 'FFE6C4', (0.5, -0.65, 0.5)),
    alley=('5A5468', '2A2C44', 0.5, 0.0, 'FFFFFF', (0, 0, 1)),
    room=('3A322C', '201E24', 0.32, 0.0, 'FFFFFF', (0, 0, 1)),
    cell=('2C3038', '181A22', 0.3, 0.0, 'FFFFFF', (0, 0, 1)),
    palace=('4A3028', '2A1C20', 0.4, 0.0, 'FFFFFF', (0, 0, 1)),
    stage=('2A1A1E', '120E14', 0.22, 0.0, 'FFFFFF', (0, 0, 1)))
_KEEP = []
_PROTO, _LAST = {}, [None]


# ---------------------------------------------------------------- small tools
def _pick(o):
    if _LAST[0] is not None:
        try:
            _LAST[0].select_set(False)
        except (ReferenceError, RuntimeError):
            pass
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    _LAST[0] = o


def _norm(kind, kw):
    """Split primitive arguments into a cacheable unit mesh and a size."""
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
    """Same call as kit3d.add, but each primitive mesh is made once and copied: this world has several thousand parts."""
    kw, sz = _norm(kind, dict(kw))
    key = (kind, tuple(sorted(kw.items())))
    if key not in _PROTO or _PROTO[key].name not in bpy.data.meshes:
        getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=(0, 0, 0), **kw)
        o = bpy.context.object
        _PROTO[key] = o.data
        bpy.data.objects.remove(o)
    me = _PROTO[key].copy()
    if sz != (1.0, 1.0, 1.0):
        me.transform(Matrix.Diagonal((sz[0], sz[1], sz[2], 1.0)))
    o = bpy.data.objects.new(kind, me)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    me.materials.append(K.mat(col, rough, emit, alpha))
    if kind in ('cube', 'cylinder', 'cone') and alpha >= 1 and not emit:
        K._bevel(o, scale)
    if parent:
        o.parent = parent
    _pick(o)
    return o


def empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new('Empty', None)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    _pick(o)
    return o


def box(col, loc, size, par=None, rot=(0, 0, 0), **kw):
    return add('cube', col, loc, rot=rot, scale=size, size=1, parent=par, **kw)


def cyl(col, loc, r, d, par=None, rot=(0, 0, 0), v=8, **kw):
    return add('cylinder', col, loc, rot=rot, radius=r, depth=d, vertices=v, parent=par, **kw)


def sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rnd(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def keep(o):
    """Remember a movable prop's parked state; reset() puts it back before every frame."""
    _KEEP.append((o, o.parent, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return o


def at(o, x, y, z=0.0):
    return (o[0] + x, o[1] + y, o[2] + z)


def plus(a, b, s=1.0):
    return (a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s)


def mix(a, b, k):
    return tuple(lerp(x, y, k) for x, y in zip(a, b))


def off(loc, yaw, v):
    """A point given in a character's own frame (x right, -y forward) as a world point."""
    c, s = math.cos(yaw), math.sin(yaw)
    return (loc[0] + v[0] * c - v[1] * s, loc[1] + v[0] * s + v[1] * c, loc[2] + v[2])


def lay(o, a, b):
    """Put an object's origin at a and point its local +Z at b."""
    d = Vector(b) - Vector(a)
    o.location = a
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()


def wpos(o, v=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(v))


def facing(frm, to):
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))


def shell(o, w, d, h, wall, floor, trim=WOODD, front=False, dado=1.5):
    """A room without a ceiling: floor, back wall at +y, side walls, a dark dado. Returns its root."""
    r = empty(o)
    box(floor, (0, 0, -0.06), (w, d, 0.12), r)
    for i in range(int(w // 1.4)):                                                                    # floorboard seams
        box(trim, (-w / 2 + 0.7 + 1.4 * i, 0, 0.005), (0.04, d, 0.012), r)
    box(wall, (0, d / 2 + 0.15, h / 2), (w + 0.6, 0.3, h), r)
    box(trim, (0, d / 2 - 0.06, dado / 2), (w, 0.14, dado), r)
    for s in (-1, 1):
        box(wall, (s * (w / 2 + 0.15), 0, h / 2), (0.3, d, h), r)
        box(trim, (s * (w / 2 - 0.06), 0, dado / 2), (0.14, d, dado), r)
    if front:
        box(wall, (0, -d / 2 - 0.15, h / 2), (w + 0.6, 0.3, h), r)
    return r


def window(par, x, y, z, w, h, glow='CFE0F0', e=2.2, frame=WOODD, ry=0.0):
    """A window as a lit pane with a frame and glazing bars, on a wall facing -y (ry turns it for side walls)."""
    r = empty((x, y, z), par, (0, 0, ry))
    box(glow, (0, 0, 0), (w, 0.06, h), r, emit=e)
    box(frame, (0, -0.05, 0), (0.1, 0.08, h), r)
    for dz in (-h / 2, 0.0, h / 2):
        box(frame, (0, -0.05, dz), (w + 0.2, 0.1, 0.12), r)
    for s in (-1, 1):
        box(frame, (s * w / 2, -0.05, 0), (0.12, 0.1, h + 0.2), r)
    return r


# ---------------------------------------------------------------- props
def make_rifle():
    """A plain rifle with a fixed bayonet, built along local +Z from the butt (origin)."""
    r = keep(empty(FAR))
    box('5E3C24', (0, 0.02, 0.26), (0.085, 0.17, 0.52), r)
    box('5E3C24', (0, 0, 0.92), (0.07, 0.1, 0.9), r)
    cyl('3A3E46', (0, -0.01, 1.55), 0.03, 0.95, r, v=6, rough=0.4)
    box('E2E6EE', (0, -0.01, 2.26), (0.022, 0.06, 0.5), r, rough=0.2)
    return r


def make_cap(par=None, loc=FAR):
    """The captain's peaked cap: blue crown, red band, black visor. Origin where it sits on a head."""
    r = empty(loc, par)
    cyl(RED, (0, 0, 0.05), 0.315, 0.1, r, v=10)
    cyl(BLUE, (0, 0, 0.16), 0.335, 0.14, r, v=10)
    cyl(BLUE, (0, 0, 0.24), 0.37, 0.04, r, v=10)
    box('15151A', (0, -0.36, 0.0), (0.42, 0.24, 0.03), r, rot=(0.28, 0, 0), rough=0.3)
    cyl(BRASS, (0, -0.325, 0.1), 0.035, 0.03, r, rot=(PI / 2, 0, 0), v=6, rough=0.3)
    return r


def spiked(col, trim):
    """A spiked helmet for soldiers and policemen."""
    def fn(head):
        add('ico_sphere', col, (0, 0.02, 0.15), scale=(1.06, 1.12, 0.78), radius=0.31, subdivisions=1, parent=head, rough=0.35)
        box(col, (0, -0.33, 0.1), (0.4, 0.2, 0.03), head, rot=(-0.35, 0, 0), rough=0.35)
        box(col, (0, 0.34, 0.06), (0.4, 0.2, 0.03), head, rot=(0.5, 0, 0), rough=0.35)
        add('cone', trim, (0, 0.02, 0.5), radius1=0.06, radius2=0.0, depth=0.3, vertices=6, parent=head, rough=0.3)
        cyl(trim, (0, 0.02, 0.37), 0.09, 0.04, head, v=8, rough=0.3)
        box(trim, (0, -0.325, 0.2), (0.14, 0.03, 0.14), head, rot=(-0.2, 0, PI / 4), rough=0.3)
    return fn


def face(skin, hair, bald=False, tache=None, beard=None, glasses=False, hat=None, curl=False):
    """A head for the humans of this case, on top of the kit's plain face."""
    def fn(head):
        d = K.human_head(skin, skin if bald else hair)(head)
        if bald:                                                                                      # a fringe of hair round the back
            for s in (-1, 1):
                add('ico_sphere', hair, (s * 0.24, 0.08, 0.02), scale=(0.5, 0.9, 0.8), radius=0.16, subdivisions=1, parent=head)
            add('ico_sphere', hair, (0, 0.24, 0.0), scale=(1.2, 0.5, 0.8), radius=0.2, subdivisions=1, parent=head)
        if tache:
            for s in (-1, 1):
                box(tache, (s * 0.085, -0.3, -0.065), (0.17, 0.06, 0.06), head, rot=(0, s * (-0.75 if curl else 0.3), s * 0.25))
                if curl:
                    box(tache, (s * 0.175, -0.29, -0.0), (0.05, 0.05, 0.11), head)
        if beard:
            add('ico_sphere', beard, (0, -0.17, -0.25), scale=(0.95, 0.75, 0.75), radius=0.2, subdivisions=1, parent=head)
        if glasses:
            for s in (-1, 1):
                add('torus', BRASS, (s * 0.105, -0.3, 0.04), rot=(PI / 2, 0, 0), major_radius=0.065, minor_radius=0.012, major_segments=10,
                    minor_segments=4, parent=head, rough=0.3)
            box(BRASS, (0, -0.3, 0.05), (0.08, 0.015, 0.015), head, rough=0.3)
        if hat:
            hat(head)
        return d
    return fn


def tunic(rig, col=BLUE, buttons=6, collar=RED, belt='E8E2D4', epaulette=None, sash=None):
    """Dress a plain rig as a uniform: collar, a row of brass buttons, a belt, optional epaulettes and sash."""
    b = rig.body
    box(collar, (0, -0.02, 1.15), (0.36, 0.34, 0.1), b)
    for i in range(buttons):
        z = 0.18 + 0.13 * i
        cyl(BRASS, (0, -0.305 - 0.07 * z, z), 0.035, 0.03, b, rot=(PI / 2, 0, 0), v=6, rough=0.25)
    if belt:
        cyl(belt, (0, 0, 0.1), 0.335, 0.09, b, v=8)
        box(BRASS, (0, -0.33, 0.1), (0.1, 0.03, 0.1), b, rough=0.3)
    if epaulette:
        for s in (-1, 1):
            box(epaulette, (s * 0.42, 0, 1.135), (0.3, 0.32, 0.05), b, rough=0.35)
    if sash:
        box(sash, (0, -0.345, 0.56), (0.92, 0.03, 0.15), b, rot=(0, 0.8, 0), rough=0.6)


def make_boot(col='2A2420', s=1.0):
    r = keep(empty(FAR))
    box(col, (0, -0.1, 0.07), (0.2, 0.5, 0.14), r, rough=0.5)
    box(col, (0, 0.08, 0.3), (0.19, 0.2, 0.42), r, rough=0.5)
    box('8A6A44', (0, -0.1, -0.01), (0.21, 0.52, 0.03), r)
    r.scale = (s, s, s)
    return r


def make_money(S):
    """The town's cash: note bundles, coin stacks, small sacks; and the captain's leather bag."""
    S['notes'] = []
    for i in range(6):
        r = keep(empty(FAR))
        box(('C8D2B4', 'D6CDB0', 'BCC8C0')[i % 3], (0, 0, 0.06), (0.5, 0.3, 0.12), r)
        box('8A4A3A', (0, 0, 0.06), (0.12, 0.31, 0.125), r)
        S['notes'].append(r)
    S['coins'] = []
    for i in range(7):
        r = keep(empty(FAR))
        n = 3 + i % 3
        for j in range(n):
            cyl('E8B848', (0.01 * (j % 2), 0, 0.03 + 0.06 * j), 0.11, 0.05, r, v=10, rough=0.25)
        S['coins'].append(r)
    S['sacks'] = []
    for i in range(3):
        r = keep(empty(FAR))
        add('ico_sphere', 'B8A27A', (0, 0, 0.2), scale=(1, 1, 0.85), radius=0.26, subdivisions=1, parent=r, rough=1.0)
        add('cone', 'B8A27A', (0, 0, 0.47), rot=(PI, 0, 0), radius1=0.14, radius2=0.04, depth=0.18, vertices=6, parent=r, rough=1.0)
        cyl('5A3A22', (0, 0, 0.4), 0.07, 0.04, r, v=6)
        S['sacks'].append(r)
    S['bag'] = r = keep(empty(FAR))
    box('5A3420', (0, 0, 0.32), (0.95, 0.5, 0.64), r, rough=0.6)
    box('46281A', (0, 0, 0.66), (0.99, 0.54, 0.06), r, rough=0.6)
    add('torus', '3A2216', (0, 0, 0.74), rot=(PI / 2, 0, 0), major_radius=0.2, minor_radius=0.03, major_segments=10, minor_segments=4, parent=r)
    box(BRASS, (0, -0.26, 0.5), (0.12, 0.03, 0.1), r, rough=0.3)
    S['cashbox'] = r = keep(empty(FAR))
    box('3A4038', (0, 0, 0.18), (0.9, 0.6, 0.36), r, rough=0.5)
    box(BRASS, (0, -0.31, 0.2), (0.12, 0.03, 0.12), r, rough=0.3)
    S['cashlid'] = empty((0, 0.3, 0.36), r)
    box('3A4038', (0, -0.3, 0.03), (0.92, 0.62, 0.06), S['cashlid'], rough=0.5)


# ---------------------------------------------------------------- sets
def make_office(S):
    r = shell(OFF, 14, 12, 7.5, '3E5648', '5A4030', front=False)
    box('7A2E2A', (0, 0.6, 0.012), (9, 6.4, 0.02), r, rough=1.0)                                      # rug
    box('B8742E', (0, 0.6, 0.006), (9.5, 6.9, 0.02), r, rough=1.0)
    for s in (-1, 1):                                                                                 # the door wall, behind the lens in the hook
        box('3E5648', (s * 4.5, -6.15, 3.75), (5.6, 0.3, 7.5), r)
        box(WOODD, (s * 4.5, -5.94, 0.75), (5.6, 0.14, 1.5), r)
        box(WOOD, (s * 1.75, -6.0, 2.3), (0.3, 0.5, 4.6), r)
        box(WOOD, (s * 2.55, -5.2, 2.2), (0.14, 1.6, 4.3), r, rot=(0, 0, s * 0.25))                   # the door leaves, thrown open
    box('3E5648', (0, -6.15, 6.05), (3.6, 0.3, 2.9), r)
    box(WOOD, (0, -6.0, 4.7), (3.8, 0.5, 0.3), r)
    box('14131A', (0, -10.5, 3), (9, 0.3, 7), r)                                                      # the dark corridor
    box('2A2622', (0, -8.3, -0.06), (9, 4.4, 0.12), r)
    for s in (-1, 1):
        box('1E1C22', (s * 3.4, -8.3, 3), (0.3, 4.4, 7), r)
    window(r, -3.9, 5.95, 4.1, 2.6, 3.8)
    for s in (-1, 1):                                                                                 # curtains
        for j in range(3):
            cyl('6A2A2A', (-3.9 + s * (1.75 + 0.22 * j), 5.75, 4.0), 0.16, 4.6, r, v=6, rough=1.0)
    box(WOODD, (4.1, 5.6, 2.9), (3.4, 0.7, 5.6), r)                                                   # bookcase
    for row in range(5):
        x = 2.6
        i = 0
        while x < 5.5:
            w = 0.14 + 0.12 * rnd(row * 31 + i, 1)
            hh = 0.62 + 0.2 * rnd(row * 31 + i, 2)
            box(('6A2E2A', '2E4A3A', '8A6A3A', '2A3A5A', '5A4A3A', 'B8742E')[int(rnd(row * 31 + i, 3) * 6)], (x + w / 2, 5.2, 0.55 + row * 1.05 + hh / 2),
                (w, 0.4, hh), r)
            x += w + 0.02
            i += 1
        box(WOOD, (4.1, 5.3, 0.48 + row * 1.05), (3.3, 0.6, 0.07), r)
    box(BRASS, (0.6, 5.9, 4.6), (2.0, 0.12, 2.6), r, rough=0.35)                                      # an empty gilt frame: no portrait
    box('24362E', (0.6, 5.84, 4.6), (1.6, 0.06, 2.2), r)
    cyl('E8E0CC', (-0.9, 5.88, 5.9), 0.42, 0.08, r, rot=(PI / 2, 0, 0), v=12)                         # wall clock
    cyl(WOODD, (-0.9, 5.9, 5.9), 0.5, 0.06, r, rot=(PI / 2, 0, 0), v=12)
    box('15151A', (-0.9, 5.82, 6.02), (0.03, 0.03, 0.28), r)
    box('15151A', (-0.8, 5.82, 5.9), (0.2, 0.03, 0.03), r)
    box(WOOD, (0, 0.6, 1.2), (4.8, 1.95, 0.13), r, rough=0.5)                                         # the desk
    box(WOODD, (0, -0.28, 0.6), (4.6, 0.1, 1.2), r)
    for s in (-1, 1):
        box(WOODD, (s * 1.75, 0.6, 0.6), (1.1, 1.8, 1.2), r)
        cyl(BRASS, (s * 1.75, -0.36, 0.85), 0.06, 0.05, r, rot=(PI / 2, 0, 0), v=6, rough=0.3)
    box('2E4A3A', (0, 0.7, 1.275), (2.2, 1.2, 0.02), r)                                               # blotter
    box('F0E8D4', (-0.25, 0.75, 1.29), (0.7, 0.95, 0.015), r, rot=(0, 0, 0.1))
    box('F0E8D4', (1.4, 0.4, 1.29), (0.6, 0.85, 0.05), r, rot=(0, 0, -0.2))
    cyl('15151A', (0.75, 1.2, 1.36), 0.1, 0.16, r, v=8, rough=0.3)                                    # inkwell
    cyl(BRASS, (-1.9, 0.9, 1.3), 0.16, 0.06, r, v=8, rough=0.3)                                       # desk lamp with an orange shade
    cyl(BRASS, (-1.9, 0.9, 1.6), 0.03, 0.6, r, v=6, rough=0.3)
    add('cone', 'FF7A1A', (-1.9, 0.9, 1.98), radius1=0.34, radius2=0.14, depth=0.3, vertices=8, parent=r, emit=2.5)
    add('ico_sphere', BRASS, (1.95, 1.1, 1.35), radius=0.12, subdivisions=1, parent=r, rough=0.3)     # desk bell
    box(WOODD, (0, 3.0, 1.75), (1.5, 0.16, 2.9), r)                                                   # the mayor's chair
    box('6A2A2A', (0, 2.9, 1.9), (1.2, 0.1, 1.9), r, rough=1.0)
    box(WOODD, (0, 2.35, 0.42), (1.5, 1.3, 0.14), r)
    for sx in (-1, 1):
        box(WOODD, (sx * 0.68, 2.35, 0.2), (0.12, 1.2, 0.42), r)
    tg = empty((0, 1.2, 1.8), r)
    light(at(OFF, -4.4, 2.6, 5.6), 1100, 'FFE4BE', size=4.0, target=tg)
    light(at(OFF, 4.5, -3.5, 5.0), 500, '9FB6FF', size=3.0, target=tg)
    light(at(OFF, -1.9, 0.75, 2.1), 60, 'FF9A4A', kind='POINT')
    S['office'] = r


def make_treasury(S):
    r = shell(TRE, 12, 10, 7, '5A4C3E', '4A3A2C')
    box('2C3038', (2.9, 4.2, 2.2), (3.0, 1.6, 4.4), r, rough=0.45)                                    # the safe
    box('14151A', (2.9, 3.42, 2.3), (2.5, 0.1, 3.8), r)
    for j in range(3):
        box('3A3E46', (2.9, 3.7, 1.0 + 1.1 * j), (2.5, 0.6, 0.07), r, rough=0.4)
        for i in range(4):
            box(('C8D2B4', 'D6CDB0', 'E8B848', 'BCC8C0')[(i + j) % 4], (2.0 + 0.6 * i, 3.6, 1.14 + 1.1 * j), (0.42, 0.3, 0.2), r,
                rough=0.3 if (i + j) % 4 == 2 else 0.9)
    dr = empty((1.55, 3.4, 0), r, (0, 0, -2.0))                                                       # its door, swung wide
    box('343842', (1.3, 0, 2.3), (2.6, 0.26, 4.0), dr, rough=0.4)
    add('torus', BRASS, (1.3, -0.2, 2.4), rot=(PI / 2, 0, 0), major_radius=0.45, minor_radius=0.05, major_segments=12, minor_segments=4, parent=dr, rough=0.3)
    for i in range(4):
        box(BRASS, (1.3, -0.2, 2.4), (0.9, 0.05, 0.05), dr, rot=(0, i * PI / 4, 0), rough=0.3)
    box(WOODD, (-3.6, 4.5, 2.6), (3.6, 0.7, 5.0), r)                                                  # ledger shelves
    for row in range(4):
        for i in range(9):
            hh = 0.7 + 0.15 * rnd(row * 17 + i, 4)
            box(('5A3A2A', '3A4A3A', '6A5A3A', '4A3A4A')[(i + row) % 4], (-5.1 + 0.36 * i, 4.15, 0.5 + row * 1.15 + hh / 2), (0.3, 0.4, hh), r)
        box(WOOD, (-3.6, 4.2, 0.44 + row * 1.15), (3.5, 0.6, 0.07), r)
    box(WOOD, (0, -0.3, 1.2), (5.4, 1.9, 0.13), r, rough=0.5)                                         # the counting table
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(WOODD, (sx * 2.4, -0.3 + sy * 0.75, 0.6), (0.2, 0.2, 1.2), r)
    box('2E4A3A', (0, -0.3, 1.272), (4.6, 1.4, 0.015), r)
    cyl('15151A', (0, 0.2, 5.4), 0.025, 3.2, r, v=5)                                                  # hanging lamp
    add('cone', '2E4A3A', (0, 0.2, 3.9), radius1=0.6, radius2=0.12, depth=0.4, vertices=10, parent=r, rough=0.4)
    add('ico_sphere', 'FFD9A0', (0, 0.2, 3.72), radius=0.14, subdivisions=1, parent=r, emit=14)
    window(r, -5.95, -1.0, 4.0, 2.2, 3.2, ry=PI / 2)
    tg = empty((0.5, 0.3, 1.6), r)
    light(at(TRE, 0, 0.0, 3.6), 520, 'FFD9A0', size=1.4, target=tg)
    light(at(TRE, -5.0, -2.5, 4.6), 600, 'CFE0FF', size=3.0, target=tg)
    light(at(TRE, 4.6, -4.0, 4.0), 260, 'FF9A4A', size=3.0, target=tg)
    S['treasury'] = r


def make_square(S):
    r = empty(EXT)
    box('5E5E66', (0, -20, -0.1), (160, 120, 0.2), r, rough=1.0)                                      # cobbles
    for i in range(60):
        box('6A6A72', (-30 + 60 * rnd(i, 1), -26 + 30 * rnd(i, 2), 0.004), (1.1 + rnd(i, 3), 0.7 + rnd(i, 4), 0.02), r, rough=1.0)
    box(BRICK, (2, 13, 7.5), (26, 10, 15), r, rough=1.0)                                              # the town hall
    box(STONE, (2, 8.05, 0.7), (26.2, 0.3, 1.4), r)
    box(STONE, (2, 8.0, 7.2), (26.2, 0.24, 0.3), r)
    box(STONE, (2, 8.0, 15.0), (26.6, 0.5, 0.5), r)
    for j, w in enumerate((11.0, 8.0, 5.0, 2.4)):                                                     # stepped gable
        box(BRICK, (2, 12, 15.9 + 1.7 * j), (w, 8, 1.8), r, rough=1.0)
        box(STONE, (2, 8.2, 16.75 + 1.7 * j), (w + 0.3, 0.5, 0.2), r)
    for row, z in enumerate((4.4, 10.6)):
        for i in range(7):
            x = -8.8 + 3.6 * i
            if row == 0 and abs(x - 2) < 2.5:
                continue
            box(STONE, (x, 7.98, z), (2.0, 0.2, 3.2), r)
            window(r, x, 7.86, z, 1.5, 2.6, glow='FFD890', e=0.9, frame='3A2A22')
    box(STONE, (2, 7.9, 2.9), (4.8, 0.5, 5.8), r)                                                     # the portal
    box('1A161A', (2, 7.62, 2.6), (3.2, 0.2, 5.0), r)
    add('cone', STONE, (2, 7.9, 6.9), rot=(PI / 2, 0, 0), radius1=2.6, radius2=2.6, depth=0.5, vertices=3, parent=r)
    for i, (y, h) in enumerate(((7.0, 0.6), (5.8, 0.4), (4.9, 0.2))):                                 # steps
        box('A39C90', (2, y, h / 2), (9.0 + 0.8 * i, 1.3 if i == 0 else 1.0, h), r)
    box('7C3628', (-11.5, 12, 13), (6.5, 7, 26), r, rough=1.0)                                        # the tower
    box(STONE, (-11.5, 8.45, 21.0), (6.8, 0.2, 0.4), r)
    cyl('E8E0CC', (-11.5, 8.42, 18.2), 1.7, 0.12, r, rot=(PI / 2, 0, 0), v=14)
    box('15151A', (-11.5, 8.32, 18.75), (0.12, 0.05, 1.2), r)
    box('15151A', (-11.05, 8.32, 18.2), (0.9, 0.05, 0.12), r)
    add('cone', '3E5A52', (-11.5, 12, 29.5), rot=(0, 0, PI / 4), radius1=5.2, radius2=0.0, depth=7.5, vertices=4, parent=r, rough=0.6)
    add('cone', BRASS, (-11.5, 12, 33.8), radius1=0.25, radius2=0.0, depth=1.6, vertices=4, parent=r, rough=0.3)
    for i, (x, w, h, c) in enumerate(((-30, 20, 12, '6E6A72'), (30, 24, 11, '7C6C5C'), (-52, 22, 14, '665E62'), (56, 22, 13, '6A6258'))):
        box(c, (x, 14, h / 2), (w, 12, h), r, rough=1.0)                                              # the neighbours
        add('cone', '4A3A38', (x, 14, h + 1.6), rot=(0, 0, PI / 4), scale=(w / 12, 1, 1), radius1=8.6, radius2=0.0, depth=3.2, vertices=4, parent=r)
        for k in range(int(w // 4)):
            window(r, x - w / 2 + 2.2 + 4 * k, 7.94, h * 0.55, 1.3, 2.2, glow='E8D6A8', e=0.5, frame='2E2622')
    for s in (-1, 1):                                                                                 # gas lamps
        cyl('1E1E24', (2 + s * 7, 3.2, 2.2), 0.09, 4.4, r, v=6)
        box('FFB25A', (2 + s * 7, 3.2, 4.6), (0.4, 0.4, 0.5), r, emit=4.0)
        add('cone', '1E1E24', (2 + s * 7, 3.2, 5.0), radius1=0.38, radius2=0.0, depth=0.35, vertices=4, parent=r)
    S['square'] = r


def stepz(y):
    """Height of the town hall steps at set-local y (centred on x = 2)."""
    return 0.6 if y > 6.35 else 0.4 if y > 5.3 else 0.2 if y > 4.4 else 0.0


def make_street(S):
    r = empty(STR)
    box('5A5A62', (0, -8, -0.1), (140, 60, 0.2), r, rough=1.0)
    for i in range(50):
        box('686870', (-28 + 56 * rnd(i, 5), -8 + 12 * rnd(i, 6), 0.004), (1.0 + rnd(i, 7), 0.6 + rnd(i, 8), 0.02), r, rough=1.0)
    box('8A8680', (0, 6.3, 0.1), (140, 2.6, 0.2), r, rough=1.0)                                       # pavement
    x = -44.0
    i = 0
    while x < 44:
        w = 7.0 + 3.0 * rnd(i, 9)
        h = 11.0 + 5.0 * rnd(i, 10)
        c = ('6C6872', '7C7064', '5E6470', '82766A', '6E6660', '74707A')[i % 6]
        box(c, (x + w / 2, 12, h / 2), (w - 0.1, 9, h), r, rough=1.0)
        box('4A4040', (x + w / 2, 12, h + 0.3), (w + 0.2, 9.4, 0.6), r)
        box('3A2A22', (x + w / 2 - 1.2, 7.48, 1.7), (1.5, 0.12, 3.4), r)
        for fl in range(int((h - 4.5) // 3)):
            for k in range(int(w // 2.6)):
                lit = rnd(i * 13 + fl * 5 + k, 11) > 0.6
                window(r, x + 1.5 + 2.6 * k, 7.44, 5.6 + 3.0 * fl, 1.2, 1.9, glow='FFD890' if lit else '8A94A4', e=0.8 if lit else 0.25, frame='2E2622')
        x += w
        i += 1
    for i in range(6):                                                                                # gas lamps along the kerb
        lx = -30 + 12 * i
        cyl('1E1E24', (lx, 5.3, 2.2), 0.09, 4.4, r, v=6)
        box('FFB25A', (lx, 5.3, 4.6), (0.4, 0.4, 0.5), r, emit=4.0)
    sb = empty((-9.5, 5.6, 0), r)                                                                     # a sentry box in black and white stripes
    for j in range(7):
        box('E8E4DA' if j % 2 else '1A1A20', (0, 0, 0.25 + 0.5 * j), (1.5, 1.5, 0.5), sb)
    add('cone', 'FF7A1A', (0, 0, 4.0), rot=(0, 0, PI / 4), radius1=1.25, radius2=0.0, depth=1.0, vertices=4, parent=sb)
    box('14141A', (0, -0.76, 1.6), (0.9, 0.06, 3.0), sb)
    for x_, w_, h_ in ((-60, 30, 14), (62, 30, 13)):                                                  # the street closes off at both ends
        box('66626A', (x_, -2, h_ / 2), (w_, 40, h_), r, rough=1.0)
    S['street'] = r


def make_alley(S):
    r = empty(ALY)
    box('4A4A52', (0, -4, -0.1), (40, 30, 0.2), r, rough=1.0)
    box('6E3C32', (0, 3.4, 6), (30, 0.8, 12), r, rough=1.0)
    for i in range(70):                                                                               # odd bricks
        box(('7C463A', '5E3229', '87503F')[i % 3], (-12 + 24 * rnd(i, 12), 2.98, 0.4 + 8.5 * rnd(i, 13)), (0.7, 0.06, 0.26), r, rough=1.0)
    box('54302A', (-7.6, -4, 6), (0.8, 16, 12), r, rough=1.0)
    box('60362E', (9.6, -4, 6), (0.8, 16, 12), r, rough=1.0)
    box('17141A', (3.6, 2.96, 2.1), (1.8, 0.1, 4.2), r)                                               # a back door
    box(STONE, (3.6, 2.9, 4.35), (2.2, 0.2, 0.3), r)
    cyl('2A2A30', (-4.6, 2.8, 5), 0.13, 10, r, v=6, rough=0.5)                                        # drainpipe
    for j, (x, y, s) in enumerate(((-5.6, 1.6, 1.3), (-5.2, 0.4, 1.0), (-5.7, 1.5, 0.9))):            # crates
        box(('7A5A36', '6A4C2E', '826240')[j], (x, y, s / 2 if j < 2 else 1.3 + s / 2), (s, s, s), r, rot=(0, 0, 0.2 * j))
    cyl('3A3A40', (6.4, 1.8, 0.7), 0.6, 1.4, r, v=10, rough=0.6)                                      # a barrel
    box('1E1E24', (-1.6, 2.7, 4.6), (0.1, 0.7, 0.1), r)                                               # wall lamp
    box('FFB25A', (-1.6, 2.3, 4.4), (0.45, 0.45, 0.6), r, emit=6.0)
    tg = empty((0.5, 0, 1.8), r)
    light(at(ALY, -1.6, 1.4, 4.3), 420, 'FFB060', kind='POINT')
    light(at(ALY, 4.5, -6, 6), 700, '8EA4E8', size=4.0, target=tg)
    S['alley'] = r


def make_cobbler(S):
    r = shell(COB, 9, 8, 6, '665C4C', '4E3E2E', trim='3E3024', dado=1.2)
    for i in range(9):                                                                                # cracked plaster
        box('544A3C', (-3.8 + 7.6 * rnd(i, 14), 3.92, 2 + 3.4 * rnd(i, 15)), (0.9 * rnd(i, 16) + 0.3, 0.04, 0.05), r, rot=(0, 0.6 * rnd(i, 17) - 0.3, 0))
    for row in range(3):                                                                              # shelves of boots waiting for repair
        box(WOOD, (1.6, 3.6, 2.2 + 1.05 * row), (4.4, 0.7, 0.08), r)
        for i in range(6):
            b = make_boot(('2A2420', '4A3222', '1E1C20', '5A3E28')[(i + row) % 4], 0.95)
            _KEEP.pop()
            b.parent = r
            b.location = (-0.3 + 0.75 * i, 3.55, 2.25 + 1.05 * row)
            b.rotation_euler = (0, 0, 0.3 * rnd(i + row * 7, 18) - 0.15)
    window(r, -2.6, 3.95, 3.6, 1.6, 2.0, glow='B8CCE4', e=1.8, frame='3E3024')
    box(WOOD, (0, 0.1, 0.95), (2.6, 1.3, 0.12), r)                                                    # the bench
    for sx in (-1, 1):
        box(WOODD, (sx * 1.1, 0.1, 0.47), (0.16, 1.1, 0.95), r)
    cyl('3A3E46', (-0.1, 0.05, 1.2), 0.05, 0.4, r, v=6, rough=0.4)                                    # the iron last
    box('3A3E46', (-0.1, -0.02, 1.42), (0.16, 0.42, 0.08), r, rough=0.4)
    for i in range(5):                                                                                # leather scraps, a tin of nails
        box(('8A6A44', '6A4A2E', '9A7A52')[i % 3], (0.5 + 0.2 * i, 0.3 * rnd(i, 19) - 0.1, 1.02), (0.3, 0.22, 0.02), r, rot=(0, 0, rnd(i, 20)))
    cyl('8A8E96', (-0.95, 0.4, 1.08), 0.12, 0.14, r, v=8, rough=0.4)
    cyl(WOODD, (0, 1.45, 0.42), 0.36, 0.1, r, v=8)                                                    # stool
    cyl(WOODD, (0, 1.45, 0.2), 0.08, 0.4, r, v=6)
    cyl('15151A', (0.4, 0.4, 4.9), 0.02, 2.2, r, v=5)                                                 # a bare hanging lamp
    add('cone', '3A3A40', (0.4, 0.4, 3.85), radius1=0.42, radius2=0.1, depth=0.26, vertices=8, parent=r)
    add('ico_sphere', 'FFC878', (0.4, 0.4, 3.72), radius=0.12, subdivisions=1, parent=r, emit=14)
    box('2A2A30', (3.6, 2.9, 1.0), (1.1, 1.1, 2.0), r, rough=0.6)                                     # a small stove
    cyl('2A2A30', (3.6, 3.1, 3.9), 0.14, 4.0, r, v=6, rough=0.6)
    box('FF7A1A', (3.6, 2.33, 0.8), (0.5, 0.04, 0.3), r, emit=5.0)
    tg = empty((0, 0.6, 1.4), r)
    light(at(COB, 0.4, 0.2, 3.6), 380, 'FFC878', size=1.2, target=tg)
    light(at(COB, -3.4, -2.4, 4.0), 320, 'A8C0F0', size=3.0, target=tg)
    S['cobbler'] = r


def make_shop(S):
    r = shell(SHP, 12, 9, 6.5, '4E4250', '4A3A30', trim='32262E', front=True)
    fw = empty((0.5, -4.45, 3.4), r, (0, 0, PI))                                                       # the shop window, seen from inside
    window(fw, 0, 0, 0, 4.6, 3.4, glow='C8D4E4', e=2.6, frame='32262E')
    box('32262E', (4.3, -4.4, 2.2), (1.7, 0.14, 4.4), r)
    cyl(BRASS, (-1.5, 4.0, 4.3), 0.05, 8.6, r, rot=(0, PI / 2, 0), v=6, rough=0.3)                    # a rail of old coats
    for i in range(13):
        if 3 <= i <= 5:
            continue
        x = -5.6 + 0.66 * i
        c = ('5A5248', '3E4A52', '6A5A4A', '4A3E48', '70684E', '38404A')[i % 6]
        box(c, (x, 4.0, 2.9 + 0.1 * rnd(i, 21)), (0.56, 0.34, 2.5), r, rot=(0, 0, 0.2 * rnd(i, 22) - 0.1), rough=1.0)
        box(c, (x, 4.0, 4.05), (0.8, 0.3, 0.14), r, rough=1.0)
    d = empty((-1.3, 1.6, 0), r)                                                                      # the tailor's dummy in the captain's tunic
    cyl(WOODD, (0, 0, 0.06), 0.42, 0.12, d, v=8)
    cyl(WOODD, (0, 0, 0.75), 0.05, 1.4, d, v=6)
    add('cone', BLUE, (0, 0, 1.95), radius1=0.34, radius2=0.42, depth=1.15, vertices=8, parent=d)
    box(BLUE, (0, 0, 2.58), (0.86, 0.38, 0.13), d)
    box(RED, (0, -0.02, 2.68), (0.38, 0.36, 0.1), d)
    for s in (-1, 1):
        box(STEEL, (s * 0.45, 0, 2.66), (0.3, 0.34, 0.05), d, rough=0.35)
        cyl(BLUE, (s * 0.5, 0, 2.2), 0.095, 0.8, d, v=6)
    S['dbuttons'] = []
    for i in range(6):
        z = 1.5 + 0.17 * i
        S['dbuttons'].append(cyl(BRASS, (0, -0.36 - 0.07 * (z - 1.4), z), 0.04, 0.035, d, rot=(PI / 2, 0, 0), v=6, rough=0.2))
    cyl('E8E2D4', (0, 0, 1.45), 0.36, 0.09, d, v=8)
    cyl(WOODD, (0, 0, 2.85), 0.07, 0.3, d, v=6)
    S['dcap'] = make_cap(d, (0, 0, 2.98))
    S['dummy'] = d
    m = empty((2.6, 3.2, 0), r, (0, 0, -0.35))                                                        # a cheval mirror
    box(BRASS, (0, 0, 2.3), (1.7, 0.12, 3.6), m, rough=0.35)
    box('B4C8D4', (0, -0.07, 2.3), (1.4, 0.04, 3.3), m, rough=0.05, emit=0.35)
    for s in (-1, 1):
        box(WOODD, (s * 0.95, 0, 0.3), (0.12, 0.9, 0.6), m)
    box(WOOD, (4.6, -0.6, 1.2), (1.6, 4.4, 0.12), r)                                                  # the counter with folded things
    box(WOODD, (4.6, -0.6, 0.6), (1.4, 4.2, 1.2), r)
    for i in range(5):
        box(('5A5248', '6A2E2A', '3E4A52', '70684E', '2E4A3A')[i], (4.5, -2.2 + 0.8 * i, 1.33 + 0.07 * (i % 2)), (0.9, 0.6, 0.14 + 0.07 * (i % 2)), r, rough=1.0)
    for i in range(4):                                                                                # hat stands
        cyl(WOODD, (-5.0, 3.2 - 1.2 * i, 1.1 + 0.3 * (i % 2)), 0.04, 2.2 + 0.6 * (i % 2), r, v=5)
        add('cone', ('2A2A30', '5A4A3A', '3A3A44', '6A2E2A')[i], (-5.0, 3.2 - 1.2 * i, 2.35 + 0.6 * (i % 2)), radius1=0.3, radius2=0.22, depth=0.34, vertices=8, parent=r)
        cyl(('2A2A30', '5A4A3A', '3A3A44', '6A2E2A')[i], (-5.0, 3.2 - 1.2 * i, 2.2 + 0.6 * (i % 2)), 0.46, 0.04, r, v=10)
    cyl('15151A', (0.6, 0.6, 5.3), 0.02, 2.2, r, v=5)
    add('cone', 'FF7A1A', (0.6, 0.6, 4.2), radius1=0.5, radius2=0.12, depth=0.34, vertices=8, parent=r, rough=0.5)
    add('ico_sphere', 'FFD9A0', (0.6, 0.6, 4.05), radius=0.13, subdivisions=1, parent=r, emit=14)
    tg = empty((-0.5, 1.2, 1.9), r)
    light(at(SHP, 0.6, 0.4, 3.9), 520, 'FFD9A0', size=1.4, target=tg)
    light(at(SHP, -4.5, -3.4, 4.2), 380, 'B4C4F4', size=3.0, target=tg)
    S['shop'] = r


def make_cell(S):
    r = shell(CEL, 7, 6, 6, '5C6068', '44464C', trim='4C5058', dado=0.0)
    for i in range(26):                                                                               # stone blocks
        box(('666A72', '52565E', '6E727A')[i % 3], (-3.2 + 6.4 * rnd(i, 23), 2.93, 0.5 + 5.0 * rnd(i, 24)), (1.1, 0.06, 0.5), r, rough=1.0)
    window(r, 1.2, 2.95, 4.4, 1.3, 1.1, glow='C4D4EC', e=3.0, frame='2A2C32')
    for i in range(4):
        cyl('1E2026', (0.72 + 0.32 * i, 2.82, 4.4), 0.045, 1.2, r, v=6, rough=0.4)
    box('4A3E32', (-0.6, 2.1, 0.62), (4.6, 1.5, 0.14), r)                                             # the bunk
    box('7A7E86', (-0.6, 2.1, 0.74), (4.5, 1.4, 0.12), r, rough=1.0)
    box('8A8474', (-2.5, 2.2, 0.88), (0.8, 1.0, 0.2), r, rough=1.0)
    for sx in (-1, 1):
        box('3A3028', (-0.6 + sx * 2.1, 2.1, 0.3), (0.16, 1.4, 0.6), r)
    cyl('5A5E66', (2.7, 2.2, 0.35), 0.32, 0.7, r, v=8, rough=0.5)                                     # bucket
    box('3E4046', (0, -5.0, -0.06), (9, 4, 0.12), r)                                                  # corridor
    box('4A4E56', (0, -7.1, 3), (9, 0.3, 6), r, rough=1.0)
    for i in range(16):                                                                               # the barred wall, with a gap for the door
        x = -3.3 + 0.44 * i
        if 0.5 < x < 2.7:
            continue
        cyl('1E2026', (x, -3.0, 2.6), 0.055, 5.2, r, v=6, rough=0.4)
    for z in (0.12, 2.6, 5.1):
        box('1E2026', (-1.5, -3.0, z), (4.0, 0.14, 0.14), r, rough=0.4)
        box('1E2026', (3.05, -3.0, z), (0.9, 0.14, 0.14), r, rough=0.4)
    S['celldoor'] = dr = keep(empty((0.55, -3.0, 0), r))
    for i in range(5):
        cyl('1E2026', (0.22 + 0.44 * i, 0, 2.5), 0.055, 5.0, dr, v=6, rough=0.4)
    for z in (0.14, 2.5, 4.9):
        box('1E2026', (1.08, 0, z), (2.16, 0.14, 0.14), dr, rough=0.4)
    box(BRASS, (2.0, -0.08, 2.4), (0.3, 0.1, 0.4), dr, rough=0.3)
    box('1E1E24', (-2.6, -6.9, 4.3), (0.1, 0.5, 0.1), r)
    box('FFB25A', (-2.6, -6.6, 4.1), (0.4, 0.4, 0.55), r, emit=6.0)
    tg = empty((0, 0.6, 1.6), r)
    S['cellkey'] = light(at(CEL, 1.2, 1.4, 4.6), 420, 'C4D4EC', size=1.6, target=tg)
    light(at(CEL, -2.6, -5.9, 4.0), 420, 'FFB060', kind='POINT')
    light(at(CEL, -2.6, -1.4, 3.6), 160, 'FFB060', size=2.0, target=tg)
    tg3 = empty((0.6, -4.4, 1.8), r)
    light(at(CEL, 3.6, -6.2, 4.4), 380, 'FFD0A0', size=2.5, target=tg3)
    S['cell'] = r


def make_palace(S):
    r = shell(PAL, 13, 9, 8, '6E2028', '6A4A2A', trim='4A141C', dado=1.6)
    for i in range(7):                                                                                # gilt pilasters and a cornice
        box(BRASS, (-6 + 2.0 * i, 4.4, 4.6), (0.22, 0.12, 6.0), r, rough=0.35)
    box(BRASS, (0, 4.38, 7.6), (13, 0.2, 0.3), r, rough=0.35)
    box(BRASS, (0, 4.38, 1.65), (13, 0.16, 0.12), r, rough=0.35)
    for i in range(12):                                                                               # parquet
        box('7A5632' if i % 2 else '5E4024', (-6 + 1.08 * i, 0, 0.004), (1.0, 9, 0.012), r, rough=0.5)
    window(r, 6.45, 1.0, 4.6, 2.6, 5.0, glow='FFE6B8', e=2.4, frame=BRASS, ry=-PI / 2)
    for j in range(3):
        cyl('8A2A32', (6.2, 2.8 + 0.22 * j, 4.4), 0.17, 6.0, r, v=6, rough=1.0)
        cyl('8A2A32', (6.2, -0.8 - 0.22 * j, 4.4), 0.17, 6.0, r, v=6, rough=1.0)
    box('E8E0CC', (0, 0.5, 1.25), (5.2, 2.1, 0.14), r, rough=0.4)                                     # a white and gold writing desk
    box('D8CEB8', (0, -0.45, 0.62), (5.0, 0.1, 1.25), r)
    for s in (-1, 1):
        box('D8CEB8', (s * 2.2, 0.5, 0.62), (0.5, 1.9, 1.25), r)
        box(BRASS, (s * 2.2, -0.52, 0.62), (0.3, 0.04, 0.9), r, rough=0.35)
    box('2E4A3A', (0, 0.55, 1.33), (2.6, 1.3, 0.02), r)
    cyl(BRASS, (1.9, 0.9, 1.45), 0.1, 0.26, r, v=8, rough=0.3)
    for s in (-1, 1):                                                                                 # candlesticks
        cyl(BRASS, (s * 2.2, 1.2, 1.7), 0.05, 0.8, r, v=6, rough=0.3)
        add('ico_sphere', 'FFD9A0', (s * 2.2, 1.2, 2.2), radius=0.09, subdivisions=1, parent=r, emit=12)
    box(BRASS, (0, 3.0, 2.3), (1.9, 0.2, 4.2), r, rough=0.35)                                         # a tall gilt chair
    box('8A2A32', (0, 2.88, 2.5), (1.5, 0.1, 3.4), r, rough=1.0)
    box(BRASS, (0, 2.4, 0.42), (1.8, 1.3, 0.14), r, rough=0.35)
    add('torus', BRASS, (0, 0.5, 6.6), major_radius=1.3, minor_radius=0.06, major_segments=14, minor_segments=4, parent=r, rough=0.3)   # chandelier
    for i in range(8):
        a = 2 * PI * i / 8
        add('ico_sphere', 'FFE2B0', (1.3 * math.cos(a), 0.5 + 1.3 * math.sin(a), 6.75), radius=0.1, subdivisions=1, parent=r, emit=10)
    tg = empty((0, 1.6, 2.0), r)
    light(at(PAL, 0, 0.3, 6.2), 800, 'FFE2B0', size=2.4, target=tg)
    light(at(PAL, 5.4, -1.5, 4.6), 700, 'FFE6B8', size=3.5, target=tg)
    light(at(PAL, -5.2, -3.4, 3.6), 260, 'A8B8F0', size=3.0, target=tg)
    S['palace'] = r


def make_theatre(S):
    r = empty(THE)
    box('5E3E28', (0, 6.5, 0.6), (18, 11, 1.2), r)                                                    # the stage
    for i in range(12):
        box('4E3220', (-8.3 + 1.5 * i, 6.5, 1.203), (0.04, 11, 0.01), r)
    box('3A2420', (0, 0.96, 0.6), (18, 0.1, 1.2), r)
    for s in (-1, 1):                                                                                 # the proscenium
        box(BRASS, (s * 7.6, 1.3, 5.5), (1.2, 0.8, 11), r, rough=0.4)
        box('2A1A20', (s * 11, 1.3, 6), (5.6, 0.8, 12), r)
    box(BRASS, (0, 1.3, 10.6), (16.4, 0.8, 1.2), r, rough=0.4)
    box('2A1A20', (0, 1.3, 12.0), (28, 0.8, 1.8), r)
    for i in range(17):                                                                               # valance
        cyl('8E1E24', (-7.2 + 0.9 * i, 1.5, 9.5 - 0.25 * (i % 2)), 0.46, 1.4 + 0.5 * (i % 2), r, v=6, rough=1.0)
    S['curtains'] = []
    for s in (-1, 1):                                                                                 # the curtains: scale x from the outer edge to draw them
        c = keep(empty((s * 7.1, 1.75, 0), r))
        for i in range(10):
            cyl('9A2228' if i % 2 else '7E1A20', (-s * (0.36 + 0.72 * i), 0.08 * (i % 2), 5.3), 0.4, 8.4, c, v=6, rough=1.0)
        box(BRASS, (-s * 3.6, -0.3, 1.5), (7.2, 0.06, 0.2), c, rough=0.4)
        S['curtains'].append((c, s))
    bd = empty((0, 11.6, 1.2), r)                                                                     # a painted backdrop of a town hall: flat and plainly scenery
    box('B8C4CC', (0, 0, 5), (17, 0.1, 10), bd, emit=0.25)
    box('A8584A', (1.5, -0.08, 3.2), (9.5, 0.06, 6.4), bd, emit=0.2)
    box('96483C', (-4.4, -0.1, 4.8), (2.4, 0.06, 9.6), bd, emit=0.2)
    add('cone', '4E6A62', (-4.4, -0.12, 10.2), rot=(PI / 2, 0, 0), scale=(1, 1, 0.02), radius1=1.9, radius2=0.0, depth=2.2, vertices=3, parent=bd, emit=0.2)
    box('3A2A2A', (1.5, -0.12, 1.5), (1.5, 0.06, 3.0), bd, emit=0.1)
    for i in range(4):
        for j in range(2):
            if j == 0 and i in (1, 2):
                continue
            box('F2DCA0', (-1.5 + 2.0 * i, -0.12, 2.2 + 2.6 * j), (0.8, 0.06, 1.3), bd, emit=0.5)
    for j, w in enumerate((4.2, 2.6, 1.2)):
        box('A8584A', (1.5, -0.08, 6.9 + 0.9 * j), (w, 0.06, 1.0), bd, emit=0.2)
    S['flat'] = box('3E4A52', (5.4, 8.4, 3.4), (2.2, 0.16, 4.4), r, rot=(0, 0, -0.5))                 # a scenery flat in the wings
    for i in range(9):                                                                                # footlights
        x = -6 + 1.5 * i
        add('cone', '1E1A1E', (x, 1.02, 1.36), rot=(0.9, 0, 0), radius1=0.28, radius2=0.1, depth=0.3, vertices=8, parent=r)
        add('ico_sphere', 'FFB25A', (x, 1.12, 1.42), radius=0.11, subdivisions=1, parent=r, emit=16)
    box('32222A', (0, -9, -1.5), (30, 20, 0.3), r)                                                    # the house
    for s in (-1, 1):
        box('2A1A22', (s * 13.5, -9, 4), (0.6, 20, 14), r)
        for j in range(3):
            box(BRASS, (s * 13.1, -3 - 5 * j, 3.4), (0.3, 3.6, 0.3), r, rough=0.4)
            box('7E1A20', (s * 13.1, -3 - 5 * j, 2.6), (0.3, 3.4, 1.3), r, rough=1.0)
    box('24161E', (0, -19, 4), (28, 0.6, 14), r)
    S['crowd'] = []
    n = 0
    for row in range(4):
        y = -2.6 - 2.1 * row
        z = -1.35 + 0.4 * row
        box('2A1A20', (0, y - 0.3, z + 0.1), (17, 2.1, 0.2), r)
        for i in range(9):
            x = -7.2 + 1.8 * i + (0.5 if row % 2 else 0)
            box('7E1A20', (x, y - 0.6, z + 1.0), (1.3, 0.2, 1.6), r, rough=1.0)                       # seat back
            if row == 0 and i == 4:
                S['seat'] = (x, y, z)
                continue
            m = empty((x, y, z), r)
            c = ('2E2E38', '4A3A34', '3A4250', '5A4A44', '34303A', '5E2E32', '2E4038')[n % 7]
            add('cone', c, (0, 0, 1.25), radius1=0.52, radius2=0.34, depth=1.5, vertices=6, parent=m, rough=1.0)
            skin = ('E6BE9E', 'D8A884', 'EAC8AA', 'C89878')[n % 4]
            add('ico_sphere', skin, (0, 0, 2.28), scale=(0.92, 1, 1.08), radius=0.28, subdivisions=1, parent=m)
            if n % 3 == 0:                                                                            # bowler
                add('ico_sphere', '1E1C22', (0, 0, 2.5), scale=(1, 1, 0.7), radius=0.29, subdivisions=1, parent=m)
                cyl('1E1C22', (0, 0, 2.45), 0.4, 0.04, m, v=10)
            elif n % 3 == 1:                                                                          # a wide hat with a ribbon
                cyl(('6A2E3A', '3A4A5A', '5A4A2E')[n % 3], (0, 0, 2.52), 0.55, 0.06, m, v=10)
                cyl('FF7A1A' if n % 5 == 1 else 'D8CEB8', (0, 0, 2.6), 0.26, 0.14, m, v=8)
            else:
                add('ico_sphere', ('3A2A22', '6A5A4A', '8A8480')[n % 3], (0, 0.05, 2.36), radius=0.29, subdivisions=1, parent=m)
            for sx in (-1, 1):                                                                        # eyes
                box('15151A', (sx * 0.1, 0.265, 2.31), (0.05, 0.03, 0.06), m)
            hands = [box(skin, (sx * 0.14, 0.5, 1.7), (0.12, 0.1, 0.2), m) for sx in (-1, 1)]
            S['crowd'].append((m, hands, rnd(n, 25) * 6.28, (x, y, z)))
            n += 1
    tg = empty((0, 5, 3.0), r)
    S['spot'] = light(at(THE, 0, -7, 9.5), 5200, 'FFF0D8', kind='SPOT', spot=0.5, target=tg)
    for i in range(3):
        light(at(THE, -4.5 + 4.5 * i, 1.6, 1.7), 260, 'FFB868', size=1.6, target=tg)
    tg2 = empty((0, -5, 1), r)
    S['house'] = light(at(THE, 0, 0.4, 5.5), 0, 'FFC890', size=6.0, target=tg2)
    S['theatre'] = r


# ---------------------------------------------------------------- the cast
def make_cast(S):
    S['rook'] = K.Rig(ROOKC, K.rook_head, coat=True)
    old = dict(skin='E0B090', hair='B4B0A8', bald=True, tache='B4B0A8')
    S['capt'] = cp = K.Rig(dict(top=BLUE, pants='1E2440', hand='ECECEC', boot='15151A', fore=BLUE), face(**old))
    tunic(cp, epaulette=STEEL)
    cp.cap = make_cap(cp.head, (0, 0, 0.24))
    for a, b in (((-0.42, 0.05, 0.12), (-0.62, 0.3, -0.95)),):                                        # a sabre at his side
        o = cyl(STEEL, (0, 0, 0), 0.5, 1, cp.body, v=5, rough=0.25)
        d = Vector(b) - Vector(a)
        o.location = (Vector(a) + Vector(b)) / 2
        o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        o.scale = (0.06, 0.06, d.length)
    cyl(BRASS, (-0.42, 0.04, 0.16), 0.07, 0.16, cp.body, v=6, rough=0.3)
    S['voigt'] = vg = K.Rig(dict(top='5E5246', pants='3E3A3C', hand='E0B090', boot='2A2420', fore='5E5246'), face(**old))
    box('3E3630', (0, -0.02, 1.15), (0.4, 0.36, 0.08), vg.body)
    S['apron'] = [box('8E7C5A', (0, -0.345, 0.32), (0.56, 0.04, 0.95), vg.body, rough=1.0), box('8E7C5A', (0, -0.36, 0.86), (0.36, 0.04, 0.3), vg.body, rough=1.0)]
    S['mayor'] = my = K.Rig(dict(top='26262E', pants='2E2E36', hand='E8BE9C', boot='15151A', fore='26262E'),
                            face('E8BE9C', '4E4038', beard='4E4038', tache='4E4038', glasses=True))
    box('ECE6DA', (0, -0.33, 0.78), (0.24, 0.05, 0.6), my.body)                                       # shirt front
    box('15151A', (0, -0.36, 1.02), (0.2, 0.05, 0.08), my.body)                                       # bow tie
    add('torus', BRASS, (0, -0.33, 0.72), rot=(PI / 2 - 0.12, 0, 0), major_radius=0.3, minor_radius=0.025, major_segments=12, minor_segments=4,
        parent=my.body, rough=0.3)                                                                    # a plain chain of office
    S['treas'] = tr = K.Rig(dict(top='6E6A5C', pants='3E3C3A', hand='E2B696', boot='2A2420', fore='E8E2D4'),
                            face('E2B696', '9A968E', bald=True, glasses=True))
    box('2A2A30', (0, -0.33, 0.6), (0.4, 0.05, 0.9), tr.body)                                         # waistcoat
    S['kaiser'] = ks = K.Rig(dict(top='C4CCD8', pants='2A3050', hand='ECECEC', boot='15151A', fore='C4CCD8'),
                             face('E6BC9C', '5E4C3A', tache='5E4C3A', curl=True))
    tunic(ks, col='C4CCD8', collar=RED, belt=None, epaulette=BRASS, sash='FF7A1A')
    S['sol'] = []
    for i in range(10):
        skin = ('E6BE9E', 'D8A884', 'EAC8AA')[i % 3]
        rg = K.Rig(dict(top=BLUE, pants='3A4058', hand=skin, boot='15151A', fore=BLUE),
                   face(skin, ('3A2A22', '6A4A2E', '8A6A3A')[i % 3], tache=('3A2A22' if i % 4 == 0 else None), hat=spiked('15151A', BRASS)))
        tunic(rg, buttons=5)
        S['sol'].append(dict(rig=rg, rifle=make_rifle()))
    S['pol'] = []
    for i in range(2):
        rg = K.Rig(dict(top='1E3034', pants='1C2428', hand='E2B696', boot='15151A', fore='1E3034'),
                   face('E2B696', '3A2A22', tache='3A2A22', hat=spiked('1C2428', STEEL)))
        tunic(rg, col='1E3034', collar='1C2428', belt='15151A', buttons=5)
        S['pol'].append(rg)
    S['humans'] = [cp, vg, my, tr, ks] + [d['rig'] for d in S['sol']] + S['pol']
    S['cast_all'] = [S['rook']] + S['humans']


def make_props(S):
    S['frifle'] = [make_rifle(), make_rifle()]
    make_money(S)
    S['glove'] = K.Hand('ECECEC', BLUE, 1.1)
    S['thand'] = K.Hand('E2B696', 'E8E2D4', 1.1)
    for h in (S['glove'], S['thand']):
        h.root.location = FAR
        keep(h.root)
    S['hammer'] = r = keep(empty(FAR))
    cyl('6A4A2E', (0, 0, 0.22), 0.03, 0.5, r, v=6)
    box('3A3E46', (0, -0.04, 0.48), (0.09, 0.26, 0.1), r, rough=0.4)
    S['bootb'] = make_boot('3A2A20', 1.15)
    S['boot2'] = make_boot('A8743E', 1.25)
    S['mag'] = r = keep(empty(FAR))
    add('torus', BRASS, (0, 0, 0), rot=(PI / 2, 0, 0), major_radius=0.22, minor_radius=0.03, major_segments=14, minor_segments=4, parent=r, rough=0.3)
    cyl('D8F0FF', (0, 0, 0), 0.21, 0.01, r, rot=(PI / 2, 0, 0), v=14, rough=0.05, alpha=0.25)
    cyl('3A2A1E', (0, 0, -0.42), 0.035, 0.42, r, v=6)
    S['button'] = keep(cyl(BRASS, FAR, 0.09, 0.035, None, rot=(PI / 2, 0, 0), v=8, rough=0.15, emit=0.5))
    S['paper'] = r = keep(empty(FAR))
    box('E8E0CC', (0, 0, 0), (1.5, 0.03, 1.05), r)
    for j in range(5):
        box('3A3A40', (-0.38, -0.02, 0.36 - 0.17 * j), (0.6, 0.012, 0.035), r)
        box('3A3A40', (0.38, -0.02, 0.36 - 0.17 * j), (0.6, 0.012, 0.035), r)
    S['stamp'] = r = keep(empty(FAR))
    cyl(WOODD, (0, 0, 0.2), 0.06, 0.3, r, v=6)
    cyl(BRASS, (0, 0, 0.04), 0.12, 0.08, r, v=8, rough=0.3)
    S['pardon'] = keep(box('F2ECD8', FAR, (0.8, 1.05, 0.015), None))
    S['flowers'] = []
    for i in range(5):
        r = keep(empty(FAR))
        cyl('3E6A3A', (0, 0, 0.2), 0.02, 0.4, r, v=5)
        add('ico_sphere', ('E84A4A', 'FF7A1A', 'F2D048', 'E86A9A', 'F2F0E8')[i], (0, 0, 0.44), radius=0.11, subdivisions=1, parent=r, emit=0.6)
        S['flowers'].append(r)
    S['glint'] = light(FAR, 0, 'FFF4E0', kind='POINT')


def build():
    sc = bpy.context.scene
    _KEEP.clear()
    _PROTO.clear()
    _LAST[0] = None
    K.add, K.empty = add, empty
    S = {}
    for fn in (make_office, make_treasury, make_square, make_street, make_alley, make_cobbler, make_shop, make_cell, make_palace,
               make_theatre, make_cast, make_props):
        fn(S)
    S['suntgt'] = empty()
    S['sun'] = light((0, 0, 100), 0.0, 'FFFFFF', kind='SUN', target=S['suntgt'])
    S['sun'].data.angle = 0.08
    tgt, rigc = empty(), empty()
    con = rigc.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_ = bpy.context.object
    cam_.parent = rigc
    cam_.data.clip_start, cam_.data.clip_end = 0.05, 4000
    sc.camera = cam_
    S.update(cam=cam_, camrig=rigc, camtgt=tgt)
    w = bpy.data.worlds.new('w43')
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    S['bg'] = nt.nodes['Background']
    tc, sep, mr, mx = (nt.nodes.new(n) for n in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeMapRange', 'ShaderNodeMix'))
    mx.data_type = 'RGBA'
    mr.inputs[1].default_value, mr.inputs[2].default_value = -0.05, 0.6
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
    c = S['capt'].cap
    c.location, c.rotation_euler = (0, 0, 0.24), (0, 0, 0)
    for o in S['apron']:
        o.hide_render = False
    S['sun'].data.energy = 0
    S['glint'].data.energy = 0
    S['glint'].location = FAR
    S['house'].data.energy = 0
    S['spot'].data.energy = 5200
    S['cashlid'].rotation_euler = (0, 0, 0)
    S.update(rface='calm', hat_tip=0.0, hat_jump=0.0, laugh=0.0)
    S['cam'].rotation_euler = (0, 0, 0)


def finish(S, t):
    """Faces, blinks and Rook's beak, after the shot has posed everyone."""
    r = S['rook'].extra
    e = S['rface']
    blink = (t * 0.41) % 1 < 0.035
    lg = S['laugh']
    ez = dict(calm=0.07, low=0.04, shocked=0.135, soft=0.06, laugh=0.02, squint=0.034).get(e, 0.07)
    tilt = dict(low=-0.06, shocked=0.36, soft=0.22, laugh=0.3, squint=-0.3).get(e, -0.22)
    if lg > 0.3:
        ez, tilt = 0.02, 0.3
    for i, s in enumerate((-1, 1)):
        r['eyes'][i].scale = (0.15, 0.03, 0.008 if blink else ez)
        r['brows'][i].rotation_euler = (0.25, s * 0.5 + s * tilt, s * -0.25)
        r['brows'][i].location.z = 0.135 + (0.07 if e == 'shocked' else 0.0)
    tip = S['hat_tip']
    r['hat'].rotation_euler = (-0.2 + tip * 0.38, 0.07, 0)
    r['hat'].location = (0, 0, 0.27 + S['hat_jump'] + tip * 0.1)
    talk = S['beak']
    r['jaw'].rotation_euler = (talk * 0.17 + (0.36 if e == 'shocked' else 0.0) + lg * (0.42 + 0.16 * math.sin(t * 26)), 0, 0)
    hd = S['rook'].head.rotation_euler
    S['rook'].head.rotation_euler = (hd[0] + (0.03 * math.sin(t * 7) if talk > 0.2 else 0) + lg * 0.12 * math.sin(t * 26), hd[1],
                                     hd[2] + (0.03 * math.sin(t * 3.1) if talk > 0.2 else 0))
    for j, rig in enumerate(S['humans']):
        x = rig.extra
        f = rig.face
        k = dict(calm=1.0, wide=1.8, tired=0.45, warm=0.75, sad=0.55, hard=0.6).get(f, 1.0)
        bl = (t * 0.31 + 0.23 * j + 0.5) % 1 < 0.03
        for ey in x['eyes']:
            ey.scale = (0.1, 0.03, 0.075 * (0.1 if bl else k))
        for i, br in enumerate(x['brows']):
            s = (-1, 1)[i]
            br.location.z = 0.125 + (0.05 if f == 'wide' else -0.022 if f in ('hard', 'tired') else 0.0)
            br.rotation_euler = (0, s * 0.12 + (s * 0.34 if f in ('sad', 'wide') else s * -0.42 if f == 'hard' else 0.0), 0)
        x['mouth'].scale = (0.2 if f == 'warm' else 0.13, 0.03, 0.035 + 0.15 * rig.jawv + (0.05 if f == 'wide' else 0))
        x['mouth'].location.z = -0.02 - 0.05 * rig.jawv


# ---------------------------------------------------------------- helpers for the shots
def amb(S, name):
    A = AMB[name]
    S['skymix'].inputs[6].default_value = K.hexc(A[0])
    S['skymix'].inputs[7].default_value = K.hexc(A[1])
    S['bg'].inputs[1].default_value = A[2]
    S['sun'].data.energy = A[3]
    S['sun'].data.color = K.hexc(A[4])[:3]
    S['suntgt'].location = (0, 0, 0)
    S['sun'].location = tuple(v * 500 for v in A[5])


def cam(S, pos, look, lens=35):
    S['camrig'].location, S['camtgt'].location = pos, look
    S['cam'].data.lens = lens


def orbit(S, k, yaw=20.0, push=0.15, rise=0.0):
    """A real camera move on top of a framing: swing round the look-at point by `yaw` degrees across the shot, close in
    by `push` of the distance, rise by `rise`. It is zero at the middle of the shot, so framings are written for k = 0.5."""
    c, tg = S['camrig'].location, S['camtgt'].location
    a = math.radians(yaw) * (k - 0.5)
    dx, dy = c[0] - tg[0], c[1] - tg[1]
    m = 1.0 + push * (0.5 - k)
    S['camrig'].location = (tg[0] + (dx * math.cos(a) - dy * math.sin(a)) * m, tg[1] + (dx * math.sin(a) + dy * math.cos(a)) * m,
                            tg[2] + (c[2] - tg[2]) * m + rise * (k - 0.5))


def stand(rig, loc, yaw=0.0, pose=None, face_=None, jaw=None):
    rig.place(loc, yaw)
    rig.apply(pose or P())
    if face_:
        rig.face = face_
    if jaw is not None:
        rig.jawv = jaw
    return rig


def head(rig):
    return wpos(rig.head)


def hand(rig, i=1):
    return wpos(rig.el[i], (0, -0.06, -0.6))


def step(t, speed=1.6, **over):
    p = K.walk(t, speed)
    p.update(over)
    for a in ('aL', 'aR'):
        p[a] = tuple(p[a]) + (0.0,) * (4 - len(p[a]))
    return p


def chat(t, on=True):
    return (0.45 + 0.45 * math.sin(t * 19)) if on else 0.0


ARMS = dict(attn=dict(aR=(0.0, 0.16, 0.3)), slope=dict(aR=(0.55, 0.0, 1.35, 0.2)), aim=dict(aR=(0.9, 0.1, 1.5, 0.5), aL=(1.35, -0.35, 0.3)),
            sling=dict())
GUN = dict(attn=((0.6, -0.08, 0.02), (0.62, -0.1, 2.6)), slope=((0.5, -0.34, 1.18), (0.4, 0.42, 3.5)), aim=((0.42, 0.25, 1.78), (0.16, -2.2, 1.98)),
           sling=((0.3, 0.36, 0.7), (-0.3, 0.36, 3.1)))


def soldier(S, i, loc, yaw, mode='attn', t=0.0, walking=False, face_='hard', **over):
    """Pose soldier i with his rifle: attn (order arms), slope (on the shoulder), aim (bayonet levelled), sling."""
    d = S['sol'][i]
    arms = dict(ARMS[mode])
    arms.update(over)
    pose = step(t + 0.13 * i, 1.7, **arms) if walking else P('stand', **arms)
    stand(d['rig'], loc, yaw, pose, face_)
    a, b = GUN[mode]
    bob = (0, 0, 0.03 * math.sin((t + 0.13 * i) * 1.7 * 4 * PI) if walking else 0.0)
    lay(d['rifle'], plus(off(loc, yaw, a), bob), plus(off(loc, yaw, b), bob))
    return d['rig']


def cap_to(rig, world, tilt=0.0):
    """Hold the captain's cap at a world point (it is parented to his head)."""
    bpy.context.view_layer.update()
    rig.cap.location = rig.head.matrix_world.inverted() @ Vector(world)
    rig.cap.rotation_euler = (tilt, 0, 0)


def cap_top(rig):
    return wpos(rig.head, (0, 0, 0.24))


# ---------------------------------------------------------------- the town hall, from the inside
def office_burst(S, k, t, lt):
    """The hook, and (prm loop) the way back into it. The mayor at his desk looks up, bayonets come in round the lens,
    he jumps to his feet with his hands up. With loop: he is writing, the camera closes in, he looks up, and the
    bayonet tips arrive at the frame edges: the last frame is the first frame of the hook."""
    amb(S, 'office')
    loop = S['prm'].get('loop')
    my = S['mayor']
    writing = P('sit', aR=(0.95, -0.2, 1.3, 0.3), aL=(0.8, -0.15, 1.4, 0.6), head=(0.55, 0.0), lean=0.3)
    looked = P('sit', aR=(0.9, 0.25, 1.25), aL=(0.9, 0.25, 1.25), head=(-0.05, 0.0), lean=0.12)
    if loop:
        up = 0.0
        scratch = 0.05 * math.sin(lt * 14) * (1 - sm((k - 0.6) / 0.1))
        pose = blend(dict(writing, aR=(0.95 + scratch, -0.2, 1.3, 0.3)), looked, (k - 0.7) / 0.26)
        fc = 'wide' if k > 0.84 else 'calm'
        cp = mix((1.1, -5.3, 3.5), (0.0, -3.4, 2.3), sm(k / 0.9))
        slide = [1.2 * (1 - sm((k - 0.8) / 0.2))] * 2
        thrust = [0.0, 0.0]
        show = k > 0.8
    else:
        up = sm((k - 0.1) / 0.22)
        pose = blend(looked, P('up', lean=-0.12, head=(-0.12, 0.0), aL=(2.7 + 0.05 * math.sin(lt * 31), 0.3, 0.2), aR=(2.7 + 0.05 * math.sin(lt * 29), 0.3, 0.2)), up)
        fc = 'wide'
        cp = (0.0, lerp(-3.4, -3.0, sm(k)), 2.3)
        slide = [0.0, 0.0]
        thrust = [sm(k / 0.2), sm((k - 0.06) / 0.2)]
        show = True
    stand(my, at(OFF, 0, 2.3, 0), 0, pose, fc, jaw=0.7 * up)
    for j, s in enumerate((1, -1)):
        if not show:
            continue
        tip = mix((s * (0.66 + slide[j]), -1.75, 1.95), (s * 0.5, -0.05 + 0.03 * math.sin(lt * 23 + j), 2.12 + 0.2 * up), thrust[j])
        lay(S['frifle'][j], at(OFF, tip[0] + s * 0.44, tip[1] - 2.42, tip[2] - 0.4), at(OFF, *tip))
    cam(S, at(OFF, *cp), at(OFF, 0, 1.9, lerp(2.0, 2.45, up)), 28)


def boots_in(S, k, t, lt):
    """Low by the floor: the captain strides in through the double doors, six soldiers at his back, bayonets levelled."""
    amb(S, 'office')
    cy = lerp(-4.6, -2.0, sm(k))
    cp = S['capt']
    stand(cp, at(OFF, 0, cy, 0), PI, step(t, 1.8, head=(-0.1, 0.0)) if k < 0.9 else P('stand', head=(-0.1, 0.0)), 'hard')
    for i in range(6):
        soldier(S, i, at(OFF, (-1.3, 1.3)[i % 2], cy - 1.5 - 1.7 * (i // 2), 0), PI, 'slope', t, walking=k < 0.9)
    cam(S, at(OFF, 3.1, -0.9, 0.5), at(OFF, 0.0, -3.6, 1.9), 22)
    orbit(S, k, 16, 0.25, 0.3)


def captain_point(S, k, t, lt):
    """From the desk, looking up: the captain stops, throws out his arm and points; two bayonets flank him."""
    amb(S, 'office')
    cp = S['capt']
    u = sm((k - 0.08) / 0.22)
    stand(cp, at(OFF, 0, -2.0, 0), PI, blend(P('stand', head=(-0.1, 0.0)), P('point', aR=(1.5, 0.05, 0.05), head=(-0.05, 0.0), lean=-0.06), u), 'hard',
          jaw=chat(t, 0.25 < k < 0.85))
    for i, (x, y) in enumerate(((-2.0, -3.2), (2.0, -3.2), (-1.2, -4.9), (1.2, -4.9))):
        soldier(S, i, at(OFF, x, y, 0), PI, 'aim', t)
    cam(S, at(OFF, 1.15, 0.3, 1.6), at(OFF, 0.0, -2.0, 2.45), 30)
    orbit(S, k, 22, 0.25, 0.0)


def mayor_up(S, k, t, lt):
    """The mayor on his feet behind the desk with his hands up, shaking; two soldiers come round the desk and take his arms."""
    amb(S, 'office')
    my = S['mayor']
    mp = at(OFF, 0, 2.45, 0)
    sh = 0.05 * math.sin(lt * 30)
    u = sm(k / 0.6)
    stand(my, mp, 0, blend(P('up', aL=(2.7 + sh, 0.3, 0.2), aR=(2.7 - sh, 0.3, 0.2), head=(-0.1, 0.25 * math.sin(lt * 5))),
                           P('stand', aL=(0.2, 0.5, 0.3), aR=(0.2, 0.5, 0.3), head=(0.2, 0.0)), (k - 0.62) / 0.3), 'wide', jaw=0.5)
    for i, s in enumerate((-1, 1)):
        p = mix(at(OFF, s * 3.6, -0.8, 0), at(OFF, s * 1.2, 2.55, 0), u)
        soldier(S, i, p, facing(p, mp), 'sling', t, walking=u < 0.98, aR=(1.25, -0.25, 0.5) if u > 0.9 and s < 0 else (0.05, 0.12, 0.15),
                aL=(1.25, -0.25, 0.5) if u > 0.9 and s > 0 else (0.05, 0.12, 0.15))
    stand(S['capt'], at(OFF, 0.3, -2.2, 0), PI, P('point', aR=(1.45, 0.1, 0.05)), 'hard')
    cam(S, at(OFF, -4.9, -3.7, 3.0), at(OFF, 0.2, 1.7, 2.3), 30)
    orbit(S, k, 24, 0.25, 0.0)


def rook_desk(S, k, t, lt):
    """Rook, already there: sitting on the front of the mayor's desk, arms crossed, brim low, the arrest going on
    behind him. "Arrested for what, exactly?" He glances back at them on the last word."""
    amb(S, 'office')
    rk = S['rook']
    turn = lerp(0.2, -0.45, sm((k - 0.55) / 0.25))
    stand(rk, at(OFF, -1.35, -0.2, 0.76), 0.15, P('sit', aL=(0.5, -0.05, 1.7, 1.3), aR=(0.42, -0.05, 1.8, 1.3), lean=0.0, head=(0.05, turn)))
    S['rface'] = 'low'
    S['hat_tip'] = 0.55
    mp = at(OFF, 0.9, 2.5, 0)
    stand(S['mayor'], mp, 0, P('stand', aL=(0.2, 0.5, 0.3), aR=(0.2, 0.5, 0.3), head=(0.25, 0.15 * math.sin(lt * 4))), 'wide')
    for i, s in enumerate((-1, 1)):
        p = plus(mp, (s * 1.2, 0.1, 0))
        soldier(S, i, p, facing(p, mp), 'sling', t, **{('aR' if s < 0 else 'aL'): (1.25, -0.25, 0.5)})
    cam(S, at(OFF, -1.0, -3.5, 2.3), at(OFF, -0.55, 0.6, 2.2), 30)
    orbit(S, k, 18, 0.2, 0.0)


# ---------------------------------------------------------------- the treasury
def table_money(S, gone=0.0, order=None):
    """Lay the cash out on the counting table; items whose turn has come arc into the captain's bag and are gone."""
    items = []
    for i, n in enumerate(S['notes']):
        items.append((n, (-0.9 + 0.62 * (i % 3), 0.05 - 0.48 * (i // 3), 1.275)))
    for i, c in enumerate(S['coins']):
        items.append((c, (-1.4 + 0.42 * i, -0.95, 1.275)))
    for i, s in enumerate(S['sacks']):
        items.append((s, (1.2 + 0.55 * i, -0.75 + 0.2 * (i % 2), 1.275)))
    bagp = (-2.05, -0.75, 1.275)
    S['bag'].location = at(TRE, *bagp)
    S['bag'].rotation_euler = (0, 0, 0.25)
    cur = None
    for j, (o, p) in enumerate(items):
        if j >= 13:
            o.location = at(TRE, *p)
            continue
        jj = j - 6 if j >= 6 else j + 7                                   # coins first, then the notes
        k0 = 0.04 + 0.84 * jj / 13
        u = (gone - k0) / 0.12
        if u >= 1:
            continue
        if u <= 0:
            o.location = at(TRE, *p)
            continue
        q = mix(p, (bagp[0], bagp[1], 1.9), sm(u))
        o.location = at(TRE, q[0], q[1], q[2] + 0.5 * math.sin(PI * u))
        cur = o.location
    return cur


def treasurer(S, k, t, lt):
    """Over the captain's shoulder: the treasurer, shaking, lifts the cash box out of the safe's shadow and sets it on
    the table in front of the outstretched glove."""
    amb(S, 'vault')
    tr = S['treas']
    u = sm((k - 0.3) / 0.4)
    sh = 0.04 * math.sin(lt * 33)
    tp = at(TRE, 1.3, 1.55, 0)
    stand(tr, tp, 0.1, P('stand', aL=(1.1 + sh, -0.2, lerp(1.0, 0.5, u)), aR=(1.1 - sh, -0.2, lerp(1.0, 0.5, u)), lean=lerp(0.05, 0.42, u), head=(0.15, -0.2 + 0.3 * u)),
          'wide', jaw=0.4)
    S['cashbox'].location = mix(at(TRE, 1.3, 0.85, 1.8), at(TRE, 1.15, 0.2, 1.275), u)
    S['cashbox'].location.z += 0.02 * math.sin(lt * 33) * (1 - u)
    table_money(S, 0.0)
    cp = S['capt']
    stand(cp, at(TRE, 0.3, -3.0, 0), PI - 0.2, P('stand', aL=(1.1, 0.2, 0.25), head=(-0.05, 0.0)), 'hard')
    soldier(S, 0, at(TRE, 3.6, -0.6, 0), facing((3.6, -0.6), (1.3, 1.55)), 'aim', t)
    cam(S, at(TRE, 1.5, -6.2, 3.0), at(TRE, 0.6, 0.8, 2.0), 32)
    orbit(S, k, 18, 0.2, 0.0)


def cash(S, k, t, lt):
    """Down on the table: note bundles, coin stacks and sacks, and a white glove sweeping them, one after another,
    into a leather bag; the treasurer's hand trembles on the open cash box."""
    amb(S, 'vault')
    S['cashbox'].location = at(TRE, 0.75, 0.75, 1.275)
    S['cashlid'].rotation_euler = (-1.9, 0, 0)
    cur = table_money(S, k)
    g = S['glove']
    rest = at(TRE, -0.6, -1.5, 1.6)
    gp = plus(cur, (0.05, -0.42, 0.14)) if cur else rest
    g.place(gp, (0.2, 0, PI))
    g.grip(0.55 if cur else 0.2)
    th = S['thand']
    th.place(at(TRE, 0.75 + 0.02 * math.sin(lt * 31), 1.45, 1.75 + 0.02 * math.sin(lt * 37)), (0.3, 0, 0.1))
    th.grip(0.3)
    cam(S, at(TRE, -0.6, -2.7, 3.5), at(TRE, -0.6, -0.3, 1.3), 26)
    orbit(S, k, 22, 0.2, 0.0)


def rook_coins(S, k, t, lt):
    """Rook at the end of the table, eyes wide at a stack of gold: his hand creeps out; a bayonet drops across his
    beak; he pulls the hand back, palms up, brim down."""
    amb(S, 'vault')
    S['cashbox'].location = at(TRE, 1.15, 0.3, 1.275)
    S['cashlid'].rotation_euler = (-1.9, 0, 0)
    for i, c in enumerate(S['coins'][:4]):
        c.location = at(TRE, 2.25 - 0.3 * (i % 2), -0.5 + 0.3 * (i // 2), 1.275)
    for i, n in enumerate(S['notes'][:3]):
        n.location = at(TRE, 0.2 + 0.6 * i, -0.6, 1.275)
    rk = S['rook']
    reach = sm(k / 0.32)
    back = sm((k - 0.5) / 0.14)
    pose = blend(P('stand', lean=0.1, head=(0.2, 0.0)), P('stand', aR=(1.25, 0.0, 0.3), lean=0.42, head=(0.1, 0.0)), reach)
    if back > 0:
        pose = blend(pose, P('shrug', lean=-0.1, head=(-0.05, 0.3)), back)
    rp = at(TRE, 3.55, -0.3, 0)
    stand(rk, rp, -PI / 2, pose)
    S['rface'] = 'shocked' if back < 0.5 and reach > 0.3 else 'low'
    S['hat_tip'] = 0.6 * back
    sp = at(TRE, 2.5, 1.75, 0)
    soldier(S, 0, sp, 0.0, 'slope', t, face_='hard')
    drop = sm((k - 0.4) / 0.08)
    a0, b0 = (off(sp, 0, v) for v in GUN['slope'])
    lay(S['sol'][0]['rifle'], mix(a0, at(TRE, 2.75, 1.1, 1.95), drop), mix(b0, at(TRE, 2.62, -1.35, 1.72), drop))
    if drop > 0:
        S['sol'][0]['rig'].apply(blend(P('stand', **ARMS['slope']), P('stand', aR=(1.2, 0.0, 0.5), aL=(1.3, -0.3, 0.4)), drop))
    cam(S, at(TRE, 0.5, -3.8, 2.3), at(TRE, 2.9, -0.2, 2.0), 32)
    orbit(S, k, 16, 0.2, 0.0)


# ---------------------------------------------------------------- outside the town hall
def line_up(S, k, t, lt):
    """In the square: six soldiers in a row, rifles grounded; the captain walks down the line with his hands behind
    his back, and each man stiffens and lifts his chin as he passes."""
    amb(S, 'square')
    cx = lerp(9.0, -4.0, k)
    cp = S['capt']
    stand(cp, at(EXT, cx, 0.5, 0), -PI / 2, step(t, 1.5, aL=(-0.5, 0.1, 0.9, 1.2), aR=(-0.5, 0.1, 0.9, 1.2), head=(-0.1, -0.5), lean=-0.03), 'hard')
    for i in range(6):
        sx = -3.0 + 2.0 * i
        sn = sm(((sx + 1.2) - cx) / 0.5)
        pulse = sn * (1 - sm((sx - 0.4 - cx) / 0.8))
        soldier(S, i, at(EXT, sx, 2.4, 0.08 * pulse), 0.0, 'attn', t, head=(-0.22 * sn, 0.0), lean=-0.05 * sn)
    cam(S, at(EXT, -6.2, -2.4, 1.8), at(EXT, 3.6, 2.2, 2.4), 30)
    orbit(S, k, 14, 0.2, 0.0)


def mayor_march(S, k, t, lt):
    """Looking up from the foot of the steps: the mayor comes down between two soldiers, head bowed, hands behind him;
    two more stand rigid either side of the door."""
    amb(S, 'square')
    y = lerp(7.0, 3.3, k)
    z = stepz(y)
    stand(S['mayor'], at(EXT, 2, y, z), 0, step(t, 1.4, aL=(-0.4, 0.0, 0.8, 1.0), aR=(-0.4, 0.0, 0.8, 1.0), head=(0.42, 0.0)), 'sad')
    for i, s in enumerate((-1, 1)):
        soldier(S, i, at(EXT, 2 + s * 1.3, y + 0.25, stepz(y + 0.25)), 0.0, 'slope', t, walking=True)
        soldier(S, 2 + i, at(EXT, 2 + s * 2.9, 7.0, 0.6), 0.0, 'attn', t)
    cam(S, at(EXT, 3.7, -0.5, 0.9), at(EXT, 2.0, 5.0, 2.7), 26)
    orbit(S, k, 14, 0.2, 0.0)


def rook_peer(S, k, t, lt):
    """Rook leans in at the captain's shoulder and prods the silver epaulette with one finger, eyes narrowed; the
    captain stares straight ahead, then slides a look down at him."""
    amb(S, 'square')
    cp = S['capt']
    c0 = at(EXT, 5.0, 0.5, 0)
    look = sm((k - 0.5) / 0.2)
    stand(cp, c0, 0.0, P('stand', aL=(-0.45, 0.1, 0.9, 1.2), aR=(-0.45, 0.1, 0.9, 1.2), head=(lerp(-0.14, 0.12, look), -0.5 * look), lean=-0.05), 'hard')
    rk = S['rook']
    r0 = at(EXT, 6.3, 1.0, 0)
    prod = 0.12 * max(0.0, math.sin(lt * 9))
    stand(rk, r0, facing(r0, c0) - 0.25, P('stand', aR=(1.45 + prod, 0.25, 0.75 - prod), aL=(0.4, 0.1, 1.2, 1.0), lean=0.3, head=(0.0, 0.2)))
    S['rface'] = 'squint'
    S['hat_tip'] = 0.4
    for i in range(3):
        soldier(S, i, at(EXT, -1.5 + 2.0 * i, 3.4, 0), 0.0, 'attn', t)
    h = head(cp)
    cam(S, plus(h, (-0.2, -4.2, -0.2)), plus(h, (0.75, 0.0, -0.2)), 40)
    orbit(S, k, 20, 0.2, 0.0)


def walk_out(S, k, t, lt):
    """Wide on the town hall: the captain comes down the steps with a leather bag and walks off across the square,
    past soldiers who stay exactly where he left them."""
    amb(S, 'square')
    a, b = (2.0, 6.7), (6.6, -6.5)
    p = mix(a, b, k)
    cp = S['capt']
    stand(cp, at(EXT, p[0], p[1], stepz(p[1])), facing(a, b), step(t, 1.6, aL=(0.1, 0.12, 0.25), head=(-0.08, 0.0)), 'hard')
    S['bag'].location = plus(hand(cp, 0), (0, 0, -0.78))
    S['bag'].rotation_euler = (0, 0, facing(a, b) + PI / 2)
    for i, (x, y) in enumerate(((-0.6, 7.0), (4.6, 7.0), (-2.4, 3.6), (6.4, 3.6))):
        soldier(S, i, at(EXT, x, y, stepz(y) if abs(x - 2) < 4 else 0), 0.0, 'attn', t)
    cam(S, at(EXT, -2.5, -12.5, 1.7), at(EXT, 1.8, 4.0, 6.4), 24)
    orbit(S, k, 10, 0.12, 0.0)


def rook_gone(S, k, t, lt):
    """Rook on the steps between two soldiers who do not move: he looks left, looks right, and shrugs."""
    amb(S, 'square')
    rk = S['rook']
    sh = sm((k - 0.6) / 0.18)
    turn = 0.75 * math.sin(min(k, 0.6) / 0.6 * 2 * PI)
    stand(rk, at(EXT, 2.0, 5.8, 0.4), 0.0, blend(P('hips', head=(0.0, turn)), P('shrug', head=(-0.05, 0.0)), sh))
    S['rface'] = 'squint' if sh < 0.5 else 'low'
    S['hat_tip'] = 0.35 * sh
    for i, s in enumerate((-1, 1)):
        soldier(S, i, at(EXT, 2 + s * 2.4, 7.0, 0.6), 0.0, 'attn', t, head=(-0.15, 0.0))
    cam(S, at(EXT, 2.7, 0.2, 1.7), at(EXT, 2.0, 5.8, 2.95), 30)
    orbit(S, k, 18, 0.22, 0.0)


# ---------------------------------------------------------------- who he is
def cap_off(S, k, t, lt):
    """A back alley under a gas lamp: the captain glances over his shoulder, lifts off his cap: a bald old man with a
    grey moustache; he lets out his breath and almost smiles."""
    amb(S, 'alley')
    cp = S['capt']
    glance = 0.6 * math.sin(min(1.0, k / 0.3) * 2 * PI)
    grab = sm((k - 0.22) / 0.12)
    off_ = sm((k - 0.36) / 0.16)
    pose = blend(P('stand', head=(0.0, glance)), P('hat', head=(0.05, 0.0)), grab)
    if off_ > 0:
        pose = blend(pose, P('stand', aR=(0.35, 0.35, 0.7, 0.3), head=(0.08, 0.0), lean=0.06), off_)
    stand(cp, at(ALY, 0.0, 0.5, 0), 0.12, pose, 'hard' if k < 0.56 else 'warm')
    if off_ > 0:
        cap_to(cp, mix(cap_top(cp), plus(hand(cp, 1), (0.0, -0.12, 0.05)), off_), 0.6 * off_)
    h = head(cp)
    cam(S, plus(h, (0.8, -3.1, 0.0)), plus(h, (0.0, 0.0, -0.12)), 42)
    orbit(S, k, 22, 0.25, 0.0)


def cobbler(S, k, t, lt):
    """A bare room: the same old man in a leather apron on a stool at a cobbler's bench, hammering a sole on an iron
    last. He stops and looks up."""
    amb(S, 'room')
    vg = S['voigt']
    stop = sm((k - 0.72) / 0.12)
    sw = abs(math.sin(lt * 7.5)) * (1 - stop)
    stand(vg, at(COB, 0.0, 1.5, 0.0), 0.0, P('sit', aL=(0.95, -0.12, 1.0, 0.4), aR=(0.8 + 0.55 * sw, 0.05, 1.75 - 0.6 * sw, 0.2), lean=0.3,
                                             head=(lerp(0.4, -0.05, stop), 0.0)), 'tired' if stop < 0.5 else 'calm')
    hp = hand(vg, 1)
    S['hammer'].location = hp
    S['hammer'].rotation_euler = (-1.1 + 0.9 * sw, 0, 0)
    S['bootb'].location = at(COB, -0.1, 0.0, 1.62)
    S['bootb'].rotation_euler = (PI, 0, 0)
    cam(S, at(COB, -2.3, -3.2, 2.9), at(COB, 0.0, 0.9, 1.7), 32)
    orbit(S, k, 22, 0.25, 0.0)


def rook_shoe(S, k, t, lt):
    """Rook holds one of the old man's boots up by the heel, looks from it to us, and his beak drops and his hat hops."""
    amb(S, 'room')
    vg = S['voigt']
    sw = abs(math.sin(lt * 7.5))
    stand(vg, at(COB, 0.0, 1.5, 0.0), 0.0, P('sit', aL=(0.95, -0.12, 1.0, 0.4), aR=(0.8 + 0.55 * sw, 0.05, 1.75 - 0.6 * sw, 0.2), lean=0.3, head=(0.4, 0.0)), 'tired')
    S['hammer'].location = hand(vg, 1)
    S['hammer'].rotation_euler = (-1.1 + 0.9 * sw, 0, 0)
    S['bootb'].location = at(COB, -0.1, 0.0, 1.62)
    S['bootb'].rotation_euler = (PI, 0, 0)
    rk = S['rook']
    shock = sm((k - 0.35) / 0.14)
    stand(rk, at(COB, 2.2, -1.0, 0), -0.3, blend(P('stand', aR=(1.35, 1.0, 0.6, 0.0), head=(0.0, -0.5)),
                                                P('stand', aR=(1.25, 1.1, 0.5, 0.0), aL=(0.4, 0.5, 0.4), lean=-0.14, head=(-0.08, 0.0)), shock))
    S['boot2'].location = plus(hand(rk, 1), (0.0, 0.0, 0.0))
    S['boot2'].rotation_euler = (0.3, 0.2, 1.2)
    S['rface'] = 'shocked' if shock > 0.4 else 'squint'
    S['hat_jump'] = 0.65 * shock * (1 - sm((k - 0.8) / 0.18))
    h = head(rk)
    cam(S, plus(h, (-1.2, -4.6, -0.1)), plus(h, (0.1, 0.0, -0.3)), 32)
    orbit(S, k, 18, 0.22, 0.0)


# ---------------------------------------------------------------- how he did it
def shop(S, k, t, lt):
    """A second-hand shop: the old man in a shabby coat, chin in hand, in front of a tailor's dummy wearing a
    captain's tunic and cap. He nods and points: that one."""
    amb(S, 'room')
    vg = S['voigt']
    for o in S['apron']:
        o.hide_render = True
    v0 = at(SHP, 1.0, -0.5, 0)
    d0 = at(SHP, -1.3, 1.6, 0)
    u = sm((k - 0.55) / 0.2)
    stand(vg, v0, facing(v0, d0), blend(P('think', head=(0.1 + 0.08 * math.sin(lt * 3), 0.1)), P('point', aR=(1.25, 0.0, 0.2), head=(0.12 * math.sin(lt * 12) * u, 0.0)), u),
          'calm' if u < 0.5 else 'warm')
    cam(S, at(SHP, -3.84, 1.75, 2.6), at(SHP, 0.6, -0.3, 2.25), 27)
    orbit(S, k, 8, 0.2, 0.0)


def rook_mag(S, k, t, lt):
    """Rook goes over the tunic's brass buttons with his magnifying glass, then straightens and taps his beak."""
    amb(S, 'room')
    rk = S['rook']
    r0 = at(SHP, 0.15, 1.35, 0)
    tap = sm((k - 0.62) / 0.16)
    scan = 0.25 * math.sin(lt * 3.2)
    stand(rk, r0, -PI / 2 + 0.2, blend(P('stand', aR=(1.2 + scan, 0.05, 0.5), aL=(0.3, 0.1, 0.9, 0.8), lean=0.36, head=(0.12, 0.0)),
                                      P('tap', lean=0.05, aR=(1.25, -0.25, 2.2 + 0.12 * math.sin(lt * 14), 0.6)), tap))
    hp = hand(rk, 1)
    S['mag'].location = plus(hp, (-0.12, 0.0, 0.3)) if tap < 0.5 else plus(hand(rk, 0), (-0.1, 0, 0.3))
    S['mag'].rotation_euler = (0, 0, PI / 2 + 0.2)
    S['rface'] = 'squint'
    S['hat_tip'] = 0.3
    S['glint'].location = at(SHP, -1.5, 0.7, 2.0 + scan)
    S['glint'].data.energy = 60 * (1 - tap)
    cam(S, at(SHP, -2.5, -2.3, 2.25), at(SHP, -0.55, 1.35, 2.05), 38)
    orbit(S, k, 20, 0.22, 0.0)


def dress(S, k, t, lt):
    """By the mirror: he does up the last button of the tunic, sets the cap on his head, and draws himself up: a captain."""
    amb(S, 'room')
    cp = S['capt']
    on = sm((k - 0.38) / 0.24)
    tall = sm((k - 0.68) / 0.18)
    fid = 0.06 * math.sin(lt * 12) * (1 - on)
    pose = blend(P('stand', aR=(0.85 + fid, -0.3, 1.95, 0.6), aL=(0.1, 0.25, 0.3), head=(0.32, 0.0), lean=0.1),
                 P('stand', aR=(0.3, 0.1, 0.3), aL=(0.2, 1.9, 1.6, -1.5), head=(0.1, 0.0)), on)
    if tall > 0:
        pose = blend(pose, P('stand', aL=(0.0, 0.14, 0.1), aR=(0.0, 0.14, 0.1), head=(-0.14, 0.0), lean=-0.08), tall)
    stand(cp, at(SHP, 1.0, 0.9, 0), 0.25, pose, 'calm' if tall < 0.5 else 'hard')
    if on < 1:
        cap_to(cp, mix(plus(hand(cp, 0), (0.0, -0.05, -0.1)), cap_top(cp), on), 0.5 * (1 - on))
    S['dcap'].location = FAR
    h = head(cp)
    cam(S, plus(h, (-0.9, -3.5, 0.0)), plus(h, (0.0, 0.0, -0.2)), 36)
    orbit(S, k, 22, 0.25, 0.0)


def halt(S, k, t, lt):
    """A Berlin street: ten soldiers marching in two files; the captain steps into their path with his hand up, and
    they stamp to a halt."""
    amb(S, 'street')
    cp = S['capt']
    stand(cp, at(STR, 1.4, 1.3, 0), -PI / 2, P('stand', aR=(2.35, 0.25, 0.2), aL=(0.0, 0.3, 0.3), head=(-0.05, 0.0), lean=-0.05), 'hard', jaw=chat(t, 0.15 < k < 0.7))
    u = min(1.0, k / 0.5)
    x0 = lerp(-6.4, -2.2, u)
    stamp = sm((k - 0.5) / 0.06) * (1 - sm((k - 0.58) / 0.1))
    for i in range(10):
        soldier(S, i, at(STR, x0 - 1.7 * (i // 2), 0.55 + 1.5 * (i % 2), 0.1 * stamp), PI / 2, 'slope', t, walking=u < 1, head=(-0.1 * (u >= 1), 0.0))
    cam(S, at(STR, 4.0, -2.3, 2.4), at(STR, -1.1, 1.3, 2.25), 30)
    orbit(S, k, 15, 0.2, 0.0)


def rook_follow(S, k, t, lt):
    """Marching towards us: the captain out in front, the ten behind him in step, and Rook keeping pace at his elbow,
    looking him up and down, then turning to us with a shrug."""
    amb(S, 'street')
    bx = -9.0 + 3.0 * lt
    cp = S['capt']
    stand(cp, at(STR, bx + 6.0, 1.3, 0), PI / 2, step(t, 1.7, head=(-0.12, 0.0), lean=0.0), 'hard')
    for i in range(10):
        soldier(S, i, at(STR, bx + 4.0 - 1.7 * (i // 2), 0.55 + 1.5 * (i % 2), 0), PI / 2, 'slope', t, walking=True)
    rk = S['rook']
    sh = sm((k - 0.4) / 0.18)
    w = step(t + 0.2, 1.7, head=(lerp(-0.1, 0.0, sh), lerp(0.3, -0.55, sh)))
    stand(rk, at(STR, bx + 5.7, -0.5, 0), PI / 2, blend(w, dict(w, aL=P('shrug')['aL'], aR=P('shrug')['aR']), sh))
    S['rface'] = 'squint' if sh < 0.5 else 'low'
    S['hat_tip'] = 0.3
    cam(S, at(STR, bx + 10.6, -3.0, 1.9), at(STR, bx + 5.6, 0.5, 2.35), 30)
    orbit(S, k, 12, 0.15, 0.0)


# ---------------------------------------------------------------- caught, and let go
def caught(S, k, t, lt):
    """The alley again, by day's last light: two policemen close in from either side and take the old man by the
    shoulders; he lifts his hands a little and lets them."""
    amb(S, 'alley')
    vg = S['voigt']
    for o in S['apron']:
        o.hide_render = True
    v0 = at(ALY, 1.0, 0.6, 0)
    u = sm(k / 0.45)
    stand(vg, v0, 0.0, blend(P('stand', head=(0.0, 0.6 * math.sin(lt * 9) * (1 - u))), P('shrug', head=(0.1, 0.0)), (k - 0.4) / 0.25), 'wide' if k < 0.5 else 'tired')
    for i, s in enumerate((-1, 1)):
        p = mix(at(ALY, 1.0 + s * 5.5, 0.1, 0), at(ALY, 1.0 + s * 1.2, 0.75, 0), u)
        arm = (1.3, -0.25, 0.4) if u > 0.9 else (0.6, 0.1, 0.8)
        stand(S['pol'][i], p, facing(p, v0), step(t + 0.3 * i, 1.8, **{('aR' if s < 0 else 'aL'): arm}) if u < 0.98 else P('stand', **{('aR' if s < 0 else 'aL'): arm}), 'hard')
    cam(S, at(ALY, -0.6, -4.3, 2.5), at(ALY, 1.0, 0.6, 2.3), 30)
    orbit(S, k, 20, 0.22, 0.0)


def rook_cell(S, k, t, lt):
    """A stone cell: the old man on the bunk with his head down, and Rook sitting beside him, tapping his beak, looking
    at him sideways."""
    amb(S, 'cell')
    vg = S['voigt']
    for o in S['apron']:
        o.hide_render = True
    stand(vg, at(CEL, -0.72, 1.7, 0.31), 0.0, P('sit', head=(0.5, 0.0), lean=0.38), 'tired')
    rk = S['rook']
    look = sm((k - 0.45) / 0.2)
    stand(rk, at(CEL, 0.72, 1.7, 0.31), 0.0, P('sit', aR=(1.25, -0.25, 2.2 + 0.12 * math.sin(lt * 13), 0.6), aL=(0.7, -0.1, 1.5, 1.0), lean=0.15,
                                              head=(0.1, 0.6 * look)))
    S['rface'] = 'low' if look < 0.5 else 'soft'
    S['hat_tip'] = 0.3
    cam(S, at(CEL, 0.3, -2.7, 2.0), at(CEL, 0.0, 1.7, 1.95), 26)
    orbit(S, k, 22, 0.22, 0.0)


def kaiser(S, k, t, lt):
    """A palace study in red and gold: a man in a pale uniform with an upturned moustache lowers his newspaper,
    shakes with laughter, and brings a stamp down on a sheet of paper."""
    amb(S, 'palace')
    ks = S['kaiser']
    low = sm((k - 0.12) / 0.2)
    lg = sm((k - 0.25) / 0.1) * (1 - sm((k - 0.66) / 0.1))
    st = sm((k - 0.68) / 0.1)
    bang = sm((k - 0.82) / 0.05)
    shake = 0.05 * math.sin(lt * 21) * lg
    pose = P('sit', aL=(1.15 - 0.35 * low, -0.2, 1.3 + 0.3 * low, 0.6), aR=(1.15 - 0.35 * low, -0.2, 1.3 + 0.3 * low, 0.6), lean=0.12 + shake, head=(-0.1 * lg + 0.1 * low, 0.0))
    if st > 0:
        pose = blend(pose, P('sit', aL=(0.8, -0.2, 1.6, 0.6), aR=(lerp(1.5, 0.95, bang), 0.0, lerp(1.9, 1.15, bang)), lean=0.25, head=(0.3, 0.0)), st)
    stand(ks, at(PAL, 0.0, 2.35, 0.3), 0.0, pose, 'warm' if low > 0.5 else 'calm', jaw=chat(t, lg > 0.3))
    S['paper'].location = mix(at(PAL, 0.0, 1.5, 2.15), at(PAL, -1.3, 0.75, 1.36), low)
    S['paper'].rotation_euler = (lerp(-0.25, -PI / 2 + 0.02, low), 0, 0.3 * low)
    S['pardon'].location = at(PAL, 0.55, 0.5, 1.345)
    S['pardon'].rotation_euler = (0, 0, 0.08)
    S['stamp'].location = plus(hand(ks, 1), (0, -0.05, -0.12)) if st > 0.3 else at(PAL, 1.5, 0.4, 1.34)
    cam(S, at(PAL, -1.3, -1.5, 2.75), at(PAL, 0.0, 2.2, 2.4), 32)
    orbit(S, k, 20, 0.22, 0.0)


def rook_free(S, k, t, lt):
    """The cell door swings open on its own weight; Rook, in the corridor, sweeps an arm: after you. The old man steps
    out and blinks at the light."""
    amb(S, 'cell')
    vg = S['voigt']
    for o in S['apron']:
        o.hide_render = True
    op = sm((k - 0.05) / 0.4)
    S['celldoor'].rotation_euler = (0, 0, 1.7 * op)
    y = lerp(-1.3, -4.3, sm((k - 0.3) / 0.55))
    walking = 0.3 < k < 0.85
    stand(vg, at(CEL, 1.5, y, 0), 0.1, step(t, 1.2, head=(-0.1, 0.0)) if walking else P('stand', head=(lerp(0.2, -0.2, sm((k - 0.85) / 0.1)), 0.0)),
          'tired' if k < 0.5 else 'wide')
    rk = S['rook']
    bow = sm((k - 0.2) / 0.25)
    r0 = at(CEL, -0.35, -3.75, 0)
    stand(rk, r0, PI / 2 - 0.9, blend(P('stand'), P('stand', aR=(0.55, 1.0, 0.35), aL=(0.2, 0.2, 0.3), lean=0.28, head=(0.12, 0.3)), bow))
    S['rface'] = 'soft'
    S['hat_tip'] = 0.35 * bow
    cam(S, at(CEL, 0.7, -6.7, 1.9), at(CEL, 0.7, -3.0, 2.3), 22)
    orbit(S, k, 9, 0.1, 0.0)


# ---------------------------------------------------------------- the stage
def curtains(S, op):
    for c, s in S['curtains']:
        c.scale = (lerp(1.0, 0.2, op), 1, 1)


def crowd(S, t, clap=1.0):
    for m, hands, ph, p in S['crowd']:
        m.location = (p[0], p[1], p[2] + 0.04 * clap * abs(math.sin(t * 5 + ph)))
        c = abs(math.sin(t * 9 + ph)) * clap
        for i, h in enumerate(hands):
            h.location.x = (-1, 1)[i] * (0.08 + 0.14 * c)
            h.location.z = 1.7 + 0.25 * clap


def stage(S, k, t, lt):
    """From the stalls, over hats and heads: the red curtains part on a painted town hall, and there he is in the
    uniform, in the spotlight, saluting the house."""
    amb(S, 'stage')
    curtains(S, sm(k / 0.5))
    crowd(S, t, sm((k - 0.5) / 0.2))
    cp = S['capt']
    u = sm((k - 0.5) / 0.15)
    stand(cp, at(THE, 0.0, 5.0, 1.2), 0.0, blend(P('stand', head=(-0.05, 0.0)), P('hat', lean=-0.06, head=(-0.1, 0.0)), u), 'warm')
    cam(S, at(THE, 0.9, -4.3, 2.9), at(THE, 0.0, 4.8, 3.3), 30)
    orbit(S, k, 12, 0.2, 0.0)


def rook_seat(S, k, t, lt):
    """From the stage: the front row clapping, and Rook in the middle of it, beak open in a caw of a laugh, clapping too."""
    amb(S, 'stage')
    curtains(S, 1.0)
    S['house'].data.energy = 1800
    crowd(S, t, 1.0)
    rk = S['rook']
    sx, sy, sz = S['seat']
    c = math.sin(lt * 15)
    stand(rk, at(THE, sx, sy, sz + 0.25), PI, P('sit', aL=(1.15, -0.3 + 0.16 * c, 1.25, 0.5), aR=(1.15, -0.3 + 0.16 * c, 1.25, 0.5), lean=0.05 - 0.1 * abs(math.sin(lt * 6)),
                                              head=(-0.2, 0.0)))
    S['laugh'] = sm((k - 0.12) / 0.12) * (1 - sm((k - 0.85) / 0.1))
    S['rface'] = 'laugh'
    h = head(rk)
    cam(S, plus(h, (-1.2, 3.9, 1.5)), plus(h, (0.0, 0.0, -0.15)), 32)
    orbit(S, k, 20, 0.22, 0.0)


def rook_wings(S, k, t, lt):
    """On the boards: he sweeps his cap off in a deep bow as flowers land round his boots; behind him, by a scenery
    flat, Rook claps slowly and then touches his brim."""
    amb(S, 'stage')
    curtains(S, 1.0)
    S['house'].data.energy = 250
    crowd(S, t, 1.0)
    cp = S['capt']
    b = sm(k / 0.3) * (1 - sm((k - 0.78) / 0.2))
    stand(cp, at(THE, 1.2, 5.0, 1.2), 0.0, P('stand', aR=(0.5, 1.15 * b + 0.12, 0.3), aL=(0.2, 0.25, 0.3), lean=0.72 * b, head=(0.25 * b, 0.0),
                                             lL=(0.25 * b, 0.0), lR=(-0.1 * b, 0.15 * b)), 'warm')
    if b > 0.02:
        cap_to(cp, mix(cap_top(cp), plus(hand(cp, 1), (0.0, -0.1, 0.0)), sm(b / 0.5)), 0.8 * b)
    for i, f in enumerate(S['flowers']):
        u = (k - 0.1 - 0.13 * i) / 0.28
        x1, y1 = -0.4 + 0.8 * i, 3.4 + 0.5 * (i % 2)
        if u <= 0:
            continue
        uu = min(1.0, u)
        f.location = at(THE, lerp(x1 - 0.6 + 0.5 * i, x1, uu), lerp(-1.5, y1, uu), lerp(0.6, 1.26, uu) + 2.6 * math.sin(PI * uu) * (uu < 1))
        f.rotation_euler = (1.4 + 3 * (1 - uu), 0.4 * i, 1.0 * i + 4 * (1 - uu))
    rk = S['rook']
    tip = sm((k - 0.66) / 0.16)
    c = max(0.0, math.sin(lt * 5.5))
    stand(rk, at(THE, 1.4, 7.7, 1.2), 0.55, blend(P('stand', aL=(1.0, -0.3 + 0.2 * c, 1.3, 0.5), aR=(1.0, -0.3 + 0.2 * c, 1.3, 0.5), head=(0.05, -0.3)), P('hat'), tip))
    S['rface'] = 'soft'
    S['hat_tip'] = 0.5 * tip
    cam(S, at(THE, -3.6, 1.7, 2.6), at(THE, 1.6, 6.0, 2.7), 28)
    orbit(S, k, 18, 0.2, 0.0)


def signoff(S, k, t, lt):
    """Rook alone between the half-drawn curtains: he spots a brass button on the boards, picks it up, turns it in the
    footlights, pockets it and tugs his brim. "Case closed." """
    amb(S, 'stage')
    curtains(S, 0.42)
    crowd(S, t, 0.0)
    rk = S['rook']
    pick = sm(k / 0.3)
    show_ = sm((k - 0.3) / 0.2) * (1 - sm((k - 0.7) / 0.15))
    pose = blend(P('stand', lL=(0.6, 1.1), lR=(0.2, 0.8), lift=-0.4, lean=0.5, aR=(0.9, 0.1, 0.3), head=(0.5, 0.0)),
                 P('stand', aR=(1.9, 0.0, 0.6, 0.4), head=(-0.2, 0.0)), pick)
    if k > 0.72:
        pose = blend(pose, P('hat'), sm((k - 0.72) / 0.2))
    stand(rk, at(THE, 0.0, 3.2, 1.2), 0.12, pose)
    S['rface'] = 'low' if k > 0.72 else 'calm'
    S['hat_tip'] = 0.25 + 0.35 * sm((k - 0.8) / 0.15)
    hr = hand(rk, 1)
    S['button'].location = plus(hr, (0, -0.1, 0.08)) if k < 0.78 else FAR
    S['button'].rotation_euler = (1.2, 0.3 + 2 * t, 0.4)
    S['glint'].location = plus(hr, (0.3, -0.7, 0.4))
    S['glint'].data.energy = 220 * show_
    h = head(rk)
    cam(S, plus(h, (0.7, -4.9, -0.5)), plus(h, (0.0, 0.0, -0.45)), 30)
    orbit(S, k, 34, 0.3, 0.0)


SHOTS3D = {'office_burst': office_burst, 'boots_in': boots_in, 'captain_point': captain_point, 'mayor_up': mayor_up, 'rook_desk': rook_desk,
           'treasurer': treasurer, 'cash': cash, 'rook_coins': rook_coins, 'line_up': line_up, 'mayor_march': mayor_march, 'rook_peer': rook_peer,
           'walk_out': walk_out, 'rook_gone': rook_gone, 'cap_off': cap_off, 'cobbler': cobbler, 'rook_shoe': rook_shoe, 'shop': shop,
           'rook_mag': rook_mag, 'dress': dress, 'halt': halt, 'rook_follow': rook_follow, 'caught': caught, 'rook_cell': rook_cell,
           'kaiser': kaiser, 'rook_free': rook_free, 'stage': stage, 'rook_seat': rook_seat, 'rook_wings': rook_wings, 'signoff': signoff}
