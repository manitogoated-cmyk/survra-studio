# Creative patterns: why some Shorts may have worked

Evidence labels: **Measured** = read directly from the API. **Correlation** = seen across our videos but not proven to cause anything. **Hypothesis** = a plausible explanation to test. Sample size: 10 comparable Shorts with view counts; 2 with retention curves.

What was inspected: each episode's `script.json` (every narration line), `storyboard.json` (every shot, camera, sound cue) and published title. **The rendered videos were not watched and the audio was not listened to** in this audit. Findings about the first frame come from storyboard descriptions, not pixels.

## 1. Every Short uses the same script structure, and the biggest drop lands on it (Measured, n=2)
All 11 Shorts follow one template: hook line (action) → Rook's doubt, "No chance. … Let's go look." (cut to Rook, his first shot is #4 or #5) → "Month Year. Name, job…" (jump back to the background) → story → "Case closed."

Matching narration word share to runtime, then reading the API retention curve:

| Runtime | Beat | Okene audience | Suitcase audience |
|---|---|---|---|
| 0–11% | Hook, in the action | 1.38 → 1.06 | 1.17 → 1.08 |
| 11–21% | **Doubt cutaway to Rook** | **−0.30** | **−0.30** |
| 21–31% | **Jump back: date, place, name** | −0.21 | −0.21 |
| 31–51% | Story moves forward again | −0.07 | −0.13 |
| 51–91% | Story, reversal, payoff | −0.04 | −0.07 |

(Curve samples at 1%, 11%, 21%, 31%, 51% and 91% of runtime. Values above 1.0 mean people re-watched that part.) **About half the audience leaves in the 2 beats right after the hook**, which is roughly seconds 5–15. Once the story runs forward, the curve almost flattens. Both curves show the same shape at the same beats.

**Hypothesis:** the hook builds momentum, and then the template stops it twice: first by cutting away from the danger to a crow who says it didn't happen, then by rewinding to background facts. Early drop-off happens on every Short, so part of this would occur anyway. But two curves dropping hardest at the same two beats is the strongest signal in the data. **Test: E1, E2.**

## 2. First frame: one person close-up vs. wide spectacle (Correlation, n=10)
| Group | Opening shot (storyboard) |
|---|---|
| Broke out (4) | Okene: a diver's lamp in a flooded corridor, then a pale hand · Grimes: "A man's eyes snap open, chest-deep in black water" · Prosperi: a runner looks back at a wall of sand · Suitcase: rushing through grass to a suitcase, a runner stops |
| Middle (1) | Vulovic: a jet breaks in two above the clouds |
| Stalled (5) | Wisnierska: a paraglider yanked up inside a cloud · Packard: a whale's mouth from behind the diver · Lemons: an umbilical cable snaps over a structure · Wow: a radio ring racing out of space · Rankin: a pilot blasts out of a jet above the clouds |

All 4 breakouts open on **one person at human scale, in the danger, close enough to read their body or face**. Most of the stalled Shorts open on **a vehicle, an object, or a tiny figure in a big sky or sea**. About half of feed viewers swipe in the first moments (engaged views were 49–56% of views), so the first frame matters a great deal.

**Caveat:** the feed test also has randomness; one stalled Short could have broken out on a rerun. **Test: E3.**

## 3. Topic (Correlation, weak)
- Sky/altitude cases: Vulovic 243, Wisnierska 40, Rankin 4. Two of three stalled.
- Sea cases: Okene 1,408, Grimes 1,227, Packard 32, Lemons 14. Mixed.
- Land/creepy: Prosperi 1,153, Suitcase 798. Both broke out.
- Space mystery (Wow signal): 6. The only non-survival topic, and the weakest result.

Topic alone doesn't separate the groups as cleanly as the opening shot does. Sky cases may struggle because they naturally open wide (a plane, a cloud, a figure far away). The upcoming slate has four more sky cases (24–27). **Don't drop the topic; change how it opens.**

## 4. Hook-line wording (Correlation, weak)
- Winners name **one strong, physical image**: "one of the hands grabs him", "wakes up in the ocean… no ship", "a man steps out of the woods", "on bat blood".
- Stalled Shorts lean on **numbers and measurements**: "a hundred metres… five minutes of gas", "fourteen kilometres up", "seventy-two seconds", "higher than Everest".

Numbers ask the viewer to work out why it matters; an image makes them feel it straight away. This fits pattern 2, so it may be the same effect.

## 5. Endings and comments (Correlation, n=1)
10 of 11 Shorts end with "Case closed." The one that ends on an open question to viewers (Suitcase, "Tell me your theory") has the only comment on the channel and the highest likes per 1,000 views (26.3). With 1 comment total, this is not proof. **Test: E4.**

## 6. Rook's role (Hypothesis)
Rook appears in his office to doubt the story, then mostly narrates. The beat that held best in Suitcase (46–54%: "Look at his feet. Boots.") is Rook **pointing at a clue inside the story world**. The beat that lost the most viewers is Rook **outside the story world**. Rook works better as a detective standing at the scene than as a narrator behind a desk. Make him part of the action (E1).

## 7. Packaging
- Shorts titles hardly affect the feed: 96% of Shorts views came from the feed, where the title is small. Search brought 18 views.
- Long-form packaging is currently broken: no custom thumbnails (see `winners-and-underperformers.md`).
- Long-form titles repeat the Short's story the same day. Someone who saw the Short already knows the ending. Hypothesis to revisit once thumbnails are live.

## 8. Sound, music, animation quality
**Not assessed.** No rendered video or audio was reviewed in this audit, and no retention curve exists yet for the videos where sound differs. The storyboards show planned sound effects on most shots (impacts, heartbeats, bubbles). See `data-gaps.md` for how to assess this next cycle.

## 9. Volume and timing (Hypothesis, not acted on)
The channel published 4 Shorts and 3 long-form videos a day from day one; `plan/LAUNCH.md` planned 1 Short a day for weeks 1–2. Breakouts came at 12:00, 18:16, 21:00 and 00:31 ET; stalled Shorts at 15:00, 18:00 and 21:00. Publish time doesn't explain the split. Whether daily volume affects how many Shorts get tested can't be measured from one channel in 4 days.
