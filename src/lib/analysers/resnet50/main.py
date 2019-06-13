from lib.common.analyser import Analyser, get_img_paths
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np


class Resnet50Analyser(Analyser):
    def pre_analyse(self, config):
        self.resnet50 = ResNet50(weights="imagenet")


    def analyse_element(self, element, config):
        imgs = get_img_paths(element["src"])
        print(imgs)
        for img_path in imgs:
            img = image.load_img(img_path, target_size=(224,224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            preds = self.resnet50.predict(x)
            print('Predicted:', decode_predictions(preds, top=5))
