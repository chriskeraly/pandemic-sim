from simulation import Simulation
from AppCreator import AppCreator
from dataPlotter import DataPlotter
import chart_studio.plotly as py
import plotly.io as pio

dataplotter = DataPlotter()
simulation = Simulation()


appcreator = AppCreator(simulation,dataplotter)


#HEARD IMMUNITY WITH SOCIAL ISOLATION
appcreator.simulation.set_params(appcreator.dataPlotter.presets['California Heard immunity scenario'])
appcreator.simulation.run()
tot_pop = appcreator.simulation.total_population.val()
tot_inf = appcreator.simulation.total_infected[-1]
fig = appcreator.create_time_series_output('California Heard immunity scenario', add_real=False)[0]
fig.update_yaxes({'type': 'linear',
                                         'title': "Percentage of Population",
                                         'range': [1,
                                                   1.2 * tot_inf],
                                         'tickvals': [ tot_inf*0.2, tot_inf*0.4, tot_inf*0.6, tot_inf*0.8, tot_inf ],
                                         'ticktext' : [f'{val*100/tot_pop:0.2f}%' for val in [tot_inf*0.2, tot_inf*0.4, tot_inf*0.6, tot_inf*0.8, tot_inf ] ],
                                         'showline': True,
                                         'linewidth': 2,
                                         'linecolor': 'black',
                                         'gridcolor': '#8e9aaf'
                                         })
fig.layout.legend.y =1.15
fig.layout.margin.update( dict(l=20, r=20, t=80, b=50))
fig.layout.updatemenus[0].y = 1.05
# fig.show()
pio.write_html(fig,file='html_plots/California_heard_immunity.html', auto_open=True)
quit()
# py.plot(fig, filename = 'California Heard immunity scenario',auto_open=False)
print('published 1')

## HEARD IMMUNITY NO SOCIAL ISOALTION
presets = appcreator.dataPlotter.presets['California Heard immunity scenario']
presets['Social Isolation window period (days)']= [96, 96]
appcreator.simulation.set_params(presets)
appcreator.simulation.run()
fig = appcreator.create_time_series_output('California Heard immunity scenario', add_real=False)[0]
tot_pop = appcreator.simulation.total_population.val()
tot_inf = appcreator.simulation.total_infected[-1]
fig.update_yaxes({'type': 'linear',
                                         'title': "Percentage of Population",
                                         'range': [1,
                                                   1.2 * tot_inf],
                                         'tickvals': [ tot_inf*0.2, tot_inf*0.4, tot_inf*0.6, tot_inf*0.8, tot_inf ],
                                         'ticktext' : [f'{val*100/tot_pop:0.2f}%' for val in [tot_inf*0.2, tot_inf*0.4, tot_inf*0.6, tot_inf*0.8, tot_inf ] ],
                                         'showline': True,
                                         'linewidth': 2,
                                         'linecolor': 'black',
                                         'gridcolor': '#8e9aaf'
                                         })
fig.layout.legend.y =1.15

fig.layout.margin.update( dict(l=20, r=20, t=80, b=50))

# fig.show()
# py.plot(fig, filename = 'California Heard immunity scenario, no social isolation',auto_open=True)
print('2')
## CALIFORNIA No testing
presets = {'Fraction of undiagnosed infections in normal testing regime': 0.65,
                    'Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)': 5,
                    'Simulation duration (days)': 120,
                    'Population Simulated': 40e6,
                    'R0: With no changes to behavior, how many people will one infected person infect': 3.08,
                    'Death Rate': 0.012,
                    'Social Isolation window period (days)': [31, 80],
                    'Intensive testing and tracking window period (days)': [120, 120],
                    "Fraction of social contact reduction during social isolation": 0.75,
                    'Fraction of undiagnosed infections in spite of intensive testing': 0.24,
                    "Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)": 0
                    }

appcreator.simulation.set_params(presets)
appcreator.simulation.run()
fig = appcreator.create_time_series_output('California', add_real=True)[0]
fig.layout.legend.y =1.15

fig.layout.margin.update( dict(l=20, r=20, t=80, b=50))


# fig.show()
#py.plot(fig, filename = 'California Heard immunity scenario, no Testing',auto_open=False)

fig = appcreator.create_differential_time_series_output('California')[0]
# fig.show()
fig.layout.margin.update( dict(l=20, r=20, t=80, b=50))

#py.plot(fig, filename = 'California Heard immunity scenario, no Testing, differential',auto_open=False)


## CALIFORNIA 76% signup
presets = appcreator.dataPlotter.presets['California']
appcreator.simulation.set_params(presets)
appcreator.simulation.run()
fig = appcreator.create_time_series_output('California', add_real=True)[0]
fig.layout.legend.y =1.15
fig.layout.margin.update( dict(l=20, r=20, t=80, b=50))

#py.plot(fig, filename = 'California 76 percent signup',auto_open=False)

# fig.show()

## CALIFORNIA 90% signup
presets = appcreator.dataPlotter.presets['California']
presets["Fraction of undiagnosed infections in spite of intensive testing"]= 0.1
appcreator.simulation.set_params(presets)
appcreator.simulation.run()
fig = appcreator.create_time_series_output('California', add_real=True)[0]
# fig.show()
fig.layout.legend.y =1.15
fig.layout.margin.update( dict(l=20, r=20, t=80, b=50))

#py.plot(fig, filename = 'California 90 percent signup',auto_open=False)


## CALIFORNIA 50% signup
presets = appcreator.dataPlotter.presets['California']
presets["Fraction of undiagnosed infections in spite of intensive testing"]= 0.5

appcreator.simulation.set_params(presets)
appcreator.simulation.run()
fig = appcreator.create_time_series_output('California', add_real=True)[0]
# fig.show()
fig.layout.legend.y =1.15
fig.layout.margin.update( dict(l=20, r=20, t=80, b=50))

py.plot(fig, filename = 'California 50 percent signup',auto_open=True)
