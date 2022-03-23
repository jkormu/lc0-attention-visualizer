import dash
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from global_data import global_data

from svg_pieces import get_svg_board
from dash import dcc, html, Input, Output, State
from server import app

from utils import callback_triggered_by


def heatmap_data(head):
    import random
    data = [[random.random() for i in range(8)] for j in range(8)]  #
    data = global_data.get_head_data(head)
    return data


def get_pieces():
    board = global_data.board.__str__()
    board = [c for c in board[::-1] if c != ' ' and c != '\n']
    return board


# def add_focused_square_highlight(fig):
#    ind = global_data.focused_square_ind
#    row = ind // 8
#    col = ind % 8
#    fig.add_shape(type="rect",
#                  x0=-0.5 + col, y0=-0.5 + row, x1=0.5 + col, y1=0.5 + row,
#                  line=dict(
#                      color="Red",
#                      width=3,
#                  ),
#                  row='all',
#                  col='all',
#                  )
#    return fig

def heatmap_figure():
    import time
    start = time.time()
    fig = make_figure()
    print('make fig:', time.time() - start)

    start = time.time()
    fig = add_heatmap_traces(fig)
    print('add traces:', time.time() - start)

    start = time.time()
    fig = add_layout(fig)
    print('add layout:', time.time() - start)

    start = time.time()
    fig = add_pieces(fig)
    print('add pieces:', time.time() - start)
    return fig


def heatmap():
    fig = heatmap_figure()

    graph_component = html.Div(style={'height': '100%', 'width': '100%',  # "overflow": "auto"
                                      })

    config = {  # 'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale']}

    graph_component.children = [dcc.Graph(figure=fig, id='graph', style={'height': '100%', 'width': '100%'},
                                          responsive=True,
                                          config=config
                                          )]

    return graph_component


def make_figure():
    titles = [f"Head {i + 1}" for i in range(global_data.number_of_heads)]
    fig = make_subplots(rows=global_data.subplot_rows, cols=global_data.subplot_cols, subplot_titles=titles,
                        horizontal_spacing=0.1 / global_data.subplot_cols,
                        vertical_spacing=0.25 / global_data.subplot_rows,
                        )
    # fig.update_layout(
    #    autosize=True
    #    )
    # fig.update_yaxes(automargin=True)
    # fig.update_xaxes(automargin=True)
    return fig


def add_layout(fig):
    layout = go.Layout(
        # title='Plot title goes here',
        margin={'t': 30, 'b': 0, 'r': 0, 'l': 0},
        plot_bgcolor='rgb(0,0,0)'
    )

    fig['layout'].update(layout)

    fig.update_xaxes(title=None, range=[-0.5, 7.5],
                     zeroline=False,
                     showgrid=False,
                     scaleanchor='y',
                     constrain='domain',
                     # constraintoward='right',
                     ticktext=[letter for letter in 'abcdefgh'],
                     tickvals=[0, 1, 2, 3, 4, 5, 6, 7])
    fig.update_yaxes(title=None,
                     range=[-0.5, 7.5],
                     zeroline=False,
                     showgrid=False,
                     scaleanchor='x',
                     constrain='domain',
                     constraintoward='top',
                     ticktext=[letter for letter in '12345678'],
                     tickvals=[0, 1, 2, 3, 4, 5, 6, 7])
    return fig


def add_heatmap_trace(fig, row, col):
    head = (row - 1) * global_data.subplot_cols + (col - 1)
    data = heatmap_data(head)
    trace = go.Heatmap(
        z=data,
        colorscale='Viridis',
        showscale=False,
        xgap=2,
        ygap=2,
        hovertemplate='<b>%{x}%{y}</b>: <b>%{z}</b><extra></extra>'
    )
    fig.add_trace(trace, row=row, col=col)
    return fig


def add_heatmap_traces(fig):
    for row in range(global_data.subplot_rows):
        for col in range(global_data.subplot_cols):
            fig = add_heatmap_trace(fig, row + 1, col + 1)
    return fig


def add_pieces(fig):
    board_svg = get_svg_board(global_data.board, global_data.focused_square_ind)
    fig.add_layout_image(
        dict(
            source=board_svg,
            xref="x",
            yref="y",
            x=3.5,
            y=3.5,
            sizex=8,
            sizey=8,
            xanchor='center',
            yanchor='middle',
            sizing="stretch",
        ),
        row='all',
        col='all',
    )
    return fig


@app.callback(Output('graph', 'figure'),
              [Input('graph', 'clickData'),
               Input('mode-selector', 'value'),
               Input('fen-text', 'children')
               ])
def update_heatmaps(click_data, mode, *args):
    fig = dash.no_update
    trigger = callback_triggered_by()
    global_data.visualization_mode = mode
    print('MODE', mode)
    if trigger == 'graph.clickData' and not click_data:
        return dash.no_update

    if trigger == 'graph.clickData':
        point = click_data['points'][0]
        x = point['x']
        y = point['y']
        square_ind = 8 * y + x
        if square_ind != global_data.focused_square_ind:
            global_data.focused_square_ind = square_ind
            fig = heatmap_figure()

    if trigger == 'fen-text.children':
        fig = heatmap_figure()

    if trigger == 'mode-selector.value':
        fig = heatmap_figure()

    return fig
