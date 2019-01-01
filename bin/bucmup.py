import sys
import argparse
import json

import dbops
import config

from pathlib import Path


parser = argparse.ArgumentParser(description='Bucephalus: Update Metadata')
parser.add_argument('id', metavar='IDENT', type=str, nargs=1,
                   help='article ID')
parser.add_argument('-t', metavar='TITLE', type=str, nargs=1,
                   help='set title', default=None)
parser.add_argument('-a', metavar='AUTHOR', type=str, nargs=1,
                   help='set author name', default=None)
parser.add_argument('-T', metavar='TAGS', type=str, nargs='+',
                   help='set tags', default=None)

args = vars(parser.parse_args())

record = dbops.get_record_by_id(args['id'][0])
didSomething = False
if(args['a'] != None):
  record['Buc_author'] = args['a'][0]
  didSomething = True
if(args['t'] != None):
  record['Buc_title'] = args['t'][0]
  didSomething = True
if(args['T'] != None):
  record['Buc_tags'] = args['T']
  didSomething = True

if didSomething:
  dbops.write_metadata(record)
