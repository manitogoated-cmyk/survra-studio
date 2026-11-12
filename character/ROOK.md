# ROOK — main host character bible

- **Approval status:** concept chosen by the owner on 2026-11-12. Model sheet v1 awaiting final sign-off. Name screening not finished (see Name).
- **Name:** Rook (working name). "Rook" alone is used by several existing characters, so the plan is a distinctive full name or series title before any commercial use. A lawyer should confirm.
- **Role:** host, narrator and investigator of every Survra story. He is in the scene, not in a corner.

## Personality
- A crow detective who does not believe anything until he has seen it. Every story starts as a case he thinks is nonsense.
- Dry, sarcastic, quick. Unimpressed by default, which makes it land when a story really shocks him.
- Secretly soft: he respects the real people in the stories and drops the jokes for the hard moments.
- Crow instincts: cannot resist shiny things. He keeps one small object from every case.

## Series frame (franchise engine)
- Every video is a **case**: "Case 014: the man who fell off a cruise ship".
- Cold open on the most unbelievable moment, then Rook: **"No chance. Let's go look."**
- Sign-off: **"Case closed."** and he pockets the case's shiny object.
- His **case board** (photos, red string, numbers) is where maps, dates and figures appear, so every graphic belongs to his world.

## Signature mannerisms
1. Hat brim drops over his eyes when unimpressed; jumps off his head when shocked.
2. Pops his coat collar before walking into a scene.
3. Taps his beak when thinking.
4. Flips a coin while waiting; pockets anything shiny.
5. Sheds a feather when scared.
6. Laughs with a short caw.

## 3D style and silhouette
Since 2026-11-12 Rook is a 3D character (owner's decision: "make it 3d", free tools only). Faceted low-poly model built in Blender from code (`engine4/kit3d.py`, `rook_head` + `Rig(coat=True)`), flat shading, noir lighting with a warm key and an orange rim. Silhouette: wide-brim hat, beak, long belted coat, thin bird legs. The 2D model sheet stays as the design reference for proportions, palette and expressions.

## Face, eyes, brows
Dark feathered head, amber almond eyes with small pupils, feather brows that tilt for emotion, steel-grey beak. Feather tufts at the back of the head in side view.

## Outfit, palette, accessories
| Part | Colour |
|---|---|
| Feathers | #2A2742 (shadow #1C1A2E) |
| Coat | #566178 (shadow #404A5E), lapels #6B7790 |
| Eyes | #FFB000 |
| Hat | #34303B (shadow #24212A) |
| Hat band and tie | #FF7A1A (Survra orange) |
| Beak | #7A8096 (shadow #565B6E) |
| Trousers / boots | #2B2834 / #191720 |
| Belt buckle | #FFC233 |
| Outline | #1B1730 |

## Model sheet
`character/rook_model_sheet.png` (2D design reference, generated from `concepts/v2.py`): front, three-quarter, side and back views; 12 expressions; 5 beak shapes for lip sync (plus side view); poses for point, run, shrug, think, arms crossed, jump and hat pop; silhouette and profile-icon tests.

## Voice direction
Low, dry, unhurried noir narrator who speeds up when the story does. Synthetic voice (Kokoro-82M, Apache-2.0); the exact voice is chosen by ear from two or three auditions in the showcase Short and then never changed. No imitation of any real person.

## Licences
Original character design. Font: Inter (OFL). Voice model: Kokoro-82M (Apache-2.0).

## Continuity rules
Preserve the approved design unless the owner approves a change. Rook is rendered in 3D from the one rig in `engine4/kit3d.py` so he cannot drift. He takes part in every story: walks in, investigates, points, reacts. Every story gets a new world around him.
