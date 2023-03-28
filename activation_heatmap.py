import dash
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from global_data import global_data

from svg_pieces import get_svg_board
from dash import dcc, html, Input, Output, State
from server import app

from utils import callback_triggered_by

import time

import numpy as np


V_GAP = 0.15
LAYOUT_MARGIN_V = 40

def heatmap_data(head):
    data = global_data.get_head_data(head)
    return data


def heatmap_figure():
    if global_data.model is None:
        return {}
    start = time.time()
    fig = make_figure()
    print('make fig:', time.time() - start)

    start = time.time()
    fig = add_heatmap_traces(fig)
    print('add traces:', time.time() - start)

    start = time.time()
    fig = add_layout(fig)
    print('add layout total:', time.time() - start)

    start = time.time()
    if not global_data.visualization_mode_is_64x64:
        fig = add_pieces(fig)
        print('add pieces:', time.time() - start)




    return fig


def heatmap():
    start = time.time()
    # We need to recalculate graph when grid size changes, other wise layout is a mess (Dash bug?). Use hidden Div's children to trigger callback for graph recalc.
    # Otherwise, we can just recalculate figure part and frontend rendering will be much faster
      #
    graph = html.Div(id='graph-container', children=[heatmap_graph()],
                     style={'height': '100%', 'width': '100%', "overflow": "auto"#, 'textAlign': 'center'#, "display": "flex", "justifyContent":"center"
                            })
    print('GRAPH CREATION:', time.time() - start)
    return graph


def heatmap_graph():
    fig = heatmap_figure()

    config = {
        'displaylogo': False,
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
        'toImageButtonOptions': {
            'format': global_data.export_format,
            'scale': global_data.export_scale
        }}

    style = {'height': global_data.figure_container_height, 'width': '100%'}#, 'margin': '0 auto'}

    graph = dcc.Graph(figure=fig, id='graph', style=style,
                      responsive='auto',#True,  # True,
                      config=config
                      )

    # graph = html.Div(id='graph-container', children=[graph], style={'height': '100%', 'width': '100%', "overflow": "auto"
    #                                                           })
    # graph_component.children = [graph]

    global_data.cache_figure(fig)

    return graph


def make_figure():
    #print('assumed key', global_data.subplot_rows, global_data.subplot_cols, global_data.visualization_mode_is_64x64,  global_data.selected_head if not global_data.show_all_heads else -1)
    #print('key', global_data.get_figure_cache_key())
    #print('all keys', global_data.figure_cache.keys())
    fig = global_data.get_cached_figure()
    if fig is None:
        if global_data.show_all_heads:
            titles = [f"Head {i + 1}" for i in range(global_data.number_of_heads)]
            print('MAKING SUBPLOTS', 'rows:', global_data.subplot_rows, 'cols:', global_data.subplot_cols)
            print('NUMBER OF HEADS:', global_data.number_of_heads)
            fig = make_subplots(rows=global_data.subplot_rows, cols=global_data.subplot_cols, subplot_titles=titles,
                                horizontal_spacing=global_data.heatmap_horizontal_gap / global_data.subplot_cols,
                                vertical_spacing=V_GAP / global_data.subplot_rows,
                                )
        else:
            print('CREATING 1x1')
            titles = [f"head {global_data.selected_head +1}"]
            fig = make_subplots(rows=1, cols=1, subplot_titles=titles)#go.Figure()#make_subplots(rows=1, cols=1, subplot_titles=titles)

    return fig


def add_layout(fig):
    start = time.time()

    #coloraxis1 = None
    #if global_data.visualization_mode_is_64x64:
    #    if global_data.colorscale_mode == '3':
    #        coloraxis1 = {'colorscale': 'Viridis'}

    coloraxis = None
    if global_data.colorscale_mode == 'mode3':
        cmin = np.amin(global_data.activations[:, :, :])
        cmax = np.amax(global_data.activations[:, :, :])
        coloraxis = {'colorscale': 'Viridis', 'colorbar': {'ypad': 0} , 'cmin': cmin, 'cmax': cmax, 'showscale': global_data.show_colorscale}

    if global_data.check_if_figure_is_cached():
        print('Using existing layout')
        fig.update_layout({'coloraxis1': coloraxis}, overwrite=True)
        return fig

    layout = go.Layout(
        # title='Plot title goes here',
        margin={'t': LAYOUT_MARGIN_V, 'b': LAYOUT_MARGIN_V, 'r': 40, 'l': 40},
        coloraxis1=coloraxis,
        modebar={'orientation': 'v'}
        #coloraxis={'colorscale': 'Viridis'}
        #pa
        #plot_bgcolor='rgb(0,0,0)',
        #paper_bgcolor="black"
    )

    fig.update_layout(layout)
    # fig['layout'].update(layout)

    print('update layout:', time.time() - start)

    start = time.time()
    fig = update_axis(fig)
    print('update axis:', time.time() - start)
    # print(fig)
    return fig


def update_axis(fig):
    if global_data.visualization_mode_is_64x64:
        tickvals_x = list(range(0, 64, 4))
        tickvals_y = list(range(3, 67, 4))#list(range(0, 64, 4))#list(range(3, 67, 4))
        if global_data.board.turn:
            ticktext_x = [x + y for x, y in zip('ae' * 8, '1122334455667788')]
        #tickvals = list(range(0, 64))
        #ticktext_x = [x + y for x, y in zip('abcdefg' * 8, '1'*8 + '2'*8 + '3'*8 + '4'*8 + '5'*8 + '6'*8 + '7'*8 + '8'*8)]
            ticktext_y = ticktext_x[::-1]
        else:
            ticktext_x = [x + y for x, y in zip('ae' * 8, '1122334455667788'[::-1])]
            ticktext_y = ticktext_x[::-1]
        showticklabels = True
        #ticklabelstep = 4
        val_range = [-0.5, 63.5]
        ticks = 'outside'
        title_x = {'text': "Keys ('to' square)", 'standoff': 1}
        title_y = {'text': "Queries ('from' square)", 'standoff': 1}
    else:
        title_x = None
        title_y = None
        tickvals_x = list(range(8))  # [0, 1, 2, 3, 4, 5, 6, 7]
        tickvals_y = tickvals_x
        ticktext_x = [letter for letter in 'abcdefgh']
        ticktext_y = [letter for letter in '12345678']
        showticklabels = True
        #ticklabelstep = 1
        val_range = [-0.5, 7.5]
        ticks = ''

    if not global_data.show_all_heads or (global_data.subplot_cols == 1 and global_data.subplot_rows == 1):
        constraintowards_x = 'center'
    else:
        constraintowards_x = 'right'


    fig.update_xaxes(title=title_x,
                     range=val_range,
                     # ticklen=50,
                     zeroline=False,
                     showgrid=False,
                     scaleanchor='y',
                     constrain='domain',
                     constraintoward=constraintowards_x,
                     ticks=ticks,  # ticks,
                     ticktext=ticktext_x,
                     tickvals=tickvals_x,
                     showticklabels=showticklabels,
                     # mirror='ticks',
                     fixedrange=True,
                     #ticklabelstep=ticklabelstep,
                     )

    fig.update_yaxes(title=title_y,
                     range=val_range,
                     zeroline=False,
                     showgrid=False,
                     scaleanchor='x',
                     constrain='domain',
                     constraintoward='top',
                     ticks=ticks,  # ticks,
                     ticktext=ticktext_y,
                     tickvals=tickvals_y,
                     showticklabels=showticklabels,
                     # mirror='allticks',
                     # side='top',
                     fixedrange=True,
                     #ticklabelstep=ticklabelstep
                     )
    return fig


def calc_colorbar(row, col):
    row = global_data.subplot_rows - row + 1 #invert
    #row = global_data.subplot_rows - row - 1 #invert

    dy = (1/global_data.subplot_rows)
    dx = (1/global_data.subplot_cols)

    offset = 1/global_data.subplot_cols - 2*(global_data.heatmap_horizontal_gap/(global_data.subplot_cols))/4#global_data.colorscale_x_offset#(494.1125)/2239.2#1/global_data.subplot_cols - 3*(global_data.heatmap_horizontal_gap/(global_data.subplot_cols))/4

    if global_data.heatmap_h == 0:
        len = (1 - V_GAP/global_data.subplot_rows) / global_data.subplot_rows #- #V_GAP/global_data.subplot_rows
        lenmode = 'fraction'
        offset2 = len / 2
    else:
        #total_h = global_data.heatmap_fig_h * global_data.heatmap_h + (global_data.subplot_rows - 1)
        len = global_data.heatmap_h/(global_data.heatmap_fig_h - 2*LAYOUT_MARGIN_V)
        lenmode = 'fraction'
        offset2 = len / 2
        #lenmode = 'pixels'
        #offset2 = 1 - len/(global_data.subplot_rows*len + V_GAP) #1/global_data.subplot_rows - (V_GAP/global_data.subplot_rows)

        tot_h = global_data.heatmap_fig_h - 2*LAYOUT_MARGIN_V
        max_h = ((1 - V_GAP)) / global_data.subplot_rows
        cur_h =  len
        offset2 = 1 - (global_data.subplot_rows-1)*(dy + (V_GAP / global_data.subplot_rows)/global_data.subplot_rows) - len/2 #0#len/2 #+ (max_h - cur_h)


    #offset = global_data.colorscale_x_offset
    #shift = (global_data.heatmap_w + 20 + 20 + global_data.heatmap_gap)/global_data.heatmap_fig_w
    #cx = (col - 1) * shift + offset


    cx = (col-1)*(dx + (global_data.heatmap_horizontal_gap / global_data.subplot_cols)/global_data.subplot_cols) + offset
    cy = (row-1)*(dy + (V_GAP / global_data.subplot_rows)/global_data.subplot_rows) + offset2
    #cy = (global_data.subplot_rows - 1 - row) * (dy + (V_GAP / global_data.subplot_rows) / global_data.subplot_rows) + offset2

    #######################


    colorbar=dict(len=len, y=cy, x=cx, ypad=0, xpad=0, ticklabelposition='inside', ticks='inside', ticklen=3, lenmode=lenmode,
                  tickfont=dict(color='#7e807f'))

    return colorbar

def add_heatmap_trace(fig, row, col, head=None):
    # print('ADDING heatmap', row, col)
    if head is None:
        head = (row - 1) * global_data.subplot_cols + (col - 1)
    data = heatmap_data(head)

    if data is None:
        return fig

    if global_data.visualization_mode_is_64x64:
        xgap, ygap = 0, 0
        #hovertemplate = 'Query: <b>%{y}</b> <br> Key: <b>%{x}</b> <br> value: <b>%{z}</b><extra></extra>'
        hovertemplate = 'Query: <b>%{customdata[0]}</b> <br>Key: <b>%{customdata[1]}</b> <br>value: <b>%{z:.5f}</b><extra></extra>'
        if global_data.board.turn:
            customdata_x = [[letter + ind for ind in '12345678' for letter in 'abcdefgh'] for _ in range(64)]
            customdata_y = [[letter + ind for _ in range(64)] for ind in '12345678'[::-1] for letter in 'abcdefgh'[::-1]]
        else:
            customdata_x = [[letter + ind for ind in '12345678'[::-1] for letter in 'abcdefgh'] for _ in range(64)]
            customdata_y = [[letter + ind for _ in range(64)] for ind in '12345678' for letter in 'abcdefgh'[::-1]]

        #customdata_y = [[letter + ind for _ in range(64)] for ind in '12345678' for letter in 'abcdefgh']
        customdata = np.moveaxis([customdata_y, customdata_x], 0, -1)#[customdata_x, customdata_y]

    else:
        xgap, ygap = 2, 2
        hovertemplate = '<b>%{x}%{y}</b>: <b>%{z}</b><extra></extra>'
        customdata = None

    coloraxis = None
    #Colorscale

    #if global_data.visualization_mode_is_64x64:
    #    if global_data.colorscale_mode == '3':
    #        coloraxis = 'coloraxis1'

    coloraxis = None
    colorscale = 'Viridis'
    colorbar = None
    #if global_data.show_colorscale and global_data.colorscale_mode == 'mode3':
    if global_data.colorscale_mode == 'mode3':
        coloraxis = 'coloraxis1'
        colorscale = None

    elif global_data.show_colorscale and not global_data.colorscale_mode == 'mode3' and not (not global_data.show_all_heads or (global_data.subplot_cols == 1 and global_data.subplot_rows == 1)):
        colorbar = calc_colorbar(row, col)

    zmin, zmax = None, None

    if global_data.colorscale_mode == 'mode2':
        pass
        zmin = np.amin(global_data.activations[head, :, :])
        zmax = np.amax(global_data.activations[head, :, :])
        #print('ZMINMAX M2', head, zmin, zmax)

    elif global_data.colorscale_mode == 'mode1':
        zmin = np.amin(data)
        zmax = np.amax(data)

    #print('Trace data shape', data.shape)
    trace = go.Heatmap(
        z=data,
        colorscale=colorscale,
        showscale=global_data.show_colorscale,#True,
        colorbar=colorbar,
        #colorbar=dict(len=len, y=cy, x=cx, ypad=0, ticklabelposition='inside', ticks='inside', ticklen=3,
        #              tickfont=dict(color='#7e807f')),
        xgap=xgap,
        ygap=ygap,
        hovertemplate=hovertemplate,
        customdata=customdata,
        zmin=zmin,
        zmax=zmax,
        coloraxis=coloraxis
        #zmin=zmin,
        #zmax=zmax
    )
    fig.add_trace(trace, row=row, col=col)
    return fig


def add_heatmap_traces(fig):
    print('adding traces, rows:', global_data.subplot_rows, 'cols:', global_data.subplot_cols)
    #adding traces is quick so we don't bother using cached values. Wipe old traces and add new.
    fig.data = []
    if global_data.show_all_heads:
        for row in range(global_data.subplot_rows):
            for col in range(global_data.subplot_cols):
                fig = add_heatmap_trace(fig, row + 1, col + 1)
    else:
        fig = add_heatmap_trace(fig, 1, 1, global_data.selected_head)
    return fig


def add_pieces(fig):
    board_svg = get_svg_board(global_data.board, global_data.focused_square_ind, True)

    if global_data.check_if_figure_is_cached():
        print('USING CACHED')
        for img in fig.layout.images:
            img['source'] = board_svg
    else:
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
            exclude_empty_subplots=True,
        )

    return fig

#a = """
# callback to update figure property of graph. In principle, this should be all we ever need to update (+graph height)
# Due to probable dash/plotly bug this is not enough if figure's subplot grid dimensions change as updating only figure will result in messed up layout
# To workaround this, we will update indicator component if grid dimension has changed, which in turn will trigger callback for full graph update
@app.callback([Output('graph', 'figure'),
               #Output('fig-store', 'data'),
               Output('recalculate-graph-indicator', 'children'),
               Output('graph', 'style'),
               Output('fit_to_single_page', 'options')],
              [Input('graph', 'clickData'),
               Input('mode-selector', 'value'),
               Input('layer-selector', 'value'),
               Input('head-selector', 'value'),
               Input('colorscale-mode-selector', 'value'),
               Input('colorscale-mode-selector-64x64', 'value'),
               Input('show-colorscale', 'value'),
               Input('heatmap-size', 'children'),
               Input('fit_to_single_page', 'value'),
               Input('selected-model', 'children'),  # New model was selected
               Input('move-table', 'style_data_conditional'),  # New move was selected in move table
               Input('position-mode-changed-indicator', 'children'),  # fen/pgn mode changed
               Input('fen-text', 'children'),  # New fen was set
               Input('head-selector', 'disabled'),  # Show all heads checkbox value was changed
               ])
def update_heatmap_figure(click_data, mode, layer, head, colorscale_mode, colorscale_mode_64x64, show_colorscale, heatmap_size, fit_to_page, *args):
    fit_to_page_disabled = [{'label': 'Dense layout', 'value': True, 'disabled': True}]
    fit_to_page_enabled = [{'label': 'Dense layout', 'value': True}]

    if layer is None or global_data.model is None:
        return dash.no_update, dash.no_update, {'visibility': 'hidden'}, fit_to_page_enabled#dash.no_update

    fig = dash.no_update
    trigger = callback_triggered_by()
    global_data.set_visualization_mode(mode)
    global_data.set_layer(layer)
    global_data.set_heatmap_size(heatmap_size)
    global_data.set_subplot_mode(fit_to_page)

    global_data.set_head(head)

    global_data.set_colorscale_mode(mode, colorscale_mode, colorscale_mode_64x64, show_colorscale)


    if trigger == 'graph.clickData' and not click_data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update  # , dash.no_update, dash.no_update


    disable_fit_to_page = global_data.figure_container_height == '100%' and global_data.subplot_mode == 'big'
    if disable_fit_to_page:
        fit_to_page_option = fit_to_page_disabled
    else:
        fit_to_page_option = fit_to_page_enabled

    # if grid dimensions have change we need to trigger full graph component recalc (workaround for dash bug where
    # figure layout is messed up if only figure is updated)
    if global_data.grid_has_changed or trigger in ('colorscale-mode-selector.value', 'colorscale-mode-selector-64x64.value') or global_data.force_update_graph:
        global_data.running_counter += 1
        global_data.grid_has_changed = False
        global_data.force_update_graph = 0
        #Erase figure, update indicator with new value, hide graph until updated again
        #return dash.no_update, global_data.running_counter, dash.no_update
        return {}, global_data.running_counter, {'visibility': 'hidden'}, fit_to_page_option

    if trigger == 'graph.clickData' and not global_data.visualization_mode_is_64x64:
        point = click_data['points'][0]
        x = point['x']
        y = point['y']
        square_ind = 8 * y + x
        if square_ind != global_data.focused_square_ind:
            global_data.focused_square_ind = square_ind
            fig = heatmap_figure()
            # container = dash.no_update

    if trigger == 'fen-text.children':
        fig = heatmap_figure()
        # container = dash.no_update

    if trigger in ('mode-selector.value', 'layer-selector.value',
                   'move-table.style_data_conditional',
                   'position-mode-changed-indicator.children',
                   'head-selector.value',
                   'show-colorscale.value', 'heatmap-size.children'):
        fig = heatmap_figure()
        # container = dash.no_update

    if trigger == 'selected-model.children':
        fig = heatmap_figure()  # dash.no_update#heatmap_figure()
        # container = heatmap_graph()
    global_data.cache_figure(fig)
    return fig, dash.no_update, dash.no_update, fit_to_page_option
#"""

@app.callback(Output('graph-container', 'children'),
              Input('recalculate-graph-indicator', 'children'))
def update_heatmap_graph(txt):
    if txt is not None:
        graph = heatmap_graph()
    else:
        graph = dash.no_update
    return graph

