from lib.common.selector import Selector
from abc import ABC
import pandas as pd
import os
import shutil
import unittest


class EmptySelector(Selector):
    def index(self, config):
        if not os.path.exists(self.ELEMENT_MAP):
            df = pd.DataFrame([{"element_id": "test"}])
            self.logger("Test select log.")
            return df
        else:
            self.logger("File already exists for index--not running again.")
            return None

    def retrieve_element(self, element, config):
        self.logger("Test retrieve log.")


class TestEmptySelector(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.emptySelector = EmptySelector({}, "empty", "test")

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.emptySelector.DIR)
        self.emptySelector = None

    def test_selector_imports(self):
        self.assertTrue(type(Selector) == type(ABC))

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Selector({}, "empty", "test")

    def test_init(self):
        self.assertEqual("test", self.emptySelector.BASE_DIR)
        self.assertEqual("empty", self.emptySelector.NAME)
        self.assertEqual("test/empty", self.emptySelector.DIR)
        self.assertEqual("test/empty/data", self.emptySelector.ELEMENT_DIR)
        self.assertEqual("test/empty/element_map.csv", self.emptySelector.ELEMENT_MAP)
        self.assertTrue(os.path.exists(self.emptySelector.ELEMENT_DIR))

    def test_index(self):
        self.emptySelector.start_indexing()
        self.assertTrue(os.path.exists(self.emptySelector.ELEMENT_MAP))

    def test_start_retrieving(self):
        self.emptySelector.start_retrieving()
        # TODO: test something

    def test_logs(self):
        self.assertTrue(os.path.exists(self.emptySelector._MTModule__LOGS_FILE))
