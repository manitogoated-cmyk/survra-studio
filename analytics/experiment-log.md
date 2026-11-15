# Experiment log

One main variable per experiment. Baseline cohort for all Shorts experiments: the 10 comparable v1 Shorts in `winners-and-underperformers.md` (snapshot 2026-11-15). Read results from `video-performance.csv` once the Analytics API has caught up (at least 3 days after publishing) and at 7 days. Never delete a row; add the result and the decision below each one.

Status values: planned → running → read → decided.

---

## E1. No doubt cutaway: Rook doubts the story inside the scene
- **Status:** planned (waiting for the owner to approve the authoring-rule change)
- **Hypothesis:** cutting from the danger to Rook in his office loses about 30% of the audience at 11–21% of runtime. If Rook voices his doubt from inside the scene, at most 1.5 s and without leaving the danger, fewer viewers will leave there.
- **Control:** v1 Shorts (Okene 0.76 and Suitcase 0.78 of the audience still watching at 21%).
- **Change:** the beat after the hook stays in the story world; Rook appears in the scene (on a rock, a rail, a branch) and doubts in one line; no office set.
- **Metric:** audience at 21% (`ret_20`) and the drop from 11% to 21%. Secondary: average % viewed.
- **Success:** median drop from 11% to 21% across the batch of 0.20 or less (vs 0.30). **Failure:** 0.27 or more.
- **Sample:** all Shorts in the next batch (10). Measured on the retention curve at the exact moment that changed, which limits how much topic choice can blur the result.

## E2. Tell it forward: no jump back to background after the hook
- **Status:** planned. Runs with E1 because both change the same 10 seconds; the batch is read as "spine v2" vs v1. This breaks the one-variable rule on purpose: the drop there is the largest measured loss, and waiting another 10 uploads to separate the two would cost more than it teaches.
- **Change:** after the hook, the story continues forward from that moment. Date, place and name appear as a 1-second on-screen card (diegetic case-file label) instead of a narrated sentence. Background comes later, only where it raises the stakes.
- **Metric:** drop from 21% to 31% (`ret_20` − `ret_30`). Baseline −0.21.
- **Success:** median −0.12 or better.

## E3. First frame: one person close-up vs. wide spectacle
- **Status:** planned
- **Hypothesis:** opening on one person at human scale, close and in the danger, makes fewer viewers swipe and helps a Short through the feed test.
- **Design:** within the next 10 Shorts, all on spine v2, alternate: odd-numbered = **person close-up** (face or hands, eye level, in the danger); even-numbered = **wide establishing spectacle** (the vehicle, storm or landscape at scale). Same story types in both arms where the slate allows.
- **Metric:** engaged views / views (swipe proxy), views at 48 h, and whether the Short "broke out" (over 500 views at 48 h).
- **Success:** the person arm beats the wide arm on the median engaged ratio by 5+ points AND has more breakouts. **Inconclusive** if within 5 points. Five per arm is small; read as direction, then confirm on the batch after.

## E4. Ending: a specific question for viewers vs "Case closed."
- **Status:** planned
- **Hypothesis:** a concrete question in Rook's sign-off gets comments, and comments feed the slate.
- **Design:** in the next 10 Shorts, cross E3 so each ending variant appears in both first-frame arms: Shorts 1, 3, 4, 8, 9 end with one specific question tied to a real decision or an open point in the story (not "like and subscribe"); 2, 5, 6, 7, 10 end with "Case closed." Question endings go to stories where a real question exists; tragedies (5, 7, 10) are not forced into one.
- **Metric:** comments per 1,000 views; secondary: subscribers per 1,000 views, average % viewed (check the question doesn't lose the end).
- **Success:** question arm reaches 1+ comment per 1,000 views and the "Case closed" arm stays near 0.

## E6. Quality upgrade: 60 fps, lit faces, acting, new mix (engine change, all videos)
- **Status:** planned (starts with the first episode rendered after `quality-upgrade` is merged)
- **Hypothesis:** smoother motion, readable faces and a mix with dynamics raise average % viewed across the board.
- **Control:** the 10 v1 Shorts. **Confound:** runs together with spine v2 (E1/E2), so read E6 on the parts of the curve E1/E2 do not touch: audience at 50% and at 90% of runtime (`ret_50`, `ret_90`).
- **Success:** median `ret_50` up 5+ points vs v1. This is a before/after comparison, not a controlled test: treat it as direction only.

## E7. On-screen hook title in the first 1.8 s
- **Status:** planned
- **Design:** alternate inside the next batch: half the Shorts with `hook_text`, half without (cross with E3 so both first-frame arms get both).
- **Metric:** engaged views / views (swipe proxy); Studio "Viewed vs swiped away" when the owner exports it (the API does not return it).
- **Success:** hook-title arm 5+ points higher on the median. Five per arm: direction only.

## E8. Loop ending and short tail
- **Status:** planned
- **Change:** tail 0.5 s or less and a last line that points back at the first.
- **Metric:** average % viewed (a replay pushes it past 100%) and `ret_90`.
- **Note:** outside sources claim loops help; none is official and none shows how YouTube weighs replays. Our own numbers decide.

## E5. Long-form custom thumbnails (fix first, then measure)
- **Status:** blocked on the owner: phone-verify the channel at youtube.com/verify. The daily `repair` job then retries the 12 failed thumbnails automatically.
- **Metric:** long-form views/day and impressions CTR (Studio) for 7 days before vs 7 days after.
- **Note:** this is a fix, not really an experiment; the before/after is recorded so its effect isn't credited to a creative change made the same week.

---

## Rules
- Do not start a new experiment that changes the first 10 seconds of a Short while E1/E2 or E3 is running.
- A result needs both: the metric threshold AND the Analytics API data being at least 3 days old.
- Write the decision (adopt / reject / rerun) here and copy adopted rules into `AUTHORING.md`.
