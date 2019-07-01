import unittest
from run import _run_yaml
import yaml
from lib.common.exceptions import InvalidConfigError

def write_config(vl):
    with open("/run_args.yaml", "w") as c:
        yaml.dump(vl, c, default_flow_style=False)

class TestRun(unittest.TestCase):

    def test_bad_yaml(self):


        with open("/run_args.yaml", "w") as c:
            c.write("foo: \"an escaped \\' single quote\"")

        with self.assertRaises(yaml.YAMLError):
            _run_yaml()

    def test_bad_config(self):
        empty = {}
        bad_folder = {"folder":1}
        good_folder = {"folder":"legit"}

        write_config(empty)
        with self.assertRaisesRegex(InvalidConfigError, "The folder attribute must exist and be a string"):
            _run_yaml()

        write_config(bad_folder)
        with self.assertRaisesRegex(InvalidConfigError, "The folder attribute must exist and be a string"):
            _run_yaml()

        bad_phase = {**good_folder, "phase":"not a phase"}
        good_phase_select = {**good_folder, "phase":"select"}
        good_phase_analyse = {**good_folder, "phase":"analyse"}
        write_config(bad_phase)
        with self.assertRaisesRegex(InvalidConfigError, "The phase attribute must be either select or analyse"):
            _run_yaml()

        bad_select_module = {**good_phase_select, "module":"not a selector"}
        bad_analyse_module = {**good_phase_analyse, "module":"not an analyser"}
        good_select_module = {**good_phase_select, "module":"local"}
        write_config(bad_select_module)
        with self.assertRaisesRegex(InvalidConfigError, "No selector named 'not a selector'"):
            _run_yaml()

        write_config(bad_analyse_module)
        with self.assertRaisesRegex(InvalidConfigError, "No analyser named 'not an analyser'"):
            _run_yaml()

        # good_select_module = {**good_phase_select, "module":"local"}
