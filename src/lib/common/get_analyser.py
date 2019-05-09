from lib.analysers.frames import main as FramesAnalyser
from lib.analysers.darknet import main as DarknetAnalyser
from lib.analysers.ocr import main as OcrAnalyser


def get_analyser(key):
    return {
        "frames": FramesAnalyser,
        "darknet": DarknetAnalyser,
        "ocr": OcrAnalyser,
    }.get(key)
