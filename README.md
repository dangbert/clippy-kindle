# ClippyKindle

Under Development (this doesn't work yet)

* Probably this program will parse a "My Clippings.txt" file and output it to a better format (json)
* Then another program could convert the json file into markdown as desired

### Usage:
````bash
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt

./clippy.py My\ Clippings.txt out/
````

### Useful:
````bash
pip3 freeze --local > requirements.txt
````

### Resources
* see "Google Books" section of [this](https://medium.com/@sawyerh/how-i-export-process-and-resurface-my-kindle-highlights-addc9de9af1a) for info on automating the download of the book's cover, etc...


---
### Programs I tried that didn't work for me personally:
* [fyodor - rccavalcanti](https://github.com/rccavalcanti/fyodor)
* [kindle_note_parser - bfreskura](https://github.com/bfreskura/kindle_note_parser)
* [kindle-highlight-parser - honza](https://github.com/honza/kindle-highlight-parser)
