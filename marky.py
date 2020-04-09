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

    # write to file as test to see that data is the same:
    #outData = []
    #for book in bookList:
    #    book.sort(removeDups=False)
    #    outData.append(book.toDict())
    #outPathJson = getAvailableFname(outPath + "collection", ".json")
    #with open(outPathJson, 'w') as f:
    #    json.dump(outData, f, indent=2) # write indented json to file
    #    print("Wrote all parsed data to: '{}'\n".format(outPathJson))

    #############################################
    ####### from clippy.py:
    #############################################
    # offer to create a settings file if not provided
    if settings == None:
        print("No settings file provided... defaulting to creating both a .md and .csv file for each book.")
        if answerYesNo("OR create settings file now (y/n)? "):
            args.settings = getAvailableFname("settings", ".json")
            settings = {"csvOnly": [], "both": [], "mdOnly": [], "skip": []}

    # remove files we will be appending to:
    for fname in [".skipped.md", ".all.md", ".all.csv"]:
        if os.path.exists(outPath + fname):
            os.remove(outPath + fname)

    # create csv and md files for books based on settings:
    for book in bookList:
        settings = writeBook(book, settings, outPath)

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

def jsonToMarkdown(data):
    """
    parameters:
        data (dict): dict holding data about a book

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
    for item in data["items"]:
        if "content" in item:  # escape all '*' as '\*'
            item["content"] = item["content"].replace('*', '\*')

        if item["type"] == "highlight":
            md += "* {} -- [{} {}]\n\n".format(item["content"], locType, item["loc"])
        if item["type"] == "note":
            md += "> {} -- [{} {}]\n\n".format(item["content"], locType, item["loc"])
        if item["type"] == "bookmark":
            md += "* [Bookmark -- {} {}]\n\n".format(locType, item["loc"])
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

def writeBook(book, settings, outPath):
    """
    writes provided Book to md and/or csv file according to provided settings object
    prompts user for input if settings == None
    parameters:
        book (Book): Book object to be (potentially) written to a md and csv file
        settings (dict or None): settings object to read/modify
        outPath (str): string path of folder to write output files
    return (dict): returns (potentially modified) settings object
    """
    outPath +=  "" if outPath.endswith("/") else "/"
    # predefined settings categories (keys in format "<bool_write_md><bool_write_csv>")
    CATEGORIES = {
        "00": "skip",    # create NO files for book
        "10": "mdOnly",  # create a .md file for book
        "01": "csvOnly", # create a .csv file for book
        "11": "both"     # create a .md and .csv file for book
    }

    bookKey = ""
    if settings == None:
        bookKey = "11" # default to generating both for book if settings not provided
    else:
        for key, value in CATEGORIES.items():
            if book.getName() in settings[value]:
                if bookKey != "":
                    print("ERROR: book '{}' appears under multiple categories ('{}' and '{}'"
                            .format(book.getName), bookKey, key)
                    print("\taborting... please correct the settings file")
                    exit(1)
                bookKey = key
        if bookKey == "":
            # prompt user to define settings
            print("\nFound new book: {}".format(book.getName()))
            writeMD = answerYesNo("\tCreate markdown file (y/n)? ")
            writeCSV = answerYesNo("\tCreate csv file (y/n)? ")
            bookKey = "{}{}".format(int(writeMD), int(writeCSV))
            settings[CATEGORIES[bookKey]].append(book.getName())

    fname = book.getName().replace("/", "|") # sanitize for output filename
    if bookKey[0] == "1":
        # write markdown file
        mdStr = jsonToMarkdown(book.toDict())
        outPathMD = "{}{}.md".format(outPath, fname)
        with open(outPathMD, 'w') as f:
            f.write(mdStr)
        print("created: '{}'".format(outPathMD))
        with open(outPath + ".all.md", 'a+') as f: # append or create file
            f.write(mdStr)
    if bookKey[1] == "1":
        # write csv file
        outPathCSV = "{}{}.csv".format(outPath, fname)
        with open(outPathCSV, 'w') as f:
            csv.writer(f).writerows(book.toCSV())
        print("created: '{}'".format(outPathCSV))
        with open(outPath + ".all.csv", 'a+') as f:  # append or create file
            csv.writer(f).writerows(book.toCSV())
    if CATEGORIES[bookKey] == "skip":
        with open(outPath + ".skipped.md", 'a+') as f: # append or create file
            f.write(jsonToMarkdown(book.toDict()))

    return settings

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
