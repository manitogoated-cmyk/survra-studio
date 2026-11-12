"""3D look test: Rook built from primitives in Blender (bpy), rendered on CPU with Cycles."""
import math, sys, time
import bpy
from mathutils import Vector

def hexc(h, a=1.0):
    h = h.lstrip('#'); r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)

def mat(name, col, rough=0.65, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = hexc(col); b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = hexc(col); b.inputs['Emission Strength'].default_value = emit
    return m

def add(kind, m, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, **kw):
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o

def build(pose='hat_tip'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = dict(fea=mat('fea', '2A2742', 0.8), coat=mat('coat', '566178', 0.7), lap=mat('lap', '6B7790', 0.7), hat=mat('hat', '34303B', 0.6),
             org=mat('org', 'FF7A1A', 0.5), beak=mat('beak', '7A8096', 0.4), eye=mat('eye', 'FFB000', 0.3, 2.5), blk=mat('blk', '111018', 0.5),
             dark=mat('dark', '2B2834', 0.7), gold=mat('gold', 'FFC233', 0.3), floor=mat('floor', '1B2A33', 0.9))
    add('plane', M['floor'], size=60)
    for s in (-1, 1):
        add('uv_sphere', M['blk'], (s * 0.16, -0.07, 0.09), scale=(0.13, 0.24, 0.09), radius=1)
        add('cylinder', M['dark'], (s * 0.16, 0, 0.56), radius=0.085, depth=0.9)
    add('cone', M['coat'], (0, 0, 1.235), radius1=0.40, radius2=0.27, depth=1.15, vertices=48)
    add('uv_sphere', M['coat'], (0, 0, 1.79), scale=(0.29, 0.26, 0.13), radius=1)
    add('cylinder', M['dark'], (0, 0, 1.2), radius=0.345, depth=0.06, vertices=48)
    add('cube', M['gold'], (0, -0.345, 1.2), scale=(0.045, 0.02, 0.04), size=1)
    add('cone', M['org'], (0, -0.265, 1.63), rot=(math.pi, 0, 0), radius1=0.075, radius2=0.0, depth=0.34)
    for s in (-1, 1):
        add('cube', M['lap'], (s * 0.13, -0.255, 1.66), rot=(0.25, 0, s * 0.5), scale=(0.11, 0.02, 0.26), size=1)
        add('cube', M['lap'], (s * 0.2, -0.12, 1.9), rot=(0.1, 0, s * -0.4), scale=(0.12, 0.02, 0.2), size=1)
    # arms: left hangs, right tips the hat
    add('cylinder', M['coat'], (-0.43, 0, 1.38), rot=(0, -0.2, 0), radius=0.08, depth=0.78)
    add('uv_sphere', M['fea'], (-0.52, 0, 0.97), radius=0.095)
    if pose == 'hat_tip':
        add('cylinder', M['coat'], (0.47, -0.05, 1.62), rot=(0.25, 0.75, 0), radius=0.08, depth=0.46)
        add('cylinder', M['coat'], (0.56, -0.2, 1.98), rot=(0.9, -0.35, 0), radius=0.075, depth=0.5)
        add('uv_sphere', M['fea'], (0.47, -0.42, 2.2), radius=0.095)
    else:
        add('cylinder', M['coat'], (0.43, 0, 1.38), rot=(0, 0.2, 0), radius=0.08, depth=0.78)
        add('uv_sphere', M['fea'], (0.52, 0, 0.97), radius=0.095)
    add('uv_sphere', M['fea'], (0, 0, 2.07), scale=(0.3, 0.3, 0.31), radius=1)
    add('cone', M['beak'], (0, -0.5, 1.98), rot=(math.radians(100), 0, 0), radius1=0.115, radius2=0.0, depth=0.64, vertices=24)
    for s in (-1, 1):
        add('uv_sphere', M['eye'], (s * 0.125, -0.245, 2.13), scale=(1, 1, 0.6), radius=0.075)
        add('uv_sphere', M['blk'], (s * 0.13, -0.305, 2.13), radius=0.03)
        add('cube', M['blk'], (s * 0.125, -0.275, 2.185), rot=(0.3, s * 0.42, 0), scale=(0.13, 0.03, 0.03), size=1)
        for k in range(3):
            add('cone', M['fea'], (s * 0.02 * k, 0.28, 2.0 + k * 0.08), rot=(math.radians(-70), 0, 0), radius1=0.07, radius2=0, depth=0.22)
    bpy.ops.object.empty_add(location=(0, 0, 2.3), rotation=(-0.16, 0.06, 0)); hat = bpy.context.object
    add('cylinder', M['hat'], (0, 0, 0), radius=0.6, depth=0.035, vertices=64, parent=hat)
    add('cone', M['hat'], (0, 0, 0.19), radius1=0.315, radius2=0.26, depth=0.36, vertices=48, parent=hat)
    add('cylinder', M['org'], (0, 0, 0.055), radius=0.322, depth=0.075, vertices=48, parent=hat)
    for o in bpy.data.objects:   # longer legs: lift everything above the knees
        if o.parent is None and o.location.z > 0.75 and o.type in ('MESH', 'EMPTY'):
            o.location.z += 0.28
    # lights, world, camera
    w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = hexc('16222B'); w.node_tree.nodes['Background'].inputs[1].default_value = 0.6
    def light(kind, loc, energy, col, size=3):
        bpy.ops.object.light_add(type=kind, location=loc); l = bpy.context.object
        l.data.energy = energy; l.data.color = hexc(col)[:3]
        if kind == 'AREA': l.data.size = size
        c = l.constraints.new('TRACK_TO'); c.target = tgt; return l
    bpy.ops.object.empty_add(location=(0, 0, 1.5)); tgt = bpy.context.object
    light('AREA', (-3.2, -4.2, 4.6), 620, 'FFF2DC', 4)
    light('AREA', (3.6, 3.2, 3.4), 1800, 'FF7A1A', 2)
    light('AREA', (2.5, -3.5, 1.0), 120, '8FB8FF', 3)
    bpy.ops.object.camera_add(location=(1.7, -6.9, 1.9)); cam = bpy.context.object; cam.data.lens = 60
    c = cam.constraints.new('TRACK_TO'); c.target = tgt; bpy.context.scene.camera = cam
    return cam

def render(out, w=900, h=1200, samples=48):
    sc = bpy.context.scene
    try: bpy.ops.preferences.addon_enable(module='cycles')
    except Exception as e: print('cycles addon:', e)
    try:
        sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
        try: sc.cycles.use_denoising = True
        except Exception: pass
    except Exception as e:
        print('cycles unavailable, using', sc.render.engine, e)
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.filepath = out
    sc.render.image_settings.file_format = 'PNG'
    t0 = time.time(); bpy.ops.render.render(write_still=True); return time.time() - t0

if __name__ == '__main__':
    build(); print('hero %.1fs' % render(sys.argv[1]), 'engine', bpy.context.scene.render.engine)
