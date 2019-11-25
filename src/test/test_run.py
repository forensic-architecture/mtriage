import pytest
import os
import yaml
from run import validate_yaml
from lib.common.exceptions import InvalidConfigError

ARGS = "/run_args.yaml"


@pytest.fixture(autouse=True)
def teardown():
    yield None
    try:
        os.remove(ARGS)
    except:
        pass


def write(vl):
    with open(ARGS, "w") as c:
        yaml.dump(vl, c, default_flow_style=False)


def validate():
    with open(ARGS, "r") as c:
        cfg = yaml.safe_load(c)
    validate_yaml(cfg)


def test_bad_yaml():
    with open(ARGS, "w") as c:
        c.write('foo: "an escaped \\\' single quote"')

    with pytest.raises(yaml.YAMLError):
        validate()


def test_validate_phase():
    empty = {}
    bad_folder = {"folder": 1, "config": {}}
    good_folder = {"folder": "legit", "config": {}}

    write(empty)
    with pytest.raises(
        InvalidConfigError, match="The folder attribute must exist and be a string"
    ):
        validate()

    write(bad_folder)
    with pytest.raises(
        InvalidConfigError, match="The folder attribute must exist and be a string"
    ):
        validate()

    bad_phase = {**good_folder, "phase": "not a phase"}
    good_phase_select = {**good_folder, "phase": "select"}
    good_phase_analyse = {**good_folder, "phase": "analyse"}
    write(bad_phase)
    with pytest.raises(
        InvalidConfigError, match="specified a phase, you must specify a module"
    ):
        validate()

    bad_select_module = {**good_phase_select, "module": "not a selector"}
    bad_analyse_module = {**good_phase_analyse, "module": "not an analyser"}
    good_select_module = {**good_phase_select, "module": "local"}
    write(bad_select_module)
    with pytest.raises(
        InvalidConfigError, match="No select module named 'not a selector'"
    ):
        validate()

    write(bad_analyse_module)
    with pytest.raises(
        InvalidConfigError, match="No analyse module named 'not an analyser'"
    ):
        validate()

    # the select module requires a 'source_folder' arg
    bad_local_config = {**good_select_module, "config": {}}
    bad_youtube_config = {
        **good_select_module,
        "module": "youtube",
        "config": {"uploaded_before": "212321"},
    }
    good_youtube_config = {
        **good_select_module,
        "module": "youtube",
        "config": {
            "search_term": "a search term",
            "uploaded_before": "212321",
            "uploaded_after": "212321",
        },
    }

    if os.path.exists("/mtriage/credentials/google.json"):
        write(good_select_module)
        with pytest.raises(
            InvalidConfigError, match="The 'config' attribute must exist."
        ):
            validate()

        write(bad_local_config)
        with pytest.raises(
            InvalidConfigError,
            match="The config you specified does not contain all the required arguments for the 'local' selector.",
        ):
            validate()

        write(bad_youtube_config)
        with pytest.raises(
            InvalidConfigError,
            match="The config you specified does not contain all the required arguments for the 'youtube' selector.",
        ):
            validate()

        write(good_youtube_config)
        validate()


def test_validate():
    bad_config = {"folder": "media/test_official", "config": {}}
    write(bad_config)
    with pytest.raises(
        InvalidConfigError,
        match="no phase must include 'select' or 'analyse' attributes",
    ):
        validate()
