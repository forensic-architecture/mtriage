from lib.common.analyser import Analyser
# from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
import os
import json
import operator
import collections
from shutil import copyfile


class RankingAnalyser(Analyser):

    def get_in_etype(self):
        return Etype.Any

    def get_out_etype(self):
        return Etype.Any

    def pre_analyse(self, config):
        self.rankingData = {}
        self.wkDir = ""

    def analyse_element(self, element, config):

        id = element["id"]
        src = element["base"]
        dest = element["dest"]
        self.logger(dest)

        if self.wkDir == "":
            self.wkDir = dest.replace(id, '')

        mpath = src + "/" + element["id"] + ".json"
        with open(mpath, 'r') as f:
            eData = json.load(f)

        labels = eData["labels"]
        for label, frames in labels.items():
            count = len(frames["frames"])
            if label not in self.rankingData:
                self.rankingData[label] = {}
            self.rankingData[label][id] = count

        dpath = dest + "/" + element["id"] + ".json"
        copyfile(mpath, dpath)


    def post_analyse(self, config, derived_dirs):
        ranking = self.dataToRanking()
        path = self.wkDir + "all"
        if not os.path.exists(path):
            os.makedirs(path)
        file = path + "/rankings.json"
        with open(file, "w") as f:
            json.dump(ranking, f)

    def dataToRanking(self):
        sortedData = {}
        for label, values in self.rankingData.items():
            s_vals = sorted(values.items(), key=operator.itemgetter(1))
            s_vals.reverse()
            s_els = [t[0] for t in s_vals]
            sortedData[label] = s_els
        return sortedData
