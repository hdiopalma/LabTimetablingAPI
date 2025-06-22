#Mutation Class

import random
from math import floor
from datetime import timedelta
from typing import List

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import LaboratoryData, ModuleData, Constant

import scheduling_algorithm.factory.timeslot_generator as timeslot_generator

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
    """SwapMutation class to swap the assistant and time slot of random two genes in a chromosome.
    """
    def __init__(self):
        super().__init__("SwapMutation")
    
    def __call__(self, chromosome: Chromosome):
        # Randomly select a gene
        gene1 = random.choice(chromosome)
        gene2 = random.choice(chromosome)
        gene1['assistant'], gene2['assistant'] = gene2['assistant'], gene1['assistant']
        gene1['time_slot_date'], gene2['time_slot_date'] = gene2['time_slot_date'], gene1['time_slot_date']
        gene1['time_slot_day'], gene2['time_slot_day'] = gene2['time_slot_day'], gene1['time_slot_day']
        gene1['time_slot_shift'], gene2['time_slot_shift'] = gene2['time_slot_shift'], gene1['time_slot_shift']
        return chromosome
    
class ShiftMutation(BaseMutation):
    def __init__(self):
        super().__init__("ShiftMutation")
        self.constant = Constant
    
    def __call__(self, chromosome: Chromosome):
        gene_idx = random.randint(0, len(chromosome)-1)  #untuk menghindari reference issue
        gene = chromosome[gene_idx]
        gene['time_slot_date'], gene['time_slot_day'], gene['time_slot_shift'] = self.shift_time_slot((gene['time_slot_date'], gene['time_slot_day'], gene['time_slot_shift']))

        return chromosome
    
    def shift_time_slot(self, time_slot: tuple) -> tuple:
        # time_slot: (timestamp, day_name, shift_name)
        timestamp, day_name, shift_name = time_slot
        days = self.constant.days
        shifts = self.constant.shifts

        def next_day(day):
            day_idx = days.index(day)
            new_day_idx = (day_idx + 1) % len(days)
            new_day = days[new_day_idx]
            # If the next day is Sunday, skip to Monday
            if new_day.lower() == "sunday":
                new_day_idx = (new_day_idx + 1) % len(days)
                new_day = days[new_day_idx]
            return new_day

        if random.random() < 0.5:
            # Shift by 1 day
            # print(f"Shifting time slot {time_slot} by 1 day")
            new_day = next_day(day_name)
            # Add 1 day (86400 seconds) to timestamp
            new_timestamp = timestamp + 86400
            return (new_timestamp, new_day, shift_name)
        else:
            # Shift by 1 shift
            # print(f"Shifting time slot {time_slot} by 1 shift")
            shift_idx = shifts.index(shift_name)
            if shift_idx == len(shifts) - 1:
                # Last shift, move to first shift and next day
                new_shift = shifts[0]
                new_day = next_day(day_name)
                new_timestamp = timestamp + 86400
                return (new_timestamp, new_day, new_shift)
            else:
                new_shift = shifts[shift_idx + 1]
                return (timestamp, day_name, new_shift)
    
class RandomMutation(BaseMutation):
    def __init__(self):
        super().__init__("RandomMutation")
        self.constant = Constant
        self.laboratories = LaboratoryData
        self.modules = ModuleData

    def __call__(self, chromosome: Chromosome):
        # Randomly select a gene
        gene_data = random.choice(chromosome)
        assistant = random.choice(self.laboratories.get_assistants(gene_data['laboratory'])).id
        week = chromosome.week
        # Change the gene
        gene_data['time_slot_date'], gene_data['time_slot_day'], gene_data['time_slot_shift'] = timeslot_generator.get_random_time_slot(gene_data['module'], gene_data['group'], assistant, week)
        gene_data['assistant'] = assistant
        return chromosome
    
class DynamicMutation(BaseMutation):
    def __init__(self, name, mutation_function):
        super().__init__(name)
        self.mutation_function = mutation_function
    
    def __call__(self, chromosome: Chromosome):

        return self.mutation_function(chromosome)
    
class MutationManager:
    '''Class to manage multiple mutation functions.'''
    def __init__(self, mutation_functions: List[BaseMutation]):
        self.mutation_functions = mutation_functions
        self.mutation_probability = None
    
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
    
    @classmethod
    def create(cls, config):
        mutation_functions = []
        if config.get("swap"):
            mutation_functions.append(SwapMutation())
        if config.get("shift"):
            mutation_functions.append(ShiftMutation())
        if config.get("random"):
            mutation_functions.append(RandomMutation())
        if not mutation_functions:
            raise ValueError("At least one mutation function must be enabled")
        print("Configuring mutation operator: ", mutation_functions)
        
        instance = cls(mutation_functions)
        instance.configure(config["mutation_probability"])
        return instance
    
