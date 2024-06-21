#!/bin/bash

# usage "./nmap_xml_csv_json.sh <IP_RANGE> <OUTPUT_FILE_NAME> "
# Check if exactly one argument is provided
if [ $# -ne 2 ]; then
    echo "usage: ./nmap_xml_csv_json.sh <IP_RANGE> <OUTPUT_FILE_NAME>"
    exit 1
fi


IP_RANGE="$1"
OUTPUT_FILE_NAME="$2"
XML="$OUTPUT_FILE_NAME.xml"
CSV="$OUTPUT_FILE_NAME.csv"
JSON="$OUTPUT_FILE_NAME.json"

# NMAP active scan and output to XML file "OUTPUT_FILE_NAME.xml"
sudo nmap -sU -p 53,123,11211 --script=dns-recursion "$IP_RANGE" -oX "$XML"
# Map XML to JSON using user-defined `.xsl` file that defines the rules of mapping
xsltproc nmap-to-csv_recursion.xsl "$XML" > "$CSV"

# Python one-liner script to map CSV to JSON
# Source: https://stackoverflow.com/questions/44780761/converting-csv-to-json-in-bash
cat "$CSV" | python -c 'import csv, json, sys; print(json.dumps([dict(r) for r in csv.DictReader(sys.stdin)]))' > "$JSON"
# Exit successfully
exit 0

