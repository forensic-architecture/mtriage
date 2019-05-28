from lib.common.selector import Selector
from abc import ABC
import pandas as pd
import os
import shutil
import unittest

class EmptySelector(Selector):

    def index(self, config):
        if not os.path.exists(self.SELECT_MAP):
            df = pd.DataFrame([])
            self.index_complete(df , ["Test log."])
        else:
            self.index_complete(None, ["File already exists for index--not running again."])

    def retrieve_row(self, row):
        pass


class TestEmptySelector(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.emptySelector = EmptySelector({}, "empty" , "test")

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.emptySelector.FOLDER)
        self.emptySelector = None
        EmptySelector.ALL_SELECTORS.clear()

    def test_selector_imports(self):
        self.assertTrue(type(Selector) == type(ABC))

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Selector({}, "empty" , "test")

    def test_init(self):
        self.assertEqual("test", self.emptySelector.BASE_FOLDER)
        self.assertEqual("empty", self.emptySelector.NAME)
        self.assertEqual("empty_0", self.emptySelector.ID)
        self.assertEqual(1, len(EmptySelector.ALL_SELECTORS))
        self.assertIn(self.emptySelector.ID, EmptySelector.ALL_SELECTORS)
        self.assertEqual("test/empty", self.emptySelector.FOLDER)
        self.assertEqual("test/empty/data", self.emptySelector.RETRIEVE_FOLDER)
        self.assertEqual("test/empty/select-logs.txt", self.emptySelector.SELECT_LOGS)
        self.assertEqual("test/empty/selected.csv", self.emptySelector.SELECT_MAP)
        self.assertEqual("test/empty/retrieve-logs.txt", self.emptySelector.RETRIEVE_LOGS)
        self.assertTrue(os.path.exists(self.emptySelector.RETRIEVE_FOLDER))

    def test_index_complete(self):
        logs = ["Test log."]
        df = pd.DataFrame(["test1"])
        self.emptySelector.index_complete(df , logs)
        self.assertTrue(os.path.exists(self.emptySelector.SELECT_MAP))
        self.assertTrue(os.path.exists(self.emptySelector.SELECT_LOGS))

    def test_retrieve_row_complete(self):
        self.emptySelector.retrieve_row_complete(True, ["another test log"])
        self.assertTrue(os.path.exists(self.emptySelector.RETRIEVE_LOGS))

    def test_retrieve_all(self):
        self.emptySelector.retrieve_all()
        self.assertTrue(os.path.exists(self.emptySelector.RETRIEVE_LOGS))
