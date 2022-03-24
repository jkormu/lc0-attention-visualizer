# -*- coding: utf-8 -*-
from server import app
from dash import dcc, html
from activation_heatmap import heatmap
from fen_input import fen_component
from controls import mode_selector, layer_selector

DEBUG = False

if DEBUG:
    APP_CONTAINER_BG = 'rgba(116, 153, 46, 0.2)'  # ugly green
    LEFT_CONTAINER_BG = 'rgba(46, 148, 153, 0.2)'  # teal
    RIGHT_CONTAINER_BG = 'rgba(212, 57, 181, 0.2)'  # pink
    GRAPH_CONTAINER_BG = 'rgba(212, 163, 57, 0.7)'  # orange-brown
    CONFIG_CONTAINER_BG = 'rgba(57, 106, 212, 0.2)'  # blue
else:
    WHITE = 'rgb(255, 255, 255)'
    APP_CONTAINER_BG = WHITE
    LEFT_CONTAINER_BG = WHITE
    RIGHT_CONTAINER_BG = WHITE
    GRAPH_CONTAINER_BG = WHITE
    CONFIG_CONTAINER_BG = WHITE
LEFT_PANE_WIDTH = 100
RIGHT_PANE_WIDTH = 100 - LEFT_PANE_WIDTH
GRAPH_PANE_HEIGHT = 100

# config_component = config_table()
# graph_component = tree_graph()


left_container = html.Div(
    style={'height': '100%', 'width': f'{LEFT_PANE_WIDTH}%', 'backgroundColor': LEFT_CONTAINER_BG}
)

graph_container = html.Div(
    style={'height': f'{GRAPH_PANE_HEIGHT}%', 'width': '100%', 'backgroundColor': GRAPH_CONTAINER_BG,
           #'position': 'relative',
           }
)
# html.Div(children=['GRAPH'])
# position_component = html.Div(children=['BOARD'])

graph_container.children = [heatmap()]

left_container.children = [graph_container]

right_container = html.Div(
    style={'height': '100%', 'width': f'{RIGHT_PANE_WIDTH}%', 'backgroundColor': RIGHT_CONTAINER_BG,
           'paddingLeft': 5, 'boxSizing': 'border-box'
           }
)

right_container.children = []

header_container = html.Div(children=[
    fen_component(),
    mode_selector(),
    layer_selector(),
],
    className='header-container',
    style={'height': '10%', 'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
           'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end',
})

top_container = html.Div(children=[
    left_container,
    #right_container,
    # left_container,
],
    style={'height': '90%', 'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
           'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end', 'overflow': 'auto'})

#bottom_container = html.Div(children=[
#],
#    style={'height': '40%', 'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
#           'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end', 'overflow': 'auto'})

layout = html.Div(children=[header_container,
                            top_container,
                            #bottom_container,
                            # left_container,
                            ],
                  style={'height': '100vh', 'width': '100vw', 'backgroundColor': APP_CONTAINER_BG,
                         'display': 'flex', 'flexDirection': 'column', 'alignItems:': 'flex-end', 'overflow': 'auto'})

app.layout = layout
