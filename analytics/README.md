# Survra performance database

The channel's permanent record of what was made and how viewers responded. Maintained under the YouTube Performance & Evolution skill.

| File | What it is | Updated |
|---|---|---|
| `video-performance.csv` | One row per video per snapshot: live counters, Analytics API metrics, retention checkpoints, traffic mix, creative tags read from each episode's source files | Daily, automatically (`audit.yml` on main) |
| `channel-history.csv` | One row per snapshot: subscribers, views, Shorts vs long-form split | Daily, automatically |
| `channel-snapshot.md` | Current state of the channel and what the data can and can't say | Each audit |
| `winners-and-underperformers.md` | Shorts and long-form ranked separately, with comparison limits | Weekly |
| `creative-patterns.md` | Why videos may have worked: measured, correlation, hypothesis | Weekly |
| `experiment-log.md` | Hypothesis, control, change, metric, result, decision | Every batch |
| `next-batch-creative-brief.md` | The next 10 videos, built from the findings | Every batch |
| `weekly-growth-report.md` | Dated weekly entries, newest first | Weekly |
| `data-gaps.md` | What can't be seen yet and how to close it | Each audit |

## Rules
- Append-only. Never edit or delete old CSV rows; a blank cell means the API had not returned that value yet.
- Shorts and long-form are never ranked together.
- Compare videos at similar ages (use `age_h`), never on lifetime totals alone.
- Label every finding as measured, correlation or hypothesis.
- Raw API JSON (which includes comment text) is never committed: this repository is public.

## Production cycle
1. The daily `audit.yml` run appends a snapshot.
2. Before authoring a new batch, read `next-batch-creative-brief.md` and `experiment-log.md`.
3. Weekly: update the markdown reports from the CSVs, record experiment results, write the next brief.
