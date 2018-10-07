# bucephalus

This repository is only a test. [There is nothing to see here](https://www.youtube.com/watch?v=V2MIvUx9uiQ).

Goal: [futuristic](https://abstrusegoose.com/440) paperless society or something.

## IAQ (Infrequently Asked Questions)
### Is Bucephalus feature complete?
No.

### Is Bucephalus stable?
No.

### Is Bucephalus documented?
No.

### Is Bucephalus suitable for my needs?
No.

### Should I use Bucephalus for X?
No.

## Installation
After cloning, run `sudo ./install.sh` in the root directory; the relevant files will be
installed into `/opt/bucephalus`, and wrapper shell scripts will be deposited into `/usr/local/bin`.

All data files will be placed into `~/bucephalus` on run. Yes, this directory is not hidden. Yes,
you can go fiddling around with things in it. Should you do that? Probably not, but you'll likely
need to when something goes wrong.

## Usage
After installation, at the time of writing the following commands will be available:

* `bucserve` - start the web server.
* `bucadd <filename> <title> <author> <tag1> ... <tagN>` (tags are optional) - add the given file to the bucephalus database.
* `bucrm <identifier` - remove the given database entry permanently and all the files associated with it. The identifier could be reused, I don't know.
* `bucvac <filename>` - vacuum up the given TeX source file which includes a section of JSON at the start, run it through the appropriate template (templates are installed in `/opt/bucephalus/prototypes`, and bucvac will also look in `~/bucephalus/prototypes`; the template chosen is given by the `Buc_hp` JSON key), and add it to the server after running XeLaTeX on it twice.

Some of these commands will check that you put sane values in. Some of them won't. Finding out which is which is a fun little game
you can play if you don't care about your data. *If these commands go wrong, they may trample your database.*

If you add two files with the same name on the same day, the later one will overwrite the earlier one and will take the same ID. This is
by design, so that you don't end up with several slightly different copies of the same file. Todo: add a switch to disable this.

## Plan.
1. Prototype template system for TeX (Done)
2. Storage of files by date for retrieval by ID in both source and PDF form where applicable. (Done.)
3. REST api and web interface barebones (Done)
4. Nice system to add files
4. Command to update existing files (todo) and delete old version. (`bucrm` can do deletions now)
4. Tag system (done)
5. Search
5. Extension from TeX to Geogebra files?
6. Scan-to-email-to-upload automatically?

## Dependencies
* [tinydb](https://pypi.org/project/tinydb/)
* [pystache](https://github.com/defunkt/pystache)
* [flask](http://flask.pocoo.org/)

