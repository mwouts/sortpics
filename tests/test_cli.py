import os
import shlex
from unittest.mock import patch
from datetime import datetime
from sortpics.cli import sortpics_cli


def test_sortpics_cli(
    tmpdir,
    capsys,
    files=[
        # Simple photo
        (
            "2020-05-23/IMG_1554.JPG",
            datetime(2020, 5, 23, 16, 55, 13, 123456),
            "2020-05/2020-05-23 16.55.13.JPG",
        ),
        # Animated photo
        (
            "2020-05-23/IMG_1555.JPG",
            datetime(2020, 5, 23, 16, 55, 43, 123456),
            "2020-05/2020-05-23 16.55.43.JPG",
        ),
        (
            "2020-05-23/IMG_1555.MOV",
            datetime(2020, 5, 23, 16, 55, 44),
            "2020-05/2020-05-23 16.55.43.MOV",
        ),
        # Custom image name
        (
            "2020-05-23/Custom name.jpg",
            datetime(2020, 5, 23, 17, 55, 43, 123456),
            "2020-05/2020-05-23 17.55.43 Custom name.jpg",
        ),
        # Same-second images
        (
            "2020/05/23/IMG_1556.JPG",
            datetime(2020, 5, 23, 18, 55, 13, 123000),
            "2020-05/2020-05-23 18.55.13.123.JPG",
        ),
        (
            "2020/05/23/IMG_1557.JPG",
            datetime(2020, 5, 23, 18, 55, 13, 251000),
            "2020-05/2020-05-23 18.55.13.251.JPG",
        ),
    ],
):

    # Create the sample files
    for filename, _, _ in files:
        dirname, basename = os.path.split(filename)
        os.makedirs(tmpdir.join(dirname), exist_ok=True)
        tmpdir.join(dirname).join(basename).write("\n")

    # Patch the timestamp function
    def creation_date(filename):
        for sample_file, timestamp, _ in files:
            if os.path.basename(filename) == os.path.basename(sample_file):
                return timestamp
        raise ValueError(f"{filename} was not found")

    with patch("sortpics.normalize.creation_date", creation_date):
        sortpics_cli(["--folder", str(tmpdir)])

    out, _ = capsys.readouterr()
    print("\n" + out)

    for filename, _, target in files:
        assert shlex.join(["mv", filename, target]) in out
