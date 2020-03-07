import glob
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, List, Union, Tuple
from lib.common.etypes import cast_to_etype, LocalElement
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
from lib.common.storage import Storage
from lib.common.etypes import Etype, LocalElement, cast_to_etype


def get_json_paths(path):
    return list(Path(path).rglob("*.[jJ][sS][oO][nN]"))


def get_video_paths(path):
    return list(Path(path).rglob("*.[mM][pP][4]"))


def get_img_paths(path):
    return list(Path(path).rglob("*.[bB][mM][pP]"))


class Analyser(MTModule):
    """ A Analyser is a pass that creates derived workables from retrieved data.

        The working directory of the selector is passed during class instantiation, and can be referenced in the
        implementations of methods.
    """
    def __init__(self, config, module, storage=None):
        super().__init__(config, module, storage)

        if not isinstance(module, str) or module == "":
            raise InvalidAnalyserConfigError(
                "You must provide a name for your analyser"
            )
        if not isinstance(storage, Storage):
            raise InvalidAnalyserConfigError("You must provide a valid storage object")
        if not "elements_in" in config:
            raise InvalidAnalyserConfigError(
                "The config must contain an 'elements_in' indicating the analyser's input."
            )
        if not isinstance(config["elements_in"], list) or not config["elements_in"]:
            raise InvalidAnalyserConfigError(
                "The 'elements_in' must be a list containing at least one string"
            )

    def construct_query(self) -> List[Tuple[str, str]]:
        """ Constructs a storage query using the "elements_in" attribute in self.CONFIG """
        q = []
        for comp in self.CONFIG["elements_in"]:
            parts = comp.split("/")

            if len(parts) is 1:
                # check selector exists
                sel = parts[0]
                q.append((sel, None))
            elif len(parts) is 2:
                if "" in parts:
                    raise InvalidElementsIn(
                        comp,
                        "If you include a '/' in a component query, it must be followed by an analyser",
                    )
                sel = parts[0]
                ana = parts[1]
                q.append((sel, ana))
        return q

    @abstractmethod
    def analyse_element(self, element: LocalElement, config):
        """ Method defined on each analyser that implements analysis element-wise.

            An element is currently simply a path to the relevant media. TODO: elements should be a more structured
            type.

            Should create a new element in the appropriate element[]'base' dir.
        """
        return NotImplemented

    def pre_analyse(self, config):
        """option to set up class variables"""

    def post_analyse(self, config):
        """option to perform any clear up"""

    def start_analysing(self, in_parallel=True):
        """ Primary entrypoint in the mtriage lifecycle.

            1. Call user-defined `pre_analyse` if it exists.
            2. Read all media from disk.
            3. Call user-defined `analyse_element` in parallel (done through @phase decorator in MTModule). The option
                to bypass parallelisation is for testing.
            4. Call user-defined `post_analyse` if it exists.
            5. Save logs, and clear the buffer. """
        self.__pre_analyse()
        all_media = self.disk.read_all_media()
        self.__analyse(all_media, in_parallel)
        self.__post_analyse()
        self.flush_logs()

    # INTERNAL METHODS
    @MTModule.phase("pre-analyse")
    def __pre_analyse(self):
        self.pre_analyse(self.CONFIG)

    def __analyse(self, media, in_parallel):
        elements = self.disk.read_media_by_query(self.construct_query())
        if in_parallel:
            self.analyse((e for e in elements))
        else:
            # analysing elements as a list will bypass parallelisation
            self.analyse(elements)

    @MTModule.phase("analyse")
    def analyse(self, elements: Union[Generator[LocalElement, None, None], List[LocalElement]]):
        """ If `elements` is a Generator, the phase decorator will run in parallel.
            If `elements` is a List, then it will run serially (which is useful for testing). """
        for element in elements:
            success = self.__attempt_analyse(5, element)

            if not success:
                shutil.rmtree(element["dest"])

            self.__carry_from_element(element)

    @MTModule.phase("post-analyse")
    def __post_analyse(self):
        self.post_analyse(self.CONFIG)

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

    def __carry_from_element(self, element: LocalElement):
        # TODO: route this through LocalStorage
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
