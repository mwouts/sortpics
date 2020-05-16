from datetime import datetime
from sortpics.timestamp import creation_date_from_path, fromisoformat


def test_fromisoformat():
    assert fromisoformat("2017-11-15T14:25:59.000567") == datetime(
        2017, 11, 15, 14, 25, 59, 567
    )


def test_creation_date_from_path():
    assert creation_date_from_path("2018/02/01/Photo 1.JPG") == datetime(2018, 2, 1)
    assert creation_date_from_path("2018-02-01/Photo 1.JPG") == datetime(2018, 2, 1)
    assert creation_date_from_path("2018-02-01 #2/Photo 1.JPG") == datetime(2018, 2, 1)
    assert creation_date_from_path("Folder/2018-02-01/Photo 1.JPG") == datetime(
        2018, 2, 1
    )
    assert creation_date_from_path("Folder/2018-02-01 Photo 1.JPG") == datetime(
        2018, 2, 1
    )
    assert creation_date_from_path(
        "2017-04-16 c2141219-017b-4ff9-a303-93947f697758.mp4'"
    ) == datetime(2017, 4, 16)


def test_file_date_overtakes_parent_date():
    assert creation_date_from_path(
        "Folder/2018-02-01/2017-02-01 Photo 1.JPG"
    ) == datetime(2017, 2, 1)
    assert creation_date_from_path(
        "Folder/2018-02-01/2017-02-01 18.55.15 Photo 1.JPG"
    ) == datetime(2017, 2, 1, 18, 55, 15)
