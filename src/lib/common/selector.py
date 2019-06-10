import os
from abc import ABC, abstractmethod
import pandas as pd
from lib.common.util import save_logs
from lib.common.exceptions import (
    ElementOperationFailedRetryError,
    ElementOperationFailedSkipError,
)


class Selector(ABC):
    """A Selector implements the indexing and retrieving of media for a platform or otherwise distinct space.

    'index' and 'retrieve_element' are abstract methods that need to be defined on selectors. Other attributes and
    methods in the class should not have to be explicitly referenced by selectors, as all data necessary is passed in
    the arguments of exposed methods.
    """

    # ALL_SELECTORS = []
    INDEX_KEY = "index"
    RETRIEVE_KEY = "retrieve"
    ERROR_KEY = "error"

    def __init__(self, config, module, folder):
        self.NAME = module
        self.BASE_DIR = folder
        self.DIR = f"{self.BASE_DIR}/{self.NAME}"
        self.ELEMENT_DIR = f"{self.DIR}/data"
        self.LOGS_DIR = f"{self.BASE_DIR}/logs"
        self.LOGS_FILE = f"{self.LOGS_DIR}/{self.NAME}.txt"

        self.ELEMENT_MAP = f"{self.DIR}/element_map.csv"

        # logs are kept in memory as index/retrieve runs, and then dumped
        # to the relevant logs file at the end of a successful operation.
        self.__LOGS = []
        # stateful variable that tells self.logger which phase we're in.
        self.__PHASE_KEY = Selector.INDEX_KEY

        # make dirs if don't exist
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)
        if not os.path.exists(self.ELEMENT_DIR):
            os.makedirs(self.ELEMENT_DIR)

    def save_and_clear_logs(self):
        save_logs(self.__LOGS, self.LOGS_FILE)
        self.__LOGS = []

    def load(self):
        """ the select DF is loaded from the appropriate file """
        return pd.read_csv(self.CSV, encoding="utf-8")

    def start_indexing(self, config):
        self__LOG_KEY = Selector.INDEX_KEY
        df = self.index(config)
        if df is not None:
            df.to_csv(self.SELECT_MAP)
        self.save_and_clear_logs()

    def logger(self, msg, element=None):
        context = f"{self.__PHASE_KEY}: "
        if element != None:
            el_id = element["id"]
            context = context + f"{el_id}: "
        msg = f"{context}{msg}"
        self.__LOGS.append(msg)
        print(msg)

    def error_logger(self, msg, element=None):
        context = f""
        if element != None:
            print("element: " + str(element))
            el_id = element["element_id"]
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

    @abstractmethod
    def index(self, config):
        """TODO: indicate the exact format this should output.
        Should populate a dataframe with the results, keep logs, and then call:
            self.index_complete(df, logs)

        REQUIRED: each result in the dataframe must contain an 'element_id' field containing
        a unique identifier for the element.

        NOTE: should be a relatively light pass that designates the space to be retrieved.
        No options for parallelisation, run on a single CPU.
        """
        raise NotImplementedError

    def setup_retrieve(self, dest, config):
        """ option to set class variables or do other work only once before each row is retrieved. """
        pass

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

    def retrieve_all(self, config):
        self.__PHASE_KEY = Selector.RETRIEVE_KEY
        df = pd.read_csv(self.SELECT_MAP, encoding="utf-8")
        self.setup_retrieve(self.ELEMENT_DIR, config)

        for index, row in df.iterrows():
            element = row.to_dict()
            element_id = row["element_id"]
            element["dest"] = f"{self.ELEMENT_FOLDER}/{element_id}"
            self.__attempt_retrieve(5, element, config)

        self.save_and_clear_logs()

    def start_retrieving(self, config):
        """ The default retrieve technique is to retrieve all. For custom retrieval heuristics,
        an overload 'retrieve' method should be specified in the preprocessor. TODO: further document, etc.
        """
        self.retrieve_all(config)

    def __attempt_retrieve(self, attempts, element, config):
        try:
            return self.retrieve_element(element, config)
        except ElementOperationFailedSkipError as e:
            self.error_logger(str(e), element)
            return
        except ElementOperationFailedRetryError as e:
            self.error_logger(str(e), element)
            if attempts > 1:
                return self.attempt_retrieve(attempts - 1, element, config)
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
