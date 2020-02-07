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

def main():
    # parse args:
    parser = argparse.ArgumentParser(description='Parses a "My Clippings.txt" file from a kindle')
    parser.add_argument('file_name', type=str, help='(string) path to kindle clippings file e.g. "./My Clippings.txt"')
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output parsed clippings')
    # (args starting with '--' are made optional)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    # parse file:
    clippy = ClippyKindle()
    # TODO: some stuff printed in clippy.parse could be printed here instead
    #       (maybe it should just print errors)...
    bookList = clippy.parse(args.file_name)

    # sort / remove duplicates:
    removeDups = True # TODO: make this a cmd flag
    writeJson  = True # TODO ^
    writeCSV   = True # TODO ^
    if removeDups:
        print("\nRemoving duplicates (this may take a few minutes)...")

    #bookList = [book.sort(removeDups=removeDups) for book in BookList]
    outPath = args.out_folder + ("" if args.out_folder.endswith("/") else "/")
    if writeJson:
        # write data from all books to a single json file:
        outData = []
        for book in bookList:
            # do post-processing on book (sorting/removing duplicates)
            book.sort(removeDups=removeDups)
            outData.append(book.toDict())

        # convert data to json and write to file:
        outPathJson = outPath + "out.json"
        with open(outPathJson, 'w') as f:
            json.dump(outData, f, indent=2) # write indented json to file
            print("\ndumped all parsed data to: '{}'".format(outPathJson))

    for book in bookList:
        if writeCSV:
            # convert data to CSV and write to file:
            fname = book.getName().replace("/", "|")
            outPathCSV = "{}{}.csv".format(outPath, fname)
            with open(outPathCSV, 'w') as f:
                csv.writer(f).writerows(book.toCSV())
            print("created: '{}'".format(outPathCSV))


if __name__ == "__main__":
    main()
