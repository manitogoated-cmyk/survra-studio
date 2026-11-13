"""Open Case 001 - the Wow! signal. The story is filmed in 3D (world3d.py). This file holds the flat graphic inserts
(the 1977 printout with 6EQUJ5 circled, Ehman's "Wow!", the hydrogen-line chart, the blank follow-up printouts and Rook's
theory wall) and the 2D overlays drawn on top of 3D shots."""
import math
import os

import skia

from concepts.chars import INK, P
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
B3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', '3d')
MONO = skia.Typeface('DejaVu Sans Mono', skia.FontStyle(700, 5, skia.FontStyle.kUpright_Slant))
_IMG = {}
CODE = '6EQUJ5'
RED = 'D8261E'


def rnd(i, salt=0):
    x = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - math.floor(x)


def photo(cv, name, x, y, w_, h_, focus=(0.5, 0.5)):
    """A 3D still (rendered by world3d.STILLS) pinned to the wall as a photograph."""
    if name not in _IMG:
        p = os.path.join(B3D, f'still_{name}.jpg')
        _IMG[name] = skia.Image.open(p) if os.path.exists(p) else None
    img = _IMG[name]
    dst = skia.Rect.MakeXYWH(x - w_ / 2, y - h_ / 2, w_, h_)
    if img is None:
        cv.drawRect(dst, P(h('1E2A4A')))
        return
    iw, ih = img.width(), img.height()
    sw = min(iw, ih * w_ / h_)
    sh = sw * h_ / w_
    cv.drawImageRect(img, skia.Rect.MakeXYWH((iw - sw) * focus[0], (ih - sh) * focus[1], sw, sh), dst,
                     skia.SamplingOptions(skia.CubicResampler.Mitchell()), skia.Paint())


def pinned(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 12, -h_ / 2 + 16, w_, h_), P(0x66000000))
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), P(col))
    cv.drawCircle(0, -h_ / 2 + 30, 20, P(h('E5392F')))
    cv.drawCircle(-5, -h_ / 2 + 25, 7, P(0x88FFFFFF))
    cv.restore()


def card(cv, text, x, y, w_, h_, ang, size, k, col='FFD866'):
    if k <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(1 + 0.5 * (1 - k), 1 + 0.5 * (1 - k))
    pinned(cv, 0, 0, w_, h_, ang, h(col))
    cv.rotate(ang)
    Wd.text_card(cv, text, 0, size * 0.42, size, INK, None)
    cv.restore()


def stamp_at(cv, text, x, y, size, k, col='FFB000', ang=-5):
    if k <= 0:
        return
    k = min(1.0, k)
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(1.7 - 0.7 * k, 1.7 - 0.7 * k)
    Wd.text_card(cv, text, 0, 0, size, h(col), 0xFF000000)
    cv.restore()


# ------------------------------------------------------------------ the printout
def greenbar(cv, y0, rows, row_h, x0=40, x1=W - 40):
    """Continuous fanfold paper: tractor holes down both edges, pale green bands every three rows."""
    cv.drawRect(skia.Rect.MakeLTRB(x0, -400, x1, H + 400), P(h('F2F0E4')))
    for r in range(-6, rows + 6):
        y = y0 + r * row_h
        if (r // 3) % 2 == 0:
            cv.drawRect(skia.Rect.MakeLTRB(x0 + 70, y, x1 - 70, y + row_h), P(h('CFE8C8')))
    for r in range(-12, rows * 2 + 12):
        y = y0 + r * row_h * 0.5
        for x in (x0 + 34, x1 - 34):
            cv.drawCircle(x, y, 12, P(h('2A2622')))
    for r in range(-6, rows + 6, 11):
        y = y0 + r * row_h - 4
        for xx in range(x0 + 70, x1 - 70, 26):
            cv.drawLine(xx, y, xx + 12, y, P(0x55000000, 2))


def column_chars(r, col):
    """What the receiver channels printed: mostly blanks and 1s, sometimes 2-4 (signal-to-noise per 12-second sample)."""
    v = rnd(r * 37 + col, 3)
    return ' ' if v < 0.55 else ('1' if v < 0.86 else ('2' if v < 0.95 else '3'))


def printout_rows(cv, y0, rows, row_h, code_row, code_col=4, ncols=11, size=58, blank=False):
    f = skia.Font(MONO, size)
    cw = f.measureText('0') * 1.9
    xs = 170
    for r in range(-6, rows + 6):
        y = y0 + r * row_h + row_h * 0.78
        for col in range(ncols):
            ch = column_chars(r, col)
            if not blank and col == code_col and 0 <= r - code_row < len(CODE):
                ch = CODE[r - code_row]
            if ch != ' ':
                cv.drawString(ch, xs + col * cw, y, f, P(h('2A2622')))
    return xs + code_col * cw + f.measureText('0') / 2, cw


def red_ellipse(cv, cx, cy, rx, ry, k, width=10):
    if k <= 0:
        return
    path = skia.Path()
    n = 64
    for i in range(int(n * min(1, k)) + 1):
        a = -PI_2 + i / n * 2 * math.pi * 1.06
        x = cx + rx * math.cos(a) * (1 + 0.04 * math.sin(a * 3))
        y = cy + ry * math.sin(a)
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    pt = P(h(RED), width)
    pt.setStrokeCap(skia.Paint.kRound_Cap)
    pt.setStrokeJoin(skia.Paint.kRound_Join)
    cv.drawPath(path, pt)


PI_2 = math.pi / 2


def printout(cv, c):
    """Hook: the 15 August 1977 printout scrolls up; the column 6EQUJ5 gets a red ring."""
    row_h = 92
    y0 = 520 - (1 - min(1, c.lt / 0.5)) * 300 - c.lt * 40
    greenbar(cv, y0, 16, row_h)
    cx, cw = printout_rows(cv, y0, 16, row_h, code_row=3)
    red_ellipse(cv, cx, y0 + 3 * row_h + row_h * 3, cw * 0.62, row_h * 3.3, (c.lt - 0.3) / 0.45)
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(0x22000000))


def wow_write(cv, c):
    """Close on the code: the red pen writes Wow! beside it."""
    row_h = 128
    cv.save()
    cv.translate(540, 900)
    cv.rotate(-4)
    cv.scale(1.0 + 0.05 * c.k, 1.0 + 0.05 * c.k)
    cv.translate(-540, -900)
    y0 = 300
    greenbar(cv, y0, 14, row_h)
    cx, cw = printout_rows(cv, y0, 14, row_h, code_row=2, code_col=3, ncols=7, size=84)
    red_ellipse(cv, cx, y0 + 2 * row_h + row_h * 3, cw * 0.62, row_h * 3.3, 1.0, 12)
    k = max(0.0, min(1.0, (c.lt - 0.15) / 0.6))
    f = skia.Font(skia.Typeface('DejaVu Serif', skia.FontStyle(700, 5, skia.FontStyle.kItalic_Slant)), 150)
    tw = f.measureText('Wow!')
    x = cx + 110
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(x - 10, 0, x + tw * k, H))
    cv.drawString('Wow!', x, y0 + row_h * 5.6, f, P(h(RED)))
    cv.restore()
    if 0 < k < 1:
        px, py = x + tw * k, y0 + row_h * 5.3
        cv.save()
        cv.translate(px, py)
        cv.rotate(35)
        cv.drawRect(skia.Rect.MakeLTRB(-14, -260, 14, 0), P(h('B81E18')))
        cv.drawRect(skia.Rect.MakeLTRB(-14, -300, 14, -250), P(h('FFC233')))
        cv.restore()
    cv.restore()


def line_chart(cv, c):
    """The receiver's channels side by side: noise everywhere, one spike right by the hydrogen line."""
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1230')), (1, h('04060E'))])
    for j in range(0, H, 80):
        cv.drawLine(0, j, W, j, P(0x14FFFFFF, 2))
    base, x0, x1 = 1180, 90, W - 90
    cv.drawLine(x0, base, x1, base, P(0x88FFFFFF, 4))
    rise = 1 - (1 - min(1, max(0, (c.lt - 0.2) / 0.35))) ** 3
    path = skia.Path()
    n = 50
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        noise = 26 * rnd(i + int(c.t * 8) * 51, 7)
        peak = 620 * rise * math.exp(-((i - 26) ** 2) / 1.2)
        y = base - noise - peak
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    glow = P(h('FFB000'), 16, a=0.25)
    cv.drawPath(path, glow)
    cv.drawPath(path, P(h('FFB000'), 7))
    Wd.text_card(cv, 'FREQUENCY', 540, base + 90, 52, 0xAAFFFFFF, None, weight=700)
    xp = x0 + (x1 - x0) * 26 / n
    if rise > 0.6:
        cv.drawLine(xp, base - 660, xp, 360, P(0x88FFFFFF, 3))
        stamp_at(cv, 'HYDROGEN LINE', 540, 300, 96, (c.lt - 0.45) / 0.12, 'FFFFFF', -2)
        stamp_at(cv, '1420 MHz', 540, 420, 84, (c.lt - 0.6) / 0.12, 'FFB000', 3)


def blank_page(cv, c):
    """The follow-up searches: page after page of nothing."""
    row_h = 92
    y0 = 300 - c.lt * 900
    greenbar(cv, y0, 30, row_h)
    printout_rows(cv, y0, 30, row_h, code_row=0, blank=True)
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(0x33000000))
    stamp_at(cv, 'NOTHING', 540, 860, 190, (c.lt - 0.25) / 0.12, 'E5392F', -6)


def theory_wall(cv, t):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2A2A44')), (1, h('12121F'))])
    for j in range(0, H + 1, 96):
        cv.drawLine(0, j, W, j, P(0x12FFFFFF, 2))
    Wd.particles(cv, W, H, t, 60, Wd.alpha(h('FFFFFF'), 0.5), 9, size=(1, 3), drift=(0, -6), wobble=4, twinkle=True)
    cv.drawRect(skia.Rect.MakeLTRB(16, 16, W - 16, H - 16), P(h('FF7A1A'), 10))


def theory_board(cv, c):
    """Rook's wall: the cloud on one side, the telescope on the other, a question mark over both."""
    theory_wall(cv, c.t)
    for (nm, x, y, ang, at_) in (('cloud', 290, 640, -4, 0.0), ('ear', 790, 640, 3, 0.3)):
        kk = min(1, max(0, (c.lt - at_) / 0.18))
        if kk <= 0:
            continue
        s = 0.75 + 0.25 * kk
        pinned(cv, x, y, 470 * s, 420 * s, ang)
        cv.save()
        cv.translate(x, y)
        cv.rotate(ang)
        cv.scale(s, s)
        photo(cv, nm, 0, 22, 420, 340, (0.5, 0.45))
        cv.restore()
    card(cv, 'A GAS CLOUD?', 290, 930, 470, 140, -4, 58, min(1, max(0, (c.lt - 0.12) / 0.14)))
    card(cv, 'OR SOMEONE SAYING HELLO?', 560, 1110, 920, 140, 2, 58, min(1, max(0, (c.lt - 0.45) / 0.14)), 'F4EEDF')
    q = (c.lt - 0.7) / 0.15
    if q > 0:
        cv.save()
        cv.translate(540, 300)
        cv.rotate(10 * math.sin(c.t * 3))
        cv.scale(1.7 - 0.7 * min(1, q), 1.7 - 0.7 * min(1, q))
        Wd.text_card(cv, '?', 0, 90, 260, h('FFB000'), 0xFF000000)
        cv.restore()


SHOTS = {f.__name__: f for f in (printout, wow_write, line_chart, blank_page, theory_board)}


# ------------------------------------------------------------------ overlays on 3D shots
def stamp(cv, c, text, x, y, size, at=0.25, col='FFB000', ang=-5):
    if c.lt > at:
        stamp_at(cv, text, x, y, size, (c.lt - at) / 0.12, col, ang)


def twinkle(cv, c):
    Wd.particles(cv, W, H, c.t, 24, Wd.alpha(h('FFFFFF'), 0.35), 31, size=(1, 3), drift=(0, -4), wobble=3, twinkle=True)


def hit_flash(cv, c):
    if c.k > 0.8:
        a = min(1, (c.k - 0.8) / 0.2)
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(0xFFFFFFFF, a=0.75 * a))


def seventy_two(cv, c):
    twinkle(cv, c)
    if c.prm.get('nostamp'):
        return
    stamp(cv, c, '72 SECONDS', 540, 560, 150, 0.35, 'FFB000', -4)


def never(cv, c):
    stamp(cv, c, 'NEVER HEARD AGAIN', 540, 430, 92, 0.45, 'E5392F', 3)


def big_ear(cv, c):
    stamp(cv, c, 'BIG EAR', 540, 430, 170, 0.25, 'FFFFFF', -4)


def listening(cv, c):
    stamp(cv, c, c.prm.get('stamp', 'LISTENING'), 540, 470, 140 if 'stamp' not in c.prm else 84, 0.3, 'FFB000', 4)


def wow_stamp(cv, c):
    stamp(cv, c, 'WOW!', 540, 430, 200, 0.25, RED, -6)


def hydrogen(cv, c):
    stamp(cv, c, '1420 MHz', 540, 430, 140, 0.4, 'FFB000', -3)


def again(cv, c):
    twinkle(cv, c)
    stamp(cv, c, 'AGAIN. AND AGAIN.', 540, 430, 86, 0.3, 'FFFFFF', 3)


def flare_fx(cv, c):
    if 0.25 < c.k < 0.6:
        a = math.sin((c.k - 0.25) / 0.35 * math.pi)
        cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), P(h('DFF2FF'), a=0.35 * a))
    stamp(cv, c, '2024 HYPOTHESIS', 540, 430, 100, 0.55, 'FFFFFF', -3)


def warp(cv, c):
    """Star streaks rushing past as the signal travels."""
    for i in range(48):
        ang = rnd(i, 50) * 2 * math.pi
        r0 = ((c.t * 900 + rnd(i, 51) * 1400) % 1400) + 60
        L = 60 + 0.25 * r0
        x0, y0 = 540 + math.cos(ang) * r0, 760 + math.sin(ang) * r0
        x1, y1 = 540 + math.cos(ang) * (r0 + L), 760 + math.sin(ang) * (r0 + L)
        cv.drawLine(x0, y0, x1, y1, P(0xFFFFFFFF, 3 + 3 * rnd(i, 52), a=0.45))


def your_theory(cv, c):
    stamp(cv, c, 'YOUR THEORY?', 540, 430, 116, 0.35, 'FFB000', -4)


def comments(cv, c):
    stamp(cv, c, 'COMMENT YOUR THEORY', 540, 430, 70, 0.3, 'FFFFFF', 3)


def still_open(cv, c):
    if c.lt > 0.5:
        k = min(1, (c.lt - 0.5) / 0.15)
        cv.save()
        cv.translate(540, 400)
        cv.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
        Wd.text_card(cv, 'SURVRA', 0, 0, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'OPEN CASE 001  STILL OPEN', 0, 90, 50, 0xFFFFFFFF, 0xFF000000)
        cv.restore()


OVER = dict(beam_hit=hit_flash, ear_night=seventy_two, ear_sweep=twinkle, ear_dark=never, ear_aerial=big_ear, horn_cu=listening,
            ehman_shock=wow_stamp, rook_chart=hydrogen, ear_search=again, flare=flare_fx, rook_cam=your_theory, rook_comment=comments,
            signoff=still_open, wave_earth=warp, rook_plane=twinkle, rook_listen=twinkle, cloud=twinkle)
