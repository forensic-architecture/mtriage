import os
import cv2
import numpy as np
from imutils.video import FileVideoStream
from subprocess import call, STDOUT
from lib.common.analyser import Analyser

def ffmpeg_frames(out_folder, fp, rate):
    # TODO: better logs for FFMPEG process
    FNULL = open(os.devnull, "w")
    out = call(
        ["ffmpeg", "-i", fp, "-r", str(rate), f"{out_folder}/%04d.bmp"],
        stdout=FNULL,
        stderr=STDOUT,
    )
    return str(out)

def frame_changed(frame_a, frame_b, threshold):
    """ Return True if frame_b is sufficiently different from frame_a.
    Currently, this uses a pretty naive subtract-and-L2-norm method.
    But! Could be pretty easily swapped out for something more advanced.
    Expects grayscale frames with float pixels (0.0 - 1.0 intensities)
    """
    assert frame_b.shape == frame_a.shape
    diff = np.linalg.norm(frame_b - frame_a)
    per_pixel_diff = diff / float(frame_a.size)
    return per_pixel_diff >= threshold


def opencv_frames(out_folder, fp, rate, threshold, sequential):
    fvs = FileVideoStream(str(fp)).start()
    file_fps = fvs.stream.get(cv2.CAP_PROP_FPS)
    
    # OpenCV doesn't have built-in framerate selection
    # so, we just skip frames to sample at the correct rate
    # i.e. if the file is 30fps and we want 2fps, we select every 15th frame
    # note: this won't work well with weird framerates (e.g. 7fps)
    read_every = int(file_fps / rate)
    frame_counter = 0
    last_frame = None
    num_output = 0
    num_considered = 0
    while fvs.more():
        frame = fvs.read()
        if frame is None:
            break

        use_frame = (frame_counter % read_every) == 0
        frame_counter += 1
        if not use_frame:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = gray.astype(np.float32) / 255.0
        if last_frame is None or frame_changed(last_frame, gray, threshold):
            last_frame = gray
            if sequential:
                num = num_output
            else:
                num = num_considered
            cv2.imwrite(f"{out_folder}/{num:04}.bmp", frame)
            num_output += 1
        num_considered += 1

    return num_output, num_considered


class FramesAnalyser(Analyser):
    def run(self, config):
        # TODO: frames for more than just YouTube.
        baseoutfolder = self.get_derived_folder("youtube")
        _media = self.media["youtube"]["data"]

        config = self._get_default_config(config)
        method = config["method"]
        fps = config["fps"]
        change_threshold = config["change_threshold"]
        sequential = config["sequential"]

        for element in _media.keys():
            outfolder = os.path.join(baseoutfolder, element)
            # create derived folder for element
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)

            if method == "ffmpeg":
                ffmpeg_frames(outfolder, _media[element], fps)
                self.logger(f"Frames successfully created for element {element}.")
            elif method == "opencv":
                num_output, num_considered = opencv_frames(
                    outfolder,
                    _media[element],
                    fps,
                    change_threshold,
                    sequential,
                )
                kept_ratio = float(num_output) / float(num_considered)
                percent = int(kept_ratio * 100)
                num = num_output
                self.logger(f"Output {num} frames for {element} ({percent}% kept)")
            else:
                raise ValueError(f"Unknown frame analysis method: {method}")


    def _get_default_config(self, config):
        defaults = {
            "change_threshold": 1e-5,
            "fps": 1,
            "method": "ffmpeg",
            "sequential": True
        }
        for k, v in config.items():
           defaults[k] = v
        return defaults


