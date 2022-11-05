import dash
from dash import dcc, html, Input, Output, State
from server import app
from global_data import global_data


def mode_selector():
    mode_selector_container = html.Div(className='header-control-container')
    label = html.Label(html.B('Mode'), className='header-label')
    selector = dcc.RadioItems(
        options=[
            {'label': "8x8 Row ('from' square)", 'value': 'ROW'},
            {'label': "8x8 Column ('to' square)", 'value': 'COL'},
            {'label': '64x64', 'value': '64x64'}
        ],
        value='ROW',
        style={'display': 'flex', 'flexDirection': 'column'},  # , 'alignItems:': 'flex-end'}
        id='mode-selector'
    )
    mode_selector_container.children = [label, selector]
    return mode_selector_container


def layer_selector():
    layer_selector_container = html.Div(
        className='header-control-container')  # style={'marginRight': '5px', 'marginLeft': '5px'},
    label = html.Label(html.B('Layer'), className='header-label')

    dropdown_options = get_layer_options()
    selector = dcc.Dropdown(
        options=dropdown_options,
        value=0,
        clearable=False,
        style={'width': '200px'},
        id='layer-selector'
    )
    layer_selector_container.children = [label, selector]
    return layer_selector_container


def get_layer_options():
    # layers = len([layer for layer in global_data.activations_data if layer.shape[-1] == 64 and layer.shape[-2] == 64])
    dropdown_options = [{'label': f'layer {layer + 1}', 'value': layer} for layer in
                        range(global_data.nr_of_layers_in_body)]
    return dropdown_options


def model_selector():
    model_selector_container = html.Div(
        className='header-control-container')  # style={'marginRight': '5px', 'marginLeft': '5px'},
    label = html.Label(html.B('Model'), className='header-label')

    model_options = [{'label': model_name, 'value': model_path} for model_name, model_path
                     in zip(global_data.model_names, global_data.model_paths)]
    selector = dcc.Dropdown(
        options=model_options,
        value=global_data.model_paths[0],
        clearable=False,
        style={'width': '200px'},
        id='model-selector'
    )
    # store selected model_path in hidden Div. This is to chain callbacks in correct order: Model selection should
    # first update selected layer as new model might have fewer layers than the current selected layer number. Once
    # selected layer is updated, only then it is safe to update Graph. So graph update callback is tied to model
    # holder changes and not directly to dropdown value
    selected_model_holder = html.Div(id='selected-model', children=global_data.model_paths[0], hidden=True)
    model_selector_container.children = [label, selector, selected_model_holder]
    return model_selector_container


def head_selector():
    head_selector_container = html.Div(
        className='header-control-container')  # style={'marginRight': '5px', 'marginLeft': '5px'},
    label = html.Label(html.B('Head'), className='header-label')

    show_all = dcc.Checklist(
        id='show-all-heads',
        options=[{'label': 'Show all', 'value': True}],
        value=[True]
    )

    head_options = [{'label': f'Head {head + 1}', 'value': head} for head in range(global_data.number_of_heads)]
    selector = dcc.Dropdown(
        options=head_options,
        value=global_data.selected_head,
        clearable=False,
        style={'width': '200px'},
        id='head-selector',
        disabled=True,
    )
    # selected_head_holder = html.Div(id='selected-model', children=global_data.model_paths[0], hidden=True)
    head_selector_container.children = [label, selector, show_all]  # selected_model_holder]
    return head_selector_container

def get_colorscale_options(mode64x64, disabled):
    if not mode64x64:
        options=[
            {'label': "Individual row/column", 'value': 'mode1', 'disabled': disabled},
            {'label': "Individual head", 'value': 'mode2', 'disabled': disabled},
            {'label': "Layer", 'value': 'mode3', 'disabled': disabled}
        ]
    else:
        options=[
            {'label': "Individual head", 'value': 'mode2', 'disabled': disabled},
            {'label': "Layer", 'value': 'mode3', 'disabled': disabled}
        ]
    return options

def colorscale_selector():
    colorscale_selector_container = html.Div(className='header-control-container')
    label = html.Label(html.B('Colorscale min/max'), className='header-label')
    show_scale = dcc.Checklist(
        id='show-colorscale',
        options=[{'label': 'Show scale', 'value': True}],
        value=[True],
        style={'marginRight': '5px'}
    )

    container = html.Div(
                         style={'display': 'flex', 'flexDirection': 'row'})
    container_8x8 = html.Div(
                         style={'display': 'flex', 'flexDirection': 'column', 'marginLeft': '5px', 'marginRight': '5px'})

    container_64x64 = html.Div(
                         style={'display': 'flex', 'flexDirection': 'column', 'marginLeft': '5px', 'marginRight': '5px'})

    label_8x8 = html.Label(id='colorscale-label-8x8', children='8x8 colorscale min/max:', style={'textDecoration': 'underline'})

    selector = dcc.RadioItems(
        options=get_colorscale_options(mode64x64=False, disabled=False),
        value='mode2',
        style={'display': 'flex', 'flexDirection': 'column'},  # , 'alignItems:': 'flex-end'}
        id='colorscale-mode-selector'
    )
    label_64x64 = html.Label(id='colorscale-label-64x64', children='64x64 colorscale min/max:', style={})
    selector_64x64 = dcc.RadioItems(
        options=get_colorscale_options(mode64x64=True, disabled=True),
        value='mode2',
        style={'display': 'flex', 'flexDirection': 'column'},  # , 'alignItems:': 'flex-end'}
        id='colorscale-mode-selector-64x64'
    )
    container_8x8.children = [label_8x8, selector]
    container_64x64.children = [label_64x64, selector_64x64]

    container.children = [container_8x8, container_64x64, show_scale]#[selector, selector_64x64]
    colorscale_selector_container.children = [label, container]#[label, selector, show_scale]

    return colorscale_selector_container

@app.callback(Output('head-selector', 'disabled'),
              Input('show-all-heads', 'value'),
              )
def update_selected_model(value):
    if value == [True]:
        disabled = True
        if not global_data.show_all_heads:
            global_data.show_all_heads = True
            global_data.grid_has_changed = True
    else:
        disabled = False
        if global_data.show_all_heads:
            global_data.show_all_heads = False
            global_data.grid_has_changed = True
    print('SHOW ALL HEADS', global_data.show_all_heads)
    return disabled

@app.callback([Output('colorscale-mode-selector', 'options'),
               Output('colorscale-mode-selector-64x64', 'options'),
               Output('colorscale-label-8x8', 'style'),
               Output('colorscale-label-64x64', 'style')
               ],
              Input('mode-selector', 'value'),
              )
def update_colorscale_selector_options(mode):
    if mode == '64x64':
        options = get_colorscale_options(mode64x64=False, disabled=True)
        options_64x64 = get_colorscale_options(mode64x64=True, disabled=False)
        style = {}
        style_64x64 = {'textDecoration': 'underline'}
    else:
        options = get_colorscale_options(mode64x64=False, disabled=False)
        options_64x64 = get_colorscale_options(mode64x64=True, disabled=True)
        style = {'textDecoration': 'underline'}
        style_64x64 = {}

    return options, options_64x64, style, style_64x64



@app.callback([Output('selected-model', 'children'),
               Output('layer-selector', 'options'),
               Output('layer-selector', 'value')
               ],
              Input('model-selector', 'value'),
              )
def update_selected_model(model):
    global_data.set_model(model)
    return model, get_layer_options(), global_data.selected_layer
