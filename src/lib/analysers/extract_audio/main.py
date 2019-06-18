from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
from subprocess import call, STDOUT
import os


class ExtractAudioAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.Video

    def get_out_etype(self):
        return Etype.Audio

    def analyse_element(self, element, config):

        dest = element["dest"]
        key = element["id"]
        media = Analyser.find_video_paths(element["src"])

        if len(media) is not 1:
            raise ElementShuoldSkipError(
                "The strip_audio analyser can only operate on elements that contain one and only one video."
            )

        video = media[0]

        output_ext = config["output_ext"]

        FNULL = open(os.devnull, "w")
        out = call(
            ["ffmpeg", "-y", "-i", video, f"{dest}/{key}.{output_ext}"],
            stdout=FNULL,
            stderr=STDOUT,
        )
