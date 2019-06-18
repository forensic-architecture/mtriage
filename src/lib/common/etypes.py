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


def globit(path, regex, is_single=False):
    glob = list(Path(path).rglob(regex))

    if len(glob) is 0:
        raise EtypeCastError("Could not find appropriate media in element")

    if is_single and len(glob) is not 1:
        raise EtypeCastError("More than one image found in element")
    elif is_single:
        return glob[0]

    return glob


def get_any_media(el_path):
    """ Return all files in the element """
    return {"all": globit(el_path, "*.*")}


def get_image_media(el_path):
    return {"image": globit(el_path, "*.[bB][mM][pP]", is_single=True)}


def get_video_media(el_path):
    return {"video": globit(el_path, "*.[mM][pP][4]", is_single=True)}


def get_audio_media(el_path):
    return {"audio": globit(el_path, "*.([mM][pP][3])|([wW][aA][vV])", is_single=True)}

def get_json_media(el_path):
    return {"json": globit(el_path, "*.[jJ][sS][oO][nN]", is_single=True)}

def get_imagearray_media(el_path):
    return {"images": globit(el_path, "*.[bB][mM][pP]")}

def get_jsonarray_media(el_path):
    return {"jsons": globit(el_path, "*.[jJ][sS][oO][nN]")}

def get_annotatedvideo_media(el_path):
    return { **get_video_media(el_path), **get_json_media(el_path) }

def get_annotatedimagearray_media(el_path):
    return { **get_imagearray_media(el_path), **get_json_media(el_path) }


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
        Etype.Any: get_any_media,
        Etype.Image: get_image_media,
        Etype.Video: get_video_media,
        Etype.Audio: get_audio_media,
        Etype.Json: get_json_media,
        Etype.ImageArray: get_imagearray_media,
        Etype.JsonArray: get_jsonarray_media,
        Etype.AnnotatedVideo: get_annotatedvideo_media,
        Etype.AnnotatedImageArray: get_annotatedimagearray_media,
    }

    media = switcher.get(etype)(el_path)

    return {"base": el_path, "etype": etype, "media": media}
