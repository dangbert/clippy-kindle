import os
import sys
import parse
import json

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime

from ClippyKindle import DataStructures

# NOTE: you can also use a config.ini to define config https://stackoverflow.com/a/38275781
HIGHLIGHT_START = "- Your Highlight"
BOOKMARK_START = "- Your Bookmark"
NOTE_START = "- Your Note"

# when we try to parse the first line of a highlight, these formats will be tried until one succeeds:
HIGHLIGHT_FORMATS = [
    "- Your Highlight {:l} {locType:l} {loc1:d}-{loc2:d} | Added on {date}",            # case like: "- Your Highlight on Location 4749-4749 | Added on Saturday, January 4, 2020 10:20:02 AM"
    "- Your Highlight {:l} {locType:l} {loc1:d} | Added on {date}",                     # case like: "- Your Highlight on page 7 | Added on Sunday, May 6, 2018 1:42:40 AM"
    "- Your Highlight {:l} {:l} {:d} | {locType:l} {loc1:d}-{loc2:d} | Added on {date}" # case like: "- Your Highlight on page 22 | location 325-325 | Added on Thursday, 15 June 2017 18:23:21"
]
BOOKMARK_FORMATS = [
    "- Your Bookmark {:l} {locType:l} {loc:d} | Added on {date}",            # case like: "- Your Bookmark on Location 604 | Added on Friday, November 25, 2016 12:13:59 AM"
    "- Your Bookmark {:l} {:l} {:d} | {locType:l} {loc:d} | Added on {date}" # case like: "- Your Bookmark on page 262 | location 3686 | Added on Friday, 23 October 2020 21:24:06"
]
NOTE_FORMATS = [
    "- Your Note {:l} {locType:l} {loc:d} | Added on {date}",                # case like: "- Your Note on page 16 | location 231 | Added on Monday, 7 December 2020 19:19:23"
    "- Your Note {:l} {:l} {:d} | {locType:l} {loc:d} | Added on {date}",    # case like: "- Your Note on page 16 | location 231 | Added on Monday, 7 December 2020 19:19:23"
]

DATE_FMT_OUT = "%B %d, %Y %H:%M:%S" # format string for outputting datetime objects
######## helper functions
def strToDate(dateStr):
    """
    converts a provided string (of desired formatting) to a dateTime object
    """
    return datetime.strptime(dateStr, DATE_FMT_OUT)

def dateToStr(dateObj):
    """
    converts a provided dateTime object to a string with desired formatting
    """
    return dateObj.strftime(DATE_FMT_OUT)
########


class ClippyKindle:
    """
    Does the work of parsing either a "My Clippings.txt" file
    or a previously exported JSON file created from a "My Clippings.txt" file.
    (using classes from ClippyKindle.DataStructures for storage)
    """

    @staticmethod
    def parseJsonFile(fname):
        """
        parses the notes/highlights/bookmarks stored in a JSON file previously created with ClippyKindle
        returns an array of Book objects

        parameters:
            fname (str): file path to json file to parse (e.g. "collection.json")
        return:
            (:type listOfObjects: DataStructures.Book) list of Book objects
        """
        bookList = []
        with open(fname) as f:
            jsonData = json.load(f)
        for bookData in jsonData:
            bookList.append(DataStructures.Book.fromDict(bookData))
        return bookList

    @staticmethod
    def parseClippings(fname, verbose=False):
        """
        parses the notes/highlights/bookmarks stored in a kindle clippings txt file (printing any errors)
        and returns the data as an array of dicts (each dict representing the data from one book).

        parameters:
            fname (str): file path to txt file to parse (e.g. "My Clippings.txt")
            # TODO: use verbose param with options 0 (print nothing), 1 (print everything), and 2 (print errors only)
        return:
            (:type listOfObjects: DataStructures.Book) list of Book objects
        """
        print("\nParsing file: '{}'".format(fname))

        def printHelper(msg, isError=False):
            """
            helper function for printing
            parameters:
                msg (str): message to print
                level (bool): True if msg is an error message, False otherwise
            """
            # TODO: implement, consider actually printing errors to stderr
            pass

        allBooks = {} # dict mapping book title/author string to a Book object
        lineNum = 0
        numErrors = 0
        with open(fname, 'r') as fh:
            allLines = fh.readlines()
            section = []
            lineNum = 0
            for line in allLines:
                lineNum += 1
                line = line.rstrip("\n")
                # TODO: remove weird character from some lines!!!
                if line == "==========":
                    res = ClippyKindle._parseSection(section, allBooks)
                    if res != None:
                        numErrors += 1
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
                numErrors += 1
                print("\n\nERROR: Unable to finsh parsing before hitting end of file")
                print("section not parsed (at line {}) >>>".format(lineNum))
                for line in section:
                    print("  '{}'".format(line))
                print("<<<")
        print("\nFinished parsing data from {} books!".format(len(allBooks)))
        if numErrors != 0 and input("{} error(s) parsing input file. Continue anyway (y/n)? "\
                .format(numErrors)).lower().strip() in ('n','no'):
            print("Aborting...")
            print("Feel free to report any issues with parsing your 'My Clippings.txt' file here: https://github.com/dangbert/clippy-kindle/issues/new")
            exit(1)

        outData = [] # list of Book objects
        for bookId in allBooks:
            outData.append(allBooks[bookId])
        return outData

    @staticmethod
    def _parseSection(section, allBooks):
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
        firstLine = contentLines[0]
        if ord(firstLine[0]) in [0xfeff, ]:
            firstLine = firstLine[1:]
#        print(f'the first character: {hex(ord(firstLine[0]))}.')
        # parse title into title / author
        title, author = firstLine, ""
        if firstLine.endswith(')') and firstLine.count(' (') >= 1:
            title = firstLine[0 : firstLine.rfind('(')-1].strip()
            author = firstLine[firstLine.rfind(" (")+2 : firstLine.rfind(")")].strip()
        
        bookId = f'{author}-{title}'
        if bookId not in allBooks:
#            print(f'*****ID: {bookId} found: {title} by {author} *****')
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
            res = None
            for formatStr in HIGHLIGHT_FORMATS:
                res = parse.parse(formatStr, contentLines[1])
                if res != None:
                    break
            if res == None:
                return "ERROR: unable to parse highlight (in unexpected/unsupported format)"

            try:
                date = parser.parse(res['date'])
                loc2 = res['loc2'] if 'loc2' in res else res['loc1'] # if loc2 not set, use loc1 in its place
                highlight = DataStructures.Highlight((res['loc1'], loc2), res['locType'].lower(), date, contentLines[2])
                allBooks[bookId].highlights.append(highlight)
            except ValueError:                  # due to date parsing or casting page/loc as an int
                return "ERROR: unable to parse date in highlight"

        elif contentLines[1].startswith(BOOKMARK_START) and len(contentLines) == 2:
            # parse bookmark:
            #   example format:
            """
            Do Androids Dream of Electric Sheep? (Dick, Philip K.)
            - Your Bookmark on Location 604 | Added on Friday, November 25, 2016 12:13:59 AM
            """
            res = None
            for formatStr in BOOKMARK_FORMATS:
                res = parse.parse(formatStr, contentLines[1])
                if res != None:
                    break
            if res == None:
                return "ERROR: unable to parse bookmark (in unexpected/unsupported format)"

            try:
                date = parser.parse(res['date'])
                bookmark = DataStructures.Bookmark(res['loc'], res['locType'].lower(), date)
                allBooks[bookId].bookmarks.append(bookmark)
            except ValueError:
                return "ERROR: unable to parse date in bookmark"

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
            res = None
            for formatStr in NOTE_FORMATS:
                res = parse.parse(formatStr, contentLines[1])
                if res != None:
                    break
            if res == None:
                return "ERROR: unable to parse note (in unexpected/unsupported format)"

            try:
                date = parser.parse(res['date'])
                content = section[2:] # get just the content lines of the note
                # remove first and trailing empty lines if they exist (notes are always preceeded by an empty line)
                content = content[1:] if content[0] == "" and len(content) > 1 else content
                while len(content) > 1 and content[-1] == "":
                    content = content[:-1]

                note = DataStructures.Note(res['loc'], res['locType'].lower(), date, '\n'.join(str(line) for line in content))
                allBooks[bookId].notes.append(note)
            except ValueError:
                return "ERROR: unable to parse date in note"

        else:
            return "ERROR: not sure how to parse section"
