from lib.common.util import save_logs
import os
import unittest

class TestSaveLogs(unittest.TestCase):

    def setUp(self):
        self.LOGPATH = "testlog.txt"

    def tearDown(self):
        if os.path.exists(self.LOGPATH):
            os.remove(self.LOGPATH)

    def test_save_no_logs(self):
        save_logs([], self.LOGPATH)
        self.assertFalse(os.path.exists(self.LOGPATH))

    def test_save_one_log(self):
        save_logs(["test log 1"], self.LOGPATH)
        self.assertTrue(os.path.exists(self.LOGPATH))
        self.assertTrue("test log 1" in open(self.LOGPATH).read())

    def test_save_another_log(self):
        save_logs(["test log 1"], self.LOGPATH)
        save_logs(["test log 2"], self.LOGPATH)
        self.assertTrue(os.path.exists(self.LOGPATH))
        with open(self.LOGPATH) as file:
            f = file.read()
            self.assertTrue("test log 2" in f)
            self.assertTrue("test log 1" in f)

    def test_save_multiple_logs(self):
        save_logs(["test log 3", "test log 4"], self.LOGPATH)
        self.assertTrue(os.path.exists(self.LOGPATH))
        with open(self.LOGPATH) as file:
            f = file.read()
            self.assertTrue("test log 3" in f)
            self.assertTrue("test log 4" in f)
