import os
import sys
import parse

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
                    res = self.parseSection(section, allBooks)
                    if res != None:
                        print(res)
                        print("problem section in file (lines {} - {}) >>>".format(lineNum - len(section), lineNum))
                        for line in section:
                            print("  '{}'".format(line))
                        print("<<<\n")
                    section = []
                else:
                    # intentially includes empty lines as well (e.g. "") because some notes can intentionally contain an empty line
                    section.append(line)
                #if lineNum >= 101: # TODO: for now
                #    break

            if len(section) != 0:
                print("\n\nERROR: Unable to finsh parsing before hitting end of file")
                print("section not parsed (at line {}) >>>".format(lineNum))
                for line in section:
                    print("  '{}'".format(line))
                print("<<<")

        print("\n\nFinished parsing data from {} books!".format(len(allBooks)))
        for bookId in allBooks: # TODO: for now (later just export to json and print some statistics...)
            print()
            print(allBooks[bookId])

    def parseSection(self, section, allBooks):
        """
        Parse lines belonging to a section of the clippings file that pertains to a single Highlight/Note/Bookmark object

        Parameters:
            section (:type: list of str): lines in clippings file containing all the information about one particular highlight, note, or bookmark
            allBooks (dict): dict mapping each book's title/author string (e.g. "Fahrenheit 451: A Novel (Bradbury, Ray)") to a Book object

        return: None if successful else returns str explaining error
        """

        # retreive just the lines in section that aren't empty
        contentLines = []
        for line in section:
            if line != "":
                contentLines.append(line)

        if not len(contentLines) >= 2:
            return "ERROR: found section with an unexpected number of lines"

        # create book object in allBooks if not already existing for this book
        bookId = contentLines[0]
        if bookId not in allBooks:
            # parse title into title / author
            title, author = bookId, None
            if bookId.endswith(')') and bookId.count(' (') >= 1:
                title = bookId[0 : bookId.rfind('(')-1].strip()
                author = bookId[bookId.rfind(" (")+2 : bookId.rfind(")")].strip()
            #print("***** found: '{}' by '{}' *****".format(title, author))
            allBooks[bookId] = DataStructures.Book(title, author)

        # parse.parse https://stackoverflow.com/a/18620969
        if contentLines[1].startswith(HIGHLIGHT_START) and len(contentLines) == 3:
            # parse highlight:
            #   example format:
            """
            Sinsajo (Suzanne Collins)
            - Your Highlight on Location 4749-4749 | Added on Saturday, January 4, 2020 10:20:02 AM
            me pongo en cuclillas
            """
            #print("\t***IDENTIFIED: HIGHLIGHT***")
            #print(">>>section:")
            #for line in contentLines:
            #    print("  '{}'".format(line))
            #print("<<<")

            res = parse.parse("- Your Highlight on {} {}-{} | Added on {}", contentLines[1])
            if res == None:
                # try again for rare case like "- Your Highlight on page 7 | Added on Sunday, May 6, 2018 1:42:40 AM"
                res = parse.parse("- Your Highlight on {} {} | Added on {}", contentLines[1])
                if res == None:
                    return "ERROR: parse.parse failed on highlight"
                res = [res[0], res[1], res[1], res[2]] # use page/loc number twice to match other format
            try:
                date = parser.parse(res[3])
            except ValueError:
                return "ERROR: unable to parse date '{}' in highlight".format(res[3])
            highlight = DataStructures.Highlight((res[1], res[2]), res[0].lower(), date, contentLines[2])
            #print("created: " + str(highlight))
            allBooks[bookId].highlights.append(highlight)
            #allBooks[bookId].highlights.append(DataStructures.Highlight((res[1], res[2]), res[0].lower(), date, contentLines[2]))

        elif contentLines[1].startswith(BOOKMARK_START) and len(contentLines) == 2:
            # parse bookmark:
            #   example format:
            """
            Do Androids Dream of Electric Sheep? (Dick, Philip K.)
            - Your Bookmark on Location 604 | Added on Friday, November 25, 2016 12:13:59 AM
            """
            print("\t***IDENTIFIED: BOOKMARK***")
            print(">>>section:")
            for line in contentLines:
                print("  '{}'".format(line))
            print("<<<")

            res = parse.parse("- Your Bookmark on {} {} | Added on {}", contentLines[1])
            if res == None:
                return "ERROR: parse.parse failed in bookmark"
            try:
                date = parser.parse(res[2])
            except ValueError:
                return "ERROR: unable to parse date '{}' in bookmark".format(res[3])

            bookmark = DataStructures.Bookmark(res[1], res[0].lower(), date)
            allBooks[bookId].bookmarks.append(bookmark)
        elif contentLines[1].startswith(NOTE_START) and len(contentLines) >= 3:
            # TODO: keep in mind that for notes, when a note is modified the earlier enty in "My Clippings.txt" is not deleted
            #     e.g. search for "my budget app" in the txt file
            #print("\t***IDENTIFIED: NOTE***")
            pass
        else:
            return "ERROR: not sure how to parse section"


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
