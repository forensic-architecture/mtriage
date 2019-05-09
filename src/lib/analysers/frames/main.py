import os
from subprocess import call, STDOUT
from lib.common.analyser import Analyser

FPS_NUMBER = 1

def ffmpeg_frames(out_folder, fp, rate):
    # TODO: better logs for FFMPEG process
    FNULL = open(os.devnull, "w")
    out = call(
        ["ffmpeg", "-i", fp, "-r", str(rate), "{}/%04d.bmp".format(out_folder)],
        stdout=FNULL,
        stderr=STDOUT,
    )
    return str(out)


class FramesAnalyser(Analyser):
    def run(self, config):
        # TODO: frames for more than just YouTube.
        baseoutfolder = self.get_derived_folder("youtube")
        _media = self.media["youtube"]["data"]

        for element in _media.keys():
            outfolder = os.path.join(baseoutfolder, element)
            # create derived folder for element
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)

            ffmpeg_frames(outfolder, _media[element], FPS_NUMBER)

            self.logger(f"Frames successfully created for element {element}.")

