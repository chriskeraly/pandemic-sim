import numpy as np


NOT_INFECTED = 0
DEAD = -1
RECOVERED = -2

class Maps:
    def __init__(self, population, days, incubation_duration, illness_duration):
        self.population = population
        self.incubation_duration = incubation_duration
        self.ILLNESS_DURATION = illness_duration
        self.days = days
        self.make_maps()
        self.make_counters()


    def make_maps(self):
        self.x_max = self.y_max = self.side = int(np.floor(np.sqrt(self.population)))
        self.simulated_population = self.side ** 2
        self.x = np.arange(self.x_max)
        self.y = np.arange(self.y_max)
        self.maps =[np.zeros((self.x_max, self.y_max), dtype=np.int8) for day in self.days]
        
    def make_counters(self):
        self.not_infected = np.zeros(self.days[-1])
        self.active = np.zeros(self.days[-1])
        self.dead = np.zeros(self.days[-1])
        self.recovered = np.zeros(self.days[-1])
        self.total_infected = np.zeros(self.days[-1])

    def initialize_first_day(self, initial_contamination):
        day = 0
        for k in range(initial_contamination):
            x_k = np.random.randint(self.x_max)
            y_k = np.random.randint(self.y_max)
            while self.maps[day][x_k, y_k] != NOT_INFECTED:
                x_k = np.random.randint(self.x_max)
                y_k = np.random.randint(self.y_max)

            self.maps[day][x_k, y_k] = np.random.randint((1, self.illness_duration -1 ))
        self.update_counters(day)

    def update_counters(self, day):
        self.not_infected[day] = np.sum(self.get_non_infected(day))
        self.active[day] = np.sum(self.get_active(day))
        self.dead[day] = np.zeros(self.get_dead(day))
        self.recovered[day] = np.zeros(self.get_recovered(day))
        self.total_infected[day] = self.simulated_population - self.not_infected[day]

    def get_non_infected(self, day):
        return self.maps[day] == NOT_INFECTED

    def get_active_cases(self, day):
        return self.maps[day] > 0

    def get_dead(self, day):
        return self.maps[day] == DEAD

    def get_recovered(self, day):
        return self.maps[day] == RECOVERED
