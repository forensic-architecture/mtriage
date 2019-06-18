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
