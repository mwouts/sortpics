from os import path
from io import open
import re
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(this_directory, "sortpics/version.py")) as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    version = version_match.group(1)

setup(
    name="sortpics",
    version=version,
    author="Marc Wouts",
    author_email="marc.wouts@gmail.com",
    description="Pictures from Google Photos, ICloud, or your Camera... all sorted!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mwouts/sortpics",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["sortpics = sortpics.cli:sortpics_cli"]},
    tests_require=["pytest"],
    install_requires=["pillow", "hachoir", "tqdm"],
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
