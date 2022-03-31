from dash import dcc, html, Input, Output, State
from server import app
from global_data import global_data

def mode_selector():
    mode_selector_container = html.Div(className='header-control-container')
    label = html.Label(html.B('Mode'), className='header-label')
    selector = dcc.RadioItems(
        options=[
            {'label': '8x8 Row', 'value': 'ROW'},
            {'label': '8x8 Column', 'value': 'COL'},
            {'label': '64x64', 'value': '64x64'}
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

    layers = len(global_data.activations_data)
    dropdown_options = get_layer_options()
    selector = dcc.Dropdown(
        options=dropdown_options,#[
            #{'label': 'layer 1', 'value': 0},
            #{'label': 'layer 2', 'value': 1},
        #],
        value=0,
        clearable=False,
        style={'width': '200px'},
        id='layer-selector'
    )
    layer_selector_container.children = [label, selector]
    return layer_selector_container

def get_layer_options():
    #layers = len([layer for layer in global_data.activations_data if layer.shape[-1] == 64 and layer.shape[-2] == 64])
    dropdown_options = [{'label': f'layer {layer + 1}', 'value': layer} for layer in range(global_data.nr_of_layers_in_body)]
    return dropdown_options