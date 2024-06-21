#!/bin/bash

# Not recursive: no answer OR grep "timed out"
# Else: Recursive DNS

#!/bin/bash

# Input file containing IP addresses
input_file="dns_servers_wild.json"

# Output file for storing recursive DNS IPs
output_file="recursive_dns_servers_wild.json"

# Temporary file for intermediate results
tmp_file="temp_results.txt"

# Initialize or clear the output file
echo "[]" > "$output_file"

# Read IP addresses from the JSON array in the input file
ips=$(jq -r '.[]' "$input_file")

# Check each IP if it is a recursive DNS server
for ip in $ips; do
    echo "Checking $ip..."
    # Use dig to query google.com from the specific DNS server, timeout set to 5 seconds
    result=$(dig @${ip} google.com +rec +time=2 +tries=1 +short)

    if [[ -z "$result" ]]; then # result is empty
        echo "$ip is not recursive: no answer"
    elif [[ $(echo "$result" | grep -q "timed out"; echo $?) -eq 0 ]]; then
         echo "$ip is not recursive: request timed out"
    else
        echo "$ip is a recursive DNS"
        # Append IP to the temporary file if it is recursive
        echo "\"$ip\"," >> "$tmp_file"
    fi
done

# Format the output JSON file
echo "[" > "$output_file"
cat "$tmp_file" | sed '$ s/,$//' >> "$output_file"  # Remove the last comma
echo "]" >> "$output_file"

# Clean up temporary file
rm "$tmp_file"

echo "Completed. Recursive DNS servers are stored in $output_file."
