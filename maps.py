import numpy as np


NOT_INFECTED = 0
DEAD = -1
RECOVERED = -2

class Maps:

    NOT_INFECTED = 0
    DEAD = -1
    RECOVERED = -2

    def __init__(self, population, days, incubation_duration, illness_duration, day_of_diagnosis_after_infection):

        self.population = population
        self.incubation_duration = incubation_duration
        self.illness_duration = illness_duration
        self.day_of_diagnosis_after_infection = day_of_diagnosis_after_infection
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
        self.not_infected = np.zeros_like(self.days)
        self.active = np.zeros_like(self.days)
        self.dead = np.zeros_like(self.days)
        self.recovered = np.zeros_like(self.days)
        self.total_infected = np.zeros_like(self.days)
        self.contagious = np.zeros_like(self.days)
        self.diagnosed = np.zeros_like(self.days)

    def initialize_first_day(self, initial_contamination):
        day = 0
        for k in range(initial_contamination):
            x_k = np.random.randint(self.x_max)
            y_k = np.random.randint(self.y_max)
            while self.maps[day][x_k, y_k] != NOT_INFECTED:
                x_k = np.random.randint(self.x_max)
                y_k = np.random.randint(self.y_max)

            self.maps[day][x_k, y_k] = np.random.randint(low =1, high = self.illness_duration -1 )
        self.update_counters(day)

    def update_counters(self, day):
        # if day == 1:
            # print(self.maps[day])
        self.not_infected[day] = np.sum(self.get_non_infected(day))
        # print(self.not_infected[day])
        self.active[day] = np.sum(self.get_active_cases(day))
        self.dead[day] = np.sum(self.get_dead(day))
        self.recovered[day] = np.sum(self.get_recovered(day))
        self.total_infected[day] = self.simulated_population - self.not_infected[day]
        # print(self.total_infected[day])
        self.contagious[day] = np.sum(self.get_contagious(day))
        self.diagnosed[day] = np.sum(self.get_diagnosed(day))

    def get_non_infected(self, day):
        return self.maps[day] == NOT_INFECTED

    def get_diagnosed(self,day):
        return np.logical_or(self.maps[day] > self.day_of_diagnosis_after_infection, np.logical_or(self.get_dead(day), self.get_recovered(day)))

    def get_contagious(self,day):
        return self.maps[day] > self.incubation_duration

    def get_active_cases(self, day):
        return self.maps[day] > 0

    def get_dead(self, day):
        return self.maps[day] == DEAD

    def get_recovered(self, day):
        return self.maps[day] == RECOVERED

    def contaminate_random(self,day, how_many):
        # print(f"contaminating on day {day} {how_many} people")
        for k in range(how_many):
            x_k = np.random.randint(self.x_max)
            y_k = np.random.randint(self.y_max)
            if self.maps[day][x_k, y_k] == NOT_INFECTED:
                self.maps[day][x_k, y_k] = 1

    def initialize_day(self, day):
            self.maps[day][:] = self.maps[day -1]
            self.maps += self.get_active_cases(day -1 ).astype(np.int8)

    def get_end_of_illness_folk(self, day):
        return self.maps[day] == self.illness_duration

    def get_random_map(self):
        return np.random.rand(self.x_max, self.y_max)

    def kill(self, day, who):
        # print(f"killing {np.sum(who)}")
        self.maps[day][who] = DEAD

    def recover(self,day, who):
        self.maps[day][who] = RECOVERED

    def get_folks_at_day(self ,day, which_day):
        return self.maps[day] == which_day

    def quarantine(self, day, who):
        self.recover(day, who)

    def get_last_map(self):
        return self.maps[-1]