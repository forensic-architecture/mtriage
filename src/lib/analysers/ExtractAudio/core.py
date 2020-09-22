from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
from subprocess import call, STDOUT
import os


class ExtractAudio(Analyser):
    in_etype = Etype.Video
    out_etype = Etype.Audio

    def analyse_element(self, element, config):
        output_ext = config["output_ext"]
        output = f"/tmp/{element.id}.{output_ext}"
        FNULL = open(os.devnull, "w")
        # TODO: add error handling
        out = call(
            ["ffmpeg", "-y", "-i", element.paths[0], output],
            stdout=FNULL,
            stderr=STDOUT,
        )

        element.paths[0] = output

        return element


module = ExtractAudio
