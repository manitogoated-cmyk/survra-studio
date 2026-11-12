"""Channel art from the 3D Rook rig: profile picture, banner (2560x1440, text inside the 1546x423 safe area), watermark.
Usage: python3 engine4/brand3d.py  ->  brand/rook_profile_800.jpg, brand/rook_banner_2560x1440.jpg, brand/rook_watermark_150.png"""
import math
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine4 import kit3d as K  # noqa: E402

OUT = os.path.join(ROOT, 'brand')
TMP = '/tmp/brand3d'


def shoot(name, w, h, pos, look, lens, pose, yaw, brow=-0.5, samples=64):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    K._M.clear()
    rook = K.Rig(dict(top='566178', belt='3E4658', lap='6B7690', pants='2A2742', hand='2F2B4D', boot='8A90A6'), K.rook_head, coat=True)
    rook.place((0, 0, 0), yaw)
    rook.apply(pose)
    ex = rook.extra
    for i, s in enumerate((-1, 1)):
        ex['eyes'][i].scale = (0.15, 0.03, 0.05)
        ex['brows'][i].rotation_euler = (0.25, s * 0.5 + (s * brow if s > 0 else 0.1), s * -0.25)
    ex['hat'].rotation_euler = (-0.05, 0.07, 0)
    aim = K.empty((0, 0, 2.2))
    K.light((-4.5, -5.5, 5.0), 1700, 'FFE2B8', 3.0, aim)
    K.light((3.5, 3.5, 4.6), 3200, 'FF7A1A', 1.5, aim)
    K.light((4.5, -5, 1.6), 260, '5E8FD0', 4.0, aim)
    tgt, rig = K.empty(look), K.empty(pos)
    con = rig.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam = bpy.context.object
    cam.parent = rig
    cam.data.lens = lens
    sc = bpy.context.scene
    sc.camera = cam
    K.setup(samples)
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.resolution_x, sc.render.resolution_y = w, h
    os.makedirs(TMP, exist_ok=True)
    sc.render.filepath = os.path.join(TMP, name + '.png')
    bpy.ops.render.render(write_still=True)
    return sc.render.filepath


def compose(bust, body):
    import skia
    tf = skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant))
    P = lambda c: skia.Paint(AntiAlias=True, Color=c)
    cubic = skia.SamplingOptions(skia.CubicResampler.Mitchell())
    b, f = skia.Image.open(bust), skia.Image.open(body)

    def backdrop(cv, w, h, cx, cy, r):
        cv.clear(0xFF12131F)
        cv.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Shader=skia.GradientShader.MakeRadial(
            (cx, cy), r, [0xFFFF8A2A, 0xFFE0621A, 0xFF7A2E12, 0xFF1A1420], [0.0, 0.35, 0.75, 1.0])))

    # profile 800
    s = skia.Surface(800, 800)
    cv = s.getCanvas()
    backdrop(cv, 800, 800, 400, 380, 620)
    cv.drawImageRect(b, skia.Rect.MakeXYWH(-20, 10, 840, 840), cubic)
    s.makeImageSnapshot().save(os.path.join(OUT, 'rook_profile_800.jpg'), skia.kJPEG, 94)
    # watermark 150 (round badge)
    s = skia.Surface(150, 150)
    cv = s.getCanvas()
    cv.clear(0x00000000)
    cv.save()
    path = skia.Path()
    path.addCircle(75, 75, 73)
    cv.clipPath(path, doAntiAlias=True)
    backdrop(cv, 150, 150, 75, 72, 115)
    cv.drawImageRect(b, skia.Rect.MakeXYWH(-6, 0, 162, 162), cubic)
    cv.restore()
    s.makeImageSnapshot().save(os.path.join(OUT, 'rook_watermark_150.png'), skia.kPNG)
    # banner 2560x1440, safe area x 507..2053, y 508..931
    W, H = 2560, 1440
    s = skia.Surface(W, H)
    cv = s.getCanvas()
    cv.clear(0xFF10111C)
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (760, 700), 1500, [0xFF3A2440, 0xFF1C1A2E, 0xFF0C0D16], [0.0, 0.5, 1.0])))
    for i in range(16):                                   # venetian-blind light, the office look
        y = 120 + i * 78
        pa = P(0xFFFF7A1A)
        pa.setAlphaf(0.10 if i % 2 == 0 else 0.05)
        cv.save()
        cv.translate(W / 2, y)
        cv.skew(-0.5, 0)
        cv.drawRect(skia.Rect.MakeXYWH(-W, 0, 2 * W, 40), pa)
        cv.restore()
    bw = 500
    cv.drawImageRect(b, skia.Rect.MakeXYWH(560, 470, bw, bw), cubic)
    x0 = 560 + bw + 30
    cv.drawTextBlob(skia.TextBlob('SURVRA', skia.Font(tf, 190)), x0, 700, P(0xFFFFB000))
    cv.drawTextBlob(skia.TextBlob('TRUE STORIES. ONE SCEPTICAL CROW.', skia.Font(tf, 50)), x0 + 6, 780, P(0xFFFFFFFF))
    cv.drawTextBlob(skia.TextBlob("ROOK'S CASE FILES  •  ANIMATED TRUE STORIES", skia.Font(tf, 36)), x0 + 6, 842, P(0xFFFF7A1A))
    s.makeImageSnapshot().save(os.path.join(OUT, 'rook_banner_2560x1440.jpg'), skia.kJPEG, 92)
    print('brand art written to', OUT)


if __name__ == '__main__':
    if len(sys.argv) > 1:                       # recompose only
        compose(os.path.join(TMP, 'bust.png'), os.path.join(TMP, 'body.png'))
        sys.exit(0)
    bust = shoot('bust', 900, 900, (1.25, -3.9, 2.55), (0.0, 0, 2.42), 62, K.P('cross', head=(0.1, -0.12)), 0.32)
    body = shoot('body', 700, 1000, (1.6, -6.4, 2.2), (0.0, 0, 1.95), 60, K.P('cross', head=(0.1, -0.12)), 0.32)
    compose(bust, body)
