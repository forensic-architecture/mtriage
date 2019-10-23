"""
Setup global fixtures for modular-wise tests.
"""
import pytest
import requests
import os
import test.utils as test_utils


@pytest.fixture(scope="session", autouse=True)
def test_element_dir():
    return "../media/test"


# TODO(lachlan): create a special fixture to allow component-wise tests to analyse sub elements
# EG_VIDEO = "https://datasheet-sources.ams3.digitaloceanspaces.com/ilovaisk_videos/platform_background.mp4"
# EG_IMAGE = "https://datasheet-sources.ams3.digitaloceanspaces.com/ilovaisk_videos/Platform_Tutorial_thumb.png"
#
# @pytest.fixture(scope="session", autouse=True)
# def analyse_stub_element()
#     if not os.path.exists("/test"):
#         os.makedirs("/test")
#     if not os.path.exists("/test/video.mp4"):
#         r = requests.get(EG_VIDEO)
#         open("/test/video.mp4", "wb").write(r.content)
#     if not os.path.exists("/test/image.png"):
#         r = requests.get(EG_IMAGE)
#         open("/test/image.png", "wb").write(r.content)
#
#     return "some val"


@pytest.fixture(scope="session", autouse=True)
def utils():
    return test_utils
