#!/bin/bash

# Check if exactly one argument is provided
if [ $# -ne 1 ]; then
    echo "usage: ./awk_parse_shodan_to_json.sh <file_path>"
    exit 1
fi

FILE_PATH="$1"

awk 'BEGIN {
    print "["
    first = 1
}
{
    # Split the line by space for initial fields, and then handle special splitting for `\n`
    match($0, /\\n/); # Find position of \n in the string
    if (RSTART > 0) {
        pre = substr($0, 1, RSTART-1); # Text before \n
        post = substr($0, RSTART+2); # Text after \n
        gsub(/^[ \t]+|[ \t]+$/, "", post); # Trim leading and trailing whitespace from post
        split(pre, parts, " "); # Split the first part by spaces
        if (!first) printf "},\n"; # Print comma before starting a new record except for the first one
        printf "{"
        printf "\"ip\": \"%s\", ", parts[1]
        printf "\"port\": \"%s\", ", parts[2]
        if (parts[3] == "") {
            printf "\"host\": null, "
        } else {
            printf "\"host\": \"%s\", ", parts[3]
        }
        printf "\"resolver_details\": \"%s\"", post
        first = 0
    } else {
        split($0, parts, " "); # Split by spaces if there is no \n
        if (!first) printf "},\n"; # Print comma before starting a new record except for the first one
        printf "{"
        printf "\"ip\": \"%s\", ", parts[1]
        printf "\"port\": \"%s\", ", parts[2]
        printf "\"host\": \"%s\", ", parts[3]
        printf "\"resolver_details\": null"
        first = 0
    }
}
END {
    print "}\n]"
}' "$FILE_PATH"
