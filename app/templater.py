import json
import pystache

import tempfile
import subprocess

from pathlib import Path

import dbops

import os
import sys

directory1=Path.home()/"bucephalus"/"prototypes"
directory2=Path(__file__).parent/"prototypes"

defaults=Path.home()/"bucephalus"/"defaults.json"

def vacuum(filename):
  if not(Path(filename).suffix == '.tex'):
    print("Include the .tex suffix on the end of the file: " + str(filename),file=sys.stderr)

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

  pdfname = Path(filename).with_suffix('.pdf')
  title = metadata['template']['Buc_title']
  author = metadata['template']['Buc_author']
  tags = metadata['template']['Buc_tags']
  templatename = metadata['template']['Buc_hp']
  metadata.update(dbops.addrecord(title, author, tags, pdfname, filename, None, True))

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
    # Run latex twice (not a typo!!!)
    subprocess.run("xelatex -halt-on-error -output-directory . -jobname " + str(Path(filename).with_suffix('')) + " " + f.name, shell=True, check=True)
    subprocess.run("xelatex -halt-on-error -output-directory . -jobname " + str(Path(filename).with_suffix('')) + " " + f.name, shell=True, check=True)

  metadata.pop('content', None)
  metadata.pop('template', None)
  dbops.addrecord(title, author, tags, pdfname, filename, metadata, False)

if len(sys.argv) < 2:
  print("Bucephalus Vacuum TeX Script")
  print("Usage: " + sys.argv[0] + " <filename.tex>")
  sys.exit()

vacuum(sys.argv[1])
