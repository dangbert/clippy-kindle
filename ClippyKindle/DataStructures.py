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

    def sort(self):
        """
        sort the arrays self.hightlights, self.notes, self.bookmarks
        in order by (increasing) page/location within the book
        """

        pass

    # TODO: add a toString type function

class Highlight:
    """ 
    Data structure for storing info about a single highlight
    """
    def __init__(self, loc, locType, date, content):
        self.loc = loc         # tuple (int locStart, int locEnd)
        self.locType = locType # str "page" or "loc" (note that a pdf has pages instead of loc)
        self.date = date       # date added
        self.content = content # content of highlight


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
