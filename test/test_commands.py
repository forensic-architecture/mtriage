import unittest
import os
from commands import parse_args, build, develop, clean, run_tests, run, DIR_PATH


def get_tag_str(cmd, tag):
    """
    Returns the string for a tag in a command, or 'None' if the tag doesn't exist.
    """
    idx = 0
    while len(cmd) > idx and cmd[idx] != tag:
        idx += 1
    if idx <= len(cmd) - 1:
        return cmd[idx+1]
    return None

def dockerimage_matches(cmd, expected):
    build_tag = get_tag_str(cmd, "-t")
    if build_tag:
        return build_tag == expected
    return False

class TestCommands(unittest.TestCase):
    def test_default_build(self):
        args = parse_args(["dev", "build", "--dry"])
        cmd = build(args)
        self.assertTrue(dockerimage_matches(cmd, "forensicarchitecture/mtriage:dev"))



