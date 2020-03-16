import pytest
import os
import json
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.exceptions import InvalidAnalyserElements, InvalidCarry
from lib.common.etypes import Etype
from lib.common.mtmodule import MTModule
from lib.common.storage import LocalStorage


class EmptyAnalyser(Analyser):
    def analyse_element(self, element, config):
        raise Exception("is the user-defined func!")


class TxtCopyAnalyser(Analyser):
    def analyse_element(self, element, config):
        """ just copy over all media in 'any' """
        for f in element.paths:
            # only copy over txt files
            if f.suffix != ".txt":
                return
            with open(f, "r") as reader:
                contents = reader.readlines()
            txt = Path("/tmp/copy.txt")
            with open(txt, "w+") as writer:
                writer.writelines(contents)

            element.paths = [txt]
            return element


# TODO: test casting errors via an analyser with explicit etype
@pytest.fixture
def additionals(utils):
    obj = lambda: None
    obj.maxDiff = None
    obj.emptyAnalyserName = "empty"
    obj.WHITELIST = ["sel1/an1", "sel1/an2", "sel2"]
    obj.sel1 = "sel1"
    obj.sel2 = "sel2"
    obj.sel1_elements = ["el1", "el2"]
    obj.sel2_elements = ["el4", "el5", "el6"]

    utils.scaffold_empty(obj.sel1, elements=obj.sel1_elements, analysers=["an1", "an2"])
    utils.scaffold_empty(obj.sel2, elements=obj.sel2_elements)
    os.rmdir(utils.get_element_path(obj.sel1, "el1", analyser="an2"))

    obj.config = {"elements_in": obj.WHITELIST}
    obj.emptyAnalyser = EmptyAnalyser(
        obj.config,
        obj.emptyAnalyserName,
        storage=LocalStorage(folder=utils.TEMP_ELEMENT_DIR),
    )
    yield obj
    utils.cleanup()


def test_selector_imports():
    assert type(Analyser) == type(MTModule)


def test_cannot_instantiate(utils):
    with pytest.raises(TypeError):
        Analyser({}, "empty", utils.TEMP_ELEMENT_DIR)


def test_init(additionals):
    assert additionals.config == additionals.emptyAnalyser.config


def test_analyse(utils, additionals):
    config = {"elements_in": ["sel1"]}
    dummyName = "dummyAnalyser"
    checkUserExceptionAnalyser = EmptyAnalyser(
        {**config, "dev": True}, "empty", LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
    )
    dummyAnalyser = TxtCopyAnalyser(
        config, dummyName, LocalStorage(folder=utils.TEMP_ELEMENT_DIR)
    )
    # test it calls the user-defined `analyse_element`
    # with pytest.raises(Exception, match="is the user-defined func!"):
    #     checkUserExceptionAnalyser.start_analysing(in_parallel=False)
    # try again with a text el mocking selection completed
    # TODO: fix these tests- adding casting throws errors in some cases, as well as extra log.
    for el in additionals.sel1_elements:
        with open(
            f"{dummyAnalyser.disk.base_dir}/sel1/{dummyAnalyser.disk.RETRIEVED_EXT}/{el}/anitem.txt",
            "w+",
        ) as f:
            f.write("Hello")
    dummyAnalyser.start_analysing(in_parallel=False)
    # confirm txt has carried
    for el in additionals.sel1_elements:
        with open(
            f"{dummyAnalyser.disk.base_dir}/sel1/{dummyAnalyser.disk.ANALYSED_EXT}/{dummyName}/{el}/copy.txt",
            "r",
        ) as f:
            lines = f.readlines()
            assert len(lines) == 1
            assert lines[0] == "Hello"
