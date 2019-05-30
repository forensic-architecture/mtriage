from lib.selectors.youtube import main as YoutubeSelector
from lib.common.get_selector import get_selector
import unittest


class TestGetSelector(unittest.TestCase):
    def test_get_selector(self):
        yt = get_selector("youtube")
        self.assertEqual(yt, YoutubeSelector)
