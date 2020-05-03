# ClippyKindle
* The program `clippy.py` will parse a "My Clippings.txt" file from a kindle and convert it to a json file.
* The program `marky.py` will parse the json file outputted by `clippy.py` and create a markdown and csv file for each book therein.
  * Outputted markdown files are a way to conveniently see all your highlights / notes / bookmarks for a book in one place.
  * Ouputted csv files can be used for additional purposes such as creating flashcards using your highlight / note pairs.
---

### How to use:
````bash
# install python requirements:
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt

# parse clippings and store them in a new file called 'collection.json':
./clippy.py "My Clippings.txt"

# now create a markdown and csv file for each book in your collection:
mkdir output
./marky.py collection.json output/
````

* Example program output:
````txt
./clippy.py "My Clippings.txt"
Parsing file: 'My Clippings.txt'

Finished parsing data from 48 books!
Removing duplicates (this may take a few minutes)...
Wrote all parsed data to: './collection.json'


./marky.py collection.json output/
No settings file provided, using defaults (creating both a .md and .csv file for every book)
Or define custom settings now instead (y/n)? n
Save settings to file for later use (y/n)? n
  
Outputting files based on selected settings...
created: 'output/Fahrenheit 451: A Novel by Bradbury, Ray.md'
created: 'output/Fahrenheit 451: A Novel by Bradbury, Ray.csv'
created: 'output/The 4 Hour Workweek.md'
created: 'output/The 4 Hour Workweek.csv'
created: 'output/Encuentro en el Ártico by Eoin Colfer.md'
created: 'output/Encuentro en el Ártico by Eoin Colfer.csv'
...
````

* If you elect to "define custom settings now" when running marky.py, you will be prompted to define for each book whether you want a markdown file outputted, and/or a csv file, or nothing outputted at all.
  * To do this you will be prompted to place each book in one of the settings groups: "csvOnly", "both", "mdOnly", or "skip"
  * If you elect to save your defined settings, you can reuse your settings next time you run marky.py by including the additional flag `--settings settings.json`.  e.g. `./marky.py collection.json output/ --settings settings.json`
* You can also run `./clippy.py` and `./marky.py` with no additional parameters to see a list of all command line options available.
* NOTE: To customize the format of the outputted markdown files simply edit the function `jsonToMarkdown()` in `marky.py`.

### CSV output files:
The following is an example csv file output (shown as a table) for a spanish book I'm reading called "Encuentro en el Ártico"
* While reading on my Kindle I highlighted words/sentences that were new to me, and I typed each highlight's english translations as a note.

| highlight                                      | associated_note                             | highlight_loc | note                                        | note_loc | bookmark_loc | 
|------------------------------------------------|---------------------------------------------|---------------|---------------------------------------------|----------|--------------| 
| chantajear                                     | To blackmail                                | 4-4           | To blackmail                                | 4        |              | 
| vencido                                        | Beaten/defeated                             | 25-25         | Beaten/defeated                             | 25       |              | 
| el cabecilla                                   |                                             | 30-30         | Course, tack, route, direction              | 32       |              | 
| rumbo                                          | Course, tack, route, direction              | 32-32         | Aghast, thunderstruck, stunned              | 55       |              | 
| pasmado.                                       | Aghast, thunderstruck, stunned              | 55-55         | Marksmanship, aiming, aim                   | 61       |              | 
| puntería                                       | Marksmanship, aiming, aim                   | 61-61         |                                             |          |              |  

If you want to create flashcards using this output, the first two columns are the only ones you need to care about.

* You can see that highlights with no note text have their "associated_note" field show up as blank.
  * If this is the case you can double check that no note exists for it (meaning marky.py had trouble associating the two) by looking in the "note" column, which always contains every note made in the book in order.

### Having Issues?
> This program is designed to explicitly report any errors parsing the clippings file if a provided file has a format issue. The hope is that it will be easy to identify the issue and fix the file or tweak this program.
* This program was designed/tested on the "My Clippings.txt" file from my Amazon Kindle Paperwhite running firmware: `Kindle 5.9.5.1`
* Feel free to [submit an issue](https://github.com/dangbert/clippy-kindle/issues/new) and include the section of your clippings file that failed, and any information about your kindle.

---
### Inherent Limitations with "My Clippings.txt":
* deleting or undoing a highlight in the book doesn't delete it from "My Clippings.txt" :(
  * However clippy.py will automatically detect and remove duplicate highlights, notes, and bookmarks
    * This means that if you make a highlight that you want to adjust to be shorter or longer, you can delete in on the kindle and re-highlight the desired area.
    * clippy.py will attempt to detect and remove sets of duplicates when it runs, keeping always the latest highlights and notes made while reading.
    * You can disable the removal of duplicates by running `./clippy.py "My Clippings.txt" --keep-dups`
    
---
### Why I made this?
I tried several programs made by others but they had issues parsing my kindle's "My Clippings.txt" file so I made my own.  Also I wanted to have more control of the removal of duplicates and formatting of the outputted markdown file.

Programs I tried that didn't work for me personally:
* [fyodor - rccavalcanti](https://github.com/rccavalcanti/fyodor)
* [kindle_note_parser - bfreskura](https://github.com/bfreskura/kindle_note_parser)
* [kindle-highlight-parser - honza](https://github.com/honza/kindle-highlight-parser)

### Further Info Resources:
* NOTE: To customize the format of the outputted markdown files simply edit the function `jsonToMarkdown()` in `marky.py`.
