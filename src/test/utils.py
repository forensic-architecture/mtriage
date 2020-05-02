import os
import json
import shutil
from types import SimpleNamespace as Ns
from pathlib import Path
from lib.common.storage import LocalStorage
from lib.common.get import get_module

TEMP_ELEMENT_DIR = "/mtriage/media/test_official"
TMP_DIR = Path("/tmp")
STUB_PATHS = Ns(imagejpg="/mtriage/src/test/etype_stubs/image.jpeg",)


def scaffold_empty(
    selector: str, elements: list = [], analysers: list = [], selector_txt=None
):
    """
    Scaffold an mtriage folder. One folder per element in the elements list will be created in the TEMP_ELEMENT_DIR.
    If an analysers list is passed, mocks of derived elements will be created in the appropriate folders.
    Only a single selector should be passed, as derived elements are nested within a selector pass. To create multiple
    selector passes, call this function multiple times.
    """
    derived_dir = f"{TEMP_ELEMENT_DIR}/{selector}/{LocalStorage.ANALYSED_EXT}"
    if not os.path.exists(derived_dir):
        os.makedirs(derived_dir)

    for element in elements:
        element_dir = (
            f"{TEMP_ELEMENT_DIR}/{selector}/{LocalStorage.RETRIEVED_EXT}/{element}"
        )
        if not os.path.exists(element_dir):
            os.makedirs(element_dir)
        if selector_txt is not None:
            with open(f"{element_dir}/item.txt", "a") as ftxt:
                ftxt.write(selector_txt)
        if len(analysers) > 0:
            for analyser in analysers:
                analyser_dir = f"{TEMP_ELEMENT_DIR}/{selector}/{LocalStorage.ANALYSED_EXT}/{analyser}/{element}"
                if not os.path.exists(analyser_dir):
                    os.makedirs(analyser_dir)


def get_element_path(selname, elementId, analyser=None):
    middle_insert = (
        LocalStorage.RETRIEVED_EXT
        if analyser is None
        else f"{LocalStorage.ANALYSED_EXT}/{analyser}"
    )
    return f"{TEMP_ELEMENT_DIR}/{selname}/{middle_insert}/{elementId}"


def scaffold_elementmap(elements=[]):
    out = [[x] for x in elements]
    out.insert(0, ["id"])
    return out


def cleanup():
    if Path(TEMP_ELEMENT_DIR).exists():
        shutil.rmtree(TEMP_ELEMENT_DIR)
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
        TMP_DIR.mkdir()


def listOfDictsEqual(l1, l2):
    if len(l1) != len(l2):
        return False

    for d1, d2 in zip(l1, l2):
        if not dictsEqual(d1, d2):
            return False

    return True


def dictsEqual(d1, d2):
    if len(d1.keys()) != len(d2.keys()):
        return False

    d1json = json.dumps(d1, sort_keys=True, default=str)
    d2json = json.dumps(d2, sort_keys=True, default=str)

    return d1json == d2json


def get_info_path(kind, mod_name):
    return f"lib/{kind}s/{mod_name}/info.yaml"


# https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))


def ltemp():
    """ Primarily for pdb debugging """
    list_files(TEMP_ELEMENT_DIR)
