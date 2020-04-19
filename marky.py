#!/usr/bin/env python3
# converts a json file created by clippy.py into a markdown file

import os
import sys
import argparse
import json
import csv
import copy

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz
import pprint

import ClippyKindle

def main():
    # parse args:
    parser = argparse.ArgumentParser(description='Parses a json file created by clippy.py and outputs a markdown file for each book')
    parser.add_argument('json_file', type=str, help='(string) path to json file created by clippy.py (e.g. "./collection.json")')
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output markdown and csv files')
    parser.add_argument('--settings', type=str, help='(string) path to json file containing settings for parsing books (optional). If no settings is provided then the program will offer to create one, otherwise a .md and .csv file will be created for all books.')
    # https://docs.python.org/dev/library/argparse.html#action
    parser.add_argument('--latest-csv', action="store_true", help='When this flag is provided, only the newly added items (since the last output) will be outputted to csv files.')
    parser.add_argument('--update-outdate', action="store_true", help='When this flag is provided, epoch of the latest item outputted for each book will be updated in the settings file.')
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
    updateSettings = True # whether to write settings to file (updating existing if provided)
    if args.settings != None:
        with open(args.settings) as f:
            settings = json.load(f)
    else:
        print("No settings file provided... defaulting to creating both a .md and .csv file for each book.")
        if not answerYesNo("Save these settings to file (y/n)? "):
            updateSettings = False

        args.settings = getAvailableFname("settings", ".json")
        # default settings (with default group names)
        settings = {
            "csvOnly": {"outputMD": False, "outputCSV": True, "combinedMD": "", "combinedCSV": "", "books": []},
            "both":    {"outputMD": True, "outputCSV": True, "combinedMD": "", "combinedCSV": "", "books": []},
            "mdOnly":  {"outputMD": True, "outputCSV": False, "combinedMD": "", "combinedCSV": "", "books": []},
            "skip":    {"outputMD": False, "outputCSV": False, "combinedMD": "", "combinedCSV": "", "books": []}
        }
        # put all books under section both
        for bookObj in bookList:
            settings["both"]["books"].append({
                "name": bookObj.getName(),
                "chapters": []
            })

    warnings = 0
    for groupName in settings:
        #print("at group: " + groupName)
        outputMD = (settings[groupName]["outputMD"] == True)    # whether to output md file for books in group
        outputCSV = (settings[groupName]["outputCSV"] == True) # whether to output csv file for books in group

        # filenames for combined output
        #   (in addition to seprate files, combine everything in group if provided path != "")
        combinedMD = settings[groupName]["combinedMD"].strip()
        combinedCSV = settings[groupName]["combinedCSV"].strip()
        # remove files we will be appending to:
        for path in [combinedMD, combinedCSV]:
            if path != "" and os.path.exists(args.out_folder + "/" + path):
                os.remove(args.out_folder + "/" + path)

        # loop over books in this group
        for i in range(len(settings[groupName]["books"])):
            bookName = settings[groupName]["books"][i]["name"]
            chapters = settings[groupName]["books"][i]["chapters"]

            #print("at book: " + bookName)
            if not bookName in bookMap:
                print("WARNING: skipping book '{}' not found in file '{}'".format(bookName, args.settings))
                warnings += 1
                continue
            if bookMap[bookName]["used"] == True:
                print("WARNING: skipping book '{}' found in multiple groups in file '{}'".format(bookName, args.settings))
                warnings += 1
                continue
            bookMap[bookName]["used"] = True

            bookObj = bookMap[bookName]["obj"]             # Book object from collection
            lastDate = bookObj.getDateRange()[1]           # datetime object of latest item added to book
            fname = bookObj.getName().replace("/", "|")    # sanitize for output filename
            outPathMD = "{}{}.md".format(outPath, fname)   # output markdown filename
            outPathCSV = "{}{}.csv".format(outPath, fname) # output csv filename

            mdStr = jsonToMarkdown(bookObj.toDict(), chapters)
            csvStr = bookObj.toCSV()
            if args.latest_csv:
                # ensure csv only contains new data since the last time it was outputted
                tmp = copy.deepcopy(bookObj)
                oldEpoch = settings[groupName]["books"][i].get("lastOutputDate", 0) # default 0
                oldEpoch = 0 if oldEpoch == 0 else datetime.strptime(oldEpoch, ClippyKindle.DATE_FMT_OUT).timestamp()
                #print("using oldEpoch = {} ({})".format(oldEpoch, datetime.fromtimestamp(oldEpoch)))
                tmp.cutBefore(datetime.fromtimestamp(oldEpoch))
                csvStr = tmp.toCSV()

            # write markdown file:
            if outputMD:
                with open(outPathMD, 'w') as f:
                    f.write(mdStr)
                print("created: '{}'".format(outPathMD))
            if combinedMD != "":
                with open(args.out_folder + "/" + combinedMD, 'a+') as f: # append or create file
                    f.write(mdStr)
            # write csv file:
            if outputCSV:
                with open(outPathCSV, 'w') as f:
                    csv.writer(f).writerows(csvStr)
                print("created: '{}'".format(outPathCSV))
                # update last outputted timestamp
                if args.update_outdate:
                    settings[groupName]["books"][i]["lastOutputDate"] = lastDate.strftime(ClippyKindle.DATE_FMT_OUT)
            if combinedCSV != "":
                # TODO: if file already exists (remove header from current csv being appended)
                # TODO: print file created the first time it's created...
                with open(args.out_folder + "/" + combinedCSV, 'a+') as f: # append or create file
                    csv.writer(f).writerows(csvStr)
                if args.update_outdate:
                    settings[groupName]["books"][i]["lastOutputDate"] = lastDate.strftime(ClippyKindle.DATE_FMT_OUT)

    #for bookName in bookList:
    for bookName in bookMap:
        if bookMap[bookName]["used"] == False:
            print("WARNING: book '{}' not found in settings file '{}'".format(bookName, args.settings))
            # TODO: if book not found in settings, offer to let the user add it to the desired given category...
            #   (consider doing this above when default settings are created)
            warnings += 1
    if warnings != 0:
        print("\nFinished with {} warnings".format(warnings))

    # update settings.json
    if updateSettings:
        with open(args.settings, 'w') as f:
            json.dump(settings, f, indent=2) # write indented json to file
        print("\nSettings stored in '{}'".format(args.settings))
    #########################################

def jsonToMarkdown(data, chapters=[]):
    """
    creates a markdown representation of a book's highlights/notes/bookmarks
    parameters:
        data (dict): dict holding data about a book (created with Book.toDict())
        chapters (array of dicts): (optional) array storing list of book chapters
            e.g. [{"loc": 248, "title": "CHAPTER 1: The cult of the Head Start"}, ...]
    return:
        (str) markdown representation of provided book data
    """
    titleStr = data["title"]
    titleStr += "" if data["author"] == None else " by {}".format(data["author"])
    #print("converting '{}'".format(titleStr))
    if len(data["items"]) > 0:
        locType = "loc" if data["items"][0]["locType"] == "location" else data["items"][0]["locType"]

    # TODO: add dates for first and last highlight/note/bookmark...
    # and maybe stats on number of each type (TODO: have clippy.py store these in the json)
    md = ""
    md += "# {}\n---\n\n".format(titleStr)
    cIndex = 0 # current index into chapters
    for item in data["items"]:
        # handle any chapters appearing before this item (that haven't yet been outputted)
        for i in range(cIndex, len(chapters)):
            if chapters[cIndex]["loc"] > item["loc"]:
                break
            md += "## {}\n".format(chapters[cIndex]["title"])
            cIndex += 1

        if "content" in item:  # escape all '*' as '\*'
            item["content"] = item["content"].replace('*', '\*')
        if item["type"] == "highlight":
            md += "* {} -- [{} {}]\n\n".format(item["content"], locType, item["loc"])
        if item["type"] == "note":
            md += "> {} -- [{} {}]\n\n".format(item["content"], locType, item["loc"])
        if item["type"] == "bookmark":
            md += "* [Bookmark -- {} {}]\n\n".format(locType, item["loc"])

    # print any chapters not yet reached:
    for cIndex in range(cIndex, len(chapters)):
        md += "## {}\n".format(chapters[cIndex]["title"])
    return md

def answerYesNo(prompt):
    """
    helper function returning the response to a y/n question prompt
    (reprompts until user provides a valid response)
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
