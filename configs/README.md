# Estimating the Amplification Factor of Three Common Protocols in DRDoS
## A Quantitative Analysis on the Weaponisation of Hosts Located in Greece

### CSE3000 / Research Project @ TU Delft
This repository hosts the code that was written to run the experiments for my Research Project (CSE3000 / Q4-2024) thesis
 along with some results of what BAFs were achieved.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Directory Structure](#directory-structure)
    - [./throwaway_scripts](#throwaway_scripts)
    - [./aggregated_results](#aggregated_results)
        - [buffersize_boxplots](#buffersize_boxplots)
        - [ntp_scatterplots](#ntp_scatterplots)
        - [compare_correlation](#compare_correlation)
        - [piecharts](#piecharts)
        - [fingerprint_boxplots](#fingerprint_boxplots)
        - [poster_plots](#poster_plots)
        - [combined_plots_buffer_sizes](#combined_plots_buffer_sizes)
        - [histograms_barplots](#histograms_barplots)
        - [combined_plots_fingerprints](#combined_plots_fingerprints)
        - [fingerprint_scatterplots](#fingerprint_scatterplots)
        - [buffersize_scatterplots](#buffersize_scatterplots)
        - [cdfs](#cdfs)
        - [network_info](#network_info)
        - [plots](#plots)
    - [./scripts](#scripts)
    - [./shell_scripts](#shell_scripts)
5. [License](#license)
6. [Contributing](#contributing)
7. [Contact](#contact)

## Introduction

My project mainly consisted of gathering hosts located in Greece that run DNS, NTP and Memcached. I further had
to measure the maximum bandwidth amplification factor (BAF) they could reach.

## Installation

The experiments I ran can be reproduced by building the Docker container and running it. The steps are shown below. 

1. Build the Docker container

Firstly, make sure that your are in the *scripts* folder, where the Dockerfile is located. Make sure your docker daemon is also running. Then run: 

`docker build -t python-app .`

You can change `python-app` to any other tag. 

2. Run the Docker container

`docker run -it python-app` 

3. You are all set

After running the previous command, you should now be in a shell and you should be able to run any script from within the Docker container. 

## Usage

An example usage of our application could be something along the lines (doing the `Installation` stage):
    - Gathering a list of hosts that run DNS (from Censys or another source) in CSV format.
    - Doing `python check.py` to filter out the offline DNS hosts.
    - Running `python measure.py` on the filtered list of hosts to measure their BAF.
    - Running plotting scripts to generate results (metadata can also be gathered via `fpdns`). 

## Directory Structure

### ./throwaway_scripts

This includes non-essential script files that need to be developed further.
Their sole purpose was to mainly prototype sending requests to Memcached servers over TCP and discovering
what keys and values are stored in them. There was also one shallow attempt at trying to modularise
the code to suit different strategies for each protocol, with the goal in mind of being able to test multiple 
servers with a multitude of different queries (i.e. if a DNS NS does not answer to "ANY", it might still lead 
to a high BAF via a "TXT" or "DNSKEY" query).

### ./aggregated_results

This directory contains aggregated results, including plots, charts, and other visualisations. 
It is organised into several subdirectories:

#### buffersize_boxplots

Contains boxplots per buffer sizes, for different DNS queries.

#### ntp_scatterplots

Contains scatterplots for NTP BAFs per Operating System ran. 

#### compare_correlation

Mainly contains heatmaps comparing two features at a time, to investigate
possible correlations (e.g. Raiden DNSD advertises an EDNS0 buffer size of 4,096 in 100% of cases).

#### piecharts

This directory has piecharts depicting the distribution of hosts and their BAF. 

#### fingerprint_boxplots

Contains boxplots for DNS BAFs per DNS software / Vendor / Product. 

#### poster_plots

This directory has plots that were used in the poster.

#### combined_plots_buffer_sizes

Combines scatter plots and box plots for DNS BAFs per EDNS0 advertised buffer size.

#### histograms_barplots

Various histograms and bar plots related to DNS and NTP BAFs.

#### combined_plots_fingerprints

Combines scatter plots and box plots for DNS BAFs per DNS software / Vendor / Product.

#### fingerprint_scatterplots

Contains scatter plots for DNS BAFs per DNS software / Vendor / Product. 

#### buffersize_scatterplots

Contains scatterplots per buffer sizes, for different DNS queries.

#### cdfs

This has CDF plots for BAF per top 5 DNS implementations / top 5 buffer size groups.

#### network_info

This directory contains visualisations of DNS BAFs per ASN.

#### plots

Contains miscellaneous plots. 

### ./scripts

This directory contains scripts used for data processing, visualization, and analysis:

- `measure.py`: Script for measuring BAF. It contains strategies for each protocol of sending requests that will lead to large responses. The
input that is generally expected is a csv file containing a single column, the IP addresses.
- `merge.py`: This mainly merges DataFrames on the IP column, to aggregate different measurements. 
- `check.py`: This script mainly contains strategies for filtering offline hosts. It contains common requests that an open
server would be expected to answer.
- `requirements.txt`: Dependency file, used for reproducibility purposes when running the scripts from the Docker container.
- `funnelchart.py`: Script for generating funnel charts.
- `Dockerfile`: Docker configuration for the project.
- `memcached_client.py`: Client script for Memcached, has some experimental methods to send Memcached hosts requests over TCP.
- `histograms_barplots.py`: Script for creating histograms and bar plots.
- `cdfs.py`: Script for generating CDF plots.
- `piecharts.py`: Script for creating pie charts.
- `get_network_info.py`: Script for retrieving network information from the Censys JSON file.
- `recursive_dns.py`: Script for checking if a DNS host is recursive.
- `domains_to_ns.py`: Script for finding authoritative NS (their domain name).
- `retrieve_domains.py`: Script for retrieving domains from the top domain list (in my case, I fetch around 1000 of the top Greek domains).
- `utils.py`: Utility functions that are used in several other scripts. Contains methods that deal with reading and writing csvs, reading, writing and processing JSON files.
- `stats.py`: Script for computing interesting statistics, such as the mean/median of the top 10% of hosts (according to the BAF achieved).
- `name_servers_to_ips.py`: Script for mapping authoritative NS (domains) to IPs.
- `scatterplots.py`: Script for generating scatter plots.
- `fingerprint_dns.py`: Script for fingerprinting DNS hosts in order to find the software version they are running.
- `boxplots.py`: Script for creating box plots.
- `compare_correlation.py`: Script for generating heatmaps.
- `rank_cctlds.py`: Script for ranking ccTLDs according to the BAF achieved (DNS). Also contains a script that retrieves the system information for NTP hosts (i.e. the operating system).

## ./shell_scripts 

This directory contains a few shell scripts that deal with processing JSON information retrieved from JSON, to only keep the information needed.

## License

This project is licensed under the terms of the [LICENSE](./LICENSE).

## Contributing

This project is not open to contributions. However, you are free to fork the repository and make changes on your own. 

## Contact

For any inquiries, feel free to contact me at [rarestoader02@gmail.com](mailto:rarestoader02@gmail.com).
