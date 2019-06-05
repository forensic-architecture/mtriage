from lib.common.analyser import Analyser
from lib.common.analyser import paths_to_components
from abc import ABC
import os
import numpy as np
import shutil
import unittest
import operator


class EmptyAnalyser(Analyser):
    def analyse_element(self, element, config):
        pass


class TestAnalyser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.FOLDER = "tempdir"
        self.NAME = "empty"
        self.WHITELIST = ["sel1/an1", "sel1/an2", "sel2"]
        os.makedirs(self.FOLDER)
        os.makedirs(f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el1")
        os.makedirs(f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el2")
        os.makedirs(f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el1")
        os.makedirs(f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el2")
        os.makedirs(f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an2/el3")
        os.makedirs(f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el4")
        os.makedirs(f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el5")
        os.makedirs(f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el6")
        self.CONFIG = {"elements_in": self.WHITELIST}
        self.emptyAnalyser = EmptyAnalyser(self.CONFIG, self.NAME, self.FOLDER)

    @classmethod
    def tearDownClass(self):
        self.emptyAnalyser = None
        EmptyAnalyser.ALL_ANALYSERS.clear()
        shutil.rmtree(self.FOLDER)

    def test_selector_imports(self):
        self.assertTrue(type(Analyser) == type(ABC))

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Analyser({}, "empty", "tempdir")

    def test_init(self):
        self.assertEqual(self.FOLDER, self.emptyAnalyser.FOLDER)
        self.assertEqual("empty", self.emptyAnalyser.NAME)
        self.assertEqual(
            f"{self.FOLDER}/analyser-logs.txt", self.emptyAnalyser.ANALYSER_LOGS
        )
        self.assertEqual("empty_0", self.emptyAnalyser.ID)
        self.assertEqual(1, len(EmptyAnalyser.ALL_ANALYSERS))
        self.assertIn(self.emptyAnalyser.ID, EmptyAnalyser.ALL_ANALYSERS)

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
                    "el1": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el1",
                    "el2": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el2",
                },
                f"{Analyser.DERIVED_EXT}": {
                    "an1": {
                        "el1": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                        "el2": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                    },
                    "an2": {
                        "el3": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an2/el3"
                    },
                },
            },
            "sel2": {
                f"{Analyser.DATA_EXT}": {
                    "el4": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el4",
                    "el5": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el5",
                    "el6": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el6",
                },
                f"{Analyser.DERIVED_EXT}": {},
            },
        }
        mediaDict = self.emptyAnalyser._Analyser__get_all_media()
        self.assertEqual(cmpDict, mediaDict)

    def test_get_derived_folder(self):
        derived_folder = self.emptyAnalyser._Analyser__get_derived_folder("sel1")
        self.assertEqual(
            derived_folder, f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}"
        )

    # derive elements
    def test_derive_elements(self):
        data_obj = {
            "el1": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el1",
            "el2": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el2",
        }
        outfolder = f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}"
        derived_elements = self.emptyAnalyser.derive_elements(data_obj, outfolder)
        expected = [
            {
                "id": "el1",
                "derived_folder": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el1",
                "dest": f"{outfolder}/el1",
            },
            {
                "id": "el2",
                "derived_folder": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el2",
                "dest": f"{outfolder}/el2",
            },
        ]
        self.assertTrue(np.array_equal(derived_elements, expected))

    # get elements
    def test_get_elements(self):

        media = {
            "sel1": {
                f"{Analyser.DATA_EXT}": {
                    "el1": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el1",
                    "el2": f"{self.FOLDER}/sel1/{Analyser.DATA_EXT}/el2",
                },
                f"{Analyser.DERIVED_EXT}": {
                    "an1": {
                        "el1": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                        "el2": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                    },
                    "an2": {
                        "el3": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an2/el3"
                    },
                },
            },
            "sel2": {
                f"{Analyser.DATA_EXT}": {
                    "el4": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el4",
                    "el5": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el5",
                    "el6": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el6",
                },
                f"{Analyser.DERIVED_EXT}": {},
            },
        }

        expected = [
            {
                "id": "el1",
                "derived_folder": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                "dest": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el1",
            },
            {
                "id": "el2",
                "derived_folder": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                "dest": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el2",
            },
            {
                "id": "el3",
                "derived_folder": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/an2/el3",
                "dest": f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el3",
            },
            {
                "id": "el4",
                "derived_folder": f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el4",
                "dest": f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el4",
            },
            {
                "id": "el5",
                "derived_folder": f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el5",
                "dest": f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el5",
            },
            {
                "id": "el6",
                "derived_folder": f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}",
                "src": f"{self.FOLDER}/sel2/{Analyser.DATA_EXT}/el6",
                "dest": f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el6",
            },
        ]

        elements = self.emptyAnalyser._Analyser__get_elements(media)

        print("elements: " + str(elements))
        print("expected: " + str(expected))
        self.assertTrue(np.array_equal(elements, expected))

    def test_run(self):
        self.emptyAnalyser._run(self.CONFIG)
        self.assertTrue(
            os.path.exists(f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el1")
        )
        self.assertTrue(
            os.path.exists(f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el2")
        )
        self.assertTrue(
            os.path.exists(f"{self.FOLDER}/sel1/{Analyser.DERIVED_EXT}/{self.NAME}/el3")
        )
        self.assertTrue(
            os.path.exists(f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el4")
        )
        self.assertTrue(
            os.path.exists(f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el5")
        )
        self.assertTrue(
            os.path.exists(f"{self.FOLDER}/sel2/{Analyser.DERIVED_EXT}/{self.NAME}/el6")
        )
