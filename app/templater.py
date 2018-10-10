import json
import pystache
import argparse

import tempfile
import subprocess

from pathlib import Path
from shutil import copyfile

import dbops
import config

import os
import sys

directory1=config.get_user_data_dir()/"prototypes"
directory2=config.get_install_dir()/"prototypes"

defaults=config.get_user_data_dir()/"defaults.json"

def vacuum(filename,output=None,update=None):
  try:
    warned = False
    if not(Path(filename).suffix == '.tex'):
      warned = True
      print("Warning: you included the .tex suffix on the end of the file: " + str(filename),file=sys.stderr)

    decoder = json.JSONDecoder()
    metadata = {'template':{}}
    if defaults.exists():
      with open(defaults) as f:
        metadata['template'].update(decoder.decode(f.read()))

    with open(filename) as f:
      inContent = False
      userdef = ""
      content = ""
      for line in f:
        if("===" in line):
          inContent = True
          continue
        if(not(inContent)):
          userdef = userdef + line
        else:
          content = content + line

      metadata["template"].update(decoder.decode(userdef))
      metadata["content"] = content

    if output == None:
      pdfname = Path(filename).with_suffix('.pdf')
    else:
      pdfname = Path(output).with_suffix('.pdf')

    if '_' in str(pdfname):
      warned = True
      print("Warning: underscore may make XeLaTeX throw a fit.", file=sys.stderr)

    title = metadata['template']['Buc_title']
    author = metadata['template']['Buc_author']
    tags = metadata['template']['Buc_tags']
    templatename = metadata['template']['Buc_hp']
    if update == None:
      metadata.update(dbops.addrecord(title, author, tags, pdfname, Path(pdfname).with_suffix('.tex'), None, True))
    else:
      metadata.update(dbops.get_record_by_id(int(update)))
      if(metadata['Buc_name'] != Path(pdfname).with_suffix('.tex')):
        print("Record ID " + str(update) + " with filename " + metadata['Buc_name'] + " doesn't match filename to be added: " + pdfname)
        sys.exit(1)

    templatepath = directory1/(templatename + ".mustache")
    if not (templatepath.exists()):
      templatepath = directory2/(templatename + ".mustache")
      if not(templatepath.exists()):
        print("No template found: " + str(templatepath),file=sys.stderr)
        sys.exit(1)

    with open(templatepath) as f:
      templateContent = f.read()
      rendered = pystache.render(templateContent, metadata)

    with tempfile.NamedTemporaryFile() as f:
      f.write(bytes(rendered, encoding="utf-8"))
      f.flush()
      # Run latex twice (not a typo!!!)
      subprocess.run("xelatex -no-pdf -halt-on-error -output-directory . -jobname " + str(Path(pdfname).with_suffix('')) + " " + f.name, shell=True, check=True)
      subprocess.run("xelatex -interaction=batchmode -halt-on-error -output-directory . -jobname " + str(Path(pdfname).with_suffix('')) + " " + f.name, shell=True, check=True)

    metadata.pop('content', None)
    metadata.pop('template', None)
    if (output == None):
      if (update == None):
        dbops.addrecord(title, author, tags, pdfname, filename, metadata, False)
      else:
        dbops.updaterecord(update, pdfname, filename)
    else:
      copyfile(filename, Path(pdfname).with_suffix('.tex'))
      if (update == None):
        dbops.addrecord(title, author, tags, pdfname, Path(pdfname).with_suffix('.tex'), metadata, False)
      else:
        dbops.updaterecord(update, pdfname, Path(pdfname).with_suffix('.tex'))
      Path(pdfname).with_suffix('.tex').unlink()
  except:
    if(warned):
      print("*** Note: Something failed. Bucephalus printed a warning earlier that might help.")
    raise

parser = argparse.ArgumentParser(description='Bucephalus Vacuum TeX Script.')
parser.add_argument('filename', metavar='FILENAME', type=str, nargs=1,
                   help='filename for processing')
parser.add_argument('-o', metavar='OUTPUTFILE', type=str, nargs=1,
                   help='optional output filename', default=None)
parser.add_argument('-u', metavar='UPDATEIDENT', type=int, nargs=1,
                   help='id to update', default=None)

args = vars(parser.parse_args())

print(args)

update = args['u'][0] if args['u'] != None else None
output = args['o'][0] if args['o'] != None else None

vacuum(args['filename'][0], output,update)

