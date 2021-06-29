import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL

import dash_design_kit as ddk
from dash.exceptions import PreventUpdate
from dash import callback_context
import db_utils as utils

from app import dash_app
import app


layout = [
    dcc.ConfirmDialog(
        id='popup',
        message='Zadané meno alebo heslo sú zle. Alebo aj oboje. Skús znova.'
    ),
    ddk.ControlCard(
        id='log-control-card'
    )
]


def serve_log_controls(login=True):

    if login:
        return html.Div(
            children=[
                ddk.ControlItem(
                    dcc.Input(
                        placeholder='Prihlasovacie meno',
                        id={'type': 'input-login', 'index': 0},
                        type='text'
                    )
                ),
                ddk.ControlItem(
                    dcc.Input(
                        placeholder='Heslo',
                        id={'type': 'input-pass', 'index': 0},
                        type='password'
                    )
                ),
                ddk.ControlItem(
                    html.Button(
                        'Prihlásiť',
                        id={'type': 'button-login', 'index': 0}
                    )
                )
            ]
        )

    else:
        return html.Div(
            children=[
                ddk.ControlItem(
                    html.Button(
                        'Odhlásiť',
                        id={'type': 'button-logout', 'index': 0}
                    )
                )
            ]
        )


@dash_app.callback(
    Output('log-control-card', 'children'),
    [Input('url', 'pathname'),
     Input('local-store', 'data')]
)
def serve_layout(url, local_store):

    if not url == '/login':
        raise PreventUpdate

    if local_store['user'] != 'none':
        return serve_log_controls(login=False)
    else:
        return serve_log_controls(login=True)


@dash_app.callback(
    [Output('local-store', 'data'),
     Output('popup', 'displayed')],
    [Input({'type': 'button-login', 'index': ALL}, 'n_clicks'),
     Input({'type': 'button-logout', 'index': ALL}, 'n_clicks')],
    [State({'type': 'input-login', 'index': ALL}, 'value'),
     State({'type': 'input-pass', 'index': ALL}, 'value'),
     State('local-store', 'data')],
     prevent_initial_call=True
)
def try_login(login_clicks, logout_clicks, login, passw, local_store):

    ctx = callback_context

    if ctx.triggered[0]['prop_id'] == '{"index":0,"type":"button-login"}.n_clicks':

        if login_clicks[0] is None or login[0] is None or passw[0] is None:
            raise PreventUpdate

        login_res = utils.rds_check_pass_generate_token(app.rds, login[0], passw[0])
        if login_res is None:
            return local_store, True

        local_store['user'] = login[0]
        local_store['token'] = login_res
        return local_store, False

    elif ctx.triggered[0]['prop_id'] == '{"index":0,"type":"button-logout"}.n_clicks':

        if logout_clicks[0] is None:
            raise PreventUpdate

        local_store['user'] = 'none'
        local_store['token'] = 'none'
        return local_store, False

    else:
        raise PreventUpdate
