import sys

import dbops
from pathlib import Path

if len(sys.argv) < 4:
  print("Bucephalus Add File Script")
  print("Usage: " + sys.argv[0] + " <filename> <title> <author> <tag1> ... <tagN>")
  sys.exit()

sys.argv.pop(0)
filename = sys.argv.pop(0)
title = sys.argv.pop(0)
author = sys.argv.pop(0)
tags = sys.argv

print(filename)

if dbops.addrecord(title, author, tags, filename) == None:
  print("Error")
