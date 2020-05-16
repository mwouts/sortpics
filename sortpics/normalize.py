"""Normalize file names using their creation date"""

import os
from itertools import groupby
from datetime import timedelta
from tqdm import tqdm
from .timestamp import creation_date
from .tags import parse_tags


def normalize_filename(filename, date, millisecond=False):
    """Normalized name for one file"""
    name, ext = os.path.splitext(os.path.basename(filename))
    tags = parse_tags(name)

    if 0 == date.hour == date.minute == date.second == date.microsecond:
        formatted_date = date.strftime("%Y-%m-%d")
        if name.startswith(formatted_date):
            return name + ext
        return " ".join((formatted_date, name)) + ext

    if millisecond:
        formatted_date = date.strftime("%Y-%m-%d %H.%M.%S.%f")[:-3]
    else:
        formatted_date = date.strftime("%Y-%m-%d %H.%M.%S")

    if tags:
        return " ".join((formatted_date, tags)) + ext
    return formatted_date + ext


def normalize_filenames(filenames, folder=""):
    """
    Return normalized filenames in the form YYYY-MM-DD h.m.s[.ms] [tag].ext

    :param filenames: an enumerable with file names
    :return: a list with the target file names (may contain duplicates).
    """

    filenames = list(filenames)
    progress_bar = tqdm(filenames)
    datetimes = []
    for filename in progress_bar:
        progress_bar.set_postfix_str(filename)
        datetimes.append(creation_date(os.path.join(folder, filename)))

    # Use same datetimes for animated images
    for i, filename in enumerate(filenames):
        if not filename.endswith((".MOV", ".mov")):
            continue

        name, ext = os.path.splitext(filename)
        jpg_ext = ".JPG" if ext == ".MOV" else ".jpg"
        try:
            j = filenames.index(name + jpg_ext)
        except ValueError:
            continue

        dt_jpg = datetimes[j]
        dt_mov = datetimes[i]
        if dt_jpg is None or dt_mov is None:
            continue

        timeshift = (dt_jpg - dt_mov) / timedelta(hours=1)
        if abs(timeshift) > 14:
            continue
        datetimes[i] = dt_jpg

    # Show the millisecond resolution only if necessary
    same_second_datetimes = {}
    for datetime in datetimes:
        if datetime is None:
            continue
        time_sec = datetime.replace(microsecond=0)
        same_second_datetimes.setdefault(time_sec, set()).add(datetime)

    targets = []
    for filename, datetime in zip(filenames, datetimes):
        if datetime is None:
            targets.append(None)
            continue

        time_sec = datetime.replace(microsecond=0)
        millisecond = len(same_second_datetimes[time_sec]) > 1
        targets.append(normalize_filename(filename, datetime, millisecond))

    return non_duplicate_targets(filenames, targets, folder)


def filesize(filename):
    """The size of the file on disk"""
    return os.stat(filename).st_size


def non_duplicate_targets(filenames, targets, folder=""):
    """When a duplicated target is identified, the corresponding targets are replaced by None, except for the largest
    file in the group."""

    reverse_mapping = sorted(
        (target, filename)
        for target, filename in zip(targets, filenames)
        if target is not None
    )
    largest_source_per_target = {}

    for target, group in groupby(reverse_mapping, lambda pair: pair[0]):
        filename_list = [filename for _, filename in group]
        if len(filename_list) <= 1:
            continue

        sizes = [
            (filesize(os.path.join(folder, filename)), filename)
            for filename in filename_list
        ]
        largest_source_per_target[target] = sorted(sizes)[-1][1]

    return [
        target if filename == largest_source_per_target.get(target, filename) else None
        for (filename, target) in zip(filenames, targets)
    ]
