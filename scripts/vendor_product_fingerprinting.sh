# jq '[.[] | {ip: .ip, product: .operating_system.product, vendor: .operating_system.vendor}]' ../data/censys_all_data/dns_ALL_8k_wild_before_filtering.json > ../data/censys_all_data/dns_8k_wild_product_vendor_fingerprinting.json
jq '[.[] | {ip: .ip, product: .operating_system.product, vendor: .operating_system.vendor}]' ../data/censys_all_data/ntp_ALL_ans_to_loopy.json > ../data/censys_all_data/NTP_ALL_ans_to_loopy_product_vendor_fingerprinting.json

