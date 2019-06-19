from lib.common.analyser import Analyser
from lib.common.etypes import Etype
import json
import io
import os

import google.auth
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson

IS_DEMO = True
MAX_REQUESTS = 15


class OcrAnalyser(Analyser):
    """ This module relies on `gcloud` installed in the Docker container,
    as well as a .config/gcloud with the following capabilities:
    ```
    gcloud services enable vision.googleapis.com
    ```

    You'll need to create a service account and put specify its absolute path in the '.env'
    the top of this repo, GOOGLE_APPLICATION_CREDENTIALS.
    """

    def get_in_etype(self):
        return Etype.ImageArray

    def get_out_etype(self):
        return Etype.Json

    def pre_analyse(self, config):
        # creds are interpolated from env variable, GOOGLE_APPLICATION_CREDENTIALS. See
        # https://cloud.google.com/docs/authentication/getting-started
        self.VISION_CLIENT = vision.ImageAnnotatorClient()

    def __analyse_text(self, path):
        """ OCR a local image using GCP's vision API. """
        with open(path, "rb") as img_file:
            content = img_file.read()

        return self.VISION_CLIENT.text_detection({"content": content})

    def analyse_element(self, element, config):
        dest = element["dest"]
        input_frames element["media"]["images"]

        # NOTE: MAX_REQUESTS is mainly an optionality passed for debugging, so that we don't
        # run GCP analysis on all frames of a video when testing.
        MAX_REQUESTS = config["max_requests"] if config["max_requests"] else -1
        if MAX_REQUESTS > 0:
            input_frames = input_frames[0:MAX_REQUESTS]

        self.logger(f"OCRing frames in element: {element['id']}")

        responses = [self.__analyse_text(t) for t in input_frames]

        for r_idx, response in enumerate(responses):
            serialized = MessageToJson(response)
            with open(f"{dest}/{r_idx}.json", "w") as fp:
                fp.write(serialized)
            self.logger(f"Frame {r_idx} OCRed: {r_idx}.json written.")
