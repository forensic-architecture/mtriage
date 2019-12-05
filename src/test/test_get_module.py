import pytest
import shutil
from os import listdir, makedirs
from os.path import isdir
from lib.common.get_module import get_module


def make_empty_main_export(pth):
    INIT = 'main = True\n__all__ = ["main"]\n'
    with open(f"{pth}/__init__.py", "w") as f:
        f.write(INIT)


@pytest.fixture
def additionals():
    obj = lambda: None
    """ Make imaginary selector and analysers """
    # tests always run from src
    obj.EMPTY_SELECTOR = "./lib/selectors/empty"
    obj.EMPTY_ANALYSER = "./lib/analysers/empty"

    if isdir(obj.EMPTY_SELECTOR):
        shutil.rmtree(obj.EMPTY_SELECTOR)
    if isdir(obj.EMPTY_ANALYSER):
        shutil.rmtree(obj.EMPTY_ANALYSER)

    makedirs(obj.EMPTY_SELECTOR)
    make_empty_main_export(obj.EMPTY_SELECTOR)
    makedirs(obj.EMPTY_ANALYSER)
    make_empty_main_export(obj.EMPTY_ANALYSER)
    yield obj
    if isdir(obj.EMPTY_SELECTOR):
        shutil.rmtree(obj.EMPTY_SELECTOR)
    if isdir(obj.EMPTY_ANALYSER):
        shutil.rmtree(obj.EMPTY_ANALYSER)


# NOTE: additionals added as arg to ensure fixture setup is run
def test_raises_when_faulty(additionals):
    with pytest.raises(ModuleNotFoundError):
        get_module("select", "smth")

    with pytest.raises(ModuleNotFoundError):
        get_module("analyse", "smth")

    with pytest.raises(ImportError, match="must be either 'select' or 'analyse'"):
        get_module("neitherthing", "smth")


def test_imports_main(additionals):
    # main just exported as 'True', to check import logic is correct
    assert get_module("select", "empty")
    assert get_module("analyse", "empty")
