#!/usr/bin/env python3
# Parses a "My Clippings.txt" file from a kindle and outputs the data to a json file

import os
import sys
import argparse
import json

from ClippyKindle import ClippyKindle

def main():
    # parse args:
    parser = argparse.ArgumentParser(description='Parses a "My Clippings.txt" file from a kindle and outputs the data to a json file.')
    parser.add_argument('file_name', type=str, help='(string) path to kindle clippings file e.g. "./My Clippings.txt"')
    parser.add_argument('--out-folder', type=str, default='.', help='(string) path of folder to output parsed clippings (default: \'.\')')
    parser.add_argument('--keep-dups', action="store_true", help="When this flag is provided, duplicate highlights/notes/bookmarks will not be detected/removed before outputting to json.")
    parser.add_argument('--separate', action="store_true", help="When this flag is provided, highlights/notes/bookmarks in each book will be written in its separate json file.")
    # TODO: (optionally) provide an existing collection.json, and only have data outside of each book's dateStart and dateEnd appended to that file
    #   lets you delete unwanted items in a book's collection and not have them show up again the next time "My Clippings.txt" is parsed
    #   also lets you get a new kindle and still have your old notes preserved

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    # parse file:
    bookList = ClippyKindle.parseClippings(args.file_name)     # list of Book objects

    if not args.keep_dups:
        print("Removing duplicates (this may take a few minutes)...")

    # get file name for outputting json data
    outPath = args.out_folder + ("" if args.out_folder.endswith("/") else "/")

    for book in bookList:
        # do post-processing on books (sorting/removing duplicates)
        book.sort(removeDups=(not args.keep_dups))
        outData = book.toDict()
        outPathJson = f'{ book.getName() }.json'
        with open(outPathJson, 'w', encoding="utf-8") as f:
            json.dump(outData, f, indent=2, ensure_ascii=False) # write indented json to file
            print("Wrote all parsed data to: '{}'\n".format(outPathJson))


if __name__ == "__main__":
    main()
