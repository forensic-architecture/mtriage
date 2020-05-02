import os
from enum import Enum
from pathlib import Path
from copy import deepcopy
from functools import reduce
from types import SimpleNamespace as Ns
from typing import Union as _Union, List, TypeVar
from abc import abstractmethod
from lib.common.exceptions import EtypeCastError
from lib.common.get import get_custom_etypes


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
    def __init__(self, name, filter_func, is_array=False):
        self.id = name
        self.filter_func = filter_func
        self.is_array = is_array

    def __repr__(self):
        ia = self.is_array
        return (
            f"{'Array(' if ia else ''}EType.{self.id.capitalize()}{')' if ia else ''}"
        )

    def __str__(self):
        return self.__repr__()

    def __get_etype(self):
        for etype in Etype:
            if self.name == etype.name:
                return etype
        return None

    def __call__(
        self, el_id: str, paths: _Union[Pth, List[Pth]], is_array=False
    ) -> LocalElement:
        if isinstance(paths, (str, Path)):
            paths = [paths]
        else:
            paths = [Path(x) if isinstance(x, str) else x for x in paths]
        paths = self.filter(paths)

        # NOTE: a bit convoluted. Only do an array check if etype is not custom,
        # as custom etypes could have more sophisticated expressions than core
        # types. TODO: make more elegant.
        is_custom = self.id in [x.__name__ for x in get_custom_etypes()]
        if not is_custom:
            if len(paths) == 0 or (
                self.id != "Any"
                and not (is_array or self.is_array)
                and (len(paths) != 1 or not paths[0].is_file())
            ):
                raise EtypeCastError(self)

        # TODO: confirm all source files exist
        this_cls = deepcopy(self)
        if this_cls.is_array:
            this_cls.is_array = True
        return LocalElement(paths=paths, id=el_id, et=this_cls)

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

    def __lt__(self, other):
        return self.id < other.id

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
        return all([x == y for x, y in zip(sorted(self.ets), sorted(other.ets))])

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


def all_etypes():
    base = [x for x in dir(Etype) if not x.startswith("_") and x != "cast"]
    custom = get_custom_etypes()

    for t in base:
        yield getattr(Etype, t)
    for t in custom:
        yield t(t.__name__, t.filter)


def cast(el_id, paths: _Union[List[Pth], Pth], to: Et = None) -> LocalElement:
    if isinstance(paths, (Path, str)):
        paths = [paths]
    # NB: cast even at the expense of losing some paths if explicit ET is provided
    if to is not None:
        return to(el_id, paths=paths)
    # implicit cast to the most inclusive type
    valid = []
    if len(paths) == 0:
        raise EtypeCastError("Paths cannot be empty.")

    for et in all_etypes():
        if et.id == "Any":
            continue
        try:
            # if both array and singular casts are valid, precedence given to singular
            et(el_id, paths=paths, is_array=True)
            v = Array(et)
            try:
                et(el_id, paths=paths)
                v = et
            except:
                pass
            valid.append(v)
        except EtypeCastError:
            pass

    if len(valid) == 0:
        return Etype.Any(el_id, paths)
    elif len(valid) == 1:
        return valid[0](el_id, paths)
    else:
        # multiple valid types, return a union
        etyped_paths = reduce(lambda a, b: a + b(el_id, paths).paths, valid, [])
        if len(etyped_paths) != len(paths):
            return Etype.Any(el_id, paths)
        return Union(*valid)(el_id, paths)


class Etype:
    Any = Et("Any", lambda ps: ps)
    Image = Et("Image", lambda ps: fglob(ps, [".bmp", ".jpg", ".jpeg", ".png"]))
    Video = Et("Video", lambda ps: fglob(ps, [".mp4", ".mov"]))
    Audio = Et("Audio", lambda ps: fglob(ps, [".mp3", ".wav", ".m4a", ".aac"]))
    Json = Et("Json", lambda ps: fglob(ps, [".json"]))


Etype.cast = cast
# make custom etypes available on Etype
for t in get_custom_etypes():
    setattr(Etype, t.__name__, t(t.__name__, t.filter))
Union = UnionEt
Array = lambda x: x.as_array()
Index = LocalElementsIndex
