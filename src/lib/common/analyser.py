import glob
import os
import shutil
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path
from lib.common.util import save_logs


def get_json_paths(path):
    return list(Path(path).rglob("*.[jJ][sS][oO][nN]"))


def get_video_paths(path):
    return list(Path(path).rglob("*.[mM][pP][4]"))


def get_img_paths(path):
    return list(Path(path).rglob("*.[bB][mM][pP]"))

def paths_to_components(whitelist):
    """ Take a list of input paths--of the form '{selector_name}/{?analyser_name}'-- and produces a list of components.
        Components are tuples whose first value is the name of a selector, and whose second value is either the name of
        an analyser, or None.
    """
    all_cmps = []
    for path in whitelist:
        cmps = path.split("/")

        if len(cmps) is 1:
            all_cmps.append((cmps[0], None))
        elif len(cmps) is 2:
            all_cmps.append((cmps[0], cmps[1]))
        else:
            # TODO: error handling...
            raise Exception(
                f"The path {path} in whitelist needs to be of the form '{{selector_name}}/{{analyser_name}}'."
            )
    return all_cmps


class Analyser(ABC):
    """ A Analyser is a pass that creates derived workables from retrieved data.

        The working directory of the selector is passed during class instantiation, and can be referenced in the
        implementations of methods.
    """

    ALL_ANALYSERS = []
    DATA_EXT = "data"
    DERIVED_EXT = "derived"

    def __init__(self, config, module, folder):
        self.CONFIG = config
        self.NAME = module
        self.FOLDER = folder

        self.ANALYSER_LOGS = f"{self.FOLDER}/analyser-logs.txt"
        self.ID = f"{self.NAME}_{str(len(Analyser.ALL_ANALYSERS))}"
        self.__logs = []
        Analyser.ALL_ANALYSERS.append(self.ID)

    # STATIC METHODS
    # intended for use in implementations of 'run_element'.
    @staticmethod
    def find_video_paths(element_path):
        return get_video_paths(element_path)

    @staticmethod
    def find_img_paths(element_path):
        return get_img_paths(element_path)

    @staticmethod
    def find_json_paths(element_path):
        return get_json_paths(element_path)

    # INTERNAL METHODS
    def logger(self, msg):
        self.__logs.append(msg)
        print(msg)

    def derive_elements(self, data_obj, outfolder):
        """ An 'element' (as it is passed to the 'run_element' method that is exposed on analysers) is currently a
            dictionary with the following attributes:
                path: The path to the element that should be analysed.
                dest: The path to the folder where element analysis should be printed.
        """

        def derive_el(key):
            return {"src": data_obj[key], "dest": f"{outfolder}/{key}"}

        return np.array(list(map(derive_el, list(data_obj.keys()))))

    def __get_elements(self, media):
        """ Derive which elements to use from available media base on the ELEMENTS_IN attr in self.CONFIG.
        """
        whitelist = self.CONFIG["elements_in"]
        cmps = paths_to_components(whitelist)

        elements = np.array([])
        for _cmp in cmps:
            if _cmp[1] is None:
                outfolder = self.get_derived_folder(_cmp[0])
                # None in component indicates that 'raw' data from selector should be used.
                elements = np.append(
                    elements,
                    self.derive_elements(media[_cmp[0]][self.DATA_EXT], outfolder),
                )
            else:
                # component points to derived data
                elements = np.append(
                    elements,
                    self.derive_elements(
                        media[_cmp[0]][self.DERIVED_EXT][_cmp[1]], outfolder
                    ),
                )

        return elements

    def __get_all_media(self):
        """Get all available media by indexing the folder system from self.FOLDER.
        The 'all_media' is currently an object (TODO: note its structure). It should only be used internally, here in
        the analyser base class implementation.
        Note that this function needs to be run dynamically (each time an analyser is run), as new elements may have
        been added since it was last run.
        """
        all_media = {}

        # the results from each selector sits in a folder of its name
        data_passes = [
            f for f in os.listdir(self.FOLDER) if os.path.isdir(f"{self.FOLDER}/{f}")
        ]
        derived_passes = [
            f for f in os.listdir(self.FOLDER) if os.path.isdir(f"{self.FOLDER}/{f}")
        ]

        for _pass in data_passes:
            all_media[_pass] = {Analyser.DATA_EXT: {}, Analyser.DERIVED_EXT: {}}
            data_pass = f"{self.FOLDER}/{_pass}/{Analyser.DATA_EXT}"
            data_els = [
                f
                for f in os.listdir(data_pass)
                if os.path.isdir(os.path.join(data_pass, f))
            ]
            for el_id in data_els:
                all_media[_pass][Analyser.DATA_EXT][el_id] = f"{data_pass}/{el_id}"

            derived_pass = f"{self.FOLDER}/{_pass}/{Analyser.DERIVED_EXT}"
            # NOTE: we have lots of nested loops here, but i think it's necessary...
            if not os.path.exists(derived_pass):
                break

            d_passes = [
                f
                for f in os.listdir(derived_pass)
                if os.path.isdir(os.path.join(derived_pass, f))
            ]
            for d_pass in d_passes:
                all_media[_pass][Analyser.DERIVED_EXT][d_pass] = {}
                _dpath = f"{derived_pass}/{d_pass}"
                data_els = [
                    f
                    for f in os.listdir(_dpath)
                    if os.path.isdir(os.path.join(_dpath, f))
                ]
                for el_id in data_els:
                    all_media[_pass][Analyser.DERIVED_EXT][d_pass][
                        el_id
                    ] = f"{data_pass}/{el_id}"

        return all_media

    def _run(self, config):
        self.setup_run()

        all_media = self.__get_all_media()
        elements = self.__get_elements(all_media)

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
    def run_element(self, element, config):
        """ Method defined on each analyser that implements analysis element-wise.

            An element is currently simply a path to the relevant media. TODO: elements should be a more structured
            type.

            Should create a new element in the appropriate 'derived' folder.
        """
        return NotImplemented
