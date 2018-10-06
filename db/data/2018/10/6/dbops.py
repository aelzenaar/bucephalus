import hashlib
import datetime
import json
import sys

from shutil import copyfile
from pathlib import Path

from tinydb import TinyDB, Query

directory="./data/"
dbname="database.db"

def addrecord(title, author, tags, meat, source=None):
  # Sort out metadata
  date = datetime.datetime.today()
  metadata = {'ts_year':date.year,
              'ts_month':date.month,
              'ts_day':date.day,
              'ts_hour':date.hour,
              'td_minute':date.minute,
              'td_second':date.second,
              'Buc_tags': tags,
              'Buc_author': author,
              'Buc_title': title,
              'Buc_name':meat.name}
  if not(source == None):
    metadata['Buc_source'] = source.name

  # Make correct directory if it doesn't exist
  dd = Path(directory)
  if not(dd.exists()):
    dd.mkdir()
  if not(dd.is_dir()):
    sys.exit("*** Data directory (" + directory + ") is not a directory.")

  datedir = dd / str(date.year) / str(date.month) / str(date.day)
  if not(datedir.exists()):
    datedir.mkdir(parents=True)
  if not(datedir.is_dir()):
    sys.exit("*** Datestamp directory (" + directory + ") is not a directory.")

  # Copy file to location, and sources if needed
  meatpath = Path(meat)
  copyfile(meatpath, datedir / meatpath.name)
  if not(source == None):
    srcpath = Path(source)
    copyfile(srcpath, datedir / 'src' / srcpath.name)

  # Sort out database
  db = TinyDB(Path(directory)/dbname)
  metatable = db.table('files')
  metatable.insert(metadata)
