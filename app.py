# -*- coding: utf-8 -*-
import dash

from server import app
from dash import dcc, html, Input, Output
from activation_heatmap import heatmap
from fen_input import fen_component
from controls import mode_selector, layer_selector, model_selector, head_selector, colorscale_selector
from position_pane import position_pane
from global_data import global_data

from constants import LEFT_PANE_WIDTH, RIGHT_PANE_WIDTH, GRAPH_PANE_HEIGHT, HEADER_HEIGHT, CONTENT_HEIGHT

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
#LEFT_PANE_WIDTH = 90
#RIGHT_PANE_WIDTH = 100 - LEFT_PANE_WIDTH
#GRAPH_PANE_HEIGHT = 100
#HEADER_HEIGHT = 10
#CONTENT_HEIGHT = 100 - HEADER_HEIGHT

# config_component = config_table()
# graph_component = tree_graph()

screen_width = html.Div(id='screen-size', children='1')
url = dcc.Location(id="url")
heatmap_size = html.Div(id='heatmap-size', children='1')
interval = dcc.Interval(id='updater', interval=5000)
hidden_info = html.Div(id='hidden-info', children=[screen_width, url, heatmap_size, interval], hidden=True)

left_container = html.Div(
    style={'height': '100%', 'width': f'{LEFT_PANE_WIDTH}%', 'backgroundColor': LEFT_CONTAINER_BG}
)

graph_container = html.Div(
    style={'height': f'{GRAPH_PANE_HEIGHT}%', 'width': '100%', 'backgroundColor': GRAPH_CONTAINER_BG,
           # 'position': 'relative',
           }
)
# html.Div(children=['GRAPH'])
# position_component = html.Div(children=['BOARD'])

graph_container.children = [heatmap()]

left_container.children = [graph_container]

right_container = html.Div(
    style={'height': '100%', 'width': f'{RIGHT_PANE_WIDTH}%', 'backgroundColor': RIGHT_CONTAINER_BG,
           'paddingLeft': 5, 'paddingRight': 5, 'paddingTop': 5,  'boxSizing': 'border-box',
           # 'display': 'flex', #'flexDirection': 'column'
           }
)

right_container.children = [position_pane()]

header_container = html.Div(children=[
    # fen_component(),
    mode_selector(),
    layer_selector(),
    model_selector(),
    head_selector(),
    colorscale_selector()
    #html.Button(id='test-button', children='TEST', n_clicks=1)
],
    className='header-container',
    style={'height': f'{HEADER_HEIGHT}%', 'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
           'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end',
            'paddingTop': '5px', 'paddingBottom': '5px'
           }
    #style = {'height': f'100px', 'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
    #     'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end',
    #         #'paddingTop': '5px', 'paddingBottom': '5px'
    #     }
)

top_container = html.Div(children=[
    left_container,
    right_container,
    # left_container,
],
    style={'height': f'{CONTENT_HEIGHT}%', 'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
           'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end',
           # 'overflow': 'auto',
           }
#style = {'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
#         'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end',
#         # 'overflow': 'auto',
#         }
)

# bottom_container = html.Div(children=[
# ],
#    style={'height': '40%', 'width': '100%', 'backgroundColor': APP_CONTAINER_BG,
#           'display': 'flex', 'flexDirection': 'row', 'alignItems:': 'flex-end', 'overflow': 'auto'})

recalculate_graph = html.Div(id='recalculate-graph-indicator', hidden=True)

layout = html.Div(children=[header_container,
                            top_container,
                            recalculate_graph,
                            # bottom_container,
                            # left_container,
                            hidden_info
                            ],
                  style={'height': '100vh', 'width': '100vw', 'backgroundColor': APP_CONTAINER_BG,
                         'display': 'flex', 'flexDirection': 'column', 'alignItems:': 'flex-end',
                         # 'overflow': 'auto',
                         })

app.layout = layout

app.clientside_callback(
    """
    function(href) {
        var w = window.innerWidth;
        var h = window.innerHeight; 
        console.log(w, h)
        return [w, h];
    }
    """,
    Output('screen-size', 'children'),
    Input('url', 'href'),
    prevent_initial_call=True
)
#var el = document.querySelectorAll("rect.nsewdrag")
app.clientside_callback(
    """
    function(n_intervals) {
        if (typeof window.HMoldWidth == 'undefined') {
            window.HMoldWidth = 0;
            window.HMoldHeight = 0;
        }
        var el = document.querySelector("rect.nsewdrag")//document.getElementsByTagName("div")
        var w = el.getAttribute('width');
        var h = el.getAttribute('height');
        console.log(w, h, window.HMoldWidth, window.MHoldHeight);
        if (w == window.HMoldWidth && h == window.HMoldHeight) {
            return window.dash_clientside.no_update
        }
        window.HMoldWidth = w;
        window.HMoldHeight = h;
        //window.dash_clientside.no_update
        console.log(w, h)
        return [w, h];
    }
    """,
    Output('heatmap-size', 'children'),
    Input('updater', 'n_intervals'),
    prevent_initial_call=True
)

#document.querySelectorAll("rect.nsewdrag")


@app.callback(Output('screen-size', 'hidden'),
              Input('screen-size', 'children')
              )
def update_screen_size(size):
    w, h = size
    #print('TYETETETETEU', global_data.screen_w)
    global_data.set_screen_size(w, h)
    print('>>>>>: WIDTH', size[0])
    print('>>>>>: HEIGHT', size[1])
    return dash.no_update


@app.callback(Output('heatmap-size', 'hidden'),
              Input('heatmap-size', 'children')
              )
def heatmap_size(size):
    if size != '1':
        print('-----------------------HEATMAP SIZE',size)
        #w, h = size
        #print('TYETETETETEU', global_data.screen_w)
        #global_data.set_screen_size(w, h)
        print('>>>>>: HEATMAP WIDTH', size[0])
        print('>>>>>: HEATMAP HEIGHT', size[1])
    return dash.no_update