
from lib.common.analyser import Analyser
from lib.common.etypes import Etype

class Yolov5(Analyser):
    in_etype = Etype.Any
    out_etype = Etype.Any

    def analyse_element(self, element, config):
        return element

module = Yolov5
