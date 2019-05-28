import glob
import os
import shutil
import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from lib.common.util import save_logs

def get_json_paths(path):
    return list(Path(path).rglob("*.[jJ][sS][oO][nN]"))

def get_video_paths(path):
    return list(Path(path).rglob("*.[mM][pP][4]"))

def get_img_paths(path):
    return list(Path(path).rglob("*.[bB][mM][pP]"))

def get_element(el_id, base_path):
    # TODO: generalise elements beyond just videos
    fp = os.path.join(base_path, el_id)
    vids = get_video_paths(fp)
    imgs = get_img_paths(fp)
    jsons = get_json_paths(fp)
    # type: Video
    if len(vids) is 1:
        return vids[0]
    # type: Image
    elif len(imgs) is 1:
        return imgs[0]
    # type: Frames
    elif len(imgs) > 1:
        return imgs
    elif len(jsons) is 1:
        return jsons[0]
    elif len(jsons) > 1:
        return jsons
    else:
        # TODO: better error handling.
        raise Exception("There was some deformed element in your data folder.")


class Analyser(ABC):
    """A Analyser is a pass that creates derived workables from retrieved data.

    The working directory of the selector is passed during class instantiation,
    and can be referenced in the implementations of methods.
    """

    ALL_ANALYSERS = []
    DATA_EXT = "data"
    DERIVED_EXT = "derived"

    def __init__(self, config, module, folder):
        self.FOLDER = folder
        self.ANALYSER_LOGS = f"{self.FOLDER}/analyser-logs.txt"
        self.NAME = module
        self.ID = f"{self.NAME}_{str(len(Analyser.ALL_ANALYSERS))}"
        self.__logs = []
        Analyser.ALL_ANALYSERS.append(self.ID)

    def logger(self, msg):
        self.__logs.append(msg)
        print(msg)

    def _run(self, config):
        all_media = {}

        # NOTE: run setup_run() lifecycle hook before anything else
        self.setup_run()

        # the results from each selector sits in a folder of its name
        data_passes = [f for f in os.listdir(self.FOLDER) if os.path.isdir(f"{self.FOLDER}/{f}")]
        derived_passes = [f for f in os.listdir(self.FOLDER) if os.path.isdir(f"{self.FOLDER}/{f}")]

        for _pass in data_passes:
            all_media[_pass] = {
                Analyser.DATA_EXT: {},
                Analyser.DERIVED_EXT: {},
            }
            data_pass = f"{self.FOLDER}/{_pass}/{Analyser.DATA_EXT}"
            data_els = [f for f in os.listdir(data_pass) if os.path.isdir(os.path.join(data_pass,f))]
            for el_id in data_els:
                all_media[_pass][Analyser.DATA_EXT][el_id] = get_element(el_id, data_pass)

            derived_pass = f"{self.FOLDER}/{_pass}/{Analyser.DERIVED_EXT}"
            # NOTE: we have lots of nested loops here, but i think it's necessary...
            if not os.path.exists(derived_pass):
                break

            d_passes = [f for f in os.listdir(derived_pass) if os.path.isdir(os.path.join(derived_pass,f))]
            for d_pass in d_passes:
                all_media[_pass][Analyser.DERIVED_EXT][d_pass] = {}
                _dpath = f"{derived_pass}/{d_pass}"
                data_els = [f for f in os.listdir(_dpath) if os.path.isdir(os.path.join(_dpath,f))]
                for el_id in data_els:
                    all_media[_pass][Analyser.DERIVED_EXT][d_pass][el_id] = get_element(el_id, _dpath)

        # NOTE: run writes to logs via the 'self.logger' function.
        self.media = all_media
        elements = self.get_elements(config)
        # TODO: parallelize
        # TODO: handle this all through something like SELECT_MAP to keep track
        # of tasks and progress.
        for element in elements:
            self.run_element(element, config)

        save_logs(self.__logs, self.ANALYSER_LOGS)

    def setup_run(self):
        """option to set up class variables"""
        pass


    def get_derived_folder(self, selector):
        """Returns the path to a derived folder from a string selector"""
        derived_folder = f"{self.FOLDER}/{selector}/{Analyser.DERIVED_EXT}/{self.NAME}"
        if not os.path.exists(derived_folder):
            os.makedirs(derived_folder)

        return derived_folder

    @abstractmethod
    def get_elements(self, config):
        """ Returns a list of elements (strings) to be processed, possibly in parallel,
        by the run_element method. This is analogous to the Selector's index method, and will
        likely be replaced by something like it once we figure out parallelism/resuming.
        """
        return NotImplemented

    @abstractmethod
    def run_element(self, element, config):
        """ Should print processed element to a 'derived' folder in the appropriate
        Selector's folder.
        """
        return NotImplemented
