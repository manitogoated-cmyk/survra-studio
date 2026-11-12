# How to make a Survra episode (for the daily authoring run)

Survra is a 3D animated channel. Everything is free and open: Blender as a Python module (`bpy`) rendered with Cycles on CPU, Kokoro voice, ffmpeg. No paid tools, no generative video services.

Read first: `character/ROOK.md` (host bible, never change his design) and `episodes/r001-okene/` (reference episode: copy its structure, never its sets or shots).

## Rules
- Follow the owner's animation-studio skill if it is available (its "2D only" line was replaced by the owner's later instruction: 3D, free tools only). Story gate: score 10 criteria out of 10 each, produce only ideas at 75/100 or more with curiosity, story potential and payoff at 6 or more. Write the scores and source notes into `episode.json`. Never ship a boring story: if the cold open would not stop a stranger scrolling, pick another story.
- True stories only, verified with web sources listed in `episode.json` (`sources`, `source_notes` for conflicts). No invented facts or quotes.
- Rook is a sceptical crow detective. Each video is a case: cold open on the most unbelievable moment, then his doubt ("No chance. Let's go look."), the story with escalation and one reversal, and "Case closed." Jokes stop for the tragic beats.
- The character stays, the whole world changes. Every story gets brand-new sets in its own `world3d.py`. Never import or copy another episode's sets. The originality gate fails shots that match earlier episodes.
- Do not change `publish/config.json` (`review_mode`, `paused`). Videos now go public, so review the contact sheet at least three times before approving an episode. Never commit secrets, mp4, wav, png, jpg or models.

## Files in `episodes/<id>/` (id like `r002-short-name`)
- `episode.json`: id, format `short` (9:16, 40 to 50 s) or `long` (16:9), status `approved` (public posting was approved by the owner on 12 Nov 2026: the workflow schedules it into the next slot after the QC gate passes) or `ready` (uploads as private for the owner) when you are not confident in it, title (Shorts end with #shorts), description, tags, hashtags, playlist, sources, story_score.
- `script.json`: voice `am_fenrir`, speed 1.12, gap 0.14, lead 0.1, tail 0.9, segments `{scene, mood, text}`. Moods: hook, tense, action, calm, wonder, sad, triumph, end. Numbers as `{2013|twenty thirteen}`.
- `storyboard.json`: shots `{n, segment, weight, kind, action, camera, cam, shake, transition (cut|whip|zoom|flash), sfx:[[name,frac]], hud, prm}`. `cam` is only used by flat 2D inserts; 3D shots move the Blender camera. Mark the sign-off shot `"brand": true`.
- `world3d.py`: the story in 3D. `build()` returns the scene dict `S`; `reset(S)` parks everything; `SHOTS3D = {kind: f(S, k, t, lt)}` poses the cast and camera for one frame (`k` 0..1 progress, `t` global time, `lt` time in shot); `finish(S, t)` applies faces and lip sync; `HOST = {kinds where Rook is on screen}`; optional `STILLS = {name: f}` for photos on the case board.
- `scenes.py`: flat inserts `SHOTS = {kind: f(cv, c)}` (case board, graphics) and `OVER = {kind: f(cv, c)}` overlays drawn on top of a 3D shot (rain, stamps, numbers) on a 1080x1920 canvas (1920x1080 for long).

## 3D toolkit (`engine4/kit3d.py`)
- `add(kind, colour, loc, rot, scale, parent, rough, emit, alpha, **primitive_args)` adds a flat-shaded low-poly primitive. `empty()`, `light()`.
- `Rig(colours, head_fn, coat)`: jointed humanoid about 3 units tall, feet at the root, facing -Y. `rig.place(loc, yaw, pitch, roll)`, `rig.apply(pose)`.
- Poses: `P('stand'|'point'|'hat'|'cross'|'shrug'|'up'|'reach'|'hips'|'sit'|'swim', **overrides)`, `blend(a, b, k)`, `walk(t)`. Arm = (swing forward, spread, elbow bend, forearm twist inward); leg = (hip forward, knee bend); head = (nod, turn).
- Heads: `rook_head` (hat, brows, eyes, lower beak for lip sync, diving helmet), `human_head(skin, hair)`, `diver_head` (lamp). `Hand(skin, sleeve)` is a close-up hand prop with `grip(0..1)`.
- Build each set inside `group(name, fn)` at its own origin so only one set renders per shot (`show(S, name)` returns a function that converts set-local to world coordinates).
- Look: faceted low poly, strong coloured light, dark noir palette with Survra orange (#FF7A1A) accents. Rook: coat #566178, feathers #2F2B4D, amber eyes, hat with orange band.

## Build and check
```
pip install -r requirements.txt bpy==5.3.0      # Python 3.13; needs ffmpeg and the Inter font
python3 engine3/voice3.py episodes/<id>/script.json episodes/<id>/build       # needs models/ (see README)
python3 engine4/kit3d.py episodes/<id> sheet && python3 engine4/sheet3d.py episodes/<id> /tmp/sheet.png
#   ^ one low-res still per shot in about a minute: LOOK at it and fix staging before any full render
./engine3/make_episode.sh episodes/<id>      # full render (resumable; about 8 s per frame on 2 cores) + QC gate
```
On GitHub the same episode is rendered by six parallel jobs, so a full local render is optional: the contact sheet plus a few full frames is the minimum review. After a cloud run, a small review copy is on the branch `renders-<id>`.

QC gate (must pass, never loosen it): first shot 1.2 s or less with an impact sound in the first second, no shot over 2.0 s, mean 1.6 s or less, no shot type more than twice or twice in a row, no static 1.5 s stretch, Rook on screen and acting in at least 35% of shots, loudness and voice clarity, no recycled visuals.

## Lessons from Case 001 (read before staging)
- Objects parented to a set root use set-local coordinates; un-parented ones use world coordinates.
- Park unused props far below the set, including long parts such as cables.
- A camera inside a visible light cone whites out the frame. Put the camera beside the beam.
- A character lit only by his own lamp is black. Give every shot a fill light.
- Faces belong in the top 60% of the frame; captions sit at 70% of the height.
- Glass reads badly at low samples. Use rings or a frame to suggest it.
- Dark shots still need movement (bubbles, light sweeps, shaking) or they fail the motion check.
- Delete `build/3d/<shot>_*.jpg` to re-render only the shots you changed.

When QC passes (or the contact sheet is reviewed and the cloud render will do the QC): set status `approved`, commit only source files and push to `main`. The publish workflow renders, checks, uploads and schedules the video for public release in the next free slot (12:15, 18:30 or 21:00 Eastern for Shorts).

## What to make next
`plan/slate.json` is the case slate: take the first case whose status is `idea`, fact-check it with at least two web sources, re-score it against the story gate, and skip it (status `rejected` with the reason) if the facts or the score do not hold. Read `plan/learnings.json` and `ANALYTICS.md` first when they exist and apply what the numbers say. Set the case's status to `authored` when its episode is pushed.
