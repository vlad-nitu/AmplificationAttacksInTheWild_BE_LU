#!/bin/sh

# Check if exactly one argument is provided
if [ $# -ne 2 ]; then
    echo "usage: ./download_shodan.sh <OUTPUT_FILENAME> <PORT_NUMBER>"
    exit 1
fi

OUTPUT_FILENAME="$1"
PORT_NUMBER="$2"
TEMP_FILENAME="temp.json"

shodan download --limit 1000 "$OUTPUT_FILENAME.gz" "country:BE,LU port:${PORT_NUMBER}"

gzip -d "$OUTPUT_FILENAME.gz"

jq -s 'map(.ip_str)' "$OUTPUT_FILENAME" > "$TEMP_FILENAME"

mv "$TEMP_FILENAME" "$OUTPUT_FILENAME"

exit 0