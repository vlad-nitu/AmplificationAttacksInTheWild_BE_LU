#!/bin/bash

# Define input and output files
input_file="domains_of_auth_servers.txt"
output_file="resolved_IPs_auth_servers.txt"
dns_resolver="8.8.8.8"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: The file $input_file does not exist."
    exit 1
fi

# Clear or create the output file
> "$output_file"

# Read each line in the input file
while IFS= read -r line
do
    # Extract the domain to resolve from the second column
    domain_to_resolve=$(echo "$line" | cut -d ',' -f 2 | tr -d '[:space:]' | tr -d '"')

    # Use dig to get the IP address of the domain
    ip_address=$(dig @"$dns_resolver" +short "$domain_to_resolve" A)

    # Extract the primary domain from the first column
    primary_domain=$(echo "$line" | cut -d ',' -f 1 | tr -d '[:space:]')

    # Check if dig found an IP address
    if [[ -n "$ip_address" ]]; then
        # Get the country code of the IP address from ipinfo.io
        country_code=$(curl -s "https://ipinfo.io/$ip_address" | jq -r '.country') # use `jq` for such an JSON output
        # Check if the country code is either BE or LU
        if [[ "$country_code" == "BE" || "$country_code" == "LU" ]]; then
            # Write the original primary domain and the resolved IP to the output file
            echo "$primary_domain,\"$ip_address\"" >> "$output_file"
         fi
     fi
done < "$input_file"

# Temporary file for sorting and removing duplicates
temp_file="temp_resolved_IPs_servers.txt"

# Remove duplicates from the output file
sort "$output_file" | uniq -u > "$temp_file"
mv "$temp_file" "$output_file"

echo "Completed dig_resolve_IPs_auth_servers.sh;  The results are stored in $output_file."

