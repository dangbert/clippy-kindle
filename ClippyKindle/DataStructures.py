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

        for item in items:
            item["sortKey"] = item["loc"] + float("." + str(int(item["dateEpoch"])))
        items.sort(key=lambda item: item["sortKey"]) # https://stackoverflow.com/a/403426
        for item in items: # remove sortKeys
            item.pop("sortKey")

        data = {"title": self.title, "author": self.author,
                "items": items}
        return data

    def sort(self, removeDups):
        """
        sorts arrays self.highlights, self.notes, and self.bookmarks.  Each array is stored by
        (increasing) location in the book (ties are broken by the date recorded)
        removes suspected duplicates within self.notes and self.highlights
        the oldest item in each set of duplicates is the one preserved
        (meaning it was the one last modified)

        return: None
        """
        tmp = [item.toDict() for item in self.highlights]
        self.highlights = [Highlight.fromDict(item) for item in tmp]

        tmp = [item.toDict() for item in self.notes]
        self.notes = [Note.fromDict(item) for item in tmp]

        tmp = [item.toDict() for item in self.bookmarks]
        self.bookmarks = [Bookmark.fromDict(item) for item in tmp]

        pass
        #print("\n\nsorting book: ")
        #print(self)
        # TODO: break this into separate functions (e.g. sortHighlights())

        # TODO:
        #   if any highlights have the same loc and locEnd, then keep the one more recently edited
        # TODO: find largest common substring between any highlights with overlapping range [loc, locEnd]

        # sort by loc first (for ties also sort by date added increasing)
        #sortKeys = [ h.loc + float("." + str(int(h.date.timestamp()))) for h in self.highlights]
        ## https://stackoverflow.com/a/6618543
        #self.highlights = [h for _, h in sorted(zip(sortKeys, self.highlights))]

        # sort highlights
        #for item in self.highlights:
        #    item["sortKey"] = item["loc"] + float("." + str(int(item["dateEpoch"])))
        #self.highlights.sort(key=lambda item: item["sortKey"]) # https://stackoverflow.com/a/403426

        ## TODO: sort notes- keeping in mind that when a note is modified the earlier enty in "My Clippings.txt" is not deleted
        ##     e.g. search for "my budget app" in the txt file
        ##     do similar largest common substring this as with the highlights
        #for item in self.notes:
        #    item["sortKey"] = item["loc"] + float("." + str(int(item["dateEpoch"])))
        #self.notes.sort(key=lambda item: item["sortKey"]) # https://stackoverflow.com/a/403426

        #print("HIGHLIGHTS:") # TODO: for debugging
        #for highlight in self.highlights:
        #    print(highlight)

    @staticmethod
    def _sortList(arr):
        """
        helper function for sorting a provided list of objects representing Hightlights/Notes/Bookmarks
        in order by (increasing) page/location within the book (ties broken by date recorded)

        parameters:
            arr (list of dict objects): list of dicts that contain (at least) the fields "loc" and "dateEpoch"
        return (list of dict objects): original array of dicts except now reordered
        """
        for item in arr:
            item["sortKey"] = item["loc"] + float("." + str(int(item["dateEpoch"])))
        arr.sort(key=lambda item: item["sortKey"]) # https://stackoverflow.com/a/403426
        for item in arr: # remove sortKeys
            item.pop("sortKey")


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
        self.content = content # content of highlight

    def __repr__(self):
        """
        represents this object as a string when it's printed
        """
        return "<Highlight object representing: {} {}-{} from {}, content (preview): '{}'>"\
                .format(self.locType, self.loc, self.locEnd, self.date, self.content)
                #.format(self.locType, self.loc[0], self.loc[1], self.date, self.content[:20])

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
        self.content = content # content of note

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
