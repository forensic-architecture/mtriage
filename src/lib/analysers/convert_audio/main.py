from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
from subprocess import call, STDOUT
from pathlib import Path
import os


class ConvertAudioAnalyser(Analyser):
    def analyse_element(self, element: Etype.Audio, config) -> Etype.Audio:
        input_ext = config["input_ext"]
        output_ext = config["output_ext"]

        FNULL = open(os.devnull, "w")
        output = f"/tmp/{element.id}.{output_ext}"
        # TODO: error handling
        out = call(
            ["ffmpeg", "-y", "-i", element.paths[0], output],
            stdout=FNULL,
            stderr=STDOUT,
        )
        return Etype.Audio(output, element.id)

