import json
import csv

# File paths
input_json_file = input("Please provide the input file path. It should be of the following format: [`ip1`, `ip2`, ..]")

output_csv_file = input_json_file[:-5] + ".csv" # The CSV file to be created

# Read the JSON data
with open(input_json_file, 'r') as file:
    ip_addresses = json.load(file)

# Append '/32' to each IP address
modified_ips = [ip + '/32' for ip in ip_addresses]

# Write to CSV file
with open(output_csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for ip in modified_ips:
        writer.writerow([ip])  # Write IP address in a single column

print("Conversion completed. The CSV file has been created.")
