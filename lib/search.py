from pathlib import Path
import re

import config

def recurse(path):
  paths = []
  if path.is_file():
    paths.append(path)
  else:
    for child in path.iterdir():
      paths = paths + recurse(child)

  return paths

def list_files():
  return recurse(config.get_user_data_dir())

def search_file_for_string(path, regexp):
  print(path)
  with path.open(mode='rb') as f:
    return (True if regexp.search(f.read()) else False)

def search_files_for_string(s, case):
  flags = 0
  flags |= (re.IGNORECASE if (not case) else 0)
  r = re.compile(s.encode('utf-8'), flags=flags)
  files = []
  for path in list_files():
    if search_file_for_string(path, r):
      files.append(path)
  return files
