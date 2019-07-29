import unittest
import yaml
from test.utils import get_info_path
from os import listdir


def is_valid_arg(arg):
    if "name" not in arg or not isinstance(arg["name"], str): return False
    if "required" not in arg or not isinstance(arg["required"], bool): return False
    # NOTE: not checking for 'input' or 'desc' attrs, considering them optional at this time.
    return True

class TestInfoYamls(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ALL_ANALYSERS = listdir("lib/analysers")
        self.ALL_SELECTORS = listdir("lib/selectors")

    def test_selectors(self):
        # selector infos
        for sel in self.ALL_SELECTORS:
            with open(get_info_path("selector", sel)) as f:
                info = yaml.safe_load(f)
            self.assertTrue("desc" in info)
            self.assertTrue("args" in info)
            self.assertTrue(isinstance(info["args"], list))
            for arg in info["args"]:
                self.assertTrue(is_valid_arg(arg))

        # analyser infos
        for ana in self.ALL_ANALYSERS:
            with open(get_info_path("analyser", ana)) as f:
                info = yaml.safe_load(f)
            self.assertTrue("desc" in info)
            self.assertTrue("args" in info)
            self.assertTrue(isinstance(info["args"], list))
            for arg in info["args"]:
                self.assertTrue(is_valid_arg(arg))
