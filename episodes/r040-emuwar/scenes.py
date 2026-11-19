"""Case 040 - the Emu War, Western Australia, November to December 1932. The story is filmed in 3D (world3d.py).
This file holds the one flat insert (Rook's case board: a sheet of corrugated iron with a photograph of the mob at the
dam and the major's own figures painted under it, with Rook's question mark) and the 2D overlays drawn on top of 3D
shots (wheat chaff on the wind, road grit behind the truck, lamp-lit dust in the tent, the sign-off). Every card is a
drawing made for this film; none of it reproduces a real photograph, document, newspaper or emblem."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER, CHALK = h('FF7A1A'), h('FFB000'), h('EFE6CC'), h('F4F0E6')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rn(i, j=0):
    return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('C8A860')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def board(cv, c):
    """Rook's board for this case: a sheet of corrugated iron, a photograph of the mob at the dam pinned to it, and the
    major's figures painted underneath. The question mark is Rook's, not the major's."""
    for i in range(0, W, 60):                                                    # corrugations
        cv.drawRect(skia.Rect.MakeXYWH(i, 0, 30, H), P(h('8A9096')))
        cv.drawRect(skia.Rect.MakeXYWH(i + 30, 0, 30, H), P(h('6E757C')))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.6, 0x10000000), (1, 0x66000000)])
    for i in range(14):                                                          # rust
        cv.drawCircle(W * rn(i, 1), H * rn(i, 2), 30 + 70 * rn(i, 3), P(h('9A5A36'), a=0.18))
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 470)
    cv.scale(s * 0.95, s * 0.95)
    cv.rotate(-2.0)
    cv.drawRect(skia.Rect.MakeXYWH(-380 + 14, -320 + 18, 760, 640), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-380, -320, 760, 640), P(PAPER))
    photo(cv, 'mob', 0, -20, 690, 540, (0.5, 0.5))
    cv.restore()
    cv.drawCircle(540, 172, 20, P(ORANGE))
    cv.drawCircle(540, 172, 20, P(INK, 5))
    if c.lt > 0.15:                                        # all text stays above the caption band (62-78 % of the height)
        fit(cv, '986 BIRDS', 540, 920, 96, 860, CHALK)
    if c.lt > 0.35:
        fit(cv, '9,860 ROUNDS', 540, 1030, 96, 860, CHALK)
    if c.lt > 0.6:
        g = ease((c.lt - 0.6) / 0.15)
        cv.save()
        cv.translate(540, 1140)
        cv.scale(1.25 - 0.25 * g, 1.25 - 0.25 * g)
        fit(cv, '= 10 EACH?', 0, 0, 96, 860, AMBER)
        cv.restore()


SHOTS = {f.__name__: f for f in (board,)}


# ---------------------------------------------------------------- overlays on the 3D shots
def chaff(cv, c):
    """Bits of wheat chaff and dust on the wind."""
    Wd.particles(cv, W, H, c.t, 26, 0x88F0D890, 141, size=(2, 6), drift=(90, 20), wobble=40, twinkle=False)


def grit(cv, c):
    """Road grit and dust thrown past the lens behind the truck."""
    Wd.particles(cv, W, H, c.t, 34, 0x99C8A070, 143, size=(3, 8), drift=(-260, 60), wobble=50, twinkle=False)
    chaff(cv, c)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x66FFE0A8, 145, size=(2, 5), drift=(10, -14), wobble=16, twinkle=True)


def glow(cv, c):
    """Sunset motes over the fence."""
    Wd.particles(cv, W, H, c.t, 24, 0x77FFC080, 147, size=(2, 5), drift=(30, -10), wobble=20, twinkle=True)


def closed(cv, c):
    glow(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(540, 360)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 040', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(dam_mob=chaff, gun_hide=chaff, gunner_eyes=chaff, jam=chaff, rook_jam=chaff, wheat_raid=chaff, wheat_eat=chaff,
            truck_mount=chaff, truck_chase=grit, emu_legs=grit, rook_truck=grit, press_drop=motes, rook_paper=motes, pack_up=grit,
            major_report=motes, emu_tank=chaff, farmers_ask=chaff, round_two=grit, weeks_sun=chaff, recalled=chaff, ledger=motes,
            casings=motes, rook_tens=motes, rook_squint=motes, asked_no=chaff, fence_build=chaff, fence_face=glow, rook_question=closed)
