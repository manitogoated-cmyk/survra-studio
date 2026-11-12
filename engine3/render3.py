"""Episode renderer: storyboard + per-episode scenes.py + Kesta acting/lip-sync -> video.

episodes/<id>/
  episode.json     format short|long, ...
  script.json      narration (Kesta's lines) with segment 'scene' and 'mood'
  storyboard.json  shots: {n, segment, weight, kind, action, camera, cam:[[z,fx,fy,rot],[..]], shake,
                           transition: cut|whip|zoom|flash|flare, sfx:[[name,frac]], hud, prm}
  scenes.py        THIS story's world: SHOTS = {kind: f(cv, ctx)} drawn in world coordinates (W x H)
"""
import importlib.util
import json
import math
import os
import subprocess
import sys

import numpy as np
import skia
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine3 import kesta as K  # noqa: E402
from engine3 import cast as CAST  # noqa: E402
from engine3 import world as Wd  # noqa: E402
from engine3.voice3 import LipSync  # noqa: E402

FPS = 30
FORMATS = {'short': (1080, 1920), 'long': (1920, 1080)}
TF = skia.Typeface('Inter', skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant))


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def ease_out(k):
    k = max(0.0, min(1.0, k))
    return 1 - (1 - k) ** 3


def load_scenes(ep_dir):
    spec = importlib.util.spec_from_file_location('scenes_' + os.path.basename(ep_dir).replace('-', '_'),
                                                  os.path.join(ep_dir, 'scenes.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def edl(timeline, board):
    segs = timeline['segments']
    total = timeline['duration']
    win = {}
    for i, s in enumerate(segs):
        a = 0.0 if i == 0 else s['start'] - 0.05
        b = segs[i + 1]['start'] - 0.05 if i + 1 < len(segs) else total
        win[s['scene']] = (a, b)
    out = []
    for seg in [s['scene'] for s in segs]:
        group = [sh for sh in board['shots'] if sh['segment'] == seg]
        a, b = win[seg]
        tw = sum(sh['weight'] for sh in group)
        t = a
        for sh in group:
            d = (b - a) * sh['weight'] / tw
            out.append({**sh, 'a': t, 'b': t + d})
            t += d
    words = [w for s in segs for w in s['words']]
    impacts = [w['start'] for w in words if any(ch.isdigit() for ch in w['w'])]
    cues = [{'t': sh['a'] + f * (sh['b'] - sh['a']), 'sfx': name} for sh in out for name, f in sh.get('sfx', [])]
    cues += [{'t': sh['a'], 'sfx': 'trans_' + sh['transition']} for sh in out if sh['a'] > 0.05]
    cues += [{'t': t, 'sfx': 'impact_num'} for t in impacts]
    moods = {s['scene']: s.get('mood', 'calm') for s in segs}
    return out, words, impacts, sorted(cues, key=lambda c: c['t']), {k: list(v) for k, v in win.items()}, moods


class Ctx:
    """Everything a scene function needs."""

    def __init__(self, W, H, lips, words):
        self.W, self.H = W, H
        self.lips = lips
        self.words = words
        self.t = self.lt = self.d = self.k = 0.0
        self.prm = {}
        self.sh = None

    def _speech(self):
        v, k = self.lips.at(self.t)
        return v, k

    def word_index(self):
        for i, w in enumerate(self.words):
            if w['start'] <= self.t < w['end'] + 0.05:
                return i
        return -1

    def kesta(self, x, y, s, pose, facing=1, expr='neutral', look=(0.0, 0.0), goggles='up', wind=0.0, speed=0.0,
              talk=True, gesture=True, alpha=1.0, prop_glow=0.0):
        vis, kopen = self._speech() if talk else ('rest', 0.0)
        p = dict(pose)
        if talk and gesture and vis != 'rest' and p.get('prop') is None and p.get('crouch', 0) < 5:
            idle_arm = abs(p.get('aFu', K.BASE['aFu']) - K.BASE['aFu']) < 25
            if idle_arm:
                wi = max(0, self.word_index())
                g = K.pose(['talk_a', 'talk_b', 'talk_c'][(wi // 3) % 3])
                beat = 0.55 + 0.25 * math.sin(self.t * 5.0)
                p['aFu'] = K.lerp(p.get('aFu', K.BASE['aFu']), g['aFu'], beat)
                p['aFl'] = K.lerp(p.get('aFl', K.BASE['aFl']), g['aFl'], beat)
                p['hF'] = g['hF']
            p['nod'] = p.get('nod', 0) + math.sin(self.t * 7) * 2.0
        K.draw_kesta(self_cv(self), x, y, s, p, self.t, facing=facing, expr=expr, viseme=vis, look=look,
                     goggles=goggles, wind=wind, speed=speed, alpha=alpha, k_open=kopen, prop_glow=prop_glow)

    def host(self, x, y, h, pose='stand', view='tq', facing=1, expr='happy', talk=True):
        """Rook. h = height in pixels (feet to hat). Lip sync and talk gestures are automatic."""
        from engine3 import host as Hm
        p = Hm.pose(pose) if isinstance(pose, str) else dict(pose)
        beak = None
        if talk:
            vis, k = self.lips.at(self.t)
            beak = Hm.VIS.get(vis, 1.5) * min(1.2, k)
            if vis != 'rest' and abs(p['hr'][0] - 4) < 7 and abs(p['hr'][1] - 29) < 7 and abs(p['hl'][1] - 29) < 7:
                g = Hm.GEST[(max(0, self.word_index()) // 4) % len(Hm.GEST)]
                p = Hm.blend(p, g, 0.6 + 0.2 * math.sin(self.t * 5))
        p['lift'] = p['lift'] + math.sin(self.t * 2.3) * 0.5
        Hm.draw_rook(self_cv(self), x, y, h, p, view, facing, expr, beak, self.t)

    def person(self, L, x, y, s, pose, facing=1, expr='neutral', look=(0.0, 0.0), alpha=1.0, prop=None, speaking=False, wet=0.0):
        vis = 'rest'
        if speaking:
            vis = ['AI', 'E', 'O', 'rest', 'etc'][int(self.t * 9) % 5]
        CAST.draw_person(self_cv(self), x, y, s, pose, self.t, L, facing=facing, expr=expr, viseme=vis, look=look,
                         alpha=alpha, prop=prop, wet=wet)


_CV = {}


def self_cv(ctx):
    return _CV['cv']


def camera(cv, sh, t, impacts, W, H):
    lt = t - sh['a']
    d = sh['b'] - sh['a']
    k = ease(lt / d)
    z0, x0, y0, r0 = sh['cam'][0]
    z1, x1, y1, r1 = sh['cam'][1]
    z, fx, fy, rot = K.lerp(z0, z1, k), K.lerp(x0, x1, k), K.lerp(y0, y1, k), K.lerp(r0, r1, k)
    tr = sh['transition']
    if tr == 'cut':
        z *= 1 + 0.10 * (1 - ease_out(lt / 0.18))
    if tr in ('zoom', 'flare'):
        z *= 1 + 0.8 * (1 - ease_out(lt / 0.25))
    amp = sh.get('shake', 0)
    for it in impacts:
        if 0 <= t - it < 0.3:
            amp = max(amp, 22 * (1 - (t - it) / 0.3))
    sx, sy = amp * math.sin(t * 93), amp * math.cos(t * 71)
    slide = W * 0.9 * (1 - ease_out(lt / 0.14)) if tr == 'whip' and lt < 0.14 else 0.0
    z *= 1 + abs(rot) * 0.035
    hw, hh = W / (2 * z), H / (2 * z)
    fx = min(max(fx, hw), W - hw)
    fy = min(max(fy, hh), H - hh)
    cv.translate(W / 2 + sx + slide, H / 2 + sy)
    cv.rotate(rot)
    cv.scale(z, z)
    cv.translate(-fx, -fy)
    return lt


def overlays(cv, sh, t, W, H):
    lt = t - sh['a']
    tr = sh['transition']
    if tr == 'whip' and lt < 0.14:
        m = 1 - lt / 0.14
        for j in range(14):
            y = (j * 151 + int(t * 997)) % H
            cv.drawRect(skia.Rect(0, y, W, y + 6 + j % 3 * 4), K.P(0xFFFFFFFF, a=0.12 * m))
    if tr == 'flash' and lt < 0.12:
        cv.drawRect(skia.Rect(0, 0, W, H), K.P(0xFFFFFFFF, a=0.85 * (1 - lt / 0.12)))
    if tr == 'zoom' and lt < 0.12:
        cv.drawRect(skia.Rect(0, 0, W, H), K.P(0xFFFFFFFF, a=0.3 * (1 - lt / 0.12)))
    if tr == 'flare' and lt < 0.45:
        # signature flare-gate: orange burst iris-out
        k = lt / 0.45
        r = (W + H) * ease_out(k)
        pa = skia.Paint(AntiAlias=True, Color=0xFFFFB000)
        pa.setAlphaf(max(0, 1 - k) * 0.95)
        cv.drawCircle(W / 2, H * 0.45, max(1, (W + H) * 0.6 - r * 0.6), pa)
        ring = K.P(0xFFFF7A1A, 40 * (1 - k) + 2)
        ring.setAlphaf(1 - k)
        cv.drawCircle(W / 2, H * 0.45, r * 0.7, ring)


def captions(cv, words, t, W, H, fmt):
    cur = [i for i, w in enumerate(words) if w['start'] - 0.02 <= t]
    if not cur:
        return
    i = cur[-1]
    if t > words[i]['end'] + 0.6:
        return
    numeric = lambda w: any(ch.isdigit() for ch in w)
    g0 = i - (i % 2)
    group = [words[g0]] + ([words[g0 + 1]] if g0 + 1 < len(words) and not numeric(words[g0]['w']) and not numeric(words[g0 + 1]['w']) else [])
    if numeric(words[i]['w']):
        group = [words[i]]
    size = (160 if numeric(words[i]['w']) else 104) if fmt == 'short' else (120 if numeric(words[i]['w']) else 78)
    cy = H * (0.70 if fmt == 'short' else 0.86)
    f = skia.Font(TF, size)
    txt = [g['w'].upper().strip(',') for g in group]
    widths = [f.measureText(s) for s in txt]
    gap = size * 0.28
    total = sum(widths) + gap * (len(txt) - 1)
    x = W / 2 - total / 2
    for g, s, w in zip(group, txt, widths):
        age = t - g['start']
        pop = 1 + 0.25 * (1 - ease_out(age / 0.12)) if age >= 0 else 1
        active = g['start'] - 0.02 <= t
        col = 0xFFFFB000 if (active and g is words[i]) or numeric(g['w']) else 0xFFFFFFFF
        cv.save()
        cv.translate(x + w / 2, cy)
        cv.scale(pop, pop)
        blob = skia.TextBlob(s, f)
        cv.drawTextBlob(blob, -w / 2, size * 0.35, K.P(0xFF000000, size * 0.2))
        cv.drawTextBlob(blob, -w / 2, size * 0.35, K.P(col if active else 0x99FFFFFF))
        cv.restore()
        x += w + gap


def hud(cv, text, age, W, H, fmt):
    if not text:
        return
    k = ease_out(age / 0.2)
    f = skia.Font(TF, 64 if fmt == 'short' else 48)
    w = f.measureText(text)
    x, y = (W - w - 70, 250) if fmt == 'short' else (W - w - 60, 90)
    cv.save()
    cv.translate(x + w / 2, y)
    cv.scale(1.6 - 0.6 * k, 1.6 - 0.6 * k)
    cv.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 - 24, -58, w + 48, 82), 16, 16, K.P(0xCC0B1020))
    cv.drawTextBlob(skia.TextBlob(text, f), -w / 2, 0, K.P(0xFFFFB000))
    cv.restore()


def progress(cv, t, total, W, H):
    cv.drawRect(skia.Rect(0, H - 12, W, H), K.P(0x55000000))
    cv.drawRect(skia.Rect(0, H - 12, W * t / total, H), K.P(0xFFFFB000))


def render(ep_dir, out_path, only=None, fmt=None, clean=False):
    build = os.path.join(ep_dir, 'build')
    ep = json.load(open(os.path.join(ep_dir, 'episode.json')))
    fmt = fmt or ep.get('format', 'short')
    W, H = FORMATS[fmt]
    tl = json.load(open(os.path.join(build, 'timeline.json')))
    board = json.load(open(os.path.join(ep_dir, 'storyboard.json')))
    scenes = load_scenes(ep_dir)
    shots, words, impacts, cues, win, moods = edl(tl, board)
    missing = sorted({sh['kind'] for sh in shots} - set(scenes.SHOTS))
    if missing:
        raise SystemExit(f'storyboard uses shots not defined in scenes.py: {missing}')
    json.dump({'shots': [{k: sh.get(k) for k in ('n', 'kind', 'segment', 'a', 'b', 'transition', 'action', 'camera')} for sh in shots],
               'cues': cues, 'impacts': impacts, 'windows': win, 'moods': moods, 'duration': tl['duration'],
               'format': fmt, 'episode': ep['id']}, open(os.path.join(build, 'edl.json'), 'w'), indent=1)
    audio, sr = sf.read(os.path.join(build, 'voice.wav'))
    lips = LipSync(tl, audio.astype(np.float32), sr)
    ctx = Ctx(W, H, lips, words)
    total = tl['duration']
    n = int(total * FPS)
    frames = range(n) if only is None else [int(x * FPS) for x in only]
    ff = None
    if only is None:
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                               '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out_path],
                              stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    _CV['cv'] = cv
    last_hud, hud_t = None, 0.0
    stills = []
    for fi in frames:
        t = fi / FPS
        sh = shots[max(i for i, s in enumerate(shots) if s['a'] <= t or i == 0)]
        cv.clear(0xFF000000)
        base = cv.save()
        lt = camera(cv, sh, t, impacts, W, H)
        ctx.t, ctx.lt, ctx.d = t, lt, sh['b'] - sh['a']
        ctx.k = max(0.0, min(1.0, lt / ctx.d))
        ctx.prm, ctx.sh = sh.get('prm', {}), sh
        scenes.SHOTS[sh['kind']](cv, ctx)
        cv.restoreToCount(base)
        assert cv.getSaveCount() == base, 'canvas state leaked'
        if clean:
            stills.append((t, surf.makeImageSnapshot()))
            continue
        overlays(cv, sh, t, W, H)
        h = sh.get('hud')
        if h != last_hud:
            last_hud, hud_t = h, t
        hud(cv, h, t - hud_t, W, H, fmt)
        captions(cv, words, t, W, H, fmt)
        if fmt == 'short':
            progress(cv, t, total, W, H)
        img = surf.makeImageSnapshot()
        if ff:
            ff.stdin.write(img.toarray().tobytes())
        else:
            stills.append((t, img))
        if ff and fi % 300 == 0:
            print(f'frame {fi}/{n}', flush=True)
    if ff:
        ff.stdin.close()
        ff.wait()
    return stills, shots


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2])
