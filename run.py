import docker
import os
import argparse
from subprocess import call

NAME = "mtriage_beta"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
HOME_PATH = os.path.expanduser("~")
DOCKER = docker.from_env()


def build():
    # TODO: port to docker py CLI.
    print(f"Building {NAME} image in Docker...")
    print("This may take a few minutes...")
    try:
        call(
            [
                "docker",
                "build",
                "-t",
                f"{NAME}:dev",
                "-f",
                "development.Dockerfile",
                ".",
            ]
        )
        print("Build successful, run with: \n\tpython run.py develop")
    except:
        print("Something went wrong. Run command directly to debug:")
        print(f"\tdocker build -t {NAME}:dev -f development.Dockerfile .")


def develop():
    # https://docker-py.readthedocs.io/en/stable/containers.html
    cont_name = f"{NAME}"
    try:
        DOCKER.containers.get(cont_name)
    except docker.errors.NotFound:
        print(f"Building container from {NAME}:dev...")
        # TODO: remake with docker py CLI.
        call(
            [
                "docker",
                "run",
                "-it",
                "--name",
                cont_name,
                "--rm",
                "--privileged",
                "-v",
                f"{DIR_PATH}:/mediatriage",
                "-v",
                f"{HOME_PATH}/.config/gcloud:/root/.config/gcloud",
                "-p",
                "5000:5000",
                "{NAME}:dev",
            ]
        )


if __name__ == "__main__":
    COMMANDS = {"build": build, "develop": develop}
    parser = argparse.ArgumentParser(description="mtriage dev scripts")
    parser.add_argument("command", choices=COMMANDS.keys())

    args = parser.parse_args()

    cmd = COMMANDS[args.command]
    cmd()

