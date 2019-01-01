import sys
import argparse
import json

import dbops
import config

from pathlib import Path


parser = argparse.ArgumentParser(description='Bucephalus: Add File')
parser.add_argument('filename', metavar='FILENAME', type=str,
                   help='filename for processing')
parser.add_argument('title', metavar='TITLE', type=str,
                   help='title to add to database', default=None)
parser.add_argument('-a', metavar='AUTHOR', type=str,
                   help='author name', default=None)
parser.add_argument('-p', help='pin the article', action='store_true', default=False)
parser.add_argument('tags', metavar='TAGS', type=str, nargs='+',
                   help='tags to add to database', default=None)

args = vars(parser.parse_args())

author = args['a'] if args['a'] != None else ""
pin = args['p']
tags = []

defaults=config.get_defaults_file_path()
if defaults.exists():
  with defaults.open() as f:
    decoder = json.JSONDecoder()
    metadata = decoder.decode(f.read())
    if ('Buc_author' in metadata) and (args['a'] == None):
      author = metadata['Buc_author']
    if 'Buc_tags' in metadata:
      tags = metadata['Buc_tags']

filename = args['filename']
title = args['title']
for tag in args['tags']:
  if not(tag in tags):
    tags.append(tag)

if dbops.add_record(title, author, tags, filename, pin=pin) == None:
  print("*** Error: failed to add record.")
