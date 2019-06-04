# -*- coding: utf-8 -*-
"""The entry point for mtriage.

Orchestrates selectors and analysers via CLI parameters.

Modules:
    Each module corresponds to a web platform API, or some equivalent method
    of programmatic retrieval.

    TODO: document where to find selector and analyser design docs.
Attributes:
    module (str): Indicates the platform or source from which media should be
        analysed. The code that implements is module is self-contained to a
        folder here in the 'select' folder.
    config (dict of str: str): Hyperparameters that refine the analyse space.
        These parameters are module-specific (although the aim is to create as
        consistent as possible a parameter language across modules).
    folder (str): The path to the directory where the data that is indexed
        during the SELECT pass will be saved. This directory serves as a kind of
        "working directory" during the SAMPLE and ANALYSE passes, in the sense
        that all generated data is saved in this directory. The directory also
        contains logs, and represents the 'saved state' of a media triage
        analysis.

"""

import argparse
import json
import os

from lib.common.get_module import get_module
from lib.common.exceptions import (
    InvalidPhaseError,
    SelectorNotFoundError,
    AnalyserNotFoundError,
    WorkingDirectorNotFoundError,
)


def _select_run(args):
    # make output dirs if they don't exist
    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    try:
        TheSelector = get_module("selector", args.module)
    except:
        raise SelectorNotFoundError(args.module)

    config = json.loads(args.config) if args.config else {}
    selector = TheSelector(config, args.module, args.folder)

    selector.start_indexing(config)
    # TODO: conditionally run retrieve based on config
    selector.start_retriving(config)


def _analyse_run(args):
    if not os.path.exists(args.folder):
        raise WorkingDirectorNotFoundError(args.folder)

    try:
        TheAnalyser = get_module("analyser", args.module)
    except:
        raise AnalyserNotFoundError(args.module)

    config = json.loads(args.config) if args.config else {}

    analyser = TheAnalyser(config, args.module, args.folder)
    analyser._run(config)


def _run():
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("--module", "-m", help="Module to use", required=True)
    PARSER.add_argument(
        "--config", "-c", help="Configuration options for module", required=True
    )
    PARSER.add_argument(
        "--phase", "-p", help="The phase to run. One of: select, analyse", required=True
    )
    PARSER.add_argument(
        "--folder", "-f", help="Path to working folder for results", required=True
    )

    ARGS = PARSER.parse_args()

    if ARGS.phase == "select":
        _select_run(ARGS)
    elif ARGS.phase == "analyse":
        _analyse_run(ARGS)
    else:
        raise(InvalidPhaseError())


if __name__ == "__main__":
    _run()
