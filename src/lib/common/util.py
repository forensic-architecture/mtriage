import ntpath
import json


def save_logs(logs, filepath):
    if len(logs) <= 0:
        return
    with open(filepath, "a") as f:
        for l in logs:
            if l is not None:
                f.write(l)
                f.write("\n")


# NOTE: this should go to a viewer's util
def vuevis_prepare_el(element):
    el_meta = element["media"]["json"]
    out = {}
    with open(el_meta, "r") as f:
        f = json.load(f)
        out["title"] = f["title"]
        out["description"] = f["description"]
        out["webpage_url"] = f["webpage_url"]
        out["duration"] = f["duration"]
        out["upload_date"] = f["upload_date"]
    return out


def deduce_frame_no(path):
    # TODO: error handling
    head, tail = ntpath.split(path)
    f = tail or nt.basename(head)
    num = f.split(".")[0]
    return int(num)
