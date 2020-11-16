# ClippyKindle
[![Documentation Status](https://readthedocs.org/projects/clippy-kindle/badge/?version=latest)](https://clippy-kindle.readthedocs.io/en/latest/?badge=latest)

* The program `clippy.py` will parse a "My Clippings.txt" file from a kindle and convert it to a json file.
* The program `marky.py` will parse the json file outputted by `clippy.py` and create a markdown and csv file for each book therein.
  * Outputted markdown files are a way to conveniently see all your highlights / notes / bookmarks for a book in one place.
  * Ouputted csv files can be used for additional purposes such as creating flashcards using your highlight / note pairs.
---

[<img src="https://i.imgur.com/mDjy5VL.png" alt="video tutorial" width="600">](https://youtu.be/3DoNWYdSNcs)


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
No settings file provided, using defaults (creating both a .md and .csv file for every book)...
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
  * To do this you will be prompted to place each book in one of the settings groups: "csvOnly", "both", "mdOnly", or "skip".
  * If you elect to save your defined settings, you can reuse your settings next time you run marky.py by including the additional flag `--settings settings.json`.  e.g. `./marky.py collection.json output/ --settings settings.json`
* NOTE: To customize the format of the outputted markdown files simply edit the function `jsonToMarkdown()` in `marky.py`.
* **You can also run `./clippy.py` and `./marky.py` with no additional parameters to see a list of all command line options available.**

### CSV output files:
The following is an example csv file output (shown as a table) for a spanish book I'm reading called "Encuentro en el Ártico".
* While reading on my Kindle I highlighted words/sentences that were new to me, and I typed each highlight's english translation as a note.
  * [I installed a Spanish->English dictionary on my kindle](http://blog.mikeasoft.com/2011/01/05/free-as-in-gpl2-translation-dictionaries-for-the-kindle/) which helps with adding the english translation as a note (if needed I'll  occasionally look up words on my phone to help with adding the english translation note).

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

### Creating Anki Flashcards From a CSV File:
1. Edit your csv file in a spreadsheet program to have just two columns with no headers:

|                                                |                                             | 
|------------------------------------------------|---------------------------------------------| 
| chantajear                                     | To blackmail                                | 
| vencido                                        | Beaten/defeated                             | 
| el cabecilla                                   | The ringleader                              | 
| rumbo                                          | Course, tack, route, direction              | 
| pasmado.                                       | Aghast, thunderstruck, stunned              | 
| puntería                                       | Marksmanship, aiming, aim                   | 

  * Also manually populate any missing notes as needed so flashcards can have two sides.

2. [Download Anki](https://apps.ankiweb.net/)  for your computer.

3. Click *File* > *Import* in Anki and select your csv file.
<img src="https://i.imgur.com/K9FC05o.png" alt="main view" width="700">

  * By using the flashcard type *"Basic (and reversed card)"* (set in the top left), each row in the csv will essentially become two separate flashcards.  One with the spanish side on the front side, and another with the english side as the front.
  * In the top right select the name of the deck you want to place the cards in (or create a new one).
  * Lastly click "Import" to finish importing your flashcards into your Anki deck.
4. I created an account on [ankiweb.net](https://ankiweb.net/) which allows me to "Sync" me decks to the Anki app on my phone so I can study my flashcards there.

#### Pro Tip for Creating Flashcards:
* In my settings.json file for marky.py, I added an additional custom settings groups, and moved my spanish language books to this section as shown below:
````json
"spanish": {
  "outputMD": false,
  "outputCSV": false,
  "combinedMD": "",
  "combinedCSV": "COMBINED-spanish.csv",
  "books": [
    {
      "name": "Los juegos del hambre by Suzanne Collins",
      "chapters": []
    },
    {
      "name": "Encuentro en el \u00c1rtico by Eoin Colfer",
      "chapters": []
    }
  ]
},
````
  * By setting the field *"combinedCSV"* to a filename, the csv data for all the books in that group will be also be combined and outputted into a single csv file.
    * (I then set *"outputCSV"* to false for these groups as I don't care about additionally having a separate csv file for each book).

* My full workflow is to every now and then, copy the latest "My Clippings.txt" from my Kindle, and then run:
````bash
./clippy.py "My Clippings.txt"
./marky.py collection.json output/ --settings settings.json --latest-csv --update-outdate
````
* NOTE:
  * the flag `--update-outdate` saves the date of the most recently added item (highlight, note, or bookmark) in each book to my settings.json
  * and the flag `--latest-csv` forces the outputted csv files to only include items that were added since the last time I ran marky.py (with the `--update-outdate` flag)
* In this way, the outputted csv file(s) will only ever contain newly added content (since the last time I created flashcards).
  * This allows me to easily create my latest flashcards even if I'm only part of the way through a book- and later I can continue adding new highlight/notes in the book to become future flashcards.
  

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

### Other related projects
* [kindle_vocab_anki - wzyboy](https://github.com/wzyboy/kindle_vocab_anki)
* [Kindle Highlights Import (Anki Extension)](https://ankiweb.net/shared/info/1525149970)
