import os
from enum import Enum
from pathlib import Path
from lib.common.exceptions import EtypeCastError
from types import SimpleNamespace as Ns
from typing import List, Union, TypeVar

def filter_files(folder, regex, allow_multiple=False):
    glob = []
    pth = Path(path)
    if isinstance(regex, list):
        for ext in regex:
            glob.extend(pth.rglob(ext))
    else:
        glob = list(pth.rglob(self.regex))

    is_single = not allow_multiple

    if len(glob) is 0:
        raise EtypeCastError(self)

    if is_single and len(glob) is not 1 and self.id != "any":
        raise EtypeCastError(self)

    elif is_single and self.id != "any":
        return glob[0]

    return [str(x) for x in glob]

class LocalElement:
    """ Local as in not from storage, but on the same comp where mtriage is running.
        Returned from Selector.retrieve_element, and also Analyser.analyse_element. """
    def __init__(self, id=None, query=None, paths=None, et=None):
        self.id = id #the element id
        self.query = query #the query string used to retrieve the element
        self.paths = paths #the path/s where the element's media are accessible locally
        self.et = et

class LocalElementsIndex:
    """ Similar to LocalElement, on the same comp as mtriage is running.
        Initialised with an array of arrays, where each inner array represents one element to be retrieved. """
    def __init__(self, rows=[]):
        self.rows = rows


Pth = TypeVar('Pth', str, Path)
class Et:
    """ Defines the primary operations that make up a basic Etype. Array functionality is built in
        as a toggle on the simple type.

        Returns a callable Etype, which is returned from user-defined functions such as `Analyser.analyse_element`.
        This Etype is then in turn used by subclasses of `Storage` to persist elements."""



    def __init__(self, name, regex, is_array=False):
        self.id = name
        self.regex = regex
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

    # def __call__(self, source: Union[List[Path], Path]):
    def __call__(self, paths: List[Pth], el_id: str) -> LocalElement:
        paths = [Path(x) if isinstance(x, str) else x for x in paths]
        # TODO: confirm all source files exist
        # TODO: filter only to the values the Et allows
        # available_files = filter_files(source.parent, self.regex, allow_multiple=self.is_array)
        return LocalElement(
            paths=paths,
            id=el_id,
            et=self,
        )


    def __eq__(self, other):
        return all(
            [
                isinstance(other, Et),
                self.id == other.id,
                self.regex == other.regex,
                self.is_array == other.is_array,
            ]
        )

    def as_array(self):
        return Et(self.id, self.regex, is_array=True)

    def array(self):
        return self.as_array()


class UnionEt:
    """ A higher order Etype that allows the additive composition of Ets. """

    def __init__(self, *ets):
        self.ets = ets

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


class Etype():
    Any = Et("Any", "*")
    Image = Et("Image", ["*.bmp", "*.jpg", "*.jpeg"])
    Video = Et("Video", "*.mp4")
    Audio = Et("Audio", ["*.mp3", "*.wav"])
    Json = Et("Json", "*.json")
    Union = UnionEt
    Array = lambda x: x.as_array()
    Index = LocalElementsIndex


def cast(paths, el_id, to:Et=None) -> LocalElement:
    # NB: cast even at the expense of losing some paths if explicit ET is provided
    if to is not None:
        return to(paths, el_id)
    # TODO: check extensions on all paths
    # fit it with the most restrictive etype possible
    # i.e. if all are .jpg, make it Et.Image rather than Et.Any
    # or Et.Union(Et.Image, Et.Json) rather than Et.Any
    # default to Et.Any
    raise NotImplementedError("TODO: cast etype implicitly based on the folder")


