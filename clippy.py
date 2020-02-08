#!/usr/bin/env python3

import os
import sys
import argparse
import json
import csv

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz

from ClippyKindle import ClippyKindle
from marky import jsonToMarkdown

def main():
    # parse args:
    parser = argparse.ArgumentParser(description='Parses a "My Clippings.txt" file from a kindle')
    parser.add_argument('file_name', type=str, help='(string) path to kindle clippings file e.g. "./My Clippings.txt"')
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output parsed clippings')
    parser.add_argument('--settings', type=str, help='(string) path to json file containing settings for parsing books (optional). If no settings is provided then a .md and .csv file will be created for all books.')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    # read json settings from file:
    settings = None
    if args.settings != None:
        with open(args.settings) as f:
            settings = json.load(f)

    # parse file:
    clippy = ClippyKindle()
    bookList = clippy.parse(args.file_name)     # list of Book objects

    # do post-processing on books (sorting/removing duplicates)
    removeDups = True # TODO: make this a cmd flag
    if removeDups:
        print("Removing duplicates (this may take a few minutes)...")
    outData = []
    for book in bookList:
        book.sort(removeDups=removeDups)
        outData.append(book.toDict())

    # get file name for outputting json data
    outPath = args.out_folder + ("" if args.out_folder.endswith("/") else "/")
    outPathJson = outPath + "collection.json"
    #if os.path.exists(outPathJson):
    #    if not answerYesNo("Overwrite '{}' (y/n)? ".format(outPathJson)):
    #        outPathJson = getAvailableFname(outPath + "collection", ".json")
    with open(outPathJson, 'w') as f:
        json.dump(outData, f, indent=2) # write indented json to file
        print("Wrote all parsed data to: '{}'\n".format(outPathJson))

    # TODO: consider moving code for generating md and csv files all to marky.py...
    # offer to create a settings file if not provided
    if settings == None:
        print("No settings file provided... defaulting to creating both a .md and .csv file for each book.")
        if answerYesNo("OR create settings file now (y/n)? "):
            args.settings = getAvailableFname("settings", ".json")
            settings = {"csvOnly": [], "both": [], "mdOnly": [], "skip": []}

    # create csv and md files for books based on settings
    for book in bookList:
        # write md and/or csv as desired and update settings object
        settings = writeBook(book, settings, outPath)

    # update settings.json
    # TODO: sort each section...
    if args.settings != None:
        with open(args.settings, 'w') as f:
            json.dump(settings, f, indent=2) # write indented json to file
        print("\nSettings stored in '{}'".format(args.settings))

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
    if bookKey[1] == "1":
        # write csv file
        outPathCSV = "{}{}.csv".format(outPath, fname)
        with open(outPathCSV, 'w') as f:
            csv.writer(f).writerows(book.toCSV())
        print("created: '{}'".format(outPathCSV))
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
