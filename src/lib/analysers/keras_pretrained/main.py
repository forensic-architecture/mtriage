from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.util import vuevis_from_preds
from lib.common.etypes import Etype
from keras.preprocessing import image
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

        self.model_module = import_module(f"keras.applications.{MOD['module']}")
        impmodel = getattr(self.model_module, config["model"])
        # NB: this downloads the weights if they don't exist
        self.model = impmodel(weights="imagenet")

        def get_preds(img_path):
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = self.model_module.preprocess_input(x)
            preds = self.model.predict(x)
            top = self.model_module.decode_predictions(preds, top=5)
            return map(lambda x: (x[1], float(x[2])), top[0])

        self.get_preds = get_preds

    def analyse_element(self, element, config):
        vuevis_from_preds(element, get_preds=self.get_preds, logger=self.logger)
