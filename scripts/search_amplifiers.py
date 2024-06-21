import csv
import json
import os
import argparse
import logging

from scapy.all import RandShort
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP
from scapy.layers.ntp import NTPHeader
from scapy.packet import Raw
from scapy.sendrecv import sr1, send, sniff

available_query_types = ["A", "ANY", "NS", "AXFR", "DNSKEY", "TXT"]
available_ntp_requests = ['version', 'monlist', 'peer_list', 'peer_list_sum', 'get_restrict', 'basic']

open_memcached_server = []
open_dns_resolver = []
open_ntp_server = []
protocols = set()

dns_params = {'domain_ip', 'dns_query_type'}
ntp_params = {'ntp_query_type'}

protocol_to_list_map = dict()
global ntp_query_type

def get_query_type_code(query_type_str):
        """
            Helper method that converts human readable DNS query type, to machine-readable query type code
            :param query_type_str: query type in string, human-readable format (i.e.: ANY) 
            :return: the code associated with the query type (i.e.: 255 for ANY)
        """
        if query_type_str == "ANY":
            query_type_code = 255
        elif query_type_str == "NS":
            query_type_code = 2
        elif query_type_str== "AXFR":
            query_type_code = 252
        elif query_type_str== "DNSKEY":
            query_type_code = 48
        elif query_type_str== "TXT":
            query_type_code = 16
        elif query_type_str== "A":  # "A"
            query_type_code = 1
        else:
            raise ValueError("Query type INVALID")
        
        return query_type_code

def craft_ntp_packet(target_ip, req_code):
    """
    Craft NTP packet of Mode 7 with request_code `req_code`,
    :param target_ip: IP that you want to probe
    :param req_code: char: req_code in a hexa char; i.e.: '\x2a' = 42_10 for MONLIST
    :return: NTP Packet
    """
     # NTP uses UDP port 123 by default
    dst_port = 123
    # Craft the base NTP packet with Private mode (7)
    # Mode 7 is used for private (implementation-specific) operations
    data = "\x1F\x00\x03" + req_code + "\x00" * 4  # Version 3
    monlist_packet = IP(dst=target_ip) / UDP(sport=RandShort(), dport=dst_port) / Raw(load=data)
    # Req_Code 42 (0x2a) corresponds to MON_GETLIST (monlist request)
    return monlist_packet

def check_dns(ip, domain_ip="google.com", query_type_code=1):
    """
    Check if `ip` server is an open DNS resolver
    For more info about DNS Packet structure, check RFC1305 : https://www.ietf.org/rfc/rfc1035.txt
    :param domain_ip: what domain the DNS resolver should resolve
    :param ip: address of server
    :param query_type_code: type of DNS record you want to retrieve; by-default is 1 ("A" : IPv4 record): https://en.wikipedia.org/wiki/List_of_DNS_record_types
    :return: True if IP it is open & responsive, False otherwise.
    """

    try:
        pkt = IP(dst=ip) / UDP(sport=RandShort(), dport=53) / DNS(rd=1,
                                                                  qd=DNSQR(qname=domain_ip, qtype=query_type_code))
        send(pkt)
        responses = sniff(lfilter=lambda x: valid_dns_response(x, ip, query_type_code),
                          timeout=3)  # Snif for 3 seconds

        if responses:  # If there are >= 1 packets sniffed using `lfilter : valid_dns_response`
            logging.info("Received a valid DNS response.")
            return True
        else:
            logging.info("Received an invalid DNS response.")
            return False
    except Exception:
        logging.error("Error thrown when sending req. or sniffing response in check_dns")
        return False


def check_ntp_basic(ip):
    """
        Check if `ip` server is running NTP on port 123
        For more info about NTP Packet structure, check RFC5905 : https://datatracker.ietf.org/doc/rfc5905/
        :param ip: address of server
        :return: True if IP it is open & responsive, False otherwise.
        """
    try:
        pkt = IP(dst=ip) / UDP(sport=RandShort(), dport=123) / NTPHeader(
            mode=3)  # Craft an NTP query packet with mode 3 (client)
        # Send the packet and wait for a response
        send(pkt)
        ans = sr1(pkt, timeout=3, verbose=0)

        # Check if the response is a valid NTP response with mode 4 (server)
        if ans and ans.haslayer(NTPHeader) and ans[NTPHeader].mode == 4:
            # Check if the server is synchronized (stratum should be different from 16)
            if ans[NTPHeader].stratum != 16:
                logging.info("Received a valid and synchronized NTP response.")
                return True
            else:
                logging.info(
                    f"Received a valid NTP response but the server is not synchronized; stratum: {ans[NTPHeader].stratum}")
        else:
            logging.info("Received an invalid NTP response or no response at all.")

    except Exception as e:
        logging.error(f"Error during NTP check: {e}")

    return False

def valid_dns_response(packet, ip, query_type_code=1):
    """
    Callback function that is used when sniffing for an DNS packet answer and checks if it is valid
    :param packet: Response packet under test
    :param ip: dst ip addr in request <=> src ip addr in response
    :param query_type_code: Code of query type, by-default: 1 = "A" record: https://en.wikipedia.org/wiki/List_of_DNS_record_types
    :return: True, if packet is valid, else False
    """

    # Should have a DNS layer, be of type `response` (qr = 1)
    # and should have `rcode` (response_code) 0 (NOERROR) or 3 (NXDOMAIN)
    valid_dns = (IP in packet and packet[IP].src == ip and UDP in packet and packet[UDP].sport == 53 and DNS in packet
                 and packet[DNS].qr == 1 and packet[DNS].rcode in {0, 3})

    if query_type_code != 255:  # Any query type that is not ANY
        return valid_dns
    else:
        # For ANY some of the responses are "malformed" in the sense that they are correct, but do not have DNS layer, instead have
        # All the data in "Raw" layer
        # https://dnspython.readthedocs.io/en/latest/message - rcode.html
        # qr == 1 => RESPONSE
        # rcode == 0 = NOERROR; rcode == 3 = NXDOMAIN
        return valid_dns or (IP in packet and packet[IP].src == ip and UDP in packet and packet[UDP].sport == 53
                             and Raw in packet and len(packet[Raw].load))


def valid_ntp_response(packet, ip):
    """
    Callback function that is used when sniffing for an NTP packet answer and checks if it is valid
    :param packet: Response packet under test
    :param ip: dst ip addr in request <=> src ip addr in response
    :return: True, if packet is valid, else False
    """

    return IP in packet and packet[IP].src == ip and UDP in packet and packet[UDP].sport == 123


def valid_memcached_response(packet, ip):
    """
    Callback function that is used when sniffing for an Memcached packet answer and checks if it is valid
    :param packet: Response packet under test
    :param ip: dst ip addr in request <=> src ip addr in response
    :return: True, if packet is valid, else False
    """

    return IP in packet and packet[IP].src == ip and UDP in packet and packet[
        UDP].sport == 11211  # and Raw in packet and 'dest-unreach' not in str(packet)


def check_ntp_query(ip: str, ntp_query_type: str):
    """
        Check if `ip` server is running NTP on port 123 & accepts the query of type Version or Monlist
        For more info about NTP Packet structure, check RFC5905 : https://datatracker.ietf.org/doc/rfc5905/
        :param ip: address of server
        :param ntp_query_type: the type of NTP query you want to retrieve
        :return: True if IP it is open & responsive & accepts the Version or Monlist command (dep. on ntp_query_type param), False otherwise.
        """
    try:

        if ntp_query_type == "version":
            req_code = '\x04' # Version Packet: SYS_INFO(4) Rcode
        elif ntp_query_type == "monlist":  # Monlist
            # Monlist Packet -> Check Mode 7 packet format: https://datatracker.ietf.org/doc/rfc9327/ Check iPad (NTP
            # file) for more info OR wireshark: `(udp.port == 123 and ip.dst == <ip>) || (ip.src == <ip> )` ; 0x2a =
            # 42_base10 = Req Code for MONLIST_GET_1 (42)
            req_code = '\x2a'
            # Version Packet -> SYS_INFO(4)
        elif ntp_query_type == "peer_list":
            req_code = '\x00' # PEER_LIST(0)
        elif ntp_query_type == "peer_list_sum":
            req_code = '\x01'  # PEER_LIST_SUM(1)
        elif ntp_query_type == "get_restrict":
            req_code = '\x10'  # GET_RESTRICT(16)
        else:  # Basic
            return check_ntp_basic(ip)

        pkt = craft_ntp_packet(ip, req_code)

        # Send the packet and wait for a response
        send(pkt)
        resp_size = 0
        responses = sniff(lfilter=lambda x: valid_ntp_response(x, ip),
                          timeout=3)

        for resp in responses:
            resp_size += len(resp[UDP].payload)
            if resp.haslayer("Padding"):
                resp_size -= len(resp["Padding"]) # Remove the padding from the BAF calculation

        if responses:
            # Check if the server is synchronized (stratum should be different from 16)
            logging.info(f"There are: {len(responses)} Monlist NTP packets received, which have in total {resp_size} bytes")
            return True
        else:
            logging.info("Received an invalid NTP response or no response at all.")
            return False
    except Exception as e:
        logging.error(f"Error during NTP check: {e}")
        return False


def check_memcached(ip) -> tuple[int, int]:
    """
    Send a Memcachded query to the given IP, and checks if it answers on UDP.
    :param ip: the IP address to send the query to
    :return: True if successful, or False otherwise
    """
    # Step 1: `stats slabs` on UDP
    attack_payload = "\x00\x01\x00\x00\x00\x01\x00\x00stats slabs\r\n"
    query = IP(dst=ip) / UDP(sport=RandShort(), dport=11211) / Raw(load=attack_payload)
    send(query)

    practice_req_size, practice_resp_size = len(query[Raw].load), 0

    responses = sniff(lfilter=lambda x: valid_memcached_response(x, ip),
                      timeout=3)  # Snif for 3 seconds

    num_responses = len(responses)
    for resp in responses:  # Sum up all the payloads from all the response packtes
        practice_resp_size += len(resp[Raw].load)

    if num_responses and practice_req_size and practice_resp_size:  # Memcached server responded to query
        logging.info(f"Memcached Server {ip} is open on UDP/11211")
        return True
    else:
        logging.info("No request OR no response")
        return False

def parse_json_list_of_ips(file_path: str, input_dict):
    """
    Parse an array of strings (IPs) that are stored in JSON format to a Python array of string
    :param file_path: the file path to the JSON file
    :param input_dict: param input dict
    :return: (list of IPs (in `str` format), max_dns_dict which holds: DNS_IP -> max_dns_buffer_size kv pairs)
    """

    if not file_path.endswith(".json"):
        raise ValueError("The provided file is not a JSON file, as it's file path does not end in `.json`")

    # File example: data/censys/dns_servers_wild.json
    # File format: JSON array of IP strings
    try:
        with open(file_path, 'r') as file:
            ip_list = json.load(file)  # Using json.load to read and parse in one step
            # ip_list = [entry['ip'] for entry in ip_list] # TODO: Change depending on JSON input format
            if 'max_udp_size' in input_dict and input_dict['max_udp_size']:
                max_udp_file_path  = input_dict['max_udp_filepath']
                try:
                    with open(max_udp_file_path, 'r') as max_udp_file:
                        max_dns_dict_array_singleton = json.load(max_udp_file)  # Singleton of dict
                        max_dns_dict = {}
                        for kv_pair in max_dns_dict_array_singleton:
                            max_dns_dict.update(kv_pair)
                        return ip_list, max_dns_dict
                except FileNotFoundError:
                    raise ValueError("The max_udp_file was not found. Please check the file path.")
            return ip_list, {}
    except FileNotFoundError:
        raise ValueError("The file was not found. Please check the file path.")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")


def parse_csv_list_of_ips(file_path: str) -> list[tuple[str, str]]:
    """
    Parse multiples lines of the format "domain","ip_authoritative" that are stored in csv format to a Python array of string
    :param file_path: the file path to the JSON file
    :return: [domain, ip_authoritative] list of tuple[str, str]
    """

    # File example: data/pagerank/resolved_IPs_auth_servers.txt
    # File format: <domain_to_resolve>,<ip_for_auth_server_of_domain>
    parsed_data = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:  # Ensure that each row has exactly two elements
                domain, ip_address = row[0].strip(), row[1].strip()
                parsed_data.append((domain, ip_address))
            else:
                logging.warning(f"Skipping invalid row: {row}")
    return parsed_data


def search_amplifiers(file_path: str, checked_protocols: set[str], input_dict: dict[str, str]) -> None:
    """
    Main method that searches for potential amplifiers in the list of IPs from our AS (Autonomous Serve)
    :param file_path:
    :param checked_protocols: set of strings that contains: `dns`, `ntp` and/or `memcached` depending on the input of
    the user
    :param input_dict: input dictionary which holds parameters of the queries, depending on the protocol we analyse
    :return: None
    """
    ip_list, _ = parse_json_list_of_ips(file_path, input_dict)
    for ip in ip_list:
        for protocol in checked_protocols:
            if protocol == 'dns' and check_dns(ip, input_dict['domain_ip'], get_query_type_code(input_dict['dns_query_type'])):
                open_dns_resolver.append(ip)
            if protocol == 'memcached' and check_memcached(ip):
                open_memcached_server.append(ip)
            if protocol == 'ntp' and check_ntp_query(ip, input_dict['ntp_query_type']):
                open_ntp_server.append(ip)

    logging.info("search_amplifiers finished successfully")



def write_json(ips, outfile_path):
    """
    Writes a list of amplifier's IPs to the output file specified by the `outfile` file_path
    :param ips: Array / List of amplifier's IPs for a specific protocol
    :param outfile_path: Path of file to write the output list; JSON format
    :return: None
    """
    logging.info("Start write_json")
    try:
        with open(outfile_path, 'w', encoding='utf-8') as file:
            json.dump(ips, file, ensure_ascii=False, indent=2)
        logging.info(f"Amplifiers have been successfully written to {outfile_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def write_ips_to_json(protocols: set[str], protocol_to_list_map: dict[str, list], file_path: str, input_dict,
                      is_baf=False) -> None:
    """
    Write the IPs of amplifiers for each of the requested protocols: `dns`, `ntp` and/or `memcached`
    Each list of amplifiers (i.e.: open_dns_resolver) will be written in JSON format to a separate JSON file situated
    under `data` directory
    If the user did not request a protocol, there won't be a file created for that specific protcol
    :param protocols: used to write to their specific JSON file
    :param protocol_to_list_map: Mapping of protocol to the list that holds its results (i.e.: `dns` -> dns_open-resolvers)
    :param file_path: the absolute input file path
    :param input_dict: input_dict that holds parameters
    :param is_baf: True, if `measure_baf.py` (you are interested in the BAF of the IPs), or False otherwise (you are only
    interested in finding amplifiers, w/o measuring the BAF)
    :return: None
    """
    logging.info("Start write_ips_to_json")
    for prot in protocols:
        if is_baf:
            # Split the filename from its extension
            base, extension = os.path.splitext(file_path)
            # Add the desired string before the file extension
            outfile_path = f"{base}"  # _baf{extension}"
            for param_key, param_value in input_dict.items():
                if param_key == 'theory_max_baf':  # Do not include entire dict in file name, but instead just mark the key as True
                    outfile_path += f"_{param_key}:True"
                    continue
                outfile_path += f"_{param_key}:{param_value}"
            outfile_path += f"_baf{extension}"

        else:
            # Split the file path into directory and filename
            directory, filename = os.path.split(file_path)
            # Remove '_before_filtering' from the filename
            new_filename = filename.replace('_before_filtering', '')
            # Combine the directory and the modified filename into a new path
            outfile_path = os.path.join(directory, new_filename)
        write_json(protocol_to_list_map[prot], outfile_path)


def main():
    parser = argparse.ArgumentParser(description="Search for potential open servers in the list of IPs.")
    
    parser.add_argument("file_path", help="Absolute input file path, ending with '_before_filtering.json'; Contains a list of IPs to actively probe whether they are open; The file format should be a JSON file containing a JSON Array, each element of the array being an IP string.")
    parser.add_argument('-p', "--protocols", nargs='+', choices=["dns", "ntp", "memcached"], required=True,
                        help="Protocols to check for servers: dns, ntp, memcached")
    parser.add_argument("--domain_ip", default='google.com', help="Domain to resolve for DNS protocol (default: google.com)")
    parser.add_argument("--dns_query_type", default='A', choices=available_query_types, 
                        help="Type of DNS query to send: A, ANY, NS, AXFR, DNSKEY, TXT (default: A) ")
    parser.add_argument("--ntp_query_type", default='basic', choices=available_ntp_requests, 
                        help="Type of NTP query to send: version, monlist, peer_list, peer_list_sum, get_restrict, basic (default: basic)")
    parser.add_argument("--max_udp_size", action='store_true', 
                        help="Flag to indicate if max UDP size statistics are required")
    parser.add_argument("--max_udp_filepath", 
                        help="File path to the EDNS Buffer Size file statistics, ending in '_max_udp.json'")
    parser.add_argument('-v', "--verbose", action='store_true', help="Increase output verbosity (by triggering DEBUG level logging)")

    args = parser.parse_args()

    if "_before_filtering.json" not in args.file_path:
        raise ValueError("Provided input file path is not valid, because it does not terminate in: '_before_filtering.json'")

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

    protocol_to_list_map = {
        'dns': open_dns_resolver,
        'ntp': open_ntp_server,
        'memcached': open_memcached_server
    }

    if not args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)


    search_amplifiers(args.file_path, set(args.protocols), input_dict)
    write_ips_to_json(set(args.protocols), protocol_to_list_map, args.file_path, input_dict)

if __name__ == "__main__":
    main()
