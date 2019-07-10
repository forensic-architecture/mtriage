import os
import json
from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.common.util import vuevis_from_preds
from fastai.vision import load_learner, open_image


class FastaiModelAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.AnnotatedImageArray

    def get_out_etype(self):
        return Etype.Json

    def pre_analyse(self, config):
        path, fname = os.path.split(config["path"])
        self.LEARNER = load_learner(path, fname)
        self.LABELS = self.LEARNER.data.classes

        if "labels" in config.keys() and len(config["labels"]) > 0:
            self.LABELS = [lb for lb in self.LABELS if lb in config["labels"]]

        self.logger(f"Model successfully loaded from {path}/{fname}.")

        def get_preds(img_path):
            img = open_image(img_path)
            _, _, losses = self.LEARNER.predict(img)
            return [
                x
                for x in zip(self.LEARNER.data.classes, map(float, losses))
                if x[0] in self.LABELS
            ]

        self.get_preds = get_preds

    def analyse_element(self, element, config):
        vuevis_from_preds(element, get_preds=self.get_preds, logger=self.logger)
