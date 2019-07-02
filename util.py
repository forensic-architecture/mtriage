import os
import json
import shutil


class InvalidPipDep(Exception):
    pass


class InvalidArgumentsError(Exception):
    pass


class InvalidViewerConfigError(Exception):
    pass


class WorkingDirectorNotFoundError(Exception):
    pass


def get_subdirs(d):
    whitelist = ["__pycache__"]
    return [
        o
        for o in os.listdir(d)
        if os.path.isdir(os.path.join(d, o)) and o not in whitelist
    ]


def name_and_ver(pipdep):
    """ Return the name and version from a string that expresses a pip dependency.
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
    """Check whether pipdep should be added.
    """
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
    """Check whether line should be added to array representing Dockerfile.
    """
    return line not in dockerfile


def add_deps(dep_path, deps, should_add):
    """ Add dependences at {folder_path} to {deps}, excluding if {should_add} is True for any given dependency.
    """
    if not os.path.isfile(dep_path):
        return

    with open(dep_path) as f:
        for line in f.readlines():
            if should_add(line, deps):
                deps.append(line)


def verify_viewer_args(inputDir, viewersDir, viewerName):
    if inputDir == None:
        raise InvalidArgumentsError("No input directory supplied for viewer plugin.")

    if viewerName == None:
        raise InvalidArgumentsError("No viewer plugin name supplied.")

    if not os.path.exists(inputDir):
        raise WorkingDirectorNotFoundError(
            "The input directory {} does not exist. ".format(inputDir)
        )

    viewerDir = "{}/{}".format(viewersDir, viewerName)
    viewerConfigPath = "{}/config.json".format(viewerDir)

    if not os.path.exists(viewerDir):
        raise InvalidArgumentsError(
            "The viewer plugin '{}' does not exist.".format(viewerName)
        )

    if not os.path.isfile(viewerConfigPath):
        raise InvalidArgumentsError(
            "Viewer config does not exist in the folder {}".format(viewerConfigPath)
        )

    return viewerDir, viewerConfigPath


def create_symlinks(inputElementsDir, serverElementsDir):
    # clean if exists
    if not os.path.exists(inputElementsDir):
        raise OSError("Server elements dir does not exist")

    # make it empty
    shutil.rmtree(serverElementsDir)
    os.makedirs(serverElementsDir)

    el_ids = [
        f
        for f in os.listdir(inputElementsDir)
        if os.path.isdir("{}/{}".format(inputElementsDir, f))
    ]

    # create symlinks for input elements
    for el_id in el_ids:
        folder_in = "{}/{}".format(inputElementsDir, el_id)
        for element_path in os.listdir(folder_in):
            folder_out = "{}/{}".format(serverElementsDir, el_id)
            folder_out_media = "{}/media".format(folder_out)
            if not os.path.exists(folder_out):
                os.makedirs(folder_out_media)
            os.symlink(
                "{}/{}".format(folder_in, element_path),
                "{}/{}".format(folder_out_media, element_path),
            )


def get_viewer_etype(viewerConfigPath):
    with open(viewerConfigPath, "r") as f:
        viewerConfig = json.load(f)
        viewerEType = viewerConfig["etype"]
        return viewerEType


def create_server_config(configPath, configDict):
    with open(configPath, "w") as config:
        json.dump(configDict, config)
