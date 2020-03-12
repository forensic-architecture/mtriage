import os
from enum import Enum
from pathlib import Path
from types import SimpleNamespace as Ns
from typing import Union as _Union, List, TypeVar
from abc import abstractmethod
from lib.common.exceptions import EtypeCastError


class LocalElement:
    """ Local as in not from storage, but on the same comp where mtriage is running.
        Returned from Selector.retrieve_element, and also Analyser.analyse_element. """

    def __init__(self, id=None, query=None, paths=None, et=None):
        self.id = id  # the element id
        self.query = query  # the query string used to retrieve the element
        self.paths = (
            paths  # the path/s where the element's media are accessible locally
        )
        self.et = et


class LocalElementsIndex:
    """ Similar to LocalElement, on the same comp as mtriage is running.
        Initialised with an array of arrays, where each inner array represents one element to be retrieved. """

    def __init__(self, rows=[]):
        self.rows = rows


Pth = TypeVar("Pth", str, Path)
Function = type(lambda _: None)


class Et:
    """ TODO: ... """

    def __init__(self, name, filter_func, is_array=False):
        self.id = name
        self.filter_func = filter_func
        self.is_array = is_array

    def __repr__(self):
        return f"EType({self.id.capitalize()}{'Array' if self.is_array else ''})"

    def __str__(self):
        return self.__repr__()

    def __get_etype(self):
        for etype in Etype:
            if self.name == etype.name:
                return etype
        return None

    def __call__(self, el_id: str, paths: _Union[Pth, List[Pth]]) -> LocalElement:
        if isinstance(paths, (str, Path)):
            paths = [paths]
        else:
            paths = [Path(x) if isinstance(x, str) else x for x in paths]
        paths = self.filter(paths)
        if (
            len(paths) == 0
            or (self.id != "Any" and not self.is_array and (len(paths) != 1 or not paths[0].is_file()))
        ):
            raise EtypeCastError(self.__class__.__name__)

        # TODO: confirm all source files exist
        return LocalElement(paths=paths, id=el_id, et=self,)

    def filter(self, ls):
        """ Exists to be overwritten, `filter_func` is just the fallback. """
        return self.filter_func(ls)

    def __eq__(self, other):
        return all(
            [
                isinstance(other, Et),
                self.id == other.id,
                self.is_array == other.is_array,
            ]
        )

    def as_array(self):
        return Et(self.id, self.filter, is_array=True)

    def array(self):
        return self.as_array()

    @property
    def is_union(self):
        return False



class UnionEt(Et):
    """ A higher order Etype that allows the additive composition of Ets. """

    def __init__(self, *ets):
        self.ets = ets
        super().__init__(self, str(self), is_array=False)

    def __repr__(self):
        inner = ""
        for et in self.ets:
            inner += f"{et}, "
        inner = inner[:-2]

        return f"Union({inner})"

    def __eq__(self, other):
        return all(
            isinstance(other, UnionEt),
            all([x == y for x, y in zip(self.ets, other.ets)]),
        )

    def __call__(self, el_id: str, paths: _Union[Pth, List[Pth]]) -> LocalElement:

        self.ets[1](el_id, paths)
        ets = [T(el_id, paths) for T in self.ets]

        all_paths = []

        for et in ets:
            all_paths += et.paths
        return LocalElement(paths=all_paths, id=el_id, et=self)

    @property
    def is_union(self):
        return True




def class_as_et(class_obj):
    return class_obj(class_obj.__name__, class_obj.filter)
    # TODO: get across all custom methods somehow...


def fglob(ps, exts):
    return [p for p in ps if p.suffix.lower() in exts]


class Etype:
    Any = Et("Any", lambda ps: ps)
    Image = Et("Image", lambda ps: fglob(ps, [".bmp", ".jpg", ".jpeg", ".png"]))
    Video = Et("Video", lambda ps: fglob(ps, [".mp4", ".mov"]))
    Audio = Et("Audio", lambda ps: fglob(ps, [".mp3", ".wav"]))
    Json = Et("Json", lambda ps: fglob(ps, [".json"]))


Union = UnionEt
Array = lambda x: x.as_array()
Index = LocalElementsIndex

# TODO: import all custom etypes and add to EType via `class_as_et`


def all_etypes():
    all_etypes = [x for x in dir(Etype) if not x.startswith("_")]
    for t in all_etypes:
        yield getattr(Etype, t)


def cast(paths, el_id, to: Et = None) -> LocalElement:
    # NB: cast even at the expense of losing some paths if explicit ET is provided
    if to is not None:
        return to(el_id, paths=paths)
    # TODO: check extensions on all paths
    # fit it with the most restrictive etype possible
    # i.e. if all are .jpg, make it Et.Image rather than Et.Any
    # or Et.Union(Et.Image, Et.Json) rather than Et.Any
    # default to Et.Any
    raise NotImplementedError("TODO: cast etype implicitly based on the folder")
