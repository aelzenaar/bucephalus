from pathlib import Path
import re

import config

def recurse(path):
  #print(str(path))
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
  print('searching ' + str(path))
  with open(path, 'rb') as f:
    return (True if regexp.search(f.read()) else False)

def search_files_for_string(s):
  r = re.compile(s.encode('utf-8'))
  files = []
  for path in list_files():
    if search_file_for_string(path, r):
      files.append(path)
  return files
