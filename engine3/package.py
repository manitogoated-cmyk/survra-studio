"""Upload packaging built from the episode itself: captions (SRT), thumbnail / cover image, description, tags."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skia
from engine3 import render3 as R
from engine3.kesta import P


def srt(ep_dir):
    tl = json.load(open(os.path.join(ep_dir, 'build', 'timeline.json')))
    def ts(x):
        ms = int(round(x * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'
    cues = []
    for seg in tl['segments']:
        words = seg['words']; line = []
        for i, w in enumerate(words):
            line.append(w)
            text = ' '.join(x['w'] for x in line)
            nxt = words[i + 1]['w'] if i + 1 < len(words) else ''
            if w['w'][-1:] in '.!?' or i == len(words) - 1 or len(text) + len(nxt) > 40:
                cues.append([line[0]['start'], line[-1]['end'] + 0.15, text]); line = []
    out = []
    for n, (a, b, text) in enumerate(cues):
        if n + 1 < len(cues): b = min(b, cues[n + 1][0] - 0.01)
        out.append(f"{n + 1}\n{ts(a)} --> {ts(b)}\n{text}\n")
    path = os.path.join(ep_dir, 'build', 'captions.srt'); open(path, 'w').write('\n'.join(out)); return path


def thumbnail(ep_dir):
    """Long-form thumbnail: each episode composes its own in scenes.py as THUMB(cv, ctx) on a 1280x720 canvas
    (Kesta + the story's key image + a 2-4 word hook), so thumbnails are designed, not random frames."""
    scenes = R.load_scenes(ep_dir)
    if not hasattr(scenes, 'THUMB'):
        return None
    TW, TH = 1280, 720
    surf = skia.Surface(TW, TH); cv = surf.getCanvas(); R._CV['cv'] = cv
    class Still:  # no speech on a still
        def at(self, t): return 'rest', 0.0
    ctx = R.Ctx(TW, TH, Still(), []); ctx.t = ctx.lt = 0.6; ctx.d = 1.0; ctx.k = 0.6
    scenes.THUMB(cv, ctx)
    path = os.path.join(ep_dir, 'build', 'thumbnail.jpg')
    surf.makeImageSnapshot().save(path, skia.kJPEG, 90); return path


def description(ep):
    d = ep.get('description', '').strip()
    if ep.get('sources'): d += '\n\nSources:\n' + '\n'.join('- ' + s for s in ep['sources'])
    d += '\n\nHosted by Kesta. Original animation by Survra. Narration is a synthetic voice; the story is researched from the sources above.'
    if ep.get('hashtags'): d += '\n\n' + ' '.join(ep['hashtags'][:5])
    return d


if __name__ == '__main__':
    print(srt(sys.argv[1])); print(thumbnail(sys.argv[1]))
