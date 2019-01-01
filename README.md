# bucephalus

:warning: **If you used `bucvac` prior to 2019, you should read the documentation below on stencils as there have been non-backward-compatible changes.**  :warning:

This repository is only a test. [There is nothing to see here](https://www.youtube.com/watch?v=V2MIvUx9uiQ).

Long-term goal: [futuristic](https://abstrusegoose.com/440) paperless society or something.

Short-tem goal: to establish the feasibility of the long-term goal, in an effort to produce a design for
software that accomplishes it in a much nicer way than this. Because [who doesn't like a good rewrite from scratch](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/).

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
* `buctask [-h] [-a DESCRIPTION | -r NUMBER [NUMBER ...]]` - manage the task list from the command line. If no options given, display the list; otherwise
add the given task string to the end, or remove the given items from the list.
* `bucadd [-h] [-a AUTHOR] [-p] FILENAME TITLE TAGS [TAGS ...]` (must have at least one tag, author optional) - add the given file to the bucephalus database. See usage below.
* `bucfup [-h] [-p] FILENAME IDENT` - update the existing file contents at id IDENT from FILENAME.
* `bucmup [-h] [-t TITLE] [-a AUTHOR] [-T TAGS [TAGS ...]] IDENT` - update the existing file metadata at id IDENT with the given metadata, or just display the current metadata if no optional arguments are given.
* `bucrm <identifier>` - remove the given database entry permanently and all the files associated with it. The identifier could be reused, I don't know.
* `bucvac [-h] [-o OUTPUTFILE] [-u UPDATEIDENT] [-p] FILENAME` - vacuum up the given TeX source file which includes a section of JSON at the start. See usage below.
* `bucdef [-h] [-a KEY VALUE | -r KEY]` - change the default tags fed into bucvac prototypes.

Some of these commands will check that you put sane values in. Some of them won't. Finding out which is which is a fun little game
you can play if you don't care about your data. *If these commands go wrong, they may trample your database.*

### Configuration
Some configuration settings can be found in [config.py](lib/config.py); for example, you can disable the random StackExchange q+a feature
by changing `config.enable_long_fortunes()` to return `False`.


### `bucvac` and `bucadd` behaviour
What is the difference? `bucadd` will add files vertabim, and `bucvac` will pass LaTeX files through a templating system and add both
the source and PDF files.

#### Adding files
Adding a file with the same name as an existing file on the same day will now error out *at the database level* (there is a new `overwrite` flag
that needs to be passed to `dbops.add_file` which is passed by `add_record` as false and `update_record` as true). You can use `bucvac -u UPDATEIDENT` (if you
have a vacuumed TeX file to update) or `bucfup` (if you are adding a real file of some sort) to overwrite files and set the modification date. Adding files of
the same name on different days adds new files, as before.

#### Default key values
If the file `defaults.json` exists in the top level of your user data directory, then the JSON tags inside it will be added to the metadata
available to `bucvac` and `bucadd`. For example, if you save the following example as your defaults file, then the author field will be automatically
set to Aeneas when vacuuming up a TeX file or using `bucadd` on any other file.

```javascript
{'Buc_author':'Aeneas', 'random_data_field':'this is data'}
```

When using `bucvac`, every field you add will be available inside both templates and the TeX files themselves: you can access the `random_data_field` from
the above example using the `{{template.random_data_field}}` template command.

The `bucdef` command can be used to modify `defaults.json` from the command line.

Note: `bucadd` will only read `Buc_author` and `Buc_tags` from the defaults file. It will append the tags specified in defaults to those on
the command line. If an author is specified to `bucadd` on the command line, it will take priority over that in the defaults. When using
`bucvac`, the fields inside the TeX file will overwrite those in defaults if there is a conflict.

#### Stencils
LaTeX files passed into `bucvac` need to be formatted as metadata dict and content sections, seperated by a line solely consisting
of the characters `===`. Examples can be seen in the [test/](test/) subdirectory. The key `Hp2_version` **must** be set to 2 (the integer,
not the string).

Each such file has to be associated with a stencil file by setting the key `Hp2_stencil`. This is a [jinja2](http://jinja.pocoo.org/) template which is passed the
metadata of the file to be added, the user-provided data in the metadata dict section of the TeX file, and the content section of this file.
See the [stencils/](stencils/) subdirectory for some examples. Stencils are, by default, searched for in `<user data dir>/stencils`
and `<install dir>/stencils`, in that order. The directories to be searched can be configured by editing `config.get_stencils_search_dirs()`.

As of commit https://github.com/aelzenaar/bucephalus/commit/88336b689fd73220c4ae76d136548755a95a6b96 (1 Jan 2019, see issue #3), there have been non-backward-compatible changes to `bucvac`. From
a practical standpoint, **at least** the following changes need to be made:

  * In TeX files to be processed, the addition of the version key `Hp2_version` and the renaming of `Buc_hp` to `Hp2_stencil`.
  * Template files need to be moved to `stencils/` (if they live in the default `prototypes/` directories).

In addition, the new templating engine ([jinja2](http://jinja.pocoo.org/)) has a slightly different syntax to the previous
engine ([pystache](https://github.com/defunkt/pystache)) which may require some minor changes to be made to templates.

### Todo list
There are two options for using the todo list: the `buctask` command line utility, or the web interface. The command line interface allows all
operations to be carried out: running the command with no options lists the todo list, `-a` allows one to add an item, and `-r` allows the removal
of one or more tasks from the list.

The web interface also allows all of these options by default, and is read-write by everyone. In other words, there is *NO AUTHENTICATION WHATSOEVER*!!!
(When I add additional features, e.g. integration with services and/or editors, I will implement some form of auth. Otherwise, do not leave the web todo
functionality running when on a public server - it can be disabled entirely by changing `enable_tasklist_web()` to return `False` in `config.py`, or can
be made read-only by changing `enable_tasklist_web_write()` to return `False` in the same file.)

### Geogebra embedding
The web service also embeds [Geogebra](https://geogebra.org/); if an article with name ending in `.ggb` is requested, the endpoint `/r/ggb/<IDENT>/<FILENAME>` is
transparently embedded into the article viewer and the source link allows download of the ggb file. (This feature can be disabled in `config.py`.)

### Git (or other VCS) integration
Bucephalus will now by default store its database in a git repository. No functionality is actually provided at this point beyond simply
commiting whenever a file is added or removed, or the task list changes. The functionality can be disabled by changing `enable_vcs_commits()`
to return `False` in `config.py`; all the VCS functionality is kept inside [vcs.py](lib/vcs.py), and so it should be relatively easy to
swap Git out for hg and/or svn and/or sccs (if you are still living that far in the past).

## Plan
[Project board](https://github.com/aelzenaar/bucephalus/projects/1)

## Dependencies
* [tinydb](https://pypi.org/project/tinydb/)
* [flask](http://flask.pocoo.org/) and [jinja2](http://jinja.pocoo.org/)
* [python-magic](https://github.com/ahupp/python-magic) (Warning: this is **not** the same as the module provided by the Debian package `python3-magic`.)
