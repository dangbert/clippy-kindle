# ClippyKindle

Under Development (not finished yet)

* This program will parse a "My Clippings.txt" file from a kindle and outputs it in a json format
* Then another program could convert the json file into markdown as desired

### Usage:
````bash
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt

./clippy.py My\ Clippings.txt out/
````
* note: if you ever rename or move this folder, you have to delete/recreate the `env/` folder for it to work

### Useful:
````bash
pip3 freeze --local > requirements.txt
````

### Having Issues?
> This program is designed to explicitly report any errors parsing the clippings file if a provided file has a format issue. The hope is that it will be easy to identify the issue and fix the file or tweak this program.
* This program was designed/tested on the "My Clippings.txt" file from my Amazon Kindle Paperwhite running firmware: `Kindle 5.9.5.1`
* Feel free to [submit an issue](https://github.com/dangbert/clippy-kindle/issues/new) and include the section of your clippings file that failed, and any information about your kindle.



---
### Resources:
* see "Google Books" section of [this](https://medium.com/@sawyerh/how-i-export-process-and-resurface-my-kindle-highlights-addc9de9af1a) for info on automating the download of the book's cover, etc...

### Programs I tried that didn't work for me personally:
* [fyodor - rccavalcanti](https://github.com/rccavalcanti/fyodor)
* [kindle_note_parser - bfreskura](https://github.com/bfreskura/kindle_note_parser)
* [kindle-highlight-parser - honza](https://github.com/honza/kindle-highlight-parser)
