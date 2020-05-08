import os
import json
import operator
from typing import List
from shutil import copyfile, rmtree
from pathlib import Path
from lib.common.etypes import Etype

WK_DIR = Path("/tmp/ranking")


def rank(elements: List, threshold=0.5, logger=print, element_id="__RANKING") -> Etype:
    ranking_data = {}

    for element in elements:
        jsons = [f for f in element.paths if f.suffix in ".json"]
        if len(jsons) != 1:
            continue

        jsonp = jsons[0]
        with open(jsonp, "r") as jsonf:
            data = json.load(jsonf)

        try:
            # TODO: this logic should be a custom etype built from a core etype class...
            # the core class can then include associated methods.
            labels = data["labels"]
            for label, preds in labels.items():
                frames, scores = preds["frames"], preds["scores"]
                valid_frames = [
                    idx for idx, _ in enumerate(frames) if scores[idx] > threshold
                ]
                rank = len(valid_frames)
                if rank > 4:
                    logger(f"label '{label}': rank {rank}")
                # gather all ranks in `ranking_data`
                if label not in ranking_data:
                    ranking_data[label] = {}
                ranking_data[label][element.id] = rank

            # dpath = WK_DIR / f"{element.id}.json"
            logger(f"Rankings indexed for {element.id}.")
            # return Etype.CvJson(element.id, dpath)
            return None

        except Exception as e:
            logger(f"Could not analyse {element.id}: {e}")

    ranking = {}
    for label, values in ranking_data.items():
        s_vals = sorted(values.items(), key=operator.itemgetter(1))
        s_vals.reverse()
        s_els = [t[0] for t in s_vals]
        ranking[label] = s_els

    path = WK_DIR / "all"
    if not os.path.exists(path):
        os.makedirs(path)
    file = path / "rankings.json"
    logger("All rankings aggregated, printed to all/rankings.json")

    with open(file, "w") as f:
        json.dump(ranking, f)

    return Etype.Json(element_id, file)
