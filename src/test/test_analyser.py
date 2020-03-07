import pytest
import os
import json
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.exceptions import InvalidAnalyserElements, InvalidCarry
from lib.common.etypes import Etype
from lib.common.mtmodule import MTModule


class EmptyAnalyser(Analyser):
    def analyse_element(self, element, config):
        pass


class TxtCopyAnalyser(Analyser):
    def analyse_element(self, element, config):
        """ just copy over all media in 'any' """
        for med in element["media"]["any"]:
            f = Path(med)
            # only copy over txt files
            if f.suffix != ".txt":
                return
            fname = f.name
            with open(med, "r") as reader:
                contents = reader.readlines()
            dest = f"{element['dest']}/{fname}"
            with open(dest, "a") as writer:
                writer.writelines(contents)


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
    os.rmdir(utils.get_element_path(obj.sel1, "el1", analyser="an2"))
    utils.scaffold_empty(obj.sel2, elements=obj.sel2_elements)

    obj.CONFIG = {"elements_in": obj.WHITELIST}
    obj.emptyAnalyser = EmptyAnalyser(
        obj.CONFIG, obj.emptyAnalyserName, utils.TEMP_ELEMENT_DIR
    )
    yield obj
    utils.cleanup()


def test_selector_imports():
    assert type(Analyser) == type(MTModule)


def test_cannot_instantiate(utils):
    with pytest.raises(TypeError):
        Analyser({}, "empty", utils.TEMP_ELEMENT_DIR)


def test_init(additionals):
    assert additionals.CONFIG == additionals.emptyAnalyser.CONFIG


def test_get_in_cmps(additionals):
    paths = additionals.emptyAnalyser._Analyser__get_in_cmps()
    assert paths[0][0] == "sel1"
    assert paths[0][1] == "an1"
    assert paths[1][0] == "sel1"
    assert paths[1][1] == "an2"
    assert paths[2][0] == "sel2"


def test_get_all_media(utils, additionals):
    cmpDict = {
        "sel1": {
            f"{Analyser.DATA_EXT}": {
                "el1": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el1",
                "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el2",
            },
            f"{Analyser.DERIVED_EXT}": {
                "an1": {
                    "el1": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                    "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                },
                "an2": {
                    "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"
                },
            },
        },
        "sel2": {
            f"{Analyser.DATA_EXT}": {
                "el4": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
                "el5": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
                "el6": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
            },
            f"{Analyser.DERIVED_EXT}": {},
        },
    }
    mediaDict = additionals.emptyAnalyser._Analyser__get_all_media()
    assert utils.dictsEqual(cmpDict, mediaDict)


def test_get_out_dir(utils, additionals):
    out_dir = additionals.emptyAnalyser._Analyser__get_out_dir("sel1")
    assert (
        out_dir
        == f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/{additionals.emptyAnalyserName}"
    )


def test_cast_elements(utils, additionals):
    # setup
    sel1an1_element_dict = {
        "el1": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
        "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
    }
    sel1an2_element_dict = {
        "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"
    }
    sel2_element_dict = {
        "el4": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
        "el5": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
        "el6": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
    }
    sel1outdir = f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/{additionals.emptyAnalyserName}"
    sel2outdir = f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DERIVED_EXT}/{additionals.emptyAnalyserName}"
    sel1_base = f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}"
    sel2_base = f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}"

    with pytest.raises(
        InvalidAnalyserElements, match="elements_in you specified could not be cast"
    ):
        sel1an1_cast_elements = additionals.emptyAnalyser._Analyser__cast_elements(
            sel1an1_element_dict, sel1outdir
        )

    with pytest.raises(
        InvalidAnalyserElements, match="elements_in you specified could not be cast"
    ):
        sel1an2_cast_elements = additionals.emptyAnalyser._Analyser__cast_elements(
            sel1an2_element_dict, sel1outdir
        )

    with pytest.raises(
        InvalidAnalyserElements, match="elements_in you specified could not be cast"
    ):
        sel2_cast_elements = additionals.emptyAnalyser._Analyser__cast_elements(
            sel2_element_dict, sel2outdir
        )

    for el in ["el4", "el5", "el6"]:
        with open(f"{utils.get_element_path('sel2', el)}/out.txt", "w") as f:
            f.write("analysed")

    sel2expected = [
        {
            "id": "el4",
            "base": f"{sel2_base}/el4",
            "dest": f"{sel2outdir}/el4",
            "etype": Etype.Any,
            "media": {"any": [f"{sel2_base}/el4/out.txt"]},
        },
        {
            "id": "el5",
            "base": f"{sel2_base}/el5",
            "dest": f"{sel2outdir}/el5",
            "etype": Etype.Any,
            "media": {"any": [f"{sel2_base}/el5/out.txt"]},
        },
        {
            "id": "el6",
            "base": f"{sel2_base}/el6",
            "dest": f"{sel2outdir}/el6",
            "etype": Etype.Any,
            "media": {"any": [f"{sel2_base}/el6/out.txt"]},
        },
    ]
    sel2_cast_elements = additionals.emptyAnalyser._Analyser__cast_elements(
        sel2_element_dict, sel2outdir
    )
    assert utils.listOfDictsEqual(sel2expected, sel2_cast_elements)

    for el in ["el1", "el2"]:
        with open(
            f"{utils.get_element_path('sel1', el, analyser='an1')}/out.txt", "w"
        ) as f:
            f.write("analysed")

    sel1an1base = f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1"
    sel1an1expected = [
        {
            "id": "el1",
            "base": f"{sel1an1base}/el1",
            "dest": f"{sel1outdir}/el1",
            "etype": Etype.Any,
            "media": {"any": [f"{sel1an1base}/el1/out.txt"]},
        },
        {
            "id": "el2",
            "base": f"{sel1an1base}/el2",
            "dest": f"{sel1outdir}/el2",
            "etype": Etype.Any,
            "media": {"any": [f"{sel1an1base}/el2/out.txt"]},
        },
    ]

    sel1an1_cast_elements = additionals.emptyAnalyser._Analyser__cast_elements(
        sel1an1_element_dict, sel1outdir
    )
    assert utils.listOfDictsEqual(sel1an1expected, sel1an1_cast_elements)

    with open(
        f"{utils.get_element_path('sel1', 'el2', analyser='an2')}/out.txt", "w"
    ) as f:
        f.write("analysed")

    sel1an2base = f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2"
    sel1an2expected = [
        {
            "id": "el2",
            "base": f"{sel1an2base}/el2",
            "dest": f"{sel1outdir}/el2",
            "etype": Etype.Any,
            "media": {"any": [f"{sel1an2base}/el2/out.txt"]},
        }
    ]

    sel1an2_cast_elements = additionals.emptyAnalyser._Analyser__cast_elements(
        sel1an2_element_dict, sel1outdir
    )
    assert utils.listOfDictsEqual(sel1an2expected, sel1an2_cast_elements)

    media = {
        "sel1": {
            f"{Analyser.DATA_EXT}": {
                "el1": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el1",
                "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el2",
            },
            f"{Analyser.DERIVED_EXT}": {
                "an1": {
                    "el1": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                    "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                },
                "an2": {
                    "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"
                },
            },
        },
        "sel2": {
            f"{Analyser.DATA_EXT}": {
                "el4": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
                "el5": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
                "el6": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
            },
            f"{Analyser.DERIVED_EXT}": {},
        },
    }

    expected = [
        {
            "id": "el1",
            "base": f"{sel1an1base}/el1",
            "dest": f"{sel1outdir}/el1",
            "etype": Etype.Any,
            "media": {"any": [f"{sel1an1base}/el1/out.txt"]},
        },
        {
            "id": "el2",
            "base": f"{sel1an1base}/el2",
            "dest": f"{sel1outdir}/el2",
            "etype": Etype.Any,
            "media": {"any": [f"{sel1an1base}/el2/out.txt"]},
        },
        {
            "id": "el2",
            "base": f"{sel1an2base}/el2",
            "dest": f"{sel1outdir}/el2",
            "etype": Etype.Any,
            "media": {"any": [f"{sel1an2base}/el2/out.txt"]},
        },
        {
            "id": "el4",
            "base": f"{sel2_base}/el4",
            "dest": f"{sel2outdir}/el4",
            "etype": Etype.Any,
            "media": {"any": [f"{sel2_base}/el4/out.txt"]},
        },
        {
            "id": "el5",
            "base": f"{sel2_base}/el5",
            "dest": f"{sel2outdir}/el5",
            "etype": Etype.Any,
            "media": {"any": [f"{sel2_base}/el5/out.txt"]},
        },
        {
            "id": "el6",
            "base": f"{sel2_base}/el6",
            "dest": f"{sel2outdir}/el6",
            "etype": Etype.Any,
            "media": {"any": [f"{sel2_base}/el6/out.txt"]},
        },
    ]

    elements = additionals.emptyAnalyser._Analyser__get_in_elements(media)
    assert utils.listOfDictsEqual(elements, expected)


def analyse(utils, additionals):
    config = {"elements_in": ["sel1"]}
    dummyName = "dummyAnalyser"
    dummyAnalyser = TxtCopyAnalyser(config, dummyName, utils.TEMP_ELEMENT_DIR)
    # confirm empty folder throws error
    with pytest.raises(InvalidAnalyserElements):
        dummyAnalyser.start_analysing()
    # try again with a text el mocking selection completed
    txtfile_name = "anitem.txt"
    for el in additionals.sel1_elements:
        with open(
            f"{dummyAnalyser.BASE_DIR}/sel1/{Analyser.DATA_EXT}/{el}/{txtfile_name}",
            "w+",
        ) as f:
            f.write("Hello")
    dummyAnalyser.start_analysing()
    # confirm txt has carried
    for el in additionals.sel1_elements:
        with open(
            f"{dummyAnalyser.BASE_DIR}/sel1/{Analyser.DERIVED_EXT}/{dummyName}/{el}/{txtfile_name}",
            "r",
        ) as f:
            lines = f.readlines()
            assert len(lines) == 1
            assert lines[0] == "Hello"


def write_dummies(base, els, name):
    txtfile_name = f"{name}.txt"
    json_name = f"{name}.json"
    rtf_name = f"{name}.rtf"
    for el in els:
        el_dir = f"{base}/{el}"
        with open(f"{el_dir}/{txtfile_name}", "w+",) as f:
            f.write("Hello")
        with open(f"{el_dir}/{json_name}", "w+") as f:
            json.dump({"empty": "json"}, f)
        with open(f"{el_dir}/{rtf_name}", "w+") as f:
            f.write("This is an RTF.")


def carry_elements(utils, additionals):
    """ If a "carry" List or str attribute is provided in an analyser config, then analysis should carry elements that
    match each of the glob strings provided over to the analysed element. """

    carry_invalid_config = {"elements_in": ["sel1"], "carry": 123}
    invalidCarryingAnalyser = TxtCopyAnalyser(
        carry_invalid_config, "CarryingAnalyserInvalid", utils.TEMP_ELEMENT_DIR
    )
    # write txt files
    dummy_name = "anitem"
    write_dummies(
        f"{invalidCarryingAnalyser.BASE_DIR}/sel1/{Analyser.DATA_EXT}",
        additionals.sel1_elements,
        dummy_name,
    )

    with pytest.raises(InvalidCarry):
        invalidCarryingAnalyser.start_analysing(in_parallel=False)

    carry_txt_config = {**carry_invalid_config, "carry": "*.json"}
    txtCarryingAnalyserSingle = TxtCopyAnalyser(
        carry_txt_config, "txtCarryingAnalyserSingle", utils.TEMP_ELEMENT_DIR
    )
    txtCarryingAnalyserSingle.start_analysing(in_parallel=False)
    # test that JSONs carried
    for el in additionals.sel1_elements:
        el_dir = f"{txtCarryingAnalyserSingle.BASE_DIR}/sel1/{Analyser.DERIVED_EXT}/txtCarryingAnalyserSingle/{el}"
        with open(f"{el_dir}/{dummy_name}.json", "r") as f:
            data = json.load(f)
            assert data["empty"] == "json"


def carry_elements_list(utils, additionals):
    listCarryingAnalyser = TxtCopyAnalyser(
        {"elements_in": ["sel1"], "carry": ["*.json", "*.rtf"]},
        "listCarryingAnalyser",
        utils.TEMP_ELEMENT_DIR,
    )

    dummy_name = "anitem"
    write_dummies(
        f"{listCarryingAnalyser.BASE_DIR}/sel1/{Analyser.DATA_EXT}",
        additionals.sel1_elements,
        dummy_name,
    )

    listCarryingAnalyser.start_analysing(in_parallel=False)

    # test that JSONs and RTFs carried
    for el in additionals.sel1_elements:
        el_dir = f"{listCarryingAnalyser.BASE_DIR}/sel1/{Analyser.DERIVED_EXT}/listCarryingAnalyser/{el}"
        with open(f"{el_dir}/{dummy_name}.json", "r") as f:
            data = json.load(f)
            assert data["empty"] == "json"
        with open(f"{el_dir}/{dummy_name}.rtf", "r") as f:
            lines = f.readlines()
            assert len(lines) == 1
            assert lines[0] == "This is an RTF."
