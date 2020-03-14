import os
import json
import operator
from shutil import copyfile, rmtree
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.common.exceptions import ElementShouldSkipError

WK_DIR = Path("/tmp/ranking")


class RankCvJson(Analyser):
    def pre_analyse(self, config):
        self.thresh = config["threshold"] if "threshold" in config else 0.5
        self.ranking_data = {}

        if WK_DIR.exists():
            rmtree(WK_DIR)
        WK_DIR.mkdir()

    def analyse_element(self, element: Etype.Any, config) -> Etype.Any:
        id = element.id

        jsons = [f for f in element.paths if f.suffix in ".json"]
        if len(jsons) != 1:
            raise ElementShouldSkipError(f"Not exactly one json in {element.id}")

        json = jsons[0]
        with open(json, "r") as f:
            data = json.load(f)

        try:
            # TODO: this logic should be a custom etype built from a core etype class...
            # the core class can then include associated methods.
            labels, frames, scores = data["labels"]
            for label, preds in labels.items():
                frames, scores = preds["frames"], preds["scores"]
                valid_frames = [
                    idx for idx, _ in enumerate(frames) if scores[idx] > self.thresh
                ]
                rank = len(valid_frames)
                if rank > 4:
                    self.logger(f"label '{label}': rank {count}")
                # gather all ranks in `ranking_data`
                if label not in self.ranking_data:
                    self.ranking_data[label] = {}
                self.ranking_data[label][id] = rank

            dpath = dest + "/" + element["id"] + ".json"
            copyfile(epath, dpath)
            self.logger(f"Rankings added for {element.id}.")
        except Exception as e:
            raise ElementShouldSkipError(str(e))

    def post_analyse(self, config, derived_dirs):
        ranking = self.data_to_ranking()
        path = WK_DIR / "all"
        if not os.path.exists(path):
            os.makedirs(path)
        file = path + "/rankings.json"
        self.logger("All rankings aggregated, printed to all/rankings.json")
        with open(file, "w") as f:
            json.dump(ranking, f)

    def data_to_ranking(self):
        sortedData = {}
        for label, values in self.ranking_data.items():
            s_vals = sorted(values.items(), key=operator.itemgetter(1))
            s_vals.reverse()
            s_els = [t[0] for t in s_vals]
            sortedData[label] = s_els
        return sortedData


module = RankCvJson
