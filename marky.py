#!/usr/bin/env python3
# converts a json file created by clippy.py into a markdown file

import os
import sys
import argparse
import json
import csv

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz
import pprint

from ClippyKindle import ClippyKindle

def main():
    # parse args:
    parser = argparse.ArgumentParser(description='Parses a json file created by clippy.py and outputs a markdown file for each book')
    parser.add_argument('json_file', type=str, help='(string) path to json file created by clippy.py (e.g. "./out.json")')
    # TODO: default to '.' as out_folder if not provided?
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output markdown and csv files')
    parser.add_argument('--settings', type=str, help='(string) path to json file containing settings for parsing books (optional). If no settings is provided then the program will offer to create one, otherwise a .md and .csv file will be created for all books.')
    # (args starting with '--' are made optional)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    # read json settings from file:
    settings = None
    if args.settings != None:
        with open(args.settings) as f:
            settings = json.load(f)
    outPath = args.out_folder + ("" if args.out_folder.endswith("/") else "/")

    bookList = ClippyKindle.parseJsonFile(args.json_file)
    bookMap = {} # map book titles to its respective Book object
    for bookObj in bookList:
        bookMap[bookObj.getName()] = {"obj": bookObj, "used": False}


    #############################################
    ####### from clippy.py:
    #############################################
    # offer to create a settings file if not provided
    if settings == None:
        print("No settings file provided... defaulting to creating both a .md and .csv file for each book.")
        if answerYesNo("OR create settings file now (y/n)? "):
            args.settings = getAvailableFname("settings", ".json")
            # default settings (with default group names)
            settings = {
                    "csvOnly": {"outputMD": false, "outputCSV": true, "books": []},
                    "both":    {"outputMD": true, "outputCSV": true, "books": []},
                    "mdOnly":  {"outputMD": true, "outputCSV": false, "books": []},
                    "skip":    {"outputMD": false, "outputCSV": false, "books": []}
            }
        else:
            print("CODE doesn't currently work when no settings are provided. fix this next.") # TODO
            # because we'd have to iterate over bookList instead of settings
            exit(1)

    # remove files we will be appending to:
    #for fname in [".skipped.md", ".all.md", ".all.csv"]:
    #    if os.path.exists(outPath + fname):
    #        os.remove(outPath + fname)
    # create csv and md files for books based on settings:
    #for book in bookList:
    #    settings = writeBook(book, settings, outPath)

    # TODO: track which books from bookList we don't use... (to notify user)
    #bookList = ClippyKindle.parseJsonFile(args.json_file)
    skippedMD = outPath + ".skipped.md" # same for every group
    if os.path.exists(skippedMD):       # remove file we will be appending to
        os.remove(skippedMD)
    # TODO: store (optional) combined filename in settings for each group

    warnings = 0
    for groupName in settings:
        #print("at group: " + groupName)
        outputMD = (settings[groupName]["outputMD"] == True)    # whether to output md file for books in group
        outputCSV = (settings[groupName]["outputCSV"] == True) # whether to output csv file for books in group
        # filenames for combined output (in addition to seprate files, combine everything in group)
        combinedMD = outPath + ".{}.md".format(groupName)
        combinedCSV = outPath + ".{}.csv".format(groupName)

        # loop over books in this group
        for i in range(len(settings[groupName]["books"])):
            if i == 0:
                # remove files we will be appending to
                if os.path.exists(combinedMD):
                    os.remove(combinedMD)
                if os.path.exists(combinedCSV):
                    os.remove(combinedCSV)

            bookName = settings[groupName]["books"][i]["name"]
            chapters = settings[groupName]["books"][i]["chapters"]

            #print("at book: " + bookName)
            if not bookName in bookMap:
                print("WARNING: skipping book '{}' not found in file '{}'".format(bookName, args.settings))
                warnings += 1
                continue
            if bookMap[bookName]["used"] == True:
                print("WARNING: book '{}' found in multiple groups in file '{}'".format(bookName, args.settings))
                warnings += 1
                continue
            bookMap[bookName]["used"] = True

            bookObj = bookMap[bookName]["obj"] # Book object from collection
            fname = bookObj.getName().replace("/", "|") # sanitize for output filename
            outPathMD = "{}{}.md".format(outPath, fname)
            outPathCSV = "{}{}.csv".format(outPath, fname)

            if outputMD:
                # write markdown file
                mdStr = jsonToMarkdown(bookObj.toDict(), chapters)
                with open(outPathMD, 'w') as f:
                    f.write(mdStr)
                print("created: '{}'".format(outPathMD))
                with open(combinedMD, 'a+') as f: # append or create file
                    f.write(mdStr)
            if outputCSV:
                # write csv file
                with open(outPathCSV, 'w') as f:
                    csv.writer(f).writerows(bookObj.toCSV())
                print("created: '{}'".format(outPathCSV))
                with open(outPath + ".all.csv", 'a+') as f:  # append or create file
                    csv.writer(f).writerows(bookObj.toCSV())

            # append md for all files that would be entirely skipped to a single file for reference
            if not outputMD and not outputCSV:
                with open(skippedMD, 'a+') as f: # append or create file
                    f.write(jsonToMarkdown(bookObj.toDict(), chapters))

    #for bookName in bookList:
    for bookName in bookMap:
        if bookMap[bookName]["used"] == False:
            print("WARNING: book '{}' not found in settings file '{}'".format(bookName, args.settings))
            warnings += 1
    if warnings != 0:
        print("\nFinished with {} warnings".format(warnings))


    ### tmp changes
    # iterate over groups (e.g. "csvOnly" "both", "mdOnly", "skip")
    #for group in settings:
    #    print("----\n")
    #    print(group)
    #    #for bookName in settings[group]:
    #    for i in range(len(settings[group])):
    #        bookName = settings[group][i]
    #        settings[group][i] = {
    #            "name": bookName,
    #            "printChapterNumber": True,
    #            "chapters": []
    #        }
    #        print(bookName)
    #        #settings[group][
    ###

    # update settings.json
    if args.settings != None: # TODO: should we check (settings != None) instead
        with open(args.settings, 'w') as f:
            json.dump(settings, f, indent=2) # write indented json to file
        print("\nSettings stored in '{}'".format(args.settings))
    #########################################

    exit(0)


    ########## original marky ###############
    #########################################
    ## read json from file:
    #with open(args.json_file) as f:
    #    jsonData = json.load(f)
    ## convert json for each book to markdown and write to file:
    #for bookData in jsonData:
    #    markdownStr = jsonToMarkdown(bookData)  # convert to markdown string
    #    fname = bookData["title"]
    #    fname += "" if bookData["author"] == "" else " by {}".format(bookData["author"])
    #    fname = fname.replace("/", "|")
    #    outPath = args.out_folder + ("" if args.out_folder.endswith("/") else "/") + fname + ".md"

    #    # TODO: check if file already exists
    #    with open(outPath, 'w') as out_file:
    #        out_file.write(markdownStr)
    #    print("created '{}'".format(outPath))
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
