from lib.common.selector import Selector
from test.utils import scaffold_elementmap
from abc import ABC
import os
import csv
import shutil
import unittest
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    SelectorIndexError,
)
from test.utils import TEMP_ELEMENT_DIR, scaffold_empty, cleanup


class EmptySelector(Selector):
    def index(self, config):
        if not os.path.exists(self.ELEMENT_MAP):
            df = scaffold_elementmap(["el1", "el2", "el3"])
            return df
        else:
            return None

    def retrieve_element(self, element, config):
        pass


class TestEmptySelector(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.emptySelector = EmptySelector({}, "empty", TEMP_ELEMENT_DIR)

    @classmethod
    def tearDownClass(self):
        cleanup()

    def test_selector_imports(self):
        self.assertTrue(type(Selector) == type(ABC))

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Selector({}, "empty", TEMP_ELEMENT_DIR)

    def test_init(self):
        self.assertEqual(TEMP_ELEMENT_DIR, self.emptySelector.BASE_DIR)
        self.assertEqual("empty", self.emptySelector.NAME)
        self.assertEqual(f"{TEMP_ELEMENT_DIR}/empty", self.emptySelector.DIR)
        self.assertEqual(
            f"{TEMP_ELEMENT_DIR}/empty/data", self.emptySelector.ELEMENT_DIR
        )
        self.assertEqual(
            f"{TEMP_ELEMENT_DIR}/empty/element_map.csv", self.emptySelector.ELEMENT_MAP
        )
        self.assertTrue(os.path.exists(self.emptySelector.ELEMENT_DIR))

    def test_index(self):
        self.emptySelector.start_indexing()
        self.assertTrue(os.path.exists(self.emptySelector.ELEMENT_MAP))
        # test element_map.csv is what it should be
        with open(self.emptySelector.ELEMENT_MAP, "r") as f:
            emreader = csv.reader(f, delimiter=",")
            rows = [l for l in emreader]
            self.assertEqual(rows, scaffold_elementmap(["el1", "el2", "el3"]))

    def test_start_retrieving(self):
        self.emptySelector.start_retrieving()
        # TODO: test something
