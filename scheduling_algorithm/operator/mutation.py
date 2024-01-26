#Mutation Class

import random
from math import floor
from datetime import timedelta
from typing import List

#Simple data structure for timeslot
from collections import namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import LaboratoryData, ModuleData, Constant

class BaseMutation:
    def __init__(self, name, probability_weight=1):
        self.name = name
        self.probability_weight = probability_weight # It is used to determine the probability of the mutation function being called if more than one mutation function is used.
    
    def __str__(self):
        return f"Mutation(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        raise NotImplementedError("Mutation function not implemented")
    
class SwapMutation(BaseMutation):
    def __init__(self):
        super().__init__("SwapMutation")
    
    def __call__(self, chromosome: Chromosome):
        # Randomly select a gene
        gene1 = random.choice(chromosome)
        gene2 = random.choice(chromosome)
        gene1['assistant'], gene2['assistant'] = gene2['assistant'], gene1['assistant']
        gene1['time_slot'], gene2['time_slot'] = gene2['time_slot'], gene1['time_slot']
        return chromosome
    
class ShiftMutation(BaseMutation):
    def __init__(self):
        super().__init__("ShiftMutation")
        self.constant = Constant
    
    def __call__(self, chromosome: Chromosome):
        gene = random.choice(chromosome)
        gene['time_slot'] = self.shift_time_slot(gene['time_slot'])

        return chromosome
    
    def shift_time_slot(self, time_slot: TimeSlot) -> TimeSlot:
        # Shift the time slot by 1 day
        if time_slot.day == self.constant.days[-1]:
            return TimeSlot(time_slot.date + timedelta(days=2), self.constant.days[0], time_slot.shift)
        return TimeSlot(time_slot.date + timedelta(days=1), self.constant.days[self.constant.days.index(time_slot.day) + 1], time_slot.shift)
    
class RandomMutation(BaseMutation):
    def __init__(self):
        super().__init__("RandomMutation")
        self.constant = Constant
        self.laboratories = LaboratoryData
        self.modules = ModuleData

    def __call__(self, chromosome: Chromosome):
        # Randomly select a gene
        gene_data = random.choice(chromosome)
        module_date = self.modules.get_dates(gene_data['module'])
        time_slot = self.generate_time_slot(module_date.start_date, module_date.end_date)
        assistant = random.choice(self.laboratories.get_assistants(gene_data['laboratory'])).id
        # Change the gene
        gene_data['time_slot'] = time_slot
        gene_data['assistant'] = assistant
        return chromosome
    
    def generate_time_slot(self, start_date, end_date):
        """Generate time slots based on the start date, end date, days and shifts"""
        #if start_date not start from Monday, then start from the next Monday
        if start_date.weekday() != 0:
            start_date = start_date + timedelta(days=7 - start_date.weekday())
        duration = (end_date - start_date).days + 1
        weeks_duration = floor(duration / 7)
        random_weeks = random.randint(0, weeks_duration)
        random_days = random.choice(self.constant.days)
        random_shifts = random.choice(self.constant.shifts)
        random_date = start_date + timedelta(days=random_weeks * 7 + self.constant.days.index(random_days))
        return TimeSlot(random_date, random_days, random_shifts)
    
class DynamicMutation(BaseMutation):
    def __init__(self, name, mutation_function):
        super().__init__(name)
        self.mutation_function = mutation_function
    
    def __call__(self, chromosome: Chromosome):

        return self.mutation_function(chromosome)
    
class MutationManager:
    def __init__(self, mutation_functions: List[BaseMutation]):
        self.mutation_functions = mutation_functions
        self.mutation_probability = 0.1
    
    def __str__(self):
        return f"MutationManager(mutation_functions={self.mutation_functions})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        #random based on probability weight
        if random.random() < self.mutation_probability:
            mutation_function = self.get_random_mutation()
            return mutation_function(chromosome)
        return chromosome
    
    def get_random_mutation(self):
        return random.choices(self.mutation_functions, weights=[mutation.probability_weight for mutation in self.mutation_functions])[0]
    
    def configure(self, mutation_probability):
        self.mutation_probability = mutation_probability
        return self