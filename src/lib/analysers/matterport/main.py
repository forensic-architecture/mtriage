import os
import sys
import time
import datetime
import json

from PIL import Image

import torch
from torch.utils.data import DataLoader
from torch.autograd import Variable

from lib.analysers.yolov3.utils import *
from lib.analysers.yolov3.models import Darknet
from lib.common.analyser import Analyser


class YoloV3Analyser(Analyser):
    """ Adapted from eriklindernoren/PyTorch-YOLOv3. See https://github.com/breezykermo/PyTorch-YOLOv3
        for reference implementation.
    """

    def pre_analyse(self, config):
        RUN_DIR = os.path.dirname(os.path.realpath(__file__))
        self.logger("TODO: setup for Mask-RCNN")


    def analyse_element(self, element, config):
        self.logger("TODO: analysing with Matterport Mask-RCNN")
