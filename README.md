# bucephalus

This repository is only a test. [There is nothing to see here](https://www.youtube.com/watch?v=V2MIvUx9uiQ).

Goal: [futuristic](https://abstrusegoose.com/440) paperless society or something.

## Plan.
1. Prototype template system for TeX [Prototyped](horsepee/)
2. Storage of files by date for retrieval by ID in both source and PDF form where applicable. [Done for date-based retrieval](app/) - need to add ID based retrieval
3. REST api and web interface barebones [Done for date-based retrieval](app/)
4. Nice system to add files
4. Tag system
5. Search
5. Extension from TeX to Geogebra files?
6. Scan-to-email-to-upload automatically?

## Dependencies
* [tinydb](https://pypi.org/project/tinydb/)
* [pystache](https://github.com/defunkt/pystache)
* [flask](http://flask.pocoo.org/)

## Notes
ID format: integer from TinyDB

Directories:-
* `data/`
  * `YYYY/MM/DD/filename`
  * `YYYY/MM/DD/src/filename`
  * `database.db`
