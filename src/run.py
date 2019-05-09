# -*- coding: utf-8 -*-
"""The entry point of the SELECT phase.

The select phase designates a media space locally, on the web, or through some
combination of both. The parameters by which a space is selected are made
available through a range of different selector modules.

Modules:
    Each module corresponds to a web platform API, or some equivalent method
    of programmatic retrieval.

    The current design for a selector module is simple: it should exist as a
    folder in lib.select that contains a 'run.py' file. This file should
    expose a function called 'main' that does the module's work by accepting
    two arguments: e.g. `main(config, folder_path)`.

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
Todo:
    * document the configuration options for Youtube module.
    * implement Twitter module
    * allow the composition of module/config pairs, e.g. the ability to specify
        multiple at the level of module arguments.
    * https://whopostedwhat.com/ - Facebook.
"""
import argparse
import json
import os

from lib.common.get_selector import get_selector
from lib.common.get_analyser import get_analyser


def _select_run(args):
    if not os.path.exists(args.folder):
        os.mkdir(args.folder)

    TheSelector = get_selector(args.module)
    print(args.config)
    config = json.loads(args.config) if args.config else {}

    selector = TheSelector(args.folder, args.module)
    selector.index(config)
    # TODO: conditionally run retrieve based on config
    selector.retrieve(config)


def _analyse_run(args):
    if not os.path.exists(args.folder):
        raise Exception(
            "No folder exists at the path you specified. Generate one by running the SELECT phase."
        )

    TheAnalyser = get_analyser(args.module)
    config = json.loads(args.config) if args.config else {}

    if TheAnalyser is None:
        raise Exception(f"The module you have specified, {args.module}, does not exist")

    analyser = TheAnalyser(args.folder, args.module)
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
