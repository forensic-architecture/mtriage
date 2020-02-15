from abc import ABC, abstractmethod
import os
import struct
import multiprocessing
from functools import partial, wraps
from types import GeneratorType
from itertools import islice, chain

from lib.common.util import save_logs, hashdict, get_batch_size, batch
from lib.common.exceptions import ImproperLoggedPhaseError, BatchedPhaseArgNotGenerator
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

    @staticmethod
    def logged_phase(phase_key):
        def decorator(function):
            @wraps(function)
            def wrapper(self, *args):
                if not isinstance(self, MTModule):
                    raise ImproperLoggedPhaseError(function.__name__)
                self.PHASE_KEY = phase_key
                ret_val = function(self, *args)
                self.save_and_clear_logs()
                return ret_val

            return wrapper

        return decorator

    def process_batch(self, innards, done_dict, done_queue, batch_num, c, other_args):
        for idx, i in enumerate(c):
            if idx not in done_dict:
                innards(self, [i], *other_args)
                done_queue.put((batch_num, idx))
            else:
                print("Batch %d item %d already done, skipping job." % (batch_num, idx))

    @staticmethod
    def batched_phase(phase_key, remove_db=True):
        """
        Run a phase in parallel using multiprocessing. Can only be applied to a class function that takes a single argument that is of GeneratorType.
        """

        def decorator(innards):
            @wraps(innards)
            def wrapper(self, *args):
                if not isinstance(self, MTModule):
                    raise ImproperLoggedPhaseError(innards.__name__)
                if len(args) < 1 or not isinstance(args[0], GeneratorType):
                    raise BatchedPhaseArgNotGenerator(innards.__name__)

                self.PHASE_KEY = phase_key

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
                        args=(innards, _done_dict, done_queue, idx, c, other_args),
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

            return wrapper

        return decorator

    def save_and_clear_logs(self):
        print(self.__LOGS)
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
            el_id = element["id"]
            context = context + f"{el_id}: "
        return context

    def is_dev(self):
        return "dev" in self.CONFIG and self.CONFIG["dev"]
