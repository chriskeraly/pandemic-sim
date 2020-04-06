from pandas import read_csv
import datetime
import colorscheme

import plotly.graph_objects as go
import numpy as np



class DataPlotter():
    presets = {'China':
                   {'Fraction of undiagnosed infections before intensive testing': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 1500000,
                    'R0: With no changes to behavior, how many people will one infected person infect': 5.3,
                    'Death Rate': 0.02,
                    'Social Isolation window period (days)': [18, 70],
                    'Intensive testing and tracking window period (days)': [62, 365],
                    "Fraction of social contact reduction during social isolation": 0.9,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.05,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 1
                    },
               'United_States_of_America':
                   {'Fraction of undiagnosed infections before intensive testing': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 200e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 3.86,
                    'Death Rate': 0.013,
                    'Social Isolation window period (days)': [25, 55],
                    'Intensive testing and tracking window period (days)': [50, 365],
                    "Fraction of social contact reduction during social isolation": 0.82,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.03,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    },
               'Italy':
                   {'Fraction of undiagnosed infections before intensive testing': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 200e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 4,
                    'Death Rate': 0.028,
                    'Social Isolation window period (days)': [22, 55],
                    'Intensive testing and tracking window period (days)': [100, 365],
                    "Fraction of social contact reduction during social isolation": 0.8,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.03,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    },
               'South_Korea':
                   {'Fraction of undiagnosed infections before intensive testing': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 200e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 4,
                    'Death Rate': 0.014,
                    'Social Isolation window period (days)': [0, 100],
                    'Intensive testing and tracking window period (days)': [12, 100],
                    "Fraction of social contact reduction during social isolation": 0.15,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.13,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    },
               'Singapore':
                   {'Fraction of undiagnosed infections before intensive testing': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 200e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 4,
                    'Death Rate': 0.014,
                    'Social Isolation window period (days)': [0, 17],
                    'Intensive testing and tracking window period (days)': [6, 100],
                    "Fraction of social contact reduction during social isolation": 0.8,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.1,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 1
                    },
               }

    def __init__(self):

        self.df = self.load_data()

    def load_data(self):
        return read_csv("data/covid-19-cases-april-4-2020.csv")

    def get_countries(self):
        countries =  self.presets.keys()#self.df.countriesAndTerritories.unique()

        return countries

    def create_scatter(self,diagnosed_sim,  match_offset_days, country = 'United_States_of_America'):
        cases_thresh = diagnosed_sim[match_offset_days]
        df_country = self.df[self.df['countriesAndTerritories'] == country]
        days = df_country.dateRep
        days = [datetime.datetime.strptime(day,"%d/%m/%Y") for day in days]
        new_cases = df_country.cases.tolist()

        deaths = df_country.deaths.tolist()
        data = list(zip(days, new_cases, deaths))
        data.sort()
        days, new_cases, deaths = zip(*data)


        deaths = np.cumsum(deaths)
        accumulated_cases = np.cumsum(new_cases)
        above_thresh = accumulated_cases > cases_thresh

        above_thresh[:-match_offset_days] = above_thresh[match_offset_days:]

        deaths_plot = deaths[above_thresh]
        accumulated_cases_plot = accumulated_cases[above_thresh]
        days_plot = np.arange(len(deaths_plot))
        # print(country)
        deaths_fig = go.Scatter(x=days_plot,
                                y=deaths_plot,
                                mode='lines',
                                line=dict(color=colorscheme.DEAD, width=2, dash='dashdot'),
                                name=f' Total Deaths, (real data for {country})')
        diagnosed_cases_fig = go.Scatter(x=days_plot,
                                         y=accumulated_cases_plot,
                                         mode='lines',
                                         line=dict(color=colorscheme.DIAGNOSED, width=2, dash='dashdot'),
                                        name=f'Total Diagnosed, (real data for {country})')
        return diagnosed_cases_fig, deaths_fig

    def create_differential_scatter(self,diagnosed_sim,  match_offset_days, country = 'United_States_of_America'):
        cases_thresh = diagnosed_sim[match_offset_days]
        df_country = self.df[self.df['countriesAndTerritories'] == country]
        days = df_country.dateRep
        days = [datetime.datetime.strptime(day,"%d/%m/%Y") for day in days]
        new_cases = df_country.cases.tolist()

        deaths = df_country.deaths.tolist()
        data = list(zip(days, new_cases, deaths))
        data.sort()
        days, new_cases, deaths = zip(*data)


        deaths = np.cumsum(deaths)
        accumulated_cases = np.cumsum(new_cases)
        above_thresh = accumulated_cases > cases_thresh

        above_thresh[:-match_offset_days] = above_thresh[match_offset_days:]

        deaths_plot = deaths[above_thresh]
        accumulated_cases_plot = accumulated_cases[above_thresh]
        days_plot = np.arange(len(deaths_plot))
        # print(country)
        deaths_fig = go.Scatter(x=days_plot[1:],
                                y=np.diff(deaths_plot),
                                mode='markers',
                                marker_symbol='x-thin',
                                marker_line_width=2,
                                marker_line_color=colorscheme.DEAD,
                                name=f'New Deaths, (real data for {country})')
        diagnosed_cases_fig = go.Scatter(x=days_plot[1:],
                                         y=np.diff(accumulated_cases_plot),
                                         mode='markers',
                                         marker_symbol='x-thin',
                                         marker_line_width=2,
                                         marker_line_color=colorscheme.DIAGNOSED,
                                         name=f'Diagnosed Cases, (real data for {country})')
        return diagnosed_cases_fig, deaths_fig



if __name__=='__main__':
    dp = DataPlotter()
    dp.create_scatter('China')