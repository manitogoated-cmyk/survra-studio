"""Case 023, the full case file (16:9) - Annette Herfkens, eight days beside the wreck of Vietnam Airlines Flight 474, 1992.
The story is filmed in 3D (world3d.py). This file holds the flat inserts on a 1920x1080 canvas (a drawn newspaper column of
black-bordered notices, and Rook's case board), the 2D overlays drawn on top of 3D shots, and the thumbnail. Both cards are
drawings made for this film: the notices carry lines only, no names and no wording, and are not a copy of any real page.
Captions run in a band low in the frame and the label sits top right, so the cards keep both clear."""
import math
import os

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1920, 1080
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
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def plain(cv, s, x, y, size, color, weight=700):
    f = font(size, weight)
    w = f.measureText(s)
    cv.drawTextBlob(skia.TextBlob(s, f), x - w / 2, y, P(color))


def push(cv, c, amount=0.1, sway=0.0):
    """A slow push in on a card (and a little sway), so a held card is never a still picture."""
    z = 1 + amount * c.k
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.rotate(sway * math.sin(c.t * 1.3))
    cv.translate(-W / 2 + 26 * math.sin(c.t * 0.9), -H / 2 + 14 * math.sin(c.t * 1.4))


# ---------------------------------------------------------------- inserts
def notice_card(cv, c):
    """Death notices had been published. A drawn newspaper column on a table: black-bordered boxes holding grey lines, no
    names and no wording. The page slides in; then a stamp comes down across it: SHE WAS ALIVE."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A2420')), (0.5, h('1E1A16')), (1, h('120F0C'))])
    cv.save()
    push(cv, c, 0.1, 0.4)
    k = ease(min(1, c.lt / 0.3))
    cv.translate(960 - 120 * (1 - k), 470)
    cv.rotate(-3.0)
    cv.drawRect(skia.Rect.MakeXYWH(-700 + 16, -420 + 20, 1400, 840), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-700, -420, 1400, 840), P(h('E4DCC6')))
    cv.drawRect(skia.Rect.MakeXYWH(-660, -385, 1320, 54), P(h('2A2622')))             # the masthead: a plain bar, no title
    for col in range(4):                                                                # columns of grey text lines
        x0 = -660 + 335 * col
        y = -300
        j = 0
        while y < 380:
            boxed = (col + j) % 3 == 1
            hh = 150 + 60 * rn(col, j) if boxed else 90 + 80 * rn(col, j + 7)
            if y + hh > 390:
                break
            if boxed:                                                                   # a black-bordered notice
                cv.drawRect(skia.Rect.MakeXYWH(x0, y, 310, hh), P(INK, 9))
                cv.drawRect(skia.Rect.MakeXYWH(x0 + 85, y + 22, 140, 12), P(h('2A2622')))
                n = int((hh - 60) / 22)
                for i in range(n):
                    wd = 250 - 90 * rn(col * 7 + j, i) if i < n - 1 else 120
                    cv.drawRect(skia.Rect.MakeXYWH(x0 + 155 - wd / 2, y + 52 + 22 * i, wd, 7), P(h('6A6258')))
            else:
                for i in range(int(hh / 18)):
                    wd = 310 - 70 * rn(col * 5 + j, i + 3)
                    cv.drawRect(skia.Rect.MakeXYWH(x0, y + 18 * i, wd, 6), P(h('9A9284')))
            y += hh + 26
            j += 1
    cv.restore()
    if c.k > 0.25:
        fit(cv, 'DEATH NOTICES', 960, 150, 84, 1100, 0xFFFFFFFF)
    if c.k > 0.6:
        q = 1.6 - 0.6 * ease((c.k - 0.6) / 0.1)
        cv.save()
        cv.translate(960, 500)
        cv.rotate(-9)
        cv.scale(q, q)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-470, -100, 940, 180), 18, 18, P(h('C8321E'), 14))
        plain(cv, 'SHE WAS ALIVE', 0, 48, 112, h('C8321E'), 900)
        cv.restore()
    Wd.particles(cv, W, H, c.t, 18, 0x44FFE8C8, 91, size=(2, 5), drift=(10, -14), wobble=14, twinkle=True)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) set into the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('6A8A78')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def leaf(cv, x, y, s, ang, col):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    cv.drawPath(poly([(0, -90), (34, -30), (30, 30), (0, 95), (-30, 30), (-34, -30)]), P(col))
    cv.drawLine(0, -86, 0, 120, P(h('1E3A22'), 5))
    for i in range(3):
        cv.drawLine(0, -40 + 40 * i, 26, -60 + 40 * i, P(h('1E3A22'), 3))
        cv.drawLine(0, -40 + 40 * i, -26, -60 + 40 * i, P(h('1E3A22'), 3))
    cv.restore()


def board(cv, c):
    """Rook's board for this case: a sheet of dull riveted aluminium, a photograph of the balls of insulation on the wet
    wing pinned to it with a jungle leaf, and the case in three lines."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A2420')), (1, h('0C1210'))])
    cv.save()
    push(cv, c, 0.07, 0.4)
    cv.drawRect(skia.Rect.MakeXYWH(40, 40, 1840, 1000), P(h('8E979C')))
    for i in range(5):                                                                 # panel seams
        cv.drawLine(40 + 368 * i, 40, 40 + 368 * i, 1040, P(h('6E777C'), 5))
    for j in range(3):
        cv.drawLine(40, 40 + 500 * j, 1880, 40 + 500 * j, P(h('6E777C'), 5))
    for i in range(26):                                                                # rivets
        for y in (62, 520, 1018):
            cv.drawCircle(64 + 71.5 * i, y, 7, P(h('C4CCD0')))
            cv.drawCircle(64 + 71.5 * i, y, 7, P(h('5A6368'), 2))
    for i in range(40):                                                                # scratches
        x, y = 60 + 1800 * rn(i, 1), 60 + 960 * rn(i, 2)
        cv.drawLine(x, y, x + 120 * rn(i, 3), y + 30 * rn(i, 4) - 15, P(h('A8B0B4'), 2, a=0.5))
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(600, 440)
    cv.scale(s, s)
    cv.rotate(-2.5)
    cv.drawRect(skia.Rect.MakeXYWH(-390 + 12, -320 + 16, 780, 640), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-390, -320, 780, 640), P(PAPER))
    photo(cv, 'wing', 0, -12, 720, 560, (0.5, 0.5))
    cv.restore()
    leaf(cv, 930, 150, 1.0, 28, h('3A7A3A'))
    cv.drawCircle(600, 130, 22, P(ORANGE))
    cv.drawCircle(600, 130, 22, P(INK, 5))
    if c.lt > 0.25:
        fit(cv, '8 DAYS', 1340, 320, 120, 620, 0xFFFFFFFF)
    if c.lt > 0.5:
        fit(cv, 'RAINWATER ONLY', 1340, 470, 84, 620, AMBER)
    if c.lt > 0.75:
        fit(cv, 'ONE SURVIVOR', 1340, 610, 84, 620, 0xFFFFFFFF)
    if c.lt > 1.1:
        q = 1.5 - 0.5 * ease((c.lt - 1.1) / 0.12)
        cv.save()
        cv.translate(900, 720)
        cv.rotate(-12)
        cv.scale(q, q)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-170, -78, 340, 132), 14, 14, P(h('2E9A4E'), 12))
        plain(cv, 'TRUE', 0, 34, 110, h('2E9A4E'), 900)
        cv.restore()
    cv.restore()


SHOTS = {f.__name__: f for f in (notice_card, board)}


# ---------------------------------------------------------------- overlays on the 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=150, c=0x66CFE6FF, slant=0.22, speed=2100, length=58)


def storm(cv, c):
    Wd.rain(cv, W, H, c.t, density=210, c=0x77CFE6FF, slant=0.35, speed=2600, length=70)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, density=70, c=0x44CFE6FF, slant=0.15, speed=1700, length=40)


def thinning(cv, c):
    """The rain thins out over the shot."""
    Wd.rain(cv, W, H, c.t, density=int(150 * (1 - 0.85 * c.k)) + 4, c=0x66CFE6FF, slant=0.2, speed=2000, length=52)


def motes(cv, c):
    Wd.particles(cv, W, H, c.t, 30, 0x55FFF4D0, 231, size=(2, 6), drift=(12, -16), wobble=20, twinkle=True)


def mist(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x44FFF0D8, 233, size=(3, 7), drift=(10, -10), wobble=16, twinkle=True)


def fireflies(cv, c):
    Wd.particles(cv, W, H, c.t, 26, 0xCCE8FF90, 235, size=(3, 7), drift=(8, -14), wobble=40, twinkle=True)


def dust(cv, c):
    Wd.particles(cv, W, H, c.t, 24, 0x44FFE8C8, 237, size=(2, 5), drift=(10, -12), wobble=14, twinkle=True)


def heat(cv, c):
    Wd.particles(cv, W, H, c.t, 22, 0x44FFF8E0, 239, size=(2, 5), drift=(26, -8), wobble=22, twinkle=True)


def leaves(cv, c):
    Wd.particles(cv, W, H, c.t, 20, 0xAAE0A030, 241, size=(5, 10), drift=(70, 90), wobble=50)


def closed(cv, c):
    motes(cv, c)
    if c.lt > 0.45:
        k = min(1, (c.lt - 0.45) / 0.15)
        cv.save()
        cv.translate(430, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 130, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 023', 0, 80, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(crash_ridge=storm, wreck_wide=rain, wing_torn=rain, rook_doubt=rain, rook_hatoff=rain, man_beside=drizzle, her_alone=rain,
            thirst_face=motes, wing_pov=motes, rook_squeeze=motes, elbow_crawl=motes, tuft_pull=motes, rook_nod=motes, rain_arrives=storm,
            tuft_drink=rain, officer_trees=mist, officer_ghost=mist, rook_brim=mist, carry_down=motes, night_wreck=fireflies,
            calm_face=fireflies, rook_vigil=fireflies, rook_wreck=motes, carry_light=mist, signoff=closed,
            desk_trade=dust, pasje_desk=dust, apron_wide=heat, apron_meet=heat, apron_stairs=heat, rook_apron=heat, cabin_flight=dust,
            cabin_drop=dust, belt_empty=drizzle, her_looks=drizzle, trousers=rain, man_talks=rain, her_resolve=thinning, sip_wait=motes,
            swat=motes, move_away=motes, sky_gap=motes, orange_man=mist, orange_gone=mist, men_arrive=mist, list_point=motes,
            ward_bed=dust, walk_again=dust, jaime_phone=dust, funeral_aisle=dust, funeral_close=dust, funeral_rook=dust, desk_back=dust,
            family_walk=leaves, return_ridge=motes, writing=dust)


def THUMB(cv, c):
    """1280x720: the 3D still (she sits against a root beside the wreck in the rain, on the right) and the hook on the left,
    over the dark trees."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('14201A'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear([(700, 0), (0, 0)], [0x00000000, 0xD0000000])))
    fit(cv, '8 DAYS', 310, 250, 170, 540, AMBER)
    fit(cv, 'ALONE', 310, 410, 150, 540, 0xFFFFFFFF)
    fit(cv, 'BY THE WRECK', 310, 530, 76, 540, 0xFFFFFFFF)
