from abc import ABC, abstractmethod
import os
import re

EXT_TO_MTYPE = {
    ".mp4": MTVideo,
    ".jpg": MTImage,
    ".mp3": MTAudio,
}

class MType(ABC):
    """ MTypes are interchangeable with file extensions.
    """
    def __init__(self, filepath):
        filename, ext = os.path.splittext(filepath)
        self.EXT = ext
        self.FILENAME = filename
        self.FILEPATH = filepath

class MTVideo(MType):
    pass

class MTImage(MType):
    pass

class MTAudio(MType):
    pass

def get_mtype(fp):
    ref = MType(fp)
    return EXT_TO_MTYPE[ref.EXT](fp)