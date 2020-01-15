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

        allBooks = {} # dict mapping book title/author string to a Book object
        lineNum = 0
        with open(fname, 'r') as fh:
            while True:
                line = fh.readline().rstrip("\n")
                # TODO: remove weird character from some lines...
                lineNum += 1
                if line == "":
                    continue

                print("line #{}: '{}'".format(lineNum, line))
                bookId = line   # contains title and sometimes the author e.g. "The Iliad (Penguin Classics) (Homer)"
                if bookId not in allBooks:
                    # parse title into title / author
                    title, author = bookId, None
                    if bookId.endswith(')') and bookId.count(' (') >= 1:
                        title = bookId[0 : bookId.rfind('(')-1].strip()
                        author = bookId[bookId.rfind(" (")+2 : bookId.rfind(")")].strip()
                    print("***** found: '{}' by '{}' *****".format(title, author))
                    allBooks[bookId] = DataStructures.Book(title, author)

                peek = self._peekLine(fh, 1)
                #print("\t peek='{}'".format(peek))
                if peek.startswith(HIGHLIGHT_START):
                    print("\t***IDENTIFIED: HIGHLIGHT")
                    highlight = self._parseHighlight(fh)
                    #allBooks[bookId] = 

                elif peek.startswith(BOOKMARK_START):
                    print("\t***IDENTIFIED: BOOKMARK")
                elif peek.startswith(NOTE_START):
                    print("\t***IDENTIFIED: NOTE")



                if lineNum >=15:
                    break

    # TODO: consider instead passing this a copy of the lines in the files belonging to this highlight
    def _parseHighlight(self, fh):
        """
        Parse lines in file at current location until done advancing through the current highlight
        Advances fh to the line immediately past this highlight

        return: (DataStructures.Book) object or None (if error)
        """
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
