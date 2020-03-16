import json
from pathlib import Path
from shutil import copyfile
from imagededup import methods
from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


class ImageDedup(Analyser):
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

    def is_dry(self):
        return "dry" in self.config and self.config["dry"]

    def analyse_element(
        self, element: Etype.Image.array(), config
    ) -> Etype.Image.array():
        # NOTE: only works if all images are in same file, should probably copy for robustness.
        basedir = element.paths[0].parent
        encodings = self.hasher.encode_images(image_dir=basedir)

        args = {"image_dir": basedir, "max_distance_threshold": self.threshold}

        duplicates = self.hasher.find_duplicates_to_remove(**args)

        self.logger(f"{len(duplicates)} duplicates found.")

        self.logger("IMAGES TO REMOVE")
        self.logger("------------------")
        for dup in duplicates:
            self.logger(dup)
        self.logger("------------------")
        if self.is_dry():
            return None

        self.logger(f"{element.id} images deduplicated.")

        deduplicated_paths = [p for p in element.paths if p.name not in duplicates]

        return Etype.Image.array()(element.id, paths=deduplicated_paths)


module = ImageDedup
