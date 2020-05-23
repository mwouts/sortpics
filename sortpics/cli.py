"""Command line interface for sortpics"""

import os
import shlex
import shutil
import argparse
import logging
from datetime import datetime
from .normalize import normalize_filenames

LOGGER = logging.getLogger(__name__)

try:
    shlex.join([])
except AttributeError:
    shlex.join = lambda args: " ".join(shlex.quote(arg) for arg in args)


def _parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Normalize the picture names and hierarchy"
    )

    parser.add_argument(
        "--folder", help="Folder to normalize (default: current folder)", default="."
    )
    parser.add_argument(
        "--subfolder",
        help="Move the pictures to a date/month subfolder",
        default="%Y-%m",
    )
    parser.add_argument(
        "--no-test",
        dest="test",
        action="store_false",
        help="Proceed with the proposed renaming",
    )
    parser.add_argument(
        "--no-scripts",
        dest="scripts",
        action="store_false",
        help="Do not generate rename and undo scripts",
    )
    parser.set_defaults(test=True, scripts=True)

    return parser.parse_args(args)


def sortpics_cli(args=None):
    """sortpics at the command line"""
    args = _parse_args(args)
    sortpics(**vars(args))


def move(folder, filenames, targets, test=True):
    """A function that moves the given filenames to their targets"""
    undo = [shlex.join(["cd", folder])]
    script = [shlex.join(["cd", folder])]

    mkdirs = set()

    for filename, target in sorted(zip(filenames, targets)):
        if target is None:
            continue

        if os.path.exists(target):
            if os.path.samefile(filename, target):
                continue

            LOGGER.warning("# Target exists: %s", shlex.join(["mv", filename, target]))
            continue

        new_dir = os.path.dirname(target)
        if new_dir and new_dir not in mkdirs:
            script.append(shlex.join(["mkdir", "-p", new_dir]))
            mkdirs.add(new_dir)

        cmd = shlex.join(["mv", filename, target])
        script.append(cmd)
        print(cmd)

        undo.append(shlex.join(["mv", target, filename]))

        if not test:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.move(filename, target)

    return script, undo


def sortpics(folder=".", test=True, scripts=True, subfolder="%Y-%m"):
    """The function that is called by sortpics command line"""
    filenames = []
    for root, dirs, files in os.walk(folder):
        files = [f for f in files if not f[0] == "."]
        dirs[:] = [d for d in dirs if not d[0] == "."]
        relative_root = os.path.relpath(root, folder)
        filenames.extend(os.path.join(relative_root, filename) for filename in files)

    targets = normalize_filenames(filenames, folder)

    # Add year-month parent folder
    if subfolder:
        targets_with_subfolder = []
        for target in targets:
            if target is None:
                targets_with_subfolder.append(None)
            else:
                date = datetime.strptime(target[:10], "%Y-%m-%d")
                targets_with_subfolder.append(
                    os.path.join(date.strftime(subfolder), target)
                )
        targets = targets_with_subfolder

    script, undo = move(folder, filenames, targets, test=test)

    if scripts:
        now = datetime.now().isoformat()
        undo = [
            "#!/bin/bash",
            f"# This script reverses the renaming {'proposed' if test else 'done'} by sortpics at {now}",
        ] + undo
        undo_script_name = (
            f'.sortpics_undo_{"test_" if test else ""}{now.replace(":", ".")}.sh'
        )
        with open(os.path.join(folder, undo_script_name), "w") as stream:
            stream.write("\n".join(undo) + "\n")

        script = [
            "#!/bin/bash",
            f"# This script does the renaming {'proposed' if test else 'done'} by sortpics at {now}",
        ] + script
        script_name = f'.sortpics_{"test_" if test else ""}{now.replace(":", ".")}.sh'
        with open(os.path.join(folder, script_name), "w") as stream:
            stream.write("\n".join(script) + "\n")

        if test:
            print(
                f"# Rerun with --no-test to rename the files, or execute 'bash {script_name}'"
            )
        print(f"# Undo the renaming with 'bash {undo_script_name}'")

    elif test:
        print("# Rerun with --no-test to rename the files")

    print(
        "# When you're done, clean up empty directories with 'find . -type d -empty -delete'"
    )
