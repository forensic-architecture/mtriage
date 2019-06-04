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
            return {"id": key, "src": data_obj[key], "dest": f"{outfolder}/{key}"}

        return np.array(list(map(derive_el, list(data_obj.keys()))))

    def __get_elements(self, media):
        """ Derive which elements to use from available media base on the ELEMENTS_IN attr in self.CONFIG.
        """
        whitelist = self.CONFIG["elements_in"]
        cmps = paths_to_components(whitelist)

        elements = np.array([])
        for _cmp in cmps:
            outfolder = self.get_derived_folder(_cmp[0])

            if _cmp[1] is None:
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
        selectors = [
            f for f in os.listdir(self.FOLDER) if os.path.isdir(f"{self.FOLDER}/{f}")
        ]

        # Elements are all associated with a selector. Those that come straight from the selector are housed in 'data'.
        # Those that have been derived in some way, either straight from the data, or from a previous derived folder,
        # are in 'derived'.

        # .
        # +-- selector1
        # |   +-- data
        # |   |   +-- element1
        # |   |   +-- element2
        # |   +-- derived
        # |   |   +-- analyser1
        # |   |   |   +-- element1
        # |   |   |   +-- element2
        # |   |   +-- analyser2
        # |   |   |   +-- element1
        # |   |   |   +-- element2
        for selector in selectors:
            all_media[selector] = {Analyser.DATA_EXT: {}, Analyser.DERIVED_EXT: {}}

            # add all original elements
            data_pass = f"{self.FOLDER}/{selector}/{Analyser.DATA_EXT}"
            _elements = [
                f
                for f in os.listdir(data_pass)
                if os.path.isdir(os.path.join(data_pass, f))
            ]

            for el_id in _elements:
                all_media[selector][Analyser.DATA_EXT][el_id] = f"{data_pass}/{el_id}"

            # add all derived elements
            derived_folder = f"{self.FOLDER}/{selector}/{Analyser.DERIVED_EXT}"

            if not os.path.exists(derived_folder):
                continue

            analysers = [
                f
                for f in os.listdir(derived_folder)
                if os.path.isdir(os.path.join(derived_folder, f))
            ]

            for _analyser in analysers:
                all_media[selector][Analyser.DERIVED_EXT][_analyser] = {}
                _dpath = f"{derived_folder}/{_analyser}"

                _elements = [
                    f
                    for f in os.listdir(_dpath)
                    if os.path.isdir(os.path.join(_dpath, f))
                ]

                for el_id in _elements:
                    all_media[selector][Analyser.DERIVED_EXT][_analyser][
                        el_id
                    ] = f"{derived_folder}/{_analyser}/{el_id}"

        return all_media

    def _run(self, config):
        self.setup_run(config)

        all_media = self.__get_all_media()
        elements = self.__get_elements(all_media)

        for element in elements:
            # TODO: create try/catch infrastructure to delete this folder if there is an error.
            if not os.path.exists(element["dest"]):
                os.makedirs(element["dest"])

            self.analyse_element(element, config)

        self.post_analyse(config)
        save_logs(self.__logs, self.ANALYSER_LOGS)

    def setup_run(self, config):
        """option to set up class variables"""
        pass

    def post_analyse(self, config):
        """option to perform any clear up"""
        pass

    def get_derived_folder(self, selector):
        """Returns the path to a derived folder from a string selector"""
        derived_folder = f"{self.FOLDER}/{selector}/{Analyser.DERIVED_EXT}/{self.NAME}"
        if not os.path.exists(derived_folder):
            os.makedirs(derived_folder)

        return derived_folder

    @abstractmethod
    def analyse_element(self, element, config):
        """ Method defined on each analyser that implements analysis element-wise.

            An element is currently simply a path to the relevant media. TODO: elements should be a more structured
            type.

            Should create a new element in the appropriate 'derived' folder.
        """
        return NotImplemented
