import json

from pathlib import Path

from tinydb import TinyDB, Query, where

import config

directory=config.get_user_data_dir()

def tasks():
  filename = Path(directory)/"tasks.json"
  decoder = json.JSONDecoder()
  if not filename.exists():
    return []

  with open(filename) as f:
    return decoder.decode(f.read())


def add(task):
  print("*** add" + task)
  filename = Path(directory)/"tasks.json"
  encoder = json.JSONEncoder()
  tasklist = tasks() + [task] # Need to read before we open for writing.
  print(tasklist)
  with open(filename, 'w') as f:
    f.write(encoder.encode(tasklist))

def rm(taskids):
  filename = Path(directory)/"tasks.json"
  encoder = json.JSONEncoder()
  tasklist = tasks()
  taskids = sorted([int(x) for x in taskids], reverse=True)
  for i in taskids:
    tasklist.pop(i)
  with open(filename, 'w') as f:
    f.write(encoder.encode(tasklist))
