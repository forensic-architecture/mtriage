import os
import json
import operator
import re
from typing import List
from shutil import copyfile, rmtree
from pathlib import Path
from lib.common.etypes import Etype
from functools import reduce

WK_DIR = Path("/tmp/ranking")


def open_json(fp):
    try:
        with open(fp, "r") as f:
            return json.load(f)
    except:
        return {}


def render_frame(element, label, frame, score):
    return {"element": element, "frame": frame, "score": score, "label": label}


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

        except Exception as e:
            logger(f"Could not analyse {element.id}: {e}")

    ranking = {}
    for label, values in ranking_data.items():
        s_vals = sorted(values.items(), key=operator.itemgetter(1))
        s_vals.reverse()
        s_els = [t[0] for t in s_vals]
        ranking[label] = s_els

    file = WK_DIR / "rankings.json"
    logger("All rankings aggregated, printed to rankings.json")

    if not os.path.exists(WK_DIR):
        os.makedirs(WK_DIR)

    with open(file, "w") as f:
        json.dump(ranking, f)

    return Etype.Json(element_id, file)


def flatten(elements: List, logger=print) -> Etype:
    """
    'Flatten' all predictions into a list, where each item is a positive frame:
    [
        { "element": "xxxx", "frame": 1, "score": 0.2, "label": "tank" },
    ]
    """
    is_json = re.compile(r".*\.json")
    # NOTE: assumes there is always one .json in each element's `paths`
    all_preds = [
        next(filter(is_json.match, [str(x) for x in x.paths])) for x in elements
    ]
    all_preds = [open_json(x) for x in all_preds]
    preds = [
        x.get("labels")
        for x in all_preds
        if isinstance(x, dict) and x.get("labels") is not None
    ]

    vls = [
        [(label, el_preds[label]) for label in el_preds.keys()] for el_preds in preds
    ]
    vls = [(x[0].id, x[1]) for x in zip(elements, vls)]
    label_in_els = [
        (x[0], y[0], y[1]["frames"], y[1]["scores"]) for x in vls for y in x[1]
    ]
    frames = [
        render_frame(x[0], x[1], y[0], y[1])
        for x in label_in_els
        for y in zip(x[2], x[3])
    ]

    output = WK_DIR / "flattened.json"

    if not os.path.exists(WK_DIR):
        os.makedirs(WK_DIR)

    with open(output, "w") as f:
        json.dump(frames, f)

    logger("All frames aggregated, printed to flattened.json")
    return Etype.Json("__FLATTENED", output)


def generate_meta(elements: List, logger=print) -> Etype:
    """ Combine various metrics inside a single element """
    a = flatten(elements, logger=logger)
    b = rank(elements, logger=logger)

    return Etype.Any("__META", a.paths + b.paths)
