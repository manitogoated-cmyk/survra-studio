# Survra Studio

Animated true-story Shorts for the Survra YouTube channel (@survra).

```
episodes/<id>/        episode.json + script.json + storyboard.json  (one folder per video)
character/           Kesta's character bible (the host: never changes)
engine3/             Kesta rig + lip sync, world toolkit, cast, renderer, score, QC (pacing, host, originality)
engine/, engine2/    first-generation engine (pilot Short) and shared sound library
publish/              YouTube uploader, publisher, config.json (pause/review switches), ledger.json
.github/workflows/    daily render -> QC -> upload job
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

## Run locally
```
pip install -r requirements.txt   # plus ffmpeg and the Inter font
./engine3/make_episode.sh episodes/<id>          # voice + animation + sound + QC for one episode
python3 publish/publisher.py status              # rebuild STATUS.md (production dashboard)
python3 -m pytest -q tests
```
