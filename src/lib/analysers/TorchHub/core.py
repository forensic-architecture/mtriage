from lib.common.analyser import Analyser
from lib.common.etypes import Etype

from PIL import Image
import torch

def cls_and_conf(pred, names):
    # `pred` is an array with 6 values: x1, y1, x2, y2, confidence, class
    _,_,_,_,conf,cl = pred
    cl = names[int(cl)]
    conf = float(conf)
    return (cl, conf)


class TorchHub(Analyser):
    in_etype = Etype.Any
    out_etype = Etype.Any

    def pre_analyse(self, config):
        if config.get('args') is None: config['args'] = []
        if config.get('kwargs') is None: config['kwargs'] = {}

        self.model = torch.hub.load(config['repo'], *config['args'], **config['kwargs'])
        self.model.conf = 0.5 # confidence threshold
        self.model.iou = 0.45 # NMS IoU threshold
        self.logger("Model loaded from remote.")

    def analyse_element(self, element, config):
        imgs = [Image.open(x) for x in element.paths]
        results = self.model(imgs).tolist()
        self.logger(f"Batched inference successfully run for element {element.id}.")

        def get_preds(img_path):
            idx = element.paths.index(img_path)
            result = results[idx]
            return [cls_and_conf(p, result.names) for p in result.pred]

        return Etype.CvJson.from_preds(element, get_preds)

module = TorchHub
