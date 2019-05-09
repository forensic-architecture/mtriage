from lib.common.analyser import Analyser
import json
import io
import os

import google.auth
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson

IS_DEMO = True
LIMIT_FRAME = 15


def paths_to_components(whitelist):
    """ Take a list of input paths--of the form '{selector_name}/{?analyser_name}'--
        and produces a list of components. Components are tuples whose first value
        is the name of a selector, and whose second value is either the name of an
        analyser, or None.
    """
    all_cmps = []
    for path in whitelist:
        cmps = os.path.split(path)
        if len(cmps) is 1:
            all_cmps.append((cmps[0], None))
        elif len(cmps) is 2:
            all_cmps.append((cmps[0], cmps[1]))
        else:
            raise Exception(
                f"The path {path} in whitelist needs to be of the form '{selector_name}/{analyser_name}'."
            )
    return all_cmps


class OcrAnalyser(Analyser):
    """ This module relies on `gcloud` installed in the Docker container,
    as well as a .config/gcloud with the following capabilities:
    ```
    gcloud services enable vision.googleapis.com
    ```

    You'll need to create a service account and put specify its absolute path in the '.env'
    the top of this repo, GOOGLE_APPLICATION_CREDENTIALS.
    """

    def setup_run(self):
        # creds are interpolated from env variable, GOOGLE_APPLICATION_CREDENTIALS. See
        # https://cloud.google.com/docs/authentication/getting-started
        self.VISION_CLIENT = vision.ImageAnnotatorClient()

    def __analyse_text(self, path):
        """ OCR a local image using GCP's vision API. """
        with open(path, "rb") as img_file:
            content = img_file.read()

        return self.VISION_CLIENT.text_detection({"content": content})

    def __analyse_component(self, component, LIMIT_FRAME):
        # NOTE: LIMIT_FRAME is mainly an optionality passed for debugging, so that we don't
        # run GCP analysis on all frames of a video when testing.
        selector_name, analyser_name = component
        baseoutfolder = self.get_derived_folder(selector_name)

        self.logger(f"Selector: {selector_name}, Analyser: {analyser_name}")
        self.logger(f"Max number of frames set: {LIMIT_FRAME}.")

        input_frames = (
            self.media[selector_name][Analyser.DERIVED_EXT][analyser_name]
            if (analyser_name is not None)
            else self.media[selector_name][Analyser.DATA_EXT]
        )

        for idx, element in enumerate(input_frames.keys()):
            self.logger(f"OCRing frames in element: {element}")
            if LIMIT_FRAME > 0:
                frames = input_frames[element][0:LIMIT_FRAME]
            else:
                frames = input_frames[element]
            responses = [self.__analyse_text(str(t)) for t in frames]

            outfolder = os.path.join(baseoutfolder, element)
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)

            for r_idx, response in enumerate(responses):
                serialized = MessageToJson(response)
                with open(f"{outfolder}/{r_idx}.json", "w") as fp:
                    fp.write(serialized)
                self.logger(f"Frame {r_idx} OCRed: {r_idx}.json written.")

    def run(self, config):

        components = paths_to_components(config["whitelist"])
        max_requests = config["max_requests"] if config["max_requests"] else -1

        for component in components:
            self.__analyse_component(component, max_requests)

