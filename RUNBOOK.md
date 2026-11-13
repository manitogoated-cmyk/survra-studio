# Runbook for the scheduled authoring runs

Each scheduled run starts a fresh session with no memory. Its prompt says which run it is (`short` or `long`) and points here. Nobody is watching: never ask questions; take the most reasonable choice and say which one you took in your final message.

Daily target set by the owner: 4 Shorts and 3 long-form videos. The target never overrides quality: a run that cannot produce a good episode reports why and ships nothing.

## Setup (both runs)
1. Get the repository `manitogoated-cmyk/survra-studio` (add it to the session with push access if it is not there, clone it, work on `main`, `git pull --rebase` before every push).
2. Read `AUTHORING.md`, `character/ROOK.md`, `plan/slate.json`, `STATUS.md`, and `ANALYTICS.md` plus `plan/learnings.json` when they exist.
3. Tools: Python 3.13, `pip install -r requirements.txt bpy==5.3.0` (add `--break-system-packages` if pip asks), ffmpeg, the Inter font, and the Kokoro voice model files in `models/` as the README shows.

## Short run
1. **Queue check.** If four or more episodes with format `short` and status `ready` or `approved` are not yet in `publish/ledger.json`, author nothing and report.
2. **Claim a case.** Take the first case in `plan/slate.json` with status `idea`, set it to `in progress`, commit and push that one change right away so a parallel run does not take the same case. If fewer than 8 ideas are left afterwards, research 10 new true-story candidates (same quality bar, two sources each) and append them with estimated scores.
3. **Fact-check and score.** At least two independent reputable sources. Re-score against the story gate in `AUTHORING.md`. If the facts do not hold or the score is under 75/100, mark the case `rejected` with the reason and claim the next one.
4. **Write the episode** in `episodes/<id>/` as `AUTHORING.md` describes (format `short`, 40 to 50 seconds, 30 to 40 shots, brand-new 3D sets, Rook on screen and acting in at least 35% of shots, playlist "Rook's Case Files (Shorts)", `"synthetic": false`). Study `episodes/r001-okene` for structure only.
5. **Review.** Voice step, then `python3 engine4/kit3d.py episodes/<id> sheet` and `python3 engine4/sheet3d.py episodes/<id> /tmp/sheet.png`. Look at the sheet and fix staging; at least three rounds, because the video goes public without another human look. Check that every 3D kind in the storyboard exists in `world3d.SHOTS3D` and that `HOST` lists every kind where Rook is on screen.
6. **Ship.** Status `approved` (or `ready`, which uploads as private, if you are not confident it is good enough to be public; say why). Slate entry `authored`. Commit only source files and push. The publish workflow runs every three hours: it renders, runs the QC gate and schedules the video into the next free slot.
7. **Report:** the case and why, its score, sources, what you checked, public or private, and anything the owner must know.

## Long run
See "Long-form" in `AUTHORING.md`. In short: a long-form video is the full case file of a case that already has a Short. Copy that Short's episode to `episodes/<id>-long/`, keep its 3D world, extend it with new shots, write a 3 to 4 minute script, and ship it the same way with format `long`.
1. **Queue check.** If three or more `long` episodes are waiting (status `ready` or `approved`, not in the ledger), author nothing.
2. **Pick the case:** among the episodes in `publish/ledger.json` whose id starts with `r`, that have a `world3d.py`, and that are public or scheduled (`privacy` is `public` or `publish_at` is set), take the oldest one with no `episodes/<id>-long/` directory yet. Create that directory with its `episode.json` (status `draft`) and push right away, so a parallel run does not take the same case. If there is no such case, report and stop.
3. Follow the long-form section of `AUTHORING.md`, review the 16:9 contact sheet at least three rounds, ship with status `approved` or `ready`, report.

## Hard rules (both runs)
- Free tools only: Blender (bpy) with Cycles on CPU, Kokoro, ffmpeg. No paid services, no Higgsfield, no generative video or image services.
- True stories only; no invented facts or quotes; treat tragedy with respect (Rook's jokes stop for those beats). No graphic gore; suitable for a general audience.
- Never change `publish/config.json`, GitHub secrets, the workflows' safety rails or the QC gate. Never touch a YouTube channel directly: publishing happens only through the repository's workflow. Never commit secrets, mp4, wav, jpg, png or models.
- No copyrighted footage, music, characters or logos. Everything on screen is built from code in this repository.
- If something blocks you (tool missing, push refused), stop and report exactly what failed instead of working around the rules.
