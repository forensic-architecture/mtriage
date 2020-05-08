from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.util.rank_cvjson import rank

class Rank(Analyser):
    """ NOTE: This class is kept for backwards compatibility, but should not be
    used in new implementations. Instaed, simply use the imported `rank`
    function directly in the relevant analyser's `post_analyse` method.
    """
    def analyse_element(self, element: Etype.CvJson, _) -> Etype.Any:
        return element

    def post_analyse(self, elements) -> Etype.Json:
        return rank(elements, logger=self.logger)

module = Rank
