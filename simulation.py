import numpy as np
import copy
from collections import OrderedDict
import dash_core_components as dcc
import dash_html_components as html
from population_manager import Maps, Counters

class InteractiveSimParam():
    def __init__(self, id, min, max, step, default_value, type = "slider", category = None, **kwargs):
        self.type = type
        self.id = id
        self.min = min
        self.max = max
        self.step = step
        self.default_value = default_value
        self.category = category
        self.kwargs = kwargs

    def set_value(self, value):
        self.value = value

    def val(self):
        return copy.deepcopy(self.value)

    def get_widget(self):

        if self.type == 'slider':
            if self.step == 1:

                marks = {int(val): '{:.0f}'.format(int(val / self.step) * self.step) for val in
                         np.linspace(self.min, self.max, 7)}
            else:
                marks = {val: '{:.02f}'.format(int(val / self.step) * self.step) for val in
                         np.linspace(self.min, self.max, 7)}
            if self.id == 'Population Simulated':
                marks = {int(val): '{:.0E}'.format(int(val / self.step) * self.step) for val in
                         np.linspace(self.min, self.max, 7)}
            # print(f"{self.id} marks {marks}")
            return dcc.Slider(id=self.id,
                       min=self.min,
                       max=self.max,
                       step=self.step,
                       value=self.default_value,
                       marks = marks,
                       **self.kwargs)
        if self.type == 'rangeslider':
            if self.step == 1:

                marks = {int(val): '{:.0f}'.format(int(val / self.step) * self.step) for val in
                         np.linspace(self.min, self.max, 20)}
            else:
                marks = {val: '{:.02f}'.format(int(val / self.step) * self.step) for val in
                         np.linspace(self.min, self.max, 20)}
            # print(f"{self.id} marks {marks}")
            return dcc.RangeSlider(id=self.id,
                       min=self.min,
                       max=self.max,
                       step=self.step,
                       value=self.default_value,
                       marks = marks,# {val:'{:.0f}'.format(int(val/self.step) * self.step) for val in np.linspace(self.min,self.max,5)},
                                   )

    def get_widget_with_labels(self):
        widget = []
        widget.append(html.P(self.id))
        widget.append(self.get_widget())
        widget.append(html.Div(id=self.id + '_selected_value'))
        return widget

class InteractiveSimParam_dayslider(InteractiveSimParam):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)





class Simulation():

    def __init__(self):
        print("created simulation")
        self.initial_contamination = 30
        self.illness_duration = 10
        self.incubation_duration = 3
        self.mode = 'counters'
        self.fraction_missed_cases_normal = InteractiveSimParam("Fraction of undiagnosed infections in normal testing regime", 0 , 0.95, 0.01, 0.4)
        self.day_of_diagnosis = InteractiveSimParam('Days during which someone is infected and can spread the disease before they are tested and quarantined (normal testing regime)', 0, self.illness_duration-self.incubation_duration-1, 1, 3)
        self.sim_days = InteractiveSimParam('Simulation duration (days)', 1 , 365, 1, 100, category = 'Simulation parameters')
        self.total_population = InteractiveSimParam('Population Simulated', 10, 1e9, 1, 60e6, category = 'Simulation parameters')
        self.R0 = InteractiveSimParam('R0: With no changes to behavior, how many people will one infected person infect', 0 , 10 , 0.01,4)
        self.death_rate = InteractiveSimParam('Death Rate',0,0.1,0.001,0.01)

        self.social_isolation_window = InteractiveSimParam_dayslider('Social Isolation window period (days)', 0 , 365, 1, [34, 55], type = 'rangeslider')
        self.social_isolation_level = InteractiveSimParam("Fraction of social contact reduction during social isolation", 0 , 1, 0.01, 0.8)

        self.intensive_testing_window = InteractiveSimParam_dayslider('Intensive testing and tracking window period (days)', 0 , 365, 1, [50, 365], type = 'rangeslider')
        self.fraction_missed_cases = InteractiveSimParam("Fraction of undiagnosed infections in spite of intensive testing", 0 , 0.95, 0.01, 0.03)
        self.day_of_testing = InteractiveSimParam("Days during which someone is infected and can spread the disease before they are tested and quarantined (intensive testing regime)", 0 , self.illness_duration-self.incubation_duration-1, 1, 1)


        self.register_InteractiveSimParams()


    def register_InteractiveSimParams(self):

        self.InteractiveSimParams = OrderedDict()
        for id, thing in self.__dict__.items():
            if isinstance(thing, InteractiveSimParam):
                self.InteractiveSimParams[thing.id]=thing

    def run(self):
        self.init_variables()
        self.run_algorithm()
        # print("%d kbytes" % (1e-3 * self.population.maps[-1].size * self.population.maps[-1].itemsize * len(self.population.maps)))

    def init_variables(self):
        self.days = np.arange(self.sim_days.val())
        if self.mode == 'maps':
            self.population_manager = Maps(self.total_population.val(), self.days, self.incubation_duration, self.illness_duration, self.day_of_diagnosis.val())
        if self.mode == 'counters':
            self.population_manager = Counters(self.total_population.val(), self.days, self.incubation_duration, self.illness_duration, self.day_of_diagnosis.val())


    def run_algorithm(self):
        self.population_manager.initialize_first_day(self.initial_contamination, self.fraction_missed_cases_normal.val())
        for i in self.days[1:]:
            self.update_day(i)
        self.get_results()

    def get_results(self):
        self.active_cases = self.population_manager.get_all_active()
        self.dead = self.population_manager.dead
        self.recovered = self.population_manager.recovered
        self.total_infected = self.population_manager.total_infected
        self.diagnosed = self.population_manager.diagnosed

        self.do_averaging()
        # print(f"active{self.active_cases}")
        # print(f"dead{self.dead}")
        # print(f"recovered{self.recovered}")
        # print(f"total_infected{self.total_infected}")
        # print(f"diagnosed{self.diagnosed}")

    def do_averaging(self):
        '''this is a bit of a hack to get smoother plots due to some artifacts in the simulation I don't have the courage to track down right now'''

        def running_mean(x, N):
            cumsum = np.cumsum(np.insert(x, 0, 0))
            temp = list((cumsum[N:] - cumsum[:-N]) / float(N))
            for i in range(N-1):
                temp.append(temp[-1])
            return np.array(temp)

        N = 3

        self.active_cases = running_mean(self.active_cases, N)
        self.dead = running_mean(self.dead,N)
        self.recovered = running_mean(self.recovered,N)
        self.total_infected = running_mean(self.total_infected,N)
        self.diagnosed = running_mean(self.diagnosed,N)




    def update_day(self, day, algorithm = 'random'):

        if algorithm == 'random':
            self.population_manager.initialize_day(day)

            ## Kill people if they have reached the end of the illness and they are unlucky
            self.population_manager.kill_or_recover_end_of_illness(day, self.death_rate.val())


            # Figure out who gets tested and isolated
            if day> self.intensive_testing_window.val()[0] and day < self.intensive_testing_window.val()[1]:

                self.population_manager.test_and_isolate(day, self.day_of_testing.val(), self.fraction_missed_cases.val(), self.death_rate.val())
            else:
                self.population_manager.test_and_isolate(day, self.day_of_diagnosis.val(), self.fraction_missed_cases_normal.val(), self.death_rate.val())

            ## Figure out new contaminations

            if day> self.social_isolation_window.val()[0] and day < self.social_isolation_window.val()[1]:
                Reff = self.R0.val()*(1- self.social_isolation_level.val())
            else:
                Reff = self.R0.val()


            Reff_day = self.fraction_missed_cases_normal.val() *  Reff / (self.day_of_diagnosis.val()) + (1-self.fraction_missed_cases_normal.val()) * Reff / (self.illness_duration - self.incubation_duration)

            self.population_manager.spread_disease(day, Reff_day)

            self.population_manager.end_day(day)


    def get_last_map(self):
        print("%d kbytes" % (1e-3 * self.map[-1].size * self.map[-1].itemsize * len(self.map)))
        return self.map[-1].tolist()



    def set_params(self, sim_params):
        for id, val in sim_params.items():
            self.InteractiveSimParams[id].set_value(val)
