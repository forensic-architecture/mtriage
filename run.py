# -*- coding: utf-8 -*-
import docker
import inspect
import os
import argparse
from subprocess import call


NAME = "forensicarchitecture/mtriage"
CONT_NAME = NAME.replace("/", "_")  # docker doesn't allow slashes in cont names
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ENV_FILE = "{}/.env".format(DIR_PATH)
HOME_PATH = os.path.expanduser("~")
DOCKER = docker.from_env()


def get_subdirs(d):
    return [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]


def check_in_pipdeps(_str, _arr):
    """Check whether _arr already contains a string representing the same pip dependency as _str.
    """
    lib_name = _str.split("==")[0]
    for depstr in _arr:
        if depstr.find(lib_name) is not -1:
            return True
    return False

def check_in_dockerlines(_str, _arr):
    """Check whether _arr already contains a string representing the same line in Dockerfile.
    """
    # NOTE: currently only exactly the same lines are disqualified
    return _str in _arr

def add_deps(dep_path, deps, deps_contains):
    """ Add dependences at {folder_path} to {deps}, excluding if {deps_contains} is True for any given dependency.
    """
    if not os.path.isfile(dep_path):
        return

    with open(dep_path) as f:
        for line in f.readlines():
            if not deps_contains(line, deps):
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

        add_deps(docker_dep, dockerlines, check_in_dockerlines)
        add_deps(pip_dep, pipdeps, check_in_pipdeps)

    for analyser in analysers:
        docker_dep = "{}/{}/{}".format(ANALYSERS_PATH, analyser, DOCKERFILE_PARTIAL)
        pip_dep = "{}/{}/{}".format(ANALYSERS_PATH, analyser, PIP_PARTIAL)

        add_deps(docker_dep, dockerlines, check_in_dockerlines)
        add_deps(pip_dep, pipdeps, check_in_pipdeps)

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

    try:
        call(
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
<<<<<<< ac4250493505e7fc7d5bbb56eedcc10845e79042
    # https://docker-py.readthedocs.io/en/stable/containers.html
    cont_name = NAME.replace("/", "_")  # NB: no / allowed in container names
=======
>>>>>>> incomplete infra to run tests in container from run.py
    try:
        DOCKER.containers.get(CONT_NAME)
        print("Develop container already running. Stop it and try again.")
    except docker.errors.NotFound:
        print("Building container from {}:dev...".format(NAME))
        # TODO: remake with docker py CLI.
        call(
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


<<<<<<< bd6984972bf04df1ebf4cfb9a80202b41e653491
<<<<<<< ac4250493505e7fc7d5bbb56eedcc10845e79042
=======
=======
def clean():
    call(["docker", "rmi", NAME])


>>>>>>> WIP: pytest in container
def __run_cmd(cmd):
    res = DOCKER.containers.run(
        "{}:dev".format(NAME),
        command=cmd,
        remove=True,
        privileged=True,
        volumes={
            DIR_PATH: {"bind": "/mtriage", "mode": "rw"},
            "{}/.config/gcloud".format(HOME_PATH): {
                "bind": "/root/.config/gcloud",
                "mode": "rw",
            },
        },
        environment={"BASE_DIR": "/mtriage"},
    )
    print(res)


>>>>>>> incomplete infra to run tests in container from run.py
def test():
    print("Creating container to run tests...")
    print("----------------------------------")
    __run_cmd("pytest") # NB: doesn't work at the moment.
    print("----------------------------------")
    print("All tests for mtriage done.")


if __name__ == "__main__":
    COMMANDS = {"build": build, "develop": develop, "test": test, "clean": clean}
    parser = argparse.ArgumentParser(description="mtriage dev scripts")
    parser.add_argument("command", choices=COMMANDS.keys())

    args = parser.parse_args()

    cmd = COMMANDS[args.command]
    cmd()
