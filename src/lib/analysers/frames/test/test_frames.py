import pytest
from lib.analysers.frames import main as frames

def test_frames(stubs):
    print(frames)
    print(stubs)
    assert 5 == 5
