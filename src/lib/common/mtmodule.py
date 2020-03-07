from abc import ABC, abstractmethod
import os
import struct
import multiprocessing
from functools import partial, wraps
from types import GeneratorType
from typing import Generator
from itertools import islice, chain

from lib.common.util import save_logs, hashdict, get_batch_size, batch
from lib.common.exceptions import ImproperLoggedPhaseError
from lib.common.etypes import Etype

TWO_INTS = "II"
RET_VAL_TESTS_ONLY = "no error"


def db_run(dbfile, q, batches_running):
    with open(dbfile, "ab") as f:
        while batches_running.value is not 0:
            try:
                done_info = q.get_nowait()
                f.write(struct.pack("II", *done_info))
                f.flush()
            except:
                pass
        while q.qsize() > 0:
            done_info = q.get()
            f.write(struct.pack("II", *done_info))
            f.flush()

        f.close()


class MTModule(ABC):
    def __init__(self, CONFIG, NAME, BASE_DIR):
        self.NAME = NAME
        self.BASE_DIR = BASE_DIR
        self.CONFIG = CONFIG

        self.UNIQUE_ID = hashdict(CONFIG)

        # logging setup
        self.PHASE_KEY = None
        self.__LOGS = []
        self.__LOGS_DIR = f"{self.BASE_DIR}/logs"
        self.__LOGS_FILE = f"{self.__LOGS_DIR}/{self.NAME}.txt"

        if not os.path.exists(self.__LOGS_DIR):
            os.makedirs(self.__LOGS_DIR)

    def get_in_etype(self):
        """ Note that only analysers implement this method, as selectors do not need to know their input type"""
        return Etype.Any

    def get_out_etype(self):
        return Etype.Any

    def process_batch(self, innards, done_dict, done_queue, batch_num, c, other_args):
        for idx, i in enumerate(c):
            if idx not in done_dict:
                innards(self, [i], *other_args)
                done_queue.put((batch_num, idx))
            else:
                print("Batch %d item %d already done, skipping job." % (batch_num, idx))

    def process_in_batches(self, args, process_element, remove_db=True):
        """
        Process elements in parallel using multiprocessing. Automatically applied to a phase that takes a single
        Generator argument, `all_elements`.

        `all_elements` is split into a number of batches, depending on the available CPU power of the machine on which
        mtriage is running. `process_element` is then run on each element in each batch, in parallel by number of
        batches. The results are collected together and return as a single list of results.
        """

        all_elements = list(args[0])
        batch_size = get_batch_size(len(all_elements))
        other_args = args[1:]
        # each chunk is a generator
        cs = batch(all_elements, n=batch_size)

        manager = multiprocessing.Manager()

        # switch logs to multiprocess access list
        self.__LOGS = manager.list()
        done_queue = manager.Queue()
        batches_running = manager.Value("i", 1)

        dbfile = f"{self.BASE_DIR}/{self.UNIQUE_ID}.db"

        done_dict = {}
        try:
            with open(dbfile, "rb") as f:
                _bytes = f.read(8)  # 8 bytes = two unsiged ints
                while _bytes:
                    fst, snd = struct.unpack(TWO_INTS, _bytes)
                    if fst not in done_dict:
                        done_dict[fst] = {}
                    done_dict[fst][snd] = 1
                    _bytes = f.read(8)
                f.close()
        except:
            pass

        db_process = multiprocessing.Process(
            target=db_run, args=(dbfile, done_queue, batches_running)
        )
        db_process.start()

        processes = []
        for idx, c in enumerate(cs):
            _done_dict = {}
            if idx in done_dict:
                _done_dict = done_dict[idx]
            p = multiprocessing.Process(
                target=self.process_batch,
                args=(process_element, _done_dict, done_queue, idx, c, other_args),
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        batches_running.value = 0
        db_process.join()

        if remove_db:
            os.remove(dbfile)

        self.save_and_clear_logs()
        return RET_VAL_TESTS_ONLY

    @staticmethod
    def phase(phase_key: str, **kwargs):
        """
        Provides phased logging for class methods on classes that inherit from MTModule.

        Before the function is called, the PHASE_KEY is set, and afterwards logs are saved to disk and the buffer
        cleared.

        If the first argument to the decorator function is a generator, then the application of the function is
        deferred to `process_in_batches`. This can be disabled by explicitly setting 'is_parallel' to False in the
        `options` argument.
        """

        def decorator(function):
            @wraps(function)
            def wrapper(self, *args):
                self.PHASE_KEY = phase_key
                ret_val = None

                if not isinstance(self, MTModule):
                    raise ImproperLoggedPhaseError(function.__name__)

                if (
                    kwargs.get("in_parallel", True)
                    and (len(args) >= 1)
                    and isinstance(args[0], GeneratorType)
                ):
                    _remove_db = kwargs.get("remove_db", True)
                    ret_val = self.process_in_batches(
                        args, function, remove_db=_remove_db
                    )

                else:
                    ret_val = function(self, *args)

                self.save_and_clear_logs()
                return ret_val

            return wrapper

        return decorator

    def save_and_clear_logs(self):
        save_logs(self.__LOGS, self.__LOGS_FILE)
        self.__LOGS = []

    def logger(self, msg, element=None):
        context = self.__get_context(element)
        msg = f"{context}{msg}"
        self.__LOGS.append(msg)
        print(msg)

    def error_logger(self, msg, element=None):
        context = self.__get_context(element)
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

    def __get_context(self, element):
        context = f"{self.NAME}: {self.PHASE_KEY}: "
        if element != None:
            context = context + f"{element.id}: "
        return context

    def is_dev(self):
        return "dev" in self.CONFIG and self.CONFIG["dev"]
