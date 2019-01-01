import sys

import dbops
from pathlib import Path

if len(sys.argv) < 2:
  print("Bucephalus Remove File Script")
  print("Usage: " + sys.argv[0] + " <identifier>")
  sys.exit()

sys.argv.pop(0)
ident = sys.argv.pop(0)

if dbops.remove_record_by_id(ident) == None:
  print("*** Error: failed to remove record.")

