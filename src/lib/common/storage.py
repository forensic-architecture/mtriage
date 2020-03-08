import os
import csv
import shutil
from pathlib import Path
from types import GeneratorType, SimpleNamespace as Ns
from typing import Tuple, Union, List, Iterable, Dict
from lib.common.etypes import Etype, LocalElement, LocalElementsIndex
from lib.common.exceptions import InvalidStorageQuery
from lib.common.util import subdirs, files
from abc import ABC, abstractmethod

Component = Tuple[str, str]

class Storage(ABC):
    """
    For interfacing with an analyser's storage folder. This layer of abstraction allows storage to either take place
    locally or remotely.
    """

    def __init__(self):
        pass

    def read_query(self, query: str) -> Component:
        """ Turn a string query of the form "selector/analyser" into a Component type """
        parts = query.split("/")
        if len(parts) is 1:
            sel = parts[0]
            return (sel, None)
        elif len(parts) is 2:
            if "" in parts:
                raise InvalidStorageQuery(
                    comp,
                    "If you include a '/' in a component query, it must be followed by an analyser",
                )
            sel = parts[0]
            ana = parts[1]
            return (sel, ana)

    @abstractmethod
    def read_elements_index(self, q:str) -> LocalElementsIndex:
        """ Returns a generator of elements, where each item is the object to be passed to `get_element` """
        pass

    @abstractmethod
    def write_elements_index(self, q:str, eidx: LocalElementsIndex):
        """ Setter for the list of pointers to the URLs where elements should be retrieved. """
        pass



class LocalStorage(Storage):
    """
    Stores elements in an element_map.csv.
    """
    RETRIEVED_EXT = "data"
    ANALYSED_EXT = "derived"
    ELEMENTS_INDEX_FILE = "element_map.csv"

    def __init__(self, folder=None):
        self.base_dir = Path(folder)

        # selecting
        self.ELEMENT_DIR = lambda name: Path(f"{folder}/{name}/data")
        self.ELEMENT_MAP = lambda name: Path(f"{folder}/{name}/element_map.csv")
        self.headers = []
        self.delete_local_on_write = True #mainly exists for testing, manually set to False

        # logging
        self.__LOGS_DIR = f"{self.base_dir}/logs"
        self.__LOGS_FILE = f"{self.__LOGS_DIR}/logs.txt"

        if not os.path.exists(self.__LOGS_DIR):
            os.makedirs(self.__LOGS_DIR)

    def read_query(self, query: str) -> Path:
        """ Override parent `read_query` to return the valid Path """
        cmp = super().read_query(query)
        is_analyser = cmp[1] is not None
        if not is_analyser:
            return self.base_dir/cmp[0]/self.RETRIEVED_EXT
        else:
            return self.base_dir/cmp[0]/self.ANALYSED_EXT/cmp[1]

    def read_elements_index(self, q:str) -> LocalElementsIndex:
        dest = self.read_query(q)
        def get_rows():
            with open(dest/self.ELEMENTS_INDEX_FILE, "r", encoding="utf-8") as f:
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

    def write_elements_index(self, q:str, eidx:LocalElementsIndex):
        # TODO: validate id column exists on csv for all rows
        dest = self.read_query(q)
        if not dest.exists():
            dest.mkdir(parents=True, exist_ok=True)

        with open(dest/self.ELEMENTS_INDEX_FILE, "w") as f:
            writer = csv.writer(f, delimiter=",")
            for line in eidx.rows:
                writer.writerow(line)

    def read_element(self, q:str, id: str) -> LocalElement:
        pass

    def write_element(self, q:str, element:LocalElement) -> bool:
        """ Write a LocalElement to persistent storage, deleting the LocalElement afterwards.
            Returns True if successful, false if otherwise. """

        dest = self.read_query(q)
        if not os.path.exists(dest):
            os.makedirs(dest)


        base = dest/element.id
        if not os.path.exists(base):
            os.makedirs(base)

        for idx, e in enumerate(element.paths):
            if not isinstance(e, Path): e = Path(e)
            # deletes LocalElement by moving
            if self.delete_local_on_write:
                shutil.move(e, base/e.name)
            else:
                shutil.copyfile(e, base/e.name)


    def remove_element(self, q:str, id:str):
        d = self.read_query(q)/id
        if os.path.exists(d):
            shutil.rmtree(d)

    def write_logs(self, logs:List[str]):
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

    def read_elements(self, qs:List[str]) -> List[LocalElement]:
        """ Take a list of queries, and returns a flattened list of LocalElements for the specified folders. The order
            of the query is maintained in the return value. """
        els = []
        for q in qs:
            element_pth = self.read_query(q)
            el_paths = subdirs(element_pth)
            els.extend([LocalElement(id=el.name, paths=files(el), query=q) for el in el_paths])
        return els



