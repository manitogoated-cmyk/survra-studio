"""Shot library. Each shot draws a full 1080x1920 frame in world space; the renderer applies the camera.
f(cv, t, d, prm): t = seconds into the shot, d = shot length, prm = storyboard params."""
import math, random
import skia
from common import W, H, C, P, lerp, clamp, ease, ease_out, BRAND, TF_BLACK, TF_BOLD
import rig
import render_short as R

J, E = rig.JOSE, rig.EZEQ

def grad(cv, top, bot, y0=0, y1=H):
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, y0), (0, y1)], [C(top), C(bot)])))

def vignette(cv, a=0.55):
    sh = skia.GradientShader.MakeRadial((W / 2, H / 2), H * 0.62, [C('#000000', 0), C('#000000', int(255 * a))], [0.55, 1.0])
    cv.drawRect(skia.Rect(-W, -H, 2 * W, 2 * H), skia.Paint(Shader=sh))

def particles(cv, t, n, seed, col, rmin, rmax, vy, vx=0.0, alpha=0.8, area=(0, 0, W, H)):
    r = random.Random(seed); x0, y0, x1, y1 = area
    for i in range(n):
        x = r.uniform(x0, x1); y = r.uniform(y0, y1); rr = r.uniform(rmin, rmax); sp = r.uniform(0.6, 1.4)
        yy = y0 + ((y - y0 + vy * sp * t) % (y1 - y0)); xx = x + vx * sp * t
        cv.drawCircle(xx, yy, rr, P(C(col), alpha=alpha))

def splash(cv, x, y, t, scale=1.0, seed=1):
    """Burst of droplets from (x, y); t in seconds since impact."""
    if t < 0 or t > 0.9: return
    r = random.Random(seed)
    for i in range(26):
        a = r.uniform(-math.pi * 0.95, -math.pi * 0.05); v = r.uniform(400, 1100) * scale
        px = x + math.cos(a) * v * t; py = y + math.sin(a) * v * t + 1800 * t * t
        cv.drawCircle(px, py, r.uniform(5, 13) * scale * (1 - t), P(C('#e8f6ff'), alpha=0.9 * (1 - t / 0.9)))

def smoke(cv, x, y, t, col='#2b2f36', n=8, rise=260, spread=60, size=40):
    for i in range(n):
        k = (t * 1.6 + i / n) % 1
        cv.drawCircle(x + math.sin(i * 2.1 + t) * spread * k, y - rise * k, size * (0.5 + k), P(C(col), blur=10, alpha=0.6 * (1 - k)))

def sparks(cv, x, y, t, seed=4):
    r = random.Random(int(t * 12) + seed)
    for i in range(10):
        a = r.uniform(0, 2 * math.pi); L = r.uniform(20, 90)
        cv.drawLine(x, y, x + math.cos(a) * L, y + math.sin(a) * L, P(C('#ffd34d'), 'stroke', 5, alpha=r.uniform(0.4, 1)))

def boat_with_crew(cv, x, y, ang, t, s=1.0, jose=('sit', 'neutral'), ez=('sit', 'neutral'), ez_alpha=1.0, engine_ok=True, wet=False):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    if ez is not None and ez_alpha > 0:
        p = ez[0] if isinstance(ez[0], dict) else rig.pose(ez[0])
        rig.draw_person(cv, 70, -40, 0.9, p, E, ez[1], t + 1.3, face=-1, alpha=ez_alpha, wet=wet)
    if jose is not None:
        p = jose[0] if isinstance(jose[0], dict) else rig.pose(jose[0])
        rig.draw_person(cv, -150, -40, 0.9, p, J, jose[1], t, face=1, wet=wet)
    cv.restore()
    R.boat(cv, x, y, ang, s, engine_ok=engine_ok)

def deck(cv, y=H * 0.80):
    cv.drawRect(skia.Rect(0, y, W, H), P(C('#c9a26b')))
    for i in range(1, 6): cv.drawLine(0, y + i * 70, W, y + i * 70, P(C('#8a6a40'), 'stroke', 5))
    cv.drawRect(skia.Rect(0, y - 26, W, y + 8), P(C('#f2f2ee'))); cv.drawRect(skia.Rect(0, y - 8, W, y + 8), P(C('#1f6fb2')))
    cv.drawLine(0, y - 26, W, y - 26, P(C('#0b1320'), 'stroke', 6))

def sea_scene(cv, t, sky='day', amp=20, horizon=H * 0.5):
    R.sky(cv, sky, t); R.ocean(cv, sky, t, amp=amp, horizon=horizon)

# ---------------- HOOK ----------------
def eyes_open(cv, t, d, prm):
    grad(cv, '#ffcf8a', '#c4683a')
    particles(cv, t, 30, 3, '#fff3d6', 2, 6, -40, alpha=0.5)
    ex = 'closed' if t < 0.18 else 'shock'
    rig.draw_face_closeup(cv, W / 2, H * 0.5, 1.05, J, ex, t, look=(0.15, -0.35), wet=True)
    vignette(cv, 0.6)

def overhead_ocean(cv, t, d, prm):
    grad(cv, '#0a3d6e', '#0f5a96')
    r = random.Random(2)
    for i in range(70):
        x = r.uniform(-100, W + 100); y = r.uniform(0, H); L = r.uniform(60, 180)
        yy = (y + t * 40) % H
        cv.drawLine(x, yy, x + L, yy + 10 * math.sin(t * 2 + i), P(C('#ffffff'), 'stroke', 4, alpha=0.18))
    bx, by = W / 2, H / 2 + 40
    wake = skia.Path(); wake.moveTo(bx - 10, by + 60); wake.lineTo(bx - 70, by + 420); wake.lineTo(bx + 50, by + 420); wake.close()
    cv.drawPath(wake, P(C('#ffffff'), blur=12, alpha=0.35))
    cv.save(); cv.translate(bx, by); cv.rotate(4 * math.sin(t * 1.3))
    hull = skia.Path(); hull.moveTo(0, -150); hull.quadTo(55, -60, 45, 120); hull.lineTo(-45, 120); hull.quadTo(-55, -60, 0, -150); hull.close()
    cv.drawPath(hull, P(C('#f2f2ee'))); cv.drawPath(hull, P(C('#0b1320'), 'stroke', 6))
    cv.drawRoundRect(skia.Rect(-28, 0, 28, 50), 6, 6, P(C('#dfe7ec')))
    cv.drawCircle(0, -50, 20, P(C(J['cap']))); cv.drawCircle(0, 85, 18, P(C('#120c08')))
    cv.restore()

def map_route(cv, t, d, prm):
    grad(cv, '#08223b', '#0c2f50')
    k = lerp(prm.get('p0', 0), prm.get('p1', 1), ease(t / d))
    cv.save(); cv.translate(W / 2, 1080); cv.scale(1.0, 1.5); cv.translate(-W / 2, -530)
    R.map_inset(cv, k, 1.0)
    cv.restore()
    f = skia.Font(TF_BLACK, 64)
    lab = prm.get('label')
    if lab: cv.drawString(lab, (W - f.measureText(lab)) / 2, 520, f, P(C('#ffffff')))

def beach_crawl(cv, t, d, prm):
    R.sky(cv, 'dawn', t); R.sun(cv, W * 0.75, H * 0.33, 80)
    R.island(cv, W * 0.45, H * 0.43, 1.3, t)
    sand = skia.Path(); sand.moveTo(0, H * 0.5); sand.quadTo(W / 2, H * 0.47, W, H * 0.52); sand.lineTo(W, H); sand.lineTo(0, H); sand.close()
    cv.drawPath(sand, P(C('#d9bf86')))
    for i in range(3):
        k = (t * 0.8 + i / 3) % 1
        cv.drawOval(skia.Rect(-200, H * 0.66 - k * 120, W + 200, H * 0.74 - k * 120), P(C('#ffffff'), 'stroke', 10, alpha=0.5 * (1 - k)))
    R.ocean(cv, 'dawn', t, amp=14, horizon=H * 0.74, upto=2, foam=True)
    p = rig.cycle(t, rig.pose('crawl_a'), rig.pose('crawl_b'), 0.7) if t < d * 0.7 else rig.keyframes(t - d * 0.7, [(0, rig.pose('crawl_a')), (0.25, rig.pose('fist'))])
    x = lerp(W * 0.32, W * 0.5, ease(t / d))
    rig.draw_person(cv, x, H * 0.66, 1.6, p, J, 'determined', t, wet=True)

# ---------------- DEPART ----------------
def harbour(cv, t, d, prm):
    R.sky(cv, 'day', t); R.sun(cv, W * 0.85, H * 0.15, 60); R.clouds(cv, t, '#ffffff', 0.9, speed=30)
    horizon = H * 0.5
    for i, hx in enumerate((W * 0.62, W * 0.8)):  # town on the shore
        cv.drawRect(skia.Rect(hx - 70, horizon - 120 - i * 30, hx + 70, horizon), P(C(['#e8a36b', '#f1d38a'][i])))
        cv.drawRect(skia.Rect(hx - 80, horizon - 140 - i * 30, hx + 80, horizon - 110 - i * 30), P(C('#b5452f')))
    R.ocean(cv, 'day', t, amp=10, horizon=horizon)
    cv.drawRect(skia.Rect(W * 0.55, horizon + 60, W + 50, horizon + 100), P(C('#7a5230')))  # pier
    for px in range(int(W * 0.58), W + 40, 90): cv.drawRect(skia.Rect(px, horizon + 100, px + 18, horizon + 260), P(C('#5a3a1e')))
    bx = lerp(W * 0.62, W * 0.25, ease(t / d)); by = R.wave_y(bx, t, 1, 10, horizon) - 10
    boat_with_crew(cv, bx, by, 2 * math.sin(t * 2), t, 0.95, ('stand', 'happy'), ('stand', 'happy'))
    for j in range(4): R.bird(cv, (W * 0.1 + j * 220 + t * 160) % (W + 100), 420 + 60 * math.sin(t * 2 + j), 1.3, t * 9 + j)

def pull_cord(cv, t, d, prm):
    R.sky(cv, 'day', t); R.clouds(cv, t, '#ffffff', 0.8, speed=20)
    horizon = H * 0.5
    R.ocean(cv, 'day', t, amp=10, horizon=horizon)
    yank = [(0, rig.pose('pull_a')), (0.22, rig.pose('pull_b')), (0.4, rig.pose('pull_a')), (0.62, rig.pose('pull_b', head=-20))]
    p = rig.keyframes(t, yank)
    started = t > 0.64
    bx, by = W * 0.62, H * 0.66
    vib = 5 * math.sin(t * 90) if started else 0
    cv.save(); cv.translate(vib, 0)
    R.boat(cv, bx, by, 0, 1.7, icebox=False)
    cv.restore()
    mx, my = bx - 275 * 1.7 + vib, by - 65 * 1.7
    rig.draw_person(cv, bx - 120, by - 60, 1.25, p, J, 'happy' if started else 'determined', t, face=-1)
    hx = bx - 120 - 1.25 * (60 if p['armF_u'] > 0 else -50); hy = by - 60 - 1.25 * 120
    cv.drawLine(mx + 30, my - 20, hx, hy, P(C('#e8e2d0'), 'stroke', 5))
    if started:
        smoke(cv, mx - 20, my - 60, t, '#6b7078', 7, 260, 50, 34)
        for i in range(8):  # prop wash
            k = (t * 4 + i / 8) % 1
            cv.drawCircle(mx - 40 - k * 260, by + 60 + 20 * math.sin(i), 18 * (1 - k) + 4, P(C('#ffffff'), alpha=0.8 * (1 - k)))
    elif 0.22 < t < 0.36: smoke(cv, mx - 20, my - 60, t * 0.5, '#3a3f45', 3, 120, 20, 22)

def boat_speed(cv, t, d, prm):
    R.sky(cv, 'day', t); R.sun(cv, W * 0.2, H * 0.2, 55)
    horizon = H * 0.42
    R.ocean(cv, 'day', t * 2, amp=16, horizon=horizon)
    bx = lerp(W * 1.4, -W * 0.4, t / d); by = H * 0.60
    boat_with_crew(cv, bx, by, -6 + 3 * math.sin(t * 9), t, 1.7, ('stand', 'happy'), ('stand', 'happy'))
    for i in range(30):  # bow spray
        k = (t * 3 + i / 30) % 1
        cv.drawCircle(bx + 520 - k * 300 + 40 * math.sin(i), by - 40 - 200 * k + 300 * k * k, 10 * (1 - k) + 3, P(C('#ffffff'), alpha=0.8 * (1 - k)))
    for i in range(18):  # speed streaks
        y = (i * 113 + 900) % H
        cv.drawLine((i * 271 - t * 3000) % (W + 400) - 200, y, (i * 271 - t * 3000) % (W + 400) + 100, y, P(C('#ffffff'), 'stroke', 4, alpha=0.25))

def stopwatch(cv, t, d, prm):
    grad(cv, '#ffb000', '#ff7a00')
    for i in range(16):
        a = i / 16 * 2 * math.pi + t * 0.6
        cv.drawLine(W / 2, H * 0.42, W / 2 + math.cos(a) * 1600, H * 0.42 + math.sin(a) * 1600, P(C('#ffffff'), 'stroke', 60, alpha=0.08))
    cx, cy, r = W / 2, H * 0.42, 300
    cv.drawCircle(cx, cy, r + 30, P(C('#0b1320'))); cv.drawCircle(cx, cy, r, P(C('#ffffff')))
    cv.drawRoundRect(skia.Rect(cx - 50, cy - r - 110, cx + 50, cy - r - 30), 14, 14, P(C('#0b1320')))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        cv.drawLine(cx + math.sin(a) * r * 0.82, cy - math.cos(a) * r * 0.82, cx + math.sin(a) * r * 0.95, cy - math.cos(a) * r * 0.95, P(C('#0b1320'), 'stroke', 10))
    a = t * 9
    cv.drawLine(cx, cy, cx + math.sin(a) * r * 0.8, cy - math.cos(a) * r * 0.8, P(C(BRAND['danger']), 'stroke', 16))
    cv.drawCircle(cx, cy, 22, P(C('#0b1320')))

# ---------------- STORM ----------------
def storm_sky(cv, t, d, prm):
    R.sky(cv, 'storm', t); R.clouds(cv, t * 4, '#1c2532', 1.0, speed=80, dark=True)
    R.clouds(cv, t * 6 + 3, '#2a3546', 0.9, speed=120)
    R.rain(cv, t, 300, 0.5)
    fl = max(0, 1 - abs(t - d * 0.35) * 8)
    R.lightning(cv, fl, 3)

def engine_die(cv, t, d, prm):
    grad(cv, '#1a2230', '#0b1018')
    R.rain(cv, t, 220, 0.45)
    cx, cy = W / 2, H * 0.47
    dying = clamp(t / (d * 0.8)); vib = (1 - dying) * 14 * math.sin(t * 70)
    cv.save(); cv.translate(cx + vib, cy); cv.rotate(vib * 0.3)
    cv.drawRoundRect(skia.Rect(-260, -380, 260, 120), 60, 60, P(C('#2a2f36'))); cv.drawRoundRect(skia.Rect(-260, -380, 260, 120), 60, 60, P(C('#0b1320'), 'stroke', 14))
    cv.drawString('2T', -90, -110, skia.Font(TF_BLACK, 160), P(C('#ffb000')))
    cv.drawRect(skia.Rect(-60, 120, 60, 520), P(C('#22262c')))
    cv.save(); cv.translate(0, 560); cv.rotate((1 - dying) * t * 2400)
    for i in range(3): cv.rotate(120); cv.drawOval(skia.Rect(-30, -150, 30, 0), P(C('#9aa3ad')))
    cv.restore(); cv.restore()
    if t < d * 0.8: sparks(cv, cx + 200, cy - 300, t)
    smoke(cv, cx + 180, cy - 380, t, '#0d0f12', 10, 420, 80, 60)
    if t > d * 0.8:
        f = skia.Font(TF_BLACK, 110); txt = 'ENGINE DEAD'
        cv.drawString(txt, (W - f.measureText(txt)) / 2, H * 0.18, f, P(C(BRAND['danger'])))

def face_fear(cv, t, d, prm):
    R.sky(cv, 'storm', t); R.rain(cv, t, 260, 0.55)
    fl = max(0, 1 - abs(t - d * 0.6) * 9)
    look = (lerp(0.0, -0.9, ease(t / (d * 0.5))), -0.2)
    rig.draw_face_closeup(cv, W / 2, H * 0.52, 1.0, J, 'fear', t, look=look, wet=True, light='#9fb7ff')
    if fl: cv.drawRect(skia.Rect(0, 0, W, H), P(C('#dfe8ff'), alpha=0.5 * fl))
    vignette(cv, 0.7)

def big_wave(cv, t, d, prm):
    R.sky(cv, 'storm', t); R.clouds(cv, t * 3, '#1c2532', 1.0, speed=90)
    horizon = H * 0.45
    R.ocean(cv, 'storm', t * 2.2, amp=60, horizon=horizon)
    k = ease(t / d); wy = lerp(H * 0.9, H * 0.25, math.sin(k * math.pi) * 0.9)
    wave = skia.Path(); wave.moveTo(-100, H + 50)
    for x in range(-100, W + 150, 40): wave.lineTo(x, wy + 140 * math.sin(x * 0.004 + t * 3) + (x / W) * 260)
    wave.lineTo(W + 150, H + 50); wave.close()
    cv.drawPath(wave, P(C('#16324a')))
    crest = skia.Path(); first = True
    for x in range(-100, W + 150, 40):
        y = wy + 140 * math.sin(x * 0.004 + t * 3) + (x / W) * 260
        (crest.moveTo if first else crest.lineTo)(x, y); first = False
    cv.drawPath(crest, P(C('#e8f6ff'), 'stroke', 18, alpha=0.8))
    bx = W * 0.5; by = wy + 140 * math.sin(bx * 0.004 + t * 3) + 130 - 60
    boat_with_crew(cv, bx, by, lerp(-25, 25, k), t, 0.95, ('brace', 'fear'), ('panic', 'shock'), engine_ok=False, wet=True)
    particles(cv, t, 60, 9, '#e8f6ff', 3, 9, 900, -300, 0.7)
    R.rain(cv, t, 320, 0.6)

# ---------------- FOOD ----------------
def grab_fish(cv, t, d, prm):
    grad(cv, '#5d7a92', '#9cb5c8', 0, H * 0.4)
    R.ocean(cv, 'grey', t, amp=18, horizon=H * 0.40)
    k = clamp(t / (d * 0.45))
    fx, fy = lerp(W * 0.75, W * 0.52, k), H * 0.62 - 380 * math.sin(k * math.pi * 0.9)
    grabbed = t > d * 0.45
    arm_y = lerp(-200, H * 0.30, ease_out(clamp((t - d * 0.3) / (d * 0.18))))
    if grabbed: fx, fy = W * 0.52, arm_y + 330
    R.fish(cv, fx, fy, 3.2, -30 + (60 * math.sin(t * 40) if grabbed else -40 * k))
    cv.drawLine(W * 0.40, -100, W * 0.48, arm_y + 260, P(C('#0b1320'), 'stroke', 120))
    cv.drawLine(W * 0.40, -100, W * 0.48, arm_y + 260, P(C(J['skin']), 'stroke', 104))
    cv.drawCircle(W * 0.5, arm_y + 300, 80, P(C(J['skin']))); cv.drawCircle(W * 0.5, arm_y + 300, 80, P(C('#0b1320'), 'stroke', 8))
    splash(cv, W * 0.7, H * 0.62, t, 1.4, 2)
    splash(cv, W * 0.52, H * 0.55, t - d * 0.45, 1.0, 5)

def underwater_turtle(cv, t, d, prm):
    grad(cv, '#0f6aa8', '#04223d')
    for i in range(6):  # light rays
        x = 120 + i * 180 + 40 * math.sin(t + i)
        ray = skia.Path(); ray.moveTo(x, 0); ray.lineTo(x + 60, 0); ray.lineTo(x + 260, H); ray.lineTo(x + 140, H); ray.close()
        cv.drawPath(ray, P(C('#bfe7ff'), blur=20, alpha=0.12))
    hull = skia.Path(); hull.moveTo(W * 0.15, 260); hull.lineTo(W * 0.85, 260); hull.quadTo(W * 0.6, 420, W * 0.3, 400); hull.close()
    cv.drawPath(hull, P(C('#071725'), alpha=0.9))
    tx = lerp(W * 1.2, W * 0.5, ease_out(t / d)); ty = H * 0.55 - 120 * ease(t / d)
    cv.save(); cv.translate(tx, ty); cv.rotate(180 + 12 * math.sin(t * 4)); R.turtle(cv, 0, 0, 3.0); cv.restore()
    particles(cv, t, 40, 7, '#dff3ff', 4, 12, -260, alpha=0.6)

def bird_land(cv, t, d, prm):
    R.sky(cv, 'grey', t, 'day', 0.4); R.ocean(cv, 'grey', t, amp=14, horizon=H * 0.58)
    deck(cv, H * 0.80)
    k = clamp(t / (d * 0.5)); bx, by = lerp(W * 1.1, W * 0.66, ease_out(k)), lerp(H * 0.2, H * 0.765, ease_out(k))
    landed = t > d * 0.5
    if landed:
        cv.drawOval(skia.Rect(bx - 70, by - 60, bx + 60, by + 10), P(C('#f4f4f4'))); cv.drawCircle(bx + 55, by - 70, 32, P(C('#f4f4f4')))
        cv.drawCircle(bx + 64, by - 76, 5, P(C('#0b1320'))); cv.drawRect(skia.Rect(bx + 82, by - 72, bx + 120, by - 62), P(C('#ffb000')))
    else:
        R.bird(cv, bx, by, 4.0, t * 14, '#f4f4f4')
    p = rig.keyframes(t, [(0, rig.pose('sit')), (d * 0.6, rig.pose('sit', head=10)), (d * 0.8, rig.pose('grab_b'))])
    rig.draw_person(cv, W * 0.30, H * 0.86, 1.6, p, J, 'determined', t)
    if t > d * 0.85:
        particles(cv, t - d * 0.85, 18, 11, '#ffffff', 6, 14, -200, 120, 0.9, (W * 0.5, H * 0.62, W * 0.85, H * 0.78))

def rain_drink(cv, t, d, prm):
    R.sky(cv, 'grey', t); R.clouds(cv, t * 2, '#7d8c99', 0.9, speed=40)
    R.rain(cv, t, 260, 0.6, wind=-0.1)
    R.ocean(cv, 'grey', t, amp=14, horizon=H * 0.62)
    deck(cv, H * 0.80)
    rig.draw_person(cv, W * 0.40, H * 0.88, 1.7, rig.pose('drink', head=-45 + 6 * math.sin(t * 3)), J, 'relief', t, wet=True)
    bx, by = W * 0.78, H * 0.72  # bucket filling
    lvl = ease(t / d)
    cv.drawRect(skia.Rect(bx - 90, by - 150, bx + 90, by + 60), P(C('#d0d7de'))); cv.drawRect(skia.Rect(bx - 90, by + 60 - 210 * lvl, bx + 90, by + 60), P(C('#3b8fd6')))
    cv.drawRect(skia.Rect(bx - 90, by - 150, bx + 90, by + 60), P(C('#0b1320'), 'stroke', 8))

# ---------------- LOSS ----------------
def calendar_flip(cv, t, d, prm):
    grad(cv, '#161d2b', '#0b0f17')
    months = ['MONTH 1', 'MONTH 2', 'MONTH 3', 'MONTH 4']
    i = min(3, int(t / (d * 0.55) * 4)); fk = (t / (d * 0.55) * 4) % 1 if t < d * 0.55 else 0
    cx, cy = W / 2, H * 0.42
    cv.drawRoundRect(skia.Rect(cx - 330, cy - 300, cx + 330, cy + 300), 30, 30, P(C('#f4efe6')))
    cv.drawRect(skia.Rect(cx - 330, cy - 300, cx + 330, cy - 170), P(C(BRAND['danger'])))
    f = skia.Font(TF_BLACK, 120); txt = months[i]
    cv.drawString(txt, cx - f.measureText(txt) / 2, cy + 80, f, P(C('#0b1320')))
    if t < d * 0.55 and i < 3:  # page flying off
        cv.save(); cv.translate(cx, cy - 300); cv.rotate(-fk * 120); cv.translate(fk * 400, -fk * 600)
        cv.drawRoundRect(skia.Rect(-330, 0, 330, 600), 30, 30, P(C('#ece6d8'), alpha=1 - fk)); cv.restore()

def refuse_food(cv, t, d, prm):
    R.sky(cv, 'sunset', t); R.ocean(cv, 'sunset', t * 0.6, amp=10, horizon=H * 0.55)
    deck(cv, H * 0.80)
    pj = rig.keyframes(t, [(0, rig.pose('sit')), (d * 0.3, rig.pose('offer'))])
    pe = rig.keyframes(t, [(0, rig.pose('sit', head=10)), (d * 0.45, rig.pose('sit', head=10)), (d * 0.8, rig.pose('turn_away'))])
    rig.draw_person(cv, W * 0.27, H * 0.88, 1.45, pj, J, 'sad' if t > d * 0.6 else 'neutral', t)
    rig.draw_person(cv, W * 0.75, H * 0.88, 1.45, pe, E, 'sad', t + 1, face=-1)
    if t > d * 0.3: R.fish(cv, W * 0.50, H * 0.70, 1.2, 0)

def alone_night(cv, t, d, prm):
    R.sky(cv, 'night', t); R.stars(cv, t, 1.0); R.moon(cv, W * 0.7, H * 0.25, 70, 0.5)
    horizon = H * 0.5
    R.ocean(cv, 'night', t * 0.5, amp=10, horizon=horizon)
    cv.drawRect(skia.Rect(W * 0.35, horizon, W * 0.9, H), P(C('#9fb7ff'), blur=60, alpha=0.08))  # moon path
    bx = W / 2; by = R.wave_y(bx, t * 0.5, 1, 10, horizon) - 10
    boat_with_crew(cv, bx, by, 1.5 * math.sin(t), t, 0.9, (rig.pose('slump'), 'sad'), None)

def face_grief(cv, t, d, prm):
    grad(cv, '#0a1222', '#1a2a4a')
    R.stars(cv, t, 0.6)
    rig.draw_face_closeup(cv, W / 2, H * 0.52, 1.0, J, 'sad', t, look=(0.0, 0.4), tear=t / d, light='#9fb7ff')
    vignette(cv, 0.7)

# ---------------- ALONE ----------------
def ship_pov(cv, t, d, prm):
    R.sky(cv, 'day', t); R.clouds(cv, t, '#ffffff', 0.7)
    horizon = H * 0.48
    R.ship(cv, lerp(W * 0.1, W * 0.8, t / d), horizon - 4, 1.3)
    R.ocean(cv, 'day', t, amp=14, horizon=horizon)
    bow = skia.Path(); bow.moveTo(W * 0.15, H); bow.quadTo(W * 0.5, H * 0.70, W * 0.85, H); bow.close()  # our bow
    cv.drawPath(bow, P(C('#f2f2ee'))); cv.drawPath(bow, P(C('#0b1320'), 'stroke', 10))
    for side in (-1, 1):  # waving arms from the bottom of frame
        a = math.radians(25 * side + 25 * math.sin(t * 11 + side))
        x0, y0 = W / 2 + side * 260, H + 40
        x1, y1 = x0 + math.sin(a) * 700, y0 - math.cos(a) * 700
        cv.drawLine(x0, y0, x1, y1, P(C('#0b1320'), 'stroke', 120)); cv.drawLine(x0, y0, x1, y1, P(C(J['skin']), 'stroke', 104))
        cv.drawCircle(x1, y1, 75, P(C(J['skin']))); cv.drawCircle(x1, y1, 75, P(C('#0b1320'), 'stroke', 8))

def ship_gone(cv, t, d, prm):
    R.sky(cv, 'sunset', t); horizon = H * 0.52
    R.ship(cv, lerp(W * 0.75, W * 1.05, t / d), horizon - 4, lerp(0.7, 0.35, t / d))
    R.ocean(cv, 'sunset', t, amp=12, horizon=horizon)
    p = rig.cycle(t, rig.pose('wave_a'), rig.pose('wave_b'), 0.35) if t < d * 0.55 else rig.keyframes(t - d * 0.55, [(0, rig.pose('wave_a')), (0.3, rig.pose('drop'))])
    bx = W * 0.35; by = R.wave_y(bx, t, 1, 12, horizon) - 10
    cv.save(); cv.translate(bx, by)
    rig.draw_person(cv, -60, -40, 1.0, p, J, 'fear' if t < d * 0.55 else 'sad', t)
    cv.restore(); R.boat(cv, bx, by, 2 * math.sin(t), 1.0, icebox=False)

def tally(cv, t, d, prm):
    grad(cv, '#cfc6b4', '#a89c86')
    for i in range(9): cv.drawLine(0, i * 230 + 60, W, i * 230 + 60, P(C('#7a6e5a'), 'stroke', 6, alpha=0.6))  # planks
    n = int(lerp(prm.get('n0', 5), prm.get('n1', 300), ease(t / d) ** 1.6))
    marks = min(n, 60)
    for m in range(marks):
        g, j = divmod(m, 5); gx = 120 + (g % 4) * 230; gy = 300 + (g // 4) * 330
        if j < 4: cv.drawLine(gx + j * 40, gy, gx + j * 40, gy + 200, P(C('#3a2e22'), 'stroke', 14))
        else: cv.drawLine(gx - 20, gy + 170, gx + 150, gy + 30, P(C('#3a2e22'), 'stroke', 14))
    kx = 120 + ((marks // 5) % 4) * 230 + (marks % 5) * 40; ky = 300 + ((marks // 5) // 4) * 330
    cv.save(); cv.translate(kx + 40, ky + 60); cv.rotate(35 + 10 * math.sin(t * 30))
    cv.drawRect(skia.Rect(-14, -220, 14, 0), P(C('#c8cfd6'))); cv.drawRect(skia.Rect(-22, 0, 22, 160), P(C('#4a2c18'))); cv.restore()

def moon_montage(cv, t, d, prm):
    cyc = t / d * 6
    night = 0.5 + 0.5 * math.cos(cyc * 2 * math.pi)
    R.sky(cv, 'day', t, 'night', night); R.stars(cv, t, night)
    R.moon(cv, W / 2, H * 0.3, 160, (cyc * 0.3) % 1)
    R.ocean(cv, 'night' if night > 0.5 else 'day', t * 2, amp=12, horizon=H * 0.6)
    bx = W / 2; by = R.wave_y(bx, t * 2, 1, 12, H * 0.6) - 10
    boat_with_crew(cv, bx, by, 2 * math.sin(t * 3), t, 0.8, (rig.pose('slump'), 'exhausted'), None)

# ---------------- LAND ----------------
def day438(cv, t, d, prm):
    R.sky(cv, 'dawn', t); R.sun(cv, W * 0.5, H * 0.46, 120)
    horizon = H * 0.5; R.ocean(cv, 'dawn', t, amp=10, horizon=horizon)
    bx = W / 2; by = R.wave_y(bx, t, 1, 10, horizon) - 10
    p = rig.keyframes(t, [(0, rig.pose('slump')), (d * 0.6, rig.pose('sit', head=-15))])
    boat_with_crew(cv, bx, by, math.sin(t), t, 1.1, (p, 'exhausted' if t < d * 0.6 else 'shock'), None)

def birds_flyby(cv, t, d, prm):
    R.sky(cv, 'day', t, 'sunset', 0.2); R.clouds(cv, t, '#ffffff', 0.8)
    R.ocean(cv, 'day', t, amp=12, horizon=H * 0.7)
    for j in range(5):
        x = lerp(-300 - j * 200, W + 300 + j * 100, t / d); y = 600 + j * 160 + 50 * math.sin(t * 4 + j)
        R.bird(cv, x, y, 4.5 - j * 0.6, t * 12 + j)

def coconut(cv, t, d, prm):
    grad(cv, '#7fc4ff', '#cdeaff', 0, H * 0.3)
    R.ocean(cv, 'day', t, amp=26, horizon=H * 0.3)
    cy = R.wave_y(W / 2, t, 2, 26, H * 0.3) - 40
    k = ease_out(t / (d * 0.6)); cx = lerp(W * 1.2, W * 0.5, k)
    R.coconut(cv, cx, cy, 7.0)
    for i in range(22):  # husk fibres + highlight
        a = i / 22 * 2 * math.pi
        cv.drawLine(cx + math.cos(a) * 120, cy + math.sin(a) * 120, cx + math.cos(a + 0.2) * 178, cy + math.sin(a + 0.2) * 178, P(C('#8a5a2e'), 'stroke', 8))
    cv.drawCircle(cx - 60, cy - 70, 40, P(C('#c08a52'), blur=12, alpha=0.6))
    for i in range(5):
        a = t * 3 + i
        cv.drawCircle(cx + math.cos(a) * 260, cy + math.sin(a) * 90 + 60, 10, P(C('#ffffff'), alpha=0.5))

def island_reveal(cv, t, d, prm):
    R.sky(cv, 'day', t, 'sunset', 0.15); R.sun(cv, W * 0.8, H * 0.3, 60)
    horizon = H * 0.5
    R.island(cv, W * 0.5, horizon + 4, lerp(0.15, 1.1, ease(t / d)), t)
    R.ocean(cv, 'day', t, amp=14, horizon=horizon)
    p = rig.keyframes(t, [(0, rig.pose('sit', head=20)), (d * 0.3, rig.pose('sit', head=-10)), (d * 0.7, rig.pose('fist'))])
    deck(cv, H * 0.86)
    rig.draw_person(cv, W * 0.22, H * 0.95, 1.9, p, J, 'shock' if t < d * 0.7 else 'relief', t)  # over-the-shoulder

def swim(cv, t, d, prm):
    R.sky(cv, 'day', t, 'sunset', 0.25)
    horizon = H * 0.44
    R.island(cv, W * 0.75, horizon + 4, 1.0, t)
    R.ocean(cv, 'day', t, amp=16, horizon=horizon)
    wl = H * 0.58
    cv.drawRect(skia.Rect(0, wl, W, H), P(C('#0d4f8b'), alpha=0.55))  # half-underwater split
    if t < d * 0.25:
        k = t / (d * 0.25); x = lerp(W * 0.1, W * 0.3, k); y = lerp(wl - 300, wl + 20, k * k)
        rig.draw_person(cv, x, y, 1.3, rig.pose('dive'), J, 'determined', t)
    else:
        tt = t - d * 0.25
        rig.draw_person(cv, lerp(W * 0.3, W * 0.65, tt / (d * 0.75)), wl + 40, 1.3, rig.cycle(tt, rig.pose('swim_a'), rig.pose('swim_b'), 0.45), J, 'determined', t)
    splash(cv, W * 0.3, wl, t - d * 0.25, 1.5, 8)
    particles(cv, t, 30, 13, '#dff3ff', 4, 10, -200, alpha=0.5, area=(0, wl, W, H))

def beach_end(cv, t, d, prm):
    grad(cv, '#e2c88f', '#cfae6c')
    for i in range(3):  # top-down surf
        k = (t * 0.5 + i / 3) % 1
        cv.drawRect(skia.Rect(-50, H * 0.72 + k * 80, W + 50, H), P(C('#3a8fd0'), alpha=0.25 + 0.1 * i))
        cv.drawLine(-50, H * 0.72 + k * 80, W + 50, H * 0.72 + k * 80, P(C('#ffffff'), 'stroke', 14, alpha=0.6 * (1 - k)))
    rig.draw_person(cv, W * 0.55, H * 0.50, 1.6, rig.pose('collapse', head=-20 + 4 * math.sin(t * 2)), J, 'relief', t)
    for j, (px, py) in enumerate(((W * 0.15, H * 0.12), (W * 0.62, H * 0.08), (W * 0.9, H * 0.26))):
        for i in range(7):
            a = i / 7 * 2 * math.pi + 0.05 * math.sin(t * 2 + j)
            leaf = skia.Path(); leaf.moveTo(px, py); leaf.quadTo(px + math.cos(a + 0.3) * 120, py + math.sin(a + 0.3) * 120, px + math.cos(a) * 210, py + math.sin(a) * 210)
            cv.drawPath(leaf, P(C('#2f7a3a'), 'stroke', 34))
        cv.drawCircle(px, py, 26, P(C('#6b4a2b')))

SHOTS = {k: v for k, v in globals().items() if callable(v) and getattr(v, '__code__', None) and v.__code__.co_argcount == 4 and k not in ('grad', 'particles', 'sea_scene')}
