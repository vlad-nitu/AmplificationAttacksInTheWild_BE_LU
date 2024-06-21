import plotly.graph_objects as go
import plotly.express as px
from visualiser_Version_meanBAF_fpdns_base import preprocess_data

SYMBOLS = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'pentagon', 'hexagon', 'star', 'star-square'
]
COLORS = px.colors.qualitative.Plotly

width = 1600
height = 1024

def draw_scatterplot(versions, baf_values_list, input_filepath) -> None:
    """
    Draws scatterplot
    :param versions: list of DNS versions
    :param baf_values_list: list of BAF values
    :param input_filepath: path to JSON input file
    :return: None
    """
    # Create a scatter plot
    fig = go.Figure()

    for idx, (version, baf_values) in enumerate(zip(versions, baf_values_list)):
        fig.add_trace(go.Scatter(
            x=[version] * len(baf_values),
            y=baf_values,
            mode='markers',
            marker=dict(symbol=SYMBOLS[idx % len(SYMBOLS)], color=COLORS[idx % len(COLORS)], size=20),
            name=version
        ))

    # Update layout
    fig.update_layout(
        xaxis_title='DNS Version (IP Count)',
        yaxis_title='BAF',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(versions))),
            ticktext=[f"{version}<br>({len(baf_values)})" for (version, baf_values) in zip(versions, baf_values_list)],
            title=dict(font=dict(size=30)), # Title font size
            tickfont=dict(size=13), # Ticks font size
            title_standoff=15
        ),
        yaxis=dict(
            title=dict(font=dict(size=28)), # Title font size
            tickfont=dict(size=24) # Ticks font size
        ),
        legend=dict(font=dict(size=10), x=0.99, y=0.99, xanchor='right', yanchor='top'),
        width=width,
        height=height
    )

    # Show the plot
    fig.show()

    # Save the plot as an image
    output_filepath = input_filepath[:-5] + "_scatterplot.png"
    # Make sure to install kaleido: pip install -U kaleido
    fig.write_image(output_filepath, width=width, height=height)


if __name__ == "__main__":
    versions, baf_values_list, input_filepath = preprocess_data()
    draw_scatterplot(versions, baf_values_list, input_filepath)

