#!/bin/bash

# Input file containing domain names
input_file="BE_LU_openpagerank-top-10m-2023-04-16_0900_UTC.csv"

# Output file to store the results
output_file="domains_of_auth_servers.txt"

# DNS server to use for the queries
dns_server="8.8.8.8"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: The file $input_file does not exist."
    exit 1
fi

# Clear or create the output file
> "$output_file"

# Read each line in the input file
while IFS= read -r domain
do
    dig @"$dns_server" "$domain" NS +short | while IFS= read -r auth_server
    do
        if [[ -n "$auth_server" ]]; then
            echo "\"$domain\",\"$auth_server\"" >> "$output_file"
        fi
    done
done < "$input_file"

# Temporary file for sorting and removing duplicates
temp_file="temp_auth_servers.txt"

# Remove duplicates from the output file
sort "$output_file" | uniq -u > "$temp_file"
mv "$temp_file" "$output_file"

echo "Completed. The results are stored in $output_file."