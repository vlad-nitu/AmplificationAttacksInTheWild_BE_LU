#!/bin/bash

# usage "./remove_baf_eq_0_entries <IN_FILEPATH>"
# Check if exactly one argument is provided

IN_FILEPATH="$1"

if [ $# -ne 1 ]; then
    echo "usage ./remove_baf_eq_0_entries.sh <IN_FILEPATH>"
    exit 1
fi

jq 'map(select(.[1] != 0))' "$IN_FILEPATH"

exit 0