import sys
import argparse
import json

import dbops
import config

from pathlib import Path


parser = argparse.ArgumentParser(description='Bucephalus: Add File')
parser.add_argument('filename', metavar='FILENAME', type=str, nargs=1,
                   help='filename for processing')
parser.add_argument('title', metavar='TITLE', type=str, nargs=1,
                   help='title to add to database', default=None)
parser.add_argument('-a', metavar='AUTHOR', type=str, nargs=1,
                   help='author name', default=None)
parser.add_argument('tags', metavar='TAGS', type=str, nargs='+',
                   help='tags to add to database', default=None)

args = vars(parser.parse_args())

author = args['a'][0] if args['a'] != None else ""
tags = []

defaults=config.get_user_data_dir()/"defaults.json"
if defaults.exists():
  with open(defaults) as f:
    decoder = json.JSONDecoder()
    metadata = decoder.decode(f.read())
    if ('Buc_author' in metadata) and (args['a'] == None):
      author = metadata['Buc_author']
    if 'Buc_tags' in metadata:
      tags = metadata['Buc_tags']

filename = args['filename'][0]
title = args['title'][0]
for tag in args['tags']:
  if not(tag in tags):
    tags.append(tag)

print(filename)

if dbops.add_record(title, author, tags, filename) == None:
  print("Error")
