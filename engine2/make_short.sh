#!/usr/bin/env bash
# One command: script -> voice -> storyboard render -> sound design -> mux -> quality gate.
set -euo pipefail
DIR=$1; NAME=$2; E=$(dirname "$0")
python3 "$E/../engine/voice.py" "$DIR/script.json" "$DIR/build"
python3 "$E/render.py" "$DIR/build" "$DIR/storyboard.json" "$DIR/build/video.mp4" 2>&1 | grep -v Fontconfig | tail -1
python3 "$E/audio2.py" "$DIR/build" "$DIR/build/mix.wav"
ffmpeg -y -loglevel error -i "$DIR/build/video.mp4" -i "$DIR/build/mix.wav" -c:v copy -c:a aac -b:a 192k -shortest "$DIR/$NAME.mp4"
python3 "$E/qc.py" "$DIR/build" "$DIR/$NAME.mp4"
