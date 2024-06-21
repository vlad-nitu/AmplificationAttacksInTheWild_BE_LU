import plotly.graph_objects as go
import plotly.express as px
from visualiser_ASNs_meanBAF_base import *

root_baf = '../data/censys_all_data/dns_8k_IPs_domain_ip:._baf.json'
root_ASNs = '../data/censys_all_data/dns_9k_ASNs.json'

width = 1600
height = 1024

def create_boxplot(asn_dict, baf_filepath):
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, (asn, data) in enumerate(asn_dict.items()):
        ips, bafs = zip(*data['ip_bafs'])
        fig.add_trace(go.Box(
            y=bafs,
            name=f"ASN {asn} ({data['name'].split()[0]})", # Take only the first word from the ASN name to keep plot succint
            boxmean=True,
            marker_color=colors[idx % len(colors)]
        ))

    fig.update_layout(
        xaxis_title='ASN (IP Count)',
        yaxis_title='BAF (Bandwidth Amplification Factor)',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(asn_dict))),
            ticktext=[f"{asn}<br>({len(data['ip_bafs'])})" for asn, data in asn_dict.items()], # ip_count = len(zip(*data['ip_bafs']))
            # tickangle=-45,
            title=dict(font=dict(size=25)), # Title font size
            tickfont=dict(size=15), # Ticks font size
            title_standoff=20
        ),
        yaxis=dict(
            title=dict(font=dict(size=25)), # Title font size
            tickfont=dict(size=24) # Ticks font size
        ),
        legend=dict(
            font=dict(
                size=15,
            ),
            itemsizing='constant',
            x=0.99,  # X position of the legend
            y=0.99,  # Y position of the legend
            xanchor='right',
            yanchor='top',
        ),
        width=width,
        height=height
    )

    fig.show()
    # Save the plot as an image
    output_filepath = baf_filepath[:-9] + f"_ASNs_boxplot.png"
    fig.write_image(output_filepath, width=width, height=height)

if __name__ == "__main__":
    baf_filepath = input("Please provide the path to the BAF JSON file ending in `_baf.json`:\n")
    if not baf_filepath.endswith("_baf.json"):
        raise ValueError("Input file is not a `_baf.json` type of file")

    asn_filepath = input("Please provide the path to the ASN JSON file ending in `_ASNs.json`:\n")
    if not asn_filepath.endswith("_ASNs.json"):
        raise ValueError("Input file is not a `_ASNs.json` type of file")

    baf_data = load_json_file(baf_filepath)
    asn_data = load_json_file(asn_filepath)

    aggregated_data = aggregate_data(baf_data, asn_data)
    sorted_aggregated_data = sort_asn_dict_by_mean_baf(aggregated_data)
    create_boxplot(sorted_aggregated_data, baf_filepath)
