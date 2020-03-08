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
        # all_media = self.disk.read_all_media()
        self.__analyse(in_parallel)
        self.__post_analyse()
        self.flush_logs()

    # INTERNAL METHODS
    @MTModule.phase("pre-analyse")
    def __pre_analyse(self):
        self.pre_analyse(self.config)

    def __analyse(self, in_parallel):
        try:
            elements = self.disk.read_elements(self.config['elements_in'])
        except:
            raise InvalidAnalyserElements(f"The 'elements_in' you specified does not exist on the storage specified.")
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
            # NB: `super` infra is necessary in case a storage class overwrites the `read_query` method
            # as LocalStorage does.
            og_query = super(type(self.disk), self.disk).read_query(element.query)
            dest_q = f"{og_query[0]}/{self.name}"

            self.__attempt_analyse(5, element, dest_q)

    @MTModule.phase("post-analyse")
    def __post_analyse(self):
        self.post_analyse(self.config)

    def __cast_elements(self, element_dict, outdir):
        # TODO: move to etypes in `cast`
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
                f"The elements_in you specified could not be cast to {self.get_in_etype()}, the input type for the {self.name} analyser."
            )

        return els

    def __attempt_analyse(self, attempts, element, dest_q):
        try:
            new_element = self.analyse_element(element, self.config)
            success = self.disk.write_element(dest_q, new_element)
            if not success:
                raise ElementShouldRetryError("Unsuccessful storage")

        except ElementShouldSkipError as e:
            self.error_logger(str(e), element)
            return False
        except ElementShouldRetryError as e:
            self.error_logger(str(e), element)
            if attempts > 1:
                return self.__attempt_analyse(attempts - 1, element, dest_q)
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
                    f"{str(e)}: skipping element", element
                )
                return False
