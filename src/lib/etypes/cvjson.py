import json
import ntpath
from typing import List, Union
from pathlib import Path
from lib.common.etypes import Etype, Et, Pth
from lib.common.exceptions import EtypeCastError

TMP = Path("/tmp")
IMG_SFXS = [".bmp", ".jpg", ".png", ".jpeg"]


def deduce_frame_no(path):
    # TODO: error handling
    head, tail = ntpath.split(path)
    f = tail or ntpath.basename(head)
    num = f.split(".")[0]
    return int(num)


def prepare_json(path):
    out = {}
    if path is not None:
        with open(path, "r") as f:
            f = json.load(f)
            out["title"] = f["title"]
            out["description"] = f["description"]
            out["webpage_url"] = f["webpage_url"]
            out["duration"] = f["duration"]
            out["upload_date"] = f["upload_date"]
    return out


class CvJson(Et):
    """A custom Etype for computer vision (CV) json files, representing
    predictions on a set of frames."""

    def __repr__(self):
        return "CvJson"

    def filter(self, paths: Union[Pth, List[Pth]]) -> List[Pth]:
        if isinstance(paths, (str, Path)):
            paths = [paths]

        pths = []
        json_count = 0
        for p in paths:
            if p.suffix in ".json" and p.name == "scores.json":
                pths.append(p)
                json_count += 1
            pths.append(p) if p.suffix in IMG_SFXS else None
        if json_count != 1:
            raise EtypeCastError(self)
        return pths

    @staticmethod
    def from_preds(element, get_preds):
        """ Generate an element containing classifier predictions in a format
        appropriate for CvJson, i.e. a single JSON file 'preds.json' that
        contains an object representing which classes are predicted for each
        frame.

        This function assumes that `element.paths` represents an array of images
        to be interpreted. The `get_preds` function operates on a single image,
        accepting one argument that is a path to an image. It returns a list of
        tuples `('classname', 0.8)`, where `'classname'` is a string
        representing the class predicted, and `0.8` is the normalized prediction
        probability between 0 and 1. See KerasPretrained/core.py in analysers
        for an example. """
        imgs = [p for p in element.paths if p.suffix in IMG_SFXS]
        labels = {}
        for imp in imgs:
            frame_no, preds = deduce_frame_no(imp), get_preds(imp)
            for pred_label, pred_conf in preds:
                if pred_label in labels.keys():
                    labels[pred_label]["frames"].append(frame_no)
                    labels[pred_label]["scores"].append(pred_conf)
                else:
                    labels[pred_label] = {"frames": [frame_no], "scores": [pred_conf]}

        meta = [p for p in element.paths if p.suffix in ".json"]
        meta = meta[0] if len(meta) > 0 else None
        out = {**prepare_json(meta), "labels": labels}
        base = TMP / element.id
        base.mkdir(parents=True, exist_ok=True)
        outp = base / "preds.json"

        with open(outp, "w") as fp:
            json.dump(out, fp)

        return Etype.Json(element.id, outp)


etype = CvJson
