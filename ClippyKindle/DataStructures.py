class Book:
    """ 
    Data structure for storing all highlights/notes/bookmarks for a given book
    """
    def __init__(self, title, author=None):
        """
        Initialize a Book object
        """
        self.title = title
        self.author = author
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
        #return """
        #=====Book Object=====
        #title: '{}', author: '{}'
        #highlights:\t{} total
        #notes:\t\t{} total
        #bookmarks:\t{} total
        #=====================
        #""".format(self.title, self.author, len(self.highlights), len(self.notes), len(self.bookmarks))

    def toJson(self):
        """
        convert this book object to json....
        TODO: (is this the best place to do this / define this function?)
        """
        pass

    def sort(self):
        """
        sort the arrays self.hightlights, self.notes, self.bookmarks
        in order by (increasing) page/location within the book
        """

        pass

class Highlight:
    """ 
    Data structure for storing info about a single highlight
    """
    def __init__(self, loc, locType, date, content):
        self.loc = loc         # tuple (int locStart, int locEnd)
        self.locType = locType # str "page" or "Location" (note that a pdf has pages instead of locations)
        self.date = date       # date added
        self.content = content # content of highlight

    def __repr__(self):
        """
        represents this object as a string when it's printed
        """
        return "<Highlight object representing: {} {}-{} from {}, content (preview): '{}'>"\
                .format(self.locType, self.loc[0], self.loc[1], self.date, self.content[:20])


class Note:
    """ 
    Data structure for storing info about a single note
    """

    def __init__(self, loc, locType, date, content):
        self.loc = loc         # int location (page or location number)
        self.locType = locType # str "page" or "loc" (note that a pdf has pages instead of loc)
        self.date = date       # date added
        self.content = content # content of note


class Bookmark:
    """ 
    Data structure for storing info about a single bookmark
    """

    def __init__(self, loc, locType, date):
        # NOTE: that a pdf has pages instead of loc
        self.loc = loc         # int location (page or location number)
        self.locType = locType # str "page" or "loc" (note that a pdf has pages instead of loc)
        self.date = date       # date added

    def __repr__(self):
        """
        represents this object as a string when it's printed
        """
        return "<Bookmark object representing: {} {} from {}>".format(self.locType, self.loc, self.date)
