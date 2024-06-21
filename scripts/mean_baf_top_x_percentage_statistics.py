import json
import logging

root_any = '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json'
root_dnskey = '../data/censys_all_data/dns_8k_IPs_root_DNSKEY_baf.json'

bg_any =  '../data/censys_all_data/bg/dns_8k_IPs_domain_ip:bg._dns_query_type:ANY_max_udp_size:True_baf.json'
bg_dnskey = '../data/censys_all_data/bg/dns_8k_IPs_bg_DNSKEY_baf.json'

sl_any = '../data/censys_all_data/sl/dns_8k_IPs_domain_ip:sl._dns_query_type:ANY_max_udp_size:False_baf.json'

ve_any = '../data/censys_all_data/ve/dns_8k_IPs_domain_ip:ve._dns_query_type:ANY_max_udp_size:False_baf.json'

auth_any = '../data/pagerank/dns_ANY_wild_baf.json'

def load_data(file_path):
    """
    Method used to read data from the user
    :param file_path: the path to the JSON file
    :return: Data in Python Array format
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_user_input():
    """
    Read a floating point number from the user between 0 and 100, inclusively
    :return: x in [0, 100], else: "Invalid Input" log warning
    """
    while True:
        try:
            x = float(input("Enter the percentage of IPs to get statistics on (e.g., 10 for 10%): "))
            if 0 < x <= 100:
                return x
            else:
                logging.warning("Please enter a value between 0 and 100.")
        except ValueError:
            logging.warning("Invalid input. Please enter a numeric value.")

def aggregate_top_percent(data, percentage):
    """
     Aggregate the top `percentage`% amplifiers, sorted decreasingly by BAF (most-vulnerable first)
    :param data:
    :param percentage:
    :return: (agg_baf_top_percentage, top_BAFs_IPs_top_percentage)
    """

    # Sort the data by BAF in descending order
    sorted_data = sorted(data, key=lambda x: x[1], reverse=True)
    
    # Calculate the number of IPs to consider
    num_ips = int(len(sorted_data) * (percentage / 100))
    
    # Get the top x% BAFs
    top_bafs = sorted_data[:num_ips]
    
    # Aggregate the BAFs
    aggregate_baf = sum(ip[1] for ip in top_bafs) / num_ips
    
    return aggregate_baf, top_bafs

def main():
    file_path = input("Please input the file path\n"
                      "It should be of the following format: [[ip1, baf1], [ip2, baf2], ..]\n"
                      "It should terminate in _baf.json\n")

    if not file_path.endswith("_baf.json"):
        raise ValueError("The file path does not end in _baf.json")
    data = load_data(file_path)
    
    percentage = get_user_input()
    aggregate_baf, _ = aggregate_top_percent(data, percentage)
    
    print(f"The aggregate BAF of the top {percentage}% IPs is: {aggregate_baf}")

if __name__ == "__main__":
    main()

