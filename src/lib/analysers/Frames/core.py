import os
from shutil import copyfile, rmtree
from subprocess import call, STDOUT
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype, Union
from lib.common.util import files

VID_SUFFIXES = [".mp4", ".mov"]
GLOSSED_FRAMES = Union(Etype.Image.array(), Etype.Json)


def ffmpeg_frames(out_folder, fp, rate):
    # TODO: better logs for FFMPEG process
    FNULL = open(os.devnull, "w")
    out = call(
        ["ffmpeg", "-i", fp, "-r", str(rate), f"{out_folder}/%04d.bmp"],
        stdout=FNULL,
        stderr=STDOUT,
    )


class Frames(Analyser):
    def analyse_element(
        self, element: Union(Etype.Json, Etype.Video), config
    ) -> GLOSSED_FRAMES:
        fps = int(config["fps"]) if "fps" in config else 1
        json = [x for x in element.paths if x.suffix in ".json"][0]
        video = [x for x in element.paths if x.suffix in VID_SUFFIXES][0]

        dest = Path("/tmp") / element.id
        if dest.exists():
            rmtree(dest)
        dest.mkdir()

        ffmpeg_frames(dest, video, fps)
        copyfile(json, dest / "meta.json")

        self.logger(f"Frames successfully created for element {element.id}.")
        self.disk.delete_local_on_write = True
        return GLOSSED_FRAMES(element.id, paths=files(dest))


module = Frames
