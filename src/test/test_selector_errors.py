import pytest
import os
from lib.common.selector import Selector
from lib.common.etypes import cast_to_etype, Etype
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    SelectorIndexError,
    EtypeCastError,
)
from test.utils import scaffold_elementmap


class BasicErrorSelector(Selector):
    def __init__(self, *args):
        super().__init__(*args)
        self.retryCount = 0

    def index(self, config):
        error = config["error"] if "error" in config else ""
        if error == "index":
            raise SelectorIndexError("test")
        else:
            elements = ["skip", "retry3", "retryN", "pass"]
            return scaffold_elementmap(elements)

    def retrieve_element(self, element, config):
        if element["id"] == "skip":
            raise ElementShouldSkipError("test")
        elif element["id"] == "retry3" and self.retryCount < 3:
            self.retryCount += 1
            raise ElementShouldRetryError("test")
        elif element["id"] == "retryN":
            raise ElementShouldRetryError("test")
        else:
            pass


class RetrieveErrorSelector(BasicErrorSelector):
    def retrieve_element(self, element, config):
        super().retrieve_element(element, config)
        with open(f"{element['base']}/out.txt", "w") as f:
            f.write("something")


class BadIndexSelector(Selector):
    def index(self, config):
        # fails to return a dataframe
        pass

    def retrieve_element(self, element, config):
        pass


@pytest.fixture
def additionals(utils):
    obj = lambda: None
    indexModule = "indexErrorSelector"
    indexConfig = {"error": "index"}
    obj.indexErrorSelector = BasicErrorSelector(
        indexConfig, indexModule, utils.TEMP_ELEMENT_DIR
    )

    castModule = "castErrorSelector"
    castConfig = {}
    obj.castErrorSelector = BasicErrorSelector(
        castConfig, castModule, utils.TEMP_ELEMENT_DIR
    )

    retrieveModule = "retrieveErrorSelector"
    retrieveConfig = {}
    obj.retrieveErrorSelector = RetrieveErrorSelector(
        retrieveConfig, retrieveModule, utils.TEMP_ELEMENT_DIR
    )
    yield obj
    utils.cleanup()


def test_index_error(additionals):
    with pytest.raises(SelectorIndexError, match="Selector index failed - test"):
        additionals.indexErrorSelector.start_indexing()


def test_retrieve_skip_error(additionals):
    with pytest.raises(ElementShouldSkipError, match="test - skipping element"):
        additionals.castErrorSelector.retrieve_element({"id": "skip"}, {})


def test_retrieve_retry_error(additionals):
    with pytest.raises(ElementShouldRetryError, match="test - attempt retry"):
        additionals.castErrorSelector.retrieve_element({"id": "retryN"}, {})


def test_integration_1(utils, additionals):
    assert additionals.castErrorSelector.retryCount == 0
    additionals.castErrorSelector.start_indexing()
    additionals.castErrorSelector.start_retrieving()

    skip_path = utils.get_element_path("castErrorSelector", "skip")
    assert not os.path.exists(skip_path)

    retryn_path = utils.get_element_path("castErrorSelector", "retryN")
    assert not os.path.exists(retryn_path)

    retry3_path = utils.get_element_path("castErrorSelector", "retry3")
    assert additionals.castErrorSelector.retryCount == 3
    assert not os.path.exists(retry3_path)

    pass_path = utils.get_element_path("castErrorSelector", "pass")
    assert not os.path.exists(pass_path)


def test_integration_2(utils, additionals):
    additionals.retrieveErrorSelector.start_indexing()
    additionals.retrieveErrorSelector.start_retrieving()

    skip_path = utils.get_element_path("retrieveErrorSelector", "skip")
    assert not os.path.exists(skip_path)

    retryn_path = utils.get_element_path("retrieveErrorSelector", "retryN")
    assert not os.path.exists(retryn_path)

    retry3_path = utils.get_element_path("retrieveErrorSelector", "retry3")
    assert additionals.retrieveErrorSelector.retryCount == 3
    assert os.path.exists(retry3_path)

    pass_path = utils.get_element_path("retrieveErrorSelector", "pass")
    assert os.path.exists(pass_path)

    etype = cast_to_etype(retry3_path, Etype.Any)
    expected = {
        "base": retry3_path,
        "etype": Etype.Any,
        "media": {"all": [f"{retry3_path}/out.txt"]},
    }
    assert utils.dictsEqual(etype, expected)
