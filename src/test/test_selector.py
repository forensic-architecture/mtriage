import pytest
import os
import csv
from abc import ABC
from pathlib import Path
from lib.common.selector import Selector
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    SelectorIndexError,
    EtypeCastError,
)
from lib.common.etypes import cast, Etype, LocalElementsIndex
from lib.common.storage import LocalStorage
from test.utils import scaffold_elementmap, STUB_PATHS, list_files


class EmptySelector(Selector):
    def __init__(self, config, name, dr):
        super().__init__(config, name, dr)
        self.disk.delete_local_on_write = False

    def index(self, config):
        if not os.path.exists(self.disk.ELEMENT_MAP):
            df = scaffold_elementmap(["el1", "el2", "el3"])
            df = [x+[STUB_PATHS.imagejpg] if idx > 0 else (x+['path']) for idx, x in enumerate(df)]
            return LocalElementsIndex(rows=df)
        else:
            return None

    def retrieve_element(self, row, config):
        return cast(row.path, row.id, to=Etype.Image)


@pytest.fixture
def additionals(utils):
    obj = lambda: None
    obj.emptySelector = EmptySelector({}, "empty", storage=LocalStorage(folder=utils.TEMP_ELEMENT_DIR))
    yield obj
    utils.cleanup()


def test_selector_imports():
    assert type(Selector) == type(ABC)


def test_cannot_instantiate(utils):
    with pytest.raises(TypeError):
        Selector({}, "empty", utils.TEMP_ELEMENT_DIR)


def test_init(utils, additionals):
    assert utils.TEMP_ELEMENT_DIR == additionals.emptySelector.BASE_DIR
    assert "empty" == additionals.emptySelector.NAME
    assert f"{utils.TEMP_ELEMENT_DIR}/empty" == additionals.emptySelector.DIR
    assert (
        Path(f"{utils.TEMP_ELEMENT_DIR}/empty/data") == additionals.emptySelector.disk.ELEMENT_DIR
    )
    assert (
        Path(f"{utils.TEMP_ELEMENT_DIR}/empty/element_map.csv")
        == additionals.emptySelector.disk.ELEMENT_MAP
    )
    assert os.path.exists(additionals.emptySelector.disk.ELEMENT_DIR)


def test_index(additionals):
    additionals.emptySelector.start_indexing()
    assert os.path.exists(additionals.emptySelector.disk.ELEMENT_MAP)
    # test element_map.csv is what it should be
    with open(additionals.emptySelector.disk.ELEMENT_MAP, "r") as f:
        emreader = csv.reader(f, delimiter=",")
        rows = [l for l in emreader]
        emap = scaffold_elementmap(["el1", "el2", "el3"])
        for idx, row in enumerate(rows):
            if idx == 0: continue
            assert row[0] == emap[idx][0]



def test_retrieve(additionals, utils):
    additionals.emptySelector.start_indexing()
    additionals.emptySelector.start_retrieving(in_parallel=False)
    els = ["el1", "el2", "el3"]
    images = [additionals.emptySelector.disk.ELEMENT_DIR/f"{x}/0.jpeg" for x in els]
    for img in images:
        assert(os.path.isfile(img))


# the values that are returned from retrieve need to be managed in Python differently according to what kind of data
# they represent.
#
# Video -> cv2.VideoCapture
# Image -> cv2.Image
# Audio -> simpleaudio.WaveObject
# Json  -> dict

# the relationship between files on disk and how they are loaded through Python should be managed in the etypes library.
