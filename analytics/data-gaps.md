# Data gaps

Updated 2026-11-15. What this audit could not see, why, and how to close each gap.

| Gap | Why | How to close it | Owner action? |
|---|---|---|---|
| Analytics for 13–15 Nov (retention, engaged views, traffic, subscribers per video) for 9 of 11 Shorts | Normal 2–3 day Analytics API processing delay | The daily audit job (once merged) picks it up automatically; first full read about 18 Nov | No |
| Impressions and impressions CTR | The API rejected `videoThumbnailImpressions` / `videoThumbnailImpressionsClickRate` for this channel ("query not supported") | Export from Studio: Analytics → Advanced mode → Content: Videos → metrics Impressions + Impressions click-through rate → last 28 days → export CSV, then drop it into `analytics/studio-exports/` | Yes, weekly (about 2 min) |
| Shorts "viewed vs swiped away" | Studio-only metric | Studio → each Short → Analytics → Engagement tab → "Viewed vs swiped away" screenshot, or the engaged-views ratio from the API as a substitute (already in the CSV) | Optional |
| Retention for long-form | No long-form views yet | Wait for thumbnails + 7 days | Phone-verify first |
| Custom thumbnails on all 12 long-form videos | YouTube 403: channel not verified | youtube.com/verify (phone). The daily `repair` job then retries the thumbnails | **Yes, now** |
| What the rendered videos actually look and sound like | This audit read scripts and storyboards only; no video was watched or listened to | Next cycle: download the episode artifacts from the publish runs and review the contact sheets and first 3 seconds of each Short; score sound per the studio skill's QC gate | No |
| Comments to learn from | 1 comment on the whole channel | E4 (question endings) | No |
| Returning viewers | API returned only "unsubscribed"; too few subscribers (5) | Will appear with more subscribers | No |
| Revenue / RPM | Not in the Partner Program | n/a until eligible | No |
| Age-matched cohorts (24 h / 7 d / 28 d) | Channel is 3.5 days old | `video-performance.csv` snapshots by age; possible from about 22 Nov (7 d) and 10 Dec (28 d) | No |
| Duplicate private upload `z52b0vJIFXc` (old 2D version of Okene, 1 view) | Left from the 2D era | Leave as is or delete in Studio; not counted in any comparison | Optional |
