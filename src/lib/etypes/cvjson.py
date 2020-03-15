from typing import List, Union
from pathlib import Path
from lib.common.etypes import Et, Pth
from lib.common.exceptions import EtypeCastError


class CvJson(Et):
    """ A custom Etype for computer vision (CV) json files, representing
        predictions on a set of frames. """

    def filter(self, paths: Union[Pth, List[Pth]]) -> List[Pth]:
        if isinstance(paths, (str, Path)):
            paths = [paths]

        pths = []
        json_count = 0
        for p in paths:
            if p.suffix in ".json" and p.name == "scores.json":
                pths.append(p)
                json_count += 1
            pths.append(p) if p.suffix in [".bmp", ".jpg", ".png", ".jpeg"] else None
        if json_count != 1:
            raise EtypeCastError(self)
        return pths

    @staticmethod
    def rank():
        pass


etype = CvJson
