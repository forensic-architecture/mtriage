import os
import csv
import yaml
import argparse
import subprocess as sp
from util import *

NAME = "forensicarchitecture/mtriage"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
HOME_PATH = os.path.expanduser("~")


def __run(cmd, cli_args, *args):
    if cli_args.dry:
        return cmd
    try:
        returncode = sp.call(cmd)
        if len(args) >= 1:
            print(args[0])
        return returncode
    except:
        if len(args) >= 2:
            print(args[1])


def __run_core_tests(args):
    return __run(
        [
            "docker",
            "run",
            "--env",
            "BASE_DIR=/mtriage",
            get_env_config(),
            "--rm",
            "-v",
            "{}:/mtriage".format(DIR_PATH),
            "--workdir",
            "/mtriage/src",
            "{}:dev".format(NAME),
            "python",
            "-m",
            "pytest",
            ".",
        ],
        args,
    )


def __run_runpy_tests(args):
    """ NOTE: runpy tests are not run in a docker container, as they operate on the local machine-- so this test is run
    using the LOCAL python (could be 2 or 3). """
    return __run(["python", "-m", "pytest", "-s", "test/"], args)


def build(args, is_testing=False):
    """ Collect all partial Pip and Docker files from selectors and analysers, and combine them with the core mtriage
        dependencies in src/build in order to create an appropriate Dockerfile and requirements.txt.
        NOTE: There is currently no way to include/exclude certain selector dependencies, but this build process is
              the setup for that optionality.
    """

    # setup
    TAG_NAME = "{}-gpu".format(args.tag) if args.gpu else args.tag
    DOCKER_BASE = "core-gpu" if args.gpu else "core-cpu"

    DOCKERFILE_PARTIAL = "partial.Dockerfile"
    PIP_PARTIAL = "requirements.txt"
    BUILD_DOCKERFILE = "{}/build.Dockerfile".format(DIR_PATH)
    BUILD_PIPFILE = "{}/build.requirements.txt".format(DIR_PATH)
    CORE_PIPDEPS = "{}/src/build/core.requirements.txt".format(DIR_PATH)
    CORE_START_DOCKER = "{}/src/build/{}.start.Dockerfile".format(DIR_PATH, DOCKER_BASE)
    CORE_END_DOCKER = "{}/src/build/core.end.Dockerfile".format(DIR_PATH)
    ANALYSERS_PATH = "{}/src/lib/analysers".format(DIR_PATH)
    SELECTORS_PATH = "{}/src/lib/selectors".format(DIR_PATH)
    BLACKLIST = []

    print("Collecting partial dependencies from selector and analyser folders...")
    with open(CORE_PIPDEPS) as cdeps:
        pipdeps = cdeps.readlines()

    with open(CORE_START_DOCKER) as dfile:
        dockerlines = dfile.readlines()

    # search all selectors/analysers for partials
    selectors = get_subdirs(SELECTORS_PATH)
    analysers = get_subdirs(ANALYSERS_PATH)

    # parse blacklist
    if not args.whitelist and args.blacklist:
        with open(args.blacklist, "r") as f:
            bl = csv.reader(f, delimiter=" ")
            BLACKLIST = list(filter(lambda x: len(x) > 1, map(extract_dep, bl)))

    elif args.whitelist:
        # create blacklist from whitelist
        BLACKLIST = selectors + analysers
        with open(args.whitelist, "r") as f:
            wl = csv.reader(f, delimiter=" ")
            for row in wl:
                dep = extract_dep(row)
                if dep is not "":
                    BLACKLIST.remove(dep)

    for selector in selectors:
        if selector in BLACKLIST:
            continue
        docker_dep = "{}/{}/{}".format(SELECTORS_PATH, selector, DOCKERFILE_PARTIAL)
        pip_dep = "{}/{}/{}".format(SELECTORS_PATH, selector, PIP_PARTIAL)

        add_deps(docker_dep, dockerlines, should_add_dockerline)
        add_deps(pip_dep, pipdeps, should_add_pipdep)

    for analyser in analysers:
        if analyser in BLACKLIST:
            continue
        docker_dep = "{}/{}/{}".format(ANALYSERS_PATH, analyser, DOCKERFILE_PARTIAL)
        pip_dep = "{}/{}/{}".format(ANALYSERS_PATH, analyser, PIP_PARTIAL)

        add_deps(docker_dep, dockerlines, should_add_dockerline)
        add_deps(pip_dep, pipdeps, should_add_pipdep)

    with open(CORE_END_DOCKER) as f:
        for line in f.readlines():
            dockerlines.append(line)

    with open(BUILD_PIPFILE, "w") as f:
        for dep in pipdeps:
            f.write(dep)

    with open(BUILD_DOCKERFILE, "w") as f:
        for line in dockerlines:
            f.write(line)

    print("All Docker dependencies collected in build.Dockerfile.")
    print("All Pip dependencies collected in build.requirements.txt.")
    print("--------------------------------------------------------")

    if args.gpu:
        print("GPU flag enabled, building for nvidia-docker...")
    else:
        print("Building for CPU in Docker...")

    cmd = [
        "docker",
        "build",
        "-t",
        "{}:{}".format(NAME, TAG_NAME),
        "-f",
        BUILD_DOCKERFILE,
        ".",
    ]

    res = __run(
        cmd,
        args,
        "Build successful, run with: \n\tpython run.py develop",
        "Something went wrong! EEK",
    )

    # cleanup
    if os.path.exists(BUILD_DOCKERFILE):
        with open(BUILD_DOCKERFILE, "r") as f:
            build_dockerfile = f.readlines()
        os.remove(BUILD_DOCKERFILE)
    if os.path.exists(BUILD_PIPFILE):
        with open(BUILD_PIPFILE, "r") as f:
            build_pipfile = f.readlines()
        os.remove(BUILD_PIPFILE)

    return res, build_dockerfile, build_pipfile


def develop(args):
    CONT_NAME = "mtriage_developer"
    TAG_NAME = "{}-gpu".format(args.tag) if args.gpu else args.tag

    # --runtime only exists on nvidia docker, so we pass a bubblegum flag when not available
    # so that the call arguments are well formed.
    return __run(
        [
            "docker",
            "run",
            "-it",
            "--rm",
            "--name",
            CONT_NAME,
            "--runtime=nvidia" if args.gpu else "--ipc=host",
            "--env",
            "BASE_DIR=/mtriage",
            get_env_config(),
            "--privileged",
            "-v",
            "{}:/mtriage".format(DIR_PATH),
            "-v",
            "{}/.config/gcloud:/root/.config/gcloud".format(HOME_PATH),
            "{}:{}".format(NAME, TAG_NAME),
            "/bin/bash",
        ],
        args,
    )


def clean(args):
    ps = sp.Popen(["docker", "ps", "--filter", "name=mtriage", "-aq"], stdout=sp.PIPE)
    try:
        sp.check_output(["xargs", "docker", "rm"], stdin=ps.stdout)
    except:
        pass


def run_tests(args):
    print("Creating container to run tests...")
    print("----------------------------------")
    core = __run_core_tests(args)
    outer = __run_runpy_tests(args)

    if core >= 1 or outer >= 1:
        exit(1)
    print("----------------------------------")
    print("All tests for mtriage done.")


def run(args):
    # read yaml args to construct container name
    yaml_path = os.path.abspath(args.yaml)
    with open(yaml_path, "r") as f:
        options = yaml.safe_load(f)
    CONT_NAME = f"mtriage_{options['phase']}_{options['module']}-{os.path.basename(options['folder'])}"
    TAG_NAME = "{}-gpu".format(args.tag) if args.gpu else args.tag

    # --runtime only exists on nvidia docker, so we pass a bubblegum flag when not available
    # so that the call arguments are well formed.
    return __run(
        [
            "docker",
            "run",
            "--name",
            CONT_NAME,
            "--runtime=nvidia" if args.gpu else "--ipc=host",
            "--env",
            "BASE_DIR=/mtriage",
            get_env_config(),
            "--privileged",
            "-v",
            "{}:/mtriage".format(DIR_PATH),
            "-v",
            "{}:/run_args.yaml".format(yaml_path),
            "-v",
            "{}/.config/gcloud:/root/.config/gcloud".format(HOME_PATH),
            "{}:{}".format(NAME, TAG_NAME),
        ],
        args,
    )


def parse_args(cli_args):
    parser = argparse.ArgumentParser(description="mtriage dev scripts")
    subparsers = parser.add_subparsers(dest="__base")

    run_p = subparsers.add_parser("run")
    run_p.add_argument("yaml", type=str2yamlfile)
    run_p.add_argument("--tag", default="dev")
    run_p.add_argument("--gpu", action="store_true")
    run_p.add_argument("--dry", action="store_true")

    dev_p = subparsers.add_parser("dev")
    dev_p.add_argument("--whitelist")
    dev_p.add_argument("--blacklist")
    dev_p.add_argument("--tag", default="dev")
    dev_p.add_argument("--gpu", action="store_true")
    dev_p.add_argument("--dry", action="store_true")
    dev_p.add_argument(
        "command",
        choices=["develop", "build", "test", "clean"],
        default="develop",
        const="develop",
        nargs="?",
    )

    return parser.parse_args(cli_args)
