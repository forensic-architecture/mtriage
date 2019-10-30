import unittest
import os
import csv
from commands import parse_args, build, develop, clean, run_tests, run, DIR_PATH


def get_tag_str(cmd, tag):
    """
    Returns the string for a tag in a command, or 'None' if the tag doesn't exist.
    """
    idx = 0
    while len(cmd) > idx and cmd[idx] != tag:
        idx += 1
    if idx <= len(cmd) - 1:
        return cmd[idx + 1]
    return None


def dockerimage_tag_matches(cmd, expected):
    build_tag = get_tag_str(cmd, "-t")
    if build_tag:
        return build_tag == expected
    return False


def builds_from_cpu_dockerfile(dfile):
    return "FROM ubuntu:18.04\n" in dfile


def builds_from_gpu_dockerfile(dfile):
    return "FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04\n" in dfile


def read_deps(component):
    pth = "src/lib/selectors/{}/requirements.txt".format(component)
    if not os.path.exists(pth):
        return []
    with open(pth, "r") as f:
        return f.readlines()


class TestBuild(unittest.TestCase):
    def setUp(self):
        # make test whitelist
        self.SELECTOR_WL = "selector_whitelist.txt"
        with open(self.SELECTOR_WL, "w") as f:
            writer = csv.writer(f)
            writer.writerows([["youtube"], ["twitter"]])

        self.BLANK_WL = "blank_whitelist.txt"
        with open(self.BLANK_WL, "w") as f:
            writer = csv.writer(f)
            writer.writerows([[""]])

    def tearDown(self):
        os.remove(self.SELECTOR_WL)
        os.remove(self.BLANK_WL)

    def test_default_build(self):
        args = parse_args(["dev", "build", "--dry"])
        cmd, dfile, pipfile = build(args)
        self.assertTrue(
            dockerimage_tag_matches(cmd, "forensicarchitecture/mtriage:dev")
        )
        self.assertTrue(builds_from_cpu_dockerfile(dfile))

    def test_gpu_build(self):
        args = parse_args(["dev", "build", "--gpu", "--dry"])
        cmd, dfile, pipfile = build(args)
        self.assertTrue(builds_from_gpu_dockerfile(dfile))

    def test_whitelist(self):
        args = parse_args(["dev", "build", "--whitelist", self.BLANK_WL, "--dry"])
        cmd, dfile, pipfile = build(args)
        with open("src/build/core.requirements.txt", "r") as f:
            core_deps = f.readlines()
        self.assertListEqual(core_deps, pipfile)

        args = parse_args(["dev", "build", "--whitelist", self.SELECTOR_WL, "--dry"])
        cmd, dfile, pipfile = build(args)
        self.assertListEqual(
            pipfile, core_deps + read_deps("youtube") + read_deps("twitter")
        )

    def test_custom_tags(self):
        args = parse_args(["dev", "build", "--tag", "CUSTOM_TAG", "--dry"])
        cmd, dfile, pipfile = build(args)
        self.assertTrue(
            dockerimage_tag_matches(cmd, "forensicarchitecture/mtriage:CUSTOM_TAG")
        )

        args = parse_args(
            ["run", "examples/youtube.yaml", "--tag", "CUSTOM_TAG", "--dry"]
        )
        cmd = run(args)
        self.assertTrue(cmd[-1] == "forensicarchitecture/mtriage:CUSTOM_TAG")
