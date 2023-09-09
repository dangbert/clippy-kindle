#!/usr/bin/env python3
#################################################
# Imports cards into anki from csv files.
# Based on https://www.juliensobczak.com/write/2020/12/26/anki-scripting-for-non-programmers.html
#
# if desired, first create test directory (and open anki):
#   mkdir ~/AnkiTest && anki -b ~/AnkiTest
#################################################

import sys
import os
import csv
from anki.storage import Collection
import argparse

# variables to set:
#################################################
MODEL_NAME = "Basic (and reversed card)"  # or 'Basic'
AUTOSAVE = False  # whether to prompt before saving Anki changes
#################################################

#  (and allow either the deck name or ID to be specified)
SRC_DIR = os.path.join(os.path.expanduser("~"), "notes/books/")


def main():
    parser = argparse.ArgumentParser(
        description="Creates/imports Anki cards from csv files outputted by marky.py"
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Don't ask for confirmation before creating Anki cards",
    )
    # COLLECTION_PATH = os.path.join(os.path.expanduser('~'), 'AnkiTest/User 1/collection.anki2')
    parser.add_argument(
        "-ad",
        "--anki-dir",
        type=str,
        help="Path to User's Anki dir",
        default=os.path.join(os.path.expanduser("~"), ".local/share/Anki2/User 1/"),
    )
    # parser.add_argument(
    #    "-s",
    #    "--settings",
    #    type=str,
    #    help="(string) path to json file containing settings for parsing books (optional)",
    #    required=True,
    # )

    # if len(sys.argv) == 1:
    #     parser.print_help(sys.stderr)
    #     exit(1)
    args = parser.parse_args()
    assert os.path.isdir(args.anki_dir), f"Directory not found: {args.anki_dir}"
    colPath = os.path.join(args.anki_dir, "collection.anki2")

    # TODO: pull this information out of settings.json instead:
    INDEX = [
        {
            "csv": "0.COMBINED-spanish.csv",
            "deck": "My - Vocab::Spanish",
            "tags": ["world::lang::es"],
        },
        {
            "csv": "0.COMBINED-portuguese.csv",
            "deck": "My - Vocab::portuguese",
            "tags": ["world::lang::pt"],
            "preprocess": preprocessPortuguese,  # (optional field)...
        },
        {
            "csv": "0.COMBINED-french.csv",
            "deck": "My - Lang::French",
            "tags": ["world::lang::fr"],
        },
        {
            "csv": "0.COMBINED-german.csv",
            "deck": "My - Lang::German",
            "tags": ["world::lang::de"],
        },
        {
            "csv": "0.COMBINED-greek.csv",
            "deck": "My - Lang::Greek",
            "tags": ["world::lang::el"],
        },
        {
            "csv": "0.COMBINED-turkish.csv",
            "deck": "My - Lang::Turkish",
            "tags": ["world::lang::tr"],
        },
        {
            "csv": "0.COMBINED-dutch.csv",
            "deck": "My - Lang::Dutch",
            "tags": ["world::lang::nl"],
        },
    ]

    for entry in INDEX:
        csvPath = os.path.join(SRC_DIR, entry["csv"])
        if not os.path.exists(csvPath):
            print("skipping non-existent file: {}".format(csvPath))
            continue
        preprocess = entry["preprocess"] if "preprocess" in entry else identityFunc
        importFromCsv(
            colPath,
            csvPath,
            entry["deck"],
            entry["tags"],
            preprocess,
            confirm=not args.yes,
        )


def identityFunc(fields):
    """identify function, returns the provided tuple of fields"""
    return fields


# TODO: create preprocessor do text to speech with google:
#   (allow user to provide a list of preprocessors to be run in order so this on can run first...)
#   https://console.cloud.google.com/apis/credentials?project=anki-326018


def preprocessPortuguese(fields):
    """tweak card fields as desired for portuguese vocab"""
    return ("{} [P]".format(fields[0]), "{} -> [P]".format(fields[1]))


def importFromCsv(
    colPath: str,
    csvPath: str,
    deckName: str,
    tags=[],
    preprocessor=identityFunc,
    confirm: bool = True,
):
    """
    Params:
        colPath (str): path to user's collection.anki2 file
        csvPath (str): path to csv file to open
        preprocess (function): function taking a tuple of fields and returning a new tuple
        tags (str[]): list of tags (if any) to add to created cards
    """
    if not os.path.isfile(colPath):
        print("COLLECTION_PATH doesn't exist: '{}'".format(colPath))
        exit(1)
    if not os.path.isfile(csvPath):
        print("csvPath doesn't exist: '{}'".format(csvPath))
        exit(1)

    print("Using collection: '{}'".format(colPath))
    col = Collection(colPath, log=True)  # load anki collection

    model = col.models.by_name(MODEL_NAME)  # 'Basic'
    # set the active deck and model type
    # print(col.decks.all_names_and_ids()) # list of all decks
    deck = col.decks.by_name(deckName)
    if deck is None:
        print(f"ERROR: deck not found '{deckName}'")
        exit(1)
    col.decks.select(deck["id"])
    col.decks.current()["mid"] = model["id"]

    # create cards from csv file
    print("reading csv: '{}'\n".format(csvPath))
    count = -1
    createdCards = 0
    with open(csvPath, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            count += 1
            if count == 0:  # skip header
                print("skipping file header: " + str(row) + "\n")
                continue
            if row[0] == "" and row[1] == "":
                print("skipping empty row (count = {})".format(count))
                continue

            fields = (row[0], row[1])
            fields = preprocessor(fields)
            note = col.newNote()
            print(fields)
            for i in range(len(fields)):
                note.fields[i] = fields[i]

            for tag in tags:
                note.add_tag(tag)

            # note: don't use col.addNote (uses a deck ID sourced from model rather than currently selected deck)
            #   see env/lib/python3.8/site-packages/anki/collection.py:addNote()
            col.add_note(note, deck["id"])
            createdCards += 1

    # save changes
    print("\n\n---------------------------------")
    print("Collection: '{}'".format(colPath))
    print(
        "Created {} new cards - '{}' in deck '{}'".format(
            createdCards, MODEL_NAME, deckName
        )
    )
    if createdCards > 0:
        if AUTOSAVE or input(
            "\nSave changes? (y/n): ".format(createdCards)
        ).lower().strip() in ("y", "yes"):
            col.save()
            print("changes saved!")
        else:
            print("no changes saved.")
    print("---------------------------------\n\n")


if __name__ == "__main__":
    main()
