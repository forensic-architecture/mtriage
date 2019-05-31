# -*- coding: utf-8 -*-
import docker
import inspect
import pytest
import os
import re
import argparse
import subprocess as sp


NAME = "forensicarchitecture/mtriage"
CONT_NAME = NAME.replace("/", "_")  # docker doesn't allow slashes in cont names
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ENV_FILE = "{}/.env".format(DIR_PATH)
HOME_PATH = os.path.expanduser("~")
DOCKER = docker.from_env()


def get_subdirs(d):
    return [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]


class InvalidPipDep(Exception):
    pass


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
            if re.search(r"^([0-9]{1,2}\.){0,2}([0-9]{1,2})$", dep_version) is None:
                raise InvalidPipDep
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
            if _dep_ver is None and dep_ver is None:
                return False
            elif _dep_ver is None:
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


def build():
    """ Collect all partial Pip and Docker files from selectors and analysers, and combine them with the core mtriage
        dependencies in src/build in order to create an appropriate Dockerfile and requirements.txt.
        NOTE: There is currently no way to include/exclude certain selector dependencies, but this build process is
              the setup for that optionality.
    """
    # setup
    DOCKERFILE_PARTIAL = "partial.Dockerfile"
    PIP_PARTIAL = "requirements.txt"
    BUILD_DOCKERFILE = "{}/build.Dockerfile".format(DIR_PATH)
    BUILD_PIPFILE = "{}/build.requirements.txt".format(DIR_PATH)
    CORE_PIPDEPS = "{}/src/build/core.requirements.txt".format(DIR_PATH)
    CORE_START_DOCKER = "{}/src/build/core.start.Dockerfile".format(DIR_PATH)
    CORE_END_DOCKER = "{}/src/build/core.end.Dockerfile".format(DIR_PATH)
    ANALYSERS_PATH = "{}/src/lib/analysers".format(DIR_PATH)
    SELECTORS_PATH = "{}/src/lib/selectors".format(DIR_PATH)

    print("Collecting partial dependencies from selector and analyser folders...")

    with open(CORE_PIPDEPS) as cdeps:
        pipdeps = cdeps.readlines()

    with open(CORE_START_DOCKER) as dfile:
        dockerlines = dfile.readlines()

    # search all selectors/analysers for partials
    selectors = get_subdirs(SELECTORS_PATH)
    analysers = get_subdirs(ANALYSERS_PATH)

    for selector in selectors:
        docker_dep = "{}/{}/{}".format(SELECTORS_PATH, selector, DOCKERFILE_PARTIAL)
        pip_dep = "{}/{}/{}".format(SELECTORS_PATH, selector, PIP_PARTIAL)

        add_deps(docker_dep, dockerlines, should_add_dockerline)
        add_deps(pip_dep, pipdeps, should_add_pipdep)

    for analyser in analysers:
        docker_dep = "{}/{}/{}".format(ANALYSERS_PATH, analyser, DOCKERFILE_PARTIAL)
        pip_dep = "{}/{}/{}".format(ANALYSERS_PATH, analyser, PIP_PARTIAL)

        add_deps(docker_dep, dockerlines, should_add_dockerline)
        add_deps(pip_dep, pipdeps, should_add_pipdep)

    with open(CORE_END_DOCKER) as f:
        for line in f.readlines():
            dockerlines.append(line)

    # create Dockerfile and requirements.txt for build
    if os.path.exists(BUILD_PIPFILE):
        os.remove(BUILD_PIPFILE)

    with open(BUILD_PIPFILE, "w") as f:
        for dep in pipdeps:
            f.write(dep)

    if os.path.exists(BUILD_DOCKERFILE):
        os.remove(BUILD_DOCKERFILE)

    with open(BUILD_DOCKERFILE, "w") as f:
        for line in dockerlines:
            f.write(line)

    print("All Docker dependencies collected in build.Dockerfile.")
    print("All Pip dependencies collected in build.requirements.txt.")
    print("--------------------------------------------------------")
    print("\n")
    print("Starting build in Docker...")

    try:
        sp.call(
            [
                "docker",
                "build",
                "-t",
                "{}:dev".format(NAME),
                "-f",
                BUILD_DOCKERFILE,
                ".",
            ]
        )
        print("Build successful, run with: \n\tpython run.py develop")
    except:
        print("Something went wrong! EEK.")

    # cleanup
    os.remove(BUILD_DOCKERFILE)
    os.remove(BUILD_PIPFILE)


def develop():
    try:
        DOCKER.containers.get(CONT_NAME)
        print("Develop container already running. Stop it and try again.")
    except docker.errors.NotFound:
        sp.call(
            [
                "docker",
                "run",
                "-it",
                "--name",
                CONT_NAME,
                "--env",
                "BASE_DIR=/mtriage",
                "--env-file={}".format(ENV_FILE),
                "--rm",
                "--privileged",
                "-v",
                "{}:/mtriage".format(DIR_PATH),
                "-v",
                "{}/.config/gcloud:/root/.config/gcloud".format(HOME_PATH),
                "{}:dev".format(NAME),
            ]
        )


def clean():
    sp.call(["docker", "rmi", NAME])


def __run_lib_tests():
    returncode = sp.call(
        [
            "docker",
            "run",
            "--env",
            "BASE_DIR=/mtriage",
            "--env-file={}".format(ENV_FILE),
            "--rm",
            "-v",
            "{}:/mtriage".format(DIR_PATH),
            "--workdir",
            "/mtriage/src",
            "{}:dev".format(NAME),
            "python",
            "-m",
            "pytest",
        ]
    )
    if returncode is 1:
        exit(returncode)


def __run_runpy_tests():
    # NOTE: runpy tests are not run in a docker container, as they operate on the local machine-- so this test is run
    # using the LOCAL python (could be 2 or 3).
    returncode = sp.call(["python", "-m", "pytest", "test/"])
    if returncode is 1:
        exit(returncode)


def test():
    print("Creating container to run tests...")
    print("----------------------------------")
    __run_lib_tests()
    __run_runpy_tests()
    print("----------------------------------")
    print("All tests for mtriage done.")


if __name__ == "__main__":
    COMMANDS = {"build": build, "develop": develop, "test": test, "clean": clean}
    parser = argparse.ArgumentParser(description="mtriage dev scripts")
    parser.add_argument("command", choices=COMMANDS.keys())

    args = parser.parse_args()

    cmd = COMMANDS[args.command]
    cmd()
