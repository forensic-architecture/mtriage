import os
import csv
from abc import abstractmethod
from typing import Dict, Generator, Union, List
from lib.common.mtmodule import MTModule
from lib.common.util import save_logs
from lib.common.exceptions import (
    InvalidElementIndex,
    ElementShouldRetryError,
    ElementShouldSkipError,
    EtypeCastError,
)
from lib.common.etypes import cast_to_etype
from lib.common.storage import LocalStorage
import shutil


import pdb
class Selector(MTModule):
    """A Selector implements the indexing and retrieving of media for a platform or otherwise distinct space.

    'index' and 'retrieve_element' are abstract methods that need to be defined on selectors. Other attributes and
    methods in the class should not have to be explicitly referenced by selectors, as all data necessary is passed in
    the arguments of exposed methods.
    """

    def __init__(self, config, module, folder, storage=LocalStorage):
        super().__init__(config, module, folder)
        self.DIR = f"{self.BASE_DIR}/{self.NAME}"
        self.disk = storage(self.DIR)

    # must be implemented by child
    @abstractmethod
    def index(self, config):
        """TODO: indicate the exact format this should output.
        Should populate a dataframe with the results, keep logs, and then call:
            self.index_complete(df, logs)

        REQUIRED: each result in the dataframe must contain an 'id' field containing
        a unique identifier for the element.

        NOTE: should be a relatively light pass that designates the space to be retrieved.
        No options for parallelisation, run on a single CPU.
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve_element(self, element, config) -> Dict[str, bytes]:
        """ Retrieve takes a single element as an argument, which is a row in the dataframe that was produced from the
        'index' method. Data that has already been retrieved will not be retrieved again.

        The method should return an object with filenames and bytestreams, which mtriage will then store appropriately.
        """
        raise NotImplementedError

    # optionally implemented by child
    # both ELEMENT_DIR and CONFIG are implicitly available on self, but passed explicitily for convenience
    def pre_retrieve(self, config: Dict):
        pass

    def post_retrieve(self, config: Dict):
        pass

    @MTModule.phase("index")
    def start_indexing(self):
        element_map = self.index(self.CONFIG)
        if element_map is not None:
            self.disk.write_elements_index(element_map)

    def start_retrieving(self, in_parallel=True):
        self.__pre_retrieve()
        elements = self.disk.read_elements_index()
        if not in_parallel:
            try:
                elements = [e for e in elements]
            except:
                raise InvalidElementIndex()
        self.__retrieve(elements)
        self.__post_retrieve()

    @MTModule.phase("pre-retrieve")
    def __pre_retrieve(self):
        self.pre_retrieve(self.CONFIG)

    @MTModule.phase("retrieve")
    def __retrieve(self, elements: Union[List, Generator]):
        for element in elements:
            success = self.__attempt_retrieve(5, element)
            if not success:
                shutil.rmtree(element.base)

    @MTModule.phase("post-retrieve")
    def __post_retrieve(self):
        self.post_retrieve(self.CONFIG)

    def __attempt_retrieve(self, attempts, element_index):
        try:
            local_element = self.retrieve_element(element_index, self.CONFIG)
            self.disk.write_element(local_element)
            return True
        except ElementShouldSkipError as e:
            self.error_logger(str(e), element)
            return False
        except ElementShouldRetryError as e:
            self.error_logger(str(e), element)
            if attempts > 1:
                return self.__attempt_retrieve(attempts - 1, element)
            else:
                self.error_logger(
                    "failed after maximum retries - skipping element", element
                )
                return False
        # TODO: flag to turn this off during development should be passed during run
        except Exception as e:
            if self.is_dev():
                raise e
            else:
                self.error_logger(
                    "unknown exception raised - skipping element", element
                )
                return False
