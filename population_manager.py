import numpy as np



class Counters:

    def __init__(self, population, days, incubation_duration, illness_duration, day_of_diagnosis_after_infection):

        self.population = population
        self.incubation_duration = incubation_duration
        self.illness_duration = illness_duration
        self.day_of_diagnosis_after_infection = day_of_diagnosis_after_infection
        self.days = days
        self.make_counters()

    def make_counters(self):

        self.not_infected = np.ones_like(self.days, dtype = np.float) * self.population
        self.active = np.zeros((len(self.days), self.illness_duration), dtype = np.float)
        self.dead = np.zeros_like(self.days, dtype = np.float)
        self.recovered = np.zeros_like(self.days, dtype = np.float)

        self.total_infected = np.zeros_like(self.days, dtype = np.float)
        self.contagious = np.zeros_like(self.days, dtype = np.float)
        self.diagnosed = np.zeros_like(self.days, dtype = np.float)

    def initialize_first_day(self, initial_diagnosed, fraction_missed_cases_normal):
        initial_contamination = initial_diagnosed / (1-fraction_missed_cases_normal)
        day = 0
        for i in range(int(initial_contamination)):
            stage_of_contam = np.random.randint(self.illness_duration -1)
            self.active[day,stage_of_contam] +=1
        self.not_infected[day] -= initial_contamination
        self.update_derived_counters(day)

    def update_derived_counters(self, day):

        self.total_infected[day] = self.population - self.not_infected[day]
        # print(self.total_infected[day])
        self.contagious[day] = self.get_contagious(day)
        self.diagnosed[day] = self.get_diagnosed(day)

    def get_non_infected(self, day):
        return self.not_infected[day]

    def get_diagnosed(self, day):
        return self.diagnosed[day]

    def get_contagious(self, day):
        return np.sum(self.active[day, self.incubation_duration:])

    def get_active_cases(self, day):
        return np.sum(self.active[day, :])

    def get_dead(self, day):
        return self.dead[day]

    def get_recovered(self, day):
        return self.recovered[day]

    def contaminate_random(self, day, how_many):

        probability_of_someone_being_healthy = self.get_non_infected(day)/self.population
        self.active[day, 0] += how_many*probability_of_someone_being_healthy
        self.not_infected[day] -= how_many*probability_of_someone_being_healthy



    def initialize_day(self, day):
        self.not_infected[day] = self.not_infected[day-1]
        self.active[day, 1:] = self.active[day-1,:-1]
        self.dead[day] = self.dead[day-1]
        self.recovered[day] = self.recovered[day-1]
        self.diagnosed[day] = self.diagnosed[day-1]
        # print(f" init day {day} check= {self.check_population(day)}")



    def get_end_of_illness_folk(self, day):
        return self.active[day,-1]

    def kill(self, day, how_many):
        # print(f"killing {np.sum(who)}")
        self.dead[day] += how_many

    def recover(self, day, how_many):
        self.recovered[day] +=how_many

    def get_folks_at_day(self, day, which_day):
        return self.active[day,which_day]

    def quarantine(self, day, how_many):
        self.recover(day, how_many)

    def kill_or_recover_end_of_illness(self, day, death_rate):

        folks_who_die = self.get_end_of_illness_folk(day -1) *  death_rate
        # print(folks_who_die.shape)
        self.kill(day, folks_who_die)
        self.recover(day, self.get_end_of_illness_folk(day-1) *(1-death_rate))
        # print(f" kill or recover illness  check= {self.check_population(day)}")


    def test_and_isolate(self, day, day_of_testing, fraction_missed_cases, death_rate):

        folks_getting_tested = self.get_folks_at_day(day, self.incubation_duration + day_of_testing)
        folks_found_positive = folks_getting_tested * (1- fraction_missed_cases)
        self.diagnosed[day] += folks_found_positive
        # now either kill them or cure them (technically this shouldn't be done right now but they don't participate in the sim anymore anyways)

        folks_dying = folks_found_positive * death_rate
        folks_cured = folks_found_positive *(1- death_rate)
        self.kill(day, folks_dying)
        self.quarantine(day, folks_cured)
        self.active[day, self.incubation_duration + day_of_testing] -= folks_found_positive
        # print(f" test and isolate  check= {self.check_population(day)}")



    def spread_disease(self, day, Reff_day):
        total_new_contaminations = Reff_day * self.get_contagious(day)

        self.contaminate_random(day, total_new_contaminations)
        # print(f" spread disease check = {self.check_population(day)}")

    def end_day(self, day):
        self.update_derived_counters(day)

    def check_population(self,day):
        return self.get_non_infected(day)+self.get_active_cases(day)+self.get_dead(day) +self.get_recovered(day)

    def get_all_active(self):
        return np.sum(self.active, axis = 1)


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
            while self.maps[day][x_k, y_k] != self.NOT_INFECTED:
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
        return self.maps[day] == self.NOT_INFECTED

    def get_diagnosed(self,day):
        return np.logical_or(self.maps[day] > self.day_of_diagnosis_after_infection, np.logical_or(self.get_dead(day), self.get_recovered(day)))

    def get_contagious(self,day):
        return self.maps[day] > self.incubation_duration

    def get_active_cases(self, day):
        return self.maps[day] > 0

    def get_dead(self, day):
        return self.maps[day] == self.DEAD

    def get_recovered(self, day):
        return self.maps[day] == self.RECOVERED

    def contaminate_random(self,day, how_many):
        # print(f"contaminating on day {day} {how_many} people")
        for k in range(how_many):
            x_k = np.random.randint(self.x_max)
            y_k = np.random.randint(self.y_max)
            if self.maps[day][x_k, y_k] == self.NOT_INFECTED:
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
        self.maps[day][who] = self.DEAD

    def recover(self,day, who):
        self.maps[day][who] = self.RECOVERED

    def get_folks_at_day(self ,day, which_day):
        return self.maps[day] == which_day

    def quarantine(self, day, who):
        self.recover(day, who)

    def get_last_map(self):
        return self.maps[-1]

    def kill_or_recover_end_of_illness(self, day, death_rate):
        folks_who_die = self.get_end_of_illness_folk(day) * (self.get_random_map() <death_rate)
        # print(folks_who_die.shape)
        self.kill(day, folks_who_die)
        self.recover(day, np.logical_not(folks_who_die) * self.get_end_of_illness_folk(day))

    def test_and_isolate(self, day, day_of_testing, fraction_missed_cases, death_rate):

        folks_getting_tested = self.get_folks_at_day(day, self.incubation_duration + day_of_testing)
        folks_found_positive = folks_getting_tested * (self.get_random_map() > fraction_missed_cases)

        # now either kill them or cure them (technically this shouldn't be done right now but they don't participate in the sim anymore anyways)
        dead_mask = self.get_random_map() < death_rate
        folks_dying = folks_found_positive * dead_mask
        folks_cured = np.logical_and(folks_found_positive, np.logical_not(dead_mask))
        self.kill(day, folks_dying)
        self.quarantine(day, folks_cured)

    def spread_disease(self, day, Reff):
        total_new_contaminations = int(np.floor(Reff * self.contagious[day - 1] / (self.illness_duration - self.incubation_duration)))
        # print(f"new contam = {total_new_contaminations}")
        frac = Reff * self.contagious[day - 1] / (
                    self.illness_duration - self.incubation_duration) - total_new_contaminations

        if np.random.rand() < frac:  # that small fraction did result in a death
            total_new_contaminations += 1
        # print(f"new contam = {total_new_contaminations}")

        self.contaminate_random(day, total_new_contaminations)

    def end_day(self, day):
        self.update_counters(day)