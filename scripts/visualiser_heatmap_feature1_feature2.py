import pandas as pd
import json
import plotly.express as px

width = 2300
height = 1280

# Just for bookkeeping purposes 
baf_path = '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json'  # Main file
edns0_buffer_size_path = '../data/censys_all_data/dns_8k_IPs_max_udp.json'
dns_version_path = '../data/censys_all_data/dns_8k_ips_fpdns.json'
vendor_path = '../data/censys_all_data/dns_fingerprinting/dns_8k_wild_product_vendor_fingerprinting_preprocessed.json'
product_path = '../data/censys_all_data/dns_fingerprinting/dns_8k_wild_product_vendor_fingerprinting_preprocessed.json'
asns_path = '../data/censys_all_data/dns_8k_ASNs.json'

# Define the sequential palette, with 0 values as white
color_scale_white_sequential_palette = [ # Tips: https://vwo.com/blog/heatmap-colors/
    [0, "white"],
    [0.00001, "#d4efdf"],  # Light green
    [0.2, "#a9dfbf"],      # Lighter green
    [0.4, "#7dcea0"],      # Medium green
    [0.6, "#52be80"],      # Darker green
    [0.8, "#27ae60"],      # Even darker green
    [1, "#1e8449"]         # Darkest green
]

# Mapping of DNS version names to their shortcuts
version_shortcuts = {
    'ISC BIND 9.2.3 -- 9.2.9 [New Rules]': 'IB92',
    'ISC BIND 9.2.3rc1 -- 9.4.0a4 [Old Rules]': 'IB92r',
    'ISC BIND 9.6.3 -- 9.7.3 [New Rules]': 'IB96',
    'Meilof Veeningen Posadis  [Old Rules]': 'MV',
    'Microsoft Windows DNS 2000 [New Rules]': 'MD2K',
    'Raiden DNSD  [Old Rules]': 'RD',
    'Simon Kelley dnsmasq  [Old Rules]': 'SK',
    'Unlogic Eagle DNS 1.0 -- 1.0.1 [New Rules]': 'UE10',
    'Unlogic Eagle DNS 1.1.1 [New Rules]': 'UE11'
}

def filter_by_group_size(df, group_column='BAF', min_size=5):
    """
    :param df: The input DataFrame.
    :param group_column: The column to group by.
    :param min_size: The minimum size of groups to store.
    :return: The filtered DataFrame.
    """
    group_counts = df[group_column].value_counts()
    valid_groups = group_counts[group_counts > min_size].index
    return df[df[group_column].isin(valid_groups)]

def sorted_dict(dct): # By values for edns0_Buffer_size
    """
    Sorts a dictionary based on the EDNS0 Buffer Size (value[1])
    :param dct: input dict
    :return: sorted input dict
    """
    return dict(sorted(dct.items(), key=lambda item: item[1]))

def preprocess_feature(feature_filepath, feature="baf"):
    """
    Loads the JSON file provided by the user, and preprocesses the data in
    DataFrame format
    :param feature_filepath: file path of the file that contains features
    :param feature:  baf or percentage
    :return: preprocessed input in DataFrame format
    """

    with open(feature_filepath, 'r') as f:
        data = json.load(f)

    if feature == 'baf':
        # Convert the JSON data into a DataFrame
        bafs_list = [{"IP": entry[0], "BAF": entry[1]} for entry in data]
        df = pd.DataFrame(bafs_list)
        df_filtered = df

    elif feature == 'edns0_buffer_size':
        # Convert the JSON data into a list of dictionaries
        buffers_list = [{"IP": ip, "edns0_buffer_size": str(size)} for entry in data for ip, size in sorted_dict(entry).items()]
        buffers_list  = sorted(buffers_list, key=lambda x: x['edns0_buffer_size'])
        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(buffers_list) # Sort by edns0 buffer size
        # Sort the DataFrame by 'edns0_buffer_size'
        df = df[df['edns0_buffer_size'] != 'None']
        # Convert 'edns0_buffer_size' back to integer for sorting in DataFrame
        df['edns0_buffer_size'] = df['edns0_buffer_size']
        df_filtered = df.sort_values(by='edns0_buffer_size')

    elif feature == "asn":
        # Convert the JSON data into a DataFrame with selected columns
        df = pd.DataFrame(data, columns=['ip', 'asn'])
        # Rename the columns to match the desired output
        df.rename(columns={'ip': 'IP', 'asn': 'asn'}, inplace=True)
        df_filtered = df

    elif feature == 'product':
        # Convert the JSON data into a DataFrame with selected columns
        df = pd.DataFrame(data, columns=['ip', 'product'])
        # Rename the columns to match the desired output
        df.rename(columns={'ip': 'IP', 'product': 'product'}, inplace=True)
        df_filtered = df

    elif feature == 'vendor':
        # Convert the JSON data into a DataFrame with selected columns
        df = pd.DataFrame(data, columns=['ip', 'vendor'])
        # Rename the columns to match the desired output
        df.rename(columns={'ip': 'IP', 'vendor': 'vendor'}, inplace=True)
        df_filtered = df

    elif feature == 'dns_version':
        # Prepare a list to store the (IP, Version) tuples
        rows = []
        # Iterate through the JSON data to extract the required information
        for version, values in data.items():
            ips = values[2]  # Get the dictionary of IPs and values
            for ip in ips.keys():
                rows.append({'IP': ip, 'dns_version': version_shortcuts.get(version, version)})
        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(rows, columns=['IP', 'dns_version'])
        df_filtered = df[(df['dns_version'] != 'TIMEOUT') & (df['dns_version'] != 'No match found')]

        print(df_filtered['dns_version'].unique())

    else: #  unknown feature
        raise ValueError(f'Feature {feature} not supported')

    return df_filtered

def top_10_percent_mean(series):
    """
    Strategy to filter out top 10% of the Series, where `top` is defined as most-vulnerable amplifiers (largest BAF)
    :param series: data in Series format
    :return: filtered Series
    """
    top_10_percent = series.quantile(0.9)
    return series[series >= top_10_percent].mean()

def intersect_dfs(df1, df2, df_baf, feature1, feature2):
    """
    Helper method that intersects 3 DataFrames: df1, df2 and df_baf using Inner Join
    :param df1: DataFrame from file1
    :param df2: DataFrame from file2
    :param df_baf: DataFrame that stores BAF statistics
    :param feature1:
    :param feature2:
    :return: (percentages_df, baf_df, merged_df)
    """
    merged_df = pd.merge(df1, df2, on='IP')
    merged_df = pd.merge(merged_df, df_baf, on='IP')

    merged_df = filter_by_group_size(merged_df, feature1)
    merged_df = filter_by_group_size(merged_df, feature2)

    matrix_df = merged_df.groupby([feature1, feature2]).size().unstack(fill_value=0)
    percentages_df = matrix_df.div(matrix_df.sum(axis=0), axis=1) * 100
    baf_df = merged_df.groupby([feature1, feature2])['BAF'].median().unstack(fill_value=0) # Median

    return percentages_df, baf_df, merged_df

def plot_heat_map(percentages_df, baf_df, merged_df, feature1, feature2) -> None:
    """
    Creates the HeatMap that combines BAF and IP percentages in each cell
    :param percentages_df:
    :param baf_df:
    :param merged_df:
    :param feature1:
    :param feature2:
    :return: None
    """

    # Ensure the index is of type object if needed
    baf_df.index = baf_df.index.astype(object)
    baf_df.columns = baf_df.columns.astype(object)

    # Sort the DataFrame by its index in ascending order
    baf_df = baf_df.sort_index(ascending=True)

    # Create a text DataFrame for displaying BAF and percentages
    text_df = baf_df.copy().astype(str)
    for row in text_df.index:
        for col in text_df.columns:
            baf_value = baf_df.loc[row, col]
            percentage_value = percentages_df.loc[row, col]
            text_df.loc[row, col] = f"{baf_value:.2f}<br>{percentage_value:.2f}%"

    fig = px.imshow(baf_df,
                    labels=dict(x=feature2, y=feature1, color="BAF"),
                    x=baf_df.columns,
                    y=baf_df.index,
                    text_auto=True,
                    color_continuous_scale=color_scale_white_sequential_palette)

    # Modify the text to be displayed as baf_value<br>ip_count and wrap text
    fig.update_traces(
        text=text_df.values,
        texttemplate="%{text}",
        textfont=dict(size=40)
    )

    fig.update_layout(
        xaxis_title=feature2,
        yaxis_title=feature1,
        height=height,
        width=width,
        font=dict(size=40),
        coloraxis_showscale=True,  # Show color bar
        coloraxis_colorbar=dict(
            orientation='h',
            title=dict(font=dict(size=60), side='top'),  # Title font size of color bar
            tickfont=dict(size=60),  # Ticks font size of color bar
            x=5,  # Center the color bar horizontally
            xanchor='center',
            y=-2,  # Position the color bar below the plot
            yanchor='top'
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(baf_df.columns))),
            ticktext=[f"{version_shortcuts.get(col, col)}" for col in baf_df.columns],  # Use shortcuts for x-axis labels
            title=dict(font=dict(size=36)),  # Title font size
            tickfont=dict(size=40),  # Ticks font size
            # tickangle=0,  # Prevent diagonal labels
            title_standoff=50  # Add spacing between the title and the x-axis ticks
        )
    )

    # Add count annotations on the x-axis (e.g. for each version)
    x_counts = merged_df[feature2].value_counts().sort_index()
    for i, col in enumerate(x_counts.index):
        count = x_counts[col]
        fig.add_annotation(dict(
            font=dict(color="black", size=34),
            x=i,
            y=len(baf_df),
            showarrow=False,
            text=str(count),
            xanchor='center',
            yanchor='bottom',
            xref="x",
            yref="y"
        ))

    # Add count annotations on the y-axis (e.g. for each buffer size)
    y_counts = merged_df[feature1].value_counts().sort_index()
    for i, row in enumerate(y_counts.index):
        count = y_counts[row]
        fig.add_annotation(dict(
            font=dict(color="black", size=34),
            x=-0.5,
            y=i,
            showarrow=False,
            text=str(count),
            xanchor='right',
            yanchor='middle',
            xref="x",
            yref="y"
        ))

    fig.show()
    fig.write_image(f'../data/censys_all_data/heatmap_correlation_{feature1}_vs_{feature2}_combined.png', width=width, height=height)


if __name__ == "__main__":
    feature1 = input("Please input which 1st feature you are interested in obtaining the statistics for\n"
                     "Options: dns_version, vendor, product, edns0_buffer_size or asn\n"
                     "This is the variable on OY (vertical) axis\n")
    feature1_filepath = input("Please input the file path to the statistics for feature 1\n")
    feature2 = input("Please input which 2nd feature you are interested in obtaining the statistics for\n"
                     "Options: dns_version, vendor, product, edns0_buffer_size or asn\n"
                     "This is the variable on OX (horizontal) axis\n")
    feature2_filepath = input("Please input the file path to the statistics for feature 2\n")
    baf_filepath = '../data/censys_all_data/dns_8k_IPs_domain_ip:._dns_query_type:ANY_max_udp_size:True_baf.json' 

    df_baf = preprocess_feature(baf_filepath)
    df1 = preprocess_feature(feature1_filepath, feature1)
    df2 = preprocess_feature(feature2_filepath, feature2)
    percentages_df, baf_df, merged_df = intersect_dfs(df1, df2, df_baf, feature1, feature2)
    plot_heat_map(percentages_df, baf_df, merged_df, feature1, feature2)
