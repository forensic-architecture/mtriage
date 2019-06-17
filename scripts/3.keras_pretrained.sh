#!/bin/bash
WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="keras_pretrained"

MODEL="ResNet50"
ELEMENTS_IN="[\"youtube/frames\"]"

CONFIG=$( jq -n \
	--arg model "$MODEL" \
	--argjson el_in "$ELEMENTS_IN" \
	'{elements_in: $el_in, model: $model }'
)

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--config "$CONFIG" \
	--module "$MODULE" \
	--folder "$WORKING_DIR"
