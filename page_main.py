import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_design_kit as ddk
from dash.exceptions import PreventUpdate
from dash import callback_context
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app import dash_app
import app

COL_LIST = px.colors.qualitative.Dark24


layout = [
    dcc.Interval(id='graph-update-interval', interval=10 * 1000),
    ddk.Card([
        html.Div(id='graph-div')
    ])
]


@dash_app.callback(
    [Output('graph-div', 'children'),
     Output('local-last-row', 'children')],
    Input('graph-update-interval', 'n_intervals'),
    State('local-last-row', 'children')
)
def generate_graphs(_, local_last_row):

    ctx = callback_context

    if local_last_row == app.global_last_row and len(ctx.triggered) > 0 and ctx.triggered[0]['value'] != None:
        raise PreventUpdate

    companies = app.prices_df.columns
    df_min, df_max = app.prices_df.values.min(), app.prices_df.values.max()

    # fig = px.line(app.prices_df, title='', color_discrete_sequence=['lightgrey'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col in companies:
        fig.add_trace(
            go.Scatter(
                x=app.prices_df.index, y=app.prices_df[col],
                name='', line_color='lightgrey', mode='lines',
                hovertemplate=None, hoverinfo='skip'
            ),
            secondary_y=False
        )

    graphs = []
    for i, cmp in enumerate(companies):
        fig_cmp = go.Figure(fig)
        fig_cmp.add_trace(
            go.Scatter(
                y=list(app.prices_df[cmp]), x=app.prices_df.index,
                mode="lines", name='', line_color=COL_LIST[i % len(COL_LIST)],
                line_width=3
            ),
            secondary_y=True
        )
        fig_cmp.update_layout(
            margin=dict(t=35, l=35, r=35, b=35),
            title_font_size=15,
            showlegend=False,
            title=cmp,
            yaxis=dict(range=[0.9 * df_min, 1.1 * df_max], title=''),
            yaxis2=dict(range=[0.9 * df_min, 1.1 * df_max], scaleanchor = 'y1', visible=False)
        )

        graph = dcc.Graph(figure=fig_cmp, style={'height':'250px'}, config={'displayModeBar': False})
        graphs.append(graph)

    return [ddk.Block(graph, style={'width':'300px'}) for graph in graphs], app.global_last_row
