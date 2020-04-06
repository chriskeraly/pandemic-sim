import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

import numpy as np
from simulation import  InteractiveSimParam_dayslider
import colorscheme


class AppCreator():

    def __init__(self,simulation, dataPlotter):
        self.simulation = simulation
        self.dataPlotter = dataPlotter

    def create_app_layout(self):
        title = [html.Div(html.H1("COVID-19 Epidemic simulator", style = {"text-align":"center"}), className= "row")]
        note = [html.Div(html.H5("An extremely simple epidemic simulator to look at trends and compare countries", style = {"text-align":"center"}), className="row")]
        line = [html.Div(html.Div(html.Hr(style={"margin-top": "50px","margin-bottom": "0px"})),className='row')]
        sliders_top, sliders_bottom = self.get_sliders()
        # map_graph, line_plot = self.get_graphs()
        country_selector = self.get_country_selector()

        line_plot = self.get_graphs()
        html_div_list_interact = sliders_top + sliders_bottom + country_selector
        thick_line = [html.Div(html.Div(html.Hr(style={"margin-top": "10px","margin-bottom": "10px"})),className='row')]

        html_div_list_results =   line_plot  #+ map_graph

        layout = html.Div([
            html.Div(title + note +  line, className = 'row'),
            html.Div([
                html.Div(html_div_list_interact, className = 'six columns'),
                html.Div(html_div_list_results, className = 'six columns')],
                className= 'row'),
            ]
            ,style = {'margin':'5%'})
        return layout

    def get_graphs(self):
        # return [html.H3("Animation of virus spread with time"),dcc.Graph(id='map graph')], [html.H3("Simulation results" ),dcc.Graph(id="line plot")]
        layout = [html.H3("Simulation results" , className= 'row'),
                  dcc.Graph(id="line plot", className= 'row'),
                  dcc.Graph(id = 'differential line plot', className= 'row')]
        return layout

    def get_country_selector(self):
        countries = self.dataPlotter.get_countries()
        options = [{'label': country, 'value': country} for country in countries]
        return [html.Div([html.Div(html.Hr( style={"margin-top": "0px","margin-bottom": "0px"}),className='row'),
                          html.H3("Country real data overlay"),
            dcc.Dropdown(
                id = 'country selector',
                options = options,
                value = 'China'
            ),
             html.Button('Load Fit for this country', id='load fit'),
        ])]

    def get_sliders(self):
        sliders_sim_params = [#html.Div(html.Div(html.Hr(style={"margin-top": "0px","margin-bottom": "0px"})),className='row'),
                              html.Div(html.H3("Simulation Parameters", className= 'ten columns offset by one'), className = 'row'),
                              html.Div([
                                  html.Div(self.simulation.sim_days.get_widget_with_labels(), className='six columns'),
                                  html.Div(self.simulation.total_population.get_widget_with_labels(), className='six columns')],
                                  className='row'
                              )]



        sliders_epidemic_params = [html.Div(html.Hr( style={"margin-top": "0px","margin-bottom": "0px"}),className='row'),
                                   html.Div(html.H3("Viral Parameters", className= 'ten columns offset by one'), className = 'row'),
                                   html.Div(
                                       [html.Div(self.simulation.R0.get_widget_with_labels(), className='six columns'),
                                        html.Div(html.Div(self.simulation.death_rate.get_widget_with_labels(), style ={ 'vertical-align':'bottom'}), className='six columns')],
                                       className='row'
                                   )]

        sliders_normal_testing_params = [html.Div(html.Hr(style={"margin-top": "0px","margin-bottom": "0px"}),className='row'),
                                         html.Div(html.H3("Normal testing regime Parameters",className= 'twelve columns'), className='row'),
                                         html.Div(
                                             [html.Div(self.simulation.day_of_diagnosis.get_widget_with_labels(),
                                                       className='six columns'),
                                              html.Div(self.simulation.fraction_missed_cases_normal.get_widget_with_labels(),
                                                       className='six columns', style ={ 'vertical-align':'bottom'})],
                                             className='row'
                                         )]

        sliders_intensive_testing = [html.Div(html.Hr(style={"margin-top": "0px","margin-bottom": "0px"}),className='row'),
                                     html.Div(html.H3("Intensive testing regime Parameters", className= 'twelve columns'), className='row'),
                                         html.Div(
                                             [html.Div(self.simulation.day_of_testing.get_widget_with_labels(),
                                                       className='six columns'),
                                              html.Div(self.simulation.fraction_missed_cases.get_widget_with_labels(),
                                                       className='six columns', style ={ 'vertical-align':'bottom'})],
                                             className='row'
                                         ),
                                        html.Div(self.simulation.intensive_testing_window.get_widget_with_labels(), className= 'row')]

        sliders_social_isolation = [html.Div(html.Hr(style={"margin-top": "0px","margin-bottom": "0px"}),className='row'),
                                    html.Div(html.H3("Social Isolation Parameters", className= 'twelve columns'),className='row'),
                                    html.Div(
                                        [html.Div(self.simulation.social_isolation_level.get_widget_with_labels(), className= 'six columns' )] ,
                                        className = 'row'),
                                    html.Div(self.simulation.social_isolation_window.get_widget_with_labels(), className= 'row')]



        sliders_top =sliders_sim_params + sliders_epidemic_params

        sliders_bottom = [html.Div( sliders_normal_testing_params + sliders_intensive_testing +sliders_social_isolation )]

        return sliders_top , sliders_bottom

    def get_outputs(self):
        day_sliders = []
        for k, isp in self.simulation.InteractiveSimParams.items():
            if type(isp) == InteractiveSimParam_dayslider:
                day_sliders.append(dash.dependencies.Output(isp.id, 'max'))

        slider_selected_values = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            slider_selected_values.append(dash.dependencies.Output( isp.id + '_selected_value', 'children'))
        # return day_sliders + slider_selected_values + [dash.dependencies.Output('line plot','figure'),
        #         dash.dependencies.Output('map graph', 'figure')]
        return day_sliders + slider_selected_values + [dash.dependencies.Output('line plot','figure')] + [dash.dependencies.Output('differential line plot','figure')]


    def get_inputs(self):
        inputs = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            inputs.append(dash.dependencies.Input(isp.id, 'value'))
        inputs.append(dash.dependencies.Input('country selector', 'value'))
        return inputs

    def get_preset_button_outputs(self):
        outputs = []
        for k,isp in self.simulation.InteractiveSimParams.items():
            outputs.append(dash.dependencies.Output( isp.id , 'value'))
        return outputs

    def create_preset_button_callback_output(self, country):
        outputs = []
        if not country in self.dataPlotter.presets.keys():
            country = 'NO PRESET FOR COUNTRIES BELLOW THIS LINE'
        for k,isp in self.simulation.InteractiveSimParams.items():
            outputs.append(self.dataPlotter.presets[country][isp.id])
        print(f"Outputs = {outputs}")
        return tuple(outputs)

    def get_preset_button_inputs(self):
        inputs = [dash.dependencies.Input('load fit','n_clicks')]
        inputs.append(dash.dependencies.Input('country selector', 'value'))
        return inputs

    def get_InteractiveSimParam_ids(self):
        return self.simulation.InteractiveSimParams.keys()

    def create_slider_values_output(self):
        slider_selected_values = []
        for k, isp in self.simulation.InteractiveSimParams.items():
            slider_selected_values.append(f"Current value: {isp.val()}")
        return slider_selected_values

    def create_callback_output(self, country):
        day_sliders_max_values = [self.simulation.sim_days.val()] * np.sum([1 if type(isp) == InteractiveSimParam_dayslider else 0 for k,isp in self.simulation.InteractiveSimParams.items()])
        # print(day_sliders_max_values)
        slider_selected_values = self.create_slider_values_output()
        fig = self.create_time_series_output(country)
        diff_fig = self.create_differential_time_series_output(country)
        # map = self.create_map_output()
        # return tuple(day_sliders_max_values + slider_selected_values+ fig+ map)
        return tuple(day_sliders_max_values + slider_selected_values+ fig + diff_fig)#+ map)

    def create_time_series_output(self, country):

        fig = go.Figure()
        fig.add_shape(
            type = "rect",
            x0 = self.simulation.social_isolation_window.val()[0],
            x1 = np.min([self.simulation.social_isolation_window.val()[1],self.simulation.sim_days.val()]),
            y0 = 1,
            y1 = 5*self.simulation.total_population.val(),
            fillcolor="LightSalmon",
            line_width = 0,
            opacity=0.2,
            layer="below"
        )

        fig.add_shape(
            type = "rect",
            x0 = self.simulation.intensive_testing_window.val()[0],
            x1 =  np.min([self.simulation.intensive_testing_window.val()[1],self.simulation.sim_days.val()]),
            y0 = 1,
            y1 = 5*self.simulation.total_population.val(),
            fillcolor="LightSkyBlue",
            line_width = 0,
            opacity=0.2,
            layer="below"
        )

        fig.add_trace(go.Scatter(
            x=[np.mean([self.simulation.social_isolation_window.val()[0],np.min([self.simulation.social_isolation_window.val()[1],self.simulation.sim_days.val()])]),
               np.mean([self.simulation.intensive_testing_window.val()[0],np.min([self.simulation.intensive_testing_window.val()[1],self.simulation.sim_days.val()])])],
            # y=[self.simulation.total_population.val()*2, self.simulation.total_population.val()*2],
            y = [20,20],
            text=["Social Isolation Window",
                  "Intensive testing Window"],
            mode="text",
            showlegend=False
        ))


        fig.add_trace(go.Scatter(
            x=self.simulation.days,
            y=self.simulation.total_infected,
            mode='lines',
            line=dict(color=colorscheme.INFECTED, width=2),
            name='Total Infected (Simulation)',
        ))

        fig.add_trace(go.Scatter(
            x=self.simulation.days,
            y=self.simulation.diagnosed,
            mode='lines',
            line=dict(color=colorscheme.DIAGNOSED, width=2,),
            name='Total Diagnosed (Simulation)',
        ))

        # fig.add_trace(go.Scatter(
        #     x=self.simulation.days,
        #     y=self.simulation.active_cases,
        #     mode='lines',
        #     name='Active cases (Simulation)',
        #     line=dict(color=colorscheme.ACTIVE_CASES, width=2, ),
        # ))

        fig.add_trace(go.Scatter(x=self.simulation.days,
                                 y=self.simulation.dead,  # self.simulation.active_cases,
                                 mode='lines',
                                 line=dict(color=colorscheme.DEAD,width = 2),
                                 name="Total Deaths (Simulation)",
                                 ))
        diagnosed_cases_fig_real , deaths_fig_real = self.dataPlotter.create_scatter( diagnosed_sim = self.simulation.diagnosed, match_offset_days =  10, country = country)

        fig.add_trace(diagnosed_cases_fig_real)
        fig.add_trace(deaths_fig_real)



        fig.update_yaxes(type="log", title="Individuals",
                         range=[np.log10(1),
                                np.log10(5*self.simulation.total_population.val())],
                         tickvals=[10,1e2,1e3,1e4,1e5,1e6,1e7,1e8,1e9],
                         showline = True,
                         linewidth=2,
                         linecolor='black',
                         gridcolor='#8e9aaf')
        fig.update_layout(
            # autosize = False,
            # width = 1200,
            height = 600,
            # legend = {'xanchor': "center",'yanchor': "top"},
            legend = {'orientation' : 'h', 'x':-0.1, 'y':1.3},
            paper_bgcolor= '#FFFFFF',
            template = 'none',#'plotly_white'
            font=dict(
                family="Avenir",
                size=16,
                color="#1f1f1f"
            )
        )
        fig.update_xaxes(title="Days",
                         range=[0, self.simulation.sim_days.val()],
                         showline = True,linewidth=2, linecolor='black',
                         showgrid = False)
        return [fig]




    def create_differential_time_series_output(self, country):

        fig = go.Figure()
        fig.add_shape(
            type="rect",
            x0=self.simulation.social_isolation_window.val()[0],
            x1=np.min([self.simulation.social_isolation_window.val()[1], self.simulation.sim_days.val()]),
            y0=1,
            y1=5 * self.simulation.total_population.val(),
            fillcolor="LightSalmon",
            line_width=0,
            opacity=0.2,
            layer="below"
        )

        fig.add_shape(
            type="rect",
            x0=self.simulation.intensive_testing_window.val()[0],
            x1=np.min([self.simulation.intensive_testing_window.val()[1], self.simulation.sim_days.val()]),
            y0=1,
            y1=5 * self.simulation.total_population.val(),
            fillcolor="LightSkyBlue",
            line_width=0,
            opacity=0.2,
            layer="below"
        )

        fig.add_trace(go.Scatter(
            x=[np.mean([self.simulation.social_isolation_window.val()[0],np.min([self.simulation.social_isolation_window.val()[1],self.simulation.sim_days.val()])]),
               np.mean([self.simulation.intensive_testing_window.val()[0],np.min([self.simulation.intensive_testing_window.val()[1],self.simulation.sim_days.val()])])],
            y=[self.simulation.total_population.val()*2, self.simulation.total_population.val()*2],
            text=["Social Isolation Window",
                  "Intensive testing Window"],
            mode="text",
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=self.simulation.days[1:],
            y=np.diff(self.simulation.total_infected),
            # mode='markers',
            name='New infections per day (Simulation)',
            marker_symbol='circle-open',
            marker_line_width=2,
            marker_color=colorscheme.INFECTED,
            mode='lines',
            line=dict(color=colorscheme.INFECTED, width=2, ),
        ))

        fig.add_trace(go.Scatter(
            x=self.simulation.days[1:],
            y=np.diff(self.simulation.diagnosed),
            # mode='markers',
            name='New Diagnosed cases per day',
            marker_symbol='circle-open',
            marker_line_width=2,
            marker_color=colorscheme.DIAGNOSED,
            mode='lines',
            line=dict(color=colorscheme.DIAGNOSED, width=2, ),
        ))

        fig.add_trace(go.Scatter(x=self.simulation.days[1:],
                                 y=np.diff(self.simulation.dead),  # self.simulation.active_cases,
                                 # mode='markers',
                                 name="New deaths per day",
                                 marker_symbol='circle-open',
                                 marker_line_width=2,
                                 marker_color=colorscheme.DEAD,
                                 mode='lines',
                                 line=dict(color=colorscheme.DEAD, width=2, ),
                                 ))


        diagnosed_cases_fig_real , deaths_fig_real = self.dataPlotter.create_differential_scatter( diagnosed_sim = self.simulation.diagnosed, match_offset_days = 10, country = country)

        fig.add_trace(diagnosed_cases_fig_real)
        fig.add_trace(deaths_fig_real)

        # fig.update_yaxes(type="log", title="individuals",
        #                  range=[np.log10(10), np.log10(5*self.simulation.total_population.val())])
        # fig.update_xaxes(title="days", range=[0, self.simulation.sim_days.val()])

        fig.update_yaxes(type="log", title="Individuals",
                         range=[np.log10(1),
                                np.log10(5 * self.simulation.total_population.val())],
                         tickvals=[10, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9],
                         showline=True, linewidth=2, linecolor='black',
                         gridcolor='#8e9aaf')
        fig.update_layout(
            # autosize = False,
            # width = 1200,
            height = 600,
            # legend = {'xanchor': "center",'yanchor': "top"},
            legend={'orientation': 'h', 'x': -0.1, 'y': 1.3},
            paper_bgcolor='#FFFFFF',
            template='none',  # 'plotly_white'
            font = dict(
                family="Avenir",
                size=16,
                color="#1f1f1f"
            )
        )
        fig.update_xaxes(title="Days",
                         range=[0, self.simulation.sim_days.val()],
                         showline=True, linewidth=2, linecolor='black',
                         showgrid=False)
        return [fig]


    #
    # def create_map_output(self):
    #     slider_steps = []
    #     frames = []
    #     for day, map in enumerate(self.simulation.map):
    #         if day%7 ==0:
    #             slider_step = {'args': [
    #                 [f'frame{day+1}'],
    #                 {'frame': {'duration': 20, 'redraw': False},
    #                  'mode': 'immediate',
    #                  'transition': {'duration': 20}}
    #             ],
    #                 'label': day,
    #                 'method': 'animate'}
    #             slider_steps.append(slider_step)
    #             frames.append(go.Frame(data=go.Heatmap(x=self.simulation.x, y=self.simulation.y, z=map), name=f'frame{day+1}'))
    #
    #     fig = go.Figure(
    #         data=[go.Heatmap(x=self.simulation.x, y=self.simulation.y, z=self.simulation.map[0])],
    #         layout=go.Layout(
    #             yaxis = {'scaleanchor':'x'},
    #             width = 700,
    #             height = 700,
    #             sliders = [ {
    #                     'active': 0,
    #                     'yanchor': 'top',
    #                     'xanchor': 'left',
    #                     'currentvalue': {
    #                         'font': {'size': 20},
    #                         'prefix': 'Day ',
    #                         'visible': True,
    #                         'xanchor': 'right'
    #                     },
    #                     'transition': {'duration': 20, 'easing': 'cubic-in-out'},
    #                     'pad': {'b': 10, 't': 50},
    #                     'len': 0.9,
    #                     'x': 0.1,
    #                     'y': 0,
    #                     'steps': slider_steps
    #                     }],
    #             updatemenus=[dict(
    #                 type="buttons",
    #                 buttons=[dict(label="Play",
    #                               method="animate",
    #                               args =  [None, {"frame": {"duration": 100},
    #                                               "fromcurrent": True, "transition": {"duration": 100,
    #                                                                                   "easing": "quadratic-in-out"}}]
    #                               )])]
    #         ),
    #         frames = frames)
    #     fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 70
    #
    #     # map = go.Figure(go.Heatmap(x=self.simulation.x, y=self.simulation.y, z=self.simulation.get_last_map()))
    #     return [fig]#[map]
