"""Case 014, the full case file - Beck Weathers. The story is filmed in 3D (world3d.py). This file holds the flat
inserts for a 1920x1080 frame (the double stamp, Rook's case board pinned to a sheet of orange tent fabric, the
drawn cards) and the 2D overlays drawn on top of 3D shots (blown snow, the blizzard, the white haze over his sight,
rotor wash, the hour counter, the sign-off), plus the thumbnail. Every card is a drawing made for this film; none of
them reproduces a real document, photograph, map, book cover, medical image or logo."""
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
ORANGE, AMBER, PAPER, RED, GREEN = h('FF7A1A'), h('FFB000'), h('F0E8D2'), h('D8362A'), h('3EC46A')
ICE, DEEP, YEL = h('CFE2FA'), h('0A1428'), h('FFD866')


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def font(size):
    return skia.Font(skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant)), size)


def fit(cv, s, x, y, size, maxw, color=0xFFFFFFFF, stroke=0xFF000000):
    """Centred text that shrinks to stay inside maxw."""
    w = font(size).measureText(s)
    if w > maxw:
        size *= maxw / w
    return Wd.text_card(cv, s, x, y, size, color, stroke)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (world3d.STILLS) pinned to the board as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('7A94B8')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def fabric_board(cv):
    """Rook's board for this case: a panel of orange tent fabric, stitched in squares, laced to a frame with cord."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(h('1C2434')))
    cv.drawRect(skia.Rect.MakeLTRB(60, 50, W - 60, H - 50), P(h('D9772A')))
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(60, 50, W - 60, H - 50))
    for i in range(-H, W + H, 26):                                # ripstop weave
        cv.drawLine(i, 0, i + H, H, P(h('E8862E'), 2, a=0.35))
        cv.drawLine(i, H, i + H, 0, P(h('B85E1C'), 2, a=0.3))
    for x in (60, 660, 1260, W - 60):                             # seams
        for y in range(60, H - 50, 34):
            cv.drawLine(x, y, x, y + 18, P(h('7A3A12'), 6))
    for y in (50, 540, H - 50):
        for x in range(70, W - 60, 34):
            cv.drawLine(x, y, x + 18, y, P(h('7A3A12'), 6))
    cv.restore()
    for i in range(15):                                           # eyelets and lacing along the top and bottom
        x = 130 + i * 118.5
        for y, y2 in ((84, 16), (H - 84, H - 16)):
            cv.drawCircle(x, y, 15, P(h('D8DCE4')))
            cv.drawCircle(x, y, 7, P(h('1C2434')))
            cv.drawLine(x, y, x + (40 if i % 2 else -40), y2, P(h('F0E8D2'), 6))
    Wd.vgrad(cv, 0, 0, W, H, [(0, 0x22000000), (0.5, 0x00000000), (1, 0x66000000)])


def card(cv, x, y, w_, h_, ang, col=PAPER, tape=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    if tape:
        for sx in (-1, 1):                                        # held by two steel clips
            cv.drawRoundRect(skia.Rect.MakeXYWH(sx * (w_ / 2 - 90) - 24, -h_ / 2 - 30, 48, 76), 18, 18, P(h('D8DCE4'), 11))
    cv.restore()


def note(cv, x, y, w_, h_, ang, col, lines, size=64, k=1.0):
    cv.save()
    cv.translate(x, y)
    s = 1.3 - 0.3 * ease(k)
    cv.scale(s, s)
    card(cv, 0, 0, w_, h_, ang, col, tape=False)
    cv.rotate(ang)
    for i, s_ in enumerate(lines):
        fit(cv, s_, 0, (i - (len(lines) - 1) / 2) * size * 1.12 + size * 0.36, size, w_ - 50, INK, None)
    cv.restore()


def stamp(cv, s, x, y, ang, k, size=150, col=RED):
    """A rubber stamp that slams down (k 0..1)."""
    f = font(size)
    tw = f.measureText(s)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    sc = 2.3 - 1.3 * k
    cv.scale(sc, sc)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-tw / 2 - 30, -size * 0.62, tw + 60, size * 1.2), 18, 18, P(col, 14, a=k))
    cv.drawString(s, -tw / 2, size * 0.36, f, P(col, a=k))
    cv.restore()


def flakes(cv, t, n=60, col=0xCCF4F8FF, drift=(-70, 230), size=(3, 8), seed=5):
    Wd.particles(cv, W, H, t, n, col, seed, size=size, drift=drift, wobble=26)


def night_sky(cv, c, top='1A2C4E', bot='060A14', peaks=True):
    """The plain backdrop for the cards: a dark sky, a far line of peaks as flat shapes, drifting snow and light."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    for i in range(7):                                            # slow bands of light, so no card is ever a still picture
        x = ((c.t * 220 + i * 420) % (W + 900)) - 450
        cv.drawPath(poly([(x, 0), (x + 240, 0), (x - 120, H), (x - 360, H)]), P(0xFF6F9CDC, a=0.07))
    if peaks:
        for i in range(11):
            x = -120 + i * 210
            top_ = 760 - 60 * (i % 3) - 30 * ((i * 7) % 4)
            cv.drawPath(poly([(x - 210, 1080), (x + 20, top_), (x + 250, 1080)]), P(h('22385E')))
            cv.drawPath(poly([(x - 55, top_ + 110), (x + 20, top_), (x + 95, top_ + 110), (x + 20, top_ + 160)]), P(h('5A76A8')))
    flakes(cv, c.t, 90, 0x88F4F8FF, (-200, 300))


def push(cv, c, amt=0.06):
    z = 1.0 + amt * c.k
    cv.translate(W / 2, H * 0.45)
    cv.scale(z, z)
    cv.translate(-W / 2, -H * 0.45)


# ------------------------------------------------------------------ flat inserts
def twice(cv, c):
    """'Left him for dead. Twice.'"""
    night_sky(cv, c)
    k1 = min(1, c.lt / 0.12)
    stamp(cv, 'LEFT FOR DEAD', 620, 300, -7, k1, 120)
    if c.k > 0.42:
        k2 = min(1, (c.k - 0.42) * c.d / 0.12)
        stamp(cv, 'LEFT FOR DEAD', 1260, 470, 5, k2, 120)
        fit(cv, 'TWICE', 960, 720 + 40 * (1 - k2), 150, 800, AMBER)


def board_no(cv, c):
    fabric_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(620, 440)
    cv.scale(s, s)
    card(cv, 0, 0, 880, 600, -3)
    cv.rotate(-3)
    photo(cv, 'peak', 0, 14, 810, 520, (0.5, 0.35))
    cv.restore()
    if c.lt > 0.1:
        cv.drawLine(1070, 420, 1190, 360, P(h('F0E8D2'), 8))
        note(cv, 1450, 330, 560, 190, 3, YEL, ['DEAD TWICE?'], 84)
    fit(cv, '1996  EVEREST', 1450, 510, 72, 560, INK, None)
    if c.k > 0.4:
        stamp(cv, 'NO CHANCE', 1450, 700, -7, min(1, (c.k - 0.4) * c.d / 0.1), 92)


def board_beck(cv, c):
    fabric_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(560, 440)
    cv.scale(s, s)
    card(cv, 0, 0, 700, 620, 2)
    cv.rotate(2)
    photo(cv, 'beck', 0, 14, 630, 540, (0.5, 0.42))
    cv.restore()
    fit(cv, 'BECK WEATHERS', 560, 818, 50, 700, INK, None)
    for i, (s_, y, t0, ang) in enumerate((('PATHOLOGIST', 250, 0.5, -3), ('DALLAS', 470, 1.3, 3), ("ROB HALL'S EXPEDITION", 690, 2.0, -2))):
        if c.lt > t0:
            j = (c.lt - t0) / 0.16
            cv.drawLine(930, 440, 1130, y, P(h('F0E8D2'), 7, a=min(1, j)))
            note(cv, 1420, y, 620, 150, ang, YEL if i < 2 else PAPER, [s_], 74, j)


def eye_shape(cv, cx, cy, s, haze=0.0):
    """A plain drawn eye, not a medical image."""
    lid = skia.Path()
    lid.moveTo(cx - 2.2 * s, cy)
    lid.quadTo(cx, cy - 1.7 * s, cx + 2.2 * s, cy)
    lid.quadTo(cx, cy + 1.7 * s, cx - 2.2 * s, cy)
    cv.drawPath(lid, P(h('F4F2EA')))
    cv.save()
    cv.clipPath(lid)
    cv.drawCircle(cx, cy, 0.95 * s, P(h('5A86B8')))
    cv.drawCircle(cx, cy, 0.42 * s, P(INK))
    cv.drawCircle(cx - 0.25 * s, cy - 0.28 * s, 0.14 * s, P(0xFFFFFFFF))
    if haze > 0:
        cv.drawRect(skia.Rect.MakeXYWH(cx - 2.3 * s, cy - 1.8 * s, 4.6 * s, 3.6 * s), P(0xFFE8EEF6, a=0.88 * haze))
    cv.restore()
    cv.drawPath(lid, P(INK, 9))


def eye_card(cv, c):
    """Two drawn eyes: clear at sea level, clouded over on the mountain."""
    night_sky(cv, c, '20304E', '080C16', peaks=False)
    push(cv, c)
    fit(cv, 'HIS EYES', 960, 150, 96, 900, 0xFFFFFFFF)
    k = ease((c.lt - 0.9) / 0.9)
    eye_shape(cv, 520, 440, 120)
    eye_shape(cv, 1400, 440, 120, k)
    fit(cv, 'AFTER EYE SURGERY', 520, 740, 58, 700, 0xFFFFFFFF)
    fit(cv, 'HIGH ON THE MOUNTAIN', 1400, 740, 58, 700, AMBER if k > 0.3 else 0xFFFFFFFF)
    a = ease((c.lt - 0.4) / 0.4)
    cv.drawLine(800, 440, lerp(800, 1100, a), 440, P(AMBER, 16))
    if a > 0.95:
        cv.drawPath(poly([(1100, 405), (1160, 440), (1100, 475)]), P(AMBER))


def accounts(cv, c):
    """Two notes side by side: the sources do not agree on who decided he should wait."""
    fabric_board(cv)
    fit(cv, 'WHY DID HE WAIT?', 960, 190, 92, 1300, INK, None)
    k1, k2 = (c.lt - 0.25) / 0.16, (c.lt - 1.5) / 0.16
    if k1 > 0:
        note(cv, 560, 450, 640, 300, -3, YEL, ['TOLD TO', 'STAY PUT'], 88, k1)
    if k2 > 0:
        note(cv, 1360, 450, 640, 300, 3, PAPER, ['CHOSE', 'TO WAIT'], 88, k2)
        fit(cv, 'OR', 960, 470, 90, 200, INK, None)
    if c.lt > 2.1:
        fit(cv, 'THE ACCOUNTS DIFFER', 960, 760, 64, 1200, INK, None)


def tally(cv, c):
    """A running count. prm n: 1 and 2 are the two times he was left; 3 adds the night nobody expected him to live through."""
    n = int(c.prm.get('n', 1))
    night_sky(cv, c)
    push(cv, c, 0.05)
    rows = (('LEFT FOR DEAD', 250), ('LEFT FOR DEAD', 440), ("WON'T LAST THE NIGHT", 630))
    for i, (s_, y) in enumerate(rows[:max(2, n)]):
        on = i < n
        new = i == n - 1
        k = min(1, c.lt / 0.14) if new else 1.0
        if on:
            stamp(cv, s_, 860 if i < 2 else 900, y, -4 + 4 * i, k, 104 if i < 2 else 58)
            fit(cv, str(i + 1), 330, y + 34, 130, 200, AMBER)
        else:
            cv.drawRoundRect(skia.Rect.MakeXYWH(420, y - 70, 880, 140), 18, 18, dashed(0x66FFFFFF, 6))
    if n == 3 and c.lt > 0.9:
        k = ease((c.lt - 0.9) / 0.3)
        for i, (s_, y) in enumerate(rows):
            cv.drawLine(450, y + 6 * i, lerp(450, 1330, k), y - 14 + 6 * i, P(GREEN, 14))
        if c.lt > 1.3:
            j = min(1, (c.lt - 1.3) / 0.14)
            fit(cv, 'WRONG', 1590, 380 + 30 * (1 - j), 96, 360, GREEN)
            fit(cv, 'x 3', 1590, 530 + 30 * (1 - j), 120, 360, GREEN)
    elif n < 3:
        fit(cv, 'TIMES LEFT: %d' % n, 1540, 345, 64, 420, 0xFFFFFFFF)


def report(cv, c):
    """A drawn report sheet. The wording paraphrases what a report written at Base Camp that week says."""
    fabric_board(cv)
    k = min(1, c.lt / 0.18)
    cv.save()
    cv.translate(960, 440 + 60 * (1 - ease(k)))
    cv.rotate(-2)
    cv.drawRect(skia.Rect.MakeXYWH(-560 + 14, -330 + 18, 1120, 660), P(0x55000000))
    cv.drawRect(skia.Rect.MakeXYWH(-560, -330, 1120, 660), P(PAPER))
    fit(cv, 'REPORT FROM BASE CAMP', 0, -220, 70, 1000, INK, None)
    cv.drawLine(-480, -170, 480, -170, P(INK, 6))
    for i in range(3):
        cv.drawLine(-480, -100 + i * 44, 480 - 120 * (i == 2), -100 + i * 44, P(h('9A927E'), 10))
    if c.lt > 1.9:
        j = ease((c.lt - 1.9) / 0.25)
        cv.drawRect(skia.Rect.MakeXYWH(-500, 40, 1000 * j, 190), P(YEL, a=0.9))
        fit(cv, 'DEATH CONFIRMED', 0, 110, 84, 940, INK, None)
        fit(cv, 'BY A DOCTOR', 0, 200, 84, 940, INK, None)
    cv.restore()
    if c.lt > 2.9:
        stamp(cv, 'NOT SO', 1500, 700, -10, min(1, (c.lt - 2.9) / 0.12), 96, GREEN)


def hours(cv, c):
    """Three cards: the lengths of time the sources give."""
    night_sky(cv, c)
    push(cv, c, 0.05)
    fit(cv, 'HOW LONG IN THE SNOW?', 960, 150, 84, 1500, 0xFFFFFFFF)
    for i, (num, who, t0) in enumerate((('15', 'HIS OWN COUNT', 1.2), ('16', 'ONE REPORT', 3.0), ('18', 'ANOTHER', 3.6))):
        if c.lt < t0:
            continue
        j = ease((c.lt - t0) / 0.18)
        x = 400 + i * 560
        cv.save()
        cv.translate(x, 470 + 50 * (1 - j))
        cv.rotate((-3, 2, -2)[i])
        cv.drawRect(skia.Rect.MakeXYWH(-220 + 12, -200 + 16, 440, 420), P(0x55000000))
        cv.drawRect(skia.Rect.MakeXYWH(-220, -200, 440, 420), P(YEL if i == 0 else PAPER))
        fit(cv, num, 0, 10, 230, 400, INK, None)
        fit(cv, 'HOURS', 0, 120, 70, 400, INK, None)
        cv.restore()
        fit(cv, who, x, 770, 50, 500, AMBER if i == 0 else 0xFFFFFFFF)


def vision(cv, c):
    """Plain silhouettes in a warm light: the family he is said to have seen. No likenesses."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A3E66')), (1, h('0A0E1A'))])
    k = ease(c.lt / 0.9)
    for i in range(6):
        pa = P(0xFFFFD9A0, a=0.1 * k)
        pa.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 60))
        cv.drawCircle(960 + 20 * math.sin(c.t * 1.3 + i), 470, 190 + i * 75 + 12 * math.sin(c.t * 2 + i), pa)
    for dx, hh, r in ((-210, 330, 62), (0, 400, 68), (200, 290, 56)):
        x = 960 + dx
        pa = P(h('3A2A1E'), a=0.9 * k)
        cv.drawCircle(x, 690 - hh, r, pa)
        cv.drawPath(poly([(x - r * 1.5, 700), (x - r * 1.25, 690 - hh + r * 1.6), (x, 690 - hh + r * 1.1), (x + r * 1.25, 690 - hh + r * 1.6), (x + r * 1.5, 700)]), pa)
    flakes(cv, c.t, 110, 0x99F4F8FF, (-240, 330))
    if c.lt > 1.3:
        fit(cv, 'HIS FAMILY', 960, 150, 96, 1200, AMBER)
    if c.lt > 0.2:
        fit(cv, 'BY ONE TELLING OF HIS STORY', 960, 790, 50, 1500, 0xFFFFFFFF)


def mountain(cv, k=1.0):
    """A drawn mountain in profile. A diagram for this film, not a map and not to scale."""
    pts = [(250, 830), (520, 700), (700, 560), (860, 450), (1010, 330), (1130, 190), (1240, 300), (1380, 520), (1560, 700), (1720, 830)]
    cv.drawPath(poly(pts), P(h('2E4A7A')))
    cv.drawPath(poly([(1010, 330), (1130, 190), (1240, 300), (1180, 350), (1120, 300), (1060, 370)]), P(h('E6EEF8')))
    cv.drawPath(poly([(250, 830), (520, 700), (640, 760), (430, 830)]), P(h('A9D4EE')))                # the icefall as a pale apron
    return dict(wait=(1085, 245), camp=(1010, 330), low=(760, 520), heli=(600, 660), base=(300, 810))


def dot(cv, p, col, label, side=1, on=1.0, size=44):
    cv.drawCircle(p[0], p[1], 20 * on, P(col))
    cv.drawCircle(p[0], p[1], 20 * on, P(0xFF000000, 5))
    if on > 0.6:
        f = font(size)
        w = f.measureText(label)
        x = p[0] + 40 if side > 0 else p[0] - 40 - w
        cv.drawString(label, x, p[1] + size * 0.36, f, P(0xFF000000, size * 0.2))
        cv.drawString(label, x, p[1] + size * 0.36, f, P(col))


def route(cv, c):
    """The way down, drawn: from the high camp to a lower camp on foot."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('26406E')), (1, h('0A1020'))])
    flakes(cv, c.t, 70, 0x77F4F8FF, (-160, 240))
    push(cv, c, 0.05)
    m = mountain(cv)
    fit(cv, 'DIAGRAM, NOT TO SCALE', 1560, 150, 34, 500, 0xAAFFFFFF, None)
    dot(cv, m['camp'], RED, 'HIGH CAMP', -1)
    k = ease((c.lt - 0.3) / 1.1)
    a, b = m['camp'], m['low']
    pa = P(AMBER, 14)
    pa.setPathEffect(skia.DashPathEffect.Make([26, 18], 0))
    cv.drawLine(a[0], a[1], lerp(a[0], b[0], k), lerp(a[1], b[1], k), pa)
    if k > 0.9:
        dot(cv, m['low'], AMBER, 'LOWER CAMP', -1, min(1, (k - 0.9) * 10))
    fit(cv, 'ON FOOT', 400, 230, 100, 480, 0xFFFFFFFF)


def altitude(cv, c):
    """Where the helicopter set down, drawn, with the one figure a report from that week gives."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('26406E')), (1, h('0A1020'))])
    flakes(cv, c.t, 70, 0x77F4F8FF, (-160, 240))
    push(cv, c, 0.05)
    m = mountain(cv)
    fit(cv, 'DIAGRAM, NOT TO SCALE', 1560, 150, 34, 500, 0xAAFFFFFF, None)
    k = ease((c.lt - 0.2) / 0.5)
    dot(cv, m['heli'], GREEN, 'ABOVE THE ICEFALL', -1, k, 40)
    x, y = m['heli'][0] + 30, m['heli'][1] - 90 - 14 * math.sin(c.t * 5)              # a plain drawn helicopter, no markings
    cv.drawOval(skia.Rect.MakeXYWH(x - 46, y - 22, 92, 44), P(h('D8DCE4'), a=k))
    cv.drawLine(x + 40, y - 4, x + 120, y - 14, P(h('D8DCE4'), 10, a=k))
    sp = 80 * abs(math.sin(c.t * 30))
    cv.drawLine(x - sp, y - 34, x + sp, y - 34, P(0xFFFFFFFF, 6, a=k))
    if c.lt > 1.4:
        j = min(1, (c.lt - 1.4) / 0.14)
        cv.save()
        cv.translate(540, 300)
        cv.scale(1.3 - 0.3 * j, 1.3 - 0.3 * j)
        fit(cv, 'ABOUT', 0, -110, 60, 700, 0xFFFFFFFF)
        fit(cv, '20,000 FT', 0, 30, 130, 640, AMBER)
        fit(cv, 'BY ONE REPORT THAT WEEK', 0, 120, 40, 760, 0xFFFFFFFF)
        cv.restore()


def hand_shape(cx, cy, s, flip=1):
    """A plain mitten-like outline of a hand, fingers up: palm path and four finger rects plus a thumb."""
    palm = skia.Rect.MakeXYWH(cx - 1.25 * s, cy - 0.2 * s, 2.5 * s, 2.5 * s)
    fingers = [skia.Rect.MakeXYWH(cx + (-1.25 + i * 0.64) * s, cy - (1.75 + (0.35 if i in (1, 2) else 0.0)) * s, 0.56 * s,
                                  (1.75 + (0.35 if i in (1, 2) else 0.0)) * s) for i in range(4)]
    thumb = skia.Rect.MakeXYWH(cx + flip * 1.25 * s - (0 if flip > 0 else 0.6 * s), cy + 0.2 * s, 0.6 * s, 1.5 * s)
    wrist = skia.Rect.MakeXYWH(cx - 0.95 * s, cy + 2.2 * s, 1.9 * s, 1.5 * s)
    return palm, fingers, thumb, wrist


def dashed(col, w_):
    pa = P(col, w_)
    pa.setPathEffect(skia.DashPathEffect.Make([22, 20], 0))
    return pa


def cost_card(cv, c):
    """Two drawn hands, backs towards us, and a list. The right hand and part of the forearm go to a dotted outline,
    then the fingers of the left; the feet and the nose are words only."""
    night_sky(cv, c, '20304E', '080C16', peaks=False)
    push(cv, c, 0.05)
    fit(cv, 'THE COST', 560, 130, 96, 900, 0xFFFFFFFF)
    s = 70
    k_r = ease((c.lt - 0.4) / 0.4)                                # "his right hand, and part of the forearm"
    k_l = ease((c.lt - 2.3) / 0.4)                                # "the fingers of his left hand"
    skin, line = h('E2B694'), h('F4F8FF')
    for side, cx in ((-1, 340), (1, 780)):                        # left hand on the left of the picture, right on the right
        palm, fingers, thumb, wrist = hand_shape(cx, 440, s, flip=-side)
        gone = k_r if side == 1 else 0.0
        fg = k_r if side == 1 else k_l
        for rect, kk in [(wrist, gone), (palm, gone), (thumb, gone)] + [(f, fg) for f in fingers]:
            if kk < 1:
                cv.drawRoundRect(rect, 20, 20, P(skin, a=1 - kk))
            if kk > 0:
                cv.drawRoundRect(rect, 20, 20, dashed(line, 6))
                cv.drawRoundRect(rect, 20, 20, P(ICE, a=0.12 * kk))
        fit(cv, 'LEFT' if side == -1 else 'RIGHT', cx, 790, 64, 400, AMBER if (side == 1 and k_r > 0) or (side == -1 and k_l > 0) else 0xFFFFFFFF)
    cv.drawLine(560, 230, 560, 800, P(0x33FFFFFF, 4))
    for i, (s_, t0) in enumerate((('RIGHT HAND', 0.4), ('PART OF THE FOREARM', 1.4), ('FINGERS OF THE LEFT', 2.3), ('PARTS OF BOTH FEET', 3.8),
                                  ('HIS NOSE: REBUILT', 5.3))):
        if c.lt > t0:
            j = ease((c.lt - t0) / 0.2)
            f = font(58)
            x, y = 1080 + 60 * (1 - j), 300 + i * 110
            cv.drawString(s_, x, y, f, P(0xFF000000, 12))
            cv.drawString(s_, x, y, f, P(AMBER if i < 4 else GREEN, a=j))
            cv.drawCircle(1040, y - 20, 12, P(AMBER if i < 4 else GREEN, a=j))


def book(cv, c):
    """A drawn book with its title. A plain cover made for this film, not the real one."""
    night_sky(cv, c, '2A2E4E', '0A0A16', peaks=False)
    k = ease(c.lt / 0.4)
    cv.save()
    cv.translate(960, 450 + 80 * (1 - k))
    cv.rotate(-5 + 3 * math.sin(c.t * 1.2))
    cv.scale(1.0 + 0.05 * c.k, 1.0 + 0.05 * c.k)
    cv.drawRect(skia.Rect.MakeXYWH(-250 + 26, -330 + 26, 500, 660), P(0x77000000))
    cv.drawRect(skia.Rect.MakeXYWH(-230, -322, 500, 644), P(h('F0E8D2')))
    cv.drawRect(skia.Rect.MakeXYWH(-250, -330, 500, 660), P(h('D9772A')))
    cv.drawRect(skia.Rect.MakeXYWH(-250, -330, 46, 660), P(h('B85E1C')))
    fit(cv, 'LEFT', 22, -150, 110, 400, 0xFFFFFFFF, None)
    fit(cv, 'FOR', 22, -30, 110, 400, 0xFFFFFFFF, None)
    fit(cv, 'DEAD', 22, 90, 110, 400, 0xFFFFFFFF, None)
    cv.drawLine(-120, 170, 160, 170, P(0xFFFFFFFF, 8))
    fit(cv, 'BECK WEATHERS', 22, 250, 40, 400, 0xFFFFFFFF, None)
    cv.restore()
    fit(cv, 'HIS BOOK', 400, 300, 70, 460, AMBER)
    fit(cv, 'DRAWN FOR THIS FILM', 1560, 780, 34, 520, 0xAAFFFFFF, None)


def board_true(cv, c):
    fabric_board(cv)
    k = min(1, c.lt / 0.16)
    s = 0.74 + 0.26 * (1 - (1 - k) ** 3)
    cv.save()
    cv.translate(620, 440)
    cv.scale(s, s)
    card(cv, 0, 0, 880, 600, 3)
    cv.rotate(3)
    photo(cv, 'walk', 0, 14, 810, 520, (0.5, 0.5))
    cv.restore()
    if c.lt > 0.1:
        cv.drawLine(1070, 420, 1190, 360, P(h('F0E8D2'), 8))
        note(cv, 1450, 320, 560, 190, -3, YEL, ['HE GOT UP'], 84)
    for i, s_ in enumerate(('LEFT FOR DEAD', 'TWICE')):
        if c.lt > 0.15 + i * 0.1:
            fit(cv, s_, 1450, 520 + i * 86, 66, 560, INK, None)
    if c.lt > 0.42:
        stamp(cv, 'TRUE', 1400, 740, -8, min(1, (c.lt - 0.42) / 0.12), 120, GREEN)


SHOTS = {f.__name__: f for f in (twice, board_no, board_beck, eye_card, accounts, tally, report, hours, vision, route, altitude, cost_card, book,
                                 board_true)}


# ------------------------------------------------------------------ overlays on 3D shots
def spindrift(cv, c, n=90, a=1.0, speed=1.0):
    """Snow blown flat across the frame, with a few long streaks."""
    Wd.particles(cv, W, H, c.t, n, 0xDDF4F8FF, 7, size=(3, 9), drift=(1900 * speed, 150 * speed), wobble=34)
    for j in range(12):
        ph = (math.sin(j * 12.9898) * 43758.5453) % 1
        x = ((c.t * 3200 * speed * (0.6 + ph)) + ph * 5000) % (W + 1100) - 550
        y = (ph * 7919) % H + 90 * math.sin(c.t * 2 + j)
        cv.drawLine(x, y, x + 420, y + 40, P(0xFFFFFFFF, 10 + 8 * ph, a=0.16 * a))


def blow(cv, c):
    spindrift(cv, c, 90, 0.9, 0.8)


def blizzard(cv, c):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFD8E2F4, a=0.2 + 0.06 * math.sin(c.t * 9)))
    spindrift(cv, c, 200, 1.6, 1.3)


def closing(cv, c):
    """The cloud closing in over the far figure: the frame greys out as the shot goes on."""
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFAAB6D0, a=0.1 + 0.45 * ease(c.k)))
    spindrift(cv, c, 120 + int(120 * c.k), 1.4, 1.1)


def night_storm(cv, c):
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFF9FB4E8, a=0.1 + 0.03 * math.sin(c.t * 9)))
    spindrift(cv, c, 170, 1.2, 1.2)


def snow(cv, c):
    flakes(cv, c.t, 70, 0xCCF4F8FF)


def haze(cv, c):
    """His sight going: a milky white closes in from every side until almost nothing is left."""
    k = ease(c.k * 1.25)
    for i in range(5):
        r = lerp(1700, 300, k) + i * 210
        pa = P(0xFFF4F6FA, 190, a=min(1.0, 0.16 + 0.5 * k))
        pa.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 80))
        cv.drawCircle(960 + 30 * math.sin(c.t * 3 + i), 500 + 24 * math.cos(c.t * 2.3 + i), r, pa)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFFF4F6FA, a=0.72 * k))


def soft(cv, c):
    """A lighter haze at the edges while we look at his face."""
    for i in range(3):
        pa = P(0xFFF4F6FA, 220, a=0.22 + 0.1 * math.sin(c.t * 2 + i))
        pa.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 90))
        cv.drawCircle(960, 500, 1100 + i * 160 + 30 * math.sin(c.t * 1.7 + i), pa)


def wash(cv, c):
    """Snow thrown outward by the rotor."""
    for i in range(110):
        ph = (math.sin(i * 12.9898) * 43758.5453) % 1
        a = (math.sin(i * 78.233) * 43758.5453) % 1 * 6.283
        d = ((c.t * 1.4 + ph) % 1) * 1700
        cv.drawCircle(960 + d * math.cos(a), 600 + d * math.sin(a) * 0.5, 4 + d * 0.012, P(0xFFF4F8FF, a=0.7 * (1 - d / 1800) * min(1, c.k * 2.5)))


def flick(cv, c):
    """Rotor shadow flickering through the cabin."""
    if int(c.t * 15) % 3 == 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(0xFF000000, a=0.08))


def clock(cv, c):
    """The hours going by while the shadow swings: a counter in the corner."""
    blow(cv, c)
    n = 1 + int(14.99 * ease(c.k))
    Wd.text_card(cv, 'HOUR', 300, 120, 64, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, str(n), 300, 300, 170, AMBER, 0xFF000000)


def closed(cv, c):
    snow(cv, c)
    if c.lt > 0.55:
        k = min(1, (c.lt - 0.55) / 0.15)
        cv.save()
        cv.translate(520, 300)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, AMBER, 0xFF000000)
        Wd.text_card(cv, 'CASE 014  CLOSED', 0, 90, 54, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(ice_body=blizzard, col_wide=blow, left_walk=blow, eyes_open=blow, rook_jolt=blow, rook_cairn=snow, blur_pov=haze, eye_cu=soft,
            descend=blow, blizzard_hit=blizzard, lost_group=night_storm, rescuer=night_storm, rescuer_no=night_storm, frozen_hand=snow,
            beck_rise=blow, beck_walks=blow, hollow=blow, heli_land=wash, rook_wrong=snow, signoff=closed, lead_high=closing, rook_up=blow,
            wait_dusk=blow, tents_near=night_storm, huddle=night_storm, rook_hat=blizzard, wander=night_storm, rook_two=snow, dawn_col=snow,
            breath_cu=snow, sundial=clock, hand_look=blow, camp_see=blow, tent_in=blow, tent_out=night_storm, dawn_camp=snow, face_down=blow,
            face_cu=blow, heli_skid=wash, heli_load=wash, cockpit=flick, cairn_stone=snow, flags_cu=snow, doctor_kneel=snow, doctor_leave=snow)


def THUMB(cv, c):
    """1280x720: the 3D still (he gets up out of the snow, iced over, Rook throwing his arms out) and three words on the right."""
    if 'thumb' not in _IMG:
        p = os.path.join(B3D, 'still_thumb.jpg')
        _IMG['thumb'] = skia.Image.open(p) if os.path.exists(p) else None
    if _IMG['thumb'] is not None:
        cv.drawImageRect(_IMG['thumb'], skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    else:
        cv.clear(h('0E1C34'))
    cv.drawRect(skia.Rect(0, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(680, 0), (1280, 0)], [0x00000000, 0xD8061020])))
    Wd.text_card(cv, 'LEFT FOR', 965, 230, 118, 0xFFFFFFFF, 0xFF000000)
    Wd.text_card(cv, 'DEAD', 965, 400, 200, RED, 0xFF000000)
    Wd.text_card(cv, 'TWICE', 965, 560, 150, AMBER, 0xFF000000)
