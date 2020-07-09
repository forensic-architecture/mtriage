import hashlib
import multiprocessing
from pathlib import Path
from typing import List

MAX_CPUS = multiprocessing.cpu_count() - 1


def get_batch_size(ls_len):
    """ Determine the batch size for multiprocessing. """
    if ls_len >= MAX_CPUS:
        return ls_len // (MAX_CPUS + 1)
    # TODO: improve this heuristic for splitting up jobs
    return ls_len


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


def serialize_dict(_dict):
    ret = ""
    for key in _dict:
        val = _dict[key]
        if isinstance(val, dict):
            ret += serialize_dict(val)
        else:
            ret += f"{key}{val}"
    return ret


def hashdict(_dict):
    m = hashlib.md5()
    m.update(serialize_dict(_dict).encode("utf-8"))
    return m.hexdigest()


def subdirs(path: Path) -> List[Path]:
    """ Return a list of Paths for subdirectories in a directory """
    return [f for f in path.iterdir() if f.is_dir()]


def files(path: Path) -> List[Path]:
    """ Return a list of Paths for files in a directory """
    return [x for x in path.iterdir() if x.is_file()]
