import hashlib
import datetime
import json
import sys

from shutil import copyfile
from pathlib import Path

from tinydb import TinyDB, Query

directory="./data/"
dbname="database.db"
date_format="%Y%m%d%H%M%S"

def getid(data):
  with open(data) as f:
    hashed = hashlib.md5(f.read().encode('utf-8')).hexdigest()
  date = datetime.datetime.today().strftime(date_format)
  short = hex(int(date,10))[2:]
  return str(short + ":" + hashed)

def dateFromId(rid):
  return str(int(rid.split(':')[0],16))

def hashFromId(rid):
  return rid.split(':')[1]

def addrecord(rid, title, author, tags, meat, source=None):
  # Sort out metadata
  datestr = dateFromId(rid)
  metadata = {'Buc_id':rid, 'Buc_timestamp':datestr, 'Buc_tags': tags, 'Buc_author': author, 'Buc_title': title, 'Buc_ext': ext}
  if not(source == None):
    metadata['Buc_source'] = source.name()

  # Make correct directory if it doesn't exist
  dd = Path(directory)
  if not(dd.exists()):
    dd.mkdir()
  if not(dd.is_dir()):
    sys.exit("*** Data directory (" + directory + ") is not a directory.")

  datedir = dd / datestr[:4] / datestr[4:6] / datestr[6:8]
  if not(datedir.exists()):
    datedir.mkdir(parents=True)
  if not(datedir.is_dir()):
    sys.exit("*** Datestamp directory (" + directory + ") is not a directory.")

  # Copy file to location, and sources if needed
  meatpath = Path(meat)
  copyfile(meatpath, meatpath.name())
  if not(source == None):
    srcpath = Path(source)
    copyfile(meatpath, srcpath.name())

  # Sort out database
  db = TinyDB(Path(directory)/dbname)
  metatable = db.table('files')
  metatable.insert(metadata)
