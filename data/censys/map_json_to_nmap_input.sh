#!/bin/bash

# usage "./map_json_to_nmap_input.sh <IN_FILEPATH> <OUT_FILEPATH> "
# Check if exactly one argument is provided
if [ $# -ne 2 ]; then
    echo "usage ./map_json_to_nmap_input.sh <IN_FILEPATH> <OUT_FILEPATH>"
    exit 1
fi

IN="$1"
OUT="$2"
sed -e 's/\[//g' -e 's/\]//g' -e 's/"//g' -e 's/,//g' -e 's/^[ \t]*//' -e '/^$/d' "$IN" > "$OUT"

exit 0
