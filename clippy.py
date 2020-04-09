#!/usr/bin/env python3

import os
import sys
import argparse
import json

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz

from ClippyKindle import ClippyKindle

def main():
    # parse args:
    parser = argparse.ArgumentParser(description='Parses a "My Clippings.txt" file from a kindle')
    parser.add_argument('file_name', type=str, help='(string) path to kindle clippings file e.g. "./My Clippings.txt"')
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output parsed clippings')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    # parse file:
    bookList = ClippyKindle.parse(args.file_name)     # list of Book objects

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

if __name__ == "__main__":
    main()
