import os
import csv
from Pathlib import Path
from types import GeneratorType, IterableType
from abc import ABC, abstractmethod


class Storage(ABC):
    """
    For interfacing with an analyser's storage folder. This layer of abstraction allows storage to either take place
    locally or remotely.
    """

    def __init__(self, name):
        self.ELEMENT_DIR = f"{name}/data"
        # build folder
        pass

    @abstractmethod
    def read_elements_index(self) -> GeneratorType:
        """ Returns a generator of elements, where each item is the object to be passed to `get_element` """
        pass

    @abstractmethod
    def write_elements_index(self, element: IterableType):
        """ Setter for the list of pointers to the URLs where elements should be retrieved. """
        pass

    @abstractmethod
    def store(self, el, path):
        pass

    @abstractmethod
    def get_element(self, element):
        pass



class LocalStorage(Storage):
    """
    Stores elements in an element_map.csv.
    """

    def __init__(self, name):
        self.ELEMENT_DIR = Path(f"{name}/data")
        self.ELEMENT_MAP = Path(f"{name}/element_map.csv")
        self.headers = []

        if not os.path.exists(self.ELEMENT_DIR):
            os.makedirs(self.ELEMENT_DIR)

    def read_elements_index(self):
        with open(self.ELEMENT_MAP, "r", encoding="utf-8") as f:
            reader = csv.reader(f):
            self.headers = reader[0]
            for row in reader[1:]:
                obj = {}
                for hdr, vl in zip(self.headers, row):
                    if hdr == "id":
                        vl = self.ELEMENT_DIR/Path(vl)
                    obj[hdr] = vl
                yield obj

    def write_elements_index(self, rows: IterableType):
        # TODO: validate id column exists on csv for all rows
        with open(self.ELEMENT_MAP, "w") as f:
            writer = csv.writer(f, delimiter=",")
            for line in element_map:
                writer.writerow(line)

    def write_element(self, element: Dict, elcontents: Dict[str, bytes]):
        if not os.path.exists(element["base"]):
            os.makedirs(element["base"])

        for fname, data in elcontents.items():
            with f"{base}"



