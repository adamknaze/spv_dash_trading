import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import dash_design_kit as ddk
from dash.exceptions import PreventUpdate
from pandas.core.algorithms import mode
import plotly.express as px
import db_utils as utils

from app import dash_app
import app


layout = [
    dcc.ConfirmDialog(
        id='popup-trading-buy',
        message='Nákup nebolo možné uskutočniť :( Ak máte pocit, že by to malo byť možné kontaktujte vedúcich'
    ),
    dcc.ConfirmDialog(
        id='popup-trading-sell',
        message='Predaj nebolo možné uskutočniť :( Ak máte pocit, že by to malo byť možné kontaktujte vedúcich'
    ),
    html.Div(0, id='signal-refresh-buy', style={'display': 'none'}),
    html.Div(0, id='signal-refresh-sell', style={'display': 'none'}),
    html.Div(id='trading-page-content')
]


def serve_layout(logged_in=False, user=None, token=None):

    if logged_in and utils.rds_check_token(app.rds, user, token):
        return [
            ddk.Card([
                ddk.CardHeader('Stav konta'),
                html.Label('Hotovosť na účte'),
                html.H1(
                    '{:.3f}'.format(utils.rds_get_user_cash(app.rds, user, token)) +'$',
                    id='value-h1',
                    style={'text-align': 'center', 'margin-top': '20px', 'margin-bottom': '20px'}
                ),
                html.Label('Vlastnené akcie'),
                ddk.DataTable(
                    id='owned-table',
                    **get_owned_df(user, token)
                )
            ], width=33),
            ddk.Card([
                ddk.CardHeader('Nákup'),
                ddk.ControlCard([
                    ddk.ControlItem(
                        dcc.Dropdown(
                            options=[{'label': cmp, 'value': cmp} for cmp in app.companies],
                            value=app.companies[0],
                            id='dropdown-company-buy'
                        ),
                        label='Spoločnosť:'
                    ),
                    ddk.ControlItem(
                        dcc.Input(
                            id='input-buy-cnt-shares',
                            type='number',
                            placeholder='Zadajte počet akcií',
                        ),
                        label='Počet akcií'
                    ),
                    ddk.ControlItem(
                        html.Button(
                            'Kúpiť',
                            id='button-buy'
                        )
                    )
                ])
            ], width=33),
            ddk.Card([
                ddk.CardHeader('Predaj'),
                ddk.ControlCard([
                    ddk.ControlItem(
                        dcc.Dropdown(
                            options=[{'label': cmp, 'value': cmp}\
                                for cmp in utils.rds_get_user_companies(app.rds, user, token)],
                            value=None,
                            id='dropdown-company-sell'
                        ),
                        label='Spoločnosť:'
                    ),
                    ddk.ControlItem(
                        dcc.Input(
                            id='input-sell-cnt-shares',
                            type='number',
                            placeholder='Zadajte počet akcií',
                        ),
                        label='Počet akcií'
                    ),
                    ddk.ControlItem(
                        html.Button(
                            'Predať',
                            id='button-sell'
                        )
                    )
                ])
            ], width=33),
            ddk.Card([
                ddk.CardHeader('Vývoj hodnoty portfólia'),
                ddk.Block(
                    get_portfolio_graph(user, token),
                    id='portfolio-block'
                )
            ], width=33)
        ]
    else:
        return [
            ddk.Card([
                'Stránka prístupná len po prihlásení'
            ])
        ]


def get_owned_df(user, token):

    user_companies = utils.rds_get_user_companies(app.rds, user, token)
    owned_df = pd.DataFrame(columns=['Spoločnosť'], data=user_companies)

    share_counts = []
    for cmp in user_companies:
        share_counts.append(utils.rds_get_user_cmp_share_cnt(app.rds, user, cmp, token))
    owned_df['Počet akcií'] = share_counts

    prices = app.prices_df.loc[:, user_companies].iloc[-1]
    owned_df['Cena akcie'] = prices.array
    owned_df['Suma'] = owned_df['Počet akcií'] * owned_df['Cena akcie']

    columns_list = [{'name': owned_df.columns[0], 'id': owned_df.columns[0]}]
    columns_list += [{'name': x, 'id': x, 'type': 'numeric', 'format': {'specifier': '.2f'}} for x in owned_df.columns[1:]]
    
    return {'columns': columns_list, 'data': owned_df.to_dict('records')}    


def get_portfolio_graph(user, token):
    
    value_df = utils.rds_get_user_portfolio_df(app.rds, user, token)

    if len(value_df.index) == 0:
        return None
    
    fig = px.line(x=value_df.index, y=value_df.value, title='', color_discrete_sequence=['green'])
    fig.update_traces(line=dict(width=3))
    fig.update_layout(margin=dict(t=35, l=35, r=35, b=35), title_font_size=15, showlegend=False)
    fig.update_yaxes(title='').update_xaxes(title='')
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


@dash_app.callback(
    [Output('signal-refresh-buy', 'children'),
     Output('popup-trading-buy', 'displayed')],
    Input('button-buy', 'n_clicks'),
    [State('signal-refresh-buy', 'children'),
     State('dropdown-company-buy', 'value'),
     State('input-buy-cnt-shares', 'value'),
     State('local-store', 'data')]
)
def buy_shares(_, old_signal, cmp, share_cnt, local_store):

    if cmp is None or share_cnt is None or cmp not in app.companies:
        raise PreventUpdate

    price = app.prices_df[cmp].iloc[-1]
    if utils.rds_buy_shares(app.rds, local_store['user'], cmp, share_cnt, price, local_store['token']):
        return old_signal + 1, False
    else:
        return old_signal, True


@dash_app.callback(
    [Output('signal-refresh-sell', 'children'),
     Output('popup-trading-sell', 'displayed')],
    Input('button-sell', 'n_clicks'),
    [State('signal-refresh-sell', 'children'),
     State('dropdown-company-sell', 'value'),
     State('input-sell-cnt-shares', 'value'),
     State('local-store', 'data')]
)
def sell_shares(_, old_signal, cmp, share_cnt, local_store):

    if cmp is None or share_cnt is None or cmp not in app.companies:
        raise PreventUpdate

    price = app.prices_df[cmp].iloc[-1]
    if utils.rds_sell_shares(app.rds, local_store['user'], cmp, share_cnt, price, local_store['token']):
        return old_signal + 1, False
    else:
        return old_signal, True


@dash_app.callback(
    Output('trading-page-content', 'children'),
    [Input('url', 'pathname'),
     Input('signal-refresh-buy', 'children'),
     Input('signal-refresh-sell', 'children')],
    State('local-store', 'data')
)
def serve_page(url, _, __, local_store):

    if not url == '/trading':
        raise PreventUpdate
    
    if local_store['user'] != 'none':
        return serve_layout(True, local_store['user'], local_store['token'])
    else:
        return serve_layout(False)
