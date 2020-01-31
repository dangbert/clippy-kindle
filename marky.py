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

    parser = argparse.ArgumentParser(description='Parses a "My Clippings.txt" file from a kindle')
    parser.add_argument('file_name', type=str, help='(string) path to json file created by clippy.py (e.g. "./out.json")')
    #parser.add_argument('out_folder', type=str, help='(string) path of folder to output parsed clippings')
    # (args starting with '--' are made optional)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()
    outPath = "out.md"

    with open(args.file_name) as f:
        jsonData = json.load(f)

    #jsonData = jsonData[0] # for now
    #print(type(jsonData))

    #jsonData = jsonData[0] # for now just use first book
    markdownStr = jsonToMarkdown(jsonData)

    with open(outPath, 'w') as out_file:
        out_file.write(markdownStr)
    print("wrote data to {}".format(outPath))

def jsonToMarkdown(data):
    #pp = pprint.PrettyPrinter(indent=4)
    print(data["title"])

    md = ""

    titleStr = data["title"]
    titleStr += "" if data["author"] == None else " by {}".format(data["title"])

    # TODO: add dates for first and last highlight/note/bookmark...
    # and maybe stats on number of each type (TODO: have clippy.py store these in the json)
    md += "# {}\n---\n\n".format(titleStr)
    for item in data["items"]:
        if item["type"] == "highlight":
            md += "> {}\n\n".format(item["content"])
        if item["type"] == "note":
            md += "* {}\n\n".format(item["content"])
        if item["type"] == "bookmark":
            pass

    #pp.pprint(jsonData)
    #print(jsonData["title"])
    #print(jsonData["author"])
    return md

if __name__ == "__main__":
    main()
