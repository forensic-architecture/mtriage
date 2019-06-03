import os
from abc import ABC, abstractmethod
import pandas as pd
from lib.common.util import save_logs


class Selector(ABC):
    """A Selector implements the indexing and retrieving of media for a platform or otherwise distinct space.

    'index' and 'retrieve_element' are abstract methods that need to be defined on selectors. Other attributes and
    methods in the class should not have to be explicitly referenced by selectors, as all data necessary is passed in
    the arguments of exposed methods.
    """

    ALL_SELECTORS = []
    INDEX_KEY = "index"
    RETRIEVE_KEY = "retrieve"

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
        self.__LOGS = {Selector.INDEX_KEY: [], Selector.RETRIEVE_KEY: []}
        self.__LOG_KEY = Selector.INDEX_KEY

        if not os.path.exists(self.RETRIEVE_FOLDER):
            os.makedirs(self.RETRIEVE_FOLDER)

    def load(self):
        """ the select DF is loaded from the appropriate file """
        return pd.read_csv(self.CSV, encoding="utf-8")

    def start_indexing(self, config):
        self__LOG_KEY = Selector.INDEX_KEY
        df = self.index(config)
        if df is not None:
            df.to_csv(self.SELECT_MAP)
        save_logs(self.__LOGS[Selector.INDEX_KEY], self.INDEX_LOGS)

    def logger(self, msg):
        self.__LOGS[self.__LOG_KEY].append(msg)
        print(msg)

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
        self.__LOG_KEY = Selector.RETRIEVE_KEY
        df = pd.read_csv(self.SELECT_MAP, encoding="utf-8")
        self.setup_retrieve(self.RETRIEVE_FOLDER, config)

        for index, row in df.iterrows():
            element = row.to_dict()
            element_id = row["element_id"]
            element["dest"] = f"{self.RETRIEVE_FOLDER}/{element_id}"
            self.retrieve_element(element, config)

        save_logs(self.__LOGS[Selector.RETRIEVE_KEY], self.RETRIEVE_LOGS)

    def start_retrieving(self, config):
        """ The default retrieve technique is to retrieve all. For custom retrieval heuristics,
        an overload 'retrieve' method should be specified in the preprocessor. TODO: further document, etc.
        """
        self.retrieve_all(config)
