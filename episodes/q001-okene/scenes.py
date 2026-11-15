"""Case 001 - Harrison Okene. The story itself is filmed in 3D (world3d.py). This file holds the flat graphic
inserts (case board, blackout, air gauge) and the 2D overlays drawn on top of 3D shots (rain, stamps, depth marks)."""
import math
import os

import skia

from concepts.chars import INK, P, fs, oval, poly
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) pinned to the board as a photograph."""
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
    sx, sy = (iw - sw) * focus[0], (ih - sh) * focus[1]
    cv.drawImageRect(img, skia.Rect.MakeXYWH(sx, sy, sw, sh), dst, skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def cork(cv):
    Wd.fill(cv, 0, 0, W, H, h('9A6E44'))
    R = Wd.Rand(4)
    for i in range(160):
        cv.drawCircle(R(0, W), R(0, H), R(2, 6), P(Wd.alpha(h('6E4A2A'), 0.5)))
    cv.drawRect(skia.Rect.MakeLTRB(20, 20, W - 20, H - 20), P(h('4A2F1A'), 40))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x55000000)])


def card(cv, x, y, w_, h_, ang, col=0xFFF4EEDF, pin=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 10, -h_ / 2 + 14, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if pin:
        cv.drawCircle(4, -h_ / 2 + 26, 16, P(0x66000000))
        cv.drawCircle(0, -h_ / 2 + 22, 15, P(h('E5392F')))
        cv.drawCircle(-4, -h_ / 2 + 18, 5, P(h('FF8A80')))
    cv.restore()


def board_ship(cv, c):
    cork(cv)
    k = min(1, c.lt / 0.25)
    s = 0.7 + 0.3 * (1 - (1 - k) ** 3)
    card(cv, 520, 800, 780 * s, 700 * s, -3)
    cv.save()
    cv.translate(520, 800)
    cv.rotate(-3)
    cv.scale(s, s)
    photo(cv, 'tug', 0, 20, 700, 560, (0.5, 0.62))
    cv.restore()
    k2 = min(1, max(0, (c.lt - 0.35) / 0.15))
    if k2 > 0:
        cv.drawLine(520, 470, lerp(520, 800, k2), lerp(470, 1210, k2), P(h('E5392F'), 8))
        cv.save()
        cv.translate(800, 1330)
        cv.scale(1 + 0.5 * (1 - k2), 1 + 0.5 * (1 - k2))
        card(cv, 0, 0, 360, 260, 6, h('FFD866'))
        cv.rotate(6)
        Wd.text_card(cv, '3 DAYS', 0, 40, 84, INK, None)
        cv.restore()


def blackout(cv, c):
    t, k = c.t, c.k
    Wd.fill(cv, 0, 0, W, H, 0xFF000000)

    def eyes(x, y, col, s, lookx, blink):
        for s_ in (-1, 1):
            if blink:
                cv.drawLine(x + s_ * 70 * s - 40 * s, y, x + s_ * 70 * s + 40 * s, y, P(col, 8))
            else:
                cv.drawRect(skia.Rect.MakeXYWH(x + s_ * 70 * s - 44 * s, y - 32 * s, 88 * s, 64 * s), P(col))
                cv.drawRect(skia.Rect.MakeXYWH(x + s_ * 70 * s + lookx * 16 * s - 14 * s, y - 16 * s, 28 * s, 34 * s), P(0xFF000000))
    Wd.particles(cv, W, H, t * 3, 50, Wd.alpha(h('BFE6FF'), 0.3), 7, size=(2, 5), drift=(-40, -30), wobble=20)
    eyes(380 + math.sin(t * 9) * 30, 980 + math.cos(t * 7) * 16, 0xFFFFFFFF, 1.0, math.sin(t * 8), (t * 1.7) % 1 < 0.08)
    if k > 0.5:
        for s_ in (-1, 1):
            cv.save()
            cv.translate(740 + s_ * 62, 900)
            cv.rotate(s_ * -12)
            cv.drawRect(skia.Rect.MakeXYWH(-46, -18, 92, 36), P(h('FFB000')))
            cv.drawRect(skia.Rect.MakeXYWH(-34 - 10, -12, 26, 26), P(0xFF000000))
            cv.restore()


def air_gauge(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1A22')), (1, h('04090C'))])
    cx, cy, r = 540, 1080, 400
    for i in range(40):
        a0 = math.radians(180 + i * 4.5)
        col = Wd.mix(h('E5392F'), h('3DDC84'), i / 39)
        cv.drawLine(cx + math.cos(a0) * (r - 70), cy + math.sin(a0) * (r - 70), cx + math.cos(a0) * r, cy + math.sin(a0) * r, P(col, 26))
    ang = math.radians(180 + lerp(128, 14, k) + math.sin(t * 30) * 2)
    cv.drawLine(cx, cy, cx + math.cos(ang) * (r - 110), cy + math.sin(ang) * (r - 110), P(0xFFFFFFFF, 20))
    cv.drawCircle(cx, cy, 40, P(0xFFFFFFFF))
    Wd.text_card(cv, 'AIR', cx, cy + 230, 170, h('E5392F') if k > 0.6 and (t * 6) % 1 < 0.5 else 0xFFFFFFFF, 0xFF000000)


def board_true(cv, c):
    cork(cv)
    card(cv, 540, 820, 720, 860, 2)
    cv.save()
    cv.translate(540, 820)
    cv.rotate(2)
    photo(cv, 'okene', 0, 20, 640, 720, (0.5, 0.12))
    cv.restore()
    k = min(1, max(0, (c.lt - 0.25) / 0.12))
    if c.lt > 0.25:
        cv.save()
        cv.translate(560, 1010)
        cv.rotate(-14)
        cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k)
        cv.drawRoundRect(skia.Rect.MakeLTRB(-300, -110, 300, 110), 20, 20, P(h('E5392F'), 22))
        Wd.text_card(cv, 'TRUE', 0, 62, 180, h('E5392F'), None)
        cv.restore()
    card(cv, 300, 1500, 330, 210, -5, h('FFD866'))
    Wd.text_card(cv, '60 HOURS', 300, 1530, 56, INK, None)


SHOTS = {f.__name__: f for f in (board_ship, blackout, air_gauge, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=150, c=0x66CFE6FF, slant=0.3, speed=2300, length=64)


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 46, Wd.alpha(h('BFE6FF'), 0.28), 11, size=(2, 6), drift=(-14, -36), wobble=24)


def depth(cv, c):
    snow(cv, c)
    for i, m in enumerate((10, 20, 30)):
        y = 520 + i * 330
        on = c.k > (i + 0.55) / 3.3
        cv.drawLine(40, y, 150, y, P(h('FFB000') if on else 0x99FFFFFF, 6))
        Wd.text_card(cv, f'{m} m', 250, y + 22, 60, h('FFB000') if on else 0x99FFFFFF, 0xFF000000)


def x1(cv, c):
    k = min(1, max(0, (c.lt - 0.25) / 0.12))
    if c.lt > 0.25:
        cv.save()
        cv.translate(850, 470)
        cv.scale(2 - k, 2 - k)
        Wd.text_card(cv, 'x1', 0, 60, 190, h('FFB000'), 0xFF000000)
        cv.restore()


def days(cv, c):
    k = c.k
    n = 1 if k < 0.5 else 2
    a = (k if k < 0.5 else k - 0.5) * 2
    cv.save()
    cv.translate(540, 470)
    cv.rotate(-6)
    cv.scale(1 + 0.6 * max(0, 1 - a * 6), 1 + 0.6 * max(0, 1 - a * 6))
    Wd.text_card(cv, f'DAY {n}', 0, 0, 220, h('FFB000'), 0xFF000000)
    cv.restore()


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'CASE 001  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(tug_storm=rain, rook_buoy=rain, big_wave=rain, capsize=rain, sinking=depth, coke=x1, day_stamp=days, signoff=closed,
            dive_search=snow, hand_float=snow, pocket_wide=snow, rook_shrug=snow, rook_feathers=snow, light_leaves=snow,
            light_back=snow, rook_fair=snow, bell_up=snow)
