"""
test_network1.py
~~~~~~~~~~~~~~~~

unit test mynet.py against network.py (the provided implementation)
"""

import os
import sys
from datetime import datetime

# enable imports from parent folder of this script:
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))  # folder containing this file
sys.path.append(os.path.dirname(FOLDER_PATH))

from tests.conftest import helperCompare
from ClippyKindle import ClippyKindle, _parseAnyDate


def test_dans_clippings():
    """
    test successful parsing of file format in https://github.com/dangbert/clippy-kindle/issues/1
    """
    helperCompare("dans--My.Clippings")


def test_issue1_format():
    """
    test successful parsing of file format in https://github.com/dangbert/clippy-kindle/issues/1
    """
    helperCompare("issue1--My.Clippings")


def test_pt():
    """
    test parsing of Portuguese language Kindle.
    """

    helperCompare("pt--My.Clippings")


def test_parse_any_date():
    date = _parseAnyDate("Friday, November 25, 2016 12:13:59 AM")
    assert date is not None

    date = _parseAnyDate("sábado, 19 de dezembro de 2001 23:36:53")
    assert date == datetime(2001, 12, 19, 23, 36, 53)
