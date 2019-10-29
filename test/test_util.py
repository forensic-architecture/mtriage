import unittest
from util import (
    name_and_ver,
    InvalidPipDep,
    should_add_pipdep,
    should_add_dockerline,
    InvalidArgumentsError,
)


class TestUtil(unittest.TestCase):
    """ Test the util functions at mtriage's outer layer.
    """

    def test_name_and_ver(self):
        name, ver = name_and_ver("numpy")
        self.assertEqual(name, "numpy")
        self.assertEqual(ver, None)

        name, ver = name_and_ver("numpy==4.0")
        self.assertEqual(name, "numpy")
        self.assertEqual(ver, "4.0")

        n1, v1 = name_and_ver("google-api-core==1.11.0")
        self.assertEqual(n1, "google-api-core")
        self.assertEqual(v1, "1.11.0")

        # self.assertRaises(InvalidPipDep, name_and_ver, "numpy==")
        # self.assertRaises(InvalidPipDep, name_and_ver, "invalid==2.h")
        self.assertRaises(InvalidPipDep, name_and_ver, "invalid==2==")

    def test_should_add_pipdeps(self):
        p1 = []
        # empty check --> false
        self.assertTrue(should_add_pipdep("numpy", p1))

        p2 = ["numpy"]
        self.assertFalse(should_add_pipdep("numpy", p2))
        self.assertTrue(should_add_pipdep("pandas", p2))
        # should add specific versions over undefined
        self.assertTrue(should_add_pipdep("numpy==2.0", p2))
        # should add higher versions
        p3 = ["numpy==1.0"]
        self.assertTrue(should_add_pipdep("numpy==3.0", p3))
        # check with multiple
        p4 = ["pack1==2.0", "pandas=3.4", "numpy==1.0", "blueray"]
        self.assertTrue(should_add_pipdep("numpy==1.1", p4))
        self.assertFalse(should_add_pipdep("numpy", p4))
        self.assertTrue(should_add_pipdep("blueray==0.1", p4))
        self.assertTrue(should_add_pipdep("newdep", p4))
        # check error
        with self.assertRaises(InvalidPipDep):
            should_add_pipdep("invalid==1==", p4)

    def test_should_add_dockerline(self):
        p1 = []
        self.assertTrue(should_add_dockerline("any line here", p1))
        p2 = ["RUN apt-get install -y vim"]
        self.assertFalse(should_add_dockerline("RUN apt-get install -y vim", p2))
        p3 = ["RUN apt-get install -y vim", "RUN curl -o https://smthn", "RUN it"]
        self.assertTrue(should_add_dockerline("RUN apt get install -y curl", p3))
        self.assertFalse(should_add_dockerline("RUN curl -o https://smthn", p3))
