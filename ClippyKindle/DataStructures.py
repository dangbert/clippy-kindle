from datetime import datetime

class Book:
    """ 
    Data structure for storing all highlights/notes/bookmarks for a given book
    """
    def __init__(self, title, author=None):
        """
        Initialize a Book object
        """
        self.title = title.strip()
        self.author = None if author == None else author.strip()
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

    # TODO: also create toCSV(self)
    def toDict(self):
        """
        converts this book object to a dict (which can be jsonified later)
        return (dict): dict storing the data in this book
        """
        items = self.highlights + self.notes + self.bookmarks
        items = [item.toDict() for item in items]
        items = sortDictList(items)

        data = {"title": self.title, "author": self.author,
                "items": items}
        return data

    def sort(self, removeDups):
        """
        sorts arrays self.highlights, self.notes, and self.bookmarks.  Each array is stored by
        (increasing) location in the book (ties are broken by the date recorded)
        optionally removes duplicates within each array

        parameters:
            removeDups (bool): set True to remove suspected duplicates within self.notes,
                               self.highlights, self.bookmarks. the oldest item in each set of
                               duplicates is the one preserved (the one last modified)
        return: None
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
        def removeDuplicates(objList):
            """
            removes duplicate objects in provided list of sorted objects
            parameters:
                objList (list): list of objects where each has method isDuplicate() defined
            returns (list): modified list of provided objects (some possibly removed)
            """
            i = 0
            while True:
                if i >= len(objList)-2: # stop when i is at the second to last element
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


class Highlight:
    """ 
    Data structure for storing info about a single highlight
    """
    def __init__(self, loc, locType, date, content):
        """
        Highlight class constructor

        parameters:
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
        """
        return "<Highlight object representing: {} {}-{} from {}, content (preview): '{}'>"\
                .format(self.locType, self.loc, self.locEnd, self.date, self.content)
                #.format(self.locType, self.loc[0], self.loc[1], self.date, self.content[:20])

    def isDuplicate(self, other, fuzzyMatch=True):
        """
        returns true if provided Highlight object can be considered a duplicate of this object

        parameters:
            other (Highlight): other Highlight object to compare this object to
            fuzzyMatch (bool): true if we should consider Highlights with overlapping content (but
                               not exactly the same) to be duplicates (default: True)
        return (bool): true or false
        """
        # duplicates will have similar locations
        if abs(self.loc - other.loc) <= (1 if self.locType == "page" else 10):
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
        Returns dict representing this object
        """
        data = {"type": "highlight", "loc": self.loc, "locEnd": self.locEnd, "locType": self.locType,
                "dateStr": self.date.strftime("%B %d, %Y %H:%M:%S"),
                "dateEpoch": self.date.timestamp(), "content": self.content}
        return data

    @staticmethod
    def fromDict(d):
        """
        Returns a new Highlight object populated with the values from a provided dict (created with toDict())
        """
        return Highlight((d["loc"], d["locEnd"]), d["locType"], datetime.fromtimestamp(d["dateEpoch"]), d["content"])


class Note:
    """ 
    Data structure for storing info about a single note
    """

    def __init__(self, loc, locType, date, content):
        """
        Note class constructor

        parameters:
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

        parameters:
            other (Note): other Note object to compare this object to
            fuzzyMatch (bool): true if we should consider Notes with overlapping content (but not
                               exactly the same) to be duplicates (default: True)
        return (bool): true or false
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
        """
        return "<Note object representing: {} {} from {}, content (preview): '{}'>"\
                .format(self.locType, self.loc, self.date, self.content[:20])
                #.format(self.locType, self.loc, self.date, self.content)

    def toDict(self):
        """
        Returns dict representing this object
        """
        data = {"type": "note", "loc": self.loc, "locType": self.locType,
                "dateStr": self.date.strftime("%B %d, %Y %H:%M:%S"),
                "dateEpoch": self.date.timestamp(), "content": self.content}
        return data

    @staticmethod
    def fromDict(d):
        """
        Returns a new Note object populated with the values from a provided dict (created with toDict())
        """
        return Note(d["loc"], d["locType"], datetime.fromtimestamp(d["dateEpoch"]), d["content"])


class Bookmark:
    """ 
    Data structure for storing info about a single bookmark
    """

    def __init__(self, loc, locType, date):
        """
        Bookmark class constructor

        parameters:
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
        """
        return "<Bookmark object representing: {} {} from {}>".format(self.locType, self.loc, self.date)

    def isDuplicate(self, other):
        """
        returns true if provided Bookmark object can be considered a duplicate of this object

        parameters:
            other (Bookmark): other Bookmark object to compare this object to
        return (bool): true or false
        """
        return self.loc == other.loc

    def toDict(self):
        """
        Returns dict representing this object
        """
        data = {"type": "bookmark", "loc": self.loc, "locType": self.locType,
                "dateStr": self.date.strftime("%B %d, %Y %H:%M:%S"),
                "dateEpoch": self.date.timestamp()}
        return data

    @staticmethod
    def fromDict(d):
        """
        Returns a new Bookmark object populated with the values from a provided dict (created with toDict())
        """
        return Bookmark(d["loc"], d["locType"], datetime.fromtimestamp(d["dateEpoch"]))


##### helper methods: #####
def sortDictList(arr):
    """
    helper function for sorting a list of objects (representing Hightlight/Note/Bookmark objects)
    in order by (increasing) page/location within the book (ties broken by date recorded).

    parameters:
        arr (list of dict objects): list of dicts that contain (at least) the fields "loc" and "dateEpoch"
                                    (these dicts should have created by a call of toDict())
    return (list of dict objects): original list of dicts except now reordered
    """
    for item in arr:
        item["sortKey"] = item["loc"] + float("." + str(int(item["dateEpoch"])))
    arr.sort(key=lambda item: item["sortKey"]) # https://stackoverflow.com/a/403426
    for item in arr: # remove sortKeys
        item.pop("sortKey")
    return arr

def GCS(string1, string2):
    """
    returns the greatest (longest) common substring between two provided strings
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
