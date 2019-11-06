import pytest
import os
from lib.common.exceptions import ImproperLoggedPhaseError, BatchedPhaseArgNotGenerator
from lib.common.mtmodule import MTModule


class EmptyMTModule(MTModule):
    pass


@pytest.fixture
def additionals(utils):
    obj = lambda: None
    obj.BASE_DIR = utils.TEMP_ELEMENT_DIR
    obj.mod = EmptyMTModule("empty", obj.BASE_DIR)
    yield obj
    utils.cleanup()


def test_class_variables(additionals):
    assert additionals.mod.NAME == "empty"
    assert additionals.mod.BASE_DIR == additionals.BASE_DIR
    assert additionals.mod._MTModule__LOGS == []
    assert additionals.mod._MTModule__LOGS_DIR == f"{additionals.BASE_DIR}/logs"
    assert (
        additionals.mod._MTModule__LOGS_FILE == f"{additionals.BASE_DIR}/logs/empty.txt"
    )
    assert os.path.exists(f"{additionals.BASE_DIR}/logs")


def test_batched_logged_phase_decorator(additionals):
    # logged_phase decorator should only work on methods that are of a class that inherits from MTModule
    class BadClass:
        @MTModule.batched_logged_phase("somekey")
        def improper_func(self):
            pass

    class GoodClass(MTModule):
        @MTModule.batched_logged_phase("somekey")
        def proper_func(self, with_list):
            self.logger("we did something.")
            return "no error"

    # test that a decorated method carries through its return value
    gc = GoodClass("my_good_mod", additionals.BASE_DIR)

    with pytest.raises(BatchedPhaseArgNotGenerator):
        gc.proper_func(1)

    eg_gen = (a for a in ["a", "b", "c"])
    assert gc.proper_func(eg_gen) == "no error"

    with open(f"{additionals.BASE_DIR}/logs/my_good_mod.txt", "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        assert lines[0] == "my_good_mod: somekey: we did something.\n"

    # check that logs were cleared after phase
    assert gc._MTModule__LOGS == []
