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
import yaml
import os
import inspect
from pathlib import Path
from subprocess import check_output
from enum import Enum

from lib.common.get_module import get_module
from lib.common.exceptions import (
    InvalidPhaseError,
    SelectorNotFoundError,
    AnalyserNotFoundError,
    WorkingDirectorNotFoundError,
    InvalidConfigError,
)

CONFIG_PATH = "/run_args.yaml"


class YamlType(Enum):
    WHOLE = 0
    COMPONENT = 1
    PHASE = 2


def validate_module(phase: str, module: str, cfg: dict):
    try:
        mod = get_module(phase, module)
    except ModuleNotFoundError as e:
        raise InvalidConfigError(f"No {phase} module named '{module}'")

    # dynamically check all required args for module config exist
    sfolder = os.path.dirname(inspect.getfile(mod))
    info = Path(sfolder) / "info.yaml"
    with open(info, "r") as f:
        options = yaml.safe_load(f)
    for option in options["args"]:
        if option["required"] is True and option["name"] not in cfg["config"].keys():
            raise InvalidConfigError(
                f"The config you specified does not contain all the required arguments for the '{module}' {phase}."
            )


def validate_yaml(cfg: dict):
    keys = cfg.keys()

    if "folder" not in keys or not isinstance(cfg["folder"], str):
        raise InvalidConfigError("The folder attribute must exist and be a string")

    if "config" not in keys or not isinstance(cfg["config"], dict):
        raise InvalidConfigError("The 'config' attribute must exist.")

    config = cfg["config"]

    if "phase" in keys or "module" in keys:
        # confirm good phase yaml
        if "module" not in keys:
            raise InvalidConfigError(
                "If you specified a phase, you must specify a module"
            )
        if "phase" not in keys:
            raise InvalidConfigError(
                "If you specified a module, you must specify a phase"
            )
        if cfg["phase"] not in ["select", "analyse"]:
            raise InvalidConfigError(
                "The phase attribute must be either select or analyse"
            )
        validate_module(cfg["phase"], cfg["module"], config)
    else:
        # confirm good yaml for full
        pass


def _run_yaml():
    with open(CONFIG_PATH, "r") as c:
        cfg = yaml.safe_load(c)

    yaml_type = validate_yaml(cfg)

    # done validating, run appropriate phase
    if not os.path.exists(cfg["folder"]):
        os.makedirs(cfg["folder"])

    Mod = get_module(cfg["phase"], cfg["module"])
    the_module = Mod(cfg["config"], cfg["module"], cfg["folder"])
    if cfg["phase"] == "select":
        the_module.start_indexing()
        the_module.start_retrieving()
    else:  # analyse
        the_module.start_analysing()


if __name__ == "__main__":
    _run_yaml()
