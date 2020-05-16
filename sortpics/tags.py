"""Identify the part of the name of a file that is not just an id."""

import re

DATE_AND_TAG = re.compile(r"([0-9\-\. _]*)\s*(.*)")
NUMBERED_FILE = re.compile(r"(DSC|IMG|MOV|VID|)(0|_)[0-9_-]*\s*(.*)")


def parse_tags(name):
    """Return the part of the file name that is not just an id."""
    name = name.rstrip()
    match = DATE_AND_TAG.match(name)
    if match:
        name = match.groups()[1]

    match = NUMBERED_FILE.match(name)
    if match:
        name = match.groups()[2]

    return name
