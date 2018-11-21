import json

from pathlib import Path

from tinydb import TinyDB, Query, where

import config
import vcs

directory=config.get_user_data_dir()

def tasks():
  filename = Path(directory)/"tasks.json"
  decoder = json.JSONDecoder()
  if not filename.exists():
    return []

  with open(filename) as f:
    return decoder.decode(f.read())


def add(task):
  #print("*** add task: " + task)
  filename = Path(directory)/"tasks.json"
  encoder = json.JSONEncoder(indent=2)
  tasklist = tasks() + [task] # Need to read before we open for writing.
  with open(filename, 'w') as f:
    f.write(encoder.encode(tasklist))
  vcs.commit("Tasklist: add task")

def rm(taskids):
  filename = Path(directory)/"tasks.json"
  encoder = json.JSONEncoder(indent=2)
  tasklist = tasks()
  taskids = sorted([int(x) for x in taskids], reverse=True)
  for i in taskids:
    tasklist.pop(i)
  with open(filename, 'w') as f:
    f.write(encoder.encode(tasklist))
  vcs.commit("Tasklist: rm task")
