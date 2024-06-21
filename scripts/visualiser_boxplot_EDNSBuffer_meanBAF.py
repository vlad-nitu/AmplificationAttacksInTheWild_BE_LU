import plotly.express as px
import plotly.graph_objects as go

from visualiser_boxplot_EDNSBuffer_meanBAF_base import preprocess_data

root_path_baf = '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json'
root_path_max_udp = '../data/censys_all_data/dns_8k_IPs_domain_ip:._ANY_max_udp.json'

width = 1280
height = 1024

def draw_boxplot(req_size, bafs_filepath, sorted_bafs_per_EDNS_buf) -> None:
    """
    Draws boxplot
    :param req_size: Size of request, in order to compute threshold
    :param bafs_filepath: filepath of BAFs received as input, to name the output file using it
    :param sorted_bafs_per_EDNS_buf: dictionary that contains data we want to plot in a boxplot
    :return: None
    """
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, (EDNS_buf_size, bafs) in enumerate(sorted_bafs_per_EDNS_buf.items()):
        # Calculate the threshold
        threshold = EDNS_buf_size / req_size

        # Assign color for the buffer size
        color = colors[idx % len(colors)]


        exceeding_threshold = sum([1 for baf in bafs if baf >= threshold])
        print(f"For EDNS_buf_size: {EDNS_buf_size}, there are {exceeding_threshold}/{len(bafs)} that exceed the threshold")

        # Add box plot for BAF values
        fig.add_trace(go.Box(
            y=bafs,
            name=str(EDNS_buf_size),
            marker_color=color,
            boxmean=True
        ))

        # Add horizontal dash-dot line for threshold
        fig.add_shape(type="line",
                      x0=idx - 0.4, y0=threshold,
                      x1=idx + 0.4, y1=threshold,
                      xref='x', yref='y',
                      line=dict(color=color, width=3, dash="dashdot"))

        # Add annotation for the threshold line
        fig.add_annotation(
            x=idx,
            y=threshold,
            text=f'{threshold:.2f}',
            showarrow=False,
            yshift=10,
            font=dict(color=color, size=28)  # Increase the font size by setting the size attribute
        )

    # Update layout
    fig.update_layout(
        yaxis_title='BAF (Bandwidth Amplification Factor)',
        xaxis_title='EDNS0 Buffer Size (IP Count)',

        yaxis=dict(
            title=dict(font=dict(size=40)),  # Title font size
            tickfont=dict(size=44)  # Ticks font size
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(sorted_bafs_per_EDNS_buf))),
            ticktext=[f"{EDNS_buf_size}<br>({len(bafs)})" for EDNS_buf_size, bafs in sorted_bafs_per_EDNS_buf.items()],
            # tickangle=-45,  # Rotate the x-axis labels
            title=dict(font=dict(size=40)),  # Title font size
            tickfont=dict(size=32),  # Ticks font size
            title_standoff=20  # Add spacing between the title and the x-axis ticks
        ),
        legend=dict(
            font=dict(
                size=42,
            ),
            # itemsizing='constant',
            x=1,  # X position of the legend
            y=1.02,  # Y position of the legend
            xanchor='right',
            yanchor='bottom',
            # bgcolor='rgba(255, 255, 255, 0.5)',  # Semi-transparent background for the legend
            # bordercolor='rgba(255, 255, 255, 0.5)',  # Semi-transparent border for the legend
            orientation='h',  # Horizontal legend
        ),
        width=width,
        height=height
    )

    # Show the plot
    fig.show()
    # Save the plot as an image
    output_filepath = bafs_filepath[:-8] + f"_EDNS0_boxplot.png"
    fig.write_image(output_filepath, width=width, height=height)


if __name__ == "__main__":
    req_size, bafs_filepath, sorted_bafs_per_EDNS_buf = preprocess_data()
    draw_boxplot(req_size, bafs_filepath, sorted_bafs_per_EDNS_buf)
