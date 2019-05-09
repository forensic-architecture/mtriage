#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please run 'source .env', and confirm you are running the script inside Docker."
	exit
fi

FILEPATH="$BASE_DIR"
LABEL="military uniform"
HARDWARE="local"

WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="keras_mobilenet"

CONFIG=$( jq -n \
	--arg filepath "$FILEPATH" \
	--arg label "$LABEL" \
	--arg hardware "$HARDWARE" \
	'{filepath: $filepath, labels: $label, hardware: $hardware}'
)

python $BASE_DIR/src/run.py \
	--phase analyse \
	--module $MODULE \
	--config $CONFIG \
	--folder $WORKING_DIR
