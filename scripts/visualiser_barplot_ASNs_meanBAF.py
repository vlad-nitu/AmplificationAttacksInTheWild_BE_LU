import plotly.graph_objects as go
import plotly.express as px
from visualiser_ASNs_meanBAF_base import *

COLORS=px.colors.qualitative.Plotly * 10 # To wrap around if # Plotly colors < # ASNs 

root_baf = '../data/censys_all_data/dns_8k_IPs_domain_ip:._baf.json'
root_ASNs = '../data/censys_all_data/dns_8k_ASNs.json'

width = 1600
height = 1024

def create_barplot(asn_dict, baf_filepath) -> None:
    """
    Method that draws the barplot based on asn_dict data
    :param asn_dict: dictionary containing ASN info
    :param baf_filepath: path to file containing BAF info to name the ouput file basd on this one
    :return: None
    """
    # Prepare data for the bar plot
    asn_labels = []
    mean_bafs = []
    ip_counts = []

    for asn, data in asn_dict.items():
        if len(data['ip_bafs']) < 10:  # Skip empty IP_BAFs lists
            continue
        mean_baf = np.mean([baf for ip, baf in data['ip_bafs']])
        asn_labels.append(str(asn))
        mean_bafs.append(mean_baf)
        ip_counts.append(f"IPs: {len(data['ip_bafs'])}")

    # Create the bar plot
    fig = go.Figure(data=[
        go.Bar(
            x=asn_labels,
            y=mean_bafs,
            text=ip_counts,
            textposition='auto',
            marker=dict(color=COLORS),
            textfont=dict(size=20)  # Increase text size for the annotations on the bars
        )
    ])

    fig.update_layout(
        xaxis_title='ASN (Autonomous System Number)',
        yaxis_title='Average BAF (Bandwidth Amplification Factor)',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(asn_labels))),
            ticktext=asn_labels,
            title=dict(font=dict(size=25)), # Title font size
            tickfont=dict(size=15), # Ticks font size
            title_standoff=20
        ),
        yaxis=dict(
            title=dict(font=dict(size=25)), # Title font size
            tickfont=dict(size=24) # Ticks font size
        ),
        width=width,
        height=height
    )

    fig.show()
    # Save the plot as an image
    output_filepath = baf_filepath[:-9] + f"_ASNs_barplot.png"
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
    create_barplot(sorted_aggregated_data, baf_filepath)
