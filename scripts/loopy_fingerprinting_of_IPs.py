import logging

import pandas as pd
import pickle
import json

def extract_unique_ips_from_pkl(file_path):
    """
    Method that extracts unique IPs from the .pkl file
    :param file_path:  the file path to the `.pkl` file
    :return: unique IPs of file located in `file_path`
    """

    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    
    unique_ips = set()
    for key, (list1, list2) in data.items():
        unique_ips.update(list1)
        unique_ips.update(list2)
    
    return unique_ips

def get_dns_product_vendor_from_json(file_path, unique_ips):
    """
    Method that reads a JSON file and obtains the product and vendor for each DNS server
    :param file_path: file path to the JSON file
    :param unique_ips: unique IPs list
    :return: (ip, (product, vendor)) dict.
    """
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    
    ip_info = {entry["ip"]: (entry["product"], entry["vendor"]) for entry in json_data}
    
    result = {ip: ip_info[ip] for ip in unique_ips if ip in ip_info}
    
    return result

def get_ntp_system_from_json(json_file_path, unique_ips):
    """
    Method that reads a JSON file and obtains the System/OS for each NTP server
    :param json_file_path: file path to the JSON file
    :param unique_ips: unique IPs list
    :return: (ip, system/OS) dict.
    """
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
    result = {ip: json_data[ip] for ip in unique_ips if ip in json_data}
    return result

    
def write_back_to_json(result, output_filepath, protocol) -> None:
    """
    Method that writes/persists the ouput in a JSON output file
    :param result: (ip, (product, vendor)) dict
    :param output_filepath: file path of the output file
    :param protocol: DNS or NTP in str format
    :return: None
    """

    if protocol == "DNS":
        result_list = [{"ip": ip, "product": product, "vendor": vendor} for ip, (product, vendor) in result.items()]
    else:
        result_list = [{"ip": ip, "system": system} for ip, system in result.items()]

    with open(output_filepath, 'w') as file:
        json.dump(result_list, file, indent=4)

def main():
    # Replace with the actual path to your .pkl file
    dns_pkl_file_path = '../loop-DoS-RP/dns_rem_100IPs_constraint_identified_cycles_results.pkl'
    ntp_pkl_file_path = '../loop-DoS-RP/ntp_rem_100IPs_constraint_identified_cycles_results.pkl'

    dns_json_file_path = ('../data//censys_all_data/dns_fingerprinting/'
                          'dns_8k_wild_product_vendor_fingerprinting_preprocessed.json')
    ntp_json_file_path = '../data/censys_all_data/ntp_monlist_wild_ans_to_monlist_IPs_system.json'

    pkl_file_path = ntp_pkl_file_path
    json_file_path = ntp_json_file_path

    protocol = input("What protocol do you want to analyse?\n"
                     "Options: DNS or NTP\n")

    if protocol not in {"DNS", "NTP"}:
        raise ValueError(f"Invalid protocol: {protocol}")
    
    unique_ips = extract_unique_ips_from_pkl(pkl_file_path)
    temp_filepath = 'file.txt'
    with open(temp_filepath, 'w') as fl:
        json.dump(list(unique_ips), fl, indent=4)
    if protocol == "DNS":
        product_vendor_info = get_dns_product_vendor_from_json(json_file_path, unique_ips)
    else:
        product_vendor_info = get_ntp_system_from_json(json_file_path, unique_ips)

    output_filepath = pkl_file_path[:-4] + '_fingerprinting.json'
    write_back_to_json(product_vendor_info, output_filepath, protocol)

    logging.info(f"The output was successfully written to: {output_filepath}")

if __name__ == "__main__":
    main()

