from lib.common.analyser import Analyser
from lib.common.exceptions import InvalidAnalyserElements
from test.utils import *
from abc import ABC
import os
import shutil
import unittest
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
        self.emptyAnalyser = EmptyAnalyser(self.CONFIG, self.emptyAnalyserName, TEMP_ELEMENT_DIR)

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
                    "an2": {"el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"},
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
        self.assertEqual(cmpDict, mediaDict)

    def test_get_out_dir(self):
        out_dir = self.emptyAnalyser._Analyser__get_out_dir("sel1")
        self.assertEqual(
            out_dir, f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}"
        )

    def test_cast_elements(self):
        #setup
        sel1an1_element_dict = {
            "el1": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el1",
            "el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el2",
        }
        sel1an2_element_dict = {"el2": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"}
        sel2_element_dict = {
            "el4": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
            "el5": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
            "el6": f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
        }
        sel1outdir = f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}"
        sel2outdir = f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}"
        sel1_base = f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}"
        sel2_base = f"{TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}"

        with self.assertRaisesRegex(InvalidAnalyserElements, "elements_in you specified could not be cast"):
            sel1an1_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
                sel1an1_element_dict, sel1outdir
            )

        with self.assertRaisesRegex(InvalidAnalyserElements, "elements_in you specified could not be cast"):
            sel1an2_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
                sel1an2_element_dict, sel1outdir
            )

        with self.assertRaisesRegex(InvalidAnalyserElements, "elements_in you specified could not be cast"):
            sel2_cast_elements = self.emptyAnalyser._Analyser__cast_elements(
                sel2_element_dict, sel2outdir
            )

        # TODO: write some files and run again
        sel2expected = [
            # sel2
            {
                "id": "el4",
                "base": f"{sel2_base}/el4",
                "dest": f"{sel2outdir}/el4",
                "media": [f"{sel2_base}/el4/out.txt"]
            },
            {
                "id": "el5",
                "base": f"{sel2_base}/el5",
                "dest": f"{sel2outdir}/el5",
                "media": [f"{sel2_base}/el5/out.txt"]
            },
            {
                "id": "el6",
                "base": f"{sel2_base}/el6",
                "dest": f"{sel2outdir}/el6",
                "media": [f"{sel2_base}/el6/out.txt"]
            },
        ]
        # self.assertTrue(listOfDictsEqual(sel2expected, sel2_cast_elements))

    # # get elements
    # def test_get_elements(self):
    #
    #     media = {
    #         "sel1": {
    #             f"{Analyser.DATA_EXT}": {
    #                 "el1": f"{TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el1",
    #                 "el2": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el2",
    #             },
    #             f"{Analyser.DERIVED_EXT}": {
    #                 "an1": {
    #                     "el1": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
    #                     "el2": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
    #                 },
    #                 "an2": {"el3": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el3"},
    #             },
    #         },
    #         "sel2": {
    #             f"{Analyser.DATA_EXT}": {
    #                 "el4": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el4",
    #                 "el5": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el5",
    #                 "el6": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el6",
    #             },
    #             f"{Analyser.DERIVED_EXT}": {},
    #         },
    #     }
    #
    #     expected = [
    #         {
    #             "id": "el1",
    #             "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}",
    #             "src": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
    #             "dest": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el1",
    #         },
    #         {
    #             "id": "el2",
    #             "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}",
    #             "src": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
    #             "dest": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el2",
    #         },
    #         {
    #             "id": "el3",
    #             "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}",
    #             "src": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el3",
    #             "dest": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el3",
    #         },
    #         {
    #             "id": "el4",
    #             "derived_dir": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}",
    #             "src": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el4",
    #             "dest": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el4",
    #         },
    #         {
    #             "id": "el5",
    #             "derived_dir": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}",
    #             "src": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el5",
    #             "dest": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el5",
    #         },
    #         {
    #             "id": "el6",
    #             "derived_dir": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}",
    #             "src": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el6",
    #             "dest": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el6",
    #         },
    #     ]
    #
    #     elements = self.emptyAnalyser._Analyser__get_elements(media)
    #     self.assertTrue(listOfDictsEqual(elements, expected))
    #
    # def test_start_analysing(self):
    #     self.emptyAnalyser.start_analysing()
    #     self.assertTrue(
    #         os.path.exists(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el1")
    #     )
    #     self.assertTrue(
    #         os.path.exists(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el2")
    #     )
    #     self.assertTrue(
    #         os.path.exists(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el3")
    #     )
    #     self.assertTrue(
    #         os.path.exists(f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el4")
    #     )
    #     self.assertTrue(
    #         os.path.exists(f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el5")
    #     )
    #     self.assertTrue(
    #         os.path.exists(f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.emptyAnalyserName}/el6")
    #     )
