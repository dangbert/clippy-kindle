import os
import sys

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz

from ClippyKindle import DataStructures

HIGHLIGHT_START = "- Your Highlight on"
BOOKMARK_START = "- Your Bookmark on"
NOTE_START = "- Your Note on"

class ClippyKindle:

    def parse(self, fname):
        print("parsing file: {}".format(fname))
        print("in parse")

        lineNum = -1
        with open(fname, 'r') as fh:
            while True:
                line = fh.readline().rstrip("\n")
                lineNum += 1
                #if line == "":
                #    continue

                print("line #{}: '{}'".format(lineNum, line))
                peek = self._peekLine(fh, 1)
                #print("\t peek='{}'".format(peek))

                title = line
                if peek.startswith(HIGHLIGHT_START):
                    print("\t***IDENTIFIED: HIGHLIGHT")
                elif peek.startswith(BOOKMARK_START):
                    print("\t***IDENTIFIED: BOOKMARK")
                elif peek.startswith(NOTE_START):
                    print("\t***IDENTIFIED: NOTE")



                if lineNum >=15:
                    break

    def _parseHighlight(self):
        pass

    # https://stackoverflow.com/a/16840747
    # TODO: check behaviour if we reach end of file
    # (note that any changes made to the file handler here persist after the function is called)
    def _peekLine(self, f, lineOffset=1):
        """
        get the value lineOffset lines ahead (without advancing the file f)

        """
        if lineOffset <= 0:
            return None
        pos = f.tell()
        for i in range(lineOffset):
            line = f.readline()
            if not line:
                line = None
                break
        f.seek(pos)
        return line.rstrip("\n")
