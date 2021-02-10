from lib.common.analyser import Analyser
from lib.common.etypes import Etype

from PIL import Image
import torch

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
        results = self.model(imgs)
        # x1, y1, x2, y2, confidence, class

        import pdb; pdb.set_trace()

        # results =
        return element

module = TorchHub
