"""Sound design from the edit decision list: ~30 synthesized SFX on storyboard cues + a sectioned score
(hook hits, upbeat departure, storm intensity, driving survival, heartbeat-only loss, sparse loneliness,
riser and major-key lift at landfall). Voice is ducked-over, never buried; output -14 LUFS."""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
SR = 48000
rng = np.random.default_rng(21)
def T(d): return np.arange(int(d * SR)) / SR
def sm(x, n): n = max(1, int(n)); return np.convolve(x, np.ones(n) / n, 'same')
def hp(x, n): return x - sm(x, n)
def nz(d): return rng.standard_normal(int(d * SR))
def env(t, a, dcy): return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t * dcy)
def tone(f, t, ph=0): return np.sin(2 * np.pi * f * t + ph)
def sweep(f0, f1, d, curve=2):
    t = T(d); f = f0 + (f1 - f0) * (t / d) ** curve; return np.sin(2 * np.pi * np.cumsum(f) / SR), t

def S_boom():  t = T(1.2); return tone(38 + 50 * np.exp(-t * 7), t) * np.exp(-t * 3.2) + hp(nz(1.2), 10) * np.exp(-T(1.2) * 20) * 0.4
def S_impact(): return S_boom() * 0.8 + np.pad(S_hit(), (0, int(1.2 * SR) - len(S_hit())))
def S_hit():   t = T(0.5); return (tone(70 * np.exp(-t * 2), t) + 0.6 * hp(nz(0.5), 6)) * np.exp(-t * 12)
def S_whoosh(d=0.35): t = np.linspace(0, 1, int(d * SR)); return hp(sm(nz(d), 5), 50) * np.sin(np.pi * t) ** 2 * 1.6
def S_riser(d=1.0): s, t = sweep(200, 1400, d); return (hp(nz(d), 25) * 0.5 + s * 0.2) * (t / d) ** 2
def S_gasp():  t = T(0.35); return hp(sm(nz(0.35), 3), 30) * np.sin(np.pi * t / 0.35) * 0.5
def S_wave():  t = T(1.6); return sm(nz(1.6), 30) * 8 * np.sin(np.pi * np.minimum(1, t / 1.6)) ** 1.5
def S_crash(): t = T(1.4); return (sm(nz(1.4), 12) * 6 + hp(nz(1.4), 6) * 0.6) * env(t, 0.05, 2.5)
def S_splash(): t = T(0.6); return hp(nz(0.6), 4) * env(t, 0.005, 9) + sm(nz(0.6), 40) * 5 * env(t, 0.01, 6)
def S_gulls():
    out = np.zeros(int(1.4 * SR))
    for k, st in enumerate((0.0, 0.35, 0.8)):
        s, t = sweep(1800, 1100, 0.28, 1); seg = s * np.sin(np.pi * t / 0.28) * 0.35
        i = int(st * SR); out[i:i + len(seg)] += seg
    return out
S_caw = S_gulls
def S_flap(): t = T(0.5); return sm(nz(0.5), 20) * 6 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 14 * t))) * np.exp(-t * 4)
def S_cord(): s, t = sweep(300, 900, 0.25, 1); return (s * 0.3 + hp(nz(0.25), 8) * 0.4) * np.exp(-t * 6)
def S_engine_start():
    t = T(1.4); f = 32 + 18 * np.minimum(1, t / 0.4)
    eng = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + tone(f * 2, t) * 0.2
    return sm(eng, 6) * np.minimum(1, t / 0.05) * np.exp(-np.maximum(0, t - 0.9) * 4)
def S_sputter():
    t = T(1.0); out = np.zeros(len(t))
    for st in np.arange(0, 0.8, 0.11) + rng.uniform(0, 0.04, 8):
        i = int(st * SR); seg = hp(nz(0.06), 6) * np.exp(-T(0.06) * 50); out[i:i + len(seg)] += seg
    return out + sm(np.sign(np.sin(2 * np.pi * 28 * t)), 8) * 0.2 * np.exp(-t * 3)
def S_clunk(): t = T(0.4); return (tone(120, t) + tone(187, t) * 0.6) * np.exp(-t * 18) + hp(nz(0.4), 5) * np.exp(-t * 40) * 0.5
def S_tick():
    out = np.zeros(int(1.2 * SR))
    for k in range(8):
        i = int(k * 0.15 * SR); seg = tone(2200, T(0.02)) * np.exp(-T(0.02) * 200); out[i:i + len(seg)] += seg * 0.6
    return out
def S_thunder(): t = T(2.5); x = np.cumsum(nz(2.5)); x = hp(x, 2000); x /= np.abs(x).max(); return x * env(t, 0.03, 1.4) * 1.2 + S_hit()[:1] * 0
def S_rain(): t = T(1.5); return hp(nz(1.5), 3) * 0.12 * np.sin(np.pi * t / 1.5)
def S_grab(): return S_hit() * 0.6 + np.pad(S_splash()[:int(0.3 * SR)] * 0.5, (0, int(0.2 * SR)))
def S_bubbles():
    out = np.zeros(int(1.0 * SR))
    for k in range(9):
        i = int(rng.uniform(0, 0.85) * SR); s, t = sweep(300, 900, 0.07, 1); out[i:i + len(s)] += s * np.exp(-t * 30) * 0.4
    return out
def S_flip(): t = T(0.18); return hp(nz(0.18), 10) * np.sin(np.pi * t / 0.18) * 0.7
def S_heartbeat():
    out = np.zeros(int(1.2 * SR))
    for st in (0.0, 0.22):
        t = T(0.25); seg = tone(52, t) * np.exp(-t * 14); i = int(st * SR); out[i:i + len(seg)] += seg * 1.1
    return out
def S_low(): t = T(3.0); return (tone(55, t) + tone(82.4, t) * 0.5) * np.sin(np.pi * t / 3.0) * 0.35
def S_horn(): t = T(1.4); return (tone(110, t) + tone(220, t) * 0.4 + tone(330, t) * 0.2) * np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 1.0) * 8) * 0.5
def S_horn_far(): x = S_horn(); return sm(x, 30) * 0.5
def S_shout(): return S_hit() * 0.3
def S_scratch(): t = T(0.22); return hp(nz(0.22), 3) * (0.5 + 0.5 * np.sin(2 * np.pi * 40 * t)) * np.sin(np.pi * t / 0.22) * 0.6
def S_bloop(): s, t = sweep(500, 180, 0.2, 1); return s * np.exp(-t * 12) * 0.7
def S_swim(): t = T(0.4); return sm(nz(0.4), 15) * 5 * np.sin(np.pi * t / 0.4)
FX = {k[2:]: v for k, v in globals().items() if k.startswith('S_')}
FX['trans_whip'] = lambda: S_whoosh(0.3); FX['trans_cut'] = lambda: S_whoosh(0.15) * 0.4
FX['trans_zoom'] = lambda: S_riser(0.25) * 1.5; FX['trans_flash'] = lambda: S_hit() * 0.7
FX['impact_num'] = S_boom
GAIN = {'thunder': 1.2, 'boom': 1.0, 'impact_num': 1.0, 'crash': 1.0, 'rain': 0.8, 'low': 0.8, 'trans_cut': 0.5}

def place(buf, at, sig, g):
    i = int(at * SR)
    if i >= len(buf): return
    if i < 0: sig = sig[-i:]; i = 0
    L = min(len(sig), len(buf) - i); buf[i:i + L] += sig[:L] * g

def score(N, win):
    t = np.arange(N) / SR; mus = np.zeros(N)
    bpm = 128; spb = 60 / bpm
    def sec(name): return win.get(name, (0, 0))
    kick = (lambda: (lambda tt: tone(45 + 110 * np.exp(-tt * 30), tt) * np.exp(-tt * 9))(T(0.35)))()
    clap = hp(nz(0.2), 12) * np.exp(-T(0.2) * 22) * 0.6
    hat = hp(nz(0.05), 3) * np.exp(-T(0.05) * 90) * 0.3
    plans = {  # section: (kick, clap, hats per beat, bass roots, pad chord)
        'hook':   (1, 0, 0, [55], [110, 130.8, 164.8]),
        'depart': (1, 1, 2, [65.4, 98.0, 87.3, 98.0], [261.6, 329.6, 392.0]),
        'storm':  (1, 1, 4, [55, 55, 58.3, 55], [110, 130.8, 155.6]),
        'food':   (1, 1, 2, [55, 43.7, 65.4, 49], [220, 261.6, 329.6]),
        'loss':   (0, 0, 0, [41.2], [164.8, 196.0, 246.9]),
        'alone':  (0, 0, 1, [41.2, 43.7], [146.8, 174.6, 220]),
        'land':   (1, 1, 2, [65.4, 87.3, 98.0, 110], [261.6, 329.6, 392.0, 523.3]),
        'end':    (0, 0, 0, [65.4], [261.6, 329.6, 392.0]),
    }
    for name, (k, c, h, roots, chord) in plans.items():
        a, b = sec(name)
        if b <= a: continue
        # pad
        tt = t[int(a * SR):int(b * SR)] - a
        pad = sum(tone(f, tt) + 0.25 * tone(2 * f, tt) for f in chord) / len(chord)
        fade = np.minimum(1, tt / 0.15) * np.minimum(1, (b - a - tt) / 0.1 + 0.001)
        mus[int(a * SR):int(a * SR) + len(tt)] += pad * fade * (0.10 if name != 'loss' else 0.16)
        # drums + bass on the global grid
        bi0 = int(np.ceil(a / spb)); bi1 = int(b / spb)
        for bi in range(bi0, bi1 + 1):
            bt = bi * spb
            if bt >= b: break
            if name == 'land' and bt < a + 0.9: continue          # hold back, then drop
            if k: place(mus, bt, kick, 0.9)
            if c and bi % 2: place(mus, bt, clap, 0.5)
            for q in range(h): place(mus, bt + q * spb / h, hat, 0.6 if q else 0.35)
            if name in ('storm', 'hook') and bi % 2 == 0: place(mus, bt, tone(36, T(spb * 2)) * np.exp(-T(spb * 2) * 1.5), 0.5)
            r = roots[bi % len(roots)]; bt_t = T(spb)
            bass = np.tanh((tone(r, bt_t) + 0.5 * tone(2 * r, bt_t)) * (2.5 if name == 'storm' else 1.2)) * np.exp(-bt_t * 3)
            place(mus, bt, bass, 0.32)
    return mus

def build(build_dir, out_wav):
    E = json.load(open(os.path.join(build_dir, 'edl.json'))); D = E['duration']; N = int(D * SR)
    fx = np.zeros(N)
    for c in E['cues']:
        f = FX.get(c['sfx'])
        if f is None: print('missing sfx', c['sfx']); continue
        sig = f(); sig = sig / (np.abs(sig).max() + 1e-9)
        place(fx, c['t'] - (0.12 if c['sfx'] in ('trans_whip',) else 0), sig, 0.5 * GAIN.get(c['sfx'], 0.7))
    mus = score(N, E['windows'])
    voice, vsr = sf.read(os.path.join(build_dir, 'voice.wav'))
    v = np.interp(np.arange(N) / SR, np.arange(len(voice)) / vsr, voice)
    vel = sm(np.abs(v), 0.2 * SR); duck = 1 - 0.72 * np.clip(vel / (vel.max() * 0.3 + 1e-9), 0, 1)
    bed = (mus * 0.8 + fx * 0.75) * duck
    mix = v * 1.0 / (np.abs(v).max() + 1e-9) + bed * 0.45
    mix /= np.abs(mix).max() + 1e-9; mix *= 0.9
    raw = out_wav.replace('.wav', '_raw.wav'); sf.write(raw, np.stack([mix, mix], 1).astype(np.float32), SR)
    # stems for QC: voice-only and bed-only
    sf.write(os.path.join(build_dir, 'stem_voice.wav'), (v / (np.abs(v).max() + 1e-9)).astype(np.float32), SR)
    sf.write(os.path.join(build_dir, 'stem_bed.wav'), (bed * 0.45).astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-2.0:LRA=9,alimiter=limit=0.79:level=disabled', '-ar', str(SR), out_wav], check=True)
    print('audio ok', len(E['cues']), 'cues')

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
