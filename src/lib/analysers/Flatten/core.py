from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.util.cvjson import flatten


class Flatten(Analyser):
    """NOTE: This class is kept for backwards compatibility, but should not be
    used in new implementations. Instaed, simply use the imported `rank`
    function directly in the relevant analyser's `post_analyse` method.
    """
    out_etype = Etype.Json

    def analyse_element(self, element: Etype.CvJson, _) -> Etype.Json:
        return element

    def post_analyse(self, elements) -> Etype.Json:
        return flatten(elements, logger=self.logger)


module = Flatten
