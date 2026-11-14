"""Sound design for Kesta episodes: synth SFX library (engine2/audio2) + a mood-driven score whose key,
tempo and progression are seeded per episode, so every story gets its own music."""
import json, os, subprocess, sys, zlib
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine2'))
import audio2 as A  # noqa: E402

SR = A.SR
MOODS = {  # kick, clap, hats/beat, intensity, minor?
    'hook': (1, 0, 0, 0.9, True), 'tense': (1, 0, 2, 0.8, True), 'action': (1, 1, 4, 1.0, True),
    'calm': (0, 0, 1, 0.4, False), 'wonder': (0, 0, 1, 0.5, False), 'sad': (0, 0, 0, 0.35, True),
    'triumph': (1, 1, 2, 0.9, False), 'end': (0, 0, 0, 0.4, False),
}
MAJ, MIN = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]

def score(N, win, moods, seed):
    rng = np.random.RandomState(seed)
    bpm = int(rng.choice([96, 104, 112, 120, 126, 132])); spb = 60 / bpm
    root = 41.2 * 2 ** (rng.randint(0, 7) / 12)            # E1..A#1
    prog_min = [[0, 5, 3, 6], [0, 3, 4, 0], [0, 6, 5, 4], [0, 2, 5, 4]][rng.randint(4)]
    prog_maj = [[0, 4, 5, 3], [0, 3, 4, 4], [0, 5, 3, 4], [0, 4, 3, 4]][rng.randint(4)]
    t = np.arange(N) / SR; mus = np.zeros(N)
    kick = (lambda tt: A.tone(45 + 110 * np.exp(-tt * 30), tt) * np.exp(-tt * 9))(A.T(0.35))
    clap = A.hp(A.nz(0.2), 12) * np.exp(-A.T(0.2) * 22) * 0.6
    hat = A.hp(A.nz(0.05), 3) * np.exp(-A.T(0.05) * 90) * 0.3
    for name, (a, b) in win.items():
        if b <= a: continue
        k, c, h, inten, minor = MOODS.get(moods.get(name, 'calm'), MOODS['calm'])
        sc = MIN if minor else MAJ; prog = prog_min if minor else prog_maj
        tt = t[int(a * SR):int(b * SR)] - a
        bar = spb * 4
        pad = np.zeros(len(tt))
        for bi in range(int(np.ceil((b - a) / bar)) + 1):
            deg = prog[bi % 4]
            chord = [root * 4 * 2 ** (sc[(deg + j) % 7] / 12 + (deg + j) // 7) for j in (0, 2, 4)]
            m = (tt >= bi * bar) & (tt < (bi + 1) * bar)
            pad[m] = sum(A.tone(f, tt[m]) + 0.2 * A.tone(2 * f, tt[m]) for f in chord) / 3
        fade = np.minimum(1, tt / 0.15) * np.minimum(1, (b - a - tt) / 0.1 + 0.001)
        mus[int(a * SR):int(a * SR) + len(tt)] += pad * fade * (0.09 + 0.05 * (moods.get(name) == 'sad'))
        for bi in range(int(np.ceil(a / spb)), int(b / spb) + 1):
            bt = bi * spb
            if bt >= b: break
            if k: A.place(mus, bt, kick, 0.85 * inten)
            if c and bi % 2: A.place(mus, bt, clap, 0.5 * inten)
            for q in range(h): A.place(mus, bt + q * spb / h, hat, 0.6 if q else 0.35)
            deg = prog[(bi // 4) % 4]
            r = root * 2 ** (sc[deg % 7] / 12); bt_t = A.T(spb)
            bass = np.tanh((A.tone(r, bt_t) + 0.5 * A.tone(2 * r, bt_t)) * (1 + 1.5 * inten)) * np.exp(-bt_t * 3)
            if inten > 0.3: A.place(mus, bt, bass, 0.3 * inten)
    return mus

def mixs(*xs):
    n = max(len(x) for x in xs); out = np.zeros(n)
    for x in xs: out[:len(x)] += x
    return out

EXTRA = {
    'jungle': lambda: A.sm(A.nz(3.0), 6) * 4 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * A.T(3.0))),
    'birdcall': lambda: (lambda tt: A.tone(2400 + 600 * np.sin(2 * np.pi * 9 * tt), tt) * np.exp(-tt * 6) * 0.5)(A.T(0.5)),
    'stream': lambda: A.sm(A.nz(2.5), 3) * 3,
    'wind': lambda: A.sm(A.nz(2.0), 40) * 9 * np.sin(np.pi * A.T(2.0) / 2.0),
    'flare': lambda: mixs(A.S_whoosh(0.3) * 0.6, A.S_boom() * 0.8),
    'creak': lambda: (lambda tt: A.tone(180 + 60 * np.sin(2 * np.pi * 3 * tt), tt) * np.sin(np.pi * tt / 0.6) * 0.4)(A.T(0.6)),
    'buzz': lambda: (lambda tt: np.sign(np.sin(2 * np.pi * 210 * tt)) * 0.15 * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * tt)))(A.T(1.0)),
    'trans_flare': lambda: mixs(A.S_whoosh(0.3) * 0.5, A.S_hit() * 0.6),
    'pop': lambda: (lambda s_t: s_t[0] * np.exp(-s_t[1] * 25) * 0.6)(A.sweep(900, 300, 0.12, 1)),
}

def build(build_dir, out_wav):
    E = json.load(open(os.path.join(build_dir, 'edl.json'))); D = E['duration']; N = int(D * SR)
    fx = np.zeros(N)
    for c in E['cues']:
        f = EXTRA.get(c['sfx']) or A.FX.get(c['sfx'])
        if f is None: print('missing sfx', c['sfx']); continue
        sig = f(); sig = sig / (np.abs(sig).max() + 1e-9)
        A.place(fx, c['t'], sig, 0.5 * A.GAIN.get(c['sfx'], 0.7))
    mus = score(N, E['windows'], E.get('moods', {}), zlib.crc32(E.get('episode', 'x').encode()) & 0xFFFF)
    voice, vsr = sf.read(os.path.join(build_dir, 'voice.wav'))
    v = np.interp(np.arange(N) / SR, np.arange(len(voice)) / vsr, voice)
    vel = A.sm(np.abs(v), 0.2 * SR); duck = 1 - 0.72 * np.clip(vel / (vel.max() * 0.3 + 1e-9), 0, 1)
    bed = (mus * 0.8 + fx * 0.75) * duck
    mix = v / (np.abs(v).max() + 1e-9) + bed * 0.45
    mix /= np.abs(mix).max() + 1e-9; mix *= 0.9
    raw = out_wav.replace('.wav', '_raw.wav'); sf.write(raw, np.stack([mix, mix], 1).astype(np.float32), SR)
    sf.write(os.path.join(build_dir, 'stem_voice.wav'), (v / (np.abs(v).max() + 1e-9)).astype(np.float32), SR)
    sf.write(os.path.join(build_dir, 'stem_bed.wav'), (bed * 0.45).astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-2.0:LRA=9,alimiter=limit=0.75:level=disabled', '-ar', str(SR), out_wav], check=True)
    print('audio ok', len(E['cues']), 'cues')

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
