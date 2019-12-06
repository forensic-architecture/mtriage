import os
from enum import Enum
from pathlib import Path
from lib.common.exceptions import EtypeCastError
from types import SimpleNamespace
from typing import List


class Et:
    def __init__(self, _id, regex, is_array=False):
        self.id = _id
        self.regex = regex
        self.is_array = is_array

    def __repr__(self):
        return f"EType({self.id.capitalize()})"

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

    def extract(self, path):
        ext = "s" if self.is_array else ""
        return {f"{self.id}{ext}": self.globit(path)}

    def globit(self, path):
        glob = list(Path(path).rglob(self.regex))
        is_single = not self.is_array

        if len(glob) is 0:
            raise EtypeCastError(
                "Could not cast to '{etype}' etype: no media found in directory"
            )

        if is_single and len(glob) is not 1:
            raise EtypeCastError(
                "Could not cast to '{etype}' etype: more than one media item found."
            )

        elif is_single and self.id != "any":
            return glob[0]

        return [str(x) for x in glob]


class UnionEt:
    def __init__(self, *ets):
        self.ets = ets

    def __repr__(self):
        inner = ""
        for et in self.ets:
            inner += f"{et}, "
        inner = inner[:-2]

        return f"EType(Union({inner}))"

    def __eq__(self, other):
        return all(
            isinstance(other, UnionEt),
            all([x == y for x, y in zip(self.ets, other.ets)]),
        )

    def extract(self, path):
        out = {}
        for x in self.ets:
            out = {**out, **x.extract(path)}
        return out


def create_etypes():
    """ Etypes are basic and composite Ets wrapped into a nice namespace """
    etypes = SimpleNamespace(
        Any=Et("any", "*"),
        Image=Et("image", "*.[bB][mM][pP]$"),
        Video=Et("video", "*.[mM][pP][4]$"),
        Audio=Et("audio", "*.([mM][pP][3])|([wW][aA][vV])$"),
        Json=Et("json", "*.[jJ][sS][oO][nN]$"),
    )
    etypes.ImageArray = etypes.Image.as_array()
    etypes.JsonArray = etypes.Json.as_array()

    etypes.AnnotatedVideo = UnionEt(etypes.Video, etypes.Json)
    etypes.AnnotatedImageArray = UnionEt(etypes.ImageArray, etypes.Json)

    etypes.Union = lambda *args: UnionEt(*args)
    etypes.Array = lambda x: x.as_array()

    return etypes


Etype = create_etypes()


# NOTE: the 'get_any' expected an all in the ID


def cast_to_etype(el_path, etype):
    """ An etype return object consists of all the paths to media in that element.
    For example:
        {
            "base": "path/to/element/dir",
            "etype": Etype.Image,
            "media": {
                /* values in 'media' depend on the etype */
            }
        }
    """
    return {
        "base": el_path,
        "etype": etype,
        "media": etype.extract(el_path),
    }
