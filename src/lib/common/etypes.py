from enum import Enum
from pathlib import Path
from lib.common.exceptions import EtypeCastError


class Etype(Enum):
    """ The 'Any' etype returns all paths to all media in an element
    { "media": { "paths": [ /* all paths as strings */ ] } }
    """

    Any = 0
    # a single image
    Image = 1
    # a single video
    Video = 2
    # a single audio
    Audio = 3
    # a single json
    Json = 4
    # a 1d array of Images
    ImageArray = 5
    # a 1d array of Jsons
    JsonArray = 6
    # a video + a json describing the video
    AnnotatedVideo = 7
    AnnotatedImageArray = 8


def globit(path, regex, is_single=False, etype=None):
    glob = list(Path(path).rglob(regex))

    if len(glob) is 0:
        raise EtypeCastError(
            "Could not cast to '{etype}' etype: no media found in directory"
        )

    if is_single and len(glob) is not 1:
        raise EtypeCastError(
            "Could not cast to '{etype}' etype: more than one media item found."
        )
    elif is_single:
        return glob[0]

    return glob


def get_any(el_path):
    """ Return all files in the element """
    return {"all": globit(el_path, "*.*", etype="Any")}


def get_image(el_path):
    return {"image": globit(el_path, "*.[bB][mM][pP]", is_single=True, etype="Image")}


def get_video(el_path):
    return {"video": globit(el_path, "*.[mM][pP][4]", is_single=True, etype="Video")}


def get_audio(el_path):
    return {
        "audio": globit(
            el_path, "*.([mM][pP][3])|([wW][aA][vV])", is_single=True, etype="Audio"
        )
    }


def get_json(el_path):
    return {"json": globit(el_path, "*.[jJ][sS][oO][nN]", is_single=True, etype="Json")}


def get_imagearray(el_path):
    return {"images": globit(el_path, "*.[bB][mM][pP]", etype="ImageArray")}


def get_jsonarray(el_path):
    return {"jsons": globit(el_path, "*.[jJ][sS][oO][nN]", etype="JsonArray")}


def get_annotatedvideo(el_path):
    return {
        "video": globit(
            el_path, "*.[mM][pP][4]", is_single=True, etype="AnnotatedVideo"
        ),
        "json": globit(
            el_path, "*.[jJ][sS][oO][nN]", is_single=True, etype="AnnotatedVideo"
        ),
    }


def get_annotatedimagearray(el_path):
    return {
        "images": globit(el_path, "*.[bB][mM][pP]", etype="AnnotatedImageArray"),
        "json": globit(
            el_path, "*.[jJ][sS][oO][nN]", is_single=True, etype="AnnotatedImageArray"
        ),
    }


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
    switcher = {
        Etype.Any: get_any,
        Etype.Image: get_image,
        Etype.Video: get_video,
        Etype.Audio: get_audio,
        Etype.Json: get_json,
        Etype.ImageArray: get_imagearray,
        Etype.JsonArray: get_jsonarray,
        Etype.AnnotatedVideo: get_annotatedvideo,
        Etype.AnnotatedImageArray: get_annotatedimagearray,
    }

    media = switcher.get(etype)(el_path)

    return {"base": el_path, "etype": etype, "media": media}
