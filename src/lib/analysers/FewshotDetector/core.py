from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
from subprocess import call, STDOUT
from pathlib import Path
import os


class FewshotDetector(Analyser):
    in_etype = Union(Array(Etype.Image), Etype.Json)
    out_etype = Etype.Json

    def analyse_element(self, element, config):
        return element


module = FewshotDetector
