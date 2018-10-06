import hashlib
import datetime

directory="./data/"
date_format="%Y%m%d%H%M%S"

def getid(data):
  with open(data) as f:
    hashed = hashlib.md5(f.read().encode('utf-8')).hexdigest()
  date = datetime.datetime.today().strftime(date_format)
  short = hex(int(date,10))[2:]
  return str(short + ":" + hashed)

def dateFromId(rid):
  return int(rid.split(:)[0],16)

def addrecord(rid, title, author, tags, meat, source=None):
  pass
