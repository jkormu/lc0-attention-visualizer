import dash
from copy import deepcopy
from global_data import global_data
from svg_pieces import get_svg_board

from dash import dcc, html, Input, Output, State

from server import app

import chess.pgn
import base64
import io

from dash import dash_table

from fen_input import fen_component

from utils import callback_triggered_by

FEN_PGN_COMPONENT_RELATIVE_HEIGHT = '40%'
PGN_COMPONENT_STYLE = {
    'height': '5em',  # '100%',
    # 'width': '100%',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    # 'position': 'absolute',
    # 'left': 0,
    'display': 'flex',
    'flexDirection': 'column',
    #"visibility": "hidden"
}

#style to disable selected and active cell highlighting in datatable
DEFAULT_STYLE_DATA_CONDITIONAL = [
        {
            "if": {"state": "active"},
            "backgroundColor": "transparent",
            "border": "none",
        },
        {
            "if": {"state": "selected"},
            "backgroundColor": "transparent",
            "border": "none",
        },
    ]

#SELECTED_CELL_COLOR = 'rgba(230,178,207,0.5) !important'



def parse_pgn(contents, filename):
    if contents is None:
        return dash.no_update
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'pgn' in filename:
            # Assume that the user uploaded a pgn file
            first_game = chess.pgn.read_game(io.StringIO(decoded.decode('utf-8')))
        else:
            return 'Not a pgn'
    except Exception as e:
        return 'Upload failed'

    board = first_game.board()
        #fen = board.fen()
        # game_data_pgn.board = board
    data = [deepcopy(board)]
    for move in first_game.mainline_moves():
        board.push(move)
        data.append(deepcopy(board))
            #print('MOVE STACK LEN', len(board.move_stack))

    global_data.pgn_data = data
    global_data.set_board(data[0])

    global_data.move_table_boards = {}

    game_info = f'**File**: {filename}\n'
    game_info += f'**White**: {first_game.headers.get("White", "?")}\n'
    game_info += f'**Black**: {first_game.headers.get("Black", "?")}'
    game_info = dcc.Markdown(game_info, style={"whiteSpace": "pre"})
    return game_info


# @app.callback(
#    [Output('pgn-info', 'children'),
#     Output('move-table', 'children')],
#    [Input('upload-pgn', 'contents'),
#     ],
#    [State('upload-pgn', 'filename')]
# )
# def update_pgn(content, filename):
#    triggerers = dash.callback_context.triggered
#    is_new_pgn = True
#    for triggerer in triggerers:
#        if triggerer['prop_id'] == 'position-mode-selector.value':
#            is_new_pgn = False
#            break
#    #if position_mode == 'fen':
#    #    return ''
#    info = parse_pgn(content, filename, is_new_pgn)
#    table = make_table()
#    return (info, table)


def position_pane():
    container = html.Div(style={'height': '100%',
                                'display': 'flex', 'flexDirection': 'column',
                                #       'position': 'relative',
                                # 'width': '100%',
                                # 'paddingBottom': FEN_PGN_COMPONENT_RELATIVE_HEIGHT,
                                #       'float': 'left',
                                #    'height': 0,
                                })

    # fen_component = html.Div(id='fen-component', style=FEN_COMPONENT_STYLE)
    # add_button = html.Button(id='add-fen',
    #                         children=['Add fen'],
    #                         style={'marginRight': '5px', 'marginBottom': '3px'})
    # fen_input = dcc.Input(id='fen-input',
    #                      type='text',
    #                      #size="70",#"92", #"70"
    #                      autoComplete="off",
    #                      style={'font-size': '12px', 'width': '100%'}
    #                      #style={'flex': 1},
    #                      )

    # click_mode = dcc.Checklist(id='click-mode',
    #                                  options=[{'label': 'Add also parents of clicked node',
    #                                            'value': 'add-also-parents'}],
    #                                  value=['add-also-parents'])

    # add_startpos = html.Button(id='add-startpos',
    #                         children=['Add start position'],
    #                         style={'marginRight': '5px', 'marginBottom': '3px'}) #, 'marginTop': '5px'

    # add_buttons = html.Div(children=[add_button, add_startpos],
    #                       style={'display': 'flex'})
    #

    mode_selector = html.Div(children=[dcc.RadioItems(id='position-mode-selector',
                                                      options=[{'label': 'pgn', 'value': 'pgn'},
                                                               {'label': 'fen', 'value': 'fen'},
                                                               ],
                                                      value='fen')],
                             style={'marginBottom': '3px'})

    mode_changed_indicator = html.Div(id='position-mode-changed-indicator', hidden=True)

    fen_pgn_container = html.Div(style={
        'position': 'relative',
        'width': '100%',
        #'paddingBottom': FEN_PGN_COMPONENT_RELATIVE_HEIGHT,
        'float': 'left',
        'marginBottom': '5px',
    #    'height': 0,
    },)


    fen_input = fen_component()

    upload = dcc.Upload(
        id='upload-pgn',
        children=[html.Div(style={'flex': 1}),
                  html.Div([
                      'Drag and Drop a pgn file or ',
                      html.A('Select File')
                  ],
                      style={'flex': 1}
                  ),
                  html.Div(style={'flex': 1}
                           ),
                  ],
        style=PGN_COMPONENT_STYLE,
        className='hidden-but-reserve-space',
        # Only one pgn allowed
        multiple=False
    )

    img = html.Img(id='board-img', src=get_svg_board(global_data.board, None, False))

    pgn_info = html.Div(id='pgn-info',
                        style={'height': '5em'},
                        hidden=True)

    fen_pgn_container.children = [fen_input, upload]

    next_button = html.Button(id='next-move-button', children='\u25BA', style={'flex': '1', 'width': '50%'})
    previous_button = html.Button(id='previous-move-button', children='\u25C4', style={'flex': '1', 'width': '50%'})

    buttons = html.Div(id='move-selection-buttons', children=[previous_button, next_button], style={'width': '100%', 'marginTop': '5px'}, className='hidden-but-reserve-space', hidden=True)

    move_table = make_datatable()

    # fen_added_indicator = html.Div(id='fen-added', style={'display': 'none'})
    # fen_deleted_indicator = html.Div(id='data-deleted-indicator', style={'display': 'none'})
    # fen_component.children = [add_buttons, fen_input, click_mode, fen_added_indicator, fen_deleted_indicator]
    # fen_pgn_container.children = [fen_component, upload]

    container.children = [mode_selector, mode_changed_indicator, fen_pgn_container, img, pgn_info, buttons, move_table]
    return container



def make_datatable():
    table = dash_table.DataTable(
        id='move-table',
        data=None,
        columns=[
            {"name": '', "id": 'dummy_left'},
            {"id": 'Move', "name": '#'},
            {"id": 'White', "name": 'White'},
            {"id": 'Black', "name": 'Black'},
            {"name": '', "id": 'dummy_right'}
        ],
        style_data={'border': 'none'},
        # style_table={'width': '100%', 'marginLeft': '0px', 'overflowY': 'auto', },
        style_table={'width': '100%', 'marginLeft': '0px', 'overflowY': 'auto',
                     },
        style_header={
            # 'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'border': 'none'
        },
        css=[{"selector": "table", "rule": "width: 100%;"},
             {"selector": ".dash-spreadsheet.dash-freeze-top, .dash-spreadsheet .dash-virtualized",
              "rule": "max-height: none;"}],
        style_data_conditional=DEFAULT_STYLE_DATA_CONDITIONAL,
        # cell_selectable=False,
        active_cell={'row': 0, 'column': 2, 'column_id': 'White'}
    )

    #next_button = html.Button(id='next-move-button', children='->', style={'flex': '1'})
    #previous_button = html.Button(id='previous-move-button', children='<-', style={'flex': '1'})

    #buttons = html.Div(children=[previous_button, next_button], style={'width': '75%', 'display': 'flex'})

    container = html.Div(id='table-container', children=[
                                                         html.Div(children=table, style={'borderLeft': f'1px solid grey',
                                                                                        'borderTop': f'1px solid grey'})],
                         style={'flex': '1', 'overflow': 'auto', },
                         hidden=True)

    #container_outer = html.Div(children=[buttons, container],
    #                           style={'display': 'flex', 'flexDirection': 'column', 'height': '100%'}) #{'display': 'flex', 'flexDirection': 'row', 'flex': '0'}

    return container


# app.clientside_callback(
#    """
#    function(active_cell) {
#        return {'row': 4, 'column': 2, 'column_id': 'White'};
#    }
#    """,
#    Output('move-table', 'active_cell'),
#    Input('move-table', 'active_cell'),
#    #Input('in-component2', 'value')
# )

#a = """

@app.callback(
    [Output('fen-component', 'className'),
     Output('upload-pgn', 'className'),
     Output('table-container', 'className'),
     Output('move-selection-buttons', 'className'),
     Output('position-mode-changed-indicator', 'children')
     ],
    Input('position-mode-selector', 'value')
)
def set_position_mode(mode):
    if mode is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


    hidden = 'hidden-but-reserve-space'
    visible = ''
    global_data.running_counter += 1
    if mode == 'fen':
        global_data.board.set_fen(global_data.fen)
        global_data.update_activations_data()
        global_data.update_selected_activation_data()
        return visible, hidden, 'completely-hidden', 'completely-hidden', global_data.running_counter
    if mode == 'pgn':
        if global_data.move_table_boards != {}:
            board = global_data.move_table_boards[global_data.active_move_table_cell]
            global_data.set_board(board)
            global_data.update_activations_data()
            global_data.update_selected_activation_data()
        return hidden, visible, '', '', global_data.running_counter

@app.callback(
    [Output('pgn-info', 'children'),
     Output('move-table', 'data'),
     Output('table-container', 'hidden'), #TODO: wrap table-container and buttons to same container and hide/unhide it
     Output('move-selection-buttons', 'hidden'),
     Output('move-table', 'active_cell'),
     ],
    [Input('upload-pgn', 'contents'),
     ],
    [State('upload-pgn', 'filename')]
)
def update_pgn(content, filename):
    triggerers = dash.callback_context.triggered
    info = parse_pgn(content, filename)
    table_data = get_datatable_data()

    hidden = global_data.pgn_data == []
    print('VALUE OF HIDDEN', hidden)
    active_cell = {'row': 0, 'column': 2, 'column_id': 'White'}
    return info, table_data, hidden, hidden, active_cell

@app.callback(
    Output('board-img', 'src'),
    [Input('fen-text', 'children'),
    Input('move-table', 'style_data_conditional'),
     Input('position-mode-changed-indicator', 'children')])
def update_board_image(*args):
    return get_svg_board(global_data.board, None, False)

@app.callback(
    Output('move-table', 'style_data_conditional'),
    #Output('move-table', 'selected_cells')],
    #[
      #  Output('move-table', 'selected_cells'),
    #Output('move-table', 'active_cell'),
    #],
    [Input('move-table', 'active_cell'),
     Input('next-move-button', 'n_clicks'),
     Input('previous-move-button', 'n_clicks')])
def cell_highlight(active_cell, *args):
    #style_data_conditional = []
    #disable_selected = {
    #        "if": {"state": "active"},
    #        #"backgroundColor": "transparent !important",
    #        "backgroundColor": "transparent",
    #        #"border": "transparent !important",
    #    }



    if active_cell is None:
        return dash.no_update#, []#[], dash.no_update

    triggerer = callback_triggered_by()

    if triggerer == 'move-table.active_cell':
        print('ACTIVE:', active_cell)

        row_ind = active_cell['row']
        col_id = active_cell['column_id']

        if col_id in ('Move', 'dummy_left', 'dummy_right'):
            return dash.no_update
    else:
        current_row_ind = global_data.active_move_table_cell[0]
        current_col_id = global_data.active_move_table_cell[1]
        if triggerer == 'next-move-button.n_clicks':
            if current_col_id == 'White':
                row_ind = current_row_ind
                col_id = 'Black'
            else:
                row_ind = current_row_ind + 1
                col_id = 'White'
        else:
            if current_col_id == 'White':
                row_ind = current_row_ind - 1
                col_id = 'Black'
            else:
                row_ind = current_row_ind
                col_id = 'White'
        if (row_ind, col_id) not in global_data.move_table_boards:
            return dash.no_update

    global_data.active_move_table_cell = (row_ind, col_id)

    cell_highlight = {
            "if": {'row_index': row_ind, 'column_id': col_id},
            "font-weight": "bold",
            "color": "red",
        }
    style_data_conditional = [cell_highlight] + DEFAULT_STYLE_DATA_CONDITIONAL

    if global_data.move_table_boards != {}:
        board = global_data.move_table_boards[(row_ind, col_id)]
        global_data.set_board(board)

        print(board)

    #col_ind = active_cell['column']
    #col_id = active_cell['column_id']
    #print('selected', row_ind, col_ind, col_id)
    #if col_id in ('Move', 'dummy_left', 'dummy_right'):  # cells in move number column are not selectable
    #    print('returning previously  selected')
    #    row_ind = global_data.move_table_active_cell['row']
    #    col_id = global_data.move_table_active_cell['column_id']
    #    #return [], global_data.move_table_active_cell
    #else:
    #    global_data.move_table_active_cell = active_cell

    #highlight = {
    #    'if': {'column_id': col_id},#'row_index': row_ind,
    #    'backgroundColor': 'blue !important'
    #}

    #style_data_conditional.append(highlight)
    #style_data_conditional.append(disable_selected)
    print(style_data_conditional)

    return style_data_conditional#, []#[], dash.no_update#style_data_conditional
#"""


def get_last_move_as_san(board):
    move = board.pop()
    san = board.san(move)
    board.push(move)

    return san


def get_datatable_data():
    if not global_data.pgn_data:
        return []
    data = []
    row = None  # {'White': '', 'Black': ''}
    row_ind = 0
    moven_nr = 0
    boards_in_table = {}
    #TODO: make it work with pgns starting from black move
    for board in global_data.pgn_data:
        if not board.turn:
            if row:
                data.append(row)
                row_ind += 1
            moven_nr += 1
            row = {'Move': f'{moven_nr}.', 'White': '', 'Black': ''}
        if board.move_stack:
            # print('----------')
            # print(board)
            # print(board.move_stack[-1])
            move = get_last_move_as_san(board)  # board.san(board.move_stack[-1])
            # print(move)
            # else:
            #    move = '*'
            col_id = ('White', 'Black')[board.turn]
            row[col_id] = move
            boards_in_table[(row_ind, col_id)] = board
        else:
            data.append({'Move': f'{moven_nr}.', 'White': '-', 'Black': '-'})
            boards_in_table[(row_ind, 'White')] = board
            boards_in_table[(row_ind, 'Black')] = board
            row_ind += 1

    #    if moven_nr == 0:
    #        row = {'Move': moven_nr, 'White': '*', 'Black': '*'}
    #        data.append(row)
    #        moven_nr += 1
    #        continue
    #    else:
    #        if board.turn:
    #            data.append(row)
    #            moven_nr += 1
    #            row = {'Move': moven_nr, 'White': '', 'Black': ''}
    #    if board.move_stack:
    #        move = board.move_stack[-1].__str__()
    #    else:
    #        move = '*'
    #    row[('White', 'Black')[board.turn]] = move

    # if board.turn:
    #    if row: #!= {'White': '', 'Black': ''}:
    #        data.append(row)
    #        moven_nr += 1
    #        #is_first_row = False
    #        row = {'Move': moven_nr, 'White': '', 'Black': ''}
    #    else:
    #        row = {'Move': moven_nr, 'White': '*', 'Black': '*'}
    # if board.move_stack:
    #    move = board.move_stack[-1].__str__()
    # else:
    #    move = '*'
    # row[('White', 'Black')[board.turn]] = move
    global_data.move_table_boards = boards_in_table
    data.append(row)
    return data


def make_table():
    data = global_data.pgn_data
    if not data:
        return []
    # header
    table_content = [html.Tr([html.Th(header) for header in ('White', 'Black')])]
    rows = []
    row = html.Tr()
    cells = []
    board = data[0]
    # if first move is not by white, add empty cell
    if not board.turn:
        cells.append(html.Td(''))
    for board in data:
        if board.turn:
            row.children = cells
            rows.append(row)
            row = html.Tr()
            cells = []
        if board.move_stack:
            move = board.move_stack[-1].__str__()
        else:
            move = '*'
        cells.append(html.Td(move))
    row.children = cells
    rows.append(row)
    table_content += rows
    return table_content

    # body
    # table_content += [html.Tr([html.Td()])]
    # table = html.Table( )

    # [html.Tr([html.Th(col) for col in dataframe.columns])] +
    # Body
    # [html.Tr([
    #    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
    # ]) for i in range(min(len(dataframe), max_rows))]
