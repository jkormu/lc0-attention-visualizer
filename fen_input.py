from dash import dcc, html, Input, Output, State
from global_data import global_data
import dash
from server import app


def fen_component():
    fen_pgn_container = html.Div(style={
        # 'position': 'relative',
        # 'width': '100%',
        # 'paddingBottom': FEN_PGN_COMPONENT_RELATIVE_HEIGHT,
        # 'float': 'left',
        # 'height': 0,
    })
    fen_component = html.Div(id='fen-component',
                             # style=FEN_COMPONENT_STYLE,
                             )
    add_button = html.Button(id='add-fen',
                             children=['Set fen'],
                             style={'marginRight': '5px', 'marginBottom': '3px'})
    fen_input = dcc.Input(id='fen-input',
                          type='text',
                          size="70",
                          autoComplete="off",
                          style={'fontSize': '12px', 'width': '100%'}
                          # style={'flex': 1},
                          )

    add_startpos = html.Button(id='add-startpos',
                               children=['Start position'],
                               style={'marginRight': '5px', 'marginBottom': '3px'})  # , 'marginTop': '5px'

    add_buttons = html.Div(children=[add_button,
                                     add_startpos
                                     ],
                           style={'display': 'flex'})

    fen_text = html.Div(id='fen-text',
                        hidden=True,
                        style={'height': '1.5em',
                               'fontSize': '15px',
                               'textAlign': 'center'},
                        children=global_data.fen)

    fen_component.children = [add_buttons, fen_input, fen_text
                              ]
    # fen_pgn_container.children = [fen_component]
    return fen_component  # fen_pgn_container


@app.callback([Output('fen-input', "value"),
               Output('fen-input', 'placeholder'),
               Output('fen-text', 'children'),
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
            return (dash.no_update, dash.no_update, dash.no_update)
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    if fen is None:  # or (add_fen and (fen is None or n_clicks_fen is None)):
        return (dash.no_update, dash.no_update, dash.no_update)

    try:
        global_data.set_fen(fen)
    except ValueError:
        return ('', 'not valid fen', dash.no_update)

    print('setting fen')
    return ('', '', fen)
