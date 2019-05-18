import youtube_dl
import re
import os
import math
import json
from subprocess import call, STDOUT

# TODO: refactor into a class so that the folder path can be an instance variable

def make_dir(fp):
    if not os.path.exists(fp):
        os.makedirs(fp)

def get_folder_path(vid_id, folder):
    return f"{folder}/{vid_id}"

def get_meta_path(vid_id, folder):
    return f"{folder}/{vid_id}/meta.json"

def id_from_url(url):
    id_search = re.search(
        "https:\/\/www\.youtube\.com\/watch\?v\=(.*)", url, re.IGNORECASE
    )
    if id:
        return id_search.group(1)
    return None

def vid_exists(vid_id, folder):
    fp = get_folder_path(vid_id, folder)
    try:
        m_vid_file = list(
            filter(lambda x: re.match("(.*\.mp4)|(.*\.mkv)", x), os.listdir(fp))
        )
        # video has already been downloaded.
        if len(m_vid_file) != 1:
            return False
        return True
    except FileNotFoundError:
        return False
