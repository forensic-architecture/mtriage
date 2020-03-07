import os
import csv
import shutil
from pathlib import Path
from types import GeneratorType, SimpleNamespace as Ns
from typing import Union, List, Iterable, Dict
from lib.common.etypes import Etype, LocalElement, LocalElementsIndex
from lib.common.exceptions import InvalidComponentQuery
from abc import ABC, abstractmethod
import pdb

class Storage(ABC):
    """
    For interfacing with an analyser's storage folder. This layer of abstraction allows storage to either take place
    locally or remotely.
    """

    def __init__(self):
        pass

    @abstractmethod
    def read_elements_index(self) -> GeneratorType:
        """ Returns a generator of elements, where each item is the object to be passed to `get_element` """
        pass

    @abstractmethod
    def write_elements_index(self, element: Iterable):
        """ Setter for the list of pointers to the URLs where elements should be retrieved. """
        pass

class LocalStorage(Storage):
    """
    Stores elements in an element_map.csv.
    """
    RETRIEVED_EXT = "data"
    ANALYSED_EXT = "derived"

    def __init__(self, folder=None):
        self.base_dir = Path(folder)

        # selecting
        self.ELEMENT_DIR = Path(f"{folder}/data")
        self.ELEMENT_MAP = Path(f"{folder}/element_map.csv")
        self.headers = []
        self.delete_local_on_write = True #mainly exists for testing, manually set to False

        if not os.path.exists(self.ELEMENT_DIR):
            os.makedirs(self.ELEMENT_DIR)

        # logging
        self.__LOGS_DIR = f"{self.base_dir}/logs"
        self.__LOGS_FILE = f"{self.__LOGS_DIR}/logs.txt"

        if not os.path.exists(self.__LOGS_DIR):
            os.makedirs(self.__LOGS_DIR)


    def read_elements_index(self) -> LocalElementsIndex:
        def get_rows():
            with open(self.ELEMENT_MAP, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    if idx == 0:
                        self.headers = row
                        continue
                    obj = Ns()
                    allvls = dict(zip(self.headers, row))
                    obj = Ns(**allvls)

                    yield obj

        return LocalElementsIndex(rows=get_rows())

    def write_elements_index(self, eidx: LocalElementsIndex):
        # TODO: validate id column exists on csv for all rows
        with open(self.ELEMENT_MAP, "w") as f:
            writer = csv.writer(f, delimiter=",")
            for line in eidx.rows:
                writer.writerow(line)

    def read_element(self, element: Dict):
        pass

    def write_element(self, element: LocalElement) -> bool:
        """ Write a LocalElement to persistent storage, deleting the LocalElement afterwards.
            Returns True if successful, false if otherwise. """
        base = self.ELEMENT_DIR/element.id
        if not os.path.exists(base):
            os.makedirs(base)

        if element.is_file_ref:
            if not isinstance(element.source, list):
                if isinstance(element.source, str): element.source = Path(element.source)
                # deletes LocalElement by moving
                if self.delete_local_on_write:
                    shutil.move(element.source, base/f"0{element.source.suffix}")
                else:
                    shutil.copyfile(element.source, base/f"0{element.source.suffix}")
            else:
                for idx, e in enumerate(element.source):
                    shutil.move(e.path, base/f"{idx}{e.path.suffix}")

    def remove_element(self, id: str):
        d = self.ELEMENT_DIR/id
        if os.path.exists(d):
            shutil.rmtree(d)

    def write_logs(self, logs: List[str]):
        if len(logs) <= 0:
            return
        with open(self.__LOGS_FILE, "a") as f:
            for l in logs:
                if l is not None:
                    f.write(l)
                    f.write("\n")

    def read_all_media(self):
        """Get all available media by indexing the dir system from self.BASE_DIR.
        The 'all_media' is currently an object (TODO: note its structure). It should only be used internally, here in
        the analyser base class implementation.
        Note that this function needs to be run dynamically (each time an analyser is run), as new elements may have
        been added since it was last run.
        Elements are all associated with a selector. Those that come straight from the selector are housed in 'data'.
        Those that have been derived in some way, either straight from the data, or from a previous derived dir,
        are in 'derived'.

        .
        +-- selector1
        |   +-- data
        |   |   +-- element1
        |   |   +-- element2
        |   +-- derived
        |   |   +-- analyser1
        |   |   |   +-- element1
        |   |   |   +-- element2
        |   |   +-- analyser2
        |   |   |   +-- element1
        |   |   |   +-- element2
        """

        all_media = {}

        # the results from each selector sits in a dir of its name
        selectors = [
            f
            for f in os.listdir(self.base_dir)
            if (os.path.isdir(self.base_dir/f) and f != "logs")
        ]

        for selector in selectors:
            all_media[selector] = {self.RETRIEVED_EXT: {}, self.ANALYSED_EXT: {}}

            # add all original elements
            data_pass = self.base_dir/selector/self.RETRIEVED_EXT
            _elements = [
                f
                for f in os.listdir(data_pass)
                if os.path.isdir(os.path.join(data_pass, f))
            ]

            for el_id in _elements:
                all_media[selector][self.RETRIEVED_EXT][el_id] = data_pass/el_id

            # add all derived elements
            derived_dir = self.base_dir/selector/self.ANALYSED_EXT

            if not os.path.exists(derived_dir):
                continue

            analysers = [
                f
                for f in os.listdir(derived_dir)
                if (derived_dir/f).is_dir()
            ]

            for _analyser in analysers:
                all_media[selector][self.ANALYSED_EXT][_analyser] = {}
                _dpath = derived_dir/_analyser

                _elements = [
                    f
                    for f in os.listdir(_dpath)
                    if (_dpath/f).is_dir()
                ]

                for el_id in _elements:
                    all_media[selector][self.ANALYSED_EXT][_analyser][
                        el_id
                    ] = derived_dir/_analyser/el_id

        return all_media

    def read_media_by_query(self, query: List[str]):
        """ Take a list of input paths--of the form '{selector_name}/{?analyser_name}'-- and produces a list of
        components.  Components are tuples whose first value is the name of a selector, and whose second value is either
        the name of an analyser, or None.
        """
        etyped_elements = []
        for _cmp in query:
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



