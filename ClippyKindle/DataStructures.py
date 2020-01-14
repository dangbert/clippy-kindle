class Highlight:
    """ 
    Data structure for storing info about a single highlight
    """
    def __init__(self, loc, locType, date, Content):
        # NOTE: that a pdf has pages instead of loc
        self.loc = loc         # tuple (int locStart, int locEnd)
        self.locType = locType # str "page" or "loc"
        self.date = date       # date added
        self.content = content # content of highlight
 
class Note:
    """ 
    Data structure for storing info about a single note
    """

    def __init__(self, loc, locType, date, content):
        # NOTE: that a pdf has pages instead of loc
        self.loc = loc         # int location (page or location number)
        self.locType = locType # str "page" or "loc"
        self.date = date       # date added
        self.content = content # content of note


class Bookmark:
    """ 
    Data structure for storing info about a single bookmark
    """

    def __init__(self, loc, locType, date):
        # NOTE: that a pdf has pages instead of loc
        self.loc = loc         # int location (page or location number)
        self.locType = locType # str "page" or "loc"
        self.date = date       # date added
