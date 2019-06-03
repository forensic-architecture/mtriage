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


def _select_run(args):
    if not os.path.exists(args.folder):
        os.mkdir(args.folder)

    TheSelector = get_module("selector", args.module)
    config = json.loads(args.config) if args.config else {}

    selector = TheSelector(config, args.module, args.folder)
    selector.start_indexing(config)

    # TODO: conditionally run retrieve based on config
    selector.start_retriving(config)


def _analyse_run(args):
    if not os.path.exists(args.folder):
        raise Exception(
            "No folder exists at the path you specified. Generate one by running the SELECT phase."
        )

    TheAnalyser = get_module("analyser", args.module)
    config = json.loads(args.config) if args.config else {}

    if TheAnalyser is None:
        raise Exception(f"The module you have specified, {args.module}, does not exist")

    analyser = TheAnalyser(config, args.module, args.folder)
    analyser._run(config)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("--module", "-m", help="Module to use")
    PARSER.add_argument("--config", "-c", help="Configuration options for module")
    PARSER.add_argument(
        "--phase", "-p", help="The phase to run. One of: select, analyse"
    )
    PARSER.add_argument("--folder", "-f", help="Path to working folder for results")

    ARGS = PARSER.parse_args()
    if ARGS.phase == "select":
        _select_run(ARGS)
    elif ARGS.phase == "analyse":
        _analyse_run(ARGS)
    else:
        print("The phase you pass must be either 'select' or 'analyse'.")
