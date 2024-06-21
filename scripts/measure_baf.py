import subprocess, argparse, logging

import numpy as np
from scapy.layers.dns import DNS, DNSQR, DNSRROPT
from scapy.layers.inet import UDP, IP
from scapy.packet import Raw
from scapy.sendrecv import send, sniff
from scapy.utils import rdpcap
from scapy.volatile import RandShort

from pymemcache.client.base import Client

from search_amplifiers import write_ips_to_json, parse_json_list_of_ips, \
    valid_ntp_response, valid_dns_response, \
    valid_memcached_response, craft_ntp_packet, \
    get_query_type_code, available_query_types, available_ntp_requests

from matplotlib import pyplot as plt
input_dict = {}


def send_ntp_query(ip: str, ntp_query_type: str) -> tuple[int, int]:
    """
    Send an NTP query to the given IP.
    :param ip: the IP to send the query to
    :param ntp_query_type: the type of NTP query (basic, version or monlist)
    :return: a tuple (length of request, length of response) to be used later in BAF computation
    """
    try:
        if ntp_query_type == "version":
            req_code = '\x04'  # 4  rkt = craft_ntp_version_packet(ip)
        elif ntp_query_type == "monlist":
            req_code = '\x2a'  # 42 pkt = craft_ntp_monlist_packet(ip)
        elif ntp_query_type == "peer_list":
            req_code = '\x00'  # 0 pkt = craft_ntp_peer_list_packet(ip)
        elif ntp_query_type == "peer_list_sum":
            req_code = '\x01'  # 1 pkt = craft_ntp_peer_list_sum_packet(ip)
        elif ntp_query_type == "get_restrict":
            req_code = '\x10'  # 16 pkt = craft_ntp_get_restrict_packet(ip)
        else:  # basic
            raise ValueError("`basic` NTP query should only be used to find amplifiers, not to estimate the BAF")

        pkt = craft_ntp_packet(ip, req_code)

        send(pkt)  # Send the request
        req_size = len(pkt[UDP].payload)
        resp_size = 0
        responses = sniff(lfilter=lambda x: valid_ntp_response(x, ip),
                          timeout=3)  # Sniff for 3 seconds

        for resp in responses:  # Sum up all the payloads from all the response packets
            resp_size += len(resp[UDP].payload)
            if resp.haslayer("Padding"):
                resp_size -= len(resp["Padding"])

        if responses:
            if req_size and resp_size and resp_size >= req_size:
                logging.info(f"Valid {ntp_query_type} NTP response w/ resp_size: {resp_size}")
                logging.info(f"IP: {ip}")
                return req_size, resp_size
            else:
                if resp_size:
                    logging.info("BAF < 1, not an amplifier")
                else:
                    logging.info("No NTP response received.")
                return 0, 0
        else:
            logging.info("Received an invalid NTP response or no response at all.")
            logging.info(f"IP: {ip}")
            return 0, 0
    except Exception as e:
        logging.error(f"Error during NTP check: {e}")
        return 0, 0


def send_dns_query_with_edns(domain="google.com", dns_server='8.8.8.8', query_type_code=255) -> tuple[int, int]:
    """
    Send ANY Query in DNS
    :param query_type_code: type of query in INTeger format (code); "ANY" -> 255, "A" -> 0, "NS" -> 2
    :param domain: domain name that you want to resolve, `google.com` by default
    :param dns_server: DNS Resolver's IP address that you want to use, `8.8.8.8` Google's Open DNS resolver by default
    :return: (req_size, resp_size) to be passed later to `compute_baf` method
    """

    # Craft the IP layer
    ip_layer = IP(dst=dns_server)

    # Craft the UDP layer
    udp_layer = UDP(sport=RandShort(), dport=53)  # DNS queries use port 53

    # Craft the DNS query layer
    dns_query_layer = DNS(ad=1, qd=DNSQR(qname=domain, qtype=query_type_code), ar=DNSRROPT(z=0x8000, rclass=4096))

    # Stack the layers
    query = ip_layer / udp_layer / dns_query_layer

    send(query)  # Send the request
    req_size = len(query[UDP].payload)
    resp_size = 0
    responses = sniff(lfilter=lambda x: valid_dns_response(x, dns_server, query_type_code),
                      timeout=3)  # Snif for 3 seconds

    UDP_header_size = 8  # Bytes
    for resp in responses:  # Sum up all the payloads from all the response packtes
        resp_size += resp[UDP].len - UDP_header_size

    # Show the response
    if req_size and resp_size and req_size <= resp_size:
        return req_size, resp_size
    else:
        if req_size == 0:
            logging.info("No request sent.")
        elif resp_size == 0:
            logging.info("No response received.")
        else:
            logging.info(
                f"BAF < 1, so do not take into account for statistics of amplifiers; req_size: {req_size}, resp_size: {resp_size}")
        return 0, 0


def send_dns_request(dns_resolver: str, ip="google.com", query_type="A") -> tuple[int, int]:
    """
    Send a DNS request to `ip` DNS resolver to resolve domain `domain`
    For more info about DNS Packet structure, check RFC1305 : https://www.ietf.org/rfc/rfc1035.txt
    :param dns_resolver: address of DNS resolver
    :param ip: the domain you want DNS to resolve
    :param query_type: type of DNS record you want to retrieve; by-default is A (IPv4 record)
    :return: (req_size, rsp_size) if successful, or (req_size, 0) otherwise
    """

    try:
        query_type_code = get_query_type_code(query_type)
        return send_dns_query_with_edns(ip, dns_resolver, query_type_code)
        # Add an OPT record to simulate basic EDNS0 functionality
        # Here we use a placeholder for UDP payload size, extended RCODE, and version

    except Exception as e:
        logging.error(f"Error thrown when sr1 in DNS: {e}")
        return 0, 0

def capture_with_tcpdump(interface, ip, output_file):
    command = [
        "sudo", "tcpdump", "-i", interface,
        "-w", output_file,
        f"udp and memcache and src port 11211 and src host {ip}"
    ]
    try:
        subprocess.run(command, timeout=45)  # Adjust timeout to ensure it stops after 3 seconds
    except subprocess.TimeoutExpired:
        logging.warning("Capture timeout expired")


def process_captured_packets(file):
    packets = rdpcap(file)
    resp_size = 0
    num_packtes = 0
    for packet in packets:
        if UDP in packet:
            num_packtes += 1
            resp_size += len(packet[Raw].load)
    return num_packtes, resp_size


def send_memcached_query(ip) -> tuple[int, int]:
    """
    Send a Memcachded query to the given IP.
    :param ip: the IP address to send the query to
    :return: (req_size, resp_size) if successful, or (req_size, 0) else
    """

    input_dict = {'theory_max_baf':  {}}
    memcached_client = Client((ip, 11211), connect_timeout=5, timeout=5)

    try:
        # Step 1: `stats slabs` to get all slabIDs on TCP
        slabs_dict = memcached_client.stats("slabs")

        slab_ids = set()  # Unique Slab IDs
        for slab_key_binary in slabs_dict.keys():
            slab_key = slab_key_binary.decode("utf-8")
            if ':' not in slab_key:
                break
            col_index = slab_key.find(':')
            slab_id = int(slab_key[:col_index])
            slab_ids.add(slab_id)

        # Step 2: For each slabID `stats cachedump <slab_id> 0`, 0 = unlimited -> get all keys for a slabID on TCP

        theory_resp_size = 0  # MAX Possible Response size for Memcached

        keys = set()  # Unique Keys on memcache_server
        for slab_id in slab_ids:
            keys_dict = memcached_client.stats('cachedump', str(slab_id), '0')
            for key_binary, val_binary in keys_dict.items():
                key = key_binary.decode("utf-8")
                # Find the position of 'b' and extract the number before it
                val = val_binary.decode("utf-8")
                b_position = val.find('b')
                num_bytes_str = val[1:b_position].strip()  # Trims any whitespace
                num_bytes = int(num_bytes_str)
                if 999600 <= num_bytes <= 1024 * 1024:  # floor(1000000 / 140) * 1400 bytes = 999600 <= x <= 1Mb
                    theory_resp_size += num_bytes
                    keys.add(key)
                    # print(key)

        # Step 3: gets <k1> <k2> ... <kn> on UDP
        attack_payload = "\x00\x01\x00\x00\x00\x01\x00\x00get"
        for key in keys:
            attack_payload += f" {key}"
        attack_payload += "\r\n"

        query = IP(dst=ip) / UDP(sport=RandShort(), dport=11211) / Raw(load=attack_payload)
        send(query)

        practice_req_size, practice_resp_size = len(query[Raw].load), 0
        theory_req_size = len(query[Raw].load)

        responses = sniff(lfilter=lambda x: valid_memcached_response(x, ip),
                          timeout=3)  # Snif for 5 seconds

        num_responses = len(responses)
        for resp in responses:  # Sum up all the payloads from all the response packtes
            practice_resp_size += len(resp[Raw].load)

        if num_responses and practice_req_size and practice_resp_size >= practice_req_size:  # Memcached server responded to query
            logging.info(f"THEORY: {theory_req_size}, {theory_resp_size}")
            input_dict['theory_max_baf'][ip] = compute_baf((theory_req_size,
                                                            theory_resp_size))  # Theoretical max. BAF we can get if there are no UDP packet loss/dropped on the way
            logging.info(f"PRACTICE: {practice_req_size}, {practice_resp_size}")
            return practice_req_size, practice_resp_size
        else:
            logging.info("No request OR no response OR BAF < 1 in Memcached")
            return 0, 0
    except Exception as e:
        logging.error(f"The Memcached Client timed out in send_memcached_query for ip: {ip}; Error: {e}")
        return 0, 0


def compute_baf(req_resp_sizes: tuple[int, int]) -> float:
    """
    Compute bandwidth amplification factor (BAF) metric, as introduced by Rossow in Amplification Hell paper
    :param req_resp_sizes:  (request's (attacker to amplifier)  payload size, response's
    (amplifier to victim) payload size)
    :return: BAF : float repr. Bandwidth Amplification Factor metric score.
    """

    request_size = req_resp_sizes[0]
    response_size = req_resp_sizes[1]

    if request_size == 0:
        return 0
    else:
        return 1.0 * response_size / request_size


baf_memcached_server = []
baf_dns_resolver = []
baf_ntp_server = []
protocols = set()
protocol_to_list_map = dict()


def compute_baf_of_amplifiers(checked_protocols: set[str], ip_list, type_of_input: str, input_dict: dict[str, str]):
    """
       Main method that calculates the BAF (bandwidth amplification factor) on the list of IPs from our NW
       (ip, baf) for each amplifier is persisteed in its relevant array (i.e.: baf_dns_resolver for DNS)

       :param checked_protocols: set of strings that contains: `dns`, `ntp` and/or `memcached` depending on the input of
       the user
       :param ip_list: List of IPs that we compute the BAF for (if type_of_input = 'json'), else ["dns_resolver_domain", "ip_authoritative"]
       :param type_of_input: `json` or `csv`
       :param input_dict: input dictionary which holds parameters of the queries, depending on the protocol we analyse
       :return: None
       """
    for ip in ip_list:
        for protocol in checked_protocols:
            if protocol == 'dns':
                if type_of_input == 'json':
                    domain_ip = input_dict['domain_ip']
                    query_type = input_dict['dns_query_type']
                    req_size, resp_size = send_dns_request(ip, domain_ip, query_type)
                    if req_size == 0 and resp_size == 0:
                        continue  # Skip, don't aggregate to statistics
                    else:
                        baf_dns_resolver.append((ip, compute_baf((req_size, resp_size))))
                else:
                    query_type = input_dict['dns_query_type']
                    req_size, resp_size = send_dns_request(ip[2], ip[0], query_type)
                    if req_size == 0 and resp_size == 0:
                        continue  # Skip, don't aggregate to statistics
                    else:
                        baf_dns_resolver.append(((ip[1], ip[0]), compute_baf((req_size, resp_size))))
            if protocol == 'memcached':
                req_size, resp_size = send_memcached_query(ip)
                if req_size == 0 and resp_size == 0:
                    continue  # Skip, don't aggregate to statistics
                else:
                    baf_memcached_server.append((ip, compute_baf((req_size, resp_size))))
            if protocol == 'ntp':
                ntp_query_type = input_dict['ntp_query_type']
                req_size, resp_size = send_ntp_query(ip, ntp_query_type=ntp_query_type)
                if req_size == 0 and resp_size == 0:
                    continue  # Skip, don't aggregate to statistics
                else:
                    baf_ntp_server.append((ip, compute_baf((req_size, resp_size))))


def plot_histogram_baf(checked_protocols: set[str], file_path: str, input_dict: dict[str, str], max_dns_dict):
    """
    Method that plots a hisotgram for the BAF (bandwidth amplification factor) on the list of IPs for the protocols
    that are found in `checked_protocols` set
    :param checked_protocols: Set of protoocls that we want to plot the histogram for
    :param file_path = absolute input file path
    :param input_dict: input dictionary which holds parameters of the queries, depending on the protocol we analyse
    :param max_dns_dict: DNS_IP -> max DNS buffer size kv pairs
    :return: None
    """
    logging.info("Start plotting histogram")
    for protocol in checked_protocols:
        if protocol == 'dns':  # TODO: Strategy later w/ domain & query type
            plot_hist_helper(protocol, 'b', file_path, input_dict, max_dns_dict)
        if protocol == 'memcached':
            plot_hist_helper(protocol, 'g', file_path, input_dict, max_dns_dict)
        if protocol == 'ntp':
            plot_hist_helper(protocol, 'r', file_path, input_dict, max_dns_dict)


def replace_json_with_png(infile_path: str) -> str:
    """
    Helper method that replaces `.json` extension from a file path with `.png` extension
    :param infile_path: absolute input file path
    :return: outfile_path: infile_path w/ .json termination replaced by .png
    """
    # Check if the file path ends with '.json'
    if infile_path.endswith('.json'):
        # Replace '.json' with '.png'
        outfile_path = infile_path[:-5] + '.png'
        return outfile_path
    else:
        raise ValueError("The input file path does not end with '.json'")


def plot_hist_helper(protocol: str, color: str, file_path: str, input_dict: dict[str, str], max_dns_dict) -> None:
    """
    Helper method to plot histogram
    :param protocol: that we plot histogram for
    :param color: color chosen for the histogram
    :param file_path: absolute input file path
    :param input_dict: input dictionary which holds parameters of the queries, depending on the protocol we analyse
    :param max_dns_dict: DNS_IP -> max_dns_buffer_size kv pairs
    :return: None
    """

    plt.figure(figsize=(10, 6))  # 1000 x 600 inches; TODO: Adjust as needed per diagram

    if 'max_udp_size' in input_dict and input_dict['max_udp_size']:  # DNS w/ max_udp stats
        data = protocol_to_list_map[protocol]
        baf_scores_blue = [x[1] for x in data if x[0] in max_dns_dict and max_dns_dict[x[0]] != 1232]
        baf_scores_yellow = [x[1] for x in data if x[0] in max_dns_dict and max_dns_dict[x[0]] == 1232]

        # Plotting the histograms
        plt.hist(baf_scores_blue, bins=30, color='blue', label='Max UDP Buffer Size != 1232'.format(protocol))
        plt.hist(baf_scores_yellow, bins=30, color='orange',
                 label='Max UDP Buffer Size = 1232'.format(protocol))

    elif 'theory_max_baf' in input_dict:  # Memcached
        practical_baf_scores = [x[1] for x in protocol_to_list_map[protocol]]
        theory_baf_scores = [x for x in input_dict['theory_max_baf'].values()]

        plt.hist(practical_baf_scores, bins=30, alpha=0.5, color="green",
                 label='Practical BAFs for memcached')
        plt.hist(theory_baf_scores, bins=30, alpha=0.5, color="red",
                 label='Theoretical maximum BAFs for memcached')

    else:
        baf_scores = [x[1] for x in protocol_to_list_map[protocol]]
        plt.hist(baf_scores, bins=30, color=color, label=f'BAF for {protocol}')

    plt.xlabel('(BAF) Bandwidth Amplification Factor')
    plt.ylabel('# of IPs')

    title_str = f'Histogram of BAF for {protocol}\n'
    no_include_in_hist_title = {'max_udp_filepath'} # List of parameters that should not be added to the name of the file
    for label, value in input_dict.items():
        if label in no_include_in_hist_title: 
            continue
        if label == 'theory_max_baf':
            title_str += f'{label}: True\n'
        else:
            title_str += f'{label}: {value}\n'
    plt.title(title_str)

    # Adjust the figure size to fit all content
    plt.tight_layout()
    plt.legend()
    if 'domain_ip' in input_dict and 'dns_query_type' in input_dict: # DNS
        outfile_path_json = file_path[:-5] + f"_{input_dict['domain_ip']}_{input_dict['dns_query_type']}_hist.json"
    else:
        outfile_path_json = file_path[:-5] + "_hist.json"
    outfile_path = replace_json_with_png(infile_path=outfile_path_json)
    plt.savefig(outfile_path)
    plt.close()


def compute_statistics(checked_protocols: set[str]) -> None:
    """
    Method that computes basic statistics (mean, median and variance)
    :param checked_protocols: Set of protocols that we want to plot the histogram for
    :return: None
    """

    for protocol in checked_protocols:
        baf_scores = [x[1] for x in protocol_to_list_map[protocol]]
        print(f"BAF Statistics for {protocol}:")
        if len(baf_scores) == 0:  # empty
            logging.warning("No servers obtained BAF > 1")
            return
        print(f"There are {len(baf_scores)} IPs that produced BAF > 1")
        if baf_scores:
            print(f"Min BAF: {np.min(baf_scores)}")
            print(f"Max BAF: {np.max(baf_scores)}")
        print(f"Mean: {np.mean(baf_scores)}")
        print(f"Median: {np.median(baf_scores)}")
        print(f"Variance: {np.var(baf_scores)}")

    logging.info("Finished computing statistics")

def main():
    parser = argparse.ArgumentParser(description="Compute BAF (Bandwidth Amplification Factor) for various protocols; Should be used after the filtering step done in `search_amplifiers.py`")

    parser.add_argument("file_path", help="Absolute input file path; Contains a list of IPs to actively probe to compute the BAF they obtain; The file format should be a JSON file containing a JSON Array, each element of the array being an IP string.")
    parser.add_argument('-p', "--protocols", nargs='+', choices=["dns", "ntp", "memcached"], required=True, 
                        help="Protocols to check for amplifiers: dns, ntp, memcached")
    parser.add_argument("--domain_ip", default="google.com", help="Domain to resolve for DNS protocol (default: google.com)")
    parser.add_argument("--dns_query_type", choices=available_query_types, default="A", 
                        help="Type of DNS query to send: A, ANY, NS, AXFR, DNSKEY, TXT (default: A)")
    parser.add_argument("--ntp_query_type", choices=available_ntp_requests, default='version', 
                        help="Type of NTP query to send: version, monlist, peer_list, peer_list_sum, get_restrict (default: version)")
    parser.add_argument("--max_udp_size", action='store_true', 
                        help="Flag to indicate if max UDP size statistics are required")
    parser.add_argument("--max_udp_filepath", 
                        help="File path to the EDNS Buffer Size file statistics, ending in '_max_udp.json'")
    parser.add_argument("-v", "--verbose", action='store_true', help="Increase output verbosity")

    args = parser.parse_args()

    protocol_to_list_map['dns'] =  baf_dns_resolver
    protocol_to_list_map['ntp'] =  baf_ntp_server
    protocol_to_list_map['memcached'] =  baf_memcached_server

    if not args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    input_dict = {}
    if 'dns' in args.protocols:
        input_dict['domain_ip'] = args.domain_ip
        input_dict['dns_query_type'] = args.dns_query_type
        if args.max_udp_size:
            input_dict['max_udp_size'] = True
            if not args.max_udp_filepath:
                raise ValueError("If --max_udp_size is specified, --max_udp_filepath must also be provided.")
            input_dict['max_udp_filepath'] = args.max_udp_filepath
        else:
            input_dict['max_udp_size'] = False

    if 'ntp' in args.protocols:
        input_dict['ntp_query_type'] = args.ntp_query_type

    if 'memcached' in args.protocols:
        input_dict['theory_max_baf'] = {}

    ip_list, max_dns_dict = parse_json_list_of_ips(args.file_path, input_dict)

    compute_baf_of_amplifiers(args.protocols, ip_list, 'json', input_dict)
    compute_statistics(args.protocols)
    plot_histogram_baf(args.protocols, args.file_path, input_dict, max_dns_dict)
    write_ips_to_json(args.protocols, protocol_to_list_map, args.file_path, input_dict, True)

if __name__ == "__main__":
    main()
