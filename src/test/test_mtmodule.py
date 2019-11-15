import pytest
import os
from lib.common.exceptions import ImproperLoggedPhaseError, BatchedPhaseArgNotGenerator
from lib.common.mtmodule import MTModule
from test.utils import scaffold_empty


class EmptyMTModule(MTModule):
    pass


@pytest.fixture
def additionals(utils):
    obj = lambda: None
    obj.BASE_DIR = utils.TEMP_ELEMENT_DIR
    obj.mod = EmptyMTModule({}, "empty", obj.BASE_DIR)
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


def test_logged_phase_decorator(additionals):
    class BadClass:
        @MTModule.logged_phase("somekey")
        def improper_func(self):
            pass

    class GoodClass(MTModule):
        @MTModule.logged_phase("somekey")
        def proper_func(self):
            self.logger("we did something.")
            return "no error"

    # test that a decorated method carries through its return value
    gc = GoodClass({}, "my_good_mod", additionals.BASE_DIR)

    assert gc.proper_func() == "no error"

    with open(f"{additionals.BASE_DIR}/logs/my_good_mod.txt", "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        assert lines[0] == "my_good_mod: somekey: we did something.\n"

    # check that logs were cleared after phase
    assert gc._MTModule__LOGS == []


def test_batched_phase_decorator(additionals):
    class GoodClass(MTModule):
        @MTModule.batched_phase("somekey")
        def func(self, gen):
            self.logger("This function only takes a generator of elements.")
            return "no error"

        @MTModule.batched_phase("somekey", False)
        def func_no_remove(self, gen):
            return "no error"

        @MTModule.batched_phase("secondkey")
        def func_w_arg(self, gen, extra):
            self.logger(f"Running func with {list(gen)}, with extra arg {extra}.")
            return "no error"

    # test that a decorated method carries through its return value
    gc = GoodClass({}, "my_good_mod", additionals.BASE_DIR)

    with pytest.raises(BatchedPhaseArgNotGenerator):
        gc.func(1)

    # test parallel logs
    eg_gen = (a for a in range(0, 100))
    assert gc.func(eg_gen) == "no error"

    with open(f"{additionals.BASE_DIR}/logs/my_good_mod.txt", "r") as f:
        lines = f.readlines()
        assert len(lines) == 100

    # test db file generation
    eg_gen = (a for a in range(0, 100))
    assert gc.func_no_remove(eg_gen) == "no error"

    dbfile = f"{gc.BASE_DIR}/{gc.UNIQUE_ID}.db"
    with open(dbfile, "rb") as f:
        _bytes = f.read()
        assert len(_bytes) == 800  # 2 4-byte entries per item for 100 items

    os.remove(dbfile)

    # test that a function is resumed properly
    eg_gen = (a for a in range(0, 50))
    assert gc.func_no_remove(eg_gen) == "no error"

    eg_gen = (a for a in range(0, 100))
    assert gc.func(eg_gen) == "no error"

    with open(f"{additionals.BASE_DIR}/logs/my_good_mod.txt", "r") as f:
        lines = f.readlines()
        assert len(lines) == 150

    # test function with argument
    eg_gen = (a for a in range(0, 100))
    assert gc.func_w_arg(eg_gen, 10) == "no error"
