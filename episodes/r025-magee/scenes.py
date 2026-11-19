"""Case 025 - Alan Magee, the ball turret gunner who fell about 22,000 feet without a usable parachute on
3 January 1943 and crashed through the glass roof of the Saint-Nazaire railway station. The story is filmed in 3D
(world3d.py). This file holds the one flat insert (Rook's case board, iron and glass) and the 2D overlays drawn on
top of 3D shots (wind streaks, flak grit, falling glass glints, dust, snow, the sign-off). Every card is a drawing
made for this film; none of it reproduces a real photograph, document or emblem."""
import math
import os

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER = h('FF7A1A'), h('FFB000'), h('EFE6CC')


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
        cv.drawRect(dst, P(h('9CB2D0')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def board(cv, c):
    """Rook's board for this case: a sheet of riveted iron with a cracked pane of glass bolted over a photograph of the
    hole in the station roof, three facts chalked below."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A3E44')), (0.55, h('2A2E34')), (1, h('16181C'))])
    for x in (60, 1020):
        for y in range(160, 1800, 120):
            cv.drawCircle(x, y, 11, P(h('5A6068')))
            cv.drawCircle(x - 3, y - 3, 4, P(h('8A9098')))
    for y in (110, 1810):
        cv.drawRect(skia.Rect.MakeXYWH(30, y - 14, 1020, 28), P(h('24282C')))
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(540, 680)
    cv.scale(s, s)
    cv.rotate(2.0)
    cv.drawRect(skia.Rect.MakeXYWH(-380 + 12, -440 + 16, 760, 880), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-380, -440, 760, 880), P(PAPER))
    photo(cv, 'hole', 0, -40, 690, 720, (0.5, 0.5))
    cv.drawRect(skia.Rect.MakeXYWH(-345, -400, 690, 720), P(0x22BFE4F0))
    for i in range(7):                                             # cracks in the pane over the photograph
        a = 0.4 + i * 0.85
        L = 160 + 220 * rn(i, 3)
        cv.drawLine(120, -170, 120 + L * math.cos(a), -170 + L * math.sin(a), P(0xCCF4FAFF, 4))
    cv.restore()
    for x in (230, 850):
        cv.drawCircle(x, 270, 22, P(ORANGE))
        cv.drawCircle(x, 270, 22, P(INK, 5))
    if c.lt > 0.2:
        fit(cv, '22,000 FEET', 540, 1500, 120, 920, 0xFFFFFFFF)
    if c.lt > 0.4:
        fit(cv, 'NO PARACHUTE', 540, 1630, 120, 920, AMBER)
    if c.lt > 0.6:
        fit(cv, 'GLASS ROOF', 540, 1760, 110, 920, h('BFE4F0'))


SHOTS = {f.__name__: f for f in (board,)}


# ---------------------------------------------------------------- overlays on the 3D shots
def grit(cv, c):
    """Flak grit and sparks drifting past the lens."""
    Wd.particles(cv, W, H, c.t, 22, 0x99FFB040, 93, size=(2, 6), drift=(-60, 260), wobble=40, twinkle=True)
    Wd.particles(cv, W, H, c.t, 16, 0x66303034, 95, size=(4, 9), drift=(-90, 200), wobble=50)


def rush(cv, c):
    """Falling: streaks of air going up past the lens."""
    for i in range(22):
        x = W * rn(i, 11)
        y = H - ((c.t * (1500 + 900 * rn(i, 12)) + H * rn(i, 13)) % (H + 300))
        cv.drawLine(x, y, x + 6 * math.sin(i), y + 110 + 120 * rn(i, 14), P(h('F2F8FF'), 4, a=0.25))


def glints(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0xCCE8F8FF, 97, size=(2, 6), drift=(10, 420), wobble=20, twinkle=True)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x55FFF0D8, 99, size=(2, 5), drift=(12, -16), wobble=16, twinkle=True)


def snow(cv, c):
    Wd.particles(cv, W, H, c.t, 46, 0xCCF4F8FF, 101, size=(3, 8), drift=(26, 150), wobble=30)


def closed(cv, c):
    dust(cv, c)
    if c.lt > 0.4:
        k = min(1, (c.lt - 0.4) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 025', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(turret_close=grit, chute_rags=dust, bomber_down=grit, roof_rush=rush, rook_ridge=dust, formation=grit, flak_hit=grit,
            turret_climb=dust, chute_find=dust, rook_silk=dust, gasp_dim=dust, thrown_clear=grit, fall_wide=rush, rook_dive=rush,
            town_below=rush, rook_look=dust, smash=glints, shards=glints, hole_up=dust, found=dust, rook_shard=dust, stretcher=dust,
            doctor=dust, rook_bed=dust, camp=snow, memorial=dust, wreath=dust, signoff=closed)
