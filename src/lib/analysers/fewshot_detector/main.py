import os
import json

from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.common.util import vuevis_prepare_el, deduce_frame_no

import torch
from utils import *
import prediction_utils
from cfg import cfg
from cfg import parse_cfg

class FewShotDetectorAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.Union(Etype.Image.array(), Etype.Json)

    def get_out_etype(self):
        return Etype.Json

    def pre_analyse(self, config):
        data_options  = read_data_cfg('cfg/metatune.data')
        darknet = parse_cfg('cfg/darknet_dynamic.cfg')
        learnet = parse_cfg('cfg/reweighting_net.cfg')
        net_options   = darknet[0]
        meta_options  = learnet[0]
        self.cuda = torch.cuda.is_available() 
        
        self.logger(
            "Using CUDA on GPU-enabled mtriage"
            if self.cuda
            else "Cannot find CUDA, using CPU"
        )
        
        self.conf_thresh = config['conf_thresh'] or 0.2
        self.nms_thresh = config['nms_thresh'] or  0.45
        
        self.logger(
            f"Using confidence threshold {self.conf_thresh} and nms threshold {self.nms_thresh})
        # Configure options
        cfg.config_data(data_options)
        cfg.config_meta(meta_options)
        cfg.config_net(net_options)
        
        weights = config['weights'] or 'weights/000020.weights'
        dynamic_weights =  config['dynamic_weights'] or 'weights/dynamic_weights.pkl'
        
        self.model = prediction_utils.load_model(darknetcfg, learnetcfg, weights, self.cuda) #TODO
        self.dynamic_weights = prediction_utils.load_dynamic_weights(dynamic_weights, self.cuda)
        self.n_cls = 20
        self.class = "triple-chaser"
        self.logger(f"Model successfully loaded from config['weights'].") #TODO

        def get_preds(img_path):
            return predict(img_path, self.model, 
                           self.dynamic_weights, self.n_cls, 
                           self.conf_thresh, self.nms_thresh,
                           self.cuda)

        self.get_preds = get_preds

    def analyse_element(self, element, config):
        if os.path.exists(f"{element['dest']}/{element['id']}.json"):
            self.logger(f"Result already found for {element['id']}, skipping.")
            return
        self.logger(f"Performing object detection for element {element['id']}:")            
                    # save predictions as single JSON that encapsulates info across frames
        labels = {}
                    
        for img_path in elements['media']['images']:
            boxes = self.get_preds(img_path)
            if len(boxes) > 0:
                conf_scores = [box[0] for box in boxes]
                pred_conf = max(conf_scores)
                frame_no = deduce_frame_no(path)
                if self.class not in labels:
                    labels[self.class] = {
                        "frames": [],
                        "scores": [],
                        "detections": [],
                    }
                labels[self.class]["frames"].append(frame_no)
                labels[self.class]["scores"].append(pred_conf)
                frame_json = f"{frame_no}_detections.json"
                labels[self.class]["detections"].append(frame_json)
                with open(f"{element['dest']}/{frame_json}", "w") as f:
                    json.dump(boxes, f)
                    
        try:
            out = vuevis_prepare_el(element)
            out.update({"labels": labels})
        except FileNotFoundError:
            self.logger(f"Could not find meta.json, skipping {element['id']}.")

        with open(f"{element['dest']}/{element['id']}.json", "w") as f:
            json.dump(out, f)
            self.logger(f"Wrote predictions JSON for {element['id']}")        
