from lib.analysers.frames import main as FramesAnalyser
from lib.analysers.darknet import main as DarknetAnalyser
from lib.analysers.ocr import main as OcrAnalyser
from lib.common.get_analyser import get_analyser
import unittest


class TestGetAnalyser(unittest.TestCase):
    def test_get_frames_analyser(self):
        fa = get_analyser("frames")
        self.assertEqual(fa, FramesAnalyser)

    def test_get_darknet_analyser(self):
        fa = get_analyser("darknet")
        self.assertEqual(fa, DarknetAnalyser)

    def test_get_ocr_analyser(self):
        fa = get_analyser("ocr")
        self.assertEqual(fa, OcrAnalyser)
