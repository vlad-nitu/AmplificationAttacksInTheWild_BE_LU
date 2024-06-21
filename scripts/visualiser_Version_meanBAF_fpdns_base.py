import json

root_fpdns = '../data/censys_all_data/dns_8k_IPs_._fpdns.json'
bg_fpdns = '../data/censys_all_data/bg/dns_8k_IPs_bg._fpdns.json'
def preprocess_data():
    """
    Read data from user & preprocess it.
    :return: (versions, baf_values_list, input_filepath)
    """
    input_filepath = input("Please provide the path to the input file\n"
                           "This file should be a JSON file of the following format: "
                           "{version1: [cnt1, mean_BAF1, {ip1: BAF1, ip2: BAF2}], "
                           "version2: [cnt2, mean_BAF2, {ip1: BAF1, ip2: BAF2}], etc.} and its name should terminate "
                           "in `_fpdns.json`\n").lower()

    if not input_filepath.endswith("_fpdns.json"):
        raise ValueError("Input file is not a _fpdns.json type of file")

    try:
        with open(input_filepath) as json_file:
            fpdns_dict = json.load(json_file)
    except FileNotFoundError:
        raise ValueError("The input file was not found")

    # Extract data for plotting
    data = []

    for key, value in fpdns_dict.items():
        if value[0] >= 5:  # Only store Versions with >= 5 IPs
            baf_values = list(value[2].values())
            data.append((key, baf_values))

    # Sort data by mean of BAF values in decreasing order
    data.sort(key=lambda x: sum(x[1]) / len(x[1]), reverse=True)

    # Extract sorted data
    versions = [item[0] for item in data]
    baf_values_list = [item[1] for item in data]

    return versions, baf_values_list, input_filepath


