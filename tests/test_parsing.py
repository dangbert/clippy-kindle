"""
test_network1.py
~~~~~~~~~~~~~~~~

unit test mynet.py against network.py (the provided implementation)
"""

import pytest
import os
import shutil
import sys
import json

# enable imports from parent folder of this script:
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__)) # folder containing this file
sys.path.append(os.path.dirname(FOLDER_PATH))

from tests.conftest import helperCompare
from ClippyKindle import ClippyKindle

def test_dans_clippings():
    """
    test successful parsing of file format in https://github.com/dangbert/clippy-kindle/issues/1
    """
    helperCompare('dans--My.Clippings')

def test_issue1_format():
    """
    test successful parsing of file format in https://github.com/dangbert/clippy-kindle/issues/1
    """
    helperCompare('issue1--My.Clippings')
