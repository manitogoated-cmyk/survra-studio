# Survra production upgrade checklist (mandatory for every video)

Created 2026-11-15 from the Case 001 animation-quality review (`quality/REVIEW-2026-11-15-case001.md`).
An episode may only be set to `approved` when every **must** item is ticked in `episode.json` → `"checklist"`, with a
note for any item that does not apply. "Looked at" means the actual rendered pixels (preview stills or the render),
never the storyboard text.

## A. Before scripting
- [ ] **must** Story passes the story gate (75/100) and spine v2 (`AUTHORING.md`).
- [ ] **must** Every big moment in the narration ("a wave flips the tug", "the diver screams") has a shot that *shows* it. List them in `episode.json` → `shown_moments`.

## B. Storyboard (before any 3D work)
- [ ] **must** Every shot names: the character action (verb), the facial expression, the camera, what moves in the set, the sound cue.
- [ ] **must** Rook does at least one signature mannerism from `character/ROOK.md` (beak tap, hat brim, coin flip, pocketing the shiny object, feather shed, caw-laugh) and one detective action inside the story world.
- [ ] **must** No shot exists only to fill a cut quota. A shot is held until its action lands (up to 3.5 s in Shorts).
- [ ] **must** No character stands in a neutral or T-pose while the narration describes action. Use `wash`, `brace`, `tap`, `think`, `scream`, or write the pose.
- [ ] **must** Faces: every reaction the script names (shock, scream, laugh, grief) is driven on the face: mouth, brows, eyes. Characters without a mouth get one.
- [ ] **should** Subjects fill at least 1/4 of the frame height in key story shots; wide shots are for geography only.
- [ ] **should** One particle style per material (spray streaks, bubble spheres, debris shards); no single generic particle reused.

## C. Preview stills (local Blender, before the cloud render)
Run: `blender -b --factory-startup -P engine4/preview3d.py -- episodes/<id> <out> [kind@k,...] 720x1280`
- [ ] **must** Every shot previewed at least at k=0.2 and k=0.8 and looked at. Fix staging before rendering.
- [ ] **must** No blown-out (flat white) or crushed (flat black) frames where the story needs to be seen.
- [ ] **must** Faces readable at phone size: shrink the still to 270x480 and check that the expression still reads.
- [ ] **must** Rook on-model: hat, beak, coat, eye glow, palette.

## D. Render settings (engine defaults; do not lower without the owner's OK)
- [ ] **must** 60 fps, every frame rendered (`KIT3D_FPS=60`), no held or doubled frames.
- [ ] **must** Render at 720x1280 or higher (Shorts), 1280x720 or higher (long-form); AgX colour management; OIDN denoising.
- [ ] **must** Production uses at least 16 frame jobs per episode.

## E. Sound
- [ ] **must** Voice is the approved Rook identity once chosen (until then: the current TTS voice, flagged in the description).
- [ ] **must** Music follows the mood map; no drum loop under sad or tragic beats; hook starts near-silent.
- [ ] **must** Every visible impact has a matching effect within 2 frames; no effect without a visible cause.
- [ ] **must** Loudness range of 4 LU or more; voice at least 9 dB over the bed.

## F. Captions and graphics
- [ ] **must** No caption leaves the frame (engine fits to 84% width) and no caption overlaps an insert's text: inserts keep the band 62–78% of the height clear.
- [ ] **must** Every number, date and name on screen is checked against the sources.

## G. Final render review (the gate)
- [ ] **must** Watch the full render at least once (or, without playback, review a 4-frames-per-second contact sheet of the whole video and the audio measurements). Write timestamped notes in `episode.json` → `review`.
- [ ] **must** Score it with the 13-category gate from the 3D studio skill; no critical category below 3.
- [ ] **must** Spot-check 3 random 1-second ranges at full resolution for artifacts (black bands, flicker, popping objects).
- [ ] **must** The QC gate passes (pacing, motion, loudness, originality).
