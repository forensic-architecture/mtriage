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
from lib.common.etypes import Etype
from lib.common.util import vuevis_prepare_el, deduce_frame_no


class YoloV3Analyser(Analyser):
    """Adapted from eriklindernoren/PyTorch-YOLOv3. See https://github.com/breezykermo/PyTorch-YOLOv3
    for reference implementation.
    """

    def pre_analyse(self, config):
        RUN_DIR = os.path.dirname(os.path.realpath(__file__))
        # TODO: allow these to be changed by values in config
        self.MODEL_DEF = f"{RUN_DIR}/config/yolov3.cfg"
        self.WEIGHTS_PATH = f"{RUN_DIR}/config/yolov3.weights"
        self.CLASS_PATH = f"{RUN_DIR}/config/coco.names"
        self.CONF_THRES = 0.5  # low threshold to get many predictions
        self.NMS_THRES = 0.4
        self.BATCH_SIZE = 10
        self.N_CPU = 2
        self.IMG_SIZE = 256

        self.logger(
            "Using CUDA on GPU-enabled mtriage"
            if torch.cuda.is_available()
            else "Cannot find CUDA, using CPU"
        )
        # Set up model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Darknet(self.MODEL_DEF, img_size=self.IMG_SIZE).to(self.device)
        self.model.load_darknet_weights(self.WEIGHTS_PATH)
        self.model.eval()

        t = transforms.Compose(
            [
                transforms.Resize((self.IMG_SIZE, self.IMG_SIZE)),
                transforms.ToTensor(),
            ]
        )
        rLabels = config["labels"]
        classes = load_classes(class_path)  # Extracts class labels from file
        Tensor = (
            torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor
        )

        def get_preds(img_path):
            """
            Gives labelds and probabilities for a single image
            This is were we preprocess the image, using a function defined in the model class
            """
            self.logger(f"Performing object detection for element {element['id']}:")
            # load image
            input_img = Variable(t(Image.open(imgpath).convert("RGB"))).unsqueeze(0)
            # Get detections
            with torch.no_grad():
                detections = model(input_img)
                detections = non_max_suppression(
                    detections, self.CONF_THRES, self.NMS_THRES
                )

            # squeeze
            detections = detections[0]

            predictions = []
            # Iterate through images and save plot of detections
            if detections is not None:
                # If needed, boxes are available here. (Don't forget to rescale them)
                for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:

                    pred_label = classes[int(cls_pred)]
                    pred_conf = cls_conf.item() * 100

                    # filter output
                    if pred_label in rLabels or len(rLabels) == 0:
                        predictions.append((pred_label, pred_conf))

            return predictions

        self.get_preds = get_preds

        def analyse_element(
            self, element: Union(Array(Etype.Image), Etype.Json), _
        ) -> Etype.Json:
            self.logger(f"Running inference on frames in {element.id}...")
            val = Etype.CvJson.from_preds(element, self.get_preds)
            self.logger(f"Wrote predictions JSON for {element.id}.")
            self.disk.delete_local_on_write = True
            return val


module = yolov3
