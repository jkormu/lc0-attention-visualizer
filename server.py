import dash
from os.path import join
from constants import ROOT_DIR

app = dash.Dash(__name__, assets_folder=join(ROOT_DIR, 'assets'), update_title=None)
#app.config['suppress_callback_exceptions'] = True
app.title = 'LC0 attention'