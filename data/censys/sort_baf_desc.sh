#!/bin/bash

# usage "./sort_baf_desc.sh <IN_FILEPATH>"
# Check if exactly one argument is provided

IN_FILEPATH="$1"

if [ $# -ne 1 ]; then
    echo "usage ./sort_baf_desc.sh <IN_FILEPATH> <OUT_FILEPATH>"
    exit 1
fi


jq 'sort_by(.[-1]) | reverse' "$IN_FILEPATH"

exit 0