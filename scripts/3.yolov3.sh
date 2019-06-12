#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please confirm you are running the script inside Docker."
	exit
fi

WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="yolov3"

## paths here are in the form ${selector_name}/${analyser_name}
## there should never be a nested analyser name, as even analysers that operate on derived
## data still produce derived data at the first level of the 'derived' folder. (??)
ELEMENTS_IN="[\"youtube/frames\"]"
# if true, generate output images that contain bounding boxes and labels. (Takes a bit
# longer.)

CONFIG=$( jq -n \
	--argjson el_in "$ELEMENTS_IN" \
	'{elements_in: $el_in }'
)

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--config "$CONFIG" \
	--module "$MODULE" \
	--folder "$WORKING_DIR"
