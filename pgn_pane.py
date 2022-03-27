import dash
from copy import deepcopy
from global_data import global_data

from dash import dcc, html, Input, Output, State

from server import app

import chess.pgn
import base64
import io

from dash import dash_table

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
}


def pgn_pane():
    container = html.Div(style={
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
        # Only one pgn allowed
        multiple=False
    )
    pgn_info = html.Div(id='pgn-info',
                        style={'height': '5em'},
                        hidden=True)

    move_table = make_datatable()

    # fen_added_indicator = html.Div(id='fen-added', style={'display': 'none'})
    # fen_deleted_indicator = html.Div(id='data-deleted-indicator', style={'display': 'none'})
    # fen_component.children = [add_buttons, fen_input, click_mode, fen_added_indicator, fen_deleted_indicator]
    # fen_pgn_container.children = [fen_component, upload]
    container.children = [upload, pgn_info, move_table]
    return container


def parse_pgn(contents, filename, is_new_pgn):
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

    if is_new_pgn:
        board = first_game.board()
        fen = board.fen()
        # game_data_pgn.board = board
        data = [deepcopy(board)]
        for move in first_game.mainline_moves():
            board.push(move)
            data.append(deepcopy(board))

        global_data.pgn_data = data

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

@app.callback(
    [Output('pgn-info', 'children'),
     Output('move-table', 'data')],
    [Input('upload-pgn', 'contents'),
     ],
    [State('upload-pgn', 'filename')]
)
def update_pgn(content, filename):
    triggerers = dash.callback_context.triggered
    is_new_pgn = True
    for triggerer in triggerers:
        if triggerer['prop_id'] == 'position-mode-selector.value':
            is_new_pgn = False
            break
    # if position_mode == 'fen':
    #    return ''
    info = parse_pgn(content, filename, is_new_pgn)
    table_data = get_datatable_data()
    return (info, table_data)


def make_datatable():
    table = dash_table.DataTable(
        id='move-table',
        # css=[dict(selector="p", rule="margin: 0px;")],
        data=None,
        columns=[
            {"id": 'Move', "name": 'Move'},
            {"id": 'White', "name": 'White'},
            {"id": 'Black', "name": 'Black'}
            #{"id": name, "name": name, "selectable": True if name != 'Move' else False} for name in ('Move', 'White', 'Black')
        ],
        style_data={'border': 'none'},
        style_table={'border': '1px solid grey'}
        # markdown_options={"html": True},
        # style_table={"width": 200},
    )
    return table

def get_last_move_as_san(board):
    move = board.pop()
    san = board.san(move)
    board.push(move)

    return san

def get_datatable_data():
    if not global_data.pgn_data:
        return []
    data = []
    row = None#{'White': '', 'Black': ''}
    moven_nr = 0
    for board in global_data.pgn_data:
        if not board.turn:
            if row:
                data.append(row)
            moven_nr += 1
            row = {'Move': moven_nr, 'White': '', 'Black': ''}
        if board.move_stack:
            print('----------')
            print(board)
            print(board.move_stack[-1])
            move = get_last_move_as_san(board)#board.san(board.move_stack[-1])
            print(move)
        #else:
        #    move = '*'
            row[('White', 'Black')[board.turn]] = move
        else:
            data.append({'Move': moven_nr, 'White': '-', 'Black': '-'})

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

        #if board.turn:
        #    if row: #!= {'White': '', 'Black': ''}:
        #        data.append(row)
        #        moven_nr += 1
        #        #is_first_row = False
        #        row = {'Move': moven_nr, 'White': '', 'Black': ''}
        #    else:
        #        row = {'Move': moven_nr, 'White': '*', 'Black': '*'}
        #if board.move_stack:
        #    move = board.move_stack[-1].__str__()
        #else:
        #    move = '*'
        #row[('White', 'Black')[board.turn]] = move
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
