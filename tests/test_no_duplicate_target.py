from unittest.mock import patch
from sortpics.normalize import non_duplicate_targets


def mock_filesize(sizes):
    def filesize(file):
        return sizes[file]

    return filesize


def test_filesize_not_called(
    filenames=["a.jpg", "b.jpg"], targets=["a.jpg", "b.jpg"], sizes={}
):
    with patch("sortpics.normalize.filesize", mock_filesize(sizes)):
        assert non_duplicate_targets(filenames, targets) == targets


def test_largest_file_preserved(
    filenames=["a.jpg", "b.jpg", "c.jpg"],
    targets=["a.jpg", "b.jpg", "b.jpg"],
    sizes={"b.jpg": 4, "c.jpg": 5},
):
    with patch("sortpics.normalize.filesize", mock_filesize(sizes)):
        assert non_duplicate_targets(filenames, targets) == ["a.jpg", None, "b.jpg"]
