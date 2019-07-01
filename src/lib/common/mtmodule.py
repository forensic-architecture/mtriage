from abc import ABC, abstractmethod
from lib.common.util import save_logs
from lib.common.exceptions import ImproperLoggedPhaseError
from lib.common.etypes import Etype
from functools import partial, wraps
import os


class MTModule(ABC):
    def __init__(self, NAME, BASE_DIR):
        self.NAME = NAME
        self.BASE_DIR = BASE_DIR
        self.__LOGS = []
        self.PHASE_KEY = None
        self.__LOGS_DIR = f"{self.BASE_DIR}/logs"
        self.__LOGS_FILE = f"{self.__LOGS_DIR}/{self.NAME}.txt"

        if not os.path.exists(self.__LOGS_DIR):
            os.makedirs(self.__LOGS_DIR)

    def get_in_etype(self):
        """ Note that only analysers implement this method, as selectors do not need to know their input type"""
        return Etype.Any

    def get_out_etype(self):
        return Etype.Any

    def get_arg_names(self):
        return []

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
