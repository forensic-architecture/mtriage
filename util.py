import os
import json
import shutil
from argparse import ArgumentTypeError

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class InvalidPipDep(Exception):
    pass


class InvalidArgumentsError(Exception):
    pass


# parseargs type functions
def str2yamlfile(fname):
    ext = os.path.splitext(fname)[1][1:]
    if ext not in "yaml":
        ArgumentTypeError("The file you specify to run mtriage must be a YAML file")
    if not os.path.exists(fname):
        ArgumentTypeError("Cannot find a file at {}.".format(fname))
    return fname


def get_subdirs(d):
    whitelist = ["__pycache__"]
    return [
        o
        for o in os.listdir(d)
        if os.path.isdir(os.path.join(d, o))
        and o not in whitelist
        and o != "__deprecated"
    ]


def name_and_ver(pipdep):
    """Return the name and version from a string that expresses a pip dependency.
    Raises an InvalidPipDep exception if the string is an invalid dependency.
    """
    pipdep = pipdep.split("==")
    dep_name = pipdep[0]
    try:
        if len(pipdep) == 1:
            dep_version = None
        elif len(pipdep) > 2:
            raise InvalidPipDep
        else:
            dep_version = pipdep[1]
            # if re.search(r"\d+(\.\d+)*", dep_version) is None:
            #     raise InvalidPipDep
        return dep_name, dep_version
    except:
        raise InvalidPipDep


def should_add_pipdep(dep, pipdeps):
    """Check whether pipdep should be added."""
    dep_name, dep_ver = name_and_ver(dep)
    for _dep in pipdeps:
        _dep_name, _dep_ver = name_and_ver(_dep)
        if _dep_name == dep_name:
            # new version unspecified, cannot be more specific
            if dep_ver is None:
                return False
            # new version more specific
            elif _dep_ver is None and dep_ver is not None:
                return True
            elif str(dep_ver) < str(_dep_ver):
                return False
    return True


def should_add_dockerline(line, dockerfile):
    """Check whether line should be added to array representing Dockerfile."""
    return line not in dockerfile


def add_deps(dep_path, deps, should_add):
    """Add dependences at {folder_path} to {deps}, excluding if {should_add} is True for any given dependency."""
    if not os.path.isfile(dep_path):
        return

    with open(dep_path) as f:
        for line in f.readlines():
            if should_add(line, deps):
                deps.append(line)
        deps.append('\n') # for good measure


def extract_dep(csv_row):
    if len(csv_row) is 1:
        return csv_row[0]
    return ""


def get_env_config():
    ENV_FILE = "{}/.env".format(DIR_PATH)
    if os.path.exists(ENV_FILE):
        return "--env-file={}".format(ENV_FILE)
    else:
        return "--env-file={}".format("{}/.env.example".format(DIR_PATH))
