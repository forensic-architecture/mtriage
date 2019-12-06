import json
from pathlib import Path
from shutil import copyfile
from imagededup import methods
from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


class ImagededupAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.ImageArray

    def get_out_etype(self):
        return Etype.ImageArray

    def __create_hasher(self, config):
        hasher_key = config["method"] if "method" in config else "phash"
        self.logger(f"Compare method is {hasher_key}")
        hasher = {
            "phash": methods.PHash,
            "ahash": methods.AHash,
            "dhash": methods.DHash,
            "whash": methods.WHash,
        }.get(hasher_key)
        if hasher is None:
            raise InvalidAnalyserConfigError(
                f"'{hasher_key}' is not a valid method for imagededup."
            )

        self.hasher = hasher()

        # super low threshold by default to only remove essentially identical images.
        if "threshold" in config:
            self.threshold = int(config["threshold"])
        else:
            self.threshold = 3

        self.logger(f"Hamming threshold is {self.threshold}")

    def pre_analyse(self, config):
        self.__create_hasher(config)

    def analyse_element(self, element, config):
        dest = element["dest"]
        basedir = element["base"]

        encodings = self.hasher.encode_images(image_dir=basedir)

        args = {"image_dir": basedir, "max_distance_threshold": self.threshold}

        duplicates = self.hasher.find_duplicates_to_remove(**args)

        self.logger(
            f"{len(duplicates)} duplicates found, copying over all other files..."
        )

        for pname in element["media"]["images"]:
            path = Path(pname)
            if path.name not in duplicates:
                copyfile(pname, f"{dest}/{path.name}")

        self.logger(f"{element['id']} images deduplicated.")
