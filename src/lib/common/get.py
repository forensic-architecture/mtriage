from pathlib import Path
from importlib import import_module
from lib.common.util import files


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

    pth = f"{module_folder}.{key}.core"
    mod = import_module(pth)
    return mod.module


def get_custom_etypes():
    base_import = "lib.etypes"
    module_folder = Path("lib/etypes")
    all_etypes = [t.stem for t in files(module_folder)]
    imports = [f"{base_import}.{p}" for p in all_etypes]
    return [import_module(mod).etype for mod in imports]
