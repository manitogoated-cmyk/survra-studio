"""Sound design for Kesta episodes: synth SFX library (engine2/audio2) + a mood-driven score whose key,
tempo and progression are seeded per episode, so every story gets its own music."""
import json, os, subprocess, sys, zlib
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine2'))
import audio2 as A  # noqa: E402

SR = A.SR
# 2026-11-15 quality upgrade: the old score was a drum loop (kick, clap, hi-hats, distorted bass) under every story,
# which made a survival documentary sound like a ringtone and left no quiet anywhere (loudness range 1.9 LU).
# Now: a restrained cinematic bed. Slow-attack pads, a low heartbeat pulse only for tense/action beats, sparse plucks for
# sad/wonder beats, near-silence under the hook so the first image and line land, and real dynamics between sections.
MOODS = {  # pad level, pulse (heartbeat) level, pluck density, minor?
    'hook': (0.25, 0.0, 0, True), 'tense': (0.7, 0.55, 0, True), 'action': (0.8, 0.8, 2, True),
    'calm': (0.55, 0.0, 1, False), 'wonder': (0.7, 0.0, 2, False), 'sad': (0.6, 0.0, 1, True),
    'triumph': (0.9, 0.35, 2, False), 'end': (0.5, 0.0, 1, False),
}
MAJ, MIN = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]


def _pad_voice(f, tt, rng):
    """Warm pad note: detuned partials with a soft high roll-off (no bare sine 'ringtone' tone)."""
    out = np.zeros(len(tt))
    for det in (-0.004, 0.0, 0.0035):
        ph = rng.uniform(0, 2 * np.pi)
        for h, g in ((1, 1.0), (2, 0.32), (3, 0.12), (4, 0.05)):
            out += g * np.sin(2 * np.pi * f * (1 + det) * h * tt + ph * h)
    return out / 4.5


def _pluck(f, d=1.6):
    t = A.T(d)
    x = sum(g * np.sin(2 * np.pi * f * h * t) for h, g in ((1, 1.0), (2, 0.4), (3, 0.18), (5, 0.06)))
    return x * np.exp(-t * 3.2) * np.minimum(1, t / 0.004)


def score(N, win, moods, seed):
    rng = np.random.RandomState(seed)
    bpm = int(rng.choice([66, 72, 76, 80, 84])); spb = 60 / bpm          # slower: pulse, not dance tempo
    root = 55.0 * 2 ** (rng.randint(0, 7) / 12)                            # A1..E2
    prog_min = [[0, 5, 3, 6], [0, 3, 4, 0], [0, 6, 5, 4], [0, 2, 5, 4]][rng.randint(4)]
    prog_maj = [[0, 4, 5, 3], [0, 3, 4, 4], [0, 5, 3, 4], [0, 4, 3, 4]][rng.randint(4)]
    mus = np.zeros(N)
    t_all = np.arange(N) / SR
    heart = (lambda tt: A.tone(52 + 18 * np.exp(-tt * 40), tt) * np.exp(-tt * 14))(A.T(0.4))
    for name, (a, b) in win.items():
        if b <= a:
            continue
        pad_g, pulse_g, plucks, minor = MOODS.get(moods.get(name, 'calm'), MOODS['calm'])
        sc = MIN if minor else MAJ
        prog = prog_min if minor else prog_maj
        i0, i1 = int(a * SR), min(N, int(b * SR))
        tt = t_all[i0:i1] - a
        bar = spb * 4
        pad = np.zeros(len(tt))
        nb = int(np.ceil((b - a) / bar)) + 1
        for bi in range(nb):
            deg = prog[bi % 4]
            chord = [root * 4 * 2 ** (sc[(deg + j) % 7] / 12 + (deg + j) // 7) for j in (0, 2, 4)]
            # each chord swells in over 0.7 s and overlaps the next: no hard switch at the bar line
            c0, c1 = bi * bar - 0.35, (bi + 1) * bar + 0.35
            m = (tt >= c0) & (tt < c1)
            if not m.any():
                continue
            x = tt[m] - c0
            envl = np.minimum(1, x / 0.7) * np.minimum(1, (c1 - c0 - x) / 0.7)
            pad[m] += sum(_pad_voice(f, tt[m], rng) for f in chord) / 3 * envl
            pad[m] += 0.35 * np.sin(2 * np.pi * chord[0] / 2 * tt[m]) * envl        # soft sub root
        fade = np.minimum(1, tt / 0.5) * np.minimum(1, (b - a - tt) / 0.4 + 1e-3)
        mus[i0:i1] += pad * fade * 0.11 * pad_g
        if pulse_g:
            for bi in range(int(np.ceil(a / spb)), int(b / spb) + 1):
                bt = bi * spb
                if bt >= b:
                    break
                A.place(mus, bt, heart, 0.5 * pulse_g)
                A.place(mus, bt + 0.22, heart, 0.28 * pulse_g)                  # lub-dub
        if plucks:
            step = bar / (2 * plucks)
            k = 0
            while a + k * step < b - 0.3:
                deg = prog[int(k * step / bar) % 4]
                f = root * 8 * 2 ** (sc[(deg + [0, 2, 4, 2][k % 4]) % 7] / 12)
                A.place(mus, a + k * step, _pluck(f), 0.09)
                k += 1
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
    # storyboard shot flag "hush": true pulls the music out for that shot: silence before the payoff is the strongest
    # sound cue there is. Effects and voice stay.
    hush = np.ones(N)
    for sh in E['shots']:
        if sh.get('hush'):
            hush[max(0, int((sh['a'] - 0.1) * SR)):min(N, int(sh['b'] * SR))] = 0.06
    mus = mus * A.sm(hush, 0.2 * SR)
    voice, vsr = sf.read(os.path.join(build_dir, 'voice.wav'))
    v = np.interp(np.arange(N) / SR, np.arange(len(voice)) / vsr, voice)
    # per-mood narration level: quiet for sad/calm, forward for action, so the film breathes instead of sitting flat
    VG = {'hook': 0.0, 'tense': -1.5, 'action': 1.5, 'calm': -3.0, 'wonder': -2.0, 'sad': -4.5, 'triumph': 1.0, 'end': -2.0}
    g = np.ones(N)
    for name, (a, b) in E['windows'].items():
        i0, i1 = int(a * SR), min(N, int(b * SR))
        g[i0:i1] = 10 ** (VG.get(E.get('moods', {}).get(name, 'calm'), 0.0) / 20)
    v = v * A.sm(g, 0.25 * SR)
    vel = A.sm(np.abs(v), 0.15 * SR); duck = 1 - 0.8 * np.clip(vel / (vel.max() * 0.25 + 1e-9), 0, 1)
    bed = mus * 0.9 * duck + fx * 0.7 * (0.55 + 0.45 * duck)      # effects duck less than music: they are the action
    mix = v / (np.abs(v).max() + 1e-9) + bed * 0.4
    mix /= np.abs(mix).max() + 1e-9; mix *= 0.9
    raw = out_wav.replace('.wav', '_raw.wav'); sf.write(raw, np.stack([mix, mix], 1).astype(np.float32), SR)
    sf.write(os.path.join(build_dir, 'stem_voice.wav'), (v / (np.abs(v).max() + 1e-9)).astype(np.float32), SR)
    sf.write(os.path.join(build_dir, 'stem_bed.wav'), (bed * 0.45).astype(np.float32), SR)
    # two-pass loudnorm in linear mode keeps the dynamics (one-pass dynamic mode squashed the range to about 2 LU)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    ln = ('loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}'
          ':measured_thresh={input_thresh}:offset={target_offset}').format(**m)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', ln + ',alimiter=limit=0.84:level=disabled', '-ar', str(SR), out_wav], check=True)
    print('audio ok', len(E['cues']), 'cues')

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
