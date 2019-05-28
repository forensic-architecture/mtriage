#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please run 'source .env', and confirm you are running the script inside Docker."
	exit
fi

WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="ocr"

# this is the number of requests that should be sent per element. It's mainly a testing
# parameter, so that we can just send 1 request per video rather than however many frames
# there are.
MAX_REQUESTS="1"
## paths here are in the form ${selector_name}/${analyser_name}
## there should never be a nested analyser name, as even analysers that operate on derived
## data still produce derived data at the first level of the 'derived' folder. (??)
ELEMENTS_IN="[\"youtube/frames\"]"

CONFIG=$( jq -n \
	--argjson mr "$MAX_REQUESTS" \
	--argjson el_in "$ELEMENTS_IN" \
	'{elements_in: $el_in, max_requests: $mr }'
)

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--config "$CONFIG" \
	--module "$MODULE" \
	--folder "$WORKING_DIR"
