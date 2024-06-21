import pandas as pd
import json
import plotly.express as px

auth_path_ANY = '../data/pagerank/dns_ANY_wild_baf.json'
non_auth_path_root_ANY  = '../data/censys_all_data/dns_8k_IPs_domain_ip:._baf.json'

non_auth_path_sl_ANY  = '../data/censys_all_data/sl/dns_8k_IPs_domain_ip:sl._dns_query_type:ANY_max_udp_size:False_baf.json'
non_auth_path_ve_ANY  = '../data/censys_all_data/ve/dns_8k_IPs_domain_ip:ve._dns_query_type:ANY_max_udp_size:False_baf.json'

auth_path = auth_path_ANY
non_auth_path  = non_auth_path_root_ANY # Change as needed

width = 1024
height = 750

# Load the authoritative servers file
with open(auth_path, 'r') as f:
    auth_data = json.load(f)

# Aggregate the authoritative servers by their IP address and take the maximum BAF
auth_df = pd.DataFrame([(entry[0][0], entry[1]) for entry in auth_data], columns=['ip', 'baf'])
auth_agg = auth_df.groupby('ip')['baf'].max().reset_index()

# Load the second file
with open(non_auth_path, 'r') as f:
    non_auth_data = json.load(f)

# Convert the second file data into a DataFrame
non_auth_df = pd.DataFrame(non_auth_data, columns=['ip', 'baf'])

# Remove the authoritative IPs from the second array
non_auth_filtered = non_auth_df[~non_auth_df['ip'].isin(auth_agg['ip'])]

# Add a 'type' column to both DataFrames for categorization
auth_agg['type'] = 'Authoritative'
non_auth_filtered['type'] = 'Non Authoritative'

# Combine both DataFrames
combined_df = pd.concat([non_auth_filtered, auth_agg])

# Define a color map for better contrast
color_map = {
    'Non Authoritative': 'green',
    'Authoritative': 'blue',  
}

# Plotting the histogram
fig = px.histogram(combined_df, x='baf', color='type', 
                   labels={'baf': 'BAF (Bandwidth Amplification Factor)', 'type': 'DNS Server Type'},
                   nbins=20, color_discrete_map=color_map)

fig.update_layout(
    xaxis_title='BAF (Bandwidth Amplification Factor)',
    yaxis_title='IPs (Frequency)',
    legend_title_text='Server Type',
    xaxis=dict(
        title=dict(font=dict(size=36)), # Title font size
        tickfont=dict(size=32), # Ticks font size
        title_standoff=20
    ),
    yaxis=dict(
        title=dict(font=dict(size=36)), # Title font size
        tickfont=dict(size=32) # Ticks font size
    ),
    legend=dict(
        font=dict(
            size=50,
        ),
        itemsizing='constant',
        x=0.99,  # X position of the legend
        y=0.99,  # Y position of the legend
        xanchor='right',
        yanchor='top',
    ),
    barmode='group', # Put barplots side by side, instead of overlapped.
    width=width,
    height=height
)

fig.show()

output_filepath = non_auth_path[:-5] + f"_auth_vs_non_auth_hist.png"
fig.write_image(output_filepath, width=width, height=height)
