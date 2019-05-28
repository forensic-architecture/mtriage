#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please run 'source .env', and confirm you are running the script inside Docker."
	exit
fi

WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="frames"

ELEMENTS_IN="[\"youtube\"]"
FRAME_METHOD="opencv"
CHANGE_THRESHOLD="1e-5"
SEQUENTIAL_FRAMES="false"
FPS="1"

CONFIG=$( jq -n \
	--arg m "$FRAME_METHOD" \
	--argjson ct "$CHANGE_THRESHOLD" \
	--argjson seq "$SEQUENTIAL_FRAMES" \
	--argjson fps "$FPS" \
	--argjson el_in "$ELEMENTS_IN" \
	'{elements_in: $el_in, method: $m, change_threshold: $ct, sequential: $seq, fps: $fps}'
)

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--module $MODULE \
	--config "$CONFIG" \
	--folder $WORKING_DIR
