import pandas as pd
import json
import plotly.express as px

width = 1600
height = 1024

# Define the file path
file_path_buffers = '../data/censys_all_data/dns_8k_IPs_max_udp.json'


def preprocess_data():
    """
    Read user input, preprocess the data and return `buffer_size_counts`
    :return: Pandas DataFrame
    """
    # Load the JSON file
    with open(file_path_buffers, 'r') as f:
        buffers_data = json.load(f)

    # Convert the JSON data into a DataFrame
    buffers_list = [{"ip": ip, "edns0_buffer_size": size} for entry in buffers_data for ip, size in entry.items()]
    buffers_df = pd.DataFrame(buffers_list)

    # Calculate the distribution of IPs per EDNS0 buffer size category
    buffer_size_counts = buffers_df['edns0_buffer_size'].value_counts().reset_index()
    buffer_size_counts.columns = ['edns0_buffer_size', 'count']

    # Calculate the percentage of each buffer size
    total_count = buffer_size_counts['count'].sum()
    buffer_size_counts['percentage'] = (buffer_size_counts['count'] / total_count) * 100

    # Aggregate categories with less than 5% into "others"
    others_count = buffer_size_counts[buffer_size_counts['percentage'] < 5]['count'].sum()
    buffer_size_counts = buffer_size_counts[buffer_size_counts['percentage'] >= 5]

    # Create a DataFrame for the "others" category
    others_df = pd.DataFrame([{'edns0_buffer_size': 'Others', 'count': others_count}])

    # Concatenate the main DataFrame with the "others" category
    buffer_size_counts = pd.concat([buffer_size_counts, others_df], ignore_index=True)

    return buffer_size_counts


def draw_piechart(buffer_size_counts) -> None:
    """
    Draws piechart that shows IP / servers distribution per EDNS0 Buffer Size
    :param buffer_size_counts: input data after preprocessign step
    :return: None
    """
    fig = px.pie(
        buffer_size_counts,
        values='count',
        names='edns0_buffer_size',
        hole=0.3  # This creates a donut chart. Remove this line if you want a regular pie chart.
    )

    # Update the layout for better visualization
    fig.update_traces(textinfo='percent+label', textfont_size=50)
    fig.update_layout(
        title=dict(font=dict(size=24)),
        annotations=[dict(text='Buffer Size', x=0.5, y=0.5, font_size=50, showarrow=False)],
        legend=dict(
            font=dict(size=40),
            x=0.85,  # Adjust the x position
            y=0.5,  # Adjust the y position
            xanchor='center',
            yanchor='middle'
        )
    )

    # Show the plot
    fig.show()
    output_filepath = file_path_buffers[:-5] + "_EDNS0_Buffer_Size_IPs_piechart.png"
    fig.write_image(output_filepath, width=width, height=height)


if __name__ == "__main__":
    buffer_size_counts = preprocess_data()
    draw_piechart(buffer_size_counts)
