import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_design_kit as ddk
from dash.exceptions import PreventUpdate
import datetime
import pandas as pd
import numpy as np

from app import dash_app
import app
import page_main
import page_trading
import page_login
import db_utils as utils
from theme import theme


def serve_layout():

    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='local-store', storage_type='local', data={'user': 'none', 'token': 'none'}),
        dcc.Interval(id='update-interval', interval=30 * 1000),
        html.Div('', id='fake-output', style={'display': 'none'}),
        html.Div(0, id='local-last-row', style={'display': 'none'}),

        ddk.App(
            [
                ddk.Header([
                    ddk.Logo(src='assets/logo.png'),
                    ddk.Title('Wellz Faargo Brokers'),
                    ddk.Menu([
                        dcc.Link('Vývoj cien', href='/'),
                        dcc.Link('Obchodovanie', href='/trading'),
                        dcc.Link('Prihlásenie', href='/login', id='login-link-name')
                    ]),
                ]),
                html.Div(id='page-content')
            ],
            show_editor=False,
            theme=theme
        )
    ])


dash_app.layout = serve_layout()


@dash_app.callback(
    Output('fake-output', 'children'),
    Input('update-interval', 'n_intervals')
)
def update_prices_df(_):

    if app.last_prices_update + app.UPDATE_COOLDOWN > datetime.datetime.now():
        raise PreventUpdate

    app.last_prices_update = datetime.datetime.now()

    rds_last_row = utils.rds_get_last_row(app.rds)

    if rds_last_row == app.global_last_row:
        raise PreventUpdate

    for i in range(app.global_last_row, rds_last_row):
        row = [x.decode('utf-8') for x in app.rds.lrange('row_'+str(i), 0, -1)]
        app.prices_df.loc[pd.to_datetime(row[0]), :] = np.array(row[1:]).astype(float)

    app.global_last_row = rds_last_row
    return ''


@dash_app.callback(
    Output('login-link-name', 'children'),
    Input('local-store', 'data')
)
def set_login_link_name(local_store):

    if local_store['user'] == 'none':
        return 'Prihlásenie'
    else:
        return '(' + local_store['user'] + ') Odhlásenie'


@dash_app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/trading':
        return page_trading.layout
    elif pathname == '/login':
        return page_login.layout
    else:
        return page_main.layout


if __name__ == '__main__':
    dash_app.run_server(debug=True)
