from lib.common.selector import Selector
import os
import unittest
from lib.common.etypes import cast_to_etype, Etype
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    SelectorIndexError,
    EtypeCastError,
)
from test.utils import (
    TEMP_ELEMENT_DIR,
    scaffold_empty,
    scaffold_elementmap,
    cleanup,
    get_element_path,
    dictsEqual,
)


class BasicErrorSelector(Selector):
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
        if element["id"] == "skip":
            raise ElementShouldSkipError("test")
        elif element["id"] == "retry3" and self.retryCount < 3:
            self.retryCount += 1
            raise ElementShouldRetryError("test")
        elif element["id"] == "retryN":
            raise ElementShouldRetryError("test")
        else:
            pass

class RetrieveErrorSelector(BasicErrorSelector):
    def retrieve_element(self, element, config):
        super().retrieve_element(element, config)
        with open(f"{element['base']}/out.txt", "w") as f:
            f.write("something")


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
        self.indexErrorSelector = BasicErrorSelector(
            indexConfig, indexModule, TEMP_ELEMENT_DIR
        )

        castModule = "castErrorSelector"
        castConfig = {}
        self.castErrorSelector = BasicErrorSelector(
            castConfig, castModule, TEMP_ELEMENT_DIR
        )

        retrieveModule = "retrieveErrorSelector"
        retrieveConfig = {}
        self.retrieveErrorSelector = RetrieveErrorSelector(
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
            self.castErrorSelector.retrieve_element({"id": "skip"}, {})

    def test_retrieve_retry_error(self):
        with self.assertRaisesRegex(ElementShouldRetryError, "test - attempt retry"):
            self.castErrorSelector.retrieve_element({"id": "retryN"}, {})

    def test_integration_1(self):
        self.assertEqual(self.castErrorSelector.retryCount, 0)
        self.castErrorSelector.start_indexing()
        self.castErrorSelector.start_retrieving()

        skip_path = get_element_path("castErrorSelector", "skip")
        self.assertFalse(os.path.exists(skip_path))

        retryn_path = get_element_path("castErrorSelector", "retryN")
        self.assertFalse(os.path.exists(retryn_path))

        retry3_path = get_element_path("castErrorSelector", "retry3")
        self.assertEqual(self.castErrorSelector.retryCount, 3)
        self.assertFalse(os.path.exists(retry3_path))

        pass_path = get_element_path("castErrorSelector", "pass")
        self.assertFalse(os.path.exists(pass_path))

    def test_integration_2(self):
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

        etype = cast_to_etype(retry3_path, Etype.Any)
        expected = {
            "base": retry3_path,
            "etype": Etype.Any,
            "media": {
                "all":[f"{retry3_path}/out.txt"]
            }
        }
        self.assertTrue(dictsEqual(etype, expected))

    # def test_etype_cast_error(self):
    #     with self.assertRaisesRegex(EtypeCastError, "Failed to cast - retrieved element was not Etype.Any"):
    #         # TODO:
    #         pass
