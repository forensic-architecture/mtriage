from shutil import copyfile
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


class ExtractTypesAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.Any

    def get_out_etype(self):
        return Etype.Any

    def analyse_element(self, element, config):
        dest = element["dest"]
        base = element["base"]
        exts = config["exts"] if "exts" in config else []
        pth = Path(base)

        matches = []
        for ext in exts:
            matches.extend(pth.rglob(ext))

        for fp in matches:
            filename = fp.name
            copyfile(fp, f"{dest}/{filename}")
            self.logger(f"{filename} extracted.")
