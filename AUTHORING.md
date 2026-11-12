# How to make a Survra episode (for the daily authoring run)

Read first: `character/ROOK.md` (host bible, never change his design) and `episodes/r001-okene/` (reference episode: copy its structure, never its scenes).

## Rules
- Follow the owner's "2D Viral Animation Studio" skill if it is available. Story gate: score 10 criteria out of 10 each, produce only ideas at 75/100 or more with curiosity, story potential and payoff at 6 or more. Write the scores and source notes into `episode.json`.
- True stories only, verified with web sources listed in `episode.json` (`sources`, `source_notes` for conflicts). No invented facts or quotes.
- Rook is a sceptical crow detective. Each video is a case: cold open on the most unbelievable moment, then his doubt ("No chance. Let's go look."), the story with escalation and one reversal, and "Case closed." Jokes stop for the tragic beats.
- Every story gets a brand-new world. Never import or copy another episode's `scenes.py`. The originality gate fails shots that match earlier episodes.
- Nothing is public: `publish/config.json` keeps `review_mode: true`. Do not change it, and do not change `paused`.

## Files in `episodes/<id>/` (id like `r002-short-name`)
- `episode.json`: id, format "short", status "ready" only after QC PASS, title (ends with #shorts), description, tags, hashtags, playlist "Rook's Case Files (Shorts)", sources, story_score.
- `script.json`: voice "am_fenrir", speed 1.12, gap 0.14, lead 0.1, tail 0.9, segments `{scene, mood, text}`. Moods: hook, tense, action, calm, wonder, sad, triumph, end. Numbers as `{2013|twenty thirteen}`. Target 40 to 50 seconds.
- `storyboard.json`: shots `{n, segment, weight, kind, action, camera, cam:[[zoom,fx,fy,rot],[...]], shake, transition (cut|whip|zoom|flash), sfx:[[name,frac]], hud, prm}`. Mark the sign-off shot `"brand": true`.
- `scenes.py`: `SHOTS = {kind: f(cv, c)}` drawn on a 1080x1920 canvas. `c.t` time, `c.lt` time in shot, `c.k` 0..1 progress, `c.prm`.

## Toolkit
- Host: `c.host(x, y, height_px, pose, view, facing, expr)`. Poses from `engine3/host.py`: `Hm.pose('stand'|'point'|'run'|'shrug'|'think'|'cross'|'hype', **overrides)`, `Hm.walk(t)`, `Hm.keys(t, [(time, pose), ...])`. Views: front, tq, side, back. Expressions: happy, laugh, awe, curious, smirk, deadpan, shocked, scared, sad, angry, thinking, wink. Lip sync and talk gestures are automatic.
- Cast in the same style: `Hm.person(cv, x, y, h, pose, COLORS, Hm.human_head(skin, skin2, hair, expr), view, facing, rot)`.
- World helpers: `engine3/world.py` (gradients, glow, rain, clouds, ridges, particles, text_card). Drawing helpers: `concepts/chars.py` (P, fs, hose, oval, poly, smooth).
- Sound names: see `engine2/audio2.py` (FX) and `engine3/audio3.py` (EXTRA).

## Build and check
```
pip install -r requirements.txt            # needs ffmpeg and the Inter font
mkdir -p models && cd models
curl -fsSL -o kokoro-v1.0.timed.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
curl -fsSL -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd .. && python3 engine3/stills3.py episodes/<id> /tmp/sheet.png   # contact sheet: LOOK at it and fix compositions
./engine3/make_episode.sh episodes/<id>                              # must end with QC PASS
```
QC gate (must pass, never loosen it): first shot 1.2 s or less with an impact sound in the first second, no shot over 2.0 s, mean 1.6 s or less, no shot type more than twice or twice in a row, no static 1.5 s stretch, Rook acting in at least 35% of shots, loudness and voice clarity, no recycled visuals.

Common mistakes: every `cv.save()` needs a `cv.restore()`; dark scenes need movement (particles, light sweeps) or they fail the motion check; keep faces and captions clear of the bottom 30% caption band.

When QC passes: set status "ready", commit only source files (no mp4, wav, png, models) and push to `main`. The publish workflow renders it again on GitHub and uploads it as a private video.
