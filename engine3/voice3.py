"""Kesta's voice: Kokoro-82M (Apache-2.0), timed export -> audio + phoneme + word timings.

script.json: {voice, speed, gap, lead, tail, segments:[{scene, text, ...}]}
Writes build/voice.wav and build/timeline.json:
  segments[i] = {..., start, end, words:[{w,start,end}], phonemes:[{p,start,end}]}
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.voice import split_display  # noqa: E402

MODELS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
TIMED = os.path.join(MODELS, 'kokoro-v1.0.timed.onnx')
STRESS = set('ˈˌːˑ')


def words_from_phonemes(ph, n_words):
    """Group phoneme timings into words on spaces/punctuation."""
    out, cur = [], []
    for p in ph:
        if p.phoneme.strip() == '' or p.phoneme in '.,!?;:—…':
            if cur:
                out.append((cur[0].start, cur[-1].end))
                cur = []
            continue
        cur.append(p)
    if cur:
        out.append((cur[0].start, cur[-1].end))
    return out


def synth(script_path, out_dir):
    s = json.load(open(script_path))
    k = Kokoro(TIMED, os.path.join(MODELS, 'voices-v1.0.bin'))
    assert k.has_timings, 'timed voice model missing (models/kokoro-v1.0.timed.onnx)'
    os.makedirs(out_dir, exist_ok=True)
    sr = 24000
    gap, t = s.get('gap', 0.3), s.get('lead', 0.15)
    full = [np.zeros(int(sr * t), dtype=np.float32)]
    timeline = []
    for seg in s['segments']:
        spoken, units = split_display(seg['text'])
        audio, sr, ph = k.create_timed(spoken, voice=s.get('voice', 'af_heart'), speed=s.get('speed', 1.0), lang='en-us')
        audio = audio.astype(np.float32)
        nz = np.where(np.abs(audio) > 0.01)[0]
        a0 = max(0, nz[0] - 240) if len(nz) else 0
        a1 = nz[-1] + 240 if len(nz) else len(audio)
        audio = audio[a0:a1]
        off = t - a0 / sr
        dur = len(audio) / sr
        phon = [dict(p=p.phoneme, start=round(p.start + off, 4), end=round(p.end + off, 4)) for p in ph
                if p.phoneme not in STRESS]
        spans = words_from_phonemes(ph, len(spoken.split()))
        sw = spoken.split()
        if len(spans) == len(sw):
            wt = [(a + off, b + off) for a, b in spans]
        else:  # fall back to proportional timing when espeak merges/splits words
            w = np.array([len(x.strip('.,!?')) + 2.5 for x in sw])
            w = w / w.sum() * dur
            st = t + np.concatenate([[0], np.cumsum(w)[:-1]])
            wt = [(float(st[i]), float(st[i] + w[i])) for i in range(len(sw))]
        words, i = [], 0
        for disp, n in units:
            j = min(i + n - 1, len(wt) - 1)
            words.append({'w': disp, 'start': round(wt[min(i, len(wt) - 1)][0], 4), 'end': round(wt[j][1], 4)})
            i += n
        timeline.append({**seg, 'start': round(t, 4), 'end': round(t + dur, 4), 'words': words, 'phonemes': phon})
        full += [audio, np.zeros(int(sr * gap), dtype=np.float32)]
        t += dur + gap
    full.append(np.zeros(int(sr * s.get('tail', 1.0)), dtype=np.float32))
    voice = np.concatenate(full)
    sf.write(os.path.join(out_dir, 'voice.wav'), voice, sr)
    json.dump({'duration': len(voice) / sr, 'segments': timeline}, open(os.path.join(out_dir, 'timeline.json'), 'w'), indent=1)
    print('duration', round(len(voice) / sr, 2))


class LipSync:
    """Viseme + mouth-open amount at any time, from the timeline."""

    def __init__(self, timeline, audio=None, sr=24000):
        from engine3.kesta import phoneme_viseme
        self.ev = []
        for seg in timeline['segments']:
            for p in seg.get('phonemes', []):
                self.ev.append((p['start'], p['end'], phoneme_viseme(p['p'])))
        self.ev.sort()
        self.starts = np.array([e[0] for e in self.ev]) if self.ev else np.zeros(0)
        self.env = None
        if audio is not None:
            hop = sr // 100
            n = len(audio) // hop
            rms = np.sqrt(np.mean(audio[:n * hop].reshape(n, hop) ** 2, axis=1))
            self.env = rms / (np.percentile(rms, 95) + 1e-6)

    def at(self, t):
        if not self.ev:
            return 'rest', 0.0
        i = int(np.searchsorted(self.starts, t, side='right')) - 1
        if i < 0:
            return 'rest', 0.0
        s, e, v = self.ev[i]
        if t > e + 0.06:
            return 'rest', 0.0
        k = 1.0
        if self.env is not None:
            j = min(len(self.env) - 1, int(t * 100))
            k = float(np.clip(0.45 + 0.8 * self.env[j], 0.4, 1.25))
        return v, k

    def speaking(self, t):
        v, _ = self.at(t)
        return v != 'rest'


if __name__ == '__main__':
    synth(sys.argv[1], sys.argv[2])
