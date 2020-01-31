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
./clippy.py "My Clippings.txt" out/  # parse clippings and store in json file
./marky.py out/out.json              # convert json file to markdown file(s)
````
* NOTE: To customize the format of the outputted markdown files simply edit the function `jsonToMarkdown()` in `clippy.py`.
* note: if you ever rename or move this folder, you have to delete/recreate the `env/` folder for it to work

### Having Issues?
> This program is designed to explicitly report any errors parsing the clippings file if a provided file has a format issue. The hope is that it will be easy to identify the issue and fix the file or tweak this program.
* This program was designed/tested on the "My Clippings.txt" file from my Amazon Kindle Paperwhite running firmware: `Kindle 5.9.5.1`
* Feel free to [submit an issue](https://github.com/dangbert/clippy-kindle/issues/new) and include the section of your clippings file that failed, and any information about your kindle.

---
### Inherent Limitations with "My Clippings.txt":
* deleting or undoing a highlight in the book doesn't delete it from "My Clippings.txt" :(
* TODO: see if highlighting a section and selecting "note" creates both a note and a highlight for that text?
* NOTE: I should accept these limitations, write the best parser I can and move on
  * if the user has to manually delete stuff they don't care about from the final webpage that's okay)
  * workflow should be that once the book is finished, the final generated markdown page can be edited and then never should need to be regenerated again...

---
### Resources:
* see "Google Books" section of [this](https://medium.com/@sawyerh/how-i-export-process-and-resurface-my-kindle-highlights-addc9de9af1a) for info on automating the download of the book's cover, etc...

### Programs I tried that didn't work for me personally:
* [fyodor - rccavalcanti](https://github.com/rccavalcanti/fyodor)
* [kindle_note_parser - bfreskura](https://github.com/bfreskura/kindle_note_parser)
* [kindle-highlight-parser - honza](https://github.com/honza/kindle-highlight-parser)

### Useful:
````bash
# list all pip requirements in environment to a file:
pip3 freeze --local > requirements.txt
````
