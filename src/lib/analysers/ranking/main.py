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
        self.thresh = config["threshold"] if "threshold" in config else 0.5
        self.rankingData = {}
        self.wkDir = ""

    def analyse_element(self, element, config):
        id = element["id"]
        src = element["base"]
        dest = element["dest"]

        # run once
        if self.wkDir == "":
            self.wkDir = dest.replace(id, "")

        epath = src + "/" + element["id"] + ".json"
        with open(epath, "r") as f:
            edata = json.load(f)

        labels = edata["labels"]
        for label, preds in labels.items():
            count = len(
                [
                    idx
                    for idx, _ in enumerate(preds["frames"])
                    if preds["scores"][idx] > self.thresh
                ]
            )
            if count > 4:
                self.logger(f"{label}: {count}")
            if label not in self.rankingData:
                self.rankingData[label] = {}
            self.rankingData[label][id] = count

        dpath = dest + "/" + element["id"] + ".json"
        copyfile(epath, dpath)
        self.logger(f"Rankings added for {element['id']}.")

    def post_analyse(self, config, derived_dirs):
        ranking = self.dataToRanking()
        path = self.wkDir + "all"
        if not os.path.exists(path):
            os.makedirs(path)
        file = path + "/rankings.json"
        self.logger("All rankings aggregated, printed to all/rankings.json")
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
