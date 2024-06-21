import json
import re
import subprocess

def query_ntp_system(ip):
    """
    Method that runs  starts an `ntpq` subprocess
    :param ip: IP address
    :return: value of `system` key in `ntpq` output, or `System key not found` otherwise
    """
    # Run the ntpq command in a separate subprocess spawned by the Python thread
    result = subprocess.run(['ntpq', '-c', 'rv', ip], capture_output=True, text=True)
    output = result.stdout # Redirect the output to STDOUT (standard out)

    # Look for the 'system' key in the output
    match = re.search(r'system="([^"]+)"', output)
    if match:
        return match.group(1)  # Return the system name
    else:
        return "System key not found"

if __name__ == "__main__":

    input_filepath = input("Please provide the path to the input file\n"
                           "This file should be a JSON file of the following format: [ip1, "
                           "ip2, etc.] and its name should terminate in `_IPs.json`\n")

    if not input_filepath.endswith("_IPs.json"):
        raise ValueError("Please provide a path ending in `_IPs.json`\n")

    with open(input_filepath, "r") as file:
        IPs = json.load(file)

    # Dictionary to store results
    results = {}
    # Process each IP in the list
    for ip in IPs:
        system_value = query_ntp_system(ip)
        print(ip, system_value)
        if system_value != "System key not found":
            results[ip] = system_value

    outfile_path = input_filepath[:-5] + "_system.json"
    with open(outfile_path, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
    print(f"Amplifiers have been successfully written to {outfile_path}")
