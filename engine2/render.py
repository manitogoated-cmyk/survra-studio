"""Storyboard -> video. Allocates each narration segment's time across its shots, runs the camera
(start->end framing, punch-ins, shake, Dutch tilt), transitions (cut / whip / zoom / flash), HUD and captions.
Writes build/edl.json (shot times + absolute SFX cues) for the sound designer and the QC gate."""
import json, math, os, subprocess, sys
import skia
from common import W, H, FPS, C, P, lerp, clamp, ease, ease_out, BRAND
import shots as S
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engine'))
import render_fast as RF
import render_short as R

def edl(timeline, board):
    segs = timeline['segments']; total = timeline['duration']
    win = {}
    for i, s in enumerate(segs):
        a = 0.0 if i == 0 else s['start'] - 0.05
        b = segs[i + 1]['start'] - 0.05 if i + 1 < len(segs) else total
        win[s['scene']] = (a, b)
    out = []
    for seg in [s['scene'] for s in segs]:
        group = [sh for sh in board['shots'] if sh['segment'] == seg]
        a, b = win[seg]; tw = sum(sh['weight'] for sh in group); t = a
        for sh in group:
            d = (b - a) * sh['weight'] / tw
            out.append({**sh, 'a': t, 'b': t + d}); t += d
    words = [w for s in segs for w in s['words']]
    impacts = [w['start'] for w in words if any(ch.isdigit() for ch in w['w'])]
    cues = [{'t': sh['a'] + f * (sh['b'] - sh['a']), 'sfx': name} for sh in out for name, f in sh['sfx']]
    cues += [{'t': sh['a'], 'sfx': 'trans_' + sh['transition']} for sh in out if sh['a'] > 0.05]
    cues += [{'t': t, 'sfx': 'impact_num'} for t in impacts]
    return out, words, impacts, sorted(cues, key=lambda c: c['t']), {k: list(v) for k, v in win.items()}

def camera(cv, sh, t, impacts):
    lt = t - sh['a']; d = sh['b'] - sh['a']; k = ease(lt / d)
    z0, x0, y0, r0 = sh['cam'][0]; z1, x1, y1, r1 = sh['cam'][1]
    z, fx, fy, rot = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k), lerp(r0, r1, k)
    tr = sh['transition']
    if tr == 'cut': z *= 1 + 0.10 * (1 - ease_out(lt / 0.18))
    if tr == 'zoom': z *= 1 + 1.0 * (1 - ease_out(lt / 0.2))
    amp = sh.get('shake', 0)
    for it in impacts:
        if 0 <= t - it < 0.3: amp = max(amp, 24 * (1 - (t - it) / 0.3))
    sx, sy = amp * math.sin(t * 93), amp * math.cos(t * 71)
    slide = 0.0
    if tr == 'whip' and lt < 0.14: slide = W * 0.9 * (1 - ease_out(lt / 0.14))
    z *= 1 + abs(rot) * 0.035                      # cover the corners when tilted
    hw, hh = W / (2 * z), H / (2 * z)               # keep the view inside the drawn world
    fx = min(max(fx, hw), W - hw); fy = min(max(fy, hh), H - hh)
    cv.translate(W / 2 + sx + slide, H / 2 + sy); cv.rotate(rot); cv.scale(z, z); cv.translate(-fx, -fy)
    return lt

def overlays(cv, sh, t):
    lt = t - sh['a']
    if sh['transition'] == 'whip' and lt < 0.14:
        m = 1 - lt / 0.14
        for j in range(14):
            y = (j * 151 + int(t * 997)) % H
            cv.drawRect(skia.Rect(0, y, W, y + 6 + j % 3 * 4), P(C('#ffffff'), alpha=0.12 * m))
    if sh['transition'] == 'flash' and lt < 0.12: cv.drawRect(skia.Rect(0, 0, W, H), P(C('#ffffff'), alpha=0.85 * (1 - lt / 0.12)))
    if sh['transition'] == 'zoom' and lt < 0.12: cv.drawRect(skia.Rect(0, 0, W, H), P(C('#ffffff'), alpha=0.3 * (1 - lt / 0.12)))

def render(build_dir, board_path, out_path, only=None):
    tl = json.load(open(os.path.join(build_dir, 'timeline.json'))); board = json.load(open(board_path))
    shots, words, impacts, cues, win = edl(tl, board)
    json.dump({'shots': [{k: sh[k] for k in ('n', 'kind', 'segment', 'a', 'b', 'transition', 'action', 'camera')} for sh in shots],
               'cues': cues, 'impacts': impacts, 'windows': win, 'duration': tl['duration']},
              open(os.path.join(build_dir, 'edl.json'), 'w'), indent=1)
    total = tl['duration']; n = int(total * FPS)
    frames = range(n) if only is None else [int(x * FPS) for x in only]
    ff = None
    if only is None:
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                               '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    last_day, changed = None, 0.0; stills = []
    for fi in frames:
        t = fi / FPS
        sh = shots[max(i for i, s in enumerate(shots) if s['a'] <= t or i == 0)]
        cv.clear(C('#000000')); cv.save()
        lt = camera(cv, sh, t, impacts)
        S.SHOTS[sh['kind']](cv, lt, sh['b'] - sh['a'], sh['prm'])
        cv.restore()
        overlays(cv, sh, t)
        if sh['hud_day'] is not None:
            if sh['hud_day'] != last_day: last_day, changed = sh['hud_day'], t
            RF.slam_day(cv, sh['hud_day'], t - changed)
        RF.pop_caption(cv, words, t)
        RF.progress(cv, t, total)
        img = surf.makeImageSnapshot()
        if ff: ff.stdin.write(img.toarray().tobytes())
        else: stills.append((t, img))
        if ff and fi % 150 == 0: print(f'frame {fi}/{n}', flush=True)
    if ff: ff.stdin.close(); ff.wait()
    return stills, shots

if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2], sys.argv[3])
