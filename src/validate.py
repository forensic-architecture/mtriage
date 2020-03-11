import os
import yaml
import inspect
from pathlib import Path
from lib.common.exceptions import InvalidYamlError
from lib.common.get_module import get_module


def validate_module(phase: str, module: str, cfg: dict):
    try:
        mod = get_module(phase, module)
    except ModuleNotFoundError as e:
        raise InvalidYamlError(f"No {phase} module named '{module}'")

    # dynamically check all required args for module config exist
    sfolder = os.path.dirname(inspect.getfile(mod))
    info = Path(sfolder) / "info.yaml"
    with open(info, "r") as f:
        options = yaml.safe_load(f)
    for option in options["args"]:
        if "config" not in cfg:
            cfg["config"] = {}
        if option["required"] is True and option["name"] not in cfg["config"].keys():
            raise InvalidYamlError(
                f"The config you specified does not contain all the required arguments for the '{module}' {phase}er."
            )


def validate_name(cfg: dict):
    if "name" not in cfg.keys():
        raise InvalidYamlError(
            "Each analyse component must be a dict containing at least a 'name' attribute."
        )


def validate_analyse(cfg: dict):
    if not isinstance(cfg, dict) and not isinstance(cfg, list):
        raise InvalidYamlError("The 'analyse' attribute must be a dict or list.")
    if isinstance(cfg, dict):
        validate_name(cfg)
        validate_module("analyse", cfg["name"], cfg)
    else:
        for _cfg in cfg:
            validate_name(_cfg)
            validate_module("analyse", _cfg["name"], _cfg)


def validate_yaml(cfg: dict) -> bool:
    """
    Confirms all values on YAML. Throws an appropriate exception if something's up.
    """
    keys = cfg.keys()

    if "folder" not in keys or not isinstance(cfg["folder"], str):
        raise InvalidYamlError("The folder attribute must exist and be a string")

    if "phase" in keys or "module" in keys:
        # confirm good phase yaml
        if "module" not in keys:
            raise InvalidYamlError(
                "If you specified a phase, you must specify a module"
            )
        if "phase" not in keys:
            raise InvalidYamlError(
                "If you specified a module, you must specify a phase"
            )

        if "config" not in keys or not isinstance(cfg["config"], dict):
            raise InvalidYamlError("The 'config' attribute must exist.")

        if cfg["phase"] not in ["select", "analyse"]:
            raise InvalidYamlError(
                "The phase attribute must be either select or analyse"
            )
        validate_module(cfg["phase"], cfg["module"], cfg)
    else:
        if "elements_in" not in keys and "select" not in keys:
            raise InvalidYamlError("You must specify either 'elements_in' or 'select'.")
        if "elements_in" in keys:
            # bypassing selector...
            if "analyse" not in keys:
                raise InvalidYamlError(
                    "You have specified 'elements_in', and so at least one 'analyse' module must be specified."
                )

        elif "select" in keys:
            # run select then analyse
            validate_name(cfg["select"])
            validate_module("select", cfg["select"]["name"], cfg["select"])

        if "analyse" in cfg:
            validate_analyse(cfg["analyse"])

