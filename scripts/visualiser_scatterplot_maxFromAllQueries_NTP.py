import json
import re
import plotly.graph_objects as go


get_restrict_path = '../data/censys_all_data/ntp_monlist_wild_ans_to_monlist_IPs_ntp_query_type:get_restrict_baf.json'
peer_list_path = '../data/censys_all_data/ntp_monlist_wild_ans_to_monlist_IPs_ntp_query_type:peer_list_baf.json'
peer_list_sum_path = '../data/censys_all_data/ntp_monlist_wild_ans_to_monlist_IPs_ntp_query_type:peer_list_sum_baf.json'
monlist_path = '../data/censys_all_data/ntp_monlist_wild_ntp_query_type:monlist_baf.json'
system_path = '../data/censys_all_data/ntp_monlist_wild_ans_to_monlist_IPs_system.json'

cisco_get_restrict_path = '../data/censys_all_data/cisco_IPs_get_restrict_baf.json'
cisco_peer_list_path = '../data/censys_all_data/cisco_IPs_get_peer_list_baf.json'
cisco_peer_list_sum_path = '../data/censys_all_data/cisco_IPs_get_peer_list_sum_baf.json'
cisco_monlist_path = '../data/censys_all_data/cisco_IPs_get_monlist_baf.json' 
cisco_system_path = '../data/censys_all_data/ntp_cisco_IPs_system.json'

SYMBOLS = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
]

width = 1600
height = 1024

def transform_array_into_dict(arr):
    """
    Helper method that converts array [IP, BAF] to dict {IP: BAF} as a preprocessing step
    :param arr: array
    :return: dict
    """
    dictionary = {ip: baf for ip, baf in arr}
    return dictionary


def read_array_file(filepath):
    """
    Read the array from file path `filepath', then converts it to a dictionary
    :param filepath: filepath provided by user to JSON file
    :return: dict (from array)
    """
    with (open(filepath, "r") as file):
        input_arr = json.load(file)
        input_dict = transform_array_into_dict(input_arr)
    return input_dict


def read_dict_file(filepath):
    """
    Read the dictionary from file path `filepath`, that contains an Object in JSON format
    :param filepath: file path provided by user to JSON file
    :return: input dict
    """
    with (open(filepath, "r") as file):
        input_dict = json.load(file)
    return input_dict


def invert_dict(ip_to_system_dict):
    """
    Helper method that inverts the dict {IP: System} to {System, listOfIPs}
    :param ip_to_system_dict: {IP: System} dict
    :return: {System: listOfIPs} dict
    """
    inverted_dict = {}
    for ip, system in ip_to_system_dict.items():
        if system not in inverted_dict:
            inverted_dict[system] = [ip]
        else:
            inverted_dict[system].append(ip)
    return inverted_dict


def extract_before_special_chars(s):
    """
    Helper method that extracts string before special characters
    :param s: input strign
    :return: string before special characters
    """
    match = re.match(r'^[^/\d-]+', s)
    return match.group(0) if match else s

# Test examples
examples = [
    "JUNOS20.2R3-S2.5",
    "Linux/3.10.0-514.16.1.el7.x86_64",
    "NoSpecialCharacters",
    "Example-Text/With/Multiple/Special/Characters"
]

def extract_before_special_chars_from_dict(ip_to_system_dict_unfiltered):
    """
    Preprocess w/ Regex to group OSes based on the main version
    :param ip_to_system_dict_unfiltered: dict before grouping
    :return: dict after grouping: {ip1: system1, ip2: system2, etc.}
    """
    ip_to_system_dict = {}
    for ip, system in ip_to_system_dict_unfiltered.items():
        # process the system/OS string to only contain the base version i.e.: Linux instead of Linux/2.18
        ip_to_system_dict[ip] = extract_before_special_chars(system)
    return ip_to_system_dict


def draw_scatterplot(system_filepath, max_NTP_response_per_system, system_ip_counts) -> None:
    """
    Method that drwas scatterplot for  'max_NTP_response_per_system' data, and also displays
    the # of IPs per System on the OX axis

    :param system_filepath: input file path used to name the ouput file path
    :param max_NTP_response_per_system: {idx: (system, BAFs)} dict
    :param system_ip_counts: {system: countOfIPs} dict
    :return: None
    """
    # Color mapping for query types & map NTP Mode 7 (Private) query types to integers (like an enum)
    get_index_of_type = {
        'get_restrict': 0,
        'peer_list_sum': 1,
        'peer_list': 2
    }
    if bool_monlist:
        get_index_of_type['monlist'] = 3
    color_mapping = {
        'get_restrict': 'red',
        'peer_list_sum': 'blue',
        'peer_list': 'orange'
    }
    if bool_monlist:
        color_mapping['monlist'] = 'green'

    # Prepare the figure
    fig = go.Figure()

    for idx, (system, values) in enumerate(max_NTP_response_per_system.items()):
        # Extract BAFs and types
        bafs = [v[0] for v in values]
        types = [v[1] for v in values]

        # Add scatter plot points for the current system
        fig.add_trace(go.Scatter(
            x=[f"{system}<br>({system_ip_counts[system]})"] * len(bafs),  # Include IP count in the label
            y=bafs,
            mode='markers',
            marker=dict(
                color=[color_mapping.get(t, 'black') for t in types],
                symbol=[SYMBOLS[get_index_of_type[t] % len(SYMBOLS)] for t in types],
                size=24
            ),
            name=system,
            showlegend=False  # Hide individual systems from the legend
        ))

    # Update layout with legend and axis titles
    fig.update_layout(
        xaxis_title='System/OS (IP Count)',
        yaxis_title='BAF (Bandwidth Amplification Factor)',
        showlegend=True,  # Show legend
        xaxis=dict(
            title=dict(font=dict(size=44)), # Title font size
            tickfont=dict(size=36), # Ticks font size
            title_standoff=40
        ),
        yaxis=dict(
            title=dict(font=dict(size=36)), # Title font size
            tickfont=dict(size=36) # Ticks font size
        ),
        legend=dict(font=dict(size=60), x=0.99, y=0.99, xanchor='right', yanchor='top'),
        width=width,
        height=height
    )

    # Add legend for the colors used
    for query_type, color in color_mapping.items():
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(color=color, symbol=SYMBOLS[get_index_of_type[query_type]], size=24),
            showlegend=True,
            name=query_type
        ))

    # Show the plot
    fig.show()

    # Save the plot as an image
    if not bool_monlist:
        output_filepath = system_filepath[:-12] + f"_no_monlist_maxFromAllQueries_scatterplot.png"
    else:
        output_filepath = system_filepath[:-12] + f"_maxFromAllQueries_scatterplot.png"

    fig.write_image(output_filepath, width=width, height=height)


if __name__ == "__main__":
    #  Step 1: get file paths and read the data from them
    get_restrict_filepath = input("Please provide the path to the input file of the get_restrict BAF file\n"
                                  "It should end in `get_restrict_baf.json\n")
    if not get_restrict_filepath.endswith("get_restrict_baf.json"):
        raise ValueError("Filepath does not end in `get_restrict_baf.json")

    peer_list_filepath = input("Please provide the path to the input file of the peer_list BAF file\n"
                               "It should end in `peer_list_baf.json\n")
    if not peer_list_filepath.endswith("peer_list_baf.json"):
        raise ValueError("Filepath does not end in `peer_list_baf.json`")

    peer_list_sum_filepath = input("Please provide the path to the input file of the peer_list_sum BAF file\n"
                                   "It should end in `peer_list_sum_baf.json\n")
    if not peer_list_sum_filepath.endswith("peer_list_sum_baf.json"):
        raise ValueError("Filepath does not end in `peer_list_sum_baf.json`")

    prompt_bool_monlist = (input("Do you want Monlist queries to be included in the scatterplot?\n"
                                 "Options: YES or NO\n")
                           .lower())
    bool_monlist = True if prompt_bool_monlist == "yes" else False

    if bool_monlist:
        monlist_filepath = input("Please provide the path to the input file of the monlist BAF file\n"
                                 "It should end in `monlist_baf.json\n")
        if not monlist_filepath.endswith("monlist_baf.json"):
            raise ValueError("Filepath does not end in `monlist_filepath.json`")

    system_filepath = input("Please provide the path to the input file of the System (OS) for NTPs file"
                            "\nIt should end in `_system.json\n")
    if not system_filepath.endswith("_system.json"):
        raise ValueError("Filepath does not end in `_system.json`")

    get_restrict_dict = read_array_file(get_restrict_filepath)
    peer_list_dict = read_array_file(peer_list_filepath)
    peer_list_sum_dict = read_array_file(peer_list_sum_filepath)
    if bool_monlist:
        monlist_dict = read_array_file(monlist_filepath)

    # Step 2: Preprocessing step
    ip_to_system_dict_unfiltered = read_dict_file(system_filepath)
    ip_to_system_dict = extract_before_special_chars_from_dict(ip_to_system_dict_unfiltered)
    system_to_list_of_ips_dict = invert_dict(ip_to_system_dict)
    system_to_list_of_ips_dict.pop('/', None) # Remove unknown systems to make the graph cleaner

    # Step 3: for each system/OS, get each IP with its max BAF from the 4 queries
    max_NTP_response_per_system = {} # {system1: [(ip1, BAF_max1), (ip2, BAX_max2), ...], system2: [...]}
    system_ip_counts = {} # To store the number of IPs per system for labeling
    for system, list_of_IPs in system_to_list_of_ips_dict.items():
        bafs_queries = []
        for ip in list_of_IPs:
            bafs = []
            bafs.append((get_restrict_dict.get(ip, -1), "get_restrict", ip))
            bafs.append((peer_list_dict.get(ip, -1), "peer_list", ip))
            bafs.append((peer_list_sum_dict.get(ip, -1), "peer_list_sum", ip))
            if bool_monlist:
                bafs.append((monlist_dict.get(ip, -1), "monlist", ip))

            sorted_bafs = sorted(bafs, key=lambda x: x[0], reverse=True)
            bafs_queries.append(sorted_bafs[0]) # largest by BAF, but also store the Query used

        max_NTP_response_per_system[system] = bafs_queries
        system_ip_counts[system] = len(list_of_IPs)  # Store IP count

    # Step 4: Draw scatterplot
    draw_scatterplot(system_filepath, max_NTP_response_per_system, system_ip_counts)
