#!/usr/bin/env python3
from setuptools import find_packages, setup

# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
setup(
    name="clippy-kindle",
    # packages to install:
    # packages=find_packages(),
    packages=["ClippyKindle"],
    version="1.2.0",
    description="Create Anki flashcards and markdown files from your Kindle notes/highlights.",
    author="dangbert",
    license="MIT",
    url="https://github.com/dangbert/clippy-kindle",
    install_requires=[
        "anki>=2.1.49",
        "parse>=1.19.0",
        "protobuf==3.20.*",  # a compatible version for anki package
        "prettytable>=3.6.0",
        "python-dateutil>=2.8.2",
    ],
    # TODO: add sphinx etc
    extras_require={
        "dev": [
            "black>=23.1.0",
            "pytest>=7.2.1",
            "Sphinx>=6.1.3",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clippy.py=ClippyKindle.clippy:main",
            "marky.py=ClippyKindle.marky:main",
            "ankiImport.py=ClippyKindle.ankiImport:main",
        ]
    },
)
