import plotly.graph_objects as go
from visualiser_Version_meanBAF_fpdns_base import preprocess_data

width = 1280
height = 1024

# Mapping of DNS version names to their shortcuts
version_shortcuts = {
    'ISC BIND 9.6.3': 'IB96',
    'ISC BIND 9.2.3': 'IB92',
    'Raiden DNSD': 'RD',
    'Meliof Veeningen': 'MV',
    'ISC BIND 9.2.3rc1': 'IB92r',
    'Simon Kelley': 'SK',
    'Mikrotik': 'MK',
    'No match': 'NM',
    'Microsoft DNS 2000': 'MD2K',
    'Unlogic Eagle 1.0': 'UE10',
    'Unlogic Eagle 1.1.1': 'UE11'
}

abbreviated_versions = [
    "ISC BIND 9.6.3", "ISC BIND 9.2.3", "Raiden DNSD", "Meliof Veeningen",
    "ISC BIND 9.2.3rc1", "Simon Kelley", "Mikrotik", "No match",
    "Microsoft DNS 2000", "Unlogic Eagle 1.0", "Unlogic Eagle 1.1.1"
]

def draw_boxplot(versions, baf_values_list, input_filepath) -> None:
    """
    Draws boxplot
    :param versions: list of DNS versions
    :param baf_values_list: list of BAF values
    :param input_filepath: path to JSON input file
    :return: None
    """
    
    # Create a box plot
    fig = go.Figure()
    for _, baf_values, abbrev_version in zip(versions, baf_values_list, abbreviated_versions):
        fig.add_trace(go.Box(
            y=baf_values,
            name=f"{version_shortcuts.get(abbrev_version, abbrev_version)}; {abbrev_version}",
            boxmean=True
        ))

    # Update layout
    fig.update_layout(
        xaxis_title='DNS Version (IP Count)',
        yaxis_title='BAF (Bandwidth Amplification Factor)',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(versions))),
            ticktext=[f"{version_shortcuts.get(abbrev_version, abbrev_version)}<br>({len(baf_values)})" for abbrev_version, baf_values in zip(abbreviated_versions, baf_values_list)],
            title=dict(font=dict(size=44)), # Title font size
            tickfont=dict(size=32), # Ticks font size
            title_standoff=20
        ),
        yaxis=dict(
            title=dict(font=dict(size=44)), # Title font size
            tickfont=dict(size=44) # Ticks font size
        ),
        legend=dict(
            font=dict(
                size=28,
            ),
            itemsizing='constant',
            x=0.99,  # X position of the legend
            y=0.99,  # Y position of the legend
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.3)' # 30% transparent
        )
    )
    # Show the plot
    fig.show()
    # Save the plot as an image
    output_filepath = input_filepath[:-5] + "_boxplot.png"
    # Make sure to install kaleido: pip install -U kaleido
    fig.write_image(output_filepath, width=width, height=height)


if __name__ == "__main__":
    versions, baf_values_list, input_filepath = preprocess_data()
    draw_boxplot(versions, baf_values_list, input_filepath)

