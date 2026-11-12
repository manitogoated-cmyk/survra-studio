#!/usr/bin/env bash
# One command per episode: Rook's voice (with lip-sync timings) -> 3D frames (Blender/Cycles, CPU, resumable)
# -> composite (captions, HUD, transitions, 2D inserts) -> sound design -> mux -> QC gate.
set -euo pipefail
DIR=$1; NAME=$(basename "$DIR"); E=$(dirname "$0")
# PRERENDERED=1 (CI): voice and 3D frames were already produced by the voice/frames jobs.
if [ -z "${PRERENDERED:-}" ]; then python3 "$E/voice3.py" "$DIR/script.json" "$DIR/build"; fi
if [ -f "$DIR/world3d.py" ] && [ -z "${PRERENDERED:-}" ]; then
  python3 "$E/../engine4/kit3d.py" "$DIR" all 2>&1 | grep -E "^3d |Error|Traceback" || true
fi
python3 "$E/render3.py" "$DIR" "$DIR/build/video.mp4" 2>&1 | grep -v Fontconfig | tail -1
python3 "$E/audio3.py" "$DIR/build" "$DIR/build/mix.wav"
ffmpeg -y -loglevel error -i "$DIR/build/video.mp4" -i "$DIR/build/mix.wav" -c:v copy -c:a aac -b:a 192k -shortest "$DIR/$NAME.mp4"
python3 "$E/qc3.py" "$DIR" "$DIR/$NAME.mp4"
