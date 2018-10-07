import json
import pystache

from pathlib import Path

import os
import sys

directory1=Path.home()/"bucephalus"/"prototypes"
directory2=Path(__file__).parent/"prototypes"

def main(filename, templatename, output=None):
  templatepath = directory1/(templatename + ".mustache")
  if not (templatepath.exists()):
    templatepath = directory2/(templatename + ".mustache")
    if not(templatepath.exists()):
      print("No template found: " + str(templatepath),file=sys.stderr)
      sys.exit(1)

  parsed = decode(filename)
  rendered = fill(templatepath, parsed)
  return rendered

def decode(filename):
  with open(filename) as f:
    parsed = {}
    inContent = False
    decoder = json.JSONDecoder()
    metadata = ""
    content = ""
    for line in f:
      if("===" in line):
        inContent = True
        continue
      if(not(inContent)):
        metadata = metadata + line
      else:
        content = content + line

    parsed.update(decoder.decode(metadata))
    parsed["content"] = content
    return parsed

def fill(template, data):
  with open(template) as f:
    templateContent = f.read()
    return pystache.render(templateContent, data)
