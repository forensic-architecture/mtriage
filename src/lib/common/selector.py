import os
import csv
from abc import abstractmethod
from lib.common.mtmodule import MTModule
from lib.common.util import save_logs
from lib.common.exceptions import ElementShouldRetryError, ElementShouldSkipError


class Selector(MTModule):
    """A Selector implements the indexing and retrieving of media for a platform or otherwise distinct space.

    'index' and 'retrieve_element' are abstract methods that need to be defined on selectors. Other attributes and
    methods in the class should not have to be explicitly referenced by selectors, as all data necessary is passed in
    the arguments of exposed methods.
    """

    def __init__(self, config, module, folder):
        super().__init__(module, folder)
        self.DIR = f"{self.BASE_DIR}/{self.NAME}"
        self.CONFIG = config
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
    @MTModule.logged_phase("index")
    def start_indexing(self):
        element_map = self.index(self.CONFIG)
        if element_map is not None:
            with open(self.ELEMENT_MAP, "w") as f:
                writer = csv.writer(f, delimiter=",")
                for line in element_map:
                    writer.writerow(line)

    @MTModule.logged_phase("pre-retrieve")
    def __pre_retrieve(self):
        # open element_map in preparation for reading line-by-line
        self.pre_retrieve(self.CONFIG, self.ELEMENT_DIR)

    def __get_elements(self):
        with open(self.ELEMENT_MAP, "r", encoding="utf-8") as f:
            for el in csv.reader(f):
                yield el

    @MTModule.logged_phase("retrieve")
    def __retrieve(self):
        elements = self.__get_elements()
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
            element["dest"] = f"{self.ELEMENT_DIR}/{id}"
            self.__attempt_retrieve(5, element)

    @MTModule.logged_phase("post-retrieve")
    def __post_retrieve(self):
        self.post_retrieve(self.CONFIG, self.ELEMENT_DIR)

    # entrypoint
    def start_retrieving(self):
        self.__pre_retrieve()
        self.__retrieve()
        self.__post_retrieve()

    def __attempt_retrieve(self, attempts, element):
        if not os.path.exists(element["dest"]):
            os.makedirs(element["dest"])

        try:
            return self.retrieve_element(element, self.CONFIG)
        except ElementShouldSkipError as e:
            os.rmdir(element["dest"])
            self.error_logger(str(e), element)
            return
        except ElementShouldRetryError as e:
            self.error_logger(str(e), element)
            if attempts > 1:
                return self.__attempt_retrieve(attempts - 1, element)
            else:
                os.rmdir(element["dest"])
                self.error_logger(
                    "failed after maximum retries - skipping element", element
                )
                return
        except Exception as e:
            dev = self.CONFIG["dev"] if "dev" in self.CONFIG else False
            if dev:
                raise e
            else:
                self.error_logger(
                    "unknown exception raised - skipping element", element
                )
                return
