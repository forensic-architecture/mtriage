import pytest
import os
from lib.common.analyser import Analyser
from test.test_analyser import EmptyAnalyser
from lib.common.storage import LocalStorage
from lib.common.etypes import LocalElement
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    InvalidAnalyserConfigError,
    MTriageStorageCorruptedError,
    InvalidAnalyserElements,
)


class ErrorThrowingAnalyser(Analyser):
    def __init__(self, *args):
        super().__init__(*args)
        self.retryCount = 0

    def analyse_element(self, element, config):
        if element.id == "skip":
            raise ElementShouldSkipError("test")
        elif element.id == "retry3" and self.retryCount < 3:
            self.retryCount += 1
            raise ElementShouldRetryError("test")
        elif element.id == "retryN":
            raise ElementShouldRetryError("test")
        else:
            pass


@pytest.fixture
def additionals(utils):
    obj = lambda: None
    obj.selname = "stub_sel"
    elements = ["skip", "retry3", "retryN", "pass"]
    utils.scaffold_empty(obj.selname, elements=elements)
    for element in elements:
        with open(f"{utils.get_element_path(obj.selname, element)}/out.txt", "w") as f:
            f.write("something")

    goodConfig = {"elements_in": [obj.selname]}

    obj.an = ErrorThrowingAnalyser(
        goodConfig, "analyserErrorSelector", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
    )
    yield obj
    utils.cleanup()


def test_analyse_skip_error(additionals):
    with pytest.raises(ElementShouldSkipError, match="test - skipping element"):
        additionals.an.analyse_element(LocalElement(id="skip"), {})


def test_analyse_retry_error(additionals):
    with pytest.raises(ElementShouldRetryError, match="test - attempt retry"):
        additionals.an.analyse_element(LocalElement(id="retryN"), {})


def test_bad_init_error(utils):
    bad0 = {}
    bad1 = {"elements_in": []}
    bad2 = {"elements_in": None}
    good = {"elements_in": ["selname"]}

    with pytest.raises(
        InvalidAnalyserConfigError,
        match="must contain an 'elements_in' indicating the analyser's input",
    ):
        no_elements_in = ErrorThrowingAnalyser(
            bad0, "stub", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
        )

    with pytest.raises(
        InvalidAnalyserConfigError,
        match="The 'elements_in' must be a list containing at least one string",
    ):
        empty_elements_in = ErrorThrowingAnalyser(
            bad1, "stub", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
        )

    with pytest.raises(
        InvalidAnalyserConfigError,
        match="The 'elements_in' must be a list containing at least one string",
    ):
        empty_elements_in = ErrorThrowingAnalyser(
            bad2, "stub", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
        )

    with pytest.raises(
        InvalidAnalyserConfigError, match="You must provide a name for your analyser"
    ):
        badan2 = ErrorThrowingAnalyser(
            good, "", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
        )


def test_integration(utils, additionals):
    assert additionals.an.retryCount == 0
    additionals.an.in_parallel = False

    additionals.an.start_analysing()

    skip_path = utils.get_element_path(
        additionals.selname, "skip", analyser=additionals.an.name
    )
    assert not os.path.exists(skip_path)

    retryn_path = utils.get_element_path(
        additionals.selname, "retryN", analyser=additionals.an.name
    )
    assert not os.path.exists(retryn_path)

    retry3_path = utils.get_element_path(
        additionals.selname, "retry3", analyser=additionals.an.name
    )
    assert additionals.an.retryCount == 3


def test_bad_whitelist(utils):
    badConfig = {"elements_in": ["sel1/an1/el1"]}
    badAn = EmptyAnalyser(
        badConfig, "whitelistErrorAnalyser", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
    )
    with pytest.raises(
        InvalidAnalyserElements, match="'elements_in' you specified does not exist"
    ):
        badAn.start_analysing()
