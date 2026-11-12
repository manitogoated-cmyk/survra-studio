"""Original sound bed generated in code (no licensing): ocean wash, storm rain/thunder, a slow minor pad
that lifts to major at the landfall. Mixed under the narration with ducking, normalized to -14 LUFS."""
import json, sys, os, subprocess, numpy as np, soundfile as sf
SR = 48000
rng = np.random.default_rng(5)

def lowpass(x, a):  # one-pole
    y = np.empty_like(x); acc = 0.0
    for i in range(0, len(x), 4096):
        seg = x[i:i+4096]; out = np.empty_like(seg)
        for j, v in enumerate(seg): acc += a * (v - acc); out[j] = acc
        y[i:i+4096] = out
    return y

def env(n, a, r):
    e = np.ones(n); ai = int(a*SR); ri = int(r*SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] = np.linspace(1, 0, ri)
    return e

def build(build_dir, out_wav):
    tl = json.load(open(os.path.join(build_dir, 'timeline.json'))); D = tl['duration']; N = int(D * SR)
    t = np.arange(N) / SR
    segs = tl['segments']
    def window(scene):
        for i, s in enumerate(segs):
            if s['scene'] == scene:
                a = s['start'] - 0.2; b = segs[i+1]['start'] - 0.2 if i + 1 < len(segs) else D
                return a, b
    # ocean wash: brown-ish noise with slow swells
    noise = rng.standard_normal(N).astype(np.float32)
    brown = np.cumsum(noise); brown -= np.convolve(brown, np.ones(4801)/4801, 'same'); brown /= np.abs(brown).max()
    swell = 0.55 + 0.45 * np.sin(2*np.pi*t/6.5) * np.sin(2*np.pi*t/3.1 + 1)
    ocean = brown * swell * 0.22
    # storm: rain hiss + thunder
    a, b = window('storm'); m = ((t > a) & (t < b)).astype(float); m = np.convolve(m, np.ones(SR)/SR, 'same')
    hiss = rng.standard_normal(N) * 0.10 * m
    thunder = np.zeros(N)
    for tt in (a + 1.2, a + 3.4):
        i0 = int(tt * SR); L = int(2.8 * SR)
        if i0 + L < N:
            th = np.cumsum(rng.standard_normal(L)); th -= np.convolve(th, np.ones(2401)/2401, 'same')
            th = th / np.abs(th).max() * np.exp(-np.linspace(0, 4, L)) * 0.9
            thunder[i0:i0+L] += th
    ocean = ocean * (1 + 1.5 * m)
    # pad: A minor -> C major lift at landfall
    la, lb = window('land')
    lift = np.clip((t - la) / 2.0, 0, 1)
    def tone(f, amp): return amp * (np.sin(2*np.pi*f*t) + 0.3*np.sin(2*np.pi*2*f*t + 0.5))
    minor = tone(110, .05) + tone(130.81, .035) + tone(164.81, .035) + tone(220, .02)
    major = tone(130.81, .05) + tone(164.81, .035) + tone(196.0, .035) + tone(261.63, .02)
    trem = 0.8 + 0.2*np.sin(2*np.pi*t*0.25)
    pad = (minor * (1 - lift) + major * lift) * trem
    # pulse during storm (tension)
    pulse = np.sin(2*np.pi*55*t) * (0.5 + 0.5*np.sign(np.sin(2*np.pi*t*2.0))) * 0.05 * m
    bed = ocean + hiss + thunder + pad + pulse
    bed *= env(N, 1.0, 2.5)
    # duck under narration
    voice, vsr = sf.read(os.path.join(build_dir, 'voice.wav'))
    v = np.interp(np.arange(N) / SR, np.arange(len(voice)) / vsr, voice)[:N]
    vel = np.convolve(np.abs(v), np.ones(int(0.3*SR))/(0.3*SR), 'same'); duck = 1 - 0.55 * np.clip(vel / (vel.max() * 0.25 + 1e-9), 0, 1)
    mix = v * 1.0 + bed * duck * 0.9
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
    raw = out_wav.replace('.wav', '_raw.wav'); sf.write(raw, np.stack([mix, mix], 1).astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR), out_wav], check=True)
    print('audio ok', round(D, 2))

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
