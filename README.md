# ClippyKindle
* The program `clippy.py` will parse a "My Clippings.txt" file from a kindle and outputs it in a json format.
* The program `marky.py` will parse the json file outputted by `clippy.py` and create a markdown file for each book therein.
---

### Usage:
````bash
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt

mkdir -p out
# parse clippings and store in json file 'collection.json':
#   also defaults to outputting a .md and .csv file for each book found in "My Clippings.txt"
./clippy.py "My Clippings.txt" out/
````
* NOTE: To customize the format of the outputted markdown files simply edit the function `jsonToMarkdown()` in `marky.py`.
* note: if you ever rename or move this folder, you have to delete/recreate the `env/` folder for it to work

### Having Issues?
> This program is designed to explicitly report any errors parsing the clippings file if a provided file has a format issue. The hope is that it will be easy to identify the issue and fix the file or tweak this program.
* This program was designed/tested on the "My Clippings.txt" file from my Amazon Kindle Paperwhite running firmware: `Kindle 5.9.5.1`
* Feel free to [submit an issue](https://github.com/dangbert/clippy-kindle/issues/new) and include the section of your clippings file that failed, and any information about your kindle.

---
### Inherent Limitations with "My Clippings.txt":
* deleting or undoing a highlight in the book doesn't delete it from "My Clippings.txt" :(
  * However clippy.py will automatically detect and remove duplicate highlights, notes, and bookmarks
* TODO: see if highlighting a section and selecting "note" creates both a note and a highlight for that text?
---
### Resources:
* see "Google Books" section of [this](https://medium.com/@sawyerh/how-i-export-process-and-resurface-my-kindle-highlights-addc9de9af1a) for info on automating the download of the book's cover, etc...

### Why I made this?
I tried several programs made by others but they had issues parsing my kindle's "My Clippings.txt" file so I made my own.  Also I wanted to have more control of the removal of duplicates and formatting of the outputted markdown file.

Programs I tried that didn't work for me personally:
* [fyodor - rccavalcanti](https://github.com/rccavalcanti/fyodor)
* [kindle_note_parser - bfreskura](https://github.com/bfreskura/kindle_note_parser)
* [kindle-highlight-parser - honza](https://github.com/honza/kindle-highlight-parser)

### Useful:
````bash
# list all pip requirements in environment to a file:
pip3 freeze --local > requirements.txt
````
