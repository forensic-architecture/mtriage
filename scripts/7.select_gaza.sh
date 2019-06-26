#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please run 'source .env', and confirm you are running the script inside Docker."
	exit
fi

# modifiable parameters
MODULE="local"
SOURCE_FOLDER="$BASE_DIR/temp/gaza/20180330-1/20180330-1-2"

CONFIG=$( jq -n \
	--arg st "$SOURCE_FOLDER" \
	'{source_folder: $st}'
)

OUTPUT_DIR="$BASE_DIR/temp/demo_output"

python3 $BASE_DIR/src/run.py \
	--phase select \
	--module "$MODULE" \
	--config "$CONFIG" \
  --folder "$OUTPUT_DIR"
