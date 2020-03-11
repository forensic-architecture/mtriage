import pytest
import os
import yaml
from run import validate_yaml
from lib.common.exceptions import InvalidYamlError
from test.utils import scaffold_empty, cleanup

ARGS = "/run_args.yaml"
BASELINE = {"folder": "media/test_official"}
WITH_ELS = {**BASELINE, "elements_in": "sel1"}
WITH_SELECT = {
    **BASELINE,
    "select": {"name": "local", "config": {"source": "/a-folder"}},
}
GOOD_ANALYSE_DICT = {**WITH_ELS, "analyse": {"name": "frames"}}
GOOD_SELECT_ANALYSE = {
    **WITH_SELECT,
    "analyse": [{"name": "frames"}, {"name": "imagededup"}],
}


def test_config_types():
    res = validate_yaml(GOOD_ANALYSE_DICT)
    assert res == False

    res = validate_yaml(GOOD_SELECT_ANALYSE)
    assert res == False
