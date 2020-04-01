import numpy as np
import json
import os
import torch
from torch.autograd import Variable
from PIL import Image
from utils import transform, modified_resnet50, decode

from lib.common.analyser import Analyser
from lib.common.etypes import Etype, Union, Array

from utils import transform, modified_resnet50

# TODO cuda ?


class ProtestsPretrained(Analyser):
    def pre_analyse(self, config):
        """
        Init the logging, etc
        Init the model
        Same as KerasPretrained
        """
        rLabels = config["labels"]
        self.THRESH = 0.1

        t = transform()
        model = modified_resnet50()
        model.load_state_dict(
            torch.load("model.pth.tar", map_location=torch.device("cpu"))["state_dict"]
        )
        model.eval()

        def get_preds(img_path):
            """
            Gives labelds and probabilities for a single image
            This is were we preprocess the image, using a function defined in the model class
            """
            # load image
            img = Image.open(img_path).convert("RGB")
            # process it
            x = t(img)
            # get in in the right format
            x = Variable(x).unsqueeze(0)
            # predictions
            output = model(x)
            # decode
            output = decode(output.cpu().data.numpy()[0])
            # filter
            output = [(x[0], x[1]) for x in output if x[0] in rLabels]
            output = [(x[0], x[1]) for x in output if x[1] >= self.THRESH]

            return output

        self.get_preds = get_preds

        def analyse_element(
            self, element: Union(Array(Etype.Image), Etype.Json), _
        ) -> Etype.Json:
            self.logger(f"Running inference on frames in {element.id}...")
            val = Etype.CvJson.from_preds(element, self.get_preds)
            self.logger(f"Wrote predictions JSON for {element.id}.")
            self.disk.delete_local_on_write = True
            return val


module = ProtestsPretrained
