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
import yaml
import os
from pathlib import Path
from subprocess import check_output
import shutil

from lib.common.get_module import get_module
from lib.common.exceptions import (
    InvalidPhaseError,
    SelectorNotFoundError,
    AnalyserNotFoundError,
    WorkingDirectorNotFoundError,
    InvalidConfigError,
)

CONFIG_PATH = "/run_args.yaml"


def _select_run(args):
    # NOTE: make output dirs if they don't exist
    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    try:
        TheSelector = get_module("selector", args.module)
    except:
        raise SelectorNotFoundError(args.module)

    config = json.loads(args.config) if args.config else {}
    selector = TheSelector(config, args.module, args.folder)

    selector.start_indexing()
    # TODO: conditionally run retrieve based on config
    selector.start_retrieving()


def _analyse_run(args):
    if not os.path.exists(args.folder):
        raise WorkingDirectorNotFoundError(args.folder)

    try:
        TheAnalyser = get_module("analyser", args.module)
    except:
        raise AnalyserNotFoundError(args.module)

    config = json.loads(args.config) if args.config else {}

    analyser = TheAnalyser(config, args.module, args.folder)
    analyser.start_analysing()


def _run():
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("--module", "-m", help="Module to use", required=True)
    PARSER.add_argument(
        "--config", "-c", help="Configuration options for module", required=True
    )
    PARSER.add_argument(
        "--phase",
        "-p",
        help="The phase to run. One of: select, analyse, view",
        required=True,
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
        raise (InvalidPhaseError())

def __validate_config(config):
    if "folder" not in config.keys() or not isinstance(config["folder"], str):
        raise InvalidConfigError("The folder attribute must exist and be a string")
    if "phase" not in config.keys() or config["phase"] not in ["select", "analyse"]:
        raise InvalidConfigError("The phase attribute must be either select or analyse")

    if "module" not in config.keys():
        raise InvalidConfigError("You must specify a module")

    def module_name(phase):
        return "selector" if phase == "select" else "analyser"

    mod_name = module_name(config["phase"])

    try:
        get_module(mod_name, config["module"])
    except ModuleNotFoundError as e:
        raise InvalidConfigError(f"No {mod_name} named '{config['module']}'")



def _run_yaml():
    with open(CONFIG_PATH, "r") as c:
        config = yaml.safe_load(c)
    __validate_config(config)


if __name__ == "__main__":
    _run_yaml()
