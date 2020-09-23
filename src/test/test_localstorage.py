import pytest
import json
from pathlib import Path
from lib.common.storage import LocalStorage


@pytest.fixture
def basic(utils):
    global base
    base = utils.TEMP_ELEMENT_DIR

    utils.scaffold_empty("Youtube", elements=["el1"], analysers=["Me"])
    utils.setup()
    yield LocalStorage(folder=base)
    utils.cleanup()


def test_core(basic):
    assert basic.base_dir == Path(base)


def test_read_query(utils, basic):
    assert isinstance(basic.read_query("Youtube"), Path)
    assert basic.read_query("Youtube") == Path(f"{base}/Youtube/{basic.RETRIEVED_EXT}")
    assert basic.read_query("Youtube/Me") == Path(
        f"{base}/Youtube/{basic.ANALYSED_EXT}/Me"
    )


def test_read_all_media(utils, basic):
    cmpDict = {
        "Youtube": {
            f"{basic.RETRIEVED_EXT}": {
                "el1": f"{base}/Youtube/{basic.RETRIEVED_EXT}/el1",
            },
            f"{basic.ANALYSED_EXT}": {
                "Me": {
                    "el1": f"{base}/Youtube/{basic.ANALYSED_EXT}/Me/el1",
                },
            },
        },
    }
    mediaDict = basic.read_all_media()
    assert utils.dictsEqual(cmpDict, mediaDict)


def test_write_meta(basic):
    q = "Youtube/Me"
    og_data = {"some": "data"}
    basic.write_meta(q, og_data)
    with open(f"{basic.read_query(q)}/{basic._LocalStorage__META_FILE}", "r") as f:
        data = json.load(f)
    assert data == og_data
