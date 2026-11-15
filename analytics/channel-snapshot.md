# Channel snapshot

**Snapshot:** 2026-11-15 17:34 UTC · **Source:** YouTube Data API v3 (live counters) + YouTube Analytics API v2, through the channel's own OAuth token (`yt-analytics.readonly`), pulled by `publish/audit.py`. Nothing here is estimated.

**Channel:** Survra / Rook's Case Files (`UC3Muz7ZHeeYDYTRt9riw6CA`), created 2026-11-12.

## Read this first: how much data there is
- The channel is **3.5 days old**. "Last 90 days" and "lifetime" are the same window (12–15 Nov 2026).
- **The Analytics API has finished data only for 12 Nov** (normal 2–3 day processing delay). Live view, like and comment counters are current; watch time, retention, traffic, audience and subscriber-per-video figures cover only the first two public Shorts (Okene, Suitcase).
- 17 public videos (11 Shorts, 6 long-form), 13 private or scheduled. One Short (Poonlim) and one long-form (Lemons) were under 3 hours old at the snapshot and are excluded from comparisons.
- Every conclusion below is a **hypothesis from a small sample** unless marked as measured.

## Totals (live, 15 Nov)
| Metric | Value |
|---|---|
| Subscribers | 5 |
| Channel views | 3,753 |
| Public videos | 17 (11 Shorts, 6 long-form) |
| Sum of per-video counters, Shorts | 4,937 |
| Sum of per-video counters, long-form | 40 |
| Comments, all videos | 1 |

The per-video counters add up to more than the channel total because YouTube refreshes them on different schedules. Treat per-video counters as current and the channel total as lagging.

## Analytics API (finished data: 12 Nov only)
| Metric | Shorts | Long-form |
|---|---|---|
| Views | 1,446 | 0 |
| Minutes watched | 385 | 0 |
| Avg view duration | 28 s | – |
| Avg % viewed | 57.9% | – |
| Likes / comments / shares | 26 / 0 / 0 | – |
| Subscribers gained / lost | 1 / 1 | – |

**Traffic (12 Nov):** Shorts feed 1,387 (96%), channel page 26, YouTube search 18, other YouTube pages 13, playlists 2.
**Devices:** mobile 887 (61%), tablet 256 (18%), TV 192 (13%), desktop 105 (7%).
**Countries:** US 1,120 (77%; 59.8% avg viewed), Philippines 101, UK 34 (70.5% avg viewed), India 24 (29.2% avg viewed).
**Audience:** 70% male / 30% female. Ages 25–34: 30%, 35–44: 23%, 13–17: 23%, 45–54: 12%, 18–24: 12%.
**Subscribed status:** 100% of views from non-subscribers.

## Not available yet
Impressions and impressions CTR (the API rejected that query for this channel), Shorts "viewed vs swiped away" (Studio only), retention for every video after 12 Nov, revenue (not monetized). See `data-gaps.md`.
