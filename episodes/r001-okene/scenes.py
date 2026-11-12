"""Case 001 - Harrison Okene, Jascon-4, May 2013. World: Rook's office, a night storm off Nigeria, a capsizing tug,
a flooded upside-down cabin 30 m down, divers with lamps, a diving bell, sunrise. Drawn for this story only."""
import math

import skia

from concepts import v2
from concepts.chars import INK, P, fs, hose, oval, poly, smooth
from engine3 import host as Hm
from engine3 import world as Wd

W, H = 1080, 1920
h = Wd.hexc
lerp = lambda a, b, k: a + (b - a) * max(0.0, min(1.0, k))
SK, SK2 = h('7A4A2E'), h('5E3822')
CK = dict(pants=h('232936'), pants_sh=h('191D27'), boot=SK, boot_sh=SK2, top=h('D9D4C8'), top_sh=h('B5AFA0'), hand=SK, hand_sh=SK2)
DV = dict(pants=h('17191F'), pants_sh=h('0D0E12'), boot=h('F2B531'), boot_sh=h('C98F1E'), top=h('20242B'), top_sh=h('14161B'),
          hand=h('F2B531'), hand_sh=h('C98F1E'), cuff=h('F2B531'))
YEL = h('F2B531')


# ------------------------------------------------------------------ pieces
def deep(cv, t, top='0B2238', bot='02060D', snow=60):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h(top)), (1, h(bot))])
    Wd.particles(cv, W, H, t, snow, Wd.alpha(h('BFE6FF'), 0.35), 7, size=(1.5, 4), drift=(-18, -12), wobble=14)


def cone(cv, x, y, ang, L=950, spread=16, a=0.6, col='FFF2C0'):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    tn = math.tan(math.radians(spread))
    sh = skia.GradientShader.MakeRadial(skia.Point(0, 0), L, [Wd.alpha(h(col), a), Wd.alpha(h(col), 0)])
    cv.drawPath(poly([(0, -10), (L, -L * tn), (L, L * tn), (0, 10)]), skia.Paint(AntiAlias=True, Shader=sh))
    cv.restore()
    Wd.glow(cv, x, y, 26, h(col), 0.9)


def bubbles(cv, x, y, t, n=10, seed=1, spread=90, rise=300):
    R = Wd.Rand(seed)
    for i in range(n):
        ph, sx, r = R(0, 1), R(-spread, spread), R(6, 20)
        k = (t * R(0.5, 0.9) + ph) % 1
        cv.drawCircle(x + sx + math.sin(t * 3 + i) * 10, y - k * rise, r * (0.6 + 0.6 * k), P(Wd.alpha(0xFFFFFFFF, 0.75 * (1 - k)), 3))


def dark(cv, a):
    Wd.fill(cv, 0, 0, W, H, Wd.alpha(0xFF000000, a))


def water(cv, y, t, col='0E3A52', a=0.72):
    Wd.fill(cv, 0, y, W, H, Wd.alpha(h(col), a))
    pth = skia.Path()
    pth.moveTo(0, y)
    for i in range(1, 19):
        pth.lineTo(i * 60, y + math.sin(t * 3 + i * 0.9) * 7)
    cv.drawPath(pth, P(Wd.alpha(h('BFEFFF'), 0.8), 5))


def dv_head(expr='calm'):
    def head(cv, v):
        f = 3 if v in ('side', 'tq') else 0
        oval(cv, 0, -92, 12.5, 12.5, YEL, v2.OW)
        fs(cv, smooth([(-8 + f * 0.5, -97), (9 + f * 0.6, -97), (10 + f * 0.6, -89), (-8 + f * 0.5, -88)]), h('0B1220'), v2.OW)
        r = 2.4 if expr == 'shocked' else 1.5
        for s_ in (-1, 1):
            cv.drawCircle(1 + f + s_ * 3.6, -92.6, r, P(0xFFFFFFFF))
            cv.drawCircle(1 + f + s_ * 3.6, -92.6, 0.7, P(INK))
        fs(cv, poly([(-3, -107), (3, -107), (3, -103.4), (-3, -103.4)]), h('9AA0B4'), v2.OW)
        cv.drawCircle(0, -105.2, 1.3, P(h('FFF2C0')))
    return head


def okene(cv, x, y, hh, p='stand', view='tq', facing=1, expr='scared', rot=0.0):
    Hm.person(cv, x, y, hh, p, CK, Hm.human_head(SK, SK2, h('17131A'), expr), view, facing, rot)


def diver(cv, x, y, hh, t, expr='calm', ang=78, p=None):
    k = math.sin(t * 5)
    p = p or dict(hl=(4, -24), hr=(8, -30), fl=(k * 5, 0), fr=(-k * 5, 0), tilt=0, lift=0)
    Hm.person(cv, x, y, hh, p, DV, dv_head(expr), 'side', 1, ang)


def hand(cv, x, y, s, ang, col, col2, grip=0.0, sleeve=None):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    hose(cv, [(0, 300), (0, 50)], 76, sleeve or col, 5, straight=True)
    for i in range(4):
        bx = -42 + i * 28
        tip = (bx - 6 + i * 4 + grip * (30 - i * 6), -150 + grip * 95 + abs(i - 1.5) * 12)
        hose(cv, [(bx, -40), ((bx + tip[0]) / 2 - grip * 22, (-40 + tip[1]) / 2 - 10), tip], 25, col, 5)
    hose(cv, [(50, 20), (88 - grip * 30, -30 - grip * 20)], 27, col2, 5, straight=True)
    oval(cv, 0, 0, 62, 70, col, 5)
    cv.restore()


def tug(cv, x, y, s, ang=0.0, lit=True):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s, s)
    fs(cv, poly([(-300, 0), (310, 0), (330, -40), (300, -40), (255, 95), (-255, 95)]), h('8E2A2A'), 5)
    fs(cv, poly([(-300, 0), (310, 0), (330, -40), (-300, -40)]), h('1C1F28'), 5)
    fs(cv, poly([(-150, -40), (70, -40), (70, -170), (-150, -170)]), h('E8E4DA'), 5)
    fs(cv, poly([(-110, -170), (30, -170), (20, -250), (-100, -250)]), h('E8E4DA'), 5)
    for i in range(4):
        cv.drawRect(skia.Rect.MakeXYWH(-132 + i * 50, -130, 30, 34), P(h('FFD866') if lit else h('2A3340')))
    cv.drawRect(skia.Rect.MakeXYWH(-88, -232, 96, 30), P(h('FFD866') if lit else h('2A3340')))
    fs(cv, poly([(95, -40), (150, -40), (145, -150), (100, -150)]), h('FF7A1A'), 5)
    cv.drawLine(-40, -250, -40, -330, P(INK, 6))
    hose(cv, [(200, -40), (255, -70)], 16, h('5A6170'), 4, straight=True)
    cv.restore()


def night_sea(cv, t, y=1150, rough=1.0):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('070B1A')), (0.6, h('16243F')), (1, h('0A1426'))])
    for i in range(5):
        Wd.cloud(cv, (i * 290 + t * 40) % (W + 400) - 200, 240 + (i % 2) * 150, 190, h('1F2C4A'), h('141D33'))


def waves(cv, t, y=1250, rough=1.0):
    for i, c in enumerate(('14304E', '0F2440', '0A1A30')):
        Wd.ridge(cv, W, H, y + i * 120, 70 * rough, h(c), 20 + i, rough=5, x_off=t * (260 + i * 120))


def office(cv, t):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('15222B')), (1, h('0D161C'))])
    Wd.fill(cv, 610, 300, 1010, 860, h('24405A'))
    for i in range(9):
        Wd.fill(cv, 610, 310 + i * 62, 1010, 340 + i * 62, Wd.alpha(h('FFB000'), 0.55))
    cv.drawRect(skia.Rect.MakeLTRB(610, 300, 1010, 860), P(INK, 8))
    Wd.fill(cv, 0, 1560, W, H, h('0A1015'))
    fs(cv, poly([(40, 1290), (560, 1290), (560, 1560), (40, 1560)]), h('5A3E28'), 6)
    fs(cv, poly([(20, 1250), (580, 1250), (580, 1296), (20, 1296)]), h('7A5636'), 6)
    hose(cv, [(150, 1250), (150, 1130), (230, 1080)], 10, h('2F3640'), 4, straight=True)
    fs(cv, poly([(190, 1050), (300, 1070), (285, 1130), (205, 1110)]), h('FF7A1A'), 5)
    cone(cv, 250, 1110, 62, 380, 30, 0.5)
    for i in range(3):
        fs(cv, poly([(330 + i * 60, 1250), (378 + i * 60, 1250), (374 + i * 60, 1232 - i * 8), (334 + i * 60, 1232 - i * 8)]), h('C9B58A'), 4)


def cork(cv):
    Wd.fill(cv, 0, 0, W, H, h('9A6E44'))
    R = Wd.Rand(4)
    for i in range(160):
        cv.drawCircle(R(0, W), R(0, H), R(2, 6), P(Wd.alpha(h('6E4A2A'), 0.5)))
    cv.drawRect(skia.Rect.MakeLTRB(20, 20, W - 20, H - 20), P(h('4A2F1A'), 40))


def card(cv, x, y, w_, h_, ang, col=0xFFF4EEDF):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.drawRect(skia.Rect.MakeXYWH(-w_ / 2 + 10, -h_ / 2 + 14, w_, h_), P(0x55000000))
    fs(cv, poly([(-w_ / 2, -h_ / 2), (w_ / 2, -h_ / 2), (w_ / 2, h_ / 2), (-w_ / 2, h_ / 2)]), col, 5)
    cv.drawCircle(0, -h_ / 2 + 22, 14, P(h('E5392F')))
    cv.drawCircle(0, -h_ / 2 + 22, 14, P(INK, 4))
    cv.restore()


def cabin(cv, t, door=True):
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('123039')), (1, h('081A20'))])
    for x in range(0, W, 180):
        cv.drawLine(x, 0, x, H, P(Wd.alpha(0xFF000000, 0.25), 6))
    if door:
        fs(cv, poly([(700, 420), (980, 420), (980, 1120), (700, 1120)]), h('2A5560'), 6)
        cv.drawCircle(740, 520, 18, P(h('B9C2CC')))
        fs(cv, poly([(780, 980), (900, 980), (900, 1060), (780, 1060)]), h('E8E4DA'), 4)
    for y in (260, 330):
        cv.drawLine(0, y, W, y, P(h('3A6A74'), 26))
        cv.drawLine(0, y, W, y, P(INK, 3))


def rook_bowl(cv, c, x, y, hh, pose_, expr, facing=1, view='tq'):
    c.host(x, y, hh, pose_, view, facing, expr)
    Hm.bowl(cv, x, y + (pose_.get('lift', 0) if isinstance(pose_, dict) else 0) * hh / 110, hh, facing)
    bubbles(cv, x + facing * 20, y - hh * 1.05, c.t, 5, 9, 30, 220)


# ------------------------------------------------------------------ shots
def dive_search(cv, c):
    t = c.t
    deep(cv, t, '14506E', '04101C', 90)
    Wd.fill(cv, 0, 0, W, 520, h('071624'))
    Wd.fill(cv, 0, 1420, W, H, h('06111C'))
    for i in range(5):
        x = (i * 330 - t * 900) % 1500 - 200
        cv.drawRect(skia.Rect.MakeLTRB(x, 520, x + 46, 1420), P(h('123048')))
    dx = lerp(-260, 300, c.k)
    cone(cv, dx + 690, 960, -8 + math.sin(t * 7) * 12, 1000, 17, 0.8)
    for i, (bx, by) in enumerate(((820, 760), (930, 1180), (640, 1300), (1200, 900))):
        bx = (bx - t * 700) % 1400 - 150
        cv.save()
        cv.rotate(t * 120 + i * 40, bx + 30, by + 25)
        fs(cv, poly([(bx, by), (bx + 60, by + 10), (bx + 50, by + 50), (bx - 6, by + 40)]), h('3A5066'), 4)
        cv.restore()
    diver(cv, dx, 1110, 720, t)
    bubbles(cv, dx + 600, 880, t * 2, 14, 1, 120, 420)


def hand_float(cv, c):
    t = c.t
    deep(cv, t, '06182A')
    Wd.fill(cv, 560, 380, 1080, 1560, h('01040A'))
    cv.drawRect(skia.Rect.MakeLTRB(560, 380, 1080, 1560), P(h('16324A'), 26))
    cone(cv, 0, 1500, -32 + math.sin(t * 1.5) * 2, 1300, 13, 0.55)
    hand(cv, lerp(900, 760, c.k), 960 + math.sin(t * 2) * 14, 1.5, -80 + math.sin(t * 1.3) * 6, SK, SK2, 0.15)
    Wd.fill(cv, 900, 380, 1080, 1560, Wd.alpha(h('01040A'), 0.85))


def hand_grab(cv, c):
    t, k = c.t, c.k
    deep(cv, t, '0A2A44')
    Wd.glow(cv, 540, 960, 520, h('FFF2C0'), 0.25)
    hose(cv, [(-40, 1090), (620, 990)], 170, h('20242B'), 7, straight=True)
    hose(cv, [(560, 1000), (700, 978)], 180, YEL, 7, straight=True)
    oval(cv, 840, 950, 150, 130, YEL, 7)
    hand(cv, 420, lerp(700, 1010, min(1, k * 4)), 2.0, 172, SK, SK2, 1.0)
    for i in range(10):
        a = i * 0.628
        cv.drawLine(430 + math.cos(a) * 300, 1010 + math.sin(a) * 300, 430 + math.cos(a) * (380 + 60 * math.sin(t * 20)), 1010 + math.sin(a) * 380, P(0xFFFFFFFF, 8))
    bubbles(cv, 430, 900, t, 12, 3, 260, 500)


def diver_shock(cv, c):
    t = c.t
    m = -1 if c.prm.get('flip') else 1
    deep(cv, t, '0A2A44')
    cv.save()
    cv.translate(540, 960)
    cv.scale(m, 1)
    cv.rotate(math.sin(t * 30) * 2.5)
    oval(cv, 0, 0, 400, 400, YEL, 9)
    fs(cv, smooth([(-270, -170), (290, -170), (320, 110), (-270, 140)]), h('0B1220'), 9)
    for s_ in (-1, 1):
        cv.drawCircle(20 + s_ * 125, -20, 92, P(0xFFFFFFFF))
        cv.drawCircle(20 + s_ * 125 + math.sin(t * 25) * 6, -20, 22, P(INK))
    fs(cv, poly([(-90, -470), (90, -470), (90, -380), (-90, -380)]), h('9AA0B4'), 8)
    cv.restore()
    Wd.glow(cv, 540, 540, 90, h('FFF2C0'), 0.9)
    bubbles(cv, 540, 1300, t, 22, 5, 420, 1100)


def rook_office(cv, c):
    office(cv, c.t)
    c.host(700, 1640, 900, 'cross', 'tq', -1, 'deadpan')


def board_ship(cv, c):
    cork(cv)
    k = min(1, c.lt / 0.25)
    card(cv, 520, 820, 760 * (0.7 + 0.3 * k), 620 * (0.7 + 0.3 * k), -3)
    cv.save()
    cv.translate(520, 820)
    cv.rotate(-3)
    Wd.fill(cv, -340, -220, 340, 250, h('BFE0EC'))
    Wd.fill(cv, -340, 170, 340, 250, h('C9B58A'))
    tug(cv, 0, 150, 0.55, 180, lit=False)
    for i in range(3):
        cv.drawLine(-300 + i * 220, -150 + i * 30, -180 + i * 220, -150 + i * 30, P(0xFFFFFFFF, 6))
    cv.restore()
    card(cv, 800, 1300, 330, 250, 6, h('FFD866'))
    Wd.text_card(cv, '3 DAYS', 800, 1330, 78, INK, None)
    cv.drawLine(520, 540, 800, 1200, P(h('E5392F'), 7))
    hand(cv, lerp(1200, 330, min(1, c.lt / 0.3)), 1560 + math.sin(c.t * 9) * 12, 1.25, -42, h('2A2742'), h('1C1A2E'), 0.2, h('566178'))


def rook_cu(cv, c):
    t = c.t
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1B2A33')), (1, h('0D161C'))])
    for i in range(10):
        cv.drawLine(-100, 200 + i * 150, W + 100, 60 + i * 150, P(Wd.alpha(h('FFB000'), 0.16), 46))
    c.host(470, 3180, 2600, 'stand', 'tq', 1, c.prm.get('expr', 'smirk'))


def door_go(cv, c):
    office(cv, c.t)
    fs(cv, poly([(760, 600), (1010, 600), (1010, 1560), (760, 1560)]), h('FFE9A8'), 8)
    cv.drawPath(poly([(760, 1560), (1010, 1560), (880, 1900), (300, 1900)]), P(Wd.alpha(h('FFE9A8'), 0.25)))
    Wd.glow(cv, 885, 1080, 300, h('FFE9A8'), 0.35)
    c.host(lerp(260, 720, c.k), 1660, 860, Hm.walk(c.t, 1.9), 'side', 1, 'happy')


def tug_storm(cv, c):
    t = c.t
    night_sea(cv, t)
    fs(cv, poly([(900, 1090), (1040, 1090), (1020, 820), (920, 820)]), h('1A2238'), 0)
    Wd.glow(cv, 970, 800, 30, h('FF7A1A'), 0.9)
    Wd.ridge(cv, W, H, 1180, 60, h('1A3A5C'), 19, rough=5, x_off=t * 200)
    tug(cv, 500, 1170 + math.sin(t * 2.4) * 22, 1.0, math.sin(t * 1.9) * 7)
    waves(cv, t, 1290)
    Wd.rain(cv, W, H, t, 130, Wd.alpha(h('B9C8FF'), 0.4))


def rook_buoy(cv, c):
    t = c.t
    night_sea(cv, t)
    tug(cv, 800, 1130 + math.sin(t * 2.4) * 12, 0.42, math.sin(t * 1.9) * 9)
    Wd.ridge(cv, W, H, 1190, 60, h('1A3A5C'), 19, rough=5, x_off=t * 200)
    by = 1330 + math.sin(t * 2.2) * 26
    cv.save()
    cv.translate(330, by)
    cv.rotate(math.sin(t * 2.2 + 1) * 7)
    c.host(0, -40, 640, 'point', 'tq', 1, 'curious')
    fs(cv, poly([(-110, -40), (110, -40), (150, 150), (-150, 150)]), h('E5392F'), 6)
    fs(cv, poly([(-125, 40), (125, 40), (137, 90), (-137, 90)]), 0xFFFFFFFF, 5)
    cv.restore()
    waves(cv, t, 1420)
    Wd.rain(cv, W, H, t, 130, Wd.alpha(h('B9C8FF'), 0.4))


def big_wave(cv, c):
    t, k = c.t, c.k
    night_sea(cv, t)
    wy = lerp(1300, 520, k)
    fs(cv, smooth([(1200, 2000), (1250, wy), (900, wy - 120), (640, wy + 60), (520, wy + 420), (380, 1500), (300, 2000)]), h('1F4A70'), 8)
    cv.drawPath(smooth([(1230, wy + 10), (900, wy - 100), (650, wy + 70), (560, wy + 330)], False), P(0xFFE8F6FF, 26))
    tug(cv, 360, 1230 - k * 60, 0.8, -14 - k * 16)
    waves(cv, t, 1340, 1.6)
    Wd.rain(cv, W, H, t, 150, Wd.alpha(h('B9C8FF'), 0.45), slant=0.5)


def capsize(cv, c):
    t, k = c.t, c.k
    night_sea(cv, t)
    Wd.ridge(cv, W, H, 1150, 90, h('1A3A5C'), 19, rough=5, x_off=t * 300)
    tug(cv, 540, 1180 + k * 60, 1.05, lerp(-35, -172, k))
    waves(cv, t, 1260, 1.8)
    R = Wd.Rand(2)
    for i in range(26):
        a, sp = R(3.4, 6.0), R(300, 900)
        cv.drawCircle(540 + math.cos(a) * sp * k, 1200 + math.sin(a) * sp * k + 500 * k * k, R(8, 22), P(Wd.alpha(0xFFFFFFFF, 0.8)))
    Wd.rain(cv, W, H, t, 150, Wd.alpha(h('B9C8FF'), 0.45), slant=0.5)


def _bathroom(cv, c, expr, pz):
    Wd.fill(cv, -400, -400, W + 400, H + 400, h('BFE3E0'))
    for x in range(-360, W + 400, 120):
        cv.drawLine(x, -400, x, H + 400, P(h('9CCFCB'), 5))
    for y in range(-360, H + 400, 120):
        cv.drawLine(-400, y, W + 400, y, P(h('9CCFCB'), 5))
    Wd.fill(cv, -400, 1500, W + 400, H + 400, h('5F8F96'))
    fs(cv, poly([(640, 620), (940, 620), (940, 1000), (640, 1000)]), h('DFF3F7'), 7)
    fs(cv, smooth([(620, 1120), (960, 1120), (930, 1250), (650, 1250)]), 0xFFFFFFFF, 7)
    hose(cv, [(790, 1250), (790, 1500)], 60, 0xFFFFFFFF, 6, straight=True)
    okene(cv, 400, 1620, 900, pz, 'tq', 1, expr)


def bathroom(cv, c):
    k = c.k
    cv.save()
    cv.rotate(lerp(0, 16, max(0, k * 2 - 1)), 540, 960)
    _bathroom(cv, c, 'happy' if k < 0.5 else 'shocked', Hm.pose('stand') if k < 0.5 else Hm.pose('shrug', tilt=-10))
    cv.restore()


def flip(cv, c):
    t, k = c.t, c.k
    cv.save()
    cv.rotate(lerp(16, 180, k), 540, 960)
    _bathroom(cv, c, 'scared', Hm.pose('hype', tilt=k * 60))
    cv.restore()
    Wd.fill(cv, 0, lerp(H, 500, k), W, H, Wd.alpha(h('0E3A52'), 0.8))
    bubbles(cv, 540, 1500, t, 20, 8, 480, 900)
    dark(cv, 0.55 * k)


def sinking(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('1E5A80')), (0.5, h('0A2238')), (1, h('01050B'))])
    Wd.ridge(cv, W, H, 1760, 90, h('0A1420'), 33, rough=5)
    ty = lerp(360, 1450, k)
    bubbles(cv, 600, ty - 80, t, 26, 4, 260, 700)
    tug(cv, 600, ty, 0.95, 180 + math.sin(t * 2) * 5, lit=False)
    rook_bowl(cv, c, 240, ty + 330, 420, Hm.pose('point', hr=(24, -20)), 'shocked')
    for i, m in enumerate((10, 20, 30)):
        y = 500 + i * 430
        cv.drawLine(40, y, 150, y, P(0xFFFFFFFF, 6))
        Wd.text_card(cv, f'{m} m', 250, y + 22, 60, 0xFFFFFFFF if ty < y - 60 else h('FFB000'), 0xFF000000)


def blackout(cv, c):
    t, k = c.t, c.k
    Wd.fill(cv, 0, 0, W, H, 0xFF000000)

    def eyes(x, y, col, s, lookx, blink):
        for s_ in (-1, 1):
            if blink:
                cv.drawLine(x + s_ * 70 * s - 40 * s, y, x + s_ * 70 * s + 40 * s, y, P(col, 8))
            else:
                oval(cv, x + s_ * 70 * s, y, 44 * s, 34 * s, col, 0)
                cv.drawCircle(x + s_ * 70 * s + lookx * 16 * s, y, 13 * s, P(0xFF000000))
    Wd.particles(cv, W, H, t * 3, 50, Wd.alpha(h('BFE6FF'), 0.3), 7, size=(2, 5), drift=(-40, -30), wobble=20)
    eyes(380 + math.sin(t * 9) * 30, 980 + math.cos(t * 7) * 16, 0xFFFFFFFF, 1.0, math.sin(t * 8), (t * 1.7) % 1 < 0.08)
    if k > 0.5:
        eyes(740, 900, h('FFB000'), 0.8, -1, False)
        cv.drawLine(620, 846, 860, 846, P(h('34303B'), 14))


def pocket_wide(cv, c):
    t = c.t
    deep(cv, t, '0A2A44', '030A12', 40)
    Wd.ridge(cv, W, H, 1500, 80, h('1A2430'), 41, rough=5)
    fs(cv, poly([(120, 1470), (960, 1470), (1010, 1400), (860, 760), (220, 760), (90, 1400)]), h('7A2424'), 8)
    fs(cv, poly([(330, 880), (760, 880), (760, 1300), (330, 1300)]), h('1E4650'), 6)
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(333, 883, 757, 1297))
    Wd.glow(cv, 545, 960, 150, h('FFF2C0'), 0.35)
    okene(cv, 545, 1420, 520, 'cross', 'front', 1, 'scared')
    water(cv, 1080, t, '0E3A52', 0.78)
    cv.restore()
    Wd.text_card(cv, 'AIR', 545, 850, 64, h('FFB000'), 0xFF000000)
    rook_bowl(cv, c, 170, 1620 + math.sin(t * 2) * 10, 430, Hm.pose('point', hr=(26, -16)), 'curious')


def chest_water(cv, c):
    t, k = c.t, c.k
    cabin(cv, t)
    fl = 0.5 + 0.5 * math.sin(t * 23) * math.sin(t * 7)
    Wd.glow(cv, 540, 900, 380, h('FFF2C0'), 0.3 * fl * (1 - k * 0.6))
    okene(cv, 600 + math.sin(t * 40) * 7, 1700, 1050, 'cross', 'tq', 1, 'scared')
    for i in range(3):
        oval(cv, 800 + i * 46 + (t * 160) % 120, 760 - i * 22, 30 + i * 12, 20 + i * 8, Wd.alpha(0xFFFFFFFF, 0.3 - i * 0.07), 0)
    ry = lerp(2100, 1560, min(1, k * 2.2))
    rook_bowl(cv, c, 230, ry, 700, 'stand', 'scared')
    water(cv, 1090 + math.sin(t * 5) * 14, t * 2.5)
    bubbles(cv, 230, 1080, t, 8, 4, 70, 260)
    dark(cv, 0.2 + 0.25 * k)


def coke(cv, c):
    t = c.t
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('123039')), (1, h('050F13'))])
    Wd.glow(cv, 540, 900, 420, h('FFF2C0'), 0.22)
    hand(cv, 520, 1420, 2.1, 6, SK, SK2, 0.75)
    cv.save()
    cv.translate(540, 1000)
    cv.rotate(-8 + math.sin(t * 2) * 2)
    fs(cv, smooth([(-70, 330), (-80, 60), (-70, -90), (-34, -210), (-30, -330), (30, -330), (34, -210), (70, -90), (80, 60), (70, 330)]), h('3A1E14'), 7)
    fs(cv, poly([(-80, 0), (80, 0), (80, 130), (-80, 130)]), h('E5392F'), 6)
    fs(cv, poly([(-36, -372), (36, -372), (36, -326), (-36, -326)]), h('B9C2CC'), 6)
    cv.drawLine(-48, -180, -56, 280, P(Wd.alpha(0xFFFFFFFF, 0.5), 12))
    cv.restore()
    hand(cv, 520, 1420, 2.1, 6, SK, SK2, 1.0)
    Wd.text_card(cv, 'x1', 860, 520, 190, h('FFB000'), 0xFF000000)


def rook_shrug(cv, c):
    t = c.t
    deep(cv, t, '0A2A44')
    fs(cv, poly([(820, 0), (1080, 0), (1080, H), (760, H)]), h('7A2424'), 8)
    oval(cv, 930, 800, 90, 90, h('1E4650'), 8)
    Wd.glow(cv, 930, 800, 60, h('FFF2C0'), 0.35)
    rook_bowl(cv, c, 420, 1640 + math.sin(t * 2) * 14, 1000, 'shrug', 'deadpan')


def day_stamp(cv, c):
    t, k = c.t, c.k
    cabin(cv, t, door=False)
    my = 1130 + math.sin(t * 2) * 8
    okene(cv, 540, my - 10, 760, dict(hl=(10, 22), hr=(-10, 22), fl=(14, -34), fr=(18, -34), tilt=8, lift=30), 'tq', 1, 'sad')
    fs(cv, smooth([(180, my), (900, my), (920, my + 90), (160, my + 90)]), h('8FA3B8'), 7)
    water(cv, my + 60, t)
    dark(cv, 0.35)
    n = 1 if k < 0.5 else 2
    a = (k if k < 0.5 else k - 0.5) * 2
    cv.save()
    cv.translate(540, 520)
    cv.rotate(-6)
    cv.scale(1 + 0.6 * max(0, 1 - a * 6), 1 + 0.6 * max(0, 1 - a * 6))
    Wd.text_card(cv, f'DAY {n}', 0, 0, 220, h('FFB000'), 0xFF000000)
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


def rook_feathers(cv, c):
    t, k = c.t, c.k
    deep(cv, t, '0A2A44')
    rook_bowl(cv, c, 520 + math.sin(t * 34) * 5, 1700, 1150, Hm.pose('cross', tilt=-4), 'scared')
    R = Wd.Rand(6)
    for i in range(9):
        fx, ph = R(-260, 260), R(0, 1)
        kk = (k * 1.3 + ph) % 1
        Wd.leaf(cv, 520 + fx + math.sin(t * 3 + i) * 40, 1250 - kk * 900, 80, 60 + t * 90 + i * 40, h('2A2742'), h('6E69A0'), INK, 4)


def light_beam(cv, c):
    t, k = c.t, c.k
    cabin(cv, t, door=False)
    okene(cv, 720, 1700, 1000, Hm.pose('stand', hr=(-4, 6)), 'tq', -1, 'awe')
    water(cv, 1120, t)
    dark(cv, 0.38)
    cone(cv, -40, 1700, lerp(-70, -28, k), 1700, 12, 0.75)
    Wd.glow(cv, 60, 1640, 120, h('FFF2C0'), 0.5)


def bang_wall(cv, c):
    t = c.t
    cabin(cv, t, door=False)
    fs(cv, poly([(860, 0), (1080, 0), (1080, H), (860, H)]), h('3A4A55'), 8)
    for y in range(120, H, 200):
        cv.drawCircle(905, y, 14, P(h('1E2A33')))
    ph = (t * 3.2) % 1
    sw = max(0, 1 - ph * 3)
    p = dict(hl=(-4, 26), hr=(lerp(8, 26, sw), lerp(-26, -10, sw)), fl=(-6, 0), fr=(8, 0), tilt=4, lift=0)
    okene(cv, 560, 1700, 1000, p, 'side', 1, 'angry')
    hx, hy = 560 + (13.5 * 0.62 + p['hr'][0]) * 1000 / 110 + 30, 1700 + (-77 + p['hr'][1]) * 1000 / 110
    hose(cv, [(hx - 20, hy + 30), (hx + 70, hy - 70)], 18, h('8A5A3A'), 5, straight=True)
    fs(cv, poly([(hx + 40, hy - 110), (hx + 120, hy - 60), (hx + 100, hy - 30), (hx + 20, hy - 80)]), h('9AA0B4'), 5)
    if ph < 0.35:
        for r in (60, 130, 200):
            cv.drawCircle(880, hy - 60, r * (0.5 + ph * 2), P(Wd.alpha(0xFFFFFFFF, 0.8 - ph * 2), 9))
    water(cv, 1150, t)
    dark(cv, 0.3)


def light_leaves(cv, c):
    t, k = c.t, c.k
    Wd.fill(cv, 0, 0, W, H, h('02070D'))
    for i in range(6):
        s = 1 - i * 0.15
        cv.drawRect(skia.Rect.MakeLTRB(540 - 480 * s, 900 - 760 * s, 540 + 480 * s, 900 + 760 * s), P(Wd.alpha(h('16324A'), 0.9 - i * 0.12), 14))
    Wd.glow(cv, lerp(560, 520, k), lerp(940, 880, k), lerp(230, 26, k), h('FFF2C0'), lerp(0.95, 0.5, k))
    hand(cv, 760, 1560, 2.0, -22, SK, SK2, 0.05)
    dark(cv, 0.25 * k)


def light_back(cv, c):
    t, k = c.t, c.k
    deep(cv, t, '0A2A44')
    Wd.fill(cv, 0, 0, W, 470, h('123039'))
    okene(cv, 800, 900, 960, Hm.pose('stand', hr=(8, 30)), 'tq', -1, 'awe')
    Wd.fill(cv, 0, 470, W, H, Wd.alpha(h('0A2A44'), 0.55))
    water(cv, 470, t, '0A2A44', 0.0)
    dx = lerp(-380, 60, k)
    cone(cv, dx + 520, 1335, -30, 1100, 14, 0.7)
    diver(cv, dx, 1500, 600, t, ang=62)
    bubbles(cv, dx + 420, 1250, t, 10)


def reach(cv, c):
    t, k = c.t, c.k
    deep(cv, t, '0E3A52')
    Wd.fill(cv, 0, 0, W, 900, h('123039'))
    Wd.glow(cv, 540, 1500, 500, h('FFF2C0'), 0.3)
    hand(cv, 600, lerp(1900, 1360, k), 1.9, 8, YEL, h('C98F1E'), 0.1, h('20242B'))
    hand(cv, 480, lerp(300, 800, k), 1.9, 188, SK, SK2, 0.1)
    water(cv, 900, t, '0E3A52', 0.35)


def the_grab(cv, c):
    t, k = c.t, c.k
    deep(cv, t, '0E3A52')
    Wd.glow(cv, 540, 980, 620, h('FFF2C0'), 0.35)
    hand(cv, 590, 1330, 2.3, 8, YEL, h('C98F1E'), 0.2, h('20242B'))
    hand(cv, 520, 930, 2.3, 188, SK, SK2, lerp(0.2, 1.0, k * 3))
    for i in range(12):
        a = i * 0.5236
        r0 = 420 + 40 * math.sin(t * 22 + i)
        cv.drawLine(550 + math.cos(a) * r0, 1080 + math.sin(a) * r0, 550 + math.cos(a) * (r0 + 130), 1080 + math.sin(a) * (r0 + 130), P(0xFFFFFFFF, 10))
    bubbles(cv, 540, 1300, t, 18, 6, 400, 900)


def rook_fair(cv, c):
    t = c.t
    deep(cv, t, '0E3A52')
    diver(cv, 860, 1150 - c.k * 600, 480, t, 'shocked', ang=-20, p=Hm.pose('hype'))
    bubbles(cv, 900, 800 - c.k * 500, t, 16, 2, 160, 600)
    rook_bowl(cv, c, 360, 1700 + math.sin(t * 2) * 12, 980, 'shrug', 'laugh' if c.k < 0.6 else 'smirk')


def bell_up(cv, c):
    t, k = c.t, c.k
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('7FD3E8')), (0.35, h('1E6A90')), (1, h('05182A'))])
    for i in range(5):
        cv.drawPath(poly([(160 + i * 190, 0), (260 + i * 190, 0), (160 + i * 230, 1500), (40 + i * 230, 1500)]), P(Wd.alpha(0xFFFFFFFF, 0.08)))
    by = lerp(1500, 620, k)
    cv.drawLine(540, 0, 540, by - 230, P(INK, 12))
    fs(cv, smooth([(-170 + 540, by + 200), (-190 + 540, by - 60), (540, by - 240), (190 + 540, by - 60), (170 + 540, by + 200)]), YEL, 8)
    oval(cv, 540, by - 20, 80, 80, h('BFEFFF'), 8)
    Hm.person(cv, 540, by + 250, 300, 'stand', CK, Hm.human_head(SK, SK2, h('17131A'), 'happy'), 'front', 1)
    cv.drawCircle(540, by - 20, 80, P(Wd.alpha(h('BFEFFF'), 0.25)))
    cv.drawCircle(540, by - 20, 80, P(INK, 8))
    bubbles(cv, 540, by + 220, t, 16, 3, 180, 500)
    rook_bowl(cv, c, 800, by + 330, 420, Hm.pose('hype', hl=(-22, -30), hr=(-12, -34)), 'happy', -1)


def sunrise(cv, c):
    t = c.t
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('2B4A7A')), (0.45, h('FF9A52')), (0.62, h('FFD9A0'))])
    Wd.glow(cv, 540, 1120, 240, h('FFF2C0'), 0.95)
    Wd.ridge(cv, W, H, 1210, 26, h('1E5A80'), 51, rough=4, x_off=t * 60)
    Wd.fill(cv, 0, 1500, W, H, h('5A6170'))
    cv.drawLine(0, 1500, W, 1500, P(INK, 8))
    for x in range(40, W, 200):
        hose(cv, [(x, 1500), (x, 1330)], 12, h('B9C2CC'), 4, straight=True)
    cv.drawLine(0, 1335, W, 1335, P(h('B9C2CC'), 12))
    okene(cv, 400, 1760, 820, Hm.pose('cross'), 'tq', 1, 'happy')
    fs(cv, smooth([(250, 1300), (400, 1210), (560, 1300), (600, 1560), (210, 1560)]), h('FF7A1A'), 7)
    okene_head = Hm.human_head(SK, SK2, h('17131A'), 'happy')
    cv.save()
    cv.translate(400, 1760)
    cv.scale(820 / 110, 820 / 110)
    okene_head(cv, 'tq')
    cv.restore()
    c.host(800, 1760, 800, Hm.pose('stand', hr=(-9, -19)), 'tq', -1, 'happy')


def board_true(cv, c):
    cork(cv)
    card(cv, 540, 860, 700, 820, 2)
    cv.save()
    cv.translate(540, 1560)
    cv.scale(5.4, 5.4)
    cv.clipRect(skia.Rect.MakeLTRB(-60, -206, 60, -60))
    Wd.fill(cv, -60, -206, 60, -60, h('BFE0EC'))
    Hm.person(cv, 0, 0, 110, 'stand', CK, Hm.human_head(SK, SK2, h('17131A'), 'happy'), 'front', 1)
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
    card(cv, 300, 1540, 300, 200, -5, h('FFD866'))
    Wd.text_card(cv, '60 HOURS', 300, 1565, 54, INK, None)


def signoff(cv, c):
    t, lt = c.t, c.lt
    Wd.vgrad(cv, 0, 0, W, H, [(0, h('15222B')), (1, h('070C10'))])
    for i in range(10):
        cv.drawLine(-100, 300 + i * 150, W + 100, 160 + i * 150, P(Wd.alpha(h('FFB000'), 0.10), 46))
    p = Hm.keys(lt, [(0, Hm.pose('stand')), (0.35, Hm.pose('stand', hr=(-9, -21), tilt=-2))])
    c.host(540, 1760, 1050, p, 'tq', 1, 'smirk')
    ck = min(1, lt / 0.9)
    cv.drawCircle(lerp(760, 880, ck), 1250 - math.sin(ck * math.pi) * 420, 26, P(h('FFD866')))
    cv.drawCircle(lerp(760, 880, ck), 1250 - math.sin(ck * math.pi) * 420, 26, P(INK, 5))
    if lt > 0.5:
        Wd.text_card(cv, 'SURVRA', 540, 430, 150, h('FFB000'), 0xFF000000)
        Wd.text_card(cv, 'CASE 001  CLOSED', 540, 520, 54, 0xFFFFFFFF, 0xFF000000)


SHOTS = {f.__name__: f for f in (
    dive_search, hand_float, hand_grab, diver_shock, rook_office, board_ship, rook_cu, door_go, tug_storm, rook_buoy, big_wave,
    capsize, bathroom, flip, sinking, blackout, pocket_wide, chest_water, coke, rook_shrug, day_stamp, air_gauge, rook_feathers,
    light_beam, bang_wall, light_leaves, light_back, reach, the_grab, rook_fair, bell_up, sunrise, board_true, signoff)}
