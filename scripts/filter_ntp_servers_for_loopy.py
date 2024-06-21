import json

# File paths
input_file_path = '../data/censys_all_data/ntp_ALL_wild.json'  # Replace with the path to your input JSON file
output_file_path = '../data/censys_all_data/ntp_ALL_ans_to_loopy.json'  # Replace with the desired path for the output file
ip_list_file_path = '../data/censys_all_data/ntp_ans_to_loopy_IPs.json'  # Replace with the path to the file containing IPs to filter by

def load_ip_list(file_path):
    with open(file_path, 'r') as file:
        ip_list = json.load(file)
    return ip_list

def filter_records_by_ip(input_file_path, output_file_path, ip_list_file_path):
    # Load IP list from file
    ip_list = load_ip_list(ip_list_file_path)
    
    # Load records from JSON file
    with open(input_file_path, 'r') as file:
        records = json.load(file)
    
    # Filter records by IP
    filtered_records = [record for record in records if record.get("ip") in ip_list]
    
    # Save filtered records to output file
    with open(output_file_path, 'w') as file:
        json.dump(filtered_records, file, indent=4)
    
    print(f"Filtered records saved to {output_file_path}")


# Run the filtering function
filter_records_by_ip(input_file_path, output_file_path, ip_list_file_path)

