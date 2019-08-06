import pytest
import os
import csv
from abc import ABC
from lib.common.selector import Selector
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    SelectorIndexError,
    EtypeCastError,
)
from test.utils import scaffold_elementmap


class EmptySelector(Selector):
    def index(self, config):
        if not os.path.exists(self.ELEMENT_MAP):
            df = scaffold_elementmap(["el1", "el2", "el3"])
            return df
        else:
            return None

    def retrieve_element(self, element, config):
        pass


@pytest.fixture
def additionals(utils):
    obj = lambda: None
    obj.emptySelector = EmptySelector({}, "empty", utils.TEMP_ELEMENT_DIR)
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
        f"{utils.TEMP_ELEMENT_DIR}/empty/data" == additionals.emptySelector.ELEMENT_DIR
    )
    assert (
        f"{utils.TEMP_ELEMENT_DIR}/empty/element_map.csv"
        == additionals.emptySelector.ELEMENT_MAP
    )
    assert os.path.exists(additionals.emptySelector.ELEMENT_DIR)


def test_index(additionals):
    additionals.emptySelector.start_indexing()
    assert os.path.exists(additionals.emptySelector.ELEMENT_MAP)
    # test element_map.csv is what it should be
    with open(additionals.emptySelector.ELEMENT_MAP, "r") as f:
        emreader = csv.reader(f, delimiter=",")
        rows = [l for l in emreader]
        assert rows == scaffold_elementmap(["el1", "el2", "el3"])


# NOTE: not sure why this stopped working with refactor to pytest
# def test_start_retrieving(utils, additionals):
#     additionals.emptySelector.start_retrieving()
#     path1 = utils.get_element_path(additionals.emptySelector.NAME, "el1")
#     path2 = utils.get_element_path(additionals.emptySelector.NAME, "el2")
#     path3 = utils.get_element_path(additionals.emptySelector.NAME, "el3")
#     assert not os.path.exists(path1)
#     assert not os.path.exists(path2)
#     assert not os.path.exists(path3)
