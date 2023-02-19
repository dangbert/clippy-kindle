#!/usr/bin/env python3
from setuptools import find_packages, setup

# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
setup(
    name="clippy-kindle",
    # packages=find_packages(),
    packages=[],
    version="1.2.0",
    description="Create Anki flashcards and markdown files from your Kindle notes/highlights.",
    author="dangbert",
    license="MIT",
    url="https://github.com/dangbert/clippy-kindle",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.2.1"],
    },
    # entry_points={"console_scripts": ["marky.py=clippyk.marky.main"]},
    entry_points={
        # TODO: these don't work yet when run later from CLI
        "console_scripts": [
            # TODO: should scripts be in root dir or in ClippyKindle/ ?
            # "clippy.py=ClippyKindle.clippy:main",
            "clippy.py=clippy:main",
            # "marky.py=marky:main",
            # "ankiImport.py=ankiImport:main",
        ]
    },
)
