import glob
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, List, Union
from lib.common.etypes import cast_to_etype
from lib.common.exceptions import (
    ElementShouldSkipError,
    ElementShouldRetryError,
    InvalidAnalyserConfigError,
    MTriageStorageCorruptedError,
    InvalidElementsIn,
    InvalidAnalyserElements,
    EtypeCastError,
    InvalidCarry,
)
from lib.common.mtmodule import MTModule
from lib.common.etypes import Etype, cast_to_etype


def get_json_paths(path):
    return list(Path(path).rglob("*.[jJ][sS][oO][nN]"))


def get_video_paths(path):
    return list(Path(path).rglob("*.[mM][pP][4]"))


def get_img_paths(path):
    return list(Path(path).rglob("*.[bB][mM][pP]"))


def check_valid_element_folder(comp, element_dir):
    try:
        _, dirs, files = next(os.walk(element_dir))
        if len(dirs) == 0 or len(files) > 0:
            raise Exception()
    except:
        raise InvalidElementsIn(
            comp,
            "The folder it represents contains no elements or is otherwise corrupted.",
        )


class Analyser(MTModule):
    """ A Analyser is a pass that creates derived workables from retrieved data.

        The working directory of the selector is passed during class instantiation, and can be referenced in the
        implementations of methods.
    """

    DATA_EXT = "data"
    DERIVED_EXT = "derived"

    def __init__(self, config, module, directory):
        try:
            super().__init__(config, module, directory)
        except PermissionError:
            raise InvalidAnalyserConfigError("You must provide a valid directory path")

        if not "elements_in" in config:
            raise InvalidAnalyserConfigError(
                "The config must contain an 'elements_in' indicating the analyser's input."
            )
        if not isinstance(config["elements_in"], list) or not config["elements_in"]:
            raise InvalidAnalyserConfigError(
                "The 'elements_in' must be a list containing at least one string"
            )

        if not isinstance(module, str) or module == "":
            raise InvalidAnalyserConfigError(
                "You must provide a name for your analyser"
            )

        if not isinstance(directory, str):
            raise InvalidAnalyserConfigError("You must provide a valid directory path")

    @abstractmethod
    def analyse_element(self, element, config):
        """ Method defined on each analyser that implements analysis element-wise.

            An element is currently simply a path to the relevant media. TODO: elements should be a more structured
            type.

            Should create a new element in the appropriate element[]'base' dir.
        """
        return NotImplemented

    def start_analysing(self, in_parallel=True):
        """ Primary entrypoint in the mtriage lifecycle.

            1. Call user-defined `pre_analyse` if it exists.
            2. Read all media from disk.
            3. Call user-defined `analyse_element` in parallel (done through @phase decorator in MTModule). The option
                to bypass parallelisation is for testing.
            4. Call user-defined `post_analyse` if it exists.
            5. Save logs, and clear the buffer. """
        self.__pre_analyse()
        all_media = self.__get_all_media()
        self.__analyse(all_media, in_parallel)
        self.__post_analyse()
        self.save_and_clear_logs()

    def pre_analyse(self, config):
        """option to set up class variables"""

    def post_analyse(self, config, derived_dirs):
        """option to perform any clear up"""

    def __get_in_cmps(self):
        """ Take a list of input paths--of the form '{selector_name}/{?analyser_name}'-- and produces a list of components.
            Components are tuples whose first value is the name of a selector, and whose second value is either the name of
            an analyser, or None.
        """
        whitelist = self.CONFIG["elements_in"]
        all_parts = []
        for comp in whitelist:
            parts = comp.split("/")

            if len(parts) is 1:
                # check selector exists
                selname = parts[0]
                element_dir = f"{self.BASE_DIR}/{selname}/{Analyser.DATA_EXT}/"
                check_valid_element_folder(comp, element_dir)
                all_parts.append((selname, None))
            elif len(parts) is 2:
                if "" in parts:
                    raise InvalidElementsIn(
                        comp,
                        "If you include a '/' in a component, it must be followed by an analyser",
                    )
                selname = parts[0]
                analysername = parts[1]
                element_dir = (
                    f"{self.BASE_DIR}/{selname}/{Analyser.DERIVED_EXT}/{analysername}"
                )
                check_valid_element_folder(comp, element_dir)
                all_parts.append((selname, analysername))
            else:
                raise InvalidElementsIn(
                    comp,
                    "It must be a list of strings in the format 'selector_name/analyser_name', where the analyser_name is optional.",
                )

        return all_parts

    # INTERNAL METHODS\
    @MTModule.phase("pre-analyse")
    def __pre_analyse(self):
        self.pre_analyse(self.CONFIG)

    def __analyse(self, media, in_parallel):
        elements = self.__get_in_elements(media)
        if in_parallel:
            self.analyse((e for e in elements))
        else:
            # analysing elements as a list will bypass parallelisation
            self.analyse(elements)

    @MTModule.phase("analyse")
    def analyse(self, elements: Union[Generator, List]):
        """ If `elements` is a Generator, the phase decorator will run in parallel.
            If `elements` is a List, then it will run serially (which is useful for testing). """
        for element in elements:
            success = self.__attempt_analyse(5, element)

            if not success:
                shutil.rmtree(element["dest"])

            self.__carry_from_element(element)

    @MTModule.phase("post-analyse")
    def __post_analyse(self):
        self.post_analyse(self.CONFIG, self.__get_out_dirs())

    def __cast_elements(self, element_dict, outdir):
        def attempt_cast_el(key):
            el_path = element_dict[key]
            etyped_attrs = cast_to_etype(el_path, self.get_in_etype())
            return {"id": key, "dest": f"{outdir}/{key}", **etyped_attrs}

        els = []
        for key in element_dict.keys():
            try:
                element = attempt_cast_el(key)
                els.append(element)
            except EtypeCastError as e:
                self.error_logger(str(e), element={"id": key})

        if len(els) is 0:
            raise InvalidAnalyserElements(
                f"The elements_in you specified could not be cast to {self.get_in_etype()}, the input type for the {self.NAME} analyser."
            )

        return els

    def __carry_from_element(self, element):
        if "carry" not in self.CONFIG:
            return

        to_carry = self.CONFIG["carry"]
        if not (isinstance(to_carry, str) or isinstance(to_carry, List)):
            raise InvalidCarry("you must pass a single string or a list of strings.")

        def carry_matches(glob):
            for path in Path(element["base"]).rglob(glob):
                shutil.copyfile(path, f"{element['dest']}/{path.name}")

        if isinstance(to_carry, str):
            carry_matches(to_carry)
        else:  # must be a list
            for matcher in to_carry:
                carry_matches(matcher)

    def __get_out_dirs(self):
        whitelist = self.CONFIG["elements_in"]
        dirs = set([])
        for _cmp in self.__get_in_cmps():
            selname = _cmp[0]
            analysername = _cmp[1]
            outdir = self.__get_out_dir(selname)
            dirs.add(outdir)
        return list(dirs)

    def __get_in_elements(self, media):
        whitelist = self.CONFIG["elements_in"]
        etyped_elements = []
        in_cmps = self.__get_in_cmps()

        for _cmp in in_cmps:
            selname = _cmp[0]
            analysername = _cmp[1]
            outdir = self.__get_out_dir(selname)
            is_selector = analysername is None

            element_dict = (
                media[selname][self.DATA_EXT]
                if is_selector
                else media[selname][self.DERIVED_EXT][analysername]
            )
            _etyped_elements = self.__cast_elements(element_dict, outdir)
            etyped_elements.extend(_etyped_elements)

        return etyped_elements

    def __get_all_media(self):
        """Get all available media by indexing the dir system from self.BASE_DIR.
        The 'all_media' is currently an object (TODO: note its structure). It should only be used internally, here in
        the analyser base class implementation.
        Note that this function needs to be run dynamically (each time an analyser is run), as new elements may have
        been added since it was last run.
        """
        all_media = {}

        # the results from each selector sits in a dir of its name
        selectors = [
            f
            for f in os.listdir(self.BASE_DIR)
            if (os.path.isdir(f"{self.BASE_DIR}/{f}") and f != "logs")
        ]

        # Elements are all associated with a selector. Those that come straight from the selector are housed in 'data'.
        # Those that have been derived in some way, either straight from the data, or from a previous derived dir,
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
            derived_dir = f"{self.BASE_DIR}/{selector}/{Analyser.DERIVED_EXT}"

            if not os.path.exists(derived_dir):
                continue

            analysers = [
                f
                for f in os.listdir(derived_dir)
                if os.path.isdir(os.path.join(derived_dir, f))
            ]

            for _analyser in analysers:
                all_media[selector][Analyser.DERIVED_EXT][_analyser] = {}
                _dpath = f"{derived_dir}/{_analyser}"

                _elements = [
                    f
                    for f in os.listdir(_dpath)
                    if os.path.isdir(os.path.join(_dpath, f))
                ]

                for el_id in _elements:
                    all_media[selector][Analyser.DERIVED_EXT][_analyser][
                        el_id
                    ] = f"{derived_dir}/{_analyser}/{el_id}"

        return all_media

    def __get_out_dir(self, selector):
        """Returns the path to a derived dir from a string selector"""
        derived_dir = f"{self.BASE_DIR}/{selector}/{Analyser.DERIVED_EXT}/{self.NAME}"

        return derived_dir

    def __attempt_analyse(self, attempts, element):
        dest = element["dest"]
        if not os.path.exists(dest):
            os.makedirs(dest)
        try:
            self.analyse_element(element, self.CONFIG)
            return True
        except ElementShouldSkipError as e:
            self.error_logger(str(e), element)
            return False
        except ElementShouldRetryError as e:
            self.error_logger(str(e), element)
            if attempts > 1:
                return self.__attempt_analyse(attempts - 1, element)
            else:
                self.error_logger(
                    "failed after maximum retries - skipping element", element
                )
                return False
        except Exception as e:
            if self.is_dev():
                raise e
            else:
                self.error_logger(
                    "unknown exception raised - skipping element", element
                )
                return False

    # STATIC METHODS
    @staticmethod
    def find_video_paths(element_path):
        return get_video_paths(element_path)

    @staticmethod
    def find_img_paths(element_path):
        return get_img_paths(element_path)

    @staticmethod
    def find_json_paths(element_path):
        return get_json_paths(element_path)
