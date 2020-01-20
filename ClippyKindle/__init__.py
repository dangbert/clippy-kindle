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
        print("\nParsing file: {}\n".format(fname))

        allBooks = {} # dict mapping book title/author string to a Book object
        lineNum = 0
        with open(fname, 'r') as fh:
            allLines = fh.readlines()
            section = []
            lineNum = 0
            for line in allLines:
                lineNum += 1
                line = line.rstrip("\n")
                # TODO: remove weird character from some lines...
                if line == "==========":
                    self.parseSection(section, allBooks)
                    section = []
                else:
                    # intentially includes empty lines as well (e.g. "") because some notes can intentionally contain an empty line
                    section.append(line)
                #if lineNum >= 100: # TODO: for now
                #    break

            if len(section) != 0:
                print("\n\nERROR: Unable to finsh parsing before hitting end of file")
                print("  lines not parsed:")
                for line in section:
                    print("  '{}'".format(line))


    def parseSection(self, section, allBooks):
        """
        Parse lines belonging to a section of the clippings file that pertains to a single Highlight/Note/Bookmark object

        Parameters:
            section (:type: list of str): lines in clippings file containing all the information about one particular highlight, note, or bookmark
            allBooks (dict): dict mapping each book's title/author string (e.g. "Fahrenheit 451: A Novel (Bradbury, Ray)") to a Book object

        return: (DataStructures.Book) object or None (if error) (TODO correct this)
        """

        # retreive just the lines in section that aren't empty
        contentLines = []
        for line in section:
            if line != "":
                contentLines.append(line)

        if not len(contentLines) >= 2:
            print("\n\nERROR: found section with an unexpected number of lines:)")
            print(">>>section:")
            for line in section:
                print("  '{}'".format(line))
            print("<<<")
            return

        # create book object in allBooks if not already existing for this book
        bookId = contentLines[0]
        if bookId not in allBooks:
            # parse title into title / author
            title, author = bookId, None
            if bookId.endswith(')') and bookId.count(' (') >= 1:
                title = bookId[0 : bookId.rfind('(')-1].strip()
                author = bookId[bookId.rfind(" (")+2 : bookId.rfind(")")].strip()
            print("***** found: '{}' by '{}' *****".format(title, author))
            allBooks[bookId] = DataStructures.Book(title, author)

        if contentLines[1].startswith(HIGHLIGHT_START) and len(contentLines) == 3:
            #print("\t***IDENTIFIED: HIGHLIGHT***")
            pass
            #highlight = self._parseHighlight(fh)
        elif contentLines[1].startswith(BOOKMARK_START) and len(contentLines) == 2:
            #print("\t***IDENTIFIED: BOOKMARK***")
            pass
        elif contentLines[1].startswith(NOTE_START) and len(contentLines) >= 3:
            # TODO: keep in mind that for notes, when a note is modified the earlier enty in "My Clippings.txt" is not deleted
            #     e.g. search for "my budget app" in the txt file
            #print("\t***IDENTIFIED: NOTE***")
            pass
        else:
            print("ERROR") # TODO:


    # TODO: consider instead passing this a copy of the lines in the files belonging to this highlight
    def _parseHighlight(self, fh):
        """
        Parse lines in file at current location until done advancing through the current highlight
        Advances fh to the line immediately past this highlight

        return: (DataStructures.Book) object or None (if error)
        """

        print("\n\nparsing highlight")

        # 
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
