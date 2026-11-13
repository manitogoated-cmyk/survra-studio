"""Case 001, full case file (16:9). The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(case board, blackout, air gauge, radio), the overlays drawn on top of 3D shots, and the thumbnail."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1920, 1080
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('BFE0EC')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def cork(cv):
    Wd.fill(cv, 0, 0, W, H, h('9A6E44'))
    R = Wd.Rand(4)
    for i in range(220):
        cv.drawCircle(R(0, W), R(0, H), R(2, 6), P(Wd.alpha(h('6E4A2A'), 0.5)))
    cv.drawRect(skia.Rect.MakeLTRB(20, 20, W - 20, H - 20), P(h('4A2F1A'), 40))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x55000000)])


def card(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 10, -h_ / 2 + 14, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(4, -h_ / 2 + 26, 16, P(0x66000000))
    cv.drawCircle(0, -h_ / 2 + 22, 15, P(h('E5392F')))
    cv.drawCircle(-4, -h_ / 2 + 18, 5, P(h('FF8A80')))
    cv.restore()


def board_ship(cv, c):
    cork(cv)
    k = min(1, c.lt / 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    card(cv, 760, 440, 900 * s, 640 * s, -3)
    cv.save()
    cv.translate(760, 440)
    cv.rotate(-3)
    cv.scale(s, s)
    photo(cv, 'tug', 0, 20, 820, 500, (0.5, 0.5))
    cv.restore()
    k2 = min(1, max(0, (c.lt - 0.4) / 0.2))
    if k2 > 0:
        cv.drawLine(760, 150, lerp(760, 1430, k2), lerp(150, 380, k2), P(h('E5392F'), 8))
        cv.save()
        cv.translate(1450, 500)
        cv.scale(1 + 0.5 * (1 - k2), 1 + 0.5 * (1 - k2))
        card(cv, 0, 0, 420, 280, 6, h('FFD866'))
        cv.rotate(6)
        Wd.text_card(cv, '3 DAYS', 0, 40, 96, INK, None)
        cv.restore()


def blackout(cv, c):
    t = c.t
    Wd.fill(cv, 0, 0, W, H, 0xFF000000)
    Wd.particles(cv, W, H, t * 3, 260, Wd.alpha(h('BFE6FF'), 0.8), 7, size=(5, 14), drift=(-220, -560), wobble=90)
    for i in range(5):
        x0 = (i * 431 + t * 900) % (W + 400) - 200
        cv.drawLine(x0, 0, x0 - 260, H, P(Wd.alpha(h('3A6A8A'), 0.5), 46))
    x, y = 800 + math.sin(t * 5) * 140, 470 + math.cos(t * 4) * 50
    blink = (t * 1.7) % 1 < 0.08
    for s_ in (-1, 1):
        if blink:
            cv.drawLine(x + s_ * 80 - 44, y, x + s_ * 80 + 44, y, P(0xFFFFFFFF, 8))
        else:
            cv.drawRect(skia.Rect.MakeXYWH(x + s_ * 80 - 48, y - 34, 96, 68), P(0xFFFFFFFF))
            cv.drawRect(skia.Rect.MakeXYWH(x + s_ * 80 + math.sin(t * 8) * 18 - 15, y - 17, 30, 36), P(0xFF000000))


def air_gauge(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1A22')), (1, h('04090C'))])
    cx, cy, r = 760, 640, 400
    for i in range(40):
        a0 = math.radians(180 + i * 4.5)
        col = Wd.mix(h('E5392F'), h('3DDC84'), i / 39)
        cv.drawLine(cx + math.cos(a0) * (r - 70), cy + math.sin(a0) * (r - 70), cx + math.cos(a0) * r, cy + math.sin(a0) * r, P(col, 26))
    ang = math.radians(180 + lerp(150, 20, k) + math.sin(t * 30) * 2)
    cv.drawLine(cx, cy, cx + math.cos(ang) * (r - 110), cy + math.sin(ang) * (r - 110), P(0xFFFFFFFF, 20))
    cv.drawCircle(cx, cy, 40, P(0xFFFFFFFF))
    Wd.text_card(cv, 'AIR', cx, cy + 150, 130, h('E5392F') if k > 0.6 and (t * 6) % 1 < 0.5 else 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'CO2 RISING', 1420, 420, 84, h('FFB000'), 0xFF000000)
    Wd.text_card(cv, 'about 60 hours', 1420, 520, 64, 0xFFFFFFFF, 0xFF000000)


def radio(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('101A24')), (1, h('05080C'))])
    cv.drawRoundRect(skia.Rect.MakeXYWH(260, 190, 1400, 560), 40, 40, P(h('1B2A38')))
    cv.drawRoundRect(skia.Rect.MakeXYWH(260, 190, 1400, 560), 40, 40, P(h('3DDC84'), 6))
    Wd.text_card(cv, 'SURFACE RADIO', 960, 270, 44, h('3DDC84'), None)
    n = 56
    for i in range(n):
        a = abs(math.sin(i * 0.9 + t * 14) * math.sin(i * 0.23 + t * 5)) * (0.25 + 0.75 * min(1, k * 3))
        x = 330 + i * (1260 / n)
        cv.drawLine(x, 470 - a * 150, x, 470 + a * 150, P(h('3DDC84'), 12))
    s = 1 + 0.5 * max(0, 1 - c.lt * 5)
    cv.save()
    cv.translate(960, 680)
    cv.scale(s, s)
    Wd.text_card(cv, "HE'S ALIVE!", 0, 0, 120, h('FFB000'), 0xFF000000)
    cv.restore()


def board_true(cv, c):
    cork(cv)
    card(cv, 700, 440, 640, 700, 2)
    cv.save()
    cv.translate(700, 440)
    cv.rotate(2)
    photo(cv, 'okene', 0, 20, 560, 580, (0.5, 0.2))
    cv.restore()
    k = min(1, max(0, (c.lt - 0.3) / 0.12))
    if c.lt > 0.3:
        cv.save()
        cv.translate(760, 560)
        cv.rotate(-14)
        cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
        cv.drawRoundRect(skia.Rect.MakeLTRB(-300, -110, 300, 110), 20, 20, P(h('E5392F'), 22))
        Wd.text_card(cv, 'TRUE', 0, 62, 180, h('E5392F'), None)
        cv.restore()
    card(cv, 1380, 330, 420, 240, -5, h('FFD866'))
    Wd.text_card(cv, '60 HOURS', 1380, 360, 64, INK, None)
    card(cv, 1420, 640, 460, 240, 4, h('F4EEDF'))
    Wd.text_card(cv, 'ONLY SURVIVOR', 1420, 670, 46, INK, None)


SHOTS = {f.__name__: f for f in (board_ship, blackout, air_gauge, radio, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=190, c=0x66CFE6FF, slant=0.3, speed=2300, length=64)


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 60, Wd.alpha(h('BFE6FF'), 0.28), 11, size=(2, 6), drift=(-14, -36), wobble=24)


def depth(cv, c):
    snow(cv, c)
    for i, m in enumerate((10, 20, 30)):
        y = 250 + i * 210
        on = c.k > (i + 0.55) / 3.3
        cv.drawLine(60, y, 190, y, P(h('FFB000') if on else 0x99FFFFFF, 6))
        Wd.text_card(cv, f'{m} m', 300, y + 22, 60, h('FFB000') if on else 0x99FFFFFF, 0xFF000000)


def x1(cv, c):
    k = min(1, max(0, (c.lt - 0.25) / 0.12))
    if c.lt > 0.25:
        cv.save()
        cv.translate(1380, 330)
        cv.scale(2 - k, 2 - k)
        Wd.text_card(cv, 'x1', 0, 60, 190, h('FFB000'), 0xFF000000)
        cv.restore()


def days(cv, c):
    a, b = c.prm.get('days', [1, 2])
    k = c.k
    n = a if k < 0.5 else b
    q = (k if k < 0.5 else k - 0.5) * 2
    cv.save()
    cv.translate(1300, 340)
    cv.rotate(-6)
    cv.scale(1 + 0.6 * max(0, 1 - q * 6), 1 + 0.6 * max(0, 1 - q * 6))
    Wd.text_card(cv, f'DAY {n}', 0, 0, 200, h('FFB000'), 0xFF000000)
    cv.restore()


def label(text, x=960, y=170, size=72, at=0.3):
    def f(cv, c):
        if c.lt > at:
            k = min(1, (c.lt - at) / 0.15)
            cv.save()
            cv.translate(x, y)
            cv.scale(1.3 - 0.3 * k, 1.3 - 0.3 * k)
            Wd.text_card(cv, text, 0, 0, size, h('FFB000'), 0xFF000000)
            cv.restore()
    return f


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1420, 330)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'CASE 001  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


def both(*fs):
    return lambda cv, c: [f(cv, c) for f in fs] and None


OVER = dict(tug_storm=rain, rook_buoy=rain, big_wave=rain, capsize=rain, sinking=depth, coke=x1, day_stamp=days, signoff=closed,
            dive_search=snow, hand_float=snow, pocket_wide=snow, rook_shrug=snow, rook_feathers=snow, light_leaves=snow,
            light_back=snow, rook_fair=snow, bell_up=snow, shadow_pass=snow, walk_out=snow,
            divers_down=snow,
            locked_doors=label('DOORS LOCKED: PIRATE WATERS', 960, 150, 60),
            platform_work=label('20 MILES OFF NIGERIA', 960, 150, 64),
            flashlights=label('x2', 1400, 320, 170, 0.5),
            chamber=label('DECOMPRESSION: 2 MORE DAYS', 960, 150, 60))


def THUMB(cv, c):
    """1280x720: the 3D still (hand, glove, Rook) + a three-word hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0B1A22'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(700, 0), (1280, 0)], [0x00000000, 0xCC000000])))
    Wd.text_card(cv, '3 DAYS', 1010, 230, 136, h('FFB000'), 0xFF000000)
    Wd.text_card(cv, 'UNDERWATER', 1010, 350, 74, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'ALIVE', 1010, 500, 136, h('3DDC84'), 0xFF000000)
