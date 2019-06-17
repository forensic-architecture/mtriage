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


def vuevis_prepare_el(element):
    # NOTE: this logic hardcodes to videos produced from the youtube selector, which produces an accompanying
    # meta.json with these fields (and many more)
    out = {"id": element["id"]}
    hacked_el_src = element["src"].replace("derived/frames", "data")

    with open(f"{hacked_el_src}/meta.json", "r") as f:
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
