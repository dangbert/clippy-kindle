import json

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

    # TODO: also create toCSV(self)
    # TODO: perhaps make this toDict() and return a dict instead so it's easier to combine each book
    #   into a json array of objects for each book
    def toJson(self):
        """
        convert this book object to json
        TODO: (is this the best place to do this / define this function?)
        """

        items = self.highlights + self.notes + self.bookmarks
        items = [json.loads(item.toJson()) for item in items]
        print(items)
        for item in items:
            print("ITEM:")
            item["sortKey"] = item["loc"] + float("." + str(int(item["dateEpoch"])))
            print(item)

        # sort by loc first (for ties also sort by date added increasing)
        #sortKeys = [item.loc + float("." + str(int(item.date.timestamp()))) for item in items]
        #sortKeys = [item["loc"] + float("." + str(int(item["dateEpoch"]))) for item in items]
        #print(sortKeys)
        #items = [item for _, item in sorted(zip(sortKeys, items))]

        items.sort(key=lambda item: item["sortKey"]) # https://stackoverflow.com/a/403426
        # TODO: don't include sortKey when returning the data...

        data = {"title": self.title, "author": self.author,
                "items": items}
                #"items": [item.toJson() for item in items]}
        return json.dumps(data)

    def sort(self):
        """
        sort the arrays self.hightlights, self.notes, self.bookmarks
        in order by (increasing) page/location within the book
        """
        print("\n\nsorting book: ")
        print(self)
        # TODO: break this into separate functions (e.g. sortHighlights())

        # sort highlights
        # TODO:
        #   sort by loc first (for ties also sort by date added increasing)
        #   if any highlights have the same loc and locEnd, then keep the one more recently edited
        sortKeys = [ h.loc + float("." + str(int(h.date.timestamp()))) for h in self.highlights]
        print(sortKeys)
        # https://stackoverflow.com/a/6618543
        self.highlights = [h for _, h in sorted(zip(sortKeys, self.highlights))]

        print("HIGHLIGHTS:")
        for highlight in self.highlights:
            print(highlight)

        # TODO: keep in mind that for notes, when a note is modified the earlier enty in "My Clippings.txt" is not deleted
        #     e.g. search for "my budget app" in the txt file

        pass

class Highlight:
    """ 
    Data structure for storing info about a single highlight

    parameters:
    loc: tuple (int locStart, int locEnd)
    """
    def __init__(self, loc, locType, date, content):
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

    def toJson(self):
        """
        Returns json representing this object
        """
        data = {"type": "highlight", "loc": self.loc, "locEnd": self.locEnd, "locType": self.locType,
                "dateStr": self.date.strftime("%B %d, %Y %H:%M:%S"),
                "dateEpoch": self.date.timestamp(), "content": self.content}
        return json.dumps(data)


class Note:
    """ 
    Data structure for storing info about a single note
    """

    def __init__(self, loc, locType, date, content):
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

    def toJson(self):
        """
        Returns json representing this object
        """
        data = {"type": "note", "loc": self.loc, "locType": self.locType,
                "dateStr": self.date.strftime("%B %d, %Y %H:%M:%S"),
                "dateEpoch": self.date.timestamp(), "content": self.content}
        return json.dumps(data)


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

    def toJson(self):
        """
        Returns json representing this object
        """
        data = {"type": "bookmark", "loc": self.loc, "locType": self.locType,
                "dateStr": self.date.strftime("%B %d, %Y %H:%M:%S"),
                "dateEpoch": self.date.timestamp()}
        return json.dumps(data)
