import pytest
import yaml
from os import listdir


def is_valid_arg(arg):
    if "name" not in arg or not isinstance(arg["name"], str):
        return False
    if "required" not in arg or not isinstance(arg["required"], bool):
        return False
    # NOTE: not checking for 'input' or 'desc' attrs, considering them optional at this time.
    return True


@pytest.fixture
def additionals():
    obj = lambda: None
    obj.ALL_ANALYSERS = listdir("lib/analysers")
    obj.ALL_SELECTORS = listdir("lib/selectors")
    return obj


def test_selectors(additionals, utils):
    # selector infos
    for sel in additionals.ALL_SELECTORS:
        with open(utils.get_info_path("selector", sel)) as f:
            info = yaml.safe_load(f)
        assert "desc" in info
        assert "args" in info
        assert isinstance(info["args"], list)
        for arg in info["args"]:
            assert is_valid_arg(arg)

    # analyser infos
    for ana in additionals.ALL_ANALYSERS:
        with open(utils.get_info_path("analyser", ana)) as f:
            info = yaml.safe_load(f)
        assert "desc" in info
        assert "args" in info
        assert isinstance(info["args"], list)
        for arg in info["args"]:
            assert is_valid_arg(arg)
