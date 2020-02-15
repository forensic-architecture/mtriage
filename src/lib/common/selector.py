import os
import csv
from abc import abstractmethod
from lib.common.mtmodule import MTModule
from lib.common.util import save_logs
from lib.common.exceptions import (
    ElementShouldRetryError,
    ElementShouldSkipError,
    EtypeCastError,
)
from lib.common.etypes import cast_to_etype
import shutil


class Selector(MTModule):
    """A Selector implements the indexing and retrieving of media for a platform or otherwise distinct space.

    'index' and 'retrieve_element' are abstract methods that need to be defined on selectors. Other attributes and
    methods in the class should not have to be explicitly referenced by selectors, as all data necessary is passed in
    the arguments of exposed methods.
    """

    def __init__(self, config, module, folder):
        super().__init__(config, module, folder)
        self.DIR = f"{self.BASE_DIR}/{self.NAME}"
        self.ELEMENT_DIR = f"{self.DIR}/data"
        self.ELEMENT_MAP = f"{self.DIR}/element_map.csv"

        if not os.path.exists(self.ELEMENT_DIR):
            os.makedirs(self.ELEMENT_DIR)

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
    def retrieve_element(self, element, config):
        """Retrieve takes a single element as an argument, which is a row in the dataframe
        that was produced from the 'index' method. It is called in PREPROCESS. Data that
        has already been retrieved will not be retrieved again.

        Should save a file with a supported extension to 'self.SAMPLE_FOLDER', and call:
            self.retrieve_row_complete(logs)
        when complete. Log printing is handled by the Sampler class.

        NOTE: exposed as a function for a single row so that MT can take responsibility
        for parallelisation.
        """
        raise NotImplementedError

    # optionally implemented by child
    # both ELEMENT_DIR and CONFIG are implicitly available on self, but passed explicitily for convenience
    def pre_retrieve(self, config, element_dir):
        pass

    def post_retrieve(self, config, element_dir):
        pass

    # logged phases that this class manages
    @MTModule.phase("index")
    def start_indexing(self):
        element_map = self.index(self.CONFIG)
        # TODO: validate id column exists on csv for all rows
        if element_map is not None:
            with open(self.ELEMENT_MAP, "w") as f:
                writer = csv.writer(f, delimiter=",")
                for line in element_map:
                    writer.writerow(line)

    @MTModule.phase("pre-retrieve")
    def __pre_retrieve(self):
        # open element_map in preparation for reading line-by-line
        self.pre_retrieve(self.CONFIG, self.ELEMENT_DIR)

    def __get_elements(self):
        with open(self.ELEMENT_MAP, "r", encoding="utf-8") as f:
            for el in csv.reader(f):
                yield el

    @MTModule.phase("retrieve", in_parallel=False)
    def __retrieve(self, elements):
        headers = next(elements)

        def to_dict(el):
            out = {}
            for idx, item in enumerate(el):
                attr = headers[idx]
                out[attr] = item
            return out

        for row in elements:
            element = to_dict(row)
            id = element["id"]
            element["base"] = f"{self.ELEMENT_DIR}/{id}"
            success = self.__attempt_retrieve(5, element)
            if success:
                etype = self.get_out_etype()
                try:
                    cast_to_etype(element["base"], etype)
                except EtypeCastError:
                    self.error_logger(
                        f"Failed to cast - retrieved element was not {etype}", element
                    )
                    shutil.rmtree(element["base"])
            else:
                shutil.rmtree(element["base"])

    @MTModule.phase("post-retrieve")
    def __post_retrieve(self):
        self.post_retrieve(self.CONFIG, self.ELEMENT_DIR)

    # entrypoint
    def start_retrieving(self):
        self.__pre_retrieve()
        elements = self.__get_elements()
        self.__retrieve(elements)
        self.__post_retrieve()

    def __attempt_retrieve(self, attempts, element):
        if not os.path.exists(element["base"]):
            os.makedirs(element["base"])

        try:
            self.retrieve_element(element, self.CONFIG)
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
