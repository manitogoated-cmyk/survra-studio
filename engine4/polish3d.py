"""Finish pass for a built 3D world: turns the kit's faceted primitives into smooth, bevelled forms.
Runs once after an episode's build(), on every mesh however it was made, so sets and characters need no rewriting:
  boxes        -> rounded edges with clean flat faces
  cylinders,
  cones        -> re-cut with many more sides (3- and 4-sided ones are deliberate prisms and pyramids, so they stay)
  ico spheres  -> re-cut fine and smooth
  the rest     -> smooth shading with hard edges kept where the surface really turns
Object transforms, parents, names and materials are untouched, so every shot function keeps working."""
import math

import bmesh
import bpy

SIDES = 40
SHARP = math.radians(42)


def _smooth(me, angle=SHARP):
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=angle)
    me.update()


def _is_box(me):
    if len(me.vertices) != 8 or len(me.polygons) != 6:
        return None
    xs = sorted({round(abs(v.co.x), 5) for v in me.vertices})
    ys = sorted({round(abs(v.co.y), 5) for v in me.vertices})
    zs = sorted({round(abs(v.co.z), 5) for v in me.vertices})
    if len(xs) == len(ys) == len(zs) == 1 and xs[0] > 0 and ys[0] > 0 and zs[0] > 0:
        return xs[0], ys[0], zs[0]
    return None


def _round_box(o, half):
    sx, sy, sz = (abs(s) for s in o.matrix_world.to_scale())      # true size on screen, parents included
    if min(sx, sy, sz) < 1e-6:
        return False
    dims = (2 * half[0] * sx, 2 * half[1] * sy, 2 * half[2] * sz)
    thin = min(dims)
    if thin < 0.012:
        return False
    r = min(max(0.05 * thin, 0.006), 0.14, 0.32 * thin)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x, v.co.y, v.co.z = v.co.x * dims[0], v.co.y * dims[1], v.co.z * dims[2]
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=r, offset_type='OFFSET', segments=3, profile=0.5, affect='EDGES', clamp_overlap=True)
    for v in bm.verts:
        v.co.x, v.co.y, v.co.z = v.co.x / sx, v.co.y / sy, v.co.z / sz
    bm.to_mesh(o.data)
    bm.free()
    _smooth(o.data, math.radians(60))
    m = o.modifiers.new('wn', 'WEIGHTED_NORMAL')
    m.keep_sharp = False
    m.weight = 100
    return True


def _is_round(me):
    """(r_bottom, r_top, depth, sides, capped) when the mesh is an upright cylinder or cone from the kit."""
    n = len(me.vertices)
    if n < 6:
        return None
    zs = sorted({round(v.co.z, 5) for v in me.vertices})
    if len(zs) != 2 or abs(zs[0] + zs[1]) > 1e-4:
        return None
    lo = [v for v in me.vertices if round(v.co.z, 5) == zs[0]]
    hi = [v for v in me.vertices if round(v.co.z, 5) == zs[1]]
    rad = lambda vs: max(math.hypot(v.co.x, v.co.y) for v in vs)
    r1, r2 = rad(lo), rad(hi)
    for vs, r in ((lo, r1), (hi, r2)):
        if any(abs(math.hypot(v.co.x, v.co.y) - r) > 1e-4 * max(1.0, r) for v in vs):
            return None
    sides = max(len(lo), len(hi))
    if sides < 5 or len(lo) not in (1, sides) or len(hi) not in (1, sides):
        return None
    capped = len(me.polygons) > sides
    return r1, r2, zs[1] - zs[0], sides, capped


def _recut_round(o, spec):
    r1, r2, depth, sides, capped = spec
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=capped, cap_tris=False, segments=SIDES, radius1=r1, radius2=r2, depth=depth)
    if capped:
        sx, sy, sz = (abs(s) for s in o.matrix_world.to_scale())
        s = min(sx, sy, sz) if min(sx, sy, sz) > 1e-6 else 1.0
        thin = min(depth, 2 * max(r1, r2)) * s
        w = min(max(0.06 * thin, 0.004), 0.1, 0.3 * thin) / s
        rim = [e for e in bm.edges if len(e.link_faces) == 2 and any(len(f.verts) > 4 for f in e.link_faces)
               and min(v.co.to_2d().length for v in e.verts) > 2.5 * w]
        if rim and thin > 0.03:
            bmesh.ops.bevel(bm, geom=rim, offset=w, offset_type='OFFSET', segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
    bm.to_mesh(o.data)
    bm.free()
    _smooth(o.data, math.radians(50))


def _is_ico(me):
    n = len(me.vertices)
    if n not in (12, 42, 162):
        return None
    rs = [v.co.length for v in me.vertices]
    r = sum(rs) / n
    if r <= 0 or max(abs(x - r) for x in rs) > 1e-4 * max(1.0, r):
        return None
    return r


def _recut_ico(o, r):
    bm = bmesh.new()
    size = r * max(abs(x) for x in o.matrix_world.to_scale())
    # hills, clouds and domes need a round outline; sparks, snow and bubbles are too small to need the detail
    bmesh.ops.create_icosphere(bm, subdivisions=4 if size > 2.0 else 2 if size < 0.1 else 3, radius=r)
    bm.to_mesh(o.data)
    bm.free()
    _smooth(o.data, math.radians(180))


def polish(skip=()):
    """Upgrade every mesh in the file. skip = objects to leave exactly as built (animated grids such as a sea)."""
    seen, n = set(), dict(box=0, round=0, ico=0, smooth=0)
    bpy.context.view_layer.update()
    skip = {o.name for o in skip}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name in skip:
            continue
        me = o.data
        if me.name in seen:
            continue
        seen.add(me.name)
        if me.users > 1 or len(me.vertices) > 4000 or len(me.polygons) < 2:
            continue
        half = _is_box(me)
        if half:
            n['box'] += bool(_round_box(o, half))
            continue
        spec = _is_round(me)
        if spec:
            _recut_round(o, spec)
            n['round'] += 1
            continue
        r = _is_ico(me)
        if r:
            _recut_ico(o, r)
            n['ico'] += 1
            continue
        if len(me.vertices) >= 12 and all(len(p.vertices) <= 4 for p in me.polygons):
            _smooth(me)
            n['smooth'] += 1
    return n
