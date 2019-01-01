import sys
import argparse
import json

import dbops
import config

from pathlib import Path


parser = argparse.ArgumentParser(description='Bucephalus: Update File')
parser.add_argument('filename', metavar='FILENAME', type=str,
                   help='filename for processing')
parser.add_argument('id', metavar='IDENT', type=int,
                   help='id number to update')
parser.add_argument('-p', help='pin the article', action='store_true', default=False)

args = vars(parser.parse_args())


if dbops.update_record(args['id'], args['filename'], pin=args['p']) == None:
  print("*** Error: failed to update record.")
