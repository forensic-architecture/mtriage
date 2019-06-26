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
		dev : true,
		delete_cache : true,
		children: [
			{
				"name" : "extract_audio",
				"config" : { "output_ext" : "wav" }
			},
      {
				"name" : "audio_onsets",
				"config" : { }
			}
		]
	}'
)

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--module $MODULE \
	--config "$CONFIG" \
	--folder $WORKING_DIR
