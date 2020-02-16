import ntpath
import json
import hashlib
import multiprocessing

MAX_CPUS = multiprocessing.cpu_count() - 1


def get_batch_size(ls_len: int):
    """ Determine the batch size for multiprocessing. """
    if ls_len >= MAX_CPUS:
        return ls_len // MAX_CPUS + 1
    # TODO: improve this heuristic for splitting up jobs
    return ls_len


def batch(iterable, n: int = 1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


def serialize_dict(_dict: dict) -> str:
    ret = ""
    for key in _dict:
        val = _dict[key]
        if isinstance(val, dict):
            ret += serialize_dict(val)
        else:
            ret += f"{key}{val}"
    return ret


def hashdict(_dict: dict):
    m = hashlib.md5()
    m.update(serialize_dict(_dict).encode("utf-8"))
    return m.hexdigest()


def save_logs(logs: list, filepath: str):
    if len(logs) <= 0:
        return
    with open(filepath, "a") as f:
        for l in logs:
            if l is not None:
                f.write(l)
                f.write("\n")


# NOTE: these vuevis functions should go to a viewer's util
def vuevis_prepare_el(element: dict) -> dict:
    el_meta = element["media"]["json"]
    out: dict = {}
    with open(el_meta, "r") as f:
        f = json.load(f)
        out["title"] = f["title"]
        out["description"] = f["description"]
        out["webpage_url"] = f["webpage_url"]
        out["duration"] = f["duration"]
        out["upload_date"] = f["upload_date"]
    return out


def vuevis_from_preds(
    element: dict, get_preds=lambda img_path: None, logger=lambda msg: None
):
    """ Where get_preds returns a list of tuples (label, loss) for each predicted label."""
    imgs = element["media"]["images"]
    labels: dict = {}

    logger(f"Running inference on frames in {element['id']}...")
    labels = {}
    for img_path in imgs:
        frame_no = deduce_frame_no(img_path)
        preds = get_preds(img_path)
        for pred_label, pred_conf in preds:
            if pred_label in labels.keys():
                labels[pred_label]["frames"].append(frame_no)
                labels[pred_label]["scores"].append(pred_conf)
            else:
                labels[pred_label] = {"frames": [frame_no], "scores": [pred_conf]}

    logger(f"Writing predictions for {element['id']}...")
    meta = vuevis_prepare_el(element)
    out = {**meta, "labels": labels}

    outpath = f"{element['dest']}/{element['id']}.json"
    with open(outpath, "w") as fp:
        json.dump(out, fp)
        logger(f"Wrote predictions JSON for {element['id']}.")


def deduce_frame_no(path: str) -> int:
    # TODO: error handling
    head, tail = ntpath.split(path)
    f = tail or nt.basename(head)
    num = f.split(".")[0]
    return int(num)
