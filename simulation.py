import numpy as np
import copy
from collections import OrderedDict
import dash_core_components as dcc
import dash_html_components as html
from maps import Maps

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

            return dcc.Slider(id=self.id,
                       min=self.min,
                       max=self.max,
                       step=self.step,
                       value=self.default_value,
                       marks = {val:'{:.2f}'.format(val) for val in np.linspace(self.min,self.max,10)},
                       **self.kwargs)
        if self.type == 'rangeslider':
            return dcc.RangeSlider(id=self.id,
                       min=self.min,
                       max=self.max,
                       step=self.step,
                       value=self.default_value,
                    marks = {val:'{:.2f}'.format(val) for val in np.linspace(self.min,self.max,10)},
                                   )

    def get_widget_with_labels(self):
        widget = []
        widget.append(html.H6(self.id))
        widget.append(self.get_widget())
        widget.append(html.Div(id=self.id + '_selected_value'))
        return widget

class InteractiveSimParam_dayslider(InteractiveSimParam):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)





class Simulation():

    def __init__(self):
        print("created simulation")
        self.initial_contamination = 100
        self.illness_duration = 10
        self.incubation_duration = 3
        self.day_of_diagnosis = InteractiveSimParam('Day of Diagnosis after infection', 1, 10, 1, 7)
        self.sim_days = InteractiveSimParam('Simulation duration (days)', 1 , 365, 1, 100, category = 'Simulation parameters')
        self.population = InteractiveSimParam('Population Simulated', 10, 1000000, 1, 150000, category = 'Simulation parameters')
        self.R0 = InteractiveSimParam('R0: With no changes to behavior, how many people will one infected person infect', 0 , 10 , 0.01,4)
        self.death_rate = InteractiveSimParam('Death Rate',0,0.1,0.001,0.01)

        self.social_isolation_window = InteractiveSimParam_dayslider('Social Isolation window period (days)', 0 , 365, 1, [34, 55], type = 'rangeslider')
        self.social_isolation_level = InteractiveSimParam("Fraction of social contact reduction during social isolation", 0 , 1, 0.01, 0.8)

        self.intensive_testing_window = InteractiveSimParam_dayslider('Intensive testing and tracking window period (days)', 0 , 365, 1, [50, 365], type = 'rangeslider')
        self.fraction_missed_cases = InteractiveSimParam("Fraction of undiagnosed infections in spite of intensive testing", 0 , 1, 0.01, 0.03)
        self.day_of_testing = InteractiveSimParam("Days during which someone is infected and can spread the disease before they are tested and quarantined", 1 , self.illness_duration, 1, 1)


        self.register_InteractiveSimParams()


    def register_InteractiveSimParams(self):

        self.InteractiveSimParams = OrderedDict()
        for id, thing in self.__dict__.items():
            if isinstance(thing, InteractiveSimParam):
                self.InteractiveSimParams[thing.id]=thing

    def run(self):
        self.init_variables()
        self.run_algorithm()
        print("%d kbytes" % (1e-3 * self.maps.maps[-1].size * self.maps.maps[-1].itemsize * len(self.maps.maps)))

    def init_variables(self):
        self.days = np.arange(self.sim_days.val())
        self.maps = Maps(self.population.val(), self.days, self.incubation_duration, self.illness_duration, self.day_of_diagnosis.val())


    def run_algorithm(self):
        self.maps.initialize_first_day(self.initial_contamination)
        for i in self.days[1:]:
            self.update_day(i)
        self.get_results()

    def get_results(self):
        self.active_cases = self.maps.active
        self.dead = self.maps.dead
        self.recovered = self.maps.recovered
        self.total_infected = self.maps.total_infected
        self.diagnosed = self.maps.diagnosed



    def update_day(self, day, algorithm = 'random'):

        if algorithm == 'random':
            self.maps.initialize_day(day)

            ## Kill people if they have reached the end of the illness and they are unlucky

            folks_who_die = self.maps.get_end_of_illness_folk(day) * (self.maps.get_random_map() < self.death_rate.val())
            # print(folks_who_die.shape)
            self.maps.kill(day, folks_who_die)
            self.maps.recover(day, np.logical_not(folks_who_die)* self.maps.get_end_of_illness_folk(day))


            # Figure out who gets tested and isolated
            if day> self.intensive_testing_window.val()[0] and day < self.intensive_testing_window.val()[1]:
                folks_getting_tested = self.maps.get_folks_at_day(day, self.incubation_duration + self.day_of_testing.val())
                folks_found_positive = folks_getting_tested * (self.maps.get_random_map() > self.fraction_missed_cases.val())

                # now either kill them or cure them (technically this shouldn't be done right now but they don't participate in the sim anymore anyways)
                dead_mask = self.maps.get_random_map() < self.death_rate.val()
                folks_dying = folks_found_positive * dead_mask
                folks_cured = np.logical_and(folks_found_positive , np.logical_not(dead_mask))
                self.maps.kill(day, folks_dying)
                self.maps.quarantine(day, folks_cured)

            ## Figure out new contaminations

            if day> self.social_isolation_window.val()[0] and day < self.social_isolation_window.val()[1]:
                Reff = self.R0.val()*(1- self.social_isolation_level.val())
            else:
                Reff = self.R0.val()

            total_new_contaminations = int(np.floor(Reff * self.maps.contagious[day - 1]/(self.illness_duration - self.incubation_duration)))
            # print(f"new contam = {total_new_contaminations}")
            frac = Reff * self.maps.contagious[day - 1]/(self.illness_duration - self.incubation_duration) - total_new_contaminations

            if np.random.rand()<frac: #that small fraction did result in a death
                total_new_contaminations +=1
            # print(f"new contam = {total_new_contaminations}")

            self.maps.contaminate_random(day, total_new_contaminations)

            self.maps.update_counters(day)


    def get_last_map(self):
        print("%d kbytes" % (1e-3 * self.map[-1].size * self.map[-1].itemsize * len(self.map)))
        return self.map[-1].tolist()



    def set_params(self, sim_params):
        for id, val in sim_params.items():
            self.InteractiveSimParams[id].set_value(val)
