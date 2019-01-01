# This is the buchp2 command for Bucephalus.
# It implements the 'new version of bucvac': it allows a user to 'vacuum' up
# a TeX file into the database as a PDF, with templating.

import json
import argparse
import jinja2

import tempfile
import subprocess

from pathlib import Path
from shutil import copyfile
import functools

import dbops
import config

import os
import sys


defaults=config.get_defaults_file_path()

def filter_hp2_set_meta(metadata, value, key):
  metadata[key] = value
  return value

def vacuum(filename,output=None,update=None,pin=False):
  try:
    warned = False
    if not(Path(filename).suffix == '.tex'):
      warned = True
      print("*** Warning: you didn't include the .tex suffix on the end of the file: " + str(filename), file=sys.stderr)

    decoder = json.JSONDecoder()
    metadata = {'template':{}}
    if defaults.exists():
      with defaults.open() as f:
        metadata['template'].update(decoder.decode(f.read()))

    with filename.open() as f:
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

    if ("Hp2_version" not in metadata["template"]) or (metadata["template"]["Hp2_version"] != 2):
      print("*** Error: your input file seems to be for an earlier version of hp. Try bucvac instead.",file=sys.stderr)
      abort(2)

    if output == None:
      pdfname = Path(filename).with_suffix('.pdf')
    else:
      pdfname = Path(output).with_suffix('.pdf')

    if '_' in str(pdfname):
      warned = True
      print("*** Warning: underscore may make XeLaTeX throw a fit.", file=sys.stderr)

    # This section of code works out what the initial metadata we need to give the template is, by
    # either finding the old metadata (if we're updating) or running add_record with delay=True
    # to work out what the new docid and so forth will be.
    author = metadata['template']['Buc_author']
    tags = metadata['template']['Buc_tags']
    templatename = metadata['template']['Hp2_stencil']
    title = (metadata['template']['Buc_title']) if 'Buc_title' in metadata['template'] else "Hp2 temporary title: template " + templatename
    if update == None:
      metadata.update(dbops.add_record(title, author, tags, pdfname, Path(pdfname).with_suffix('.tex'), metadata=None, delay=True))
    else:
      metadata.update(dbops.get_record_by_id(int(update)))
      if(metadata['Buc_name'] != str(pdfname)):
        print("*** Error: Record ID " + str(update) + " with filename " + metadata['Buc_name'] + " doesn't match filename to be added: " + str(pdfname),file=sys.stderr)
        sys.exit(1)

    # Actually render the stencil with the given metadata and content
    loaders = []
    for d in config.get_stencils_search_dirs():
      loaders.append(jinja2.loaders.FileSystemLoader(str(d)))
    env = jinja2.Environment(loader = jinja2.loaders.ChoiceLoader(loaders))
    env.filters['hp2_set_meta'] = functools.partial(filter_hp2_set_meta, metadata)
    template = env.get_template(templatename+".tex")
    rendered = template.render(metadata)

    # Compile the rendered file
    with tempfile.NamedTemporaryFile() as f:
      f.write(bytes(rendered, encoding="utf-8"))
      f.flush()
      # Run latex twice (not a typo!!!)
      subprocess.run("xelatex -no-pdf -halt-on-error -output-directory . -jobname " + str(Path(pdfname).with_suffix('')) + " " + f.name, shell=True, check=True)
      subprocess.run("xelatex -interaction=batchmode -halt-on-error -output-directory . -jobname " + str(Path(pdfname).with_suffix('')) + " " + f.name, shell=True, check=True)

    # Actually commit the files to the database.
    metadata.pop('content', None)
    metadata.pop('template', None)
    if (output == None):
      if (update == None):
        dbops.add_record(title, author, tags, pdfname, filename, metadata, False, pin=pin)
      else:
        dbops.update_record(update, pdfname, filename, pin=pin)
    else:
      copyfile(filename, Path(pdfname).with_suffix('.tex'))
      if (update == None):
        dbops.add_record(title, author, tags, pdfname, Path(pdfname).with_suffix('.tex'), metadata, False, pin=pin)
      else:
        dbops.update_record(update, pdfname, Path(pdfname).with_suffix('.tex'), pin=pin)
      Path(pdfname).with_suffix('.tex').unlink()
  except:
    if(warned):
      print("*** Note: Something failed. Bucephalus printed a warning earlier that might help.")
    raise

parser = argparse.ArgumentParser(description='Bucephalus Vacuum TeX Script (version 2).')
parser.add_argument('filename', metavar='FILENAME', type=str,
                   help='filename for processing')
parser.add_argument('-o', metavar='OUTPUTFILE', type=str,
                   help='optional output filename', default=None)
parser.add_argument('-u', metavar='UPDATEIDENT', type=int,
                   help='id to update', default=None)
parser.add_argument('-p', help='pin the article', action='store_true', default=False)

args = vars(parser.parse_args())
vacuum(Path(args['filename']), args['o'],args['u'],args['p'])

