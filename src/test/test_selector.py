from lib.common.selector import Selector
from abc import ABC

def func(x):
    return x + 1

def test_selector_imports():
    assert type(Selector) == type(ABC)
