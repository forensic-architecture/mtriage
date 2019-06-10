import glob
import os
import shutil
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path
from lib.common.util import save_logs
from lib.common.exceptions import (
    ElementOperationFailedSkipError,
    ElementOperationFailedRetryError,
)


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

    DATA_EXT = "data"
    DERIVED_EXT = "derived"
    PRE_ANALYSE_KEY = "preanalyse"
    MAIN_ANALYSE_KEY = "analyse"
    POST_ANLALYSE_KEY = "postanalyse"

    def __init__(self, config, module, folder):
        self.NAME = module
        self.CONFIG = config
        self.BASE_DIR = folder
        self.LOGS_DIR = f"{self.BASE_DIR}/logs"
        self.LOGS_FILE = f"{self.LOGS_DIR}/{self.NAME}.txt"

        # setup for phases of logging
        self.__LOGS =  []
        self.__PHASE_KEY = Analyser.PRE_ANALYSE_KEY

        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)

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

    def save_and_clear_logs():
        save_logs(self.__LOGS, self.__LOGS_FILE)
        self.__LOGS = []

    # INTERNAL METHODS
    def logger(self, msg, element=None):
        context = f"{self.NAME}: {self.__PHASE_KEY}: "
        if element != None:
            el_id = element["id"]
            context = context + f"{el_id}: "
        msg = f"{context}{msg}"
        self.__LOGS.append(msg)

        print(msg)

    def error_logger(self, msg, element=None):
        context = f"{self.NAME}: "
        if element != None:
            print("element: " + str(element))
            el_id = element["id"]
            context = context + f"{el_id}: "
        err_msg = f"ERROR: {context}{msg}"
        self.__LOGS.append("")
        self.__LOGS.append(
            "-----------------------------------------------------------------------------"
        )
        self.__LOGS.append(err_msg)
        self.__LOGS.append(
            "-----------------------------------------------------------------------------"
        )
        self.__LOGS.append("")
        err_msg = f"\033[91m{err_msg}\033[0m"
        print(err_msg)

    def derive_elements(self, data_obj, outfolder):
        """ An 'element' (as it is passed to the 'run_element' method that is exposed on analysers) is currently a
            dictionary with the following attributes:
                path: The path to the element that should be analysed.
                dest: The path to the folder where element analysis should be printed.
        """

        def derive_el(key):
            return {
                "id": key,
                "derived_folder": outfolder,
                "src": data_obj[key],
                "dest": f"{outfolder}/{key}",
            }

        return np.array(list(map(derive_el, list(data_obj.keys()))))

    def __get_elements(self, media):
        """ Derive which elements to use from available media base on the ELEMENTS_IN attr in self.CONFIG.
        """
        whitelist = self.CONFIG["elements_in"]
        cmps = paths_to_components(whitelist)

        elements = np.array([])
        for _cmp in cmps:
            outfolder = self.__get_derived_folder(_cmp[0])

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
        """Get all available media by indexing the folder system from self.BASE_DIR.
        The 'all_media' is currently an object (TODO: note its structure). It should only be used internally, here in
        the analyser base class implementation.
        Note that this function needs to be run dynamically (each time an analyser is run), as new elements may have
        been added since it was last run.
        """
        all_media = {}

        # the results from each selector sits in a folder of its name
        selectors = [
            f
            for f in os.listdir(self.BASE_DIR)
            if (os.path.isdir(f"{self.BASE_DIR}/{f}") and f != "analyser-logs")
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
            data_pass = f"{self.BASE_DIR}/{selector}/{Analyser.DATA_EXT}"
            _elements = [
                f
                for f in os.listdir(data_pass)
                if os.path.isdir(os.path.join(data_pass, f))
            ]

            for el_id in _elements:
                all_media[selector][Analyser.DATA_EXT][el_id] = f"{data_pass}/{el_id}"

            # add all derived elements
            derived_folder = f"{self.BASE_DIR}/{selector}/{Analyser.DERIVED_EXT}"

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
        self.__PHASE_KEY = Analyser.PRE_ANALYSE_KEY
        self.pre_analyse(config)

        self.__PHASE_KEY = Analyser.MAIN_ANALYSE_KEY
        all_media = self.__get_all_media()
        elements = self.__get_elements(all_media)

        derived_folders = set([])
        for element in elements:
            # TODO: create try/catch infrastructure to delete this folder if there is an error.
            if not os.path.exists(element["dest"]):
                os.makedirs(element["dest"])

            self.__attempt_analyse(5, element, config)
            derived_folders.add(element["derived_folder"])

        self.__PHASE_KEY = Analyser.POST_ANLALYSE_KEY
        self.post_analyse(config, derived_folders)

        self.save_and_clear_logs()

    def pre_analyse(self, config):
        """option to set up class variables"""
        pass

    def post_analyse(self, config, derived_folders):
        """option to perform any clear up"""
        pass

    def __get_derived_folder(self, selector):
        """Returns the path to a derived folder from a string selector"""
        derived_folder = (
            f"{self.BASE_DIR}/{selector}/{Analyser.DERIVED_EXT}/{self.NAME}"
        )
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

    def __attempt_analyse(self, attempts, element, config):
        try:
            self.analyse_element(element, config)
        except ElementOperationFailedSkipError as e:
            self.error_logger(str(e), element)
            return
        except ElementOperationFailedRetryError as e:
            self.error_logger(str(e), element)
            if attempts > 1:
                return self.attempt_analyse(attempts - 1, element, config)
            else:
                self.error_logger(
                    "failed after maximum retries - skipping element", element
                )
                return
        except Exception as e:
            dev = config["dev"] if "dev" in config else False
            if dev:
                raise e
            else:
                self.error_logger(
                    "unknown exception raised - skipping element", element
                )
                return
