from lib.common.selector import Selector
import os
import unittest
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    SelectorIndexError,
)
from test.utils import (
    TEMP_ELEMENT_DIR,
    scaffold_empty,
    scaffold_elementmap,
    cleanup,
    get_element_path,
)
import pandas


class ErrorThrowingSelector(Selector):
    def __init__(self, *args):
        super().__init__(*args)
        self.retryCount = 0

    def index(self, config):
        error = config["error"] if "error" in config else ""
        if error == "index":
            raise SelectorIndexError("test")
        else:
            elements = ["skip", "retry3", "retryN", "pass"]
            return scaffold_elementmap(elements)

    def retrieve_element(self, element, config):
        if element["element_id"] == "skip":
            raise ElementShouldSkipError("test")
        elif element["element_id"] == "retry3" and self.retryCount < 3:
            self.retryCount += 1
            raise ElementShouldRetryError("test")
        elif element["element_id"] == "retryN":
            raise ElementShouldRetryError("test")
        else:
            pass


class BadIndexSelector(Selector):
    def index(self, config):
        # fails to return a dataframe
        pass

    def retrieve_element(self, element, config):
        pass


class TestSelectorErrors(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        indexModule = "indexErrorSelector"
        indexConfig = {"error": "index"}
        self.indexErrorSelector = ErrorThrowingSelector(
            indexConfig, indexModule, TEMP_ELEMENT_DIR
        )

        retrieveModule = "retrieveErrorSelector"
        retrieveConfig = {}
        self.retrieveErrorSelector = ErrorThrowingSelector(
            retrieveConfig, retrieveModule, TEMP_ELEMENT_DIR
        )

    @classmethod
    def tearDownClass(self):
        cleanup()

    def test_index_error(self):
        with self.assertRaisesRegex(SelectorIndexError, "Selector index failed - test"):
            self.indexErrorSelector.start_indexing()

    def test_retrieve_skip_error(self):
        with self.assertRaisesRegex(ElementShouldSkipError, "test - skipping element"):
            self.retrieveErrorSelector.retrieve_element({"element_id": "skip"}, {})

    def test_retrieve_retry_error(self):
        with self.assertRaisesRegex(ElementShouldRetryError, "test - attempt retry"):
            self.retrieveErrorSelector.retrieve_element({"element_id": "retryN"}, {})

    def test_integration(self):
        self.assertEqual(self.retrieveErrorSelector.retryCount, 0)
        self.retrieveErrorSelector.start_indexing()
        self.retrieveErrorSelector.start_retrieving()

        skip_path = get_element_path("retrieveErrorSelector", "skip")
        self.assertFalse(os.path.exists(skip_path))

        retryn_path = get_element_path("retrieveErrorSelector", "retryN")
        self.assertFalse(os.path.exists(retryn_path))

        retry3_path = get_element_path("retrieveErrorSelector", "retry3")
        self.assertEqual(self.retrieveErrorSelector.retryCount, 3)
        self.assertTrue(os.path.exists(retry3_path))

        pass_path = get_element_path("retrieveErrorSelector", "pass")
        self.assertTrue(os.path.exists(pass_path))
