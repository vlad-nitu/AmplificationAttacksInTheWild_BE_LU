import pandas as pd
import json
import plotly.graph_objs as go

SYMBOLS = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
]

width = 1600
height = 1024

# Define file paths
file_path_buffers = '../data/censys_all_data/dns_8k_IPs_max_udp.json'
file_path_bafs_root = '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json'
file_path_bafs_sl = '../data/censys_all_data/sl/dns_8k_IPs_domain_ip:sl._dns_query_type:ANY_max_udp_size:False_baf.json'
file_path_bafs_bg = '../data/censys_all_data/bg/dns_8k_IPs_domain_ip:bg._dns_query_type:ANY_max_udp_size:True_baf.json'
# Define the file path you will use
file_path_bafs = file_path_bafs_bg


def preprocess_data():
    """
    Read user data & preprocess it
    :return: preprocessed data in the form of a Pandas DataFrame
    """
    # Load the JSON files
    with open(file_path_buffers, 'r') as f:
        buffers_data = json.load(f)

    with open(file_path_bafs, 'r') as f:
        bafs_data = json.load(f)

    # Convert the JSON data into DataFrames
    buffers_df = pd.DataFrame(buffers_data)
    buffers_df = buffers_df.melt(var_name='ip', value_name='edns0_buffer_size')
    buffers_df.dropna(inplace=True)  # Drop any rows with NaN values

    bafs_df = pd.DataFrame(bafs_data, columns=['ip', 'baf'])

    # Merge the data on IP addresses
    merged_df = pd.merge(buffers_df, bafs_df, on='ip')
    return merged_df

def draw_cdf(merged_df) -> None:
    """
    Draw CDF based on input preprocessed data (merged_df)
    :param merged_df: input, preprocessed data
    :return: None
    """

    # Initialize the plotly figure
    fig = go.Figure()

    # Get the unique EDNS0 buffer sizes
    buffer_sizes = merged_df['edns0_buffer_size'].unique()

    # Plot the CDF for each buffer size using the BAF values
    for idx, buffer_size in enumerate(buffer_sizes):
        subset = merged_df[merged_df['edns0_buffer_size'] == buffer_size]
        if len(subset) <= 5:  # Skip ENDS0 Buffer Size category if it has <= 5 IPs in it
            continue

        subset = subset.sort_values(by='baf')
        subset['cdf'] = subset['baf'].rank(method='max') / len(subset)

        fig.add_trace(go.Scatter(
            x=subset['baf'],
            y=subset['cdf'],
            mode='lines+markers',
            name=f'Buffer Size {buffer_size}',
            marker=dict(symbol=SYMBOLS[idx % len(SYMBOLS)], size=16)
        ))

    # Update plot layout to include all CDFs
    fig.update_layout(
        xaxis_title='BAF (Bandwidth Amplification Factor)',
        yaxis_title='CDF (Cumulative Distribution Function)',
        xaxis=dict(
            showgrid=True,
            title=dict(font=dict(size=30)),  # Title font size
            tickfont=dict(size=26),  # Ticks font size
            title_standoff=40  # Add spacing between the title and the x-axis ticks
        ),
        yaxis=dict(
            showgrid=True,
            title=dict(font=dict(size=30)),  # Title font size
            tickfont=dict(size=26),  # Ticks font size
        ),
        legend=dict(
            font=dict(
                size=24,
            ),
            title=dict(text='Buffer Size', font=dict(size=30)),
            itemsizing='constant',
            x=0.99,  # X position of the legend
            y=0.01,  # Y position of the legend
            xanchor='right',
            yanchor='bottom',
        ),
        width=width,
        height=height
    )

    # Show the plot
    fig.show()

    cdf_output_filepath = file_path_bafs[:-5] + "_ENDS0_Buffer_Size_baf_cdf.png"
    fig.write_image(cdf_output_filepath, width=width, height=height)

if __name__ == "__main__":
    df = preprocess_data()
    draw_cdf(df)
