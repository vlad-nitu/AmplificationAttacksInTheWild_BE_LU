import pandas as pd
import json
import plotly.express as px

# Define the file paths
file_paths = {
    'sl': '../data/censys_all_data/sl/dns_8k_IPs_domain_ip:sl._dns_query_type:ANY_max_udp_size:False_baf.json',
    'bg': '../data/censys_all_data/bg/dns_8k_IPs_domain_ip:bg._dns_query_type:ANY_max_udp_size:True_baf.json',
    'root': '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json'
}

width = 1600
height = 1024

# Initialize an empty DataFrame
combined_df = pd.DataFrame(columns=['ip', 'baf', 'type'])

# Load each file and add the type column
for key, path in file_paths.items():
    with open(path, 'r') as f:
        data = json.load(f)
        df = pd.DataFrame(data, columns=['ip', 'baf'])
        df['type'] = key
        combined_df = pd.concat([combined_df, df])

# Define a color map for the three categories
color_map = {
    'sl': 'rgba(31, 119, 180, 0.7)',  # Blue with some transparency
    'bg': 'rgba(255, 127, 14, 0.7)',  # Orange with some transparency
    'root': 'rgba(44, 160, 44, 0.7)'  # Green with some transparency
}

# Plotting the histogram
fig = px.histogram(
    combined_df,
    x='baf',
    color='type',
    barmode='group',  # Grouped bars
    labels={'baf': 'BAF (Bandwidth Amplification Factor)', 'type': 'Domain Type'},
    nbins=25,  # You can adjust the number of bins as needed
    color_discrete_map=color_map
)

fig.update_layout(
    xaxis_title='BAF (Bandwidth Amplification Factor)',
    yaxis_title='IPs (Frequency)',
    legend_title_text='Domain Type',

    xaxis=dict(
        title=dict(font=dict(size=48)), # Title font size
        tickfont=dict(size=44), # Ticks font size
        title_standoff=20
    ),
    yaxis=dict(
        title=dict(font=dict(size=48)), # Title font size
        tickfont=dict(size=44) # Ticks font size
    ),
    legend=dict(
        font=dict(
            size=54,
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
output_filepath = '../data/censys_all_data/multiple_variables'
for domain in file_paths.keys():
    output_filepath += f"_{domain}"
output_filepath += f"_hist.png"
fig.write_image(output_filepath, width=width, height=height)
