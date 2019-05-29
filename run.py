import docker
import inspect
import os
import argparse
from subprocess import call


NAME = "forensicarchitecture/mtriage"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ENV_FILE = "{}/.env".format(DIR_PATH)
HOME_PATH = os.path.expanduser("~")
DOCKER = docker.from_env()


def get_subdirs(d):
    return [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]


def check_in_deps(_str, _arr):
    """Check whether _arr already contains a string representing the same pip dependency as _str.
    """
    lib_name = _str.split("==")[0]
    for depstr in _arr:
        if depstr.find(lib_name) is not -1:
            return True
    return False


def build():
    ANALYSERS_PATH = "{}/src/lib/analysers".format(DIR_PATH)
    SELECTORS_PATH = "{}/src/lib/selectors".format(DIR_PATH)

    BUILD_DOCKERFILE = "{}/build.Dockerfile".format(DIR_PATH)
    BUILD_PIPFILE = "{}/build.requirements.txt".format(DIR_PATH)
    CORE_PIPDEPS = "{}/core.requirements.txt".format(DIR_PATH)
    CORE_START_DOCKER = "{}/core.start.Dockerfile".format(DIR_PATH)
    CORE_END_DOCKER = "{}/core.end.Dockerfile".format(DIR_PATH)

    selectors = get_subdirs(SELECTORS_PATH)
    analysers = get_subdirs(ANALYSERS_PATH)

    with open(CORE_PIPDEPS) as cdeps:
        pipdeps = cdeps.readlines()

    with open(CORE_START_DOCKER) as dfile:
        dockerlines = dfile.readlines()

    def add_pipdeps(path):
        if not os.path.isfile(path):
            return

        with open(path) as f:
            for line in f.readlines():
                if not check_in_deps(line, pipdeps):
                    pipdeps.append(line)

    def add_dockerdeps(path):
        if not os.path.isfile(path):
            return

        with open(path) as f:
            for line in f.readlines():
                dockerlines.append(line)
        dockerlines.append('\n')

    for selector in selectors:
        docker_dep = "{}/{}/Dockerfile".format(SELECTORS_PATH, selector)
        pip_dep = "{}/{}/requirements.txt".format(SELECTORS_PATH, selector)

        add_dockerdeps(docker_dep)
        add_pipdeps(pip_dep)

    for analyser in analysers:
        docker_dep = "{}/{}/Dockerfile".format(ANALYSERS_PATH, analyser)
        pip_dep = "{}/{}/requirements.txt".format(ANALYSERS_PATH, analyser)

        add_dockerdeps(docker_dep)
        add_pipdeps(pip_dep)

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
        print("Something went wrong! EEK")


def develop():
    # https://docker-py.readthedocs.io/en/stable/containers.html
    cont_name = NAME.replace("/", "_")  # NB: no / allowed in container names
    try:
        DOCKER.containers.get(cont_name)
    except docker.errors.NotFound:
        print("Building container from {}:dev...".format(NAME))
        # TODO: remake with docker py CLI.
        call(
            [
                "docker",
                "run",
                "-it",
                "--name",
                cont_name,
                "--env",
                "BASE_DIR=/mtriage",
                "--env-file={}".format(ENV_FILE),
                "--rm",
                "--privileged",
                "-v",
                "{}:/mtriage".format(DIR_PATH),
                "-v",
                "{}/.config/gcloud:/root/.config/gcloud".format(HOME_PATH),
                "-p",
                "5000:5000",
                "{}:dev".format(NAME),
            ]
        )


def test():
    print("Running mtriage tests...")
    print("All tests for mtriage done.")


if __name__ == "__main__":
    COMMANDS = {"build": build, "develop": develop, "test": test}
    parser = argparse.ArgumentParser(description="mtriage dev scripts")
    parser.add_argument("command", choices=COMMANDS.keys())

    args = parser.parse_args()

    cmd = COMMANDS[args.command]
    cmd()
