import json
import os
import shodan

SHODAN_UIUC_API_KEY = os.environ.get('SHODAN_UIUC_API_KEY')
SHODAN_TUD_API_KEY = os.environ.get('SHODAN_TUD_API_KEY')


class NTP:
    def __init__(self, asn, os, isp, transport, accepts_monlist, stratum, hostnames, domains, org, data, ip_str,
                 location):
        """
        Ctor that stores only the attributes we are interested in
        :param asn:
        :param os:
        :param isp:
        :param transport:
        :param accepts_monlist:
        :param stratum:
        :param hostnames:
        :param domains:
        :param org:
        :param data:
        :param ip_str:
        :param location:
        """

        self.asn = asn
        self.os = os
        self.isp = isp
        self.transport = transport
        self.accepts_monlist = accepts_monlist
        self.stratum = stratum
        self.hostnames = hostnames
        self.domains = domains
        self.org = org
        self.data = data
        self.ip_str = ip_str
        self.location = location

    def to_dict(self):
        """
        Converts an object instances into a dict
        :return: dict storing: asn, os, etc.
        """
        return {
            "asn": self.asn,
            "os": self.os,
            "isp": self.isp,
            "transport": self.transport,
            "accepts_monlist": self.accepts_monlist,
            "stratum": self.stratum,
            "hostnames": self.hostnames,
            "domains": self.domains,
            "org": self.org,
            "data": self.data,
            "ip_str": self.ip_str,
            "location": self.location
        }

    def __str__(self):
        """
        ToString method for debugging purposes
        :return: a String representation of the object
        """
        return (f"NTP Server:\n"
                f"ASN: {self.asn}\n"
                f"OS: {self.os}\n"
                f"ISP: {self.isp}\n"
                f"Transport: {self.transport}\n"
                f"Accepts Monlist: {self.accepts_monlist}\n"
                f"Stratum: {self.stratum}\n"
                f"Hostnames: {self.hostnames}\n"
                f"Domains: {self.domains}\n"
                f"Org: {self.org}\n"
                f"Data: {self.data}\n"
                f"IP Address: {self.ip_str}\n"
                f"Location: {self.location}")


def write_ntp_list_to_json(ntp_list, file_path):
    """
    Writes a list of NTP object instances to a JSON List, after converting it to dict using `to_dict()`
    :param ntp_list: List of Memcached object instances
    :param file_path: path to file
    :return: JSON List depicting NTP object instances in a List format
    """

    with open(file_path, 'w') as file:
        json_list = [ntp.to_dict() for ntp in ntp_list]
        json.dump(json_list, file, indent=4)


def write_ntp_to_json(total_searches, file_path) -> None:
    """
    Writes total searches to JSON file
    :param total_searches: total searches
    :param file_path: file path
    :return: None
    """
    with open(file_path, 'w') as file:
        # Write the integer directly to the file
        json.dump(total_searches, file, indent=4)


ntp_arr = []
if __name__ == "__main__":
    try:
        SHODAN_API_KEY = SHODAN_UIUC_API_KEY  # TUD : SHODAN_TUD_API_KEY
        api = shodan.Shodan(SHODAN_API_KEY)
        # Search Shodan
        results = api.search('country:"LU" port:123')

        total_searches = results['total']

        for res in results['matches']:
            ntp = NTP(res['asn'], res['os'], res['isp'], res['transport'], res['ntp']['monlist'], res['ntp']['stratum'],
                      res['hostnames'], res['domains'], res['org'], res['data'], res['ip_str'], res['location'])
            ntp_arr.append(ntp)

        write_ntp_list_to_json(ntp_arr, '../data/shodan/Luxembourg/LuxembourgNTPPort123.json')
        write_ntp_to_json(total_searches, '../data/shodan/Luxembourg/LuxembourgNTPTotalEntries.json')

    except shodan.APIError as e:
        print('Error: {}'.format(e))
