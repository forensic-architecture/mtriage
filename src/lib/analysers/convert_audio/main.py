from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
from subprocess import call, STDOUT
from pathlib import Path
import os


class ConvertAudioAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.Audio

    def get_out_etype(self):
        return Etype.Audio

    def analyse_element(self, element, config):
        dest = element["dest"]
        key = element["id"]
        input_ext = config["input_ext"]
        output_ext = config["output_ext"]
        audio = element["media"]["audio"]

        FNULL = open(os.devnull, "w")
        out = call(
            ["ffmpeg", "-y", "-i", audio, f"{dest}/{key}.{output_ext}"],
            stdout=FNULL,
            stderr=STDOUT,
        )
