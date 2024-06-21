import json

import numpy as np
import plotly.graph_objects as go

# List of symbols to use for the CDF curves
SYMBOLS = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
]

width = 1600
height = 1024

root_fpdns = '../data/censys_all_data/dns_8k_IPs_._fpdns.json'
n = 5
 

def generate_cdf(input_dict_sorted) -> None:
    """
    Generate the CDF (cumulative distribution function) for the sorted input dictionary
    :param input_dict_sorted: sorted input dictionary
    :return: None
    """
    fig = go.Figure()  # Init figure
    n_most_largest_mean_BAFs_versions = list(input_dict_sorted.items())[:n]  # Take first (head) `n`
    # Visualiser BAF vs CDF for 5-most largest BAF versions
    for idx, (version, (count, mean_BAF, ips_bafs_dict)) in enumerate(n_most_largest_mean_BAFs_versions):
        all_bafs = list(ips_bafs_dict.values())
        print(version, count)

        # Generate the CDF data
        all_bafs_sorted = np.sort(all_bafs)
        cdf = np.arange(1, len(all_bafs_sorted) + 1) / len(all_bafs_sorted)

        # Add each CDF trace to the figure
        fig.add_trace(go.Scatter(
            x=all_bafs_sorted,
            y=cdf,
            mode='lines+markers',
            name=f'{version}',
            marker=dict(symbol=SYMBOLS[idx % len(SYMBOLS)], size=16)
        ))

    # Update plot layout to include all CDFs
    fig.update_layout(
        xaxis_title='BAF (Bandwidth Amplification Factor)',
        yaxis_title='CDF (Cumulative Distribution Function)',
        xaxis=dict(
            showgrid=True,
            title=dict(font=dict(size=40)), # Title font size
            tickfont=dict(size=44), # Ticks font size
            title_standoff=40  # Add spacing between the title and the x-axis ticks
        ),
        yaxis=dict(
            showgrid=True,
            title=dict(font=dict(size=36)), # Title font size
            tickfont=dict(size=36), # Ticks font size
        ),
        legend=dict(
            font=dict(
                size=32,
            ),
            title=dict(text='Versions',font=dict(size=30)),
            itemsizing='constant',
            x=0.99,  # X position of the legend
            y=0.01,  # Y position of the legend
            xanchor='right',
            yanchor='bottom',
        ),
        width=width,
        height=height
    )

    # Show the combined plot
    fig.show()
    # 1
    cdf_output_filepath = input_filepath[:-5] + f"_cdfs_{n}_most_largest_mean_BAFs.png"
    fig.write_image(cdf_output_filepath, width=width, height=height)


def generate_version_BAF(input_dict_sorted) -> None:
    """
    Generate a bar plot that depicts the BAFs distribution per DNS version
    :param input_dict_sorted: sorted input dictionary
    :return: None
    """
    # Visualiser Version vs BAF for all DNS versions
    # Initialize lists to store your data for plotting
    versions = []
    mean_BAFs = []

    # Extract data from the dictionary
    for version, (count, mean_BAF, ips_bafs_dict) in input_dict_sorted.items():
        versions.append(version)
        mean_BAFs.append(mean_BAF)

    # Create a bar plot
    fig = go.Figure(data=[
        go.Bar(x=versions, y=mean_BAFs, marker_color='indigo')
    ])

    # Update plot layout
    fig.update_layout(
        title='Version vs. Bandwidth Amplification Factor (BAF)',
        xaxis_title='Version',
        yaxis_title='Mean BAF',
        xaxis={'categoryorder': 'total descending'}
    )

    # Show the figure
    fig.show()
    baf_version_output_filepath = input_filepath[:-5] + f"mean_BAFs_versions.png"
    fig.write_image(baf_version_output_filepath, width=1024, height=768)


if __name__ == "__main__":
    input_filepath = input("Please provide the path to the input file\n"
                           "This file should be a JSON file and should terminate in `_fpdns.json`\n").lower()
    if not input_filepath.endswith("_fpdns.json"):
        raise ValueError("Input file is not a _fpdns.json type of file")

    n = int(input("Please input `n`, where `n` = n-most versions that you are interested in to analyse\n"))

    with open(input_filepath, "r") as file:
        input_dict = json.load(file)
        input_dict_sorted = {k: v for k, v in
                             reversed(sorted(input_dict.items(), key=lambda item: item[1][1]))}  # Sort by mean_BAF

    generate_cdf(input_dict_sorted)
    generate_version_BAF(input_dict_sorted)
