## Investigating the Amplification Potential of Common UDP-Based Protocols in DDoS Attacks across Belgium and Luxembourg

### Overview
This repository contains the code and resources developed for my Bachelor's thesis at TU Delft, in the EEMCS (Electrical Engineering, Mathematics and Computer Science) faculty, for the CSE (Computer Science and Engineering) degree.
The project focuses on investigating the amplification potential of three commonly exploited UDP-based protocols: DNS, NTP, and Memcached. 
This study was conducted within the network infrastructure in Belgium and Luxembourg to identify potential vulnerabilities and correlations that influence the weaponization of these protocols in Distributed Reflection Denial-of-Service (DRDoS) attacks.
The responsible professor of this thesis was [Professor Georgios Smaragdakis](https://gsmaragd.github.io/) and the supervisor was [Professor Harm Griffioen](https://www.tudelft.nl/ewi/over-de-faculteit/afdelingen/intelligent-systems/cybersecurity/people/harm-griffioen).

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Example Work Flow](#example-work-flow)
5. [Project Structure](#project-structure)
6. [Contact](#contact)
## Introduction

This project investigates the amplification potential of three commonly exploited UDP-based protocols: DNS, NTP, and Memcached. Distributed Reflection Denial-of-Service (DRDoS) attacks leverage these protocols to amplify traffic and overwhelm targets, posing significant cyber threats.

The study focuses on:

-  We provide a framework on how attackers can find amplifiers in the wild for servers running DNS, NTP and Memcached.

- We audit a sample of the Belgium and Luxembourg network landscape, estimating the amplification factors of vulnerable systems and whether these are susceptible to application-layer level loops.
 
- We reflect on the results and define success factors for amplification attacks. We relate these factors to how attackers behave by following Griffioen et al.'s framework and propose countermeasures to mitigate such vulnerabilities.

- We analyse the correlation between factors that influence amplification attacks.

Our research analyses whether such amplifiers can still be found in the wild, estimate the amplification factors of such servers, and determine which parameters affect the success of cyberattacks. We also compare our observations with those of other networking infrastructures analysed by our peers: Greece, The Netherlands, Sweden and France.  

The research paper related on our work can be found [here](https://www.overleaf.com/read/nrzpjghcbfmc#76541b).

## Installation 

### Prerequisite
- Ensure you have [Docker](https://docs.docker.com/engine/install/) installed.

To set up the project locally, and spin up a Docker container to reproduce our experiments, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/vlad-nitu/AmplificationAttacksInTheWild_BE_LU
cd AmplificationAttacksInTheWild_BE_LU
````

2. Spin up Docker container, that contains all the Python dependencies and CLI tools needed:
```bash
docker build -t rp_container -f configs/Dockerfile . # Build the Docker image from the Dockerfile
docker run -it rp_container:latest # Create Docker container (in interactive mode, so start a shell inside the container) from the Docker image.
```

## Usage
### `scripts/search_amplifier.py` (CLI Interface):
- ❗❗❗ This steps assumes that the user has already followed Step 1 from Methodology V.1: "Obtain the data"; The data can be aquired either through passive scanning, by retrieving servers from search engines targeting internet-connected devices, such as: [Censys](https://search.censys.io/) or [Shodan](https://www.shodan.io/dashboard), or through active scanning by using tools such as [ZMap](https://zmap.io/)
- **Step 2** ("Check if the server is open to the public") from Methodology V.1 in [paper](https://www.overleaf.com/read/nrzpjghcbfmc#76541b) - Fig. 1:
- Obtains the open servers, depending on the protocol you are interested in: DNS, NTP or Memcached, by probing the servers from `file_path` with a "basic" query, such as: 
  - DNS: Requesting for "A" records from "google.com".
  - NTP: Sending a Mode 3 (Client) query.
  - Memcached: Sending a "stats slabs" query.
- The file residing at `file_path` should have the following format:
```json
[
  IP1_str,
  IP2_str,
  ...
]
```
For example:
```json
[
  "1.2.3.4",
  "4.5.6.7",
  ...
]
```
- 💡 Filepath should end in `_before_filtering.json`, a suffix that the Python script will remove when creating the output file path. 
; i.e.: If `file_path` is `X_before_filtering.json`, the output filepath (that points to the file which contains the list of filtered IPs after only persisting the open servers) will be `X.json`


For more information about the script, run `python3 search_amplifier.py` from the `scripts` directory, or check [the source code](https://github.com/vlad-nitu/AmplificationAttacksInTheWild_BE_LU/blob/main/scripts/search_amplifiers.py)
```bash
➜  scripts git:(main) python3 search_amplifiers.py -h
usage: search_amplifiers.py [-h] -p {dns,ntp,memcached} [{dns,ntp,memcached} ...] [--domain_ip DOMAIN_IP] [--dns_query_type {A,ANY,NS,AXFR,DNSKEY,TXT}]
                            [--ntp_query_type {version,monlist,peer_list,peer_list_sum,get_restrict,basic}] [--max_udp_size] [--max_udp_filepath MAX_UDP_FILEPATH] [-v]
                            file_path

Search for potential open servers in the list of IPs.

positional arguments:
  file_path             Absolute input file path, ending with '_before_filtering.json'; Contains a list of IPs to actively probe whether they are open; The file format should be a JSON file containing a JSON Array, each
                        element of the array being an IP string.

optional arguments:
  -h, --help            show this help message and exit
  -p {dns,ntp,memcached} [{dns,ntp,memcached} ...], --protocols {dns,ntp,memcached} [{dns,ntp,memcached} ...]
                        Protocols to check for servers: dns, ntp, memcached
  --domain_ip DOMAIN_IP
                        Domain to resolve for DNS protocol (default: google.com)
  --dns_query_type {A,ANY,NS,AXFR,DNSKEY,TXT}
                        Type of DNS query to send: A, ANY, NS, AXFR, DNSKEY, TXT (default: A)
  --ntp_query_type {version,monlist,peer_list,peer_list_sum,get_restrict,basic}
                        Type of NTP query to send: version, monlist, peer_list, peer_list_sum, get_restrict, basic (default: basic)
  --max_udp_size        Flag to indicate if max UDP size statistics are required
  --max_udp_filepath MAX_UDP_FILEPATH
                        File path to the EDNS Buffer Size file statistics, ending in '_max_udp.json'
  -v, --verbose         Increase output verbosity (by triggering DEBUG level logging)
```

### `scripts/measure_baf.py` (CLI Interface):

- ❗❗❗ This steps assumes that the user has already followed Step 1 and 2 from Methodology V.1: "Obtain the data" and "Check if the server is open to the public", respectively.; 
- **Step 3 & 4** ("Check if the server is an amplifier" & "Measure the BAF") from Methodology V.1 in [paper](https://www.overleaf.com/read/nrzpjghcbfmc#76541b) - Fig. 1:
- 💡️ The `file_path` received as input by the program should be the output file path produced by running the previous file on `_before_filtering.json` filepath. (i.e.: the `file_path` should be `X_json`). It should point to a file of the following format
```json
[
  IP1_open_server,
  IP2_open_server,
  ...
]
```
For example:

```json
[
  "1.2.3.4",
  "4.5.6.7",
  ...
]
```
- ✍️ The output filepath of this step will append `_baf.json` to the filepath received as input, and will point to a file that has the following format:
```json
[
  [
    IP1_str,
    BAF1_float
  ],
  [
    IP2_str,
    BAF2_float
  ],
  ...
]
```
For example:

```json
[
  [
    "1.2.3.4",
    1232.00
  ],
  [
    "5.6.7.8",
    4242.42
  ],
  ...
]
```
For more instructions about this Python script, run `python3 measure_baf.py -h` from the `scripts `directory, or check [the source code](https://github.com/vlad-nitu/AmplificationAttacksInTheWild_BE_LU/blob/main/scripts/measure_baf.py)
```bash
 ➜  scripts git:(modify_loop_DoS_code) python3 measure_baf.py -h
usage: measure_baf.py [-h] -p {dns,ntp,memcached} [{dns,ntp,memcached} ...] [--domain_ip DOMAIN_IP] [--dns_query_type {A,ANY,NS,AXFR,DNSKEY,TXT}]
                      [--ntp_query_type {version,monlist,peer_list,peer_list_sum,get_restrict,basic}] [--max_udp_size] [--max_udp_filepath MAX_UDP_FILEPATH]
                      [-v]
                      file_path

Compute BAF (Bandwidth Amplification Factor) for various protocols; Should be used after the filtering step done in `search_amplifiers.py`

positional arguments:
  file_path             Absolute input file path; Contains a list of IPs to actively probe to compute the BAF they obtain; The file format should be a JSON file
                        containing a JSON Array, each element of the array being an IP string.

optional arguments:
  -h, --help            show this help message and exit
  -p {dns,ntp,memcached} [{dns,ntp,memcached} ...], --protocols {dns,ntp,memcached} [{dns,ntp,memcached} ...]
                        Protocols to check for amplifiers: dns, ntp, memcached
  --domain_ip DOMAIN_IP
                        Domain to resolve for DNS protocol (default: google.com)
  --dns_query_type {A,ANY,NS,AXFR,DNSKEY,TXT}
                        Type of DNS query to send: A, ANY, NS, AXFR, DNSKEY, TXT (default: A)
  --ntp_query_type {version,monlist,peer_list,peer_list_sum,get_restrict,basic}
                        Type of NTP query to send: version, monlist, peer_list, peer_list_sum, get_restrict (default: version)
  --max_udp_size        Flag to indicate if max UDP size statistics are required
  --max_udp_filepath MAX_UDP_FILEPATH
                        File path to the EDNS Buffer Size file statistics, ending in '_max_udp.json'
  -v, --verbose         Increase output verbosity
```


### `scripts/visualiser_*.py` (Visualisation tool):
- Several visualisation scripts that have the filepath starting with `visualiser_`, ranging from bar plots and box plots, to CDFs, scatter plots and heatmaps.; These scripts were mainly used to generate aggregated statistics for the final report and the poster presentation, but may prove useful for users of this tool in obtaining more insight of their data. 
- ❗❗❗ These visualiser scripts do not have the form of a CLI Interface, but instead have to be run interactively by the user; If there is anything unclear in terms of how to use a visualiser script, make sure to first check its source code, and if you still find yourself in trouble, contact [the author](mailto:v.p.nitu@student.tudelft.nl?cc=nituvladpetru@gmail.com)

### `scripts/loop-DoS-RP` (Forked & adapted repository):
- [Forked repository](https://github.com/vlad-nitu/loop-DoS-RP) from [Pan et al.'s source code](https://github.com/cispa/loop-DoS) to adapt the constraints to the scale of our dataset (read our paper for more details of how and why we removed constraints).
- Follow the methodology described in that repository's ReadME file. 
 
## Example Work Flow
- Step 1.1: Gather a list of hosts that run DNS, NTP or Memcached (from Censys, Shodan or any other search engine).
- Step 1.2: Preprocess the list of hosts to be stored in JSON format, in a [JSON Array](https://www.microfocus.com/documentation/silk-performer/205/en/silkperformer-205-webhelp-en/GUID-0847DE13-2A2F-44F2-A6E7-214CD703BF84.html), as detailed in [Usage subsection](#usage).
- Step 2: Running `python search_amplifiers.py` to filter out the offline  hosts.
- Step 3: Running `python measure_baf.py` on the filtered list (outputted after Step 2) of hosts to measure their BAF.
- Step 4: Running visualisation scripts to generate aggregated results.

**NOTE** that metadata can also be gathered via `fpdns`, `ntpd` and other CLI tools, depending on the protocol, as detailed in the paper. This metadata can be used
in some visualisation scripts to aggreagte data on different categories, such as OS run by NTP server, DNS version run by DNS server, etc.

## Project Structure

```bash
PublishedCode
├── configs # Configuration files - Dockerfile 
├── converters # Scripts to convert data formats
├── data # Stores files related to aggregated data (plots)
│       ├── IANA # ccTLDs retrieved from IANA
│       ├── censys_all_data # Censys DNS and NTP data
│       │       ├── ai # .ai gTLD
│       │       ├── bg # .bg ccTLD
│       │       ├── bn # .bn ccTLD
│       │       ├── dns_fingerprinting # DSN Fingerprinting conducted w/ `fpdns`
│       │       ├── rwe # .bn gTLD
│       │       ├── si # .si gTLD
│       │       ├── sl # .sl ccTLD
│       │       └── ve # .ve ccTLD
│       ├── ntp_pool # NTP Pool servers
│       ├── pagerank # Most searched domains ranked using the PageRank algo.
│       └── shodan # Shodan Memcached data
│            └── BE_LU
├── loop-DoS-RP # Loopy code used to check for application-level loops
│       ├── rsps
│       └── verify
└── scripts # Stores the files for methodology, that gather statistics and visualisation scrips
    └── nmap
```

## Contact
- Student Name: [Vlad-Petru Nitu](mailto:v.p.nitu@student.tudelft.nl?cc=nituvladpetru@gmail.com)
- Student E-mail: V.P.Nitu@student.tudelft.nl
- [Cybersecurity group](https://www.tudelft.nl/ewi/over-de-faculteit/afdelingen/intelligent-systems/cybersecurity) at EEEMCS@TUDelft: if you are interested in collaborating with the Responsible Professor or the Supervisor.