import sys
import argparse
import json

import dbops
import config

from pathlib import Path


parser = argparse.ArgumentParser(description='Bucephalus: Update File')
parser.add_argument('filename', metavar='FILENAME', type=str, nargs=1,
                   help='filename for processing')
parser.add_argument('id', metavar='IDENT', type=int, nargs=1,
                   help='id number to update')

args = vars(parser.parse_args())

if dbops.update_record(args['id'][0], args['filename'][0]) == None:
  print("Error")
