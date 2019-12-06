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
import os
import yaml
from lib.common.get_module import get_module
from validate import validate_yaml

CONFIG_PATH = "/run_args.yaml"


def _run_yaml():
    with open(CONFIG_PATH, "r") as c:
        cfg = yaml.safe_load(c)

    is_single_phase = validate_yaml(cfg)

    if is_single_phase:
        print("-----------------------------------------------")
        print("Note: you are using the deprecated YAML format.")
        print("-----------------------------------------------")
        # run single phase
        # NB: this is actually only for backwards compatibility. could remove as the new config fmt is expressive
        # enough to accommodate running a single phase of analyser or selector just as easily.
        if not os.path.exists(cfg["folder"]):
            os.makedirs(cfg["folder"])

        Mod = get_module(cfg["phase"], cfg["module"])
        the_module = Mod(cfg["config"], cfg["module"], cfg["folder"])
        if cfg["phase"] == "select":
            the_module.start_indexing()
            the_module.start_retrieving()
        else:  # analyse
            the_module.start_analysing()

    else:
        base_cfg = {}
        if "select" not in cfg and "elements_in" in cfg:
            base_cfg["elements_in"] = cfg["elements_in"]
        else:
            # run select
            sel = cfg["select"]
            Selector = get_module("select", sel["name"])
            selector = Selector(
                sel["config"] if "config" in sel.keys() else {}, sel["name"], cfg["folder"]
            )
            selector.start_indexing()
            selector.start_retrieving()
            base_cfg["elements_in"] = [sel["name"]]

        # then analyse if specified
        if "analyse" not in cfg:
            return

        ana = cfg["analyse"]
        if isinstance(ana, dict):
            # run a single analyser
            Analyser = get_module("analyse", ana["name"])
            analyser = Analyser(
                { **ana["config"], **base_cfg } if "config" in ana.keys() else base_cfg,
                ana["name"],
                cfg["folder"],
            )
            analyser.start_analysing()

        else:
            # run the meta analyser to chain them all together
            # Analyser = get_module("analyse", "meta")
            # meta_cfg = {"children": }
            # analyser = Analyser()
            raise NotImplemented("Chaining analysers is not yet implemented.")


if __name__ == "__main__":
    _run_yaml()
