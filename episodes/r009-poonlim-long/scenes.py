"""Case 009, the full case file - Poon Lim. The story is filmed in 3D (world3d.py). This file holds the flat
inserts on a 1920x1080 canvas (Rook's case board on a sea chart, the knotted-cord counter, the crew file, three
sketch maps, the raft's stores, the food and water bars, the two readings of the freighter, the scale, the manual
page, the quota form, the certificate, the record card), the 2D overlays drawn on top of 3D shots, and the
thumbnail. Every card that looks like a document is an illustration and says so; none is a real document."""
import math
import os

import skia

from concepts.chars import INK, P, poly
from engine3 import world as Wd

W, H = 1920, 1080
h = Wd.hexc
T = Wd.text_card
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
_IMG = {}
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F1E6CC'), h('D8362A'), h('2E9A5A')
WHITE, BLACK = 0xFFFFFFFF, 0xFF000000


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def pop(lt, t0, d=0.14):
    return ease((lt - t0) / d)


def font(size, weight=900):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=WHITE, stroke=BLACK, center=True):
    """Text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return T(cv, s, x, y, size, color, stroke, center=center)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) pinned to the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('7EC0EE')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def chart(cv, t=0.0):
    """Rook's board for this case: an old sea chart, soundings and a compass rose."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1C4A5E')), (1, h('0E2C3C'))])
    for i in range(1, 15):
        cv.drawLine(i * 135, 0, i * 135, H, P(0x2EBFE6F2, 2))
    for i in range(1, 8):
        cv.drawLine(0, i * 135, W, i * 135, P(0x2EBFE6F2, 2))
    R = Wd.Rand(9)
    f = skia.Font(skia.Typeface('Inter'), 24)
    for i in range(54):
        cv.drawString(str(int(R(12, 4800))), R(30, W - 90), R(60, H - 40), f, skia.Paint(Color=0x44BFE6F2, AntiAlias=True))
    cx, cy = 1700, 830
    for i in range(16):
        a = i * math.pi / 8
        r = 140 if i % 4 == 0 else (100 if i % 2 == 0 else 66)
        cv.drawLine(cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r, P(0x66F1E6CC, 5 if i % 4 == 0 else 3))
    cv.drawCircle(cx, cy, 106, P(0x55F1E6CC, 4))
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(h('0A1C26'), 32))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x33000000), (0.5, 0x00000000), (1, 0x66000000)])


def sea(cv, top='1C5A72', bot='0E3446'):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])


def card(cv, x, y, w_, h_, ang, col=PAPER, tape=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if tape:
        cv.drawRect(skia.Rect.MakeXYWH(-70, -h_ / 2 - 22, 140, 44), P(0xCCFFB000))
    cv.restore()


def note(cv, s, x, y, w_, h_, ang, size, col=h('FFD866'), k=1.0):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 10, -h_ / 2 + 12, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    fit(cv, s, 0, size * 0.36, size, w_ - 40, INK, None)
    cv.restore()


def stamp(cv, s, x, y, ang, k, size=150, col=RED, back=0xEE0E2C3C):
    """A rubber stamp that slams down (k 0..1)."""
    if k <= 0:
        return
    tw = font(size).measureText(s)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    sc = 2.3 - 1.3 * k
    cv.scale(sc, sc)
    r = skia.Rect.MakeLTRB(-tw / 2 - 40, -size * 0.72, tw / 2 + 40, size * 0.42)
    cv.drawRoundRect(r, 16, 16, P(back))
    cv.drawRoundRect(r, 16, 16, P(col, 14))
    T(cv, s, 0, size * 0.18, size, col, None)
    cv.restore()


def sketch_note(cv, s, y=842):
    T(cv, s, W / 2, y, 30, 0xCCFFFFFF, None)


def sheet(cv, x, y, w_, h_, ang, k, head, head_col=h('2A4658'), col=h('E6D3A6')):
    """A sheet of paper that slides up; leaves the canvas translated to its centre (caller restores)."""
    cv.save()
    cv.translate(x, y + 600 * (1 - k))
    cv.rotate(ang)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), 18, 18, P(0x66000000))
    cv.drawRoundRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), 18, 18, P(col))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, 96), P(head_col))
    fit(cv, head, 0, -h_ / 2 + 68, 58, w_ - 60, PAPER, None)


# ------------------------------------------------------------------ flat inserts
def tally_133(cv, c):
    """He counted days with knots in a cord (and later by the moon): the count runs up to 133."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C2233')), (1, h('05101A'))])
    n = int(round(133 * ease(c.k / 0.72)))
    for row in range(7):
        y = 90 + row * 44 if row < 3 else 640 + (row - 3) * 44
        cv.drawLine(110, y, W - 110, y + 8 * math.sin(row * 1.7), P(h('C9B48A'), 8))
        for i in range(19):
            idx = row * 19 + i
            if idx < n:
                x = 150 + i * 90
                yy = y + 8 * math.sin(row * 1.7) * (x - 110) / (W - 220)
                cv.drawCircle(x, yy, 13, P(h('E4D2A6')))
                cv.drawCircle(x, yy, 13, P(h('6E5C3A'), 4))
    pp = 1 + 0.25 * max(0.0, 1 - abs(c.k - 0.74) / 0.1)
    cv.save()
    cv.translate(780, 420)
    cv.scale(pp, pp)
    T(cv, str(n), 0, 90, 320, AMBER if n >= 133 else WHITE, BLACK)
    cv.restore()
    T(cv, 'DAYS', 1260, 500, 150, WHITE, BLACK)


def board_no(cv, c):
    chart(cv)
    k = min(1, c.lt / 0.22)
    s = 0.72 + 0.28 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(640, 440)
    cv.scale(s, s)
    card(cv, 0, 0, 860, 600, -3)
    cv.rotate(-3)
    photo(cv, 'raft', 0, 8, 800, 520, (0.5, 0.6))
    cv.restore()
    k2 = pop(c.lt, 0.3)
    if k2 > 0:
        cv.drawLine(1040, 300, lerp(1040, 1330, k2), lerp(300, 250, k2), P(RED, 7))
        note(cv, '133 DAYS', 1480, 250, 420, 170, 5, 80, k=k2)
    k3 = pop(c.lt, 0.5)
    if k3 > 0:
        cv.drawLine(1040, 520, lerp(1040, 1330, k3), lerp(520, 520, k3), P(RED, 7))
        note(cv, 'ALONE', 1470, 520, 340, 170, -6, 80, h('BFE0EC'), k3)
    if c.k > 0.7:
        stamp(cv, 'NO CHANCE', 760, 470, -12, min(1, (c.k - 0.7) / 0.1), 140)


def id_card(cv, c):
    """Crew file. The portrait is a drawn silhouette, not a photograph of him; the card is an illustration."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('10283A')), (1, h('081620'))])
    k = ease(c.lt / 0.22)
    sheet(cv, 960, 440, 1300, 700, -1.5, k, 'CREW FILE')
    cv.drawRect(skia.Rect.MakeXYWH(-590, -220, 330, 400), P(h('B8C8CC')))
    cv.drawRect(skia.Rect.MakeXYWH(-590, -220, 330, 400), P(INK, 6))
    cv.drawCircle(-425, -70, 82, P(h('3A4A56')))
    cv.drawPath(poly([(-560, 180), (-540, 50), (-470, 14), (-380, 14), (-310, 50), (-290, 180)]), P(h('3A4A56')))
    for i, (lab, val) in enumerate((('NAME', 'POON LIM'), ('RATING', '2ND STEWARD'), ('BORN', 'HAINAN, CHINA, 1918'))):
        y = -190 + i * 124
        T(cv, lab, -200, y, 32, h('7A6A48'), None, center=False)
        if c.lt > 0.3 + i * 0.25:
            fit(cv, val, -200, y + 62, 60, 760, INK, None, center=False)
    cv.drawLine(-200, 186, 590, 186, P(h('7A6A48'), 4))
    T(cv, 'SHIP', -200, 226, 32, h('7A6A48'), None, center=False)
    if c.lt > 1.1:
        T(cv, 'SS BENLOMOND', -200, 296, 70, h('2A4658'), None, center=False)
    cv.restore()
    sketch_note(cv, 'ILLUSTRATION: THE PORTRAIT IS A DRAWN SILHOUETTE')


CHINA = [(104, 26), (104, 22.6), (106.7, 21.9), (108, 21.6), (109.2, 21.5), (109.7, 21.5), (109.9, 20.5), (110.3, 20.3), (110.6, 20.6), (110.4, 21.3),
         (111.6, 21.5), (113, 22.1), (114.3, 22.4), (116, 23), (117.4, 23.8), (118.4, 26)]
HAINAN = [(108.7, 19.3), (109.2, 19.9), (110.0, 20.05), (110.7, 20.1), (111.0, 19.6), (110.6, 18.9), (110.0, 18.4), (109.5, 18.2), (108.8, 18.5), (108.6, 19.0)]


def hainan(cv, c):
    """Sketch of the south coast of China and Hainan island. prm home: the second visit, for the fins."""
    sea(cv)
    px = lambda lon, lat: (960 + (lon - 110.6) * 150, 500 - (lat - 20.6) * 150)
    for pts, col in ((CHINA, 'D8C890'), (HAINAN, 'E8D49A')):
        path = poly([px(*p) for p in pts])
        cv.drawPath(path, P(h(col)))
        cv.drawPath(path, P(h('5E4E2A'), 6))
    T(cv, 'CHINA', px(110, 23.4)[0], px(110, 23.4)[1], 110, h('5E4E2A'), None)
    T(cv, 'SOUTH CHINA SEA', px(113.6, 19.4)[0], px(113.6, 19.4)[1], 44, 0x88DFF4FF, None)
    hx, hy = px(109.8, 19.2)
    k = pop(c.lt, 0.25, 0.2)
    if k > 0:
        cv.drawCircle(hx, hy, 150 + 40 * ((c.t * 1.5) % 1), P(Wd.alpha(AMBER, 1 - (c.t * 1.5) % 1), 8))
        cv.drawCircle(hx, hy, 150, P(AMBER, 8))
        cv.save()
        cv.translate(480, 420)
        cv.scale(1.5 - 0.5 * k, 1.5 - 0.5 * k)
        T(cv, 'HAINAN', 0, 0, 150, AMBER, BLACK)
        T(cv, 'HOME' if c.prm.get('home') else 'BORN 1918', 0, 110, 84, WHITE, BLACK)
        cv.restore()
        cv.drawLine(700, 470, hx - 150, hy - 20, P(AMBER, 7))
    sketch_note(cv, 'SKETCH MAP, NOT TO SCALE')


AFRICA = [(-17, 16), (-17, 12), (-13, 8), (-8, 4.5), (-2, 5), (3, 6.3), (9, 4), (9, -1), (12, -6), (13.5, -12), (12, -17), (14.5, -23), (17, -29),
          (18.4, -34.3), (20, -34.8), (27, -34), (27, 16)]
SAMER = [(-70, 12), (-62, 10.7), (-57, 6), (-55.2, 5.9), (-52, 4.6), (-50, 0.5), (-48, -0.7), (-44, -2.7), (-38.5, -3.7), (-35, -5.5), (-35, -9), (-39, -14),
         (-39, -18), (-41, -22), (-48, -25.5), (-48.5, -28), (-53, -34), (-58, -38.5), (-62, -41), (-70, -41)]


def map_route(cv, c):
    """Sketch of the South Atlantic: Cape Town toward Suriname, and where she was sunk. Not to scale."""
    sea(cv)
    px = lambda lon, lat: (960 + (lon + 20) * 19.5, 420 - (lat + 13) * 19.5)
    for pts in (AFRICA, SAMER):
        path = poly([px(*p) for p in pts])
        cv.drawPath(path, P(h('D8C890')))
        cv.drawPath(path, P(h('5E4E2A'), 6))
    cv.drawLine(0, px(0, 0)[1], W, px(0, 0)[1], P(0x55BFE6F2, 3))
    T(cv, 'EQUATOR', 960, px(0, 0)[1] - 12, 26, 0x99BFE6F2, None)
    T(cv, 'AFRICA', px(19, -8)[0], px(19, -8)[1], 64, h('5E4E2A'), None)
    T(cv, 'SOUTH AMERICA', px(-56, -12)[0], px(-56, -12)[1], 56, h('5E4E2A'), None)
    T(cv, 'SOUTH ATLANTIC', px(-12, -26)[0], px(-12, -26)[1], 44, 0x88DFF4FF, None)
    a, x_, b = px(18.4, -33.9), px(-38.75, 0.5), px(-55.2, 5.9)
    k = ease(c.k / 0.62)
    for i in range(30):
        u = i / 29
        if u > k:
            break
        cv.drawCircle(lerp(a[0], x_[0], u), lerp(a[1], x_[1], u) - 40 * math.sin(u * math.pi), 8, P(WHITE))
    cv.drawCircle(a[0], a[1], 16, P(AMBER))
    fit(cv, 'CAPE TOWN', a[0] - 30, a[1] + 78, 54, 420, WHITE)
    fit(cv, 'LEFT 10 NOV 1942', a[0] - 30, a[1] + 128, 38, 420, AMBER)
    cv.drawCircle(b[0], b[1], 14, P(0xFFFFFFFF, 6))
    fit(cv, 'SURINAME', b[0] - 20, b[1] - 34, 46, 340, WHITE)
    if k >= 1:
        kk = pop(c.k, 0.64, 0.08)
        cv.drawLine(x_[0] - 26 * kk, x_[1] - 26 * kk, x_[0] + 26 * kk, x_[1] + 26 * kk, P(RED, 13))
        cv.drawLine(x_[0] - 26 * kk, x_[1] + 26 * kk, x_[0] + 26 * kk, x_[1] - 26 * kk, P(RED, 13))
        fit(cv, 'SUNK 23 NOV', x_[0] + 230, x_[1] + 16, 54, 380, WHITE)
        for i in range(8):
            u = i / 8
            cv.drawCircle(lerp(x_[0], b[0], u + 0.1), lerp(x_[1], b[1], u + 0.1), 5, P(0x66FFFFFF))
    sketch_note(cv, 'SKETCH MAP, NOT TO SCALE')


def _icon(cv, i, x, y):
    if i == 0:      # water tank
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 46, y - 62, 92, 120), 12, 12, P(h('A8B0B8')))
        cv.drawRect(skia.Rect.MakeXYWH(x - 14, y - 82, 28, 22), P(h('6A7078')))
        cv.drawRect(skia.Rect.MakeXYWH(x - 46, y - 10, 92, 68), P(h('3A8AC8')))
    elif i == 1:    # biscuit tins
        for j, col in enumerate(('B8442E', 'D8B048')):
            cv.drawRoundRect(skia.Rect.MakeXYWH(x - 70 + j * 62, y - 26 - j * 22, 78, 84), 8, 8, P(h(col)))
            cv.drawRect(skia.Rect.MakeXYWH(x - 70 + j * 62, y - 26 - j * 22, 78, 16), P(0x55000000))
    elif i == 2:    # chocolate
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 62, y - 44, 124, 88), 8, 8, P(h('5A3220')))
        for a in range(1, 4):
            cv.drawLine(x - 62 + a * 31, y - 44, x - 62 + a * 31, y + 44, P(h('3A1E12'), 4))
        cv.drawLine(x - 62, y, x + 62, y, P(h('3A1E12'), 4))
    elif i == 3:    # sugar
        cv.drawPath(poly([(x - 52, y + 56), (x - 40, y - 30), (x + 40, y - 30), (x + 52, y + 56)]), P(h('E8E0D0')))
        cv.drawPath(poly([(x - 40, y - 30), (x - 20, y - 58), (x + 20, y - 58), (x + 40, y - 30)]), P(h('C8C0B0')))
        for a, b in ((-16, 12), (14, 20), (0, -6)):
            cv.drawRect(skia.Rect.MakeXYWH(x + a - 9, y + b - 9, 18, 18), P(WHITE))
    elif i == 4:    # flares
        for j in range(3):
            cv.save()
            cv.translate(x - 40 + j * 40, y)
            cv.rotate(-12 + j * 12)
            cv.drawRoundRect(skia.Rect.MakeXYWH(-11, -56, 22, 112), 6, 6, P(h('C8452E')))
            cv.drawRect(skia.Rect.MakeXYWH(-11, -56, 22, 20), P(h('F2B531')))
            cv.restore()
    else:           # flashlight
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 66, y - 20, 96, 40), 8, 8, P(h('39404A')))
        cv.drawPath(poly([(x + 30, y - 20), (x + 64, y - 38), (x + 64, y + 38), (x + 30, y + 20)]), P(h('4A525E')))
        cv.drawRect(skia.Rect.MakeXYWH(x + 64, y - 34, 8, 68), P(h('FFF2C0')))


def stores(cv, c):
    """What the sources agree was on the raft (their lists differ in the details)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('14303E')), (1, h('0A1A24'))])
    T(cv, 'ON THE RAFT', 960, 120, 96, WHITE, BLACK)
    names = ('WATER', 'BISCUITS', 'CHOCOLATE', 'SUGAR', 'FLARES', 'FLASHLIGHT')
    for i, s in enumerate(names):
        k = pop(c.lt, 0.15 + i * 0.3)
        if k <= 0:
            continue
        x, y = 340 + (i % 3) * 620, 330 + (i // 3) * 300
        cv.save()
        cv.translate(x, y)
        cv.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
        cv.drawRoundRect(skia.Rect.MakeXYWH(-270, -120, 540, 250), 20, 20, P(0x66000000))
        cv.drawRoundRect(skia.Rect.MakeXYWH(-280, -130, 540, 250), 20, 20, P(h('E6D3A6')))
        _icon(cv, i, -180, -6)
        fit(cv, s, 70, 16, 62, 300, INK, None)
        cv.restore()
    sketch_note(cv, 'THE LISTS DIFFER BETWEEN ACCOUNTS')


def crew_lost(cv, c):
    """The ship's company. Sources give 53 or 54 aboard; one man was ever found."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C1A28')), (1, h('04080E'))])
    T(cv, 'SS BENLOMOND', 960, 130, 84, 0xFFBFD0DC, None)
    fade = ease((c.lt - 0.5) / 1.0)
    for i in range(54):
        x, y = 285 + (i % 18) * 80, 250 + (i // 18) * 110
        one = i == 43
        col = AMBER if one else Wd.alpha(h('8FA4B4'), 1 - 0.82 * fade)
        cv.drawCircle(x, y, 17, P(col))
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - 20, y + 22, 40, 50), 12, 12, P(col))
    T(cv, 'CREW: MORE THAN 50', 620, 680, 66, 0xFFBFD0DC, None)
    k = pop(c.lt, 1.3, 0.2)
    if k > 0:
        T(cv, 'FOUND: 1', 1330, 690, 110, AMBER, BLACK)


def weeks(cv, c):
    """Two bars run down: food about eight weeks, water about ten (most accounts; one says he first rationed for 30 days)."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('14303E')), (1, h('0A1A24'))])
    T(cv, 'HOW LONG THE STORES LASTED', 960, 130, 72, WHITE, BLACK)
    k = ease(c.k / 0.75)
    for j, (name, wk, col) in enumerate((('FOOD', 8, 'E0C080'), ('WATER', 10, '3A8AC8'))):
        y = 290 + j * 250
        T(cv, name, 330, y + 62, 84, WHITE, BLACK)
        x0, full = 560, 1120
        cv.drawRoundRect(skia.Rect.MakeXYWH(x0, y, full, 110), 14, 14, P(0x55000000))
        used = min(1.0, k * 10 / wk)
        cv.drawRoundRect(skia.Rect.MakeXYWH(x0, y, full * wk / 10 * (1 - used) + 1, 110), 14, 14, P(h(col)))
        for i in range(1, 10):
            cv.drawLine(x0 + i * full / 10, y, x0 + i * full / 10, y + 110, P(0x66FFFFFF, 3))
        cv.drawRoundRect(skia.Rect.MakeXYWH(x0, y, full, 110), 14, 14, P(WHITE, 5))
        if used >= 1:
            T(cv, f'GONE AFTER ABOUT {wk} WEEKS', x0 + full / 2, y + 74, 54, AMBER, BLACK)
    T(cv, 'WEEK ' + str(min(10, 1 + int(k * 10))) if k < 1 else 'THEN NOTHING', 960, 780, 76, AMBER if k >= 1 else WHITE, BLACK)
    sketch_note(cv, 'ACCOUNTS DIFFER ON THE EXACT NUMBERS')


def views(cv, c):
    """Why the freighter did not stop: his own belief, and the other explanation that has been offered."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2A34')), (1, h('120C14'))])
    T(cv, 'WHY DID IT NOT STOP?', 960, 130, 84, WHITE, BLACK)
    for j, (head, l1, l2, col, t0) in enumerate((('HE BELIEVED:', 'BECAUSE HE', 'WAS CHINESE', 'F1E6CC', 0.3), ('OTHERS SAY:', 'U-BOATS WERE RUMOURED', 'TO USE A RAFT AS BAIT', 'BFE0EC', 1.6))):
        k = pop(c.lt, t0, 0.2)
        if k <= 0:
            continue
        cv.save()
        cv.translate(500 + j * 920, 450)
        cv.rotate(-2 + j * 4)
        cv.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
        cv.drawRect(skia.Rect.MakeXYWH(-388, -168, 800, 380), P(0x66000000))
        cv.drawRect(skia.Rect.MakeXYWH(-400, -180, 800, 380), P(h(col)))
        cv.drawRect(skia.Rect.MakeXYWH(-70, -202, 140, 44), P(0xCCFFB000))
        T(cv, head, 0, -90, 54, h('7A5A48'), None)
        fit(cv, l1, 0, 10, 66, 740, INK, None)
        fit(cv, l2, 0, 100, 66, 740, INK, None)
        cv.restore()
    k = pop(c.lt, 2.9, 0.2)
    if k > 0:
        T(cv, 'EITHER WAY, IT SAILED ON', 960, 790, 70, AMBER, BLACK)


LAND = [(-56, 6.4), (-52, 5), (-50.5, 1.5), (-48.5, -0.6), (-44.5, -2.6), (-40, -2.9), (-37.2, -4.7), (-35, -5.6), (-35, -9), (-37, -11),
        (-56, -11)]


def map_drift(cv, c):
    """Sketch of the sea off northern Brazil. The two ends are from the record; the path between them is not known."""
    sea(cv)
    px = lambda lon, lat: (960 + (lon + 44) * 76.0, 470 - lat * 60.0)
    for lon in range(-55, -30, 5):
        cv.drawLine(px(lon, 0)[0], 60, px(lon, 0)[0], 860, P(0x33BFE6F2, 2))
    cv.drawLine(0, 470, W, 470, P(0x66BFE6F2, 3))
    T(cv, 'EQUATOR', 1800, 456, 28, 0x99BFE6F2, None)
    path = poly([px(*p) for p in LAND])
    cv.drawPath(path, P(h('D8C890')))
    cv.drawPath(path, P(h('5E4E2A'), 6))
    T(cv, 'BRAZIL', px(-47, -6.6)[0], px(-47, -6.6)[1], 110, h('5E4E2A'), None)
    T(cv, 'ATLANTIC OCEAN', 1300, 240, 46, 0x88DFF4FF, None)
    a, b = px(-38.75, 0.5), px(-47.3, -0.45)
    k = ease(c.k / 0.6)
    for i in range(26):
        u = i / 25
        if u > k:
            break
        cv.drawCircle(lerp(a[0], b[0], u), lerp(a[1], b[1], u) + 40 * math.sin(u * 9.0) * (1 - u), 9, P(WHITE))
    cv.drawLine(a[0] - 26, a[1] - 26, a[0] + 26, a[1] + 26, P(RED, 13))
    cv.drawLine(a[0] - 26, a[1] + 26, a[0] + 26, a[1] - 26, P(RED, 13))
    fit(cv, 'SUNK 23 NOV 1942', a[0] + 250, a[1] - 60, 50, 480, WHITE)
    if k >= 1:
        cv.drawCircle(b[0], b[1], 22, P(AMBER))
        cv.drawCircle(b[0], b[1], 22 + 36 * ((c.t * 2) % 1), P(Wd.alpha(AMBER, 1 - (c.t * 2) % 1), 7))
        fit(cv, 'FOUND 5 APR 1943', b[0] - 60, b[1] - 60, 50, 480, AMBER)
        T(cv, 'ABOUT 750 MILES', (a[0] + b[0]) / 2, 330, 84, WHITE, BLACK)
    T(cv, '133 DAYS ADRIFT', 520, 150, 84, WHITE, BLACK)
    sketch_note(cv, 'SKETCH: THE DRIFT PATH IS NOT KNOWN')


def scale20(cv, c):
    """A scale: about 20 pounds (9 kg) lost."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('14303E')), (1, h('0A1A24'))])
    cx, cy, r = 620, 640, 400
    cv.drawArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), 180, 180, True, P(h('E6D3A6')))
    cv.drawArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), 180, 180, True, P(INK, 10))
    for i in range(21):
        a = math.pi * (1 + i / 20)
        r0 = r - (70 if i % 5 == 0 else 40)
        cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (r - 14), cy + math.sin(a) * (r - 14), P(INK, 8 if i % 5 == 0 else 4))
    k = ease((c.lt - 0.25) / 0.6)
    a = math.pi * (1 + lerp(0.72, 0.52, k)) + 0.01 * math.sin(c.t * 14) * (1 - k)
    cv.drawLine(cx, cy, cx + math.cos(a) * (r - 90), cy + math.sin(a) * (r - 90), P(RED, 16))
    cv.drawCircle(cx, cy, 30, P(INK))
    T(cv, 'AFTER 133 DAYS', 1380, 300, 70, WHITE, BLACK)
    kk = pop(c.lt, 0.8, 0.2)
    if kk > 0:
        cv.save()
        cv.translate(1380, 520)
        cv.scale(1.5 - 0.5 * kk, 1.5 - 0.5 * kk)
        T(cv, 'ABOUT', 0, -110, 70, WHITE, BLACK)
        T(cv, '20 LB', 0, 60, 210, AMBER, BLACK)
        T(cv, 'LOST', 0, 170, 90, WHITE, BLACK)
        cv.restore()
    sketch_note(cv, 'ILLUSTRATION OF THE REPORTED FIGURE (ABOUT 9 KG)')


def manual(cv, c):
    """A page standing in for the survival manuals. Not a real page."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('16283A')), (1, h('0A121C'))])
    k = ease(c.lt / 0.25)
    sheet(cv, 960, 450, 1500, 720, 1.2, k, 'INTO THE ROYAL NAVY\'S SURVIVAL MANUALS', h('1E3A5A'))
    # raft diagram
    cv.drawRect(skia.Rect.MakeXYWH(-680, -190, 430, 300), P(h('B08A58')))
    for i in range(1, 8):
        cv.drawLine(-680, -190 + i * 37.5, -250, -190 + i * 37.5, P(h('6E5030'), 4))
    cv.drawRect(skia.Rect.MakeXYWH(-680, -190, 430, 300), P(INK, 7))
    cv.drawPath(poly([(-680, -190), (-250, -190), (-250, -60), (-680, -60)]), P(0x99CDB98C))
    for x in (-680, -250):
        cv.drawCircle(x, -190, 12, P(INK))
        cv.drawCircle(x, -60, 12, P(INK))
    T(cv, 'HIS RAFT', -465, 170, 44, h('7A6A48'), None)
    rows = ('A HOOK FROM A FLASHLIGHT SPRING', 'A LINE FROM UNPICKED ROPE', 'A KNIFE FROM A TIN', 'RAIN CAUGHT IN CANVAS')
    for i, s in enumerate(rows):
        y = -150 + i * 108
        kk = pop(c.lt, 0.5 + i * 0.55)
        fit(cv, s, -170, y + 20, 50, 760, INK if kk > 0 else h('B8A478'), None, center=False)
        if kk > 0:
            p = skia.Path()
            p.moveTo(630, y - 6)
            p.lineTo(630 + 22 * kk, y + 20 * kk)
            p.lineTo(630 + 22 * kk + 44 * kk, y + 20 * kk - 60 * kk)
            cv.drawPath(p, P(GREEN, 14))
    cv.restore()
    sketch_note(cv, 'ILLUSTRATION, NOT A PAGE FROM A REAL MANUAL')


def quota(cv, c):
    """The quota for Chinese immigrants was full; a senator won him a special exception. Not a real form."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A2630')), (1, h('100E14'))])
    k = ease(c.lt / 0.25)
    sheet(cv, 960, 450, 1300, 700, -1.2, k, 'APPLICATION TO IMMIGRATE', h('3A3A52'))
    for i, (lab, val) in enumerate((('NAME', 'POON LIM'), ('QUOTA', 'CHINESE IMMIGRANTS'))):
        y = -170 + i * 150
        T(cv, lab, -580, y, 34, h('7A6A48'), None, center=False)
        T(cv, val, -580, y + 70, 66, INK, None, center=False)
        cv.drawLine(-580, y + 92, 580, y + 92, P(h('B8A478'), 4))
    for i in range(3):
        cv.drawLine(-580, 170 + i * 50, 300 - i * 120, 170 + i * 50, P(h('C8B88E'), 12))
    cv.restore()
    if c.k > 0.2:
        stamp(cv, 'QUOTA FULL', 1180, 420, -9, min(1, (c.k - 0.2) / 0.06), 110, RED, 0x00000000)
    if c.k > 0.62:
        stamp(cv, 'SPECIAL EXCEPTION', 900, 640, 6, min(1, (c.k - 0.62) / 0.06), 100, GREEN, 0xEEF1E6CC)
    sketch_note(cv, 'ILLUSTRATION, NOT A REAL FORM')


def citizen(cv, c):
    """1952: a United States citizen. Not a real certificate."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1A2A44')), (1, h('0A101E'))])
    k = ease(c.lt / 0.25)
    cv.save()
    cv.translate(960, 440 + 600 * (1 - k))
    cv.rotate(1.0)
    cv.drawRect(skia.Rect.MakeXYWH(-638, -298, 1300, 620), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-650, -310, 1300, 620), P(h('F1E6CC')))
    cv.drawRect(skia.Rect.MakeXYWH(-620, -280, 1240, 560), P(h('8A6A2A'), 8))
    cv.drawRect(skia.Rect.MakeXYWH(-600, -260, 1200, 520), P(h('8A6A2A'), 3))
    T(cv, 'UNITED STATES CITIZEN', 0, -130, 84, h('1A2A44'), None)
    T(cv, 'POON LIM', 0, 10, 110, INK, None)
    cv.drawLine(-380, 40, 380, 40, P(h('8A6A2A'), 4))
    cv.restore()
    kk = pop(c.lt, 0.7, 0.16)
    if kk > 0:
        cv.save()
        cv.translate(960, 640)
        cv.scale(1.7 - 0.7 * kk, 1.7 - 0.7 * kk)
        T(cv, '1952', 0, 0, 170, AMBER, BLACK)
        cv.restore()
    sketch_note(cv, 'ILLUSTRATION, NOT A REAL CERTIFICATE')


def record(cv, c):
    """Still the longest recorded survival alone on a raft."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0C2233')), (1, h('05101A'))])
    for row in range(2):
        y = 110 + row * 660
        cv.drawLine(110, y, W - 110, y + 8 * math.sin(row * 1.7), P(h('C9B48A'), 8))
        for i in range(19):
            cv.drawCircle(150 + i * 90, y + 4, 13, P(h('E4D2A6')))
    k = ease(c.lt / 0.2)
    cv.save()
    cv.translate(960, 400)
    cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
    T(cv, '133 DAYS', 0, 60, 260, AMBER, BLACK)
    cv.restore()
    T(cv, 'ALONE ON A RAFT', 960, 580, 90, WHITE, BLACK)
    if c.k > 0.55:
        stamp(cv, 'STILL THE RECORD', 960, 300, -7, min(1, (c.k - 0.55) / 0.08), 96, AMBER)


def board_true(cv, c):
    chart(cv)
    card(cv, 660, 440, 760, 640, 2)
    cv.save()
    cv.translate(660, 440)
    cv.rotate(2)
    photo(cv, 'poon', 0, 8, 700, 560, (0.5, 0.3))
    cv.restore()
    if c.lt > 0.3:
        stamp(cv, 'TRUE', 700, 540, -14, min(1, (c.lt - 0.3) / 0.12), 190)
    note(cv, '133 DAYS', 1400, 300, 420, 180, -5, 80, k=pop(c.lt, 0.15))
    note(cv, 'ALONE', 1440, 560, 340, 170, 6, 80, h('BFE0EC'), pop(c.lt, 0.5))


SHOTS = {f.__name__: f for f in (tally_133, board_no, id_card, hainan, map_route, stores, crew_lost, weeks, views, map_drift, scale20, manual, quota, citizen,
                                 record, board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def rain(cv, c):
    Wd.rain(cv, W, H, c.t, density=170, c=0x77D8ECFF, slant=0.22, speed=1900, seed=5, length=52)


def squall(cv, c):
    Wd.rain(cv, W, H, c.t, density=280, c=0x88D8ECFF, slant=0.55, speed=2700, seed=8, length=78)


def drizzle(cv, c):
    Wd.rain(cv, W, H, c.t, density=70, c=0x55D8ECFF, slant=0.3, speed=1500, seed=11, length=40)


def size8(cv, c):
    if c.prm.get('alt'):
        return
    k = ease((c.lt - 0.15) / 0.2)
    if k <= 0:
        return
    y = 150
    x0, x1 = 960 - 250 * k, 960 + 250 * k
    cv.drawLine(x0, y, x1, y, P(BLACK, 16))
    cv.drawLine(x0, y, x1, y, P(AMBER, 8))
    for x in (x0, x1):
        cv.drawLine(x, y - 30, x, y + 30, P(BLACK, 16))
        cv.drawLine(x, y - 30, x, y + 30, P(AMBER, 8))
    T(cv, '8 FT', 960, y - 36, 96, AMBER, BLACK)


def day133(cv, c):
    k = ease((c.lt - 0.9) / 0.14)
    if k <= 0:
        return
    cv.save()
    cv.translate(420, 250)
    cv.rotate(-5)
    cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
    T(cv, 'DAY 133', 0, 0, 170, AMBER, BLACK)
    cv.restore()


def closed(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(1380, 380)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        T(cv, 'SURVRA', 0, 0, 170, AMBER, BLACK)
        T(cv, 'CASE 009  CLOSED', 0, 96, 60, WHITE, BLACK)
        cv.restore()


OVER = dict(rain_catch=rain, life_cover=rain, storm_hide=squall, storm_after=drizzle, marker_lost=drizzle, raft_top=size8, fish_boat=day133, signoff=closed)


# ------------------------------------------------------------------ thumbnail
def THUMB(cv, c):
    """1280x720: the 3D still (the man on the raft with a line down, a fin beside it, Rook's hat in the air) + a hook."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('7EC0EE'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(660, 0), (1020, 0)], [0x00000000, 0xC8000000])))
    T(cv, '133 DAYS', 975, 300, 138, AMBER, BLACK)
    T(cv, 'ALONE', 975, 440, 138, WHITE, BLACK)
    T(cv, 'ON A RAFT', 975, 540, 70, WHITE, BLACK)
