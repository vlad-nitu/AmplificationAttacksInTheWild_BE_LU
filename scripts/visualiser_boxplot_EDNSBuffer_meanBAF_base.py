import json
import re


def preprocess_data():
    """
    Reads data from two files speciifed by two filepaths from the user, one of BAFs, one of Max UPDs (ENDS0 Buffer Size)
    Computes the treshold that the response should not exceed (max answer)
    Adds EDNS0 Buffer Size and BAF to result dict
    Removes entries w/ less than items per category to ensure statistical significance
    Sorts EDNS0 dict increasingly by the BAF
    :return: (req_size, filepath, result_dict)
    """
    print("Please provide the path to the input file paths you would like to compute EDNS0 Buffer Size "
          "v.s. Mean BAF Box Plot statistics\n")
    bafs_filepath = input(
        "1. This file should be a JSON file of the following format: [[ip1, BAF1], [ip2, BAF2], "
        "etc] and should end in `baf.json` \n")

    if not bafs_filepath.endswith("_baf.json"):
        raise ValueError("The filepath does not end in `_baf.json`")

    max_udp_filepath = input("2. This file should be a JSON file of the following format: [{ip1: EDNS0_buf_size1}, "
                             "{ip2: EDNS0_buf_size2}, etc] and should end in `max_udp.json` \n")
    if not max_udp_filepath.endswith("_max_udp.json"):
        raise ValueError("The filepath does not end in `_max_udp.json`")

    domain_ip = re.search(r'domain_ip:([^_]+)', bafs_filepath).group(1)
    print(domain_ip)
    if domain_ip.endswith("."):  # Remove trailing `.`
        domain_ip = domain_ip[:-1]
    req_size = 28
    if domain_ip:  # not empty
        req_size += len(domain_ip) + 1

    agg_dict = {}
    with open(bafs_filepath, "r") as bafs_file:
        with open(max_udp_filepath, "r") as max_udp_file:
            # Step 1 -> append EDNS0 Buffer Size in the dict
            IPS_max_udp = json.load(max_udp_file)
            for IP_EDNS0_buf in IPS_max_udp:
                for ip, max_udp_buff_size in IP_EDNS0_buf.items():  # Singleton dict, but is not subscriptable
                    if max_udp_buff_size is not None:
                        agg_dict[ip] = [max_udp_buff_size]

            # Step 2 -> append the BAFs in the dict
            IPS_bafs = json.load(bafs_file)
            for IP_baf in IPS_bafs:
                ip = IP_baf[0]
                baf = IP_baf[1]
                if ip in agg_dict:  # max_udp_buff_size of this IP is not None
                    agg_dict[ip].append(baf)

            # Step 3: Organize BAFs by EDNS0 buffer size for the box plot
            bafs_per_EDNS_buf = {}  # EDNS_buf_size -> list of BAFs

            for arr in agg_dict.values():
                if len(arr) != 2:  # for this IP, there's no BAF recorded
                    continue
                EDNS_buf_size = arr[0]
                BAF = arr[1]
                if EDNS_buf_size not in bafs_per_EDNS_buf:
                    bafs_per_EDNS_buf[EDNS_buf_size] = [BAF]
                else:
                    bafs_per_EDNS_buf[EDNS_buf_size].append(BAF)

            # Remove entries with less than 3 data points for statistical significance
            bafs_per_EDNS_buf = {k: v for k, v in bafs_per_EDNS_buf.items() if len(v) >= 3}

            # Sort the EDNS0 buffer sizes in increasing order
            sorted_bafs_per_EDNS_buf = dict(sorted(bafs_per_EDNS_buf.items()))
            return req_size, bafs_filepath, sorted_bafs_per_EDNS_buf
