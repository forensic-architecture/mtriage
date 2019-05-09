#!/bin/bash
if [ -z $BASE_DIR ]; then
	echo "Please run 'source .env', and confirm you are running the script inside Docker."
	exit
fi

# modifiable parameters
MODULE="youtube"
SEARCH_TERM="Triple chaser"
UPLOADED_AFTER="2015-10-01T00:00:00Z"
UPLOADED_BEFORE="2015-10-02T00:00:00Z"

CONFIG=$( jq -n \
	--arg st "$SEARCH_TERM" \
	--arg upbef "$UPLOADED_BEFORE" \
	--arg upaft "$UPLOADED_AFTER" \
	--argjson daily "true" \
	'{search_term: $st, uploaded_before: $upbef, uploaded_after: $upaft, daily: $daily}'
)

OUTPUT_DIR="$BASE_DIR/temp/demo_output"

python3 $BASE_DIR/src/run.py \
	--phase select \
	--module "$MODULE" \
	--config "$CONFIG" \
  --folder "$OUTPUT_DIR"
