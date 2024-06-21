import json
import os

import shodan

SHODAN_UIUC_API_KEY = os.environ.get('SHODAN_UIUC_API_KEY')
SHODAN_TUD_API_KEY = os.environ.get('SHODAN_TUD_API_KEY')


class Memcached:
    def __init__(self, asn, os, isp, transport, hostnames, location, org, data, ip_str):
        """
        Ctor that stores only the attributes we are interested in
        :param asn:
        :param os:
        :param isp:
        :param transport:
        :param hostnames:
        :param location:
        :param org:
        :param data:
        :param ip_str:
        """
        self.asn = asn
        self.os = os
        self.isp = isp
        self.transport = transport
        self.hostnames = hostnames
        self.location = location
        self.org = org
        self.data = data
        self.ip_str = ip_str

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
            "hostnames": self.hostnames,
            "location": self.location,
            "org": self.org,
            "data": self.data,
            "ip_str": self.ip_str
        }


def write_memcached_list_to_json(memcached_list, file_path) -> None:
    """
    Writes a list of Memcached object instances to a JSON List, after converting it to dict using `to_dict()`
    :param memcached_list: List of Memcached object instances
    :param file_path: path to file
    :return: JSON List  depicting Memcached object instances in a List format
    """
    with open(file_path, 'w') as file:
        json_list = [memcached.to_dict() for memcached in memcached_list]
        json.dump(json_list, file, indent=4)


def write_total_searches_memcached_to_json(total_searches, file_path) -> None:
    """
    Writes total searches to JSON file
    :param total_searches: total searches
    :param file_path: file path
    :return: None
    """
    with open(file_path, 'w') as file:
        # Write the integer directly to the file
        json.dump(total_searches, file, indent=4)


memcached_arr = []
if __name__ == "__main__":
    # Wrap the request in a try/ except block to catch errors
    try:
        SHODAN_API_KEY = SHODAN_UIUC_API_KEY  # TUD: SHODAN_TUD_API_KEY"
        api = shodan.Shodan(SHODAN_API_KEY)
        # Search Shodan
        results = api.search('country:"LU" port:11211')
        total_searches = results['total']
        for res in results['matches']:
            memcached = Memcached(res['asn'], res['os'], res['isp'], res['transport'], res['hostnames'],
                                  res['location'], res['org'], res['data'], res['ip_str'])
            memcached_arr.append(memcached)

        write_memcached_list_to_json(memcached_arr, '../data/shodan/Luxembourg/LuxembourgMemcachedPort123.json')
        write_total_searches_memcached_to_json(total_searches,
                                               '../data/shodan/Luxembourg/LuxembourgMemcachedTotalEntries.json')
    except shodan.APIError as e:
        print('Error: {}'.format(e))
