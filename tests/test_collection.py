import pytest
from unittest.mock import patch
from sortpics.normalize import normalize_filenames
from datetime import datetime


def mock_creation_date(timestamps):
    def creation_date(file):
        return timestamps[file]

    return creation_date


def test_animated_photos_are_moved_in_pair(
    timestamps={
        "IMG_2505.JPG": datetime(2020, 3, 1, 17, 25, 12, 567000),
        "IMG_2505.MOV": datetime(2020, 3, 1, 15, 25, 14),
    }
):
    with patch("sortpics.normalize.creation_date", mock_creation_date(timestamps)):
        assert normalize_filenames(timestamps.keys()) == [
            "2020-03-01 17.25.12.JPG",
            "2020-03-01 17.25.12.MOV",
        ]


def test_same_name_files_with_different_timestamps_are_not_animated_photos(
    timestamps={
        "IMG_2505.JPG": datetime(2020, 3, 1, 17, 25, 12, 567000),
        "IMG_2505.MOV": datetime(2020, 3, 4, 15, 25, 14),
    }
):
    with patch("sortpics.normalize.creation_date", mock_creation_date(timestamps)):
        assert normalize_filenames(timestamps.keys()) == [
            "2020-03-01 17.25.12.JPG",
            "2020-03-04 15.25.14.MOV",
        ]


def test_same_second_photos_get_ms_resolution(
    timestamps={
        "IMG_2505.JPG": datetime(2020, 3, 1, 17, 25, 12, 567000),
        "IMG_2506.JPG": datetime(2020, 3, 1, 17, 25, 12, 667000),
    }
):
    with patch("sortpics.normalize.creation_date", mock_creation_date(timestamps)):
        assert normalize_filenames(timestamps.keys()) == [
            "2020-03-01 17.25.12.567.JPG",
            "2020-03-01 17.25.12.667.JPG",
        ]


@pytest.mark.parametrize(
    "timestamps,target",
    [
        ({"DSC_2505.JPG": datetime(2020, 3, 1, 17, 25, 12)}, "2020-03-01 17.25.12.JPG"),
        ({"IMG_2506.JPG": datetime(2020, 3, 1, 17, 25, 13)}, "2020-03-01 17.25.13.JPG"),
        (
            {"2017/received_10154584629387791.jpeg": datetime(2020, 3, 1, 17, 25, 14)},
            "2020-03-01 17.25.14 received_10154584629387791.jpeg",
        ),
        (
            {"2020/04/01/long_name.jpg": datetime(2020, 4, 1)},
            "2020-04-01 long_name.jpg",
        ),
        (
            {"2020-04-01 long_name.jpg": datetime(2020, 4, 1)},
            "2020-04-01 long_name.jpg",
        ),
        ({"IMG_9226.MOV": datetime(2020, 4, 1)}, "2020-04-01 IMG_9226.MOV"),
        (
            {"VID_20150103_141719.3gp": datetime(2015, 1, 3, 14, 17, 19)},
            "2015-01-03 14.17.19.3gp",
        ),
    ],
)
def test_normalize_with_tags_or_just_date(timestamps, target):
    with patch("sortpics.normalize.creation_date", mock_creation_date(timestamps)):
        assert normalize_filenames(timestamps.keys()) == [target]
