from pathlib import Path
from importlib import import_module


def get_module(_from, key):
    """ Dynamically loads in all analysers from the analysers folder, generating a dictionary in which the folder name
        is the key, and the export from 'main' is the value.
    """
    if _from == "select":
        module_folder = f"lib.selectors"
    elif _from == "analyse":
        module_folder = f"lib.analysers"
    else:
        raise ImportError("The phase argument must be either 'select' or 'analyse'")

    pth = f"{module_folder}.{key}"
    mod = import_module(pth)
    return mod.main
