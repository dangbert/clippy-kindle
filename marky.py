#!/usr/bin/env python3
# converts a json file created by clippy.py into a markdown file

import os
import sys
import argparse
import json

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz
import pprint

def main():
    # parse args

    parser = argparse.ArgumentParser(description='Parses a json file created by clippy.py and outputs a markdown file for each book')
    parser.add_argument('file_name', type=str, help='(string) path to json file created by clippy.py (e.g. "./out.json")')
    # TODO: default to '.' as out_folder if not provided
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output parsed clippings')
    # (args starting with '--' are made optional)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    with open(args.file_name) as f:
        jsonData = json.load(f)


    for bookData in jsonData:
        markdownStr = jsonToMarkdown(bookData)
        titleStr = bookData["title"]
        titleStr += "" if bookData["author"] == None else " by {}".format(bookData["author"])

        outPath = args.out_folder + "/" + titleStr.replace(" ", "-") + ".md"
        # TODO: check if file already exists
        with open(outPath, 'w') as out_file:
            out_file.write(markdownStr)
        print("created '{}'".format(outPath))
        #return # for now just use first book

def jsonToMarkdown(data):
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(jsonData)
    md = ""
    titleStr = data["title"]
    titleStr += "" if data["author"] == None else " by {}".format(data["author"])
    #print("converting '{}'".format(titleStr))

    # TODO: add dates for first and last highlight/note/bookmark...
    # and maybe stats on number of each type (TODO: have clippy.py store these in the json)
    md += "# {}\n---\n\n".format(titleStr)
    for item in data["items"]:
        if "content" in item:  # escape all '*' as '\*'
            item["content"] = item["content"].replace('*', '\*')

        if item["type"] == "highlight":
            md += "> {} -- {} {}\n\n".format(item["content"], item["locType"], item["loc"])
        if item["type"] == "note":
            md += "* {} -- {} {}\n\n".format(item["content"], item["locType"], item["loc"])
        if item["type"] == "bookmark":
            md += "* [Bookmark -- {} {}]\n\n".format(item["locType"], item["loc"])

    return md

if __name__ == "__main__":
    main()
