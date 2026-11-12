"""k001 - Juliane Koepcke. World: 1971 Peruvian Amazon. Storm sky, a four-prop airliner, free fall,
rainforest floor, a jungle stream, a stilt hut, a river and today's research station.
Everything below is drawn for this story only."""
import math

import skia

from engine3 import world as Wd
from engine3.cast import Look
from engine3.kesta import INK, P, circle, oval, poly, pose, seg, walk, keyframes, lerp

W, H = 1080, 1920
h = Wd.hexc
PAL = dict(
    far=h('1E4A3A'), mid=h('2E6B4A'), near=h('3F8A4E'), hi=h('6FBF5A'), dark=h('12301F'),
    shaft=h('FFE9A8'), mud=h('5A4028'), mud_d=h('3E2C1C'), water=h('4E8F86'), water_d=h('2F5A58'),
    storm_top=h('141833'), storm_bot=h('3A3F66'), cloud=h('5A6090'), cloud_d=h('3A3F66'),
    sky=h('8FD3E8'), sky2=h('E8F6F2'), seat=h('2F5C9A'), seat_d=h('234776'), metal=h('B8BEC8'),
    river=h('8A6A3A'), river_d=h('5E4626'),
)
JULIANE = Look(skin=h('F0C8A6'), skin_sh=h('D4A584'), hair=h('8A6A40'), hair_style='long', top=h('E9E2D0'),
               top_sh=h('CFC6B0'), top_style='dress', shoes=h('9A7A50'), eye=h('4A6A8A'))
FATHER = Look(skin=h('EDC3A0'), skin_sh=h('D0A17E'), hair=h('9A9A9A'), beard='full', glasses=True, top=h('B9A57A'),
              top_sh=h('A08E64'), accent=h('8A7A54'), pants=h('6B5E45'), hair_style='short')
WORKER1 = Look(skin=h('A06A45'), skin_sh=h('84553A'), hair=h('1A1410'), hair_style='cap', hat=h('7A2E2E'),
               top=h('5C8A4A'), top_sh=h('4A7238'), pants=h('4A4038'), shoes=h('2A2420'))
WORKER2 = Look(skin=h('8E5A38'), skin_sh=h('74482C'), hair=h('1A1410'), hair_style='wide_hat', hat=h('CBB27A'),
               top=h('D8D0B8'), top_sh=h('BDB49C'), beard='moustache', pants=h('3A4250'), width=1.15)

SIT = pose('stand', crouch=16, fFx=17, fBx=15, fFy=-2, fBy=-2, lean=-6, aFu=30, aFl=-60, aBu=20, aBl=-60)


# ------------------------------------------------------------------ world pieces
def jungle(cv, t, drift=0.0, light=1.0, night=False, ground_y=1500, fog=True, shafts=True):
    top = h('0E2A22') if night else h('2E7A5A')
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('071711') if night else h('9ED8B0')), (0.45, top), (1, h('0A1F17'))])
    if shafts and not night:
        for i, x in enumerate((180, 520, 860)):
            pa = P(Wd.alpha(PAL['shaft'], 0.10 * light + 0.04 * math.sin(t + i)))
            path = skia.Path()
            path.moveTo(x - 40 + drift * 0.1, 0)
            path.lineTo(x + 60 + drift * 0.1, 0)
            path.lineTo(x + 260, ground_y)
            path.lineTo(x + 60, ground_y)
            path.close()
            cv.drawPath(path, pa)
    for i, (y, c, amp, sd, sp) in enumerate([(780, PAL['far'], 260, 11, 0.15), (1000, PAL['mid'], 300, 12, 0.35), (1250, PAL['near'], 260, 13, 0.6)]):
        cc = Wd.mix(c, h('06140F'), 0.55) if night else c
        Wd.ridge(cv, W, H, y, amp, cc, sd, rough=7, x_off=drift * sp)
        for k in range(4):
            tx = ((k * 330 + sd * 47 - drift * sp) % (W + 400)) - 200
            Wd.tree_jungle(cv, tx, y + 80, 520 + i * 160, Wd.mix(h('3A2A1C'), cc, 0.4), cc, Wd.mix(cc, 0xFF000000, 0.25), t, seed=sd * 10 + k, ink=None if i < 2 else INK, buttress=i == 2)
        if fog and not night:
            Wd.mist(cv, W, y + 60, 120, Wd.alpha(h('DFF5E8'), 0.10), t, seed=sd, speed=15)
    Wd.fill(cv, 0, ground_y, W, H, Wd.mix(PAL['mud'], 0xFF000000, 0.4 if night else 0.0))
    Wd.vgrad(cv, 0, ground_y, W, H, [(0, Wd.alpha(PAL['dark'], 0.0)), (1, Wd.alpha(PAL['dark'], 0.8))])


def foreground_ferns(cv, t, y=1880, drift=0.0, night=False):
    c = Wd.mix(PAL['near'], 0xFF000000, 0.5 if night else 0.15)
    for i, x in enumerate((-60, 260, 640, 980, 1180)):
        xx = ((x - drift) % (W + 400)) - 200
        Wd.fern(cv, xx, y, 520, -110 + i * 17, c, t, sway=4, vein=Wd.mix(c, 0xFFFFFFFF, 0.25))


def stream(cv, t, y0=1380, y1=1920, wide=1.0, flow=1.0, brown=False):
    deep, light = (PAL['river_d'], PAL['river']) if brown else (PAL['water_d'], PAL['water'])
    path = skia.Path()
    path.moveTo(W * 0.5 - 90 * wide, y0)
    path.lineTo(W * 0.5 + 90 * wide, y0)
    path.lineTo(W * 0.5 + 520 * wide, y1)
    path.lineTo(W * 0.5 - 520 * wide, y1)
    path.close()
    cv.save()
    cv.clipPath(path, True)
    Wd.river(cv, W, y0, y1, deep, light, t, flow=flow, seed=7)
    cv.restore()
    cv.drawPath(path, P(INK, 4))
    for i in range(7):
        k = i / 6
        Wd.rock(cv, W * 0.5 + (-1) ** i * lerp(110, 560, k) * wide, lerp(y0, y1, k) + 10, lerp(18, 70, k), h('6F6A5E'), h('8C877A'), seed=i)


def storm_sky(cv, t, flash=0.0, drift=0.0):
    Wd.vgrad(cv, 0, 0, W, H, [(0, PAL['storm_top']), (1, PAL['storm_bot'])])
    for i in range(9):
        x = ((i * 260 - drift * (0.3 + 0.1 * (i % 3))) % (W + 600)) - 300
        Wd.cloud(cv, x, 300 + (i * 211) % 1500, 200 + (i % 3) * 70, Wd.mix(PAL['cloud'], 0xFFFFFFFF, flash * 0.5), PAL['cloud_d'])
    Wd.rain(cv, W, H, t, density=120, c=Wd.alpha(h('B9C8FF'), 0.35))
    if flash > 0:
        Wd.fill(cv, 0, 0, W, H, Wd.alpha(0xFFFFFFFF, flash * 0.6))


def seat_row(cv, x, y, s, ang, t, girl=None, fall=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    for i in range(3):
        sx = (i - 1) * s * 0.36
        poly(cv, [(sx - s * 0.16, -s * 0.5), (sx + s * 0.16, -s * 0.5), (sx + s * 0.17, 0), (sx - s * 0.17, 0)], PAL['seat'], INK, 3)
        poly(cv, [(sx - s * 0.18, 0), (sx + s * 0.18, 0), (sx + s * 0.2, s * 0.14), (sx - s * 0.2, s * 0.14)], PAL['seat_d'], INK, 3)
        cv.drawLine(sx - s * 0.12, -s * 0.42, sx + s * 0.12, -s * 0.42, P(Wd.mix(PAL['seat'], 0xFFFFFFFF, 0.3), 5))
        seg(cv, (sx, s * 0.14), (sx, s * 0.45), s * 0.03, PAL['metal'], INK, 2)
    if girl:
        girl(s)
        seg(cv, (-s * 0.17, s * 0.02), (s * 0.17, s * 0.02), s * 0.025, h('C9C2B0'), INK, 2)  # lap belt
    cv.restore()


def journal_lines(cv, x, y, lines, k, size=58, col=h('3A2A1C')):
    for i, ln in enumerate(lines):
        kk = max(0.0, min(1.0, k * len(lines) * 1.4 - i))
        if kk <= 0:
            continue
        Wd.text_card(cv, ln, x, y + i * size * 1.35, size, Wd.alpha(col, kk), None)


# ------------------------------------------------------------------ shots
def freefall_hook(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('9ED0F0')), (1, h('E8F4EC'))])
    for i in range(10):
        y = ((i * 260 - t * 2600) % (H + 600)) - 300
        Wd.cloud(cv, (i * 377) % W, y, 140 + (i % 3) * 60, Wd.alpha(0xFFFFFFFF, 0.85), Wd.alpha(h('C8DCEC'), 0.8))
    Wd.ridge(cv, W, H, H + 200 - 900 * k, 300, PAL['mid'], 4, rough=6)
    seat_row(cv, W / 2, 900, 420, math.sin(t * 5) * 25 + t * 60, t, girl=lambda s_: c.person(JULIANE, -s_ * 0.06, s_ * 0.13, s_ * 0.78, SIT, expr='scared', look=(0, 1)))
    for i in range(16):
        x = (i * 71 + 30) % W
        y = ((i * 191 - t * 3800) % H)
        cv.drawLine(x, y, x, y + 140, P(Wd.alpha(0xFFFFFFFF, 0.5), 4))


def canopy_reveal(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('7EC7E6')), (0.5, h('CFEFE4')), (1, h('3F8A4E'))])
    Wd.cloud(cv, 250, 380, 170, 0xFFFFFFFF, h('DCEAF2'))
    Wd.cloud(cv, 850, 520, 130, 0xFFFFFFFF, h('DCEAF2'))
    Wd.ridge(cv, W, H, 1250, 200, PAL['far'], 21, rough=8)
    for i in range(12):
        Wd.tree_jungle(cv, (i * 103) % W, 1500, 520, h('3A2A1C'), PAL['mid'], PAL['far'], t, seed=40 + i, buttress=False)
    # thin silver stream far below
    path = skia.Path()
    path.moveTo(-20, 1700)
    path.cubicTo(300, 1640, 600, 1780, 1100, 1700)
    cv.drawPath(path, P(h('BFEAF0'), 10))
    # tiny figure by the stream
    circle(cv, 560, 1700, 7, h('E9E2D0'), INK, 2)
    # Kesta on a giant branch
    seg(cv, (-40, 1180), (720, 1120), 46, h('5A3E28'), INK, 4)
    Wd.leaf(cv, 690, 1120, 120, -20, PAL['hi'])
    Wd.leaf(cv, 690, 1120, 110, 30, PAL['near'])
    kp = keyframes(c.lt, [(0, pose('stand')), (0.5, pose('point_down')), (2, pose('point_down'))])
    c.kesta(400, 1105, 520, kp, expr='awed', look=(0.6, 1), wind=0.7)


def flare_fire(cv, c):
    t, lt = c.t, c.lt
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1020')), (1, h('1A2440'))])
    Wd.particles(cv, W, H, t, 70, Wd.alpha(0xFFFFFFFF, 0.6), 5, size=(1, 3), drift=(0, 0), twinkle=True)
    # lighthouse silhouette - where Kesta's stories start
    poly(cv, [(820, 1500), (900, 1500), (880, 1060), (840, 1060)], h('1F2A44'), None)
    poly(cv, [(828, 1060), (892, 1060), (884, 1000), (836, 1000)], h('2A3656'), None)
    Wd.glow(cv, 860, 1030, 40, h('FFE9A8'), 0.7)
    Wd.fill(cv, 0, 1500, W, H, h('101828'))
    kp = keyframes(lt, [(0, pose('stand')), (0.35, pose('flare_aim')), (0.9, pose('flare_fire'))])
    glow = max(0.0, (lt - 0.8) * 3)
    c.kesta(430, 1500, 820, kp, expr='determined', goggles='down' if lt > 0.6 else 'up', prop_glow=min(1, glow), wind=0.3)
    if glow > 0:
        Wd.glow(cv, 640, 470 - 600 * min(1, glow * 0.3), 30 + 40 * glow, h('FFB000'), min(1, glow))


def sky_kesta(cv, c):
    t, k = c.t, c.k
    flash = 1.0 if 0.55 < k < 0.62 else 0.0
    storm_sky(cv, t, flash, drift=t * 120)
    Wd.cloud(cv, 380, 1460, 380, PAL['cloud'], PAL['cloud_d'])
    Wd.cloud(cv, 800, 1520, 300, PAL['cloud'], PAL['cloud_d'])
    Wd.airliner(cv, lerp(-300, 1300, k), 760, 900, h('E8E8EE'), h('C0392B'), h('9FD4F0'), props_t=t)
    kp = keyframes(c.lt, [(0, pose('stand')), (0.4, pose('point_up'))])
    c.kesta(330, 1360, 560, kp, expr='worried', look=(0.6, -1), wind=1.0)


def plane_storm(cv, c):
    t, k = c.t, c.k
    storm_sky(cv, t, 0.0, drift=t * 300)
    # towering anvil cloud
    Wd.cloud(cv, 760, 900, 520, h('4A5080'), h('2A2F55'))
    Wd.cloud(cv, 760, 520, 400, h('4A5080'), h('2A2F55'))
    Wd.airliner(cv, lerp(150, 560, k), 1050, 1100, h('E8E8EE'), h('C0392B'), h('9FD4F0'), ang=-4, props_t=t)


def strike(cv, c):
    t, k = c.t, c.k
    fl = max(0.0, 1 - abs(k - 0.3) * 6)
    storm_sky(cv, t, fl, drift=t * 200)
    Wd.airliner(cv, 560, 1000, 1200, h('E8E8EE'), h('C0392B'), h('9FD4F0'), ang=-3 + math.sin(t * 40) * fl * 3, props_t=t)
    if 0.22 < k < 0.55:
        Wd.bolt(cv, 520, -50, 1010, seed=int(t * 20) % 5 + 3, width=10, branches=3)
        Wd.glow(cv, 520, 1010, 140, h('CFE6FF'), 0.9)


def breakup(cv, c):
    t, k = c.t, c.k
    storm_sky(cv, t, max(0, 0.5 - k), drift=t * 200)
    Wd.airliner(cv, 540, 980 + k * 200, 1150, h('E8E8EE'), h('C0392B'), h('9FD4F0'), ang=6 * k, props_t=t, breakup=min(1, k * 1.6))
    R = Wd.Rand(9)
    for i in range(26):
        ang = R(0, 6.28)
        r = k * R(200, 700)
        x, y = 540 + math.cos(ang) * r, 980 + math.sin(ang) * r + k * k * 300
        cv.save()
        cv.translate(x, y)
        cv.rotate(t * R(-400, 400))
        poly(cv, [(-14, -6), (16, -9), (12, 8), (-10, 6)], R.pick([h('E8E8EE'), h('C0392B'), h('8A8F99')]), INK, 2)
        cv.restore()
    Wd.glow(cv, 540, 980, 200 * (1 - k), h('FFB000'), 0.8 * (1 - k))


def seatrow_fall(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, PAL['storm_bot']), (1, h('6C7AA0'))])
    for i in range(12):
        y = ((i * 230 - t * 3200) % (H + 500)) - 250
        Wd.cloud(cv, (i * 311) % W, y, 120 + (i % 4) * 40, Wd.alpha(h('8A93B8'), 0.8), None)
    seat_row(cv, W / 2, 960, 460, t * 140, t, girl=lambda s_: c.person(JULIANE, -s_ * 0.06, s_ * 0.13, s_ * 0.78, SIT, expr='shocked', look=(0, 0.5)))
    for i in range(18):
        x = (i * 63 + 20) % W
        y = ((i * 171 - t * 4200) % H)
        cv.drawLine(x, y, x, y + 160, P(Wd.alpha(0xFFFFFFFF, 0.4), 3))


def kesta_falling(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('5A6A98')), (1, h('9AB0C8'))])
    for i in range(12):
        y = ((i * 230 - t * 3000) % (H + 500)) - 250
        Wd.cloud(cv, (i * 271) % W, y, 110 + (i % 4) * 50, Wd.alpha(h('D8E0EE'), 0.75), None)
    seat_row(cv, 760, 700, 320, t * 140 + 30, t, girl=lambda s_: c.person(JULIANE, -s_ * 0.06, s_ * 0.13, s_ * 0.78, SIT, expr='scared', look=(0, 0.5)))
    kp = pose('point', lean=-20, head=-10, fFx=12, fBx=-12, fFy=-8, fBy=-4, aBu=-60, aBl=-30)
    cv.save()
    cv.translate(330, 1200)
    cv.rotate(-25 + math.sin(t * 3) * 6)
    c.kesta(0, 300, 640, kp, expr='scared', goggles='down', wind=1.5, look=(1, -0.5))
    cv.restore()


def canopy_rush(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, PAL['far']), (1, PAL['dark'])])
    z = 0.4 + 2.6 * k ** 2
    cv.save()
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-W / 2, -H / 2)
    R = Wd.Rand(5)
    for i in range(40):
        x, y = R(-200, W + 200), R(-200, H + 200)
        Wd.cloud(cv, x, y, R(80, 180), R.pick([PAL['mid'], PAL['near'], PAL['hi']]), PAL['far'], INK)
    cv.restore()
    seat_row(cv, W / 2, 1000, 260 + 300 * k, t * 140, t)
    if k > 0.75:
        for i in range(30):
            a = i * 0.7
            r = (k - 0.75) * 3000
            Wd.leaf(cv, W / 2 + math.cos(a) * r, 1000 + math.sin(a) * r, 70, math.degrees(a) + t * 300, PAL['hi'])


def forest_wake(cv, c):
    t, k = c.t, c.k
    jungle(cv, t, drift=0, light=1.2, ground_y=1450)
    seat_row(cv, 470, 1420, 380, -14, t)
    cv.save()
    cv.translate(600, 1600)
    cv.rotate(-88)
    c.person(JULIANE, 0, 0, 440, pose('stand', aFu=40, aFl=-40), expr='wince' if k < 0.5 else 'sad', look=(0.5, 0))
    cv.restore()
    for i in range(7):
        oval(cv, 120 + i * 140, 1600 + (i % 2) * 40, 50, 14, Wd.alpha(PAL['hi'], 0.6), None)
    foreground_ferns(cv, t, y=1920)
    Wd.particles(cv, W, H, t, 26, Wd.alpha(PAL['shaft'], 0.8), 31, size=(2, 4), drift=(8, -10))


def kesta_inspect(cv, c):
    t, lt, k = c.t, c.lt, c.k
    jungle(cv, t, drift=200, ground_y=1450)
    cv.save()
    cv.translate(300, 1610)
    cv.rotate(-88)
    c.person(JULIANE, 0, 0, 400, pose('stand', aFu=60, aFl=-80), expr='wince')
    cv.restore()
    kp = keyframes(lt, [(0, pose('crouch')), (0.4, pose('inspect'))])
    c.kesta(640, 1600, 560, kp, facing=-1, expr='worried', look=(1, 0.6))
    kk = Wd.journal_page(cv, 120, 220, 840, 520, max(0, lt - 0.3), title='FIELD NOTES')
    if kk > 0:
        journal_lines(cv, 540, 430, ['BROKEN COLLARBONE', 'ONE EYE SWOLLEN', 'ALONE'], kk * min(1, max(0, lt - 0.4) / max(0.3, c.d - 0.8)))
    foreground_ferns(cv, t, y=1940, drift=100)


def eye_close(cv, c):
    t, k = c.t, c.k
    jungle(cv, t, drift=400, ground_y=1700, shafts=True)
    c.person(JULIANE, 470, 2250, 1500, pose('stand', head=-6), expr='wince' if k < 0.6 else 'sad', look=(-0.5, 0))
    Wd.vgrad(cv, 0, 0, W, H, [(0, Wd.alpha(0xFF000000, 0.35)), (0.4, Wd.alpha(0xFF000000, 0.0)), (1, Wd.alpha(0xFF000000, 0.4))])


def father_memory(cv, c):
    t, lt, k = c.t, c.lt, c.k
    jungle(cv, t, drift=600, ground_y=1500)
    # memory bubble: warm, sepia, wobbling edge
    r = 400 * Wd.Rand(0)(1, 1) * min(1, lt / 0.3)
    cv.save()
    path = skia.Path()
    path.addCircle(560, 760, max(1, r))
    cv.clipPath(path, True)
    Wd.vgrad(cv, 0, 300, W, 1200, [(0, h('F6D9A0')), (1, h('C48A4A'))])
    Wd.fill(cv, 0, 900, W, 1300, h('7A5A3A'))
    p2 = skia.Path()
    p2.moveTo(160, 1000)
    p2.cubicTo(400, 940, 700, 1080, 980, 960)
    cv.drawPath(p2, P(h('D8F0F0'), 30))
    c.person(FATHER, 470, 1010, 420, pose('point_down', aFu=95, aFl=-5, hF='point2', crouch=6, fFx=9), expr='happy', speaking=True)
    c.person(JULIANE, 690, 1010, 300, pose('stand', head=6), facing=-1, expr='curious')
    cv.restore()
    cv.drawCircle(560, 760, max(1, r), P(h('FFE2A8'), 12))
    kp = pose('stand', head=-8)
    c.kesta(800, 1820, 600, kp, facing=-1, expr='awed', look=(0.5, -1))


def stream_map(cv, c):
    t, lt, k = c.t, c.lt, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2E7A5A')), (1, h('12301F'))])
    Wd.journal_page(cv, 80, 220, 920, 1300, lt, title='FOLLOW THE WATER')
    kk = min(1.0, max(0.0, (lt - 0.15) / max(0.4, c.d - 0.5)))
    pts = [(260, 520), (320, 700), (420, 860), (560, 1000), (700, 1140), (820, 1320)]
    widths = [6, 10, 18, 28, 40]
    for i in range(len(pts) - 1):
        seg_k = max(0.0, min(1.0, kk * 5 - i))
        if seg_k <= 0:
            continue
        a, b = pts[i], pts[i + 1]
        e = (lerp(a[0], b[0], seg_k), lerp(a[1], b[1], seg_k))
        cv.drawLine(*a, *e, P(h('3A7AB0'), widths[i]))
    labels = [('small stream', 330, 650), ('bigger stream', 470, 860), ('river', 700, 1060)]
    for i, (lb, x, y) in enumerate(labels):
        if kk * 5 > i * 1.6 + 0.6:
            Wd.text_card(cv, lb, x + 120, y, 40, h('3A2A1C'), None, weight=700)
    if kk > 0.85:
        for i in range(3):
            Wd.hut(cv, 760 + i * 70, 1400, 90, h('C9A46A'), h('8A6A3A'), h('6B4E2A'), stilts=False)
        Wd.text_card(cv, 'PEOPLE', 820, 1470, 56, h('C0392B'), None)
    kp = pose('journal')
    c.kesta(250, 1880, 520, kp, expr='smirk', look=(0.5, -0.5))


def kesta_stream(cv, c):
    t, lt, k = c.t, c.lt, c.k
    jungle(cv, t, drift=900, ground_y=1380)
    stream(cv, t, 1380, 1920, wide=0.9, flow=1.2)
    kp = keyframes(lt, [(0, pose('stand')), (0.3, pose('point', aFu=70, aFl=5))])
    c.kesta(250, 1680, 600, kp, expr='determined', look=(0.8, 0.6))
    foreground_ferns(cv, t, y=1950, drift=300)


def wade(cv, c):
    t, k = c.t, c.k
    dr = t * 160
    jungle(cv, t, drift=dr, ground_y=1300)
    stream(cv, t, 1300, 1920, wide=1.3, flow=1.6)
    cv.save()
    p = walk(t, speed=0.8)
    c.person(JULIANE, 520, 1720, 520, p, expr='determined', look=(1, 0.2), wet=1)
    cv.restore()
    for i in range(6):  # water around her legs
        oval(cv, 520 + math.sin(t * 4 + i) * 60, 1650 + i * 6, 170 - i * 18, 18, Wd.alpha(h('BFEAF0'), 0.35), None)
    Wd.fill(cv, 0, 1660, W, H, Wd.alpha(PAL['water_d'], 0.55))
    foreground_ferns(cv, t, y=1950, drift=dr * 1.6)


def swim(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('A8DCC8')), (0.4, h('3F8A4E')), (1, h('12301F'))])
    Wd.ridge(cv, W, H, 900, 240, PAL['mid'], 61, x_off=t * 80)
    Wd.ridge(cv, W, H, 1050, 180, PAL['near'], 62, x_off=t * 140)
    Wd.river(cv, W, 1100, H, PAL['river_d'], PAL['river'], t, flow=1.4, seed=8)
    stroke = math.sin(t * 5)
    p = pose('stand', aFu=150 * (0.5 + 0.5 * stroke), aFl=-10, aBu=150 * (0.5 - 0.5 * stroke), aBl=-10, fFx=10, fBx=-10)
    cv.save()
    cv.translate(330, 1400)
    cv.rotate(78)
    c.person(JULIANE, 0, 0, 420, p, expr='determined', wet=1)
    cv.restore()
    Wd.fill(cv, 0, 1400, W, H, Wd.alpha(PAL['river_d'], 0.7))
    for i in range(5):
        oval(cv, 440 + i * 60 + stroke * 20, 1400, 80, 10, Wd.alpha(0xFFFFFFFF, 0.5), None)
    # Kesta keeps pace on a log
    seg(cv, (40, 1500), (420, 1480), 54, h('5A3E28'), INK, 4)
    c.kesta(220, 1470, 420, walk(t, 1.0), expr='worried', look=(1, 0), speed=0.5)


def sweets(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3F8A4E')), (1, h('1E4A3A'))])
    Wd.particles(cv, W, H, t, 30, Wd.alpha(PAL['shaft'], 0.6), 12, size=(3, 7), drift=(0, -20))
    # big hands holding a paper bag of sweets
    for sx in (-1, 1):
        oval(cv, 540 + sx * 260, 1300, 150, 110, JULIANE.skin, INK, 4)
    poly(cv, [(380, 1260), (700, 1260), (680, 820), (400, 820)], h('E8D9B5'), INK, 5)
    poly(cv, [(400, 820), (680, 820), (660, 760), (420, 760)], h('D8C49A'), INK, 4)
    R = Wd.Rand(3)
    for i in range(9):
        x = 430 + (i % 3) * 90 + R(-10, 10)
        y = 900 + (i // 3) * 110 + math.sin(t * 3 + i) * 6
        col = R.pick([h('E74C3C'), h('F1C40F'), h('2ECC71'), h('9B59B6')])
        cv.save()
        cv.translate(x, y)
        cv.rotate(t * 40 + i * 30)
        oval(cv, 0, 0, 40, 26, col, INK, 3)
        poly(cv, [(-40, 0), (-62, -16), (-62, 16)], col, INK, 3)
        poly(cv, [(40, 0), (62, -16), (62, 16)], col, INK, 3)
        cv.restore()


def kesta_bank(cv, c):
    t, k = c.t, c.k
    dr = t * 260
    jungle(cv, t, drift=dr, ground_y=1450)
    stream(cv, t, 1450, 1920, wide=0.7, flow=1.4)
    c.person(JULIANE, 760, 1760, 360, walk(t, 0.7), expr='exhausted' if False else 'sad', wet=1)
    c.kesta(320, 1560, 560, walk(t, 1.0), expr='determined', look=(1, 0.2), speed=0.6)
    foreground_ferns(cv, t, y=1960, drift=dr * 1.5)


def night(cv, c):
    t, k = c.t, c.k
    jungle(cv, t, drift=0, night=True, ground_y=1450, shafts=False)
    Wd.rain(cv, W, H, t, density=90, c=Wd.alpha(h('9FC8E0'), 0.3))
    Wd.particles(cv, W, H, t, 30, Wd.alpha(h('E8FF7A'), 0.9), 77, size=(3, 5), drift=(10, -5), wobble=40, twinkle=True)
    Wd.tree_jungle(cv, 780, 1520, 900, h('2A1E14'), h('0E2A22'), h('081A14'), t, seed=99)
    c.person(JULIANE, 700, 1560, 300, pose('crouch', aFu=40, aFl=-150, aBu=30, aBl=-150, hF='fist', hB='fist', head=14), facing=-1, expr='sad')
    c.kesta(280, 1600, 480, pose('sad'), expr='sad', talk=True, gesture=False, look=(1, 0.3))


def boat_found(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('BFE6D8')), (0.5, h('5FA070')), (1, h('2E6B4A'))])
    Wd.ridge(cv, W, H, 950, 220, PAL['mid'], 71)
    Wd.hut(cv, 700, 1290, 520, h('C9A46A'), h('9A7A44'), h('6B4E2A'))
    Wd.fill(cv, 0, 1290, W, 1360, PAL['mud'])
    Wd.river(cv, W, 1360, H, PAL['river_d'], PAL['river'], t, flow=0.6, seed=11)
    Wd.canoe(cv, 420, 1470 + math.sin(t * 2) * 6, 320, h('6B4A2B'), h('4A321C'), ang=math.sin(t * 1.5) * 2)
    seg(cv, (180, 1460), (300, 1330), 4, h('C9B07A'), INK, 2)
    c.person(JULIANE, 920, 1380, 280, pose('stand', head=-6), facing=-1, expr='awed', look=(-1, 0))


def kesta_hut(cv, c):
    t, lt = c.t, c.lt
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('BFE6D8')), (1, h('2E6B4A'))])
    Wd.ridge(cv, W, H, 1000, 240, PAL['near'], 72)
    Wd.hut(cv, 820, 1400, 380, h('C9A46A'), h('9A7A44'), h('6B4E2A'))
    Wd.fill(cv, 0, 1400, W, H, PAL['mud'])
    kp = keyframes(lt, [(0, pose('gasp')), (0.4, pose('point'))])
    c.kesta(300, 1720, 620, kp, expr='excited' if lt > 0.4 else 'shocked', look=(1, -0.4))
    foreground_ferns(cv, t, y=1960, drift=500)


def fuel(cv, c):
    t, lt, k = c.t, c.lt, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('3A2A1C')), (1, h('1E140C'))])
    for i in range(7):  # plank walls with light gaps
        x = i * 160
        Wd.fill(cv, x, 0, x + 150, H, h('4A3420'))
        Wd.fill(cv, x + 150, 0, x + 160, H, Wd.alpha(PAL['shaft'], 0.35))
    tilt = min(1, k * 1.6)
    cv.save()
    cv.translate(720, 1080)
    cv.rotate(-70 * tilt)
    poly(cv, [(-110, -150), (110, -150), (110, 150), (-110, 150)], h('B03A2E'), INK, 5)
    poly(cv, [(40, -150), (90, -150), (90, -210), (40, -210)], h('8A8F99'), INK, 4)
    cv.restore()
    if tilt > 0.6:
        for i in range(10):
            yy = 1100 + ((t * 900 + i * 60) % 400)
            circle(cv, 560 + math.sin(i) * 10, yy, 9, Wd.alpha(h('E8D070'), 0.8), None)
    c.person(JULIANE, 380, 1900, 900, pose('stand', aFu=60, aFl=-20), facing=1, expr='wince' if k > 0.5 else 'determined', look=(1, -0.5))


def workers(cv, c):
    t, lt, k = c.t, c.lt, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('CFEFE4')), (1, h('3F8A4E'))])
    Wd.ridge(cv, W, H, 1000, 220, PAL['mid'], 81)
    Wd.hut(cv, 280, 1420, 420, h('C9A46A'), h('9A7A44'), h('6B4E2A'))
    Wd.fill(cv, 0, 1420, W, H, PAL['mud'])
    walk_in = min(1, lt / 0.7)
    p1 = walk(t, 0.9) if walk_in < 1 else pose('reach')
    c.person(WORKER1, lerp(1200, 780, walk_in), 1760, 520, p1, facing=-1, expr='shocked' if walk_in >= 1 else 'neutral')
    c.person(WORKER2, lerp(1400, 960, walk_in), 1780, 540, walk(t + 0.3, 0.9) if walk_in < 1 else pose('gasp'), facing=-1, expr='shocked')
    c.person(JULIANE, 420, 1740, 400, pose('sad', aFu=20, aFl=-30), facing=1, expr='relieved' if walk_in >= 1 else 'worried')


def boat_ride(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('FFD9A0')), (0.45, h('8FD3E8')), (1, h('5FA070'))])
    Wd.glow(cv, 820, 420, 120, h('FFE9A8'), 0.9)
    Wd.ridge(cv, W, H, 1050, 240, PAL['mid'], 91, x_off=t * 120)
    Wd.ridge(cv, W, H, 1150, 160, PAL['near'], 92, x_off=t * 220)
    Wd.river(cv, W, 1200, H, PAL['river_d'], PAL['river'], t, flow=2.2, seed=12)
    bx, by = 540, 1420 + math.sin(t * 3) * 8
    c.person(WORKER2, bx - 230, by + 10, 300, SIT, expr='happy')
    c.person(JULIANE, bx, by + 10, 300, SIT, expr='relieved')
    c.person(WORKER1, bx + 230, by + 10, 300, SIT, expr='happy', facing=-1)
    Wd.canoe(cv, bx, by + 30, 470, h('6B4A2B'), h('4A321C'))
    for i in range(6):
        oval(cv, bx - 520 - i * 60, by + 60, 60 - i * 6, 10, Wd.alpha(0xFFFFFFFF, 0.6 - i * 0.08), None)


def ninety_two(cv, c):
    t, lt, k = c.t, c.lt, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1020')), (1, h('1A2440'))])
    Wd.journal_page(cv, 90, 330, 900, 1100, lt, title='LANSA 508')
    fade = min(1, max(0, (lt - 0.4) / max(0.4, c.d - 0.9)))
    for i in range(92):
        x, y = 190 + (i % 10) * 78, 490 + (i // 10) * 88
        if i == 57:
            Wd.glow(cv, x, y, 40, h('FFB000'), 0.6 * fade)
            circle(cv, x, y, 22, h('FFB000'), INK, 3)
        else:
            circle(cv, x, y, 18, Wd.alpha(h('3A2A1C'), 1 - 0.85 * fade), None)
    c.kesta(860, 1880, 480, pose('sad', aFu=8), facing=-1, expr='sad', look=(-1, -0.6))


def station(cv, c):
    t, lt, k = c.t, c.lt, c.k
    jungle(cv, t, drift=0, ground_y=1450)
    # modern research station on stilts
    poly(cv, [(480, 1150), (1000, 1150), (1000, 1350), (480, 1350)], h('E6E2D6'), INK, 4)
    poly(cv, [(450, 1150), (740, 1020), (1030, 1150)], h('2F7A6B'), INK, 4)
    for i in range(4):
        poly(cv, [(520 + i * 115, 1200), (590 + i * 115, 1200), (590 + i * 115, 1270), (520 + i * 115, 1270)], h('9FD4F0'), INK, 3)
    for x in (500, 640, 840, 980):
        seg(cv, (x, 1350), (x, 1450), 12, h('6B4A2B'), INK, 3)
    Wd.text_card(cv, 'RESEARCH STATION', 740, 1110, 34, h('2F7A6B'), None, weight=800)
    p = walk(t, 0.9) if lt < 1.2 else keyframes(lt - 1.2, [(0, pose('stand')), (0.3, pose('wave_a')), (0.6, pose('wave_b')), (0.9, pose('wave_a'))])
    c.kesta(lerp(120, 330, min(1, lt / 1.2)), 1680, 600, p, expr='happy', look=(0.3, 0), speed=0.4 if lt < 1.2 else 0.0)
    foreground_ferns(cv, t, y=1960, drift=200)


def kesta_closeup(cv, c):
    t, lt = c.t, c.lt
    jungle(cv, t, drift=150, ground_y=1700, fog=True)
    Wd.fill(cv, 0, 0, W, H, Wd.alpha(h('0B1020'), 0.35))
    Wd.particles(cv, W, H, t, 40, Wd.alpha(PAL['shaft'], 0.8), 51, size=(3, 6), drift=(10, -30))
    kp = keyframes(lt, [(0, pose('stand', head=-4)), (0.5, pose('stand', head=4, nod=6))])
    c.kesta(470, 2330, 1700, kp, expr='happy', look=(-0.3, 0), wind=0.4)


def signoff(cv, c):
    t, lt, k = c.t, c.lt, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('0B1020')), (1, h('20305A'))])
    Wd.particles(cv, W, H, t, 60, Wd.alpha(0xFFFFFFFF, 0.6), 41, size=(1, 3), drift=(0, 0), twinkle=True)
    kp = keyframes(lt, [(0, pose('stand')), (0.2, pose('flare_aim')), (0.5, pose('flare_fire'))])
    c.kesta(540, 1700, 900, kp, expr='smirk', goggles='up', wind=0.5, prop_glow=max(0, min(1, (lt - 0.5) * 4)))
    if lt > 0.5:
        a = min(1, (lt - 0.5) * 5)
        Wd.text_card(cv, 'SURVRA', 540, 560, 150, Wd.alpha(h('FFB000'), a), Wd.alpha(0xFF000000, a))


SHOTS = {f.__name__: f for f in (
    freefall_hook, canopy_reveal, flare_fire, sky_kesta, plane_storm, strike, breakup, seatrow_fall, kesta_falling,
    canopy_rush, kesta_closeup, forest_wake, kesta_inspect, eye_close, father_memory, stream_map, kesta_stream, wade, swim, sweets,
    kesta_bank, night, boat_found, kesta_hut, fuel, workers, boat_ride, ninety_two, station, signoff)}
