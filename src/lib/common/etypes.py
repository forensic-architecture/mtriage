import os
from enum import Enum
from pathlib import Path
from lib.common.exceptions import EtypeCastError
from types import SimpleNamespace
from typing import List, Callable, Union


class Et:
    """ Defines the primary operations that make up a basic Etype. Array functionality is built in
        as a toggle on the simple type."""

    def __init__(self, _id, regex: Union[str, List[str]], is_array:bool=False):
        """
        
        """
        self.id = _id
        self.regex = regex
        self.is_array = is_array

    def __repr__(self) -> str:
        return f"EType({self.id.capitalize()}{'Array' if self.is_array else ''})"

    def __str__(self):
        return self.__repr__()

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

    def extract(self, path: str) -> dict:
        ext = "s" if self.is_array else ""
        return {f"{self.id}{ext}": self.globit(path)}

    def globit(self, path: str) -> list:
        glob: list = []
        pth = Path(path)
        if isinstance(self.regex, list):
            for ext in self.regex:
                glob.extend(pth.rglob(ext))
        else:
            glob = list(pth.rglob(self.regex))

        is_single = not self.is_array

        if len(glob) is 0:
            raise EtypeCastError(self)

        if is_single and len(glob) is not 1 and self.id != "any":
            raise EtypeCastError(self)

        elif is_single and self.id != "any":
            return glob[0] # TODO: setting return to list complains because it expects a Path

        return [str(x) for x in glob]


class UnionEt:
    """ A higher order Etype that allows the additive composition of Ets. """

    def __init__(self, *ets):
        self.ets = ets

    def __repr__(self) -> str:
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

    def extract(self, path: str) -> dict:
        out: dict = {}
        for x in self.ets:
            out = {**out, **x.extract(path)}
        return out


def create_etypes() -> SimpleNamespace:
    """ Etypes are basic and composite Ets wrapped into a nice namespace """
    etypes = SimpleNamespace(
        Any=Et("any", "*"),
        Image=Et("image", ["*.bmp", "*.jpg", "*.jpeg"]),
        Video=Et("video", "*.mp4"),
        Audio=Et("audio", ["*.mp3", "*.wav"]),
        Json=Et("json", "*.json"),
    )

    etypes.Union = lambda *args: UnionEt(*args)
    etypes.Array = lambda x: x.as_array()

    return etypes


Etype = create_etypes()


def cast_to_etype(el_path: str, etype: Et) -> dict:
    return {
        "base": el_path,
        "etype": etype,
        "media": etype.extract(el_path),
    }
