import sys
import argparse
import json

import config
import vcs

from pathlib import Path


parser = argparse.ArgumentParser(description='Bucephalus: Edit Defaults and Configuration')
group = parser.add_mutually_exclusive_group()
group.add_argument('-a', metavar='KEY', type=str, nargs=2, help='add a default key with given value')
group.add_argument('-r', metavar='KEY', type=str, help='remove a default key')

args = vars(parser.parse_args())

filename = config.get_defaults_file_path()
decoder = json.JSONDecoder()
if filename.exists():
  with open(filename) as f:
    defaults = decoder.decode(f.read())

need_write = False
if args['a'] != None:
  defaults[args['a'][0]] = args['a'][1]
  need_write = True
elif args['r'] != None:
  defaults.pop(args['r'])
  need_write = True
else:
  for key,val in defaults.items():
    print(": " + str(key) + "\t\t" + str(val))

if need_write:
  encoder = json.JSONEncoder(indent=2)
  with open(filename, 'w') as f:
    f.write(encoder.encode(defaults))
  vcs.commit("Defaults_cmd: change defaults")
