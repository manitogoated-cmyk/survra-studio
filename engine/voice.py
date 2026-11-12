"""Narration: Kokoro-82M (Apache-2.0) via kokoro-onnx, one clip per segment, plus word timings."""
import json, sys, os, re, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

MODELS = os.path.join(os.path.dirname(__file__), '..', 'models')

TOKEN = re.compile(r"\{([^|}]+)\|([^}]+)\}")

def split_display(text):
    """'{438|four hundred thirty-eight} days' -> spoken text + [(display_word, n_spoken_words)]"""
    spoken = TOKEN.sub(lambda m: m.group(2), text)
    units = []; pos = 0
    for m in TOKEN.finditer(text):
        units += [(w, 1) for w in text[pos:m.start()].split()]
        disp = m.group(1); trail = ''
        after = text[m.end():]
        if after[:1] in '.,!?': trail = after[0]
        units.append((disp, len(m.group(2).split()))); pos = m.end()
    units += [(w, 1) for w in text[pos:].split()]
    # attach punctuation that directly followed a token to it
    out = []
    for w, n in units:
        if out and w in ('.', ',', '!', '?'): out[-1] = (out[-1][0] + w, out[-1][1])
        elif out and w[:1] in '.,!?' and len(w) > 1 and out[-1][1] > 1: out[-1] = (out[-1][0] + w[0], out[-1][1]); out.append((w[1:], 1))
        else: out.append((w, n))
    return spoken, out

def synth(script_path, out_dir):
    s = json.load(open(script_path))
    k = Kokoro(os.path.join(MODELS, 'kokoro-v1.0.onnx'), os.path.join(MODELS, 'voices-v1.0.bin'))
    os.makedirs(out_dir, exist_ok=True)
    sr = 24000; gap = s.get('gap', 0.35); t = s.get('lead', 0.15)  # lead-in silence
    full = [np.zeros(int(sr * t), dtype=np.float32)]
    timeline = []
    for i, seg in enumerate(s['segments']):
        spoken, units = split_display(seg['text'])
        audio, sr = k.create(spoken, voice=s['voice'], speed=s.get('speed', 1.0), lang='en-us')
        audio = audio.astype(np.float32)
        # trim leading/trailing near-silence
        nz = np.where(np.abs(audio) > 0.01)[0]
        if len(nz): audio = audio[max(0, nz[0]-240): nz[-1]+240]
        dur = len(audio) / sr
        sw = spoken.split()
        # word timing ~ proportional to characters (+ small constant per word)
        w = np.array([len(x.strip('.,!?')) + 2.5 for x in sw]); w = w / w.sum() * dur
        starts = t + np.concatenate([[0], np.cumsum(w)[:-1]])
        words = []; i = 0
        for disp, n in units:
            words.append({'w': disp, 'start': float(starts[i]), 'end': float(starts[i + n - 1] + w[i + n - 1])}); i += n
        timeline.append({**seg, 'start': t, 'end': t + dur, 'words': words})
        full += [audio, np.zeros(int(sr * gap), dtype=np.float32)]
        t += dur + gap
    full.append(np.zeros(int(sr * s.get('tail', 1.2)), dtype=np.float32))
    voice = np.concatenate(full)
    sf.write(os.path.join(out_dir, 'voice.wav'), voice, sr)
    json.dump({'duration': len(voice) / sr, 'segments': timeline}, open(os.path.join(out_dir, 'timeline.json'), 'w'), indent=1)
    print('duration', round(len(voice) / sr, 2))

if __name__ == '__main__':
    synth(sys.argv[1], sys.argv[2])
