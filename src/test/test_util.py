import pytest
import os
from lib.common.util import save_logs

LOGPATH = "testlog.txt"


@pytest.fixture
def additionals(autouse=True):
    if os.path.exists(LOGPATH):
        os.remove(LOGPATH)


def test_save_no_logs(additionals):
    save_logs([], LOGPATH)
    assert not os.path.exists(LOGPATH)


def test_save_one_log(additionals):
    save_logs(["test log 1"], LOGPATH)
    assert os.path.exists(LOGPATH)
    assert "test log 1" in open(LOGPATH).read()


def test_save_another_log(additionals):
    save_logs(["test log 1"], LOGPATH)
    save_logs(["test log 2"], LOGPATH)
    assert os.path.exists(LOGPATH)
    with open(LOGPATH) as file:
        f = file.read()
        assert "test log 2" in f
        assert "test log 1" in f


def test_save_multiple_logs(additionals):
    save_logs(["test log 3", "test log 4"], LOGPATH)
    assert os.path.exists(LOGPATH)
    with open(LOGPATH) as file:
        f = file.read()
        assert "test log 3" in f
        assert "test log 4" in f
