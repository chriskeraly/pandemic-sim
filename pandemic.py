import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import numpy as np

app = dash.Dash()

days = np.arange(1,365)

app.layout = html.Div([
    dcc.Graph(
        id='infected_cases'
    ),
    dcc.Slider(
        id='R0',
        min=0,
        max=20,
        step=0.1,
        value=4,
    )]
)


def create_time_series(R0):
    xaxis_type = 'Linear'
    yaxis_type = 'Log'
    return {
        'data': [dict(
            x = days,
            y = np.exp(R0/14*days),
            mode='markers',
            marker = {
            'size': 15,
            'opacity': 0.5,
            'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            xaxis={
                'title': 'days',
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': 'infected_people',
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('infected_cases', 'figure'),
    [dash.dependencies.Input('R0','value')]
)
def update_infected_cases(R0):
    return create_time_series(R0)

if __name__ == '__main__':
    app.run_server()