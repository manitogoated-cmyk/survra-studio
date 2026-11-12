"""Driving sound bed for fast Shorts, all synthesized (no licensing): 128 BPM kick/clap/hats + bass,
whooshes on every edit, booms on number slams, a riser into the landfall, ocean texture underneath.
Ducked under the narration and normalized to -14 LUFS."""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

SR = 48000
rng = np.random.default_rng(9)

def smooth(x, n):
    n = max(1, int(n)); k = np.ones(n) / n
    return np.convolve(x, k, 'same')

def add(buf, at, sig, gain=1.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(sig) <= 0: return
    j0 = max(0, -i); i = max(0, i); L = min(len(sig) - j0, len(buf) - i)
    buf[i:i + L] += sig[j0:j0 + L] * gain

def kick():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 45 + 110 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)

def clap():
    n = int(0.22 * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n); x = x - smooth(x, 12)
    return x * np.exp(-tt * 22) * 0.6

def hat():
    n = int(0.05 * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n); x = x - smooth(x, 4)
    return x * np.exp(-tt * 90) * 0.25

def whoosh(dur=0.32):
    n = int(dur * SR); tt = np.linspace(0, 1, n)
    x = rng.standard_normal(n); x = smooth(x, 6) - smooth(x, 60)
    return x * np.sin(np.pi * tt) ** 2 * 1.4

def boom():
    n = int(0.9 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 4)
    nz = rng.standard_normal(n) * np.exp(-tt * 18) * 0.5
    return s + smooth(nz, 8)

def riser(dur):
    n = int(dur * SR); tt = np.linspace(0, 1, n)
    x = rng.standard_normal(n); x = x - smooth(x, 30)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * tt ** 2) / SR) * 0.15
    return (x * 0.5 + tone) * tt ** 2

def build(build_dir, out_wav):
    tl = json.load(open(os.path.join(build_dir, 'timeline.json'))); cuts = json.load(open(os.path.join(build_dir, 'cuts.json')))
    D = tl['duration']; N = int(D * SR); t = np.arange(N) / SR
    beats = {sc: (a, b) for a, b, sc in cuts['beats']}
    drums = np.zeros(N); bass = np.zeros(N); fx = np.zeros(N)
    bpm = 128; spb = 60 / bpm
    land_a = beats['land'][0]; storm_a, storm_b = beats['storm']
    k, c, h = kick(), clap(), hat()
    nbeats = int(D / spb) + 1
    roots = [110.0, 87.31, 130.81, 98.0]  # A F C G
    for bi in range(nbeats):
        bt = bi * spb
        if land_a - 1.0 < bt < land_a + 0.2: continue          # drop out before the landfall hit
        add(drums, bt, k, 0.9)
        if bi % 2 == 1: add(drums, bt, c, 0.55)
        add(drums, bt + spb / 2, h, 0.7); add(drums, bt, h, 0.4)
        if storm_a < bt < storm_b: add(drums, bt + spb / 4, h, 0.5); add(drums, bt + 3 * spb / 4, h, 0.5)
        root = roots[(bi // 4) % 4]
        n = int(spb * SR); tt = np.arange(n) / SR
        note = (np.sin(2 * np.pi * root * tt) + 0.35 * np.sin(2 * np.pi * root * 2 * tt)) * np.exp(-tt * 3.5)
        add(bass, bt, note, 0.45)
    for cu in cuts['cuts']:
        add(fx, cu['t'] - 0.16, whoosh(0.32 if cu['type'] == 'whip' else 0.18), 0.55 if cu['type'] == 'whip' else 0.3)
    for it in cuts['impacts']: add(fx, it - 0.02, boom(), 0.9)
    add(fx, land_a - 1.0, riser(1.0), 0.7)
    add(fx, land_a, boom(), 1.0)
    # ocean texture
    noise = rng.standard_normal(N); ocean = smooth(noise, 400) * 6 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 5))
    storm_m = smooth(((t > storm_a) & (t < storm_b)).astype(float), SR * 0.3)
    ocean = ocean * (1 + 2.5 * storm_m) + (noise - smooth(noise, 8)) * 0.12 * storm_m
    music = (drums + bass) * 0.5
    voice, vsr = sf.read(os.path.join(build_dir, 'voice.wav'))
    v = np.interp(t, np.arange(len(voice)) / vsr, voice)
    vel = smooth(np.abs(v), 0.25 * SR); duck = 1 - 0.5 * np.clip(vel / (vel.max() * 0.3 + 1e-9), 0, 1)
    mix = v * 1.15 + (music * 0.55 + ocean * 0.25) * duck + fx * 0.45
    mix /= np.abs(mix).max() + 1e-9; mix *= 0.9
    raw = out_wav.replace('.wav', '_raw.wav'); sf.write(raw, np.stack([mix, mix], 1).astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-ar', str(SR), out_wav], check=True)
    print('audio ok')

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
