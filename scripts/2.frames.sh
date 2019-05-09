#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please run 'source .env', and confirm you are running the script inside Docker."
	exit
fi

WORKING_DIR="$BASE_DIR/temp/demo_output"
MODULE="frames"

python3 $BASE_DIR/src/run.py \
	--phase analyse \
	--module $MODULE \
	--folder $WORKING_DIR
