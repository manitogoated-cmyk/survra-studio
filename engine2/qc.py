"""Pacing & quality gate. A video must PASS before it can be scheduled for upload.

Checks (thresholds in RULES, tuned for animated Shorts):
  Edit:   first shot length, hook impact in the first second, max/mean shot length, repeated or back-to-back
          shot types, every shot has sound design.
  Motion: decodes the actual video; rejects any 1.5 s window with no cut and almost no on-screen motion,
          a static first second, and near-identical shots reused.
  Audio:  loudness -14 LUFS +/-1.5, true peak, voice at least 6 dB above music/SFX while speaking, no dead air.
Usage: python3 qc.py <build_dir> <video.mp4>   -> prints report, writes build/qc.json, exit 1 on FAIL
"""
import json, os, subprocess, sys, re
import numpy as np, soundfile as sf

RULES = dict(first_shot_max=1.2, hook_impact_by=1.0, shot_max=2.0, shot_mean_max=1.6, kind_max_uses=2,
             static_window=1.5, static_motion_min=1.2, cut_diff=28.0, first_second_motion_min=2.0,
             repeat_corr=0.97, repeat_pairs_max=1, lufs=-14.0, lufs_tol=1.5, tp_max=-1.0,
             voice_over_bed_db=6.0, dead_air_s=0.8, dead_air_db=-45.0)

def frames_gray(video, w=54, h=96, fps=30):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', video, '-vf', f'scale={w}:{h},format=gray', '-r', str(fps),
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)

def loudness(path):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    summ = err[err.rfind('Summary:'):]
    I = float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)); tp = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1))
    return I, tp

def run(build, video):
    R = RULES; E = json.load(open(os.path.join(build, 'edl.json'))); shots = E['shots']; fails, warns, notes = [], [], []
    # ---- edit rules ----
    lens = [s['b'] - s['a'] for s in shots]
    if lens[0] > R['first_shot_max']: fails.append(f"Weak opening: first shot lasts {lens[0]:.2f}s (max {R['first_shot_max']}s)")
    early = [c for c in E['cues'] if c['t'] <= R['hook_impact_by'] and c['sfx'] in ('impact', 'boom', 'hit', 'impact_num', 'trans_flash')]
    if not early: fails.append('Weak opening: no impact/hit in the first second')
    for s, L in zip(shots, lens):
        if L > R['shot_max']: fails.append(f"Shot {s['n']} ({s['kind']}) holds {L:.2f}s (max {R['shot_max']}s)")
    if np.mean(lens) > R['shot_mean_max']: fails.append(f"Pacing: average shot {np.mean(lens):.2f}s (max {R['shot_mean_max']}s)")
    kinds = [s['kind'] for s in shots]
    for a, b in zip(kinds, kinds[1:]):
        if a == b: fails.append(f'Repetitive: same shot type twice in a row ({a})')
    for k in set(kinds):
        if kinds.count(k) > R['kind_max_uses']: fails.append(f'Repetitive: shot type {k} used {kinds.count(k)} times')
    cued = {round(c['t'], 3) for c in E['cues'] if not c['sfx'].startswith('trans_') and c['sfx'] != 'impact_num'}
    for s in shots:
        if not any(s['a'] - 0.01 <= t <= s['b'] for t in cued): warns.append(f"Shot {s['n']} ({s['kind']}) has no action sound")
    notes.append(f'{len(shots)} shots, mean {np.mean(lens):.2f}s, longest {max(lens):.2f}s')
    # ---- motion ----
    F = frames_gray(video); fps = 30
    diff = np.concatenate([[0], np.abs(F[1:] - F[:-1]).mean(axis=(1, 2))])
    cuts = diff > R['cut_diff']
    win = int(R['static_window'] * fps); bad = []
    for i in range(0, len(diff) - win, 5):
        seg = diff[i:i + win]
        if not cuts[i:i + win].any() and seg.mean() < R['static_motion_min']: bad.append(i / fps)
    if bad:
        # merge adjacent windows into ranges
        rng = [[bad[0], bad[0] + R['static_window']]]
        for b in bad[1:]:
            if b <= rng[-1][1]: rng[-1][1] = b + R['static_window']
            else: rng.append([b, b + R['static_window']])
        for a, b in rng: fails.append(f'Static/boring stretch {a:.1f}s-{b:.1f}s: no cut and little movement')
    if diff[1:fps].mean() < R['first_second_motion_min'] and not cuts[1:fps].any():
        fails.append('Weak opening: first second has too little movement')
    mids = [F[min(len(F) - 1, int((s['a'] + s['b']) / 2 * fps))].ravel() for s in shots]
    mids = [(m - m.mean()) / (m.std() + 1e-6) for m in mids]
    pairs = [(shots[i]['n'], shots[j]['n']) for i in range(len(mids)) for j in range(i + 2, len(mids))
             if float(np.dot(mids[i], mids[j]) / len(mids[i])) > R['repeat_corr']]
    if len(pairs) > R['repeat_pairs_max']: fails.append(f'Repetitive visuals: near-identical shots {pairs[:5]}')
    elif pairs: warns.append(f'Similar shots {pairs}')
    notes.append(f'motion: mean frame change {diff.mean():.2f}, {int(cuts.sum())} hard cuts detected')
    # ---- audio ----
    I, tp = loudness(video)
    if abs(I - R['lufs']) > R['lufs_tol']: fails.append(f'Loudness {I:.1f} LUFS (target {R["lufs"]})')
    if tp > R['tp_max']: fails.append(f'True peak {tp:.1f} dBFS (max {R["tp_max"]})')
    v, sr = sf.read(os.path.join(build, 'stem_voice.wav')); b, _ = sf.read(os.path.join(build, 'stem_bed.wav'))
    n = int(0.5 * sr); ratios = []
    for i in range(0, min(len(v), len(b)) - n, n):
        vr = np.sqrt(np.mean(v[i:i + n] ** 2)); br = np.sqrt(np.mean(b[i:i + n] ** 2))
        if vr > 0.05: ratios.append(20 * np.log10(vr / (br + 1e-9)))
    vob = float(np.median(ratios)) if ratios else 0
    if vob < R['voice_over_bed_db']: fails.append(f'Voice not clear: only {vob:.1f} dB above music/SFX (min {R["voice_over_bed_db"]})')
    a, asr = sf.read(video.replace('.mp4', '.wav')) if os.path.exists(video.replace('.mp4', '.wav')) else (None, None)
    mix, msr = sf.read(os.path.join(build, 'mix.wav')); mono = mix.mean(axis=1) if mix.ndim > 1 else mix
    m = int(R['dead_air_s'] * msr); content_end = len(mono) - int(1.0 * msr)
    for i in range(0, content_end - m, m // 2):
        if 20 * np.log10(np.sqrt(np.mean(mono[i:i + m] ** 2)) + 1e-9) < R['dead_air_db']: fails.append(f'Dead air at {i / msr:.1f}s'); break
    notes.append(f'audio: {I:.1f} LUFS, peak {tp:.1f} dBFS, voice {vob:.1f} dB over bed')
    rep = {'pass': not fails, 'fails': fails, 'warnings': warns, 'notes': notes, 'rules': R}
    json.dump(rep, open(os.path.join(build, 'qc.json'), 'w'), indent=1)
    return rep

if __name__ == '__main__':
    r = run(sys.argv[1], sys.argv[2])
    print('QC', 'PASS' if r['pass'] else 'FAIL')
    for k in ('fails', 'warnings', 'notes'):
        for x in r[k]: print(f'  [{k[:-1]}] {x}')
    sys.exit(0 if r['pass'] else 1)
