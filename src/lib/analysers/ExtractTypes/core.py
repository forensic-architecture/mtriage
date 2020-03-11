from shutil import copyfile
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


class ExtractTypes(Analyser):
    def analyse_element(self, element: Etype.Any, config) -> Etype.Any:
        exts = config["exts"] if "exts" in config else []
        element.paths = [x for x in element.paths
                         if x.suffix in exts or x.suffix[1:] in exts]
        self.logger(f"Paths for {element.id}: {[str(x) for x in element.paths]}")
        if len(element.paths) == 0:
            return None
        return element

module = ExtractTypes
