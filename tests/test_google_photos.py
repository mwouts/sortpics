"""Test sortpics on a Google Photo collection extracted with Takeout (https://takeout.google.com)"""
from sortpics.normalize import normalize_filename
from sortpics.timestamp import fromisoformat


def test_matching_name_date(
    path="2011-12-25/2011-12-15 14.49.56.jpg",
    exif_date=fromisoformat("2011-12-15 14:49:56"),
    target_name="2011-12-15 14.49.56.jpg",
):
    assert normalize_filename(path, exif_date) == target_name


def test_exif_date_overrides_name(
    path="2011-12-25/2011-12-15 14.49.56.jpg",
    exif_date=fromisoformat("2011-12-15 14:49:57"),
    target_name="2011-12-15 14.49.57.jpg",
):
    assert normalize_filename(path, exif_date) == target_name
