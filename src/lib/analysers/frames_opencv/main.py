import os
from shutil import copyfile
import cv2
import numpy as np
from imutils.video import FileVideoStream
from subprocess import call, STDOUT
from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype


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

    last_frame = None
    num_output = 0
    num_considered = 0
    time_elapsed = 0
    use_every = 1.0 / float(rate)
    frame_duration = 1.0 / file_fps
    while fvs.more():
        frame = fvs.read()
        if frame is None:
            break

        if num_considered == 0:
            use_frame = True
        elif (time_elapsed + frame_duration) >= use_every:
            use_frame = True
            time_elapsed -= use_every
        else:
            use_frame = False
        time_elapsed += frame_duration

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


class FramesOpencvAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.AnnotatedVideo

    def get_out_etype(self):
        return Etype.AnnotatedImageArray

    def analyse_element(self, element, config):
        FPS_NUMBER = config.get("fps")
        THRESHOLD = config.get("change_threshold")
        SEQUENTIAL = config.get("sequential")
        METHOD = config.get("method")

        # defaults
        if FPS_NUMBER is None: FPS_NUMBER = 1
        if THRESHOLD is None: THRESHOLD = "1e-5"
        THRESHOLD = np.fromstring(THRESHOLD, dtype=np.float64, sep=" ")
        if SEQUENTIAL is None: SEQUENTIAL = True

        dest = element["dest"]
        json = element["media"]["json"]
        video = element["media"]["video"]

        opencv_frames(dest, video, FPS_NUMBER, THRESHOLD, SEQUENTIAL)
        copyfile(json, f"{dest}/meta.json")

        self.logger(f"Frames successfully created for element {element['id']}.")
