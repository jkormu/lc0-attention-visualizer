import dash

def callback_triggered_by():
    triggerers = dash.callback_context.triggered
    if triggerers:
        return triggerers[0]['prop_id']
    else:
        return None

