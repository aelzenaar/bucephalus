import hashlib
import datetime
import json
import sys

from shutil import copyfile
from pathlib import Path

from tinydb import TinyDB, Query, where

directory="./data/"
dbname="database.db"

def addrecord(title, author, tags, meat, source=None):
  meatpath = Path(meat)
  if not(meatpath.exists()):
    return None
  # Sort out metadata
  date = datetime.datetime.today()
  metadata = {'ts_year':date.year,
              'ts_month':date.month,
              'ts_day':date.day,
              'ts_hour':date.hour,
              'ts_minute':date.minute,
              'ts_second':date.second,
              'Buc_tags': tags,
              'Buc_author': author,
              'Buc_title': title,
              'Buc_name': meatpath.name}
  if not(source == None):
    srcpath = Path(source)
    metadata['Buc_source'] = sourcepath.name

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
  copyfile(meatpath, datedir / meatpath.name)
  if not(source == None):
    copyfile(srcpath, datedir / 'src' / srcpath.name)

  # Sort out database
  db = TinyDB(Path(directory)/dbname)
  metatable = db.table('files')
  metatable.insert(metadata)
  return metatable

def get_records_by_date(year=None, month=None, day=None, name=None):
  db = TinyDB(Path(directory)/dbname).table('files')

  if year == None:
    years = []
    for item in db:
      if not(item['ts_year'] in years):
        years.append(item['ts_year'])
    return sorted(years)

  if month == None:
    months = []
    for item in db.search(where('ts_year')==int(year)):
      if not(item['ts_month'] in months):
        months.append(item['ts_month'])
    return sorted(months)

  if day == None:
    days = []
    for item in db.search((where('ts_year')==int(year)) & (where('ts_month')==int(month))):
      if not(item['ts_day'] in days):
        days.append(item['ts_day'])
    return sorted(days)

  if name == None:
    docs = []
    for item in db.search((where('ts_year')==int(year)) & (where('ts_month')==int(month)) & (where('ts_day')==int(day))):
      docs.append(item)
    return docs

  return db.get((where('ts_year')==int(year)) & (where('ts_month')==int(month)) & (where('ts_day')==int(day)) & (where('Buc_name') == name))
