from shutil import copyfile
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


class ExtractTypes(Analyser):
    def analyse_element(self, element: Etype.Any, config) -> Etype.Any:
        exts = config["exts"] if "exts" in config else []
        element.paths = [
            x for x in element.paths if x.suffix in exts or x.suffix[1:] in exts
        ]
        if len(element.paths) == 0:
            self.logger(f"No extracted media in element {element.id}.")
            return None
        self.logger(f"Extracting element {element.id} with paths: {[x.name for x in element.paths]}")
        return element


module = ExtractTypes
