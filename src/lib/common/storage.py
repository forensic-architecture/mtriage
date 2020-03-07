import os
import csv
import shutil
from pathlib import Path
from types import GeneratorType, SimpleNamespace as Ns
from typing import Union, List, Iterable, Dict
from lib.common.etypes import Etype, LocalElement, LocalElementsIndex
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

    # @abstractmethod
    # def store(self, el, path):
    #     pass
    #
    # @abstractmethod
    # def get_element(self, element):
    #     pass


class LocalStorage(Storage):
    """
    Stores elements in an element_map.csv.
    """

    def __init__(self, folder=None):
        self.base_dir = folder

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







