from dash import dcc, html, Input, Output, State
from global_data import global_data
import dash
from server import app

#FEN_COMPONENT_STYLE = {'position': 'absolute', 'left': 0, 'height': '100%', 'width': '97%'}

def fen_component():
    fen_component = html.Div(id='fen-component',
                             style={'position': 'absolute', 'left': 0,
                                    'display': 'flex', 'flexDirection': 'column',
                                    'width': '100%'},
                             #className='header-control-container',
                             # style=FEN_COMPONENT_STYLE,
                             )
    add_button = html.Button(id='add-fen',
                             children=['Set fen'],
                             style={#'marginRight': '5px',
                                    'marginBottom': '3px',
                                    'width':'100%',
                                    'box-sizing': 'border-box'})
    fen_input = dcc.Textarea(id='fen-input',
                          #type='text',
                          #size="75",
                          #autoComplete="off",
                          style={#'fontSize': '12px',
                                'width': '100%',
                                'height': '50px',
                                'box-sizing': 'border-box',
                                #'border': 'none',
                                 },
                          placeholder=global_data.board.fen(),
                          # style={'flex': 1},
                          )



    add_startpos = html.Button(id='add-startpos',
                               children=['Start position'],
                               style={'marginRight': '5px', 'marginBottom': '3px'},
                               hidden=True)  # , 'marginTop': '5px'

    add_buttons = html.Div(children=[add_button,
                                     fen_input,
                                     add_startpos
                                     ],
                           # style={'display': 'flex'},
                           )

    fen_text = html.Div(id='fen-text',
                        hidden=True,
                        style={'height': '1.5em',
                               'fontSize': '15px',
                               'textAlign': 'center'},
                        children=global_data.fen)
    #label = html.Label(html.B('Fen'), className='header-label')
    side_to_move = html.Label(children=['Side to move: ', html.B(global_data.get_side_to_move())], id='side-to-move', hidden=True)
    fen_feedback = html.B('Invalid FEN', id='fen-feedback', style={'color': 'red'}, className='hidden-but-reserve-space'
                          #hidden=True,
                          )
    fen_component.children = [#label,
                              # fen_input,
                              add_buttons,
                              fen_text,
                              fen_feedback,
                              side_to_move,
                              ]
    # fen_pgn_container.children = [fen_component]
    return fen_component  # fen_pgn_container


@app.callback([Output('fen-input', "value"),
               Output('fen-input', 'placeholder'),
               Output('fen-text', 'children'),
               Output('side-to-move', 'children'),
               Output('fen-feedback', 'className')
               ],
              [Input('add-fen', 'n_clicks'),
               Input('add-startpos', 'n_clicks')],
              [State('fen-input', 'value'), ]
              )
def add_fen(n_clicks_fen, n_clicks_startpos, fen):
    triggerers = dash.callback_context.triggered
    add_fen = False
    add_startpos = False

    for triggerer in triggerers:
        if triggerer['prop_id'] == 'add-fen.n_clicks':
            add_fen = False
        elif triggerer['prop_id'] == 'add-startpos.n_clicks':
            add_startpos = True
            fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    if add_startpos:
        print('adding start pos')
        if n_clicks_startpos is None:
            return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    if fen is None:  # or (add_fen and (fen is None or n_clicks_fen is None)):
        return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)

    try:
        global_data.set_fen(fen)
    except ValueError:
        return ('', dash.no_update, dash.no_update, dash.no_update, '') #'not valid fen'

    print('setting fen')
    global_data.update_selected_activation_data()
    return ('', fen, fen, ['Side to move: ', html.B(global_data.get_side_to_move())], 'hidden-but-reserve-space')
