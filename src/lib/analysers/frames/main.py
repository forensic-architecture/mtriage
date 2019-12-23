import os
from shutil import copyfile
from subprocess import call, STDOUT
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


def ffmpeg_frames(out_folder, fp, rate):
    # TODO: better logs for FFMPEG process
    FNULL = open(os.devnull, "w")
    out = call(
        ["ffmpeg", "-i", fp, "-r", str(rate), f"{out_folder}/%04d.bmp"],
        stdout=FNULL,
        stderr=STDOUT,
    )
    return str(out)


class FramesAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.Union(Etype.Json, Etype.Video)

    def get_out_etype(self):
        return Etype.Union(Etype.Image.array(), Etype.Json)

    def analyse_element(self, element, config):
        FPS_NUMBER = int(config["fps"])
        dest = element["dest"]
        json = element["media"]["json"]
        video = element["media"]["video"]

        ffmpeg_frames(dest, video, FPS_NUMBER)
        copyfile(json, f"{dest}/meta.json")

        self.logger(f"Frames successfully created for element {element['id']}.")
