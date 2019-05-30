import os
from abc import ABC, abstractmethod
import pandas as pd
from lib.common.util import save_logs


class Selector(ABC):
    """A Selector implements the indexing and retrieving of media for a platform
    or otherwise distinct space.

    The working directory of the selector is passed during class instantiation,
    and can be referenced in the implementations of methods.
    """

    ALL_SELECTORS = []

    def __init__(self, config, module, folder):
        self.BASE_FOLDER = folder
        self.NAME = module
        # unique ID
        self.ID = f"{self.NAME}_{str(len(Selector.ALL_SELECTORS))}"
        Selector.ALL_SELECTORS.append(self.ID)
        # derived instance variables
        self.FOLDER = f"{self.BASE_FOLDER}/{self.NAME}"
        self.RETRIEVE_FOLDER = f"{self.FOLDER}/data"
        self.INDEX_LOGS = f"{self.FOLDER}/index-logs.txt"
        self.SELECT_MAP = f"{self.FOLDER}/selected.csv"
        self.RETRIEVE_LOGS = f"{self.FOLDER}/retrieve-logs.txt"
        self.__retrieveLogs = []
        self.__indexLogs = []

        if not os.path.exists(self.RETRIEVE_FOLDER):
            os.makedirs(self.RETRIEVE_FOLDER)

    def load(self):
        """ the select DF is loaded from the appropriate file """
        return pd.read_csv(self.CSV, encoding="utf-8")

    def start_indexing(self, config):
        df = self.index(config)
        if df is not None:
            df.to_csv(self.SELECT_MAP)
        save_logs(self.__indexLogs, self.INDEX_LOGS)

    def index_logger(self, msg):
        self.__indexLogs.append(msg)
        print(msg)

    def retrieve_logger(self, msg):
        self.__retrieveLogs.append(msg)
        print(msg)

    @abstractmethod
    def index(self, config):
        """TODO: indicate the exact format this should output.

        Should populate a dataframe with the results, keep logs, and then call:
            self.index_complete(df, logs)

        NOTE: should be a relatively light pass that designates the space to be retrieved.
        No options for parallelisation, run on a single CPU.
        """
        raise NotImplementedError
        return pd.DataFrame()

    def setup_retrieve(self):
        """ option to set class variables or do other work only once before each row is retrieved. """
        pass

    def retrieve_row_complete(self, success):
        """ called with the path to the retrieved element (str), and the logs (list of str)
        if 'path_to_media' is None then we save logs, but nothing else.
        """
        # NOTE: nothing done with success currently
        save_logs(self.__retrieveLogs, self.RETRIEVE_LOGS)

    def _retrieve_row(self, row):
        #  store row idx for 'retrieve_row_complete'
        self.LAST_ROW_IDX = row.name
        self.retrieve_row(row)

    @abstractmethod
    def retrieve_row(self, row):
        """Retrieve takes a single element as an argument, which is a row in the dataframe
        that was produced from the 'index' method. It is called in PREPROCESS. Data that
        has already been retrieved will not be retrieved again.

        Should save a file with a supported extension to 'self.SAMPLE_FOLDER', and call:
            self.retrieve_row_complete(logs)
        when complete. Log printing is handled by the Sampler class.

        NOTE: exposed as a function for a single row so that MT can take responsibility
        for parallelisation.
        """
        # return NotImplemented

    def retrieve_all(self):
        df = pd.read_csv(self.SELECT_MAP, encoding="utf-8")
        self.setup_retrieve()
        df.apply(self._retrieve_row, axis=1)
        save_logs(self.__retrieveLogs, self.RETRIEVE_LOGS)

    def retrieve(self, config):
        """ The default retrieve technique is to retrieve all. For custom retrieval heuristics,
        an overload 'retrieve' method should be specified in the preprocessor. TODO: further document, etc.
        """
        self.retrieve_all()
