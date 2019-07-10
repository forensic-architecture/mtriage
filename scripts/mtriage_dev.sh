#!/usr/bin/env bash

# run inside a bash shell in the Docker container, from mtriage directory using:
# 	./scripts/mtriage_dev examples/an-frames.yaml

cp $1 /run_args.yaml
python src/run.py
rm /run_args.yaml
