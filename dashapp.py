import dash
import dash_core_components as dcc
import dash_html_components as html

from AppCreator import AppCreator
from simulation import Simulation
from dataPlotter import DataPlotter

import time

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

base_simulation = Simulation()
dataPlotter = DataPlotter()
creator = AppCreator(base_simulation, dataPlotter)

app.layout = html.Div(creator.create_app_layout(), style ={'max-width':"1000px"})

@app.callback(
    creator.get_outputs(),
    creator.get_inputs()
)
def update_infected_cases(*args):
    simulation = Simulation()
    ids = creator.get_InteractiveSimParam_ids()
    sim_params = dict(zip(ids, args[:-1]))\

    simulation.set_params(sim_params)
    start = time.time()
    simulation.run()
    sim_done =time.time()
    country = args[-1]
    callback_out =  AppCreator(simulation, dataPlotter).create_callback_output(country)
    callback_done = time.time()
    print(f'Simulation ran in {(sim_done-start)}')
    print(f'Callbacks created in {(callback_done-start)}')
    return callback_out


if __name__ == '__main__':
    app.run_server()#debug = True)        return tuple(day_sliders_max_values + slider_selected_values+ fig+ map)
