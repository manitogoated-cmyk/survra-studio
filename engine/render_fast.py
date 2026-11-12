"""Fast-paced Shorts renderer.

Reuses the drawn world from render_short (sky, sea, boat, rigged characters...) and adds what makes a Short
hold attention: a new shot every ~1.5-2.5 s with punch-in zooms, whip-pan + flash transitions between beats,
camera shake on impacts, 1-2 word pop captions, slamming numbers and a progress bar.
Writes build/cuts.json so the sound bed can put whooshes and hits exactly on the edits.
"""
import json, math, os, subprocess, sys
import skia
sys.path.insert(0, os.path.dirname(__file__))
import render_short as R
from render_short import W, H, FPS, C, P, lerp, clamp, ease, ease_out, BRAND, TF_BLACK, TF_BOLD

# (zoom, focus_x, focus_y) per shot; a beat's time is split across its shots
SHOTS = {
    'hook':   [(2.2, 600, 900), (1.0, 540, 960)],
    'depart': [(1.0, 540, 960), (2.0, 470, 960)],
    'storm':  [(1.25, 540, 1000), (2.4, 380, 890), (1.0, 540, 960)],
    'food':   [(1.5, 540, 1000), (1.0, 540, 960)],
    'loss':   [(1.35, 540, 1050), (2.3, 370, 940)],
    'alone':  [(1.0, 540, 960), (2.2, 600, 940)],
    'land':   [(1.0, 540, 960), (1.35, 540, 900), (2.0, 540, 1150)],
    'end':    [(1.0, 540, 960)],
}
WHIP = 0.13  # seconds each side of a beat change

def plan(tl):
    segs = tl['segments']; total = tl['duration']
    beats = []
    for i, s in enumerate(segs):
        a = 0.0 if i == 0 else s['start'] - 0.06
        b = segs[i + 1]['start'] - 0.06 if i + 1 < len(segs) else total
        beats.append((a, b, s))
    shots = []
    for bi, (a, b, s) in enumerate(beats):
        spec = SHOTS[s['scene']]; n = len(spec)
        for k, sh in enumerate(spec):
            sa = a + (b - a) * k / n; sb = a + (b - a) * (k + 1) / n
            shots.append({'beat': bi, 'a': sa, 'b': sb, 'zoom': sh[0], 'fx': sh[1], 'fy': sh[2], 'first': k == 0})
    words = [w for s in segs for w in s['words']]
    impacts = [w['start'] for w in words if any(ch.isdigit() for ch in w['w'])]
    cuts = [{'t': sh['a'], 'type': 'whip' if sh['first'] else 'cut'} for sh in shots if sh['a'] > 0.05]
    return beats, shots, words, impacts, cuts

def shake_at(t, impacts, storm):
    amp = 0.0
    for it in impacts:
        if 0 <= t - it < 0.35: amp = max(amp, 22 * (1 - (t - it) / 0.35))
    amp += 6 if storm else 0
    return amp * math.sin(t * 91.0), amp * math.cos(t * 77.0)

def draw_world(cv, beat, shot, t, impacts):
    a, b, s = beat
    lt = t - a
    # punch-in at each shot start, then a slow push
    since = t - shot['a']
    z = shot['zoom'] * (1 + 0.14 * (1 - ease_out(since / 0.28))) * (1 + 0.025 * since)
    sx, sy = shake_at(t, impacts, s['scene'] == 'storm')
    cv.save()
    cv.translate(W / 2 + sx, H / 2 + sy); cv.scale(z, z); cv.translate(-shot['fx'], -shot['fy'])
    R.SCENES[s['scene']](cv, lt, b - a)
    cv.restore()

def pop_caption(cv, words, t):
    live = [i for i, w in enumerate(words) if w['start'] - 0.04 <= t]
    if not live or t > words[-1]['end'] + 0.5: return
    i = live[-1]
    # group 2 words, but a number always stands alone
    groups = []; g = []
    for k, w in enumerate(words):
        isnum = any(ch.isdigit() for ch in w['w'])
        if isnum:
            if g: groups.append(g); g = []
            groups.append([k]); continue
        g.append(k)
        if len(g) == 2 or w['w'][-1:] in '.,?!': groups.append(g); g = []
    if g: groups.append(g)
    grp = next(gr for gr in groups if i in gr)
    g0 = words[grp[0]]['start']; age = t - g0
    sc = 0.6 + 0.4 * ease_out(age / 0.12) + 0.08 * math.sin(clamp(age / 0.2) * math.pi)
    big = any(ch.isdigit() for ch in words[grp[0]]['w'])
    size = 190 if big else 118
    f = skia.Font(TF_BLACK, size); space = f.measureText(' ')
    texts = [words[k]['w'].upper().strip(',') for k in grp]
    widths = [f.measureText(x) for x in texts]; total = sum(widths) + space * (len(texts) - 1)
    if total > W - 100:
        size *= (W - 100) / total; f = skia.Font(TF_BLACK, size); space = f.measureText(' ')
        widths = [f.measureText(x) for x in texts]; total = sum(widths) + space * (len(texts) - 1)
    cy = H * 0.70
    cv.save(); cv.translate(W / 2, cy); cv.scale(sc, sc); cv.rotate(-3 if big else 0)
    x = -total / 2
    for k, txt, wd in zip(grp, texts, widths):
        active = k == i
        col = BRAND['accent'] if (big or active) else '#ffffff'
        cv.drawString(txt, x + 6, 8, f, P(C('#000000'), alpha=0.55))           # drop shadow
        cv.drawString(txt, x, 0, f, P(C('#000000'), 'stroke', size * 0.16))
        cv.drawString(txt, x, 0, f, P(C(col)))
        x += wd + space
    cv.restore()

def slam_day(cv, day, since_change):
    k = clamp(since_change / 0.22)
    sc = 1.0 + 0.45 * (1 - ease_out(k))
    cv.save(); cv.translate(70, 250); cv.scale(sc, sc); cv.translate(-70, -250)
    R.day_counter(cv, day, pulse=0.8 * (1 - k))
    cv.restore()

def title_slam(cv, t):
    """Hook overlay: '438 DAYS' slams in at the very start."""
    if t > 2.2: return
    k = ease_out(t / 0.18); fade = 1 - ease((t - 1.8) / 0.4)
    f = skia.Font(TF_BLACK, 210); f2 = skia.Font(TF_BLACK, 92)
    cv.save(); cv.translate(W / 2, H * 0.24); cv.scale(2.2 - 1.2 * k, 2.2 - 1.2 * k); cv.rotate(-4)
    for txt, ff, y, col in (('438', f, 0, BRAND['accent']), ('DAYS ADRIFT', f2, 105, '#ffffff')):
        x = -ff.measureText(txt) / 2
        cv.drawString(txt, x, y, ff, P(C('#000000'), 'stroke', 26, alpha=fade))
        cv.drawString(txt, x, y, ff, P(C(col), alpha=fade))
    cv.restore()

def progress(cv, t, total):
    cv.drawRect(skia.Rect(0, 0, W, 10), P(C('#000000'), alpha=0.35))
    cv.drawRect(skia.Rect(0, 0, W * clamp(t / total), 10), P(C(BRAND['accent'])))

def render(build_dir, out_path):
    tl = json.load(open(os.path.join(build_dir, 'timeline.json'))); total = tl['duration']
    beats, shots, words, impacts, cuts = plan(tl)
    json.dump({'cuts': cuts, 'impacts': impacts, 'beats': [(a, b, s['scene']) for a, b, s in beats]},
              open(os.path.join(build_dir, 'cuts.json'), 'w'), indent=1)
    n = int(total * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    last_day = None; day_changed_at = 0.0
    for fi in range(n):
        t = fi / FPS
        si = max(i for i, sh in enumerate(shots) if sh['a'] <= t or i == 0); shot = shots[si]
        beat = beats[shot['beat']]
        cv.clear(C('#000000'))
        # whip transition across beat changes: outgoing slides left, incoming arrives from the right
        nxt = shots[si + 1] if si + 1 < len(shots) else None
        into = t - shot['a'] if shot['first'] and shot['beat'] > 0 else 99
        outof = (nxt['a'] - t) if (nxt and nxt['first']) else 99
        if into < WHIP:
            k = 1 - ease_out(into / WHIP)
            cv.save(); cv.translate(W * 0.9 * k, 0); draw_world(cv, beat, shot, t, impacts); cv.restore()
        elif outof < WHIP:
            k = 1 - ease(outof / WHIP)
            cv.save(); cv.translate(-W * 0.9 * k, 0); draw_world(cv, beat, shot, t, impacts); cv.restore()
        else:
            draw_world(cv, beat, shot, t, impacts)
        if into < WHIP or outof < WHIP:  # motion streaks + flash
            m = 1 - min(into, outof) / WHIP
            for j in range(14):
                y = (j * 151 + int(t * 997)) % H
                cv.drawRect(skia.Rect(0, y, W, y + 6 + j % 3 * 4), P(C('#ffffff'), alpha=0.10 * m))
            cv.drawRect(skia.Rect(0, 0, W, H), P(C('#ffffff'), alpha=0.35 * m))
        a, b, s = beat
        # HUD
        if s['scene'] == 'hook':
            title_slam(cv, t)
        elif s['scene'] != 'end':
            day = s['day']
            if day != last_day: last_day = day; day_changed_at = t
            slam_day(cv, day, t - day_changed_at)
            food = {'depart': 1.0, 'storm': 0.8, 'food': 0.45, 'loss': 0.25, 'alone': 0.15, 'land': 0.08}.get(s['scene'])
            if food is not None:
                R.meter(cv, 'FOOD', food, 150, '#ffb000'); R.meter(cv, 'WATER', food * 0.9 + 0.05, 230, '#3b8fd6')
            if s['scene'] in ('alone', 'land'):
                p0, p1 = {'alone': (0.25, 0.85), 'land': (0.88, 1.0)}[s['scene']]
                kk = clamp((t - a) / (b - a)); al = ease((t - a) / 0.25) * (1 - ease((t - (b - 0.2)) / 0.2))
                if al > 0: R.map_inset(cv, lerp(p0, p1, kk), al)
        pop_caption(cv, words, t)
        progress(cv, t, total)
        ff.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
        if fi % 150 == 0: print(f'frame {fi}/{n}', flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2])
