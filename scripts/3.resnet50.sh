#!/bin/bash
WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="resnet50"

ELEMENTS_IN="[\"youtube/frames\"]"

CONFIG=$( jq -n \
	--argjson el_in "$ELEMENTS_IN" \
	'{elements_in: $el_in }'
)

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--config "$CONFIG" \
	--module "$MODULE" \
	--folder "$WORKING_DIR"
