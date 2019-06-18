from lib.common.analyser import Analyser
import os
import unittest
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    InvalidAnalyserConfigError,
)
from test.utils import (
    TEMP_ELEMENT_DIR,
    scaffold_empty,
    scaffold_elementmap,
    cleanup,
    get_element_path,
)
import pandas


class ErrorThrowingAnalyser(Analyser):
    def __init__(self, *args):
        super().__init__(*args)
        self.retryCount = 0

    def analyse_element(self, element, config):
        if element["element_id"] == "skip":
            raise ElementShouldSkipError("test")
        elif element["element_id"] == "retry3" and self.retryCount < 3:
            self.retryCount += 1
            raise ElementShouldRetryError("test")
        elif element["element_id"] == "retryN":
            raise ElementShouldRetryError("test")
        else:
            pass


class TestAnalyserErrors(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.selname = "stub_sel"

        scaffold_empty(self.selname, elements=["skip", "retry3", "retryN", "pass"])
        good = { "elements_in": [ self.selname ] }


        self.an = ErrorThrowingAnalyser(
            good, "analyserErrorSelector", TEMP_ELEMENT_DIR
        )

    @classmethod
    def tearDownClass(self):
        cleanup()

    def test_analyse_skip_error(self):
        with self.assertRaisesRegex(ElementShouldSkipError, "test - skipping element"):
            self.an.analyse_element({"element_id": "skip"}, {})

    def test_analyse_retry_error(self):
        with self.assertRaisesRegex(ElementShouldRetryError, "test - attempt retry"):
            self.an.analyse_element({"element_id": "retryN"}, {})


    def test_bad_init_error(self):
        bad0 = {}
        bad1 = { "elements_in": [] }
        bad2 = { "elements_in": None }
        good = { "elements_in": [ "selname" ] }

        with self.assertRaisesRegex(InvalidAnalyserConfigError, "must contain an 'elements_in' whitelist"):
            no_elements_in = ErrorThrowingAnalyser(
                bad0, "stub", TEMP_ELEMENT_DIR
            )

        with self.assertRaisesRegex(InvalidAnalyserConfigError, "The 'elements_in' whitelist must be a list containing at least one string"):
            empty_elements_in = ErrorThrowingAnalyser(
                bad1, "stub", TEMP_ELEMENT_DIR
            )

        with self.assertRaisesRegex(InvalidAnalyserConfigError, "The 'elements_in' whitelist must be a list containing at least one string"):
            empty_elements_in = ErrorThrowingAnalyser(
                bad2, "stub", TEMP_ELEMENT_DIR
            )

        with self.assertRaisesRegex(InvalidAnalyserConfigError, "You must provide a name for your analyser"):
            badan2 = ErrorThrowingAnalyser(
                good, "", TEMP_ELEMENT_DIR
            )


    # def test_integration(self):
    #     self.assertEqual(self.an.retryCount, 0)
    #     self.an.start_analysing()
    #
    #     skip_path = get_element_path(self.selname, "skip", analyser=self.an.NAME)
    #     self.assertFalse(os.path.exists(skip_path))
    #
    #     retryn_path = get_element_path(self.selname, "retryN", analyser=self.an.NAME)
    #     self.assertFalse(os.path.exists(retryn_path))
    #
    #     retry3_path = get_element_path(self.selname, "retry3", analyser=self.an.NAME)
    #     self.assertEqual(self.an.retryCount, 3)
    #     self.assertTrue(os.path.exists(retry3_path))
    #
    #     pass_path = get_element_path(self.selname, "pass", analyser=self.an.NAME)
    #     self.assertTrue(os.path.exists(pass_path))
