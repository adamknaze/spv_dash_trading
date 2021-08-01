import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_design_kit as ddk
from dash.exceptions import PreventUpdate
from pandas.core.algorithms import mode
import plotly.express as px
import db_utils as utils

from app import dash_app
import app


layout = [
    html.Div(id='values-page-content')
]


def get_portfolios_graph():
    
    values_df = utils.rds_get_all_portfolios_df(app.rds)

    if len(values_df.index) == 0:
        return None
    
    fig = px.line(values_df, title='')#, color_discrete_sequence=['green'])
    fig.update_traces(line=dict(width=3))
    fig.update_layout(margin=dict(t=35, l=35, r=35, b=35), title_font_size=15)
    fig.update_yaxes(title='').update_xaxes(title='')
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


@dash_app.callback(
    Output('values-page-content', 'children'),
    Input('url', 'pathname'),
    State('local-store', 'data')
)
def serve_page(url, local_store):

    if not url == '/values':
        raise PreventUpdate

    if local_store['user'] != 'veduci':
        return ddk.Card(['Stránka len pre vedúcich'])

    return ddk.Card(
        [
            ddk.CardHeader('Vývoj hodnôt portfólií'),
            ddk.Block(
                get_portfolios_graph(),
                id='portfolios-block'
            )
        ], width=95
    )
