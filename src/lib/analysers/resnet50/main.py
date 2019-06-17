from lib.common.analyser import Analyser, get_img_paths
from lib.common.util import vuevis_prepare_el, deduce_frame_no
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import json


class Resnet50Analyser(Analyser):
    def pre_analyse(self, config):
        # NB: this downloads the weights if they don't exist
        self.resnet50 = ResNet50(weights="imagenet")


    def analyse_element(self, element, config):
        imgs = get_img_paths(element["src"])
        labels = {}

        self.logger(f"Running inference on frames in {element['id']}...")
        for img_path in imgs:
            # TODO: does this resizing lead to bad inference?
            img = image.load_img(img_path, target_size=(224,224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            preds = self.resnet50.predict(x)

            top5 = decode_predictions(preds, top=5)
            frame_no = deduce_frame_no(img_path)

            for _, pred_label, pred_conf in top5[0]:
                # NB: numpy.float32s are not JSON serializable
                pred_conf = float(pred_conf)
                if pred_label in labels.keys():
                    labels[pred_label]["frames"].append(frame_no)
                    labels[pred_label]["scores"].append(pred_conf)
                else:
                    labels[pred_label] = {
                        "frames": [frame_no],
                        "scores": [pred_conf],
                    }

        self.logger(f"Writing predictions for {element['id']}...")
        meta = vuevis_prepare_el(element)
        out = {**meta, "labels": labels }

        outpath = f"{element['dest']}/{element['id']}.json"
        with open(outpath, "w") as fp:
            json.dump(out, fp)
            self.logger(f"Wrote predictions JSON for {element['id']}.")
