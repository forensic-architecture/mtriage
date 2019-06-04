#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please run 'source .env', and confirm you are running the script inside Docker."
	exit
fi

WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="meta"

ELEMENTS_IN="[\"local\"]"

CONFIG=$( jq -n \
	--argjson el_in "$ELEMENTS_IN" \
	'{
		elements_in: $el_in,
		delete_cache : true,
		modules: [
			{
				"name" : "extract_audio",
				"config" : { "output_ext" : "mp3" }
			},
			{
				"name" : "convert_audio",
				"config" : { "input_ext" : "mp3", "output_ext" : "wav" }
			}
		]
	}'
)

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--module $MODULE \
	--config "$CONFIG" \
	--folder $WORKING_DIR
