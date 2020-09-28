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
from lib.common.etypes import Etype, LocalElementsIndex
from lib.common.storage import LocalStorage
from test.utils import scaffold_elementmap, STUB_PATHS, list_files


class EmptySelector(Selector):
    out_etype = Etype.Any

    def __init__(self, config, name, dr):
        super().__init__(config, name, dr)
        self.disk.delete_local_on_write = False

    def index(self, config):
        if not os.path.exists(self.disk.read_query(self.name)):
            df = scaffold_elementmap(["el1", "el2", "el3"])

            df = [
                x + [STUB_PATHS.imagejpg] if idx > 0 else (x + ["path"])
                for idx, x in enumerate(df)
            ]
            return LocalElementsIndex(rows=df)
        else:
            return None

    def retrieve_element(self, row, config):
        return Etype.cast(row.id, row.path)


@pytest.fixture
def additionals(utils):
    obj = lambda: None
    obj.emptySelector = EmptySelector(
        {"dev": True}, "empty", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
    )
    utils.setup()
    yield obj
    utils.cleanup()


def test_selector_imports():
    assert type(Selector) == type(ABC)


def test_cannot_instantiate(utils):
    with pytest.raises(TypeError):
        Selector({}, "empty", utils.TEMP_ELEMENT_DIR)


def test_init(utils, additionals):
    assert Path(utils.TEMP_ELEMENT_DIR) == additionals.emptySelector.disk.base_dir
    assert "empty" == additionals.emptySelector.name


def test_index(additionals):
    additionals.emptySelector.start_indexing()
    # test element_map.csv is what it should be
    eidx = additionals.emptySelector.disk.read_elements_index("empty")
    emap = scaffold_elementmap(["el1", "el2", "el3"])
    for idx, row in enumerate(eidx.rows):
        assert row.id == emap[idx + 1][0]


def test_retrieve(additionals, utils):
    additionals.emptySelector.start_indexing()
    additionals.emptySelector.start_retrieving(in_parallel=False)
    pth = additionals.emptySelector.disk.read_query("empty")
    images = [pth / f"{x}/image.jpeg" for x in ["el1", "el2", "el3"]]
    for img in images:
        assert os.path.isfile(img)


# the values that are returned from retrieve need to be managed in Python differently according to what kind of data
# they represent.
#
# Video -> cv2.VideoCapture
# Image -> cv2.Image
# Audio -> simpleaudio.WaveObject
# Json  -> dict

# the relationship between files on disk and how they are loaded through Python should be managed in the etypes library.
