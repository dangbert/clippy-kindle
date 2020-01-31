import os
import sys
import parse
import json

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
        """
        parses the notes/highlights/bookmarks stored in a kindle clippings txt file (printing any errors)
        and returns the data as an array of dicts outputs the data to a json file

        parameters:
            fname (str): file path to txt file to parse (e.g. "My Clippings.txt")
        return:
            (:type listOfObjects: list<dict>) where each dict stores the data for a single book
        """
        print("\nParsing file: {}".format(fname))

        allBooks = {} # dict mapping book title/author string to a Book object
        lineNum = 0
        with open(fname, 'r') as fh:
            allLines = fh.readlines()
            section = []
            lineNum = 0
            for line in allLines:
                lineNum += 1
                line = line.rstrip("\n")
                # TODO: remove weird character from some lines!!!
                if line == "==========":
                    res = self._parseSection(section, allBooks)
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

            if len(section) != 0:
                print("\n\nERROR: Unable to finsh parsing before hitting end of file")
                print("section not parsed (at line {}) >>>".format(lineNum))
                for line in section:
                    print("  '{}'".format(line))
                print("<<<")
        print("\nFinished parsing data from {} books!".format(len(allBooks)))

        outData = []
        for bookId in allBooks:
            allBooks[bookId].sort() # do post-processing on book (sorting/removing duplicates)
            outData.append(allBooks[bookId].toDict())
        return outData


    def _parseSection(self, section, allBooks):
        """
        Parses lines belonging to a section of the clippings file that pertains to a single Highlight/Note/Bookmark object
        Creates a Highlight, Note, or Bookmark object as needed and stores it in allBooks under its relevant book

        Parameters:
            section (:type: list of str): array of lines from a clippings file containing all the information pertaining to one particular highlight, note, or bookmark
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
            #print("\n\t***IDENTIFIED: HIGHLIGHT***")
            #print("section: >>>")
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
                highlight = DataStructures.Highlight((int(res[1]), int(res[2])), res[0].lower(), date, contentLines[2])
                #print("created: " + str(highlight))
                allBooks[bookId].highlights.append(highlight)
            except ValueError:                  # due to date parsing or casting page/loc as an int
                return "ERROR: unable to parse date or page/location in highlight"

        elif contentLines[1].startswith(BOOKMARK_START) and len(contentLines) == 2:
            # parse bookmark:
            #   example format:
            """
            Do Androids Dream of Electric Sheep? (Dick, Philip K.)
            - Your Bookmark on Location 604 | Added on Friday, November 25, 2016 12:13:59 AM
            """
            #print("\n\t***IDENTIFIED: BOOKMARK***")
            #print("section: >>>")
            #for line in contentLines:
            #    print("  '{}'".format(line))
            #print("<<<")

            res = parse.parse("- Your Bookmark on {} {} | Added on {}", contentLines[1])
            if res == None:
                return "ERROR: parse.parse failed in bookmark"
            try:
                date = parser.parse(res[2])
                bookmark = DataStructures.Bookmark(int(res[1]), res[0].lower(), date)
                #print("created: " + str(bookmark))
                allBooks[bookId].bookmarks.append(bookmark)
            except ValueError:
                return "ERROR: unable to parse date or page/location in bookmark"

        elif contentLines[1].startswith(NOTE_START) and len(contentLines) >= 3:
            # parse note:
            #   example format:
            """
            Theogony  
            - Your Note on page 1 | Added on Monday, September 11, 2017 10:56:38 PM

            HW: Due Tues
            Choose 3 elements or themes of the poem that you think are the most important, the most centeral to understanding what is going on in the poem.

            Explain why you chose each element/theme.
            Cite specific lines from the text to illustrate where you saw the elements/themes.
            ==========
            """
            #print("\n\t***IDENTIFIED: NOTE***")
            #print("section: >>>")
            #for line in section:
            #    print("  '{}'".format(line))
            #print("<<<")

            res = parse.parse("- Your Note on {} {} | Added on {}", contentLines[1])
            if res == None:
                return "ERROR: parse.parse failed in note"
            try:
                date = parser.parse(res[2])
                content = section[2:] # get just the content lines of the note
                # remove first and trailing empty lines if they exist (notes are always preceeded by an empty line)
                content = content[1:] if content[0] == "" and len(content) > 1 else content
                while len(content) > 1 and content[-1] == "":
                    content = content[:-1]

                note = DataStructures.Note(int(res[1]), res[0].lower(), date, '\n'.join(str(line) for line in content))
                #print("created: " + str(note))
                allBooks[bookId].notes.append(note)
            except ValueError:
                return "ERROR: unable to parse date or page/location in note"

        else:
            return "ERROR: not sure how to parse section"


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
