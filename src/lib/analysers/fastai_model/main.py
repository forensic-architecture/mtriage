import os
import json
from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.common.util import vuevis_prepare_el, deduce_frame_no
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

    def analyse_element(self, element, config):
        imgs = element["media"]["images"]
        labels = {}

        self.logger(f"Running inference on frames in {element['id']}...")
        labels = {}
        for img_path in imgs:
            img = open_image(img_path)
            _, _, losses = self.LEARNER.predict(img)
            frame_no = deduce_frame_no(img_path)
            preds = [
                x
                for x in zip(self.LEARNER.data.classes, map(float, losses))
                if x[0] in self.LABELS
            ]

            for pred_label, pred_conf in preds:
                if pred_label in labels.keys():
                    labels[pred_label]["frames"].append(frame_no)
                    labels[pred_label]["scores"].append(pred_conf)
                else:
                    labels[pred_label] = {"frames": [frame_no], "scores": [pred_conf]}

        self.logger(f"Writing predictions for {element['id']}...")
        meta = vuevis_prepare_el(element)
        out = {**meta, "labels": labels}

        outpath = f"{element['dest']}/{element['id']}.json"
        with open(outpath, "w") as fp:
            json.dump(out, fp)
            self.logger(f"Wrote predictions JSON for {element['id']}.")
