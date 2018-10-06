# bucephalus

This repository is only a test. [There is nothing to see here](https://www.youtube.com/watch?v=V2MIvUx9uiQ).

Goal: [futuristic](https://abstrusegoose.com/440) paperless society or something.

## Plan.
1. Prototype template system for TeX [Prototyped](horsepee/)
2. Storage of files by date for retrieval by ID in both source and PDF form where applicable.
3. REST api and web interface barebones
4. Tag system
5. Extension from TeX to Geogebra files?
6. Scan-to-email-to-upload automatically?

## Dependencies
* [tinydb](https://pypi.org/project/tinydb/)
* [pystache](https://github.com/defunkt/pystache)

## Notes
ID format: '[date in YYYYMMDDhhmmss, converted to hexadecimal]:[md5hash of file]' --- but if you want the date, pull it
from the metadata in the database (or from the file structure).

Directories:-
* `data/`
  * `YYYY/MM/DD/hash.ext`
  * `YYYY/MM/DD/hash-src/blah`
  * `database.db`
