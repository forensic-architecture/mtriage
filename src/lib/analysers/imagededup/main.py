import json
from pathlib import Path
from shutil import copyfile
from imagededup.methods import PHash
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


class ImagededupAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.AnnotatedImageArray

    def get_out_etype(self):
        return Etype.AnnotatedImageArray

    def pre_analyse(self, config):
        self.phasher = PHash()

    def analyse_element(self, element, config):
        dest = element["dest"]
        basedir = element["base"]
        # super low threshold by default to only remove essentially identical images.
        threshold = int(config["threshold"]) if "threshold" in config else 2
        self.logger(f"Hamming threshold is {threshold}")

        encodings = self.phasher.encode_images(image_dir=basedir)
        duplicates = self.phasher.find_duplicates_to_remove(
            image_dir=basedir, max_distance_threshold=threshold
        )

        self.logger(
            f"{len(duplicates)} duplicates found, copying over all other files..."
        )

        for pname in element["media"]["images"]:
            path = Path(pname)
            if path.name not in duplicates:
                copyfile(pname, f"{dest}/{path.name}")

        self.logger(f"{element['id']} images deduplicated.")
