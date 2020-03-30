import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# img_rgb = [[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
#            [[0, 255, 0], [0, 0, 255], [255, 0, 0]]]
class AppCreator():

    def __init__(self,simulation):
        self.simulation = simulation

    def create_app_layout(self):
        html_div_list =  self.get_graphs() + self.get_sliders()
        return html_div_list

    def get_graphs(self):
        return [ dcc.Graph(id='infected_cases'),
            dcc.Graph(id="graph")]

    def get_sliders(self):
        sliders = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            slider = isp.get_widget()

            sliders.append(html.Label(isp.id))
            sliders.append(html.Div(id = isp.id + '_selected_value'))
            sliders.append(slider)

        return sliders

    def get_outputs(self):
        slider_selected_values = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            slider_selected_values.append(dash.dependencies.Output( isp.id + '_selected_value', 'children'))
        return slider_selected_values + [dash.dependencies.Output('graph','figure'),
                dash.dependencies.Output('infected_cases', 'figure')]

    def get_inputs(self):
        inputs = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            inputs.append(dash.dependencies.Input(isp.id, 'value'))
        return inputs

    def get_InteractiveSimParam_ids(self):
        return self.simulation.InteractiveSimParams.keys()

    def create_slider_values_output(self):
        slider_selected_values = []
        for k, isp in self.simulation.InteractiveSimParams.items():
            slider_selected_values.append(f"Simulation running with {isp.val()}")
        return slider_selected_values

    def create_callback_output(self):
        slider_selected_values = self.create_slider_values_output()
        fig = self.create_time_series_output()
        map = self.create_map_output()
        return tuple(slider_selected_values+ fig+ map)

    def create_time_series_output(self):

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.simulation.days,
                                 y=self.simulation.dead,  # self.simulation.active_cases,
                                 mode='markers',
                                 name="Dead",
                                 ))
        fig.add_trace(go.Scatter(
            x=self.simulation.days,
            y=self.simulation.active_cases,
            mode='markers',
            name='Active cases',
        ))
        fig.add_trace(go.Scatter(
            x=self.simulation.days,
            y=self.simulation.total_infected,
            mode='markers',
            name='Total Infected',
        ))

        fig.update_yaxes(type="log", title="individuals",
                         range=[np.log10(1), np.log10(self.simulation.population.val())])
        fig.update_xaxes(title="days")
        return [fig]

    def create_map_output(self):
        slider_steps = []
        frames = []
        for day, map in enumerate(self.simulation.map):
            if day%7 ==0:
                slider_step = {'args': [
                    [f'frame{day+1}'],
                    {'frame': {'duration': 20, 'redraw': False},
                     'mode': 'immediate',
                     'transition': {'duration': 20}}
                ],
                    'label': day,
                    'method': 'animate'}
                slider_steps.append(slider_step)
                frames.append(go.Frame(data=go.Heatmap(x=self.simulation.x, y=self.simulation.y, z=map), name=f'frame{day+1}'))

        fig = go.Figure(
            data=[go.Heatmap(x=self.simulation.x, y=self.simulation.y, z=self.simulation.map[0])],
            layout=go.Layout(
                sliders = [ {
                        'active': 0,
                        'yanchor': 'top',
                        'xanchor': 'left',
                        'currentvalue': {
                            'font': {'size': 20},
                            'prefix': 'Day ',
                            'visible': True,
                            'xanchor': 'right'
                        },
                        'transition': {'duration': 20, 'easing': 'cubic-in-out'},
                        'pad': {'b': 10, 't': 50},
                        'len': 0.9,
                        'x': 0.1,
                        'y': 0,
                        'steps': slider_steps
                        }],
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(label="Play",
                                  method="animate",
                                  args =  [None, {"frame": {"duration": 100},
                                                  "fromcurrent": True, "transition": {"duration": 100,
                                                                                      "easing": "quadratic-in-out"}}]
                                  )])]
            ),
            frames = frames)
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 70

        # map = go.Figure(go.Heatmap(x=self.simulation.x, y=self.simulation.y, z=self.simulation.get_last_map()))
        return [fig]#[map]
