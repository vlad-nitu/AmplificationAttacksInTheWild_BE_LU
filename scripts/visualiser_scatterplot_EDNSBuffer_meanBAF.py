import plotly.graph_objects as go
import plotly.express as px

from visualiser_boxplot_EDNSBuffer_meanBAF_base import preprocess_data

root_bafs = '../data/censys_all_data/dns_8k_IPs_domain_ip:._baf.json'
root_max_udps = '../data/censys_all_data/dns_8k_IPs_domain_ip:._ANY_max_udp.json'

width = 1600
height = 1024

SYMBOLS = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
]


def draw_scatterplot(req_size, bafs_filepath, sorted_bafs_per_EDNS_buf):
    """
    Draws scatterplot
    :param req_size: Size of request, in order to compute threshold
    :param bafs_filepath: filepath of BAFs received as input, to name the output file using it
    :param sorted_bafs_per_EDNS_buf: dictionary that contains data we want to plot in a boxplot
    :return: None
    """
    # Step 4: Plot the results in a single scatter plot
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, (EDNS_buf_size, bafs) in enumerate(sorted_bafs_per_EDNS_buf.items()):
        # Calculate the threshold
        threshold = EDNS_buf_size / req_size

        # Assign color for the buffer size
        color = colors[idx % len(colors)]

        # Add scatter plot for BAF values
        fig.add_trace(go.Scatter(
            x=[str(EDNS_buf_size)] * len(bafs),
            y=bafs,
            mode='markers',
            marker=dict(color=color, symbol=SYMBOLS[idx % len(SYMBOLS)], size=18),
            name=f'{EDNS_buf_size}'
        ))

        # Add horizontal line for threshold
        fig.add_shape(type="line",
                      x0=idx - 0.4, y0=threshold,
                      x1=idx + 0.4, y1=threshold,
                      line=dict(color=color, width=2, dash="dash"))

    # Update layout
    fig.update_layout(
        xaxis_title='EDNS0 Buffer Size (IP Count)',
        yaxis_title='BAF (Bandwidth Amplification Factor)',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(sorted_bafs_per_EDNS_buf))),
            ticktext=[f"{EDNS_buf_size}<br>({len(bafs)})" for EDNS_buf_size, bafs in sorted_bafs_per_EDNS_buf.items()],
            title=dict(font=dict(size=28)),  # Title font size
            tickfont=dict(size=24),  # Ticks font size
            title_standoff=40
        ),
        yaxis=dict(
            title=dict(font=dict(size=28)),  # Title font size
            tickfont=dict(size=24)  # Ticks font size
        ),
        legend=dict(font=dict(size=20), x=0.01, y=0.99, xanchor='left', yanchor='top'),
        width=width,
        height=height
    )

    # Show the plot
    fig.show()

    # Save the plot as an image
    output_filepath = bafs_filepath[:-9] + f"_ENDS0_scatterplot.png"
    fig.write_image(output_filepath, width=width, height=height)


if __name__ == "__main__":
    req_size, bafs_filepath, sorted_bafs_per_EDNS_buf = preprocess_data()
    draw_scatterplot(req_size, bafs_filepath, sorted_bafs_per_EDNS_buf)
