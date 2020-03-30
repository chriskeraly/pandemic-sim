import numpy as np
import copy
from collections import OrderedDict
import dash_core_components as dcc
import dash_html_components as html


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
        self.initial_contamination = 10
        self.active_days = 21
        self.sim_days = InteractiveSimParam('Simulation duration (days)', 1 , 365, 1, 150, category = 'Simulation parameters')
        self.population = InteractiveSimParam('Population Simulated', 10, 100000, 1, 10000, category = 'Simulation parameters')
        self.R0 = InteractiveSimParam('R0: With no changes to behavior, how many people will one infected person infect', 0 , 20 , 0.01,4)
        self.death_rate = InteractiveSimParam('Death Rate',0,0.1,0.001,0.01)

        self.social_isolation_window = InteractiveSimParam_dayslider('Social Isolation window period (days)', 0 , 365, 1, [21, 70], type = 'rangeslider')
        self.social_isolation_level = InteractiveSimParam("Fraction of social contact reduction during social isolation", 0 , 1, 0.01, 0.8)

        self.intensive_testing_window = InteractiveSimParam_dayslider('Intensive testing and tracking window period (days)', 0 , 365, 1, [75, 365], type = 'rangeslider')
        self.fraction_missed_cases = InteractiveSimParam("Fraction of undiagnosed infections in spite of intensive testing", 0 , 1, 0.01, 0.1)
        self.day_of_testing = InteractiveSimParam("Delay between infection and test/quarantine during intensive testing regime", 0 , self.active_days, 1, 3)


        # self.testing_schem_start =


        self.register_InteractiveSimParams()


    def register_InteractiveSimParams(self):

        self.InteractiveSimParams = OrderedDict()
        for id, thing in self.__dict__.items():
            if isinstance(thing, InteractiveSimParam):
                self.InteractiveSimParams[thing.id]=thing

    def run(self):
        self.init_variables()
        self.run_algorithm()
        print("%d kbytes" % (1e-3 * self.map[-1].size * self.map[-1].itemsize * len(self.map)))

    def create_map(self):
        self.x_max = self.y_max =self.side = int(np.floor(np.sqrt(self.population.val())))
        self.simulated_population = self.side**2
        self.x = np.arange(self.x_max)
        self.y = np.arange(self.y_max)
        #TODO: Map should be a class
        self.map = []
        for i in self.days:
            self.map.append(np.array(np.zeros((self.x_max, self.y_max), dtype=np.int8)))


    # def get_xy(self, i):
    #     x = self.x%self.y_max
    #     y = dunno yet
    #     return x, y

    def init_variables(self):
        self.days = np.arange(self.sim_days.val())
        self.create_map()
        self.virgin = np.ones(self.sim_days.val())
        self.active_cases = np.zeros(self.sim_days.val())
        self.dead = np.zeros(self.sim_days.val())
        self.recovered = np.zeros(self.sim_days.val())
        self.total_infected = np.zeros(self.sim_days.val())
        # self.init_variables_algorithm()

    # def init_variables_algorithm(self,algorithm = 'random'):
    #     if algorithm == 'random':
    #         self.random_
    #

    def run_algorithm(self):
        self.create_first_day()
        for i in self.days[1:]:
            self.update_day(i)


    def create_first_day(self,algorithm = 'random'):
        day = 0
        if algorithm == 'random':
            for k in np.arange(self.initial_contamination):
                #TODO check if not already contaminated
                x_k = np.random.randint(self.x_max)
                y_k = np.random.randint(self.y_max)
                self.map[day][x_k, y_k] = np.min((k,self.active_days-1))
        currently_infected_map = np.logical_and(self.map[day] > 0, self.map[day] < self.active_days)
        self.active_cases[day] = np.sum(currently_infected_map)


    def update_day(self, day, algorithm = 'random'):

        if algorithm == 'random':
            ## Who is infected this morning?
            yesterday_infected_map = np.logical_and(self.map[day-1] > 0, self.map[day-1] < self.active_days)
            self.map[day] = self.map[day - 1] + np.ones(self.map[day].shape, dtype=np.int8) * yesterday_infected_map
            ## Figure out who gets tested and isolated
            if day> self.intensive_testing_window.val()[0] and day < self.intensive_testing_window.val()[1]:
                folks_getting_tested = (self.map[day] == self.day_of_testing.val())
                folks_found_positive = folks_getting_tested * (np.random.rand(self.x_max, self.y_max) > self.fraction_missed_cases.val())

                #now either kill them or cure them (technically this shouldn't be done right now but they don't participate in the sim anymore anyways
                dead_mask = np.random.rand(self.x_max, self.y_max) < self.death_rate.val()
                folks_dying = folks_found_positive * dead_mask
                folks_cured = np.logical_and(folks_found_positive ,np.logical_not(dead_mask))
                self.map[day][folks_dying] = self.active_days *2
                self.map[day][folks_cured] = self.active_days - 1

            ## Figure out new contaminations
            # print(currently_infected_map)
            # print(self.map[day-1])

            if day> self.social_isolation_window.val()[0] and day < self.social_isolation_window.val()[1]:
                Reff = self.R0.val()*(1- self.social_isolation_level.val())
            else:
                Reff = self.R0.val()

            total_new_contaminations = np.floor(Reff * self.active_cases[day - 1]/self.active_days)

            frac = Reff * self.active_cases[day - 1]/self.active_days - total_new_contaminations

            if np.random.rand()<frac: #that small fraction did result in a death
                x_k = np.random.randint(self.x_max)
                y_k = np.random.randint(self.y_max)
                if self.map[day - 1][x_k, y_k] == 0:
                    self.map[day][x_k, y_k] = 1
            for k in np.arange(total_new_contaminations):

                x_k = np.random.randint(self.x_max)
                y_k = np.random.randint(self.y_max)
                if self.map[day-1][x_k, y_k] == 0:
                    self.map[day][x_k, y_k] = 1
            # today_infected_map = np.logical_and(self.map[day] > 0, self.map[day] < self.active_days)

            ##Figure out deaths

            folks_who_can_die = self.map[day] == self.active_days -1
            folks_who_die = folks_who_can_die * (np.random.rand(self.x_max, self.y_max) < self.death_rate.val())

            self.map[day] += folks_who_die * (self.active_days + 1)
            today_infected_map = np.logical_and(self.map[day] > 0, self.map[day] < self.active_days)
            self.active_cases[day] = np.sum(today_infected_map)
            self.total_infected[day] = np.sum(self.map[day]!=0)
            self.recovered = np.sum(self.map[day]==self.active_days -1 )
            self.dead[day] = np.sum(self.map[day] == self.active_days *2)


    def get_last_map(self):
        # print(self.map[-1])
        # print(self.active_cases)
        # print(type(self.active_cases))
        img_rgb = [[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                   [[0, 255, 0], [0, 0, 255], [255, 0, 0]]]
        # print( self.map[-1].tolist())
        # print(type(self.map[-1].tolist()[1]))\
        import sys
        # print(sys.getsizeof(self.map))
        # print(type(self.map[-1]))
        # print(self.map[-1].dtype)
        print("%d kbytes" % (1e-3 * self.map[-1].size * self.map[-1].itemsize * len(self.map)))
        return self.map[-1].tolist()



    def set_params(self, sim_params):
        for id, val in sim_params.items():
            self.InteractiveSimParams[id].set_value(val)


