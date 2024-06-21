import logging

import plotly.graph_objects as go
import itertools
import numpy as np

MAX_VALUE = 1024 * 1024  # 1MB = 1024 * 1024 Bytes
width = 1600
height = 1400


def generate_3d_plot(key_size_values, num_keys_values, results) -> None:
    """
    Generates a 3D Plot that depicts the theoretical maximal BAF in Memacached
    The plot assumes that each key is only 1 character long, and stores the max. value of 1MB

    :param key_size_values: # of keys of 1 char. long
    :param num_keys_values: # of k
    :param results: max BAFs
    :return: None
    """
    # Create a 3D surface plot
    fig = go.Figure(data=[go.Surface(
        z=results,
        x=key_size_values,
        y=num_keys_values,
        colorscale='Viridis',
        colorbar=dict(
            thickness=40,
            len=0.75,
            x=0.9,
            tickfont=dict(size=30),  # Increase font size for the color bar ticks
            titlefont=dict(size=30)  # Increase font size for the color bar title
        )  # Adjust the color bar position and size
    )])

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Key Length', titlefont=dict(size=28), tickfont=dict(size=18)),
            # Add spacing between the title and the x-axis ticks
            yaxis=dict(title='Number of Keys', titlefont=dict(size=28), tickfont=dict(size=18)),
            zaxis=dict(
                title='BAF (Bandwidth Amplification Factor)',
                titlefont=dict(size=28),
                tickfont=dict(size=15),
                tickvals=np.arange(50000, 500000 + 1, step=50000),
                ticks='inside'
            )
        ),
        font=dict(size=18),
        autosize=False,
        width=width,
        height=height,
        margin=dict(t=100, b=20, l=0, r=0)  # Adjust top and bottom margins
    )

    # Add an annotation for the Z-axis title to move it to the left
    fig.add_annotation(
        x=0,  # Adjust as needed
        y=0.5,  # Center on the Y-axis
        text='BAF (Bandwidth Amplification Factor)',
        showarrow=False,
        xref='paper',
        yref='paper',
        xanchor='right',
        yanchor='middle',
        font=dict(size=28),
        textangle=-90  # Rotate the text
    )

    # Show & Persist the figure
    output_filepath = "../data/censys_all_data/memcached_factors.png"
    fig.write_image(output_filepath, width=width, height=height)
    logging.warning(f"The 3D Plot was saved in {output_filepath}\n")


def max_BAF_memcached(key_size, num_keys):
    """
    Method that computer the theoretical max BAF (Bandwith Amplification Factor) in a Memcached db, assuming
    `num_keys` keys of size `key` holding MAX_VALUE = 1MB value
    :param key_size: # of characters of key
    :param num_keys: # of keys in database
    :return: theoretical max BAF
    """
    #   Prefix  `get` `\r\n`
    req_size = 8 + 3 + 2 + num_keys * (1 + key_size)
    resp_size = num_keys * MAX_VALUE
    BAF = resp_size / req_size
    return BAF


if __name__ == "__main__":
    data = []
    key_size_values = range(1, 100 + 1)
    num_keys_values = range(1, 100 + 1)

    for key_size, num_keys in itertools.product(key_size_values, num_keys_values):
        data.append(
            {
                "key_size": key_size,
                "num_keys": num_keys,
                "result": max_BAF_memcached(key_size, num_keys)
            }
        )
    # Generate data
    key_size_values = np.linspace(1, 100, 100)  # Range of key sizes
    num_keys_values = np.linspace(1, 100, 100)  # Range of number of keys
    key_size, num_keys = np.meshgrid(key_size_values, num_keys_values)
    results = max_BAF_memcached(key_size, num_keys)
    generate_3d_plot(key_size_values, num_keys_values, results)
