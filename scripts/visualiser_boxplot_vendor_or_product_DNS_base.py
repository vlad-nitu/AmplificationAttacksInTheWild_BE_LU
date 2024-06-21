import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

root_fingerprinting_path = '../data/censys_all_data/dns_fingerprinting/dns_8k_wild_product_vendor_fingerprinting_preprocessed.json'
root_baf_path = '../data/censys_all_data/dns_8k_IPs_domain_ip:._baf.json'

width = 1600
height = 1200


def preprocess_data(factor, ip_count_threshold):
    consider_non_responsive_servers_prompt = input(
        "Would you like to consider non-responsive servers in your statistics"
        " to understand if a vendor is secure or not?\n"
        "Options: YES or NO\n")

    consider_non_responsive_servers = True if consider_non_responsive_servers_prompt == "YES" else False

    # Load the JSON files
    dns_data = pd.read_json(root_fingerprinting_path)
    baf_data = pd.read_json(root_baf_path)

    # Rename columns for clarity
    baf_data.columns = ['ip', 'baf']

    # Fill missing BAF values with 0
    if consider_non_responsive_servers:
        # Merge data on IP addresses with a left join
        merged_data = pd.merge(dns_data, baf_data, on='ip', how='left')

        merged_data['baf'].fillna(0, inplace=True)

        # Ensure the BAF column is of integer type (optional, depending on your data needs)
        merged_data['baf'] = merged_data['baf'].astype(int)
    else:
        merged_data = pd.merge(dns_data, baf_data, on='ip')

    # Filter out rows where 'product' is null
    filtered_data = merged_data.dropna(subset=[factor])

    # Calculate the mean BAF for each product and sort them
    factor_means = filtered_data.groupby(factor)['baf'].mean().sort_values(ascending=False)

    # Create a list of box plots, one for each product, sorted by mean BAF
    box_plots = []
    for cur_factor in factor_means.index:
        product_data = filtered_data[filtered_data[factor] == cur_factor]
        ip_count = len(product_data)
        if ip_count >= ip_count_threshold:  # Only include products with IP count >= 6; TODO: Check if OK
            box_plots.append(go.Box(
                y=product_data['baf'],
                name=f"{cur_factor} ({ip_count})",
                boxmean=True  # Display the mean
            ))

    return box_plots


def draw_boxplot(factor, box_plots) -> None:
    # Layout configuration
    layout = go.Layout(

        yaxis=dict(
            title=dict(text='BAF (Bandwidth Amplification Factor)', font=dict(size=30)),  # Title font size
            tickfont=dict(size=26)  # Ticks font size
        ),

        xaxis=dict(
            title=dict(text=f'{factor.capitalize()} (IP Count)', font=dict(size=30)),  # Title font size
            tickfont=dict(size=26),  # Ticks font size
            title_standoff=50  # Add spacing between the title and the x-axis ticks
        ),
        legend=dict(
            font=dict(
                size=18,
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

    # Create the figure and add the box plots
    fig = go.Figure(data=box_plots, layout=layout)
    # Show the plot
    pio.show(fig)
    # Save the plot as an image
    output_filepath = root_fingerprinting_path[:-5] + f"_{factor}_boxplot.png"
    fig.write_image(output_filepath, width=width, height=height)
