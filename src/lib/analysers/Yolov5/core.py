import numpy as np
from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.etypes import Etype, Union, Array
from lib.util.cvjson import generate_meta
from lib.etypes.cvjson import CvJson

import torch

class Yolov5(Analyser):
    in_etype = Union(Array(Etype.Image), Etype.Json)
    out_etype = CvJson
    """ Override to always run serially. Otherwise it hangs, presumably due to
    the parallelisation that tensorflow does under the hood. """

    @property
    def in_parallel(self):
        return False

    def pre_analyse(self, config):
        # TODO: work out how to load in custom weights, rather than using this default.
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5n")

        # This function assumes that `element.paths` represents an array of images
        # to be interpreted. The `get_preds` function operates on a single image,
        # accepting one argument that is a path to an image. It returns a list of
        # tuples `('classname', 0.8)`, where `'classname'` is a string
        # representing the class predicted, and `0.8` is the normalized prediction
        # probability between 0 and 1. See KerasPretrained/core.py in analysers
        # for an example. """
        def get_preds(img_path: Path):
            results = self.model(img_path)
            # TODO: work out how to return not the `results` object from yolov5,
            # but a list of tuples as specified above
            return []

        self.get_preds = get_preds


    def analyse_element(self, element, _):
        self.logger(f"Running inference on frames in {element.id}...")
        val = Etype.CvJson.from_preds(element, self.get_preds)
        self.logger("Tried to show results.")
        self.disk.delete_local_on_write = True
        return val

    def post_analyse(self, elements) -> Etype.Json.as_array():
        return generate_meta(elements, logger=self.logger)


module = Yolov5
