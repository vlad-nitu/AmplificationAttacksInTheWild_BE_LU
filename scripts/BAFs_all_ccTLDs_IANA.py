import json

from measure_baf import send_dns_request

if __name__ == "__main__":
    input_filepath = input("Please provide the path to the input file\n"
                           "This file should be a JSON file of the following format: [{'TLD': ccTLD1}, "
                           "{'TLD': ccTLD2}, etc.] and its name should terminate in `TLDs.json`\n")

    if not input_filepath.endswith("TLDs.json"):
       raise ValueError("Please provide the path to the input file that ends in `TLDs.json`\n")

    vulnerable_DNS_resolver = "8.8.8.8" # Google's open resolver.

    with open(input_filepath, "r") as file:
        ccTLDs = json.load(file) # List [] of singleton dictionaries: {'TLD': ccTLD_i}
        print(ccTLDs)
        for kv in ccTLDs:
            ccTLD = kv['TLD']
            rq, rsp = send_dns_request(vulnerable_DNS_resolver, ccTLD, "ANY")
            if rsp >= rq and rq > 0:
                kv['BAF'] = rsp / rq


    output_filepath = input_filepath[:-5] + "_BAFs.json"
    json.dump(ccTLDs, open(output_filepath, "w"), indent=2)