from lib.common.analyser import Analyser
from subprocess import call, STDOUT
from pathlib import Path
import os


class ConvertAudioAnalyser(Analyser):
    def analyse_element(self, element, config):

        src = element["src"]
        dest = element["dest"]
        key = element["id"]
        input_ext = config["input_ext"]
        output_ext = config["output_ext"]
        media = list(Path(src).rglob(f"*.{input_ext}"))

        if len(media) is not 1:
            raise Error(
                "The convert_audio analyser can only operate on elements that contain one and only one audio file."
            )

        audio = media[0]

        FNULL = open(os.devnull, "w")
        out = call(
            ["ffmpeg", "-i", audio, f"{dest}/{key}.{output_ext}"],
            stdout=FNULL,
            stderr=STDOUT,
        )
