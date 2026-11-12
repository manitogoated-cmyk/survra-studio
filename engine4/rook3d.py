"""3D Rook, faceted low-poly style (free: Blender bpy on CPU). build() -> handles; hero still + short motion test."""
import math, os, subprocess, sys, time
import bpy

def hexc(h, a=1.0):
    h = h.lstrip('#'); r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)

def mat(name, col, rough=0.9, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = hexc(col); b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = hexc(col); b.inputs['Emission Strength'].default_value = emit
    return m

def add(kind, m, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, **kw):
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m)   # flat shading on purpose: crisp facets
    if parent: o.parent = parent
    return o

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = dict(fea=mat('fea', '2F2B4D'), coat=mat('coat', '4E5A72'), lap=mat('lap', '6B7790'), hat=mat('hat', '2B2733'),
             org=mat('org', 'FF7A1A', 0.6), beak=mat('beak', '8A90A6', 0.5), eye=mat('eye', 'FFB000', 0.4, 3.0), blk=mat('blk', '0E0D14', 0.6),
             dark=mat('dark', '23212B'), gold=mat('gold', 'FFC233', 0.35), floor=mat('floor', '18242C'))
    add('plane', M['floor'], size=80)
    bpy.ops.object.empty_add(location=(0, 0, 0)); root = bpy.context.object
    P = dict(parent=root)
    for s in (-1, 1):
        add('cube', M['blk'], (s * 0.16, -0.09, 0.07), scale=(0.2, 0.42, 0.14), size=1, **P)
        add('cylinder', M['dark'], (s * 0.16, 0, 0.6), radius=0.09, depth=0.95, vertices=6, **P)
    add('cone', M['coat'], (0, 0, 1.55), radius1=0.44, radius2=0.3, depth=1.2, vertices=8, **P)
    add('cube', M['coat'], (0, 0, 2.13), scale=(0.74, 0.34, 0.12), size=1, **P)
    add('cylinder', M['dark'], (0, 0, 1.5), radius=0.385, depth=0.07, vertices=8, **P)
    add('cube', M['gold'], (0, -0.36, 1.5), scale=(0.07, 0.03, 0.06), size=1, **P)
    add('cone', M['org'], (0, -0.3, 1.9), rot=(math.pi, 0, 0), radius1=0.09, radius2=0.0, depth=0.42, vertices=4, **P)
    for s in (-1, 1):
        add('cube', M['lap'], (s * 0.15, -0.29, 1.93), rot=(0.22, 0, s * 0.5), scale=(0.13, 0.025, 0.34), size=1, **P)
        add('cube', M['lap'], (s * 0.2, -0.1, 2.3), rot=(0.1, 0, s * -0.35), scale=(0.16, 0.025, 0.28), size=1, **P)
    add('cylinder', M['coat'], (-0.5, 0, 1.72), rot=(0, -0.16, 0), radius=0.085, depth=0.82, vertices=6, **P)
    add('ico_sphere', M['fea'], (-0.57, 0, 1.27), radius=0.11, subdivisions=1, **P)
    add('cylinder', M['coat'], (0.52, -0.05, 1.95), rot=(0.25, 0.8, 0), radius=0.085, depth=0.5, vertices=6, **P)
    fore = add('cylinder', M['coat'], (0.62, -0.22, 2.33), rot=(0.9, -0.35, 0), radius=0.08, depth=0.52, vertices=6, **P)
    hand = add('ico_sphere', M['fea'], (0.52, -0.45, 2.56), radius=0.11, subdivisions=1, **P)
    bpy.ops.object.empty_add(location=(0, 0, 2.42)); head = bpy.context.object; head.parent = root
    H = dict(parent=head)
    add('ico_sphere', M['fea'], (0, 0, 0), scale=(1, 1, 1.08), radius=0.33, subdivisions=1, **H)
    add('cone', M['beak'], (0, -0.52, -0.1), rot=(math.radians(103), 0, 0), radius1=0.14, radius2=0.0, depth=0.72, vertices=4, **H)
    eyes = []
    for s in (-1, 1):
        eyes.append(add('cube', M['eye'], (s * 0.14, -0.285, 0.06), rot=(0.2, s * 0.32, s * -0.25), scale=(0.15, 0.03, 0.07), size=1, **H))
        add('cube', M['blk'], (s * 0.15, -0.305, 0.055), rot=(0.2, s * 0.32, s * -0.25), scale=(0.045, 0.02, 0.05), size=1, **H)
        add('cube', M['blk'], (s * 0.14, -0.29, 0.135), rot=(0.25, s * 0.5, s * -0.25), scale=(0.2, 0.05, 0.04), size=1, **H)
        for k in range(3):
            add('cone', M['fea'], (s * 0.04 * k, 0.3, -0.12 + k * 0.1), rot=(math.radians(-65), 0, 0), radius1=0.08, radius2=0, depth=0.26, vertices=4, **H)
    bpy.ops.object.empty_add(location=(0, 0, 0.27), rotation=(-0.2, 0.07, 0)); hat = bpy.context.object; hat.parent = head
    add('cylinder', M['hat'], (0, 0, 0), radius=0.66, depth=0.04, vertices=10, parent=hat)
    add('cone', M['hat'], (0, 0, 0.2), radius1=0.34, radius2=0.27, depth=0.38, vertices=8, parent=hat)
    add('cylinder', M['org'], (0, 0, 0.065), radius=0.35, depth=0.08, vertices=8, parent=hat)
    w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = hexc('101A21'); w.node_tree.nodes['Background'].inputs[1].default_value = 0.5
    bpy.ops.object.empty_add(location=(0, 0, 1.65)); tgt = bpy.context.object
    def light(loc, energy, col, size):
        bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object
        l.data.energy, l.data.color, l.data.size = energy, hexc(col)[:3], size
        l.constraints.new('TRACK_TO').target = tgt
    light((-3.5, -4.0, 4.8), 900, 'FFF0D8', 2.0)
    light((3.8, 3.0, 3.6), 2200, 'FF7A1A', 1.5)
    light((3.0, -3.0, 0.8), 90, '7FA8FF', 3)
    bpy.ops.object.camera_add(location=(1.8, -7.6, 2.0)); cam = bpy.context.object; cam.data.lens = 60
    cam.constraints.new('TRACK_TO').target = tgt; bpy.context.scene.camera = cam
    return dict(root=root, head=head, hat=hat, eyes=eyes, cam=cam, hand=hand, fore=fore)

def setup(engine='CYCLES', samples=48):
    sc = bpy.context.scene
    try: bpy.ops.preferences.addon_enable(module='cycles')
    except Exception: pass
    sc.render.engine = engine
    if engine == 'CYCLES':
        sc.cycles.samples, sc.cycles.device = samples, 'CPU'
        try: sc.cycles.use_denoising = True
        except Exception: pass
    sc.render.image_settings.file_format = 'PNG'

def render(out, w, h):
    sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath = w, h, out
    t0 = time.time(); bpy.ops.render.render(write_still=True); return time.time() - t0

if __name__ == '__main__':
    R = build(); setup('CYCLES', 48)
    print('hero %.1fs' % render(sys.argv[1], 900, 1200))
    n, fps, d = 54, 18, '/tmp/rook3d_frames'; os.makedirs(d, exist_ok=True); setup('CYCLES', 10); t0 = time.time()
    for i in range(n):
        k = i / (n - 1); a = -0.5 + 1.0 * k
        R['cam'].location = (7.8 * math.sin(a), -7.8 * math.cos(a), 2.0 + 0.3 * math.sin(k * math.pi))
        tip = math.sin(min(1, k * 2.2) * math.pi)            # hat tip, then settle
        R['hat'].rotation_euler = (-0.2 - 0.3 * tip, 0.07, 0)
        R['head'].rotation_euler = (0.12 * tip, 0, 0.45 * math.sin(k * math.pi * 2) * 0.6)
        R['root'].location = (0, 0, 0.03 * math.sin(k * math.pi * 4))
        blink = 0.15 if 0.62 < k < 0.68 else 1.0
        for e in R['eyes']: e.scale = (0.15, 0.03, 0.07 * blink)
        render(f'{d}/f{i:03d}.png', 432, 768)
    print('clip %d frames, %.1fs per frame' % (n, (time.time() - t0) / n))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-r', str(fps), '-i', f'{d}/f%03d.png', '-vf', 'scale=864:1536:flags=lanczos', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', sys.argv[2]], check=True)
