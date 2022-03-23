from dash import dcc, html, Input, Output, State
from server import app


def mode_selector():
    mode_selector_container = html.Div()
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