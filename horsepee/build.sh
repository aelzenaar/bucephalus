#!/bin/bash

template="$1"
file="$2"
output="$3"

temp_file=$(mktemp)
# trap "rm -f $temp_file" 0 2 3 15

python -c "from horsepee import *; print(fill(\"$template\", decode(\"$file\")))" > $temp_file

latexargs="-halt-on-error -output-directory . -jobname=\"$output\" $temp_file"
pdflatex $latexargs && pdflatex $latexargs
