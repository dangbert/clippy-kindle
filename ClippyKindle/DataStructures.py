from datetime import datetime
import ClippyKindle

class Book:
    """
    Data structure for storing all highlights/notes/bookmarks for a given book.

    """
    def __init__(self, title, author=""):
        """
        Initialize a Book object.

        Args:
            title (str): Title of the book.
            author (str): Optional; Author of the book.
        """
        self.title = title.strip()
        self.author = author.strip()
        self.highlights = [] # array of Highlight objects for this book
        self.notes = []      # array of Note objects for this book
        self.bookmarks = []  # array of Bookmark objects for this book

    def __repr__(self):
        """
        represents this object as a string when it's printed
        """
        tmp = "=====Book Object=====\n"
        tmp += "title: '{}'\n".format(self.title)
        tmp += "author: '{}'\n".format(self.author)
        tmp += "highlights:\t{} total\n".format(len(self.highlights))
        tmp += "notes:\t\t{} total\n".format(len(self.notes))
        tmp += "bookmarks:\t{} total\n".format(len(self.bookmarks))
        tmp += "====================="
        return tmp

    def getName(self):
        """
        returns a string containing the book's title and author (if known)
        e.g. "How to Live on 24 Hours a Day by Arnold Bennett.md"
        """
        author = self.author if self.author else 'unknown'
        return f'{ author }-{ self.title }'

    def cutBefore(self, cutDate):
        """
        removes all data in Book object that was modified on or before provided timestamp
        Args:
            cutDate (datetime.datetime): cutoff date for preserving data in this Book.
        Returns:
            None
        """
        self.highlights = [obj for obj in self.highlights if obj.date.timestamp() > cutDate.timestamp()]
        self.notes = [obj for obj in self.notes if obj.date.timestamp() > cutDate.timestamp()]
        self.bookmarks = [obj for obj in self.bookmarks if obj.date.timestamp() > cutDate.timestamp()]

    def cutAfter(self, cutDate):
        """
        removes all data in Book object that was modified on or after the provided timestamp
        Args:
            cutDate (datetime.datetime): cutoff date for preserving data in this Book
        Returns:
            None
        """
        self.highlights = [obj for obj in self.highlights if obj.date.timestamp() < cutDate.timestamp()]
        self.notes = [obj for obj in self.notes if obj.date.timestamp() < cutDate.timestamp()]
        self.bookmarks = [obj for obj in self.bookmarks if obj.date.timestamp() < cutDate.timestamp()]


    def getDateRange(self):
        """
        retrieves the datetime of the earliest and latest item (note, highlight, or bookmark) stored in this book
        (the datetime of an item is the timestamp at which it was originally added to the book)

        Returns:
            (tuple of datetime.datetime objects) first object in tuple is the earliest date, second is the latest
            (if book has no items, earliest will be returned as None, and the latest as the datetimes at epoch 0)
        """
        latest = datetime.fromtimestamp(0)
        earliest = None
        for obj in self.highlights + self.notes + self.bookmarks:
            #print(latest.date.timestamp())
            latest = datetime.fromtimestamp(max(latest.timestamp(), obj.date.timestamp()))
            if earliest == None:
                earliest = obj.date
            else:
                earliest = datetime.fromtimestamp(min(earliest.timestamp(), obj.date.timestamp()))
        return (earliest, latest)

    def toDict(self):
        """
        converts this book object to a dict (which can be jsonified later)
        Returns:
            (dict): A dict storing all the data in this book.
        """
        items = self.highlights + self.notes + self.bookmarks
        items = sortDictList([item.toDict() for item in items])
        dateRange = self.getDateRange()
        return {"title": self.title, "author": self.author,
                "dateStart": None if dateRange[0] == None else ClippyKindle.dateToStr(dateRange[0]),
                "dateEnd": ClippyKindle.dateToStr(dateRange[1]), "annotations": items}

    def toCSV(self):
        """
        converts this book object to a CSV file (columns sorted by location in book increasing)
        Returns:
            Array of lists representing each row (can be written to csv file later).
        """
        self.sort(removeDups=False) # in case user didn't sort first
        csvRows = [["highlight", "associated_note", "highlight_loc", "note", "note_loc", "bookmark_loc"]]

        nIdx = 0 # running associated note index (for matching highlights with an overlapping note)
        usedNotes = {} # keys will be the indices in self.notes already associated with a highlight
        for i in range(0, max(len(self.highlights), len(self.notes), len(self.bookmarks))):
            curRow = []
            if i < len(self.highlights):
                ascNote = ""
                # advance nIdx until its loc passes the current highlight:
                while nIdx < len(self.notes)-1 and self.notes[nIdx].loc < self.highlights[i].loc:
                    nIdx += 1
                #print("nIdx = note {}/{} (loc {}),\tcur highlight {}/{} (loc {}-{})".format(nIdx,len(self.notes), self.notes[nIdx].loc, i, len(self.highlights), self.highlights[i].loc, self.highlights[i].locEnd))
                for offset in [1,0]:   # look at nIdx-1 and nIdx for a match
                    tmpI = nIdx-offset # index to look at in self.notes
                    if (0 <= tmpI < len(self.notes) and (tmpI not in usedNotes) and
                            self.highlights[i].loc <= self.notes[tmpI].loc <= self.highlights[i].locEnd):
                        ascNote = self.notes[tmpI].content
                        usedNotes[tmpI] = True
                        nIdx = tmpI+1           # advance nIdx
                        break
                curRow += [self.highlights[i].content, ascNote, "{}-{}".format(self.highlights[i].loc, self.highlights[i].locEnd)]
            else:
                curRow += ["", "", ""]
            curRow += [self.notes[i].content, self.notes[i].loc] if i < len(self.notes) else ["", ""]
            curRow += [self.bookmarks[i].loc] if i < len(self.bookmarks) else [""]
            csvRows.append(curRow)
        return csvRows

    def sort(self, removeDups):
        """
        sorts arrays self.highlights, self.notes, and self.bookmarks.  Each array is stored by
        (increasing) location in the book (ties are broken by the date recorded)
        optionally removes duplicates within each array

        Args:
            removeDups (bool): set True to remove suspected duplicates within self.notes,
                self.highlights, self.bookmarks. the oldest item in each set of
                duplicates is the one preserved (the one last modified)
        Returns:
            None
        """
        # sort self.highlights:
        tmp = sortDictList([item.toDict() for item in self.highlights])
        self.highlights = [Highlight.fromDict(item) for item in tmp]
        # sort self.notes:
        tmp = sortDictList([item.toDict() for item in self.notes])
        self.notes = [Note.fromDict(item) for item in tmp]
        # sort self.bookmarks:
        tmp = sortDictList([item.toDict() for item in self.bookmarks])
        self.bookmarks = [Bookmark.fromDict(item) for item in tmp]

        if not removeDups:
            return
        # now remove duplicates from each list:
        # TODO: store the set of each removed element in a separate json file (along with the final preserved "duplicate")
        #  randomly sample this file to check for false ?positives?
        def removeDuplicates(objList):
            """
            removes duplicate objects in provided list of sorted objects
            Args:
                objList (list): list of objects where each has method isDuplicate() defined

            Returns:
                Modified list of provided objects (some possibly removed).
            """
            i = 0
            while True:
                if i >= len(objList)-1: # stop when i is at the second to last element
                    break
                # compare to bookmark i+1:
                if objList[i].isDuplicate(objList[i+1]):
                    #print("deleting: " + str(objList[i]))
                    del objList[i] # delete the older one (and don't advance i this loop)
                else:
                    i += 1 
            return objList
        self.highlights = removeDuplicates(self.highlights) # remove duplicate highlights
        self.notes = removeDuplicates(self.notes)           # remove duplicate notes
        self.bookmarks = removeDuplicates(self.bookmarks)   # remove duplicate bookmarks

    @staticmethod
    def fromDict(d):
        """
        Returns:
            A new Book object populated with the values from a provided dict (e.g. read from a JSON file)
        """
        book = Book(d["title"], d["author"])
        for item in d["items"]:
            if item["type"] == "highlight":
                book.highlights.append(Highlight.fromDict(item))
            if item["type"] == "note":
                book.notes.append(Note.fromDict(item))
            if item["type"] == "bookmark":
                book.bookmarks.append(Bookmark.fromDict(item))
        book.sort(removeDups=False) # don't remove dupes if provided dict contained them
        return book


# TODO: don't store locType in Highlight/Note/Bookmark classes (just in Book)
class Highlight:
    """ 
    Data structure for storing info about a single highlight
    """
    def __init__(self, loc, locType, date, content):
        """
        Highlight class constructor

        Args:
            loc tuple: (int locStart, int locEnd)
            locType (str): "page or "location" (identifies what location type this highlight uses)
            date (datetime.datetime): date this highlight was made
            content (str): book text stored in this highlight
        """
        self.loc = loc[0]
        self.locEnd = loc[1]
        self.locType = locType # str "page" or "Location" (note that a pdf has pages instead of locations)
        self.date = date       # date added
        self.content = content.strip() # content of highlight

    def __repr__(self):
        """
        represents this object as a string when it's printed

        Returns:
            None
        """
        return "<Highlight object representing: {} {}-{} from {}, content (preview): '{}'>"\
                .format(self.locType, self.loc, self.locEnd, self.date, self.content)
                #.format(self.locType, self.loc[0], self.loc[1], self.date, self.content[:20])

    def isDuplicate(self, other, fuzzyMatch=True):
        """
        returns true if provided Highlight object can be considered a duplicate of this object

        Args:
            other (Highlight): other Highlight object to compare this object to
            fuzzyMatch (bool): true if we should consider Highlights with overlapping content (but
                               not exactly the same) to be duplicates (default: True)
        Returns:
            (bool): true or false.
        """
        # duplicates will have similar locations
        loc_gap = abs(self.loc - other.loc)
        if loc_gap <= 1:
            return True
        if loc_gap <= (1 if self.locType == "page" else 10):
            if self.content in other.content or other.content in self.content:
                return True
            thisWords, otherWords = self.content.count(" "), other.content.count(" ")
            if thisWords < 5: # speed things up bc we check this later
                return False

            sub = GCS(self.content, other.content).strip()  # get longest common substring
            subWords = sub.count(" ")
            # err on the side of false negatives
            if thisWords >= 5 and len(sub)/len(self.content) >= 0.5:
                # (self.content is a decent length and over half of it is identical to other.content)
                return True
        return False

    def toDict(self):
        """
        Returns:
            (dict): A dict representing this object.
        """
        return {"type": "highlight", "loc": self.loc, "locEnd": self.locEnd, "locType": self.locType,
                "dateStr": ClippyKindle.dateToStr(self.date), "text": self.content}

    @staticmethod
    def fromDict(d):
        """
        Returns:
            A new Highlight object populated with the values from a provided dict (created with toDict()).
        """
        return Highlight((d["loc"], d["locEnd"]), d["locType"],
                ClippyKindle.strToDate(d["dateStr"]), d["text"])


class Note:
    """ 
    Data structure for storing info about a single note
    """

    def __init__(self, loc, locType, date, content):
        """
        Note class constructor

        Args:
            loc (int): page or location value this note was made at
            locType (str): "page or "location" (identifies what location type this highlight uses)
            date (datetime.datetime): date this highlight was made
            content (str): text contents of the note
        """
        self.loc = loc         # int location (page or location number)
        self.locType = locType # str "page" or "loc" (note that a pdf has pages instead of loc)
        self.date = date       # date added
        self.content = content.strip() # content of note

    def isDuplicate(self, other, fuzzyMatch=True):
        """
        returns true if provided Note object can be considered a duplicate of this object

        Args:
            other (Note): other Note object to compare this object to
            fuzzyMatch (bool): true if we should consider Notes with overlapping content (but not
                               exactly the same) to be duplicates (default: True)
        Returns:
            (bool): true or false
        """
        # duplicate notes will have the exact the same location
        # (but remember that nearby (potentially noted) words in ebook can have the same location)
        if self.loc == other.loc:
            if self.content in other.content or other.content in self.content:
                return True
            thisWords, otherWords = self.content.count(" "), other.content.count(" ")
            if thisWords < 6: # speed things up bc we check this later
                return False

            sub = GCS(self.content, other.content).strip()  # get longest common substring
            subWords = sub.count(" ")
            # err on the side of false negatives
            if thisWords >= 6 and len(sub)/len(self.content) >= 0.5:
                # (self.content is a decent length and over half of it is identical to other.content)
                return True
        return False

    def __repr__(self):
        """
        represents this object as a string when it's printed
        Returns:
            None
        """
        return "<Note object representing: {} {} from {}, content (preview): '{}'>"\
                .format(self.locType, self.loc, self.date, self.content[:20])
                #.format(self.locType, self.loc, self.date, self.content)

    def toDict(self):
        """
        Returns:
            (dict): A dict representing this object
        """
        return {"type": "note", "loc": self.loc, "locType": self.locType,
                "dateStr": ClippyKindle.dateToStr(self.date), "text": self.content}

    @staticmethod
    def fromDict(d):
        """
        Returns:
            A new Note object populated with the values from a provided dict (created with toDict())
        """
        return Note(d["loc"], d["locType"], ClippyKindle.strToDate(d["dateStr"]), d["text"])


class Bookmark:
    """ 
    Data structure for storing info about a single bookmark
    """

    def __init__(self, loc, locType, date):
        """
        Bookmark class constructor

        Args:
            loc (int): page or location value this note was made at
            locType (str): "page or "location" (identifies what location type this highlight uses)
            date (datetime.datetime): date this highlight was made
        """
        # NOTE: that a pdf has pages instead of loc
        self.loc = loc         # int location (page or location number)
        self.locType = locType # str "page" or "loc" (note that a pdf has pages instead of loc)
        self.date = date       # date added

    def __repr__(self):
        """
        represents this object as a string when it's printed
        Returns:
            None
        """
        return "<Bookmark object representing: {} {} from {}>".format(self.locType, self.loc, self.date)

    def isDuplicate(self, other):
        """
        returns true if provided Bookmark object can be considered a duplicate of this object

        Args:
            other (Bookmark): other Bookmark object to compare this object to
        Returns:
            (bool): true or false.
        """
        return self.loc == other.loc

    def toDict(self):
        """
        Returns:
            (dict): Dict representing this object.
        """
        return {"type": "bookmark", "loc": self.loc, "locType": self.locType,
                "dateStr": ClippyKindle.dateToStr(self.date)}
    @staticmethod
    def fromDict(d):
        """
        Returns:
            (Bookmark): A new Bookmark object populated with the values from a provided dict (created with toDict())
        """
        return Bookmark(d["loc"], d["locType"], ClippyKindle.strToDate(d["dateStr"]))


##### helper methods: #####
def sortDictList(arr):
    """
    helper function for sorting a list of objects (representing Hightlight/Note/Bookmark objects)
    in order by (increasing) page/location within the book (ties broken by date recorded).

    Args:
        arr (list of dict objects): list of dicts that contain (at least) the fields "loc" and "dateStr"
            (these dicts should have created by a call of toDict())
    Returns:
        (list of dict objects): original list of dicts except now reordered
    """
    for item in arr:
        dateEpoch = ClippyKindle.strToDate(item["dateStr"]).timestamp()
        item["sortKey"] = item["loc"] + float("." + str(int(dateEpoch)))
    arr.sort(key=lambda item: item["sortKey"]) # https://stackoverflow.com/a/403426
    for item in arr: # remove sortKeys
        item.pop("sortKey")
    return arr

def GCS(string1, string2):
    """
    Returns:
        (str): The greatest (longest) common substring between two provided strings
        (returns empty string if there is no overlap)
    """
    # this function copied directly from:
    #   https://stackoverflow.com/a/42882629
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        for j in range(len2):
            lcs_temp=0
            match=''
            while ((i+lcs_temp < len1) and (j+lcs_temp<len2) and string1[i+lcs_temp] == string2[j+lcs_temp]):
                match += string2[j+lcs_temp]
                lcs_temp+=1
            if (len(match) > len(answer)):
                answer = match
    return answer
