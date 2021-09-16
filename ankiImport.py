#!/usr/bin/env python3
#################################################
# Imports cards into anki from csv files.
# Based on https://www.juliensobczak.com/write/2020/12/26/anki-scripting-for-non-programmers.html
#
# if desired, first create test directory (and open anki):
#   mkdir ~/AnkiTest && anki -b ~/AnkiTest
#################################################

import os
import csv
from anki.storage import Collection

# variables to set:
#################################################
COLLECTION_PATH = os.path.join(os.path.expanduser('~'), '.local/share/Anki2/User 1/collection.anki2')
#COLLECTION_PATH = os.path.join(os.path.expanduser('~'), 'AnkiTest/DEV 1 (copy)/collection.anki2')
DECK_NAME = 'My - Vocab'
MODEL_NAME = 'Basic (and reversed card)' # or 'Basic'
AUTOSAVE = False # whether to prompt before saving Anki changes

#COLLECTION_PATH = os.path.join(os.path.expanduser('~'), 'AnkiTest/User 1/collection.anki2')
#DECK_NAME = 'Default'
#################################################

def main():
    # import spanish vocab
    csvPath = os.path.join(os.path.expanduser('~'), 'notes/books/0.COMBINED-spanish.csv')
    importFromCsv(csvPath, ['world::lang::es'])

    # import portuguese vocab
    csvPath = os.path.join(os.path.expanduser('~'), 'notes/books/0.COMBINED-portuguese.csv')
    importFromCsv(csvPath, ['world::lang::pt'], preprocessPortuguese)

def identityFunc(fields):
    """identify function, returns the provided tuple of fields"""
    return fields

# TODO: create preprocessor do text to speech with google:
#   (allow user to provide a list of preprocessors to be run in order so this on can run first...)
#   https://console.cloud.google.com/apis/credentials?project=anki-326018

def preprocessPortuguese(fields):
    """tweak card fields as desired for portuguese vocab"""
    return ("{} [P]".format(fields[0]), "{} -> [P]".format(fields[1]))

def importFromCsv(csvPath, tags=[], preprocessor=identityFunc):
    """
    Params:
        csvPath (str): path to csv file to open
        preprocess (function): function taking a tuple of fields and returning a new tuple
        tags (str[]): list of tags (if any) to add to created cards
    """
    if not os.path.isfile(COLLECTION_PATH):
        print("COLLECTION_PATH doesn't exist: '{}'".format(COLLECTION_PATH))
    if not os.path.isfile(csvPath):
        print("csvPath doesn't exist: '{}'".format(csvPath))

    print("Using collection: '{}'".format(COLLECTION_PATH))
    col = Collection(COLLECTION_PATH, log=True) # load anki collection

    model = col.models.by_name(MODEL_NAME) # 'Basic'
    # set the active deck and model type
    # print(col.decks.all_names_and_ids()) # list of all decks
    deck = col.decks.by_name(DECK_NAME)
    col.decks.select(deck['id'])
    col.decks.current()['mid'] = model['id']

    # create cards from csv file
    print("reading csv: '{}'\n".format(csvPath))
    count = -1 
    createdCards = 0
    with open(csvPath, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            count += 1
            if count == 0: # skip header
                print("skipping file header: " + str(row) + "\n")
                continue
            if row[0] == '' and row[1] == '':
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
            col.add_note(note, deck['id'])
            createdCards += 1

    # save changes
    print("\n\n---------------------------------")
    print("Collection: '{}'".format(COLLECTION_PATH))
    print("Created {} new cards - '{}' in deck '{}'".format(createdCards, MODEL_NAME, DECK_NAME))
    if AUTOSAVE or input("\nSave changes? (y/n): ".format(createdCards)).lower().strip() in ('y','yes'):
        col.save()
        print("changes saved!")
    else:
        print("no changes saved.")
    print("---------------------------------\n\n")

if __name__ == "__main__":
    main()
