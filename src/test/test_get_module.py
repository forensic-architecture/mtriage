from lib.common.get_module import get_module
import unittest
import shutil
from os import listdir, makedirs
from os.path import isdir


def make_empty_main_export(pth):
    INIT = 'main = False\n__all__ = ["main"]\n'
    with open(f"{pth}/__init__.py", "w") as f:
        f.write(INIT)


class TestGetModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """ Make imaginary selector and analysers """
        # tests always run from src
        self.EMPTY_SELECTOR = "./lib/selectors/empty"
        self.EMPTY_ANALYSER = "./lib/analysers/empty"

        if isdir(self.EMPTY_SELECTOR):
            shutil.rmtree(self.EMPTY_SELECTOR)
        if isdir(self.EMPTY_ANALYSER):
            shutil.rmtree(self.EMPTY_ANALYSER)

        makedirs(self.EMPTY_SELECTOR)
        make_empty_main_export(self.EMPTY_SELECTOR)
        makedirs(self.EMPTY_ANALYSER)
        make_empty_main_export(self.EMPTY_ANALYSER)

    @classmethod
    def tearDownClass(self):
        if isdir(self.EMPTY_SELECTOR):
            shutil.rmtree(self.EMPTY_SELECTOR)
        if isdir(self.EMPTY_ANALYSER):
            shutil.rmtree(self.EMPTY_ANALYSER)

    def test_raises_when_faulty(self):
        with self.assertRaises(ModuleNotFoundError):
            get_module("selector", "smth")

        with self.assertRaises(ModuleNotFoundError):
            get_module("analyser", "smth")

        with self.assertRaisesRegex(ImportError, "must be 'selector' or 'analyser'"):
            get_module("neitherthing", "smth")

    def test_imports_main(self):
        # main just exported as 'True', to check import logic is correct
        self.assertTrue(get_module("selector", "empty"))
        self.assertTrue(get_module("analyser", "empty"))
