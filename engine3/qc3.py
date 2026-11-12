"""Quality gate for Kesta episodes. Wraps the pacing/motion/audio gate (engine2/qc.py) and adds:

  * Format rules: Shorts 9:16 <= 60 s with fast pacing; long-form 16:9 with long-form pacing.
  * Host rule: Kesta must physically appear and act in at least 35% of shots (not a corner talking head).
  * Originality rule: every shot's frame fingerprint is compared against ALL previous episodes;
    near-identical shots (correlation >= 0.93) fail, so no scene or footage is ever recycled.
    Shots flagged "brand": true in the storyboard (e.g. the sign-off) are exempt.
  * Captions + sources present.
Writes build/qc.json and qc/fingerprints/<episode>.npz. Exit 1 on FAIL.
"""
import glob
import inspect
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'engine2'))
sys.path.insert(0, ROOT)
import qc as BASE  # noqa: E402
from engine3.render3 import load_scenes  # noqa: E402

FP_DIR = os.path.join(ROOT, 'qc', 'fingerprints')
LONG_RULES = dict(first_shot_max=4.0, shot_max=7.0, shot_mean_max=3.8, kind_max_uses=4, static_window=3.5,
                  static_motion_min=0.8, repeat_pairs_max=3)


def fingerprints(video, edl, w, h):
    fr = BASE.frames_gray(video, w=w, h=h)
    out = []
    for s in edl['shots']:
        i = min(len(fr) - 1, int((s['a'] + 0.55 * (s['b'] - s['a'])) * 30))
        f = fr[i] - fr[i].mean()
        out.append(f / (np.linalg.norm(f) + 1e-6))
    return np.array(out)


def run(ep_dir, video):
    build = os.path.join(ep_dir, 'build')
    ep = json.load(open(os.path.join(ep_dir, 'episode.json')))
    board = json.load(open(os.path.join(ep_dir, 'storyboard.json')))
    E = json.load(open(os.path.join(build, 'edl.json')))
    fmt = E.get('format', 'short')
    saved = dict(BASE.RULES)
    if fmt == 'long':
        BASE.RULES.update(LONG_RULES)
        orig = BASE.frames_gray
        BASE.frames_gray = lambda v, w=96, h=54, fps=30: orig(v, w=96, h=54, fps=fps)
    try:
        rep = BASE.run(build, video)
    finally:
        BASE.RULES.clear()
        BASE.RULES.update(saved)
        if fmt == 'long':
            BASE.frames_gray = orig
    fails, notes = rep['fails'], rep['notes']
    # format
    if fmt == 'short' and E['duration'] > 60:
        fails.append(f"Short runs {E['duration']:.1f}s (max 60s for our Shorts format)")
    # host presence: Kesta must act in the scene
    scenes = load_scenes(ep_dir)
    host = [s for s in E['shots'] if 'c.kesta(' in inspect.getsource(scenes.SHOTS[s['kind']])]
    share = len(host) / len(E['shots'])
    notes.append(f'host: Kesta acts in {len(host)}/{len(E["shots"])} shots ({share:.0%})')
    if share < 0.35:
        fails.append(f'Host missing: Kesta appears in only {share:.0%} of shots (min 35%)')
    # originality vs every previous episode
    w, h = (54, 96) if fmt == 'short' else (96, 54)
    fp = fingerprints(video, E, w, h)
    brand = {sh['n'] for sh in board['shots'] if sh.get('brand')}
    os.makedirs(FP_DIR, exist_ok=True)
    worst = (0.0, None)
    for f in sorted(glob.glob(os.path.join(FP_DIR, '*.npz'))):
        other = os.path.basename(f)[:-4]
        if other == ep['id']:
            continue
        d = np.load(f)
        if d['fp'].shape[1:] != fp.shape[1:]:
            continue
        sim = fp.reshape(len(fp), -1) @ d['fp'].reshape(len(d['fp']), -1).T
        for i, s in enumerate(E['shots']):
            if s['n'] in brand:
                continue
            j = int(sim[i].argmax())
            if sim[i, j] > worst[0]:
                worst = (float(sim[i, j]), f"shot {s['n']} vs {other}")
            if sim[i, j] >= 0.93:
                fails.append(f"Recycled visuals: shot {s['n']} ({s['kind']}) matches {other} shot {j + 1} ({sim[i, j]:.2f})")
    notes.append(f'originality: closest match to any earlier episode {worst[0]:.2f} ({worst[1]})')
    # packaging basics
    if not ep.get('sources'):
        fails.append('No sources listed')
    if not E.get('shots'):
        fails.append('Empty edit')
    rep['pass'] = not fails
    rep['format'] = fmt
    json.dump(rep, open(os.path.join(build, 'qc.json'), 'w'), indent=1)
    if rep['pass']:
        np.savez_compressed(os.path.join(FP_DIR, ep['id'] + '.npz'), fp=fp)
    return rep


if __name__ == '__main__':
    r = run(sys.argv[1], sys.argv[2])
    print('QC', 'PASS' if r['pass'] else 'FAIL')
    for k in ('fails', 'warnings', 'notes'):
        for x in r[k]:
            print(f'  [{k[:-1]}] {x}')
    sys.exit(0 if r['pass'] else 1)
