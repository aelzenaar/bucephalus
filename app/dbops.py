import hashlib
import datetime
import json
import sys

from shutil import copyfile
from pathlib import Path

from tinydb import TinyDB, Query, where

directory=Path.home()/"bucephalus"
dbname="database.db"

def addrecord(title, author, tags, meat, source=None, metadata=None, delay=False):
  meatpath = Path(meat)

  if (metadata == None):
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
      metadata['Buc_source'] = srcpath.name
  if delay == True:
    return metadata

  if not(meatpath.exists()):
    return None

  # Make correct directory if it doesn't exist
  dd = Path(directory)
  if not(dd.exists()):
    dd.mkdir()
  if not(dd.is_dir()):
    sys.exit("*** Data directory (" + directory + ") is not a directory.")

  datedir = dd / str(metadata['ts_year']) / str(metadata['ts_month']) / str(metadata['ts_day'])
  if not(datedir.exists()):
    datedir.mkdir(parents=True)
  if not(datedir.is_dir()):
    sys.exit("*** Datestamp directory (" + directory + ") is not a directory.")

  # Copy file to location, and sources if needed
  copyfile(meatpath, datedir / meatpath.name)
  if not(source == None):
    srcpath = Path(source)
    srcdest = datedir / 'src'
    if not(srcdest.exists()):
      srcdest.mkdir()
    if not(srcdest.is_dir()):
      sys.exit("*** Source directory (" + directory + ") is not a directory.")
    copyfile(srcpath, srcdest/srcpath.name)

  # Sort out database
  db = TinyDB(Path(directory)/dbname)
  metatable = db.table('files')
  oldrecord = get_records_by_date(metadata['ts_year'], metadata['ts_month'], metadata['ts_day'], metadata['Buc_name'])
  if(oldrecord == None):
    metatable.insert(metadata)
  else:
    metatable.update(metadata, doc_ids=[oldrecord.doc_id])

  return metatable

def get_records_by_tag(tags=None):
  db = TinyDB(Path(directory)/dbname).table('files')
  if tags == None:
    tags = []
    for item in db:
      for tag in item['Buc_tags']:
        if tag not in tags:
          tags.append(tag)
    return sorted(tags)

  q = Query()
  return db.search(q.Buc_tags.all(tags))

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

def get_record_by_id(ident):
  db = TinyDB(directory/dbname)
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return None
  return item

def get_single_record_path(ident, meat):
  db = TinyDB(directory/dbname)
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return None
  if not(item['Buc_name'] == meat):
    return None

  filename = directory/str(item['ts_year'])/str(item['ts_month'])/str(item['ts_day'])/str(item['Buc_name'])
  return filename

def get_single_record_src_path(ident,src):
  db = TinyDB(directory/dbname)
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return None
  if not(src == str(item['Buc_source'])):
    return None

  filename = directory/str(item['ts_year'])/str(item['ts_month'])/str(item['ts_day'])/"src"/str(item['Buc_source'])
  return filename

def remove_record_by_id(ident):
  db = TinyDB(directory/dbname)
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return None

  filepath = get_single_record_path(ident, item['Buc_name'])
  if 'Buc_source' in item:
    sourcepath = get_single_record_src_path(ident, item['Buc_source'])
  else:
    sourcepath = None

  print("*** Deleting record " + str(ident) + " which lives at " + str(filepath))

  # Now we delete.
  db.table('files').remove(doc_ids=[int(ident)])
  filepath.unlink()
  if not(sourcepath == None):
    sourcepath.unlink()

  print("*** Deleted.")
  return True
