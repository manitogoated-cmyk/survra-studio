# Survra launch, ramp-up and monetization plan

No outcome here is guaranteed: nobody can promise views, virality or income. This is the plan and the numbers it is measured against.

## Launch sequence
1. **Owner review (once).** Case 001 in 3D is uploaded as a private video. When the owner approves the look, set `"review_mode": false` in `publish/config.json` and mark approved episodes `"status": "approved"`. From then on the workflow schedules each approved episode into the next free slot.
2. **Weeks 1-2: one Short a day.** The nightly authoring run writes one new case; the publish workflow renders it on six parallel free GitHub runners (about 15 minutes), runs the QC gate and uploads. Goal: 10 public cases with no QC failures and a stable look.
3. **Weeks 3-4: two to three Shorts a day** if the weekly analytics report shows Shorts at 70% average viewed or better. Raise the nightly run's quota, not the quality bar.
4. **Month 2: long-form.** One 6 to 8 minute "full case file" a week, built from the best-performing Short (same story, deeper, new shots), then up to three a week. Long-form uses the same 3D pipeline in 16:9; a full episode is about 7,000 frames, which the six frame jobs render in roughly 1.5 hours.
5. **Six a day (3 long + 3 Shorts)** is the owner's target and stays a target: it needs three authoring runs a night and a larger frame-job matrix. Only step up when the previous step has held its quality for two weeks.

## Capacity (free tiers only)
- Rendering: GitHub Actions on a public repository, no minutes charge. One Short uses 6 frame jobs of 8 to 15 minutes; 20 jobs can run at once, so three Shorts fit in one run.
- YouTube Data API: uploads have their own limit of 100 a day, far above this plan; the other calls (thumbnail, playlist, status) are a small part of the default daily quota.
- Authoring: one scheduled Claude session per night (the "Survra daily case" scheduled task).

## Monetization milestones (YouTube Partner Program)
- Fan funding tier: 500 subscribers, 3 public uploads in 90 days, and 3,000 public watch hours in 12 months or 3 million public Shorts views in 90 days.
- Ads and Premium revenue: 1,000 subscribers and 4,000 public watch hours in 12 months or 10 million public Shorts views in 90 days. Several industry sources report that for new applicants from 1 February 2027 this becomes 8,000 hours or 20 million Shorts views; check YouTube's own page before applying.
- Shorts watch time does not count toward the watch-hour path, which is why long-form starts in month 2.
- Sources: https://support.google.com/youtube/answer/72851 , https://www.newscaststudio.com/2026/08/10/youtube-partner-program-monetization-changes-2027/
- Later options once there is an audience: sponsorships, a "Rook's Case Files" membership, merchandise of Rook (after a name/trademark check by a lawyer).

## Promotion (no bots, no bought engagement, no spam)
- Every Short ends on Rook's sign-off and belongs to the playlist "Rook's Case Files (Shorts)"; long-form links back to its Short.
- Pin one comment per video asking which case Rook should take next; the best answers feed `plan/slate.json`.
- Repost each Short natively to TikTok and Instagram Reels by hand or with an official scheduler once the owner connects those accounts. Nothing is auto-posted to accounts that have not been authorized.
- Community posts on the channel when a long-form case is released.

## Weekly loop
The "Survra channel ops" workflow writes `ANALYTICS.md` and `plan/learnings.json` every Monday from real API numbers. The nightly authoring run reads both before choosing and writing the next case.

## Still needs the owner
- Watch the private 3D video and say whether it can go public.
- Profile picture: upload `brand/rook_profile_800.jpg` in YouTube Studio (the API cannot change it).
- Captions as a separate track need one re-authorization with an extra permission; captions are burned into the picture meanwhile.
- Retention numbers need the YouTube Analytics API switched on in the Google Cloud project.
