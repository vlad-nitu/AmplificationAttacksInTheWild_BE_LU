import json
import logging
import re
import subprocess


# Plan:
# Version dict[version, list[IPs]; IP, version: string, list[IPs] -> IPs that are in this cluster (of this version)
# Count per version: count_per_version -> dict[str, int]
# Sum of bafs per version: sum_bafs -> dict[str, float]
# mean_baf_version = sum_bafs[version] / count[version]

# Visualiser of fpdns (in a separate file so that we can decouple the script from the visualiser) -> histogram w/
# mean BAF value per version -> check `visualiser_barplot_Version_meanBAF_fpdns.py`
#

def get_version(IPs: list[str]) -> dict[str, list[str]]:
    """
    Method to obtain the DNS version run by an IP, by using `fpdns`
    :param IPs: list of IPs
    :return: mapping of IPs to DNS versions, based on `fpdns` output
    """

    version_IPs_dict = {}
    for ip in IPs:

        fpdns_res = subprocess.check_output(['fpdns', '-t', '5', ip], text=True)
        # Consider all outputs that are not legit DNS versions (i.e: TIMEOUT, No match found ,etc.) as `No match found`
        # to cluster them in the same result category
        if ':' in fpdns_res:
            version = fpdns_res.split(':', 1)[1].strip()
            if version == "TIMEOUT":
                version = "No match found"
        else:
            version = "No match found"

        # populate dict
        if version not in version_IPs_dict:
            version_IPs_dict[version] = [ip]
        else:
            version_IPs_dict[version].append(ip)

        logging.warning(f"Finished FPDNSing IP: {ip} and got version: {version}")

    return version_IPs_dict


def get_count_per_version(version_IPs_dict) -> dict[str, int]:
    """
    Method that counts how many IPs have a specific DNS version
    :param version_IPs_dict: (version, IP) dict
    :return: (version, count_IPs) dict
    """

    count_per_version_dict = {}
    for version, IPs in version_IPs_dict.items():
        count_per_version_dict[version] = len(IPs)
    return count_per_version_dict


def get_sum_of_bafs_per_version(version_IPs_dict, bafs_dict) -> dict[str, float] :
    """
    Sum the obtained BAFs for a specific DNS version
    :param version_IPs_dict: (version, listOfIPs) dict
    :param bafs_dict: (ip, BAF) dict
    :return: (ip, sumOfBAFs) dict
    """

    sum_bafs = {}
    for version, IPs in version_IPs_dict.items():
        sum_bafs[version] = 0.0
        for ip in IPs:
            sum_bafs[version] += bafs_dict[ip]
    return sum_bafs


def get_output_dict(sum_bafs, count_per_version_dict, bafs_dict, version_IPs_dict) -> dict[str, tuple[int, float]]:
    """
    :param sum_bafs: (ip, sumOfBAFs) dict
    :param count_per_version_dict: (version, count_IPs) dict
    :param bafs_dict: (ip, BAF) dict
    :param version_IPs_dict: (version, listOfIPs) dict.
    :return: (version, (count_per_version, meanBAF, IPS_BAF_dict)) dict
    """

    output_dict = {}
    for version in count_per_version_dict.keys():
        mean_BAF = sum_bafs[version] / count_per_version_dict[version]
        IPs_BAF_dict = {}
        for IP in version_IPs_dict[version]:
            baf = bafs_dict[IP]
            IPs_BAF_dict[IP] = baf
        output_dict[version] = count_per_version_dict[version], mean_BAF, IPs_BAF_dict
    return output_dict

if __name__ == "__main__":
    input_filepath = input("Please provide the path to the input file\n"
                           "This file should be a JSON file of the following format: [ip1, "
                           "ip2, etc.] and its name should terminate in `_IPs.json`\n")

# i.e: ../data/censys_all_data/dns_8k_IPs.json

try:
    with open(input_filepath) as json_file:
        IPs = json.load(json_file)  # Load IPs; type: list[IPs], IP: string
        baf_filepath = input("Please provide the path to the BAF file\n"
                           "This file should be a JSON file of the following format: [[ip1, BAF1], "
                           "[IP2, BAF2], etc.] and its name should terminate in `_baf.json`\n") # input_filepath[:-5] + "_baf.json"
        domain_ip = re.search(r'domain_ip:([^_]+)', baf_filepath).group(1)
        try:
            with open(baf_filepath) as baf_file:
                bafs = json.load(baf_file)  # Load BAFs; type: list[list[IP, baf]]; IP : string, baf: float
                bafs_dict = {item[0]: item[1] for item in bafs}  # Convert list to dict
        except FileNotFoundError:
            raise ValueError("The BAF file was not found")

except FileNotFoundError:
    raise ValueError("The input file was not found")


def preprocess_IPs(IPs, bafs_dict):
    """
    Remove the IPs that do not have BAF >= 1
    :param IPs: list of IPs that we want ot filter out
    :param bafs_dict: dictionary of IPs that we want to inner join (by running a nested for-loop) w/ IPs
    :return: [str] - preprocessed list of IPs
    """

    IPs_with_baf = []
    for ip in IPs:
        if ip in bafs_dict:
            IPs_with_baf.append(ip)
    return IPs_with_baf


logging.info("preprocess_IPs")
IPs = preprocess_IPs(IPs, bafs_dict)

logging.info("get_version")
version_IPs_dict: dict[str, list[str]] = get_version(IPs)
logging.info("get_count_per_version")
count_per_version_dict: dict[str, int] = get_count_per_version(version_IPs_dict)
logging.info("get_sum_of_bafs_per_version")
sum_bafs: dict[str, float] = get_sum_of_bafs_per_version(version_IPs_dict, bafs_dict)
logging.info("get_output_dict")
output_dict: dict[str, tuple[int, float]] = get_output_dict(sum_bafs, count_per_version_dict, bafs_dict,
                                                            version_IPs_dict)

logging.info(output_dict)
logging.info(domain_ip)
outfile_path = input_filepath[:-5] + f"_{domain_ip}_fpdns.json"
try: # Outfile format: JSON object; key: IP, value: (count, mean_BAF)
    with open(outfile_path, 'w', encoding='utf-8') as file:
        json.dump(output_dict, file, ensure_ascii=False, indent=2)
except FileNotFoundError:
    raise FileNotFoundError(f"Could not write to output file: {outfile_path}")
