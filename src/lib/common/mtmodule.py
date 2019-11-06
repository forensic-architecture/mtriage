from abc import ABC, abstractmethod
from lib.common.util import save_logs
from lib.common.exceptions import ImproperLoggedPhaseError, BatchedPhaseArgNotGenerator
from lib.common.etypes import Etype
from functools import partial, wraps
from types import GeneratorType
from itertools import islice, chain
import os
import multiprocessing

MAX_CPUS = multiprocessing.cpu_count() - 1
MIN_ELEMENTS_PER_CPU = 4


def get_batch_size(ls_len):
    """ Determine the batch size for multiprocessing. """
    if ls_len > MAX_CPUS * MIN_ELEMENTS_PER_CPU:
        return ls_len // MAX_CPUS + 1
    # TODO: improve this heuristic for splitting up jobs
    return ls_len


def chunks(iterable, size=1):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


class MTModule(ABC):
    def __init__(self, NAME, BASE_DIR):
        self.NAME = NAME
        self.BASE_DIR = BASE_DIR

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

    @staticmethod
    def batched_phase(phase_key):
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
                # cs = batch(all_elements, n=batch_size)
                #
                # for idx, c in enumerate(cs):
                #     p = multiprocessing.Process(target=innards, args=(self, c, *other_args))
                #     p.start()

                # TODO: work out how to consolidate logs
                ret_val = innards(self, all_elements, *other_args)

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
            el_id = element["id"]
            context = context + f"{el_id}: "
        return context
