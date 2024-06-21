import json

import numpy as np


def load_json_file(filepath):
    """
    Load the contents of a JSON file and return it as a Python list.
    :param filepath: the path to the file
    :return: Python Array containing the contents of the JSON file
    """
    with open(filepath, 'r') as file:
        return json.load(file)

def aggregate_data(baf_data, asn_data):
    """
    Aggregates the data from the baf_data and asn_data
    :param baf_data: data containing BAF info
    :param asn_data: data containing ASNs (Autonomous System Names) info
    :return: aggregated dict.
    """
    # Create a dictionary to hold the aggregated data
    asn_dict = {}

    # Populate the dictionary with ASN data
    for entry in asn_data:
        ip = entry['ip']
        asn = entry['asn']
        if asn not in asn_dict:
            asn_dict[asn] = {'name': entry['name'], 'description': entry['description'], 'ip_bafs': []}

    # Populate the dictionary with BAF data
    for ip, baf in baf_data:
        for entry in asn_data:
            if entry['ip'] == ip:
                asn = entry['asn']
                asn_dict[asn]['ip_bafs'].append((ip, baf))
                break

    # Filter to only keep ASNs with at least 10 elements in their ip_bafs list
    asn_dict = {asn: data for asn, data in asn_dict.items() if len(data['ip_bafs']) >= 10}

    return asn_dict
def sort_asn_dict_by_mean_baf(asn_dict):
    """
    Sorts a dictionary containing ASN info by the mean BAF
    :param asn_dict: Dictionary containing ASN info
    :return: sorted dict containing same info as asn_dict
    """
    # Calculate the mean BAF for each ASN and sort the dictionary accordingly
    sorted_asn_dict = dict(
        sorted(asn_dict.items(), key=lambda item: np.mean([baf for ip, baf in item[1]['ip_bafs']]), reverse=True))
    return sorted_asn_dict
