from abc import ABC
from lib.common.exceptions import ImproperLoggedPhaseError
from lib.common.mtmodule import MTModule
import os
import shutil
import unittest


class EmptyMTModule(MTModule):
    pass

class TestEmptyMTModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.BASE_DIR = "../tempdir"
        self.mod = EmptyMTModule("empty", self.BASE_DIR)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.BASE_DIR)

    def test_class_variables(self):
        self.assertEqual(self.mod.NAME, "empty")
        self.assertEqual(self.mod.BASE_DIR, self.BASE_DIR)
        self.assertEqual(self.mod._MTModule__LOGS, [])
        self.assertEqual(self.mod._MTModule__LOGS_DIR, f"{self.BASE_DIR}/logs")
        self.assertEqual(self.mod._MTModule__LOGS_FILE, f"{self.BASE_DIR}/logs/empty.txt")
        self.assertTrue(os.path.exists(f"{self.BASE_DIR}/logs"))

    def test_logged_phase_decorator(self):
        # logged_phase decorator should only work on methods that are of a class that inherits from MTModule
        class BadClass():
            @MTModule.logged_phase("somekey")
            def improper_func(self):
                pass

        class GoodClass(MTModule):
            @MTModule.logged_phase("somekey")
            def proper_func(self):
                self.logger("we did something.")
                return "no error"

        with self.assertRaisesRegex(ImproperLoggedPhaseError, "inherits from MTModule"):
            bc = BadClass()
            bc.improper_func()

        # test that a decorated method carries through its return value
        gc = GoodClass("my_good_mod", self.BASE_DIR)
        self.assertEqual(gc.proper_func(), "no error")

        # test that logged_phase generated logs correctly when called
        with open(f"{self.BASE_DIR}/logs/my_good_mod.txt", "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0], "my_good_mod: somekey: we did something.\n")

        # check that logs were cleared after phase
        self.assertEqual(gc._MTModule__LOGS, [])



