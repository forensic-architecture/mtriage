from typing import List
from lib.common.etypes import Et, Pth

class CvJson(Et):
    """ A custom Etype for computer vision (CV) json files, representing
        predictions on a set of frames. """
    def filter(self, paths: List[Pth]) -> List[Pth]:
        jsons = []
        for p in paths:
            jsons.append(p) if p.suffix in ".json" else None
            if p.name == "scores.json":
                return [p]
        if len(jsons) is not 1:
            return []
        return jsons

    @staticmethod
    def rank():
        pass
