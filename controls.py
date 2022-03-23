from dash import dcc, html, Input, Output, State
from server import app


def mode_selector():
    mode_selector_container = html.Div(className='header-control-container')
    label = html.Label(html.B('Mode'), className='header-label')
    selector = dcc.RadioItems(
        options=[
            {'label': 'Row', 'value': 'ROW'},
            {'label': 'Column', 'value': 'COL'},
        ],
        value='ROW',
        style={'display': 'flex', 'flexDirection': 'column'},#, 'alignItems:': 'flex-end'}
        id='mode-selector'
    )
    mode_selector_container.children = [label, selector]
    return mode_selector_container

def layer_selector():
    layer_selector_container = html.Div(className='header-control-container')#style={'marginRight': '5px', 'marginLeft': '5px'},
    label = html.Label(html.B('Layer'), className='header-label')
    selector = dcc.Dropdown(
        options=[
            {'label': 'Dummy head1', 'value': 1},
            {'label': 'Dummy head2', 'value': -1},
        ],
        value=-1,
        clearable=False,
        style={'width': '200px'}
    )
    layer_selector_container.children = [label, selector]
    return layer_selector_container