#!/usr/bin/env python3
# converts books defined in a json file created by clippy.py into a markdown and csv files

import os
import sys
import argparse
import json
import csv
import copy

from datetime import datetime
from prettytable import PrettyTable
import ClippyKindle

def main():
    # parse args:
    parser = argparse.ArgumentParser(description='Parses a json file created by clippy.py and creates markdown and csv files for each book as desired.')
    parser.add_argument('json_file', type=str, help='(string) path to json file created by clippy.py (e.g. "./collection.json")')
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output markdown and csv files (e.g. "./output")')
    parser.add_argument('--settings', type=str, help='(string) path to json file containing settings for parsing books (optional). If no settings is provided then the program will offer to create one.')
    # https://docs.python.org/dev/library/argparse.html#action
    parser.add_argument('--latest-csv', action="store_true", help='Causes only the newly added items (since the last output using --update-outdate) to be outputted to csv files.')
    parser.add_argument('--update-outdate', action="store_true", help='Stores the date of the latest item outputted for each book in the settings file.')
    parser.add_argument('--omit-notes', action="store_true", help="Omits the user's typed notes for each book in markdown output.")
    # (args starting with '--' are made optional)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    outPath = args.out_folder + ("" if args.out_folder.endswith("/") else "/")
    bookList = ClippyKindle.ClippyKindle.parseJsonFile(args.json_file)
    bookMap = {} # map book titles to its respective Book object
    for bookObj in bookList:
        bookMap[bookObj.getName()] = {"obj": bookObj, "used": False}

    # read json settings from file:
    settings = None
    saveSettings = True # whether to write settings to file (updating existing if provided)
    if args.settings != None:
        with open(args.settings) as f:
            settings = json.load(f)
        settings = updateSettings(bookList, settings, useDefaults=False)
    else:
        # settings file not provided, so make settings here:
        print("No settings file provided, using defaults... (create both a .md and .csv file for each book)")
        useDefaults = not answerYesNo("Or define custom settings now (y/n)? ")
        settings = updateSettings(bookList, settings=None, useDefaults=useDefaults)
        if not answerYesNo("Save settings to file for later use (y/n)? "):
            saveSettings = False
        else:
            args.settings = getAvailableFname("settings", ".json")

    print("\nOutputting files based on selected settings...")
    for groupName in settings:
        #print("at group: " + groupName)
        outputMD = (settings[groupName]["outputMD"] == True)   # whether to output md file for books in group
        outputCSV = (settings[groupName]["outputCSV"] == True) # whether to output csv file for books in group

        # filenames for combined output
        #   (create additional file for everything in group if provided path != "")
        combinedMD = settings[groupName]["combinedMD"].strip()
        combinedCSV = settings[groupName]["combinedCSV"].strip()
        # remove files we will be appending to:
        for path in [combinedMD, combinedCSV]:
            if path != "" and os.path.exists(args.out_folder + "/" + path):
                os.remove(args.out_folder + "/" + path)
        # TODO: add settings option for each group "separateFolder": True, (create folder for each group if needed)
        #       use os.join() to append folder path to the filenames above (not below)

        # loop over books in this group
        for i in range(len(settings[groupName]["books"])):
            bookName = settings[groupName]["books"][i]["name"]
            chapters = settings[groupName]["books"][i]["chapters"]

            bookMap[bookName]["used"] = True

            bookObj = bookMap[bookName]["obj"]             # Book object from collection
            lastDate = bookObj.getDateRange()[1]           # datetime object of latest item added to book
            fname = bookObj.getName().replace("/", "|")    # sanitize for output filename
            outPathMD = "{}{}.md".format(outPath, fname)   # output markdown filename
            outPathCSV = "{}{}.csv".format(outPath, fname) # output csv filename

            mdStr = jsonToMarkdown(bookObj.toDict(), chapters, args.omit_notes)
            csvStr = bookObj.toCSV()
            if args.latest_csv:
                # ensure csv only contains new data since the last time it was outputted
                tmp = copy.deepcopy(bookObj)
                oldEpoch = settings[groupName]["books"][i].get("lastOutputDate", 0) # default 0
                oldEpoch = 0 if oldEpoch == 0 else ClippyKindle.strToDate(oldEpoch).timestamp()
                tmp.cutBefore(datetime.fromtimestamp(oldEpoch))
                csvStr = tmp.toCSV()

            # write markdown file:
            if outputMD:
                with open(outPathMD, 'w') as f:
                    f.write(mdStr)
                print("created: '{}'".format(outPathMD))
            if combinedMD != "":
                combinePath = os.path.join(args.out_folder, combinedMD)
                existed = os.path.exists(combinePath)
                with open(combinePath, 'a+') as f: # append or create file
                    f.write(mdStr)
                if not existed:
                    print("created: '{}'".format(combinePath)) # print the first time only
            # write csv file:
            if outputCSV:
                with open(outPathCSV, 'w') as f:
                    csv.writer(f).writerows(csvStr)
                print("created: '{}'".format(outPathCSV))
                # update last outputted timestamp
                if args.update_outdate:
                    settings[groupName]["books"][i]["lastOutputDate"] = ClippyKindle.dateToStr(lastDate)
            if combinedCSV != "":
                combinePath = os.path.join(args.out_folder, combinedCSV)
                existed = os.path.exists(combinePath)
                with open(combinePath, 'a+') as f:  # append or create file
                    csv.writer(f).writerows(csvStr if not existed else csvStr[1:]) # remove header if file already existed
                if args.update_outdate:
                    settings[groupName]["books"][i]["lastOutputDate"] = ClippyKindle.dateToStr(lastDate)
                if not existed:
                    print("created: '{}'".format(combinePath)) # print the first time only

    # update settings file:
    if saveSettings:
        with open(args.settings, 'w') as f:
            json.dump(settings, f, indent=2) # write indented json to file
        print("\nSettings stored in '{}'".format(args.settings))
    #########################################

def jsonToMarkdown(data, chapters=[], omitNotes=False):
    """
    creates a markdown representation of a book's highlights/notes/bookmarks
    parameters:
        data (dict): dict holding data about a book (created with Book.toDict())
        chapters (array of dicts): (optional) array storing list of book chapters
            e.g. [{"loc": 248, "title": "CHAPTER 1: The cult of the Head Start"}, ...]
    return:
        (str) markdown representation of provided book data
    """
    #DATE_FMT = ClippyKindle.DATE_FMT_OUT # includes time
    DATE_FMT = "%B %d, %Y"
    titleStr = data["title"]
    titleStr += "" if data["author"] == None else " by {}".format(data["author"])
    if len(data["items"]) > 0:
        locType = "loc" if data["items"][0]["locType"] == "location" else data["items"][0]["locType"]

    md = ""
    if len(data["items"]) == 0:
        dateInfo = "* (No notes taken for this book)"
    else:
        # simplify formatting of date strings
        dateStart = ClippyKindle.strToDate(data["dateStart"]).strftime(DATE_FMT)
        dateEnd = ClippyKindle.strToDate(data["dateEnd"]).strftime(DATE_FMT)
        dateInfo = "* Notes from: {} - {}".format(dateStart, dateEnd)
    md += "# {}\n{}\n---\n\n".format(titleStr, dateInfo)

    # current index into chapters (some chapters have subchapters, rightmost value is deepest nested subchapter index)
    cIndex = [0] if len(chapters) > 0 else None
    for item in data["items"]:
        # handle any chapters appearing before this item (that haven't yet been outputted)
        while cIndex != None:
            chap = getChapterAt(cIndex, chapters)
            if chap == None:
                cIndex = None
                break
            if chap["loc"] > item["loc"]:
                break
            # print number of '#' based on current chapter level
            md += "#{} {}\n".format("#" * len(cIndex), chap["title"])
            cIndex = cIndexAdvance(cIndex, chapters, verbose=True)
        if "content" in item:  # escape all '*' as '\*'
            item["content"] = item["content"].replace('*', '\*')
        if item["type"] == "highlight":
            md += "* {} -- [{} {}]\n\n".format(item["content"], locType, item["loc"])
        if item["type"] == "note" and not omitNotes:
            md += "> {} -- [{} {}]\n\n".format(item["content"], locType, item["loc"])
        if item["type"] == "bookmark":
            md += "* [Bookmark -- {} {}]\n\n".format(locType, item["loc"])

    # print any chapters not yet reached:
    while cIndex != None:
        chap = getChapterAt(cIndex, chapters)
        if chap == None:
            cIndex = None
            break
        md += "#{} {}\n".format("#" * len(cIndex), chap["title"])
        cIndex = cIndexAdvance(cIndex, chapters, verbose=True)
    return md

def cIndexAdvance(cIndex, chapters, verbose=False, _tryDeeper=True):
    """
    helper function for iterating through a nested list of chapter dicts
    params:
        cIndex: array of indices into chapters
        chapters: array of chapter dict objects (which individually may or may not have nested chapters
    return (array or None): an updated cIndex that refers to the next chapter after the provided cIndex
        (in depth first descent, BUT counting parent chapters as visited on the descent down)
        returns None if we finish traversing chapters
    """
    # try to descend one level deeper:
    if _tryDeeper:
        if getChapterAt(cIndex + [0], chapters) != None:
            return cIndex + [0]
    # try advancing within current level:
    cIndex[-1] += 1
    if getChapterAt(cIndex, chapters) != None:
        return cIndex
    # try backing out one level (so we can advance within that level):
    if len(cIndex) == 1:
        return None # reached end of chapters
    return cIndexAdvance(cIndex[:-1], chapters, _tryDeeper=False)

def getChapterAt(cur_cIndex, cur_chapters):
    """
    helper function for getting a chapter object at a desired location within a nested list of chapter dicts
    params:
        cur_cIndex: array of indices into cur_chapters
        cur_chapters: array of chapter dict objects (which individually may or may not have nested chapters
        (i.e. store their own array of chaper dict objects (which are subchapters))
    return: the chapter dict object found at provided cIndex (or None if not found)
    """
    if len(cur_cIndex) == 1:
        # finally returns a chapter dict object (not an array)
        return cur_chapters[cur_cIndex[0]] if (cur_cIndex[0] < len(cur_chapters)) else None
    if "chapters" not in cur_chapters[cur_cIndex[0]] or not isinstance(cur_chapters[cur_cIndex[0]]["chapters"], list):
        return None # unable to descend further as expected
    return getChapterAt(cur_cIndex[1:], cur_chapters[cur_cIndex[0]]["chapters"])

def updateSettings(bookList, settings=None, useDefaults=False):
    """
    ensures that every book in the provided list exists in the settings
    modifies existing settings if provided or creates default settings to modify
    params:
        bookList: list of ClippyKindle.Book objects for settings to be created for
        useDefaults (bool): true when we want to default to outputting a md and csv file for each book
            otherwise prompt user to choose the group for each book that needs to be added to settings.
            (Ignored if settings != None)
        settings (dict): optional existing settings to modify. If not provided, default settings
            are created and modified.
    return (dict): settings to use for these books
    """
    if settings == None:
        # default settings groups:
        settings = {
            "csvOnly": {"outputMD": False, "outputCSV": True, "combinedMD": "", "combinedCSV": "", "books": []},
            "both":    {"outputMD": True, "outputCSV": True, "combinedMD": "", "combinedCSV": "", "books": []},
            "mdOnly":  {"outputMD": True, "outputCSV": False, "combinedMD": "", "combinedCSV": "", "books": []},
            "skip":    {"outputMD": False, "outputCSV": False, "combinedMD": "", "combinedCSV": "", "books": []}
        }
    else:
        useDefaults = False # (group "both" isn't guranteed to exist in this case)
    # determine which books aren't in the settings:
    tmpMap = {} # map book names -> count of their appearences in settings 
    for groupName in settings:
        for b in settings[groupName]["books"]:
            tmpMap[b["name"]] = 1 if (b["name"] not in tmpMap) else tmpMap[b["name"]] + 1
    newBooks = [bookObj for bookObj in bookList if bookObj.getName() not in tmpMap]
    # print warning for books appearing in settings multipe times:
    for name in [bookName for bookName in tmpMap if tmpMap[bookName] > 1]:
        print("NOTE: book appears {} times in settings: '{}'".format(tmpMap[name], name))

    if len(newBooks) > 0:
        print("{} book(s) must have their output settings defined...".format(len(newBooks)))
    # place each new book under desired group (default is "both"):
    for bookIndex, bookObj in zip(range(len(newBooks)), newBooks):
        selectedGroup = "both"
        if not useDefaults:
            prompt = "\nSelect a settings group for book {} of {}: '{}'\n"\
                    .format(bookIndex+1, len(newBooks), bookObj.getName())
            table = PrettyTable()  # http://zetcode.com/python/prettytable/
            table.field_names = ["Group #", "Group", "md file?", "csv file?", "Combined md for group?", "Combined csv for group?"]
            for index, groupName in zip(range(len(settings)), settings):
                table.add_row([index+1, groupName, settings[groupName]["outputMD"], settings[groupName]["outputCSV"],
                    settings[groupName]["combinedMD"] != "", settings[groupName]["combinedCSV"] != ""])
            prompt += str(table) + "\nEnter group number ({}-{}): ".format(1, len(settings))
            selectedGroup = [g for g in settings][answerMenu(prompt, len(settings))-1]
            print()
        settings[selectedGroup]["books"].append({
            "name": bookObj.getName(),
            "chapters": []
        })
    return settings

def answerMenu(prompt, numOptions):
    """
    returns the response to a prompt that expects the user to choose a number
    between 1 and numOptions (reprompts until user provides a valid response).
    params:
        prompt (string): prompt to show user before awaiting input
        numOptions (int): number of options user is being asked to choose from
    return (int): number
    """
    val = ""
    while val not in range(1, numOptions+1):
        try:
            val = int(input(prompt))
        except ValueError:
            continue
    return val

def answerYesNo(prompt):
    """
    returns the response to a y/n question prompt (reprompts until user provides a valid response)
    params:
        prompt (string): prompt to show user before awaiting input
    return (bool): True if user responds yes, False if user responds no
    """
    val = ""
    while val not in ["y", "yes", "n", "no"]:
        val = input(prompt).strip().lower()
    return val in ["y", "yes"]

def getAvailableFname(prefix, ext):
    """
    returns a valid filename (to a file not already existing)
    that starts with prefix and ends with the provided extension
    (adds a number in between if needed)
    parameters:
        prefix (str): file prefix (e.g. "./out")
        ext (str): file extension including '.' (e.g. ".json")
    return (str): file path to use
    """

    if not os.path.exists(prefix + ext):
        return prefix + ext
    prefix += "1"
    # increment number at end of prefix until file doesn't already exist
    while os.path.exists(prefix + ".json"):
        prefix = prefix[:-1] + str(int(prefix[-1]) + 1)
    return prefix + ext

if __name__ == "__main__":
    main()
