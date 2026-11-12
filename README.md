# Survra Studio

Animated true-story Shorts for the Survra YouTube channel (@survra).

```
episodes/<id>/        episode.json + script.json + storyboard.json  (one folder per video)
engine/, engine2/     voice (Kokoro, Apache-2.0), storyboard renderer, sound design, QC gate
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
While the Google OAuth app is in "Testing", the refresh token lasts 7 days; the workflow opens
an issue when it expires.

## Run locally
```
pip install -r requirements.txt   # plus ffmpeg and the Inter font
python3 publish/publisher.py --dry-run          # render + QC every ready episode
python3 -m pytest -q tests
```
