import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from simulation import  InteractiveSimParam_dayslider
# img_rgb = [[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
#            [[0, 255, 0], [0, 0, 255], [255, 0, 0]]]
class AppCreator():

    def __init__(self,simulation):
        self.simulation = simulation

    def create_app_layout(self):
        title = [html.H1("COVID-19 Epidemic simulator")]
        note = [html.H5("Please wait a couple seconds after moving a slider, as simulation can take a few seconds with a large population size")]
        sliders_top, sliders_bottom = self.get_sliders()
        map_graph, line_plot = self.get_graphs()
        html_div_list = title + note + sliders_top + sliders_bottom + line_plot + map_graph
        return html_div_list

    def get_graphs(self):
        return [html.H2("Animation of virus spread with time"),dcc.Graph(id='map graph')], [html.H2("Simulation results" ),dcc.Graph(id="line plot")]

    def get_sliders_(self):
        sliders = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            slider = isp.get_widget()

            sliders.append(html.Label(isp.id))
            sliders.append(html.Div(id = isp.id + '_selected_value'))
            sliders.append(slider)





        return sliders

    def get_sliders(self):
        sliders_sim_params = [html.Div(html.H2("Simulation Parameters"))]
        sliders_sim_params.append(html.Div(self.simulation.sim_days.get_widget_with_labels(), style={'width': '48%', 'display': 'inline-block'}))
        sliders_sim_params.append(html.Div(self.simulation.population.get_widget_with_labels(), style={'width': '48%', 'float': 'right', 'display': 'inline-block'}))

        sliders_epidemic_params = [html.Div(html.H2("Viral Parameters"))]
        sliders_epidemic_params.append(html.Div(self.simulation.R0.get_widget_with_labels(),
                                           style={'width': '48%', 'display': 'inline-block'}))
        sliders_epidemic_params.append(html.Div(self.simulation.death_rate.get_widget_with_labels(),
                                           style={'width': '48%', 'float': 'right', 'display': 'inline-block'}))

        sliders_top = [html.Div(sliders_sim_params + sliders_epidemic_params)]

        sliders_social_isolation = []
        sliders_social_isolation.append(html.Div(html.H2("Social Isolation parameters"),style={'width': '48%', 'display': 'inline-block'}))
        sliders_social_isolation.append(html.Div(self.simulation.social_isolation_level.get_widget_with_labels(), style={'width': '48%', 'float': 'right', 'display': 'inline-block'}))
        sliders_social_isolation.append(html.Div(self.simulation.social_isolation_window.get_widget_with_labels()))

        sliders_intensive_testing = []
        sliders_intensive_testing.append(html.Div(html.H2("Intensive Testing parameters")))
        sliders_intensive_testing.append(html.Div(self.simulation.day_of_testing.get_widget_with_labels(),
                                           style={'width': '48%', 'display': 'inline-block'}))
        sliders_intensive_testing.append(html.Div(self.simulation.fraction_missed_cases.get_widget_with_labels(),
                                           style={'width': '48%', 'float': 'right', 'display': 'inline-block'}))
        sliders_intensive_testing.append(html.Div(self.simulation.intensive_testing_window.get_widget_with_labels()))

        sliders_bottom = [html.Div(sliders_social_isolation + sliders_intensive_testing)]

        return sliders_top , sliders_bottom

    def get_outputs(self):
        day_sliders = []
        for k, isp in self.simulation.InteractiveSimParams.items():
            if type(isp) == InteractiveSimParam_dayslider:
                day_sliders.append(dash.dependencies.Output(isp.id, 'max'))

        slider_selected_values = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            slider_selected_values.append(dash.dependencies.Output( isp.id + '_selected_value', 'children'))
        return day_sliders + slider_selected_values + [dash.dependencies.Output('line plot','figure'),
                dash.dependencies.Output('map graph', 'figure')]

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
            slider_selected_values.append(f"Current value: {isp.val()}")
        return slider_selected_values

    def create_callback_output(self):
        day_sliders_max_values = [self.simulation.sim_days.val()] * np.sum([1 if type(isp) == InteractiveSimParam_dayslider else 0 for k,isp in self.simulation.InteractiveSimParams.items()])
        print(day_sliders_max_values)
        slider_selected_values = self.create_slider_values_output()
        fig = self.create_time_series_output()
        map = self.create_map_output()
        return tuple(day_sliders_max_values + slider_selected_values+ fig+ map)

    def create_time_series_output(self):

        fig = go.Figure()
        fig.add_shape(
            type = "rect",
            x0 = self.simulation.social_isolation_window.val()[0],
            x1 = np.min([self.simulation.social_isolation_window.val()[1],self.simulation.sim_days.val()]),
            y0 = 1,
            y1 = self.simulation.population.val(),
            fillcolor="LightSalmon",
            line_width = 0,
            opacity=0.5,
            layer="below"
        )

        fig.add_shape(
            type = "rect",
            x0 = self.simulation.intensive_testing_window.val()[0],
            x1 =  np.min([self.simulation.intensive_testing_window.val()[1],self.simulation.sim_days.val()]),
            y0 = 1,
            y1 = self.simulation.population.val(),
            fillcolor="LightSkyBlue",
            line_width = 0,
            opacity=0.5,
            layer="below"
        )

        fig.add_trace(go.Scatter(
            x=[np.mean([self.simulation.social_isolation_window.val()[0],np.min([self.simulation.social_isolation_window.val()[1],self.simulation.sim_days.val()])]),
               np.mean([self.simulation.intensive_testing_window.val()[0],np.min([self.simulation.intensive_testing_window.val()[1],self.simulation.sim_days.val()])])],
            y=[self.simulation.population.val()/2, self.simulation.population.val()/2],
            text=["Social Isolation Window",
                  "Intensive testing Window"],
            mode="text",
        ))

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
        fig.update_xaxes(title="days", range=[0, self.simulation.sim_days.val()])
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
                yaxis = {'scaleanchor':'x'},
                width = 700,
                height = 700,
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
