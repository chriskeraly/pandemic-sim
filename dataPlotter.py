from pandas import read_csv
import datetime

import plotly.graph_objects as go
import numpy as np


class DataPlotter():
    def __init__(self):

        self.df = self.load_data()

    def load_data(self):
        return read_csv("data/covid-19-cases-march-30-2020.csv")

    def get_countries(self):
        countries =  self.df.countriesAndTerritories.unique()
        return countries

    def create_scatter(self, country = 'United_States_of_America', cases_thresh = 10):
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
        deaths_plot = deaths[above_thresh]
        accumulated_cases_plot = accumulated_cases[above_thresh]
        days_plot = np.arange(len(deaths_plot))

        deaths_fig = go.Scatter(x=days_plot, y=deaths_plot,mode='markers',
            name=f'Deaths, (real data for {country})')
        diagnosed_cases_fig = go.Scatter(x=days_plot, y=accumulated_cases_plot,mode='markers',
            name=f'Diagnosed Cases, (real data for {country})')
        return diagnosed_cases_fig, deaths_fig



if __name__=='__main__':
    dp = DataPlotter()
    dp.create_scatter('China')