import numpy as np
import json
import os
import torch
from torch.autograd import Variable
from PIL import Image

# import sys
# from utils import transform, modified_resnet50, decode

from lib.common.analyser import Analyser
from lib.common.etypes import Etype, Union, Array

# TODO cuda ?
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models


def transform():
    return transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def decode(preds):
    classes = [
        "protest",
        "violence",
        "sign",
        "photo",
        "fire",
        "police",
        "children",
        "group_20",
        "group_100",
        "flag",
        "night",
        "shouting",
    ]
    return [(x, preds[c]) for c, x in enumerate(classes)]


class FinalLayer(nn.Module):
    """modified last layer for resnet50 for our dataset"""

    def __init__(self):
        super(FinalLayer, self).__init__()
        self.fc = nn.Linear(2048, 12)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.fc(x)
        out = self.sigmoid(out)
        return out


def modified_resnet50():
    model = models.resnet50(pretrained=True)
    model.fc = FinalLayer()
    return model


class ProtestsPretrained(Analyser):
    def pre_analyse(self, config):
        """
        Init the logging, etc
        Init the model
        """
        rLabels = config["labels"]
        self.THRESH = 0.6

        t = transform()
        model = modified_resnet50()
        model.load_state_dict(
            torch.load(
                "/mtriage/src/lib/analysers/ProtestsPretrained/model.pth.tar",
                map_location=torch.device("cpu"),
            )["state_dict"]
        )
        model.eval()

        def get_preds(img_path):
            """
            Gives labelds and probabilities for a single image
            This is were we preprocess the image, using a function defined in the model class
            """
            print(img_path)
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
