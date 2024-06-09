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
        gene = random.choice(chromosome)
        gene['time_slot_date'], gene['time_slot_day'], gene['time_slot_shift'] = self.shift_time_slot((gene['time_slot_date'], gene['time_slot_day'], gene['time_slot_shift']))

        return chromosome
    
    def shift_time_slot(self, time_slot: tuple) -> tuple:
        # Shift the time slot by 1 day
        if time_slot[1] == self.constant.days[-1]:
            return (time_slot[0] + timedelta(days=2), self.constant.days[0], time_slot[2])
        return (time_slot[0] + timedelta(days=1), self.constant.days[self.constant.days.index(time_slot[1]) + 1], time_slot[2])
    
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
    
