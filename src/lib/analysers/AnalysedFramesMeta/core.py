from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.util.cvjson import generate_meta
from lib.etypes.cvjson import CvJson


class AnalysedFramesMeta(Analyser):
    out_etype = Etype.CvJson

    def analyse_element(self, element, _):
        return element

    def post_analyse(self, elements) -> Etype.Json.as_array():
        return generate_meta(elements, logger=self.logger)


module = AnalysedFramesMeta
