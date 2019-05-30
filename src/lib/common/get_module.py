from pathlib import Path
from importlib import import_module


def get_module(_from, key):
    """ Dynamically loads in all analysers from the analysers folder, generating a dictionary in which the folder name
        is the key, and the export from 'main' is the value.
    """
    if _from != "selector" and _from != "analyser":
        raise ImportError("The first argument of 'get_module' must be 'selector' or 'analyser'")

    module_folder = f"lib.{_from}s"
    pth = f"{module_folder}.{key}"

    mod = import_module(pth)
    return mod.main
