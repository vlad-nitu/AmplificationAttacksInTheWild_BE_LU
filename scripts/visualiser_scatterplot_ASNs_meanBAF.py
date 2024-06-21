import plotly.graph_objects as go
import plotly.express as px

from visualiser_ASNs_meanBAF_base import load_json_file, aggregate_data, sort_asn_dict_by_mean_baf

root_baf = '../data/censys_all_data/dns_8k_IPs_domain_ip:._baf.json'
root_ASNs = '../data/censys_all_data/dns_8k_ASNs.json'

width = 1600
height = 1024

SYMBOLS = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
]


def create_scatterplot(asn_dict, baf_filepath) -> None:
    """
    Draws scatterplot based on `asn_dict data`, and uses `baf_filepath` to name the ouput filepath
    :param asn_dict: preprocessed data that stores statistics about ASN (Autonomous System Number)
    and associated BAFs of IPs of that are part of a given ASN
    :param baf_filepath: filepath of the input file, used to name the output filepath
    :return: None
    """
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, (asn, data) in enumerate(asn_dict.items()):
        if len(data['ip_bafs']) < 10:  # Skip empty IP_BAFs lists
            continue
        _, bafs = zip(*data['ip_bafs'])
        fig.add_trace(go.Scatter(
            x=[f"ASN {asn}"] * len(bafs),
            y=bafs,
            mode='markers',
            name=f"ASN {asn}<br>({data['name']})",
            marker=dict(color=colors[idx % len(colors)], symbol=SYMBOLS[idx % len(SYMBOLS)], size=18)
        ))

    fig.update_layout(
        xaxis_title='ASN (IP Count)',
        yaxis_title='BAF (Bandwidth Amplification Factor)',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(asn_dict))),
            ticktext=[f"{asn}<br>({len(data['ip_bafs'])})" for asn, data in asn_dict.items()],
            title=dict(font=dict(size=28)),  # Title font size
            tickfont=dict(size=16),  # Ticks font size
            title_standoff=40
        ),
        yaxis=dict(
            title=dict(font=dict(size=28)),  # Title font size
            tickfont=dict(size=24)  # Ticks font size
        ),
        legend=dict(font=dict(size=10), x=0.99, y=0.99, xanchor='right', yanchor='top'),
        width=width,
        height=height
    )

    fig.show()
    # Save the plot as an image
    output_filepath = baf_filepath[:-9] + f"_ASNs_scatterplot.png"
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
    create_scatterplot(sorted_aggregated_data, baf_filepath)
