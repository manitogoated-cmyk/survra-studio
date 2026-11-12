#!/usr/bin/env bash
# One command per episode: Kesta's voice (with lip-sync timings) -> render -> sound design -> mux -> QC gate.
set -euo pipefail
DIR=$1; NAME=$(basename "$DIR"); E=$(dirname "$0")
python3 "$E/voice3.py" "$DIR/script.json" "$DIR/build"
python3 "$E/render3.py" "$DIR" "$DIR/build/video.mp4" 2>&1 | grep -v Fontconfig | tail -1
python3 "$E/audio3.py" "$DIR/build" "$DIR/build/mix.wav"
ffmpeg -y -loglevel error -i "$DIR/build/video.mp4" -i "$DIR/build/mix.wav" -c:v copy -c:a aac -b:a 192k -shortest "$DIR/$NAME.mp4"
python3 "$E/qc3.py" "$DIR" "$DIR/$NAME.mp4"
