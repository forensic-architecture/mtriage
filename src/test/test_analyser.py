from lib.common.analyser import Analyser
from lib.common.analyser import paths_to_components
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


class TestAnalyser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.DIR = "../tempdir"
        self.NAME = "empty"
        self.WHITELIST = ["sel1/an1", "sel1/an2", "sel2"]
        os.makedirs(self.DIR)
        os.makedirs(f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el1")
        os.makedirs(f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el2")
        os.makedirs(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1")
        os.makedirs(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2")
        os.makedirs(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el3")
        os.makedirs(f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el4")
        os.makedirs(f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el5")
        os.makedirs(f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el6")
        self.CONFIG = {"elements_in": self.WHITELIST}
        self.emptyAnalyser = EmptyAnalyser(self.CONFIG, self.NAME, self.DIR)

    @classmethod
    def tearDownClass(self):
        self.emptyAnalyser = None
        shutil.rmtree(self.DIR)

    def test_selector_imports(self):
        self.assertTrue(type(Analyser) == type(MTModule))

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Analyser({}, "empty", self.DIR)

    def test_init(self):
        self.assertEqual(self.CONFIG, self.emptyAnalyser.CONFIG)

    def test_paths_to_components(self):
        paths = paths_to_components(self.WHITELIST)
        self.assertEqual(paths[0][0], "sel1")
        self.assertEqual(paths[0][1], "an1")
        self.assertEqual(paths[1][0], "sel1")
        self.assertEqual(paths[1][1], "an2")
        self.assertEqual(paths[2][0], "sel2")

    def test_get_all_media(self):
        cmpDict = {
            "sel1": {
                f"{Analyser.DATA_EXT}": {
                    "el1": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el1",
                    "el2": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el2",
                },
                f"{Analyser.DERIVED_EXT}": {
                    "an1": {
                        "el1": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                        "el2": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                    },
                    "an2": {"el3": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el3"},
                },
            },
            "sel2": {
                f"{Analyser.DATA_EXT}": {
                    "el4": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el4",
                    "el5": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el5",
                    "el6": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el6",
                },
                f"{Analyser.DERIVED_EXT}": {},
            },
        }
        mediaDict = self.emptyAnalyser._Analyser__get_all_media()
        self.assertEqual(cmpDict, mediaDict)

    def test_get_derived_dir(self):
        derived_dir = self.emptyAnalyser._Analyser__get_derived_dir("sel1")
        self.assertEqual(
            derived_dir, f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}"
        )

    # derive elements
    def test_derive_elements(self):
        data_obj = {
            "el1": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el1",
            "el2": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el2",
        }
        outdir = f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}"
        derived_elements = self.emptyAnalyser._Analyser__derive_elements(
            data_obj, outdir
        )
        expected = [
            {
                "id": "el1",
                "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el1",
                "dest": f"{outdir}/el1",
            },
            {
                "id": "el2",
                "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el2",
                "dest": f"{outdir}/el2",
            },
        ]
        self.assertTrue(listOfDictsEqual(derived_elements, expected))

    # get elements
    def test_get_elements(self):

        media = {
            "sel1": {
                f"{Analyser.DATA_EXT}": {
                    "el1": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el1",
                    "el2": f"{self.DIR}/sel1/{Analyser.DATA_EXT}/el2",
                },
                f"{Analyser.DERIVED_EXT}": {
                    "an1": {
                        "el1": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                        "el2": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                    },
                    "an2": {"el3": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el3"},
                },
            },
            "sel2": {
                f"{Analyser.DATA_EXT}": {
                    "el4": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el4",
                    "el5": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el5",
                    "el6": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el6",
                },
                f"{Analyser.DERIVED_EXT}": {},
            },
        }

        expected = [
            {
                "id": "el1",
                "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                "dest": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el1",
            },
            {
                "id": "el2",
                "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                "dest": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el2",
            },
            {
                "id": "el3",
                "derived_dir": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el3",
                "dest": f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el3",
            },
            {
                "id": "el4",
                "derived_dir": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el4",
                "dest": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el4",
            },
            {
                "id": "el5",
                "derived_dir": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el5",
                "dest": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el5",
            },
            {
                "id": "el6",
                "derived_dir": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.DIR}/sel2/{Analyser.DATA_EXT}/el6",
                "dest": f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el6",
            },
        ]

        elements = self.emptyAnalyser._Analyser__get_elements(media)
        self.assertTrue(listOfDictsEqual(elements, expected))

    def test_start_analysing(self):
        self.emptyAnalyser.start_analysing()
        self.assertTrue(
            os.path.exists(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el1")
        )
        self.assertTrue(
            os.path.exists(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el2")
        )
        self.assertTrue(
            os.path.exists(f"{self.DIR}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el3")
        )
        self.assertTrue(
            os.path.exists(f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el4")
        )
        self.assertTrue(
            os.path.exists(f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el5")
        )
        self.assertTrue(
            os.path.exists(f"{self.DIR}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el6")
        )
