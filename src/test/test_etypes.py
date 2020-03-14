import pytest
from types import SimpleNamespace as Ns
from pathlib import Path
from lib.common.etypes import Etype, Union, Array, all_etypes, cast
from lib.common.exceptions import EtypeCastError
from test import utils


def write_stub(f):
    with open(f, "w+") as f:
        f.write("stub")


@pytest.fixture
def base():
    obj = Ns()
    obj.id = "xasd123"
    obj.txt1 = Path("/tmp/1.txt")
    obj.md1 = Path("/tmp/1.md")
    obj.im1 = Path("/tmp/1.png")
    obj.im2 = Path("/tmp/2.jpg")
    obj.im3 = Path("/tmp/3.bmp")
    obj.aud1 = Path("/tmp/1.mp3")
    write_stub(obj.txt1)
    write_stub(obj.md1)
    write_stub(obj.im1)
    write_stub(obj.im2)
    write_stub(obj.im3)
    write_stub(obj.aud1)
    yield obj
    utils.cleanup()


def test_etype_construction(base):
    # shouldn't be okay with empty
    for t in all_etypes():
        with pytest.raises(EtypeCastError):
            assert t(base.id, [])


def test_Any(base):
    e = Etype.Any(base.id, [base.txt1])
    assert len(e.paths) == 1
    e = Etype.Any(base.id, [base.txt1, base.md1, base.im3])
    assert len(e.paths) == 3


def test_Image(base):
    # shouldn't accept one txt
    with pytest.raises(EtypeCastError):
        Etype.Image(base.id, ["/tmp/notafile.txt"])

    # shouldn't accept an image that doesn't exist
    with pytest.raises(EtypeCastError):
        Etype.Image(base.id, ["/tmp/nonexistent_image.png"])

    # shouldn't be okay with 2 valid images
    with pytest.raises(EtypeCastError):
        Etype.Image(base.id, [base.im1, base.im2])

    # works with either single path or list
    im1 = Etype.Image(base.id, base.im1)
    assert len(im1.paths) == 1
    im1 = Etype.Image(base.id, [base.im1])
    assert len(im1.paths) == 1
    im2 = Etype.Image(base.id, base.im2)
    assert len(im1.paths) == 1

    # filters out invalid files
    im1_filtered = Etype.Image(base.id, [base.im1, base.txt1])
    assert len(im1.paths) == 1
    assert im1.paths[0] == base.im1

def test_Array(base):
    ImArr = Array(Etype.Image)
    with pytest.raises(EtypeCastError):
        ImArr(base.id, [])

    with pytest.raises(EtypeCastError):
        ImArr(base.id, base.txt1)

    has1 = ImArr(base.id, base.im1)
    assert len(has1.paths) == 1
    has3 = ImArr(base.id, [base.im1, base.im2, base.im3])
    assert len(has3.paths) == 3
    has2 = ImArr(base.id, [base.im1, base.md1, base.txt1, base.im3])
    assert len(has2.paths) == 2


def test_Union(base):
    ImAud = Union(Etype.Image, Etype.Audio)
    with pytest.raises(EtypeCastError):
        ImAud(base.id, [])
    with pytest.raises(EtypeCastError):
        ImAud(base.id, base.txt1)
    with pytest.raises(EtypeCastError):
        ImAud(base.id, base.im1)
    with pytest.raises(EtypeCastError):
        ImAud(base.id, base.aud1)

    has2 = ImAud(base.id, [base.aud1, base.im1])
    assert len(has2.paths) == 2
    f2 = ImAud(base.id, [base.im3, base.md1, base.aud1])
    assert len(f2.paths) == 2
    assert base.im3 in f2.paths
    assert base.aud1 in f2.paths

def test_cast(base):
    # explicit cast
    with pytest.raises(EtypeCastError):
        cast(base.id, [], Etype.Image)
    with pytest.raises(EtypeCastError):
        cast(base.id, [base.txt1], Etype.Image)

    t1 = cast(base.id, [base.im1], to=Etype.Image)
    assert len(t1.paths) == 1
    assert t1.et == Etype.Image

    # implicit cast
    with pytest.raises(EtypeCastError):
        cast(base.id, [])

    i1 = cast(base.id, [base.im1])
    assert len(i1.paths) == 1
    assert i1.et == Etype.Image
    i2 = cast(base.id, [base.im2])
    assert len(i2.paths) == 1
    assert i2.et == Etype.Image

    ia1 = cast(base.id, [base.im1, base.im2])
    assert len(ia1.paths) == 2
    assert ia1.et == Array(Etype.Image)

    a1 = cast(base.id, base.aud1)
    assert len(a1.paths) == 1
    assert a1.et == Etype.Audio

    # unions

    ai1 =  cast(base.id, [base.im3, base.aud1])
    assert len(ai1.paths) == 2
    assert ai1.et == Union(Etype.Image, Etype.Audio)

    ai2 = cast(base.id, [base.aud1, base.im2])
    assert len(ai1.paths) == 2
    assert ai1.et == Union(Etype.Image, Etype.Audio)

    iaa1 = cast(base.id, [base.im1, base.im2, base.aud1])
    assert len(iaa1.paths) == 3
    assert iaa1.et == Union(Array(Etype.Image), Etype.Audio)

    any1 = cast(base.id, [base.im1, base.im2, base.aud1, base.txt1])
    assert len(any1.paths) == 4
    assert any1.et == Etype.Any
