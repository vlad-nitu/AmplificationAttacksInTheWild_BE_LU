#!/bin/bash

# Define input and output files
input="openpagerank-top-10m-2023-04-16_0900_UTC.csv"
output="BE_LU_openpagerank-top-10m-2023-04-16_0900_UTC.csv"

# Check if input file exists
if [ ! -f "$input" ]; then
    echo "Error: Input file does not exist."
    exit 1
fi

# Create or clear the output file
> "$output"

# Read the input file and filter domains
while IFS= read -r line
do
    if echo "$line" | grep -E '\.be"|\.lu"' > /dev/null; then
      # Extract the domain using cut and delimiter ","
      domain=$(echo "$line" | cut -d ',' -f 2 | tr -d '"')
      echo "$domain" >> "$output"
    fi
done < "$input"

echo "Filtered domains have been stored in $output."

