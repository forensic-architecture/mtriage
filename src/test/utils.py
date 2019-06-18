import os
import pandas as pd
from lib.common.analyser import Analyser
import shutil

TEMP_ELEMENT_DIR = "../temp/test"


def scaffold_empty(selname, elements=[], analysers=[]):
    print("scaffold run")
    if not os.path.exists(TEMP_ELEMENT_DIR):
        raise Exception(
            "temp element dir doesn't exist - you need to instantiate it in a selector or analyser before using test methods."
        )

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
    rows = list(map(lambda elid: {"element_id": elid}, elements))
    return pd.DataFrame(rows)


def cleanup():
    shutil.rmtree(TEMP_ELEMENT_DIR)
