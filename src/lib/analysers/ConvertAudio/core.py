from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
from subprocess import call, STDOUT
from pathlib import Path
import os


class ConvertAudio(Analyser):
    in_etype = Etype.Audio
    out_etype = Etype.Audio
    def analyse_element(self, element, config):
        output_ext = config["output_ext"]

        FNULL = open(os.devnull, "w")
        output = f"/tmp/{element.id}.{output_ext}"
        # TODO: error handling
        out = call(
            ["ffmpeg", "-y", "-i", element.paths[0], output],
            stdout=FNULL,
            stderr=STDOUT,
        )
        self.logger(
            f"Converted '{element.id}' from {element.paths[0].suffix} to .{output_ext}"
        )
        return Etype.Audio(element.id, paths=[output])


module = ConvertAudio
