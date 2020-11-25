import numpy as np
import json
import os
from importlib import import_module
from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.etypes import Etype, Union, Array
from lib.util.rank_cvjson import rank

KERAS_HOME = "/mtriage/data/.keras"
os.environ["KERAS_HOME"] = KERAS_HOME

import tensorflow as tf
from tensorflow.keras.preprocessing import image

SUPPORTED_MODELS = {
    "ResNet50": {"module": "resnet50"},
    "VGG16": {"module": "vgg16"},
    "VGG19": {"module": "vgg19"},
}


class KerasPretrained(Analyser):
    in_etype = Union(Array(Etype.Image), Etype.Json)
    out_etype = Etype.Json

    """ Override to always run serially. Otherwise it hangs, presumably due to
    some parallelisation that tensorflow does under the hood. """
    @property
    def in_parallel(self): return False

    def pre_analyse(self, config):
        self.logger(config["model"])
        self.logger(f"Storing models in {KERAS_HOME}")
        MOD = SUPPORTED_MODELS.get(config["model"])
        if MOD is None:
            raise InvalidAnalyserConfigError(
                f"The module '{config['model']}' either does not exist, or is not yet supported."
            )

        rLabels = config["labels"]

        # TODO: make it so that this doesn't redownload every run.
        # i.e. refactor it into partial.Dockerfile
        self.model_module = import_module(f"tensorflow.keras.applications.{MOD['module']}")
        impmodel = getattr(self.model_module, config["model"])
        # NB: this downloads the weights if they don't exist
        self.model = impmodel(weights="imagenet")
        self.THRESH = 0.1

        # revert to serial if CPU (TODO: debug why parallel CPU doesn't work)
        if not tf.test.is_gpu_available():
            self.in_parallel = False

        def get_preds(img_path):
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = self.model_module.preprocess_input(x)
            preds = self.model.predict(x)

            # top field must be included or defaults to 5, huge number ensures
            # it gets all labels
            decoded = self.model_module.decode_predictions(preds, top=10)

            # filter by labels provided in whitelist
            filteredPreds = [p for p in decoded[0] if p[1] in rLabels]

            return [
                (x[1], float(x[2])) for x in filteredPreds if float(x[2]) >= self.THRESH
            ]

        self.get_preds = get_preds

    def analyse_element(self, element, _):
        self.logger(f"Running inference on frames in {element.id}...")
        val = Etype.CvJson.from_preds(element, self.get_preds)
        self.logger(f"Wrote predictions JSON for {element.id}.")
        self.disk.delete_local_on_write = True
        return val

    def post_analyse(self, elements) -> Etype.Json:
        return rank(elements, logger=self.logger)


module = KerasPretrained
