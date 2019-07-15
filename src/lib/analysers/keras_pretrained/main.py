from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.util import vuevis_from_preds
from lib.common.etypes import Etype
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
import json

from importlib import import_module

SUPPORTED_MODELS = {
    "ResNet50": {"module": "resnet50"},
    "VGG16": {"module": "vgg16"},
    "VGG19": {"module": "vgg19"},
}


class Resnet50Analyser(Analyser):
    def get_in_etype(self):
        return Etype.AnnotatedImageArray

    def get_out_etype(self):
        return Etype.Json

    def pre_analyse(self, config):
        self.logger(config["model"])
        MOD = SUPPORTED_MODELS.get(config["model"])
        if MOD is None:
            raise InvalidAnalyserConfigError(
                f"The module '{config['model']}' either does not exist, or is not yet supported."
            )

        rLabels = config["labels"]

        self.model_module = import_module(f"keras.applications.{MOD['module']}")
        impmodel = getattr(self.model_module, config["model"])
        # NB: this downloads the weights if they don't exist
        self.model = impmodel(weights="imagenet")
        self.THRESH = 0.1

        def get_preds(img_path):
            img = load_img(img_path, target_size=(224, 224))
            x = img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = self.model_module.preprocess_input(x)
            preds = self.model.predict(x)

            # top field must be included or defaults to 5, huge number ensures
            # it gets all labels
            decoded = self.model_module.decode_predictions(preds, top=100)

            # filter by labels provided in whitelist
            filteredPreds = [p for p in decoded[0] if p[1] in rLabels]

            # return map(lambda x: (x[1], float(x[2])), filteredPreds)
            return [(x[1], float(x[2])) for x in filteredPreds if float(x[2]) >= self.THRESH]

        self.get_preds = get_preds

    def analyse_element(self, element, config):
        vuevis_from_preds(element, get_preds=self.get_preds, logger=self.logger)
