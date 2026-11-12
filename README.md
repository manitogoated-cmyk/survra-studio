# Survra Studio

3D animated true-story videos for the Survra YouTube channel (@survra), hosted by Rook, a sceptical crow detective.
Everything is made with free, open tools: Blender as a Python module (Cycles on CPU), Kokoro voice, skia, ffmpeg.

```
episodes/<id>/        episode.json, script.json, storyboard.json, world3d.py (3D sets + shots), scenes.py (flat inserts/overlays)
character/            ROOK.md, the host bible (the host never changes; every story gets a new world)
engine4/              3D kit: jointed rig, heads, hand props, lip sync, frame renderer, contact sheet, channel art
engine3/              voice + phoneme timings, compositor (captions, HUD, transitions), score and sound, QC gate
engine/, engine2/     first-generation engine and the shared sound library
publish/              YouTube uploader, publisher, ops (banner, watermark, analytics), config.json, ledger.json
plan/                 slate.json (case slate), learnings.json (from the weekly analytics report)
.github/workflows/    publish.yml (voice -> 6 parallel 3D frame jobs -> composite + QC -> upload), ops.yml (analytics, branding)
AUTHORING.md          how a new episode is made; STATUS.md production dashboard; ANALYTICS.md weekly numbers
```

## Safety switches (publish/config.json)
- `"paused": true` stops all uploads.
- `"review_mode": true` uploads everything as **private** with no publish date, for owner review.
  Set it to `false` only after the owner approves a test batch; then episodes with
  `"status": "approved"` are scheduled into the next free slot.
- A video is never uploaded unless the QC gate passes. `publish/ledger.json` blocks re-uploads.

## Secrets
Stored only as GitHub encrypted secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
Never commit them. Locally they live in the untracked `secrets/` folder.
The Google OAuth app is "In production" (unverified, owner-only), so the refresh token does not
expire weekly. If it is ever revoked, the workflow opens an issue asking for re-authorization.

## Run locally (Python 3.13)
```
pip install -r requirements.txt bpy==5.3.0        # plus ffmpeg and the Inter font
mkdir -p models && cd models
curl -fsSL -o kokoro-v1.0.timed.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
curl -fsSL -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ..
python3 engine3/voice3.py episodes/<id>/script.json episodes/<id>/build
python3 engine4/kit3d.py episodes/<id> sheet && python3 engine4/sheet3d.py episodes/<id> /tmp/sheet.png   # quick look
./engine3/make_episode.sh episodes/<id>          # voice + 3D frames + composite + sound + QC for one episode
python3 publish/publisher.py status              # rebuild STATUS.md (production dashboard)
python3 -m pytest -q tests
```
