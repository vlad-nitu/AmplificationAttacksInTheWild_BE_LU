#!/bin/bash

# File containing JSON array of IP addresses
ip_file="$1" # TODO: Check if ip_file of form `.json`
domain_ip="$2"
query_type="$3"

# usage "./get_max_udp.sh <INPUT_FILE> <DOMAIN_IP> <QUERY_TYPE>"
# Check if exactly one argument is provided
if [ $# -ne 3 ]; then
    echo "usage ./get_max_udp.sh <INPUT_FILE> <DOMAIN_IP> <QUERY_TYPE>"
    exit 1
fi

# Extract the base name without the extension
base_name=$(basename "$ip_file" .json)
# Define the output file
output_file="${base_name}_${domain_ip}_${query_type}_max_udp.json"


# Read IP addresses from the JSON file (assuming a simple one-line JSON array format)
ips=($(jq -r '.[]' $ip_file))  # Requires jq installed

# Create an empty array to hold the results
declare -a results

# Loop through each IP address
for ip in "${ips[@]}"; do
    # Perform the DNS query using dig
    output=$(dig @$ip "$domain_ip" "$query_type" +bufsize=4096 +notcp)

    # Extract the UDP payload size using grep and awk
    udp_payload_size=$(echo "$output" | grep -o 'udp: [0-9]*' | awk '{print $2}')

    # Check if we found the UDP payload size and add it to the results array
    if [[ -n "$udp_payload_size" ]]; then
        # Append the result in the format ['ip', max_udp_value]
        results+=("{\"$ip\": $udp_payload_size}")
    else
        # Handle the case where no payload size was found
        results+=("{\"$ip\": null}")
    fi

    echo "$ip processed"
done

# Begin constructing the JSON output
echo '[' > $output_file
first=1  # This flag helps in formatting the JSON array

# Append each result to the JSON file
for result in "${results[@]}"; do
    if [[ $first -eq 1 ]]; then
        echo "  $result" >> $output_file
        first=0
    else
        echo ", $result" >> $output_file
    fi
done

# Close the JSON array
echo ']' >> $output_file

# Print the JSON file content
cat $output_file
