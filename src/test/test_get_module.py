from lib.common.get_module import get_module
import unittest


class TestGetModule(unittest.TestCase):
    def test_faulty_module(self):
        with self.assertRaises(ModuleNotFoundError):
            get_module('selector', "smth")

        with self.assertRaises(ModuleNotFoundError):
            get_module('analyser', "smth")

        with self.assertRaisesRegex(ImportError,"must be 'selector' or 'analyser'"):
            get_module('neitherthing', "smth")

