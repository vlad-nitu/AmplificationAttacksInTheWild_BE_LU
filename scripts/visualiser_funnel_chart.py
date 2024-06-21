import json

import matplotlib.pyplot as plt
from plotly import graph_objects as go

width = 1600
height = 1024

dns_paths = {
    'protocol': 'dns',
    'before_filtering_root': '../data/censys_all_data/dns_8k_IPs_before_filtering.json',
    'baf_root': '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json',
    # 'after_filtering_root': '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json',
    'max_udp_root': '../data/censys_all_data/dns_8k_IPs_domain_ip:._ANY_max_udp.json'
}

ntp_paths = {
    'protocol': 'ntp',
    'before_filtering_root': '../data/censys_all_data/ntp_wild_15k_before_filtering.json',
    'baf_root': '../data/censys_all_data/ntp_monlist_wild_ntp_query_type:monlist_baf.json',
    'after_filtering_basic_root': '../data/censys_all_data/ntp_wild_15k.json',  # Monlist
    'after_filtering_version_root': '../data/censys_all_data/ntp_version_wild_ntp_query_type:version_baf.json'
}

memcached_paths = {
    'protocol': 'memcached',
    'before_filtering': '../data/censys_all_data/memcached_11may_before_filtering.json',
    'baf_root': '../data/censys_all_data/memcached_11may_theory_max_baf:True_baf.json',
    'after_filtering_stats_root': '../data/censys_all_data/memcached_11may.json',
}


def read_ntp_basic():
    """
    Obtain all IPs after the filtering step (i.e.: that answer to Mode 3 (Client) query type Added as an extension
    after Midterm presentation (at Supervisor Griffioen) inquiry, which was interested in how many NTP servers are
    acutally not responding because they are closed to the public, and how many of them are offline (i.e.: ICMP
    Cannot be reached response due to IP Churning, etc.)
    """

    ntp_basic_path = input(
        "Please input the path to the file that was obtained after filtering non-responsive NTP servers"
        "(i.e.: after running search_amplifeis.py on _before_filtering.json file)\n"
        "This file should be a JSON file of the following format: [[ip1, ip2, ...], "
        "and should end in `.json`, having the same prefix as the `_before_filtering.json` file\n")

    with open(ntp_basic_path, 'r') as ntp_basic_file:
        ntp_basic_arr = json.load(ntp_basic_file)
        return ntp_basic_arr


def max_udp_buff_size_statistics(input_filepath) -> dict[str, float]:
    """
    Reads user's data and return `max_dns_dict`, which holds EDNS0 Buffer Size statistics
    :param input_filepath: file path to the JSON input file
    :return: max_dns_dict, which holds kv pairs of {IP: max_UDP_buff_size}
    """
    max_udp_file_path = input("Please input the file path to the EDNS Buffer Size file statistics if you wish such "
                              "statistics\nThe file path should end in `_max_udp.json`\nIf you do not want these "
                              "statistics, type: `No`)\n")
    if max_udp_file_path == "No":  # input_filepath[:-9] + "_max_udp.json"
        return {}
    try:
        with open(max_udp_file_path, 'r') as max_udp_file:
            max_dns_dict_array_singleton = json.load(max_udp_file)  # Singleton of dict
            max_dns_dict = {}
            for kv_pair in max_dns_dict_array_singleton:
                max_dns_dict.update(kv_pair)
            return max_dns_dict
    except FileNotFoundError:
        return {}


def read_ips_from_json(protocol) -> list[str]:
    """
    Reads all the IPs from a file that is found at filepath `filepath`, which is expected to be a JSON file
    :param protocol: `ntp` or `memcached`
    :return: list of IP in list[str] format
    """
    try:
        if protocol == "memcached":
            prompt = "This file should contain all Memcached servers that answered to `stats`\n"
        else:
            prompt = "This file should contain all NTP servers that answered to `version`\n"

        filepath = input("Provide the file path of the JSON file that has a list of IPs (without BAFs); the initial "
                         "file that was inputted to `measure_baf.py`, which (should be) the output file of "
                         f"`search_amplifiers.py`; {prompt}")
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError("File was not found")


if __name__ == "__main__":
    protocol = input("What protocol would you like to visualise?\nPossible options: dns, ntp or memcached\n")
    if protocol not in ["dns", "ntp", "memcached"]:
        raise ValueError("Protocol not supported")

    before_filtering_filepath = input(
        "Please provide the path to the input file used before the filtering step\nThe file should be a JSON file "
        "of the following"
        "format: [ip1, ip2, ...] and its name should terminate in `_before_filtering.json`\n")
    if not before_filtering_filepath.endswith("_before_filtering.json"):
        raise ValueError("The path you provided does not contain `before_filtering.json`")

    with open(before_filtering_filepath, 'r') as before_filtering_file:
        before_filtering_arr = json.load(before_filtering_file)
        num_servers_before_filtering = len(before_filtering_arr)

    input_filepath = input("Please provide the path to the input file\n"
                           "This file should be a JSON file of the following format: [[ip1, baf1], "
                           "[ip2, baf], etc.]}] and its name should terminate in `_baf.json`\n").lower()

    if not input_filepath.endswith("_baf.json"):
        raise ValueError("Provided input filepath does not end in `_baf.json")

    try:
        with (open(input_filepath, 'r') as input_file):
            input_arr = json.load(input_file)  # Parse data from JSON into Python built-in array

            if protocol == "dns":
                total_IPs, open_resolvers = num_servers_before_filtering, len(input_arr)
                bafs_gte10 = sum([1 for [_, baf] in input_arr if baf >= 10])
                bafs_gte30 = sum([1 for [_, baf] in input_arr if baf >= 30])
                bafs_gte80 = sum([1 for [_, baf] in input_arr if baf >= 80])

                udp_buff_size_dict = max_udp_buff_size_statistics(input_filepath)
                if udp_buff_size_dict:
                    bafs_gte80_max_udp_diff_from_1232 = sum([1 for [ip, baf] in input_arr
                                                             if baf >= 80
                                                             and ip in udp_buff_size_dict
                                                             and udp_buff_size_dict[ip] is not None
                                                             and udp_buff_size_dict[ip] != 1232])

                    numbers = [total_IPs, open_resolvers, bafs_gte10, bafs_gte30, bafs_gte80,
                               bafs_gte80_max_udp_diff_from_1232]
                    stages = ["DNS servers", "Open resolvers", "BAF >= 10x", "BAF >= 30x", "BAF >= 80x",
                              "Buff Size != 1232"]
                else:
                    numbers = [total_IPs, open_resolvers, bafs_gte10, bafs_gte30, bafs_gte80]
                    stages = ["DNS servers", "Open resolvers", "BAF >= 10x", "BAF >= 30x", "BAF >= 80x"]

            elif protocol == "ntp":  # ../data/censys_all_data/ntp_monlist_wild_ntp_query_type:monlist_baf.json

                all_ntp_ips_answering_to_basic = read_ntp_basic()
                all_ntp_ips_answering_to_version = read_ips_from_json(
                    protocol)  # ../data/censys_all_data/ntp_version_wild_ans_to_version_IPs.json
                total_IPs, open_to_basic_ntp, open_to_version_ntp, open_to_monlist_ntp = num_servers_before_filtering, len(all_ntp_ips_answering_to_basic), len(all_ntp_ips_answering_to_version), len(input_arr)
                bafs_gte6 = sum([1 for [_, baf] in input_arr if baf >= 6])
                bafs_gte18 = sum([1 for [_, baf] in input_arr if baf >= 18])
                bafs_gte30 = sum([1 for [_, baf] in input_arr if baf >= 3000])

                numbers = [total_IPs, open_to_basic_ntp, open_to_version_ntp, open_to_monlist_ntp, bafs_gte6,
                           bafs_gte18,
                           bafs_gte30]
                stages = ["NTP servers", "Open servers", "Ans. to `version`", "Ans. to`monlist`", "BAF >= 6x",
                          "BAF >= 18x",
                          "BAF >= 3000x"]

            else:  # Memcached
                all_memcached_ips = num_servers_before_filtering
                all_memcached_ips_answering_to_stats = read_ips_from_json(protocol)
                total_IPs, memcached_answering_to_stats = all_memcached_ips, len(all_memcached_ips_answering_to_stats)
                bafs_gte100 = sum([1 for [_, baf] in input_arr if baf >= 100])
                bafs_gte3k = sum([1 for [_, baf] in input_arr if baf >= 3000])
                bafs_gte50k = sum([1 for [_, baf] in input_arr if baf >= 50000])

                numbers = [total_IPs, memcached_answering_to_stats, bafs_gte100, bafs_gte3k, bafs_gte50k]
                stages = ["Memcached servers", "Ans. to `stats`", "BAF >= 100x", "BAF >= "
                                                                                              "3'000x",
                          "BAF >= 50'000x"]

            fig = go.Figure(go.Funnel(
                y=stages,
                x=numbers,
                textposition="auto", # Move text from stages inside plot
                textinfo="none",  # Hide default textinfo
                texttemplate="%{value}<br>%{percentPrevious:.2%}",
                # Custom text template for value and percentage with two decimal places
                textfont=dict(size=34) # Increase font size for the text inside the funnel
                )
            )

            # Update layout to increase font size for the stages
            fig.update_layout(
                yaxis=dict(
                    title=dict(font=dict(size=46)),  # Increase font size for the stages
                    tickfont=dict(size=46),  # Increase font size for the y-axis ticks (stages)
                    ticklabelposition='inside'
                )
            )

            # Step 1: Draw Funnel Chart to show the process's results
            output_filepath = input_filepath[:-9] + "_funnel_chart.png"
            fig.write_image(output_filepath, width=width, height=height)

            # Step 2: Draw BoxPlot for statistics about the data
            data = [baf for [_, baf] in input_arr]
            plt.figure(figsize=(10, 6))
            plt.title(f"Boxplot of {protocol.upper()} BAF results")
            plt.ylabel('BAF (Bandwidth Amplification Factor)')  # Adding a label to the y-axis
            plt.boxplot(data)
            boxplot_path = output_filepath = input_filepath[:-9] + "_boxplot.png"
            plt.savefig(boxplot_path)
            plt.pause(3)
            plt.close()
    except FileNotFoundError:
        raise ValueError("The file was not found. Please check the file path.")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")
