#!/usr/bin/env bash

## run from top level, i.e. `bash scripts/lint.sh`
black src/
black test/
black commands.py
black util.py
black mtriage
