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
from lib.common.util import vuevis_prepare_el, deduce_frame_no


class YoloV3Analyser(Analyser):
    """ Adapted from eriklindernoren/PyTorch-YOLOv3. See https://github.com/breezykermo/PyTorch-YOLOv3
        for reference implementation.
    """

    def get_in_etype(self):
        return Etype.AnnotatedImageArray

    def get_out_etype(self):
        return Etype.Json

    def pre_analyse(self, config):
        RUN_DIR = os.path.dirname(os.path.realpath(__file__))
        # TODO: allow these to be changed by values in config
        self.MODEL_DEF = f"{RUN_DIR}/config/yolov3.cfg"
        self.WEIGHTS_PATH = f"{RUN_DIR}/config/yolov3.weights"
        self.CLASS_PATH = f"{RUN_DIR}/config/coco.names"
        self.CONF_THRES = 0.8
        self.NMS_THRES = 0.4
        self.BATCH_SIZE = 10
        self.N_CPU = 2
        self.IMG_SIZE = 256

        self.logger(
            "Using CUDA on GPU-enabled mtriage"
            if torch.cuda.is_available()
            else "Cannot find CUDA, using CPU"
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Set up model
        self.model = Darknet(self.MODEL_DEF, img_size=self.IMG_SIZE).to(self.device)

        if self.WEIGHTS_PATH.endswith(".weights"):
            # Load darknet weights
            self.model.load_darknet_weights(self.WEIGHTS_PATH)
        else:
            # Load checkpoint weights
            self.model.load_state_dict(torch.load(self.WEIGHTS_PATH))

        self.model.eval()  # Set in evaluation mode

    def analyse_element(self, element, config):
        # PLACEHOLDER: skip if already done
        if os.path.exists(f"{element['dest']}/{element['id']}.json"):
            self.logger(f"Result already found for {element['id']}, skipping.")
            return

        dataloader = DataLoader(
            ImageFolder(element["src"], img_size=self.IMG_SIZE),
            batch_size=self.BATCH_SIZE,
            shuffle=False,
            num_workers=self.N_CPU,
        )

        classes = load_classes(self.CLASS_PATH)  # Extracts class labels from file

        Tensor = (
            torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor
        )

        imgs = []  # Stores image paths
        img_detections = []  # Stores detections for each image index

        self.logger(f"Performing object detection for element {element['id']}:")
        prev_time = time.time()

        # inference images in batches
        for batch_i, (img_paths, input_imgs) in enumerate(dataloader):
            # Configure input
            input_imgs = Variable(input_imgs.type(Tensor))

            # Get detections
            with torch.no_grad():
                detections = self.model(input_imgs)
                detections = non_max_suppression(
                    detections, self.CONF_THRES, self.NMS_THRES
                )

            # Log progress
            current_time = time.time()
            inference_time = datetime.timedelta(seconds=current_time - prev_time)
            prev_time = current_time
            # self.logger("\t+ Batch %d, Inference Time: %s" % (batch_i, inference_time))

            # Save image and detections
            imgs.extend(img_paths)
            img_detections.extend(detections)

        # save predictions as single JSON that encapsulates info across frames
        labels = {}

        for img_i, (path, detections) in enumerate(zip(imgs, img_detections)):
            if detections is not None:
                frame_no = deduce_frame_no(path)
                for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
                    # NOTE: we currently don't use localisations, we just want to know if there is a prediction
                    # pred_x1 = x1.item()
                    # pred_y1 = y1.item()
                    # pred_x2 = x2.item()
                    # pred_y2 = y2.item()
                    pred_label = classes[int(cls_pred)]
                    pred_conf = cls_conf.item() * 100

                    if pred_label in labels.keys():
                        labels[pred_label]["frames"].append(frame_no)
                        labels[pred_label]["scores"].append(pred_conf)
                    else:
                        labels[pred_label] = {
                            "frames": [frame_no],
                            "scores": [pred_conf],
                        }

        try:
            out = vuevis_prepare_el(element)
            out.update({"labels": labels})
        except FileNotFoundError:
            self.logger(f"Could not find meta.json, skipping {element['id']}.")

        with open(f"{element['dest']}/{element['id']}.json", "w") as f:
            json.dump(out, f)
            self.logger(f"Wrote predictions JSON for {element['id']}")
