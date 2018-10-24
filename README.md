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
* `bucadd [-h] [-a AUTHOR] FILENAME TITLE TAGS [TAGS ...]` (must have at least one tag, author optional) - add the given file to the bucephalus database.
* `bucfup [-h] FILENAME IDENT` - update the existing file with id IDENT using FILENAME.
* `bucrm <identifier>` - remove the given database entry permanently and all the files associated with it. The identifier could be reused, I don't know.
* `bucvac [-h] [-o OUTPUTFILE] [-u UPDATEIDENT] FILENAME` - vacuum up the given TeX source file which includes a section of JSON at the start, run it through the appropriate template (templates are installed in `/opt/bucephalus/prototypes`, and bucvac will also look in `~/bucephalus/prototypes`; the template chosen is given by the `Buc_hp` JSON key), and add it to the server after running XeLaTeX on it twice. The filename on the server will be outputname.pdf. Only overwrites files if -u is given a valid ID.

Some of these commands will check that you put sane values in. Some of them won't. Finding out which is which is a fun little game
you can play if you don't care about your data. *If these commands go wrong, they may trample your database.*

**Old behaviour.** ~~If you add two files with the same name on the same day, the later one will overwrite the earlier one and will take the same ID. This is
by design, so that you don't end up with several slightly different copies of the same file.~~

**New behaviour.** Adding a file with the same name as an existing file on the same day will now error out *at the database level* (there is a new `overwrite` flag
that needs to be passed to `dbops.add_file` which is passed by `add_record` as false and `update_record` as true). You can use `bucvac -u UPDATEIDENT` (if you
have a vacuumed TeX file to update) or `bucfup` (if you are adding a real file of some sort) to overwrite files and set the modification date. Adding files of
the same name on different days adds new files, as before.

## Configuration
Some configuration settings can be found in [config.py](app/config.py); for example, you can disable the random StackExchange q+a feature
by changing `config.enable_long_fortunes()` to return `False`.

If the file `defaults.json` exists in the top level of your user data directory, then the JSON tags inside it will be added to the metadata
available to `bucvac` and `bucadd`. For example, if you save the following example as your defaults file, then the author field will be automatically
set to Aeneas when vacuuming up a TeX file or using `bucadd` on any other file.

```javascript
{'Buc_author':'Aeneas', 'random_data_field':'this is data'}
```

When using `bucvac`, every field you add will be available inside both templates and the TeX files themselves: you can access the `random_data_field` from
the above example using the `{{template.random_data_field}}`` template command.

Note: `bucadd` will only read `Buc_author` and `Buc_tags` from the defaults file. It will append the tags specified in defaults to those on
the command line. If an author is specified to `bucadd` on the command line, it will take priority over that in the defaults. When using
`bucvac`, the fields inside the TeX file will overwrite those in defaults if there is a conflict.


## Plan.
[Project board](https://github.com/aelzenaar/bucephalus/projects/1)

## Dependencies
* [tinydb](https://pypi.org/project/tinydb/)
* [pystache](https://github.com/defunkt/pystache)
* [flask](http://flask.pocoo.org/)
* [python-magic](https://github.com/ahupp/python-magic)
