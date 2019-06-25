from lib.common.analyser import Analyser
import librosa as lb
import os
from shutil import copyfile
from lib.common.etypes import Etype
import json


class AudioOnsetAnalyser(Analyser):

    def get_in_etype(self):
        return Etype.Audio

    def get_out_etype(self):
        return Etype.AnnotatedAudio

    def analyse_element(self, element, config):

        src = element["base"]
        dest = element["dest"]
        key = element["id"]
        audiofile = element["media"]["audio"]

        duration, onset_times = self.extract(audiofile)

        json_dest = os.path.join(dest, "onsets.json")
        data = {
            "duration": duration,
            "onsets": onset_times
        }

        with open(json_dest, "w") as fp:
            json.dump(data, fp)

        f_dest = os.path.join(dest, f"{key}.wav")

        copyfile(audiofile, f_dest)

    def extract(self, audiofile):
        x, sr = lb.load(audiofile)
        duration = lb.get_duration(x, sr)
        for index, s in enumerate(x):
            t = 0 if abs(s) < 0.02 else s
            x[index] = t
        onset_frames = lb.onset.onset_detect(
            x, sr=sr, wait=1, pre_avg=1, pre_max=1, post_max=1
        )
        return duration, lb.frames_to_time(onset_frames).tolist()
