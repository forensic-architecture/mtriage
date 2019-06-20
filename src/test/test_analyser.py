from lib.common.analyser import Analyser
from lib.common.exceptions import InvalidAnalyserElements
from lib.common.etypes import Etype
from test.utils import *
from abc import ABC
import os
import shutil
import unittest
import pytest
import operator
from lib.common.mtmodule import MTModule
from test.utils import listOfDictsEqual


class EmptyAnalyser(Analyser):
    def analyse_element(self, element, config):
        pass


# TODO: test casting errors via an analyser with explicit etype


class TestAnalyser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.emptyAnalyserName = "empty"
        self.WHITELIST = ["sel1/an1", "sel1/an2", "sel2"]
        scaffold_empty("sel1", elements=["el1", "el2"], analysers=["an1", "an2"])
        os.rmdir(get_element_path("sel1", "el1", analyser="an2"))
        scaffold_empty("sel2", elements=["el4", "el5", "el6"])

        self.CONFIG = {"elements_in": self.WHITELIST}
        self.emptyAnalyser = EmptyAnalyser(
            self.CONFIG, self.emptyAnalyserName, TEMP_ELEMENT_DIR
        )

    @classmethod
    def tearDownClass(self):
        cleanup()

    def test_selector_imports(self):
        self.assertTrue(type(Analyser) == type(MTModule))

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Analyser({}, "empty", TEMP_ELEMENT_DIR)

    def test_init(self):
        self.assertEqual(self.CONFIG, self.emptyAnalyser.CONFIG)

    def test_get_in_cmps(self):
        paths = self.emptyAnalyser._Analyser__get_in_cmps()
        self.assertEqual(paths[0][0], "sel1")
        self.assertEqual(paths[0][1], "an1")
        self.assertEqual(paths[1][0], "sel1")
        self.assertEqual(paths[1][1], "an2")
        self.assertEqual(paths[2][0], "sel2")

    def test_get_all_media(self):
        cmpDict = {
            "sel1": {
                f"{Analyser.DATA_EXT}": {
                    "el1": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el1",
                    "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el2",
                },
                f"{Analyser.DERIVED_EXT}": {
                    "an1": {
                        "el1": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                        "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                    },
                    "an2": {
                        "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"
                    },
                },
            },
            "sel2": {
                f"{Analyser.DATA_EXT}": {
                    "el4": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
                    "el5": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
                    "el6": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
                },
                f"{Analyser.DERIVED_EXT}": {},
            },
        }
        mediaDict = self.emptyAnalyser._Analyser__get_all_media()
        self.assertTrue(dictsEqual(cmpDict, mediaDict))

    def test_get_out_dir(self):
        out_dir = self.emptyAnalyser._Analyser__get_out_dir("sel1")
        self.assertEqual(
            out_dir,
            f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}",
        )

    def test_cast_elements(self):
        print("WERUUU")
        # setup
        sel1an1_element_dict = {
            "el1": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
            "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
        }
        sel1an2_element_dict = {
            "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"
        }
        sel2_element_dict = {
            "el4": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
            "el5": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
            "el6": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
        }
        sel1outdir = (
            f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}"
        )
        sel2outdir = (
            f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}"
        )
        sel1_base = f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}"
        sel2_base = f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}"

        with self.assertRaisesRegex(
            InvalidAnalyserElements, "elements_in you specified could not be cast"
        ):
            sel1an1_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
                sel1an1_element_dict, sel1outdir
            )

        with self.assertRaisesRegex(
            InvalidAnalyserElements, "elements_in you specified could not be cast"
        ):
            sel1an2_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
                sel1an2_element_dict, sel1outdir
            )

        with self.assertRaisesRegex(
            InvalidAnalyserElements, "elements_in you specified could not be cast"
        ):
            sel2_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
                sel2_element_dict, sel2outdir
            )

        for el in ["el4", "el5", "el6"]:
            with open(f"{get_element_path('sel2', el)}/out.txt", "w") as f:
                f.write("analysed")

        sel2expected = [
            {
                "id": "el4",
                "base": f"{sel2_base}/el4",
                "dest": f"{sel2outdir}/el4",
                "etype": Etype.Any,
                "media": {"all": [f"{sel2_base}/el4/out.txt"]},
            },
            {
                "id": "el5",
                "base": f"{sel2_base}/el5",
                "dest": f"{sel2outdir}/el5",
                "etype": Etype.Any,
                "media": {"all": [f"{sel2_base}/el5/out.txt"]},
            },
            {
                "id": "el6",
                "base": f"{sel2_base}/el6",
                "dest": f"{sel2outdir}/el6",
                "etype": Etype.Any,
                "media": {"all": [f"{sel2_base}/el6/out.txt"]},
            },
        ]
        sel2_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
            sel2_element_dict, sel2outdir
        )
        self.assertTrue(listOfDictsEqual(sel2expected, sel2_cast_elements))

        for el in ["el1", "el2"]:
            with open(
                f"{get_element_path('sel1', el, analyser='an1')}/out.txt", "w"
            ) as f:
                f.write("analysed")

        sel1an1base = f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1"
        sel1an1expected = [
            {
                "id": "el1",
                "base": f"{sel1an1base}/el1",
                "dest": f"{sel1outdir}/el1",
                "etype": Etype.Any,
                "media": {"all": [f"{sel1an1base}/el1/out.txt"]},
            },
            {
                "id": "el2",
                "base": f"{sel1an1base}/el2",
                "dest": f"{sel1outdir}/el2",
                "etype": Etype.Any,
                "media": {"all": [f"{sel1an1base}/el2/out.txt"]},
            },
        ]

        sel1an1_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
            sel1an1_element_dict, sel1outdir
        )
        self.assertTrue(listOfDictsEqual(sel1an1expected, sel1an1_cast_elements))

        with open(
            f"{get_element_path('sel1', 'el2', analyser='an2')}/out.txt", "w"
        ) as f:
            f.write("analysed")

        sel1an2base = f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2"
        sel1an2expected = [
            {
                "id": "el2",
                "base": f"{sel1an2base}/el2",
                "dest": f"{sel1outdir}/el2",
                "etype": Etype.Any,
                "media": {"all": [f"{sel1an2base}/el2/out.txt"]},
            }
        ]

        sel1an2_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
            sel1an2_element_dict, sel1outdir
        )
        self.assertTrue(listOfDictsEqual(sel1an2expected, sel1an2_cast_elements))

        media = {
            "sel1": {
                f"{Analyser.DATA_EXT}": {
                    "el1": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el1",
                    "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el2",
                },
                f"{Analyser.DERIVED_EXT}": {
                    "an1": {
                        "el1": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                        "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                    },
                    "an2": {
                        "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"
                    },
                },
            },
            "sel2": {
                f"{Analyser.DATA_EXT}": {
                    "el4": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
                    "el5": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
                    "el6": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
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
                "media": {"all": [f"{sel1an1base}/el1/out.txt"]},
            },
            {
                "id": "el2",
                "base": f"{sel1an1base}/el2",
                "dest": f"{sel1outdir}/el2",
                "etype": Etype.Any,
                "media": {"all": [f"{sel1an1base}/el2/out.txt"]},
            },
            {
                "id": "el2",
                "base": f"{sel1an2base}/el2",
                "dest": f"{sel1outdir}/el2",
                "etype": Etype.Any,
                "media": {"all": [f"{sel1an2base}/el2/out.txt"]},
            },
            {
                "id": "el4",
                "base": f"{sel2_base}/el4",
                "dest": f"{sel2outdir}/el4",
                "etype": Etype.Any,
                "media": {"all": [f"{sel2_base}/el4/out.txt"]},
            },
            {
                "id": "el5",
                "base": f"{sel2_base}/el5",
                "dest": f"{sel2outdir}/el5",
                "etype": Etype.Any,
                "media": {"all": [f"{sel2_base}/el5/out.txt"]},
            },
            {
                "id": "el6",
                "base": f"{sel2_base}/el6",
                "dest": f"{sel2outdir}/el6",
                "etype": Etype.Any,
                "media": {"all": [f"{sel2_base}/el6/out.txt"]},
            },
        ]

        elements = self.emptyAnalyser._Analyser__get_in_elements(media)
        self.assertTrue(listOfDictsEqual(elements, expected))
