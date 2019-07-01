import unittest
from run import validate_yaml
import yaml
from lib.common.exceptions import InvalidConfigError


def write_config(vl):
    with open("/run_args.yaml", "w") as c:
        yaml.dump(vl, c, default_flow_style=False)

def validate_config():
    with open("/run_args.yaml", "r") as c:
        cfg = yaml.safe_load(c)
    print(cfg)
    validate_yaml(cfg)


class TestRun(unittest.TestCase):
    def test_bad_yaml(self):

        with open("/run_args.yaml", "w") as c:
            c.write('foo: "an escaped \\\' single quote"')

        with self.assertRaises(yaml.YAMLError):
            validate_config()

    def test_bad_config(self):
        empty = {}
        bad_folder = {"folder": 1}
        good_folder = {"folder": "legit"}

        write_config(empty)
        with self.assertRaisesRegex(
            InvalidConfigError, "The folder attribute must exist and be a string"
        ):
            validate_config()

        write_config(bad_folder)
        with self.assertRaisesRegex(
            InvalidConfigError, "The folder attribute must exist and be a string"
        ):
            validate_config()

        bad_phase = {**good_folder, "phase": "not a phase"}
        good_phase_select = {**good_folder, "phase": "select"}
        good_phase_analyse = {**good_folder, "phase": "analyse"}
        write_config(bad_phase)
        with self.assertRaisesRegex(
            InvalidConfigError, "The phase attribute must be either select or analyse"
        ):
            validate_config()

        bad_select_module = {**good_phase_select, "module": "not a selector"}
        bad_analyse_module = {**good_phase_analyse, "module": "not an analyser"}
        good_select_module = {**good_phase_select, "module": "local"}
        write_config(bad_select_module)
        with self.assertRaisesRegex(
            InvalidConfigError, "No selector named 'not a selector'"
        ):
            validate_config()

        write_config(bad_analyse_module)
        with self.assertRaisesRegex(
            InvalidConfigError, "No analyser named 'not an analyser'"
        ):
            validate_config()

        # the select module requires a 'source_folder' arg
        bad_local_config = {**good_select_module, "config": {}}
        bad_youtube_config = {**good_select_module, "module": "youtube", "config": {
            "search_term": "a search term",
            "uploaded_before": "212321",
        }}
        good_youtube_config = {**good_select_module, "module": "youtube", "config": {
            "search_term": "a search term",
            "uploaded_before": "212321",
            "uploaded_after": "212321",
        }}

        write_config(good_select_module)
        with self.assertRaisesRegex(
            InvalidConfigError, "The 'config' attribute must exist."
        ):
            validate_config()

        write_config(bad_local_config)
        with self.assertRaisesRegex(
            InvalidConfigError,
            "The config you specified does not contain all the required arguments for the 'local' selector.",
        ):
            validate_config()

        write_config(bad_youtube_config)
        with self.assertRaisesRegex(
            InvalidConfigError,
            "The config you specified does not contain all the required arguments for the 'youtube' selector.",
        ):
            validate_config()


        write_config(good_youtube_config)
        validate_config()
