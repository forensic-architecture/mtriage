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
from validate import validate_yaml
from lib.common.get import get_module
from lib.common.storage import LocalStorage

CONFIG_PATH = "/run_args.yaml"


def make_storage(cfg: dict) -> LocalStorage:
    # TODO: generalise `folder` here to a `storage` var that is passed from YAML
    return LocalStorage(folder=cfg["folder"])


def _run_analyser(ana: dict, base_cfg: dict, cfg: dict):
    # run a single analyser
    Analyser = get_module("analyse", ana["name"])
    analyser = Analyser(
        {**ana["config"], **base_cfg} if "config" in ana.keys() else base_cfg,
        ana["name"],
        make_storage(cfg),
    )
    analyser.start_analysing()


def _run_yaml():
    with open(CONFIG_PATH, "r") as c:
        cfg = yaml.safe_load(c)

    validate_yaml(cfg)

    base_cfg = {}
    if "select" not in cfg and "elements_in" in cfg:
        base_cfg["elements_in"] = cfg["elements_in"]
        sel = None
    else:
        # run select
        sel = cfg["select"]
        Selector = get_module("select", sel["name"])
        selector = Selector(
            sel["config"] if "config" in sel.keys() else {},
            sel["name"],
            make_storage(cfg),
        )
        selector.start_indexing()
        selector.start_retrieving()
        base_cfg["elements_in"] = [sel["name"]]

    if "analyse" not in cfg:
        return

    analyse_phase = cfg["analyse"]

    if isinstance(analyse_phase, dict):
        _run_analyser(analyse_phase, base_cfg, cfg)

    else:
        for ana in analyse_phase:
            _run_analyser(ana, base_cfg, cfg)
            if sel is None:
                # take the selector from elements in
                fst = cfg["elements_in"][0]
                sel = { 'name': fst.split("/")[0] }
            base_cfg["elements_in"] = [f"{sel['name']}/{ana['name']}"]


if __name__ == "__main__":
    _run_yaml()
