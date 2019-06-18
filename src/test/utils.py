import os
from lib.common.analyser import Analyser
import shutil
import json

TEMP_ELEMENT_DIR = "../temp/test"


def scaffold_empty(selname, elements=[], analysers=[]):
    os.makedirs(f"{TEMP_ELEMENT_DIR}/{selname}/{Analyser.DERIVED_EXT}")

    for element in elements:
        os.makedirs(f"{TEMP_ELEMENT_DIR}/{selname}/{Analyser.DATA_EXT}/{element}")
        if len(analysers) > 0:
            for analyser in analysers:
                os.makedirs(
                    f"{TEMP_ELEMENT_DIR}/{selname}/{Analyser.DERIVED_EXT}/{analyser}/{element}"
                )


def get_element_path(selname, elementId, analyser=None):
    middle_insert = (
        Analyser.DATA_EXT if analyser is None else f"{Analyser.DERIVED_EXT}/{analyser}"
    )
    return f"{TEMP_ELEMENT_DIR}/{selname}/{middle_insert}/{elementId}"


def scaffold_elementmap(elements=[]):
    out = [[x] for x in elements]
    out.insert(0, ["id"])
    return out

def cleanup():
    shutil.rmtree(TEMP_ELEMENT_DIR)

def listOfDictsEqual(l1, l2):
    if len(l1) != len(l2):
        return False

    _l1 = [json.dumps(x, sort_keys=True, indent=2) for x in l1]
    _l2 = [json.dumps(x, sort_keys=True, indent=2) for x in l2]

    for idx in range(len(_l1)):
        if _l1[idx] != _l2[idx]:
            return False

    return True
