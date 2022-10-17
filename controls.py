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

@app.callback([Output('selected-model', 'children'),
               Output('layer-selector', 'options'),
               Output('layer-selector', 'value')
               ],
              Input('model-selector', 'value'),
              )
def update_selected_model(model):
    global_data.set_model(model)
    return model, get_layer_options(), global_data.selected_layer
