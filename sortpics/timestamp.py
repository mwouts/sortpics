"""Based on the exif data, generate a dated path"""

import os
import re
from datetime import datetime, timedelta
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

try:
    fromisoformat = datetime.fromisoformat
except AttributeError:

    def fromisoformat(string):
        """An alternative to datetime.fromisoformat in Python < 3.7"""
        string = string.replace("T", " ")
        if "." in string:
            return datetime.strptime(string, "%Y-%m-%d %H:%M:%S.%f")
        return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


DATE = re.compile(r"(.*)([0-9]{4})[-/]?([0-9]{2})[-/]?([0-9]{2})(.*)")
DATETIME = re.compile(
    r"(.*)([0-9]{4})-?([0-9]{2})-?([0-9]{2})[ _]?-?([0-9]{2})[\.-]?([0-9]{2})[\.-]?([0-9]{2})(.*)"
)
JPEG_EXTENSIONS = (".jpg", ".jpeg", ".JPG", ".JPEG")


def _find_date(string):
    match = DATE.match(string)
    if not match:
        raise ValueError(f"Cannot find a date in {string}")

    _, year, month, day, _ = match.groups()
    return datetime(int(year), int(month), int(day))


def _find_datetime(string):
    match = DATETIME.match(string)
    if not match:
        raise ValueError(f"Cannot find a datetime in {string}")

    _, year, month, day, hour, minute, second, _ = match.groups()
    return datetime(
        int(year), int(month), int(day), int(hour), int(minute), int(second)
    )


def creation_date_from_path(filename):
    """The creation time from the file name or parent folder"""
    try:
        return _find_datetime(os.path.basename(filename))
    except ValueError:
        pass

    try:
        return _find_date(os.path.basename(filename)[:10])
    except ValueError:
        pass

    try:
        return _find_date(os.path.basename(filename))
    except ValueError:
        pass

    try:
        return _find_date(os.path.dirname(filename))
    except ValueError:
        pass

    raise ValueError(f"No date found in path for {filename}")


def creation_date_from_exif(filename):
    """The creation date from the exif data"""
    # Source: https://orthallelous.wordpress.com/2015/04/19/extracting-date-and-time-from-images-with-python/
    with Image.open(filename) as img:
        exif = img.getexif()

    if exif is None:
        raise ValueError(f"No exif data for {filename}")

    # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
    tags = [
        (36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
        (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
        (306, 37520),  # (DateTime, SubsecTime)
    ]

    for tag in tags:
        dat = exif.get(tag[0])
        sub = exif.get(tag[1], 0)

        # PIL.PILLOW_VERSION >= 3.0 returns a tuple
        dat = dat[0] if isinstance(dat, tuple) else dat
        if not dat:
            continue

        sub = sub[0] if isinstance(sub, tuple) else sub
        if isinstance(sub, int):
            sub = f"{sub:06d}"

        date, time = dat.split(" ")
        date = date.replace(":", "-")
        return fromisoformat(f"{date}T{time}.{sub}")

    raise ValueError(f"No date found in the exif data for {filename}")


def creation_date_from_hachoir(filename):
    """The creation date from the file metadata"""
    parser = createParser(filename)
    metadata = extractMetadata(parser)
    if metadata is None:
        raise ValueError(f"Hachoir found no metadata for {filename}")
    return metadata.get("creation_date")


def creation_date(filename):
    """Our best guess for the creation date of the file"""
    try:
        if filename.endswith(JPEG_EXTENSIONS):
            timestamp = creation_date_from_exif(filename)
        else:
            timestamp = creation_date_from_hachoir(filename)
    except ValueError:
        timestamp = None

    try:
        path_date = creation_date_from_path(filename)
    except ValueError:
        return timestamp

    if not timestamp:
        return path_date

    # Preserve path timestamp if incompatible with image timestamp
    if timestamp < path_date - timedelta(days=2):
        return path_date
    if timestamp > path_date + timedelta(days=1):
        return path_date

    return timestamp
