import hashlib
import datetime
import json
import sys
import os
import errno

from shutil import copyfile
from pathlib import Path

from tinydb import TinyDB, Query, where

import config
import vcs

class BucephalusException(Exception):
  pass

# Raised when a file in the database is to be updated, but the file in the database has a different
# name to the file to be added.
class UpdateDifferentFile(BucephalusException):
  def __init__(self, file_in_db, file_to_add):
    self.file_in_db = file_in_db
    self.file_to_add = file_to_add
    self.message = "File to be updated has wrong name: file in database is '" + file_in_db + "', attempted to updated with '" + file_to_add + "'"

  def __str__(self):
    return self.message

# Raised when a file in the database is to be updated, but the ID is not in the database.
class UpdateMissingFile(BucephalusException):
  def __init__(self, ident):
    self.ident = ident
    self.message = "File to be updated doesn't already exist in database: nonexistent ID is " + str(ident)

  def __str__(self):
    return self.message

directory=config.get_user_data_dir()
dbname="database.db"

# We could probably cache the database object. However, most applications only do one db operation and then exit; the only
# thing which might benefit is the web server. We could just cache it anyway, it's not like it will add any kind of overhead;
# but at the same time, the way everything below is implemented (by looping through the entire DB for things like finding all
# the represented years) is incredibly awful, so this can't be a slowdown compared to that.
def get_database_object():
  return TinyDB(str(Path(directory)/dbname), indent=2)

def get_recents():
  filename = config.get_recent_file_path()
  decoder = json.JSONDecoder()
  if not filename.exists():
    return []

  with filename.open() as f:
    ids = decoder.decode(f.read())

  return ids

def set_recent(recents):
  filename = config.get_recent_file_path()
  if not filename.exists():
    filename.touch()
  encoder = json.JSONEncoder(indent=2)
  with filename.open(mode='w') as f:
    f.write(encoder.encode(recents))

def add_recent(dbid):
  recent = get_recents()
  if dbid in recent:
    recent.pop(recent.index(dbid))
  elif len(recent) == 5:
    recent.pop(0)

  recent.append(dbid)
  set_recent(recent)

# Write the given metadata into the database, overwriting old records.
def write_metadata(metadata):
  date = datetime.datetime.today()
  metadata['ts_year2'] = date.year
  metadata['ts_month2'] = date.month
  metadata['ts_day2'] = date.day
  metadata['ts_hour2'] = date.hour
  metadata['ts_minute2'] = date.minute
  metadata['ts_second2'] = date.second

  db = get_database_object()
  metatable = db.table('files')
  oldrecord = get_records_by_date(metadata['ts_year'], metadata['ts_month'], metadata['ts_day'], metadata['Buc_name'])
  if(oldrecord == None):
    dbid = metatable.insert(metadata)
  else:
    dbid = oldrecord.doc_id
    metatable.update(metadata, doc_ids=[oldrecord.doc_id])

  add_recent(dbid)
  return dbid


# Copy a file into the database, based on the given metadata; check for overwriting if overwrite == true.
def add_file(metadata, overwrite, filename, source = None):
  meatpath = Path(filename)
  if not meatpath.exists():
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(meatpath))

  dd = Path(directory)
  if not(dd.exists()):
    dd.mkdir()
  if not(dd.is_dir()):
    raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), str(dd))

  datedir = dd / str(metadata['ts_year']) / str(metadata['ts_month']) / str(metadata['ts_day'])
  if (not overwrite) and (datedir / meatpath.name).exists():
    raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), str(datedir / meatpath.name))
  if not(datedir.exists()):
    datedir.mkdir(parents=True)
  if not(datedir.is_dir()):
    raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), str(datedir))

  # Copy file to location, and sources if needed
  copyfile(str(meatpath), str(datedir / meatpath.name))
  if not(source == None):
    srcpath = Path(source)
    srcdest = datedir / 'src'
    if not(srcdest.exists()):
      srcdest.mkdir()
    if not(srcdest.is_dir()):
      raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), str(srcdest))
    copyfile(str(srcpath), str(srcdest/srcpath.name))

# Open an item for reading.
def open_read(item):
  return (dd / str(item['ts_year']) / str(item['ts_month']) / str(item['ts_day']) / str(item['Buc_name'])).open(mode='rb')

# Update an existing record.
def update_record(ident, meat, source=None, pin=False):
  db = get_database_object()
  metatable = db.table('files')
  oldrecord = get_record_by_id(ident)
  if(oldrecord == None):
    raise UpdateMissingFile(ident)
  if(oldrecord['Buc_name'] != Path(meat).name):
    raise UpdateDifferentFile(oldrecord['Buc_name'], str(Path(meat).name))

  add_file(oldrecord, True, meat, source)
  dbid = write_metadata(oldrecord)
  if pin:
    set_pinned(dbid)
  vcs.commit("dbops: update record")
  return True

# Create a new record, try not to overwrite existing stuff.
def add_record(title, author, tags, meat, source=None, metadata=None, delay=False, pin=False):
  meatpath = Path(meat)
  srcpath = None

  if (metadata == None):
    # Sort out metadata
    date = datetime.datetime.today()
    metadata = {'ts_year':date.year,     'ts_year2':date.year,
                'ts_month':date.month,   'ts_month2':date.month,
                'ts_day':date.day,       'ts_day2':date.day,
                'ts_hour':date.hour,     'ts_hour2':date.hour,
                'ts_minute':date.minute, 'ts_minute2':date.minute,
                'ts_second':date.second, 'ts_second2':date.second,
                'Buc_tags': tags,
                'Buc_author': author,
                'Buc_title': title,
                'Buc_name': meatpath.name}
    if not(source == None):
      srcpath = Path(source)
      metadata['Buc_source'] = srcpath.name
  if delay == True:
    return metadata

  add_file(metadata, False, meatpath, srcpath)
  dbid = write_metadata(metadata)
  if pin:
    set_pinned(dbid)

  vcs.commit("dbops: add new record")
  return metadata

# If tags==None, return list of all tags; otherwise return intersection of given tags.
def get_records_by_tag(tags=None):
  db = get_database_object().table('files')
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
  db = get_database_object().table('files')

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

# Return metadata for given ID
def get_record_by_id(ident):
  db = get_database_object()
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return None
  return item

# Return path to actual file stored based on id and filename
def get_single_record_path(ident, meat):
  db = get_database_object()
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return None
  if not(item['Buc_name'] == meat):
    return None

  filename = directory/str(item['ts_year'])/str(item['ts_month'])/str(item['ts_day'])/str(item['Buc_name'])
  return filename

# Return path to actual SOURCE file stored based on id and filename
def get_single_record_src_path(ident,src):
  db = get_database_object()
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return None
  if not(src == str(item['Buc_source'])):
    return None

  filename = directory/str(item['ts_year'])/str(item['ts_month'])/str(item['ts_day'])/"src"/str(item['Buc_source'])
  return filename

# Delete given record
def remove_record_by_id(ident):
  db = get_database_object()
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

  # Remove deleted item from recents, if needed
  recent = get_recents()
  if int(ident) in recent:
    recent.pop(recent.index(int(ident)))
  set_recent(recent)

  # Remove deleted item from pinned, if needed
  if get_pinned() == int(ident):
    unset_pinned()

  print("*** Deleted.")
  vcs.commit("dbops: delete record")
  return True

# Get record based on date and filename.
def get_record_by_file(year, month, day, filename):
  db = get_database_object()
  return db.table('files').get((where('ts_year')==int(year)) & (where('ts_month')==int(month)) & (where('ts_day')==int(day)) & ((where('Buc_name') == filename) | (where('Buc_source') == filename)))

def get_pinned():
  filename = config.get_pinned_file_path()
  decoder = json.JSONDecoder()
  if not filename.exists():
    return None

  with filename.open() as f:
    ident = decoder.decode(f.read())['pinned']

  return ident

def unset_pinned():
  config.get_pinned_file_path().unlink()

def set_pinned(ident):
  filename = config.get_pinned_file_path()
  if not filename.exists():
    filename.touch()
  encoder = json.JSONEncoder(indent=2)
  with filename.open(mode='w') as f:
    f.write(encoder.encode({'pinned': ident}))
