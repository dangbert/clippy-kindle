#!/usr/bin/env python3

import os
import sys
import argparse

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz

from ClippyKindle import ClippyKindle

def main():
    # parse args
    parser = argparse.ArgumentParser(description='Parses a "My Clippings.txt" file from a kindle')
    parser.add_argument('file_name', type=str, help='(string) path to kindle clippings file e.g. "./My Clippings.txt"')
    parser.add_argument('out_folder', type=str, help='(string) path of folder to output parsed clippings')
    # (args starting with '--' are made optional)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args = parser.parse_args()

    clippy = ClippyKindle()
    # TODO: have this return the json so we can write it to a file here (and use args.out_folder)
    clippy.parse(args.file_name)


if __name__ == "__main__":
    main()
