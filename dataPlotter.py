from pandas import read_csv
import datetime
import colorscheme

import plotly.graph_objects as go
import numpy as np



class DataPlotter():
    presets = {'China':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 5,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 1500000,
                    'R0: With no changes to behavior, how many people will one infected person infect': 5.9,
                    'Death Rate': 0.018,
                    'Social Isolation window period (days)': [24, 70],
                    'Intensive testing and tracking window period (days)': [62, 365],
                    "Fraction of social contact reduction during social isolation": 0.9,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.05,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 1
                    },
               'United_States_of_America':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 5,
                    'Simulation duration (days)': 90,
                    'Population Simulated': 200e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 5.11,
                    'Death Rate': 0.013,
                    'Social Isolation window period (days)': [33, 90],
                    'Intensive testing and tracking window period (days)': [100, 100],
                    "Fraction of social contact reduction during social isolation": 0.82,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.03,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    },
               'Italy':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 60e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 4.44,
                    'Death Rate': 0.03,
                    'Social Isolation window period (days)': [29, 100],
                    'Intensive testing and tracking window period (days)': [100, 100],
                    "Fraction of social contact reduction during social isolation": 0.8,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.035,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    },
               'South_Korea':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 5,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 20e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 4,
                    'Death Rate': 0.014,
                    'Social Isolation window period (days)': [0, 100],
                    'Intensive testing and tracking window period (days)': [19, 100],
                    "Fraction of social contact reduction during social isolation": 0.15,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.17,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    },
               'Singapore':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 100,
                    'Population Simulated': 10e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 4,
                    'Death Rate': 0.07,
                    'Social Isolation window period (days)': [0, 35],
                    'Intensive testing and tracking window period (days)': [35, 100],
                    "Fraction of social contact reduction during social isolation": 0.8,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.24,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 1
                    },
               'California':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 5,
                    'Simulation duration (days)': 153,
                    'Population Simulated': 40e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 3.08,
                    'Death Rate': 0.012,
                    'Social Isolation window period (days)': [32, 80],
                    'Intensive testing and tracking window period (days)': [76, 153],
                    "Fraction of social contact reduction during social isolation": 0.73,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.24,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    },
               'California Heard immunity scenario':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 4,
                    'Simulation duration (days)': 160,
                    'Population Simulated': 40e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 3.08,
                    'Death Rate': 0.012,
                    'Social Isolation window period (days)': [63, 96],
                    'Intensive testing and tracking window period (days)': [100, 100],
                    "Fraction of social contact reduction during social isolation": 0.47,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.1,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 1
                    },
               'NO PRESET FOR COUNTRIES BELLOW THIS LINE':
                   {'Fraction of undiagnosed infections in normal testing regime': 0.65,
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
               }

    def __init__(self):

        self.df_countries = self.load_data_countries()
        self.df_states = self.load_data_states()

    def load_data_countries(self):
        return read_csv("data/covid-19-cases-april-20-2020.csv")

    def load_data_states(self):
        return read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')

    def get_countries(self):
        preset_countries =  list(self.presets.keys())

        all_countries = list(self.df_states.state.unique()) + list(self.df_countries.countriesAndTerritories.unique())  + ['NO PRESET FOR COUNTRIES BELLOW THIS LINE']
        for country in preset_countries:
            try:
                all_countries.remove(country)
            except:
                pass


        return preset_countries + all_countries


    def create_scatter(self,diagnosed_sim,  match_offset_days, country = 'United_States_of_America'):
        if 'California' in country:
            country = 'California'
        cases_thresh = diagnosed_sim[match_offset_days]

        if country in list(self.df_countries.countriesAndTerritories.unique()):

            df_country = self.df_countries[self.df_countries['countriesAndTerritories'] == country]
            days = df_country.dateRep
            days = [datetime.datetime.strptime(day,"%d/%m/%Y") for day in days]
            new_cases = df_country.cases.tolist()

            deaths = df_country.deaths.tolist()
            data = list(zip(days, new_cases, deaths))
            data.sort()
            days, new_cases, deaths = zip(*data)

            deaths = np.cumsum(deaths)
            accumulated_cases = np.cumsum(new_cases)

        else:
            df_state = self.df_states[self.df_states['state'] == country]
            days = df_state.date
            days = [datetime.datetime.strptime(day, "%Y-%m-%d") for day in days]
            accumulated_cases = df_state.cases.tolist()

            deaths = df_state.deaths.tolist()
            data = list(zip(days, accumulated_cases, deaths))
            data.sort()
            days, accumulated_cases, deaths = zip(*data)
            deaths = np.array(deaths)
            accumulated_cases = np.array(accumulated_cases)

            new_cases = np.array([0] + list(np.diff(accumulated_cases)))


        above_thresh = accumulated_cases > cases_thresh

        above_thresh[:-match_offset_days] = above_thresh[match_offset_days:]

        deaths_plot = deaths[above_thresh]
        accumulated_cases_plot = accumulated_cases[above_thresh]
        days_plot = np.arange(len(deaths_plot))
        days_plot = np.array(days)[above_thresh]
        # print(country)
        deaths_fig = go.Scatter(x=days_plot,
                                y=deaths_plot,
                                mode='lines',
                                line=dict(color=colorscheme.DEAD, width=2, dash='dashdot'),
                                name=f' Total Deaths (real data for {country})')
        diagnosed_cases_fig = go.Scatter(x=days_plot,
                                         y=accumulated_cases_plot,
                                         mode='lines',
                                         line=dict(color=colorscheme.DIAGNOSED, width=2, dash='dashdot'),
                                        name=f'Total Diagnosed (real data for {country})')
        return diagnosed_cases_fig, deaths_fig, days_plot

    def create_differential_scatter(self,diagnosed_sim,  match_offset_days, country = 'United_States_of_America'):
        if 'California' in country:
            country = 'California'
        cases_thresh = diagnosed_sim[match_offset_days]

        if country in list(self.df_countries.countriesAndTerritories.unique()):

            df_country = self.df_countries[self.df_countries['countriesAndTerritories'] == country]
            days = df_country.dateRep
            days = [datetime.datetime.strptime(day,"%d/%m/%Y") for day in days]
            new_cases = df_country.cases.tolist()

            deaths = df_country.deaths.tolist()
            data = list(zip(days, new_cases, deaths))
            data.sort()
            days, new_cases, deaths = zip(*data)

            deaths = np.cumsum(deaths)
            accumulated_cases = np.cumsum(new_cases)

        else:
            df_state = self.df_states[self.df_states['state'] == country]
            days = df_state.date
            days = [datetime.datetime.strptime(day, "%Y-%m-%d") for day in days]
            accumulated_cases = df_state.cases.tolist()

            deaths = df_state.deaths.tolist()
            data = list(zip(days, accumulated_cases, deaths))
            data.sort()
            days, accumulated_cases, deaths = zip(*data)
            deaths = np.array(deaths)
            accumulated_cases = np.array(accumulated_cases)

            new_cases = np.array([0] + list(np.diff(accumulated_cases)))

        above_thresh = accumulated_cases > cases_thresh

        above_thresh[:-match_offset_days] = above_thresh[match_offset_days:]

        deaths_plot = deaths[above_thresh]

        days_plot = np.array(days)[above_thresh]

        accumulated_cases_plot = accumulated_cases[above_thresh]
        # days_plot = np.arange(len(deaths_plot))
        # print(country)
        deaths_fig = go.Scatter(x=days_plot[1:],
                                y=np.diff(deaths_plot),
                                mode='markers',
                                marker_symbol='x-thin',
                                marker_line_width=2,
                                marker_line_color=colorscheme.DEAD,
                                name=f'New Deaths (real data for {country})')
        diagnosed_cases_fig = go.Scatter(x=days_plot[1:],
                                         y=np.diff(accumulated_cases_plot),
                                         mode='markers',
                                         marker_symbol='x-thin',
                                         marker_line_width=2,
                                         marker_line_color=colorscheme.DIAGNOSED,
                                         name=f'New Diagnosed Cases (real data for {country})')
        return diagnosed_cases_fig, deaths_fig, days_plot



if __name__=='__main__':
    dp = DataPlotter()
    dp.create_scatter('China')