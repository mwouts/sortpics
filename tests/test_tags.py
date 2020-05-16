from datetime import datetime
from sortpics.tags import parse_tags
from sortpics.normalize import normalize_filename


def test_parse_tags():
    assert parse_tags("Cute cat") == "Cute cat"
    assert parse_tags("2011-12-15 14.49.56 Cute cat") == "Cute cat"
    assert parse_tags("IMG_2505 Cute cat") == "Cute cat"
    assert parse_tags("DSC05991") == ""
    assert parse_tags("IMG_0166-EFFECTS") == "EFFECTS"


def test_keep_tag(
    path="2011/12/25/Cute cat.jpg",
    exif_date=datetime.fromisoformat("2011-12-15 14:49:56"),
    target_name="2011-12-15 14.49.56 Cute cat.jpg",
):
    assert normalize_filename(path, exif_date) == target_name


def test_keep_tag_after_date(
    path="2011/12/25/2011-12-15 14.49.56 Cute cat.jpg",
    exif_date=datetime.fromisoformat("2011-12-15 14:49:56"),
    target_name="2011-12-15 14.49.56 Cute cat.jpg",
):
    assert normalize_filename(path, exif_date) == target_name


def test_keep_tag_after_image_name(
    path="2011/12/25/IMG_2505 Cute cat.jpg",
    exif_date=datetime.fromisoformat("2011-12-15 14:49:56"),
    target_name="2011-12-15 14.49.56 Cute cat.jpg",
):
    assert normalize_filename(path, exif_date) == target_name
